<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-docker.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-docker.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Docker from Zero: Containers for Agent Builders

Our entire local AI stack (the model servers, the gateways, the agent frameworks, the web frontends) runs in **Docker containers**, and so will the agents you build.  This tutorial assumes you have never touched Docker and ends with you writing Dockerfiles and composing multi-service stacks.  We move today from **images versus containers -> run, exec, logs, stop -> ports -> volumes -> writing a Dockerfile -> docker compose -> talking to the host**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Hands-on rules from the shell module apply: everyone types everything.  Install Docker before class (Docker Desktop on macOS and Windows; Docker Engine on Linux) and verify with `docker run hello-world`.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

Before diving in, anchor these terms.  You will see every one of them today; look back here whenever something feels unfamiliar.

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Image** | A frozen, read-only snapshot of a filesystem and a default startup command, like a template you never edit directly. | `ghcr.io/open-webui/open-webui:main` is the image you pull to run the chat interface. |
| **Container** | A live, running instance created from an image, like a copy of the template that can accumulate state while it runs. | Each time you run `docker run ubuntu bash` you get a new container from the same Ubuntu image. |
| **Registry** | A remote library that stores and serves images, the way GitHub stores and serves code repositories. | Docker Hub (`hub.docker.com`) and GitHub Container Registry (`ghcr.io`) are the two registries used in this course. |
| **Tag** | A version label appended after `:` in an image name that identifies a specific build of that image. | In `ollama/ollama:latest`, the tag `latest` means "the most recent published version." |
| **Volume / Bind Mount** | A link between a folder on your real machine and a path inside the container, so data written inside the container is actually saved on your disk. | `-v "$HOME/agents/data:/app/data"` makes the container write its data to your home directory instead of into its own temporary layer. |
| **Port Mapping** | A rule that forwards traffic from a port on your machine to a port inside the container, making the containerized service reachable from your browser. | `-p 3000:8080` means "my browser visits port 3000; Docker delivers that traffic to port 8080 inside the container." |

---

### Before You Start

**What you need:** Docker Desktop (or Docker Engine on Linux) and a terminal.  No prior container experience assumed.

**What you will have at the end:** images and containers you built yourself, a Compose stack, and a fenced sandbox for running a coding agent.

Please go through the sections in order, and run each code block as you hit it.  Reading past them will cost you later.

---

# Part I: The Mental Model

In this Part, you will build the conceptual model that makes every Docker command make sense: the distinction between an image (the frozen template) and a container (the live, running copy).  Once this distinction is clear, you will be able to predict what happens to data when containers start, stop, and restart.

> Think of Docker containers as self-contained apartments: everything the tenant needs (furniture, utilities, appliances) is already inside.  Nothing leaks into the neighbor's unit, and if you want a second identical apartment you can clone the whole floor plan instantly.  Model 1 explores what that "self-contained" property means when you want to leave a note on the kitchen table.

## 1.  Images and Containers

An image is a frozen, shippable snapshot of a filesystem plus a default command; a container is a running instance of an image.  The relationship is exactly class to object: one image, many containers, each with its own running state.  Images come from **registries** (Docker Hub by default; GitHub Container Registry, written `ghcr.io`, increasingly often), named like `ollama/ollama:latest`, where the part after `:` is the **tag** (a version label).

**Why containers for AI work?**  Three reasons that will recur all semester.  *Reproducibility*: the container carries its exact dependencies, so "works on my machine" becomes "works in this image" (and your evaluation harnesses demand that).  *Isolation*: an agent running in a container can only see what you mount into it, which is our data-minimization principle enforced by architecture rather than by hope.  *Disposability*: experiments can be destroyed completely with one command, leaving no residue on your host.

## 2.  The Core Verbs

The table below pairs every key command with a plain-English translation and a flag explanation.  Read it once top-to-bottom, then use it as a reference during the exercises.

