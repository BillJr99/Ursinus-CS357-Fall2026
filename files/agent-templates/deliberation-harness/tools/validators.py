"""Validators: run external checks and report what actually happened.

The point of this module is that a check is something a *process* did, not
something a model said.  Every function here returns the exit code, the captured
output, and the elapsed time, so a claim like "the tests pass" can be traced to a
command and a zero.

Nothing here deletes, overwrites, publishes, or pushes.  If you add a validator
that does any of those, put it behind confirm_irreversible() in deliberate_loop.py.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import shlex
import time
import traceback
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# --------------------------------------------------------------------------- #
# One command's result
# --------------------------------------------------------------------------- #

@dataclass
class CommandResult:
    """Everything observable about running one validator command."""

    command: str
    exit_code: int | None          # None means it never finished (timed out or died)
    stdout: str
    stderr: str
    timed_out: bool
    elapsed_s: float

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TierResult:
    """The outcome of one tier of the validation hierarchy."""

    tier: int
    name: str
    results: list[CommandResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        # A tier with no commands configured passes vacuously; say so in your
        # report rather than counting it as evidence of anything.
        return all(r.passed for r in self.results)

    @property
    def ran(self) -> bool:
        return len(self.results) > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier,
            "name": self.name,
            "ran": self.ran,
            "passed": self.passed,
            "results": [r.to_dict() for r in self.results],
        }


# --------------------------------------------------------------------------- #
# Running commands
# --------------------------------------------------------------------------- #

async def run_command(command: str, cwd: Path, timeout_s: int) -> CommandResult:
    """Run one shell command, capturing everything, and never raise.

    A validator that raises takes the whole run down with it, which is exactly
    backwards: a validator failing to run IS a result, and the loop needs to see
    it as one.
    """
    started = time.monotonic()
    try:
        proc = await asyncio.create_subprocess_exec(
            *shlex.split(command),
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as e:                                    # noqa: BLE001
        print(f"[validators.run_command] could not start {command!r}: {e}")
        traceback.print_exc()
        return CommandResult(command, None, "", str(e), False, time.monotonic() - started)

    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
        return CommandResult(
            command=command,
            exit_code=proc.returncode,
            stdout=out.decode("utf-8", "replace"),
            stderr=err.decode("utf-8", "replace"),
            timed_out=False,
            elapsed_s=time.monotonic() - started,
        )
    except asyncio.TimeoutError:
        # A hung validator is a failure with a specific cause; kill it and say which.
        try:
            proc.kill()
            await proc.wait()
        except Exception as e:                                # noqa: BLE001
            print(f"[validators.run_command] could not kill {command!r}: {e}")
        return CommandResult(command, None, "", f"timed out after {timeout_s}s",
                             True, time.monotonic() - started)
    except Exception as e:                                    # noqa: BLE001
        print(f"[validators.run_command] {command!r} failed: {e}")
        traceback.print_exc()
        return CommandResult(command, None, "", str(e), False, time.monotonic() - started)


async def run_tier(tier_spec: dict[str, Any], cwd: Path, artifact: Path,
                   timeout_s: int) -> TierResult:
    """Run every command in one tier, in order, and stop at the first failure.

    Stopping early inside a tier is a choice: it keeps the log short and the
    fingerprint stable.  Run them all instead if you would rather see the full
    picture each iteration, and say in your reflection which you chose and why.
    """
    result = TierResult(tier=tier_spec["tier"], name=tier_spec["name"])
    for template in tier_spec.get("commands", []):
        command = template.replace("{artifact}", str(artifact))
        outcome = await run_command(command, cwd, timeout_s)
        result.results.append(outcome)
        if not outcome.passed:
            break
    return result


async def validate(config: dict[str, Any], cwd: Path, artifact: Path) -> list[TierResult]:
    """Run the whole hierarchy in order, stopping after the first failing tier.

    This is the lexicographic rule in code: tier 2 failing means tiers 3 and
    below never run, because nothing they could report would change the verdict.
    A polished style score does not offset a failed acceptance test.
    """
    spec = config["validators"]
    timeout_s = spec.get("command_timeout_s", 120)
    tiers: list[TierResult] = []
    for tier_spec in spec["tiers"]:
        tier = await run_tier(tier_spec, cwd, artifact, timeout_s)
        tiers.append(tier)
        if tier.ran and not tier.passed:
            break
    return tiers


# --------------------------------------------------------------------------- #
# Ranking and fingerprinting
# --------------------------------------------------------------------------- #

def rank_key(tiers: list[TierResult]) -> tuple:
    """A sortable key implementing the lexicographic hierarchy.

    Higher is better, compared with `>`.  The key is (0, index of the first
    failing tier) for a failure and (1, 0) for a clean pass, so a candidate that
    gets further down the hierarchy before failing beats one that fails earlier,
    a clean pass beats every failure, and nothing in a lower tier can rescue a
    higher one: the key ignores everything after the first failure.
    """
    for i, tier in enumerate(tiers):
        if tier.ran and not tier.passed:
            return (0, i)         # failed: rank by how far down it got
    return (1, 0)                 # nothing failed: beats any failure


def is_better(new: list[TierResult], best: list[TierResult] | None) -> bool:
    """Did this attempt actually improve on the best we already had?

    Used to decide whether to keep a repair.  Equal is not better: a repair that
    changes the code without moving the validation result gets discarded, which
    is what keeps the loop from wandering.
    """
    if best is None:
        return True
    return rank_key(new) > rank_key(best)


def failure_fingerprint(tiers: list[TierResult]) -> str:
    """A stable identifier for *how* this attempt failed.

    Two iterations producing the same fingerprint means the repair loop is going
    in a circle, which is a stopping condition.  Numbers, paths, addresses, and
    timings are stripped so that the same logical failure fingerprints the same
    across runs.
    """
    parts: list[str] = []
    for tier in tiers:
        if not tier.ran or tier.passed:
            continue
        for r in tier.results:
            if r.passed:
                continue
            text = (r.stderr or r.stdout or "")[-4000:]
            text = re.sub(r"0x[0-9a-fA-F]+", "<addr>", text)
            text = re.sub(r"\b\d+\.\d+s?\b", "<num>", text)
            text = re.sub(r"\b\d+\b", "<num>", text)
            text = re.sub(r"(/[\w.\-]+)+", "<path>", text)
            text = re.sub(r"\s+", " ", text).strip()
            parts.append(f"{tier.name}:{text}")
    if not parts:
        return "no-failure"
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def summarize(tiers: list[TierResult]) -> dict[str, Any]:
    """The shape written into validation-results.json.

    Note the three-way split. "Not run" is reported separately from "passed",
    because a tier with no configured commands is not evidence of correctness
    and a final report that conflates them is overstating its case.
    """
    passed, failed, not_run = [], [], []
    for tier in tiers:
        if not tier.ran:
            not_run.append(tier.name)
        elif tier.passed:
            passed.append(tier.name)
        else:
            failed.append(tier.name)
    return {
        "passed": passed,
        "failed": failed,
        "not_run": not_run,
        "fingerprint": failure_fingerprint(tiers),
        "all_hard_gates_pass": not failed,
        "tiers": [t.to_dict() for t in tiers],
    }


def write_results(path: Path, tiers: list[TierResult]) -> None:
    """Persist one validation pass as JSON, creating parent directories."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summarize(tiers), indent=2), encoding="utf-8")
    except Exception as e:                                    # noqa: BLE001
        print(f"[validators.write_results] could not write {path}: {e}")
        traceback.print_exc()
