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
|------|---------------|
| Manager | Keeps the team on pace; calls time on each question |
| Recorder | Writes the team's consensus answers and posts to the board |
| Presenter | Speaks for the team during whole-class debrief |
| Reflector | Notes where the team was uncertain or disagreed; reports to whole class |

---

## Model 1: Four Loop Architectures

These are not mutually exclusive. Production systems often layer them: an outer ReAct loop with periodic Reflexion passes and Tree-of-Thought for particularly ambiguous steps.

| Pattern | Core Idea | When to Use | Primary Failure Mode |
|---------|-----------|-------------|---------------------|
| **Simple Loop** | Act → observe → repeat until done signal | Short, well-defined tasks; known termination | Infinite loop if done signal never fires |
| **ReAct** (Yao et al., 2022) | Interleave `Thought:` and `Action:` tokens in the context window before every action | Tasks requiring multi-step reasoning over tool outputs | Context window fills before task completes |
| **Reflexion** (Shinn et al., 2023) | After each episode, agent critiques its own trajectory and stores a verbal "lesson" in episodic memory | Tasks with clear success/failure signal; iterative improvement | Critique adds tokens; poor self-assessment yields bad lessons |
| **Tree-of-Thought** (Yao et al., 2023) | Branch $k$ candidate next steps; evaluate each with a scoring LLM call; expand the best branch | Tasks where early choices are hard to reverse; planning problems | $k \times$ token cost per step; slow |

**The inner loop vs. the outer loop:** The *inner loop* is the LLM generating tokens for one completion — deterministic given temperature. The *outer loop* is the agent choosing actions, calling tools, and updating its context — stochastic and long-running. Most failures occur in the outer loop, but most compute cost is in the inner loop.

### Critical Thinking Questions

1. A ReAct agent is solving a ten-step research task. Each step adds approximately 800 tokens to the context (thought + action + observation). The model has a 32,000-token context window. At what step does the agent risk running out of context? What options does the agent have at that point?

2. The Reflexion pattern stores lessons in episodic memory between runs. What is the difference between a lesson stored in memory and a change to the agent's system prompt? When would you prefer each approach?

3. Tree-of-Thought evaluates $k$ branches at each step using an LLM judge. If $k = 3$ and the task has 5 steps, how many total LLM calls does the agent make in the worst case (all branches evaluated at every step)? Compare this to a simple loop with the same 5 steps.

---

## Model 2: A ReAct Trace — Five Steps in Detail

The task: *"Find the three most-cited papers on transformer self-attention published before 2020 and list their citation counts."*

| Step | Thought | Action | Observation | Next Thought |
|------|---------|--------|-------------|--------------|
| 1 | The task asks for citation data. I should search Semantic Scholar, which has an API. | `search_papers(query="transformer self-attention", year_max=2019, limit=10)` | Returns 10 papers with titles and IDs but no citation counts | Citation counts require a separate lookup per paper ID. I have 10 IDs. I will look up the top 3 by title heuristic first. |
| 2 | "Attention Is All You Need" (2017) is almost certainly the most cited. Look it up. | `get_paper_citations(paper_id="204e3073870fae3d05bcbc2f6a8e263d9b72e776")` | 97,432 citations | That is the most cited. Now retrieve "BERT: Pre-training of Deep Bidirectional Transformers…" |
| 3 | BERT is transformer-based and pre-2020. Retrieve its citation count. | `get_paper_citations(paper_id="df2b0e26d0599ce3e70df8a9da02e51594e0e992")` | 51,618 citations | Two found. Need a third. The search returned "Universal Language Model Fine-Tuning (ULMFiT)" — check it. |
| 4 | ULMFiT is 2018 and transformer-adjacent. Checking. | `get_paper_citations(paper_id="1e077413b25c4d68cd0a8e6e8e42fcc50c85db7a")` | 4,441 citations | The third result. Now I have three papers and counts. I can compile the answer. |
| 5 | I have all data needed. No more tool calls required. Composing final answer. | *(No tool call — final answer generation)* | — | Done. |

Observe that at step 1 the agent decides it needs two separate API calls rather than assuming one call returns everything. At step 5, the agent recognizes termination because it has satisfied all sub-goals, not because it hit a step limit.

### Critical Thinking Questions

4. At step 3, the agent chose the third paper by heuristic ("ULMFiT is transformer-adjacent"). A more rigorous approach would fetch citation counts for all 10 papers from step 1. What is the tradeoff between the heuristic approach (steps saved) and the exhaustive approach (accuracy)?

5. Rewrite step 4 assuming the API call fails with a timeout error. What should appear in the "Next Thought" column? Write the thought the agent should produce to handle this gracefully without abandoning the task.

6. This trace shows the agent terminating because it self-assessed completion. Identify two ways the task could have been specified differently (in the original prompt) that would make termination detection more reliable, without relying on the agent's self-assessment.

---

## Model 3: Loop Safety Controls

Even a well-architected loop can fail. These controls are not optional — they are the engineering equivalent of a circuit breaker.

