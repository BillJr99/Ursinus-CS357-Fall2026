# Docker from Zero: Containers for Agent Builders
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-docker.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-docker.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Docker from Zero: Containers for Agent Builders

Our entire local AI stack (the model servers, the gateways, the agent frameworks, the web frontends) runs in **Docker containers**, and so will the agents you build. This tutorial assumes you have never touched Docker and ends with you writing Dockerfiles and composing multi-service stacks. The arc: **images versus containers $\rightarrow$ run, exec, logs, stop $\rightarrow$ ports $\rightarrow$ volumes $\rightarrow$ writing a Dockerfile $\rightarrow$ docker compose $\rightarrow$ talking to the host**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Hands-on rules from the shell module apply: everyone types everything. Install Docker before class (Docker Desktop on macOS and Windows; Docker Engine on Linux) and verify with `docker run hello-world`. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Mental Model

## 1. Images and Containers

**An image is a frozen, shippable snapshot of a filesystem plus a default command; a container is a running instance of an image.** The relationship is exactly class to object: one image, many containers, each with its own running state. Images come from **registries** (Docker Hub by default; GitHub Container Registry, written `ghcr.io`, increasingly often), named like `ollama/ollama:latest`, where the part after `:` is the **tag** (a version label).

**Why containers for AI work?** Three reasons that will recur all semester. *Reproducibility*: the container carries its exact dependencies, so "works on my machine" becomes "works in this image" (and your evaluation harnesses demand that). *Isolation*: an agent running in a container can only see what you mount into it, which is our data-minimization principle enforced by architecture rather than by hope. *Disposability*: experiments can be destroyed completely with one command, leaving no residue on your host.

## 2. The Core Verbs

```bash
docker run hello-world                  # download (if needed) and run an image
docker run -it ubuntu bash              # -it: interactive terminal; explore, then `exit`
docker run -d --name web nginx          # -d: detached (background); --name: a handle
docker ps                               # list RUNNING containers
docker ps -a                            # list all, including exited ones
docker logs web                         # what has it printed?
docker logs -f web                      # follow live (the tail -f of Docker)
docker exec -it web bash                # open a shell INSIDE a running container
docker stop web                         # graceful stop
docker rm web                           # remove the stopped container
docker rmi nginx                        # remove the image itself
docker run --rm -it ubuntu bash         # --rm: self-cleaning; vanishes on exit
```

The pair worth internalizing is **run versus exec**: `run` creates a *new* container from an image; `exec` enters an *existing, running* one. Confusing them produces the classic beginner mystery of "I installed it but it is gone," because each `run` starts from the frozen image again.

---

## Model 1: The Disappearing File

A teammate runs `docker run -it ubuntu bash`, creates `/notes.txt` inside, exits, runs the same command again, and the file is gone.

### Critical Thinking Questions

1. Explain the disappearance using the image/container distinction. Where does (did) `/notes.txt` actually live?
2. `docker ps -a` shows the first container still exists, exited. What command sequence would get the file back? (Hint: `docker start` plus the verb that enters a running container.)
3. State the design lesson as a rule: anything that must survive the container goes in a ______. (Part II names it.)

---

# Part II: Ports and Volumes

## 3. Ports: Letting the Outside In

A containerized server listens on a port *inside* the container, invisible to your browser until you **publish** it with `-p HOST:CONTAINER`:

```bash
docker run -d --name webui -p 3000:8080 ghcr.io/open-webui/open-webui:main
# Open WebUI listens on 8080 INSIDE; your browser visits http://localhost:3000
```

Read `-p 3000:8080` as "host port 3000 forwards to container port 8080." The host side is yours to choose, which is how you run two services that both *internally* use 8080 (map them to 3000 and 3001). When `docker run` fails with "port is already allocated," some other process owns the host port: `lsof -i :3000` from the shell module finds the culprit, and remapping is the usual fix. Plan your ports in a table before launching a stack; the agent stack module provides ours.

## 4. Volumes: Letting Data Survive

**A bind mount maps a host directory into the container** with `-v HOST_PATH:CONTAINER_PATH`, and it is the answer to Model 1:

```bash
docker run -d --name webui \
  -p 3000:8080 \
  -v "$HOME/agents/openwebui/data:/app/backend/data" \
  ghcr.io/open-webui/open-webui:main
```

