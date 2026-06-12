# The Local Agent Stack: Wiring Containers into a System
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

One container is a demo; a *stack* of containers that talk to each other is infrastructure. This module deploys the course's local AI ecosystem (model servers, a unifying gateway, tool servers, web frontends, and autonomous agents) and teaches the wiring discipline that makes two dozen services coexist: tiered roles, a port plan, per-service identity directories, and `host.docker.internal` as the connective tissue. The arc: **the tier model $\rightarrow$ the inference foundation $\rightarrow$ the gateway $\rightarrow$ frontends and tools $\rightarrow$ agents $\rightarrow$ wiring and verification**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisites: the shell and Docker modules, completed honestly. Hardware note: the full stack runs comfortably on a mini PC or a mid-range laptop because we choose small models; nothing here requires a GPU. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Architecture Before Containers

## 1. The Tier Model

Memorizing two dozen container names is hopeless; memorizing **five tiers** is easy, and every container in our stack slots into one:

| Tier | Job | Our containers |
|------|-----|----------------|
| Inference | Run models, speak an API | `ollama`, `lmstudio`, `local-ai`, `longcat-video` |
| Gateway | One endpoint, many backends | `llmproxy` |
| Tools | Capabilities agents can call | `mcpproxy`, `searxng`, `surrealdb` |
| Frontends | Humans talk to the stack | `open-webui`, `open-terminal`, `open-design`, `open-notebook`, `voicebox`, `presenton`, `calibre-web` |
| Agents | Autonomous and task-bounded workers | `hermes`, `freebuff`, `agent0`, `openhands-server`/`openhands`, `nanoclaw`, `nanoclaw-dind`, `zeroclaw`, `openclaw-gateway`, `n8n` |

Two structural principles govern everything. First, **all inference flows through the gateway**: every frontend and agent sends OpenAI-compatible requests to `llmproxy`, which routes to Ollama, LocalAI, or a cloud free tier per one YAML file, so swapping a model never touches more than that file. Second, **every service gets its own identity directory** under `$HOME/agents/<service>/`, bind-mounted in, so any container can be destroyed and recreated without losing state, and no two services can contaminate each other.

## 2. The Port Plan

Containers collide on ports before they collide on anything else, so the plan comes first. The well-known defaults anchor the table; every other service is assigned a host port in its `run.sh`, and the table (kept in your stack repository) is the single source of truth:

| Service | Host port | Notes |
|---------|-----------|-------|
| `ollama` | 11434 | Native service or container; the workhorse |
| `lmstudio` | 1234 | LM Studio's local server default |
| `local-ai` | 8080 | OpenAI-compatible GGUF inference |
| `llmproxy` | 4000 | The gateway; everything points here |
| `open-webui` | 3000 | Browser chat frontend |
| `searxng` | 8081 | Private metasearch (default 8080 remapped to avoid local-ai) |
| `n8n` | 5678 | Workflow automation |
| `surrealdb` | 8000 | Multi-model database |
| `calibre-web` | 8083 | E-book library |
| `agent0` | 8082 | Autonomous agent web UI |
| remaining services | assigned | One row each in your stack's port table, no exceptions |

Notice the `searxng` row: its image default (8080) collides with `local-ai`, so we remap on the host side, which is the entire point of `-p HOST:CONTAINER`. **The rule: before any `docker run`, the service gets a row.** Port conflicts then become impossible by construction rather than debugged at midnight.

---

## Model 1: Place the Pieces

### Critical Thinking Questions

1. A teammate proposes having `open-webui` talk directly to `ollama` "to skip a hop." What does the stack lose? (Name two concrete things the gateway tier buys, using the one-YAML-file argument.)
2. `nanoclaw-dind` runs Docker *inside* Docker so its agent can spawn sandboxed sub-containers. Which tier does it belong to, and what governance property is the inner Docker layer providing? Connect to the irreversible-actions taxonomy from class.
3. Assign host ports to three unassigned services from the table, checking your choices against every existing row. State the collision you avoided.

---

