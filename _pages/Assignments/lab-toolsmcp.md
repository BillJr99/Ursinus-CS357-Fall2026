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
      proficient: "A typed tool is registered and invoked end to end, the transcript shows request and execution and the fed-back result, and the writeup names precisely what your code is responsible for that the model is not. On the no-code and low-code routes, the exported chat transcript or Langflow run showing the tool firing stands in for the code transcript; the requirement to name the boundary precisely is unchanged and carries the row."
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
      proficient: "As progressing, plus the token and latency cost of the reasoning, and a defensible sentence on when that cost was earned and when it was not. On a no-code route, wall-clock time and response length are acceptable stand-ins for latency and token counts, provided the measurement method is stated."
    - weight: 20
      description: "MCP"
      preemerging: "No MCP work."
      beginning: "An MCP server or client is configured but no discover-and-invoke round trip is shown."
      progressing: "A transcript shows tool discovery followed by a successful invocation."
      proficient: "As progressing, and the writeup states what MCP standardizes that a hand-rolled tools list does not, and, for the consume option, names the trust question raised by running someone else's tool definitions. Consuming a server through a client's configuration file earns this row on the same terms as consuming it from code."
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

The Local Agent Lab built an agent that perceives, plans, and acts in a loop, but the only action it could take was producing text.  This lab gives it hands.

The three capabilities below were previously bolted onto the Local Agent Lab, where they were due before the sessions that teach them.  They now stand on their own, handed out the day we cover tool use and due after we cover MCP, so that every part of this lab is something you have already seen in class.

**Prerequisites, all taught before this lab is due:** the Tool Use and Function Calling session, the MCP and APIs session, and the structured-output reading attached to both.

## Before You Start

**This builds on:** the *Tool Use and Function Calling* session (which this lab is handed out on), the *Connecting Agents to the World: MCP and APIs* session (before it is due), and the structured-output reading attached to both.  It also assumes the agent loop you built in the **Local Agent Lab**: this lab gives that agent hands.

**You need**, on the code route:

```bash
curl -s http://localhost:11434/api/tags | head -c 120   # Ollama answering
python3 -c "import requests; print('requests ok')"
ollama pull llama3.2                                    # a model that supports tool calling
```

On the low-code route you need Open WebUI or Langflow running; on the no-code route, Open WebUI alone.

> **One thing to check now rather than at hour four:** not every local model does native function calling well, and a model that does not will simply produce prose describing a tool call instead of emitting one.  Test with a trivial tool before you build anything real.  If your model will not emit tool calls, say so in your writeup, switch models, and note what you observed; that observation is worth more than a clean run on a model you did not choose deliberately.

Please start the reasoning comparison early.  Eight tasks times two conditions is mostly wall-clock waiting, and it is the one part of this lab you cannot compress on the last night.

**What you will have at the end:** an agent that can act on the world, a demonstrated technique for making its output parseable, a measured answer to "did making it reason pay for itself," and a working relationship with the protocol the rest of the ecosystem is standardizing on.

---

## Choose Your Path

The three capabilities and the writeup are the same on every route.  What differs is whether you build the wiring or configure it.

| Route | Tool use | Reasoning | MCP | Pick this if |
|-------|----------|-----------|-----|--------------|
| **No-code** | Enable a built-in or community tool on a model in **Open WebUI** and observe the invocation inline | Compare a plain model against a reasoning-prompted one across your eight fixed tasks, both run in the chat interface | Add an MCP server to Open WebUI's tool settings and show discovery, then invocation | You want your attention on *when the model chooses to call a tool*, which is the hard part, rather than on the plumbing |
| **Low-code** | A **Tool** node wired to an **Agent** node in **Langflow** | The same comparison, as two flows | Configure an MCP server in a client's config file, show discovery and invocation | You think better in a diagram, or you want the visual trace of which path executed |
| **Code** | Register a typed tool and own the executor loop | Two runners over a fixed task set at a fixed seed | Author a small MCP server, or consume one from code | You are heading for the Local Agent Lab's MCP and OAuth direction |

Every route must still show **structured output** (below), and every route needs a transcript.  On the no-code route, that means exporting the chat rather than pasting a screenshot of the answer: the tool invocation record is the evidence, not the reply.

