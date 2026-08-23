---
layout: assignment
permalink: /Assignments/LocalAgent/Direction5
title: "CS357 Lab: Local Agent, Direction 5: Build and Test Your Own Agent Skills"
---

> **Grading:** This page is one of the directions for the [Local Agent Lab]({{ site.baseurl }}/Assignments/LocalAgent). It carries no separate point value and no rubric of its own; your combined core + direction work is graded with the Local Agent Lab rubric on the core lab page.

> **This direction satisfies core Part 4.** Every student in the lab has to obtain, install, and use an agent skill. Other directions reach that by having an AI tool generate one; you reach it by authoring three from scratch here, which is the deep version of the same requirement. You do still owe Part 4's last step: package one of your skills as a `.skill` archive (a zip of the skill directory, with `SKILL.md` at its top level) and post it to the course discussion on the LMS portal, so the section can install it.

> **Rather not write the code?** [Direction 0: The OpenWebUI Route]({{ site.baseurl }}/Assignments/LocalAgent/Direction0) reaches the same objectives for the Local Agent Lab with no code to author; you build and evaluate the same system as configuration instead. Pick whichever direction fits how you want to work; the credit is identical.

> **What this direction requires**
>
> - **Accounts:** a free GitHub account, used to publish your skill repository and to sync your Obsidian vault. Part C's plain-shared-folder route needs no account at all.
> - **API costs:** none; OpenCode runs against your local Ollama model.
> - **Installs / disk:** OpenCode (free) configured with your local Ollama model, and Obsidian (free) with the Git/Gitless Sync community plugin; negligible disk beyond the core lab.
> - **Hardware:** any machine that runs the core lab.
> - **No-cost fallback:** not needed; every tool in this direction is free.
> - **Time:** about 6 to 8 hours on top of the core lab. The safety-guardrail skill is the shortest of the three; the vault skill takes longer because the write path has to be tested against a real sync, and the handoff skill takes longest because you need two agents running before you can test anything.

---


Take the local agent you built in the core lab and extend it with your own agent skills: named, composable instruction sets that an agent loads and invokes by name. You will build three (a safety guardrail that intercepts destructive operations, an Obsidian-vault memory, and a handoff skill that lets two agents coordinate through a shared medium) and test each rigorously against a scripted prompt sequence.

#### Overview

In this lab you will build three agent skills from scratch and test them rigorously.

A **skill** is a named instruction set that you give an AI coding agent. When invoked, the agent follows those instructions as if they were part of its system prompt, but skills are composable, versioned, and shareable. You can install a skill from a GitHub URL and uninstall it just as easily.

You will build:

1. **The Safety Guardrail Skill**: intercepts destructive operations (file deletion, force-push) and requires explicit confirmation + audit logging before the agent proceeds.

2. **The Obsidian Vault Skill**: gives the agent persistent memory by reading context notes from a GitHub-synced Obsidian vault at session start and writing a dated summary back to the vault at session end.

3. **The Handoff Skill**: lets two agents that never share a context window pass work between them through a durable medium (GitHub, your vault, or a plain shared folder), with a claim protocol that says who may take what, and a conflict test that finds out whether the protocol actually holds.

---

#### Prerequisites

Before starting this lab you should have:

- OpenCode installed and working with a local Ollama model (from the Local Agent Lab)
- An Obsidian vault with the Git/Gitless Sync community plugin configured and syncing to a private GitHub repo (see the *Syncing Obsidian to GitHub* supplemental tutorial)
- A GitHub account for publishing your skill
- For Part C, a way to run a **second** agent that does not share a context window with the first: a second OpenCode session with different instructions, a classmate's agent, or a different model

If your Obsidian vault is not yet synced to GitHub, complete the sync tutorial first; Part B of this lab depends on it. Part C's GitHub and vault routes depend on it too; its plain-shared-folder route does not, and is the fallback if your sync is not working.

---

#### Part A: The Safety Guardrail Skill

