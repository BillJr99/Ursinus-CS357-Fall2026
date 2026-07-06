---
layout: assignment
permalink: /Assignments/CodingAgents
title: "CS357: Foundations of Artificial Intelligence - Lab: Coding Agents in Practice"

info:
  coursenum: CS357
  purpose: "To learn to direct, constrain, and critically review a coding agent so you reach trustworthy code rather than merely accepting what it generates."
  tilt:
    task: "Drive a coding agent to build a REST endpoint from a written spec, then review, constrain, and iterate on its diffs until the result is trustworthy."
    criteria: "Assessed on spec fidelity, line-by-line diff review, and the system prompt that constrains the agent; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To use a coding agent (OpenCode or Claude Code) to implement a feature from a written spec
    - To design an agent system prompt that constrains the coding agent's behavior appropriately
    - To evaluate coding agent output for correctness, style, security, and test coverage
    - To document the agent's decision-making process and review its diffs before accepting
  rubric:
    - weight: 30
      description: Task Execution and Spec Fidelity
      preemerging: The agent was run without a written spec, or the resulting code does not match the spec in major ways
      beginning: A spec exists and the agent produced code, but significant gaps remain between the spec and the implementation and no follow-up iteration was attempted
      progressing: The agent produced code that matches most of the spec after at least one iteration, with a minor mismatch or missing error case remaining
      proficient: The final code faithfully implements every requirement in the spec, including error cases and testing criteria, and the connection between each spec requirement and the corresponding code is traceable
    - weight: 25
      description: Review and Diff Analysis
      preemerging: Diffs were accepted without review, or no critique document was produced
      beginning: A critique document exists but identifies only surface issues (e.g., formatting) and the follow-up prompt does not address substantive problems
      progressing: The critique identifies at least one correctness issue and one security or completeness issue, and the follow-up prompt addresses both, with a minor gap remaining
      proficient: Every proposed change is reviewed line by line, the critique document clearly categorizes findings (correct, wrong, missing, security risk), the follow-up prompt is precise, and the second diff shows measurable improvement
    - weight: 25
      description: Safety and Constraint Design
      preemerging: No system prompt was written to constrain the agent, or the system prompt is so vague it provides no actual constraints
      beginning: A system prompt exists with at least one constraint, but the agent violated it and the violation was not noticed or addressed
      progressing: The system prompt defines file scope, library choices, and at least one prohibition, and violations (if any) are identified in the critique document
      proficient: The system prompt defines file scope, library choices, and explicit prohibitions (e.g., no external network calls, must include tests), all constraints are verified against the agent trace, and any constraint violations are documented and remediated
    - weight: 20
      description: Documentation and Reflection
      preemerging: No pair log or annotated diff is submitted
      beginning: Artifacts are submitted but annotations are minimal and reflection prompts receive one-sentence answers
      progressing: The annotated diff identifies most significant changes with comments, the pair log shows at least two role swaps, and reflection prompts are answered with specific examples
      proficient: Every diff annotation explains the why not just the what, the pair log shows regular swaps with timestamps, the scanner output is included and addressed, and reflection answers demonstrate a changed mental model about coding agents
  readings:
    - rtitle: "Coding Agents Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-codingagents.md"
    - rtitle: "The Local Agent Stack Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md"

tags:
  - agents
  - coding
  - security
  - testing

---

In this lab, you and your partner will use a coding agent to implement a real feature from a written specification — specifically a REST API endpoint — then critically review the generated diff, iterate with a follow-up prompt, and harden the final result with linting and security scanning. The skill being assessed is not whether the agent produces working code on the first try. It is whether you can evaluate, constrain, and direct the agent to reach a trustworthy outcome. This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a logged swap record**.

---

## Before You Start

**Estimated time:** Part 1 ~30 min | Part 2 ~45 min | Part 3 ~45 min | Part 4 ~30 min

### Prerequisite concepts

Before beginning, make sure you have completed both of the following activities (linked in the readings above):

- [Coding Agents Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-codingagents.md) — covers what a coding agent is, how it reads files, proposes edits, and accepts or rejects changes
- [The Local Agent Stack Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md) — covers how to run a local agent with a system prompt, how the agent loop works, and how to capture a trace

