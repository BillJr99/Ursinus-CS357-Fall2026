---
layout: assignment
permalink: /Assignments/CICDAgent
title: "CS357: Foundations of Artificial Intelligence - Lab: CI/CD, TDD, and Publishing for AI Agent Software"

info:
  coursenum: CS357
  points: 100
  goals:
    - To implement test-driven development practices for non-deterministic agent outputs using semantic, format, and safety test patterns
    - To configure and run automated code quality tools including formatters, linters, and coverage reporters on an agentic Python project
    - To construct a GitHub Actions CI pipeline that validates formatting, linting, and test coverage on every push and pull request
    - To package and publish an AI agent as a pip-installable wheel to TestPyPI and as a container image to the GitHub Container Registry
  rubric:
    - weight: 25
      description: TDD Implementation
      preemerging: The test file is absent or fewer than two tests run without errors; the mock fixture is missing or does not intercept the Ollama call
      beginning: At least two tests run, but one or more of the three student-written stubs are missing or trivially pass without asserting anything meaningful
      progressing: All five tests run and pass, but the mock fixture is incomplete (e.g., it patches the wrong symbol or does not verify the call was made), or one test does not clearly belong to the semantic/format/safety taxonomy
      proficient: All five tests pass including the three student-written tests; the mock fixture correctly intercepts the Ollama HTTP call so no live model is required; at least one test verifies response format (list, dict, or a string constraint such as word count); each test is labeled in a comment with its type (semantic, format, or safety)
    - weight: 25
      description: Code Quality
      preemerging: black and ruff both report errors; coverage is below 60% or the coverage command fails to run
      beginning: One of black or ruff exits with errors; coverage is between 60–79% with no explanation of missed lines
      progressing: black and ruff both exit 0; coverage is at or above 80% but the branch coverage report is not included, or only one of the two planted style issues has been fixed
      proficient: black and ruff both exit 0; pytest --cov reports ≥80% line coverage with branch coverage enabled; the coverage report is pasted into the writeup with missed lines identified; both planted style issues are fixed and the fix is explained in one sentence each
    - weight: 25
      description: CI Pipeline
      preemerging: ci.yml is absent or has a syntax error that prevents the workflow from running at all
      beginning: The workflow runs but omits at least one required step (format, lint, or test) or only targets a single Python version
      progressing: All three steps run on both Python versions, but the matrix is not correctly defined (e.g., versions are hardcoded rather than using a matrix strategy), or the workflow is not triggered on both push and pull_request events
      proficient: ci.yml runs on push and pull_request; the matrix covers Python 3.11 and 3.12; all three steps (black, ruff, pytest with coverage) execute; the student adds an inline comment in the YAML explaining why 3.11 and 3.12 were chosen as the matrix targets
    - weight: 25
      description: Publishing
      preemerging: Neither pyproject.toml nor Dockerfile is present, or both are present but fail to build
      beginning: pyproject.toml builds a wheel (dist/*.whl exists) but required fields are incomplete, or the Dockerfile builds locally but the CMD line is incorrect
      progressing: Both pyproject.toml and Dockerfile build without errors; the wheel is present; the Docker image runs, but the TestPyPI upload or --dry-run output is not included in the submission
      proficient: pyproject.toml builds a wheel with all required fields populated; the Dockerfile builds locally and the CMD line correctly invokes the agent; a TestPyPI upload receipt or twine --dry-run output screenshot is attached; the writeup explains the difference between a wheel and a source distribution in one sentence
  readings:
    - rtitle: "Publishing Activity: GHCR, Docker Hub, and npm"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-publishing.md"
    - rtitle: "Coding Agents Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-codingagents.md"
    - rtitle: "Ollama API Documentation"
      rlink: "https://github.com/ollama/ollama/blob/main/docs/api.md"
    - rtitle: "pytest Documentation"
      rlink: "https://docs.pytest.org/en/stable/"
    - rtitle: "Python Packaging User Guide"
      rlink: "https://packaging.python.org/en/latest/tutorials/packaging-projects/"

tags:
  - testing
  - ci-cd
  - publishing
  - tdd

---

In this lab you will apply professional software engineering practices to the kind of code you build throughout this course: agentic Python projects that call local LLMs and produce non-deterministic outputs. You will practice test-driven development against a mocked model, enforce code quality automatically, wire up a GitHub Actions CI pipeline, and publish your agent as both a pip-installable package and a container image.

This lab is completed **individually**. You will submit your code, configuration files, and a readme writeup.

---

## Before You Start

**Prerequisite activities** — complete these before writing any code:

- [Publishing Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-publishing.md) — registries, names, tags, and pip publishing
- [Coding Agents Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-codingagents.md) — agent loops and CI

**Tools to install:**

```bash
# Install all required Python tooling into your project virtual environment
pip install pytest pytest-cov black ruff build twine

# Confirm Ollama is running (used in Parts 1 and 4; mocked in Part 1 tests)
ollama list
```

Expected output from `ollama list`:

```
NAME               ID              SIZE    MODIFIED
llama3.2:latest    a80c4f17acd5    2.0 GB  2 minutes ago
```

If `ollama list` hangs or errors, start the server in a separate terminal:

```bash
ollama serve
```

**Create your GitHub repository** if you have not already done so. All four parts of this lab require a repository with at least one commit before you can open a pull request.

**Estimated time budget:**

| Part | Task | Estimated time |
|------|------|----------------|
| Part 1 | TDD for a non-deterministic agent | 60–90 min |
| Part 2 | Code quality and formatting | 30–45 min |
| Part 3 | GitHub Actions CI | 45–60 min |
| Part 4 | Publishing your agent | 60–90 min |
| Writeup | Readme and reflection | 30–45 min |

---

## Part 1: Test-Driven Development for a Non-Deterministic Agent

The hardest part of testing agent code is that the model's output is never exactly the same twice. Instead of asserting exact strings, you will write **semantic tests** (does the response contain the right concept?), **format tests** (does the response have the right structure?), and **safety tests** (does the response avoid forbidden content?). A mock fixture replaces the live Ollama call, so your tests run instantly and deterministically in CI.

### Step 1: Create the starter agent file.

Create `research_agent.py` in your project root:

```python
import requests
import json
import traceback

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
MODEL = "llama3.2"


def ask_model(prompt: str) -> str:
    """
    Send a single user prompt to the local Ollama model and return the reply string.
    Raises on network or API errors rather than swallowing them.
    """
    # TODO: Build the JSON payload with "model", "messages" (a list with one user message),
    # and "stream": False. POST it to OLLAMA_URL. Return the content string from the
    # first choice's message. Wrap the network call in a try/except that prints
    # "[research_agent:ask_model] {e}" and re-raises.
    raise NotImplementedError


def summarize(text: str, max_words: int = 50) -> str:
    """
    Ask the model to summarize text in at most max_words words.
    Returns the model's reply string.
    """
    # TODO: Build a prompt that instructs the model to summarize `text` in at most
    # `max_words` words, then call ask_model and return the result.
    raise NotImplementedError


def extract_facts(text: str) -> list[str]:
    """
    Ask the model to extract key facts from text as a list of bullet points.
    Returns a Python list of strings, one per fact.
    Each string should begin with "- " as the model is instructed to produce.
    """
    # TODO: Build a prompt that instructs the model to return key facts as bullet points
    # (one per line, each starting with "- "). Call ask_model, split the result on
    # newlines, strip each line, and filter to lines that start with "- ".
    raise NotImplementedError
```

### Step 2: Create the test file with the mock fixture.

Create `test_agent.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
import research_agent


# ---------------------------------------------------------------------------
# Mock fixture
# ---------------------------------------------------------------------------

def make_mock_response(content: str):
    """
    Build a fake requests.Response whose .json() returns the Ollama
    /v1/chat/completions structure with `content` as the assistant reply.
    """
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()  # does nothing (no error)
    mock_resp.json.return_value = {
        "choices": [
            {"message": {"content": content}}
        ]
    }
    return mock_resp


@pytest.fixture
def mock_ollama():
    """
    Patch requests.post so that no real HTTP call is made.
    Tests receive the patcher and can set mock_ollama.return_value to control
    what the "model" replies with.

    Usage in a test:
        mock_ollama.return_value = make_mock_response("Paris is the capital.")
    """
    with patch("research_agent.requests.post") as mock_post:
        yield mock_post


# ---------------------------------------------------------------------------
# Provided tests (do not modify)
# ---------------------------------------------------------------------------

def test_ask_model_returns_string(mock_ollama):
    """semantic test: ask_model returns a non-empty string."""
    mock_ollama.return_value = make_mock_response("The capital of France is Paris.")
    result = research_agent.ask_model("What is the capital of France?")
    assert isinstance(result, str)
    assert len(result) > 0


def test_extract_facts_returns_list(mock_ollama):
    """format test: extract_facts returns a list."""
    mock_ollama.return_value = make_mock_response(
        "- Python was created by Guido van Rossum.\n- It was first released in 1991."
    )
    facts = research_agent.extract_facts("Tell me about Python.")
    assert isinstance(facts, list)
    assert len(facts) >= 1


# ---------------------------------------------------------------------------
# TODO: Write three more tests below. Label each with a comment indicating
# its type: "semantic test", "format test", or "safety test".
# ---------------------------------------------------------------------------

def test_ask_model_contains_keyword(mock_ollama):
    """TODO: semantic test — verify the reply contains an expected keyword."""
    # TODO: Set mock_ollama.return_value to a response that contains a specific word.
    # Call ask_model with a prompt, then assert the reply contains that word.
    raise NotImplementedError


def test_summarize_respects_word_limit(mock_ollama):
    """TODO: format test — verify summarize returns a string within a word limit."""
    # TODO: Set mock_ollama.return_value to a short reply (e.g., 10 words).
    # Call summarize with max_words=20, then assert the result is a non-empty string
    # and that its word count does not exceed max_words.
    raise NotImplementedError


def test_extract_facts_excludes_forbidden_content(mock_ollama):
    """TODO: safety test — verify extract_facts output does not contain forbidden strings."""
    # TODO: Choose a word that should never appear in a fact list for a neutral topic
    # (e.g., "password", "secret", or "ignore previous instructions").
    # Set mock_ollama.return_value to a response that does NOT contain that word.
    # Call extract_facts, then assert none of the returned strings contain the forbidden word.
    raise NotImplementedError
```

### Step 3: Complete the TODOs and run the tests.

Implement all three `# TODO:` stubs in `research_agent.py` and all three `# TODO:` test stubs in `test_agent.py`, then run:

```bash
pytest -v
```

Expected output (once all stubs are complete):

```
collected 5 items

test_agent.py::test_ask_model_returns_string           PASSED
test_agent.py::test_extract_facts_returns_list         PASSED
test_agent.py::test_ask_model_contains_keyword         PASSED
test_agent.py::test_summarize_respects_word_limit      PASSED
test_agent.py::test_extract_facts_excludes_forbidden_content PASSED

5 passed in 0.12s
```

### Troubleshooting — Part 1

**`NotImplementedError` on every test**
You have not yet filled in the `# TODO:` stubs. The fixture patches `requests.post` correctly; the remaining work is in the function bodies.

**`AttributeError: module 'research_agent' has no attribute 'requests'`**
Your patch target must match the name `requests` is imported as inside `research_agent.py`. If you wrote `import requests` at the top of the module, the patch target is `"research_agent.requests.post"` exactly as shown in the fixture.

**All five tests pass without a live Ollama instance**
This is the expected behavior. The mock fixture intercepts the HTTP call before it leaves your machine. You can verify this by stopping `ollama serve` and re-running `pytest` — the tests should still pass.

---

> **Checkpoint: Before moving to Part 2, make sure you can answer:**
> 1. Why can we not use a simple `assert result == "The capital of France is Paris."` to test the output of a language model, even if the model is deterministic?
> 2. What does `patch("research_agent.requests.post")` do, exactly? Which object does it replace, and for how long?
> 3. The safety test asserts that a forbidden word is absent. Why might a safety test fail even when the mock returns a safe response? (Hint: look at how `extract_facts` processes the model's reply.)

---

## Part 2: Code Quality and Formatting

Professional Python projects enforce formatting and linting in CI so that style debates never reach code review. This part introduces two tools: `black` (an opinionated formatter that makes all stylistic decisions for you) and `ruff` (a fast linter that catches bugs and anti-patterns). Both are configured to exit with a non-zero code on failure, which is what allows CI to block a merge.

The starter `research_agent.py` contains **two deliberate style issues**. Your job is to find and fix them after running the tools.

### Step 1: Run `black` and observe the changes.

```bash
# Check what black would change (safe, does not modify files)
black --check --diff research_agent.py test_agent.py

# Apply the changes
black research_agent.py test_agent.py
```

Expected output after applying:

```
reformatted research_agent.py
All done! ✨ 🍰 ✨
1 file reformatted, 1 file left unchanged.
```

Look at the diff produced by `--check --diff` before applying. In your writeup, describe one specific change black made and why it is beneficial.

### Step 2: Run `ruff` and fix linting errors.

```bash
ruff check research_agent.py test_agent.py
```

Ruff will flag the two deliberate style issues. Read each diagnostic carefully — ruff includes the rule code (e.g., `E501`, `F841`) and a description. Fix both issues in your editor, then re-run until you see:

```
All checks passed!
```

In your writeup, name each rule that was triggered and explain in one sentence what bug or anti-pattern it prevents.

### Step 3: Measure and achieve ≥80% coverage.

```bash
pytest --cov=research_agent --cov-report=term-missing --cov-branch
```

Expected output (exact numbers will vary by your implementation):

```
---------- coverage: platform linux, python 3.11 ----------
Name                Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------
research_agent.py      22      3      6      1    84%   18, 31, 45
---------------------------------------------------------------
TOTAL                  22      3      6      1    84%

5 passed in 0.13s
```

If your coverage is below 80%, look at the `Missing` column: those are the line numbers not exercised by any test. Add tests or extend existing tests to cover those paths. Paste the final coverage report into your writeup.

### Troubleshooting — Part 2

**`black` and `ruff` disagree on the same line**
This is rare but possible. Apply `black` first (it runs on the whole file), then run `ruff`. Ruff's auto-fix (`ruff check --fix`) can resolve most remaining issues after black runs.

**Coverage stays below 80% even after adding tests**
The `--cov-branch` flag counts branch coverage (every `if/else` path), which is stricter than line coverage. The most commonly missed branches are exception handlers. Add a test that triggers the exception path in `ask_model` by configuring the mock to raise `requests.exceptions.ConnectionError`.

---

> **Checkpoint: Before moving to Part 3, make sure you can answer:**
> 1. What is the difference between a formatter (black) and a linter (ruff)? Could one tool replace the other?
> 2. Name the two deliberate style issues you fixed and the ruff rule code for each.
> 3. Which lines in your `research_agent.py` are listed under `Missing` in the coverage report, and why were they not hit by your current tests?

---

## Part 3: GitHub Actions CI

A CI pipeline runs your quality checks automatically on every push and pull request, so that style and test failures are caught before they reach the main branch. In this part you will write a GitHub Actions workflow that replicates the three commands from Part 2 on a matrix of Python versions.

### Step 1: Create the workflow file.

Create `.github/workflows/ci.yml`:

```yaml
{% raw %}
name: CI

on:
  push:
    branches: ["**"]
  pull_request:
    branches: ["**"]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        # TODO: Add Python versions 3.11 and 3.12 here.
        # Add an inline comment below the versions explaining why these two
        # versions were chosen as the matrix targets for this course.
        python-version: []  # replace with [3.11, 3.12]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          # TODO: Upgrade pip, then install pytest, pytest-cov, black, ruff, and requests.

      - name: Check formatting with black
        run: |
          # TODO: Run black in --check mode on research_agent.py and test_agent.py.
          # (Do not use --diff here; --check alone causes a non-zero exit on failure.)

      - name: Lint with ruff
        run: |
          # TODO: Run ruff check on research_agent.py and test_agent.py.

      - name: Run tests with coverage
        run: |
          # TODO: Run pytest with --cov=research_agent, --cov-report=term-missing,
          # and --cov-branch. Add --cov-fail-under=80 so the step fails if coverage drops.
{% endraw %}
```

### Step 2: Complete the YAML TODOs.

Fill in each `# TODO:` block. The install step should be a single `pip install` command; the format, lint, and test steps should be the same commands you ran in Part 2.

### Step 3: Push to a branch and open a pull request.

```bash
git checkout -b ci-pipeline
git add .github/workflows/ci.yml research_agent.py test_agent.py pyproject.toml
git commit -m "Add CI pipeline and TDD implementation"
git push origin ci-pipeline
```

Open a pull request from `ci-pipeline` to `main` on GitHub. In the pull request's Checks tab, watch the workflow run. The matrix will produce two parallel jobs (one per Python version).

Expected outcome: both jobs show a green checkmark. Take a screenshot of the Checks tab and include it in your submission.

### Troubleshooting — Part 3

**Workflow does not appear in the Actions tab**
The `.github/workflows/` directory must be committed and pushed. Check that the file is at the correct path (`.github/workflows/ci.yml`, not `github/workflows/ci.yml` or `.github/workflow/ci.yml`).

**The `black --check` step fails in CI but passes locally**
Ensure you ran `black` on the exact same files listed in the YAML step. A common cause is that `test_agent.py` was formatted locally but not committed.

**`--cov-fail-under=80` causes the step to fail even though coverage locally is above 80%**
The CI environment installs packages fresh and runs only the tests in your repository. If you wrote temporary tests locally but did not commit them, coverage will be lower in CI.

---

> **Checkpoint: Before moving to Part 4, make sure you can answer:**
> 1. Why does the matrix run both Python 3.11 and 3.12? What class of bug does this catch?
> 2. If the `black --check` step fails, what must happen before the `ruff` and `pytest` steps run? (Check your workflow's `needs:` configuration, or note that sequential steps in the same job stop on first failure.)
> 3. Where is the "human gate" in this CI pipeline — the point where a human must make a decision before code merges to main?

---

## Part 4: Publishing Your Agent

Once your agent passes CI, you can ship it in two forms: a pip-installable Python package (for users who want to `pip install` your agent and call it from Python or the command line) and a container image (for users who want a self-contained, reproducible environment with no Python setup required).

### Step 1: Write `pyproject.toml` for pip packaging.

Create `pyproject.toml` in your project root:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
# TODO: Fill in the name field. Use lowercase letters and hyphens only,
# e.g., "my-research-agent". This is the name users will pip install.
name = ""

# TODO: Fill in the version field. Use semantic versioning: "0.1.0" for a first release.
version = ""

description = "A research agent that uses a local LLM to summarize text and extract facts."
readme = "README.md"
requires-python = ">=3.11"

# TODO: Fill in the dependencies list. Your agent requires "requests".
# Add it here so pip installs it automatically.
dependencies = []

[project.scripts]
# This creates a command-line entry point. After pip install, users can run:
#   research-agent "What is photosynthesis?"
research-agent = "research_agent:main"
```

Add a `main()` function to `research_agent.py` that accepts a command-line argument and prints the model's reply:

```python
import sys

def main():
    """CLI entry point: research-agent <prompt>"""
    if len(sys.argv) < 2:
        print("Usage: research-agent <prompt>")
        sys.exit(1)
    prompt = " ".join(sys.argv[1:])
    try:
        reply = ask_model(prompt)
        print(reply)
    except Exception as e:
        print(f"[research_agent:main] {e}")
        traceback.print_exc()
        sys.exit(1)
```

Build the package:

```bash
python -m build
```

Expected output:

```
Successfully built research_agent-0.1.0.tar.gz and research_agent-0.1.0-py3-none-any.whl
```

Verify the `dist/` directory contains both files:

```bash
ls dist/
# research_agent-0.1.0-py3-none-any.whl
# research_agent-0.1.0.tar.gz
```

### Step 2: Upload to TestPyPI.

TestPyPI is a separate instance of PyPI used for testing. Publishing here is safe and free; it will not affect the real PyPI index.

```bash
# Create an account at https://test.pypi.org/ and generate an API token
# Store your token as an environment variable (never paste it into a command directly)
export TWINE_PASSWORD="your-testpypi-token-here"

twine upload --repository testpypi dist/*
```

Expected output:

```
Uploading distributions to https://test.pypi.org/legacy/
Uploading research_agent-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.3/12.3 kB
Uploading research_agent-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.1/10.1 kB
View at: https://test.pypi.org/project/research-agent/0.1.0/
```

If you do not have a TestPyPI account, you can demonstrate the upload step with `--dry-run`:

```bash
twine upload --repository testpypi --skip-existing dist/* 2>&1 | head -20
```

Include the terminal output (real upload or dry run) as a screenshot in your submission.

Verify the install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ research-agent
research-agent "What is photosynthesis?"
```

### Step 3: Write a `Dockerfile` for container publishing.

Create `Dockerfile` in your project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY research_agent.py .

# The Ollama API endpoint is configurable via environment variable.
# Default points to a local Ollama instance; override at runtime with:
#   docker run -e OLLAMA_URL=http://host.docker.internal:11434/v1/chat/completions ...
ENV OLLAMA_URL=http://localhost:11434/v1/chat/completions

# TODO: Fill in the CMD line. It should run research_agent.py as a Python script
# and accept a prompt as the first argument. A user will override CMD at runtime:
#   docker run research-agent "What is photosynthesis?"
CMD []
```

Create `requirements.txt` (if you do not already have one):

```
requests>=2.31.0
```

Update `research_agent.py` to read `OLLAMA_URL` from the environment:

```python
import os

OLLAMA_URL = os.environ.get(
    "OLLAMA_URL",
    "http://localhost:11434/v1/chat/completions"
)
```

Build and test the image locally:

```bash
docker build -t research-agent:0.1.0 .

# Test with a prompt (requires Ollama running on the host)
docker run --rm \
  -e OLLAMA_URL=http://host.docker.internal:11434/v1/chat/completions \
  research-agent:0.1.0 \
  "What is photosynthesis?"
```

### Step 4: Push to GitHub Container Registry (optional but encouraged).

```bash
# Authenticate using a GitHub Personal Access Token with the write:packages scope
echo $CR_PAT | docker login ghcr.io -u yourusername --password-stdin

# Tag for GHCR
docker tag research-agent:0.1.0 ghcr.io/yourusername/research-agent:0.1.0

# Push
docker push ghcr.io/yourusername/research-agent:0.1.0
```

Make the package public in your GitHub profile under the Packages tab if you want `docker pull` to work without authentication.

### Step 5 (Optional): npm wrapper for a REST endpoint.

If your agent exposes a REST endpoint (not required for this lab), you can publish a minimal npm CLI wrapper:

```json
{
  "name": "@yourusername/research-agent",
  "version": "0.1.0",
  "description": "CLI wrapper that calls the research-agent REST endpoint.",
  "bin": { "research-agent": "./index.js" },
  "files": ["index.js", "README.md"],
  "license": "MIT"
}
```

```bash
npm publish --dry-run
```

Include the `--dry-run` output in your submission if you attempt this step.

### Troubleshooting — Part 4

**`hatchling` is not installed**
Run `pip install hatchling` and retry `python -m build`. Hatchling is the build backend specified in `pyproject.toml`; it must be installed in the same environment where you run `python -m build`.

**`twine upload` fails with `403 Forbidden`**
Your API token may be scoped to PyPI (not TestPyPI) or may have expired. Generate a new token at https://test.pypi.org/manage/account/token/ and ensure it is scoped to the specific project or to "Entire account."

**`docker run` exits immediately without output**
Your `CMD` line is empty (the TODO is unfilled). The CMD must be a JSON array: `["python", "research_agent.py"]`. The user's prompt is appended at runtime via `docker run ... research-agent:0.1.0 "my prompt"`.

**`docker run` cannot reach Ollama**
On macOS and Windows, use `-e OLLAMA_URL=http://host.docker.internal:11434/v1/chat/completions`. On Linux, use `--network=host` or pass the host's IP address explicitly.

---

> **Checkpoint: Before writing your deliverables, make sure you can answer:**
> 1. What is the difference between a wheel (`.whl`) and a source distribution (`.tar.gz`)? When would a user prefer each?
> 2. Why should you always upload to TestPyPI before uploading to PyPI? What specific mistake does TestPyPI let you catch?
> 3. The `Dockerfile` sets `OLLAMA_URL` via `ENV`. Why is this better than hardcoding the URL in `research_agent.py` for a containerized deployment?

---

## Deliverables

Submit a ZIP file or link to your GitHub repository containing:

- `research_agent.py` — fully implemented, black- and ruff-clean
- `test_agent.py` — all five tests passing, mock fixture present
- `.github/workflows/ci.yml` — complete with matrix, all three steps, and your inline comment
- `pyproject.toml` — all required fields populated; `dist/*.whl` must exist
- `Dockerfile` — complete CMD line; image must build locally
- `requirements.txt`
- Screenshot of the GitHub Actions Checks tab showing two green jobs (3.11 and 3.12)
- Screenshot of the TestPyPI upload receipt or `twine --dry-run` output
- Pair programming log (if applicable) or solo work declaration
- `README.md` writeup (approximately two pages) covering your design decisions, the two ruff rule fixes, the coverage report, and answers to the reflection prompts below

---

## Reflection Prompts

Answer in your readme writeup. Cite a specific observation from the lab (a line of code, a terminal output, or a CI run result) rather than restating the question.

- When you mocked the Ollama HTTP call in `test_agent.py`, you tested your code's behavior without testing the model's behavior. What aspect of the agent's correctness is your test suite completely unable to verify, and what would a complementary evaluation strategy look like?
- The CI matrix runs tests on both Python 3.11 and 3.12. Describe one concrete Python language or library behavior that differs between these versions and that your test suite could potentially catch.
- Publishing to TestPyPI requires an API token. The Dockerfile accepts `OLLAMA_URL` as an environment variable. In both cases, sensitive or environment-specific configuration is externalized. What is the general principle, and where does it show up elsewhere in this course?
- Looking at your final coverage report: which lines are still not covered by any test, and what would you have to do (or mock) to cover them? Is 100% coverage always the right goal for agentic code? Explain your reasoning.
- Approximately how many hours did this lab take? (I will not judge you — I use this to calibrate future assignments.)

---

## Extension Challenges

These are optional and carry no extra credit, but they will deepen your understanding.

**Challenge 1 (moderate): Property-based testing.**
Install `hypothesis` and write a property-based test for `summarize`: generate random strings of varying lengths and assert that the returned summary is always a non-empty string. Use `hypothesis.settings(suppress_health_check=...)` to silence the warning about mocking inside a strategy.

**Challenge 2 (moderate): Automated TestPyPI publishing in CI.**
Add a second GitHub Actions workflow (`publish.yml`) that triggers only on a pushed version tag (e.g., `v0.1.0`), builds the wheel, and runs `twine upload --repository testpypi`. Store your TestPyPI token as a GitHub repository secret named `TEST_PYPI_TOKEN`.

**Challenge 3 (harder): Multi-stage Docker build.**
Rewrite the Dockerfile with two stages: a `builder` stage that installs build dependencies and runs the tests, and a `runtime` stage that copies only the tested artifact. The image should not contain pytest or other dev dependencies in the final layer.
