---
layout: assignment
permalink: /Assignments/ToolsMCP
title: "CS357: Foundations of Artificial Intelligence - Lab: Tools and MCP"

info:
  coursenum: CS357
  points: 100
  goals:
    - To give an agent real tools using native function calling, and to know which side of the boundary your code owns
    - To make an agent reason explicitly, and to measure whether the reasoning paid for itself
    - To both author and consume an MCP server, and to articulate what the protocol standardizes
    - To constrain model output so that downstream code can parse it reliably rather than hopefully
  rubric:
    - weight: 30
      description: "Tool Use"
      preemerging: "No working tool call, or the model is asked for a tool but nothing executes."
      beginning: "A tool is called, but the schema is untyped or the result is not fed back to the model as a tool-role message."
      progressing: "A typed tool is registered and invoked end to end, with a transcript showing the round trip."
      proficient: "A typed tool is registered and invoked end to end, the transcript shows request and execution and the fed-back result, and the writeup names precisely what your code is responsible for that the model is not."
    - weight: 20
      description: "Structured Output"
      preemerging: "Output is parsed ad hoc from prose; no technique demonstrated."
      beginning: "A structured-output technique is used but no failure case is shown, so the reliability claim is untested."
      progressing: "One technique is demonstrated with a before-and-after: naive parsing breaks on a real response, the constrained version does not."
      proficient: "As progressing, and the writeup distinguishes which techniques guarantee validity by construction from those that merely encourage it, with the evidence to back the distinction."
    - weight: 25
      description: "Reasoning, Measured"
      preemerging: "No reasoning variant, or no comparison."
      beginning: "A reasoning variant exists but is compared informally, without a fixed task set or a fixed seed."
      progressing: "Plain and reasoning versions run over at least eight fixed tasks at a fixed seed, with an accuracy delta reported."
      proficient: "As progressing, plus the token and latency cost of the reasoning, and a defensible sentence on when that cost was earned and when it was not."
    - weight: 20
      description: "MCP"
      preemerging: "No MCP work."
      beginning: "An MCP server or client is configured but no discover-and-invoke round trip is shown."
      progressing: "A transcript shows tool discovery followed by a successful invocation."
      proficient: "As progressing, and the writeup states what MCP standardizes that a hand-rolled tools list does not - and, for the consume option, names the trust question raised by running someone else's tool definitions."
    - weight: 5
      description: "Writeup and Reproducibility"
      preemerging: "No writeup, or one that cannot be followed."
      beginning: "A writeup exists but a reader could not reproduce the runs from it."
      progressing: "Model, parameters, and commands are recorded well enough to reproduce."
      proficient: "Fully reproducible, with an AI-use disclosure naming what was AI-assisted and how it was verified."

tags:
  - lab

---

# Lab: Tools and MCP

The Local Agent Lab built an agent that perceives, plans, and acts in a loop - but its only action was producing text. This lab gives it hands.

The three capabilities below were previously bolted onto the Local Agent Lab, where they were due before the sessions that teach them. They now stand on their own, handed out the day we cover tool use and due after we cover MCP, so that every part of this lab is something you have already seen in class.

**Prerequisites, all taught before this lab is due:** the Tool Use and Function Calling session, the MCP and APIs session, and the structured-output reading attached to both.

## The Three Capabilities

Every submission must show that you can make an agent **use a tool**, make an agent **reason**, and work with **MCP** (the Model Context Protocol). Each capability comes in two flavors — build it **from scratch** (you own the wiring) or drive it **from a framework / served model / existing server** (you own the configuration). **Complete at least one option from Tool Use, at least one from Reasoning, and at least one from MCP.** You may do both flavors of one if it interests you, but one of each capability is the floor. Fold your chosen options into your writeup with the transcript evidence each one asks for.

