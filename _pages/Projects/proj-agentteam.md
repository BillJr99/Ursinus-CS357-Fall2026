---
layout: assignment
permalink: /Projects/AgentTeam
title: "CS357: Foundations of Artificial Intelligence - Final Project: Custom Agent Team"

info:
  coursenum: CS357
  purpose: "To synthesize the entire course into one running, published, evaluated multi-agent system you can defend — proving that each architectural choice was a decision, not a default."
  tilt:
    task: "Design, build, evaluate, and present a team of at least three specialized agents that accomplishes a real goal-oriented task end to end on your local stack, benchmarked against a monolithic baseline and governed by a document you can defend."
    criteria: "Assessed most heavily on system design and rationale and on evaluation against a baseline, then explainability and governance, implementation quality, presentation, and stakeholder grounding and process; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To design and implement a team of at least three specialized agents that accomplishes a goal-oriented task end to end on local infrastructure
    - To justify every major architectural decision by naming the course pattern or principle that motivated it
    - To evaluate the multi-agent system against a monolithic baseline using a fixed ten-task set, defined metrics, and a reproducible protocol, and to document at least three failure modes with transcripts
    - To make the system explainable through the honest evidence hierarchy with a human confirmation gate on consequential actions and a demonstrated abstention behavior
    - To commit a governance document that matches the deployed system's behavior and to lead a class discussion grounded in the team's own measurements
    - To complete four sprints with rotating POGIL roles, producing a runnable increment and a numeric evaluation update at each sprint boundary
    - To ground the system in the team's Stakeholder Brief and Literature Review, follow the Project Thread process standards, and communicate the result to technical and non-technical audiences using the Open Questions to assess growth (Goals 11, 12, 13, 14, 15)
  rubric:
    - weight: 25
      description: System Design and Rationale
      preemerging: The system is a single undifferentiated prompt, or the design is undocumented
      beginning: Multiple agents exist but roles overlap, contexts are bloated, and design choices are unjustified
      progressing: The team decomposes the task into focused roles with a documented design table and topology statement; some choices reference a course pattern but others are left as defaults
      proficient: The team decomposes the task into at least three agents with meaningfully distinct roles and small contexts; the design table is complete with one row per agent covering role, prompt summary, inputs, outputs, temperature with justification, and tools; the report names the topology (pipeline, router, planner, blackboard, or hybrid) and defends the choice in 3 sentences; every major choice — including state design, handoff format, and temperature settings — is justified by a named course pattern or principle
    - weight: 22
      description: Evaluation and Analysis
      preemerging: No systematic evaluation is provided
      beginning: Informal trials are described without a protocol, metric, or baseline comparison
      progressing: A fixed task set with defined metrics is evaluated against the monolith baseline with numeric results; failure analysis is present but fewer than three failure modes are documented with transcripts
      proficient: A fixed ten-task evaluation set (finalized no later than Sprint 1) is evaluated against the monolith baseline with a stated protocol that a stranger could reproduce; metrics are numeric (e.g., precision, recall, parse success rate, latency); results are disaggregated where applicable; at least three failure modes are documented with agent transcripts showing the actual inputs and outputs; at least one mitigation is implemented and re-measured with before-and-after numbers
    - weight: 17
      description: Explainability and Governance
      preemerging: The system offers no insight into its behavior and no governance document accompanies it
      beginning: Traces exist but are not surfaced to the user; the governance document is present but generic — it does not match the specific system's agents, data flows, or risks
      progressing: The system surfaces traces, citations, or confidence scores to the user; a human gate guards at least one consequential action; the governance document matches the system with minor gaps such as a missing data retention period or an unaddressed pre-mortem risk
      proficient: The system surfaces evidence following the honest hierarchy (direct retrieval citation preferred over generated summary); a confirmation gate shows the user the evidence at the moment of decision for every consequential action; an abstention behavior is demonstrated in the presentation (the system declines rather than hallucinating when evidence is absent); the committed GOVERNANCE.md matches the deployed behavior including data handling, human gates, and incident response; the team leads a 10-minute class discussion grounded in their own measurements — at least one claim is supported by a number from the evaluation table
    - weight: 11
      description: Implementation Quality and Artifact Packaging
      preemerging: The system fails to run from a fresh start, and no tests or CI are present
      beginning: The system runs but configuration is hard-coded, exceptions produce silent failures, setup is undocumented, and no tests exist
      progressing: The system runs from documented setup with externalized configuration and located exception handling (error messages name the file and line); at least one automated test exists but CI is absent or fails intermittently
      proficient: The system runs from a fresh start in under three minutes following the README on a machine the team has not configured; all configuration (model names, paths, seeds) is externalized to config.json with no hard-coded values in any committed file; exceptions are handled with located messages and tracebacks; model versions and random seeds are pinned; a test suite with at least one end-to-end test passes in CI on every push; the submission tag triggers a publish step that pushes the artifact to GHCR, Docker Hub, or npm; the repository is organized so a stranger can navigate it in under 5 minutes
    - weight: 10
      description: Presentation and Report
      preemerging: The presentation or report is missing
      beginning: The presentation demonstrates only the happy path; the report restates the code without design rationale or evaluation results
      progressing: The presentation demonstrates the system including one known failure case; the report covers design, evaluation results, and limitations but the baseline comparison table is absent or the contribution statements do not document role rotation
      proficient: The presentation demonstrates the happy path live (not screenshots), includes a rehearsed failure disclosure showing a case where the system fails and explaining why, shows the evaluation table with the baseline comparison side by side, delivers the 90-second explainability story, and has every teammate speaking for a substantive portion; the report covers design rationale tied to named course patterns, the evaluation results with baseline comparison and failure analysis with transcripts, the explainability design, the "disclose" bucket from the gallery walk verbatim, a governance summary referencing the committed GOVERNANCE.md, and individual contribution statements documenting which role each member held in each sprint
    - weight: 15
      description: Stakeholder Grounding, Multi-Audience Communication, and Process Quality (Goals 11, 12, 13, 14, 15)
      preemerging: The project shows no connection to the team's Stakeholder Brief or Literature Review, the presentation addresses only a technical audience, and no Project Thread process artifacts (decision log, signatures, AI-use disclosures) are present
      beginning: The stakeholder is mentioned but the proposal does not actually build on the Brief and Literature Review, or the Demo Day presentation lacks a non-technical segment or a disseminable artifact, or process artifacts are spotty across milestones
      progressing: The proposal integrates the Stakeholder Brief and Literature Review and Demo Day includes both technical and stakeholder-facing segments with a disseminable artifact, with minor gaps such as a thin multidisciplinary reflection, an incomplete GANTT-style timeline, or one milestone missing its AI-use disclosure
      proficient: The proposal integrates the Stakeholder Brief and Literature Review, naming the problem in the stakeholder's terms and the gap the system addresses (Goals 11, 12); team process is visible throughout — decision log and role rotation are current, every team document names a primary author per section, every progress report carries all members' signatures, and an AI-use disclosure accompanies each milestone (Goal 13); Demo Day includes a live technical demo, a non-technical stakeholder-facing segment in plain language, and a disseminable artifact (poster, one-pager, or public page) that presents the stakeholder context and a multidisciplinary reflection on how disciplines beyond CS shaped the design (Goal 14); the individual reflection uses the Open Questions to describe specific new understandings and growth (Goal 15); milestone work shows approach, professionalism/process, and product, and the grade record supports combining team output with individual contribution and individual understanding
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

