#!/usr/bin/env bash
#
# CS357 — Launch the hardened "YOLO mode" agent container.
#
# The flags here are the whole point: they turn a normal container into a
# defensible trust boundary so you can run a coding agent with its own
# permission prompts disabled and still sleep at night. Each flag maps to a
# threat in liascript-containerizationsafety.md. Read that activity first.
#
# Usage:
#   ./run.sh                 # mounts ./workspace, no network
#   NET=1 ./run.sh           # allow network (needed for hosted-model agents)
#   ./run.sh claude          # run a specific agent at startup instead of a shell
#
# This script never passes your API keys on the command line. Put them in
# ./agent.env (which is .gitignored) and they are injected as env vars only.
set -euo pipefail

IMAGE="${IMAGE:-cs357/agent-yolo:latest}"
HOST_WORKSPACE="${HOST_WORKSPACE:-$PWD/workspace}"
ENV_FILE="${ENV_FILE:-$PWD/agent.env}"

mkdir -p "$HOST_WORKSPACE"

# --- Hardening flags -------------------------------------------------------
ARGS=(
  --rm -it
  --name cs357-agent-yolo

  # Mount ONLY the scratch workspace, read-write. Nothing else from the host
  # is visible: the agent cannot read ~/.ssh, ~/.aws, or your real project.
  -v "$HOST_WORKSPACE:/workspace"
  -w /workspace

  # Disposability: the container's own root filesystem is read-only, with a
  # small writable tmpfs. The agent can scribble in /workspace and /tmp only.
  --read-only
  --tmpfs /tmp:rw,size=512m
  --tmpfs /home/agent/.cache:rw,size=256m

  # No privilege escalation: setuid binaries cannot gain new powers.
  --security-opt no-new-privileges:true

  # Drop ALL Linux capabilities; the agent does not need any root powers.
  --cap-drop ALL

  # Resource quotas (cgroups): an agent stuck in a tool-call loop cannot
  # exhaust host RAM/CPU and take down everything else on the machine.
  --memory 4g
  --memory-swap 4g
  --cpus 2
  --pids-limit 512

  # Locale/timezone parity with the image.
  -e TZ=America/New_York
  -e LANG=en_US.UTF-8
)

# --- Network policy --------------------------------------------------------
# Default to AIR-GAPPED. A coding agent that only edits local files needs no
# network; a hosted-model agent (Claude Code, Codex) does. Opt in explicitly.
if [[ "${NET:-0}" == "1" ]]; then
  echo "WARNING: network ENABLED. Prompt-injected exfiltration is now possible." >&2
  # When online, also reach a local Ollama on the host for private models.
  ARGS+=( -e OLLAMA_HOST="http://host.docker.internal:11434"
          --add-host=host.docker.internal:host-gateway )
else
  ARGS+=( --network none )
fi

# --- Secrets ---------------------------------------------------------------
# API keys come from a gitignored env file, never from the image or argv.
if [[ -f "$ENV_FILE" ]]; then
  ARGS+=( --env-file "$ENV_FILE" )
else
  echo "INFO: no $ENV_FILE found; running without API keys (local/offline only)." >&2
fi

# --- Optional agent context ------------------------------------------------
# If a teammate profile exists, mount it read-only so the agent reads its
# charter / how-I-work / resume at startup. See files/agent-teammate-profile/.
PROFILE_DIR="${PROFILE_DIR:-$PWD/files/agent-teammate-profile}"
if [[ -d "$PROFILE_DIR" ]]; then
  ARGS+=( -v "$PROFILE_DIR:/workspace/.profile:ro" )
fi

exec docker run "${ARGS[@]}" "$IMAGE" "${@:-bash -l}"
