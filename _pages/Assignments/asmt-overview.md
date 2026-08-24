---
layout: assignment
permalink: /Assignments/Overview
title: "CS357: Foundations of Artificial Intelligence - Overview"

info:
  coursenum: CS357
  purpose: "To get your local AI stack working before the labs depend on it, capture a baseline snapshot of your thinking about AI that you will revisit at the end of the semester, and launch your team."
  tilt:
    task: "Install and verify a working local AI environment and write a short baseline reflection on AI agency and trust."
    criteria: "I grade this on a complete setup-verification transcript and a specific, personal reflection in equal measure.  Please read the rubric below for the details."
  points: 100
  goals:
    - To install and verify a working local AI environment including Ollama, a pulled model, and a Python API call
    - To demonstrate baseline command-line, git, and Python-environment fluency by navigating a shell, cloning and committing to a repository, and creating a reproducible environment with uv
    - To articulate personal baseline beliefs about AI agency, trust, and delegation with specific examples
  rubric:
    - weight: 40
      description: Environment Setup and Verification
      preemerging: Little or no evidence that the environment was attempted
      beginning: Some components installed, but the verification transcript is missing or incomplete
      progressing: Ollama installed and verified with a transcript, with a minor omission such as a missing model listing or version information, or the command-line and git checkpoint is incomplete
      proficient: The transcript shows all four Ollama steps completed with verbatim terminal output, the output of ollama --version, ollama list showing at least one model, the curl /api/tags JSON response, and the Python script output including a non-empty "content" field, plus the operating system name and version; the command-line and git checkpoint (Part 1.5) is also complete, showing the shell-navigation commands, a git clone/commit/push transcript, and the uv environment creation; any failed step includes the verbatim error message, a stated hypothesis, and what was tried
    - weight: 40
      description: Reflection Essay
      preemerging: The reflection is missing or does not address the prompts
      beginning: The reflection addresses some prompts superficially without naming specific tools or moments
      progressing: The reflection addresses all four sections with specific examples, but the connection between the two delegation examples is not analyzed or the "What I Want to Build" section is vague
      proficient: All four sections are present and addressed with concrete specifics, a named AI tool and a described moment of surprise in "My AI Experience," a personal definition of agency distinct from any course reading in "What Agent Means to Me," a pair of delegation examples where the contrast between the two is explicitly analyzed, and a "What I Want to Build" description naming what the system would do, who would use it, and what working would look like
    - weight: 20
      description: Submission
      preemerging: An incomplete submission is provided
      beginning: The submission is provided but is disorganized, the transcript and the reflection are hard to tell apart, or one is missing
      progressing: All required components are present in a single file, with a minor omission such as an unlabeled transcript section or missing OS information
      proficient: A single well-organized PDF or Markdown file with each component clearly labeled, the four-step setup transcript with version and OS details, the Part 1.5 command-line and git checkpoint, and the four-section reflection, with the collaboration, AI-disclosure, and time questions answered at the end
  readings:
    - rtitle: "Welcome Activity"
      rlink: "https://www.billmongan.com/Ursinus-CS357-Overview"
    - rtitle: "Required setup (Route A): the Your AI Workbench activity, on your course development environment - Host Ollama, the Course Container, Git, and GitHub"
      rlink: "Activities/liascript-devenvironment.md"
      liapage: true
    - rtitle: "Required setup: the Your AI Workbench activity, Step 0 (the shell in ten minutes), covering the terminal skills every later lab assumes and the read-before-you-run habit"
      rlink: "Activities/liascript-devenvironment.md"
      liapage: true
    - rtitle: "The Shell, in Full: pipes, redirection, background jobs, and PATH, if the shell is new to you"
      rlink: "/Tutorials/Shell"
    - rtitle: "Mitchell, Prologue and Chapter 1"

tags:
  - intro
  - ai
  - agents

---