# Part II: Standing Up the Core

## 3. Inference: Ollama First

Ollama is the foundation; everything else can be added incrementally once it answers:

```bash
# Native install (preferred: keeps model I/O off the Docker path)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:3b && ollama pull llama3 && ollama pull hermes3:8b
curl http://localhost:11434/api/tags        # verify: lists your models
```

`lmstudio` and `local-ai` are alternates with the same OpenAI-compatible surface (LM Studio adds a friendly GUI for model management on port 1234; LocalAI adds whisper transcription and image generation behind 8080); the gateway makes the choice invisible to everything downstream, so start with Ollama and add the others when a need appears.

## 4. The Gateway: llmproxy

The gateway (a LiteLLM-style router) is one Compose service plus one routing file:

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

```bash
docker compose up -d
curl -s http://localhost:4000/models -H "Authorization: Bearer sk-litellm-local"
```

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

The same attach-by-URL move adds the rest of the frontend tier as you need each one (`open-notebook` for research notebooks, `voicebox` for speech, `presenton` for slide generation, `open-terminal` for a browser shell, `open-design` for the agent-embedded canvas, `calibre-web` for your reading library): each gets a port row, an identity directory, the `--add-host` flag, and its connection settings pointed at the gateway. Tool-tier services follow suit: `searxng` gives your agents private web search, `mcpproxy` hosts MCP tools from YAML definitions, and `surrealdb` provides persistence; agents reach them at `http://host.docker.internal:<port>` exactly as they reach the gateway.

[[MC]]
Inside the llmproxy container, the routing config points at http://host.docker.internal:11434 rather than http://localhost:11434 because:
- ( ) Port 11434 is reserved for host.docker.internal
- (x) Inside a container, localhost means the container itself, so reaching the host-resident Ollama requires the special host alias (with --add-host or extra_hosts on Linux)
- ( ) The gateway requires HTTPS
- ( ) localhost works but is slower

---

## 6. The Agent Tier

Agents are where the stack earns its name, and they come in personalities. `hermes` is a named agent identity built around the Hermes 3 model family's unusually reliable tool calling; our deployment probes the image first, then runs interactively with an identity mount:

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

A stack is not up until its connections are proven, pairwise, from the right vantage points. Build the matrix:

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

When a cell of the matrix fails, the Docker module's diagnostic ladder applies: host-side first, container-side second, then the `--add-host` flag, the port row, and the logs, in that order.

---

# Part III: Practice

## 8. Exercises

1. *Minimal viable stack.* Deploy Ollama, llmproxy, and Open WebUI; complete a chat in the browser that round-trips through all three; submit your port table and the end-to-end curl output.
2. *Add a tool.* Deploy searxng on its remapped port and confirm from inside another container that `http://host.docker.internal:8081` answers a search query. Explain in two sentences why the remap was necessary.
3. *Add an agent.* Deploy hermes (or agent0 if you prefer a web UI) with its identity directory, give it one small task in the shared workspace, destroy the container, recreate it, and demonstrate that its identity persisted.
4. *Break and fix.* Remove the `--add-host` flag from one Linux deployment (or simulate by using `localhost` in a config), capture the exact failure symptom, restore it, and write the three-line postmortem.
5. *Automate one flow.* In n8n, build a workflow with at least two nodes that calls the gateway on a schedule and writes the result into the workspace. Screenshot the canvas and the output file.

---

## Reflection Prompt

In your notebook: this stack gives you, personally, capabilities that required a funded lab five years ago, running on hardware you own, with no data leaving your desk. Which of the course's governance concerns get *easier* under local-first architecture, and which one, honestly, gets harder when there is no provider watching?

---

## 9. Further Reading

- W. Mongan, "Building a Private AI Stack: From Mini PC to Autonomous Agents" (billmongan.com, May 2026): the complete architecture this module deploys, with every Dockerfile and run script.
- The LiteLLM documentation (docs.litellm.ai): the gateway's routing options in depth.
- The n8n documentation (docs.n8n.io): workflow patterns for scheduling agents.
