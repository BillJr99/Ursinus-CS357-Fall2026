<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-multiagentprotocols.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Multi-Agent Communication: Protocols, Shared State, and Coordination

**CS357: Foundations of Artificial Intelligence / Agentic AI**
Ursinus College

---

## POGIL Roles

In this activity, your team will work together using the following roles.  Rotate roles with each new activity.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the team on task and on time; ensures everyone contributes; calls for consensus before moving on |
| **Recorder** | Writes down the team's agreed answers; manages the shared document or whiteboard |
| **Presenter** | Speaks for the team during class discussion; summarizes findings to the class |
| **Reflector** | Monitors team process; notes what is working and what is not; leads the Reflection section |

> Before starting, confirm your roles aloud.  If your team has fewer than 4 members, one person may take two roles (e.g., Manager + Reflector).

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Message passing** | One agent sends a structured message directly to another agent, who reads and replies, like sending an email that demands a response before the sender continues working | Agent A asks Agent B for a research summary using a JSON-RPC call; B sends back the result |
| **Shared blackboard** | All agents read from and write to a single shared storage location, like a collaborative Google Doc where nobody talks to each other directly, but everyone updates the same file | Three agents each write their section of a report to a shared JSON document |
| **Event streaming** | Agents emit events to a central channel; other agents subscribe and react when relevant events arrive, like subscribing to a group chat where you only respond to messages addressed to you | Agent B starts summarizing as soon as Agent A posts a "search complete" event |
| **Race condition** | When two agents read the same data, make decisions based on it, and write back at the same time, potentially overwriting each other's work or acting on stale information | Two agents both claim task #7 from a queue and execute it twice |
| **Deadlock** | A standstill where Agent A waits for Agent B, while Agent B simultaneously waits for Agent A; neither can ever proceed | Agent A holds a database lock waiting for a file that Agent B holds, while B waits for the database |
| **A2A / MCP** | A2A (Agent-to-Agent) is an emerging protocol for how agents discover and delegate to each other; MCP (Model Context Protocol) is the standardized way agents call external tools like databases and APIs | An orchestrator agent uses A2A to delegate a research task to a specialist, which uses MCP to query a paper database |

---

## Model 1: How Agents Communicate

Message passing between agents is like email between colleagues: you need to agree on a format, a subject line, and what kind of response you expect, or nothing gets understood.  When one agent simply shouts data into the void and another has to guess what it means, the system breaks down quickly.  The three communication primitives below are the fundamental building blocks that real multi-agent frameworks use, and each one solves a different coordination problem.

When multiple agents collaborate on a task, they must exchange information.  There is no single correct way to do this; the right choice depends on the task structure, how frequently agents need to coordinate, and what kinds of failures must be tolerated.

Three fundamental communication primitives appear across multi-agent frameworks:

| Primitive | How It Works | Best For | Failure Mode | Example in Course Tools |
|-----------|-------------|----------|--------------|------------------------|
| **Message passing** | Agent A sends a structured message directly to Agent B; B reads it and responds. Common standards: FIPA ACL (formal performatives, the "speech act" type of the message), JSON-RPC (function-call style), HTTP REST (request and response over the web). | Sequential pipelines; tasks with clear handoffs where one step must complete before the next begins; situations where a response is needed before continuing | Message lost in transit; receiver crashes before reading; malformed message schema that neither agent can parse | Anthropic A2A agent-to-agent calls; MCP tool request/response |
| **Shared blackboard** | All agents read from and write to a common state object (e.g., a JSON document, database, or file). Agents communicate indirectly by changing what they see in the shared state; no direct agent-to-agent messages. | Parallel tasks where multiple agents each contribute a piece of the whole; stigmergic coordination (agents react to changes in the environment rather than to each other) | Race conditions when multiple agents write simultaneously; stale reads where an agent acts on outdated data; one agent accidentally overwrites another's completed work | Shared tool-call memory object; Anthropic shared context window |
| **Event streaming** | Agents emit events (e.g., "search complete," "error occurred") to a bus or stream; other agents subscribe to event types they care about. Producers and consumers are loosely coupled; they never address each other directly. | Loose coupling where producers and consumers should not need to know about each other; broadcast notifications; reactive pipelines where Agent B should act automatically whenever Agent A finishes | Events delivered out of order; subscriber misses events if it was not connected when they were emitted; event schema mismatches between producer and consumer | Server-Sent Events in streaming tool responses; Kafka-style agent coordination |

