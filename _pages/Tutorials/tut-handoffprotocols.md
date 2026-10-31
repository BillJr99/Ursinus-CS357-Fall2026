---
layout: textbook
permalink: /Tutorials/HandoffProtocols
title: 'CS357: Foundations of Artificial Intelligence - Handoff Protocols: Claims, Stale Claims, and a Handoff Skill for Your Project'
info:
  coursenum: CS357
  purpose: "To practice coordinating two agents through a durable medium on a small problem first, and then to write a handoff SKILL.md for a project repository of your own choosing."
  eyebrow: "Tutorial"
  numbering: false
tags:
- agents
- handoff
- skills
- observability
---

## About This Tutorial

Two agents are pointed at the same task list.  Neither can see the other's context window.  Agent A starts a task, and an hour later Agent B looks at the same list.  How does B know the task is taken?  What if A crashed halfway through?  And when B finds a file in `done/`, how does it know the work was finished rather than abandoned?  This tutorial answers those questions on a small practice problem first.  Then you write the answers down as a handoff skill for a real repository.
{: .tb-lede}

Part I reviews start, stop, and restart, the three moments every agent session has.  Part II states the four rules of a claim protocol, separates the rules the medium enforces from the ones that are only advisory, and adds one trace line per action.  Part III is practice in isolation, on one of two paths.  The **code path** is a pure-Python claim race between two agents over a folder, and it needs nothing but `python3`.  The **no-code path** runs the same protocol by hand with a GitHub issue or a shared folder.  In Part IV, you write a `SKILL.md` for a project repository you choose.  Your team's final project repository is one option, and your own `cs357-work` repository is another.

This page builds on *Agents That Talk, Observability, and Handoff Protocols* (Parts II and IV).  It reuses that session's file names, its claim race, and its `SKILL.md` skeleton.  Nothing on this page is collected.  You need one path in Part III, not both.  The skill in Part IV is the part worth keeping.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|:-----|:------------------------|:------------------------|
| **Durable medium** | Something outside both agents that survives either one crashing: a repository, an issue thread, or a folder on disk | `handoff/` with `inbox/`, `claimed/`, and `done/`, or GitHub issue #42 |
| **Claim** | A mark, visible to the other agent through the medium alone, that says "this item is mine and I started it at this time" | Renaming a file into `handoff/claimed/` and writing `task-7.md.claim`; assigning yourself an issue and opening a draft pull request |
| **Stale claim** | A claim whose holder has stopped writing for longer than the protocol allows, usually because it crashed or ran out of quota | `claimed_at` older than `STALE_AFTER` with no write to the `.notes` file since |
| **Enforced rule** | A rule the medium itself guarantees, whether or not the agents cooperate | One `os.rename()` on one disk succeeds and the other fails; GitHub merges a pull request once |
| **Advisory rule** | A rule that holds only because both agents chose to follow it | The staleness timeout; "only the holder writes the notes"; what to do with a conflicted copy |
| **Conflicted copy** | The file a sync service creates when two machines changed the same path before either saw the other's change | `task-7 (conflicted copy).md` beside the winner in a Dropbox folder |
| **Trace line** | One JSON object per action, naming who acted, what they did, and the rule that allowed it, with no prompt text | A line in `.ai/trace.jsonl` with `"rule": "handoff-protocol#10"` |
{: .tb-full}

---

# Part I: Start, Stop, Restart

## 1.  Three Moments Every Session Has

A handoff protocol is mostly about two agents, but it starts with one.  Every session starts, every session stops, and sooner or later a session restarts as a stranger to its own work.  The *Governing Coding Agents* tutorial and Part IV of the *Agents That Talk* session give each moment a rule.  You will use the files they name here:

- **On start**, read in a fixed order before doing anything else: `START_HERE.md`, `CHARTER.md`, `docs/ROADMAP.md`, `.ai/CURRENT_TASK.md`, `.ai/SESSION.md` (at least the most recent entry), and the most recent commit.  Then state the mission, the active task, and the Next Safe Action in your own words.  Do not act until you have.
- **On stop**, for any reason, including finishing normally, append a dated entry to `.ai/SESSION.md` that ends with a Next Safe Action, and update `.ai/CURRENT_TASK.md`.  Annotate superseded guidance in place, and never delete it.
- **On restart**, run the start rule, and then re-run every command in the Reality Check table of `CURRENT_TASK.md` before relying on it.  That table lists what is *not* done.  Each row gives the command or test that proves it.

