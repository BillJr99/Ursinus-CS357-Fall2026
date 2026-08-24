---
layout: default-standard
permalink: /Tutorials/AgentCLIs
title: 'CS357: Foundations of Artificial Intelligence - Agentic CLI Tools'
info:
  coursenum: CS357
  purpose: "To install and compare the major terminal coding agents (Claude Code, Codex, Gemini CLI, opencode, and pi) and to teach the review discipline their generated diffs demand."
tags:
- coding-agents
- cli
- tooling
---

# CS357: Foundations of Artificial Intelligence - Agentic CLI Tools

## Purpose

To install and compare the major terminal coding agents (Claude Code, Codex, Gemini CLI, opencode, and pi) and to teach the review discipline their generated diffs demand.

## About This Tutorial

The agent loop you study in this course ships today as a family of **terminal programs**: you describe a goal, the agent reads your files, proposes shell commands and edits, asks permission at the gates, and iterates.  This tutorial installs the major tools from zero, teaches the shared workflow they all follow, and shows how to drive them from inside VS Code.  We take today in this order: **the shared anatomy $\rightarrow$ installing the big five $\rightarrow$ project context files $\rightarrow$ permission gates and supervision $\rightarrow$ routing them through our local gateway $\rightarrow$ VS Code integration**.

## Key Concepts

Make sure these terms are solid before you start.  You will meet all of them below, and the table is here to look back at to return to.

| Term | Plain-English Definition | Where You'll Meet It |
|------|--------------------------|--------------------------|
| **Agent loop** | The repeating cycle an AI agent runs: observe the environment, plan the next step, use a tool, observe the result, repeat until done | When you ask Claude Code to write a weather script, it reads your directory, drafts the file, proposes a shell command to test it, and waits for your approval, then loops again |
| **REPL** | Read-Eval-Print Loop: an interactive session where you type something, the program responds, and you keep going, like a conversation | The `claude` command drops you into a REPL; you type goals, it replies with plans and proposed changes |
| **Permission gate** | A pause point where the tool stops and asks you to approve or refuse a proposed action before it runs | Before running `pip install requests`, Claude Code will display the command and ask "allow?" |
| **Context file** | A project-specific text file (e.g., `CLAUDE.md`) the agent reads automatically at startup, containing standing instructions about the project | You write "never modify files under `data/raw/`" in `CLAUDE.md` and the agent respects that boundary every session without you repeating it |
| **MCP (Model Context Protocol)** | An open standard that lets agents connect to external tools (databases, APIs, browsers) in a uniform way | Both Claude Code and Gemini CLI can call the same MCP server to query your database; you only write the server once |
| **Gateway / base URL** | A local proxy server that sits between your CLI tool and any AI model, letting you swap models without changing the tool | Setting `ANTHROPIC_BASE_URL=http://localhost:4000` makes Claude Code talk to your local Ollama instance instead of Anthropic's cloud |

---

## The Three Paradigms: Chat, Code, and Cowork

Before you install a single tool, it helps to know *which kind* of tool you are installing.  The AI-assistant landscape has settled into three paradigms, and the difference between them is not the model; it is **who runs the actions and where those actions land**.  A useful analogy: a **chat** assistant is a knowledgeable colleague on the phone (they tell you what to do, you do it); a **code** agent is a contractor you handed the keys to *one room* (they do the work, you approve each consequential step); a **cowork** agent is a personal assistant loose in your *whole office* (they open apps, edit documents, and run errands across your desktop).

| Paradigm | What you do | Who runs the actions | Primarily for | Autonomy | Example tools |
|----------|-------------|----------------------|---------------|----------|---------------|
| **Chat** | Converse in a window; copy answers and code out yourself | **You** are the runtime; you paste and run the code by hand | Anyone; ideation, explanation, quick snippets | None (no file or shell access) | ChatGPT, Claude.ai, **LM Studio** (chat mode), Ollama chat |
| **Code** | Give a goal in your terminal or IDE; the agent reads files, edits them, runs commands and tests, and loops | **The agent** acts on your repository, behind permission gates | Developers working inside a codebase | Medium-high, but gated | **Claude Code**, **opencode**, Codex CLI, Gemini CLI, pi, and, at scale, managed by **herdr** |
| **Cowork** | Delegate general computer and document tasks on a desktop | The agent drives apps, files, and the desktop directly | **Non-developers** and knowledge work beyond code | High, task-scoped | **Claude Cowork**, **OpenWork** (open-source, opencode-powered) |

The whole of this tutorial lives in the **code** column: an agent scoped to a project directory, acting through gates.  But the paradigms are worth holding in your head together for two reasons.  First, they mark a ladder of blast radius: chat can only mislead you, code can change your repository, and cowork can touch anything on your machine, so the human-oversight lessons in Parts II and III matter *more* as you climb, not less.  Second, the boundaries are blurring.  **LM Studio Bionic** is a case in point: it began as a chat app for open, local models and grew a code-project mode (point it at a folder and it investigates, edits, and debugs) plus local voice input; one tool spanning chat and code, run entirely on models you host yourself.

A teammate says, "Chat, code, and cowork are just three brand names for the same thing, a model answering prompts."  The most accurate correction is:

- They differ only in price; the underlying capability and risk are identical
- They differ in *who executes the actions and how large the blast radius is*: in chat you run everything by hand, in code a gated agent changes your repo, and in cowork the agent acts across your whole desktop
- They differ only in which company trained the model behind them
- They are ordered by intelligence: cowork models are strictly smarter than code models, which are smarter than chat models

<details markdown="1"><summary>Answer</summary>

