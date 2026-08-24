"""The controller: the part of the harness a SKILL.md cannot be.

A skill can describe this workflow.  It cannot enforce it.  Only code can
guarantee that three candidates were generated in separate calls, that the best
one was preserved before a repair touched it, that a budget was actually
checked, and that the loop stopped for a stated reason rather than because the
model announced it was finished.  That is what this file is for, and it is the
line the assignment asks you to be able to draw.

This is a starting point, not a solution.  It runs, and it is deliberately
missing the parts that make it *yours*: your charter questions, your validators,
your stopping rules.  Read it, then change it.

    python tools/deliberate_loop.py --task-id fizzbuzz --objective "..." --workdir .
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import shutil
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import validators

try:
    import requests
except ImportError:                                            # noqa: BLE001
    print("[deliberate_loop] this needs `requests`: pip install requests")
    raise


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path: Path) -> dict[str, Any]:
    """Read a JSON file, failing with the path in the message."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[load_json] missing file: {path}")
        raise
    except json.JSONDecodeError as e:
        print(f"[load_json] {path} is not valid JSON: {e}")
        raise


def write_json(path: Path, obj: Any) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    except Exception as e:                                     # noqa: BLE001
        print(f"[write_json] could not write {path}: {e}")
        traceback.print_exc()


def append_jsonl(path: Path, obj: Any) -> None:
    """Append one record to a JSONL log. Append-only on purpose: the repair log
    is evidence, and evidence you can rewrite is not evidence."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj) + "\n")
    except Exception as e:                                     # noqa: BLE001
        print(f"[append_jsonl] could not append to {path}: {e}")
        traceback.print_exc()


def confirm_irreversible(description: str) -> bool:
    """Ask a human before anything that cannot be undone.

    Charter acceptance is not this confirmation.  Accepting a charter says "these
    are the rules"; this says "do this specific irreversible thing now."  Keep
    them separate, and never let a flag turn this into an automatic yes.
    """
    print(f"\n  IRREVERSIBLE: {description}")
    try:
        answer = input("  Type 'yes' to proceed, anything else to skip: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n  no input available, treating as declined")
        return False
    return answer == "yes"


# --------------------------------------------------------------------------- #
# Budgets
# --------------------------------------------------------------------------- #

@dataclass
class Budget:
    """A budget the controller actually checks. An unchecked budget is a wish."""

    wall_clock_s: int
    max_model_calls: int
    started_at: float
    model_calls: int = 0

    def spend_call(self) -> None:
        self.model_calls += 1

    def elapsed_s(self) -> float:
        return time.monotonic() - self.started_at

    def exhausted(self) -> str | None:
        """Return the name of the exhausted budget, or None."""
        if self.elapsed_s() >= self.wall_clock_s:
            return "wall_clock"
        if self.model_calls >= self.max_model_calls:
            return "model_calls"
        return None


# --------------------------------------------------------------------------- #
# The charter gate
# --------------------------------------------------------------------------- #

def charter_gate(workdir: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Refuse to do substantive work until a human has accepted the charter.

    Three separate things are checked, and each has bitten someone: the file
    exists, a human set accepted=true, and CHARTER.md has not been edited since
    that acceptance.  The third is why content_hash is in the schema; without it
    the charter can be rewritten after approval and the gate means nothing.
    """
    charter_path = workdir / config["paths"]["charter_json"]
    md_path = workdir / config["paths"]["charter_md"]

    if not charter_path.exists():
        raise SystemExit(
            f"[charter_gate] no charter at {charter_path}.\n"
            "  Run the charter-builder skill first. The orchestrator does not start without one."
        )

    charter = load_json(charter_path)

    if not charter.get("accepted"):
        raise SystemExit(
            "[charter_gate] the charter exists but has not been accepted by a human.\n"
            "  Review it, then set \"accepted\": true and record accepted_at and owner."
        )

    if md_path.exists():
        digest = hashlib.sha256(md_path.read_bytes()).hexdigest()
        recorded = charter.get("content_hash")
        if recorded and recorded != digest:
            raise SystemExit(
                "[charter_gate] CHARTER.md changed after it was accepted.\n"
                f"  accepted hash: {recorded}\n  current hash:  {digest}\n"
                "  A material change needs renewed approval. Re-run the charter-builder skill."
            )

    print(f"  charter {charter.get('charter_version')} accepted by "
          f"{charter.get('owner')} at {charter.get('accepted_at')}")
    return charter


