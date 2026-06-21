# Advanced Agent Loops: Control Flow, Reflection, and Recovery
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-agentloopsadvanced.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentloopsadvanced.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Advanced Agent Loops: Control Flow, Reflection, and Recovery

In the first agent loop activity we established perceive → plan → act → observe. That works for simple, short-horizon tasks. Real deployments reveal failure modes that the basic loop cannot handle: **infinite oscillation**, **context overflow**, **catastrophic forgetting in long tasks**, and **the agent not knowing it is done**. Today we study four architectural patterns — ReAct, Reflexion, Tree-of-Thought, and checkpointing — and the engineering controls that make long-running agents reliable.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss as a team. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports disagreements or alternative interpretations. After class, respond to the reflective prompt individually in your notebook.

| Role | Responsibility |
|------|----------------|
| Manager | Keeps the team on pace; calls time on each question to maintain forward momentum. |
| Recorder | Writes the team's consensus answers in complete sentences and posts them to the discussion board. |
| Presenter | Speaks for the team during the whole-class debrief and represents any minority opinions the team noted. |
| Reflector | Notes where the team was uncertain or disagreed, and brings those unresolved questions to the whole class. |

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **ReAct** | A loop architecture where the agent alternates between writing a "Thought:" (its reasoning) and an "Action:" (a tool call or next step) in its context, making the reasoning process visible and inspectable. ReAct stands for Reasoning and Acting. | Step 1 of the trace: "Thought: The task asks for citation data. I should search Semantic Scholar." followed by an actual API call. |
| **Reflexion** | A pattern where after each attempt at a task, the agent critiques its own trajectory and stores a short "lesson" in memory, so future runs of the same class of task start with that accumulated wisdom. | After failing to find an arXiv ID via Google, the agent stores: "For arXiv IDs, search arXiv directly rather than Google." |
| **Tree-of-Thought** | A pattern where the agent generates several candidate next steps (a "tree" of possibilities), evaluates each with a scoring model call, and pursues only the most promising branch. | At each step, generate k=3 candidate actions, score each, pick the best — at a cost of 3× as many model calls. |
| **Context Window** | The total amount of text (measured in tokens) that a model can "see" at once. Every thought, action, and observation in a ReAct trace adds to this count, and once it fills up the agent cannot proceed without compressing or discarding earlier content. | A 32,000-token window fills after roughly 40 steps of 800 tokens each. |
| **Checkpointing** | Saving the agent's complete state (current step, context, memory, external actions taken) to disk periodically, so that if the agent crashes mid-task it can resume from the last checkpoint rather than starting over. | `state.save(step=7, context=..., files_written=[...])` after each action. |
| **Idempotency** | A property of an action meaning it produces the same result whether called once or multiple times. An idempotency check detects when an agent is about to repeat an action it already performed, which often signals oscillation. | Detecting that `search("climate data")` at step 8 is identical to the call at step 2, suggesting the agent is stuck. |

---

## Model 1: Four Loop Architectures

**Why this matters:** Self-correction makes agents far more reliable on real tasks. Think of a surgeon who, after each incision, checks the patient's vital signs before proceeding — this feedback loop catches problems before they cascade. ReAct gives agents the same property: by writing out reasoning before each action, the agent can catch its own mistakes mid-task rather than only at the end. Reflexion takes this further, letting agents learn from entire failed attempts. These patterns transform agents from one-shot guessers into iterative problem-solvers.

These patterns are not mutually exclusive. Production systems often layer them: an outer ReAct loop with periodic Reflexion passes and Tree-of-Thought for particularly ambiguous steps.

