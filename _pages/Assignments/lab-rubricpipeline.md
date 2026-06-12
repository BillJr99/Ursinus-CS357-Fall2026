---
layout: assignment
permalink: /Assignments/RubricPipeline
title: "CS357: Foundations of Artificial Intelligence - Lab 5: An LLM Rubric-Grading Pipeline"

info:
  coursenum: CS357
  points: 100
  goals:
    - To build a batch pipeline that scores a folder of submissions against a JSON rubric using a local model and emits a CSV report
    - To require and verify quoted evidence for every awarded score
    - To validate the judge against human scores on a calibration set
    - To measure at least one judge bias empirically and propose a countermeasure
  rubric:
    - weight: 30
      description: Pipeline Implementation
      preemerging: The pipeline fails to run due to major issues, or the program fails to run
      beginning: The pipeline runs but fails on the test submissions due to one or more minor issues
      progressing: The pipeline scores a folder of submissions against the JSON rubric and emits a well formed CSV, with a fragile component such as JSON parsing fallback or evidence capture
      proficient: The pipeline robustly scores a folder or ZIP of submissions, emits one CSV row per artifact with per criterion levels, quoted evidence, and weighted totals, handles malformed judge output with a fail closed policy and located logging, and externalizes the rubric, model, and paths in configuration
    - weight: 25
      description: Human Agreement Validation
      preemerging: No human validation is attempted
      beginning: Human scores exist but are collected after seeing the judge output, or agreement is not quantified
      progressing: Both partners independently score a calibration set before running the judge, and human to human and human to judge agreement are reported
      proficient: Both partners independently score a calibration set of at least eight artifacts blind to the judge, agreement is quantified per criterion, the weakest criterion is identified, and a rubric revision is tested with before and after agreement reported
    - weight: 20
      description: Bias Measurement
      preemerging: No bias probe is attempted
      beginning: A bias is discussed but not measured
      progressing: One judge bias (position, verbosity, or byline) is measured with a controlled experiment
      proficient: One judge bias is measured with a controlled experiment of adequate size, the effect is quantified, a countermeasure is implemented or prescribed, and its residual risk is discussed honestly
    - weight: 15
      description: Evidence Verification
      preemerging: Evidence quotes are not collected
      beginning: Evidence quotes are collected but never verified
      progressing: Evidence quotes are spot checked by hand with a reported faithfulness rate
      proficient: Evidence quotes are verified programmatically against the source artifact (substring or fuzzy match), hallucinated quotes are flagged in the CSV, and the hallucinated evidence rate is reported
    - weight: 10
      description: Writeup, Reflection, and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup, the pair log, and thoughtful answers to the reflection prompts
  readings:
    - rtitle: "LLM-as-Judge Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmasjudge.md"
    - rtitle: "Evaluating Outputs Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md"

tags:
  - evaluation
  - llm-as-judge
  - pipelines

---

In this lab, you and your partner will industrialize the in-class judge into a batch grading pipeline: a JSON rubric and a folder (or ZIP) of submissions go in; a CSV of per-criterion scores, quoted evidence, and weighted totals comes out; and, crucially, you will measure whether the judge deserves to be trusted. **All submissions in this lab are synthetic artifacts you author yourselves; no real student work may be used.** This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

## Part 1: The Pipeline

Author a JSON rubric with at least four criteria, each with four observable levels and integer weights summing to 100, for a short artifact type of your choosing (a persuasive paragraph, a function with docstring, a lab abstract). Then implement a pipeline that:

1. Walks a folder or ZIP of text submissions (configuration externalized: paths, model, rubric file, temperature, seed).
2. Prompts your local model to award a level per criterion **with a quoted sentence of evidence for each score**, returning strict JSON.
3. Fails closed on malformed judge output (flag the row for human review rather than guessing), with located exception messages and tracebacks.
4. Emits a CSV with one row per submission: filename, per-criterion level and evidence, weighted total, and any flags.

Author at least twelve synthetic submissions spanning the quality range, including at least two edge cases (empty file, off-topic content).

## Part 2: Validate Against Humans

Before running the judge, you and your partner **independently** hand-score a calibration set of at least eight submissions. Then run the judge and report: human-to-human agreement per criterion, and human-to-judge agreement per criterion. Identify the criterion with the worst machine-human gap, revise its level descriptors toward observability, and report agreement before and after the revision.

## Part 3: Verify the Evidence

Implement a programmatic check that each quoted evidence string actually appears in the source submission (exact substring or a fuzzy match with a stated threshold). Report the **hallucinated evidence rate** across your corpus, and flag offending rows in the CSV.

## Part 4: Measure a Bias

Design and run a controlled probe of one judge pathology from class: position bias (A/B comparisons in both orders), verbosity bias (padded versus unpadded versions of the same content), or byline bias (identical essays with varied author names). Quantify the effect, implement or prescribe a countermeasure, and state honestly what risk remains.

## Deliverables

Submit a ZIP containing your code, JSON rubric and configuration, synthetic submission corpus, output CSV, calibration scores and agreement analysis, bias probe design and results, pair log, and a readme writeup of approximately two pages. Ensure reproducibility by fixing random seeds and listing software version information.

## Reflection Prompts

- Your pipeline could grade a real class's submissions tomorrow by changing one path in a configuration file. List two conditions that you believe must be satisfied before that would be responsible, and connect each to a course concept.
- Where did you and your partner disagree with each other more than with the judge, and what does that imply about rubrics as instruments?
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