| Command | What It Does | Key Flags Explained |
|---|---|---|
| `docker run hello-world` | Downloads the `hello-world` image (if not cached) and runs it, printing a confirmation message. | No flags needed; this is the simplest possible run. |
| `docker run -it ubuntu bash` | Starts a fresh Ubuntu container and drops you into an interactive Bash shell inside it. | `-i` keeps stdin open so you can type; `-t` allocates a terminal so output is formatted correctly. Always use them together as `-it`. |
| `docker run -d --name web nginx` | Starts an Nginx web server container in the background and names it `web` so you can reference it easily. | `-d` means "detached": the container runs in the background and your terminal is returned immediately. `--name web` gives the container a memorable handle instead of a random ID. |
| `docker ps` | Lists every container that is currently running, showing its ID, image, name, and uptime. | No flags; shows only running containers. |
| `docker ps -a` | Lists all containers, including ones that have exited or crashed. | `-a` stands for "all." |
| `docker logs web` | Prints everything the `web` container has written to standard output since it started. | Replace `web` with any container name or ID. |
| `docker logs -f web` | Streams the container's output live, exactly like `tail -f` on a log file. Press Ctrl-C to stop. | `-f` stands for "follow." |
| `docker exec -it web bash` | Opens a new Bash shell inside the already-running `web` container. | Same `-it` flags as `docker run -it`. The crucial difference from `run` is that `exec` enters an *existing* container; it does not create a new one. |
| `docker stop web` | Sends a graceful shutdown signal (SIGTERM) to the container and waits up to 10 seconds before forcing it off. | Graceful means running processes get a chance to finish cleanly. |
| `docker rm web` | Deletes the stopped container record. The image is untouched. | You must stop a container before removing it, or add `-f` to force. |
| `docker rmi nginx` | Deletes the `nginx` image from your local disk. | You must remove all containers using the image first. |
| `docker run --rm -it ubuntu bash` | Runs an interactive Ubuntu shell and automatically deletes the container the moment you exit. | `--rm` is perfect for throwaway experiments; no cleanup required. |

The pair worth internalizing is **run versus exec**: `run` creates a *new* container from an image; `exec` enters an *existing, running* one.  Confusing them produces the classic beginner mystery of "I installed it but it is gone," because each `run` starts from the frozen image again; your changes from the previous run are not carried over.

---

## Model 1: The Disappearing File

> Remember the apartment analogy: each time you call `docker run` you are moving into a **brand-new, empty apartment** cloned from the master floor plan, not returning to the one you previously lived in.  Any notes you left in the old apartment stay there, in that stopped container, untouched but unreachable until you go back to it explicitly.

A teammate runs `docker run -it ubuntu bash`, creates `/notes.txt` inside, exits, runs the same command again, and the file is gone.

### Critical Thinking Questions

1.  Explain the disappearance using the image/container distinction.  Where does (did) `/notes.txt` actually live?

   *Hint:* Think about which layer holds new files written during a container's lifetime.  The image itself is read-only, so where does the writable layer go, and what happens to it when you start a second container?

2. `docker ps -a` shows the first container still exists, exited.  What command sequence would get the file back?  (Hint: `docker start` plus the verb that enters a running container.)

   *Hint:* The sequence has two steps.  First restart the stopped container: `docker start <container-id>`.  Then open a shell inside it using the command that enters an existing running container rather than creating a new one: `docker exec -it <container-id> bash`.  Once inside, `cat /notes.txt` should show the file.

3.  State the design lesson as a rule: anything that must survive the container goes in a ______. (Part II names it.)

   *Hint:* The blank is a word that describes something stored on your host machine and linked into the container at startup.  What mechanism lets data outlive the container that wrote it?

---

*Part I showed that a container is isolated and disposable by design.  Part II shows how to pierce that isolation intentionally: ports let your browser reach inside, and volumes let data survive even when the container is destroyed.*

# Part II: Ports and Volumes

In this Part, you will learn the two flags that appear in nearly every real Docker command: `-p` for port mapping (making a service reachable from your browser) and `-v` for volumes (keeping data alive across container restarts).  These are the mechanisms that make containerized services actually usable.

> Continuing the apartment analogy: by default your apartment has no mailbox slot (no ports) and no storage unit outside the building (no persistent volumes).  This section is about installing both.  Ports are the doorbell that lets the outside world ring in; volumes are the storage locker in the parking garage that survives even if the apartment is demolished and rebuilt.

## 3.  Ports: Letting the Outside In

A containerized server listens on a port *inside* the container, invisible to your browser until you **publish** it with `-p HOST:CONTAINER`:

```bash
docker run -d --name webui -p 3000:8080 ghcr.io/open-webui/open-webui:main
# Open WebUI listens on 8080 INSIDE; your browser visits http://localhost:3000
```

Read `-p 3000:8080` as "host port 3000 forwards to container port 8080."  The host side is yours to choose, which is how you run two services that both *internally* use 8080 (map them to 3000 and 3001).  When `docker run` fails with "port is already allocated," some other process owns the host port: `lsof -i :3000` from the shell module finds the culprit, and remapping is the usual fix.  Plan your ports in a table before launching a stack; the agent stack module provides ours.

**Port mapping quick-reference:**

| Scenario | Flag to Use | Try It |
|---|---|---|
| Expose a web UI on port 3000 from a container that listens on 8080 | `-p 3000:8080` | `docker run -d -p 3000:8080 nginx` then visit `http://localhost:3000` |
| Run two services that both internally use 8080 without a conflict | `-p 3000:8080` for the first, `-p 3001:8080` for the second | Start each `docker run` separately with different host ports |
| Find what is already using port 3000 on your host | (not a Docker flag; use the shell) | `lsof -i :3000` |
| Check which host ports a running container has published | (inspect, not a run flag) | `docker port <container-name>` |