> **Do not read the no-code column as "the version without the hard part."**  The hard part of this lab is explaining *why the model called the tool when it did and not when it didn't*, and that question is identical in all three columns.  What the code route buys you is a clearer view of the boundary between what your code owns and what the model owns; what the no-code route buys you is more time looking at the decision itself.

---

## The Three Capabilities

Every submission must show that you can make an agent **use a tool**, make an agent **reason**, and work with **MCP** (the Model Context Protocol).  Each capability comes in two flavors: build it **from scratch** (you own the wiring) or drive it **from a framework / served model / existing server** (you own the configuration).  **Complete at least one option from Tool Use, at least one from Reasoning, and at least one from MCP.** You may do both flavors of one if it interests you, but one of each capability is the floor.  Fold your chosen options into your writeup with the transcript evidence each one asks for.

> **Required for everyone, Structured output.**  Before your tool-use option can be trusted, the model has to return data your code can parse *reliably*, not free-form prose that happens to contain JSON. As part of your Tool Use exploration, demonstrate **one** structured-output technique and show it recovering from a case where naive parsing fails.  Pick one:
> - **Ollama's `format` parameter**: pass a JSON Schema (or `"json"`) in the request so the server constrains the response to valid JSON. See the [Ollama structured outputs docs](https://docs.ollama.com/capabilities/structured-outputs).
> - **[Instructor](https://python.useinstructor.com/integrations/ollama/)**: define a Pydantic model (a typed schema much like the dataclasses you already write) and let Instructor validate and auto-retry until the response conforms.
> - **[Outlines](https://github.com/dottxt-ai/outlines)**: constrain decoding to a grammar/regex/JSON schema so invalid tokens are *impossible*, not merely discouraged.
>
> Deliver: a two-or-three-sentence note in your writeup showing a before (free-form parse breaks on a real model response) and after (constrained output parses every time), and one sentence on which of the three guarantees validity versus merely encourages it.  This is the reliability glue the rest of your agent's tool-calling depends on.

**Tool Use, pick at least one:**

<details markdown="1">
<summary><strong>Tool Use · From Scratch, expose a function to the model</strong></summary>

Give your agent a real, typed tool using **native function calling** (not the week-1 regex parse).  Define a Python function, describe it as a JSON schema in a `tools` list, and let the model emit a structured `tool_calls` request that your code executes and feeds back as a `tool`-role message.  Do this against Ollama's `/api/chat` *or* OpenWebUI's OpenAI-compatible `/api/chat/completions`; the schema is identical across both (see the [Tool Use and Function Calling activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-tooluse.md), Parts II-2b).  Deliver: your tool schema, a transcript showing the model requesting the tool and your program executing it, and one sentence on what your code (not the model) is responsible for.

</details>

<details markdown="1">
<summary><strong>Tool Use · From a Framework, give an agent tools you did not wire</strong></summary>

Hand the same tool to an agent through a framework so the framework owns the tool-calling loop.  Register a Python function as a tool with **smolagents** (Hugging Face's lightweight agent library, the gentlest starting point), LangChain/DeepAgents, or Agno, and let it drive invocation (see the [Agent Frameworks activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-agentframeworks.md), including how to point the framework at your local Ollama/OpenWebUI model).  If you are new to frameworks, prefer smolagents: it is a much thinner wrapper than LangChain, so less of the loop is hidden and the code you write stays close to the from-scratch version.  Deliver: the tool registration, a run transcript, and two things the framework hid from you that you had to do by hand in the from-scratch version.

</details>

**Reasoning / Thinking, pick at least one:**

<details markdown="1">
<summary><strong>Reasoning · From Scratch, make the agent think, and measure it</strong></summary>

Add explicit reasoning to your agent and test whether it helps.  Either (a) insert a scratchpad/chain-of-thought step where the model reasons before it answers, or (b) spend **test-time compute**: sample several reasoning paths at nonzero temperature and select the best (majority vote or a self-check).  Run both the plain and the reasoning version over a fixed set of at least eight tasks at a fixed seed, and report the accuracy delta *and* the extra tokens/latency it cost.  Deliver: both versions, the paired results table, and a sentence on when the extra reasoning earned its cost.  Concepts are in the [model-types lecture]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-modeltypes.md).

</details>

<details markdown="1">
<summary><strong>Reasoning · From a Model/User Perspective, use a reasoning model</strong></summary>

Drive reasoning by *choosing the model* rather than building the loop.  Run a reasoning-capable model (or toggle a "think step by step" / extended-thinking mode where your server supports it) and compare it against a direct-answer model on the same eight-task set.  Report accuracy, latency, and token cost for each, and identify a task type where the reasoning model clearly wins and one where it is wasteful.  Deliver: the comparison table and a short recommendation on which model you would ship for this workload and why.  See the [model-types lecture]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-modeltypes.md) for what makes a model a "reasoning" model.

</details>

**MCP (Model Context Protocol), pick at least one:**

<details markdown="1">
<summary><strong>MCP · Create, stand up your own MCP server</strong></summary>

Expose your tool(s) over MCP so *any* MCP-aware client can discover and call them, not just your own loop.  Build a small MCP server (e.g. with the Python MCP SDK / FastMCP) that advertises one or two tools, then connect a client and show the discover -> invoke round-trip.  Deliver: the server code, a transcript of a client listing the tools and calling one, and one sentence on what MCP standardizes that a hand-rolled `tools` list does not.  *(If you take the [MCP Server with OAuth 2.0 direction](LocalAgent/Direction4), that fully satisfies this option.)*  Background: the [MCP activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-mcp.md) and the free [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course/) (built with Anthropic), whose early units walk through building and connecting an MCP server step by step.

</details>

<details markdown="1">
<summary><strong>MCP · Use, connect your agent to an existing MCP server</strong></summary>

Consume MCP instead of authoring it.  Point your agent (or a framework client) at an existing MCP server (for example a filesystem, fetch, or SQLite server) and let it discover the server's tools and call them to complete a task.  Deliver: the connection/config, a transcript showing tool discovery and at least one successful invocation, and one sentence on the trust question this raises (you are now running someone else's tool definitions).  Background: the [MCP activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-mcp.md).

