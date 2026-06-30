# Agent Traceability: Switching Models and Stop/Start/Resume for the Context Window
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-agenttraceability.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agenttraceability.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Agent Traceability: Switching Models and Stop/Start/Resume for the Context Window

A long agent session always ends the same way if you let it: the context window fills, the agent drifts, and the last good idea is buried under a thousand tokens of tool output. Skilled operators do not fight this by buying a bigger window — they **checkpoint**. They stop the agent at a clean boundary, write down just enough state to resume, and start a *fresh* session (sometimes on a *different* model) from that checkpoint. The discipline that makes this possible is **traceability**: leaving a durable, inspectable record of what the agent did and decided, so a stop is recoverable and a model swap is seamless. Today we use the most universal traceability tool there is — **git** — as the running example: we make a plan, let an agent start, hand off, and resume, with the repository as the shared memory. The arc: **why long sessions decay $\rightarrow$ traceability as durable state $\rightarrow$ the stop/checkpoint/resume loop $\rightarrow$ switching models mid-task $\rightarrow$ git as the worked use case.**

> Builds on *Advanced Agent Loops* (`liascript-agentloopsadvanced.md`), *Memory and Context* (`liascript-memorycontext.md`), *Agent Observability* (`liascript-observability.md`), and the CTP2 *how-I-work* document (`liascript-ctp2teammateprofile.md`).

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss as a team. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports disagreements. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Traceability** | A durable, inspectable record of what an agent did and why, separate from the volatile context window | A git history plus a `NOTES.md` checkpoint, so anyone can reconstruct the agent's progress |
| **Checkpoint** | A saved summary of just-enough state to resume cleanly later | A short "where we are / what's next" note written before stopping |
| **Stop/start (resume)** | Deliberately ending a session at a boundary and beginning a fresh one from the checkpoint | Stopping after the plan is committed, then resuming to implement it with an empty window |
| **Context window** | The finite text a model can attend to at once; every action adds to it | A 200k-token window that fills with tool output over a long task |
| **Model switching** | Moving a task from one model to another mid-flow, using the checkpoint as the handoff | Planning on a strong reasoning model, then implementing on a cheaper/faster one |
| **Handoff artifact** | The durable thing passed between sessions or models so neither relies on chat history | The branch + diff + `NOTES.md`, not "remember what we said earlier" |

---

# Part I: Why Long Sessions Decay

In this part, you will connect the context window's finiteness to the practical reason operators stop and resume rather than running one endless session.

## Model 1: The Window Always Wins

Recall from *Advanced Agent Loops* that **every** thought, action, and observation is appended to the context window. Over a long task this produces three compounding problems (the same ones that motivate deep agents): **overflow** (you hit the limit before finishing), **drift** (the goal dilutes as detail piles up), and **cost/quality decay** (a fuller window is slower, pricier, and reasons worse — "lost in the middle"). The naive responses — bigger window, "please remember everything" — only postpone the wall.

The professional response is to treat a session as **disposable** and the *record* as durable. You do not need the agent to remember the conversation if the important decisions are written down somewhere it can re-read. That somewhere is your traceability layer.

### Critical Thinking Questions

1. A teammate runs a single 6-hour agent session and is frustrated that quality "fell off a cliff" near the end. Explain what almost certainly happened in terms of the context window, and why starting three fresh 2-hour sessions from checkpoints would likely have done better.

2. "Just summarize the conversation when it gets long" is one tactic (in-context compaction). How is writing a checkpoint to a *file* a stronger form of the same idea? What does the file survive that an in-context summary does not?

---

# Part II: Traceability as Durable State

In this part, you will distinguish volatile context from durable trace, and identify what belongs in each.

## Model 2: Two Memories

| | Volatile (context window) | Durable (traceability layer) |
|---|---|---|
| **Lives in** | the model's current session | git history, `NOTES.md`, commit messages, observability traces |
| **Survives a restart?** | no | yes |
| **Survives a model swap?** | no | yes |
| **Good for** | the current step's reasoning | the plan, decisions, "where we are / what's next" |
| **Failure if overused** | overflow, drift | stale or missing checkpoints → cannot resume |

