# Coding Agents: Agentic Development Tools
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

## Model 1: A Comparison of Coding Agent Architectures

Three open or widely-used coding agents take meaningfully different architectural approaches to the same problem: how does an agent read a codebase, plan changes, and execute them safely?

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

[[MC]]
In the coding agent loop, the *Verify* stage fails silently when:
- ( ) The test runner crashes with an exception
- ( ) The agent runs out of context window space
- (x) The existing test suite passes but does not cover the new behavior the agent just added
- ( ) The agent emits a "Final Answer" action before running tests

---

## Model 3: Scenario — "Add OAuth2 Login"

A student types: *"Add OAuth2 login with GitHub to this Flask app."* The coding agent begins its loop. Trace what happens at each stage.

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

---

## Reflection Prompt

*Personal:* Coding agents blur the line between "tool I use" and "colleague I supervise." Think about a task in your own coding experience where you wish you could have handed off the implementation to someone else while staying in charge of the design. At what point in the process would you have wanted to reclaim control?

*Technical:* Based on today's models, at which stage of the agent loop do you most want human oversight, and at which stage would you be comfortable letting the agent run unsupervised? What specific signals or artifacts from the agent would increase your confidence enough to expand its autonomy? What would need to be true about the agent's track record?

*Societal:* If coding agents can implement features from a plain-English description, what happens to entry-level software engineering jobs that are currently filled by people writing exactly that kind of code? Is this similar to or different from previous waves of automation in programming (compilers, IDEs, code generators)? What new skills become more valuable when implementation is cheap?

---

→ Coming Up Next: We will zoom in on one of the most consequential actions a coding agent can take — writing to and reading from the filesystem. The next activity examines how to constrain that access so that a mistake stays recoverable.

---

## Further Reading

- Shunyu Yao et al. "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR* (2023). The reasoning pattern underlying most coding agents.
- Plandex documentation: https://docs.plandex.ai — especially the "plans" concept and diff review workflow.
- OpenCode GitHub repository: https://github.com/sst/opencode — read the README for architecture decisions and the `--dangerously-skip-permissions` flag discussion.
- Lilian Weng. "LLM Powered Autonomous Agents." *Lil'Log* (2023). https://lilianweng.github.io/posts/2023-06-23-agent/ — comprehensive survey of agent architectures including coding agents.
