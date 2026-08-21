<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-scheduledagents.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-scheduledagents.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Scheduled and Autonomous Agent Runs: Cron, systemd, n8n, and GitHub Actions

So far every agent we have built waited for *us* to press enter. This module asks a different question: what if the agent runs **while you sleep**? We move from **a trigger on a clock $\rightarrow$ the scheduling substrates that provide it $\rightarrow$ a governed unattended run $\rightarrow$ a worked example that clones a repo, reviews it, and opens a pull request**. The reward is leverage; the risk is an agent taking consequential actions with no human in the room, so governance rides along the whole way.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| Scheduler / trigger | The clock or event that starts a run without a human pressing go | A `cron` line that fires a script at 2 a.m. nightly |
| Unattended run | An agent execution with no human watching in real time | The nightly repo-review job in Model 2 |
| Governed autonomy | An architecture where an unattended agent may *propose* any action but may *execute* only what its gate policy classifies as safe | The Autorun / Queue / Forbidden lanes below |
| Idempotency | A job you can run twice with the same result as running it once: no duplicates, no double-posting | Checking "did I already open a PR for this commit?" before opening one |
| Catch-up policy | What a scheduler does about runs it missed while the machine was off | Collapse a weekend of misses into a single catch-up run |
| Headless execution | Running with no interactive terminal or GUI attached | The same agent, driven by CI instead of your keyboard |

---

### Before You Start

**What you need:** An agent script that already works when you run it yourself. Scheduling comes second.

**What you will have at the end:** that agent running unattended on a schedule, with logs you can inspect afterward.

Work through the sections in order; each one builds on the last, and the code blocks are meant to be run as you reach them, not read past.

---

# Part I: A Trigger Is Just a Clock

In this part you will see that "autonomous" mostly means "something other than a human started the run," and that the something is one of a small, boring set of schedulers. The intelligence is the same agent you already built; only the *trigger* changed.

## 1. Four Ways to Start a Run Without You

An unattended agent needs exactly one new ingredient over the agents we have already built: a **trigger**. Four substrates cover almost everything you will meet.

| Substrate | Where it lives | Fires by | Best for |
|-----------|----------------|----------|----------|
| **`cron`** | Any Linux/macOS machine | A time schedule (`min hour day month weekday`) | Simple recurring local jobs |
| **`systemd` timer** | Modern Linux | A schedule *plus* logging, retries, and dependency ordering | Robust local jobs that must survive reboots |
| **n8n** | The agent stack (port 5678) | A schedule node *or* a webhook/event | Visual multi-step workflows that call your gateway and tools |
| **GitHub Actions** | GitHub's cloud | A `schedule:` (cron) *or* repo events (push, PR) | Jobs that act on a repository, in a clean cloud runner |

The classic `cron` line is five fields and a command. This one runs a script every day at 2:00 a.m.:

```text
# + minute  + hour  + day-of-month  + month  + day-of-week
  0         2       *               *        *        /home/agent/nightly_review.sh
```

A `systemd` timer expresses the same idea with more safety rails (it logs to the journal and can run a "catch-up" pass with `Persistent=true`):

```text
# nightly-review.timer
[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true
[Install]
WantedBy=timers.target
```

And GitHub Actions uses cron syntax too, but runs in a fresh cloud machine that already has `git` and secrets available:

```text
# .github/workflows/nightly-review.yml
on:
  schedule:
    - cron: "0 2 * * *"     # 02:00 UTC daily
  workflow_dispatch: {}       # ...and a manual "run now" button
```

> **Common Misconception:** Students often think "autonomous agent" names a special kind of AI. It does not. The **model is identical** to the one you call by hand; autonomy is entirely about *who pulls the trigger*. Swap your keyboard for a `cron` line and the same agent is now "autonomous." That reframing is the whole lesson, and it is why the hard part is governance, not intelligence.

---

## Model 1: Where Does the Schedule Live?

Consider three ways to run the same "summarize my new email each morning" agent: (A) a `cron` line on your laptop; (B) an **n8n** schedule node in the local stack that calls your gateway; (C) a **GitHub Actions** workflow on a `schedule:` trigger.

### Critical Thinking Questions