They differ in *who executes the actions and how large the blast radius is*: in chat you run everything by hand, in code a gated agent changes your repo, and in cowork the agent acts across your whole desktop

</details>

---

# Part I: One Anatomy, Many Tools

In this part, you will learn the shared anatomy of agentic CLI tools and install your first tool end-to-end, so that the differences between tools become variations on a pattern you already understand, rather than five separate things to memorize.

## 1.  What Every Agentic CLI Shares

Think of these tools the way you think about web browsers: Chrome, Firefox, and Safari look and feel different, but under the hood they all speak HTTP, render HTML, and run JavaScript.  Agentic CLIs are the same story: different names, different makers, different default personalities, but every one of them is running the same agent loop you studied in week one.  The shared parts are: a **REPL-style chat** in your project directory; **file tools** (read, edit, create) scoped to that directory; a **shell tool** that proposes commands; **permission gates** before consequential actions; a **project context file** read automatically at startup; and a growing convergence on **MCP** (Model Context Protocol, an open standard for connecting agents to external tools like databases and browsers) for external tools.  Once you can drive one, you can drive them all; what differs is philosophy, which the comparison below makes concrete.

| Tool | Maker | Install | Context file | Personality |
|------|-------|---------|--------------|-------------|
| Claude Code | Anthropic | `npm install -g @anthropic-ai/claude-code`, installs the `claude` binary globally via npm; requires Node 20+ | `CLAUDE.md` in your project root | The most fully-featured of the five: supports autonomous subagents that spawn their own loops, a rich MCP tool ecosystem, and the finest-grained permission gates (allow once / allow for session / allow always, per command pattern) |
| Codex CLI | OpenAI | `npm install -g @openai/codex`, installs the `codex` binary; the core is written in Rust for speed, wrapped in a Node package for distribution | `AGENTS.md` in your project root | Configured via a TOML file that names multiple model providers; you can point it at OpenAI, Azure, or any compatible endpoint in the same config block |
| Gemini CLI | Google | `npm install -g @google/gemini-cli`, installs the `gemini` binary; authenticate with `gemini auth login` the first time | `GEMINI.md` in your project root | Comes with the most generous free tier of the commercial tools; uses a three-tier skill discovery system (local -> project -> global) to find custom capabilities |
| opencode | opencode.ai | `curl -fsSL https://opencode.ai/install \| bash`, a single-line installer that detects your OS and places the binary on your PATH | `AGENTS.md` in your project root (same spec as Codex) | The most provider-flexible of the group: it speaks to any OpenAI-compatible backend, which means you can point it at Claude, Gemini, local Ollama, or any API that follows the spec, all via a small JSON config file |
| pi | pi.dev | `npm install -g @mariozechner/pi-coding-agent`, installs the `pi` binary; no gate configuration needed because there are no gates | Minimal, reads a small `pi.md` if present but does not require it | Deliberately stripped down: no permission gates, no plan mode, no subagents. This is not a limitation to fix; it is a design choice that makes pi fast and low-ceremony for quick experiments. Use it for low-stakes exploration where speed matters more than oversight |

A few more belong to our course ecosystem and are covered where they live: **freebuff**, a task harness we run as a container in the local stack (the agent stack module deploys it; configure per its README); **KiloCode**, the VS Code-native member, in Part III; and **LM Studio Bionic**, a desktop **agent for open, local models** (GLM- and Kimi-class) that spans the chat and code paradigms and adds local voice input, with an optional Zero-Data-Retention cloud path for the largest open models.  Bionic is the same data-minimization story as the local gateway in Section 6: the model runs on hardware you control, so privacy-sensitive coursework never leaves your machine.  Each tool authenticates on first run (`claude` then `/login`, or an exported API key per its docs); the course site lists the current free-access path for each.

## 2.  The First Session, Step by Step

From zero to a working session, with Claude Code as the example (the others are near-identical):

The following commands take you from a fresh machine to a running Claude Code session.  Watch carefully for the authentication step; the tool will prompt you to log in on first launch.

```bash
node --version                                # 1. confirm Node 20+
npm install -g @anthropic-ai/claude-code      # 2. install
cd ~/projects/my-first-agent-project          # 3. ALWAYS start in the project dir
claude                                        # 4. launch; authenticate when prompted
```

Then, inside the session, the rhythm: describe a small goal ("write a Python script that fetches the weather for Collegeville and prints it; include error handling with traceback"), watch the agent read the directory, review each proposed edit and command at its gate, approve or refuse, and iterate.  Useful in-session commands shared (with small spelling differences) across tools: `/help`, `/clear` (reset the conversation), `/model` (switch models), and plain `Ctrl+C` twice to leave.  **Start the tool in the right directory**: the working directory *is* the agent's world, the same scoping idea as a Docker mount, and the most common beginner error is launching from `~` and granting an agent your entire home directory.

---

## 2b.  Install, Configure, Run: Every Tool, Concretely

Section 2 walked one tool end to end.  Here is the same path for each of the others, so you can pick one and be running in ten minutes.  **You do not need all of them**; install one, finish the session, and add a second only when you want to compare.

### Prerequisites, once

```bash
node --version     # need 20+ for the Node-based tools; install from nodejs.org or via nvm
python3 --version  # need 3.10+ for the Python-based tools
git --version      # every one of these tools assumes git
```

If `node` is missing and you would rather not install it on your host, skip to §2c and run the tool in a container instead.

### The tools, side by side

