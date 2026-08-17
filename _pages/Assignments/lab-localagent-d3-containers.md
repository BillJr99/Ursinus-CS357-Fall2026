---
layout: assignment
permalink: /Assignments/LocalAgent/Direction3
title: "CS357 Local Agent Lab Direction 3: Containerizing an AI System Safely"
---

> **Grading:** This page is one of the directions for the [Local Agent Lab](/Assignments/LocalAgent). It carries no separate point value and no rubric of its own — your combined core + direction work is graded with the Local Agent Lab rubric on the core lab page.

> **What this direction requires**
>
> - **Accounts:** an Anthropic account with an API key — the agent script in this direction calls the hosted API.
> - **API costs:** small but nonzero; the agent makes short summarization calls, so expect a few cents to a few dollars of usage at this lab's scale (budget under $5).
> - **Installs / disk:** Docker Desktop (Mac/Windows) or Docker Engine with Compose (Linux), the `anthropic` Python package, and the `trivy` image scanner; budget roughly 6 GB of free disk for images and build layers.
> - **Hardware:** run Part 1's deliberately insecure baseline in a dedicated test VM or on a machine with no sensitive files — this is a stated requirement of the direction, not a suggestion.
> - **No-cost fallback:** none is written into this direction's steps, but the hardening work itself is model-agnostic. If obtaining an API key is a barrier, talk to me: re-pointing the agent script at your local Ollama server (swapping the SDK call for the local `/api/chat` endpoint you used in the core lab) preserves every security step and earns full credit.

---


Take the local agent you built in the core lab and put it in a box. You begin with a deliberately insecure AI agent container, document exactly what it can do in that state, and then harden it step by step until it operates under the principle of least privilege — building an explicit trust boundary between the agent and your host system. The goal is not to memorize Docker flags but to understand why each boundary exists and what specific threat it addresses.

In this lab, you and your partner will take a deliberately insecure AI agent container, document exactly what it can do in that state, and then harden it step by step until it operates under the principle of least privilege. The goal is not to memorize Docker flags — it is to understand *why* each boundary exists and what specific threat it addresses. By the end, you will have a concrete mental model of what a container can and cannot protect you from. This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

---

#### Before You Start

##### Prerequisite Concepts

Before beginning, make sure you have completed (or are ready to reference) both prerequisite activities:

- [Docker from Zero Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-docker.md) — covers images, containers, volumes, and basic compose syntax
- [The Local Agent Stack Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md) — covers building a local LLM-calling agent and running it in Docker

If you are fuzzy on any of the following terms, re-read the relevant activity before continuing: image vs. container, bind mount vs. volume, `docker compose up`, `docker exec`, environment variable injection.

##### Tools to Install

Verify that Docker and Docker Compose are installed and available on your system:

```bash
docker --version
docker compose version
```

> **What you should see:**
> ```
> Docker version 24.0.x, build ...
> Docker Compose version v2.x.x
> ```
>
> If you see `command not found`, install Docker Desktop (Mac/Windows) or Docker Engine (Linux) from [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/). Make sure the Docker daemon is running before continuing — on Linux, run `sudo systemctl start docker`; on Mac/Windows, launch Docker Desktop.

Install the Python Anthropic SDK on your host machine (you will also install it inside the container, but having it on the host helps with local testing):

```bash
pip install anthropic
```

Verify your API key is exported in your shell:

```bash
echo $ANTHROPIC_API_KEY
```

> **What you should see:** A long string beginning with `sk-ant-`. If you see nothing, add `export ANTHROPIC_API_KEY=sk-ant-...` to your shell profile and reload it with `source ~/.bashrc` (or `~/.zshrc`).

##### Estimated Time

| Part | Task | Estimated Time |
|------|------|---------------|
| Part 1 | Baseline (Insecure) Deployment | ~30 minutes |
| Part 2 | Hardening Step by Step | ~60 minutes |
| Part 3 | Threat Modeling | ~45 minutes |
| Part 4 | Compose and Document | ~30 minutes |

> **Important:** Run everything in a dedicated test VM or machine — Part 1 intentionally creates a container with dangerous access to demonstrate the threat. Do not run the insecure baseline on a machine containing sensitive files or credentials you cannot afford to expose.

---

#### Part 1: Baseline (Insecure) Deployment

**Goal:** Deploy a minimal AI agent with no security hardening and document exactly what it can access. This serves as your "before" state. Everything you find here is what the hardening in Part 2 is designed to prevent.

##### Step 1: Create the Project Directory Structure

On your host machine, create a workspace directory for this lab. All files in this lab live here.

