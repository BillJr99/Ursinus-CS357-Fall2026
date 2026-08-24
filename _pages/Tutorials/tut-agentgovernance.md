---
layout: default-standard
permalink: /Tutorials/AgentGovernance
title: 'CS357: Foundations of Artificial Intelligence - Governing Coding Agents'
info:
  coursenum: CS357
  purpose: "To follow one real multi-month modernization run by a rotating cast of coding agents, and to extract the charters, handoffs, and durable memory that kept it coherent."
tags:
- case-study
- coding-agents
- governance
---
# CS357: Foundations of Artificial Intelligence - Governing Coding Agents

## Purpose

To follow one real multi-month modernization run by a rotating cast of coding agents, and to extract the charters, handoffs, and durable memory that kept it coherent.

## About This Tutorial

This is a case study of a real production system, anonymized.  A single engineer ran a **multi-month modernization of a legacy codebase** using a rotating cast of coding agents: different vendors, different CLIs, different context windows, sessions that died mid-task when quotas ran out.  The project survived every one of those interruptions, because it was governed by one organizing idea:

> **The repository is the durable memory for the project.  Conversation history is not durable project state.**

You have already learned to write project instructions in an `AGENTS.md` file and to work spec-first with tests.  This tutorial is about the layer above that: the *constitution*, the *handoff protocol*, and the *decision record* that let agents come and go while the work continues.  Here is the path for today: **the read-order funnel $\rightarrow$ the charter $\rightarrow$ the `.ai/` handoff directory $\rightarrow$ kickoff prompts and decision records $\rightarrow$ the disposable devbox**.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|------|--------------------------|--------------------------|
| **Charter** | The project's constitution: mission, ranked priorities, rules, milestones, and guardrails, written down once and treated as the highest authority in every agent session. | A `CHARTER.md` whose Documentation Authority Rule overrides anything an agent "remembers" |
| **Documentation Authority Rule** | The rule that written project documentation always beats an agent's memory: if the docs conflict with remembered context, the docs win; if the docs are incomplete, fix the docs. | An agent that "remembers" a build step from a prior session must re-read `docs/` instead of acting on the memory |
| **Handoff State** | The small set of files an agent must update before stopping *for any reason*, so that a brand-new agent can continue safely with zero conversation history. | `.ai/SESSION.md` and `.ai/CURRENT_TASK.md`, each ending with a "Next Safe Action" |
| **Kickoff Prompt** | A versioned, paste-into-a-fresh-agent prompt that boots a session: role, source of authority, read order, scope boundary, prohibitions, and a required closing report. | A kickoff prompt on its fourth revision; the prompt itself is engineered and iterated like code |
| **Decision Record** | A durable trace of *why* the project evolved as it did: RFCs for proposals, a decision log for outcomes, a forensics table for inherited work. | A log entry with decision, rationale, alternatives considered, and long-term implications |
| **Milestone Gate** | A hard stop between project phases: the agent must halt at the end of a milestone and wait for explicit human direction before starting the next. | "Stop after Milestone 0 is complete. Do not begin Milestone 1 until explicitly directed." |

---

# Part I: The Repository as Durable Memory

In this part, you will trace what a brand-new agent actually knows at each step of a fixed read order, and see why "just remember what we did yesterday" is not an engineering strategy.

## 1.  The Read-Order Funnel

**Why this matters:** Every agent session eventually ends: a context window fills, a five-hour quota expires, a laptop reboots, or you simply switch to a cheaper model.  If the project's state lives in the conversation, every one of those events is a partial project loss.  The case-study project treats agent sessions the way good distributed systems treat servers: *any node can fail at any moment, so no node may hold unique state.*  All durable state lives in files, and every new session begins with the same fixed read order:

1. `START_HERE.md`: the entry funnel and ground rules (one page)
2. `CHARTER.md`: the constitution; all authority derives from it
3. `docs/ROADMAP.md`: the milestone status board
4. `.ai/CURRENT_TASK.md`: active milestone, active subtask, next immediate action
5. `.ai/SESSION.md`: the running engineering log (most recent entry at minimum)
6.  The most recent Git commit or commits: the ground truth

