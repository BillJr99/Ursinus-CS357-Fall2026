---
layout: textbook
permalink: /Tutorials/OrchestrationPatterns
title: 'CS357: Foundations of Artificial Intelligence - Orchestration Patterns: Pipeline, Router, and Supervisor'
info:
  coursenum: CS357
  purpose: "To practice a fixed pipeline, a router, and a supervisor loop one at a time on one small task, to count what each one costs in model calls, and then to apply the least dynamic pattern that works to a task of your own."
  eyebrow: "Tutorial"
  numbering: false
tags:
- orchestration
- agents
- multi-agent
---

## About This Tutorial

*Orchestration and Multi-Agent Patterns* named three ways to connect small agents: a fixed pipeline, a router, and a supervisor loop in which a model picks the next move.  The *Orchestration Worked Example* built all three in class.  In this tutorial, you practice each one on your own, one at a time, on the same small task.  The task is the nightly club digest: five raw messages go in, and one short digest comes out with every day and time intact.  Then you pick one pattern and try it on a task you choose.  Your team's project task is one good option, but any small task with a checkable output works.
{: .tb-lede}

Part I sets up the task.  Part II runs each pattern in isolation, makes each control fire on purpose, and ends with a cost table that shows how many model calls each pattern spent on the same digest.  Part III runs the same patterns on a real model, by code or by hand.  Part IV is your own task.  Nothing here is collected or graded.  If you are short on time, Parts I and II and one path in Part III are enough to get you started on Part IV.

There are two paths, and either one is enough:

- **Code path.**  You use pure Python with a scripted stand-in for the model.  Every cell in Parts I and II runs anywhere with `python3`, with no network and no packages.  Part III swaps in Ollama by redefining one function.
- **No-code path.**  You use saved Open WebUI presets, or prompt nodes on a Langflow canvas, and move the text between them by hand.  You enforce the controls yourself and log every step in a spreadsheet.  Read the code in Part II anyway.  It is the specification of what you will do by hand.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|---|---|---|
| **Fixed pipeline** | A sequence of model calls whose order you wrote before the run; each stage sees only the previous stage's output | Section 2: extract, draft, polish |
| **Check in code** | A test written in ordinary code at a seam, for a property a program can verify without a model | `check_times`, which confirms every day and time survived |
| **Router** | One classification into a closed set of labels, then a dispatch; anything outside the set fails closed to a person | Section 3: event, change, question, or `needs_human` |
| **Supervisor loop** | A loop in which a model chooses the next sub-agent each turn, or stops | Section 4: `supervise` |
| **Roster** | The fixed menu of sub-agents the supervisor may call; an unknown name is refused | `ROSTER`, three entries |
| **Budget** | A hard ceiling on turns, set in configuration rather than in the prompt, so a confused loop cannot run forever | `CONFIG["spawn_budget"]`, six turns |
| **Stop condition** | A rule in your code that ends the loop for a named reason | The four `return` lines in `supervise` |
| **Fail closed** | When output cannot be parsed or trusted, stop or hand it to a person rather than guess | The malformed-decision stop and the router's `needs_human` |
{: .tb-full}

---

# Part I: The Task and the Settings You Own

## 1.  Five Messages, Four Prompts, One Function

Five messages arrived today.  Three are events for the digest, one is a question that belongs in an FAQ queue, and one is something the categories did not anticipate.  `CONFIG` holds the settings you own, outside any prompt.  The four system prompts are one sentence each, following the small-context discipline from the orchestration deck.  Every pattern calls one function, `llm()`, and `CALLS` counts every call.

Here `llm()` calls `stand_in()`, which is a set of fixed rules per role, not a language model.  It extracts events with a regular expression and writes one sentence per event.  In the polish stage it makes a mistake on purpose: it changes "Thursday" to "Friday" while editing for concision.  It also returns a label outside the closed set for the pizza message.  Both mistakes are scripted, so you can watch the controls catch them on every run.

Run the cells in order, in one Python session (a notebook, or one file that you add to as you go).  Each cell uses what the cells before it built.

