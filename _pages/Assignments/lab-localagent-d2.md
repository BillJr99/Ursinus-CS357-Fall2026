---
layout: assignment
permalink: /Assignments/LocalAgent/Direction2
title: "CS357 Lab 1 Direction 2: Composing the Local Agent Stack"
---

> **Grading:** This page is one of the directions for [Lab 1: Your First Local Agent](/Assignments/LocalAgent). It carries no separate point value and no rubric of its own — your combined core + direction work is graded with the Lab 1 rubric on the core lab page.

> **What this direction requires**
>
> - **Accounts:** none — the OpenWebUI login you create is stored locally on your own machine.
> - **API costs:** none — the stack uses placeholder API keys and your local Ollama server.
> - **Installs / disk:** Docker Desktop (Mac/Windows) or Docker Engine with Compose v2 (Linux), plus roughly 6 GB of image pulls (`llama3.2` ~2 GB, the open-webui image, and the searxng image). **Pull the images before lab day** — they are large.
> - **Hardware:** 8 GB of RAM or more is recommended to run five services at once.
> - **No-cost fallback:** not needed — fully local and free.

---


Take the local agent you built in the core lab and give it a home: a full five-tier local AI stack — one service from every tier of the course architecture — wired together correctly, verified systematically, and reproducible from a single Docker Compose file. The skill being developed is wiring discipline: knowing which address to use from which location, and documenting your choices so another person can reproduce the result from scratch.

In this lab, you and your partner will stand up a working local AI stack: one service from every tier of the course architecture, wired together correctly, verified systematically, and reproducible from a compose file. This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**. The skill being graded is not typing commands — it is the wiring discipline that makes two dozen services coexist, demonstrated on five.

---

#### Before You Start

Complete both prerequisite activities before lab day. These are not optional warm-ups; the lab builds directly on them.

- [The Local Agent Stack Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md) — introduces each tier of the stack and how they connect
- [Docker from Zero Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-docker.md) — covers containers, images, compose files, volumes, and networks

##### Tools to Install

Run these commands before lab day. The image pulls are large and will consume time you do not have during lab.

```bash
# Verify Docker and Docker Compose are installed
docker --version          # Need 24.0+
docker compose version    # Need 2.x

# Pull the images you'll need (do this before lab day — these are large)
ollama pull llama3.2      # ~2 GB inference model
docker pull ghcr.io/open-webui/open-webui:main    # frontend
docker pull searxng/searxng     # tool service
```

##### Health-Check Commands

Run these after installation to confirm everything is ready.

```bash
$ docker --version
Docker version 24.0.7, build afdd53b

$ ollama list
NAME            ID              SIZE      MODIFIED
llama3.2:latest abc123def456    2.0 GB    2 minutes ago
```

If `ollama list` shows no models, the pull did not complete. Re-run `ollama pull llama3.2` and wait for it to finish.

##### The Key Mental Model

Before writing a single config file, internalize this distinction. It is the source of the majority of failures in this lab.

- **`localhost`** inside a container refers to that container itself — not the host machine, not any other container. A process inside `open-webui` hitting `http://localhost:11434` is trying to reach port 11434 inside the `open-webui` container, where nothing is listening.
- **`host.docker.internal`** inside a container refers to the Docker host machine — the laptop or server running Docker. Use this when a container needs to reach a process running directly on the host (such as Ollama running natively).
- **A service name like `ollama`** inside a container refers to another container on the same Docker network. This only works when both containers are declared in the same compose file and Docker has created a shared network for them.

```
Your Machine (host)
├── Terminal: curl localhost:11434  →  hits Ollama running on host
│
├── Container A (open-webui)
│   ├── curl localhost:3000         →  hits itself (useless)
│   ├── curl host.docker.internal:11434  →  hits Ollama on host
│   └── curl ollama:11434           →  hits Ollama container (if same network)
│
└── Container B (gateway)
    └── curl host.docker.internal:11434  →  hits Ollama on host
```

##### Linux-Specific Note

On Mac and Windows, Docker Desktop automatically makes `host.docker.internal` resolve to the host machine inside every container. **On Linux, this does not happen automatically.** You must add the following stanza to every service in your compose file that needs to reach the host:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