The order is not arbitrary: it moves from *most stable* (the mission never changes mid-week) to *most volatile* (the session log changes hourly), so that each document is interpreted in the frame established by the one before it.

---

## What Does a Fresh Agent Know?

A new agent with no conversation history is pointed at the funnel.  After each read, its knowledge grows:

| After reading... | The agent can now answer... | But still cannot answer... |
|---|---|---|
| `START_HERE.md` | "What are the ground rules? What do I read next?" | "What is this project?" |
| `CHARTER.md` | "What is the mission? What are the ranked priorities? What is forbidden?" | "What has been done so far?" |
| `docs/ROADMAP.md` | "Which milestones are complete? Which is active?" | "What exactly is in flight right now?" |
| `.ai/CURRENT_TASK.md` | "What is the active subtask, its completion criteria, and the next immediate action?" | "What did the last session actually do and verify?" |
| `.ai/SESSION.md` | "What happened last session, what was validated, and what is the Next Safe Action?" | "Does the working tree really match what the log claims?" |
| `git log` / working tree | Everything above, *verified against reality* | - |

### Questions to Work Through

1.  The Documentation Authority Rule from the case-study charter reads: *"If project documentation conflicts with remembered context, prior chat context, historical notes, or assumptions, the project documentation wins.  If the documentation is incomplete, update it rather than relying on memory."*  What failure mode is this rule designed to prevent, and why does it name *four* different sources that lose to the documentation?

   > *Hint: Think about what an agent's context window contains after summarization or after a long session, and what happens when a confident-but-stale "memory" of the build process meets a repository that changed last week.*

2.  Why is the Git log placed *last* in the read order rather than first, given that it is called "the ground truth"?

   > *Hint: A diff is only meaningful if you know what the project is trying to do.  What frame do the earlier documents provide that makes the commits interpretable?*

3.  The case-study project also enforced: *"Do not claim that a file, artifact, log, or generated output is missing or present without checking the current repository/runtime state first.  Treat prior logs and memory as hints only."*  Relate this rule to what you learned about hallucination earlier in the course.  Why are agents *especially* prone to this failure on long-running projects?

   > *Hint: In the Why Different Answers Every Time?  Sampling, Temperature, and Generation activity you saw that models generate plausible continuations.  What makes "the file we created last time is still there" an extremely plausible (and frequently wrong) continuation?*

> **Common Misconception:** "Good agents have long context windows now, so this bookkeeping is obsolete."  Context length does not survive a *vendor switch*, a *quota reset*, or a *conversation you deleted*.  The funnel is not a workaround for small contexts; it is what makes the project independent of any one agent, vendor, or session.  It is the same reason teams of humans write documentation even though each human has an excellent memory.

The Documentation Authority Rule says that when an agent's remembered context conflicts with the project documentation, the agent must:

- Trust its memory if the memory is more recent than the document's last commit
- Follow the documentation, and if the documentation is incomplete, update the documentation rather than acting from memory
- Ask the user to adjudicate every conflict before proceeding
- Merge the two by writing its remembered version into the documentation

<details markdown="1"><summary>Answer</summary>

Follow the documentation, and if the documentation is incomplete, update the documentation rather than acting from memory

</details>

---

# Part II: The Charter, a Constitution for Agents

In this part, you will dissect the charter that governed the case-study project and compare its rules to a widely circulated set of rules for AI coding agents distilled from Andrej Karpathy's guidance.

## 2.  Anatomy of a Charter

**Why this matters:** An `AGENTS.md` file (which you built in the *Designing Your AI Development Environment* module) tells an agent how to work in a repository *today*.  A charter answers a harder question: how should *hundreds of sessions by different agents over many months* stay pointed at the same goal?  The case-study charter did this with a few load-bearing sections:

- **Mission**: one product sentence, so every session can test "does my change serve this?"
- **Ranked engineering philosophy**: not a list of values but an *ordered* one (in the case study: correctness-preservation first, then reproducibility, maintainability, automation, documentation).  Ranking resolves mid-task conflicts without a human in the loop.
- **Git policy**: *"Git is the only version history.  Never create `*_new`, `*_old`, `*_backup`, `*_fixed`, or duplicate edited files.  Each commit should represent one logical engineering change."*
- **The task loop**: an 11-step per-task cycle: investigate -> read docs -> read history -> document findings -> short plan -> smallest useful change -> build -> test -> collect logs -> update docs -> commit one logical change.
- **Milestone gates**: Milestone 0 is always *project initialization*: scaffolding, documentation, and inventory only, **no feature work**, followed by a hard stop: *"Stop after Milestone 0 is complete.  Do not begin Milestone 1 until explicitly directed."*
- **A regression rule**: *"Whenever a bug is fixed, create a regression test that would have detected it."*
- **A closing standard**: *"The repository should become easier for the next contributor than it was for the current contributor."*

---

## The Charter Meets Karpathy's Rules

A community template known as the "Karpathy `CLAUDE.md`," distilled from Andrej Karpathy's talks and posts about working with coding agents, circulates four core rules.  Compare them with the case-study charter:

| Karpathy-style rule | What it demands of the agent | Where the charter encodes the same idea |
|---|---|---|
| **Think before coding** | State assumptions, surface multiple interpretations, push back when the request seems wrong, stop when confused | Task-loop steps 1-5 (investigate, read, document findings, plan) come *before* any code |
| **Simplicity first** | The minimum code that solves the problem; nothing speculative | "Implement the smallest useful change"; the `FUTURE_WORK.md` parking lot keeps speculation out of the diff |
| **Surgical changes** | Touch only what needs to change | "One logical engineering change" per commit; the git policy against duplicate/backup files |
| **Goal-driven execution** | Verifiable success criteria, tests-first | Completion criteria in `CURRENT_TASK.md`; the regression rule; milestone success criteria |

The two documents were written independently; the convergence is the interesting part.  Both discover that the failure modes of capable agents are *eagerness* failures (acting before understanding, changing more than asked, declaring victory without verification), so both spend most of their rules slowing the agent down at exactly those three moments.

### Questions to Work Through

1.  Why does *ranking* the engineering philosophy matter more than listing it?  Construct a concrete mid-task conflict between two values on the list, and show how a ranked list resolves it without asking the human.

   > *Hint: Suppose adding an automated test (automation) requires restructuring a module in a way that risks changing behavior (correctness/preservation).  What does the agent do if the values are ranked?  Unranked?*

2.  Milestone 0 forbids feature work entirely; an agent's first sessions produce only scaffolding, documentation, and an inventory of the inputs.  What does this gate buy the project, given that agents are *most* error-prone when they know *least* about a codebase?

   > *Hint: What is the blast radius of a wrong assumption made in week one versus the same wrong assumption made after an inventory exists?  What artifact does Milestone 0 leave behind that every later session reads?*

3.  The Karpathy-style rules and the charter both distrust "declaring victory."  Find the *two* distinct mechanisms in the charter sections above that force verification, and explain what category of false claim each one catches.

   > *Hint: One mechanism runs during the task loop; the other is created in response to a failure.  Consider the difference between "my change works" and "my fix stays fixed."*

> **Common Misconception:** "A charter is just a longer system prompt."  A system prompt configures *one agent in one session*.  The charter is **agent-independent**: it is read by whichever agent shows up, it is versioned in Git, it survives every session boundary, and (because of the Documentation Authority Rule) it outranks whatever any individual session believes.  The system prompt is the *voice*; the charter is the *law*.

Why does the case-study charter make Milestone 0 (initialization: docs, scaffolding, inventory, no features) mandatory with a hard stop at its end?

- Because feature work is impossible before continuous integration is configured
- To give the human time to select which agent vendor to use for the project
- Because agents are most error-prone when they know least; the gate limits early blast radius and forces the project to become documentable-by-a-fresh-agent before anything irreversible happens
- Because Git repositories require an initial commit before branches can be created

<details markdown="1"><summary>Answer</summary>

Because agents are most error-prone when they know least; the gate limits early blast radius and forces the project to become documentable-by-a-fresh-agent before anything irreversible happens

</details>

---

# Part III: The `.ai/` Handoff Directory

In this part, you will examine the six files that let an agent be swapped mid-project, and practice executing a clean handoff under a quota deadline.

