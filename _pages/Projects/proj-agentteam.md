---
layout: assignment
permalink: /Projects/AgentTeam
title: "CS357: Foundations of Artificial Intelligence - Final Project: Custom Agent Team"

info:
  coursenum: CS357
  points: 100
  goals:
    - To design and implement a team of specialized agents that accomplishes a goal oriented task end to end on local infrastructure
    - To justify every architectural decision with the patterns and principles of the course, including the small context window principle
    - To evaluate the system rigorously against a monolithic baseline with a fixed task set, metrics, and protocol
    - To make the system explainable through traces, citations, or calibrated confidence, with a human oversight gate on any consequential action
    - To lead a class discussion on the responsible use and governance of the system
    - To work in sustained team sprints with rotating roles and structured peer review
  rubric:
    - weight: 30
      description: System Design and Rationale
      preemerging: The system is a single undifferentiated prompt, or the design is undocumented
      beginning: Multiple agents exist but roles overlap, contexts are bloated, and design choices are unjustified
      progressing: The team decomposes the task into focused roles with a documented design table and topology, with some choices justified by course patterns
      proficient: The team decomposes the task into focused roles with small contexts, a complete design table, an explicit topology defense, deliberate state and handoff design, and every major choice justified by a named course pattern or principle
    - weight: 25
      description: Evaluation and Analysis
      preemerging: No systematic evaluation is provided
      beginning: Informal trials are described without a protocol, metric, or baseline
      progressing: A fixed task set with defined metrics is evaluated against the monolith baseline, with limited failure analysis
      proficient: A fixed task set with defined metrics and a reproducible protocol is evaluated against the monolith baseline, results are disaggregated where applicable, at least three failure modes are documented with transcripts, and one mitigation is implemented and re-measured
    - weight: 20
      description: Explainability and Governance
      preemerging: The system offers no insight into its behavior and no governance document accompanies it
      beginning: Traces exist but are not surfaced, and the governance document is generic
      progressing: The system surfaces traces, citations, or confidence to its user, a human gate guards consequential actions, and the governance document matches the system with minor gaps
      proficient: The system surfaces evidence following the honest hierarchy, a confirmation gate shows evidence at the moment of decision, an abstention behavior is demonstrated, the governance document matches the deployed behavior, and the team leads a substantive class discussion of responsible use grounded in their own measurements
    - weight: 13
      description: Implementation Quality and Artifact Packaging
      preemerging: The system fails to run from a fresh start, and no tests or CI are present
      beginning: The system runs but configuration is hard coded, exceptions are silent, setup is undocumented, and no tests exist
      progressing: The system runs from documented setup with externalized configuration and located exception handling; at least one automated test exists but CI is absent or fails intermittently
      proficient: The system runs from a fresh start in under three minutes following the readme, configuration is externalized, exceptions are handled with located messages and tracebacks, seeds and model versions are pinned, a test suite with at least one end-to-end test passes in CI on every push, the submission tag triggers a publish step that pushes the artifact to GHCR, Docker Hub, or npm, and the repository is organized for a stranger to navigate
    - weight: 12
      description: Presentation and Report
      preemerging: The presentation or report is missing
      beginning: The presentation demonstrates the happy path only, and the report restates the code
      progressing: The presentation demonstrates the system including one known failure case, and the report covers design, evaluation, and limitations
      proficient: The presentation demonstrates the system including a rehearsed failure disclosure, every teammate delivers part of the explainability story, and the report covers design rationale, evaluation with the baseline comparison, limitations, the governance summary, and individual contribution statements
  readings:
    - rtitle: "Agent Teams Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentteams.md"
    - rtitle: "Project Studio Protocol"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-projectstudio.md"
    - rtitle: "Explainability Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-explainability.md"

tags:
  - final-project
  - multi-agent
  - agents
  - governance

---

# Overview

Your team will design, build, evaluate, and present a **custom agent team**: a system of cooperating, specialized agents that accomplishes a real goal-oriented task end to end on your local AI stack. The project is the synthesis of the entire course: the agent loop, prompting, retrieval, memory, tools, orchestration, critique, debate or consensus, judging, explainability, and governance all have a place, and your report must show that each architectural choice was a *decision*, not a default.

