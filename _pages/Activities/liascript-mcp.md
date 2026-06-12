# Connecting Agents to the World: MCP and APIs
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

Yesterday each team hand-wired tools into one agent; that approach does not scale to the world. Today we study how tools become **shared infrastructure**: web **APIs** as the world's function registry, and the **Model Context Protocol (MCP)** as a standard way for any agent to discover and call any tool server. We move from **APIs $\rightarrow$ the N-by-M problem $\rightarrow$ MCP architecture $\rightarrow$ building a tiny tool server**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Integration Problem

## 1. APIs, Then the N-by-M Problem

**An API is a published contract for calling someone else's functions over the network.** REST APIs expose endpoints (`GET /weather?city=...`) returning JSON; your agent's tools so far were local Python, but nothing stops a tool's body from being an HTTP request. Suddenly the agent can reach weather, library catalogs, campus systems, anything with an API.

**The problem is multiplication.** With $N$ agent applications and $M$ services, bespoke integration requires up to $N \times M$ adapters, each with its own schema conventions and auth quirks. The history of computing solves such problems with *protocols*: USB for peripherals, HTTP for documents, LSP for editors and languages.

**MCP is that protocol for tools.** A service wraps itself once as an **MCP server** exposing `tools/list` (machine-readable schemas, like yesterday's, discovered at runtime) and `tools/call`. Any **MCP client** (a chat app, an IDE, your Python agent) connects, lists, and calls. Integration cost drops from $N \times M$ to $N + M$. The agent loop is unchanged; what changes is that tools arrive by discovery rather than by hard-coding.

---

## Model 1: Count the Adapters

A campus has 4 agent applications (advising bot, library bot, IT helpdesk bot, research assistant) and 6 services (catalog, calendar, LMS, ticketing, weather, room booking).

### Critical Thinking Questions

1. Compute the worst-case adapter count without a protocol, and the count with MCP. Show the arithmetic.
2. The library upgrades its catalog API. In each world, who must change code, and how many codebases are touched?
3. Yesterday you wrote tool schemas by hand. Which MCP method replaces that step, and what new *trust* question does runtime discovery create? (Hold this thought for the governance unit.)

---

# Part II: A Tiny Tool Server

## 2. Speaking the Pattern in Code

Full MCP runs over JSON-RPC with sessions and capability negotiation; the essence, a discoverable registry plus a call dispatcher, fits in a screen of Flask. We build the essence.

---

## Code Cell

```python
# server.py: run with `python server.py`, then query it from another terminal.
from flask import Flask, request, jsonify

app = Flask(__name__)

def room_lookup(building: str):
    rooms = {"pfahler": ["007", "012", "108"], "iddc": ["116", "214"]}
    return rooms.get(building.lower(), [])

def hours(facility: str):
    table = {"library": "8am-midnight M-R", "gym": "6am-10pm daily"}
    return table.get(facility.lower(), "unknown facility")

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
        print(f"[mcpserver:tools_call] {e}")
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8765, threaded=True)
```

---

## Code Cell

```python
# client side: discover the server's tools, hand them to the model, dispatch calls.
import requests

SERVER = "http://localhost:8765"

discovered = requests.get(f"{SERVER}/tools/list", timeout=10).json()
print("discovered tools:", [t["name"] for t in discovered])

def call_remote(name, arguments):
    r = requests.post(f"{SERVER}/tools/call",
                      json={"name": name, "arguments": arguments}, timeout=10)
    return r.json()

print(call_remote("hours", {"facility": "library"}))
print(call_remote("room_lookup", {"building": "Pfahler"}))
```

---

## Model 2: Discovery in Action

### Critical Thinking Questions

4. Your client knew nothing about rooms or hours at startup, yet ended up calling both. Trace exactly where the knowledge entered the program. How does this differ from yesterday's hard-coded `TOOLS` list?
5. Convert yesterday's agent to use `discovered` schemas (sketch the three changed lines). What stays identical? What does that invariance tell you about good layering?
6. A malicious server could describe a tool as "harmless lookup" while its implementation deletes files. Which side of the protocol can lie, and what defenses (allowlists, sandboxes, human gates, audits) operate at which layer?

[[MC]]
The primary value MCP adds over each team writing custom tool integrations is:
- ( ) It makes models more accurate
- (x) It standardizes discovery and invocation so any client can use any compliant tool server
- ( ) It eliminates the need for authentication
- ( ) It runs tools inside the model for speed

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Extend the server.* Add a third tool, `events(day)`, returning campus events from a small dictionary, and demonstrate discovery picking it up with no client changes.
2. *Real API.* Wrap a genuinely public API (for example, the National Weather Service at api.weather.gov) as a tool on your server, with the exception-handling pattern from class. Demonstrate an end-to-end agent question that uses it.
3. *Trust memo.* In a half page, propose the checklist your final-project team will apply before connecting any third-party MCP server (who wrote it, what permissions it needs, read-only or write, audit logging). This memo feeds your governance assignment.

---

## Reflection Prompt

In your notebook: protocols like HTTP made the web explode by letting strangers' systems interoperate, with consequences both wonderful and harmful. As agents gain a universal tool protocol, what is one consequence you predict in five years, and is it more wonderful or more harmful?

---

## 4. Further Reading

- Model Context Protocol specification and documentation: https://modelcontextprotocol.io
- Roy Fielding's REST dissertation, Chapter 5 (online), for the architectural style behind web APIs.
- Anthropic. "Introducing the Model Context Protocol" (2024, online).
