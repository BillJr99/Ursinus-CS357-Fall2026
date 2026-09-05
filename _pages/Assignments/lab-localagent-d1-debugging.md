---
layout: assignment
permalink: /Assignments/LocalAgent/Direction1
title: "CS357 Lab: Local Agent, Direction 1: Debugging a Broken Agent"
---

> **Grading:** This page is one of the directions for the [Local Agent Lab]({{ site.baseurl }}/Assignments/LocalAgent).  It has no separate point value and no rubric of its own.  I grade your combined core and direction work with the Local Agent Lab rubric on the core lab page.

> **Rather not write the code?**  [Direction 0: The OpenWebUI Route]({{ site.baseurl }}/Assignments/LocalAgent/Direction0) reaches the same objectives for the Local Agent Lab with no code to write; you build and evaluate the same system as configuration instead.  Pick whichever direction fits how you want to work.  The credit is the same either way.

> **What this direction requires**
>
> - **Accounts:** none.
> - **API costs:** none; every model call goes to your local Ollama server.
> - **Installs / disk:** nothing beyond the core lab setup (Ollama with `llama3.2`, ~2 GB, and the Python `requests` library).
> - **Hardware:** any machine that runs the core lab.
> - **No-cost fallback:** not needed; this direction is already fully local and free.

---


In this direction you turn the debugging and instrumentation discipline from the core lab on a research agent that someone else wrote, seeded with five deliberate bugs.  Your job is to find them, fix them, explain them, and then instrument the agent so the same bugs would be unmistakable if they reappeared.

Agent bugs differ from ordinary software bugs.  A function that returns the wrong value gives you the wrong value immediately.  An agent with a bug might produce a convincing but incorrect answer, loop forever on a malformed tool call, silently drop the tool result and answer from memory, or reach its step budget without telling you why.

**Why this matters:** In production, agent bugs cost real money and trust.  When an agent-assisted code review approves a vulnerability, or an agent-assisted customer service tool gives wrong refund information, the human in the loop often did not catch it because the agent was confidently wrong.  You need both debugging skill and defensive instrumentation.  A stack trace points to a line number, but an agent failure often shows up many steps after its root cause; the bug may be in how tool results are fed back, not in the tool itself.  You will practice tracing cause through effect across the message history, which is the core skill of agent debugging.

Complete this lab in **pairs using driver/navigator roles**: the driver types while the navigator reviews, questions, and consults documentation.  **Swap roles at least every 30 minutes** and log each swap time with who held each role.

---

#### Before You Start

**Prerequisite concepts**: complete these before you write any code:

- [Agent Loop Activity]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-agentloop.md): the perceive/plan/act/remember cycle
- The Local Agent Lab, or working familiarity with the Ollama `/api/chat` endpoint and the `requests` library

**Tools to install:**

```bash
# Confirm Ollama is running and a model is available
ollama list

# All other dependencies are Python standard library (requests, json, logging, time)
pip install requests   # only if not already installed
```

**Health check**: run this before you start:

```bash
curl -s http://localhost:11434/api/tags | python3 -m json.tool | head -10
```

Expected output includes `"name": "llama3.2:latest"` (or whichever model you have pulled).

**Pair programming setup:**

Keep a log file called `pair_log.txt` in your project folder.  Each entry looks like:

```
2025-09-15 10:00  Driver: Alice  Navigator: Bob
2025-09-15 10:32  Driver: Bob    Navigator: Alice
```

**Estimated time budget:**

| Part | Task | Estimated time |
|------|------|----------------|
| Part 1 | Reproduce and Diagnose | 30-45 min |
| Part 2 | Fix All Five Bugs | 45-60 min |
| Part 3 | Add Structured Logging | 30-45 min |
| Part 4 | Write the Test Suite | 30-45 min |
| Writeup | Readme and reflection | 30 min |

---

#### The Broken Agent

Copy the file below into your project as `broken_agent.py`.  Do not fix anything yet.  Run it first and observe the symptoms in Part 1.

