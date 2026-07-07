<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-mcp.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-mcp.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Connecting Agents to the World: MCP and APIs

Yesterday each team hand-wired tools into one agent; that approach does not scale to the world. Today we study how tools become **shared infrastructure**: web **APIs** as the world's function registry, and the **Model Context Protocol (MCP)** as a standard way for any agent to discover and call any tool server. We move from **the services you already use $\rightarrow$ APIs $\rightarrow$ the N-by-M problem $\rightarrow$ MCP architecture $\rightarrow$ building a tiny tool server $\rightarrow$ a no-code alternative**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **API (Application Programming Interface)** | A published contract that lets one program call functions in another program over the network, without knowing how the other program works internally. | Calling `GET /weather?city=Philadelphia` to get current weather data from a weather service. |
| **REST API** | A style of web API where you send requests to URLs (called endpoints) and receive data back as JSON text. REST stands for Representational State Transfer. | `GET https://api.weather.gov/points/40.19,-75.46` returns campus weather as JSON. |
| **MCP (Model Context Protocol)** | A standard protocol that allows any AI agent to discover and call tools from any compliant tool server, without custom integration code for each pair. Think of it as USB for AI tools. | Your agent calls `GET /tools/list` to discover what a server can do, then calls `POST /tools/call` to use a tool. |
| **N-by-M Problem** | If you have N agent applications and M services, bespoke (custom, one-off) integration requires up to N × M separate adapters. MCP reduces this to N + M by providing one standard both sides follow. | 4 agents × 6 services = 24 adapters without MCP; 4 + 6 = 10 with MCP. |
| **Tool Discovery** | The ability of an agent to ask a server at runtime "what can you do?" rather than having the tool list hard-coded in the agent's source code. | `requests.get("http://localhost:8765/tools/list")` returns the current tool menu dynamically. |
| **JSON-RPC** | A protocol for making remote function calls by sending JSON messages. MCP's full specification is built on top of JSON-RPC. | `{"method": "tools/call", "params": {"name": "hours", "arguments": {"facility": "library"}}}` |
| **OAuth 2.0** | An authorization standard that lets a user grant an app limited, revocable access to their account on another service without sharing their password; the app receives a scoped token instead. | Clicking "Allow this app to read my Google Calendar" issues a token, not your password. |
| **No-code automation / connector** | A platform that builds service-to-service workflows by configuring pre-built "connectors" — each wrapping a service's OAuth/REST API — instead of writing integration code. | Power Automate, Zapier, Make, and IFTTT expose Google, Asana, and hundreds of services as ready-made connectors. |

---

# Part I: The Integration Problem

## Warm-Up: The Services You Already Use

Before we study the integration problem in the abstract, make it personal. As a team, brainstorm the online services and apps each of you relies on in a typical week — email and calendars, task and project managers, banking and budgeting, cloud storage, music, campus systems.

For every service someone names, ask the question this entire unit turns on: **could an agent reach it, and how?** Investigate whether each service exposes:

- an **MCP server** — an agent can discover and call its tools directly through the protocol we study today;
- an **OAuth 2.0 / REST API** — an agent can call it over HTTP with the user's delegated, revocable permission; or
- **neither** — no public programmatic access, so a human (or brittle screen-scraping) is the only way in.

Look each service up rather than guessing — the answer keeps changing as vendors ship new APIs and MCP servers. A few examples to prime the conversation:

| Service | What people use it for | Programmatic access to investigate |
|---|---|---|
| **Google** (Gmail, Calendar, Drive) | Email, scheduling, documents, storage | Mature OAuth 2.0 REST APIs per product; a fast-growing set of MCP servers wraps them |
| **Asana** | Team task and project tracking | Documented OAuth 2.0 REST API for tasks and projects; MCP servers are available |
| **Personal Capital / Empower** | Personal budgeting and net-worth tracking | No official public API — a good example of a service that is *not* openly agent-reachable, where access means unofficial scraping or a third-party data aggregator |

[[___ List 3-5 services your team uses. For each, mark MCP? / OAuth-REST? / neither, and note how you found out. ___]]

> **Talking point:** A pattern is already forming. Google and Asana give an agent a *standard front door* (OAuth/REST, increasingly MCP); Personal Capital gives it *no* front door at all. That split — a few services are agent-reachable, many are walled off, and each open one still has its own auth quirks — is exactly the fragmentation the rest of this activity is about. Keep your team's list handy; you will recognize the N-by-M problem in it on the next slide.

---

## 1. APIs, Then the N-by-M Problem

