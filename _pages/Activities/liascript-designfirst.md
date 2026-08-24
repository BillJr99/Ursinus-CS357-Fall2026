<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-designfirst.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-designfirst.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Design First: Plan Before You Build

In *How I AI* you wrote a charter and reviewed a plan before letting an agent act on a single task.  Today we scale both of those to a whole system, and we do it on paper.  In traditional software engineering, the cost of a mistake scales with how late it is discovered: a bug found in code review is cheaper to fix than one found in production.  Agentic systems amplify this principle dramatically.  An agent that sends emails, modifies databases, or calls external APIs can produce **irreversible side effects** within seconds of starting.  If the design was wrong, you may not be able to undo what the agent did.

The **design-first** practice insists that before any code is written or any agent is deployed, you produce a written artifact that answers: *What is each agent trying to do?  What can it touch?  How will we know if it succeeded?  How will we know if it failed?*  This is not bureaucracy.  It is the minimum viable protection against an agent that is confidently wrong at scale.

The discipline of design-first also comes from an older engineering tradition.  Electricians plan their wiring diagrams before pulling wire through conduit: once the walls are closed, changing the circuit is expensive.  The same principle applies here, so plan your ports, your identity directories, and your data flows on paper before any agent sends its first request.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Read each model as a team before tackling the questions.  The Manager keeps discussion moving; the Reflector watches for assumptions the team is making without evidence.  The Recorder documents the team's answers; the Presenter prepares to explain the team's pre-mortem (Model 2) to the class.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Agent Table** | A structured design document with one row per agent, capturing every agent's role, inputs, outputs, tools, temperature setting, and predicted failure mode, filled out before any code is written. | The three-row table in Model 1 describing ResearchAgent, WriterAgent, and CriticAgent. |
| **System Prompt Skeleton** | A draft of the instructions you will give an agent, written at design time to force you to be explicit about what the agent should and should not do. | "You are a research assistant. Search only for peer-reviewed academic sources. Do not fabricate citations." |
| **Temperature** | A number (usually 0.0 to 1.0) that controls how random or creative an AI model's outputs are. Lower temperature means more deterministic (same answer every time); higher temperature means more varied. | CriticAgent uses 0.0 for binary pass/fail judgment; WriterAgent uses 0.7 for creative latitude. |
| **Pre-Mortem** | A technique where a team imagines, before starting work, that the project has already failed, then identifies the most plausible causes of that failure. The goal is to find and fix risks while the cost of changing course is still low. | The six-row table in Model 2 listing component failures and their mitigations. |
| **Adversarial Test Case** | A deliberately flawed or tricky input designed to expose weaknesses in a system, written before the system is built, not after a real failure occurs. | Injecting a draft with known fabricated citations to verify the CriticAgent catches them. |
| **Irreversible Side Effect** | An action taken by an agent that cannot be undone after the fact, such as sending an email, deleting a record, or posting to a public API. | An agent that emails 500 students with incorrect course information; you cannot un-send those emails. |
| **Charter** | The document that decides a project's recurring questions once: mission, **ranked** values, definition of done, and the guardrails no agent may cross. Written from *How I AI*; the agent table below implements it | A charter ranking correctness above speed, which settles "may an agent loosen a test to go faster" without anyone asking |
| **Reversibility Class** | A label on each agent action saying how hard it is to undo: **free** (a file in git), **costly** (a database write with a backup), or **irreversible** (an email, a payment, a public post). Assigned at design time, because you cannot assign it afterwards | The Reversibility column you add to the agent table in Model 1 |
| **Observability, isolation, reversibility** | The three properties that make delegating safe: can I see what it did, can I bound what it reaches, can I undo it. Named in *Your AI Workbench*, applied to notes and projects in *How I AI*, and designed in on purpose today | Every row of the agent table should let you answer all three for that agent |

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Why design first, and what a bad first prompt actually costs |
| 10-40 | Draft your system design: components, contracts, and failure modes |
| 40-65 | Trade drafts and review a teammate's design against the same checklist |
| 65-75 | Revise your own draft with what the review surfaced.  The Extension is self-paced |

---
## Designing for Observability, Isolation, and Reversibility

The agent table below is a good design artifact and it is missing three columns that this course keeps insisting on.  Add them, and the table stops describing what each agent *does* and starts describing what happens when it is wrong.

For **every agent** in your system, before it exists, answer:

| Column | The question | Why it belongs at design time |
|---|---|---|
| **Observed how** | When this agent acts, what record is left, and who reads it? | You cannot bolt logging onto a decision that was never written down. If the answer is "the model explains itself in chat," you have no record |
| **Reaches what** | Exactly which files, services, credentials, and network destinations can this agent touch? | The honest answer is usually wider than the intended answer. Narrowing it costs nothing on paper and is a rewrite once it ships |
| **Undone how** | If this action was wrong, what is the exact undo, and who can perform it? | This is the column that turns "irreversible side effect" from a vocabulary word into a design constraint |

That last column is the one that changes designs.  Work through your system and label each action **free** to undo (a commit in a repository you control), **costly** (a database write you have a backup for, restorable in an hour), or **irreversible** (an email sent, a payment made, a message posted, a record deleted from a system you do not own).

Then apply the rule that follows from the labels: **every irreversible action gets a human gate, and the gate goes in the design, not in a later hardening pass.**  Not because agents are unusually careless, but because "confidently wrong at scale, quickly" is the specific failure mode of this technology, and the only defense that survives contact with a real deployment is that the irreversible step could not happen without someone approving it.