Handing work to a second agent adds one more thing to the stop rule: the claim.  The rest of this page is about that addition.

### Questions to Work Through

1.  Why does the stop rule apply when a session finishes normally, and not only when it is interrupted?  Think of a Friday session that finishes cleanly and a Monday session run by a different tool.

2.  A restarted agent reads "12 of 14 tests pass" in `CURRENT_TASK.md`.  What should it do before it believes that line, and what would it be risking if it skipped that step?

---

# Part II: Claims Through a Durable Medium

## 2.  Four Rules a Claim Protocol Needs

The *Agent Skills and Plugins* tutorial lists four things a handoff `SKILL.md` must specify.  Here they are with the folder from the *Agents That Talk* session beside them:

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

1.  **How to claim.**  Move the task from `inbox/` to `claimed/`, then write the `.claim` file with `claimed_by` and `claimed_at`.  The test of a claim is whether the *other* agent can see it through the medium alone, with no message from you.
2.  **What a second agent does on seeing a claim.**  Skip it, wait, or take it.  Your protocol has to pick one.
3.  **When a claim is stale, and who may break it.**  An agent that claims an item and dies leaves it claimed forever unless some rule says otherwise.  The rule needs a number (how long with no write) and a name (which agents may take over).  An agent that breaks a claim records whose claim it took.
4.  **What done looks like.**  Anything in `done/` with a `.result.md` beside it is finished.  Anything still in `claimed/` with a stale claim is abandoned.  A fresh claim is work in progress, and a file in `inbox/` has not been started.

Write each rule as a path and a condition.  "Agents should coordinate" is not a rule anyone can check.

## 3.  Enforced Rules and Advisory Rules

Some of those rules hold no matter what the agents do.  Others hold only because both agents agreed to them.  The difference matters most when the second agent runs a different model, because a different model may read your advisory rules differently.

| Rule | Folder on one disk | Folder synced across two machines | GitHub |
|---|---|---|---|
| Only one agent wins a claim | **Enforced**: `os.rename()` is atomic, so one rename succeeds and the other gets "file not found" | Advisory: each machine's rename succeeds on its own disk, and the sync service later leaves a conflicted copy | Advisory: GitHub allows several assignees and does not stop a second agent from opening its own pull request |
| Work lands once | Partly: `finish()` uses a rename, which fails if the task has already left `claimed/`, but nothing checks that the finisher still holds the claim | Advisory | **Enforced**: a pull request is merged once, and a draft pull request cannot be merged until it is marked ready |
| A stale claim may be broken after N minutes | Advisory | Advisory | Advisory |
| Only the holder writes the notes | Advisory | Advisory | Advisory: anyone with access can comment on the issue or push to the branch |
{: .tb-full}

Two habits follow from the table.  First, put your most important rule where the medium enforces it.  That is why the claim is a rename and not "check whether the file is there, then copy it."  Second, say in your protocol what an agent does when an advisory rule has clearly been broken.  For a conflicted copy, *stop and ask* is the safe default.

One more point from the *Agent Skills* tutorial: every clause in a `SKILL.md` is a request to the model, not a rule the harness enforces.  The medium enforces the rename and the merge.  A hook (such as a `Stop` hook that checks whether `SESSION.md` changed) can verify a few more rules.  Everything else is advisory.

## 4.  One Trace Line per Action

Every claim, skip, wait, takeover, and finish writes one JSON line to `.ai/trace.jsonl`.  Every line carries a `rule` field that names the rule in your skill that allowed the action.  This is the same habit as the `rule` field in Model 4 of the *Agents That Talk* session.  A trace without the rule tells you what happened.  A trace with it tells you what to change.  Rule 4 of the skeleton in Part IV logs each loop phase.  The handoff actions add their own lines to the same file, with the same `trace_id` habit.

Store identifiers and measurements, never content.  The trace gets the task name, the agent name, the time, the rule, and numbers such as how long the claim had been idle.  It does not get the prompt, the task text, or the notes.  The notes live in their own file, which the medium already keeps.

### Questions to Work Through

3.  The `.claim` file is written *after* the rename succeeds.  What does a third agent see if it looks at `claimed/` in the moment between the two steps?  Would the other order be better or worse?

4.  In the table above, "work lands once" is advisory for a synced folder.  Two machines share `handoff/` through a sync service.  Describe a sequence of events in which two results for the same task end up in `done/`.

---

# Part III: Practice the Protocol in Isolation

Practice this on a toy problem before you put it in a project, so that a broken claim costs you nothing.  Pick one path.  Both practice the same four rules, and both end with a trace you can read.

