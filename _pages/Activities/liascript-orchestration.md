<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-orchestration.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-orchestration.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Orchestration Patterns: Pipelines, Routers, and Planners

Unit 3 begins: with your design artifacts from the *Design First: Plan Before You Build* activity in hand, instead of making one agent smarter, we make **several simple agents cooperate**.  The enabling insight comes straight from the small context window principle of the *Memory and the Small Context Window Principle* activity: a model given one narrow job and a tiny prompt outperforms the same model juggling five jobs in a bloated prompt.  We move from **why decompose $\rightarrow$ the pipeline $\rightarrow$ the router $\rightarrow$ the planner $\rightarrow$ composing them in code $\rightarrow$ keeping the composed loop reliable**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Orchestrator** | An agent (or piece of code) whose job is to coordinate other agents: deciding what task to assign to whom, in what order, and how to combine their outputs. The orchestrator does not do the actual work; it manages the process. | A campus event system where the orchestrator assigns announcements to an ExtractAgent, then a DraftAgent, then a PolishAgent in sequence. |
| **Subagent** | A specialized agent that receives a narrow task from the orchestrator, completes it, and returns a result. The subagent typically knows nothing about the larger workflow; it just does its one job. | The PolishAgent, which only sees a draft announcement and returns a polished version; it does not know about the extraction or drafting steps. |
| **Pipeline** | An orchestration pattern where agents are arranged in a fixed sequence, each passing its output to the next. The sequence is determined before the pipeline runs and does not change based on what the agents produce. | extract -> draft -> polish for a digest email, with each stage seeing only its own input. |
| **Router** | An orchestration pattern where a classifier agent reads an input and decides which specialist agent should handle it. The router's only job is to classify; it does not do the work itself. | A help-desk router that classifies incoming tickets as "hardware", "software", or "accounts" and sends each ticket to the right specialist. |
| **Planner** | An orchestration pattern where a planning agent writes a step list for a task at runtime (because the steps cannot be determined in advance), worker agents execute the steps, and the planner revises the plan when workers report failures. | "Plan my study schedule for finals, adapting dynamically as I report which topics I have finished." |
| **Seam** | The boundary between two agents in an orchestration: the point where one agent's output becomes the next agent's input. Seams are the most common location of bugs in multi-agent systems, because small inconsistencies in format or content can compound across a pipeline. | The JSON structure that ResearchAgent produces must exactly match the structure WriterAgent expects; a missing field at this seam causes a silent bug. |

---

# Part I: Decomposition

## 1.  Three Foundational Patterns

**Why this matters:** Think of a restaurant kitchen.  The head chef does not cook every dish, take orders, and serve tables simultaneously.  Instead, the work is divided: servers take orders (routing), line cooks handle specific stations (specialized subagents), and the expediter coordinates the flow (orchestration).  This division works because each role has a narrow, well-defined job.  When the pasta cook knows nothing about the appetizer station, neither can interfere with the other, and both can focus completely on their job.  The same principle applies to agent orchestration: narrow roles, clear handoffs, and an orchestrator that manages the overall flow without doing the detail work.

**Pipeline (fixed sequence).**  Stage outputs feed stage inputs: extract $\rightarrow$ draft $\rightarrow$ polish.  Each stage has its own small system prompt and sees *only* what it needs.  Pipelines are predictable, debuggable (you can inspect any intermediate output), and cheap.  They are the right default when the workflow is known in advance.

**Router (one decision, then dispatch).**  A classifier agent reads the input and forwards it to one of several specialists: billing questions to the billing agent, technical questions to the tech agent.  The router's entire context is the input plus the menu of destinations, about as small as a context gets.  Reliability comes from constraining the router's output to a closed set of labels.

**Planner (dynamic decomposition).**  When the workflow is *not* known in advance, a planner agent writes a step list, worker agents execute steps, and the planner revises on failures.  Planners buy flexibility at the cost of predictability, so we bound them with step budgets, a technique covered in depth in the supplemental *Advanced Agent Loops: Control Flow, Reflection, and Recovery* activity, if you explored it.

A useful design heuristic follows: **choose the least dynamic pattern that solves the problem.**  Pipelines before routers, routers before planners, planners before free-roaming autonomy.

---

## Model 1: Match the Pattern

| Task | Best Pattern? |
|------|---------------|
| Every night, summarize the day's club announcements into one digest email draft. | ? |
| Triage incoming help-desk tickets to hardware, software, or accounts queues. | ? |
| "Plan my study schedule for finals, adapting if I fall behind on a topic." | ? |

