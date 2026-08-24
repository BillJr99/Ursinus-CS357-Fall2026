---
layout: default-standard
permalink: /Tutorials/AgenticOpenWebUI
title: 'CS357: Foundations of Artificial Intelligence - Agentic OpenWebUI'
info:
  coursenum: CS357
  purpose: "To use OpenWebUI as an agent frontend rather than a chat window: registering tools, holding uploaded knowledge, and running multi-agent workflows."
tags:
- openwebui
- tools
- local-ai
---
# CS357: Foundations of Artificial Intelligence - Agentic OpenWebUI

## Purpose

To use OpenWebUI as an agent frontend rather than a chat window: registering tools, holding uploaded knowledge, and running multi-agent workflows.

## About This Tutorial

You already run OpenWebUI as a chat window over Ollama.  Here we treat it as something more interesting: an **agent frontend**: a server that registers tools, holds uploaded knowledge, manages models, and exposes an OpenAI-compatible API that *your Python code* can drive.  We move from **OpenWebUI as an agent frontend $\rightarrow$ driving its API from Python (two hands-on notebooks) $\rightarrow$ a goal-directed planner/worker/critic workflow built entirely from successive API calls**.

This is a **supplemental tutorial**: it is not graded and no commercial API keys are required.  It builds directly on the local agent stack you assembled in the [Agent Stack activity]({{ site.baseurl }}/Tutorials/AgentStack) and the [Compose and Verify a Local Agent Stack lab](https://www.billmongan.com/Ursinus-CS357/Assignments/LocalAgent/Direction2).

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|------|--------------------------|--------------------------|
| **Agent Frontend** | A server that sits between users (or programs) and a model backend, adding capabilities the raw model lacks: tool registration, document knowledge, users and permissions, and an API. | OpenWebUI in front of Ollama: the model generates text; OpenWebUI supplies tools, uploads, and access control. |
| **OpenWebUI Tool** | A Python class you register in OpenWebUI's Workspace -> Tools panel. Its method signatures and docstrings become tool schemas the model can call during chat, with OpenWebUI executing the Python server-side. | A `get_current_time()` tool whose docstring ("Returns the current time...") is the only thing the model reads when deciding to call it. |
| **OpenWebUI Function (Pipe/Filter)** | An extension point that modifies the request/response pipeline itself. A *pipe* acts like a custom model in the model list; a *filter* rewrites messages before (inlet) or after (outlet) the model sees them. | A filter that appends "Answer in one paragraph" to every user message; a pipe that routes requests to two models and merges the answers. |
| **Knowledge Collection** | A set of uploaded documents that OpenWebUI chunks, embeds, and retrieves from: RAG managed by the frontend rather than by your code. | Uploading the course syllabus into a "CS357" collection, then referencing it with `#CS357` in chat so answers cite the syllabus. |
| **OpenAI-Compatible API** | OpenWebUI re-exposes its models at `/api/chat/completions` (and files at `/api/v1/files/`) using the same request shape as OpenAI's API, authenticated by a Bearer API key. Any OpenAI client library or plain `requests` code works against it. | `POST http://localhost:3000/api/chat/completions` with `{"model": "llama3.2", "messages": [...]}` and an `Authorization: Bearer sk-...` header. |
| **API Key (Bearer Token)** | A secret string identifying *your account* to the API. Every request your scripts make runs with your permissions and shows up in your account's history. | The notebooks read the key from a variable rather than hard-coding it, so it never lands in a Git repository. |
| **Blackboard** | A shared data structure that multiple agents read from and write to as their only communication channel: a fan-in point for multi-agent state. | The multi-agent notebook's dictionary holding the goal, the plan, completed steps, and critiques. |
| **Planner / Worker / Critic** | A three-role decomposition: one call plans the steps, one call executes each step, one call judges the result and requests revisions. All three can be the *same model* prompted differently. | Three successive `/api/chat/completions` calls with different system prompts, orchestrated by a Python loop. |

---

# Part I: OpenWebUI as an Agent Frontend

In this Part you will inventory the agentic capabilities OpenWebUI layers on top of a bare Ollama server, and reason about which layer (model, frontend, or your own code) is responsible for what.

**Why this matters:** In the agent stack, every capability lives at some tier, and misplacing a capability creates real bugs: a tool registered in OpenWebUI is invisible to a script that calls Ollama directly on port 11434, and a governance rule enforced only in the UI evaporates the moment someone scripts the API. Knowing *where each capability lives* is the difference between an architecture and a pile of containers.

## What the Frontend Adds

A bare Ollama server answers `POST /api/generate` and `POST /api/chat`: text in, text out, plus native function calling if you supply schemas yourself.  OpenWebUI in front of it adds distinct capability layers:

| Layer | What you do | What OpenWebUI does | Where it lives |
|-------|-------------|---------------------|----------------|
| **Chat UI** | Type in a browser at `http://localhost:3000` | Manages conversations, history, model switching | Frontend container |
| **Tool registration** | Paste a Python class into Workspace -> Tools; enable it for a model | Turns docstrings into tool schemas, offers them to the model, executes the Python when the model calls, feeds results back | Frontend container (server-side execution) |
| **Functions (pipes/filters)** | Install or write inlet/outlet code | Rewrites requests and responses in flight; pipes appear as new "models" | Frontend container |
| **Knowledge uploads** | Drag documents into Workspace -> Knowledge | Chunks, embeds, stores, and retrieves per query; injects passages into the prompt | Frontend container + its vector store |
| **Users and keys** | Create accounts and API keys | Authenticates every request; scopes history and permissions per user | Frontend container |
| **OpenAI-compatible API** | Point any script at `/api/chat/completions` with a Bearer key | Routes to Ollama, *applying the tools, knowledge, and filters configured for that model* | Frontend container -> Ollama container |

The last row is the pivot of this tutorial: a script that calls **OpenWebUI's** API gets the whole agentic layer; a script that calls **Ollama** directly on port 11434 gets none of it.

### Questions to Work Through

1.  A teammate registers a `search_catalog` tool in OpenWebUI and enables it for `llama3.2`.  Their Python script then calls `http://localhost:11434/api/chat` and reports "the tool never fires."  Diagnose the bug using the table, and state the one-line fix.

   > *Hint: Port 11434 is Ollama: the backend tier.  The tool lives in the frontend tier at port 3000.  Which URL (and which extra header) makes the script's requests pass through the tier where the tool is registered?*

2.  Tools in OpenWebUI execute *server-side*, inside the frontend container, with whatever filesystem and network access that container has.  Compare this to the tool registry you built in the Tool Use activity, where *your own process* executed the function.  Who controls the security boundary in each case, and which arrangement would you trust with a `read_file` tool?

   > *Hint: In your own agent loop, you wrote the registry and could wrap any call in a confirmation gate.  In OpenWebUI, the execution environment and sandboxing policy belong to the frontend.  Consider: who audits the tool code your teammates install from the community library?*

3.  Knowledge collections give you RAG without writing retrieval code.  Name one thing you *lose* relative to the RAG pipeline you built yourself, and one situation where the frontend-managed version is clearly the right call.

   > *Hint: What you lose is visibility and control: chunk size, embedding model, top-k, and the exact injected passages are the frontend's decisions (though some are configurable in Admin Settings).  When is "good defaults, zero code, shared with every user of the server" worth more than that control?*

A tool registered in OpenWebUI's Workspace -> Tools panel will be available to:

- Any program that queries the Ollama server directly on port 11434
- Chats and API calls that go through OpenWebUI with a model for which the tool is enabled
- Only the browser UI, never API clients
- Every model on the machine, automatically and immediately

<details markdown="1"><summary>Answer</summary>

Chats and API calls that go through OpenWebUI with a model for which the tool is enabled

</details>

---

# Part II: Driving OpenWebUI from Python

In this Part you will move from clicking the UI to scripting it: the same chat, upload, and RAG capabilities, invoked from `requests` calls your code controls, the step that turns a chat website into a programmable agent platform.

**Why this matters:** Everything an agent workflow needs (send a message as a role, attach knowledge, collect the answer, decide what to do next) becomes a function call once you can hit the API. This is exactly how production teams wire frontends into pipelines, schedulers, and other agents.

## 2.  The Minimal Client

Every interaction reduces to one authenticated POST. Run this against your own stack (replace the API key with yours; the default OpenWebUI port from the agent stack lab is 3000):

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import requests

BASE = "http://localhost:3000"      # OpenWebUI, not Ollama's 11434
API_KEY = "sk-REPLACE-ME"           # Settings -> Account -> API Keys

r = requests.post(
    f"{BASE}/api/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": "You answer in exactly two sentences."},
            {"role": "user", "content": "What does an agent frontend add on top of a bare model server?"},
        ],
    },
    timeout=120,
)
print(r.json()["choices"][0]["message"]["content"])
```

Note the shape: it is the OpenAI `/v1/chat/completions` request format you met in the RESTful LLM Access tutorial; OpenWebUI speaks that dialect, so every OpenAI-compatible client works here unchanged.

## The Two Hands-On Notebooks

The hands-on core of this tutorial is two Colab-ready notebooks from the course repository.  Work through them in order; each is fully commented and runs against your local stack (or any OpenAI-compatible endpoint you point it at).

**Notebook 1: [OpenWebUI API Client with Upload](https://www.billmongan.com/Ursinus-CS357/files/notebooks/OpenWebUI_API_Client_With_Upload.ipynb):** the single-agent plumbing.  It builds an OpenAI-compatible client in plain `requests`, configures a system prompt and user query, uploads a document via the `/v1/files` endpoint *with a graceful fallback* (if the server does not accept the upload, the notebook parses the document to text locally and injects it into the prompt as context instead), then invokes `/v1/chat/completions` and saves the response artifacts.  The engineering lesson is the fallback pattern: the notebook degrades from server-side RAG to client-side context injection without changing the rest of the pipeline.

**Notebook 2: [OpenWebUI Multi-Agent Goal Workflow](https://www.billmongan.com/Ursinus-CS357/files/notebooks/OpenWebUI_MultiAgent_Goal_Workflow.ipynb):** the multi-agent orchestration.  It defines agent *roles* as system prompts, a **blackboard** dictionary as shared memory, and an **orchestrator** loop that pursues a goal by making successive chat-completion calls (planning, executing steps, recording results on the blackboard, and critiquing), then exports the full run for inspection.  Every "agent" is the same OpenWebUI endpoint wearing a different system prompt; the intelligence of the *system* lives in the Python routing loop.

### Questions to Work Through

4.  Notebook 1's upload step has a fallback: if `/v1/files` fails, parse the document locally and paste its text into the prompt.  Identify one way the *fallback* behavior can silently differ from the *upload* behavior for a long document, and how you would detect the difference from the response alone.

   > *Hint: Server-side knowledge is chunked and retrieved: only relevant passages reach the prompt.  Client-side injection pastes the document up to whatever fits in context.  For a 100-page document, which approach risks truncation, and which risks retrieving the wrong chunk?  A response that cites material from the document's final pages tells you what about the path taken?*

5.  In Notebook 2, every agent is "the same model with a different system prompt."  What, concretely, makes the Critic's judgment independent enough to be useful, given that it shares every parameter with the Worker it is judging?  What would strengthen that independence?

   > *Hint: The system prompt changes the model's instructions and the blackboard slice it sees; a fresh call has no memory of the Worker's reasoning process, only its output.  Strengthening options: a different model for the Critic, structured rubrics, or evidence requirements.  Recall the LLM-as-judge module's findings on self-evaluation bias.*

6.  The blackboard in Notebook 2 lives in a Python dictionary in the orchestrator, not in OpenWebUI. Why must it live there and not in the chat history of a single OpenWebUI conversation?  What does this tell you about where the "agent system" actually resides?

   > *Hint: Each API call in the workflow is stateless; the orchestrator chooses exactly which blackboard slices to include in each call's messages.  A single shared conversation would show every agent everything (recall the AutoGen group-chat leak from the frameworks activity).  The system's memory and routing live in your code; OpenWebUI supplies completions.*

In the multi-agent notebook, the Planner, Worker, and Critic are implemented as:

- Three different models that must all be pulled in Ollama
- Three OpenWebUI user accounts with separate API keys
- Successive API calls to the same endpoint with different system prompts, coordinated by a Python orchestrator and a shared blackboard
- Three OpenWebUI "Functions" installed from the community library

<details markdown="1"><summary>Answer</summary>

Successive API calls to the same endpoint with different system prompts, coordinated by a Python orchestrator and a shared blackboard

</details>

---

# Part III: A Goal-Directed Multi-Agent Workflow

In this Part you will trace the planner/worker/critic loop as a sequence of API calls, and decide where in that sequence control, memory, and governance live.

## Planner -> Worker -> Critic via Successive API Calls

The workflow pattern from Notebook 2, reduced to its skeleton:

```text
            +---------------------------- orchestrator (your Python) ---------------------------+
            |                                                                                    |
 goal --> [call 1: PLANNER]                [call 2..k: WORKER]                [call k+1: CRITIC] |
            | system: "Decompose the        | system: "Execute exactly        | system: "Judge   |
            | goal into numbered steps"     | one step; use the context       | the results      |
            |                               | provided"                       | against the goal"|
            v                               v                                 v                  |
          plan  ----> blackboard ----> step results ----> blackboard ----> verdict -------------+
                                                                             |
                                             "revise" --> loop back to WORKER with critique
                                             "done"   --> final answer assembled from blackboard