This is safe to include on Mac and Windows too — it is a no-op there. Include it everywhere for portability.

##### Estimated Time

- Part 1 — Plan Before Pulling: ~30 minutes
- Part 2 — The Core Chain: ~60 minutes
- Part 3 — Tool and Agent: ~45 minutes
- Part 4 — Verify, Break, and Declare: ~30 minutes

---

#### Overview

In this lab you will stand up a local AI stack with one service per tier, wired together correctly, verified systematically, and reproducible from a compose file. The five tiers are: an inference backend (the model engine), a unified gateway (a single URL that routes to the backend), a frontend (the user-facing chat interface), a tool service (something the agent can call), and an agent (an autonomous loop that uses the other services). The skill being developed is wiring discipline — understanding which address to use from which location, and documenting your choices so that another person (or your future self) can reproduce the result from scratch.

---

#### Part 1: Plan Before Pulling

**Do not start any container until you have completed every step in this section.** The most common lab failure is a port collision discovered at midnight. The purpose of this part is to prevent it.

##### Step 1: Choose One Service Per Tier

Select one service from each tier. The recommended choices are marked; you may choose alternatives if you understand the trade-offs.

| Tier | Recommended | Alternatives |
|------|-------------|--------------|
| Inference backend | Ollama | LM Studio |
| Gateway | llmproxy | (no alternatives in scope) |
| Frontend | open-webui | (no alternatives in scope) |
| Tool service | SearXNG | SurrealDB |
| Agent | Hermes | Agent0, freebuff |

Write your choices down before moving on. Every subsequent step refers to your five chosen services by name.

##### Step 2: Create the Port Table

Fill in this table before starting any container. Look up each image's default port in its documentation. Resolve every collision by assigning a different host port — you cannot have two services on the same host port.

| Tier | Service | Image | Default Port | Assigned Port | Notes |
|------|---------|-------|-------------|---------------|-------|
| Inference | ollama | ollama/ollama | 11434 | 11434 | No conflict |
| Gateway | llmproxy | (see llmproxy docs) | 4000 | 4000 | |
| Frontend | open-webui | ghcr.io/open-webui/open-webui:main | 8080 | 3000 | Remapped to avoid conflict |
| Tool | searxng | searxng/searxng | 8080 | 8081 | Conflict with frontend — must remap |
| Agent | hermes | (see hermes docs) | TBD | TBD | |

**The "Assigned Port" column is your contract with yourself.** Every config file you write in Parts 2 and 3 must use the assigned ports from this table, not the image defaults.

##### Step 3: Create the Identity Directory Tree

```bash
mkdir -p $HOME/agents/{ollama,llmproxy,open-webui,searxng,hermes}
ls $HOME/agents/
```

> **Expected output:**
> ```
> hermes  llmproxy  ollama  open-webui  searxng
> ```

Each directory will hold bind-mounted data for one service. When a container is destroyed and recreated, its data survives because it lives on the host, not inside the container layer.

##### Step 4: Sketch the Wiring Diagram

Before writing any compose file, draw (or copy and annotate) this wiring diagram. Add the actual port numbers from your table.

```
Agent (hermes)
  └─── via host.docker.internal ───► Gateway (llmproxy :4000)
                                          └──► Inference Backend (ollama :11434)
Frontend (open-webui :3000)
  └─── via host.docker.internal ───► Gateway (llmproxy :4000)
Tool (searxng :8081)
  └─── (agent calls this directly via host.docker.internal)
```

This diagram tells you exactly which `extra_hosts` stanzas you will need. Any arrow that crosses from a container to the host requires `host.docker.internal` and, on Linux, the `extra_hosts` declaration.

##### Troubleshooting — Part 1

**Port 8080 is already in use before you even start.**
Run `docker ps` and `lsof -i :8080` (or `netstat -tulpn | grep 8080` on Linux) to find the occupant. Either stop that process or assign a different port in your table.

**The identity directory already exists with stale data from a previous attempt.**
If you are redoing the lab from scratch, remove the old data first: `rm -rf $HOME/agents && mkdir -p $HOME/agents/{ollama,llmproxy,open-webui,searxng,hermes}`. Do not do this mid-lab without understanding what data you are discarding.

