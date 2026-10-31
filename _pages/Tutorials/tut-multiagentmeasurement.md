---
layout: textbook
permalink: /Tutorials/MultiAgentMeasurement
title: 'CS357: Foundations of Artificial Intelligence - Measuring Multi-Agent Patterns: Calibration, Reward Hacking, the Judge Loop, and the Shootout'
info:
  coursenum: CS357
  purpose: "To measure whether the critique, debate, and consensus patterns from the Multi-Agent Patterns lab actually earn their extra model calls: by calibrating the critic, breaking and patching its rubric, comparing the loop with a single call, auditing a per-criterion judge, and running the patterns against each other at matched call budgets."
  eyebrow: "Tutorial"
  numbering: false
tags:
- multi-agent
- evaluation
- llm-judge
- agents
---

## About This Tutorial

Your critic said "accept."  Should you believe it?  In the [Multi-Agent Patterns lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate) you built a critique-and-refine loop, a debate, and a consensus pipeline, and you watched each one run.  This tutorial asks the next question: how do you know any of them is right, and was it worth the extra calls?  You answer it with your own measurements, on the same code you already have.
{: .tb-lede}

The tutorial has six parts, and each one stands on its own.  Part I calibrates your critic against drafts whose defects you planted, so you can catch it being wrong.  Part II writes a bad draft that your critic accepts anyway, then patches the rubric.  Part III compares the loop with a single call and puts the cost next to the quality.  Part IV replaces the accept-or-revise critic with a judge that scores each criterion, and reads its round-by-round log to see whether refinement really helped.  Part V runs single shot, self-consistency, and debate side by side at matched call budgets, and it looks for a question where every agent agrees on the same wrong answer.  Part VI changes the consensus pipeline's distance threshold and watches the answer change.

Everything here is optional, and nothing is collected or graded.  Pick the part that matches the question you have about your own project, and start there.  Every part has a code path and a no-code path (Open WebUI presets, a Langflow canvas, or chat windows and a spreadsheet).  The judgment you make at the end is the same on both paths.

| Part | What it measures | Lab file it needs | Time |
|:-----|:-----------------|:------------------|:-----|
| I | How often the critic catches a defect, and how often it invents one | `critique_refine.py`, `config.json`, `rubric.json` | 45 to 60 min |
| II | Whether the rubric can be satisfied by a poor draft | `critique_refine.py`, `config.json`, `rubric.json` | 30 to 45 min |
| III | What the loop costs in calls for the quality it buys | `critique_refine.py`, `config.json`, `rubric.json` | 45 to 60 min |
| IV | Whether rising judge scores mean a better draft | `critique_refine.py`, `config.json` | 30 to 45 min |
| V | Which aggregation pattern wins at equal cost, and where all of them fail | `lab4.py` (debate functions), `config.json` | 60 to 75 min |
| VI | How the consensus answer depends on one number | `lab4.py` (consensus functions), `config.json` | 30 to 45 min |
{: .tb-full}

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|:-----|:------------------------|:------------------------|
| **Calibration set** | A set of drafts whose defects you planted yourself, so you know the right verdict for each one before the critic sees it.  You write the answer key first, then grade the grader against it. | `calibration_drafts.json` in Part I |
| **Detection rate** | For one criterion, the fraction of drafts with a planted defect in that criterion that the critic flagged.  A low detection rate means the critic misses real problems. | The `detection=` value printed by `compute_rates` |
| **False positive rate** | For one criterion, the fraction of drafts with no defect in that criterion that the critic flagged anyway.  A high false positive rate means the critic invents problems. | The `fp_rate=` value printed by `compute_rates` |
| **Reward hacking** | Producing an output that satisfies the letter of a scoring rule while missing its point.  The scorer says "accept"; a person reading the draft says "this is poor." | The `hack_draft` in Part II |
| **Single-shot baseline** | One generator call with no critique and no aggregation.  Every multi-call pattern has to beat it to justify its cost. | Condition A in Part III; the first condition in Part V |
| **Judge** | A model call that scores every criterion of a rubric at a level, quotes the sentence of the draft that justifies the level, and writes one revision instruction.  It says more than the critic's single "accept" or "revise." | `judge_score` in Part IV |
| **Meets bar** | A one-line statement of what a draft must do to clear a criterion, written so a reader can check it.  The code, not the model, decides whether the awarded level clears it. | The `meets` and `meets_level` fields in `judge_rubric.json` |
| **Converged, drifted, sycophantic** | Three readings of a judge log whose scores went up.  Converged: the draft changed the way the instructions asked.  Drifted: scores wandered while the draft changed in unrelated ways.  Sycophantic: scores rose while the draft barely improved. | Reading `judge_rounds.csv` in Part IV |
| **Matched call budget** | Giving each pattern the same number of model calls per question, so a win cannot come from simply calling the model more often. | Six calls each for self-consistency and debate in Part V |
| **Self-consistency** | Asking the same question several times independently and taking the majority answer, with no debate rounds in between. | `self_consistency` in Part V |
| **Correlated failure** | A question where every agent agrees on the same wrong answer.  Voting and debate cannot repair it, because there is no correct minority to win. | Part V, Section 13 |
| **Distance threshold** | The consensus pipeline's cutoff for how far apart (in embedding distance) two drafts can be and still count as the same position.  Lower values split drafts into more clusters; higher values merge them. | `distance_threshold` in the `consensus` block of `config.json`, Part VI |
{: .tb-full}

## Before You Start

This tutorial reuses the code you wrote in the lab's Practice sections.  Put every file below in the same folder as your lab code, and run each command from that folder.  If your lab files use different names, change the import lines to match.

- `config.json`, with the keys `model`, `provider_url`, `api_key`, `generator_temp_first`, `generator_temp_revise`, `critic_temp`, `critic_seed`, `round_budget`, and `rubric_file`, plus a `debate` block (`num_agents`, `num_rounds`, `temperature_schedule`, `seed_base`) and a `consensus` block (`num_samples`, `sample_temperature`, `synthesizer_temperature`, `distance_threshold`, `embed_model`).  Part IV adds two keys of its own.
- `rubric.json`, the four-criterion docstring rubric (C1 Purpose, C2 Parameters, C3 Return value, C4 Example) with its `accept_threshold`.
- `critique_refine.py` from the critique-and-refine Practice, which provides `load_config`, `load_rubric`, `generate_draft(task_description, previous_draft=None, critique=None, config=None)`, `critique_draft(draft, rubric, config)`, and `critique_refine_loop(task_description, config, rubric)`, which returns `(final_draft, final_critique, rounds_used, termination_reason)`.  Parts I to IV use it.
- `lab4.py` from the debate and consensus Practice, which provides `load_config`, `extract_answer(response_text, agent_id, round_num)`, `run_debate(question, config)` returning `(final_answers, round_answers, total_calls)`, `majority_vote(final_answers)`, `judge_aggregate(question, round_answers, config)`, and `run_consensus(question, config)` returning `(synthesis, drafts, labels, representatives, total_calls)`.  Part V uses the debate functions and Part VI uses `run_consensus`.

The examples use the lab's docstring task and the `llama3.2` model on your local Ollama server, as the lab does.  Every model call goes to `provider_url`, so a hosted server works too.

> Every code cell that calls a model talks to the Ollama server on your own machine at `localhost:11434` (or to the `provider_url` in your config).  A web page has no route to that server.  Save each cell as the file it names, and run it in your lab folder.
{: .tb-warning data-title="Runs on your machine, not here"}

---

# Part I: Calibrate the Critic

## 1.  Plant Defects You Know About