<!-- Project Thread integration: original rubric weights before the Stakeholder Grounding / Multi-Audience Communication / Process Quality row was added were 30 / 25 / 20 / 13 / 12. -->

> **The Project Thread:** This track is the final stage of the semester-long [Project Thread](/Projects/PBLThread). Your proposal must build on your team's [Stakeholder Brief](/Assignments/StakeholderBrief) and [Literature Review](/Assignments/LitReview), your team operates under its signed charter and the [Team Playbook](/Projects/PBLThread), and Demo Day (wk15.0) addresses both technical and non-technical audiences. See the Thread hub for the semester map and assessment philosophy.

## Project Overview

Your team will design, build, evaluate, and present a **custom agent team**: a system of cooperating, specialized agents that accomplishes a real goal-oriented task end to end on your local AI stack. This is the synthesis of the entire course. The agent loop, prompting, retrieval, memory, tools, orchestration, critique, debate, judging, explainability, and governance all have a place here — and your report must show that each architectural choice was a *decision*, not a default. At the end of the project, you will have a running, published, evaluated system; a governance document you can defend; and a class presentation that includes an honest failure disclosure. The project is worth 100 points and constitutes your final exam.

Choose a task that matters to someone: a club operations assistant, a research literature triage system, a campus event concierge, a study-group coach, a document quality pipeline. The task must require at least three meaningfully distinct agent roles, at least one retrieval or tool capability, and at least one evaluation or critique stage. Tasks touching sensitive data require instructor approval and must run fully locally with de-identification; your governance document must say so explicitly.

