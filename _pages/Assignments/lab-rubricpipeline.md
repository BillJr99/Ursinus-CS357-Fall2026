---
layout: assignment
permalink: /Assignments/RubricPipeline
title: "CS357: Foundations of Artificial Intelligence - Lab: Rubric Pipeline"

info:
  coursenum: CS357
  purpose: "To industrialize an LLM judge you run into a batch grading pipeline, and to prove with human-agreement and bias tests whether it can be trusted."
  tilt:
    task: "Build a batch pipeline that scores submissions against a JSON rubric into a CSV, then validate it against blind human scores and measure a judge bias."
    criteria: "Assessed on the batch scoring pipeline, human-to-judge agreement on a blind calibration set, and an empirical bias measurement; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To build a batch pipeline that scores a folder of submissions against a JSON rubric using a local model and emits a CSV report with per-criterion evidence and a weighted total
    - To verify quoted evidence programmatically against source artifacts and report a hallucinated-evidence rate
    - To validate the judge against blind human scores on a calibration set using percent agreement or Cohen's kappa
    - To measure at least one judge bias empirically with a controlled experiment and propose a concrete countermeasure
    - To express the judge's expected behavior as a versioned, declarative eval configuration in an industry harness (promptfoo or Inspect AI) and demonstrate a regression run against a golden set
    - To design a structured evaluation dataset with golden, stylistic, and adversarial question categories that expose distinct failure modes in an agent
    - To implement multiple automated evaluation metrics including exact match, G-Eval LLM-as-judge scoring, and semantic similarity
    - To identify regressions and improvements by running a controlled before-and-after comparison on a well-defined eval set
    - To integrate the evaluation harness into a CI/CD pipeline that enforces a minimum pass rate on every code push
    - To instrument an AI agent with OpenTelemetry spans, capturing LLM call metadata, tool call metadata, and retrieval metadata as structured attributes
    - To design span attribute schemas that balance diagnostic value against verbosity and PII exposure
    - To analyze distributed traces in Jaeger or Zipkin to locate latency hotspots and diagnose failure modes
    - To write operational alert rules and a runbook that translates trace-derived thresholds into on-call actions
    - To implement test-driven development practices for non-deterministic agent outputs using semantic, format, and safety test patterns
    - To configure and run automated code quality tools including formatters, linters, and coverage reporters on an agentic Python project
    - To construct a GitHub Actions CI pipeline that validates formatting, linting, and test coverage on every push and pull request
    - To package and publish an AI agent as a pip-installable wheel to TestPyPI and as a container image to the GitHub Container Registry
  rubric:
    - weight: 25
      description: Pipeline Implementation
      preemerging: The pipeline fails to run due to major issues, or the program fails to run
      beginning: The pipeline runs but fails on the test submissions due to one or more minor issues
      progressing: The pipeline scores the corpus of submissions against the rubric and emits well formed results (CSV on the code route; captured harness output on Direction 0), with a fragile component such as output-parsing fallback or evidence capture
      proficient: The batch scorer robustly processes the full synthetic corpus end-to-end and emits one result row per artifact with per-criterion outcomes and an overall result (code route — CSV with level labels, quoted evidence strings, and a weighted total; Direction 0 — per-criterion judge verdicts across all dataset items); malformed or unusable judge output is surfaced rather than guessed at (code route — a "REVIEW_NEEDED" flag with the raw output logged; Direction 0 — noted and re-run); the rubric, model, paths, and settings live in configuration files, not hardcoded; a terminal screenshot or log confirms the end-to-end run on the full corpus
    - weight: 20
      description: Human Agreement Validation
      preemerging: No human validation is attempted
      beginning: Human scores exist but are collected after seeing the judge output, or agreement is not quantified
      progressing: Both partners independently score a calibration set before running the judge, and human to human and human to judge agreement are reported
      proficient: Both partners independently score the calibration set (at least eight artifacts on the code route; all fifteen on Direction 0) blind to the judge; agreement is quantified per criterion as percent agreement or Cohen's kappa (Direction 0 uses percent agreement plus the written disagreement analysis of the three worst mismatches); the criterion with the worst human-to-judge gap is identified; a rubric revision is tested and before/after agreement is reported in a table; all human score sheets are included in the submission
    - weight: 20
      description: Bias Measurement
      preemerging: No bias probe is attempted
      beginning: A bias is discussed but not measured
      progressing: One judge bias (position/order, verbosity, or byline) is measured with a controlled experiment
      proficient: At least one judge bias is measured with a controlled experiment (code route — at least four matched pairs; Direction 0 — the reordered and padded dataset variants over all items); the effect is quantified (e.g., "the judge awarded 0.8 more points on average when the longer essay appeared first," or "padding flipped 5 of 60 verdicts"); a countermeasure is implemented or prescribed with a concrete code, configuration, or prompt change; the residual risk after the countermeasure is stated honestly
    - weight: 15
      description: Evidence Verification
      preemerging: The judge's evidence or stated reasoning is not collected
      beginning: The judge's evidence or stated reasoning is collected but never checked against the source
      progressing: The judge's evidence or stated reasoning is spot checked by hand with a reported faithfulness rate
      proficient: The judge's grounding is verified against the source artifacts (code route — evidence quotes checked programmatically by exact substring or fuzzy match with the stated threshold, hallucinated quotes flagged in the CSV with a "HALLUCINATED_EVIDENCE" marker, and the hallucinated evidence rate reported, e.g., "3 of 48 quotes, 6.25%"; Direction 0 — the judge's stated reasoning for the three worst human-judge mismatches is checked line-by-line against the answer text, with unfaithful or fabricated reasoning called out in the disagreement analysis)
    - weight: 10
      description: Reproducible Eval Harness
      preemerging: No declarative eval configuration is attempted
      beginning: A harness (promptfoo or Inspect AI) is installed and runs, but the eval cases do not correspond to the pipeline's golden set, or results are not captured
      progressing: The judge's expected behavior is expressed as a versioned eval configuration over the golden calibration set, and one full harness run against the local model is captured
      proficient: A versioned eval configuration (promptfoo YAML or an Inspect AI task) encodes the calibration set with at least one assertion per case; the configuration is committed alongside the submission; a before-and-after regression run demonstrates that a deliberate change to the judge prompt or rubric is caught by the harness, with both result sets included and a short interpretation in the readme (on Direction 0 the whole route is such a configuration, and Part E's regression diff satisfies this row)
    - weight: 10
      description: Writeup, Reflection, and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The work is submitted according to the directions, including a readme writeup, a pair log with at least two timestamped role swaps, all human score sheets, and reflection answers that each cite a specific agreement figure (kappa or percent agreement), bias effect size, or evidence-faithfulness finding from the lab rather than restating the prompt
  readings:
    - rtitle: "LLM-as-Judge Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmasjudge.md"
    - rtitle: "Evaluating Outputs Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md"
    - rtitle: "Testing Agents Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-testingagents.md"
    - rtitle: "LLM as Judge Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmasjudge.md"
    - rtitle: "Observability Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-observability.md"
    - rtitle: "Publishing Activity: GHCR, Docker Hub, and npm"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-publishing.md"
    - rtitle: "Coding Agents Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-codingagents.md"
    - rtitle: "Ollama API Documentation"
      rlink: "https://github.com/ollama/ollama/blob/main/docs/api.md"
    - rtitle: "promptfoo Documentation (Part 5, Option A)"
      rlink: "https://www.promptfoo.dev/docs/intro/"
    - rtitle: "Inspect AI Documentation (Part 5, Option B)"
      rlink: "https://inspect.aisi.org.uk/"
    - rtitle: "pytest Documentation"
      rlink: "https://docs.pytest.org/en/stable/"
    - rtitle: "Python Packaging User Guide"
      rlink: "https://packaging.python.org/en/latest/tutorials/packaging-projects/"

tags:
  - evaluation
  - llm-as-judge
  - pipelines
  - testing
  - ci
  - observability
  - opentelemetry
  - monitoring
  - ci-cd
  - publishing
  - tdd

---

In this lab, you and your partner will industrialize the in-class judge into a batch grading pipeline: a JSON rubric and a folder (or ZIP) of submissions go in; a CSV of per-criterion scores, quoted evidence, and weighted totals comes out; and, crucially, you will measure whether the judge deserves to be trusted. **All submissions in this lab are synthetic artifacts you author yourselves; no real student work may be used.** This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

**See the course schedule for the assigned and due dates.**

This lab has two pathways: the **code route** below (core Parts 1–5, then one of Directions 1–3), or the **low-code route**, [Direction 0: The promptfoo Route]({{ site.baseurl }}/Assignments/RubricPipeline/Direction0), which meets the same objectives declaratively and replaces the core Parts 1–4 coding. See "Choose Your Pathway and Direction" near the end of this page before you start.

---

## Before You Start

**Prerequisite concepts** — complete these activities before writing any code:

- [LLM-as-Judge Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmasjudge.md) — judge prompting, structured output, fail-closed policies
- [Evaluating Outputs Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md) — agreement metrics, bias taxonomy, evidence faithfulness

**Tools to install:**

```bash
# All you need is requests (Ollama) and optionally fuzzywuzzy for Part 3
pip install requests
pip install thefuzz python-Levenshtein   # optional; for fuzzy evidence matching in Part 3
```

**Health check:**

```bash
# Verify Ollama is running and your model responds to structured output requests
python -c "
import requests, json
r = requests.post('http://localhost:11434/api/chat', json={
    'model': 'llama3.2',
    'messages': [{'role': 'user', 'content': 'Respond with only this JSON: {\"test\": \"ok\"}'}],
    'stream': False
})
print(r.json()['message']['content'])
"
```

Expected output:

```json
{"test": "ok"}
```

If you see connection errors, start Ollama: `ollama serve` in a separate terminal.

**Estimated time budget:**

| Part | Task | Estimated time |
|------|------|----------------|
| Part 1 | The Pipeline | 75–90 min |
| Part 2 | Validate Against Humans | 45–60 min |
| Part 3 | Verify the Evidence | 30–45 min |
| Part 4 | Measure a Bias | 45–60 min |
| Part 5 | Reproducible Evals with a Declarative Harness | 45–60 min |
| Writeup | Readme and reflection | 30–45 min |

**Totals:**

| Pathway | Total time |
|---------|------------|
| Core code route (Parts 1–5 + writeup) | **≈ 4.5–6 h** |
| ...plus your chosen code-route direction (1, 2, or 3) | **adds ≈ 3–6 h** |
| **OR** Direction 0, the promptfoo low-code route (replaces core Parts 1–4 coding) | **≈ 7–9 h total** |

Plan multiple pair sessions — no pathway through this lab fits in one sitting.

---

## Part 1: The Pipeline

Author a JSON rubric with at least four criteria, each with four observable levels and integer weights summing to 100, for a short artifact type of your choosing (a persuasive paragraph, a function with docstring, a lab abstract). Then implement a pipeline that:

1. Walks a folder or ZIP of text submissions (configuration externalized: paths, model, rubric file, temperature, seed).
2. Prompts your local model to award a level per criterion **with a quoted sentence of evidence for each score**, returning strict JSON.
3. Fails closed on malformed judge output (flag the row for human review rather than guessing), with located exception messages and tracebacks.
4. Emits a CSV with one row per submission: filename, per-criterion level and evidence, weighted total, and any flags.

Author at least twelve synthetic submissions spanning the quality range, including at least two edge cases (empty file, off-topic content).

### Step-by-step guide

**Step 1: Create your rubric and configuration files.**

`rubric.json` (example for a persuasive paragraph):

```json
{
  "artifact_type": "persuasive_paragraph",
  "criteria": [
    {
      "id": "C1",
      "name": "Claim",
      "weight": 30,
      "levels": {
        "4": "A clear, specific, arguable claim is stated in the first sentence.",
        "3": "A claim is present but is vague or stated later in the paragraph.",
        "2": "A topic is identified but no arguable claim is made.",
        "1": "No claim or topic can be identified."
      }
    },
    {
      "id": "C2",
      "name": "Evidence",
      "weight": 30,
      "levels": {
        "4": "At least two distinct pieces of evidence directly support the claim, each connected with explicit reasoning.",
        "3": "Evidence is present but only one piece is connected to the claim with reasoning.",
        "2": "Evidence is mentioned but not connected to the claim.",
        "1": "No evidence is present."
      }
    },
    {
      "id": "C3",
      "name": "Counterargument",
      "weight": 20,
      "levels": {
        "4": "A counterargument is acknowledged and refuted with a specific rebuttal.",
        "3": "A counterargument is acknowledged but the rebuttal is weak or generic.",
        "2": "A counterargument is hinted at but not named or addressed.",
        "1": "No counterargument is addressed."
      }
    },
    {
      "id": "C4",
      "name": "Conclusion",
      "weight": 20,
      "levels": {
        "4": "The paragraph ends with a sentence that restates the claim in new words and signals its significance.",
        "3": "A concluding sentence is present but merely repeats the opening claim.",
        "2": "The paragraph ends abruptly without a concluding sentence.",
        "1": "The paragraph is incomplete or ends mid-thought."
      }
    }
  ]
}
```

`config.json`:

```json
{
  "model": "llama3.2",
  "ollama_url": "http://localhost:11434/api/chat",
  "temperature": 0.0,
  "seed": 42,
  "rubric_file": "rubric.json",
  "submissions_dir": "submissions",
  "output_csv": "grades.csv"
}
```

**Step 2: Author twelve synthetic submissions.**

Create a `submissions/` folder. Write twelve `.txt` files covering the full quality range:

| File | Description |
|------|-------------|
| `s01_excellent.txt` | All four criteria at level 4 |
| `s02_good.txt` | Three criteria at 4, one at 3 |
| `s03_adequate.txt` | Mix of 3s and 2s |
| `s04_poor.txt` | Mostly 1s and 2s |
| `s05_no_claim.txt` | Good evidence but no arguable claim (tests C1) |
| `s06_no_evidence.txt` | Strong claim, no evidence at all (tests C2) |
| `s07_no_counter.txt` | Good claim and evidence but ignores counterarguments (tests C3) |
| `s08_abrupt_end.txt` | Good opening but ends mid-sentence (tests C4) |
| `s09_off_topic.txt` | Edge case: content about a completely unrelated topic |
| `s10_empty.txt` | Edge case: empty file |
| `s11_verbose.txt` | Same content as s01 but padded with filler sentences (for bias probe in Part 4) |
| `s12_borderline.txt` | Genuinely ambiguous: reasonable people could disagree on two criteria |

Make sure you know the expected level for each criterion in each file — you will need this for Part 2.

**Step 3: Implement the judge prompt function.**

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

def build_judge_prompt(submission_text, rubric):
    """
    Build the system and user messages for the judge.
    Returns (system_message, user_message).
    """
    criteria_section = ""
    for c in rubric["criteria"]:
        criteria_section += f"\n{c['id']} — {c['name']} (weight: {c['weight']})\n"
        for level, desc in sorted(c["levels"].items(), reverse=True):
            criteria_section += f"  Level {level}: {desc}\n"

    system_message = (
        "You are an objective grading assistant. "
        "You will be given an artifact and a rubric. "
        "For each criterion, award a level (1-4) and quote ONE sentence from the artifact as evidence. "
        "The evidence must be a verbatim quote from the artifact — do not paraphrase.\n\n"
        "Return ONLY valid JSON in this exact format:\n"
        "{\n"
        '  "grades": [\n'
        '    {"criterion_id": "C1", "level": 3, "evidence": "exact quote from artifact"},\n'
        "    ...\n"
        "  ]\n"
        "}\n\n"
        "If the artifact is empty or off-topic, award level 1 for all criteria and use the evidence: 'N/A'.\n"
        "Do not add any text outside the JSON object."
    )

    user_message = (
        f"RUBRIC:\n{criteria_section}\n\n"
        f"ARTIFACT TO GRADE:\n{submission_text}"
    )

    return system_message, user_message

def judge_submission(submission_text, rubric, config):
    """
    Run the judge on a single submission.
    Returns (grades_dict, raw_output) where grades_dict has the parsed JSON,
    or (None, raw_output) if parsing fails.
    """
    system_msg, user_msg = build_judge_prompt(submission_text, rubric)
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "stream": False,
        "options": {"temperature": config["temperature"], "seed": config["seed"]}
    }

    try:
        response = requests.post(config["ollama_url"], json=payload, timeout=90)
        response.raise_for_status()
        raw = response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab5:judge_submission:network] {e}")
        traceback.print_exc()
        raise

    # Parse JSON; fail closed on malformed output
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        parsed = json.loads(clean)
        assert "grades" in parsed and isinstance(parsed["grades"], list)
        return parsed, raw
    except Exception as e:
        print(f"[lab5:judge_submission:json_parse] Malformed output — flagging for review. Error: {e}. Raw: {raw[:300]!r}")
        return None, raw