| Control | Implementation | What It Prevents |
|---------|---------------|-----------------|
| **Max iterations** | `if step >= MAX_STEPS: return partial_result` | Infinite loops; runaway API cost |
| **Token budget check** | Before each LLM call, check `tokens_used + estimated_tokens < context_limit` | Context overflow and truncation mid-reasoning |
| **Idempotency check** | `if (action, args) in seen_actions: skip or reflect` | Oscillation — agent alternating between two actions indefinitely |
| **Confidence threshold** | `if agent.confidence < THRESHOLD: escalate_to_human()` | Agent acting on a guess when it should ask for clarification |
| **Human escalation gate** | `if action.is_irreversible() and uncertainty > 0.3: pause()` | Irreversible harm from a low-confidence decision |
| **Checkpointing** | `state.save(step, context, memory)` after each action | Lost progress on long tasks after crashes or timeouts |

**Idempotency and oscillation** deserve a closer look. An agent oscillates when it alternates between two actions: `search("climate data")` → finds nothing new → `refine_query("climate data 2024")` → finds nothing new → `search("climate data")` again. The idempotency check stores a hash of `(action_name, args)` and flags repetition.

**Checkpointing** allows a loop to resume after failure. The checkpoint stores the full context window, the tool call history, and any external state (files written, IDs retrieved). On restart, the agent replays from the last checkpoint rather than from zero. This is especially important for tasks that take hours or involve expensive API calls.

### Critical Thinking Questions

7. The idempotency check compares `(action, args)` hashes. An agent calls `search("transformer attention mechanisms")` at step 2, gets 5 results, calls other tools, and then at step 8 calls `search("transformer attention mechanisms")` again hoping for updated results. Is this a true oscillation or a legitimate re-query? How would you modify the idempotency check to allow legitimate re-queries while still catching true oscillation?

8. A checkpointed agent resumes at step 7 after a crash. Steps 1–6 included writing a file to a cloud storage bucket. When the agent resumes, should it re-verify that the file exists, or trust the checkpoint? Argue for one approach.

9. The "token budget check" estimates the next call's token cost before making it. Why is estimation necessary rather than just letting the API call fail if the context is too long? (Hint: think about what happens to the reasoning in the context window when truncation occurs mid-thought.)

---

## Model 4: Termination — How Does an Agent Know It Is Done?

This is one of the hardest problems in agent design. There are three approaches:

**Explicit stop condition:** The task specification includes a machine-checkable success criterion. Example: *"Return when you have found exactly 3 papers and each has a citation count above 1,000."* The agent evaluates the criterion, not itself.

**Self-assessed completion:** The agent generates a `DONE` token or calls a `finish()` tool when it believes the task is complete. This is the ReAct trace above. Risk: the agent may declare completion prematurely (hallucinating that it answered the question) or never (perfectionism spiral).

**Budget exhaustion:** The outer loop simply ends when a budget (steps, tokens, dollars, time) is consumed and returns whatever partial result exists. This is reliable but may return incomplete work.

Production systems typically combine all three: an explicit criterion when possible, self-assessment as the primary signal, and budget as a hard fallback. The key insight is that **"done" is a property of the task specification, not of the agent's internal state**.

### Critical Thinking Questions

10. An agent is tasked with *"Write a complete test suite for this Python module."* There is no explicit count. The agent writes 12 tests and declares itself done. How would you revise the task specification to give the agent a more checkable termination criterion without over-specifying the solution?

11. A "perfectionism spiral" occurs when an agent keeps improving its output without stopping. Describe the observable signature of this failure in the ReAct trace format (what would `Thought:` entries look like across five steps), and state which safety control from Model 3 breaks the cycle.

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

**Exercise A — Trace Extension:** Extend the Model 2 ReAct trace to handle the case where the Semantic Scholar API is rate-limited at step 2 (returns HTTP 429). Add steps 2b and 2c showing the agent's Thought, Action, and Observation for waiting and retrying, and update the Next Thought at step 2 to reflect this.

**Exercise B — Oscillation Detector:** Write a Python function `is_oscillating(history, window=6)` that takes a list of `(action_name, args_hash)` tuples and returns `True` if any `(action, args)` pair appears more than once in the last `window` entries.

**Exercise C — Reflexion Design:** An agent fails three times at the task *"Find the arXiv ID for the original BERT paper."* Its trajectories are: (1) searched Google, got wrong paper; (2) searched Semantic Scholar by title, found it but missed the arXiv ID in the metadata; (3) searched arXiv directly, correct. Write the Reflexion "lesson" the agent should store after trajectory 3 — a single concise sentence that would prevent failures 1 and 2 in future runs of the same class of task.

---

## Reflection Prompt

*(Respond individually in your course notebook after class.)*

Every safety control in Model 3 has a cost: max iterations can cut a task short; idempotency checks can block legitimate re-queries; human escalation gates slow the agent down. Reflect on how you would calibrate these controls for two very different agents: (1) an agent that automates literature review for a research paper (high stakes, slow, user has time to review), and (2) an agent that responds to customer support tickets in real time (low stakes per ticket, must be fast). Which controls would you tighten, which would you loosen, and why?

---

## Further Reading

- [ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)
- [Reflexion: Language Agents with Verbal Reinforcement Learning (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366)
- [Tree of Thoughts: Deliberate Problem Solving with Large Language Models (Yao et al., 2023)](https://arxiv.org/abs/2305.10601)
- [Cognitive Architectures for Language Agents — Survey (Sumers et al., 2023)](https://arxiv.org/abs/2309.02427)
- [The Agent Loop (Anthropic Blog)](https://www.anthropic.com/research/building-effective-agents)
