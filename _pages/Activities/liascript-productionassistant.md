<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-productionassistant.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-productionassistant.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# From Second Brain to Chief of Staff: A Personal Agent in Production

In *The Second Brain* module you built the foundation: a Markdown vault on GitHub, a sync protocol, and an `AGENTS.md` contract that let an agent like **hermes** read and write your knowledge safely.  This case study (a real production system, anonymized) shows what that foundation grows into after a year of daily use: a standing assistant wired into a task manager, calendar, file store, email, and GitHub, running scheduled routines around the clock, accumulating skills, and updating its own memory, all without ever once being trusted to send an email on its own.

Today's route runs **the three-file contract $\rightarrow$ confirmation gates and governed autonomy $\rightarrow$ integrations and scheduled routines $\rightarrow$ the robustness harness $\rightarrow$ operations as knowledge**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Standing Prompt** | A versioned system-prompt file that governs *every* session of a personal assistant: habits, style, gates, and escalation: the law the persona operates under. | `SYSTEMPROMPT.md` §9: "Drafting is permitted without confirmation; sending is not." |
| **Confirmation Gate** | A rule that a specific category of irreversible action requires fresh, explicit approval at the moment of execution; no blanket consent. | "Go ahead and handle everything" still does NOT authorize sending an email |
| **Governed Autonomy** | An architecture where an unattended agent may *propose* any action but may *execute* only actions its gate policy classifies as safe; everything else queues for approval. | An Automation Spine that classifies each action as Autorun, Queue, or Forbidden |
| **Self-Updating Memory** | A durable memory file the assistant itself writes back to, under a sync rule that no live memory may be deleted or compressed before it is reflected in the file. | `LLMMEMORIES.md`, appended with dated entries rather than silently rewritten |
| **No-Agent Routine** | A scheduled job implemented as a deterministic script with *no LLM in the loop*, reserving the model for judgment and keeping routine work reproducible. | A morning-brief cron job whose empty output means "no message today" |
| **Living Runbook** | The assistant's versioned memory of its *own* infrastructure (instances, services, skills, known issues) maintained by the assistant as part of every setup change. | A service-ownership table that prevents two instances from silently fighting over one capability |

---

# Part I: The Three-File Contract in Production

In this part, you will see how the vault contract you built in *The Second Brain* hardens into three root files with distinct jobs, and learn which file governs which situation.

## 1.  Three Files, Three Jobs

**Why this matters:** A production assistant is governed by documents the same way the coding agents in the companion case study are.  At the vault root live exactly three canonical meta-files:

**`AGENTS.md`: the environment contract.**  You already know its core (three zones, sync metadata, write scope) from *The Second Brain*.  The production version adds teeth:

- A **question-answering protocol**: read `/wiki/` first as the authoritative curated source; use `/raw/` only to fill gaps or catch new material; *if `/wiki/` is stale relative to `/raw/`, update `/wiki/` first, then answer*; so answering questions continuously repairs the knowledge base.
- A **maintenance loop** (the vault linter): enumerate files, repair broken links (classifying each as valid / file-not-found / ambiguous / heading-not-found), audit metadata, and emit a dated lint report.  With two write disciplines: *"Before writing any file back to disk, diff the proposed content against the current content.  Do not write if the diff is empty"* and *"Prefer surgical edits over full file rewrites."*
- A **judgment clause** for everything unenumerated: *"prefer clean structure over clutter; prefer canonical pages over duplicates; prefer linking over copying; prefer thoughtful synthesis over raw aggregation; prefer preserving useful detail over vague summarization."*

**`SYSTEMPROMPT.md`: the standing prompt.**  Where *Designing Agent Personas* taught you to shape a voice, the production standing prompt is mostly **governance**.  Its load-bearing sections:

- *Operating habits:* "Lead with the outcome."  "Ground every claim in evidence; state explicitly when a claim is unverified, inferred, or assumed."  "Assess before acting; do not act uninvited; when the owner is thinking aloud rather than requesting a change, the deliverable is the assessment itself."
- *Clarification protocol:* "Do not begin execution if the goal, audience, format, or scope is ambiguous and that ambiguity would materially affect the output.  Ask targeted, numbered clarifying questions... Do not invent facts, decisions, dates, numbers, approvals, citations, or source attributions."
- *Output discipline:* "When a task produces multiple discrete outputs, complete and display **one representative example first** and request confirmation before generating the full batch."
- *Memory hygiene:* "Sessions do not retain memory between sessions.  Treat the vault's context files as the authoritative persistent memory... If a task produces information that should persist, suggest saving it to the appropriate context file and offer to do so."
- *Escalation:* "On unexpected state: STOP, report clearly, wait for guidance.  Do not attempt to recover autonomously from unexpected states.  The cost of pausing is always lower than the cost of an unintended irreversible action."

**`LLMMEMORIES.md`: the self-updating memory.**  Durable facts and preferences, written back by the assistant itself, under two rules: the **memory-to-vault sync rule** (no live memory is deleted or compressed before this file reflects it) and an **append-and-date** discipline (memories are added with provenance, not silently rewritten).  Its most interesting section is instructions *to future agents about how to consume it*: "a living summary of durable user-context, not a substitute for reading the vault itself."

A precedence rule ties the set together: *where `AGENTS.md` and `SYSTEMPROMPT.md` overlap, the stricter requirement applies; where equally strict, `SYSTEMPROMPT.md` governs.*

---

## Model 1: Which File Governs?

For each scenario, decide which of the three files the assistant should be obeying:

| # | Scenario | Governing file? |
|---|---|---|
| 1 | The assistant answered a question from `/raw/` because the relevant `/wiki/` page didn't exist yet, and moves on without creating it | ? |
| 2 | Asked to "clean up my notes," the assistant plans to regenerate every page from scratch for consistency | ? |
| 3 | The owner mentions in passing that they've switched task managers; the session will end in five minutes | ? |
| 4 | Asked to draft thank-you notes to 40 people, the assistant generates all 40 immediately | ? |
| 5 | Mid-task, a cloud API starts returning errors the assistant has never seen | ? |

### Critical Thinking Questions

1.  Resolve each scenario: name the governing file *and* the specific rule violated or invoked.  Scenarios 2 and 4 violate different rules with the same underlying philosophy; what is it?

   > *Hint: For 2, re-read the linter's write disciplines.  For 4, the output-discipline rule.  Both rules force a small, inspectable step before a large, expensive one.*

2.  The memory-to-vault sync rule orders operations: file first, *then* live-store deletion or compression.  What failure does the opposite order create, and why is it unrecoverable in a way most assistant failures are not?

   > *Hint: Every other artifact in this system is versioned in Git.  What is the live memory store versioned in?*

3.  The standing prompt's "assess before acting" habit and the escalation protocol's "do not recover autonomously" rule both make the assistant *less* autonomous.  Given that the entire point of the system is delegation, argue why these rules increase rather than decrease the total work safely delegated.

   > *Hint: Think about what one uninvited irreversible action does to the owner's willingness to delegate the next hundred reversible ones.  Trust is the budget; what spends it?*

> **Common Misconception:** "The system prompt is where you make the assistant smart."  Nothing in the standing prompt improves the model's intelligence.  Every section either *routes* intelligence (read the vault, lead with the outcome) or *bounds* it (gates, escalation).  Capability comes from the model and its tools; a production standing prompt is how capability becomes trustworthy.

Under the production `AGENTS.md`, when the assistant finds `/wiki/` outdated relative to `/raw/` while answering a question, it should:

[( )] Answer from `/raw/` directly, since it is the fresher source
[( )] Refuse to answer until the owner reorganizes the vault
[(X)] Update `/wiki/` first when appropriate, then answer grounded in the curated content, so every question asked makes the vault better
[( )] Answer from `/wiki/` anyway, since it is the authoritative source

