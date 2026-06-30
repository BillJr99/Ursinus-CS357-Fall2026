# CS357 — Hardened "YOLO mode" container for AI coding agents
#
# Purpose: give an autonomous coding agent (Claude Code, Codex, opencode, pi,
# codewhale) a disposable, isolated home so that running it WITHOUT per-action
# permission prompts ("yolo mode") cannot damage your host. The container is the
# trust boundary; see liascript-containerizationsafety.md and liascript-yolomode.md.
#
# Build:  docker build -t cs357/agent-yolo:latest files/agent-yolo-container
# Run:    ./files/agent-yolo-container/run.sh   (applies the hardening flags)
#
# This image is intentionally pinned to a specific Ubuntu release for
# reproducibility. Update the digest deliberately, not by accident.
FROM ubuntu:24.04

# Build args let us create a non-root user whose UID/GID match the host caller,
# so files written into the mounted /workspace are owned by you, not by root.
ARG AGENT_USER=agent
ARG AGENT_UID=1000
ARG AGENT_GID=1000

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=America/New_York \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# --- System packages -------------------------------------------------------
# Mirrors the toolchain from the course's container-isolation use case: build
# tools, Python, Node, plus bubblewrap for a second, in-container sandbox layer.
RUN apt-get update && \
    apt-get install -y --no-install-recommends locales && \
    sed -i 's/^# *en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 && \
    apt-get install -y --no-install-recommends \
      git curl wget unzip zip tar bzip2 xz-utils \
      build-essential cmake ninja-build pkg-config \
      python3 python3-pip python3-venv \
      nodejs npm \
      bubblewrap \
      ca-certificates ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# --- AI coding agents ------------------------------------------------------
# Installed globally so any of them can be launched inside the sandbox. Pin
# versions in a real deployment; @latest is used here for classroom currency.
# --ignore-scripts on pi avoids running untrusted postinstall code at build time.
RUN npm install -g @openai/codex && \
    npm install -g --ignore-scripts @earendil-works/pi-coding-agent && \
    npm install -g opencode-ai && \
    npm install -g @anthropic-ai/claude-code@latest && \
    npm install -g codewhale && \
    npm cache clean --force

# --- Non-root user ---------------------------------------------------------
# Never run the agent as root inside the container. If a "root-in-container"
# escape is found, mapping to a non-root host UID limits the blast radius.
RUN groupadd -g ${AGENT_GID} ${AGENT_USER} 2>/dev/null || true && \
    useradd -m -u ${AGENT_UID} -g ${AGENT_GID} -s /bin/bash ${AGENT_USER} && \
    mkdir -p /workspace && chown -R ${AGENT_UID}:${AGENT_GID} /workspace

USER ${AGENT_USER}
WORKDIR /workspace

# Agents read their identity/context from these files if you mount them in:
#   CHARTER.md, HOW-I-WORK.md, RESUME.md  (see files/agent-teammate-profile/)
# and their per-tool context files (AGENTS.md, CLAUDE.md, opencode.json).
CMD ["bash", "-l"]
