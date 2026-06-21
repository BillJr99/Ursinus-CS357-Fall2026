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

A working agent on a developer's laptop is not a deployed agent. This module closes the gap between a prototype and a production system: **how agents are packaged, where they run, how they survive being killed and restarted, and how you ship a new version without breaking the users who depend on the old one.** The arc: **deployment tiers $\rightarrow$ stateful agents in a stateless world $\rightarrow$ CI/CD pipelines for non-deterministic software**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Where Agents Live

## Model 1: Deployment Tiers

Every deployment context makes different promises about latency, cost, and persistence. The table below maps five tiers commonly used for production agent systems.

| Deployment Context | Startup Latency | Scaling Model | Cost Model | Best For | Agent Persistence Challenge |
|---|---|---|---|---|---|
| **Local Dev (laptop)** | < 1 s (process already running) | Manual; one instance | Developer time only | Prototyping; demos | State lives in RAM; lost on Ctrl-C |
| **VPS / Bare Metal** | 1–5 s (process restart) | Vertical (bigger machine) or manual horizontal | Fixed monthly, always-on | Small, predictable traffic; long-running daemons | Crashes lose in-memory state; must persist externally |
| **Containerized VPS** | 2–10 s (container pull + start) | Horizontal via container replicas | Pay-per-instance, can scale to zero overnight | Teams sharing infrastructure; reproducible builds | Each container is ephemeral; session must survive container death |
| **Kubernetes (K8s)** | 5–30 s (pod scheduling + pull) | Auto-horizontal via HPA; multi-region possible | Compute + orchestration overhead | High-availability, multi-tenant, enterprise deployments | Pod restarts are routine; external state store is mandatory |
| **Serverless / Edge** | 50–2000 ms (cold start) or < 10 ms (warm) | Fully automatic, per-request | Pay per invocation + duration | Bursty or unpredictable traffic; simple request-response | Function is stateless by contract; large models cannot be loaded per-call |

### Critical Thinking Questions

1. A startup ships an agent as a single Python process on a VPS. At 3 AM, the server crashes and restarts. List every piece of agent state that is lost if no external storage is used.

2. Kubernetes schedules pod restarts during routine maintenance. A team argues this is fine because "the agent just starts fresh." Explain what a *user* experiences when the pod restarts mid-conversation, and why "starting fresh" is not cost-free.

3. Compare the **cost model** of bare metal and serverless for an agent that handles exactly 10 requests per day versus one that handles 10,000 requests per day. Which tier is cheaper for each workload, and why?

4. The "startup latency" for Kubernetes is listed as 5–30 seconds. Identify two scenarios where this latency is acceptable and two where it is not. What design pattern converts a high-latency tier into an acceptable one for latency-sensitive workloads?

---

# Part II: State and the Cold-Start Problem

## Model 2: Stateless vs. Stateful Agents in Production

Infrastructure platforms favor **stateless** services: a process that holds no memory between requests can be killed, duplicated, or moved without user impact. Agents are inherently **stateful**: the user's conversation history, the agent's scratchpad, and multi-step task progress must all persist across requests. Reconciling these facts is the central deployment challenge.

**The cold-start problem** has two meanings in agent deployment:

1. *Compute cold start*: a serverless function initializes a large model (potentially gigabytes) on every invocation, adding seconds to the first response.
2. *Context cold start*: a restarted container has no memory of the conversation that was in progress, so the agent behaves as if it is meeting the user for the first time.

Three architectural patterns address the context cold-start problem:

---

### Pattern A — Session Database (Redis / PostgreSQL)

```
# On every response, persist the updated message history
def handle_request(session_id, new_user_message, db):
    history = db.get(session_id) or []
    history.append({"role": "user", "content": new_user_message})
    reply = llm_call(history)
    history.append({"role": "assistant", "content": reply})
    db.set(session_id, history, ttl=3600)   # expire after 1 hour idle
    return reply
```

The agent is stateless; the database is stateful. Any replica can serve any request because they all read from the same store.

---

### Pattern B — Client-Sent Context Window

```
# The CLIENT stores the conversation; sends it on every turn
# Server side (stateless):
def handle_request(full_history_from_client, new_user_message):
    full_history_from_client.append(
        {"role": "user", "content": new_user_message}
    )
    reply = llm_call(full_history_from_client)
    full_history_from_client.append(
        {"role": "assistant", "content": reply}
    )
    return reply, full_history_from_client   # client stores updated history
```

No server-side state at all. The client (browser, mobile app) holds the conversation and echoes it back on each turn.

---

### Pattern C — External Memory Service

```
# A dedicated memory service handles retrieval and compression
def handle_request(session_id, new_user_message, memory_service):
    # Retrieve only the relevant prior context
    relevant_history = memory_service.retrieve(
        session_id, query=new_user_message, top_k=10
    )
    messages = build_messages(relevant_history, new_user_message)
    reply = llm_call(messages)
    # Asynchronously index the new exchange
    memory_service.store(session_id, new_user_message, reply)
    return reply
```

State lives in a vector store or structured memory layer. Retrieval selects *relevant* prior turns rather than sending everything, which keeps the context window bounded regardless of conversation length.

[[MC]]
An agent is deployed as a serverless function that loads a 4 GB model from disk on each invocation. Median response latency is 18 seconds; users complain. The MOST effective fix for cold-start latency is:

