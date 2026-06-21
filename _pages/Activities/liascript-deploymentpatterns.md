# Deploying Agents: From Laptop to Production
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-deploymentpatterns.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-deploymentpatterns.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Deploying Agents: From Laptop to Production

A working agent on a developer's laptop is not a deployed agent. This module closes the gap between a prototype and a production system: **how agents are packaged, where they run, how they survive being killed and restarted, and how you ship a new version without breaking the users who depend on the old one.** The arc: **deployment tiers → stateful agents in a stateless world → CI/CD pipelines for non-deterministic software**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|:-----|:------------------------|:------------------------|
| **Deployment Tier** | The infrastructure environment where an agent runs — from a developer's laptop (one user, no availability guarantees) to Kubernetes (thousands of concurrent users, automated recovery). Each tier makes different promises about latency, cost, and how long the agent stays alive between requests. | Choosing serverless for a bursty exam-period chatbot saves money during the 22 hours per day when no one is using it, but may cause a 2-second cold-start delay for the first student who asks a question. |
| **Stateless Service** | A server or function that holds no information between requests — every request arrives with everything it needs, and nothing persists when the request is done. Cloud platforms prefer stateless services because they can be killed, duplicated, or moved without user impact. | A serverless function that computes a tax amount from inputs is stateless: the same inputs always produce the same output and nothing is remembered between calls. |
| **Stateful Agent** | An agent that maintains context across multiple turns — conversation history, partially completed tasks, user preferences — which must survive server restarts, container replacements, and load balancer reassignments. Reconciling stateful agents with stateless infrastructure is the central deployment challenge. | A tutoring agent that remembers what a student struggled with last session and continues from where they left off is stateful; if the server restarts between sessions, that memory must survive in an external store. |
| **Cold Start** | The delay that occurs when a service (especially a serverless function) must initialize from scratch — loading model weights, establishing database connections, importing libraries — before it can respond. For large LLMs, cold starts can add 2–20 seconds to the first response. | A serverless function that loads a 4 GB model on every invocation will take 15–20 seconds for the first request; subsequent requests reuse the warm container and respond in under 2 seconds. |
| **Canary Deployment** | A deployment strategy where a small fraction of real traffic (e.g., 5%) is routed to the new version of an agent while 95% continues to use the old version. If the new version causes problems, only 5% of users are affected and rollback is immediate. | Rolling out a new system prompt to 5% of users for 48 hours to verify it does not increase content-filter refusals before enabling it for everyone. |
| **CI/CD Pipeline** | Continuous Integration / Continuous Deployment — an automated sequence of build, test, and deploy steps that runs every time code changes. For agents, the pipeline must include prompt regression testing and LLM-as-judge evaluation (using a second language model to score whether each response meets quality criteria, instead of exact string matching), not just unit tests. | Every pull request to the agent codebase automatically runs 500 golden test cases through an LLM judge before it is allowed to merge, preventing silent regressions in model behavior. |

---

# Part I: Where Agents Live

In this part, you will compare five deployment tiers — from a developer's laptop to Kubernetes — and identify which tier is appropriate for which workload, including the specific promises each tier makes about latency, cost, and what happens to agent state when a server restarts.

## Model 1: Deployment Tiers

> **Why this matters:** Choosing the wrong deployment tier is not just a performance mistake — it can mean your agent loses every conversation when the server restarts, costs ten times more than necessary, or is unable to handle the burst of traffic when 200 students open it simultaneously during an exam. Understanding the trade-offs now means you make this decision intentionally, not accidentally.

Every deployment context makes different promises about latency, cost, and persistence. The table below maps five tiers commonly used for production agent systems.