> **Required for everyone — Structured output.** Before your tool-use option can be trusted, the model has to return data your code can parse *reliably*, not free-form prose that happens to contain JSON. As part of your Tool Use exploration, demonstrate **one** structured-output technique and show it recovering from a case where naive parsing fails. Pick one:
> - **Ollama's `format` parameter** — pass a JSON Schema (or `"json"`) in the request so the server constrains the response to valid JSON. See the [Ollama structured outputs docs](https://docs.ollama.com/capabilities/structured-outputs).
> - **[Instructor](https://python.useinstructor.com/integrations/ollama/)** — define a Pydantic model (a typed schema much like the dataclasses you already write) and let Instructor validate and auto-retry until the response conforms.
> - **[Outlines](https://github.com/dottxt-ai/outlines)** — constrain decoding to a grammar/regex/JSON schema so invalid tokens are *impossible*, not merely discouraged.
>
> Deliver: a two-or-three-sentence note in your writeup showing a before (free-form parse breaks on a real model response) and after (constrained output parses every time), and one sentence on which of the three guarantees validity versus merely encourages it. This is the reliability glue the rest of your agent's tool-calling depends on.

**Tool Use — pick at least one:**

<details markdown="1">
<summary><strong>Tool Use · From Scratch — expose a function to the model</strong></summary>

Give your agent a real, typed tool using **native function calling** (not the week-1 regex parse). Define a Python function, describe it as a JSON schema in a `tools` list, and let the model emit a structured `tool_calls` request that your code executes and feeds back as a `tool`-role message. Do this against Ollama's `/api/chat` *or* OpenWebUI's OpenAI-compatible `/api/chat/completions` — the schema is identical across both (see the [Tool Use and Function Calling activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-tooluse.md), Parts II–2b). Deliver: your tool schema, a transcript showing the model requesting the tool and your program executing it, and one sentence on what your code — not the model — is responsible for.

</details>

<details markdown="1">
<summary><strong>Tool Use · From a Framework — give an agent tools you did not wire</strong></summary>

Hand the same tool to an agent through a framework so the framework owns the tool-calling loop. Register a Python function as a tool with **smolagents** (Hugging Face's lightweight agent library — the gentlest starting point), LangChain/DeepAgents, or Agno, and let it drive invocation (see the [Agent Frameworks activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentframeworks.md), including how to point the framework at your local Ollama/OpenWebUI model). If you are new to frameworks, prefer smolagents: it is a much thinner wrapper than LangChain, so less of the loop is hidden and the code you write stays close to the from-scratch version. Deliver: the tool registration, a run transcript, and two things the framework hid from you that you had to do by hand in the from-scratch version.

</details>

**Reasoning / Thinking — pick at least one:**

<details markdown="1">
<summary><strong>Reasoning · From Scratch — make the agent think, and measure it</strong></summary>

Add explicit reasoning to your agent and test whether it helps. Either (a) insert a scratchpad/chain-of-thought step where the model reasons before it answers, or (b) spend **test-time compute**: sample several reasoning paths at nonzero temperature and select the best (majority vote or a self-check). Run both the plain and the reasoning version over a fixed set of at least eight tasks at a fixed seed, and report the accuracy delta *and* the extra tokens/latency it cost. Deliver: both versions, the paired results table, and a sentence on when the extra reasoning earned its cost. Concepts are in the [model-types lecture](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-modeltypes.md).

</details>

<details markdown="1">
<summary><strong>Reasoning · From a Model/User Perspective — use a reasoning model</strong></summary>

Drive reasoning by *choosing the model* rather than building the loop. Run a reasoning-capable model (or toggle a "think step by step" / extended-thinking mode where your server supports it) and compare it against a direct-answer model on the same eight-task set. Report accuracy, latency, and token cost for each, and identify a task type where the reasoning model clearly wins and one where it is wasteful. Deliver: the comparison table and a short recommendation on which model you would ship for this workload and why. See the [model-types lecture](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-modeltypes.md) for what makes a model a "reasoning" model.

</details>

**MCP (Model Context Protocol) — pick at least one:**

<details markdown="1">
<summary><strong>MCP · Create — stand up your own MCP server</strong></summary>

Expose your tool(s) over MCP so *any* MCP-aware client can discover and call them, not just your own loop. Build a small MCP server (e.g. with the Python MCP SDK / FastMCP) that advertises one or two tools, then connect a client and show the discover → invoke round-trip. Deliver: the server code, a transcript of a client listing the tools and calling one, and one sentence on what MCP standardizes that a hand-rolled `tools` list does not. *(If you take the [MCP Server with OAuth 2.0 direction](LocalAgent/Direction4), that fully satisfies this option.)* Background: the [MCP activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-mcp.md) and the free [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course/) (built with Anthropic), whose early units walk through building and connecting an MCP server step by step.

</details>

<details markdown="1">
<summary><strong>MCP · Use — connect your agent to an existing MCP server</strong></summary>

Consume MCP instead of authoring it. Point your agent (or a framework client) at an existing MCP server — for example a filesystem, fetch, or SQLite server — and let it discover the server's tools and call them to complete a task. Deliver: the connection/config, a transcript showing tool discovery and at least one successful invocation, and one sentence on the trust question this raises (you are now running someone else's tool definitions). Background: the [MCP activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-mcp.md).

</details>

---

## Low-Code Route (equal credit)

You may complete this lab **without writing tool-calling code**, by wiring the same three capabilities in Open WebUI or Langflow. The learning goal is identical — understand what a tool call is, when the model chooses one, and how it fails — and so is the credit.

**How to do it:**

1. **Give the model a tool without code.** In Open WebUI, enable a built-in tool (web search, or the code interpreter) for one model, or import a community tool. In Langflow, drag a **Tool** node onto the canvas and connect it to an **Agent** node.
2. **Watch the decision, not the output.** Ask three questions: one the model can answer from memory, one that clearly needs the tool, and one that is ambiguous. For each, capture *whether the tool fired* — Open WebUI shows the tool invocation inline; Langflow highlights the executed path.
3. **Break it on purpose.** Disconnect the tool (or revoke its permission) and re-ask the question that needed it. Record what the model does when the capability disappears: does it say so, or does it invent an answer?

**What you submit instead of code:** screenshots of the flow or tool configuration, a table of your three questions with *tool fired: yes/no* and the answer given, and the same written analysis the code route requires. The analysis is where the grade lives, and it is unchanged.

> Choosing this route is not the easy way out — you still have to explain *why* the model called the tool when it did, which is the hard part either way.

## What to Submit

One repository or archive containing your code, plus a writeup that includes, for each of the three capabilities, the deliverable that capability asks for. Record the model and parameters you used so a reader can reproduce your runs, and include an AI-use disclosure naming what was AI-assisted and how you verified it.

## Estimated Effort

Roughly 6 to 8 hours: about 2 hours for tool use plus structured output, 2 to 3 for the reasoning comparison (most of it waiting on runs), and 2 to 3 for MCP. The reasoning comparison is the one to start early, because eight tasks times two conditions is a lot of wall-clock time if you leave it to the last night.
