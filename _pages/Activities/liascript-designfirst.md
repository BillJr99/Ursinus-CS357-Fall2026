<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-designfirst.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-designfirst.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Design First: Plan Before You Build

In the *Studio: Local Agent Stack Clinic* session you stood up a working local stack; before we build anything more ambitious on top of it, we learn to plan on paper. In traditional software engineering, the cost of a mistake scales with how late it is discovered: a bug found in code review is cheaper to fix than one found in production. Agentic systems amplify this principle dramatically. An agent that sends emails, modifies databases, or calls external APIs can produce **irreversible side effects** within seconds of starting. If the design was wrong, you may not be able to undo what the agent did.

The **design-first** practice insists that before any code is written or any agent is deployed, you produce a written artifact that answers: *What is each agent trying to do? What can it touch? How will we know if it succeeded? How will we know if it failed?* This is not bureaucracy - it is the minimum viable protection against an agent that is confidently wrong at scale.

The discipline of design-first also comes from an older engineering tradition. Electricians plan their wiring diagrams before pulling wire through conduit: once the walls are closed, changing the circuit is expensive. The same principle applies here - plan your ports, your identity directories, and your data flows on paper before any agent sends its first request.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Read each model as a team before tackling the questions. The Manager keeps discussion moving; the Reflector watches for assumptions the team is making without evidence. The Recorder documents the team's answers; the Presenter prepares to explain the team's pre-mortem (Model 2) to the class.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Agent Table** | A structured design document with one row per agent, capturing every agent's role, inputs, outputs, tools, temperature setting, and predicted failure mode — filled out before any code is written. | The three-row table in Model 1 describing ResearchAgent, WriterAgent, and CriticAgent. |
| **System Prompt Skeleton** | A draft of the instructions you will give an agent, written at design time to force you to be explicit about what the agent should and should not do. | "You are a research assistant. Search only for peer-reviewed academic sources. Do not fabricate citations." |
| **Temperature** | A number (usually 0.0 to 1.0) that controls how random or creative an AI model's outputs are. Lower temperature means more deterministic (same answer every time); higher temperature means more varied. | CriticAgent uses 0.0 for binary pass/fail judgment; WriterAgent uses 0.7 for creative latitude. |
| **Pre-Mortem** | A technique where a team imagines, before starting work, that the project has already failed, then identifies the most plausible causes of that failure. The goal is to find and fix risks while the cost of changing course is still low. | The six-row table in Model 2 listing component failures and their mitigations. |
| **Adversarial Test Case** | A deliberately flawed or tricky input designed to expose weaknesses in a system — written before the system is built, not after a real failure occurs. | Injecting a draft with known fabricated citations to verify the CriticAgent catches them. |
| **Irreversible Side Effect** | An action taken by an agent that cannot be undone after the fact, such as sending an email, deleting a record, or posting to a public API. | An agent that emails 500 students with incorrect course information — you cannot un-send those emails. |

---

## Model 1: The Agent Table

In this model you will read a completed agent table for a three-agent research pipeline, then fill in a fourth row from scratch — the fastest way to internalize what information the table is designed to capture before you need it for your own project.

**Why this matters:** "Measure twice, cut once" is the carpenter's version of design-first. In carpentry, cutting a board too short means buying new wood. In agentic AI, deploying an agent with a poorly defined role can mean sending incorrect information to thousands of users, corrupting a database, or spending hundreds of dollars on API calls that accomplished nothing useful. The agent table forces you to articulate every important decision about each agent in writing, before any of those decisions have real consequences. Empty cells in the table are not gaps in the document — they are unresolved risks in your system.

The **agent table** is the core design artifact for a multi-agent system. One row per agent. Before you write a single line of code, you should be able to fill in every cell. Empty cells are design gaps - risks waiting to become bugs.

