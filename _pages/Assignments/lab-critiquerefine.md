---
layout: assignment
permalink: /Assignments/CritiqueRefine
title: "CS357: Foundations of Artificial Intelligence - Lab 3: Critique and Refine"

info:
  coursenum: CS357
  points: 100
  goals:
    - To implement the generator, critic, refine loop with a structured JSON rubric and explicit stopping rules
    - To calibrate a critic against drafts with planted defects
    - To detect and patch a reward hacking loophole in a rubric
    - To measure whether separated critique outperforms single-shot generation
  rubric:
    - weight: 30
      description: Loop Implementation
      preemerging: The loop fails to run due to major issues, or the program fails to run
      beginning: The loop runs but fails on the test tasks due to one or more minor issues
      progressing: The loop runs correctly with structured critic output and a stopping rule, but a component such as JSON fallback handling or the round budget is fragile
      proficient: The loop runs correctly, producing a verdict of "accept" or "revise" as valid JSON on every round; invalid JSON is logged and treated as "revise" (fail-closed); on budget exhaustion the system returns the last draft with the outstanding critique attached; all of this is demonstrated in a terminal log or screenshot showing at least two complete generate/critique/refine cycles
    - weight: 25
      description: Critic Calibration
      preemerging: No calibration is attempted
      beginning: A few informal trials are described without planted defects or a protocol
      progressing: The critic is tested against drafts with planted defects and a detection rate is reported per criterion
      proficient: The critic is tested against at least ten drafts with planted defects spanning every rubric criterion, plus at least two defect-free drafts; detection rate and false positive rate are reported per criterion in a table; the weakest criterion is identified by name, its descriptors are rewritten, and re-test results show the detection rate for that criterion before and after
    - weight: 20
      description: Reward Hacking Analysis
      preemerging: No reward hacking analysis is provided
      beginning: A loophole is described but not demonstrated
      progressing: A working reward hack against the rubric is demonstrated with a transcript
      proficient: A working reward hack is shown verbatim (the critic's "accept" verdict alongside the student's human judgment that the draft is poor); the rubric patch that closes the loophole is shown in a diff; and a second transcript demonstrates that the patched rubric (a) rejects the hack and (b) still accepts a defect-free draft
    - weight: 15
      description: Comparative Evaluation
      preemerging: No comparison is provided
      beginning: A comparison is described anecdotally without a protocol
      progressing: Critique and refine is compared with single-shot generation on a task set with a defined metric
      proficient: The comparison uses a fixed set of at least eight tasks, the same scoring instrument for both conditions, and reports quality score and model-call count per condition; the writeup draws a specific defensible conclusion (e.g., "critique-and-refine improves quality by X points at a cost of Y extra calls; it earns its latency when ...")
    - weight: 10
      description: Code Quality, Writeup, and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions with externalized configuration, located exception handling with tracebacks, the pair log, and thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Critique and Refine Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-critiquerefine.md"
    - rtitle: "Orchestration Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-orchestration.md"

tags:
  - multi-agent
  - evaluation
  - agents

---

In this lab, you and your partner will build the evaluator-optimizer workhorse of agentic systems: a generator that drafts, a critic that judges against an explicit JSON rubric, and a loop that converges or honestly reports that it did not. This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

---

## Before You Start

**Prerequisite concepts** — complete these activities before writing any code:

- [Critique and Refine Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-critiquerefine.md) — the generator/critic/refine loop and stopping rules
- [Orchestration Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-orchestration.md) — chaining agents with structured outputs

**Tools to install:**