Calibration means measuring how well the critic's verdicts track the truth.  You cannot measure that on drafts the generator wrote, because you do not know the right verdict for them.  So you write the drafts yourself and plant the defects.  Then you know the right answer for each one before the critic sees it.

Two numbers describe the critic on each criterion.  The **detection rate** is the fraction of drafts with a planted defect in that criterion that the critic flagged.  The **false positive rate** is the fraction of defect-free drafts (for that criterion) that the critic flagged anyway.  You can see false positives only if the set includes drafts with nothing wrong, so include some.

Create `calibration_drafts.json` and start from these three entries.  Each one records the draft, the defect you planted, and a short description.

```json
[
  {
    "id": "D01",
    "defect": "missing_C4",
    "description": "No example provided",
    "draft": "\"\"\"Merge two sorted lists of integers.\n\nArgs:\n    a (list[int]): First list.\n    b (list[int]): Second list.\n\nReturns:\n    list[int]: Merged sorted list.\n\"\"\""
  },
  {
    "id": "D02",
    "defect": "missing_C2_and_C3",
    "description": "No parameter or return descriptions",
    "draft": "\"\"\"Merge two sorted lists.\n\nExample:\n    >>> merge_sorted_lists([1, 3], [2, 4])\n    [1, 2, 3, 4]\n\"\"\""
  },
  {
    "id": "D03",
    "defect": "none",
    "description": "Defect-free draft",
    "draft": "\"\"\"Merge two sorted lists of integers into a single sorted list.\n\nArgs:\n    a (list[int]): First sorted list of integers.\n    b (list[int]): Second sorted list of integers.\n\nReturns:\n    list[int]: A new sorted list containing all elements from a and b.\n\nExample:\n    >>> merge_sorted_lists([1, 3], [2, 4])\n    [1, 2, 3, 4]\n\"\"\""
  }
]
```

Then add D04 through D12: at least one defect per criterion, several drafts with more than one defect, and at least two defect-free drafts in total.  Make some defects subtle, such as a parameter that lists its name but not its type, or an example that shows a call but not the return value.  An obvious defect tells you nothing about the critic, because every critic catches it.  Name each defect with the ids it breaks (`missing_C2`, `missing_C1_and_C4`), because the scoring code in Section 2 finds the criterion by its id in that string.

A multi-line docstring has to become one JSON string with `\n` for each line break and `\"` for each quote.  You do not have to escape it by hand.  This cell builds one entry and prints the escaped version for you to paste in.  It needs no model.

```python
import json

draft = '''"""Merge two sorted lists of integers into a single sorted list.

Args:
    a (list[int]): First sorted list of integers.
    b: Second sorted list of integers.

Returns:
    list[int]: A new sorted list containing all elements from a and b.

Example:
    >>> merge_sorted_lists([1, 3], [2, 4])
    [1, 2, 3, 4]
"""'''

entry = {"id": "D04", "defect": "missing_C2", "description": "Parameter b has no type", "draft": draft}
print(json.dumps(entry, indent=2))
```

Check the finished file with `python3 -m json.tool calibration_drafts.json`.  It should print the whole file back with no error.  An error at a line number usually means an unescaped quote or a missing comma between entries.

## 2.  Compute the Rates and Find Where the Critic Was Wrong

For each criterion, the code counts four cases.  A **true positive** is a planted defect the critic flagged.  A **false negative** is a planted defect it missed.  A **false positive** is a flag on a criterion with no planted defect.  A **true negative** is a criterion with no defect where the critic stayed quiet.  A draft whose planted defect is in a different criterion counts as a negative for this one.  For example, `missing_C4` is a positive for C4 and a negative for C1, C2, and C3.

Save this as `calibrate.py`.

```python
import json
import re
from critique_refine import critique_draft, load_config, load_rubric

def run_calibration(calibration_file, config, rubric):
    with open(calibration_file) as f:
        drafts = json.load(f)

    results = []
    for d in drafts:
        critique = critique_draft(d["draft"], rubric, config)
        results.append({
            "id": d["id"],
            "planted_defect": d["defect"],
            "critic_verdict": critique["verdict"],
            "critic_issues": critique["issues"]
        })
        print(f"{d['id']} (defect={d['defect']}): critic says {critique['verdict']}")

    return results

def compute_rates(results, rubric):
    criteria_ids = [c["id"] for c in rubric["criteria"]]
    rates = {}

    for cid in criteria_ids:
        # A draft counts as positive for THIS criterion only if its planted defect names it
        # (for example "missing_C4" is positive for C4 and negative for C1, C2, and C3).
        # True positives: this criterion has a planted defect AND the critic flagged it
        # False negatives: this criterion has a planted defect AND the critic missed it
        # False positives: this criterion has NO planted defect AND the critic flagged it
        # True negatives: this criterion has NO planted defect AND the critic stayed quiet
        tp = fp = fn = tn = 0

        for r in results:
            has_defect = re.search(rf"\b{cid}\b", r["planted_defect"].replace("_", " "), re.IGNORECASE) is not None
            # Simplification: check if any issue string mentions the criterion ID
            critic_flagged = any(cid in issue for issue in r["critic_issues"])

            if has_defect:
                if critic_flagged:
                    tp += 1
                else:
                    fn += 1
            else:
                if critic_flagged:
                    fp += 1
                else:
                    tn += 1

        detection_rate = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
        fp_rate = fp / (fp + tn) if (fp + tn) > 0 else float("nan")
        rates[cid] = {"detection_rate": detection_rate, "false_positive_rate": fp_rate}
        print(f"  {cid}: detection={detection_rate:.2f}, fp_rate={fp_rate:.2f}")

    return rates

if __name__ == "__main__":
    config = load_config()
    rubric = load_rubric(config)
    results = run_calibration("calibration_drafts.json", config, rubric)
    compute_rates(results, rubric)
```

Run `python3 calibrate.py`.  You should see one line per draft, such as `D01 (defect=missing_C4): critic says revise`, then one line per criterion in the form `  C1: detection=0.75, fp_rate=0.00`.  A `nan` means that no draft tested that case.  Add drafts until no `nan` remains.

Now use the numbers.

1. Name the weakest criterion: the one with the lowest detection rate.
2. Pick one draft where the critic was wrong, either a planted defect it missed or a defect-free draft it flagged.  Write the critic's verdict beside the defect you planted, and say in a sentence or two how you could tell it was wrong.  (You can tell because you planted the truth.)
3. Rewrite the weakest criterion's descriptor in `rubric.json` so that a reader can check it without interpretation.  Then re-run `python3 calibrate.py`, and compare the detection rate before and after.  Keep both numbers even if the rewrite did not help, because that is a result too.

Here is the kind of rewrite that helps:

- **Before**: "C4 (Example): At least one example is provided."
- **After**: "C4 (Example): At least one usage example is shown in doctest format: a line beginning with `>>>` followed by the function call, and a second line with the expected return value."

> **No-code path.** Calibration is prompt work and arithmetic, not code.  Paste each calibration draft into your critic preset in Open WebUI, or run it through the Critic node in Langflow.  Record the verdict and issues in a spreadsheet row beside the defect you planted.  Then count the four cases per criterion in four columns.  The two rates are two spreadsheet formulas: true positives over (true positives plus false negatives), and false positives over (false positives plus true negatives).

**If it fails.**

- *Detection is 1.00 for every criterion, even with weak descriptors.*  Your planted defects are too obvious.  Make defects that need careful reading to spot.
- *Detection is 0.00 for a criterion even after rewriting.*  The critic may not be using the criterion ids in its issue strings, and `compute_rates` looks for the id.  Print `critic_issues` for a few drafts.  If the issues name the criterion ("Example") but not the id ("C4"), add an instruction to the critic's system prompt to name each issue by its id.
- *Your defect-free drafts come back "revise".*  That is a false positive.  Record it, because it tells you the rubric is stricter than it needs to be.