```bash
mkdir -p ~/cs357-containerlab/workspace
cd ~/cs357-containerlab
```

Your directory should look like this when you are done with Part 1:

```
cs357-containerlab/
├── agent.py
├── docker-compose-insecure.yml
├── docker-compose.yml          # (created in Part 2)
├── Dockerfile                  # (created in Part 2)
├── workspace/                  # the only directory the agent should legitimately access
│   └── sample.txt
└── secrets/                    # (created in Part 2, step f)
```

Create a sample file for the agent to read:

```bash
echo "This is a sample document about neural networks and gradient descent." > ~/cs357-containerlab/workspace/sample.txt
```

##### Step 2: Create the Agent Script

Create the file `~/cs357-containerlab/agent.py` with the following starter code. The TODOs mark the places you need to fill in — read the comments carefully before running anything.

```python
# agent.py - Minimal LLM agent for containerization lab
# This agent intentionally has no security hardening — that is the point of Part 1.
import os, sys
from anthropic import Anthropic

client = Anthropic()  # Uses ANTHROPIC_API_KEY from environment

def main():
    # TODO: Read a file path from argv[1] and include its content in a prompt.
    # Hint: use sys.argv[1] to get the path, then open() to read it.
    if len(sys.argv) < 2:
        print("Usage: python agent.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # TODO: Read the file contents. Handle FileNotFoundError gracefully.
    try:
        with open(file_path, "r") as f:
            file_contents = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}")
        sys.exit(1)

    # TODO: Ask the model to summarize the file contents.
    # Build a user message that includes the file path and contents,
    # then call client.messages.create() with model="claude-sonnet-4-5"
    # (or the model your instructor specifies), max_tokens=256.
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Please summarize the following file ({file_path}):\n\n"
                    f"{file_contents}"
                ),
            }
        ],
    )

    # TODO: Print the response text.
    print(message.content[0].text)

if __name__ == "__main__":
    main()
```

Fill in each TODO before moving on. When the script runs on your host machine (outside Docker), you should see a one-paragraph summary of `workspace/sample.txt`.

```bash
python agent.py workspace/sample.txt
```

> **What you should see:** A short paragraph summarizing the contents of `sample.txt`. If you see an `AuthenticationError`, your `ANTHROPIC_API_KEY` is not set correctly. If you see a `ModuleNotFoundError`, run `pip install anthropic` again.

##### Step 3: Create the Insecure Compose File

Create the file `~/cs357-containerlab/docker-compose-insecure.yml` with the following content. Read every comment — each one identifies a specific security problem that you will fix in Part 2.

```yaml
# docker-compose-insecure.yml
# WARNING: This configuration is deliberately insecure for baseline documentation only.
# Do NOT use this in production.
services:
  agent:
    image: python:3.11-slim
    volumes:
      - ${HOME}:/hostdata   # INSECURE: Mounts entire home directory — agent can read all your files
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}   # INSECURE: Secret visible in docker inspect
    command: >
      sh -c "pip install anthropic -q &&
             python /hostdata/cs357-containerlab/agent.py
             /hostdata/cs357-containerlab/workspace/sample.txt"
```

##### Step 4: Start the Container and Document What It Can Access

Start the container using the insecure compose file:

```bash
docker compose -f docker-compose-insecure.yml up
```

> **What you should see:** Docker pulls the `python:3.11-slim` image (first run only), installs the `anthropic` package, then prints a summary of `sample.txt`. Copy this output into your lab notes as the baseline.

Now open a second terminal and explore what the container can access while it is running. Because the command finishes quickly, use this one-shot approach to explore:

```bash
docker compose -f docker-compose-insecure.yml run --rm --entrypoint sh agent
```

This drops you into a shell inside the container. Run the following exploration commands and copy the output into your notes:

```bash
# What user are we running as?
id

# What files are visible under /hostdata?
ls /hostdata

# Can we read files outside the intended workspace?
ls /hostdata/.ssh 2>/dev/null && echo "SSH keys visible!" || echo "(no .ssh directory)"

# What environment variables are set?
env | grep -i key
```

> **What you should see:** You are running as `root` (uid=0). You can see your entire home directory. Any SSH keys, `.aws` credentials, or other secrets in your home directory are visible. The `ANTHROPIC_API_KEY` value appears in `env` output.

Type `exit` to leave the shell.

##### Step 5: Demonstrate One Unsafe Action

Still using the insecure compose file, demonstrate one specific unsafe action: reading a file from outside the intended workspace. Run this exact command (it runs a one-shot container, reads a sensitive-looking file, and exits):

