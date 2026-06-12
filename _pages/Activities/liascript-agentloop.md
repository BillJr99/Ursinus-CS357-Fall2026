# The Agent Loop: Perceive, Plan, Act
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-agentloop.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentloop.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Agent Loop: Perceive, Plan, Act

This module develops the **agent loop**, the control structure that turns a reactive language model into a goal-directed system. We move from **intuition $\rightarrow$ the sense-think-act cycle $\rightarrow$ the ReAct pattern $\rightarrow$ a working agent loop in Python** against a local Ollama model.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## 0. Environment and Utilities

This section assumes Ollama is running locally (we install it together next class; today your instructor's machine serves the room). The only dependency is `requests`.

---

## Code Cell

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

## 1. From Reaction to Agency

**A bare LLM call is a pure function of its prompt.** It has no goal that persists beyond one response and no way to affect the world. The agent loop adds three things: **state** (memory of what has happened), a **goal** (a condition for being done), and **actions** (things the agent can do besides talk).

$$
\text{while not done: } o_t \leftarrow \text{perceive}(); \quad a_t \leftarrow \pi(o_t, m_t); \quad m_{t+1} \leftarrow \text{update}(m_t, o_t, a_t)
$$

Here $o_t$ is the observation at step $t$, $m_t$ is memory, $\pi$ is the policy implemented by the LLM, and $a_t$ is the chosen action. The loop terminates when the agent emits a distinguished *final answer* action or exceeds a step budget.

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

The step budget matters: without it, an agent that never satisfies its goal loops forever, consuming resources. Bounded autonomy is a design principle we revisit in the governance unit.

---

## 2. The ReAct Pattern

**ReAct (Reason + Act)** interleaves explicit reasoning text with actions (Yao et al., 2023). The model is prompted to emit structured steps:

```
Thought: I need today's weather before recommending an activity.
Action: get_weather("Collegeville, PA")
Observation: 54 degrees, light rain
Thought: Rain rules out the hike. An indoor option is better.
Final Answer: Visit the Berman Museum this afternoon.
```

**Why does writing out thoughts help?** The model's reasoning becomes part of its own context, so each step conditions on an explicit plan rather than an implicit one. The transcript also gives *us* a trace to audit, our first encounter with explainability.

[[MC]]
In the ReAct pattern, the *Observation* lines are produced by:
- ( ) The language model, as part of its generated text
- (x) The surrounding program, which executes the action and inserts the real result
- ( ) The human user at each step
- ( ) A second language model acting as a judge

---

# Part II: Building the Loop

## 3. A Minimal Tool-Using Agent

We give the model exactly one tool, a calculator, and parse its output for an action. Notice how small the scaffolding is: the "agent" is mostly a prompt, a parser, and a loop.

---

## Code Cell

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

Run (or examine the projected run of) the agent above as a team.

### Critical Thinking Questions

1. Identify each component of the agent loop in the code: where does the agent *perceive*, *plan*, *act*, and *remember*?
2. We set `temperature=0.0` for the agent's reasoning. Why might determinism matter more inside a loop than in open conversation?
3. The `eval` call is sandboxed but still risky. List two ways a malicious or confused model output could cause harm here, and one mitigation for each.
4. What happens to the conversation `memory` as steps accumulate? Predict a problem this causes for long-running agents. (We name this problem in week 6.)

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Budget experiment.* Lower `max_steps` to 1 and 2. Report at what budget the agent fails, and explain why multi-step problems require multi-step budgets.
2. *Second tool.* Design (on paper) a `today()` tool returning the date. Write the one or two lines of parser and prompt changes needed, and explain how the system prompt advertises a tool to the model.
3. *Failure hunt.* Craft a goal that makes the agent loop without terminating or produce a wrong final answer. The Recorder documents the trace; the Presenter explains the failure mode to the class.
4. *Spectrum revisited.* Place this calculator agent on last class's agency spectrum, and justify the placement relative to the thermostat and the campsite-finder.

---

## Reflection Prompt

In your notebook: the agent's "thoughts" are text we asked it to produce. Do you consider this reasoning, a record of reasoning, or a performance of reasoning? What evidence from today's traces supports your view?

---

## 5. Further Reading

- Shunyu Yao et al. "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR* (2023). The pattern implemented today.
- Stuart Russell and Peter Norvig. *Artificial Intelligence: A Modern Approach* (4th ed.), Chapter 2. Agent architectures from simple reflex to utility-based.
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 2.