There is a design move worth knowing here: **convert irreversible into reversible before you gate it.**  An agent that sends email is irreversible.  An agent that *drafts* email into a folder, with a human pressing send, is free to undo, and it keeps almost all of the value.  Most irreversible agent actions have a draft-shaped version, and finding it is usually a better answer than adding a confirmation dialog.

Your team designs an agent that files issues in your project's GitHub repository when it finds a bug.  Classify its reversibility and decide whether it needs a gate.

[( )] Irreversible, so it needs a human gate before every filing
[(X)] Costly rather than irreversible: an issue can be closed and edited, but it notified everyone watching the repository and that notification cannot be recalled.  A gate is optional; a rate limit and a label marking it agent-filed are not
[( )] Free, since issues can be deleted
[( )] It depends entirely on how good the model is

    --{{0}}--
The interesting part of this question is the notification.  The artifact is editable, so the state is recoverable; the side effect on other people's attention is not.  A great many agent actions look free when you consider only the data and turn out to be costly when you consider who got pinged.  Ask about both.

---

## Model 1: The Agent Table

In this model you will read a completed agent table for a three-agent research pipeline, then fill in a fourth row from scratch, the fastest way to internalize what information the table is designed to capture before you need it for your own project.

**Why this matters:** "Measure twice, cut once" is the carpenter's version of design-first.  In carpentry, cutting a board too short means buying new wood.  In agentic AI, deploying an agent with a poorly defined role can mean sending incorrect information to thousands of users, corrupting a database, or spending hundreds of dollars on API calls that accomplished nothing useful.  The agent table forces you to articulate every important decision about each agent in writing, before any of those decisions have real consequences.  Empty cells in the table are not gaps in the document; they are unresolved risks in your system.

The **agent table** is the core design artifact for a multi-agent system.  One row per agent.  Before you write a single line of code, you should be able to fill in every cell.  Empty cells are design gaps, which is to say risks waiting to become bugs.

The table below carries the original six columns.  When you build your own for the *Design Your Agent System* assignment, add the three from the section above: **observed how**, **reaches what**, and **undone how**.

| Agent Name | Role and Goal | System Prompt Skeleton | Inputs | Outputs | Temperature | Tools Available | Failure Mode |
|---|---|---|---|---|---|---|---|
| **ResearchAgent** | Find and summarize the top 5 peer-reviewed sources on a given topic, providing structured citations the WriterAgent can use directly. | "You are a research assistant. Search only for peer-reviewed academic sources. Do not fabricate citations. Return structured JSON." | Topic string from the orchestrator, specifying the research question. | JSON list of objects, each with fields: title, authors, year, url, and a one-sentence summary. | 0.2: low temperature for factual precision; we do not want creative variation in citations. | `web_search`, `fetch_url` | Hallucinates a plausible-sounding citation that does not exist at the provided URL. |
| **WriterAgent** | Draft a 500-word section using the research summaries provided by ResearchAgent, with inline citations. | "You are a technical writer. Use only the sources provided. Cite inline. Do not introduce new claims." | JSON research list from ResearchAgent, plus the original topic string. | Markdown text string, approximately 500 words, with inline citations in [Author, Year] format. | 0.7: moderate temperature for some creative latitude in phrasing and structure. | None: text generation only, no tool calls. | Ignores the JSON source list and generates claims from training data, producing confident but unsupported assertions. |
| **CriticAgent** | Evaluate the draft against a rubric and flag any unsupported claims before the output reaches the user. | "You are a fact-checker. For each claim in the draft, identify which source supports it. Flag claims with no source." | Draft markdown from WriterAgent, plus the original research JSON from ResearchAgent. | JSON list of objects, each with fields: claim (quoted from draft), supported_by (source ID or null), and flag (true/false). | 0.0: deterministic; claim support is a binary pass/fail judgment that should not vary across runs. | None: evaluation only, no tool calls. | Passes a hallucinated claim because the confident phrasing sounds plausible, even though no source supports it. |

### Critical Thinking Questions

1.  The system prompt skeleton for ResearchAgent includes "Do not fabricate citations."  Why is this instruction necessary; doesn't the model already "know" citations should be real?  What does this tell us about how system prompts function?

   > *Hint: Think about the difference between knowing a rule in general and following it under pressure.  When a model is "trying to be helpful" and no sources exist, what might it do instead of saying "I don't know"?*

2.  Temperature is set differently for each agent.  WriterAgent has temperature 0.7 while CriticAgent has 0.0.  Explain the reasoning: what would go wrong if their temperatures were swapped?

   > *Hint: Imagine a critic that gives a different verdict each time you run it on the same draft.  Is that useful?  Now imagine a writer that produces the exact same sentence structure every single time.  Is that a problem?*

3.  The "Failure Mode" column is filled in *before* building the system.  What information source are you drawing on when you predict how an agent might fail?  Is this prediction reliable?

   > *Hint: You are not predicting from test data; the system does not exist yet.  What general knowledge about LLMs are you applying?  What kinds of failures are hardest to predict in advance?*

4.  A new agent is needed: a **FormatterAgent** that converts the critic-approved draft into HTML. Fill in a complete row for this agent in your team's Recorder notes.  Be specific about its system prompt skeleton and its failure mode; do not leave any cell as "TBD."

   > *Hint: What should FormatterAgent do if it receives a draft that CriticAgent marked as having unfixed issues?  Should it proceed anyway?  How would you encode that decision in the system prompt?*

