# Human-in-the-Loop: Oversight, Escalation, and Appropriate Autonomy
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-humanintheloop.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-humanintheloop.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Human-in-the-Loop: Oversight, Escalation, and Appropriate Autonomy

An agent that can act in the world — send emails, write files, submit forms, execute code — raises an immediate governance question: which actions should it take unilaterally, and which should it pause on and ask a human? Too much autonomy means errors compound without correction. Too many checkpoints means the human becomes a rubber stamp who stops reading the prompts. This activity develops a principled framework for **human-in-the-loop (HITL)** design: when to escalate, how to preserve task state during a pause, how to avoid approval fatigue, and how to calibrate trust over time.

---

## Directions and Group Roles

Work in your POGIL team of four with clearly assigned roles:

- **Manager**: Keeps the group on task and on time; ensures everyone contributes before moving on.
- **Recorder**: Documents the group's answers and posts the final responses to the Class Activity Questions discussion board.
- **Presenter**: Speaks for the group during debrief; articulates areas of genuine disagreement or alternative interpretations.
- **Reflector**: Monitors group process and captures lessons learned for the reflection prompt.

Consider each model and its questions individually before discussing with your group. Disagreement within the group is productive — different team members may draw the checkpoint boundary in different places, and reconciling those differences is the point.

---

## Model 1: The Autonomy Spectrum and Checkpoint Criteria

Agent deployment exists on a spectrum from fully manual (the human does every step) to fully autonomous (the agent acts without any checkpoints). Between these extremes are two important operating modes:

- **Human-on-the-loop**: The agent acts immediately but a human monitors and can intervene. Used for low-stakes, reversible, high-volume tasks.
- **Human-in-the-loop**: The agent *pauses before acting* on specific trigger conditions and waits for explicit human approval. Used for high-stakes, irreversible, or ambiguous situations.

The key design decision is identifying the **trigger conditions** that promote an action from autonomous execution to human review. Research and practice have converged on five primary triggers:

1. **Irreversibility**: The action cannot be undone (file deletion, sent email, financial transaction).
2. **High stakes**: The consequences of error are large (production deployment, external communication, legal document).
3. **Low confidence**: The agent's own uncertainty about the goal or the action is above a threshold.
4. **Novelty**: The situation does not match prior successful patterns.
5. **Ambiguity**: The user's intent admits multiple reasonable interpretations that lead to different actions.

The **minimal footprint principle** is a design heuristic that says: when multiple actions could accomplish a goal, prefer the one with the smallest scope, fewest side effects, and highest reversibility. Escalate *before* taking large actions, not after.

| Situation | Action Type | Reversible? | Stakes | Escalate? | Rationale |
|-----------|-------------|-------------|--------|-----------|-----------|
| Agent identifies 3 files as duplicates and is about to delete them | File deletion | No | Medium | Yes | Deletion is irreversible; false positives exist; user should confirm |
| Agent is about to send an email on the user's behalf to a client | External communication | No | High | Yes | Irreversible; high stakes; reputational risk |
| Agent is adding a calendar event for a meeting the user explicitly requested | Calendar write | Yes (deletable) | Low | No | Low stakes; reversible; user intent is unambiguous |
| Agent is about to purchase a $500 software license | Financial transaction | No (refund may exist, not guaranteed) | High | Yes | Financial cost; irreversibility; exceeds routine threshold |
| Agent is pushing code to a production branch | Code deployment | Partially (rollback is possible but costly) | Critical | Yes | Production impact; blast radius is high; novelty risk |
| Agent is fetching a public webpage to answer a factual question | Read-only | N/A | Low | No | No side effects; reversible by nature |

### Critical Thinking Questions

1. The table marks calendar-event creation as "No escalation" because it is reversible. Describe a realistic scenario in which a calendar write *should* trigger escalation despite being reversible. What property of the situation changes the calculus?

2. The minimal footprint principle says prefer smaller-scope actions. An agent is asked to "clean up the project folder." It could (a) move files to a dated archive folder, (b) delete files it deems unnecessary, or (c) ask the user for a list of files to remove. Rank these by footprint and identify which trigger condition applies to each.

3. Confidence-based escalation requires the agent to know when it does not know. How would you operationalize a confidence threshold? What specific signal from the model would you use, and what are its failure modes?

---

## Model 2: The Escalation Protocol

When a trigger condition fires, the agent must pause execution, preserve its current state, communicate the reason for escalation to the human in a way that enables an informed decision, and then resume (or abort) once the human responds. A naive implementation blocks the entire process synchronously. A production-grade implementation suspends state asynchronously.

```python
def execute_action(action, context, confidence):
    """
    Attempt to execute an action. Escalate to a human if any trigger fires.
    Returns the action result or raises EscalationPending.
    """
    reasons = []

    if action.is_irreversible():
        reasons.append(f"irreversible: {action.describe_side_effects()}")

    if action.estimated_cost > COST_THRESHOLD:
        reasons.append(f"cost exceeds threshold: ${action.estimated_cost:.2f}")

    if confidence < CONFIDENCE_THRESHOLD:
        reasons.append(f"confidence below threshold: {confidence:.2f}")

    if action.category in HIGH_STAKES_CATEGORIES:
        reasons.append(f"action category requires approval: {action.category}")

    if reasons:
        checkpoint = Checkpoint(
            task_id=context.task_id,
            action=action,
            reasons=reasons,
            state_snapshot=context.serialize()   # preserve full agent state
        )
        checkpoint.save()
        notify_human(checkpoint)
        raise EscalationPending(checkpoint.id)   # caller suspends and waits

    return sandbox.execute(action, context)
```