## 4.  Volumes: Letting Data Survive

**A bind mount maps a host directory into the container** with `-v HOST_PATH:CONTAINER_PATH`, and it is the answer to Model 1:

```bash
docker run -d --name webui \
  -p 3000:8080 \
  -v "$HOME/agents/openwebui/data:/app/backend/data" \
  ghcr.io/open-webui/open-webui:main
```

Now the application's data directory lives on *your* disk; destroy and recreate the container and your chats, settings, and accounts persist.  Append `:ro` to make a mount **read-only** (`-v "$HOME/vault:/vault:ro"`), which is precisely how we hand an agent reference material it must not modify.  Our course stack uses a disciplined four-tier mount layout (identity, workspace, skills, tool data) that the agent stack module details; the principle to absorb today is that *the container is disposable and the mounts are not*.

**Volume flag quick-reference:**

| Goal | Flag Syntax | Example Command |
|---|---|---|
| Persist application data to your home directory | `-v "HOST_PATH:CONTAINER_PATH"` | `docker run -v "$HOME/mydata:/app/data" myimage` |
| Give a container read-only access to a reference folder | `-v "HOST_PATH:CONTAINER_PATH:ro"` | `docker run -v "$HOME/vault:/vault:ro" myimage` |
| Mount the current working directory into the container | `-v "$(pwd):/app"` | Useful during development so code changes take effect without rebuilding the image |

You run a model server with `docker run -p 8080:11434 ...` and the docs say the server listens on port 11434 inside the container.  Which URL does your browser use to reach it?

[( )] http://localhost:11434, because that is the port the server actually listens on
[(X)] http://localhost:8080, because the host side of -p (the left number) is what the outside world sees
[( )] http://localhost:8080:11434, combining both ports
[( )] Either one; Docker forwards both directions automatically

---

*With ports and volumes, you can run and persist pre-built images.  The next step is building your own: writing a Dockerfile that packages your Python agent code into a portable, reproducible image anyone can run with a single command.*

## 5.  Writing a Dockerfile

**A Dockerfile is the recipe that builds an image**, a text file of instructions that Docker executes top to bottom, saving each step as a layer (a cached snapshot).  One instruction per layer, and Docker only re-executes layers where something changed.  Here is a complete, real one for a tiny Python agent service, annotated:

```dockerfile
FROM python:3.12-slim
# Start FROM a base image: Python preinstalled on slim Debian.

WORKDIR /app
# All later commands run here; created automatically.

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy ONLY the dependency list first, then install. Docker caches layers:
# as long as requirements.txt is unchanged, rebuilds skip the slow install.

COPY . .
# Now copy the application code (changes often, so it goes LAST).

EXPOSE 8000
# Documentation of the listening port (publishing still needs -p at run time).

CMD ["python", "server.py"]
# The default command a container runs at start.
```

Build and run it:

```bash
docker build -t myagent:0.1 .          # -t names (tags) the image; . is the build context
docker run -d -p 8000:8000 --name myagent myagent:0.1
curl http://localhost:8000/health      # verify
```

The ordering rule (stable layers first, volatile layers last) is the single most useful Dockerfile habit: it turns five-minute rebuilds into five-second ones.

**Dockerfile instruction reference:**

| Instruction | What It Does | Example |
|---|---|---|
| `FROM image:tag` | Sets the base image every subsequent instruction builds on top of. Always the first line. | `FROM python:3.12-slim` starts from a minimal Python 3.12 environment. |
| `WORKDIR /path` | Sets the working directory inside the image for all following instructions. Creates the directory if it does not exist. | `WORKDIR /app` means subsequent `COPY` and `RUN` commands operate in `/app`. |
| `COPY src dest` | Copies files from your build context (your local folder) into the image. | `COPY requirements.txt .` copies the file into the current `WORKDIR`. |
| `RUN command` | Executes a shell command during the build and saves the result as a new layer. | `RUN pip install --no-cache-dir -r requirements.txt` installs Python packages. |
| `EXPOSE port` | Documents which port the container expects to receive traffic on. Does not actually publish the port; you still need `-p` at run time. | `EXPOSE 8000` |
| `CMD ["exec", "args"]` | The default command run when the container starts. Overridable at `docker run` time. | `CMD ["python", "server.py"]` |

*A single Dockerfile defines one service.  When your stack needs multiple services (a model gateway, a chat UI, your agent) Compose lets you define and start them all with one command.*

## 6.  Docker Compose: Stacks as a File

