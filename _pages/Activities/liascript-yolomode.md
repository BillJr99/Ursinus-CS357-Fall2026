# Running Agents in YOLO Mode Safely
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-yolomode.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-yolomode.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Running Agents in YOLO Mode Safely

Every agentic CLI offers a tempting flag: a way to stop asking you to approve each action so the agent can just *go*. Claude Code calls it `--dangerously-skip-permissions`; opencode has `--dangerously-skip-permissions` too; the community calls the whole idea **"yolo mode."** Used carelessly it is exactly as dangerous as the flag name warns. Used correctly — *inside a disposable, isolated container, behind a charter* — it is how you get the productivity of autonomy without betting your laptop on it. This supplemental tutorial connects three things you have already met (permission gates, containers, and the agent teammate profile) into one safe pattern: **the container is the boundary, the charter is the intent, and skipping prompts is only acceptable once both are in place.** The arc: **what yolo mode actually turns off $\rightarrow$ why a prompt is not a security boundary $\rightarrow$ the container as the real boundary $\rightarrow$ a safe-yolo checklist you can run.**

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisites: *Agentic CLI Tools* (`liascript-agentclis.md`), *Docker from Zero* (`liascript-docker.md`), and *Containerizing AI Systems* (`liascript-containerizationsafety.md`). After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Permission gate** | A prompt the agent shows before a risky action, waiting for human approval | "Allow `rm -rf build/`? (y/N)" |
| **Yolo mode** | Running an agent with permission gates disabled so it acts without asking | `claude --dangerously-skip-permissions` |
| **Trust boundary** | The line past which an attacker's or agent's actions are contained | The container wall: damage stays inside, host stays safe |
| **Blast radius** | How much can be harmed if something goes wrong | With only `/workspace` mounted, the blast radius is the scratch directory |
| **Disposability** | The property that the environment can be thrown away and recreated cleanly | `--rm` + read-only root filesystem; nothing the agent does persists to the image |
| **Defense in depth** | Layering independent protections so one failure is not catastrophic | Charter (words) + container (walls) + no network (no exit) |

---

## Model 1: What Yolo Mode Actually Turns Off

A permission gate is a pause: "I am about to run this command / edit this file / call this network host — approve?" Turning the gate off does not make the agent *more* capable; it makes it *unsupervised*. Everything the agent could do with your approval, it can now do without it — including the things it would have done wrong, and the things a prompt injection tells it to do.

| With gates on | With gates off (yolo) |
|---|---|
| You see and approve each shell command | The agent runs commands immediately |
| A destructive `rm` pauses for confirmation | A destructive `rm` just happens |
| A network call to a new host asks first | The agent reaches any host it wants |
| A prompt injection's "run this" is caught at the prompt | The injection's command executes silently |

The key realization: **yolo mode removes the human, so the human's judgment must be pre-loaded elsewhere.** Part of it goes into the charter (intent and guardrails). But intent in words is not enough, which is Model 2.

### Critical Thinking Questions

1. Skipping permissions makes an agent faster on a long, multi-step task. Name one concrete task where that speedup is worth it, and one where you would absolutely keep gates on even though it is slower. What distinguishes them?

2. A teammate says, "I run everything with `--dangerously-skip-permissions` on my normal laptop because I trust the model." Identify the two unstated assumptions in that sentence and explain why each is unsafe.

---

## Model 2: A Prompt Is Not a Security Boundary

Your charter can say, in capital letters, "NEVER exfiltrate secrets." That is a real and useful instruction — and it can still be defeated, because the same channel that carries your instructions (text in the context window) also carries the attacker's (text in a file the agent reads). A sufficiently clever **prompt injection** competes with your charter for the model's attention, and sometimes wins. Treating the prompt as your only protection is like writing "please do not steal" on an unlocked door.

So we separate two jobs:

- **The charter expresses intent.** It tells a *cooperative* agent what you want and what is off-limits. It improves behavior in the common case.
- **The container enforces limits.** It makes certain actions *impossible* regardless of what any text says. It protects you in the worst case.

This is **defense in depth**: words *and* walls. Yolo mode is safe only when the walls are real, because in yolo mode the words are the only thing standing between a prompt injection and your machine — unless the walls make the dangerous action impossible.

