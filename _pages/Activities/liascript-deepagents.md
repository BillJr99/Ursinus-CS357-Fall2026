# Deep Agents: Planning, Subagents, and a Virtual Filesystem (LangChain) with LangSmith Tracing
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-deepagents.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-deepagents.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Deep Agents: Planning, Subagents, and a Virtual Filesystem (LangChain) with LangSmith Tracing

A plain tool-calling agent is a sprint runner: great at short bursts, but it loses the thread on a marathon. Ask it to "research a topic, write a report, and revise it against a checklist" and it forgets step one by step five, because everything lives in a single, overflowing context window. **Deep agents** are LangChain's answer to the marathon: a "batteries-included" harness that adds four things a long task needs — an explicit **plan**, a **scratch filesystem** to offload work out of the context window, the ability to spawn **subagents** with their own fresh context, and **long-term memory**. We build one with `create_deep_agent`, watch it think, and then make its hidden reasoning visible with **LangSmith** tracing. The arc: **why long tasks break a flat agent $\rightarrow$ the four pillars of a deep agent $\rightarrow$ building one with `create_deep_agent` $\rightarrow$ tracing a run in LangSmith $\rightarrow$ when a deep agent is the wrong tool.**

> This activity is the lecture/POGIL companion to the hands-on notebook `files/notebooks/deepagents_langsmith_tutorial.ipynb` and the graded **Deep Agent lab** (`/Assignments/DeepAgents`). It builds on *Agent Frameworks* (`liascript-agentframeworks.md`), *Memory and Context* (`liascript-memorycontext.md`), and *Agent Teams* (`liascript-agentteams.md`).

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss as a team. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports disagreements. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Deep agent** | An agent harness designed for long, multi-step tasks by adding planning, a filesystem, and subagents on top of a normal tool-calling loop | A research agent that plans, writes notes to files, spawns a sub-researcher, then drafts a report |
| **Planning tool** (`write_todos`) | A built-in tool that lets the agent maintain a structured to-do list (pending / in-progress / done) it can revise as it works | The agent writes a 5-step plan, then checks items off as it completes them |
| **Virtual filesystem** | File tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`) backed by a pluggable store, used as working memory *outside* the context window | The agent saves retrieved passages to `notes.md` instead of holding them all in context |
| **Subagent** (`task` tool) | An ephemeral agent the main agent spawns for an isolated piece of work; it runs with a fresh context and returns a single report | The main agent delegates "summarize these 10 files" to a subagent so its own context stays clean |
| **Context offloading** | Moving information out of the context window (into files or a subagent) so the main agent's window stays small and focused | Writing intermediate results to disk and re-reading only what the next step needs |
| **LangSmith** | LangChain's observability platform that records a trace of every model call, tool call, and subagent for inspection and debugging | Opening a run and seeing the plan, each file write, and the subagent call as nested spans |

---

# Part I: Why a Flat Agent Breaks on Long Tasks

In this part, you will connect a familiar failure — an agent losing the thread on a long task — to its root cause in the context window, and see why "just use a bigger window" is not the fix.

## Model 1: The Marathon Problem

Recall the ReAct loop (`liascript-agentloop.md`): the agent alternates *thought → action → observation*, and **every** thought, action, and observation is appended to the context window. On a short task this is fine. On a long task three things go wrong at once:

- **Overflow:** the window fills with old observations and the agent runs out of room before finishing (the "perfectionism spiral" from `liascript-agentloopsadvanced.md`).
- **Drift:** as the window fills with detail, the original goal gets diluted and the agent wanders.
- **No structure:** with no explicit plan, the agent cannot tell how far along it is, so it repeats or skips steps.

"Use a model with a bigger context window" delays the wall but does not move it — and a fuller window also costs more and reasons worse (lost-in-the-middle). The real fix is **architectural**: stop trying to hold everything in the window. That is exactly what a deep agent does.

### Critical Thinking Questions

1. A flat agent is asked to "read these 12 source files and write a design doc." It produces a good doc about files 1–4 and ignores the rest. Diagnose this in terms of the context window. Which of the three failures above is most likely, and why?

2. Why does keeping the agent's context window *small* (a principle from `liascript-memorycontext.md`) actually *improve* reliability on long tasks, rather than just saving money? Argue it in terms of drift.

---

# Part II: The Four Pillars of a Deep Agent

In this part, you will map each deep-agent feature to the specific flat-agent failure it fixes, so the harness feels like a set of deliberate answers rather than magic.

## Model 2: Plan, Files, Subagents, Memory

| Pillar | What it adds | The failure it fixes |
|--------|--------------|----------------------|
| **Planning** (`write_todos`) | An explicit, revisable to-do list the agent maintains as state | "No structure" — the agent always knows the plan and its progress |
| **Virtual filesystem** | `read/write/edit/ls/glob/grep` over a scratch store used as working memory | "Overflow" — bulky intermediate work lives in files, not the window |
| **Subagents** (`task`) | Spawn an ephemeral agent with a *fresh* context that returns one report | "Drift" + "overflow" — isolated work never pollutes the main window |
| **Long-term memory** | A store that persists across runs/sessions | Continuity — the agent can resume and recall prior work |

The mental model: the **main agent is a manager.** It keeps a short plan, delegates bulky or specialized work to **subagents**, files paperwork in the **filesystem**, and keeps its own desk (context window) clear. This is the same instinct as the *Agent Teams* activity — except here one harness gives you the team structure for free.

### Critical Thinking Questions

3. A subagent runs with a *fresh* context and returns only a final report (a "single handoff"). State one major advantage and one real risk of that design. (Hint for the risk: what does the main agent *not* get to see?)

4. The filesystem and a subagent are two different ways to "offload context." Give a task where writing to a file is the better choice, and a task where spawning a subagent is better. What distinguishes them?

---

# Part III: Building One with `create_deep_agent`

In this part, you will read the smallest useful deep agent and identify where each pillar appears, so the API maps onto Model 2.

## Model 3: Three Parameters and You Have a Team

The headline of the harness is how little you write: a model, your custom tools, and an instruction string. Planning, the filesystem, and the subagent `task` tool are built in.

```python
# pip install deepagents langchain langsmith
from deepagents import create_deep_agent