| Tool | Install | Launch | Config lives in | Auth |
|---|---|---|---|---|
| **Claude Code** | `npm i -g @anthropic-ai/claude-code` | `claude` | `~/.claude/`, project `CLAUDE.md` | Browser login on first run, or `ANTHROPIC_API_KEY` |
| **Codex CLI** | `npm i -g @openai/codex` | `codex` | `~/.codex/config.toml`, project `AGENTS.md` | `OPENAI_API_KEY` or sign-in |
| **Gemini CLI** | `npm i -g @google/gemini-cli` | `gemini` | `~/.gemini/`, project `GEMINI.md` | Google sign-in or `GEMINI_API_KEY` |
| **opencode** | `npm i -g opencode-ai` | `opencode` | `~/.config/opencode/opencode.json`, project `opencode.json` | Provider key, or a local gateway |
| **Aider** | `pip install aider-chat` | `aider` | `~/.aider.conf.yml`, project `CONVENTIONS.md` | Provider key in env |

> **Watch out!** `npm i -g` on some systems wants `sudo`, which installs the tool as root and then complains about permissions later.  The clean fix is a Node version manager (`nvm`) so your global installs land in your home directory, or a container, which sidesteps the question entirely.

### First run, in order

1.  **`cd` into the project first.**  The working directory is the agent's world.  Launching from `~` hands the agent your whole home directory, the same mistake as `-v $HOME:/work` in the Docker module.
2.  **Authenticate.**  Most tools open a browser on first launch.  For a key-based setup, export it in your shell profile rather than pasting it into the session:
   ```bash
   echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc && source ~/.bashrc
   ```
3.  **Check the model and the mode** before you type a real task: `/model` to see what you are talking to, and the tool's status line for the current permission mode.
4.  **Give it a small, checkable job first** ("add a docstring to every function in `parser.py`") so you see the review loop before you rely on it.
5.  **`git status` when you are done.**  If you cannot see the agent's work as a diff, stop and fix that before continuing.

### Configure: the three files that matter

Every one of these tools reads a **project instruction file**: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `opencode.json`, `CONVENTIONS.md`.  They differ in name and format, not in purpose: standing instructions so you stop retyping context.  Start with four headings and grow it only when you catch yourself repeating a correction:

```markdown

# Project
One paragraph: what this is, who uses it, what "working" means.

# Conventions
Language version, formatter, test command, naming rules.

# Boundaries
Files and directories to never touch. Secrets never to read or print.

# How to verify
The exact command that proves a change is good: `pytest -q`, `npm test`.
```

Commit that file.  It is the cheapest reliability improvement available, and it is reviewable by your teammates in a pull request like any other code.

---

## 2c.  Running Any of Them in a Container

If you would rather not install a coding agent on your laptop at all (or you want the freedom to let it work without approving every step), run it in the fenced container from the Docker module:

```bash
docker run -it --rm \
  -v "$PWD:/work" \
  -v "$HOME/notes/vault:/reference:ro" \
  -e ANTHROPIC_API_KEY \
  --cap-drop ALL --security-opt no-new-privileges \
  course-agent claude
```

One writable mount (`/work`, git-tracked), one read-only mount, no host credentials.  The **[Docker from Zero]({{ site.baseurl }}/Tutorials/Docker)** module builds `course-agent` and explains each flag, including when disabling the permission prompts becomes a reasonable trade rather than a reckless one.

---

## First Contact

**Why this matters:** The first session with an agentic CLI is a bit like handing someone the keys to your apartment and watching what they do.  The agent will open drawers (read files) you did not point it to, propose actions you did not anticipate, and ask permission at moments that reveal its internal plan.  Paying close attention during this first session (rather than just clicking "approve") is what transforms you from a passive user into someone who can supervise an agent intentionally.  Think of the permission gates as the dashboard of a car: you can ignore them and still arrive somewhere, but reading them tells you a lot about where the car thinks it is going.

Each pair installs one assigned tool, runs the weather-script task above in a fresh directory, and captures the transcript.

### Questions to Work Through

1.  List every permission request your tool raised, in order.  Which proposed action was the riskiest, and would you have noticed without the gate?

   *Hint:* Most tools print a gate prompt that looks like `Allow [tool] to run: <command>? (y/n/a)`.  Review your transcript top-to-bottom and copy every line containing that pattern.  For the "riskiest" judgment, consider: does the action write to disk, make a network call, or run a shell command with side effects?  Commands like `pip install`, `curl`, or any `rm` are higher risk than a simple `cat`.

2.  Compare transcripts across the team's tools: same task, different agents.  Where did they differ in plan, in verbosity, in caution?  Connect one difference to the table's "personality" column.

   *Hint:* Look for three things in each transcript: (a) how many steps the agent planned before acting, (b) how many files it read before writing any, and (c) how many permission gates it raised.  A tool described as "most complete" in the personality column should show more gates than one described as "deliberately small."  Quote a specific line from two transcripts to anchor your comparison.

3.  The agent read files you never mentioned.  Which ones, and how do you know?  (Find the evidence in the transcript; observability is a course theme, not an accident.)

   *Hint:* Look for lines where the tool reports a file-read action: Claude Code shows `Read file: <path>`, Codex shows a similar tool-use trace, and Gemini prints the file name before processing it.  Common files an agent reads even in an "empty" directory: `.gitignore`, `pyproject.toml`, `requirements.txt`, `README.md`, and any `*.md` context file.  If your directory is truly empty, the agent will likely say so; that is also useful evidence.

With the anatomy clear and your first session running, Part II builds on that foundation by showing how to give the agent standing instructions, calibrate its safety gates, and route it through your local model stack.

---

# Part II: Context, Gates, and the Local Gateway

