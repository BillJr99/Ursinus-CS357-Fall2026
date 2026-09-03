# Personal Deliberation Harness: starter files

Starter scaffolding for the **Personal Deliberation Harness** pathway of the
[Local Agent Lab, Direction 5](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/LocalAgent/Direction5).

This is a starting point, not a solution.  It runs, and it is deliberately
missing the parts that make it yours.

```
deliberation-harness/
|-- config/
|   |-- charter-schema.json   the machine-readable half of your charter
|   |-- energy-profiles.json  token-to-carbon rates, and the training term
|   `-- loop-config.json      every budget and threshold the controller obeys
`-- tools/
    |-- deliberate_loop.py    the controller: gates, candidates, repair, reports
    |-- token_meter.py        what a run actually cost, measured not estimated
    `-- validators.py         running external checks and ranking their results
```

Your skills go in `.agents/skills/<name>/SKILL.md`, which **both** opencode and
pi discover from a project directory.  See the assignment for the full layout.

## Why the controller is Python and not a SKILL.md

A `SKILL.md` can describe this whole workflow, and it cannot enforce any of it.
It cannot guarantee that three candidates were generated in three separate
calls, that the best one was copied aside before a repair edited it, that a
wall-clock budget was actually checked, or that the run stopped for a stated
reason rather than because the model announced it was done.  Each of those is a
line of code here, and the difference between "the instructions say to do this"
and "the process cannot proceed otherwise" is most of what this pathway is
about.

## Quick start

```bash
pip install requests
mkdir -p my-harness && cd my-harness
cp -r /path/to/deliberation-harness/* .

# 1. Build a charter with your charter-builder skill, then accept it by hand.
#    The controller refuses to run until charter.json has "accepted": true.

# 2. Run one task.
python tools/deliberate_loop.py \
  --task-id fizzbuzz \
  --objective "Write fizzbuzz(n) returning a list of strings for 1..n"
```

Everything lands in `runs/<task-id>/`: the candidates and their validation, the
repair log, the evidence report, and the handoff.

## What to change, and where

| You want to change | Edit |
|---|---|
| How many candidates, and their strategies | `config/loop-config.json` → `candidates` |
| Which checks run, and in what order | `config/loop-config.json` → `validators.tiers` |
| Repair iterations and stopping | `config/loop-config.json` → `repair` |
| Budgets, including the token budget | `config/loop-config.json` → `budgets` |
| Carbon rates, training totals, and the lifetime-request denominators | `config/energy-profiles.json` |
| What questions the charter asks | your `charter-builder/SKILL.md` |
| How results are ranked and compared | `tools/validators.py` → `rank_key`, `is_better` |
| What a repair prompt says | `tools/deliberate_loop.py` → `repair_loop` |

Nothing that matters is hardcoded in the Python.  If you find yourself editing
a number in `deliberate_loop.py`, that number probably belongs in the JSON.

## Measuring what a run cost

`tools/token_meter.py` reads `prompt_eval_count` and `eval_count` off every
Ollama response, so the token counts in `summary.json` and the evidence report
are measured rather than estimated. When those counters are missing it falls
back to `tiktoken` and sets `measured` to False, and that flag travels all the
way into the report, because an estimate presented as a measurement is worse
than no number at all.

The conversion to grams has two terms and keeps them apart:

```
total = operational + training_share
        |             |
        |             `- the model's one-time training cost, divided by an
        |                assumed number of lifetime requests
        `- this request's own energy, from measured tokens
```

The denominator in that second term is an assumption, not a measurement, and it
is the largest source of uncertainty in the whole calculation. Run your numbers
under the shipped denominator and under one you argue for yourself, and report
both. With the denominators in the shipped config, the offline profile's
training share is larger than its operational cost, which is worth understanding
before you describe local inference as free.

## Two things the starter does not decide for you

**Tie-breaking among equally-failing candidates.**  `rank_key` ranks by how far
down the hierarchy a candidate got before failing.  When two candidates fail at
the *same* tier, they tie, and the incumbent is kept.  Whether that is right for
your task is a design decision you should make deliberately and defend: you
could break the tie on the number of failing checks, on the diversity of the
approach, or by keeping the shorter artifact.  Say what you chose.

**Execution order versus severity order.**  The tier list is both "what runs
first" and "what counts as more serious," and those are not always the same
thing.  Acceptance tests sit above compilation in severity, and running them
first means a candidate that does not compile and a candidate that compiles but
answers wrong both fail at the same tier and tie.  Moving the cheap structural
checks earlier differentiates them and changes what "further down the hierarchy"
means.  There is a real trade here.  Pick one, and explain the consequence.

## Safety

The controller never deletes, overwrites outside its run directory, pushes, or
publishes.  `confirm_irreversible()` is there for when you add something that
does; route it through that function rather than around it, and note that
accepting the charter is not the same as confirming a specific irreversible
action.
