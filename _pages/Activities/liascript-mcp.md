<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-mcp.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-mcp.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# MCP: Connecting Agents to Tools and Your Obsidian Vault

In the *Tool Use and Function Calling* activity each team hand-wired tools into one agent.  That approach does not scale to the world.  Today tools become shared infrastructure: web APIs (Application Programming Interfaces) are the world's function registry, and the Model Context Protocol (MCP) is a standard way for any agent to discover and call any tool server.  You leave with a tiny tool server you built yourself, the same server extended to read and write your Obsidian vault, and a trust checklist for connecting servers you did not write.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **API (Application Programming Interface)** | A published contract that lets one program call functions in another program over the network, without knowing how the other program works internally. | Calling `GET /weather?city=Philadelphia` to get current weather data from a weather service. |
| **REST API** | A style of web API where you send requests to URLs (called endpoints) and receive data back as JSON text.  REST stands for Representational State Transfer. | `GET https://api.weather.gov/points/40.19,-75.46` returns campus weather as JSON. |
| **MCP (Model Context Protocol)** | A standard protocol that lets any AI agent discover and call tools from any compliant tool server, without custom integration code for each pair.  Think of it as USB for AI tools. | Your agent calls `GET /tools/list` to discover what a server can do, then calls `POST /tools/call` to use a tool. |
| **N-by-M Problem** | With N agent applications and M services, bespoke (custom, one-off) integration needs up to N × M separate adapters.  MCP reduces this to N + M because both sides follow one standard. | 4 agents × 6 services = 24 adapters without MCP; 4 + 6 = 10 with MCP. |
| **Tool Discovery** | The agent asks a server at runtime "what can you do?" instead of carrying a hard-coded tool list in its source code. | `requests.get("http://localhost:8765/tools/list")` returns the current tool menu. |
| **JSON-RPC** | A protocol for making remote function calls by sending JSON messages.  The full MCP specification is built on JSON-RPC. | `{"method": "tools/call", "params": {"name": "hours", "arguments": {"facility": "library"}}}` |
| **OAuth 2.0** | An authorization standard that lets a user grant an app limited, revocable access to their account on another service without sharing their password; the app receives a scoped token instead. | Clicking "Allow this app to read my Google Calendar" issues a token, not your password. |
| **Trust boundary** | The line between the model, which can be argued with, and the tool server, which runs code you wrote: the server holds the secret, checks the arguments the same way every time, and decides what comes back into the context window. | Part IIc: `github_issue` reads its token from the server's environment and returns four redacted fields; the model never sees the token or the full response. |
| **No-code automation / connector** | A platform that builds service-to-service workflows by configuring pre-built connectors (each wrapping a service's OAuth/REST API) instead of writing integration code. | Power Automate, Zapier, Make, and IFTTT expose Google, Asana, and hundreds of services as ready-made connectors. |

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Part I, the integration problem: the services you already use, then why N times M connectors was never going to work |
| 10-20 | Model 1, count the adapters and report the arithmetic |
| 20-40 | Part II, build the tiny tool server and connect a client to it |
| 40-60 | Part IIb, put a vault of Markdown notes behind the same server and trace one gated write |
| 60-70 | Part III, start the exercises: add a tool and confirm the client discovers it |
| 70-75 | Report out and the reflection prompt |

---
# Part I: The Integration Problem

## Warm-Up: The Services You Already Use

Make the integration problem personal before you study it in the abstract.  As a team, brainstorm the online services and apps each of you relies on in a typical week: email and calendars, task and project managers, banking and budgeting, cloud storage, music, campus systems.

For every service someone names, ask the question this whole unit turns on: could an agent reach it, and how?  Check whether each service exposes:

- an **MCP server**, so an agent can discover and call its tools directly through the protocol we study today;
- an **OAuth 2.0 / REST API**, so an agent can call it over HTTP with the user's delegated, revocable permission; or
- **neither**, no public programmatic access, so a human (or brittle screen-scraping) is the only way in.

Look each service up rather than guessing; the answer keeps changing as vendors ship new APIs and MCP servers.  A few examples to start the conversation:

| Service | What people use it for | Programmatic access to investigate |
|---|---|---|
| **Google** (Gmail, Calendar, Drive) | Email, scheduling, documents, storage | Mature OAuth 2.0 REST APIs per product; a fast-growing set of MCP servers wraps them |
| **Asana** | Team task and project tracking | Documented OAuth 2.0 REST API for tasks and projects; MCP servers are available |
| **Personal Capital / Empower** | Personal budgeting and net-worth tracking | No official public API.  This is a service that is *not* openly agent-reachable; access means unofficial scraping or a third-party data aggregator |

[[___ List 3-5 services your team uses.  For each, mark MCP? / OAuth-REST? / neither, and note how you found out. ___]]

> **Talking point:** A pattern is already forming.  Google and Asana give an agent a *standard front door* (OAuth/REST, increasingly MCP); Personal Capital gives it *no* front door at all.  That split (a few services are agent-reachable, many are walled off, and each open one has its own auth quirks) is the fragmentation the rest of this activity is about.  Keep your team's list handy; you will recognize the N-by-M problem in it on the next slide.

---

## 1.  APIs, Then the N-by-M Problem

Connecting agents to many services gets expensive without a shared standard.  In this Part you work through the arithmetic of how MCP reduces that cost from multiplicative to additive.

**Why this matters:** Think about phone chargers before USB-C existed.  Every phone maker had a different cable, so you needed a different charger for every device you owned.  USB-C created one standard: one cable works with any compliant device.  MCP does the same thing for AI tools.  Before MCP, every agent team wrote custom glue code to connect to every service.  With MCP, you write a service once as a compliant MCP server, and any MCP client (any agent application anywhere) can use it.  The analogy stops at the plug: USB-C says nothing about what the device does once connected, and neither does MCP.

An API is a published contract for calling someone else's functions over the network.  REST APIs expose endpoints (`GET /weather?city=...`) that return JSON.  Your agent's tools so far were local Python, but nothing stops a tool's body from being an HTTP request.  Suddenly the agent can reach weather, library catalogs, campus systems, anything with an API.

The problem is multiplication.  With $N$ agent applications and $M$ services, bespoke integration requires up to $N \times M$ adapters, each with its own schema conventions and auth quirks.  Computing solves such problems with *protocols*: USB for peripherals, HTTP for documents, LSP (the Language Server Protocol) for editors and languages.

MCP is that protocol for tools.  A service wraps itself once as an **MCP server** that exposes `tools/list` (machine-readable schemas like the ones you wrote by hand in the *Tool Use and Function Calling* activity, now discovered at runtime) and `tools/call`.  Any **MCP client** (a chat app, an IDE, your Python agent) connects, lists, and calls.  Integration cost drops from $N \times M$ to $N + M$.  The agent loop is unchanged; what changes is that tools arrive by discovery rather than by hard-coding.

Remember two things from this section.  A protocol turns a multiplication into an addition.  The protocol standardizes how tools are found and called, not what they do.

---

## Model 1: Count the Adapters

A campus has 4 agent applications (advising bot, library bot, IT helpdesk bot, research assistant) and 6 services (catalog, calendar, LMS, ticketing, weather, room booking).

### Critical Thinking Questions

1.  Compute the worst-case adapter count without a protocol, and the count with MCP.  Show the arithmetic.

   > *Hint: Multiply for bespoke; add for MCP.  Then ask: what happens if the campus adds a 5th service?*

2.  The library upgrades its catalog API.  In each world (bespoke vs. MCP), who must change code, and how many codebases are touched?

   > *Hint: In the bespoke world, draw arrows from "catalog" to every agent that uses it.  Each arrow is a codebase change.*

3.  In the *Tool Use and Function Calling* activity you wrote tool schemas by hand.  Which MCP method replaces that step, and what new *trust* question does runtime discovery create?  (Hold this thought for the governance unit.)

   > *Hint: If you receive a tool schema from a stranger's server, what are you agreeing to when you call it?*

---

# Part II: A Tiny Tool Server

## 2.  Speaking the Pattern in Code

**Why this matters:** The theory of MCP is helpful, but building a minimal version yourself makes the architecture concrete and memorable.  The server below is not production MCP.  It is a teaching implementation of the same two-endpoint pattern: list your tools, then call a tool by name.  Real MCP adds session management, capability negotiation, and streaming, but the core idea is identical.

In this Part you write a small Flask web server (Flask is a Python library for creating web endpoints, URLs your code can respond to over HTTP) that exposes two routes: `/tools/list` returns the server's tool descriptions, and `/tools/call` runs a named tool.  You then run a client that discovers and calls those tools without any hard-coded knowledge of what tools exist.

Full MCP runs over JSON-RPC with sessions and capability negotiation.  The essence, a discoverable registry plus a call dispatcher, fits in a screen of Flask.  We build the essence.

You can run the server with:

```bash
# In a terminal: start the server
pip install flask requests
python server.py

# In a second terminal: test that it's alive
curl http://localhost:8765/tools/list
```

---

## Code Cell

> **Runs on your machine, not here.**  This cell starts a server and binds a port, which a web page cannot do.  Copy it into your course container and run it there.

```python
# server.py: run with `python server.py`, then query it from another terminal.
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Tool implementations (the actual functions the server knows how to run) ---

def room_lookup(building: str):
    # A simple dictionary lookup: building name -> list of room numbers
    rooms = {"pfahler": ["007", "012", "108"], "iddc": ["116", "214"]}
    return rooms.get(building.lower(), [])

def hours(facility: str):
    # Another dictionary lookup: facility name -> hours string
    table = {"library": "8am-midnight M-R", "gym": "6am-10pm daily"}
    return table.get(facility.lower(), "unknown facility")

# --- TOOLS registry: maps each tool name to its function AND its schema ---
# The schema is what the client receives when it calls /tools/list.
# This is the key MCP insight: the server describes its own capabilities.
TOOLS = {
  "room_lookup": {"fn": room_lookup,
    "schema": {"name": "room_lookup",
               "description": "List classroom numbers for a campus building.",
               "parameters": {"building": "string"}}},
  "hours": {"fn": hours,
    "schema": {"name": "hours",
               "description": "Operating hours for a campus facility.",
               "parameters": {"facility": "string"}}},
}

# --- MCP-style endpoints ---

@app.get("/tools/list")
def tools_list():
    # Returns only the schemas (not the functions); clients learn what exists here
    return jsonify([t["schema"] for t in TOOLS.values()])

@app.post("/tools/call")
def tools_call():
    try:
        body = request.get_json()
        name, args = body["name"], body.get("arguments", {})
        if name not in TOOLS:
            return jsonify({"error": "unknown tool"}), 404
        # Look up the function by name and call it with the provided arguments
        return jsonify({"result": TOOLS[name]["fn"](**args)})
    except Exception as e:
        print(f"[mcpserver:tools_call] {e}")
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8765, threaded=True)
```

---

The client code below runs three steps in order: (1) ask the server what tools exist, (2) define a reusable function for calling any of them by name, and (3) demonstrate both tools.  The client never imports or defines `room_lookup` or `hours`; it learns they exist at runtime from the server's response.

## Code Cell

> **Runs on your machine, not here.**  This cell makes network calls that the page sandbox blocks.  Copy it into your course container and run it there.

```python
# client side: discover the server's tools, hand them to the model, dispatch calls.
# This is a simplified MCP client: it asks "what can you do?" then does it.
import requests

SERVER = "http://localhost:8765"

# Step 1: Discover what tools exist, no hard-coding required
discovered = requests.get(f"{SERVER}/tools/list", timeout=10).json()
print("discovered tools:", [t["name"] for t in discovered])
# Output: discovered tools: ['room_lookup', 'hours']

# Step 2: Define a reusable call function
def call_remote(name, arguments):
    r = requests.post(f"{SERVER}/tools/call",
                      json={"name": name, "arguments": arguments}, timeout=10)
    return r.json()

# Step 3: Use the tools; the client never needed to know these existed at startup
print(call_remote("hours", {"facility": "library"}))
# Output: {'result': '8am-midnight M-R'}

print(call_remote("room_lookup", {"building": "Pfahler"}))
# Output: {'result': ['007', '012', '108']}
```

---

## Model 2: Discovery in Action

### Critical Thinking Questions

4.  Your client knew nothing about rooms or hours at startup, yet ended up calling both.  Trace exactly where the knowledge entered the program.  How does this differ from the hard-coded `TOOLS` list you built in the *Tool Use and Function Calling* activity?

   > *Hint: At what line of the client code does the client first learn that "room_lookup" exists?  Now compare to the Tool Use and Function Calling activity's file, where tool names appeared directly in the source.*

5.  Convert your agent from the *Tool Use and Function Calling* activity to use `discovered` schemas (sketch the three changed lines).  What stays identical?  What does that invariance tell you about good layering?

   > *Hint: The agent loop (perceive, plan, act, observe) does not need to know whether tools came from discovery or hard-coding.  What does this tell you about the value of keeping layers separate?*

6.  A malicious server could describe a tool as "harmless lookup" while its implementation deletes files.  Which side of the protocol can lie, and what defenses (allowlists, sandboxes, human gates, audits) operate at which layer?

   > *Hint: Think of a restaurant: you trust the menu description, but what stops a bad kitchen from putting something harmful in your food?  Who provides each kind of protection?*

> **Common Misconception:** Many students assume that because MCP standardizes the interface, it also guarantees the safety of the tools behind it.  It does not.  MCP standardizes *how* you discover and call tools; it says nothing about *what those tools are allowed to do*.  A perfectly spec-compliant MCP server could read your files, make purchases, or send emails on your behalf.  You establish trust by checking who wrote the server, what permissions it requests, and whether it has been audited, not by assuming the protocol protects you.

The primary value MCP adds over each team writing custom tool integrations is:

[( )] It makes models more accurate
[(X)] It standardizes discovery and invocation so any client can use any compliant tool server
[( )] It eliminates the need for authentication
[( )] It runs tools inside the model for speed

---

> **A no-code route to the same problem.**  Microsoft Power Automate wires services together without a line of code, and it is worth seeing next to MCP.  The optional activity [Agentic OpenWebUI and No-Code Integration](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgenticOpenWebUI) covers it.

# Part IIb: A Vault Behind a Tool Server

## 2b.  Your Notes as Tools

The two campus lookups in Part II were stand-ins.  The same server pattern works over something you care about: an Obsidian vault, which is a folder of Markdown files.  In this Part you give the server three vault tools and watch a client discover them, exactly as it discovered `hours`.  The three tools cover the read path and the write path from the [Obsidian Sync tutorial](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/ObsidianSync).  `search_notes` finds notes whose text contains a phrase.  `read_note` returns one note by its path.  `append_daily_note` adds a line to today's daily note, and it refuses to write unless the call includes `confirm` set to true.  Reading is cheap to allow; writing changes your files, so the write tool carries a gate.  One thing to say plainly: a real MCP server speaks JSON-RPC over stdio (standard input and output, for a server launched as a local process) or over HTTP.  This deck's Flask server uses two plain HTTP routes instead.  It is the *pattern*, list then call, not the *protocol*.  When you are ready for the real thing, the Hugging Face MCP Course in Further Reading builds a compliant server step by step, and the [Tools and MCP lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/ToolsMCP) offers your Obsidian vault as one MCP option.

Set `VAULT` to your own vault path before you run the cell.  If you do not have a vault yet, make a folder with two or three `.md` files in it; the server does not care which editor made them.  Start it with `python vault_server.py`, then confirm the three tools are advertised with `curl http://localhost:8766/tools/list` in a second terminal.

---

## Code Cell

> **Runs on your machine, not here.**  This cell starts a server and reads files on your disk, which a web page cannot do.  Copy it into your course container and run it there.

```python
# vault_server.py: server.py with three vault tools. Run with `python vault_server.py`.
# The endpoints are the ones from server.py; only the tools are new.
import datetime
import pathlib
from flask import Flask, request, jsonify

app = Flask(__name__)

VAULT = pathlib.Path.home() / "Documents" / "Obsidian" / "MyVault"

# --- Vault tools (three functions over a folder of Markdown files) ---

def search_notes(query: str):
    # Case-insensitive text search over every .md file under the vault
    hits = []
    for md_file in sorted(VAULT.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        if query.lower() in text.lower():
            hits.append(str(md_file.relative_to(VAULT)))
    return hits

def read_note(path: str):
    # Return one note by its vault-relative path; refuse paths that escape the vault
    target = (VAULT / path).resolve()
    if VAULT.resolve() not in target.parents:
        return "refused: path is outside the vault"
    if not target.is_file():
        return "no such note"
    return target.read_text(encoding="utf-8")

def append_daily_note(text: str, confirm: bool = False):
    # Append to today's daily note. Nothing is written unless confirm is True.
    if not confirm:
        return "not written: call again with confirm=true to append"
    today = datetime.date.today().isoformat()
    note = VAULT / "daily" / f"{today}.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    with note.open("a", encoding="utf-8") as f:
        f.write(f"\n- {text}\n")
    return f"appended to daily/{today}.md"

TOOLS = {
  "search_notes": {"fn": search_notes,
    "schema": {"name": "search_notes",
               "description": "Find vault notes whose text contains a phrase.",
               "parameters": {"query": "string"}}},
  "read_note": {"fn": read_note,
    "schema": {"name": "read_note",
               "description": "Read one note by its path inside the vault.",
               "parameters": {"path": "string"}}},
  "append_daily_note": {"fn": append_daily_note,
    "schema": {"name": "append_daily_note",
               "description": "Append a line to today's daily note. Writes only when confirm is true.",
               "parameters": {"text": "string", "confirm": "boolean"}}},
}

@app.get("/tools/list")
def tools_list():
    return jsonify([t["schema"] for t in TOOLS.values()])

@app.post("/tools/call")
def tools_call():
    try:
        body = request.get_json()
        name, args = body["name"], body.get("arguments", {})
        if name not in TOOLS:
            return jsonify({"error": "unknown tool"}), 404
        return jsonify({"result": TOOLS[name]["fn"](**args)})
    except Exception as e:
        print(f"[vaultserver:tools_call] {e}")
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8766, threaded=True)
```

The client is the Part II client with `SERVER` set to `http://localhost:8766`.  Keep Steps 1 and 2 as they are and replace Step 3 with these four calls, then run it on your machine and keep the transcript:

```python
print(call_remote("search_notes", {"query": "chroma"}))
print(call_remote("read_note", {"path": "../../.ssh/id_rsa"}))
print(call_remote("append_daily_note", {"text": "Tried the vault server in class."}))
print(call_remote("append_daily_note", {"text": "Tried the vault server in class.", "confirm": True}))
```

---

## Model 3: A Gated Write

### Critical Thinking Questions

7.  Predict the first line the client prints, then run it.  At that moment, what does the client know about your vault, and what does it still not know (how many notes, what they say, whether a write will succeed)?  Nothing in the client mentions Obsidian; where did the word "note" enter the program?

   > *Hint: The client learns names, descriptions, and parameter types from `/tools/list`, and nothing else.  Compare with the file-injection approach in the Obsidian Sync tutorial, where the agent starts with the notes already in its prompt.  Which approach tells the model more at startup, and which lets it fetch on demand?*

8.  The third call returns "not written" and the fourth writes.  Who decides that `confirm` is true: the model, the client code, or a person?  Describe where a human gate would sit in the agent loop from the *Tool Use and Function Calling* activity, and explain what the flag inside the tool protects against that the schema description ("Writes only when confirm is true") cannot.

   > *Hint: A description is advice to the model; the flag is a check the server enforces.  A model that ignores the advice, or a prompt injection that tells it to "always confirm", meets the check anyway.  What does a real client do with a write-capable tool before calling it?  Now ask the same question of `read_note`: why does it refuse `../../.ssh/id_rsa`, and who wrote that refusal?*

9.  Your vault is also synced to GitHub by the Obsidian Git plugin, which commits and pushes on a timer.  The timer fires while `append_daily_note` is writing.  Walk through what git sees.  Why does the append-only design of this tool usually survive that race, and what would happen instead if the tool rewrote the whole daily note with a fresh summary?

   > *Hint: The plugin commits the file as it existed when the timer fired; the append adds lines below that.  A rewrite changes lines the plugin already committed, so the two versions disagree about the same lines and git reports a conflict.  The Obsidian Sync tutorial's write path gives the conflict-resolution steps; which of them does the append-only rule make unnecessary?*

Which statement about `vault_server.py` is true?

[( )] It is a compliant MCP server because it exposes `/tools/list` and `/tools/call`
[(X)] It follows the MCP pattern (list, then call by name) but does not speak the MCP protocol, which is JSON-RPC over stdio or HTTP
[( )] It is safe to expose on the public internet because `read_note` refuses paths outside the vault
[( )] The `confirm` flag guarantees that a model can never write to the vault without a human's approval

Remember two things from this Part.  Discovery gives the client names and descriptions, never the data behind them, so a vault stays private until a tool is called.  A tool with side effects needs a gate the server enforces, because a description is only advice.

---

# Part IIc: The Server as a Trust Boundary (self-paced)

## 2c.  What the Model Never Has to See

Nothing in the seventy-five minute plan assumes this Part, and nothing graded today depends on it.  It is here because the final project and the Local Agent lab both put a credentialed service behind a tool server, and the design decisions below decide whether that server protects your data or merely relays it.

Model 3 showed two safeguards without naming the pattern they belong to.  `read_note` refused a path outside the vault, and `append_daily_note` refused to write without `confirm`.  Both checks ran in the server, on the real arguments, after the model had already decided what to do.  A prompt injection can change what the model decides; it cannot change what the server enforces.  That is the first of three things a tool server can do that a prompt cannot, and together they make the server a **trust boundary**: the line on the diagram where the model's influence ends and deterministic code takes over.

1.  **The server holds the secret.**  An API key, an OAuth token, or a database password lives in the server's environment and is attached to the outgoing request there.  The model sees a tool name, a schema, and a result.  It never sees the token, so no injection, no verbose error message, and no "print your system prompt" has anything to extract.  The Local Agent lab's Direction 4 calls this injecting the token at the tool-call layer; the server is that layer.
2.  **The server decides, and it decides the same way every time.**  Path checks, allowlists, confirmation flags, rate limits, and scope checks are ordinary code.  Given the same arguments they give the same answer, which is what a guardrail should mean.  A rule in a system prompt is advice the model usually follows; a check in the server is a fact about what can happen.
3.  **The server minimizes and sanitizes what comes back.**  Everything a tool returns lands in the context window, where the model can be talked into repeating it, summarizing it into a file, or sending it somewhere else.  The return path is where you return only the fields the task needs and redact the rest.  `search_notes` currently returns paths; a version that returned full note bodies would hand the model the whole vault one query at a time.

Here is the shape as a picture.  Read it left to right for a request and right to left for a result.

```text
person ──prompt──> model ──tool call: name + args──> client ──> tool server ──HTTPS + token──> service
                     ^                                             │
                     │                                             │ 1. holds the secret (environment, not prompt)
                     │                                             │ 2. checks the arguments (paths, scopes, confirm)
                     │                                             │ 3. calls the service
                     │                                             │ 4. filters fields, redacts, truncates
                     └────────── sanitized result ─────────────────┘ 5. writes one audit line
```

Everything to the left of the tool server is text the model can be argued with about.  Everything inside the box is code you wrote and can test.

---

## Code Cell

> **Runs on your machine, not here.**  This cell extends `vault_server.py` and reads an environment variable on your disk.  Copy it into your course container and run it there.  Set `GITHUB_TOKEN` in the shell that starts the server, never in the file.

The three additions below implement the three safeguards.  `redact` is the return-path sanitizer: a small set of patterns for things that should never travel back to the model, applied to every string a tool returns.  `search_notes` now returns a short snippet around the match instead of the path alone, which is more useful, and instead of the note body, which would be more than the task needs.  `github_issue` is a tool over a real credentialed service: the token comes from the server's environment, the request is made server-side, and the model receives four fields rather than the API's full response.

```python
# vault_server.py additions: paste above the TOOLS dictionary, then extend TOOLS as shown.
import os
import re
import traceback
import requests as req   # a different alias, so it does not shadow Flask's `request`

# --- Safeguard 3: the return-path sanitizer --------------------------------
# Patterns for things that should never travel back into the context window.
# Extend this list for your own domain (student IDs, room numbers, whatever you hold).
REDACT = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[email]"),
    (re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"), "[phone]"),
    (re.compile(r"\b(ghp|gho|ghs|github_pat)_[A-Za-z0-9_]{20,}\b"), "[github-token]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "[api-key]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[aws-key]"),
]

def redact(text: str) -> str:
    for pattern, label in REDACT:
        text = pattern.sub(label, text)
    return text

# --- Safeguard 3 again: minimize. Snippets, not bodies. ---------------------
def search_notes(query: str, width: int = 80):
    # Returns the path and one short snippet per hit. The note body stays in the vault.
    hits = []
    q = query.lower()
    for md_file in sorted(VAULT.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        i = text.lower().find(q)
        if i >= 0:
            start, end = max(0, i - width // 2), min(len(text), i + width // 2)
            hits.append({"path": str(md_file.relative_to(VAULT)),
                         "snippet": redact(text[start:end].replace("\n", " "))})
    return hits[:20]   # a cap is also a safeguard: no single call can dump the vault

# --- Safeguards 1 and 2: the secret stays here, and the checks run here. ----
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")          # read once, at startup, from the server's shell
ALLOWED_REPOS = {"BillJr99/Ursinus-CS357-Fall2026"}    # an allowlist the model cannot edit

def github_issue(repo: str, number: int):
    # Fetch one issue. The model supplies repo and number; the server supplies everything else.
    if repo not in ALLOWED_REPOS:
        return "refused: repository is not on the allowlist"
    if not GITHUB_TOKEN:
        return "refused: server has no GITHUB_TOKEN configured"
    try:
        r = req.get(f"https://api.github.com/repos/{repo}/issues/{int(number)}",
                    headers={"Authorization": f"Bearer {GITHUB_TOKEN}",
                             "Accept": "application/vnd.github+json"},
                    timeout=10)
        if r.status_code != 200:
            return f"github returned {r.status_code}"     # the body may echo headers; do not forward it
        issue = r.json()
        return {"title": redact(issue.get("title", "")),
                "state": issue.get("state"),
                "labels": [l["name"] for l in issue.get("labels", [])],
                "body": redact((issue.get("body") or "")[:1500])}
    except Exception as e:
        print(f"[vault_server:github_issue] {e}")
        traceback.print_exc()
        return "github unavailable"                       # the exception text stays in the server log

# Extend TOOLS: replace the search_notes entry's description, and add github_issue.
TOOLS["search_notes"]["schema"]["description"] = "Find vault notes containing a phrase; returns paths and short snippets."
TOOLS["github_issue"] = {"fn": github_issue,
    "schema": {"name": "github_issue",
               "description": "Read the title, state, labels, and body of one GitHub issue in an allowed repository.",
               "parameters": {"repo": "string", "number": "integer"}}}
```

Trace the token through that cell and notice where it is not.  It is read once from `os.environ` when the server starts, it appears in one `headers` dictionary inside `github_issue`, and it appears nowhere in anything the function returns, prints to the model, or advertises through `/tools/list`.  Now trace a failure: when the request fails, the server returns a status code, and when the code raises, the server returns a fixed string and keeps the exception text for its own log, because a stack trace can carry a URL, a header, or a fragment of the response, and every string the tool returns is a string the model will read.

Restart the server and run these four calls from the Part II client with `SERVER` set to port `8766`:

```python
print(call_remote("search_notes", {"query": "office hours"}))
print(call_remote("github_issue", {"repo": "BillJr99/Ursinus-CS357-Fall2026", "number": 1}))
print(call_remote("github_issue", {"repo": "someone-else/private-repo", "number": 1}))
print(requests.get(f"{SERVER}/tools/list").json()[-1])   # what the model is told about github_issue
```

The second call succeeds only if `GITHUB_TOKEN` was set in the server's shell; the third is refused by the allowlist before any network request is made; the fourth shows that discovery describes the tool and says nothing about how it authenticates.

---

## The Same Pattern in Servers You Did Not Write

Most of the MCP servers your agent will use were written by someone else, and the safeguards above are the questions to ask of each one.  Where does the secret live?  What does the server refuse on its own?  What does a tool return, and how much of it did you need?  The configurations below are for four widely used servers.  The shapes are the ones the two agents read: Claude Code takes a `.mcp.json` file at the project root, and opencode takes an `mcp` block in `opencode.json`.  Both let a configuration file name an environment variable instead of containing a value, so the file can be committed and the secret cannot.

**GitHub, hosted.**  GitHub runs the server; you connect over HTTPS with either an OAuth sign-in or a personal access token.  The token goes in a header that the client attaches; the model never sees the header.  Prefer OAuth where the client supports it (in Claude Code, add the server without a header and run `/mcp` to sign in), and when you must use a token, make it fine-grained, scope it to one repository, and give it read-only permissions unless a tool needs more.

```json
// .mcp.json (Claude Code): the value comes from the GITHUB_PAT variable in your shell
{ "mcpServers": { "github": {
    "type": "http",
    "url": "https://api.githubcopilot.com/mcp/",
    "headers": { "Authorization": "Bearer ${GITHUB_PAT}" } } } }
```

```json
// opencode.json (opencode): same server, same variable, opencode's substitution syntax
{ "mcp": { "github": {
    "type": "remote",
    "url": "https://api.githubcopilot.com/mcp/",
    "enabled": true,
    "headers": { "Authorization": "Bearer {env:GITHUB_PAT}" } } } }
```

**GitHub, local, read-only.**  The same server runs in a container on your machine.  Two flags make it a smaller target: `GITHUB_TOOLSETS` limits which groups of tools it advertises, so the model is never offered a write it should not have, and `GITHUB_READ_ONLY` removes every mutating tool.  The token reaches the container as an environment variable and no further.

```json
// .mcp.json (Claude Code)
{ "mcpServers": { "github": {
    "command": "docker",
    "args": ["run", "-i", "--rm",
             "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "-e", "GITHUB_TOOLSETS", "-e", "GITHUB_READ_ONLY",
             "ghcr.io/github/github-mcp-server"],
    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}",
             "GITHUB_TOOLSETS": "repos,issues,pull_requests",
             "GITHUB_READ_ONLY": "1" } } } }
```

```json
// opencode.json (opencode)
{ "mcp": { "github": {
    "type": "local",
    "command": ["docker", "run", "-i", "--rm",
                "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "-e", "GITHUB_TOOLSETS", "-e", "GITHUB_READ_ONLY",
                "ghcr.io/github/github-mcp-server"],
    "enabled": true,
    "environment": { "GITHUB_PERSONAL_ACCESS_TOKEN": "{env:GITHUB_PAT}",
                     "GITHUB_TOOLSETS": "repos,issues,pull_requests",
                     "GITHUB_READ_ONLY": "1" } } } }
```

**Filesystem.**  The reference filesystem server takes the directories it may touch as command-line arguments and refuses everything else, which is the `read_note` path check as a whole server.  List the narrowest directories that will do; a vault folder, not your home directory.

```json
// .mcp.json (Claude Code)
{ "mcpServers": { "files": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem",
             "${HOME}/Documents/Obsidian/MyVault"] } } }
```

```json
// opencode.json (opencode)
{ "mcp": { "files": {
    "type": "local",
    "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem",
                "{env:HOME}/Documents/Obsidian/MyVault"],
    "enabled": true } } }
```

**Notion, hosted with OAuth.**  Several vendors now host their own MCP servers behind OAuth, and this is the configuration with the least to protect: no token in any file, a sign-in the vendor controls, and a scope the vendor's consent screen shows you.  Claude Code opens the sign-in when you run `/mcp`; opencode is configured the same way with `"type": "remote"` and no `headers`.

```json
// .mcp.json (Claude Code): nothing secret in the file
{ "mcpServers": { "notion": { "type": "http", "url": "https://mcp.notion.com/mcp" } } }
```

Two habits carry across all four.  A configuration file names a variable and never contains a value, so `git diff` can never leak a token.  And a server you did not write still exposes only what you allow it to: toolsets, read-only flags, and directory arguments are the allowlists of Safeguard 2, set in the configuration instead of in code.

---

## Three Scenarios, One Architecture

The pattern is easiest to see in systems where the data is sensitive and the model still has real work to do.  In each row below the model does the reasoning, and the server does the holding, the checking, and the trimming.  The scenarios are the kinds of agent a final-project team might build; the first is one your instructor could use.

| Scenario | What the server holds | What the server checks, deterministically | What the model receives | Where a person sits |
|---|---|---|---|---|
| **Feedback assistant over a course LMS.**  The agent drafts comments on submissions. | The instructor's LMS API token, read from the environment | The assignment ID is on an allowlist for this course; `post_feedback` refuses without `confirm`; at most N posts per hour | A pseudonymous submission ID, the submission text with names and emails redacted, and the rubric.  Never the roster, never a grade history | Reads every draft before `confirm` is sent; the server writes an audit line per post |
| **Issue triage over a repository.**  The agent labels and summarizes new issues. | A fine-grained token scoped to one repository, read-only | The repository is on an allowlist; only the `issues` toolset is exposed; write tools are not advertised at all | Title, labels, state, and a body with emails and pasted credentials redacted (people do paste keys into issues) | Applies labels from the agent's proposal; the agent cannot, because no write tool exists |
| **Analytics over student records.**  The agent answers questions such as "which topics had the lowest quiz averages?" | The database password and a read-only connection | No raw SQL tool exists; each tool is a parameterized query over an allowed column list; any group smaller than a minimum size is suppressed before the result is returned | Aggregates only: means, counts, and distributions per topic.  Never a row, never an identifier | Reviews any query the server logs as suppressed, since a suppressed group is a signal that someone tried to isolate a student |
| **Mail assistant.**  The agent finds threads and drafts replies. | The mailbox OAuth refresh token | Recipients on any draft must be inside the organization's domain; there is no `send` tool, only `create_draft` | Sender domain, subject, date, and a redacted excerpt per thread, not the full message | Opens the draft in the mail client and sends it, or does not |

Here is the first scenario as a workflow, so the order of operations is explicit.  The order is the point: the model never gets a turn between the service and the sanitizer.

1.  The instructor asks the agent to draft feedback for one assignment.
2.  The model calls `list_submissions(assignment_id)`.  The server checks the ID against its allowlist, calls the LMS with its own token, replaces each student identity with a pseudonym it stores in a table the model cannot read, redacts names and emails inside the submission text, and returns the trimmed list.
3.  The model drafts feedback for each pseudonym and calls `post_feedback(submission_id, text)` without `confirm`.  The server returns "not posted" and stores the draft.
4.  The instructor reads the drafts in the server's review page.  The server, not the model, maps pseudonyms back to students for that page.
5.  The instructor approves; the server posts each approved draft with `confirm=true` and writes one audit line per post naming the time, the pseudonym, and the hash of the text.

Student records are covered by FERPA in the United States, and the design above is how an agent can help with them without any student's identity entering a model's context at all.  If your final project touches data of that kind, this is the section to reread.

### Critical Thinking Questions

10.  Suppose the model in the feedback assistant is completely compromised: a submission contains an injection and the model now does whatever the injection says.  List what it can leak and what it cannot, given the design in the workflow above.  Then remove one safeguard at a time (the pseudonyms, the redaction, the `confirm` flag, the allowlist) and say what becomes reachable.

   > *Hint: The model can leak only what is in its context: pseudonyms, redacted text, and its own drafts.  It cannot post, because `confirm` comes from the review page, and it cannot name a student, because the mapping table is on the other side of the boundary.  Which safeguard, removed, exposes identities?  Which exposes the token?  Which makes an unwanted post possible?*

11.  Classify each of the following as a deterministic check or as a model rule, and for each model rule say where it would move to become deterministic: a system prompt line "never reveal email addresses"; the `redact` function; a tool description that says "read-only"; `GITHUB_READ_ONLY=1`; a `confirm` flag; a schema whose `repo` parameter is described as "must be a course repository."

   > *Hint: A description is advice about how to call a tool.  A flag, a function, and an allowlist decide what a call does.  Every model rule in the list has a server-side counterpart already in this Part; name it.*

12.  `redact` will miss things.  Name two kinds of sensitive content in a submission that none of its five patterns would catch, and then explain why a server-side sanitizer that misses some cases is still a better place for the safeguard than a prompt that asks the model not to repeat sensitive content.

   > *Hint: A student's name in running text, or a diagnosis in a sentence, matches no pattern.  The argument for the server is not that it is perfect; it is that it is testable, it is the same every time, and adding a pattern fixes every future call.  What does adding a sentence to a prompt fix?*

Which statement about the trust boundary is true?

[( )] Once the token is in an environment variable, the model can read it with a tool call and use it directly
[( )] The `redact` function protects the token, because the token would otherwise appear in the tool's result
[(X)] The model can only leak what a tool returned to it, so what the server returns is a security decision, not a formatting one
[( )] A tool described as "read-only" in its schema cannot be used to write, because the model follows the description

Remember two things from this Part.  A tool server is where a secret can live without ever entering a context window, and it is where a check can run the same way every time.  And the return path is a boundary too: what a tool returns is what a compromised model can leak, so return the least that does the job.

---

# Part III: Synthesis and Practice

## 3.  Exercises

In this Part you extend the server with a new tool to confirm that discovery is automatic, connect the server to a real-world API, and write the trust checklist your final project will use before connecting any third-party MCP server.

1.  **Extend the server with a new tool.**

   *What to do:* Add a third tool, `events(day)`, that returns campus events from a small hard-coded dictionary (e.g., `{"monday": ["Chess Club 7pm Olin 107"], "tuesday": [...]}`).  Restart the server and demonstrate that the client discovers the new tool automatically, with no changes to the client code.

   *Starter hint:*
   ```python
   # Add this function above the TOOLS dictionary in server.py
   def events(day: str):
       schedule = {
           "monday": ["Chess Club 7pm Olin 107"],
           "tuesday": ["Hawk Hacks info session 5pm IDDC"],
           "friday": ["Ultimate Frisbee 4pm quad"],
       }
       return schedule.get(day.lower(), [])  # return empty list if day not found

   # Then add this entry to the TOOLS dict:
   "events": {"fn": events,
     "schema": {"name": "events",
                "description": "Campus events for a given day of the week.",
                "parameters": {"day": "string"}}},
   ```

   *You've succeeded when:* Running `curl http://localhost:8765/tools/list` shows three tools including `events`, and calling `call_remote("events", {"day": "monday"})` from the client returns the correct list without editing the client file.

2.  **Wrap a real public API as an MCP tool.**

   *What to do:* Wrap the National Weather Service (NWS) API (`https://api.weather.gov`) as a tool on your server.  Add a `get_weather(lat, lon)` tool whose implementation calls the real NWS API and returns the current forecast text.  Then write a short agent loop that asks "What should I wear today at Ursinus College?" and calls your tool to answer it.

   *Starter hint:*
   ```python
   import requests as req  # use a different alias to avoid conflict with Flask's `request`

   def get_weather(lat: str, lon: str):
       # NWS requires two API calls: first get the grid point, then get the forecast
       try:
           points = req.get(f"https://api.weather.gov/points/{lat},{lon}", timeout=10).json()
           forecast_url = points["properties"]["forecast"]
           forecast = req.get(forecast_url, timeout=10).json()
           # Return the first period's short forecast
           return forecast["properties"]["periods"][0]["shortForecast"]
       except Exception as e:
           return f"Weather unavailable: {e}"
   # Ursinus College: lat=40.1914, lon=-75.4532
   ```

   *You've succeeded when:* Your agent produces a sentence like "You should wear a jacket; the forecast is partly cloudy with a high of 58°F" and that answer is demonstrably sourced from the live NWS API, not the model's training data.

3.  **Write a Trust Memo for your final project.**

   *What to do:* In half a page, propose the checklist your final-project team will apply before connecting any third-party MCP server.  Address: who wrote it, what permissions it requests, whether it is read-only or write-capable, and how you would audit its behavior.  Test the checklist on `vault_server.py`: it is write-capable, so say what your team would require before letting an agent call `append_daily_note`.

   *Starter hint:* Your memo should have sections for (a) Source Verification, how do you confirm who wrote the server and whether it has been reviewed?, (b) Permission Scope, what is the minimum set of capabilities the server needs?, (c) Audit Logging, how will you record every call made through the server so you can reconstruct what happened?, and (d) Return Path, what does each tool return, is that more than the task needs, and where does the server hold its credential?

   *You've succeeded when:* Your memo gives a concrete yes/no checklist (not vague guidelines) that a teammate could apply in five minutes to a new MCP server they have never seen before.

---

## Reflection Prompt

In your notebook, respond to all three levels:

**Personal:** Think of a time you used a standard that made your life easier: perhaps a charging cable that worked on multiple devices, or a file format that opened in different programs.  How did having that standard change what you did or built?  Would you have worked differently without it?

**Technical:** Protocols like HTTP made the web explode by letting strangers' systems interoperate.  As agents gain a universal tool protocol in MCP, what is one technically specific consequence you predict in five years?  Consider: what new kinds of services will appear that could not exist before MCP?  What new security risks emerge?

**Societal:** Interoperability standards create network effects: the more people adopt them, the more valuable they become for everyone.  But they also concentrate power: whoever controls the standard has power over everyone who depends on it.  Who currently controls MCP, and what governance structures would you want to see to prevent that control from being abused?

---

-> **Coming Up Next:** Your agent can now reach tools, and it can reach your notes one at a time by search and path.  Next it needs to reach *documents* at scale.  In *RAG Knowledge Base: Code and No-Code Routes* we put the semantic search you built by hand in [Tokens, Embeddings, and Attention](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/TokensEmbeddingsAttention) to work over a whole corpus, so the model answers from your notes instead of from memory.  The vault server you built today is the starting point for the Obsidian vault option in the [Tools and MCP lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/ToolsMCP).

---

## Further Reading

- Model Context Protocol specification and documentation: https://modelcontextprotocol.io
- Hugging Face MCP Course (built with Anthropic), whose early units build and connect a compliant MCP server over JSON-RPC: https://huggingface.co/learn/mcp-course/
- Roy Fielding's REST dissertation, Chapter 5 (online), for the architectural style behind web APIs.
- Anthropic.  "Introducing the Model Context Protocol" (2024, online).
