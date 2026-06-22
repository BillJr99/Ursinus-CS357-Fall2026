# Agent Skills and Plugins: Building, Configuring, and Publishing Custom Capabilities
<!--
author:   Prof. Bill Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-agentskills.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentskills.md

import: https://raw.githubusercontent.com/liaScript/coderunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap

-->

# Agent Skills and Plugins: Building, Configuring, and Publishing Custom Capabilities

Context files tell an agent about your project; **skills** tell an agent *how to think and act* in specific recurring situations. Where a context file (`AGENTS.md`, `opencode.json`) is always-on background knowledge, a skill is a named, composable instruction set that an agent can recognize and invoke on demand — a reusable behavior you author once and apply across projects. This tutorial teaches the anatomy of a skill, shows how to configure skills in OpenCode and pi.ai, walks through writing and publishing your own, and ends with exercises where your team authors skills that encode real workflow assumptions. The arc: **what skills are and why they differ from system prompts $\rightarrow$ configuring skills in OpenCode $\rightarrow$ writing and publishing your own skill $\rightarrow$ synthesis and peer comparison**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisites: the Agentic CLI Tools module (you will work with `opencode` and pi's CLI) and a working local Ollama installation. You do not need any cloud API access for this activity — everything runs on your local stack. After class, respond to the reflective prompt individually in your notebook.

---

## Key Terms

Before diving in, anchor the vocabulary. You will encounter all of these terms in today's work; return to this table whenever a term appears unfamiliar.

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Skill** | A named instruction set that an agent can invoke on demand, scoped to a specific purpose | A "code-review" skill that instructs the agent to always check for hardcoded secrets before approving a diff |
| **Plugin** | A packaged bundle of one or more skills (and optionally tools) distributed as an installable unit — often a Git repository | The Superpowers plugin (`git+https://github.com/obra/superpowers.git`) bundles several utility skills into one install |
| **System prompt** | An always-on, always-active instruction injected before every conversation turn | "You are a helpful coding assistant. Always explain your reasoning." — loaded automatically, not invokable by name |
| **`opencode.json`** | OpenCode's configuration file; lives at `$HOME/.config/opencode/opencode.json` (global) or `.opencode.json` in a project root (local) | The file where you add a `skills` array to register named instruction sets |
| **Skill manifest** | A `SKILL.md` or `skill.md` file at the root of a publishable skill repository; contains frontmatter metadata (name, description, author, version) and human-readable description | The file a tool reads to discover, list, and display a skill's purpose |
| **Tool (function call)** | A piece of code the agent can execute — a real function that runs in the host environment and returns structured data | `read_file("main.py")` runs in the shell and returns the file's contents; it is not an instruction template |
| **`when` trigger** | An optional field in an OpenCode skill entry that specifies a condition string; when the agent detects that condition in the conversation, it automatically surfaces the skill | `"when": "user asks to delete"` makes the safety-check skill appear whenever deletion is discussed |
| **Superpowers plugin** | A community skill bundle for agent CLIs installable via a single Git URL | `opencode skills install git+https://github.com/obra/superpowers.git` |

---

# Part I: What Skills and Plugins Are

In this part, you will learn what distinguishes a skill from the other forms of agent instruction you already know — system prompts, context files, and tool calls — and see the concrete anatomy of a skill entry so you can recognize and compare them across platforms.

## 1. The Spectrum of Agent Instruction

Think of the ways you can give a colleague standing guidance. You might write a team handbook that everyone always consults (system prompt). You might leave a note on a specific project folder (context file). You might hand someone a checklist to follow whenever they perform a code review (skill). Or you might give them a calculator they can press to get an answer (tool). These are not synonyms: each one carries a different scope, trigger, and encoding.

| Instruction Form | Scope | Always Active? | Invoked How? | Encoded As |
|-----------------|-------|----------------|--------------|------------|
| System prompt | Global — every conversation turn | Yes | Automatically | Text injected before the conversation |
| Context file (`AGENTS.md`, `opencode.json`) | Project — read at startup | Yes | Automatically at launch | Markdown or JSON file in project root or `$HOME/.config` |
| Skill | Named — surfaced on demand | No | By name or trigger | Named entry in config; optionally a `SKILL.md` file |
| Tool (function call) | Named — executes real code | No | By name, returns data | Code function registered with the agent runtime |

The critical distinction between a skill and a tool: a skill is an **instruction template** — it tells the agent *how to behave* in a situation. A tool is **executable code** — the agent calls it and gets back structured data. A skill says "when reviewing a diff, follow steps 1-4." A tool says "call `run_tests()` and here is the exit code." You can combine them: a safety skill instructs the agent to always call a `list_files` tool before deletion, then pause for confirmation. The instruction is the skill; the file-listing is the tool.

> **⚠️ Common Misconception:** Many students assume that adding a skill to `opencode.json` will make the agent *automatically* follow those instructions on every turn — like a system prompt. It will not. A skill is surfaced (made available) by its registration, but the agent invokes it by recognizing the situation or because you explicitly name it in your prompt ("use the code-review skill"). If you want always-on behavior, a context file or system prompt is the right instrument. If you want composable, named behavior you can invoke selectively, a skill is correct.

## 2. The OpenCode Skill Model

OpenCode stores its configuration in a JSON file with a top-level `skills` array. Each entry in that array is a skill definition. Here is the minimal shape of the file with two skill entries:

```json
{
  "model": "ollama/llama3.1",
  "skills": [
    {
      "name": "code-review",
      "description": "Review a diff or set of changed files using a structured checklist.",
      "instructions": "When the user asks you to review code or a diff:\n1. Read every changed file completely before commenting.\n2. Check for hardcoded secrets, API keys, or passwords.\n3. Check for missing error handling in I/O and network calls.\n4. Check that new public functions have docstrings.\n5. Summarize findings as: [BLOCKER], [WARNING], or [SUGGESTION] on separate lines.\n6. Do not approve a diff that contains a [BLOCKER] item."
    },
    {
      "name": "safety-check",
      "description": "Run a mandatory pre-action check before any destructive file operation.",
      "instructions": "Before deleting, overwriting, or moving any file:\n1. List every file that will be affected, with full paths.\n2. Print the message: 'SAFETY CHECK: the following files will be permanently modified or deleted.'\n3. Wait for explicit user confirmation ('yes' or 'proceed') before continuing.\n4. If the user does not confirm within the same turn, abort and explain what you did not do.",
      "when": "user asks to delete or remove or overwrite"
    }
  ]
}
```

The key fields: `name` is the identifier you use to invoke the skill by name in a prompt. `description` is what the agent displays when you ask it to list available skills. `instructions` is the multi-line string the agent treats as scoped guidance when the skill is active. `when` is an optional trigger string — if the agent detects that phrase pattern in the conversation, it will surface the skill automatically.

The file location matters: `$HOME/.config/opencode/opencode.json` applies globally to every project on your machine. A `.opencode.json` file in a project directory applies only when you run `opencode` from inside that project. Project-local skills override global skills of the same name, which lets you customize per-project without polluting your global config.

## 3. Installing a Community Plugin: Superpowers

The Superpowers plugin is a community-maintained bundle of utility skills packaged as a Git repository and installable with a single command. It demonstrates the distribution model: anyone can author a skill bundle, host it on GitHub, and let others install it without copying configuration manually.

```bash
# Install the Superpowers plugin into your OpenCode global config:
opencode skills install git+https://github.com/obra/superpowers.git

# Verify it appears in the skill list:
opencode skills list
```

After installation, the skills from the bundle appear in your `opencode.json` `skills` array automatically. You can inspect them — `opencode skills show <skill-name>` prints the full instruction body — and you can override any individual skill by adding an entry with the same name to your project-local `.opencode.json`.

## 4. The pi.ai Plugin Model

pi.ai uses a plugin system rather than a JSON config array, but the underlying idea is identical: a named instruction bundle is registered with the agent. A pi plugin is either a URL pointing to a manifest file or a local file path. The manifest describes the plugin's name, what it does, the instruction text it injects when active, and optionally a list of capability strings the agent can use to decide when to invoke it.

A minimal pi plugin manifest (`my-review-plugin.md`) looks like this:

```markdown
---
name: code-review
description: Review diffs using a structured checklist with severity levels.
version: 1.0.0
author: your-username
capabilities:
  - review
  - diff
---

## Instructions

When the user asks you to review code, a pull request, or a diff:

1. Read all changed files in full before writing any comment.
2. Flag hardcoded credentials as BLOCKER items.
3. Flag missing error handling as WARNING items.
4. Suggest documentation improvements as SUGGESTION items.
5. Never approve a change set containing a BLOCKER.
```

To add this plugin to a pi project, you point pi at the file or URL:

```bash
# From a GitHub URL (raw content):
pi plugin add https://raw.githubusercontent.com/your-username/my-skills/main/my-review-plugin.md

# From a local file during development:
pi plugin add ./my-review-plugin.md

# List loaded plugins to verify:
pi plugin list
```

Scoping works the same way as OpenCode: a plugin added from inside a project directory (where a `pi.md` project file is present) is scoped to that project. A plugin added from outside a project applies globally.

[[MC]]
A classmate says: "I added a safety-check skill to `opencode.json`, so now the agent will always ask for confirmation before deleting anything, just like a system prompt does." What is wrong with this claim?
- ( ) Nothing — skills and system prompts are functionally identical; both are injected before every turn
- (x) A skill is surfaced on demand or by a `when` trigger, not injected on every turn; without the `when` field or an explicit invocation, the agent will not use the skill automatically
- ( ) Skills in `opencode.json` override system prompts, so the system prompt would be suppressed
- ( ) The `opencode.json` file does not support a `skills` array; skills must be stored in `AGENTS.md`

---

With the taxonomy clear and both platforms understood, Part II builds on that foundation by configuring real skills in OpenCode — including a worked example and the Superpowers verification workflow.

---

# Part II: Configuring Skills in OpenCode

In this part, you will write a complete `opencode.json` skills configuration, trace through two realistic skill examples, install the Superpowers community plugin and verify it loads, and configure a pi.ai plugin scoped to a project. The goal is fluency with the configuration layer before you write your own skills from scratch.

## 5. The `opencode.json` Schema in Full

A production-ready `opencode.json` file pulls together model routing, global settings, and skills in one place. Here is a realistic example for a CS357 coursework machine:

```json
{
  "model": "ollama/llama3.1",
  "baseURL": "http://localhost:11434/v1",
  "theme": "dark",
  "skills": [
    {
      "name": "code-review",
      "description": "Structured diff review with severity classification.",
      "instructions": "When reviewing code or a diff:\n1. Read every changed file in full — do not skim.\n2. Classify each finding as one of:\n   - [BLOCKER] Correctness bug, security flaw, or data loss risk\n   - [WARNING]  Missing error handling, performance issue, or convention violation\n   - [SUGGESTION] Style, naming, or documentation improvement\n3. List findings grouped by file, then by severity.\n4. End with a one-sentence overall verdict: APPROVE, APPROVE WITH CHANGES, or REQUEST CHANGES.\n5. Do not approve any diff containing a [BLOCKER]."
    },
    {
      "name": "safety-check",
      "description": "Mandatory pre-action pause before any destructive operation.",
      "instructions": "Before executing any command or edit that deletes, overwrites, truncates, or moves a file:\n1. List every affected file with its full absolute path.\n2. Print: 'SAFETY CHECK — the following files will be permanently modified or deleted:'\n3. Wait for the user to type exactly 'yes' or 'proceed' before continuing.\n4. If the user types anything else, or does not respond in the same turn, abort all actions and print what you did NOT do and why.\n5. Never skip this check, even if the user previously said 'always approve deletes'.",
      "when": "user asks to delete or remove or overwrite or truncate or drop"
    },
    {
      "name": "obsidian-memory",
      "description": "After each session, append a dated summary to the Obsidian session log.",
      "instructions": "At the end of every work session, or when the user says 'wrap up' or 'end session':\n1. Collect the key decisions made, files created or modified, and commands run during this session.\n2. Format them as a Markdown section with a level-2 heading of today's ISO date (YYYY-MM-DD).\n3. Append that section to `vault/memories/session-log.md`, creating the file if it does not exist.\n4. Print: 'Session log updated at vault/memories/session-log.md'",
      "when": "user says wrap up or end session or close out"
    }
  ]
}
```

Every field is optional except `name` and `instructions` inside a skill entry. `description` is the human-readable summary shown by `opencode skills list`. `when` is the trigger phrase — the agent pattern-matches against it in the current conversation; if there is a match, the agent proactively surfaces the skill. Omitting `when` means the skill is available but never auto-surfaced; you invoke it by name in your prompt.

> **⚠️ Common Misconception:** A `when` trigger is not a filter that prevents the skill from being used at other times — it is a *hint* that auto-surfaces the skill when the pattern matches. You can still invoke a skill explicitly at any time by naming it in your prompt ("use the safety-check skill before running this command"), regardless of whether the trigger fired. Think of `when` as a notification, not a lock.

## 6. A Worked Example: The Code Review Skill

Trace through what happens when you invoke this skill. You are in an OpenCode session, and you type:

```
Please do a code review on my latest changes using the code-review skill.
```

The agent:
1. Looks up the `code-review` entry in the `skills` array.
2. Temporarily injects the `instructions` text as scoped guidance for this turn.
3. Reads every file you have staged or recently edited (it may call `git diff --staged` or ask which files to check).
4. Produces output structured exactly as the instructions specify: findings grouped by file, classified by severity, ending with a verdict.
5. Returns to normal behavior for the next turn — the skill's instructions are not persistent beyond the invocation.

The skill does three things that a plain chat prompt cannot reliably do: it establishes a **consistent output format** across all uses, it embeds **domain-specific constraints** (never approve a BLOCKER), and it is **reusable** without re-typing the checklist. These are the authoring principles that distinguish a good skill from a long prompt you paste by hand.

## 7. Verifying the Superpowers Plugin

After installing the Superpowers plugin, you should verify it loaded correctly before relying on it. A quick verification workflow:

```bash
# Step 1: list all registered skills; Superpowers entries should appear
opencode skills list

# Step 2: inspect one Superpowers skill in full to confirm the instruction body loaded
opencode skills show <superpowers-skill-name>

# Step 3: inside a session, invoke a Superpowers skill by name and confirm it behaves
# as its description says
opencode
# Inside the session:
# > Use the <superpowers-skill-name> skill to ...
```

If the skill does not appear in `list`, check that the install command succeeded without errors and that `$HOME/.config/opencode/opencode.json` was updated. The plugin installer appends to the `skills` array; you can open the file and confirm the new entries are present.

## 8. Configuring pi.ai: Scoping a Plugin to a Project

When you add a plugin inside a pi project directory (one that contains a `pi.md` file), the plugin is scoped to that project. Here is the full workflow:

```bash
# Step 1: create or navigate to a project directory
mkdir ~/cs357-pi-project && cd ~/cs357-pi-project

# Step 2: initialize pi in this directory (creates pi.md)
pi init

# Step 3: add a plugin from a GitHub raw URL, scoped to this project
pi plugin add https://raw.githubusercontent.com/your-username/my-skills/main/my-review-plugin.md

# Step 4: verify the plugin loaded and is listed as project-scoped
pi plugin list

# Step 5: inside a session, confirm the skill is available
pi
# > Review the diff in feature-branch.diff using the code-review plugin.
```

Global pi plugins (installed outside a project directory) apply to all pi sessions. Project-scoped plugins (installed from within a project directory that has a `pi.md`) only activate when pi is run from that directory or any subdirectory. This gives you a clean separation: project-specific coding conventions in local plugins, general-purpose utilities in global plugins.

[[MC]]
You want to use a "safety-check" skill in OpenCode that fires automatically whenever the user mentions deletion, but you also want to be able to invoke it explicitly at any time. Which configuration achieves both goals simultaneously?
- ( ) Add two entries to the `skills` array: one with `"when"` and one without, both named `"safety-check"`
- ( ) Set `"when"` to `"always"` so the skill fires on every turn and is also explicitly invokable
- (x) Add one entry with `"name": "safety-check"` and `"when": "user asks to delete or remove"` — the `when` field enables auto-surfacing while explicit invocation by name is always available regardless
- ( ) Move the skill instructions to the system prompt so they are always active, and keep a stub skill entry for the `list` command to show

> *Hint:* Re-read the "Common Misconception" box at the end of Section 5. The `when` field is a notification mechanism, not a gating mechanism. Consider what the entry needs vs. what the `when` field adds on top of it.

---

Now that you can configure skills on both platforms, Part III shows you how to write your own skill from scratch — including the manifest format for publishing it as a GitHub-installable plugin that partners in this class (or anyone) can install with a single command.

---

# Part III: Writing Your Own Skill

In this part, you will learn the authoring principles that make a skill reliable and maintainable, study two complete template skills you can adapt, and learn the repository layout for publishing your skill as a Git-installable plugin. The goal is that by the end of Part III, your team will have a skill ready to publish to a GitHub repository.

## 9. Skill Authoring Principles

A skill that is vague or open-ended will be applied inconsistently — the agent will interpret its instructions differently on each invocation, and you will not be able to predict or test its behavior. Three principles make skills reliable:

**One clear purpose.** A skill that tries to do "code review, plus security scanning, plus documentation generation" will do all three poorly. Split compound behaviors into separate skills. If you cannot name the skill's purpose in ten words or fewer, split it.

**Explicit constraints.** Do not write "be careful." Write "never proceed without listing all affected files first." Do not write "check for security issues." Write "check for hardcoded strings matching the regex `[A-Z]{2,}_KEY|password|secret|token`." Concrete constraints can be tested; abstract ones cannot.

**Concrete output format.** Specify exactly what the agent should produce: which headings, which labels, which order. A skill that produces consistently formatted output is automatable — you can pipe its output to another tool. A skill with free-form output is not.

> **⚠️ Common Misconception:** Students often write skills that say "follow best practices for X." This phrase is not a skill instruction — it is a deference to an undefined standard. The agent will infer "best practices" from its training data, which may not match your project's conventions at all. Replace "follow best practices" with the specific practices you want: the exact linting rule, the exact naming convention, the exact checklist item. A skill you authored and a skill that says "use best practices" will produce very different results on the same input.

## 10. The Skill Manifest Format

A publishable skill is a Git repository with a predictable layout. When someone runs `opencode skills install git+https://github.com/you/your-skills.git`, the tool looks for this structure:

```
your-skills/                    ← repository root
├── SKILL.md                    ← manifest: name, description, author, version
├── instructions/               ← one .md file per skill in this bundle
│   ├── safety-check.md
│   ├── code-review.md
│   └── obsidian-memory.md
└── package.json                ← optional: enables npm install as alternative
```

The `SKILL.md` manifest file with frontmatter:

```markdown
---
name: cs357-skills
description: A bundle of safety, review, and memory skills for CS357 coursework.
author: your-github-username
version: 1.0.0
skills:
  - safety-check
  - code-review
  - obsidian-memory
---

## CS357 Agent Skills

This bundle provides three skills designed for safe, consistent agent-assisted
development in CS357: Foundations of AI at Ursinus College.

- **safety-check**: Mandatory pre-action pause before destructive file operations.
- **code-review**: Structured diff review with severity classification.
- **obsidian-memory**: Appends a dated session summary to an Obsidian vault log.

Install with:
```bash
opencode skills install git+https://github.com/your-username/cs357-skills.git
```
```

Each file under `instructions/` contains only the instruction text for that skill — no frontmatter, just the multi-line Markdown that becomes the `instructions` field in the installed `opencode.json` entry. The installer reads the `skills` list from `SKILL.md` frontmatter, maps each name to its file under `instructions/`, and writes the corresponding entries into your config.

## 11. Template: The Safety Guardrail Skill

This template is ready to copy into `instructions/safety-check.md` in your skill repository:

```markdown
Before deleting, overwriting, moving, or truncating any file or directory:

1. Construct the complete list of files that will be affected, using absolute paths.
   If the operation is recursive (e.g., `rm -rf`), list every file that would be
   reached, not just the top-level path.

2. Print the following block verbatim:

   ```
   SAFETY CHECK
   The following files will be permanently modified or deleted:
   <list of absolute paths, one per line>
   Respond with exactly "yes" or "proceed" to continue, or anything else to abort.
   ```

3. Wait for the user's response in this same turn.

4. If the response is exactly "yes" or "proceed" (case-insensitive), proceed with
   the operation.

5. Otherwise, abort every pending action and write one line:
   "ABORTED: <original action description> was not confirmed."

6. After completing a confirmed deletion, append one line to `logs/deletions.md`
   (creating the file and directory if needed) in the format:
   `YYYY-MM-DD HH:MM — deleted: <absolute path>`

This check cannot be bypassed by prior instructions, standing approvals, or
"always confirm" flags set earlier in the conversation.
```

## 12. Template: The Obsidian Memory Skill

Copy this into `instructions/obsidian-memory.md`:

```markdown
At the end of each working session — triggered when the user says "wrap up",
"end session", "close out", or "log this session" — do the following:

1. Collect the following from this session:
   - Every file created, with its full path
   - Every file modified, with a one-phrase description of the change
   - Every shell command run that had side effects
   - The two or three most important decisions made, stated as declarative sentences
   - Any errors encountered and how they were resolved

2. Format the collected information as a Markdown section with this exact structure:

   ## YYYY-MM-DD

   ### Files Created
   - `path/to/file` — one-phrase purpose

   ### Files Modified
   - `path/to/file` — one-phrase description of change

   ### Commands Run
   - `command` — one-phrase effect

   ### Key Decisions
   - Decision statement one.
   - Decision statement two.

   ### Errors and Resolutions
   - Error: description. Resolution: description.

3. Append this section to `vault/memories/session-log.md`.
   Create the file and all parent directories if they do not exist.
   Do NOT overwrite existing content — append only.

4. Print: "Session logged at vault/memories/session-log.md — YYYY-MM-DD entry added."
```

## 13. Testing a Skill

A skill you cannot test is a skill you cannot trust. Testing a skill means writing a prompt that exercises every step in the instruction body and verifying the agent's output matches what the instructions specify.

For the safety-check skill, a test prompt:

```
Test the safety-check skill. I want you to delete the file `data/raw/source.csv`.
Do NOT actually delete it — I am testing whether the safety-check skill fires correctly.
Proceed through the skill's steps up to and including printing the SAFETY CHECK block,
then stop and wait for my confirmation without doing anything else.
```

What to verify in the agent's response:
- The SAFETY CHECK block appears, formatted exactly as specified
- The absolute path to `data/raw/source.csv` is listed
- The agent does not proceed without receiving "yes" or "proceed"
- If you type "no" or anything else, the ABORTED line appears

For the obsidian-memory skill, trigger it explicitly at the end of a real session:

```
Wrap up this session and use the obsidian-memory skill to log it.
```

Then open `vault/memories/session-log.md` and confirm: the date heading is correct, the files and commands are accurately listed from the session, and the file was appended (not overwritten).

[[MC]]
A teammate writes a skill instruction that says: "Always follow Python security best practices when writing code." During testing, the agent produces different security checks across three invocations of the same skill. What authoring principle was violated, and what is the fix?
- ( ) One clear purpose — the skill should be split into separate skills for each security check
- ( ) Concrete output format — the skill should specify which headings to use in its security report
- (x) Explicit constraints — "best practices" is undefined; the fix is to list the specific checks by name (e.g., "check for use of `eval()`, `exec()`, or `pickle.loads()` with untrusted input")
- ( ) Skills cannot encode security guidance; move this to the system prompt

> *Hint:* Ask yourself: could two reasonable developers disagree about what "Python security best practices" means? If yes, the instruction is underspecified — the agent will fill in the gap from its training data, not from your intent.

---

Part IV brings everything together through exercises that require you to write, publish, and compare real skills with a classmate — surfacing the workflow assumptions each of you embedded in your choices.

---

# Part IV: Synthesis and Practice

In this part, you will write skills for two real scenarios (safety guardrails and session memory), publish a skill to GitHub, and install a partner's skill — then compare notes on the assumptions each of you encoded. The comparison exercise is not a grading exercise: there is no single correct skill. It is a professional practice: making implicit assumptions explicit and negotiating them with collaborators.

## 14. Exercise 1: Safety Skill for Branch Protection

Write a safety skill for OpenCode that prevents committing to `main` without confirmation. This skill should fire whenever `git commit` or `git push` is mentioned and the current or target branch appears to be `main` or `master`.

Add this entry to your `$HOME/.config/opencode/opencode.json`:

```json
{
  "name": "branch-protection",
  "description": "Prevent direct commits to main or master without explicit confirmation.",
  "instructions": "Before executing any `git commit`, `git push`, or `git merge` command:\n1. Run `git branch --show-current` to determine the current branch.\n2. If the current branch is `main` or `master`, OR if the push target includes `main` or `master`:\n   a. Print: 'BRANCH PROTECTION: You are about to commit or push directly to <branch-name>.'\n   b. Print: 'This action cannot be undone without force-pushing or reverting. Confirm with \"yes\" to proceed.'\n   c. Wait for explicit confirmation before proceeding.\n3. If the current branch is anything other than `main` or `master`, proceed without interruption.",
  "when": "user asks to commit or push or merge"
}
```

**Test your skill:** Open an OpenCode session in a Git repository. Check out `main` or `master`. Ask the agent to "commit my changes with the message 'test commit'." Verify the BRANCH PROTECTION block appears. Then check out a feature branch and repeat — verify the block does *not* appear.

**Record your observations:**

1. Did the `when` trigger fire at the right moment? Did it fire when it should not have?

   > *Hint:* Try asking the agent to "review my changes" (no commit intent) and see whether the skill fires. If it does, your `when` phrase is too broad. Try "commit or push or merge to" as a more specific trigger.

2. The skill runs `git branch --show-current` to detect the branch. What happens if the agent's working directory is not a Git repository? Revise the skill to handle this case gracefully.

   > *Hint:* `git branch --show-current` exits with a non-zero status and prints an error if it is not inside a Git repository. Add an instruction step: "If `git branch --show-current` fails or returns empty output, skip the branch check and proceed normally."

3. This skill protects against accidental commits but cannot prevent deliberate ones — a user can always type "yes." What governance mechanism beyond a skill would you combine with it to enforce the protection technically (not just procedurally)?

## 15. Exercise 2: Obsidian Memory Skill

Using the template from Section 12, write an Obsidian memory skill for your own workflow. Your version must differ from the template in at least two ways — adapt it to what you actually want to log in your own development sessions.

**Add it to your project-local `.opencode.json`** (so it only fires in projects where you want session logging, not globally):

```bash
# Create a project directory for this exercise:
mkdir ~/cs357-memory-project && cd ~/cs357-memory-project

# Create or edit .opencode.json:
# Add your obsidian-memory skill with your two customizations
```

**Run a real session:** Do three to five minutes of actual work in the project (create a file, edit it, run a command), then trigger the memory skill with "wrap up this session."

**Record your observations:**

1. What two adaptations did you make to the template, and why? What assumption about your workflow did each one encode?

2. Open the generated `vault/memories/session-log.md` file. Is the entry accurate? Did the agent include anything it should have omitted, or omit anything it should have included?

3. If you ran the skill again immediately in the same session, would it create a duplicate entry? How would you revise the instructions to prevent duplicates?

   > *Hint:* Before appending, the skill could check whether a section with today's date already exists in the file. Add an instruction step: "Before appending, search `vault/memories/session-log.md` for a section heading matching today's ISO date. If one exists, append to that section rather than creating a new one."

## 16. Exercise 3: Publish and Install

**Part A — Publish your skill:**

1. Create a public GitHub repository named `cs357-skills` under your GitHub account.
2. Add the repository layout from Section 10: `SKILL.md` with frontmatter, `instructions/` directory, at least two skill files.
3. Include both the safety-check skill (your Exercise 1 version) and the obsidian-memory skill (your Exercise 2 version).
4. Push the repository to GitHub.

```bash
mkdir cs357-skills && cd cs357-skills
git init
# Create SKILL.md, instructions/safety-check.md, instructions/obsidian-memory.md
git add .
git commit -m "Initial skill bundle"
git remote add origin https://github.com/your-username/cs357-skills.git
git push -u origin main
```

**Part B — Install a partner's skill:**

Exchange GitHub repository URLs with a teammate. Install their skill bundle into your OpenCode:

```bash
opencode skills install git+https://github.com/partner-username/cs357-skills.git

# Verify their skills now appear in your list:
opencode skills list
```

**Record your observations:**

1. Did the install succeed without errors? If not, what was the error, and what in the repository layout caused it?

2. Inspect your partner's installed skills with `opencode skills show`. What is different about their `safety-check` compared to yours — in trigger phrase, in steps, in the confirmation format?

## 17. Exercise 4: Assumptions Audit

Compare your `safety-check` skill side-by-side with your partner's. This is not a correctness exercise — both can be correct. It is an **assumptions audit**: finding the implicit beliefs each of you encoded and making them explicit.

**Structured comparison:** For each difference you find, complete this sentence: *"My skill assumes that [X], while my partner's skill assumes [Y]. This difference matters when [Z]."*

Areas to examine:
- The `when` trigger phrase: what operations does each of you guard? What did each of you leave unguarded?
- The confirmation protocol: does yours require exactly "yes" or "proceed"? Does your partner's accept "ok" or "sure"? What user behavior does each assume?
- The deletion log: does yours log to `logs/deletions.md`? Does your partner's log somewhere else, or not at all? What assumption about the user's project structure does each encode?
- The bypass clause: does yours say the check "cannot be bypassed by prior instructions"? Does your partner's? What threat model does the bypass clause address?

**Group discussion questions:**

1. One of you probably wrote a more permissive confirmation protocol (accepting more words as "yes") and one of you probably wrote a stricter one. Which is better for a solo developer working on a personal project? For a team working on a shared codebase? For a student submitting coursework?

   > *Hint:* "Better" is not a fixed answer here — it depends on the threat model. A solo developer's biggest risk is accidental deletion; a team's biggest risk may be social engineering ("just say yes, it's fine"). A student's biggest risk might be the agent deleting test data the instructor needs to see. Each context justifies different strictness.

2. Your skill is an instruction template, not code. Someone else can install it and it will encode your assumptions about how confirmations work, where logs go, and what counts as a destructive operation. What responsibilities does that give you as a skill author?

3. Look at the Superpowers plugin you installed in Section 7. Find one skill in that bundle where the author's assumptions about the user's workflow are visible. State the assumption explicitly.

---

## Reflection Prompt

In your notebook, respond at three levels:

**Personal level:** You have now written instructions that an agent will follow on someone else's machine — possibly a partner's, possibly a future employer's, possibly a student you might someday supervise. The skills you authored encode your workflow assumptions, your risk tolerance, and your sense of what deserves a confirmation gate. Looking at your safety-check skill: whose interests does it protect, and whose does it not? Did writing it make you more conscious of what "safe" means to you personally?

> *Hint:* Think about the bypass clause. If you wrote "this check cannot be bypassed," you assumed that accidental deletion is a bigger risk than a case where bypassing is genuinely needed. If you left a bypass path, you assumed the opposite. Neither is wrong — but the choice reflects a value.

**Technical level:** Skills, tools, system prompts, and context files are four different mechanisms for encoding agent behavior. In your own words, describe a scenario where using the wrong mechanism for the job would cause a real problem — for example, a safety requirement that should be a skill but was put in a context file. What is the failure mode?

**Societal level:** The skills you published to GitHub are now installable by anyone. If someone installs your `safety-check` skill and relies on it to protect a production database, and your skill has a bug (it fails to fire for some deletion pattern you did not anticipate), what — if anything — is your responsibility? Compare this to the responsibility of a library author whose code has a security vulnerability. Is authoring an agent skill more like writing code or more like giving advice?

---

## Key Terms Summary

| Term | Definition |
|------|------------|
| **Skill** | A named, composable instruction set an agent can invoke on demand, scoped to a specific purpose |
| **Plugin** | A packaged bundle of one or more skills distributed as an installable unit (usually a Git repository) |
| **System prompt** | Always-on instructions injected before every conversation turn |
| **`opencode.json`** | OpenCode's configuration file; contains the `skills` array and model routing settings |
| **Skill manifest** | `SKILL.md` frontmatter file at the root of a publishable skill repository |
| **Tool (function call)** | Executable code the agent calls at runtime; returns structured data |
| **`when` trigger** | Optional field that auto-surfaces a skill when the agent detects a matching phrase pattern |
| **Superpowers plugin** | A community skill bundle installable via `opencode skills install git+https://github.com/obra/superpowers.git` |
| **Assumptions audit** | A structured comparison of two artifacts to surface the implicit beliefs each author encoded |

---

## Community Skills Worth Knowing

Two open-source skills from the community are worth studying as design examples — both for what they do and for the engineering principles they embody. Both are MIT licensed and installable with a single `opencode skills install` command.

### grill-me (mattpocock/skills, MIT)

**What it does:** Before you commit to a plan, architecture, or implementation approach, `grill-me` subjects your proposal to exhaustive critical questioning. It walks a decision tree — probing hidden assumptions, unstated alternatives, and unresolved dependencies — until every branch is explicit. It is particularly useful before writing code, because it forces you to articulate *why* you chose one design over its alternatives.

**Why it is a good skill example:** It has a single, narrow purpose (pre-commitment scrutiny), a concrete trigger (when you describe a plan), and a well-defined output (structured questions, one branch at a time). It does not try to also write code, generate documentation, or do anything else.

**Install and try:**
```bash
opencode skills install git+https://github.com/mattpocock/skills.git
# Then inside a session:
# > I'm planning to use a single SQLite database for all user data in our RAG pipeline. Grill me on this.
```

Source: https://github.com/mattpocock/skills — MIT License.

---

### caveman (JuliusBrussee/caveman, MIT)

**What it does:** `caveman` compresses the agent's output by 65–75% by forcing terse, article-free responses ("No articles. Short. Cave-style."). It drops filler words and pleasantries while preserving all technical terms, code, and precision. Three intensity levels (lite, full, ultra) let you tune verbosity to your task — `full` for interactive sessions where you want fast scanning; `lite` for when you still want some prose; `ultra` for token-budget-constrained pipelines. It automatically reverts to normal communication for security warnings and irreversible actions.

**Why it is a good skill example:** It demonstrates scoped behavior with explicit safety overrides — the instruction to revert to normal prose for warnings is a concrete constraint that prevents the compression from obscuring critical information. It also shows how to implement multiple intensity modes within a single skill by name-parameterizing invocations.

**Install and try:**
```bash
opencode skills install git+https://github.com/JuliusBrussee/caveman.git
# Then inside a session:
# > /caveman full   (or invoke: "use caveman full mode")
# > Explain how KV caching works.
```

Source: https://github.com/JuliusBrussee/caveman — MIT License.

---

**Design comparison exercise:** After studying both skills, answer: (a) What is each skill's single clear purpose? (b) What explicit constraint prevents each skill from misbehaving in a dangerous situation? (c) How does each skill's `when` trigger (or invocation pattern) differ from a system prompt? Compare your answers with a partner's before the next class.

---

## Further Reading

- OpenCode documentation (opencode.ai/docs): the full `opencode.json` schema, skill configuration reference, and plugin install commands.
- pi.ai documentation (pi.dev/docs): the plugin manifest format, `pi plugin` subcommands, and scoping rules.
- The Superpowers plugin repository (github.com/obra/superpowers): a real-world example of a well-structured skill bundle with `SKILL.md` frontmatter and an `instructions/` directory layout.
- grill-me (github.com/mattpocock/skills, MIT): pre-commitment decision-tree interrogation skill — study the SKILL.md manifest format and how a single-purpose instruction is structured.
- caveman (github.com/JuliusBrussee/caveman, MIT): output-compression skill with intensity levels and safety overrides — a good example of scoped constraint and parameterized invocation.
- W. Mongan, "Agentic CLI Tools" (this course, prior module): the context file and permission gate foundations that skills build on.
- "Prompt Engineering for Agents" — the course reading on specifying behavior precisely enough to test; the same precision discipline applies to skill authoring.
- The Model Context Protocol site (modelcontextprotocol.io): if you want your skill to call an external tool (a real function, not an instruction template), MCP is the standard the underlying agent runtime uses.
