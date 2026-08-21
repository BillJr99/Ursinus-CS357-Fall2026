---
layout: assignment
permalink: /Assignments/AgentSystemDesign
title: "CS357: Foundations of Artificial Intelligence - Written Assignment 2: Design Your Agent System"

info:
  coursenum: CS357
  purpose: "To build the discipline of designing an agent system on paper: its goals, agents, data flow, gates, failure modes, and success criteria, so ambiguity and risk surface in writing while they are still cheap to fix, before or alongside implementation."
  tilt:
    task: "Choose one direction and produce a complete written design for an agent system: either a spec-first design document (problem statement, agent design table, data-flow diagram, pre-mortem, and measurable success criteria) or a full agent operating system (charter, agent contract, standing prompt with confirmation gates, and handoff files) proven by an interrupted-session handoff walkthrough."
    criteria: "Assessed on one shared rubric across both directions: problem framing and constraints, architecture and specification quality, failure-mode analysis and gate design, verifiability and evidence, and reflection and presentation; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To articulate the goals, constraints, and rules of an agentic system in writing before or alongside implementation, with every constraint or rule specific enough that a third party could determine whether it was satisfied or enforced
    - To specify the agents that compose a system (their roles, prompts or contracts, inputs, outputs, and capabilities) precisely enough that someone else could build or operate the system from the document alone
    - To trace how data, tasks, and state move through the system, including every handoff, branch, and external call, or every zone of the workspace and the write protocols that govern it
    - To anticipate failure before it happens, through a concrete pre-mortem with detection and mitigation, or through confirmation gates and an autorun/queue/forbidden action classification justified by named failure modes and reversibility reasoning
    - To define how an outsider would verify the design works, through third-party-measurable success criteria, or through a handoff walkthrough in which a second session resumes an interrupted task from the written state alone
    - To reflect honestly on where the design changed, where it leaked, and what revision each discovery motivates
  rubric:
    - weight: 20
      description: Problem Framing, Scope, and Constraints
      preemerging: The problem or domain statement is missing, or describes a feature list rather than a problem the system solves for someone
      beginning: A problem or domain statement is present but omits who the system serves, the context of use, or the key constraints and priorities; constraints read as aspirations rather than boundaries
      progressing: The statement identifies the system's purpose, users, and context with most constraints or priorities named, though some remain vague or unmeasurable, for example, "the system should be fast" without a threshold, or a priority list with no demonstrated tie-break
      proficient: "For Direction A: the one-paragraph problem statement answers all four questions (what, for whom, in what context, under what constraints), every constraint names a specific measurable boundary a stranger could check, and at least two constraints limit the system's behavior or data access rather than describing desired qualities. For Direction B: the charter states a one-sentence mission, a ranked priority list whose ranking is demonstrated with a concrete conflict it resolves, a definition of success, and rules the author could actually enforce, all unmistakably about the chosen domain"
    - weight: 25
      description: Architecture and Specification Quality
      preemerging: No agent design table or document set is provided, or a single undifferentiated agent is described, or required documents are missing or contain unfilled placeholders
      beginning: The table or document set is present but incomplete, missing required columns or sections, roles that are not meaningfully distinct, or sections copied from templates with no domain adaptation
      progressing: All required components are present and mostly specific; prompt skeletons or contract rules are present but generic enough to apply to a different system, or some retained rules have no realistic enforcement path and some deletions are unexplained
      proficient: "For Direction A: every agent row contains a distinct role; the three-sentence prompt skeleton names persona and scope, primary task, and an explicit refusal or abstention condition; inputs, outputs, a justified decimal temperature, and tools are specified; and the data-flow diagram shows every agent, every handoff with its data format, every external call, and every branch labeled with its triggering condition. For Direction B: the charter, agent contract, standing prompt, and handoff files are present, internally consistent, and unmistakably about the chosen domain; every deleted template section is listed with a one-line reason; and no rule remains that the author could not actually enforce"
    - weight: 25
      description: Failure-Mode Analysis and Gate Design
      preemerging: No pre-mortem or confirmation gates are provided, or risks and gates are copied verbatim without reference to the specific system
      beginning: Risks or gates are present but justified by abstract danger ("this could be bad") rather than a named, concrete failure mode; fewer than the required six pre-mortem risks or ten classified actions are provided
      progressing: The required coverage is met with mostly sound reasoning, but some detection signals, mitigations, or consequence descriptions remain generic ("we would notice", "be more careful"), or the forbidden lane conflates "very risky" with "no approval can make this safe"
      proficient: "For Direction A: at least six concrete, system-specific risks each name the agent, input type, and output fault; detection names a specific observable signal and mitigation names an action the system or team could actually take; at least one row addresses contradictory outputs between two agents and at least one addresses user data or privacy. For Direction B: at least ten realistic domain actions are classified autorun/queue/forbidden with explicit reversibility reasoning; every gate is justified by a concrete failure scenario naming the action, the harm, and why after-the-fact recovery is impossible or expensive; and at least one forbidden item carries an argument for why no approval should ever make it safe"
    - weight: 20
      description: Verifiability and Evidence
      preemerging: No success criteria or walkthrough is provided, or criteria are purely subjective, or the walkthrough is absent
      beginning: Criteria are stated but cannot be measured without access to the system's internals or its authors; or a walkthrough is described but the interruption is trivial or the resumption relies on information not present in the written state
      progressing: Most criteria are third-party measurable from outputs alone though at least one needs clarification, or the token ledger questions are attempted with an arithmetic or setup error; or a genuine mid-task interruption and resumption is shown but the write-up does not distinguish what the second session learned from the documents versus what it rediscovered
      proficient: "For Direction A: three to five criteria complete all four columns (criterion, what success looks like, measurement method, passing threshold), cover functional correctness plus at least one safety or quality dimension, and the reflection states how the data would be collected one week after deployment, by whom, and what follows if a criterion fails. For Direction B: the walkthrough shows a real or rigorously simulated session interrupted mid-task; the updated SESSION and CURRENT_TASK files are included verbatim, each ending with a next safe action and an evidence-cited reality check; the second session resumes from the written state alone without duplicating completed work; and every question it had to ask a human is identified along with the document revision that now answers it. Both directions: the token ledger questions are answered with correct, shown arithmetic grounded in the submission's own tool count and prompt sizes"
    - weight: 10
      description: Reflection and Presentation
      preemerging: No reflection is provided, or the submission is incomplete or contains unredacted personal or sensitive information
      beginning: A reflection is present but reports only that the design worked, without identifying a changed assumption, a leak, or a revision
      progressing: The reflection identifies at least one place the design changed or would break under real use, with a plausible revision, though the connection between evidence and revision is loose
      proficient: The reflection names a specific assumption that changed, a specific surprise or leak surfaced by the pre-mortem or walkthrough, and the concrete revision each motivates; the submission is professionally formatted, internally consistent, fully anonymized where the domain involves real people or data, and answers every reflection prompt with a specific observation from this assignment
  readings:
    - rtitle: "Agent Design Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-designfirst.md"
    - rtitle: "Pre-mortem Technique (Klein, 2007)"
      rlink: "https://hbr.org/2007/09/performing-a-project-premortem"
    - rtitle: "Case Study: Governing Coding Agents - Charters, Handoffs, and Durable Memory"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentgovernance.md"
    - rtitle: "Case Study: From Second Brain to Chief of Staff - A Personal Agent in Production"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-productionassistant.md"
    - rtitle: "Agent Operating System Templates (starting points for the Direction B document set)"
      rlink: "https://www.billmongan.com/Ursinus-CS357/files/agent-templates/README.md"
    - rtitle: "Human-in-the-Loop: Oversight, Escalation, and Appropriate Autonomy"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-humanintheloop.md"

