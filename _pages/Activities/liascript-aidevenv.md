<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-aidevenv.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-aidevenv.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Designing Your AI Development Environment

A coding agent that starts every session knowing nothing about your project is like a new teammate who reads none of the onboarding docs — capable but constantly asking questions you have already answered. We move from **the stateless agent problem $\rightarrow$ three layers of persistent context $\rightarrow$ writing effective project instructions $\rightarrow$ plugins and skills $\rightarrow$ the meta-loop of improving the environment itself**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Agent Memory File** | A plain-text file the agent reads at the start of every session to reconstruct context it cannot remember across sessions — project structure, conventions, what not to do. | `AGENTS.md` in the project root listing architecture and invariants |
| **Project Instructions** | Agent memory scoped to one project: the architecture, key invariants, test commands, and common pitfalls. Lives next to the code it describes. | An `AGENTS.md` for the RAG lab telling the agent "do not modify the Chroma schema" |
| **Global Instructions** | Agent memory that applies to every project you work on: your personal style preferences, preferred libraries, tone. Lives in your home directory or agent config. | `~/.opencode/instructions.md` containing "always use Black for Python formatting" |
| **Skill** | A reusable prompt template — a named workflow you can invoke by name instead of re-typing the same long prompt. | A "security-review" skill that prompts the agent to check a diff for OWASP top-10 agent risks |
| **Plugin** | A collection of skills and tools packaged together and loaded by the agent at startup via a config file. | The `superpowers` plugin providing pre-built skills for TDD, security audit, and refactoring |
| **Environment as Code** | The principle that your agent config files, instructions files, and skill definitions are version-controlled alongside your source code, so the agent environment is reproducible. | Committing `opencode.json` and `AGENTS.md` to the same repository as the application code |
| **Context Window Hygiene** | The discipline of keeping what goes into the agent's context window purposeful and compact — avoiding bloated instructions that crowd out the actual task. | A 10-line `AGENTS.md` that constrains behavior vs. a 200-line file that describes every method |

---

# Part I: The Problem of Stateless Agents

In this part, you will diagnose why AI coding agents "forget" your project conventions between sessions and map the three layers of context (working memory, project memory, long-term memory) that a well-designed environment must provide.

## 1. Why Context Does Not Persist

**Why this matters:** Every time you start a new session with a coding agent, you are talking to a version of that agent with no memory of your previous conversations, your project architecture, or your preferences. This is by design — agent context windows are finite, and persisting all prior work would quickly overflow them. But it creates a real cost: if you re-explain the same project context at the start of every session, you waste tokens, introduce inconsistencies, and rely on yourself to remember what to say. Systematic context management is the solution.

**The naive approach** is to paste a block of project context at the start of every prompt: "We are building a RAG system. The corpus is stored in Chroma. Do not modify the collection schema. Tests live in `tests/`. Run them with `pytest -q`." This works, but it is fragile — you forget details, the block grows, and different sessions receive different context.

**The systematic approach** is to encode context in files that the agent always reads, so you never have to re-explain. There are three layers, each scoped appropriately:

| Layer | Where it Lives | What it Contains | Who Writes it |
|-------|----------------|------------------|---------------|
| **Global instructions** | `~/.opencode/instructions.md` or equivalent home-directory config | Personal style (formatting, preferred libraries, tone) that applies to every project | You, once |
| **Project instructions** | `./AGENTS.md` or `opencode.json` `instructions` field in the project root | Project architecture, key invariants, test commands, what not to do | You, per project |
| **Skills** | Named `.md` files loaded by the agent config | Reusable prompt templates for specific workflows | You or the plugin author |

---

## Model 1: Matching Context to Layer

A developer is working on the RAG lab from earlier in the course. They have accumulated the following pieces of context they want the agent to know:

| Context Item | Description |
|---|---|
| A | "Always use Black for Python formatting." |
| B | "The Chroma collection name is `campus`; never delete or recreate it." |
| C | "Run tests with `pytest -q tests/`." |
| D | "Prefer `pathlib.Path` over `os.path` for file operations." |
| E | "The embedding model is `nomic-embed-text` served by Ollama at `localhost:11434`." |

### Critical Thinking Questions

1. For each context item A–E, decide which layer (Global, Project, Skill) is most appropriate. Justify your answer in one sentence each.

   > *Hint: Ask yourself: would this context apply to a completely different project the developer works on next semester? If yes, it is global. If it is specific to this RAG project, it is project-level. If it describes a repeatable multi-step workflow rather than a fact, it might be a skill.*

2. What is the cost of putting context item B ("never delete the collection") in the global instructions file instead of the project instructions file?

   > *Hint: The global file is read for every project. If you start a different project with a different database, the instruction to not delete the `campus` collection in Chroma is irrelevant noise. What happens to the agent's context window when irrelevant instructions pile up?*

3. A teammate clones the repository and starts a new agent session. Which layers of context do they automatically inherit, and which do they need to set up themselves?

   > *Hint: Only files that are version-controlled in the repository are shared when the repo is cloned. Which of the three layers lives inside the repository?*

> **⚠️ Common Misconception:** "More context is always better — fill the instructions file with everything you know about the project." Context window space is finite and shared with the actual task. An instructions file that lists every class name, every function signature, and the history of every decision crowds out the agent's working space for the current prompt. Effective instructions describe *constraints and invariants* — what the agent must not do, where things are, and what the conventions are — not a narration of the code.

A developer always wants their coding agent to use Black for Python formatting, regardless of which project they are working on. Which layer is most appropriate for this instruction?

[( )] Project instructions (`AGENTS.md` in the project root) — so it is version-controlled
[(X)] Global instructions (`~/.opencode/instructions.md`) — so it applies to every project automatically
[( )] A skill — so it can be invoked by name when formatting is needed
[( )] The prompt — paste it at the start of every session

---

# Part II: Writing Effective Project Instructions

In this part, you will write and critique `AGENTS.md` project instruction files — the persistent context layer that tells a coding agent your architecture, invariants, and out-of-scope changes before it writes a single line.

## 2. What Belongs in `AGENTS.md`

**Why this matters:** An agent that misunderstands your project architecture will make confident, plausible-sounding changes that break invariants you thought were obvious. The `AGENTS.md` file (or equivalent) is your opportunity to state those invariants explicitly, in a form the agent reads before it does anything. Think of it as the onboarding document you wish you had written for a new team member who cannot ask questions.

**What belongs in a project instructions file:**

- **Architecture overview** (2–3 sentences per component, not per file): "The ingestion pipeline reads from `data/`, embeds with Ollama, and writes to Chroma. The query path reads from Chroma only — it never writes."
- **Key invariants the agent must not violate**: "Do not modify the Chroma collection schema. Do not add new dependencies without updating `requirements.txt`."
- **What is out of scope**: "Do not add a web UI. Do not add authentication. Do not change the embedding model without a lab-wide discussion."
- **Where the tests are and how to run them**: "Tests live in `tests/`. Run with `pytest -q`. All tests must pass before committing."
- **Common pitfalls in this codebase**: "The `embed()` function returns `[]` on failure — callers must check for this. Do not call `embed()` in a loop without rate-limiting."

---

## Model 2: A Real Project Instructions File

Below is an example `AGENTS.md` for the RAG lab from earlier in the course.

```markdown
# RAG Lab — Agent Instructions

## Architecture
The system has two phases: indexing (run once, writes to Chroma) and query (run per request,
reads from Chroma). The Chroma client is ephemeral (in-memory); re-running the indexing script
resets it. The embedding model is `nomic-embed-text`; the generation model is `llama3.2`.
Both are served by Ollama at `http://localhost:11434`.

