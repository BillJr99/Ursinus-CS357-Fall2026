<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-agentloop.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-agentloop.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Agent Loop: Perceive, Plan, Act

In the *Welcome: What Is AI, and What Is an Agent?* activity we placed systems on an agency spectrum; today we build the machinery that moves a system along it.  This module develops the **agent loop**, the control structure that turns a reactive language model into a goal-directed system.  We move from **intuition $\rightarrow$ the sense-think-act cycle $\rightarrow$ the ReAct pattern $\rightarrow$ a working agent loop in Python** against a local Ollama model.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| Agent loop | The repeating cycle in which an agent reads its situation, decides on an action, executes it, and updates its memory, then repeats until the goal is reached | The `run_agent` function in Part II: it calls the model, parses the output, runs a calculator, feeds the result back, and loops |
| Policy (pi) | The decision-making rule that maps the agent's current knowledge and goal to its next action | The language model that reads the full conversation history and decides whether to call `calc(...)` or emit `Final Answer:` |
| ReAct pattern | A prompting style (Reason + Act) where the model is asked to write out its reasoning as text before choosing an action, producing a trace that humans can audit | The Thought / Action / Observation transcript shown in Part I |
| Step budget | A hard limit on how many loop iterations an agent may take, preventing infinite loops when a goal is never satisfied | `max_steps=5` in the `run_agent` function |
| Memory (context) | The running list of everything the agent has seen and said so far, passed to the model at each step so it can build on prior work | The `memory` list that grows with each assistant message and observation |
| Tool | A function in the surrounding program that the agent can invoke by name to interact with the world; the model cannot run code itself | The `eval()` call that executes arithmetic when the model outputs `calc(...)` |
| System prompt | A block of standing instructions sent ahead of the user's message, setting the agent's job, its output format, and its limits. The user never sees it; the model treats it as the rules of the room | The `SYSTEM` string in Part II, which tells the agent it may call `calc(...)` and exactly how to format `Thought:` / `Action:` lines. Writing good ones is the whole subject of *Prompt Engineering as Agent Design* |
| Model | The specific trained language model doing the generating, named like a package version. Different models have different sizes, speeds, and habits | `MODEL = "llama3.2"` in the code cell below; you install and run this one yourself in the *Running Your Own AI* activity |
| Temperature | A setting between 0 and about 2 that controls how much the model varies its wording. Near 0 it picks its single most likely next word every time, so the same prompt gives you nearly the same answer; higher values let it wander. Today you only need to know that **0 means repeatable**; you will turn this dial yourself in *Running Your Own AI* and learn what it is actually doing to the math in *Why Different Answers Every Time? Sampling, Temperature, and Generation* | `temperature=0.0` in `run_agent`, chosen so a trace you record today reproduces tomorrow |

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Key Concepts and the search-and-rescue framing: what makes a loop an agent |
| 10-30 | Part I, the sense-think-act cycle and the ReAct trace, worked on paper |
| 30-60 | Part II, paper-trace the minimal tool-using agent step by step |
| 60-75 | Part III, the budget experiment and the failure hunt; Reflection at home |

---
## 0.  Environment and Utilities

This section sets up the Python helper function that all later code cells will reuse.  It sends a list of messages (the conversation history so far) to a locally running Ollama server and returns the model's reply as a plain string.  You don't need to understand every line yet; just run it and confirm the "Environment ready." message appears before moving on.

This section assumes Ollama is running locally (we install it together in the *Running Your Own AI: Ollama, OpenWebUI, and Private Local Models* activity; today your instructor's machine serves the room).  The only dependency is `requests`.

---

## Code Cell

> **Today: trace on paper, run after the install session.**  Ollama is not on your machines yet; we install it together in the *Running Your Own AI: Ollama, OpenWebUI, and Private Local Models* activity.  Today your team traces the agent loop **on paper**; run this and the later code cells after that install session.  Paper-trace protocol:
>
> 1.  Given the user query, **write the model's likely action line** (a `Thought:` plus either `Action: calc(...)` or `Final Answer: ...`).
> 2.  **Parse it exactly as your code would**: which branch fires, the `Final Answer:` check or the `calc(...)` regex?
> 3.  **Write the observation** your program would compute and append to memory.
> 4.  **Repeat** from step 1 with the updated memory until the trace reaches `Final Answer:`.

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

def chat(messages, temperature=0.7):
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature}
        }, timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[agentloop:chat] {e}")
        import traceback; traceback.print_exc()
        return ""

