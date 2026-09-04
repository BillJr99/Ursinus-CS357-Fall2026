<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-observability.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-observability.md

import: https://raw.githubusercontent.com/LiaTemplates/Pyodide/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Observability, Traceability, and Handoff Protocols

Last session, in *How I AI*, you built a vault, a charter, and a `.ai/` directory so that one agent could stop and another could pick up the work.  Today you learn the three properties that make that safe, and then you write them down as a protocol: a skill an agent must follow when it starts, when it stops, when it restarts, and when it hands work to another agent through a repository or a shared folder.  You leave with a `SKILL.md` draft and a checklist.  The *Design Your Agent System* written assignment, introduced next session, requires exactly that protocol.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board and keeps the team's draft protocol; the Presenter reads one rule of it aloud at report-out; the Reflector notes where the team disagreed about what an agent must write down before it stops.  After class, answer the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Small context principle** | Each agent call gets the minimum context sufficient for its current decision: standing instructions, a compact state summary, the latest turn, and facts fetched on demand | Model 1, where a 30-step history costs about 200 times what step 1 cost |
| **External memory** | Project state that lives in files outside the context window, so it survives the session, the tool, and the model | `.ai/SESSION.md`, a trace file, a GitHub issue |
| **Observability** | Being able to see what the agent did, from the outside, after the fact | The JSON-lines trace written by the Code Cell |
| **Log** | One timestamped event with structured fields | `{"step": 1, "phase": "act", "tool_name": "search"}` |
| **Trace** | The causally linked chain of events for one request or task, tied together by a shared `trace_id` | Model 2, six lines that share `trace_id` `t-77b0` |
| **Traceability** | Being able to answer, weeks later, *why* something is the way it is: which rule allowed it, which task it served, which goal that task served | The `rule` field in the trace, and the four-link chain in Section 4 |
| **Handoff** | A deliberate stop in which an agent writes down enough state that a different agent can continue safely | The Next Safe Action at the end of a `SESSION.md` entry |
| **Durable medium** | Something outside both agents that survives either of them crashing, through which one agent hands work to another | A GitHub issue and pull request, or `handoff/inbox/` and `handoff/done/` in a shared folder |
| **Claim** | A mark, visible through the medium alone, that says one agent has taken an item and others should leave it | `claimed_by` and `claimed_at` in the item, or an assignee on the issue |
| **Next Safe Action** | The one step a brand-new agent could take next without breaking anything | The last line of every session entry |

---

### Before You Start

**You need:** your `cs357-work` repository from *How I AI*, with its `.ai/` directory, and the two course templates linked in Part III.  There is nothing to install today; the Code Cell runs in this page.

**Due today:** the [Tools and MCP lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/ToolsMCP).  Nothing in today's session depends on it, so finish it before you leave rather than during Part I.

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.

| Minutes | What we do |
|---|---|
| 0-12 | Part I, why the small context principle forces external memory |
| 12-35 | Part II, observability and traceability: logs, traces, and reading one |
| 35-65 | Part III, handoff protocols, and the `SKILL.md` written together |
| 65-70 | Part IV, one exercise chosen by the team |
| 70-75 | Report-out |

---
# Part I: Why the Small Context Principle Forces External Memory

## 1.  Three Forces Against Long Contexts

Giving an agent unlimited memory hurts it in three separate ways, and each one pushes state out of the context window and into files.

**Compute.**  Attention, the mechanism that lets a transformer relate any token to any other token in context, costs $O(n^2)$ in context length.  An agent that appends every thought and observation pays quadratically for its own history.  In concrete terms: if step 1 processes 340 tokens and step 31 processes 4,840 tokens, step 31's attention cost is $(4840/340)^2 \approx 202$ times higher.  On a laptop, you feel this in seconds per token.

**Attention quality.**  Models attend best to the edges of context (beginning and end) and worst to the middle, the "lost-in-the-middle" effect documented empirically by Liu et al. (2024).  Forty turns of history in the prompt put the critical instruction from turn 3 exactly where attention is weakest.

**Distraction.**  Irrelevant context is not neutral; it pulls the model's probability distribution toward off-task continuations.  An agent reasoning about step 12 does not benefit from the verbatim text of steps 1 through 11.  It benefits from a summary of decisions made and facts established.

