---
layout: assignment
permalink: /Assignments/DeepAgents
title: "CS357: Foundations of Artificial Intelligence - Lab: Build a Deep Agent with Planning, Subagents, and a Virtual Filesystem, Traced in LangSmith"

info:
  coursenum: CS357
  points: 100
  goals:
    - To build a deep agent with LangChain's create_deep_agent that uses planning, a virtual filesystem, and at least one subagent on a long, multi-step task
    - To compare the deep agent against a flat tool-calling baseline on the same task and explain the difference in terms of the context window
    - To instrument the agent with LangSmith and read the resulting trace to locate where work and tokens go
    - To diagnose at least one failure by reading the trace rather than the final output
    - To articulate when a deep agent is the wrong tool for a task
  rubric:
    - weight: 30
      description: Deep Agent Implementation
      preemerging: No working deep agent is submitted, or it does not run
      beginning: The agent runs but uses none of the deep-agent pillars beyond a basic tool-calling loop (no plan, no files, no subagent)
      progressing: The agent runs and demonstrably uses at least two pillars (e.g., a plan via write_todos and the virtual filesystem) on a genuinely multi-step task
      proficient: The agent runs on a long, multi-step task and demonstrably uses planning, the virtual filesystem, and at least one subagent; the instructions are well-crafted so each pillar is used purposefully, and the created files are inspected and included in the writeup
    - weight: 25
      description: Flat vs Deep Comparison
      preemerging: No baseline comparison is provided
      beginning: A flat baseline is mentioned but not run, or the comparison is purely assertion
      progressing: Both a flat agent and the deep agent are run on the same task with their outputs shown, and a difference is described
      proficient: Both agents are run on an identical long task with outputs shown side by side, the difference in completeness or quality is documented with specifics, and the explanation correctly attributes the difference to context-window pressure (overflow, drift, or lack of structure)
    - weight: 25
      description: LangSmith Tracing and Diagnosis
      preemerging: No trace is captured
      beginning: Tracing is enabled and a screenshot or export is included, but it is not interpreted
      progressing: The trace is captured and the student identifies the plan, tool calls, and subagent spans within it
      proficient: The trace is captured and read as a tree; the student locates the plan, file writes, and subagent spans, reports where tokens/time concentrated, and uses the trace (not the final output) to diagnose at least one weakness, stating the next diagnostic step
    - weight: 20
      description: Judgment and Reflection
      preemerging: No discussion of when a deep agent is inappropriate is provided
      beginning: The reflection restates what was built without evaluating fit
      progressing: The reflection names at least one task type where a deep agent is overkill, with a brief reason
      proficient: The reflection gives a clear flat-vs-deep decision rule grounded in the lab's evidence, names the new failure modes a deep agent introduces (bad plan, runaway subagent, added latency/cost), and connects the privacy caveat of tracing to the observability lab
  readings:
    - rtitle: "Deep Agents: Planning, Subagents, and a Virtual Filesystem (LangChain) with LangSmith Tracing"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-deepagents.md"
    - rtitle: "Hands-on Notebook: Deep Agents + LangSmith (files/notebooks/deepagents_langsmith_tutorial.ipynb)"
      rlink: "https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/files/notebooks/deepagents_langsmith_tutorial.ipynb"
    - rtitle: "Agent Frameworks Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentframeworks.md"
    - rtitle: "Agent Observability Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-observability.md"

tags:
  - agents
  - langchain
  - deepagents
  - observability

---

In this lab, you build an agent that can actually finish a marathon. A flat tool-calling agent loses the thread on a long task because everything competes for one context window; a **deep agent** fixes this architecturally with a plan, a scratch filesystem, and subagents. You will build one with LangChain's `create_deep_agent`, race it against a flat baseline on the same task, and then make its hidden reasoning visible with **LangSmith** so you can debug it like a professional. Start from `files/notebooks/deepagents_langsmith_tutorial.ipynb`. This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

---

## Before You Start

### Prerequisites

- The **Deep Agents** activity and the tutorial notebook (linked above).
- The **Agent Frameworks** and **Agent Observability** activities.
- A working **Ollama** install with a tool-capable model (e.g., `llama3.1`); no paid API required.
- A free **LangSmith** account (<https://smith.langchain.com>) for an API key. If you genuinely cannot use LangSmith, you may substitute Langfuse or LangChain's local callback logging and explain the substitution — but a trace of some kind is required.

---

## Part A — Pick a Long Task

Choose a task that genuinely needs multiple steps and benefits from offloading — for example: "audit a small folder of source files for hardcoded secrets and write a remediation report," "turn a directory of rough notes into a structured study guide," or "research a question across several stub sources and produce a cited summary." A one-shot Q&A does **not** qualify; the point is to stress a flat agent.

## Part B — Build the Flat Baseline

Implement a flat tool-calling agent (the notebook's step 1) for your task. Run it and save the output. Note specifically where it falls short on the long task.

## Part C — Build the Deep Agent

Using `create_deep_agent`, implement the same task so that it **demonstrably** uses:

1. **Planning** (`write_todos`),
2. the **virtual filesystem** (writes and reads at least one file), and
3. at least one **subagent** (the `task` tool) for an isolated piece of work.

Run it, inspect the created files (the `files` key of the returned state), and save the output.

## Part D — Trace It in LangSmith

Enable tracing (`LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`) and re-run the deep agent. From the trace:

1. Identify the plan, the file writes, and the subagent span(s) in the tree.
2. Report where tokens and time concentrated.
3. **Diagnose one weakness using the trace, not the final output** (e.g., a thin subagent report, a plan that skipped a step), and state your next diagnostic step.

## Part E — Compare and Judge

1. Put the flat and deep outputs side by side; document the difference and attribute it to context-window pressure (overflow, drift, or no structure).
2. State a **flat-vs-deep decision rule** grounded in your evidence, and name the new failure modes a deep agent introduces.

---

## What to Submit

- Your notebook (or scripts) for the flat baseline and the deep agent, runnable from the documented setup.
- The deep agent's created files (including the final report) and the side-by-side output comparison.
- A LangSmith trace export or screenshots, with your annotations identifying the plan, file writes, and subagent spans, plus the documented diagnosis from Part D.
- Your Part E decision rule and reflection (including the tracing privacy caveat).
- Your driver/navigator swap log.
