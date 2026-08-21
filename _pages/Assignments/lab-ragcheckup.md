---
layout: assignment
permalink: /Assignments/RAGCheckup
title: "CS357: Foundations of Artificial Intelligence - Lab: RAG Quality Checkup Checkpoint"

info:
  coursenum: CS357
  purpose: "To run a structured mid-flight diagnostic on your in-progress RAG pipeline: retrieval quality measured, citations audited, one failure understood, and to freeze that diagnostic into a rerunnable regression harness that follows you into the Rubric Pipeline Lab."
  tilt:
    task: "Complete the studio worksheet on your own RAG Knowledge Base Lab pipeline: recall@k across two chunking configurations, a citation audit, and one analyzed failure, then pin a golden set into a rerunnable regression harness and demonstrate reproducibility."
    criteria: "Assessed on a completed worksheet with real measurements from your own pipeline, and a regression harness that reruns identically; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To measure retrieval quality (recall@k) empirically across two chunking configurations on your own corpus
    - To audit citations by hand, classifying each answer's claims as supported or unsupported by the cited chunk
    - To capture and analyze one concrete pipeline failure with a hypothesis and planned fix
    - To freeze an evaluation into a rerunnable regression harness and demonstrate its reproducibility
  rubric:
    - weight: 60
      description: "The Checkup Worksheet (Goals 1-3)"
      preemerging: The worksheet is empty or filled with invented numbers not produced by the student's pipeline
      beginning: Some measurements exist but only one chunking configuration was tested, or the citation audit is missing
      progressing: recall@k for both configurations and a five-row citation audit are complete, but the failure case is missing or has no hypothesis
      proficient: recall@k is measured for both chunking configurations on the student's own corpus with the winner identified; the five-row citation audit classifies each claim as supported or unsupported with chunk references; and one observed failure is recorded with a plausible hypothesis and a planned fix
    - weight: 40
      description: "The Regression Harness (Goal 4)"
      preemerging: No harness exists, or it cannot be rerun
      beginning: A harness exists but the golden set is not pinned (questions or scoring change between runs), or it was run only once
      progressing: The harness reruns with a pinned golden set and protocol, but the two runs' outputs were not compared, or the harness is not committed alongside the RAG Knowledge Base Lab work
      proficient: The harness (plain Python built on the class evaluation harness, or declarative promptfoo YAML, student's choice) pins a golden set (seeded from the Golden-Set Benchmark lab, extended with corpus-specific items) and a fixed protocol; two runs are shown to agree; and the harness lives in the RAG Knowledge Base Lab repository where the Rubric Pipeline Lab's pipeline work can pick it up
  readings:
    - rtitle: "Hallucinations and Evaluating Agent Outputs Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md"
    - rtitle: "RAG Quality: Chunking, Clustering, and Reranking Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ragquality.md"
    - rtitle: "Required prep for the Rubric Pipeline Lab: Testing Agents, Evaluation, Regression, and the Non-Determinism Problem"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-testingagents.md"
    - rtitle: "Reference: promptfoo, declarative LLM/agent eval and red-teaming (harness option, runs against Ollama)"
      rlink: "https://www.promptfoo.dev/"

tags:
  - rag
  - evaluation
  - regression-testing
  - lab

---

This small **lab** is a structured checkup on the RAG pipeline you are building in the RAG Knowledge Base Lab, begun during the studio session and finished on your own; budget **two to three hours total, most of it in class**. It is deliberately a scaffold: everything you produce here is work the RAG Knowledge Base Lab's evaluation asks for anyway, done earlier and under supervision, plus one forward investment: a **regression harness** you will be glad to already have when the Rubric Pipeline Lab asks you to build a reproducible evaluation pipeline.

Work on your **own** pipeline and corpus (this lab is individual, though the studio makes collaboration on debugging natural). Bring your RAG Knowledge Base Lab repository to the studio session running.

See the course schedule for the assigned and due dates.

---

## Part 1: The Checkup Worksheet (60 points)

Complete `checkup.md` against your in-progress RAG Knowledge Base Lab pipeline:

1. **Retrieval quality.** For five queries representative of your corpus, measure **recall@k** under your current chunking configuration and one alternative (different chunk size or overlap). Record the table and name the winner, and carry the winning configuration back into the RAG Knowledge Base Lab.
2. **Citation audit.** For five answered queries, one row each: the answer's central claim, the chunk it cites, and your verdict: **supported** (the chunk actually contains the claim) or **unsupported**. The RAG Knowledge Base Lab rubric weights citation quality heavily; this is that muscle, built early.
3. **One failure.** Capture one concrete misbehavior you observed (a wrong retrieval, an unsupported citation, a failed abstention) with the query, the output, a one-paragraph hypothesis for the mechanism, and your planned fix.

## Part 2: The Regression Harness (40 points)

Freeze your evaluation so it can be rerun forever:

- Pin a golden set: start from your **Golden-Set Benchmark** items, replace or extend with at least five corpus-specific questions (including at least one that should trigger abstention).
- Build the harness in your choice of medium: **plain Python** grown from the class evaluation harness, or **declarative promptfoo YAML** run against your local Ollama, the same tool that anchors the Rubric Pipeline Lab's low-code direction, so either choice pays forward.
- Pin the protocol (temperature 0.0, fixed seed, model recorded), run it **twice**, and show the runs agree.
- Commit the harness and golden set inside your RAG Knowledge Base Lab repository.

---

## Deliverables

Submit `checkup.md` (worksheet with real measurements), the harness (script or YAML) with its golden set, and the two-run agreement log, all committed in your RAG Knowledge Base Lab repository, with paths noted in the submission.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Checkup Worksheet | 60 |
| Part 2: Regression Harness | 40 |
| **Total** | **100** |

## Reflection Prompts

- Which chunking configuration won on your corpus, and did the margin surprise you?
- What did the citation audit reveal that the recall@k numbers alone would have hidden?
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
