# Multi-Agent Communication: Protocols, Shared State, and Coordination

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multiagentprotocols.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

**CS357: Foundations of Artificial Intelligence / Agentic AI**
Ursinus College

---

## POGIL Roles

In this activity, your team will work together using the following roles. Rotate roles with each new activity.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the team on task and on time; ensures everyone contributes; calls for consensus before moving on |
| **Recorder** | Writes down the team's agreed answers; manages the shared document or whiteboard |
| **Presenter** | Speaks for the team during class discussion; summarizes findings to the class |
| **Reflector** | Monitors team process; notes what is working and what is not; leads the Reflection section |

> Before starting, confirm your roles aloud. If your team has fewer than 4 members, one person may take two roles (e.g., Manager + Reflector).

---

## Model 1: How Agents Communicate

When multiple agents collaborate on a task, they must exchange information. There is no single correct way to do this — the right choice depends on the task structure, how frequently agents need to coordinate, and what kinds of failures must be tolerated.

Three fundamental communication primitives appear across multi-agent frameworks:

| Primitive | How It Works | Best For | Failure Mode | Example in Course Tools |
|-----------|-------------|----------|--------------|------------------------|
| **Message passing** | Agent A sends a structured message directly to Agent B; B reads it and responds. Common standards: FIPA ACL (formal performatives), JSON-RPC (function-call style), HTTP REST. | Sequential pipelines; tasks with clear handoffs; when a response is needed before continuing | Message lost in transit; receiver crashes before reading; malformed message schema | Anthropic A2A agent-to-agent calls; MCP tool request/response |
| **Shared blackboard** | All agents read from and write to a common state object (e.g., a JSON document, database, or file). No direct agent-to-agent communication — they communicate via the shared state. | Parallel tasks where multiple agents contribute pieces; stigmergic coordination (agents react to what they see in the environment) | Race conditions when multiple agents write simultaneously; stale reads; one agent overwrites another's work | Shared tool-call memory object; Anthropic shared context window |
| **Event streaming** | Agents emit events to a bus or stream; other agents subscribe to event types they care about. No direct coupling between producer and consumer. | Loose coupling; broadcast notifications; reactive pipelines where agent B acts when agent A finishes | Events delivered out of order; subscriber misses events if not connected; event schema mismatches | Server-Sent Events in streaming tool responses; Kafka-style agent coordination |

### Critical Thinking Questions

**Question 1.** In a multi-agent system where three agents all have write access to the same JSON document (shared blackboard), what can go wrong if two agents try to update the same field at the same time? Describe the problem concretely — what state does the document end up in, and how does that compare to what either agent intended?

[[___ Your answer here ___]]

**Question 2.** FIPA ACL messages include a **performative** field that specifies the communicative intent of the message — for example: `inform` (I am telling you a fact), `request` (I am asking you to do something), `propose` (I am suggesting a deal), `agree`, `refuse`, `query-if`. What does this add over sending raw JSON? Give one example where knowing the performative changes how the receiving agent should respond.

[[___ Your answer here ___]]

**Question 3.** A research pipeline has three agents: a searcher that queries a database, an analyst that processes results, and a writer that drafts a report. Under what circumstances would **event streaming** be a better choice than direct message passing between these agents? Under what circumstances would message passing be the better choice? Identify the trade-off.

[[___ Your answer here ___]]

---

## Model 2: Coordination Problems

Multi-agent systems inherit the coordination problems of distributed computing, plus new ones specific to LLM agents. The four most important coordination problems are:

| Problem | Description | Example with Agents | Prevention Strategy |
|---------|-------------|--------------------|--------------------|
| **Race condition** | Two agents read shared state, both decide to act based on what they read, both write — but the second write overwrites the first, or both take an action that should only happen once | Agent A and Agent B both read a task queue, both claim task #7 as "in progress," and both execute it; task runs twice | Atomic compare-and-swap; locking; task queue with acknowledgment; optimistic concurrency with version numbers |
| **Deadlock** | Agent A is waiting for Agent B to finish before it can proceed; Agent B is waiting for Agent A. Neither can move forward. | Agent A holds a database lock and is waiting for Agent B to release a file lock; Agent B holds the file lock and is waiting for Agent A to release the database lock | Lock ordering (always acquire locks in the same order); timeouts with retry; lock-free designs; leader arbitration |
| **Priority inversion** | A high-priority agent is blocked by a low-priority agent holding a resource the high-priority agent needs | Critical summary agent is blocked waiting for a low-priority formatting agent to finish writing to the shared document | Priority inheritance; preemption; avoiding shared resources between agents of different priorities |
| **Consensus failure** | Agents must agree on a value or decision but cannot reach agreement; no majority or quorum forms | Three analyst agents produce three different numerical summaries of the same data; orchestrator cannot determine which to use | Quorum protocols (2-of-3 agreement required); designated tiebreaker; confidence-weighted voting; human-in-the-loop for unresolved conflicts |

