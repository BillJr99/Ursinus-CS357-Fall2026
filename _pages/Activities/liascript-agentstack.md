<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-agentstack.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Local Agent Stack: Wiring Containers into a System

> **Supplemental — required prep only for Lab 1 Directions 2–3 (the Compose-stack and container-hardening directions).** Do the installs and image pulls at home before the *Studio: Local Agent Stack Clinic* session: Docker Desktop plus roughly 6 GB of images. In the studio we build only the 3-container minimal stack; the full 20-service tour below is reference material.

The *Docker from Zero: Containers for Agent Builders* supplemental activity gave you one container — and one container is a demo; a *stack* of containers that talk to each other is infrastructure. This module deploys the course's local AI ecosystem (model servers, a unifying gateway, tool servers, web frontends, and autonomous agents) and teaches the wiring discipline that makes two dozen services coexist: tiered roles, a port plan, per-service identity directories, and `host.docker.internal` as the connective tissue. The arc: **the tier model $\rightarrow$ the inference foundation $\rightarrow$ the gateway $\rightarrow$ frontends and tools $\rightarrow$ agents $\rightarrow$ wiring and verification**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisites: the *The Shell: Your Agent's Native Habitat* and *Docker from Zero: Containers for Agent Builders* supplemental activities, completed honestly. Hardware note: the full stack runs comfortably on a mini PC or a mid-range laptop because we choose small models; nothing here requires a GPU. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Container** | A self-contained, isolated software environment — like a shipping container that carries everything a program needs to run, so it works identically on any machine. | Each service (Ollama, Open WebUI, etc.) runs in its own container |
| **Tier** | A layer in a system where every component in that layer has the same job. Grouping by tier makes it easy to reason about which piece does what. | The Inference tier runs models; the Gateway tier routes requests to them |
| **Gateway** | A single entry point that routes incoming requests to the right backend service. Like a hotel switchboard: you call one number, and it connects you to housekeeping or room service. | `llmproxy` on port 4000 routes to Ollama, LocalAI, or cloud models |
| **Port** | A numbered "door" on a computer through which one specific service listens for connections. Two services cannot share the same port number on the same machine. | Ollama listens on port 11434; Open WebUI on port 3000 |
| **`host.docker.internal`** | A special hostname that, from inside a Docker container, refers back to the host machine where Docker is running. Essential for containers that need to call services running on the host. | The gateway uses this to reach Ollama running natively on the host |
| **Identity Directory** | A folder on the host machine that is mounted into a container as its persistent storage. When the container is deleted and recreated, its state survives because it lived on the host. | `$HOME/agents/hermes/home` persists the Hermes agent's memory |

---

# Part I: Architecture Before Containers

In this part, you will learn the five-tier mental model that organizes every service in our stack — so that instead of memorizing twenty container names, you can place any new service by asking "what job does it do?" This mental model is the same one professional engineers use to design and debug complex distributed systems.

## 1. The Tier Model

**Why this matters:** When you first see a list of twenty container names, it looks overwhelming — like being handed a car's parts list before you have seen a car. The tier model is the map that organizes all those parts. Instead of memorizing twenty names, you memorize five jobs, and every container slots into one. This is the same principle engineers use to design any complex system: layer it so each layer has one responsibility, and components in different layers communicate through clean interfaces. Think of it like a restaurant: the kitchen (inference) prepares food, the server (gateway) carries it to tables, the dining room (frontend) is where guests sit, and the delivery app (agent tier) places orders automatically.

Memorizing two dozen container names is hopeless; memorizing **five tiers** is easy, and every container in our stack slots into one:

| Tier | Job | Our Containers | Example / In Our Course |
|------|-----|----------------|-------------------------|
| Inference | Run AI models and expose them through a standard API that other software can call | `ollama`, `lmstudio`, `local-ai`, `longcat-video` | Ollama on port 11434 answers questions like "summarize this document" |
| Gateway | Provide one stable endpoint that hides which backend model is actually running, so swapping models requires only one config change | `llmproxy` | LiteLLM on port 4000 routes your request to whichever model you configured |
| Tools | Give agents capabilities beyond text generation — web search, databases, external APIs | `mcpproxy`, `searxng`, `surrealdb` | SearXNG lets agents search the web privately; SurrealDB stores results persistently |
| Frontends | Provide human-facing interfaces (chat UIs, notebooks, voice, slides) that talk to the gateway | `open-webui`, `open-terminal`, `open-design`, `open-notebook`, `voicebox`, `presenton`, `calibre-web` | Open WebUI at port 3000 gives you a ChatGPT-style chat interface connected to your local models |
| Agents | Run autonomous or task-bounded workers that can take multi-step actions without human input at each step | `hermes`, `freebuff`, `agent0`, `openhands-server`/`openhands`, `nanoclaw`, `nanoclaw-dind`, `zeroclaw`, `openclaw-gateway`, `n8n` | n8n at port 5678 runs scheduled workflows; Hermes handles tool-calling tasks |

