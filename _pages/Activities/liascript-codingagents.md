<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-codingagents.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-codingagents.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Coding Agents: Agentic Development Tools

A **coding agent** is not a smarter autocomplete. When GitHub Copilot suggests the next line, it reads your cursor position and offers a completion you accept or reject. A coding agent reads your entire repository, understands a goal ("add OAuth2 login"), decomposes it into file-level tasks, edits multiple files, runs your test suite, interprets failures, and iterates until the goal is satisfied — or until it runs out of context or budget. The difference is agency: a persistent goal, world-affecting actions, and a loop that continues until done.

This matters for software engineering because it changes the unit of human judgment. Instead of reviewing every keystroke, you review the agent's *plan* before it acts and its *diff* before you merge. Getting that review right is a professional skill this module develops.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Read each model carefully as a team, then answer the Critical Thinking Questions individually before discussing. The Recorder compiles the team's consensus answers; the Presenter will share at least one point of disagreement with the class. After class, complete the Reflection Prompt in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Coding Agent** | An AI system that reads a codebase, makes a plan, edits files, runs commands, and loops until a programming goal is met — without you steering each step | An agent that adds GitHub login to a Flask app by editing five files and running tests on its own |
| **Agent Loop** | The repeated cycle of Perceive → Plan → Act → Verify that an agent runs until its goal is achieved or its budget runs out | The agent reading test output (Verify) and going back to fix the code (Plan → Act) when a test fails |
| **Context Window** | The fixed-size "working memory" an LLM can read at one time; older information scrolls out as new information is added | A large codebase has millions of tokens — the agent must choose which files to load and which to skip |
| **Diff / Patch** | A file showing exactly which lines were removed (marked −) and which were added (marked +) when a file is changed | The agent's changes to `app.py` shown as a diff before you decide whether to merge them |
| **Step Budget** | A maximum number of actions or loop iterations the agent is allowed to take before it must stop, preventing runaway cost | Setting `MAX_ITERATIONS = 25` so a stuck agent cannot loop forever and run up API bills |
| **Acceptance Criteria** | A checklist of specific, testable conditions that must all be true before the agent (or a human) declares the task "done" | "The `/auth/callback` route returns HTTP 200" and "All existing tests still pass" |

---

## Getting a Coding Agent Running: Install, Configure, Run

Before comparing architectures, get one working. Ten minutes, one tool, one small task.

### Install one (not all)

```bash
# Pick ONE to start.
npm install -g @anthropic-ai/claude-code    # Claude Code
npm install -g opencode-ai                  # opencode
npm install -g @openai/codex                # Codex CLI
pip install aider-chat                      # Aider (Python)
```

Prefer not to install anything on your laptop? The **[Docker module](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-docker.md)** builds a `course-agent` image that carries the CLI, so your host stays clean and the agent's blast radius is one mounted folder.

### Configure: point it somewhere, tell it the rules

```bash
export ANTHROPIC_API_KEY="sk-ant-..."     # or OPENAI_API_KEY / GEMINI_API_KEY
# or route everything through the local gateway instead:
export ANTHROPIC_BASE_URL="http://localhost:4000"
```

Then write the project instruction file — `CLAUDE.md`, `AGENTS.md`, or `opencode.json` — with the test command and the off-limits paths. An agent that knows how to verify its own work is a different tool from one that does not.

### Run: the loop that actually works

```bash
cd ~/projects/mylang        # the working directory IS the agent's world
git status                  # start clean, so the diff at the end is only the agent's work
claude                      # or: opencode / codex / aider
```

Give it something small and checkable first:

> "Add a `--verbose` flag to `cli.py` that prints each token as it is scanned. Run `pytest -q` and make sure it still passes."

Then **read the diff**. Not the summary — the diff:

```bash
git diff                    # what actually changed
git add -p                  # stage it hunk by hunk, rejecting what you did not want
```

If the change is wrong, `git checkout -- .` costs you nothing. This is why we start every agent session from a clean git tree: it converts "did the agent break something?" from an act of faith into a two-second check.

You started a coding agent from your home directory instead of the project folder. What is the practical consequence?

[( )] Nothing — the agent asks before touching anything outside the project
[(X)] The agent's working context is your entire home directory: it may read files you never meant to share and propose edits far outside the project
[( )] The agent runs faster because it has more context available
[( )] The tool refuses to start outside a git repository

---

## Agents Talking to Agents: GitHub as the Message Bus

Here is the working pattern I use daily, and it is worth adopting early because it scales from one agent to a team of them without inventing any new infrastructure.

**Use GitHub as the coordination layer.** Issues, pull requests, and review comments are already a durable, threaded, permissioned, notification-driven message bus — and both humans and agents can read and write them.

