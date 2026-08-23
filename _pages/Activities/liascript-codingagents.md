<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-codingagents.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-codingagents.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Coding Agents: OpenCode, Spec-First Development, and Reading the Diff

In *Your AI Workbench* you installed **opencode**, pointed it at the model on your own machine, and gave it one small job: add a docstring, change one line. You read the diff, approved it, and it worked. Today we turn that ten-minute demonstration into a working practice.

A **coding agent** is not a smarter autocomplete. When an editor suggests the next line, it reads your cursor position and offers a completion you accept or reject. A coding agent reads your repository, takes a goal ("add OAuth2 login"), decomposes it into file-level tasks, edits several files, runs your test suite, interprets the failures, and iterates until the goal is met or its budget runs out. The difference is agency: a persistent goal, world-affecting actions, and a loop that continues until done. It is the same perceive-plan-act loop you built by hand in *The Agent Loop*, with your file system as the world.

That changes where your judgment goes. You are no longer reviewing keystrokes. You are reviewing a **plan** before the agent acts and a **diff** before you keep it, and the quality of your work now depends on three skills that have nothing to do with typing code: **writing a specification precise enough to be checked**, **reading a plan and rejecting it while rejection is still cheap**, and **reading a diff adversarially**. Those are the three skills today builds, in that order, because that is the order in which they save you time.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Read each model carefully as a team, then answer the Critical Thinking Questions individually before discussing. The Recorder compiles the team's consensus answers; the Presenter will share at least one point of disagreement with the class. After class, complete the Reflection Prompt in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Coding Agent** | An AI system that reads a codebase, makes a plan, edits files, runs commands, and loops until a programming goal is met, without you steering each step | An agent that adds GitHub login to a Flask app by editing five files and running tests on its own |
| **Agent Loop** | The repeated cycle of Perceive -> Plan -> Act -> Verify that an agent runs until its goal is achieved or its budget runs out. The same loop you wrote by hand in *The Agent Loop*, with your repository as the world | The agent reading test output (Verify) and going back to fix the code (Plan -> Act) when a test fails |
| **Context Window** | The fixed-size "working memory" an LLM can read at one time; older information scrolls out as new information is added | A large codebase has millions of tokens; the agent must choose which files to load and which to skip |
| **Diff / Patch** | A file showing exactly which lines were removed (marked −) and which were added (marked +) when a file is changed | The agent's changes to `app.py` shown as a diff before you decide whether to merge them |
| **Step Budget** | A maximum number of actions or loop iterations the agent is allowed to take before it must stop, preventing runaway cost | Setting `MAX_ITERATIONS = 25` so a stuck agent cannot loop forever and run up API bills |
| **Acceptance Criteria** | A checklist of specific, testable conditions that must all be true before the agent (or a human) declares the task "done" | "The `/auth/callback` route returns HTTP 200" and "All existing tests still pass" |
| **Specification-First Development** | Writing a plain-English spec, then its acceptance criteria, then a failing test per criterion, all *before* any implementation exists, so there is an objective standard the code must meet | Model 2: writing five `pytest` cases for `search_memory` and watching them fail before the agent writes a line |
| **Test-Driven Development (TDD)** | The discipline of defining every new behavior with a failing test first, writing the least code that makes it pass, then cleaning up. **Red -> green -> refactor** | `pytest` showing five `FAILED` lines (red), then the agent's implementation turning them `PASSED` (green) |
| **Supervision Level** | How closely you watch: **autocomplete** (every token), **pair** (every changed line), or **vibe** (only the diff and the test results). Chosen to match the task's stakes, not your mood | Section 3: choosing "pair" for a security-sensitive module and "vibe" for well-tested utility code |
| **Diff Review** | Reading the exact lines an agent added and removed, rather than reading the finished file, so you see what it *changed* instead of what it left alone | Model 3: spotting `eval(query)` in an implementation that passes every test |
| **Plan** | A written statement of what the agent intends to do, produced *before* it touches anything: the files it will change, the order, and why. The cheapest artifact to reject | Section 2b: rejecting a four-file plan in ten seconds instead of reviewing a four-file diff in ten minutes |
| **Thinking / reasoning trace** | The agent's written-out deliberation before it commits to an action. Text you can read, not a window into the model's mind | The `Thought:` lines from *The Agent Loop*, now produced by a tool you did not write |
| **Observability, isolation, reversibility** | The three properties that make delegating safe: can I see what it did, can I bound what it reaches, can I undo it. Named in *Your AI Workbench*, Step 8.5 | The plan and the diff, the container mount, and `git checkout .` |

---

### Before You Start

**You should already have** opencode installed and configured from *Your AI Workbench* (Step 8), a `cs357-work` repository, and Ollama running. Check with:

```bash
opencode --version
git -C ~/cs357-work status
```

**If any of that is missing,** Section 1 below is the two-minute recovery path; do it now rather than during the models.

**What you will have at the end:** a specification with executable acceptance criteria, an agent-written implementation of it, and a documented review of a diff in which you found three real problems.

---

## How Today Runs

Today has three parts and a going-deeper section you take home.

| | What you do | Roughly |
|---|---|---|
| **Part I** | Get your agent driving again, and learn the pattern that lets agents hand work to each other through GitHub instead of a chat window | 25 min |
| **Part II** | Write a specification and its failing tests *before* any code exists, review the agent's **plan** before it acts, then let it implement against them | 25 min |
| **Part III** | Read a diff that passes every test and is still dangerous | 20 min |
| **Part IV** | Exercises and reflection | take-home |
| **Part V** | Going further: architecture comparison, a full worked scenario, unattended loops, cowork agents, and the full opencode configuration reference | self-paced |

Part V is real material, not filler; it is where you go when a lab direction or your project needs it. Nothing in it is assumed by Parts I through IV.

---

# Part I: Driving the Agent

In this part you get your agent running against a real repository, and then learn the pattern that turns "me and my agent in a chat window" into something a team, and other agents, can participate in.


## 1. Recap and Recovery: Install, Configure, Run

You did this in *Your AI Workbench*, Step 8. This section exists so a broken setup costs you two minutes rather than the session. Run the check; if it passes, skip to *The habits that make this work*, which is the part that is new.

```bash
opencode --version
git -C ~/cs357-work status
curl -s http://localhost:11434/api/tags | head -c 80
```

**If `opencode` is missing**, reinstall and put it on your `PATH`:

```bash
curl -fsSL https://opencode.ai/install | bash
export PATH="$HOME/.local/bin:$PATH"
```

**If it starts but finds no model**, the config did not survive. Rewrite it:

```bash
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/config.json <<'JSON'
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://host.docker.internal:11434/v1" },
      "models": { "llama3.2": { "name": "llama3.2" } }
    }
  }
}
JSON
```