| Agent Name | Role and Goal | System Prompt Skeleton | Inputs | Outputs | Temperature | Tools Available | Failure Mode |
|---|---|---|---|---|---|---|---|
| **ResearchAgent** | Find and summarize the top 5 peer-reviewed sources on a given topic, providing structured citations the WriterAgent can use directly. | "You are a research assistant. Search only for peer-reviewed academic sources. Do not fabricate citations. Return structured JSON." | Topic string from the orchestrator, specifying the research question. | JSON list of objects, each with fields: title, authors, year, url, and a one-sentence summary. | 0.2 — low temperature for factual precision; we do not want creative variation in citations. | `web_search`, `fetch_url` | Hallucinates a plausible-sounding citation that does not exist at the provided URL. |
| **WriterAgent** | Draft a 500-word section using the research summaries provided by ResearchAgent, with inline citations. | "You are a technical writer. Use only the sources provided. Cite inline. Do not introduce new claims." | JSON research list from ResearchAgent, plus the original topic string. | Markdown text string, approximately 500 words, with inline citations in [Author, Year] format. | 0.7 — moderate temperature for some creative latitude in phrasing and structure. | None — text generation only, no tool calls. | Ignores the JSON source list and generates claims from training data, producing confident but unsupported assertions. |
| **CriticAgent** | Evaluate the draft against a rubric and flag any unsupported claims before the output reaches the user. | "You are a fact-checker. For each claim in the draft, identify which source supports it. Flag claims with no source." | Draft markdown from WriterAgent, plus the original research JSON from ResearchAgent. | JSON list of objects, each with fields: claim (quoted from draft), supported_by (source ID or null), and flag (true/false). | 0.0 — deterministic; claim support is a binary pass/fail judgment that should not vary across runs. | None — evaluation only, no tool calls. | Passes a hallucinated claim because the confident phrasing sounds plausible, even though no source supports it. |

### Critical Thinking Questions

1. The system prompt skeleton for ResearchAgent includes "Do not fabricate citations." Why is this instruction necessary — doesn't the model already "know" citations should be real? What does this tell us about how system prompts function?

   > *Hint: Think about the difference between knowing a rule in general and following it under pressure. When a model is "trying to be helpful" and no sources exist, what might it do instead of saying "I don't know"?*

2. Temperature is set differently for each agent. WriterAgent has temperature 0.7 while CriticAgent has 0.0. Explain the reasoning: what would go wrong if their temperatures were swapped?

   > *Hint: Imagine a critic that gives a different verdict each time you run it on the same draft. Is that useful? Now imagine a writer that produces the exact same sentence structure every single time. Is that a problem?*

3. The "Failure Mode" column is filled in *before* building the system. What information source are you drawing on when you predict how an agent might fail? Is this prediction reliable?

   > *Hint: You are not predicting from test data — the system does not exist yet. What general knowledge about LLMs are you applying? What kinds of failures are hardest to predict in advance?*

4. A new agent is needed: a **FormatterAgent** that converts the critic-approved draft into HTML. Fill in a complete row for this agent in your team's Recorder notes. Be specific about its system prompt skeleton and its failure mode — do not leave any cell as "TBD."

   > *Hint: What should FormatterAgent do if it receives a draft that CriticAgent marked as having unfixed issues? Should it proceed anyway? How would you encode that decision in the system prompt?*

In the agent table, WriterAgent runs at temperature 0.7 while CriticAgent runs at 0.0. The key distinction this encodes is:

[( )] WriterAgent is a larger model, so it can tolerate more randomness
[(X)] Generation benefits from creative variation, but evaluation must be deterministic — a critic that gives different verdicts on identical drafts is useless
[( )] Higher temperature makes WriterAgent's citations more accurate
[( )] Temperature 0.0 disables CriticAgent's tools, which is safer

Complete the design principle: an empty cell in the agent table is not a gap in the document — it is an unresolved [[risk]] waiting to become a bug.

---

With your agent table complete, the next model turns to the question of how those agents can fail — and specifically how to predict failures before they happen, while the cost of changing the design is still low.

## Model 2: The Pre-Mortem

In this model you will work through a six-row pre-mortem table covering every component of the research pipeline, identify one failure mode the table does not yet cover, and add it with all four columns filled in.

**Why this matters:** Most teams think about how their system could fail after it fails. The pre-mortem technique inverts this: you deliberately imagine failure before it happens, when you still have time to prevent it. For agentic systems, this is especially important because agents can fail in ways that are hard to detect from the outside — the system appears to run successfully while quietly producing wrong outputs. A pre-mortem forces you to ask not just "what could go wrong?" but "how would we even know if it went wrong?"

A **pre-mortem** is a technique from project management: before starting a project, the team imagines it is six months in the future and the project has *failed*. Working backward, they identify the most plausible causes of failure and design mitigations now, while the cost is low.