```python
"""
broken_agent.py - A deliberately broken research agent for CS357 Lab.
Find and fix 5 bugs. Each bug is marked with # BUG [N] - but the comment
does NOT tell you what the bug is. You must diagnose it from the symptoms.
"""
import requests
import json
import time

CONFIG = {
    "model": "llama3.2",
    "ollama_url": "http://localhost:11434",
    "max_steps": 8,
    "temperature": 0.7,
}

TOOLS = {
    "search_facts": "Search a local knowledge base for facts. Args: topic (string)",
    "calculate": "Evaluate an arithmetic expression safely. Args: expression (string like '5 * 12')"
}

FACT_DB = {
    "eiffel tower": "The Eiffel Tower is 330 meters tall, located in Paris, and completed in 1889.",
    "python": "Python is a programming language created by Guido van Rossum, first released in 1991.",
    "moon": "The Moon orbits Earth at an average distance of 384,400 km.",
    "speed of light": "The speed of light in a vacuum is approximately 299,792,458 meters per second.",
    "pi": "Pi (π) ≈ 3.14159265358979. It is the ratio of a circle's circumference to its diameter.",
}

def search_facts(topic: str) -> str:
    key = topic.lower().strip()
    return FACT_DB.get(key, f"No information found about: {topic}")

def calculate(expression: str) -> str:
    # BUG 1 - this implementation has a security issue that also breaks on some inputs
    import ast
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # BUG 1: restricted but still dangerous + breaks on floats like "3.14e2"
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"

def get_system_prompt() -> str:
    tool_desc = "\n".join(f"- {name}: {desc}" for name, desc in TOOLS.items())
    return f"""You are a research assistant with access to these tools:
{tool_desc}

When you need information or to calculate something, respond with EXACTLY:
ACTION: <tool_name>
INPUT: <input>

When you have the final answer, respond with EXACTLY:
FINAL: <your answer>

Use tools whenever you are not certain. Do not answer from memory for factual questions."""

def parse_response(text: str):
    """Parse ACTION/INPUT or FINAL from model response."""
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    action = None
    input_val = None
    final = None

    for line in lines:
        # BUG 2: split on first colon only - values like "http://example.com" get truncated
        if line.startswith("ACTION:"):
            action = line.split(":")[1].strip()  # BUG 2
        elif line.startswith("INPUT:"):
            input_val = line.split(":")[1].strip()  # BUG 2
        elif line.startswith("FINAL:"):
            final = line.split(":", 1)[1].strip()  # This one is correct - notice the difference

    return action, input_val, final

def run_agent(user_query: str) -> str:
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": user_query}
    ]

    for step in range(CONFIG["max_steps"]):
        # BUG 3: stream=True returns server-sent events, not a single JSON object
        resp = requests.post(
            f"{CONFIG['ollama_url']}/api/chat",
            json={
                "model": CONFIG["model"],
                "messages": messages,
                "stream": True,   # BUG 3
                "options": {"temperature": CONFIG["temperature"]}
            }
        ).json()

        message = resp["message"]
        response_text = message["content"]
        messages.append({"role": "assistant", "content": response_text})

        action, input_val, final = parse_response(response_text)

        if final:
            return final

        if action:
            input_val = input_val or ""

            if action == "search_facts":
                result = search_facts(input_val)
            elif action == "calculate":
                result = calculate(input_val)
            else:
                result = f"Error: unknown tool '{action}'"

            # BUG 4: tool results should be added as 'tool' role (or as 'user' with context),
            # not as 'assistant' - this makes the model think it called the tool itself
            messages.append({
                "role": "assistant",  # BUG 4
                "content": f"[Tool result: {result}]"
            })
        else:
            # Model gave neither a tool call nor a FINAL answer - nudge it
            messages.append({
                "role": "user",
                "content": "Please either use a tool (ACTION: / INPUT:) or give your FINAL: answer."
            })

    # BUG 5: silently returns None instead of a clear "max steps reached" message
    return None  # BUG 5

if __name__ == "__main__":
    queries = [
        "How tall is the Eiffel Tower in feet? (1 meter = 3.28084 feet)",
        "What is pi to 3 decimal places, and what is pi squared?",
        "How far is the Moon from Earth in miles? (1 km = 0.621371 miles)",
    ]
    for q in queries:
        print(f"\nQuery: {q}")
        result = run_agent(q)
        print(f"Answer: {result}")
```

