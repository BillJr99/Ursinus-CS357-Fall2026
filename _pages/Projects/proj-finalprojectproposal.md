---
layout: assignment
permalink: /Projects/FinalProjectProposal
title: "CS357: Foundations of Artificial Intelligence - Final Project Proposal"

info:
  coursenum: CS357
  purpose: "To commit your team to one defensible plan before you start building: a declared direction, a stakeholder-grounded problem, an argued set of design decisions, and a sprint timeline with named owners, so that the sprint window is spent executing a plan rather than discovering one."
  tilt:
    task: "With your standing team, write a 2-3 page proposal that declares your Final Project direction (A, B, or C), grounds it in your Stakeholder Brief and an initial evidence base, sketches the implementation and assessment plan with a GANTT-style timeline, includes the direction-specific elements, and discloses AI use."
    criteria: "Assessed on three course families worth 60 points between them, Approach (a defended direction and argued design decisions), Process and Professionalism (authorship, timeline, signatures, check-in, and disclosure), and Plan Quality (scope, feasibility, and stakeholder grounding), plus the four AAC&U VALUE Problem Solving criteria that a plan can actually demonstrate, worth 40; see the rubric below for the full breakdown."
  points: 25
  goals:
    - To declare one Final Project direction and defend it against the two you did not choose, naming what your team gains and gives up
    - To carry the stakeholder problem forward from the Stakeholder Brief into a scoped, buildable plan, and to state the gap the project addresses specifically enough that the Literature Review can later confirm or refute it (Goals 11, 12)
    - To argue every major design decision at the point where it is still cheap to change, naming the alternative rejected and the course pattern, principle, or evidence that motivated the choice
    - To size the work honestly against three sprints, producing a GANTT-style timeline with named owners and a role-rotation plan the team has agreed to
    - To anticipate failure before it happens through a pre-mortem, a preliminary risk hypothesis, or a verified gap, depending on direction
    - To practice visible, professional team process at the first milestone of the project, with per-section primary authorship, all-member signatures, and an honest AI-use disclosure (Goal 13)
  rubric:
    - weight: 22
      description: Approach, a defended direction and argued design decisions
      preemerging: No direction is declared, or a direction is named with no reasoning; design decisions are absent or are unexplained defaults; the direction-specific proposal elements are missing
      beginning: A direction is declared but the justification is generic ("it seemed most interesting") rather than tied to the team's stakeholder problem or capabilities; design choices are asserted rather than argued; several direction-specific elements are missing or filled in with placeholders
      progressing: The direction is declared and reasonably defended, most major design decisions are justified with reference to course patterns or evidence, and the direction-specific elements are present and substantially complete, with minor gaps in how the alternatives were weighed or in the specificity of one or more elements
      proficient: The direction is declared and defended against the two rejected alternatives in terms of the team's stakeholder problem and capabilities; every major design decision names the alternative that was rejected and the course pattern, principle, or evidence that motivated the choice; and all direction-specific elements are complete and specific (Direction A - an agent design table with per-agent temperature justification and isolated evaluations, a defended topology, a memory and context plan, a 5-row pre-mortem each with its owning checker or gate, and an evaluation plan naming the baseline and numeric metrics; Direction B - a named deployed system with an identified operator, affected populations traced to decisions, a framework choice defended against the two alternatives, a written-in-advance risk hypothesis, and two independent sources evidencing sufficient public information; Direction C - a stranger-legible artifact description, two to three specific personas, an exact install sequence, a gap verified against the closest existing alternative with linked evidence, a one-sentence minimum viable scope with stretch goals, and a governance sketch naming prohibited uses)
    - weight: 18
      description: Process and Professionalism, authorship, timeline, signatures, check-in, and disclosure
      preemerging: The proposal shows no evidence of team process, no per-section primary authors, no timeline, no signatures, and no AI-use disclosure
      beginning: Some process artifacts exist but are thin, the timeline is a list of tasks without owners or sprint boundaries, the role-rotation plan is missing, one or more members are not primary author of any section, signatures are incomplete, or the AI-use disclosure is a single generic sentence
      progressing: Per-section primary authorship, a GANTT-style timeline mapped to the three sprints, a role-rotation plan, all-member signatures, and an AI-use disclosure are all present, and the second intra-team check-in was submitted, but one element is thin, late, or inconsistent with what the rest of the proposal says (Goal 13)
      proficient: "Every student is named primary author of at least one section, editable by teammates; the GANTT-style timeline maps tasks to the three sprints with named owners and honest durations, and is consistent with the scope claimed elsewhere in the proposal; the role-rotation plan assigns Coordinator, Builder, Evaluator, and Scribe across sprint boundaries so every member holds every role; the document's version or commit history shows a real drafting trajectory rather than a single late paste; the proposal carries all members' signatures; the second intra-team check-in was submitted on time and its content is visibly reflected in the proposal's scope; and the AI-use disclosure states specifically what was AI-assisted, with what tool, why it was used there, and how the output was verified (Goal 13)"
    - weight: 20
      description: "Plan Quality: scope, feasibility, and stakeholder grounding"
      preemerging: The plan is too generic to act on, the scope is unbounded or unrelated to the team's stakeholder, and there is no evidence the work could be completed in three sprints
      beginning: The scope is stated but is either far too large for three sprints or so small it would not exercise the direction's requirements; the stakeholder connection is nominal, a sentence asserting relevance rather than a problem framed in the partner's terms
      progressing: The scope is plausible for three sprints and the plan builds on the Stakeholder Brief and an initial evidence base, but sprint boundaries are uneven, one milestone carries most of the risk, or the account of what the partner's needs imply for scope is thin
      proficient: The scope is specific, accessible, and demonstrably sized to three sprints, with each sprint producing a runnable increment or evidenced stage checkpoint and no single boundary carrying disproportionate risk; the problem appears in the partner's terms, the gap the project addresses is named specifically enough that the Literature Review that follows could confirm or refute it, and the proposal states explicitly what the partner's stated needs imply for scope, including what the team has decided not to do (Goals 11, 12)
    - weight: 9
      description: "Define Problem (AAC&U VALUE Problem Solving); here, the stakeholder problem carried from your Brief into the proposal"
      preemerging: Demonstrates a limited ability in identifying a problem statement or related contextual factors.
      beginning: Begins to demonstrate the ability to construct a problem statement with evidence of most relevant contextual factors, but problem statement is superficial.
      progressing: Demonstrates the ability to construct a problem statement with evidence of most relevant contextual factors, and problem statement is adequately detailed.
      proficient: Demonstrates the ability to construct a clear and insightful problem statement with evidence of all relevant contextual factors.
    - weight: 7
      description: "Identify Strategies (AAC&U VALUE Problem Solving); here, the directions and architectures you weighed before choosing"
      preemerging: Identifies one or more approaches for solving the problem that do not apply within a specific context.
      beginning: Identifies only a single approach for solving the problem that does apply within a specific context.
      progressing: Identifies multiple approaches for solving the problem, only some of which apply within a specific context.
      proficient: Identifies multiple approaches for solving the problem that apply within a specific context.
    - weight: 14
      description: "Propose Solutions/Hypotheses (AAC&U VALUE Problem Solving); here, the proposed project itself and its design decisions"
      preemerging: Proposes a solution/hypothesis that is difficult to evaluate because it is vague or only indirectly addresses the problem statement.
      beginning: Proposes one solution/hypothesis that is "off the shelf" rather than individually designed to address the specific contextual factors of the problem.
      progressing: "Proposes one or more solutions/hypotheses that indicates comprehension of the problem. Solutions/hypotheses are sensitive to contextual factors as well as the one of the following: ethical, logical, or cultural dimensions of the problem."
      proficient: "Proposes one or more solutions/hypotheses that indicates a deep comprehension of the problem. Solution/hypotheses are sensitive to contextual factors as well as all of the following: ethical, logical, and cultural dimensions of the problem."
    - weight: 10
      description: "Evaluate Potential Solutions (AAC&U VALUE Problem Solving); here, your pre-mortem, risk hypothesis, or gap verification, and the alternatives you rejected"
      preemerging: "Evaluation of solutions is superficial (for example, contains cursory, surface level explanation) and includes the following: considers history of problem, reviews logic/reasoning, examines feasibility of solution, and weighs impacts of solution."
      beginning: "Evaluation of solutions is brief (for example, explanation lacks depth) and includes the following: considers history of problem, reviews logic/reasoning, examines feasibility of solution, and weighs impacts of solution."
      progressing: "Evaluation of solutions is adequate (for example, contains thorough explanation) and includes the following: considers history of problem, reviews logic/reasoning, examines feasibility of solution, and weighs impacts of solution."
      proficient: "Evaluation of solutions is deep and elegant (for example, contains thorough and insightful explanation) and includes, deeply and thoroughly, all of the following: considers history of problem, reviews logic/reasoning, examines feasibility of solution, and weighs impacts of solution."
  readings:
    - rtitle: "Agent Teams Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentteams.md"
    - rtitle: "Project Studio Protocol"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-projectstudio.md"
    - rtitle: "Problem Solving VALUE Rubric (AAC&U); the four problem-solving criteria in the rubric below are quoted from it"
      rlink: "https://www.lamar.edu/data-analytics-reporting-analysis/_files/documents/problem_solving.pdf"