Running three services with hand-typed `docker run` lines gets old immediately.  **Compose declares the whole stack in one YAML file** (YAML is a human-readable configuration format, similar to a Python dictionary but without the quotes and brackets):

```yaml
# docker-compose.yml
services:
  gateway:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    volumes:
      - ./litellm_config.yaml:/app/config.yaml:ro
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped

  webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - ./webui-data:/app/backend/data
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - gateway
```

```bash
docker compose up -d        # start the whole stack
docker compose ps           # status
docker compose logs -f      # all logs, interleaved and labeled
docker compose down         # stop and remove (volumes survive)
```

Within a Compose file, services reach each other *by name* (`http://gateway:4000`), because Compose puts them on a private network together.  Reaching things *outside* that network, on your host machine, is the next section, and it is the key to our whole stack.

**Compose command reference:**

| Command | What It Does | When to Use It |
|---|---|---|
| `docker compose up -d` | Starts all services defined in `docker-compose.yml` in detached (background) mode, pulling images if needed. | Starting your stack at the beginning of a work session. |
| `docker compose ps` | Shows the current status (running, exited, restarting) of every service in the stack. | Quick health check: are all services actually up? |
| `docker compose logs -f` | Streams live, interleaved log output from all services, each line prefixed with the service name. | Debugging: watch what happens across services in real time. |
| `docker compose down` | Stops and removes all containers and networks for this stack. Named volumes are preserved by default. | Cleanly shutting down between sessions. |
| `docker compose down -v` | Same as `down` but also deletes named volumes, wiping all persisted data. | Starting completely fresh; use with caution. |

*Compose puts your services on a private network where they can reach each other by name.  But they cannot automatically reach things on your host machine (your laptop or workstation) because the container's network is isolated.  This section explains the special address that bridges that gap.*

## 7. host.docker.internal: Talking to the Host

