---
layout: textbook
permalink: /Tutorials/PydanticAI
title: "CS357: Foundations of Artificial Intelligence - Pydantic AI From the Loop Up: Tools, Validation, the Agentic Loop, Memory, Skills, and MCP"
info:
  coursenum: CS357
  purpose: "To rebuild the hand-written agent loop in Pydantic AI one responsibility at a time, so that you can say exactly which pieces the framework took over (schemas, dispatch, retries, the loop, limits) and which stay yours (instructions, permissions, approvals, memory policy, and what counts as a correct answer)."
  eyebrow: "Tutorial"
  numbering: false
tags:
- agents
- frameworks
- pydantic
- mcp
- ollama
---

## About This Tutorial

You have already written an agent by hand.  The *Local Agent From Scratch* tutorial kept the message history in a list, parsed the model's requests, ran a safety gate before every command, and stopped after a fixed budget of steps.  The *Tool Use* deck's two-tool agent described `get_today` and `days_until` in JSON Schema, looked each request up in a registry, and appended every result as a `tool` message.  This tutorial keeps that same small task and moves it into [Pydantic AI](https://ai.pydantic.dev) one responsibility at a time.  Each part ends with two lists: what the framework did for you, and what is still yours.
{: .tb-lede}

Read this after the hand-written versions, not instead of them.  A framework is only a time saver once you can say what it is doing on your behalf, and the fastest way to say that is to have done it yourself first.  After this tutorial, Part V of *Agent Frameworks* shows the same framework from a different angle, by printing the context window, and the rest of that tutorial compares other frameworks.

> **Recommended order:** [Local Agent From Scratch]({{ site.baseurl }}/Tutorials/LocalAgentFromScratch), then the [Tool Use deck]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-tooluse.md) (its Part II two-tool agent), then this tutorial, then [Agent Frameworks, Part V]({{ site.baseurl }}/Tutorials/AgentFrameworks#part-v-hands-on-pydantic-ai-and-the-context-window), and only then the optional framework comparisons.
{: .tb-tip data-title="Reading path"}

---

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|---|---|---|
| **Pydantic** (core) | A validation library: a `BaseModel` with typed fields accepts data that fits and rejects data that does not.  It knows nothing about models or agents. | Part 2, and the P1 to P9 cells already in the decks |
| **Pydantic AI** | An agent framework from the same team.  It builds tool schemas from your type hints, runs the tool-calling loop, validates arguments and outputs with core Pydantic, and enforces limits. | Every part |
| **Tool** | A Python function the model may ask your program to run.  The docstring and type hints become its description and schema. | `@agent.tool_plain`, `@agent.tool` |
| **Dependencies** (`deps`) | The objects your tools need at run time (today's date, a folder, a database), passed in by your program rather than chosen by the model | Part 3, `RunContext[Deps]` |
| **`ModelRetry`** | An exception a tool or validator raises to send a correction back to the model, so the loop can recover | Parts 3 and 4 |
| **Approval** | A tool call that pauses the run until a person says yes or no | Part 3, `ApprovalRequired` |
| **Usage limits** | Hard caps on a run: `request_limit` counts model calls, `tool_calls_limit` counts tool executions | Part 5 |
| **Message history** | The list of everything said so far.  Passing it back in is short-term memory; saving it to disk makes it long-term. | Part 6 |
| **Toolset** | A group of tools from somewhere other than your file, such as an MCP (Model Context Protocol) server | Part 8, `MCPToolset` |
{: .tb-full}

---

## Part 0: Setup

Everything here runs against the Ollama server on your own machine.  Nothing calls a hosted model, and nothing sends traces anywhere: Pydantic AI only reports to Logfire if you install and configure Logfire, which this tutorial does not do.

```bash
python -m venv .venv && source .venv/bin/activate
pip install "pydantic-ai-slim[openai,mcp]==2.54.0" "fastmcp==4.0.11" "pytest==8.*"
ollama pull qwen2.5:3b     # this tutorial's default: a reliable tool caller (3B, about 1.9 GB)
ollama pull llama3.2       # the course's general chat model, for the comparisons (3B, about 2 GB)
```

> **Tested versions:** `pydantic-ai-slim` 2.54.0, `fastmcp` 4.0.11 (which brings `mcp` 2.3.0), `pydantic` 2.13.5, Python 3.13, and Ollama 0.40.0, on a 4-core CPU with no GPU.  Each model call in this tutorial took between 5 and 45 seconds on that machine.  Pydantic AI moves quickly, so if an import fails, check [ai.pydantic.dev](https://ai.pydantic.dev) before fighting the error.
{: .tb-warning data-title="Versions"}

Save this helper as `common.py`.  `make_model()` is the only place the code names a model, and `show_trace()` prints every message in a run so that you can compare it with the `[tool]` lines your hand-written loop printed.

> **Why qwen2.5:3b for tool calling:** The rest of the course uses `llama3.2` for chat, and it is fine there.  For tool calling, we switch to `qwen2.5:3b`, which is the same size and calls tools far more reliably.  When we ran this tutorial with `llama3.2`, it wrote a tool call as plain text instead of making one (Part 7), and it ignored a tool's result in its answer (Part 5).  `qwen2.5:3b` did neither.  Every output below comes from `qwen2.5:3b` unless it says otherwise, and setting `MODEL=llama3.2` reproduces the comparisons.  `qwen2.5:3b` is released under the Qwen Research License, so read its terms before using it outside class.
{: .tb-tip data-title="Model choice"}

```python
# common.py: one place that says which model the agent talks to, plus a trace printer.
import os

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")   # no start-up banner on every run

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider


def make_model():
    """A local Ollama model through its OpenAI-compatible endpoint. No hosted fallback.

    qwen2.5:3b is the default because it calls tools reliably; set MODEL=llama3.2 to compare.
    """
    provider = OllamaProvider(base_url=os.environ.get("BASE_URL", "http://localhost:11434/v1"),
                              api_key=os.environ.get("API_KEY"))
    return OpenAIChatModel(os.environ.get("MODEL", "qwen2.5:3b"), provider=provider)


def show_trace(messages):
    """Print every message part in a run: who wrote it, and what it said."""
    for m in messages:
        for part in m.parts:
            kind = part.part_kind
            if kind == "tool-call":
                print(f"  [{kind}] {part.tool_name}({part.args})")
            elif kind in ("tool-return", "retry-prompt"):
                print(f"  [{kind}] {getattr(part, 'tool_name', '')} -> {str(part.content)[:120]!r}")
            elif hasattr(part, "content"):
                print(f"  [{kind}] {str(part.content)[:120]!r}")
```

`MODEL=llama3.2 python step1_paired.py` switches models without editing code.  To go through OpenWebUI instead, set `BASE_URL=http://localhost:3000/api` and `API_KEY` to your OpenWebUI key.

---

## Part 1: The Same Two Tools, Both Ways

Here is the hand-written loop from the Tool Use deck, unchanged.  Run it first so that you have something to compare against:

```text
$ python raw_loop.py
[tool] days_until({'target_iso': '2026-12-07'}) -> 61
The last day of classes is 61 days from today.
```

Now the same task in Pydantic AI:

```python
# step1_paired.py: the Tool Use deck's two tools, now registered with Pydantic AI.
from datetime import date

from pydantic_ai import Agent, UsageLimits

from common import make_model, show_trace

agent = Agent(
    make_model(),
    instructions="Answer date questions. Use the tools for today's date and for day counts; never guess them.",
    model_settings={"temperature": 0.0, "seed": 42},
)


@agent.tool_plain
def get_today() -> str:
    """Returns today's date in ISO format (YYYY-MM-DD)."""
    return date.today().isoformat()


@agent.tool_plain
def days_until(target: date) -> int:
    """Returns the number of days from today until the target date (positive means the future).

    Args:
        target: The target date, for example 2026-12-07.
    """
    return (target - date.today()).days


result = agent.run_sync(
    "How many days until the last day of classes, December 7, 2026?",
    usage_limits=UsageLimits(request_limit=4),   # the deck's max_steps=4
)
print(result.output)
show_trace(result.all_messages())
print(result.usage)
```

```text
$ python step1_paired.py
There are 61 days until the last day of classes on December 7, 2026.
  [user-prompt] 'How many days until the last day of classes, December 7, 2026?'
  [tool-call] days_until({"target":"2026-12-07"})
  [tool-return] days_until -> '61'
  [text] 'There are 61 days until the last day of classes on December 7, 2026.'
RunUsage(input_tokens=520, output_tokens=53, requests=2, tool_calls=1)
```

The trace is the deck's Model 2 protocol: a user message, a model reply that asks for a tool, a tool result that **your program** wrote, and a final reply.  Pydantic AI did not change the protocol.  It wrote the parts of the program that every agent repeats.

| Responsibility | Hand-written loop (deck) | Pydantic AI | Still yours? |
|---|---|---|---|
| Message history | `msgs` list, appended by hand | Kept per run; `result.all_messages()` returns it | You decide what to keep between runs (Part 6) |
| Tool schema | `TOOLS` JSON written by hand | Generated from type hints and the docstring | You write a docstring the model can act on |
| Dispatch | `REGISTRY[name](**args)` | Only registered tools can run | You decide which tools exist |
| Argument validation | `date.fromisoformat` inside a `try` | Arguments validated against the hints; a bad value goes back to the model as a retry | You add rules a type cannot express (Part 3) |
| Stopping | `for _ in range(max_steps)` | Stops when the model answers without a tool call | You set the limits (Part 5) |
| Limits | `max_steps=4` | `UsageLimits(request_limit=4)`, plus `tool_calls_limit` and token limits | You choose the numbers |
| Permission | Not in the deck's loop (its question 6) | Nothing by default | **Yours**: a check in the tool, plus approval (Part 3) |
| State | Globals | `deps`, passed in per run | You decide what the tools may touch |
| Correctness | Not checked | Not checked | **Yours** (Parts 4 and 9) |
{: .tb-full}

---

## Part 2: Core Pydantic Versus Pydantic AI

The two names are easy to blur, and they do different jobs.  Core Pydantic validates data.  It has no idea that a model exists:

```python
# step2_schema.py: the schema you wrote by hand in the deck, generated from the signature.
import json
from datetime import date

from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Tool


def days_until(target: date) -> int:
    """Returns the number of days from today until the target date (positive means the future).

    Args:
        target: The target date, for example 2026-12-07.
    """
    return (target - date.today()).days


print(json.dumps(Tool(days_until).tool_def.parameters_json_schema, indent=2))


# Core Pydantic, with no agent anywhere: a model validates data, and that is all it does.
class DaysUntilArgs(BaseModel):
    target: date = Field(description="The target date, for example 2026-12-07.")


print(DaysUntilArgs.model_validate({"target": "2026-12-07"}))
try:
    DaysUntilArgs.model_validate({"target": "next Tuesday"})
except ValidationError as e:
    print("rejected:", e.errors()[0]["msg"])
```

```text
{
  "additionalProperties": false,
  "properties": {
    "target": {
      "description": "The target date, for example 2026-12-07.",
      "format": "date",
      "type": "string"
    }
  },
  "required": ["target"],
  "type": "object"
}
target=datetime.date(2026, 12, 7)
rejected: Input should be a valid date or datetime, invalid character in year
```

The first block is the JSON Schema you wrote by hand in the deck, generated here from the function's signature and the `Args:` line of its docstring.  The second half is plain Pydantic with no agent at all: `DaysUntilArgs` is the P1 cell from the Tool Use deck's Pydantic extension.  Pydantic AI uses this same machinery for every tool argument and every structured output, which is why the P1 to P9 cells in the [Tool Use]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-tooluse.md), [MCP]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-mcp.md), and [RAG]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-rag.md) decks and Part V of [Local Agent From Scratch]({{ site.baseurl }}/Tutorials/LocalAgentFromScratch) are worth knowing before you use the framework.  Everything those cells check, the framework now checks for you.  Anything those cells *could not* check, the framework does not check either.