tags:
  - design
  - agents
  - governance
  - safety
  - written

---

**Handed out** alongside the Design First session; **see the course schedule for the assigned and due dates.**

Every trustworthy agent system exists twice: once as running code, and once on paper: as the specification, contract, and gates that say what it is supposed to do, what it must never do, and how anyone would know the difference. This assignment asks you to produce that paper system. Both directions below build the same skill: designing an agent system in writing, before or alongside building it, so that ambiguity and risk surface while they are still cheap to fix. Direction A designs a system that does not exist yet: a spec-first design document of the kind engineering teams call a design proposal, system spec, or RFC. Direction B designs the operating system *around* an agent: the charter, contract, gates, and handoff state that make it trustworthy, interruptible, and independent of any single model or vendor, and then proves it works by interrupting a session mid-task. In both, the document *is* the deliverable, and polish matters exactly as much as it would in production, because in Direction B these documents are the production system.

Read both directions before choosing. Pick the one that best fits where you are: if you are still shaping what your system should be, Direction A forces the clarity; if you already have an agent (or a domain with real work in it), Direction B forces the accountability. Complete **one** direction in full depth; depth on one is worth far more than a shallow pass over both.

---

## Before You Start

**This builds on:** the *Design First* session, whose agent table and pre-mortem are the backbone of Direction A, and *How I AI*, whose charter, contract, and handoff documents are the backbone of Direction B. Both are taught before this is due.

