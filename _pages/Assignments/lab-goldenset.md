---
layout: assignment
permalink: /Assignments/GoldenSet
title: "CS357: Foundations of Artificial Intelligence - Lab: Golden-Set Benchmark Checkpoint"

info:
  coursenum: CS357
  purpose: "To build the personal 10-item benchmark you will reuse all semester, a golden set of questions with expected answers, designed to separate what your local model reliably knows from where it hallucinates."
  tilt:
    task: "Design a 10-item benchmark with per-item rationale, run it against your local model with the class evaluation harness, and analyze where your predictions held."
    criteria: "I assess your work on the design quality of the benchmark items and rationales, and on a faithful run with prediction-versus-outcome analysis.  Please read the rubric below for the details."
  points: 100
  goals:
    - To design benchmark items that deliberately probe both reliable knowledge and hallucination-prone territory
    - To state a falsifiable prediction and scoring rule for each item before running it
    - To run a fixed evaluation protocol (pinned temperature and seed) and analyze prediction versus outcome
  rubric:
    - weight: 50
      description: "Benchmark Design (Goals 1-2)"
      preemerging: Fewer than ten items exist, or items lack expected answers
      beginning: Ten items exist with expected answers, but the set does not deliberately mix reliable and hallucination-prone territory, or rationales are missing
      progressing: The set mixes five expected-reliable and five expected-fragile items with rationales, but several rationales do not connect to why model training data would be thick or thin there
      proficient: "Ten items (five expected-reliable, five expected-fragile) each with an expected answer, a scoring rule the harness can apply, and a one-sentence rationale grounded in training-data reasoning (recency, locality, specificity, or citation-shaped risk). This row is about judgment, not medium: it is earned identically whether the set is a JSON file, a promptfoo YAML case list, or a spreadsheet"
    - weight: 50
      description: "Run and Analysis (Goal 3)"
      preemerging: The benchmark was never run, or results are reported without the protocol
      beginning: The benchmark ran but without a pinned protocol (temperature/seed unstated), or the analysis restates the score without engaging predictions
      progressing: A pinned run is reported with per-item outcomes, but misses (wrong predictions) are listed rather than explained
      proficient: A pinned run (temperature 0.0, fixed seed, model named) reports per-item outcomes; every prediction miss gets a sentence separating knowledge failure from metric failure; and the writeup states one revision the results motivated. On the no-code route the protocol is pinned in the chat interface rather than in code, and the run log or screenshot stands in for the harness output; the analysis requirement is unchanged
  readings:
    - rtitle: "Hallucinations and Evaluating Agent Outputs Activity"
      rlink: "Activities/liascript-evaluatingoutputs.md"
      liapage: true

tags:
  - evaluation
  - benchmarks
  - lab

---

This small **lab** builds an artifact you'll use for the rest of the course, your personal **golden set** of ten benchmark questions, each with an expected answer and a scoring rule, run against your local model under a fixed protocol.  The RAG Quality Checkup lab reuses it as the seed of your regression harness, the RAG Knowledge Base Lab's evaluation leans on it, and the Rubric Pipeline Lab's rubric pipeline grades against exactly this kind of set.  Budget **one to two hours**; the class evaluation-harness code from the Hallucinations and Evaluating Agent Outputs session is your starting point, so there is little new code to write.

See the course schedule for the assigned and due dates.

---

## Before You Start

**This builds on:** the *Hallucinations and Evaluating Agent Outputs* session, where we mapped the territory where models are unreliable, and the evaluation harness written in class.  You do not need any other lab finished first.

**You need:** Ollama running with a model pulled, and either Python with `requests` (code route), promptfoo (low-code route), or a spreadsheet and a chat window (no-code route).  Check your model server is up:

```bash
curl -s http://localhost:11434/api/tags | head -c 200
```

**Pace yourself:** most of your effort belongs in Part 1, and that is the right proportion.  Designing ten good items is harder than running them.

**What you will have at the end:** a ten-item benchmark that you will reuse three more times this semester (RAG Quality Checkup, RAG Knowledge Base, Rubric Pipeline).  Build it to keep.

---

## Choose Your Path

All three routes are graded on the same rubric and are worth the same credit.  The design work in Part 1 is identical on all three; they differ only in how you run the set in Part 2.