```python
# Section 1: the task, the settings you own, and a scripted stand-in for the model.
import json
import re

MESSAGES = [
    "Chess club meets Thursday at 7pm in Olin 107.",
    "Hawk Hacks is Saturday at 10am in IDDC. Bring laptops!",
    "Ultimate frisbee pickup moved to Sunday at 2pm on the quad.",
    "Does anyone know if the library is open late during finals?",
    "Free pizza in the lobby, first come first served.",
]

CONFIG = {"spawn_budget": 6, "temperature": 0.0, "seed": 42}   # yours, not the model's

EXTRACT = "Extract every event as 'name | day | time | place', one per line. Output only the lines."
DRAFT   = "Write a friendly digest of these events for students, one sentence per event."
POLISH  = "Edit the digest for concision and warmth. Keep every day and time."
CLASSIFY = "Classify the message as exactly one word: event, change, or question. Output only that word."

EVENT = re.compile(r"^(?P<name>.+?) (?:meets|is|moved to) (?P<day>\w+day) at (?P<time>\d+(?:am|pm)) "
                   r"(?:in|on) (?P<place>[^.!]+)")
CALLS = []   # every model call, so each pattern's cost can be counted

def stand_in(system, user):
    """Not a language model: fixed rules per role, so every intermediate output is
    visible and repeatable.  Part III replaces this function with a real model call."""
    if system == EXTRACT:
        rows = []
        for line in user.splitlines():
            m = EVENT.match(line.strip())
            if m:
                rows.append(" | ".join(m.group("name", "day", "time", "place")))
        return "\n".join(rows)
    if system == DRAFT:
        out = []
        for row in user.splitlines():
            name, day, time, place = [x.strip() for x in row.split("|")]
            out.append(f"{name} is on {day} at {time} ({place}).")
        return " ".join(out)
    if system == POLISH:   # the scripted mistake: a fact changes during editing
        return user.replace(" is on ", ": ").replace("Thursday", "Friday")
    if system == CLASSIFY:
        if "moved" in user or "cancel" in user:
            return "change"
        if user.rstrip().endswith("?"):
            return "question"
        return "event" if EVENT.match(user) else "announcement"   # outside the closed set
    return ""

def llm(system, user):
    """The one function every pattern calls.  Here it is the stand-in."""
    CALLS.append(system[:24])
    return stand_in(system, user)

print(f"{len(MESSAGES)} messages; settings {CONFIG}")
print(repr(llm(CLASSIFY, MESSAGES[0])), repr(llm(EXTRACT, MESSAGES[0])))
CALLS.clear()
```

**You should see:**

```text
5 messages; settings {'spawn_budget': 6, 'temperature': 0.0, 'seed': 42}
'event' 'Chess club | Thursday | 7pm | Olin 107'
```

On the no-code path, this section is your setup.  Copy the five messages and the four prompts somewhere you can paste from.  Then start a spreadsheet with the columns `pattern`, `step`, `prompt used`, `input`, `output`, `check`, and `model calls so far`.

---

# Part II: Each Pattern in Isolation

## 2.  A Fixed Pipeline With a Check at the Seam

You wrote the order: extract, then draft, then polish.  Every intermediate output is printed.  After the last stage, a check in code runs.  The check is not a fourth model call.  A program can verify exactly whether "Thursday at 7pm" appears in the digest, so a program does the verifying.  When the check fails, the pipeline stops for a stated reason and returns the last version that passed, with the problem attached.

```python
# Section 2: a fixed pipeline.  You wrote the order; the code checks the seam the model cannot.
def check_times(facts, text):
    """A check in code, not a model: every extracted day and time must survive into the text."""
    missing = []
    for row in facts.splitlines():
        fields = [x.strip() for x in row.split("|")]
        if len(fields) != 4:               # a real model can break the format: report it, do not crash
            if row.strip():
                missing.append(f"unreadable fact line: {row.strip()}")
            continue
        name, day, time, _ = fields
        if f"{day} at {time}" not in text:
            missing.append(f"{name}: {day} at {time}")
    return missing

def digest_pipeline(messages):
    facts = llm(EXTRACT, "\n".join(messages))
    print("1. EXTRACT ->\n" + facts)
    draft = llm(DRAFT, facts)
    print("2. DRAFT ->\n" + draft)
    final = llm(POLISH, draft)
    print("3. POLISH ->\n" + final)
    missing = check_times(facts, final)
    print("4. CHECK ->", missing or "every day and time present")
    if missing:                        # stop condition: never ship a digest that lost a fact
        print("   polish broke a fact; returning the draft, with the problem attached")
        return draft, missing
    return final, []

CALLS.clear()
digest, problems = digest_pipeline(MESSAGES)
print(f"\nRESULT: {digest}\nmodel calls: {len(CALLS)}")
```