```bash
docker compose -f docker-compose-insecure.yml run --rm --entrypoint sh agent \
  -c "cat /hostdata/.bashrc | head -5"
```

> **What you should see:** The first five lines of your `.bashrc` file — a file the agent has no legitimate reason to read. Copy this output into your notes as exhibit A of the baseline threat.

To confirm that secrets are exposed via `docker inspect`, run:

```bash
docker compose -f docker-compose-insecure.yml run --rm --entrypoint sh agent \
  -c "echo secret_visible=\$ANTHROPIC_API_KEY" 
```

> **What you should see:** The actual value of your API key printed to stdout. In a production incident, this is how a compromised container leaks credentials.

##### Troubleshooting for Part 1

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `Cannot connect to the Docker daemon` | Docker daemon is not running | Run `sudo systemctl start docker` (Linux) or launch Docker Desktop (Mac/Windows) |
| `AuthenticationError` from the Anthropic SDK | `ANTHROPIC_API_KEY` not passed into container | Verify `echo $ANTHROPIC_API_KEY` on host returns a value; check the `environment:` block in the compose file |
| `ModuleNotFoundError: No module named 'anthropic'` | `pip install` step failed silently | Add `pip install anthropic` to the compose `command:` and check for network connectivity inside the container |

##### ✅ Part 1 Checkpoint

Answer these questions in your notes before moving to Part 2:

1. What is the effective UID of the process running inside the baseline container, and why is running as that UID a security problem?
2. List three specific files or directories on your host machine that the baseline container can read that it has no legitimate reason to access.
3. How would an attacker who had achieved remote code execution inside this container exfiltrate your `ANTHROPIC_API_KEY`? Describe the exact mechanism.

---

#### Part 2: Hardening Step by Step

**Goal:** Apply six hardening measures one at a time. After each step, verify the change took effect before applying the next one. Do not batch them — the point is to observe each layer independently.

Start by creating a `Dockerfile` alongside your `docker-compose.yml`. Some hardening steps require a custom image.

Create `~/cs357-containerlab/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Step a: Create a non-root user (fill in during Step a below)
# RUN useradd --create-home --shell /bin/bash --uid 1000 agent

# Install dependencies
RUN pip install anthropic --no-cache-dir

# Copy the agent script
COPY agent.py /app/agent.py

WORKDIR /app

# Step a: Switch to non-root user (fill in during Step a below)
# USER agent
```

Create the initial (not yet hardened) `docker-compose.yml`:

```yaml
# docker-compose.yml — start here, harden step by step
services:
  agent:
    build: .
    volumes:
      - ./workspace:/workspace
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    command: python /app/agent.py /workspace/sample.txt
```

Verify the base (pre-hardening) compose file works before adding any hardening:

```bash
docker compose build
docker compose up
```

> **What you should see:** The agent summarizes `sample.txt` exactly as it did in Part 1, but now only the `workspace/` subdirectory is mounted instead of your entire home directory. This is already slightly better, but it is still running as root with no other protections.

---

##### Step a: Add a Non-Root User

**What this protects against:** If the agent process is compromised, running as root gives the attacker full control of the container filesystem and any mounted volumes; a non-root user limits the blast radius.

Edit your `Dockerfile` to uncomment the two lines you added above:

```dockerfile
FROM python:3.11-slim

RUN useradd --create-home --shell /bin/bash --uid 1000 agent

RUN pip install anthropic --no-cache-dir

COPY agent.py /app/agent.py

WORKDIR /app

USER agent
```

Rebuild and verify:

```bash
docker compose build
docker compose run --rm --entrypoint id agent
```

> **What you should see:**
> ```
> uid=1000(agent) gid=1000(agent) groups=1000(agent)
> ```
> If you still see `uid=0(root)`, the `USER` directive is not being applied. Check that `docker compose build` ran successfully and that you are using the compose file that references `build: .`.

Also verify the agent still functions after this change:

```bash
docker compose up
```

> **What you should see:** The same summary output as before. The change should be transparent to the agent's behavior.

---

##### Step b: Read-Only Filesystem with tmpfs at /tmp

**What this protects against:** If the agent is tricked into writing a malicious file (for example, a modified script or a backdoor), a read-only filesystem ensures the write fails immediately rather than silently succeeding.

Edit `docker-compose.yml` to add `read_only: true` and a `tmpfs` entry:

```yaml
services:
  agent:
    build: .
    volumes:
      - ./workspace:/workspace:ro   # also make the workspace mount read-only
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    command: python /app/agent.py /workspace/sample.txt
    read_only: true
    tmpfs:
      - /tmp:size=64m,mode=1777
```