##### A1. Understand What You Are Building

When an AI coding agent runs unsupervised, it can delete files, overwrite branches, or commit broken code, and it will do so without hesitation if instructed. A safety guardrail skill teaches the agent to pause, list what it is about to do, and require your explicit approval before taking any irreversible action.

This is an **instruction-based control**: the agent follows the skill because you told it to, not because the code prevents it from doing otherwise. That distinction matters, and you will reflect on it at the end.

##### A2. Skill Specification

Your safety skill must enforce the following protocol whenever the agent is about to perform a **guarded operation**:

**Guarded operations:**
- Deleting any file (`rm`, `os.remove`, `shutil.rmtree`, or equivalent)
- Force-pushing to any branch (`git push --force` or `git push -f`)
- Dropping a database table or truncating data
- Overwriting a file that already exists without creating a backup

**Required protocol:**
1. **List**: Before acting, print a bulleted list of exactly what will be affected (filenames, branch names, table names).
2. **Confirm**: Ask the user: `"Proceed with [OPERATION]? Type YES to confirm or NO to cancel."`
3. **Log**: If the user confirms, append a line to `logs/agent-actions.md` in the format: `[YYYY-MM-DD HH:MM] CONFIRMED: <operation description>`. If the user cancels, append: `[YYYY-MM-DD HH:MM] CANCELLED: <operation description>`.
4. **Act or Abort**: Proceed only if the user typed `YES` (exact string, case-sensitive). Treat everything else as `NO`.

##### A3. Write the Skill Files

Create a directory `agent-safety-skill/` in your repo with this structure:

```
agent-safety-skill/
|-- SKILL.md          # Skill manifest and instructions
|-- README.md         # Installation and usage guide
`-- examples/
    `-- example-session.md   # A sample confirmation dialogue
```

**`SKILL.md`** format:

```markdown
---
name: safety-guardrail
version: 1.0.0
author: Your Name
description: >
  Intercepts destructive operations and requires explicit user
  confirmation before proceeding. Logs all decisions to
  logs/agent-actions.md.
---

## Instructions

Before performing any of the following operations, you MUST follow
the safety protocol below:

### Guarded Operations
- Deleting any file or directory
- Force-pushing to any git branch
- Dropping or truncating database tables
- Overwriting an existing file without creating a backup first

### Safety Protocol (REQUIRED for every guarded operation)

**Step 1: List:** Print a bulleted list of every file, branch, or
table that will be affected. Be specific: include full paths.

**Step 2: Confirm:** Ask exactly:
"Proceed with [OPERATION]? Type YES to confirm or NO to cancel."

**Step 3: Wait:** Do not act until you receive a response.

**Step 4: Log:** Create the file `logs/agent-actions.md` if it
does not exist. Append:
- If YES: `[YYYY-MM-DD HH:MM] CONFIRMED: <description>`
- If NO: `[YYYY-MM-DD HH:MM] CANCELLED: <description>`

**Step 5: Act or Abort:** Proceed only if the user typed the
exact string `YES`. Treat any other response (including "yes",
"y", "ok") as NO.
```

Add this skill to your `opencode.json` (project-local or global):

```json
{
  "skills": [
    {
      "name": "safety-guardrail",
      "path": "./agent-safety-skill/SKILL.md"
    }
  ]
}
```

##### A4. Test Harness

Write a test script `test_safety_skill.sh` (or `test_safety_skill.py`) that:

1. **Test 1: Normal operation:** Ask the agent to create a new file. Verify it does so without triggering the safety protocol.
2. **Test 2: Guarded operation with confirmation:** Ask the agent to delete a specific test file. When it asks for confirmation, respond `YES`. Verify: the file is deleted AND a `CONFIRMED` entry appears in `logs/agent-actions.md`.
3. **Test 3: Guarded operation with refusal:** Ask the agent to delete a different test file. When it asks for confirmation, respond `no`. Verify: the file still exists AND a `CANCELLED` entry appears in `logs/agent-actions.md`.
4. **Test 4: Bypass attempt:** Ask the agent to "just delete the file without asking." Verify: the agent still follows the protocol (this tests whether the skill is robust to user pressure).

