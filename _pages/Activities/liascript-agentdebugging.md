<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-agentdebugging.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Debugging AI Agents: What Went Wrong and How to Find Out

CS357 - Foundations of Artificial Intelligence / Agentic AI | Ursinus College

---

## POGIL Roles

This activity uses the **POGIL** (Process Oriented Guided Inquiry Learning) structure.  Assign one role to each group member before beginning.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the group on task, monitors time, ensures everyone contributes, and moves the group to the next question when ready |
| **Recorder** | Writes down the group's agreed answers and keeps a record of key decisions and reasoning |
| **Spokesperson** | Presents the group's answers during class discussion and asks the instructor clarifying questions on behalf of the group |
| **Reflector** | Monitors group process, notes what is working and what is not, and leads the end-of-activity reflection |

> Rotate roles across activities so everyone practices each one.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Non-determinism** | The property of an AI system where the same input can produce different outputs on different runs, making bugs difficult to reproduce reliably | An agent gives a rude response on Tuesday but behaves perfectly when you test the same prompt on Wednesday |
| **Prompt Bisection** | A binary-search debugging technique: replay the first half of a conversation to see if the bug appears; if not, try the second half; repeat until you find the smallest context that triggers the failure | Narrowing down a 40-turn conversation to the single turn at turn 22 where the agent first started giving wrong answers |
| **Hallucination** | When an AI model generates confident-sounding text that is factually wrong or made up, often triggered when the model lacks the information needed to answer correctly | An agent that cannot retrieve the current weather returns a confident but fabricated forecast instead of admitting failure |
| **Context Overflow** | When a conversation exceeds the model's context window length, causing the model to lose access to earlier instructions, tool outputs, or conversation history | An agent that follows its system prompt perfectly for 30 turns but "forgets" its formatting rules by turn 60 |
| **Persona Drift** | The gradual shift in an agent's behavior away from its system prompt instructions as the conversation history accumulates and earlier instructions become relatively less influential | An agent instructed to be concise that starts giving long answers after many turns of conversation with a user who prefers verbose responses |
| **Observability Platform** | A tool such as LangSmith or Langfuse that captures detailed traces of every LLM call and tool invocation in an agent run, enabling post-hoc inspection of exactly what happened | Using LangSmith to see that the agent received a valid weather API response but then generated text saying it couldn't retrieve the data |

---

In this first model, you will identify why AI agent bugs are qualitatively harder to debug than conventional software bugs, and why strategies that work for Python programs often fail for agents.  This matters because you cannot fix what you cannot reproduce, and agents have five specific properties that make reproduction difficult.

## Model 1: Why Agent Debugging Is Hard

Debugging a non-deterministic system is like diagnosing a car that only breaks down on Tuesdays: by the time you get it to the mechanic, it's running fine, and reproducing the problem requires recreating an exact combination of conditions you may not fully know.  AI agents are harder to debug than traditional software for five distinct and compounding reasons.  Understanding these reasons is the first step to building agents that are debuggable in the first place.

### Five Reasons Agent Debugging Is Hard

1.  **Non-determinism.**  The same input can produce different outputs on different runs because of sampling temperature, different random seeds, or variability in external tool responses.  A bug you cannot reproduce reliably is a bug you cannot confidently fix; you do not know whether your fix eliminated the bug or just got lucky on the next few runs.

2.  **Long causal chains.**  In a multi-step agent, the error you observe at step 12 may have been caused by a subtly wrong decision at step 6.  The visible symptom is far removed in time and context from the actual root cause, unlike a stack trace that points directly to the failing line of code.

3.  **Black-box model internals.**  You cannot set a breakpoint inside a neural network.  The model's "reasoning" is only visible through its output text, and that output text may not accurately reflect the internal computation that produced it.  A model can generate confident-sounding text that bears little relationship to any interpretable internal state.

4.  **Context sensitivity.**  A bug may appear only when the conversation history exceeds a certain length, or only when a specific tool output was present three turns earlier.  A bug that requires 50 prior turns of specific conversation to reproduce is nearly impossible to catch in standard unit tests.

5.  **Emergent failures.**  Each individual component (the model, each tool, and the orchestration logic) may behave correctly when tested in isolation, but the combination of all three produces a wrong or harmful outcome.  The bug is in the interaction between components, not in any single part.

### Classic Software Bug vs. Agent Bug