In the agent table, WriterAgent runs at temperature 0.7 while CriticAgent runs at 0.0.  The key distinction this encodes is:

[( )] WriterAgent is a larger model, so it can tolerate more randomness
[(X)] Generation benefits from creative variation, but evaluation must be deterministic; a critic that gives different verdicts on identical drafts is useless
[( )] Higher temperature makes WriterAgent's citations more accurate
[( )] Temperature 0.0 disables CriticAgent's tools, which is safer

Complete the design principle: an empty cell in the agent table is not a gap in the document; it is an unresolved [[risk]] waiting to become a bug.

---

With your agent table complete, the next model turns to the question of how those agents can fail, and specifically how to predict failures before they happen, while the cost of changing the design is still low.

## Model 2: The Pre-Mortem

In this model you will work through a six-row pre-mortem table covering every component of the research pipeline, identify one failure mode the table does not yet cover, and add it with all four columns filled in.

**Why this matters:** Most teams think about how their system could fail after it fails.  The pre-mortem technique inverts this: you deliberately imagine failure before it happens, when you still have time to prevent it.  For agentic systems, this is especially important because agents can fail in ways that are hard to detect from the outside: the system appears to run successfully while quietly producing wrong outputs.  A pre-mortem forces you to ask not just "what could go wrong?" but "how would we even know if it went wrong?"

A **pre-mortem** is a technique from project management: before starting a project, the team imagines it is six months in the future and the project has *failed*.  Working backward, they identify the most plausible causes of failure and design mitigations now, while the cost is low.

For agentic systems, the pre-mortem is especially important because agents can fail in ways that are hard to detect, where the system appears to work while producing subtly wrong outputs.

| Component | What Could Go Wrong | How We Would Detect It | Mitigation |
|---|---|---|---|
| **ResearchAgent** | Returns 5 results, but 2 are from predatory journals or retracted papers, polluting the entire pipeline with low-quality sources. | Spot-check a sample of outputs against known databases; CriticAgent flags source quality using a domain whitelist. | Add a `validate_source_credibility` tool; include an approved domain whitelist in the ResearchAgent system prompt. |
| **ResearchAgent** | Context window fills before processing all candidate results, causing the agent to silently truncate its search and return fewer than 5 sources without warning. | Log token counts for every run; compare the output source count against the expected count of 5. | Paginate search results; process in batches with explicit count assertions before returning. |
| **WriterAgent** | Ignores the JSON source list passed as input and writes from its training memory instead, producing confident but unsourced claims. | CriticAgent finds claims with no supporting source; a high flag rate signals this failure. | Instruct WriterAgent to cite inline as it writes each sentence; CriticAgent rejects any draft with more than N flagged claims. |
| **CriticAgent** | Approves everything because it is too agreeable, a failure mode called sycophancy, where the model avoids giving negative feedback. | Inject a known-bad draft with planted fabricated claims and verify that CriticAgent flags them; if it does not, the critic is failing. | Include adversarial test cases in the evaluation suite; compare CriticAgent output against a ground-truth flag list on those cases. |
| **Orchestrator** | Passes outputs between agents out of order or with wrong dictionary keys, causing agents to operate on the wrong data without realizing it. | Type-check and schema-validate every payload at each agent handoff; log all inter-agent messages with timestamps. | Use Pydantic models or JSON Schema to validate every payload structure before passing it to the next agent. |
| **The whole pipeline** | Runs for 45 minutes and produces plausible-looking output that is subtly wrong in ways no single agent caught, because errors compounded across handoffs. | End-to-end human review of a random 10% of outputs; compare cost of review against cost of fully manual research. | Define an evaluation rubric before building; run a blind comparison of agent output versus human-written output on the same topics. |

### Critical Thinking Questions

5.  The pre-mortem row for CriticAgent includes injecting a "known-bad draft" as a test.  This is called an **adversarial test case**.  Why must this test be designed *before* the system is built, and not added later when a real failure is discovered?

   > *Hint: Think about what happens to your objectivity once you have already seen the system run successfully 100 times.  Is it harder or easier to design a truly adversarial test at that point?  Why?*

6.  The last row covers the "whole pipeline" failing in a way no single agent caught.  What property of multi-agent systems makes this kind of failure possible even when each individual agent passes its own tests?

   > *Hint: Think about a game of telephone.  Each person in the chain repeats correctly what they heard, but what happens at the end?  What is the difference between "each step is correct" and "the composition is correct"?*

7.  Identify one failure mode that is *not* in this table but that you believe is plausible given what you know about LLMs.  Add it to the table with all four columns filled in; do not leave any cell empty.

   > *Hint: Consider: what happens if the WriterAgent or CriticAgent receives an unusually long input that approaches its context limit?  What happens if two agents receive slightly different versions of the same source document?*

> **Common Misconception:** Many students treat the pre-mortem as a pessimistic exercise or feel that spending time on it is wasteful when they are eager to start coding.  The opposite is true: the pre-mortem is the most cost-effective work you will do on the project.  Every failure mode you identify and mitigate in writing takes about five minutes to address.  The same failure mode discovered after deployment may take days or weeks to diagnose, and may leave outputs that cannot be recalled or corrected.  Designing for failure is not pessimism; it is professionalism.

A pre-mortem is most useful when it is conducted:

[( )] After the system is deployed, so real failure data informs the analysis
[( )] During the debugging phase, when actual failures have been observed
[(X)] Before building begins, when changing the design is still cheap
[( )] After the first end-to-end test, when the team has hands-on intuition about the system

