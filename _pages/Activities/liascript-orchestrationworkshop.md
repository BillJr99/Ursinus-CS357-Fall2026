<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-orchestrationworkshop.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-orchestrationworkshop.md

import: https://raw.githubusercontent.com/LiaTemplates/Pyodide/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Orchestration Worked Example: Build a Pipeline, a Router, and a Supervisor

*Orchestration and Multi-Agent Patterns* named the patterns: a fixed pipeline, a router, and a supervisor loop in which a model decides the next move, bounded by a roster, a budget, and a stop condition that stay yours.  Today we build all three on **one task**, end to end, and print every intermediate output.  The task is the nightly club digest from Tuesday's deck: five raw messages in, one short digest out, with every day and time intact.  The same task through all three patterns lets you compare them on the two things the [Multi-Agent Patterns lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate) grades: whether the loop stopped for a stated reason, and how many model calls it spent to get there.

The first half runs in this page with a scripted stand-in for the model, so every run is repeatable and every stop condition can be made to fire on purpose.  The second half swaps in Ollama with one function and runs the same code on your machine, or runs the same protocol by hand on the lab's no-code route.

**Today:** the [RAG Knowledge Base lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RAGKnowledgeBase) and your individual annotated bibliographies for the [Literature Review](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/LitReview) are due, and I hand out the [Multi-Agent Patterns lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate), due Thursday, December 3.  Sprint Check 1 is at the start of class.

---

## Directions and Group Roles

Work in your POGIL (Process Oriented Guided Inquiry Learning) team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  This is a build-along session.  The Manager asks for a prediction before every cell runs, and in particular for the number of model calls.  The Recorder keeps the team's cost table (Checkpoint 4).  The Presenter reports which stop condition fired in the team's run on a real model.  The Reflector watches for any decision the team handed to the model that a line of code could have made instead.  After class, answer the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Where You See It Today |
|---|---|---|
| **Fixed pipeline** | A sequence of model calls whose order you wrote before the run; each stage sees only the previous stage's output | Step 1: extract, draft, polish |
| **Check in code** | A test written in ordinary code at a seam, for a property a program can verify without a model | `check_times`, which confirms every day and time survived |
| **Router** | One classification into a closed set of labels, then a dispatch; anything outside the set fails closed to a person | Step 2: event, change, question, or `needs_human` |
| **Supervisor loop** | A loop in which a model chooses the next sub-agent each turn, or stops | Step 3, `supervise` |
| **Roster** | The fixed menu of sub-agents the supervisor may call; an unknown name is refused | `ROSTER`, three entries |
| **Budget** | A hard ceiling on turns, set in configuration rather than in the prompt, so a confused loop cannot run forever | `CONFIG["spawn_budget"]`, six turns |
| **Stop condition** | A rule in your code that ends the loop for a named reason: done and checked, malformed decision, repeated call, or budget reached | The four `return` lines in `supervise` |
| **Fail closed** | When output cannot be parsed or trusted, stop or hand it to a person rather than guess | The malformed-decision stop and the router's `needs_human` |

---

### Before You Start

**Have ready:** for Part II's code route, Ollama with `llama3.2` pulled and Python with `requests` installed, the setup from the lab's Step 0.2.  For the no-code route, Open WebUI or Langflow pointed at your local Ollama, as the lab's *Choose Your Path* describes.  Part I needs nothing; its cells run in this page.

**Run the cells in order.**  Each cell uses what the cell before it built.  If a cell reports a `NameError`, run the cells above it first.

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.

| Minutes | What we do |
|---|---|
| 0-10 | Sprint check: a member picked at random shows one thing running (Direction B: one cited finding), and each Coordinator says what is next and what is blocking |
| 10-15 | The task, the settings you own, and the stand-in model |
| 15-27 | Part I, Step 1: the fixed pipeline, and the check that catches the polish stage (Checkpoint 1) |
| 27-37 | Part I, Step 2: a router in front of the pipeline, with a closed set that fails closed (Checkpoint 2) |
| 37-55 | Part I, Step 3: the supervisor loop, a refused stop, the budget firing, and the other two stop conditions (Checkpoint 3) |
| 55-60 | The cost table: model calls per pattern for the same digest (Checkpoint 4) |
| 60-72 | Part II, the same code on a real model, or the same protocol by hand on the no-code route (Checkpoint 5) |
| 72-75 | The lab handout, and where today's controls appear in it |