def web_search(query: str) -> str:
    """Return search results for a query."""   # your real tool here
    ...

agent = create_deep_agent(
    model="ollama:llama3.1",          # any LangChain-compatible model; local is fine
    tools=[web_search],               # YOUR domain tools...
    instructions=(                    # ...the built-ins (plan, files, subagents) come free
        "You are a research assistant. Make a plan with write_todos first. "
        "Save sources and notes to files. Use a subagent to summarize long sources. "
        "Then write report.md and revise it against the checklist."
    ),
)

result = agent.invoke({"messages": [{"role": "user",
            "content": "Research local-vs-hosted LLM tradeoffs and write report.md"}]})
```

What you did *not* have to build: the to-do tool, the six file tools, the subagent spawner, or the loop that ties them together. What you still own: the **domain tools** and the **instructions** that tell the agent *how* to use the plan, files, and subagents. That instruction string is where a deep agent succeeds or fails — it is the agent's working agreement, the same idea as the how-I-work document in the CTP2 case study.

### Critical Thinking Questions

5. In the code above, point to where each Model-2 pillar shows up (planning, filesystem, subagents) — some are in the call, some are only in the *instructions*. What does it tell you that two of the pillars are invoked by **prose**, not by an argument?

6. `create_deep_agent` returns a compiled LangGraph graph. Tie this back to the *Agent Frameworks* table: what do you gain by the harness being "just LangGraph underneath" when you eventually hit something it does not do for you?

---

# Part IV: Making It Visible with LangSmith

In this part, you will reason about what a trace should show for a deep-agent run, connecting back to the observability pillars.

## Model 4: Reading a Deep-Agent Trace

A deep agent does a *lot* off-screen: it plans, writes files, and spawns subagents. Without tracing, a failure ("the report missed half the sources") is nearly impossible to debug. **LangSmith** records the run as nested spans — turning on tracing is just environment variables:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=ls-...        # from smith.langchain.com
export LANGSMITH_PROJECT=cs357-deepagents
# then run your agent normally; the trace appears in the LangSmith UI
```

A healthy trace for the research agent shows, as a tree: the **plan** (`write_todos`) near the top, a series of **tool calls** (search, `write_file`), one or more **subagent** spans each with their *own* nested calls, and a final **draft/revise** step. Reading it, you can answer: did the plan match the task? did a subagent return a thin report? where did time and tokens go? This is the *Observability* activity's three pillars (logs, metrics, traces) applied to a deep agent — and LangSmith is the LangChain-native sibling of the OpenTelemetry/Jaeger stack you used in the observability lab.

> **Privacy note (carried over from the observability lab):** a trace can capture raw prompts and tool inputs. Treat a LangSmith project like any log sink — do not send secrets or real personal data through a traced agent without thinking about retention.

### Critical Thinking Questions

7. You open the trace and the final report is weak. The plan looks correct, but one subagent's span shows it returned three sentences for "summarize these 8 files." Where is the bug most likely to be — the main agent, the subagent's instructions, or the file tools — and what is your next diagnostic step?

8. Compare debugging this run *with* the LangSmith trace versus *without* it (only the final output). Name two specific questions the trace answers that the output alone cannot.

---

# Part V: When NOT to Use a Deep Agent

A deep agent is overkill for a one-shot question and adds latency, cost, and new failure modes (a bad plan, a runaway subagent). Use a flat tool-calling agent when the task fits in one window and finishes in a few steps; reach for a deep agent when the task is long, open-ended, and benefits from planning and offloading.

### Critical Thinking Question

9. For each task, decide *flat agent* or *deep agent* and defend it in one sentence: (a) "What's the capital of France, and convert its population to millions?"; (b) "Audit this 30-file repo for hardcoded secrets and write a remediation report"; (c) "Summarize this one email." What feature of the task drives your choice each time?

---

## Reflective Prompt

In your notebook (3–5 sentences): Describe a multi-step task from another course or project that a *flat* agent would likely botch. Which one deep-agent pillar (plan, files, subagents, or memory) would help it most, and why? Then state one thing you would specifically look for in the LangSmith trace to confirm the agent actually used that pillar the way you intended.