**You should see** (the `RESULT` line is shortened here):

```text
1. EXTRACT ->
Chess club | Thursday | 7pm | Olin 107
Hawk Hacks | Saturday | 10am | IDDC
Ultimate frisbee pickup | Sunday | 2pm | the quad
2. DRAFT ->
Chess club is on Thursday at 7pm (Olin 107). Hawk Hacks is on Saturday at 10am (IDDC). Ultimate frisbee pickup is on Sunday at 2pm (the quad).
3. POLISH ->
Chess club: Friday at 7pm (Olin 107). Hawk Hacks: Saturday at 10am (IDDC). Ultimate frisbee pickup: Sunday at 2pm (the quad).
4. CHECK -> ['Chess club: Thursday at 7pm']
   polish broke a fact; returning the draft, with the problem attached

RESULT: Chess club is on Thursday at 7pm (Olin 107). ...
model calls: 3
```

### Questions to Work Through

1.  The extract stage dropped the pizza message and the library question without saying so.  Is that the right behavior for a digest, and where in the output would you find out it happened?
2.  Before you ran the cell, could you have said it would cost exactly three model calls?  What property of the pattern lets you say so?
3.  `check_times` only checks days and times.  Name one other fact in a digest line that the polish stage could break and this check would miss, and write the one-line test that would catch it.

    *Hint:* Look at the four fields the extract stage produces, and at which ones `check_times` reads.

## 3.  A Router That Fails Closed

A router classifies each message once, into one label from a closed set, and then dispatches it.  Events and changes go on to the digest pipeline, questions go to an FAQ queue, and anything outside the set goes to a person.  When the help-desk router in the orchestration deck got an unexpected label, it silently fell back to "software."  This router fails closed and says so.

**Predict before you run:** how many model calls will routing the five messages cost, and how many messages will go on to the pipeline?

```python
# Section 3: a router.  One classification per message, a closed set, and a loud failure.
ROUTES = {"event": "digest", "change": "digest (marked UPDATED)", "question": "FAQ queue"}

def route(message):
    label = llm(CLASSIFY, message).strip().lower()
    if label not in ROUTES:            # closed-set guard: fail closed, and say so
        return label, "needs_human"
    return label, ROUTES[label]

CALLS.clear()
for_digest = []
for message in MESSAGES:
    label, destination = route(message)
    print(f"{label:<13} -> {destination:<24} {message[:44]}")
    if destination.startswith("digest"):
        for_digest.append(message)
print(f"\nmodel calls: {len(CALLS)}; {len(for_digest)} of {len(MESSAGES)} messages go on to the pipeline")
```

**You should see:**

```text
event         -> digest                   Chess club meets Thursday at 7pm in Olin 107
event         -> digest                   Hawk Hacks is Saturday at 10am in IDDC. Brin
change        -> digest (marked UPDATED)  Ultimate frisbee pickup moved to Sunday at 2
question      -> FAQ queue                Does anyone know if the library is open late
announcement  -> needs_human              Free pizza in the lobby, first come first se

model calls: 5; 3 of 5 messages go on to the pipeline
```

### Questions to Work Through

4.  The stand-in invented a label, `announcement`, that the prompt never offered.  Name the line that kept it out of the digest.  What would have happened to the pizza message under the deck's silent fallback?
5.  The router adds one model call per message.  For which inputs is that cost worth paying, and for which would you skip the router and send everything down the pipeline?
{: start="4"}

## 4.  A Supervisor Loop With a Roster, a Budget, and Stop Conditions

Now a model decides, each turn, which sub-agent runs next or whether to stop.  The supervisor's reply must be JSON in one of two shapes: `{"action": "call", "agent": ..., "input": ...}` or `{"action": "stop", "answer": ...}`.  Everything that keeps the loop safe lives in `supervise`, not in the supervisor:

- **The roster.**  Only `extractor`, `writer`, and `polisher` exist.  Any other name is refused and logged.
- **The budget.**  The loop runs at most `CONFIG["spawn_budget"]` turns.  Each turn's decision is itself a model call, so it is counted.
- **A refused stop.**  The supervisor may say "stop," but the answer must pass `check_times` first.  A model saying it is done is not the same as the work being done.
- **Four stop conditions**, each a `return` with a named status: the answer passed the check (`done`); the decision was not valid JSON (fail closed); the same sub-agent was asked for the same input twice (a loop); or the budget ran out.  Every early stop returns the newest text that passed the check, never just the newest text.

The stand-in supervisor below makes a plausible mistake: it always stops with the newest text, whether or not that text passed the check.

**Predict before you run:** which stop condition will end this run, after how many turns, and how many model calls?

```python
# Section 4: a supervisor loop.  A model picks the next move each turn; you own the roster,
# the budget, and every stop condition.
ROSTER = {"extractor": EXTRACT, "writer": DRAFT, "polisher": POLISH}

def naive_supervisor(task, transcript):
    """A scripted stand-in for the supervisor model.  It replies with the same JSON a real
    supervisor must produce, and it always stops with the newest text."""
    results = [t for t in transcript if "result" in t]
    done = [t["agent"] for t in results]
    if "extractor" not in done:
        return json.dumps({"action": "call", "agent": "extractor", "input": task})
    if "writer" not in done:
        return json.dumps({"action": "call", "agent": "writer", "input": results[0]["result"]})
    if "polisher" not in done:
        return json.dumps({"action": "call", "agent": "polisher", "input": results[-1]["result"]})
    return json.dumps({"action": "stop", "answer": results[-1]["result"]})

def supervise(task, decide, budget=CONFIG["spawn_budget"]):
    transcript, seen, facts = [], set(), None
    def best():                                        # the newest text that passed the check
        ok = [t["result"] for t in transcript if t.get("check") == "ok"]
        return ok[-1] if ok else None
    for turn in range(1, budget + 1):
        CALLS.append("SUPERVISOR")                     # the supervisor's own decision is a model call
        raw = decide(task, transcript)
        print(f"turn {turn}: {raw[:84]}")
        try:
            step = json.loads(raw)
        except json.JSONDecodeError:                   # stop condition: fail closed
            return {"status": "stopped: malformed decision", "answer": best(), "turns": turn}
        if step.get("action") == "stop":
            missing = check_times(facts, step.get("answer", "")) if facts else ["no facts yet"]
            if not missing:                            # stop condition: the check passed
                return {"status": "done", "answer": step["answer"], "turns": turn}
            transcript.append({"agent": "supervisor", "error": f"stop refused, missing {missing}"})
            print(f"   stop refused: missing {missing}")
            continue
        agent, text = step.get("agent"), step.get("input", "")
        if agent not in ROSTER:                        # closed roster, like the router's labels
            transcript.append({"agent": agent, "error": "unknown sub-agent"})
            print(f"   refused: {agent!r} is not on the roster")
            continue
        if (agent, text) in seen:                      # stop condition: the same call twice is a loop
            return {"status": f"stopped: repeated call to {agent}", "answer": best(), "turns": turn}
        seen.add((agent, text))
        result = llm(ROSTER[agent], text)              # the sub-agent sees only its own input
        entry = {"agent": agent, "result": result}
        if agent == "extractor":
            facts = result
        elif facts:
            entry["check"] = check_times(facts, result) or "ok"
        transcript.append(entry)
        print(f"   {agent} -> {result[:58].replace(chr(10), ' / ')}...  check={entry.get('check', '-')}")
    return {"status": f"stopped: budget of {budget} turns reached", "answer": best(), "turns": budget}

CALLS.clear()
outcome = supervise("\n".join(for_digest), naive_supervisor)
print(f"\nSTATUS: {outcome['status']} (turns: {outcome['turns']}, model calls: {len(CALLS)})")
print(f"ANSWER (newest text that passed the check): {outcome['answer']}")
```

**You should see** (turn 5 is the same as turn 4, and the answer is shortened):

