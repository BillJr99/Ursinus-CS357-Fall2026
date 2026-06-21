# Debugging AI Agents: What Went Wrong and How to Find Out

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentdebugging.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

## POGIL Roles

This activity uses the POGIL (Process Oriented Guided Inquiry Learning) structure. Assign one role to each group member before beginning.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the group on task, monitors time, ensures everyone contributes, moves the group to the next question when ready |
| **Recorder** | Writes down the group's agreed answers, keeps a record of key decisions and reasoning |
| **Spokesperson** | Presents the group's answers during class discussion, asks the instructor clarifying questions on behalf of the group |
| **Reflector** | Monitors group process, notes what is working and what is not, leads the end-of-activity reflection |

---

## Model 1: Why Agent Debugging Is Hard

Debugging a traditional software program is already difficult. Debugging an AI agent is harder in five distinct ways:

1. **Non-determinism.** The same input can produce different outputs on different runs (due to sampling temperature, random seeds, or external service variability). A bug you cannot reproduce reliably is a bug you cannot easily fix.

2. **Long causal chains.** In a multi-step agent, the error you observe at step 12 may have been caused by a wrong decision at step 6. The visible symptom is far removed from the root cause.

3. **Black-box model internals.** You cannot set a breakpoint inside a neural network. You have no access to the model's "reasoning" except through its output text — which may not accurately reflect internal processing.

4. **Context sensitivity.** A bug may appear only when the conversation history exceeds a certain length, or only when certain prior tool outputs are present. A bug that requires 50 prior turns to reproduce is nearly impossible to catch in unit tests.

5. **Emergent failures.** Each component (the model, each tool, the orchestration logic) may behave correctly in isolation, but the combination produces a wrong or harmful outcome. The bug is in the interaction, not in any single part.

### Classic Software Bug vs. Agent Bug

| Category | Classic Software Example | Agent Analog | How You Would Debug Each |
|----------|-------------------------|--------------|--------------------------|
| **Logic error** | Function returns wrong calculation | Model draws incorrect inference from correct context | Trace the reasoning chain; examine which facts the model cited |
| **State corruption** | Global variable mutated by two threads | Prior tool output corrupts subsequent model interpretation | Log tool outputs before and after insertion into context |
| **Off-by-one** | Loop runs one extra iteration | Model miscounts items in a list in context | Test with lists of varying lengths; look for length-dependent failure |
| **Missing case** | Unhandled null input crashes function | Unhandled tool failure causes model to confabulate result | Insert deliberate tool failures in testing; check model's recovery behavior |
| **Race condition** | Two processes write to file simultaneously | Two agent branches produce conflicting context updates | Review concurrency controls in orchestration; serialize context writes |

### Critical Thinking Questions

**Question 1.** Why can't you simply add `print()` statements to debug an LLM? What is the LLM's "internal state" equivalent, and why is it inaccessible in the way that a variable's value is accessible in conventional code?

[[___ Your answer here ___]]

**Question 2.** A user reports "sometimes the agent is rude, but I can't reproduce it." What is the minimum set of information you need before you can begin investigating? List at least four pieces of information and explain why each is necessary.

[[___ Your answer here ___]]

**Question 3.** What is the difference between a bug in the prompt and a bug in the code surrounding the prompt? Give a concrete example of each. Why does the distinction matter for how you fix it?

[[___ Your answer here ___]]

---

## Model 2: A Systematic Debugging Process for Agents

Agent debugging benefits from a structured approach. The following five-stage process adapts classic software debugging methodology to the agent context.

**Stage 1 — Reproduce.** Capture the complete execution context so you can run the same scenario again. This means: system prompt text and version hash, model name and version, temperature and other sampling parameters, full conversation history including all tool calls and their outputs, and timestamps. "It worked on my machine" is especially dangerous with agents because any difference in model version, system prompt, or tool response can change behavior unpredictably.

**Stage 2 — Isolate.** Use **prompt bisection** to find the turn where behavior diverged from correct. Binary-search through the conversation: does the bug appear if you replay only the first half of the conversation? If not, it is in the second half. Repeat until you identify the minimal context that produces the bug.

**Stage 3 — Hypothesize.** Generate a specific, testable hypothesis. Common failure mode categories:

- **Context overflow:** The conversation exceeded the model's context window, causing earlier instructions to be forgotten.
- **Tool failure mistaken for model failure:** The tool returned an error that the model silently handled incorrectly.
- **Hallucination triggered by low-confidence state:** The model lacked information and invented a plausible-sounding but incorrect answer.
- **Persona drift:** Accumulated conversation history caused the model to gradually shift away from its system prompt instructions.

**Stage 4 — Test the hypothesis.** Design a minimal test that confirms or refutes your hypothesis. If you think it is context overflow, replay the scenario with a truncated history. If you think it is tool failure, inject a synthetic tool failure and observe the response.

**Stage 5 — Fix and regression-test.** After fixing, write a test case that would have caught the bug before the fix. Add it to your test suite. Verify that the fix does not break other behaviors.

### Critical Thinking Questions

**Question 4.** A user's agent starts giving unhelpful answers beginning at turn 35 of a conversation. Describe step-by-step how you would use prompt bisection to find the turn where behavior diverged. How many bisection steps would you need in the worst case?

[[___ Your answer here ___]]

**Question 5.** You need to build a logging system that makes failures reproducible. However, the agent handles sensitive user data, so you cannot store raw conversation text. Describe a logging schema that captures enough information to reproduce failures without capturing PII. What do you log? What do you deliberately omit or hash?

[[___ Your answer here ___]]