# --------------------------------------------------------------------------- #
# Task contract
# --------------------------------------------------------------------------- #

def build_task_contract(task_id: str, objective: str, charter: dict[str, Any]) -> dict[str, Any]:
    """Draft the acceptance specification for one task.

    Drafted here, corrected by the human before execution.  Every hard constraint
    needs an acceptance check or an explicit note that it takes human judgment;
    a constraint nothing checks is a preference wearing a constraint's clothes.
    """
    return {
        "task_id": task_id,
        "objective": objective,
        "deliverables": [],
        "hard_constraints": list(charter.get("prohibited", [])),
        "soft_preferences": [],
        "acceptance_checks": list(charter.get("definition_of_done", [])),
        "assumptions": [],
        "unknowns": [],
        "prohibited_actions": list(charter.get("prohibited", [])),
        "required_confirmations": list(charter.get("require_confirmation", [])),
        "resource_budget": dict(charter.get("budgets", {})),
        "status": "draft",
        "charter_version": charter.get("charter_version"),
        "created_at": now_iso(),
    }


def approve_contract(path: Path) -> dict[str, Any]:
    """Give the human a chance to correct the contract before anything runs.

    This is the second gate, and it is the one that catches a misunderstood
    objective while a misunderstanding is still cheap.
    """
    print(f"\n  Task contract drafted at {path}")
    print("  Open it, fix anything wrong, then set \"status\": \"approved\".")
    try:
        input("  Press Enter once you have done that: ")
    except (EOFError, KeyboardInterrupt):
        print()
    contract = load_json(path)
    if contract.get("status") != "approved":
        raise SystemExit("[approve_contract] contract is not approved; stopping.")
    return contract


# --------------------------------------------------------------------------- #
# Talking to the model
# --------------------------------------------------------------------------- #

async def call_model(prompt: str, config: dict[str, Any], budget: Budget) -> str:
    """One model call, off the event loop thread so candidates can run at once.

    Returns "" on any failure rather than raising: one dead candidate should not
    end a run that has two healthy ones.
    """
    exhausted = budget.exhausted()
    if exhausted:
        print(f"[call_model] refusing: {exhausted} budget exhausted")
        return ""
    budget.spend_call()

    model_cfg = config["model"]

    def _post() -> str:
        r = requests.post(
            model_cfg["provider_url"],
            json={"model": model_cfg["name"], "prompt": prompt, "stream": False},
            timeout=model_cfg["request_timeout_s"],
        )
        r.raise_for_status()
        return r.json().get("response", "")

    try:
        return await asyncio.to_thread(_post)
    except Exception as e:                                     # noqa: BLE001
        print(f"[call_model] {e}")
        traceback.print_exc()
        return ""


def extract_code(text: str) -> str:
    """Pull the first fenced block out of a model response, or return it whole."""
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            block = parts[1]
            if "\n" in block:
                first, rest = block.split("\n", 1)
                # Drop a language tag like ```python
                return rest if first.strip().isalpha() or not first.strip() else block
            return block
    return text


# --------------------------------------------------------------------------- #
# Candidates
# --------------------------------------------------------------------------- #

async def generate_candidate(index: int, strategy: str, contract: dict[str, Any],
                             context: str, config: dict[str, Any],
                             run_dir: Path, budget: Budget) -> Path | None:
    """Generate one candidate under one strategy, in its own call.

    Its own call is the point.  Asking one session for three variations gives you
    three things that saw each other; separate calls at least remove that
    coupling.  They remain correlated through the shared model and prompt family,
    which is a limitation to measure rather than to wave away.
    """
    prompt = (
        f"You are solving one task. Approach: {strategy}\n\n"
        f"Objective: {contract['objective']}\n\n"
        f"Hard constraints:\n" + "\n".join(f"- {c}" for c in contract["hard_constraints"]) + "\n\n"
        f"Acceptance checks:\n" + "\n".join(f"- {c}" for c in contract["acceptance_checks"]) + "\n\n"
        f"Context:\n{context}\n\n"
        "Return only the complete implementation in a single fenced code block."
    )
    text = await call_model(prompt, config, budget)
    if not text.strip():
        print(f"  candidate {index} produced nothing")
        return None

    path = run_dir / "candidates" / f"candidate_{index}.py"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(extract_code(text), encoding="utf-8")
    except Exception as e:                                     # noqa: BLE001
        print(f"[generate_candidate] could not write candidate {index}: {e}")
        traceback.print_exc()
        return None

    write_json(run_dir / "candidates" / f"candidate_{index}.meta.json",
               {"index": index, "strategy": strategy, "generated_at": now_iso(),
                "chars": len(text)})
    return path