---

## Part 3: Dependencies, Permissions, and Approval

Validation answers "is this a well-formed date?"  It does not answer "may the agent write to this file?"  Those are different questions, and a framework that answers the first one for you can make it easy to forget the second.

This agent can save a deadline to a notes file.  Its tools receive a `RunContext` carrying **dependencies**: today's date, the one folder it may write to, and the student's courses.  Your program supplies those, not the model, so a test can pin today's date and a real run can point at a real folder.

```python
# step3_deps.py: typed dependencies, a validated tool, a permission check, and a human approval.
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from pydantic_ai import (Agent, ApprovalRequired, DeferredToolRequests, DeferredToolResults,
                         ModelRetry, RunContext, ToolDenied, UsageLimits)

from common import make_model, show_trace


@dataclass
class Deps:
    today: date                           # injected, so tests can pin it
    notes_dir: Path                       # the only folder the agent may write to
    allowed_courses: set[str] = field(default_factory=lambda: {"CS357", "MATH211"})


agent = Agent(
    make_model(),
    deps_type=Deps,
    output_type=[str, DeferredToolRequests],     # a run may end by asking a human
    instructions="You help a student track deadlines. Use the tools; never guess dates.",
    model_settings={"temperature": 0.0, "seed": 42},
)


@agent.tool
def days_until(ctx: RunContext[Deps], target: date) -> int:
    """Returns the number of days from today until the target date.

    Args:
        target: The target date, for example 2026-12-07.
    """
    if target.year > ctx.deps.today.year + 1:
        # Valid as a date, but not plausible here: tell the model why so it can try again.
        raise ModelRetry(f"{target} is more than a year out; check the year.")
    return (target - ctx.deps.today).days


@agent.tool
def save_deadline(ctx: RunContext[Deps], course: str, due: date, title: str) -> str:
    """Saves a deadline to the student's notes file for one course.

    Args:
        course: A course code such as CS357.
        due: The due date.
        title: A short title for the deadline.
    """
    # Validation said these are a string and a date. It did not say this write is allowed.
    if course not in ctx.deps.allowed_courses:
        return f"refused: {course} is not one of this student's courses"
    if not ctx.tool_call_approved:
        raise ApprovalRequired()          # pause the run; a person decides
    path = ctx.deps.notes_dir / f"{course}.md"
    with path.open("a") as f:
        f.write(f"- {due.isoformat()}: {title}\n")
    return f"saved to {path.name}"
```