```bash
# All you need is the requests library and Ollama (already installed if you did Labs 1-2)
pip install requests

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

**Health check:**

```bash
python -c "
import requests, json
r = requests.post('http://localhost:11434/api/chat', json={
    'model': 'llama3.2',
    'messages': [{'role': 'user', 'content': 'Reply with exactly: {\"verdict\": \"accept\", \"issues\": []}'}],
    'stream': False
})
print(r.json()['message']['content'])
"
```

Expected output (the model may add extra text, but the JSON should be present):

```
{"verdict": "accept", "issues": []}
```

If you see a connection error, start Ollama with `ollama serve` in a separate terminal.

**Estimated time budget:**

| Part | Task | Estimated time |
|------|------|----------------|
| Part 1 | The Loop | 60–90 min |
| Part 2 | Calibrate the Critic | 45–60 min |
| Part 3 | Reward Hack Your Rubric | 30–45 min |
| Part 4 | Comparative Evaluation | 45–60 min |
| Writeup | Readme and reflection | 30–45 min |

---

## Part 1: The Loop

Choose a generation task with checkable criteria: a structured class announcement, a function docstring, an abstract for a lab report, or a concept of your own. Implement:

1. A **generator** agent with a warm temperature for the first draft and a cooler temperature for revisions (justify your settings using sampling theory from class).
2. A **critic** agent that receives a JSON rubric of at least four criteria with observable descriptors, and returns `{"verdict": "accept" | "revise", "issues": [...]}`. The critic runs at temperature 0 with a fixed seed.
3. A **loop** with a configurable round budget (externalized in JSON configuration). Invalid critic JSON fails closed (treated as revise) and is logged. On budget exhaustion, your system returns the final draft *with its outstanding critique attached*.

### Step-by-step guide

**Step 1: Create your configuration and rubric files.**

`config.json`:
```json
{
  "model": "llama3.2",
  "generator_temp_first": 0.8,
  "generator_temp_revise": 0.3,
  "critic_temp": 0.0,
  "critic_seed": 42,
  "round_budget": 5,
  "rubric_file": "rubric.json",
  "ollama_url": "http://localhost:11434/api/chat"
}
```

`rubric.json` (example for a function docstring task — adapt to your chosen task):
```json
{
  "task": "function_docstring",
  "criteria": [
    {
      "id": "C1",
      "name": "Purpose",
      "descriptor": "The docstring contains a one-sentence summary of what the function does, not how it does it."
    },
    {
      "id": "C2",
      "name": "Parameters",
      "descriptor": "Every parameter is listed with its name, type, and a brief description."
    },
    {
      "id": "C3",
      "name": "Return value",
      "descriptor": "The return value's type and meaning are explicitly described. If the function returns None, this is stated."
    },
    {
      "id": "C4",
      "name": "Example",
      "descriptor": "At least one usage example is provided in a doctest-compatible format (>>> function_call())."
    }
  ],
  "accept_threshold": "All four criteria must be met for a verdict of 'accept'."
}
```

**Step 2: Implement the generator agent.**

```python
import requests
import json
import traceback

def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def load_rubric(config):
    with open(config["rubric_file"]) as f:
        return json.load(f)

def generate_draft(task_description, previous_draft=None, critique=None, config=None):
    """
    Generate a draft for the given task.
    If previous_draft and critique are provided, this is a revision call.
    """
    temperature = config["generator_temp_first"] if previous_draft is None else config["generator_temp_revise"]

    if previous_draft is None:
        user_message = f"Generate a draft for the following task:\n\n{task_description}"
    else:
        user_message = (
            f"Here is the task:\n\n{task_description}\n\n"
            f"Here is your previous draft:\n\n{previous_draft}\n\n"
            f"Here is the critique you must address:\n\n{json.dumps(critique, indent=2)}\n\n"
            f"Please revise the draft to address every issue listed. Return only the revised draft, no commentary."
        )

    messages = [{"role": "user", "content": user_message}]
    payload = {
        "model": config["model"],
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature}
    }

    try:
        response = requests.post(config["ollama_url"], json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab3:generate_draft] {e}")
        traceback.print_exc()
        raise