| Deployment Context | Startup Latency | Scaling Model | Cost Model | Best For | Agent Persistence Challenge |
|:------------------|:----------------|:--------------|:-----------|:---------|:----------------------------|
| **Local Dev (laptop)** | Under 1 second because the process is already running in memory | Manual — one instance, one developer, no load balancing | Developer time only; no infrastructure cost | Prototyping and demos where you control all the inputs and can restart freely | State lives entirely in RAM; every Ctrl-C wipes the conversation history and any in-progress task state |
| **VPS / Bare Metal** | 1–5 seconds for a process restart after a crash or reboot | Vertical scaling (upgrade to a bigger machine) or manual horizontal (add another server by hand) | Fixed monthly cost regardless of traffic — you pay the same whether you serve 1 request or 10,000 | Small, predictable traffic where you want always-on availability without container overhead | Server crashes lose all in-memory state; must persist conversation history to an external database before every response |
| **Containerized VPS** | 2–10 seconds for the container to pull the image and start | Horizontal by adding container replicas, typically managed by a tool like Docker Compose or Nomad | Pay-per-instance; can scale to zero overnight to save cost | Teams sharing infrastructure; reproducible builds where "it works on my machine" is eliminated | Each container is ephemeral — any restart creates a fresh container with no memory of what the previous one knew |
| **Kubernetes (K8s)** | 5–30 seconds for pod scheduling, image pull, and initialization | Automatic horizontal scaling via the Horizontal Pod Autoscaler; multi-region possible | Compute cost plus orchestration overhead (cluster management, ingress, monitoring) | High-availability, multi-tenant, enterprise deployments where the agent must be reachable 24/7 across multiple geographic regions | Pod restarts are routine maintenance events in K8s — an external state store is not optional, it is mandatory |
| **Serverless / Edge** | 50–2000 ms for a cold start (first invocation after idle period), or under 10 ms for a warm invocation | Fully automatic, scales to zero and to thousands of instances per second with no manual configuration | Pay per invocation plus duration — extremely cheap at low volume, can be expensive at high sustained volume | Bursty or unpredictable traffic; simple request-response interactions where the agent finishes work in a single function call | Functions are stateless by contract; large models cannot be loaded per-call at 50–2000 ms cold start without making every first interaction unusable |

### Critical Thinking Questions

1. A startup ships an agent as a single Python process on a VPS. At 3 AM, the server crashes and reboots automatically. List every distinct piece of agent state that is lost if no external storage was used — be specific about what each piece of state is and why losing it matters to the user whose session was in progress.

   *Hint:* Think about the different kinds of things an agent might "know" at the moment of the crash: what the user said in the last 10 turns, what task the agent was in the middle of, what tools the agent had already called, what the agent had already said. Each of those is a separate state artifact. Which ones are most disruptive to lose?

2. Kubernetes schedules pod restarts during routine maintenance. A team argues this is acceptable because "the agent just starts fresh after a restart." Explain specifically what a *user* experiences when the pod restarts mid-conversation — give a concrete example of a two-turn exchange that shows why "starting fresh" is not cost-free.

   *Hint:* Imagine a student who just spent three turns explaining their academic situation to an advising agent. The pod restarts. What does the agent say on the next turn? What does the student have to do? How does that feel?

3. Compare the cost model of bare metal and serverless for two different workloads: (a) an agent that handles exactly 10 requests per day, each taking 5 seconds of compute, and (b) an agent that handles 10,000 requests per day, each taking 5 seconds. For each workload, argue which tier is cheaper and explain why the crossover point between the two tiers exists.

   *Hint:* Bare metal has fixed cost regardless of usage. Serverless has zero cost when idle and per-second cost when running. At what request volume does the serverless cost exceed the flat monthly VPS cost? You do not need exact numbers — the reasoning matters more than the arithmetic.

4. The startup latency for Kubernetes is listed as 5–30 seconds. Give two specific deployment scenarios where this startup latency is acceptable and two where it is not. Then name the design pattern that converts a high-startup-latency tier into an acceptable one for latency-sensitive use cases.

   *Hint:* Latency is only a problem if a user is waiting for it. Are there agent use cases where no one is waiting during the startup period? What does "provisioned concurrency" or "warm pods" do for this problem?

With the deployment tiers mapped, Part II addresses the central engineering challenge: agents are inherently stateful, but cloud infrastructure prefers stateless services, and reconciling these two facts requires one of three architectural patterns.

---

# Part II: State and the Cold-Start Problem

In this part, you will study three patterns for keeping conversation state alive across container restarts and identify the specific security and failure risks each pattern introduces — because the "simplest" pattern often introduces the most surprising vulnerability.

## Model 2: Stateless vs. Stateful Agents in Production

> **Why this matters:** Cloud infrastructure is designed for stateless services — things that can be killed and replaced without any user noticing. Agents are inherently stateful — they are useless if they cannot remember what you said two turns ago. Bridging this gap is the central engineering challenge of production agent deployment. The three patterns below are the three main solutions the industry has converged on. Each solves the problem differently and introduces different failure modes.

Infrastructure platforms favor **stateless** services: a process that holds no memory between requests can be killed, duplicated, or moved without user impact. Agents are inherently **stateful**: the user's conversation history, the agent's scratchpad, and multi-step task progress must all persist across requests. Reconciling these facts is the central deployment challenge.