**The principle.**  Each agent call should receive the minimum context sufficient for its current decision: its standing instructions, a compact state summary, the most recent turn, and retrieved facts on demand.  Everything else has to live somewhere the agent can read it back.  That somewhere is today's subject.  If state must leave the context window, the files it lands in have to be observable, traceable, and ready to hand off, because the next reader may be a different agent.

---

## Model 1: The Bloated Agent

An agent has run 30 steps.  Its prompt now contains: the system prompt (300 tokens), all 30 thought-action-observation triples at 150 tokens each (4,500 tokens total), and the current question (40 tokens).  Total: 4,840 tokens.

### Critical Thinking Questions

1.  Where in this prompt does the system prompt sit positionally, and what does the lost-in-the-middle effect predict about the agent's continued obedience to it?

   > *Hint: The system prompt is at the very beginning (tokens 1-300).  The current question is at the very end.  The 30 historical triples are in the middle (tokens 301-4,800).  The lost-in-the-middle effect says attention is strongest at the beginning and end and weakest in the middle.  So which parts of the prompt does the model "read most carefully"?  What does that imply for the 30 historical triples?*

2.  Which of the 30 triples does the *current* decision actually need?  Propose a rule for what to keep verbatim, what to summarize, and what to discard.

   > *Hint: Consider three categories of past steps: (a) the most recent 3-4 steps, which give immediate context; (b) steps that established a fact or decision still relevant now; (c) steps that were tried and failed, or were intermediate steps to a completed sub-task.  Which category needs verbatim text?  Which needs a bullet-point summary?  Which can be discarded entirely?*

3.  Estimate the cost ratio of step 31's attention computation relative to step 1's (treat prompt length as 4,840 versus 340 tokens).  Show the arithmetic.

   > *Hint: Attention cost scales as $n^2$. Step 1's cost is proportional to $340^2 = 115,600$. Step 31's cost is proportional to $4840^2 = 23,425,600$. Divide to get the ratio.  Does the answer surprise you?*

4.  Now suppose the agent stops after step 30 and a fresh agent with an empty context takes over at step 31.  Of the 4,500 tokens of history, what must be *written down* for the new agent to continue, and in what form?  Predict a token count for that file before you reach Part III, and check your prediction there.

---

## 2.  Four Types of Memory, and Which One Survives a Stop

Cognitive science names four memory systems, and agent designers use the same names because each maps onto a storage mechanism.

| Memory type | What it stores | Where it lives | How it fails | Survives a stop? |
|---|---|---|---|---|
| **Working** | The current conversation: system prompt, retrieved documents, tool results, reasoning so far | The context window, in GPU memory during inference | Exhausted when the token budget is exceeded; the oldest content is dropped or the request fails | No.  Gone when the session closes |
| **Episodic** | Records of specific past events with timestamps: what was said, what tool was called, what it returned | An external database, log file, or vector store indexed by session and time | Retrieval fails if events are not indexed; the log grows without bound if no retention policy is set | Yes, if it was written before the stop |
| **Semantic** | General facts and concept relationships, the encyclopedia the agent consults | Model weights, or a RAG vector store queried at run time | Stale after the world changes; retrieval misses when the query does not match the chunk | Yes; it was never inside the session |
| **Procedural** | How to do tasks: conventions, step-by-step approaches, formatting habits | Fine-tuned weights, or standing examples in the system prompt; in this course, a skill on disk | Catastrophic forgetting when retrained; a skill that no longer matches the tool | Yes, if it is a file |

The last column is the one today cares about.  Working memory is the only kind that dies at a stop, so a handoff is the act of copying what matters out of working memory into episodic memory (the session log and the trace) and into procedural memory (the skill) before the window closes.  Retrieval-Augmented Generation (RAG) is semantic memory fetched on demand; the session log is episodic memory read at start.

**Recap.**  Long contexts cost quadratically, bury instructions in the middle, and distract.  So state must leave the window, which means the files it lands in *are* the agent's memory, and a file can be read by anyone who comes next.

---
# Part II: Observability and Traceability

## 3.  Logs, Metrics, and Traces

Observability is built from three data types.  No one of them is enough alone.