Every agent in the pipeline passes its own individual tests, yet the end-to-end output is still subtly wrong.  The pre-mortem's key distinction that explains this is:

[( )] Individual tests are unreliable for language models, so passing them means nothing
[( )] The orchestrator must be a larger model than the agents it coordinates
[(X)] Component correctness does not imply composition correctness; errors can compound across handoffs that no single agent's test examines
[( )] Temperature settings drift over the course of a long run

---

The pre-mortem identified what could go wrong; this model shows, week by week, how the consequences of skipping the pre-mortem play out in a real project compared to a team that did the design work upfront.

## Exercises

> Read the six-week timeline below before the next session; it is the narrative version of what you just did on paper.

## Model 3 (At Home): Design-First vs. Code-First - A Six-Week Timeline

In this model you will compare two student teams building the same pipeline on parallel tracks and trace exactly when and why the code-first team's early-saved time is spent back, with interest.

**Why this matters:** The design-first approach is sometimes dismissed as "slowing down" development.  This timeline shows that the total time spent is similar, but *where* the work happens differs dramatically.  Design-first front-loads effort into cheap, reversible planning.  Code-first back-loads the same effort into expensive, disruptive rework.  The question is not whether to do the hard thinking; it is whether to do it on paper or in production.

Two student teams build the same 3-agent research pipeline.  Team A starts coding immediately.  Team B spends the first three days writing a one-page design document (agent table, pre-mortem, data flow diagram, evaluation rubric).

| Milestone | Team A: Code-First | Team B: Design-First |
|---|---|---|
| **Week 1** | ResearchAgent is running, but its output format varies call to call (sometimes JSON, sometimes plain prose) because format was never specified. WriterAgent has not been started yet. | Design document is complete. The agent table contains agreed-upon input/output schemas for all three agents. No code exists yet, but the entire team knows exactly what they are building toward. |
| **Week 2** | WriterAgent is added, but it immediately breaks because ResearchAgent output format is inconsistent. Team A rewrites ResearchAgent to standardize output format. Two days of progress are lost to a problem that could have been decided in 30 minutes on paper. | ResearchAgent and WriterAgent are both implemented against the agreed schema. The first end-to-end run succeeds. A CriticAgent stub is in place for integration next week. |
| **Week 3** | CriticAgent is added. The team discovers they never defined what "a supported claim" means, so the critic's prompt is vague and its output is unreliable. The team spends a full day arguing about the rubric. | CriticAgent is complete and running. The team executes their pre-designed adversarial test cases and discovers that WriterAgent ignores sources approximately 30% of the time. They fix the system prompt and rerun the tests. |
| **Week 4** | Team A runs an end-to-end pipeline for the first time. The output looks reasonable, but they have no rubric to evaluate it against. They ask their instructor "Is this good?" with no quantitative answer available. | Team B runs their full evaluation rubric (defined in the design document) against 20 test outputs. They compute a flag rate and a source accuracy score. They have concrete numbers to report and defend. |
| **Week 5** | Team A discovers their ResearchAgent has been hallucinating citations since Week 1. They have three weeks of pipeline outputs they cannot trust and cannot easily reprocess. | Team B's CriticAgent caught hallucinated citations in Week 3. Their Week 5 outputs are clean, auditable, and backed by a known-good source list. |
| **Week 6** | Team A submits a system that mostly works most of the time. They cannot clearly explain their design choices because those choices were made reactively, under pressure, without documentation. | Team B submits a system with documented design rationale, a working evaluation pipeline, quantified error rates, and a clear audit trail of every decision made. |

### Critical Thinking Questions

8.  Team A lost two days in Week 2 to a schema disagreement they could have resolved in 30 minutes during a design session.  What is the general principle here, and does it apply to non-agentic software projects as well?

   > *Hint: The cost of a decision is the cost of reversing it plus the cost of everything built on top of it before you reversed it.  How does this principle scale with how late the reversal happens?*

9.  In Week 4, Team A asks "Is this good?" but has no rubric to answer the question.  Why is it impossible to evaluate an AI system without criteria that were defined *before* seeing the output?

   > *Hint: If you define "good" after seeing the output, you are at risk of unconsciously defining "good" as "what the system produced."  What is the technical name for this kind of reasoning error in statistics?*

10.  Team B's design document took three days.  Team A saved three days at the start and lost them elsewhere.  What does this suggest about the relationship between upfront design cost and total project cost?  Under what circumstances might Team A's approach actually be *better*?

    > *Hint: Is there any project type where the requirements are so unstable or unknown that writing a design doc first would be wasted effort? What would a project like that look like, and is a 3-agent research pipeline that kind of project?*

---

Having seen what design-first buys you across six weeks, these exercises give you practice writing the artifacts yourself (agent table, pre-mortem, and debate) before you face blank-page paralysis on your final project.


1.  **Write a one-page design document.**

   *What to do:* Choose one of these 2-agent systems: (a) a ticket triage system that classifies support requests and drafts responses, (b) a code review system that reads a pull request diff and flags potential bugs, (c) a meeting summarizer that transcribes audio and extracts action items.  Write a complete agent table with all columns filled in, plus a 5-row pre-mortem using the four-column format from Model 2.

   *Starter hint:* Start by writing down the output of the *last* agent in the pipeline: what does the final user receive?  Work backward from there: what does the second-to-last agent need to produce to enable that output?  Then ask the same question of the first agent.  This backward-from-output approach often reveals design gaps faster than working forward.

   *You've succeeded when:* Every cell in your agent table contains a complete sentence or value, and your pre-mortem includes at least one failure mode that involves agents interacting in an unexpected way, not just individual agents failing in isolation.

