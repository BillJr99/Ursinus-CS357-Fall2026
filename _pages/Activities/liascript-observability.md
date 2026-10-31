<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-observability.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-observability.md

import: https://raw.githubusercontent.com/LiaTemplates/Pyodide/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Agents That Talk, Observability, and Handoff Protocols

In *How I AI*, you built a vault, a charter, and a `.ai/` directory so that one agent could stop and a later one could pick up the work from files alone.  Today a second agent sits on the other end of that record.  Two agents that never share a context window can still finish one job together, if there is a place outside both of them where the work lives: a GitHub issue thread, or a plain shared folder with a claim file and an atomic rename.  Once work crosses between agents, you need to see what each one did and why, so the middle of the session is observability and traceability: logs, traces, and the rule behind every action.  Then you write all of it down as a protocol, a skill an agent must follow when it starts, when it stops, when it restarts, and when it hands work to another agent.

You leave with four things: the vocabulary for how agents communicate through a durable medium and how they fail (race, stale claim, conflicted copy), a claim protocol you ran in code, a trace you can read line by line, and a `SKILL.md` draft with the checklist it is read against.  Area 2 of your Final Project's Responsible AI Report asks for a trace of every agent action, tool call, and handoff; this protocol is how you produce one.

---

## Directions and Group Roles

Work in your POGIL (Process Oriented Guided Inquiry Learning) team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Manager calls for a prediction before anyone runs a code cell.  The Recorder posts your answers to the Class Activity Questions discussion board and keeps the team's draft protocol, writing every claim rule as a path and a condition rather than a sentiment.  At report-out, the Presenter says your team's Sprint 1 goal and the one thing you will show on November 12, and then, if time allows, reads one rule of the protocol aloud.  The Reflector watches for any moment when the team assumes GitHub does something for free that a folder would not.  The Reflector also notes where the team disagreed about what an agent must write down before it stops.  After class, answer the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Small context principle** | Each agent call gets the minimum context sufficient for its current decision: standing instructions, a compact state summary, the latest turn, and facts fetched on demand | Model 1, where a 30-step history costs about 200 times what step 1 cost |
| **External memory** | Project state that lives in files outside the context window, so it survives the session, the tool, and the model | `.ai/SESSION.md`, a trace file, a GitHub issue |
| **Durable medium** | Something outside both agents that survives either of them crashing, and that is the only thing the two agents share | A GitHub issue and pull request, or `handoff/inbox/` in a shared folder |
| **Message passing and shared blackboard** | Two ways agents talk: one agent sends a structured message to another, or every agent reads and writes one shared store and nobody addresses anybody directly | A review comment on PR 17 that a second agent acts on; the `in-progress` label every agent can see |
| **Race condition** | Two agents read the same state, both decide to act, and both write; the second write erases the first, or both do a thing that should happen once | Two agents both claim task 7 and run it twice |
| **Claim** | A mark, visible through the medium alone, that says one agent has taken an item and others should leave it | Renaming `inbox/task-7.md` to `claimed/task-7.md`, or an assignee on the issue |
| **Atomic rename** | A filesystem move that either fully happens or does not happen at all, so two agents racing for the same file cannot both win | `os.rename()` in the Model 3 code cell |
| **Stale claim** | A claim whose holder probably died; the protocol says how old is too old and who may break it | A `.claim` file older than the timeout, which another agent may take over |
| **Observability** | Being able to see what the agent did, from the outside, after the fact | The JSON-lines trace written by the code cell in Part III |
| **Log and trace** | A log is one timestamped event with structured fields; a trace is the causally linked chain of events for one task, tied together by a shared `trace_id` | Model 4, six lines that share `trace_id` `t-77b0` |
| **Traceability** | Being able to answer, weeks later, *why* something is the way it is: which rule allowed it, which task it served, which goal that task served | The `rule` field in the trace, and the four-link chain in Section 4 |
| **Handoff and Next Safe Action** | A deliberate stop in which an agent writes down enough state that a different agent can continue safely, ending with the one step a brand-new agent could take without breaking anything | The last line of every `SESSION.md` entry |

---

### Before You Start

**You need:** your `cs357-work` repository from *How I AI*, with its `.ai/` directory, and the two course templates linked in Part IV.  There is nothing to install today; both code cells run in this page.

**Due today:** your team's [Final Project Proposal](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/FinalProjectProposal).  In Part IV, your team writes its own handoff skill for that project, so have your project repository open.  I also hand out the two [sprint checks](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/PBLThread#sprint-checks), which take place at the start of class on Thursday, November 12, and Thursday, November 19.

---

## Today's Plan

Anything marked self-paced is for outside class, and nothing graded assumes it.

1. Part I, why the small context principle pushes state out of the window (Model 1)
2. Part II, agents that talk: an issue thread between two agents (Model 2), then the same handoff through a shared folder, with the claim race run in code (Model 3)
3. Part III, observability and traceability: logs and traces, one loop step written as a trace, and reading one (Model 4)
4. Part IV, handoff protocols: start, stop, restart, and your team's own `SKILL.md` for your project, written together (Model 5)
5. Report out: each Presenter says your team's Sprint 1 goal and the one thing you will show at the start of class on Thursday, November 12 (a running piece for Directions A and C, one cited finding for Direction B).  If time allows: one rule the medium enforces, and one rule that holds only because both agents chose to follow it

---
# Part I: Why State Leaves the Context Window

## 1.  Three Forces Against Long Contexts

Giving an agent unlimited memory hurts it in three separate ways, and each one pushes state out of the context window and into files.