Classic distributed systems solutions — developed over decades for databases and networked systems — apply directly to agents:

- **Mutex/lock**: only one agent may write a shared resource at a time; others wait
- **Optimistic concurrency**: agents write freely, but include a version number; if the version has changed since they read, the write is rejected and they must re-read and retry
- **Leader election**: one agent is designated coordinator; others send it requests rather than acting directly on shared state
- **Vector clocks**: each message carries a logical timestamp that captures which events preceded it, allowing receivers to determine the causal order of events even without synchronized clocks

### Critical Thinking Questions

**Question 4.** Two research agents are both querying the same paper database. Agent A queries for "machine learning + climate" and Agent B queries for "deep learning + weather." Both find paper P, which is relevant to both queries. Both agents independently decide to add paper P to a shared "relevant papers" list. Describe specifically how a race condition could produce an incorrect final state of the list, and what that incorrect state might look like.

[[___ Your answer here ___]]

**Question 5.** You need to implement a mutex so that only one agent at a time can update a shared JSON document. The agents communicate over HTTP and do not share memory. Describe, in concrete steps, how you would implement this mutex. (Hint: consider what a "lock file" or "lock key" in a database would look like, and how an agent would acquire and release it.)

[[___ Your answer here ___]]

**Question 6.** A two-phase commit protocol (2PC) is used in distributed databases to ensure that either all nodes commit a transaction or none do. Describe the "agent equivalent" of 2PC: a protocol where a group of agents must either all take an action or all abort, with no partial execution. What would the two phases look like, and who would play the role of the "coordinator"?

[[___ Your answer here ___]]

---

Three agents are collaborating on a report. Agent A finishes writing its section and writes the string `"DONE"` to a shared status file to signal completion. Agent B reads the status file before Agent A writes, sees nothing (or sees the old status), concludes the file is empty, and begins writing its own content — overwriting Agent A's completed section. This scenario is best described as:

- ( ) A deadlock, because both agents are waiting for each other
- (x) A race condition caused by missing synchronization between the read and write operations
- ( ) A consensus failure, because the agents disagree on the content of the report
- ( ) An example of priority inversion, because Agent B executed before Agent A's higher-priority write completed

---

## Model 3: The Anthropic Agent-to-Agent (A2A) and MCP Standards

As multi-agent systems move from research prototypes to production, the field has developed emerging standards for how agents should discover, delegate to, and communicate with each other.

**The A2A (Agent-to-Agent) Protocol** addresses three core needs:

1. **Discovery**: An agent advertises its capabilities in a machine-readable format (its "agent card"), allowing an orchestrator to identify which specialist agent to delegate to for a given subtask.
2. **Delegation**: Agent A (the orchestrator) spawns Agent B (a specialist) to handle a subtask, passing it the necessary context. Crucially, Agent B operates in its own context window — it does not automatically see everything Agent A knows.
3. **Trust boundaries**: Agent B cannot exceed the permissions of the user who authorized Agent A. If the user authorized "read-only access to documents," Agent B cannot acquire write access — even if Agent B's own system prompt would otherwise allow it. This principle prevents privilege escalation through agent delegation.

**MCP (Model Context Protocol)** serves as the standardized tool interface: agents use MCP to call tools (file systems, databases, APIs, other services) in a consistent, discoverable format. Multi-agent systems can compose MCP servers — one agent's tools can include calling another agent that exposes itself as an MCP server.

**Example pipeline (described as a table):**

