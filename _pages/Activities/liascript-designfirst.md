# Design First: Plan Before You Build
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

In traditional software engineering, the cost of a mistake scales with how late it is discovered: a bug found in code review is cheaper to fix than one found in production. Agentic systems amplify this principle dramatically. An agent that sends emails, modifies databases, or calls external APIs can produce **irreversible side effects** within seconds of starting. If the design was wrong, you may not be able to undo what the agent did.

The **design-first** practice insists that before any code is written or any agent is deployed, you produce a written artifact that answers: *What is each agent trying to do? What can it touch? How will we know if it succeeded? How will we know if it failed?* This is not bureaucracy - it is the minimum viable protection against an agent that is confidently wrong at scale.

The discipline of design-first also comes from an older engineering tradition. Electricians plan their wiring diagrams before pulling wire through conduit: once the walls are closed, changing the circuit is expensive. The same principle applies here - plan your ports, your identity directories, and your data flows on paper before any agent sends its first request.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Read each model as a team before tackling the questions. The Manager keeps discussion moving; the Reflector watches for assumptions the team is making without evidence. The Recorder documents the team's answers; the Presenter prepares to explain the team's pre-mortem (Model 2) to the class.

---

## Model 1: The Agent Table

The **agent table** is the core design artifact for a multi-agent system. One row per agent. Before you write a single line of code, you should be able to fill in every cell. Empty cells are design gaps - risks waiting to become bugs.

| Agent Name | Role / Goal | System Prompt Skeleton | Inputs | Outputs | Temperature | Tools Available | Failure Mode |
|---|---|---|---|---|---|---|---|
| *(example)* ResearchAgent | Find and summarize the top 5 peer-reviewed sources on a given topic | "You are a research assistant. Search only for peer-reviewed academic sources. Do not fabricate citations. Return structured JSON." | Topic string from orchestrator | JSON list of {title, authors, year, url, 1-sentence summary} | 0.2 (low: we want factual precision) | `web_search`, `fetch_url` | Hallucinates a plausible-sounding citation that does not exist |
| *(example)* WriterAgent | Draft a 500-word section using the research summaries | "You are a technical writer. Use only the sources provided. Cite inline. Do not introduce new claims." | JSON research list from ResearchAgent | Markdown text string | 0.7 (moderate: some creative latitude) | *(none - text only)* | Ignores the source list and generates claims from training data |
| *(example)* CriticAgent | Evaluate the draft against a rubric; flag unsupported claims | "You are a fact-checker. For each claim in the draft, identify which source supports it. Flag claims with no source." | Draft markdown + original research JSON | JSON list of {claim, supported\_by, flag} | 0.0 (deterministic: binary pass/fail per claim) | *(none)* | Passes a hallucinated claim because it sounds plausible |

### Critical Thinking Questions

1. The system prompt skeleton for ResearchAgent includes "Do not fabricate citations." Why is this instruction necessary - doesn't the model already "know" citations should be real? What does this tell us about how system prompts function?
2. Temperature is set differently for each agent. WriterAgent has temperature 0.7 while CriticAgent has 0.0. Explain the reasoning: what would go wrong if their temperatures were swapped?
3. The "Failure Mode" column is filled in *before* building the system. What information source are you drawing on when you predict how an agent might fail? Is this prediction reliable?
4. A new agent is needed: a **FormatterAgent** that converts the critic-approved draft into HTML. Fill in a complete row for this agent in your team's Recorder notes. Be specific about its system prompt skeleton and its failure mode.

---

## Model 2: The Pre-Mortem

A **pre-mortem** is a technique from project management: before starting a project, the team imagines it is six months in the future and the project has *failed*. Working backward, they identify the most plausible causes of failure and design mitigations now, while the cost is low.

For agentic systems, the pre-mortem is especially important because agents can fail in ways that are hard to detect - the system appears to work while producing subtly wrong outputs.

| Component | What Could Go Wrong | How We Would Detect It | Mitigation |
|---|---|---|---|
| **ResearchAgent** | Returns 5 results, but 2 are from predatory journals or retracted papers | Spot-check sample outputs against known databases; CriticAgent flags source quality | Add `validate_source_credibility` tool; include domain whitelist in system prompt |
| **ResearchAgent** | Context window fills before processing all candidate results; silently truncates | Log token counts per run; compare output count to expected count | Paginate search results; process in batches with explicit count assertions |
| **WriterAgent** | Ignores the JSON source list passed as input, writes from memory instead | CriticAgent finds claims with no supporting source; high flag rate | Instruct WriterAgent to cite inline as it writes; CriticAgent rejects drafts with >N flagged claims |
| **CriticAgent** | Approves everything because it is too agreeable (sycophancy) | Inject a known-bad draft with fabricated claims; verify CriticAgent flags them | Include adversarial test cases in evaluation suite; compare against a ground-truth flag list |
| **Orchestrator** | Passes outputs between agents out of order or with wrong keys | Type-check and schema-validate at each handoff; log all inter-agent messages | Use Pydantic models or JSON Schema to validate every payload before passing |
| **The whole pipeline** | Runs for 45 minutes and produces plausible-looking output that is subtly wrong in ways no single agent caught | End-to-end human review of a random 10% of outputs; compare cost vs. manual research | Define evaluation rubric before building; run blind comparison of agent output vs. human researcher |