A container has its own network, so inside a container, `localhost` refers to *the container itself*, not your machine.  The special hostname **`host.docker.internal`** is a DNS name (a human-readable address that Docker resolves to your host machine's IP) that lets a containerized service reach programs running on your host.  This is how a containerized agent reaches a model server running natively on the host (our Ollama runs this way).  One platform difference matters enormously: Docker Desktop (macOS, Windows) provides the name automatically, but **on Linux Docker Engine you must request it explicitly** on every container that needs it:

```bash
docker run --add-host=host.docker.internal:host-gateway ...
```

or, in Compose, the `extra_hosts` block shown above.  Forgetting this flag on Linux is the most common wiring failure in the agent stack lab, and now you will recognize its symptom instantly: connection refused to `host.docker.internal` from inside a container that works fine from the host.

**Host networking quick-reference:**

| Platform | Is `host.docker.internal` automatic? | What you must add if not |
|---|---|---|
| Docker Desktop on macOS | Yes, available in every container without any extra flags. | Nothing; it just works. |
| Docker Desktop on Windows | Yes, available in every container without any extra flags. | Nothing; it just works. |
| Docker Engine on Linux | No, you must opt in per container. | Add `--add-host=host.docker.internal:host-gateway` to every `docker run`, or add an `extra_hosts` block to every service in `docker-compose.yml`. |

---

## Model 2: Diagnose the Stack

> Back to the apartment analogy: imagine the gateway (Ollama) is a restaurant on the ground floor of a different building.  From the street (your host) you can walk in the front door.  But a tenant sealed inside their self-contained apartment (the WebUI container) cannot walk to the restaurant using "my front door"; that address leads to their own building's lobby, not the restaurant's.  They need the restaurant's external street address.  That external address is `host.docker.internal`.

A teammate's Open WebUI container cannot reach Ollama.  From the host, `curl http://localhost:11434` answers; from inside the container (`docker exec -it webui bash`), `curl http://localhost:11434` fails.

### Critical Thinking Questions

4.  Explain why the same URL behaves differently in the two places, using the container networking model.

   *Hint:* What does `localhost` resolve to when you are on your host machine versus when you are inside a container?  Each network namespace has its own loopback interface.  Draw a box labeled "host" and a box labeled "container" and trace where `localhost` points in each.

5.  Give the corrected URL the container should use, and the run-time flag a Linux host requires for it to resolve.

   *Hint:* The corrected hostname is the special DNS name Docker provides for reaching the host machine from inside a container.  Check Section 7 for the exact name.  The Linux flag is also in Section 7; it is a `--add-host` argument to `docker run`.

6.  Propose the three-step diagnostic ladder for any future "container cannot reach X" report: test from host, test from inside the container, then check what?  (Logs, the flag, the port map: order them and justify.)

   *Hint:* Start by narrowing down whether the problem is on the host side or the container side.  Step 1: `curl http://localhost:<port>` from your host terminal; does the service respond at all?  Step 2: `docker exec -it <container> bash` then repeat the curl; does it fail?  If yes, the problem is networking between the container and host, not the service itself.  Step 3: for that networking failure, what are the two most likely causes, missing flag or wrong hostname?  Check those next.

---

> **Common Misconception:** Many beginners assume that because `curl http://localhost:11434` works from the host, the containerized service should "just see it" too.  This is wrong.  Each container runs in its own network namespace.  Inside the container, `localhost` (or `127.0.0.1`) refers to the container's own loopback interface, not the host's.  The Ollama server bound to the host's port 11434 is completely invisible at that address from inside the container.  The fix is always to use `host.docker.internal` as the hostname, and on Linux, to explicitly enable it with `--add-host=host.docker.internal:host-gateway`.

---

*You now have the full toolkit: images, containers, ports, volumes, Dockerfiles, Compose stacks, and host networking.  Part III puts it all together through hands-on exercises that build on each other; completing all five means you are ready to wire the full course AI stack.*

## 8.  Making a Host Folder Available to a Container

This is the single most common thing you will do all semester, and the single most common thing to get wrong.  The flag is `-v HOST_PATH:CONTAINER_PATH[:MODE]`, and each of the three parts deserves care.

**Step 1: create the folder on the host first.**  Docker will happily create a missing host path *as root*, leaving you a folder you cannot write to.  Make it yourself:

```bash
mkdir -p "$HOME/agents/work"
```

**Step 2: use an absolute path.**  A relative path like `-v ./work:/work` works in Compose but is unreliable on the command line. `$HOME` and `$(pwd)` are your friends, and the quotes matter if any folder name contains a space:

```bash
docker run --rm -v "$HOME/agents/work:/work" alpine ls /work
```

**Step 3: know where "your machine" actually is.**  This trips up nearly everyone once:

| You are on | Host path to use | Note |
|---|---|---|
| macOS or Linux | `$HOME/agents/work` | Just works. |
| Windows + WSL2 (our setup) | `$HOME/agents/work` *inside WSL* | Keep project files in the Linux filesystem. |
| Windows + WSL2, files on `C:` | `/mnt/c/Users/you/work` | Works, but **much** slower, and file permissions behave oddly. |
| Windows PowerShell | `C:\Users\you\work` | Docker Desktop translates it; forward slashes also work. |

> **Watch out!**  On WSL, a project living under `/mnt/c/...` can be five to ten times slower for the many-small-files work that agents do (git operations, `npm install`, test runs).  If your agent feels inexplicably sluggish, check which filesystem the folder is on before you blame the model.

**Step 4: verify from inside.**  Never assume the mount landed:

```bash
docker run --rm -v "$HOME/agents/work:/work" alpine sh -c 'ls -la /work && touch /work/hello && echo wrote'
ls "$HOME/agents/work"          # hello should be here, on your real disk
```

If `/work` is empty inside the container but full on the host, you mounted the wrong path; Docker created an empty directory rather than erroring.

**Step 5: choose the mode deliberately.**  Appending `:ro` makes the mount read-only *inside* the container:

```bash
-v "$HOME/agents/work:/work"           # read-write: the agent may create and edit files here
-v "$HOME/notes:/reference:ro"         # read-only: the agent may read, and cannot corrupt
```

The mode is enforced by the kernel, not by politeness.  A process in the container that tries to write to a `:ro` mount gets `Read-only file system` and fails, no matter what it intended.

---

## 9.  Running a Coding Agent Inside a Container

A coding agent is a program that reads your files, writes new ones, and runs shell commands on your behalf, which is precisely the capability profile you would never grant a stranger.  A container is how you grant it anyway, on your terms.  The goal is not to make the agent weak; it is to make the **blast radius** small and known.

### 9.1 Build a small agent image

Install the agent CLI into an image rather than onto your laptop, so the tool and its dependencies are disposable too:

```dockerfile
# Dockerfile.agent
FROM node:22-slim

# git and ripgrep are what coding agents reach for constantly
RUN apt-get update && apt-get install -y --no-install-recommends \
      git ripgrep ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install whichever agent CLI you are using. Examples:
RUN npm install -g @anthropic-ai/claude-code
# RUN npm install -g @google/gemini-cli
# RUN npm install -g @openai/codex
# (Aider is Python: pip install aider-chat)

# Never run as root inside a container you are handing to an agent
RUN useradd -m agent
USER agent
WORKDIR /work
CMD ["bash"]
```

```bash
docker build -f Dockerfile.agent -t course-agent .
```

### 9.2 The mount layout: exactly one writable folder

The discipline that makes everything else safe is **one read-write mount and everything else read-only or absent**:

```bash
docker run -it --rm \
  --name agent \
  -v "$HOME/agents/project:/work" \
  -v "$HOME/notes/vault:/reference:ro" \
  -e ANTHROPIC_API_KEY \
  course-agent
```

- `/work`: the project.  Read-write, because the agent's job is to change it.  This folder is a **git repository**, so every change the agent makes is reviewable with `git diff` and revertible with `git checkout`.
- `/reference:ro`: your notes, style guides, or corpus.  The agent reads them and physically cannot modify them.
- `-e ANTHROPIC_API_KEY` with no value passes the variable through from your shell without baking it into the image or its history.  That is the right move for a throwaway `--rm` session, and it is not the end of the story: an environment variable is still readable by anyone who can run `docker inspect` on the container.  For anything longer-lived than an experiment, Step f of the [Containerized Agent direction](https://www.billmongan.com/Ursinus-CS357/Assignments/LocalAgent/Direction3) of the Local Agent lab shows the leak and moves the secret into Docker secrets instead.

What is deliberately **not** mounted matters more than what is:

| Do not mount | Why |
|---|---|
| `$HOME` | Hands the agent your entire life, including everything below. |
| `~/.ssh` | Keys that authenticate as you, everywhere. |
| `~/.aws`, `~/.config/gcloud` | Cloud credentials with real billing behind them. |
| `~/.config/gh` | A GitHub token that can push to every repo you can. |
| `/var/run/docker.sock` | The classic mistake: a container with the Docker socket can start a *privileged* container and own the host entirely. |

### 9.3 Trusted mode, and when it is actually reasonable

Coding agents prompt before each shell command or file write.  That prompt is the safety mechanism when the agent runs on your laptop, and it is also why people get prompt-fatigued and start approving without reading, which is worse than no prompt at all.

Most agents offer a way to skip the prompts.  Claude Code, for example, has `--dangerously-skip-permissions`; other tools call this "yolo", "auto-approve", or "full-auto" mode.  The name is a warning, and it is accurate **on a host**.

Inside a properly constrained container, the calculus changes: the container boundary replaces the per-action prompt.

```bash
# Reasonable ONLY because of the flags around it
docker run -it --rm \
  -v "$HOME/agents/project:/work" \
  -v "$HOME/notes/vault:/reference:ro" \
  --network none \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --pids-limit 256 \
  --memory 4g \
  -e ANTHROPIC_API_KEY \
  course-agent claude --dangerously-skip-permissions
```

Read that command as a sentence: *the agent may act without asking, and the worst it can do is damage one git-tracked folder.*  Every clause earns the first one.

> **Watch out!** `--network none` also blocks the agent from reaching the model API. Use it for offline refactoring against a local model reachable another way, or drop it and accept network egress.  There is no configuration where an agent can call a hosted model and also be unable to send data outward; decide which property you need.  There is, however, a middle setting worth knowing: put the agent on a network whose only reachable host is your own gateway, so it can call models but cannot reach anything else on the internet.  That is rung 5 in the next section's ladder, and the gateway it points at is the one the [Agentic CLI Tools tutorial](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-agentclis.md) routes through.

### 9.4 Read-only root, writable workspace

Isolation gets stronger when the container's *own* filesystem is read-only and only your workspace is writable:

```bash
docker run -it --rm \
  --read-only \
  --tmpfs /tmp:rw,size=256m \
  --tmpfs /home/agent/.cache:rw,size=512m \
  -v "$HOME/agents/project:/work" \
  -v "$HOME/notes/vault:/reference:ro" \
  course-agent
```

`--read-only` makes the entire container root filesystem immutable; the two `--tmpfs` mounts give back the scratch space that tools need, in memory, discarded on exit.  An agent under this configuration cannot install a background service, cannot modify its own tooling, and cannot leave anything behind outside `/work`.

**A ladder of configurations,** from most permissive to most constrained; pick the lowest rung that still lets the work happen:

| Rung | Command shape | Agent can | You are trusting |
|---|---|---|---|
| 0 | Agent on the host | Everything you can | The model, entirely |
| 1 | `-v $HOME:/work` | Read and write your whole home directory | Almost everything |
| 2 | `-v ./project:/work` | Change one project | Git to catch mistakes |
| 3 | Rung 2 + `:ro` reference + `--cap-drop ALL` | Change one project, read reference | The kernel |
| 4 | Rung 3 + `--read-only --tmpfs` | Change one project only | The kernel, and nothing persists |
| 5 | Rung 4 + egress only to your gateway | Change one project, reach models but no other host | The gateway's routing and its logs |
| 6 | Rung 4 + `--network none` | Change one project, offline | Nothing leaves |

### 9.5 Verify the fence before you trust it

Do not take the flags on faith; test them, the same way you would test any other claim:

```bash
# Should print "Read-only file system"
docker run --rm -v "$HOME/notes/vault:/reference:ro" course-agent \
  sh -c 'touch /reference/breakme || echo BLOCKED-as-expected'

# Should fail: no network
docker run --rm --network none course-agent \
  sh -c 'getent hosts api.anthropic.com || echo NO-NETWORK-as-expected'

# Should show only /work as a writable bind mount
docker run --rm -v "$HOME/agents/project:/work" course-agent mount | grep /work
```

Then `git status` and `git diff` in the project after a session.  The agent's work should be entirely visible as tracked changes; if something appeared that git does not show, your mount layout is wider than you thought.

Which change makes it reasonable to run a coding agent with its permission prompts disabled?

[( )] Using a more capable model, since stronger models make fewer destructive mistakes
[(X)] Running it in a container whose only writable mount is one git-tracked project folder, so the worst case is a reviewable diff
[( )] Adding an instruction to the system prompt telling the agent not to delete files
[( )] Running the agent as root inside the container so it can repair anything it breaks

> **Common Misconception:** "Skip permissions" is often read as a statement about the *agent*, that you trust it now.  It is really a statement about the *environment*: you have made the consequences of any single action small enough that approving each one adds no information.  If you cannot describe the worst case in one sentence, you have not earned the flag.

---

# Part III: Practice

## 10.  Exercises

1.  *First container.*

   *What to do:* Run an interactive Ubuntu container, install `curl` inside it with `apt-get update && apt-get install -y curl`, verify it works with `curl --version`, then exit.  Next, run a *new* Ubuntu container with `docker run -it ubuntu bash` and show that `curl` is missing.  Finally, use `docker start` and `docker exec` to re-enter the *original* container and confirm `curl` is still there.  Document both behaviors with copy-pasted terminal output.

   *Starter hint:* Run `docker ps -a` after your first session to find the original container's ID. Then use `docker start <id>` followed by `docker exec -it <id> bash` to re-enter it; do not run a new `docker run ubuntu bash` or you will get a fresh container.

   *You've succeeded when:* You can show side-by-side that `curl --version` works in the original container and fails in a freshly started one, and you can explain in one sentence why the two containers differ despite using the same image.

2.  *Persistent service.*

   *What to do:* Run Open WebUI with a published port and a bind-mounted data directory.  Create a user account inside the web interface.  Stop and remove the container completely with `docker stop webui && docker rm webui`.  Then recreate the container using the exact same `-v` flag pointing to the same host directory, and log back in to demonstrate your account survived container destruction.  Submit both `docker run` commands.

   *Starter hint:* Your two run commands should look like this (fill in the blanks):
   ```bash
   docker run -d --name webui \
     -p 3000:8080 \
     -v "$HOME/agents/openwebui/data:/app/backend/data" \
     ghcr.io/open-webui/open-webui:main
   ```
   The second run command after `docker rm webui` is identical; that is the whole point.

   *You've succeeded when:* You log back into the recreated container and your previously created account, settings, or chat history is still present, proving the data lived on your disk rather than inside the (now-deleted) container.

3.  *Your first image.*

   *What to do:* Write a `Dockerfile` for a Python script that prints the current time and exits.  Build the image, run it to confirm the output, then edit the Python script (for example, change the output message), rebuild, and record which layers Docker rebuilt and which it served from cache.  The cache behavior is the lesson; pay attention to the build output.

   *Starter hint:* Your `Dockerfile` should follow the pattern from Section 5.  Start with `FROM python:3.12-slim`, set a `WORKDIR`, copy your script with `COPY`, and set a `CMD`.  Build with:
   ```bash
   docker build -t mytime:0.1 .
   docker run --rm mytime:0.1
   ```
   After editing the script, rebuild with `docker build -t mytime:0.2 .` and watch which steps say "CACHED."

   *You've succeeded when:* You can point to a specific line in the build output showing a layer was served from cache and explain in one sentence which Dockerfile instruction caused Docker to use the cache versus rebuild from scratch.

4.  *Compose conversion.*

   *What to do:* Convert exercise 2's `docker run` command into a `docker-compose.yml` file with at least two services: Open WebUI and one additional service of your choosing (Ollama, a simple Nginx server, or anything from Docker Hub).  Start the stack with `docker compose up -d`, observe combined logs with `docker compose logs -f`, then tear it down with `docker compose down`.  Submit the complete `docker-compose.yml`.

   *Starter hint:* Your Compose file should have a `services:` block with two named entries.  Each entry mirrors the flags of your `docker run` command (`image:`, `ports:`, `volumes:`) written as YAML keys instead of CLI flags.  Start from the example in Section 6 and adapt it.

   *You've succeeded when:* `docker compose ps` shows both services in a running state, `docker compose logs -f` shows interleaved output from both, and `docker compose down` cleanly stops everything.  Bonus: add `depends_on:` so your second service waits for the first.

5.  *The host bridge.*

   *What to do:* Start any server on your host machine: Ollama if it is installed, or a simple Python HTTP server with `python3 -m http.server 8001` run in a terminal.  Then start a container with an interactive shell.  From inside the container, attempt `curl http://localhost:8001` and show that it fails.  Then attempt `curl http://host.docker.internal:8001` and show that it succeeds.  On Linux, include the required flag.  Paste both curl outputs as your deliverable.

   *Starter hint:* On macOS or Windows with Docker Desktop, run:
   ```bash
   docker run --rm -it ubuntu bash
   # then inside:
   apt-get update && apt-get install -y curl
   curl http://localhost:8001          # should fail
   curl http://host.docker.internal:8001  # should succeed
   ```
   On Linux, you must add the host flag when starting the container:
   ```bash
   docker run --rm -it --add-host=host.docker.internal:host-gateway ubuntu bash
   ```

   *You've succeeded when:* You have copy-pasted terminal output showing `curl http://localhost:8001` returning a connection error and `curl http://host.docker.internal:8001` returning a successful HTTP response, and you can explain in one sentence why the two addresses produce different results from inside the same container.

6.  *The agent's fence.*

   *What to do:* Build the agent image from Section 9.1 and prove its boundaries hold before you trust an agent inside it.  Create a scratch git repository to be the writable workspace and a second folder to be the read-only reference.  Build the image, then run all three verification commands from Section 9.5 and paste the output of each.  Finally, write one sentence naming the worst thing an agent could do to your machine from inside that container.

   *Starter hint:* Save the Section 9.1 Dockerfile as `Dockerfile.agent` and build it:
   ```bash
   mkdir -p ~/agents/project ~/agents/reference
   git -C ~/agents/project init
   docker build -f Dockerfile.agent -t course-agent .
   ```
   Then run the three checks from Section 9.5 in order: write to the `:ro` mount, resolve a hostname under `--network none`, and list the writable bind mounts.  Each is written to *fail loudly* when the fence is working, so a failure is your evidence, not your bug.

   *You've succeeded when:* Your three pasted outputs show, in order, `Read-only file system` (or your `BLOCKED-as-expected` message) from the reference mount, a name-resolution failure under `--network none`, and exactly one writable bind mount at `/work`.  Your worst-case sentence names a specific, bounded outcome, damage to files in one git-tracked folder, rather than a vague reassurance.  If you cannot write that sentence, Section 9.3 says you have not earned `--dangerously-skip-permissions`, and this exercise is where you find that out.

   *Going further:* Try to actually run an agent under the full Section 9.3 command.  You will hit the contradiction the Watch Out box names: `--network none` blocks the model API too.  Record what happened, then decide which rung of the Section 9.4 ladder your real work belongs on and say why.

---

## Reflection Prompt

Take 10 minutes individually in your notebook to respond at three levels:

**Personal level:** Containers enforce isolation by default and require explicit grants (a published port, a mounted directory, a host alias) for every capability.  Think about the apps and AI tools you use personally.  Which ones have access to far more of your data than they actually need to do their job?  What would it look like to apply a "deny by default, grant by exception" rule to your own digital life?

**Technical level:** The same principle (deny everything by default, explicitly grant only what is required) appears in firewall rules, file permissions, API scopes, and OAuth consent screens.  Describe one specific technical system you have encountered (in this course or elsewhere) that either upholds or violates this principle.  What were the consequences?

**Societal level:** AI agents running in containers are isolated from the host by default, but they still communicate outward over the network.  Isolation addresses what data an agent can *read*, but it does not address what an agent can *transmit*.  Who should be responsible for auditing what a containerized AI agent sends over the network: the developer, the user, the platform, or a regulator?  What mechanisms (technical or policy) could enforce that boundary?

---

## Coming Up Next

In the next module you will apply everything here to deploy the full course AI stack: Ollama running natively on the host, LiteLLM as a containerized gateway translating between model providers, and Open WebUI as the containerized chat interface, all wired together with the port mappings and `host.docker.internal` bridges you practiced today.  You will also write your first agent service as a Dockerfile and add it to a Compose stack, so the Dockerfile and volume habits from exercises 3 and 4 will matter immediately.

---

## 11.  Further Reading

- Docker, "Get Started" guide (docs.docker.com): the official walkthrough, well-paced.
- W. Mongan, "Building a Private AI Stack: From Mini PC to Autonomous Agents" (billmongan.com, May 2026): the course stack's full architecture, which the agent stack module deploys.
- Compose file reference (docs.docker.com/compose): the YAML keys we used and the many we did not.