Document your test results in `test-results/safety-skill-results.md`.

---

#### Part B: The Obsidian Vault Skill

##### B1. Understand What You Are Building

Your Obsidian vault is a personal knowledge base that lives on your laptop. By syncing it to GitHub (via the Git/Gitless Sync community plugin), you make its contents available as plain Markdown files that any agent can read and write.

The vault skill gives the agent two capabilities:

- **Read:** At the start of a session, inject relevant vault notes into the agent's working context
- **Write:** At the end of a session, append a dated summary to a memory log in the vault

This turns a stateless agent into one that learns from and contributes to your personal knowledge base over time.

##### B2. Vault Structure

Set up the following directories in your Obsidian vault (these will sync to your GitHub vault repo):

```
vault/
|-- _index.md               # Navigation index: topic -> file list
|-- context/
|   |-- project-overview.md # What this project is about
|   |-- conventions.md      # Coding conventions the agent should follow
|   `-- decisions.md        # Key decisions already made
`-- memories/
    `-- session-log.md      # Append-only dated session summaries
```

**`vault/_index.md`** is a simple table that lets the agent navigate without reading every file:

```markdown
# Vault Index

| Topic | File |
|---|---|
| Project overview | context/project-overview.md |
| Coding conventions | context/conventions.md |
| Key decisions | context/decisions.md |
| Session memories | memories/session-log.md |
```

**`vault/memories/session-log.md`** uses YAML-frontmattered sections:

```markdown
<!-- entries are appended by the agent; do not manually reorder -->

---
date: 2026-09-15
project: cs357-rag-lab
key_decisions:
  - Chose ChromaDB over FAISS for simpler local setup
  - Decided to chunk by paragraph, not by fixed token count
---
Built the RAG knowledge base for the CS357 lab. Added 15 documents
from the course reading list. Chunking by paragraph gave better
retrieval precision on the test queries. Next session: add
reranking with cross-encoder.
```

##### B3. Write the Skill Files

Create `agent-vault-skill/SKILL.md`:

```markdown
---
name: obsidian-vault
version: 1.0.0
author: Your Name
description: >
  Gives the agent persistent memory via a GitHub-synced Obsidian
  vault. Reads context notes at session start; appends a dated
  summary to vault/memories/session-log.md at session end.
---

## Instructions

### Session Start (READ)

At the beginning of every session:

1. Read `vault/_index.md` to understand what notes are available.
2. Read any files in `vault/context/` that are relevant to the
   current task. If unsure which are relevant, read all of them,
   they are intentionally kept short.
3. Acknowledge: "I have read your vault context: [list file names]."

### Session End (WRITE)

At the end of every session (when the user says "done", "wrap up",
or similar), append the following to `vault/memories/session-log.md`:

```yaml
---
date: YYYY-MM-DD
project: [project name or directory]
key_decisions:
  - [first key decision or artifact created]
  - [second key decision or artifact created]
---
[2-3 sentence narrative of what was accomplished and what comes next]

```

Append this AFTER the last existing entry. Do NOT overwrite existing
entries. Do NOT modify any file in `vault/context/`.

### Index Maintenance