```

**Step 4: Implement the batch pipeline and CSV emitter.**

```python
import pathlib
import csv
import zipfile

def compute_weighted_total(grades, rubric):
    """Compute the weighted total score (0-100) from the grades list."""
    criterion_weights = {c["id"]: c["weight"] for c in rubric["criteria"]}
    total = 0
    for grade in grades:
        cid = grade["criterion_id"]
        level = int(grade["level"])
        weight = criterion_weights.get(cid, 0)
        # Level 4 = full weight, Level 1 = 25% weight
        total += weight * (level / 4)
    return round(total, 1)

def run_pipeline(config):
    """
    Walk the submissions directory, grade each file, and write grades.csv.
    """
    rubric = load_rubric(config)
    submissions_path = pathlib.Path(config["submissions_dir"])
    output_csv = config["output_csv"]

    # Collect all .txt and .md files
    files = sorted(list(submissions_path.glob("*.txt")) + list(submissions_path.glob("*.md")))
    print(f"Found {len(files)} submissions in {submissions_path}")

    # Build CSV column headers
    criterion_ids = [c["id"] for c in rubric["criteria"]]
    fieldnames = ["filename", "weighted_total", "flags"]
    for cid in criterion_ids:
        fieldnames += [f"{cid}_level", f"{cid}_evidence"]

    rows = []
    for i, filepath in enumerate(files):
        print(f"\n[{i+1}/{len(files)}] Grading {filepath.name}...")
        text = filepath.read_text(encoding="utf-8", errors="replace").strip()

        row = {"filename": filepath.name, "flags": ""}

        if not text:
            # Empty file edge case
            row["flags"] = "EMPTY_FILE"
            row["weighted_total"] = 0.0
            for cid in criterion_ids:
                row[f"{cid}_level"] = 1
                row[f"{cid}_evidence"] = "N/A"
            rows.append(row)
            print(f"  Flagged: EMPTY_FILE")
            continue

        grades_dict, raw_output = judge_submission(text, rubric, config)

        if grades_dict is None:
            # Fail closed: flag for human review
            row["flags"] = f"REVIEW_NEEDED|raw={raw_output[:100]!r}"
            row["weighted_total"] = "N/A"
            for cid in criterion_ids:
                row[f"{cid}_level"] = "N/A"
                row[f"{cid}_evidence"] = "N/A"
        else:
            grades = grades_dict["grades"]
            row["weighted_total"] = compute_weighted_total(grades, rubric)
            for grade in grades:
                cid = grade["criterion_id"]
                row[f"{cid}_level"] = grade["level"]
                row[f"{cid}_evidence"] = grade.get("evidence", "")
            print(f"  Weighted total: {row['weighted_total']}")

        rows.append(row)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Results written to {output_csv}")
    return rows