## 5.  The Code Path: A Claim Race Over a Folder

The three cells below need only `python3` and the standard library.  Save each one as its own file in an empty folder and run it with `python3 <file>.py`.  The first cell creates a `handoff-demo/` folder in the folder you run it from.  The third cell reads that folder, so run them from the same place.  The "agents" here are one set of Python functions, called with two agent names, standing in for two agent sessions.  The protocol does not care what is on the other side of the folder.

## Code Cell: The Protocol, One Step at a Time

This is the claim race from Model 3 of the *Agents That Talk* session, with two additions: a `.notes` file whose writes count as a sign of life, and a trace line for every action.  Read `claim()` first.  The whole claim rule rests on one fact: a rename cannot half-happen.

```python
import os, json, time, shutil

ROOT = "handoff-demo"
shutil.rmtree(ROOT, ignore_errors=True)   # fresh folder for the demo
INBOX, CLAIMED, DONE = (os.path.join(ROOT, "handoff", d)
                        for d in ("inbox", "claimed", "done"))
TRACE = os.path.join(ROOT, ".ai", "trace.jsonl")
for d in (INBOX, CLAIMED, DONE, os.path.dirname(TRACE)):
    os.makedirs(d, exist_ok=True)

STALE_AFTER = 300  # seconds with no write before a claim may be broken
TRACE_ID = "t-task7"

def log_action(agent, action, task, rule, **fields):
    """One JSON line per action.  Names and numbers only, never prompt text."""
    record = {"ts": round(time.time(), 3), "trace_id": TRACE_ID, "agent": agent,
              "action": action, "task": task, "rule": rule}
    record.update(fields)
    with open(TRACE, "a") as f:
        f.write(json.dumps(record) + "\n")

def post_task(name, text):
    with open(os.path.join(INBOX, name), "w") as f:
        f.write(text)

def claim(agent, name):
    src, dst = os.path.join(INBOX, name), os.path.join(CLAIMED, name)
    try:
        os.rename(src, dst)              # atomic on one disk: one caller wins
    except FileNotFoundError:
        log_action(agent, "skip", name, "handoff-protocol#9")
        return False                     # someone else already moved it
    with open(dst + ".claim", "w") as f:
        json.dump({"claimed_by": agent, "claimed_at": time.time()}, f)
    log_action(agent, "claim", name, "handoff-protocol#8")
    return True

def note(agent, name, text):
    """Append to the notes file.  Each write also counts as a sign of life."""
    with open(os.path.join(CLAIMED, name + ".notes"), "a") as f:
        f.write(f"[{agent}] {text}\n")
    log_action(agent, "note", name, "handoff-protocol#8")

def last_write(name):
    with open(os.path.join(CLAIMED, name + ".claim")) as f:
        c = json.load(f)
    notes = os.path.join(CLAIMED, name + ".notes")
    newest = c["claimed_at"]
    if os.path.exists(notes):
        newest = max(newest, os.path.getmtime(notes))
    return c, newest

def take_if_stale(agent, name):
    c, newest = last_write(name)
    idle = time.time() - newest
    if c["claimed_by"] == agent or idle < STALE_AFTER:
        log_action(agent, "wait", name, "handoff-protocol#10", idle_s=int(idle))
        return False                     # the holder may still be working
    with open(os.path.join(CLAIMED, name + ".claim"), "w") as f:
        json.dump({"claimed_by": agent, "claimed_at": time.time(),
                   "taken_from": c["claimed_by"]}, f)
    log_action(agent, "break-claim", name, "handoff-protocol#10",
               idle_s=int(idle), taken_from=c["claimed_by"])
    return True

def finish(agent, name, result):
    os.rename(os.path.join(CLAIMED, name), os.path.join(DONE, name))
    os.remove(os.path.join(CLAIMED, name + ".claim"))
    notes = os.path.join(CLAIMED, name + ".notes")
    if os.path.exists(notes):
        os.rename(notes, os.path.join(DONE, name + ".notes"))
    with open(os.path.join(DONE, name.replace(".md", ".result.md")), "w") as f:
        f.write(f"finished_by: {agent}\n\n{result}\n")
    log_action(agent, "finish", name, "handoff-protocol#11")

def show():
    for d in (INBOX, CLAIMED, DONE):
        print(f"  {os.path.basename(d)}/: {sorted(os.listdir(d))}")

post_task("task-7.md", "Summarize the three failure modes of message passing.")
print("A claims:", claim("agent-A", "task-7.md"))
print("B claims:", claim("agent-B", "task-7.md"))
note("agent-A", "task-7.md", "Plan: read Part II, list the modes, cite the deck.")
print("B takes over too early:", take_if_stale("agent-B", "task-7.md"))
show()

# Agent A dies here.  Move the clock back on both of its writes.
path = os.path.join(CLAIMED, "task-7.md.claim")
with open(path) as f:
    c = json.load(f)
c["claimed_at"] -= STALE_AFTER + 1
with open(path, "w") as f:
    json.dump(c, f)
old = time.time() - STALE_AFTER - 1
os.utime(os.path.join(CLAIMED, "task-7.md.notes"), (old, old))

print("B takes the stale claim:", take_if_stale("agent-B", "task-7.md"))
finish("agent-B", "task-7.md", "Lost message, crashed receiver, unparseable schema.")
show()
```