| Pillar | What it captures | Best for | In our course |
|---|---|---|---|
| **Logs** | Discrete events with a timestamp, a severity level, and structured fields such as `finish_reason` or `query_hash` | Debugging one specific failure after the fact; auditing what the agent did at a given moment | One JSON line per loop phase, written by the Code Cell below |
| **Metrics** | Numbers aggregated over time: request rate, error rate, tokens per minute | Alerting when a threshold is crossed; spotting trends over hours or days | Counting `finish_reason=length` per hour to catch a runaway loop |
| **Traces** | Causally linked spans for one request: each has a parent, a start, an end, and attributes, all tied to one `trace_id` | Root-cause analysis across steps; finding which step took the time or produced the fault | Model 2, one task's six events read as a chain |

A metric says the error rate rose at 2:00 PM.  A log gives the exact message for one failing request.  A trace says which step in the pipeline caused it and how long each step took: in the tutorial's RAG example, the `llm_generate` span accounts for 1,710 of the request's 2,340 milliseconds, and nothing but a trace would show that.

A production agent is silently failing on approximately 8% of queries: users receive a response, but it is unhelpful or factually wrong.  There are currently no logs, metrics, or traces in place.  Which observability pillar would you add FIRST to diagnose this problem?

[( )] Metrics; aggregate rates tell you that 8% of requests failed but cannot tell you what went wrong in any specific request, so you still cannot diagnose the root cause
[( )] Traces; a span tree requires knowing in advance which steps to instrument; without first understanding the failure pattern from logs, you may instrument the wrong spans
[(X)] Logs; structured per-request logging of the input, model response, and finish reason gives you the raw evidence needed to identify patterns in the failures before you know what to measure
[( )] All three simultaneously; instrumenting all three at once is expensive and slow to implement; start with the cheapest source of raw evidence and add the others as needed

**What not to log.**  Storing raw prompt text as a span attribute can expose private user data to your tracing vendor, violate the Family Educational Rights and Privacy Act (FERPA) or the General Data Protection Regulation (GDPR), and generate storage costs that make traces unusable at scale.  Store identifiers and measurements (a hash of the query, token counts, `finish_reason`), not content.

---

## 4.  Traceability: Answering "Why Is It Like This?"

Observability answers *what happened*.  Traceability answers *why*, weeks later, when nobody remembers.  For an agent's work, "why" has four links, each stored in a different file:

1.  **The change.**  A commit, with its diff.  Answers: what exactly is different?
2.  **The session entry.**  The dated `.ai/SESSION.md` entry that describes that commit.  Answers: what was the agent trying to do, and what did it deliberately not do?
3.  **The task.**  The `.ai/CURRENT_TASK.md` milestone the entry served, or the GitHub issue.  Answers: which piece of work was this part of?
4.  **The rule or goal.**  The `CHARTER.md` value, gate, or `AGENTS.md` rule that permitted or required the action.  Answers: what standing decision made this the right move?

You walked this chain in the traceability drill in *How I AI*, and you found the link that broke.  The trace closes the smallest gap: every logged action carries a `rule` field naming the rule that allowed it.  Then "why did the agent call `search` here?" is answered by the trace line, and "why is that the rule?" is answered by the charter.  A trace without a `rule` field tells you what happened.  A trace with one tells you what to change.

> **Common Misconception:** "Traceability is `git blame`."  `git blame` gives you link 1 and the name of whoever committed, which for an agent is nearly useless.  The other three links are documents somebody chose to write.  If nobody wrote them, the chain ends at the diff, and the only way to find out why is to ask the agent, whose context is gone.

---

## Code Cell: One Loop Step as a JSON-Lines Trace

The smallest useful trace is one line per phase of one loop step, in JSON Lines: one JSON object per line, so `grep` can search it and the file can be appended to forever.  Run the cell.  Then change `finish_reason` in `fake_llm` to `"length"` and run it again; the printed answer does not change, but the trace does, and that is the point.

