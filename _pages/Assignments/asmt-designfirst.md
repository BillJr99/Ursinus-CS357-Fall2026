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

In this assignment you will produce a complete system design document for an agentic AI system before writing a single line of code. You will define what the system does and for whom, design the agents that compose it, trace data as it flows through the system, anticipate failures before they happen, and state success criteria that an outside evaluator could apply. The discipline of specifying a system before building it catches ambiguity early, forces you to think about failure before you are attached to your solution, and produces the artifact your team will need when implementation begins. This kind of document — sometimes called a design proposal, a system spec, or an RFC — is a standard professional writing genre in engineering and AI product development.

---

## What a Strong Submission Looks Like

A strong submission has these qualities:

- **Constraints are specific and falsifiable.** "The system must respond in under 5 seconds on commodity hardware" is a constraint. "The system should be fast and helpful" is not. Every constraint in a strong submission passes this test: could a stranger determine, from the system's outputs, whether the constraint was satisfied?
- **The agent design table contains real prompt skeletons, not role names.** A weak table says: *Summarizer Agent — summarizes documents.* A strong table says: *"You are a document summarizer specialized in academic research papers. Your task is to produce a 100-word abstract of the document provided. If the document is not in English, respond: 'I cannot summarize this document — please provide an English-language version.'"* The three sentences establish persona, task, and refusal condition.
- **The pre-mortem is concrete and specific.** A weak pre-mortem lists "the model hallucinates" as a risk. A strong pre-mortem lists: "The Retrieval Agent returns a passage from a different document than the user queried because two documents share a similar opening sentence. Detection: the retrieved passage's source metadata does not match the user's query document name. Mitigation: require the Retrieval Agent to include source metadata in every returned chunk and have the Synthesis Agent verify the source before incorporating it."

---

## Instructions

Choose one of the following domains for your system:

- **Course tutoring agent**: answers student questions about a specific course topic using provided materials
- **Research assistant**: helps a user locate, summarize, and synthesize academic sources on a query
- **Code reviewer**: reviews submitted code against a rubric and returns structured feedback
- **Meeting summarizer**: processes a transcript and produces action items, decisions, and open questions

Produce the five components below. You do not need to implement anything. The deliverable is the design document only.

---

### Component 1: Problem Statement

Write one paragraph — no more, no less — that answers all four questions:

1. **What** does the system do?
2. **For whom** does it do it?
3. **In what context** is it used?
4. **Under what constraints** must it operate?

A good constraint limits what the system may do, what data it may use, or how it may behave when uncertain. Vague constraints ("the system should be safe and helpful") do not count. Name the specific boundary — for example: "The system may only use documents the user has explicitly uploaded in the current session and must not retrieve information from the open internet."

**Example problem statement (meeting summarizer):**
> This system processes audio transcripts of team meetings and produces structured summaries for remote employees who were unable to attend. It is used within a corporate Slack workspace by teams of 5–20 people conducting 30–90 minute project syncs. Constraints: the system must never include names or identifying information in summaries without the speaker's prior consent; it must complete processing within two minutes of transcript submission; and it must abstain from summarizing any segment it cannot parse with at least 80% word-recognition confidence, flagging those segments for human review instead.

---

### Component 2: Agent Design Table

Produce a table with one row per agent. Your system must have at least two meaningfully distinct agents. Use the following columns:

| Agent Name | Role | System Prompt Skeleton (3 sentences) | Inputs | Outputs | Temperature | Tools | Failure Mode & Detection Signal |
|---|---|---|---|---|---|---|---|

**Column guidance:**

- **System Prompt Skeleton:** Write exactly three sentences. Sentence 1: establishes persona and scope. Sentence 2: states the primary task. Sentence 3: states at least one explicit refusal or abstention condition.
- **Temperature:** A decimal value (e.g., 0.2) followed by a one-sentence justification. Example: "0.2 — low temperature reduces creative variation in structured classification tasks where consistency matters more than diversity."
- **Failure Mode & Detection Signal:** Name the specific observable signal that would indicate the failure, not just the abstract risk. "Hallucination" is not a failure mode. "The agent returns a citation with an author name that does not appear in any uploaded document, detectable by string-matching cited names against the document index" is a failure mode.

---

### Component 3: Data Flow Diagram

Describe the flow of data through your system in text or ASCII art. Show:
- Where user input enters
- Which agent receives it first
- What is passed between agents (and in what format)
- Where external tools or retrieval systems are called
- Where the final output is produced
- Any branches: if an agent can refuse, escalate, or short-circuit the flow, show that branch with a label

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

---

### Component 4: Pre-mortem Table

Imagine your system has been deployed for two weeks and has failed. Working backwards, identify at least six specific things that could have gone wrong. For each, fill in the following table:

| What Could Go Wrong | How We Would Detect It | How We Would Mitigate It |
|---|---|---|
| *(be specific: name the agent, the input type, the output fault)* | *(name a specific observable signal, not "we would notice")* | *(name an action your system or team could actually take, not "we would be more careful")* |

**Required coverage:** At least one row must address a failure that occurs when two agents produce contradictory or incompatible outputs. At least one row must address a risk involving user data or privacy.

**Example rows:**

| What Could Go Wrong | How We Would Detect It | How We Would Mitigate It |
|---|---|---|
| The Summarizer Agent invents an action item not present in any transcript segment | A reviewer finds an action item in the summary that does not appear in the transcript; string-match check between action items and transcript passages fails | Require the Summarizer Agent to return a citation (transcript line number) for each action item; automated checker verifies every action item maps to a real transcript line |
| The Parser Agent assigns a turn to the wrong speaker when two speakers have similar voice patterns | A meeting attendee reports that their name appears on a statement they did not make | Add a confidence threshold for speaker identification; if confidence < 0.9, replace speaker name with "Speaker [unknown]" |

---

### Component 5: Success Criteria

State three to five measurable criteria that a third-party evaluator — someone who has never seen your system or spoken to you — could use to determine whether your system is working. Criteria must be evaluable from outputs alone, without access to the system's internals.

For each criterion, fill in this table:

| Criterion | What "Success" Looks Like | Measurement Method | Passing Threshold |
|---|---|---|---|
| *(name the property being measured)* | *(describe the output when the criterion is met)* | *(human rating with a rubric / automated string match / latency timer / precision on test set)* | *(the specific value or rating that constitutes passing)* |

**Example rows (meeting summarizer):**

| Criterion | What "Success" Looks Like | Measurement Method | Passing Threshold |
|---|---|---|---|
| Action item completeness | Every genuine action item from the transcript appears in the summary | Human rater compares summary action items to manually identified ground-truth action items from the same transcript | Recall ≥ 0.85 on a 20-transcript test set |
| Processing latency | Summary is delivered quickly enough to be useful | Timer from transcript submission to Slack delivery | Under 120 seconds for a 60-minute meeting transcript on the lab server |
| Privacy compliance | No participant's real name appears in the summary without consent | Automated scan of summary output against list of participant names from meeting invite | Zero name appearances in summaries for meetings marked "anonymous" |

---

## Reflection Prompts

Write one paragraph addressing each of the three prompts below:

1. **Which part of the design changed the most as you thought through it, and why did it change?** Be specific: which component (problem statement, agent table, pre-mortem, or success criteria) required the most revision, and what assumption did you discover was wrong?
2. **What failure mode surprised you most when you wrote the pre-mortem, and what does that surprise reveal about your initial assumptions?** The most useful pre-mortems surface failures that the designer initially believed "could not happen."
3. **How would you know, one week after deployment, whether your success criteria were actually being met?** Name the specific data you would collect, who would collect it, and what you would do if a criterion was not being met.

---

## Frequently Asked Questions

**Q: My system only needs one agent to accomplish the task. Can I still submit it?**
A: The rubric requires "meaningfully distinct roles" in the agent table. If a single agent genuinely handles the full task, you may design it with one orchestrator and one specialist (for example, a router agent that decides what to do and a specialist agent that does it). Think about where responsibilities could be separated — even simple systems can benefit from a verification or formatting agent.

**Q: How long should the data flow diagram be?**
A: As long as it takes to show every handoff clearly. A simple two-agent system might need only 10 lines of ASCII art. A four-agent system with branches might need 30 lines. Length is not the goal; clarity is. Every agent and every handoff should be visible.

**Q: My pre-mortem has seven risks, but only one addresses coordination failure and none addresses privacy. Can I still get full credit?**
A: No. The rubric specifically requires at least one coordination failure and at least one data/privacy risk. These are not optional — they represent the two most common failure categories in real multi-agent deployments.

**Q: The success criteria seem redundant — isn't "accuracy" covered by multiple criteria?**
A: It can be. The rubric rewards criteria that cover distinct dimensions: one functional correctness criterion (does it do the right thing?), one quality criterion (is the output useful?), and one safety or reliability criterion (does it behave appropriately at the boundary?). If all your criteria are variations on accuracy, you are missing at least one dimension.

**Q: Can I choose a domain not on the list?**
A: Yes, if you confirm with the instructor first. The listed domains are well-scoped for this assignment. A custom domain may require more work to scope appropriately, and an overly ambitious scope will make the design document less precise, which will hurt your grade.

---

## Submission Instructions

Submit a single PDF or markdown file containing all five components and your three reflection responses. You do not need to implement anything for this assignment; the deliverable is the design document only.

- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did it take you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