If you have not done both activities, do them now before reading further. The concepts introduced there are assumed throughout this lab.

### Install required tools

Run the following commands in your terminal to install the Python packages needed for Parts 2–4:

```bash
pip install openai anthropic flake8 bandit
```

Then install your coding agent. Choose one (or install both for the Extension Challenges):

**Claude Code:**
```bash
npm install -g @anthropic-ai/claude-code
```

**OpenCode:**
```bash
npm install -g opencode-ai
```

If `npm` is not available on your machine, install Node.js first from [https://nodejs.org](https://nodejs.org), then rerun the command above.

### Health-check: verify your setup

After installing, run each of the following commands and confirm you see the expected output before moving on.

```bash
flake8 --version
```

> Expected output (version numbers may differ):
> ```
> 7.1.1 (mccabe: 0.7.0, pycodestyle: 2.11.1, pyflakes: 3.2.0) CPython 3.11.9 on linux
> ```

```bash
bandit --version
```

> Expected output:
> ```
> bandit 1.7.9
>   python version = 3.11.9 (...)
> ```

**Claude Code:**
```bash
claude --version
```

> Expected output:
> ```
> claude-code/1.x.x
> ```

**OpenCode:**
```bash
opencode --version
```

> Expected output:
> ```
> opencode x.x.x
> ```

You also need an API key for whichever agent you are using. Set it as an environment variable:

```bash
# For Claude Code
export ANTHROPIC_API_KEY="sk-ant-..."

# For OpenCode (uses OpenAI by default)
export OPENAI_API_KEY="sk-..."
```

Add this line to your `~/.bashrc` or `~/.zshrc` so it persists across terminal sessions.

---

## Overview

In this lab you will write a specification for a `POST /search` REST API endpoint that queries a local in-memory knowledge base and returns summarized results. You will then hand that spec to a coding agent and watch it implement the feature. After the first run you will not accept the changes yet — instead you will read every line of the proposed diff, write a critique document that categorizes what the agent got right and wrong, and feed that critique back to the agent as a follow-up prompt. After the second run you will accept the final diff, run the agent's tests, add at least two tests the agent missed, and run both a linter and a security scanner. By the end you will have a complete picture of what coding agents can and cannot be trusted to do on their own.

---

## Part 1: Design First (Before Any Agent Interaction)

**Estimated time: ~30 minutes**

The single most important rule of this lab: **write the spec and the system prompt before you touch the agent.** Agents that receive a vague task produce vague code. Agents that receive no constraints violate them. You are designing the guardrails first.

### Step 1: Create the project directory

Create a fresh directory for this lab. All files you create in this lab go inside it.

```bash
mkdir cs357-coding-agents
cd cs357-coding-agents
```

Create the following empty files now so you know what you are building toward:

```bash
touch spec.md system_prompt.txt app.py test_app.py critique.md pair_log.md
```

### Step 2: Write the spec in `spec.md`

Open `spec.md` and fill in the template below. Every blank marked `[TODO]` must be completed before you run the agent. Do not skip any field — the agent will use this document as its task description.

```markdown
# Feature Spec: POST /search Endpoint

## Author(s)
[TODO: Your names]

## Date
[TODO: Today's date]

## Feature summary
A REST API endpoint that accepts a JSON search query and returns matching
entries from a local in-memory knowledge base.

## Function / route signature
- Method: POST
- Path: /search
- Framework: Flask (Python)
- Handler function name: search_knowledge_base

## Inputs
The request body must be valid JSON with the following fields:

| Field   | Type   | Required | Description                              |
|---------|--------|----------|------------------------------------------|
| query   | string | yes      | The search string (1–200 characters)     |
| max_results | int | no   | Max entries to return (default 5, max 20)|

## Outputs
On success (HTTP 200), return JSON:

```json
{
  "results": [
    { "id": "<string>", "title": "<string>", "snippet": "<string>" }
  ],
  "count": <int>,
  "query": "<string echoed back>"
}
```

## Error cases (all must be handled and tested)

| Condition                         | HTTP status | Error JSON key | Message                         |
|-----------------------------------|-------------|----------------|---------------------------------|
| `query` field missing             | 400         | error          | "query field is required"       |
| `query` is empty string           | 400         | error          | "query must not be empty"       |
| `query` exceeds 200 characters    | 400         | error          | "query exceeds maximum length"  |
| `max_results` is not a positive int | 400       | error          | "max_results must be a positive integer" |
| No entries match the query        | 200         | results        | Empty list, count 0             |
| Request body is not valid JSON    | 400         | error          | "request body must be valid JSON"|

## Knowledge base
The knowledge base is a Python list of dicts defined at module level in `app.py`.
It must contain at least 5 hardcoded entries, each with keys: id, title, body.
Matching is case-insensitive substring match on both title and body.
The snippet returned is the first 100 characters of the body.

## Testing criteria (the test suite must cover all of these)
1. Valid query that matches at least one entry returns HTTP 200 and correct fields
2. Valid query that matches no entries returns HTTP 200 with empty results list
3. Missing query field returns HTTP 400
4. Empty query string returns HTTP 400
5. Query longer than 200 characters returns HTTP 400
6. Non-positive max_results returns HTTP 400
7. Non-JSON body returns HTTP 400
8. max_results limits the number of returned results

## Files the agent may create or edit
- app.py
- test_app.py

## Files the agent must NOT touch
- spec.md
- system_prompt.txt
- critique.md
- pair_log.md
```

Save `spec.md`. Read through it once together and confirm every field is filled in.

### Step 3: Write the system prompt in `system_prompt.txt`

The system prompt is the set of instructions the agent reads before it sees the task. It defines the rules. Open `system_prompt.txt` and fill in the template below. Every `[TODO]` must be completed.

```text
You are a careful Python backend developer. Your job is to implement a
feature according to the spec provided. Follow these rules without exception.

## Allowed files
You may read and edit ONLY these files:
- app.py
- test_app.py

You must NOT read, edit, create, or delete any other file.

## Required libraries
- Flask (for the web framework)
- pytest (for tests)
- No other third-party libraries are permitted.

## Explicit prohibitions
1. Do NOT make any external network calls (no requests.get, urllib, httpx, etc.).
2. Do NOT hardcode any credentials, tokens, or API keys.
3. Do NOT use eval() or exec() anywhere in the code.
4. You MUST include unit tests in test_app.py that cover every error case in the spec.
5. Do NOT modify the knowledge base list after it is defined at module level.

## Code style
- All functions must have docstrings.
- Use type hints on all function signatures.
- Follow PEP 8.

## [TODO: Add at least one more constraint specific to your project]
[TODO: Write your additional constraint here, e.g., "All error responses must
use the same JSON schema" or "The search function must be extracted into its
own helper function separate from the Flask route handler."]

## Output
When you are done, print a one-paragraph summary of what you changed and why.
```

Save `system_prompt.txt`.

### ✅ Checkpoint 1 — Answer these questions before moving to Part 2

Write your answers in `pair_log.md` under a heading `## Checkpoint 1`.

1. Look at your spec's error case table. For each row, identify which HTTP status code you chose and explain in one sentence why that status code is semantically correct for that error.
2. Read your system prompt's prohibition list. For each prohibition, describe a specific thing the agent might do if that prohibition were not there. Be concrete — name a function or pattern the agent might reach for.
3. Your spec says the snippet is the first 100 characters of the body. What happens if a body is shorter than 100 characters? Write the expected behavior as a one-sentence addition to your spec, then add it to `spec.md`.

---

## Part 2: First Agent Run

**Estimated time: ~45 minutes**

You have a spec. You have a system prompt. Now you run the agent — and watch carefully.

### Step 1: Launch the coding agent

Make sure you are inside your `cs357-coding-agents` directory. Run the agent using the command for your chosen tool.

**Claude Code:**
```bash
claude --system-prompt "$(cat system_prompt.txt)" "$(cat spec.md)"
```

Or, to use the interactive mode where you can watch the agent work step by step:
```bash
claude
```
Then paste your system prompt when prompted, and paste the contents of `spec.md` as the task.

**OpenCode:**
```bash
opencode run --system "$(cat system_prompt.txt)" --task "$(cat spec.md)"
```

Or interactively:
```bash
opencode
```

### What you should see

> The agent will begin by reading existing files (it will likely read `app.py` and `test_app.py`, both of which are empty). It will then propose one or more file edits. For each edit, you will see a diff showing lines added (prefixed with `+`) and lines removed (prefixed with `-`). The agent may also print reasoning about what it is doing. **Do not accept any changes yet.** Your job right now is to watch, not approve.

### Step 2: Capture the agent trace

Before you do anything else, save the agent's full output to a file. If you ran the agent in a terminal, scroll up and copy everything, then paste it into a new file:

```bash
# If your agent supports output redirection (Claude Code example):
claude --system-prompt "$(cat system_prompt.txt)" "$(cat spec.md)" 2>&1 | tee agent_trace_1.txt
```

If you used interactive mode, copy the terminal output manually and save it to `agent_trace_1.txt`. This file is a required deliverable.

### Step 3: Save the raw diff without accepting

Most coding agents show you a diff before applying it. Save the proposed diff to a separate file:

```bash
# If using git, after the agent stages but before you commit:
git diff > diff_1.patch
```

If the agent does not use git, copy the proposed changes shown in the terminal and paste them into `diff_1.patch`. The file should look like this:

```diff
--- a/app.py
+++ b/app.py
@@ -0,0 +1,52 @@
+from flask import Flask, request, jsonify
+from typing import Any
+
+app = Flask(__name__)
+
+KNOWLEDGE_BASE = [
+    {"id": "1", "title": "Flask documentation", "body": "Flask is a micro web framework..."},
+    ...
+]
+
+def search_entries(query: str, max_results: int) -> list[dict[str, Any]]:
+    """Return knowledge base entries whose title or body contains the query."""
+    ...
```

> You should see two files modified: `app.py` (the implementation) and `test_app.py` (the tests). If the agent only produced one of these files, note that in `pair_log.md` — it may have violated the spec.

### Troubleshooting — Part 2

**Problem: `claude: command not found` or `opencode: command not found`**

The tool is not on your PATH. Try:
```bash
npx @anthropic-ai/claude-code --version
# or
npx opencode-ai --version
```
If that works, use `npx claude` instead of `claude` throughout this lab, or re-run the npm install with the `-g` flag and open a new terminal.

**Problem: `Error: ANTHROPIC_API_KEY is not set` (or equivalent)**

You need to export your API key. Run:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```
Then rerun the agent command. If you do not have an API key, ask your instructor — do not share or hardcode keys.

**Problem: The agent immediately edits a file you prohibited in the system prompt**

Do not accept the change. Note the violation in `pair_log.md` with the exact file name and the line in your system prompt that prohibits it. Then try again with a stronger prompt — rewrite the prohibition to include the exact file path and add the phrase "under no circumstances."

### ✅ Checkpoint 2 — Answer these questions before moving to Part 3

Write your answers in `pair_log.md` under a heading `## Checkpoint 2`.

1. Open `diff_1.patch`. Count the number of lines added and the number of lines removed. How many distinct functions did the agent define in `app.py`? List them by name.
2. Did the agent produce a `test_app.py` file? If so, list the test function names. If not, does that constitute a violation of your system prompt? Explain.
3. Without running the code yet, read the implementation the agent proposed for the error case where `query` is an empty string. Does the code handle that case? Cite the specific lines from the diff.

---

## Part 3: Diff Review and Critique

**Estimated time: ~45 minutes**

You have a diff. Now you read every line of it as though you were a senior engineer reviewing a colleague's pull request — except you need to be more skeptical than you would be with a human, because the agent has no stake in whether the code is correct, secure, or complete.

### Step 1: Read through the entire diff

Open `diff_1.patch` in your editor and go line by line. You are looking for four categories of finding:

- **Correct** — the agent did this right; it matches the spec and is sound
- **Incorrect / broken** — the agent got this wrong; it does not match the spec or will not work
- **Missing** — something the spec requires that the agent did not implement
- **Security risk** — a pattern that could be exploited or that violates a system prompt prohibition

### Step 2: Produce the critique document in `critique.md`

Open `critique.md` and fill in the template below. You must have at least one entry in each category. If you genuinely cannot find a security risk, look harder — common agent habits include using `eval()`, constructing SQL queries by string concatenation, returning raw exception messages to the client, or importing libraries your system prompt prohibited.

```markdown
# Critique Document

## Agent: [Claude Code | OpenCode — fill in which you used]
## Diff reviewed: diff_1.patch
## Reviewers: [Your names]
## Date: [Today's date]

---

## Category 1: Correct

List things the agent did correctly. Cite diff line numbers.

| Finding | Diff lines | Why it is correct |
|---------|-----------|-------------------|
| [TODO: e.g., "Returns HTTP 400 for missing query field"] | [TODO: line numbers] | [TODO: matches spec row 3] |
| [TODO] | [TODO] | [TODO] |

---

## Category 2: Incorrect / Broken

List things that are wrong or will not work as the spec requires.

| Finding | Diff lines | What the spec requires instead |
|---------|-----------|-------------------------------|
| [TODO: e.g., "max_results default is 10, not 5"] | [TODO] | [TODO: spec says default is 5] |
| [TODO] | [TODO] | [TODO] |

---

## Category 3: Missing

List spec requirements that are absent from the diff entirely.

| Missing requirement | Spec section | Impact if left out |
|--------------------|-------------|-------------------|
| [TODO: e.g., "No test for max_results limiting results"] | [TODO: Testing criteria #8] | [TODO: Spec requirement not verified] |
| [TODO] | [TODO] | [TODO] |

---

## Category 4: Security Risk

List patterns that could be exploited or that violate system prompt prohibitions.

| Finding | Diff lines | Risk description | Severity (Low / Med / High) |
|---------|-----------|-----------------|----------------------------|
| [TODO: e.g., "Exception message returned verbatim in error JSON"] | [TODO] | [TODO: Leaks internal stack trace to client] | [TODO] |
| [TODO] | [TODO] | [TODO] | [TODO] |

---

## System prompt compliance check

For each prohibition in your system_prompt.txt, state whether the agent complied.

| Prohibition | Complied? | Evidence (diff line or "not present in diff") |
|------------|-----------|----------------------------------------------|
| No external network calls | [TODO: Yes / No] | [TODO] |
| No hardcoded credentials | [TODO: Yes / No] | [TODO] |
| No eval() or exec() | [TODO: Yes / No] | [TODO] |
| Must include unit tests | [TODO: Yes / No] | [TODO] |
| [Your additional constraint] | [TODO: Yes / No] | [TODO] |
```

### Step 3: Write a follow-up prompt

Create a file called `followup_prompt.txt`. This prompt will be your second message to the agent. It should address every finding in Categories 2, 3, and 4 of your critique document. Be precise — tell the agent exactly what to fix and why.

A good follow-up prompt looks like this:

```text
Thank you for the initial implementation. I have reviewed the diff and found
the following issues that must be corrected before I can accept the changes:

1. [INCORRECT] The default for max_results is 10 in your implementation but
   the spec requires 5. Change the default value on line [X] of app.py.

2. [MISSING] There is no test for the case where max_results limits the
   number of returned results (spec testing criterion #8). Add a test named
   test_max_results_limit to test_app.py.

3. [SECURITY] The exception handler on line [X] returns str(e) in the JSON
   response. This leaks internal error details to the client. Replace it with
   a generic message: "an unexpected error occurred".

4. [TODO: Add one entry for each finding in your critique's Categories 2–4]

Do not change anything else. Do not touch spec.md, system_prompt.txt,
critique.md, or pair_log.md.
```

### Step 4: Run the second agent iteration

Run the agent again, this time using your follow-up prompt as the task:

**Claude Code:**
```bash
claude --system-prompt "$(cat system_prompt.txt)" "$(cat followup_prompt.txt)" 2>&1 | tee agent_trace_2.txt
```

**OpenCode:**
```bash
opencode run --system "$(cat system_prompt.txt)" --task "$(cat followup_prompt.txt)" 2>&1 | tee agent_trace_2.txt
```

Save the new diff:
```bash
git diff > diff_2.patch
```

### Step 5: Compare the two diffs

Open both `diff_1.patch` and `diff_2.patch` side by side. For each finding in your critique document, confirm whether the second diff addresses it. Add a column to each table in `critique.md`:

```markdown
| ... | Resolved in diff_2? (Yes / No / Partially) |
```

### Troubleshooting — Part 3

**Problem: The agent repeated the same mistakes in the second diff**

This usually means your follow-up prompt was not specific enough. Rewrite the relevant instruction with an explicit line number reference and the exact text the agent should produce. Then run a third iteration if needed — there is no penalty for a third pass, but document it.

**Problem: The agent fixed what you asked but introduced a new bug**

This is extremely common. Add the new bug to a new row in your critique document under the correct category, write another follow-up prompt entry for it, and note in `pair_log.md` that you needed a third iteration.

**Problem: The agent edited a file you prohibited in your system prompt**

Do not accept the edit to the prohibited file. Use your agent's undo/reject mechanism, or restore the file with:
```bash
git checkout -- spec.md   # replace with the prohibited filename
```
Document the violation in `critique.md` under "System prompt compliance check."

### ✅ Checkpoint 3 — Answer these questions before moving to Part 4

Write your answers in `pair_log.md` under a heading `## Checkpoint 3`.

1. Compare `diff_1.patch` and `diff_2.patch`. List every finding from your critique document and state whether it was resolved, partially resolved, or not resolved in `diff_2.patch`. If anything was not resolved, explain why in one sentence.
2. Did the agent introduce any new issues in the second diff that were not present in the first? If so, describe them.
3. Look at the follow-up prompt you wrote. Which instruction was most effective (the agent followed it precisely)? Which was least effective? What would you write differently?

---

## Part 4: Verification and Hardening

**Estimated time: ~30 minutes**

The agent's second diff is as good as you are going to get from it. Now you take over: accept the changes, verify the tests, add missing coverage, and run static analysis tools.

### Step 1: Accept the final diff

Apply the final diff to your working directory:

```bash
git apply diff_2.patch
```

If you were not using git staging, the files may already be in place — verify that `app.py` and `test_app.py` are non-empty:

```bash
wc -l app.py test_app.py
```

> Expected: both files should have more than 10 lines.

### Step 2: Run the agent-generated tests

Install Flask and pytest if needed, then run the tests:

```bash
pip install flask pytest
pytest test_app.py -v
```

> Expected output (all tests should pass):
> ```
> test_app.py::test_valid_query_returns_results PASSED
> test_app.py::test_query_with_no_matches PASSED
> test_app.py::test_missing_query_field PASSED
> ...
> X passed in 0.XXs
> ```

If any test fails, read the error message carefully. Do not edit `app.py` to make the test pass by cheating (e.g., hardcoding a return value) — fix the actual bug. Document any failing test in `pair_log.md` and describe what you changed to fix it.

Look at the tests that exist and compare them against the eight testing criteria in your `spec.md`. Make a checklist: which criteria are covered, and which are missing?

### Step 3: Add at least two missing tests

Open `test_app.py` and add two tests that the agent did not write. Use the starter template below as a guide. Replace every `[TODO]` with the actual test logic.

```python
def test_max_results_limit(client):
    """Verify that max_results limits the number of entries returned."""
    # TODO: Send a POST request with a query that would match more than 2 entries
    # and max_results set to 2. Assert that the response contains exactly 2 results.
    response = client.post(
        "/search",
        json={"query": "[TODO: a term that matches many entries]", "max_results": 2},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["results"]) == 2  # TODO: confirm this is the right assertion


def test_query_echoed_in_response(client):
    """Verify that the response echoes back the original query string."""
    # TODO: Send a POST request with a specific query string.
    # Assert that data["query"] equals the string you sent.
    response = client.post(
        "/search",
        json={"query": "[TODO: your test query]"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["query"] == "[TODO: the same query string]"
```

After adding your tests, run pytest again and confirm all tests still pass:

```bash
pytest test_app.py -v
```

Save the full pytest output to a file:
```bash
pytest test_app.py -v > test_output.txt 2>&1
```

### Step 4: Run the flake8 linter

```bash
flake8 app.py test_app.py
```

> If the code passes with no issues, flake8 produces no output and exits with code 0:
> ```
> (no output)
> ```
>
> If there are style issues, you will see output like:
> ```
> app.py:14:1: E302 expected 2 blank lines, got 1
> app.py:23:80: E501 line too long (84 > 79 characters)
> test_app.py:8:5: W291 trailing whitespace
> ```

Fix any errors or warnings that flake8 reports. Then rerun until it exits cleanly. Save the final (clean) output:

```bash
flake8 app.py test_app.py > flake8_output.txt 2>&1; echo "Exit code: $?" >> flake8_output.txt
```

### Step 5: Run the bandit security scanner

```bash
bandit -r app.py
```

> Bandit output looks like this:
> ```
> [main]  INFO    profile include tests: None
> [main]  INFO    profile exclude tests: None
> [main]  INFO    cli include tests: None
> [main]  INFO    cli exclude tests: None
> Run started: 2026-06-21 ...
>
> Test results:
>         No issues identified.
>
> Code scanned:
>         Total lines of code: 52
>         Total lines skipped (#nosec): 0
>
> Run metrics:
>         Total issues (by severity):
>                 Undefined: 0
>                 Low: 0
>                 Medium: 0
>                 High: 0
>         Total issues (by confidence):
>                 Undefined: 0
>                 Low: 0
>                 Medium: 0
>                 High: 0
> Files skipped (0):
> ```
>
> If bandit finds issues, you will see entries like:
> ```
> >> Issue: [B110:try_except_pass] Try, Except, Pass detected.
>    Severity: Low   Confidence: High
>    CWE: CWE-390 (https://cwe.mitre.org/data/definitions/390.html)
>    Location: app.py:31:4
> ```

Save the bandit output:
```bash
bandit -r app.py > bandit_output.txt 2>&1
```

### Step 6: Address any high-severity findings

Read the bandit output. For each finding with **Severity: High** or **Severity: Medium**, you must fix the underlying issue in `app.py`. Do not use `# nosec` comments to silence findings without first understanding what they mean — if you disagree with a finding, document your reasoning in `pair_log.md` under a heading `## Security scanner findings`.

After any fixes, rerun both flake8 and bandit to confirm the fixes did not introduce new issues.

### Troubleshooting — Part 4

**Problem: `ModuleNotFoundError: No module named 'flask'` when running pytest**

```bash
pip install flask
```
Then rerun pytest. If you are in a virtual environment, make sure it is activated.

**Problem: `ERRORS` in pytest output — a test raises an exception instead of failing cleanly**

Read the traceback. If it says `fixture 'client' not found`, the agent did not create a pytest fixture for the Flask test client. Add one manually at the top of `test_app.py`:

```python
import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client
```

**Problem: bandit reports `[B201:flask_debug_true]` — Flask app running in debug mode**

Check `app.py` for a line like `app.run(debug=True)`. Change `debug=True` to `debug=False`, or remove the `app.run()` call entirely if it is inside an `if __name__ == "__main__":` block that is not needed for testing.

### ✅ Checkpoint 4 — Answer these questions as part of your reflection

Write your answers in `pair_log.md` under a heading `## Checkpoint 4`.

1. How many of the eight spec testing criteria were covered by the agent's tests before you added your two? List which were covered and which were not.
2. Did flake8 find any issues that were not stylistic — that is, issues that indicated an actual logic problem or bad practice beyond formatting? If so, describe them.
3. Did bandit flag anything? If yes, describe the finding and what you changed. If no, explain in one sentence what bandit would have flagged if the agent had used `eval()` to parse the query string.

---

## Deliverables

Submit a single ZIP file named `LASTNAME1_LASTNAME2_CodingAgents.zip` containing all of the following. Missing files will result in point deductions from the corresponding rubric category.

| File | Description |
|------|-------------|
| `spec.md` | Your completed feature specification |
| `system_prompt.txt` | Your system prompt with all TODOs filled in |
| `app.py` | The final accepted implementation |
| `test_app.py` | The final test file including your two added tests |
| `diff_1.patch` | The raw diff from the first agent run |
| `diff_1_annotated.patch` | The same diff with inline comments explaining each significant change (add `# COMMENT:` lines) |
| `critique.md` | Your completed critique document with the "Resolved in diff_2?" column filled in |
| `followup_prompt.txt` | The follow-up prompt you sent for the second iteration |
| `diff_2.patch` | The raw diff from the second agent run |
| `agent_trace_1.txt` | Full terminal output from the first agent run |
| `agent_trace_2.txt` | Full terminal output from the second agent run |
| `test_output.txt` | pytest output showing all tests passing |
| `flake8_output.txt` | flake8 output (clean or with documented fixes) |
| `bandit_output.txt` | bandit output (clean or with documented resolutions) |
| `pair_log.md` | Swap log with timestamps, all checkpoint answers, and security scanner findings section |

---

## Extension Challenges

These challenges are optional and will not affect your grade on the base rubric. They are progressively harder and are intended for pairs who finish early or want to go deeper.

### Challenge 1: Deliberate ambiguity

Add one deliberately contradictory requirement to a copy of your spec — for example, "The endpoint must return results sorted alphabetically by title" combined with "The endpoint must return results in the order they appear in the knowledge base." Give this contradictory spec to the coding agent without any hint about the contradiction. Document exactly what the agent does: does it pick one interpretation silently, ask for clarification, implement both with a flag, or do something else? Write a one-paragraph analysis of what the agent's choice reveals about how it handles underspecified instructions.

### Challenge 2: Two agents, one spec

Install both Claude Code and OpenCode (if you only have one, pair with another group that has the other). Run both agents on exactly the same `spec.md` and `system_prompt.txt`, in separate directories so they cannot influence each other. Compare the two `diff_1.patch` files. Answer: How do the implementations differ structurally? Which agent's tests were more complete? Did one agent violate a system prompt constraint that the other respected? Produce a side-by-side comparison table with at least five dimensions.

### Challenge 3: Automated constraint violation harness

Write a Python script called `harness.py` that runs the coding agent multiple times with system prompts of varying strictness (you define three levels: minimal, moderate, strict) and, after each run, checks the resulting `app.py` for the presence of prohibited patterns using regex or AST inspection. For example, check whether `eval` appears, whether any `import` of a prohibited library appears, or whether any function is missing a docstring. Record the violation rate for each prompt level and produce a summary table. This gives you empirical data on how much system prompt strength actually changes agent behavior.

---

## Reflection Prompts

Answer each prompt in `pair_log.md` under a heading `## Reflection`. Write at least three to five sentences per prompt — one-sentence answers will not receive full credit.

1. **What did the coding agent do well that surprised you?** Describe a specific part of the implementation where the agent made a better choice than you expected, and explain what that reveals about what these models are trained on.

2. **Where did it make assumptions you had not anticipated, and how did those assumptions affect the output?** Give at least two concrete examples. For each, explain whether the assumption was reasonable given the spec, and what you would add to the spec or system prompt to prevent that assumption in the future.

3. **How did your system prompt constrain its behavior — and what slipped through the constraints anyway?** For each prohibition in your system prompt, state whether the agent complied on the first run. For anything that slipped through, propose a more precise formulation of the prohibition.

4. **Would you trust this code in production? What specifically would need to change before you would?** Think about more than just tests — consider rate limiting, input sanitization depth, error logging, deployment configuration, and dependency management. List at least four specific changes and explain the risk each one addresses.

5. **How does reviewing a coding agent's diff differ from reviewing a human colleague's pull request? What additional skepticism is warranted, and why?** Think about what you know about a human colleague that you do not know about the agent: their understanding of business context, their ability to ask clarifying questions, their stake in the outcome, and their track record. How do those differences change how you read a diff?

6. **If you were deploying this pattern at scale — hundreds of developers using coding agents daily — what organizational controls (beyond individual system prompts) would you want in place?** Consider: who approves system prompts before they are used? How do you audit what agents actually do versus what they are told to do? What happens when an agent produces code that passes all tests but is subtly wrong in a way tests do not catch? Name at least three concrete organizational controls and explain the failure mode each one addresses.

7. **If collaboration beyond your pair occurred, identify it.** Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.

8. **Approximately how many hours did this lab take** (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
