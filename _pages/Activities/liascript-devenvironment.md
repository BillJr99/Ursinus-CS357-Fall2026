<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-devenvironment.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-devenvironment.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Your AI Workbench: Shell, Git, Containers, and Your First Coding Agent

Today you build the bench you will work at for the rest of the semester, and by the end of it you will have watched an AI agent write code on your own machine.

The bench has four parts, and we build them in order: **the shell** (Step 0, the language you give every one of these tools their instructions in), **a model server** (Step 1), **a versioned workspace** (Step 3), and **a container** (Steps 2 and 4) that keeps everything an agent does inside a box you chose. Step 8 then hands the whole bench to a coding agent and asks it to do something small, so you can see what that feels like before any of it is graded.

This tutorial builds **one environment that runs every CS357 lab**: a Docker container with the whole course Python stack preinstalled (retrieval, classical ML, NLP, explainability, plus Node.js and promptfoo for evaluation), bind-mounted onto a directory that is a **git repository with a GitHub remote**, so everything you write inside the container is versioned and pushed like normal work.

One deliberate exception: **Ollama stays on your host.** Model inference is the performance-critical piece, so it runs natively with direct access to your hardware, and your containerized code reaches it over the host bridge at `http://host.docker.internal:11434`. If that hostname looks familiar, it should; it is exactly the pattern you studied in the [Docker from Zero activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-docker.md) (Section 7, *host.docker.internal: Talking to the Host*). That activity explains how everything here works under the hood; this one just puts it to work. When any step below feels like magic, that is the page to reread.

Two ideas carry the whole design:

1. **The image is the environment.** One course Dockerfile, built once, gives everyone a byte-for-byte identical lab environment. No more "works on my machine."
2. **The mount is the only door.** The container can see exactly one directory of your machine: the workspace you mount into it. For a course where you *run agent code that takes actions*, that boundary is not a nicety; it is the blast-radius principle, enforced by architecture.

Work through the steps in order. Each practice step shows the command *and* the output you should expect. If Docker cannot run on your machine, Step 10 (the native fallback) is a complete, fully supported route.

---

## Step 0: The Shell in Ten Minutes

Every step below, and every lab this semester, is typed into a **shell**. If `cd`, `|`, and `$PATH` are already comfortable, skim the table and go to Step 1. If they are not, this section is the ten minutes that make the other nine steps make sense instead of feeling like incantation.

A shell is not complicated. It reads one line of text, runs the command named at the front of it, and prints what comes back. That is the entire contract. Everything else is vocabulary.

| Term | What it means | How you see it |
|------|---------------|----------------|
| **Shell** | The program that reads your typed line and runs it. On macOS and Linux it is usually `zsh` or `bash`; on Windows, use WSL2 or Git Bash so your commands match everyone else's | The `$` (or `%`) prompt waiting for you |
| **Terminal** | The window the shell runs inside. The shell is the engine; the terminal is the dashboard | Terminal.app, Windows Terminal, or the panel at the bottom of VS Code |
| **Working directory** | The folder the shell currently considers "here." Every relative path is measured from it | `pwd` prints it; `cd somewhere` changes it |
| **PATH** | The ordered list of folders the shell searches when you type a program's name. Not in any of them, and you get `command not found` | `echo $PATH` |
| **Pipe** (`\|`) | Sends the output of the command on the left straight into the command on the right, with no file in between | `grep ERROR agent.log \| wc -l` counts error lines |
| **Redirect** (`>`, `>>`) | Sends output into a file instead of onto your screen. `>` overwrites, `>>` appends | `python3 run_eval.py > results.txt` |
| **Environment variable** | A named value the shell hands to every program it launches. The standard way to pass configuration and secrets without typing them into your code | `export OLLAMA_HOST=http://localhost:11434` |

### The eight commands that carry the whole course

```bash
pwd                 # where am I?
ls -la              # what is here, including hidden files like .git
cd ~/cs357-work     # go there ( ~ means your home directory )
cat notes.md        # print a file
less agent.log      # page through a long file ( q to quit )
grep ERROR agent.log      # print only the lines containing ERROR
python3 script.py         # run a program
ps aux | grep ollama      # is that process actually running?
```