Rebuild (no Dockerfile change) and verify that writes are rejected:

```bash
docker compose run --rm --entrypoint sh agent \
  -c "echo test > /app/evil.py && echo 'wrote file' || echo 'write blocked'"
```

> **What you should see:**
> ```
> write blocked
> ```
> If you see `wrote file`, the `read_only: true` setting is not in effect. Double-check the indentation in your compose file — YAML is sensitive to indentation.

Verify that the agent can still write to `/tmp` (some Python internals need this):

```bash
docker compose run --rm --entrypoint sh agent \
  -c "echo test > /tmp/ok.txt && echo 'tmp write succeeded'"
```

> **What you should see:**
> ```
> tmp write succeeded
> ```

Verify the agent still functions:

```bash
docker compose up
```

---

##### Step c: Drop All Capabilities, Add Back Only What Is Needed

**What this protects against:** Linux capabilities grant fine-grained privileges beyond normal user permissions; dropping all of them prevents the agent from performing privileged operations (binding low ports, modifying network interfaces, loading kernel modules) even if it runs as root.

Edit `docker-compose.yml` to add capability controls:

```yaml
services:
  agent:
    build: .
    volumes:
      - ./workspace:/workspace:ro
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    command: python /app/agent.py /workspace/sample.txt
    read_only: true
    tmpfs:
      - /tmp:size=64m,mode=1777
    cap_drop:
      - ALL
    # cap_add:          # uncomment and add capabilities only if the agent stops working
    #   - NET_BIND_SERVICE
```

Verify capabilities are dropped:

```bash
docker compose run --rm --entrypoint sh agent \
  -c "cat /proc/self/status | grep CapEff"
```

> **What you should see:**
> ```
> CapEff: 0000000000000000
> ```
> All zeros means no effective capabilities. If the value is nonzero, `cap_drop: ALL` is not being applied.

Verify the agent still functions:

```bash
docker compose up
```

> **What you should see:** The agent runs normally. A simple Python script that calls an external API does not need any Linux capabilities. If it fails, check the error message — if it is a capability-related error (`EPERM`), identify the specific capability needed and add only that one to `cap_add:`.

---

##### Step d: Restrict Network Access

**What this protects against:** Without network restrictions, a compromised agent can make outbound connections to any host on the internet, enabling data exfiltration or communication with an attacker's command-and-control server.

First, create a named network that only the agent can use, and disable the default bridge:

```yaml
services:
  agent:
    build: .
    volumes:
      - ./workspace:/workspace:ro
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    command: python /app/agent.py /workspace/sample.txt
    read_only: true
    tmpfs:
      - /tmp:size=64m,mode=1777
    cap_drop:
      - ALL
    networks:
      - agent-net

networks:
  agent-net:
    driver: bridge
```

> **Note:** The agent needs to reach `api.anthropic.com` to call the API. A named network still allows outbound internet access by default; full network egress filtering requires a firewall rule or an egress proxy outside of compose. What this step does accomplish is removing the agent from the `default` bridge network, which prevents it from reaching other containers that are also on the default bridge. In Part 3, the extension challenge asks you to go further.

Verify the agent is on the named network and not on the default bridge:

```bash
docker compose up -d
docker inspect $(docker compose ps -q agent) | grep -A 5 '"Networks"'
docker compose down
```

> **What you should see:** The output should show `agent-net` as the network and should NOT show `default` as a network. The gateway and subnet will reflect the named network's configuration.

Verify the agent still functions:

```bash
docker compose up
```

---

##### Step e: Add Resource Limits

**What this protects against:** An AI agent that enters an infinite loop, receives a prompt designed to cause runaway token generation, or is exploited to launch a fork bomb can consume unlimited CPU, memory, and process slots, bringing down the host or other containers.

Edit `docker-compose.yml` to add resource limits using the `deploy` key:

```yaml
services:
  agent:
    build: .
    volumes:
      - ./workspace:/workspace:ro
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    command: python /app/agent.py /workspace/sample.txt
    read_only: true
    tmpfs:
      - /tmp:size=64m,mode=1777
    cap_drop:
      - ALL
    networks:
      - agent-net
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M
    pids_limit: 64

networks:
  agent-net:
    driver: bridge
```

> **Note:** `deploy.resources.limits` works with `docker compose up` when using Docker Compose v2. The `pids_limit` key limits the total number of processes/threads the container can spawn, which blocks fork bombs.

Verify the limits are applied:

```bash
docker compose up -d
docker inspect $(docker compose ps -q agent) | grep -E '"Memory"|"NanoCpus"|"PidsLimit"'
docker compose down
```