**Confusion about which tier a service belongs to.**
If you are unsure, ask: does the service run the model weights (inference), route API calls (gateway), present a UI (frontend), give the agent external information (tool), or autonomously loop and call other services (agent)? A service belongs to exactly one tier.

##### ✅ Part 1 Checkpoint

Before moving to Part 2, confirm you can answer all three questions:

1. What is the assigned host port for every service in your stack? Where did the default port come from, and why did you choose to keep or change it?
2. Which services in your wiring diagram need `host.docker.internal` in their config? Why?
3. What does the identity directory for `open-webui` store, and what would happen if you deleted it?

---

#### Part 2: The Core Chain

Build the stack one link at a time. **Verify each link before adding the next.** Adding three services simultaneously and then debugging why nothing works is a trap.

##### Step 2a: Stand Up the Inference Backend (Ollama)

Ollama runs directly on the host — not in Docker. This is intentional: GPU access from within a container requires additional configuration, and simplicity is the goal here.

```bash
ollama serve &
# Or, to capture logs:
ollama serve > $HOME/agents/ollama/ollama.log 2>&1 &
```

Verify it is listening from the host terminal:

```bash
curl http://localhost:11434/api/tags
```

> **Expected output:**
> ```json
> {"models":[{"name":"llama3.2:latest","model":"llama3.2:latest","modified_at":"...","size":2019700992,...}]}
> ```

If you see `connection refused`, Ollama is not running. Check whether the background process exited: `jobs` (bash) or check `ollama.log`. If you see an empty models list, the pull did not complete — run `ollama pull llama3.2` again.

Run one inference to confirm the model responds before proceeding:

```bash
curl http://localhost:11434/api/generate \
  -d '{"model":"llama3.2","prompt":"Hello","stream":false}'
```

> **Expected output:**
> ```json
> {"model":"llama3.2","response":"Hello! How can I help you today?","done":true,...}
> ```

Do not proceed to Step 2b until this command returns a response.

##### Step 2b: Stand Up llmproxy as a Compose Service

Create a working directory for your compose project:

```bash
mkdir -p $HOME/stack
cd $HOME/stack
```

Create `llmproxy-config.yaml` in that directory. This file tells llmproxy where to find the inference backend. Use `host.docker.internal` — not `localhost` — because llmproxy will be running inside a container, not on the host.

```yaml
# llmproxy-config.yaml
model_list:
  - model_name: llama3.2
    litellm_params:
      model: ollama/llama3.2
      api_base: http://host.docker.internal:11434
```

Create `docker-compose.yml` with the llmproxy service:

```yaml
services:
  llmproxy:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    volumes:
      - ./llmproxy-config.yaml:/app/config.yaml
    command: ["--config", "/app/config.yaml", "--port", "4000"]
    extra_hosts:
      - "host.docker.internal:host-gateway"   # Required on Linux; harmless on Mac/Windows
    restart: unless-stopped
```

Start just llmproxy:

```bash
docker compose up -d llmproxy
docker compose logs llmproxy
```

Verify from the host terminal:

```bash
curl http://localhost:4000/models
```

> **Expected output:**
> ```json
> {"object":"list","data":[{"id":"llama3.2","object":"model","created":...}]}
> ```

Do not proceed to Step 2c until this returns the model list.

##### Step 2c: Stand Up the Frontend (open-webui)

Add `open-webui` to your `docker-compose.yml`:

```yaml
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - $HOME/agents/open-webui:/app/backend/data
    environment:
      - OPENAI_API_BASE_URL=http://host.docker.internal:4000/v1
      - OPENAI_API_KEY=sk-placeholder
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped
    depends_on:
      - llmproxy
```

Apply the change:

```bash
docker compose up -d open-webui
docker compose logs open-webui
```

Open a browser to `http://localhost:3000`. Create an account when prompted (this is local-only — the credentials are stored in your bind-mounted data directory).

> **What you should see:** The open-webui chat interface loads. Select `llama3.2` from the model dropdown at the top. Type a message and press enter. The response should arrive within a few seconds.

