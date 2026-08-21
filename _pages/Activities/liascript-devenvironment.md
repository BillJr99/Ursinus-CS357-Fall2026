<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-devenvironment.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-devenvironment.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Course Development Environment: One Container for Every Lab

This self-paced setup tutorial builds **one environment that runs every CS357 lab**: a Docker container with the whole course Python stack preinstalled (retrieval, classical ML, NLP, explainability, plus Node.js and promptfoo for evaluation), bind-mounted onto a directory that is a **git repository with a GitHub remote**, so everything you write inside the container is versioned and pushed like normal work.

One deliberate exception: **Ollama stays on your host.** Model inference is the performance-critical piece, so it runs natively with direct access to your hardware, and your containerized code reaches it over the host bridge at `http://host.docker.internal:11434`. If that hostname looks familiar, it should; it is exactly the pattern you studied in the [Docker from Zero activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-docker.md) (Section 7, *host.docker.internal: Talking to the Host*). That activity explains how everything here works under the hood; this one just puts it to work. When any step below feels like magic, that is the page to reread.

Two ideas carry the whole design:

1. **The image is the environment.** One course Dockerfile, built once, gives everyone a byte-for-byte identical lab environment. No more "works on my machine."
2. **The mount is the only door.** The container can see exactly one directory of your machine: the workspace you mount into it. For a course where you *run agent code that takes actions*, that boundary is not a nicety; it is the blast-radius principle, enforced by architecture.

Work through the ten steps in order. Each practice step shows the command *and* the output you should expect. If Docker cannot run on your machine, Step 9 (the native fallback) is a complete, fully supported route.

---

## Step 1: Ollama on the Host, First

Everything in this course talks to a local model, so the model server comes first, **installed natively on your machine, not in Docker**.

