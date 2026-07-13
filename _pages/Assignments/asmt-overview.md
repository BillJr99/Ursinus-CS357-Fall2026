---
layout: assignment
permalink: /Assignments/Overview
title: "CS357: Foundations of Artificial Intelligence - Overview"

info:
  coursenum: CS357
  purpose: "To get your local AI stack working before the labs depend on it, capture a baseline snapshot of your thinking about AI that you will revisit at the end of the semester, and launch your team."
  tilt:
    task: "Install and verify a working local AI environment, write a short baseline reflection on AI agency and trust, and co-author a team charter with your semester group."
    criteria: "Assessed on a complete setup-verification transcript and a specific, personal reflection in equal measure, plus an actionable team charter; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To install and verify a working local AI environment including Ollama, a pulled model, and a Python API call
    - To demonstrate baseline command-line, git, and Python-environment fluency by navigating a shell, cloning and committing to a repository, and creating a reproducible environment with uv
    - To articulate personal baseline beliefs about AI agency, trust, and delegation with specific examples
    - To co-author a team charter with concrete role rotation, communication, and conflict-resolution procedures
  rubric:
    - weight: 40
      description: Environment Setup and Verification
      preemerging: Little or no evidence that the environment was attempted
      beginning: Some components installed, but the verification transcript is missing or incomplete
      progressing: Ollama installed and verified with a transcript, with a minor omission such as a missing model listing or version information, or the command-line and git checkpoint is incomplete
      proficient: The transcript shows all four Ollama steps completed with verbatim terminal output — the output of ollama --version, ollama list showing at least one model, the curl /api/tags JSON response, and the Python script output including a non-empty "content" field — plus the operating system name and version; the command-line and git checkpoint (Part 1.5) is also complete, showing the shell-navigation commands, a git clone/commit/push transcript, and the uv environment creation; any failed step includes the verbatim error message, a stated hypothesis, and what was tried
    - weight: 40
      description: Reflection Essay
      preemerging: The reflection is missing or does not address the prompts
      beginning: The reflection addresses some prompts superficially without naming specific tools or moments
      progressing: The reflection addresses all four sections with specific examples, but the connection between the two delegation examples is not analyzed or the "What I Want to Build" section is vague
      proficient: All four sections are present and addressed with concrete specifics — a named AI tool and a described moment of surprise in "My AI Experience," a personal definition of agency distinct from any course reading in "What Agent Means to Me," a pair of delegation examples where the contrast between the two is explicitly analyzed, and a "What I Want to Build" description naming what the system would do, who would use it, and what working would look like
    - weight: 20
      description: Team Charter and Submission
      preemerging: An incomplete submission is provided
      beginning: The submission is provided but the team charter is missing or does not address role rotation
      progressing: The submission is complete with a charter that addresses roles and communication, with a minor omission such as a missing disagreement procedure or undefined response time expectation
      proficient: The charter addresses all six rows of the Charter Template — role rotation schedule with named roles and rotation timing, a primary communication channel with a specific response-time expectation, a meeting cadence with a named day and time, a disagreement procedure naming who has the deciding vote or how consensus is reached, a missed-deadline procedure with a stated timeline, and a definition of done naming who checks it — and all team members' typed names appear at the bottom
  readings:
    - rtitle: "Welcome Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-welcomeagents.md"
    - rtitle: "Mitchell, Prologue and Chapter 1"

tags:
  - intro
  - ai
  - agents

---

In this warmup you will install your local AI stack, write a short baseline reflection on your experiences with AI, and co-author a team charter with your semester group. This assignment is deliberately low-stakes: it exists to make sure your tools work before the labs depend on them, to capture a snapshot of your thinking that you will revisit at the end of the semester, and to launch your team before the first real project sprint. There are no wrong answers in the reflection — this is a starting point, not an evaluation of knowledge. See the course schedule for this onboarding assignment's due date; it is assessed within the Class Activities and Participation category.

---

## What a Strong Submission Looks Like

A strong submission has three qualities:

1. **The transcript is complete and honest.** It shows the actual terminal output — version numbers, model names, the API response — copied faithfully. If something broke, the error is quoted verbatim and the student explains what they tried. Fabricated or paraphrased transcripts earn no credit.
2. **The reflection is personal and specific.** It names a real AI tool the student used, describes a real moment of surprise or confusion, and takes a genuine position on agency and trust — not a dictionary definition, not a summary of the course syllabus. A strong reflection reads like a journal entry from someone thinking carefully, not like an answer written to please a grader.
3. **The charter is actionable.** It names specific meeting times, specific communication channels, and a concrete procedure for the team to follow when a member misses a deadline. Vague statements like "we will communicate openly" do not count.

