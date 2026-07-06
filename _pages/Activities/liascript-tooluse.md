# Tool Use and Function Calling
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-tooluse.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-tooluse.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tool Use and Function Calling

Our week 1 agent parsed `calc(...)` out of free text with a regular expression, and it worked until it did not. Today we upgrade to **structured function calling** (also called tool use): the model emits a machine-readable request to invoke a function, and the runtime executes it. We move from **why structure beats parsing $\rightarrow$ tool schemas $\rightarrow$ native function calling with Ollama $\rightarrow$ safety boundaries for tools that change the world**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Tool (Function)** | A typed, named function that an agent can request the runtime to execute on its behalf. The model never runs code itself — it asks your program to run the function and report back the result. | `get_today()` returns today's date; `days_until("2026-12-07")` returns the number of days |
| **Tool Schema** | A structured description of a tool: its name, a natural-language description (the only thing the model knows about what the tool does), and a list of typed parameters. Written in JSON Schema format. | `{"name": "days_until", "description": "Returns days from today to the given ISO date", "parameters": {"target_iso": {"type": "string"}}}` |
| **`tool_calls` Field** | The structured field the model returns (instead of prose) when it decides to use a tool. Contains the tool name and the argument values, parsed as a JSON object — not free text. | `{"function": {"name": "days_until", "arguments": {"target_iso": "2026-12-07"}}}` |
| **Tool Registry** | A dictionary in your code that maps tool names to actual Python functions, used to look up and execute the function the model requested. Acts as a security boundary. | `REGISTRY = {"get_today": get_today, "days_until": days_until}` |
| **Perceive-Plan-Act Loop** | The cycle an agent runs: receive input (perceive), decide what to do including which tool to call (plan), execute the tool and observe the result (act), then loop. Tool calling formalizes the "act" step. | The `agent()` function loops up to `max_steps=4` times through this cycle |
| **Read-Only vs. Irreversible-Write** | A classification of tools by the consequences of their actions. Read-only tools (look up a date, search the web) are safe to call without confirmation. Irreversible-write tools (send an email, delete a file, post to social media) require human approval before execution. | `get_today()` is read-only; a hypothetical `send_email()` is irreversible-write |
| **Context window** | The fixed-size token buffer that holds *everything* the model can see on a given turn: system prompt, conversation history, **every tool schema**, and every tool result. Nothing outside it exists to the model. | A model with a 128K-token window; see `liascript-memorycontext.md` |
| **Tool-definition token cost** | Each tool's schema (name + description + parameter spec) occupies tokens in the prompt on *every* turn it is offered — not just when the tool is called. Ten tools are ten schemas riding along in the context the whole conversation. | A 5-parameter tool schema might cost ~120 tokens every turn |
| **Tool round-trip** | A single tool use adds tokens to the context *twice*: once for the model's `tool_calls` request, and again for the `tool`-role result your code appends. Both stay in the history for the rest of the conversation. | A search tool returning 200 tokens of results leaves 200 tokens in context permanently |

---

# Part I: From Parsing to Protocol

## 1. The Contract

In this Part you will see why the regex-based tool-calling approach from week 1 breaks on real user input, then learn how structured function calling — where the model emits a machine-readable JSON request instead of prose — solves the problem and moves authority over execution into your code.

**Why this matters:** In week 1 our agent extracted tool calls using string patterns like `calc(3+4)`. This works for controlled demos and breaks immediately in the real world: users write "calculate 3 plus 4" or "what is 3+4?", and the regex matches nothing. Worse, a model trying to call a tool by free text might write "I will now call the calculator with the arguments 3 and 4" — grammatically valid, semantically clear to a human, but unexecutable by a regex. Structured function calling solves this by giving the model a formal protocol: instead of embedding a tool call in prose, the model returns a machine-readable JSON object that your code can execute reliably. It is the difference between a human telling a colleague "please send the email" and a computer sending a precisely formatted API request.