| Route | What you build | Pick this if | What you submit instead |
|-------|----------------|--------------|-------------------------|
| **No-code** | The set in a spreadsheet; you run each item by hand in Open WebUI and record what came back | You want your effort in the *design* of the items, or you are not comfortable in Python yet | A CSV export of the sheet, plus a screenshot or pasted log of your runs |
| **Low-code** | The set as a `promptfoo` YAML case list, run against your local Ollama, which gives you a pass/fail grid without a harness | You would rather configure than program, or you plan to take the Rubric Pipeline Lab's promptfoo direction later | The YAML file and the promptfoo output |
| **Code** | `goldenset.json` plus a short runner grown from the class evaluation harness | You want the harness you will extend in later labs | `goldenset.json` and `results.md` |

Whichever you pick, **the written analysis in Part 2 is the same and carries the same weight.**  The judgment of what to measure is the assignment; the machinery is a detail.

> **A note on "no-code is the easy one."**  It is not.  Running ten items by hand means you read every answer closely, which is exactly what catches a *metric failure* (your rule mis-graded a correct answer).  Students on the code route often miss those because the harness printed FAIL and they believed it.

---

## Part 1: Design the Set (50 points)

Create `goldenset.json`: ten items, each with `question`, `expected` (the answer text your scoring rule matches), `rule` (exact, substring, or normalized match, your choice per item, stated), and `rationale` (one sentence predicting whether the model will pass and *why*, reasoned from training data: how recent, how local, how specific, how citation-shaped the fact is).

Design deliberately:

- **Five expected-reliable items**: stable, well-documented knowledge (famous dates, authors, capitals, definitions).
- **Five expected-fragile items**: the territory the Hallucinations session mapped: local or niche facts, post-cutoff events, exact statistics, and at least one citation-shaped item (a request for a source, reference, or attribution).

### Two worked items, so you can see what "good" looks like

An **expected-reliable** item:

```json
{
  "question": "In what year was the Declaration of Independence signed?",
  "expected": "1776",
  "rule": "substring",
  "rationale": "Expect PASS. This date appears in a vast number of training documents in exactly this form, so it is about as thick as training data gets. Substring matching is safe because any correct phrasing contains the four digits."
}
```

An **expected-fragile** item:

```json
{
  "question": "Which building houses the Ursinus College mathematics and computer science department, and what are its office hours?",
  "expected": "Pfahler Hall",
  "rule": "substring",
  "rationale": "Expect FAIL on the second half. The building name may appear in a handful of pages; the office hours almost certainly appear nowhere, and they change every term. I predict a confident, invented answer, which is exactly the failure mode worth catching."
}
```

Notice what each rationale does: it names a *reason from the training data* (thick, thin, recent, local, changing), and it commits to a prediction before the run.  A rationale that says "this seems hard" earns the `beginning` row; a rationale that says *why the data would be thin here* earns `proficient`.

### Step by step

1.  Write your five reliable items first.  They are easier, and they calibrate your sense of what an unambiguous `expected` looks like.
2.  Write the five fragile items, deliberately spread across the four kinds of thin territory: **local**, **post-cutoff**, **exact statistic**, and **citation-shaped**.  At least one of each.
3.  For each item, choose the `rule` **last**, after you know what a correct answer would look like.  Ask: could a fully correct answer fail this rule?  Could a wrong answer pass it?
4.  Write every rationale as a prediction plus a reason.  The prediction is what Part 2 grades you against.

> **You've succeeded when** you have ten items, each with all four fields, and a classmate reading only your rationales could predict your pass rate to within two items.

---

## Part 2: Run and Analyze (50 points)

Run all ten items against your local model with the protocol pinned: **temperature 0.0, a fixed seed, and the model name recorded.**  Pinning is not bureaucracy: an unpinned run cannot be repeated, and a result you cannot repeat is not a measurement.  (This is the dial from *Running Your Own AI*, Section 3b, doing real work.)

### Step by step

1.  **Pin the protocol** on your route: `"options": {"temperature": 0, "seed": 42}` in code; `config.temperature: 0` in promptfoo YAML; the **Advanced Params** panel in Open WebUI on the no-code route.  Record the model name and the exact settings at the top of `results.md`.
2.  **Run all ten** and record PASS/FAIL per item, alongside the prediction you made in Part 1.
3.  **Find your misses.**  A miss is any item where the outcome differs from your prediction, in *either* direction.  A fragile item that passed is as interesting as a reliable one that failed.
4.  **Classify each miss** in one sentence:
   - **Knowledge failure**: the model genuinely does not have the fact.
   - **Metric failure**: the model answered correctly (or incorrectly) and *your rule graded it wrong*.  For example, the model answered "seventeen seventy-six" and your substring rule looked for "1776".
   That distinction is the whole point of this lab.  A benchmark whose failures are mostly metric failures is measuring your rules, not the model.