2.  **Minimum viable design: a team debate.**

   *What to do:* As a team, debate and agree on the answer to this question: what is the *minimum* design artifact you need before starting to build an agentic system?  What can you skip if you are in a hurry?  Produce a ranked list of design artifacts from "never skip under any circumstances" down to "skip if you are pressed for time."  The Presenter defends the team's top-priority item to the class.

   *Team vote first:* Before any discussion, each member votes silently, **agent table** (structure-first) or **evaluation rubric** (measurement-first), as the single never-skip artifact.  The Recorder tallies the votes and announces the split.  If the vote is not unanimous, the team must reconcile it: each side states the most expensive failure its artifact would have prevented, and the team debates until it agrees on one answer (and records what argument moved the minority).  Only then build the full ranked list.

   *Starter hint:* Consider these candidates: (1) agent table, (2) data flow diagram, (3) pre-mortem, (4) evaluation rubric, (5) system prompt drafts.  Which single artifact, if it were all you had, would prevent the most expensive failures?

   *You've succeeded when:* The team can defend the top item on the list with a concrete example of a catastrophic failure it would have prevented in a real project.

3.  **Evaluate a design document from a previous semester.**

   *What to do:* Your instructor will share a sample design document from a previous semester project.  As a team, apply the pre-mortem technique to it: identify two failure modes the original team missed.  Write each one in the full four-column format from Model 2.

   *Starter hint:* Pay special attention to handoff points between agents: where does one agent's output become another agent's input?  These seams are the most common source of missed failure modes in real design documents.

   *You've succeeded when:* Each of your two identified failure modes has a plausible detection mechanism that is not "run the system and see if it fails"; it should be something you could check proactively, before or during a run.

---

## Reflection Prompt

Respond to all three levels in your notebook:

**Personal:** Describe a personal experience (in software development, in school, or in any other domain) where skipping planning cost you more time than planning would have taken.  What conditions were you in when you made the decision to skip planning?  What conditions would have made you more likely to plan first?

**Technical:** The design-first principle creates a tension with agile development practices, which favor delivering working software quickly over comprehensive documentation.  How would you adapt the agent table and pre-mortem practices to fit a two-week sprint cycle?  What is the minimum version of each artifact that still provides meaningful protection?

**Societal:** Design-first practices were developed in contexts where individual engineers or small teams made design decisions with limited accountability.  In large organizations, design reviews can become bureaucratic gatekeeping that slows innovation without proportionally improving outcomes.  What governance structures would make design-first practices protective rather than performative?

---

-> **Coming Up Next:** The *Orchestration Patterns: Pipelines, Routers, and Planners* activity is next: how the agents you just designed on paper get wired into pipelines, routers, and planner-led workflows.  The design artifacts from today feed directly into Written Assignment 2 and your Final Project's design document.

---

## Further Reading

- Gary Klein.  "Performing a Project Premortem."  *Harvard Business Review* (2007).  The origin of the pre-mortem technique applied here.
- Chip Heath and Dan Heath.  *Decisive: How to Make Better Choices in Life and Work* (2013), Chapter 7.  The "premortem" and "preparade" as decision tools.
- Anthropic.  "Building Effective Agents." https://www.anthropic.com/research/building-effective-agents, the orchestration and agent design patterns section is directly relevant.
- Fred Brooks.  *The Mythical Man-Month* (1975/1995), Chapter 1.  "Plan to throw one away", still the most candid advice about first-system costs.

---

# Extension: Designing Your AI Development Environment (self-paced)

Not required for today's design work, and nothing above assumes it.  Design-first is a discipline you apply once per project; this is the standing infrastructure that makes it stick across projects: context models, AGENTS.md, and instructions that survive a new session and a new machine.

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Agent Memory File** | A plain-text file the agent reads at the start of every session to reconstruct context it cannot remember across sessions: project structure, conventions, what not to do. | `AGENTS.md` in the project root listing architecture and invariants |
| **Project Instructions** | Agent memory scoped to one project: the architecture, key invariants, test commands, and common pitfalls. Lives next to the code it describes. | An `AGENTS.md` for the RAG lab telling the agent "do not modify the Chroma schema" |
| **Global Instructions** | Agent memory that applies to every project you work on: your personal style preferences, preferred libraries, tone. Lives in your home directory or agent config. | `~/.config/opencode/AGENTS.md` containing "always use Black for Python formatting" |
| **Skill** | A reusable prompt template, a named workflow you can invoke by name instead of re-typing the same long prompt. | A "security-review" skill that prompts the agent to check a diff for OWASP top-10 agent risks |
| **Plugin** | A collection of skills and tools packaged together and loaded by the agent at startup via a config file. | The `superpowers` plugin providing pre-built skills for TDD, security audit, and refactoring |
| **Environment as Code** | The principle that your agent config files, instructions files, and skill definitions are version-controlled alongside your source code, so the agent environment is reproducible. | Committing `opencode.json` and `AGENTS.md` to the same repository as the application code |
| **Context Window Hygiene** | The discipline of keeping what goes into the agent's context window purposeful and compact, avoiding bloated instructions that crowd out the actual task. | A 10-line `AGENTS.md` that constrains behavior vs. a 200-line file that describes every method |

---

#### Before You Start

**What you need:** Ollama running locally, and a project folder under git.