Three different checks happen in `save_deadline`, in this order:

1. **Validation, done by the framework.**  `course` must be a string and `due` must be a date.  A model that sends `"due": "next week"` gets a retry message and never reaches your code.
2. **Permission, done by you.**  `HIST101` is a valid string.  It is refused because it is not this student's course, and no schema could have known that.
3. **Approval, done by a person.**  Even a permitted write pauses with `ApprovalRequired`.  The run ends early and returns `DeferredToolRequests` listing the calls waiting for a decision; nothing has been written yet.

The script that runs the agent asks the person and resumes the run with their decisions:

```python
# step3_run.py: run the deadline agent, and put a person in front of every write.
from datetime import date
from pathlib import Path

from pydantic_ai import DeferredToolRequests, DeferredToolResults, ToolDenied, UsageLimits

from common import show_trace
from step3_deps import Deps, agent

deps = Deps(today=date.today(), notes_dir=Path("notes"))
deps.notes_dir.mkdir(exist_ok=True)
limits = UsageLimits(request_limit=6, tool_calls_limit=4)

result = agent.run_sync("Save my CS357 RAG lab deadline, 2026-11-12, titled 'RAG lab'.",
                        deps=deps, usage_limits=limits)
for _ in range(2):                                  # bounded: at most two rounds of asking
    if not isinstance(result.output, DeferredToolRequests):
        break
    decisions = DeferredToolResults()
    for call in result.output.approvals:
        answer = input(f"Approve {call.tool_name}({call.args})? [y/N] ").strip().lower()
        decisions.approvals[call.tool_call_id] = (
            True if answer == "y" else ToolDenied("The student declined. Do not try again; say so."))
    result = agent.run_sync(message_history=result.all_messages(), deferred_tool_results=decisions,
                            deps=deps, usage_limits=limits)

print(result.output)
show_trace(result.all_messages())
```