In this part, you will write a project context file, configure permission gates deliberately, and redirect your CLI tool through the course's local gateway, the three controls that turn a capable tool into a supervised one.

## 3.  Project Context Files: Standing Instructions

Imagine you hired a very capable but completely new contractor to work on your apartment.  On day one you explain everything: "don't touch the walls in the east bedroom, always ask before buying materials, and the supply list is in the kitchen drawer."  On day two, you would have to explain it all again, unless you left a note on the door.  The context file is that note on the door.  Every tool reads its context file (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) from the project root at startup, making it the place for standing instructions that survive every session: what the project is, conventions to follow, commands to use for testing, and boundaries.  A starter worth copying:

```markdown

# CLAUDE.md

## Project
A CS357 lab implementing a critique-and-refine loop. Python 3.12.

## Conventions
- Exception handling: print with a [module:function] prefix and traceback.print_exc()
- Configuration lives in config.json; never hardcode paths or models
- Run tests with: python -m pytest tests/ -v

## Boundaries
- Never modify files under data/raw/ (read-only source material)
- Ask before adding any new dependency
```

This is the same pattern as the vault's `AGENTS.md` in the second brain module, and the same pattern as a system prompt: **context as a versioned artifact**, not a thing you retype.  Teams that maintain a good context file find their agents need half the correction.

## 4.  Permission Gates Are Your Governance Layer

The gates are not friction; they are the course's human-oversight principle running on your laptop.  Think of them as the "sign here" moments in a legal document: they exist so that later, if something goes wrong, there is a clear record of what was authorized by a human and what was not.  Tools differ in granularity (Claude Code lets you allow a command pattern once, for the session, or always; pi has no gates at all, which is exactly why it is for low-stakes exploration only).  Calibrate deliberately: auto-approve reads, gate writes, and *always* gate `rm`, `git push`, network calls to new hosts, and anything touching credentials.  When a tool offers a "skip all permissions" mode, recognize it as the same trade the Governance direction of the Responsible AI in Practice assignment analyzes, and decline it for coursework.

A teammate launches an agent CLI from their home directory instead of the project directory "to save a cd".  The principled objection is:

- The agent will run more slowly because it must index all files before starting; launch location is a performance concern, not a safety one
- The working directory defines the agent's accessible world, so launching from home grants it the entire filesystem of personal documents rather than one scoped project
- Context files are only read from the home directory, so launching from there is actually required for the context file to be found
- The working directory only affects which files the agent proposes to edit in its plan; file tool calls are still scoped to the project folder

<details markdown="1"><summary>Answer</summary>

The working directory defines the agent's accessible world, so launching from home grants it the entire filesystem of personal documents rather than one scoped project

</details>

---

## 5.  Permission Modes: The Dial Above the Gates

Section 4's gates fire one action at a time.  Sitting *above* them is a coarser control that most tools now expose: a **permission mode**: a single setting that fixes your default posture for the whole session, and therefore decides how many individual gates you will ever see.  If a gate is the "sign here" on one line of a contract, the mode is the standing instruction you give your lawyer *before* reading any of it: "stop me on everything," "let the small stuff through," or "just handle it."  You set the dial once; every gate inherits its default.  The gates from Section 4 do not disappear; the mode decides which of them still get to interrupt you.

Four postures have converged across the tools, ordered here from most supervised to least:

| Mode | What it does | Gates you still see | Reach for it when |
|------|--------------|---------------------|-------------------|
| **Plan / read-only** | The agent may read files and reason out loud, but changes *nothing*; it produces a written plan and waits for your approval before acting | Every write and shell command is blocked until you leave the mode | Exploring an unfamiliar codebase, or getting a design reviewed before a single line changes |
| **Default (ask)** | The normal loop: the agent acts, but pauses at each consequential gate for a yes/no | Every write, shell command, and irreversible action | Ordinary supervised work, the calibration Section 4 describes |
| **Auto-accept edits** | File edits apply without a per-edit prompt; shell commands and irreversible actions *still* gate | Shell commands, network calls, `rm`, `git push` | A well-scoped task where you trust the edits but not the side effects, e.g., renaming a symbol across many files in a git repo you can `reset` |
| **Full-auto / bypass** ("YOLO") | No gates at all; the agent reads, writes, and runs commands unattended | None | Almost never for coursework, only inside a throwaway container with no network and no credentials |

The labels differ by tool, but it is the same dial.  In **Claude Code** you cycle modes with **Shift+Tab** (default -> auto-accept edits -> plan), and the fully ungated mode is the `--dangerously-skip-permissions` flag, whose name is itself the warning.  **Codex** exposes approval modes plus a `--full-auto` flag; **Gemini CLI** has a `--yolo` flag; **opencode** offers a plan-style review before it applies a change.  **pi**, true to its personality in the Part I table, effectively has *only* the last row; it is always full-auto, which is exactly why the course reserves it for low-stakes throwaway work.

The connection to the human-in-the-loop principle is direct: a mode is how you *spend your oversight budget*.  Plan mode spends it all up front: you review one plan instead of twenty gates.  Full-auto spends none, and inherits all the risk.  Auto-accept edits is the deliberate middle: it aims your attention at the actions that can actually leave your machine or destroy data, which is precisely where the governance module argues a human's judgment is worth the interruption.  The mistake is never simply "picking a permissive mode"; it is picking one *without matching it to the task's blast radius*.  Auto-accept edits inside a git repo you can roll back is prudent; the same mode on files with no version control is how an afternoon's work quietly disappears.