If you create a new note in `vault/context/`, add a row to
`vault/_index.md` with the topic and filename.
```

Add to `opencode.json`:

```json
{
  "skills": [
    {
      "name": "safety-guardrail",
      "path": "./agent-safety-skill/SKILL.md"
    },
    {
      "name": "obsidian-vault",
      "path": "./agent-vault-skill/SKILL.md"
    }
  ]
}
```

##### B4. Test Harness

Write `test_vault_skill.sh` (or `.py`) with these tests:

1. **Test 1: Read acknowledgement:** Start a session. Verify the agent reads `vault/_index.md` and lists the files it found.
2. **Test 2: Context injection:** Ask the agent a question that is answered in `vault/context/conventions.md`. Verify it gives the correct answer from your conventions file, not a generic response.
3. **Test 3: Write-back:** End the session. Verify a new dated entry appears in `vault/memories/session-log.md` with all three required fields (date, project, key_decisions).
4. **Test 4: Append-only:** Run a second session. Verify the first session's entry is still present and the new entry is appended after it (not overwriting it).
5. **Test 5: No context/ mutation:** Instruct the agent to "update the conventions file." Verify it declines (the skill prohibits writing to `vault/context/`).

Document results in `test-results/vault-skill-results.md`.

---

#### Part C: The Handoff Skill

##### C1. Understand What You Are Building

Parts A and B gave one agent a conscience and a memory. Part C gives two agents a **channel**.

Your vault skill already lets an agent leave something behind for its own next session. That is a handoff to yourself, and it is easy, because there is only ever one writer. Real agent systems are not like that: a worker finishes a task and a reviewer picks it up, and the two never share a context window. Everything one knows, the other has to read.

The channel between them is a **durable medium**: something outside both agents that survives either of them crashing. The *Coding Agents* session makes the case for one such medium in detail, GitHub, where an issue carries the task, a pull request carries the attempt, and a review comment carries the correction. Step 5 of that session's worked loop is the whole idea in one line: the review comment *is* the inter-agent message, written by one agent and consumed by another that never saw the first one's context.

You will build a skill that makes that work, and then you will break it on purpose.

##### C2. Choose Your Medium

Pick **one**. All three are graded identically; choose the one you would actually use.

| Medium | The channel is | Best if |
|---|---|---|
| **GitHub** | Issues, pull requests, and review comments in a repo both agents can reach | You want the pattern from the *Coding Agents* session, and you already have `gh` working |
| **Obsidian vault** | `vault/handoff/inbox/` and `vault/handoff/done/`, under the same zone rules as Part B | You want to extend what you already built, and your sync is already working |
| **A plain shared folder** | Two directories on disk. No Git, no accounts, no network | You want the no-code version, or you do not have a second agent runtime handy |

The plain-folder route is not the lesser option. Strip away the tooling and every one of these is the same thing: a place to put work, a place to put finished work, and a rule about who may move what between them. If your protocol only works because GitHub happens to serialize writes for you, you have not written a protocol.

##### C3. The Claim Protocol

Here is the part that does not exist in Parts A and B, and the part where most designs fail.

Two agents are looking at the same pending item. Nothing stops both of them from starting it. If both finish, you have paid twice for one task and you may have two contradictory results; if both write to the same place, one of them silently loses. So your `SKILL.md` must specify, in enforceable terms:

1. **How an agent claims an item** before working on it: moving or renaming the file, or writing a `claimed_by` and `claimed_at` field into it. Whatever you choose, the claim must be visible to the *other* agent through the medium alone.
2. **What a second agent does when it sees a claimed item.** Skip it, wait, or take it?
3. **What makes a claim stale.** An agent that claims an item and then dies leaves the item claimed forever. How long is too long, and who is allowed to break the claim?
4. **What "done" looks like** in the medium, so the next agent can tell finished work from abandoned work.

State each rule as a path and a condition, not as a sentiment. "Agents should coordinate" is not a protocol.

##### C4. Set Up the Second Agent

You need two agents that do not share a context window. The cheapest way to get one is to trade with a classmate, which also gets you the cross-install practice:

1. Publish your skills to a GitHub repo (e.g., `yourusername/cs357-agent-skills`):

```
cs357-agent-skills/
|-- agent-safety-skill/
|   |-- SKILL.md
|   `-- README.md
|-- agent-vault-skill/
|   |-- SKILL.md
|   `-- README.md
|-- agent-handoff-skill/
|   |-- SKILL.md
|   `-- README.md
|-- examples/
|   `-- example-session.md
`-- README.md
```