1. Your laptop is closed at 7 a.m. Which of the three still runs, and which silently miss? What does that tell you about *where* a scheduler should live for a job that must not be skipped?

   > *Hint: cron and n8n run on your machine; GitHub Actions runs in GitHub's cloud. A sleeping laptop runs neither local option.*

2. A run was missed because the machine was off all weekend. Describe two different **catch-up policies** and a task where each is the right choice.

   > *Hint: "Run once immediately to catch up" suits a daily digest; "skip the misses and wait for the next slot" suits a job whose old output is now stale.*

3. Two of these substrates make it easy to give the agent access to a private GitHub repository and a secret token. Which two, and why does that convenience also raise the stakes?

   > *Hint: n8n stores credentials; GitHub Actions injects repo secrets. Convenient, and now an unattended process holds the keys.*

---

# Part II: Governing an Unattended Run

In this part you will add the safety architecture that makes unattended execution acceptable. An agent no one is watching must not be free to do anything it can imagine, so we separate what it may *propose* from what it may *execute*.

## 2. Propose Freely, Execute by Policy

The core pattern (borrowed from the *Personal Agent in Production* case study) is **governed autonomy**: the agent may reason about and *propose* any action, but a deterministic **gate** decides which proposals actually run. Sort every possible action into three lanes:

| Lane | Policy | Examples |
|------|--------|----------|
| **Autorun** | Safe + reversible -> execute immediately, log it | Read files, run tests, open a *draft* PR, write to a scratch dir |
| **Queue** | Consequential -> hold as a proposal for human approval | Merge a PR, send an email, delete data, spend money |
| **Forbidden** | Never, regardless of reasoning | Push to `main`, rotate credentials, touch production data |

Two properties make an unattended job trustworthy. **Idempotency**: running it twice must not double-act, so before opening a PR the job checks whether one already exists for this commit. And a **silent-on-success** habit: routines that succeed say nothing, so that the *only* messages you get are the ones that need you.

An unattended nightly agent is about to take an action. Which action belongs in the **Autorun** lane rather than **Queue**?

[( )] Merging its own pull request because CI passed
[( )] Emailing the whole team a summary
[(X)] Opening a **draft** pull request with its proposed changes
[( )] Force-pushing a rebased branch to `main`

> **Common Misconception:** "If the tests pass, the agent should just merge." Passing tests mean the change is *plausibly* correct, not that it is *wanted*, the same "sounds right ≠ is right" gap we saw with token prediction. Opening a draft PR (Autorun) keeps a human as the one who clicks merge (Queue). Autonomy is about removing toil, not removing accountability.

---

## Model 2: Anatomy of a "Clone -> Review -> Open a PR" Run

Here is the run the whole module builds toward, traced stage by stage. A scheduler fires nightly; the agent reviews a repository and proposes changes as a draft PR, never merging.

| Stage | What happens | Lane |
|-------|--------------|------|
| 1. Trigger | `cron` / GitHub Actions `schedule:` fires at 02:00 | - |
| 2. Clone | `git clone` the repo into a throwaway working directory | Autorun |
| 3. Read | The agent reads changed files / the diff and any `AGENTS.md` house rules | Autorun |
| 4. Review | A local model produces structured review comments and a suggested patch | Autorun (proposes) |
| 5. Branch | Create `agent/nightly-review-<date>`; apply the patch; run the tests | Autorun |
| 6. Open PR | If tests pass **and** no PR already exists for this commit, open a **draft** PR | Autorun |
| 7. Merge | A human reads the draft PR and merges, or closes it | **Queue** (human) |

The **review** stage is the only part that needs an LLM, and it is fully runnable against your local stack. The cell below reviews a small diff with a local model and asks for structured output, exactly what stage 4 emits.

## Code Cell

```python
import requests, json

def review_diff(diff, model="llama3.2"):
    system = ("You are a careful code reviewer. Given a diff, return ONLY JSON: "
              '{"summary": str, "issues": [{"severity":"low|med|high","note":str}], '
              '"safe_to_open_pr": true|false}. Be conservative: if unsure, safe_to_open_pr=false.')
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": 0.0, "seed": 42},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": "Review this diff:\n\n" + diff}]},
            timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[scheduledagents:review] {e}")
        import traceback; traceback.print_exc()
        return ""

sample_diff = """
--- a/util.py
+++ b/util.py
@@
-def divide(a, b):
-    return a / b
+def divide(a, b):
+    return a / b  # TODO: what if b == 0?
"""

print(review_diff(sample_diff))
```