tags:
  - final-project
  - proposal
  - agents
  - governance
---

> **The Project Thread:** The Final Project Proposal is the first graded stage of the [Final Project]({{ site.baseurl }}/Projects/FinalProject), which is itself the last stage of the semester-long [Project Thread]({{ site.baseurl }}/Projects/PBLThread). Your proposal must build on your team's [Stakeholder Brief]({{ site.baseurl }}/Assignments/StakeholderBrief); the [Literature Review]({{ site.baseurl }}/Assignments/LitReview) is handed out the day this is due and reads against the plan you commit to here. Your team writes it under its signed charter and the [Team Playbook]({{ site.baseurl }}/Projects/PBLThread).

## What This Is

This is the plan you will be held to. It is worth **25 of the Final Project's 100 points**; the remaining 75 are earned at Demo Day and in the final submission, and are graded against the [Final Project rubric]({{ site.baseurl }}/Projects/FinalProject), not this one.

The proposal exists because the sprint window is short and unforgiving. A team that arrives at Sprint 1 with a declared direction, an argued architecture, named owners, and an honest sense of what could go wrong spends the sprints building. A team that arrives still deciding spends the sprints deciding, and demos an apology.

**This is not a new assignment.** Nearly everything it asks for already exists in your team's work: the stakeholder you interviewed, the literature you synthesized, the agent system you designed, and the labs you built. Read what follows as an assembly plan.

