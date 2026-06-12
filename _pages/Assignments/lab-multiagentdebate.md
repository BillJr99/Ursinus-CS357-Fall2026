---
layout: assignment
permalink: /Assignments/MultiAgentDebate
title: "CS357: Foundations of Artificial Intelligence - Lab 4: Multi-Agent Debate and Consensus"

info:
  coursenum: CS357
  points: 100
  goals:
    - To implement multi-agent debate with independent first rounds and peer-informed revision rounds
    - To implement stochastic consensus with embedding clustering and a synthesis agent
    - To compare debate, consensus, and single-shot baselines at matched call budgets
    - To identify correlated failure modes that aggregation cannot repair
  rubric:
    - weight: 30
      description: Debate Implementation
      preemerging: The debate fails to run due to major issues, or the program fails to run
      beginning: The debate runs but fails on test questions due to one or more minor issues
      progressing: The debate runs correctly with configurable agents and rounds and majority vote aggregation, with a fragile component such as answer extraction
      proficient: The debate runs correctly with configurable agents, rounds, and temperature schedule, robust answer extraction, and both majority vote and judge aggregation options
    - weight: 25
      description: Consensus Implementation
      preemerging: The consensus pipeline fails to run due to major issues
      beginning: Drafts are sampled but clustering or synthesis is missing or incorrect
      progressing: The pipeline samples, clusters by embedding similarity with normalized vectors, and synthesizes from cluster representatives, with a minor issue
      proficient: The pipeline samples, clusters correctly with a justified distance threshold, synthesizes with support weighted majority handling and dissent disclosure, and the synthesizer context contains cluster summaries rather than all transcripts
    - weight: 25
      description: Comparative Evaluation
      preemerging: No evaluation is provided
      beginning: Conditions are compared anecdotally without matched budgets or a protocol
      progressing: Debate, consensus, and single shot baselines are compared on a labeled task set with accuracy and call counts reported
      proficient: All conditions are compared at matched call budgets on a labeled task set of at least ten items, accuracy and cost are reported per condition, at least one correlated failure is documented where all agents agreed on the same wrong answer, and the writeup explains why aggregation could not repair it
    - weight: 10
      description: Code Quality and Documentation
      preemerging: Code commenting and structure are absent, or code structure departs significantly from best practice
      beginning: Code commenting and structure is limited in ways that reduce the readability of the program
      progressing: Code documentation is present that re-states the explicit code definitions
      proficient: Code is documented at non-trivial points in a manner that enhances the readability of the program, with externalized configuration and located exception handling with tracebacks
    - weight: 10
      description: Writeup, Reflection, and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup, the pair log, and thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Multi-Agent Debate Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multiagentdebate.md"
    - rtitle: "Stochastic Consensus Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-consensus.md"

tags:
  - multi-agent
  - agents
  - evaluation

---

In this lab, you and your partner will build and rigorously compare the two aggregation architectures from class: **debate** (agents see and rebut each other) and **stochastic consensus** (independent samples, clustered by meaning, merged by synthesis). This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

## Part 1: Debate

Implement a configurable debate (number of agents, number of rounds, temperature schedule, all externalized in JSON configuration): independent answers in round one, peer-informed revisions in later rounds, and aggregation by both majority vote and an optional judge agent. Answer extraction must tolerate formatting drift (anchor on a required `ANSWER:` line and handle its absence gracefully with a located error message).

## Part 2: Consensus

Implement the sample, cluster, synthesize pipeline: $k$ high-temperature drafts, embedding clustering over normalized vectors with cosine geometry, and a low-temperature synthesizer that receives one representative per cluster with its support count, follows the majority on conflicts, and **discloses any close disagreement in one line**. Demonstrate the pipeline on a long-form question with no single correct answer (the in-class tomatillo salsa question is a fine starting point; choose your own analogous question too).

## Part 3: The Shootout

Construct a labeled task set of at least ten questions with checkable answers (arithmetic word problems with traps work well). At **matched call budgets**, compare:

1. Single shot (one agent, one sample).
2. Self-consistency (sample $k$, majority vote, no debate rounds).
3. Full debate (your Part 1 system).

Report accuracy and total model calls per condition. Then find and document at least one **correlated failure**: a question where every agent agrees on the same wrong answer. Explain, using the independence argument from class, why no aggregation strategy could have saved you, and what non-LLM addition (a tool, retrieval) would.

## Part 4: Threshold Sensitivity

Vary the clustering `distance_threshold` across at least three values and report how the cluster structure, and therefore the synthesized consensus, changes on your long-form question. Conclude with one paragraph: who should own this parameter in a deployed system, and how would you document its setting?

## Deliverables

Submit a ZIP containing your code, JSON configuration, task set with labels, comparison results (CSV or table), debate and consensus transcripts for at least two questions each, the correlated failure analysis, pair log, and a readme writeup of approximately two pages. Ensure reproducibility by fixing random seeds where determinism is intended and listing software version information.

## Reflection Prompts

- Debate and consensus spend extra computation to buy reliability. Name one decision in your own life where you would pay that cost and one where you would not, and map each onto a condition from your shootout.
- Your synthesizer "follows the majority." When is the majority of a model's samples the wrong thing to follow?
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