---

#### Part 1: Reproduce and Diagnose

**Do not fix anything yet.**  Run the broken agent and observe carefully what happens for each of the three sample queries.

##### Step 1: Run and observe

```bash
python broken_agent.py
```

For each query, note:
- Does the program crash?  If so, what is the error message and traceback?
- Does it return `None` or print `Answer: None`?
- Does it return an incorrect answer without crashing?
- Does it appear to loop or hang?

##### Step 2: Fill in the diagnosis table

Create a file called `diagnosis.md` in your project and fill in this table before you write any fixes:

| Bug # | Observable symptom | File / line number | Root cause (your hypothesis) |
|-------|-------------------|--------------------|------------------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

**Hint for Bug 3:** If the first run crashes with a JSON-related error, inspect the raw bytes returned by `requests.post(...).content` before calling `.json()`.  What do you see?

**Hint for Bug 2:** Try a query that involves the `calculate` tool with a floating-point number like `3.14`.  Does the INPUT value arrive at the tool function as expected?

##### Step 3: Identify which bugs crash vs. which fail silently

Write one sentence for each bug: is it a crash (exception raised, traceback printed) or a silent failure (wrong answer returned with no error)?

---

> **Checkpoint: Before moving to Part 2, make sure you can answer:**
> 1.  Which of the five bugs causes a crash on the very first API call?  What is the exception type?
> 2.  Which bugs could produce a wrong answer without any Python exception being raised?
> 3.  Why is a silent wrong answer generally harder to catch than a crash?

---

#### Part 2: Fix All Five Bugs

Work through the bugs one at a time.  After you fix each one, rerun the three sample queries and confirm that the symptom you observed in Part 1 is gone before you move to the next fix.

##### Bug 1: `calculate` function

The `calculate` function calls `eval` with `{"__builtins__": {}}` as the globals.  This is meant as a safety measure, but it has two problems.  First, it is not actually safe: certain Python expressions can escape the sandbox.  Second, it fails on floating-point scientific notation like `3.14e2`, because `e` is not a recognized name in the empty namespace.

**Fix:** Replace `eval` with `ast.literal_eval`, which parses only Python literals.  For arithmetic expressions, use an allowlist approach with the `ast` module to parse and evaluate safely, or restrict the allowed character set.  A minimal fix:

```python
def calculate(expression: str) -> str:
    """Evaluate a simple arithmetic expression. Supports +, -, *, /, ** and floats."""
    # TODO: Replace the eval-based implementation with one that:
    # (a) supports floating-point scientific notation (e.g., "3.14e2")
    # (b) does not use eval with unrestricted globals
    # Hint: import ast and use ast.parse + a recursive node evaluator,
    # or restrict the character allowlist to: digits, spaces, +-*/.**()e.E
    pass
```

##### Bug 2: `parse_response` function

Look at this line:

```python
action = line.split(":")[1].strip()  # BUG 2
```

Compare it to the correct version used for FINAL:

```python
final = line.split(":", 1)[1].strip()  # This one is correct
```

The difference is the `1` argument to `split`.  Without it, `split(":")` splits on every colon.  `INPUT: 3.14e2` becomes `["INPUT", " 3.14e2"]`, which is harmless in that case.  But `INPUT: http://example.com` becomes `["INPUT", " http", "//example.com"]`, and only `http` reaches the tool.

**Fix:** Change both the `ACTION:` and `INPUT:` lines to use `split(":", 1)`.

##### Bug 3: Streaming mode