**A tool is a typed function the model may request.** We describe each tool with a schema: name, natural-language description, and parameters with types. The description is not documentation for humans; it is *the only thing the model knows about what the tool does*, so writing it clearly is prompt engineering. Modern chat APIs (including Ollama's) accept a `tools` list and return, when the model chooses, a structured `tool_calls` field instead of prose:

```
request:  messages + tools=[{name, description, parameters}]
response: message.tool_calls = [{function: {name: "get_weather", arguments: {"city": "Collegeville"}}}]
```

The runtime executes the function, appends the result as a `tool` role message, and calls the model again — which is precisely our perceive-plan-act loop with the parsing risk engineered away. The model never executes anything; it only *asks*. Authority lives in our code, which is where governance will attach.

---

## Model 1: Schema as Interface

Two teams expose the same function with different schemas:

| | Team A | Team B |
|-|--------|--------|
| **Tool name** | `lookup` | `course_lookup` |
| **Description** | "looks stuff up" | "Given an Ursinus course code like CS357, returns the course title, meeting times, and prerequisites from the live catalog." |
| **Parameter name** | `s` | `course_code` |
| **Parameter description** | (none) | "An Ursinus course code in the format DEPT followed by a 3-digit number, e.g., CS357 or MATH375." |
| **Example / In Our Course** | Model sees only: name="lookup", description="looks stuff up" | Model sees: name="course_lookup", description tells it what format to pass and what it will receive back |

### Critical Thinking Questions

1. For the user question "When does the AI class meet?", which schema gives the model enough signal to (a) choose the tool and (b) construct correct arguments? Identify the failure mode Team A invites.

   > *Hint: The model must decide: should I use `lookup`? What do I pass to it? Team A's description gives no signal about what this tool does or what it expects. The model might guess, pass the wrong thing, or not call the tool at all. For Team B: the description says "course code like CS357" — does the user's question contain a course code?*

2. The model passes `course_code="the AI class"`. Whose bug is this — the model's or the schema's — and what one schema change reduces it?

   > *Hint: The model is trying to be helpful by passing what the user said. But the schema's parameter description should have told the model what *format* is expected. Adding an example ("e.g., CS357 or BIO110") and a constraint ("must be a valid department abbreviation followed by a 3-digit number") gives the model the signal it needs to recognize that "the AI class" is not a valid argument.*

3. List the three places natural language appears in this protocol, and rank them by how much care they deserve. (The Recorder writes a priority order with justification.)

   > *Hint: Natural language appears in (a) the tool's description field, (b) the parameter description fields, and (c) the user's message. Rank them: which one is written by you and read by the model at every call, making it the most consequential to get right? Which one is written by a user and may be ambiguous?*

---

# Part II: Native Function Calling

## 2. A Two-Tool Agent

In this Part you will run a working two-tool agent that knows today's date and can calculate deadlines. Watch the `[tool]` print lines as it runs — each one shows a moment where your Python program, not the model, executed a function and handed the result back to the model for the next step.

The code below defines two tools (`get_today` and `days_until`), describes them in JSON Schema format so the model knows what each tool does and what arguments it expects, and runs a perceive-plan-act loop (the repeating cycle where an agent receives input, decides what to do, executes a tool or answers, then loops) that automatically calls whichever tool the model requests.

---

## Code Cell

```python
import json
import requests
from datetime import date

def get_today():
    return str(date.today())

def days_until(target_iso):
    try:
        d = date.fromisoformat(target_iso)
        return str((d - date.today()).days)
    except Exception as e:
        print(f"[tooluse:days_until] {e}")
        import traceback; traceback.print_exc()
        return "error: bad date"

TOOLS = [
  {"type": "function", "function": {
     "name": "get_today",
     "description": "Returns today's date in ISO format (YYYY-MM-DD). Call this whenever you need to know the current date before computing a duration or deadline.",
     "parameters": {"type": "object", "properties": {}, "required": []}}},
  {"type": "function", "function": {
     "name": "days_until",
     "description": "Returns the number of days from today until the given ISO date. The result is positive if the date is in the future and negative if it has passed.",
     "parameters": {"type": "object",
                    "properties": {"target_iso": {"type": "string",
                                                  "description": "The target date in YYYY-MM-DD format, e.g., 2026-12-07"}},
                    "required": ["target_iso"]}}},
]
REGISTRY = {"get_today": get_today, "days_until": days_until}

def agent(question, max_steps=4):
    msgs = [{"role": "user", "content": question}]
    for _ in range(max_steps):
        try:
            r = requests.post("http://localhost:11434/api/chat", json={
                "model": "llama3.2", "stream": False, "tools": TOOLS,
                "options": {"temperature": 0.0, "seed": 42},
                "messages": msgs}, timeout=120).json()["message"]
        except Exception as e:
            print(f"[tooluse:agent] {e}")
            import traceback; traceback.print_exc()
            return ""
        msgs.append(r)
        calls = r.get("tool_calls") or []
        if not calls:
            return r["content"]
        for c in calls:
            name = c["function"]["name"]
            args = c["function"]["arguments"] or {}
            result = REGISTRY[name](**args) if name in REGISTRY else "unknown tool"
            print(f"[tool] {name}({args}) -> {result}")
            msgs.append({"role": "tool", "content": result})
    return "step budget exceeded"

print(agent("How many days until the last day of classes, December 7, 2026?"))
```

---

## Model 2: Trace the Protocol

**Why this matters:** The message sequence in tool calling is the core of how structured AI agents work. If you can trace exactly what each message contains and who authored it — human, model, or your Python code — you understand the full control flow and know where to add governance at every step. This trace is also your debugging tool when agents misbehave: find which message in the sequence contains the wrong information, and you know which component to fix.

### Critical Thinking Questions

4. List the exact sequence of messages exchanged for the question above (roles and brief content descriptions). Which message was authored by our Python code rather than by a human or the model?

   > *Hint: The sequence is: (1) user message with the question, (2) model response with a tool_call request, (3) ??? authored by Python code, (4) model response with the final answer. What does message 3 contain? Look at the line `msgs.append({"role": "tool", "content": result})` — who wrote that line of the conversation?*

5. The registry lookup `REGISTRY[name]` is a security boundary. What does it prevent that a Python `eval` of the model's text output would not?

   > *Hint: If the model could request execution of arbitrary Python code strings (like `eval("import os; os.system('rm -rf /')")`), what would happen? The registry only allows functions that you explicitly added to it. What is the maximum damage a malicious or confused model can do through the registry?*

6. Add (on paper) a `send_email(to, body)` tool. Which single line of today's code would you wrap with a human-confirmation gate, and why there rather than in the prompt?

   > *Hint: Find the line `result = REGISTRY[name](**args)`. What happens immediately before this line? What happens immediately after? Where in this sequence would a confirmation dialog ("Are you sure you want to send this email to X?") fit? Why is it more reliable to enforce this in code rather than by adding "always ask for confirmation before sending email" to the prompt?*

> **⚠️ Common Misconception:** Many beginners assume the language model "executes" the tool itself — that the model somehow runs Python code or queries a database during its forward pass. This is not how it works. The model only *describes* which function it wants called and with what arguments, in structured JSON. Your Python program reads that description, looks up the function in the registry, calls it, and sends the result back to the model. The model never has direct access to your file system, your network, or any external resource — all of that access is mediated by your code. This is where governance lives.

[[MC]]
In native function calling, the component that actually executes the function is:
- ( ) The language model, inside its forward pass
- ( ) The Ollama server, automatically
- (x) Your program, after reading the model's structured request
- ( ) The vector database

---

# Part III: What a Tool Call Costs in the Context Window

Part II traced the *messages* in a tool call — who authors each one and in what order. This Part traces the *tokens*. Everything the model can see on a turn — the system prompt, the whole conversation history, **every tool schema you offer**, and every tool result — shares one fixed-size buffer, the context window (`liascript-memorycontext.md`). Tools are not free riders in that buffer. Understanding their token cost is what separates an agent that stays fast and accurate from one that slows down, gets more expensive, and starts picking the wrong tool.

## Model 3: The Token Ledger of a Tool Call

Return to the message sequence from Model 2 and attach an approximate token cost to each piece. (Exact counts depend on the tokenizer; these are illustrative, but the *structure* is exact.) Suppose the agent is offered two tools and answers "How many days until the final exam?"

| # | What enters the context | Author | Approx. tokens | Stays in context after? |
|---|---|---|---|---|
| 0 | System prompt | You (setup) | ~150 | Yes — every turn |
| 0 | **Schema for `get_today`** | You (setup) | ~60 | **Yes — every turn, called or not** |
| 0 | **Schema for `days_until`** | You (setup) | ~90 | **Yes — every turn, called or not** |
| 1 | User question | Human | ~12 | Yes |
| 2 | Model's `tool_calls` request | Model | ~25 | Yes |
| 3 | `tool`-role result your code appends | **Your code** | ~15 | Yes |
| 4 | Model's next `tool_calls` (chained) | Model | ~30 | Yes |
| 5 | Second `tool`-role result | Your code | ~10 | Yes |
| 6 | Final natural-language answer | Model | ~20 | Yes |

Two facts fall out of this ledger. First, the **two tool schemas cost ~150 tokens on every single turn**, whether or not either tool is used — they are standing furniture in the prompt, exactly like the system prompt. Offer twenty tools and you are carrying twenty schemas in every request for the whole conversation. Second, each tool use is a **round-trip**: the request (row 2) *and* the result (row 3) both land in the history and stay there. A tool that returns 200 tokens of search results does not cost 200 tokens once — it costs 200 tokens for the rest of the conversation, re-sent on every subsequent turn. This is the same token-occupancy accounting as the "Bloated Agent" ledger in `liascript-memorycontext.md`, now applied to tools.

### Critical Thinking Questions

1. An agent is offered 15 tools, each with a schema costing about 80 tokens, but a typical conversation only ever uses 2 of them. How many tokens per turn are spent on tool schemas, and how many of those are for tools that are never called in this conversation?

   > *Hint: Every offered schema rides along every turn regardless of use. $15 \times 80$ is the standing cost; only 2 tools are used, so how many schemas' worth is pure overhead here?*

2. A research tool returns 500 tokens of retrieved text. The agent then has a 10-turn conversation. Roughly how many token-turns does that one result consume, and why is that different from the cost of the *request* that triggered it?

   > *Hint: A result appended to history is re-sent on every later turn. Multiply the result size by the remaining turns. The request is small; the result is the heavy part that lingers.*

3. Connect this to cost and latency from `liascript-costoptimization.md` and `liascript-llmserving.md`: if tool schemas and results inflate the input token count on every turn, which two user-facing quantities get worse, and why?

   > *Hint: More input tokens means more to bill for and more to prefill. What happens to per-turn cost, and to time-to-first-token, as the prompt grows?*

[[MC]]
You offer an agent 12 tools but a given conversation only calls 1 of them. What is the token cost of the other 11 tool schemas?
- ( ) Zero — schemas only cost tokens when their tool is actually called
- ( ) They cost tokens once, on the first turn only
- (x) They cost tokens on every turn of the conversation, because all offered schemas sit in the prompt whether or not they are called
- ( ) They are stored on the server and never count against the context window

## Model 4: Fewer Tools, Cleaner Context — and Subagents

Two practices follow directly from the ledger.

**Limit the tools you offer.** Beyond the raw token cost, a long tool list *degrades tool selection*. The model must choose the right tool from everything offered; the more near-duplicate or irrelevant options crowd the list, the more often it picks wrong or fills arguments poorly — the same lesson as the schema-quality ablation in the Exercises, now at the level of tool *count*. Offer the smallest set of well-described tools each task actually needs, not everything you have ever built.

**Use subagents to keep each context focused.** When a task genuinely needs many tools or produces large intermediate results, the fix is not one agent holding all of it. It is to hand a narrow sub-task to a **subagent** running in its *own* context window, with only the few tools and the brief it needs, and return just the answer to the main thread — so the main context never accumulates the sub-task's schemas and scratch work. This course teaches that pattern in depth elsewhere: the small-context-window principle (`liascript-memorycontext.md`), subagents with isolated context and filesystem offload (`liascript-agentframeworks.md`), and orchestration where each stage "sees only what it needs" (`liascript-orchestration.md`). The token ledger above is *why* those patterns work.

### Critical Thinking Questions

1. You have built 30 tools across a semester. A new task needs 3 of them. Give two distinct reasons — one about tokens, one about accuracy — why you should offer only those 3 rather than all 30.

   > *Hint: One reason is the standing schema cost from Model 3. The other is what a crowded menu does to the model's chance of selecting and arguing the right tool.*

2. A subagent runs a 12-tool research sub-task and returns a 3-sentence summary to the main agent. What does the main agent's context *avoid* carrying compared to doing the research inline itself?

   > *Hint: Think about what stays in history when you do the work inline — the schemas, every tool request, every raw result. What comes back from the subagent instead?*

[[MC]]
Why does offering an agent *fewer, well-chosen* tools tend to improve tool-selection accuracy?
- ( ) Fewer tools make each schema description longer automatically
- (x) A shorter, less redundant menu gives the model fewer wrong or near-duplicate options to confuse, so it more reliably picks and fills the right one
- ( ) The model can only read the first tool in any list
- ( ) Fewer tools disable the context window limit

> **⚠️ Common Misconception:** It feels safe — even helpful — to give an agent *every* tool it might conceivably need, on the theory that more capability is strictly better. It is not free. Every tool you attach is a schema that occupies context on every turn (raising cost and latency) *and* one more option the model can mis-select. Capability and context-hygiene trade off against each other. The professional move is to offer the minimal tool set for the task at hand and to push overflow work into subagents with their own contexts — not to hand one agent a giant toolbox and a bloated prompt.

---

# Part IV: Synthesis and Practice

## 3. Exercises

1. *Third tool.* Implement `course_lookup(course_code)` backed by a small dictionary of five courses. Demonstrate a question that requires chaining it with `days_until`.

   - *What to do:* Add a Python dictionary like `COURSES = {"CS357": {"title": "Foundations of AI", "meets": "MWF 10am", "prereqs": "CS174"}, ...}`. Write the function `course_lookup(course_code)` that returns the entry as a string, add it to TOOLS and REGISTRY, and ask a question like "How many days until the final exam for the AI course?" that requires the agent to first look up when CS357's final is, then compute days remaining.
   - *Starter hint:* `def course_lookup(course_code): return str(COURSES.get(course_code, "Course not found"))`. The key to chaining is that the agent must call `course_lookup` first to get the final exam date, then call `days_until` with that date. Observe whether the model chains the calls automatically.
   - *You've succeeded when:* The agent calls both tools in sequence without you explicitly telling it to, and produces a correct final answer with the tool call trace visible in the `[tool]` print output.

2. *Schema ablation.* Replace both tool descriptions with the single word "tool" and rerun your test questions. Report the tool-selection accuracy before and after; connect the result to Model 1.

   - *What to do:* Change both description fields in TOOLS to `"tool"`. Re-run three questions: one that should use `get_today`, one that should use `days_until`, and one that should use both. Compare how often the correct tool is selected and with correct arguments, versus with full descriptions.
   - *Starter hint:* Tool selection accuracy = (correct tool choices) / (total tool decision points). A "correct tool choice" means the model chose the right tool AND passed valid arguments. Count each step's tool call as one decision point.
   - *You've succeeded when:* You have accuracy numbers for both conditions (full descriptions vs. "tool"), and you can connect the drop in accuracy to the specific insight from Model 1 about what the description field communicates to the model.

3. *Read-write taxonomy.* Classify ten plausible tools as read-only, reversible-write, or irreversible-write. Propose a default policy for each class. Keep this taxonomy: it becomes part of your project governance document.

   - *What to do:* Choose 10 tools from this list (or substitute your own): web search, calendar read, calendar write, file read, file delete, grade lookup, post to social media, send email, order pizza, book a flight reservation. Classify each by the worst-case consequence of an unintended call.
   - *Starter hint:* Read-only: no state changes; safe to call without confirmation. Reversible-write: changes state but can be undone (calendar event can be deleted, file can be restored from backup). Irreversible-write: cannot be easily undone (sent email, deleted account, posted public message). Your policy for each class should specify: who must confirm before execution, and what log must be kept.
   - *You've succeeded when:* You have a table of 10 tools with their class and your proposed policy, and you can articulate why the irreversible-write class requires the strongest governance even when the agent's instructions are correct.

4. *Refusal behavior.* Ask the agent a question no tool can answer. Does it improvise a tool call, hallucinate an answer, or say it cannot help? Report and explain which behavior you want and how to prompt for it.

   - *What to do:* Ask a question entirely outside the tools' scope, such as "What is the capital of France?" or "Write me a poem." Observe which of three behaviors occurs: (a) the model invents a tool call to a non-existent function, (b) the model answers from parametric memory without any tool call, or (c) the model says it cannot help with this. Run at least 3 different out-of-scope questions.
   - *Starter hint:* Add to the user message: "You have access to tools. Use them when applicable. If no tool can answer the question, say 'I cannot help with that using my available tools.'" Does that system instruction reliably produce behavior (c)?
   - *You've succeeded when:* You can report which behavior you observed for 3 out-of-scope questions, which behavior is most desirable and why, and what prompt change (if any) you found that produces that behavior.

---

With the protocol understood from Part I and II, this Hands-On section has you build three distinct tools — a safe arithmetic evaluator, a clock, and a word counter — and observe exactly how the model decides which one to call based solely on the tool's description field.

## Hands-On: Build and Call a Tool (30 minutes)

In this section you define three tools using the OpenAI function-calling JSON schema format (the standard way to describe a tool's name, purpose, and parameters as a JSON object) and call them from your local model via Ollama's `/api/chat` endpoint. Run all code locally — no external API keys or cloud services needed.

---

### Tool Definitions

Each tool is a JSON object with a `name`, a `description` (the only thing the model reads to decide whether to use this tool), and a `parameters` block written in JSON Schema:

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

The executor pattern keeps a **registry** (a plain Python dictionary mapping tool names to their implementations). Your agent loop never calls a tool directly from the model's request; it looks up the name in the registry first. This is the security boundary: only tools you explicitly register can ever run. Notice that the `calculator` function uses Python's `ast` module (a library for safely parsing code into a tree of operations) rather than `eval()` — see the note after the code block for why this matters.

```python
import ast
import operator
import datetime

# Safe arithmetic evaluator — no eval() of arbitrary code
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

Note that `calculator` uses Python's `ast` module to parse the expression rather than calling `eval()`. This is intentional: `eval()` on a model-supplied string is an arbitrary code execution vulnerability. The `_safe_eval` function only handles numeric literals and the four arithmetic operators, so the model cannot inject `import os; os.system(...)` or any other dangerous expression.

---

### The Agent Loop

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
            # Model chose to answer directly — no tool needed
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

7. The model decides whether to call a tool based on the tool's **description**, not its name. Change the `calculator` tool's description to `"counts the words in text"` and re-run the word-count question. What does the model do? What does this tell you about where the real "logic" of tool selection lives?

   > *Hint: The model never sees your Python function bodies — it only sees the JSON schema. Swapping the description effectively swaps the tool's identity from the model's perspective. Run `agent("How many words are in 'hello world'?")` with the swapped description and observe which tool fires.*

[[MC]]
When the agent loop appends a tool result back into the conversation, what `role` value must that message use?
- ( ) `"user"`
- ( ) `"assistant"`
- (x) `"tool"`
- ( ) `"system"`

> *Hint: Look at the line `msgs.append({"role": "tool", "content": result})` in the agent loop. The OpenAI-compatible API (which Ollama follows) requires the role `"tool"` so the model knows this message is a function result rather than a user turn or its own prior response.*

8. Consider a fourth tool: `read_file(path: str) -> str` that opens a file path supplied by the user and returns its contents. What security risk does this create, and what would you do to mitigate it?

   > *Hint: Think about what happens when the model (prompted by a malicious user) supplies the path `/etc/passwd`, `~/.ssh/id_rsa`, or `../../config/secrets.json`. The mitigation involves restricting which directories the tool is allowed to read from — for example, only allowing paths that begin with an approved prefix such as `/home/user/documents/`. You might also check that the resolved absolute path (after following symlinks with `os.path.realpath`) still begins with that prefix, to prevent path traversal attacks.*

> **⚠️ Common Misconception:** Students often assume `tool_choice="auto"` means the model will always call a tool. In reality, it means the model *may* call a tool if it decides one is needed — but it can also answer from memory without calling any tool at all. If you need a specific tool to be invoked for every request (for safety, auditing, or consistency), set `tool_choice={"type": "function", "function": {"name": "tool_name"}}` to force it. The difference matters for tools like `log_query` that you want called every time regardless of the model's judgment.

---

## Reflection Prompt

*Personal:* In your notebook: with tools, an agent's words become actions. Recall a moment when you gave an instruction — to a person or a system — that was carried out too literally and produced an unintended result. What would "asking a clarifying question first" look like as an agent design feature, and when should an agent be required to use it?

*Technical:* The registry is a security boundary, but it is not the only one needed. For a `send_email(to, body)` tool, list three additional safeguards you would implement at the code level (not the prompt level), and explain what attack or mistake each one prevents.

*Societal:* Tool-calling agents can take actions at machine speed — sending thousands of emails, making purchases, or modifying files in seconds. Name one professional domain (medicine, law, finance, education) where this speed is a benefit, and one where it is a serious risk. What institution or regulatory body should set the rules for how fast AI agents are allowed to act?

---

## → Coming Up Next

Our agents can now call tools, but each agent works alone. The next major topic in the course introduces **multi-agent systems**: teams of specialized agents that collaborate, delegate, and check each other's work — and the governance challenges that arise when agents are supervising other agents.

---

## 4. Further Reading

- Ollama tool-calling documentation: https://github.com/ollama/ollama/blob/main/docs/api.md
- Schick et al. "Toolformer: Language Models Can Teach Themselves to Use Tools." *NeurIPS* (2023).
- Mialon et al. "Augmented Language Models: A Survey." *TMLR* (2023).
- [Multimodal AI and Monte Carlo Simulation lab](/Assignments/MonteCarlo) — a complete tool-calling case study: the simulation is wrapped as a schema-described tool, and an agent chooses its parameters, invokes it, and interprets the resulting chart.
- [Monte Carlo Retirement companion notebook](/files/notebooks/MonteCarloRetirement.ipynb) — a runnable version of that lab, including the full function-calling agent loop with offline sample responses.