If the model dropdown is empty, open-webui cannot reach llmproxy. Check the `OPENAI_API_BASE_URL` value: it must use `host.docker.internal`, not `localhost`.

Complete a chat message that gets a response. **This is your first end-to-end verification of the core chain.** Do not proceed to Part 3 until a chat completes successfully.

##### Troubleshooting — Part 2

**llmproxy starts but cannot reach Ollama (Linux).**
The log will show something like `Connection refused` or `Failed to connect to host.docker.internal port 11434`. The fix is to add `extra_hosts: ["host.docker.internal:host-gateway"]` to the llmproxy service and run `docker compose up -d --force-recreate llmproxy`.

**open-webui shows "Connection Error" when you send a chat message.**
The `OPENAI_API_BASE_URL` environment variable is wrong. Common mistake: using `http://localhost:4000/v1` instead of `http://host.docker.internal:4000/v1`. Inside the open-webui container, `localhost` refers to the container itself, not the host where llmproxy's port is published.

**`curl http://localhost:4000/models` returns "connection refused" immediately.**
The llmproxy container has not finished starting. Run `docker compose ps` and check the `STATUS` column. If it says `Restarting`, run `docker compose logs llmproxy` to see the startup error.

##### ✅ Part 2 Checkpoint

Before moving to Part 3, confirm you can answer all three questions:

1. You ran `curl http://localhost:11434/api/generate` from the host terminal, and the same URL appears in `llmproxy-config.yaml` — but it will not work there. Why? What URL does the config file use instead?
2. open-webui is published on host port 3000 but listens on container port 8080. Why is this remapping necessary?
3. What does `restart: unless-stopped` mean? When would `always` be a better choice, and when would `no` be better?

---

#### Part 3: Tool and Agent

##### Step 3a: Add the Tool Service (SearXNG or SurrealDB)

Add `searxng` to `docker-compose.yml`:

```yaml
  searxng:
    image: searxng/searxng:latest
    ports:
      - "8081:8080"
    volumes:
      - $HOME/agents/searxng:/etc/searxng
    restart: unless-stopped
```

Note the port remapping: SearXNG's container port is 8080, but host port 8080 is already in use by open-webui's internal mapping. You assigned 8081 in your port table, so use that here.

Start the service:

```bash
docker compose up -d searxng
```

Verify from the host:

```bash
curl "http://localhost:8081/search?q=test&format=json"
```

> **Expected output:** A JSON object with a `results` array.

Now verify from inside another container. This tests the wiring the agent will actually use:

```bash
# Verify searxng from inside the llmproxy container:
docker compose exec llmproxy \
  curl "http://host.docker.internal:8081/search?q=test&format=json"
```

> **Expected output:** The same JSON object as above.

Notice the URL used inside the container: `http://host.docker.internal:8081`, not `http://localhost:8081`. Inside the `llmproxy` container, `localhost` refers to the `llmproxy` container itself. SearXNG is a separate process whose port is published on the host, so you reach it via `host.docker.internal`.

If this command fails with "connection refused" and you are on Linux, verify that `llmproxy` has the `extra_hosts` stanza. If you get "name resolution failure" for `host.docker.internal`, same fix.

##### Step 3b: Add the Agent (Hermes or Equivalent)

Add your agent to `docker-compose.yml`. The critical details are the bind mount for identity persistence and `extra_hosts` for host connectivity:

```yaml
  hermes:
    image: # (use the hermes image from the activity)
    ports:
      - "TBD:TBD"   # Replace with your assigned agent port
    volumes:
      - $HOME/agents/hermes:/app/identity
    environment:
      - OPENAI_API_BASE=http://host.docker.internal:4000/v1
      - OPENAI_API_KEY=sk-placeholder
      - TOOL_SEARCH_URL=http://host.docker.internal:8081
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped
    depends_on:
      - llmproxy
      - searxng
```

Start the agent:

```bash
docker compose up -d hermes
docker compose logs hermes
```

Give the agent a task:

```bash
docker compose exec hermes \
  ask "What recent news is there about Ursinus College? Use the search tool."
```

> **What you should see:** The agent logs show it calling the search tool with a query, receiving results, and composing a response. The final output in your terminal is a paragraph about Ursinus College drawn from search results.

