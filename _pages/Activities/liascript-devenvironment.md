<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-devenvironment.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-devenvironment.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Your AI Workbench: Shell, Git, Containers, and Your First Coding Agent

Today you build the bench you will work at for the rest of the semester, and by the end of it you will have watched an AI agent write code on your own machine.

The bench has four parts, and we build them in order: **the shell** (Step 0, the language you give every one of these tools their instructions in), **a model server** (Step 1), **a versioned workspace** (Step 3), and **a container** (Steps 2 and 4) that keeps everything an agent does inside a box you chose.  Step 8 then hands the whole bench to a coding agent and asks it to do something small, so you can see what that feels like before any of it is graded.

This tutorial builds **one environment that runs every CS357 lab**: a Docker container with the whole course Python stack preinstalled (retrieval, classical ML, NLP, explainability, plus Node.js with promptfoo for evaluation and opencode, the coding agent), bind-mounted onto a directory that is a **git repository with a GitHub remote**, so everything you write inside the container is versioned and pushed like normal work.

One deliberate exception: **Ollama stays on your host.**  Model inference is the performance-critical piece, so it runs natively with direct access to your hardware, and your containerized code reaches it over the host bridge at `http://host.docker.internal:11434`.  That hostname is doing real work: inside a container, `localhost` means *the container*, so reaching your own machine needs a different name.  The [Docker from Zero tutorial](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Docker) (Section 7, *host.docker.internal: Talking to the Host*) explains that and everything else here from the ground up; today we put it to work.  When a step below feels like magic, that is the page to read.

Two ideas carry the whole design:

1.  **The image is the environment.**  One course Dockerfile, built once, gives everyone a byte-for-byte identical lab environment.  No more "works on my machine."
2.  **The mount is the only door.**  The container can see exactly one directory of your machine: the workspace you mount into it.  For a course where you *run agent code that takes actions*, that boundary is the blast-radius principle, enforced by architecture.

Work through the steps in order.  Each practice step shows the command *and* the output you should expect.  If Docker cannot run on your machine, Step 10 (the native fallback) is a complete, fully supported route.

### What each step produces for the Overview assignment

Most of what the Overview assignment asks you to paste comes out of this page.  Capture the output of each proof command as you go, and you will not have to redo any of it.

| Step | The command that proves it | The Overview item it satisfies |
|---|---|---|
| 1 | `ollama --version` and `curl http://localhost:11434/api/tags` | Part 1A, Steps 1 and 3 |
| 2 | `docker run hello-world` | Your route choice: a working Docker means Route A |
| 3 | `git remote -v` | Part 1.5, Step 2 (the repository you will push to) |
| 4 | The `student@...:/workspace$` prompt | Route A evidence: include this prompt in every container transcript |
| 5 | The five checks in 5.1 through 5.5 | The container verification lines the Overview's Route A asks for |
| 7 | `python3 hello_agent.py`, then `git log --oneline` after the push | Part 1.5, Steps 1 and 2.  For Part 1A, Step 4, run the Overview's `ollama_check.py` from this same prompt; it prints the full JSON |
| 8.1 through 8.3 | `opencode --version`, `/models`, and one answered prompt | Part 1B, Step 5 |
| 10 | The `uv` commands | Part 1.5, Step 3, which runs on your host on both routes |

---

## Directions and Group Roles

Today is a hands-on build day rather than a discussion, so the POGIL roles work a little differently.  Keep them, and rotate them at Step 5.

- **Manager**: keeps the build moving and makes the call to skip ahead.  Nobody should be stuck on one step while the room moves on; a blocked machine goes to the native route in Step 10 and catches up later.
- **Recorder**: logs every command and every error *verbatim*, including the ones that got fixed.  That log is most of what the Overview assignment asks you to submit, and a transcript reconstructed from memory is worth much less than one captured as it happened.
- **Presenter**: at the end, demos the team's working stack, including the coding-agent run in Step 8, and reports the one thing that took longest.
- **Reflector**: watches for friction the rest of the team stops noticing, and notes which failures were *environment* problems versus *instruction* problems.  That distinction is worth more than it sounds.

Help each other.  This session is graded through the Overview assignment, not through who finishes first, and an install that fails in an interesting way is a better class artifact than one that just works.

---

## Key Concepts

Step 0 defines the shell vocabulary.  These are the terms the rest of the page assumes.

| Term | Plain-English Definition | Where You'll Meet It |
|------|--------------------------|----------------------|
| **Image** | A frozen, read-only snapshot of an entire environment: an operating system, the installed packages, the settings. Built once from a recipe, then reused | The course image, built from the `Dockerfile` in Step 4. Everyone's is byte-for-byte identical, which is the point |
| **Container** | A running instance of an image, isolated from the rest of your machine. Disposable: deleting one costs you nothing, because the image can make another | What you enter at Step 4 and leave with `exit`. `--rm` deletes it on the way out |
| **Mount** | A directory of your real machine deliberately made visible inside the container. The container sees nothing else of yours | `/workspace`, which *is* your `cs357-work` folder. The one door in an otherwise closed box |
| **Host** | Your actual machine, as seen from inside a container. Worth naming because inside the container, `localhost` means the container, not you | `host.docker.internal`, the address your containerized code uses to reach Ollama running natively |
| **Repository (repo)** | A folder whose entire history git tracks, so any past state can be restored and any change can be undone | `cs357-work`, created in Step 3 and pushed to GitHub in Step 7 |
| **Commit** | A saved point in that history, with a message saying what changed and why | Step 7.4. Commit at every working stopping point, not at the end of the day |
| **Coding agent** | A program that takes a goal in plain English, reads your files, proposes edits and commands, and loops until it is done or you stop it. The agent loop from *The Agent Loop*, pointed at your file system | `opencode`, already in the course image and given one small job in Step 8 |
| **Action log** | The running account an agent prints as it works, naming each file it opens or writes and each command it runs. What you read instead of trusting the summary | The log the agent prints as it edits `hello_agent.py`. Reading it, then opening the file, is the skill, not a formality |
| **`AGENTS.md`** | A file of standing instructions an agent reads automatically, so you stop retyping context. A system prompt you keep in version control | Written in Step 8.4, and grown for the rest of the semester |

---

## Today's Plan

Anything marked self-paced is for outside class, and nothing graded assumes it.

1. Check what everyone already has installed, and pair up anyone whose Docker did not survive the download
2. Steps 0 through 3: the shell, Ollama on the host, Docker, and your repository
3. Steps 4 through 7: the container, its verification checks, Git credentials, and your first end-to-end call
4. Step 8: hand opencode a real task and watch it work.  Any step you do not reach today is the homework