### Critical Thinking Questions

1.  Assign a pattern (Pipeline, Router, or Planner) to each task and write a one-sentence justification for each choice that uses the heuristic stated above.

   > *Hint: For each task, ask: is the sequence of steps known before the task starts?  If yes, consider pipeline.  Is the task just a single classification decision?  If yes, consider router.  Does the workflow need to change based on what happens during execution?  If yes, consider planner.*

2.  For the triage task, the router sometimes invents a fourth category that is not in its allowed list.  Give two distinct fixes: one that changes only the system prompt, and one that changes only the surrounding Python code, with no changes to the prompt.

   > *Hint: The prompt fix should make the closed set explicit and unambiguous.  The code fix should intercept whatever label the model produces and force it into the valid set; this is already partially shown in the code below.  What is the difference between these two approaches in terms of reliability?*

3.  For the digest pipeline, name the intermediate artifact that passes between the Extract stage and the Draft stage, and explain how inspecting that artifact helps you localize a quality bug, contrasting this with debugging a single large prompt that does everything at once.

   > *Hint: If the final digest contains wrong information, with a pipeline you can check whether the problem is in the extracted facts (a bad Extract stage) or in how those facts were used to write the draft (a bad Draft stage).  With a single mega-prompt, how would you diagnose the same problem?*

---

# Part II: A Pipeline and Router in Code

## 2.  Small Agents, Explicit Seams

**Why this matters:** The code below shows the key property of well-designed orchestration: each agent's system prompt is one sentence long.  This is not laziness; it is the point.  A one-sentence context cannot distract the model with competing concerns.  Each agent does exactly one thing and returns a result.  The pipeline orchestrator then passes that result, without modification, to the next agent.  The seams between agents are where the data flows, and they are the most important thing to get right, because a small error at a seam (wrong JSON key, missing field, unexpected format) propagates silently through the rest of the pipeline.

You can run this code locally using `ollama run llama3.2` to start the model server, then run the script in a separate terminal:

```bash
# Start the local model server (do this once)
ollama run llama3.2

# In a second terminal, run your orchestration script
python orchestration.py
```

---

## Code Cell

The code below implements both a three-stage pipeline (extract -> draft -> polish) and a two-stage router (classify -> dispatch) using a local language model.  Read through the comments before running it; each comment explains a design choice you will be asked about in the questions that follow.

```python
import requests

def llm(system, user, temperature=0.0):
    """
    Call a locally running LLM via Ollama.
    system: the agent's role and constraints (kept short on purpose)
    user:   the actual input this agent should process
    temperature=0.0: deterministic output for predictable pipelines
    """
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": temperature, "seed": 42},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[orchestration:llm] {e}")
        import traceback; traceback.print_exc()
        return ""

# --- Pipeline: extract -> draft -> polish ---
# Each stage sees only what it needs; intermediate outputs are inspectable.

def digest_pipeline(raw_announcements):
    # Stage 1: Extract structured facts from raw text
    # Output: one line per event, in a predictable format
    facts = llm(
        "Extract every event as 'name | date | location', one per line. Output only the lines.",
        raw_announcements
    )
    # Stage 2: Draft a human-readable summary from the structured facts
    # Note: the draft stage never sees the raw announcements, only the extracted facts
    draft = llm(
        "Write a friendly 3-sentence digest of these events for students.",
        facts
    )
    # Stage 3: Polish for length and tone
    final = llm(
        "Edit for concision and warmth. Keep under 60 words.",
        draft
    )
    return facts, draft, final  # return all intermediates for inspection and debugging

raw = (
    "The chess club meets Thursday at 7 in Olin 107. "
    "Hawk Hacks is Saturday 10am in IDDC. Bring laptops! "
    "Ultimate frisbee pickup moved to Sunday 2pm on the quad."
)
facts, draft, final = digest_pipeline(raw)
print("EXTRACTED FACTS:\n", facts)
print("\nDRAFT:\n", draft)
print("\nFINAL DIGEST:\n", final)

# --- Router: classify input, then dispatch to the right specialist ---
# The router makes ONE decision; the specialist does the actual work.

SPECIALISTS = {
    "hardware": "You fix physical computer problems. Give exactly 2 concrete troubleshooting steps.",
    "software": "You fix application and software problems. Give exactly 2 concrete steps.",
    "accounts": "You handle login, password, and account access issues. Give exactly 2 concrete steps.",
}

def route(ticket):
    # Router: classify into exactly one of the allowed labels
    # The closed-set guard below handles cases where the model invents a new category
    label = llm(
        "Classify the ticket as exactly one word: hardware, software, or accounts. Output only that word.",
        ticket
    ).lower()
    # Guard: if the model returns something unexpected, default to "software"
    # This is a code-level fix; a prompt-level fix would say "output ONLY one of these three words"
    label = label if label in SPECIALISTS else "software"
    # Dispatch to the appropriate specialist
    response = llm(SPECIALISTS[label], ticket)
    return label, response

for ticket in [
    "My laptop screen flickers and goes completely black after five minutes.",
    "I cannot log into the campus portal after the password reset last night."
]:
    label, response = route(ticket)
    print(f"\n[Category: {label}]\nTicket: {ticket}\nResponse: {response}")
```