Now the application's data directory lives on *your* disk; destroy and recreate the container and your chats, settings, and accounts persist. Append `:ro` to make a mount **read-only** (`-v "$HOME/vault:/vault:ro"`), which is precisely how we hand an agent reference material it must not modify. Our course stack uses a disciplined four-tier mount layout (identity, workspace, skills, tool data) that the agent stack module details; the principle to absorb today is that *the container is disposable and the mounts are not*.

[[MC]]
You run a model server with `docker run -p 8080:11434 ...` and the docs say the server listens on port 11434. Which URL does your browser use?
- ( ) http://localhost:11434, because that is the server's port
- (x) http://localhost:8080, because the host side of -p is what the outside world sees
- ( ) http://localhost:8080:11434
- ( ) Either one; Docker forwards both

---

## 5. Writing a Dockerfile

**A Dockerfile is the recipe that builds an image**, one layer per instruction. Here is a complete, real one for a tiny Python agent service, annotated:

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

## 6. Docker Compose: Stacks as a File

Running three services with hand-typed `docker run` lines gets old immediately. **Compose declares the whole stack in one YAML file**:

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

Within a Compose file, services reach each other *by name* (`http://gateway:4000`), because Compose puts them on a private network together. Reaching things *outside* that network, on your host machine, is the next section, and it is the key to our whole stack.

## 7. host.docker.internal: Talking to the Host

A container has its own network, so inside a container, `localhost` means *the container itself*, not your machine. The special name **`host.docker.internal`** resolves to your host, which is how a containerized agent reaches a model server running natively on the host (our Ollama runs this way). One platform difference matters enormously: Docker Desktop (macOS, Windows) provides the name automatically, but **on Linux Docker Engine you must request it explicitly** on every container that needs it:

```bash
docker run --add-host=host.docker.internal:host-gateway ...
```

or, in Compose, the `extra_hosts` block shown above. Forgetting this flag on Linux is the most common wiring failure in the agent stack lab, and now you will recognize its symptom instantly: connection refused to `host.docker.internal` from inside a container that works fine from the host.

---

## Model 2: Diagnose the Stack

A teammate's Open WebUI container cannot reach Ollama. From the host, `curl http://localhost:11434` answers; from inside the container (`docker exec -it webui bash`), `curl http://localhost:11434` fails.

### Critical Thinking Questions

4. Explain why the same URL behaves differently in the two places, using the container networking model.
5. Give the corrected URL the container should use, and the run-time flag a Linux host requires for it to resolve.
6. Propose the three-step diagnostic ladder for any future "container cannot reach X" report: test from host, test from inside the container, then check what? (Logs, the flag, the port map: order them and justify.)

---

# Part III: Practice

## 8. Exercises

1. *First container.* Run an interactive Ubuntu container, install `curl` inside it (`apt-get update && apt-get install -y curl`), exit, and demonstrate with `docker run` versus `docker start`/`docker exec` that you understand why a fresh `run` lacks curl.
2. *Persistent service.* Run Open WebUI with a published port and a bind-mounted data directory; create an account; destroy the container; recreate it with the same mount; show your account survived. Submit the two run commands.
3. *Your first image.* Write the Dockerfile for a Python script that prints the time and exits, build it, run it, change the script, rebuild, and report which layers rebuilt and which came from cache.
4. *Compose conversion.* Convert exercise 2's run command into a `docker-compose.yml`, add a second service of your choosing, and demonstrate `up`, `logs -f`, and `down`.
5. *The host bridge.* With any server running on your host (Ollama, or `python3 -m http.server 8001`), prove from inside a container that `localhost` fails and `host.docker.internal` succeeds (with the Linux flag if applicable). Paste both curl outputs.

---

## Reflection Prompt

In your notebook: containers enforce isolation by default and require explicit grants (a published port, a mounted directory, a host alias) for every capability. Compare this "deny by default, grant by exception" stance with how you currently grant capabilities to the AI tools in your life. Which direction should each move?

---

## 9. Further Reading

- Docker, "Get Started" guide (docs.docker.com): the official walkthrough, well-paced.
- W. Mongan, "Building a Private AI Stack: From Mini PC to Autonomous Agents" (billmongan.com, May 2026): the course stack's full architecture, which the agent stack module deploys.
- Compose file reference (docs.docker.com/compose): the YAML keys we used and the many we did not.
