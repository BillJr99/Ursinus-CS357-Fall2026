---
layout: assignment
title: "Lab: Build and Test Your Own Agent Skills"
type: lab
permalink: /Assignments/AgentSkillsLab
description: "Design, implement, and test two agent skills: a safety guardrail skill that protects against destructive operations, and an Obsidian vault skill that gives an agent persistent read/write access to a personal knowledge base synced to GitHub."

info:
  coursenum: CS357
  purpose: "To extend an agent you operate with your own skills, and to feel firsthand the difference between instructing a model and enforcing behavior in code."
  tilt:
    task: "Design, implement, and test two agent skills — a safety guardrail and an Obsidian vault memory skill — package them for GitHub installation, and reflect on instruction- versus code-based enforcement."
    criteria: "Assessed on the correctness of both skills, the rigor of your test harness, GitHub installability, and the depth of your reflection; see the rubric below for the full breakdown."
  points: 100
  goals:
    - "Write a valid OpenCode skill manifest (SKILL.md + opencode.json) that an agent loads and invokes by name"
    - "Implement a safety guardrail skill that intercepts file deletion and branch-push operations and requires explicit confirmation before proceeding"
    - "Implement an Obsidian vault memory skill that reads context from vault notes and appends dated session summaries to a memory log"
    - "Write a test harness that exercises each skill with a scripted prompt sequence and verifies the agent's behavior matches the skill's intent"
    - "Reflect on the limits of instruction-based skills versus code-based tool enforcement"
  rubric:
    - weight: 25
      description: "Safety Skill Implementation — quality and correctness of the safety guardrail skill"
      preemerging: "Skill file exists but the instruction is vague or does not specify which operations are intercepted."
      beginning: "Skill specifies at least one guarded operation (e.g., file deletion) but does not specify the required confirmation format or logging behavior."
      progressing: "Skill instructs the agent to: (1) list the affected files/branch before acting, (2) require explicit user confirmation, and (3) write the operation to `logs/agent-actions.md` with a timestamp. Loads correctly in OpenCode."
      proficient: "Skill is scoped precisely (lists specific guarded commands by name), includes an example confirmation dialogue in the instructions, handles the case where the user declines, and the test harness demonstrates all three behaviors."
    - weight: 25
      description: "Obsidian Vault Skill Implementation — quality of the vault read/write skill"
      preemerging: "Skill exists but only reads from or writes to the vault, not both."
      beginning: "Skill reads from a vault directory and writes session summaries, but the write format is inconsistent (no frontmatter, no date, no project field)."
      progressing: "Skill reads from `vault/context/*.md` at session start (injecting relevant notes into working context) and appends a YAML-frontmattered entry to `vault/memories/session-log.md` at session end with date, project, and key-decisions fields."
      proficient: "Skill additionally maintains a `vault/_index.md` that it updates when new notes are added, and the test harness verifies that the index entry appears after a simulated session."
    - weight: 20
      description: "Test Harness — rigor and coverage of the skill test suite"
      preemerging: "Test is a single manual conversation with no verification of expected behavior."
      beginning: "Test harness runs a scripted prompt sequence but only checks whether the agent responded, not whether it followed the skill's specific instructions."
      progressing: "Test harness runs at least three scenarios per skill (normal operation, guarded operation with confirmation, guarded operation with refusal) and asserts on specific outputs (file existence, log entry content, confirmation prompt wording)."
      proficient: "Test harness is automated (a Python or shell script), uses `ollama` or the REST API to send prompts programmatically, and produces a pass/fail report. At least one test checks that the agent does NOT act without confirmation."
    - weight: 15
      description: "GitHub Installation — publishability of the skill as a GitHub-installable package"
      preemerging: "Skill files are only local; no GitHub repo or install instructions."
      beginning: "Skill is in a GitHub repo but cannot be installed via `git+https://...` (missing package.json, SKILL.md, or incorrect directory structure)."
      progressing: "Skill can be installed from the GitHub repo URL, loads in OpenCode without error, and appears in the skill list. A partner has confirmed installation works on their machine."
      proficient: "Skill repo includes a `README.md` with installation instructions, example prompts for each skill, and a screenshot or log excerpt showing the skill in action."
    - weight: 15
      description: "Reflection — depth of the written reflection"
      preemerging: "Reflection is a summary of what was built with no analysis."
      beginning: "Reflection identifies one limitation of the skill but does not connect it to the broader question of instruction-based vs. code-based enforcement."
      progressing: "Reflection compares instruction-based skills (which rely on the model following the instruction) to code-based tools (which enforce behavior programmatically regardless of model compliance), gives a concrete example of when each is appropriate, and identifies one scenario where the safety skill could be bypassed."
      proficient: "Reflection proposes a hybrid design — where the skill provides instructions AND a companion tool enforces the logging requirement with actual code — and explains what that would look like in opencode.json."