**Demonstrate identity persistence.** This shows that the bind-mounted identity directory survives container destruction.

```bash
# Stop and remove the agent container
docker compose stop hermes
docker compose rm -f hermes

# Recreate it
docker compose up -d hermes

# Verify the identity directory still has data
ls $HOME/agents/hermes/
```

> **Expected output:** The identity files that existed before the container was destroyed are still present. The agent resumes with the same identity rather than starting fresh.

##### Troubleshooting — Part 3

**The agent starts but cannot reach the search tool.**
Check the `TOOL_SEARCH_URL` environment variable. It must use `host.docker.internal`, not `localhost`. Also confirm SearXNG is running: `docker compose ps searxng`.

**The bind mount path is wrong and the container fails to start.**
Docker will create the directory if it does not exist, but it will be empty. If the agent fails because it cannot find its identity files, check that the host path (`$HOME/agents/hermes`) actually exists and contains the expected files.

**The agent restarts in a loop.**
Run `docker compose logs hermes` to see the error before the restart. Common causes: the gateway URL is unreachable at startup (add `depends_on` and a `healthcheck` to llmproxy), or the agent binary is not found in the image (wrong image or wrong command).

##### ✅ Part 3 Checkpoint

Before moving to Part 4, confirm you can answer all three questions:

1. From inside the `hermes` container, what URL does the agent use to reach llmproxy? What URL does it use to reach SearXNG? Why are both `host.docker.internal` and not service names like `llmproxy` or `searxng`?
2. You destroyed and recreated the hermes container but its identity survived. What specific mechanism made this possible?
3. The agent's `depends_on` lists `llmproxy` and `searxng`. What does `depends_on` actually guarantee, and what does it NOT guarantee?

---

#### Part 4: Verify, Break, and Declare

##### Step 4a: Build the Wiring Matrix

The wiring matrix is your systematic proof that the stack works. Fill in every cell with the command you ran and whether it passed or failed.

| Check | Ollama | llmproxy | open-webui | SearXNG | Hermes |
|-------|--------|----------|------------|---------|--------|
| Host liveness (curl from terminal) | | | | | |
| Container-to-host (host.docker.internal) | | | | | |
| End-to-end chat completion | | | | | |

**Host-side liveness checks** — run these from your terminal, not from inside a container:

```bash
# Ollama
curl http://localhost:11434/api/tags

# llmproxy
curl http://localhost:4000/models

# open-webui (expect HTTP 200)
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

# SearXNG
curl "http://localhost:8081/search?q=test&format=json"

# Hermes (replace port with your assigned port)
curl http://localhost:TBD/health
```

**Container-side reachability checks** — run these from inside containers:

```bash
# From llmproxy container, reach Ollama on the host
docker compose exec llmproxy curl http://host.docker.internal:11434/api/tags

# From open-webui container, reach llmproxy on the host
docker compose exec open-webui curl http://host.docker.internal:4000/models

# From hermes container, reach SearXNG on the host
docker compose exec hermes curl "http://host.docker.internal:8081/search?q=test&format=json"
```

**End-to-end chat completion via curl** (bypasses the browser, tests the full chain):

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-placeholder" \
  -d '{
    "model": "llama3.2",
    "messages": [{"role": "user", "content": "Say hello in one sentence."}],
    "stream": false
  }'