if __name__ == "__main__":
    config = load_config()
    run_pipeline(config)
```

**Step 5: Run the pipeline and inspect the output.**

```bash
python pipeline.py
```

Expected output:

```
Found 12 submissions in submissions

[1/12] Grading s01_excellent.txt...
  Weighted total: 95.0
[2/12] Grading s02_good.txt...
  Weighted total: 85.0
...
[10/12] Grading s10_empty.txt...
  Flagged: EMPTY_FILE
...
Done. Results written to grades.csv
```

Open `grades.csv` and verify it has 12 rows with the correct columns. Check that `s10_empty.txt` shows `EMPTY_FILE` in the flags column.

### Troubleshooting — Part 1

**`REVIEW_NEEDED` appears for most submissions**
The model is not returning valid JSON. First, print the raw output to see what it is producing. Common fixes: (1) Add `"Keep your response to ONLY the JSON object, nothing else."` at the end of the system prompt. (2) Strip markdown code fences with `.lstrip("```json").lstrip("```")` — already in the template. (3) Try a simpler artifact type with fewer rubric criteria.

**`weighted_total` values are all the same (e.g., 62.5 for every submission)**
The model may be awarding level 2 for everything. Check `C1_level` and `C2_level` columns — if they are all 2, your rubric descriptors may be ambiguous at levels 1 and 3. Make the level 4 descriptor very specific so the model can distinguish excellent work from average work.

**The pipeline is slow (>2 minutes per submission)**
Reduce the number of rubric criteria to 3 for testing, then add the fourth back when the code works. Also check that `"stream": False` is in your payload — streaming responses parsed as non-streaming will time out.

---

> **Checkpoint: Before moving to Part 2, make sure you can answer:**
> 1. What does "fail closed" mean in the context of this pipeline, and what specific behavior does your code exhibit when the judge returns malformed JSON?
> 2. Open `grades.csv`. Does the `weighted_total` for `s01_excellent.txt` match your expectation? If not, which criterion level is wrong, and why might the judge have awarded that level?
> 3. What two edge cases did you include, and how does the pipeline handle each one? (Verify by reading the CSV rows for those files.)

---

## Part 2: Validate Against Humans

Before running the judge, you and your partner **independently** hand-score a calibration set of at least eight submissions. Then run the judge and report: human-to-human agreement per criterion, and human-to-judge agreement per criterion. Identify the criterion with the worst machine-human gap, revise its level descriptors toward observability, and report agreement before and after the revision.

### Step-by-step guide

**Step 1: Score independently BEFORE running the pipeline.**

This order matters: if you see the judge's scores first, your human scores will be anchored to them and the comparison will be biased.

Each partner scores eight submissions on a separate sheet (paper or spreadsheet). For each criterion, record the level (1-4) and a one-sentence justification. Do not discuss scores with your partner until both sheets are complete.

Template for your score sheet:

```
Scorer: [your name]   Date: [today]
Submission: s01_excellent.txt