| Category | Classic Software Example | Agent Analog | How You Would Debug Each |
|----------|-------------------------|--------------|--------------------------|
| **Logic error** | A function returns the wrong calculation because of an incorrect formula | The model draws an incorrect inference from context that is technically accurate but misinterpreted | Trace the model's reasoning chain in its output; examine which facts the model cited and whether it cited them correctly |
| **State corruption** | A global variable is mutated by two concurrent threads, leaving it in an unexpected state | A prior tool output corrupts the model's subsequent interpretation of context | Log tool outputs immediately before and after they are inserted into the context window; compare expected vs. actual context |
| **Off-by-one** | A loop runs one extra iteration, processing one more item than intended | The model miscounts items in a list that appears in context | Test with lists of varying lengths; look for length-dependent failure patterns |
| **Missing case** | An unhandled null input causes the function to crash with an unhandled exception | An unhandled tool failure causes the model to hallucinate a plausible-sounding result rather than reporting the error | Insert deliberate tool failures in testing; check whether the model's recovery behavior is correct or confabulated |
| **Race condition** | Two processes write to the same file simultaneously, corrupting the data | Two agent branches produce conflicting context updates that are both inserted into the prompt | Review concurrency controls in the orchestration layer; serialize context writes; test with parallel branches |

### Critical Thinking Questions

**Question 1.**  Why can't you simply add `print()` statements to debug an LLM? What is the LLM's equivalent of a "variable's value," and why is it inaccessible in the way that a Python variable's value is accessible in conventional code?

[[___ Your answer here ___]]

> *Hint:* In a traditional program, a variable holds a specific value at each point in execution: you can print it, inspect it in a debugger, and reason about how it got there.  An LLM's "state" is distributed across billions of floating-point weights that encode statistical patterns learned from training data.  There is no variable that holds "what the model is currently thinking."  The only observable output is the token probability distribution, and even that is only partially informative about why the model generated a specific output.  If you can't inspect internal state, what can you observe?  What logs and outputs are available, and what can you infer from them?

---

**Question 2.**  A user reports: "Sometimes the agent is rude, but I can't reproduce it."  What is the minimum set of information you need before you can begin investigating?  List at least four specific pieces of information and explain why each is necessary for your investigation.

[[___ Your answer here ___]]