**What you will have at the end:** a context setup (instruction file, folder layout, and session habits) that your agent tools read automatically.

Please work through the sections in order.  Each one builds on the last, and the code blocks are there to be run as you reach them.

---

## The Problem of Stateless Agents

In this part, you will diagnose why AI coding agents "forget" your project conventions between sessions and map the three layers of context (working memory, project memory, long-term memory) that a well-designed environment must provide.

### Why Context Does Not Persist

**Why this matters:** Every time you start a new session with a coding agent, you are talking to a version of that agent with no memory of your previous conversations, your project architecture, or your preferences.  This is by design: agent context windows are finite, and persisting all prior work would quickly overflow them.  But it creates a real cost: if you re-explain the same project context at the start of every session, you waste tokens, introduce inconsistencies, and rely on yourself to remember what to say.  Systematic context management is the solution.

**The naive approach** is to paste a block of project context at the start of every prompt: "We are building a RAG system.  The corpus is stored in Chroma.  Do not modify the collection schema.  Tests live in `tests/`.  Run them with `pytest -q`."  This works, but it is fragile: you forget details, the block grows, and different sessions receive different context.

**The systematic approach** is to encode context in files that the agent always reads, so you never have to re-explain.  There are three layers, each scoped appropriately:

| Layer | Where it Lives | What it Contains | Who Writes it |
|-------|----------------|------------------|---------------|
| **Global instructions** | `~/.config/opencode/AGENTS.md` or equivalent home-directory config | Personal style (formatting, preferred libraries, tone) that applies to every project | You, once |
| **Project instructions** | `./AGENTS.md` or `opencode.json` `instructions` field in the project root | Project architecture, key invariants, test commands, what not to do | You, per project |
| **Skills** | Named `.md` files loaded by the agent config | Reusable prompt templates for specific workflows | You or the plugin author |

---

### Matching Context to Layer

A developer is working on the RAG lab from earlier in the course.  They have accumulated the following pieces of context they want the agent to know:

| Context Item | Description |
|---|---|
| A | "Always use Black for Python formatting." |
| B | "The Chroma collection name is `campus`; never delete or recreate it." |
| C | "Run tests with `pytest -q tests/`." |
| D | "Prefer `pathlib.Path` over `os.path` for file operations." |
| E | "The embedding model is `nomic-embed-text` served by Ollama at `localhost:11434`." |

#### Questions to Work Through

1.  For each context item A-E, decide which layer (Global, Project, Skill) is most appropriate.  Justify your answer in one sentence each.

   > *Hint: Ask yourself: would this context apply to a completely different project the developer works on next semester?  If yes, it is global.  If it is specific to this RAG project, it is project-level.  If it describes a repeatable multi-step workflow rather than a fact, it might be a skill.*

2.  What is the cost of putting context item B ("never delete the collection") in the global instructions file instead of the project instructions file?

   > *Hint: The global file is read for every project.  If you start a different project with a different database, the instruction to not delete the `campus` collection in Chroma is irrelevant noise.  What happens to the agent's context window when irrelevant instructions pile up?*

3.  A teammate clones the repository and starts a new agent session.  Which layers of context do they automatically inherit, and which do they need to set up themselves?

   > *Hint: Only files that are version-controlled in the repository are shared when the repo is cloned.  Which of the three layers lives inside the repository?*

> **Common Misconception:** "More context is always better; fill the instructions file with everything you know about the project."  Context window space is finite and shared with the actual task.  An instructions file that lists every class name, every function signature, and the history of every decision crowds out the agent's working space for the current prompt.  Effective instructions describe *constraints and invariants* (what the agent must not do, where things are, and what the conventions are), not a narration of the code.

A developer always wants their coding agent to use Black for Python formatting, regardless of which project they are working on.  Which layer is most appropriate for this instruction?

[( )] Project instructions (`AGENTS.md` in the project root), so it is version-controlled
[(X)] Global instructions (`~/.config/opencode/AGENTS.md`), so it applies to every project automatically
[( )] A skill, so it can be invoked by name when formatting is needed
[( )] The prompt, paste it at the start of every session

---

## Writing Effective Project Instructions

In this part, you will write and critique `AGENTS.md` project instruction files, the persistent context layer that tells a coding agent your architecture, invariants, and out-of-scope changes before it writes a single line.

### What Belongs in `AGENTS.md`

**Why this matters:** An agent that misunderstands your project architecture will make confident, plausible-sounding changes that break invariants you thought were obvious.  The `AGENTS.md` file (or equivalent) is your opportunity to state those invariants explicitly, in a form the agent reads before it does anything.  Think of it as the onboarding document you wish you had written for a new team member who cannot ask questions.

**What belongs in a project instructions file:**

- **Architecture overview** (2-3 sentences per component, not per file): "The ingestion pipeline reads from `data/`, embeds with Ollama, and writes to Chroma.  The query path reads from Chroma only; it never writes."
- **Key invariants the agent must not violate**: "Do not modify the Chroma collection schema.  Do not add new dependencies without updating `requirements.txt`."
- **What is out of scope**: "Do not add a web UI. Do not add authentication.  Do not change the embedding model without a lab-wide discussion."
- **Where the tests are and how to run them**: "Tests live in `tests/`.  Run with `pytest -q`.  All tests must pass before committing."
- **Common pitfalls in this codebase**: "The `embed()` function returns `[]` on failure; callers must check for this.  Do not call `embed()` in a loop without rate-limiting."

---

### A Real Project Instructions File