**You need:** no code and no running system. Direction B's walkthrough needs an agent you can actually interrupt, so if you take it, use a real project (your Project Thread repository, or your `cs357-work`).

**Time:** eight to ten hours, nearly all of it thinking and writing. The pre-mortem in Direction A and the interruption walkthrough in Direction B are the parts that take longest and carry the most points; do not leave either for the last evening.

**Choosing a direction.** Read both. Then:

- Take **Direction A** if your system does not exist yet, or exists only as an idea you keep re-explaining differently each time. The document is what forces one version of it.
- Take **Direction B** if you already have an agent doing real work, or a domain with real work in it. The interruption walkthrough is unforgiving in a useful way: it tells you exactly which of your beliefs about the project were written down and which were only in your head.

**Carry three columns into your design.** From the *Design First* session: for every agent and every action, be able to say **how it is observed**, **what it can reach**, and **how it is undone**. Direction A's agent table and Direction B's action classification are both places those answers belong, and a design that cannot answer them for some component has found its own weakest point.

> **The single most common way this assignment loses points** is writing constraints that sound like values. "The system should handle sensitive data responsibly" cannot be checked by anyone. "The agent may read `students.csv` and may never write to it or transmit it off the machine" can. Apply the stranger test to every constraint and every rule before you submit: could someone who has never met you determine, from evidence, whether it held?

---

## What a Strong Submission Looks Like

A strong submission, in either direction, has these qualities:

- **Constraints and rules are specific and falsifiable.** "The system must respond in under 5 seconds on commodity hardware" is a constraint; "the system should be fast and helpful" is not. "Everything under `originals/` is immutable; the agent works only in `derived/`" is a rule; "the agent should be careful with important files" is not. Every constraint or rule passes this test: could a stranger determine, from evidence, whether it was satisfied?
- **Specifications contain real prompts and contracts, not role names.** A weak agent table says: *Summarizer Agent summarizes documents.* A strong one gives the three-sentence skeleton: persona and scope, primary task, explicit refusal condition. A weak charter is about documents; a strong charter is about your domain.
- **Every risk and gate earns its place with a story.** A weak pre-mortem lists "the model hallucinates." A strong one names the agent, the input, the observable fault, the detection signal, and the mitigation the team could actually take. A weak gate justification says "sending messages is risky." A strong one names the concrete failure (the resignation email auto-answered with a scheduling template) and why no follow-up un-sends it.
- **The verification is honest.** In Direction A, the success criteria could be applied by someone who has never met you. In Direction B, the most valuable sentence is usually something like: "The second agent asked which test command to run; my documents never said. That answer belongs in the charter's testing section, which now reads: ..."

---

## Choose One Direction

Both directions carry the full 100 points under the shared rubric above. Choose **one** and complete it in full.

- **Direction A: Design Before You Build**: produce a complete spec-first design document for an agentic system: problem statement, agent design table, data-flow diagram, six-item pre-mortem, and measurable success criteria. No implementation required; the document is the deliverable.
- **Direction B: Design Your Agent Operating System**: author the governing document set for an agent in a domain of your choosing (charter, agent contract, standing prompt with confirmation gates, handoff files, and an action classification), then prove it works with an interrupted-session handoff walkthrough.

Expand your chosen direction below for the full instructions.

<details markdown="1">
<summary><strong>Direction A: Design Before You Build</strong></summary>

You will produce a complete system design document for an agentic AI system before writing a single line of code. You will define what the system does and for whom, design the agents that compose it, trace data as it flows through the system, anticipate failures before they happen, and state success criteria that an outside evaluator could apply. You do not need to implement anything; the deliverable is the design document only.

Choose one of the following domains for your system (or propose your own, with instructor confirmation first; an overly ambitious scope will make the document less precise, which will hurt your grade):

- **Course tutoring agent**: answers student questions about a specific course topic using provided materials
- **Research assistant**: helps a user locate, summarize, and synthesize academic sources on a query
- **Code reviewer**: reviews submitted code against a rubric and returns structured feedback
- **Meeting summarizer**: processes a transcript and produces action items, decisions, and open questions