**The cold-start problem** has two meanings in agent deployment:

1. *Compute cold start*: a serverless function must initialize a large model (potentially gigabytes of weights) from disk on its first invocation after an idle period, adding seconds to the first response.
2. *Context cold start*: a restarted container has no memory of the conversation that was in progress, so the agent behaves as if it is meeting the user for the first time even though the user is in the middle of a complex task.

Three architectural patterns address the context cold-start problem:

---

### Pattern A — Session Database (Redis / PostgreSQL)

Pattern A stores conversation state in an external database so any container replica can serve any request. Read the `db.get` and `db.set` calls — these are the two lines that make a stateless server behave like a stateful agent.

```python
# On every response, persist the updated message history to an external database
def handle_request(session_id, new_user_message, db):
    history = db.get(session_id) or []      # load prior turns from DB
    history.append({"role": "user", "content": new_user_message})
    reply = llm_call(history)              # LLM sees full prior context
    history.append({"role": "assistant", "content": reply})
    db.set(session_id, history, ttl=3600)  # persist; expire after 1 hr idle
    return reply
```

The agent process is stateless — any replica can serve any request because they all read from the same database. The database is stateful. If the container dies, the next container picks up the conversation from the database without the user noticing anything changed.

---

### Pattern B — Client-Sent Context Window

Pattern B eliminates server-side state entirely by having the client send the full conversation history with every request. Notice what this means for server complexity — and think about what it means for the security of that history.

```python
# The CLIENT stores the conversation; sends the full history on every turn
# Server side is completely stateless:
def handle_request(full_history_from_client, new_user_message):
    full_history_from_client.append(
        {"role": "user", "content": new_user_message}
    )
    reply = llm_call(full_history_from_client)
    full_history_from_client.append(
        {"role": "assistant", "content": reply}
    )
    # Return both the reply and the updated history;
    # the client stores the updated history and echoes it back next turn
    return reply, full_history_from_client
```

No server-side state at all — zero database infrastructure needed. The client application (browser, mobile app) holds the conversation and sends the full history with every new message. This pattern is used by many simple chatbot implementations.

---

### Pattern C — External Memory Service

Pattern C uses a dedicated memory service that retrieves only the most relevant prior turns rather than the full history. This keeps the context window bounded as conversations grow, but at the cost of implementation complexity and the risk that a critical earlier turn is not retrieved.

```python
# A dedicated memory service handles storage, compression, and relevance retrieval
def handle_request(session_id, new_user_message, memory_service):
    # Retrieve only the prior turns that are relevant to the current message
    relevant_history = memory_service.retrieve(
        session_id, query=new_user_message, top_k=10
    )
    messages = build_messages(relevant_history, new_user_message)
    reply = llm_call(messages)
    # Asynchronously index the new exchange for future retrieval
    memory_service.store(session_id, new_user_message, reply)
    return reply
```

State lives in a vector store or structured memory layer. At each turn, only the most *relevant* prior turns are retrieved and included — not the full history. This keeps the context window bounded regardless of how long the conversation has been running, at the cost of implementation complexity.

[[MC]]
An agent is deployed as a serverless function that loads a 4 GB model from disk on each invocation. Median response latency is 18 seconds; users complain. The MOST effective fix for cold-start latency is:

- ( ) Increase the function timeout limit from 30 s to 60 s — the model finishes loading before the timeout, so the limit is not what is causing the 18-second delay
- (x) Use provisioned concurrency (or an always-warm instance) so the model stays loaded in memory between invocations
- ( ) Reduce the system prompt length by 50% — the 18-second latency is dominated by model weight loading, not by prompt processing time
- ( ) Switch from batch response to streaming output — streaming reduces time-to-first-token after the model is loaded, but does not affect the loading latency that precedes the first token

> **Common Misconception:** Many developers assume that Pattern B (client-sent context) is "simpler and safer" than Pattern A (session database) because there is no server-side state to manage. In reality, Pattern B introduces its own risks: the full conversation history is stored in the client's browser or app, where it can be inspected, modified, or stolen by malicious scripts. A user who modifies their local conversation history before sending it to the server can inject fabricated "prior assistant messages" that manipulate the agent's behavior. Pattern A's centralized database is actually easier to secure than the client's local storage.

### Critical Thinking Questions

