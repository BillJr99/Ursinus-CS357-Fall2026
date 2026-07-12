---
layout: project
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
      proficient: Team process is visible and current throughout — every meeting has a posted agenda and notes with owners and dates; the decision log records alternatives and rationale; project management is real (a maintained GANTT-style timeline with named owners, sprint boundaries honored, runnable increments at each sprint); all three intra-team check-ins are submitted on time; the team demonstrably operates under its signed charter, including its conflict protocol; roles rotate per sprint and every student is primary author of at least one section or component of every team deliverable (editable by teammates); every milestone carries all members' signatures and an AI-use disclosure stating specifically what was AI-assisted, with what tool, why, and how it was verified (Goal 13)
    - weight: 40
      description: Product — the working system, audit, or publication; the Demo Day presentation; and the partner-facing artifact
      preemerging: The direction's core artifact is missing or does not function — the system does not run, the audit lacks findings and governance, or nothing was published; the Demo Day presentation is missing or covers only a happy path with no honest limitation; no partner-facing artifact exists
      beginning: The core artifact partially meets its direction's requirements but would not be usable by its intended audience without significant rework — the system runs but is unreproducible or unevaluated, the audit's governance recommendations lack owners, thresholds, or timelines, or the published artifact lacks working documentation, tests, or a registry presence; the presentation serves only a technical audience or omits the failure disclosure; the partner-facing artifact is missing or unusable by the partner
      progressing: The core artifact meets its direction's requirements — a running, documented, evaluated system with committed governance (A); a complete risk analysis and adoptable governance document (B); or a published, installable, tested, documented artifact with a community exchange (C) — and Demo Day includes both a technical segment and a stakeholder-facing segment with a partner-facing artifact, with minor gaps in polish, accessibility, or the honesty of the limitations discussion, and a public repository or write-up exists but has gaps in recruiter-legibility (a README a stranger could not follow, or no contribution attribution) (Goal 14)
      proficient: The core artifact fully meets its direction's requirements and is honest about its limits - Direction A - the system runs from a fresh start following the README, configuration and seeds are externalized and pinned, CI passes on the submission SHA, evidence is surfaced to the user with a confirmation gate on consequential actions, and the committed GOVERNANCE.md matches deployed behavior; Direction B - the artifact package (risk analysis with at least 8 citations, governance document with monitoring plan, incident response, communication plan, and appeal process) could be handed to a regulator without modification; Direction C - the artifact is live and installable from a public registry with green CI, a stranger-tested quickstart, CONTRIBUTING.md and GOVERNANCE.md, and a documented substantive community exchange; the Demo Day presentation serves the multi-audience — a live technical segment with a rehearsed failure or limitation disclosure and a plain-language stakeholder segment — with every teammate speaking substantively and every teammate able to present any part; and the partner-facing artifact (one-page brief, demo video, or deployed tool) is something the community partner can actually use, presented at Demo Day and included in the submission; and the project leaves a public, recruiter-legible trace — a public repository (Directions A and C) or a public write-up or portfolio page (Direction B) whose README or summary answers what it is, why it matters, and how to run or read it in thirty seconds, names each member's contribution, and is suitable for linking from a resume (Goal 14)
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

> **The Project Thread:** The Final Project is the final stage of the semester-long [Project Thread](/Projects/PBLThread). Your proposal must build on your team's [Stakeholder Brief](/Assignments/StakeholderBrief) and [Literature Review](/Assignments/LitReview), your team operates under its signed charter and the [Team Playbook](/Projects/PBLThread), and Demo Day addresses both technical and non-technical audiences. See the Thread hub for the semester map and assessment philosophy.

## Project Overview

The Final Project is **one required project with three directions**. Every team completes the same arc — proposal, sprints with check-ins, a gallery walk, and Demo Day — and every team is graded on the same three rubric families. What differs is the direction your team chooses for its intervention:

- **Direction A: Custom Agent Team** — design, build, and evaluate a system of at least three cooperating, specialized agents that accomplishes a real goal-oriented task end to end on your local stack, benchmarked against a monolithic baseline and governed by a document you can defend.
- **Direction B: Responsible AI Audit** — perform a structured, evidenced responsible-AI audit of a specific deployed system: a risk analysis with mechanistic failure modes, a governance document a real organization could adopt, and a presentation a real board could act on.
- **Direction C: Build and Publish an Open-Source Agent** — identify and verify a real gap in the agent tooling ecosystem, then build, test, document, and publish an open-source agent to a public registry, engaging a real community with its governance and limitations disclosed — or, as a variant, contribute reviewed pull requests to an existing open-source agent project (see the variant under Direction C below).

These are directions within the one project, not separate assignments: your team chooses the direction that best serves the stakeholder problem you have carried since the [Stakeholder Brief](/Assignments/StakeholderBrief). All three directions are completed with your standing Project Thread team, operating under its signed charter, with project roles (**Coordinator**, **Builder**, **Evaluator**, **Scribe**) rotating at every sprint boundary.

**The project is the vehicle, not the destination.** The graded emphasis falls on your *process* as much as your *product*: how you decided, how you worked together, how you engaged your community partner, and how honestly you disclosed what worked and what did not. A team that meets on schedule, logs its decisions, checks in candidly, and reports a limitation honestly will outscore a team with a slicker artifact and no visible process.

**There is no final exam in this course.** Demo Day presentations — plus the registrar's final-exam slot if needed for presentation overflow — are the terminal event of the semester.

---

## The Unified Timeline

This is the authoritative schedule for the Final Project, superseding any dates on earlier drafts or handouts. **No work is accepted after the last class meeting.**

| Date | Week | Milestone | Points |
|------|------|-----------|--------|
| Thu Oct 29 | wk9 | **Project handed out.** Teams read all three directions and begin converging on one. | — |
| Tue Nov 3 | wk10 | **Intra-team check-in 2** (private, to the instructor) — this check-in precedes and informs your proposal. | — |
| Tue Nov 10 | wk11 | **Proposal due**, with direction declared, stakeholder grounding, and AI-use disclosure. | **25 / 100** |
| wk12 – wk14 | wk12–14 | **Sprints.** Rotating roles, a runnable increment (or evidenced stage checkpoint) at every sprint boundary, and a **partner feedback pass** during the sprint/gallery-walk window (week 14). | — |
| Tue Dec 1 | wk14 | **Gallery walk + peer review (SQR cards)**, and **intra-team check-in 3**. | — |
| Tue Dec 8 | wk15 (last class) | **Demo Day + final submission**, including the partner-facing artifact and the final AI-use disclosure. | **75 / 100** |

The registrar's final-exam slot is reserved for Demo Day overflow only — if all teams present on Dec 8, it is not used. Either way, Dec 8 is the submission deadline: no work is accepted after the last class meeting.

---

## Community Partner Engagement

This project is deliberately community-grounded: **every team connects its project to a community stakeholder**. Partners are identified by the instructor — see the partner roster in the syllabus. Three touchpoints are required:

1. **Proposal (Tue Nov 10):** the partner's stated needs inform the proposal, building directly on your Project Thread [Stakeholder Brief](/Assignments/StakeholderBrief). Name the problem in the partner's terms and state how the direction you chose serves it.
2. **Partner feedback pass (week 14):** during the sprint/gallery-walk window, share your in-progress work with your partner (a demo, a findings summary, or a draft artifact) and document their feedback and how you triaged it — incorporate, disclose, or defer.
3. **Partner-facing artifact (Demo Day, Tue Dec 8):** deliver an artifact an external stakeholder can actually use — a one-page brief, a demo video, or a deployed tool — and present it at Demo Day to a **multi-audience** of technical peers and community stakeholders.

---

## How the Grade Works

Your final-project grade combines **team output**, **individual contribution**, and **individual understanding**:

- **Team output** is the team's score on the three rubric families below, applied to the proposal (25 points) and the final submission and Demo Day (75 points).
- **Individual contribution**: every student must be **primary author of at least one section or component** of every team deliverable — named in the document, and editable by teammates. Your primary-author sections, check-in record, and role-rotation history are your contribution evidence. Riding along is not a strategy, and neither is doing everything yourself.
- **Individual understanding** is assessed through the **Demo Day question-and-answer** and your **individual reflection**: can you explain and defend any part of the work, including parts you did not primarily author?