A student sets their agent to **auto-accept edits** mode to refactor a Python package, reasoning that they will review the final diff in git anyway.  Midway, the agent decides it needs a library and proposes `pip install requests`.  What happens?

- It runs without a prompt; auto-accept edits approves every action, shell commands included, so the install proceeds silently
- It stops at a gate: auto-accept edits waives the prompt for *file edits only*; a shell command like `pip install` still pauses, which is the whole point of a mode that sits between "ask" and "full-auto"
- It runs without a prompt, but only because `pip install` counts as a file edit since it writes package files to disk
- It stops, because auto-accept mode automatically reverts to "ask" mode the instant any shell command is proposed

<details markdown="1"><summary>Answer</summary>

It stops at a gate: auto-accept edits waives the prompt for *file edits only*; a shell command like `pip install` still pauses, which is the whole point of a mode that sits between "ask" and "full-auto"

</details>

---

## 6.  Routing Through the Local Gateway

Our stack (agent stack module) exposes one OpenAI-compatible endpoint for everything, and pointing a commercial CLI at it is two environment variables:

```bash
export ANTHROPIC_BASE_URL=http://localhost:4000   # redirect all API calls to local gateway
export ANTHROPIC_API_KEY=sk-litellm-local         # dummy key accepted by the local proxy
claude        # now running against local models through the gateway
```

The flags explained: `ANTHROPIC_BASE_URL` overrides the default `https://api.anthropic.com` endpoint; any value you set here is where Claude Code sends its requests. `ANTHROPIC_API_KEY` is still required by the client library, but the gateway ignores its value and uses its own routing rules instead; `sk-litellm-local` is a conventional placeholder.

For the other tools, the same redirect looks slightly different:

```bash

# opencode: edit ~/.config/opencode/opencode.json and set, inside the

# provider's "options" block:

# "baseURL": "http://localhost:4000/v1"

# "apiKey":  "sk-litellm-local"

# Codex: add to ~/.codex/config.toml:

# [model_providers.local]

# base_url = "http://localhost:4000/v1"

# api_key  = "sk-litellm-local"

# pi: add to models.json in your pi config directory:

# { "provider": "openai", "base_url": "http://host.docker.internal:11434/v1" }

# (use host.docker.internal instead of localhost when running pi in a container)
```

The payoff is the unbundling theme of this course: the *interface* (the CLI you like) is now independent of the *model* (local, free-tier, or frontier), swappable per task with `/model`.  For privacy-sensitive coursework, local routing is not just cheaper; it is the data-minimization requirement satisfied by architecture.

Now that your tool is scoped, instructed, and routed, Part III shows how to bring it into your editor and run it inside a container so the workspace boundary is enforced by the operating system, not just convention.

---

> **Common Misconception:** Many students assume that "permission gates" and "the working directory" are two separate safety measures that each protect against different risks.  In practice, they compose: the working directory limits *what* the agent can touch (only files under that directory are reachable by the file tools), while permission gates limit *when* the agent acts (it must pause and ask before each consequential step).  Disabling either one alone cuts your safety roughly in half.  Turning off gates while keeping a narrow working directory still lets the agent delete every file in your project without a pause.  Keeping gates active while launching from `~` means every gate prompt covers a blast radius of your entire home directory.  You need both, calibrated together.

---

# Part III: VS Code, Containers, and Practice

In this part, you will integrate your chosen agent CLI into VS Code and understand the containerized invocation pattern so you can isolate an agent's filesystem access by design rather than by trust.

## 7.  Driving Agents from VS Code