print("Environment ready.")
```

---

# Part I: The Sense-Think-Act Cycle

In this part, you will build a mental model of how agents perceive their environment, reason about it, and act, and why this cycle repeats rather than stopping after one exchange.  Understanding this cycle is what separates a bare chatbot from a true agent.

## 1.  From Reaction to Agency

Before we look at the code, consider a search-and-rescue dog.  The dog perceives the environment (smells, sounds), plans where to move next, acts by running toward a scent, then perceives again based on what it finds.  It does not stop after one sniff; it loops until it either finds the target or its handler calls it back.  AI agents work the same way, but instead of a physical environment they navigate text, tool outputs, and their own prior reasoning.

A bare language model call is a pure function of its prompt.  It has no goal that persists beyond one response and no way to affect the world.  The agent loop adds three things: **state** (memory, a running record of everything the agent has seen and said so far), a **goal** (a condition for being done), and **actions** (things the agent can do besides talk).

$$
\text{while not done: } o_t \leftarrow \text{perceive}(); \quad a_t \leftarrow \pi(o_t, m_t); \quad m_{t+1} \leftarrow \text{update}(m_t, o_t, a_t)
$$

Here $o_t$ is the observation at step $t$, $m_t$ is memory, $\pi$ is the policy implemented by the language model, and $a_t$ is the chosen action.  The loop terminates when the agent emits a distinguished *final answer* action or exceeds a step budget.

> **One caution to carry all term.**  The loop is worth building when the next step genuinely depends on what came back from the last one, and it is pure overhead when it does not.  A task with a fixed sequence of steps is a script; a task whose rule you can state is a function; a task with thousands of labeled examples and a small fixed answer set is usually a classifier.  Each of those is faster, cheaper, and always right, which a loop around a language model is not.  We build the loop today because you cannot judge when to reach for it until you know exactly what it costs, and *Design First* comes back to that judgment with a decision table once you do.

### Pseudocode

```
function AGENT(goal):
    memory = [goal]
    for step in 1..MAX_STEPS:
        thought = LLM(memory)            # think
        action = parse(thought)          # decide
        if action is FINAL_ANSWER:
            return action.content
        observation = execute(action)    # act on the world
        append thought, observation to memory
    return "step budget exceeded"
```

The step budget matters: without it, an agent that never satisfies its goal loops forever, consuming resources.  Bounded autonomy is a design principle we revisit in the governance unit.

---

## 2.  The ReAct Pattern

Think of ReAct (Reason + Act) as giving the agent a scratch pad.  Before taking any action, the agent writes down what it is thinking, just like you might jot notes before making a decision.  That written reasoning then becomes part of the context for the next step, so the agent builds on its own work rather than starting fresh each time.

**ReAct** interleaves explicit reasoning text with actions (Yao et al., 2023).  The model is prompted to emit structured steps:

```
Thought: I need today's weather before recommending an activity.
Action: get_weather("Collegeville, PA")
Observation: 54 degrees, light rain
Thought: Rain rules out the hike. An indoor option is better.
Final Answer: Visit the Berman Museum this afternoon.
```

**Why does writing out thoughts help?**  The model's reasoning becomes part of its own context (the text it can see), so each step conditions on an explicit plan rather than an implicit one.  The transcript also gives *us* a trace to audit, our first encounter with explainability.

In the ReAct pattern, the *Observation* lines are produced by:

[( )] The language model, as part of its generated text
[(X)] The surrounding program, which executes the action and inserts the real result
[( )] The human user at each step
[( )] A second language model acting as a judge

---

# Part II: Building the Loop

In this part, you will read and run a real agent loop in Python, about 20 lines that implement the perceive-plan-act cycle from Part I. Pay attention to where each piece of the loop lives in the code: you will be asked to identify them by name.

## 3.  A Minimal Tool-Using Agent

We give the model exactly one tool (a calculator) and parse its output for an action.  Notice how small the scaffolding is: the "agent" is mostly a prompt, a parser, and a loop.  The model never actually runs arithmetic; it asks the surrounding program to do it and then reads back the result.

---

## Code Cell

> **Run after the install session:** trace this on paper today; execute it after the *Running Your Own AI* install session.

```python
import re