For agentic systems, the pre-mortem is especially important because agents can fail in ways that are hard to detect - the system appears to work while producing subtly wrong outputs.

| Component | What Could Go Wrong | How We Would Detect It | Mitigation |
|---|---|---|---|
| **ResearchAgent** | Returns 5 results, but 2 are from predatory journals or retracted papers, polluting the entire pipeline with low-quality sources. | Spot-check a sample of outputs against known databases; CriticAgent flags source quality using a domain whitelist. | Add a `validate_source_credibility` tool; include an approved domain whitelist in the ResearchAgent system prompt. |
| **ResearchAgent** | Context window fills before processing all candidate results, causing the agent to silently truncate its search and return fewer than 5 sources without warning. | Log token counts for every run; compare the output source count against the expected count of 5. | Paginate search results; process in batches with explicit count assertions before returning. |
| **WriterAgent** | Ignores the JSON source list passed as input and writes from its training memory instead, producing confident but unsourced claims. | CriticAgent finds claims with no supporting source; a high flag rate signals this failure. | Instruct WriterAgent to cite inline as it writes each sentence; CriticAgent rejects any draft with more than N flagged claims. |
| **CriticAgent** | Approves everything because it is too agreeable — a failure mode called sycophancy, where the model avoids giving negative feedback. | Inject a known-bad draft with planted fabricated claims and verify that CriticAgent flags them; if it does not, the critic is failing. | Include adversarial test cases in the evaluation suite; compare CriticAgent output against a ground-truth flag list on those cases. |
| **Orchestrator** | Passes outputs between agents out of order or with wrong dictionary keys, causing agents to operate on the wrong data without realizing it. | Type-check and schema-validate every payload at each agent handoff; log all inter-agent messages with timestamps. | Use Pydantic models or JSON Schema to validate every payload structure before passing it to the next agent. |
| **The whole pipeline** | Runs for 45 minutes and produces plausible-looking output that is subtly wrong in ways no single agent caught, because errors compounded across handoffs. | End-to-end human review of a random 10% of outputs; compare cost of review against cost of fully manual research. | Define an evaluation rubric before building; run a blind comparison of agent output versus human-written output on the same topics. |

### Critical Thinking Questions

5. The pre-mortem row for CriticAgent includes injecting a "known-bad draft" as a test. This is called an **adversarial test case**. Why must this test be designed *before* the system is built, and not added later when a real failure is discovered?

   > *Hint: Think about what happens to your objectivity once you have already seen the system run successfully 100 times. Is it harder or easier to design a truly adversarial test at that point? Why?*

6. The last row covers the "whole pipeline" failing in a way no single agent caught. What property of multi-agent systems makes this kind of failure possible even when each individual agent passes its own tests?

   > *Hint: Think about a game of telephone. Each person in the chain repeats correctly what they heard — but what happens at the end? What is the difference between "each step is correct" and "the composition is correct"?*

7. Identify one failure mode that is *not* in this table but that you believe is plausible given what you know about LLMs. Add it to the table with all four columns filled in — do not leave any cell empty.

   > *Hint: Consider: what happens if the WriterAgent or CriticAgent receives an unusually long input that approaches its context limit? What happens if two agents receive slightly different versions of the same source document?*

> **Common Misconception:** Many students treat the pre-mortem as a pessimistic exercise or feel that spending time on it is wasteful when they are eager to start coding. The opposite is true: the pre-mortem is the most cost-effective work you will do on the project. Every failure mode you identify and mitigate in writing takes about five minutes to address. The same failure mode discovered after deployment may take days or weeks to diagnose, and may leave outputs that cannot be recalled or corrected. Designing for failure is not pessimism — it is professionalism.

A pre-mortem is most useful when it is conducted:

[( )] After the system is deployed, so real failure data informs the analysis
[( )] During the debugging phase, when actual failures have been observed
[(X)] Before building begins, when changing the design is still cheap
[( )] After the first end-to-end test, when the team has hands-on intuition about the system

Every agent in the pipeline passes its own individual tests, yet the end-to-end output is still subtly wrong. The pre-mortem's key distinction that explains this is:

[( )] Individual tests are unreliable for language models, so passing them means nothing
[( )] The orchestrator must be a larger model than the agents it coordinates
[(X)] Component correctness does not imply composition correctness — errors can compound across handoffs that no single agent's test examines
[( )] Temperature settings drift over the course of a long run