Part III, the exercise on a supervisor that stops correctly, is self-paced.

## Sprint Check 1 (the first ten minutes)

Sprint Check 1 opens today's session, with no slides.  I pick one member of each team at random, who has 90 seconds to show one thing running (Direction B: one cited finding), and your Coordinator says what is next and what is blocking.  Every member's evidence line, the linked first line of their latest standup, should already be in the team note.  I mark each team shown or not yet.  The full protocol is in [Sprint Checks](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/PBLThread#sprint-checks).


---
# Part I: One Task Through Three Patterns

## Setup: The Task, the Settings You Own, and the Stand-In

Five messages arrived today.  Three are events for the digest, one is a question that belongs in an FAQ queue, and one is something the categories did not anticipate.  `CONFIG` holds the settings you own, outside any prompt, the same way the lab keeps its round budget in `config.json`.  The four system prompts are each one sentence, the small-context discipline from Tuesday.  `llm()` is the one function every pattern calls, and every call is counted in `CALLS`.

In this page, `llm()` calls `stand_in()`: fixed rules per role, not a language model.  It extracts events with a regular expression, writes one sentence per event, and, in the polish stage, makes on purpose the mistake Tuesday's Question 6 warned about: it changes "Thursday" to "Friday" while editing for concision.  It also returns a label outside the closed set for the pizza message.  Both mistakes are scripted so you can watch the controls catch them every time.

```python
# Setup: the task, the settings you own, and a scripted stand-in for the model.
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
    visible and repeatable.  Part II replaces this function with a real model call."""
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
    if system == POLISH:   # the mistake the orchestration deck's Question 6 warned about
        return user.replace(" is on ", ": ").replace("Thursday", "Friday")
    if system == CLASSIFY:
        if "moved" in user or "cancel" in user:
            return "change"
        if user.rstrip().endswith("?"):
            return "question"
        return "event" if EVENT.match(user) else "announcement"   # outside the closed set
    return ""

def llm(system, user):
    """The one function every pattern calls.  In this page it is the stand-in."""
    CALLS.append(system[:24])
    return stand_in(system, user)

print(f"{len(MESSAGES)} messages; settings {CONFIG}")
print(repr(llm(CLASSIFY, MESSAGES[0])), repr(llm(EXTRACT, MESSAGES[0])))
CALLS.clear()
```
@Pyodide.eval

**You should see:**

```text
5 messages; settings {'spawn_budget': 6, 'temperature': 0.0, 'seed': 42}
'event' 'Chess club | Thursday | 7pm | Olin 107'
```

## Step 1: A Fixed Pipeline With a Check at the Seam

**Goal:** extract, draft, and polish in an order you wrote, with every intermediate printed, and a check in code after the last stage.  The check is not a fourth model call.  Whether "Thursday at 7pm" appears in the digest is a property a program can verify exactly, so a program verifies it.  When the check fails, the pipeline stops for a stated reason and returns the last version that passed, with the problem attached, the same contract the lab's critique loop uses when its budget runs out.

```python
# Step 1: a fixed pipeline.  You wrote the order; the code checks the seam the model cannot.
def check_times(facts, text):
    """A check in code, not a model: every extracted day and time must survive into the text."""
    missing = []
    for row in facts.splitlines():
        name, day, time, _ = [x.strip() for x in row.split("|")]
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
@Pyodide.eval

**You should see:**

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

> **Checkpoint 1.**  The extract stage never saw the pizza message's lack of a day and time, and dropped it silently.  Is that the right behavior for a digest, and where would you find out it happened?  Then: the pipeline cost exactly three model calls.  Could you have said so before running it?  That is the property a fixed pipeline buys.

## Step 2: A Router in Front of the Pipeline

**Goal:** one classification per message into a closed set, then a dispatch: events and changes go on to the digest pipeline, questions go to an FAQ queue, and anything outside the set goes to a person.  Tuesday's router fell back silently to "software."  This one fails closed and says so, which is the louder failure Tuesday's Question 5 asked for.

```python
# Step 2: a router.  One classification per message, a closed set, and a loud failure.
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
@Pyodide.eval

**You should see:**

```text
event         -> digest                   Chess club meets Thursday at 7pm in Olin 107
event         -> digest                   Hawk Hacks is Saturday at 10am in IDDC. Brin
change        -> digest (marked UPDATED)  Ultimate frisbee pickup moved to Sunday at 2
question      -> FAQ queue                Does anyone know if the library is open late
announcement  -> needs_human              Free pizza in the lobby, first come first se

model calls: 5; 3 of 5 messages go on to the pipeline
```

> **Checkpoint 2.**  The stand-in invented a fifth label, `announcement`, exactly as Tuesday's Question 2 predicted a real router would.  Name the line that kept it out of the digest.  Then count: the router adds one model call per message, so routing these five cost five calls before the pipeline's three.  For which inputs is that cost worth paying?

## Step 3: A Supervisor Loop With a Budget and Stop Conditions

**Goal:** the same digest, but now a model decides each turn which sub-agent runs next, or whether to stop.  The supervisor's reply must be JSON, the same two shapes as Tuesday's Code Cell: `{"action": "call", "agent": ..., "input": ...}` or `{"action": "stop", "answer": ...}`.  Everything that keeps the loop safe is in `supervise`, not in the supervisor:

- **The roster.**  Only `extractor`, `writer`, and `polisher` exist.  Any other name is refused and logged.
- **The budget.**  At most `CONFIG["spawn_budget"]` turns, and each turn's decision is itself a model call, so it is counted.
- **Four stop conditions**, each a `return` with a named status: the answer passed the check (`done`); the decision was not valid JSON (fail closed); the same sub-agent was asked for the same input twice (a loop, caught by an idempotency check); or the budget ran out.  Every early stop returns the newest text that passed the check, flagged, never the newest text.
- **A refused stop.**  The supervisor may say "stop," but the answer must pass `check_times` first, the explicit, machine-checkable stop condition from Tuesday's section on termination.

The stand-in supervisor below is scripted to make a plausible mistake: it always stops with the newest text, whether or not that text passed the check.

```python
# Step 3: a supervisor loop.  A model picks the next move each turn; you own the roster,
# the budget, and every stop condition.
ROSTER = {"extractor": EXTRACT, "writer": DRAFT, "polisher": POLISH}

def naive_supervisor(task, transcript):
    """A scripted stand-in for the supervisor model.  It replies with the same JSON a real
    supervisor must produce, and it makes a plausible mistake: it always stops with the
    newest text, whether or not that text passed the check."""
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
@Pyodide.eval

**You should see:**

```text
turn 1: {"action": "call", "agent": "extractor", "input": "Chess club meets Thursday at 7pm 
   extractor -> Chess club | Thursday | 7pm | Olin 107 / Hawk Hacks | Saturd...  check=-
turn 2: {"action": "call", "agent": "writer", "input": "Chess club | Thursday | 7pm | Olin 1
   writer -> Chess club is on Thursday at 7pm (Olin 107). Hawk Hacks is...  check=ok
turn 3: {"action": "call", "agent": "polisher", "input": "Chess club is on Thursday at 7pm (
   polisher -> Chess club: Friday at 7pm (Olin 107). Hawk Hacks: Saturday...  check=['Chess club: Thursday at 7pm']
turn 4: {"action": "stop", "answer": "Chess club: Friday at 7pm (Olin 107). Hawk Hacks: Satu
   stop refused: missing ['Chess club: Thursday at 7pm']
turn 5: ...
turn 6: ...
   stop refused: missing ['Chess club: Thursday at 7pm']

STATUS: stopped: budget of 6 turns reached (turns: 6, model calls: 9)
ANSWER (newest text that passed the check): Chess club is on Thursday at 7pm (Olin 107). ...
```

Read the transcript as the loop's log.  Turns 1 to 3 are the pipeline again, chosen by the supervisor instead of written by you.  At turn 4 the supervisor tried to stop with the broken digest, and the check refused it.  It then asked twice more to stop with the same broken text, and the budget ended the run.  The loop still returned something useful, because the early-stop path returns the newest *checked* text and says that it stopped early.

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
@Pyodide.eval

**You should see:**

```text
turn 1: {"action": "call", "agent": "extractor", "input": "Chess club meets Thursday at 7pm 
   extractor -> Chess club | Thursday | 7pm | Olin 107 / Hawk Hacks | Saturd...  check=-
turn 2: {"action": "call", "agent": "extractor", "input": "Chess club meets Thursday at 7pm 
-> stubborn: stopped: repeated call to extractor (turns: 2, model calls: 3)

turn 1: Sure! First I will extract the events, then write the digest.
-> chatty: stopped: malformed decision (turns: 1, model calls: 1)
```

> **Checkpoint 3.**  For each of the three runs, name the stop condition that fired and the line of `supervise` that fired it.  Then answer Tuesday's Question 19 with evidence from your screen: what happens at the moment the budget is hit, and why does the status say `stopped` rather than presenting the transcript as a finished answer?

## The Cost Table

**Checkpoint 4.**  The same digest, three ways.  Fill in the last two columns from your runs, and have the Recorder keep the table.

| Pattern | Model calls | Who decided the order | Delivered a digest that passed the check? | Stopped because |
|---|---|---|---|---|
| Fixed pipeline (Step 1) | 3 | You, before the run | | |
| Router, then pipeline (Steps 2 and 1) | 5 + 3 | You; the model picks one label per message | | |
| Supervisor (Step 3) | 9 | The model, each turn | | |

The supervisor spent three times the pipeline's calls to reach the same checked draft, and it reached it only because your code refused its stop and capped its turns.  That is the "least dynamic pattern that solves the problem" heuristic from Tuesday, measured on one task.  The supervisor earns its cost only when you cannot write the order down in advance.

### Common Mistakes

- **Putting the budget in the prompt.**  "Stop after six steps" in a system prompt is a request.  `range(budget)` in your loop is a guarantee.  Keep the number in configuration, as the lab does with `round_budget`.
- **Trusting the supervisor's "stop."**  A model saying it is done is self-assessed completion.  Check the answer against something a program can verify before you accept it.
- **Returning the newest text on an early stop.**  The newest text in Step 3 was the broken one.  Return the newest text that passed the check, and say that the run stopped early.
- **Not counting the supervisor's own calls.**  Every decision is a model call.  A supervisor that makes six decisions to dispatch three sub-agents spent nine calls, not three.
- **Silent fallbacks.**  A router that maps an unknown label to a default hides the failure.  Fail closed to a person, and log it.
- **Letting a parse error crash the loop.**  Wrap `json.loads` and stop with a named status, as `supervise` does, rather than letting an exception end the run with no record.

---
# Part II: The Same Code on a Real Model

## Code Route: Swap in Ollama

> **Runs on your machine, not here.**  This block talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.

Copy the five cells from Part I into one file, `orchestrate.py`.  Paste the block below directly after the Setup cell's code.  Because every pattern calls `llm()` by name when it runs, redefining `llm()` here sends the pipeline, the router, and the sub-agents to Ollama with no other change.  Then change one argument in Step 3: pass `model_supervisor` instead of `naive_supervisor`.  The supervisor prompt is the one from Tuesday's Code Cell, and `"format": "json"` asks Ollama to constrain the reply to JSON, the structured-output setting from the *Tool Use* readings.  The fail-closed stop stays, because a constraint on the format is not a guarantee about the content.

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

Run `python orchestrate.py` and save the full output.  Your outputs will differ from the page, because a real model does not make the stand-in's scripted mistakes; it makes its own.  An empty reply from `chat_once` means the request failed, and `supervise` will stop it as a malformed decision rather than guess.

> **Checkpoint 5 (code route).**  Add a row to the Checkpoint 4 table for each pattern on the real model.  Did the real polish stage keep every day and time?  Did the real router stay inside its four labels?  Which stop condition ended the real supervisor's run, after how many turns and model calls?  If the run differs between two executions with the same seed, write down where.

## No-Code Route: Run the Protocol by Hand

The lab's no-code route runs each role as a saved Open WebUI preset, or as a prompt node on a Langflow canvas, and moves text between them by hand.  Today's three patterns work the same way, and you become the code.

1.  **Pipeline.**  Save three presets with the `EXTRACT`, `DRAFT`, and `POLISH` system prompts from the Setup cell.  Paste the five messages into the first, its output into the second, and that output into the third.  Then do the check yourself: is every day and time from the extract still in the polished digest?  If not, keep the draft and write down why.
2.  **Router.**  Save a fourth preset with the `CLASSIFY` prompt and send each message to it separately.  Any reply that is not exactly `event`, `change`, or `question` goes to "needs a person," and you write that down.
3.  **Supervisor.**  Save a fifth preset with the `SUPERVISOR` prompt from the code route.  Each turn, paste the task and your running transcript into it, and carry out its decision by hand with the other presets.  You enforce the controls: refuse any agent not on the roster, refuse a stop whose answer fails your check, stop at a repeated request, and stop at six turns.  Log every turn in a spreadsheet: the decision, the result, the check, and the running count of model calls.

> **Checkpoint 5 (no-code route).**  Add your rows to the Checkpoint 4 table from the spreadsheet.  Which control was hardest to enforce by hand, and what does that tell you about where the code route's guarantees come from?

## Where These Controls Appear in the Lab

| Today | In the Multi-Agent Patterns lab |
|---|---|
| `CONFIG["spawn_budget"]`, read from configuration | `round_budget` and the debate's `num_rounds` in `config.json` (Before You Start) |
| The malformed-decision stop | Invalid critic JSON fails closed: the loop treats it as "revise" and logs it (Part A) |
| The newest checked text returned on an early stop, flagged | On budget exhaustion, the loop returns the final draft with its outstanding critique attached (Part A, Practice) |
| `check_times`, a check in code at a seam | Answer extraction anchored on a required `ANSWER:` line, with a located warning when it is missing (Part B, Practice) |
| `CALLS`, counted per pattern | Each Try It counts the pattern's model calls against a single call (Parts A to C); the matched-budget shootout is in the [Measuring Multi-Agent Patterns](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/MultiAgentMeasurement) tutorial |
| Located error messages such as `[orchestrate:chat_once]` | Every model call wrapped in a handler that prints a located message and a traceback (the proficient level of each Part's rubric row) |

The supervisor's writer, check, and refused stop are already a critique-and-refine loop with a critic that is a program instead of a model.  Part A of the lab replaces that program with a critic model and a written rubric.  Measuring when that critic is wrong is the first part of the [Measuring Multi-Agent Patterns](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/MultiAgentMeasurement) tutorial.

---
# Part III: Exercise and Wrap-Up

## Exercise: A Supervisor That Stops Correctly (self-paced)

- *What to do*: Write `careful_supervisor(task, transcript)`, a stand-in like `naive_supervisor` that follows the same first three moves, but when it stops, stops with the newest text in the transcript whose `check` is `"ok"`.  Run `supervise` with it in this page.  Then, on the code route, add one sentence to the `SUPERVISOR` prompt that asks for the same behavior from the real model, and rerun.
- *Starter hint*: The transcript entries for the writer and polisher carry a `check` field.  Filter on it before you choose the answer.  For the prompt, say what "done" means in terms the model can see in its transcript.
- *You've succeeded when*: In this page, `supervise` returns `done` in 4 turns with 7 model calls, and you can say in one sentence why that is still more than the pipeline's 3.  On the real model, you can report whether the added sentence changed which stop condition fired, with the transcript as evidence.

## Reflection Prompt

*Personal:* Today you were the code on the no-code route, or you watched the code refuse a model's "stop."  Think of a group project where someone declared a task done before it was.  What was the check that would have caught it, and who should have owned it?

*Technical:* The supervisor reached the same checked draft as the pipeline at three times the cost.  Describe a task, from your Final Project if you can, where you could not write the order down in advance, and say which of today's four stop conditions you would need first.

*Societal:* An organization replaces a fixed approval workflow with a supervisor agent "for flexibility."  Every run now takes a different path.  What does an auditor lose, and which of today's controls would you require before agreeing that the system is accountable?

---

-> Coming Up Next: *Critique, Consensus, and the LLM Judge: One Loop, Three Uses* (Tuesday) takes the check you wrote today and asks what happens when it cannot be a program: a critic model that feeds issues back to a generator, several generators compared by meaning, and a judge that scores against a rubric.  That loop is the core of the Multi-Agent Patterns lab you received today.  Have `supervise` and your cost table ready.

## Further Reading

- [From Second Brain to Chief of Staff: one personal agent followed into production](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/ProductionAssistant)
- [Orchestration Patterns](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OrchestrationPatterns), today's three patterns on their own, and [Measuring Multi-Agent Patterns](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/MultiAgentMeasurement), for the measurement the lab leaves out.
- The [Multi-Agent Patterns lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate), where the budget, the fail-closed parse, and the call counts are graded.
- [Orchestration and Multi-Agent Patterns](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-orchestration.md), especially Loop Safety Controls and Termination, for the controls this session implemented.
- [Pydantic AI From the Loop Up](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/PydanticAI): the RAG lab's agent caps its loop with `UsageLimits(request_limit=4)`, the same budget idea enforced by a framework instead of your own `range()`.
- [Agent Frameworks](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentFrameworks), for frameworks that build the supervisor pattern for you, and what they move into their own prompts when they do.
- Anthropic engineering blog.  "Building Effective Agents" (2024, online).  The workflow patterns built today.