---

## Model 2: Reading the Seams

### Critical Thinking Questions

4.  Each `llm` call in the pipeline has a one-sentence system prompt and sees only its own immediate input.  Connect this design choice directly to the "lost in the middle" finding from the memory module, where models fail to use information that appears in the middle of a long context.

   > *Hint: If a single mega-prompt contained all three jobs (extract, draft, and polish) how long would it be?  Where in that context would the "polish for concision" instruction appear relative to the raw announcements?  What does the lost-in-the-middle finding predict about how well the model would follow that instruction?*

5.  The router guard `label if label in SPECIALISTS else "software"` makes a silent default decision when the model produces an unexpected label.  Argue for or against this silent default, and propose what a "louder" failure would look like and when you would prefer it.

   > *Hint: A silent default means the ticket gets routed to "software" even if it really belongs to "accounts"; no one is notified that the classification failed.  A louder failure would log the error, send an alert, or raise an exception.  When does silence protect the user experience, and when does it hide a bug?*

6.  The polish stage could introduce errors the extract stage never made: for example, changing "Thursday at 7" to "Friday at 7" while editing for concision.  Where in the pipeline would you insert a verification step, and which tool or pattern from earlier in the course would you reuse for it?

   > *Hint: Think about the critique-and-refine pattern.  Could you add a "verify" stage after "polish" that checks the final output against the extracted facts?  What would its one-sentence system prompt say?*

> **Common Misconception:** Many students assume that because a pipeline has multiple agents, it is inherently more reliable than a single agent.  This is not automatically true.  A pipeline can fail at any seam, and because each agent is working from the previous agent's output rather than the original input, errors can compound silently.  A pipeline is more *maintainable* and more *debuggable* than a mega-prompt, but only if you actually inspect the intermediate outputs.  Return all intermediates from your pipeline functions (as the code above does with `return facts, draft, final`) and check them.

According to the design heuristic developed today, a team should reach for a planner agent only when:

[( )] The task involves more than two steps
[( )] Maximum autonomy is a project goal
[(X)] The sequence of steps cannot be determined before runtime
[( )] The budget allows a larger model

---

# Part III: Synthesis and Practice

In this part you first fold in two reliability upgrades (reflection and recovery, summarized here from the supplemental *Advanced Agent Loops* activity) and then extend and evaluate the pipeline and router you built in Part II, designing the message format for a planner.  These exercises connect directly to Lab work, so the design decisions you make here carry forward.

## Model 3: Reflection and Recovery - Keeping Composed Loops Reliable

*(A two-model summary of material from the supplemental Advanced Agent Loops activity; see Going Deeper at the end if you want the full treatment.)*

**Why this matters:** Every orchestration you built today is still a loop, and loops fail in loop-shaped ways: they oscillate, overrun budgets, crash mid-task, and repeat the same mistake on every run.  Two upgrades address this.  The **reflection loop** (Reflexion, Shinn et al., 2023): after each *complete attempt* at a task, the agent critiques its own trajectory and stores a short "lesson" in memory ("for arXiv IDs, search arXiv directly rather than Google") and the next attempt starts with those lessons loaded.  It shines on tasks with a clear success/failure signal that you expect to run many times; its failure mode is that a poor self-critique stores a *bad* lesson that actively hurts future runs, and every lesson spends context tokens.  The **recovery/budget model**: even a well-architected loop needs circuit breakers, controls that keep a small failure from cascading:

| Control | One-line implementation | What it prevents |
|---------|------------------------|------------------|
| Max iterations | `if step >= MAX_STEPS: return partial_result`, a hard ceiling, whatever the agent "thinks" | Infinite loops and runaway spend |
| Token budget check | Estimate the next call's tokens; compress context if it will not fit | Silent front-truncation of the task mid-thought |
| Idempotency check | Flag any repeated `(action, args_hash)` pair as possible oscillation | Alternating between two actions forever |
| Escalation gate | Pause for a human before irreversible actions taken under uncertainty | Low-confidence irreversible harm |
| Checkpointing | Save full state after each action; on crash, resume, never restart | Lost progress on long or expensive tasks |