5.  **State one revision** the results motivated: an item you would replace, or a rule you would tighten, and why.

### A worked miss, for calibration

> **Item 7** (fragile, citation-shaped).  Predicted FAIL, outcome PASS.
>
> I asked for a source on a claim about local rainfall and expected an invented citation.  The model instead refused, saying it did not have a reliable source.  That is a **metric failure**: my rule scored "no answer" as a pass because the invented-citation string was absent, but abstention and correctness are not the same outcome and my rule cannot tell them apart.  **Revision:** split this into two items, one that scores abstention as a pass and one that scores a fabricated citation as a fail, so the two behaviors stop sharing a row.

> **You've succeeded when** `results.md` names the model and protocol, shows ten prediction-versus-outcome rows, explains every miss as knowledge or metric, and ends with one revision you can justify.

Keep your golden set under version control with your course work; you will point your RAG Checkup regression harness at it, extend it for the RAG Knowledge Base Lab's corpus, and recognize its shape again in the Rubric Pipeline Lab.

---

## The No-Code and Low-Code Routes, in Detail (equal credit)

The whole point of a golden set is judgment about *what to measure*, not the harness that measures it.  You may therefore build and run your set **in a spreadsheet plus a chat interface**, with no code at all.

1.  **Design the set in a spreadsheet.**  One row per case: `id`, `input`, `expected`, `why this case earns its place`.  The design criteria in Part 1 apply unchanged: coverage, discriminating power, and honest hard cases.
2.  **Run it by hand or with promptfoo's UI.** Either paste each input into Open WebUI and record the output in a `got` column, or use `promptfoo` in its web view, which takes a YAML list of cases and shows a pass/fail grid without you writing a harness.
3.  **Analyze in the same spreadsheet.**  Add `pass/fail` and `failure mode` columns, then compute the pass rate and group the failures by cause.

**What you submit instead of code:** the spreadsheet (CSV export), a screenshot of the grid or your run log, and the identical written analysis: which cases discriminate, which turned out to be duplicates, and what the failure clusters tell you about the model.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Every item fails, including the easy ones | The model server is not reachable, and your runner is scoring an empty string | `curl -s http://localhost:11434/api/tags`. If that fails, start Ollama. If you are in the course container, the address is `host.docker.internal:11434`, not `localhost` |
| Two runs of the same item disagree | Temperature or seed is not actually pinned | Print the request body you are sending and confirm `options` really contains both. In Open WebUI, confirm the setting applied to *this* chat, not just the model default |
| Everything "passes" and you do not believe it | Your `expected` strings are too short. `"1"` is a substring of almost every answer | Lengthen `expected`, or switch that item to exact or normalized matching |
| A correct answer scores FAIL | Formatting mismatch, not a knowledge gap | This is a **metric failure** and it is a finding, not a bug to hide. Record it as one, then decide whether to normalize |
| The model refuses instead of answering | Abstention, which is a distinct outcome from right and wrong | Your rule probably cannot distinguish abstention from a wrong answer. Say so in the analysis; that observation is worth points |
| promptfoo cannot find your provider | The Ollama provider string is wrong or the server is not up | Use `ollama:chat:llama3.2` and confirm the `curl` above answers first |

---

## Self-Check Before You Submit

Hold your own work against the rubric's `proficient` column:

- [ ] Ten items, with **five** predicted reliable and **five** predicted fragile.
- [ ] The fragile five cover all four kinds of thin territory, including **at least one citation-shaped** item.
- [ ] Every item has `question`, `expected`, a stated `rule`, and a `rationale`.
- [ ] Every rationale names a **training-data reason** (recency, locality, specificity, citation-shaped risk), not just a difficulty guess.
- [ ] The protocol is recorded: **model name, temperature 0.0, fixed seed**.
- [ ] Per-item outcomes are shown next to the predictions you made beforehand.
- [ ] **Every** miss is classified as knowledge failure or metric failure, in a sentence.
- [ ] One revision is stated, with its reason.
- [ ] The AI-disclosure and hours reflections are answered.

If a box is unchecked, that is a specific, fixable thing rather than a vague worry.  Fix it and check it.

---

## Deliverables

Submit your benchmark (`goldenset.json`, the promptfoo YAML, or the spreadsheet CSV) and `results.md` (protocol, per-item outcomes, miss analysis, one motivated revision).  Name your route at the top of `results.md` so it is graded against the right column of the rubric.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Benchmark Design | 50 |
| Part 2: Run and Analysis | 50 |
| **Total** | **100** |

## Reflection Prompts

- Which fragile item surprised you in either direction, and what does that tell you about your mental model of the training data?
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