```text
turn 1: {"action": "call", "agent": "extractor", "input": "Chess club meets Thursday at 7pm 
   extractor -> Chess club | Thursday | 7pm | Olin 107 / Hawk Hacks | Saturd...  check=-
turn 2: {"action": "call", "agent": "writer", "input": "Chess club | Thursday | 7pm | Olin 1
   writer -> Chess club is on Thursday at 7pm (Olin 107). Hawk Hacks is...  check=ok
turn 3: {"action": "call", "agent": "polisher", "input": "Chess club is on Thursday at 7pm (
   polisher -> Chess club: Friday at 7pm (Olin 107). Hawk Hacks: Saturday...  check=['Chess club: Thursday at 7pm']
turn 4: {"action": "stop", "answer": "Chess club: Friday at 7pm (Olin 107). Hawk Hacks: Satu
   stop refused: missing ['Chess club: Thursday at 7pm']
...
turn 6: {"action": "stop", "answer": "Chess club: Friday at 7pm (Olin 107). Hawk Hacks: Satu
   stop refused: missing ['Chess club: Thursday at 7pm']

STATUS: stopped: budget of 6 turns reached (turns: 6, model calls: 9)
ANSWER (newest text that passed the check): Chess club is on Thursday at 7pm (Olin 107). ...
```

Read the transcript as the loop's log.  Turns 1 to 3 repeat the pipeline, but this time the supervisor chose the order instead of you.  At turn 4 the supervisor tried to stop with the broken digest, and the check refused it.  It asked twice more, and the budget ended the run.  The loop still returned something useful, because the early-stop path returns the newest *checked* text and says that it stopped early.

Now make the other two stop conditions fire, one misbehaving supervisor at a time.

```python
# The other two stop conditions, each fired on purpose by a misbehaving stand-in supervisor.
def stubborn(task, transcript):        # asks for the same extraction forever
    return json.dumps({"action": "call", "agent": "extractor", "input": task})

def chatty(task, transcript):          # answers in prose instead of the required JSON
    return "Sure! First I will extract the events, then write the digest."

for name, decide in [("stubborn", stubborn), ("chatty", chatty)]:
    CALLS.clear()
    result = supervise("\n".join(for_digest), decide)
    print(f"-> {name}: {result['status']} (turns: {result['turns']}, model calls: {len(CALLS)})\n")
```

**You should see:**

```text
turn 1: {"action": "call", "agent": "extractor", "input": "Chess club meets Thursday at 7pm 
   extractor -> Chess club | Thursday | 7pm | Olin 107 / Hawk Hacks | Saturd...  check=-
turn 2: {"action": "call", "agent": "extractor", "input": "Chess club meets Thursday at 7pm 
-> stubborn: stopped: repeated call to extractor (turns: 2, model calls: 3)

turn 1: Sure! First I will extract the events, then write the digest.
-> chatty: stopped: malformed decision (turns: 1, model calls: 1)
```

### Questions to Work Through

6.  For each of the three runs, name the stop condition that fired and the line of `supervise` that fired it.
7.  In the naive run, the supervisor asked to stop with the same broken text on turns 4, 5, and 6.  Why did the repeated-call check not end the run at turn 5?  Would you change that, and what would the new status say?
8.  Why does every early stop return `best()` instead of the newest text in the transcript?  Point to the turn in the naive run where the two would differ.
9.  Write a stand-in supervisor that asks for an agent named `"fact_checker"`.  Predict what `supervise` prints and which stop condition ends the run, then run it.
{: start="6"}

## 5.  The Cost Table

This section runs the same digest through each pattern.  The cell reruns each one with its printing hidden and reports only the model calls it spent.

```python
# Section 5: model calls per pattern, for the same digest.
import contextlib
import io

def calls_for(run):
    CALLS.clear()
    with contextlib.redirect_stdout(io.StringIO()):   # hide each run's log; keep its cost
        run()
    return len(CALLS)

task = "\n".join(for_digest)
runs = [
    ("Fixed pipeline", lambda: digest_pipeline(MESSAGES)),
    ("Router, then pipeline", lambda: ([route(m) for m in MESSAGES], digest_pipeline(for_digest))),
    ("Supervisor (naive)", lambda: supervise(task, naive_supervisor)),
    ("Supervisor (stubborn)", lambda: supervise(task, stubborn)),
    ("Supervisor (chatty)", lambda: supervise(task, chatty)),
]
for name, run in runs:
    print(f"{name:<24} model calls: {calls_for(run)}")
```