**AI-use disclosure:** both the proposal and the final submission must include a disclosure statement of **how and why AI tools were used** — what was AI-assisted, with what tool, why you chose to use it there, and how the output was verified. Disclosed, verified AI assistance is professional practice; undisclosed AI assistance is an integrity violation.

**Absence policy for Demo Day:** every team member must be able to present *any* part of the project — prepare accordingly. The grade of a member absent on Demo Day depends on the reason for the absence and on that member's documented contribution to that point.

---

## Stage 1: Proposal — due Tue Nov 10 (25 points)

Every proposal (2–3 pages), regardless of direction, must include:

- **Direction declaration** and a one-paragraph problem statement naming the task or system, the affected users or populations, and the success criterion.
- **Stakeholder grounding** integrating your [Stakeholder Brief](/Assignments/StakeholderBrief) and [Literature Review](/Assignments/LitReview): the problem in the partner's terms, the gap your review identified, how this project addresses it, and what the partner's needs imply for scope (Goals 11, 12).
- **Implementation-and-assessment sketch**: who holds which role in which sprint, how progress will be assessed at each sprint boundary, and a shared GANTT-style timeline mapping tasks to weeks 12–14 with named owners (Goal 13).
- **AI-use disclosure** for the proposal itself.
- The **direction-specific elements** listed under your direction below.

Incomplete proposals are returned ungraded; proposals whose scope is too generic, inaccessible, or infeasible in three sprints are redirected. The second intra-team check-in (Tue Nov 3) lands one week before this deadline — use it to surface scope disagreements early.

---

## Stage 2: Sprints — weeks 12 through 14