---

## Before You Start

**Read the [Final Project]({{ site.baseurl }}/Projects/FinalProject) page in full first**, including all three directions. That page is the complete reference for the project; this page is the proposal deliverable and its rubric.

**Where this sits in the Project Thread.** The proposal comes *before* the [Literature Review]({{ site.baseurl }}/Assignments/LitReview), and the ordering is deliberate: you commit to a plan, then read against it. The review is expected to confirm parts of this document, complicate others, and occasionally kill one, and the team synthesis has to say which. Propose the plan you actually believe in, not the one that will be easiest to defend later.

**Choosing a direction** is the one decision worth making slowly, because all three are real and they suit genuinely different teams:

| Take | If your team |
|---|---|
| **A: Custom Agent Team** | Wants to build. You have people who enjoy making things run, and a stakeholder problem a multi-agent system actually fits |
| **B: Responsible AI Audit** | Wants to investigate. This is a **fully non-programming** direction and it is not the lesser one; a good audit is harder than a mediocre build |
| **C: Open-Source Agent** | Wants what you make to outlive the semester, and is willing to take documentation, packaging, and licensing as seriously as the code |

**The second intra-team check-in lands shortly before this deadline.** It is private, it goes to the instructor, and it exists precisely so that scope disagreements surface here rather than in week 14. Use it honestly; a check-in that says "everything is fine" from a team that is not fine is a wasted instrument.