async def generate_all(contract: dict[str, Any], context: str, config: dict[str, Any],
                       run_dir: Path, budget: Budget) -> list[Path]:
    """Generate every candidate concurrently.

    Concurrency here is not a performance flourish: it is what keeps the
    candidates from being generated in sequence in a shared context, which would
    make the second and third react to the first.
    """
    strategies = config["candidates"]["strategies"][: config["candidates"]["count"]]
    tasks = [generate_candidate(i, s, contract, context, config, run_dir, budget)
             for i, s in enumerate(strategies)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    paths: list[Path] = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            print(f"[generate_all] candidate {i} raised: {r}")
        elif r is not None:
            paths.append(r)
    return paths


async def select_best(candidates: list[Path], config: dict[str, Any], workdir: Path,
                      run_dir: Path) -> tuple[Path | None, list[validators.TierResult]]:
    """Validate every candidate and keep the one that gets furthest down the hierarchy."""
    best_path: Path | None = None
    best_tiers: list[validators.TierResult] | None = None

    for path in candidates:
        tiers = await validators.validate(config, workdir, path)
        summary = validators.summarize(tiers)
        print(f"  {path.name}: passed={summary['passed']} failed={summary['failed']}")
        write_json(run_dir / "candidates" / f"{path.stem}.validation.json", summary)
        if validators.is_better(tiers, best_tiers):
            best_path, best_tiers = path, tiers

    return best_path, (best_tiers or [])


# --------------------------------------------------------------------------- #
# The bounded repair loop
# --------------------------------------------------------------------------- #

async def repair_loop(best: Path, best_tiers: list[validators.TierResult],
                      contract: dict[str, Any], config: dict[str, Any],
                      workdir: Path, run_dir: Path,
                      budget: Budget) -> tuple[Path, list[validators.TierResult], str]:
    """Repair against evidence, keep only improvements, and stop for a stated reason.

    Returns (best artifact, its validation, the reason the loop stopped).  The
    reason is a required output, not a nicety: "we stopped because the same
    failure fingerprint came back twice" and "we stopped because everything
    passes" are very different claims about the result.
    """
    log = run_dir / "repair-log.jsonl"
    max_iters = config["repair"]["max_iterations"]
    plateau_limit = config["repair"]["stop_on_plateau_after"]

    seen_fingerprints: set[str] = set()
    plateau = 0

    for iteration in range(1, max_iters + 1):
        summary = validators.summarize(best_tiers)

        if summary["all_hard_gates_pass"]:
            return best, best_tiers, "all_gates_pass"

        fingerprint = summary["fingerprint"]
        if config["repair"]["stop_on_repeated_fingerprint"] and fingerprint in seen_fingerprints:
            return best, best_tiers, "repeated_failure_fingerprint"
        seen_fingerprints.add(fingerprint)

        exhausted = budget.exhausted()
        if exhausted:
            return best, best_tiers, f"budget_exhausted:{exhausted}"

        # Preserve the best-known candidate BEFORE editing anything. This is what
        # makes a rollback possible, and it is the step people skip.
        preserved = run_dir / "candidates" / f"best_before_iter_{iteration}.py"
        try:
            shutil.copy2(best, preserved)
        except Exception as e:                                 # noqa: BLE001
            print(f"[repair_loop] could not preserve best candidate: {e}")
            traceback.print_exc()
            return best, best_tiers, "preserve_failed"

        failing = "\n\n".join(
            f"[{t.name}] {r.command}\nexit={r.exit_code}\n{(r.stderr or r.stdout)[-2000:]}"
            for t in best_tiers if t.ran and not t.passed for r in t.results if not r.passed
        )
        prompt = (
            f"This implementation fails a check. Fix the smallest plausible cause.\n\n"
            f"Objective: {contract['objective']}\n\n"
            f"Current implementation:\n```\n{best.read_text(encoding='utf-8')}\n```\n\n"
            f"Failing checks:\n{failing}\n\n"
            "First name the single most likely cause in one sentence, then return the "
            "complete corrected implementation in one fenced code block. Change as "
            "little as possible."
        )
        text = await call_model(prompt, config, budget)
        if not text.strip():
            return best, best_tiers, "model_returned_nothing"

        candidate = run_dir / "candidates" / f"repair_{iteration}.py"
        candidate.write_text(extract_code(text), encoding="utf-8")

        new_tiers = await validators.validate(config, workdir, candidate)
        improved = validators.is_better(new_tiers, best_tiers)

        append_jsonl(log, {
            "iteration": iteration,
            "at": now_iso(),
            "fingerprint_before": fingerprint,
            "fingerprint_after": validators.failure_fingerprint(new_tiers),
            "before": validators.summarize(best_tiers)["failed"],
            "after": validators.summarize(new_tiers)["failed"],
            "kept": improved,
            "elapsed_s": round(budget.elapsed_s(), 1),
            "model_calls": budget.model_calls,
        })

        if improved:
            best, best_tiers = candidate, new_tiers
            plateau = 0
            print(f"  iteration {iteration}: improved, kept")
        else:
            # Rejected. The preserved copy is still the best-known state, so
            # nothing was lost by trying, which is the whole reason to preserve.
            plateau += 1
            print(f"  iteration {iteration}: no improvement, discarded "
                  f"(plateau {plateau}/{plateau_limit})")
            if plateau >= plateau_limit:
                return best, best_tiers, "plateau"

    return best, best_tiers, "max_iterations"


# --------------------------------------------------------------------------- #
# Reporting and handoff
# --------------------------------------------------------------------------- #

def write_evidence_report(run_dir: Path, contract: dict[str, Any],
                          tiers: list[validators.TierResult], stop_reason: str,
                          budget: Budget) -> None:
    """The final report, written so that a reader can tell claims from evidence.

    Notice what is not here: any statement that the task succeeded because the
    model said so.  Acceptance comes from the validators or it is marked
    unresolved.
    """
    summary = validators.summarize(tiers)
    satisfied = summary["all_hard_gates_pass"]
    lines = [
        f"# Final Evidence Report: {contract['task_id']}",
        "",
        f"- Generated: {now_iso()}",
        f"- Charter version: {contract.get('charter_version')}",
        f"- Loop stopped because: **{stop_reason}**",
        f"- Budget consumed: {budget.model_calls} model calls, "
        f"{round(budget.elapsed_s(), 1)}s wall clock",
        "",
        "## What was requested",
        "",
        contract["objective"],
        "",
        "## Checks passed",
        "",
        *([f"- {n}" for n in summary["passed"]] or ["- (none)"]),
        "",
        "## Checks failed",
        "",
        *([f"- {n}" for n in summary["failed"]] or ["- (none)"]),
        "",
        "## Checks NOT run",
        "",
        "These were not executed, so they are not evidence of anything.",
        "",
        *([f"- {n}" for n in summary["not_run"]] or ["- (none)"]),
        "",
        "## Assumptions",
        "",
        *([f"- {a}" for a in contract.get("assumptions", [])] or ["- (none recorded)"]),
        "",
        "## Unresolved",
        "",
        *([f"- {u}" for u in contract.get("unknowns", [])] or ["- (none recorded)"]),
        "",
        "## Does this satisfy the task contract?",
        "",
        ("**Yes.** Every configured hard gate passed." if satisfied else
         "**Not established.** At least one gate failed or was never run. "
         "Do not record this as done."),
        "",
    ]
    try:
        (run_dir / "final-evidence-report.md").write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:                                     # noqa: BLE001
        print(f"[write_evidence_report] {e}")
        traceback.print_exc()


def write_handoff(run_dir: Path, contract: dict[str, Any],
                  tiers: list[validators.TierResult], stop_reason: str,
                  best: Path | None) -> None:
    """State durable enough for a session with none of this context to continue.

    The test for this file is cold-start: close everything, open a new session,
    hand it only this, and see whether it asks you a question it should have been
    able to answer from the file.  Every such question is a missing section.
    """
    summary = validators.summarize(tiers)
    lines = [
        f"# HANDOFF: {contract['task_id']}",
        "",
        f"- Charter version: {contract.get('charter_version')}",
        f"- Created: {now_iso()}",
        f"- Owner / current claim: (write your claim mechanism's holder here)",
        "",
        "## Objective",
        "",
        contract["objective"],
        "",
        "## Current state",
        "",
        f"Loop stopped: **{stop_reason}**. "
        + ("All configured gates pass." if summary["all_hard_gates_pass"]
           else f"Still failing: {', '.join(summary['failed']) or 'unknown'}."),
        "",
        "## Artifacts",
        "",
        f"- Best implementation: `{best}`" if best else "- No artifact produced",
        f"- Validation: `{run_dir / 'validation-results.json'}`",
        f"- Repair log: `{run_dir / 'repair-log.jsonl'}`",
        "",
        "## Validators run",
        "",
        f"- Passed: {', '.join(summary['passed']) or 'none'}",
        f"- Failed: {', '.join(summary['failed']) or 'none'}",
        f"- Not run: {', '.join(summary['not_run']) or 'none'}",
        "",
        "## Approaches that failed, do not repeat",
        "",
        "(read `repair-log.jsonl`; every entry with \"kept\": false is one of these)",
        "",
        "## Next safe action",
        "",
        ("Review and accept, or run the next task." if summary["all_hard_gates_pass"]
         else "Diagnose the failing check named above before editing anything."),
        "",
        "## Human decisions required",
        "",
        "- (list anything the loop could not settle on its own)",
        "",
        f"## Acceptance status: {'MEETS CONTRACT' if summary['all_hard_gates_pass'] else 'NOT ESTABLISHED'}",
        "",
    ]
    try:
        (run_dir / "HANDOFF.md").write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:                                     # noqa: BLE001
        print(f"[write_handoff] {e}")
        traceback.print_exc()


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

async def orchestrate(args: argparse.Namespace) -> int:
    workdir = Path(args.workdir).resolve()
    config = load_json(Path(args.config))

    print("1. charter gate")
    charter = charter_gate(workdir, config)

    run_dir = workdir / config["paths"]["runs_dir"] / args.task_id
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "charter-reference.json", {
        "charter_version": charter.get("charter_version"),
        "content_hash": charter.get("content_hash"),
        "accepted_at": charter.get("accepted_at"),
    })

    budget = Budget(
        wall_clock_s=config["budgets"]["wall_clock_s"],
        max_model_calls=config["budgets"]["max_model_calls"],
        started_at=time.monotonic(),
    )

    print("2. task contract")
    contract_path = run_dir / "task-contract.json"
    if not contract_path.exists():
        write_json(contract_path, build_task_contract(args.task_id, args.objective, charter))
    contract = approve_contract(contract_path)

    print("3. context pack")
    context_path = run_dir / "context-pack.md"
    if not context_path.exists():
        context_path.write_text(
            "# Context pack\n\n"
            "Bounded on purpose. Put only what this task needs here: the relevant "
            "files, the interface being implemented, the constraints. Everything "
            "you add competes for the same attention budget.\n",
            encoding="utf-8")
    context = context_path.read_text(encoding="utf-8")

    print("4. candidates")
    candidates = await generate_all(contract, context, config, run_dir, budget)
    if not candidates:
        print("[orchestrate] no candidates generated; stopping.")
        return 1
    print(f"  generated {len(candidates)}")

    print("5. select")
    best, best_tiers = await select_best(candidates, config, workdir, run_dir)
    if best is None:
        print("[orchestrate] no candidate could be validated; stopping.")
        return 1
    print(f"  best: {best.name}")

    print("6. repair")
    best, best_tiers, stop_reason = await repair_loop(
        best, best_tiers, contract, config, workdir, run_dir, budget)
    print(f"  stopped: {stop_reason}")

    print("7. regression")
    final_tiers = await validators.validate(config, workdir, best)
    validators.write_results(run_dir / "validation-results.json", final_tiers)

    print("8. report and handoff")
    write_evidence_report(run_dir, contract, final_tiers, stop_reason, budget)
    write_handoff(run_dir, contract, final_tiers, stop_reason, best)

    summary = validators.summarize(final_tiers)
    write_json(run_dir / "summary.json", {
        "task_id": args.task_id,
        "stop_reason": stop_reason,
        "all_hard_gates_pass": summary["all_hard_gates_pass"],
        "passed": summary["passed"],
        "failed": summary["failed"],
        "not_run": summary["not_run"],
        "model_calls": budget.model_calls,
        "elapsed_s": round(budget.elapsed_s(), 1),
        "finished_at": now_iso(),
    })

    print(f"\nrun artifacts in {run_dir}")
    return 0 if summary["all_hard_gates_pass"] else 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded deliberation loop over one local model.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--workdir", default=".")
    parser.add_argument("--config", default="config/loop-config.json")
    args = parser.parse_args()
    try:
        return asyncio.run(orchestrate(args))
    except SystemExit:
        raise
    except KeyboardInterrupt:
        print("\n[main] interrupted; run artifacts so far are preserved.")
        return 130
    except Exception as e:                                     # noqa: BLE001
        print(f"[main] unhandled: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