Outside the container, use `http://localhost:11434/v1`. **No API key anywhere**: everything today runs against the model on your own machine, which is why this session costs nothing and works offline. (If you are routing through OpenWebUI rather than straight to Ollama, that variant does take a key, your own, from your own server; Step 8.2 of the [Development Environment tutorial](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-devenvironment.md) shows the config and explains why it is still free.)

> **Other tools in this family** (Claude Code, Codex CLI, Gemini CLI, Aider, pi) install differently and mostly want a provider key. The going-further tutorial on agentic CLIs compares them. Today we all drive the same one so that when something breaks, the person next to you can help.

### The habits that make this work

Three, and they matter more than the tool:

```bash
cd ~/cs357-work        # the working directory IS the agent's world
git status             # start clean, so the diff at the end is only the agent's work
opencode
```

**Start from a clean tree.** This is what converts "did the agent break something?" from an act of faith into a two-second check.

**Give it something small and checkable first.** Not "improve my code." Something with a done condition you could verify yourself:

> "Add a `--verbose` flag to `hello_agent.py` that prints the full request body before sending it. Do not change anything else."

**Read the diff, not the summary.** The agent's prose describes what it believes it changed. `git diff` shows what it changed. Those are different documents.

```bash
git diff               # what actually changed
git add -p             # stage it hunk by hunk, rejecting what you did not want
```

If the change is wrong, `git checkout -- .` costs you nothing, which is the whole reason for the clean tree.

You started a coding agent from your home directory instead of the project folder. What is the practical consequence?

[( )] Nothing; the agent asks before touching anything outside the project
[(X)] The agent's working context is your entire home directory: it may read files you never meant to share and propose edits far outside the project
[( )] The agent runs faster because it has more context available
[( )] The tool refuses to start outside a git repository

---

## 2. Agents Talking to Agents: GitHub as the Message Bus

Here is the working pattern I use daily, and it is worth adopting early because it scales from one agent to a team of them without inventing any new infrastructure.

**Use GitHub as the coordination layer.** Issues, pull requests, and review comments are already a durable, threaded, permissioned, notification-driven message bus, and both humans and agents can read and write them.

| Artifact | What it carries | Who writes it |
|---|---|---|
| **Issue** | The task, its acceptance criteria, and the discussion of approach | You, or an agent that found the problem |
| **Branch + PR** | One agent's attempt at that task, as a reviewable diff | The coding agent |
| **PR review comment** | A specific, line-anchored instruction: "this misses the empty-input case" | You, or a *reviewing* agent |
| **PR checks (CI)** | The objective verdict: tests pass or they do not | The machine |
| **Merge** | Consensus: this attempt is accepted | You |

**Why this beats a chat window.** A conversation with an agent is ephemeral, unreviewable by teammates, and invisible to CI. The same exchange conducted through an issue and a PR is permanent, searchable a semester later, reviewable by your project team, and gated by tests. Your Project Thread team will thank you.

**The loop, concretely:**

