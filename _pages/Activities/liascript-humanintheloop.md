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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Human-in-the-Loop (HITL)** | A system design where a human must review and approve specific agent actions before they are executed, rather than letting the agent act freely | An agent pausing before sending an email to 847 customers and showing a human the draft for approval |
| **Human-on-the-Loop** | A design where the agent acts immediately but a human monitors the activity stream and can intervene if something goes wrong | An agent filing support tickets autonomously while a supervisor watches a dashboard showing each ticket as it is filed |
| **Escalation Trigger** | A specific condition that causes an agent to pause and ask for human approval instead of proceeding | "If the estimated cost of the action exceeds $50, always ask for approval" |
| **Approval Fatigue** | The phenomenon where a reviewer who sees too many approval prompts starts clicking "approve" without reading them, eliminating the safety benefit of the checkpoint | A human who approves 200 checkpoints per day in an average of 1.5 seconds each is not actually reading the checkpoints |
| **Minimal Footprint Principle** | The design heuristic that says: when multiple actions could accomplish a goal, prefer the one with the smallest scope, fewest side effects, and highest reversibility | Moving duplicate files to an archive folder (reversible) rather than deleting them permanently (irreversible) |
| **Trust Calibration** | The ongoing process of adjusting how much autonomy an agent gets based on its measured error rate in a domain — more autonomy as it proves reliable, less if errors rise | Reducing the agent's confidence threshold for escalation after it makes three wrong classifications in a row |

---

## Model 1: The Autonomy Spectrum and Checkpoint Criteria

Agent deployment exists on a spectrum from fully manual (the human does every step) to fully autonomous (the agent acts without any checkpoints). Between these extremes are two important operating modes:

- **Human-on-the-loop**: The agent acts immediately but a human monitors and can intervene. Used for low-stakes, reversible, high-volume tasks where errors are catchable before they cause harm.
- **Human-in-the-loop**: The agent *pauses before acting* on specific trigger conditions and waits for explicit human approval. Used for high-stakes, irreversible, or ambiguous situations where a mistake before intervention could cause lasting harm.

The key design decision is identifying the **trigger conditions** that promote an action from autonomous execution to human review. Research and practice have converged on five primary triggers:

1. **Irreversibility**: The action cannot be undone — file deletion, sent email, financial transaction, published post.
2. **High stakes**: The consequences of error are large — production deployment, external communication to many people, legally binding document.
3. **Low confidence**: The agent's own uncertainty about the goal or the action is above a threshold — the model is less than 70% confident in its classification.
4. **Novelty**: The situation does not closely match any prior successful pattern in the agent's history — this type of request has never been handled before.
5. **Ambiguity**: The user's intent admits multiple reasonable interpretations that would lead to different actions — "clean up the folder" could mean archive, delete, or reorganize.

The **minimal footprint principle** is a design heuristic that says: when multiple actions could accomplish a goal, prefer the one with the smallest scope, fewest side effects, and highest reversibility. Escalate *before* taking large actions, not after.

| Situation | Action Type | Reversible? | Stakes | Escalate? | Rationale for This Decision |
|-----------|-------------|-------------|--------|-----------|-----------|
| Agent identifies 3 files as duplicates and is about to delete them permanently | File deletion | No — deleted files may not be recoverable even from trash | Medium — data loss is costly but not catastrophic | Yes | Deletion is irreversible; false positives are common in duplicate detection; user should verify before data is lost |
| Agent is about to send an email on the user's behalf to a client | External communication | No — recipient has received the email and cannot un-receive it | High — professional reputation and client relationship are at stake | Yes | Irreversible action; high stakes; the agent cannot know the full context of the client relationship |
| Agent is adding a calendar event for a meeting the user explicitly requested in the same conversation | Calendar write | Yes — the event can be deleted or edited immediately | Low — a wrong event is easily corrected | No | Low stakes; reversible; user intent is unambiguous (they just asked for this); escalation would add friction with no safety benefit |
| Agent is about to purchase a $500 software license using the user's payment method | Financial transaction | No — refund may or may not be possible; time and effort are lost | High — $500 expenditure; potentially non-refundable | Yes | Financial cost; irreversibility uncertain; exceeds routine spending threshold |
| Agent is pushing code to a production branch that serves real users | Code deployment | Partially — rollback is possible but requires effort and causes downtime | Critical — a bug in production affects real users immediately | Yes | Production impact; blast radius is very high; even small errors affect users who cannot wait for a fix |
| Agent is fetching a public webpage to answer a factual question | Read-only web request | N/A — reads have no lasting effect | Low — the worst outcome is a wrong answer | No | No side effects; nothing is changed; any error is easily corrected by asking again |