```text
$ python step3_run.py
Approve save_deadline({"course":"CS357","due":"2026-11-12","title":"RAG lab"})? [y/N] y
I have saved your CS357 RAG lab deadline, titled 'RAG lab', for the due date of 2026-11-12.
  [user-prompt] "Save my CS357 RAG lab deadline, 2026-11-12, titled 'RAG lab'."
  [tool-call] save_deadline({"course":"CS357","due":"2026-11-12","title":"RAG lab"})
  [tool-return] save_deadline -> 'saved to CS357.md'
  [text] "I have saved your CS357 RAG lab deadline, titled 'RAG lab', for the due date of 2026-11-12."
$ cat notes/CS357.md
- 2026-11-12: RAG lab
```

Answer `n` instead and the tool returns the denial message to the model, and the file is never created.  `qwen2.5:3b` then repeated the denial message as its answer.  We also saw two things while testing with `llama3.2`.  First, after a plain denial it sometimes asked for the same call again, which is why the loop above asks at most twice and why the denial message tells the model not to retry.  Second, after a successful save, its final sentence was muddled ("User question: Add a deadline...") even though the file was correct.  **The file is the truth, not the model's description of it.**  Check the side effect, not the sentence.

> **Two different budgets:** `request_limit` caps how many times the model is called.  `tool_calls_limit` caps how many tools actually run.  A model that asks for three tools in one reply uses one request and three tool calls, so a loop can stay under one limit and still blow through the other.  Part 5 trips each one on purpose.
{: .tb-tip data-title="Request limits and tool-call limits"}

**What the framework did:** passed `deps` to every tool, validated arguments, turned `ModelRetry` into a message the model can act on, paused for approval, and resumed from saved history.  **What is still yours:** the permission rule, the approval prompt, the decision to bound re-asking, and checking the file.

---

## Part 4: Structured Output, and What Validation Cannot Catch

Sometimes the answer itself should be data rather than prose.  Pydantic AI can require that the final answer validate against a Pydantic model (a typed validation class, not a language model).  Our first attempt asked for `{event, target, days_left}` and let the model call `days_until` along the way.  With `llama3.2` on CPU (this part was tested before the switch to `qwen2.5:3b`), that failed in instructive ways:

- With the default tool-based output, where the model is supposed to hand back its answer by calling a special output tool, the model answered in prose instead of calling that tool, and the run stopped at its request limit.
- With `NativeOutput` (Ollama constrains the reply to the JSON schema), the reply always parsed, but `days_left` was `0`, and the model had not called the tool at all.
- With an output validator that recomputed `days_left` and raised `ModelRetry`, the model never got the arithmetic right, and the run ended with "Exceeded maximum output retries (3)".

The validator was doing its job: it caught a well-formed wrong answer every time.  The fix was a design change, not a better prompt.  **The model extracts; your code computes.**

```python
# step4_output.py: the answer as a validated object. The model extracts; your code computes.
import traceback
from datetime import date

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, NativeOutput, UsageLimits

from common import make_model


class Deadline(BaseModel):
    event: str = Field(description="What the deadline is, in a few words")
    target: date


agent = Agent(
    make_model(),
    output_type=NativeOutput(Deadline),   # Ollama constrains the reply to this JSON schema
    retries=3,
    instructions="Extract the deadline the user names.",
    model_settings={"temperature": 0.0, "seed": 42},
)


@agent.output_validator
def not_in_the_past(output: Deadline) -> Deadline:
    # A rule the schema cannot express: valid dates can still be wrong for this task.
    if output.target < date.today():
        raise ModelRetry(f"{output.target} has already passed; re-read the year in the request.")
    return output


try:
    result = agent.run_sync("Countdown to the last day of classes, 2026-12-07.",
                            usage_limits=UsageLimits(request_limit=4))
    d = result.output
    print(repr(d))
    print(f"{d.event}: {(d.target - date.today()).days} days left")   # arithmetic stays in code
except Exception as e:
    print(f"[step4_output:main] {e}")
    traceback.print_exc()
```

```text
$ python step4_output.py
Deadline(event='last day of classes', target=datetime.date(2026, 12, 7))
last day of classes: 61 days left
```

The schema guarantees that `target` is a date.  The validator adds a rule the schema cannot express (not in the past).  The arithmetic, which a 3B model gets wrong and a dozen lines of Python get right, never touches the model.

**What the framework did:** sent the schema, validated the reply, retried on failure.  **What is still yours:** deciding which parts of the answer a model should produce at all.

---

## Part 5: The Agentic Loop, Node by Node

`run_sync` runs a loop.  `agent.iter` lets you step through that loop one node, or stage, at a time:

```python
# step5_loop.py: walk the agentic loop one node at a time, then trip each kind of limit.
import asyncio
from datetime import date

from pydantic_ai import Agent, UsageLimitExceeded, UsageLimits

from common import make_model

agent = Agent(make_model(), instructions="Use the tools for dates; never guess them.",
              model_settings={"temperature": 0.0, "seed": 42})


@agent.tool_plain
def get_today() -> str:
    """Returns today's date in ISO format (YYYY-MM-DD)."""
    return date.today().isoformat()


@agent.tool_plain
def days_until(target: date) -> int:
    """Returns the number of days from today until the target date."""
    return (target - date.today()).days


QUESTION = "What is today's date, and how many days until 2026-12-07?"


async def walk():
    async with agent.iter(QUESTION, usage_limits=UsageLimits(request_limit=5)) as run:
        async for node in run:
            name = type(node).__name__
            if name == "CallToolsNode":
                calls = [p.tool_name for p in node.model_response.parts if p.part_kind == "tool-call"]
                print(f"{name}: model asked for {calls or 'no tools (final answer)'}")
            else:
                print(name)
    print(run.result.output)
    print(run.usage)




async def trip_limits():
    for limits in (UsageLimits(request_limit=1), UsageLimits(tool_calls_limit=1)):
        try:
            await agent.run(QUESTION, usage_limits=limits)
            print(limits, "-> finished within the limit")
        except UsageLimitExceeded as e:
            print(limits, "->", str(e).split(".")[0])


async def main():
    await walk()
    await trip_limits()


asyncio.run(main())
```

```text
$ python step5_loop.py
UserPromptNode
ModelRequestNode
CallToolsNode: model asked for ['get_today', 'days_until']
ModelRequestNode
CallToolsNode: model asked for no tools (final answer)
End
Today's date is 2026-10-07, and there are 61 days until 2026-12-07.
RunUsage(input_tokens=490, output_tokens=82, requests=2, tool_calls=2)
UsageLimits(request_limit=1) -> The next request would exceed the request_limit of 1
UsageLimits(tool_calls_limit=1) -> The next tool call(s) would exceed the tool_calls_limit of 1 (tool_calls=2)
```

Map the nodes onto your hand-written loop.  `ModelRequestNode` is the `requests.post` to the model.  `CallToolsNode` is the `for c in calls` dispatch.  `End` is the `if not calls: return` line.  The two limits stop the run in different places: the request limit before the second model call, and the tool-call limit when one reply asks for two tools at once.

Now run it with `MODEL=llama3.2`.  The trace is the same: it called `get_today`, received `2026-10-07`, and then wrote "Today's date is October 7, **2023**."  The tool ran, the result was in the context, and the model still did not copy it correctly.  A tool call guarantees that the right number reached the model.  It does not guarantee that the model used it, which is why Part 4 moved arithmetic into code and why Part 9 checks tool results rather than final sentences.

---

## Part 6: Memory

Short-term memory is the message list, handed back with `message_history`.  Long-term memory is the same list saved to disk.  A history processor decides how much of it is sent to the model on each call, so the file can grow without the context window growing with it.

```python
# step6_memory.py: short-term memory is the message list; saving it to disk makes it long-term.
from pathlib import Path

from pydantic_ai import Agent, ModelMessagesTypeAdapter, ModelRequest
from pydantic_ai.capabilities import ProcessHistory

from common import make_model

HISTORY = Path("history.json")


def keep_recent(messages):
    """Send only the last six messages. The file keeps everything; the window does not."""
    recent = messages[-6:]
    while recent and not isinstance(recent[0], ModelRequest):   # never start on a model reply
        recent = recent[1:]
    return recent


agent = Agent(make_model(), instructions="You are a concise study assistant.",
              capabilities=[ProcessHistory(keep_recent)],
              model_settings={"temperature": 0.0, "seed": 42})

history = ModelMessagesTypeAdapter.validate_json(HISTORY.read_bytes()) if HISTORY.exists() else []
print(f"loaded {len(history)} earlier messages")

question = input("you> ") or "My name is Sam and my exam is on Friday. What is my name?"
result = agent.run_sync(question, message_history=history)
print("agent>", result.output)

HISTORY.write_bytes(ModelMessagesTypeAdapter.dump_json(result.all_messages(), indent=2))
print(f"saved {len(result.all_messages())} messages to {HISTORY}")
```

```text
$ rm -f history.json; echo "" | python step6_memory.py
loaded 0 earlier messages
you> agent> Your name is Sam.
saved 2 messages to history.json
$ echo "What is my name, and when is my exam?" | python step6_memory.py
loaded 2 earlier messages
you> agent> Your name is Sam. Your exam is on Friday. Please let me know if you need any help preparing for your exam.
saved 4 messages to history.json
```

The second process started cold, read `history.json`, and answered from it.  Open the file: it is ordinary JSON, every part labeled the way `show_trace` prints it.  `keep_recent` is a memory **policy**, and it is yours to choose.  The [Memory and Context]({{ site.baseurl }}/Tutorials/MemoryAndContext) tutorial compares other policies (summaries, retrieval of old turns) that would replace those few lines.

> **Watch the cut:** A trimmed history must still begin with a request, and a tool call must never be separated from its result.  `keep_recent` drops leading model replies for the first reason.  If you trim in the middle of a tool exchange, the provider rejects the request.
{: .tb-warning data-title="Trimming history"}

---

## Part 7: Skills

A skill is a prompt the agent loads only when it needs it.  The agent sees a one-line menu on every call, and a tool returns a skill's full text on demand.  The files are the `SKILL.md` format from the [Agent Skills]({{ site.baseurl }}/Tutorials/AgentSkills) tutorial:

```markdown
---
name: exam-planner
description: Turn an exam date and a topic list into a day-by-day study plan.
---
Call days_until with the exam date first. Give each topic at least one day, put the
hardest topic first, and leave the last day for a full practice exam. Answer as a
numbered list with one line per day.
```

```python
# step7_skills.py: a skill menu in the instructions, and a tool that loads one skill on demand.
from datetime import date, timedelta
from pathlib import Path

from pydantic import BaseModel
from pydantic_ai import Agent, ModelRetry, UsageLimits

from common import make_model, show_trace


class SkillCard(BaseModel):
    name: str
    description: str


def read_skill(path: Path) -> tuple[SkillCard, str]:
    _, front, body = path.read_text().split("---", 2)
    fields = dict(line.split(":", 1) for line in front.strip().splitlines())
    return SkillCard(**{k.strip(): v.strip() for k, v in fields.items()}), body.strip()


SKILLS = {p.parent.name: read_skill(p) for p in sorted(Path("skills").glob("*/SKILL.md"))}

agent = Agent(make_model(), model_settings={"temperature": 0.0, "seed": 42})


@agent.instructions
def skill_menu() -> str:
    menu = "\n".join(f"- {card.name}: {card.description}" for card, _ in SKILLS.values())
    return ("You are a concise study assistant. When a skill fits the task, call load_skill "
            "first and follow it.\nSkills:\n" + menu)


@agent.tool_plain
def load_skill(name: str) -> str:
    """Loads the full instructions for one skill by name."""
    if name not in SKILLS:       # the registry, not the path, decides what can be read
        raise ModelRetry(f"No skill named {name!r}. Choose one of: {', '.join(SKILLS)}")
    return SKILLS[name][1]


@agent.tool_plain
def days_until(target: date) -> int:
    """Returns the number of days from today until the target date."""
    return (target - date.today()).days


exam = (date.today() + timedelta(days=5)).isoformat()   # always five days out, whenever you run it
result = agent.run_sync(f"My calculus exam is on {exam} and covers series, integrals, and limits. Plan my studying.",
                        usage_limits=UsageLimits(request_limit=6, tool_calls_limit=4))
print(result.output)
show_trace(result.all_messages())
```

`SkillCard` is core Pydantic again, checking the front matter.  `load_skill` refuses any name that is not in `SKILLS` and lists the valid ones; the registry, not the model's string, decides what can be read.  That is the same lesson as the deck's `REGISTRY[name]`, and the same lesson as a path-traversal check.

This step separated the two local models more clearly than any other, and it is the main reason this tutorial defaults to `qwen2.5:3b`.  These runs were made on October 7, so the exam date reads 2026-10-12; yours will be five days from the day you run it:

```text
$ MODEL=qwen2.5:3b python step7_skills.py
  ...
  [tool-call] load_skill({"name":"exam-planner"})
  [tool-return] load_skill -> 'Call days_until with the exam date first. ...'
  [tool-call] days_until({"target":"2026-10-12"})
  [tool-return] days_until -> '5'
  [tool-call] days_until({"topic_list":[...],"exam_date":"2026-10-12","days_until":5})
  [retry-prompt] days_until -> "[{'type': 'missing', 'loc': ('target',), 'msg': 'Field required', ...
  [text] "It seems there was a misunderstanding ... "

$ MODEL=llama3.2 python step7_skills.py
{"name":"exam-planner","parameters":{"target":"2026-10-12","topics":["series","integrals","limits"]}}
```

`qwen2.5:3b` loaded the skill and followed its first instruction.  Its second `days_until` call was malformed, so Pydantic AI sent back a validation retry, and the model then wrote out the study plan.  `llama3.2` wrote a tool call *as text* in its final answer, so no tool ever ran.  Pydantic AI cannot repair that: it only sees a reply with no tool call in it.  If your agent depends on tool calls, choose a model that makes them, and check the trace.

---

## Part 8: MCP, the Real Protocol

The MCP deck's Flask server teaches the shape of MCP (`/tools/list`, `/tools/call`), but it is not an MCP server: it speaks plain HTTP and JSON, not the JSON-RPC protocol (a standard way to encode function calls and their results as JSON messages) that MCP clients expect.  This part runs a real one.  The two date tools move out of your program and into a server process:

```python
# calendar_server.py: the same two tools, served over real MCP (JSON-RPC over stdio).
from datetime import date

from fastmcp import FastMCP

mcp = FastMCP("calendar")


@mcp.tool
def get_today() -> str:
    """Returns today's date in ISO format (YYYY-MM-DD)."""
    return date.today().isoformat()


@mcp.tool
def days_until(target: date) -> int:
    """Returns the number of days from today until the target date (positive means the future)."""
    return (target - date.today()).days


if __name__ == "__main__":
    mcp.run(show_banner=False)          # stdio by default: the client starts this process
```

The client starts the server as a separate process and talks to it over stdio (standard input and output), asks what it offers, and calls a tool, first by hand and then through an agent:

```python
# step8_mcp.py: discover the server's tools over MCP, then hand them to an agent.
import asyncio
from pathlib import Path

from fastmcp import Client
from pydantic_ai import Agent, UsageLimits
from pydantic_ai.mcp import MCPToolset

from common import make_model, show_trace


async def inspect_server():
    async with Client(Path("calendar_server.py")) as client:          # starts the server over stdio
        for tool in await client.list_tools():
            print(f"tools/list -> {tool.name}: {tool.input_schema}")
        result = await client.call_tool("days_until", {"target": "2026-12-07"})
        print("tools/call ->", result.data)
        try:
            await client.call_tool("days_until", {"target": "next Tuesday"})
        except Exception as e:
            print("tools/call with a bad date ->", type(e).__name__, str(e).splitlines()[0])


asyncio.run(inspect_server())

agent = Agent(make_model(), toolsets=[MCPToolset(Path("calendar_server.py"))],
              instructions="Use the tools for dates; never guess them.",
              model_settings={"temperature": 0.0, "seed": 42})
result = agent.run_sync("How many days until 2026-12-07?", usage_limits=UsageLimits(request_limit=4))
print(result.output)
show_trace(result.all_messages())
```

```text
$ python step8_mcp.py
tools/list -> get_today: {'type': 'object', 'additionalProperties': False, 'properties': {}}
tools/list -> days_until: {'type': 'object', 'additionalProperties': False, 'properties': {'target': {'format': 'date', 'type': 'string'}}, 'required': ['target']}
tools/call -> 61
tools/call with a bad date -> ToolError 1 validation error for call[days_until]
There are 61 days until December 7, 2026.
  [user-prompt] 'How many days until 2026-12-07?'
  [tool-call] days_until({"target":"2026-12-07"})
  [tool-return] days_until -> '61'
  [text] 'There are 61 days until December 7, 2026.'
```

The server validated the bad date itself, on its side of the connection, before your function ran.  The agent's trace is identical to Part 1's: the model sees a description going in and a result coming back, whether the function lives in your file or in another process.  What changed is who runs the code, and therefore where permission checks have to live.  A server you connect to decides for itself what its tools may do, so an approval gate in your agent cannot reach inside it.  Connect only servers you trust, and give them only the access their tools need; the [What a Container Isolates]({{ site.baseurl }}/Tutorials/ContainerIsolation) tutorial is about exactly that.

> **Older examples:** FastMCP 4 warns when you pass a bare filename string (`MCPToolset("calendar_server.py")`); pass `Path("calendar_server.py")` as above.  `Tool.inputSchema` is now `Tool.input_schema`.
{: .tb-warning data-title="FastMCP 4"}

---

## Part 9: Testing Without a Model

Every result above depended on a model that answers differently on different machines.  The plumbing does not have to.  Pydantic AI can swap the model for `TestModel` (which calls each tool with schema-valid arguments) or `FunctionModel` (which plays back the calls you script), so the checks that matter most run in a second, with no Ollama at all:

```python
# test_agents.py: test the plumbing with no model at all. Run with: python -m pytest -q test_agents.py
from datetime import date
from pathlib import Path

import pytest
from pydantic_ai import DeferredToolRequests, ModelResponse, TextPart, ToolCallPart, UsageLimitExceeded, UsageLimits
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel

from step3_deps import Deps, agent as deadline_agent


def deps(tmp_path: Path) -> Deps:
    return Deps(today=date(2026, 10, 7), notes_dir=tmp_path)


def test_every_tool_gets_called_with_schema_valid_arguments(tmp_path):
    # TestModel calls each tool once with arguments generated from its schema.
    with deadline_agent.override(model=TestModel(call_tools=["days_until"])):
        result = deadline_agent.run_sync("anything", deps=deps(tmp_path))
    returns = [p for m in result.all_messages() for p in m.parts if p.part_kind == "tool-return"]
    assert returns and returns[0].tool_name == "days_until"


def scripted(*turns):
    """A fake model that plays back the given tool calls, then a final answer."""
    turns = list(turns)

    def respond(messages, info: AgentInfo) -> ModelResponse:
        if turns:
            name, args = turns.pop(0)
            return ModelResponse(parts=[ToolCallPart(name, args)])
        return ModelResponse(parts=[TextPart("done")])
    return FunctionModel(respond)


def test_days_until_uses_the_injected_today(tmp_path):
    with deadline_agent.override(model=scripted(("days_until", {"target": "2026-12-07"}))):
        result = deadline_agent.run_sync("q", deps=deps(tmp_path))
    ret = [p for m in result.all_messages() for p in m.parts if p.part_kind == "tool-return"][0]
    assert ret.content == 61


def test_a_bad_date_goes_back_to_the_model_as_a_retry(tmp_path):
    with deadline_agent.override(model=scripted(("days_until", {"target": "next Tuesday"}))):
        result = deadline_agent.run_sync("q", deps=deps(tmp_path))
    kinds = [p.part_kind for m in result.all_messages() for p in m.parts]
    assert "retry-prompt" in kinds and "tool-return" not in kinds


def test_valid_arguments_are_not_permission(tmp_path):
    call = ("save_deadline", {"course": "HIST101", "due": "2026-11-17", "title": "essay"})
    with deadline_agent.override(model=scripted(call)):
        result = deadline_agent.run_sync("q", deps=deps(tmp_path))
    ret = [p for m in result.all_messages() for p in m.parts if p.part_kind == "tool-return"][0]
    assert ret.content.startswith("refused") and not list(tmp_path.iterdir())


def test_a_write_pauses_for_approval(tmp_path):
    call = ("save_deadline", {"course": "CS357", "due": "2026-11-12", "title": "RAG lab"})
    with deadline_agent.override(model=scripted(call)):
        result = deadline_agent.run_sync("q", deps=deps(tmp_path))
    assert isinstance(result.output, DeferredToolRequests) and not list(tmp_path.iterdir())


def test_request_limit_and_tool_call_limit_are_different(tmp_path):
    many = [("days_until", {"target": "2026-12-07"})] * 3
    with deadline_agent.override(model=scripted(*many)):
        with pytest.raises(UsageLimitExceeded, match="request_limit"):
            deadline_agent.run_sync("q", deps=deps(tmp_path), usage_limits=UsageLimits(request_limit=2))
    with deadline_agent.override(model=scripted(*many)):
        with pytest.raises(UsageLimitExceeded, match="tool_calls_limit"):
            deadline_agent.run_sync("q", deps=deps(tmp_path), usage_limits=UsageLimits(tool_calls_limit=2))
```