```bash
# 1. The task becomes an issue (agents can read it by number)
gh issue create --title "Agent loop ignores the step budget on a malformed action" \
  --body "Repro: give agent.py a goal that makes the model emit calc( with no closing paren.
Expected: the parse fails, the step counter still increments, the budget stops it.
Actual: the regex misses, nothing is appended to memory, and it spins until killed.
Acceptance: a test asserting the loop exits at max_steps on unparseable output."

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

> **Watch out!** Give the agent a **scoped** token, not your personal one. A fine-grained GitHub token limited to one repository with issue and PR write access is enough for this entire loop. Never mount `~/.config/gh` into an agent container; that token can push to everything you can.

**Notes as the other half.** The same instinct applies to your own thinking: I keep an [Obsidian](https://obsidian.md) vault of plain Markdown notes and mount it into agent containers **read-only** (`-v "$HOME/notes/vault:/reference:ro"`), so agents can ground their answers in what I have already worked out without being able to corrupt it. Notes are the long-term memory; issues and PRs are the working memory; the container mount decides which the agent may write to. The **Obsidian Second Brain** and **Syncing Obsidian to GitHub** modules build this out.

---

## 2b. Read the Plan Before You Read the Diff

The review discipline in Part III is about the diff, and by then the work is done. There is a cheaper place to catch a mistake, and every serious coding agent gives it to you: **the plan**.

Before an agent edits anything, it can be made to write down what it intends to do. Which files, in what order, and why. That artifact costs one screen to read and is free to reject. A diff costs ten minutes to review and, if you reject it, the agent's work is thrown away and yours was too.

| | Plan review | Diff review |
|---|---|---|
| **What you are reading** | Intent: files, order, rationale | Consequence: exact lines added and removed |
| **Catches** | Wrong file, wrong layer, missing dependency, scope creep, a misunderstanding of the goal | Security holes, hidden assumptions, resource problems, spec drift |
| **Cost to reject** | Seconds. Nothing has happened yet | The agent's whole run, and your review time |
| **Cannot catch** | Anything about the code that does not exist yet | A plan that was wrong in a way the code faithfully implemented |

Neither replaces the other. The plan catches "you are about to edit the generated file instead of the generator"; only the diff catches `eval(query)`.

### Getting a plan out of your agent

Every tool in this family exposes some version of it, and the labels differ more than the idea does. **Claude Code** has an explicit plan mode you cycle to with Shift+Tab. **opencode** offers a plan-style review before it applies a change. **Plandex** is built around the separation: it emits a full diff plan as a reviewable document, and no file changes until you approve it. **pi** deliberately has none of this, which is exactly why the course reserves it for throwaway work.

If your tool has no mode for it, ask for one in words. This works everywhere:

```text
Before you change anything: list the files you intend to modify, in the order you
will touch them, with one sentence each on why. Then stop and wait. Do not edit.
```

### The trace, and what it is not

Many agents also show you their **thinking**: the deliberation they write out before choosing an action. Read it. It is genuinely useful, and it is the same `Thought:` line you built by hand in *The Agent Loop*, produced by a tool you did not write.

Read it for what it is, though. The trace is *text the model generated because we asked it to*, not a recording of a hidden reasoning process. It can be perfectly coherent and describe a step the agent then does not take. It can rationalize an action rather than explain it. Treat it as the agent's stated intent, useful for spotting a misunderstanding early and worthless as proof that the code is right. That is why you still read the diff.

Your agent's plan says it will modify `parser.py`, `parser_test.py`, and `build/generated_tokens.py`. You know `build/` is regenerated by a script on every build. What is the correct response, and at what cost?

[( )] Approve the plan; the generated file will be overwritten anyway, so it is harmless
[(X)] Reject the plan now and say the token list is generated from `tokens.yaml`. Cost: about fifteen seconds
[( )] Approve it, review the diff, and revert the `build/` hunk afterwards
[( )] Approve it and add `build/` to `.gitignore` so the change stops showing up

    --{{0}}--
The third option gets to the same end state and pays for it with a full agent run and a full diff review. The fourth hides the symptom and leaves the agent believing the generated file is where token definitions live, so it will do the same thing next time. Rejecting at the plan stage is cheaper than both, and it corrects the agent's model of the project rather than the file.

---

## Model 1: The Coding Agent Loop

The agent loop for coding tasks is an instance of the general perceive-think-act cycle, specialized for a software development environment. Each stage produces artifacts the next stage depends on.

Think of the agent loop like a student working through a homework problem: they read the question (Perceive), make a plan (Plan), write an answer (Act), check it against the rubric (Verify), and either submit or revise. The key difference is that each revision costs money (API calls) and can make things worse if the agent misreads the rubric.

The table below traces a coding agent through its five stages. As you read each row, notice the Failure Mode column; these are not edge cases, they are the normal ways the loop goes wrong.

| Stage | What the Agent Does | Inputs | Outputs | Failure Mode |
|---|---|---|---|---|
| **1. Perceive** | Reads the repository: directory tree, relevant source files, open issues, and existing tests to build a picture of the current state | File system contents, git log history, and the task description provided by the user | A working context loaded into the LLM prompt, the agent's "understanding" of the codebase | Loads too many files, causing a context overflow where earlier information is forgotten; or loads the wrong files, leading to hallucinated edits targeting nonexistent functions |
| **2. Plan** | Identifies which files to change and what changes to make; may emit a structured, ordered plan the human can review | The loaded context combined with the task goal | An ordered list of file edits and shell commands, with rationale for each choice | Underestimates dependencies between files; plans changes at the wrong abstraction layer (e.g., editing generated code instead of the generator) |
| **3. Act** | Applies edits file by file and runs shell commands such as build, lint, and test | The plan combined with the current contents of the files to be changed | Modified files and the output of any shell commands that were run | An edit breaks unrelated functionality; a shell command has an irreversible side effect such as deleting a file or sending a network request |
| **4. Verify** | Reads test output, lint results, and compiler errors; decides whether the stated goal has been satisfied | Command output combined with the original acceptance criteria | A pass/fail judgment; a failure result triggers the agent to return to the Plan stage with failure context added | Interprets a passing test suite as "done" when the existing tests did not cover the new feature that was just added |
| **5. Commit or Loop** | If verified: commits with a descriptive message. If not verified: returns to Plan with the failure context appended | Output of the Verify stage | A git commit (success) or an updated plan (failure, triggers another loop iteration) | Infinite loop if Verify never passes; commit with broken code if the step budget runs out before verification succeeds |

### Critical Thinking Questions

1. The "Failure Mode" column shows that verification can be fooled by a test suite that does not cover the new feature. Whose responsibility is it to write acceptance criteria before the agent starts? What does this imply about the human's role even in a highly automated agentic workflow?

   *Hint: If you give a contractor "make my kitchen look nice" with no further specification, you cannot complain when the result is not what you pictured. What is the equivalent of a detailed architectural blueprint in agent development?*

2. Trace the loop for a concrete task: "rename function `calculate_total` to `compute_total` across all files in the project." Walk through each of the five stages. Which stages are essentially trivial for this task? Which stage is most likely to introduce a subtle bug, and why?

   *Hint: A function can be called from unexpected places: test files, configuration files, documentation strings, or even inside a string literal like `"calling calculate_total here"`. What happens if the agent misses one?*

3. The step budget (max iterations) is a safety parameter. If you set it too low, the agent stops before finishing. If you set it too high, a stuck agent runs up API costs and possibly makes cascading bad edits. How would you choose a budget for a medium-complexity task like "add pagination to the search results page"?

   *Hint: Estimate the number of distinct files that probably need to change, multiply by the number of verify-and-fix cycles you'd expect, and add a buffer. What information would you want to collect from past runs to refine this estimate?*

> **Common Misconception:** Many students assume that a coding agent "understands" the codebase the way a senior developer does, holding a mental model of every function, every dependency, and every implicit assumption. It does not. The agent only knows what it has loaded into its context window during the current run. If a critical convention (like "never use raw SQL strings; always use the ORM") was established in a file the agent did not load, the agent will happily violate it. This is why human diff review remains essential even when the test suite passes: tests verify behavior, not design adherence.

In the coding agent loop, the *Verify* stage fails silently when:

[( )] The test runner crashes with an exception
[( )] The agent runs out of context window space
[(X)] The existing test suite passes but does not cover the new behavior the agent just added
[( )] The agent emits a "Final Answer" action before running tests

---

# Part II: You Own the Spec, the Agent Owns the Code

In this part you practice the division of labor that makes coding agents useful instead of merely fast. The core observation, which Andrej Karpathy has articulated as clearly as anyone: **humans are better at writing specifications than at reviewing arbitrary code, and models are better at writing code than at writing specifications.** So you write the spec. The agent writes the code. The diff is the handoff.

## 3. Three Supervision Levels

Handing an agent a task without deciding how closely you will watch is like handing a contractor your house keys and leaving for a month: possibly fine, possibly catastrophic, depending entirely on how well you specified the job.

The three levels sit on a continuum, and the right choice depends on the stakes, the clarity of the spec, and how much you trust the existing tests.

| Supervision Level | Description | Appropriate For | Risk Level | What the Human Reviews |
|-------------------|-------------|-----------------|------------|------------------------|
| **Autocomplete** | Agent suggests the next token, line, or block; you accept or reject inline | Boilerplate, well-understood APIs, single-function completions | Low | Every token as it is accepted |
| **Pair** | You describe a task; the agent produces a full file or function; you read every line before accepting | New features in production code, security-sensitive modules | Medium | Every changed file, every line |
| **Vibe** | You write a spec and tests; the agent implements the whole feature; you review only the diff | Well-tested utility code, prototypes, features with complete acceptance criteria | High without tests, medium with them | The diff against the spec, and the test results |

One column is missing from that table on purpose, and Section 2b supplied it: **at every level, you can also review the plan before the agent acts.** Plan review is not a fourth supervision level; it is a discount available at all three. It is what makes the third row survivable on a task where the tests are thinner than you would like.

Notice what the third row actually requires. "Vibe" is only the low-risk option **when the tests exist first.** Without them it is not a supervision level at all; it is hoping. Your Week 1 session was closest to "pair": you read every line of a three-line change. Today we earn our way to the third row by building the thing that makes it safe.

Which supervision level is appropriate for adding a password-hashing function to a production login system, given that the module has no existing tests?

[( )] Vibe, because password hashing is a well-known problem with standard solutions
[(X)] Pair, because the stakes are high and there is no test suite to catch an incorrect implementation
[( )] Autocomplete, because security code should be typed by hand one token at a time
[( )] Any of them; supervision level is a matter of personal preference

---

## 4. Writing the Spec Before the Code

The worst outcome in agent-assisted development is code that passes all your tests and does not do what you wanted, because your tests were incomplete. Specification-first development is the discipline that prevents it: write down what the code must do, in plain English, before you write a single test. The tests then operationalize the spec, and the agent's code is measured against the tests.

Writing the tests first forces you to confront every ambiguity in the spec *before* an implementation is sitting there to distract you.

**Three artifacts, in this order:**

1. A one-paragraph natural-language spec: the what and the why, not the how.
2. A list of acceptance criteria: specific, testable statements of the form "given X, the function must do Y."
3. One failing test per acceptance criterion: executable `pytest` that fails **before any implementation exists**. This is the **red** phase.

---

## Model 2: The `search_memory` Spec

**Natural-language spec:** `search_memory(query, k)` takes a user query string and a positive integer `k`, searches an in-memory list of text documents by cosine similarity of their embeddings, and returns the `k` most relevant documents as a list of strings. It must reject invalid inputs gracefully and must never return more than `k` results. It must raise a clear error rather than silently failing.

**Acceptance criteria:**

| # | Criterion |
|---|-----------|
| AC-1 | Given a query and `k=2`, the function returns exactly 2 strings. |
| AC-2 | The returned strings are drawn from the corpus; no invented text is returned. |
| AC-3 | Given `k` larger than the corpus size, the function raises `ValueError`. |
| AC-4 | Given an empty string query, the function raises `ValueError`. |
| AC-5 | Given `k=0`, the function raises `ValueError`. |

**Failing tests (the red phase):**

```python
import pytest