The `requests.post` call uses `"stream": True`.  When Ollama streams, it sends the response as a sequence of newline-delimited JSON objects (one per token), not as a single JSON body.  Calling `.json()` on a multi-line response raises a `JSONDecodeError`, because the decoder stops at the first complete JSON object and finds unexpected data after it.

**Error message you observed** (approximately):

```
json.decoder.JSONDecodeError: Extra data: line 2 column 1 (char ...)
```

**Fix:** Change `"stream": True` to `"stream": False`.  With streaming disabled, the API returns a single JSON object and `.json()` works correctly.

```python
resp = requests.post(
    f"{CONFIG['ollama_url']}/api/chat",
    json={
        "model": CONFIG["model"],
        "messages": messages,
        "stream": False,   # Fixed: was True
        "options": {"temperature": CONFIG["temperature"]}
    }
)
resp.raise_for_status()
data = resp.json()
```

##### Bug 4: Wrong role for tool results

After a tool runs, the code appends the result to `messages` with `"role": "assistant"`.  The message history then looks as if the *model itself* produced the tool result, as if the assistant generated a line saying `[Tool result: 330 meters...]`.  On the next step, the model sees its own previous response and may keep generating more tool invocations instead of treating the result as a grounded observation.

The correct role for a tool result injected by the Python code (not generated by the model) is `"user"`, which tells the model "here is information from the environment."  Add clear framing so the model knows it is an observation:

```python
messages.append({
    "role": "user",   # Fixed: was "assistant"
    "content": f"Observation from tool '{action}': {result}"
})
```

##### Bug 5: Silent `None` return

When `max_steps` runs out, the function falls off the end of the loop and implicitly returns `None`.  Any code that calls `run_agent` and receives `None` will either crash with an `AttributeError` (if it calls a method on the result) or silently print `Answer: None`.  Neither tells the operator why the agent stopped.

**Fix:** Return a descriptive string when the budget runs out:

```python
    # After the loop ends
    return (
        f"[Agent stopped: step budget of {CONFIG['max_steps']} steps exhausted. "
        f"Last response: {messages[-1]['content'][:200]}]"
    )
```

##### Confirm all fixes

After you apply all five fixes, rerun the three sample queries.  Expected behavior:

```yaml
Query: How tall is the Eiffel Tower in feet? (1 meter = 3.28084 feet)
Answer: The Eiffel Tower is 330 meters tall, which is approximately 1082.68 feet.

Query: What is pi to 3 decimal places, and what is pi squared?
Answer: Pi to 3 decimal places is 3.142. Pi squared is approximately 9.870.

Query: How far is the Moon from Earth in miles? (1 km = 0.621371 miles)
Answer: The Moon is approximately 384,400 km from Earth, which is about 238,855 miles.
```

Your exact wording will differ.  What matters is that: (a) no crash occurs, (b) no `None` appears, (c) the numerical answers are correct.

---

> **Checkpoint: Before moving to Part 3, make sure you can answer:**
> 1.  Bug 3 caused a crash.  Bugs 1, 2, 4, and 5 caused wrong or missing answers.  Which class of bug is easier to detect in production and why?
> 2.  Why does adding `raise_for_status()` after the `requests.post` call improve observability even when the server returns a valid response?
> 3.  After fixing Bug 4, run a query that requires two tool calls.  Paste the full message history (all `messages` entries) after both tool calls have completed.  Does it look correct now?

---

#### Part 3: Add Structured Logging

Observability means that when something goes wrong, the log tells you what happened and when.  A print statement at key points is a start.  Structured logging adds severity levels, timestamps, and a persistent file, and you need all three when an agent runs unattended.

##### Step 1: Set up the logger

Add this function to `broken_agent.py` (you will rename the fixed version `agent.py`):

```python
import logging
import datetime

def setup_logging(log_file: str = "agent_trace.log") -> logging.Logger:
    """
    Configure logging to write to log_file AND to the console.

    Console handler: INFO level and above, format includes timestamp and level.
    File handler: DEBUG level and above (captures everything), same format.

    TODO: Return a Logger named "agent" with both handlers attached.
    Use the format string:
      "%(asctime)s [%(levelname)s] %(message)s"

    The returned logger should be used throughout run_agent via extra={} fields
    or by passing it as a parameter.
    """
    pass
```