Two more you will want the first time something hangs: **Ctrl-C** interrupts whatever is running in the foreground, and **Ctrl-D** (or `exit`) leaves the shell or container you are in.

### Read before you run

This is a course about handing work to systems that act on your behalf, so start the habit here: **read a command before you press Enter, especially one you pasted.** Ask three questions.

1. *What does it change?* `ls` and `grep` only read. `rm`, `mv`, and `>` destroy or overwrite.
2. *Where does it point?* `rm -rf build/` deletes a folder in your project. `rm -rf /` attacks your whole machine. One character.
3. *Who wrote it?* A command from these notes and a command a chatbot produced for you deserve different amounts of trust, and by Step 8 you will be running commands an agent proposed.

A classmate pastes you this and says it will clean up the workspace:

```bash
rm -rf ~ /cs357-work/scratch
```

What does it actually do?

[( )] Deletes the `scratch` folder inside `cs357-work`
[(X)] Deletes your entire home directory, then complains that `/cs357-work/scratch` does not exist
[( )] Nothing; the space makes it invalid
[( )] Asks for confirmation before deleting anything

    --{{0}}--
There is a space after the tilde. That splits one path into two arguments, and the first one is your home directory. This is not a trick question; it is a real and well documented way people have lost their work, and it is exactly the class of mistake you are being asked to catch in a command a machine hands you.

> **Going deeper on the shell.** Pipes, redirection into and out of files, background jobs, signals, and the `PATH` mechanics behind "command not found" are worked in full in the shell tutorial linked from today's schedule entry. You do not need it to finish this page.

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

- [Dockerfile](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/Dockerfile), the recipe for the course image; every package is commented with the lab that uses it
- [docker-compose.yml](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/docker-compose.yml), one-command build/run, the workspace bind mount, and the Linux `host.docker.internal` fix
- [devcontainer.json](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/devcontainer.json), VS Code Dev Containers configuration
- (optional) [README.md](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/README.md), the quickstart version of this activity

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

## Step 8: Your First Coding Agent

Everything so far has been you typing commands. Now you hand the same bench to an agent and watch it type them instead.

A **coding agent** is the agent loop from the *Agent Loop* activity, wired to your file system and your terminal instead of a calculator. You state a goal in plain English; it reads your files, proposes edits and commands, asks permission at the gates you leave open, runs what you approve, reads the result, and loops. Same perceive-plan-act cycle, much larger blast radius, which is exactly why we are doing this *inside* the container and *inside* a git repository. If it makes a mess, `git checkout .` undoes the mess.

We use **opencode** because it is the most provider-flexible of the family: it speaks to any OpenAI-compatible backend, so it will talk to the Ollama server already running on your host without an account, an API key, or a bill.

### 8.1: Install it

Run this **inside the container**, at the `/workspace` prompt:

```bash
curl -fsSL https://opencode.ai/install | bash
```

(If Node.js is your preference, `npm i -g opencode-ai` does the same job. On the native route from Step 10, run either one in your normal terminal.)

You just piped a script off the internet into a shell, which is precisely the thing Step 0 told you to think twice about. Two reasons it is defensible here: the URL is the project's own documented installer, and you are inside a container whose only door is `/workspace`. Notice that both halves of that sentence had to be true.

Verify:

```bash
opencode --version
```

### 8.2: Point it at your own model

opencode reads `~/.config/opencode/config.json`. Create it so the agent uses the Ollama server on your host rather than a paid API:

```bash
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/config.json <<'JSON'
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://host.docker.internal:11434/v1" },
      "models": { "llama3.2": { "name": "llama3.2" } }
    }
  }
}
JSON
```

On the native route, use `http://localhost:11434/v1` instead: the same substitution as everywhere else in this tutorial.

> **A candid expectation.** `llama3.2` is a 3-billion-parameter model running on your laptop. It is a fine model to *learn the loop with* and a weak one to build with. Expect it to be slow, to sometimes ignore your instructions, and to occasionally propose an edit that makes no sense. That is not your setup failing; that is the honest capability of a small local model, and noticing where the ceiling sits is a real part of today's learning. Later labs let you point the same tool at a larger model.

