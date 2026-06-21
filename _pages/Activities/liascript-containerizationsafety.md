# Containerizing AI Systems: Safety, Isolation, and Trust Boundaries
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-containerizationsafety.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-containerizationsafety.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Containerizing AI Systems: Safety, Isolation, and Trust Boundaries

We have run agents in plain Python scripts. That is fine for learning but dangerous in production: a misbehaving agent, a compromised tool, or a successful prompt injection attack can affect the entire host machine. **Containers** are the engineering answer. Today we study what containers actually isolate, what they do not, and the specific safety patterns that matter when the process inside the container is an LLM agent that can generate and execute arbitrary code.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss as a team. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports disagreements or alternative interpretations. After class, respond to the reflective prompt individually in your notebook.

| Role | Responsibility |
|------|---------------|
| Manager | Keeps the team on pace; calls time on each question |
| Recorder | Writes the team's consensus answers and posts to the board |
| Presenter | Speaks for the team during whole-class debrief |
| Reflector | Notes where the team was uncertain or disagreed; reports to whole class |

---

## Model 1: What Docker Actually Isolates

Docker does not virtualize hardware. It uses two Linux kernel features:

- **Namespaces** partition kernel resources so that processes in a container see only their own slice. The six relevant namespaces for security are:

| Namespace | Isolates | Practical Effect |
|-----------|----------|-----------------|
| `pid` | Process IDs | Agent cannot see or signal host processes |
| `net` | Network interfaces, routes | Container gets its own virtual NIC |
| `mnt` | Filesystem mount points | Container has its own root filesystem |
| `uts` | Hostname and domain | Container can have a different hostname |
| `ipc` | Shared memory segments | Prevents cross-container shared-memory attacks |
| `user` | UID/GID mappings | UID 0 inside container maps to non-root outside |

- **cgroups** (control groups) enforce resource *quotas*: maximum CPU shares, memory bytes, open file descriptors, and I/O bandwidth. Without cgroup limits, a single agent can exhaust host memory and take down every other container on the machine.

### Critical Thinking Questions

1. A container uses `--network none`. Which namespace enforces this restriction? What legitimate agent capability does this break, and when is that an acceptable tradeoff?

2. Linux capabilities are fine-grained permissions below root. `CAP_NET_BIND_SERVICE` lets a process bind to ports below 1024; `CAP_SYS_PTRACE` lets a process attach a debugger to another process. Why should an AI coding agent container drop `CAP_SYS_PTRACE`? What attack does dropping it prevent?

3. Without a cgroup memory limit, an agent enters an infinite tool-call loop generating large JSON responses. Describe the failure mode on a multi-tenant server, and write the `docker run` flag that prevents it.

---

## Model 2: Threat Model for an AI Agent Container

A **threat model** lists what can go wrong, how, and what the defense is. For a coding agent (one that can write and execute code), the threat surface is larger than for a typical web service because the agent's *output* is executable.

| Threat | Attack Vector | Container Defense | What Still Leaks Through |
|--------|---------------|-------------------|--------------------------|
| **Prompt injection → shell exec** | Malicious text in retrieved document causes agent to call `subprocess.run(malicious_cmd)` | `--read-only` filesystem; drop `CAP_SYS_ADMIN` | Agent can still exec within its own writable `/tmp` tmpfs |
| **Data exfiltration via HTTP** | Agent crafts an outbound HTTP request encoding stolen data in query string | `--network none` or egress firewall rules | None if network truly disabled |
| **Resource exhaustion** | Agent loops infinitely; each iteration calls an LLM API, accumulating cost and tokens | `--memory 2g --cpus 1.5`; outer iteration limit | Cost at the LLM API level (billed before container killed) |
| **Secret theft from env vars** | Prompt injection causes agent to `print(os.environ)` | Docker secrets (mounted as files, not env vars); rotate tokens | If agent has read access to `/run/secrets`, it can still read them |
| **Container escape** | Exploit in container runtime (rare but real) | Never `--privileged`; keep Docker daemon patched | Zero-days in kernel namespaces |

### Critical Thinking Questions

4. The threat table shows that `--network none` blocks data exfiltration via HTTP, but the agent still needs to call an external LLM API. How do you give the agent access to exactly one external endpoint while blocking all others? (Hint: consider a sidecar proxy or egress firewall rules.)

5. Docker secrets mount credentials as files under `/run/secrets/`. An agent that can run `cat /run/secrets/github_token` still reads the secret. What does Docker secrets buy you compared to `--env GITHUB_TOKEN=abc123`? (Hint: think about `docker inspect` and process environment visibility.)

6. The table says container escape via `--privileged` is the most severe threat. Look up what `--privileged` actually does: it disables all namespace isolation and grants all capabilities. Give a concrete scenario where an agent + `--privileged` leads to full host compromise.

---

## Model 3: Docker Run — From Unsafe to Hardened

Below are four `docker run` configurations ranging from dangerous to production-grade. Study each and its rationale.

| Configuration | Key Flags | Safety Level | Appropriate Use Case |
|---------------|-----------|--------------|---------------------|
| **Dangerous** | `docker run --privileged -v /:/host image` | None — container is the host | Never appropriate for agents |
| **Default** | `docker run -v /workspace:/workspace image` | Minimal — filesystem and cgroup defaults only | Local development, trusted code only |
| **Hardened** | `docker run --read-only --tmpfs /tmp --cap-drop ALL --cap-add NET_BIND_SERVICE --user nobody --memory 2g --cpus 1 image` | High | Agent in production, needs network but not root |
| **Air-gapped** | Above flags `--network none` + Docker secrets for creds + `--log-driver json-file --log-opt max-size=10m` | Maximum | Coding agent processing untrusted user input |