### Critical Thinking Questions

**Question 1.**  In a multi-agent system where three agents all have write access to the same JSON document (shared blackboard), what can go wrong if two agents try to update the same field at the same time?  Describe the problem concretely: what state does the document end up in, and how does that compare to what either agent intended?

[[___ Your answer here ___]]

*Hint:* Imagine both agents read the field at the same moment (both see `"status": "pending"`), each decides to update it, and each writes their update, but the second write simply overwrites the first.  Think about what gets lost, and whether the final state reflects either agent's intention.

**Question 2.**  FIPA ACL messages include a **performative** field that specifies the communicative intent of the message, for example: `inform` (I am telling you a fact), `request` (I am asking you to do something), `propose` (I am suggesting a deal), `agree`, `refuse`, `query-if`.  What does this add over sending raw JSON? Give one example where knowing the performative changes how the receiving agent should respond.

[[___ Your answer here ___]]

*Hint:* Consider what a receiving agent would do differently upon receiving `{"type": "inform", "content": "task complete"}` versus `{"type": "request", "content": "task complete"}`.  The performative tells the receiver *what kind of reply or action is expected*, not just what the content says.

**Question 3.**  A research pipeline has three agents: a searcher that queries a database, an analyst that processes results, and a writer that drafts a report.  Under what circumstances would **event streaming** be a better choice than direct message passing between these agents?  Under what circumstances would message passing be the better choice?  Identify the trade-off.

[[___ Your answer here ___]]

*Hint:* Think about what happens when you want to add a fourth agent (e.g., a fact-checker) to the pipeline.  With message passing, who needs to be updated?  With event streaming, who needs to be updated?  Then think about a situation where the writer must not start until the analyst has fully finished; which primitive enforces that guarantee more naturally?

Choosing the right communication primitive avoids some failures, but once agents share any state at all, a new class of coordination problems emerges that no communication style alone can prevent.

---

## Model 2: Coordination Problems

Real pipelines fail in predictable ways, and those failure patterns have names.  Distributed systems engineers discovered these problems while building databases in the 1970s and 80s, and multi-agent LLM systems run into exactly the same traps.  Learning the vocabulary now means you can diagnose failures in your own systems instead of spending hours wondering what went wrong.

Multi-agent systems inherit the coordination problems of distributed computing, plus new ones specific to LLM agents.  The four most important coordination problems are:

| Problem | Description | Example with Agents | Prevention Strategy |
|---------|-------------|--------------------|--------------------|
| **Race condition** | Two agents read shared state, both decide to act based on what they read, both write, but the second write overwrites the first, or both take an action that should only happen once | Agent A and Agent B both read a task queue, both claim task #7 as "in progress," and both execute it; the task runs twice and produces duplicate output | Atomic compare-and-swap (write only if the value is still what you read); locking; task queue with acknowledgment; optimistic concurrency with version numbers |
| **Deadlock** | Agent A is waiting for Agent B to finish before it can proceed; Agent B is simultaneously waiting for Agent A. Neither can ever move forward because each holds something the other needs. | Agent A holds a database lock and is waiting for Agent B to release a file lock; Agent B holds the file lock and is waiting for Agent A to release the database lock | Lock ordering (always acquire locks in the same order everywhere in the system); timeouts with retry; lock-free designs; leader arbitration |
| **Priority inversion** | A high-priority agent is blocked waiting for a resource held by a low-priority agent, so the low-priority task effectively determines when the high-priority task runs | A critical summary agent is blocked waiting for a low-priority formatting agent to finish writing to the shared document; the urgent output is delayed by a trivial task | Priority inheritance (the low-priority agent temporarily inherits the high-priority agent's priority while it holds the resource); preemption; avoiding shared resources between agents of different priorities |
| **Consensus failure** | Agents must agree on a value or decision but cannot reach agreement; no majority or quorum forms, leaving the system stuck | Three analyst agents each produce a different numerical summary of the same dataset; the orchestrator cannot determine which to use and must stall or escalate | Quorum protocols (2-of-3 agreement required before proceeding); designated tiebreaker agent; confidence-weighted voting; human-in-the-loop for unresolved conflicts |

Classic distributed systems solutions (developed over decades for databases and networked systems) apply directly to agents:

- **Mutex/lock**: only one agent may write a shared resource at a time; others wait until the lock is released
- **Optimistic concurrency**: agents write freely, but include a version number with every write; if the version has changed since they last read, the write is rejected and they must re-read and retry with fresh data
- **Leader election**: one agent is designated coordinator for a given task or resource; others send requests to the leader rather than acting directly on shared state
- **Vector clocks**: each message carries a logical timestamp that captures which events preceded it, allowing receivers to determine the causal order of events even without synchronized clocks; think of it as a "happened-before" tracker

### Critical Thinking Questions

**Question 4.**  Two research agents are both querying the same paper database.  Agent A queries for "machine learning + climate" and Agent B queries for "deep learning + weather."  Both find paper P, which is relevant to both queries.  Both agents independently decide to add paper P to a shared "relevant papers" list.  Describe specifically how a race condition could produce an incorrect final state of the list, and what that incorrect state might look like.

[[___ Your answer here ___]]

*Hint:* Both agents read the list, see it does not contain paper P, and each decides to append it.  Trace through what the list looks like after both writes complete.  Is paper P listed once or twice?  Does the list reflect what either agent intended?

**Question 5.**  You need to implement a mutex so that only one agent at a time can update a shared JSON document.  The agents communicate over HTTP and do not share memory.  Describe, in concrete steps, how you would implement this mutex.  (Hint: consider what a "lock file" or "lock key" in a database would look like, and how an agent would acquire and release it.)

[[___ Your answer here ___]]

*Hint:* Think of a "lock token" stored in the database.  An agent acquires the lock by writing its own ID to a special `lock_holder` field, but only if that field is currently empty (an atomic check-and-set).  It releases the lock by clearing the field.  What happens if an agent crashes while holding the lock?  How do you prevent the lock from being held forever?

**Question 6.**  A two-phase commit protocol (2PC) is used in distributed databases to ensure that either all nodes commit a transaction or none do.  Describe the "agent equivalent" of 2PC: a protocol where a group of agents must either all take an action or all abort, with no partial execution.  What would the two phases look like, and who would play the role of the "coordinator"?

[[___ Your answer here ___]]

*Hint:* Phase 1 is the "can you do this?" round: the coordinator asks each agent to prepare and confirm readiness.  Phase 2 is the "commit or abort" round: only if all agents say yes does the coordinator tell everyone to execute.  What should the coordinator do if even one agent says it cannot proceed?

These coordination problems are not hypothetical; they motivated the development of industry standards that allow real multi-agent systems to interoperate safely across team and organizational boundaries.

---

> **Common Misconception:** Students often assume that if agents each have their own context window and their own prompt, they cannot interfere with each other.  This is only true if agents never share state.  The moment two agents read from and write to the same resource (a file, a database record, a task queue) all the classical coordination problems apply, regardless of how sophisticated the agents are.  The problem is not in the agents' "minds"; it is in the shared resource they both touch.

---

Three agents are collaborating on a report.  Agent A finishes writing its section and writes the string `"DONE"` to a shared status file to signal completion.  Agent B reads the status file before Agent A writes, sees nothing (or sees the old status), concludes the file is empty, and begins writing its own content, overwriting Agent A's completed section.  This scenario is best described as:

[( )] A deadlock, because both agents are waiting for each other; a deadlock requires both agents to be *blocked waiting*, but here Agent B proceeds immediately; neither agent is stuck waiting for the other
[(X)] A race condition caused by missing synchronization between the read and write operations
[( )] A consensus failure, because the agents disagree on the content of the report; consensus failure requires multiple agents to have produced conflicting outputs and be unable to choose; here Agent B simply overwrote Agent A without negotiation
[( )] An example of priority inversion, because Agent B executed before Agent A's higher-priority write completed; priority inversion requires a low-priority agent to *hold a resource* that a high-priority agent is waiting for; here no priority ordering or blocking is involved

---

## Model 3: The Anthropic Agent-to-Agent (A2A) and MCP Standards

Real-world multi-agent systems need more than clever coordination logic; they need agreed-upon standards so that an orchestrator built by one team can delegate to a specialist built by a completely different team.  The A2A and MCP standards are the industry's current answer to this problem, and they are the foundation of the agent pipelines you will build in this course.

As multi-agent systems move from research prototypes to production, the field has developed emerging standards for how agents should discover, delegate to, and communicate with each other.

**The A2A (Agent-to-Agent) Protocol** addresses three core needs:

1.  **Discovery**: An agent advertises its capabilities in a machine-readable format (its "agent card"), allowing an orchestrator to identify which specialist agent to delegate to for a given subtask, without needing to be pre-programmed with every specialist's capabilities.
2.  **Delegation**: Agent A (the orchestrator) spawns Agent B (a specialist) to handle a subtask, passing it the necessary context.  Crucially, Agent B operates in its own context window; it does not automatically see everything Agent A knows.  The orchestrator must explicitly decide what context to send.
3.  **Trust boundaries**: Agent B cannot exceed the permissions of the user who authorized Agent A. If the user authorized "read-only access to documents," Agent B cannot acquire write access, even if Agent B's own system prompt would otherwise allow it.  This principle prevents privilege escalation through agent delegation.

**MCP (Model Context Protocol)** serves as the standardized tool interface: agents use MCP to call tools (file systems, databases, APIs, other services) in a consistent, discoverable format.  Multi-agent systems can compose MCP servers: one agent's tools can include calling another agent that exposes itself as an MCP server.

**Example pipeline (described as a table):**

| Component | Role | Communicates Via | Tools Used |
|-----------|------|-----------------|------------|
| Orchestrator Agent | Receives the user's task; plans subtasks; delegates to specialist agents; collects and assembles results | A2A delegation to specialists | Task planner; memory store |
| Research Specialist | Finds and summarizes relevant sources from academic databases and the web | A2A (receives task from Orchestrator); MCP tool calls to retrieve documents | Semantic Scholar MCP; web search MCP |
| Analysis Specialist | Processes and interprets research findings; performs calculations or data transformations | A2A (receives task from Orchestrator); MCP tool calls to run code | Code execution MCP; data analysis MCP |
| Writer Specialist | Drafts the final document from the assembled analysis and research | A2A (receives task from Orchestrator); reads from shared blackboard where prior agents wrote results | Document MCP; shared context store |

### Critical Thinking Questions

**Question 7.**  The A2A trust boundary rule states that a sub-agent cannot have *more* permissions than its spawning agent (which in turn cannot exceed the permissions of the user who authorized it).  Why is this rule necessary?  Describe a specific attack or failure mode that would be possible if sub-agents could acquire additional permissions not granted to the original user.

[[___ Your answer here ___]]

*Hint:* Imagine a user grants an orchestrator "read-only" access to their files.  If that orchestrator could delegate to a sub-agent with "read-write" permissions, what could a malicious or buggy sub-agent do that the user never authorized?  Consider that sub-agents might themselves delegate further; how far could permissions escalate without this rule?

**Question 8.**  When Agent A receives a message claiming to be from "Agent B, Research Specialist," how does Agent A know that the message really comes from the legitimate Agent B and not from a malicious actor impersonating it?  Describe at least two mechanisms (one cryptographic and one architectural) that could provide this assurance.

[[___ Your answer here ___]]

*Hint:* For the cryptographic mechanism, think about how websites prove their identity (TLS certificates, digital signatures).  For the architectural mechanism, think about whether there is a trusted intermediary (like the orchestrator itself) that controls which agents are even allowed to communicate in the system.

**Question 9.**  Agent C is writing a long document section to a shared workspace.  Midway through the write operation, Agent C crashes (network failure, resource exhaustion, or model error).  The shared workspace now contains a partial write: some sections are written, some are absent, and one section ends mid-sentence.  What problems does this cause for the other agents, and describe a protocol (using concepts from Model 2) that would ensure the shared workspace is always in a consistent state even if an agent crashes mid-write.

[[___ Your answer here ___]]

*Hint:* What do the other agents see when they read the workspace?  Can they tell the difference between "Agent C finished" and "Agent C crashed"?  Look back at the two-phase commit idea from Question 6: how could you apply the same principle to writing a document section?  What would "commit" and "abort" look like here?

---

## Exercises

**Exercise 1.**  Design a shared blackboard schema in JSON for a three-agent report-writing pipeline with a **Researcher**, an **Analyst**, and an **Editor**.  Your schema must include: (a) a task status field for each agent, (b) the content each agent produces, (c) a version number for optimistic concurrency control, and (d) a field for inter-agent notes or flags.  Write the JSON structure with example values and annotate each field with a comment explaining its purpose.

*What to do:* Draft a JSON object that all three agents would share.  Every agent reads the whole document and writes only to its own designated fields.  Include at least one field that a downstream agent uses to know whether an upstream agent has finished.

*Starter hint:* The JSON schema below shows a complete example; notice how the `version` field enables optimistic concurrency (an agent can detect a conflict by checking whether the version changed since it last read), and how the `lock_holder` field provides mutual exclusion for writes:

```json
{
  "version": 3,
  "agents": {
    "researcher": {
      "status": "done",           // "pending" | "in_progress" | "done" | "error"
      "output": "Found 12 papers on...",
      "notes": ""
    },
    "analyst": {
      "status": "in_progress",
      "output": "",
      "notes": "Waiting on researcher"
    },
    "editor": {
      "status": "pending",
      "output": "",
      "notes": ""
    }
  },
  "lock_holder": null             // null means no agent holds the write lock right now
}
```

*You've succeeded when:* The schema makes it possible for the Editor to check whether both the Researcher and Analyst are done before it starts, and makes it impossible (by convention) for two agents to write at the same time.

[[___ Your explanation here ___]]

**Exercise 2.**  Implement a naive "turn-taking" protocol in pseudocode that prevents the race condition from Model 2.  Your protocol should allow the three agents from Exercise 1 to take turns writing to the shared blackboard, ensuring that no two agents write simultaneously.  Include: (a) how an agent requests the turn, (b) how it is granted, (c) how it is released, and (d) what happens if an agent holding the turn crashes.

*What to do:* Write pseudocode (plain English structured like code) that an individual agent would follow before and after every write operation.  Think about the crash case carefully: what is the mechanism that prevents the lock from being held forever?

*Starter hint:* The pseudocode below implements a mutex using atomic compare-and-set; read the crash-handling comment at the bottom carefully, because it addresses the most dangerous failure mode (an agent dies while holding the lock and blocks everyone else forever):

```
function write_to_blackboard(agent_id, field, value):
    # Step 1: acquire the lock
    loop until lock acquired:
        result = atomic_set_if_null("lock_holder", agent_id)
        if result == "success":
            break
        wait(0.5 seconds)  # back off before retrying

    # Step 2: perform the write
    blackboard[field] = value
    increment blackboard["version"]

    # Step 3: release the lock
    blackboard["lock_holder"] = null

    # Crash handling: set a lock_expiry timestamp when acquiring;
    # any agent may steal an expired lock from a crashed holder
```

*You've succeeded when:* Your protocol prevents two agents from writing at the same time and includes a mechanism so a crashed agent does not block the others forever.

[[___ Your explanation here ___]]

**Exercise 3.**  In class, we discussed the "Orchestrator to Specialist" agent pattern.  Map this pattern to *either* the message-passing primitive *or* the shared blackboard primitive from Model 1 (choose one).  Justify your choice: explain why the pattern maps more naturally to your chosen primitive and identify one limitation of that primitive in this context that would push you to consider the other option.

*What to do:* Pick one primitive and draw (or describe) the flow of information in an Orchestrator-Specialist system using only that primitive.  Then honestly identify one scenario where your chosen primitive fails and the other would handle it better.

*Starter hint:* Consider: does the Orchestrator need to wait for each Specialist's response before delegating the next task?  Or can it fire off all delegations at once and collect results later?  Your answer should shape which primitive fits better.

*You've succeeded when:* You have named a specific, concrete limitation (not just "it can be slower") and explained exactly which aspect of the Orchestrator-Specialist pattern that limitation affects.

[[___ Your answer here ___]]

---

## Reflection Prompt

Distributed systems researchers spent decades (from Lamport's work in the 1970s through the CAP theorem debates of the 2000s) developing protocols for coordination, consistency, and fault tolerance in networked systems.  Multi-agent AI systems face structurally similar problems: concurrent access, partial failures, and the need for consistent shared state.

**Personal level:** Think about a group project you have worked on with other people.  Did you encounter any of the coordination problems from today: race conditions in who was editing the shared document, deadlocks waiting for someone else to respond?  How did your team resolve them, and what "protocol" did you end up following?

**Technical level:** What can the AI agent field learn directly from distributed systems research, and what is new about multi-agent LLM systems that has no clear parallel in classical distributed computing?  (Consider: classical distributed nodes execute deterministic code; LLM agents produce probabilistic outputs.  How does that change coordination?)

**Societal level:** Multi-agent systems are increasingly making decisions that affect real people: approving loans, routing emergency services, flagging content.  If a race condition or consensus failure causes an incorrect outcome, who is responsible?  How should accountability be assigned when the failure is an emergent property of agent interaction rather than a bug in any single agent?

Write a combined reflection of 150-250 words addressing at least two of the three levels.  The Reflector should be prepared to share one specific distributed systems concept the team thinks is most directly applicable to multi-agent LLMs.

[[___ Your reflection here ___]]

---

-> Coming Up Next: In the next activity, we look inside the agents themselves: specifically at how we can explain *why* an agent made the decision it did, and why that turns out to be much harder than it sounds.

---

## Further Reading

- FIPA ACL (Foundation for Intelligent Physical Agents Agent Communication Language) Specification.  Available at: http://www.fipa.org/specs/fipa00061/
- Google.  (2025).  "Agent-to-Agent (A2A) Protocol."  *Google Developers Blog*. https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
- Anthropic.  (2024).  "Model Context Protocol (MCP) Documentation." https://modelcontextprotocol.io/
- Lamport, L. (1978).  "Time, Clocks, and the Ordering of Events in a Distributed System."  *Communications of the ACM*, 21(7), 558-565.
- Gray, J., and Reuter, A. (1992).  *Transaction Processing: Concepts and Techniques*.  Morgan Kaufmann.  [Chapter on two-phase commit]
- Brewer, E. A. (2000).  "Towards Robust Distributed Systems."  *PODC Keynote*.  [CAP theorem]