Below is an example `AGENTS.md` for the RAG lab from earlier in the course.

```markdown
# RAG Lab: Agent Instructions

## Architecture
The system has two phases: indexing (run once, writes to Chroma) and query (run per request,
reads from Chroma). The Chroma client is ephemeral (in-memory); re-running the indexing script
resets it. The embedding model is `nomic-embed-text`; the generation model is `llama3.2`.
Both are served by Ollama at `http://localhost:11434`.

## Invariants
- Do not change the Chroma collection name from `campus`.
- Do not add network calls outside of `embed()` and `chat()`.
- Do not use `eval()`, `exec()`, or `subprocess` anywhere in the codebase.
- All external calls must be wrapped in try/except with traceback logging.

## Out of Scope
- Do not add a web server or HTTP API.
- Do not add authentication.
- Do not change the embedding model without updating this file and all tests.

## Tests
- Location: `tests/`
- Run with: `pytest -q tests/`
- All tests must pass before any commit.
- Do not delete existing tests; only add new ones.

## Common Pitfalls
- `embed()` returns `[]` on failure; callers must raise `RuntimeError`, not return silently.
- Chroma `n_results` must not exceed the collection size; guard with `min(k, col.count())`.
```

#### Questions to Work Through

4.  The instructions file above has 12 substantive lines of constraints.  A teammate suggests expanding it to include a description of every function in the codebase.  What is the argument against that expansion?

   > *Hint: The agent can read the source code directly when it needs to understand a function.  What is the unique value of the instructions file that a code-reading agent cannot get from the source itself?*

5.  The "Common Pitfalls" section mentions that `embed()` returns `[]` on failure.  This is a fact about the current implementation that could become outdated if `embed()` is changed.  What process would you add to ensure the instructions file stays current?

   > *Hint: If the instructions file is version-controlled, what event (a commit, a pull request review, a test failure) could trigger a reminder to update it?  Think about how you keep a README in sync with code.*

6.  The instructions say "Do not use `eval()`, `exec()`, or `subprocess`."  How would you verify that the agent followed this instruction after it made changes?  Write a one-line shell command or `pytest` test that checks for this.

   > *Hint: You do not need to trust the agent's output; you can check the code directly.  The `grep` command can search for patterns in files: `grep -r "eval(" .` returns any line containing `eval(`.  How would you turn this into a `pytest` test using Python's `subprocess.run`?*

> **Common Misconception:** "Project instructions are like a README; describe what the code does."  A README is for humans orienting themselves to a project.  An instructions file is for constraining agent behavior.  The distinction: a README says "this module handles embeddings"; an instructions file says "do not change the embedding model without updating this file."  One describes; the other constrains.  Descriptions help humans understand; constraints prevent agent errors.

Which of the following best belongs in a project instructions file rather than in the source code itself?

[( )] The signature of the `search_memory` function
[( )] The list of all Python files in the project
[(X)] The invariant "do not modify the Chroma collection schema" and how to run the tests
[( )] A copy of the project's git log

---

## Synthesis and Practice

In this part, you will extend your dev environment with the Superpowers plugin for OpenCode and design your own personalized AI environment, choosing which context layers to populate and how to keep them maintained as your project evolves.

### The Superpowers Plugin for OpenCode

**Why this matters:** Writing every skill from scratch is repetitive; common developer workflows like "review this diff for security issues" or "write tests for this function before implementing it" are the same across many projects.  Plugins package pre-built skills that you can load with a single line in your project config, giving the agent a vocabulary of named workflows without requiring you to write the prompt templates yourself.

**OpenCode supports plugins** defined in `opencode.json` at the project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [
    "superpowers@git+https://github.com/obra/superpowers.git"
  ]
}
```

When OpenCode starts, it reads this file, downloads the listed plugins, and makes their skills available by name.  The `superpowers` plugin provides pre-built skills for common developer workflows: the design-TDD-review cycle, security audits, and refactoring patterns.

**Scoping a plugin to one project:** Placing `opencode.json` in the project root (not the home directory) means the plugin is available only when the agent is invoked from that directory.  This prevents a project-specific skill (e.g., one that assumes a Chroma database exists) from being invoked accidentally in an unrelated project.

**Writing your own skill** requires a Markdown file with a structured prompt template.  The file describes what the agent should do when the skill is invoked, what it should look at, and what output it should produce.

---

### A Sample Skill

Below is a `security-review` skill that checks a diff for OWASP top-10 agent risks:

```markdown
# Security Review Skill

You are performing a security review of the diff provided. Check for each of the following
OWASP top-10 risks for LLM-integrated applications:

1. **Prompt Injection**: does any user-supplied string reach a model prompt without sanitization?
2. **Insecure Output Handling**: does any model output reach `eval()`, `exec()`, or a shell?
3. **Excessive Agency**: does the agent take destructive actions (delete, overwrite) without confirmation?
4. **Sensitive Data Exposure**: are API keys, tokens, or PII logged or returned to the user?
5. **Unbounded Resource Consumption**: are there loops or queries with no upper bound?

For each risk, state: FOUND / NOT FOUND / CANNOT DETERMINE, with a one-line explanation.
If any risk is FOUND, suggest the minimal fix.

Review the most recent diff provided by the user.
```

#### Questions to Work Through

7.  Why is it better to install the `superpowers` plugin in `./opencode.json` (project root) rather than a global config file in the home directory?

   > *Hint: The `superpowers` plugin includes skills that assume specific project structures (a Chroma database, a `tests/` directory, a `pytest` test runner).  If these skills are available globally, what happens when you invoke the "design-TDD-review" skill in a project that uses a different database and a different test framework?*

8.  The security-review skill above checks for five specific risks.  A teammate argues: "A good skill should be general; check for *all* security issues, not just these five."  What is the argument on the other side?

   > *Hint: A skill that says "check for all security issues" gives the agent no guidance about what to look for or how to report.  What does specificity in a prompt template give you that generality does not?*

9.  Suppose you want to write a skill for the final project in this course (an agent team or RAG system).  Write the first two lines of the skill's Markdown file: the skill name (as an H1) and the first sentence of the agent instruction.

   > *Hint: The first sentence should tell the agent what role it is playing and what it is about to review.  Look at the security-review skill above: it opens with "You are performing a security review of the diff provided."  What is the analogous opening for a skill that reviews a RAG system's retrieval quality?*

> **Common Misconception:** "A skill is just a shortcut for typing a long prompt."  A skill is a *reusable contract*: it defines what the agent will examine, what it will report, and in what format.  Because it is version-controlled and shared with the team, everyone's agent invokes the same workflow.  The reproducibility is the value, not just the typing saved.

Why is it preferable to install a project-specific plugin in `./opencode.json` rather than the global agent configuration?

[( )] The global configuration file has a size limit that project configs do not
[( )] Skills defined in the project config run faster than globally installed ones
[(X)] Skills in the project config are only available when working in that project, preventing them from being invoked incorrectly in unrelated projects
[( )] The global config does not support the `plugin` field

---

### Exercises

1.  *Write a 10-line project instructions file.*

   - *What to do:* Choose a project you have worked on this semester (the RAG lab, the prompt engineering lab, or a personal project).  Write an `AGENTS.md` file with at most 10 lines covering: one architecture sentence, three invariants, one "out of scope" statement, and the test command.  Then start a fresh agent session with and without the file and compare the agent's first response to a task prompt.
   - *Starter hint:* Keep each invariant to a single sentence beginning with "Do not" or "Always."  Architecture sentences should name components and the direction of data flow, not list files.  Test command should be copy-paste runnable.
   - *You've succeeded when:* You can show that a fresh agent session with `AGENTS.md` present correctly names the test command, the forbidden operation, and the component that handles embedding, without you mentioning any of these in the prompt.

2.  *Write a skill for retrieval quality review.*

   - *What to do:* Write a skill Markdown file called `retrieval-review.md` that instructs a coding agent to review a RAG system's retrieval results.  The skill should ask the agent to check: (a) whether the retrieved chunks are topically relevant to the query, (b) whether any crucial chunk was missed (false negative), and (c) whether any irrelevant chunk was retrieved (false positive).  The skill should produce a structured report with GOOD / PROBLEM / UNCERTAIN for each criterion.
   - *Starter hint:* Start with a role sentence ("You are reviewing the retrieval results of a RAG system"), then list the three criteria as numbered items, then specify the output format.  Keep it under 15 lines.
   - *You've succeeded when:* You can invoke the skill on a sample query-result pair from the RAG lab and the agent produces a structured report that correctly identifies at least one retrieval problem in your test case.

3.  *The meta-loop: improve your own environment.*

   - *What to do:* Identify one repeated pattern in your recent agent sessions: a piece of context you re-explain every session, a task you re-describe every time, or a format you always ask for.  Encode it as either (a) an addition to `AGENTS.md`, (b) a new skill, or (c) a global instruction.  Test the encoded version by starting a fresh session and checking whether the agent gets it right without being told.
   - *Starter hint:* Good candidates for encoding: "always print the retrieved context before the answer," "always run `pytest -q` after making changes," "always include a one-line summary of what changed at the top of your response."  Pick the one you re-type most often.
   - *You've succeeded when:* You can demonstrate a fresh session in which the agent exhibits the desired behavior without any explicit instruction in the prompt, and you can point to the file that produced that behavior.

4.  *Design the environment for the final project.*

   - *What to do:* Design (do not fully implement) the complete agent environment for the final project in this course, an agent team or a RAG system.  Produce: (a) a 10-line `AGENTS.md`, (b) a list of three skills you would want pre-built, and (c) an `opencode.json` that loads the `superpowers` plugin.  Justify each item in one sentence.
   - *Starter hint:* The `AGENTS.md` should cover the multi-agent architecture (which agent does what), the key invariants (what each agent must not do), and the test command.  The three skills should cover the three most repeated tasks, likely: run the full evaluation, review a new agent's tool for security issues, and summarize the agent team's latest output.
   - *You've succeeded when:* You can hand your environment design to a teammate and they can, without asking you any questions, start a fresh agent session and correctly describe the project architecture, run the tests, and invoke a skill by name.

---

### Reflection Prompt

*Personal:* Identify one repeated prompt you have typed more than three times in this course's agent sessions: a context explanation, a formatting request, or a task description.  Would you encode it as a global instruction, a project instruction, or a skill?  Why that layer?

*Technical:* In your notebook: how does "environment as code" differ from a project README? A README is also a text file that describes the project.  What does version-controlling `AGENTS.md` and `opencode.json` give you that version-controlling only a README does not?

*Societal:* Your `AGENTS.md` encodes invariants ("do not modify the database schema") and your global instructions encode preferences ("prefer functional style").  These reflect your assumptions and values.  Who should review those files, and should they be subject to the same code review process as the source code?  Identify one assumption you have already encoded and argue whether it should be visible to collaborators or kept private.

---