### Critical Thinking Questions

1. The table marks calendar-event creation as "No escalation" because it is reversible. Describe a realistic scenario in which creating a calendar event *should* trigger escalation despite being easy to undo. What specific property of the situation changes the calculus?

   *Hint: Consider an agent that creates a meeting invitation and sends it to 50 external attendees. The event itself is deletable, but what side effect of creating a recurring meeting invitation cannot be easily undone?*

2. The minimal footprint principle says prefer smaller-scope actions. An agent is asked to "clean up the project folder." It could (a) move files to a dated archive folder with a name like `archive-2026-06-21/`, (b) delete files it deems unnecessary, or (c) ask the user for an explicit list of files to remove before doing anything. Rank these three options by their footprint from smallest to largest, and identify which escalation trigger applies to each option.

   *Hint: Think about what information is destroyed or moved beyond easy recovery in each option. Which option creates the smallest blast radius if the agent makes a mistake?*

3. Confidence-based escalation requires the agent to know when it does not know. How would you operationalize a "confidence threshold" in practice — what specific numeric signal from the model would you measure, and what are its failure modes (situations where the confidence score is wrong)?

   *Hint: LLMs can output a probability score for each token they generate. One approach is to look at the probability of the top choice versus the second choice: a high-probability first choice suggests confidence; a near-tie suggests uncertainty. But when might a model be confidently wrong — outputting a high-probability answer that is nevertheless incorrect?*

---

## Model 2: The Escalation Protocol

When a trigger condition fires, the agent must pause execution, preserve its current state, communicate the reason for escalation to the human in a way that enables an informed decision, and then resume (or abort) once the human responds. A naive implementation blocks the entire process synchronously — the agent freezes and waits. A production-grade implementation suspends state asynchronously — the agent saves its work and resumes when the human responds, potentially hours later.

```python
def execute_action(action, context, confidence):
    """
    Attempt to execute an action. Escalate to a human if any trigger fires.
    Returns the action result, or raises EscalationPending if human approval is needed.
    """
    reasons = []    # Collect all reasons for escalation — there may be more than one

    # Trigger 1: irreversibility — cannot be undone once executed
    if action.is_irreversible():
        reasons.append(f"irreversible: {action.describe_side_effects()}")
        # Example: "irreversible: sends email to client@example.com"

    # Trigger 2: cost exceeds a threshold defined in configuration
    if action.estimated_cost > COST_THRESHOLD:
        reasons.append(f"cost exceeds threshold: ${action.estimated_cost:.2f}")
        # Example: "cost exceeds threshold: $523.00"

    # Trigger 3: the model's own confidence in this action is too low
    if confidence < CONFIDENCE_THRESHOLD:
        reasons.append(f"confidence below threshold: {confidence:.2f}")
        # Example: "confidence below threshold: 0.43"

    # Trigger 4: certain categories of actions always require approval (configured at deployment time)
    if action.category in HIGH_STAKES_CATEGORIES:
        reasons.append(f"action category requires approval: {action.category}")
        # Example: "action category requires approval: external_communication"

    if reasons:
        # One or more triggers fired — create a checkpoint and notify the human
        checkpoint = Checkpoint(
            task_id=context.task_id,         # ID of the parent task this action belongs to
            action=action,                    # The full action object, including all parameters
            reasons=reasons,                  # List of reasons so the human understands why this was escalated
            state_snapshot=context.serialize()  # Complete agent state — everything needed to resume later
        )
        checkpoint.save()       # Persist to database so it survives if the server restarts
        notify_human(checkpoint)    # Send notification (email, Slack, dashboard alert, etc.)
        raise EscalationPending(checkpoint.id)  # Caller catches this and suspends the task

    # No triggers fired — execute the action normally and return the result
    return sandbox.execute(action, context)
```

