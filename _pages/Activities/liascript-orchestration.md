# Orchestration Patterns: Pipelines, Routers, and Planners
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-orchestration.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-orchestration.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Orchestration Patterns: Pipelines, Routers, and Planners

Unit 3 begins: instead of making one agent smarter, we make **several simple agents cooperate**. The enabling insight comes straight from the small context window principle: a model given one narrow job and a tiny prompt outperforms the same model juggling five jobs in a bloated prompt. We move from **why decompose $\rightarrow$ the pipeline $\rightarrow$ the router $\rightarrow$ the planner $\rightarrow$ composing them in code**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Orchestrator** | An agent (or piece of code) whose job is to coordinate other agents — deciding what task to assign to whom, in what order, and how to combine their outputs. The orchestrator does not do the actual work; it manages the process. | A campus event system where the orchestrator assigns announcements to an ExtractAgent, then a DraftAgent, then a PolishAgent in sequence. |
| **Subagent** | A specialized agent that receives a narrow task from the orchestrator, completes it, and returns a result. The subagent typically knows nothing about the larger workflow — it just does its one job. | The PolishAgent, which only sees a draft announcement and returns a polished version — it does not know about the extraction or drafting steps. |
| **Pipeline** | An orchestration pattern where agents are arranged in a fixed sequence, each passing its output to the next. The sequence is determined before the pipeline runs and does not change based on what the agents produce. | extract → draft → polish for a digest email, with each stage seeing only its own input. |
| **Router** | An orchestration pattern where a classifier agent reads an input and decides which specialist agent should handle it. The router's only job is to classify; it does not do the work itself. | A help-desk router that classifies incoming tickets as "hardware", "software", or "accounts" and sends each ticket to the right specialist. |
| **Planner** | An orchestration pattern where a planning agent writes a step list for a task at runtime (because the steps cannot be determined in advance), worker agents execute the steps, and the planner revises the plan when workers report failures. | "Plan my study schedule for finals, adapting dynamically as I report which topics I have finished." |
| **Seam** | The boundary between two agents in an orchestration — the point where one agent's output becomes the next agent's input. Seams are the most common location of bugs in multi-agent systems, because small inconsistencies in format or content can compound across a pipeline. | The JSON structure that ResearchAgent produces must exactly match the structure WriterAgent expects — a missing field at this seam causes a silent bug. |

---

# Part I: Decomposition

## 1. Three Foundational Patterns

**Why this matters:** Think of a restaurant kitchen. The head chef does not cook every dish, take orders, and serve tables simultaneously. Instead, the work is divided: servers take orders (routing), line cooks handle specific stations (specialized subagents), and the expediter coordinates the flow (orchestration). This division works because each role has a narrow, well-defined job. When the pasta cook knows nothing about the appetizer station, neither can interfere with the other — and both can focus completely on their job. The same principle applies to agent orchestration: narrow roles, clear handoffs, and an orchestrator that manages the overall flow without doing the detail work.

**Pipeline (fixed sequence).** Stage outputs feed stage inputs: extract $\rightarrow$ draft $\rightarrow$ polish. Each stage has its own small system prompt and sees *only* what it needs. Pipelines are predictable, debuggable (you can inspect any intermediate output), and cheap. They are the right default when the workflow is known in advance.

**Router (one decision, then dispatch).** A classifier agent reads the input and forwards it to one of several specialists: billing questions to the billing agent, technical questions to the tech agent. The router's entire context is the input plus the menu of destinations — about as small as a context gets. Reliability comes from constraining the router's output to a closed set of labels.

**Planner (dynamic decomposition).** When the workflow is *not* known in advance, a planner agent writes a step list, worker agents execute steps, and the planner revises on failures. Planners buy flexibility at the cost of predictability, so we bound them with step budgets, exactly as in the advanced loops activity.

A useful design heuristic follows: **choose the least dynamic pattern that solves the problem.** Pipelines before routers, routers before planners, planners before free-roaming autonomy.

---

## Model 1: Match the Pattern

| Task | Best Pattern? |
|------|---------------|
| Every night, summarize the day's club announcements into one digest email draft. | ? |
| Triage incoming help-desk tickets to hardware, software, or accounts queues. | ? |
| "Plan my study schedule for finals, adapting if I fall behind on a topic." | ? |