Two structural principles govern everything. First, **all inference flows through the gateway**: every frontend and agent sends OpenAI-compatible requests to `llmproxy`, which routes to Ollama, LocalAI, or a cloud free tier per one YAML file, so swapping a model never touches more than that file. Second, **every service gets its own identity directory** under `$HOME/agents/<service>/`, bind-mounted in, so any container can be destroyed and recreated without losing state, and no two services can contaminate each other.

## 2. The Port Plan

**Why this matters:** Port conflicts are the most common reason a new service silently fails to start — it tries to claim a port that is already taken, crashes quietly, and you spend an hour debugging what looks like a network problem. The discipline here is simple: write down every port assignment before you run anything. It takes two minutes and prevents hours of frustration. Think of ports like parking spaces in a lot: each car (service) needs its own assigned spot, and two cars cannot share one spot.

Containers collide on ports before they collide on anything else, so the plan comes first. The well-known defaults anchor the table; every other service is assigned a host port in its `run.sh`, and the table (kept in your stack repository) is the single source of truth:

| Service | Host Port | Notes | Example / In Our Course |
|---------|-----------|-------|-------------------------|
| `ollama` | 11434 | Native service or container; the workhorse inference engine | `curl http://localhost:11434/api/tags` lists your downloaded models |
| `lmstudio` | 1234 | LM Studio's local server default; adds a friendly GUI for model management | Useful when you want a visual model browser instead of the command line |
| `local-ai` | 8080 | OpenAI-compatible GGUF inference; adds Whisper transcription and image generation | Use when you need voice-to-text or image generation alongside language models |
| `llmproxy` | 4000 | The gateway; every frontend and agent points here instead of directly at models | All your apps use `http://localhost:4000/v1` as their "OpenAI" base URL |
| `open-webui` | 3000 | Browser-based chat frontend resembling ChatGPT | Point your browser to `http://localhost:3000` for a full chat UI |
| `searxng` | 8081 | Private metasearch engine; default image port 8080 is remapped to avoid collision with local-ai | Agents call this to search the web without sending queries to Google |
| `n8n` | 5678 | Visual workflow automation — build pipelines with a drag-and-drop canvas | "Every morning at 7am, summarize new emails and save to workspace" |
| `surrealdb` | 8000 | Multi-model database for persistent agent storage | Agents write facts here and retrieve them across sessions |
| `calibre-web` | 8083 | E-book library management with a web interface | Index your PDF collection and let agents search it |
| `agent0` | 8082 | Autonomous agent with a full web UI for monitoring its actions | Watch Agent Zero plan and execute multi-step tasks in real time |
| remaining services | assigned | One row each in your stack's port table, no exceptions | Before adding any new service, add its row first |

Notice the `searxng` row: its image default (8080) collides with `local-ai`, so we remap on the host side with `-p 8081:8080`, which is the entire point of the `-p HOST:CONTAINER` Docker flag. **The rule: before any `docker run`, the service gets a row.** Port conflicts then become impossible by construction rather than debugged at midnight.

---

## Model 1: Place the Pieces

**Why this matters:** Architecture decisions made on paper are far cheaper to revise than architecture decisions discovered in production at midnight. This model practices the reasoning you will use every time you add a new service: where does it belong, what does it need, and how does it connect to what is already running?

### Critical Thinking Questions

1. A teammate proposes having `open-webui` talk directly to `ollama` "to skip a hop." What does the stack lose? Name two concrete things the gateway tier buys, using the one-YAML-file argument.

   > *Hint: Imagine you have five frontends all pointed directly at Ollama. Now you want to swap Ollama for a different model. How many config files do you have to update? Now imagine they all point at the gateway. How many files change?*

