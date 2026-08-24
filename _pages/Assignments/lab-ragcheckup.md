---
layout: assignment
permalink: /Assignments/RAGCheckup
title: "CS357: Foundations of Artificial Intelligence - Lab: RAG Quality Checkup Checkpoint"

info:
  coursenum: CS357
  purpose: "To run a structured mid-flight diagnostic on your in-progress RAG pipeline, measuring retrieval quality, auditing citations, and understanding one failure, and then to freeze that diagnostic into a rerunnable regression harness that follows you into the Rubric Pipeline Lab."
  tilt:
    task: "Complete the studio worksheet on your own RAG Knowledge Base Lab pipeline: recall@k across two chunking configurations, a citation audit, and one analyzed failure, then pin a golden set into a rerunnable regression harness and demonstrate reproducibility."
    criteria: "I grade this on a completed worksheet with real measurements from your own pipeline, and a regression harness that reruns identically.  See the rubric below for the full breakdown."
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
      proficient: "recall@k is measured for both chunking configurations on the student's own corpus with the winner identified; the five-row citation audit classifies each claim as supported or unsupported with chunk references; and one observed failure is recorded with a plausible hypothesis and a planned fix. The medium does not matter: measurements taken by hand in Open WebUI's knowledge-base view earn this row on the same terms as measurements printed by a script, provided the numbers came from the student's own pipeline"
    - weight: 40
      description: "The Regression Harness (Goal 4)"
      preemerging: No harness exists, or it cannot be rerun
      beginning: A harness exists but the golden set is not pinned (questions or scoring change between runs), or it was run only once
      progressing: The harness reruns with a pinned golden set and protocol, but the two runs' outputs were not compared, or the harness is not committed alongside the RAG Knowledge Base Lab work
      proficient: The harness (a scripted run sheet in a spreadsheet, declarative promptfoo YAML, or plain Python built on the class evaluation harness, student's choice) pins a golden set (seeded from the Golden-Set Benchmark lab, extended with corpus-specific items) and a fixed protocol; two runs are shown to agree; and the harness lives in the RAG Knowledge Base Lab repository where the Rubric Pipeline Lab's pipeline work can pick it up
  readings:
    - rtitle: "Hallucinations and Evaluating Agent Outputs Activity"
      rlink: "Activities/liascript-evaluatingoutputs.md"
      liapage: true
    - rtitle: "RAG Quality: Chunking, Clustering, and Reranking Activity"
      rlink: "Activities/liascript-ragquality.md"
      liapage: true
    - rtitle: "Required prep for the Rubric Pipeline Lab: Testing Agents, Evaluation, Regression, and the Non-Determinism Problem"
      rlink: "Activities/liascript-testingagents.md"
      liapage: true
    - rtitle: "promptfoo, for declarative LLM and agent evaluation and red-teaming.  One of the harness options, and it runs against Ollama"
      rlink: "https://www.promptfoo.dev/"

tags:
  - rag
  - evaluation
  - regression-testing
  - lab

---

This small **lab** is a structured checkup on the RAG pipeline you are building in the RAG Knowledge Base Lab, begun during the studio session and finished on your own, with most of the work happening in class.  It is a scaffold on purpose.  Everything you produce here is work the RAG Knowledge Base Lab's evaluation asks for anyway, just done earlier and under supervision, plus one forward investment: a **regression harness** you will be glad to already have when the Rubric Pipeline Lab asks you to build a reproducible evaluation pipeline.

Work on your **own** pipeline and corpus (this lab is individual, though the studio makes collaboration on debugging natural).  Bring your RAG Knowledge Base Lab repository to the studio session running.

See the course schedule for the assigned and due dates.

---

## Before You Start

**This builds on:** the *RAG Quality: Chunking, Clustering, and Reranking* session, the **Golden-Set Benchmark** lab (whose items you reuse here), and your in-progress **RAG Knowledge Base** lab.  You do not need the RAG Knowledge Base lab finished; you need it *running*, even badly.  A pipeline that answers poorly is a better subject for a checkup than one that does not answer at all.

**Bring to the studio session:**

- Your RAG Knowledge Base repository, cloned and runnable.
- Your corpus indexed, with at least one chunking configuration working end to end.
- Your `goldenset.json` (or spreadsheet) from the Golden-Set lab.
- Five questions you actually care about the answers to, drawn from your own corpus.

Sanity check before you arrive:

```bash
# your pipeline answers one question, however badly
python3 ask.py "a question your corpus should be able to answer"
```

**Pace yourself:** most of this happens in class.  Part 2 goes quickly if Part 1 went well, because your golden set already exists.

**If your pipeline is not running,** come anyway and say so at the start.  Debugging it *is* the studio, and the checkup works on a pipeline you got running at 12:20.

---

## Choose Your Path

Same rubric, same credit.  The judgment (which configuration wins, which citations are real, what the failure means) is identical; the routes differ in how you collect and rerun the numbers.

| Route | How you measure | How you freeze it | Pick this if |
|-------|-----------------|-------------------|--------------|
| **No-code** | Query both configurations in **Open WebUI's** knowledge-base interface and record hits and misses in a spreadsheet | A **run sheet**: the pinned question list, the pinned settings, and a dated results column per run. Rerunning means working the sheet again and comparing columns | Your RAG Knowledge Base work took the low-code route, or you want your attention on the citation audit rather than on plumbing |
| **Low-code** | Same, or a small promptfoo run against your retriever | `promptfoo` YAML with the golden set as cases and `temperature: 0` pinned | You expect to take the Rubric Pipeline Lab's promptfoo direction |
| **Code** | A loop over your five queries that prints retrieved chunk IDs, scored against your own relevance judgments | A Python script grown from the class evaluation harness | You want the harness you will extend in the Rubric Pipeline Lab |

> **The no-code route is not the shortcut here.**  Measuring recall@k by hand means you look at every retrieved chunk, which is exactly how people discover that their retriever was returning the right document and the wrong *part* of it.  A script that prints `recall@5 = 0.6` hides that.

---

## Part 1: The Checkup Worksheet (60 points)

Complete `checkup.md` against your in-progress RAG Knowledge Base Lab pipeline.  Three measurements, in this order.

### 1.  Retrieval quality

For five queries representative of your corpus, measure **recall@k** under your current chunking configuration and one alternative (a different chunk size or overlap).  Record the table, name the winner, and carry the winning configuration back into the RAG Knowledge Base Lab.

**What recall@k means here, concretely.**  For each query you decide, *by reading*, which chunks in your corpus actually contain the answer.  Those are the relevant chunks.  Then you ask your retriever for its top `k` and count how many of the relevant ones came back.  Recall@k is that fraction, averaged over your five queries.  There is no way to skip the reading: recall is measured against *your* judgment of relevance, and you are the only source of it.

**Step by step:**

1.  Fix `k` (5 is a reasonable default) and **do not change it** between configurations.  Comparing recall@5 against recall@10 tells you nothing.
2.  For each of your five queries, read your corpus and write down which chunks *should* come back.  Do this **before** you run the retriever, so its answers do not anchor your judgment.
3.  Run all five under configuration A. Record which relevant chunks appeared in the top `k`.
4.  Change exactly **one thing** (chunk size or overlap, not both), re-index, and run the same five.
5.  Fill in the table and name the winner.

**Worked row**, so the format is unambiguous:

| Query | Relevant chunks (my judgment) | Config A (512/50): retrieved | Recall@5 | Config B (256/25): retrieved | Recall@5 |
|---|---|---|---|---|---|
| "What is the late policy for a three-day extension?" | c14, c15 | c14, c22, c31, c07, c19 | 1/2 = 0.50 | c14, c15, c22, c31, c07 | 2/2 = 1.00 |

Read that row before you build your own.  Config A retrieved `c14` and stopped; the policy spanned two chunks and the 512-token chunking put the second half of the sentence in a chunk that scored just below the cut.  That is a *chunking* failure that looks like a *retrieval* failure, and it is the single most common thing this checkup finds.

> **You've succeeded when** you have a five-row table with the same `k` in both columns, a named winner, and one sentence explaining *why* the winner won that refers to your corpus rather than to general principle.

### 2.  Citation audit

For five answered queries, one row each: the answer's central claim, the chunk it cites, and your verdict: **supported** (the chunk actually contains the claim) or **unsupported**.  The RAG Knowledge Base Lab rubric weights citation quality heavily; this is that muscle, built early.

**Step by step:**

1.  Ask your pipeline five questions and capture the full answer plus whatever it offered as a citation.
2.  For each, write down the answer's **single central claim**, in your words, in one sentence.  If you cannot state one, that is itself a finding: record "no single claim" and say why.
3.  Open the cited chunk and read it.  Not the document; the chunk.
4.  Verdict: **supported** if the claim is actually in there, **unsupported** if it is not, and **partial** if the chunk supports a weaker version of the claim than the answer stated.  Add the partial column; it is where most real systems live.

> **A "partial" is the interesting finding.**  The chunk says the extension is available "with prior permission"; the answer says students "may take a three-day extension."  Everything in the answer traces to the chunk, and a condition has quietly dropped.  No retrieval metric catches that.  You do.

> **You've succeeded when** you have five rows with verdicts, and at least one row where the verdict required actually reading the chunk rather than pattern-matching a phrase.

### 3.  One failure

Capture one concrete misbehavior you observed (a wrong retrieval, an unsupported citation, a failed abstention) with the query, the output, a one-paragraph hypothesis for the mechanism, and your planned fix.

A hypothesis is not a complaint.  "The model hallucinated" is a complaint.  A hypothesis names the stage that failed and says why:

> *"The retriever returned c31 rather than c14 for this query.  Both chunks mention 'extension,' but c31 is a syllabus paragraph about deadline extensions for the project and c14 is the late-work policy.  My embedding cannot distinguish the two senses because the chunks are short enough that neither carries the surrounding context that disambiguates them.  **Fix:** increase overlap so each chunk carries its section heading, and re-measure."*

Notice the shape: **which stage, what mechanism, what change, and how I would know it worked.**

> **You've succeeded when** your hypothesis names a *stage* (chunking, embedding, retrieval, reranking, generation) and your fix is something you could actually do this week.

## Part 2: The Regression Harness (40 points)

Freeze your evaluation so it can be rerun forever.  The point is not the code; it is that **six weeks from now you can prove a change made things better rather than believing it did.**

### Step by step

1.  **Pin a golden set.**  Start from your Golden-Set Benchmark items, then replace or extend with at least five corpus-specific questions.  Include at least one that **should trigger abstention**: a question your corpus cannot answer, where the correct behavior is to say so.  A harness with no abstention case cannot tell a confident wrong answer from a right one.
2.  **Pin the protocol.**  Temperature 0.0, a fixed seed, the model name, the chunking configuration, and `k`.  Write all five at the top of the harness, not in your memory of what you did.
3.  **Build it in your chosen medium**: a spreadsheet run sheet with a dated column per run, a promptfoo YAML case list, or a Python script grown from the class harness.
4.  **Run it twice**, changing nothing between runs.
5.  **Compare the two runs and show they agree.** `diff run1.txt run2.txt` on the code route; two columns side by side on the no-code route.  Paste the comparison, not a claim about it.
6.  **Commit** the harness and the golden set inside your RAG Knowledge Base repository, where the Rubric Pipeline Lab can pick them up.

> **If the two runs disagree,** you have found something worth more than the points for this part.  Say so in `checkup.md` and chase it: something in your pipeline is not pinned.  Usual suspects, in order: temperature is not actually zero, the seed is not being passed through, the index was rebuilt between runs, or your retriever ties on score and breaks the tie differently each time.  Report what you found even if you cannot fix it today.

> **You've succeeded when** two runs of the same golden set produce identical results, and you can point at the exact lines where the protocol is pinned.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Recall@k is 1.0 for every query | Your relevance judgments were made *after* seeing what the retriever returned | Redo step 2 of Part 1 on fresh queries, writing the relevant chunks down before you run anything |
| Recall@k is 0.0 for every query | Chunk IDs are not stable across re-indexing, so your judgments no longer refer to the same chunks | Record chunk *text* alongside the ID, or re-derive judgments after the final index build |
| Re-indexing with a new chunk size changes nothing | The index was not actually rebuilt; the old collection is still being queried | Delete or rename the collection before re-indexing. Confirm the count of stored chunks changed |
| The pipeline answers but shows no citation | Your prompt does not require one, or the chunk IDs are not being passed into the prompt | Fix it now and note it in the failure section; ungrounded answers are the thing this lab exists to find |
| Two runs disagree | Something is unpinned; see the Part 2 note above | Diagnose in this order: temperature, seed, index rebuild, score ties |
| Everything is slow enough that you cannot finish | You are re-embedding the whole corpus per query | Embed and store once; embed only the query per run. If it is still slow, cut the corpus for this checkup and say you did |

---

## Self-Check Before You Submit

- [ ] Recall@k measured for **two** chunking configurations, at the **same** `k`, on your own corpus.
- [ ] Relevance judgments were made before seeing the retriever's output.
- [ ] A winner is named, with a reason specific to your corpus.
- [ ] The citation audit has five rows, each with a stated central claim, the cited chunk, and a verdict.
- [ ] At least one **partial** or **unsupported** verdict, or an explicit note that you looked for one and everything checked out.
- [ ] One failure recorded with the query, the output, a hypothesis naming a **stage**, and a fix you could do this week.
- [ ] The golden set is pinned and includes at least one **abstention** case.
- [ ] The protocol is written down: temperature, seed, model, chunking configuration, `k`.
- [ ] Two runs, compared, with the comparison pasted.
- [ ] Everything committed inside the RAG Knowledge Base repository, with paths noted.
- [ ] Route named at the top of `checkup.md`.
- [ ] AI disclosure and hours answered.

---

## Deliverables

Submit `checkup.md` (the worksheet, with real measurements from your own pipeline), the harness (run sheet, YAML, or script) with its golden set, and the two-run agreement log, all committed in your RAG Knowledge Base Lab repository, with paths noted in the submission.  Name your route at the top of `checkup.md`.

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