| Pattern | Core Idea | When to Use It | Primary Failure Mode |
|---------|-----------|----------------|----------------------|
| **Simple Loop** | Act once, observe the result, repeat until a "done" signal is received or a step limit is hit. | Short, well-defined tasks where you know termination will happen quickly and reliably. | Infinite loop if the done signal never fires — the agent runs forever and spends unbounded API budget. |
| **ReAct** (Yao et al., 2022) | Before every action, write a "Thought:" token that explains the reasoning; then write an "Action:" token; then observe the result. The reasoning appears in the context and can be inspected by humans. | Multi-step tasks that require reasoning over tool outputs, where you want the agent's logic to be auditable. | The context window fills before the task completes, truncating earlier reasoning and causing the agent to lose track of what it has already done. |
| **Reflexion** (Shinn et al., 2023) | After each complete attempt at a task, the agent writes a "lesson" critiquing its own trajectory and stores it in episodic memory. The next attempt starts with those lessons loaded. | Tasks with a clear success or failure signal that can be measured after the fact, and tasks you expect to run many times. | Each critique adds tokens to the context; if the agent's self-assessment is poor, it stores bad lessons that actively hurt future performance. |
| **Tree-of-Thought** (Yao et al., 2023) | At each step, branch into k candidate next actions, evaluate each with a separate scoring LLM call, and expand only the highest-scoring branch. | Tasks where early choices are hard to reverse and planning quality matters more than speed or cost. | Costs k × as many token calls per step compared to a simple loop; for k=3 and a 10-step task, this is 30 scoring calls in addition to the main calls. |

**The inner loop vs. the outer loop:** The *inner loop* is the LLM generating tokens for one completion — deterministic given temperature and seed. The *outer loop* is the agent choosing actions, calling tools, and updating its context — stochastic and long-running. Most failures occur in the outer loop, but most compute cost is in the inner loop.

### Critical Thinking Questions

1. A ReAct agent is solving a ten-step research task. Each step adds approximately 800 tokens to the context (thought + action + observation). The model has a 32,000-token context window. At what step does the agent risk running out of context? What options does the agent have at that point?

   > *Hint: Divide the window size by the tokens per step. Then think: if the agent must summarize earlier content to make room, what information is most important to preserve — the most recent steps, the earliest steps, or something else?*

2. The Reflexion pattern stores lessons in episodic memory between runs. What is the difference between a lesson stored in memory and a change to the agent's system prompt? When would you prefer each approach?

   > *Hint: A system prompt change affects every future run permanently. A memory entry affects runs until it is cleared or overridden. If you discover that your ResearchAgent repeatedly makes the same mistake, which mechanism is more appropriate, and what would make you choose differently?*

3. Tree-of-Thought evaluates k branches at each step using an LLM judge. If k = 3 and the task has 5 steps, how many total LLM calls does the agent make in the worst case (all branches evaluated at every step)? Compare this to a simple loop with the same 5 steps.

   > *Hint: At each step: 3 branches generated + 3 branches scored = 6 calls. Multiply by 5 steps. Now compare to 5 calls for a simple loop. When is this 6× overhead worth paying?*

---

## Model 2: A ReAct Trace — Five Steps in Detail

**Why this matters:** Reading an actual ReAct trace makes the abstract pattern concrete. Notice that the agent is not just calling tools at random — each "Thought:" entry reflects a real decision about what to do next based on what was observed. This is what makes ReAct traces valuable for debugging: you can inspect the reasoning at each step and identify exactly where the agent made a wrong assumption or missed an opportunity.

The task: *"Find the three most-cited papers on transformer self-attention published before 2020 and list their citation counts."*

