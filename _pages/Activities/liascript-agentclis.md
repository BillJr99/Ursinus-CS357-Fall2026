# Agentic CLI Tools: Claude Code, Codex, Gemini, opencode, pi, and Friends
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-agentclis.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentclis.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Agentic CLI Tools: Claude Code, Codex, Gemini, opencode, pi, and Friends

The agent loop you study in this course ships today as a family of **terminal programs**: you describe a goal, the agent reads your files, proposes shell commands and edits, asks permission at the gates, and iterates. This tutorial installs the major tools from zero, teaches the shared workflow they all follow, and shows how to drive them from inside VS Code. The arc: **the shared anatomy $\rightarrow$ installing the big five $\rightarrow$ project context files $\rightarrow$ permission gates and supervision $\rightarrow$ routing them through our local gateway $\rightarrow$ VS Code integration**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisites: the shell module (you will live in the terminal) and Node.js 20 or later installed (`node --version` to check; install from nodejs.org or your package manager). A free-tier or course-provided API path exists for every tool; nobody needs to pay to complete this module. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: One Anatomy, Many Tools

## 1. What Every Agentic CLI Shares

Strip away the branding and every tool in this family is the same machine, the agent loop from week one wearing a terminal interface: a **REPL-style chat** in your project directory; **file tools** (read, edit, create) scoped to that directory; a **shell tool** that proposes commands; **permission gates** before consequential actions; a **project context file** read automatically at startup; and a growing convergence on **MCP** for external tools. Once you can drive one, you can drive them all; what differs is philosophy, which the comparison below makes concrete.

| Tool | Maker | Install | Context file | Personality |
|------|-------|---------|--------------|-------------|
| Claude Code | Anthropic | `npm install -g @anthropic-ai/claude-code` | `CLAUDE.md` | Most complete: subagents, MCP, fine-grained gates |
| Codex CLI | OpenAI | `npm install -g @openai/codex` | `AGENTS.md` | Rust core; native multi-provider TOML config |
| Gemini CLI | Google | `npm install -g @google/gemini-cli` | `GEMINI.md` | Generous free tier; three-tier skill discovery |
| opencode | opencode.ai | `curl -fsSL https://opencode.ai/install \| bash` | `AGENTS.md` | Most provider-flexible; any OpenAI-compatible backend |
| pi | pi.dev | `npm install -g @mariozechner/pi-coding-agent` | minimal | Deliberately small: no gates, no plan mode; for fast exploration |

Two more belong to our course ecosystem and are covered where they live: **freebuff**, a task harness we run as a container in the local stack (the agent stack module deploys it; configure per its README), and **KiloCode**, the VS Code-native member, in Part III. Each tool authenticates on first run (`claude` then `/login`, or an exported API key per its docs); the course site lists the current free-access path for each.

## 2. The First Session, Step by Step

From zero to a working session, with Claude Code as the example (the others are near-identical):

```bash
node --version                                # 1. confirm Node 20+
npm install -g @anthropic-ai/claude-code      # 2. install
cd ~/projects/my-first-agent-project          # 3. ALWAYS start in the project dir
claude                                        # 4. launch; authenticate when prompted
```

Then, inside the session, the rhythm: describe a small goal ("write a Python script that fetches the weather for Collegeville and prints it; include error handling with traceback"), watch the agent read the directory, review each proposed edit and command at its gate, approve or refuse, and iterate. Useful in-session commands shared (with small spelling differences) across tools: `/help`, `/clear` (reset the conversation), `/model` (switch models), and plain `Ctrl+C` twice to leave. **Start the tool in the right directory**: the working directory *is* the agent's world, the same scoping idea as a Docker mount, and the most common beginner error is launching from `~` and granting an agent your entire home directory.

---

## Model 1: First Contact

Each pair installs one assigned tool, runs the weather-script task above in a fresh directory, and captures the transcript.

### Critical Thinking Questions

1. List every permission request your tool raised, in order. Which proposed action was the riskiest, and would you have noticed without the gate?
2. Compare transcripts across the team's tools: same task, different agents. Where did they differ in plan, in verbosity, in caution? Connect one difference to the table's "personality" column.
3. The agent read files you never mentioned. Which ones, and how do you know? (Find the evidence in the transcript; observability is a course theme, not an accident.)

---

# Part II: Context, Gates, and the Local Gateway

## 3. Project Context Files: Standing Instructions

Every tool reads its context file (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) from the project root at startup, making it the place for standing instructions that survive every session: what the project is, conventions to follow, commands to use for testing, and boundaries. A starter worth copying:

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

This is the same pattern as the vault's `AGENTS.md` in the second brain module, and the same pattern as a system prompt: **context as a versioned artifact**, not a thing you retype. Teams that maintain a good context file find their agents need half the correction.

## 4. Permission Gates Are Your Governance Layer