```python
import json
import os
import time
import hashlib

TRACE_PATH = "trace.jsonl"
TRACE_ID = "t-4c1e"

if os.path.exists(TRACE_PATH):
    os.remove(TRACE_PATH)   # fresh file for the demo; a real agent only appends

def log_event(step, phase, **fields):
    """Append one JSON object per line.  Identifiers and measurements only."""
    record = {"ts": round(time.time(), 3), "trace_id": TRACE_ID,
              "step": step, "phase": phase}
    record.update(fields)
    with open(TRACE_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

def fake_llm(prompt):
    # Stands in for the model call.  Change finish_reason to "length" and rerun.
    return {"text": "CALL search(query='Ursinus College founding year')",
            "prompt_tokens": len(prompt.split()), "completion_tokens": 9,
            "finish_reason": "stop"}

def fake_tool(name, query):
    return "Ursinus College was founded in 1869 in Collegeville, Pennsylvania."

question = "When was Ursinus College founded?"
prompt = "You are a research agent.  Cite before you claim.\nQuestion: " + question
step = 1

# Perceive: what came in, hashed rather than stored
log_event(step, "perceive",
          query_hash=hashlib.sha1(question.encode()).hexdigest()[:8],
          prompt_tokens_est=len(prompt.split()))

# Plan: the model call, with its cost and how it ended
t0 = time.time()
reply = fake_llm(prompt)
log_event(step, "plan", model="hermes-3",
          latency_ms=int((time.time() - t0) * 1000),
          prompt_tokens=reply["prompt_tokens"],
          completion_tokens=reply["completion_tokens"],
          finish_reason=reply["finish_reason"],
          decision="tool_call", tool_name="search")

# Act: the tool call, and the rule that allowed it
observation = fake_tool("search", "Ursinus College founding year")
log_event(step, "act", tool_name="search", success=True,
          result_chars=len(observation),
          rule="CHARTER.md#cite-before-claim")

print("Answer:", observation)
print("\nTrace:")
print(open(TRACE_PATH).read())
```
@Pyodide.eval

Three habits are already in that cell.  The question is hashed rather than stored.  Every line shares the `trace_id`, so one step can be pulled back out of a file holding thousands.  And the `act` line names the rule that allowed the action, which is the fourth traceability link written at the moment it is cheapest to write.

---

## Model 2: Reading a Trace

An agent was asked to add a citation to a paragraph in `draft.md`.  Here are six lines from its `trace.jsonl`, all sharing one `trace_id`.

```json
{"ts": 1761062401.104, "trace_id": "t-77b0", "step": 1, "phase": "perceive", "query_hash": "9b1f3a02", "prompt_tokens_est": 412}
{"ts": 1761062403.877, "trace_id": "t-77b0", "step": 1, "phase": "plan", "model": "hermes-3", "latency_ms": 2773, "prompt_tokens": 412, "completion_tokens": 41, "finish_reason": "stop", "decision": "tool_call", "tool_name": "search"}
{"ts": 1761062404.061, "trace_id": "t-77b0", "step": 1, "phase": "act", "tool_name": "search", "success": true, "result_chars": 3120, "rule": "CHARTER.md#cite-before-claim"}
{"ts": 1761062404.090, "trace_id": "t-77b0", "step": 2, "phase": "perceive", "query_hash": "9b1f3a02", "prompt_tokens_est": 3690}
{"ts": 1761062412.512, "trace_id": "t-77b0", "step": 2, "phase": "plan", "model": "hermes-3", "latency_ms": 8422, "prompt_tokens": 3690, "completion_tokens": 512, "finish_reason": "length", "decision": "final_answer"}
{"ts": 1761062412.540, "trace_id": "t-77b0", "step": 2, "phase": "act", "action": "write_file", "path": "draft.md", "success": true, "result_chars": 2048}
```

The paragraph the agent wrote cites page 47 of a source that has 31 pages.

### Critical Thinking Questions

5.  Before reading on, predict which line explains the bad citation.  Then check: what does `"finish_reason": "length"` on step 2 mean, and why does a truncated plan produce a confident wrong page number rather than an error?

   > *Hint: The model hit its completion limit in the middle of an answer.  What was it in the middle of writing, and what did the agent do with the fragment?*

6.  `prompt_tokens_est` jumped from 412 to 3,690 between steps 1 and 2.  Using Part I, say where the extra 3,278 tokens came from and what the small context principle says to do about them before step 3.

7.  Step 2's `act` line has no `rule` field.  Which of the four traceability links is missing for the file write, and what question can nobody answer about `draft.md` as a result?