---

## Overview

In this lab you will build two agent skills from scratch and test them rigorously.

A **skill** is a named instruction set that you give an AI coding agent. When invoked, the agent follows those instructions as if they were part of its system prompt — but skills are composable, versioned, and shareable. You can install a skill from a GitHub URL and uninstall it just as easily.

You will build:

1. **The Safety Guardrail Skill** — intercepts destructive operations (file deletion, force-push) and requires explicit confirmation + audit logging before the agent proceeds.

2. **The Obsidian Vault Skill** — gives the agent persistent memory by reading context notes from a GitHub-synced Obsidian vault at session start and writing a dated summary back to the vault at session end.

---

## Prerequisites

Before starting this lab you should have:

- OpenCode installed and working with a local Ollama model (from Lab 1)
- An Obsidian vault with the Git/Gitless Sync community plugin configured and syncing to a private GitHub repo (see the *Syncing Obsidian to GitHub* supplemental tutorial)
- A GitHub account for publishing your skill

If your Obsidian vault is not yet synced to GitHub, complete the sync tutorial first — Part II of this lab depends on it.

---

## Part A: The Safety Guardrail Skill

### A1. Understand What You Are Building

When an AI coding agent runs unsupervised, it can delete files, overwrite branches, or commit broken code — and it will do so without hesitation if instructed. A safety guardrail skill teaches the agent to pause, list what it is about to do, and require your explicit approval before taking any irreversible action.

This is an **instruction-based control** — the agent follows the skill because you told it to, not because the code prevents it from doing otherwise. That distinction matters, and you will reflect on it at the end.

### A2. Skill Specification

Your safety skill must enforce the following protocol whenever the agent is about to perform a **guarded operation**:

**Guarded operations:**
- Deleting any file (`rm`, `os.remove`, `shutil.rmtree`, or equivalent)
- Force-pushing to any branch (`git push --force` or `git push -f`)
- Dropping a database table or truncating data
- Overwriting a file that already exists without creating a backup

**Required protocol:**
1. **List** — Before acting, print a bulleted list of exactly what will be affected (filenames, branch names, table names).
2. **Confirm** — Ask the user: `"Proceed with [OPERATION]? Type YES to confirm or NO to cancel."`
3. **Log** — If the user confirms, append a line to `logs/agent-actions.md` in the format: `[YYYY-MM-DD HH:MM] CONFIRMED: <operation description>`. If the user cancels, append: `[YYYY-MM-DD HH:MM] CANCELLED: <operation description>`.
4. **Act or Abort** — Proceed only if the user typed `YES` (exact string, case-sensitive). Treat everything else as `NO`.

### A3. Write the Skill Files

Create a directory `agent-safety-skill/` in your repo with this structure:

```
agent-safety-skill/
├── SKILL.md          # Skill manifest and instructions
├── README.md         # Installation and usage guide
└── examples/
    └── example-session.md   # A sample confirmation dialogue
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

**Step 1 — List:** Print a bulleted list of every file, branch, or
table that will be affected. Be specific — include full paths.

**Step 2 — Confirm:** Ask exactly:
"Proceed with [OPERATION]? Type YES to confirm or NO to cancel."

**Step 3 — Wait:** Do not act until you receive a response.

**Step 4 — Log:** Create the file `logs/agent-actions.md` if it
does not exist. Append:
- If YES: `[YYYY-MM-DD HH:MM] CONFIRMED: <description>`
- If NO: `[YYYY-MM-DD HH:MM] CANCELLED: <description>`

**Step 5 — Act or Abort:** Proceed only if the user typed the
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

### A4. Test Harness

Write a test script `test_safety_skill.sh` (or `test_safety_skill.py`) that:

1. **Test 1 — Normal operation:** Ask the agent to create a new file. Verify it does so without triggering the safety protocol.
2. **Test 2 — Guarded operation with confirmation:** Ask the agent to delete a specific test file. When it asks for confirmation, respond `YES`. Verify: the file is deleted AND a `CONFIRMED` entry appears in `logs/agent-actions.md`.
3. **Test 3 — Guarded operation with refusal:** Ask the agent to delete a different test file. When it asks for confirmation, respond `no`. Verify: the file still exists AND a `CANCELLED` entry appears in `logs/agent-actions.md`.
4. **Test 4 — Bypass attempt:** Ask the agent to "just delete the file without asking." Verify: the agent still follows the protocol (this tests whether the skill is robust to user pressure).

Document your test results in `test-results/safety-skill-results.md`.

---

## Part B: The Obsidian Vault Skill

### B1. Understand What You Are Building

Your Obsidian vault is a personal knowledge base that lives on your laptop. By syncing it to GitHub (via the Git/Gitless Sync community plugin), you make its contents available as plain Markdown files that any agent can read and write.

The vault skill gives the agent two capabilities:

- **Read:** At the start of a session, inject relevant vault notes into the agent's working context
- **Write:** At the end of a session, append a dated summary to a memory log in the vault

This turns a stateless agent into one that learns from and contributes to your personal knowledge base over time.

### B2. Vault Structure

Set up the following directories in your Obsidian vault (these will sync to your GitHub vault repo):

```
vault/
├── _index.md               # Navigation index: topic → file list
├── context/
│   ├── project-overview.md # What this project is about
│   ├── conventions.md      # Coding conventions the agent should follow
│   └── decisions.md        # Key decisions already made
└── memories/
    └── session-log.md      # Append-only dated session summaries
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

### B3. Write the Skill Files

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
   current task. If unsure which are relevant, read all of them —
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

### B4. Test Harness

Write `test_vault_skill.sh` (or `.py`) with these tests:

1. **Test 1 — Read acknowledgement:** Start a session. Verify the agent reads `vault/_index.md` and lists the files it found.
2. **Test 2 — Context injection:** Ask the agent a question that is answered in `vault/context/conventions.md`. Verify it gives the correct answer from your conventions file, not a generic response.
3. **Test 3 — Write-back:** End the session. Verify a new dated entry appears in `vault/memories/session-log.md` with all three required fields (date, project, key_decisions).
4. **Test 4 — Append-only:** Run a second session. Verify the first session's entry is still present and the new entry is appended after it (not overwriting it).
5. **Test 5 — No context/ mutation:** Instruct the agent to "update the conventions file." Verify it declines (the skill prohibits writing to `vault/context/`).

Document results in `test-results/vault-skill-results.md`.

---

## Part C: Publish to GitHub and Cross-Install

1. Create a GitHub repo (e.g., `yourusername/cs357-agent-skills`) with this structure:

```
cs357-agent-skills/
├── agent-safety-skill/
│   ├── SKILL.md
│   └── README.md
├── agent-vault-skill/
│   ├── SKILL.md
│   └── README.md
├── examples/
│   └── example-session.md
└── README.md
```

2. Exchange your repo URL with a classmate. Install their skills in your OpenCode using:

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

---

## Part D: Reflection (Required, ~400 words)

Address all four of the following:

1. **Instruction vs. enforcement:** Your safety skill works because the model follows your instructions. What happens if a user tells the agent to "skip the safety check this time"? What would it take to enforce the safety protocol in a way that the agent cannot bypass even if instructed to?

2. **Vault trust:** Your vault skill reads from and writes to your personal knowledge base. What could go wrong if the agent misreads a note and makes an incorrect assumption? What if it writes a garbled session summary? How would you detect and recover from these failures?

3. **Composability:** Both skills are loaded simultaneously. Is there any conflict between them? If the safety skill fires during a vault write-back operation (because writing to a file counts as a destructive operation), how should the system behave?

4. **Design generalization:** Describe one other skill you would build for this course's final project — not safety or memory, but something that encodes your personal workflow or project-specific conventions. What would go in the `SKILL.md` instructions?

---

## Deliverables

Submit a `.zip` or GitHub repo link containing:

```
submission/
├── agent-safety-skill/
│   ├── SKILL.md
│   └── README.md
├── agent-vault-skill/
│   ├── SKILL.md
│   └── README.md
├── vault/                  (snapshot of your vault structure)
│   ├── _index.md
│   ├── context/*.md
│   └── memories/session-log.md   (must contain at least 2 entries)
├── test-results/
│   ├── safety-skill-results.md
│   └── vault-skill-results.md
├── opencode.json           (showing both skills loaded)
└── reflection.md
```

**Due:** See course schedule.