CORPUS = [
    "The Myrin Library closes at midnight on weekdays.",
    "First-year students may not bring vehicles to campus.",
    "Wismer Center serves continuous dining from 7am to 8pm.",
    "All students must complete a writing seminar in their first year.",
    "The Bakes Center is open to all students with a valid ID.",
]

def search_memory(query, k):
    raise NotImplementedError  # the agent will replace this

def test_returns_k_results():
    results = search_memory("library hours", k=2)
    assert len(results) == 2

def test_results_are_from_corpus():
    results = search_memory("library hours", k=2)
    for r in results:
        assert r in CORPUS

def test_k_exceeds_corpus_raises():
    with pytest.raises(ValueError):
        search_memory("dining", k=100)

def test_empty_query_raises():
    with pytest.raises(ValueError):
        search_memory("", k=2)

def test_k_zero_raises():
    with pytest.raises(ValueError):
        search_memory("library", k=0)
```

Running `pytest` on this file before any implementation shows five `FAILED` lines. That is the red phase, and it is not a formality: a test that passes before the implementation exists is testing the wrong thing.

### Do this now

Save the file above as `spec_search_memory.py` in your `cs357-work` repo, run `pytest spec_search_memory.py` and confirm five failures, then **commit the failing tests before any implementation exists**. That commit is your reversibility line: whatever the agent does next, `git checkout .` returns you to a known state with the spec intact.

Now start `opencode` and ask for the **plan** first, exactly as in Section 2b:

```text
Read spec_search_memory.py. Before you change anything, tell me which functions you
will add and what each one will do. One sentence each. Then stop and wait.
```

Read what comes back. If the plan proposes editing the tests, or inventing a corpus, or reaching for a library you did not ask for, **say no now**, while saying no is free. Only when the plan is right:

```text
Good. Implement it. Do not modify the tests. Do not modify CORPUS.
```

> **You've succeeded when** you have a plan you approved in your scrollback, `pytest` is green, you did not touch the tests, and `git diff` shows changes confined to the body of `search_memory` and any helpers it needed.

> **Start the run, then keep reading.** `llama3.2` is a 3-billion-parameter model on your laptop, and implementing five tests' worth of behavior may take it several minutes and more than one attempt. That is the honest capability of a small local model, not a broken setup. Kick off the implementation, then read Part III while it works, and come back to the result. If it is still flailing after two attempts, shrink the ask to one failing test and write down what you changed: *the size of instruction this model can actually follow* is a real finding, and it is worth more than a green test suite you got by luck. If you had to reject a plan first, say so in your notes; that rejection is the most valuable thing that happened in this exercise.

### Critical Thinking Questions

4. AC-1 says the function returns "exactly 2 strings." Is that a testable acceptance criterion? What would make an acceptance criterion *un*testable?

   > *Hint: A testable criterion can be checked by a program with no human judgment. Words like "good," "appropriate," "reasonable," or "fast" make a criterion untestable unless you define the measurement.*

5. AC-2 says results must be "drawn from the corpus," and the test checks `assert r in CORPUS`. Why does that check fail if the agent returns a plausible paraphrase instead of a verbatim document, and why do you *want* it to fail in that case?

6. The spec says the function must "raise a clear error rather than silently failing," and AC-3 through AC-5 operationalize it. Describe what a *silently failing* implementation would do instead, and why that is more dangerous than a crash in a system other code depends on.

7. You told the agent "do not modify the tests." Suppose it had modified them and everything went green. What exactly would you have lost?

   > *Hint: What were the tests standing in for?*

> **Common Misconception:** "TDD means writing tests after the code to check that it works." In test-driven development the tests come first and they must *fail* first. The red phase is what confirms your test is actually measuring something. An agent that can see your tests and cannot see your intent will satisfy the tests; that is precisely why the tests have to encode the intent.

In the TDD cycle, what does "red" mean?

[( )] The code compiles but has a runtime error
[( )] The test file has a syntax error that prevents it from loading
[(X)] The test runs but fails, because the implementation does not yet exist or is incorrect
[( )] The test passes but the code is slow

---


# Part III: Reading the Diff

In this part you do the thing that no model does for you. Your tests are green. That is necessary and it is not sufficient, and the gap between those two words is where this part lives.

## 5. What to Look For

Tests are not a complete specification of correct behavior; they are a sample of the behaviors you thought to check. Diff review is how you find the behaviors you forgot to test. Four questions, every time:

1. **Spec fidelity.** Does the implementation match the *spec*, or only the letter of the tests?
2. **Hidden assumptions.** Does it assume sorted input, single-threaded access, ASCII-only text, a network that is always up, or some other precondition the spec never stated?
3. **Security.** Does it use `eval()`, build a shell command out of user input, write outside the working directory, or otherwise let external input become executable?
4. **Resources.** Does it leave files open, build unbounded data structures, or loop with no exit condition?

Read the diff, not the summary the agent gives you. `git diff` shows what changed; the agent's prose describes what it *believes* it changed, and those are different documents.

---

## Model 3: A Planted-Bug Diff

Below is an implementation of `search_memory` that an agent might plausibly produce. **It passes all five tests from Model 2.** It contains three deliberate problems. Read it as a team before answering; the Recorder marks the line number of each problem your team finds.

```python
import requests
import math