Produce the five components below.

#### Component 1: Problem Statement

Write one paragraph (no more, no less) that answers all four questions:

1. **What** does the system do?
2. **For whom** does it do it?
3. **In what context** is it used?
4. **Under what constraints** must it operate?

A good constraint limits what the system may do, what data it may use, or how it may behave when uncertain. Vague constraints ("the system should be safe and helpful") do not count; name the specific boundary, for example: "The system may only use documents the user has explicitly uploaded in the current session and must not retrieve information from the open internet."

**Example problem statement (meeting summarizer):**
> This system processes audio transcripts of team meetings and produces structured summaries for remote employees who were unable to attend. It is used within a corporate Slack workspace by teams of 5-20 people conducting 30-90 minute project syncs. Constraints: the system must never include names or identifying information in summaries without the speaker's prior consent; it must complete processing within two minutes of transcript submission; and it must abstain from summarizing any segment it cannot parse with at least 80% word-recognition confidence, flagging those segments for human review instead.

#### Component 2: Agent Design Table

Produce a table with one row per agent. Your system must have at least two meaningfully distinct agents. (If a single agent genuinely handles the full task, split it into an orchestrator/router and a specialist; even simple systems benefit from a verification or formatting agent.) Use the following columns:

| Agent Name | Role | System Prompt Skeleton (3 sentences) | Inputs | Outputs | Temperature | Tools | Failure Mode & Detection Signal |
|---|---|---|---|---|---|---|---|

**Column guidance:**

- **System Prompt Skeleton:** Write exactly three sentences. Sentence 1 establishes persona and scope; sentence 2 states the primary task; sentence 3 states at least one explicit refusal or abstention condition. Example: *"You are a document summarizer specialized in academic research papers. Your task is to produce a 100-word abstract of the document provided. If the document is not in English, respond: 'I cannot summarize this document; please provide an English-language version.'"*
- **Temperature:** A decimal value with a one-sentence justification. Example: "0.2; low temperature reduces creative variation in structured classification tasks where consistency matters more than diversity."
- **Failure Mode & Detection Signal:** Name the specific observable signal that would indicate the failure, not the abstract risk. "Hallucination" is not a failure mode. "The agent returns a citation with an author name that does not appear in any uploaded document, detectable by string-matching cited names against the document index" is.

#### Component 3: Data Flow Diagram

Describe the flow of data through your system in text or ASCII art. Show: where user input enters; which agent receives it first; what is passed between agents and in what format (plain text, JSON with named fields); where external tools or retrieval systems are called; where the final output is produced; and every branch: if an agent can refuse, escalate, or short-circuit the flow, show that branch labeled with the condition that triggers it. Length is not the goal; clarity is. A two-agent system might need 10 lines, a four-agent system with branches might need 30.

**Example (excerpt, meeting summarizer):**

```
User uploads transcript (plain text)
         |
         v
[Transcript Parser Agent]
  - Input: raw text
  - Output: JSON with speaker turns, timestamps, and confidence scores
  - On confidence < 0.80 for any segment: flag segment, route to [Human Review Queue]
         |
         v
[Summarizer Agent]
  - Input: JSON from Parser (only high-confidence segments)
  - Output: structured summary (JSON with action_items[], decisions[], open_questions[])
         |
         v
[Formatter Agent]
  - Input: structured summary JSON
  - Output: Slack-formatted markdown block
         |
         v
Final output delivered to Slack channel
```

#### Component 4: Pre-mortem Table

Imagine your system has been deployed for two weeks and has failed. Working backwards, identify at least **six** specific things that could have gone wrong:

| What Could Go Wrong | How We Would Detect It | How We Would Mitigate It |
|---|---|---|
| *(be specific: name the agent, the input type, the output fault)* | *(name a specific observable signal, not "we would notice")* | *(name an action your system or team could actually take, not "we would be more careful")* |

**Required coverage (not negotiable; these are the two most common failure categories in real multi-agent deployments):** at least one row must address a failure where two agents produce contradictory or incompatible outputs, and at least one row must address a risk involving user data or privacy.

**Example row:**

| What Could Go Wrong | How We Would Detect It | How We Would Mitigate It |
|---|---|---|
| The Summarizer Agent invents an action item not present in any transcript segment | String-match check between summary action items and transcript passages fails | Require the Summarizer to return a citation (transcript line number) for each action item; an automated checker verifies every action item maps to a real transcript line |