```

**Step 3: Implement the critic agent.**

```python
def critique_draft(draft, rubric, config):
    """
    Ask the critic to evaluate the draft against the rubric.
    Returns a dict: {"verdict": "accept"|"revise", "issues": [...]}
    On JSON parse failure, returns {"verdict": "revise", "issues": ["[JSON parse failure — treating as revise]"]}
    """
    criteria_text = "\n".join(
        f"- {c['id']} ({c['name']}): {c['descriptor']}"
        for c in rubric["criteria"]
    )

    system_prompt = (
        "You are a strict quality critic. Evaluate the draft against every criterion below. "
        "Return ONLY valid JSON in this exact format, with no additional text:\n"
        '{"verdict": "accept" or "revise", "issues": ["issue 1", "issue 2", ...]}\n\n'
        "Use 'accept' only if ALL criteria are fully met. "
        "Use 'revise' if ANY criterion is not met. "
        "List every unmet criterion as a separate issue string.\n\n"
        f"CRITERIA:\n{criteria_text}\n\n"
        f"ACCEPT THRESHOLD: {rubric['accept_threshold']}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"DRAFT TO EVALUATE:\n\n{draft}"}
    ]

    payload = {
        "model": config["model"],
        "messages": messages,
        "stream": False,
        "options": {"temperature": config["critic_temp"], "seed": config["critic_seed"]}
    }

    try:
        response = requests.post(config["ollama_url"], json=payload, timeout=60)
        response.raise_for_status()
        raw = response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab3:critique_draft:network] {e}")
        traceback.print_exc()
        raise

    # Try to parse JSON; fail closed on malformed output
    try:
        # Strip markdown code fences if present
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        critique = json.loads(clean)
        assert "verdict" in critique and "issues" in critique
        return critique
    except Exception as e:
        print(f"[lab3:critique_draft:json_parse] Malformed critic output — failing closed. Raw: {raw!r}")
        return {"verdict": "revise", "issues": [f"[JSON parse failure] Raw output: {raw[:200]}"]}
```

**Step 4: Implement the main loop.**

```python
def critique_refine_loop(task_description, config, rubric):
    """
    Run the generate/critique/refine loop.
    Returns (final_draft, final_critique, rounds_used, termination_reason).
    """
    draft = None
    critique = None

    for round_num in range(1, config["round_budget"] + 1):
        print(f"\n=== Round {round_num} ===")

        # Generate
        draft = generate_draft(task_description, previous_draft=draft, critique=critique, config=config)
        print(f"[Generator] Draft (first 200 chars): {draft[:200]}...")

        # Critique
        critique = critique_draft(draft, rubric, config)
        print(f"[Critic] Verdict: {critique['verdict']}")
        if critique["issues"]:
            print(f"[Critic] Issues: {critique['issues']}")

        if critique["verdict"] == "accept":
            return (draft, critique, round_num, "accepted")

    # Budget exhausted — return last draft with critique attached
    final_output = f"{draft}\n\n--- OUTSTANDING CRITIQUE (budget exhausted after {config['round_budget']} rounds) ---\n{json.dumps(critique, indent=2)}"
    return (final_output, critique, config["round_budget"], "budget_exhausted")
```

**Step 5: Run a smoke test.**

```python
if __name__ == "__main__":
    config = load_config()
    rubric = load_rubric(config)
    task = "Write a Python docstring for a function called `merge_sorted_lists` that takes two sorted lists of integers and returns a single sorted list."
    draft, critique, rounds, reason = critique_refine_loop(task, config, rubric)
    print(f"\n=== FINAL OUTPUT ===\nRounds: {rounds} | Reason: {reason}")
    print(draft)
```

Expected output (abbreviated):

```
=== Round 1 ===
[Generator] Draft (first 200 chars): """Merge two sorted lists.

Args:
    a (list): First sorted list.
    b (list): Second sorted list.
...
[Critic] Verdict: revise
[Critic] Issues: ['C4 (Example): No usage example in doctest format is provided.']

=== Round 2 ===
[Generator] Draft (first 200 chars): """Merge two sorted lists of integers into one sorted list.

Args:
    a (list[int]): First sorted list.
