---
layout: assignment
permalink: /Projects/FinalProject
title: "CS357: Foundations of Artificial Intelligence - Final Project"

info:
  coursenum: CS357
  purpose: "To synthesize the entire course — and the semester-long Project Thread — into one substantial, community-grounded final project: a system you build, an audit you evidence, or an artifact you publish, carried from proposal through sprints to a multi-audience Demo Day, with the process graded alongside the product."
  tilt:
    task: "With your standing team, choose one of three directions — build a custom agent team, perform a responsible AI audit, or build and publish an open-source agent — then propose it, build it in sprints with a community partner in the loop, and present it at Demo Day with a partner-facing artifact."
    criteria: "Assessed on three families — Approach (sound methods and justified design decisions), Process and Professionalism (meeting discipline, communication, project management, check-ins, charter adherence), and Product (the working system, audit, or publication, the Demo Day presentation, and the partner-facing artifact); see the rubric below for the full breakdown."
  points: 100
  goals:
    - To carry one substantial project from proposal through sprints to Demo Day, choosing the direction (build, audit, or publish) that best serves the team's stakeholder problem
    - To justify every major methodological and design decision — architectural choices, framework selection, or scoping — by naming the course pattern, principle, or evidence that motivated it
    - To produce direction-appropriate evidence of rigor - a baseline-compared evaluation with documented failure modes (Direction A), a systematic framework application with mechanistic failure modes and adoptable governance (Direction B), or a verified ecosystem gap with property tests, publication, and community engagement — or a verified issue in an existing project carried to a submitted, reviewed contribution (Direction C)
    - To practice visible, professional team process — meeting agendas and notes, a decision log, role rotation, all-member signatures, intra-team check-ins, and charter adherence — throughout the project
    - To engage a community partner: grounding the proposal in stakeholder needs, incorporating a partner feedback pass during the sprint window, and delivering a partner-facing artifact at Demo Day
    - To communicate the result to a multi-audience of technical peers and community stakeholders, and to disclose honestly how and why AI tools were used at the proposal and at the final submission
    - To ground the project in the team's Stakeholder Brief and Literature Review and use the Open Questions to assess growth (Goals 11, 12, 13, 14, 15)
  rubric:
    - weight: 30
      description: Approach — sound methods and justified design decisions
      preemerging: The work shows no evidence of a deliberate approach — decisions are unexplained defaults, the direction's required rigor (baseline evaluation, framework application, or gap verification) is absent, and the project does not build on the Stakeholder Brief or Literature Review
      beginning: An approach is described but is generic or unjustified — design decisions are asserted rather than argued, the direction's evidence of rigor is attempted but incomplete (an evaluation without a baseline, a framework applied superficially, a gap asserted without evidence), or the connection to the stakeholder problem is nominal
      progressing: The approach is deliberate and mostly sound — major design decisions are justified with reference to course patterns or evidence, the direction's rigor requirement is substantially met (baseline comparison with metrics, systematic framework application with citations, or verified gap with linked evidence), and the proposal builds on the Stakeholder Brief and Literature Review, with minor gaps in how alternatives were considered or in the failure analysis
      proficient: The approach is deliberate, documented, and defensible — every major decision names the alternative that was rejected and the course pattern, principle, or evidence that motivated the choice; the direction's rigor requirement is fully met (Direction A - a fixed evaluation set compared against a monolith baseline with at least three failure modes documented from transcripts and at least one mitigation re-measured; Direction B - every major framework step yields a specific, cited finding with at least three mechanistic failure modes distinguishing materialized from foreseeable risks; Direction C - an independently verifiable ecosystem gap with named alternatives, a one-sentence minimum viable scope, and at least three non-trivially specified property tests); and the work is explicitly grounded in the Stakeholder Brief, Literature Review, and the partner's stated needs (Goals 11, 12)
    - weight: 30
      description: Process and Professionalism — meetings, communication, project management, check-ins, charter adherence
      preemerging: There is no evidence of team process — no meeting agendas or notes, no decision log, no role rotation, missing check-ins and signatures, and no AI-use disclosure on the proposal or final submission
      beginning: Some process artifacts exist but are spotty — meeting notes or the decision log have gaps, one or more intra-team check-ins are missing, the GANTT-style timeline is absent or stale, signatures are missing from a milestone, or an AI-use disclosure is absent from the proposal or the final submission
      progressing: The Team Playbook is followed with minor lapses — meeting agendas and notes, the decision log, role rotation, the project timeline, all three intra-team check-ins, all-member signatures, and AI-use disclosures on the proposal and final submission are present, but one element is thin, late, or inconsistently maintained (Goal 13)
      proficient: Team process is visible and current throughout — every meeting has a posted agenda and notes with owners and dates; the decision log records alternatives and rationale; project management is real (a maintained GANTT-style timeline with named owners, sprint boundaries honored, runnable increments at each sprint); all three intra-team check-ins are submitted on time; the team demonstrably operates under its signed charter, including its conflict protocol; roles rotate per sprint and every student is primary author of at least one section or component of every team deliverable (editable by teammates); each team document's version or commit history shows a real drafting trajectory rather than a single late paste; every milestone carries all members' signatures and an AI-use disclosure stating specifically what was AI-assisted, with what tool, why, and how it was verified (Goal 13)
    - weight: 40
      description: Product — the working system, audit, or publication; the Demo Day presentation; and the partner-facing artifact
      preemerging: The direction's core artifact is missing or does not function — the system does not run, the audit lacks findings and governance, or nothing was published; the Demo Day presentation is missing or covers only a happy path with no disclosed limitation; no partner-facing artifact exists
      beginning: The core artifact partially meets its direction's requirements but would not be usable by its intended audience without significant rework — the system runs but is unreproducible or unevaluated, the audit's governance recommendations lack owners, thresholds, or timelines, or the published artifact lacks working documentation, tests, or a registry presence; the presentation serves only a technical audience or omits the failure disclosure; the partner-facing artifact is missing or unusable by the partner
      progressing: The core artifact meets its direction's requirements — a running, documented, evaluated system with committed governance (A); a complete risk analysis and adoptable governance document (B); or a published, installable, tested, documented artifact with a community exchange (C) — and Demo Day includes both a technical segment and a stakeholder-facing segment with a partner-facing artifact, with minor gaps in polish, accessibility, or the honesty of the limitations discussion, and a public repository or write-up exists but has gaps in recruiter-legibility (a README a stranger could not follow, or no contribution attribution) (Goal 14)
      proficient: "The core artifact fully meets its direction's requirements and is honest about its limits. — Direction A: the system runs from a fresh start following the README; configuration and seeds are externalized and pinned; CI passes on the submission SHA; evidence is surfaced to the user with a confirmation gate on consequential actions; and the committed GOVERNANCE.md matches deployed behavior. — Direction B: the artifact package (risk analysis with at least 8 citations; governance document with monitoring plan, incident response, communication plan, and appeal process) could be handed to a regulator without modification. — Direction C: the artifact is live and installable from a public registry with green CI, a stranger-tested quickstart, CONTRIBUTING.md and GOVERNANCE.md, and a documented substantive community exchange. — All directions: the Demo Day presentation serves the multi-audience — a live technical segment with a rehearsed failure or limitation disclosure and a plain-language stakeholder segment — with every teammate speaking substantively and every teammate able to present any part; the partner-facing artifact (one-page brief, demo video, or deployed tool) is something the community partner can actually use, presented at Demo Day and included in the submission; and the project leaves a public, recruiter-legible trace — a public repository (Directions A and C) or a public write-up or portfolio page (Direction B) whose README or summary answers what it is, why it matters, and how to run or read it in thirty seconds, names each member's contribution, and is suitable for linking from a resume (Goal 14)"
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
  - responsible-ai
  - open-source
  - community