In **asynchronous HITL**, the agent saves a complete state snapshot before raising `EscalationPending`. The human reviews the checkpoint — potentially hours later — approves, rejects, or modifies the action, and the agent reloads the snapshot and continues. The human's response must be cryptographically tied to the specific checkpoint (not just "approve the last thing") to prevent replay attacks where an old approval is reused for a new action.

> **⚠️ Common Misconception:** Many students assume that "human-in-the-loop" means a human watches every single action the agent takes. This is not scalable and, paradoxically, produces worse oversight — humans who must approve hundreds of actions per day stop reading them carefully. Good HITL design is *selective*: humans review the actions that most need their judgment, and the agent handles everything else autonomously. The goal is quality of oversight, not quantity of approvals.

### Critical Thinking Questions

4. The pseudocode saves `context.serialize()` before escalating. This snapshot must contain everything needed for the agent to resume correctly after the human approves — potentially hours later. List at least five specific fields that must be in the snapshot and explain why each is necessary for correct resumption.

   *Hint: Think about what the agent knew at the moment it paused: the original task description, what it has done so far, the action it wants to take, the files it has already modified, and the tool call history. What would happen if any of these were missing when the agent tried to resume?*

5. The human receives a notification: "Agent wants to delete `/project/data/results_old.csv`. Approve?" This single-line notification is not enough for an informed decision. Design a richer notification format that includes everything a human needs to make a meaningful choice. Write out the fields and example values.

   *Starter hint: Think about what questions you would ask before approving this deletion:*
   - *Why does the agent want to delete this file? (What task is it working on?)*
   - *How large is the file? When was it last modified? Is it tracked in git?*
   - *What happens to the task if the human says No?*
   - *Is there a backup? Can this be undone?*

6. The code raises `EscalationPending` and the caller suspends the task. In a web-based agent system, what happens to the HTTP connection between the browser and the server while the agent waits for human approval? Propose two different architectural patterns for handling this — one synchronous approach and one asynchronous approach — and identify the key tradeoff between them.

   *Hint: Synchronous approach: keep the HTTP connection open (long-poll) and respond when the human approves — simple to implement, but HTTP connections time out after ~30 seconds. Asynchronous approach: return immediately with a task ID, and the browser polls or uses a WebSocket to check for updates — more complex, but scales to waits of hours or days.*

---

## Model 3: Approval Fatigue and Trust Calibration

Human oversight only has value if humans engage thoughtfully with the checkpoints they are given. When the approval rate approaches 100% and the average review time drops to under two seconds, the human is no longer providing oversight — they are providing a rubber stamp. This is **approval fatigue**, and it is actively harmful: it creates the *appearance* of oversight without the substance, while adding latency and annoying the reviewer.

Compare two designs for an agent that processes 50 incoming support tickets per day:

**Design A** (checkpoint-heavy): The agent asks for human approval before (1) classifying each ticket, (2) selecting a response template, (3) personalizing the template, and (4) sending the response. That is up to 200 approval prompts per day from a single agent.

**Design B** (trigger-based): The agent acts autonomously on routine tickets (classification confidence > 0.9, template match score > 0.8, no refund or account-closure language). It escalates only when a trigger fires. On average, 8 of 50 tickets per day reach a human reviewer.

| Metric | Design A — Checkpoint-Heavy | Design B — Trigger-Based |
|--------|----------|----------|
| Approvals per day | ~200 — human approves every sub-step of every ticket | ~8 — human reviews only the tickets that hit a trigger condition |
| Avg. human review time per approval | 1.5 seconds — reviewer is skimming because there are too many | 45 seconds — reviewer is engaged because each escalation is unusual and important |
| Probability human catches an actual error | Low — reviewer skimming at 1.5 sec per prompt does not read carefully | High — reviewer spending 45 seconds on 8 focused cases can read, question, and decide thoughtfully |
| Total human time per day | ~5 minutes total, but low quality and low attention | ~6 minutes total, but high quality and high attention |
| Agent latency per ticket | High — every ticket blocks multiple times waiting for human clicks | Low — 84% of tickets flow through without any pause |