**You should see:**

```text
Fixed pipeline           model calls: 3
Router, then pipeline    model calls: 8
Supervisor (naive)       model calls: 9
Supervisor (stubborn)    model calls: 3
Supervisor (chatty)      model calls: 1
```

Copy the table below into your notes, or into your spreadsheet on the no-code path, and fill in the last two columns from your runs.

| Pattern | Model calls | Who decided the order | Delivered a digest that passed the check? | Stopped because |
|---|---|---|---|---|
| Fixed pipeline (Section 2) | 3 | You, before the run | | |
| Router, then pipeline (Sections 3 and 2) | 5 + 3 | You; the model picks one label per message | | |
| Supervisor, naive (Section 4) | 9 | The model, each turn | | |
| Supervisor, stubborn (Section 4) | 3 | The model, each turn | | |
| Supervisor, chatty (Section 4) | 1 | The model, each turn | | |
{: .tb-full}

The supervisor spent three times the pipeline's calls to reach the same checked draft.  It reached that draft only because your code refused its stop and capped its turns.  This table measures the deck's heuristic, **choose the least dynamic pattern that solves the problem**, on one task.

### Questions to Work Through

10.  The chatty supervisor cost one call and the pipeline cost three.  Why is the chatty run still the worse result?  What does that tell you about reading a cost table without the "Stopped because" column?
11.  Describe one change to the task that would make the supervisor worth its cost.  What would the supervisor know at turn 3 that you could not have written down before the run?
{: start="10"}

> **Common mistakes.**  Putting the budget in the prompt ("stop after six steps" is a request; `range(budget)` is a guarantee).  Trusting the supervisor's "stop" without a check.  Returning the newest text on an early stop, when the newest text is the broken one.  Forgetting to count the supervisor's own decisions as model calls.  A router that maps an unknown label to a default.  Letting `json.loads` crash the loop instead of stopping with a named status.
{: .tb-pitfall data-title="Common Mistakes"}

---

# Part III: The Same Patterns on a Real Model

Pick one path.  Either one is enough.

## 6.  Code Path: Swap in Ollama

> This block talks to the Ollama server on your own machine at `localhost:11434`.  It needs Ollama with `llama3.2` pulled and Python with `requests` installed.  This is the setup from Before You Start in the Multi-Agent Patterns lab.
{: .tb-warning data-title="Runs on your machine, not here"}

Copy the cells from Part II into one file, `orchestrate.py`, and paste the block below directly after the Section 1 code.  Every pattern calls `llm()` by name when it runs, so redefining `llm()` here sends the pipeline, the router, and the sub-agents to Ollama with no other change.  Then change one argument in Section 4: pass `model_supervisor` instead of `naive_supervisor`.  `"format": "json"` asks Ollama to constrain the reply to JSON.  The fail-closed stop stays anyway, because a constraint on the format is not a guarantee about the content.

```python
import requests
import traceback

CONFIG.update({"model": "llama3.2", "provider_url": "http://localhost:11434/api/chat"})


def chat_once(system, user, json_only=False):
    """One request to Ollama.  Returns the text, or "" after printing a located error."""
    body = {"model": CONFIG["model"], "stream": False,
            "options": {"temperature": CONFIG["temperature"], "seed": CONFIG["seed"]},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}
    if json_only:
        body["format"] = "json"
    try:
        r = requests.post(CONFIG["provider_url"], json=body, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[orchestrate:chat_once] {e}")
        traceback.print_exc()
        return ""


def llm(system, user):
    """Replaces the stand-in: every pattern below now calls the real model."""
    CALLS.append(system[:24])
    return chat_once(system, user)


SUPERVISOR = ("You are an orchestrator. Choose the next step and reply with ONLY JSON. "
              "Available sub-agents: extractor, writer, polisher. "
              'Reply {"action":"call","agent":"<name>","input":"<text>"} '
              'to delegate, or {"action":"stop","answer":"<final text>"} when done.')


def model_supervisor(task, transcript):
    """A real supervisor.  supervise() already counts this call and parses the reply."""
    return chat_once(SUPERVISOR, f"TASK: Write the digest for these messages.\n{task}\n\n"
                                 f"TRANSCRIPT SO FAR:\n{json.dumps(transcript, indent=2)}",
                     json_only=True)
```