---

> **The Project Thread:** The Final Project is the final stage of the semester-long [Project Thread]({{ site.baseurl }}/Projects/PBLThread). Your proposal must build on your team's [Stakeholder Brief]({{ site.baseurl }}/Assignments/StakeholderBrief) and [Literature Review]({{ site.baseurl }}/Assignments/LitReview), your team operates under its signed charter and the [Team Playbook]({{ site.baseurl }}/Projects/PBLThread), and Demo Day addresses both technical and non-technical audiences. See the Thread hub for the semester map and assessment philosophy.

## Project Overview

The Final Project is **one required project with three directions**. Every team completes the same arc — proposal, sprints with check-ins, a gallery walk, and Demo Day — and every team is graded on the same three rubric families. What differs is the direction your team chooses for its intervention:

- **Direction A: Custom Agent Team** — design, build, and evaluate a system of at least three cooperating, specialized agents that accomplishes a real goal-oriented task end to end on your local stack, benchmarked against a monolithic baseline and governed by a document you can defend.
- **Direction B: Responsible AI Audit** — perform a structured, evidenced responsible-AI audit of a specific deployed system: a risk analysis with mechanistic failure modes, a governance document a real organization could adopt, and a presentation a real board could act on.
- **Direction C: Build and Publish an Open-Source Agent** — identify and verify a real gap in the agent tooling ecosystem, then build, test, document, and publish an open-source agent to a public registry, engaging a real community with its governance and limitations disclosed — or, as a variant, contribute reviewed pull requests to an existing open-source agent project (see the variant under Direction C below).

These are directions within the one project, not separate assignments: your team chooses the direction that best serves the stakeholder problem you have carried since the [Stakeholder Brief]({{ site.baseurl }}/Assignments/StakeholderBrief). All three directions are completed with your standing Project Thread team, operating under its signed charter, with project roles (**Coordinator**, **Builder**, **Evaluator**, **Scribe**) rotating at every sprint boundary.

**The project is the vehicle, not the destination.** The graded emphasis falls on your *process* as much as your *product*: how you decided, how you worked together, how you engaged your community partner, and how honestly you disclosed what worked and what did not. A team that meets on schedule, logs its decisions, checks in candidly, and reports a limitation honestly will outscore a team with a slicker artifact and no visible process.

**There is no final exam in this course.** Demo Day presentations — plus the registrar's final-exam slot if needed for presentation overflow — are the terminal event of the semester.

---

## The Unified Timeline

The Final Project's milestones run in the sequence below; see the course schedule in the syllabus for the dates. **No work is accepted after the last class meeting.**

| Sequence | Milestone | Points |
|------|-----------|--------|
| Hand-out | **Project handed out.** Teams read all three directions and begin converging on one. | - |
| Before the proposal | **Intra-team check-in 2** (private, to the instructor) — this check-in precedes and informs your proposal. | - |
| Proposal deadline | **Proposal due**, with direction declared, stakeholder grounding, and AI-use disclosure. | **25 / 100** |
| Sprint window | **Sprints.** Rotating roles, a runnable increment (or evidenced stage checkpoint) at every sprint boundary, and a **partner feedback pass** during the sprint/gallery-walk window (the final sprint). | - |
| Final sprint | **Gallery walk + peer review (SQR cards)**, and **intra-team check-in 3**. | - |
| Last class | **Demo Day + final submission**, including the partner-facing artifact and the final AI-use disclosure. | **75 / 100** |

The registrar's final-exam slot is reserved for Demo Day overflow only — if all teams present at the last class meeting, it is not used. Either way, the last class meeting is the submission deadline: no work is accepted after it.

---

## Community Partner Engagement

This project is deliberately community-grounded: **every team connects its project to a community stakeholder**. Partners are identified by the instructor and the roster is shared in class (it is not published on the website). Three touchpoints are required:

1. **Proposal:** the partner's stated needs inform the proposal, building directly on your Project Thread [Stakeholder Brief]({{ site.baseurl }}/Assignments/StakeholderBrief). Name the problem in the partner's terms and state how the direction you chose serves it.
2. **Partner feedback pass:** during the sprint/gallery-walk window, share your in-progress work with your partner (a demo, a findings summary, or a draft artifact) and document their feedback and how you triaged it — incorporate, disclose, or defer.
3. **Partner-facing artifact (Demo Day):** deliver an artifact an external stakeholder can actually use — a one-page brief, a demo video, or a deployed tool — and present it at Demo Day to a **multi-audience** of technical peers and community stakeholders.

---

## How the Grade Works

Your final-project grade combines **team output**, **individual contribution**, and **individual understanding**:

- **Team output** is the team's score on the three rubric families below, applied to the proposal (25 points) and the final submission and Demo Day (75 points).
- **Individual contribution**: every student must be **primary author of at least one section or component** of every team deliverable — named in the document, and editable by teammates. Your primary-author sections, check-in record, and role-rotation history are your contribution evidence. Riding along is not a strategy, and neither is doing everything yourself.
- **Individual understanding** is assessed through the **Demo Day question-and-answer** and your **individual reflection**: can you explain and defend any part of the work, including parts you did not primarily author?

**AI-use disclosure:** both the proposal and the final submission must include a disclosure statement of **how and why AI tools were used** — what was AI-assisted, with what tool, why you chose to use it there, and how the output was verified. Disclosed, verified AI assistance is professional practice; undisclosed AI assistance is an integrity violation.

**Absence policy for Demo Day:** every team member must be able to present *any* part of the project — prepare accordingly. The grade of a member absent on Demo Day depends on the reason for the absence and on that member's documented contribution to that point.

---

## Stage 1: Proposal (25 points)

Every proposal (2-3 pages), regardless of direction, must include:

- **Direction declaration** and a one-paragraph problem statement naming the task or system, the affected users or populations, and the success criterion.
- **Stakeholder grounding** integrating your [Stakeholder Brief]({{ site.baseurl }}/Assignments/StakeholderBrief) and [Literature Review]({{ site.baseurl }}/Assignments/LitReview): the problem in the partner's terms, the gap your review identified, how this project addresses it, and what the partner's needs imply for scope (Goals 11, 12).
- **Implementation-and-assessment sketch**: who holds which role in which sprint, how progress will be assessed at each sprint boundary, and a shared GANTT-style timeline mapping tasks to the three sprints with named owners (Goal 13).
- **AI-use disclosure** for the proposal itself.
- The **direction-specific elements** listed under your direction below.

Incomplete proposals are returned ungraded; proposals whose scope is too generic, inaccessible, or infeasible in three sprints are redirected. The second intra-team check-in lands shortly before this deadline — use it to surface scope disagreements early.

---

## Stage 2: Sprints

Build in three sprints between the proposal and Demo Day, aligned with in-class studio days; see the [course schedule](/) for the boundaries. Each sprint produces: a **runnable increment or evidenced stage checkpoint** (per your direction's milestones below), an **updated evaluation or evidence table** (a number or a citation, not an adjective), and **Scribe notes** from the sprint retrospective. Roles rotate at each boundary so every member holds every role.

| Sprint | Direction A milestone | Direction B milestone | Direction C milestone |
|---|---|---|---|
| Sprint 1 (proposal submitted -> cross-team proposal critique) | Monolith baseline running; 10-task evaluation set finalized (frozen after this); agent design table drafted; repo + CI placeholder | Evidence folder with 5+ sources; framework mapping begun; first failure-mode candidates identified | Running MVP (core feature only); at least 3 tests (1 unit + 2 property); CI green on the MVP |
| Sprint 2 (proposal critique -> gallery walk; spans the Thanksgiving break) | All agents implemented and individually testable; at least 5 evaluation tasks run; GOVERNANCE.md first draft committed | Risk analysis report drafted (4-6 pages, 8+ citations, 3 mechanistic failure modes); governance document outlined | Non-trivial feature implemented; third property test added; README quickstart drafted and cold-tested by a classmate |
| Sprint 3 (gallery walk -> Demo Day) | Full evaluation with baseline comparison; 3+ failure modes documented with transcripts; one mitigation re-measured; gallery-walk prep | Governance document complete (monitoring plan, incident response, communication plan, appeal process); board presentation rehearsed | Published to a registry, tagged v1.0.0; community post made; CONTRIBUTING.md and GOVERNANCE.md complete |

**Partner feedback pass (final sprint):** during this window, put your work in front of your community partner and document the exchange (see Community Partner Engagement above).

**Gallery walk + peer review (final sprint):** mandatory and graded within the Process family. Host honestly — demonstrate your work including at least one known failure or open finding. Walk generously — fill out a **S**trength / **Q**uestion / **R**isk card for every team you visit. Triage all feedback you receive into three buckets — *fix before submission*, *disclose in the report*, or *defer to future work* — and put your triage decisions in the artifacts folder. Intra-team check-in 3 is due the same day.

---

## Stage 3: Demo Day and Final Submission (75 points)

**Demo Day logistics:** all teams present within the single class slot, splitting the time evenly, so each team's window is short and fixed, including Q&A — rehearse to time.

Every team, regardless of direction, delivers at Demo Day:

- A **live technical segment** for CS peers — a real demonstration (Direction A: the running system; Direction B: a walkthrough of the framework application and evidence for one failure mode's mechanism; Direction C: the installed, published artifact) including a **rehearsed failure or limitation disclosure**.
- A **non-technical, stakeholder-facing segment** in plain language: who this is for, the problem in their terms, what the work does for them, what it must not be used for, and a brief multidisciplinary reflection on how disciplines beyond CS shaped the work (Goal 14).
- The **partner-facing artifact**, presented to the multi-audience and included in the submission.
- A **public portfolio artifact**: the public repository (Directions A and C) or public write-up/portfolio page (Direction B) described in the Product rubric — run the [ShipIt](#shipping-your-artifact-the-shipit-checklist) self-check against it before your publish gate.
- **Every teammate speaks substantively**, and every teammate must be prepared to present any part (see the absence policy above).
- Q&A with the instructor, peers, and partners — this is where individual understanding is assessed. Demo Day is **external-facing**: alumni, industry guests, and faculty from other departments may join the audience and Q&A, as available — your grade never depends on who attends. Prepare with the [Demo Day Guide](#demo-day-external-guests-and-technical-interview-practice); the final Project Studio includes a cross-team mock-interview rehearsal, credited as class participation.

The final submission (due the same day) includes your direction's deliverables below, individual contribution statements documenting the role rotation, individual reflections, and the **final AI-use disclosure**.

---

## Direction A: Custom Agent Team

Design, build, evaluate, and present a **custom agent team**: cooperating, specialized agents accomplishing a real goal-oriented task end to end on your local AI stack. The agent loop, prompting, retrieval, memory, tools, orchestration, critique, judging, explainability, and governance all have a place here — and your report must show that each architectural choice was a *decision*, not a default. Choose a task that matters to your partner's community; it must require at least three meaningfully distinct agent roles, at least one retrieval or tool capability, and at least one evaluation or critique stage. Tasks touching sensitive data require instructor approval, must run fully locally with de-identification, and your governance document must say so explicitly.

**Direction A proposal elements** (in addition to the shared elements):
- An **agent design table**, one row per agent: role, system-prompt summary, inputs, outputs, temperature with justification, tools, and the isolated evaluation you will run on it
- A **topology statement** — pipeline, router, planner, blackboard, or hybrid — with a 3-sentence defense
- A **memory and context plan**: what each agent carries, summarizes, retrieves, and discards
- A **pre-mortem table** with at least 5 predicted risks (your specification gap, irreversible action, global invariant, and two more), each with the deterministic checker or gate that owns it
- An **evaluation plan**: the 10-task set sketch, numeric metrics (precision, recall, parse success rate, latency, or human rating), the protocol, and the **monolith baseline** description

**Direction A build requirements:**
- Build the monolith baseline *first* and evaluate against it; freeze the 10-task evaluation set at Sprint 1
- Document at least three failure modes with agent transcripts; implement and re-measure at least one mitigation with before-and-after numbers
- Surface evidence to the user following the evidence hierarchy (direct retrieval citation over generated summary), with a **human confirmation gate** on every consequential action and a demonstrated **abstention behavior** (the system declines rather than hallucinating when evidence is absent)
- Commit a **GOVERNANCE.md** that matches the deployed system's behavior — data handling, human gates, incident response — updated at each sprint boundary, not written at the end
- Lead a **10-minute class discussion** (scheduled per team during the sprint weeks) on the responsible use of your system, grounded in your own measurements, with at least 4 minutes for class questions and two genuine questions you do not know the answer to

**Direction A final deliverables:**
1. **The system:** a repository that runs from a fresh start following the README in under 3 minutes on a machine the team has not configured — configuration externalized to `config.json`, model versions and seeds pinned, exceptions handled with located messages, a test suite with at least one end-to-end test, CI on every push, and a publish step (triggered by the `submission` tag) pushing the artifact to GHCR, Docker Hub, or npm
2. **The report** (6-8 pages): design rationale tied to named course patterns; evaluation results with the baseline comparison table, failure analysis with transcripts, and re-measurement after mitigation; explainability design; limitations (your "disclose" bucket from the gallery walk, verbatim); a governance summary referencing the committed GOVERNANCE.md; and individual contribution statements documenting the role rotation
3. **The presentation** (12 minutes plus questions), meeting the shared Demo Day requirements, plus: the evaluation table (baseline vs. multi-agent, side by side) and the 90-second explainability story (what does a user see when the system makes a decision?)
4. **The artifacts folder:** final agent design table, final pre-mortem with binding governance clauses noted, all sprint notes, gallery-walk cards received with your triage, and a release-readiness checklist signed by the Evaluator confirming CI passes on the submission SHA, the artifact is live at its published URL, and the README was tested by a stranger

---

## Direction B: Responsible AI Audit

Perform a structured **responsible AI audit** of a publicly available, deployed AI system — the kind of analysis increasingly required by regulation, expected by investors, and demanded by affected communities. The deliverable is not an opinion piece: it is evidenced, structured, and written for people who will make decisions based on it. The audited system should live in the domain your community partner cares about.

The system must be **specific**: a named, deployed product with a defined purpose and identifiable affected populations — not "AI in hiring" but a named tool as deployed by a named operator. Strong candidates: a hiring screening tool, a medical imaging AI, a content moderation system, a predictive risk tool in criminal justice or benefits eligibility, or an educational AI that grades or places students. Avoid general-purpose chatbots unless scoped to a specific deployment context. You are not expected to have access to the system's internals — base the analysis on public documentation, news coverage, academic studies, and regulatory filings, and cite every claim; documented absence of information is itself a finding.

**Direction B proposal elements** (in addition to the shared elements):
- **System identification**: name, operator, what it does, where it is deployed
- **Affected populations**: who is affected and how the system's decisions reach them
- **Framework choice** — NIST AI RMF, EU AI Act, or Montreal Declaration — with a 3-sentence justification for why it fits this system better than the alternatives
- **Preliminary hypothesis**: where you expect the highest risks to lie, written before the deep analysis
- Evidence that enough public information exists (at least two independent sources from an initial search)

**Direction B build requirements (the audit):**
- **Systematic risk analysis** (4-6 pages, at least 8 citations): apply the chosen framework in full — all four NIST functions (GOVERN, MAP, MEASURE, MANAGE), an argued EU AI Act risk-tier classification with applicable obligations, or all ten Montreal Declaration principles each with an evidentiary basis. Every major framework step produces a specific, evidenced finding
- At least **three failure modes with named mechanisms** — each naming the affected group or input type, the specific erroneous output, and the mechanism — distinguishing risks that have materialized from risks that are foreseeable, and naming accountability gaps specifically (what role is absent, and what decision cannot be made without it)
- **Governance document** (3-5 pages) a real organization could adopt, passing the third-party test (could an outside auditor verify compliance from evidence?): a **monitoring plan** (each metric with data source, frequency, review threshold, and named owner), an **incident response procedure** (specific incident definition, notification order and timeframes, suspension authority), a **stakeholder communication table** (general public, affected individuals, regulators), and an **appeal process** navigable without a lawyer (initiation, reviewer, evidence, remedies, timeline). Every recommendation must trace to a specific risk finding

**Direction B final deliverables:**
1. **The artifact package**, organized so it could be handed to a regulator without modification: the approved proposal, the risk analysis report, the governance document, and the presentation materials
2. **The board presentation** (15 minutes, timing graded): the class role-plays the operator's board — intelligent, busy, skeptical, and mixed technical/non-technical. Required arc: what the system does and who uses it (2 min, plain English); who is at risk and how (3 min, including at least one concrete individual harm example); what you found, by severity (5 min, most serious first, sources on request); what you recommend, in priority order (3 min, each with estimated effort and timeline); questions (remaining). Prepare evidence-based responses to the three standard board objections: "these risks are theoretical," "the vendor tested it for fairness," and "we lack the resources"
3. **Demo Day additions:** the shared requirements above — the technically grounded evidence walkthrough serves as this direction's technical segment, and the partner-facing artifact presents the stakeholder context, the top findings by severity, and the priority recommendations
4. Individual contribution statements and reflections

---

## Direction C: Build and Publish an Open-Source Agent

Build something that outlasts the semester: a published, documented, reusable agent or agent component that real users can discover, install, and run. The deliverable is a **software artifact with a community presence** — a package on a public registry, a README a stranger can follow, a CI badge, a governance statement, and at least one authentic exchange with a real community member. The gap your artifact fills should serve the community your partner belongs to. Artifacts touching sensitive data or making outbound API calls on behalf of users require instructor approval and a governance statement addressing those risks.

> **Direction C variant: Contribute to an Existing Open-Source Project.** Instead of publishing a new artifact, your team may make substantive, reviewed contributions to an existing project in the agent ecosystem — an MCP server, the Ollama or OpenWebUI ecosystem, promptfoo, or Inspect AI are strong candidates. The same rubric applies with these equivalences: *gap verification* becomes issue selection (a triaged open issue or feature request, with linked evidence that a maintainer or real user wants it); *publication* becomes one or more submitted pull requests with tests and documentation, carried through maintainer review (a merge is ideal but not required — a substantive review exchange is, because maintainer response times are outside your control); *community engagement* is intrinsic to the PR thread and documented from it; and the CONTRIBUTING.md and GOVERNANCE.md requirements are met by following the upstream project's own documents and stating in your report what they required of you. Scope must be approved in the proposal, whose "what the artifact does / who would use it / how they would install it" elements describe the upstream feature you are adding. A contribution reviewed by the maintainers of a real project is a portfolio line few graduates have.

**Direction C proposal elements** (in addition to the shared elements):
- **What the artifact does**, in one paragraph a stranger can understand
- **Who would use it**: two to three user personas with realistic, specific use cases
- **How they would install it**: the exact command sequence from a clean machine to a working demo
- **Gap verification**: the closest existing alternative, the specific gap it does not fill, and linked evidence the gap is real (a community post, GitHub issue, or unanswered Stack Overflow question where a real person asked for this)
- **Minimum viable scope** in one sentence, plus two to three stretch goals
- **Governance sketch**: who is responsible, what the artifact must never be used for, and what risk the instructor should know about before approving

**Direction C build requirements:**
- Core functionality works on a clean machine by following the README, with at least one **non-trivial feature** fully implemented (streaming responses, token-level authentication, persistent memory across sessions, or multiple integrated tools with error recovery)
- **Unit tests** for all deterministic components with meaningful assertions, and at least **three property tests** for LLM-dependent components, each naming a clearly stated behavioral contract (e.g., "every response includes a source citation," "the output is valid JSON matching the named schema") — no trivially passing properties
- **GitHub Actions CI** running the full suite on every push, green on the submission SHA; configuration externalized with documented defaults; no credentials anywhere in the git history; model versions and seeds pinned
- **Documentation:** a README whose quickstart works in 5 commands or fewer on a clean machine (verified by a classmate cold-following it, result documented), with a configuration reference, two worked examples, the registry link, and the CI badge; a **CONTRIBUTING.md** covering bug reporting, PR submission, local test execution, and a code of conduct; a **GOVERNANCE.md** covering scope, prohibited uses with reasons, responsibility and contact, harm reporting, and known limitations that could cause harm; and a **LICENSE** (MIT, Apache 2.0, or AGPL) justified in one paragraph naming what the choice means for users
- **Publication:** installable from at least one public registry (npm, PyPI, Docker Hub, or the MCP marketplace); submission commit tagged `v1.0.0` and matching the published version
- **Community engagement:** a post in a relevant community (r/LocalLLaMA, r/MachineLearning, a relevant Discord, or Show HN); respond substantively to feedback — acknowledge its substance and incorporate it, explain why not, or file an issue — and document the exchange with a screenshot or link. If no response arrives within a week, post to a second community and document the attempt

**Direction C final deliverables:**
1. **The repository and the published package**: public GitHub repo running from a fresh start, CI green on the submission SHA, and a live registry URL where the artifact is installable
2. **The report** (3-5 pages): the gap and how it was verified; key design decisions and tradeoffs; property-test results; documentation strategy and the classmate quickstart-test result; license justification; governance rationale; the community engagement summary with evidence; and individual contribution statements
3. **The presentation** (8 minutes plus questions), meeting the shared Demo Day requirements, plus: property-test results and a 60-second governance statement addressed to the audience as potential users; the partner-facing artifact may be a well-crafted public project page presenting the stakeholder context, what the artifact does, its limits, and how to get it

---

## Reflection Prompts

Answer individually in your final submission:

- Which course principle did your team most rely on, and where did you knowingly depart from one, with what consequence?
- What did your direction's rigor requirement — the baseline, the framework, or the gap verification — teach you that you did not expect?
- What did your community partner's feedback change about the work, and what did you decide not to change, and why?
- Using the four Open Questions (*What should matter to me? How should we live together? How can we understand the world? What will I do?*), describe one specific new understanding and one area of growth or skill development from the Project Thread — from formation survey to Demo Day (Goal 15).
- Do you certify that your contribution statement accurately represents your own work? Please identify any and all portions of the project that were not originally created by your team, including any AI-assisted work and how it was verified.
- Approximately how many hours did the project take you personally (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

## Shipping Your Artifact: The ShipIt Checklist

*To experience the maker's full arc on one small, real, public artifact — carrying it from a written specification through AI-assisted building, testing, and CI to responsible publication under your own name.*

### Goals

- To carry one artifact from specification through testing and continuous integration to public publication
- To practice the AI maker discipline in your chosen track, with the agent generating and the human specifying, verifying, and owning
- To publish responsibly to a real registry or hosting platform (GHCR, Docker Hub, npm, or Cloudflare) with the human gate observed
- To document the artifact for strangers with a readme and a disclosed AI contribution statement

### Background Reading and References

- [The AI Maker Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-aimaker.md)
- [Publishing Your Work Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-publishing.md)
- [Hosting with Cloudflare Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-cloudflare.md)

This guide is not separately graded; its checklist is assessed within the Final Project rubric.

This guide — required reading for the Final Project — walks you through carrying one artifact from a written specification through building with an AI agent, testing, continuous integration, and public publication under your own name. This is the maker's full arc compressed into one real, public, small artifact. By the end, something you built will exist in the world, installable or reachable by anyone, with your name on it. The self-assessment checklist above rewards discipline, not scope: a small, finished, well-tested, well-documented artifact demonstrates more than an ambitious one that does not run. Use the checklist as a self-assessment before your project's publish gate. **Choose one track and one artifact**, and observe the standing course rule throughout: agents may prepare every step, but a human (you) runs every publish or deploy command.

---

#### What Strong Work Looks Like

Strong work has these qualities:

- **The specification preceded the artifact — with a timestamp to prove it.** The dated specification file is preserved in its original form, before any agent-generated code touches it. The self-assessment values the original spec even if it was imperfect; discovering and documenting a spec gap is part of the discipline, not a failure.
- **CI is wired to reality, not a placeholder.** The GitHub Actions workflow runs the project's actual tests (or actual accessibility/content checks for Track B), not `echo "tests pass"`. The evidence portfolio includes links or screenshots of one red run and one green run — the red run proves the CI was not trivially passing before the code worked.
- **A classmate confirmed it works cold.** The "stranger test" is documented: a classmate's GitHub username or name, what they installed or visited, and their one-line confirmation that it worked from the public record alone. This is not optional — it is what "published" means.
- **The AI contribution statement is honest and specific.** A weak statement says "I used AI to help build this." A strong statement says: "The agent generated the initial `handler.js` function and all three test files. I wrote the `config.json` schema and the README, and I rewrote the error handling in lines 44-62 of `handler.js` after the agent's version silently swallowed exceptions. I verified every test manually before pushing."

Weak work has CI that passes immediately with no red run, a readme that only an author could follow, and an AI contribution statement that could apply to any project.

---

#### Choose Your Track and Artifact

**Track A (software engineering background).** Choose one:
- A container image published to GHCR — a small useful service such as a rubric-checking API or a markdown linter for course conventions
- A scoped npm package with a working `bin` — a CLI utility you actually want to exist
- A Cloudflare Worker API — the gateway-facade pattern is a strong choice

*What this track requires:* a GitHub account, plus GHCR or Docker Hub (container option) or an npm account (package option).

Your specification instrument is a **failing test suite written before implementation**. The agent's job is to make the tests pass without modifying them.

**Track B (maker track, no programming background assumed — you will use guided DevOps tooling (GitHub Actions and Cloudflare's wrangler), following step-by-step instructions).** Choose one:
- A static site deployed to Cloudflare Pages — a project page, a resource hub, or an interactive explainer built with an agent
- A simple Cloudflare Worker built entirely through agent collaboration — a JSON API for something you care about

*What this track requires:* a GitHub account and a Cloudflare free-tier account.

Your specification instruments are an **acceptance checklist written before generation** and the five-questions instruction to your agent (what it should do, what it must not do, who will use it, what counts as working, and what the edge cases are).

Artifacts must be original, must not include course-restricted materials or anyone's personal data, and must carry a license. If your idea touches credentials, payments, or other people's private information, redesign or consult the instructor first — recognizing that boundary is part of the assignment.

---

#### Stage 1: Specify (before building)

Write and date your specification before generation begins. The timestamp is part of the discipline — commit it to the repository (or post it where your project lives) before any agent-generated code exists.

**Track A specification:**
Write your failing test suite. Tests should cover: the happy path, at least one edge case (empty input, malformed input), and at least one deliberate misuse case (input designed to trigger an error or unexpected behavior). Include a `spec.md` describing what the artifact should do in plain English — one paragraph per major feature.

**Track B specification:**
Write your acceptance checklist. Each item should be a falsifiable statement: "The page loads in under 3 seconds on a standard wifi connection," not "The page is fast." Also write: a one-paragraph persona (who uses this, on what device, under what pressure) and explicit expected behavior for at least one misuse case (what happens when someone submits an empty form, clicks an unexpected button, or uses the artifact in an unintended way).

**Both tracks:** State in your specification what "done" means — the specific condition under which you would consider this artifact ready to publish. You will compare your shipped artifact against this standard in the writeup.

---

#### Stage 2: Build and Verify

Work with your agent against the specification.

**Track A:** Instruct your agent: "Make these tests pass without modifying the test files." Keep the conversation log or session notes. When the agent generates code, read it before running it. Verify every test passes. Run your misuse case. If you modify any agent-generated code, note what you changed and why.

**Track B:** Iterate against your checklist. For each failed checklist item, file a bug report in the agent conversation in what-I-did / what-I-expected / what-happened form. When all items pass, conduct the **silent stranger test**: give a classmate the public URL and nothing else. Watch (or ask them to document) what they do, where they get confused, and whether they complete the primary task without help. Log their experience.

**Both tracks:** Document one specification gap you discovered during building — a criterion you forgot to specify, a behavior you assumed but did not state, or a constraint you discovered mid-build. Show the original spec, the gap, and how you repaired the spec (not just the artifact).

---

#### Stage 3: Continuous Integration

Add the automated check appropriate to your artifact.

**Track A:** A GitHub Actions workflow (`.github/workflows/ci.yml`) that installs dependencies, runs your test suite, and reports pass/fail on every push to `main` and every pull request.

**Track B:** A preview-deployment-plus-checklist pipeline, or an Actions-driven build check that verifies the site builds without errors and key content is present.

**Both tracks:**
- Demonstrate one **red run**: a commit that intentionally fails at least one check. Include the link or screenshot.
- Demonstrate one **green run**: the commit that makes all checks pass. Include the link or screenshot.
- Arrange the pipeline so that publication to the public registry requires CI green **plus** a deliberate human act (pushing a tag, merging to a release branch, or running a manual publish step). In your writeup, state in exactly one sentence where the human gate lives.

---

#### Stage 4: Publish

Before publishing, conduct the pre-publication audit:
- **npm:** Run `npm pack --dry-run` and review the file listing. Verify no secrets, no test fixtures, no node_modules are included.
- **Container image:** Run `docker image inspect <image>` and review the layer listing. Verify no credentials or private data are in any layer.
- **Cloudflare:** Review the deploy directory listing before `wrangler deploy`. Verify no `.env` files or private keys are staged.

Document the audit output in your evidence portfolio — this is not just a checklist item, it is evidence of the professional discipline the course requires.

Then publish:
- `npm publish --access public` (npm)
- `docker push` and set visibility to public (GHCR)
- `wrangler deploy` or `wrangler pages deploy` (Cloudflare)

**Versioning:** Start at `0.1.0`. Ship at least one subsequent patch release (`0.1.1`) so the version walk is demonstrated. Use semantic versioning: patch for bug fixes, minor for new features.

**Stranger confirmation:** A classmate must install or visit your artifact from the public record alone — no setup instructions from you, no personal help. They should use only your README. Their one-line confirmation ("I ran `npm install -g your-package` and `your-package --help` worked — [GitHub username]") goes in your evidence portfolio.

---

#### Evidence Portfolio

Assemble the following evidence — this is what you will check against the self-assessment checklist before your project's publish gate, and it is assessed within the Final Project rubric:

1. The dated specification (original form, before generation)
2. The build transcript or session log (conversation with the agent, or commit history)
3. Verification evidence for every specification criterion, including the misuse case
4. For Track B: the stranger-test log (what your classmate did, where they got confused, what you changed as a result)
5. The CI workflow file and links or screenshots of one red run and one green run
6. The pre-publication audit artifact (the dry-run output, layer listing, or deploy directory review)
7. The public URL or registry name with install instructions
8. The classmate confirmation (one line, with their name or username)
9. A README suitable for strangers (what, install, use — answerable in 30 seconds)
10. An **AI contribution statement** honestly delineating what the agent produced, what you wrote or changed, and what you verified
11. A **portfolio entry**: the repository pinned or linked from your GitHub profile or portfolio page with your 200-word project story, **plus a drafted LinkedIn-style post** (150-250 words: the problem, what you built, one concrete number, and what you learned). Submitting the draft is required; **publishing it is always optional and never graded — your professional profiles are yours.** The draft exists so that if you choose to post it, the post is already written while the evidence is fresh

Ensure reproducibility by pinning dependency versions and listing software version information (Node version, npm version, Docker version, or Wrangler version as applicable).

---

#### Your Portfolio Entry and GitHub Profile

Publication is only half of existing in the world; the other half is being findable. Once the artifact is live:

- **Pin the repository** on your GitHub profile. If you do not have a profile README, create one now — it is a ten-minute job with an outsized payoff, and this artifact is its first entry.
- **Write a project story of roughly 200 words**: the problem, what you built (and what the agent built, honestly delineated — your AI contribution statement is most of this already), and the evidence — the registry link, the CI badge, the classmate's stranger confirmation. Name what *you* did explicitly, because that is the sentence a resume bullet and an interview answer are made from.
- **Reuse the story.** The same story is your opening move with guests at Demo Day (see the [Demo Day Guide](#demo-day-external-guests-and-technical-interview-practice)) and the public, recruiter-legible trace the Final Project's Product rubric asks for. Update your resume and LinkedIn while the numbers are fresh.
- **Draft the post.** Turn the story into a **drafted LinkedIn-style post** (150-250 words: problem, what you built, one number, what you learned) and include the draft in your submission. Publishing is always optional and never graded — the draft simply means that if you want the post, it is already written at the moment the project is most impressive to describe.

---

#### Frequently Asked Questions

**Q: My CI keeps failing because of a flaky network call in my tests. What should I do?**
A: Mock the network call in tests. The specification discipline the course teaches requires tests that are deterministic. If a test depends on an external service, it should be mocked in the test suite and tested against the real service only in a separate integration test step that is clearly labeled as potentially flaky. Document the decision in your writeup.

**Q: What counts as a "deliberate misuse case"?**
A: An input or user action that is wrong, adversarial, or outside the happy path. Examples: an empty input field, an input that is 10,000 characters long, a file of the wrong type, a sequence of requests that tries to exhaust a rate limit. The requirement is that your specification named the case and your testing shows what the artifact does when it happens.

**Q: Do I really need to publish to a public registry? Can I just push to a private GitHub repo?**
A: No. The "stranger confirmation" criterion requires a classmate to install or visit from the public record alone, which means the artifact must be publicly accessible. A private repository does not satisfy this requirement.

**Q: Can my classmate "confirm it works" by email instead of in the evidence portfolio?**
A: Include the confirmation in your evidence portfolio, not just in email. Quote their exact words and identify them by name or GitHub username. The confirmation should describe what they did, not just say "it worked."

**Q: My Track B artifact is a static site. Do I still need to demonstrate CI?**
A: Yes. Even a static site can have automated checks: a build step that verifies the HTML is valid, a link checker, a content check that confirms key pages exist. The CI requirement applies to both tracks. Cloudflare Pages has built-in GitHub Actions integration that makes this straightforward.

---

#### Reflection Prompts

Answer these as part of your self-assessment before your project's publish gate:

- Where in this project did the agent's output most need you, and what would have shipped if you had not been paying attention there?
- Publication is effectively irreversible. Describe the moment you ran the publish command: what had to be true for you to feel entitled to run it, and is that standard now portable to bigger things?
- If collaboration with a buddy was permitted, did you work with a buddy on this artifact? If so, who? If not, do you certify that this work represents your own original work? Please identify any and all portions of your work that were not originally written by you.
- Approximately how many hours it took you to work through this guide (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

### Self-Check

| Criterion | Pre-Emerging | Beginning | Progressing | Proficient |
|---|---|---|---|---|
| Self-Check: Specification and Verification Discipline | I let the agent generate code before I wrote any specification, and I have no systematic verification — I should revisit Stage 1 before applying this guide to my Final Project | I have a specification, but it is vague and my verification covers only the happy path | I wrote a concrete specification (failing tests in Track A; an acceptance checklist with a stranger test in Track B) before generation began, and I can point to verification evidence for most criteria | My specification preceded generation and is preserved in its original form, every criterion has verification evidence, at least one deliberate misuse case is covered, and I documented one specification gap I discovered mid-project along with how I repaired it |
| Self-Check: Continuous Integration | I have no automated checking — my project cannot pass the Final Project's publish gate yet | I have a CI workflow, but it does not run my project's real checks | My CI runs the real checks on every push, and I can show one demonstrated red run and one demonstrated green run | My CI runs the real checks on every push with demonstrated red and green runs, publication is gated on green plus a deliberate human act (a tag or merge) that I perform myself, and I can state in one sentence exactly where the human gate lives in my pipeline |
| Self-Check: Publication Quality | I have not published anything, or my publication is broken for strangers | My artifact is published, but a stranger cannot use it from the public record alone | My artifact is published, installable or reachable by a stranger, with versioning and a readme, though a minor gap remains such as a missing license or visibility friction | My artifact is published with semantic versioning, a license, and a readme answering what, install, and use in thirty seconds; I documented a pre-publication audit (dry run output or layer listing reviewed); a classmate verified a stranger installation or visit; and the artifact is pinned or linked from my GitHub profile or personal portfolio page with a short project story |
| Self-Check: Writeup, AI Disclosure, and Evidence Portfolio | My evidence portfolio is incomplete | My evidence portfolio exists, but the AI contribution statement or human-centric design evidence is missing | My evidence portfolio is complete with an AI contribution statement and design evidence, and I gave at least superficial responses to the reflection prompts | My evidence portfolio is complete, my AI contribution statement honestly delineates agent work from my own work, my human-centric design evidence covers the persona and at least one failure path, and I answered the reflection prompts thoughtfully |


---

## Demo Day: External Guests and Technical Interview Practice

*To prepare you to present your project to people beyond the course — your community partner, invited alumni and industry guests, and eventually interviewers — by practicing the plain-language pitch, the limitation disclosure, and the interview-style deep dive on a system you actually built.*

### Goals

- To open your project for a non-specialist in ninety seconds — the stakeholder problem, what the system does about it, and what working means — without jargon
- To practice the interview form on your own work - explaining your agent architecture, defending a topology or scoping decision, and telling a real failure story with its mitigation
- To handle questions honestly, including redirecting a question you cannot answer and disclosing a known limitation without being asked
- To connect the project to what comes next - a portfolio story, a resume conversation, and venues for presenting student work beyond the course

### Background Reading and References

- [Project Studio Protocol](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-projectstudio.md)
- [Final Project](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/FinalProject)
- [ShipIt Guide: Build, Test, CI, and Publish One Artifact](#shipping-your-artifact-the-shipit-checklist)

This guide is not separately graded; the presentation is assessed within the Final Project's **Product** dimension, and the mock-interview rehearsal is credited as **class participation**.

Demo Day is already a multi-audience event: your community partner's world and your CS peers' world meet in one room. This guide widens the circle one step further — alumni, industry guests, and faculty from other departments may join as audience members and Q&A panelists, invited **as available**; your grade never depends on who attends — and prepares you for the skill all of those audiences share with a technical interviewer: explain a system you built, in plain language first and full depth on request, defend your decisions, and be honest about what does not work. Nothing here is extra work — it is rehearsal for work you already owe.

---

#### What Strong Work Looks Like

- **The opener lands with someone who has never heard of an agent loop.** "Our partner's food pantry answers the same fifty questions by phone every week. We built a system that answers them from the pantry's own documents, says *I don't know* when the documents don't say, and never sends anything without a human approving it. I built the retrieval piece that finds the right document." Ninety seconds, no jargon, ends with what *working* means — and what the system refuses to do.
- **Depth is available on demand, not imposed up front.** When a guest asks "how does it actually work?", the answer walks one request through the system — perceive, plan, act; what each agent sees, decides, and hands off — at whatever level the asker's follow-ups invite.
- **The limitation is volunteered, not extracted.** Strong presenters disclose a rehearsed failure mode with its transcript evidence — or, for audit teams, a finding with its citations — before anyone asks. It reads as command of the work, because it is.
- **Questions come back.** The best conversations at Demo Day are two-way: ask a guest what they build, how their team uses (or refuses) AI tools, what they wish new graduates knew.

---

#### The One-Page Brief: Talking to Guests

Have these five moves rehearsed before Demo Day:

1. **The ninety-second opener.** The stakeholder problem in the partner's terms, what your project does about it, who it is for, and one sentence on what you personally built. Write it, say it aloud, cut every term a non-CS friend would stumble on. (Your stakeholder-facing Demo Day segment is the long form of this; the opener is the version you give a guest standing in front of your table.)
2. **The three-sentence architecture.** The system in plain words: *a request comes in; specialist agents each handle their piece — one retrieves evidence, one drafts, one critiques; a human approves anything consequential before it happens.* Then one sentence on where your part lives. Audit teams: the framework in plain words — *we mapped who the system touches, measured where it fails, and wrote the rules a real organization could adopt.*
3. **The limitation.** One known failure mode or finding, stated plainly, with its evidence and why you triaged it as disclose-rather-than-fix. Practice saying it without apologizing.
4. **The redirect.** For questions you cannot answer: "I don't know — my teammate built that part, let me hand you to them," or "I don't know, but here's how I'd find out." Both are strong answers. Bluffing is the only weak one — and in this course, saying *I don't know* when the evidence is absent is literally what we graded your systems on.
5. **The question back.** Prepare two genuine questions to ask a guest — about their work, how AI is changing it, or their path. Demo Day is a networking event wearing a final-exam costume; treat the conversation as two-way.

---

#### The Mock Technical Interview (Week 14 Project Studio)

During the "Final Integration and Demo Rehearsal" studio, you will pair **across teams** for interview rounds, credited as class participation:

**Format.** Ten minutes per round, then swap roles. The interviewer asks from the question bank below (or invents better ones); the interviewee answers **without slides** — a whiteboard or paper is allowed, your repository is not. Close each round with an SQR-style feedback card: one **Strength**, one **Question** the interviewee should be ready for at Demo Day.

**Question bank** (interviewers: pick three or four, follow the answers, dig where they wobble):

- Walk me through your agent architecture — what happens to one request, from arrival to answer, naming each agent and what it hands to the next.
- Why this topology over a monolith? What did the baseline comparison actually show, and what would make you go back to the monolith?
- Tell me about a failure you found in your own system — how you caught it, what the transcript showed, and what changed after your mitigation.
- Where does your system say "I don't know," and how do you know it actually does?
- What would you do with two more weeks? Two more months?
- (For audit teams) Which of your findings would the operator dispute most vigorously, and what is your evidence when they do?
- (For open-source teams) A stranger files an issue saying your quickstart fails on their machine. Walk me through what you do.

**Why cross-team pairs:** explaining your system to someone who has never seen it is the whole game — your own teammates know too much to be useful practice, and interviewing *them* about their project teaches you what good interviewer questions feel like from the inside.

---

#### Taking It Further

The project does not have to end at Demo Day:

- **[CCSC-Eastern](https://ccscne.org/)** and similar regional conferences run **student poster sessions** — an evaluated multi-agent system, a regulator-ready audit, or a published open-source tool is exactly the kind of work they exist to showcase. Talk to the instructor about submitting; your proposal and report are most of the abstract.
- **Campus research and creative-work showcases** welcome course projects of this scope; presenting there is a low-stakes rehearsal for any external venue.
- **Your profile.** The [ShipIt guide](#shipping-your-artifact-the-shipit-checklist)'s portfolio entry — the pinned repository or public write-up and the 200-word project story — is the durable version of everything you rehearsed here. Update your resume and LinkedIn while the numbers (evaluation results, test counts, the registry link) are fresh.

---

#### Frequently Asked Questions

**Q: Will there definitely be external guests at Demo Day?**
A: Guests are invited as available — some years the room is full, some years it is classmates, partners, and faculty. Prepare the same either way: the Product rubric's multi-audience expectations do not change, and the mock-interview rehearsal happens regardless.

**Q: Does talking to guests affect my grade?**
A: The presentation is graded by the Final Project's existing rubric; guest attendance and guest reactions are never grading conditions. The mock-interview rehearsal is credited as ordinary class participation for the studio session it happens in.

**Q: I get nervous in interview settings. Can I opt out of the mock interview?**
A: Talk to the instructor beforehand — the format can be adjusted (a smaller room, a written walk-through, extra prep time). The rehearsal exists precisely because the tenth time explaining your architecture is calmer than the first; we want you to spend nervous repetitions here, where they are cheap.

**Q: Our project is an audit with no running system. What do we demo to a guest?**
A: The evidence walkthrough is your demo: one failure mode, its mechanism, and the trail of citations behind it — shown, not asserted. Guests with industry experience often find the audit conversations the most engaging in the room.

---

#### Reflection Prompts

Answer individually after the mock-interview rehearsal, connecting to the course's Open Questions — especially *What will I do?* (Goal 15):

- Which question made you realize you understood something less well than you thought, and what did you do about it before Demo Day?
- What did you learn from being the *interviewer* that you could not have learned as the interviewee?
- You practiced telling the story of work you built with AI assistance, honestly disclosed. How does that conversation change what you will claim — and disclose — about your work after this course?
- Approximately how many hours did you spend preparing with this guide (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

### Self-Check

| Criterion | Pre-Emerging | Beginning | Progressing | Proficient |
|---|---|---|---|---|
| Self-Check: Guest-Facing Communication | I cannot explain the project without assuming the listener took this course | I can describe the project, but my opening runs long, leans on jargon, or hides what does not work | I can open the project in about ninety seconds in plain language and disclose a limitation when asked, though my answers to unexpected questions still wobble | I can open the project in ninety seconds in plain language, volunteer one rehearsed limitation or failure mode with its evidence, redirect a question I cannot answer honestly ("I don't know, but here is how I would find out"), and ask a guest a genuine question back |
| Self-Check: Mock Technical Interview | I skipped the rehearsal or could not explain my own part of the system | I explained my component but not how it connects to the rest of the system, or I could not tell a single concrete failure story | I walked my partner through the architecture, defended one design decision, and told one failure story with its mitigation, though I leaned on notes or slides | Without slides, I explained the system end to end, defended a design decision by naming the alternative we rejected and why, told a failure story with its measured mitigation (or a finding with its evidence, for audit teams), and asked my partner at least one probing question about their project when roles reversed |
| Self-Check: Portfolio Story | I have no way to show this project to anyone outside the course | I can point at the repository or write-up but cannot yet tell its story in a way a recruiter would follow | My 200-word project story exists and names my contribution, though it is not yet linked from anywhere or rehearsed aloud | My project story is written, linked from my profile or portfolio per the ShipIt guide, rehearsed aloud as a two-minute narrative, a drafted (publication-optional) LinkedIn-style post exists, and I can produce the evidence behind every claim in it on request |