In this Part you will see why connecting agents to many services becomes expensive without a shared standard, then work through the arithmetic of how MCP (Model Context Protocol — a standard that lets any agent discover and call any compliant tool server) reduces that cost from multiplicative to additive.

**Why this matters:** Think about phone chargers before USB-C existed. Every phone maker had a different cable, so you needed a different charger for every device you owned. USB-C created a universal standard: one cable works with any compliant device. MCP does the same thing for AI tools. Before MCP, every agent team wrote custom glue code to connect to every service. With MCP, you write a service once as a compliant MCP server, and any MCP client — any agent application anywhere — can use it. Integration cost drops from multiplicative to additive.

**An API is a published contract for calling someone else's functions over the network.** REST APIs expose endpoints (`GET /weather?city=...`) returning JSON; your agent's tools so far were local Python, but nothing stops a tool's body from being an HTTP request. Suddenly the agent can reach weather, library catalogs, campus systems, anything with an API.

**The problem is multiplication.** With $N$ agent applications and $M$ services, bespoke integration requires up to $N \times M$ adapters, each with its own schema conventions and auth quirks. The history of computing solves such problems with *protocols*: USB for peripherals, HTTP for documents, LSP for editors and languages.

**MCP is that protocol for tools.** A service wraps itself once as an **MCP server** exposing `tools/list` (machine-readable schemas, like yesterday's, discovered at runtime) and `tools/call`. Any **MCP client** (a chat app, an IDE, your Python agent) connects, lists, and calls. Integration cost drops from $N \times M$ to $N + M$. The agent loop is unchanged; what changes is that tools arrive by discovery rather than by hard-coding.

---

## Model 1: Count the Adapters

A campus has 4 agent applications (advising bot, library bot, IT helpdesk bot, research assistant) and 6 services (catalog, calendar, LMS, ticketing, weather, room booking).

### Critical Thinking Questions

1. Compute the worst-case adapter count without a protocol, and the count with MCP. Show the arithmetic.

   > *Hint: Multiply for bespoke; add for MCP. Then ask: what happens if the campus adds a 5th service?*

2. The library upgrades its catalog API. In each world (bespoke vs. MCP), who must change code, and how many codebases are touched?

   > *Hint: In the bespoke world, draw arrows from "catalog" to every agent that uses it. Each arrow is a codebase change.*

3. Yesterday you wrote tool schemas by hand. Which MCP method replaces that step, and what new *trust* question does runtime discovery create? (Hold this thought for the governance unit.)

   > *Hint: If you receive a tool schema from a stranger's server, what are you agreeing to when you call it?*

---

# Part II: A Tiny Tool Server

## 2. Speaking the Pattern in Code

**Why this matters:** Understanding the theory of MCP is helpful, but building a minimal version yourself makes the architecture concrete and memorable. The server below is not production MCP — it is a teaching implementation of the same two-endpoint pattern: list your tools, then call a tool by name. Real MCP adds session management, capability negotiation, and streaming, but the core idea is identical.

In this Part you will write a small Flask web server (Flask is a Python library for creating web endpoints — URLs your code can respond to over HTTP) that exposes two routes: `/tools/list` to return the server's tool descriptions, and `/tools/call` to execute a named tool by name. You will then run a client that discovers and calls those tools without any hard-coded knowledge of what tools exist.

Full MCP runs over JSON-RPC (a protocol for making remote function calls by sending JSON messages) with sessions and capability negotiation; the essence, a discoverable registry plus a call dispatcher, fits in a screen of Flask. We build the essence.

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
    # Returns only the schemas (not the functions) — clients learn what exists here
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

The client code below runs three steps in order: (1) ask the server what tools exist, (2) define a reusable function for calling any of them by name, and (3) demonstrate both tools. Notice that the client never imports or defines `room_lookup` or `hours` — it learns they exist at runtime from the server's response.

## Code Cell

```python
# client side: discover the server's tools, hand them to the model, dispatch calls.
# This is a simplified MCP client: it asks "what can you do?" then does it.
import requests

SERVER = "http://localhost:8765"

# Step 1: Discover what tools exist — no hard-coding required
discovered = requests.get(f"{SERVER}/tools/list", timeout=10).json()
print("discovered tools:", [t["name"] for t in discovered])
# Output: discovered tools: ['room_lookup', 'hours']

# Step 2: Define a reusable call function
def call_remote(name, arguments):
    r = requests.post(f"{SERVER}/tools/call",
                      json={"name": name, "arguments": arguments}, timeout=10)
    return r.json()

# Step 3: Use the tools — the client never needed to know these existed at startup
print(call_remote("hours", {"facility": "library"}))
# Output: {'result': '8am-midnight M-R'}

print(call_remote("room_lookup", {"building": "Pfahler"}))
# Output: {'result': ['007', '012', '108']}
```

---

## Model 2: Discovery in Action

### Critical Thinking Questions

4. Your client knew nothing about rooms or hours at startup, yet ended up calling both. Trace exactly where the knowledge entered the program. How does this differ from yesterday's hard-coded `TOOLS` list?

   > *Hint: At what line of the client code does the client first learn that "room_lookup" exists? Now compare to yesterday's file where tool names appeared directly in the source.*

5. Convert yesterday's agent to use `discovered` schemas (sketch the three changed lines). What stays identical? What does that invariance tell you about good layering?

   > *Hint: The agent loop — perceive, plan, act, observe — does not need to know whether tools came from discovery or hard-coding. What does this tell you about the value of keeping layers separate?*

6. A malicious server could describe a tool as "harmless lookup" while its implementation deletes files. Which side of the protocol can lie, and what defenses (allowlists, sandboxes, human gates, audits) operate at which layer?

   > *Hint: Think of a restaurant analogy: you trust the menu description, but what stops a bad kitchen from putting something harmful in your food? Who provides each kind of protection?*

> **⚠️ Common Misconception:** Many students assume that because MCP standardizes the interface, it also guarantees the safety of the tools behind it. This is not true. MCP standardizes *how* you discover and call tools — it says nothing about *what those tools are allowed to do*. A perfectly spec-compliant MCP server could read your files, make purchases, or send emails on your behalf. Trust must be established by checking who wrote the server, what permissions it requests, and whether it has been audited — not by assuming the protocol protects you.

[[MC]]
The primary value MCP adds over each team writing custom tool integrations is:
- ( ) It makes models more accurate
- (x) It standardizes discovery and invocation so any client can use any compliant tool server
- ( ) It eliminates the need for authentication
- ( ) It runs tools inside the model for speed

---

## No-Code Integration: Microsoft Power Automate

You just built an integration in **code** — a Flask server plus a Python client. Most organizations also connect services a second way: **no-code automation platforms**. Microsoft **Power Automate** is the one you are most likely to meet in a workplace (Zapier, Make, and IFTTT are close cousins). Instead of writing an MCP server, you assemble a **flow** from pre-built **connectors**, each of which already wraps a service's OAuth/REST API. It is the same "reach the world's services" goal as MCP, reached with configuration instead of code.

**The building blocks of a flow:**

- **Trigger** — the event that starts the flow: a schedule, a new email, a new Asana task, a submitted form, or a manual button.
- **Connector actions** — the steps that follow ("Create a Google Calendar event," "Add a task in Asana," "Post to Teams"). Each connector authenticates once with **OAuth 2.0** and the platform stores the token, so the flow itself never contains a password or key.
- **Conditions and loops** — no-code control flow ("if the email has an attachment, then…").
- **HTTP action** *(premium)* — call any REST endpoint the built-in connectors do not cover, including a language-model API or one of your own services.
- **AI Builder / Copilot** — Microsoft's built-in AI steps: prompt a model, summarize, extract fields, or classify, dragged in like any other action.

**How to build one, end to end:**

1. Sign in at **make.powerautomate.com** with a Microsoft account (a school or work account unlocks more connectors).
2. Choose **Create → Automated cloud flow**, name it, and pick a **trigger** (for example "When a new email arrives" in Outlook, or "When a task is created" in the Asana connector).
3. Add a step and search for the **connector** you want (Google, Asana, Teams, SharePoint, …). The first time you use a connector it opens an **OAuth consent screen**; you grant scoped access once and the platform holds the token.
4. Map fields from the trigger into the action with the **dynamic content** picker (for example, put the email's subject into a new task's title).
5. To add AI, insert an **AI Builder** action (prompt a model, extract information) or an **HTTP** action that POSTs to a model's `/v1/chat/completions` endpoint — the same request body you have used all unit.
6. **Test** with the built-in run panel, inspect each step's inputs and outputs, then **turn the flow on** so its trigger runs it automatically.

**Where it fits — and where it does not.** No-code platforms are fastest when a connector already exists for both services and the logic is simple. They struggle when you need custom logic, real version control, or a portable integration you can host yourself — which is exactly when writing an MCP server or a small agent (as you did above) wins. And the trust questions do not disappear: a connector holds a real OAuth token with real scopes, so the same "who wrote it, what can it do, is it least-privilege" checklist from Model 2 still applies.

### Critical Thinking Questions

7. A Power Automate connector and your Flask server both let a system "create a calendar event." Name two things the no-code connector gives you for free that you handled yourself in code, and one thing the code version gives you that the connector cannot.

   > *Hint: For free — the OAuth flow and token storage, plus a maintained schema/UI for the service's fields. In code you keep — custom logic, self-hosting and portability, and version-controlled review of exactly what runs.*

8. In step 5 you can call a model with an HTTP action whose body is a `/v1/chat/completions` payload. Where should the model's API key live so it does not end up pasted into the flow definition that teammates can open and export?

   > *Hint: Store it as a secure input / environment variable / connection secret (or a Key Vault reference) and reference it — never hard-code it into the HTTP action's headers, where it becomes part of the exported flow. Same rule as every other secret this term.*

[[MC]]
Compared with writing an MCP server, a no-code platform like Power Automate primarily trades:
- ( ) accuracy for speed — its flows produce less correct results
- (x) control and portability for speed and pre-built, already-authenticated connectors
- ( ) security for convenience — flows cannot use OAuth
- ( ) nothing; it is strictly better in every way

> **⚠️ Common Misconception:** "No-code means there is no security to think about." Often the opposite: one flow can hold OAuth tokens to your email, files, and calendar at once and run unattended. The connector hides the *plumbing*, not the *risk* — least-privilege scopes, controlling who can edit the flow, and keeping model keys out of the flow body all still matter.

---

# Part III: Synthesis and Practice

## 3. Exercises

In this Part you extend the server with a new tool to confirm that discovery is truly automatic, connect the server to a real-world API, and write the trust checklist your final project will use before connecting any third-party MCP server.

1. **Extend the server with a new tool.**

   *What to do:* Add a third tool, `events(day)`, that returns campus events from a small hard-coded dictionary (e.g., `{"monday": ["Chess Club 7pm Olin 107"], "tuesday": [...]}`). Restart the server and demonstrate that the client discovers the new tool automatically, with no changes to the client code.

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

2. **Wrap a real public API as an MCP tool.**

   *What to do:* Wrap the National Weather Service API (`https://api.weather.gov`) as a tool on your server. Add a `get_weather(lat, lon)` tool whose implementation calls the real NWS API and returns the current forecast text. Then write a short agent loop that asks "What should I wear today at Ursinus College?" and calls your tool to answer it.

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

   *You've succeeded when:* Your agent produces a sentence like "You should wear a jacket — the forecast is partly cloudy with a high of 58°F" and that answer is demonstrably sourced from the live NWS API, not the model's training data.

3. **Write a Trust Memo for your final project.**

   *What to do:* In half a page, propose the checklist your final-project team will apply before connecting any third-party MCP server. Address: who wrote it, what permissions it requests, whether it is read-only or write-capable, and how you would audit its behavior.

   *Starter hint:* Your memo should have sections for (a) Source Verification — how do you confirm who wrote the server and whether it has been reviewed?, (b) Permission Scope — what is the minimum set of capabilities the server needs?, (c) Audit Logging — how will you record every call made through the server so you can reconstruct what happened?

   *You've succeeded when:* Your memo gives a concrete yes/no checklist (not vague guidelines) that a teammate could apply in five minutes to a new MCP server they have never seen before.

---

## Reflection Prompt

In your notebook, respond to all three levels:

**Personal:** Think of a time you used a standard that made your life easier — perhaps a charging cable that worked on multiple devices, or a file format that opened in different programs. How did having that standard change what you did or built? Would you have worked differently without it?

**Technical:** Protocols like HTTP made the web explode by letting strangers' systems interoperate. As agents gain a universal tool protocol in MCP, what is one technically specific consequence you predict in five years? Consider: what new kinds of services will appear that could not exist before MCP? What new security risks emerge?

**Societal:** Interoperability standards create network effects — the more people adopt them, the more valuable they become for everyone. But they also concentrate power: whoever controls the standard has leverage over everyone who depends on it. Who currently controls MCP, and what governance structures would you want to see to prevent that control from being abused?

---

→ **Coming Up Next:** In the next activity, we look at *design-first* practices — how to plan a multi-agent system on paper before writing any code, so that your MCP integrations and agent interactions are deliberate rather than accidental.

---

## Further Reading

- Model Context Protocol specification and documentation: https://modelcontextprotocol.io
- Roy Fielding's REST dissertation, Chapter 5 (online), for the architectural style behind web APIs.
- Anthropic. "Introducing the Model Context Protocol" (2024, online).