**Trust calibration** is the practice of periodically reviewing autonomous decisions in shadow mode — where the agent acts but a human also reviews the same cases after the fact — to detect systematic errors and adjust thresholds. As the agent proves reliable in a domain, checkpoint frequency decreases. If error rates climb, thresholds tighten automatically. This is not a one-time setup but an ongoing measurement process.

### Critical Thinking Questions

7. Design A has a higher approval count but lower actual oversight quality. Explain the specific cognitive mechanism by which reviewing more checkpoints leads to *worse* attention per checkpoint. What psychological phenomenon is at work, and what analogies from other fields (medicine, aviation, nuclear power) show the same pattern?

   *Hint: Research on checklists in high-stakes environments shows that when every item on a checklist is always green, operators stop reading the checklist. This is sometimes called "alarm fatigue" in medical monitoring. What does a human brain do differently when it expects a problem versus when it expects everything to be fine?*

8. In Design B, the agent handles 42 of 50 tickets autonomously — 84% of the workload with no human in the loop. A critic argues this is dangerous: "If the agent makes a systematic error in how it classifies tickets, 42 tickets per day will be mishandled before anyone notices." Write a specific counterargument that defends Design B as providing *better* oversight than Design A, using the numbers in the table and the concept of shadow mode review.

   *Hint: Design A provides the illusion of oversight (200 rubber-stamp approvals) while Design B provides actual oversight (8 focused reviews + shadow mode sampling that catches systematic errors). Which approach is more likely to notice a systematic classification error?*

9. Trust calibration gradually reduces checkpoint frequency as the agent proves reliable. What safeguard should prevent this process from reducing oversight to zero — even for a perfect agent? Who should be authorized to change the trust calibration parameters, and what governance structure should exist around that authority?

   *Hint: Even a perfectly reliable agent might make different errors in novel situations it has never encountered. What is the minimum checkpoint frequency that should exist regardless of the agent's track record? Is there a category of actions (by stakes or irreversibility) that should always require human review, no matter how well-calibrated the agent is?*

[[MC]]
An agent is given a task that runs overnight as a batch job: process 1,000 customer records and generate personalized outreach emails. No human is available to review approvals until morning. The most appropriate human-in-the-loop design for this scenario is:
- ( ) Synchronous HITL: pause the batch job for every high-stakes action and wait for a human response before continuing
- ( ) Disable HITL entirely for batch jobs since no human is available anyway
- (x) Asynchronous HITL with a pre-approved action policy: define which actions are pre-approved for batch context, escalate exceptions to a human review queue, and do not send any emails until a human clears the queue in the morning
- ( ) Run the job fully autonomously and review the sent emails after the fact

---

## Exercises

1. **Escalation trigger design.**

   *What to do:* You are building a coding agent that can write files, run tests, and commit to a git repository. Define a complete set of escalation triggers with specific, measurable thresholds. For each trigger, explain what harm it prevents and what the cost of a false positive (unnecessary escalation) would be for the developer's workflow.

   *Starter hint:* Think about each action type separately:
   ```
   write_file:   trigger if file is in /etc/, /usr/, or any path outside /workspace/
   run_tests:    no escalation (read-only operation with no side effects)
   git_commit:   trigger if any file containing "secret", "key", or "token" is staged
   git_push:     ALWAYS trigger — push to remote is irreversible and affects others
   delete_file:  ALWAYS trigger — even in /workspace/, deletion is irreversible
   ```
   For each trigger, ask: what is the worst thing that happens if this fires unnecessarily (false positive), and what is the worst thing that happens if it fails to fire (false negative)?

   *You've succeeded when* your trigger list covers all five of the actions above, has specific thresholds (not just "if it seems dangerous"), and includes an explicit cost-benefit statement for each trigger's false-positive rate.