Three levels of integration, in increasing depth.  **Level one, the integrated terminal** (Ctrl+`): launch any CLI tool there and you get the workflow most professionals actually use, agent in the bottom pane, live diffs in the editor above; this works today for every tool in the table with zero configuration.  **Level two, official extensions**: Claude Code and Codex ship VS Code extensions (search the marketplace by name) that surface the session in a panel, render proposed diffs in VS Code's native diff view, and let you approve from the editor; install, sign in, and the workflow is the terminal workflow with better optics.  **Level three, editor-native agents**: KiloCode lives entirely inside VS Code with direct access to the language server (diagnostics, symbols, refactoring), and connects to our gateway with a one-field base URL change in its settings.  Recommendation for this course: level one for fluency first, then level two; you will debug problems best in the layer you understand.

## 8.  Containerized Invocation (the Course Pattern)

Our stack runs every CLI tool inside a dedicated container with three mounts: an identity directory (the tool's logins and settings), the shared workspace, and an optional read-only skills directory.  The shape, from the course deploy scripts:

The following `docker run` command is the standard course pattern for running a CLI agent inside a container.  Read each flag carefully before running it; each one enforces a specific boundary between the agent and your host machine.

```bash
docker run --rm -it \
  --add-host=host.docker.internal:host-gateway \
  -v "$HOME/agents/commercial/claude/home:/home/agent" \
  -v "$HOME/agents/workspace:/workspace" \
  -w /workspace \
  commercial-ai:latest claude
```

The flags explained: `--rm` deletes the container when it exits (experiments are self-cleaning). `-it` allocates an interactive terminal (required for any REPL). `--add-host=host.docker.internal:host-gateway` makes `host.docker.internal` resolve to your actual machine's IP from inside the container, which is how containerized tools reach the local gateway at `http://host.docker.internal:4000`.  The two `-v` flags mount directories from your host into the container: the first keeps the agent's authentication tokens and settings persistent across container restarts (otherwise you would re-login every time); the second is the shared workspace the agent reads and writes. `-w /workspace` sets the container's working directory so the agent's world is exactly the workspace mount, nothing else.  The payoff paragraph from the Docker module applies verbatim: the agent sees exactly what is mounted and nothing else, identities hot-swap by changing one path, and an experiment is destroyed with the container.  The agent stack module provides the full `build.sh`/`run.sh` set; today, understand *why* the mounts are shaped this way.

---

# Part IV: Running Agents Unattended, Terminal Multiplexing and herdr

So far every session has assumed you sit and watch.  But a coding agent working through a real task can run for many minutes, and you will often want to start several at once and step away.  In this part you will learn the mechanism that lets an agent keep working after you disconnect (the terminal multiplexer) and **herdr**, a multiplexer built specifically for herding coding agents, and you will turn "walk away and come back" into a discipline rather than a hope.

## 9.  Terminal Multiplexing: Sessions That Outlive Your Connection

Here is a failure every remote worker eventually hits: you SSH into a machine, launch a half-hour agent task, close your laptop for the train, and the task dies, because it was a child of your SSH connection and the connection went away.  A **terminal multiplexer** (`tmux` or the older `screen`) fixes this by running your shell inside a persistent **server process** that is *not* tied to your terminal.  You **attach** a view to it, and you can **detach** that view without stopping anything underneath.

```bash
tmux new -s agents        # start a persistent session named "agents"
claude                    # launch a long agent task inside it

# press Ctrl-b then d      -> DETACH: the view closes, the agent keeps running

# ... close your laptop, ride the train, open it again ...
tmux attach -t agents     # REATTACH from anywhere, even a fresh SSH login
```

The session is a room that keeps its lights on after you leave.  Detaching is walking out the door; the work inside continues.  Multiplexers also **split** one terminal into several panes, so you can watch two or three agents side by side.  This is the mechanical foundation of every "walk away and come back" workflow: a long agent run belongs inside a multiplexer, never in a raw SSH shell that dies with the connection.

## 10. herdr: An Agent-Aware Multiplexer

`tmux` is agent-*ignorant*: to it, a pane running Claude Code is just bytes on a screen.  It cannot tell you *which* of your five agents is stuck waiting for a permission answer and which is still churning.  **herdr** closes that gap.  It is a single Rust binary: think "`tmux` rebuilt from scratch with first-class awareness of coding agents."  Its architecture mirrors `tmux`: a persistent, **headless server** keeps every agent's pane and process alive, and a **TUI client** attaches to it.  What herdr adds is *state*: it watches each agent and shows you, at a glance, whether it is **blocked** (needs your input), **working**, or **done**.

That one addition changes the job from *babysitting one agent* to *supervising a herd*. herdr runs Claude Code, Codex, opencode, Cursor Agent, Copilot CLI, and 15+ other agents each in its own real pane; you glance at the status column, jump to whichever agent is blocked, answer its gate, and move on.  And because the server is persistent, you **detach and reattach from any terminal, over SSH, even from your phone**, and the herd survives restarts.

| Capability | `tmux` / `screen` | **herdr** |
|------------|-------------------|-----------|
| Persistent, detachable server | yes | yes |
| Reattach over SSH / from a phone | yes | yes |
| Split panes for many agents at once | yes | yes |
| **Knows which agent is blocked / working / done** | no (just panes of text) | yes |
| Purpose-built for coding-agent workflows | no | yes |

The relationship is not "herdr *versus* `tmux`"; it is `tmux`'s persistence *plus* the observability an agent workflow needs.  Learn the plain multiplexer first (it is everywhere, on every server); reach for herdr when you are running enough agents that "which one needs me?" becomes the real question.

## 11.  The "Walk Away and Come Back" Discipline

Put the pieces together and the pattern has three properties, each supplied by something you have now seen:

- **Persistence**: the background server keeps agents alive after you disconnect (the multiplexer, §9).
- **Observability**: agent-state awareness tells you *who needs you* without your having to watch (herdr, §10).
- **Reattachment**: you resume from any terminal, over SSH, from a phone (both).

But persistence cuts both ways, and this is the governance point: **detaching does not pause an agent.**  It keeps reading, editing, running commands, and spending tokens the entire time you are gone.  An agent you would supervise closely for five minutes is the *same* agent, now acting for an hour with nobody at the gate.  That is exactly where the controls from Parts II and III stop being optional.  Before you walk away, set the permission **mode** deliberately (Section 5): an unattended agent in full-auto is an unattended agent with your whole account's blast radius, and prefer to run it inside the **scoped container** from Section 8, with no credentials mounted and a workspace you can `git reset`.  The rule of thumb: *the less you are watching, the more the environment, not your attention, has to be the thing keeping the agent safe.*  Never hand `--dangerously-skip-permissions` to an agent you are about to stop watching on a machine that matters.

This same idea (an agent that keeps working while you are away) scales up in the next module from "several agents in panes" to **loops that restart themselves and crews that coordinate** (the Ralph loop, `gnhf`, and `firstmate`).

### Questions to Work Through

1.  A classmate runs a 40-minute refactor over SSH *without* a multiplexer, closes their laptop, and returns to find the agent gone and the work half-done.  Explain precisely what killed the process, and what one command at the start would have prevented it.

   *Hint:* Think about the process tree.  Your shell (and everything it launched) is a child of the SSH session.  What happens to children when their parent (the connection) is terminated?  A multiplexer moves the agent out from under that parent into a server process that the disconnect does not touch.

2. herdr and `tmux` both keep agents alive after you detach, but only herdr tells you which agent is blocked.  Describe a concrete situation with three simultaneous agents where that difference changes how much time you waste.  Then name one situation where plain `tmux` is still the right choice.

   *Hint:* With three agents in plain `tmux` panes, how do you discover that agent #2 has been sitting at a permission prompt for ten minutes?  You cycle through panes and read.  Now consider a server where you cannot install anything new: what is guaranteed to already be available?

3.  "The environment, not your attention, keeps an unattended agent safe."  Take the containerized pattern from Section 8 and the permission modes from Section 5, and describe the specific configuration you would use before detaching from an agent overnight.  What is each choice protecting against?

   *Hint:* Walk the blast radius.  What can the agent reach (the `-v` mounts and `-w` working dir)?  What can it do without asking (the permission mode)?  What credentials are within reach if it goes wrong (what did you *not* mount)?  How do you undo an hour of bad edits (what makes the workspace reversible)?

> **Common Misconception:** Many students believe that detaching from a multiplexer *pauses* the agent, the way closing a laptop lid sleeps a machine, so "I'll detach to stop it for a bit" feels safe.  It does the opposite: detaching only removes your *view*.  The agent keeps running at full speed on the persistent server, reading files, executing commands, and spending tokens with no one watching the gates.  Persistence is the feature you came for and the risk you must plan around, which is why the permission mode and the container boundary are set *before* you walk away, not after you come back.

You start a long agent task inside `tmux`, press `Ctrl-b d`, and close your SSH connection.  Thirty minutes later you `tmux attach` from a different machine.  What do you find?

- The task is paused at the moment you detached and resumes only now that you have reattached
- The task was killed when the SSH connection closed and must be restarted from scratch
- The task kept running the whole time on the multiplexer's persistent server, and you are now viewing its current state, including anything it did while you were gone
- The task ran only while at least one client was attached, so it made no progress during the 30 minutes you were disconnected

<details markdown="1"><summary>Answer</summary>

The task kept running the whole time on the multiplexer's persistent server, and you are now viewing its current state, including anything it did while you were gone

</details>

---

## 12.  Exercises

1.  *Install two.*

   *What to do:* Install Claude Code plus one other tool from the comparison table, complete authentication for both, and run the identical three-line task ("write a Python script that fetches the weather for Collegeville, prints the result, and handles errors with a traceback") in both tools inside a fresh empty directory.  Submit both full transcripts with one paragraph comparing the experience.

   *Starter hint:* Run these commands in order, substituting your second tool's install command from the table:
   ```bash
   mkdir ~/cs357-exercise1 && cd ~/cs357-exercise1
   npm install -g @anthropic-ai/claude-code   # install Claude Code
   npm install -g @google/gemini-cli          # example: install Gemini CLI as your second tool
   claude                                     # start Claude Code session; /login if prompted
   ```

   *You've succeeded when:* You have two transcript files saved, each showing the full exchange from the first prompt to a working Python script, and your comparison paragraph names at least one specific difference in how the two tools handled permission gates or file reads.

2.  *Context file experiment.*

   *What to do:* Run the same task in a project directory first *without* any context file, then create the starter `CLAUDE.md` shown in Section 3 (adapt the project description to your actual task), and rerun the identical prompt.  Document two concrete behavior changes the context file caused: things the agent did differently in session two that you can point to in the transcript.

   *Starter hint:*
   ```bash
   mkdir ~/cs357-exercise2 && cd ~/cs357-exercise2
   claude   # run your task; save transcript as transcript-no-context.txt
   # now add the context file:
   # create CLAUDE.md in ~/cs357-exercise2 with the starter from Section 3
   claude   # run the identical task again; save as transcript-with-context.txt
   diff transcript-no-context.txt transcript-with-context.txt   # look for differences
   ```

   *You've succeeded when:* You can quote two specific lines (one from each transcript) that show a concrete difference in agent behavior attributable to the context file, such as a different test command, a different boundary the agent respected, or a different convention in the generated code.

3.  *Gate calibration.*

   *What to do:* In your preferred tool, locate the permission settings and configure them so that file reads are auto-approved, file writes are gated, and shell commands are gated.  Then deliberately provoke each gate type once (read a file, write a file, run a shell command) and screenshot each gate prompt as it appears.

   *Starter hint:* For Claude Code, gate settings live in the settings file and can also be set interactively.  The quickest way to configure per-session behavior is the `--allowedTools` and `--disallowedTools` flags at launch:
   ```bash
   cd ~/cs357-exercise3
   # Launch with reads allowed automatically, writes and shell requiring approval:
   claude --allowedTools "read_file" --disallowedTools "write_file,execute_command"
   # Then inside the session, ask: "read README.md, then create hello.py, then run it"
   # Each of the three actions will hit a different gate behavior
   ```

   *You've succeeded when:* You have three screenshots showing (a) a file read that passed silently, (b) a file write gate prompt, and (c) a shell command gate prompt, and you can explain in one sentence why each is calibrated the way it is.

4.  *Gateway switch.*

   *What to do:* With the course stack running locally, set the two environment variables from Section 6 to route your tool through the local gateway.  Verify the redirect worked by asking the agent to name the model it is using.  Then switch models mid-session using `/model` and send the same prompt to both models.  Write a two-sentence report on any latency or quality differences you noticed.

   *Starter hint:*
   ```bash
   # In your terminal, before launching the tool:
   export ANTHROPIC_BASE_URL=http://localhost:4000   # redirect to local gateway
   export ANTHROPIC_API_KEY=sk-litellm-local         # placeholder key for the proxy
   cd ~/cs357-exercise4
   claude   # now talking to the gateway
   # Inside the session, type: "What model are you?"
   # Then: /model    (to see available models and switch)
   ```

   *You've succeeded when:* The agent's response to "what model are you?" names a model served by your local gateway (not the default Anthropic cloud model), and you have tried at least two different models via `/model` with the same prompt.

5.  *VS Code session.*

   *What to do:* Complete one full task entirely inside VS Code: either in the integrated terminal (Ctrl+`) or via the official Claude Code or Codex extension if you have it installed.  Use the editor's diff view to review every proposed file change before you approve it.  Reflect in three sentences: did seeing the diff visually (rather than reading it in the terminal) change any decision you made?

   *Starter hint:*
   ```bash
   # Open VS Code in your project directory:
   code ~/cs357-exercise5
   # Press Ctrl+` to open the integrated terminal
   cd ~/cs357-exercise5
   claude   # launch the agent in the VS Code terminal
   # When the agent proposes a file edit, look at the diff view that appears in the editor pane above
   ```

   *You've succeeded when:* You have approved at least one change and refused or revised at least one proposed change based on what you saw in the diff view, and your three-sentence reflection names the specific change you caught or reconsidered.

6.  *Detach and reattach.*

   *What to do:* Start a multi-minute agent task inside a multiplexer (`tmux`, or `herdr` if you have installed it), give the agent a goal that will take a little while ("write a small CLI tool with tests and run the tests"), then **detach** the session.  Do something else for two minutes.  **Reattach** and confirm the agent kept working while you were gone.  Write two sentences: what state did you return to, and what would have happened without the multiplexer?

   *Starter hint:*
   ```bash
   tmux new -s ex6            # persistent session
   cd ~/cs357-exercise6
   claude                     # give it a multi-step goal
   # press Ctrl-b then d      -> detach; the agent keeps running
   tmux ls                    # confirm the session still exists
   tmux attach -t ex6         # reattach and inspect progress
   ```

   *You've succeeded when:* Your reattached session shows progress the agent made *after* you detached (new files, more test output, or a completed task), and you can state in one sentence why the same task in a plain SSH shell would not have survived a disconnect.

7.  *Chat vs. code on local models (optional).*

   *What to do:* Install **LM Studio Bionic**, load an open model, and try the same small task twice: once in **chat** mode (you copy the code out and run it yourself) and once as a **Code project** pointed at a local folder (Bionic reads, edits, and runs).  Write three sentences comparing the two experiences and mapping each to a row of the Three Paradigms table.

   *Starter hint:* Create an empty folder, open it as a Code project in Bionic, and give it the weather-script task from Section 2.  In chat mode, paste the same prompt into a plain chat and notice everything *you* have to do that the Code project did on its own (save the file, run it, read the error, fix it).

   *You've succeeded when:* You can name at least two concrete steps that the Code project performed for you but that you had to perform by hand in chat mode, and you correctly identify which paradigm each mode belongs to.

---

## Reflection Prompt

In your notebook, respond at three levels:

**Personal level:** These tools place a capable agent one keystroke from your filesystem, and the differences between them are mostly differences in how much friction they put between intention and action.  After today, where do you personally want that friction?  Did your answer change from what it was before you ran your first session, and if so, what in the session shifted it?

> *Hint:* Think about the permission gates you met above.  Did any gate prompt make you pause and reconsider?  Did any gate fire for an action you had not anticipated?  Your intuition about friction may have updated from the session itself.

**Technical level:** The working directory, the context file, and the permission gates form a three-layer scoping system.  Describe in your own words what each layer controls and what breaks if you remove any one of them.  Is there a fourth layer you think is missing?

**Societal level:** These tools are yours in the sense that you installed them and you approve their actions.  But the models they connect to are trained on data you did not consent to, by companies whose values you did not set, running on infrastructure you do not own.  Is your answer about where you want friction the same for yourself as for the students you might someday supervise, or for a professional domain (medicine, law, journalism) where the stakes of an unreviewed agent action are higher than a broken Python script?

---

## Where This Goes Next

In the *The Local Agent Stack: Wiring Containers into a System* activity you will move from individual CLI tools to an **orchestrated agent stack**: multiple tools running behind a shared gateway, with a task harness (freebuff) that can route work to the right model automatically.  The containerized invocation pattern you saw in Section 8 is the building block; next you will see how those containers are networked together, how the gateway decides which model handles each request, and how to add your own tools to the MCP ecosystem the entire stack shares.  Everything you practiced today (working directories, context files, gate calibration, gateway routing) will be preconditions for that module, so make sure your Exercise 4 gateway redirect is working before you take on that activity.  The *Coding Agents* activity then takes the "walk away and come back" idea from Part IV one step further: into **loops that restart themselves and crews that coordinate** (the Ralph loop, `gnhf`, and `firstmate`).

---

## 13.  Further Reading

- Each tool's official docs: docs.anthropic.com (Claude Code), the Codex CLI repository, the Gemini CLI repository, opencode.ai, pi.dev.
- W. Mongan, "Building a Private AI Stack" (billmongan.com, May 2026): the containerized invocation and gateway routing patterns in full.
- The Model Context Protocol site (modelcontextprotocol.io): the tool-integration standard these CLIs converge on.
- **herdr**: the agent-aware terminal multiplexer: github.com/ogulcancelik/herdr.
- **tmux**: the ubiquitous terminal multiplexer that underlies the "detach / reattach" pattern: github.com/tmux/tmux/wiki.
- **LM Studio Bionic**: an agent for open, local models spanning chat and code: lmstudio.ai/blog/introducing-lm-studio-bionic.
- **Cowork** and open alternatives: Claude Cowork (claude.ai), and **OpenWork**, the open-source, opencode-powered cowork tool: github.com/different-ai/openwork.