| Step | Thought | Action | Observation | Next Thought |
|------|---------|--------|-------------|--------------|
| 1 | The task asks for citation data. I should search Semantic Scholar, which has an API for academic papers and returns citation counts. I will start with a broad search and filter by year. | `search_papers(query="transformer self-attention", year_max=2019, limit=10)` | Returns 10 papers with titles and Semantic Scholar IDs, but no citation counts are included in the search response. | Citation counts require a separate API call per paper ID. I have 10 IDs. I will look up the most likely candidates by title first rather than fetching all 10 counts. |
| 2 | "Attention Is All You Need" (Vaswani et al., 2017) is almost certainly the most-cited transformer paper. I will fetch its citation count first as a baseline. | `get_paper_citations(paper_id="204e3073870fae3d05bcbc2f6a8e263d9b72e776")` | Returns: 97,432 citations as of today's date. | That is the most-cited paper. Now I will fetch the BERT paper, which is also transformer-based and pre-2020. |
| 3 | BERT (Devlin et al., 2018) is a major transformer paper published before 2020. I will retrieve its citation count next. | `get_paper_citations(paper_id="df2b0e26d0599ce3e70df8a9da02e51594e0e992")` | Returns: 51,618 citations. | Two papers found with counts. I need a third. The search results include "Universal Language Model Fine-Tuning (ULMFiT)" by Howard and Ruder (2018) — I will check it. |
| 4 | ULMFiT is a 2018 NLP transfer learning paper that is transformer-adjacent. It appeared in the top 10 search results, making it a reasonable candidate for third most-cited. | `get_paper_citations(paper_id="1e077413b25c4d68cd0a8e6e8e42fcc50c85db7a")` | Returns: 4,441 citations. | I now have three papers with citation counts: 97,432; 51,618; 4,441. I can compile and return the final answer. All sub-goals are satisfied. |
| 5 | I have all data needed to answer the task. No more tool calls are required. The three papers are identified and their citation counts are verified from the API. | *(No tool call — generating final answer text)* | — | Task complete. Returning the three papers and their citation counts to the user. |

Observe that at step 1 the agent decides it needs two separate API calls rather than assuming one call returns everything. At step 5, the agent recognizes termination because it has satisfied all sub-goals — not because it hit a step limit.

### Critical Thinking Questions

4. At step 3, the agent chose the third candidate by heuristic ("ULMFiT appeared in the top 10 results"). A more rigorous approach would fetch citation counts for all 10 papers from step 1 and sort them. What is the tradeoff between the heuristic approach (fewer steps, less cost) and the exhaustive approach (guaranteed accuracy)?

   > *Hint: The heuristic gets to step 5 in 5 API calls. The exhaustive approach requires 10 API calls for citation lookups plus 1 search call = 11 calls. For this specific task, which would you choose, and what information would change your answer?*

5. Rewrite step 4 assuming the API call fails with a timeout error (HTTP 408). What should appear in the "Next Thought" column? Write the full Thought entry the agent should produce to handle this gracefully without abandoning the task or repeating a call that already timed out.

   > *Hint: The agent should (a) acknowledge the failure, (b) decide whether to retry or try a different approach, and (c) have a fallback plan. What would a good fallback be if the Semantic Scholar API is unavailable?*

6. This trace shows the agent terminating because it self-assessed completion at step 5. Identify two ways the task could have been specified differently in the original prompt that would make termination detection more reliable, without relying on the agent's judgment that it is "done."

   > *Hint: What machine-checkable criterion could be added to the task? For example, instead of "find three papers," what if the task specified a verifiable property each paper must have?*

> **⚠️ Common Misconception:** Students often assume that a ReAct trace is a log of what the model "really thought" — that the `Thought:` entries are genuine inner reasoning. They are not. The `Thought:` entries are generated text, just like the `Action:` entries. The model generates them because the ReAct prompt instructs it to, not because they reflect a separate internal deliberation process. This means a model can generate a confident-sounding `Thought:` entry that is factually wrong or that contradicts its own next step. ReAct traces are useful for debugging and auditing because they make the agent's reasoning *visible and checkable* — but visibility does not guarantee correctness. Always verify key claims in the thought entries against the observations they are based on.

Now that you have seen what a ReAct loop looks like step by step, the next model examines what can go wrong when such a loop runs unsupervised — and the engineering controls that prevent those failures.

---

## Model 3: Loop Safety Controls

In this section you will examine six concrete engineering controls that keep agent loops safe in production. Understanding these controls matters because even a loop that works perfectly in testing can spin out of control when deployed on real, messy inputs.