SYSTEM = """You are an agent that solves problems step by step.
You may use the tool calc(expression) to evaluate arithmetic.
Respond in this exact format:
Thought: <your reasoning>
Action: calc(<expression>) OR Final Answer: <answer>"""

def run_agent(goal, max_steps=5):
    memory = [{"role": "system", "content": SYSTEM},
              {"role": "user", "content": goal}]
    for step in range(max_steps):
        out = chat(memory, temperature=0.0)
        print(f"--- step {step} ---\n{out}\n")
        if "Final Answer:" in out:
            return out.split("Final Answer:")[-1].strip()
        m = re.search(r"calc\((.+?)\)", out)
        if m:
            try:
                obs = str(eval(m.group(1), {"__builtins__": {}}))  # classroom-only sandbox
            except Exception as e:
                obs = f"error: {e}"
            memory.append({"role": "assistant", "content": out})
            memory.append({"role": "user", "content": f"Observation: {obs}"})
    return "step budget exceeded"

print(run_agent("A 4-credit course meets 100 minutes twice weekly for 14 weeks. How many hours of class time is that?"))
```

---

## Model: Trace Analysis

Run (or examine the projected run of) the agent above as a team.  Pay attention not just to the final answer but to the full printed trace: the agent's thoughts, its tool calls, and the observations that come back.

### Critical Thinking Questions

1.  Identify each component of the agent loop in the code: where does the agent *perceive*, *plan*, *act*, and *remember*?

   > *Hint: "Perceive" happens when the agent reads something new.  "Plan" happens when the language model generates text.  "Act" happens when the code calls `eval`.  "Remember" happens when something is appended to `memory`.*

2.  Notice the one setting we changed: `temperature=0.0` in `run_agent`, where the helper's default was `0.7`.  As the Key Concepts table says, **temperature near 0 makes the model repeat itself**: the same input produces very nearly the same output every run.  Higher values let its wording vary.

   Given only that, why would you want the repeatable setting *inside a loop*, when a chatbot answering one question might be better off varying?  Answer in terms of what the surrounding program has to do with the model's text.

   > *Hint: Your code does not read the model's answer the way a person does; it searches for the exact strings `Final Answer:` and `calc(...)`.  What happens to that search if the wording drifts between runs?  And if step 2's output is garbled, what does step 3 build on?*

3.  The `eval` call is sandboxed but still risky.  List two ways a confused or adversarial model output could cause harm here, and one mitigation for each.

   > *Hint: Think about what `eval` can do in Python even with `__builtins__` restricted.  Also think about what the model might put inside `calc(...)` if it is confused about the tool's purpose.*

4.  What happens to the conversation `memory` list as steps accumulate?  Predict a specific problem this causes for long-running agents.  (We name this problem in the *Memory and the Small Context Window Principle* activity.)

   > *Hint: Language models can only read a fixed amount of text at once, their "context window."  What happens when `memory` grows beyond that limit?*

> **Common Misconception:** It is tempting to think the language model is "running" the calculator or browsing the web.  It is not.  The model only produces text that looks like a tool call (for example, `calc(2 + 2)`).  The surrounding Python code detects that text, runs the real operation, and feeds the result back as an Observation.  The model never executes code directly; it just asks, and the program does.  This distinction matters enormously for security and for understanding what agents can and cannot do on their own.

---

## 3b.  From Scratch: Driving the Loop Yourself

We build the *minimal* tool-using agent together above.  The **from-scratch version** (you own the loop, the tool registry, and the message list, driving the OpenWebUI API directly) moved to the **[Local Agent lab](https://www.billmongan.com/Ursinus-CS357/Assignments/LocalAgent)**, where you build it for credit.

Doing it twice in one session was the crunch; doing it once here and once for real in the lab is the same learning with room to breathe.

# Part III: Synthesis and Practice

In this part, you will extend and stress-test the agent you just built (changing its budget, designing new tools, and deliberately breaking it), so that you understand not just how it works when it succeeds, but why it fails when it does.

## 4.  Exercises

1.  *Budget experiment.*

   - *What to do*: Lower `max_steps` to 1 and then 2.  Record at which budget the agent fails on the given problem, and explain why multi-step problems require multi-step budgets.
   - *Starter hint*: The course-hours problem requires at least two multiplications plus unit conversion.  How many `calc(...)` calls does the agent actually make in a successful run?  That number is your minimum budget.
   - *You've succeeded when*: You can state the minimum step budget for this problem with evidence from the trace, and you can explain in one sentence why the budget cannot be set to 1 without changing the problem.

2.  *Second tool.*

   - *What to do*: Design (on paper) a `today()` tool that returns the current date as a string.  Write the one or two lines of parser change needed and the additions to the system prompt that advertise this tool to the model.
   - *Starter hint*: Look at how `calc(...)` is advertised in `SYSTEM` and parsed with `re.search`.  Your `today()` tool takes no arguments, so the regex is simpler.  The system prompt line might read: "You may also use today() to get the current date."
   - *You've succeeded when*: You can show (on paper or in code) the system prompt addition, the regex that would detect `today()`, and the one line of Python that computes the result.

3.  *Failure hunt.*

   - *What to do*: Craft a goal (a question or task) that causes the agent to loop without terminating, or that produces a confidently wrong final answer.  The Recorder documents the full trace; the Presenter explains the failure mode to the class.
   - *Starter hint*: Try goals involving ambiguous units (miles versus kilometers), questions with no arithmetic component that confuse the agent into calling `calc()` anyway, or goals that require more than five steps.
   - *You've succeeded when*: Your team can name the specific failure mode (step budget exceeded, wrong tool call, confused parse, hallucinated number) and propose one targeted fix.

4.  *Spectrum revisited.*

   - *What to do*: Place this calculator agent on the agency spectrum from the *Welcome: What Is AI, and What Is an Agent?* activity, and justify the placement relative to the thermostat and the campsite-finder.
   - *Starter hint*: Consider: how many steps does it take autonomously?  Does it use tools?  Can it recover from an error observation?  Compare those answers to the thermostat (one fixed rule) and the campsite-finder (many steps, many tools, external web).
   - *You've succeeded when*: Your placement is backed by at least two specific features of the agent's behavior that distinguish it from both the thermostat and the campsite-finder.

---

## Reflection Prompt

*Personal*: The agent's "thoughts" are text we asked it to produce by putting instructions in the system prompt.  Do you consider this reasoning, a record of reasoning, or a performance of reasoning?  Did your view change after seeing the traces?  Describe the moment, if any, where the trace surprised you.

*Technical*: The agent today had one tool and a five-step budget.  If you were extending it to handle a homework question that required both arithmetic and a web search for a current statistic, what would you add?  Describe the new tool, the updated system prompt, and any new failure modes you would expect.

*Societal*: The step budget is a form of bounded autonomy; we deliberately limit how far the agent can go without human oversight.  Where else in society do we apply bounded autonomy to powerful systems (think aviation, medicine, financial trading)?  What does it cost us, and what does it protect?

---

-> Coming Up Next: You traced this loop on paper because none of it runs on your machine yet.  That changes next session: in *Your AI Workbench* we build the bench, install a model server, and hand a real coding agent a real task, so that from then on every activity is something you can run rather than read.  Bring a laptop with Docker Desktop already installed.

## 5.  Further Reading

- Shunyu Yao et al. "ReAct: Synergizing Reasoning and Acting in Language Models."  *ICLR* (2023).  The pattern implemented today.
- Melanie Mitchell.  *AI: A Guide for Thinking Humans*, Chapter 2.
