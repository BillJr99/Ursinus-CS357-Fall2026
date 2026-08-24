<!--
author:   Prof. Bill Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-obsidiansync.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-obsidiansync.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap

-->

# Syncing Obsidian to GitHub and Wiring AI Agents to Your Vault

Your Obsidian vault contains your best thinking: class notes, project plans, decisions you've made and why.  But right now it lives entirely on one machine, invisible to every agent you run.  The fix is architectural: **put the vault on GitHub, write a navigation contract agents can read, give agents a write-back path so knowledge accumulates across sessions, and wire the whole loop through the local tools you already use**.  This tutorial builds that system from zero: why GitHub is the right host $\rightarrow$ the Obsidian Git community plugin and its configuration $\rightarrow$ pointing agents at your vault as read context $\rightarrow$ letting agents write back to it as persistent memory.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Prerequisites: a GitHub account, Obsidian installed, and at least one agent CLI (OpenCode, pi.ai, or another tool from the agent CLIs module) running locally.  This is a supplemental tutorial; no commercial API keys are required.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Obsidian vault** | A folder of plain Markdown files that Obsidian treats as a unified knowledge base. Because the files are just text, every other tool (agents, scripts, editors) can read and write them without a special library. | Your vault might contain class notes, project decision logs, and a folder of `agent-context/` files that your local agents read before each session. |
| **Community plugin** | An Obsidian extension written by the community and installed through the in-app plugin browser. Community plugins are not audited by the Obsidian team, so you review them before enabling. | Obsidian Git is the most widely used community sync plugin; it wraps standard git operations in a background process that pushes on a configurable interval. |
| **Obsidian Git plugin** | A community plugin that runs git inside Obsidian, auto-committing and pushing your vault on a set interval without you ever touching the terminal. | Configured with a 5-minute auto-push interval, the plugin commits any changed notes and pushes them to your private GitHub repo while you keep writing. |
| **Personal Access Token (PAT)** | A secret string that authenticates GitHub API and git-over-HTTPS operations. It grants specific permissions without sharing your full account credentials. | The Obsidian Git plugin uses your PAT as the HTTPS password when pushing to GitHub; agents use the same or a separate token to pull the vault and push session memories. |
| **Vault index** | A single Markdown file (`_index.md` or `index.md`) that lists every note in the vault by topic with a one-sentence description, letting an agent navigate the vault without reading every file. | An agent given the path to `_index.md` can decide which three notes are relevant to your question and read only those, rather than loading the entire vault into its context. |
| **File-based context injection** | Passing relevant file contents directly in the context window before an agent starts work, as opposed to embedding+retrieval (RAG). | Concatenating `agent-context/*.md` files and prepending them to an OpenCode session prompt gives the agent your standing instructions and recent decisions without a vector database. |
| **Write-back / agent memory** | An agent appending what it learned during a session to a persistent file in your vault, so future sessions start with that knowledge already present. | At the end of a coding session, OpenCode appends a YAML-headed entry to `memories/session-log.md` noting the date, the project, and the key decisions made. |
| **Append-only memory** | A memory convention where agents always add a new dated section rather than overwriting existing content. | An agent writing to `memories/session-log.md` adds `## 2026-06-21` at the bottom and writes new content there; it never modifies the sections above that line. |

---

# Part I: Why Your Vault Needs to Be on GitHub

In this part, you will understand why a local Obsidian vault is invisible to agents and what it takes to make it accessible, and you will set up the Obsidian Git plugin with a private repository so that your notes are one sync away from any tool you run.

## Model 1: The Locality Problem and the Git Solution

Agents read files.  When you run OpenCode or pi.ai in a project directory, the agent can see every file in that directory tree.  But your Obsidian vault is somewhere else (probably `~/Documents/Obsidian/MyVault` or a similar location) and unless you explicitly point an agent at it, the agent has no idea it exists.  This is the **locality problem**: your knowledge lives in one place; your agents work in another.

There are two ways to bridge the gap.  The expensive way is a retrieval-augmented generation (RAG) pipeline: embed every note as a vector, run a similarity search on each query, and inject the top results.  RAG is powerful for large vaults but requires infrastructure.  The cheap, reliable alternative is **file-based context**: make the vault a git repository, push it to GitHub, and let agents clone or read it directly.  Every note is already plain Markdown.  No embedding pipeline required.  No vector database to maintain.  Agents that can read files can read your vault.

GitHub is the right host for three reasons:

