---
layout: assignment
permalink: /Assignments/AgentArchitecture
title: "CS357: Foundations of Artificial Intelligence - Written Assignment: Design Your Agent Operating System"

info:
  coursenum: CS357
  points: 100
  goals:
    - To author the governing document set for an AI agent system in a domain of the student's choosing - a charter, an agent contract, a standing prompt with confirmation gates, and handoff state files - adapted from production templates rather than copied verbatim
    - To justify every retained rule and gate against a named, concrete failure mode it prevents, and to justify every deleted template rule with a reason it does not apply
    - To classify a realistic set of domain actions into autorun, queue, and forbidden lanes with defensible reversibility reasoning
    - To demonstrate handoff traceability by running or rigorously simulating an agent session governed by the documents, interrupting it, and showing that a second session can resume from the written state alone
    - To evaluate where the document set held, where it leaked, and what revision each leak motivates
  rubric:
    - weight: 30
      description: Completeness and Adaptation of the Document Set
      preemerging: One or more required documents is missing, or the templates are submitted with placeholders unfilled
      beginning: All documents are present but largely unmodified from the templates; sections that do not apply to the chosen domain are retained anyway, or domain-specific sections read as generic
      progressing: All documents are present and adapted to the domain; most sections are domain-specific, though some retained rules have no realistic enforcement path and some deletions are unexplained
      proficient: The charter, agent contract, standing prompt, and handoff files are all present, internally consistent, and unmistakably about the chosen domain; every template section that was deleted is listed with a one-line reason; the ranked priority list breaks ties in a way the student demonstrates with a concrete conflict scenario; and no rule remains that the student could not actually enforce
    - weight: 30
      description: Gate Design and Failure-Mode Justification
      preemerging: No confirmation gates are defined, or gates are copied verbatim from the template without reference to the domain
      beginning: Gates are present but justified by abstract risk ("this could be bad") rather than a named failure mode; the autorun/queue/forbidden classification is missing or contains fewer than ten actions
      progressing: At least ten domain actions are classified with mostly sound reversibility reasoning; each gate names a failure mode, though some detection or consequence descriptions remain vague; the forbidden lane may conflate "very risky" with "no approval can make this safe"
      proficient: At least ten realistic domain actions are classified into autorun, queue, and forbidden with explicit reversibility reasoning; every gate is justified by a concrete failure scenario naming the action, the harm, and why after-the-fact recovery is impossible or expensive; at least one forbidden item is accompanied by an argument for why no approval should ever make it safe; and the batch-threshold and blanket-consent rules are either retained with a domain-specific example or removed with a defensible argument
    - weight: 25
      description: Handoff Traceability Walkthrough
      preemerging: No walkthrough is provided
      beginning: A walkthrough is described but the interruption is trivial (the task was already complete) or the second session's resumption relies on information not present in the written state
      progressing: A genuine mid-task interruption is shown with updated handoff files, and the second session resumes correctly, though the write-up does not clearly distinguish what the second session learned from documents versus what it rediscovered on its own
      proficient: The walkthrough shows a real or rigorously simulated session interrupted mid-task; the updated SESSION and CURRENT_TASK files are included verbatim, each ending with a concrete next safe action and an evidence-cited reality check; the second session (a different agent, model, or cleared-history session) resumes from the written state alone without duplicating completed work; and every question the second session had to ask a human is identified, along with which document should have answered it and the revision that now does
    - weight: 15
      description: Reflection, Professionalism, and Presentation
      preemerging: No reflection is provided, or the submission contains unredacted personal or sensitive information
      beginning: A reflection is present but reports only that the system worked, without identifying a leak, a rot risk, or a revision
      progressing: The reflection identifies at least one place the document set leaked or would rot under pressure, with a plausible revision, though the connection between evidence and revision is loose
      proficient: The reflection names at least one specific leak observed in the walkthrough and one document the student predicts would rot first under real use, each paired with a concrete revision or automation; the submission is professionally formatted, internally cross-referenced, and fully anonymized - no real credentials, tokens, personal data, or identifying third-party information appears anywhere in the document set
  readings:
    - rtitle: "Case Study: Governing Coding Agents - Charters, Handoffs, and Durable Memory"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentgovernance.md"
    - rtitle: "Case Study: From Second Brain to Chief of Staff - A Personal Agent in Production"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-productionassistant.md"
    - rtitle: "Agent Operating System Templates (starting points for every required document)"
      rlink: "https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/README.md"
    - rtitle: "Human-in-the-Loop: Oversight, Escalation, and Appropriate Autonomy"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-humanintheloop.md"

