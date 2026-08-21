---
layout: assignment
permalink: /Assignments/CritiqueRefine
title: "CS357: Foundations of Artificial Intelligence - Critique and Refine"

info:
  coursenum: CS357
  purpose: "To build the generator-critic-refine loop at the heart of self-improving agentic systems, and to learn when separated critique earns its cost."
  tilt:
    task: "Implement a generator-critic-refine loop against a JSON rubric, calibrate the critic on planted defects, and demonstrate then patch a reward hack."
    criteria: "Assessed on a correct fail-closed loop, critic calibration against planted defects, and a demonstrated-then-patched reward hack; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To implement the generator, critic, refine loop with a structured JSON rubric and explicit stopping rules
    - To calibrate a critic against drafts with planted defects and report detection and false-positive rates per criterion
    - To detect and patch a reward hacking loophole in a rubric by demonstrating the exploit and verifying the fix
    - To measure whether separated critique outperforms single-shot generation on a defined task set with matched scoring
    - To use a coding agent (OpenCode or Claude Code) to implement a feature from a written spec
    - To design an agent system prompt that constrains the coding agent's behavior appropriately
    - To evaluate coding agent output for correctness, style, security, and test coverage
    - To document the agent's decision-making process and review its diffs before accepting
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
      proficient: The program is submitted according to the directions with externalized configuration in a JSON file, located exception handling with tracebacks on all model calls, a pair log with at least two timestamped role swaps, and reflection answers that each cite a specific numeric result or transcript excerpt from the lab
  readings:
    - rtitle: "Critique and Refine Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-critiquerefine.md"
    - rtitle: "Orchestration Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-orchestration.md"
    - rtitle: "Coding Agents Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-codingagents.md"
    - rtitle: "The Local Agent Stack Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md"

tags:
  - multi-agent
  - evaluation
  - agents
  - coding
  - security
  - testing

---

In this lab, you and your partner will build the evaluator-optimizer workhorse of agentic systems: a generator that drafts, a critic that judges against an explicit JSON rubric, and a loop that converges or honestly reports that it did not. This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

**See the course schedule for the assigned and due dates.**

---

## Before You Start

> **Choose your route first.** This lab has a full **no-code and low-code route** (near the end of this page) that carries equal credit: three saved Open WebUI presets with text moved by hand, or a Langflow canvas, instead of orchestration code. Parts 2 and 3 (calibrating the critic, and building a working reward hack) are prompt-and-analysis work on every route, and they carry 45 of the 100 points. Decide before you start.

**Prerequisite concepts**: complete these activities before writing any code:

- [Critique and Refine Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-critiquerefine.md): the generator/critic/refine loop and stopping rules
- [Orchestration Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-orchestration.md): chaining agents with structured outputs

**Tools to install:**