2. `nanoclaw-dind` runs Docker *inside* Docker so its agent can spawn sandboxed sub-containers. Which tier does it belong to, and what governance property is the inner Docker layer providing? Connect to the irreversible-actions taxonomy from class.

   > *Hint: If an agent can execute arbitrary code, what is the worst thing it could accidentally do to the host machine? What does wrapping that code execution inside an inner Docker container prevent?*

3. Assign host ports to three unassigned services from the table, checking your choices against every existing row. State the collision you avoided.

   > *Hint: List all reserved ports first: 11434, 1234, 8080, 4000, 3000, 8081, 5678, 8000, 8083, 8082. Your three new services must pick ports not in that list. Common safe ranges: 8084–8099, 7000–7999, 9000–9099.*

---

# Part II: Standing Up the Core

In this part, you will bring up the stack tier by tier — inference first, then gateway, then frontends and tools, then agents. Each tier must be working before the next one is added. This incremental approach is the professional practice: it isolates failures and makes debugging tractable.

## 3. Inference: Ollama First

Ollama is the inference foundation — the service that downloads model files and answers requests. Everything else can be added incrementally once it answers:

```bash
# Native install (preferred: keeps model I/O off the Docker path)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:3b && ollama pull llama3 && ollama pull hermes3:8b
curl http://localhost:11434/api/tags        # verify: lists your models
```

`lmstudio` and `local-ai` are alternates with the same OpenAI-compatible surface (LM Studio adds a friendly GUI for model management on port 1234; LocalAI adds whisper transcription and image generation behind 8080); the gateway makes the choice invisible to everything downstream, so start with Ollama and add the others when a need appears.

## 4. The Gateway: llmproxy

The gateway (a LiteLLM-style router — a program that receives requests in the standard OpenAI format and forwards them to whichever local or cloud model you have configured) is one Compose service plus one routing file. Pay attention to the `api_base` field: this is where the `host.docker.internal` hostname (the special address that lets a container reach the host machine) becomes critical.

Build it as a numbered checklist — complete and verify each step before starting the next:

1. **Create the routing file** at `llmproxy/litellm_config.yaml`. This maps each public model name to a backend:

   ```yaml
   # llmproxy/litellm_config.yaml
   model_list:
     - model_name: llama3
       litellm_params:
         model: ollama/llama3
         api_base: http://host.docker.internal:11434
     - model_name: qwen2.5-3b
       litellm_params:
         model: ollama/qwen2.5:3b
         api_base: http://host.docker.internal:11434
   ```

2. **Create the Compose file** at `llmproxy/docker-compose.yml`, mounting the routing file read-only:

   ```yaml
   # llmproxy/docker-compose.yml
   services:
     llmproxy:
       image: ghcr.io/berriai/litellm:main-latest
       ports: ["4000:4000"]
       volumes: ["./litellm_config.yaml:/app/config.yaml:ro"]
       command: ["--config", "/app/config.yaml", "--port", "4000"]
       extra_hosts: ["host.docker.internal:host-gateway"]
       restart: unless-stopped
   ```

3. **Start the service** from the `llmproxy/` directory:

   ```bash
   docker compose up -d
   ```

   ✅ **Checkpoint:** what should `docker compose ps` show now?

   <details>
   <summary>Expected answer</summary>

   Exactly one service, `llmproxy`, with status `Up` (or `running`) and the ports column showing `0.0.0.0:4000->4000/tcp`. If the status is `Restarting`, run `docker logs llmproxy` — the usual culprit is a typo in the mounted config path or invalid YAML in the routing file.

   </details>

4. **Verify from the host** that the gateway answers and knows its models:

   ```bash
   curl -s http://localhost:4000/models -H "Authorization: Bearer sk-litellm-local"
   ```

   ✅ **Checkpoint:** what should this `curl` return?

   <details>
   <summary>Expected answer</summary>

   A JSON object whose `data` array lists the two configured model names, `llama3` and `qwen2.5-3b`. An empty list means the routing file did not mount into the container; `connection refused` means the container is not running — go back to the step 3 checkpoint.

   </details>

Read the config's `api_base` carefully: the gateway is *itself a container*, so it reaches host-resident Ollama via `host.docker.internal`, and the `extra_hosts` line is what makes that name resolve on Linux. This one file is where every future model, local or cloud, gets added.