Run `python orchestrate.py` and save the full output.  Your output will differ from Part II, because a real model does not make the stand-in's scripted mistakes.  It makes its own.  An empty reply from `chat_once` means the request failed.  `supervise` then stops the run as a malformed decision rather than guess.

Add one row per pattern to your cost table for the real model.  Did the real polish stage keep every day and time?  Did the real router stay inside its three labels?  Which stop condition ended the real supervisor's run, after how many turns and model calls?  If two runs with the same seed differ, write down where.

## 7.  No-Code Path: Presets, Moved by Hand

On this path you are the code.  In Open WebUI, save each role as its own model: **Workspace**, **Models**, **+ Create a model**, with `llama3.2` as the base model and the prompt in **System Prompt**.  Under **Advanced Params**, set temperature to `0` and, if the field exists, the seed to `42`.  In Langflow, make each role a prompt node pointed at your local Ollama.  Either way, every reply you paste is one model call, and every call gets a row in your spreadsheet.

1.  **Pipeline.**  Save three presets (or nodes) with the `EXTRACT`, `DRAFT`, and `POLISH` prompts from Section 1.  Paste the five messages into the first, its output into the second, and that output into the third.  Then do the check yourself: is every day and time from the extract still in the polished digest?  If not, keep the draft and write down which fact was lost.
2.  **Router.**  Save a fourth preset with the `CLASSIFY` prompt and send each message to it in a fresh chat.  Any reply that is not exactly `event`, `change`, or `question` goes to "needs a person," and you write that down.  Do not reword the reply into the nearest label.  That would be the silent fallback.
3.  **Supervisor.**  Save a fifth preset with the `SUPERVISOR` prompt from Section 6.  Each turn, paste the task and your running transcript into it, and carry out its decision by hand with the other presets.  You enforce the controls: refuse any agent not on the roster, refuse a stop whose answer fails your check, stop at a repeated request, stop at a reply that is not valid JSON, and stop at six turns.  Log every turn: the decision as pasted, the agent, the result, the check, the running count of model calls, and the control you applied, if any.

Then fill in the cost table from your spreadsheet.  Which control was hardest to enforce by hand?  That answer tells you where the code path's guarantees come from.

---

# Part IV: Try One Pattern on Your Own Task

## 8.  Pick a Task and the Least Dynamic Pattern That Works

Choose a small task with an output you can check.  Your team's project task is one option, or one stage of it.  A task from another course, a club, or a job works just as well.  One pattern, one run, and one row in a cost table is enough here.  Work through these in order, in your notes or your spreadsheet:

1.  **Write the task in one sentence**, as input and output: "Given ___, produce ___."
2.  **Ask the deciding question:** can you list the steps and their order before the run starts?  If yes, start with a pipeline.  If each input is one of a few kinds and each kind has one handler, a router goes in front.  Use a supervisor only if the next step depends on what an earlier step finds.
3.  **Write one check a program can do.**  For example: a required field is present, a date or number survived, the reply parses as JSON, or the output is under a word limit.  If you cannot write any check without a model, write that down.  It is a finding, and it is the problem the critique-and-judge session takes up.
4.  **Write down the controls for your pattern.**  For a pipeline: the order and where the check sits.  For a router: the closed set of labels, and where anything else goes.  For a supervisor: the roster, the budget, and which stop condition you expect to fire.
5.  **Predict the number of model calls**, then run it and record what actually happened.  On the code path, `calls_for` from Section 5 does the counting.

On the code path, the cell below is a general pipeline with a check at the end.  It runs here on the digest to show it matches Section 2.  For your own task, replace the stages and the check.  Then pick one way to run it.  Either add one `if system == YOUR_PROMPT:` branch to `stand_in` that returns a reply you wrote, with one plausible mistake in it, or run it on Ollama with the Section 6 block.