It prints:

```text
A claims: True
B claims: False
B takes over too early: False
  inbox/: []
  claimed/: ['task-7.md', 'task-7.md.claim', 'task-7.md.notes']
  done/: []
B takes the stale claim: True
  inbox/: []
  claimed/: []
  done/: ['task-7.md', 'task-7.md.notes', 'task-7.result.md']
```

Now open `handoff-demo/.ai/trace.jsonl`.  There are six lines, one per action, and each one names a rule.  A's claim and note fall under rule 8, B's skip under rule 9, B's early wait and its later takeover under rule 10 (with `idle_s` and `taken_from`), and B's finish under rule 11.  The task text and the note text are not in it.

This cell runs the agents one after the other, so it cannot show you a real race.  The next cell does.

## Code Cell: Two Agents at the Same Moment

Here, the code releases two threads at the same instant, a hundred times, and both threads try to claim the same file.  The first version claims with a rename.  The second checks whether the file is there and then copies it, which is two steps.

```python
import os, shutil, tempfile, threading, time

def rename_claim(src, dst):
    try:
        os.rename(src, dst)              # one step: it happens or it does not
        return True
    except FileNotFoundError:
        return False

def check_then_act_claim(src, dst):
    if not os.path.exists(src):          # step 1: check
        return False
    text = open(src).read()
    time.sleep(0.01)                     # anything can happen between the steps
    open(dst, "w").write(text)           # step 2: act
    try:
        os.remove(src)
    except FileNotFoundError:
        pass                             # the other agent already removed it
    return True

def race(claim_fn, rounds=100):
    double = 0
    for _ in range(rounds):
        root = tempfile.mkdtemp()
        src = os.path.join(root, "task-7.md")
        open(src, "w").write("one task")
        start = threading.Barrier(2)     # release both agents at the same moment
        winners = []
        def agent(who):
            start.wait()
            if claim_fn(src, os.path.join(root, f"claimed-by-{who}.md")):
                winners.append(who)
        threads = [threading.Thread(target=agent, args=(w,)) for w in "AB"]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if len(winners) > 1:
            double += 1
        shutil.rmtree(root)
    return double

print("rename:         rounds with two winners =", race(rename_claim))
print("check then act: rounds with two winners =", race(check_then_act_claim))
```

The first line should print 0 every time you run it.  The second line prints how many of the hundred rounds ended with both agents believing they owned the task.  Run it a few times and write down what you see.  The second number can change from run to run, but the first should not.

## Code Cell: Auditing the Trace

The checklist in Part IV asks two things of every trace: each action names a rule, and no prompt text or other content is stored.  A few lines of Python can check both.  Run this after the first cell.

```python
import json
from collections import Counter

TRACE = "handoff-demo/.ai/trace.jsonl"
FORBIDDEN = {"prompt", "text", "content", "messages"}   # content, not measurements

actions, problems = Counter(), []
with open(TRACE) as f:
    for n, line in enumerate(f, start=1):
        rec = json.loads(line)
        actions[(rec["agent"], rec["action"])] += 1
        if not rec.get("rule"):
            problems.append(f"line {n}: {rec['action']} names no rule")
        leaked = FORBIDDEN & rec.keys()
        if leaked:
            problems.append(f"line {n}: stores {sorted(leaked)}")

for (agent, action), count in sorted(actions.items()):
    print(f"{agent:8} {action:12} x{count}")
print("problems:", problems or "none")
```

On the trace from the first cell, it prints one row for each of the six actions and ends with `problems: none`.  Now change `note()` in the first cell so its `log_action` call also passes `text=text`, rerun both cells, and confirm that the audit catches it.