```text
$ python -m pytest -q test_agents.py
......                                                                   [100%]
6 passed in 3.30s
```

These are the tests to keep green as you change the agent: a bad date becomes a retry, valid arguments for the wrong course are refused, a permitted write still pauses for a person, and the two limits trip where they should.  They say nothing about whether a real model answers well; the runs in Parts 1 through 8 do that, and they are a different kind of evidence.

---

## Part 10: Putting It Together

You now have every piece of a small, honest agent: typed tools with dependencies (Part 3), a permission check and a human gate on the one tool that writes (Part 3), extraction instead of model arithmetic (Part 4), limits on both requests and tool calls (Part 5), a history file with a trimming policy (Part 6), a skill menu (Part 7), and an MCP server for the tools that live elsewhere (Part 8), all covered by tests that need no model (Part 9).  To combine them, pass more than one thing to the same `Agent`:

```python
agent = Agent(
    make_model(),
    deps_type=Deps,
    output_type=[str, DeferredToolRequests],
    toolsets=[MCPToolset(Path("calendar_server.py"))],     # get_today, days_until
    capabilities=[ProcessHistory(keep_recent)],
    model_settings={"temperature": 0.0, "seed": 42},
)
# then register save_deadline (Part 3), skill_menu and load_skill (Part 7) on this agent,
# and call it with deps=..., message_history=..., and usage_limits=UsageLimits(...)
```

Building that file is Exercise 1.

---

## Exercises

1.  *Assemble the agent.*
   - *What to do*: Combine Parts 3, 6, 7, and 8 into `study_agent.py`, with the date tools served over MCP and `save_deadline` local.
   - *Starter hint*: Start from the block in Part 10.  Keep `step3_run.py`'s approval loop around the run.
   - *You've succeeded when*: one session can plan an exam with the skill, save the exam date only after you approve it, and remember your name after a restart.

2.  *Find the line.*
   - *What to do*: For each row of Part 1's responsibility table, point to the line of `step1_paired.py` (or the library) that now does it.
   - *Starter hint*: Some rows have no line, because the framework does not do them at all.
   - *You've succeeded when*: you can name every row that is still yours.

3.  *Break the description.*
   - *What to do*: Change `days_until`'s docstring to "Computes something about dates." and rerun Part 1 with both models.
   - *Starter hint*: Compare the traces, not the final sentences.
   - *You've succeeded when*: you can say what the model lost, in terms of the schema it was sent.

4.  *Test the gap.*
   - *What to do*: Add a `FunctionModel` test in which the model calls `get_today` and then answers with a different date.
   - *Starter hint*: The test should pass, and that is the point.
   - *You've succeeded when*: you can explain which property your other tests guarantee and which one no plumbing test can.

---

## Reflection

*Personal*: Which row of the responsibility table had you been assuming the framework handled?

*Technical*: Part 4 moved arithmetic out of the model and Part 3 moved permission out of the prompt.  Name one more decision in your own lab agent that should move from the model into code, and say how you would test it.

*Societal*: An approval gate makes a person responsible for each write.  When an agent asks for approval forty times a day, what happens to the quality of that person's attention, and who is accountable when they click yes by habit?

---

## Where This Goes Next

[Agent Frameworks, Part V]({{ site.baseurl }}/Tutorials/AgentFrameworks#part-v-hands-on-pydantic-ai-and-the-context-window) uses the same framework to print the context window after each feature is added, which makes the cost of every tool description and memory line visible.  Part 8's MCP client is a natural next step after the [Tools and MCP lab]({{ site.baseurl }}/Assignments/ToolsMCP), which connects a client to an existing MCP server.  The [Offline RAG and LoRA tutorial]({{ site.baseurl }}/Tutorials/OfflineRAGFineTuning) reuses `common.py` to put a retrieval tool behind the same kind of agent.

## Further Reading

- Pydantic AI documentation: [agents](https://ai.pydantic.dev/agent/), [tools](https://ai.pydantic.dev/tools/), [deferred tools and approval](https://ai.pydantic.dev/deferred-tools/), [message history](https://ai.pydantic.dev/message-history/), [MCP client](https://ai.pydantic.dev/mcp/client/), and [testing](https://ai.pydantic.dev/testing/)
- [FastMCP on PyPI](https://pypi.org/project/fastmcp/), which links its documentation
- [Model Context Protocol specification](https://modelcontextprotocol.io)
- [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility)