A weak submission has a transcript that says "it worked" without showing output, a reflection that restates prompts without answering them, and a charter that could belong to any group of three strangers.

---

## Part 1: Tool Setup

Complete this part by **one of two routes** — the four verification steps and the checklist below apply to both.

### Route A (recommended): host Ollama + the course dev container

Set up the full course environment by following the [Development Environment activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-devenvironment.md): Ollama installs **natively on your host** exactly as in Route B, and the rest of the semester's toolchain lives in one course Docker container bind-mounted onto a `cs357-work` GitHub repository you create in the activity. On this route, run steps 1–3 below on your host as written, and run step 4 (the Python request) **from inside the container**, replacing `localhost` with `host.docker.internal` in the URL. A verification transcript captured from inside the container is fully accepted — include the container prompt in your copy-paste so it is visible where each command ran, along with the activity's own container verification output (the `/api/tags` one-liner, `promptfoo --version`, and the spacy model check).

### Route B: native install

Install [Ollama](https://ollama.com/download) on your own machine (or a lab machine if yours cannot run it; ask the instructor if you are unsure which to use). Then complete each step below and capture the output:

1. Pull a small model: `ollama pull llama3.2`
2. Run a CLI sanity check: `ollama run llama3.2 "Say hello in five words."`
3. Verify the REST API responds: `curl http://localhost:11434/api/tags`
4. From Python, send one chat request using the `requests` library, as we did in class, and print the response. Your script should look roughly like this:

```python
import requests, json

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3.2",
        "messages": [{"role": "user", "content": "What is 2 + 2?"}],
        "stream": False
    }
)
print(json.dumps(response.json(), indent=2))
```

Copy-paste or screenshot the output of all four steps, including the output of `ollama --version` and your operating system name and version.

**If any step fails:** document the error message verbatim, state your hypothesis about the cause, and describe what you tried. A well-documented failure with a follow-up plan earns full credit for that step. Do not delete error output or write "it eventually worked" without showing what changed.

### Setup Checklist

Before moving on, confirm you can answer yes to each of these:

- [ ] `ollama --version` returns a version string
- [ ] `ollama list` shows at least one downloaded model
- [ ] The `curl` command to `/api/tags` returns JSON (not a connection error)
- [ ] Your Python script prints a response that includes a `"content"` field

---

## Part 1.5: Command-Line and Git Checkpoint

Every lab this semester runs from a terminal, lives in a git repository, and depends on a reproducible Python environment. This checkpoint makes sure those underlying tools work *before* the labs depend on them — the same philosophy as the Ollama setup above. You do not need to be a shell wizard; you need to be able to move around, version your work, and stand up an environment without guesswork. If any command below is unfamiliar, the **Command-Line Survival** resources at the end of this section will get you there.

**Container-route note (Route A):** perform the git steps of this checkpoint **from inside the course container**, against the `cs357-work` GitHub repository you created in the [Development Environment activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-devenvironment.md) — the activity's practice section (create `hello_agent.py`, run it against host Ollama, commit, push) is exactly this checkpoint, so its transcript satisfies the navigation and git items below. The `uv` step still runs on your host (the container image already bundles the course packages; `uv` is your reproducible-environment tool for the native route and anywhere outside the container).

Complete each step and capture the terminal output:

1. **Navigate.** From a terminal, create a working directory for this course, enter it, and list its contents: `mkdir -p ~/cs357 && cd ~/cs357 && pwd && ls -la`. Then use one search tool — `grep` (or `ripgrep`/`rg` if installed) — to find a string in a file, and paste the command you ran.
2. **Version control.** Create a small git repository, make a commit, and connect it to a remote (your course GitHub Classroom repo, or a throwaway GitHub repo): `git init`, add a file, `git add`, `git commit -m "first commit"`, then `git remote add origin <url>` and `git push -u origin main`. Paste the transcript of `git log --oneline` showing your commit.
3. **Reproducible Python with uv.** Install [uv](https://docs.astral.sh/uv/) (the fast, modern Python environment manager we standardize on this term). Create and activate a project environment and add the one dependency the labs start with: `uv venv`, then `uv add requests`, then `uv run python -c "import requests; print(requests.__version__)"`. Paste the output. (If you cannot install uv, fall back to `python -m venv` and `pip install requests`, and note in your submission that you used the fallback.)

### Command-Line Survival — reference (use as needed, not required reading cover-to-cover)

- [tldr pages](https://tldr.sh/) — plain-language example-first cheat sheets for any command (`tldr tar`).
- [explainshell](https://explainshell.com/) — paste any command line and see each flag explained.
- [ShellCheck](https://www.shellcheck.net/) — catches bugs in shell scripts before they bite.
- `curl` and [HTTPie](https://httpie.io/) plus [jq](https://jqlang.github.io/jq/) — you will hit JSON APIs (Ollama, MCP) all semester; `curl … | jq` is your friend.

### Part 1.5 Checklist

- [ ] A shell transcript showing directory creation, navigation, and a `grep`/`rg` search
- [ ] A `git log --oneline` transcript showing at least one commit pushed to a remote
- [ ] A `uv` (or documented fallback) transcript importing `requests`

---

## Part 2: Baseline Reflection

Write approximately one page addressing all four prompts below. This is captured now so you can compare it to your thinking at the end of the semester. There are no wrong answers.

**Reflection Template** (use these as section headings; write a paragraph under each):

### My AI Experience So Far
Describe which AI tools you use, for what purposes, and how often. Then describe one specific moment when an AI output surprised you — either because it was better than you expected, or because it failed in an unexpected way. Name the tool, describe the task, and describe the surprise.

### What "Agent" Means to Me Right Now
Write your own definition of what makes a system an "agent" rather than just a program or a tool. You do not need to match any textbook definition — write what you actually think. After the semester, we will return to this and see how your thinking changed.

### What I Would and Would Not Delegate
Name one task you would happily hand to an AI agent and one you would not. For each, write one or two sentences explaining the specific reason — what is it about that task that makes delegation feel appropriate or inappropriate? The difference between your two examples is more interesting than either example alone.

### What I Want to Build
Describe one thing you hope to be able to build or do by the end of the semester that you cannot do today. Be as concrete as you can: what would it do, who would use it, and what would "working" look like?

---

## Part 3: Team Charter

> **Note:** the charter you write here is the **pre-draft**. Your team will expand it into the full, signed semester charter in the dedicated [Team Charter and Norms activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-groupcharter.md) — bring this draft with you.

With your assigned team, co-author a one-page charter. All members must contribute. Typed names at the bottom serve as signatures.

**Charter Template:**

| Charter Section | Your Team's Answer |
|---|---|
| **Role rotation schedule** | Which POGIL role does each member hold in Sprint 1? How and when do roles rotate? |
| **Primary communication channel** | Where (Slack, Discord, text, email) and when (response time expectation)? |
| **Meeting cadence** | When does the team meet outside class? What is the minimum preparation expected before each meeting? |
| **Disagreement procedure** | When the team disagrees on a technical decision, what is the process for resolving it? Who has the deciding vote, or how do you reach consensus? |
| **Missed deadline procedure** | If a member cannot meet a deadline, what do they do, and by when? |
| **Definition of "done"** | What does it mean for a sprint task to be complete? Who checks? |

---

## Deliverables

Submit a single PDF or markdown file containing:
- Your tool setup transcript (all four steps plus version and OS info)
- Your command-line and git checkpoint transcript (Part 1.5: navigation, git commit/push, uv environment)
- Your baseline reflection (one page, four sections)
- Your team charter (one per team is fine; include it with each member's individual submission)

---

## Frequently Asked Questions

**Q: I don't have a machine that can run Ollama. What should I do?**
A: Use a lab machine or contact the instructor before the due date. Do not wait until the night before — lab access may require scheduling. Document which machine you used in your transcript.

**Q: My Python API call returns an error or the model responds very slowly. Is that okay?**
A: Slow is okay for a small model on older hardware. An error is okay as long as you document it fully: copy the full error message, describe what you tried, and state whether it was eventually resolved. A partial success with complete documentation earns full credit for that step.

**Q: The reflection prompts ask about "agency" and "trust" — do I need to use the textbook definitions?**
A: No. This is a baseline, not a knowledge test. Write what you actually think before the course shapes your view. The textbook will be there later; this snapshot of your prior thinking is valuable precisely because it is unfiltered.

**Q: Can my team charter be just a paragraph instead of a table?**
A: Yes, format is flexible. What matters is that every required topic is addressed concretely. A paragraph that says "we will use Discord and meet Sundays at 2pm and rotate roles every two weeks" covers more ground than a table full of vague entries.

**Q: Do all team members submit the same charter, or do we each write our own?**
A: Submit the same jointly authored charter with each member's individual submission. The charter is a team document; the transcript and reflection are individual.

---

Please also answer the following questions in your submission:

- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