### Questions to Work Through

5.  Predict before you change anything: set `STALE_AFTER = 0` in the first cell and rerun it.  What does "B takes over too early" print now, and what does that tell you about choosing the timeout for a slow but healthy agent?

6.  In the second cell, why does the `time.sleep(0.01)` make the check-then-act bug show up so often?  If you deleted the sleep, would the code be correct?

7.  Agent A was slow, not dead.  It wakes up after B took the claim and calls `finish("agent-A", ...)`.  Trace what happens to `done/` and to the trace.  Which rule needs another clause, and what check would you add to `finish()`?

8.  `take_if_stale()` reads the `.claim` file and then rewrites it, which is check-then-act again.  What happens if two agents both decide the claim is stale at the same moment?  How could a rename make breaking a claim safe in the same way it makes claiming safe?

---

## 6.  The No-Code Path: The Same Protocol by Hand

You can run the whole protocol without writing a line of code.  Use two agent sessions that do not share a context window, two people, or yourself playing both roles in two browser windows.  Choose the GitHub version or the folder version.

### With a GitHub Issue

Make a throwaway practice repository for this, not your project repository.

1.  **Post the task.**  Open an issue with the task and its acceptance criteria.  Create an `in-progress` label.
2.  **Claim it (rule 8).**  Agent A assigns itself, adds `in-progress`, and comments "Claiming this.  Plan: ...  (rule 8)".  Then it opens a **draft** pull request whose description says `Closes #<issue number>`, so the claim is also visible from the pull request list.
3.  **See the claim (rule 9).**  Agent B opens the issue, sees the assignee, the label, and the linked draft pull request, and comments "Skipping, claimed by A (rule 9)."
4.  **Break a stale claim (rule 10).**  Decide on a number before you start, such as two hours with no commit and no comment on the draft pull request.  Once that has passed, B comments "Claim from A is stale: last activity at [time] (rule 10)", reassigns the issue to itself, and either continues A's branch or opens its own draft pull request and closes A's.
5.  **Finish (rule 11).**  The holder marks the pull request ready for review, someone merges it, and the issue closes against the merge commit.  Remove `in-progress`.