##### Step 2: Add log calls at key events

In `run_agent`, add logging at each of the following points.  Make each log message self-contained: someone reading the log file without the source code should understand what happened.

| Event | Level | Fields to log |
|-------|-------|---------------|
| Step start | INFO | step number, total steps allowed, query (truncated to 80 chars) |
| Tool invocation | INFO | step number, tool name, tool arguments |
| Tool result received | INFO | step number, tool name, result (truncated to 200 chars) |
| FINAL answer returned | INFO | step number, response length in characters, elapsed time since query start |
| Unexpected model format (neither tool call nor FINAL) | WARNING | step number, raw response (truncated to 200 chars) |
| Max steps exhausted | WARNING | max_steps value, last response truncated to 100 chars |
| Any exception (network, JSON parse, etc.) | ERROR | exception type, message, step number |

##### Step 3: Verify the log file

After you run the three sample queries, your `agent_trace.log` should contain entries like:

```
2025-09-15 10:14:02,881 [INFO] Step 1/8 | Query: "How tall is the Eiffel Tower in feet?"
2025-09-15 10:14:04,103 [INFO] Step 1/8 | Tool call: search_facts("eiffel tower")
2025-09-15 10:14:04,104 [INFO] Step 1/8 | Tool result (search_facts): "The Eiffel Tower is 330 meters tall..."
2025-09-15 10:14:05,447 [INFO] Step 2/8 | Tool call: calculate("330 * 3.28084")
2025-09-15 10:14:05,448 [INFO] Step 2/8 | Tool result (calculate): "1082.6772"
2025-09-15 10:14:07,211 [INFO] Step 3/8 | FINAL answer returned | length=68 chars | elapsed=4.33s
```

Include a snippet of your actual log output in your writeup.

---

> **Checkpoint: Before moving to Part 4, make sure you can answer:**
> 1.  What is the difference between `logging.INFO` and `logging.WARNING`?  Give one concrete example from your agent where each is appropriate.
> 2.  Why write logs to a file in addition to the console?  Name one scenario where the console output is gone but the file log is what saves you.
> 3.  If a user runs your agent overnight and you find `Answer: None` in the output, what would you look for first in `agent_trace.log`?

---

#### Part 4: Write the Test Suite

A test suite catches regressions.  If you change the agent later and accidentally re-introduce a bug, the tests tell you immediately, rather than letting a user discover it.

##### Step 1: Create `test_agent.py`

```python
"""
test_agent.py - Regression tests for the fixed research agent.
Run with: python test_agent.py
Each test prints PASS or FAIL with the actual output.
"""
from agent import run_agent, CONFIG  # import from your fixed agent file

def run_tests():
    """Run all 5 test cases. Print PASS/FAIL for each."""
    tests = [
        {
            "name": "fact_retrieval",
            "description": "Agent retrieves a known fact from the knowledge base",
            "query": "What year was Python created?",
            "check": lambda r: r is not None and "1991" in r,
        },
        {
            "name": "two_tool_chain",
            "description": "Agent chains search_facts then calculate in sequence",
            "query": "What is the height of the Eiffel Tower in meters, multiplied by 3.28084?",
            "check": lambda r: r is not None and any(n in r for n in ["1082", "1083", "1,082", "1,083"]),
        },
        {
            "name": "empty_query",
            "description": "Agent handles an empty input without crashing",
            "query": "",
            "check": lambda r: r is not None,  # Must not crash or return None
        },
        {
            "name": "unknown_topic_abstains",
            "description": "Agent reports no information rather than confabulating",
            "query": "What is the population of Atlantis?",
            "check": lambda r: r is not None and (
                "No information" in r
                or "not found" in r.lower()
                or "don't know" in r.lower()
                or "cannot find" in r.lower()
            ),
        },
        {
            "name": "step_budget_respected",
            "description": "Agent terminates within max_steps even on an unsolvable query",
            "query": "Keep searching until you find the meaning of life. Never stop searching.",
            "check": lambda r: r is not None,  # Must terminate and return a string
        }
    ]

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n{'='*60}")
        print(f"TEST: {test['name']}")
        print(f"  {test['description']}")
        print(f"  Query: {repr(test['query'][:80])}")

        # TODO: Call run_agent with test["query"]
        # Apply test["check"] to the result
        # Print PASS or FAIL with the actual result (truncated to 150 chars)
        result = None  # replace with actual call
        ok = False     # replace with actual check

        if ok:
            passed += 1
            print(f"  PASS | Result: {repr(str(result)[:150])}")
        else:
            failed += 1
            print(f"  FAIL | Result: {repr(str(result)[:150])}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
```