## 3.  Six Files, Six Volatilities

**Why this matters:** The charter is stable law; the work changes hourly.  The case-study project kept the volatile state in a dedicated `.ai/` directory, with each file owning one question a fresh agent must answer:

| File | The question it answers | How often it changes |
|---|---|---|
| `.ai/CONTEXT.md` | "What is this project, in one sentence, and what do I read first?" | Almost never |
| `.ai/CURRENT_TASK.md` | "What exactly is in flight: milestone, subtask, completion criteria, safe handoff point, next immediate action?" | Every task change |
| `.ai/SESSION.md` | "What just happened, what was verified, and what is the Next Safe Action?" | Continuously, a running log, *not* a final summary |
| `.ai/KNOWN_ISSUES.md` | "What verified defects and constraints should I not rediscover?" | As defects are confirmed |
| `.ai/FUTURE_WORK.md` | "Which good ideas are deliberately deferred so they stop competing with the milestone?" | Rarely |
| `.ai/AGENT_HANDOFF_KICKOFF.md` | "If I am a brand-new agent taking over right now, what is my first move?" | Static template |

Two disciplines make the directory trustworthy:

- **Every `SESSION.md` entry ends with a "Next Safe Action"**: the one step a brand-new agent could take without breaking anything.  Superseded guidance is annotated in place ("superseded by the entry below"), never deleted.
- **`CURRENT_TASK.md` contains a "Reality Check"**: a table of what is *not* done, each row citing the command, test, or artifact that proves its status.  It exists to fight the most common agent failure on long projects: quietly inflating "attempted" into "completed."

And one rule makes the whole system work, the handoff rule: *"Before stopping for any reason (user interruption, session exhaustion, context exhaustion, quota exhaustion, or completion of the current task) update the handoff state: `.ai/SESSION.md`, `.ai/CURRENT_TASK.md`, and any affected document under `docs/`."*  The case-study working agreement paired it with limit awareness: *"Monitor visible or inferable session windows, context limits, quota windows, and time-based limits.  If any limit is approaching, stop new work and prepare a clean handoff before failure."*

---

## The Mid-Session Swap

An agent has been refactoring a parser for 40 minutes.  Its quota window expires in ~10 minutes.  Tests currently fail on 2 of 14 cases.  Here are the steps of a clean handoff, **scrambled**:

A. Commit one logical change containing the passing subset of the work, with documentation updates.
B. Append a `SESSION.md` entry: scope, what was completed (with the test command output), what remains, the two failing cases by name, and a Next Safe Action.
C. Stop starting new work the moment the limit is recognized as near.
D. Update `CURRENT_TASK.md`: reality-check table now shows 12/14 passing with the verifying command; next immediate action names the first failing case.
E. A new agent (different vendor) is started later with the `AGENT_HANDOFF_KICKOFF.md` prompt; it reads the funnel and *states the mission, active task, and Next Safe Action before proceeding*.

### Questions to Work Through

1.  Put steps A-E in the correct order, and identify which single step, if skipped, would most likely cause the *next* agent to duplicate or destroy work.  Defend your choice.

   > *Hint: Consider what the new agent reads first, and which document is the only one that distinguishes "12 passing because fixed" from "12 passing because the last two were never run."*

2.  Why does the handoff prompt require the new agent to *state* the mission, active task, and Next Safe Action before proceeding, rather than just telling it to "continue the work"?

   > *Hint: This is a verification gate on comprehension.  What failure does an agent reveal by restating incorrectly, and how cheap is catching it at that moment compared to catching it three commits later?*

3.  The Reality Check table requires each status to cite a verifying artifact ("Verified by: `pytest tests/parser -q`, 2026-06-30").  Explain how this rule interacts with the Documentation Authority Rule from Part I when the *next* session begins.

   > *Hint: The next agent must treat docs as authoritative, but the Reality Check row tells it exactly how to re-establish the claim against live state.  What does that turn a stale claim into, instead of a landmine?*

