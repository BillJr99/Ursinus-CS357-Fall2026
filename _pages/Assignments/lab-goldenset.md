---
layout: assignment
permalink: /Assignments/GoldenSet
title: "CS357: Foundations of Artificial Intelligence - Local Agent Lab Checkpoint: Golden-Set Benchmark"

info:
  coursenum: CS357
  purpose: "To build the personal 10-item benchmark you will reuse all semester — a golden set of questions with expected answers, designed to separate what your local model reliably knows from where it hallucinates."
  tilt:
    task: "Design a 10-item benchmark with per-item rationale, run it against your local model with the class evaluation harness, and analyze where your predictions held."
    criteria: "Assessed on the design quality of the benchmark items and rationales, and on a faithful run with prediction-versus-outcome analysis; see the rubric below for the full breakdown."
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
      proficient: Ten items — five expected-reliable, five expected-fragile — each with an expected answer, a scoring rule the harness can apply, and a one-sentence rationale grounded in training-data reasoning (recency, locality, specificity, or citation-shaped risk)
    - weight: 50
      description: "Run and Analysis (Goal 3)"
      preemerging: The benchmark was never run, or results are reported without the protocol
      beginning: The benchmark ran but without a pinned protocol (temperature/seed unstated), or the analysis restates the score without engaging predictions
      progressing: A pinned run is reported with per-item outcomes, but misses (wrong predictions) are listed rather than explained
      proficient: A pinned run (temperature 0.0, fixed seed, model named) reports per-item outcomes; every prediction miss gets a sentence separating knowledge failure from metric failure; and the writeup states one revision the results motivated
  readings:
    - rtitle: "Hallucinations and Evaluating Agent Outputs Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md"

tags:
  - evaluation
  - benchmarks
  - lab

---

This small **lab** builds an artifact you will use for the rest of the course: your personal **golden set** — ten benchmark questions with expected answers and scoring rules, run against your local model under a fixed protocol. The RAG Quality Checkup lab reuses it as the seed of your regression harness, the RAG Knowledge Base Lab's evaluation leans on it, and the Rubric Pipeline Lab's rubric pipeline grades against exactly this kind of set. Budget **one to two hours**; the class evaluation-harness code from the Hallucinations and Evaluating Agent Outputs session is your starting point, so there is little new code to write.

See the course schedule for the assigned and due dates.

---

## Part 1: Design the Set (50 points)

Create `goldenset.json`: ten items, each with `question`, `expected` (the answer text your scoring rule matches), `rule` (exact, substring, or normalized match — your choice per item, stated), and `rationale` (one sentence predicting whether the model will pass and *why*, reasoned from training data: how recent, how local, how specific, how citation-shaped the fact is).

Design deliberately:

- **Five expected-reliable items** — stable, well-documented knowledge (famous dates, authors, capitals, definitions).
- **Five expected-fragile items** — the territory the Hallucinations session mapped: local or niche facts, post-cutoff events, exact statistics, and at least one citation-shaped item (a request for a source, reference, or attribution).

## Part 2: Run and Analyze (50 points)

Run all ten items against your local model with the class harness protocol pinned: temperature 0.0, a fixed seed, and the model name recorded. Capture per-item PASS/FAIL in `results.md`, then write the analysis: for every item where your prediction missed, one sentence classifying it as a **knowledge failure** (the model doesn't know) or a **metric failure** (your scoring rule mis-graded a correct or incorrect answer) — and one revision to the set that the results motivated (an item you would replace, or a rule you would tighten).

Keep `goldenset.json` under version control with your course work — you will point your RAG Checkup regression harness at it, extend it for the RAG Knowledge Base Lab's corpus, and recognize its shape again in the Rubric Pipeline Lab.

---

## Deliverables

Submit `goldenset.json` and `results.md` (protocol, per-item outcomes, miss analysis, one motivated revision).

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Benchmark Design | 50 |
| Part 2: Run and Analysis | 50 |
| **Total** | **100** |

## Reflection Prompts

- Which fragile item surprised you in either direction, and what does that tell you about your mental model of the training data?
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all — I am simply using it to gauge if the labs are too easy or hard)?