### 8.3: Give it one small job

Still in `/workspace`, with `hello_agent.py` from Step 7 sitting there:

```bash
opencode
```

Then type, as your goal:

```text
Add a docstring to hello_agent.py explaining what it does, and print the
model's reply with a "Model says: " prefix. Do not change anything else.
```

Watch what happens, and *watch it deliberately*. The agent will show you what it intends to change before it changes it. Read the proposed diff. Approve it. Then, back at the shell:

```bash
git diff
python3 hello_agent.py
```

> **You've succeeded when** `git diff` shows you a change you can explain line by line, and the script still runs. If the agent broke it, that is a perfectly good outcome for today: `git checkout hello_agent.py` and try a smaller instruction.

### 8.4: Leave it standing instructions

Every tool in this family reads a project instruction file so you stop retyping context. For opencode the file is `AGENTS.md` in your project root:

```bash
cat > AGENTS.md <<'MD'
# cs357-work

My CS357 lab workspace.

- The model server is on the host at http://host.docker.internal:11434 (llama3.2).
- Python 3, standard library plus `requests`. Ask before adding a dependency.
- Every script must handle network errors and print a located message, e.g. [lab1:chat].
- Small, readable functions with docstrings. No cleverness I would not want to grade.
MD
git add AGENTS.md hello_agent.py && git commit -m "First coding-agent session"
```

That file is a **system prompt you keep in version control**. The connection is exact: the `SYSTEM` string in the *Agent Loop* activity told a calculator agent what its job was and how to format its answers; `AGENTS.md` tells a coding agent what your project is and what "good work" means in it. You will refine it all semester.

### 8.5: Three Properties to Insist On

Look back at what just happened. You gave a program permission to change files on your computer, and it did. The reason that was a reasonable thing to do is not that you trusted the model. It is that the bench you built in Steps 1 through 7 gives you three specific properties, and they are the vocabulary for the rest of this course.

| Property | The question it answers | What gave it to you today | What its absence looks like |
|---|---|---|---|
| **Observability** | *What did it actually do?* | The proposed diff before the change, then `git diff` after it | An agent that reports "done, I fixed the bug" and you have no independent way to check |
| **Isolation** | *What could it have reached?* | The container: one mount, `/workspace`, and nothing else of yours | An agent running on your host with your credentials, one bad path away from your documents |
| **Reversibility** | *Can I undo it?* | `git checkout .`, because you started from a clean tree | An afternoon's work quietly overwritten with no version history to restore from |

Three things worth noticing about that table.

**They are independent.** You can have any two without the third, and each combination fails differently. Observability without reversibility means you get to watch the damage in detail. Isolation without observability means the agent can only wreck the sandbox, but you will not know what it did in there or why the result is wrong. Reversibility without isolation means you can restore the repository and not the credential that leaked out of it.

**None of them come from the model.** They are properties of the *environment* you put the model in. A more capable model does not give you any of the three, and a less capable one does not take them away. This is why we spent a session on the bench before we spent one on the agent.

**They are what "trust" actually decomposes into.** When someone asks whether you would let an agent do X, the useful reply is not yes or no. It is: can I see what it did, can I bound what it touches, and can I put it back?

You will meet all three again, made much more serious: **observability** as tracing and structured logs in the evaluation labs, **isolation** as non-root containers, read-only mounts, and OAuth scopes in the Local Agent Lab's containerization and MCP directions, and **reversibility** as branch discipline, rollback, and the governance question of who is accountable when an autonomous system errs.

A student runs a coding agent directly in their home directory, outside any container, on a folder that is not a git repository, and carefully reads every diff before approving it. Which of the three properties do they have?

[( )] All three; reading the diffs covers it
[(X)] Observability only. Nothing bounds what the agent can reach, and nothing can restore a file it overwrote
[( )] Observability and reversibility, since they could retype anything lost
[( )] None; reading a diff is not real observability

    --{{0}}--
Reading the diff is genuine observability and it is worth something. The trap is believing it is worth everything. Careful review catches a bad change you are shown; it does nothing about a file the agent touched outside the change it described, and it gives you no way back once the write has landed.