> **What you should see:**
> ```json
> "Memory": 268435456,
> "NanoCpus": 500000000,
> "PidsLimit": 64,
> ```
> `268435456` bytes = 256 MB. `500000000` NanoCPUs = 0.5 CPUs. If you see `0` for any of these, the limit is not applied — check that you are using Docker Compose v2 (`docker compose version`).

Verify the agent still functions:

```bash
docker compose up
```

---

##### Step f: Move Secrets to Docker Secrets

**What this protects against:** Environment variables are visible to every process in the container and to anyone who can run `docker inspect`. Docker secrets deliver the value through a file at `/run/secrets/`, which is harder to accidentally log or expose.

Create a secrets directory and write the key to a file:

```bash
mkdir -p ~/cs357-containerlab/secrets
echo -n "$ANTHROPIC_API_KEY" > ~/cs357-containerlab/secrets/anthropic_api_key
chmod 600 ~/cs357-containerlab/secrets/anthropic_api_key
```

Update `agent.py` to read the key from the secrets file if it exists, falling back to the environment variable:

```python
# agent.py - updated to read from Docker secrets
import os, sys
from anthropic import Anthropic

def get_api_key():
    secret_path = "/run/secrets/anthropic_api_key"
    if os.path.exists(secret_path):
        with open(secret_path) as f:
            return f.read().strip()
    return os.environ.get("ANTHROPIC_API_KEY")

client = Anthropic(api_key=get_api_key())

def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as f:
            file_contents = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}")
        sys.exit(1)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Please summarize the following file ({file_path}):\n\n"
                    f"{file_contents}"
                ),
            }
        ],
    )

    print(message.content[0].text)

if __name__ == "__main__":
    main()
```

Now update `docker-compose.yml` to use Docker secrets and remove the `ANTHROPIC_API_KEY` environment variable:

```yaml
services:
  agent:
    build: .
    volumes:
      - ./workspace:/workspace:ro
    command: python /app/agent.py /workspace/sample.txt
    read_only: true
    tmpfs:
      - /tmp:size=64m,mode=1777
    cap_drop:
      - ALL
    networks:
      - agent-net
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M
    pids_limit: 64
    secrets:
      - anthropic_api_key

networks:
  agent-net:
    driver: bridge

secrets:
  anthropic_api_key:
    file: ./secrets/anthropic_api_key
```

Rebuild (the `agent.py` changed) and verify:

```bash
docker compose build
docker compose up -d
docker inspect $(docker compose ps -q agent) | grep -i "ANTHROPIC"
docker compose down
```

> **What you should see:** No `ANTHROPIC_API_KEY` value appears in the `docker inspect` output. The environment variable block should be empty or absent. If you still see the key, verify you removed the `environment:` block from the compose file.

Verify the agent still functions:

```bash
docker compose up
```

> **What you should see:** The agent still produces its summary, now reading the API key from `/run/secrets/anthropic_api_key` instead of an environment variable.

##### Cumulative Hardened docker-compose.yml

After all six steps, your complete hardened `docker-compose.yml` should look exactly like this:

```yaml
# docker-compose.yml — fully hardened
# All six security measures applied: non-root user (Dockerfile), read-only filesystem,
# dropped capabilities, named network, resource limits, and Docker secrets.
services:
  agent:
    build: .
    volumes:
      - ./workspace:/workspace:ro
    command: python /app/agent.py /workspace/sample.txt
    read_only: true
    tmpfs:
      - /tmp:size=64m,mode=1777
    cap_drop:
      - ALL
    networks:
      - agent-net
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M
    pids_limit: 64
    secrets:
      - anthropic_api_key

networks:
  agent-net:
    driver: bridge

secrets:
  anthropic_api_key:
    file: ./secrets/anthropic_api_key
```

And your complete hardened `Dockerfile`:

```dockerfile
FROM python:3.11-slim

RUN useradd --create-home --shell /bin/bash --uid 1000 agent

RUN pip install anthropic --no-cache-dir

COPY agent.py /app/agent.py

WORKDIR /app

USER agent
```

##### Troubleshooting for Part 2

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Container crashes after adding `read_only: true` | Python or a library tries to write to a location other than `/tmp` | Check `docker compose logs` for the error path; add a `tmpfs` entry for that path, or set the `TMPDIR` env var to `/tmp` |
| `connection refused` or API timeout after adding the named network | DNS resolution failing inside the named network | Add `dns: [8.8.8.8]` under the `agent:` service, or verify the host has outbound internet access |
| `secret not found` or `FileNotFoundError: /run/secrets/anthropic_api_key` | The secrets file path is wrong or the file is empty | Run `ls -la secrets/` on the host; verify the file exists and is not empty (`wc -c secrets/anthropic_api_key` should print a nonzero number) |