5. For each of the three patterns (A, B, C), identify one specific failure mode that could cause the agent to behave incorrectly or lose user data, and propose a concrete mitigation for each failure mode.

   *Hint:* For Pattern A, think about what happens if the database is temporarily unavailable. For Pattern B, think about what happens if the client sends a corrupted or maliciously modified history. For Pattern C, think about what happens if the relevance retrieval misses an important earlier turn — one where the user said something critical that the current message does not obviously reference.

6. Pattern B places the full conversation history in the client. List two specific security risks that Pattern B introduces that Pattern A does not share. For each risk, describe a concrete attack scenario and the mitigation you would implement.

   *Hint:* What can a user (or malicious script on their device) do to the conversation history if it is stored in browser local storage? What can the server do to verify that the history it receives was not tampered with?

7. A user's conversation reaches 200 turns — roughly 40,000 tokens of combined user and assistant messages. Compare the server-side resource consumption and the per-request latency of Pattern A versus Pattern C at this conversation length. Which pattern scales better, and what is the trade-off you accept to get that scalability?

   *Hint:* Pattern A loads the entire 40,000-token history from the database and sends it all to the LLM on every turn. Pattern C retrieves only the 10 most relevant turns. What are the LLM API costs for each at 200 turns? What does Pattern C risk losing that Pattern A preserves?

8. Some agents maintain *task state* — the record of partially completed multi-step work (e.g., "I have called tools A and B; next I need to call C and return the synthesized result") — in addition to *conversation state*. Which of the three patterns best supports task state that must survive a server crash? Justify your choice with a specific argument about what happens to in-progress task state during a crash for each pattern.

   *Hint:* Task state is more structured than conversation history — it is more like a database record than a chat log. Which pattern's storage mechanism is better suited to structured, transactional state? What happens to a task that was 70% complete when Pattern A's container crashes mid-execution?

With state persistence solved, Part III tackles a subtler problem: how do you ship a new version of an agent safely when you cannot write `assert response == exact_string` to know if it is working correctly?

---

# Part III: Shipping Agent Updates Safely

In this part, you will study the stages of a production agent CI/CD pipeline and the deployment strategies used to roll out changes safely — including why canary deployments expose some users to degraded behavior by design, and how to bound that exposure.

## Model 3: CI/CD for Agents

> **Why this matters:** In traditional software, "does it work?" is answered by unit tests: same input, same output, test passes. For agents, behavior is non-deterministic and emergent — you cannot write `assert response == "exact expected string"`. This means the entire CI/CD methodology must be redesigned for agents: statistical thresholds instead of boolean assertions, LLM judges instead of exact matching, and canary deployments that measure real user behavior before full rollout. Every production team building agents uses some version of what you are learning here.

Traditional software CI/CD pipelines test deterministic code: the same input always produces the same output, so assertions are exact. Agent behavior is **non-deterministic** (temperature > 0), **emergent** (behavior comes from billions of weights, not readable source lines), and **evaluated qualitatively** (is this response *good*?). These properties make standard CI/CD pipelines necessary but insufficient.

**A production agent CI/CD pipeline adds stages that do not exist in ordinary software CI:**

```
Stage 1:  Lint + unit tests
          (tool schemas valid, API contracts satisfied, deterministic utilities)

Stage 2:  Prompt regression suite
          (golden dataset of (input, expected behavior) pairs;
           judged by LLM-as-judge or embedding similarity, not exact match)

Stage 3:  Canary deploy (5% of production traffic → new version)
          (monitor latency, error rate, user satisfaction signal for 24–48 h)

Stage 4:  Shadow mode comparison
          (run old and new versions on same traffic; diff their outputs;
           human reviewers sample divergent cases)

Stage 5:  Full rollout (if stages 3–4 pass gates)
```

**What makes agent CI/CD harder than normal software CI/CD:**

- *Non-determinism*: a test that passes once may fail on the next run at the same temperature. Statistical thresholds replace boolean pass/fail — "passes 94% of the time" is a meaningful result.
- *Eval latency*: running an LLM judge over a 500-item golden dataset takes minutes to hours, not milliseconds. A test suite that takes 2 hours to run changes how often you can deploy.
- *No ground truth*: for open-ended tasks (summarization, advice, code review), "correct" is ill-defined. Human agreement on golden data may be only 80%, which means any eval score above 80% may be indistinguishable from human-level performance.
- *Silent regressions*: a prompt change can make some tasks better and others worse simultaneously, so aggregate metrics can look flat while user experience degrades on a specific subpopulation — and you will not notice until users complain.

**Deployment strategies for agent updates:**