### Critical Thinking Questions

1. Assign a pattern (Pipeline, Router, or Planner) to each task and write a one-sentence justification for each choice that uses the heuristic stated above.

   > *Hint: For each task, ask: is the sequence of steps known before the task starts? If yes, consider pipeline. Is the task just a single classification decision? If yes, consider router. Does the workflow need to change based on what happens during execution? If yes, consider planner.*

2. For the triage task, the router sometimes invents a fourth category that is not in its allowed list. Give two distinct fixes: one that changes only the system prompt, and one that changes only the surrounding Python code, with no changes to the prompt.

   > *Hint: The prompt fix should make the closed set explicit and unambiguous. The code fix should intercept whatever label the model produces and force it into the valid set — this is already partially shown in the code below. What is the difference between these two approaches in terms of reliability?*

3. For the digest pipeline, name the intermediate artifact that passes between the Extract stage and the Draft stage, and explain how inspecting that artifact helps you localize a quality bug — contrasting this with debugging a single large prompt that does everything at once.

   > *Hint: If the final digest contains wrong information, with a pipeline you can check whether the problem is in the extracted facts (a bad Extract stage) or in how those facts were used to write the draft (a bad Draft stage). With a single mega-prompt, how would you diagnose the same problem?*

---

# Part II: A Pipeline and Router in Code

## 2. Small Agents, Explicit Seams

**Why this matters:** The code below shows the key property of well-designed orchestration: each agent's system prompt is one sentence long. This is not laziness — it is the point. A one-sentence context cannot distract the model with competing concerns. Each agent does exactly one thing and returns a result. The pipeline orchestrator then passes that result, without modification, to the next agent. The seams between agents are where the data flows — and they are the most important thing to get right, because a small error at a seam (wrong JSON key, missing field, unexpected format) propagates silently through the rest of the pipeline.

You can run this code locally using `ollama run llama3.2` to start the model server, then run the script in a separate terminal:

```bash
# Start the local model server (do this once)
ollama run llama3.2

# In a second terminal, run your orchestration script
python orchestration.py
```

---

## Code Cell

The code below implements both a three-stage pipeline (extract → draft → polish) and a two-stage router (classify → dispatch) using a local language model. Read through the comments before running it — each comment explains a design choice you will be asked about in the questions that follow.

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
    # This is a code-level fix — a prompt-level fix would say "output ONLY one of these three words"
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

4. Each `llm` call in the pipeline has a one-sentence system prompt and sees only its own immediate input. Connect this design choice directly to the "lost in the middle" finding from the memory module, where models fail to use information that appears in the middle of a long context.

   > *Hint: If a single mega-prompt contained all three jobs — extract, draft, and polish — how long would it be? Where in that context would the "polish for concision" instruction appear relative to the raw announcements? What does the lost-in-the-middle finding predict about how well the model would follow that instruction?*

5. The router guard `label if label in SPECIALISTS else "software"` makes a silent default decision when the model produces an unexpected label. Argue for or against this silent default, and propose what a "louder" failure would look like and when you would prefer it.

   > *Hint: A silent default means the ticket gets routed to "software" even if it really belongs to "accounts" — no one is notified that the classification failed. A louder failure would log the error, send an alert, or raise an exception. When does silence protect the user experience, and when does it hide a bug?*

6. The polish stage could introduce errors the extract stage never made — for example, changing "Thursday at 7" to "Friday at 7" while editing for concision. Where in the pipeline would you insert a verification step, and which tool or pattern from earlier in the course would you reuse for it?

   > *Hint: Think about the critique-and-refine pattern. Could you add a "verify" stage after "polish" that checks the final output against the extracted facts? What would its one-sentence system prompt say?*

> **⚠️ Common Misconception:** Many students assume that because a pipeline has multiple agents, it is inherently more reliable than a single agent. This is not automatically true. A pipeline can fail at any seam, and because each agent is working from the previous agent's output rather than the original input, errors can compound silently. A pipeline is more *maintainable* and more *debuggable* than a mega-prompt — but only if you actually inspect the intermediate outputs. Return all intermediates from your pipeline functions (as the code above does with `return facts, draft, final`) and check them.