...
[Critic] Verdict: accept
[Critic] Issues: []

=== FINAL OUTPUT ===
Rounds: 2 | Reason: accepted
```

### Troubleshooting — Part 1

**The critic always returns `"verdict": "revise"` even after many rounds**
Print the full critic output (`raw` before JSON parsing) to see what the model is actually saying. Common causes: (1) the model is outputting JSON wrapped in markdown fences — the strip step in the parser should handle this, but check for unusual fence formats; (2) the rubric descriptors are so strict that no draft can satisfy them — loosen one criterion as a test.

**`json.JSONDecodeError` fires on valid-looking output**
The model may be inserting a BOM or non-breaking space before the opening `{`. Add `raw = raw.encode('ascii', 'ignore').decode('ascii')` before `json.loads` to strip non-ASCII, then re-try.

**The loop never terminates (no `accept` and no budget exhaustion)**
Check that your `for round_num in range(1, config["round_budget"] + 1)` loop is iterating the correct number of times. Print `round_num` at the start of each iteration. If it runs forever, your `return` on `"accepted"` may be inside an inner scope — check indentation.

---

> **Checkpoint: Before moving to Part 2, make sure you can answer:**
> 1. Why does the critic run at temperature 0 while the generator runs at a higher temperature? What property does each temperature setting encourage?
> 2. What does "fail closed" mean in the context of JSON parsing? Why is fail-closed safer than ignoring the parse error?
> 3. On budget exhaustion, your loop attaches the outstanding critique to the returned draft. Why is this useful to the caller?

---

## Part 2: Calibrate the Critic

Write at least ten drafts with **planted defects** that you select to span every criterion (and include at least two defect-free drafts). Run the critic over all of them and report, per criterion, the detection rate and the false positive rate. Identify the weakest criterion, rewrite its descriptors to be more observable, and report the improvement.

### Step-by-step guide

**Step 1: Write your calibration drafts.**

Create a file `calibration_drafts.json`:

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
  // TODO: Add D04 through D12 — at least one defect per criterion, multiple multi-defect drafts
]
```

**Step 2: Run the critic over every draft and record results.**

```python
import json

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
```

**Step 3: Compute per-criterion detection and false positive rates.**

```python
def compute_rates(results, rubric):
    criteria_ids = [c["id"] for c in rubric["criteria"]]
    rates = {}

    for cid in criteria_ids:
        # True positives: draft has this defect AND critic mentioned it
        # False negatives: draft has this defect AND critic missed it
        # False positives: draft has NO defect AND critic flagged this criterion
        tp = fp = fn = tn = 0

        for r in results:
            has_defect = cid.lower() in r["planted_defect"].lower() or "none" not in r["planted_defect"].lower()
            # Simplification: check if any issue string mentions the criterion ID or name
            critic_flagged = any(cid in issue for issue in r["critic_issues"])

            if r["planted_defect"] == "none":
                # Defect-free draft
                if critic_flagged:
                    fp += 1
                else:
                    tn += 1
            else:
                # Draft has planted defect
                if critic_flagged:
                    tp += 1
                else:
                    fn += 1

        detection_rate = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
        fp_rate = fp / (fp + tn) if (fp + tn) > 0 else float("nan")
        rates[cid] = {"detection_rate": detection_rate, "false_positive_rate": fp_rate}
        print(f"  {cid}: detection={detection_rate:.2f}, fp_rate={fp_rate:.2f}")

    return rates
```

**Step 4: Identify the weakest criterion and rewrite it.**

The weakest criterion is the one with the lowest detection rate. Compare the original descriptor to your new one in your readme, and show the before/after detection rates.

Example:
- **Before**: "C4 (Example): At least one example is provided."
- **After**: "C4 (Example): At least one usage example is shown in doctest format: a line beginning with `>>>` followed by the function call, and a second line with the expected return value."

### Troubleshooting — Part 2

**Detection rate is 1.0 for all criteria even with weak descriptors**
Your planted defects may be too obvious. Try subtle defects: a parameter description that lists the name but not the type, or an example that shows a call but not the return value. Make the defect require careful reading to spot.

**Detection rate is 0.0 for a criterion even after rewriting**
The model may not be parsing your criterion ID correctly. Change the prompt to include the criterion name in full (not just "C1") and check that the model's issue strings reference those names.

**Your two defect-free drafts get critiqued as "revise"**
This is a false positive. Record the rate and include it in your analysis — it is an important signal about rubric over-strictness.

---

> **Checkpoint: Before moving to Part 3, make sure you can answer:**
> 1. Which criterion had the lowest detection rate before your rewrite? What specifically made that criterion hard for the model to evaluate?
> 2. What is the difference between a detection rate and a false positive rate? Which one is more costly in a real deployment, and why?
> 3. Why must you include defect-free drafts in a calibration set, not just defective ones?

---

## Part 3: Reward Hack Your Own Rubric

Attempt to produce a draft that the critic accepts while being, by your human judgment, a poor artifact: satisfy the letter while betraying the intent. Document the successful hack with a transcript, then **patch the rubric** to close the loophole and demonstrate that the patch (a) rejects the hack and (b) still accepts your defect-free drafts.

### Step-by-step guide

**Step 1: Identify a loophole.**

Think about each criterion's descriptor literally. Common loophole types:
- **Keyword stuffing**: The descriptor says "contains a one-sentence summary" — can you write a sentence so vague it is technically present but useless?
- **Minimal compliance**: The descriptor says "every parameter is listed" — can you list parameters with empty or copy-pasted descriptions?
- **Format gaming**: The descriptor says "in doctest format" — can you write a syntactically valid doctest that tests nothing meaningful?

**Step 2: Author the hack draft and confirm the critic accepts it.**

```python
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

Document this transcript verbatim in your readme with your human judgment of why it is poor.

**Step 3: Patch the rubric and verify the patch.**

Create `rubric_patched.json` — change only the exploited criterion's descriptor. Show a diff in your readme. Then:

```python
rubric_patched = load_rubric_from_file("rubric_patched.json")

# Test 1: patch rejects the hack
critique_hack = critique_draft(hack_draft, rubric_patched, config)
print(f"Patched rubric on hack: {critique_hack['verdict']}")  # Expected: revise

# Test 2: patch still accepts a good draft
good_draft = "..."  # your defect-free draft from Part 2
critique_good = critique_draft(good_draft, rubric_patched, config)
print(f"Patched rubric on good draft: {critique_good['verdict']}")  # Expected: accept
```

### Troubleshooting — Part 3

**You cannot find a hack — the critic is too strict**
Try the minimal-compliance approach: meet every criterion with the absolute minimum. For example, if the criterion says "every parameter is listed with name, type, and description," write a description of a single character: `a (list[int]): x.`

**The patch rejects both the hack AND the good draft**
Your patch is too strict. Revise the wording to be more precise rather than more restrictive. The goal is to close the specific loophole, not to raise the bar for all drafts.

**The critic is non-deterministic even at temperature 0**
Some Ollama models ignore the seed parameter. Try running the same draft three times and recording whether the verdict is consistent. If it is not, note this in your writeup as a threat to calibration reliability.

---

> **Checkpoint: Before moving to Part 4, make sure you can answer:**
> 1. Describe your hack in one sentence. Which criterion's descriptor had the loophole?
> 2. What does the existence of reward hacking imply about using any rubric — automated or human — as the sole quality gate?
> 3. In your patched rubric, what specific wording change closed the loophole? Why does that wording prevent the hack while still accepting good work?

---

## Part 4: Did It Earn Its Latency?

On a fixed set of at least eight tasks, compare single-shot generation against your full critique and refine loop. Score both conditions with the same instrument (your calibrated critic on a held-out rubric, or a blind human ranking between you and your partner). Report quality and cost (number of model calls), and conclude in a paragraph when the pattern is and is not worth deploying.

### Step-by-step guide

**Step 1: Define your eight tasks and scoring instrument.**

```python
COMPARISON_TASKS = [
    "Write a docstring for a function `binary_search(arr, target)` that searches a sorted list.",
    "Write a docstring for a function `flatten(nested_list)` that recursively flattens nested lists.",
    # TODO: Add 6 more tasks of increasing complexity
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
```

**Step 2: Run both conditions on all eight tasks.**

```python
import csv

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

Expected output format (your numbers will differ):

```
T01: single=2/4 (2 calls) | loop=4/4 (6 calls, 3 rounds)
T02: single=3/4 (2 calls) | loop=4/4 (4 calls, 2 rounds)
...
Single-shot: avg score=2.75, avg calls=2.0
Loop: avg score=3.50, avg calls=5.2
```

**Step 3: Write your conclusion paragraph.**

In your readme, answer: did the loop earn its extra model calls? Under what conditions (task complexity, quality threshold, latency budget) would you choose each approach?

### Troubleshooting — Part 4

**Single-shot and loop produce identical scores**
Your rubric criteria may be too easy to satisfy in a single shot. Try harder tasks (more criteria to satisfy simultaneously) or add a fifth criterion to your rubric. Alternatively, single-shot may score high because you chose simple tasks — the benefit of the loop shows most clearly on tasks with four or more competing constraints.

**The loop always hits the round budget without accepting**
Decrease the `round_budget` to 3 for the comparison experiment so budget-exhaustion cases are more frequent and visible in your data. Document these cases — they show the loop's failure mode.

**Scores from the critic feel inconsistent across conditions**
Use a fresh critic call with a fixed seed for all final scoring (not the verdicts from within the loop). This ensures both conditions are scored by the same "judge call" and results are comparable.

---

> **Checkpoint: Before writing your deliverables, make sure you can answer:**
> 1. On average, how many extra model calls did the loop use compared to single-shot? What was the average quality improvement?
> 2. On which tasks did the loop NOT improve over single-shot? What do those tasks have in common?
> 3. If each model call costs $0.001, what is the maximum quality improvement you would pay for in a real deployment, and how does that compare to what you measured?

---

## Deliverables

Submit a ZIP containing your code, JSON configuration and rubric files, planted-defect drafts with labels, calibration results (CSV or table), reward hack transcript and patch, comparison results, pair log, and a readme writeup of approximately two pages. Ensure reproducibility by fixing random seeds and listing software version information.

## Reflection Prompts

- Your critic is an LLM judging an LLM. At what specific points in this lab did you, the humans, remain indispensable — and what would have gone wrong if you had removed yourselves? Connect your answer to the broader question of when it is safe to remove humans from an evaluation pipeline.
- Describe the most surprising critic behavior you observed: a missed defect, a phantom defect, or an oscillation (the critic reverses its verdict across rounds without the draft changing). What does that behavior imply about using this critic in a high-stakes setting?
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

## Extension Challenges

These are optional and carry no extra credit.

**Challenge 1 (moderate): Add a revision history log.**
After each round, store the draft and critique in a list. At the end of the loop, print a table showing how many issues were resolved each round (issues in round N minus issues in round N+1). Identify which criteria took the most rounds to satisfy.

**Challenge 2 (harder): Multi-agent cross-critique.**
Instead of one critic, use two critics with different system prompts (one strict, one lenient). Accept a draft only when both critics agree on "accept." Measure how this changes the average rounds-to-acceptance and the quality of accepted drafts.

**Challenge 3 (hardest): Self-referential calibration.**
Use your loop to generate and refine its own rubric: start with a vague rubric, ask the critic "is this rubric's criterion C1 observable enough to detect without ambiguity?", and refine criterion descriptors until the critic accepts the rubric as well-specified. Then run Part 2's calibration on the auto-refined rubric and compare its detection rates to your manually-refined rubric.