</details>

---

## Build and Call a Tool: The Full Walkthrough

In this section you define three tools using the OpenAI function-calling JSON schema format (the standard way to describe a tool's name, purpose, and parameters as a JSON object) and call them from your local model via Ollama's `/api/chat` endpoint.  Run all code locally; no external API keys or cloud services needed.

**Files you will create.**  Everything below goes in one folder (call it `tools-lab/`) as three files, built in this order:

| File | Holds | Section |
|---|---|---|
| `tool_definitions.py` | The `TOOLS` list: each tool's name, description, and JSON Schema | Tool Definitions |
| `tool_impl.py` | The Python functions themselves plus the `REGISTRY` that maps a name to a function | Tool Implementations |
| `agent.py` | The loop that calls the model, dispatches tool calls, and feeds results back | The Agent Loop |

Splitting them this way is the point of the exercise, not bookkeeping: the model only ever sees `tool_definitions.py`, never the code in `tool_impl.py`.  Keeping them in separate files makes that boundary visible.  If you would rather work in a single file or a notebook, that is fine; just keep the three parts in clearly separated, labeled sections.

---

### Tool Definitions

Create `tool_definitions.py`.  Each tool is a JSON object with a `name`, a `description` (the only thing the model reads to decide whether to use this tool), and a `parameters` block written in JSON Schema:

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Evaluates a simple arithmetic expression and returns the numeric result. "
                "Use this whenever the user asks for a calculation, not for counting words."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A valid Python arithmetic expression using only numbers and "
                            "operators +, -, *, /, **, and parentheses. "
                            "Example: '(3 + 4) * 2' or '2 ** 10'."
                        )
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": (
                "Returns the current local date and time as a string. "
                "Call this whenever the user asks what time or date it is."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "word_count",
            "description": (
                "Counts the number of words in the provided text and returns the integer count. "
                "Use this when the user asks how many words are in a passage or sentence."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text whose words should be counted."
                    }
                },
                "required": ["text"]
            }
        }
    },
]
```

---

### Tool Implementations and the Executor Pattern

Create `tool_impl.py`.

The executor pattern keeps a **registry** (a plain Python dictionary mapping tool names to their implementations).  Your agent loop never calls a tool directly from the model's request; it looks up the name in the registry first.  This is the security boundary: only tools you explicitly register can ever run.  Notice that the `calculator` function uses Python's `ast` module (a library for safely parsing code into a tree of operations) rather than `eval()`; see the note after the code block for why this matters.

```python
import ast
import operator
import datetime