CORPUS = [
    "The Myrin Library closes at midnight on weekdays.",
    "First-year students may not bring vehicles to campus.",
    "Wismer Center serves continuous dining from 7am to 8pm.",
    "All students must complete a writing seminar in their first year.",
    "The Bakes Center is open to all students with a valid ID.",
]

def embed(text):
    try:
        r = requests.post("http://localhost:11434/api/embeddings",
                          json={"model": "nomic-embed-text", "prompt": text},
                          timeout=120)
        return r.json()["embedding"]
    except Exception as e:
        print(f"[search_memory:embed] {e}")
        import traceback; traceback.print_exc()
        return []

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0

def search_memory(query, k):
    processed_query = eval(f'"{query}"')

    if k <= 0:
        raise ValueError("k must be positive")
    if not query:
        raise ValueError("query must not be empty")
    if k > len(CORPUS):
        raise ValueError("k exceeds corpus size")

    q_vec = embed(processed_query)

    if not q_vec:
        return []

    scored = [(cosine(q_vec, embed(doc)), doc) for doc in CORPUS]
    scored.sort(reverse=True)

    return [doc for _, doc in scored[:k]]
```

### Critical Thinking Questions

8. **Find the `eval()`.** Explain why calling `eval()` on `query`, a string that comes from the user, is a security problem. What happens if someone passes `query = "__import__('os').system('rm -rf /')"`? What is the correct way to handle that string?

   > *Hint: `eval()` executes arbitrary Python. If `query` arrives from an HTTP request or a form field, the caller chooses what runs. Also ask: what was `eval` even for here? Nothing in the spec asked for it.*

9. **Find the silent failure.** The spec says the function must "raise a clear error rather than silently failing." Look at the block beginning `if not q_vec`. Does it follow the spec? Write the one-line fix.

   > *Hint: Returning `[]` when the embedding service is down tells the caller "no documents matched," which is a lie. What exception, with what message?*

10. **Find the resource problem.** The `k > len(CORPUS)` guard means the `[:k]` slice is always bounded, so where is the cost? For a five-document corpus it is invisible. Imagine ten million documents, and read the `scored = [...]` line again.

   > *Hint: How many network calls does that line make before anything is sliced? How would you bound it?*

11. For each of the three problems, describe one `pytest` case that would have caught it. One sentence each is enough.

12. Now the uncomfortable one. Every problem above survived a green test suite. Go back to the acceptance criteria in Model 2 and propose **one additional criterion** that would have made at least one of these bugs impossible to ship. What does the difficulty of writing that criterion tell you about the limits of specification?

> **Common Misconception:** "If all the tests pass, the code is correct." Tests verify the behaviors you thought to test. A function can pass a hundred tests and still hold a security hole, a resource leak, or a wrong answer on an input nobody imagined. Passing tests are necessary and not sufficient, which is exactly why diff review sits alongside testing rather than being replaced by it.

A coding agent produces an implementation that passes all five acceptance-criterion tests. A reviewer then spots `eval(query)` on line 4. What does that demonstrate?

[( )] The tests were badly written and should be discarded
[( )] The agent made a mistake the test suite should have caught automatically
[(X)] Tests verify sampled behaviors; diff review catches behaviors outside the tests' scope, such as security properties
[( )] The reviewer is being overly cautious; passing tests mean the code is safe to ship

---


# Part IV: Synthesis and Practice


## 6. Exercises

1. **Design an agent brief.**

   *What to do:* Write a 3-5 sentence task description for a coding agent that is specific enough to be verifiable. Then write an acceptance criteria checklist of at least 4 items the agent's Verify stage could use to determine "done." Trade your brief with another team and critique their criteria for testability.

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

   *You've succeeded when* your Presenter can explain the team's rejection reasoning in terms of a specific risk, not just "it looks wrong" but "if this change ships, then X could happen."

4. **Design an overnight brief.**

   *What to do:* Write a brief you would hand a `gnhf`-style self-running loop to work on while you sleep. It must contain three things: (a) a goal small and concrete enough to be verifiable, (b) an acceptance-criteria checklist the loop's Verify stage can check on its own (reuse the testable-vs-vague discipline from Exercise 1), and (c) an explicit **stop condition**: a step budget *and* the check that means "done." Then write one sentence naming the worst thing that could land in the morning's branch if your acceptance criteria are too weak.

   *Starter hint:* A good overnight goal is bounded and testable, e.g. "Add input validation to every route in `api/`, so that a missing required field returns HTTP 400 with a JSON error body." A weak acceptance criterion ("validation works") lets a loop commit code that passes because no test exercises the missing-field case, exactly the silent-Verify failure from Model 2. Pair every criterion with a test the loop can actually run:
   ```text
   Goal: add missing-field validation to all routes in api/
   Acceptance:
     - POST /users with no "email" returns HTTP 400  (test: test_users_missing_email)
     - every existing test in tests/ still passes
   Stop when: all acceptance tests pass, OR 30 iterations reached
   ```

   *You've succeeded when* another team could hand your brief to an unattended loop and know, without asking you, both when it should stop and how it would decide it succeeded, and you can name the failure a weak criterion would let through.

---

## Reflection Prompt

*Personal:* Coding agents blur the line between "tool I use" and "colleague I supervise." Think about a task in your own coding experience where you wish you could have handed off the implementation to someone else while staying in charge of the design. At what point in the process would you have wanted to reclaim control?

*Technical:* Based on today's models, at which stage of the agent loop do you most want human oversight, and at which stage would you be comfortable letting the agent run unsupervised? What specific signals or artifacts from the agent would increase your confidence enough to expand its autonomy? What would need to be true about the agent's track record?

*Societal:* If coding agents can implement features from a plain-English description, what happens to entry-level software engineering jobs that are currently filled by people writing exactly that kind of code? Is this similar to or different from previous waves of automation in programming (compilers, IDEs, code generators)? What new skills become more valuable when implementation is cheap?

> *Hint:* Consider the history of compilers (which eliminated assembly programmers), high-level languages (which eliminated much manual memory management), and IDEs with autocomplete (which changed how code is written). What new roles emerged after each of those transitions?

---

---

---

-> Coming Up Next: You watched the agent produce a different plan each time you asked, and you pinned `temperature` in Week 1 to stop exactly that. Next session, *Why Different Answers Every Time? Sampling, Temperature, and Generation*, explains where the variation comes from, which is also the reason a schema your parser depends on has to be constrained rather than requested. Keep `spec_search_memory.py`: writing the check before the work is the through-line of the next several weeks.


# Part V: Going Further (self-paced)

Nothing below is assumed by Parts I through IV, and none of it is required to finish today's work. It is here because your labs and your project will eventually need it: a comparison of how different agents are built, a full worked scenario from goal to commit, the patterns for loops that run unattended overnight, the cowork paradigm for agents that work outside a codebase, and the complete opencode configuration reference. Read the section you need when you need it.


## Going Further A: A Comparison of Coding Agent Architectures

Three open or widely-used coding agents take meaningfully different architectural approaches to the same problem: how does an agent read a codebase, plan changes, and execute them safely?

Study the table below like you would compare three contractors before hiring one: focus on the Safety Model column, because that column determines how much damage a wrong decision can cause.

Think of these architectures the way you might think about three different contractors you could hire to renovate your kitchen. One starts work immediately with full access to your house. One writes a detailed blueprint you must approve before picking up a hammer. One can only use tools you have explicitly handed them. Each approach has real advantages and real risks.

| Agent | Architecture | How It Plans | File Access Method | How It Executes | Safety Model |
|---|---|---|---|---|---|
| **OpenCode** | Terminal-native; single LLM session with tool calls | Inline reasoning: the agent plans and acts in the same generation loop without separating these phases | Shell tools (`read_file`, `list_dir`, shell exec) called directly from the agent loop with no intermediary | Executes shell commands directly in the user's live environment, affecting real files immediately | Permission prompts before destructive operations; the `--dangerously-skip-permissions` flag disables all prompts and lets the agent act freely |
| **Plandex / pi.dev** | Plan-first; explicitly separates the planning phase from the execution phase | Generates a full *diff plan* as a structured, human-readable artifact before touching any file | Loads relevant file segments into context via semantic search, finds the most relevant code rather than reading everything | Applies the pre-approved plan as a batch operation; the user reviews the plan document before any file is changed | Human approval gate sits between plan and apply; no file is changed until the human clicks approve; changes are reversible until committed |
| **Hermes (tool-calling orchestrator)** | LLM acts as an orchestrator that selects and sequences registered function tools | Selects and sequences tool calls; each tool call is one discrete "action" the agent chooses | Registered filesystem tools (`read_file`, `write_file`) with defined JSON schemas that specify exactly what each tool can do | Tool functions run in the host process and return results to the LLM as observations it can reason about | Controlled entirely by which tools are registered; if a tool is not registered, that action is simply impossible |

### Critical Thinking Questions

A1. OpenCode and Hermes both execute in the host environment, while Plandex adds a human approval gate between planning and execution. What does this gate cost in terms of speed and developer interruptions, and what does it buy in terms of safety? Describe a situation where you would prefer each of the three models.

   *Hint: Think about the tradeoff between a surgeon who pauses before each cut to ask permission versus one who follows a pre-approved surgical plan. When does each approach make more sense?*

A2. In the table, "file access method" varies from raw shell commands to registered tool schemas. If the agent can run arbitrary shell commands, it can do *anything*, including deleting files or calling the network. If it can only call registered tools, it is limited to what the tools permit. Describe a specific attack or accident that shell access makes possible but registered-tool access prevents.

   *Hint: Consider what `rm -rf ~` does when run as a shell command, versus whether a `write_file` tool would allow that operation.*

A3. Every agent above must load file content into its context window before reasoning about it. A typical codebase has millions of tokens, far more than any context window can hold. How does each agent decide *which* files to load? What happens if the agent loads the wrong files (files that seem relevant but are not) and then makes edits based on them?

   *Hint: If you asked a contractor to fix your plumbing but they studied the electrical blueprints by mistake, what kind of "fix" might result?*

---

## Going Further B: A Full Scenario, "Add OAuth2 Login"

A student types: *"Add OAuth2 login with GitHub to this Flask app."* The coding agent begins its loop. Trace what happens at each stage.

Read the table below as a time-lapse of one real agent run. Pay special attention to the Commit step at the bottom; it contains the most common beginner surprise about how git staging works in an agentic context.

Reading this table top-to-bottom is like watching a time-lapse of the agent working. Notice that the agent hits a problem at the Verify stage (a test fails) and loops back to fix it; this is the normal, healthy behavior of the loop. Also notice Step "Act (shell)" at the bottom: `git add -A` stages *everything* in the working directory, including files the agent did not intentionally change.

| Step | Agent Action | Files Read | Files Written | Shell Commands Run |
|---|---|---|---|---|
| Perceive | Scans the repository tree to understand the project structure; finds `app.py`, `requirements.txt`, `templates/login.html`, and the existing `/login` route | `app.py`, `requirements.txt`, `templates/login.html` | *(none, this step only reads)* | `ls` (list directory), `git log --oneline -10` (see recent changes) |
| Plan | Identifies four changes needed: (1) add `authlib` dependency, (2) add GitHub OAuth config variables, (3) add `/auth/github` and `/auth/callback` routes, (4) update login template to link to the new OAuth flow | *(loaded context from Perceive step)* | *(plan is internal, not written to a file in this architecture)* | *(none, planning does not execute commands)* |
| Act (edit 1) | Appends `authlib` to `requirements.txt` so the dependency is declared | `requirements.txt` (reads current content) | `requirements.txt` (appends one line) | *(none)* |
| Act (edit 2) | Adds the OAuth config block (client ID, secret, redirect URL) and two new route functions to `app.py` | `app.py` (reads current content) | `app.py` (adds ~40 lines of code) | *(none)* |
| Act (shell) | Installs the new dependency and runs the full existing test suite to check for regressions | *(none)* | *(none, pip and pytest do not write project files)* | `pip install -r requirements.txt` (installs authlib), `pytest` (runs all tests) |
| Verify | Reads pytest output; 3 tests pass, 1 fails: the `/login` redirect test now expects a GitHub OAuth redirect URL but the old test expected a different URL | pytest output shown in the terminal | *(none)* | *(none)* |
| Loop - Replan | Updates the `/login` redirect test to match the new expected behavior (redirecting to GitHub OAuth); re-runs pytest to confirm all 4 tests now pass | `tests/test_routes.py` | `tests/test_routes.py` | `pytest` |
| Commit | All tests pass; stages all changed files and commits with a descriptive message | *(none)* | *(git commit record)* | `git add -A` (stages everything in the working directory), `git commit -m "Add GitHub OAuth2 login via authlib"` |

### Critical Thinking Questions

B1. In the Commit step, the agent runs `git add -A`. This command stages *every modified and untracked file* in the working directory, not just the files the agent intentionally changed. What files could be accidentally staged if the working directory contained a `.env` file holding secrets like `GITHUB_CLIENT_SECRET=abc123`? What specific design choice in the agent or its environment would prevent this accident?

   *Hint: A `.gitignore` file tells git which files to never stage. Who is responsible for ensuring `.env` is listed there: the developer, the agent, or both?*

B2. The agent modified `tests/test_routes.py` to make the failing test pass. This sounds reasonable, but describe a scenario where changing the test to match the implementation is actually the *wrong* decision. When does a failing test mean "fix the test" versus "fix the code"?

   *Hint: A test that asserts "the login page requires a password" is not wrong just because the new code skips the password check. What should the agent do when the failing test is documenting a requirement, not an outdated expectation?*

B3. The agent's context window at the Verify stage contains the original task, the full plan, all edits made so far, and the pytest output. For a large codebase, information from the beginning of the session may have scrolled out of the context window by this point. What specific information from the Perceive stage might be lost, and how might that loss cause the agent to introduce a subtle bug in a later repair attempt?

   *Hint: Consider a case where the agent learned at the start that the project uses a custom session management library, but that fact has since scrolled out of the context window. What might go wrong when it tries to implement the OAuth callback?*

---

## Going Further C: Loops That Run Themselves - Ralph, autoresearch, gnhf, and Crews

Model 2 traced *one* pass of the agent loop. But the loop's real power appears when you run it **over and over, unattended**: the agent finishes, a shell script starts it again, and it keeps going while you sleep. The surprising design choice that makes this work is that each iteration begins with a **fresh context window**. That sounds like amnesia, and it would be, except the agent's memory does not live in the conversation; it lives on **disk**: the codebase itself, a running `TODO` file, and the `git` history. Fresh context is a *feature*: it sidesteps the context-overflow failure mode from Model 2's Perceive stage, because the agent re-reads only what it needs each round instead of dragging a bloated, half-forgotten history behind it.

Think of it like a relay of identical runners who cannot talk to each other but share one notebook. Each runner reads the notebook, runs one leg, writes down what they did, and hands off. No runner remembers the race; the notebook does.

Study the Safety Model column below the way you did in Model 1: when the loop runs while you are asleep, that column is the only thing standing between you and a branch full of confident nonsense.

| Pattern | What it is | Memory between iterations | How it stops | Safety model |
|---|---|---|---|---|
| **Ralph loop** (Geoffrey Huntley) | A brute-force `while` loop that re-runs the *same prompt file* against the agent, iteration after iteration | The codebase, a `TODO` file, and `git` history; each iteration starts with a fresh context and re-reads them | A human stops it, or a "task complete" check written into the prompt trips | Deliberately minimal: relies entirely on the test suite plus the ability to `git revert` a bad iteration |
| **autoresearch** (Karpathy's variant) | The *same* loop pointed at ML research instead of code | Model checkpoints and metrics logs on disk | A target validation-loss or metric is reached | The success *metric* is the guardrail: you iterate on model quality, and a worse score is simply discarded |
| **gnhf** ("good night, have fun") | An overnight orchestrator that splits a goal into small steps, each run in a fresh context seeded with a base context plus prior learnings | Each successful step is a commit on a dedicated `gnhf/<slug>` branch | A step budget, or the goal's acceptance check, is met | Success => commit; failure => `git reset --hard` and exponential backoff; `git` worktrees isolate parallel agents; agent-agnostic (Claude Code, Codex, opencode, Copilot, pi, ACP targets) |
| **firstmate** (a "crew") | An agent *distro*, a portable directory of instructions, skills, tooling, policies, and state that turns one general agent into a coordinated crew | Shared distro state plus the repository | You end the primary session | "Talk to one agent, ship with a crew": one primary session delegates to specialized sub-agents, each with a narrower, safer scope |

Notice what these share: they are the **Step Budget** and **Acceptance Criteria** from the Key Concepts table, scaled up. In an interactive session you are the stopping condition and the final judge. In an unattended loop you are asleep, so the *step budget* is the only thing preventing a runaway bill, and the *acceptance check* (usually the test suite) is the only thing preventing a tidy commit of broken code. Model 2's Verify stage is no longer one step among five; when the loop runs itself, **Verify is the whole game**.

### Critical Thinking Questions

C1. A Ralph loop starts each iteration with an empty context window, yet it can complete a multi-day refactor no single session could hold. Explain where the agent's "memory" actually lives, and why re-reading it each iteration is *safer* than carrying the full history forward.

    *Hint: A single long session accumulates every file it ever read until the important early facts scroll out, the exact failure in Model 2's Perceive row. What does a runner who re-reads the shared notebook each leg avoid that a runner trying to remember the whole race does not?*

C2. `gnhf` commits each successful step to a branch but runs `git reset --hard` after a failed one. Contrast this with a Ralph loop that edits files in place with no automatic rollback. For an overnight run on a codebase you care about, which safety model would you choose, and what property of your project (tests? review habits? branch protection?) does your choice depend on?

    *Hint: What does `git reset --hard` throw away, and what does it protect? If your test suite is thin, does per-step rollback still save you, or does it just tidily discard work while still letting a passing-but-wrong step through?*

C3. `firstmate` turns one agent into a crew of specialized sub-agents. Using Model 1's "controlled entirely by which tools are registered" idea, explain how giving each crew member a *narrow* scope can make the whole crew safer than a single agent with every capability at once. Then name a coordination failure a crew introduces that a single agent does not have.

    *Hint: A sub-agent that can only edit tests cannot also `git push`. But now two sub-agents share one repository: what goes wrong if both edit the same file, or if one's idea of "done" contradicts another's?*

> **Common Misconception:** Students often assume that "fresh context each iteration" means the agent forgets everything and cannot make real progress, that it must be flailing in circles. The opposite is true, *and it is the whole point*: the loop deliberately externalizes memory to the filesystem and `git` so that no single context window has to hold the entire task. The agent is not remembering less; it is remembering *on disk*, where memory is durable, inspectable, and does not decay as the window fills. The real risk is not amnesia; it is an unattended loop with a weak Verify stage happily committing work that passes thin tests but violates a requirement no test encodes.

Why does a Ralph loop start each iteration with a *fresh* context window instead of carrying the full conversation forward?

[( )] To reduce the number of API calls, since a fresh context uses fewer total tokens over the whole run
[( )] Because the model is legally required to discard prior context between runs
[(X)] Because the task's memory lives on disk (codebase, `TODO` file, `git` history), so each iteration can re-read exactly what it needs and avoid the context-overflow failure that plagues one very long session
[( )] Because a fresh context makes the agent more creative by preventing it from repeating earlier ideas

---

## Going Further E: The Cowork Paradigm, General Agents Beyond Code

Every architecture so far assumes the agent's world is a **codebase**. But the same loop (perceive, plan, act, verify) works just as well when the "files" are a spreadsheet, a slide deck, and a browser tab. That is a different paradigm, and it is worth naming the three explicitly (the *Agentic CLI Tools* activity develops this framing in full):

| Paradigm | The agent's world | Who it is for | Example tools |
|----------|-------------------|---------------|---------------|
| **Chat** | A conversation window; *you* run any action it suggests | Anyone | ChatGPT, Claude.ai, LM Studio |
| **Code** | A scoped project directory the agent reads, edits, and tests | Developers | Claude Code, opencode, Codex |
| **Cowork** | Your whole desktop: apps, documents, files | Non-developers and general knowledge work | **Claude Cowork**, **OpenWork** |

**Cowork** is the coding-agent loop pointed at general computer work: drafting and editing documents, filling spreadsheets, moving files, driving apps, for people who are not writing code at all. **Claude Cowork** is a desktop application built for exactly this; **OpenWork** is an open-source alternative that wraps the same **opencode** engine you configured earlier in this activity, which is a neat illustration that "code" and "cowork" are the same machinery aimed at different worlds. And `firstmate`'s "crew" idea generalizes cleanly here: a crew of general agents can research, draft, and cross-check a report the way a code crew builds a feature.

The paradigm shift raises the stakes on everything this module taught about review. A wrong diff in the code paradigm is caught by tests and reversed by `git`. A cowork agent editing the wrong document, emailing the wrong person, or deleting the wrong file has no test suite and often no undo. The human's judgment does not disappear as agents leave the codebase; it *moves*, from "review the diff" to "define the guardrails of a world that has no `git revert`."

**Question B.** In the code paradigm, `git` and the test suite give you a safety net: you can review a diff and roll back a bad change. When a cowork agent operates across your whole desktop, what plays the role of "the diff" and "the rollback", and where does that leave the human's responsibility?

[[___ Your answer here ___]]

---

## Going Further D: Configuring OpenCode with Plugins and Project Instructions

OpenCode is configurable at two scopes: **project scope** (a file in your repository that everyone on the team shares) and **global scope** (a file in your home directory that applies to all your projects). Understanding which configuration belongs where is the same discipline as deciding which secrets belong in environment variables versus which belong in version control; the wrong choice exposes either too much or too little.

---

### The opencode.json Schema

OpenCode reads its configuration from `opencode.json`. Place this file at:

- **Project root** (`./opencode.json`) for settings that all contributors to this repository should share: things like the project's test command, architectural invariants, and which files the agent should never touch.
- **`~/.opencode/opencode.json`** for settings that are personal to you: your preferred model, your global instructions, your authentication tokens.

The file follows a published schema, which means your editor can validate it in real time:

The following JSON shows the minimal `opencode.json` schema declaration. This single line tells your editor to validate the file against the published schema, catching typos in configuration keys before they cause unexpected agent behavior.

```json
{
  "$schema": "https://opencode.ai/config.json"
}
```

---

### The Superpowers Plugin

OpenCode supports plugins that extend its built-in skill set. The Superpowers plugin adds pre-built skills for common agent development workflows (design-then-TDD, security audit, and structured refactor) so you do not have to write these prompts from scratch. Add it with a single line:

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
  "instructions": "This project uses pytest for all tests. Run `pytest -v` to verify. Never modify files in the `generated/` directory; they are auto-generated by the build step and will be overwritten. The database schema is in `models.py`; do not alter it without a migration."
}
```