The art is deciding *what* to write down. Too little and you cannot resume; too much and the checkpoint itself becomes bloated. A good checkpoint answers three questions: **what is done, what is next, and what must not be forgotten** (constraints, gotchas, the charter's guardrails).

### Critical Thinking Questions

3. For an agent implementing a feature, sort these into volatile vs. durable: (a) the exact wording of the last tool error, (b) "the API key lives in an env var, never commit it," (c) the current half-finished function body, (d) "tests for module X still fail — fix next." Which durable items belong in a commit message vs. a `NOTES.md`?

4. The observability activity recorded traces for debugging. How is an observability trace *also* a traceability/handoff artifact? What can a LangSmith/OTel trace tell a resuming session that a `NOTES.md` might omit?

---

# Part III: The Stop / Checkpoint / Resume Loop

In this part, you will read the loop and identify clean boundaries for stopping.

## Model 3: Where to Cut

Not every moment is a good place to stop. The best boundaries are where the durable state is *consistent*: the build is green, work is committed, and a checkpoint is written. The loop:

```text
plan ──▶ work a bounded chunk ──▶ reach a clean boundary
  ▲                                     │
  │                                     ▼
resume from checkpoint ◀── write checkpoint + commit ◀── (stop here)
```

A "clean boundary" for a coding agent: tests pass (or are knowingly red and noted), changes are committed, and `NOTES.md` says what is done and what is next. Stopping mid-edit with an uncommitted, broken tree is the *worst* place to stop — the resume cost is huge.

### Critical Thinking Questions

5. Your agent is 40 minutes into a task and the window is 80% full. It is halfway through editing a function and the tests are red. Do you stop now or push to a boundary first? Describe the cheapest safe way to reach a clean checkpoint.

6. Connect this to the CTP2 *how-I-work* document. Which line in a how-I-work doc operationalizes this loop, and why does an autonomous (yolo-mode) agent need it written down explicitly rather than relying on a human to call the stop?

---

# Part IV: Switching Models Mid-Task

In this part, you will reason about handing a task from one model to another through the trace.

## Model 4: The Checkpoint Is the Handoff

Because the checkpoint is durable and model-agnostic, it doubles as a **model-switch** mechanism. A common pattern:

- **Plan** on a strong reasoning model — it produces the to-do list and the design decisions, committed to the repo.
- **Implement** on a cheaper/faster model — it reads the plan and grinds through the mechanical edits (tie-in: cost/routing, `liascript-costoptimization.md`).
- **Review** on a strong model again — it reads the diff and critiques.

Each handoff passes the *artifact* (branch + diff + `NOTES.md`), never "remember our chat." This is why traceability and model-switching are the same skill: if your state is durable enough to resume *yourself*, it is durable enough to resume a *different model*.

### Critical Thinking Questions

7. Why does a model swap *force* good traceability hygiene that a single-model session lets you get away with skipping? What silently-assumed context breaks the moment a different model reads your half-finished work?

8. Give one task where switching to a *cheaper* model mid-flow is clearly worth it, and one where switching models would be risky. What property of the work decides it?

---

# Part V: Git as the Worked Use Case (plan → start → hand off → resume)

Git is the traceability layer most teams already have. Walk this end-to-end loop; your team narrates what is in the *durable* layer at each step.

```bash
# 1. PLAN — capture the plan durably before the agent touches code
git checkout -b claude/feature-x
printf '# NOTES\n## Plan\n- [ ] step 1\n- [ ] step 2\n## Next\n- start step 1\n' > NOTES.md
git add NOTES.md && git commit -m "Plan feature-x"

# 2. START — agent works a bounded chunk, then reaches a clean boundary
#    (tests green or knowingly red and noted)
git add -A && git commit -m "Implement step 1; tests green"

# 3. HAND OFF — update the checkpoint so ANY session/model can resume
printf '## Next\n- step 2: wire X to Y; gotcha: do not rename the schema\n' >> NOTES.md
git add NOTES.md && git commit -m "Checkpoint: step 1 done, step 2 next"
#    (stop the session here; window is freed)

# 4. RESUME — a FRESH session (possibly a different model) reconstructs state
git log --oneline           # what happened
git diff HEAD~2             # what changed
cat NOTES.md               # what's next + gotchas
#    ...then continue from "## Next" with an empty context window
```

The key property: at every numbered step, a brand-new agent with **zero** chat history could read `git log`, the diff, and `NOTES.md` and keep going. That is traceability made concrete.

### Critical Thinking Questions

9. The loop above commits `NOTES.md` alongside the code. Argue for and against keeping the checkpoint *in the repo* (committed) versus *outside* it (a separate scratchpad). Which would you choose for an autonomous agent running in the hardened container, and why?

10. A resuming model reads `git log` and sees a commit "fix stuff" with a 600-line diff. Why is that commit a *traceability failure*, and what one habit from this activity would have prevented it?

---

## Reflective Prompt

In your notebook (3–5 sentences): Describe a long task (in this course or elsewhere) where you would want an agent to stop, hand off, and resume rather than run straight through. Identify your "clean boundary" for stopping, the three things your checkpoint would record (done / next / must-not-forget), and one point where you would deliberately switch models — and say what durable artifact makes that switch safe.