## 5. Frontends and Tools

With the gateway answering, frontends attach by URL. Open WebUI:

```bash
docker run -d --name open-webui -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v "$HOME/agents/openwebui/data:/app/backend/data" \
  ghcr.io/open-webui/open-webui:main
# Then in its Admin Settings -> Connections -> OpenAI:
#   URL http://host.docker.internal:4000/v1, key sk-litellm-local
```


> **Isolation and trust boundaries** - which tier may talk to which, and what a container actually isolates - are worked through in the optional activity [Containerization and Safety](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-containerizationsafety.md).

## 6. The Agent Tier

Agents are where the stack earns its name — they are the autonomous workers that use the inference, gateway, frontend, and tool tiers as their instruments. Each agent has a distinct personality and capability level, but they all deploy the same way: a port row, an identity directory, and a gateway URL in their config. The code below shows the pattern for `hermes`, a tool-calling agent; the others follow the same template.

```bash
docker pull nousresearch/hermes-agent:latest
mkdir -p "$HOME/agents/hermes/home"
docker run --rm -it --name hermes \
  --add-host=host.docker.internal:host-gateway \
  -v "$HOME/agents/hermes/home:/home/hermes/.hermes" \
  -v "$HOME/agents/workspace:/workspace" \
  nousresearch/hermes-agent:latest
```

The others slot in by personality: `agent0` (Agent Zero) is the fully autonomous, self-improving end of the spectrum with a web UI; `openhands-server` plus `openhands` provide a software-engineering agent with its own runtime sandbox; `freebuff` is our task-bounded harness (give it a task and a workspace, it executes and exits); the `nanoclaw`/`nanoclaw-dind`/`zeroclaw` family and `openclaw-gateway` are lightweight Claude-style workers behind a routing gateway; and `n8n` is the workflow scheduler that strings any of them into timed pipelines (its visual editor at port 5678 makes it the natural home for "every morning, summarize new items"). Deploy each the same way, without exception: a port row, an identity directory, `--add-host`, gateway URL in its config. The uniformity *is* the lesson.

## 7. Verification: The Wiring Matrix

A stack is not up until its connections are proven, pairwise, from the right vantage points. The matrix below tests each critical link: host-to-service, container-to-host, and end-to-end through the full chain. Run these commands in order; a failure at any cell tells you exactly which link broke and where to look first.

Build the matrix:

```bash
# From the HOST: is each service alive?
curl -s http://localhost:11434/api/tags | head -3        # ollama
curl -s http://localhost:4000/models -H "Authorization: Bearer sk-litellm-local" | head -3
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000   # open-webui

# From INSIDE a container: does the host alias resolve and answer?
docker exec -it open-webui curl -s http://host.docker.internal:4000/models \
  -H "Authorization: Bearer sk-litellm-local" | head -3

# End to end: one chat completion through the whole chain
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-litellm-local" -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5-3b","messages":[{"role":"user","content":"Say STACK OK."}]}'
```

When a cell of the matrix fails, the diagnostic ladder from the *Docker from Zero: Containers for Agent Builders* supplemental activity applies: host-side first, container-side second, then the `--add-host` flag, the port row, and the logs, in that order.

---

# Part III: Practice

In this part, you will build and verify a working minimal stack, extend it with a tool and an agent, and deliberately break and fix a common networking issue — so that when something goes wrong in your project work, you have already seen and diagnosed it.

## 8. Exercises

1. *Minimal viable stack.* Deploy Ollama, llmproxy, and Open WebUI; complete a chat in the browser that round-trips through all three; submit your port table and the end-to-end curl output.

   - *What to do:* Follow sections 3 and 4 above. Once both services are running, open `http://localhost:3000` in your browser, configure the OpenAI connection to point at `http://host.docker.internal:4000/v1`, and send one message. Then run the end-to-end `curl` command from the Verification section and capture the output.
   - *Starter hint:* If the browser chat fails, run the end-to-end `curl` first. If that works, the problem is the Open WebUI connection setting. If the curl fails, check `docker logs llmproxy` and verify the `extra_hosts` line is present.
   - *You've succeeded when:* The browser shows a response from your local model, and the curl command returns a JSON object containing `"STACK OK"` in the content field.