**Why this matters:** Even a well-designed ReAct loop can fail in ways that are expensive, embarrassing, or harmful. Safety controls are the engineering equivalent of a circuit breaker in an electrical system: they do not prevent all failures, but they prevent a small failure from cascading into a catastrophic one. Just as circuit breakers are not optional in buildings, these controls are not optional in production agent systems. Every agent that runs unsupervised in the real world needs at least a step limit and a human escalation gate.

Even a well-architected loop can fail. These controls are not optional — they are the engineering equivalent of a circuit breaker.

| Control | Implementation | What It Prevents |
|---------|----------------|------------------|
| **Max iterations** | `if step >= MAX_STEPS: return partial_result` — hard ceiling on the number of loop iterations, regardless of whether the agent thinks it is done. | Infinite loops and runaway API costs that could exhaust a budget in minutes. |
| **Token budget check** | Before each LLM call, check `tokens_used + estimated_next_tokens < context_limit` and compress context if not. | Context overflow and mid-thought truncation, which produces incoherent or dangerous reasoning. |
| **Idempotency check** | Maintain a set of `(action_name, args_hash)` pairs seen so far; if the current action matches a previous one, flag it as potential oscillation rather than executing it again. | Oscillation — agent alternating between two actions indefinitely, spending tokens and API budget without progress. |
| **Confidence threshold** | `if agent.confidence < THRESHOLD: escalate_to_human()` — if the agent rates its own certainty below a set level, pause and ask a human rather than proceeding on a guess. | Agent acting on a low-confidence guess when the cost of being wrong is high. |
| **Human escalation gate** | `if action.is_irreversible() and uncertainty > 0.3: pause_and_notify()` — before any write, delete, send, or purchase action with nontrivial uncertainty, stop and ask for human approval. | Irreversible harm from a low-confidence or misunderstood instruction. |
| **Checkpointing** | `state.save(step, context, memory, external_actions)` after each action completes — save the full state to disk or a database. | Lost progress on long tasks after crashes, timeouts, or infrastructure failures. |

**Idempotency and oscillation** deserve a closer look. An agent oscillates when it alternates between two actions: `search("climate data")` → finds nothing new → `refine_query("climate data 2024")` → finds nothing new → `search("climate data")` again. The idempotency check stores a hash of `(action_name, args)` and flags repetition.

**Checkpointing** allows a loop to resume after failure. The checkpoint stores the full context window, the tool call history, and any external state (files written, IDs retrieved). On restart, the agent replays from the last checkpoint rather than from zero. This is especially important for tasks that take hours or involve expensive API calls.

### Critical Thinking Questions

7. The idempotency check compares `(action, args)` hashes. An agent calls `search("transformer attention mechanisms")` at step 2, gets 5 results, calls other tools, and then at step 8 calls `search("transformer attention mechanisms")` again, hoping for updated results from the search index. Is this a true oscillation or a legitimate re-query? How would you modify the idempotency check to allow legitimate re-queries while still catching true oscillation?

   > *Hint: What distinguishes a legitimate re-query from an oscillation loop? Is it the time elapsed? The number of intervening actions? The agent's stated reason for repeating the call? Which of these can be checked programmatically?*

8. A checkpointed agent resumes at step 7 after a crash. Steps 1–6 included writing a file to a cloud storage bucket. When the agent resumes, should it re-verify that the file exists before proceeding, or should it trust the checkpoint's record of what was done? Construct the strongest argument for one approach.

   > *Hint: Consider two scenarios: (a) the file write succeeded and the crash happened after; (b) the file write appeared to succeed but silently failed due to a network issue. Which scenario is more dangerous to assume incorrectly, and does that change your answer?*

9. The "token budget check" estimates the next call's token cost before making it. Why is estimation necessary rather than just letting the API call fail if the context is too long?

   > *Hint: When a context window is exceeded, the API does not return a clean error — it silently truncates the input from the beginning of the context. If the truncation removes the task description or early reasoning steps, what happens to the quality of the agent's response? Is a truncated context more dangerous than a detected budget failure?*