**Length:** 2-3 pages, excluding the timeline, tables, and appendices.

---

## What Every Proposal Must Include

Regardless of direction:

- **Direction declaration** and a one-paragraph problem statement naming the task or system, the affected users or populations, and the success criterion. Declare the direction explicitly; do not leave it inferable.
- **Direction defense**: why this direction, and what you gain and give up relative to the two you did not choose. Two or three sentences is enough, but they must be about *your* team and *your* stakeholder, not about the directions in general.
- **Stakeholder grounding** built on your [Stakeholder Brief]({{ site.baseurl }}/Assignments/StakeholderBrief): the problem in the partner's terms, the gap this project addresses, the initial evidence you have that the gap is real (sources you have actually opened, per your direction's requirements), and what the partner's needs imply for scope, **including what you have decided not to do** (Goals 11, 12). The [Literature Review]({{ site.baseurl }}/Assignments/LitReview) that follows tests this gap claim in depth, so state it here specifically enough to be proven wrong.
- **Implementation-and-assessment sketch**: who holds which role in which sprint, how progress will be assessed at each sprint boundary, and a shared **GANTT-style timeline** mapping tasks to the three sprints with named owners (Goal 13).
- **Design decisions**, each naming the alternative rejected and the course pattern, principle, or evidence that motivated the choice. This is the section that most distinguishes a proposal from a summary.
- **AI-use disclosure** for the proposal itself: what was AI-assisted, with what tool, why you chose to use it there, and how the output was verified. Disclosed, verified AI assistance is professional practice; undisclosed AI assistance is an integrity violation.
- **Signatures** from every team member, and a named **primary author for each section**, editable by teammates.
- The **direction-specific elements** below.

---

## Direction-Specific Proposal Elements

These mirror the elements listed under each direction on the [Final Project]({{ site.baseurl }}/Projects/FinalProject) page; that page carries the full build requirements and final deliverables for each.

### Direction A: Custom Agent Team

- An **agent design table**, one row per agent: role, system-prompt summary, inputs, outputs, temperature with justification, tools, and the isolated evaluation you will run on it
- A **topology statement** (pipeline, router, planner, blackboard, or hybrid) with a 3-sentence defense
- A **memory and context plan**: what each agent carries, summarizes, retrieves, and discards
- A **pre-mortem table** with at least 5 predicted risks (your specification gap, irreversible action, global invariant, and two more), each with the deterministic checker or gate that owns it
- An **evaluation plan**: the 10-task set sketch, numeric metrics (precision, recall, parse success rate, latency, or human rating), the protocol, and the **monolith baseline** description

> The [Design Your Agent System]({{ site.baseurl }}/Assignments/AgentSystemDesign) written assignment is due the week after this proposal and develops these same artifacts in full depth. Sketch them here at proposal fidelity, enough to defend the architecture and show the work is feasible; the design assignment is where they become a specification someone else could build from.

### Direction B: Responsible AI Audit

- **System identification**: name, operator, what it does, where it is deployed. The system must be specific: not "AI in hiring" but a named tool as deployed by a named operator
- **Affected populations**: who is affected and how the system's decisions reach them
- **Framework choice** (NIST AI RMF, EU AI Act, or Montreal Declaration) with a 3-sentence justification for why it fits this system better than the alternatives
- **Preliminary hypothesis**: where you expect the highest risks to lie, written before the deep analysis
- Evidence that enough public information exists (at least two independent sources from an initial search)

> **Your framework choice may be provisional.** Governance and policy writing comes after this proposal on the schedule. Declare the framework you expect to use and defend it as well as you can now; you may revise that choice once, with a written justification, by the end of Sprint 1. The other Direction B elements are not provisional.

### Direction C: Build and Publish an Open-Source Agent

- **What the artifact does**, in one paragraph a stranger can understand
- **Who would use it**: two to three user personas with realistic, specific use cases
- **How they would install it**: the exact command sequence from a clean machine to a working demo
- **Gap verification**: the closest existing alternative, the specific gap it does not fill, and linked evidence the gap is real (a community post, GitHub issue, or unanswered Stack Overflow question where a real person asked for this)
- **Minimum viable scope** in one sentence, plus two to three stretch goals
- **Governance sketch**: who is responsible, what the artifact must never be used for, and what risk the instructor should know about before approving