# Safe arithmetic evaluator - no eval() of arbitrary code
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def _safe_eval(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported node type: {type(node)}")

def calculator(expression: str) -> str:
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except Exception as e:
        return f"error: {e}"

def get_current_time() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def word_count(text: str) -> str:
    return str(len(text.split()))

REGISTRY = {
    "calculator": calculator,
    "get_current_time": get_current_time,
    "word_count": word_count,
}
```

Note that `calculator` uses Python's `ast` module to parse the expression rather than calling `eval()`.  This is intentional: `eval()` on a model-supplied string is an arbitrary code execution vulnerability.  The `_safe_eval` function only handles numeric literals and the four arithmetic operators, so the model cannot inject `import os; os.system(...)` or any other dangerous expression.

---

### The Agent Loop

Create `agent.py`, importing `TOOLS` from `tool_definitions.py` and `REGISTRY` from `tool_impl.py`.

```python
import json
import requests

def agent(question: str, max_steps: int = 5) -> str:
    msgs = [{"role": "user", "content": question}]

    for step in range(max_steps):
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3.2",
                    "stream": False,
                    "tools": TOOLS,
                    "options": {"temperature": 0.0, "seed": 42},
                    "messages": msgs,
                },
                timeout=120,
            ).json()["message"]
        except Exception as e:
            import traceback; traceback.print_exc()
            return f"request error: {e}"

        msgs.append(response)
        calls = response.get("tool_calls") or []

        if not calls:
            # Model chose to answer directly - no tool needed
            return response.get("content", "")

        for call in calls:
            name = call["function"]["name"]
            args = call["function"].get("arguments") or {}
            if name in REGISTRY:
                result = REGISTRY[name](**args)
            else:
                result = f"unknown tool: {name}"
            print(f"[tool] {name}({args}) -> {result}")
            # Tool result goes back as a 'tool' role message
            msgs.append({"role": "tool", "content": result})

    return "step budget exceeded"