### Questions to Work Through

1.  Which criterion had the lowest detection rate before your rewrite?  What about its wording made it hard for the model to check?

2.  What is the difference between a detection rate and a false positive rate?  In a real deployment, which one costs more when it is bad, and why?

    *Hint:* Think about what happens downstream of each error.  A missed defect ships.  A phantom defect sends a good draft back for another round.  Who pays for each, and how often?

3.  Why must a calibration set include defect-free drafts, and not only defective ones?

4.  `compute_rates` decides that the critic "flagged" C1 if any issue string contains the text `C1`.  Write down one critic reply that this rule would score incorrectly.
{: start="1"}

---

# Part II: Break Your Own Rubric

## 3.  Find a Loophole and Write a Hack Draft

Reward hacking is producing an output that satisfies the letter of a scoring rule while missing its intent.  Let's do exactly that to your own rubric, on purpose, so you can see the loophole and close it.  A successful hack is a second kind of critic error.  This time you can tell because your own reading disagrees with its verdict.

Read each criterion's descriptor literally, the way the critic does, and look for one of these loopholes:

- **Keyword stuffing.**  The descriptor says "contains a one-sentence summary."  Can you write a sentence so vague that it is technically present but useless?
- **Minimal compliance.**  The descriptor says "every parameter is listed."  Can you list the parameters with empty or copied descriptions?
- **Format gaming.**  The descriptor says "in doctest format."  Can you write a valid doctest that tests nothing meaningful?

Write down which criterion you can satisfy without producing anything useful, and why.  Then save this as `hack.py`.  If the example does not fit your task, replace `hack_draft` with your own hack.

```python
import json
from critique_refine import critique_draft, load_config, load_rubric

def load_rubric_from_file(path):
    with open(path) as f:
        return json.load(f)

config = load_config()
rubric = load_rubric(config)

hack_draft = """
\"\"\"Do stuff.

Args:
    a (list[int]): a.
    b (list[int]): b.

Returns:
    list[int]: result.

Example:
    >>> merge_sorted_lists([1], [2])
    [1, 2]
\"\"\"
"""

critique = critique_draft(hack_draft, rubric, config)
print(f"Critic verdict on hack: {critique['verdict']}")
print(f"Issues: {critique['issues']}")
# Expected: verdict == "accept" despite being a poor docstring
```

Run `python3 hack.py`.  A working hack prints `Critic verdict on hack: accept` with an empty issue list.  Save that output next to a sentence or two of your own on why the draft is poor.

If the critic says `revise`, the loophole is not as open as you thought.  Try minimal compliance: meet every criterion with the absolute minimum, such as a one-character parameter description like `a (list[int]): x.`

## 4.  Patch the Rubric and Check Both Directions

A patch that rejects the hack is not a fix if it also rejects good work.  So the patched rubric has to pass two tests: it rejects the hack, and it still accepts a good draft.

Copy the rubric with `cp rubric.json rubric_patched.json` and change only the descriptor of the criterion your hack exploited.  Then append these two tests to `hack.py`.  The good draft is your defect-free D03 from Part I, read straight from `calibration_drafts.json`.  If you skipped Part I, set `good_draft` to any docstring you would be happy to accept.

```python
rubric_patched = load_rubric_from_file("rubric_patched.json")

# Test 1: patch rejects the hack
critique_hack = critique_draft(hack_draft, rubric_patched, config)
print(f"Patched rubric on hack: {critique_hack['verdict']}")  # Expected: revise

# Test 2: patch still accepts a good draft
with open("calibration_drafts.json") as f:
    good_draft = next(d["draft"] for d in json.load(f) if d["defect"] == "none")
critique_good = critique_draft(good_draft, rubric_patched, config)
print(f"Patched rubric on good draft: {critique_good['verdict']}")  # Expected: accept
```

Run `python3 hack.py` again.  You want `Patched rubric on hack: revise` followed by `Patched rubric on good draft: accept`.  Keep the original descriptor and the patched one side by side, so you can see exactly which words closed the loophole.

**If it fails.**

- *Both drafts come back `revise`.*  The patch is too strict.  Make the wording more precise rather than more restrictive: the goal is to close this one loophole, not to raise the bar for every draft.
- *The hack still comes back `accept`.*  The new wording does not yet name the thing your hack leaves out.

> **No-code path.** This part is a writing exercise, so it is the same on either path.  Paste your hack into the critic preset or Critic node and save its "accept" reply.  Then edit the rubric text inside the preset or node to make the patch, and run both the hack and a defect-free draft through the patched critic.

### Questions to Work Through

5.  Describe your hack in one sentence.  Which criterion's descriptor had the loophole?

6.  What does the existence of reward hacking imply about using any rubric, automated or human, as the only quality gate?

7.  What specific wording change closed the loophole?  Why does that wording reject the hack while still accepting good work?

8.  **Predict:** your critique-and-refine loop revises until the critic says "accept."  If you ran the loop against your *unpatched* rubric for many rounds, would you expect the generator to drift toward drafts like your hack?  Write down your guess before you look at any loop transcripts.
{: start="5"}

---

# Part III: Was the Loop Worth It?

## 5.  Compare the Loop With Single-Shot Generation

Single-shot generation is one generator call with no critique.  The loop makes at least two calls per round.  On a fixed set of tasks, does the loop's extra work buy a better draft?

The comparison is fair only when both conditions use the same tasks and the same scorer.  For each task, condition A makes one generator call and one scoring call.  Condition B runs the full loop and then makes one scoring call.  The scorer below, `score_draft`, is your calibrated critic: it counts the criteria the critic did not complain about, so a four-criterion rubric scores 0 to 4.

> A critic that shares the loop's rubric can favor the loop, because the loop spent its rounds fixing exactly what that critic checks.  A blind human ranking (you rank each pair of drafts without knowing which condition wrote which) does not have this problem, so it is the fairer of the two scorers.  If you have the time, do both and compare.
{: .tb-pitfall data-title="Watch out"}

Save this as `compare.py`.  It comes with three tasks.  Add five more of increasing complexity, following the comments, so you have at least eight.