2. *Add a tool.* Deploy searxng on its remapped port and confirm from inside another container that `http://host.docker.internal:8081` answers a search query. Explain in two sentences why the remap was necessary.

   - *What to do:* Run SearXNG with `-p 8081:8080`. Then, from inside the Open WebUI container, run `docker exec -it open-webui curl http://host.docker.internal:8081/search?q=test&format=json` and verify you get search results.
   - *Starter hint:* The remap flag is `-p HOST_PORT:CONTAINER_PORT`. The container internally still thinks it is listening on 8080; only the host-side port changes. Your explanation should mention port 8080 and `local-ai`.
   - *You've succeeded when:* The `curl` from inside the container returns JSON search results, and you can articulate why 8081 was chosen instead of 8080.

3. *Add an agent.* Deploy hermes (or agent0 if you prefer a web UI) with its identity directory, give it one small task in the shared workspace, destroy the container, recreate it, and demonstrate that its identity persisted.

   - *What to do:* Run the `hermes` docker command from section 6. Give it a task that causes it to write a file to `/workspace`. Then run `docker rm hermes`, recreate the container with the same command, and show that the file in `$HOME/agents/workspace` still exists.
   - *Starter hint:* After the first run, check `ls $HOME/agents/hermes/home` and `ls $HOME/agents/workspace` on the host before destroying the container. After recreating, check the same paths.
   - *You've succeeded when:* You can show `ls` output from before and after the container recreation demonstrating the files persisted, proving that state lives in the host directory, not in the container.

4. *Break and fix.* Remove the `--add-host` flag from one Linux deployment (or simulate by using `localhost` in a config), capture the exact failure symptom, restore it, and write the three-line postmortem.

   - *What to do:* Edit the Open WebUI connection setting to use `localhost:4000` instead of `host.docker.internal:4000`. Try to send a message. Capture the error. Restore the correct setting.
   - *Starter hint:* The error will appear either in the browser UI or in `docker logs open-webui`. Your three-line postmortem format: (1) What failed and what the error said. (2) Why it failed (the networking reason). (3) What the fix was.
   - *You've succeeded when:* You have a screenshot or log excerpt of the failure and a written postmortem that correctly identifies `localhost`-inside-container as the root cause.

5. *Automate one flow.* In n8n, build a workflow with at least two nodes that calls the gateway on a schedule and writes the result into the workspace. Screenshot the canvas and the output file.

   - *What to do:* In the n8n UI at `http://localhost:5678`, create a workflow with a Schedule trigger node and an HTTP Request node pointed at `http://host.docker.internal:4000/v1/chat/completions`. Add a Write File node to save the response to `/workspace/daily_summary.txt`.
   - *Starter hint:* The HTTP Request node needs method `POST`, the URL above, header `Authorization: Bearer sk-litellm-local`, and a JSON body of `{"model": "qwen2.5-3b", "messages": [{"role": "user", "content": "Give me a one-sentence motivational thought for today."}]}`.
   - *You've succeeded when:* The workflow runs manually at least once, and `cat $HOME/agents/workspace/daily_summary.txt` shows the model's response.

---

## Reflection Prompt

*Personal:* Before this module, what was your mental model of how an AI service like ChatGPT works at an infrastructure level? How has the tier diagram changed that mental model?

*Technical:* In your notebook: this stack gives you, personally, capabilities that required a funded lab five years ago, running on hardware you own, with no data leaving your desk. Which of the course's governance concerns get *easier* under local-first architecture, and which one, honestly, gets harder when there is no provider watching?

*Societal:* The ability to run capable AI agents locally without any data leaving your machine is currently accessible only to people with the technical knowledge and hardware to do it. What are the equity implications of a world where "private AI" is a skill-gated privilege? Who benefits and who does not?

---

## → Coming Up Next

Now that the stack is running, the *Design First: Plan Before You Build* activity follows the studio: before wiring more services together, we learn to plan a multi-agent system on paper. The stack knowledge from today feeds directly into Lab 1 Directions 2–3 (the Compose-stack and container-hardening directions).

---

## 9. Further Reading

- W. Mongan, "Building a Private AI Stack: From Mini PC to Autonomous Agents" (billmongan.com, May 2026): the complete architecture this module deploys, with every Dockerfile and run script.
- The LiteLLM documentation (docs.litellm.ai): the gateway's routing options in depth.
- The n8n documentation (docs.n8n.io): workflow patterns for scheduling agents.