8.  The trace stores `query_hash` and `result_chars` but never the query or the search result.  Name one thing you can still diagnose from this trace and one thing you cannot, and say whether the trade is worth it for an agent that reads student documents.

9.  Write one metric you would compute over a day of these traces, with a threshold and a time window, that would have alerted someone before a reader found the page-47 citation.

   > *Hint: The metrics row of Section 3 names one.  What rate, and over what window?*

**Recap.**  A log is one event; a trace is the chain for one task; a metric is a number over many.  Traceability is the four links from a diff back to a rule, and the `rule` field in the trace is the cheapest link to keep.

---
# Part III: Handoff Protocols

## 5.  Start, Stop, Restart

The charter is stable law; the work changes hourly.  The `.ai/` directory holds the volatile state, one file per question a fresh agent must answer:

| File | The question it answers | How often it changes |
|---|---|---|
| `.ai/CONTEXT.md` | "What is this project, in one sentence, and what do I read first?" | Almost never |
| `.ai/CURRENT_TASK.md` | "What exactly is in flight: milestone, subtask, completion criteria, safe handoff point, next immediate action?" | Every task change |
| `.ai/SESSION.md` | "What just happened, what was verified, and what is the Next Safe Action?" | Continuously, a running log, *not* a final summary |
| `.ai/KNOWN_ISSUES.md` | "What verified defects and constraints should I not rediscover?" | As defects are confirmed |
| `.ai/FUTURE_WORK.md` | "Which good ideas are deliberately deferred so they stop competing with the milestone?" | Rarely |
| `.ai/AGENT_HANDOFF_KICKOFF.md` | "If I am a brand-new agent taking over right now, what is my first move?" | Static template |

Three rules make the directory trustworthy, and they are the start, stop, and restart of your protocol.

**On start**, the agent reads in a fixed order before doing anything else, then *states* the mission, the active task, and the Next Safe Action in its own words, and does not proceed until it has.  Restating is a comprehension gate: an agent that restates wrongly reveals the misunderstanding now, at the cost of one paragraph, instead of three commits later.  The course [kickoff template](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/ai/AGENT_HANDOFF_KICKOFF.md) is that instruction written out:

```text
You are taking over as the lead engineer for the <ProjectName> project from a
previous coding agent. You have no conversation history, and you do not need any:
the repository is the durable memory for this project.

Your authority is derived entirely from the project documentation.

Read these documents in order before doing anything else:
1. START_HERE.md
2. CHARTER.md
3. docs/ROADMAP.md
4. .ai/CURRENT_TASK.md
5. .ai/SESSION.md (at least the most recent entry)
6. The most recent Git commit or commits.

Then:
- State, in your own words, the mission, the active task, and the Next Safe Action
  recorded in .ai/SESSION.md. Do not proceed until you have stated them.
- Continue from the Next Safe Action. Prefer continuing existing work over
  reimplementing it.
- Follow the Development Workflow and Documentation Authority Rule in CHARTER.md.
- Before stopping for any reason, update .ai/SESSION.md, .ai/CURRENT_TASK.md, and
  any affected document under docs/.

At the end of this session, report: Summary / Files changed / Tests run /
Remaining blockers / Suggested next task.
```

**On stop**, for any reason (user interruption, session exhaustion, context exhaustion, quota exhaustion, or completion of the current task), the agent updates the handoff state: `.ai/SESSION.md`, `.ai/CURRENT_TASK.md`, and any affected document under `docs/`.  Every `SESSION.md` entry ends with a Next Safe Action, and superseded guidance is annotated in place ("superseded by the entry below"), never deleted.  The [session log template](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/ai/SESSION.md) fixes the entry's shape: Scope, In Progress, Completed (with the commands or commits that prove it), Runtime Facts, Validation, Next Safe Action.  Pair the stop rule with limit awareness: monitor visible or inferable session windows, context limits, quota windows, and time-based limits, and if any is approaching, stop new work and prepare a clean handoff before failure.

**On restart**, the agent is a stranger, even when it is the same model in the same tool an hour later.  It runs the start rule.  It reads the Reality Check table in `CURRENT_TASK.md`, which lists what is *not* done with the command, test, or artifact that proves each row, and it re-runs those commands before relying on them.  That table exists to fight the most common agent failure on long projects: quietly inflating "attempted" into "completed."