tags:
  - agents
  - governance
  - safety
  - written

---

The two production case studies you read describe an "agent operating system": the written contract, charter, gates, and handoff state that make an AI agent system trustworthy, interruptible, and independent of any single model or vendor. In this assignment you will author that operating system for a domain of **your** choosing — and then prove it works by interrupting an agent mid-task and letting a second one resume from your documents alone. The deliverable is the document set plus the walkthrough; polish in the documents matters exactly as much as it would in production, because these documents *are* the production system.

---

## What a Strong Submission Looks Like

- **The documents are about your domain, not about documents.** A weak charter says "the agent should be careful with important files." A strong charter for a photo-archive project says: "Everything under `originals/` is immutable. The agent works only in `derived/`. A deleted original cannot be recovered; there is no gate that makes deleting one acceptable — it is forbidden, not queued."
- **Every gate earns its place with a story.** A weak justification: "sending messages is risky." A strong one: "The agent triages my club's inbox. If it auto-replies to a member's resignation email with a scheduling template, the member is publicly ignored at the moment they most needed a human; no follow-up un-sends it. Therefore: drafting autoruns, sending queues, and replies to anything classified 'sensitive' queue with the classification shown."
- **The walkthrough is honest.** The most valuable sentence in a strong submission is usually something like: "The second agent asked which test command to run — my documents never said. That answer belongs in the charter's testing section, which now reads: ..."

---

## Instructions

### Step 1: Choose a domain

Any domain with real work and at least one genuinely irreversible action qualifies. It does **not** need to be a software project. Good examples: managing a student organization's communications and files; maintaining a research-notes vault; running a small online shop's catalog; organizing a family photo/document archive; operating a course-project repository; managing a fantasy-sports or gaming community. You may reuse your Project Thread system.

### Step 2: Author the document set

Starting from the [course templates](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/README.md), produce:

1. **A charter** (`CHARTER.md`): mission (one sentence), a **ranked** priority list (demonstrate the ranking with one concrete conflict it resolves), definition of success, the rules you will actually enforce, at least one milestone with a gate.
2. **An agent contract** (`AGENTS.md` style): the zones of your workspace (what is read-only, what is writable, what is off-limits), write protocols, and maintenance behavior.
3. **A standing prompt** (`SYSTEMPROMPT.md` style): operating habits and, centrally, **confirmation gates rewritten for your domain's irreversible actions**, plus an escalation rule.
4. **Handoff state files** (`.ai/` style): `CURRENT_TASK.md` with completion criteria and a reality-check table, and `SESSION.md` ready to receive entries that end with a next safe action.
5. **An action classification**: at least **ten** realistic actions an agent would take in your domain, classified Autorun / Queue / Forbidden, each with one line of reversibility reasoning.

Delete every template section you cannot honestly enforce — and list what you deleted and why (a rule nobody enforces is worse than no rule).

### Step 3: Run the handoff walkthrough

Govern a real agent session with your documents (any agent CLI or chat agent from this course works; if your domain has no digital surface an agent can touch, a rigorous simulated transcript is acceptable — mark it as simulated):

1. Start a session; require the agent to read your document set first and restate mission, task, and next action.
2. Give it a task; **interrupt it mid-task**; require it to write the handoff state.
3. Start a **second** session (different agent, different model, or cleared history). Give it only the kickoff/handoff prompt.
4. Record: what it resumed correctly, what it duplicated, and every question it asked that your documents should have answered.

Include the two handoff files verbatim (as updated by session one) and the relevant transcript excerpts.

### Step 4: Reflect

One page or less: where did the document set hold, where did it leak, which document would rot first under a month of real use, and what one revision or automation does each answer motivate?

---

## Submission

Submit a single PDF or Markdown bundle containing the five documents, the classification table, the walkthrough (files + transcript excerpts), and the reflection. **Anonymize everything**: no real credentials, tokens, personal data, or identifying information about third parties may appear anywhere in the submission — treat this rule as your first Forbidden-lane item.