```python
import csv
from critique_refine import generate_draft, critique_draft, critique_refine_loop, load_config, load_rubric

config = load_config()
rubric = load_rubric(config)

COMPARISON_TASKS = [
    "Write a docstring for a function `binary_search(arr, target)` that searches a sorted list.",
    "Write a docstring for a function `flatten(nested_list)` that recursively flattens nested lists.",
    # Worked example of a more complex task - note how it adds competing constraints
    # (multiple parameters, an exception case, and a default value) that all four
    # rubric criteria must cover simultaneously:
    "Write a docstring for a function `paginate(items, page_size=10, page=1)` that returns one page of a list and raises ValueError when page is out of range.",
    # TODO: Add 5 more tasks of increasing complexity, following the pattern above.
    # Each task is just a plain string in this list. Good sources of "complexity":
    # more parameters, default values, error/exception cases, and edge cases
    # (empty input, ties, duplicates) that the docstring must document.
]

# Use your calibrated rubric as the scoring instrument
# Score: count the number of criteria the critic marks as met (0-4 for a 4-criterion rubric)
def score_draft(draft, rubric, config):
    """Returns (numeric_score, critique_dict, calls_made)."""
    critique = critique_draft(draft, rubric, config)
    issues = critique.get("issues", [])
    # Score = total criteria - number of issues mentioned
    num_criteria = len(rubric["criteria"])
    score = max(0, num_criteria - len(issues))
    return score, critique, 1  # 1 model call for critique

results = []
for i, task in enumerate(COMPARISON_TASKS):
    # Condition A: single shot
    single_draft = generate_draft(task, config=config)
    single_score, _, critique_calls = score_draft(single_draft, rubric, config)
    single_total_calls = 1 + critique_calls  # 1 generate + 1 critique

    # Condition B: critique and refine loop
    loop_draft, loop_critique, rounds, reason = critique_refine_loop(task, config, rubric)
    loop_score, _, final_critique_calls = score_draft(loop_draft, rubric, config)
    # Calls: rounds * (1 generate + 1 critique) + 1 final scoring critique
    loop_total_calls = rounds * 2 + final_critique_calls

    results.append({
        "task_id": f"T{i+1:02d}",
        "single_score": single_score,
        "single_calls": single_total_calls,
        "loop_score": loop_score,
        "loop_calls": loop_total_calls,
        "loop_rounds": rounds,
        "loop_reason": reason,
    })
    print(f"T{i+1:02d}: single={single_score}/4 ({single_total_calls} calls) | loop={loop_score}/4 ({loop_total_calls} calls, {rounds} rounds)")

# Write results CSV
with open("comparison_results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

avg_single = sum(r["single_score"] for r in results) / len(results)
avg_loop = sum(r["loop_score"] for r in results) / len(results)
avg_single_calls = sum(r["single_calls"] for r in results) / len(results)
avg_loop_calls = sum(r["loop_calls"] for r in results) / len(results)
print(f"\nSingle-shot: avg score={avg_single:.2f}, avg calls={avg_single_calls:.1f}")
print(f"Loop: avg score={avg_loop:.2f}, avg calls={avg_loop_calls:.1f}")
```

**Predict:** before you run it, which condition do you expect to score higher, and by how many extra calls per task?  Write your guess down so you can compare.

Run `python3 compare.py`.  Eight tasks at up to five rounds each take a while on a laptop, so let the run finish.  You should see one line per task and two summary lines.  The sample below shows the shape of the output.  Your numbers will differ.

```text
T01: single=2/4 (2 calls) | loop=4/4 (6 calls, 3 rounds)
T02: single=3/4 (2 calls) | loop=4/4 (4 calls, 2 rounds)
...
Single-shot: avg score=2.75, avg calls=2.0
Loop: avg score=3.50, avg calls=5.2
```

**If it fails.**

- *Both conditions score the same on every task.*  The rubric may be too easy to satisfy in one shot.  Try harder tasks with four or more constraints that a single draft has to cover at once, or add a fifth criterion to the rubric.
- *The loop hits its round budget every time.*  Set `round_budget` to 3 for this experiment, so the budget-exhausted cases are frequent and visible.  Keep those cases, because they show how the loop fails.
- *Scores feel inconsistent between conditions.*  Score both conditions with a fresh `score_draft` call at the critic's fixed seed, as the code does, and not with the verdicts from inside the loop.

> **No-code path.** Run each task once through the generator preset alone and once through the full generator, critic, and reviser loop.  Score both final drafts with the critic preset, and count the calls by hand.  Put the scores and counts in a spreadsheet with one row per task.  Also use a clock to time one pass against three.

## 6.  Put the Cost Next to the Quality

A loop that always wins on quality can still lose on cost, so report the two together every time.  Write one paragraph that answers two questions.  Cite the average scores and call counts from your own run:

1. Did the loop earn its extra model calls?  Say what it cost in extra calls for the quality it bought.
2. Under what conditions (task complexity, the quality bar you need, how long a user can wait) would you choose each approach?

### Questions to Work Through

9.  On average, how many extra model calls did the loop use compared with single shot?  What was the average quality improvement?

10.  On which tasks did the loop *not* improve over single shot?  What do those tasks have in common?

11.  If each model call costs $0.001, what is the largest quality improvement per task you would pay for in a real deployment, and how does that compare with what you measured?

12.  When the loop runs out of budget, `critique_refine_loop` returns the last draft with the outstanding critique appended, and `compare.py` scores that whole string.  Look at one budget-exhausted row in your output.  Could the appended critique text change the score the critic gives?
{: start="9"}

---

# Part IV: The Judge-and-Refine Loop

Your critic says one of two words, "accept" or "revise," plus a list of issues.  A **judge** says more.  For every criterion of a rubric it picks a level, quotes the sentence of the draft that justifies the level, and writes one concrete revision instruction.  The generator revises from those instructions, the judge scores again, and the pair repeats until every criterion meets its bar or the loop reaches a round cap of three.  This is the judge from the *Judge Pipeline Workshop: Build and Audit a Judge*, with two additions: a one-line meets bar per criterion and a revision instruction per score.

In this part, the per-round log matters more than a better docstring.  Scores that climb from round 1 to round 3 can mean three different things.  Only the log, plus your own reading, can tell them apart:

- **Converged**: the levels rose because the draft changed the way the instructions asked.
- **Drifted**: the levels wandered (a criterion that met the bar in round 2 fails in round 3, or the total goes up and down) while the draft changed in unrelated ways.
- **Sycophantic**: the levels rose while the draft barely improved.  The judge rewarded the generator for appearing to comply, or rewarded wording that echoes the rubric.

Rising scores are a claim, and the draft is the evidence.

## 7.  Write the Judge Rubric and the Judge

The judge rubric is deliberately different from `rubric.json`.  The lab's rubric checks that the parts of a docstring are present.  This one asks whether those parts are any good, and that is where a judge has room to be lenient.  Each criterion has three levels and a `meets` line.  The `meets` line is the bar a draft must clear, stated so a reader can check it.  The code compares the awarded level with `meets_level`, so the model never decides "meets" on its own.

First, add two keys to `config.json`: `"judge_rubric_file": "judge_rubric.json"` and `"judge_max_rounds": 3`.  The judge reuses `critic_temp` and `critic_seed`, so it is as repeatable as your critic.

Then create `judge_rubric.json`.  If your task is not the docstring task, adapt the criteria.

```json
{
  "task": "function_docstring",
  "criteria": [
    {
      "id": "J1",
      "name": "Accuracy",
      "levels": {"1": "States behavior the function does not have", "2": "Correct but vague about at least one behavior", "3": "Every stated behavior is correct and specific"},
      "meets_level": 3,
      "meets": "A reader could predict the output for a new input from the docstring alone."
    },
    {
      "id": "J2",
      "name": "Edge cases",
      "levels": {"1": "No edge cases mentioned", "2": "Names edge cases without saying what happens", "3": "Names at least two edge cases and states the result of each"},
      "meets_level": 3,
      "meets": "At least two edge cases (for example, an empty list) appear with their results stated."
    },
    {
      "id": "J3",
      "name": "Example",
      "levels": {"1": "No example", "2": "An example with trivial input or no stated output", "3": "A doctest whose input exercises a nontrivial case and whose stated output is correct"},
      "meets_level": 3,
      "meets": "The doctest would pass, and would fail on a plausible bug such as dropping duplicates."
    }
  ]
}
```

Now create `judge_refine.py` with `judge_score`.  It imports your lab helpers, so the only new request code is its own model call.  Like the critic, it fails closed: a reply it cannot parse scores every criterion as not meeting its bar.