An `AGENTS.md` file at the repository root is the preferred place for longer project instructions; it reads like a document for humans while also being parsed by the agent at startup.

**An `AGENTS.md` file at the repository root** (preferred for longer instructions, because it is readable as a document without parsing JSON):

```markdown
# Agent Instructions

## Architecture
This is a Flask application with a SQLAlchemy ORM layer. The agent loop
is in `agent.py`; the tool registry is in `tools/`. Do not add business
logic to `app.py`; it is a thin routing layer only.

## Invariants
- All database access must go through the ORM in `models.py`. Never write raw SQL strings.
- The public API (routes in `app.py`) is versioned. Do not change existing route signatures.

## Test Commands
- Run all tests: `pytest -v`
- Run with coverage: `pytest --cov=. --cov-report=term-missing`
- Lint: `ruff check . && black --check .`

## Do NOT Modify
- `generated/`: auto-generated by `make generate`
- `migrations/`: managed by Alembic; create new migrations with `flask db migrate`
```

**What to put in project instructions:**

- The architecture overview: what each top-level module does and how they connect
- Invariants: rules the codebase enforces that are not visible in tests (e.g., "never use raw SQL," "all API responses must be JSON")
- The exact commands to run tests, linters, and builds; the agent uses these in its Verify stage
- An explicit list of files or directories the agent should never modify