The clone/branch/PR stages around it are ordinary shell, meant to run on your machine or in CI (not in this browser). This is the *shape* of `nightly_review.sh`:

```text
set -euo pipefail
work=$(mktemp -d)
git clone --depth 50 "$REPO_URL" "$work" && cd "$work"
python review_agent.py --diff "$(git diff HEAD~1)" > review.json   # calls review_diff()
git checkout -b "agent/nightly-review-$(date +%F)"
python apply_patch.py review.json && pytest -q || exit 0            # tests gate the PR
# idempotency: only open a PR if one does not already exist for this HEAD
gh pr list --head "agent/nightly-review-$(date +%F)" | grep -q . \
  || gh pr create --draft --title "Nightly agent review" --body-file review.json
```

### Critical Thinking Questions

4. Stage 6 checks whether a PR already exists before opening one. Which Key Concept is that, and what goes wrong on the *second* night without it?

   > *Hint: Idempotency. Without the check, every night opens another near-identical PR until the repo is buried in duplicates.*

5. The whole pipeline is Autorun except stage 7. Rewrite the boundary: name one change that would move "open a PR" from Autorun to Queue, and one that would move "merge" from Queue to Forbidden.

   > *Hint: If PRs auto-notify 50 reviewers, opening one is now consequential. If the repo is production infrastructure, merging by machine may be Forbidden outright.*

6. The review model is called at `temperature=0.0`. Why is that the right choice for an unattended reviewer, when a brainstorming agent might use 0.9?

   > *Hint: Unattended means no human to catch a wild output. Determinism and conservatism matter more than creativity here.*

---

# Part III: Is OpenWebUI Enough? and Your Build

In this part you will answer a question students always ask ("can I just do this in OpenWebUI?") and then build a scheduled agent of your own.

## 3. Can You Schedule This with OpenWebUI?

Short answer: **OpenWebUI has no built-in scheduler.** It is a request/response frontend; it runs *one completion per request* and has no concept of "run this every night." Its Functions (pipes/filters) reshape a request as it passes through; they are not background timers.

But OpenWebUI is still useful here, because it exposes an **OpenAI-compatible API** at `http://localhost:3000/api/chat/completions` (Bearer-key authenticated), which applies the tools, knowledge, and filters you configured for a model. So the pattern is:

> **Pair an external scheduler with OpenWebUI's API.** Let `cron`, a `systemd` timer, **n8n**, or GitHub Actions be the clock, and have it POST to OpenWebUI's `/api/chat/completions` (or straight to Ollama's `/api/chat`). The scheduler supplies autonomy; OpenWebUI supplies the agentic layer.

This is exactly how the local stack already wires n8n (port 5678) in front of the gateway: *"Every morning at 7am, summarize new emails and save to workspace."* The scheduler is the new part; the model call is the same one you already know.

A student says "I'll make OpenWebUI run my agent every night." The most accurate correction is:

[( )] OpenWebUI can schedule jobs, but only on the paid tier
[(X)] OpenWebUI has no scheduler; pair it with cron/systemd/n8n/GitHub Actions that call its API on a timer
[( )] You must rewrite the agent as an OpenWebUI Function to schedule it
[( )] Scheduling is impossible without a cloud provider

---

## 4. Exercises

1. *Pick your clock.*

   - *What to do*: For each of three jobs, (a) a 7 a.m. personal news digest, (b) a repo reviewer that must act on a private GitHub repo, (c) a job that tidies a shared lab server's `downloads/` folder, choose one of the four substrates and justify it in one sentence.
   - *Starter hint*: Ask where the data and the trigger need to live. A GitHub-repo job wants GitHub Actions; a server-folder job wants a local `systemd` timer.
   - *You've succeeded when*: You can defend each pairing against one alternative ("why not cron for the repo job?").

2. *Draw the gate.*

   - *What to do*: For an unattended agent that manages your email, sort ten concrete actions into Autorun / Queue / Forbidden. Include at least one action your group disagrees about and record why.
   - *Starter hint*: Start with the obvious ends (read = Autorun, delete-all = Forbidden) and fight over the middle (auto-reply? archive? unsubscribe?).
   - *You've succeeded when*: Every action has a lane and a one-line reason, and the contested one has both sides noted.

3. *Make it idempotent.*

   - *What to do*: Take the `nightly_review.sh` sketch and add a second guard (beyond the PR-exists check) that prevents duplicate or wasteful work if the job runs twice in one night.
   - *Starter hint*: Could you record the last-reviewed commit SHA in a file and exit early if `HEAD` has not changed?
   - *You've succeeded when*: Running your script twice in a row causes exactly one PR and one review, and you can explain which guard stopped the second.

---

## Lab Option: Build a Scheduled Agent (Choose Your Direction)

Everyone completes the **core**: a script that runs one useful agent task, wired to a real scheduler (a local `cron`/`systemd` timer, an n8n schedule node, or a GitHub Actions `schedule:`), that logs each run and is safe to run twice. Once it runs end-to-end on a timer for two consecutive fires, extend it in **one** direction below. This is offered as a lab-scale build; check with your instructor about submitting it for lab credit.

<details markdown="1"><summary><strong>Direction A: The Nightly Repo Reviewer (clone -> review -> draft PR)</strong></summary>

Build the Model 2 pipeline against a repository you own. A scheduler clones the repo, runs `review_diff()` (from the Code Cell) on the latest diff, opens a **draft** PR on a new branch if and only if the tests pass and no PR already exists for that commit, and never merges.

- *What proficient work looks like*: the job runs unattended on a timer; a draft PR appears with structured review comments; running the job twice yields exactly one PR (idempotent); merging is left to a human; a short `run.log` records each fire, including the silent "nothing to review" nights.

</details>

<details markdown="1"><summary><strong>Direction B: The Directory Organizer (timer -> tidy a folder)</strong></summary>

Build a scheduled agent that organizes a messy directory (e.g., `downloads/`): it proposes a tidy structure (by type/date/topic), and (under the gate) *moves* files in the Autorun lane while *queuing* any deletion or overwrite for human approval. Use a local model to suggest categories from filenames.

- *What proficient work looks like*: the job runs on a timer; files are sorted into a sensible tree; no file is ever deleted or overwritten without a queued proposal; a dry-run mode prints the plan without touching disk; running it again after tidying is a no-op (idempotent).

</details>

---

## Reflection Prompt

*Personal*: Think of one recurring chore in your own digital life. Would you actually let an unattended agent do it while you sleep? What single action, if it went wrong at 3 a.m. with no one watching, would make you say "no", and which lane does that action belong in?

*Technical*: You now know that "autonomous" means "a scheduler pulled the trigger." Sketch the smallest change that would turn one agent you have already built this semester into a scheduled one, and name the one action you would move to the Queue lane before you would trust it overnight.

*Societal*: Unattended agents acting on repositories, inboxes, and servers scale a single person's intent across thousands of actions with no human in each loop. If many people run such agents, what new failure modes appear at scale, and who is accountable when an agent that "just ran on a schedule" causes harm?

---

-> Coming Up Next: We have let an agent act on a clock. Next we widen the lens to full production deployment: packaging, monitoring, and the governance policy you will write for the agent team you ship as your final project.

## 5. Further Reading

- crontab and `systemd.timer` manual pages (`man 5 crontab`, `man 5 systemd.timer`).
- GitHub Actions, Events that trigger workflows: the `schedule` trigger. https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule
- This course's *From Second Brain to Chief of Staff: A Personal Agent in Production* (governed autonomy, scheduled/no-agent routines, catch-up policy) and *The LLM Wiki Pattern* (an n8n nightly clone->process->commit agent).
- This course's *Human-in-the-Loop: Oversight, Escalation, and Appropriate Autonomy* and *Agentic OpenWebUI* (why OpenWebUI is stateless-per-request and orchestration lives in your code).
- Ollama API (`/api/chat`) and OpenWebUI (`/api/chat/completions`) docs, for the model call a scheduler drives.