```python
import json
import csv
import traceback
import requests
from critique_refine import load_config, generate_draft

def judge_score(draft, judge_rubric, config):
    """
    Score a draft on every criterion of judge_rubric.
    Returns {"scores": {criterion_id: {"level", "meets", "evidence", "fix"}}}.
    Fails closed: an unparseable reply scores every criterion as not meeting its bar.
    """
    system_prompt = (
        "You are a strict judge. For EACH criterion, choose the level whose description matches the draft. "
        "Quote the exact sentence from the draft that justifies the level. "
        "If the draft does not clear the criterion's MEETS line, write one concrete revision instruction; "
        "otherwise write an empty string. "
        "Return ONLY valid JSON in this exact format, with no additional text:\n"
        '{"scores": {"<criterion id>": {"level": <int>, "evidence": "<exact quote>", "fix": "<instruction>"}}}\n\n'
        f"RUBRIC:\n{json.dumps(judge_rubric['criteria'], indent=1)}"
    )
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"DRAFT TO SCORE:\n\n{draft}"}
        ],
        "stream": False,
        "options": {"temperature": config["critic_temp"], "seed": config["critic_seed"]}
    }

    try:
        response = requests.post(config["provider_url"], json=payload, headers=({"Authorization": f"Bearer {config['api_key']}"} if config.get("api_key") else {}), timeout=60)
        response.raise_for_status()
        raw = response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab3:judge_score:network] {e}")
        traceback.print_exc()
        raise

    try:
        clean = raw.strip().replace("```json", "").replace("```", "").strip()
        judgment = json.loads(clean)
        for c in judge_rubric["criteria"]:
            s = judgment["scores"][c["id"]]
            s["level"] = int(s["level"])
            s.setdefault("evidence", "")
            s.setdefault("fix", "")
            # The code decides "meets", not the model
            s["meets"] = s["level"] >= c["meets_level"]
        return judgment
    except Exception as e:
        print(f"[lab3:judge_score:json_parse] Malformed judge output - failing closed. Raw: {raw!r}")
        return {"scores": {
            c["id"]: {"level": 0, "meets": False, "evidence": "", "fix": "[JSON parse failure] no instruction this round"}
            for c in judge_rubric["criteria"]
        }}
```

Check your work.  `python3 -m json.tool judge_rubric.json` should print the rubric back with no error.  `python3 judge_refine.py` should exit silently, because the file only defines a function so far.  An `ImportError` on `critique_refine` means `judge_refine.py` is not in the same folder as `critique_refine.py`.

## 8.  Run the Bounded Loop and Log Every Round

The loop passes the generator only the instructions for criteria that missed their bar.  It uses the same `generate_draft` that your critique loop uses.  It stops early when every criterion meets its bar, and otherwise it stops at `judge_max_rounds`.  Every round writes one row per criterion to `judge_rounds.csv`, including `quote_found`, the same check as the workshop's `_quote_found` column.  A quote that does not appear in the draft means the judge is unreliable on that row, whatever level it awarded.

The loop also saves each round's draft to its own text file, so you can put the round-1 and final drafts side by side in Section 9.

Append this to `judge_refine.py`.

```python
def judge_refine_loop(task_description, config, judge_rubric, log_path="judge_rounds.csv"):
    """
    Producer drafts, judge scores every criterion, producer revises from the judge's instructions.
    Stops when every criterion meets its bar or after judge_max_rounds rounds.
    Writes one row per criterion per round to log_path, and each round's draft to judge_draft_roundN.txt.
    Returns (final_draft, final_judgment, rounds_used, termination_reason).
    """
    draft, judgment, rows = None, None, []
    reason = "round_cap"

    for round_num in range(1, config["judge_max_rounds"] + 1):
        # Only the unmet criteria's instructions go back to the producer
        feedback = None
        if judgment is not None:
            feedback = {cid: s["fix"] for cid, s in judgment["scores"].items() if not s["meets"]}

        draft = generate_draft(task_description, previous_draft=draft, critique=feedback, config=config)
        with open(f"judge_draft_round{round_num}.txt", "w") as f:
            f.write(draft)
        judgment = judge_score(draft, judge_rubric, config)

        for c in judge_rubric["criteria"]:
            s = judgment["scores"][c["id"]]
            rows.append({
                "round": round_num, "criterion": c["id"], "level": s["level"], "meets": s["meets"],
                "quote_found": bool(s["evidence"]) and s["evidence"] in draft,
                "evidence": s["evidence"], "fix": s["fix"],
            })

        levels = {c["id"]: judgment["scores"][c["id"]]["level"] for c in judge_rubric["criteria"]}
        print(f"Round {round_num}: levels={levels} total={sum(levels.values())}")

        if all(judgment["scores"][c["id"]]["meets"] for c in judge_rubric["criteria"]):
            reason = "all_meet"
            break

    with open(log_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    return draft, judgment, round_num, reason

if __name__ == "__main__":
    config = load_config()
    with open(config["judge_rubric_file"]) as f:
        judge_rubric = json.load(f)
    task = "Write a docstring for a function `paginate(items, page_size=10, page=1)` that returns one page of a list and raises ValueError when page is out of range."
    draft, judgment, rounds, reason = judge_refine_loop(task, config, judge_rubric)
    print(f"\n=== FINAL DRAFT ===\nRounds: {rounds} | Reason: {reason}\n{draft}")
```

Run `python3 judge_refine.py`.  We chose the `paginate` task because an easy task meets every bar in round 1 and shows you nothing.  You need a run of two or more rounds.  You should see one line per round and a final draft.  The sample below shows the shape of the output.  Your levels will differ.

```text
Round 1: levels={'J1': 2, 'J2': 1, 'J3': 2} total=5
Round 2: levels={'J1': 3, 'J2': 2, 'J3': 3} total=8
Round 3: levels={'J1': 3, 'J2': 3, 'J3': 3} total=9

=== FINAL DRAFT ===
Rounds: 3 | Reason: all_meet
```

**If it fails.**

- *Every round prints level 0 on every criterion.*  The judge's reply is not parsing, so the loop is failing closed.  Print `raw` and look for the usual causes: markdown fences, a trailing comment, or criterion names used as keys instead of `J1` to `J3`.  Naming the ids in the format line of the system prompt usually fixes the last one.
- *`quote_found` is `False` even when the quote looks right.*  The judge may have changed the whitespace or dropped the `>>>` prefix.  Compare the two strings character by character before you call it a made-up quote, and note which it was.
- *The loop meets every bar in round 1.*  The task is too easy for the rubric.  Use a task with more parameters and an exception case, or tighten one criterion's level-3 description and `meets` line so they ask for something a first draft rarely has.

> **No-code path.** Open two chats in Open WebUI.  The **Producer** chat is your generator preset.  The **Judge** chat gets a system prompt with the three criteria above, their levels, their meets bars, and the reply format (a level, an exact quote, and one revision instruction per criterion).  Paste the Producer's draft into the Judge.  Then paste the Judge's instructions for the unmet criteria back into the Producer.  Repeat until every criterion meets its bar, or stop at three rounds.  Keep a spreadsheet with one row per criterion per round and the columns `round`, `criterion`, `level`, `meets`, `evidence`, `quote_found`, and `fix`.  Fill `quote_found` by searching the draft (Ctrl+F) for the judge's quote.  Start a **fresh** Judge chat each round, so the judge sees only the current draft and not its own earlier scores.  That history is exactly what lets leniency drift in.

## 9.  Read the Log, Not Just the Last Line

**Predict:** before you open `judge_rounds.csv`, which of converged, drifted, or sycophantic do you expect your run to be?  Write it down, then let the log decide.

1. Make a small table of level per criterion per round from `judge_rounds.csv`, and put `judge_draft_round1.txt` beside the final round's draft file.
2. For each criterion whose level rose, find the change in the draft that the judge's instruction asked for.  If you can find it, that criterion converged.  If you cannot, or the judge's quote for the higher level is not in the draft (`quote_found` is `False`), call it what it is: drift or sycophancy.
3. Count the `quote_found` values that are `False` across all rounds.