```python
# Section 8: a general pipeline.  stages are system prompts in the order you wrote;
# check(outputs) returns a list of problems, where outputs[0] is the input.
def run_pipeline(stages, text, check):
    outputs = [text]
    for i, system in enumerate(stages, 1):
        outputs.append(llm(system, outputs[-1]))
        print(f"{i}. {system[:40]}... ->\n{outputs[-1]}")
    problems = check(outputs)
    print("CHECK ->", problems or "passed")
    if problems:                       # return the stage before the last, with the problem attached
        return outputs[-2], problems
    return outputs[-1], []

CALLS.clear()
result, problems = run_pipeline([EXTRACT, DRAFT, POLISH], "\n".join(MESSAGES),
                                lambda outs: check_times(outs[1], outs[-1]))
print(f"model calls: {len(CALLS)}; problems: {problems}")
```

**You should see** the same three outputs as Section 2, each labeled with the first words of its prompt, then:

```text
CHECK -> ['Chess club: Thursday at 7pm']
model calls: 3; problems: ['Chess club: Thursday at 7pm']
```

### Questions to Work Through

12.  Which pattern did you choose, and what was your answer to the deciding question in step 2?
13.  What did your check catch, or what would it have missed?  Name one failure you saw that no check of yours would have caught.
14.  How far off was your call-count prediction?  If you ran a supervisor, which stop condition fired, and was it the one you expected?
{: start="12"}

---

## Exercises

Everything below is optional.  Nothing here is collected or graded.  Each exercise ends with a check you apply yourself, so you can tell whether it worked.

1.  **A supervisor that stops correctly.**

    *What to do:* Write `careful_supervisor(task, transcript)`, a stand-in like `naive_supervisor` that makes the same first three moves.  When it stops, though, it should stop with the newest text in the transcript whose `check` is `"ok"`.  Run `supervise` with it.  Then, on the code path, add one sentence to the `SUPERVISOR` prompt that asks the real model for the same behavior, and rerun.

    *Starter hint:* The writer and polisher entries in the transcript carry a `check` field.  Filter on it before you choose the answer.  For the prompt, say what "done" means in terms the model can see in its transcript.

    *You've succeeded when:* `supervise` returns `done` in 4 turns with 7 model calls, and you can say in one sentence why that is still more than the pipeline's 3.  On the real model, you can report whether the added sentence changed which stop condition fired, with the transcript as evidence.

2.  **Your task, a second pattern.**

    *What to do:* Run your Part IV task through the next more dynamic pattern (a pipeline becomes a router in front of a pipeline, or a pipeline becomes a supervisor with the same roster).  Add its row to your cost table.

    *Starter hint:* Reuse `supervise` with your prompts in `ROSTER` and your check in place of `check_times`, or log the turns by hand on the no-code path.

    *You've succeeded when:* Your table has two rows for the same task, both with "Stopped because" filled in, and one sentence says whether the extra calls bought anything.

---

## Reflection Prompt

*Personal:* Think of a group project where someone declared a task done before it was.  What was the check that would have caught it, and who should have owned it?

*Technical:* For your own task in Part IV, which decision did you hand to the model that a line of code could have made instead?  If none, which one came closest?

*Societal:* An organization replaces a fixed approval workflow with a supervisor agent "for flexibility."  Every run now takes a different path.  What does an auditor lose, and which of this tutorial's controls would you require before agreeing that the system is accountable?

---

## Further Reading

- [Orchestration and Multi-Agent Patterns](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-orchestration.md), especially Loop Safety Controls, Termination, and The Supervisor Loop.
- [Orchestration Worked Example](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-orchestrationworkshop.md), the in-class build-along this tutorial follows, with the table mapping each control to the lab.
- The [Multi-Agent Patterns lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate), where the budget, the fail-closed parse, and the call counts are graded.
- [Agent Teams](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentTeams), for composing these patterns into a project team and choosing a topology.
- [Agent Frameworks](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentFrameworks), for frameworks that build the supervisor for you, and what they move into their own prompts when they do.
- [Pydantic AI From the Loop Up](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/PydanticAI), where a framework enforces the same kind of budget with `UsageLimits`.
- Anthropic engineering blog.  "Building Effective Agents" (2024, online).