---

### Model: What Did You Just Delegate?

Look back at the session you just ran, with your team.

### Critical Thinking Questions

1. Name the four parts of the agent loop in what you just watched: where did opencode **perceive**, **plan**, **act**, and **remember**? Point at specific things on your screen, not at the diagram.

   > *Hint: Reading your files is one of them. The proposed diff is another. Your approval sits between two of them, which is the whole point.*

2. You approved a diff before it was applied. What, precisely, would have been different if you had approved without reading? Name a specific bad outcome that the reading step was your only defense against.

3. The same install command (`curl ... | bash`) would have been a much worse idea on your host machine than it was inside the container. Explain the difference in one sentence, using the word *mount*.

4. Compare two ways of telling this agent about your project: retyping the context at the start of every session, versus committing `AGENTS.md`. Beyond convenience, what does putting the instructions under version control let you do that retyping does not?

   > *Hint: What happens when the instructions turn out to be wrong? What can you do with a file that has a history?*

> **Common Misconception:** "The agent ran my code, so the agent understands my project." It does not. It read the text of some of your files and produced text that looked like a plausible edit. Everything that made that edit *correct* was your reading of the diff and the test you ran afterward. The review step is not a formality you will outgrow with a better model; it is the part of the loop where a human is still doing the work.

---

## Step 9: The Daily Workflow (and Why the Isolation Matters)

Everything after today is this loop:

> **Daily workflow**
>
> 1. **Start**: Ollama running on the host, then `docker compose run --rm cs357` (from `cs357-work/.devcontainer/`), or "Reopen in Container" in VS Code.
> 2. **Work**: edit files in `/workspace` (or on the host side; same directory).
> 3. **Test**: run the lab's script or checks against `host.docker.internal:11434`.
> 4. **Commit**: `git add -A && git commit -m "what changed and why"` at every working stopping point.
> 5. **Push**: `git push` before you close the laptop.
>
> The container is disposable; the workspace is not. And whenever a step above is tedious, `opencode` is sitting in that same container, one `AGENTS.md` better informed than it was yesterday.

Now the *why*, in this course's own terms. Later in the semester you will run **agent loops**: code that reads model output and then *does things*: writes files, renames, deletes, retries. Agents fail in creative ways, and an agent that misparses a response and executes `rm` on the wrong path is not hypothetical; it is a lab week. Inside the course container, the worst any runaway script can touch is `/workspace`; that is **isolation** from Step 8.5, enforced by the mount rather than by hope. And because `/workspace` is a git repository pushed to GitHub, even a trashed workspace is one `git checkout` (worst case, one fresh `git clone`) from restored: that is **reversibility**, and it is the reason the daily loop above insists on committing at every working stopping point rather than at the end. Your documents, your other courses, your credentials (if you took the PAT route): unreachable, by construction.

The same property answers "did I break my environment or my code?": exit, rerun `docker compose run --rm cs357`, and you have a factory-fresh environment on the same workspace. If the bug survives, it is yours. For the mechanics underneath every claim in this paragraph (writable layers, bind mounts, network namespaces) see the [Docker from Zero activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-docker.md).

---

## Step 10: The Native Fallback (No Docker)

If your machine cannot run Docker (unsupported hardware, administrator locks, disk limits), work natively. Every lab's **Before You Start** section already documents its native installs, and those remain fully valid; the container simply pre-bundles them. The outline:

1. **Ollama**: exactly as in Step 1; it is native in both routes.
2. **Python environment**: in your cloned `cs357-work` repo, use [uv](https://docs.astral.sh/uv/) (from the Overview assignment's Part 1.5): `uv venv`, then `uv add` each lab's packages as that lab lists them: `requests` first (every lab), then `chromadb sentence-transformers` (retrieval), `scikit-learn numpy` (the ML labs), `spacy` plus `python -m spacy download en_core_web_sm` (NLP direction), `shap lime matplotlib pandas` (explainability direction), `flask` (web-endpoint direction).
3. **Node.js + promptfoo** (evaluation lab): install Node.js from [nodejs.org](https://nodejs.org/), then `npm install -g promptfoo`.
4. **Addresses**: use `http://localhost:11434` everywhere this activity says `host.docker.internal:11434`; with no container wall, `localhost` on your host really is Ollama.
5. **Git practice**: Steps 3, 6, and 7 work identically in a native terminal in your `cs357-work` clone (with the `localhost` substitution in `hello_agent.py`); do them there and capture the same transcript.

---

## Step 11: Troubleshooting

**`Cannot connect to the Docker daemon`.** Docker Desktop is not running (start the app), or on Linux the service is stopped (`sudo systemctl start docker`) or your user is not in the docker group (`sudo usermod -aG docker $USER`, then log out and in).

**Connection refused to `host.docker.internal:11434` (the Step 5.1 failure).** Diagnose with the ladder from Docker from Zero Model 2: (1) from the *host*, `curl http://localhost:11434/api/tags`; if this fails, Ollama is not running; start it. (2) If the host works but the container does not, and you are **on Linux**, the container was probably started without the host-gateway mapping; `host.docker.internal` is automatic on Docker Desktop (macOS/Windows) but must be opted into on Docker Engine. The course `docker-compose.yml` includes `extra_hosts: ["host.docker.internal:host-gateway"]` and `devcontainer.json` includes the matching `--add-host` run argument, so this bites only when running the image by hand: add `--add-host=host.docker.internal:host-gateway` to your `docker run`. (3) Some Ollama installs bind only to `127.0.0.1`, which the host gateway cannot reach; setting the environment variable `OLLAMA_HOST=0.0.0.0` where Ollama starts (see Ollama's docs for your OS) makes it listen on all interfaces.

**Windows: the bind mount is empty or the build cannot find files.** Keep the clone under your user profile (or better, in your WSL2 home directory), and run `docker compose` from the `.devcontainer/` folder; the `..` in the compose file is relative to that folder.

**`git push` rejected: `Authentication failed` / `Support for password authentication was removed`.** GitHub does not accept account passwords over HTTPS; paste a **personal access token** at the password prompt. If a token is rejected, check its scope: it must list `cs357-work` under *Only select repositories* with **Contents: Read and write**, and it must not be expired.

**Line endings: every file shows modified, or scripts fail with `\r: command not found`.** Windows CRLF vs. container LF. Add a `.gitattributes` containing `* text=auto eol=lf`, run `git add --renormalize .`, commit; set VS Code's status-bar line ending to `LF` for new files.

**The first build fails partway through the big pip layer.** Almost always a network hiccup during the large ML downloads. Rerun `docker compose build`; completed layers are cached and the build resumes at the failed step.

**`opencode` says "command not found" right after the installer succeeded.** The installer places the binary in `~/.local/bin`, which is not on the container's `PATH` by default. `export PATH="$HOME/.local/bin:$PATH"` fixes the current session; add the same line to `~/.bashrc` to make it stick. This is the `PATH` mechanic from Step 0, met in the wild.

**`opencode` starts but reports no provider or no models.** It is reading a config it cannot use. Check three things in order: that `~/.config/opencode/config.json` is valid JSON (`python3 -m json.tool ~/.config/opencode/config.json`), that the `baseURL` ends in `/v1`, and that the Step 5.1 host-bridge check still passes. The agent reaches Ollama by exactly the same route your Python does; if 5.1 works and opencode does not, the fault is in the config file.

**The agent proposes an edit that is obviously wrong, or loops on the same failed idea.** Expected behavior for a 3B local model. Stop it with Ctrl-C, `git checkout .` to discard, and give a smaller, more concrete instruction. "Refactor this module" is beyond it; "add a docstring to this one function" is not.

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
| Install the coding agent | `curl -fsSL https://opencode.ai/install \| bash`, then `opencode --version` |
| Point the agent at your model | `~/.config/opencode/config.json`, `baseURL` = `http://host.docker.internal:11434/v1` |
| Standing instructions for the agent | `AGENTS.md` in the repo root, committed |
| Undo whatever the agent did | `git checkout .` (or `git checkout <file>`) |
| Native fallback | each lab's Before-You-Start installs + `localhost:11434` instead of the bridge |
| How it all works | [Docker from Zero activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-docker.md) |