Teams are your standing POGIL teams of three or four. Project roles (**Coordinator**, **Builder**, **Evaluator**, **Scribe**) rotate at every sprint boundary so that every member holds every role at least once; your report's contribution statements must document the rotation.

---

## Example Project: Study Group Coach

To calibrate the expected level of ambition, here is a fully worked example at the proficient level.

**Task:** A team of three agents helps a student prepare for an exam. The student provides a set of course notes (plain-text files). The system produces a 10-question practice quiz, evaluates the student's answers, and identifies the two topics where the student performed worst.

**Agents:**
1. **Quiz Generator Agent** (temperature 0.7): Given a chunk of course notes, generates three factual questions and their correct answers in JSON. System prompt establishes it as an exam-question author specializing in Socratic factual recall; refuses to generate questions about topics not present in the provided notes.
2. **Answer Evaluator Agent** (temperature 0.1): Given a question, the correct answer, and the student's answer, outputs a JSON object with `correct: true/false` and a one-sentence explanation. System prompt establishes it as a strict but fair grader; refuses to award partial credit.
3. **Topic Summarizer Agent** (temperature 0.3): Given the evaluation results across all 10 questions, identifies the two most-missed topic areas and produces a 2-sentence study recommendation for each.

**Topology:** Pipeline. Notes → Quiz Generator → (questions presented to student) → Answer Evaluator → Topic Summarizer → output.

**Monolith baseline:** A single agent that takes the same notes and the student's answers and produces a study recommendation in one prompt. The evaluation compares topic identification accuracy and recommendation specificity on a 20-question fixed test set.

**Pre-mortem example risks:**
- Quiz Generator invents a question about a topic not in the notes (detection: string-match question keywords against note index; mitigation: add a post-generation checker)
- Answer Evaluator marks a correct paraphrase as wrong (detection: human spot-check 10% of evaluations; mitigation: increase temperature slightly and add "accept paraphrases" to system prompt)

This project is achievable in 3 sprints. It uses only local models, requires no external APIs, and produces measurable outcomes.

---

## Getting Started: First 5 Steps

Take these steps in your first team meeting after the project is announced:

1. **Agree on the task in one sentence.** If the team cannot write one sentence that everyone accepts, the task is not well-defined. Write it down and put it in the proposal.
2. **Name three agents.** Before doing anything else, ask: what are the three most distinct jobs this system needs to do? Write them on paper or a whiteboard. If two agents sound the same, collapse them; if one agent sounds like it does two things, split it.
3. **Write the monolith prompt.** Before building the multi-agent system, write the single-agent version in 5 minutes. Run it. Save the output. This is your baseline. The multi-agent system needs to beat it.
4. **Define your 10-task evaluation set.** Write 10 representative inputs for your system on day one. These do not change after you start building. This is your protection against overfitting your system to the cases you happened to test.
5. **Set up the repository.** Create a GitHub repo, add a `README.md`, a `config.json` with placeholder values, and a `.github/workflows/ci.yml` with a placeholder test step. This takes 20 minutes and prevents the "we have to set up the repo" crisis in Week 14.