The `--read-only` flag makes the container's root filesystem immutable. Any write attempt raises a permissions error. The `--tmpfs /tmp` flag carves out a RAM-backed writable directory specifically at `/tmp`; this is where the agent writes scratch files, and it vanishes when the container exits (no persistent artifact).

Running as `--user nobody` means the agent process has UID 65534. Even if it escapes the container, it arrives on the host as `nobody` — still dangerous, but not root.

### Critical Thinking Questions

7. The hardened configuration includes `--cap-drop ALL --cap-add NET_BIND_SERVICE`. Why is it better to drop all capabilities and add back only what is needed rather than leaving the default capability set?

8. A coding agent generates a Python file, writes it to `/tmp/solution.py`, and executes it with `python /tmp/solution.py`. The container is `--read-only` with `--tmpfs /tmp`. Does this workflow succeed or fail? Explain which flag does what in this scenario.

9. The air-gapped configuration uses `--log-driver json-file --log-opt max-size=10m` to cap log size. Why is log size a security concern specifically for LLM agents (as opposed to typical web services)?

---

## Model 4: Safety Patterns Inside the Agent Loop

Containerization is the outer shell. Inside it, the agent code itself needs safety rails. The two most common failure modes for LLM agents are **unbounded loops** and **unchecked execution**.

```python
MAX_ITERATIONS = 25
MAX_TOOL_CALLS = 50
tool_call_count = 0

for iteration in range(MAX_ITERATIONS):
    action = agent.decide(context)           # LLM inference

    # Safety gate 1: irreversible actions require human confirmation
    if action.is_irreversible():
        confirmed = human_checkpoint(action)
        if not confirmed:
            return AgentResult(status="halted", reason="user declined")

    # Safety gate 2: validate output before execution
    if action.type == "code_execution":
        if not sandbox_validates(action.code):
            context.add("Rejected: code failed static analysis")
            continue

    # Safety gate 3: tool call budget
    tool_call_count += 1
    if tool_call_count > MAX_TOOL_CALLS:
        return AgentResult(status="budget_exceeded")

    result = sandbox.execute(action, timeout=30)  # hard timeout per action

    if result.failed():
        context.add(f"Action failed: {result.error}")   # reflect, do not retry blindly
```

Never pass LLM-generated strings directly to `eval()`, `exec()`, or `subprocess.run(shell=True)`. Even with a sandboxed container, these calls can consume resources, corrupt the agent's own working state, or exploit vulnerabilities in the Python interpreter.

### Critical Thinking Questions

10. The code above calls `human_checkpoint(action)` only for irreversible actions. Give two examples of actions an agent might classify as reversible that are actually difficult or impossible to undo in practice.

11. The `sandbox.execute(action, timeout=30)` call has a 30-second hard timeout. A file download of a large dataset legitimately takes 90 seconds. How should the agent loop handle legitimate long-running actions without removing the timeout entirely?

---

## Multiple Choice Checkpoint

[[MC]]
A development team deploys a code-generation agent with `docker run --privileged -v /:/host`. A red team finds a prompt injection vulnerability. What is the worst-case outcome compared to a hardened deployment?
- ( ) The agent generates incorrect code, which is the same in both cases
- ( ) The attacker can read files in /tmp, which the hardened deployment also allows
- (x) The attacker gains read/write access to the entire host filesystem and can escalate to full host compromise
- ( ) The privileged flag only affects network access, so the impact is limited

---

## Exercises

**Exercise A — Dockerfile Hardening:** The following Dockerfile runs an agent as root with no resource limits. Rewrite it to use a non-root user, a read-only filesystem with a `/tmp` tmpfs, and to drop all capabilities.

```dockerfile
FROM python:3.12
COPY agent.py /app/agent.py
CMD ["python", "/app/agent.py"]
```

**Exercise B — Threat Table Extension:** Add two new rows to the threat model table in Model 2: (1) an agent that calls `os.fork()` to spawn background processes, and (2) an agent that writes files faster than the tmpfs limit.

**Exercise C — Budget Arithmetic:** An agent runs on a machine with 16 GB RAM. You set `--memory 2g` and allow up to 6 concurrent agent containers. An LLM inference library loads a 1.5 GB model into each container's memory. How much RAM is available for actual agent work per container, and what is the total RAM committed across all six containers? Is this configuration safe given the host's 16 GB?

---

## Reflection Prompt

*(Respond individually in your course notebook after class.)*

Containerization reduces *blast radius* but does not eliminate risk. An agent that is fully contained can still call an external API in ways that cause harm (sending spam, deleting cloud resources, making purchases). In two paragraphs: (1) describe a harm that containerization cannot prevent, and (2) propose a design-level control (not a container flag) that would reduce that harm.

---

## Further Reading

- [Docker Security Documentation](https://docs.docker.com/engine/security/)
- [NIST SP 800-190: Application Container Security Guide](https://csrc.nist.gov/publications/detail/sp/800-190/final)
- [Linux Capabilities Man Page](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [OWASP LLM Top 10: LLM02 — Insecure Output Handling](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Anthropic: Responsible Scaling Policy](https://www.anthropic.com/news/anthropics-responsible-scaling-policy)
