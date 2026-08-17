---
layout: default-standard
permalink: /Assignments/RubricPipeline/Direction0
title: 'CS357: Foundations of Artificial Intelligence - Rubric Pipeline Lab, Direction 0: The promptfoo Route'
info:
  coursenum: CS357
  purpose: To meet the core Rubric Pipeline Lab objectives — batch rubric scoring, human-agreement validation, bias measurement, and regression testing — declaratively with promptfoo and local Ollama, writing configuration files instead of Python.
  readings:
  - rtitle: 'Rubric Pipeline Lab Core: An LLM Rubric-Grading Pipeline'
    rlink: /Assignments/RubricPipeline
  - rtitle: LLM-as-Judge Activity
    rlink: https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmasjudge.md
  - rtitle: Evaluating Outputs Activity
    rlink: https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md
  - rtitle: promptfoo Documentation
    rlink: https://www.promptfoo.dev/docs/intro/
tags:
- evaluation
- llm-as-judge
- pipelines
- testing
---

# CS357: Foundations of Artificial Intelligence - Rubric Pipeline Lab, Direction 0: The promptfoo Route

## Purpose

To meet the core Rubric Pipeline Lab objectives — batch rubric scoring, human-agreement validation, bias measurement, and regression testing — declaratively with promptfoo and local Ollama, writing configuration files instead of Python.

## Background Reading and References