1.  **Versioning**: every commit records what changed and when.  If an agent writes something wrong, you can revert it.
2.  **Portability**: a private repo is accessible from any machine with a PAT, including containers and remote agents.
3.  **Atomic writes**: git commits bundle a file change and its associated metadata into one unit, which matters when agents need to write without corrupting the state you'll pull back into Obsidian.

The Obsidian Git community plugin handles the sync automatically: it runs `git add`, `git commit`, and `git push` on a configurable interval in the background while you write.

| Setup Step | What You Do | What the Plugin Does Afterward |
|------------|-------------|-------------------------------|
| Create a private GitHub repo | `New repository` on github.com; set **Private**; do not initialize with a README (you'll push from your vault) | Nothing yet; the repo is empty |
| Generate a fine-grained PAT | GitHub Settings -> Developer Settings -> Fine-grained tokens -> New token; set expiration; grant **Contents: Read and Write** on only this repo | Stores the token; uses it as the HTTPS password for every push |
| Initialize git in your vault | `git init` in your vault directory; `git remote add origin https://github.com/YOURUSERNAME/obsidian-vault.git`; push the first commit | Nothing yet; the plugin reads the existing `.git` folder |
| Install the Obsidian Git plugin | Settings -> Community plugins -> Browse -> search "Obsidian Git" -> Install -> Enable | Reads `.obsidian/plugins/obsidian-git/data.json` for its own config |
| Configure the plugin | Set **Auto-pull interval** and **Auto-push interval** (5 minutes is a good starting point); set **Commit message template** (see below) | Runs on a timer: pulls on the pull interval, commits any changes and pushes on the push interval |

### Installing Community Plugins in Obsidian

Community plugins are disabled by default because they run arbitrary code.  To enable them: **Settings -> Community plugins -> Turn on community plugins -> Browse**.  After installing Obsidian Git, review its GitHub repository before trusting it with your vault and PAT; this is the same due-diligence habit as reviewing a Docker image before running it.

### The `.gitignore` for Obsidian Vaults

Not every file in your vault folder should go to GitHub.  The workspace state and plugin caches change constantly and create noisy commits with no informational value.  A minimal `.gitignore`:

```gitignore
# Obsidian workspace state; changes on every open/close, no information value
.obsidian/workspace.json
.obsidian/workspace-mobile.json

# Graph layout cache; large, regenerated automatically
.obsidian/graph.json

# Plugin-generated caches
.obsidian/plugins/obsidian-git/data.json.bak
.obsidian/.trash/

# OS noise
.DS_Store
Thumbs.db
```

Keep `.obsidian/plugins/` and `.obsidian/app.json` in version control so your plugin settings travel with the vault.

### Commit Message Template

The plugin's commit message template controls what appears in your GitHub history.  A useful template that records context automatically:

```
{% raw %}
vault: {{date}} {{time}} - {{numFiles}} file(s) changed
{% endraw %}
```

{% raw %}`{{date}}` and `{{time}}`{% endraw %} are built-in template variables the plugin replaces at commit time.  You will see entries like `vault: 2026-06-21 14:32 - 3 file(s) changed` in your history, which makes it easy to verify sync is working and to correlate agent commits with your own edits.

> **Common Misconception:** "Obsidian sync and Obsidian Git are the same thing."
>
> They are not.  **Obsidian Sync** is the paid cloud service run by the Obsidian team; it stores your vault on Obsidian's servers and syncs across devices automatically.  **Obsidian Git** is a free community plugin that uses git and any git host you choose.  They solve the same problem (cross-device sync) by entirely different mechanisms.  For this tutorial, we use Obsidian Git with a private GitHub repository because it gives you a versioned, agent-accessible copy of your vault under your own control; Obsidian Sync's servers are not accessible to agents you run locally.

### Security Note: What NOT to Put in a Synced Vault

A private GitHub repo is protected by your account credentials, but "private" does not mean invulnerable.  Token theft, account compromise, or an accidentally public setting expose everything in the repository.  Before you sync any note, ask: "Would I be comfortable if this appeared in a breach?"

Categories to exclude by policy:

- **Credentials and API keys**: never in plaintext, anywhere, ever.  Use a password manager.
- **Legal/medical/financial records**: subject to breach notification requirements even from private repos.
- **Information belonging to others**: private conversations, contact details, notes about third parties who did not consent.
- **Work product with an NDA**: your employer's confidential information does not belong in your personal vault.

A rule of thumb: the vault is for *your knowledge about the world*, not *secrets that unlock access to the world*.

### Critical Thinking Questions

1.  You generate a fine-grained PAT scoped to Contents read/write on your vault repo.  Your roommate generates a classic `repo`-scope PAT for the same task.  Compare what an attacker gains from each token if it leaks.  Which token does the principle of least privilege select, and why?

   > *Hint:* A fine-grained PAT scoped to one repo gives access to exactly one repository's file contents.  A classic `repo`-scope PAT gives read/write access to every repository in your account, including private ones you haven't mentioned.  Consider: if the token appeared in a public CI log, what is the blast radius of each?

2.  The plugin's auto-push interval defaults to 5 minutes.  A student changes it to 60 minutes to reduce API calls.  Describe a concrete scenario where the 60-minute interval causes a problem that the 5-minute interval would have caught in time.

   > *Hint:* Think about what happens if you make a change on one device (your laptop), then pick up your phone to continue working.  How stale is the phone's copy if the laptop hasn't pushed in 55 minutes?  Now add an agent that pulls the vault expecting the latest notes.

3.  Your `.gitignore` excludes `.obsidian/workspace.json` but a teammate's does not.  After both of you push from different machines, explain the specific kind of merge conflict that will result and why the file should never have been tracked.

   > *Hint:* `workspace.json` stores which panels are open and where they are positioned; it changes every time Obsidian opens or resizes a pane.  Two people (or two devices) will generate different versions of this file on every session.  What does git do when it sees two divergent edits to the same file?

---

With your vault synced to GitHub and your `.gitignore` keeping the commit history clean, you have the foundation for the next step: pointing agents at your notes so they can use your accumulated knowledge as context before they start work.

---

# Part II: The Vault as Agent Context (Read Path)

In this part, you will learn how agents read from files, build a vault index that lets an agent navigate without reading everything, and wire OpenCode and pi.ai to your vault so they start every session informed by your notes.

## Model 2: File-Based Context vs. RAG

There are two ways to get your vault contents into an agent's context window.  Understanding the tradeoff guides your design choice.

| Approach | How It Works | When to Use It | Limitation |
|----------|-------------|----------------|------------|
| **File-based injection** | Read specific Markdown files and prepend them to the prompt before the agent starts. | Small-to-medium vaults; notes whose topic is known in advance; standing instructions that apply every session. | You must know (or decide) which files to inject. If the vault has 500 notes, you cannot inject all of them; the context window has a limit. |
| **RAG (Retrieval-Augmented Generation)** | Embed every note as a vector; at query time, retrieve the top-k most similar notes and inject only those. | Large vaults (hundreds of notes) where you cannot predict which notes are relevant to any given query. | Requires a running embedding model and vector store (e.g., Chroma, Qdrant). More infrastructure, more failure modes. |

For the local agents in this course (OpenCode, pi.ai, Ollama-backed tools), file-based injection is almost always the right starting point.  It requires no infrastructure, it is transparent (you can see exactly what the agent sees), and it is fast.

### The Vault Index Pattern

A single file (`_index.md` at the root of your vault) lists every note by topic with a one-sentence description.  An agent given only this file can decide which two or three notes are relevant to the current task and read those, rather than loading the entire vault.

A well-structured `_index.md`:

```markdown
# Vault Index

## CS357: Foundations of AI
- [[CS357/lectures/agent-loops]]: Notes on the observe-plan-act cycle and how it maps to tool calls
- [[CS357/lectures/rag]]: Retrieval-augmented generation: chunking, embedding, retrieval, injection
- [[CS357/projects/rag-pipeline]]: My implementation plan for the RAG assignment; current status: chunking done, embedding WIP

## Personal Projects
- [[projects/homelab-docker]]: Docker Compose setup for my home server; last updated 2026-05-10
- [[projects/reading-tracker]]: Books I'm reading, notes on each chapter

## Agent Context Files
- [[agent-context/standing-instructions]]: Behavioral instructions every agent should read before starting work
- [[agent-context/project-state]]: Current state of active projects; updated after each session
- [[agent-context/key-decisions]]: Decisions I've made about tools and approaches, with rationale

## Memories (Agent Write Path)
- [[memories/session-log]]: Append-only log of agent session summaries (date, project, key decisions)
```

The double-bracket syntax (`[[path]]`) is Obsidian's wikilink format.  Agents that read the index as plain Markdown see it as a structured list of paths and descriptions, enough to navigate.

### The `agent-context/` Pattern

Create a folder called `agent-context/` in your vault.  Files here are short (one to two pages each) and focused:

```
agent-context/
|-- standing-instructions.md   # Behavioral rules for every agent
|-- project-state.md           # What I'm working on right now
`-- key-decisions.md           # Choices I've made + why
```

A Python helper that injects this folder into an agent session:

```python
# inject_vault_context.py
# Concatenates all agent-context/*.md files into a system prompt preamble.
# Usage: python inject_vault_context.py | opencode --system-prompt -
import os
import pathlib
import traceback

VAULT_PATH = pathlib.Path.home() / "Documents" / "Obsidian" / "MyVault"
CONTEXT_DIR = VAULT_PATH / "agent-context"

def load_context() -> str:
    try:
        parts = []
        for md_file in sorted(CONTEXT_DIR.glob("*.md")):
            parts.append(f"### {md_file.stem}\n")
            parts.append(md_file.read_text(encoding="utf-8"))
            parts.append("\n\n")
        return "".join(parts)
    except Exception as e:
        print(f"[inject_vault_context:load_context] {e}")
        traceback.print_exc()
        return ""

if __name__ == "__main__":
    print(load_context())
```

### Pointing OpenCode at Your Vault

OpenCode reads its system instructions from `AGENTS.md` in the current working directory.  To give OpenCode persistent access to your vault context, add a reference at the top of your project's `AGENTS.md`:

```markdown
# AGENTS.md

## Vault Context
Before starting any task, read the following files from the vault and treat them
as authoritative context for this session:

- ~/Documents/Obsidian/MyVault/agent-context/standing-instructions.md
- ~/Documents/Obsidian/MyVault/agent-context/project-state.md
- ~/Documents/Obsidian/MyVault/_index.md (use this to navigate to relevant notes)

Do not modify any file in the vault except under the memory write-back protocol
described in Part III of the vault's standing-instructions.md.
```

Because OpenCode reads and follows `AGENTS.md` at session start, this instruction is applied automatically every time you open a session in that project directory; no flags, no pasting.

### Pointing pi.ai at Your Vault

pi.ai reads a minimal `pi.md` context file if one is present in the working directory.  Add a knowledge directory reference:

```markdown
# pi.md

## Knowledge Base
Read the following files before starting work:
- ~/Documents/Obsidian/MyVault/agent-context/standing-instructions.md
- ~/Documents/Obsidian/MyVault/_index.md

These files describe standing behavioral rules and the structure of my personal
knowledge base. Use them to orient your work before asking clarifying questions.
```

For agents that do not support a project context file, use the Python helper above to pipe context directly:

```bash
python ~/scripts/inject_vault_context.py > /tmp/vault_context.txt
pi --context /tmp/vault_context.txt
```

You have 400 notes in your vault.  You want an agent to answer a question that may involve any of them.  Which approach is most appropriate?

[( )] Inject all 400 notes into the system prompt; agents can handle unlimited context
[( )] Only use agents that have been specifically trained on your vault's content
[(X)] Use a vault index so the agent can identify which subset of notes to read, then inject only those
[( )] RAG is the only correct answer for vaults larger than 50 notes; file injection cannot work

> **Common Misconception:** "The agent will figure out which notes are relevant if I just give it the vault directory path."
>
> An agent given a directory path can list the files in that directory, but listing 400 filenames tells it almost nothing about which two or three notes are relevant to your question.  The vault index solves this by providing a human-curated summary of each note's topic: the agent reads the index (one file, one context window), decides which notes to request, and reads only those.  Without the index, the agent must either read everything (often too much) or guess from filenames (unreliable).

### Critical Thinking Questions

4.  A teammate argues: "I'll just give the agent access to my entire vault directory and tell it to search for what it needs."  Explain two specific failure modes this causes (one related to context window size, one related to agent decision quality) that the vault index pattern prevents.

   > *Hint:* Context window limit: if the agent tries to read all 400 notes, it will hit the model's context window maximum and either fail or silently truncate the most recent notes.  Decision quality: an agent searching blindly through filenames like `note-2026-03-14.md` has no information about content; it can only guess, and it will guess wrong or read irrelevant files.  How does a structured index fix both of these?

5.  The `agent-context/` folder contains `key-decisions.md` with the entry: "Decided to use Chroma as the vector store because the team already knows Python."  Explain how this single sentence changes the agent's behavior on your *next* session compared to a session where the file doesn't exist.

   > *Hint:* Without the file, the agent must either ask which vector store to use (interrupting your flow) or guess (risking recommending a store that conflicts with your existing code).  With the file, the agent starts already knowing the decision and its rationale, and can make recommendations consistent with it.  What else might the agent do differently: for example, in which imports it writes or which documentation it looks up?

6.  You set up file-based injection for your vault, but your OpenCode sessions take 30 seconds longer to start than before.  Diagnose the likely cause and propose a fix that preserves the benefit of vault context without the latency.

   > *Hint:* If `agent-context/*.md` files have grown large (detailed session logs appended over months), the injection is passing a lot of text to the model on every session.  Which specific files matter most at the *start* of a session versus which ones the agent can look up on demand?  Consider splitting the always-inject files (standing instructions, project state) from the on-demand files (detailed notes, session log history).

---

With your vault connected as readable context, agents can now start each session knowing what you know.  The next step closes the loop: letting agents write back to the vault so that what they learn accumulates there permanently.

---

# Part III: The Vault as Agent Memory (Write Path)

In this part, you will learn why agent write-back matters, design a structured memory format agents can append to reliably, and handle the one real failure mode in a bidirectional system: the simultaneous write conflict.

## Model 3: Persistent Memory via Write-Back

An agent that reads your vault but never writes to it is a student who does your homework but never updates your notes.  Every insight the agent produces, every decision it makes with you, every refinement it surfaces: all of it disappears when the session ends.  The next session starts from the same place as the last one.  Over weeks, this is a significant waste.

Write-back solves this: at the end of a session, the agent appends a structured summary to `memories/session-log.md`.  Every future session reads that log as part of its context injection, so the accumulated record of past sessions is available as context from the start.

### The Memory Entry Format

Structure each memory entry with YAML frontmatter for machine-readable metadata and a narrative body for human and agent readability:

```markdown
## 2026-06-21

---
date: 2026-06-21
project: cs357-rag-pipeline
agent: opencode
key_decisions:
  - "Chose Chroma over Qdrant: team knows Python, Chroma has no external server"
  - "Chunking strategy: 512 tokens, 64-token overlap, paragraph boundaries preferred"
  - "Embedding model: nomic-embed-text via Ollama (already in our stack)"
---

Worked on the chunking module for the RAG pipeline assignment. The main design
question was chunking strategy. After testing three approaches (fixed-size,
paragraph-boundary, sentence-boundary), paragraph-boundary with 512/64 token
windows gave the best retrieval quality on the test set.

Also resolved the import conflict between the local Chroma client and the
containerized version; the fix is to always use `HttpClient` rather than
the ephemeral client, even for local instances, so the connection string is
configurable without code changes.

Next session should start with: reviewing the embedding step and connecting
it to the retrieval query path.
```

The YAML block lets a script extract structured data (dates, projects, decisions) without parsing prose.  The narrative body lets a future agent (or you) understand what happened in context.  Together they serve both audiences.

### The Append-Only Rule

Agents must **never rewrite or delete** existing entries in `session-log.md`.  They must always append a new dated section at the bottom.  Two reasons:

1.  **Correctness**: older entries recorded what was true at the time.  Rewriting them substitutes the agent's current understanding for the historical record, which may have been updated because a decision turned out to be wrong.  The history of wrong turns is often as valuable as the history of correct ones.
2.  **Conflict safety**: if the agent rewrites the file and Obsidian Git's auto-push runs simultaneously, git will see two different versions of the same file and create a merge conflict.  Appending to the bottom is almost always conflict-free because it touches only lines that did not exist in the previous commit.

### OpenCode Write-Back Skill

Add a memory write skill to your project's `AGENTS.md` that OpenCode invokes at session end:

```markdown
## Memory Write-Back Protocol

At the end of every session, before closing:

1. Create a new section in ~/Documents/Obsidian/MyVault/memories/session-log.md
   with today's date as the heading (## YYYY-MM-DD).
2. Write a YAML frontmatter block with: date, project name, agent (opencode),
   and a list of key_decisions (2-5 bullet points, each a complete sentence).
3. Write a narrative paragraph summarizing what was accomplished and why the
   key decisions were made.
4. End with a "Next session should start with:" sentence naming the next open
   task or question.
5. Append ONLY; do not modify any existing content above the new section.
6. After writing, run: cd ~/Documents/Obsidian/MyVault && git add memories/session-log.md && git commit -m "memory: session $(date +%Y-%m-%d)"
```

The git commit at step 6 means the memory is immediately in version control and will be pushed to GitHub on the next auto-push interval.  Obsidian will pull it on the next sync.

### Conflict Resolution: Simultaneous Writes

The one real failure mode in a bidirectional system is a **simultaneous write**: the auto-push timer fires while the agent is in the middle of writing to `session-log.md`, and two versions of the file reach GitHub at nearly the same time.

In practice, this almost never causes a problem because:

- The append-only rule means the agent touches only the bottom of the file.
- The Obsidian Git plugin commits the file as it existed when the timer fired.
- The agent's commit appends new content below what the plugin committed.

When a conflict does occur (visible as `<<<<<<< HEAD` markers in the file), the resolution strategy is always the same:

```bash
cd ~/Documents/Obsidian/MyVault
git pull origin main --no-rebase   # fetch the other side
# Open memories/session-log.md in any editor
# The conflict markers show: your version on top, remote version on bottom
# Resolution: keep BOTH sections; remove the markers, keep all content
git add memories/session-log.md
git commit -m "memory: merge conflict resolved (kept both sections)"
git push
```

This strategy is safe for append-only files because both conflicting versions added content; neither deleted or modified existing entries.  The merged result contains everything from both sides.

An agent finishes a session and wants to update `memories/session-log.md`.  Which action is correct under the append-only protocol?

[( )] Rewrite the entire file with a fresh, corrected summary of all past sessions
[( )] Delete the oldest entries to keep the file under 100 lines
[(X)] Add a new section with today's date at the bottom of the file, below all existing content
[( )] Create a new file (e.g., `session-log-2026-06-21.md`) for each session to avoid any possibility of conflict

> **Common Misconception:** "Creating a new file per session avoids all conflict issues, so it's safer than appending."
>
> Separate files avoid write conflicts but create a different problem: the vault index must be updated every time a new session file is created, or the agent won't know the file exists.  Worse, an agent reading context must now decide how many session files to read and which ones are most relevant.  The append-only log in a single file is searchable, readable top-to-bottom, and requires only one index entry.  A one-line git conflict in an append-only file is trivially resolved; a vault with 300 individual session files and a stale index is not.

### Critical Thinking Questions

7.  The YAML frontmatter in each memory entry includes `key_decisions` as a list.  Write a ten-line Python function that parses `session-log.md` and returns all `key_decisions` entries tagged with a given `project` name, as a flat list of strings.

   > *Hint:* Each entry is separated by `## YYYY-MM-DD`.  Within each entry, the YAML block is between the `---` delimiters.  You can use the `yaml` module to parse the frontmatter.  Walk through the file section by section: when you find a `## ` heading, start a new section; when you hit the second `---`, you've finished the frontmatter for that section.

8.  An agent rewrites `session-log.md` instead of appending.  You don't notice for three weeks.  Describe the specific data loss that occurred and explain why git history does not fully protect you from this mistake.

   > *Hint:* The data loss is the content that existed before the rewrite; the agent replaced it with its own summary.  Git history *does* contain the old content in previous commits, but recovering it requires: (a) knowing which commit was the last good one, (b) running `git show <commit>:memories/session-log.md` or a similar command, and (c) manually re-integrating the recovered content.  If you didn't notice for three weeks, there are also three weeks of *new* sessions that were appended to the wrong file.  What would the recovery actually look like?

9.  Design a canary check (a simple script or scheduled command) that detects within 24 hours if the vault's auto-push has silently stopped working (e.g., because the PAT expired).  Describe what the check does, how it is triggered, and what alert it produces.

   > *Hint:* One approach: a cron job that runs daily, clones (or pulls) the vault repo, checks the timestamp of the most recent commit, and prints a warning if it is more than 25 hours old.  Another approach: a "canary note" (`agent-context/sync-canary.md`) that the agent updates with today's date at the start of every session; if the canary date is stale by more than one day, sync has stopped.  Which approach is cheaper?  Which catches more failure modes?

---

With the read path and write path both working, you now have a full bidirectional loop: your vault informs agents, and agents update your vault.  The final part puts the four pieces together in structured exercises and asks you to design the folder structure that makes the whole system sustainable.

---

# Part IV: Synthesis and Practice

In this part, you will execute each component of the vault-agent system from scratch, verify that each piece works end-to-end, and design a folder structure that serves both personal knowledge and AI project memory simultaneously.

## Model 4: The Full Loop

When all four pieces are working, the session rhythm looks like this:

1.  You edit notes in Obsidian on any device.  The plugin pushes them to GitHub within 5 minutes.
2.  You start an OpenCode or pi.ai session.  The agent reads `agent-context/` and `_index.md` before any task.
3.  The agent works with you.  It navigates to relevant vault notes as needed using the index.
4.  At session end, the agent appends a structured memory entry to `memories/session-log.md` and commits it.
5.  You open Obsidian, sync once, and the session memory is visible as a note.
6.  The next session reads the updated log and starts more informed than the last.

Each session compounds.  Over a semester, the vault becomes a persistent, versioned record of every decision you made and why, readable by you, readable by any agent you run, and recoverable from any mistake via git history.

### Reference Folder Structure

A vault designed to serve both personal knowledge and AI project memory:

```
MyVault/
|-- _index.md                   # Navigation hub: all notes by topic, one sentence each
|-- AGENTS.md                   # Agent contract: read this before acting in the vault
|-- .gitignore                  # Exclude workspace state, caches
|
|-- agent-context/              # Always-inject context (read at session start)
|   |-- standing-instructions.md
|   |-- project-state.md
|   `-- key-decisions.md
|
|-- memories/                   # Agent write-back (append-only)
|   `-- session-log.md
|
|-- CS357/                      # Course notes (human-authored, agent-readable)
|   |-- lectures/
|   |-- projects/
|   `-- reflections/
|
|-- personal-projects/          # Project notes (agent-assisted authorship)
|   `-- rag-pipeline/
|
`-- raw/                        # Read-only inbox: PDFs, exports, transcripts
                                # Agents read from here; never write here
```

The `raw/` folder mirrors the zone boundary concept from the second brain module: it is a one-way inbox for source material that should stay pristine.  Agents synthesize from `raw/` into `CS357/` or `personal-projects/`; they never modify `raw/` itself.

---

## Exercises

1.  **Set up Gitless Sync on your Obsidian vault and confirm push to GitHub.**

   *What to do:* Complete the five-step setup from Model 1 (create private repo, generate fine-grained PAT, initialize git in vault, install Obsidian Git plugin, configure auto-push).  Create one new note titled `test-sync.md`, wait for the auto-push interval, and verify the note appears in your GitHub repository.  Submit a screenshot of the GitHub repository showing `test-sync.md` in the commit history, with your PAT redacted from any settings screenshots.

   *Starter hint:* If auto-push does not fire, check the plugin's status bar icon in Obsidian (bottom right); it shows sync status.  You can also trigger a manual push with the command palette (`Ctrl+P` or `Cmd+P`): search for "Obsidian Git: Commit and push all changes".

   *You've succeeded when:* The GitHub repository shows at least one commit from the Obsidian Git plugin (the commit message will follow your configured template), and `test-sync.md` appears in the file listing.

2.  **Write a `_index.md` for your vault and verify an agent can use it to navigate.**

   *What to do:* Create `_index.md` at the root of your vault following the structure in Model 2.  Include at least 8 entries across at least 3 topic sections.  Then start an OpenCode or pi.ai session, give the agent only the path to `_index.md` and a question whose answer is in one of your listed notes, and observe whether the agent navigates correctly to that note.  Submit: the `_index.md` file content and a two-sentence description of whether the agent used it successfully and what (if anything) it missed.

   *Starter hint:* Ask the agent something specific: "Based on my vault index at `~/Documents/Obsidian/MyVault/_index.md`, which note should I look at for information about [topic]?  Read that note and summarize its key point."  This forces the agent to use the index rather than guessing.

   *You've succeeded when:* The agent reads `_index.md`, identifies the correct note from it, reads that note, and produces a summary that accurately reflects the note's content, without reading any other vault files.

3.  **Write a session memory entry by hand, then script it so OpenCode does it automatically.**

   *What to do:* First, manually write one well-formed memory entry in `memories/session-log.md`, following the YAML frontmatter format from Model 3.  Commit and push it.  Then add the Memory Write-Back Protocol to your project's `AGENTS.md` and start an OpenCode session.  After completing any small task, verify that OpenCode appended a new entry at the bottom of `session-log.md` without modifying your hand-written entry.  Submit: the file content after the agent's write, with both entries visible.

   *Starter hint:* After adding the protocol to `AGENTS.md`, tell OpenCode explicitly at the end of the session: "We're done; please write the session memory entry now."  Review the result before committing.  Check that the YAML frontmatter is well-formed (valid YAML, no tab characters), and that the `## 2026-XX-XX` heading is at the bottom.

   *You've succeeded when:* `session-log.md` contains your hand-written entry unchanged at the top, and the agent's new entry below it, separated by the correct heading and frontmatter.

4.  **Design the folder structure for a vault that serves as both personal knowledge base and AI project memory simultaneously.**

   *What to do:* Design (on paper or in a Markdown file) the complete folder structure for a vault that you would actually use for the rest of this course and beyond.  The structure must support: (a) human-authored course notes that agents can read; (b) an agent context folder injected at session start; (c) an append-only session memory log; (d) a read-only inbox for source material (PDFs, transcripts); (e) at least one personal project area.  For each folder, write one sentence explaining its purpose and who (human, agent, or both) is expected to write to it.  Submit the annotated folder tree.

   *Starter hint:* Start from the reference structure in Model 4 and adapt it.  Ask yourself: where do my class notes actually live today?  Where should the agent's memories go so I can find them in Obsidian's graph view?  What is the one source of truth for "what am I working on right now"?  Your design should answer all three.

   *You've succeeded when:* Every folder in your design has a clear owner (human, agent, or both), the structure satisfies all five requirements, and you can explain in one sentence why the `raw/` folder must be read-only for agents.

---

## Reflection Prompt

**Personal level:** After completing Exercise 3, you have both a hand-written memory entry and an agent-written one in the same file.  Compare them: which one is more useful to you as a future reader?  Which is more useful to a future agent?  What does the difference reveal about who you are writing the vault for (yourself or your agents) and does the answer change depending on which section of the file you are looking at?

**Technical level:** The append-only memory log depends on two separate systems (Obsidian Git auto-push and the agent's manual commit) writing to the same file without stepping on each other.  Describe the full causal chain of a simultaneous-write conflict: what triggers it, what the conflicting commits contain, what git does when they arrive, and what the merge looks like.  Then explain why the append-only rule makes the resolution trivial in this case but would make it impossible if agents were allowed to rewrite earlier entries.

**Societal level:** This vault accumulates, over time, a detailed and searchable record of every decision you made, every question you asked an agent, and every insight the agent helped you reach.  This record is stored in a private GitHub repository, accessible to anyone with your PAT. Describe three distinct ways this accumulated personal record could cause harm (to you, to others, or to the integrity of the work itself) and identify one structural safeguard for each that goes beyond "keep the repo private."

---

## Key Concepts

| Term | Definition |
|------|------------|
| **Obsidian Git plugin** | A community plugin that runs git inside Obsidian, auto-committing and pushing on a configurable interval. |
| **Fine-grained PAT** | A GitHub Personal Access Token scoped to specific permissions on a single repository, following the principle of least privilege. |
| **Community plugin** | An Obsidian extension written by the community; requires deliberate opt-in because it runs arbitrary code. |
| **Vault index (`_index.md`)** | A curated file listing all vault notes by topic and description, enabling agents to navigate without reading everything. |
| **`agent-context/` folder** | A designated folder of short, always-injected files that establish standing instructions and current project state for every agent session. |
| **File-based context injection** | Prepending relevant Markdown file contents to an agent's context window before it starts work, the low-infrastructure alternative to RAG. |
| **Write-back / agent memory** | An agent appending a structured summary entry to a persistent vault file at session end, so future sessions inherit what past sessions learned. |
| **Append-only rule** | The convention that agents add new dated sections at the bottom of a memory file and never modify existing content above. |
| **YAML frontmatter** | Structured key-value metadata at the top of a Markdown file, delimited by `---`, parseable by scripts while remaining human-readable. |
| **Simultaneous-write conflict** | A git merge conflict caused by two processes committing different versions of the same file at nearly the same time; resolved by keeping both sections in an append-only file. |

---

## Further Reading

- Obsidian Git community plugin repository (github.com/Vinzent03/obsidian-git): full configuration reference, conflict handling documentation, and mobile sync notes.
- GitHub Docs, "Managing your personal access tokens": how to create and scope fine-grained tokens, and how to rotate them before expiration.
- W. Mongan, "A Private AI Knowledge Base: Obsidian, GitHub Sync, and Cross-Platform AI Context" (billmongan.com, May 2026): the full second-brain architecture this module is part of.
- OpenCode documentation (opencode.ai): `AGENTS.md` specification, session context injection, and skill definitions.
- "Building a Second Brain" (Tiago Forte, 2022): the personal knowledge management framework that motivates the zone structure and the distinction between capturing, organizing, and expressing knowledge.
- Git documentation, "git merge" and "resolving conflicts": the mechanics of merge conflict markers and resolution strategies.