| Artifact | What it carries | Who writes it |
|---|---|---|
| **Issue** | The task, its acceptance criteria, and the discussion of approach | You, or an agent that found the problem |
| **Branch + PR** | One agent's attempt at that task, as a reviewable diff | The coding agent |
| **PR review comment** | A specific, line-anchored instruction: "this misses the empty-input case" | You, or a *reviewing* agent |
| **PR checks (CI)** | The objective verdict — tests pass or they do not | The machine |
| **Merge** | Consensus: this attempt is accepted | You |

**Why this beats a chat window.** A conversation with an agent is ephemeral, unreviewable by teammates, and invisible to CI. The same exchange conducted through an issue and a PR is permanent, searchable a semester later, reviewable by your project team, and gated by tests. Your Project Thread team will thank you.

**The loop, concretely:**

```bash
# 1. The task becomes an issue (agents can read it by number)
gh issue create --title "Lexer drops trailing newline" \
  --body "Repro: echo 'x' | ./mylang. Expected NEWLINE token; got EOF. Acceptance: test added."

# 2. Point the agent at the issue
claude "Fix issue #42. Read it with 'gh issue view 42', write a failing test first, then fix it."

# 3. The agent opens a PR
gh pr create --fill

# 4. Review happens in the PR, not in the chat
gh pr diff 17
gh pr review 17 --comment -b "The fix works but the test only covers LF. Add a CRLF case."

# 5. A second agent can pick up that comment
claude "Read the review comments on PR 17 with 'gh pr view 17 --comments' and address them."
```

Step 5 is the interesting one: **the review comment is the inter-agent message.** One agent wrote code, a human (or another agent) critiqued it in a durable place, and a second agent consumed that critique without either of them sharing a context window. That is multi-agent communication built from tools you already have, with an audit trail as a side effect.

> **Watch out!** Give the agent a **scoped** token, not your personal one. A fine-grained GitHub token limited to one repository with issue and PR write access is enough for this entire loop. Never mount `~/.config/gh` into an agent container — that token can push to everything you can.