One compact loop wearing both upgrades:

```python
LESSONS = []                                      # reflection memory: survives across attempts

def attempt(task, max_steps=6):
    state = load_checkpoint(task) or fresh_state(task, lessons=LESSONS)
    seen = set()                                  # idempotency ledger
    for step in range(state.step, max_steps):     # budget: hard ceiling
        if not fits_in_context(state):
            state = compress(state)               # budget: summarize, never truncate silently
        action = plan_next(state)                 # the ordinary perceive/plan call
        if (action.name, action.args_hash) in seen:
            return escalate("oscillating", state) # recovery: flag it, do not spin
        seen.add((action.name, action.args_hash))
        if action.irreversible and state.uncertain:
            return escalate("needs approval", state)   # recovery: human gate
        state.observe(execute(action))
        save_checkpoint(task, state, step)        # recovery: crash-safe resume point
        if state.done:
            break
    LESSONS.append(critique(state.trajectory))    # reflection: store one lesson for next time
    return state.result
```

### Critical Thinking Questions

7.  Which of the five controls does the Part II *pipeline* barely need, and which does a dynamic *planner or supervisor* absolutely need?  Explain using the difference in who authors the control flow.

   > *Hint: the pipeline's step count is fixed at three by your code, so max-iterations is satisfied by construction, but a planner chooses its own next step every turn, so the ceiling, the idempotency ledger, and the escalation gate are the only things standing between it and an unbounded run.*

8.  The nightly digest pipeline mangles a date once a week.  Write the one-sentence Reflexion lesson you would want stored, and name the safeguard that prevents a bad lesson (say, "always skip the polish stage") from silently degrading every future run.

   > *Hint: a lesson should name the successful strategy, not just criticize the failure, and because lessons are generated by the same model that failed, they deserve the same review you give any seam: log them, cap how many load per run, and audit them when quality drifts.*

---

## 3.  Exercises

1.  **Add a fact-check stage to the pipeline.**

   *What to do:* Add a fourth stage to the `digest_pipeline` function, a `verify` stage that compares the final polished digest against the extracted facts and returns a JSON object indicating whether any facts in the digest are inconsistent with the extracted facts.  Then demonstrate it catching a seeded error by manually modifying the digest to introduce a wrong date before passing it to the verify stage.

   *Starter hint:*
   ```python
   def verify_stage(facts, final_digest):
       return llm(
           """You are a fact-checker. Compare the digest to the extracted facts.
           Return JSON: {"consistent": true/false, "issues": ["list any discrepancies"]}.
           Output only the JSON.""",
           f"Extracted facts:\n{facts}\n\nDigest to verify:\n{final_digest}",
           temperature=0.0  # deterministic: fact-checking should not vary
       )

   # Test with a seeded error: change "Thursday" to "Friday" in the final digest
   corrupted = final.replace("Thursday", "Friday")
   result = verify_stage(facts, corrupted)
   print("Verification result:", result)  # should report the date discrepancy
   ```

   *You've succeeded when:* Your verify stage correctly identifies the seeded date error and reports it in the issues list, and also correctly reports `"consistent": true` when the digest matches the facts.

2.  **Evaluate the router with a labeled test set.**

   *What to do:* Build a set of 12 help-desk tickets (4 hardware, 4 software, 4 accounts) where you know the correct category.  Run your router on all 12 and compute its classification accuracy.  Then deliberately degrade the router's prompt (remove the instruction that restricts output to one of three words) and re-measure accuracy.  Report the difference.

   *Starter hint:*
   ```python
   test_tickets = [
       ("My keyboard is not responding after I spilled water on it.", "hardware"),
       ("The application crashes every time I open the Reports tab.", "software"),
       ("My account was locked after three failed login attempts.", "accounts"),
       # ... add 9 more with known correct labels
   ]

   correct = 0
   for ticket_text, true_label in test_tickets:
       predicted_label, _ = route(ticket_text)
       if predicted_label == true_label:
           correct += 1
   accuracy = correct / len(test_tickets)
   print(f"Router accuracy: {accuracy:.0%}")
   ```

   *You've succeeded when:* You have a before-and-after accuracy number for both the constrained and unconstrained router, and you can explain in one sentence why adding the closed-set instruction (or the code-level guard) improved accuracy.