---

The pre-mortem identified what could go wrong; this model shows, week by week, how the consequences of skipping the pre-mortem play out in a real project compared to a team that did the design work upfront.

## Exercises

> Read the six-week timeline below before the next session; it is the narrative version of what you just did on paper.

## Model 3 (At Home): Design-First vs. Code-First — A Six-Week Timeline

In this model you will compare two student teams building the same pipeline on parallel tracks and trace exactly when and why the code-first team's early-saved time is spent back — with interest.

**Why this matters:** The design-first approach is sometimes dismissed as "slowing down" development. This timeline shows that the total time spent is similar, but *where* the work happens differs dramatically. Design-first front-loads effort into cheap, reversible planning. Code-first back-loads the same effort into expensive, disruptive rework. The question is not whether to do the hard thinking — it is whether to do it on paper or in production.

Two student teams build the same 3-agent research pipeline. Team A starts coding immediately. Team B spends the first three days writing a one-page design document (agent table, pre-mortem, data flow diagram, evaluation rubric).

| Milestone | Team A: Code-First | Team B: Design-First |
|---|---|---|
| **Week 1** | ResearchAgent is running, but its output format varies call to call — sometimes JSON, sometimes plain prose — because format was never specified. WriterAgent has not been started yet. | Design document is complete. The agent table contains agreed-upon input/output schemas for all three agents. No code exists yet, but the entire team knows exactly what they are building toward. |
| **Week 2** | WriterAgent is added, but it immediately breaks because ResearchAgent output format is inconsistent. Team A rewrites ResearchAgent to standardize output format. Two days of progress are lost to a problem that could have been decided in 30 minutes on paper. | ResearchAgent and WriterAgent are both implemented against the agreed schema. The first end-to-end run succeeds. A CriticAgent stub is in place for integration next week. |
| **Week 3** | CriticAgent is added. The team discovers they never defined what "a supported claim" means, so the critic's prompt is vague and its output is unreliable. The team spends a full day arguing about the rubric. | CriticAgent is complete and running. The team executes their pre-designed adversarial test cases and discovers that WriterAgent ignores sources approximately 30% of the time. They fix the system prompt and rerun the tests. |
| **Week 4** | Team A runs an end-to-end pipeline for the first time. The output looks reasonable, but they have no rubric to evaluate it against. They ask their instructor "Is this good?" with no quantitative answer available. | Team B runs their full evaluation rubric — defined in the design document — against 20 test outputs. They compute a flag rate and a source accuracy score. They have concrete numbers to report and defend. |
| **Week 5** | Team A discovers their ResearchAgent has been hallucinating citations since Week 1. They have three weeks of pipeline outputs they cannot trust and cannot easily reprocess. | Team B's CriticAgent caught hallucinated citations in Week 3. Their Week 5 outputs are clean, auditable, and backed by a known-good source list. |
| **Week 6** | Team A submits a system that mostly works most of the time. They cannot clearly explain their design choices because those choices were made reactively, under pressure, without documentation. | Team B submits a system with documented design rationale, a working evaluation pipeline, quantified error rates, and a clear audit trail of every decision made. |

### Critical Thinking Questions

8. Team A lost two days in Week 2 to a schema disagreement they could have resolved in 30 minutes during a design session. What is the general principle here, and does it apply to non-agentic software projects as well?

   > *Hint: The cost of a decision is the cost of reversing it plus the cost of everything built on top of it before you reversed it. How does this principle scale with how late the reversal happens?*

9. In Week 4, Team A asks "Is this good?" but has no rubric to answer the question. Why is it impossible to evaluate an AI system without criteria that were defined *before* seeing the output?

   > *Hint: If you define "good" after seeing the output, you are at risk of unconsciously defining "good" as "what the system produced." What is the technical name for this kind of reasoning error in statistics?*

10. Team B's design document took three days. Team A saved three days at the start and lost them elsewhere. What does this suggest about the relationship between upfront design cost and total project cost? Under what circumstances might Team A's approach actually be *better*?

    > *Hint: Is there any project type where the requirements are so unstable or unknown that writing a design doc first would be wasted effort? What would a project like that look like, and is a 3-agent research pipeline that kind of project?*

---