> **Common Misconception:** "Handoff notes are for when you switch agents."  The case-study rule says *before stopping for any reason*, including finishing normally.  That is because you cannot reliably predict which stop is a swap: the session that "completed its task" on Friday becomes a handoff on Monday when the vendor has an outage and a different CLI picks up the work.  Every stop is treated as a potential handoff, so no stop is a bad one.

Every entry in the case-study `SESSION.md` ends with a "Next Safe Action" because:

- LiaScript requires every log entry to end with an action item
- It lets the project bill sessions accurately to the correct milestone
- A brand-new agent with no conversation history needs exactly one trustworthy, concrete first step, and the outgoing session is the only party that can name it
- It prevents the session log from growing without bound

<details markdown="1"><summary>Answer</summary>

A brand-new agent with no conversation history needs exactly one trustworthy, concrete first step, and the outgoing session is the only party that can name it

</details>

---

# Part IV: Kickoff Prompts and Decision Records

In this part, you will dissect the versioned prompt that boots a cold-start session, and the records that preserve *why* decisions were made.

## 4.  The Kickoff Prompt as Engineered Artifact

**Why this matters:** The case-study project's first-session prompt was a *file* on its fourth revision, versioned like code (through Git commits and an in-file version marker, per the charter's own git policy) because it was iterated like code.  Its structure is a checklist you can reuse for any project:

1.  **Role assignment**: "You are the lead software engineer for the `<ProjectName>` project."
2.  **Source of authority**: "Your authority is derived entirely from the project documentation."  The agent has no standing beyond the docs.
3.  **The mandatory read order**: the funnel from Part I.
4.  **A reframed first objective**: "Your first objective is NOT to `<the obvious end goal>`.  Your first objective is to establish a reproducible engineering baseline."  This single sentence prevents the most expensive failure of a capable agent: sprinting confidently toward the wrong finish line.
5.  **Defensive environment setup**: e.g., probe the local model endpoint over HTTP and continue gracefully without it: "Lack of local model access is not an error."
6.  **Operating rules**: limit awareness, no duplicate work, repository as source of truth.
7.  **Scope boundary**: "Complete Milestone 0 only.  Do not begin Milestone 1."
8.  **An explicit prohibition list**: "Do not modify `<protected areas>`.  Do not move assets.  Do not delete files."
9.  **A required closing report**: "Summary / Files changed / Tests run / Remaining blockers / Suggested next task."

Alongside the prompts, the project kept three kinds of **decision record**:

- **RFCs** (`docs/rfcs/0001-....md`) for proposals: Summary / Motivation / Design / Alternatives / Compatibility Impact / Testing Plan / Documentation Plan / Open Questions.  Some RFCs were two lines long (a status and a pointer) because the *number and the record* matter, not the length.
- **A decision log** for outcomes: decision, rationale, alternatives considered, long-term implications, so "future contributors understand why the project evolved as it did."
- **A forensics table** for inherited work (the project inherited artifacts from earlier, undocumented AI sessions): each claim about the prior work became a row of `Finding | Evidence | Confidence | Action`, under the stance *"treat previous work as archaeology, not as a branch to clean up"*; inherited work is evidence to re-verify, never authority.

### Questions to Work Through

1.  Items 7 and 8 (scope boundary, prohibition list) look redundant with the charter, which already contains the milestone gate and protections.  Why does the kickoff prompt repeat them anyway?

   > *Hint: When is the prompt read relative to the charter?  Consider an agent that partially fails step 3; which document is guaranteed to have been in its context?*

2.  The forensics table assigns each finding a *confidence*, and the prior sessions' own claims are filed under "Non-Authoritative Prior Claims."  Connect this to the LLM-as-judge and evaluation material from this course: why is an AI agent's self-report about its own past work treated as the *least* trustworthy evidence class?

   > *Hint: What incentive gradient does an agent's training create around reporting success?  And what independent artifacts (logs, diffs, test outputs) exist that do not share that gradient?*

3.  Propose a rule for *when* a decision deserves an RFC versus a decision-log entry versus nothing.  Your rule must be executable by an agent without asking a human.

   > *Hint: Think in terms of reversibility and blast radius, the same dimensions the confirmation-gate material in the companion activity uses.*

The kickoff prompt reframes the first objective ("Your first objective is NOT to <the end goal>...") because:

- End goals are secret and should not appear in prompts that may be logged
- A capable agent given the end goal will pursue it immediately; redirecting the first session toward a reproducible baseline prevents fast, confident progress in an unverified direction
- The first session's model is usually too weak to attempt the end goal
- Vendors bill discovery sessions at a lower rate than implementation sessions

<details markdown="1"><summary>Answer</summary>

A capable agent given the end goal will pursue it immediately; redirecting the first session toward a reproducible baseline prevents fast, confident progress in an unverified direction

</details>

---

# Part V: The Disposable Devbox

In this part, you will see how the case-study project ran agents with their permission prompts *disabled*, safely.

## 5.  Auto-Approve, But Only in a Sandbox

**Why this matters:** You learned in the *Terminal and Filesystem Isolation* and *Docker* modules why agents should not roam a host filesystem.  The case-study project drew the logical conclusion: it ran every agent inside a single **disposable container**: rebuilt from a script, destroyed after use (`docker run --rm`), hardened with `no-new-privileges`, with exactly one bind-mounted directory: the repository.  Inside that boundary, each installed agent CLI (there were five, from different vendors) got a wrapper script that launched it with its auto-approve / skip-permissions flag.

That combination is the point, and each half is unsafe without the other:

- **Auto-approve without the sandbox** hands an agent your entire machine on its worst day.
- **The sandbox without auto-approve** wastes the isolation: you built walls and then made a human babysit every command anyway, which reintroduces approval fatigue, and approval fatigue, as you saw in the *Human-in-the-Loop* module, degrades into rubber-stamping exactly when vigilance matters most.

Two more properties completed the pattern: **local-first inference** (the container pointed at a local model server on the host for routine work, with cloud models reserved for hard reasoning) and **agent parity** (all five CLIs shared the same container, same mount, same Git identity, so swapping agents changed *nothing* about the environment, only the brain).

The safety boundary is the sandbox, not the approval prompt.  The *decision* boundary (what the agent is allowed to attempt at all) still lives in the charter and the prohibition lists.  Isolation bounds the damage; governance bounds the intent.

### Questions to Work Through

1.  The only durable surface in the devbox is the mounted repository, which is exactly the thing the agent is supposed to change.  What, then, actually protects the *repository* from a destructive agent inside the sandbox?  Name the two mechanisms from earlier in this tutorial that fill that role.

   > *Hint: One is a property of Git itself given the charter's commit discipline; the other is a document the agent must obey that enumerates what it must never do.*

2.  Approval fatigue and sandboxing are both responses to the same tension.  State the tension in one sentence, and explain why "sandbox + auto-approve + charter" resolves it better than "host access + per-command approval."

   > *Hint: Where does each design place the human's finite attention, on individual commands, or on reviewing outcomes (diffs, logs, session entries)?*

In the devbox pattern, agents run with permission prompts disabled.  This is acceptable because:

- The agents used were verified by their vendors to be incapable of destructive commands
- The local model is too small to generate dangerous shell commands
- The container is disposable, privilege-restricted, and exposes only the mounted repository, so the sandbox is the safety boundary, and Git history plus the charter's prohibitions govern what happens to the one durable surface
- Auto-approve flags only apply to read-only commands

<details markdown="1"><summary>Answer</summary>

The container is disposable, privilege-restricted, and exposes only the mounted repository, so the sandbox is the safety boundary, and Git history plus the charter's prohibitions govern what happens to the one durable surface

</details>

---

# Part VI: Synthesis and Practice

## 6.  Exercises