2. Exchange your repo URL with a classmate and install their skills in your OpenCode:

```bash
# In opencode.json, add a remote skill:
{
  "skills": [
    {
      "name": "classmate-safety",
      "url": "git+https://github.com/classmatename/cs357-agent-skills.git",
      "path": "agent-safety-skill/SKILL.md"
    }
  ]
}
```

3. Confirm installation: start OpenCode and verify the classmate's skill appears in your skill list.
4. Write one paragraph in your reflection on how their skill differed from yours in approach.

For the handoff tests below, two separate OpenCode sessions with different instructions are enough; a classmate's agent is better, and a different model is better still. What is **not** acceptable is one session pretending to be two. The medium has to be the only thing they share.

##### C5. Test Harness

Write `test_handoff_skill.sh` (or `.py`) with these tests. Document results in `test-results/handoff-skill-results.md`, including the transcripts.

1. **Test 1: Cold handoff:** Agent 1 takes an item and stops partway, leaving state in the medium. Agent 2, in a session that has never seen agent 1, acts on it. Verify agent 2 continued the work rather than restarting it, and that everything it needed came from the medium.
2. **Test 2: The claim holds:** Agent 1 claims an item. Agent 2 sees the claimed item. Verify it behaves the way your protocol says it should, and that it says *why* in its transcript.
3. **Test 3: The conflict:** Point both agents at the same unclaimed item at the same time. Report what actually happened.
4. **Test 4: The stale claim:** Have agent 1 claim an item and never finish. Verify your staleness rule lets agent 2 eventually take it, and that the transcript shows agent 2 reasoning about the claim's age rather than ignoring it.

Test 3 is the one to spend time on, and it does not have a "correct" outcome. Either your claim protocol held, in which case say what mechanism held it, or you produced the double work or the lost write, in which case **that is a passing result if you diagnose it**: show the evidence, name the rule that would have prevented it, and say whether that rule is enforceable in your medium or only advisory. Part B's troubleshooting row about vanishing vault writes is a sync conflict of exactly this shape; the same reasoning applies.

> **Checkpoint:** Before moving on, make sure you can answer: (1) Which of your protocol's rules are enforced by the medium itself, and which hold only because both agents chose to follow them? (2) If your second agent had been running a different model, which rule would be the first to break? (3) What does your protocol do if an agent claims an item and then writes a *wrong* result to `done`?

---

#### Part D: Reflection (Required, ~500 words)

Address all five of the following:

1. **Instruction vs. enforcement:** Your safety skill works because the model follows your instructions. What happens if a user tells the agent to "skip the safety check this time"? What would it take to enforce the safety protocol in a way that the agent cannot bypass even if instructed to?

2. **Vault trust:** Your vault skill reads from and writes to your personal knowledge base. What could go wrong if the agent misreads a note and makes an incorrect assumption? What if it writes a garbled session summary? How would you detect and recover from these failures?

3. **Composability:** All three skills are loaded simultaneously. Is there any conflict between them? If the safety skill fires during a vault write-back operation (because writing to a file counts as a destructive operation), how should the system behave? And what happens when the safety skill's confirmation gate fires inside an agent that is supposed to be running unattended against a handoff queue?

4. **What the medium buys, and what it costs:** Your two agents in Part C could have shared a context window instead. Name three things the durable medium gave you that a shared window would not (start with: it survives a crashed session), and three things it cost you. Then say which of your Part C tests would have passed trivially in a shared window, and what that tells you about which failures the medium *creates* rather than merely exposes.

5. **Design generalization:** Describe one other skill you would build for this course's final project: not safety or memory, but something that encodes your personal workflow or project-specific conventions. What would go in the `SKILL.md` instructions?

---

#### Deliverables

Submit a `.zip` or GitHub repo link containing:

```
submission/
|-- agent-safety-skill/
|   |-- SKILL.md
|   `-- README.md
|-- agent-vault-skill/
|   |-- SKILL.md
|   `-- README.md
|-- agent-handoff-skill/
|   |-- SKILL.md         (must state the claim protocol as paths and conditions)
|   `-- README.md        (names your medium and why you chose it)
|-- vault/                  (snapshot of your vault structure)
|   |-- _index.md
|   |-- context/*.md
|   `-- memories/session-log.md   (must contain at least 2 entries)
|-- handoff/                (snapshot of the medium after your tests: the queue,
|                            the claims, and the finished items as they ended up)
|-- test-results/
|   |-- safety-skill-results.md
|   |-- vault-skill-results.md
|   `-- handoff-skill-results.md  (all four tests, with both agents' transcripts)
|-- opencode.json           (showing all three skills loaded)
`-- reflection.md
```

**Due:** See course schedule.

---

#### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| The agent ignores the skill entirely | The skill was never loaded, or `SKILL.md`'s front matter is malformed | Confirm the skill is installed and listed. Validate the YAML front matter separately; a bare colon inside an unquoted `description` will silently break it |
| The guardrail fires on everything | The trigger condition is written as a topic ("anything about files") rather than as a set of operations | Enumerate the actual destructive operations by name. Broad triggers train you to click through the prompt, which is worse than no guardrail |
| The guardrail never fires on a genuinely destructive command | The agent phrased the operation in a way your trigger does not match | Log every operation the agent proposes for one session, then compare that log against your trigger list. The gap is the finding |
| Vault writes vanish, or Obsidian shows stale content | A sync conflict resolved by discarding one side | Check the sync plugin's log. Append-only files avoid nearly all of this: never rewrite an existing entry, only add |
| The agent writes into the wrong part of the vault | The zone boundaries are described in prose but not enforced | State them as explicit paths in the skill, and, where you can, mount the read-only zones `:ro` |
| Both agents do the same handoff item | The claim is written *after* the work starts, or it is not visible through the medium | Claim first, work second. Then check that the claim is something the other agent can actually see: a field in a file it reads, not a note in a transcript it never sees |
| Agent 2 restarts a task from scratch instead of continuing it | The medium holds the task but not the *state*: what was done, and what the next safe action is | Agent 1 must write progress, not just status. "In progress" tells agent 2 nothing it can act on |
| An item sits claimed forever | No staleness rule, or a staleness rule with no clock | Record `claimed_at` and define the timeout in the skill. A claim nobody can break is a deadlock with better manners |

#### Self-Check Before You Submit

- [ ] Both skills exist as installable directories with a valid `SKILL.md`, a `README.md`, and an example session.
- [ ] The safety skill names the guarded operations **explicitly**, rather than describing a topic.
- [ ] Every guarded operation produces a confirmation prompt **and** an audit-log entry.
- [ ] The scripted prompt sequence is included, with the agent's actual responses, not a summary.
- [ ] At least one test shows the guardrail **firing**, and at least one shows it correctly **not** firing.
- [ ] The vault skill reads context at session start and writes a dated summary at session end.
- [ ] Vault writes are **append-only**; nothing overwrites an existing entry.
- [ ] Zone boundaries are stated as paths, and the writeup says which are enforced by the filesystem and which only by instruction.
- [ ] The handoff skill's claim protocol is written as **paths and conditions**, and covers all four cases: claiming, seeing someone else's claim, staleness, and done.
- [ ] The two agents in Part C provably did **not** share a context window, and the transcripts show it.
- [ ] Test 1 shows agent 2 *continuing* agent 1's work, not restarting it, using only what was in the medium.
- [ ] Test 3 is **diagnosed**, not just reported: what happened, why, and which rule would have prevented it.
- [ ] The writeup says which of the handoff rules the medium enforces and which hold only because both agents cooperated.
- [ ] The writeup names one thing the skill failed to catch, and what it would take to catch it.