3.  **Design a planner message format.**

   > *Hint: Think about what the planner needs to know when a worker fails.  The planner must decide whether to retry the task, skip it, adjust the timeline, or ask the user for help, and it must make that decision based solely on what the failure report contains.  What fields would you need in the failure report to support all four of those decisions?*

   *What to do:* On paper, design the JSON message format for the planner-worker interaction in the study-schedule task from Model 1.  Your design must specify: (a) what the planner sends to a worker as a task assignment, (b) what a worker sends back to report success, and (c) what a worker sends back to report failure and what information the planner needs to revise the plan.  Write out three example messages in full.

   *Starter hint:*
   ```json
   // Planner -> Worker: task assignment
   {"task_id": "t1", "action": "study", "topic": "probability", "duration_minutes": 60, "deadline": "2026-12-10"}

   // Worker -> Planner: success report
   {"task_id": "t1", "status": "complete", "notes": "Covered chapters 4-6, comfortable with Bayes theorem"}

   // Worker -> Planner: failure report (what should go here?)
   {"task_id": "t1", "status": "blocked", "reason": "...", "suggestion": "..."}
   ```

   *You've succeeded when:* Your failure report format contains enough information for the planner to decide whether to reassign the task, adjust the timeline, or ask the user for clarification, without needing to ask the worker any follow-up questions.

---

## Reflection Prompt

Respond to all three levels in your notebook:

**Personal:** Decomposing a big task into narrow roles is also how effective study groups, sports teams, and workplaces operate.  Think of a team project (in this class or any other context) where unclear roles caused confusion or duplicated effort.  How does the pipeline/router/planner framework map onto what went wrong, and what would the "seam" between two team members look like in practice?

**Technical:** Describe one place in today's pipeline design where information lost at a seam could cause a poor outcome.  For example: if the polish stage changes a date while editing for concision, neither the extract stage nor the draft stage will catch it.  What is the technical mechanism (a validation step, a schema check, a logging requirement) that would detect this specific failure?

**Societal:** Decomposition into narrow roles is how both efficient organizations and surveillance systems work.  A pipeline of agents that each know only their own step can process sensitive data (a student's grades, a person's medical history) without any single agent "knowing" the full picture.  Is this a privacy protection or a way to obscure accountability?  Who is responsible when a pipeline of individually-compliant agents produces a harmful outcome?

---

-> **Coming Up Next:** *The Critique and Refine Pattern* activity is next: a specific pipeline where one agent generates content and a second agent evaluates it against explicit criteria, looping until the quality bar is met or a budget expires.

---

## Further Reading

- Anthropic engineering blog.  "Building Effective Agents" (2024, online).  The workflow patterns formalized today.
- Wu et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation."  (2023).
- Leon Festinger's classic organizational-communication literature, for the human analogy (optional browse).

---

# Going Deeper (at home): Fixed Pipelines vs. Dynamic Orchestration

> **The full advanced-loops activity:** Model 3 above compresses two models from [Advanced Agent Loops: Control Flow, Reflection, and Recovery](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-agentloopsadvanced.md), read that activity for the complete treatment: ReAct traces, Tree-of-Thought, checkpointing in depth, and termination design.

Everything below is **at-home material**: nothing in this section is needed for today's in-class session, but all of it deepens what you built in class.  Parts I-III gave you the vocabulary (pipeline, router, planner) and two working orchestrators in code.  This section steps back to the single decision that sits *above* all of them: **who decides the control flow, you, in advance, or a model, at runtime?**  Every orchestration you will ever build belongs to one of two families, and the choice between them is really a choice about predictability, cost, and how much open-endedness the task needs.  We move from **the two families $\rightarrow$ each fixed shape explained separately $\rightarrow$ the dynamic supervisor loop $\rightarrow$ a recap you can reach for on the job.**

---

## Model 4: Two Families of Orchestration

**Why this matters:** A fixed pipeline is a scheduled commuter train: the same stops, in the same order, every single day; you can print the timetable a year in advance.  Dynamic orchestration is a taxi driver who decides the route while driving, rerouting around traffic you could not have predicted.  The train is boring, cheap, and easy to audit: if a passenger ends up in the wrong place, you know exactly which segment failed.  The taxi is flexible and handles trips no timetable anticipated, but you cannot promise, before the trip starts, exactly which streets it will use.  Neither is "better."  They answer different questions.

**Family 1: Fixed (known) orchestration.**  *You*, the developer, wire a predetermined graph of agents.  The nodes and edges are decided before any input arrives; the control flow lives in your Python, not in a model's head.  The pipeline and router from Parts I-II are both of this family.  Its virtues are exactly the ones you already measured: predictability, step-by-step debuggability (inspect any intermediate output), and bounded cost (you can count the model calls before you run).