## Invariants
- Do not change the Chroma collection name from `campus`.
- Do not add network calls outside of `embed()` and `chat()`.
- Do not use `eval()`, `exec()`, or `subprocess` anywhere in the codebase.
- All external calls must be wrapped in try/except with traceback logging.

## Out of Scope
- Do not add a web server or HTTP API.
- Do not add authentication.
- Do not change the embedding model without updating this file and all tests.

## Tests
- Location: `tests/`
- Run with: `pytest -q tests/`
- All tests must pass before any commit.
- Do not delete existing tests; only add new ones.

## Common Pitfalls
- `embed()` returns `[]` on failure — callers must raise `RuntimeError`, not return silently.
- Chroma `n_results` must not exceed the collection size — guard with `min(k, col.count())`.
```

### Critical Thinking Questions

4. The instructions file above has 12 substantive lines of constraints. A teammate suggests expanding it to include a description of every function in the codebase. What is the argument against that expansion?

   > *Hint: The agent can read the source code directly when it needs to understand a function. What is the unique value of the instructions file that a code-reading agent cannot get from the source itself?*

5. The "Common Pitfalls" section mentions that `embed()` returns `[]` on failure. This is a fact about the current implementation that could become outdated if `embed()` is changed. What process would you add to ensure the instructions file stays current?

   > *Hint: If the instructions file is version-controlled, what event (a commit, a pull request review, a test failure) could trigger a reminder to update it? Think about how you keep a README in sync with code.*

6. The instructions say "Do not use `eval()`, `exec()`, or `subprocess`." How would you verify that the agent followed this instruction after it made changes? Write a one-line shell command or `pytest` test that checks for this.

   > *Hint: You do not need to trust the agent's output — you can check the code directly. The `grep` command can search for patterns in files: `grep -r "eval(" .` returns any line containing `eval(`. How would you turn this into a `pytest` test using Python's `subprocess.run`?*

> **⚠️ Common Misconception:** "Project instructions are like a README — describe what the code does." A README is for humans orienting themselves to a project. An instructions file is for constraining agent behavior. The distinction: a README says "this module handles embeddings"; an instructions file says "do not change the embedding model without updating this file." One describes; the other constrains. Descriptions help humans understand; constraints prevent agent errors.

Which of the following best belongs in a project instructions file rather than in the source code itself?

[( )] The signature of the `search_memory` function
[( )] The list of all Python files in the project
[(X)] The invariant "do not modify the Chroma collection schema" and how to run the tests
[( )] A copy of the project's git log

---

# Part III: Synthesis and Practice

In this part, you will extend your dev environment with the Superpowers plugin for OpenCode and design your own personalized AI environment — choosing which context layers to populate and how to keep them maintained as your project evolves.

## 3. The Superpowers Plugin for OpenCode

**Why this matters:** Writing every skill from scratch is repetitive — common developer workflows like "review this diff for security issues" or "write tests for this function before implementing it" are the same across many projects. Plugins package pre-built skills that you can load with a single line in your project config, giving the agent a vocabulary of named workflows without requiring you to write the prompt templates yourself.

**OpenCode supports plugins** defined in `opencode.json` at the project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [
    "superpowers@git+https://github.com/obra/superpowers.git"
  ]
}
```

When OpenCode starts, it reads this file, downloads the listed plugins, and makes their skills available by name. The `superpowers` plugin provides pre-built skills for common developer workflows: the design-TDD-review cycle, security audits, and refactoring patterns.

**Scoping a plugin to one project:** Placing `opencode.json` in the project root (not the home directory) means the plugin is available only when the agent is invoked from that directory. This prevents a project-specific skill (e.g., one that assumes a Chroma database exists) from being invoked accidentally in an unrelated project.

**Writing your own skill** requires a Markdown file with a structured prompt template. The file describes what the agent should do when the skill is invoked, what it should look at, and what output it should produce.

---

## Model 3: A Sample Skill

Below is a `security-review` skill that checks a diff for OWASP top-10 agent risks:

```markdown
# Security Review Skill

You are performing a security review of the diff provided. Check for each of the following
OWASP top-10 risks for LLM-integrated applications:

1. **Prompt Injection** — does any user-supplied string reach a model prompt without sanitization?
2. **Insecure Output Handling** — does any model output reach `eval()`, `exec()`, or a shell?
3. **Excessive Agency** — does the agent take destructive actions (delete, overwrite) without confirmation?
4. **Sensitive Data Exposure** — are API keys, tokens, or PII logged or returned to the user?
5. **Unbounded Resource Consumption** — are there loops or queries with no upper bound?

For each risk, state: FOUND / NOT FOUND / CANNOT DETERMINE, with a one-line explanation.
If any risk is FOUND, suggest the minimal fix.

Review the most recent diff provided by the user.
```

### Critical Thinking Questions

7. Why is it better to install the `superpowers` plugin in `./opencode.json` (project root) rather than a global config file in the home directory?

   > *Hint: The `superpowers` plugin includes skills that assume specific project structures (a Chroma database, a `tests/` directory, a `pytest` test runner). If these skills are available globally, what happens when you invoke the "design-TDD-review" skill in a project that uses a different database and a different test framework?*

8. The security-review skill above checks for five specific risks. A teammate argues: "A good skill should be general — check for *all* security issues, not just these five." What is the argument on the other side?

   > *Hint: A skill that says "check for all security issues" gives the agent no guidance about what to look for or how to report. What does specificity in a prompt template give you that generality does not?*

9. Suppose you want to write a skill for the final project in this course (an agent team or RAG system). Write the first two lines of the skill's Markdown file: the skill name (as an H1) and the first sentence of the agent instruction.

   > *Hint: The first sentence should tell the agent what role it is playing and what it is about to review. Look at the security-review skill above — it opens with "You are performing a security review of the diff provided." What is the analogous opening for a skill that reviews a RAG system's retrieval quality?*

> **⚠️ Common Misconception:** "A skill is just a shortcut for typing a long prompt." A skill is a *reusable contract*: it defines what the agent will examine, what it will report, and in what format. Because it is version-controlled and shared with the team, everyone's agent invokes the same workflow. The reproducibility is the value — not just the typing saved.

Why is it preferable to install a project-specific plugin in `./opencode.json` rather than the global agent configuration?

[( )] The global configuration file has a size limit that project configs do not
[( )] Skills defined in the project config run faster than globally installed ones
[(X)] Skills in the project config are only available when working in that project, preventing them from being invoked incorrectly in unrelated projects
[( )] The global config does not support the `plugin` field

---

## 4. Exercises

1. *Write a 10-line project instructions file.*

   - *What to do:* Choose a project you have worked on this semester (the RAG lab, the prompt engineering lab, or a personal project). Write an `AGENTS.md` file with at most 10 lines covering: one architecture sentence, three invariants, one "out of scope" statement, and the test command. Then start a fresh agent session with and without the file and compare the agent's first response to a task prompt.
   - *Starter hint:* Keep each invariant to a single sentence beginning with "Do not" or "Always." Architecture sentences should name components and the direction of data flow, not list files. Test command should be copy-paste runnable.
   - *You've succeeded when:* You can show that a fresh agent session with `AGENTS.md` present correctly names the test command, the forbidden operation, and the component that handles embedding — without you mentioning any of these in the prompt.

2. *Write a skill for retrieval quality review.*

   - *What to do:* Write a skill Markdown file called `retrieval-review.md` that instructs a coding agent to review a RAG system's retrieval results. The skill should ask the agent to check: (a) whether the retrieved chunks are topically relevant to the query, (b) whether any crucial chunk was missed (false negative), and (c) whether any irrelevant chunk was retrieved (false positive). The skill should produce a structured report with GOOD / PROBLEM / UNCERTAIN for each criterion.
   - *Starter hint:* Start with a role sentence ("You are reviewing the retrieval results of a RAG system"), then list the three criteria as numbered items, then specify the output format. Keep it under 15 lines.
   - *You've succeeded when:* You can invoke the skill on a sample query-result pair from the RAG lab and the agent produces a structured report that correctly identifies at least one retrieval problem in your test case.

3. *The meta-loop: improve your own environment.*

   - *What to do:* Identify one repeated pattern in your recent agent sessions — a piece of context you re-explain every session, a task you re-describe every time, or a format you always ask for. Encode it as either (a) an addition to `AGENTS.md`, (b) a new skill, or (c) a global instruction. Test the encoded version by starting a fresh session and checking whether the agent gets it right without being told.
   - *Starter hint:* Good candidates for encoding: "always print the retrieved context before the answer," "always run `pytest -q` after making changes," "always include a one-line summary of what changed at the top of your response." Pick the one you re-type most often.
   - *You've succeeded when:* You can demonstrate a fresh session in which the agent exhibits the desired behavior without any explicit instruction in the prompt, and you can point to the file that produced that behavior.

4. *Design the environment for the final project.*

   - *What to do:* Design (do not fully implement) the complete agent environment for the final project in this course — an agent team or a RAG system. Produce: (a) a 10-line `AGENTS.md`, (b) a list of three skills you would want pre-built, and (c) an `opencode.json` that loads the `superpowers` plugin. Justify each item in one sentence.
   - *Starter hint:* The `AGENTS.md` should cover the multi-agent architecture (which agent does what), the key invariants (what each agent must not do), and the test command. The three skills should cover the three most repeated tasks — likely: run the full evaluation, review a new agent's tool for security issues, and summarize the agent team's latest output.
   - *You've succeeded when:* You can hand your environment design to a teammate and they can, without asking you any questions, start a fresh agent session and correctly describe the project architecture, run the tests, and invoke a skill by name.

---

## Reflection Prompt

*Personal:* Identify one repeated prompt you have typed more than three times in this course's agent sessions — a context explanation, a formatting request, or a task description. Would you encode it as a global instruction, a project instruction, or a skill? Why that layer?

*Technical:* In your notebook: how does "environment as code" differ from a project README? A README is also a text file that describes the project. What does version-controlling `AGENTS.md` and `opencode.json` give you that version-controlling only a README does not?

*Societal:* Your `AGENTS.md` encodes invariants ("do not modify the database schema") and your global instructions encode preferences ("prefer functional style"). These reflect your assumptions and values. Who should review those files — and should they be subject to the same code review process as the source code? Identify one assumption you have already encoded and argue whether it should be visible to collaborators or kept private.

---

## → Coming Up Next

Your agent environment is version-controlled, your skills are shareable, and your project instructions run automatically. The next challenge is making this reproducible across the whole team and across deployments. The next module introduces **CI/CD and Publishing**: wiring a pipeline that installs your agent environment, runs the test suite, and publishes a working artifact — so the environment you designed today is the environment that ships.

---

## 5. Further Reading

- OpenCode documentation: https://opencode.ai/docs — covers `opencode.json` schema, plugin installation, and instructions file format.
- obra. "Superpowers plugin for OpenCode." https://github.com/obra/superpowers — the plugin used in Part III; source is instructive for writing your own skills.
- OWASP. "OWASP Top 10 for Large Language Model Applications." https://owasp.org/www-project-top-10-for-large-language-model-applications/ — the risk framework referenced in the security-review skill.
- Simon Willison. "Prompt injection explained." https://simonwillison.net/2023/Apr/14/prompt-injection/ — on why "do not use user input in prompts without sanitization" is a project invariant worth encoding.
- This course: [Governing Coding Agents — Charters, Handoffs, and Durable Memory](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentgovernance.md) — the layer above `AGENTS.md`: the charter, handoff protocol, and decision records that keep many sessions pointed at one goal.