# Test all three tools
print(agent("What is (144 / 12) ** 2?"))
print(agent("What time is it right now?"))
print(agent("How many words are in the sentence: 'The quick brown fox jumps over the lazy dog'?"))
```

---

### Critical Thinking Questions

7.  The model decides whether to call a tool based on the tool's **description**, not its name.  Change the `calculator` tool's description to `"counts the words in text"` and re-run the word-count question.  What does the model do?  What does this tell you about where the real "logic" of tool selection lives?

   > *Hint: The model never sees your Python function bodies; it only sees the JSON schema.  Swapping the description effectively swaps the tool's identity from the model's perspective.  Run `agent("How many words are in 'hello world'?")` with the swapped description and observe which tool fires.*

When the agent loop appends a tool result back into the conversation, what `role` value must that message use?

- `"user"`
- `"assistant"`
- `"tool"`
- `"system"`

<details><summary>Answer</summary>

`"tool"`

</details>

> *Hint: Look at the line `msgs.append({"role": "tool", "content": result})` in the agent loop.  The OpenAI-compatible API (which Ollama follows) requires the role `"tool"` so the model knows this message is a function result rather than a user turn or its own prior response.*

8.  Consider a fourth tool: `read_file(path: str) -> str` that opens a file path supplied by the user and returns its contents.  What security risk does this create, and what would you do to mitigate it?

   > *Hint: Think about what happens when the model (prompted by a malicious user) supplies the path `/etc/passwd`, `~/.ssh/id_rsa`, or `../../config/secrets.json`.  The mitigation involves restricting which directories the tool is allowed to read from: for example, only allowing paths that begin with an approved prefix such as `/home/user/documents/`.  You might also check that the resolved absolute path (after following symlinks with `os.path.realpath`) still begins with that prefix, to prevent path traversal attacks.*

> **Common Misconception:** Students often assume `tool_choice="auto"` means the model will always call a tool.  In reality, it means the model *may* call a tool if it decides one is needed, but it can also answer from memory without calling any tool at all.  If you need a specific tool to be invoked for every request (for safety, auditing, or consistency), set `tool_choice={"type": "function", "function": {"name": "tool_name"}}` to force it.  The difference matters for tools like `log_query` that you want called every time regardless of the model's judgment.

---

---

**In-class work stops here.**  The exercises below are homework and going-deeper material; attempt them before the related lab.


## The No-Code and Low-Code Routes, in Detail (equal credit)

You may complete this lab **without writing tool-calling code**, by wiring the same three capabilities in Open WebUI or Langflow.  The learning goal is identical (understand what a tool call is, when the model chooses one, and how it fails) and so is the credit.

**How to do it:**

1.  **Give the model a tool without code.**  In Open WebUI, enable a built-in tool (web search, or the code interpreter) for one model, or import a community tool.  In Langflow, drag a **Tool** node onto the canvas and connect it to an **Agent** node.
2.  **Watch the decision, not the output.**  Ask three questions: one the model can answer from memory, one that clearly needs the tool, and one that is ambiguous.  For each, capture *whether the tool fired*: Open WebUI shows the tool invocation inline; Langflow highlights the executed path.
3.  **Break it on purpose.**  Disconnect the tool (or revoke its permission) and re-ask the question that needed it.  Record what the model does when the capability disappears: does it say so, or does it invent an answer?

**What you submit instead of code:** screenshots of the flow or tool configuration, a table of your three questions with *tool fired: yes/no* and the answer given, and the same written analysis the code route requires.  The analysis is where the grade lives, and it is unchanged.

> Choosing this route is not the easy way out; you still have to explain *why* the model called the tool when it did, which is the hard part either way.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| The model describes a tool call in prose instead of emitting one | The model does not support native function calling, or the tools were passed in the prompt rather than in the `tools` field | Confirm your model supports tool calling; pass tools in the request's `tools` parameter, not as prose in the system prompt |
| The model calls the tool, then ignores the result | The result was never fed back as a `tool`-role message, so the model never saw it | Append the execution result to the message list with `"role": "tool"` and call again. The round trip is the whole mechanism |
| The tool fires on every question, including ones it should not | The tool description is too broad. The model chooses from the description alone | Rewrite the description to say when *not* to use it. Record the before and after; it is a good finding |
| The tool never fires, even on questions that need it | Description too narrow or too abstract, or the parameter schema is missing required fields | Compare your schema against a working one field by field. `required` is the usual omission |
| `json.loads` fails on the model's output | This is the failure the structured-output requirement exists to catch | Capture it. That broken parse *is* your "before"; do not fix it silently |
| MCP client reports zero tools | The server process is not running, the command path in the client config is wrong, or the transport does not match | Run the server by hand first and confirm it responds. Most MCP misconfiguration is a wrong path in a config file |
| The reasoning comparison shows no difference | Your eight tasks are too easy; both conditions get them all right | Pick tasks that need at least two steps. A ceiling at 8/8 measures your task set, not the model |
| Runs take forever | Eight tasks times two conditions times retries | Start it early, run it in the background, and use the waiting time for the MCP part |

---

## Self-Check Before You Submit

- [ ] **Tool use:** a transcript showing the request, the execution, and the result fed *back* to the model.
- [ ] The writeup names precisely what your code is responsible for that the model is not.
- [ ] **Structured output:** a real before (naive parse breaks on an actual response) and after (constrained output parses), plus one sentence on which techniques guarantee validity versus merely encourage it.
- [ ] **Reasoning:** at least eight fixed tasks, at a fixed seed, run in both conditions, with an accuracy delta.
- [ ] Cost reported alongside accuracy: tokens and latency, or a stated stand-in.
- [ ] One defensible sentence on when the reasoning cost was earned and when it was not.
- [ ] **MCP:** a transcript showing discovery followed by invocation.
- [ ] The writeup says what MCP standardizes that a hand-rolled tools list does not; if you consumed someone else's server, it names the trust question that raises.
- [ ] Model name and parameters recorded so a reader can reproduce your runs.
- [ ] Route named at the top of the writeup.
- [ ] AI-use disclosure included.

---

## What to Submit

One repository or archive containing your code, plus a writeup that includes, for each of the three capabilities, the deliverable that capability asks for.  Record the model and parameters you used so a reader can reproduce your runs, and include an AI-use disclosure naming what was AI-assisted and how you verified it.

## Estimated Effort

Roughly 6 to 8 hours: about 2 hours for tool use plus structured output, 2 to 3 for the reasoning comparison (most of it waiting on runs), and 2 to 3 for MCP. The reasoning comparison is the one to start early, because eight tasks times two conditions is a lot of wall-clock time if you leave it to the last night.