C1 (Claim): Level ___ | Justification: ___
C2 (Evidence): Level ___ | Justification: ___
C3 (Counterargument): Level ___ | Justification: ___
C4 (Conclusion): Level ___ | Justification: ___
```

**Step 2: Compute human-to-human agreement.**

```python
# After both partners have scored independently:
# partner_a_scores[file][criterion] = level (int)
# partner_b_scores[file][criterion] = level (int)

def percent_agreement(scores_a, scores_b, criterion_id, files):
    """Exact-match agreement rate for one criterion."""
    matches = sum(
        1 for f in files
        if scores_a[f][criterion_id] == scores_b[f][criterion_id]
    )
    return matches / len(files)

# Example (fill in your actual scores):
partner_a = {
    "s01_excellent.txt": {"C1": 4, "C2": 4, "C3": 4, "C4": 4},
    "s12_borderline.txt": {"C1": 3, "C2": 3, "C3": 2, "C4": 3},
    # ... add all 8 files
}
partner_b = {
    "s01_excellent.txt": {"C1": 4, "C2": 4, "C3": 4, "C4": 4},
    "s12_borderline.txt": {"C1": 3, "C2": 2, "C3": 3, "C4": 3},
    # ...
}

calibration_files = list(partner_a.keys())
criteria = ["C1", "C2", "C3", "C4"]