**Family 2: Dynamic orchestration.**  An orchestrator (often called a **supervisor**) is itself an LLM. You hand it the task plus a *roster* of available sub-agents, and each turn *it* decides which sub-agent to run, whether to spawn a fresh one for a newly-discovered subtask, or whether the work is done.  The control flow is now a model *output*, not your code.  Its virtues are the mirror image of Family 1: flexibility, open-endedness, and the ability to handle tasks whose shape you could not enumerate in advance.  Its costs are the same mirror: unpredictable paths, harder debugging (the "why did it do that?" lives in a prompt), and open-ended spend unless you cap it.

| | Fixed / known orchestration | Dynamic / supervisor orchestration |
|---|---|---|
| Who authors the control flow | The developer, before runtime | An orchestrator LLM, each turn |
| Path through the agents | The same every run (up to loops you bounded) | Chosen at runtime; may differ per input |
| Debugging story | Inspect the intermediate at each fixed seam | Read the supervisor's decisions in a trace |
| Cost | Countable before you run | Open-ended until you impose a budget |
| Best when | The workflow is known in advance | The workflow cannot be enumerated in advance |

This extends Part I's heuristic (**choose the least dynamic pattern that solves the problem**) one rung further: fixed families before dynamic ones, and a *bounded* dynamic supervisor before free-roaming autonomy.

---

## 4.  Fixed Pipelines, Explained Separately

Fixed orchestration is not one shape but a small family of reusable ones.  Below is each shape as its own "slide": a one-line *when to use*, a tiny flow sketch, and a pointer to where you have already met it.  In all five, notice the common property: **the wiring is authored by you and does not change based on what the agents produce.**

### 4a.  Sequential Pipeline (A -> B -> C)

*When to use:* the steps are known ahead of time and each stage refines the previous stage's output.

```text
input --> [ Extract ] --> [ Draft ] --> [ Polish ] --> output
             facts          prose         tight prose
```

This is the `digest_pipeline` from Part II. Each stage carries a one-sentence system prompt and sees only its own input; the seams between stages are where you inspect for bugs.

### 4b.  Router / Dispatch (classify, then one specialist)

*When to use:* one input, several possible handlers, and exactly one of them applies.

```text
                       .--> [ Hardware specialist ]
input --> [ Classify ] +--> [ Software specialist ] --> output
                       '--> [ Accounts specialist ]
```

This is `route()` from Part II. The classifier's only job is to emit one label from a closed set; a code-level guard forces any stray output back into the valid set.

### 4c.  Parallel Fan-Out / Gather (map-reduce)

*When to use:* the task splits into N *independent* subtasks whose separate results are then combined.

```text
              .--> [ Agent 1 ] --.
input --> split +--> [ Agent 2 ] --+--> [ Aggregate ] --> output
              '--> [ Agent N ] --'
```

The subtasks share no context (that independence is what lets them run in parallel) and a final aggregator agent (or plain code) merges the results.  Compare this to the sequential pipeline: there each stage *depends* on the last; here the branches are deliberately isolated until the gather step.

### 4d.  Critique-Refine (generator <-> critic loop)

*When to use:* there is a quality bar you can articulate and check, and one pass is not reliably good enough.

```text
input --> [ Generate ] --> draft <==> [ Critique ] --> (revise until pass OR budget) --> output
```

The loop is bounded (it stops when the critic is satisfied or a revision budget expires) so the control flow is still fixed, even though it iterates.  This is the subject of its own activity: [Critique-and-Refine](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-critiquerefine.md).

### 4e.  Debate / Stochastic Consensus (many agents, vote or cluster)

*When to use:* the answer is uncertain or subjective, and several independent attempts give you a more robust result than any single one.

```text
          .--> [ Agent A ] --.
input --> +--> [ Agent B ] --+--> [ Vote / Cluster ] --> consensus
          '--> [ Agent C ] --'
```

The agents argue or answer independently, and a fixed aggregation rule (majority vote, clustering of answers) produces the final result.  Two activities develop this shape: [Multi-Agent Debate](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-multiagentdebate.md) and [Stochastic Consensus](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-consensus.md).

Every shape above is *fixed*: even the critique loop and the debate vote follow a control flow you authored and can draw on a whiteboard before running.  What changes in the next section is who draws that diagram.

---

## 5.  Dynamic Orchestration: the Supervisor Loop