**Notes as the other half.** The same instinct applies to your own thinking: I keep an [Obsidian](https://obsidian.md) vault of plain Markdown notes and mount it into agent containers **read-only** (`-v "$HOME/notes/vault:/reference:ro"`), so agents can ground their answers in what I have already worked out without being able to corrupt it. Notes are the long-term memory; issues and PRs are the working memory; the container mount decides which the agent may write to. The **Obsidian Second Brain** and **Syncing Obsidian to GitHub** modules build this out.

---

## Model 1: A Comparison of Coding Agent Architectures

Three open or widely-used coding agents take meaningfully different architectural approaches to the same problem: how does an agent read a codebase, plan changes, and execute them safely?

Study the table below like you would compare three contractors before hiring one: focus on the Safety Model column, because that column determines how much damage a wrong decision can cause.

Think of these architectures the way you might think about three different contractors you could hire to renovate your kitchen. One starts work immediately with full access to your house. One writes a detailed blueprint you must approve before picking up a hammer. One can only use tools you have explicitly handed them. Each approach has real advantages and real risks.

| Agent | Architecture | How It Plans | File Access Method | How It Executes | Safety Model |
|---|---|---|---|---|---|
| **OpenCode** | Terminal-native; single LLM session with tool calls | Inline reasoning — the agent plans and acts in the same generation loop without separating these phases | Shell tools (`read_file`, `list_dir`, shell exec) called directly from the agent loop with no intermediary | Executes shell commands directly in the user's live environment, affecting real files immediately | Permission prompts before destructive operations; the `--dangerously-skip-permissions` flag disables all prompts and lets the agent act freely |
| **Plandex / pi.dev** | Plan-first; explicitly separates the planning phase from the execution phase | Generates a full *diff plan* as a structured, human-readable artifact before touching any file | Loads relevant file segments into context via semantic search — finds the most relevant code rather than reading everything | Applies the pre-approved plan as a batch operation; the user reviews the plan document before any file is changed | Human approval gate sits between plan and apply; no file is changed until the human clicks approve; changes are reversible until committed |
| **Hermes (tool-calling orchestrator)** | LLM acts as an orchestrator that selects and sequences registered function tools | Selects and sequences tool calls; each tool call is one discrete "action" the agent chooses | Registered filesystem tools (`read_file`, `write_file`) with defined JSON schemas that specify exactly what each tool can do | Tool functions run in the host process and return results to the LLM as observations it can reason about | Controlled entirely by which tools are registered; if a tool is not registered, that action is simply impossible |

### Critical Thinking Questions

1. OpenCode and Hermes both execute in the host environment, while Plandex adds a human approval gate between planning and execution. What does this gate cost in terms of speed and developer interruptions, and what does it buy in terms of safety? Describe a situation where you would prefer each of the three models.

   *Hint: Think about the tradeoff between a surgeon who pauses before each cut to ask permission versus one who follows a pre-approved surgical plan. When does each approach make more sense?*

2. In the table, "file access method" varies from raw shell commands to registered tool schemas. If the agent can run arbitrary shell commands, it can do *anything* — including deleting files or calling the network. If it can only call registered tools, it is limited to what the tools permit. Describe a specific attack or accident that shell access makes possible but registered-tool access prevents.

   *Hint: Consider what `rm -rf ~` does when run as a shell command, versus whether a `write_file` tool would allow that operation.*

3. Every agent above must load file content into its context window before reasoning about it. A typical codebase has millions of tokens, far more than any context window can hold. How does each agent decide *which* files to load? What happens if the agent loads the wrong files — files that seem relevant but are not — and then makes edits based on them?

   *Hint: If you asked a contractor to fix your plumbing but they studied the electrical blueprints by mistake, what kind of "fix" might result?*

---

## Model 2: The Coding Agent Loop

The agent loop for coding tasks is an instance of the general perceive-think-act cycle, specialized for a software development environment. Each stage produces artifacts the next stage depends on.

Think of the agent loop like a student working through a homework problem: they read the question (Perceive), make a plan (Plan), write an answer (Act), check it against the rubric (Verify), and either submit or revise. The key difference is that each revision costs money (API calls) and can make things worse if the agent misreads the rubric.

The table below traces a coding agent through its five stages. As you read each row, notice the Failure Mode column — these are not edge cases, they are the normal ways the loop goes wrong.

| Stage | What the Agent Does | Inputs | Outputs | Failure Mode |
|---|---|---|---|---|
| **1. Perceive** | Reads the repository: directory tree, relevant source files, open issues, and existing tests to build a picture of the current state | File system contents, git log history, and the task description provided by the user | A working context loaded into the LLM prompt — the agent's "understanding" of the codebase | Loads too many files, causing a context overflow where earlier information is forgotten; or loads the wrong files, leading to hallucinated edits targeting nonexistent functions |
| **2. Plan** | Identifies which files to change and what changes to make; may emit a structured, ordered plan the human can review | The loaded context combined with the task goal | An ordered list of file edits and shell commands, with rationale for each choice | Underestimates dependencies between files; plans changes at the wrong abstraction layer (e.g., editing generated code instead of the generator) |
| **3. Act** | Applies edits file by file and runs shell commands such as build, lint, and test | The plan combined with the current contents of the files to be changed | Modified files and the output of any shell commands that were run | An edit breaks unrelated functionality; a shell command has an irreversible side effect such as deleting a file or sending a network request |
| **4. Verify** | Reads test output, lint results, and compiler errors; decides whether the stated goal has been satisfied | Command output combined with the original acceptance criteria | A pass/fail judgment; a failure result triggers the agent to return to the Plan stage with failure context added | Interprets a passing test suite as "done" when the existing tests did not cover the new feature that was just added |
| **5. Commit or Loop** | If verified: commits with a descriptive message. If not verified: returns to Plan with the failure context appended | Output of the Verify stage | A git commit (success) or an updated plan (failure, triggers another loop iteration) | Infinite loop if Verify never passes; commit with broken code if the step budget runs out before verification succeeds |

### Critical Thinking Questions

4. The "Failure Mode" column shows that verification can be fooled by a test suite that does not cover the new feature. Whose responsibility is it to write acceptance criteria before the agent starts? What does this imply about the human's role even in a highly automated agentic workflow?

   *Hint: If you give a contractor "make my kitchen look nice" with no further specification, you cannot complain when the result is not what you pictured. What is the equivalent of a detailed architectural blueprint in agent development?*

5. Trace the loop for a concrete task: "rename function `calculate_total` to `compute_total` across all files in the project." Walk through each of the five stages. Which stages are essentially trivial for this task? Which stage is most likely to introduce a subtle bug, and why?

   *Hint: A function can be called from unexpected places — test files, configuration files, documentation strings, or even inside a string literal like `"calling calculate_total here"`. What happens if the agent misses one?*

6. The step budget (max iterations) is a safety parameter. If you set it too low, the agent stops before finishing. If you set it too high, a stuck agent runs up API costs and possibly makes cascading bad edits. How would you choose a budget for a medium-complexity task like "add pagination to the search results page"?

   *Hint: Estimate the number of distinct files that probably need to change, multiply by the number of verify-and-fix cycles you'd expect, and add a buffer. What information would you want to collect from past runs to refine this estimate?*

> **⚠️ Common Misconception:** Many students assume that a coding agent "understands" the codebase the way a senior developer does — holding a mental model of every function, every dependency, and every implicit assumption. It does not. The agent only knows what it has loaded into its context window during the current run. If a critical convention (like "never use raw SQL strings — always use the ORM") was established in a file the agent did not load, the agent will happily violate it. This is why human diff review remains essential even when the test suite passes: tests verify behavior, not design adherence.

In the coding agent loop, the *Verify* stage fails silently when:

[( )] The test runner crashes with an exception
[( )] The agent runs out of context window space
[(X)] The existing test suite passes but does not cover the new behavior the agent just added
[( )] The agent emits a "Final Answer" action before running tests

---

## Model 3: Scenario — "Add OAuth2 Login"

A student types: *"Add OAuth2 login with GitHub to this Flask app."* The coding agent begins its loop. Trace what happens at each stage.

Read the table below as a time-lapse of one real agent run. Pay special attention to the Commit step at the bottom — it contains the most common beginner surprise about how git staging works in an agentic context.

Reading this table top-to-bottom is like watching a time-lapse of the agent working. Notice that the agent hits a problem at the Verify stage (a test fails) and loops back to fix it — this is the normal, healthy behavior of the loop. Also notice Step "Act (shell)" at the bottom: `git add -A` stages *everything* in the working directory, including files the agent did not intentionally change.

| Step | Agent Action | Files Read | Files Written | Shell Commands Run |
|---|---|---|---|---|
| Perceive | Scans the repository tree to understand the project structure; finds `app.py`, `requirements.txt`, `templates/login.html`, and the existing `/login` route | `app.py`, `requirements.txt`, `templates/login.html` | *(none — this step only reads)* | `ls` (list directory), `git log --oneline -10` (see recent changes) |
| Plan | Identifies four changes needed: (1) add `authlib` dependency, (2) add GitHub OAuth config variables, (3) add `/auth/github` and `/auth/callback` routes, (4) update login template to link to the new OAuth flow | *(loaded context from Perceive step)* | *(plan is internal — not written to a file in this architecture)* | *(none — planning does not execute commands)* |
| Act (edit 1) | Appends `authlib` to `requirements.txt` so the dependency is declared | `requirements.txt` (reads current content) | `requirements.txt` (appends one line) | *(none)* |
| Act (edit 2) | Adds the OAuth config block (client ID, secret, redirect URL) and two new route functions to `app.py` | `app.py` (reads current content) | `app.py` (adds ~40 lines of code) | *(none)* |
| Act (shell) | Installs the new dependency and runs the full existing test suite to check for regressions | *(none)* | *(none — pip and pytest do not write project files)* | `pip install -r requirements.txt` (installs authlib), `pytest` (runs all tests) |
| Verify | Reads pytest output; 3 tests pass, 1 fails — the `/login` redirect test now expects a GitHub OAuth redirect URL but the old test expected a different URL | pytest output shown in the terminal | *(none)* | *(none)* |
| Loop — Replan | Updates the `/login` redirect test to match the new expected behavior (redirecting to GitHub OAuth); re-runs pytest to confirm all 4 tests now pass | `tests/test_routes.py` | `tests/test_routes.py` | `pytest` |
| Commit | All tests pass; stages all changed files and commits with a descriptive message | *(none)* | *(git commit record)* | `git add -A` (stages everything in the working directory), `git commit -m "Add GitHub OAuth2 login via authlib"` |

### Critical Thinking Questions

7. In the Commit step, the agent runs `git add -A`. This command stages *every modified and untracked file* in the working directory, not just the files the agent intentionally changed. What files could be accidentally staged if the working directory contained a `.env` file holding secrets like `GITHUB_CLIENT_SECRET=abc123`? What specific design choice in the agent or its environment would prevent this accident?

   *Hint: A `.gitignore` file tells git which files to never stage. Who is responsible for ensuring `.env` is listed there — the developer, the agent, or both?*

8. The agent modified `tests/test_routes.py` to make the failing test pass. This sounds reasonable, but describe a scenario where changing the test to match the implementation is actually the *wrong* decision. When does a failing test mean "fix the test" versus "fix the code"?

   *Hint: A test that asserts "the login page requires a password" is not wrong just because the new code skips the password check. What should the agent do when the failing test is documenting a requirement, not an outdated expectation?*

9. The agent's context window at the Verify stage contains the original task, the full plan, all edits made so far, and the pytest output. For a large codebase, information from the beginning of the session may have scrolled out of the context window by this point. What specific information from the Perceive stage might be lost, and how might that loss cause the agent to introduce a subtle bug in a later repair attempt?

   *Hint: Consider a case where the agent learned at the start that the project uses a custom session management library — but that fact has since scrolled out of the context window. What might go wrong when it tries to implement the OAuth callback?*

---

## Model 4: Loops That Run Themselves — Ralph, autoresearch, gnhf, and Crews

Model 2 traced *one* pass of the agent loop. But the loop's real power appears when you run it **over and over, unattended** — the agent finishes, a shell script starts it again, and it keeps going while you sleep. The surprising design choice that makes this work is that each iteration begins with a **fresh context window**. That sounds like amnesia, and it would be, except the agent's memory does not live in the conversation — it lives on **disk**: the codebase itself, a running `TODO` file, and the `git` history. Fresh context is a *feature*: it sidesteps the context-overflow failure mode from Model 2's Perceive stage, because the agent re-reads only what it needs each round instead of dragging a bloated, half-forgotten history behind it.

Think of it like a relay of identical runners who cannot talk to each other but share one notebook. Each runner reads the notebook, runs one leg, writes down what they did, and hands off. No runner remembers the race — the notebook does.

Study the Safety Model column below the way you did in Model 1: when the loop runs while you are asleep, that column is the only thing standing between you and a branch full of confident nonsense.

| Pattern | What it is | Memory between iterations | How it stops | Safety model |
|---|---|---|---|---|
| **Ralph loop** (Geoffrey Huntley) | A brute-force `while` loop that re-runs the *same prompt file* against the agent, iteration after iteration | The codebase, a `TODO` file, and `git` history — each iteration starts with a fresh context and re-reads them | A human stops it, or a "task complete" check written into the prompt trips | Deliberately minimal — relies entirely on the test suite plus the ability to `git revert` a bad iteration |
| **autoresearch** (Karpathy's variant) | The *same* loop pointed at ML research instead of code | Model checkpoints and metrics logs on disk | A target validation-loss or metric is reached | The success *metric* is the guardrail — you iterate on model quality, and a worse score is simply discarded |
| **gnhf** ("good night, have fun") | An overnight orchestrator that splits a goal into small steps, each run in a fresh context seeded with a base context plus prior learnings | Each successful step is a commit on a dedicated `gnhf/<slug>` branch | A step budget, or the goal's acceptance check, is met | Success ⇒ commit; failure ⇒ `git reset --hard` and exponential backoff; `git` worktrees isolate parallel agents; agent-agnostic (Claude Code, Codex, opencode, Copilot, pi, ACP targets) |
| **firstmate** (a "crew") | An agent *distro* — a portable directory of instructions, skills, tooling, policies, and state that turns one general agent into a coordinated crew | Shared distro state plus the repository | You end the primary session | "Talk to one agent, ship with a crew" — one primary session delegates to specialized sub-agents, each with a narrower, safer scope |

Notice what these share: they are the **Step Budget** and **Acceptance Criteria** from the Key Concepts table, scaled up. In an interactive session you are the stopping condition and the final judge. In an unattended loop you are asleep — so the *step budget* is the only thing preventing a runaway bill, and the *acceptance check* (usually the test suite) is the only thing preventing a tidy commit of broken code. Model 2's Verify stage is no longer one step among five; when the loop runs itself, **Verify is the whole game**.

### Critical Thinking Questions

10. A Ralph loop starts each iteration with an empty context window, yet it can complete a multi-day refactor no single session could hold. Explain where the agent's "memory" actually lives, and why re-reading it each iteration is *safer* than carrying the full history forward.

    *Hint: A single long session accumulates every file it ever read until the important early facts scroll out — the exact failure in Model 2's Perceive row. What does a runner who re-reads the shared notebook each leg avoid that a runner trying to remember the whole race does not?*

11. `gnhf` commits each successful step to a branch but runs `git reset --hard` after a failed one. Contrast this with a Ralph loop that edits files in place with no automatic rollback. For an overnight run on a codebase you care about, which safety model would you choose, and what property of your project (tests? review habits? branch protection?) does your choice depend on?

    *Hint: What does `git reset --hard` throw away, and what does it protect? If your test suite is thin, does per-step rollback still save you — or does it just tidily discard work while still letting a passing-but-wrong step through?*

12. `firstmate` turns one agent into a crew of specialized sub-agents. Using Model 1's "controlled entirely by which tools are registered" idea, explain how giving each crew member a *narrow* scope can make the whole crew safer than a single agent with every capability at once. Then name a coordination failure a crew introduces that a single agent does not have.

    *Hint: A sub-agent that can only edit tests cannot also `git push`. But now two sub-agents share one repository — what goes wrong if both edit the same file, or if one's idea of "done" contradicts another's?*

> **⚠️ Common Misconception:** Students often assume that "fresh context each iteration" means the agent forgets everything and cannot make real progress — that it must be flailing in circles. The opposite is true, *and it is the whole point*: the loop deliberately externalizes memory to the filesystem and `git` so that no single context window has to hold the entire task. The agent is not remembering less; it is remembering *on disk*, where memory is durable, inspectable, and does not decay as the window fills. The real risk is not amnesia — it is an unattended loop with a weak Verify stage happily committing work that passes thin tests but violates a requirement no test encodes.

Why does a Ralph loop start each iteration with a *fresh* context window instead of carrying the full conversation forward?

[( )] To reduce the number of API calls, since a fresh context uses fewer total tokens over the whole run
[( )] Because the model is legally required to discard prior context between runs
[(X)] Because the task's memory lives on disk (codebase, `TODO` file, `git` history), so each iteration can re-read exactly what it needs and avoid the context-overflow failure that plagues one very long session
[( )] Because a fresh context makes the agent more creative by preventing it from repeating earlier ideas

---

## The Cowork Paradigm: General Agents Beyond Code

Every architecture so far assumes the agent's world is a **codebase**. But the same loop — perceive, plan, act, verify — works just as well when the "files" are a spreadsheet, a slide deck, and a browser tab. That is a different paradigm, and it is worth naming the three explicitly (the *Agentic CLI Tools* activity develops this framing in full):

| Paradigm | The agent's world | Who it is for | Example tools |
|----------|-------------------|---------------|---------------|
| **Chat** | A conversation window; *you* run any action it suggests | Anyone | ChatGPT, Claude.ai, LM Studio |
| **Code** | A scoped project directory the agent reads, edits, and tests | Developers | Claude Code, opencode, Codex |
| **Cowork** | Your whole desktop — apps, documents, files | Non-developers and general knowledge work | **Claude Cowork**, **OpenWork** |

**Cowork** is the coding-agent loop pointed at general computer work: drafting and editing documents, filling spreadsheets, moving files, driving apps — for people who are not writing code at all. **Claude Cowork** is a desktop application built for exactly this; **OpenWork** is an open-source alternative that wraps the same **opencode** engine you configured earlier in this activity, which is a neat illustration that "code" and "cowork" are the same machinery aimed at different worlds. And `firstmate`'s "crew" idea generalizes cleanly here: a crew of general agents can research, draft, and cross-check a report the way a code crew builds a feature.

The paradigm shift raises the stakes on everything this module taught about review. A wrong diff in the code paradigm is caught by tests and reversed by `git`. A cowork agent editing the wrong document, emailing the wrong person, or deleting the wrong file has no test suite and often no undo. The human's judgment does not disappear as agents leave the codebase — it *moves*, from "review the diff" to "define the guardrails of a world that has no `git revert`."

**Question B.** In the code paradigm, `git` and the test suite give you a safety net: you can review a diff and roll back a bad change. When a cowork agent operates across your whole desktop, what plays the role of "the diff" and "the rollback" — and where does that leave the human's responsibility?

[[___ Your answer here ___]]

---

## Exercises

1. **Design an agent brief.**

   *What to do:* Write a 3–5 sentence task description for a coding agent that is specific enough to be verifiable. Then write an acceptance criteria checklist of at least 4 items the agent's Verify stage could use to determine "done." Trade your brief with another team and critique their criteria for testability.

   *Starter hint:* A good task description names the framework, the specific feature, and the expected behavior. For example: "This is a Flask app using SQLAlchemy for the database. Add a password-reset-by-email feature. Users should be able to request a reset link on `/forgot-password`, click the link in email, and set a new password on `/reset-password/<token>`."

   A good acceptance criterion is specific and binary: it is either true or false. Compare:
   - Vague: "The password reset works correctly." (How would a test know?)
   - Testable: "GET `/forgot-password` returns HTTP 200 and renders a form with an email input field."

   *You've succeeded when* your acceptance criteria checklist could be given directly to a test runner (or another student) who has never seen your task description and they could verify each item independently.

2. **Trust boundary audit.**

   *What to do:* For the OAuth2 scenario in Model 3, list every external service or system the agent contacted during its run. For each, write one sentence describing what goes wrong if that service is compromised or returns incorrect data during the agent's session.

   *Starter hint:* Start by listing the shell commands that ran. Each command that touches something outside the local files is a trust boundary crossing:
   ```bash
   pip install -r requirements.txt  # contacts PyPI (the Python package registry)
   pytest                            # runs local code, but that code may make network requests
   git add -A && git commit          # writes to the local git history (no network, but irreversible)
   ```
   For each, ask: "What if this returned a malicious or incorrect response?"

   *You've succeeded when* you have a table with at least 4 external services, a specific failure mode for each, and at least one mitigation for the most dangerous failure.

3. **Diff review exercise.**

   *What to do:* Your instructor will display a git diff from an actual coding agent session. As a team, identify: (a) one change that is clearly correct and requires no further review, (b) one change that requires domain knowledge to evaluate and cannot be verified by reading code alone, and (c) one change you would reject and why. The Presenter explains the team's reasoning.

   *Starter hint:* When reading a diff, lines beginning with `+` were added and lines beginning with `-` were removed. Context lines (no prefix) show surrounding code that was not changed. Look for: added imports that were not needed, deleted lines that might have been load-bearing, and test changes that reduce coverage rather than add it.

   *You've succeeded when* your Presenter can explain the team's rejection reasoning in terms of a specific risk — not just "it looks wrong" but "if this change ships, then X could happen."

4. **Design an overnight brief.**

   *What to do:* Write a brief you would hand a `gnhf`-style self-running loop to work on while you sleep. It must contain three things: (a) a goal small and concrete enough to be verifiable, (b) an acceptance-criteria checklist the loop's Verify stage can check on its own (reuse the testable-vs-vague discipline from Exercise 1), and (c) an explicit **stop condition** — a step budget *and* the check that means "done." Then write one sentence naming the worst thing that could land in the morning's branch if your acceptance criteria are too weak.

   *Starter hint:* A good overnight goal is bounded and testable, e.g. "Add input validation to every route in `api/`, so that a missing required field returns HTTP 400 with a JSON error body." A weak acceptance criterion ("validation works") lets a loop commit code that passes because no test exercises the missing-field case — exactly the silent-Verify failure from Model 2. Pair every criterion with a test the loop can actually run:
   ```text
   Goal: add missing-field validation to all routes in api/
   Acceptance:
     - POST /users with no "email" returns HTTP 400  (test: test_users_missing_email)
     - every existing test in tests/ still passes
   Stop when: all acceptance tests pass, OR 30 iterations reached
   ```

   *You've succeeded when* another team could hand your brief to an unattended loop and know, without asking you, both when it should stop and how it would decide it succeeded — and you can name the failure a weak criterion would let through.

---

## Configuring OpenCode with Plugins and Project Instructions

OpenCode is configurable at two scopes: **project scope** (a file in your repository that everyone on the team shares) and **global scope** (a file in your home directory that applies to all your projects). Understanding which configuration belongs where is the same discipline as deciding which secrets belong in environment variables versus which belong in version control — the wrong choice exposes either too much or too little.

---

### The opencode.json Schema

OpenCode reads its configuration from `opencode.json`. Place this file at:

- **Project root** (`./opencode.json`) for settings that all contributors to this repository should share — things like the project's test command, architectural invariants, and which files the agent should never touch.
- **`~/.opencode/opencode.json`** for settings that are personal to you — your preferred model, your global instructions, your authentication tokens.

The file follows a published schema, which means your editor can validate it in real time:

The following JSON shows the minimal `opencode.json` schema declaration. This single line tells your editor to validate the file against the published schema, catching typos in configuration keys before they cause unexpected agent behavior.

```json
{
  "$schema": "https://opencode.ai/config.json"
}
```

---

### The Superpowers Plugin

OpenCode supports plugins that extend its built-in skill set. The Superpowers plugin adds pre-built skills for common agent development workflows — design-then-TDD, security audit, and structured refactor — so you do not have to write these prompts from scratch. Add it with a single line:

Adding the Superpowers plugin requires only one new field in your config. The `git+https://` prefix tells OpenCode to fetch the plugin source directly from GitHub at install time.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [
    "superpowers@git+https://github.com/obra/superpowers.git"
  ]
}
```

The `plugin` field accepts an array of plugin specifiers. The `git+https://` prefix tells OpenCode to fetch the plugin from a GitHub repository at install time, the same way `npm install` handles git URLs. Once the plugin is installed, OpenCode exposes its skills alongside the built-in ones.

**What Superpowers adds:**

- **Design + TDD skill**: generates a test suite against an interface *before* writing the implementation, enforcing the red-green-refactor cycle at the agent level.
- **Security audit skill**: scans a file or module for common vulnerability patterns (hardcoded secrets, unsafe deserialization, injection-prone string formatting) and produces a structured findings report.
- **Refactor skill**: restructures code to a specified pattern (e.g., extract a function, flatten nested conditionals) while guaranteeing that all existing tests still pass before and after the change.

---

### Project Instructions: opencode.json vs. AGENTS.md

OpenCode reads project-level instructions from two places. You can use either or both:

The `instructions` field embeds project-level rules directly in `opencode.json`. Use it for short, machine-readable invariants; use `AGENTS.md` for longer human-readable documentation.

**The `instructions` field in `opencode.json`:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [
    "superpowers@git+https://github.com/obra/superpowers.git"
  ],
  "instructions": "This project uses pytest for all tests. Run `pytest -v` to verify. Never modify files in the `generated/` directory — they are auto-generated by the build step and will be overwritten. The database schema is in `models.py`; do not alter it without a migration."
}
```

An `AGENTS.md` file at the repository root is the preferred place for longer project instructions — it reads like a document for humans while also being parsed by the agent at startup.

**An `AGENTS.md` file at the repository root** (preferred for longer instructions, because it is readable as a document without parsing JSON):

```markdown
# Agent Instructions

