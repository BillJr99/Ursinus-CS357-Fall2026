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
      proficient: The loop runs correctly with structured critic output, a round budget, a fail-closed JSON fallback, and on budget exhaustion returns the best draft with outstanding critique attached
    - weight: 25
      description: Critic Calibration
      preemerging: No calibration is attempted
      beginning: A few informal trials are described without planted defects or a protocol
      progressing: The critic is tested against drafts with planted defects and a detection rate is reported per criterion
      proficient: The critic is tested against at least ten drafts with planted defects spanning every criterion, per criterion detection and false positive rates are reported, and the weakest criterion is rewritten and retested with results
    - weight: 20
      description: Reward Hacking Analysis
      preemerging: No reward hacking analysis is provided
      beginning: A loophole is described but not demonstrated
      progressing: A working reward hack against the rubric is demonstrated with a transcript
      proficient: A working reward hack is demonstrated, a rubric patch closes it, and the patched rubric is shown to still accept legitimately good drafts
    - weight: 15
      description: Comparative Evaluation
      preemerging: No comparison is provided
      beginning: A comparison is described anecdotally without a protocol
      progressing: Critique and refine is compared with single-shot generation on a task set with a defined metric
      proficient: The comparison uses a fixed task set, metric, and protocol, reports quality and cost (model calls) for both conditions, and draws a defensible conclusion about when the pattern earns its latency
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

## Part 1: The Loop

Choose a generation task with checkable criteria: a structured class announcement, a function docstring, an abstract for a lab report, or a concept of your own. Implement:

1. A **generator** agent with a warm temperature for the first draft and a cooler temperature for revisions (justify your settings using sampling theory from class).
2. A **critic** agent that receives a JSON rubric of at least four criteria with observable descriptors, and returns `{"verdict": "accept" | "revise", "issues": [...]}`. The critic runs at temperature 0 with a fixed seed.
3. A **loop** with a configurable round budget (externalized in JSON configuration). Invalid critic JSON fails closed (treated as revise) and is logged. On budget exhaustion, your system returns the final draft *with its outstanding critique attached*.

## Part 2: Calibrate the Critic

Write at least ten drafts with **planted defects** that you select to span every criterion (and include at least two defect-free drafts). Run the critic over all of them and report, per criterion, the detection rate and the false positive rate. Identify the weakest criterion, rewrite its descriptors to be more observable, and report the improvement.

## Part 3: Reward Hack Your Own Rubric

Attempt to produce a draft that the critic accepts while being, by your human judgment, a poor artifact: satisfy the letter while betraying the intent. Document the successful hack with a transcript, then **patch the rubric** to close the loophole and demonstrate that the patch (a) rejects the hack and (b) still accepts your defect-free drafts.

## Part 4: Did It Earn Its Latency?

On a fixed set of at least eight tasks, compare single-shot generation against your full critique and refine loop. Score both conditions with the same instrument (your calibrated critic on a held-out rubric, or a blind human ranking between you and your partner). Report quality and cost (number of model calls), and conclude in a paragraph when the pattern is and is not worth deploying.

## Deliverables

Submit a ZIP containing your code, JSON configuration and rubric files, planted-defect drafts with labels, calibration results (CSV or table), reward hack transcript and patch, comparison results, pair log, and a readme writeup of approximately two pages. Ensure reproducibility by fixing random seeds and listing software version information.

## Reflection Prompts

- Your critic is an LLM judging an LLM. Where in this lab did you, the humans, remain indispensable, and what does that say about removing humans from evaluation pipelines?
- Describe the most surprising critic behavior you observed (a missed defect, a phantom defect, an oscillation).
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