#### Component 5: Success Criteria

State three to five measurable criteria that a third-party evaluator (someone who has never seen your system or spoken to you) could use to determine whether your system is working, from outputs alone:

| Criterion | What "Success" Looks Like | Measurement Method | Passing Threshold |
|---|---|---|---|

Criteria should cover distinct dimensions: functional correctness (does it do the right thing?), quality (is the output useful?), and at least one safety or reliability dimension (does it behave appropriately at the boundary?). If all your criteria are variations on accuracy, you are missing a dimension. Example row: *Privacy compliance, no participant's real name appears in the summary without consent, automated scan of output against the participant list, zero name appearances in summaries for meetings marked "anonymous."*

#### Direction A Deliverable

A single PDF or markdown file containing all five components plus the shared reflection responses below.

</details>

<details markdown="1">
<summary><strong>Direction B: Design Your Agent Operating System</strong></summary>

The two production case studies you read describe an "agent operating system": the written contract, charter, gates, and handoff state that make an AI agent system trustworthy, interruptible, and independent of any single model or vendor. You will author that operating system for a domain of **your** choosing, and then prove it works by interrupting an agent mid-task and letting a second one resume from your documents alone.

#### Step 1: Choose a domain

Any domain with real work and at least one genuinely irreversible action qualifies. It does **not** need to be a software project. Good examples: managing a student organization's communications and files; maintaining a research-notes vault; running a small online shop's catalog; organizing a family photo/document archive; operating a course-project repository; managing a fantasy-sports or gaming community. You may reuse your Project Thread system.

#### Step 2: Author the document set