##### ✅ Part 2 Checkpoint

Answer these questions in your notes before moving to Part 3:

1. After Step b, you made the workspace mount read-only (`:ro`). What is the difference between the container filesystem being read-only (`read_only: true`) and the volume mount being read-only (`:ro`)? Could you have one without the other?
2. After Step c, all capabilities are dropped. Your agent calls an external HTTPS API. Why does it not need `NET_BIND_SERVICE` or any network capability to make outbound connections?
3. After Step f, run `docker inspect $(docker compose ps -q agent)` and look at the `Env` section. What do you see, and how does this compare to the baseline in Part 1?

---

#### Part 3: Threat Modeling

**Goal:** Formalize what you observed into a structured threat model, then stress-test the hardening with a red team exercise.

##### Step 1: Fill In the Threat Model Table

Copy this table into your lab notes document and fill in every cell. Do not leave any cell blank. The `Residual Risk` column should be honest — every defense has limits.

| # | Threat | Specific Attack Vector | Defense Applied (Part 2 Step) | Residual Risk After Hardening |
|---|--------|----------------------|-------------------------------|-------------------------------|
| 1 | Prompt injection leading to unauthorized file access | | | |
| 2 | Data exfiltration via outbound network calls | | | |
| 3 | Resource exhaustion (CPU/memory/fork bomb) | | | |
| 4 | Secret theft via environment variable inspection | | | |

**Guidance for each row:**

- **Row 1 (Prompt injection / file access):** The attack vector should describe a specific prompt a user or attacker could send to the agent that would cause it to read a file it was not supposed to. The defense should reference the read-only mount and non-root user. The residual risk should acknowledge that the agent CAN read any file in `/workspace` — so what happens if sensitive files end up there?

- **Row 2 (Data exfiltration):** The attack vector should describe how a compromised agent could transmit data to an attacker's server. The defense should reference the named network. The residual risk should be honest: does the named network actually block outbound internet access to arbitrary hosts, or just isolate the container from other containers?

- **Row 3 (Resource exhaustion):** The attack vector should describe a specific prompt or exploit that causes runaway resource use (for example, a recursive prompt that generates an infinite loop in code the agent writes and executes). The defense should reference `cpus:`, `memory:`, and `pids_limit`. The residual risk should note what happens when the limit is hit — does the container crash? Does it affect the host?

- **Row 4 (Secret theft):** The attack vector should describe how environment variables are visible (via `docker inspect`, via `/proc/self/environ` inside the container, via container logs). The defense should reference Step f. The residual risk should note that the secret is now a file at `/run/secrets/` — who can read that file inside the container?

##### Step 2: Red Team Exercise

Attempt to make your hardened container take each of the following unsafe actions. For each attempt, record exactly what command you ran and exactly what output or error you received. These records are part of your deliverables.

**Attempt 1: Write to the read-only filesystem**

```bash
docker compose run --rm --entrypoint sh agent \
  -c "echo malicious > /app/backdoor.py && echo 'write succeeded' || echo 'write blocked'"
```

> **What you should see:**
> ```
> sh: /app/backdoor.py: Read-only file system
> write blocked
> ```
> If you see `write succeeded`, the read-only setting is not in effect. Revisit Step b.

**Attempt 2: Connect to an unauthorized host**

```bash
docker compose run --rm --entrypoint sh agent \
  -c "curl -s --max-time 5 http://example.com && echo 'connection succeeded' || echo 'connection failed'"
```

> **What you should see:**
> ```
> connection failed
> ```
> or a curl timeout error. Note: if your named network still allows outbound internet access (which the default Docker bridge driver does), you may see `connection succeeded` here. Record what you actually see and explain it in your threat model's residual risk for Row 2. This is an important finding — the named network alone does NOT block outbound internet access; it only prevents cross-container communication on the default bridge.

**Attempt 3: Read a file outside the workspace**

```bash
docker compose run --rm --entrypoint sh agent \
  -c "cat /etc/shadow && echo 'read succeeded' || echo 'read blocked'"
```

> **What you should see:**
> ```
> cat: /etc/shadow: Permission denied
> read blocked
> ```
> The non-root user (uid=1000) cannot read `/etc/shadow`, which is owned by root. Record the exact error.

After all three attempts, write a one-paragraph summary in your notes: what did the hardening successfully prevent, and what did it not prevent? Which finding surprised you most?