Every entry in `SESSION.md` ends with a "Next Safe Action" because:

[( )] LiaScript requires every log entry to end with an action item
[( )] It lets the project bill sessions accurately to the correct milestone
[(X)] A brand-new agent with no conversation history needs exactly one trustworthy, concrete first step, and the outgoing session is the only party that can name it
[( )] It prevents the session log from growing without bound

> **Common Misconception:** "Handoff notes are for when you switch agents."  The rule says *before stopping for any reason*, including finishing normally, because you cannot predict which stop becomes a swap: the session that completed its task on Friday becomes a handoff on Monday when the vendor has an outage and a different CLI picks up the work.  Every stop is treated as a potential handoff, so no stop is a bad one.

---

## 6.  Handing Work to Another Agent

A handoff to your own next session has one writer.  Real systems have two: a worker finishes a task and a reviewer picks it up, and the two never share a context window.  Everything one knows, the other reads from a **durable medium**, something outside both agents that survives either of them crashing.

| Medium | The channel is | A claim looks like | Done looks like |
|---|---|---|---|
| **GitHub** | Issues carry the task, pull requests carry the attempt, review comments carry the correction | The agent assigns itself the issue and opens a draft PR that references it | The PR is merged and the issue is closed with a comment naming the merge commit |
| **Shared folder (Dropbox-style, or `vault/handoff/` under the zone rules from *How I AI*)** | `handoff/inbox/` holds pending items, `handoff/done/` holds finished ones; no Git, no accounts, no network | The agent writes `claimed_by` and `claimed_at` into the item, or renames it to mark the claim | The item moves to `handoff/done/` with a result section appended |

The plain folder is not the lesser option.  Strip away the tooling and every medium is the same thing: a place to put work, a place to put finished work, and a rule about who may move what between them.  If your protocol only works because GitHub happens to serialize writes for you, you have not written a protocol.

**The claim protocol.**  Two agents look at the same pending item, and nothing stops both from starting it.  If both finish, you have paid twice for one task and may hold two contradictory results; if both write to the same place, one of them silently loses.  So the protocol must state, as a path and a condition rather than a sentiment:

1.  **How an agent claims an item** before working on it: moving or renaming the file, or writing a `claimed_by` and `claimed_at` field into it.  Whatever you choose, the claim must be visible to the *other* agent through the medium alone.
2.  **What a second agent does when it sees a claimed item.**  Skip it, wait, or take it?
3.  **What makes a claim stale.**  An agent that claims an item and then dies leaves the item claimed forever.  How long is too long, and who is allowed to break the claim?
4.  **What "done" looks like** in the medium, so the next agent can tell finished work from abandoned work.

On GitHub the review comment *is* the inter-agent message: one agent wrote code, another critiqued it in a durable place, and a third consumed the critique without any of them sharing a context window.  The PR thread is scoped to one change; the session journal spans every change.  A working system keeps both, and reads the journal first.

---

## Model 3: The Protocol as a `SKILL.md`

Write this together.  The Recorder types; the team supplies each rule as a path and a condition.  A skill is a directory containing a `SKILL.md` whose front matter carries `name` and `description`, as you built in the skills lab; the agent loads it when the description matches the task.  Here is the skeleton.  The bracketed parts are yours, and the numbers are what the checklist below cites.

```markdown
---
name: handoff-protocol
description: >
  Follow at the start, stop, and restart of every session, and whenever
  work is handed to another agent through the repository or the shared
  folder. Load before doing anything else in a session.
---

## On start

1. Read, in order: START_HERE.md, CHARTER.md, .ai/CURRENT_TASK.md,
   .ai/SESSION.md (last three entries), the most recent commit.
2. State the mission, the active task, and the Next Safe Action.
   Do not act until they are stated.
3. Re-run every command in the CURRENT_TASK.md Reality Check table.

## While working

4. Append one JSON line to .ai/trace.jsonl per loop phase: trace_id,
   step, phase, and on every act line the rule that allowed the action.
   Never write prompt text or retrieved content into the trace.

## On stop (any reason, including finishing)

5. Append a dated SESSION.md entry: Scope, In Progress, Completed
   (with proving commands), Runtime Facts, Validation, Next Safe Action.
6. Update the Reality Check in CURRENT_TASK.md. Never overwrite an entry.
7. Commit one logical change. Leave failing work uncommitted and named.

## Handing to another agent

8. Claim: [the path and field, e.g., set claimed_by and claimed_at in
   the item, or assign yourself the issue and open a draft PR].
9. On a claimed item: [skip, wait N minutes, or take; say which].
10. Stale claim: [claimed_at older than N with no write since; name who
    may break it].
11. Done: [move to handoff/done/ with a result section, or merge the PR
    and close the issue naming the commit].

## Limits

12. Watch context, quota, and time. When any is near, stop new work and
    run rules 5 through 7 before failure.
```

