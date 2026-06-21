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

A **coding agent** is not a smarter autocomplete. When GitHub Copilot suggests the next line, it reads your cursor position and offers a completion you accept or reject. A coding agent reads your entire repository, understands a goal ("add OAuth2 login"), decomposes it into file-level tasks, edits multiple files, runs your test suite, interprets failures, and iterates until the goal is satisfied - or until it runs out of context or budget. The difference is agency: a persistent goal, world-affecting actions, and a loop that continues until done.

This matters for software engineering because it changes the unit of human judgment. Instead of reviewing every keystroke, you review the agent's *plan* before it acts and its *diff* before you merge. Getting that review right is a professional skill this module develops.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Read each model carefully as a team, then answer the Critical Thinking Questions individually before discussing. The Recorder compiles the team's consensus answers; the Presenter will share at least one point of disagreement with the class. After class, complete the Reflection Prompt in your notebook.

---

## Model 1: A Comparison of Coding Agent Architectures

Three open or widely-used coding agents take meaningfully different architectural approaches to the same problem: how does an agent read a codebase, plan changes, and execute them safely?

| Agent | Architecture | How It Plans | File Access Method | How It Executes | Safety Model |
|---|---|---|---|---|---|
| **OpenCode** | Terminal-native; single LLM session with tool calls | Inline reasoning - plans and acts in the same generation loop | Shell tools (`read_file`, `list_dir`, shell exec) called directly from the agent loop | Executes shell commands in the user's live environment | Permission prompts before destructive ops; `--dangerously-skip-permissions` flag disables them |
| **Plandex / pi.dev** | Plan-first; separates planning from execution | Generates a full *diff plan* as a structured artifact before touching any file | Loads relevant file segments into context via semantic search | Applies the pre-approved plan as a batch; user reviews the plan doc first | Human approval gate between plan and apply; changes are reversible until committed |
| **Hermes (tool-calling orchestrator)** | LLM-as-orchestrator calling registered function tools | Selects and sequences tool calls; each tool call is one "action" | Registered filesystem tools (`read_file`, `write_file`) with defined schemas | Tool functions run in the host process; results returned to the LLM as observations | Controlled by which tools are registered; unregistered actions are impossible |

### Critical Thinking Questions

1. OpenCode and Hermes both execute in the host environment, while Plandex adds a human approval gate between planning and execution. What does this gate cost, and what does it buy? When would you prefer each model?
2. In the table, "file access method" varies from raw shell commands to registered tool schemas. What is the security implication of allowing `shell exec` vs. restricting access to only defined tool functions?
3. Every agent above must load file content into its context window before reasoning about it. A typical codebase has millions of tokens. How does each agent decide *which* files to load, and what risk does the selection process itself introduce?

---

## Model 2: The Coding Agent Loop

The agent loop for coding tasks is an instance of the general perceive-think-act cycle, specialized for a software development environment. Each stage produces artifacts the next stage depends on.

| Stage | What the Agent Does | Inputs | Outputs | Failure Mode |
|---|---|---|---|---|
| **1. Perceive** | Reads the repository: directory tree, relevant source files, open issues, existing tests | File system, git log, task description | Working context loaded into the prompt | Loads too many files (context overflow) or wrong files (hallucinated edits) |
| **2. Plan** | Identifies which files to change and what changes to make; may emit a structured plan | Loaded context + task goal | Ordered list of file edits and shell commands | Underestimates dependencies; plans changes to wrong abstraction layer |
| **3. Act** | Applies edits file by file; runs shell commands (build, lint, test) | Plan + current file contents | Modified files, command outputs | Edit breaks unrelated functionality; shell command has irreversible side effect |
| **4. Verify** | Reads test output, lint results, and compiler errors; decides whether the goal is satisfied | Command output + original acceptance criteria | Pass/fail judgment; failure triggers replanning | Interprets a passing test suite as "done" when the tests didn't cover the new feature |
| **5. Commit or Loop** | If verified: commits with a message. If not: returns to Plan with failure context | Verify output | Git commit or updated plan | Infinite loop if verification never passes; commit with broken code if budget runs out |

### Critical Thinking Questions

4. The "Failure Mode" column shows that verification can be fooled by a test suite that doesn't cover the new feature. Whose responsibility is it to write acceptance criteria before the agent starts? What does this imply about the human's role in agentic development?
5. Trace the loop for a simple task: "rename function `calculate_total` to `compute_total` across all files." Which stages are trivial? Which stage is most likely to introduce a bug?
6. The step budget (max iterations) is a safety parameter. If you set it too low, the agent stops before finishing. If you set it too high, a stuck agent runs up API costs and possibly makes cascading bad edits. How would you decide on a budget for a medium-complexity task?