- ( ) Increase the function timeout limit from 30 s to 60 s
- (x) Use provisioned concurrency (or an always-warm instance) so the model stays loaded in memory between invocations
- ( ) Reduce the system prompt length by 50%
- ( ) Switch from batch response to streaming output

### Critical Thinking Questions

5. For each of the three patterns (A, B, C), identify one failure mode that could cause the agent to behave incorrectly or lose user data, and propose a mitigation.

6. Pattern B places the conversation history in the client. List two security risks this creates that Pattern A does not have. How would you mitigate them?

7. A user's conversation reaches 200 turns. Compare the server-side memory consumption and the per-request latency of Pattern A vs. Pattern C at this scale.

8. Some agents maintain *task state* (partially completed multi-step work) in addition to *conversation state*. Which pattern best supports task state that must survive a server crash? Justify your choice.

---

# Part III: Shipping Agent Updates Safely

## Model 3: CI/CD for Agents

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

- *Non-determinism*: a test that passes once may fail on the next run at the same temperature. Statistical thresholds replace boolean pass/fail.
- *Eval latency*: running an LLM judge over a 500-item golden dataset takes minutes to hours, not milliseconds.
- *No ground truth*: for open-ended tasks (summarization, advice), "correct" is ill-defined. Human agreement on golden data may be only 80%.
- *Silent regressions*: a prompt change can make some tasks better and others worse simultaneously, so aggregate metrics can look flat while user experience degrades on a subpopulation.

**Deployment strategies for agent updates:**

| Strategy | Mechanism | Agent-Specific Advantage | Agent-Specific Risk |
|---|---|---|---|
| **Rolling** | Replace old instances one at a time | Minimal over-provisioning | Users may get old and new behavior in the same session if load balancer routes to different replicas |
| **Blue-Green** | Run two full environments; switch traffic | Instant rollback by flipping traffic | A user mid-conversation on blue is cut off when traffic moves to green; state must be migrated |
| **Canary** | Route a fraction of traffic to new version | Real user signal before full commit | Canary users experience degraded behavior if new version has a subtle regression |

### Critical Thinking Questions

9. Your prompt regression suite runs 500 golden examples. The new version scores 91% and the old scores 89%. The pipeline gate is set at "new ≥ old." Should you auto-promote to canary? What additional information would change your answer?

10. A rolling deployment sends some users to the old agent and some to the new one. A user opens a conversation, gets one response from the old version, then gets the next response from the new version (which has a different persona). Describe the user experience and propose a technical fix that preserves session affinity.

11. Blue-green deployment lets you instant-rollback by flipping traffic. What happens to a user who has an active 20-turn conversation on the blue environment when traffic is switched to green? Design a migration protocol that handles this case.

12. Traditional software has version numbers visible to users ("v2.3.1"). Agent deployments typically do not. How does this asymmetry of information affect trust, accountability, and debugging when something goes wrong?

---

# Part IV: Synthesis and Practice

## Exercises

1. **Deployment Architecture Design.** A campus course chatbot must handle 1,000 concurrent students during a midterm exam (a 2-hour burst window) and fewer than 10 users at other times. Design a complete deployment architecture: which tier(s) to use, how state is persisted, how you handle the burst, and what the estimated cost difference is between always-on bare metal and a burst-capable serverless or Kubernetes approach. Produce a labeled architecture diagram (boxes and arrows are fine) and a one-paragraph rationale.

2. **Canary Rollout Plan.** Your team has trained a new model version that changes the tone of responses from formal to conversational. Write a step-by-step canary rollout plan: what metrics you monitor, what thresholds trigger a rollback, how long the canary phase runs, what the shadow comparison samples, and how you handle users who explicitly prefer the old formal tone. Include a decision flowchart.

3. **SLA Analysis: Serverless for Medical Triage.** A hospital proposes deploying a patient intake triage agent as a serverless function (cold-start latency: up to 3 seconds; 99.9% uptime SLA from the cloud provider). The agent asks patients about symptoms and routes them to the appropriate care level. Identify three specific SLA implications of this architecture choice, explain what could go wrong for a patient during a cold start or an outage, and propose an alternative architecture that meets a more appropriate SLA for this use case.

---

## Reflection Prompt

In your notebook: a production agent can be updated silently — there is no user-visible version number, no changelog, no notification. A student who uses a course assistant on Monday may be talking to a meaningfully different system on Friday. Should agents be required to disclose their model version and last update date to users? Who should set this requirement — the deploying institution, the model provider, a regulator, or the users themselves? What would "informed consent" to an agent update look like in practice?

---

## Further Reading

- Chip Huyen. *Designing Machine Learning Systems*, Chapter 7: "Model Deployment and Prediction Service" (2022). The infrastructure patterns in today's activity are grounded here.
- Google Cloud. "Deployment Strategies: Canary, Blue-Green, Rolling." *Google Cloud Architecture Center* (2024). Concrete implementation details for each strategy.
- Martin Fowler. "Strangler Fig Application." *martinfowler.com* (2004). The classic pattern for incrementally replacing a monolith — applies directly to migrating from v1 to v2 of an agent backend.
- Zeno AI. "LLM Evaluation in CI/CD." *zenoml.com* (2024). Tools for running prompt regression suites in automated pipelines.