```

A compact implementation.  Three roles, one endpoint, the loop visible:

> **Runs on your machine, not here.**  This cell makes network calls that the page sandbox blocks.  Copy it into your course container and run it there.

```python
import requests

BASE, API_KEY, MODEL = "http://localhost:3000", "sk-REPLACE-ME", "llama3.2"

def ask(system, user):
    """One stateless call: a role is just a system prompt."""
    r = requests.post(f"{BASE}/api/chat/completions",
                      headers={"Authorization": f"Bearer {API_KEY}"},
                      json={"model": MODEL,
                            "messages": [{"role": "system", "content": system},
                                         {"role": "user", "content": user}]},
                      timeout=180)
    return r.json()["choices"][0]["message"]["content"]

goal = "Produce a three-bullet briefing on running local LLMs safely in a classroom."
blackboard = {"goal": goal, "results": [], "critiques": []}

plan = ask("You are a planner. Decompose the goal into 3 numbered steps. Output only the steps.",
           blackboard["goal"])

for step in [s for s in plan.splitlines() if s.strip()][:3]:
    result = ask("You are a worker. Execute exactly the step you are given, in 3-5 sentences. "
                 "Use only the context provided; do not do other steps.",
                 f"Goal: {blackboard['goal']}\nStep: {step}\nPrior results: {blackboard['results']}")
    blackboard["results"].append({"step": step, "result": result})