---

## Model 4: Termination — How Does an Agent Know It Is Done?

In this section you will compare three ways of defining "done" for an agent, and you will practice revising task specifications to make termination more reliable. This connects directly back to the loop safety controls in Model 3: a clear stopping rule is what makes the max-iterations control meaningful.

**Why this matters:** "Being done" sounds obvious, but for an AI agent it is surprisingly hard to define. Unlike a traditional program that returns when a function exits, an agent is generating text in a loop and must decide for itself when to stop. Get this wrong in one direction and the agent quits too early with incomplete work; get it wrong in the other direction and you get the "perfectionism spiral" — an agent that keeps polishing indefinitely. Understanding the three approaches to termination lets you choose the right one for your task.

This is one of the hardest problems in agent design. There are three approaches:

**Explicit stop condition:** The task specification includes a machine-checkable success criterion. Example: *"Return when you have found exactly 3 papers and each has a citation count above 1,000."* The agent evaluates the criterion against the data it has collected — not against its own feeling of being done.

**Self-assessed completion:** The agent generates a `DONE` token or calls a `finish()` tool when it believes the task is complete. This is the approach used in the Model 2 trace. Risk: the agent may declare completion prematurely (hallucinating that it answered the question) or never (perfectionism spiral, where it keeps improving the answer without stopping).

**Budget exhaustion:** The outer loop simply ends when a budget (steps, tokens, dollars, or wall-clock time) is consumed and returns whatever partial result exists at that point. This approach is reliable and predictable, but may return incomplete work on complex tasks.

Production systems typically combine all three: an explicit criterion when possible, self-assessment as the primary signal, and budget exhaustion as a hard fallback. The key insight is that **"done" is a property of the task specification, not of the agent's internal state**.

### Critical Thinking Questions

10. An agent is tasked with *"Write a complete test suite for this Python module."* There is no explicit count of required tests. The agent writes 12 tests and declares itself done. How would you revise the task specification to give the agent a more checkable termination criterion without over-specifying the solution?

    > *Hint: What properties of a test suite can be verified automatically? Coverage percentage? Presence of tests for each public function? At least one edge case per function? Pick a criterion that is machine-checkable but does not dictate how the agent should write the tests.*

11. A "perfectionism spiral" occurs when an agent keeps improving its output without ever declaring completion. Describe the observable signature of this failure in the ReAct trace format — write out what the `Thought:` entries would look like across five consecutive steps — and state which specific safety control from Model 3 breaks the cycle.

    > *Hint: In a perfectionism spiral, each Thought will say something like "The draft is good, but it could be improved by..." even when the draft is already high quality. Which control imposes a hard ceiling on how long this can continue?*

---

## Multiple Choice Checkpoint

[[MC]]
A ReAct agent is on step 18 of a task. Its context window shows 28,000 of 32,000 tokens used. The agent decides to call a tool that typically returns a 6,000-token observation. What is the correct action before making this tool call?
- ( ) Make the tool call and let the API truncate the response automatically
- ( ) Immediately terminate the task and return the partial result
- (x) Summarize or compress earlier context to free token budget before making the tool call
- ( ) Switch to Tree-of-Thought because it uses fewer tokens

---

## Exercises

**Exercise A — Trace Extension**

*What to do:* Extend the Model 2 ReAct trace to handle the case where the Semantic Scholar API is rate-limited at step 2 (returns HTTP 429 Too Many Requests). Add steps 2b and 2c showing the agent's Thought, Action, and Observation for waiting and retrying, and update the Next Thought at step 2 to reflect the rate-limit scenario.

*Starter hint:*
```
Step 2b:
  Thought: The API returned HTTP 429, which means I am sending requests too fast.
           I should wait before retrying. The response header says "Retry-After: 5".
  Action: wait(seconds=5)   # or: skip to a different paper while waiting
  Observation: 5 seconds elapsed.
  Next Thought: I can now retry the original call.
```