The *Design Your Agent System* assignment asks for this protocol, and this is the checklist it is read against.  Every row must be true of your protocol, and every row must cite the rule number that makes it true.

| Check | Rule that makes it true |
|---|---|
| A fresh agent can state mission, task, and Next Safe Action from files alone | |
| Every stop, including a normal finish, writes the handoff state | |
| Every action in the trace names the rule that allowed it | |
| No prompt text or retrieved content is stored in the trace | |
| A claim is visible to the other agent through the medium alone | |
| A stale claim can be broken, and the protocol says by whom and when | |
| Finished work is distinguishable from abandoned work in the medium | |
| Every not-done row in the Reality Check cites a command or artifact | |

### Critical Thinking Questions

10.  Rules 8 through 11 are blank.  Fill them for your team's chosen medium, then classify each as enforced by the medium (a file rename is atomic on one disk; GitHub will not merge the same PR twice) or advisory (both agents chose to obey).  Which of the four is the first to break if the second agent runs a different model?

11.  Rule 4 asks the agent to write its own trace.  What does a self-reported trace miss that an external observer (a wrapper around the tool call, or an OpenTelemetry span) would catch?  Name the one line in Model 2 you would trust least if the agent wrote it about itself.

12.  An agent claims an item, writes a wrong result to `done/`, and stops cleanly with a complete `SESSION.md` entry.  Which property failed: observability, traceability, or the handoff?  Which rule would have caught it, and if none would, write the rule.

13.  Estimate the tokens rule 1 costs on every start (five reads and a commit).  Compare that with the 4,500 tokens of history Model 1 was carrying, and with your prediction from question 4.  When does reading stop being cheaper than remembering?

   > *Hint: A session entry is a few hundred tokens.  The reads are bounded; the history was not.*

**Recap.**  Start by reading and restating; stop by writing the entry and the Next Safe Action; restart as a stranger who re-verifies.  Hand off through a medium with a claim, a staleness rule, and a visible "done."

---
# Part IV: Synthesis and Practice

## 7.  Exercises

1.  *Trace your own agent.*

   - *What to do*: Add `log_event` and its three calls to the agent loop from your Local Agent lab (any direction), run three steps, and read the trace back with `grep '"phase": "act"' .ai/trace.jsonl`.
   - *Starter hint*: The hardest field is `rule`.  If you cannot name the rule that allowed an action, that is a finding, not a formatting problem.
   - *You've succeeded when*: You have a trace of at least three steps and can point to one line that told you something the transcript did not.

2.  *The mid-session swap.*

   - *What to do*: An agent has been refactoring a parser for 40 minutes.  Its quota window expires in about 10 minutes.  Tests currently fail on 2 of 14 cases.  Put these scrambled steps in order: (A) commit one logical change containing the passing subset of the work, with documentation updates; (B) append a `SESSION.md` entry with scope, what was completed (with the test command output), what remains, the two failing cases by name, and a Next Safe Action; (C) stop starting new work the moment the limit is recognized as near; (D) update `CURRENT_TASK.md` so the Reality Check shows 12/14 passing with the verifying command and the next immediate action names the first failing case; (E) a new agent from a different vendor is started with the kickoff prompt, reads the funnel, and states the mission, active task, and Next Safe Action before proceeding.
   - *Starter hint*: Ask which document is the only one that distinguishes "12 passing because fixed" from "12 passing because the last two were never run."
   - *You've succeeded when*: Your order is defended, and you have named the single step that, if skipped, would most likely make the next agent duplicate or destroy work.