verdict = ask("You are a critic. Say APPROVE if the results satisfy the goal, "
              "or REVISE followed by specific fixes.",
              f"Goal: {blackboard['goal']}\nResults: {blackboard['results']}")
blackboard["critiques"].append(verdict)
print(verdict)
```

If the verdict begins with `REVISE`, the orchestrator loops the affected steps back through the Worker with the critique appended, bounded by a maximum iteration count, exactly like `max_steps` in your Local Agent Lab agent loop.

### Questions to Work Through

7.  List every decision in Model 3 that is made by *Python code* rather than by a model (there are at least four).  Then answer: if the workflow misbehaves, why is this list the first place to look?

   > *Hint: Which text becomes each call's context; how the plan is split into steps; how many steps run; when the loop terminates; what "begins with REVISE" means.  These are deterministic and inspectable, unlike the model's generations.  Recall the debugging module: check the deterministic scaffolding before blaming the stochastic component.*

8.  The Worker's system prompt says "Execute exactly the step you are given; do not do other steps."  Connect this instruction to the small-context-window principle from *Memory and the Small Context Window Principle*: what failure appears if the Worker is instead handed the whole plan and told to "make progress"?

   > *Hint: With the whole plan in context, the model tends to do a shallow pass over everything, the same dilution as one-big-prompt research.  One step per call keeps each generation focused and makes the blackboard entries attributable to a step.*

9.  Where would you add a human-approval gate in Model 3 if one Worker step could trigger an irreversible action (say, posting to a course forum via an OpenWebUI tool)?  Identify the exact line and defend it against putting the rule in the Worker's system prompt instead.

   > *Hint: The gate belongs in the orchestrator, around the `ask(...)` call (or around the tool-enabled step), where Python can block until a human confirms.  A prompt instruction is a request to a stochastic system; a code gate is enforcement.  This is the same argument as the tool-registry boundary in the Tool Use activity.*

> **Common Misconception:** Students often expect OpenWebUI to "run the multi-agent workflow" once the roles are defined.  OpenWebUI executes *one completion per request*; it has no idea your Planner and Critic are related calls.  The workflow (sequencing, memory, revision loops, stopping) exists only in your orchestrator code.  The frontend supplies completions, tools, and knowledge; *you* supply the agency.

---

## Exercises

1.  *Key in hand.*  Generate an OpenWebUI API key, run the minimal client from Part II against your stack, and then break it three ways: wrong port (11434), missing Bearer header, and a model name you have not pulled.  Record the three error responses.

   - *What to do:* Make each mistake deliberately and capture status codes and bodies.  Build yourself a one-paragraph troubleshooting table.
   - *You've succeeded when:* You can identify from an error response alone which of the three mistakes a classmate made.

2.  *Notebook run-through.*  Complete [OpenWebUI_API_Client_With_Upload.ipynb](https://www.billmongan.com/Ursinus-CS357/files/notebooks/OpenWebUI_API_Client_With_Upload.ipynb) with a document of your own (a course reading, a README).  Force the fallback path by pointing the upload at a bad endpoint, and compare the two answers you get for the same question about the document.

   - *You've succeeded when:* You can state one concrete difference between the server-RAG answer and the context-injection answer, and explain it using CTQ 4.

3.  *Tool + workflow integration.*  Register a simple tool in OpenWebUI (e.g., a `get_current_time` or a word-count tool from the Tool Use activity), enable it for your model, then extend the Part III skeleton (or [OpenWebUI_MultiAgent_Goal_Workflow.ipynb](https://www.billmongan.com/Ursinus-CS357/files/notebooks/OpenWebUI_MultiAgent_Goal_Workflow.ipynb)) with a goal that requires the tool.

   - *Starter hint:* In OpenWebUI, a tool is a Python class whose typed methods and docstrings become the schema.  Whether tools fire on API calls depends on the model's tool support and the server's function-calling settings; observing *whether and when* the tool fires is the point of the exercise.
   - *You've succeeded when:* You can show one workflow run where the tool executed (visible in the response or server logs) and state which tier executed it.

4.  *Critic ablation.*  Run the Part III workflow five times with the Critic enabled, then five times with the verdict hard-coded to APPROVE. Score the ten briefings (rubric of your design) without knowing which condition produced each.

   - *You've succeeded when:* You can report whether the Critic measurably improved the output on your rubric, and connect the result to the critique-refine module.

---

## Reflection Prompt

*Personal:* This tutorial moved you from *using* a chat interface to *programming* it.  Recall another tool you first used through its interface and later automated (a spreadsheet, a photo editor, a grade tracker).  What did automation reveal about the tool that the interface hid?  What did the interface protect you from that your scripts no longer do?

*Technical:* The same capability (RAG over your documents) now exists in three places in your toolkit: the pipeline you wrote yourself, OpenWebUI's knowledge collections, and framework abstractions like LlamaIndex.  For your final project, which do you choose and why?  Name the specific visibility or control feature that decides it.

*Societal:* An API key turns every OpenWebUI account into a programmable actor: scripts can chat, upload, and invoke tools at machine speed under a person's identity.  Universities, hospitals, and companies deploying frontends like this must decide who may hold API keys and what their scripts may do.  Propose one policy rule for a campus OpenWebUI deployment and identify what harm it prevents and what legitimate use it burdens.

---

## Where This Goes Next

You now have an orchestration substrate that is neither raw shell nor a framework: Python workflows driving an agent frontend, with every step visible in a chat transcript.  The *Agent Frameworks* module shows what LangChain, CrewAI, and AutoGen add (and hide) on top of exactly the loops you just wrote by hand.

---

## Further Reading

- OpenWebUI documentation: Tools, Functions (pipes and filters), and Knowledge: https://docs.openwebui.com
- OpenWebUI API reference (OpenAI-compatible endpoints, files, and RAG): https://docs.openwebui.com/getting-started/api-endpoints
- Ollama OpenAI compatibility documentation: https://github.com/ollama/ollama/blob/main/docs/openai.md
- Hands-on notebooks from this tutorial: [OpenWebUI_API_Client_With_Upload.ipynb](https://www.billmongan.com/Ursinus-CS357/files/notebooks/OpenWebUI_API_Client_With_Upload.ipynb) and [OpenWebUI_MultiAgent_Goal_Workflow.ipynb](https://www.billmongan.com/Ursinus-CS357/files/notebooks/OpenWebUI_MultiAgent_Goal_Workflow.ipynb)
- Course lab: [Compose and Verify a Local Agent Stack](https://www.billmongan.com/Ursinus-CS357/Assignments/LocalAgent/Direction2)

> **From the MCP and APIs session.**  Power Automate is a second, no-code route to the same integration problem MCP solves; it was moved here so the MCP session could stay on the protocol itself.

## No-Code Integration: Microsoft Power Automate

You just built an integration in **code**: a Flask server plus a Python client.  Most organizations also connect services a second way: **no-code automation platforms**.  Microsoft **Power Automate** is the one you are most likely to meet in a workplace (Zapier, Make, and IFTTT are close cousins).  Instead of writing an MCP server, you assemble a **flow** from pre-built **connectors**, each of which already wraps a service's OAuth/REST API. It is the same "reach the world's services" goal as MCP, reached with configuration instead of code.

**The building blocks of a flow:**

- **Trigger**: the event that starts the flow: a schedule, a new email, a new Asana task, a submitted form, or a manual button.
- **Connector actions**: the steps that follow ("Create a Google Calendar event," "Add a task in Asana," "Post to Teams").  Each connector authenticates once with **OAuth 2.0** and the platform stores the token, so the flow itself never contains a password or key.
- **Conditions and loops**: no-code control flow ("if the email has an attachment, then...").
- **HTTP action** *(premium)*: call any REST endpoint the built-in connectors do not cover, including a language-model API or one of your own services.
- **AI Builder / Copilot**: Microsoft's built-in AI steps: prompt a model, summarize, extract fields, or classify, dragged in like any other action.

**Predict, then read on.**  Suppose you have two flows turned on: Flow A's trigger is "When a new email arrives" (Outlook connector); Flow B's trigger is "When a task is created" (Asana connector).  A student submits a web form, the forms service sends a confirmation *email* to the team inbox, and an hour later a teammate *manually creates* an Asana task for the request.  Predict which trigger(s) fire, and in what order; write your prediction down before expanding the answer.

<details>
<summary>Reveal: which triggers fire?</summary>

Flow A fires first, the moment the confirmation email lands in the inbox.  Flow B fires an hour later, when the teammate creates the Asana task.  The form submission itself fires *nothing*; no flow is watching the forms service.  A trigger responds only to the specific event its connector watches, never to the upstream cause of that event.

</details>

**How to build one, end to end:**

1.  Sign in at **make.powerautomate.com** with a Microsoft account (a school or work account unlocks more connectors).
2.  Choose **Create -> Automated cloud flow**, name it, and pick a **trigger** (for example "When a new email arrives" in Outlook, or "When a task is created" in the Asana connector).
3.  Add a step and search for the **connector** you want (Google, Asana, Teams, SharePoint, ...).  The first time you use a connector it opens an **OAuth consent screen**; you grant scoped access once and the platform holds the token.
4.  Map fields from the trigger into the action with the **dynamic content** picker (for example, put the email's subject into a new task's title).
5.  To add AI, insert an **AI Builder** action (prompt a model, extract information) or an **HTTP** action that POSTs to a model's `/v1/chat/completions` endpoint, the same request body you have used all unit.
6.  **Test** with the built-in run panel, inspect each step's inputs and outputs, then **turn the flow on** so its trigger runs it automatically.

In a Power Automate flow, the OAuth 2.0 credential that lets a connector act on your account is:

- typed into each action as a password parameter
- granted once through a consent screen and stored by the platform, so the flow definition never contains the secret
- pasted into the flow's exported definition so teammates can reuse it
- regenerated by the AI Builder step on every run

<details markdown="1"><summary>Answer</summary>

granted once through a consent screen and stored by the platform, so the flow definition never contains the secret

</details>

**Where it fits and where it does not.**  No-code platforms are fastest when a connector already exists for both services and the logic is simple.  They struggle when you need custom logic, real version control, or a portable integration you can host yourself, which is exactly when writing an MCP server or a small agent (as you did above) wins.  And the trust questions do not disappear: a connector holds a real OAuth token with real scopes, so the same "who wrote it, what can it do, is it least-privilege" checklist from Model 2 still applies.

### Questions to Work Through

7.  A Power Automate connector and your Flask server both let a system "create a calendar event."  Name two things the no-code connector gives you for free that you handled yourself in code, and one thing the code version gives you that the connector cannot.

   > *Hint: For free: the OAuth flow and token storage, plus a maintained schema/UI for the service's fields.  In code you keep: custom logic, self-hosting and portability, and version-controlled review of exactly what runs.*

8.  In step 5 you can call a model with an HTTP action whose body is a `/v1/chat/completions` payload.  Where should the model's API key live so it does not end up pasted into the flow definition that teammates can open and export?

   > *Hint: Store it as a secure input / environment variable / connection secret (or a Key Vault reference) and reference it; never hard-code it into the HTTP action's headers, where it becomes part of the exported flow.  Same rule as every other secret this term.*

Compared with writing an MCP server, a no-code platform like Power Automate primarily trades:

- accuracy for speed: its flows produce less correct results
- control and portability for speed and pre-built, already-authenticated connectors
- security for convenience: flows cannot use OAuth
- nothing; it is strictly better in every way

<details markdown="1"><summary>Answer</summary>

control and portability for speed and pre-built, already-authenticated connectors

</details>

> **Common Misconception:** "No-code means there is no security to think about."  Often the opposite: one flow can hold OAuth tokens to your email, files, and calendar at once and run unattended.  The connector hides the *plumbing*, not the *risk*: least-privilege scopes, controlling who can edit the flow, and keeping model keys out of the flow body all still matter.

---