When you *cannot* draw the diagram in advance (the task is open-ended, and which sub-agents are needed depends on what earlier ones discover) you promote the orchestrator itself to an LLM. This is the pattern behind LangGraph's **supervisor** and behind LangChain **DeepAgents**, which you meet hands-on in the [Agent Frameworks]({{ site.baseurl }}/Tutorials/AgentFrameworks) activity.

The mechanism is a loop.  You give the supervisor the task and a **roster**: a menu of sub-agents (and the tools each may use).  Then, each turn, the supervisor model reads the task, the roster, and the transcript so far, and emits one *action*: "call sub-agent X on this input," "spawn a new researcher for this newly-discovered subtask," or "STOP, here is the answer."  Your code dispatches the chosen action, appends the result to the transcript, and asks the supervisor again.  DeepAgents dresses this loop in extra machinery (a planning tool that writes a todo list, sub-agents that run in *isolated context windows* so their scratch work never pollutes the main thread, and a synthesis step at the end), but underneath, it is the same "model decides the next move" loop.

Contrast it with the fixed families: a router makes **one** classification decision and then hands off; a supervisor makes a **new** decision on **every** turn and may keep spawning.  That is the source of both its power and its danger.

## Code Cell

The sketch below is illustrative; **read it locally**, do not treat it as production.  It uses the course's `chat(messages)` convention against a local OpenAI-compatible endpoint (e.g., Ollama's `/v1`, LM Studio, or a `llama.cpp` server).  Watch for the three things that stay *yours* even in a "dynamic" system: the **roster**, the **spawn budget**, and the **stop condition**.

```python
import json, requests

def chat(messages, temperature=0.0):
    """One turn against a local OpenAI-compatible chat endpoint.
    messages: the running list of {"role": ..., "content": ...} dicts.
    Returns the assistant's text. Illustrative; run locally only."""
    r = requests.post("http://localhost:11434/v1/chat/completions", json={
        "model": "llama3.2", "temperature": temperature, "messages": messages,
    }, timeout=120)
    return r.json()["choices"][0]["message"]["content"].strip()

# The ROSTER is YOURS: the fixed menu of sub-agents the supervisor may call.
# Each value is a one-sentence system prompt -- the same small-context
# discipline as the pipeline stages in Part II.
ROSTER = {
    "researcher": "You gather facts for a narrow question. Return exactly 3 bullet points.",
    "writer":     "You turn bullet points into one tight paragraph. Output only the paragraph.",
    "critic":     "You list concrete problems with a paragraph, or reply exactly 'OK' if none.",
}

SPAWN_BUDGET = 6   # YOURS: a hard cap on sub-agent calls -- the stop condition of last resort.

def supervise(task):
    """The supervisor LLM decides, each turn, which sub-agent to run next -- or to STOP."""
    transcript = []
    for _ in range(SPAWN_BUDGET):          # the budget caps runaway spawning
        decision = chat([
            {"role": "system", "content":
                "You are an orchestrator. Choose the next step and reply with ONLY JSON. "
                f"Available sub-agents: {list(ROSTER)}. "
                'Reply {"action":"call","agent":"<name>","input":"<text>"} '
                'to delegate, or {"action":"stop","answer":"<final text>"} when done.'},
            {"role": "user", "content":
                f"TASK: {task}\n\nTRANSCRIPT SO FAR:\n{json.dumps(transcript, indent=2)}"},
        ])
        try:
            step = json.loads(decision)
        except json.JSONDecodeError:
            break                          # malformed decision -> stop safely (YOUR guard)

        if step.get("action") == "stop":
            return step.get("answer", "")  # the supervisor decided the work is done

        agent = step.get("agent")
        if agent not in ROSTER:            # closed-set guard, exactly like the Part II router
            transcript.append({"agent": agent, "error": "unknown sub-agent"})
            continue

        # Dispatch: the sub-agent runs in its OWN tiny context -- isolation by construction,
        # so one sub-agent's scratch work never leaks into another's prompt.
        result = chat([
            {"role": "system", "content": ROSTER[agent]},
            {"role": "user",   "content": step.get("input", "")},
        ])
        transcript.append({"agent": agent, "input": step.get("input"), "result": result})

    # Budget exhausted without a STOP: return what we have, and FLAG that we were cut off.
    return f"[stopped: spawn budget of {SPAWN_BUDGET} reached]\n{json.dumps(transcript, indent=2)}"

print(supervise("Write one tight paragraph on why local models matter, then have it reviewed."))
```