**Doing this on your own, outside class?**  Follow the same steps in the same order and skip the roles.  Budget about ninety minutes, most of it downloads: start the Step 1 model pull and the Step 4 image build as soon as you reach them, and read ahead while they run.

---
## Step 0: The Shell, Briefly

Every step below, and every lab this semester, is typed into a **shell**.  If `cd`, `|`, and `$PATH` are already comfortable, skim the table and go to Step 1.  If they are not, this section is what makes everything after it make sense instead of feeling like incantation.

A shell is not complicated.  It reads one line of text, runs the command named at the front of it, and prints what comes back.  That is the entire contract.  Everything else is vocabulary.

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

This is a course about handing work to systems that act on your behalf, so start the habit here: **read a command before you press Enter, especially one you pasted.**  Ask three questions.

1.  *What does it change?* `ls` and `grep` only read. `rm`, `mv`, and `>` destroy or overwrite.
2.  *Where does it point?* `rm -rf build/` deletes a folder in your project. `rm -rf /` attacks your whole machine.  One character.
3.  *Who wrote it?*  A command from these notes and a command a chatbot produced for you deserve different amounts of trust, and by Step 8 you will be running commands an agent proposed.

A classmate pastes you this and says it will clean up the workspace:

```bash
rm -rf ~ /cs357-work/scratch
```

What does it actually do?

[( )] Deletes the `scratch` folder inside `cs357-work`
[(X)] Deletes your entire home directory, then complains that `/cs357-work/scratch` does not exist
[( )] Nothing; the space makes it invalid
[( )] Asks for confirmation before deleting anything

> **Why this answer?**  There is a space after the tilde.  That splits one path into two arguments, and the first one is your home directory.  This is not a trick question; it is a real and well documented way people have lost their work, and it is the class of mistake you are being asked to catch in a command a machine hands you.

> **Going deeper on the shell.**  Pipes, redirection into and out of files, background jobs, signals, and the `PATH` mechanics behind "command not found" are worked in full in the shell tutorial linked from today's schedule entry.  You do not need it to finish this page.

---

## Step 1: Ollama on the Host, First

Everything in this course talks to a local model, so the model server comes first, **installed natively on your machine, not in Docker**.