The gates are not friction; they are the course's human-oversight principle running on your laptop. Tools differ in granularity (Claude Code lets you allow a command pattern once, for the session, or always; pi has no gates at all, which is exactly why it is for low-stakes exploration only). Calibrate deliberately: auto-approve reads, gate writes, and *always* gate `rm`, `git push`, network calls to new hosts, and anything touching credentials. When a tool offers a "skip all permissions" mode, recognize it as the same trade your governance assignment analyzes, and decline it for coursework.

[[MC]]
A teammate launches an agent CLI from their home directory instead of the project directory "to save a cd". The principled objection is:
- ( ) The agent will run more slowly with more files present
- (x) The working directory defines the agent's accessible world, so launching from home grants it the entire filesystem of personal documents rather than one scoped project
- ( ) Context files are only read from the home directory
- ( ) There is no objection; directories do not matter to agents

---

## 5. Routing Through the Local Gateway

Our stack (agent stack module) exposes one OpenAI-compatible endpoint for everything, and pointing a commercial CLI at it is two environment variables:

```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_API_KEY=sk-litellm-local
claude        # now running against local models through the gateway
```

opencode does the same in its JSON config (`"baseURL": "http://localhost:4000/v1"`), Codex via a `[model_providers.*]` block in its TOML, and pi via a provider block in `models.json` pointing at `http://host.docker.internal:11434/v1` when containerized. The payoff is the unbundling theme of this course: the *interface* (the CLI you like) is now independent of the *model* (local, free-tier, or frontier), swappable per task with `/model`. For privacy-sensitive coursework, local routing is not just cheaper; it is the data-minimization requirement satisfied by architecture.

---

# Part III: VS Code, Containers, and Practice

## 6. Driving Agents from VS Code

Three levels of integration, in increasing depth. **Level one, the integrated terminal** (Ctrl+`): launch any CLI tool there and you get the workflow most professionals actually use, agent in the bottom pane, live diffs in the editor above; this works today for every tool in the table with zero configuration. **Level two, official extensions**: Claude Code and Codex ship VS Code extensions (search the marketplace by name) that surface the session in a panel, render proposed diffs in VS Code's native diff view, and let you approve from the editor; install, sign in, and the workflow is the terminal workflow with better optics. **Level three, editor-native agents**: KiloCode lives entirely inside VS Code with direct access to the language server (diagnostics, symbols, refactoring), and connects to our gateway with a one-field base URL change in its settings. Recommendation for this course: level one for fluency first, then level two; you will debug problems best in the layer you understand.

## 7. Containerized Invocation (the Course Pattern)

Our stack runs every CLI tool inside a dedicated container with three mounts: an identity directory (the tool's logins and settings), the shared workspace, and an optional read-only skills directory. The shape, from the course deploy scripts:

```bash
docker run --rm -it \
  --add-host=host.docker.internal:host-gateway \
  -v "$HOME/agents/commercial/claude/home:/home/agent" \
  -v "$HOME/agents/workspace:/workspace" \
  -w /workspace \
  commercial-ai:latest claude
```

The payoff paragraph from the Docker module applies verbatim: the agent sees exactly what is mounted and nothing else, identities hot-swap by changing one path, and an experiment is destroyed with the container. The agent stack module provides the full `build.sh`/`run.sh` set; today, understand *why* the mounts are shaped this way.

## 8. Exercises

1. *Install two.* Install Claude Code plus one other tool from the table, complete authentication, and run the same three-line task in both. Submit both transcripts with one paragraph comparing the experience.
2. *Context file experiment.* Run a task in a project without a context file, then add the starter `CLAUDE.md` above (adapted) and rerun. Document two concrete behavior changes the file caused.
3. *Gate calibration.* In your preferred tool, find the permission settings and configure: reads auto-approved, writes gated, shell gated. Provoke each gate once and screenshot it.
4. *Gateway switch.* With the course stack running, route your tool through the local gateway, verify with a prompt that names its own model, then switch models mid-session with `/model`. Two-sentence report on latency and quality differences you noticed.
5. *VS Code session.* Complete one full task entirely inside VS Code (terminal or extension), using the editor's diff view to review every change before approval. Reflect in three sentences: did the visual diff change any decision?

---

## Reflection Prompt

In your notebook: these tools place a capable agent one keystroke from your filesystem, and the differences between them are mostly differences in how much friction they put between intention and action. After today, where do you personally want that friction, and is your answer the same for yourself as for the students you might someday supervise?

---

## 9. Further Reading

- Each tool's official docs: docs.anthropic.com (Claude Code), the Codex CLI repository, the Gemini CLI repository, opencode.ai, pi.dev.
- W. Mongan, "Building a Private AI Stack" (billmongan.com, May 2026): the containerized invocation and gateway routing patterns in full.
- The Model Context Protocol site (modelcontextprotocol.io): the tool-integration standard these CLIs converge on.