3.  *Cold start with the kickoff.*

   - *What to do*: Paste the kickoff template into a fresh session pointed at your `cs357-work` repository.  Record every question the agent asks before it states the mission, task, and Next Safe Action.
   - *Starter hint*: Each question is a missing sentence in one of the six files.  Write the sentence, not a longer prompt.
   - *You've succeeded when*: A second fresh session restates all three without asking anything.

4.  *The conflict.*

   - *What to do*: Point two sessions that do not share a context window at the same unclaimed item in your medium at the same time.  Report what actually happened.
   - *Starter hint*: There is no correct outcome.  Either your claim held, in which case say what mechanism held it, or you produced double work or a lost write, which is a passing result if you diagnose it: show the evidence, name the rule that would have prevented it, and say whether that rule is enforceable in your medium or only advisory.
   - *You've succeeded when*: You can say which of your rules the medium enforces and which hold only because both agents chose to follow them.

5.  *Price the protocol.*

   - *What to do*: Count the tokens (about three-quarters of a word each) in the five files rule 1 reads, and compare the total with the 4,840-token prompt in Model 1.
   - *Starter hint*: If your `.ai/` files are larger than the history they replace, the session log has stopped being a log and become a transcript.  Annotate and condense; do not delete.
   - *You've succeeded when*: You can state the per-start cost of your protocol in tokens and the condition under which it would exceed carrying the history.

---

## Reflection Prompt

*Personal*: Think of a time you picked up someone else's unfinished work, a group project, a shift, a document, with only what they left behind.  What did they leave that helped most, and what did you wish they had written down?  Compare that with the entry you would want an agent to leave you.

*Technical*: The trace in Model 2 was written by the agent about itself.  The session entry is also written by the agent about itself.  For a system you would actually run, which claims in those files would you insist be produced by something other than the model (a test runner, a wrapper, the filesystem), and what does that cost you?  Then rank the three properties for your project: if you could keep only two of observability, traceability, and a written handoff protocol, which goes, and what breaks first?

*Societal*: A complete trace of an agent's actions is also a complete record of what its user asked for, hashed or not.  Who else could want that file, under what circumstances, and does storing a hash instead of the text protect the user in the ways they would expect?  Compare the privacy risk of a trace you own against the risk of a vendor's dashboard you do not.

---

-> Coming Up Next: In *Design First: Plan Your Agent System Before You Build It* we plan a whole agent system on paper before building it.  Its written assignment now requires an observability, traceability, and handoff protocol, and the `SKILL.md` you drafted today is that protocol.  Bring the draft and the checklist.

## Further Reading

- Liu et al.  "Lost in the Middle: How Language Models Use Long Contexts."  *TACL* (2024).  The attention-quality force from Part I.
- OpenTelemetry Documentation: https://opentelemetry.io/docs/ and the OpenTelemetry Semantic Conventions for LLMs (GenAI): https://opentelemetry.io/docs/specs/semconv/gen-ai/.  The vendor-neutral standard for the spans in Section 3.
- Honeycomb.  *Observability Engineering.*  O'Reilly Media, 2022.
- Charity Majors.  "Observability: the Big Picture." https://charity.wtf/2020/03/03/observability-is-a-many-splendored-thing/
- Jaeger Distributed Tracing: https://www.jaegertracing.io/
- This course: [Agent Observability and Tracing](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Observability), the full three-pillars tutorial with the OpenTelemetry example; [Governing Coding Agents](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentGovernance), the case study the `.ai/` directory comes from; and the [agent templates](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/README.md), including [`AGENT_HANDOFF_KICKOFF.md`](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/ai/AGENT_HANDOFF_KICKOFF.md) and [`SESSION.md`](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/ai/SESSION.md).
- This course: [Local Agent, Direction 5: Build and Test Your Own Agent Skills](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/LocalAgent/Direction5), whose Part C is the handoff skill, the claim protocol, and the four handoff tests that exercise 4 borrows from.
- This course: [How I AI](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-howiai.md), where the handoff entry in Model 2 was first read, and [Memory and the Small Context Window Principle](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-memorycontext.md), where the arithmetic in Model 1 comes from.