Starting from the [course templates](https://www.billmongan.com/Ursinus-CS357/files/agent-templates/README.md), produce:

1. **A charter** (`CHARTER.md`): mission (one sentence), a **ranked** priority list (demonstrate the ranking with one concrete conflict it resolves), definition of success, the rules you will actually enforce, at least one milestone with a gate.
2. **An agent contract** (`AGENTS.md` style): the zones of your workspace (what is read-only, what is writable, what is off-limits), write protocols, and maintenance behavior.
3. **A standing prompt** (`SYSTEMPROMPT.md` style): operating habits and, centrally, **confirmation gates rewritten for your domain's irreversible actions**, plus an escalation rule.
4. **Handoff state files** (`.ai/` style): `CURRENT_TASK.md` with completion criteria and a reality-check table, and `SESSION.md` ready to receive entries that end with a next safe action.
5. **An action classification**: at least **ten** realistic actions an agent would take in your domain, classified Autorun / Queue / Forbidden, each with one line of reversibility reasoning.

Delete every template section you cannot honestly enforce, and list what you deleted and why (a rule nobody enforces is worse than no rule). Every gate must earn its place with a concrete failure scenario: the action, the harm, and why after-the-fact recovery is impossible or expensive. At least one forbidden item should carry an argument for why no approval should ever make it safe. Retain the batch-threshold and blanket-consent rules with a domain-specific example, or remove them with a defensible argument.

#### Step 3: Run the handoff walkthrough

Govern a real agent session with your documents (any agent CLI or chat agent from this course works; if your domain has no digital surface an agent can touch, a rigorous simulated transcript is acceptable; mark it as simulated):

1. Start a session; require the agent to read your document set first and restate mission, task, and next action.
2. Give it a task; **interrupt it mid-task**; require it to write the handoff state.
3. Start a **second** session (different agent, different model, or cleared history). Give it only the kickoff/handoff prompt.
4. Record: what it resumed correctly, what it duplicated, and every question it asked that your documents should have answered.

Include the two handoff files verbatim (as updated by session one) and the relevant transcript excerpts.

#### Step 4: Reflect

One page or less: where did the document set hold, where did it leak, which document would rot first under a month of real use, and what one revision or automation does each answer motivate? (Fold these answers into the shared reflection responses below.)

#### Direction B Deliverable

A single PDF or Markdown bundle containing the five documents, the classification table, the walkthrough (files + transcript excerpts), and the reflection. **Anonymize everything**: no real credentials, tokens, personal data, or identifying information about third parties may appear anywhere in the submission; treat this rule as your first Forbidden-lane item.

</details>

---

## Required for Both Directions: Token Ledger Questions

Whichever direction you choose, close your submission with this short worked-theory section: the by-hand budget math from the Tool Use session's token ledger and the Memory and Small Context Window session, applied to *your* designed system. Show your arithmetic; these are graded within the **Verifiability and Evidence** rubric row, because a design whose costs you cannot compute is a design you cannot verify.

1. **Schema overhead.** Your design advertises some number of tools. Using ~80 tokens per schema, compute the per-turn token overhead of your tool menu, and the overhead per turn that is *wasted* on tools the turn does not use in your system's most common workflow. State one design change (e.g., a sub-agent holding some tools, per the Small Context Window principle) and recompute.
2. **Conversation growth.** Assume your system re-sends full history each turn and averages some tokens per exchange (state your estimate and justify it from your prompt skeletons). Compute total tokens *sent* across a 10-turn session (show why the total grows roughly quadratically rather than linearly) and identify the turn at which your chosen model's context window overflows.
3. **The mitigation, priced.** For one mitigation from the memory session (sliding window with a pinned summary, or summarize-and-restart), recompute question 2's total and state what information your system loses in exchange.

## Submission Instructions

Submit a single PDF or markdown bundle containing your chosen direction's deliverable, the token ledger questions, and your reflection responses. State at the top of the first page which direction you chose.

---

## Reflection Prompts

Answer each of the following with a specific observation from this assignment:

1. **Which part of the design changed the most as you worked through it, and why?** Name the component or document that required the most revision, and the assumption you discovered was wrong.
2. **What surprised you most**: the pre-mortem failure you initially believed "could not happen" (Direction A), or the leak your walkthrough exposed in documents you thought were complete (Direction B)? What does that surprise reveal about your initial assumptions?
3. **How would you know the design is actually working?** For Direction A: one week after deployment, what data would you collect, who would collect it, and what would you do if a criterion was not being met? For Direction B: which document do you predict would rot first under a month of real use, and what revision or automation would prevent it?
4. If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you, including any text drafted or revised with an AI tool, with a brief note on how the tool was used.
5. Approximately how many hours did it take you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

## Self-Check Before You Submit

Held against the rubric's `proficient` column. Skip the rows for the direction you did not take.

**Both directions**

- [ ] Every constraint or rule passes the stranger test: someone who has never met me could determine from evidence whether it held.
- [ ] Nothing in the document is a template section I left unadapted; every retained section is unmistakably about my domain.
- [ ] The token ledger questions are answered with arithmetic **shown**, grounded in my own tool count and prompt sizes.
- [ ] The reflection names a specific assumption that changed, a specific leak or surprise, and the revision each motivates.
- [ ] Real names and sensitive data are redacted.

**Direction A**

- [ ] The problem statement answers all four questions: what, for whom, in what context, under what constraints.
- [ ] At least two constraints **limit the system's behavior or data access** rather than describing a desired quality.
- [ ] Every agent row has a distinct role, a three-sentence prompt skeleton (persona and scope, primary task, explicit refusal condition), inputs, outputs, a justified decimal temperature, and tools.
- [ ] The data-flow diagram shows every agent, every handoff **with its data format**, every external call, and every branch labeled with what triggers it.
- [ ] Six or more risks, each naming the agent, the input type, and the output fault; each with an observable detection signal and an action the team could actually take.
- [ ] At least one risk is about contradictory outputs between two agents, and at least one is about user data or privacy.
- [ ] Three to five success criteria, all four columns filled, covering functional correctness plus at least one safety or quality dimension.
- [ ] The reflection says how the data would be collected one week after deployment, by whom, and what happens if a criterion fails.

**Direction B**

- [ ] The charter has a one-sentence mission, a **ranked** priority list, a definition of success, and rules I could actually enforce.
- [ ] The ranking is demonstrated with a concrete conflict it resolves, not merely asserted.
- [ ] Every deleted template section is listed with a one-line reason.
- [ ] Ten or more realistic domain actions classified autorun, queue, or forbidden, with explicit reversibility reasoning.
- [ ] Every gate is justified by a concrete failure scenario: the action, the harm, and why recovery afterwards is impossible or expensive.
- [ ] At least one forbidden item argues why **no** approval could make it safe.
- [ ] The walkthrough interrupts a genuine mid-task moment, not a convenient boundary.
- [ ] `SESSION` and `CURRENT_TASK` are included verbatim, each ending with a next safe action and an evidence-cited reality check.
- [ ] The second session resumed **from the written state alone** and did not redo completed work.
- [ ] Every question the second session had to ask a human is named, along with the document revision that now answers it.