> If you are taking the **Direction C variant** (contributing to an existing open-source project rather than publishing a new one), the "what the artifact does / who would use it / how they would install it" elements describe the upstream feature you are adding, and gap verification becomes issue selection with linked evidence that a maintainer or real user wants it. Scope must be approved here, in the proposal.

---

## How This Is Graded

The rubric has two halves, in the same spirit as the Final Project's:

- Three **course families** worth 60 points between them: **Approach** (a defended direction and argued design decisions), **Process and Professionalism** (authorship, timeline, signatures, check-in, and disclosure), and **Plan Quality** (scope, feasibility, and stakeholder grounding).
- Four criteria worth 40 between them, quoted verbatim from the **Problem Solving VALUE Rubric** published by the Association of American Colleges and Universities and reproduced here under its permission for classroom use. AAC&U's four performance levels map onto this course's four: *Benchmark 1* is read as pre-emerging, *Milestone 2* as beginning, *Milestone 3* as progressing, and *Capstone 4* as proficient. The translation into a graded course rubric, and the weights, are mine.

Only four of AAC&U's six problem-solving criteria appear here, and the omission is deliberate: *Implement Solution* and *Evaluate Outcomes* cannot be demonstrated by a plan. They are graded at Demo Day, on the [Final Project rubric]({{ site.baseurl }}/Projects/FinalProject). What a proposal *can* demonstrate is that you defined the problem, weighed the strategies, proposed something specific, and evaluated it honestly before committing, which is why *Propose Solutions/Hypotheses* and *Evaluate Potential Solutions* carry the most weight of the four.

**A note on what "evaluate potential solutions" means here.** Your pre-mortem (Direction A), preliminary risk hypothesis (Direction B), or gap verification (Direction C) is the evidence for this criterion, together with the alternatives you rejected and why. A proposal that names no rejected alternative and predicts no failure cannot score above beginning on it, however polished the plan looks.

---

## What Happens After You Submit

- **Incomplete proposals are returned ungraded.** Complete means every shared element and every direction-specific element is present, not that every one is perfect.
- **Proposals whose scope is too generic, inaccessible, or infeasible in three sprints are redirected**, with specific guidance on what to cut or change. A redirect is not a penalty; it is much cheaper here than in week 14.
- **Sprint 1 begins from the approved proposal**, and runs to the cross-team proposal critique. Your Sprint 1 milestone is set by your direction; see the sprint table on the [Final Project]({{ site.baseurl }}/Projects/FinalProject) page.
- **The [Literature Review]({{ site.baseurl }}/Assignments/LitReview) is handed out the day this is due**, and it reads against the plan you have just committed to. Its team synthesis must state what the evidence confirms, complicates, or changes about this proposal. A synthesis that changes nothing is a warning sign, not a clean bill of health.
- Some proposal artifacts are **living documents**: the pre-mortem, the decision log, and the timeline are maintained through the sprints and resubmitted with the final artifacts folder, not frozen here.

---

## Self-Check Before You Submit

Answer these honestly as a team. Every "no" is cheaper to fix now than at any later point in the project.

- Could a classmate outside your team read the problem statement and say who is affected and what success would look like?
- Does the proposal name at least one alternative you rejected, and say why?
- Would your community partner recognize their problem in your description of it, in their own words?
- Does the timeline have a named owner on every task, and does each sprint boundary produce something runnable or evidenced?
- Is there anything on the timeline that only one person on the team knows how to do?
- Have you written down what you are *not* doing?
- Is every team member primary author of at least one section, and can every member explain every section?
- Does the AI-use disclosure name the tool, the section, the reason, and the verification, rather than gesturing at "AI was used for editing"?
- Is your gap claim specific enough that the Literature Review could prove it wrong?
- If your most likely predicted failure happened in Sprint 2, does the plan survive it?
