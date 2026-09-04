---
layout: assignment
permalink: /Assignments/RAGCheckup
title: "CS357: Foundations of Artificial Intelligence - Lab: RAG Quality Checkup Checkpoint"

info:
  coursenum: CS357
  purpose: "To design a personal ten-item benchmark that separates what your model reliably knows from where it invents, to run a structured mid-flight diagnostic on your in-progress RAG pipeline, measuring retrieval quality, auditing citations, and understanding one failure, and then to freeze both into a rerunnable regression harness that follows you into the Rubric Pipeline Lab."
  tilt:
    task: "Design a ten-item golden set with a per-item prediction and rationale, complete the studio worksheet on your own RAG Knowledge Base Lab pipeline (recall@k across two chunking configurations, a citation audit, and one analyzed failure), then pin that golden set into a rerunnable regression harness and demonstrate reproducibility."
    criteria: "I grade this on the design quality of your benchmark items and their rationales, a completed worksheet with real measurements from your own pipeline, and a regression harness that reruns identically.  See the rubric below for the full breakdown."
  points: 100
  goals:
    - To design benchmark items that deliberately probe both reliable knowledge and hallucination-prone territory
    - To state a falsifiable prediction and a scoring rule for each item before running it
    - To measure retrieval quality (recall@k) empirically across two chunking configurations on your own corpus
    - To audit citations by hand, classifying each answer's claims as supported or unsupported by the cited chunk
    - To capture and analyze one concrete pipeline failure with a hypothesis and planned fix
    - To freeze an evaluation into a rerunnable regression harness, demonstrate its reproducibility, and separate knowledge failures from metric failures in the results
  rubric:
    - weight: 25
      description: "Benchmark Design (Goals 1-2)"
      preemerging: Fewer than ten items exist, or items lack expected answers
      beginning: Ten items exist with expected answers, but the set does not deliberately mix reliable and hallucination-prone territory, or rationales are missing
      progressing: The set mixes five expected-reliable and five expected-fragile items with rationales, but several rationales do not connect to why model training data would be thick or thin there
      proficient: "Ten items (five expected-reliable, five expected-fragile) each with an expected answer, a scoring rule the harness can apply, and a one-sentence rationale grounded in training-data reasoning (recency, locality, specificity, or citation-shaped risk). This row is about judgment, not medium: it is earned identically whether the set is a JSON file, a promptfoo YAML case list, or a spreadsheet"
    - weight: 45
      description: "The Checkup Worksheet (Goals 3-5)"
      preemerging: The worksheet is empty or filled with invented numbers not produced by the student's pipeline
      beginning: Some measurements exist but only one chunking configuration was tested, or the citation audit is missing
      progressing: recall@k for both configurations and a five-row citation audit are complete, but the failure case is missing or has no hypothesis
      proficient: "recall@k is measured for both chunking configurations on the student's own corpus with the winner identified; the five-row citation audit classifies each claim as supported or unsupported with chunk references; and one observed failure is recorded with a plausible hypothesis and a planned fix. The medium does not matter: measurements taken by hand in Open WebUI's knowledge-base view earn this row on the same terms as measurements printed by a script, provided the numbers came from the student's own pipeline"
    - weight: 30
      description: "The Regression Harness (Goal 6)"
      preemerging: No harness exists, or it cannot be rerun
      beginning: A harness exists but the golden set is not pinned (questions or scoring change between runs), or it was run only once
      progressing: The harness reruns with a pinned golden set and protocol, but the two runs' outputs were not compared, prediction misses are listed rather than explained, or the harness is not committed alongside the RAG Knowledge Base Lab work
      proficient: The harness (a scripted run sheet in a spreadsheet, declarative promptfoo YAML, or plain Python built on the class evaluation harness, student's choice) pins the Part 1 golden set, extended with corpus-specific items, and a fixed protocol (temperature 0.0, a fixed seed, the model named); two runs are shown to agree; every item whose outcome differs from its Part 1 prediction gets a sentence separating knowledge failure from metric failure; and the harness lives in the RAG Knowledge Base Lab repository where the Rubric Pipeline Lab's pipeline work can pick it up
  readings:
    - rtitle: "Hallucinations and Evaluating Agent Outputs Activity: the evaluation harness, and the Part IIb benchmark-design work that Part 1 finishes"
      rlink: "Activities/liascript-evaluatingoutputs.md"
      liapage: true
    - rtitle: "RAG Quality: Chunking, Clustering, and Reranking Activity"
      rlink: "Activities/liascript-ragquality.md"
      liapage: true
    - rtitle: "Required prep for the Rubric Pipeline Lab: the Testing Agents tutorial, Evaluation, Regression, and the Non-Determinism Problem"
      rlink: "../Tutorials/TestingAgents"
    - rtitle: "promptfoo, for declarative LLM and agent evaluation and red-teaming.  One of the harness options, and it runs against Ollama"
      rlink: "https://www.promptfoo.dev/"

tags:
  - rag
  - evaluation
  - regression-testing
  - lab

---

This small **lab** is a structured checkup on the RAG pipeline you are building in the RAG Knowledge Base Lab, begun during the open studio in *How I AI* and finished on your own, with most of the work happening in class.  It is handed out mid-window on purpose: your RAG Knowledge Base pipeline is running by then and is not yet due, which is the only point in the term when a diagnostic can still change what you build.  It opens by building the thing every checkup needs and nobody has: a **golden set**, ten questions with expected answers and a stated scoring rule, designed so that five should be easy for your model and five should not.  It is a scaffold on purpose.  Everything else you produce here is work the RAG Knowledge Base Lab's evaluation asks for anyway, just done earlier and under supervision, plus one forward investment: a **regression harness**, built on that golden set, that you will be glad to already have when the Rubric Pipeline Lab asks you to build a reproducible evaluation pipeline.

Work on your **own** pipeline and corpus (this lab is individual, though the studio makes collaboration on debugging natural).  Bring your RAG Knowledge Base Lab repository to the studio session running.

See the course schedule for the assigned and due dates.

---

## Before You Start

**This builds on:** the *Hallucinations and Evaluating Agent Outputs* session, where we mapped the territory where models are unreliable and wrote the evaluation harness Part 1 starts from; the *RAG Quality: Chunking, Clustering, and Reranking* session; and your in-progress **RAG Knowledge Base** lab.  You do not need the RAG Knowledge Base lab finished; you need it *running*, even badly.  A pipeline that answers poorly is a better subject for a checkup than one that does not answer at all.

**Bring to the studio session:**

- Your RAG Knowledge Base repository, cloned and runnable.
- Your corpus indexed, with at least one chunking configuration working end to end.
- Any benchmark questions you already sketched in the *Hallucinations and Evaluating Agent Outputs* session (Part IIb and its Exercise 1).  Part 1 turns them into a finished ten-item set; if you have none, bring nothing and start there.
- Five questions you actually care about the answers to, drawn from your own corpus.

Sanity check before you arrive:

```bash
# your pipeline answers one question, however badly
python3 ask.py "a question your corpus should be able to answer"
```

**Pace yourself:** most of this happens in class.  **Part 1 is the exception, and it is meant to be done before the studio**: it is paper-and-thinking work that needs no running pipeline, and doing it early is the single best way to make the studio session productive.  Part 3 then goes quickly, because your golden set already exists.

**Time budget.**  Part 1 is about **one hour**, and most of that is judgment rather than typing.  Parts 2 and 3 are the studio session plus an hour or two of finishing on your own.  If Part 1 is running past an hour you are polishing: ten adequate items beat six perfect ones.

**If your pipeline is not running,** come anyway and say so at the start.  Debugging it *is* the studio, and the checkup works on a pipeline you got running at 12:20.

---

## Choose Your Path

Same rubric, same credit.  **Part 1 is identical on all three routes**: designing ten good items is the assignment and the file format is a detail.  The judgment in the rest of the lab (which configuration wins, which citations are real, what the failure means) is identical too; the routes differ only in how you collect and rerun the numbers.

| Route | Where your golden set lives | How you measure | How you freeze it | Pick this if |
|-------|-----------------------------|-----------------|-------------------|--------------|
| **No-code** | A spreadsheet, one row per item: `question`, `expected`, `rule`, `rationale` | Query both configurations in **Open WebUI's** knowledge-base interface and record hits and misses in a spreadsheet | A **run sheet**: the pinned question list, the pinned settings, and a dated results column per run. Rerunning means working the sheet again and comparing columns | Your RAG Knowledge Base work took the low-code route, or you want your attention on the citation audit rather than on plumbing |
| **Low-code** | A `promptfoo` YAML case list | Same, or a small promptfoo run against your retriever | `promptfoo` YAML with the golden set as cases and `temperature: 0` pinned | You expect to take the Rubric Pipeline Lab's promptfoo direction |
| **Code** | `goldenset.json` | A loop over your five queries that prints retrieved chunk IDs, scored against your own relevance judgments | A Python script grown from the class evaluation harness | You want the harness you will extend in the Rubric Pipeline Lab |

> **The no-code route is not the shortcut here.**  Measuring recall@k by hand means you look at every retrieved chunk, which is exactly how people discover that their retriever was returning the right document and the wrong *part* of it.  A script that prints `recall@5 = 0.6` hides that.  The same holds in Part 1: running ten items by hand means you read every answer closely, which is exactly what catches a *metric failure*, where your rule mis-graded a correct answer.  Students on the code route often miss those because the harness printed FAIL and they believed it.

---

## Part 1: Design Your Golden Set (25 points)

Before you can tell whether your pipeline is any good, you need a fixed set of questions with known answers.  Build one: ten items, each with `question`, `expected` (the answer text your scoring rule matches), `rule` (exact, substring, or normalized match, your choice per item, stated), and `rationale` (one sentence predicting whether the model will pass and *why*, reasoned from training data: how recent, how local, how specific, how citation-shaped the fact is).

These ten items are about the **model**, not yet about your corpus.  That is deliberate.  Part 3 extends the set with corpus-specific questions, and the gap between how the bare model does on the fragile five and how the same model does with your retrieved chunks in front of it is the entire argument for having built a RAG pipeline at all.  You cannot make that argument without a before.

Design deliberately:

- **Five expected-reliable items**: stable, well-documented knowledge (famous dates, authors, capitals, definitions).
- **Five expected-fragile items**: the territory the *Hallucinations and Evaluating Agent Outputs* session mapped: local or niche facts, post-cutoff events, exact statistics, and at least one citation-shaped item (a request for a source, reference, or attribution).

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
4.  Write every rationale as a prediction plus a reason.  The prediction is what Part 3 grades you against.

> **You've succeeded when** you have ten items, each with all four fields, and a classmate reading only your rationales could predict your pass rate to within two items.

---

## Part 2: The Checkup Worksheet (45 points)

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

## Part 3: The Regression Harness (30 points)

Freeze your evaluation so it can be rerun forever.  The point is not the code; it is that **six weeks from now you can prove a change made things better rather than believing it did.**

### Step by step

1.  **Pin a golden set.**  Take your Part 1 items and **extend** them with at least five corpus-specific questions drawn from your own corpus.  Keep the Part 1 items; step 6 grades your predictions against what actually happened.  Include at least one question that **should trigger abstention**: something your corpus cannot answer, where the correct behavior is to say so.  A harness with no abstention case cannot tell a confident wrong answer from a right one.
2.  **Pin the protocol.**  Temperature 0.0, a fixed seed, the model name, the chunking configuration, and `k`.  Write all five at the top of the harness, not in your memory of what you did.
3.  **Build it in your chosen medium**: a spreadsheet run sheet with a dated column per run, a promptfoo YAML case list, or a Python script grown from the class harness.
4.  **Run it twice**, changing nothing between runs.
5.  **Compare the two runs and show they agree.** `diff run1.txt run2.txt` on the code route; two columns side by side on the no-code route.  Paste the comparison, not a claim about it.
6.  **Classify your misses.**  A miss is any Part 1 item whose outcome differs from the prediction you wrote in its `rationale`, in *either* direction; a fragile item that passed is as interesting as a reliable one that failed.  In one sentence each, say which it was:
    - **Knowledge failure**: the model genuinely does not have the fact.
    - **Metric failure**: the model answered correctly (or incorrectly) and *your rule graded it wrong*.  For example, the model answered "seventeen seventy-six" and your substring rule looked for "1776".

    That distinction is why you wrote the predictions down first.  A benchmark whose failures are mostly metric failures is measuring your rules, not your system.  In a RAG pipeline you may also find a third kind, a **retrieval failure**: the model would have known the answer from the right chunk and did not get it.  If you see one, name it, because it points straight back at Part 2's recall numbers.
7.  **Commit** the harness and the golden set inside your RAG Knowledge Base repository, where the Rubric Pipeline Lab can pick them up.

### A worked miss, for calibration

> **Item 7** (fragile, citation-shaped).  Predicted FAIL, outcome PASS.
>
> I asked for a source on a claim about local rainfall and expected an invented citation.  The model instead refused, saying it did not have a reliable source.  That is a **metric failure**: my rule scored "no answer" as a pass because the invented-citation string was absent, but abstention and correctness are not the same outcome and my rule cannot tell them apart.  **Revision:** split this into two items, one that scores abstention as a pass and one that scores a fabricated citation as a fail, so the two behaviors stop sharing a row.

> **If the two runs disagree,** you have found something worth more than the points for this part.  Say so in `checkup.md` and chase it: something in your pipeline is not pinned.  Usual suspects, in order: temperature is not actually zero, the seed is not being passed through, the index was rebuilt between runs, or your retriever ties on score and breaks the tie differently each time.  Report what you found even if you cannot fix it today.

> **You've succeeded when** two runs of the same golden set produce identical results, you can point at the exact lines where the protocol is pinned, and every prediction miss is explained as a knowledge failure or a metric failure.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Recall@k is 1.0 for every query | Your relevance judgments were made *after* seeing what the retriever returned | Redo step 2 of Part 2 on fresh queries, writing the relevant chunks down before you run anything |
| Recall@k is 0.0 for every query | Chunk IDs are not stable across re-indexing, so your judgments no longer refer to the same chunks | Record chunk *text* alongside the ID, or re-derive judgments after the final index build |
| Re-indexing with a new chunk size changes nothing | The index was not actually rebuilt; the old collection is still being queried | Delete or rename the collection before re-indexing. Confirm the count of stored chunks changed |
| The pipeline answers but shows no citation | Your prompt does not require one, or the chunk IDs are not being passed into the prompt | Fix it now and note it in the failure section; ungrounded answers are the thing this lab exists to find |
| Two runs disagree | Something is unpinned; see the Part 3 note above | Diagnose in this order: temperature, seed, index rebuild, score ties |
| Everything is slow enough that you cannot finish | You are re-embedding the whole corpus per query | Embed and store once; embed only the query per run. If it is still slow, cut the corpus for this checkup and say you did |
| Everything "passes" and you do not believe it | Your `expected` strings are too short. `"1"` is a substring of almost every answer | Lengthen `expected`, or switch that item to exact or normalized matching |
| A correct answer scores FAIL | Formatting mismatch, not a knowledge gap | This is a **metric failure** and it is a finding, not a bug to hide. Record it as one, then decide whether to normalize |
| The model refuses instead of answering | Abstention, which is a distinct outcome from right and wrong | Your rule probably cannot distinguish abstention from a wrong answer. Say so in the analysis; that observation is worth points |
| promptfoo cannot find your provider | The Ollama provider string is wrong or the server is not up | Use `ollama:chat:llama3.2` and confirm your model server answers first |

---

## Self-Check Before You Submit

- [ ] Ten benchmark items, with **five** predicted reliable and **five** predicted fragile.
- [ ] The fragile five cover all four kinds of thin territory, including **at least one citation-shaped** item.
- [ ] Every item has `question`, `expected`, a stated `rule`, and a `rationale`.
- [ ] Every rationale names a **training-data reason** (recency, locality, specificity, citation-shaped risk), not just a difficulty guess.
- [ ] Recall@k measured for **two** chunking configurations, at the **same** `k`, on your own corpus.
- [ ] Relevance judgments were made before seeing the retriever's output.
- [ ] A winner is named, with a reason specific to your corpus.
- [ ] The citation audit has five rows, each with a stated central claim, the cited chunk, and a verdict.
- [ ] At least one **partial** or **unsupported** verdict, or an explicit note that you looked for one and everything checked out.
- [ ] One failure recorded with the query, the output, a hypothesis naming a **stage**, and a fix you could do this week.
- [ ] The pinned harness set is the Part 1 golden set **plus at least five** corpus-specific items, including at least one **abstention** case.
- [ ] The protocol is written down: temperature, seed, model, chunking configuration, `k`.
- [ ] Two runs, compared, with the comparison pasted.
- [ ] **Every** prediction miss is classified as a knowledge failure or a metric failure, in a sentence.
- [ ] Everything committed inside the RAG Knowledge Base repository, with paths noted.
- [ ] Route named at the top of `checkup.md`.
- [ ] AI disclosure and hours answered.

If a box is unchecked, that is a specific, fixable thing rather than a vague worry.  Fix it and check it.

---

## Deliverables

Submit your golden set (`goldenset.json`, the promptfoo YAML case list, or the spreadsheet CSV), `checkup.md` (the worksheet, with real measurements from your own pipeline, plus the prediction-versus-outcome miss analysis), the harness (run sheet, YAML, or script) with its extended golden set, and the two-run agreement log, all committed in your RAG Knowledge Base Lab repository, with paths noted in the submission.  Name your route at the top of `checkup.md`.

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Part 1: Golden-Set Design | 25 |
| Part 2: Checkup Worksheet | 45 |
| Part 3: Regression Harness | 30 |
| **Total** | **100** |

## Reflection Prompts

- Which fragile item surprised you in either direction, and what does that tell you about your mental model of the training data?
- Which chunking configuration won on your corpus, and did the margin surprise you?
- What did the citation audit reveal that the recall@k numbers alone would have hidden?
- AI disclosure: list any generative-AI tools you used, for what, and how you verified the results (or state 'none').
- Approximately how many hours it took you to finish this lab (I will not judge you for this at all; I am simply using it to gauge if the labs are too easy or hard)?