Copy-paste starting points for every document in this tutorial are in the course template set: [Agent Operating System Templates](https://www.billmongan.com/Ursinus-CS357/files/agent-templates/README.md).

1.  *Charter a project you actually have.*

   - *What to do:* Take any project you are running this semester (your Project Thread system, a lab, a personal repo) and fill in the `CHARTER.md` template: mission (one sentence), a **ranked** five-item engineering philosophy, a definition of success a fresh agent could test, one milestone with objectives/deliverable/success criteria, and the Milestone-0 stop rule.  Delete every template section you cannot honestly enforce.
   - *Starter hint:* The ranking is the hard part; force yourself to break ties.  If you cannot decide whether reproducibility outranks documentation for your project, invent a conflict scenario and see which loss hurts more.
   - *You've succeeded when:* A teammate reading only your charter can correctly answer: "The agent found a shortcut that speeds up the build but changes output formatting; may it take the shortcut?"

2.  *Run a real handoff.*

   - *What to do:* Start a coding agent (any CLI from the coding-agents lab) on a small task in a repo containing the `.ai/` templates.  Interrupt it deliberately at the halfway point and require it to write the handoff state (`SESSION.md` entry with Next Safe Action, updated `CURRENT_TASK.md` with a Reality Check row).  Then open a **different** agent (or a fresh session with history cleared), paste the `AGENT_HANDOFF_KICKOFF.md` prompt, and let it finish the task.
   - *Starter hint:* Pick a task with a visible finish line, such as "make these 6 failing tests pass"; the Reality Check table then writes itself (`3/6 passing, verified by pytest -q`).
   - *You've succeeded when:* The second agent completes the task without redoing the first agent's work and without asking you anything the handoff documents already answered.  If it asks, the answer belongs in a document; add it and note which one.

3.  *Audit an agent's claim.*

   - *What to do:* From any past agent session you have (this course's labs count), find one claim of completion ("all tests pass," "the file was created," "the bug is fixed").  Build a three-row forensics table for it: `Finding | Evidence | Confidence | Action`, where Evidence must be an artifact (test output, commit diff, file listing) that you re-ran or re-checked yourself, not the agent's statement.
   - *Starter hint:* If you cannot find independent evidence for the claim, that *is* the finding: record confidence "low" and action "re-verify before use."
   - *You've succeeded when:* At least one row's confidence surprised you, in either direction, and you can say what artifact was missing that would have made verification trivial.

---

## Reflection Prompt

*Personal:* Which document in this system would you *actually* keep updated under deadline pressure, and which would silently rot first?  What does your answer tell you about where automation (a commit hook, a session-end checklist) should enforce what discipline will not?

*Technical:* In your notebook: the charter, the `.ai/` directory, and the kickoff prompt all redundantly encode some of the same rules.  Is that redundancy a defect (violating "one canonical page per topic") or a feature?  Under what specific failure conditions does the redundancy pay for itself?

*Societal:* This tutorial's system lets one person supervise a rotating cast of autonomous agents doing months of engineering.  If this pattern generalizes, what happens to the apprenticeship pipeline: the junior roles where human engineers traditionally learned judgment by doing the small tasks agents now do?  Who writes the charters in twenty years, and where did they learn how?

---

## Where This Goes Next

The charter governs agents working on a *repository*.  The companion case study, **From Second Brain to Chief of Staff: A Personal Agent in Production**, applies the same governance thinking to an agent wired into your *life*: calendars, task managers, email, and a self-updating knowledge vault, where the irreversible actions are not force-pushes but sent emails and published pages.

---

## 7.  Further Reading

- The course template set for this tutorial: [Agent Operating System Templates](https://www.billmongan.com/Ursinus-CS357/files/agent-templates/README.md).
- Andrej Karpathy.  "Software 2.0."  *Medium* (2017).  The framing that motivates treating specs and docs as the durable program.
- The Menon Lab.  "The Karpathy CLAUDE.md: Four Rules That Fix AI Coding Agents." https://themenonlab.blog/blog/karpathy-claude-md-four-rules-ai-coding-agents: the community distillation compared in Model 2.
- AI Builder Club.  "Karpathy's agents.md: What It Is and Why It Matters." https://www.aibuilderclub.com/blog/karpathy-agents-md-framework: on instruction files as the control layer for coding agents.
- This course: [The Karpathy Coding Approach]({{ site.baseurl }}/Tutorials/VibeCoding) (the workflow this tutorial governs), [Designing Your AI Development Environment](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-designfirst.md) (the `AGENTS.md` layer beneath the charter), and [Terminal and Filesystem Isolation for Agent Safety]({{ site.baseurl }}/Tutorials/FilesystemIsolation) (the sandbox layer beneath the devbox).