*You've succeeded when:* Your extended trace handles the failure without abandoning the task, and the Next Thought entries at each step reflect genuine reasoning about the failure rather than just "try again."

**Exercise B — Oscillation Detector**

*What to do:* Write a Python function `is_oscillating(history, window=6)` that takes a list of `(action_name, args_hash)` tuples representing recent actions and returns `True` if any `(action, args)` pair appears more than once in the last `window` entries.

*Starter hint:*
```python
def is_oscillating(history, window=6):
    # Look only at the most recent `window` actions
    recent = history[-window:]  # slice the last `window` items
    # Count occurrences of each (action, args) pair
    from collections import Counter
    counts = Counter(recent)    # counts[(action, hash)] = number of times seen
    # If any pair appears more than once, we have oscillation
    return any(count > 1 for count in counts.values())

# Example usage:
history = [("search", "abc"), ("fetch", "def"), ("search", "abc")]
print(is_oscillating(history))  # should print True
```

*You've succeeded when:* Your function correctly returns `True` for a clear oscillation (same action twice in 6 steps) and `False` for a sequence where the same action appears at step 1 and step 9 (outside the window).

**Exercise C — Reflexion Lesson**

*What to do:* An agent fails three times at the task *"Find the arXiv ID for the original BERT paper."* The trajectories are: (1) searched Google, retrieved the wrong paper's ID; (2) searched Semantic Scholar by title, found the paper but missed the arXiv ID in the metadata field; (3) searched arXiv directly using the exact title, found the correct arXiv ID immediately. Write the Reflexion "lesson" the agent should store after trajectory 3 — a single concise sentence that would prevent both failures 1 and 2 if loaded at the start of a future run on any similar task.

*Starter hint:* A good Reflexion lesson is specific enough to be actionable but general enough to apply to a class of tasks. It should name the successful strategy, not just criticize the failed ones. Start with: "When searching for arXiv IDs, ..."

*You've succeeded when:* Your single-sentence lesson would cause the agent to go directly to arXiv search on the next run, avoiding both the Google detour (failure 1) and the Semantic Scholar metadata miss (failure 2).

---

## Reflection Prompt

Respond to all three levels in your notebook:

**Personal:** Every safety control in Model 3 has a cost: max iterations can cut a task short; idempotency checks can block legitimate re-queries; human escalation gates slow the agent down. Think about your own work habits. Do you tend to under-plan (diving in without enough reflection) or over-plan (getting stuck in analysis)? Which safety controls in Model 3 most resemble good habits you already have, and which feel like constraints you would struggle to enforce?

**Technical:** Reflect on how you would calibrate these controls for two very different agents: (1) an agent that automates literature review for a research paper (high stakes, slow task, user has time to review each output), and (2) an agent that responds to customer support tickets in real time (low stakes per ticket, must respond within seconds). For each agent, which controls would you tighten, which would you loosen, and what specific threshold values would you start with?

**Societal:** Long-running agents that operate autonomously raise questions about accountability. If an agent running for four hours takes an action that causes harm at hour three, who is responsible — the developer who set the step limit too high, the organization that deployed the agent, or the user who initiated the task? What legal and ethical frameworks would you want to exist before deploying an agent that runs unsupervised for hours?

---

→ **Coming Up Next:** The next activity covers *orchestration patterns* — how to compose multiple specialized agents into pipelines, routers, and planners, and how the lessons from loop safety apply when agents are handing off work to each other.

---

## Further Reading

- [ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)
- [Reflexion: Language Agents with Verbal Reinforcement Learning (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366)
- [Tree of Thoughts: Deliberate Problem Solving with Large Language Models (Yao et al., 2023)](https://arxiv.org/abs/2305.10601)
- [Cognitive Architectures for Language Agents — Survey (Sumers et al., 2023)](https://arxiv.org/abs/2309.02427)
- [The Agent Loop (Anthropic Blog)](https://www.anthropic.com/research/building-effective-agents)