1. Install [Ollama](https://ollama.com/download) for your operating system.
2. Pull the course model (about 2 GB; do this on good wifi):

```bash
ollama pull llama3.2
```

3. Verify the server answers **from your host terminal**:

```bash
ollama --version
curl http://localhost:11434/api/tags
```

Expected: a version string, then a JSON blob whose `"models"` list includes `llama3.2`. (This is the same pre-class checklist as the Overview assignment's tool setup; if you already completed it there, just rerun the `curl` to confirm Ollama is currently running, and move on.)

Note the address you just used: `localhost:11434`. Hold that thought: in Step 5 the *same server* will need a *different name*, and knowing why is the point of this whole architecture.

---

## Step 2: Install Docker Desktop

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS/Windows) or [Docker Engine](https://docs.docker.com/engine/install/) (Linux). If you completed the Docker from Zero activity you already did this; skip to the verification.

**Disk note:** Docker Desktop plus the course image (the ML libraries are hefty) needs roughly **8-10 GB** free, on top of Ollama's models. Clear space now, not mid-download.

Verify:

```bash
docker run hello-world
```

Expected (abridged):

```text
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

`Cannot connect to the Docker daemon` means Docker Desktop is installed but not running; start the application.

---

## Step 3: Create Your Workspace Repository on GitHub

Your lab work lives in a private GitHub repository named `cs357-work`, the directory you will mount into the container and push to all semester.

1. On [github.com](https://github.com/): **New repository** -> name `cs357-work` -> **Private** -> check **Add a README file**.
2. Clone it:

```bash
cd ~
git clone https://github.com/YOURUSERNAME/cs357-work.git
cd cs357-work
git remote -v
```

Expected:

```text
origin  https://github.com/YOURUSERNAME/cs357-work.git (fetch)
origin  https://github.com/YOURUSERNAME/cs357-work.git (push)
```

The clone is a git repository that already knows its GitHub remote, the versioned half of the environment.

---

## Step 4: Add the Course Container Files, Build, Enter

Download the three course container files and place them in a `.devcontainer/` folder inside your clone:

- [Dockerfile](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/files/devcontainer/Dockerfile), the recipe for the course image; every package is commented with the lab that uses it
- [docker-compose.yml](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/files/devcontainer/docker-compose.yml), one-command build/run, the workspace bind mount, and the Linux `host.docker.internal` fix
- [devcontainer.json](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/files/devcontainer/devcontainer.json), VS Code Dev Containers configuration
- (optional) [README.md](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/files/devcontainer/README.md), the quickstart version of this activity

```text
cs357-work/
  .devcontainer/
    Dockerfile
    docker-compose.yml
    devcontainer.json
  README.md
```

Open the Dockerfile and *read it*; it is exactly the anatomy from Docker from Zero Section 5 (`FROM`, `RUN`, `ENV`, `WORKDIR`, `CMD`), and every `pip` line names its lab. Commit the files; they are part of your work:

```bash
git add .devcontainer
git commit -m "Add course dev container configuration"
```

Now build and enter, by either front door (both use the same Dockerfile; switch anytime):

**Option A: VS Code Dev Containers.** Install the **Dev Containers** extension, open the `cs357-work` folder, run **Dev Containers: Reopen in Container**. Terminals you open in VS Code are now inside the container.

**Option B: plain Docker Compose.** From the `.devcontainer/` folder:

```bash
cd ~/cs357-work/.devcontainer
docker compose build
docker compose run --rm cs357
```

The first build downloads the ML libraries and takes a while; start it and go read a course paper. When it finishes:

```text
student@a1b2c3d4e5f6:/workspace$
```

You are the non-root user `student`, in `/workspace`, which *is* your `cs357-work` clone (`ls -la` shows `.git`, `.devcontainer`, `README.md`). Exit anytime with `exit` or Ctrl-D; `--rm` deletes the container but never your files; they live in the mounted repo on your disk.

---

## Step 5: Verify the Stack from Inside the Container

Keep Ollama running on the host, enter the container, and run these three checks **at the container prompt**. This transcript is what the Overview assignment asks for.

**5.1: The host bridge to Ollama.** One line of Python, straight through the container wall to the model server on your host:

```bash
python3 -c "import requests; print(requests.get('http://host.docker.internal:11434/api/tags').json())"
```

Expected output (yours will show your models and digests):

```text
{'models': [{'name': 'llama3.2:latest', 'model': 'llama3.2:latest', 'modified_at': '...', 'size': 2019393189, 'digest': '...', 'details': {...}}]}
```

If you see a `models` list containing `llama3.2`, the whole architecture works: containerized Python -> `host.docker.internal` -> native Ollama, exactly Model 2 from the Docker from Zero activity, now load-bearing. (Try `curl http://localhost:11434/api/tags` from the same container prompt and watch it fail; `localhost` inside the container is *the container*, not your machine. That failure is correct behavior.)

The image also sets `OLLAMA_HOST=http://host.docker.internal:11434`, so tools that read that variable find the host server automatically; in your own code, use the `host.docker.internal` URL whenever a lab handout says `localhost:11434`.

**5.2: promptfoo (the evaluation lab's harness):**

```bash
promptfoo --version
```

```text
0.x.x
```

Any version string means Node.js and promptfoo are wired correctly.

**5.3: The spacy language model (explainability/NLP directions):**

```bash
python3 -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spacy OK:', nlp('Agents plan and act.')[0].pos_)"
```

```text
spacy OK: NOUN
```

If all three pass, your environment for every lab is done.

    --{{0}}--
The single most common failure at this step is the host bridge: the one-liner in 5.1 raises a connection error. Before anything else, check the two usual suspects: is Ollama actually running on the host right now, and, on Linux, was the container started through the course compose file, which contains the extra hosts mapping that makes host dot docker dot internal resolve at all?

From *inside* the course container, which URL reaches the Ollama server running natively on your host?

[( )] `http://localhost:11434`, because that is where Ollama listens
[(X)] `http://host.docker.internal:11434`, because inside the container `localhost` means the container itself
[( )] `http://127.0.0.1:11434`, because the loopback address is shared with the host
[( )] Either of the first two; Docker forwards both automatically

---

## Step 6: Git Identity and Credentials Inside the Container

The container ships with `git` but knows nothing about you. Set your identity **per repository** so it persists (it is stored in `/workspace/.git/config`, on your disk, inside the mount, and therefore survives container teardown):

```bash
cd /workspace
git config user.name "Your Name"
git config user.email "you@example.com"
```

(The VS Code route copies your host `~/.gitconfig` into the container automatically, so Option A students often find this already done.)

**Pushing needs credentials.** Two workable choices:

**Choice 1: HTTPS with a personal access token (PAT). Recommended default.**

1. GitHub -> **Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens -> Generate new token**.
2. Scope it tightly: *Only select repositories* -> `cs357-work`; Repository permissions -> **Contents: Read and write**; expiration at or beyond the end of the semester.
3. Copy the token (shown once). When `git push` prompts for a password, paste the token. Cache it for a work session so you are not retyping:

```bash
git config credential.helper 'cache --timeout=7200'
```

**Choice 2: SSH keys, mounted read-only.** If you already use SSH with GitHub, add one line to the `volumes:` list in `docker-compose.yml`:

```yaml
    volumes:
      - "..:/workspace"
      - "~/.ssh:/home/student/.ssh:ro"
```

`:ro` makes the mount read-only (the container can use the keys, not modify them), and you would use the `git@github.com:...` remote form.

> **Security note: think like this course.** Mounting `~/.ssh` deliberately widens the container's view of your machine: you are handing everything that runs inside (including, later, *agent code*) a credential that can push to **every** repository your key reaches. The fine-grained PAT is the tighter default because its blast radius is one repository, `cs357-work`, and nothing else. Least privilege is not just a lecture topic here; it is a configuration choice you are making right now.

---

## Step 7: Practice - The Full Loop, End to End

Run the complete workflow once, deliberately. Every command below runs **inside the container** at the `/workspace` prompt, with Ollama running on the host.

**7.1: Create `hello_agent.py`**, a first program that crosses the host bridge:

```bash
cat > hello_agent.py <<'PYEOF'
import requests

response = requests.post(
    "http://host.docker.internal:11434/api/chat",
    json={
        "model": "llama3.2",
        "messages": [{"role": "user", "content": "Say hello to CS357 in five words."}],
        "stream": False,
    },
)
print(response.json()["message"]["content"])
PYEOF
```

**7.2: Run it:**

```bash
python3 hello_agent.py
```

Expected: one short model-generated greeting, something like:

```text
Hello CS357, great to meet!
```

(The exact words vary; it is a language model. A sentence of text means success; a `ConnectionError` means revisit Step 5.1.)

**7.3: Check what git sees:**

```bash
git status
```

```text
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        hello_agent.py
```

**7.4: Stage and commit:**

```bash
git add hello_agent.py
git commit -m "First containerized call to host Ollama"
```

```text
[main 1a2b3c4] First containerized call to host Ollama
 1 file changed, 13 insertions(+)
 create mode 100644 hello_agent.py
```

**7.5: Push** (HTTPS users: the PAT prompt appears here the first time):

```bash
git push
```

```text
...
To https://github.com/YOURUSERNAME/cs357-work.git
   9f8e7d6..1a2b3c4  main -> main
```

**7.6: Verify on GitHub:** open `https://github.com/YOURUSERNAME/cs357-work` in your browser and see `hello_agent.py` with your commit message. That file was written, executed against a host model server, committed, and pushed (entirely from inside the container) and it also sits on your host disk, because `/workspace` *is* your clone. That double-existence is the whole architecture in one observation.

---

## Step 8: The Daily Workflow (and Why the Isolation Matters)

Everything after today is this loop:

> **Daily workflow**
>
> 1. **Start**: Ollama running on the host, then `docker compose run --rm cs357` (from `cs357-work/.devcontainer/`), or "Reopen in Container" in VS Code.
> 2. **Work**: edit files in `/workspace` (or on the host side; same directory).
> 3. **Test**: run the lab's script or checks against `host.docker.internal:11434`.
> 4. **Commit**: `git add -A && git commit -m "what changed and why"` at every working stopping point.
> 5. **Push**: `git push` before you close the laptop.
>
> The container is disposable; the workspace is not.

Now the *why*, in this course's own terms. Later in the semester you will run **agent loops**: code that reads model output and then *does things*: writes files, renames, deletes, retries. Agents fail in creative ways, and an agent that misparses a response and executes `rm` on the wrong path is not hypothetical; it is a lab week. Inside the course container, the worst any runaway script can touch is `/workspace`; this is the **blast-radius idea** from our containerization-safety discussions, enforced by the mount rather than by hope. And because `/workspace` is a git repository pushed to GitHub, even a trashed workspace is one `git checkout` (worst case, one fresh `git clone`) from restored. Your documents, your other courses, your credentials (if you took the PAT route): unreachable, by construction.

The same property answers "did I break my environment or my code?": exit, rerun `docker compose run --rm cs357`, and you have a factory-fresh environment on the same workspace. If the bug survives, it is yours. For the mechanics underneath every claim in this paragraph (writable layers, bind mounts, network namespaces) see the [Docker from Zero activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-docker.md).

---

## Step 9: The Native Fallback (No Docker)

If your machine cannot run Docker (unsupported hardware, administrator locks, disk limits), work natively. Every lab's **Before You Start** section already documents its native installs, and those remain fully valid; the container simply pre-bundles them. The outline:

1. **Ollama**: exactly as in Step 1; it is native in both routes.
2. **Python environment**: in your cloned `cs357-work` repo, use [uv](https://docs.astral.sh/uv/) (from the Overview assignment's Part 1.5): `uv venv`, then `uv add` each lab's packages as that lab lists them: `requests` first (every lab), then `chromadb sentence-transformers` (retrieval), `scikit-learn numpy` (the ML labs), `spacy` plus `python -m spacy download en_core_web_sm` (NLP direction), `shap lime matplotlib pandas` (explainability direction), `flask` (web-endpoint direction).
3. **Node.js + promptfoo** (evaluation lab): install Node.js from [nodejs.org](https://nodejs.org/), then `npm install -g promptfoo`.
4. **Addresses**: use `http://localhost:11434` everywhere this activity says `host.docker.internal:11434`; with no container wall, `localhost` on your host really is Ollama.
5. **Git practice**: Steps 3, 6, and 7 work identically in a native terminal in your `cs357-work` clone (with the `localhost` substitution in `hello_agent.py`); do them there and capture the same transcript.

---

## Step 10: Troubleshooting

**`Cannot connect to the Docker daemon`.** Docker Desktop is not running (start the app), or on Linux the service is stopped (`sudo systemctl start docker`) or your user is not in the docker group (`sudo usermod -aG docker $USER`, then log out and in).

**Connection refused to `host.docker.internal:11434` (the Step 5.1 failure).** Diagnose with the ladder from Docker from Zero Model 2: (1) from the *host*, `curl http://localhost:11434/api/tags`; if this fails, Ollama is not running; start it. (2) If the host works but the container does not, and you are **on Linux**, the container was probably started without the host-gateway mapping; `host.docker.internal` is automatic on Docker Desktop (macOS/Windows) but must be opted into on Docker Engine. The course `docker-compose.yml` includes `extra_hosts: ["host.docker.internal:host-gateway"]` and `devcontainer.json` includes the matching `--add-host` run argument, so this bites only when running the image by hand: add `--add-host=host.docker.internal:host-gateway` to your `docker run`. (3) Some Ollama installs bind only to `127.0.0.1`, which the host gateway cannot reach; setting the environment variable `OLLAMA_HOST=0.0.0.0` where Ollama starts (see Ollama's docs for your OS) makes it listen on all interfaces.

**Windows: the bind mount is empty or the build cannot find files.** Keep the clone under your user profile (or better, in your WSL2 home directory), and run `docker compose` from the `.devcontainer/` folder; the `..` in the compose file is relative to that folder.

**`git push` rejected: `Authentication failed` / `Support for password authentication was removed`.** GitHub does not accept account passwords over HTTPS; paste a **personal access token** at the password prompt. If a token is rejected, check its scope: it must list `cs357-work` under *Only select repositories* with **Contents: Read and write**, and it must not be expired.

**Line endings: every file shows modified, or scripts fail with `\r: command not found`.** Windows CRLF vs. container LF. Add a `.gitattributes` containing `* text=auto eol=lf`, run `git add --renormalize .`, commit; set VS Code's status-bar line ending to `LF` for new files.

**The first build fails partway through the big pip layer.** Almost always a network hiccup during the large ML downloads. Rerun `docker compose build`; completed layers are cached and the build resumes at the failed step.

**Model responses are slow inside the container.** They should be exactly as fast as from the host; inference runs *on the host*; the container only sends HTTP requests. If host-side `ollama run llama3.2 "hi"` is also slow, that is your hardware and a small model like `llama3.2` is the right call; if only the containerized call is slow, something is off in your networking; ask in the course channel with your Step 5.1 transcript.

---

## Quick Reference

| Task | Command |
|------|---------|
| Start the model server (host) | `ollama serve` or the Ollama desktop app, `ollama pull llama3.2` once |
| Enter the container | `docker compose run --rm cs357` (from `.devcontainer/`) |
| Rebuild the image | `docker compose build` |
| Verify the host bridge | `python3 -c "import requests; print(requests.get('http://host.docker.internal:11434/api/tags').json())"` |
| Verify promptfoo / spacy | `promptfoo --version` / `python3 -c "import spacy; spacy.load('en_core_web_sm')"` |
| One-repo git identity | `git config user.name "..."` / `git config user.email "..."` (in `/workspace`) |
| Cache the PAT for a session | `git config credential.helper 'cache --timeout=7200'` |
| The daily loop | Ollama up -> container -> work -> test -> commit -> push |
| Native fallback | each lab's Before-You-Start installs + `localhost:11434` instead of the bridge |
| How it all works | [Docker from Zero activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-docker.md) |