---

## Common Pitfalls

These are mistakes teams have made in previous semesters. Learn from them.

1. **Building the monolith baseline too late.** Teams that build the baseline in the last week cannot change their system if it loses. Build the baseline in the first sprint, run the evaluation, and use the results to guide your design.
2. **Designing agents with overlapping roles.** If your Summarizer Agent and your Synthesis Agent both "summarize," you have one agent doing the same job twice. Distinct roles means distinct *capabilities* — retrieval vs. generation, evaluation vs. execution, formatting vs. deciding.
3. **Writing the governance document as an afterthought.** The governance document is graded on whether it matches the deployed behavior. If you write it after the system is done, it will describe what you intended, not what you built. Write it alongside the system, updating it at each sprint boundary.
4. **Treating CI as optional polish.** The rubric requires CI to pass on the submission SHA. Teams that add CI in the last sprint often discover their tests were never actually running. Set up CI in the first week, even with placeholder tests, and add real tests as you build.
5. **Presenting only the happy path.** The rubric specifically requires a "rehearsed failure disclosure" in the presentation. Practice showing a case where the system fails or behaves unexpectedly. Judges and employers are more impressed by honest failure analysis than by demos that never break.

---

## Stage 1: Proposal (due week 12, first meeting)

A two-to-three page proposal containing all of the following. Incomplete proposals are returned ungraded.

**Proposal Checklist:**

By the end of Stage 1, you will have submitted:
- A 1-paragraph problem statement naming the task, the user, and the success criterion
- An **agent design table** with one row per agent (role, system prompt summary, inputs, outputs, temperature, tools, and the isolated evaluation you will run on it)
- A topology statement: which pattern (pipeline, router, planner, blackboard, or hybrid) and a 3-sentence defense of why
- A memory and context plan: what each agent carries, what is summarized, what is retrieved, and what is discarded between turns
- A **pre-mortem table** with at least 5 predicted risks: your specification gap, irreversible action, global invariant, and two more; each with the deterministic checker or gate that owns it
- An evaluation plan: your 10-task task set sketch, the metrics you will use (precision, recall, latency, parse success rate, or human rating), the protocol, and a description of the **monolith baseline**
- A sprint plan mapping the remaining weeks, with the role rotation schedule showing who holds which role in which sprint
- A **stakeholder grounding section** integrating your [Stakeholder Brief](/Assignments/StakeholderBrief) and [Literature Review](/Assignments/LitReview): the problem in the stakeholder's terms, the gap your review identified, how this system addresses it, and anything that has changed since (Goals 11, 12)
- An **implementation-and-assessment sketch**: who holds which project role in which sprint, how the system will be assessed at each sprint boundary, and a shared GANTT-style timeline mapping tasks to weeks with named owners (Goal 13)

---

## Stage 2: Sprints and Studio (weeks 12 through 15)

Build in sprints aligned with in-class studio days. Each sprint produces three things: a **runnable increment** (the system runs on the evaluation set), an **updated evaluation table** (a number, not an adjective — "0.72 precision" not "it's getting better"), and **Scribe notes** from the sprint retrospective.

The week 15 **gallery walk** is mandatory and graded. Host honestly: demonstrate the system including at least one known failure. Walk generously: for every team you visit, fill out a Strength / Question / Risk card. Triage all feedback you receive into three buckets: fix before submission, disclose in the report, or defer to future work. Your triage decisions go in the artifacts folder.

**Sprint milestone checkpoints:**

| Sprint | By the end of this sprint, you have... |
|---|---|
| Sprint 1 (week 12) | Monolith baseline running, evaluation task set finalized (no changes after this), agent design table drafted, repo set up with CI placeholder |
| Sprint 2 (week 13) | All agents implemented and individually testable, at least 5 evaluation tasks run on the multi-agent system, governance document first draft committed |
| Sprint 3 (week 14) | Full evaluation complete with baseline comparison, at least 3 failure modes documented with transcripts, gallery walk preparation done |
| Sprint 4 (week 15) | Gallery walk complete, feedback triaged, submission packaging done, CI green on submission SHA |

