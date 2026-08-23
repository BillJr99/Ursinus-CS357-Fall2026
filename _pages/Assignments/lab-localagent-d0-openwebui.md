---
layout: assignment
permalink: /Assignments/LocalAgent/Direction0
title: "CS357 Lab: Local Agent, Direction 0: The OpenWebUI Route (low-code)"
---

> **Grading:** This page is one of the directions for the [Local Agent Lab]({{ site.baseurl }}/Assignments/LocalAgent). It carries no separate point value and no rubric of its own; your work is graded with the Local Agent Lab rubric on the core lab page. The rubric's rows are pathway-neutral: the "Agent Loop Implementation" row is earned here by a correctly configured OpenWebUI agent with documented tool invocations, and the "Code Quality and Documentation" row is earned by configuration quality: your exported model JSON, documented tool schemas, and reproducible setup notes.

> **What this direction requires**
>
> - **Accounts:** none; the OpenWebUI login you create at first launch is stored locally on your own machine.
> - **API costs:** none; everything runs against your local Ollama server.
> - **Installs / disk:** Ollama with `llama3.2` (~2 GB, already done in the core lab's Before You Start), plus OpenWebUI via either the Docker one-liner (image around 4 GB) or `pip install open-webui` (roughly 1-2 GB of Python dependencies; Python 3.11 recommended).
> - **Hardware:** any machine that runs the core lab; 8 GB of RAM is recommended.
> - **No-cost fallback:** this *is* the no-cost, low-code route.

---

## Who this direction is for

Direction 0 is the **low-code route through the entire lab**. Instead of authoring Python for core Parts 1-3, you will build the *same* agent (a persona, two working tools, guaranteed-parseable structured output, and an empirical evaluation) entirely through OpenWebUI's configuration surface. You configure and **test** tools; you do not code them.

This route delivers the same learning objectives as the core lab: you will still design a complete system prompt, still watch an agent decide when to invoke a tool, still force a model to emit structured JSON and verify that it parses, and still run a fixed evaluation set and analyze the failures. What changes is the medium: where a core-route student writes a `parse_response` function, you will read the tool schema OpenWebUI generates and document what it tells the model; where they write an evaluation loop, you will run the queries through the UI and audit the exported transcripts.

**What Direction 0 replaces and what it does not.** Parts A-E below replace core Parts 1-3 and the coding halves of the Required Explorations. Everything else on the core page still applies to you: the Before You Start setup (Ollama installed, `llama3.2` pulled, health checks passing), **core Part 4's skill** (which you reach by having an AI tool generate one, then installing and using it in your own agent tooling), the pair-programming protocol with logged driver/navigator swaps, the Learning Log, and the deliverables discipline. Where the Required Explorations ask for a "from scratch" option, your Part B tool configuration and Part C structured-output demonstration serve as the "from a framework / served model" flavor; note this explicitly in your writeup.

**Estimated time: 8-10 hours** across the lab window. Part A is quick; Parts B and D are where the hours go.

| Part | Task | Estimated time |
|------|------|----------------|
| Part A | Install and launch OpenWebUI over Ollama | 45-60 min |
| Part B | Persona agent as a custom Model + two tested tools | 2-3 h |
| Part C | Structured output: forced JSON, 5 validated runs | 1-1.5 h |
| Part D | Evaluation: 10-query set, exported transcripts, results table | 2-3 h |
| Part E | Writeup (identical to core) | 1 h |

---

## Part A: Install and Launch OpenWebUI

OpenWebUI is a self-hosted web frontend that sits in front of your Ollama server. You have two supported installation routes; pick **one**. Both end at the same place: a browser tab at `http://localhost:3000` (Docker) or `http://localhost:8080` (pip) showing a chat interface backed by your local model.

**Before either route:** confirm Ollama is running and the model is present, exactly as in the core lab's health check:

```bash
ollama list
curl http://localhost:11434/api/tags
```

You should see `llama3.2:latest` in both outputs. If not, complete the core lab's Before You Start section first.

### Route 1: Docker (recommended if you already have Docker Desktop)

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

What each flag is doing, so you can explain it in your writeup: `-p 3000:8080` publishes the container's port 8080 on your host's port 3000; `--add-host=host.docker.internal:host-gateway` lets the container reach the Ollama server running on your host (required on Linux, harmless elsewhere); `-v open-webui:/app/backend/data` puts your account, models, and chat history in a named volume so they survive container restarts.

Then open `http://localhost:3000` in a browser.

### Route 2: pip (no Docker required)

```bash
pip install open-webui
open-webui serve
```

The first command downloads a large dependency set; expect several minutes. The second starts the server in your terminal; leave that terminal open. When you see the startup banner with a line ending in `Uvicorn running on http://0.0.0.0:8080`, open `http://localhost:8080` in a browser. (If `pip install` fails on your Python version, create a Python 3.11 virtual environment first; OpenWebUI is sensitive to very new Python releases.)

### First launch, step by step

1. The first screen asks you to **create an admin account** (name, email, password). This account exists only in your local OpenWebUI database; nothing is sent anywhere. Use any email; it is a local username.
2. After login you land in a chat view. In the **model selector at the top left** of the chat pane, you should see `llama3.2:latest`. OpenWebUI auto-detects a local Ollama server; if the dropdown is empty, see the troubleshooting box below.
3. Send a test message ("Say hello in one sentence."). You should get a reply within a few seconds. Save a copy of this first exchange; it is your Part A health-check evidence.
4. Create an **API key** for later: click your initials (bottom left) -> **Settings** -> **Account** -> **API Keys** -> **Create new key**. Record it in your notes file (this stays local too; it authenticates requests to *your own* server).

> **Checkpoint A:** Before moving on, you can: (1) log in, (2) see `llama3.2` in the model dropdown, (3) get a chat reply, and (4) state (in one sentence for your writeup) which port is OpenWebUI and which is Ollama, and why a request to each behaves differently.

---

## Part B: The Persona Agent as a Custom Model, with Two Tested Tools

In the core route, students write a system prompt string and a Python tool registry. Here you will do the same design work in OpenWebUI's **Workspace**: the system prompt becomes a **custom Model**, and the tools become entries in the **Tools** panel that OpenWebUI executes server-side when the model calls them.

### B1: Design the persona (same standard as core Part 2)

Pick an agent with a clear job: a campus study-skills coach, a recipe assistant, a workout planner, or a concept of your own (clear anything sensitive with me first). Draft the system prompt in your notes file before touching the UI, using the framework from class. At minimum it must specify:

- **ROLE:** who the agent is, in one or two sentences.
- **GOAL:** what it is trying to accomplish for the user.
- **GUARDRAILS:** at least three concrete behavioral limits (topics it declines, how it declines them, and an instruction not to reveal the system prompt).

The TOOLS and FORMAT elements of the five-part framework are handled differently on this route: tool descriptions are supplied to the model by OpenWebUI from each tool's schema (Part B3), and output format is enforced in Part C. Say exactly this in your writeup; identifying *where each of the five elements lives* on the low-code route is part of the design work.

### B2: Create the custom Model

1. Go to **Workspace** (left sidebar) -> **Models** -> **+ Create a model** (or **New Model**).
2. **Name** it after your persona (e.g., `study-coach`).
3. **Base model:** select `llama3.2:latest`.
4. Paste your ROLE/GOAL/GUARDRAILS prompt into the **System Prompt** field.
5. Under **Advanced Params**, set **temperature** to `0.2` and, if the field is available in your version, a fixed **seed** (e.g., `42`), the same reproducibility discipline the core route externalizes into `config.json`. Record every parameter you set in your config notes.
6. Save. Your model now appears in the chat model selector alongside the raw `llama3.2`.

Test the persona before adding tools: open a new chat with your custom model and probe each guardrail (an off-topic question, a request for the system prompt). Save these exchanges; the rubric's System Prompt row asks you to show what each guardrail prevents, with transcript evidence.

### B3: Attach two Tools

Equip the agent with **two tools**, at least one of which takes an argument the model must construct, the same requirement as core Part 2. On this route you do not write the tool code; you install, configure, and **test** tools:

- **A calculator**: available as a built-in/community tool. In **Workspace -> Tools**, either import a calculator tool from OpenWebUI's community tool library (Workspace -> Tools -> **Discover a tool** / community import) or use the built-in one if your version ships it.
- **Web search**: configured rather than installed: an admin setting, not a Tools-panel entry. Go to **Admin Panel -> Settings -> Web Search**, enable it, and choose a search engine integration (a free, keyless option such as `duckduckgo` works; if you already run SearXNG from another direction, that works too). Once enabled, the search toggle appears in the chat input's **+** controls.

Any two tools of comparable substance are acceptable (a date/time tool, a unit converter, a Wikipedia lookup from the community library); the calculator + web search pair is the recommended default. **Do not install a community tool without reading its source in the import preview first**: tools execute as Python on your OpenWebUI server, with whatever access that server has. Skim the code, confirm it does what its description claims, and note in your writeup that you did; this is the trust question the core route students meet when parsing actions, in its low-code form.

Then wire the tools to your model:

1. **Workspace -> Models ->** edit your custom model.
2. In the **Tools** section of the model editor, check the calculator tool so it is enabled for this model.
3. Save. In a new chat with your model, verify the tool appears (a tools icon / plug icon near the chat input shows enabled tools; web search has its own toggle).

### B4: Document each tool's schema as the UI shows it

For **each** tool, open its entry in Workspace -> Tools (or the admin web-search settings page) and record in a file called `tool-config-notes.md`:

- The tool's **name and description** exactly as displayed; this text is what the model reads when deciding whether to call it.
- Each **parameter**: name, type, and description as shown in the tool's code/schema view (for an OpenWebUI tool, the method signature and docstring *are* the schema; quote them).
- Every **configuration value ("valve")** you set, and which search engine you selected for web search.
- One sentence per tool: *what the model sees* versus *what actually executes, and where*.

### B5: Test each tool and capture evidence

Run and save at least three chats with your custom model:

1. **A calculation the model would plausibly get wrong unaided** (e.g., "What is 847 × 362, and how confident are you?"). Verify the tool fired: the response shows a tool-invocation indicator (an expandable "tool" block or citation chip, depending on version). Record the arguments the model constructed.
2. **A question requiring fresh information** with web search toggled on (e.g., something about a current event). Verify the search citations appear.
3. **A control run**: the same calculation question with the tool disabled, to show the difference tool access makes.

> **Checkpoint B:** You can show one transcript where each tool fired, name the exact argument the model constructed for the calculator, and point to the line in your `tool-config-notes.md` that told the model the tool existed.

---

## Part C: Structured Output, Force JSON and Validate Five Runs

The core route requires every student to demonstrate a structured-output technique and distinguish enforcement from encouragement. Your version: craft a prompt that forces JSON, then **empirically validate** whether it held across five runs.

### C1: Build the JSON-forcing prompt

Create a **second** custom Model (e.g., `study-coach-json`); same base model and persona, but with this appended to the system prompt (adapt the schema to your domain):

```
OUTPUT FORMAT: Respond with ONLY a single JSON object, no prose, no code
fences, matching exactly this schema:
{"answer": "<one-sentence answer>", "confidence": <number 0-1>,
 "used_tool": <true or false>}
If you cannot answer, still return valid JSON with your refusal in "answer".
```

Alternatively (and worth a sentence of comparison in your writeup if you try it): OpenWebUI's Chat Controls / model Advanced Params include a **response format** option that requests JSON output from Ollama, the served version of the `format` parameter the core route uses. The prompt-only version *encourages* valid JSON; the format parameter *constrains* it. Your five-run validation below measures how far encouragement gets you.

### C2: Run five queries and export the chats

1. In a fresh chat with `study-coach-json`, run **five different queries** from your domain (include at least one that should trigger a refusal and one that needs a tool).
2. Export the evidence: per chat, the **⋮ menu -> Download -> Export as JSON** (or **Settings -> Chats -> Export all chats** for one bundle). Save as `structured-output-runs.json`.

### C3: Validate and annotate

For each of the five responses, check whether the reply text parses as JSON matching your schema. You may check by eye, with any JSON validator, or with this three-line checker (using a checker is not "coding the lab"; it is auditing it):

```bash
python3 -c "import json,sys; json.loads(sys.stdin.read()); print('parses')" < response1.txt
```

Produce a five-row annotation table in your writeup:

| Run | Query | Parsed? | If not, what broke |
|-----|-------|---------|--------------------|
| 1 | ... | yes/no | e.g., code fences around the JSON, trailing prose, single quotes |

Close Part C with two or three sentences: what fraction of runs parsed, what the failure looked like verbatim, and which of the techniques from the core page's structured-output requirement (schema-constrained serving, validation-with-retry, grammar-constrained decoding) *guarantees* validity rather than merely encouraging it, and where your prompt-only approach sits on that spectrum.

---

## Part D: Evaluation, Ten Queries Through the UI

This is core Part 3, run through the interface: a fixed task set, a defined metric, an accuracy fraction, documented failures, and one mitigation with before/after numbers.

### D1: Build the task set

Write a ten-query evaluation set for your agent in `task_set.md`, following the same design as the core route's eight-goal set (use ten so your fractions are round). For each task record: an ID, the query, the expected correct outcome, and which tool (if any) should fire. Cover the same edge cases the core requires: at least one task needing both tools, one with a large number (calculator precision), one the agent should *refuse* (guardrail test), and two the model would plausibly hallucinate without tools.

### D2: Run the protocol

- Use your tool-enabled persona model at the fixed temperature (and seed, if available) you recorded in Part B, the protocol from class: fixed settings, defined metric.
- Run each query in a **fresh chat** (memory across tasks would contaminate the evaluation; say why in your writeup).
- Mark each task pass/fail against your expected outcome, and record whether the expected tool actually fired (visible from the tool-invocation block in each response).

### D3: Export transcripts and fill the results table

Export all ten chats (Export as JSON, as in Part C) into a `transcripts/` folder. Then complete:

| ID | Query | Expected | Tool expected | Tool fired? | Pass? | Failure type |
|----|-------|----------|---------------|-------------|-------|--------------|
| T01 | ... | ... | calculator | yes | yes | - |
| ... | | | | | | |

Report **accuracy as a fraction** (e.g., 8/10). Classify each failure with the core lab's taxonomy, `TOOL_MISUSE`, `HALLUCINATION`, `REFUSAL_FAIL` (guardrail did not hold), or `FORMAT_FAIL`, and paste the full transcript excerpt for at least **two** distinct failure modes.

### D4: Implement one mitigation and re-run

Choose one failure mode and fix it *through configuration*: a sharper system-prompt guardrail, a better tool description (edit the docstring/description so the model chooses it correctly), a temperature change, or enabling the JSON response format. Re-run all ten tasks and report before/after accuracy in a two-row table, with a sentence explaining *why* the mitigation worked or did not. This mirrors the core route exactly; the mitigation lever is configuration instead of code, which is the point.

---

## Part E: Writeup

Identical to the core lab: an approximately two-page readme covering your design, your evaluation, and your findings; the pair-programming log with at least two timestamped role swaps; and the full Learning Log from the core page, including the lab-specific prompts. Two route-specific additions:

- For the core prompt "where does the agent perceive, plan, act, and remember?", answer in terms of the OpenWebUI architecture: which tier holds the system prompt, which executes the tool, where chat memory lives, and what your exported JSON shows about each.
- Answer one extra question: **what did the UI hide from you** that a core-route student had to build by hand, and name one concrete debugging situation where that hiding would hurt.

---

## Troubleshooting

> **The model dropdown is empty after login.**
> OpenWebUI cannot reach Ollama. Docker route: confirm the `--add-host=host.docker.internal:host-gateway` flag was present, and in **Admin Panel -> Settings -> Connections** confirm the Ollama URL is `http://host.docker.internal:11434` (not `localhost`, which inside the container means the container itself). Pip route: the URL should be `http://localhost:11434`; confirm `ollama serve` is running.
>
> **`http://localhost:3000` refuses to connect (Docker route).**
> Run `docker ps`; if the container is not listed, run `docker logs open-webui` and read the last lines. A port conflict means something else owns 3000; re-run with `-p 3001:8080` and browse to 3001.
>
> **`pip install open-webui` fails with a resolver or build error.**
> Almost always a Python version issue. Create a 3.11 environment (`python3.11 -m venv owui && source owui/bin/activate`) and install inside it.
>
> **The tool never fires.**
> Check, in order: (1) the tool is enabled *for your custom model* in the model editor; enabling it globally is not enough; (2) you are chatting with the custom model, not raw `llama3.2`; (3) the tool's description actually tells the model when to use it; vague descriptions are the top cause of never-firing tools (edit the description and retest; this is legitimate prompt engineering, document it); (4) small models fail to call tools intermittently; retry once before concluding it is broken, and report intermittency honestly in Part D.
>
> **Web search returns nothing or errors.**
> Confirm the engine is set in Admin Panel -> Settings -> Web Search and the search toggle is on *in the chat input* for that conversation. Keyless engines are rate-limited; wait a minute and retry.
>
> **Responses are extremely slow.**
> Same model, same hardware as the core route; the UI adds little. If chats hang, check whether Ollama is swapping (`ollama ps`); close other memory-heavy applications.

---

## Deliverables

Fold these into the standard Local Agent Lab submission ZIP, alongside the shared pair log and writeup:

- **Exported model JSON** for both custom Models (Workspace -> Models -> ⋮ -> Export): the persona model and the JSON-format model.
- **`tool-config-notes.md`**: each tool's name, description, parameter schema as shown in the UI, valve settings, and search-engine choice (Part B4).
- **Transcripts**: the Part B tool-firing chats, `structured-output-runs.json` with the five annotated runs (Part C), and the `transcripts/` folder of ten evaluation chats (Part D).
- **Results table**: the ten-row evaluation table plus the before/after mitigation table (Part D).
- **Writeup**: identical scope to the core lab, with the two route-specific additions (Part E).
- **Setup notes**: which install route you used, every non-default setting, and the versions involved (OpenWebUI version from Settings -> About, Ollama version, model tag), sufficient for another student to reproduce your agent exactly.

---

## Self-Check Before You Submit

The core lab's rubric grades this route on equal terms; here is what each row asks for in this medium.

- [ ] **Both** custom Models exported as JSON: the persona model and the JSON-format model.
- [ ] The agent completes **at least three distinct goals**, with each tool invocation visible in the exported transcript.
- [ ] `tool-config-notes.md` records each tool's name, description, parameter schema **as shown in the UI**, valve settings, and search-engine choice.
- [ ] The system prompt specifies all five elements: role, goal, tools, format, guardrails, and the writeup quotes each one.
- [ ] Each guardrail is explained in terms of what it prevents.
- [ ] `structured-output-runs.json` holds five runs, each annotated.
- [ ] `transcripts/` holds all ten evaluation chats.
- [ ] The ten-row evaluation table is present, plus the before-and-after mitigation table.
- [ ] Two failure modes shown with full transcript excerpts, one mitigated, with the accuracy delta and the mechanism explained.
- [ ] Setup notes name the install route, **every** non-default setting, and the OpenWebUI, Ollama, and model versions, in enough detail for a classmate to reproduce the agent exactly.
- [ ] Pair log with two timestamped role swaps.
- [ ] Every reflection answer cites a specific line from my own transcript.