**What you still own.**  Handing control flow to a model does *not* hand it your responsibilities.  Three levers stay in your code, and they are the whole reason a dynamic system is safe to ship:

- **The roster.**  The supervisor can only call sub-agents you put on the menu.  An empty or overly-broad roster is where open-endedness turns into risk.
- **The spawn budget.**  The `for _ in range(SPAWN_BUDGET)` loop is a hard ceiling on model calls.  Without it, a confused supervisor can spawn sub-agents forever, burning tokens and time with no result.
- **The stop condition.**  The supervisor may declare `"stop"`, but *you* also stop it when the budget is hit, and you **flag** that outcome rather than pretending the truncated transcript is a finished answer.

DeepAgents makes exactly these decisions (when to plan, when to spawn, when to finish) *inside* its built-in system prompt, which is why it is so concise to use and so much harder to debug when it misbehaves.  When you write the loop yourself, those decisions are visible in ten lines; when the framework writes it, they move into the framework's prompt.

---

## Model 5: Who Decides Control Flow?

| Pattern | Who decides the control flow | Reach for it when | Main risk |
|---|---|---|---|
| Sequential pipeline | You, before runtime | The steps are known and each refines the last | An error at a seam propagates silently downstream |
| Router / dispatch | You (the classifier only picks a label) | One input, several handlers, exactly one applies | A mis-classification sends the whole task to the wrong specialist |
| Parallel fan-out / gather | You (branches are independent by design) | N independent subtasks whose results combine | The aggregator hides disagreement or drops a branch's result |
| Critique-refine | You (a bounded generator <-> critic loop) | A checkable quality bar that one pass misses | The loop never converges and burns the revision budget |
| Debate / consensus | You (a fixed voting or clustering rule) | Uncertain or subjective answers needing robustness | Correlated agents "agree" on the same wrong answer |
| Supervisor (dynamic) | An orchestrator LLM, each turn | The workflow cannot be enumerated in advance | Runaway spawning and unpredictable, hard-to-audit paths |

### Critical Thinking Questions

9.  A hospital wants an agent system to draft discharge summaries and must certify to a regulator that the process is auditable and behaves the same way for comparable patients.  Argue why a **fixed** pipeline is easier to certify than a supervisor loop, and name the specific property of each that a regulator would ask about.

   > *Hint: A regulator asks "can you show me, in advance, every path this system can take, and can you reproduce a given run?"  For a fixed pipeline the path is the same every time and each seam's intermediate is inspectable.  For a supervisor, the path is a model output that can differ between two similar inputs.  Which property makes "we tested this exact flow" a true statement?*

10.  A supervisor loop is given a vague task and, on each turn, decides to spawn "one more researcher to be thorough."  Describe the runaway failure this invites, and explain precisely how the `SPAWN_BUDGET` in the Code Cell caps it, including what should happen at the moment the budget is hit.

    > *Hint: Without a ceiling, "one more to be thorough" has no natural stopping point; cost and latency grow unbounded while the answer never finalizes. The budget converts an open-ended loop into a bounded one. But capping is not enough: look at the final `return` in the code. Why does it prepend `[stopped: ...]` instead of returning the transcript as if it were a finished answer?*

11.  You are handed a new task and must pick a family before writing any code.  Give one concrete question you would ask about the task whose answer decides between a **fixed** shape and a **dynamic supervisor**, and explain why the same "least dynamic pattern that works" heuristic from Part I still applies one level up.

    > *Hint: The decisive question is roughly "can I enumerate the sequence (or set) of sub-agents this task needs before it starts?" If yes, a fixed shape is cheaper, more predictable, and easier to debug, so prefer it. A supervisor earns its unpredictability only when the answer is "no, the needed steps depend on what we discover along the way." How does choosing dynamic-when-fixed-would-do repeat the exact mistake the Part I heuristic warns against?*

> **Common Misconception:** Students often assume "dynamic orchestration" means "the developer no longer controls the system."  The opposite is true of any system you would actually deploy.  In a supervisor loop the model chooses the *next move*, but you still author the roster it chooses from, the budget that bounds it, and the stop condition that ends it.  Dynamic orchestration relocates *some* decisions to the model; it never relocates your responsibility for the roster, the budget, and the stop.

Which single property most distinguishes a supervisor (dynamic) orchestrator from a router (fixed)?

[( )] A supervisor uses a larger model than a router
[( )] A router can call tools but a supervisor cannot
[(X)] A router makes one classification decision and then hands off, while a supervisor makes a new control-flow decision on every turn and may spawn additional sub-agents
[( )] A supervisor is always cheaper because it stops as soon as it is confident