---

## Stage 3: Governance Discussion (weeks 13 through 15, scheduled per team)

Your team leads a **10-minute class discussion** on the responsible use of your system, grounded in your governance document and your own measurements. This is a discussion you facilitate, not a presentation you deliver. Come with two genuine questions for the class — questions you actually do not know the answer to.

Required elements:
- Ground every claim in your own system's data: "We measured X and found Y" beats "AI systems in general tend to..."
- Identify at least one harm your system could cause and what you gated, measured, or disclosed in response
- Leave at least 4 minutes for class questions and discussion

---

## Stage 4: Submission and Presentation (final class meeting and exam slot)

### Deliverables

**1. The system:** A repository that runs from a fresh start following the README in under 3 minutes. Requirements:
- Configuration externalized to `config.json` (no hard-coded model names, paths, or seeds)
- Model versions and random seeds pinned in configuration
- Exceptions handled with located messages and tracebacks (no silent failures)
- A test suite with at least one end-to-end test
- A GitHub Actions CI workflow that runs the suite on every push
- A publish step (triggered by the submission tag `submission`) that pushes the container image or package to GHCR, Docker Hub, or npm
- Repository organized so a stranger can navigate it in under 5 minutes

**2. The report** (approximately 6 to 8 pages):
- Design rationale tied to course patterns (name the pattern, explain the choice)
- Evaluation results: the monolith baseline comparison table, the failure analysis with transcripts, and any re-measurement after mitigation
- Explainability design: how the system surfaces evidence to the user, and what the confirmation gate shows
- Limitations: your "disclose" bucket from the gallery walk triage, verbatim
- Governance summary: a 1-paragraph summary of the governance document referencing the committed `GOVERNANCE.md`
- Individual contribution statements covering the role rotation (who held which role in which sprint and what they produced)

**3. The presentation** (12 minutes plus questions):
- Live demonstration of the happy path (must show a real system running, not screenshots)
- A rehearsed failure disclosure: show a case where the system fails and explain why
- The evaluation table (baseline vs. multi-agent, side by side)
- The 90-second explainability story (what does a user see when the system makes a decision?)
- A **non-technical, stakeholder-facing segment** (2-3 minutes, plain language, no unexplained jargon): the stakeholder context — who this is for and the problem in their terms — what the system does for them, what it must not be used for, and a brief **multidisciplinary reflection** on how disciplines beyond CS shaped the design (Goal 14)
- Every teammate speaks for a substantive portion of the presentation

**5. The disseminable artifact:** a poster, one-pager, or public web page, suitable for handing to your stakeholder or displaying publicly, that presents the project for a non-technical audience: the stakeholder context, what the system does, its limits, and where to learn more (Goal 14). Bring it to Demo Day and include it in the artifacts folder.

**4. The artifacts folder:**
- Agent design table (final version)
- Pre-mortem (final version, with binding governance clauses noted)
- Sprint notes (all sprints)
- Gallery walk cards received and your triage (fix / disclose / future work)
- Release readiness checklist signed by the Evaluator role, confirming: CI passes on the submission SHA, the artifact is live at its published URL, and the README was tested by a stranger

---

## Reflection Prompts

Answer individually in your contribution statement:

- Which course principle did your team most rely on, and where did you knowingly violate one, with what consequence?
- What did the monolith baseline teach you that you did not expect?
- Using the four Open Questions (*What should matter to me? How should we live together? How can we understand the world? What will I do?*), describe one specific new understanding and one area of growth or skill development from the Project Thread — from formation survey to Demo Day (Goal 15).
- Do you certify that your contribution statement accurately represents your own work? Please identify any and all portions of the project that were not originally created by your team.
- Approximately how many hours did the project take you personally (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