> *Hint:* Think about everything that could differ between the run that produced rudeness and the run you would try to reproduce it with: the exact text of the system prompt (including its version); the model name and version (model providers update models silently); the temperature and any other sampling parameters; the full conversation history including the exact text of every user and assistant turn; any tool call inputs and outputs; the exact timestamp (in case a tool's data source changed over time).  Without each of these, you cannot know whether a different reproduction attempt is testing the same conditions or different ones.

---

**Question 3.**  What is the difference between a bug in the *prompt* and a bug in the *code surrounding the prompt*?  Give a concrete example of each.  Why does the distinction matter for how you fix it and how you test the fix?

[[___ Your answer here ___]]

> *Hint:* A prompt bug is an error in the text instructions given to the model: for example, a system prompt that says "always respond in Spanish" when it should say "always respond in the user's language," or a tool description that incorrectly describes the format of the tool's output.  A code bug is an error in the Python (or other language) code that constructs the prompt, calls the model, parses the response, or invokes tools: for example, a bug that accidentally truncates the system prompt when the conversation history is long, or a bug that passes tool results in the wrong format.  The distinction matters because fixing a prompt bug requires no code deployment; fixing a code bug does.  Testing a prompt fix requires running the model; testing a code fix can sometimes be done with unit tests that mock the model.

---

*Model 1 showed why agent bugs are hard to find.  Model 2 gives you a structured five-stage process for finding them systematically, the equivalent of a debugger and stack trace for a system that has neither.*

## Model 2: A Systematic Debugging Process for Agents

Agent debugging benefits enormously from a structured approach.  Without structure, debugging a non-deterministic, multi-step system becomes an unguided search through an enormous space of possible causes.  The following five-stage process adapts classic software debugging methodology to the agent context.  Think of it as the agent equivalent of the scientific method: observe, isolate, hypothesize, test, fix.

**Stage 1: Reproduce.**  Capture the complete execution context so you can run the exact same scenario again.  This means logging: the system prompt text and a version hash of it; the model name and exact version string; the temperature and all other sampling parameters; the full conversation history including every user message, assistant message, tool call, and tool result; and timestamps for each turn.  "It worked on my machine" is especially dangerous with agents because any difference in model version, system prompt, or tool response can cause completely different behavior.

**Stage 2: Isolate.**  Use **prompt bisection** (a binary-search technique applied to conversation history) to find the turn where behavior first diverged from correct.  Binary-search through the conversation history: does the bug appear if you replay only the first half of the conversation?  If not, the bug is in the second half.  If yes, the bug is in the first half.  Repeat until you identify the minimal context that reliably produces the failure.  For a 64-turn conversation, this takes at most log₂(64) = 6 bisection steps in the worst case, the same efficiency as binary search in a sorted list.

**Stage 3: Hypothesize.**  Generate a specific, testable hypothesis.  Common failure mode categories to consider first:

- **Context overflow:** The conversation exceeded the model's context window, causing the model to lose access to earlier instructions or facts.
- **Tool failure mistaken as success:** The tool returned an error code or malformed output that the model interpreted as a valid result and acted on incorrectly.
- **Hallucination triggered by low-confidence state:** The model lacked information it needed and generated a plausible-sounding but incorrect answer rather than admitting uncertainty.
- **Persona drift:** Accumulated conversation history caused the model to gradually shift away from its system prompt persona and instructions.

**Stage 4: Test the hypothesis.**  Design a minimal test that either confirms or refutes your specific hypothesis.  If you hypothesize context overflow, replay the scenario with a truncated history and see if the bug disappears.  If you hypothesize tool failure, inject a synthetic tool failure and observe whether the model's response matches the failure pattern you saw.

**Stage 5: Fix and regression-test.**  After fixing the root cause, write a test case that would have caught the bug before the fix was applied.  Add it to your regression test suite.  Verify that the fix resolves the bug without breaking other agent behaviors.

> **Common Misconception:** Many developers try to fix agent bugs by tweaking the prompt slightly and running the agent a few times to see if the bug disappears.  If the bug is non-deterministic, this approach is unreliable; the bug may appear to be fixed when it has actually just not triggered randomly.  The systematic five-stage process above forces you to confirm a specific, testable hypothesis before declaring the bug fixed, which is the only way to have confidence that your fix actually addresses the root cause.

### Critical Thinking Questions

**Question 4.**  A user's agent starts giving unhelpful, off-topic answers beginning around turn 35 of a long conversation.  Describe step-by-step how you would use prompt bisection to find the exact turn where behavior diverged.  How many bisection steps would you need in the worst case if the conversation has 64 turns total?

[[___ Your answer here ___]]

> *Hint:* Start by replaying turns 1 through 32 and checking whether the behavior is correct at the end.  If correct at turn 32, the bug is in turns 33-64; replay turns 33-48.  If still correct, the bug is in turns 49-64; replay turns 49-56.  Continue halving the range.  For a 64-turn conversation, log₂(64) = 6 bisection steps are sufficient to identify the single turn that introduces the failure.  At each step, you need to actually run the model with exactly that prefix of the conversation and observe the output.  What are you looking for at each step: what does "correct behavior" mean at an intermediate turn, before the conversation has fully developed?

---

**Question 5.**  You need to build a logging system that makes agent failures reproducible.  However, your agent handles sensitive user data, so you cannot store raw conversation text in logs.  Describe a logging schema that captures enough information to reproduce failures without capturing any PII. For each field you log, explain what it enables you to diagnose.

[[___ Your answer here ___]]

> *Hint:* You can log: a SHA-256 hash of the system prompt (tells you which version was running without storing the text); the model name and version as a string (identifies the model behavior); temperature and other sampling parameters as structured JSON (enables non-determinism reproduction); tool call arguments in redacted form (if arguments contain PII, log a schema-level description or redacted version); tool response status codes and response length in tokens (distinguishes tool success from failure without storing content); token counts for prompt and completion from the API response (detects context overflow).  What you cannot log without PII risk: raw user messages, assistant responses containing user information, tool outputs that echo user data back.  How does losing this information affect your ability to debug certain categories of failures?

---

**Question 6.**  Your agent calls a weather tool.  The tool sometimes returns HTTP 503 (service unavailable).  Examining logs, you find that the agent sometimes correctly says "I was unable to retrieve current weather data" and sometimes gives a confident but fabricated forecast.  How would you distinguish "tool failure causing correct graceful degradation" from "tool failure causing hallucination" using only your logs?  What specific log fields would tell you which category a given incident belongs to?

[[___ Your answer here ___]]

> *Hint:* The critical question is: what did the model see in the context at the moment it generated the response?  Log: (1) the tool's HTTP status code and response body separately from the model's subsequent response; if the tool returned 503 but the model's response contains specific temperature and precipitation values, the model hallucinated because no valid data was available; (2) the exact text inserted into the context from the tool result; if it says "Error: service unavailable" but the model responded with a forecast, you know the model didn't follow the error signal; (3) the token count of the tool result: a 503 error response is typically short; a rich forecast is longer.  What would you see in your logs for the hallucination case vs. the graceful degradation case?

---

### Multiple Choice Question

An agent produces correct answers for 100 random test prompts but fails on one specific user's session that you cannot currently reproduce.  The most productive next step is:

[[ ]] Declare it an anomaly and move on; single-case failures are not statistically significant enough to investigate
[[ ]] Roll back to the previous model version immediately without investigating; you do not yet know whether the old version had the same bug
[[x]] Add logging to capture the full conversation context (system prompt version, conversation history, tool outputs, model version, and sampling parameters) so the next occurrence of the failure can be reproduced and investigated
[[ ]] Increase the model's temperature setting to introduce more variety and hope the failure disappears on its own; temperature controls randomness, not the source of this specific failure

> **Why this answer?**  A single unreproducible failure is the hardest category of agent bug to address, but the correct response is to instrument the system so the *next* occurrence can be reproduced.  Rolling back without understanding the cause leaves you unable to know whether the previous version also had the bug or a different one.  Adjusting temperature does not address any root cause and may introduce new non-deterministic failures.  Declaring it an anomaly is risky because a failure in an agent could affect safety, correctness, or user trust if it recurs at a higher rate than one observed case suggests.

---

*Models 1 and 2 gave you the conceptual framework for agent debugging.  Model 3 introduces the concrete tools that make that framework practical: observability platforms that capture traces, and logging schemas that make failures reproducible without storing sensitive user data.*

## Model 3: Tools and Techniques for Agent Debugging

### Observability Platforms

- **LangSmith** (LangChain): Captures full agent run traces with a hierarchical span structure for each LLM call and tool invocation.  Allows side-by-side comparison of runs that succeeded vs. failed on the same input.  Supports human annotation and user feedback collection on individual spans.

- **Langfuse:** Open-source alternative to LangSmith with self-hosting capability, making it appropriate for use cases where agent data cannot leave the operator's infrastructure.  Captures traces, supports prompt versioning that links each run to the exact prompt version that was active, and integrates with multiple agent frameworks.

- **Arize Phoenix:** Focuses on LLM evaluation and production drift detection.  Useful for identifying when a model's output distribution shifts over time: for example, detecting that the average length of agent responses has dropped, which might signal a model update or system prompt change.

**To use a trace viewer effectively:** identify the span where the model's output first diverges from expected; examine the exact prompt that was assembled and sent to the model (including all injected context); check the tool call inputs and outputs immediately preceding the divergence point; and compare token counts across turns to detect context overflow.

### Prompt Logging Best Practices

| What to Log | How to Log It | Why It Matters for Debugging |
|------------|---------------|------------------------------|
| Prompt hash | SHA-256 hash of the full prompt text | Identifies which prompt version is running without storing the full text, enabling correlation across runs |
| Model name and version | Log as an exact string from the API response | The same prompt can behave differently across model versions, especially after silent provider updates |
| Temperature and sampling parameters | Log as structured JSON with all fields | Enables reproduction of non-deterministic behavior |
| Tool call: input arguments | Log serialized tool arguments (redact PII fields) | Distinguishes "the model called the tool incorrectly" from "the tool received correct input but returned wrong output" |
| Tool call: output status code and body length | Log separately from the model's next response | If the tool returned HTTP 200 but the model said it failed, the issue is in the model's interpretation, not the tool |
| Token count for prompt and completion | Log from the API response metadata | The single most reliable detector of context overflow: when prompt tokens approach the model's context limit, earlier content is being dropped |

### Regression Testing for Agents

A **regression test** (a test that verifies a previously fixed bug has not come back) is especially valuable for agents because model updates can silently reintroduce behavior that was previously patched by a prompt change.  Agent regression test suites typically include three layers:

- **Golden output tests:** For deterministic behaviors (those that don't depend on model generation), assert that the output matches a known-good response exactly.  Example: assert that a tool routing decision correctly selects the weather tool for "what's the weather in Philadelphia?"
- **Output range tests:** For non-deterministic generated text, assert that the output contains required elements or avoids prohibited elements.  Example: "the response must include the word 'unavailable' when the tool returns a 503 error" or "the response must not include a specific temperature value when no weather data was retrieved."
- **Refusal assertion tests:** For safety-critical inputs, assert that the agent produces a refusal rather than a compliant response.  Example: "given a prompt requesting the agent to reveal its system prompt, the response must not contain the text of the system prompt."

Run the full regression suite on every prompt change, model upgrade, and tool schema change, not just on code changes.

### Critical Thinking Questions

**Question 7.**  What is a "prompt hash" and why would you log the SHA-256 hash of a prompt instead of the full prompt text?  What debugging information does the hash give you?  What information does it deny you?  Under what circumstances would you need to store the actual full prompt text?

[[___ Your answer here ___]]

> *Hint:* A SHA-256 hash is a fixed-length fingerprint of the prompt text: if two runs have the same hash, they used the exact same prompt; if the hashes differ, the prompts differ.  This tells you whether a behavioral difference between two runs is due to a prompt change or to model non-determinism.  What the hash cannot tell you: what the prompt said, which part of it changed, or how to fix a prompt bug.  You would need the actual prompt text when: (a) you are debugging a suspected prompt bug and need to read the text; (b) a run produced a harmful output and you need to audit exactly what instruction was active; or (c) you need to reproduce a run for a legal or compliance investigation.  Under what data retention policies is storing full prompt text acceptable?

---

**Question 8.**  Your agent's tool call log shows that the weather tool returned HTTP 200 with a syntactically valid JSON response containing temperature and precipitation data.  However, the model's next output says "I couldn't retrieve that information."  What does this tell you about where the failure occurred?  What specifically would you examine next to diagnose the root cause?

[[___ Your answer here ___]]

> *Hint:* The tool succeeded: it returned 200 with valid data.  The failure is in how that data was processed or presented to the model.  Possible locations: (1) the code that inserts the tool result into the context may be inserting it incorrectly: wrong format, wrong location in the prompt, or truncated; (2) the model may have received the data but interpreted the JSON in a way that made it look like an error (e.g., a null field for one value caused the model to generalize to "all data is unavailable"); (3) context overflow may have pushed the tool result out of the effective context window before the model generated its response.  Examine: the exact text of the tool result as it appeared in the assembled context (not just the raw API response), and the token count at that point in the conversation.

---

**Question 9.**  A support engineer needs to investigate complaint tickets about agent misbehavior.  The engineer should not have access to raw user conversation data for privacy reasons.  Design a specific 5-step debugging protocol the support engineer can follow using only the logged metadata (no raw user text).  Describe what information each step uses and what category of failure it rules out.

[[___ Your answer here ___]]

> *Hint:* Step 1: Check the model version and prompt hash for the failing session against the baseline from the same time period; rules out "something changed in the infrastructure" vs. "this is an edge case in normal operation."  Step 2: Check the token counts for each turn; rules out context overflow as a cause if all turns are well below the context limit.  Step 3: Check tool call status codes and response sizes; rules out tool failure if all tools returned 200 with non-trivial response sizes.  Step 4: Check the conversation turn count; rules out early-turn bugs if the failure occurred after many turns.  Step 5: Check whether the prompt hash matches known-bad prompt versions flagged in the incident log; rules out prompt regression.  After all five steps, what categories of failure remain uninvestigated, and what additional (non-PII) information could you request to narrow further?

---

*Models 1-3 gave you the framework, the process, and the tools.  The exercises below ask you to use all three on real agents: first by introducing and finding a bug yourself, then by designing the logging and testing infrastructure that would prevent the same bug from hiding in the future.*

## Exercises

**Exercise 1.**

*What to do:* Introduce an intentional bug into a simple agent you have built or will build for this exercise.  Debug the bug using only the agent's output and whatever logging you design, without reading the source code to find it directly.

*Starter hint:* Here is a concrete buggy agent scenario to replicate: Write a simple tool-using agent that looks up a city's population and answers questions about it.  Introduce this specific bug: the tool returns the population as a string ("Philadelphia: 1,600,000") but your code accidentally wraps the entire tool result in a JSON object as `{"result": "Philadelphia: 1,600,000"}` before inserting it into the context.  The model will see malformed context and may either hallucinate a number, report confusion, or silently misparse the result.  Now debug the problem using only the agent's outputs and your logs, without peeking at the code.  Document your bisection steps, your hypotheses, and how you confirmed the root cause.

*You've succeeded when:* Your write-up describes: the bug you introduced, the observable symptoms in the agent's output, the log evidence you used to form your hypothesis, and the confirmation step that proved the hypothesis correct before you looked at the code.

---

**Exercise 2.**

*What to do:* Design a logging schema for an agent that captures enough information to reproduce failures without storing raw user PII. Produce the schema as a JSON template.

*Starter hint:* Your JSON log entry should include at minimum: `session_id` (a random UUID, not linked to user identity), `turn_number`, `prompt_hash` (SHA-256), `model_version`, `temperature`, `tool_calls` (an array of objects with `tool_name`, `input_schema_version`, `status_code`, `response_token_count`), `prompt_token_count`, `completion_token_count`, and `timestamp_utc`.  For each field, note in a comment whether it poses any PII risk and how you handle it.

*You've succeeded when:* You have a complete JSON schema with all fields specified with their data types, a written explanation of what each field enables you to diagnose, and an explicit note for each field explaining whether it poses PII risk and how that risk is mitigated.

---

**Exercise 3.**

*What to do:* Choose a bug you encountered in any earlier lab or project in this course (it does not need to be an agent-specific bug).  Write a regression test that would have caught that bug before it was introduced, specific enough that someone else could run it without knowing what the original bug was.

*Starter hint:* A good regression test has three parts: (1) the specific input or setup that triggers the bug; (2) the specific assertion that checks for the correct behavior (not just "it doesn't crash" but "the output contains X" or "the function returns Y"); (3) a comment explaining what the bug was and why this test catches it.  For an agent bug, your test might assert something like: "when the weather tool returns HTTP 503, the agent's response must contain the substring 'unavailable' and must NOT contain any numerical temperature value."

*You've succeeded when:* Your regression test is self-contained enough that a classmate can run it without knowing what the original bug was, and the test would have FAILED before your bug fix and PASSES after it.

---

## Reflection Prompt

**Personal:** Think about a time when you were debugging a program or a system that was behaving unexpectedly.  What made the debugging process frustrating or satisfying?  How would the strategies in this activity have helped, and what aspects of AI agent debugging feel fundamentally different from that experience?

**Technical:** Most software bugs are deterministic: the same code path with the same input always produces the same wrong output, making bugs reproducible and fixable with confidence.  AI agent "bugs" can be stochastic: the same prompt fails 10% of the time and succeeds 90% of the time.  How does probabilistic failure change what we mean by "fixed"?  If a fix reduces a failure rate from 10% to 0.5%, is the bug fixed?  How would you communicate that to a user who experienced the failure?  How should your test suite handle a behavior that is correct 99.5% of the time but catastrophically wrong 0.5% of the time?

**Societal:** When a traditional software product has a critical bug, the company can issue a patch that replaces the buggy code with correct code, and the fix is complete.  When an AI agent "has a bug" that stems from how it was trained rather than from the surrounding code, the fix may require retraining the model, which costs millions of dollars and takes months.  What does this asymmetry imply for how AI agent developers should approach quality assurance before deployment?  Who bears the cost when a deployed AI agent causes harm due to a stochastic failure that passed all pre-deployment tests?

Write at least 200 words addressing at least two of the three levels above.  Please have your Reflector ready to share your group's key idea during class discussion.

[[___ Your reflection here ___]]

---

-> Coming Up Next: In the next activity, we examine synthetic data (using AI to generate training data for AI) and ask what happens when that feedback loop runs for many generations.

## Further Reading

- LangSmith documentation: https://docs.smith.langchain.com: Covers trace capture, evaluation, and prompt versioning for LangChain-based agents.

- Anthropic.  "Building Effective Agents" (2024).  Practical guidance on agent architecture, failure modes, and design patterns that reduce debugging complexity.

- Zinkevich, M. "Rules of Machine Learning: Best Practices for ML Engineering."  Google Research.  Rule 5 ("Test the infrastructure independently from the ML") and Rule 37 ("Measure training/serving skew") apply directly to agent debugging.

- Langfuse documentation: https://langfuse.com/docs: Open-source alternative to LangSmith with self-hosting options; useful reference for understanding what a full observability schema looks like.
