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

# Part III: Synthesis and Practice

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