| Component | Role | Communicates Via | Tools Used |
|-----------|------|-----------------|------------|
| Orchestrator Agent | Receives user task; plans subtasks; delegates to specialists; collects results | A2A delegation to specialists | Task planner; memory store |
| Research Specialist | Finds and summarizes relevant sources | A2A (receives task from Orchestrator); MCP tool calls | Semantic Scholar MCP; web search MCP |
| Analysis Specialist | Processes and interprets research findings | A2A (receives task from Orchestrator); MCP tool calls | Code execution MCP; data analysis MCP |
| Writer Specialist | Drafts the final document | A2A (receives task from Orchestrator); reads from shared blackboard | Document MCP; shared context store |

### Critical Thinking Questions

**Question 7.** The A2A trust boundary rule states that a sub-agent cannot have *more* permissions than its spawning agent (which in turn cannot exceed the permissions of the user who authorized it). Why is this rule necessary? Describe a specific attack or failure mode that would be possible if sub-agents could acquire additional permissions not granted to the original user.

[[___ Your answer here ___]]

**Question 8.** When Agent A receives a message claiming to be from "Agent B — Research Specialist," how does Agent A know that the message genuinely comes from the legitimate Agent B and not from a malicious actor impersonating it? Describe at least two mechanisms — one cryptographic and one architectural — that could provide this assurance.

[[___ Your answer here ___]]

**Question 9.** Agent C is writing a long document section to a shared workspace. Midway through the write operation, Agent C crashes (network failure, resource exhaustion, or model error). The shared workspace now contains a partial write: some sections are written, some are absent, and one section ends mid-sentence. What problems does this cause for the other agents, and describe a protocol (using concepts from Model 2) that would ensure the shared workspace is always in a consistent state even if an agent crashes mid-write.

[[___ Your answer here ___]]

---

## Exercises

**Exercise 1.** Design a shared blackboard schema in JSON for a three-agent report-writing pipeline with a **Researcher**, an **Analyst**, and an **Editor**. Your schema must include: (a) a task status field for each agent, (b) the content each agent produces, (c) a version number for optimistic concurrency control, and (d) a field for inter-agent notes or flags. Write the JSON structure with example values and annotate each field with a comment explaining its purpose.

```json
{
  // Your schema here
}
```

[[___ Your explanation here ___]]

**Exercise 2.** Implement a naive "turn-taking" protocol in pseudocode that prevents the race condition from Model 2. Your protocol should allow the three agents from Exercise 1 to take turns writing to the shared blackboard, ensuring that no two agents write simultaneously. Include: (a) how an agent requests the turn, (b) how it is granted, (c) how it is released, and (d) what happens if an agent holding the turn crashes.

```
// Your pseudocode here
```

[[___ Your explanation here ___]]

**Exercise 3.** In class, we discussed the "Orchestrator to Specialist" agent pattern. Map this pattern to *either* the message-passing primitive *or* the shared blackboard primitive from Model 1 (choose one). Justify your choice: explain why the pattern maps more naturally to your chosen primitive and identify one limitation of that primitive in this context that would push you to consider the other option.

[[___ Your answer here ___]]

---

## Reflection Prompt

Distributed systems researchers spent decades — from Lamport's work in the 1970s through the CAP theorem debates of the 2000s — developing protocols for coordination, consistency, and fault tolerance in networked systems. Multi-agent AI systems face structurally similar problems: concurrent access, partial failures, and the need for consistent shared state.

What can the AI agent field learn directly from distributed systems research, and what is genuinely new about multi-agent LLM systems that has no clear parallel in classical distributed computing? Write a personal reflection of 150–250 words. The Reflector should be prepared to share one specific distributed systems concept the team thinks is most directly applicable.

[[___ Your reflection here ___]]

---

## Further Reading

- FIPA ACL (Foundation for Intelligent Physical Agents Agent Communication Language) Specification. Available at: http://www.fipa.org/specs/fipa00061/
- Google. (2025). "Agent-to-Agent (A2A) Protocol." *Google Developers Blog*. https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/
- Anthropic. (2024). "Model Context Protocol (MCP) Documentation." https://modelcontextprotocol.io/
- Lamport, L. (1978). "Time, Clocks, and the Ordering of Events in a Distributed System." *Communications of the ACM*, 21(7), 558–565.
- Gray, J., and Reuter, A. (1992). *Transaction Processing: Concepts and Techniques*. Morgan Kaufmann. [Chapter on two-phase commit]
- Brewer, E. A. (2000). "Towards Robust Distributed Systems." *PODC Keynote*. [CAP theorem]
