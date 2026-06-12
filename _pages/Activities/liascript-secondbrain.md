# The Second Brain: Obsidian, Gitless GitHub Sync, and Agent Access
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-secondbrain.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-secondbrain.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Second Brain: Obsidian, Gitless GitHub Sync, and Agent Access

Every AI tool you use maintains its own little memory of you, in its own format, in its own silo, and none of them agree. The cure is architectural: **one Markdown vault, hosted on GitHub, edited by you in Obsidian, and readable and writable by every agent you run**, so that your context becomes a single, versioned, portable artifact instead of five inconsistent copies. This tutorial builds that system from zero: the vault, the gitless sync, the personal access token, the agent contract, and the wiring to an agent like **hermes** from our stack. The arc: **why a vault $\rightarrow$ Obsidian and the repository $\rightarrow$ gitless sync with a PAT $\rightarrow$ the three-zone structure and AGENTS.md $\rightarrow$ the metadata protocol agents must honor $\rightarrow$ wiring hermes by prompting**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisites: a GitHub account and the shell module; the agent stack module helps for Part IV but the wiring also works with any agent CLI. Privacy note before we begin: this vault will contain personal context by design, so it lives in a **private** repository, and what you choose to put in it is itself a data-handling decision this course has prepared you to make deliberately. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Architecture

## 1. Context as a First-Class, Versioned Artifact

The design has four pieces, each replaceable, which is the point. **Obsidian** is a free note application that edits a folder of plain Markdown files (a *vault*) with wikilinks, graph view, and mobile apps; crucially, it imposes no proprietary format, so the vault is just files. **GitHub** hosts the vault as a private repository, providing versioning, an API surface agents can reach from anywhere, and a webhook surface for automation. **The GitHub Gitless Sync plugin** (a community Obsidian plugin) bridges the two *without git*: it translates every file operation into GitHub REST API calls, so there is no `.git` directory, no merge conflicts from stray command-line operations, and identical behavior on desktop and phone. **Your agents** complete the loop: they read the vault for context and, following a contract we will write, push changes that appear in Obsidian on the next sync. The deliberate absence of git tooling on your machine is a feature, not a shortcut: one sync mechanism, owned by one plugin, means one consistent state machine instead of three fighting ones.

## 2. Setup: Vault, Repository, Plugin, PAT

The full path from nothing, in order:

1. **Install Obsidian** (obsidian.md) and create a new vault in a normal folder, for example `~/obsidian-vault`.
2. **Create a private GitHub repository** (empty, no README) to back it, for example `yourusername/Obsidian-Vault`.
3. **Create the Personal Access Token.** On GitHub: Settings, Developer settings, Personal access tokens. Generate a token with **repo scope** (a classic token with `repo`, or a fine-grained token restricted to this one repository with Contents read and write permission, which is the tighter and better choice). Two operational rules: set an expiration you will actually remember, because **an expired token breaks sync silently** (Obsidian keeps working locally and you only notice when an agent's changes from two days ago never arrived); and treat the token like the credential it is, per every secret-handling rule this course has issued.
4. **Install the plugin.** In Obsidian: Settings, Community plugins, disable restricted mode, browse, search *GitHub Gitless Sync*, install, enable.
5. **Configure four values** in the plugin's settings: the token, the repository owner, the repository name, and the branch (typically `main`). Then trigger the first sync from the command palette; the plugin pushes your vault up (or pulls a pre-existing repository down) and thereafter syncs bidirectionally, manually or on a configurable interval.

One caution from the plugin's own documentation, worth repeating because the failure is ugly: **do not sync the vault's configuration folder to a public repository**, since the plugin's settings (including your token) live there; with a private repository and default settings you are fine, and the safest habit is simply never making this repository public.

---

## Model 1: Threat-Model the Token

### Critical Thinking Questions

1. Compare the classic `repo`-scope token against a fine-grained token limited to one repository's Contents permission. Enumerate what an attacker gains with each if it leaks, and state which our data-minimization principle selects.
2. The expired-token failure is *silent*: local editing continues and only cross-device or agent staleness reveals it. Design the cheapest detection habit (a calendar entry? a canary note an agent updates daily?) and justify it.
3. Your vault will hold personal context. List three categories of information you would deliberately keep *out* of even a private synced vault, and the principle behind each exclusion.

---

# Part II: Structure and the Agent Contract

## 3. The Three-Zone Vault

Structure is what turns a pile of notes into a system agents can be trusted inside. The layout, which Part III's metadata protocol and Part IV's wiring both assume:

```
vault/
├── AGENTS.md           # The agent contract: read completely before acting
├── LLMMEMORIES.md      # Persistent user context every AI session should know
├── SYSTEMPROMPT.md     # Standing behavioral and style instructions
├── raw/                # READ-ONLY inbox: PDFs, transcripts, exports; never modified
├── wiki/               # The curated, cross-linked knowledge base agents WRITE
│   └── index.md        # The hub page
└── .obsidian/
    └── github-sync-metadata.json   # Sync state: plugin-managed, agent-updated
```

The boundaries are the design. `raw/` is a one-way inbox: humans and automations drop source material there and *nobody* ever modifies it, so sources stay pristine and reprocessable. `wiki/` is where all authored knowledge lives, organized into topical subdirectories with wikilinks, and **agents are its primary authors**: their job is synthesis from `raw/` into `wiki/`, not transcription. The three root files are the only files that belong at the root: `LLMMEMORIES.md` is your externalized, version-controlled memory (who you are, what you are working on), `SYSTEMPROMPT.md` holds the standing instructions you would otherwise paste into every tool's custom-instructions box, and `AGENTS.md` is the contract, next.

## 4. AGENTS.md: The Self-Documenting Contract

`AGENTS.md` opens with a non-negotiable instruction (read this file completely before taking any action) and then specifies everything an agent needs: the zone boundaries (`raw/` strictly read-only; `.obsidian/` untouchable *except* the sync metadata file; any `.trash/` ignored entirely); the quick-start workflow (read the contract, inspect `wiki/`, inspect relevant `raw/` material, change only `wiki/`, update the metadata, commit atomically); the synthesis rules (summarize and deduplicate rather than mirror, preserve uncertainty and conflicts between sources rather than smoothing them, prefer enriching existing canonical pages over spawning duplicates); the organization rules (topical directories, hub pages, extensive wikilinks, no flat dumps); and the question-answering rule (answer from `wiki/` first, consulting `raw/` only to fill gaps, updating the wiki *before* answering when it is stale). The architectural elegance worth naming: because the contract travels *inside* the repository, every agent that can read files receives the full specification with zero per-tool configuration, which is your project context file pattern promoted to a whole knowledge system.

[[MC]]
An agent processing a new PDF in raw/ notices a typo in the PDF and also that wiki/index.md lacks a link to the page it just created. Under the AGENTS.md contract, the correct actions are:
- ( ) Fix the typo in the PDF and add the index link
- (x) Leave the PDF untouched (raw/ is read-only), add the index link, and note the source's typo in the wiki page if it matters
- ( ) Fix the typo and skip the index, since navigation is the human's job
- ( ) Move the PDF into wiki/ so it can be edited

---

# Part III: The Metadata Protocol (the Part Everyone Gets Wrong)

## 5. Why Agent Writes Need One Extra Step

Here is the subtle mechanic that makes bidirectional sync work, and the single most common failure when wiring agents to a gitless-synced vault. The plugin tracks every file's sync state in `.obsidian/github-sync-metadata.json`. When **you** edit in Obsidian, the plugin maintains this file itself. But when an **agent** creates or modifies vault files directly through the GitHub API, the plugin has no record of the change, and on the next sync it may simply not pull the agent's work. **The rule: any process that writes vault files outside Obsidian must update the metadata file in the same atomic commit.** Each entry follows this schema:

```json
{
  "path": "wiki/projects/cs357.md",
  "sha": null,
  "dirty": true,
  "justDownloaded": false,
  "lastModified": 1718100000000
}
```

The easy, correct path for agents: after creating or modifying a file, write its entry with `sha` set to **null** and `dirty` set to **true**, with `lastModified` as the current time in milliseconds; the plugin uploads on the next sync and fills in the real SHA itself. Deletions add `deleted: true` and a `deletedAt` timestamp. The two invariants that must never break: the file change and its metadata entry land in **one commit** (splitting them desynchronizes the state machine), and nothing else inside `.obsidian/` is ever touched.

For completeness, because a thorough agent may pre-compute it: the `sha` field, when not null, is a **git blob SHA**, not a plain SHA-1 of the file. Git hashes the byte string `blob {N}\0` (where `{N}` is the content's byte length and `\0` a literal null byte) concatenated with the raw content. Executable proof:

## Code Cell

```python
# The git blob SHA, demystified: this reproduces `git hash-object` exactly.
import hashlib, traceback

def git_blob_sha(content: str) -> str:
    try:
        raw = content.encode("utf-8")                # BYTES, not characters
        header = f"blob {len(raw)}\0".encode("utf-8")
        return hashlib.sha1(header + raw).hexdigest()
    except Exception as e:
        print(f"[secondbrain:git_blob_sha] {e}")
        traceback.print_exc()
        return ""

note = "# CS357\nAgentic AI, Fall 2026.\n"
print("blob sha:", git_blob_sha(note))
print("plain sha1 (WRONG for git):", hashlib.sha1(note.encode()).hexdigest())
# Multi-byte check: byte length vs character count matters
emoji_note = "café ☕\n"
print("bytes:", len(emoji_note.encode("utf-8")), "chars:", len(emoji_note))
```

---

## Model 2: Audit the Agent's Commit

An agent's commit contains: a new file `wiki/people/silverman.md`, an edit to `wiki/index.md`, and a metadata file updated with an entry for `silverman.md` only, whose `sha` field holds the plain SHA-1 of the file's text.

### Critical Thinking Questions

4. Find both protocol violations and predict the concrete symptom each produces on the next Obsidian sync (one file invisible; one file spuriously re-downloaded or treated as conflicting: match them).
5. Write the corrected metadata entries (both of them) using the safe null-and-dirty pattern.
6. Why does the contract make the *agent* responsible for this bookkeeping rather than asking the human to "just resync"? Connect to whose time the architecture is designed to spend.

---

# Part IV: Wiring an Agent (hermes) by Prompting

## 6. The Beautiful Part: The Wiring Is a Prompt

Because the contract lives in the repository, connecting an agent requires no plugin and no integration code; it requires *telling the agent where the contract is*. For hermes from our stack (or Claude Code, or any capable agent CLI), the entire ingestion wiring is:

```
Clone https://github.com/YOURUSERNAME/Obsidian-Vault using the token in the
GITHUB_TOKEN environment variable, read AGENTS.md completely, and follow it to
process any unprocessed documents in raw/. Commit and push your changes
atomically, including the sync metadata updates AGENTS.md specifies.
```

Provide the PAT as an environment variable when launching the container (never inline in the prompt, which lands in logs):

```bash
docker run --rm -it --name hermes \
  --add-host=host.docker.internal:host-gateway \
  -e GITHUB_TOKEN="$VAULT_PAT" \
  -v "$HOME/agents/hermes/home:/home/hermes/.hermes" \
  -v "$HOME/agents/workspace:/workspace" \
  nousresearch/hermes-agent:latest
```

For agents on the same machine, an even simpler read path exists: bind-mount the vault directory itself (`-v "$HOME/obsidian-vault:/vault:ro"` for context-consuming agents; read-write only for designated wiki authors). Standing instructions then go in each project's context file, the pattern from the agent CLI module:

```markdown
## Context
Before any task, fetch and read from the knowledge repository:
- AGENTS.md, LLMMEMORIES.md, SYSTEMPROMPT.md (repository root)
Treat them as authoritative for all decisions this session.
```

The session rhythm that results: you drop a PDF into `raw/` from your phone, sync; hermes runs (manually, or on an n8n schedule from the stack module), reads the contract, synthesizes wiki pages, updates the metadata, commits; you open Obsidian, sync, and the new cross-linked pages are simply *there*. The question-answering direction is one more prompt: *"Using the vault per AGENTS.md, what do my notes say about X? Update the wiki first if raw/ has newer material."* Obsidian, in this design, becomes the comfortable viewer onto a knowledge base your agents largely maintain, and the next module (the LLM Wiki) is devoted to what becomes possible once that loop is running.

## 7. Exercises

1. *Stand it up.* Complete the five-step setup with a private repository, sync from two devices (or two vault locations), and demonstrate a round trip. Submit your (token-redacted) plugin settings and the repository's commit list.
2. *Author the contract.* Write your own `AGENTS.md`, `LLMMEMORIES.md`, and `SYSTEMPROMPT.md` (a page each is plenty to start), adapting the structures from this module to your actual life and standards. The contract must state the zone boundaries and the metadata protocol explicitly.
3. *First agent write.* Drop one real document into `raw/`, run the ingestion prompt against hermes or your preferred agent CLI, and verify the result appears in Obsidian after a sync. Submit the agent's commit (showing the atomic file-plus-metadata change) and a screenshot of the synced wiki page.
4. *Protocol forensics.* Deliberately commit a vault change *without* the metadata update (from the GitHub web editor, say), observe and document the sync behavior, then repair it following the protocol. Three-sentence postmortem.
5. *The memory loop.* After a substantive session with any AI tool, write one refined fact about your context back into `LLMMEMORIES.md`, and confirm a fresh agent session (told to read the vault) reflects it. This bidirectional habit is the whole system's compounding interest; report whether the new session actually behaved differently.

---

## Reflection Prompt

In your notebook: this system makes your accumulated context durable, portable, and agent-readable, which is power; it also concentrates an intimate record of your work and mind into one token-protected repository, which is risk. Where did you personally draw the inclusion line in exercise 2, and what does your line reveal about which you currently fear more: forgetting, or being legible?

---

## 8. Further Reading

- W. Mongan, "A Private AI Knowledge Base: Obsidian, GitHub Sync, and Cross-Platform AI Context" (billmongan.com, May 2026): the full architecture this module teaches, including the complete AGENTS.md specification and SHA protocol.
- The GitHub Gitless Sync plugin repository and README: settings, conflict resolution, and the config-sync caution.
- GitHub Docs, "Managing your personal access tokens": fine-grained tokens and scoping.