```

> **Expected output:** A JSON object with a `choices` array containing the model's response.

##### Step 4b: Break It on Purpose

This step builds diagnostic intuition. You will introduce a known failure, observe the symptom, fix it, and write the postmortem.

**The break:** In `docker-compose.yml`, remove the `extra_hosts` stanza from one service that reaches the host — for example, `llmproxy`. Then restart that service:

```bash
docker compose up -d --force-recreate llmproxy
```

Now repeat the host-side liveness check for llmproxy:

```bash
curl http://localhost:4000/models
```

> **What you should see:** The endpoint times out or returns an error. The llmproxy logs show it cannot reach `host.docker.internal:11434`.

Capture the exact error message from the logs:

```bash
docker compose logs llmproxy 2>&1 | tail -20
```

**The fix:** Restore the `extra_hosts` stanza and recreate the container:

```bash
# Edit docker-compose.yml to restore extra_hosts, then:
docker compose up -d --force-recreate llmproxy
```

Verify recovery:

```bash
curl http://localhost:4000/models
# Expected: model list returns normally
```

Write the postmortem using this template:

```
Postmortem: llmproxy could not reach Ollama on the host
Symptom:  [paste the exact error message or behavior you observed]
Cause:    [the specific misconfiguration — what was missing or wrong]
Fix:      [the exact change that resolved it]
```

If you encountered a **real unplanned failure** during the lab, you may substitute its postmortem. A real failure with an honest postmortem is more valuable than the intentional break.

##### Step 4c: Final Compose File and Down/Up Test

Your complete `docker-compose.yml` for the core stack (gateway, frontend, and tool at minimum — all five services if you have them working) should look like this structure. Fill in your actual image names, ports, and paths:

```yaml
services:
  llmproxy:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    volumes:
      - ./llmproxy-config.yaml:/app/config.yaml
      - $HOME/agents/llmproxy:/app/data
    command: ["--config", "/app/config.yaml", "--port", "4000"]
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - $HOME/agents/open-webui:/app/backend/data
    environment:
      - OPENAI_API_BASE_URL=http://host.docker.internal:4000/v1
      - OPENAI_API_KEY=sk-placeholder
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped
    depends_on:
      - llmproxy

  searxng:
    image: searxng/searxng:latest
    ports:
      - "8081:8080"
    volumes:
      - $HOME/agents/searxng:/etc/searxng
    restart: unless-stopped

  hermes:
    image: # your agent image
    ports:
      - "TBD:TBD"
    volumes:
      - $HOME/agents/hermes:/app/identity
    environment:
      - OPENAI_API_BASE=http://host.docker.internal:4000/v1
      - OPENAI_API_KEY=sk-placeholder
      - TOOL_SEARCH_URL=http://host.docker.internal:8081
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped
    depends_on:
      - llmproxy
      - searxng
```

Run the down/up test to confirm reproducibility:

```bash
docker compose down
docker compose up -d
```

Wait for services to start (about 10–15 seconds), then verify data persistence:

```bash
curl http://localhost:4000/models
# Expected: same model list as before the down
```

Open a browser to `http://localhost:3000` and confirm your chat history is still present.

##### Troubleshooting — Part 4

**`docker compose down` removed your data.**
If you accidentally ran `docker compose down --volumes`, named volumes were deleted. Bind mounts (paths like `$HOME/agents/...`) are unaffected by `--volumes`. If you used named volumes instead of bind mounts and lost data, this is a learning moment: prefer bind mounts for data you want to keep across `down` commands.

**After `up -d`, a container keeps restarting.**
Run `docker compose logs <service>` to see the error. The most common cause after a clean `down/up` is a missing config file that the container expected to find. Check that your volume bind mounts point to files and directories that actually exist on the host.

**Containers start in wrong order and fail because dependencies are not ready.**
`depends_on` ensures start order but not readiness. Add a `healthcheck` to llmproxy so that open-webui waits for it to be actually healthy, not just started:

```yaml
  llmproxy:
    # ... existing config ...
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/models"]
      interval: 10s
      timeout: 5s
      retries: 5

  open-webui:
    # ... existing config ...
    depends_on:
      llmproxy:
        condition: service_healthy
```

##### ✅ Part 4 Checkpoint

Before writing up your deliverables, confirm you can answer all three questions:

1. Your wiring matrix has a row for "container-to-host" checks. What does it mean for this check to pass? What does it prove that the "host liveness" check does not?
2. When you ran `docker compose down` and then `docker compose up -d`, which data survived and which did not? How is that determined by your compose file?
3. The postmortem template has three lines: symptom, cause, fix. Why is the distinction between symptom and cause important? Give an example where the symptom is the same but the cause (and therefore the fix) is different.

---

#### Deliverables

Submit a ZIP file containing the following items. Everything must be present for the submission to be considered complete.

**Port table (filled in)**
The table from Part 1, Step 2 with all five rows complete — assigned ports, image names, and notes on any collisions resolved.