##### Step 2: Complete the TODO in `run_tests`

Fill in the two lines marked `# TODO`.  Then run:

```bash
python test_agent.py
```

Expected output when all bugs are fixed:

```
============================================================
TEST: fact_retrieval
  Agent retrieves a known fact from the knowledge base
  Query: 'What year was Python created?'
  PASS | Result: 'Python was created by Guido van Rossum and first released in 1991.'

============================================================
TEST: two_tool_chain
  Agent chains search_facts then calculate in sequence
  Query: 'What is the height of the Eiffel Tower in meters, multiplied by 3.28084?'
  PASS | Result: '330 meters × 3.28084 = approximately 1082.68 feet.'

============================================================
TEST: empty_query
  Agent handles an empty input without crashing
  Query: ''
  PASS | Result: 'I need a question to help you. Please provide a topic or query.'

============================================================
TEST: unknown_topic_abstains
  Agent reports no information rather than confabulating
  Query: 'What is the population of Atlantis?'
  PASS | Result: 'No information found about: Atlantis.'

============================================================
TEST: step_budget_respected
  Agent terminates within max_steps even on an unsolvable query
  Query: 'Keep searching until you find the meaning of life. Never stop searching.'
  PASS | Result: '[Agent stopped: step budget of 8 steps exhausted. Last response: ...]'

============================================================
Results: 5 passed, 0 failed out of 5 tests
```

##### Step 3: Run the tests against the unfixed agent (optional but worth doing)

Before you make your fixes, run `test_agent.py` against `broken_agent.py` by temporarily importing from it.  Document which tests fail and why.  This shows the value of having tests before fixing: you can see the before-state clearly.

---

> **Checkpoint: You have succeeded when:**
> - All five bugs are identified in `diagnosis.md` with symptom, line number, and root cause
> - The fixed `agent.py` runs all three sample queries without crashes or `None` returns
> - `agent_trace.log` contains a complete trace of at least one successful multi-step query
> - `python test_agent.py` exits with code 0 (all five tests pass)
> - Your writeup explains the diagnostic process for each bug, not only the fix

---

#### Troubleshooting

**Bug 3 crash, `JSONDecodeError: Extra data`**

When `stream=True`, Ollama sends the response as multiple lines, each a valid JSON object, one per token.  Calling `.json()` on the full response body fails because the parser hits the second JSON object and treats it as unexpected data.  The fix is `"stream": False`.  To inspect the raw body before fixing, replace `.json()` with `.text` and print the first 500 characters; you will see multiple JSON lines.

**Bug 4 symptom, model generates repeated tool result lines**

When tool results carry the `"assistant"` role, the model on the next step sees its own prior content and may continue it, generating additional `[Tool result: ...]` lines as if it were producing more tool output.  After the fix (`"role": "user"`), the model sees the tool result as an incoming observation and responds to it rather than continuing it.

**Bug 5 symptom, `Answer: None` printed with no error**

Python functions return `None` implicitly when no `return` statement is reached.  The caller receives `None`, and `print(f"Answer: {result}")` prints `Answer: None` with no indication of why.  Always make budget exhaustion explicit with a return value that contains the word "stopped" or "exhausted" so callers can detect it without inspecting the return type.

