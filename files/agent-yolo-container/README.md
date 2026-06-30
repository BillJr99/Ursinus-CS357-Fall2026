# CS357 Hardened "YOLO mode" Agent Container

A disposable, isolated home for autonomous AI coding agents so that running them
**without per-action permission prompts** ("yolo mode", e.g. Claude Code's
`--dangerously-skip-permissions`) cannot harm your host. **The container is the
safety boundary** — read the activity *Running Agents in YOLO Mode Safely*
(`liascript-yolomode.md`) and *Containerizing AI Systems*
(`liascript-containerizationsafety.md`) before you use this.

## What's inside

`ubuntu:24.04` + build tools, Python, Node, bubblewrap, and five coding agents
(`@anthropic-ai/claude-code`, `@openai/codex`, `opencode-ai`,
`@earendil-works/pi-coding-agent`, `codewhale`).

## Quick start

```bash
# 1. Build (UID/GID default to 1000; override to match your host user)
docker build -t cs357/agent-yolo:latest files/agent-yolo-container

# 2. (Optional) put API keys in a gitignored env file
echo 'ANTHROPIC_API_KEY=sk-...' > files/agent-yolo-container/agent.env

# 3. Launch — mounts ./workspace, air-gapped by default
cd files/agent-yolo-container && ./run.sh

# 4. Inside the container, run an agent in yolo mode against /workspace ONLY
claude --dangerously-skip-permissions
```

Allow network access (required for hosted models) with `NET=1 ./run.sh` — note
the printed warning: with the network on, a prompt-injected agent can exfiltrate
anything it can read, which is exactly why only `/workspace` is mounted.

## The hardening, and what each flag defends against

| Flag | Threat it addresses |
|------|---------------------|
| `-v ./workspace:/workspace` (and nothing else) | Agent cannot read `~/.ssh`, `~/.aws`, or your real projects |
| `--read-only` + small `--tmpfs` | Disposability; agent cannot persist tampering to the image |
| `--network none` (default) | Blocks data exfiltration and C2 callbacks |
| `--security-opt no-new-privileges` | Blocks setuid privilege escalation |
| `--cap-drop ALL` | Removes every root capability the agent doesn't need |
| `--memory` / `--cpus` / `--pids-limit` | Stops a runaway tool-call loop from DoS-ing the host |
| `--env-file` for secrets | Keys never bake into the image or appear in `argv` |

## What this does NOT protect against

Containers share the host kernel. A kernel-level escape, a malicious base image,
or secrets you mount into `/workspace` are still at risk. See the residual-risk
table in `liascript-containerizationsafety.md`.