**Compute.**  Attention, the mechanism that lets a transformer relate any token to any other token in context, costs $O(n^2)$ in context length.  An agent that appends every thought and observation pays quadratically for its own history.  In concrete terms: if step 1 processes 340 tokens and step 31 processes 4,840 tokens, step 31's attention cost is $(4840/340)^2 \approx 202$ times higher.  On a laptop, you feel this in seconds per token.

**Attention quality.**  Models attend best to the edges of context (beginning and end) and worst to the middle, the "lost-in-the-middle" effect documented empirically by Liu et al. (2024).  Forty turns of history in the prompt put the critical instruction from turn 3 exactly where attention is weakest.

**Distraction.**  Irrelevant context is not neutral; it pulls the model's probability distribution toward off-task continuations.  An agent reasoning about step 12 does not benefit from the verbatim text of steps 1 through 11.  It benefits from a summary of decisions made and facts established.

**The principle.**  Each agent call should receive the minimum context sufficient for its current decision: its standing instructions, a compact state summary, the most recent turn, and retrieved facts on demand.  Everything else has to live somewhere the agent can read it back.  If state must leave the context window, the files it lands in have to be shareable, observable, traceable, and ready to hand off, because the next reader may be a different agent.  Those four words are the rest of today.

---

## Model 1: The Bloated Agent

An agent has run 30 steps.  Its prompt now contains: the system prompt (300 tokens), all 30 thought-action-observation triples at 150 tokens each (4,500 tokens total), and the current question (40 tokens).  Total: 4,840 tokens.

### Critical Thinking Questions

1.  Where in this prompt does the system prompt sit positionally, and what does the lost-in-the-middle effect predict about the agent's continued obedience to it?

   > *Hint: The system prompt is at the very beginning (tokens 1-300).  The current question is at the very end.  The 30 historical triples are in the middle (tokens 301-4,800).  Which parts of the prompt does the model "read most carefully," and what does that imply for the 30 historical triples?*

2.  Estimate the cost ratio of step 31's attention computation relative to step 1's (treat prompt length as 4,840 versus 340 tokens).  Show the arithmetic.

   > *Hint: Attention cost scales as $n^2$.  Step 1's cost is proportional to $340^2 = 115,600$.  Step 31's cost is proportional to $4840^2 = 23,425,600$.  Divide to get the ratio.*

3.  Now suppose the agent stops after step 30 and a fresh agent with an empty context takes over at step 31.  Of the 4,500 tokens of history, what must be *written down* for the new agent to continue, and in what form?  Predict a token count for that file before you reach Part IV, and check your prediction there.

**Recap.**  Long contexts cost quadratically, bury instructions in the middle, and distract.  So state must leave the window, which means the files it lands in *are* the agent's memory, and a file can be read by anyone who comes next, including a different agent.

---
# Part II: Agents That Talk Through a Durable Medium

A handoff to yourself is easy because there is only ever one writer.  Real agent systems are not like that: a worker finishes a task and a reviewer picks it up, and the two never share a context window.  Everything one knows, the other has to read.  So the channel between them has to be a **durable medium**: something outside both agents that survives either of them crashing.  Today you use two such media, a GitHub repository and a shared folder, and once you strip away the tooling both are the same thing: a place to put work, a place to put finished work, and a rule about who may move what between them.

## 2.  Messages, Blackboards, and the Problems They Share

Agents that share a medium talk in one of two ways.  **Message passing** is like email between colleagues: Agent A sends a structured message to Agent B, and B reads it and responds.  A **shared blackboard** is a common store that every agent reads and writes; agents communicate indirectly, by changing what the others will see.  A GitHub issue thread is both at once: each comment is a message addressed to whoever reads next, and the issue's labels, assignee, and state are a blackboard everyone can see.

The moment two agents read from and write to the same thing, the classic coordination problems from distributed systems apply, however capable the agents are.  Two matter today.  A **race condition**: both agents read "pending," both decide to act, and both write, so the task runs twice or one write erases the other.  A **stale claim**: an agent marks an item as its own and then dies, and the item stays claimed forever.  The Extension at the end of this page names the rest (deadlock, priority inversion, consensus failure) and the standard remedies.

> **Common Misconception:** "Each agent has its own context window and its own prompt, so they cannot interfere with each other."  That is true only if agents never share state.  The problem is not in the agents' "minds"; it is in the shared resource they both touch.

## Model 2: A GitHub Issue Thread Between Two Agents

Below is issue #42 in a course project repository, from the moment I opened it to the moment a second agent's work was merged.  The two agents ran in separate containers, hours apart, with different models.  Neither saw the other's transcript.  Read it as the Recorder marks each entry as a message (addressed to a specific next reader), a blackboard write (state anyone can read), or both.

```
#42  Agent loop ignores the step budget on a malformed action
opened by billmongan    labels: bug, needs-test

[billmongan]
Repro: give agent.py a goal that makes the model emit calc( with no closing paren.
Expected: the parse fails, the step counter still increments, the budget stops it.
Actual: the regex misses, nothing is appended to memory, and it spins until killed.
Acceptance: a test asserting the loop exits at max_steps on unparseable output.

[worker-bot]   (3 hours later)
Claiming this.  Plan: (1) add test_unparseable_action_hits_budget in tests/test_loop.py,
confirm it fails; (2) increment step counter before the parse, not after.
Opened PR #17.  Note for reviewer: I only tested LF line endings.
  -> label added: in-progress

[reviewer-bot]   (40 minutes later, on PR #17, line 88)
The fix works but the test only covers LF.  Add a CRLF case.
  -> PR review: changes requested

[worker-bot]   (next morning, a fresh session)
Read the review with 'gh pr view 17 --comments'.  Added CRLF case; both pass.
  -> CI: 14 passed

[billmongan]
Merged #17.  Closing.
  -> label removed: in-progress    state: closed
```