**What NOT to put in project instructions:**

- API tokens, passwords, or any secrets; these belong in environment variables
- Personal preferences (your editor, your color scheme); these belong in global config
- Instructions that are only relevant to one contributor; these belong in that person's global `~/.opencode/` config

---

### Critical Thinking Questions

**Question A.** Why would you commit `opencode.json` to version control but NOT your global `~/.opencode/instructions.md`?

[[___ Your answer here ___]]

*Hint: Think about what each file contains and who should be affected by it. The project `opencode.json` describes invariants and conventions of the codebase that every contributor and every agent session working on this repository should respect. The global `~/.opencode/instructions.md` describes your personal preferences (things like your preferred coding style, your typical workflow, or notes about your development machine) that are irrelevant or even wrong for other contributors. What happens if you commit your personal instructions and a teammate with different preferences pulls them? What happens if the project instructions are not committed and a new contributor's agent session does not know the invariants?*

Two instructions are being considered for `opencode.json` in a project's repository. Which instruction belongs in **project scope** (committed to the repository) rather than in a developer's personal global config?

[( )] "Use Black for formatting"; this belongs in project scope because formatting consistency matters to all contributors, not just one developer's personal taste
[(X)] "Do not modify the database schema in `models.py` without creating an Alembic migration first"; this is a project-specific invariant that all contributors and all agent sessions must respect
[( )] "My preferred model is llama3.2 at temperature 0.2"; this is a project-wide default that should be committed so all contributors use the same model for reproducibility
[( )] "Open files in VSCode rather than the terminal editor"; this should be in project scope to enforce a consistent editing environment across the team

---

## Further Reading

- Shunyu Yao et al. "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR* (2023). The reasoning pattern underlying most coding agents.
- Plandex documentation: https://docs.plandex.ai, especially the "plans" concept and diff review workflow.
- OpenCode GitHub repository: https://github.com/sst/opencode, read the README for architecture decisions and the `--dangerously-skip-permissions` flag discussion.
- Lilian Weng. "LLM Powered Autonomous Agents." *Lil'Log* (2023). https://lilianweng.github.io/posts/2023-06-23-agent/, comprehensive survey of agent architectures including coding agents.
- Geoffrey Huntley. "everything is a ralph loop." https://ghuntley.com/loop/, the origin and rationale of the fresh-context brute-force loop; see also https://ralph-wiggum.ai/.
- **gnhf** ("good night, have fun"), overnight autonomous orchestrator: https://github.com/kunchenguid/gnhf.
- **firstmate**, an agent distro for running a crew: https://github.com/kunchenguid/firstmate.
- **OpenWork**, the open-source, opencode-powered alternative to Claude Cowork: https://github.com/different-ai/openwork.