| Strategy | Mechanism | Agent-Specific Advantage | Agent-Specific Risk |
|:---------|:----------|:------------------------|:--------------------|
| **Rolling** | Replace old instances one at a time, with health checks between each replacement | Minimal over-provisioning; gradual exposure to any instability in the new version | Users may get old-version and new-version responses in the same session if the load balancer routes different turns to different replicas — the agent's "persona" can shift mid-conversation |
| **Blue-Green** | Run two complete environments simultaneously; flip all traffic from old (blue) to new (green) in one instant | Instant, clean rollback — flip traffic back to blue if green has problems | A user mid-conversation on the blue environment is cut off when traffic flips to green; the green environment has no knowledge of that user's conversation history unless state migration is performed |
| **Canary** | Route a small percentage of real traffic (typically 2–10%) to the new version while the majority stays on the old version | Real production signal — real users with real queries expose behavior that synthetic tests miss | The canary users experience degraded behavior if the new version has a subtle regression; you are intentionally exposing some users to a potentially worse system |

### Critical Thinking Questions

9. Your prompt regression suite runs 500 golden examples. The new version scores 91% pass rate and the old version scores 89%. The pipeline gate is set at "new must be >= old." Should you auto-promote to canary? Describe at least two additional pieces of information that would change your answer — and for each, explain what it would tell you that the aggregate score does not.

   *Hint:* An aggregate score hides subgroup performance. What if the new version is better on 80% of categories but dramatically worse on one specific category? What if 91% overall hides 60% on the safety-critical subset of test cases? What does a 2-percentage-point difference even mean when human raters agree only 80% of the time?

10. A rolling deployment sends some users to the old agent and some to the new one. A user opens a conversation, receives one response from the old version, and then receives the next response from the new version because the load balancer assigned their next request to a different replica. Describe the specific user experience problem this creates. Then propose a technical fix that preserves session affinity — routing all turns of a single session to the same version.

    *Hint:* The user is not aware there are two versions. They see one conversation with two responses that may have different tones, different factual assertions, or different formatting styles. Session affinity is typically implemented via sticky sessions at the load balancer level — how would you implement that, and what does it require from the session identifier?

11. Blue-green deployment enables instant rollback by flipping all traffic from green back to blue. What happens to a user who has an active 20-turn conversation on the green environment when traffic is flipped back to blue? Design a concrete migration protocol that handles this specific case — be specific about the data that needs to move and when.

    *Hint:* The user's conversation state is stored somewhere — either in the green environment's database or in the client. If it is in a shared database (Pattern A), flipping traffic does not lose the state. If it is environment-specific, you need to either migrate it before the flip or have a graceful degradation strategy for in-flight conversations.

12. Traditional software exposes version numbers to users — you can see "app version 2.3.1" in the settings menu. Agent deployments typically do not expose version numbers — users interact with the same interface regardless of which prompt version or model checkpoint is running. Explain specifically how this asymmetry of information affects trust, accountability, and debugging when a user reports that the agent "used to be helpful but now gives worse answers."

    *Hint:* If you cannot tell the user which version changed, what can you tell them? If a deployer is accused of degrading service quality, what evidence is available to adjudicate the claim? What would it take to implement meaningful version transparency for an agent system?

The three parts above have given you the vocabulary — tiers, state patterns, and CI/CD stages — that Part IV now applies to realistic deployment design exercises with real constraints and tradeoffs.

---

# Part IV: Synthesis and Practice

In this part, you will design a complete deployment architecture, write a canary rollout plan with concrete thresholds, and analyze a medical-grade SLA requirement — applying every concept from the prior three parts to scenarios where the consequences of a wrong decision are real.

## Exercises

1. **Deployment Architecture Design.**

   *What to do:* A campus course chatbot must handle 1,000 concurrent students during a midterm exam (a 2-hour burst window) and fewer than 10 users during the remaining 22 hours of the day. Design a complete deployment architecture: which tier(s) to use, how conversation state is persisted across the burst period, how you handle the traffic spike at exam start, and what the estimated cost difference is between always-on bare metal and a burst-capable serverless or Kubernetes approach. Produce a labeled architecture diagram (boxes and arrows are fine) and a one-paragraph rationale.

   *Starter hint:* Consider a hybrid approach: a small always-warm fleet handles baseline traffic cheaply, while an auto-scaling group or serverless overflow handles the burst. Draw the request flow: student browser → load balancer → agent instance → external session database → LLM API. Label each arrow with what travels across it (HTTP request, session ID, conversation history, LLM response). For cost estimation, assume a small VPS costs $50/month and serverless costs $0.0001 per request-second.

   *You've succeeded when:* Your diagram shows state persistence explicitly (not just "the agent"), your cost estimate makes a specific numerical argument for the hybrid approach over always-on, and your rationale addresses what happens to users who start a conversation at minute 118 of the 2-hour exam window.