Finished work is a closed issue with a merged pull request.  Abandoned work is either an open issue whose assignee has gone quiet, or an issue closed with no merged pull request (GitHub's "Close as not planned" option records this).  The issue's timeline already records who changed each label and assignee and when, so GitHub writes part of your trace for you.  It does not record the rule, which is why each comment ends with one.

### With a Shared Folder, Moved by Hand

1.  Make `handoff/inbox/`, `handoff/claimed/`, and `handoff/done/` in a folder both "agents" can reach.  Put `task-7.md` in `inbox/`.
2.  **Claim it (rule 8).**  Drag `task-7.md` from `inbox/` into `claimed/` in your file manager.  Then create `task-7.md.claim` beside it with two lines, `claimed_by: A` and `claimed_at: <date and time>`.
3.  **Race it.**  Have both "agents" count down and drag the same file at the same moment.  On one disk, only one move can succeed, because the file is gone by the time the second one tries.  If the folder is synced between two machines, look for a conflicted copy a minute later.
4.  **Break and finish (rules 10 and 11)** the same way the code does.  To break the claim, edit the `.claim` file to name the new holder and add a `taken_from:` line.  To finish, move the task into `done/` and write `task-7.result.md` with `finished_by:` and a Next Safe Action.
5.  **Trace it.**  For every move or edit, add one line to `.ai/trace.jsonl` by hand, such as `{"ts": "2026-11-02 14:05", "agent": "B", "action": "break-claim", "task": "task-7.md", "rule": "handoff-protocol#10"}`.  Leave out the task text and the notes.

The folder version teaches one thing the code does not.  Dragging a file between folders on the same drive is a rename.  Dragging it to a different drive is a copy followed by a delete, which is two steps.  Keep all three folders on one drive.

### Questions to Work Through

9.  In the GitHub version, both agents assign themselves within the same minute.  What does the issue show afterward?  Which of rules 8 through 11 did GitHub enforce, and which did it only display?

10.  In the folder version, which of your hand-written trace lines could you check against the medium itself (the files in each folder, the sync service's history), and which could only be taken on trust?

---

# Part IV: A Handoff Skill for Your Project

## 7.  Choose the Repository and the Medium

Now take what you practiced into a real repository.  Choose one project repository of your own.  Your team's final project repository is one option.  It is the natural choice if more than one agent works in it, because the Responsible AI Report asks for traces of agent actions and handoffs.  Your `cs357-work` repository, or any other repository you will keep working in, also works.

Then choose the medium the agents will hand work through: GitHub issues and pull requests, a `handoff/` folder inside the repository, or an Obsidian vault folder (the *Agent Skills* tutorial lists all three).  If your repository does not have `START_HERE.md`, `CHARTER.md`, or the `.ai/` files yet, the [agent templates](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/README.md) have a starting copy of each.  That step is optional.  The skill works as long as rule 1 names files that exist.

## 8.  Write the `SKILL.md`

Put the skill at `.agents/skills/handoff-protocol/SKILL.md` in that repository.  The directory name must match the `name` in the front matter.  Both opencode and pi look in `.agents/skills/`.  Start from the skeleton in Model 5 of the *Agents That Talk* session:

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

Fill in rules 8 through 11 for the medium you chose, using what you saw in Part III.  Two more edits are worth making.  If your repository has a `docs/ROADMAP.md`, add it to rule 1 after `CHARTER.md`, since the kickoff template reads it there.  And give each rule an identifier your trace lines can cite, such as `handoff-protocol#10`, the way the code path did.

## 9.  Check It

Read your skill against this checklist from the *Agents That Talk* session.  Every row must be true of your protocol, and every row must cite the rule number that makes it true.

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
{: .tb-full}

### Questions to Work Through

11.  Mark each of your rules 8 through 11 as enforced by your medium or advisory.  Which one is the first to break if the second agent runs a different model?

12.  Your skill is text the model reads, so every clause is a request.  Pick the one clause you most need to hold every time.  What would a program look at to decide whether it held, and could a `Stop` hook check it?

---

## Exercises

These are optional, and both use the repository and skill from Part IV.  Each one ends with a check you can apply yourself.

1.  **The conflict.**

    *What to do:* Point two sessions that do not share a context window at the same unclaimed item in your project's medium, at the same time.  Report what happened.

    *Starter hint:* There is no correct outcome.  Either your claim held, and you can say what mechanism held it, or you got double work or a lost write.  The second is a passing result if you diagnose it: show the evidence, name the rule that would have prevented it, and say whether that rule is enforced or advisory in your medium.

    *You've succeeded when:* You can say which of your rules the medium enforces and which hold only because both agents chose to follow them.

2.  **Hand it to a stranger.**

    *What to do:* Commit your `SKILL.md`, start a fresh session in that repository, and ask it to pick up the next unclaimed item.  Record every question it asks before it claims anything.

    *Starter hint:* Each question is a missing sentence in your skill or in one of the files rule 1 reads.  Add the sentence.  Do not write a longer prompt.

    *You've succeeded when:* A second fresh session claims, works, and stops cleanly without asking anything, and its trace passes the audit from the third code cell (or the same two checks done by eye).

---

## Reflection Prompt

*Personal*: Think of a time someone said "I've got this section" in a group project and then went quiet.  How long did you wait before you took it over, who decided, and did you tell them?  What would have made that easier to settle?

*Technical*: The trace in this tutorial is written by the agents about themselves.  Which lines would you trust only if something else produced them, such as the filesystem, a wrapper around the tool call, or GitHub's own timeline?  What would it cost you to get them that way?

*Societal*: When a stale claim or a race between two agents produces a wrong result that reaches a real person, the fault belongs to the interaction rather than to either agent alone.  Who should be responsible: the people who wrote the protocol, the people who ran the agents, or someone else?

---

## Further Reading

- This course: [Agents That Talk, Observability, and Handoff Protocols](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-observability.md), Parts II and IV, where the claim race, the `SKILL.md` skeleton, and the checklist come from.
- This course: [Agent Skills and Plugins](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentSkills), for where skills live on disk, why every clause is a request, and the claim-protocol section this page practices.
- This course: [Governing Coding Agents](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentGovernance), for the read-order funnel, the `.ai/` directory, and the mid-session swap.
- This course: [Memory and the Small Context Window Principle](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/MemoryAndContext), for why state has to leave the context window in the first place.
- This course: [Agent Observability and Tracing](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Observability), for logs, traces, and metrics, and for what not to store in a trace.
- This course: the [agent templates](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/README.md), including [`AGENT_HANDOFF_KICKOFF.md`](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/ai/AGENT_HANDOFF_KICKOFF.md) and [`SESSION.md`](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/ai/SESSION.md), and the [Final Project](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/FinalProject) Responsible AI Report, which asks for traces of agent actions and handoffs.