In **asynchronous HITL**, the agent saves a complete state snapshot before raising `EscalationPending`. The human reviews the checkpoint — potentially hours later — approves, rejects, or modifies the action, and the agent reloads the snapshot and continues. The human's response must be cryptographically tied to the specific checkpoint (not just "approve the last thing") to prevent replay attacks.

### Critical Thinking Questions

4. The pseudocode saves `context.serialize()` before escalating. What specific information must be in that snapshot for the agent to resume correctly after a human approves the action? List at least five fields and explain why each is necessary.

5. The human receives a notification: "Agent wants to delete `/project/data/results_old.csv`. Approve?" What additional information would you include in the notification to make this a *meaningful* choice rather than a reflexive click? Design the notification format.

6. The code raises `EscalationPending` and the caller suspends. In a web-based agent system, what happens to the HTTP connection while the agent waits for human approval? Propose two different architectural patterns for handling this — one synchronous (long-poll or WebSocket) and one asynchronous (webhook or queue-based) — and identify the trade-offs.

---

## Model 3: Approval Fatigue and Trust Calibration

Human oversight only has value if humans engage thoughtfully with the checkpoints they are given. When the approval rate approaches 100% and the average review time drops to under two seconds, the human is no longer providing oversight — they are providing a rubber stamp. This is **approval fatigue**, and it is actively harmful: it creates the appearance of oversight without the substance, while adding latency.

Compare two designs for an agent that processes 50 incoming support tickets per day:

**Design A** (checkpoint-heavy): The agent asks for human approval before (1) classifying each ticket, (2) selecting a response template, (3) personalizing the template, and (4) sending the response. That is up to 200 approval prompts per day.

**Design B** (trigger-based): The agent acts autonomously on routine tickets (classification confidence > 0.9, template match score > 0.8, no refund or account-closure language). It escalates only when a trigger fires. On average, 8 of 50 tickets per day reach a human.

| Metric | Design A | Design B |
|--------|----------|----------|
| Approvals per day | ~200 | ~8 |
| Avg. human review time per approval | 1.5 sec (fatigue) | 45 sec (engaged) |
| Probability human catches an error | Low (skimming) | High (focused) |
| Total human time per day | ~5 min (low quality) | ~6 min (high quality) |
| Agent latency per ticket | High (blocks on each step) | Low (most tickets flow through) |

**Trust calibration** is the practice of periodically reviewing autonomous decisions in shadow mode — where the agent acts but a human also reviews the outcome after the fact — to detect systematic errors and adjust thresholds. As the agent proves reliable in a domain, checkpoint frequency decreases. If error rates climb, thresholds tighten automatically.

### Critical Thinking Questions

7. Design A has a higher approval count but lower actual oversight quality. Explain the mechanism by which more checkpoints leads to *worse* human attention per checkpoint. What cognitive phenomenon is at work?

8. In Design B, the agent handles 42 of 50 tickets autonomously. A critic argues this is dangerous because the human is "not in the loop." Write a counterargument that defends Design B as actually providing better oversight than Design A, using the table's numbers.

9. Trust calibration gradually reduces checkpoint frequency as the agent proves reliable. What safeguard prevents this process from reducing oversight to zero? Who should be authorized to adjust the trust calibration parameters, and should there be a floor below which checkpoint frequency cannot go?

[[MC]]
An agent is given a task that runs overnight as a batch job: process 1,000 customer records and generate personalized outreach emails. No human is available to review approvals until morning. The most appropriate human-in-the-loop design for this scenario is:
- ( ) Synchronous HITL: pause the batch job for every high-stakes action and wait for a human response before continuing
- ( ) Disable HITL entirely for batch jobs since no human is available anyway
- (x) Asynchronous HITL with a pre-approved action policy: define which actions are pre-approved for batch context, escalate exceptions to a human review queue, and do not send any emails until a human clears the queue in the morning
- ( ) Run the job fully autonomously and review the sent emails after the fact

---

## Exercises

1. **Escalation trigger design.** You are building a coding agent that can write files, run tests, and commit to a git repository. Define a complete set of escalation triggers with specific thresholds. For each trigger, explain what harm it prevents and what the cost of the false-positive rate (unnecessary escalations) would be.

2. **Checkpoint notification design.** Design the human-facing notification for the scenario: "Agent wants to send the following email to 847 customers." Include all fields a human needs to make an informed decision. Mock it up as structured text.

3. **Approval fatigue audit.** You have logs showing that a human reviewer approved 312 of 315 agent checkpoints last month, with an average review time of 2.1 seconds. Write a brief analysis: is oversight functioning? What would you change, and how would you measure improvement?

4. **Async HITL state machine.** Draw a state diagram (as a table of states and transitions) for an agent task that supports asynchronous HITL. States should include at minimum: Running, Escalated, AwaitingApproval, Approved, Rejected, Resumed, Completed, Aborted.

---

## Reflection Prompt

In your notebook: approval fatigue is not unique to AI systems — it appears in security certificate warnings, terms-of-service agreements, and safety checklists in high-pressure environments. Describe a time when you or someone you know clicked "approve" or "accept" without reading carefully. What was the system designer assuming about human attention that turned out to be wrong? How does that experience shape how you would design a checkpoint in an agent system?

---

## Further Reading

- Christiano et al. "Deep Reinforcement Learning from Human Preferences." *NeurIPS* (2017). https://arxiv.org/abs/1706.03741
- Anthropic. "Constitutional AI: Harmlessness from AI Feedback." https://arxiv.org/abs/2212.08073
- Ouyang et al. "Training Language Models to Follow Instructions with Human Feedback." *NeurIPS* (2022). https://arxiv.org/abs/2203.02155
- Shneiderman, B. "Human-Centered AI." Oxford University Press (2022). Chapter 4: Trust and Oversight.