Build in three sprints aligned with in-class studio days. Each sprint produces: a **runnable increment or evidenced stage checkpoint** (per your direction's milestones below), an **updated evaluation or evidence table** (a number or a citation, not an adjective), and **Scribe notes** from the sprint retrospective. Roles rotate at each boundary so every member holds every role.

| Sprint | Direction A milestone | Direction B milestone | Direction C milestone |
|---|---|---|---|
| Sprint 1 (wk12) | Monolith baseline running; 10-task evaluation set finalized (frozen after this); agent design table drafted; repo + CI placeholder | Evidence folder with 5+ sources; framework mapping begun; first failure-mode candidates identified | Running MVP (core feature only); at least 3 tests (1 unit + 2 property); CI green on the MVP |
| Sprint 2 (wk13) | All agents implemented and individually testable; at least 5 evaluation tasks run; GOVERNANCE.md first draft committed | Risk analysis report drafted (4–6 pages, 8+ citations, 3 mechanistic failure modes); governance document outlined | Non-trivial feature implemented; third property test added; README quickstart drafted and cold-tested by a classmate |
| Sprint 3 (wk14) | Full evaluation with baseline comparison; 3+ failure modes documented with transcripts; one mitigation re-measured; gallery-walk prep | Governance document complete (monitoring plan, incident response, communication plan, appeal process); board presentation rehearsed | Published to a registry, tagged v1.0.0; community post made; CONTRIBUTING.md and GOVERNANCE.md complete |

**Partner feedback pass (week 14):** during this window, put your work in front of your community partner and document the exchange (see Community Partner Engagement above).

**Gallery walk + peer review (Tue Dec 1):** mandatory and graded within the Process family. Host honestly — demonstrate your work including at least one known failure or open finding. Walk generously — fill out a **S**trength / **Q**uestion / **R**isk card for every team you visit. Triage all feedback you receive into three buckets — *fix before submission*, *disclose in the report*, or *defer to future work* — and put your triage decisions in the artifacts folder. Intra-team check-in 3 is due the same day.

---

## Stage 3: Demo Day and Final Submission — Tue Dec 8 (75 points)

Every team, regardless of direction, delivers at Demo Day:

- A **live technical segment** for CS peers — a real demonstration (Direction A: the running system; Direction B: a walkthrough of the framework application and evidence for one failure mode's mechanism; Direction C: the installed, published artifact) including a **rehearsed failure or limitation disclosure**.
- A **non-technical, stakeholder-facing segment** in plain language: who this is for, the problem in their terms, what the work does for them, what it must not be used for, and a brief multidisciplinary reflection on how disciplines beyond CS shaped the work (Goal 14).
- The **partner-facing artifact**, presented to the multi-audience and included in the submission.
- A **public portfolio artifact**: the public repository (Directions A and C) or public write-up/portfolio page (Direction B) described in the Product rubric — run the [ShipIt](/Assignments/ShipIt) self-check against it before your publish gate.
- **Every teammate speaks substantively**, and every teammate must be prepared to present any part (see the absence policy above).
- Q&A with the instructor, peers, and partners — this is where individual understanding is assessed. Demo Day is **external-facing**: alumni, industry guests, and faculty from other departments may join the audience and Q&A, as available — your grade never depends on who attends. Prepare with the [Demo Day Guide](/Assignments/DemoDayGuide); the week 14 Project Studio includes a cross-team mock-interview rehearsal, credited as class participation.

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
- Surface evidence to the user following the honest evidence hierarchy (direct retrieval citation over generated summary), with a **human confirmation gate** on every consequential action and a demonstrated **abstention behavior** (the system declines rather than hallucinating when evidence is absent)
- Commit a **GOVERNANCE.md** that matches the deployed system's behavior — data handling, human gates, incident response — updated at each sprint boundary, not written at the end
- Lead a **10-minute class discussion** (scheduled per team during the sprint weeks) on the responsible use of your system, grounded in your own measurements, with at least 4 minutes for class questions and two genuine questions you do not know the answer to

**Direction A final deliverables:**
1. **The system:** a repository that runs from a fresh start following the README in under 3 minutes on a machine the team has not configured — configuration externalized to `config.json`, model versions and seeds pinned, exceptions handled with located messages, a test suite with at least one end-to-end test, CI on every push, and a publish step (triggered by the `submission` tag) pushing the artifact to GHCR, Docker Hub, or npm
2. **The report** (6–8 pages): design rationale tied to named course patterns; evaluation results with the baseline comparison table, failure analysis with transcripts, and re-measurement after mitigation; explainability design; limitations (your "disclose" bucket from the gallery walk, verbatim); a governance summary referencing the committed GOVERNANCE.md; and individual contribution statements documenting the role rotation
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
- **Systematic risk analysis** (4–6 pages, at least 8 citations): apply the chosen framework in full — all four NIST functions (GOVERN, MAP, MEASURE, MANAGE), an argued EU AI Act risk-tier classification with applicable obligations, or all ten Montreal Declaration principles each with an evidentiary basis. Every major framework step produces a specific, evidenced finding
- At least **three failure modes with named mechanisms** — each naming the affected group or input type, the specific erroneous output, and the mechanism — distinguishing risks that have materialized from risks that are foreseeable, and naming accountability gaps specifically (what role is absent, and what decision cannot be made without it)
- **Governance document** (3–5 pages) a real organization could adopt, passing the third-party test (could an outside auditor verify compliance from evidence?): a **monitoring plan** (each metric with data source, frequency, review threshold, and named owner), an **incident response procedure** (specific incident definition, notification order and timeframes, suspension authority), a **stakeholder communication table** (general public, affected individuals, regulators), and an **appeal process** navigable without a lawyer (initiation, reviewer, evidence, remedies, timeline). Every recommendation must trace to a specific risk finding

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
- **Community engagement:** an honest post in a relevant community (r/LocalLLaMA, r/MachineLearning, a relevant Discord, or Show HN); respond substantively to feedback — acknowledge its substance and incorporate it, explain why not, or file an issue — and document the exchange with a screenshot or link. If no response arrives within a week, post to a second community and document the attempt

**Direction C final deliverables:**
1. **The repository and the published package**: public GitHub repo running from a fresh start, CI green on the submission SHA, and a live registry URL where the artifact is installable
2. **The report** (3–5 pages): the gap and how it was verified; key design decisions and tradeoffs; property-test results; documentation strategy and the classmate quickstart-test result; license justification; governance rationale; the community engagement summary with evidence; and individual contribution statements
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