---

# Part II: Governed Autonomy - Gates and the Automation Spine

In this part, you will classify real actions the way the production system does, and see how an unattended agent asks permission.

## 2.  Confirmation Gates

**Why this matters:** The *Human-in-the-Loop* module gave you the theory: autonomy spectra, escalation, approval fatigue.  Here is a production implementation.  The standing prompt defines six gate categories: file system, external communications, version control, web/cloud publishing, financial/administrative/credentialed actions, and a batch threshold, under one umbrella rule:

> "A general instruction to 'go ahead and handle everything' does NOT constitute confirmation for actions in these categories.  Each gate requires its own confirmation at the moment of execution."

Representative gates:

- *External communications:* "**Drafting is permitted without confirmation; sending is not.**"
- *File system:* deleting or overwriting requires confirmation and a proposed dated backup; bulk renames of more than 3 files gate.
- *Batch threshold:* "Any automated batch operation affecting more than 5 files, records, or API calls in a single execution requires confirmation **before the batch runs**, not after."
- And every confirmation request must display: (a) the target, (b) the nature of the change, (c) backup status, (d) a one-line plain-English summary of what is lost or changed.

## 3.  The Automation Spine

A gate is easy when the owner is in the chat.  But this assistant also runs *unattended*, so consequential actions become **proposals** stored before execution, and a policy classifies every action type into three lanes:

| Lane | Meaning | Examples from the production policy |
|---|---|---|
| **Autorun** | Execute immediately + write an audit row | Create/update/complete a task; send a digest *to the owner*; create a branch; open a *draft* PR; capture a note; authorized vault write-backs |
| **Queue** | Store as a proposal; wait for explicit approval | Send email/message to a third party; push to a non-vault repo; merge; force-push; deploy a site; any financial transaction; modify an institutional system; large batches |
| **Forbidden** | Refuse outright, even if asked casually | Write a secret to the vault; log a secret; exfiltrate a credential; send raw regulated personal data to a cloud service |

Approvals arrive over authenticated channels (dashboard buttons, or `approve #17` / `reject #17` replies in chat or email) with an owner-identity check before applying, and a daily digest renders pending proposals as a stable numbered list.

---

## Model 2: Classify the Action

Classify each action into **Autorun**, **Queue**, or **Forbidden** under the policy above:

1.  Mark yesterday's completed tasks done in the task manager
2.  Reply to a colleague's email asking about a meeting time
3.  Append today's meeting notes to the vault's project page
4.  Merge the assistant's own draft PR now that CI is green
5.  Store the owner's API key in the vault "so it isn't lost"
6.  Send the owner their morning schedule digest
7.  Renew a $12 domain registration that expires tomorrow
8.  Rename 200 scanned documents to a consistent date format
9.  Open a draft PR with a proposed fix to the owner's website
10.  Include a student's graded submission in a prompt to a cloud model to "summarize progress"

### Critical Thinking Questions

1.  Classify all ten.  Two of them are Forbidden, and the reason they are Forbidden rather than merely Queued is different for each.  Explain the two distinct principles.

   > *Hint: One violates "never persist secrets outside the secret store"; no approval can make it safe, because the danger is the artifact existing at all.  The other violates a data-boundary rule about regulated personal data; whose consent is missing, and can the owner supply it?*

2.  "Open a draft PR" is Autorun, but "merge" is Queue, even though the merge was of the assistant's own work and CI was green.  What distinction between the two actions justifies the different lanes?  State it as a general rule you could apply to a brand-new action type.

   > *Hint: Which of the two actions is trivially reversible?  Which one changes what other people and systems consume?*