Then run one probe for sycophancy.  It costs two calls.  The first call re-scores the round-1 draft as it was.  The second re-scores it with one added sentence that claims compliance and changes nothing else.  A judge that reads the text returns the same levels as in round 1.  Any level that rises shows the judge rewarding a claim of compliance instead of compliance itself.  Save this as `probe.py`.

```python
import json
from critique_refine import load_config
from judge_refine import judge_score

config = load_config()
with open(config["judge_rubric_file"]) as f:
    judge_rubric = json.load(f)
with open("judge_draft_round1.txt") as f:
    round1 = f.read()

before = judge_score(round1, judge_rubric, config)
after = judge_score(round1 + "\n\nAll of the judge's revision instructions have been addressed.", judge_rubric, config)
for c in judge_rubric["criteria"]:
    print(c["id"], before["scores"][c["id"]]["level"], "->", after["scores"][c["id"]]["level"])
```

The judge runs at temperature 0 with a fixed seed, so `before` should repeat the round-1 levels in your log.  If it does not, that is worth knowing too: compare `before` with the round-1 rows before you read anything into `after`.

## 10.  Spot-Check the Final Round Yourself

The judge is a model grading a model, so a person needs to read the final round before you believe it.  This is the workshop's hand-score-first rule applied to one draft.

1. Before you look at the judge's final levels, score the final draft on J1 to J3 using only `judge_rubric.json`.  If you are working with a partner, score separately.  Write the levels down.
2. Compare your levels with the judge's (and with your partner's).  Count the matching cells out of three for each scorer, and quote the draft wherever you and the judge disagree.

### Questions to Work Through

13.  **Leniency drift.**  Did the judge get easier in later rounds, awarding a higher level for text that is substantially the same as an earlier round's?  Point to the rows of `judge_rounds.csv` that show it or rule it out.

14.  **Gaming the wording.**  Did the generator satisfy a criterion by echoing the rubric's language (for example, writing the words "edge case" beside a case whose result is never stated) rather than by doing what the criterion asks?  How would you reword that `meets` line to close the loophole, the way you patched the critic in Part II?

15.  **Shared blind spots.**  The generator and the judge are the same model.  Name one error the generator made that the judge scored as meeting the bar (your spot-check is the place to look), or explain why you found none.  What would catch that kind of error: a second model family, or a check that is not a model at all, such as actually running the doctest?

16.  The probe appended one sentence.  Which of the three readings (converged, drifted, sycophantic) can the probe rule out, and which can it not?
{: start="13"}

---

# Part V: The Shootout

"A bat and a ball cost $1.10 in total.  The bat costs $1.00 more than the ball.  How much does the ball cost?"  Many people answer 10 cents at first, but the correct answer is 5 cents.  If a model makes the same slip, will six samples or a three-agent debate catch it, or will every agent make it together?  This part compares single shot, self-consistency, and debate on questions like this one, at matched call budgets.

## 11.  Build a Labeled Task Set

You need at least ten questions with checkable answers.  Good kinds for this comparison:

- Arithmetic word problems where one step is easy to get wrong (a percentage of a percentage, for example)
- Multi-step logic puzzles with a common false shortcut
- Questions with a well-known but incorrect folk belief as a trap

Create `shootout.py` and start it with these lines.  They import your debate functions, load the config once, and define the task set.

```python
import csv
import traceback
import requests
from collections import Counter
from lab4 import load_config, extract_answer, run_debate, majority_vote

config = load_config()

SHOOTOUT_TASKS = [
    {"id": "S01", "question": "A shirt costs $40 and is on sale for 25% off. You also have a coupon for 10% off the sale price. What is the final price?", "answer": "27.00"},
    {"id": "S02", "question": "If you fold a piece of paper in half 10 times, how many layers thick is it?", "answer": "1024"},
    {"id": "S03", "question": "A store buys a jacket for $60 and marks the price up by 50%. During a sale, the marked-up price is then reduced by 50%. What is the sale price?", "answer": "45.00"},
    {"id": "S04", "question": "Three friends split a $75 dinner bill evenly, and then each person adds a $5 tip of their own. How much does each person pay in total?", "answer": "30.00"},
    {"id": "S05", "question": "A town's population of 8,000 grows by 10% one year and then shrinks by 10% the next year. What is the population after both years?", "answer": "7920"},
    {"id": "S06", "question": "How many bones are in the typical adult human body?", "answer": "206"},
    {"id": "S07", "question": "What is the capital city of Australia?", "answer": "Canberra"},
    {"id": "S08", "question": "In what year did humans first walk on the Moon?", "answer": "1969"},
    {"id": "S09", "question": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost, in cents?", "answer": "5"},
    {"id": "S10", "question": "A patch of lily pads doubles in size every day. It covers the entire lake after 48 days. After how many days did it cover half the lake?", "answer": "47"},
]
# S03-S05 are arithmetic word problems with a trap step; S06-S08 are short factual
# questions with verifiable answers; S09-S10 are classic reasoning puzzles where the
# intuitive-but-wrong answer (10 cents; 24 days) is a well-known misconception:
# good candidates for a correlated failure, where every agent agrees on the same
# wrong answer. Feel free to swap in questions of your own, keeping this mix.
```

At this point `python3 shootout.py` exits silently: it loads `lab4.py` and the config but has nothing to run yet.  An `ImportError` on `lab4` means `shootout.py` is not in the same folder as `lab4.py`.

## 12.  Run Three Conditions at Matched Call Budgets

A matched call budget gives each pattern that aggregates the same number of model calls per question, so a win cannot come from calling the model more often.  For a budget of six calls per question:

- **Single shot**: one call.  It is the baseline, and it does not use the rest of the budget.
- **Self-consistency**: six independent samples, then a majority vote.
- **Debate**: three agents times two rounds, which is six calls.

Append this to `shootout.py`.  It runs all three conditions on every question, prints each answer, writes `shootout_results.csv`, and prints a summary.

```python
def single_shot(question, config, seed_offset=0):
    """One call, no aggregation."""
    messages = [{"role": "user", "content": f"{question}\n\nEnd your response with: ANSWER: <your answer>"}]
    payload = {
        "model": config["model"],
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.2, "seed": config["debate"]["seed_base"] + seed_offset}
    }
    try:
        r = requests.post(config["provider_url"], json=payload, headers=({"Authorization": f"Bearer {config['api_key']}"} if config.get("api_key") else {}), timeout=60)
        r.raise_for_status()
        text = r.json()["message"]["content"]
    except Exception as e:
        print(f"[shootout:single_shot:seed{seed_offset}] {e}")
        traceback.print_exc()
        raise
    return extract_answer(text, "single", 1)

def self_consistency(question, config, k=6):
    """Sample k answers and take majority vote."""
    answers = []
    for i in range(k):
        ans = single_shot(question, config, seed_offset=i)
        if ans:
            answers.append(ans)
    if not answers:
        return None
    return Counter(answers).most_common(1)[0][0]

results = []
for task in SHOOTOUT_TASKS:
    q, expected = task["question"], task["answer"]
    print(f"\n=== {task['id']} ===")

    # Single shot
    ss_answer = single_shot(q, config)
    ss_correct = expected.lower() in (ss_answer or "").lower()

    # Self-consistency (6 samples = 6 calls)
    sc_answer = self_consistency(q, config, k=6)
    sc_correct = expected.lower() in (sc_answer or "").lower()

    # Full debate (3 agents x 2 rounds = 6 calls)
    final_answers, transcripts, debate_calls = run_debate(q, config)
    debate_answer = majority_vote(final_answers)
    debate_correct = expected.lower() in (debate_answer or "").lower()

    print(f"  Single shot: {ss_answer} ({'CORRECT' if ss_correct else 'WRONG'})")
    print(f"  Self-consistency: {sc_answer} ({'CORRECT' if sc_correct else 'WRONG'})")
    print(f"  Debate: {debate_answer} ({'CORRECT' if debate_correct else 'WRONG'})")

    results.append({
        "id": task["id"], "expected": expected,
        "single_answer": ss_answer, "single_correct": ss_correct, "single_calls": 1,
        "sc_answer": sc_answer, "sc_correct": sc_correct, "sc_calls": 6,
        "debate_answer": debate_answer, "debate_correct": debate_correct, "debate_calls": debate_calls,
    })

with open("shootout_results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

# Print summary
for condition, calls_key, correct_key in [
    ("Single shot", "single_calls", "single_correct"),
    ("Self-consistency", "sc_calls", "sc_correct"),
    ("Debate", "debate_calls", "debate_correct"),
]:
    acc = sum(r[correct_key] for r in results) / len(results)
    avg_calls = sum(r[calls_key] for r in results) / len(results)
    print(f"{condition}: accuracy={acc:.1%}, avg_calls={avg_calls:.1f}")
```

