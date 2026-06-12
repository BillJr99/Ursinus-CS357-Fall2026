# Prompt Engineering as Agent Design: Personas and System Prompts
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-promptengineering.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-promptengineering.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Prompt Engineering as Agent Design: Personas and System Prompts

A prompt is not a question; it is a **program written in natural language** that configures an agent's behavior. This module moves from **anatomy of a prompt $\rightarrow$ core patterns $\rightarrow$ personas and system prompts $\rightarrow$ designing the policy of your own agent**, because in an agentic system the system prompt *is* the agent's job description.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Anatomy of a Prompt

## 1. Three Channels of Instruction

**Modern chat models receive layered instructions.** The **system prompt** establishes durable role, constraints, and format. The **user message** carries the immediate task. The **conversation history** carries everything either party has said. The model conditions on all three, but well-trained models weight the system prompt as standing policy:

$$
P(\text{response} \mid \text{system}, \text{history}, \text{user})
$$

**For an agent, the system prompt is the constitution.** It declares the agent's goal, its allowed actions, its output format, and its boundaries. When we built the calculator agent, two-thirds of the design lived in that one string.

---

## Model 1: Two Prompts, Two Agents

| Prompt A | Prompt B |
|----------|----------|
| "Tell me about photosynthesis." | "You are a patient biology tutor for first-year students. Use one everyday analogy, then a three-sentence technical explanation, then ask the student one check-for-understanding question. Topic: photosynthesis." |

### Critical Thinking Questions

1. List every behavioral commitment Prompt B makes that Prompt A leaves to chance.
2. Which prompt makes the output easier to *evaluate*? Why does specifying format make quality measurable?
3. Prompt B constrains tone and structure but not correctness. What would you add to push the model toward accuracy?
4. Rewrite Prompt B for a different audience (a graduate seminar, a fifth grader). Which elements changed and which were durable?

---

## 2. Core Prompting Patterns

The community has converged on a small set of reliable patterns, each of which we will reuse all semester. **Role and persona** assigns an identity and expertise frame. **Few-shot examples** show the desired input-output mapping rather than describing it. **Chain-of-thought** requests intermediate reasoning before the answer. **Output structuring** demands a machine-parseable format such as JSON, which is what allows a *program* to act on a model's response. **Constraints and refusals** state what the agent must not do.

A practical agent system prompt composes several patterns:

```
ROLE: who the agent is and for whom it works
GOAL: what done looks like
TOOLS: actions it may take, with exact syntax
FORMAT: the exact output schema
GUARDRAILS: what it must refuse or escalate to a human
```

[[MC]]
An agent must return JSON so that downstream code can parse its decision. The most reliable prompting approach is:
- ( ) Ask politely for JSON at the end of the user message
- ( ) Raise the temperature so the model explores formats
- (x) Specify the exact schema in the system prompt and include a few-shot example of a valid response
- ( ) Avoid mentioning JSON so the model is not confused

---

# Part II: Personas in Practice

## 3. Personas Shape Distributions, Not Souls

**A persona does not create knowledge; it reweights it.** Telling a model it is a cautious pharmacist shifts the distribution of its outputs toward hedged, safety-conscious language present in its training data. This is powerful and dangerous: a persona can also reweight toward confident-sounding error. Personas should therefore be paired with *epistemic instructions* such as "say so when you are unsure," and we will measure whether models obey them.

---

## Code Cell

```python
import requests

def chat(system, user, temperature=0.7, model="llama3.2"):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": temperature},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[promptengineering:chat] {e}")
        import traceback; traceback.print_exc()
        return ""

personas = {
    "tutor": "You are a patient tutor. Explain with one analogy, then ask one question.",
    "skeptic": "You are a careful fact-checker. State confidence (high/medium/low) for each claim.",
    "json_bot": 'Respond ONLY with JSON: {"answer": str, "confidence": "high|medium|low"}'
}

question = "Why is the sky blue?"
for name, system in personas.items():
    print(f"===== {name} =====")
    print(chat(system, question, temperature=0.3), "\n")
```

---

## Model 2: Persona Comparison

Run the cell (or examine projected outputs) and compare the three responses to the identical question.

### Critical Thinking Questions

5. Which differences across the three outputs are *formatting*, which are *tone*, and which (if any) are *substance*?
6. The `json_bot` output is the only one a program can reliably consume. Sketch the two lines of Python that would extract the confidence field, and identify what happens if the model adds a single word of preamble.
7. Design a persona that would be actively harmful for this question, and explain the mechanism of harm. (Keep it classroom-appropriate; the point is to reason about failure.)

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Job description.* Write the complete system prompt (ROLE, GOAL, TOOLS, FORMAT, GUARDRAILS) for an agent that helps students plan four-year course schedules. Trade prompts with another team and red-team theirs: find one input that breaks it.
2. *Few-shot lift.* Take a task where the bare model fails (for example, converting dates to ISO 8601 inside sentences) and show that two examples in the prompt fix it. Report before and after outputs.
3. *Persona audit.* Pick one persona from Model 2 and run the same factual question five times. Does the persona change the *facts* asserted, or only their presentation? Provide evidence.
4. *Guardrail test.* Add a refusal instruction to any persona, then attempt three circumventions. Record which succeed; we will revisit these results during the governance unit.

---

## Reflection Prompt

In your notebook: a system prompt is invisible to the end user of an agent. What obligations, if any, does a designer have to disclose the persona and guardrails an agent is operating under? Connect your answer to one experience you have had with a chatbot whose instructions you could not see.

---

## 5. Further Reading

- Anthropic and OpenAI prompt engineering guides (online). Practical pattern catalogs maintained by model vendors.
- Jason Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *NeurIPS* (2022).
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 3, on what models do and do not understand.