```bash
# All you need is the requests library and Ollama (already installed if you did the earlier labs)

> **This page is Part A of the Multi-Agent Patterns Lab, not a separate assignment.** It has no deadline of its own and no separate grade. Build what it describes, then continue to the **[Multi-Agent Patterns Lab](https://www.billmongan.com/Ursinus-CS357/Assignments/MultiAgentDebate)**, which carries the single rubric and the single due date for both halves.


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

```json
{"verdict": "accept", "issues": []}
```

If you see a connection error, start Ollama with `ollama serve` in a separate terminal.

**Estimated time budget:**

| Part | Task | Estimated time |
|------|------|----------------|
| Part 1 | The Loop | 60-90 min |
| Part 2 | Calibrate the Critic | 45-60 min |
| Part 3 | Reward Hack Your Rubric | 30-45 min |
| Part 4 | Comparative Evaluation | 45-60 min |
| Writeup | Readme and reflection | 30-45 min |

**Total:** plan on roughly **3.5-4.5 hours for the core lab** (Parts 1-4 plus the writeup), plus roughly **2.5-3 hours for the direction** if you choose to extend. Budget your pair sessions accordingly; this is not a single-sitting lab.

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

`rubric.json` (example for a function docstring task, adapt to your chosen task):

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
    On JSON parse failure, returns {"verdict": "revise", "issues": ["[JSON parse failure - treating as revise]"]}
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
        print(f"[lab3:critique_draft:json_parse] Malformed critic output - failing closed. Raw: {raw!r}")
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

    # Budget exhausted - return last draft with critique attached
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

### Troubleshooting, Part 1

**The critic always returns `"verdict": "revise"` even after many rounds**
Print the full critic output (`raw` before JSON parsing) to see what the model is actually saying. Common causes: (1) the model is outputting JSON wrapped in markdown fences; the strip step in the parser should handle this, but check for unusual fence formats; (2) the rubric descriptors are so strict that no draft can satisfy them; loosen one criterion as a test.

**`json.JSONDecodeError` fires on valid-looking output**
The model may be inserting a BOM or non-breaking space before the opening `{`. Add `raw = raw.encode('ascii', 'ignore').decode('ascii')` before `json.loads` to strip non-ASCII, then re-try.

**The loop never terminates (no `accept` and no budget exhaustion)**
Check that your `for round_num in range(1, config["round_budget"] + 1)` loop is iterating the correct number of times. Print `round_num` at the start of each iteration. If it runs forever, your `return` on `"accepted"` may be inside an inner scope; check indentation.

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
  // TODO: Add D04 through D12 - at least one defect per criterion, multiple multi-defect drafts
]
```

> **Worked example, adding a new entry (D04).** Two things trip people up here. First, JSON does not allow comments, so **delete the `// TODO` line** before you run your code; it is a note to you, not valid JSON. Second, a multi-line docstring must be written as a single JSON string with `\n` for each line break and `\"` for each quote. Here is a complete D04 entry with a *subtle* planted defect (the parameter descriptions list names but omit types, a violation of C2 that requires careful reading to spot):
>
> ```json
> {
>   "id": "D04",
>   "defect": "missing_C2",
>   "description": "Parameters listed but types omitted",
>   "draft": "\"\"\"Merge two sorted lists of integers into a single sorted list.\n\nArgs:\n    a: The first sorted list.\n    b: The second sorted list.\n\nReturns:\n    list[int]: A new sorted list containing all elements from a and b.\n\nExample:\n    >>> merge_sorted_lists([1, 3], [2, 4])\n    [1, 2, 3, 4]\n\"\"\""
> }
> ```
>
> Rather than hand-escaping every entry, you can let Python do the escaping for you. Write the draft as a normal triple-quoted string and let `json.dumps` produce the escaped version to paste into your file:
>
> ```python
> import json
>
> draft_d05 = """\"\"\"Merge two sorted lists.
>
> Args:
>     a (list[int]): First sorted list.
>     b (list[int]): Second sorted list.
> \"\"\""""  # planted defect: no Returns section and no Example (missing C3 and C4)
>
> entry = {
>     "id": "D05",
>     "defect": "missing_C3_and_C4",
>     "description": "No return description and no example",
>     "draft": draft_d05,
> }
> print(json.dumps(entry, indent=2))  # copy this output into calibration_drafts.json
> ```
>
> Follow this same pattern for D06 through D12: pick a criterion (or two), decide on a defect that violates it, write the draft, and record the defect label so Step 3 can score it.

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

### Troubleshooting, Part 2

**Detection rate is 1.0 for all criteria even with weak descriptors**
Your planted defects may be too obvious. Try subtle defects: a parameter description that lists the name but not the type, or an example that shows a call but not the return value. Make the defect require careful reading to spot.

**Detection rate is 0.0 for a criterion even after rewriting**
The model may not be parsing your criterion ID correctly. Change the prompt to include the criterion name in full (not just "C1") and check that the model's issue strings reference those names.

**Your two defect-free drafts get critiqued as "revise"**
This is a false positive. Record the rate and include it in your analysis; it is an important signal about rubric over-strictness.

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
- **Keyword stuffing**: The descriptor says "contains a one-sentence summary"; can you write a sentence so vague it is technically present but useless?
- **Minimal compliance**: The descriptor says "every parameter is listed"; can you list parameters with empty or copy-pasted descriptions?
- **Format gaming**: The descriptor says "in doctest format"; can you write a syntactically valid doctest that tests nothing meaningful?

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

Create `rubric_patched.json`; change only the exploited criterion's descriptor. Show a diff in your readme. Then:

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

### Troubleshooting, Part 3

**You cannot find a hack: the critic is too strict**
Try the minimal-compliance approach: meet every criterion with the absolute minimum. For example, if the criterion says "every parameter is listed with name, type, and description," write a description of a single character: `a (list[int]): x.`

**The patch rejects both the hack AND the good draft**
Your patch is too strict. Revise the wording to be more precise rather than more restrictive. The goal is to close the specific loophole, not to raise the bar for all drafts.

**The critic is non-deterministic even at temperature 0**
Some Ollama models ignore the seed parameter. Try running the same draft three times and recording whether the verdict is consistent. If it is not, note this in your writeup as a threat to calibration reliability.

---

> **Checkpoint: Before moving to Part 4, make sure you can answer:**
> 1. Describe your hack in one sentence. Which criterion's descriptor had the loophole?
> 2. What does the existence of reward hacking imply about using any rubric (automated or human) as the sole quality gate?
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

### Troubleshooting, Part 4

**Single-shot and loop produce identical scores**
Your rubric criteria may be too easy to satisfy in a single shot. Try harder tasks (more criteria to satisfy simultaneously) or add a fifth criterion to your rubric. Alternatively, single-shot may score high because you chose simple tasks; the benefit of the loop shows most clearly on tasks with four or more competing constraints.

**The loop always hits the round budget without accepting**
Decrease the `round_budget` to 3 for the comparison experiment so budget-exhaustion cases are more frequent and visible in your data. Document these cases; they show the loop's failure mode.

**Scores from the critic feel inconsistent across conditions**
Use a fresh critic call with a fixed seed for all final scoring (not the verdicts from within the loop). This ensures both conditions are scored by the same "judge call" and results are comparable.

---

> **Checkpoint: Before writing your deliverables, make sure you can answer:**
> 1. On average, how many extra model calls did the loop use compared to single-shot? What was the average quality improvement?
> 2. On which tasks did the loop NOT improve over single-shot? What do those tasks have in common?
> 3. If each model call costs $0.001, what is the maximum quality improvement you would pay for in a real deployment, and how does that compare to what you measured?

---

## The No-Code and Low-Code Routes (equal credit)

You may run the full critique-and-refine loop **without writing the orchestration**, using Open WebUI or Langflow. The Open WebUI version is genuinely no-code: three saved model presets and text you move between them by hand. It is slower per round, and the seams (where the critic's words become the reviser's instructions) are far more visible, which is where the learning is.

1. **Two roles, one canvas.** In Langflow, chain **Generator -> Critic -> Reviser** as three prompt nodes, feeding the critic's output back into the reviser. In Open WebUI, do it as three saved model presets and pass the text between them by hand; slower, but the loop is identical and the seams are more visible.
2. **Calibrate the critic the same way.** Part 2's work (checking whether the critic's criticism actually tracks quality) is prompt work and analysis, not code. Run your calibration cases through the critic and record agreement.
3. **Reward-hack it the same way.** Part 3 asks you to write something that scores well and is bad. That is a writing exercise; the route you used to run the rubric does not change it.
4. **Latency and worth.** Time one pass versus three by the clock, and answer Part 4's question with your own measurements.

**What you submit instead of code:** the exported flow (or your preset prompts), the transcript of at least three refine rounds, your calibration table, your successful reward hack, and the identical written analysis.

## Self-Check Before You Submit

Held against the rubric's `proficient` column. On the no-code or low-code route, read "code" as "presets or flow" and "log" as "transcript".