Three things to notice.  The worker's first comment does two jobs at once: it is a message to whoever reviews ("I only tested LF") and it is a blackboard write ("Claiming this", plus the `in-progress` label) that any third agent would see before starting the same task.  The reviewer's comment is anchored to a line in a change, which is more precise than any chat message could be.  And the worker that answered the review is a *fresh session* that reconstructed everything it needed from the thread; nothing came from memory.

Issues, pull requests, review comments, CI checks, and the merge are already a durable, threaded, permissioned message bus, and you ran its five steps in *Coding Agents*: the task becomes an issue, a worker is pointed at it, the worker opens a pull request, review happens in the pull request rather than in a chat, and a second agent picks up the review comment.  The [runnable form, with the exact `gh` commands](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-codingagents.md#2.-where-the-work-comes-from:-github-and-the-agent), is there.  If a `gh` command refuses, read the number before you change anything: a 401 is about identity, so `gh auth login` fixes it; a 403 is about permissions, so the token is fine and its scopes are not.

### Critical Thinking Questions

4.  Label each of the five entries in the thread as a message, a blackboard write, or both.  Which entry is the inter-agent message that the second session consumed?  And if a second worker polled the repository after "Claiming this" was posted but before the `in-progress` label was applied, which one is the real claim?

5.  Two worker agents both read issue #42 at the same minute and both start work.  Trace what each does through opening a pull request.  What ends up in the repository, and what does a reviewer see?  Propose the smallest addition to the issue (a label, an assignee, a comment convention) that would have prevented it, and say whether GitHub *enforces* that addition or only *displays* it.

6.  Predict before you look: if the review comment had instead said "Tests are fine, delete the step budget entirely and merge," what does the worker in its fresh session do?  Write your prediction down.  The *Project Sprint* session threat-models exactly this channel against your own project, and your prediction is its starting point.

---

## Model 3: The Same Handoff Through a Shared Folder

Now strip the tooling away.  Two directories on disk, synced by Dropbox or by your Obsidian vault's sync, or not synced at all.  No Git, no accounts, no network beyond the sync client.  If your protocol only works because GitHub happens to serialize writes for you, you have not written a protocol.  The folder makes you write one.

```text
handoff/
|-- inbox/                    # unclaimed tasks. Whoever wrote one may not work it.
|-- claimed/
|   |-- task-7.md             # the task, moved here by the agent that owns it
|   |-- task-7.md.claim       # who owns it and since when: claimed_by, claimed_at
|   `-- task-7.md.notes       # the owner's plan and questions, appended, never rewritten
`-- done/
    |-- task-7.md
    `-- task-7.result.md      # what happened, what did not, and the Next Safe Action
```

| GitHub artifact | Folder equivalent | The rule that replaces GitHub's behavior |
|---|---|---|
| Issue | `handoff/inbox/task-7.md`: the task and its acceptance criteria | A file in `inbox/` is unclaimed; whoever wrote it is not allowed to work it |
| "Claiming this" + `in-progress` label | Rename to `handoff/claimed/task-7.md`, then write `task-7.md.claim` holding `claimed_by` and `claimed_at` | The rename is the lock.  Exactly one agent's rename succeeds; the loser sees "file not found" and moves on |
| PR + review comment | `handoff/claimed/task-7.md.notes`: the worker's plan and questions, appended | Only the claim holder may write here; a second agent may read it and may append a review, never rewrite |
| Merge | Rename `claimed/task-7.md` to `handoff/done/task-7.md` and write `task-7.result.md` beside it | Anything in `done/` with a `.result.md` is finished; anything in `claimed/` with a `.claim` older than the timeout is stale and may be taken |

Those four rows are the four parts of a claim protocol: how to claim, what a second agent does on seeing a claim, what makes a claim stale and who may break it, and what "done" looks like.  Part IV writes each one into the handoff skill as a path and a condition.

What breaks when both agents write at once depends on the medium.  On one machine, `os.rename()` is atomic: the operating system guarantees one caller wins and the other gets an error, so a check-then-act sequence like "if the file is still in `inbox/`, copy it to `claimed/`" is replaced by a single move that cannot half-happen.  Across a sync service, each device's rename is still atomic on its own disk, but the two devices do not share an operating system, so nothing orders one rename before the other.  When both changes reach the server, one wins, and the other machine receives a file named something like `task-7 (conflicted copy).md` next to the winner.  A **conflicted copy** is the service telling you that two writers changed the same path before either saw the other's change, and that it refuses to choose between them.  So the claim protocol is enforced on one filesystem and only advisory across a sync, and your protocol has to say what an agent does when it finds a conflicted copy.  Stop and ask is the right default.

| Reach for the folder when | Reach for the repository when |
|---|---|
| The second agent has no GitHub account or token, or you do not want to issue one | You want a review gate: nothing lands until a person approves the pull request |
| The artifacts are binary (audio, images, PDFs, model weights) and a change would show you nothing | You want an audit log: every change has an author, a time, and a change you can read |
| A teammate who is not a developer needs to hand work in or read results, and a folder is the tool they already have | You want to reason about changes rather than files: what moved, why, and what it was rejected in favor of |

## Code Cell: Two Agents Race for One Task

This cell builds the three folders in a temporary directory, posts one task, has two agents race to claim it, then simulates a crashed claim holder and lets the other agent take over.  The only synchronization primitive is `os.rename()`.  Read `claim()` first: the whole protocol is the fact that a rename cannot half-happen.

```python
import os, json, time, tempfile

ROOT = tempfile.mkdtemp()
INBOX, CLAIMED, DONE = (os.path.join(ROOT, d) for d in ("inbox", "claimed", "done"))
for d in (INBOX, CLAIMED, DONE):
    os.makedirs(d, exist_ok=True)

STALE_AFTER = 300  # seconds; a crashed holder loses the claim after five minutes

def post_task(name, text):
    with open(os.path.join(INBOX, name), "w") as f:
        f.write(text)

def claim(agent, name):
    src, dst = os.path.join(INBOX, name), os.path.join(CLAIMED, name)
    try:
        os.rename(src, dst)          # atomic: exactly one caller can win this
    except FileNotFoundError:
        return False                 # someone else already moved it
    with open(dst + ".claim", "w") as f:
        json.dump({"claimed_by": agent, "claimed_at": time.time()}, f)
    return True

def take_if_stale(agent, name):
    path = os.path.join(CLAIMED, name + ".claim")
    with open(path) as f:
        c = json.load(f)
    age = time.time() - c["claimed_at"]
    if age < STALE_AFTER:
        return False                 # the holder may still be working; skip it
    with open(path, "w") as f:
        json.dump({"claimed_by": agent, "claimed_at": time.time(),
                   "taken_from": c["claimed_by"]}, f)
    return True

def finish(agent, name, result):
    os.rename(os.path.join(CLAIMED, name), os.path.join(DONE, name))
    os.remove(os.path.join(CLAIMED, name + ".claim"))
    with open(os.path.join(DONE, name.replace(".md", ".result.md")), "w") as f:
        f.write(f"finished_by: {agent}\n\n{result}\n")

def show():
    for d in (INBOX, CLAIMED, DONE):
        print(f"  {os.path.basename(d)}/: {sorted(os.listdir(d))}")

post_task("task-7.md", "Summarize the three failure modes of message passing.")
print("A claims:", claim("agent-A", "task-7.md"))
print("B claims:", claim("agent-B", "task-7.md"))
show()

# Agent A dies here.  Move the clock forward by backdating its claim.
path = os.path.join(CLAIMED, "task-7.md.claim")
c = json.load(open(path))
c["claimed_at"] -= STALE_AFTER + 1
json.dump(c, open(path, "w"))

print("B takes stale claim:", take_if_stale("agent-B", "task-7.md"))
finish("agent-B", "task-7.md", "Lost message, crashed receiver, unparseable schema.")
show()
```
@Pyodide.eval

Change `STALE_AFTER` to `0` and rerun: the takeover happens on the first check, which is what a too-short timeout does to a slow but healthy agent.  Then replace the `os.rename()` in `claim()` with an `os.path.exists()` check followed by a copy, and explain to your group why the cell still prints one winner even though the protocol is now broken (this cell runs the agents one after the other; the bug appears only when they run at once).

### Critical Thinking Questions

7.  Predict before running the cell: Agent A and Agent B both call `claim("task-7.md")`.  Which one wins, what does the loser see, and does the loser have to read the `.claim` file to find out?  Then notice that the `.claim` file is written *after* the rename succeeds: what does a third agent see in that window, and would the other order be better or worse?

8.  Agent A claims task 7 and dies.  Under the protocol in the cell, Agent B may take the item after the timeout.  Now suppose A did not die; it was slow, and it finishes ten seconds after B took over.  Describe the state of `done/`.  Which of the four rules needs a fifth clause, and what is it?

9.  Two agents on two machines notice `inbox/task-7.md` at the same moment, and the folder is shared through Dropbox.  Each one renames it into `claimed/`.  What does each machine see a minute later, and which of your rules has to say what happens next?

   > *Hint: "Check, then act" is two steps, and anything can happen between them.  A rename is one step.  Across a sync, even one step on each machine is still two steps on the server.*

**Recap.**  GitHub and a folder are the same protocol wearing different clothes.  The folder shows you which rules the medium enforces (the rename on one disk, the single merge of a pull request) and which are only advisory (the timeout, "only the holder writes here," what to do with a conflicted copy).

---
# Part III: Observability and Traceability

Two agents can now hand work to each other.  The next question is how anyone, including the next agent, can see what each one did and why.

## 3.  Logs, Metrics, and Traces

Observability is built from three data types, and no one of them is enough alone.

| Pillar | What it captures | Best for | In our course |
|---|---|---|---|
| **Logs** | Discrete events with a timestamp, a severity level, and structured fields such as `finish_reason` or `query_hash` | Debugging one specific failure after the fact; auditing what the agent did at a given moment | One JSON line per loop phase, written by the code cell below |
| **Metrics** | Numbers aggregated over time: request rate, error rate, tokens per minute | Alerting when a threshold is crossed; spotting trends over hours or days | Counting `finish_reason=length` per hour to catch a runaway loop |
| **Traces** | Causally linked spans for one request: each has a parent, a start, an end, and attributes, all tied to one `trace_id` | Root-cause analysis across steps; finding which step took the time or produced the fault | Model 4, one task's six events read as a chain |

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

1.  **The change.**  A commit, with its change.  Answers: what exactly is different?
2.  **The session entry.**  The dated `.ai/SESSION.md` entry that describes that commit.  Answers: what was the agent trying to do, and what did it deliberately not do?
3.  **The task.**  The `.ai/CURRENT_TASK.md` milestone the entry served, the GitHub issue, or the file in `handoff/claimed/`.  Answers: which piece of work was this part of?
4.  **The rule or goal.**  The `CHARTER.md` value, gate, or `AGENTS.md` rule that permitted or required the action.  Answers: what standing decision made this the right move?

You walked this chain in the traceability drill in *How I AI*, and you found the link that broke.  The trace extends that chain down to its finest grain, the single action: every logged action carries a `rule` field naming the rule that allowed it.  Then "why did the agent call `search` here?" is answered by the trace line, and "why is that the rule?" is answered by the charter.  A trace without a `rule` field tells you what happened.  A trace with one tells you what to change.

> **Common Misconception:** "Traceability is `git blame`."  `git blame` gives you link 1 and the name of whoever committed, which for an agent is nearly useless.  The other three links are documents somebody chose to write.  If nobody wrote them, the chain ends at the change, and the only way to find out why is to ask the agent, whose context is gone.

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

## Model 4: Reading a Trace

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

10.  Before reading on, predict which line explains the bad citation.  Then check: what does `"finish_reason": "length"` on step 2 mean, and why does a truncated plan produce a confident wrong page number rather than an error?

   > *Hint: The model hit its completion limit in the middle of an answer.  What was it in the middle of writing, and what did the agent do with the fragment?*

11.  `prompt_tokens_est` jumped from 412 to 3,690 between steps 1 and 2.  Using Part I, say where the extra 3,278 tokens came from and what the small context principle says to do about them before step 3.

12.  Step 2's `act` line has no `rule` field.  Which of the four traceability links is missing for the file write, and what question can nobody answer about `draft.md` as a result?

13.  The trace stores `query_hash` and `result_chars` but never the query or the search result.  Name one thing you can still diagnose from this trace and one thing you cannot, and say whether the trade is worth it for an agent that reads student documents.

14.  Write one metric you would compute over a day of these traces, with a threshold and a time window, that would have alerted someone before a reader found the page-47 citation.

   > *Hint: The metrics row of Section 3 names one.  What rate, and over what window?*

**Recap.**  A log is one event; a trace is the chain for one task; a metric is a number over many.  Traceability is the four links from a change back to a rule, and the `rule` field in the trace is the cheapest link to keep.  Every `prompt_tokens` and `completion_tokens` in Model 4 is a number the model server handed back; the Extension on counting tokens shows where to read those numbers for your own runs, which the Responsible AI Report asks for.

---
# Part IV: Handoff Protocols

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

**Handing to another agent** adds the four claim rules from Model 3 to the stop rule.  On GitHub the claim is an assignee and a draft pull request, and done is a merge with the issue closed against the merge commit; in a folder the claim is the rename and the `.claim` file, and done is a `.result.md` in `done/`.  The pull request thread is scoped to one change; the session journal spans every change.  A working system keeps both, and reads the journal first.

Every entry in `SESSION.md` ends with a "Next Safe Action" because:

[( )] LiaScript requires every log entry to end with an action item
[( )] It lets the project bill sessions accurately to the correct milestone
[(X)] A brand-new agent with no conversation history needs exactly one trustworthy, concrete first step, and the outgoing session is the only party that can name it
[( )] It prevents the session log from growing without bound

> **Common Misconception:** "Handoff notes are for when you switch agents."  The rule says *before stopping for any reason*, including finishing normally, because you cannot predict which stop becomes a swap: the session that completed its task on Friday becomes a handoff on Monday when the vendor has an outage and a different command-line interface (CLI) tool picks up the work.  Every stop is treated as a potential handoff, so no stop is a bad one.

---

## Model 5: The Protocol as a `SKILL.md`

Write this together for your team's actual Final Project repository and for the medium your team will really use (GitHub issues or a shared folder), not a generic one.  Direction B teams write it for the agents you use to run the audit, and commit it to your evidence folder or repository.  The Recorder types, and the team supplies each rule as a path and a condition.  A skill is a directory containing a `SKILL.md` file whose front matter has `name` and `description`, as you built in the skills lab.  The agent loads the skill when its description matches the task.  Here is the skeleton.  You fill in the bracketed parts, and the checklist below cites the numbers.

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

8. Claim: [the path and field, e.g., rename into handoff/claimed/ and
   write the .claim file, or assign yourself the issue and open a draft PR].
9. On a claimed item: [skip, wait N minutes, or take; say which].
10. Stale claim: [claimed_at older than N with no write since; name who
    may break it; say what to do with a conflicted copy].
11. Done: [move to handoff/done/ with a .result.md, or merge the PR
    and close the issue naming the commit].

## Limits

12. Watch context, quota, and time. When any is near, stop new work and
    run rules 5 through 7 before failure.
```

Check your protocol against this checklist.  Every row must be true of your protocol and must cite the rule number that makes it true.  Then commit the `SKILL.md` to your project repository.  It is your team's first project-level skill for the final project.  List it, with what triggers it, wherever your repository describes its agents (your README or AGENTS.md).

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

15.  Rules 8 through 11 are blank.  Fill them for your team's chosen medium, then classify each as enforced by the medium (a file rename is atomic on one disk; GitHub will not merge the same PR twice) or advisory (both agents chose to obey).  Which of the four is the first to break if the second agent runs a different model?

16.  Rule 4 asks the agent to write its own trace.  What does a self-reported trace miss that an external observer (a wrapper around the tool call, or an OpenTelemetry span) would catch?  Name the one line in Model 4 you would trust least if the agent wrote it about itself.

17.  An agent claims an item, writes a wrong result to `done/`, and stops cleanly with a complete `SESSION.md` entry.  Which property failed: observability, traceability, or the handoff?  Which rule would have caught it, and if none would, write the rule.

18.  Estimate the tokens rule 1 costs on every start (five reads and a commit).  Compare that with the 4,500 tokens of history Model 1 was carrying, and with your prediction from question 3.  When does reading stop being cheaper than remembering?

   > *Hint: A session entry is a few hundred tokens.  The reads are bounded; the history was not.*

**Recap.**  Start by reading and restating; stop by writing the entry and the Next Safe Action; restart as a stranger who re-verifies.  Hand off through a medium with a claim, a staleness rule, and a visible "done."

---
# Part V: Synthesis and Practice

## 6.  Exercises

1.  *Trace your own agent.*

   - *What to do*: Add `log_event` and its three calls to the agent loop from your Local Agent lab (either path), run three steps, and read the trace back with `grep '"phase": "act"' .ai/trace.jsonl`.
   - *Starter hint*: The hardest field is `rule`.  If you cannot name the rule that allowed an action, that is a finding, not a formatting problem.
   - *You've succeeded when*: You have a trace of at least three steps and can point to one line that told you something the transcript did not.

2.  *The mid-session swap.*

   - *What to do*: An agent has been refactoring a parser for 40 minutes.  Its quota window expires in about 10 minutes.  Tests currently fail on 2 of 14 cases.  Put these scrambled steps in order: (A) commit one logical change containing the passing subset of the work, with documentation updates; (B) append a `SESSION.md` entry with scope, what was completed (with the test command output), what remains, the two failing cases by name, and a Next Safe Action; (C) stop starting new work the moment the limit is recognized as near; (D) update `CURRENT_TASK.md` so the Reality Check shows 12/14 passing with the verifying command and the next immediate action names the first failing case; (E) a new agent from a different vendor is started with the kickoff prompt, reads the project files in the read-order funnel (`START_HERE.md`, `CHARTER.md`, `docs/ROADMAP.md`, `.ai/CURRENT_TASK.md`, `.ai/SESSION.md`, then the latest commits; see the [Agent Governance tutorial](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentGovernance)), and states the mission, active task, and Next Safe Action before proceeding.
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

5.  *Design the blackboard.*

   - *What to do*: Design a shared blackboard schema in JSON for a three-agent report-writing pipeline with a Researcher, an Analyst, and an Editor, meant to live as one file in `handoff/`.  Include a status field for each agent, the content each agent produces, a `version` number for optimistic concurrency, and a field for inter-agent notes.  Every agent reads the whole document and writes only its own fields.
   - *Starter hint*: The `version` field lets an agent detect a conflict by checking whether the version changed since it last read; a `lock_holder` field set to `null` when free provides mutual exclusion by convention.  Then rewrite the lock using only `os.rename()` on a lock file, the way the Model 3 cell does, and say which version is enforceable in a Dropbox folder.
   - *You've succeeded when*: The Editor can check that both upstream agents are done before starting, two agents cannot write at once by convention, and you have named the rule that is only advisory across a sync.

6.  *Price the protocol.*

   - *What to do*: Count the tokens (about three-quarters of a word each) in the five files rule 1 reads, and compare the total with the 4,840-token prompt in Model 1.
   - *Starter hint*: If your `.ai/` files are larger than the history they replace, the session log has stopped being a log and become a transcript.  Annotate and condense; do not delete.
   - *You've succeeded when*: You can state the per-start cost of your protocol in tokens and the condition under which it would exceed carrying the history.

---

## Reflection Prompt

*Personal*: Think of a time you picked up someone else's unfinished work, a group project, a shift, a document, with only what they left behind.  What did they leave that helped most, and what did you wish they had written down?  Did you ever hit a race (two people editing the same paragraph) or a stale claim (someone said "I've got this section" and vanished)?  Compare that with the entry you would want an agent to leave you.

*Technical*: The trace in Model 4 was written by the agent about itself.  The session entry is also written by the agent about itself.  For a system you would actually run, which claims in those files would you insist be produced by something other than the model (a test runner, a wrapper, the filesystem), and what does that cost you?  Then rank the three properties for your project: if you could keep only two of observability, traceability, and a written handoff protocol, which goes, and what breaks first?

*Societal*: A complete trace of an agent's actions is also a complete record of what its user asked for, hashed or not.  Who else could want that file, under what circumstances, and does storing a hash instead of the text protect the user in the ways they would expect?  And if a race, a stale claim, or a bad handoff message between two agents causes a wrong outcome for a real person, who is responsible when the failure belongs to the interaction rather than to any single agent?

---

-> Coming Up Next: In *Orchestration and Multi-Agent Patterns* (Tuesday) we stop handing work between agents by hand and start composing them: pipelines, routers, and a supervisor loop in which a model decides which agent runs next.  Every one of those compositions passes work across a seam, and today's trace and claim rules are how you will see what crossed it.  Have your `SKILL.md` draft and its checklist ready; the roster, budget, and stop condition you meet there are rules 8 through 12 in another form.

## Further Reading

- [Handoff Protocols](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/HandoffProtocols), claims, stale claims, and the handoff skill from Part IV, written for a repository you choose.
- Liu et al.  "Lost in the Middle: How Language Models Use Long Contexts."  *TACL* (2024).  The attention-quality force from Part I.
- OpenTelemetry Documentation: https://opentelemetry.io/docs/ and the OpenTelemetry Semantic Conventions for LLMs (GenAI): https://opentelemetry.io/docs/specs/semconv/gen-ai/.  The vendor-neutral standard for the spans in Section 3.
- Charity Majors, Liz Fong-Jones, and George Miranda.  *Observability Engineering.*  O'Reilly Media, 2022.
- Charity Majors.  "Observability is a Many-Splendored Thing." https://charity.wtf/2020/03/03/observability-is-a-many-splendored-thing/
- Jaeger Distributed Tracing: https://www.jaegertracing.io/
- Anthropic engineering blog.  "How we built our multi-agent research system" (2025, online), on verification and state in long-running agents.
- This course: [Agent Observability and Tracing](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Observability), the full three-pillars tutorial with the OpenTelemetry example and the token accounting code for OpenCode and Ollama; [Governing Coding Agents](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentGovernance), the case study the `.ai/` directory comes from; and the [agent templates](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/README.md), including [`AGENT_HANDOFF_KICKOFF.md`](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/ai/AGENT_HANDOFF_KICKOFF.md) and [`SESSION.md`](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/ai/SESSION.md).
- This course: [Agent Skills and Plugins](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentSkills), whose claim-protocol section is the handoff skill that exercise 4 borrows from; [The Second Brain](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/SecondBrain) and [Syncing Obsidian to GitHub](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/ObsidianSync), for the vault as a shared-folder channel.
- This course: [How I AI](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-howiai.md), where the handoff entry was first read, and [Memory and the Small Context Window Principle](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/MemoryAndContext), where the arithmetic in Model 1 comes from.

---

# Extension: Counting Tokens, the Number Under Every Cost (self-paced)

Every `prompt_tokens` and `completion_tokens` in Model 4 is a number the model server handed back, not a guess.  That makes the token count the cheapest metric you will ever collect: you do not compute it, you only have to keep it.  It is also the number every cost is built from, which is why the final project's Responsible AI Report asks for input and output tokens measured on every evaluation run.  You can read it in two places this semester.

| Where | Input tokens | Output tokens | Also there |
|---|---|---|---|
| **OpenCode**, the sidebar (`ctrl+x b` if hidden) | The session's running token count, and the share of the context window used | (same panel) | Cost, which reads `$0.00` for a local model |
| **OpenCode**, `opencode stats --days 1 --project ""` | Input, totaled | Output, totaled | Cache reads, cost, tokens per session; add `--models` for a per-model split |
| **Ollama**, every `/api/chat` or `/api/generate` response | `prompt_eval_count` | `eval_count` | `prompt_eval_duration`, `eval_duration`, `total_duration`, all in nanoseconds |

The cell below is the Ollama response behind Model 4's step 1 `plan` line.  Run it and read what the durations say about where the 2,773 milliseconds went.

```python
# The Ollama response behind Model 4, step 1 (durations are in nanoseconds)
resp = {"model": "hermes-3", "done": True, "done_reason": "stop",
        "total_duration": 2_773_000_000, "load_duration": 12_000_000,
        "prompt_eval_count": 412, "prompt_eval_duration": 610_000_000,
        "eval_count": 41, "eval_duration": 2_100_000_000}

NS = 1e9
in_tok, out_tok = resp["prompt_eval_count"], resp["eval_count"]
read_s = resp["prompt_eval_duration"] / NS
write_s = resp["eval_duration"] / NS
total_s = resp["total_duration"] / NS

print(f"read  {in_tok:>4} input tokens  in {read_s:.2f} s  ({in_tok / read_s:.0f} tokens/s)")
print(f"wrote {out_tok:>4} output tokens in {write_s:.2f} s  ({out_tok / write_s:.1f} tokens/s)")
print(f"total {total_s:.2f} s, and writing was {write_s / total_s:.0%} of it")

# The trace line, built from measured numbers rather than estimates
print({"trace_id": "t-77b0", "step": 1, "phase": "plan",
       "prompt_tokens": in_tok, "completion_tokens": out_tok,
       "latency_ms": int(total_s * 1000), "finish_reason": resp["done_reason"]})
```
@Pyodide.eval

Ten times as many input tokens took well under a second; forty-one output tokens took two.  Reading is one parallel pass over the prompt, and writing is one pass per token.  Now use the cell's two speeds to predict how long step 2, with 3,690 input and 512 output tokens, should have taken.  Compare your prediction with the 8,422 milliseconds Model 4 logged, and say what the gap suggests: a faster machine, a prompt served partly from cache, or a trace line you should not trust.

You switch your helper to `"stream": true`, and the token column of your trace fills with zeros.  Where did the counts go?

[( )] Ollama does not count tokens when it streams
[(X)] They arrive only in the last chunk, the one with `"done": true`, and the helper kept the text and dropped that chunk
[( )] They are spread across every chunk, and the helper has to add them up
[( )] They move to the HTTP response headers

**Try it on your machine.**  In opencode, open the sidebar and note the session's token count, then run `opencode stats --days 1 --project ""` and find the same session's tokens in the totals.  Then run the `token_usage.py` example from the [token accounting section of the tutorial](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Observability#token-accounting-counting-what-every-call-spends) against Ollama; it prints the input tokens, output tokens, and tokens per second for every call and appends a row to `token_usage.csv`.  The tutorial also shows how to wrap an existing `chat` helper so every call in your agent loop is counted without changing the loop, and how to read per-message counts out of `opencode export`.  Put the same `run_id` in the CSV and in `.ai/trace.jsonl`, so a row of tokens can be matched to the steps that spent them.

---

# Extension: Four Kinds of Memory, and Which One Survives a Stop (self-paced)

Cognitive science names four memory systems, and agent designers use the same names because each maps onto a storage mechanism.

| Memory type | What it stores | Where it lives | How it fails | Survives a stop? |
|---|---|---|---|---|
| **Working** | The current conversation: system prompt, retrieved documents, tool results, reasoning so far | The context window, in GPU memory during inference | Exhausted when the token budget is exceeded; the oldest content is dropped or the request fails | No.  Gone when the session closes |
| **Episodic** | Records of specific past events with timestamps: what was said, what tool was called, what it returned | An external database, log file, or vector store indexed by session and time | Retrieval fails if events are not indexed; the log grows without bound if no retention policy is set | Yes, if it was written before the stop |
| **Semantic** | General facts and concept relationships, the encyclopedia the agent consults | Model weights, or a RAG vector store queried at run time | Stale after the world changes; retrieval misses when the query does not match the chunk | Yes; it was never inside the session |
| **Procedural** | How to do tasks: conventions, step-by-step approaches, formatting habits | Fine-tuned weights, or standing examples in the system prompt; in this course, a skill on disk | Catastrophic forgetting when retrained; a skill that no longer matches the tool | Yes, if it is a file |

Working memory is the only kind that dies at a stop, so a handoff is the act of copying what matters out of working memory into episodic memory (the session log and the trace) and into procedural memory (the skill) before the window closes.  Retrieval-Augmented Generation (RAG) is semantic memory fetched on demand; the session log is episodic memory read at start.

---

# Extension: Coordination Problems and Cross-Team Standards (self-paced)

Part II named two coordination problems.  Distributed systems engineers found the whole family while building databases in the 1970s and 1980s, and multi-agent LLM systems fall into the same traps.

| Problem | Description | Example with Agents | Prevention Strategy |
|---------|-------------|--------------------|--------------------|
| **Race condition** | Two agents read shared state, both decide to act on what they read, both write, and the second write overwrites the first, or both take an action that should happen once | Agent A and Agent B both read a task queue, both claim task #7 as "in progress," and both execute it; the task runs twice and produces duplicate output | Atomic compare-and-swap (write only if the value is still what you read); locking; task queue with acknowledgment; optimistic concurrency with version numbers |
| **Deadlock** | Agent A waits for Agent B to finish before it can proceed; Agent B simultaneously waits for Agent A.  Neither can move because each holds something the other needs. | Agent A holds a database lock and waits for Agent B to release a file lock; Agent B holds the file lock and waits for Agent A to release the database lock | Lock ordering (always acquire locks in the same order everywhere); timeouts with retry; lock-free designs; leader arbitration |
| **Priority inversion** | A high-priority agent is blocked on a resource held by a low-priority agent, so the low-priority task decides when the high-priority task runs | A critical summary agent waits for a low-priority formatting agent to finish writing the shared document; the urgent output is delayed by a trivial task | Priority inheritance (the low-priority holder temporarily inherits the waiter's priority); preemption; avoiding shared resources between agents of different priorities |
| **Consensus failure** | Agents must agree on a value or decision but cannot; no majority or quorum forms and the system is stuck | Three analyst agents each produce a different numerical summary of the same dataset; the orchestrator cannot choose and must stall or escalate | Quorum protocols (2-of-3 agreement before proceeding); designated tiebreaker agent; confidence-weighted voting; human-in-the-loop for unresolved conflicts |

The classic remedies apply directly to agents: a **mutex** (only one agent may write a shared resource at a time), optimistic concurrency (write freely, but carry a version number and retry if it changed), leader election (one agent coordinates a resource and the others ask it), and vector clocks (each message carries a logical timestamp so receivers can reconstruct which events happened before which).

A third way agents talk, beside message passing and the blackboard, is **event streaming**: agents emit events ("search complete," "error occurred") to a bus, and other agents subscribe to the event types they care about.  Producers and consumers never address each other directly, which buys loose coupling at the cost of out-of-order delivery and missed events for a subscriber that was not connected.

Three agents are collaborating on a report.  Agent A finishes its section and writes `"DONE"` to a shared status file to signal completion.  Agent B reads the status file before Agent A writes, sees the old status, concludes the file is empty, and begins writing its own content, overwriting Agent A's completed section.  This scenario is best described as:

[( )] A deadlock, because both agents are waiting for each other; a deadlock requires both agents to be *blocked waiting*, but here Agent B proceeds immediately
[(X)] A race condition caused by missing synchronization between the read and write operations
[( )] A consensus failure, because the agents disagree on the content of the report; here Agent B simply overwrote Agent A without negotiation
[( )] Priority inversion, because Agent B executed before Agent A's higher-priority write completed; no priority ordering or blocking is involved here

**Standards for crossing team boundaries.**  Both channels in Part II work because both agents follow the same convention.  When an orchestrator built by one team must delegate to a specialist built by another, the convention has to be a published standard.  The **A2A (Agent-to-Agent)** protocol addresses three needs: discovery (an agent publishes an "agent card" describing what it can do), delegation (the orchestrator spawns a specialist in its own context window and must decide explicitly what context to send), and trust boundaries (a sub-agent cannot exceed the permissions of the user who authorized the agent that spawned it, which prevents privilege escalation through delegation).  **MCP (Model Context Protocol)** is the standard tool interface: agents use MCP to call file systems, databases, and APIs in a consistent, discoverable format, and one agent's tools can include another agent that exposes itself as an MCP server.

### Questions to Work Through

1.  FIPA ACL (the Agent Communication Language from the Foundation for Intelligent Physical Agents) messages carry a **performative** that names the intent: `inform`, `request`, `propose`, `agree`, `refuse`, `query-if`.  Rewrite the reviewer's comment and the worker's reply in Model 2 as `{"performative": ..., "content": ...}` pairs.  What does the performative add over the raw text?  Give one case where the receiving agent should act differently on `inform: task complete` than on `request: task complete`.

2.  Map each of the five steps of the GitHub loop to a row of the coordination table: which step is where a race could happen, which step is a lock, and which step is the consensus mechanism?  GitHub serializes some of these for you.  Name one thing it serializes and one thing it does not.

3.  Pick one remedy from the table (mutex, optimistic concurrency, leader election, vector clocks) and say what carries over unchanged to agents and what a probabilistic participant, one that reads instructions from the same channel it reads data from, breaks about it.