[[MC]]
According to the design heuristic developed today, a team should reach for a planner agent only when:
- ( ) The task involves more than two steps
- ( ) Maximum autonomy is a project goal
- (x) The sequence of steps cannot be determined before runtime
- ( ) The budget allows a larger model

---

# Part III: Synthesis and Practice

In this section you will extend and evaluate the pipeline and router you built in Part II, and you will design the message format for a planner. These exercises connect directly to Lab work, so the design decisions you make here carry forward.

## 3. Exercises

1. **Add a fact-check stage to the pipeline.**

   *What to do:* Add a fourth stage to the `digest_pipeline` function — a `verify` stage that compares the final polished digest against the extracted facts and returns a JSON object indicating whether any facts in the digest are inconsistent with the extracted facts. Then demonstrate it catching a seeded error by manually modifying the digest to introduce a wrong date before passing it to the verify stage.

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

2. **Evaluate the router with a labeled test set.**

   *What to do:* Build a set of 12 help-desk tickets — 4 hardware, 4 software, 4 accounts — where you know the correct category. Run your router on all 12 and compute its classification accuracy. Then deliberately degrade the router's prompt (remove the instruction that restricts output to one of three words) and re-measure accuracy. Report the difference.

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

3. **Design a planner message format.**

   > *Hint: Think about what the planner needs to know when a worker fails. The planner must decide whether to retry the task, skip it, adjust the timeline, or ask the user for help — and it must make that decision based solely on what the failure report contains. What fields would you need in the failure report to support all four of those decisions?*

   *What to do:* On paper, design the JSON message format for the planner-worker interaction in the study-schedule task from Model 1. Your design must specify: (a) what the planner sends to a worker as a task assignment, (b) what a worker sends back to report success, and (c) what a worker sends back to report failure and what information the planner needs to revise the plan. Write out three example messages in full.

   *Starter hint:*
   ```json
   // Planner → Worker: task assignment
   {"task_id": "t1", "action": "study", "topic": "probability", "duration_minutes": 60, "deadline": "2026-12-10"}

   // Worker → Planner: success report
   {"task_id": "t1", "status": "complete", "notes": "Covered chapters 4-6, comfortable with Bayes theorem"}

   // Worker → Planner: failure report (what should go here?)
   {"task_id": "t1", "status": "blocked", "reason": "...", "suggestion": "..."}
   ```

   *You've succeeded when:* Your failure report format contains enough information for the planner to decide whether to reassign the task, adjust the timeline, or ask the user for clarification — without needing to ask the worker any follow-up questions.

---

## Reflection Prompt

Respond to all three levels in your notebook:

**Personal:** Decomposing a big task into narrow roles is also how effective study groups, sports teams, and workplaces operate. Think of a team project — in this class or any other context — where unclear roles caused confusion or duplicated effort. How does the pipeline/router/planner framework map onto what went wrong, and what would the "seam" between two team members look like in practice?

**Technical:** Describe one place in today's pipeline design where information lost at a seam could cause a poor outcome. For example: if the polish stage changes a date while editing for concision, neither the extract stage nor the draft stage will catch it. What is the technical mechanism (a validation step, a schema check, a logging requirement) that would detect this specific failure?

**Societal:** Decomposition into narrow roles is how both efficient organizations and surveillance systems work. A pipeline of agents that each know only their own step can process sensitive data — a student's grades, a person's medical history — without any single agent "knowing" the full picture. Is this a privacy protection or a way to obscure accountability? Who is responsible when a pipeline of individually-compliant agents produces a harmful outcome?

---

→ **Coming Up Next:** The next activity introduces the *critique-and-refine* pattern — a specific pipeline where one agent generates content and a second agent evaluates it against explicit criteria, looping until the quality bar is met or a budget expires.

---

## Further Reading

- Anthropic engineering blog. "Building Effective Agents" (2024, online). The workflow patterns formalized today.
- Wu et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." (2023).
- Leon Festinger's classic organizational-communication literature, for the human analogy (optional browse).