**Question 6.** Your agent calls a weather tool. The tool sometimes returns HTTP 503 (service unavailable). The agent's output sometimes says "I was unable to retrieve current weather data" (correct behavior) and sometimes gives a confident but fabricated forecast (incorrect behavior). How would you distinguish "tool failure causing correct graceful degradation" from "tool failure causing hallucination" in your logs? What would you look for?

[[___ Your answer here ___]]

### Check Your Understanding

An agent produces a correct answer for 100 random test prompts but fails on one specific user's session that you cannot reproduce. The most productive next step is:

- ( ) Declare it an anomaly and move on — single-case failures are not statistically significant
- ( ) Roll back to the previous model version immediately
- (x) Add logging to capture the full conversation context (system prompt, history, tool outputs, model version) so the next occurrence can be reproduced and investigated
- ( ) Increase the model temperature to introduce more variety and hope the failure disappears

---

## Model 3: Tools and Techniques for Agent Debugging

Several specialized tools and practices have emerged to support agent debugging at scale.

### Observability Platforms

- **LangSmith** (LangChain): Captures full agent run traces with spans for each LLM call and tool invocation. Allows side-by-side comparison of runs that succeeded vs. failed. Supports annotation and human feedback collection.

- **Langfuse:** Open-source alternative to LangSmith. Captures traces, supports prompt versioning, and integrates with multiple frameworks. Can be self-hosted to avoid sending data to a third party.

- **Arize Phoenix:** Focuses on LLM evaluation and drift detection in production. Useful for identifying when a model's behavior changes over time.

To use a trace viewer effectively: identify the span where the model's output diverges from expected, examine the exact prompt that was sent (including injected context), check the tool call inputs and outputs immediately preceding the divergence, and compare token counts to detect context overflow.

### Prompt Logging Best Practices

| What to Log | How | Why |
|------------|-----|-----|
| Prompt hash | SHA-256 of prompt text | Identifies which prompt version is running without storing the full text |
| Model name + version | Log as string | Same prompt behaves differently across model versions |
| Temperature + sampling params | Log as structured JSON | Reproduces non-determinism |
| Tool call: input | Log serialized tool arguments | Distinguishes model error from tool error |
| Tool call: output + status code | Log separately from model response | If tool returns 200 but model says it failed, you know the issue is the model's interpretation |
| Token count (prompt + completion) | Log from API response | Detects context overflow |

### Regression Testing for Agents

Once you fix a bug, codify it as a test case. Agent test suites typically include:

- **Golden output tests:** For deterministic behaviors, assert the output matches a known-good response exactly.
- **Output range tests:** For non-deterministic behaviors, assert the output contains required elements (e.g., "must mention the deadline", "must not include a price").
- **Refusal assertion tests:** Assert that safety-relevant inputs produce refusals, not compliant responses.

Run this test suite on every prompt change, model upgrade, and tool schema change.

### Critical Thinking Questions

**Question 7.** What is a "prompt hash" and why would you log it instead of the full prompt text? What information does it give you? What information does it deny you? Under what circumstances would you need to store the actual prompt text?

[[___ Your answer here ___]]

**Question 8.** Your agent's tool call log shows that the weather tool returned HTTP 200 with valid JSON. However, the model's next output says "I couldn't retrieve that information." What does this imply about where the failure occurred? What would you examine next to confirm?

[[___ Your answer here ___]]

**Question 9.** A support engineer needs to investigate agent complaint tickets. They should not have access to raw user conversation data. Design a 5-step debugging protocol they can follow using only logs (no raw user text). What information does each step use, and what does it rule out?

[[___ Your answer here ___]]

---

## Exercises

**Exercise 1.** Introduce an intentional bug into a simple agent you have built or can build for this exercise. Options: use a wrong tool schema (mismatched parameter type), insert context that overflows near the limit, or write a system prompt that conflicts with a user instruction. Debug the bug using only the agent's output and whatever logs you design. Document the steps you took, what you hypothesized, and how you confirmed the root cause.

**Exercise 2.** Design a logging schema for an agent that captures enough information to reproduce failures without storing raw user PII. Specify: the exact fields you log, their data types, which fields you hash vs. truncate vs. omit, and what a single log entry looks like as JSON. Explain the tradeoff between debugging utility and privacy for each field.

**Exercise 3.** Choose a bug you encountered in any earlier lab or project in this course (it does not need to be an agent bug). Write a regression test that would have caught that bug before it was introduced. The test should be specific enough that someone else could run it without knowing the original bug. Explain how the test detects the bug.

---

## Reflection Prompt

Most software bugs are deterministic — the same code path with the same input always produces the same wrong output. AI agent "bugs" can be stochastic — the same prompt fails 10% of the time and succeeds 90% of the time.

> **How does probabilistic failure change what we mean by "fixed"?** If a fix reduces the failure rate from 10% to 0.5%, is the bug fixed? How would you communicate this to a user who experienced the failure? How should your test suite handle a behavior that is correct 99.5% of the time but catastrophically wrong 0.5% of the time?

Write at least one paragraph responding to this prompt. Your Reflector should share your group's key idea during class discussion.

[[___ Your reflection here ___]]

---

## Further Reading

- LangSmith documentation: https://docs.smith.langchain.com — Covers trace capture, evaluation, and prompt versioning for LangChain-based agents.

- Anthropic. "Building Effective Agents" (2024). Practical guidance on agent architecture, failure modes, and design patterns that reduce debugging complexity.

- Zinkevich, M. "Rules of Machine Learning: Best Practices for ML Engineering." Google Research. Rule 5 ("Test the infrastructure independently from the ML") and Rule 37 ("Measure training/serving skew") apply directly to agent debugging.

- Langfuse documentation: https://langfuse.com/docs — Open-source alternative to LangSmith with self-hosting options; useful reference for understanding what a full observability schema looks like.