1.  Install [Ollama](https://ollama.com/download) for your operating system.
2.  Pull the course model (about 2 GB; do this on good wifi):

```bash
ollama pull llama3.2
```

3.  Verify the server answers **from your host terminal**:

```bash
ollama --version
curl http://localhost:11434/api/tags
```

Expected: a version string, then a JSON blob whose `"models"` list includes `llama3.2`.  (The Overview assignment, handed out today, asks you to submit a transcript of exactly this.  Capture your output as you go and you will not have to redo it.  If you installed Ollama before class, just rerun the `curl` to confirm it is running now, and move on.)

Note the address you just used: `localhost:11434`.  Hold that thought: in Step 5 the *same server* will need a *different name*, and knowing why is the point of this whole architecture.

---

## Step 2: Install Docker Desktop

If Docker is already on your machine from another course or project, skip to the verification in 2.4.  If Docker cannot be installed on your machine at all (unsupported hardware, an administrator lock, or too little disk), go to Step 10 now rather than at the end; it is a complete route, and nothing before Step 10 is wasted.

**Disk note:** Docker Desktop plus the course image (the ML libraries are hefty) needs roughly **8-10 GB** free, on top of Ollama's models.  Clear space now, not mid-download.

**2.1: Windows only: install Ubuntu on WSL2 first.**  Docker Desktop on Windows does not run containers on Windows itself; it runs them inside **WSL2**, the Windows Subsystem for Linux.  Installing the Linux side first prevents most of the Windows trouble on this page.  Open **PowerShell as Administrator** and run:

```powershell
wsl --install -d Ubuntu
```

Reboot if it asks.  Then launch **Ubuntu** from the Start menu and set the UNIX username and password it prompts for; these are new, and separate from your Windows account.  If `wsl --install` is not recognized, your Windows is too old for the one-liner: update Windows, or follow Microsoft's [manual WSL2 install steps](https://learn.microsoft.com/en-us/windows/wsl/install-manual).  Do the rest of this page from the **Ubuntu** terminal: `~` means what it says, paths are ordinary Linux paths, and a repository kept in your WSL2 home directory bind-mounts far faster than one on the Windows side.

**2.2: Install Docker.**  Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS/Windows) or [Docker Engine](https://docs.docker.com/engine/install/) (Linux), and start it.

**2.3: Windows only: check two Docker settings.**  Open Docker Desktop's **Settings** (the gear icon) and verify both of these:

- **General**: **Use the WSL 2 based engine** is checked.
- **Resources -> WSL Integration**: the **Ubuntu** toggle is switched **on**.  Click **Apply & Restart**.

That second setting is the one students most often miss, and its symptom is confusing: Docker Desktop looks perfectly healthy in its own window, but `docker` is not a command inside Ubuntu.

**2.4: Verify.**

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

1.  On [github.com](https://github.com/): **New repository** -> name `cs357-work` -> **Private** -> check **Add a README file**.
2.  Clone it:

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

The clone is a git repository that already knows its GitHub remote, the versioned half of the environment.  The address is HTTPS on purpose: inside the container you will authenticate with a repository-scoped token (Step 6), and that token works over HTTPS.  The credential from Part 1.5 of the Overview assignment stays on your host, where it belongs.

If you already installed and signed in to `gh` on your host, which is Part 1.5 Step 2 of the Overview assignment, both halves above collapse into one command:

```bash
gh repo create cs357-work --private --clone
```

Either route leaves you in the same place.  Do whichever you have the tools for right now; the rest of today does not care which you used.

---

## Step 4: Add the Course Container Files, Build, Enter

Download the three course container files and place them in a `.devcontainer/` folder inside your clone:

- [Dockerfile](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/Dockerfile), the recipe for the course image; every package is commented with the lab that uses it
- [docker-compose.yml](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/docker-compose.yml), one-command build/run, the workspace bind mount, and the Linux `host.docker.internal` fix
- [devcontainer.json](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/devcontainer.json), VS Code Dev Containers configuration
- (optional) [README.md](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/README.md), the quickstart version of this activity

The commands below fetch all three into the right place.  Run them from your clone:

```bash
cd ~/cs357-work
mkdir -p .devcontainer
cd .devcontainer
curl -fsSL -o Dockerfile https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/Dockerfile
curl -fsSL -o docker-compose.yml https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/docker-compose.yml
curl -fsSL -o devcontainer.json https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/files/devcontainer/devcontainer.json
cd ..
ls -la .devcontainer
```

Expected: the three files, under exactly those names.  If you saved them from a browser instead, check the names, because browsers sometimes save `Dockerfile` as `Dockerfile.txt`, and Docker will not find it under that name.  Your repository should now look like this:

```text
cs357-work/
  .devcontainer/
    Dockerfile
    docker-compose.yml
    devcontainer.json
  README.md
```

Open the Dockerfile and *read it*; it is exactly the anatomy from Docker from Zero Section 5 (`FROM`, `ARG`, `RUN`, `ENV`, `WORKDIR`, `CMD`), and every `pip` line names its lab.  Commit the files; they are part of your work:

```bash
git add .devcontainer
git commit -m "Add course dev container configuration"
```

Now build and enter, by either front door (both use the same Dockerfile; switch anytime):

**Option A: VS Code Dev Containers.**  Install the **Dev Containers** extension, open the `cs357-work` folder, run **Dev Containers: Reopen in Container**.  Terminals you open in VS Code are now inside the container.

**Option B: plain Docker Compose.**  From the `.devcontainer/` folder:

```bash
cd ~/cs357-work/.devcontainer
docker compose build
docker compose run --rm cs357
```

The first build downloads the ML libraries and takes a while; start it and go read a course paper.  When it finishes:

```text
student@a1b2c3d4e5f6:/workspace$
```

You are the non-root user `student`, in `/workspace`, which *is* your `cs357-work` clone (`ls -la` shows `.git`, `.devcontainer`, `README.md`).  Exit anytime with `exit` or Ctrl-D.  `--rm` deletes the container but never your files, which live in the mounted repo on your disk.

---

## Step 5: Verify the Stack from Inside the Container

Keep Ollama running on the host, enter the container, and run these five checks **at the container prompt**.  This transcript is what the Overview assignment asks for.

**5.1: The host bridge to Ollama.**  One line of Python, straight through the container wall to the model server on your host:

```bash
python3 -c "import requests; print(requests.get('http://host.docker.internal:11434/api/tags').json())"
```

Expected output (yours will show your models and digests):

```text
{'models': [{'name': 'llama3.2:latest', 'model': 'llama3.2:latest', 'modified_at': '...', 'size': 2019393189, 'digest': '...', 'details': {...}}]}
```

If you see a `models` list containing `llama3.2`, the whole architecture works: containerized Python -> `host.docker.internal` -> native Ollama, exactly Model 2 from the Docker from Zero activity, now load-bearing.  (Try `curl http://localhost:11434/api/tags` from the same container prompt and watch it fail; `localhost` inside the container is *the container*, not your machine.  That failure is correct behavior.)

The image also sets `OLLAMA_HOST=http://host.docker.internal:11434`, so tools that read that variable find the host server automatically; in your own code, use the `host.docker.internal` URL whenever a lab handout says `localhost:11434`.

**5.2: promptfoo (the evaluation lab's harness):**

```bash
promptfoo --version
```

```text
0.x.x
```

Any version string means Node.js and promptfoo are wired correctly.  An `ExperimentalWarning: DecompressInterceptor is experimental` line above it comes from promptfoo's own dependencies and is harmless.  If instead promptfoo refuses to start and complains that your Node is too old, run `node --version`: the image pins `v24.21.0`, and anything older than 22.22 means you are running a stale build of the image, which `docker compose build` fixes once you have re-fetched the current Dockerfile.

**5.3: The spacy language model (explainability/NLP directions):**

```bash
python3 -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spacy OK:', nlp('Agents plan and act.')[0].pos_)"
```

```text
spacy OK: NOUN
```

**5.4: opencode (the coding agent, and the OpenCode Studio lab's whole toolchain):**

```bash
opencode --version
```

```text
opencode x.x.x
```

The agent is baked into the image, so a version string here means Step 8 has nothing left to install and only needs its provider configured.

**5.5: gh (the GitHub CLI, which the next session, *Coding Agents*, runs its whole loop through):**

```bash
gh --version
```

```text
gh version 2.x.x
```

Also baked in, for the same reason opencode is.  It has no credential yet, which Step 6 gives it.

If all five pass, your environment for every lab is done.

> **If this check fails, start here.**  The most common failure at this step is the host bridge, where the one-liner in 5.1 raises a connection error.  Check the two usual suspects before anything else.  First, is Ollama actually running on the host right now?  Second, on Linux, was the container started through the course compose file?  That file carries the `extra_hosts` mapping (`host.docker.internal:host-gateway`) that makes the hostname resolve at all.

From *inside* the course container, which URL reaches the Ollama server running natively on your host?

[( )] `http://localhost:11434`, because that is where Ollama listens
[(X)] `http://host.docker.internal:11434`, because inside the container `localhost` means the container itself
[( )] `http://127.0.0.1:11434`, because the loopback address is shared with the host
[( )] Either of the first two; Docker forwards both automatically

---

## Step 6: Git Identity and Credentials Inside the Container

The container ships with `git` but knows nothing about you.  Set your identity **per repository** so it persists (it is stored in `/workspace/.git/config`, on your disk, inside the mount, and therefore survives container teardown):

```bash
cd /workspace
git config user.name "Your Name"
git config user.email "you@example.com"
```

(The VS Code route copies your host `~/.gitconfig` into the container automatically, so Option A students often find this already done.)

Pushing needs credentials, and this is the one place in the course where your own machine and the container are set up **differently on purpose**.  Read the reason before you pick, because the reason is the lesson.

**On your own machine, use an SSH key.**  Part 1.5 of the [Overview assignment](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/Overview) walks through checking for a key you already have, creating one with `ssh-keygen -t ed25519` if you do not, adding the public half under GitHub's *Settings -> SSH and GPG keys*, and confirming it with `ssh -T git@github.com`.  That is the right default there: the machine is yours, the key is yours, and it is the credential every later lab assumes once you are driving git from a terminal.

**Inside the container, the default flips to a scoped token**, and the reason is not convenience.  The container is not only yours: it runs a course image, and from Step 8 onward it runs *agent code* that acts on your files on your behalf.  A credential you place inside it is a credential that code can use.  So choose deliberately, and if you are not sure, take Choice 1:

**Choice 1: HTTPS with a personal access token (PAT).  Recommended default inside the container.**

1.  GitHub -> **Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens -> Generate new token**.
2.  Scope it tightly: *Only select repositories* -> `cs357-work`; Repository permissions -> **Contents: Read and write**; expiration at or beyond the end of the semester.  Add **Issues: Read and write** and **Pull requests: Read and write** if you already know you will let an agent open them for you, which is the next session, *Coding Agents: OpenCode, Spec-First Development, Hooks, and Reading the Log*.  Granting them later means `gh auth refresh -s <scope>` or a fresh token, and the symptom that sends you looking is a bare 403 from a command that worked yesterday.
3.  Copy the token (shown once).  When `git push` prompts for a password, paste the token.  Cache it for a work session so you are not retyping:

```bash
git config credential.helper 'cache --timeout=7200'
```

> **One rule that outlives this step.**  Never paste this token, or any other credential, into a chat with a model.  A hosted provider may retain, review, or train on what you send, and deleting the conversation does not reach it, so the only repair is to revoke the token and issue another.  Paste the variable name, never the value.  The Overview assignment's *Making a token, and putting it in your environment* section has the full rule at https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/Overview

**And the same token, for `gh`.**  The image carries `gh` as well, and it authenticates from an environment variable rather than from a sign-in.  Export it on your **host**, in the shell you start the container from:

```bash
export GH_TOKEN=github_pat_yourtokenhere
```

The `environment:` block in `docker-compose.yml` passes `GH_TOKEN` through by name, so the value lives in your shell and never in a file.  Check it inside with `gh auth status`.

Two things not to do here, and the reason is the same one this whole step is about.  Do not run `gh auth login` at the container prompt: it works, and it writes a credential carrying whatever reach your whole account has into a filesystem that is about to run agent code.  Do not mount `~/.config/gh` in either: that hands the same code a token that can push to every repository you own.  One scoped token, passed in by name, disappearing with the container, is the shape that matches the blast radius you actually want.

**Choice 2: SSH keys, mounted read-only.**  If you already use SSH with GitHub, add one line to the `volumes:` list in `docker-compose.yml`:

```yaml
    volumes:
      - "..:/workspace"
      - "~/.ssh:/home/student/.ssh:ro"
```

`:ro` makes the mount read-only (the container can use the keys, not modify them), and you would use the `git@github.com:...` remote form.

> **Security note: think like this course.**  Mounting `~/.ssh` deliberately widens the container's view of your machine: you are handing everything that runs inside (including, later, *agent code*) a credential that can push to **every** repository your key reaches.  The fine-grained PAT is the tighter default inside the container because its blast radius is one repository, `cs357-work`, and nothing else.  Least privilege is more than a lecture topic here: it is a configuration choice you are making right now.
>
> **And that is why the two environments differ.**  The question "which credential should I use?" has two different right answers here, and the difference is not the tool, it is the **blast radius**.  On your own machine, the SSH key is the correct credential and the passphrase is what protects it.  Inside a container that will shortly be running an agent, the correct credential is the narrowest one that still works.  If you find yourself wanting a single rule for both, notice that the rule *is* single: give each environment the least authority that lets it do its job.

---

## Step 7: Practice - The Full Loop, End to End

Run the complete workflow once, deliberately.  Every command below runs **inside the container** at the `/workspace` prompt, with Ollama running on the host.

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

(The exact words vary; it is a language model.  A sentence of text means success; a `ConnectionError` means revisit Step 5.1.)

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

**7.6: Verify on GitHub:** open `https://github.com/YOURUSERNAME/cs357-work` in your browser and see `hello_agent.py` with your commit message.  That file was written, executed against a host model server, committed, and pushed (entirely from inside the container) and it also sits on your host disk, because `/workspace` *is* your clone.  That double-existence is the whole architecture in one observation.

---

## Step 8: Your First Coding Agent

Everything so far has been you typing commands.  Now you hand the same bench to an agent and watch it type them instead.

A **coding agent** is the agent loop from the *Agent Loop* activity, wired to your file system and your terminal instead of a calculator.  You state a goal in plain English; it reads your files, proposes edits and commands, asks permission at the gates you leave open, runs what you approve, reads the result, and loops.  Same perceive-plan-act cycle, much larger blast radius, which is why we are doing this *inside* the container and *inside* a git repository.  If it makes a mess, `git checkout .` undoes the mess.

We use **opencode** because it is the most provider-flexible of the family: it speaks to any OpenAI-compatible backend, so it will talk to the Ollama server already running on your host without an account, an API key, or a bill.

### 8.1: It is already installed (on the container route)

The course image ships opencode, so on the container route there is nothing to install.  At the `/workspace` prompt:

```bash
opencode --version
```

That is deliberate rather than convenient.  `docker compose run --rm` deletes the container when you exit, and the only thing mounted is `/workspace`, so an agent you installed by hand into your container home directory would be gone every morning.  Baking it into the image is what makes it survive.

**On the native route** from Step 10, install it in your normal terminal:

```bash
curl -fsSL https://opencode.ai/install | bash
```

(If Node.js is your preference, `npm i -g opencode-ai` does the same job, and it is what the course Dockerfile uses.)

That first command pipes a script off the internet into a shell, which is the thing Step 0 told you to think twice about.  Two reasons it is defensible: the URL is the project's own documented installer, and on the container route you are not running it at all.  Notice that both halves of that sentence had to be true.

Verify either way:

```bash
opencode --version
```

**Every install route in one place:** [opencode.ai](https://opencode.ai/).  Two beyond the two above are worth knowing.  On Windows without WSL, `choco install opencode` or `scoop install opencode` install the command-line version natively, though the project itself recommends WSL, which is the route Step 10 and the Overview assignment describe.  That same page also offers a **desktop application**, in beta for macOS, Windows, and Linux, which puts this agent in a window with tabs instead of a terminal.

Use the container route for this course, because every lab assumes it and a classmate can reproduce it.  Install the command-line version natively only if you are on the Step 10 fallback.  Try the desktop app if you would rather have a window than a terminal, but treat it as a second face on one tool rather than a replacement: the labs hand you commands, and the OpenCode Studio lab asks for a transcript.

### 8.2: Point it at your own model

opencode reads a file called `opencode.json`, and the name matters: it is not `config.json`.  If opencode later reports no provider or no models, this file name is the first thing to check.  It reads that file from two places, a project directory and your home directory, and choosing between them is a decision about scope rather than about convenience.

| Where you are | The file to create |
|---|---|
| **Inside the course container** | `/workspace/opencode.json`, at the root of your repository |
| macOS, Linux, or WSL, natively | `~/.config/opencode/opencode.json` |
| Windows, native shell | `%USERPROFILE%\.config\opencode\opencode.json` (paste `%USERPROFILE%\.config\opencode` into the Run box with Win+R to open the folder) |

Read that first row carefully, because it is the one that saves you an hour.  A **project-level** `opencode.json` at a repository root configures that repository; the copy in your home directory configures everything you open.  Inside the container there is a second reason to prefer the project copy: your home directory is deleted when the container exits and `/workspace` is not.  The file then survives, it is versioned along with everything else, and a classmate who clones your repository gets your provider setup for free.  (Do not commit a real API key this way.  The Ollama block below has none, which is one more reason to prefer it.)

Hold on to the scope half of that, because it comes back.  In the *MCP* session you will attach a whole tool server to a configuration, and a server that belongs to one repository will sit in every other project you open, spending context it has no business spending, if you put it in the home-directory copy.

Before you write it, settle the address, because getting this wrong produces a connection error that looks like a broken install.  **`localhost` means "the machine this process is running on."**  Run opencode natively and that is your laptop; run it in the container and that is the container, where nothing is listening.

| Where opencode runs | Ollama | OpenWebUI |
|---|---|---|
| Natively on your laptop | `http://localhost:11434/v1` | `http://localhost:3000/api/v1` |
| Inside the container | `http://host.docker.internal:11434/v1` | `http://host.docker.internal:3000/api/v1` |

Write the file now.  The heredoc below is bash, so run it in a macOS, Linux, or WSL shell; on native Windows, make the folder and save the same JSON with an editor.  It is written for the container route, so put `localhost` in place of `host.docker.internal` if you installed opencode natively:

```bash
# Container route: write it to the repository root, where it survives `--rm`.
# Native route: use ~/.config/opencode/opencode.json instead (mkdir -p it first).
cat > /workspace/opencode.json <<'JSON'
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://host.docker.internal:11434/v1" },
      "models": { "llama3.2": { "name": "llama3.2 (raw Ollama)" } }
    }
  }
}
JSON
```

That file is everything the Overview assignment needs, and everything Steps 8.3 and 8.4 need.

**Optional: register OpenWebUI as a second provider.**  The `provider` block is a map, so you do not have to choose: name two keys and you get two providers, both live, both listed in `/models`.  OpenWebUI is not part of today's build; the optional OpenWebUI section of the [Overview assignment](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/Overview) installs it on your host.  Add this second entry once it is running there, because until then the entry appears in `/models` but cannot answer.  The two-provider version of the file looks like this, again written for the container route:

```bash
cat > /workspace/opencode.json <<'JSON'
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://host.docker.internal:11434/v1" },
      "models": { "llama3.2": { "name": "llama3.2 (raw Ollama)" } }
    },
    "openwebui": {
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "http://host.docker.internal:3000/api/v1",
        "apiKey": "sk-REPLACE-ME"
      },
      "models": { "llama3.2": { "name": "llama3.2 (via OpenWebUI)" } }
    }
  }
}
JSON
```

**These two routes are not the same thing, which is the reason to register both once you have both.**  Ollama hands you the raw model: the weights you pulled, answering with nothing around them.  OpenWebUI hands you that same model *plus* everything you configured in front of it, meaning your knowledge bases, your tools, your system prompts.  Later, when an answer is wrong, you will ask the same question through each and learn in one step whether the problem is the model or the pipeline you built around it.  That is worth two minutes of setup now.

Two clarifications about that key, because "API key" usually means "bill":

- **The key is yours, from your own server.**  Generate it in OpenWebUI under *Settings -> Account -> API Keys*, the same key you will mint for the Python clients in the Local Agent lab.  It authenticates you to a server running on your machine; it is not a payment credential.  Ollama takes no key at all, which is why its block has none.
- **Both routes are free** as long as the models behind them are the local ones you have pulled.  You are adding a front door, not a bill.  Point the same config at a paid provider's models later and the cost follows the model, not the config.

Port 3000 is the OpenWebUI default this course uses.  One more thing if you are on Linux: `host.docker.internal` is provided automatically by Docker Desktop on macOS and Windows, but not by Docker Engine on Linux, where you add `--add-host=host.docker.internal:host-gateway` to your `docker run`.  And Ollama listens only on `127.0.0.1` unless you start it as `OLLAMA_HOST=0.0.0.0 ollama serve`, which a container needs and which also means anything that can route to your machine can use your models.

> **Prefer a different agent?**  pi does the same two-provider trick through a plugin, and the instructions are in the [agentic CLI tools tutorial](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentCLIs).  If you want it running inside a container with the Dockerfile written out, that is in [terminal and filesystem isolation](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/FilesystemIsolation).

> **Tired of editing the `models` map?**  Each model you pull from here on means another entry in these blocks by hand.  §7 of the [OpenCode setup tutorial](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OpenCodeSetup) names an optional plugin that queries each provider and fills the map for you.

> **On OpenCode v2 with an AI gateway?**  v2 spells the provider block differently (`providers`, `package`, `settings`, and an `env` list for the key) and sets the key with `opencode service set env`.  The full configuration is in [OpenCode v2: a custom provider through an AI gateway](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OpenCodeSetup#opencode-v2-a-custom-provider-through-an-ai-gateway) in the OpenCode setup tutorial.

> **A candid expectation.** `llama3.2` is a 3-billion-parameter model running on your laptop.  It is a fine model to *learn the loop with* and a weak one to build with.  Expect it to be slow, to sometimes ignore your instructions, and to occasionally propose an edit that makes no sense.  That is not your setup failing; that is the honest capability of a small local model, and noticing where the ceiling sits is part of today's learning.  Later labs let you point the same tool at a larger model.


### 8.2b: Pick the agent, not just the model

The file you just wrote settles the **model**: which weights answer you.  It does not settle the **agent**: the named set of permissions and standing instructions that the model runs under.  opencode ships two primary agents, and the difference between them is the one you will care about all semester.  `build` may edit files and run commands.  `plan` may read the repository and propose steps but may not change anything until you approve it, which is the plan mode that the *Coding Agents* session and the OpenCode Studio lab are both built on.  Find the switch now, while nothing is at stake, rather than in the middle of a lab.

**In the desktop application, first.**  Open **File -> Settings** and turn on **Show Agent**, which puts the agent selector in the message bar beside the model dropdown.  It is not always shown on a fresh install, and its absence is the most common reason a student concludes, wrongly, that the desktop app has no plan mode.  With the selector visible you are choosing two things before every run, and you can see both: the model on one side, the agent on the other.

**In the terminal.**  `/models` lists the providers you registered above, so your Ollama entry, and your OpenWebUI entry if you added it, should appear there, distinguishable by the `name` fields you gave them.  **Tab** cycles the primary agents, `shift+tab` cycles back through them, and `<leader>a` lists them outright.  Those are the `agent_cycle`, `agent_cycle_reverse`, and `agent_list` keybinds, and you rebind them in `tui.json`; keybinds in `opencode.json` are deprecated and migrated for you.  The agent you are currently in is shown on the input line, so make a habit of reading it before you press Enter.

> **Why this is a setup step and not a detail.**  Every gate this course later asks you to build assumes you know which agent was running when it fired.  A rule that is obviously in force under `plan` is not in force under `build`, and the same prompt sent under each produces two very different transcripts.

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

Watch what happens, and *watch it deliberately*.  The agent will show you what it intends to change before it changes it.  Read the action log.  Approve it.  Then, back at the shell:

```bash
git status --short     # which files it touched
python3 hello_agent.py
```

Scroll back through the action log in the session before you leave it.  That record, every file opened and every command run, is the only account of what the agent did, and it is gone when you quit.  The *Coding Agents* session runs the same job non-interactively so the record lands in a file instead.

> **You've succeeded when** the action log names a file you can then open and explain line by line, and the script still runs.  If the agent broke it, that is a perfectly good outcome for today: `git checkout hello_agent.py` and try a smaller instruction.

### 8.4: Leave it standing instructions

Every tool in this family reads a project instruction file so you stop retyping context.  For opencode the file is `AGENTS.md` in your project root:

```bash
cat > AGENTS.md <<'MD'
# cs357-work

My CS357 lab workspace.

- The model server is on the host at http://host.docker.internal:11434 (llama3.2).
- Python 3, standard library plus `requests`. Ask before adding a dependency.
- Every script must handle network errors and print a located message, e.g. [lab1:chat].
- Small, readable functions with docstrings. No cleverness I would not want to grade.

## GitHub: try gh, fall back to git, then ask

1. Reach for `gh` first for anything GitHub-side: creating and cloning
   repositories, issues, pull requests, reviews. Confirm once per session
   with `gh auth status`.
2. Fall back to `git` for what it does on its own: pull, add, commit, push,
   log, status. Say in your next message that you fell back, and why.
3. If both fail, stop and ask me. A push that prompts for a password, or a
   401 or 403 from either tool, means there is no working credential here.
   Tell me which command failed and what it said. Do not switch the remote
   between HTTPS and SSH, do not ask me to paste a token into a file, and
   do not retry in a loop.

## Credentials

Never ask me to paste a token, key, or password into this conversation, and
never print one into your output. If a task needs a secret, stop and tell me
which environment variable should hold it, then assume it is set.
MD
git add AGENTS.md hello_agent.py && git commit -m "First coding-agent session"
```

Rule 3 is the one doing real work, and it is worth saying why it has to be written down.  An agent that hits an authentication failure will try to fix it, because fixing things is what you asked it to do, and every repair available to it is worse than stopping: rewriting your remote, asking you to paste a token into a file it can read, or retrying until something times out.  "Stop and tell me" is not the agent's instinct.  It is a rule you give it.

That file is a **system prompt you keep in version control**.  The connection is exact: the `SYSTEM` string in the *Agent Loop* activity told a calculator agent what its job was and how to format its answers; `AGENTS.md` tells a coding agent what your project is and what "good work" means in it.  You will refine it all semester.

### 8.5: Three Properties to Insist On

Look back at what just happened.  You gave a program permission to change files on your computer, and it did.  The reason that was a reasonable thing to do is not that you trusted the model.  It is that the bench you built in Steps 1 through 7 gives you three specific properties, and they are the vocabulary for the rest of this course.

| Property | The question it answers | What gave it to you today | What its absence looks like |
|---|---|---|---|
| **Observability** | *What did it actually do?* | The plan before the change, then the action log after it, then the file itself | An agent that reports "done, I fixed the bug" and you have no independent way to check |
| **Isolation** | *What could it have reached?* | The container: one mount, `/workspace`, and nothing else of yours | An agent running on your host with your credentials, one bad path away from your documents |
| **Reversibility** | *Can I undo it?* | `git checkout .`, because you started from a clean tree | An afternoon's work quietly overwritten with no version history to restore from |

Notice three things about that table.

They are independent.  You can have any two without the third, and each combination fails differently.  Observability without reversibility means you get to watch the damage in detail.  Isolation without observability means the agent can only wreck the sandbox, but you will not know what it did in there or why the result is wrong.  Reversibility without isolation means you can restore the repository and not the credential that leaked out of it.

None of them come from the model.  They are properties of the *environment* you put the model in.  A more capable model does not give you any of the three, and a less capable one does not take them away.  This is why we spent a session on the bench before we spent one on the agent.

They are what "trust" actually decomposes into.  When someone asks whether you would let an agent do X, the useful reply is not yes or no. It is: can I see what it did, can I bound what it touches, and can I put it back?

You will meet all three again, made much more serious: **observability** as tracing and structured logs in the evaluation labs, **isolation** as non-root containers, read-only mounts, and OAuth scopes in the What a Container Isolates tutorial and the MCP, REST, and OAuth 2.0 tutorial, and **reversibility** as branch discipline, rollback, and the governance question of who is accountable when an autonomous system errs.

A student runs a coding agent directly in their home directory, outside any container, on a folder that is not a git repository, and carefully reads every change before approving it.  Which of the three properties do they have?

[( )] All three; reading the changes covers it
[(X)] Observability only.  Nothing bounds what the agent can reach, and nothing can restore a file it overwrote
[( )] Observability and reversibility, since they could retype anything lost
[( )] None; reading a change is not real observability

> **Why this answer?**  Reading the action log is genuine observability and it is worth something.  The trap is believing it is worth everything.  Careful review catches a bad change you are shown; it does nothing about a file the agent touched outside the change it described, and it gives you no way back once the write has landed.

### 8.6: herdr, for When One Agent Becomes Several

You ran one agent today and watched it the whole time.  That does not stay true.  By the Local Agent Lab you will start a task that runs for many minutes, and you will want to start a second one while the first works.

Two problems show up the moment you do.  An agent launched from an SSH shell dies when the connection drops, because it is a child of that connection.  And once three agents are running, the real question becomes *which one is waiting for me?*

**herdr** answers both.  It is an agent-aware terminal multiplexer: a persistent background server keeps every agent alive whether or not you are attached, and the interface shows you at a glance which agent is **blocked**, **working**, or **done**.  Plain `tmux` gives you the first half and not the second; to `tmux`, an agent waiting at a permission prompt is just text on a screen.

**On the container route, it is already installed**, alongside opencode.  Check it the same way:

```bash
herdr --version
```

**On the native route** from Step 10, install it in your normal terminal:

```bash
curl -fsSL https://herdr.dev/install.sh | sh
```

The installer downloads one release binary, verifies its SHA-256, and drops it in `~/.local/bin`.  `brew install herdr` works on macOS, and Windows without WSL uses `powershell -ExecutionPolicy Bypass -c "irm https://herdr.dev/install.ps1 | iex"`.  The same read-before-you-run caution from 8.1 applies, and the same two defenses: it is the project's documented installer, and on the container route you are not running it at all.

You do not need herdr today.  It is here so that it is on your bench before the session that assumes it.  The full treatment, including the "walk away and come back" discipline and why detaching is *not* the same as pausing, is Part IV of the [agentic CLI tools tutorial](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentCLIs).

> **The governance point, early:** detaching does not pause an agent.  It keeps reading, editing, running commands, and spending tokens the entire time you are gone.  The three properties in 8.5 are what make that acceptable, and the less you are watching, the more the *environment* rather than your attention has to be the thing keeping the agent safe.

---

### Model: What Did You Just Delegate?

Look back at the session you just ran, with your team.

### Critical Thinking Questions

1.  Name the four parts of the agent loop in what you just watched: where did opencode **perceive**, **plan**, **act**, and **remember**?  Point at specific things on your screen, not at the diagram.

   > *Hint: Reading your files is one of them.  The action log is another.  Your approval sits between two of them, which is the whole point.*

2.  You approved a change before it was applied.  What, precisely, would have been different if you had approved without reading?  Name a specific bad outcome that the reading step was your only defense against.

3.  The same install command (`curl ... | bash`) would have been a much worse idea on your host machine than it was inside the container.  Explain the difference in one sentence, using the word *mount*.

4.  Compare two ways of telling this agent about your project: retyping the context at the start of every session, versus committing `AGENTS.md`.  Beyond convenience, what does putting the instructions under version control let you do that retyping does not?

   > *Hint: What happens when the instructions turn out to be wrong?  What can you do with a file that has a history?*

> **Common Misconception:** "The agent ran my code, so the agent understands my project."  It does not.  It read the text of some of your files and produced text that looked like a plausible edit.  Everything that made that edit *correct* was your reading of the change and the test you ran afterward.  The review step is not a formality you will outgrow with a better model; it is the part of the loop where a human is still doing the work.

---

## Step 9: The Daily Workflow (and Why the Isolation Matters)

Everything after today is this loop:

> **Daily workflow**
>
> 1.  **Start**: Ollama running on the host, then `docker compose run --rm cs357` (from `cs357-work/.devcontainer/`), or "Reopen in Container" in VS Code.
> 2.  **Work**: edit files in `/workspace` (or on the host side; same directory).
> 3.  **Test**: run the lab's script or checks against `host.docker.internal:11434`.
> 4.  **Commit**: `git add -A && git commit -m "what changed and why"` at every working stopping point.
> 5.  **Push**: `git push` before you close the laptop.
>
> The container is disposable; the workspace is not.  And whenever a step above is tedious, `opencode` is sitting in that same container, one `AGENTS.md` better informed than it was yesterday.

Now the *why*, in this course's own terms.  Later in the semester you will run **agent loops**: code that reads model output and then *does things*: writes files, renames, deletes, retries.  Agents fail in creative ways, and an agent that misparses a response and executes `rm` on the wrong path is not hypothetical; it is a lab week.  Inside the course container, the worst any runaway script can touch is `/workspace`; that is **isolation** from Step 8.5, enforced by the mount rather than by hope.  And because `/workspace` is a git repository pushed to GitHub, even a trashed workspace is one `git checkout` (worst case, one fresh `git clone`) from restored: that is **reversibility**, and it is the reason the daily loop above insists on committing at every working stopping point rather than at the end.  Your documents, your other courses, your credentials (if you took the PAT route): unreachable, by construction.

The same property answers "did I break my environment or my code?": exit, rerun `docker compose run --rm cs357`, and you have a factory-fresh environment on the same workspace.  If the bug survives, it is yours.  For the mechanics underneath every claim in this paragraph (writable layers, bind mounts, network namespaces) see the [Docker from Zero activity](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Docker).

---

## Step 10: The Native Fallback (No Docker)

If your machine cannot run Docker (unsupported hardware, administrator locks, disk limits), work natively.  Every lab's **Before You Start** section already documents its native installs, and those remain fully valid; the container simply pre-bundles them.  The outline:

1.  **Ollama**: exactly as in Step 1; it is native in both routes.
2.  **Python environment**: in your cloned `cs357-work` repo, use [uv](https://docs.astral.sh/uv/) (from the Overview assignment's Part 1.5): `uv venv`, then `uv add` each lab's packages as that lab lists them: `requests` first (every lab), then `chromadb sentence-transformers` (retrieval), `scikit-learn numpy` (the ML labs), `spacy` plus `python -m spacy download en_core_web_sm` (NLP direction), `shap lime matplotlib pandas` (explainability direction), `flask` (web-endpoint direction).
3.  **Node.js, promptfoo, and opencode** (evaluation lab and the coding-agent labs): install Node.js from [nodejs.org](https://nodejs.org/), version **22.22 or newer**, because promptfoo refuses to start on anything older; the current 24 LTS is the safe choice, and the version your package manager offers is often not.  Confirm with `node --version`, then `npm install -g promptfoo opencode-ai`.
4.  **Addresses**: use `http://localhost:11434` everywhere this activity says `host.docker.internal:11434`; with no container wall, `localhost` on your host really is Ollama.
5.  **Git practice**: Steps 3, 6, and 7 work identically in a native terminal in your `cs357-work` clone (with the `localhost` substitution in `hello_agent.py`); do them there and capture the same transcript.

---

## Step 11: Troubleshooting

The entries are in step order.  Find the step you are on, and work down its entries before you post in the course channel; when you do post, include the exact command and its full output.

**Step 1: `ollama: command not found` right after installing.**  The installer put the binary somewhere not on your `PATH`, or your terminal predates the install.  Open a new terminal.  If it persists, find the binary (`ls /usr/local/bin/ollama`) and add its directory to `PATH`; that is the `PATH` idea from Step 0.

**Step 2: `Cannot connect to the Docker daemon`.**  Docker Desktop is not running (start the app), or on Linux the service is stopped (`sudo systemctl start docker`) or your user is not in the docker group (`sudo usermod -aG docker $USER`, then log out and in).

**Step 2: Docker Desktop is running, but `docker` is not a command inside Ubuntu (Windows).**  The WSL integration is off.  In Docker Desktop, **Settings -> Resources -> WSL Integration**, switch the **Ubuntu** toggle on, **Apply & Restart**, and open a new Ubuntu terminal.  While you are there, confirm **Settings -> General -> Use the WSL 2 based engine** is checked.

**Step 3: `git: command not found` or `'git' is not recognized`.**  On macOS, run `xcode-select --install`.  On Windows, install [Git for Windows](https://git-scm.com/download/win) or GitHub Desktop, which bundles it, or use the Ubuntu terminal from Step 2.1, where `sudo apt install git` provides it.

**Step 4: the build cannot find the Dockerfile.**  Check the file names in `.devcontainer/` with `ls -la`: a browser download often saves `Dockerfile` as `Dockerfile.txt`.  Rename it, and confirm you are running `docker compose` from the `.devcontainer/` folder.

**Step 4 (Windows): the bind mount is empty or the build cannot find files.**  Keep the clone under your user profile (or better, in your WSL2 home directory), and run `docker compose` from the `.devcontainer/` folder; the `..` in the compose file is relative to that folder.

**Step 4: the first build fails partway through the big pip layer.**  Almost always a network hiccup during the large ML downloads.  Rerun `docker compose build`; completed layers are cached and the build resumes at the failed step.

**Step 5: connection refused to `host.docker.internal:11434` (the 5.1 failure).**  Diagnose with the ladder from Docker from Zero Model 2: (1) from the *host*, `curl http://localhost:11434/api/tags`; if this fails, Ollama is not running; start it.  (2) If the host works but the container does not, and you are **on Linux**, the container was probably started without the host-gateway mapping; `host.docker.internal` is automatic on Docker Desktop (macOS/Windows) but must be opted into on Docker Engine.  The course `docker-compose.yml` includes `extra_hosts: ["host.docker.internal:host-gateway"]` and `devcontainer.json` includes the matching `--add-host` run argument, so this bites only when running the image by hand: add `--add-host=host.docker.internal:host-gateway` to your `docker run`.  (3) Some Ollama installs bind only to `127.0.0.1`, which the host gateway cannot reach; setting the environment variable `OLLAMA_HOST=0.0.0.0` where Ollama starts (see Ollama's docs for your OS) makes it listen on all interfaces.

**Step 5: model responses are slow inside the container.**  They should be exactly as fast as from the host, because inference runs *on the host* and the container only sends HTTP requests.  If host-side `ollama run llama3.2 "hi"` is also slow, that is your hardware and a small model like `llama3.2` is the right call; if only the containerized call is slow, something is off in your networking, so ask in the course channel with your Step 5.1 transcript.

**Step 7: `git push` rejected: `Authentication failed` / `Support for password authentication was removed`.**  GitHub does not accept account passwords over HTTPS; paste a **personal access token** at the password prompt.  If a token is rejected, check its scope: it must list `cs357-work` under *Only select repositories* with **Contents: Read and write**, and it must not be expired.

**Step 7: `gh` fails with 401, or says you are not logged in.**  The token expired or was never passed in.  `gh auth status` says which.  On your host, `gh auth login`; inside the container, export `GH_TOKEN` on the host before `docker compose run`, because the container has no browser to sign in with.

**Step 7: `gh issue create` or `gh pr create` returns 403, but `gh auth status` looks healthy.**  This is a permissions answer rather than a sign-in problem, which is why the status looks fine.  A token scoped to **Contents** alone cannot touch issues or pull requests; add **Issues** and **Pull requests**, read and write, to the fine-grained token, or run `gh auth refresh -s <scope>`.

**Step 7: line endings: every file shows modified, or scripts fail with `\r: command not found`.**  Windows CRLF vs. container LF. Add a `.gitattributes` containing `* text=auto eol=lf`, run `git add --renormalize .`, commit; set VS Code's status-bar line ending to `LF` for new files.

**Step 8: `opencode` says "command not found" on the native route, right after the installer succeeded.**  The installer places the binary in `~/.local/bin`, which is not on your `PATH` by default. `export PATH="$HOME/.local/bin:$PATH"` fixes the current session; add the same line to `~/.bashrc` to make it stick.  This is the `PATH` mechanic from Step 0, met in the wild.  Inside the course container this cannot happen, because opencode is installed globally by the image; if it does, you are on an old image and `docker compose build` will fix it.

**Step 8: `opencode` starts but reports no provider or no models.**  Nine times out of ten the config is named `config.json` instead of `opencode.json`, so opencode never reads it.  Check the file name first.  Then check the location: `/workspace/opencode.json` on the container route, `~/.config/opencode/` natively (or `%USERPROFILE%\.config\opencode\` on native Windows).  Then check that the JSON parses, with `python3 -m json.tool /workspace/opencode.json`.  If your provider block disappeared between sessions, you wrote it into the container's home directory rather than into `/workspace`, and `--rm` deleted it; that is the failure the project-level file exists to prevent.

**Step 8: the agent proposes an edit that is obviously wrong, or loops on the same failed idea.**  Expected behavior for a 3B local model.  Stop it with Ctrl-C, `git checkout .` to discard, and give a smaller, more concrete instruction.  "Refactor this module" is beyond it; "add a docstring to this one function" is not.

---

## Quick Reference

| Task | Command |
|------|---------|
| Start the model server (host) | `ollama serve` or the Ollama desktop app, `ollama pull llama3.2` once |
| Enter the container | `docker compose run --rm cs357` (from `.devcontainer/`) |
| Rebuild the image | `docker compose build` |
| Verify the host bridge | `python3 -c "import requests; print(requests.get('http://host.docker.internal:11434/api/tags').json())"` |
| Verify promptfoo / spacy / opencode | `promptfoo --version` / `python3 -c "import spacy; spacy.load('en_core_web_sm')"` / `opencode --version` |
| One-repo git identity | `git config user.name "..."` / `git config user.email "..."` (in `/workspace`) |
| Cache the PAT for a session | `git config credential.helper 'cache --timeout=7200'` |
| The daily loop | Ollama up -> container -> work -> test -> commit -> push |
| Install the coding agent | Already in the course image; `opencode --version`.  Native route: `curl -fsSL https://opencode.ai/install \| bash` |
| Point the agent at your model | `/workspace/opencode.json` in the container (or `~/.config/opencode/opencode.json` natively), `baseURL` = `http://host.docker.internal:11434/v1` |
| Standing instructions for the agent | `AGENTS.md` in the repo root, committed |
| Undo whatever the agent did | `git checkout .` (or `git checkout <file>`) |
| Native fallback | each lab's Before-You-Start installs + `localhost:11434` instead of the bridge |
| How it all works | [Docker from Zero activity](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Docker) |

---

## Further Reading

- [The Shell, in Full: pipes, redirection, background jobs, signals, and the PATH mechanics behind "command not found".  Step 0 of today's activity is the short version of this](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Shell)