## Architecture
This is a Flask application with a SQLAlchemy ORM layer. The agent loop
is in `agent.py`; the tool registry is in `tools/`. Do not add business
logic to `app.py` — it is a thin routing layer only.

## Invariants
- All database access must go through the ORM in `models.py`. Never write raw SQL strings.
- The public API (routes in `app.py`) is versioned. Do not change existing route signatures.

## Test Commands
- Run all tests: `pytest -v`
- Run with coverage: `pytest --cov=. --cov-report=term-missing`
- Lint: `ruff check . && black --check .`

## Do NOT Modify
- `generated/` — auto-generated by `make generate`
- `migrations/` — managed by Alembic; create new migrations with `flask db migrate`
```

**What to put in project instructions:**

- The architecture overview: what each top-level module does and how they connect
- Invariants: rules the codebase enforces that are not visible in tests (e.g., "never use raw SQL," "all API responses must be JSON")
- The exact commands to run tests, linters, and builds — the agent uses these in its Verify stage
- An explicit list of files or directories the agent should never modify

**What NOT to put in project instructions:**

- API tokens, passwords, or any secrets — these belong in environment variables
- Personal preferences (your editor, your color scheme) — these belong in global config
- Instructions that are only relevant to one contributor — these belong in that person's global `~/.opencode/` config

---

### Critical Thinking Questions

**Question A.** Why would you commit `opencode.json` to version control but NOT your global `~/.opencode/instructions.md`?

[[___ Your answer here ___]]

*Hint: Think about what each file contains and who should be affected by it. The project `opencode.json` describes invariants and conventions of the codebase that every contributor and every agent session working on this repository should respect. The global `~/.opencode/instructions.md` describes your personal preferences — things like your preferred coding style, your typical workflow, or notes about your development machine — that are irrelevant or even wrong for other contributors. What happens if you commit your personal instructions and a teammate with different preferences pulls them? What happens if the project instructions are not committed and a new contributor's agent session does not know the invariants?*

Two instructions are being considered for `opencode.json` in a project's repository. Which instruction belongs in **project scope** (committed to the repository) rather than in a developer's personal global config?

[( )] "Use Black for formatting" — this belongs in project scope because formatting consistency matters to all contributors, not just one developer's personal taste
[(X)] "Do not modify the database schema in `models.py` without creating an Alembic migration first" — this is a project-specific invariant that all contributors and all agent sessions must respect
[( )] "My preferred model is llama3.2 at temperature 0.2" — this is a project-wide default that should be committed so all contributors use the same model for reproducibility
[( )] "Open files in VSCode rather than the terminal editor" — this should be in project scope to enforce a consistent editing environment across the team

---

## Reflection Prompt

*Personal:* Coding agents blur the line between "tool I use" and "colleague I supervise." Think about a task in your own coding experience where you wish you could have handed off the implementation to someone else while staying in charge of the design. At what point in the process would you have wanted to reclaim control?

*Technical:* Based on today's models, at which stage of the agent loop do you most want human oversight, and at which stage would you be comfortable letting the agent run unsupervised? What specific signals or artifacts from the agent would increase your confidence enough to expand its autonomy? What would need to be true about the agent's track record?

*Societal:* If coding agents can implement features from a plain-English description, what happens to entry-level software engineering jobs that are currently filled by people writing exactly that kind of code? Is this similar to or different from previous waves of automation in programming (compilers, IDEs, code generators)? What new skills become more valuable when implementation is cheap?

> *Hint:* Consider the history of compilers (which eliminated assembly programmers), high-level languages (which eliminated much manual memory management), and IDEs with autocomplete (which changed how code is written). What new roles emerged after each of those transitions?

---

→ Coming Up Next: We will zoom in on one of the most consequential actions a coding agent can take — writing to and reading from the filesystem. The next activity examines how to constrain that access so that a mistake stays recoverable.

---

## Further Reading

- Shunyu Yao et al. "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR* (2023). The reasoning pattern underlying most coding agents.
- Plandex documentation: https://docs.plandex.ai — especially the "plans" concept and diff review workflow.
- OpenCode GitHub repository: https://github.com/sst/opencode — read the README for architecture decisions and the `--dangerously-skip-permissions` flag discussion.
- Lilian Weng. "LLM Powered Autonomous Agents." *Lil'Log* (2023). https://lilianweng.github.io/posts/2023-06-23-agent/ — comprehensive survey of agent architectures including coding agents.
- Geoffrey Huntley. "everything is a ralph loop." https://ghuntley.com/loop/ — the origin and rationale of the fresh-context brute-force loop; see also https://ralph-wiggum.ai/.
- **gnhf** ("good night, have fun") — overnight autonomous orchestrator: https://github.com/kunchenguid/gnhf.
- **firstmate** — an agent distro for running a crew: https://github.com/kunchenguid/firstmate.
- **OpenWork** — the open-source, opencode-powered alternative to Claude Cowork: https://github.com/different-ai/openwork.