- [Rubric Pipeline Lab Core: An LLM Rubric-Grading Pipeline](/Assignments/RubricPipeline)
- [LLM-as-Judge Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmasjudge.md)
- [Evaluating Outputs Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md)
- [promptfoo Documentation](https://www.promptfoo.dev/docs/intro/)

This page is **Direction 0** of the [Rubric Pipeline Lab](/Assignments/RubricPipeline). It is the **low-code route** through the lab: you meet the same core objectives — batch rubric scoring, human-agreement validation, bias measurement, and regression testing — by writing **declarative YAML configuration** for [promptfoo](https://www.promptfoo.dev/) instead of Python code.

**Direction 0 replaces the coding in core Parts 1–4.** If you choose this route, you do not build the Python pipeline; you build the same measurements out of promptfoo configs. Core **Part 5** (expressing the judge as a versioned, declarative harness) **is inherently satisfied by this route** — the entire route *is* a declarative harness. You are graded under the same 100-point rubric on the core lab page; that rubric's wording is pathway-neutral, and this page tells you what each row means on this route. As with the core lab, this route is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log** — the blind human-scoring step in Part C requires both partners.

**See the course schedule for the assigned and due dates.** Budget: expect **7–9 hours total** for this route (it replaces the core coding, so this is your entire Rubric Pipeline Lab time, not an add-on).

> **What this direction requires**
>
> - **Node.js and npm** (install from [https://nodejs.org](https://nodejs.org)) — promptfoo runs via `npx`, so nothing else needs a global install
> - **Local Ollama** with the `llama3.2` model, as in Labs 1–4
> - **No API key.** Everything on this route runs locally.

---

## Part A: Install promptfoo and Point It at Ollama

**Estimated time: 30–45 min**

Initialize a project directory:

```bash
mkdir cs357-lab5-d0
cd cs357-lab5-d0
npx promptfoo@latest init
```

The `init` command scaffolds a `promptfooconfig.yaml`. Verify promptfoo can reach your local Ollama with a minimal smoke-test config — replace the scaffolded file's contents with:

{% raw %}
```yaml
# smoke-test promptfooconfig.yaml — verify Ollama connectivity
description: "Rubric Pipeline Lab Direction 0 smoke test"

prompts:
  - "Reply with exactly one word: the capital of France."

providers:
  - ollama:chat:llama3.2

tests:
  - assert:
      - type: contains
        value: "Paris"
```
{% endraw %}

Run it:

```bash
npx promptfoo@latest eval
npx promptfoo@latest view   # opens the results viewer in your browser
```

Expected: 1 test, 1 pass. If promptfoo cannot reach Ollama, confirm `ollama serve` is running and that `curl http://localhost:11434/api/tags` responds; promptfoo reads the base URL from the `OLLAMA_BASE_URL` environment variable if your Ollama runs elsewhere.

---

## Part B: Batch Rubric Scoring with `llm-rubric`

**Estimated time: 2–2.5 h (most of it authoring the rubric and the 15 answers)**

This is the declarative counterpart of core Parts 1–2's pipeline: a rubric, a corpus of sample answers, and a judge that scores every answer against every criterion in one command.

**Step 1: Author your rubric.** Exactly as in the core lab, write a rubric with **four criteria** and observable level descriptors for a short artifact type of your choosing (persuasive paragraph, function docstring, lab abstract). You will embed each criterion's text into an `llm-rubric` assertion below. For each criterion, the judge's job is binary: **PASS if the answer sits at level 3 or 4 of that criterion, FAIL if at level 1 or 2.** Write each criterion's rubric text so that this pass line is explicit and observable.

**Step 2: Author your dataset — 15 sample answers.** Create `dataset.csv` with one row per answer, spanning the full quality range (like the core lab's 12 synthetic submissions, plus three more: include at least one empty-ish answer, one off-topic answer, and one verbose-but-weak answer). All answers are synthetic — no real student work.

```csv
id,answer
a01,"<your excellent answer here>"
a02,"<your good answer here>"
a03,"<your adequate answer>"
...
a15,"<your off-topic answer>"
```

Record privately (before running anything) which criteria you *intend* each answer to pass — you need this for Part C.

**Step 3: The baseline scoring config.** This skeleton is complete except for your rubric text — copy it to `promptfooconfig-baseline.yaml` and fill in the four `value:` blocks with your criterion descriptors:

{% raw %}
```yaml
# promptfooconfig-baseline.yaml
# Validated against: ollama llama3.2, temperature 0
description: "Rubric Pipeline Lab Direction 0 — baseline rubric-as-judge batch scoring"

prompts:
  # The echo provider passes each stored answer straight through as the "output",
  # so the llm-rubric judge grades your dataset answers, not a freshly generated one.
  - "{{answer}}"

providers:
  - echo

defaultTest:
  options:
    # The judge model that grades every llm-rubric assertion:
    provider: ollama:chat:llama3.2
  assert:
    - type: llm-rubric
      value: >
        Criterion C1 (<your criterion name>): PASS only if <your level 3-4
        descriptor, stated observably — what must visibly be present in the
        answer>. FAIL otherwise.
    - type: llm-rubric
      value: >
        Criterion C2 (<name>): PASS only if <level 3-4 descriptor>. FAIL otherwise.
    - type: llm-rubric
      value: >
        Criterion C3 (<name>): PASS only if <level 3-4 descriptor>. FAIL otherwise.
    - type: llm-rubric
      value: >
        Criterion C4 (<name>): PASS only if <level 3-4 descriptor>. FAIL otherwise.

tests: file://dataset.csv
```
{% endraw %}

**Step 4: Run the batch and capture the output.**

```bash
npx promptfoo@latest eval -c promptfooconfig-baseline.yaml --output run_baseline.json
npx promptfoo@latest view
```

Expected: 15 rows × 4 assertions = 60 judge verdicts. Save `run_baseline.json` — it is a deliverable, and Part E diffs against it. In the viewer, spot-check three items: does the judge's reasoning for each verdict reference the actual answer text? Note one example where its reasoning is weak or generic — that is this route's version of the core lab's evidence-faithfulness concern, and it feeds your Part C disagreement analysis.

**Troubleshooting:** if every assertion passes (or fails), your rubric text is not discriminating — sharpen the PASS line with countable features ("names an opposing view in a full sentence AND rebuts it with a reason"), exactly the observability lesson from the core lab. If the judge output is erratic, re-run; `llm-rubric` verdicts from a small local model are noisy, and observing that noise is a legitimate finding for your writeup.

---

## Part C: Human Agreement — Blind Scoring and Percent Agreement

**Estimated time: 1.5–2 h**

**Before looking at any judge output**, each partner independently hand-scores all 15 answers, criterion by criterion, as PASS (level 3–4) or FAIL (level 1–2). This order matters for the same reason as in the core lab: seeing the judge's scores first anchors yours.

**The score spreadsheet.** Build a spreadsheet (Google Sheets, Excel, or CSV) with exactly these columns:

| Column | Contents |
|--------|----------|
| `item_id` | a01 … a15 |
| `C1_human_A`, `C2_human_A`, `C3_human_A`, `C4_human_A` | Partner A's blind P/F per criterion |
| `C1_human_B`, `C2_human_B`, `C3_human_B`, `C4_human_B` | Partner B's blind P/F per criterion |
| `C1_judge`, `C2_judge`, `C3_judge`, `C4_judge` | The judge's P/F per criterion (filled in **after** both humans finish, from `run_baseline.json`) |
| `mismatches` | count of criteria where the human-consensus verdict differs from the judge |
| `notes` | one line on any disputed item |

Where you and your partner disagree with each other, record both marks and use discussion to set a consensus verdict for the judge comparison (do not erase the original marks — human-to-human disagreement is a finding, just as in the core lab).

**Compute percent agreement** (no code needed; a spreadsheet formula or a calculator is fine):

```
percent agreement = (number of criterion-cells where human consensus == judge verdict)
                    ÷ (15 items × 4 criteria = 60 cells) × 100
```

Report percent agreement overall **and per criterion** (each criterion has 15 cells).

**Kappa replacement — read this.** The code route computes Cohen's kappa, which corrects agreement for chance. **On this route, kappa is not required.** It is replaced by: (1) the percent-agreement numbers above, and (2) a **written disagreement analysis of the 3 worst mismatches** — the three items with the highest `mismatches` count. For each of the three, quote the answer, state the human verdict and the judge verdict per disputed criterion, quote the judge's stated reasoning from the promptfoo output, and diagnose *why* they diverged: is the criterion's wording ambiguous, is the judge pattern-matching on surface features, or did the humans read something into the answer that is not on the page? Then revise the wording of the single worst criterion's rubric text, re-run the baseline config, and report that criterion's per-criterion agreement before and after — the same revise-and-remeasure discipline as core Part 2.

---

## Part D: Bias Tests as Config Variants

**Estimated time: 1–1.5 h**

The core lab measures a judge bias with a controlled Python experiment; here you measure two with **two more config files over the same dataset**.

**Variant (i) — reordering (position/order effects).** Create `dataset_reordered.csv`: the same 15 answers with the row order reversed (a15 first, a01 last). Copy the baseline config to `promptfooconfig-reordered.yaml`, changing only the last line to `tests: file://dataset_reordered.csv`. Since each answer is judged in isolation, a trustworthy judge should give **identical verdicts regardless of order** — any per-item verdict that flips between runs is evidence of order sensitivity or judge instability, which in a real grading deployment amounts to position bias against whoever gets graded late.

**Variant (ii) — padding (verbosity bias).** Create `dataset_padded.csv`: the same 15 answers, each with three filler sentences appended (substantive-sounding but vacuous, e.g., "Furthermore, it is important to consider the various aspects of this topic from multiple perspectives."). Copy the baseline config to `promptfooconfig-padded.yaml`, changing only the tests line. Padding adds no rubric-relevant content, so verdicts should not improve; any criterion that flips FAIL→PASS under padding is verbosity bias.

Run both and keep the outputs:

```bash
npx promptfoo@latest eval -c promptfooconfig-reordered.yaml --output run_reordered.json
npx promptfoo@latest eval -c promptfooconfig-padded.yaml --output run_padded.json
```

**Compare the three runs in this table** (one row per item; a deliverable in your writeup):

| item_id | baseline passes (of 4) | reordered passes (of 4) | padded passes (of 4) | reorder delta | padding delta |
|---------|------------------------|-------------------------|----------------------|---------------|---------------|
| a01 | | | | | |
| … | | | | | |
| **Total flips** | | | | | |

Summarize each bias in one sentence with a number (e.g., "padding flipped 5 of 60 verdicts FAIL→PASS, an 8% verbosity effect"), propose one countermeasure you could express *in the rubric text of the config* (e.g., "Length and repetition must not be credited; judge only the content that addresses the criterion"), apply it, re-run the padded config, and report the residual effect — mirroring core Part 4's countermeasure-and-residual-risk discipline.

---

## Part E: Regression — Change the Judge, Diff the Runs

**Estimated time: 45–60 min**

This is the harness discipline of core Part 5, which this route satisfies by construction — now demonstrate it. Make a deliberate, plausible-seeming **degradation to the judge prompt**: in a copy of the baseline config (`promptfooconfig-regressed.yaml`), weaken one criterion's rubric text (for example, delete the observable PASS line and leave only the criterion name). Re-run and diff:

```bash
npx promptfoo@latest eval -c promptfooconfig-regressed.yaml --output run_regressed.json
```

Compare `run_baseline.json` and `run_regressed.json` — the viewer's side-by-side, a text diff, or a hand-built table of the 60 verdicts all work. Identify which items' verdicts changed and in which direction. In two or three sentences in your writeup, interpret the result: this is what a versioned eval configuration buys you — a tripwire that catches a silent judge-quality regression before it grades anything real. Then revert the change and confirm the baseline verdicts recover.

---

## Part F: Writeup

**Same writeup as the core lab.** Complete the [core lab page](/Assignments/RubricPipeline)'s **Learning Log** (all six prompts plus the lab-specific prompts) in your readme, citing your percent-agreement numbers, bias flip counts, and regression diff as the specific evidence. Approximately two pages.

---

## Deliverables (Direction 0)

Submit a ZIP containing:

- **At least 3 YAML configs** (baseline, reordered, padded — plus the regressed copy from Part E and the smoke test if you kept it)
- **The dataset file(s)**: `dataset.csv`, `dataset_reordered.csv`, `dataset_padded.csv`
- **The score spreadsheet** with both partners' blind scores, the judge's verdicts, and the mismatch counts
- **Run outputs**: `run_baseline.json`, `run_reordered.json`, `run_padded.json`, `run_regressed.json`
- **The writeup** (readme, approximately two pages), including the percent-agreement figures, the 3-worst-mismatches disagreement analysis, the bias comparison table with countermeasure results, the regression interpretation, and the pair log with at least two timestamped role swaps

## How the rubric reads on this route

You are graded under the same rubric as everyone else, on the [core lab page](/Assignments/RubricPipeline). On this route: *Pipeline Implementation* is your baseline config scoring all 15 items end-to-end; *Human Agreement Validation* is the blind spreadsheet plus percent agreement and the criterion revision; *Bias Measurement* is the two config variants with the comparison table and countermeasure; *Evidence Verification* is the judge-reasoning faithfulness check inside your 3-worst-mismatches analysis; *Reproducible Eval Harness* is the regression demonstration of Part E; *Writeup* is Part F.