- [ ] Every round produces a verdict of **accept** or **revise** as valid JSON.
- [ ] Invalid JSON is logged and treated as **revise**, failing closed rather than open.
- [ ] On budget exhaustion the system returns the last draft **with the outstanding critique attached**.
- [ ] At least two complete generate, critique, refine cycles are shown.
- [ ] **Calibration:** at least ten drafts with planted defects spanning **every** rubric criterion, plus at least two defect-free drafts.
- [ ] Detection rate and **false positive** rate reported per criterion, in a table.
- [ ] The weakest criterion is named, its descriptors rewritten, and re-test results show before and after for that criterion.
- [ ] **Reward hack:** a working one, shown verbatim, with the critic's "accept" next to my own judgment that the draft is poor.
- [ ] The rubric patch that closes it is shown as a **diff**.
- [ ] A second transcript shows the patched rubric rejects the hack **and still accepts a defect-free draft**.
- [ ] **Comparison:** at least eight fixed tasks, the same scoring instrument on both sides, quality score and call count per condition.
- [ ] The conclusion is specific and defensible, naming when the latency is earned.
- [ ] Configuration is externalized; located exception handling with tracebacks on model calls.
- [ ] Pair log with at least two timestamped role swaps.
- [ ] Every reflection answer cites a specific numeric result or transcript excerpt.
- [ ] The route I took is named at the top of the writeup.

## Deliverables

Submit a ZIP containing your code, JSON configuration and rubric files, planted-defect drafts with labels, calibration results (CSV or table), reward hack transcript and patch, comparison results, pair log, and a readme writeup of approximately two pages. Ensure reproducibility by fixing random seeds and listing software version information.

## Learning Log

Keep a metacognitive learning log for this lab in your readme: in the spirit of multiple means of action and expression, you may respond to each prompt in prose, in bullet points, or with an annotated diagram, whichever best conveys your thinking. (Prompt 4 adapts the AI-Assisted Learning Template by Marc Watkins.)

1. **What I built.** One paragraph, in plain language that a friend outside of computer science could follow (this is deliberate practice in writing for multiple audiences).
2. **What surprised me.**
3. **What I verified and how.** Evidence, not vibes.
4. **How I used AI during this lab**, and what I learned from that use.
5. **What I'd tell the next student** before they start.
6. **One open question I still have.**

### Lab-specific prompts

- Your critic is an LLM judging an LLM. At what specific points in this lab did you, the humans, remain indispensable, and what would have gone wrong if you had removed yourselves? Connect your answer to the broader question of when it is safe to remove humans from an evaluation pipeline.
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

---

## Choose Your Direction

Everyone completes the core Critique-and-Refine lab above: the generator/critic/refine loop, the calibration study, the reward-hack analysis, and the comparative evaluation. That core is the required spine of this assignment.

You may then **extend** the core in the direction below. The direction is not a separate assignment and does not carry its own grade; the single 100-point rubric at the top of this page covers the core lab *and* your chosen direction together. Pick the direction that best fits your interests and carry your critique-and-refine discipline into it.

- **Direction 1: Coding Agents in Practice**: run the generate/critique/refine loop with a coding agent as the generator: hand it a REST API spec, review its diff line by line, feed a categorized critique back as one refine turn, then harden the accepted result with linting and security scanning.

<details markdown="1">
<summary><strong>Direction 1: Coding Agents in Practice</strong></summary>