print("Human-to-human agreement:")
for cid in criteria:
    agr = percent_agreement(partner_a, partner_b, cid, calibration_files)
    print(f"  {cid}: {agr:.0%}")
```

Expected output (your numbers will differ):

```
Human-to-human agreement:
  C1: 87%
  C2: 75%
  C3: 62%
  C4: 87%
```

**Step 3: Compare human scores to judge scores.**

```python
# Load judge scores from grades.csv
import csv

judge_scores = {}
with open("grades.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        filename = row["filename"]
        judge_scores[filename] = {
            cid: int(row[f"{cid}_level"]) if row[f"{cid}_level"] not in ("N/A", "") else None
            for cid in criteria
        }

print("\nHuman A to Judge agreement:")
for cid in criteria:
    files_with_valid = [f for f in calibration_files if judge_scores.get(f, {}).get(cid) is not None]
    agr = percent_agreement(partner_a, judge_scores, cid, files_with_valid)
    print(f"  {cid}: {agr:.0%}")
```

**Step 4: Identify the weakest criterion and revise it.**

The weakest criterion is the one with the lowest human-to-judge agreement. Revise its level descriptors to be more observable (specific, countable, anchored to visible text features). Update `rubric.json`, re-run the pipeline on the same eight files, and report the before/after agreement table.

Example revision for a vague criterion:

- **Before**: "C3 Level 4: A counterargument is acknowledged and refuted."
- **After**: "C3 Level 4: A sentence explicitly names an opposing view (e.g., 'Some argue that...') AND a following sentence provides a specific rebuttal that gives a reason the counterargument does not hold."

### Troubleshooting — Part 2

**Human-to-human agreement is very low (below 50%) on one criterion**
This means the criterion is poorly defined, not that your scores are wrong. This is valuable data. In your writeup, explain what made that criterion ambiguous and how your rubric revision addresses it. Do NOT revise your scores to match your partner — disagreement is the finding.

**Judge scores are missing from `grades.csv` for some calibration files**
Those files triggered `REVIEW_NEEDED`. Check the console log for the raw output. You may need to retry those files with a slightly rephrased system prompt.

**You realize you designed your synthetic submissions to be too obvious**
If levels 1 and 4 are easy to distinguish but levels 2 and 3 look the same, your calibration will show high agreement at the extremes and low agreement in the middle. This is a real problem in rubric design — note it in your writeup and consider whether `s12_borderline.txt` falls in this gap.

---

> **Checkpoint: Before moving to Part 3, make sure you can answer:**
> 1. Which criterion had the worst human-to-judge agreement? What specific wording in that criterion's level descriptors made it ambiguous?
> 2. After your rubric revision, did human-to-judge agreement improve for that criterion? If it did not, what further change might help?
> 3. Why must human scores be collected BEFORE running the judge? What specific bias would you introduce by reversing the order?

---

## Part 3: Verify the Evidence

Implement a programmatic check that each quoted evidence string actually appears in the source submission (exact substring or a fuzzy match with a stated threshold). Report the **hallucinated evidence rate** across your corpus, and flag offending rows in the CSV.

### Step-by-step guide

**Step 1: Implement the evidence verification function.**

```python
def verify_evidence(evidence_quote, submission_text, fuzzy_threshold=90):
    """
    Check whether evidence_quote appears in submission_text.
    First tries exact substring match. Falls back to fuzzy match.
    Returns (is_faithful, match_type, match_score).
    match_type: "exact", "fuzzy", or "hallucinated"
    """
    if not evidence_quote or evidence_quote.strip() in ("N/A", ""):
        return True, "n/a", 100  # N/A evidence is treated as faithful

    # Exact substring match (case-insensitive)
    if evidence_quote.lower() in submission_text.lower():
        return True, "exact", 100

    # Fuzzy match (optional — requires thefuzz)
    try:
        from thefuzz import fuzz
        score = fuzz.partial_ratio(evidence_quote.lower(), submission_text.lower())
        if score >= fuzzy_threshold:
            return True, "fuzzy", score
        else:
            return False, "hallucinated", score
    except ImportError:
        # If thefuzz is not installed, treat non-exact as hallucinated
        return False, "hallucinated", 0
```

**Step 2: Run verification over the full CSV and re-emit with flags.**

```python
def verify_all_evidence(csv_path, submissions_dir, rubric, fuzzy_threshold=90):
    """
    Read grades.csv, check every evidence quote, and rewrite with HALLUCINATED_EVIDENCE flags.
    Returns (hallucination_count, total_evidence_count).
    """
    rows = []
    criteria = [c["id"] for c in rubric["criteria"]]
    hallucinated = 0
    total = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ["evidence_flags"]
        for row in reader:
            filename = row["filename"]
            filepath = pathlib.Path(submissions_dir) / filename
            try:
                submission_text = filepath.read_text(encoding="utf-8", errors="replace")
            except FileNotFoundError:
                row["evidence_flags"] = "FILE_NOT_FOUND"
                rows.append(row)
                continue

            evidence_issues = []
            for cid in criteria:
                evidence = row.get(f"{cid}_evidence", "")
                if row.get(f"{cid}_level") in ("N/A", "", "1"):
                    continue  # Skip N/A and level-1 (often "N/A" evidence)
                faithful, match_type, score = verify_evidence(evidence, submission_text, fuzzy_threshold)
                total += 1
                if not faithful:
                    hallucinated += 1
                    evidence_issues.append(f"{cid}:HALLUCINATED(score={score})")
                    print(f"  [HALLUCINATED] {filename} | {cid} | Quote: {evidence!r}")

            row["evidence_flags"] = "|".join(evidence_issues) if evidence_issues else ""
            # Update flags column
            existing_flags = row.get("flags", "")
            if evidence_issues:
                row["flags"] = (existing_flags + "|HALLUCINATED_EVIDENCE").strip("|")
            rows.append(row)

    # Rewrite CSV with evidence_flags column
    verified_csv = csv_path.replace(".csv", "_verified.csv")
    with open(verified_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    rate = hallucinated / total if total > 0 else 0
    print(f"\nEvidence verification complete.")
    print(f"Hallucinated: {hallucinated}/{total} = {rate:.1%}")
    print(f"Verified CSV written to: {verified_csv}")
    return hallucinated, total

# Run it
config = load_config()
rubric = load_rubric(config)
verify_all_evidence(config["output_csv"], config["submissions_dir"], rubric)
```

Expected output:

```
  [HALLUCINATED] s03_adequate.txt | C2 | Quote: 'Studies consistently demonstrate that...'
Evidence verification complete.
Hallucinated: 3/42 = 7.1%
Verified CSV written to: grades_verified.csv
```

Include the hallucination rate and any verbatim hallucinated quotes in your readme.

### Troubleshooting — Part 3

**Hallucinated rate is 0% even when you expected some hallucinations**
The judge may be copying sentences so faithfully that even paraphrases pass the fuzzy threshold. Lower `fuzzy_threshold` to 80 to see if any marginal quotes appear. Alternatively, check a few quotes by hand to verify the automated check is working correctly.

**Hallucinated rate is very high (above 30%)**
The model may be paraphrasing rather than quoting. Strengthen the prompt: add "The evidence MUST be a verbatim copy-paste from the artifact. Do not rephrase." If paraphrasing persists, lower your fuzzy threshold to 85 and accept partial matches as faithful.

**`thefuzz` import fails**
Run `pip install thefuzz python-Levenshtein`. If you cannot install it, use Python's built-in `difflib.SequenceMatcher` as an alternative:

```python
from difflib import SequenceMatcher
score = SequenceMatcher(None, evidence.lower(), submission_text.lower()).ratio() * 100
```

---

> **Checkpoint: Before moving to Part 4, make sure you can answer:**
> 1. What is your hallucinated evidence rate? Is it higher or lower than you expected?
> 2. Look at one hallucinated quote. Is it a fabrication (completely invented), a paraphrase (real idea, different words), or a conflation (combines two real sentences)? Which is most dangerous in a grading pipeline and why?
> 3. If a quote passes fuzzy matching at 85% similarity but not exact match, is it faithful? Does your answer change depending on the length of the quote?

---

## Part 4: Measure a Bias

Design and run a controlled probe of one judge pathology from class: position bias (A/B comparisons in both orders), verbosity bias (padded versus unpadded versions of the same content), or byline bias (identical essays with varied author names). Quantify the effect, implement or prescribe a countermeasure, and state honestly what risk remains.

### Step-by-step guide

**Step 1: Choose and design your bias probe.**

**Option A — Verbosity bias** (recommended for this lab): Compare scores for `s01_excellent.txt` versus `s11_verbose.txt` (same content, padded with filler sentences). If the judge scores the verbose version higher, that is verbosity bias.

**Option B — Position bias**: Present two submissions in a comparison prompt (A then B, then B then A). Check if the judge consistently favors the first-presented submission.

**Option C — Byline bias**: Add a fake author byline to otherwise identical submissions (e.g., "Written by: Sarah Chen" vs. "Written by: [no name]" vs. a name that correlates with demographic assumptions). Check if scores differ.

**Step 2: Run the probe and record results.**

For verbosity bias (at least 4 matched pairs):

```python
# Create 4 versions of different quality submissions with and without padding
FILLER = "\n\nFurthermore, it is important to consider the various aspects of this topic from multiple perspectives, as has been noted by many scholars and practitioners in the field."

matched_pairs = [
    ("s01_excellent.txt", "s01_verbose.txt"),  # s01_verbose = s01 + FILLER * 3
    ("s04_poor.txt", "s04_verbose.txt"),
    ("s07_no_counter.txt", "s07_verbose.txt"),
    ("s03_adequate.txt", "s03_verbose.txt"),
]

# Create the verbose versions
for original, verbose_name in matched_pairs:
    original_text = (pathlib.Path(config["submissions_dir"]) / original).read_text()
    verbose_text = original_text + FILLER * 3
    (pathlib.Path(config["submissions_dir"]) / verbose_name).write_text(verbose_text)

# Grade all pairs and compare totals
results = {}
for original, verbose in matched_pairs:
    for fname in [original, verbose]:
        text = (pathlib.Path(config["submissions_dir"]) / fname).read_text()
        grades, _ = judge_submission(text, rubric, config)
        total = compute_weighted_total(grades["grades"], rubric) if grades else None
        results[fname] = total
        print(f"  {fname}: {total}")

# Compute the average bias
deltas = []
for original, verbose in matched_pairs:
    if results[original] and results[verbose]:
        delta = results[verbose] - results[original]
        deltas.append(delta)
        print(f"  {original} -> {verbose}: delta = {delta:+.1f}")

avg_delta = sum(deltas) / len(deltas) if deltas else 0
print(f"\nAverage verbosity bias: {avg_delta:+.1f} points (positive = verbose scores higher)")
```

Expected output:

```yaml
  s01_excellent.txt: 95.0
  s01_verbose.txt: 97.5
  s04_poor.txt: 32.5
  s04_verbose.txt: 40.0
  ...
Average verbosity bias: +4.2 points (positive = verbose scores higher)
```

**Step 3: Implement or prescribe a countermeasure.**

For verbosity bias, add a note to the judge system prompt: "Score based solely on the quality of the argument, not the length of the submission. A concise, high-quality paragraph should score the same as a longer one that makes the same argument." Then re-run the probe and report the residual bias.

For position or byline bias, the countermeasure is procedural: always score submissions in isolation (no comparison prompts), and strip author bylines before grading.

**Step 4: Report your findings.**

In your readme, create a table:

| Condition | Avg score (control) | Avg score (treatment) | Avg delta | After countermeasure delta |
|-----------|--------------------|-----------------------|-----------|---------------------------|
| Verbosity bias | 65.6 | 69.8 | +4.2 | +1.1 |

State honestly what risk remains even after the countermeasure.

### Troubleshooting — Part 4

**No verbosity bias detected (delta ≈ 0)**
This is a valid finding. Confirm it by checking whether the filler sentences you added are coherent — incoherent filler may actually lower the score. Try adding substantive-looking but vacuous sentences ("This demonstrates the complexity of the issue at hand.") rather than obviously meaningless padding.

**Bias is inconsistent across runs (sometimes positive, sometimes negative)**
Your temperature may be 0 but the seed is not deterministic in your Ollama version. Run each submission three times and report the average. If variance is high at temperature 0, note this as a reliability issue in your writeup.

**Byline bias probe seems unethical**
It is ethical to measure potential bias in a grading system using synthetic test cases — doing so is responsible AI development, not an expression of bias. You are measuring whether the system IS biased; the point is to find and fix it. Your synthetic submissions do not involve real people.

---

> **Checkpoint: Before writing your deliverables, make sure you can answer:**
> 1. What bias did you measure, and what was the average effect size? Is that effect size large enough to matter in a real grading context?
> 2. What was your countermeasure? Did it eliminate the bias or reduce it? What residual risk remains?
> 3. Name one condition from the course that must be satisfied before you would trust this pipeline to grade real student work. Be specific about what "trust" means — not just "the bias is low," but what evidence you would need and from whom.

---

## Part 5: Reproducible Evals with a Declarative Harness

So far, your confidence in the judge lives in ad-hoc scripts and a readme. Industry teams instead encode that confidence as a **versioned eval configuration**: a declarative file that says "given these inputs, the judge must produce these outputs (or satisfy these assertions)," checked into the repository next to the code so that every future change to the prompt, model, or rubric can be re-verified with one command. In this part you will wrap the pipeline you built in Parts 1–4 in exactly such a harness. This replaces any further ad-hoc verification scripting — the harness *is* your verification from here on.

Choose **one** harness (this is a choice within the lab, not an optional extra — everyone completes Part 5 with one of the two):

- **Option A (default): [promptfoo](https://www.promptfoo.dev/)** — a declarative YAML-based harness. You describe prompts, providers, test cases, and assertions in `promptfooconfig.yaml` and run `npx promptfoo eval`. promptfoo speaks to local models through Ollama's OpenAI-compatible endpoint, so no hosted API is required. Most assertion types (`contains`, `equals`, `javascript`, `regex`) run without any judge model at all.
- **Option B (for pairs who want a Python-native harness): [Inspect AI](https://inspect.aisi.org.uk/)** — the UK AI Security Institute's open-source framework. You define a `Task` (Dataset → Solver → Scorer) in Python and run `inspect eval`. Point the model at your local Ollama endpoint. Inspect's log viewer gives you a per-sample trace of every call.

### Step-by-step guide

1. **Define your golden set.** Reuse the calibration set from Part 2: the (at least eight) synthetic submissions with agreed blind human scores. Each becomes one eval case: the input is the submission text plus the rubric criterion, and the expected output is the human-consensus level for that criterion. Add two adversarial cases from Part 4's bias probe (e.g., the padded and unpadded versions of the same submission, which must receive the same level).
2. **Encode assertions.** For each case, write at least one assertion: the judge's returned level equals the human-consensus level (exact match on the parsed JSON field), or, for the adversarial pairs, that the two levels are equal to each other. In promptfoo these are `assert:` blocks; in Inspect they are scorers.
3. **Run the harness against your local model** and capture the results (promptfoo's `output.json`/web viewer screenshot, or Inspect's `.eval` log). Record the pass rate. It will likely not be 100% — that is a finding, not a failure; your Part 2 kappa already told you the judge and humans disagree sometimes.
4. **Demonstrate a regression.** Make a deliberate, plausible-seeming degradation to your judge prompt (for example, delete the instruction that evidence must be quoted verbatim, or remove the fail-closed JSON instruction). Re-run the harness. Show the pass rate drop, then revert the change and show it recover. Include both result sets and a two-or-three-sentence interpretation in your readme: this is what the harness buys you — a tripwire that catches silent quality regressions before they reach anything real.
5. **Commit the configuration.** The eval config file lives in your submission alongside the code, with a comment header stating the model, temperature, and seed it was validated against.

> **Connection to Direction 1:** if you choose Direction 1 (Building an Agent Evaluation Harness), you will generalize this discipline — hand-rolling the metrics and the regression runner yourself to see what's inside tools like promptfoo and Inspect. Your Part 5 configuration becomes the baseline your hand-rolled harness must match.

### Troubleshooting — Part 5

**promptfoo cannot reach Ollama**
Set the provider to Ollama's OpenAI-compatible endpoint, e.g. `openai:chat:llama3.2` with `apiBaseUrl: http://localhost:11434/v1` (any non-empty API key satisfies the client). Verify first with `curl http://localhost:11434/v1/models`.

**Assertions fail because the judge output wraps JSON in prose**
Reuse the fail-closed JSON parsing lesson from the core pipeline: assert on the *parsed* field, not the raw text — in promptfoo use a `javascript` assertion that parses first; in Inspect, parse in the scorer. If parsing itself fails, that is a legitimate eval failure worth counting.

**Inspect eval runs but every score is zero**
Check that your scorer compares the parsed level as the same type (int vs string) as the target. Inspect's log viewer (`inspect view`) shows the raw model output per sample, which usually reveals the mismatch immediately.

---

## Deliverables

Submit a ZIP containing your code, JSON rubric and configuration, synthetic submission corpus, output CSV, calibration scores and agreement analysis, bias probe design and results, your Part 5 eval harness configuration with both regression result sets, pair log, and a readme writeup of approximately two pages. Ensure reproducibility by fixing random seeds and listing software version information.

## Learning Log

Keep a metacognitive learning log for this lab in your readme: in the spirit of multiple means of action and expression, you may respond to each prompt in prose, in bullet points, or with an annotated diagram — whichever best conveys your thinking. (Prompt 4 adapts the AI-Assisted Learning Template by Marc Watkins.)

1. **What I built.** One paragraph, in plain language that a friend outside of computer science could follow (this is deliberate practice in writing for multiple audiences).
2. **What surprised me.**
3. **What I verified and how.** Evidence, not vibes.
4. **How I used AI during this lab**, and what I learned from that use.
5. **What I'd tell the next student** before they start.
6. **One open question I still have.**

### Lab-specific prompts

- Your pipeline could grade a real class's submissions tomorrow by changing one path in a configuration file. List two conditions — one technical and one procedural — that you believe must be satisfied before that would be responsible. For each condition, name the specific course concept it connects to (e.g., hallucinated evidence rate, human-to-judge agreement, bias measurement).
- Where did you and your partner disagree with each other more than with the judge? What does that specific disagreement reveal about what the rubric was measuring versus what you thought it was measuring? What would you add to the rubric to resolve it?
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

## Extension Challenges

These are optional and carry no extra credit.

**Challenge 1 (moderate): Add a confidence score.**
Modify the judge prompt to also return `"confidence": 1-5` for each criterion grade, where 1 means "I am guessing" and 5 means "the evidence clearly determines this level." Analyze the correlation between confidence score and faithfulness of the evidence quote — do low-confidence grades also have higher hallucination rates?

**Challenge 2 (harder): Implement two-pass grading.**
Run the judge twice on each submission with different seeds. If the two runs agree on a criterion level, accept it. If they disagree, flag it as "DISPUTED" and run a third tiebreaker call. Measure whether two-pass grading reduces human-to-judge disagreement at the cost of more model calls.

**Challenge 3 (hardest): Grading as a RAG problem.**
Instead of putting the entire submission in the prompt, treat grading as a retrieval task: for each criterion, retrieve the three most relevant sentences from the submission using a sentence embedder, then ask the judge to grade that criterion based only on those three sentences. Measure whether focused-retrieval grading reduces the hallucinated evidence rate compared to full-text grading.

---

## Choose Your Pathway and Direction

There are two pathways through this lab:

- **The code route (default):** complete the **core rubric-grading pipeline** above — the batch scorer, the human-agreement validation, the evidence verification, the bias measurement, and the declarative eval harness — and then extend it in **one** direction of your choosing (Directions 1–3). The core is the required spine; the direction matures it.
- **The low-code route (Direction 0):** meet the same core objectives declaratively with promptfoo configuration instead of Python. **Direction 0 replaces the coding in core Parts 1–4** (Part 5's declarative harness is inherently satisfied by this route), and it is your entire lab — you do not also pick a code-route direction.

Either way, you submit **one** deliverable, and it earns **one grade against the single 100-point rubric at the top of this page** — that grade covers everything you did. The directions are not separate labs and do not add rubric rows; they are different ways to mature the same measurement pipeline from a one-shot script into a trustworthy, observable, shippable system. Each direction page carries its own setup, step-by-step instructions, deliverables, and reflection prompts, plus a "What this direction requires" box so you can check the prerequisites before committing.

Wherever a direction refers to "your agent," you may use the rubric-grading pipeline you built above as that agent (the judge and pipeline are themselves a tool-using, LLM-calling system worth evaluating, tracing, and shipping), or another agent you built earlier in the course. Whichever you choose, keep the connection explicit in your writeup: the direction should measure, instrument, or package the *same* evaluation/measurement pipeline, not an unrelated project.

| Direction | What it is | Estimated time | Key requirements |
|-----------|------------|----------------|------------------|
| **[Direction 0: The promptfoo Route]({{ site.baseurl }}/Assignments/RubricPipeline/Direction0)** | The low-code pathway: batch rubric scoring, human agreement, bias tests, and regression runs, all as promptfoo YAML against local Ollama. Replaces core Parts 1–4 coding. | **≈ 7–9 h total** (this is the whole lab, not an add-on) | Node.js, local Ollama; no API key |
| **[Direction 1: Building an Agent Evaluation Harness]({{ site.baseurl }}/Assignments/RubricPipeline/Direction1)** | Generalize the judge validation into a standing test suite: a categorized eval dataset, multiple automated metrics including an LLM judge, a regression runner, and a CI gate on every push. | core ≈ 4.5–6 h **+ ≈ 3–6 h** | GitHub repo + Actions; API key as a repo secret, or Ollama with a self-hosted runner / `act` |
| **[Direction 2: Instrumenting Agents with OpenTelemetry]({{ site.baseurl }}/Assignments/RubricPipeline/Direction2)** | Turn the pipeline from a black box into a system you can reason about: a trace span for every LLM call, tool invocation, and retrieval step, visualized in Jaeger, with alert rules and a runbook. | core ≈ 4.5–6 h **+ ≈ 3–6 h** | Docker + the Jaeger all-in-one image; no API key needed with local Ollama |
| **[Direction 3: CI/CD, TDD, and Publishing for AI Agent Software]({{ site.baseurl }}/Assignments/RubricPipeline/Direction3)** | Earn trust through engineering discipline: TDD against a mocked model, automated code quality, a GitHub Actions CI pipeline, and publishing as a pip package and container image. | core ≈ 4.5–6 h **+ ≈ 3–6 h** | GitHub repo, TestPyPI account, Docker, GHCR personal access token |

Read the direction pages before choosing — each opens with a "What this direction requires" box listing accounts, tools, and any keys, so nothing ambushes your time budget mid-lab.
