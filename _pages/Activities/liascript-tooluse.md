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

Our week 1 agent parsed `calc(...)` out of free text with a regular expression, and it worked until it did not. Today we upgrade to **structured function calling**: the model emits a machine-readable request to invoke a function, and the runtime executes it. We move from **why structure beats parsing $\rightarrow$ tool schemas $\rightarrow$ native function calling with Ollama $\rightarrow$ safety boundaries for tools that change the world**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: From Parsing to Protocol

## 1. The Contract

**A tool is a typed function the model may request.** We describe each tool with a schema: name, natural-language description, and parameters with types. The description is not documentation for humans; it is *the only thing the model knows about the tool*, so writing it clearly is prompt engineering. Modern chat APIs (including Ollama's) accept a `tools` list and return, when the model chooses, a structured `tool_calls` field instead of prose:

```
request:  messages + tools=[{name, description, parameters}]
response: message.tool_calls = [{function: {name: "get_weather", arguments: {"city": "Collegeville"}}}]
```

The runtime executes the function, appends the result as a `tool` role message, and calls the model again, which is precisely our perceive-plan-act loop with the parsing risk engineered away. The model never executes anything; it only *asks*. Authority lives in our code, which is where governance will attach.

---

## Model 1: Schema as Interface

Two teams expose the same function with different descriptions:

| Team A | Team B |
|--------|--------|
| `lookup(s)`: "looks stuff up" | `course_lookup(course_code)`: "Given an Ursinus course code like CS357, returns title, meeting times, and prerequisites from the live catalog." |

### Critical Thinking Questions

1. For the user question "When does the AI class meet?", which schema gives the model enough signal to (a) choose the tool and (b) construct correct arguments? Identify the failure mode Team A invites.
2. The model passes `course_code="the AI class"`. Whose bug is this, the model's or the schema's, and what one schema change reduces it?
3. List the three places natural language appears in this protocol, and rank them by how much care they deserve.

---

# Part II: Native Function Calling

## 2. A Two-Tool Agent

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
     "description": "Returns today's date in ISO format (YYYY-MM-DD).",
     "parameters": {"type": "object", "properties": {}, "required": []}}},
  {"type": "function", "function": {
     "name": "days_until",
     "description": "Returns the number of days from today until the given ISO date.",
     "parameters": {"type": "object",
                    "properties": {"target_iso": {"type": "string",
                                                  "description": "Date in YYYY-MM-DD form"}},
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

### Critical Thinking Questions

4. List the exact sequence of messages (roles and contents) exchanged for the question above. Which message was authored by our Python code rather than by a human or the model?
5. The registry lookup `REGISTRY[name]` is a security boundary. What does it prevent that a Python `eval` of the model's text would not?
6. Add (on paper) a `send_email(to, body)` tool. Which single line of today's code would you wrap with a human-confirmation gate, and why there rather than in the prompt?

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
2. *Schema ablation.* Replace both tool descriptions with the single word "tool" and rerun your test questions. Report the tool-selection accuracy before and after; connect the result to Model 1.
3. *Read-write taxonomy.* Classify ten plausible tools (search, calendar read, calendar write, file delete, grade lookup, post to social media, and so on) as read-only, reversible-write, or irreversible-write. Propose a default policy for each class. Keep this taxonomy: it becomes part of your project governance document.
4. *Refusal behavior.* Ask the agent a question no tool can answer. Does it improvise a tool call, hallucinate an answer, or say it cannot help? Report and explain which behavior you want and how to prompt for it.

---

## Reflection Prompt

In your notebook: with tools, an agent's words become actions. Recall a moment when you gave an instruction (to a person or a system) that was carried out too literally. What would "asking a clarifying question first" look like as an agent design feature, and when should an agent be required to do it?

---

## 4. Further Reading

- Ollama tool-calling documentation: https://github.com/ollama/ollama/blob/main/docs/api.md
- Schick et al. "Toolformer: Language Models Can Teach Themselves to Use Tools." *NeurIPS* (2023).
- Mialon et al. "Augmented Language Models: A Survey." *TMLR* (2023).