In this warmup you'll install your local AI stack and write a short baseline reflection on your experiences with AI.  I have kept the stakes low here on purpose.  It exists to make sure your tools work before the labs depend on them, and to capture a snapshot of your thinking that you'll come back to at the end of the semester.  (Your team charter is **not** part of this assignment; it is handed out separately once teams are announced; see the [Project Thread]({{ site.baseurl }}/Projects/PBLThread#the-team-charter-a-signed-team-contract).)  There are no wrong answers in the reflection.  This is a starting point, and I am not evaluating what you know.  See the course schedule for this onboarding assignment's due date; it is assessed within the Class Activities and Participation category.

---

## Before You Start

This is the first thing you install for this course.  I have put it early on purpose, so that a broken setup costs you this assignment rather than a lab.

**Pace yourself:** **most of this is downloading.**  The model pull alone is about 2 GB, and the container image is larger.  Please start the downloads on good wifi and write the reflection while they run.  Don't leave this for the night before; the downloads will not go any faster because you are in a hurry, and I can't help you at 11 PM.

**You need:** a laptop you can install software on, a GitHub account, and about 10 GB free disk.  If any of those is a problem, please say so this week rather than in week four.  There is a lab-machine route, and it takes some scheduling.

**Do it in this order:**

1.  Start the Ollama download (Part 1).  It runs in the background.
2.  While it downloads, write the baseline reflection (Part 2).  It needs no tools.
3.  Come back and finish the setup transcript.
4.  Do the command-line and git checkpoint (Part 1.5) last, since it uses what you just installed.

**Two routes, and I support both.**  Route A (host Ollama plus the course container) is the one I recommend, because every later lab assumes it and it is what we build together in the *Your AI Workbench* session.  Route B (native install) is complete and supported too, so take it if Docker will not run on your machine, and please say so in your transcript.  Neither route is the "real" one.

> **You've succeeded when** all four boxes in the Setup Checklist are checked, all three in the Part 1.5 checklist are checked, and your reflection has four labeled sections.  If a step failed, a documented failure with the verbatim error and what you tried earns full credit for that step; a vague "it worked eventually" does not.

---

## What a Strong Submission Looks Like

A strong submission has these qualities:

1.  **The transcript is complete and honest.**  It shows the actual terminal output (version numbers, model names, the API response), copied faithfully.  If something broke, quote the error verbatim and tell me what you tried.  I won't give credit for a fabricated or paraphrased transcript.
2.  **The reflection is personal and specific.**  It names a real AI tool you used, describes a real moment of surprise or confusion, and takes an actual position on agency and trust.  I am not looking for a dictionary definition or a summary of the syllabus.  A strong reflection reads like a journal entry from someone thinking carefully.

A weak submission has a transcript that says "it worked" without showing output and a reflection that restates prompts without answering them.

---

## Part 1: Tool Setup

Complete this part by **one of two routes**; the four verification steps and the checklist below apply to both.

### Route A (recommended): host Ollama + the course dev container

Set up the full course environment by following the [Development Environment activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-devenvironment.md): Ollama installs **natively on your host** exactly as in Route B, and the rest of the semester's toolchain lives in one course Docker container bind-mounted onto a `cs357-work` GitHub repository you create in the activity.  On this route, run steps 1-3 below on your host as written, and run step 4 (the Python request) **from inside the container**, replacing `localhost` with `host.docker.internal` in the URL. A verification transcript captured from inside the container is fully accepted; include the container prompt in your copy-paste so it is visible where each command ran, along with the activity's own container verification output (the `/api/tags` one-liner, `promptfoo --version`, and the spacy model check).

### Route B: native install

Install [Ollama](https://ollama.com/download) on your own machine (or a lab machine if yours cannot run it; ask the instructor if you are unsure which to use).  Then complete each step below and capture the output:

1.  Pull a small model: `ollama pull llama3.2`
2.  Run a CLI sanity check: `ollama run llama3.2 "Say hello in five words."`
3.  Verify the REST API responds: `curl http://localhost:11434/api/tags`
4.  From Python, send one chat request using the `requests` library, as we did in class, and print the response.  Your script should look roughly like this:

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

**If any step fails:** document the error message verbatim, state your hypothesis about the cause, and describe what you tried.  A well-documented failure with a follow-up plan earns full credit for that step.  Do not delete error output or write "it eventually worked" without showing what changed.

### Setup Checklist

Before moving on, confirm you can answer yes to each of these:

- [ ] `ollama --version` returns a version string
- [ ] `ollama list` shows at least one downloaded model
- [ ] The `curl` command to `/api/tags` returns JSON (not a connection error)
- [ ] Your Python script prints a response that includes a `"content"` field

---

## Part 1.5: Command-Line and Git Checkpoint

Every lab this semester runs from a terminal, lives in a git repository, and depends on a reproducible Python environment.  This checkpoint makes sure those underlying tools work *before* the labs depend on them, the same philosophy as the Ollama setup above.  You do not need to be a shell wizard; you need to be able to move around, version your work, and stand up an environment without guesswork.  If any command below is unfamiliar, the **Command-Line Survival** resources at the end of this section will get you there.

**Container-route note (Route A):** perform the git steps of this checkpoint **from inside the course container**, against the `cs357-work` GitHub repository you created in the [Development Environment activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-devenvironment.md); the activity's practice section (create `hello_agent.py`, run it against host Ollama, commit, push) is exactly this checkpoint, so its transcript satisfies the navigation and git items below.  The `uv` step still runs on your host (the container image already bundles the course packages; `uv` is your reproducible-environment tool for the native route and anywhere outside the container).

Complete each step and capture the terminal output:

1.  **Navigate.**  From a terminal, create a working directory for this course, enter it, and list its contents: `mkdir -p ~/cs357 && cd ~/cs357 && pwd && ls -la`.  Then use one search tool, `grep` (or `ripgrep`/`rg` if installed), to find a string in a file, and paste the command you ran.
2.  **Version control.**  Create a small git repository, make a commit, and connect it to a remote (your course GitHub Classroom repo, or a throwaway GitHub repo): `git init`, add a file, `git add`, `git commit -m "first commit"`, then `git remote add origin <url>` and `git push -u origin main`.  Paste the transcript of `git log --oneline` showing your commit.
3.  **Reproducible Python with uv.**  Install [uv](https://docs.astral.sh/uv/) (the fast, modern Python environment manager we standardize on this term).  Create and activate a project environment and add the one dependency the labs start with: `uv venv`, then `uv add requests`, then `uv run python -c "import requests; print(requests.__version__)"`.  Paste the output.  (If you cannot install uv, fall back to `python -m venv` and `pip install requests`, and note in your submission that you used the fallback.)

### Command-Line Survival: reference (use as needed, not required reading cover-to-cover)

- [tldr pages](https://tldr.sh/): plain-language example-first cheat sheets for any command (`tldr tar`).
- [explainshell](https://explainshell.com/): paste any command line and see each flag explained.
- [ShellCheck](https://www.shellcheck.net/): catches bugs in shell scripts before they bite.
- `curl` and [HTTPie](https://httpie.io/) plus [jq](https://jqlang.github.io/jq/): you will hit JSON APIs (Ollama, MCP) all semester; `curl ... | jq` is your friend.

### Part 1.5 Checklist

- [ ] A shell transcript showing directory creation, navigation, and a `grep`/`rg` search
- [ ] A `git log --oneline` transcript showing at least one commit pushed to a remote
- [ ] A `uv` (or documented fallback) transcript importing `requests`

---

## Part 2: Baseline Reflection

Write approximately one page addressing all four prompts below.  This is captured now so you can compare it to your thinking at the end of the semester.  There are no wrong answers.

**Reflection Template** (use these as section headings; write a paragraph under each):

### My AI Experience So Far

Describe which AI tools you use, for what purposes, and how often.  Then describe one specific moment when an AI output surprised you, either because it was better than you expected, or because it failed in an unexpected way.  Name the tool, describe the task, and describe the surprise.

### What "Agent" Means to Me Right Now

Write your own definition of what makes a system an "agent" rather than just a program or a tool.  You do not need to match any textbook definition; write what you actually think.  After the semester, we will return to this and see how your thinking changed.

### What I Would and Would Not Delegate

Name one task you would happily hand to an AI agent and one you would not.  For each, write one or two sentences explaining the specific reason: what is it about that task that makes delegation feel appropriate or inappropriate?  The difference between your two examples is more interesting than either example alone.

### What I Want to Build

Describe one thing you hope to be able to build or do by the end of the semester that you cannot do today.  Be as concrete as you can: what would it do, who would use it, and what would "working" look like?

---

## Troubleshooting

Work down this table before you post in the course channel; if none of it helps, post the exact command you ran and its full output.

| Symptom | Likely cause | Fix |
|---|---|---|
| `ollama: command not found` after installing | The installer put the binary somewhere not on your `PATH` | Restart your terminal. If it persists, find the binary (`ls /usr/local/bin/ollama`) and add its directory to `PATH`. This is the `PATH` idea from Step 0 of the Workbench session |
| The `curl` to `/api/tags` says connection refused | The Ollama *server* is not running, which is separate from Ollama being installed | Start the desktop app, or run `ollama serve` in its own terminal and leave it open |
| The model download stalls or fails partway | Network interruption on a 2 GB transfer | Rerun `ollama pull llama3.2`; it resumes rather than restarting |
| Inside the container, `localhost:11434` refuses the connection | Correct behavior: `localhost` inside a container means the container | Use `http://host.docker.internal:11434`. On Linux, start via the course compose file so that hostname resolves |
| `Cannot connect to the Docker daemon` | Docker Desktop is installed but not running | Start the application. On Linux, `sudo systemctl start docker`, and confirm your user is in the `docker` group |
| `git push` rejected, "authentication failed" | GitHub no longer accepts account passwords over HTTPS | Use a fine-grained personal access token scoped to that one repository, with Contents: read and write |
| `uv: command not found` | Not installed, or not on `PATH` yet | Follow the uv install docs, restart the terminal, and if it still fails use the documented `python -m venv` fallback and say so |
| Responses are very slow | A small model on CPU-only hardware | Expected. `llama3.2` is the right choice for that machine. Note the speed in your transcript; it is a real observation, not a failure |
| Out of disk space partway through the build | The course image plus models is roughly 8 to 10 GB | Clear space and rerun `docker compose build`; completed layers are cached and the build resumes |

---

## Self-Check Before You Submit

Hold your submission against the rubric's `proficient` column:

- [ ] One file, PDF or Markdown, with each component **clearly labeled**.
- [ ] Setup transcript covers all four steps, and states your **OS and version numbers**.
- [ ] Transcript output is **copied verbatim**, not retyped or paraphrased.
- [ ] Any failure is quoted exactly, with a hypothesis and what you tried.
- [ ] Part 1.5: shell navigation and a search, a `git log --oneline` showing a pushed commit, and the uv (or documented fallback) output.
- [ ] Reflection has **four** labeled sections and is about a page.
- [ ] The reflection says what you actually think, not what you expect the course to want.
- [ ] Which route you took (A or B) is stated.
- [ ] Collaboration, AI-disclosure, and hours questions answered at the end.

---

## Deliverables

Submit a single PDF or markdown file containing:
- Your tool setup transcript (all four steps plus version and OS info)
- Your command-line and git checkpoint transcript (Part 1.5: navigation, git commit/push, uv environment)
- Your baseline reflection (one page, four sections)

---

## Frequently Asked Questions

**Q: I don't have a machine that can run Ollama.  What should I do?**
A: Use a lab machine or contact the instructor before the due date.  Do not wait until the night before; lab access may require scheduling.  Document which machine you used in your transcript.

**Q: My Python API call returns an error or the model responds very slowly.  Is that okay?**
A: Slow is okay for a small model on older hardware.  An error is okay as long as you document it fully: copy the full error message, describe what you tried, and state whether it was eventually resolved.  A partial success with complete documentation earns full credit for that step.

**Q: The reflection prompts ask about "agency" and "trust"; do I need to use the textbook definitions?**
A: No.  This is a baseline, and not a knowledge test.  Write what you actually think before the course shapes your view.  The textbook will be there later; this snapshot of your prior thinking is valuable precisely because it is unfiltered.

---

Please also answer the following questions in your submission:

- If collaboration with a buddy was permitted, did you work with a buddy on this assignment?  If so, who?  If not, do you certify that this submission represents your own original work?  Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