2. **Checkpoint notification design.**

   *What to do:* Design the human-facing notification for this scenario: "Agent wants to send the following email to 847 customers." Format it as structured text that includes all the information a human needs to make an informed, non-fatigued decision in under 60 seconds.

   *Starter hint:* A good checkpoint notification answers these questions without requiring the reviewer to ask:
   ```
   CHECKPOINT REQUIRED — External Communication
   Task: [What is the agent trying to accomplish overall?]
   Action: Send email to 847 customers
   Subject: [The email subject line]
   Preview: [First 3 sentences of the email body]
   Triggered by: [Which trigger fired and why]
   If approved: [What happens next]
   If rejected: [What the agent will do instead]
   Estimated impact if wrong: [What goes wrong if this email is incorrect]
   Reversibility: [Can customers be un-emailed? Can a correction be sent?]
   [APPROVE]  [REJECT]  [MODIFY AND APPROVE]
   ```

   *You've succeeded when* your notification design could be handed to a reviewer who has never seen the task before and they could make a confident decision in under 60 seconds without needing to look up additional information.

3. **Approval fatigue audit.**

   *What to do:* You have logs showing that a human reviewer approved 312 of 315 agent checkpoints last month (99% approval rate), with an average review time of 2.1 seconds per checkpoint. Write a brief analysis: is oversight functioning? What specific changes would you make to the checkpoint design, and how would you measure whether the changes improved oversight quality?

   *Starter hint:* A 99% approval rate at 2.1 seconds per review strongly suggests the reviewer is not reading. To diagnose: pull the 3 rejections and look at what properties they shared. To fix: consider raising the confidence threshold (so fewer, more important things escalate), adding a "why does this need review?" explanation to each checkpoint, and implementing shadow mode to catch systematic errors that approvals are missing.

   *You've succeeded when* your analysis includes: (1) a diagnosis of why the current system is not working, (2) at least two specific changes to the checkpoint design, and (3) a metric you would track to confirm the changes improved oversight quality.

4. **Async HITL state machine.**

   *What to do:* Design a state diagram for an agent task that supports asynchronous HITL. Represent it as a table showing all states and the transitions between them, with the event or condition that triggers each transition.

   *Starter hint:* Minimum states to include: Running, Escalated, AwaitingApproval, Approved, Rejected, Resumed, Completed, Aborted. For each transition, name the event: for example, "Running → Escalated" is triggered by "trigger condition fires." Some states should have timeout transitions — what happens if a checkpoint sits in AwaitingApproval for 48 hours with no response?

   *You've succeeded when* your state diagram is complete enough that a developer could implement it directly — every state has at least one incoming transition and at least one outgoing transition, and there are no dead ends except Completed and Aborted.

---

## Reflection Prompt

*Personal:* Approval fatigue is not unique to AI systems — it appears in security certificate warnings in web browsers, terms-of-service agreements, and safety checklists in high-pressure environments. Describe a specific time when you or someone you know clicked "approve" or "accept" without reading carefully. What was the system designer assuming about human attention that turned out to be wrong? How does that experience shape how you would design a checkpoint in an agent system?

*Technical:* Based on today's models, write a specific escalation policy for one of the following agent types: (a) a coding agent that can write files and run tests, (b) a customer service agent that can read and respond to support tickets, or (c) a research agent that can search the web and save documents. Your policy should include specific trigger conditions with thresholds, a trust calibration schedule, and a minimum checkpoint frequency that cannot be reduced regardless of performance.

*Societal:* Human-in-the-loop is sometimes described as the solution to AI safety problems. But this activity shows that HITL has real costs: latency, reviewer attention limits, approval fatigue, and the need for humans to be available at arbitrary times. As AI agents become more capable and are deployed in higher-stakes domains (medical diagnosis, legal advice, financial planning), is HITL a sustainable long-term solution, or does it need to evolve into something else? What would that something else look like?

---

→ Coming Up Next: Human-in-the-loop oversight relies on the agent communicating clearly about what it wants to do and why. The next activity examines how to make agent outputs structured and machine-readable — so that downstream systems can validate what the agent produces before acting on it.

---

## Further Reading

- Christiano et al. "Deep Reinforcement Learning from Human Preferences." *NeurIPS* (2017). https://arxiv.org/abs/1706.03741
- Anthropic. "Constitutional AI: Harmlessness from AI Feedback." https://arxiv.org/abs/2212.08073
- Ouyang et al. "Training Language Models to Follow Instructions with Human Feedback." *NeurIPS* (2022). https://arxiv.org/abs/2203.02155
- Shneiderman, B. "Human-Centered AI." Oxford University Press (2022). Chapter 4: Trust and Oversight.