> **What this direction requires**
>
> - **Node.js and npm** (install from [https://nodejs.org](https://nodejs.org) if you do not have them)
> - **One coding agent**, installed via npm: `@anthropic-ai/claude-code` **or** `opencode-ai`
> - **An API key** for the provider your agent uses (roughly $5 of credit is more than enough for this direction, or use the instructor-provided key if one is announced in class)
>
> **The API key is required for this direction**: the coding agents used here call a hosted model, not your local Ollama instance. This is the only part of this lab that needs an API key; the core lab (Parts 1-4) runs entirely against your local Ollama setup from the earlier labs. If the cost or the account setup is a barrier, talk to me before you start rather than after; do not let a missing key silently eat your time budget.

In this direction you apply the very same generator-critic-refine loop you built above, but with a **coding agent standing in as the generator**. You hand the agent a written specification for a REST API endpoint and it drafts an implementation. You play the critic: instead of accepting its diff, you read every line against the spec, categorize your findings the way your JSON critic categorizes rubric violations, and feed a precise critique back to the agent as a follow-up prompt, one turn of the refine loop. After the loop converges you harden the accepted result with linting and security scanning. The skill being assessed is not whether the agent produces working code on the first try; it is whether your critique-and-refine discipline can drive the agent to a trustworthy outcome. Complete this direction in **pairs using driver/navigator roles with swaps at least every 30 minutes and a logged swap record**.

#### What proficient work looks like

Because this direction is graded under the same 100-point rubric as the core lab, there are no separate rubric rows to satisfy. Proficient work on this direction shows up as:

- **Spec fidelity:** the final code faithfully implements every requirement in your spec, including every error case and testing criterion, and each spec requirement is traceable to the corresponding code.
- **Line-by-line critique:** every proposed change is reviewed line by line, your critique document clearly categorizes findings (correct, wrong, missing, security risk), your follow-up prompt is precise, and the second diff shows measurable improvement over the first.
- **Constraint design:** your system prompt defines file scope, library choices, and explicit prohibitions; you verify every constraint against the agent trace and document and remediate any violations.
- **Documentation and reflection:** every diff annotation explains the *why* and not just the *what*, your pair log shows regular timestamped swaps, the linter and security-scanner output is included and addressed, and your reflections demonstrate a changed mental model about what coding agents can and cannot be trusted to do.

#### Before You Start

**Estimated time:** Part 1 ~30 min | Part 2 ~45 min | Part 3 ~45 min | Part 4 ~30 min

##### Prerequisite concepts

Before beginning, make sure you have completed both of the following activities (linked in the readings above):

- [Coding Agents Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-codingagents.md): covers what a coding agent is, how it reads files, proposes edits, and accepts or rejects changes
- [The Local Agent Stack Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md): covers how to run a local agent with a system prompt, how the agent loop works, and how to capture a trace

If you have not done both activities, do them now before reading further. The concepts introduced there are assumed throughout this direction.

##### Install required tools

Run the following commands in your terminal to install the Python packages needed for Parts 2-4:

```bash
pip install openai anthropic flake8 bandit
```

Then install your coding agent. Choose one (or install both for the Extension Challenges):

**Claude Code:**

```bash
npm install -g @anthropic-ai/claude-code
```

**OpenCode:**

```bash
npm install -g opencode-ai
```

If `npm` is not available on your machine, install Node.js first from [https://nodejs.org](https://nodejs.org), then rerun the command above.

##### Health-check: verify your setup

After installing, run each of the following commands and confirm you see the expected output before moving on.

```bash
flake8 --version
```

> Expected output (version numbers may differ):
> ```
> 7.1.1 (mccabe: 0.7.0, pycodestyle: 2.11.1, pyflakes: 3.2.0) CPython 3.11.9 on linux
> ```

```bash
bandit --version
```

> Expected output:
> ```
> bandit 1.7.9
>   python version = 3.11.9 (...)
> ```

**Claude Code:**

```bash
claude --version
```

> Expected output:
> ```
> claude-code/1.x.x
> ```

**OpenCode:**

```bash
opencode --version
```

> Expected output:
> ```
> opencode x.x.x
> ```

You also need an API key for whichever agent you are using. Set it as an environment variable:

```bash
# For Claude Code
export ANTHROPIC_API_KEY="sk-ant-..."

# For OpenCode (uses OpenAI by default)
export OPENAI_API_KEY="sk-..."
```

Add this line to your `~/.bashrc` or `~/.zshrc` so it persists across terminal sessions.

#### Overview

In this direction you will write a specification for a `POST /search` REST API endpoint that queries a local in-memory knowledge base and returns summarized results. You will then hand that spec to a coding agent (the generator) and watch it implement the feature. After the first run you will not accept the changes yet; instead you will read every line of the proposed diff, write a critique document that categorizes what the agent got right and wrong (the same categorize-then-revise move at the heart of your core loop), and feed that critique back to the agent as a follow-up prompt. After the second run you will accept the final diff, run the agent's tests, add at least two tests the agent missed, and run both a linter and a security scanner. By the end you will have a complete picture of what coding agents can and cannot be trusted to do on their own.

#### Part 1: Design First (Before Any Agent Interaction)

**Estimated time: ~30 minutes**

The single most important rule of this direction: **write the spec and the system prompt before you touch the agent.** Agents that receive a vague task produce vague code. Agents that receive no constraints violate them. You are designing the guardrails first, the coding-agent analogue of writing your JSON rubric before you run the critic.

##### Step 1: Create the project directory

Create a fresh directory for this direction. All files you create here go inside it.

```bash
mkdir cs357-coding-agents
cd cs357-coding-agents
```

Create the following empty files now so you know what you are building toward:

```bash
touch spec.md system_prompt.txt app.py test_app.py critique.md pair_log.md
```

##### Step 2: Write the spec in `spec.md`

Open `spec.md` and fill in the template below. Every blank marked `[TODO]` must be completed before you run the agent. Do not skip any field; the agent will use this document as its task description.

```markdown
# Feature Spec: POST /search Endpoint

## Author(s)
[TODO: Your names]

## Date
[TODO: Today's date]

## Feature summary
A REST API endpoint that accepts a JSON search query and returns matching
entries from a local in-memory knowledge base.

## Function / route signature
- Method: POST
- Path: /search
- Framework: Flask (Python)
- Handler function name: search_knowledge_base

## Inputs
The request body must be valid JSON with the following fields:

| Field   | Type   | Required | Description                              |
|---------|--------|----------|------------------------------------------|
| query   | string | yes      | The search string (1-200 characters)     |
| max_results | int | no   | Max entries to return (default 5, max 20)|

## Outputs
On success (HTTP 200), return JSON:

```json
{
  "results": [
    { "id": "<string>", "title": "<string>", "snippet": "<string>" }
  ],
  "count": <int>,
  "query": "<string echoed back>"
}

```

## Error cases (all must be handled and tested)

| Condition                         | HTTP status | Error JSON key | Message                         |
|-----------------------------------|-------------|----------------|---------------------------------|
| `query` field missing             | 400         | error          | "query field is required"       |
| `query` is empty string           | 400         | error          | "query must not be empty"       |
| `query` exceeds 200 characters    | 400         | error          | "query exceeds maximum length"  |
| `max_results` is not a positive int | 400       | error          | "max_results must be a positive integer" |
| No entries match the query        | 200         | results        | Empty list, count 0             |
| Request body is not valid JSON    | 400         | error          | "request body must be valid JSON"|

## Knowledge base
The knowledge base is a Python list of dicts defined at module level in `app.py`.
It must contain at least 5 hardcoded entries, each with keys: id, title, body.
Matching is case-insensitive substring match on both title and body.
The snippet returned is the first 100 characters of the body.

## Testing criteria (the test suite must cover all of these)
1. Valid query that matches at least one entry returns HTTP 200 and correct fields
2. Valid query that matches no entries returns HTTP 200 with empty results list
3. Missing query field returns HTTP 400
4. Empty query string returns HTTP 400
5. Query longer than 200 characters returns HTTP 400
6. Non-positive max_results returns HTTP 400
7. Non-JSON body returns HTTP 400
8. max_results limits the number of returned results

## Files the agent may create or edit
- app.py
- test_app.py

## Files the agent must NOT touch
- spec.md
- system_prompt.txt
- critique.md
- pair_log.md
```

Save `spec.md`. Read through it once together and confirm every field is filled in.

##### Step 3: Write the system prompt in `system_prompt.txt`

The system prompt is the set of instructions the agent reads before it sees the task. It defines the rules. Open `system_prompt.txt` and fill in the template below. Every `[TODO]` must be completed.

```text
You are a careful Python backend developer. Your job is to implement a
feature according to the spec provided. Follow these rules without exception.

## Allowed files
You may read and edit ONLY these files:
- app.py
- test_app.py

You must NOT read, edit, create, or delete any other file.

## Required libraries
- Flask (for the web framework)
- pytest (for tests)
- No other third-party libraries are permitted.

## Explicit prohibitions
1. Do NOT make any external network calls (no requests.get, urllib, httpx, etc.).
2. Do NOT hardcode any credentials, tokens, or API keys.
3. Do NOT use eval() or exec() anywhere in the code.
4. You MUST include unit tests in test_app.py that cover every error case in the spec.
5. Do NOT modify the knowledge base list after it is defined at module level.

## Code style
- All functions must have docstrings.
- Use type hints on all function signatures.
- Follow PEP 8.

## [TODO: Add at least one more constraint specific to your project]
[TODO: Write your additional constraint here, e.g., "All error responses must
use the same JSON schema" or "The search function must be extracted into its
own helper function separate from the Flask route handler."]

## Output
When you are done, print a one-paragraph summary of what you changed and why.
```

Save `system_prompt.txt`.

##### Checkpoint 1, Answer these questions before moving to Part 2

Write your answers in `pair_log.md` under a heading `## Checkpoint 1`.

1. Look at your spec's error case table. For each row, identify which HTTP status code you chose and explain in one sentence why that status code is semantically correct for that error.
2. Read your system prompt's prohibition list. For each prohibition, describe a specific thing the agent might do if that prohibition were not there. Be concrete: name a function or pattern the agent might reach for.
3. Your spec says the snippet is the first 100 characters of the body. What happens if a body is shorter than 100 characters? Write the expected behavior as a one-sentence addition to your spec, then add it to `spec.md`.

#### Part 2: First Agent Run

**Estimated time: ~45 minutes**

You have a spec. You have a system prompt. Now you run the agent (the generator) and watch carefully.

##### Step 1: Launch the coding agent

Make sure you are inside your `cs357-coding-agents` directory. Run the agent using the command for your chosen tool.

**Claude Code:**

```bash
claude --system-prompt "$(cat system_prompt.txt)" "$(cat spec.md)"
```

Or, to use the interactive mode where you can watch the agent work step by step:

```bash
claude
```
Then paste your system prompt when prompted, and paste the contents of `spec.md` as the task.

**OpenCode:**

```bash
opencode run --system "$(cat system_prompt.txt)" --task "$(cat spec.md)"
```

Or interactively:

```bash
opencode
```

##### What you should see

> The agent will begin by reading existing files (it will likely read `app.py` and `test_app.py`, both of which are empty). It will then propose one or more file edits. For each edit, you will see a diff showing lines added (prefixed with `+`) and lines removed (prefixed with `-`). The agent may also print reasoning about what it is doing. **Do not accept any changes yet.** Your job right now is to watch, not approve; this is the draft the critic will judge.

##### Step 2: Capture the agent trace

Before you do anything else, save the agent's full output to a file. If you ran the agent in a terminal, scroll up and copy everything, then paste it into a new file:

```bash
# If your agent supports output redirection (Claude Code example):
claude --system-prompt "$(cat system_prompt.txt)" "$(cat spec.md)" 2>&1 | tee agent_trace_1.txt
```

If you used interactive mode, copy the terminal output manually and save it to `agent_trace_1.txt`. This file is a required deliverable.

##### Step 3: Save the raw diff without accepting

Most coding agents show you a diff before applying it. Save the proposed diff to a separate file:

```bash
# If using git, after the agent stages but before you commit:
git diff > diff_1.patch
```

If the agent does not use git, copy the proposed changes shown in the terminal and paste them into `diff_1.patch`. The file should look like this:

```diff
--- a/app.py
+++ b/app.py
@@ -0,0 +1,52 @@
+from flask import Flask, request, jsonify
+from typing import Any
+
+app = Flask(__name__)
+
+KNOWLEDGE_BASE = [
+    {"id": "1", "title": "Flask documentation", "body": "Flask is a micro web framework..."},
+    ...
+]
+
+def search_entries(query: str, max_results: int) -> list[dict[str, Any]]:
+    """Return knowledge base entries whose title or body contains the query."""
+    ...
```

> You should see two files modified: `app.py` (the implementation) and `test_app.py` (the tests). If the agent only produced one of these files, note that in `pair_log.md`; it may have violated the spec.

##### Troubleshooting, Part 2

**Problem: `claude: command not found` or `opencode: command not found`**

The tool is not on your PATH. Try:

```bash
npx @anthropic-ai/claude-code --version
# or
npx opencode-ai --version
```
If that works, use `npx claude` instead of `claude` throughout this direction, or re-run the npm install with the `-g` flag and open a new terminal.

**Problem: `Error: ANTHROPIC_API_KEY is not set` (or equivalent)**

You need to export your API key. Run:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```
Then rerun the agent command. If you do not have an API key, ask your instructor; do not share or hardcode keys.

**Problem: The agent immediately edits a file you prohibited in the system prompt**

Do not accept the change. Note the violation in `pair_log.md` with the exact file name and the line in your system prompt that prohibits it. Then try again with a stronger prompt: rewrite the prohibition to include the exact file path and add the phrase "under no circumstances."

##### Checkpoint 2, Answer these questions before moving to Part 3

Write your answers in `pair_log.md` under a heading `## Checkpoint 2`.

1. Open `diff_1.patch`. Count the number of lines added and the number of lines removed. How many distinct functions did the agent define in `app.py`? List them by name.
2. Did the agent produce a `test_app.py` file? If so, list the test function names. If not, does that constitute a violation of your system prompt? Explain.
3. Without running the code yet, read the implementation the agent proposed for the error case where `query` is an empty string. Does the code handle that case? Cite the specific lines from the diff.

#### Part 3: Diff Review and Critique

**Estimated time: ~45 minutes**

You have a diff. This is the heart of the direction: the diff review *is* the critique step of your generate/critique/refine loop. Read every line as though you were a senior engineer reviewing a colleague's pull request, except you need to be more skeptical than you would be with a human, because the agent has no stake in whether the code is correct, secure, or complete.

##### Step 1: Read through the entire diff

Open `diff_1.patch` in your editor and go line by line. You are looking for four categories of finding, the coding-agent counterpart to the issue list your JSON critic emits:

- **Correct**: the agent did this right; it matches the spec and is sound
- **Incorrect / broken**: the agent got this wrong; it does not match the spec or will not work
- **Missing**: something the spec requires that the agent did not implement
- **Security risk**: a pattern that could be exploited or that violates a system prompt prohibition

##### Step 2: Produce the critique document in `critique.md`

Open `critique.md` and fill in the template below. You must have at least one entry in each category. If you genuinely cannot find a security risk, look harder; common agent habits include using `eval()`, constructing SQL queries by string concatenation, returning raw exception messages to the client, or importing libraries your system prompt prohibited.

```markdown
# Critique Document

## Agent: [Claude Code | OpenCode; fill in which you used]
## Diff reviewed: diff_1.patch
## Reviewers: [Your names]
## Date: [Today's date]

---

## Category 1: Correct

List things the agent did correctly. Cite diff line numbers.

| Finding | Diff lines | Why it is correct |
|---------|-----------|-------------------|
| [TODO: e.g., "Returns HTTP 400 for missing query field"] | [TODO: line numbers] | [TODO: matches spec row 3] |
| [TODO] | [TODO] | [TODO] |

---

## Category 2: Incorrect / Broken

List things that are wrong or will not work as the spec requires.

| Finding | Diff lines | What the spec requires instead |
|---------|-----------|-------------------------------|
| [TODO: e.g., "max_results default is 10, not 5"] | [TODO] | [TODO: spec says default is 5] |
| [TODO] | [TODO] | [TODO] |

---

## Category 3: Missing

List spec requirements that are absent from the diff entirely.

| Missing requirement | Spec section | Impact if left out |
|--------------------|-------------|-------------------|
| [TODO: e.g., "No test for max_results limiting results"] | [TODO: Testing criteria #8] | [TODO: Spec requirement not verified] |
| [TODO] | [TODO] | [TODO] |

---

## Category 4: Security Risk

List patterns that could be exploited or that violate system prompt prohibitions.

| Finding | Diff lines | Risk description | Severity (Low / Med / High) |
|---------|-----------|-----------------|----------------------------|
| [TODO: e.g., "Exception message returned verbatim in error JSON"] | [TODO] | [TODO: Leaks internal stack trace to client] | [TODO] |
| [TODO] | [TODO] | [TODO] | [TODO] |

---

## System prompt compliance check

For each prohibition in your system_prompt.txt, state whether the agent complied.

| Prohibition | Complied? | Evidence (diff line or "not present in diff") |
|------------|-----------|----------------------------------------------|
| No external network calls | [TODO: Yes / No] | [TODO] |
| No hardcoded credentials | [TODO: Yes / No] | [TODO] |
| No eval() or exec() | [TODO: Yes / No] | [TODO] |
| Must include unit tests | [TODO: Yes / No] | [TODO] |
| [Your additional constraint] | [TODO: Yes / No] | [TODO] |
```

##### Step 3: Write a follow-up prompt

Create a file called `followup_prompt.txt`. This prompt will be your second message to the agent, the refine turn of the loop. It should address every finding in Categories 2, 3, and 4 of your critique document. Be precise; tell the agent exactly what to fix and why.

A good follow-up prompt looks like this:

```text
Thank you for the initial implementation. I have reviewed the diff and found
the following issues that must be corrected before I can accept the changes:

1. [INCORRECT] The default for max_results is 10 in your implementation but
   the spec requires 5. Change the default value on line [X] of app.py.

2. [MISSING] There is no test for the case where max_results limits the
   number of returned results (spec testing criterion #8). Add a test named
   test_max_results_limit to test_app.py.

3. [SECURITY] The exception handler on line [X] returns str(e) in the JSON
   response. This leaks internal error details to the client. Replace it with
   a generic message: "an unexpected error occurred".

4. [TODO: Add one entry for each finding in your critique's Categories 2-4]

Do not change anything else. Do not touch spec.md, system_prompt.txt,
critique.md, or pair_log.md.
```

##### Step 4: Run the second agent iteration

Run the agent again, this time using your follow-up prompt as the task:

**Claude Code:**

```bash
claude --system-prompt "$(cat system_prompt.txt)" "$(cat followup_prompt.txt)" 2>&1 | tee agent_trace_2.txt
```

**OpenCode:**

```bash
opencode run --system "$(cat system_prompt.txt)" --task "$(cat followup_prompt.txt)" 2>&1 | tee agent_trace_2.txt
```

Save the new diff:

```bash
git diff > diff_2.patch
```

##### Step 5: Compare the two diffs

Open both `diff_1.patch` and `diff_2.patch` side by side. For each finding in your critique document, confirm whether the second diff addresses it; this is the convergence check of your loop. Add a column to each table in `critique.md`:

```markdown
| ... | Resolved in diff_2? (Yes / No / Partially) |
```

##### Troubleshooting, Part 3

**Problem: The agent repeated the same mistakes in the second diff**

This usually means your follow-up prompt was not specific enough. Rewrite the relevant instruction with an explicit line number reference and the exact text the agent should produce. Then run a third iteration if needed; there is no penalty for a third pass, but document it.

**Problem: The agent fixed what you asked but introduced a new bug**

This is extremely common. Add the new bug to a new row in your critique document under the correct category, write another follow-up prompt entry for it, and note in `pair_log.md` that you needed a third iteration.

**Problem: The agent edited a file you prohibited in your system prompt**

Do not accept the edit to the prohibited file. Use your agent's undo/reject mechanism, or restore the file with:

```bash
git checkout -- spec.md   # replace with the prohibited filename
```
Document the violation in `critique.md` under "System prompt compliance check."

##### Checkpoint 3, Answer these questions before moving to Part 4

Write your answers in `pair_log.md` under a heading `## Checkpoint 3`.

1. Compare `diff_1.patch` and `diff_2.patch`. List every finding from your critique document and state whether it was resolved, partially resolved, or not resolved in `diff_2.patch`. If anything was not resolved, explain why in one sentence.
2. Did the agent introduce any new issues in the second diff that were not present in the first? If so, describe them.
3. Look at the follow-up prompt you wrote. Which instruction was most effective (the agent followed it precisely)? Which was least effective? What would you write differently?

#### Part 4: Verification and Hardening

**Estimated time: ~30 minutes**

The agent's second diff is as good as you are going to get from it. Now you take over: accept the changes, verify the tests, add missing coverage, and run static analysis tools.

##### Step 1: Accept the final diff

Apply the final diff to your working directory:

```bash
git apply diff_2.patch
```

If you were not using git staging, the files may already be in place; verify that `app.py` and `test_app.py` are non-empty:

```bash
wc -l app.py test_app.py
```

> Expected: both files should have more than 10 lines.

##### Step 2: Run the agent-generated tests

Install Flask and pytest if needed, then run the tests:

```bash
pip install flask pytest
pytest test_app.py -v
```

> Expected output (all tests should pass):
> ```
> test_app.py::test_valid_query_returns_results PASSED
> test_app.py::test_query_with_no_matches PASSED
> test_app.py::test_missing_query_field PASSED
> ...
> X passed in 0.XXs
> ```

If any test fails, read the error message carefully. Do not edit `app.py` to make the test pass by cheating (e.g., hardcoding a return value); fix the actual bug. Document any failing test in `pair_log.md` and describe what you changed to fix it.

Look at the tests that exist and compare them against the eight testing criteria in your `spec.md`. Make a checklist: which criteria are covered, and which are missing?

##### Step 3: Add at least two missing tests

Open `test_app.py` and add two tests that the agent did not write. Use the starter template below as a guide. Replace every `[TODO]` with the actual test logic.

```python
def test_max_results_limit(client):
    """Verify that max_results limits the number of entries returned."""
    # TODO: Send a POST request with a query that would match more than 2 entries
    # and max_results set to 2. Assert that the response contains exactly 2 results.
    response = client.post(
        "/search",
        json={"query": "[TODO: a term that matches many entries]", "max_results": 2},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["results"]) == 2  # TODO: confirm this is the right assertion


def test_query_echoed_in_response(client):
    """Verify that the response echoes back the original query string."""
    # TODO: Send a POST request with a specific query string.
    # Assert that data["query"] equals the string you sent.
    response = client.post(
        "/search",
        json={"query": "[TODO: your test query]"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["query"] == "[TODO: the same query string]"
```

After adding your tests, run pytest again and confirm all tests still pass:

```bash
pytest test_app.py -v
```

Save the full pytest output to a file:

```bash
pytest test_app.py -v > test_output.txt 2>&1
```

##### Step 4: Run the flake8 linter

```bash
flake8 app.py test_app.py
```

> If the code passes with no issues, flake8 produces no output and exits with code 0:
> ```
> (no output)
> ```
>
> If there are style issues, you will see output like:
> ```
> app.py:14:1: E302 expected 2 blank lines, got 1
> app.py:23:80: E501 line too long (84 > 79 characters)
> test_app.py:8:5: W291 trailing whitespace
> ```

Fix any errors or warnings that flake8 reports. Then rerun until it exits cleanly. Save the final (clean) output:

```bash
flake8 app.py test_app.py > flake8_output.txt 2>&1; echo "Exit code: $?" >> flake8_output.txt
```

##### Step 5: Run the bandit security scanner

```bash
bandit -r app.py
```

> Bandit output looks like this:
> ```
> [main]  INFO    profile include tests: None
> [main]  INFO    profile exclude tests: None
> [main]  INFO    cli include tests: None
> [main]  INFO    cli exclude tests: None
> Run started: 2026-06-21 ...
>
> Test results:
>         No issues identified.
>
> Code scanned:
>         Total lines of code: 52
>         Total lines skipped (#nosec): 0
>
> Run metrics:
>         Total issues (by severity):
>                 Undefined: 0
>                 Low: 0
>                 Medium: 0
>                 High: 0
>         Total issues (by confidence):
>                 Undefined: 0
>                 Low: 0
>                 Medium: 0
>                 High: 0
> Files skipped (0):
> ```
>
> If bandit finds issues, you will see entries like:
> ```
> >> Issue: [B110:try_except_pass] Try, Except, Pass detected.
>    Severity: Low   Confidence: High
>    CWE: CWE-390 (https://cwe.mitre.org/data/definitions/390.html)
>    Location: app.py:31:4
> ```

Save the bandit output:

```bash
bandit -r app.py > bandit_output.txt 2>&1
```

##### Step 6: Address any high-severity findings

Read the bandit output. For each finding with **Severity: High** or **Severity: Medium**, you must fix the underlying issue in `app.py`. Do not use `# nosec` comments to silence findings without first understanding what they mean; if you disagree with a finding, document your reasoning in `pair_log.md` under a heading `## Security scanner findings`.

After any fixes, rerun both flake8 and bandit to confirm the fixes did not introduce new issues.

##### Troubleshooting, Part 4

**Problem: `ModuleNotFoundError: No module named 'flask'` when running pytest**

```bash
pip install flask
```
Then rerun pytest. If you are in a virtual environment, make sure it is activated.

**Problem: `ERRORS` in pytest output, a test raises an exception instead of failing cleanly**

Read the traceback. If it says `fixture 'client' not found`, the agent did not create a pytest fixture for the Flask test client. Add one manually at the top of `test_app.py`:

```python
import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client
```

**Problem: bandit reports `[B201:flask_debug_true]`, Flask app running in debug mode**

Check `app.py` for a line like `app.run(debug=True)`. Change `debug=True` to `debug=False`, or remove the `app.run()` call entirely if it is inside an `if __name__ == "__main__":` block that is not needed for testing.

##### Checkpoint 4, Answer these questions as part of your reflection

Write your answers in `pair_log.md` under a heading `## Checkpoint 4`.

1. How many of the eight spec testing criteria were covered by the agent's tests before you added your two? List which were covered and which were not.
2. Did flake8 find any issues that were not stylistic: that is, issues that indicated an actual logic problem or bad practice beyond formatting? If so, describe them.
3. Did bandit flag anything? If yes, describe the finding and what you changed. If no, explain in one sentence what bandit would have flagged if the agent had used `eval()` to parse the query string.

#### Deliverables (Direction 1)

If you choose this direction, include the following alongside your core Critique-and-Refine deliverables. Missing files will result in point deductions from the corresponding rubric category.

| File | Description |
|------|-------------|
| `spec.md` | Your completed feature specification |
| `system_prompt.txt` | Your system prompt with all TODOs filled in |
| `app.py` | The final accepted implementation |
| `test_app.py` | The final test file including your two added tests |
| `diff_1.patch` | The raw diff from the first agent run |
| `diff_1_annotated.patch` | The same diff with inline comments explaining each significant change (add `# COMMENT:` lines) |
| `critique.md` | Your completed critique document with the "Resolved in diff_2?" column filled in |
| `followup_prompt.txt` | The follow-up prompt you sent for the second iteration |
| `diff_2.patch` | The raw diff from the second agent run |
| `agent_trace_1.txt` | Full terminal output from the first agent run |
| `agent_trace_2.txt` | Full terminal output from the second agent run |
| `test_output.txt` | pytest output showing all tests passing |
| `flake8_output.txt` | flake8 output (clean or with documented fixes) |
| `bandit_output.txt` | bandit output (clean or with documented resolutions) |
| `pair_log.md` | Swap log with timestamps, all checkpoint answers, and security scanner findings section |

#### Extension Challenges (Direction 1)

These challenges are optional and will not affect your grade on the base rubric. They are progressively harder and are intended for pairs who finish early or want to go deeper.

##### Challenge 1: Deliberate ambiguity

Add one deliberately contradictory requirement to a copy of your spec: for example, "The endpoint must return results sorted alphabetically by title" combined with "The endpoint must return results in the order they appear in the knowledge base." Give this contradictory spec to the coding agent without any hint about the contradiction. Document exactly what the agent does: does it pick one interpretation silently, ask for clarification, implement both with a flag, or do something else? Write a one-paragraph analysis of what the agent's choice reveals about how it handles underspecified instructions.

##### Challenge 2: Two agents, one spec

Install both Claude Code and OpenCode (if you only have one, pair with another group that has the other). Run both agents on exactly the same `spec.md` and `system_prompt.txt`, in separate directories so they cannot influence each other. Compare the two `diff_1.patch` files. Answer: How do the implementations differ structurally? Which agent's tests were more complete? Did one agent violate a system prompt constraint that the other respected? Produce a side-by-side comparison table with at least five dimensions.

##### Challenge 3: Automated constraint violation harness

Write a Python script called `harness.py` that runs the coding agent multiple times with system prompts of varying strictness (you define three levels: minimal, moderate, strict) and, after each run, checks the resulting `app.py` for the presence of prohibited patterns using regex or AST inspection. For example, check whether `eval` appears, whether any `import` of a prohibited library appears, or whether any function is missing a docstring. Record the violation rate for each prompt level and produce a summary table. This gives you empirical data on how much system prompt strength actually changes agent behavior.

#### Reflection Prompts (Direction 1)

Answer each prompt in `pair_log.md` under a heading `## Reflection`. Write at least three to five sentences per prompt; one-sentence answers will not receive full credit.

1. **What did the coding agent do well that surprised you?** Describe a specific part of the implementation where the agent made a better choice than you expected, and explain what that reveals about what these models are trained on.

2. **Where did it make assumptions you had not anticipated, and how did those assumptions affect the output?** Give at least two concrete examples. For each, explain whether the assumption was reasonable given the spec, and what you would add to the spec or system prompt to prevent that assumption in the future.

3. **How did your system prompt constrain its behavior, and what slipped through the constraints anyway?** For each prohibition in your system prompt, state whether the agent complied on the first run. For anything that slipped through, propose a more precise formulation of the prohibition.

4. **Would you trust this code in production? What specifically would need to change before you would?** Think about more than just tests: consider rate limiting, input sanitization depth, error logging, deployment configuration, and dependency management. List at least four specific changes and explain the risk each one addresses.

5. **How does reviewing a coding agent's diff differ from reviewing a human colleague's pull request? What additional skepticism is warranted, and why?** Think about what you know about a human colleague that you do not know about the agent: their understanding of business context, their ability to ask clarifying questions, their stake in the outcome, and their track record. How do those differences change how you read a diff?

6. **If you were deploying this pattern at scale (hundreds of developers using coding agents daily), what organizational controls (beyond individual system prompts) would you want in place?** Consider: who approves system prompts before they are used? How do you audit what agents actually do versus what they are told to do? What happens when an agent produces code that passes all tests but is subtly wrong in a way tests do not catch? Name at least three concrete organizational controls and explain the failure mode each one addresses.

7. **If collaboration beyond your pair occurred, identify it.** Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.

8. **Approximately how many hours did this direction take** (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

</details>
