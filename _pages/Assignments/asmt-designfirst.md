---
layout: assignment
permalink: /Assignments/DesignFirst
title: "CS357: Foundations of Artificial Intelligence - Written Assignment: Design Before You Build"

info:
  coursenum: CS357
  points: 100
  goals:
    - To articulate the goals, constraints, and evaluation criteria for an agentic system before implementation
    - To produce an agent design table mapping each agent's role, prompt skeleton, inputs, outputs, tools, and failure modes
    - To conduct a pre-mortem identifying likely failure modes and mitigations
    - To define explicit success criteria that could be evaluated by a third party
  rubric:
    - weight: 25
      description: Problem Statement and Constraints
      preemerging: The problem statement is missing or describes a feature list rather than a problem
      beginning: A problem statement is present but omits who the system serves, the context of use, or the key constraints
      progressing: The problem statement identifies the system's purpose, users, and context with most constraints named, though some remain vague or unmeasurable
      proficient: The problem statement precisely identifies what the system does, for whom, in what context, and under what constraints, and every constraint is specific enough that a third party could determine whether it was satisfied
    - weight: 25
      description: Agent Design Table
      preemerging: No agent design table is provided, or a single undifferentiated agent is described
      beginning: A table is present but is missing required columns or contains identical roles that are not meaningfully distinct
      progressing: The table covers most required columns with reasonably distinct roles, though the prompt skeletons are generic and failure modes are cursory
      proficient: Every row contains a distinct role, a system prompt skeleton whose first three sentences establish persona, scope, and refusal boundary, clearly specified inputs and outputs, a justified temperature setting, named tools, and at least one concrete failure mode with a detection signal
    - weight: 25
      description: Pre-mortem and Risk Analysis
      preemerging: No pre-mortem is provided
      beginning: Fewer than six risks are identified, or risks are vague and detection or mitigation strategies are absent
      progressing: At least six risks are present with detection and mitigation strategies, though some mitigations are generic rather than specific to the system
      proficient: At least six concrete, system-specific risks are identified with a plausible detection mechanism and an actionable mitigation for each; at least one risk addresses a cross-agent coordination failure and one addresses a data or privacy concern
    - weight: 25
      description: Evaluation Criteria and Testability
      preemerging: No success criteria are provided, or criteria are purely subjective
      beginning: Criteria are stated but cannot be measured without access to the system's internals or its authors
      progressing: Most criteria are measurable by a third party, though at least one requires clarification or is redundant with another
      proficient: Three to five criteria are stated, each is measurable from outputs alone by a third party who does not know the system, criteria cover both functional correctness and at least one safety or quality dimension, and the reflection addresses how you would verify each
  readings:
    - rtitle: "Agent Design Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentdesign.md"
    - rtitle: "Pre-mortem Technique (Klein, 2007)"
      rlink: "https://hbr.org/2007/09/performing-a-project-premortem"

tags:
  - design
  - agents
  - written

---

This assignment reverses the usual order: you will produce a complete system design document for an agentic AI system *before* writing a single line of code. The discipline of specifying a system before building it catches ambiguity early, forces you to think about failure before you are attached to your solution, and produces the artifact your team will actually need when implementation begins.

## Instructions

Choose one of the following domains for your system:

- **Course tutoring agent**: answers student questions about a specific course topic using provided materials
- **Research assistant**: helps a user locate, summarize, and synthesize academic sources on a query
- **Code reviewer**: reviews submitted code against a rubric and returns structured feedback
- **Meeting summarizer**: processes a transcript and produces action items, decisions, and open questions

Produce the following five components. Each is described in detail below.

### 1. Problem Statement (1 paragraph)

Write one paragraph — no more, no less — that answers all four questions: What does the system do? For whom? In what context? Under what constraints? A good constraint is one that limits what the system may do, what data it may use, or how it may behave when uncertain. Vague constraints ("the system should be safe and helpful") do not count; name the specific boundary.

### 2. Agent Design Table

Produce a table with one row per agent and the following columns:

| Agent Name | Role | System Prompt Skeleton (first 3 sentences) | Inputs | Outputs | Temperature | Tools | Failure Mode |

The system prompt skeleton must contain exactly three sentences: the first establishes persona and scope, the second states the primary task, and the third states at least one explicit refusal or abstention condition. Temperature must be a decimal value with a one-sentence justification. The failure mode must be concrete: name the signal that would indicate the failure, not just the abstract risk.

### 3. Data Flow Diagram

Describe the flow of data through your system in text or ASCII art. Show: where user input enters, which agent receives it first, what is passed between agents, where external tools or retrieval systems are called, and where the final output is produced. If an agent can short-circuit the flow (for example, by refusing or escalating), show that branch.

### 4. Pre-mortem Table

Imagine your system has been deployed for two weeks and has failed. Working backwards, identify at least six things that could have gone wrong. For each, complete the following table:

| What Could Go Wrong | How We Would Detect It | How We Would Mitigate It |

Mitigations must be actions your system or your team could actually take, not aspirations. At least one row must address a failure that occurs when two agents produce contradictory outputs, and at least one must address a risk involving user data or privacy.

### 5. Success Criteria

State three to five measurable criteria that a third-party evaluator — someone who has never seen your system or spoken to you — could use to determine whether your system is working. Criteria must be evaluable from outputs alone. For each criterion, name the measurement method (for example: human rating on a 1–5 scale with a provided rubric, automated string match, latency in seconds, precision on a held-out task set).

## Reflection Prompts

Answer all three prompts in a short paragraph each:

- Which part of the design changed the most as you thought through it, and why did it change?
- What failure mode surprised you most when you wrote the pre-mortem, and what does that surprise reveal about your initial assumptions?
- How would you know, one week after deployment, whether your success criteria were actually being met?

## Submission Instructions

Submit a single PDF or markdown file containing all five components and your three reflection responses. You do not need to implement anything for this assignment; the deliverable is the design document only.

- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did it take you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