Having seen what design-first buys you across six weeks, these exercises give you practice writing the artifacts yourself — agent table, pre-mortem, and debate — before you face blank-page paralysis on your final project.


1. **Write a one-page design document.**

   *What to do:* Choose one of these 2-agent systems: (a) a ticket triage system that classifies support requests and drafts responses, (b) a code review system that reads a pull request diff and flags potential bugs, (c) a meeting summarizer that transcribes audio and extracts action items. Write a complete agent table with all columns filled in, plus a 5-row pre-mortem using the four-column format from Model 2.

   *Starter hint:* Start by writing down the output of the *last* agent in the pipeline — what does the final user receive? Work backward from there: what does the second-to-last agent need to produce to enable that output? Then ask the same question of the first agent. This backward-from-output approach often reveals design gaps faster than working forward.

   *You've succeeded when:* Every cell in your agent table contains a complete sentence or value, and your pre-mortem includes at least one failure mode that involves agents interacting in an unexpected way — not just individual agents failing in isolation.

2. **Minimum viable design — a team debate.**

   *What to do:* As a team, debate and agree on the answer to this question: what is the *minimum* design artifact you need before starting to build an agentic system? What can you skip if you are in a hurry? Produce a ranked list of design artifacts from "never skip under any circumstances" down to "skip if genuinely pressed for time." The Presenter defends the team's top-priority item to the class.

   *Team vote first:* Before any discussion, each member votes silently — **agent table** (structure-first) or **evaluation rubric** (measurement-first) — as the single never-skip artifact. The Recorder tallies the votes and announces the split. If the vote is not unanimous, the team must reconcile it: each side states the most expensive failure its artifact would have prevented, and the team debates until it agrees on one answer (and records what argument moved the minority). Only then build the full ranked list.

   *Starter hint:* Consider these candidates: (1) agent table, (2) data flow diagram, (3) pre-mortem, (4) evaluation rubric, (5) system prompt drafts. Which single artifact, if it were all you had, would prevent the most expensive failures?

   *You've succeeded when:* The team can defend the top item on the list with a concrete example of a catastrophic failure it would have prevented in a real project.

3. **Evaluate a design document from a previous semester.**

   *What to do:* Your instructor will share a sample design document from a previous semester project. As a team, apply the pre-mortem technique to it: identify two failure modes the original team missed. Write each one in the full four-column format from Model 2.

   *Starter hint:* Pay special attention to handoff points between agents — where does one agent's output become another agent's input? These seams are the most common source of missed failure modes in real design documents.

   *You've succeeded when:* Each of your two identified failure modes has a plausible detection mechanism that is not "run the system and see if it fails" — it should be something you could check proactively, before or during a run.

---

## Reflection Prompt

Respond to all three levels in your notebook:

**Personal:** Describe a personal experience — in software development, in school, or in any other domain — where skipping planning cost you more time than planning would have taken. What conditions were you in when you made the decision to skip planning? What conditions would have made you more likely to plan first?

**Technical:** The design-first principle creates a tension with agile development practices, which favor delivering working software quickly over comprehensive documentation. How would you adapt the agent table and pre-mortem practices to fit a two-week sprint cycle? What is the minimum version of each artifact that still provides meaningful protection?

**Societal:** Design-first practices were developed in contexts where individual engineers or small teams made design decisions with limited accountability. In large organizations, design reviews can become bureaucratic gatekeeping that slows innovation without proportionally improving outcomes. What governance structures would make design-first practices genuinely protective rather than performative?

---

-> **Coming Up Next:** The *Orchestration Patterns: Pipelines, Routers, and Planners* activity is next — how the agents you just designed on paper get wired into pipelines, routers, and planner-led workflows. The design artifacts from today feed directly into Written Assignment 2 and your Final Project's design document.

---

## Further Reading

- Gary Klein. "Performing a Project Premortem." *Harvard Business Review* (2007). The origin of the pre-mortem technique applied here.
- Chip Heath and Dan Heath. *Decisive: How to Make Better Choices in Life and Work* (2013), Chapter 7. The "premortem" and "preparade" as decision tools.
- Anthropic. "Building Effective Agents." https://www.anthropic.com/research/building-effective-agents — the orchestration and agent design patterns section is directly relevant.
- Fred Brooks. *The Mythical Man-Month* (1975/1995), Chapter 1. "Plan to throw one away" — still the most candid advice about first-system costs.