**Predict:** before you run it, which of S01 to S10 do you expect all three conditions to get wrong together?

Run `python3 shootout.py`.  Ten questions at thirteen calls each take a while on a laptop, so let the run finish.  You should see one block per question, then three summary lines.  The sample below shows the shape of the output.  Your percentages will differ.

```text
Single shot: accuracy=60.0%, avg_calls=1.0
Self-consistency: accuracy=70.0%, avg_calls=6.0
Debate: accuracy=80.0%, avg_calls=6.0
```

> The script marks an answer correct when the expected string appears inside it, ignoring case.  That check is quick, but it can be wrong in both directions.  Before you trust the accuracy line, check every `WRONG` line against the expected answer yourself.  Do the same for every `CORRECT` line on the arithmetic questions.
{: .tb-pitfall data-title="Watch out"}

**If it fails.**

- *Self-consistency and debate give identical results on every question.*  For debate to beat self-consistency, some agents have to change their minds in the revision round.  That needs questions where the first-round answers differ.  Add more word problems with common arithmetic traps, because single-step questions rarely produce disagreement.
- *All three conditions miss the same questions, well beyond one correlated failure.*  The task set may be too hard for your model.  Add some easier questions so the results spread across right and wrong.  If everything is wrong, you cannot see which pattern is better.
- *One agent never produces an `ANSWER:` line.*  Check that agent's temperature and seed.  Above 1.0 the output can turn incoherent, so keep `temperature_schedule` at 0.9 or below.

> **No-code path.** Use one row per question in a spreadsheet.  For single shot, ask the question once in a fresh Open WebUI chat.  For self-consistency, ask it in six fresh chats and take the most common answer.  For debate, open two or three chats and have each one answer on its own first.  Then paste each chat's answer into the others, and ask each chat to revise or defend its answer.  In Langflow, the debate is two Agent nodes and a loop.  For each condition, record the answer, whether it is right, the number of calls, and a cost column (a rough token count or the wall-clock time).

## 13.  Document a Correlated Failure

1. Find a question in your task set (or add one) where every agent agrees on the same wrong answer.
2. Copy every agent's `ANSWER:` line for that question, from the debate rounds the script printed, and put them beside the correct answer.
3. Explain why aggregation fails here, using the independence argument from class.  Then name a resource that is not a language model (a calculator, a lookup, retrieval from a trusted source) that would fix it.

## 14.  Optional: Exchange Positions Through a Channel

This section is optional, even within this tutorial.  You can run the debate condition as two agents that exchange positions through a shared channel, instead of three agents inside one Python process.  The channel is a GitHub issue thread (the list of comments under one issue, each one timestamped) or a shared folder.  The agents follow the claim protocol from *Agents That Talk, Observability, and Handoff Protocols*.

A **claim** is a visible mark in the channel, made before any work starts, that says "this item is mine now."  On GitHub it is a "Claiming this" comment plus an `in-progress` label.  In a folder it is a rename from `inbox/` to `claimed/` followed by a `.claim` file holding `claimed_by` and `claimed_at`.  For a debate, the rule that matters is this: an agent claims the other agent's position before it reads it.  Then the record shows who read what, and when.

For each question:

1. **Write the protocol down first.**  For GitHub: one issue per question, titled with the task id, plus four conventions (the claim comment and label, a reply format ending in `ANSWER:`, a stale timeout, and a closing comment that records the vote).  For a folder: `handoff/inbox/`, `handoff/claimed/`, and `handoff/done/`, the rename-as-claim rule, the `.claim` file, the stale timeout, and a `.result.md` file that marks a position as answered.
2. **Round 1, independent.**  Each agent is its own chat session, or its own script with its own seed.  Each agent answers from the question alone, before reading anything the other posted, and ends with an `ANSWER:` line.  On GitHub, each agent posts its response as a comment.  In the folder, each agent writes `S01-agentA-round1.md` or `S01-agentB-round1.md` into `inbox/`.
3. **Round 2, handoff.**  Each agent claims the other's round-1 position, reads it, and posts a revision.  The revision is either a changed answer or a held position with a rebuttal, and it again ends in `ANSWER:`.  In the folder, the agent moves the claimed file into `done/` and writes its revision beside it as `S01-agentA-round1.result.md`.
4. **Aggregate.**  Pull the `ANSWER:` line from each round-2 post with the same `extract_answer` rule, including the warning when the line is missing.  Two agents can tie, so the protocol has to state the tie rule: a judge agent (one extra call) picks, or the pair records the tie as no answer.
5. **Match the budget.**  The channel debate costs two agents times two rounds, plus one call if the judge ran.  Set `k` for self-consistency to the same number so the conditions stay matched.

A reader of the thread or the folder listing (for example, `ls -l --time-style=full-iso -R handoff/`) should be able to see that each claim happened before the read it authorized, and that every round-2 post replies to a specific round-1 position.

> A comment in the thread is text the other agent will read, so a stray or injected line in one position becomes part of the next agent's context.
{: .tb-pitfall data-title="Watch out"}

### Questions to Work Through

17.  On your task set, which condition had the best accuracy?  Did it also use the most calls?  What does that tradeoff mean for deciding which one to deploy?

18.  Describe your correlated failure in one sentence.  Why could neither majority vote nor debate fix it?

19.  Name the resource that would fix your correlated failure.  Using the tool pattern from the [Local Agent lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/LocalAgent), how would you add it to your existing agent?

20.  **Predict:** `self_consistency` samples at temperature 0.2, the same temperature as single shot, and only the seed changes between its six calls.  If you raised that temperature to 0.8, would you expect self-consistency's accuracy on your task set to go up or down?  Write down your guess and your reason before you try it.

21.  `majority_vote` returns `Counter(...).most_common(1)[0][0]`.  When the final answers tie one to one to one, which answer does it return?  Check the Python documentation for `most_common` rather than guessing.
{: start="17"}

---

# Part VI: Threshold Sensitivity

In the lab's consensus Practice, your six study-group drafts became some number of clusters at a distance threshold of 0.3.  That 0.3 came with the config file, and nobody has checked whether it is a good choice.  If you change it, the same six drafts can become six separate positions or one, and the synthesized answer changes with them.  This part makes that dial visible.

## 15.  Run Consensus at Three Thresholds

**Predict:** at a threshold of 0.1, will you get more clusters or fewer than at 0.3?  Why?