3.  The urgent domain renewal (#7) is $12 and expires *tomorrow*; queueing it risks losing the domain.  Does the policy still make the right call?  Design one mechanism that preserves the gate while handling real urgency, without creating an "urgent" loophole an agent could learn to invoke.

   > *Hint: The gate governs who decides, not how fast.  What properties would an escalation channel need, and who defines "urgent," the policy or the agent?*

> **Common Misconception:** "Approval gates don't scale; you end up approving hundreds of things a day."  In the production system the opposite happened, because the *classification* did the scaling: routine actions were deliberately moved into Autorun **with an audit row**, so the queue stayed short enough that each item got real attention.  The failure mode to fear is not too many gates; it is gates so numerous and noisy that approval becomes a reflex.  (You saw this as *approval fatigue* in the Human-in-the-Loop module.)

Under the umbrella rule, the owner says: "I trust you; just handle my inbox this week."  The assistant may:

[( )] Send routine replies but queue sensitive ones
[( )] Send replies but BCC the owner on each
[(X)] Triage, label, and draft replies freely, but every send still queues for its own approval, because blanket consent never satisfies a per-action gate
[( )] Nothing, because the instruction is ambiguous

---

# Part III: Integrations and Scheduled Routines

In this part, you will see the pattern for wiring one assistant into many external systems without multiplying risk.

## 4.  Reads Are Free; Writes Are Gated

**Why this matters:** The production assistant connects over MCP (which you built servers for in the MCP modules) to a task manager, calendar, file store, email, and GitHub.  Across all five, one asymmetry repeats:

- **Task manager:** read tasks, comments, and project state freely for context; task *mutations* are Autorun-with-audit (low stakes, fully reversible), but only inside the owner's own workspace.
- **Calendar:** read free; event creation proposes.
- **File store:** *metadata only* in routine digests (names, dates, sharing status), not contents, unless a task requires a specific document.
- **Email:** triage and drafting are unrestricted; **sending never is** (drafts-never-sends).
- **GitHub:** read and draft-PR free; merge/push to shared repos queues.

The second big pattern is **no-agent routines**: the scheduled layer is almost entirely *deterministic scripts with no LLM call at all*: a morning brief, a deadline radar scanning the next 14 days, a weekly digest per project, and infrastructure watchdogs (network and container liveness every five minutes, *silent on success*, alerting only on actionable failure).  A script that finds nothing prints nothing, and empty output means no message.  Each job "writes only local report files and performs no source-system mutations."

And because an always-on host is sometimes off, the routines carry a **catch-up policy**: after a restart, "collapse the downtime into one missed-execution event, run the job exactly once immediately as catch-up, record that catch-up, advance the next scheduled run normally, and avoid replaying every missed interval."

### Critical Thinking Questions

1.  Why implement the morning brief as a deterministic script rather than an LLM prompt ("summarize my day"), given that the assistant has a perfectly good model available?  Name three concrete advantages, at least one involving failure behavior.

   > *Hint: Consider cost, reproducibility ("why did Tuesday's brief omit the deadline?"), testing, and what a hallucination in a trusted daily artifact does that a hallucination in a chat answer does not.*

2.  The watchdogs are silent on success.  Connect this to alarm fatigue (the operational cousin of approval fatigue): what happens to the *information content* of a notification channel as its false-positive and no-op rate rises?

   > *Hint: If the assistant messages you 40 times a day saying "all fine," what is your reaction time to message 41, which isn't?*

3.  The catch-up policy runs a missed job *exactly once*, not once per missed interval.  Construct a concrete example where replaying every missed interval would be actively harmful, and one where a single catch-up loses something.  How would you decide a job's policy?

   > *Hint: Think about a deadline-radar job missed for three days versus a "log a daily metric snapshot" job missed for three days.  Which output is cumulative and which is a view of "now"?*

The production system's file-store integration reads *metadata only* in routine digests.  The best justification is:

[( )] File contents are too large for the model's context window
[(X)] Routine jobs should consume the minimum data needed for their purpose; surfacing that a document changed does not require reading it, and least-privilege limits both privacy exposure and blast radius
[( )] The file-store API charges per byte read
[( )] Metadata is more accurate than file contents

---

# Part IV: Reliability: the Robustness Harness

In this part, you will find the missing verification in a flawed transcript, using the discipline the production system applies when it cannot trust its own model.

## 5.  Verification Is External, Not Self-Judgment

**Why this matters:** Parts of the production system run against pools of *weak, load-balanced* models: cheap, fast, and unreliable.  Rather than hoping for a smarter model, the vault contract ships a **robustness harness**: a standing sub-contract that makes weak intelligence produce trustworthy work.  Its skeleton:

- **Role routing:** distinct model tiers for Executor, Planner, Verifier, and Fallback; the verifier is never the executor.
- **The two-gate protocol:** Gate 1, restate the goal as *intent-level success criteria* and stop for approval.  Gate 2, present a plan with **a concrete, verifiable check for every criterion** and stop for approval.  After approval, the criteria are **frozen**: "you may not edit, relax, reinterpret, or override" them mid-task.
- **The coverage matrix:** a table of requirement -> criterion -> plan step -> check -> status (open / passed / failed / deferred), maintained on disk, so nothing silently drops.
- **Verification dialects** by domain: *code* verifies with exit codes and test runs; *operations* verifies by re-reading live state after the change (and knowing the reversal path); *research* verifies with a provenance ledger and an adversarial pass.
- **Blind cross-check:** a fresh sub-agent, given only the frozen criteria and the artifact (not the transcript) judges whether the work satisfies the criteria.
- **The final reconciliation gate:** before delivery, scan for stubs and TODOs and tag every element by *how it was confirmed*.
- **The self-improvement guardrail:** the assistant may canonize a new skill or memory **only from runs that passed the reconciliation gate**, stamped with provenance, so the system never learns from its own unverified work.

Governing one-liners, verbatim: *"Verify before you assert."*  *"Verification is external, not self-judgment."*  *"Surface uncertainty inline, and abstain rather than guess."*  And a persistence clause: *"This harness is immutable once persisted... re-read at session start."*

---

## Model 3: The Flawed Transcript

An assistant using the harness was asked to "clean up the vault's project pages: fix broken links and update the status field on each of the 12 project pages."  Its transcript, condensed:

> Gate 1: criteria agreed - (a) zero broken links on project pages, (b) every project page has a current status field.  Approved.
> Gate 2: plan, meaning enumerate pages, lint links, patch statuses; check for (a): re-run linter, expect zero broken; check for (b): grep for status field on all 12 pages.  Approved.  Criteria frozen.
> ...work happens...
> "Done!  I fixed 9 broken links across the pages.  I also noticed the status fields used inconsistent vocabulary, so I standardized them to Active/Paused/Done, which better satisfies the spirit of criterion (b).  The pages look much better now; I'm confident everything is in order.  Marking both criteria passed."

### Critical Thinking Questions

1.  Find *three* distinct harness violations in the closing message.  For each, name the harness element that should have caught it.

   > *Hint: What evidence is shown for criterion (a)?  Who judged that the work "is in order"?  And what happened to the frozen criteria when the assistant improved "the spirit" of (b)?*

2.  The vocabulary standardization might well be an improvement.  What is the harness-compliant way to handle a mid-task better idea, and why does the harness refuse to let even *good* ideas bypass it?

   > *Hint: The freeze exists because a weak model cannot reliably distinguish "improving the criteria" from "drifting away from the request."  Where do good mid-task ideas go instead; recall the parking-lot pattern from the companion activity?*

3.  The blind cross-checker receives only the frozen criteria and the artifact, deliberately *not* the transcript.  What class of error does withholding the transcript prevent the verifier from inheriting?

   > *Hint: Transcripts are persuasive.  If the executor's narration says "I verified all links," what does a verifier reading that narration tend to do, and what does a verifier who can only run the linter itself do?*

Under the self-improvement guardrail, the assistant may add a new skill or durable memory only when:

[( )] The owner explicitly dictates the exact content to store
[( )] The model's confidence in the lesson exceeds a threshold
[(X)] The lesson comes from a run that passed the final reconciliation gate, and it is stored with provenance identifying that run
[( )] The same lesson has been observed in at least three sessions

---

# Part V: Operations as Knowledge

In this part, you will see the move that completes the "second brain" idea: the assistant's own infrastructure becomes pages in the vault it maintains.

## 6.  The Living Runbook

**Why this matters:** After a year, the production assistant is *itself* a system: two deployments (a containerized worker and an always-on control-plane instance on a small headless machine), sidecar services, dozens of skills, scheduled jobs, credentials.  Where does the knowledge of *that* live?  In the vault, of course, maintained by the assistant, under the same contract as everything else:

- **A living runbook** page indexes the setup: an environment-topology table naming each instance precisely ("avoid the bare assistant name when the distinction affects paths, credentials, service ownership, or uptime assumptions"), and a topic page per subject with a "read or update when..." routing table.  Its maintenance directive: every setup change is recorded *in the topic page that owns the subject*, at the time it happens.
- **A service-ownership and cutover table** prevents the two instances from silently duplicating or disabling one another: every capability has exactly one current owner, and *transferring* ownership requires a staged checklist (starts successfully -> handles a real input -> responds on the right channel -> survives restart -> survives reboot -> documented -> owner explicitly confirms the old instance may be disabled).
- **A known-issues ledger** with stable IDs (`KI-01`, `KI-02`...): status, environment, evidence, current handling, plus the discipline *"verify the upstream fix is present before reapplying an old patch."*
- **A skills inventory with a reconstruction manifest**: every skill (you wrote skills in the *Agent Skills* modules) is listed with its restore path, portability class, and a one-line verification command, so the entire skill layer can be rebuilt on a fresh host, *explicitly without copying secrets*.  A provenance-naming rule keeps authorship honest: third-party skills keep their canonical names; locally authored or locally adapted skills take a personal prefix and document their inspiration "rather than presenting it as an upstream mirror."
- **Secrets: names, never values.**  Vault pages "may list variable names, credential file paths, ownership, and purpose, but never credential contents."  Secrets live in the secret store; the vault stores the *map* to them.

The through-line of the whole case study: intelligence is cheap and replaceable; the model behind this assistant changed several times in that year.  What persisted, and what made each new model immediately competent, was the **written operating system around it**: contract, prompt, memory, gates, routines, harness, runbook.  That is the part you can start building today, and it is the part this course's templates give you.

### Critical Thinking Questions

1.  The cutover checklist requires "survives a host reboot" *and* "survives a service restart" as separate checks before an old capability owner is disabled.  Why are these distinct failure modes, and what specifically breaks if you test only the restart?

   > *Hint: What launches a service after a reboot?  Is that mechanism exercised by restarting the service by hand?*

2.  The reconstruction manifest makes the skill layer rebuildable "explicitly without copying secrets."  Explain how the names-never-values rule is what makes it *safe for this manifest to exist at all*, and what the manifest would become without it.

   > *Hint: A complete, well-organized inventory of a system is exactly what an attacker wants.  What turns a treasure map into a harmless index?*

The service-ownership table exists primarily to prevent:

[( )] The owner from forgetting which cloud vendor hosts the assistant
[(X)] Two assistant instances from silently duplicating or disabling one another when a capability migrates, by recording exactly one current owner and gating every transfer behind a verified cutover
[( )] Skills from being installed on more than one instance
[( )] The assistant from exceeding its API budget

---

# Part VI: Synthesis and Practice

## 7.  Exercises

Copy-paste starting points (the vault contract, standing prompt, memory file, and runbook) are in the course template set: [Agent Operating System Templates](https://www.billmongan.com/Ursinus-CS357/files/agent-templates/README.md).

1.  *Write your own gates.*

   - *What to do:* Take the `SYSTEMPROMPT.md` template and rewrite §9 for **your** life: identify every irreversible action an assistant with your accounts could take (think: messages, money, grades, publishing, deletion), sort each into a gate category, and write the confirmation-display rule for the two you consider most dangerous.  Then classify 10 actions you'd actually delegate into Autorun / Queue / Forbidden.
   - *Starter hint:* Start from your sent-mail folder, bank statement, and GitHub activity for the past week; everything there was an irreversible action *you* took.  Which would you let hermes take?
   - *You've succeeded when:* A teammate can take your policy and correctly classify three actions you didn't list, and at least one Forbidden item is something no approval should ever make safe.

2.  *Build one no-agent routine.*

   - *What to do:* Write a deterministic script (no LLM call) that produces your own "morning brief" from at least two real sources you can read programmatically (a calendar export, a task list file, your vault's task pages, a GitHub notifications feed).  Follow the production conventions: empty output = no message; no source-system mutations; output to a local report file.
   - *Starter hint:* An `.ics` export and a Markdown task list are enough.  The interesting design decision is the *filter*: what earns a line in the brief?  Deadline radar (next 14 days) is a good default.
   - *You've succeeded when:* Running it twice in a row produces identical output (determinism), and on a day with nothing actionable it prints nothing at all.

3.  *Harness a weak model.*

   - *What to do:* Using a small local model from your course stack (deliberately not your best model), run one nontrivial task twice: once with a plain prompt, once under the harness: Gate 1 criteria, Gate 2 plan-with-checks, a coverage matrix you keep in a file, and a blind cross-check by a *fresh* session that sees only the criteria and the artifact.
   - *Starter hint:* Good task shape: "produce a study guide covering all 6 Key Concepts from activity X, each with an example not from the activity."  Criteria are then countable, and the blind verifier can check coverage mechanically.
   - *You've succeeded when:* You can point to at least one defect the harness caught that the plain run shipped, or, if both succeeded, you can say precisely which harness step was wasted effort for this task and why.

---

## Reflection Prompt

*Personal:* The production system's owner never granted send-access to email, after a full year of daily, trusted use.  Is there any evidence bar after which *you* would grant it?  Name the bar concretely, or argue why "drafting yes, sending no" should be permanent.

*Technical:* In your notebook: this system survives model swaps because its "operating system" is written down outside the model.  List the artifacts from this activity in order of how expensive each would be to reconstruct if lost.  What does that ordering tell you about what to version, back up, and write first?

*Societal:* A chief-of-staff agent reads your email, calendar, finances, and notes, a more complete picture of you than any single human has.  The vault architecture keeps that picture in *your* repository rather than a vendor's servers, but the model calls still transit a provider.  Who should bear the legal duty of care for this aggregation: you, the model provider, the tool vendors, or nobody (caveat emptor)?  Defend one position.

---

## -> Coming Up Next

You now have both halves of the governance story: charters and handoffs for agents that build software, and gates, routines, and self-updating memory for an agent that runs a life.  The remaining modules put these to work at team scale (multi-agent debate, consensus, and agent teams) where every lesson about traceability and verification applies *between* agents, not just between an agent and you.

---

## 8.  Further Reading

- The course template set for this activity: [Agent Operating System Templates](https://www.billmongan.com/Ursinus-CS357/files/agent-templates/README.md).
- This course: [The Second Brain](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-secondbrain.md) (the foundation this activity builds on), [Human-in-the-Loop](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-humanintheloop.md) (the theory behind the gates), [Governing Coding Agents](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-agentgovernance.md) (the companion case study), and [Agent Skills and Plugins](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-agentskills.md) (the skill format this system's inventory manages).
- Model Context Protocol documentation. https://modelcontextprotocol.io, the integration layer behind the tool connections in Part III.
- Atul Gawande.  *The Checklist Manifesto*.  Metropolitan Books (2009).  Why written procedure outperforms expert memory in high-stakes operations, the human-institutions version of everything in this activity.