##### Troubleshooting for Part 3

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Red team attempt 1 succeeds (write is not blocked) | `read_only: true` is missing or misindented in compose file | Run `docker inspect` and look for `"ReadonlyRootfs": true`; if you see `false`, fix the compose file and rebuild |
| Red team attempt 2 succeeds (outbound connection works) | Named networks do not block outbound internet by default | This is expected behavior — document it as residual risk in your threat model; the extension challenge covers egress filtering |
| Red team attempt 3 succeeds (can read /etc/shadow) | Container is still running as root | Check `docker compose run --rm --entrypoint id agent` — if it shows `uid=0`, the Dockerfile `USER` directive is not in effect; rebuild with `docker compose build --no-cache` |

##### ✅ Part 3 Checkpoint

Answer these questions in your notes before moving to Part 4:

1. In Attempt 2, you may have found that outbound internet connections still work from the hardened container. What additional control (outside of Docker Compose's built-in features) would you need to add to actually block the agent from reaching unauthorized hosts?
2. The threat model table asks for "residual risk." For Threat 4 (secret theft), is the secret completely safe now that it is in `/run/secrets/`? What would an attacker need to do inside the container to read it?
3. Suppose you wanted to add a fifth row to the threat model covering "supply chain attack via a malicious dependency in the agent's requirements." What would the attack vector, defense, and residual risk look like? (You do not need to implement a defense — just reason through it.)

---

#### Part 4: Compose and Document

**Goal:** Confirm the complete hardened configuration is correct, write the security runbook, and verify the stack can be torn down and restored cleanly.

##### Step 1: Final docker-compose.yml Check

Before writing any documentation, verify all six hardening measures are present in your final `docker-compose.yml`. Use this checklist:

| # | Hardening Measure | How to Verify It Is Present |
|---|------------------|-----------------------------|
| a | Non-root user | `docker compose run --rm --entrypoint id agent` shows `uid=1000` |
| b | Read-only filesystem + tmpfs | `docker inspect ... \| grep ReadonlyRootfs` shows `true` |
| c | Capabilities dropped | `docker compose run --rm --entrypoint sh agent -c "cat /proc/self/status \| grep CapEff"` shows `0000000000000000` |
| d | Named network, no default bridge | `docker inspect ... \| grep -A5 Networks` shows only `agent-net` |
| e | Resource limits | `docker inspect ... \| grep -E 'Memory\|NanoCpus\|PidsLimit'` shows nonzero values |
| f | Docker secrets (no env var) | `docker inspect ... \| grep ANTHROPIC` returns nothing |

Run each verification command and record the output. Do not proceed to Step 2 until all six pass.

##### Step 2: Write the Security Runbook

Create a file `~/cs357-containerlab/RUNBOOK.md`. Use this template and fill in every section marked `[TODO]`:

```markdown
# Security Runbook — CS357 Containerized AI Agent

## Procedure 1: Updating a Docker Secret Without Restarting the Full Stack

**When to use this procedure:** [TODO: describe the scenario — e.g., routine key rotation]

**Steps:**
1. [TODO: describe how to write the new secret value to the secrets file on the host]
2. [TODO: describe the Docker command to force the container to pick up the new secret — hint: secrets are bind-mounted, so the file change is visible immediately; but does the running process re-read the file?]
3. [TODO: describe how to verify the new secret is in use]

**Gotcha:** [TODO: note whether a running process that cached the key at startup will automatically see the new value, or whether a container restart is required]

## Procedure 2: Rotating Credentials When a Secret Is Suspected Compromised

**When to use this procedure:** [TODO: describe the trigger — e.g., key appears in logs, container was compromised]

**Steps:**
1. [TODO: immediately revoke the old key at the provider (Anthropic console)]
2. [TODO: generate a new key]
3. [TODO: update the secrets file and restart the container]
4. [TODO: audit logs to determine what the key was used for between the suspected compromise and the revocation]

**Verification:** [TODO: how do you confirm the old key no longer works?]

## Procedure 3: Auditing Container Logs to Detect Anomalous Agent Behavior

**When to use this procedure:** [TODO: describe when you would proactively audit vs. react to an alert]

**Steps:**
1. View recent logs: `docker compose logs --since 1h agent`
2. [TODO: describe what "normal" log output looks like for this agent]
3. [TODO: describe at least two specific log patterns that would indicate anomalous behavior — e.g., repeated failed file opens outside /workspace, unusually large API responses]
4. [TODO: describe how you would export logs for long-term retention]

**Escalation:** [TODO: if you detect a confirmed incident, what is the first action?]
```

##### Step 3: Test Stack Teardown and Restore

Verify that `docker compose down` cleanly removes the stack and `docker compose up -d` restores it:

```bash
docker compose down
docker compose up -d
docker compose logs agent
docker compose down
```

> **What you should see:** `docker compose down` removes the container and network. `docker compose up -d` recreates them. `docker compose logs agent` shows the agent ran and produced a summary. The final `docker compose down` removes everything cleanly. Record the full output.

##### ✅ Part 4 Checkpoint

Answer these questions in your notes before writing your reflection:

1. In Step 1, did all six verification commands pass on the first attempt? If not, which ones failed and what did you have to fix?
2. In the runbook, you noted whether a running process automatically sees an updated Docker secrets file. What is the answer, and why does it matter for operational security?
3. Suppose you wanted to add automated log monitoring (for example, an alert when the agent makes more than 10 API calls in a minute). Where in the current architecture would you add that monitoring, and would adding it require any changes to the compose file?

---

#### Deliverables

Submit a ZIP file named `cs357-containerlab-[yournames].zip` containing all of the following. Missing items will result in point deductions as indicated in the rubric.

| File | Description |
|------|-------------|
| `docker-compose-insecure.yml` | Baseline insecure compose file from Part 1, with inline comments identifying each security problem |
| `docker-compose.yml` | Fully hardened compose file with all six measures applied |
| `Dockerfile` | Hardened Dockerfile used by the compose file |
| `agent.py` | Final agent script (reads secrets from `/run/secrets/`, not environment) |
| `baseline-notes.md` | Documentation of what the insecure agent could access (Part 1 Steps 4-5 output) |
| `hardening-log.md` | Verification output for each of the six hardening steps, in order |
| `threat-model.md` | Completed threat model table (all four rows, all four columns) |
| `red-team-notes.md` | Red team exercise results: what you tried, what happened, and what it means |
| `RUNBOOK.md` | Security runbook covering all three procedures |
| `pair-log.md` | Role-swap log with driver/navigator names and timestamps (at least every 30 minutes) |

---

#### Extension Challenges

These challenges are optional but highly recommended for students who want to push further. They are not graded as part of the main rubric, but completing them demonstrates mastery.

##### Challenge 1: Enforce Strict Egress Filtering Between Containers

Add a second container to your compose file — a lightweight web server (use `nginx:alpine`) that serves a static file. Reconfigure the agent so it can reach the nginx container by hostname but cannot reach any other host (including `api.anthropic.com`). This requires adding an egress firewall rule or a proxy container.

Hints:
- Look into `iptables` rules applied at container startup, or consider running a forward proxy (such as `squid`) as a third container that the agent routes all traffic through.
- The agent's `networks:` should only include the internal network where nginx lives.
- Verify by running `curl http://nginx-container/` (should succeed) and `curl http://example.com/` (should fail) from inside the agent container.

Document the full compose file and explain how the egress restriction works.

##### Challenge 2: Scan the Agent Image for CVEs

Use `trivy` (or `docker scout`, or `snyk`) to scan the `python:3.11-slim`-based image for known vulnerabilities.

```bash
# Install trivy (Linux)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan your built image
trivy image cs357-containerlab-agent
```

Document all HIGH and CRITICAL severity findings. For each finding, answer: is this CVE reachable given the agent's behavior? What would you do to remediate it (update the base image, remove the affected package, accept the risk)?

##### Challenge 3: CI Check with GitHub Actions

Write a GitHub Actions workflow file at `.github/workflows/container-security.yml` that:

1. Checks out the repository
2. Builds the hardened Docker image with `docker compose build`
3. Runs `docker compose up --abort-on-container-exit` with a test input file to verify the agent completes without error
4. Runs `trivy image` on the built image and fails the workflow if any CRITICAL CVEs are found

The workflow should trigger on every push to `main` and every pull request. Include the workflow file in your deliverables ZIP and attach a screenshot of a passing workflow run.

---

#### Reflection Prompts

Answer each prompt in complete sentences. Answers that reference specific observations from this lab (file names, command outputs, step letters) will receive full credit. Generic answers will not.

- Which hardening step had the most surprising effect on the agent's behavior, and why?
- The container boundary is not a complete security guarantee. Name one class of attack that your hardening does not prevent, and describe what additional control would be needed.
- How does the principle of least privilege apply differently to an AI agent than to a traditional web server?
- After completing this lab, how would you advise a team that wants to give an AI coding agent write access to their production codebase? What specific container-level controls would you require, and which threats would those controls not address?
- The six hardening steps you applied are independent layers. If an attacker could bypass exactly one layer, which would they target first, and why?
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