### Critical Thinking Questions

3. For each guardrail, name the container setting that turns the *forbidden* into the *impossible*:
   a. "NEVER read files outside the project."
   b. "NEVER call external network services."
   c. "NEVER consume all the machine's memory."
   d. "NEVER modify system files."

   *Hint: the answers are bind-mount scope, `--network none`, `--memory`, and `--read-only`.*

4. Why can't a container make "NEVER `git push` to the wrong branch" impossible the way it can make "NEVER read `~/.ssh`" impossible? What *other* mechanism (outside the container) would you use to enforce the branch rule?

---

## Model 3: The Container Is the Boundary

The course's hardened image (`files/agent-yolo-container/`) and its `run.sh` launcher exist precisely so that "yolo" means "yolo *inside a box*." Here is the mapping from each hardening flag to the worst-case it defuses — the same flags you harden by hand in the containerization lab:

| `run.sh` setting | Turns this guardrail from "forbidden" into "impossible" |
|---|---|
| only `-v ./workspace:/workspace` mounted | reading `~/.ssh`, `~/.aws`, your real repos |
| `--network none` (default) | exfiltration, command-and-control callbacks |
| `--read-only` + small `--tmpfs` | persistent tampering; the box resets clean |
| `--cap-drop ALL`, `--security-opt no-new-privileges` | privilege escalation inside the box |
| `--memory`, `--cpus`, `--pids-limit` | a runaway loop DoS-ing the host |
| `--env-file` (gitignored) for keys | secrets in the image or in `argv` |

Notice what is **still not** protected: anything you choose to mount into `/workspace` is fair game, the host kernel is shared (a kernel exploit escapes), and a malicious base image is trusted by definition. Containers reduce blast radius dramatically; they do not make risk zero. (Full residual-risk treatment: `liascript-containerizationsafety.md`.)

```bash
# The safe-yolo pattern, end to end:
docker build -t cs357/agent-yolo:latest files/agent-yolo-container
cd files/agent-yolo-container && ./run.sh          # air-gapped, ./workspace only
# ...then INSIDE the container:
claude --dangerously-skip-permissions               # yolo — but inside the box
```

### Critical Thinking Questions

5. The default `run.sh` uses `--network none`, but a research agent needs the web and a hosted-model agent needs to reach its API. `NET=1 ./run.sh` enables networking and prints a warning. Once the network is on, which Model 3 protection is gone, and what *narrower* network policy (rather than all-or-nothing) would you propose for a research agent? (Connect to OAuth scopes and allow-lists from the governance discussion.)

6. "Disposability" is listed as a safety property. Explain how `--rm` plus a read-only root filesystem changes your *recovery* story after a bad agent run, compared to running the same agent directly on your laptop.

---

## Part: Run the Safe-Yolo Checklist

Before you ever add `--dangerously-skip-permissions` to a command, your team walks this checklist against a task of your choice. The agent may run in yolo mode only if **every** box is checked.

1. **Charter present?** The agent reads a `CHARTER.md` with explicit out-of-bounds guardrails.
2. **Isolation?** It runs in the container, not on the host.
3. **Mount scope?** Only the scratch `/workspace` is mounted; no home directory, no real repo, no SSH/cloud creds.
4. **Network?** Off, unless the task truly needs it — and if on, scoped/allow-listed, with the risk acknowledged.
5. **Resource limits?** Memory, CPU, and PID limits set.
6. **Secrets?** None in the image or `argv`; injected via gitignored env file only, and only the keys this task needs.
7. **Reversibility?** Work is on a disposable branch/workspace; nothing irreversible or outward-facing is reachable without a human.

If any box is unchecked, keep the permission gates **on**. The flag is a reward for having built the box, not a shortcut around building it.

---

## Reflective Prompt

In your notebook (3–5 sentences): Describe a time you (or someone you have seen) ran a tool with a "skip all confirmations" option and what could have gone wrong. Re-tell it as if the tool had been an autonomous agent in yolo mode — first on a bare laptop, then inside the hardened container. What specifically changes about the worst-case outcome between those two settings, and which single checklist item would have mattered most?