Save this as `threshold.py`.  It changes `distance_threshold` in memory only, so your `config.json` stays as it was.

```python
from lab4 import load_config, run_consensus
config = load_config()

long_form_q = "What makes a great study group, and what are the biggest pitfalls to avoid?"
thresholds = [0.1, 0.3, 0.5]  # tight, medium, loose

for threshold in thresholds:
    config["consensus"]["distance_threshold"] = threshold
    synthesis, drafts, labels, reps, calls = run_consensus(long_form_q, config)
    num_clusters = len(set(labels))
    print(f"\n=== Threshold = {threshold} ===")
    print(f"Clusters: {num_clusters}")
    print(f"Synthesis (first 200 chars): {synthesis[:200]}...")
```

Run `python3 threshold.py`.  Each threshold makes seven calls (six samples and one synthesis), so the run makes twenty-one.  The cluster count should fall as the threshold rises.  The sample below shows the shape of the output.  Your counts and text will differ.

```text
=== Threshold = 0.1 ===
Clusters: 6   <- each draft is its own cluster
Synthesis (first 200 chars): There were 6 distinct perspectives on what makes a great study group...

=== Threshold = 0.3 ===
Clusters: 3   <- moderate merging
Synthesis (first 200 chars): A great study group combines clear goals (supported by 3 samples)...

=== Threshold = 0.5 ===
Clusters: 1   <- everything merged
Synthesis (first 200 chars): A great study group needs...
```

Each threshold samples six new drafts.  So part of the change you see comes from the new samples, and part comes from the threshold.  To separate the two, run the loop twice and see how much the cluster count moves at the same threshold.

**If it fails.**

- *Every threshold gives the same number of clusters.*  The drafts may be nearly identical.  Raise `sample_temperature` to 0.9 or 1.0, or use a more open-ended question.  To see the distances you are working with, you can also print the pairwise cosine distances with `1 - (normed @ normed.T)` inside `cluster_drafts`.
- *0.1 gives fewer clusters than 0.3.*  A lower threshold should give more, tighter clusters.  Check that your code uses `distance_threshold` as the upper bound for merging.  That is how `AgglomerativeClustering` uses it.

> **No-code path.** Use the answers you clustered by hand in the lab's consensus Practice.  Vary the agreement bar you would accept: how many of your hand-clustered answers have to agree before you call it a consensus.  Then use your own spreadsheet to show where the answer flips.

## 16.  Tabulate and Decide Who Owns the Dial

Fill in a table like this one with your own numbers and descriptions.  The rows below are only a template.

| Threshold | Clusters | Synthesis character |
|-----------|----------|---------------------|
| 0.1 | 6 | Highly fragmented; all views presented equally |
| 0.3 | 3 | Balanced; majority position emerges |
| 0.5 | 1 | Over-merged; diversity lost |

Then write one paragraph: who should own this parameter in a deployed system (the developer, the deployer, or the end user), and what documentation would help them choose a value?

### Questions to Work Through

22.  At which threshold did the synthesizer give the most useful answer to your long-form question?  Why?

23.  What goes wrong when the threshold is too low?  What goes wrong when it is too high?

24.  If you were deploying this system for a company's internal knowledge base, who would you recommend owns the threshold, and what guidance would you write in the documentation?

25.  The synthesizer adds a disclosure line when the largest cluster holds less than 60% of the samples.  How does moving the threshold change how often that line appears?
{: start="22"}

---

## Exercises

Everything below is optional.  Each exercise ends with a check you apply yourself, so you can tell whether it worked.

1.  **Is the critic repeatable?**  The critic runs at temperature 0 with a fixed seed, so that the same draft gets the same verdict.  Some Ollama models ignore the seed, and every number in Part I assumes that your model does not.

    *What to do:* Run `critique_draft` three times on each of three calibration drafts, and record whether the verdict and the issue list match across the three runs.

    *Starter hint:* A loop of `for _ in range(3): print(critique_draft(d["draft"], rubric, config))` inside `calibrate.py` is enough.

    *You've succeeded when:* You can say, for each draft, whether the verdict was stable, and you can state in one sentence what an unstable verdict would mean for the detection rates you computed.

2.  **Let the loop write its own rubric.**  Start with a vague rubric, ask the critic "is criterion C1 observable enough to detect without ambiguity?", and refine the descriptors until the critic accepts the rubric as well specified.

    *What to do:* Use `critique_refine_loop` with the rubric text itself as the draft and a short rubric about rubric quality.  Then run Part I's calibration on the refined rubric.

    *Starter hint:* The rubric-about-rubrics needs only two or three criteria, such as "each descriptor names something a reader can see in the draft."

    *You've succeeded when:* You have detection rates for both your hand-refined rubric and the machine-refined one, side by side, and you can say which criterion each one handles better.

3.  **The judge against the vote.**  The lab's `judge_aggregate` reads every agent's final reasoning and picks the best-supported answer, even a minority one.

    *What to do:* In `shootout.py`, call `judge_aggregate(q, transcripts, config)` after each debate and add its answer to the results.  It costs one extra call per question.

    *Starter hint:* Add `judge_aggregate` to the `from lab4 import ...` line.  It returns `(chosen_answer, judge_text)`.

    *You've succeeded when:* You can report the judge's accuracy beside majority vote's, list every question where the judge picked the minority answer, and say whether it was right on those.

4.  **A second model family.**  Correlated failures come from agents that share the same training.  Does mixing models help?

    *What to do:* Pull a second model with `ollama pull` (for example, `mistral` or `phi3`), set `model` in a copy of `config.json`, and rerun the shootout.  Then try a debate in which the agents use different models.

    *Starter hint:* `agent_respond` reads `config["model"]`, so a mixed debate needs a small change that picks the model by `agent_id`.

    *You've succeeded when:* You have the shootout table for both models, and you can say whether your correlated failure from Section 13 survives in the mixed debate.

---

## Reflection Prompt

**Personal level:** Debate and consensus spend extra computation to buy reliability.  Name one decision in your own life where you would pay that cost (ask several people, compare their answers) and one where you would not.  What about the decision, beyond the cost, drives the choice?

**Technical level:** Your critic and your judge are models grading a model.  At which points in this tutorial were you, the person, indispensable?  Name what would have gone wrong at each one if you had removed yourself, and say what that implies about when it is safe to take people out of an evaluation pipeline.

**Societal level:** The synthesizer follows the majority.  Name a real situation, in medicine, law, or public policy, where most experts could be wrong in the same direction.  What would catch that error, other than asking more experts?

---

## Further Reading

- This course: the [Multi-Agent Patterns lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate), whose Practice code every part of this tutorial runs on.
- This course: [Critique, Consensus, and the LLM Judge: One Loop, Three Uses](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-critiqueconsensusjudge.md), for stopping rules, the independence argument behind debate and voting, and the judge's known biases.
- This course: [Judge Pipeline Workshop: Build and Audit a Judge](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-rubricworkshop.md), the leveled JSON rubric, quoted evidence, and the `_quote_found` check that Part IV reuses.
- This course: [Agents That Talk, Observability, and Handoff Protocols](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-observability.md), Part II, the claim protocol behind Section 14.
- This course: [Why Different Answers Every Time? Sampling, Temperature, and Generation](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/SamplingAndTemperature), for the temperature settings the generator, critic, and samplers use, and [Testing Agents](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/TestingAgents).
- Xuezhi Wang et al. "Self-Consistency Improves Chain of Thought Reasoning in Language Models."  *ICLR* (2023).
- Du et al. "Improving Factuality and Reasoning in Language Models through Multiagent Debate."  (2023).
- Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena."  *NeurIPS* (2023).  Pathologies and agreement rates.