### Critical Thinking Questions

5. The pre-mortem row for CriticAgent includes injecting a "known-bad draft" as a test. This is called an **adversarial test case**. Why must this test be designed *before* the system is built, and not added later when a real failure is discovered?
6. The last row covers the "whole pipeline" failing in a way no single agent caught. What property of multi-agent systems makes this kind of failure possible even when each individual agent passes its own tests?
7. Identify one failure mode that is *not* in this table but that you believe is plausible given what you know about LLMs. Add it to the table with all four columns filled in.

[[MC]]
A pre-mortem is most useful when it is conducted:
- ( ) After the system is deployed, so real failure data informs the analysis
- ( ) During the debugging phase, when actual failures have been observed
- (x) Before building begins, when changing the design is still cheap
- ( ) After the first end-to-end test, when the team has hands-on intuition about the system

---

## Model 3: Design-First vs. Code-First - A Six-Week Timeline

Two student teams build the same 3-agent research pipeline. Team A starts coding immediately. Team B spends the first three days writing a one-page design document (agent table, pre-mortem, data flow diagram, evaluation rubric).

| Milestone | Team A: Code-First | Team B: Design-First |
|---|---|---|
| **Week 1** | ResearchAgent is running; it returns results but the format varies call to call (sometimes JSON, sometimes prose). WriterAgent is not started yet. | Design doc is complete. Agent table has agreed-upon input/output schemas for all three agents. No code yet, but the team knows exactly what they're building. |
| **Week 2** | WriterAgent is added; it breaks because ResearchAgent output format is inconsistent. Team A rewrites ResearchAgent to standardize output. Two days lost. | ResearchAgent and WriterAgent are both coded against the agreed schema. First end-to-end run works. CriticAgent stub is in place. |
| **Week 3** | CriticAgent is added. The team discovers they never defined what "a supported claim" means, so the critic prompt is vague. They argue about the rubric for a day. | CriticAgent is complete. The team runs their pre-designed adversarial test cases and finds that WriterAgent ignores sources 30% of the time. They fix the system prompt. |
| **Week 4** | Team A runs end-to-end for the first time. The output looks okay but they have no rubric to evaluate it against. They ask their instructor, "Is this good?" | Team B runs their full evaluation rubric (defined in the design doc) against 20 outputs. They quantify the flag rate and source accuracy. They have numbers to report. |
| **Week 5** | Team A discovers their agent has been hallucinating citations since Week 1. They have 3 weeks of outputs they cannot trust. | Team B's CriticAgent caught hallucinated citations in Week 3. Their Week 5 output is clean and auditable. |
| **Week 6** | Team A submits a system that mostly works. They cannot explain their design choices because they made them reactively. | Team B submits a system with documented design rationale, a working evaluation pipeline, and a quantified error rate. |

### Critical Thinking Questions

8. Team A lost two days in Week 2 to a schema disagreement they could have resolved in 30 minutes during a design session. What is the general principle here, and does it apply to non-agentic software as well?
9. In Week 4, Team A asks "Is this good?" but has no rubric to answer the question. Why is it impossible to evaluate an AI system without criteria that were defined *before* seeing the output? (Hint: think about what changes when you define criteria after seeing results.)
10. Team B's design doc took three days. Team A saved three days at the start and lost them elsewhere. What does this suggest about the relationship between upfront design cost and total project cost? Under what circumstances might Team A's approach actually be *better*?

---

## Exercises

1. **Write a one-page design doc.** Choose a 2-agent system from this list: (a) a ticket triage system that classifies support requests and drafts responses, (b) a code review system that reads a PR diff and flags potential bugs, (c) a meeting summarizer that transcribes audio and extracts action items. Write a complete agent table and a 5-row pre-mortem for your chosen system. You have 20 minutes.

2. **Minimum viable design.** As a team, debate and agree on the answer to: what is the *minimum* design artifact you need before starting to build an agentic system? What can you skip if you're in a hurry? Write a ranked list of design artifacts from "never skip" to "skip if pressed." The Presenter defends the team's top-priority choice.

3. **Evaluate a design doc.** Your instructor will share a sample design doc from a previous semester. As a team, apply the pre-mortem technique to it: identify two failure modes the original team missed. Write them up in the four-column format from Model 2.

---

## Reflection Prompt

In your notebook: the design-first principle asks you to slow down before you build. There is a real tension between this discipline and the pressure to ship quickly. Describe a personal experience (in software or in any other domain) where skipping planning cost you more time than planning would have taken. What conditions would have made you more likely to plan first?

---

## Further Reading

- Gary Klein. "Performing a Project Premortem." *Harvard Business Review* (2007). The origin of the pre-mortem technique applied here.
- Chip Heath and Dan Heath. *Decisive: How to Make Better Choices in Life and Work* (2013), Chapter 7. The "premortem" and "preparade" as decision tools.
- Anthropic. "Building Effective Agents." https://www.anthropic.com/research/building-effective-agents - the orchestration and agent design patterns section is directly relevant.
- Fred Brooks. *The Mythical Man-Month* (1975/1995), Chapter 1. "Plan to throw one away" - still the most honest advice about first-system costs.