[[MC]]
In the coding agent loop, the *Verify* stage fails silently when:
- ( ) The test runner crashes with an exception
- ( ) The agent runs out of context window space
- (x) The existing test suite passes but does not cover the new behavior the agent just added
- ( ) The agent emits a "Final Answer" action before running tests

---

## Model 3: Scenario - "Add OAuth2 Login"

A student types: *"Add OAuth2 login with GitHub to this Flask app."* The coding agent begins its loop. Trace what happens at each stage.

| Step | Agent Action | Files Read | Files Written | Shell Commands Run |
|---|---|---|---|---|
| Perceive | Scans repo tree; finds `app.py`, `requirements.txt`, `templates/login.html`, existing `/login` route | `app.py`, `requirements.txt`, `templates/login.html` | *(none)* | `ls`, `git log --oneline -10` |
| Plan | Identifies: (1) add `authlib` dependency, (2) add GitHub OAuth config vars, (3) add `/auth/github` and `/auth/callback` routes, (4) update login template | *(loaded context)* | *(plan artifact, internal)* | *(none)* |
| Act (edit 1) | Appends `authlib` to `requirements.txt` | `requirements.txt` | `requirements.txt` | *(none)* |
| Act (edit 2) | Adds OAuth config block and two new routes to `app.py` | `app.py` | `app.py` | *(none)* |
| Act (shell) | Installs dependencies; runs existing test suite | *(none)* | *(none)* | `pip install -r requirements.txt`, `pytest` |
| Verify | Reads pytest output; 3 tests pass, 1 fails - `/login` redirect test now expects GitHub OAuth redirect | pytest output | *(none)* | *(none)* |
| Loop - Replan | Updates the `/login` redirect test to match new behavior; re-runs pytest | `tests/test_routes.py` | `tests/test_routes.py` | `pytest` |
| Commit | All tests pass; commits with message "Add GitHub OAuth2 login via authlib" | *(none)* | *(git commit)* | `git add -A`, `git commit -m "..."` |

### Critical Thinking Questions

7. In Step "Act (shell)", the agent runs `git add -A` at the end. What files could be accidentally staged if the working directory contained a `.env` file with secrets? What design choice would prevent this?
8. The agent modified `tests/test_routes.py` to make the tests pass. Is this always the right call? Describe a scenario where changing the test to match the implementation is *wrong*.
9. The agent's context window at the Verify stage contains: the original task, the full plan, all edits made so far, and the pytest output. For a large codebase, what information has been *lost* from earlier in the session by this point, and how might that loss cause a subtle bug?

---

## Exercises

1. **Design an agent brief.** Write a 3-5 sentence task description for a coding agent that is specific enough to be verifiable. Then write an *acceptance criteria* checklist (at least 4 items) the agent's Verify stage could use to determine "done." Trade with another team and critique their criteria for testability.

2. **Trust boundary audit.** For the OAuth2 scenario in Model 3, list every external service or system the agent contacted (file system, network, package registry, git). For each, write one sentence describing what goes wrong if that service is compromised or returns incorrect data during the agent's run.

3. **Diff review exercise.** Your instructor will display a git diff from an actual coding agent session. As a team, identify: (a) one change that is clearly correct, (b) one change that requires domain knowledge to evaluate, and (c) one change you would reject and why. The Presenter explains the team's reasoning to the class.

---

## Reflection Prompt

In your notebook: coding agents blur the line between "tool I use" and "colleague I supervise." Based on today's models, at what stage of the agent loop do you most want human oversight, and at what stage would you be comfortable letting the agent run unsupervised? What would need to be true about the agent's track record before you expanded its autonomy?

---

## Further Reading

- Shunyu Yao et al. "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR* (2023). The reasoning pattern underlying most coding agents.
- Plandex documentation: https://docs.plandex.ai - especially the "plans" concept and diff review workflow.
- OpenCode GitHub repository: https://github.com/sst/opencode - read the README for architecture decisions and the `--dangerously-skip-permissions` flag discussion.
- Lilian Weng. "LLM Powered Autonomous Agents." *Lil'Log* (2023). https://lilianweng.github.io/posts/2023-06-23-agent/ - comprehensive survey of agent architectures including coding agents.