**Bug 1, `calculate` fails on scientific notation**

The expression `3.14e2` is valid Python, but `eval(..., {"__builtins__": {}}, {})` evaluates in a namespace with no names, including `e`.  Python parses `3.14e2` as a float literal (not as `3.14 * e^2`), so it should work in a bare `eval`.  The failure actually comes from certain compound expressions.  Verify that your fix handles: `"330 * 3.28084"`, `"3.14e2"`, `"9.870841"`, and `"384400 * 0.621371"`.

**Test `unknown_topic_abstains` fails, model confabulates an answer**

Some local models answer questions about unknown topics confidently rather than reporting uncertainty.  If this test fails reliably, add an explicit guardrail to the system prompt: "If the search_facts tool returns 'No information found', you must include that phrase verbatim in your FINAL answer.  Do not answer from memory."  Re-run the test after adding the guardrail and note the change in the writeup.

---

#### Reflection Prompts

Answer these in your writeup (`readme.md`), approximately one paragraph each:

1.  **Crash vs. silent failure.**  Bug 3 caused a crash.  Bugs 1, 2, 4, and 5 caused wrong or missing answers without raising an exception.  Which type is harder to debug in a deployed system and why?  What instrumentation would catch silent failures automatically?

2.  **Role confusion.**  Bug 4 caused the model to attribute the tool result to itself.  What behavior did you observe in the message history?  Write 2-3 sentences explaining why this confused the model's later responses; refer to how the model uses conversational role context to decide what to generate next.

3.  **Hardest bug.**  Which bug was hardest to find, and what made it hard?  Was it the distance between cause and symptom, the absence of a crash, or something else?

4.  **Architectural prevention.**  What single architectural change would make the most bugs impossible?  Consider: what if the message history were an immutable append-only log validated at each step?  What if tool results were typed (e.g., a `ToolResult` dataclass) rather than raw strings?  Pick one structural change and argue which class of bugs it would eliminate.

5.  **Confidence and correctness.**  Agent bugs often appear as "convincing wrong answers" rather than crashes.  How does this affect your confidence in agent outputs you have not specifically tested?  What would a production team need to do before trusting an agent to produce outputs that are acted on without human review?

6.  **Pair programming.**  How did the driver/navigator split change how you diagnosed the bugs?  Describe one instance where the navigator caught something the driver missed.

---

#### Deliverables

Submit a ZIP containing:

- `agent.py`: the fully fixed agent (renamed from `broken_agent.py`)
- `test_agent.py`: the complete test suite with all five test cases implemented
- `agent_trace.log`: the log file from at least one complete run of the three sample queries
- `diagnosis.md`: the completed diagnosis table (symptom, line, root cause for each bug)
- `readme.md`: approximately two pages covering: the diagnostic process for each bug, the logging design, the test design, and answers to the reflection prompts
- `pair_log.txt`: the driver/navigator swap log

Make sure `python test_agent.py` exits cleanly on a fresh run before you submit.

---

#### Submission Checklist

Before submitting, verify each item:

- [ ] `broken_agent.py` is included unchanged alongside the fixed `agent.py` (so the grader can compare)
- [ ] All five bugs are documented in `diagnosis.md` with observable symptom, line number, and root cause
- [ ] `python agent.py` runs all three sample queries without crash or `None` output
- [ ] `python test_agent.py` exits with code 0 (5/5 tests pass)
- [ ] `agent_trace.log` contains at least one complete multi-step trace including tool calls
- [ ] Logging writes to both console and file; INFO for normal flow, WARNING for unexpected behavior, ERROR for exceptions
- [ ] `readme.md` explains the diagnostic process (not only the fix) for each bug
- [ ] `readme.md` identifies the hardest bug and proposes one structural architectural change
- [ ] `pair_log.txt` shows at least two role swaps with timestamps
- [ ] Software versions are listed (Python version, Ollama version, model name)