**`docker-compose.yml`**
The compose file that reproduces your running stack. Requirements:
- All services present (gateway, frontend, tool, agent at minimum)
- Image tags pinned (e.g., `:main-latest`, not `:latest` if there is a more specific tag)
- No hardcoded secrets — use `sk-placeholder` or environment variable references
- Bind mounts using `$HOME/agents/...` paths
- `restart` policies explicitly set for every service
- `extra_hosts` stanza on every service that reaches the host

**Configuration files**
Any supporting files required by your compose file (e.g., `llmproxy-config.yaml`). Tokens and API keys redacted.

**`README.md` (approximately one page)**
Written for a classmate who has not done this lab. Must include:
- Prerequisites (what to install and pull before starting)
- Setup steps (numbered, in order)
- How to verify the stack is working
- How to stop the stack cleanly

**Wiring matrix with outputs**
The completed table from Part 4, Step 4a. Every cell must contain the command run and whether it passed or failed. Do not summarize — paste the actual commands and actual outputs (truncated if long).

**Postmortem**
Either the intentional break from Part 4, Step 4b or a real failure encountered during the lab. Must follow the three-line template: symptom, cause, fix.

**Pair log**
A timestamped record of driver/navigator swaps. Minimum three swaps. Format: `HH:MM — [name] takes driver`, alternating.

**Answers to reflection prompts**
See the Reflection Prompts section below.

---

#### Extension Challenges

These are optional and ungraded. Attempt them only after completing all four parts.

**Challenge 1: Health Checks for All Services**

Add a `healthcheck:` block to every service in your compose file so that `docker compose ps` shows `(healthy)` for all of them. For each health check, write one sentence in your README explaining what it tests and why that test is meaningful for that service.

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:<port>/<health-endpoint>"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

**Challenge 2: Monitoring Stack**

Add a sixth service — a monitoring stack using Prometheus and Grafana, or Netdata — that displays CPU and memory usage per container in real time. Create a dashboard showing at least: CPU usage per service, memory usage per service, and one application-level metric (such as llmproxy request count). Document the Grafana URL and how to access the dashboard in your README.

**Challenge 3: Automated Verification Script**

Write a shell script `verify_stack.sh` that automatically runs every check in your wiring matrix and prints `PASS` or `FAIL` for each one. The script must:
- Test host-side liveness for every service
- Test at least one container-to-host connection using `docker compose exec`
- Run the end-to-end chat completion curl and check that the response contains a non-empty `choices` array
- Exit with code `0` if all checks pass, and code `1` if any check fails

```bash
#!/bin/bash
# verify_stack.sh — automated wiring matrix
set -euo pipefail

PASS=0
FAIL=0

check() {
  local name="$1"
  local cmd="$2"
  if eval "$cmd" > /dev/null 2>&1; then
    echo "PASS: $name"
    ((PASS++))
  else
    echo "FAIL: $name"
    ((FAIL++))
  fi
}

check "Ollama liveness"     "curl -sf http://localhost:11434/api/tags"
check "llmproxy liveness"   "curl -sf http://localhost:4000/models"
check "open-webui liveness" "curl -sf http://localhost:3000"
check "SearXNG liveness"    "curl -sf 'http://localhost:8081/search?q=test&format=json'"
# Add container-to-host checks here

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
```

---

#### Reflection Prompts

Answer each prompt in two to five sentences. Shallow answers receive shallow credit.

**Prompt 1**
Which connection in your stack took longest to get right, and what diagnostic step would have found it faster?

**Prompt 2**
Your stack now runs capable agents entirely on hardware you control. Name one governance obligation that this locality satisfies automatically and one it quietly transfers onto you.

**Prompt 3**
If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.

**Prompt 4**
Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

**Prompt 5**
The `host.docker.internal` pattern is a workaround for the fact that containers have their own network namespace. What would a cleaner architectural solution look like — one that did not require this workaround? What trade-offs would it introduce? (Hint: think about what would need to change about where Ollama runs, or how Docker networking is configured.)

**Prompt 6**
You deployed five services in this lab. In a real production AI system, you might have fifty. What would need to be different about how you manage ports, secrets, health checks, and restarts at that scale? Name at least two things that do not scale from this lab's approach and explain specifically why they break down.