2. **Canary Rollout Plan.**

   *What to do:* Your team has trained a new model version that changes the tone of agent responses from formal to conversational. Write a step-by-step canary rollout plan: what metrics you monitor, what thresholds trigger an automatic rollback, how long the canary phase runs, what the shadow comparison samples, and how you handle users who explicitly prefer the formal tone. Include a simple decision flowchart (text-based is fine).

   *Starter hint:* Your metrics should include at least one safety metric (e.g., content-filter refusal rate, which should not change with a tone update), one quality metric (e.g., LLM-judge helpfulness score on sampled conversations), and one user satisfaction signal (e.g., thumbs-up/thumbs-down rate if your interface has one). Your rollback threshold should be specific: "if content-filter rate increases by more than 0.5 percentage points over the 48-hour canary window, auto-rollback." The tone preference issue is a product decision — document your proposed approach.

   *You've succeeded when:* Your plan specifies every metric with a concrete threshold, specifies a rollback trigger that does not require human judgment to evaluate, and addresses the user preference case with a specific product decision rather than "we will think about it."

3. **SLA Analysis: Serverless for Medical Triage.**

   *What to do:* A hospital proposes deploying a patient intake triage agent as a serverless function. The cloud provider promises cold-start latency up to 3 seconds and a 99.9% uptime SLA. The agent asks patients about symptoms and routes them to the appropriate care level. Identify three specific SLA implications of this architecture choice, explain what could go wrong for a patient during a cold start or during the 0.1% downtime (approximately 8.7 hours per year), and propose an alternative architecture that meets a more appropriate SLA for this medical use case.

   *Starter hint:* The 99.9% uptime SLA sounds impressive until you calculate that 0.1% of a year is 8.76 hours — during which the triage agent is completely unavailable. For a patient arriving at the ER at 2 AM, a 3-second cold start may feel like a system failure. Consider: what SLA does a medical triage system actually need? What does a five-nines (99.999%) SLA require architecturally, and what does it cost? Your alternative architecture should address both the cold-start and the uptime problems explicitly.

   *You've succeeded when:* You have calculated the actual downtime implied by 99.9% uptime, described a specific patient-harm scenario (not just "slower response"), and proposed an alternative architecture with a specific uptime target and a specific cost justification for the upgrade.

---

## Reflection Prompt

**Personal level:** Think about a digital product you use regularly — a course management system, a bank app, a social media platform. Has it ever changed in a way that was disorienting or that made it worse for you, without any explanation? How did you find out what changed, and were you given any choice about it? How does that experience inform your view on agent version transparency?

**Technical level:** A production agent can be updated silently — there is no user-visible version number, no changelog, no notification. A student who uses a course assistant on Monday may be talking to a meaningfully different system on Friday. Should agents be required to disclose their model version and last update date to users? Who should set this requirement — the deploying institution, the model provider, a regulator, or the users themselves?

**Societal level:** What would "informed consent" to an agent update look like in practice? Draft a one-paragraph disclosure notice that a university would send to students before deploying a new version of a course advising agent. Then evaluate your own draft: is it actually informative, or is it the kind of consent notice that people click through without reading?

---

→ **Coming Up Next:** In the next activity, we examine adversarial robustness and red-teaming — the discipline of systematically trying to break your own agent before malicious users do, and building the test infrastructure to detect regressions in safety as you ship updates.

---

## Further Reading

- Chip Huyen. *Designing Machine Learning Systems*, Chapter 7: "Model Deployment and Prediction Service" (2022). The infrastructure patterns in today's activity are grounded here.
- Google Cloud. "Deployment Strategies: Canary, Blue-Green, Rolling." *Google Cloud Architecture Center* (2024). Concrete implementation details for each strategy.
- Martin Fowler. "Strangler Fig Application." *martinfowler.com* (2004). The classic pattern for incrementally replacing a monolith — applies directly to migrating from v1 to v2 of an agent backend.
- Zeno AI. "LLM Evaluation in CI/CD." *zenoml.com* (2024). Tools for running prompt regression suites in automated pipelines.