Choose a task that matters to someone: a club operations assistant, a research literature triage system, a campus event concierge, a study-group coach, a document quality pipeline. The task must require at least three meaningfully distinct agent roles, at least one retrieval or tool capability, and at least one evaluation or critique stage. Tasks touching sensitive data require instructor approval and must run fully locally with de-identification; your governance document must say so.

Teams are your standing POGIL teams of three or four. Project roles (**Coordinator**, **Builder**, **Evaluator**, **Scribe**) rotate at every sprint boundary so that every member holds every role at least once; your report's contribution statements must show the rotation.

---

## Stage 1: Proposal (due week 12, first meeting)

A two-to-three page proposal containing:

**Checklist:**
- The task, the user it serves, and the success criterion in one paragraph each.
- The **agent design table**: one row per agent with role, system prompt summary, inputs, outputs, temperature, tools, and the isolated evaluation you will run on it.
- The topology (pipeline, router, planner, blackboard, or hybrid) with a three-sentence defense.
- The memory and context plan: what each agent carries, what is summarized, what is retrieved.
- The **pre-mortem**: your predicted specification gap, irreversible action, and global invariant, with the deterministic checker or gate that owns each.
- The evaluation plan: task set sketch, metrics, protocol, and the **monolith baseline** you will compare against.
- A sprint plan mapping the remaining weeks, with the role rotation schedule.

---

## Stage 2: Sprints and Studio (weeks 12 through 15)

Build in sprints aligned with the in-class studio days. Each sprint produces a runnable increment, an updated evaluation table (a number, not an adjective), and Scribe notes. The week 15 **gallery walk** is mandatory: host honestly (show one known failure), walk generously (Strength, Question, Risk cards), and triage all feedback into fix, disclose, or future work.

---

## Stage 3: Governance Discussion (week 13 through 15, scheduled per team)

Your team leads a 10-minute class discussion on the responsible use of *your* system, grounded in your governance document (the written assignment) and your own measurements: who could be harmed, what you gated, what you measured, what you would not deploy without. This is a discussion you facilitate, not a presentation you deliver; come with two genuine questions for the class.

---

## Stage 4: Submission and Presentation (final class meeting and exam slot)

**Deliverables:**
1. **The system**: a repository that runs from a fresh start following the readme in under three minutes, with externalized JSON configuration, pinned model versions, fixed seeds, and located exception handling throughout. The repository must include a test suite with at least one end-to-end test, a GitHub Actions CI workflow that runs the suite on every push, and a publish step (triggered by the submission tag) that pushes the container image or package to GHCR, Docker Hub, or npm. See the [ShipIt guide](https://www.billmongan.com/Ursinus-CS357/Assignments/ShipIt) for the expected packaging checklist.
2. **The report** (approximately six to eight pages): design rationale tied to course patterns, evaluation results including the monolith baseline comparison and failure analysis, explainability design, limitations (your "disclose" bucket, verbatim), the governance summary, and individual contribution statements covering the role rotation.
3. **The presentation** (12 minutes plus questions): a live demonstration including the happy path and one rehearsed failure disclosure, the evaluation table, and the 90-second explainability story, with every teammate speaking.
4. **The artifacts folder**: design table, pre-mortem, sprint notes, gallery walk cards received and your triage, and the release readiness checklist signed by your Evaluator (must include confirmation that CI passes on the submission SHA and the artifact is live at its published URL).

---

### Submission Rubric

See the **rubric** section in this assignment for the detailed evaluation breakdown.

## Reflection Prompts

Answer individually in your contribution statement:

- Which course principle did your team most rely on, and where did you knowingly violate one, with what consequence?
- What did the monolith baseline teach you that you did not expect?
- Do you certify that your contribution statement accurately represents your own work? Please identify any and all portions of the project that were not originally created by your team.
- Approximately how many hours did the project take you personally (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
