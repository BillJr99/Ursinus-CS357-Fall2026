# Publishing Your Work: GHCR, Docker Hub, and npm
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-publishing.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-publishing.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Publishing Your Work: GHCR, Docker Hub, and npm

Building something that works on your machine is the first half of making; **publishing** it so anyone can `docker pull` or `npm install` your work is the second half, and it is far less mysterious than it looks. This tutorial takes you from zero accounts to published artifacts on the three registries that matter for this course: **GitHub Container Registry (GHCR)**, **Docker Hub**, and **npm**. The arc: **what registries are $\rightarrow$ names, tags, and versions $\rightarrow$ publishing a container image (both registries) $\rightarrow$ publishing an npm package $\rightarrow$ automating it with CI $\rightarrow$ publishing responsibly**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisites: the Docker module, a GitHub account, and (for Part III) Node.js. Everything in this module is free; we publish small, honest artifacts under your own names. **Course safety rule, stated up front: a human runs every publish command. Agents may prepare; only you push the button**, which is our external-publication governance gate practiced for real. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Registry** | A server that stores versioned, named software artifacts and serves them to anyone who asks — like a public library for code packages and container images | `ghcr.io` is GitHub's registry; `hub.docker.com` is Docker's; `registry.npmjs.org` is npm's |
| **Image tag** | A human-readable label attached to a specific version of a container image — like a version sticker on a jar of jam | `ghcr.io/yourusername/agent-eval:0.1.0` — the part after the colon is the tag |
| **Semver** | Semantic versioning: a three-number version scheme (`MAJOR.MINOR.PATCH`) where each number communicates what kind of change was made | Version `1.4.2` means: 1 major (breaking) release, 4 minor (backward-compatible feature) releases, 2 patch (bug-fix) releases |
| **Personal Access Token (PAT)** | A unique, revocable string that proves your identity to a registry — like a temporary badge you generate and can cancel, instead of sharing your actual password | `echo $CR_PAT \| docker login ghcr.io -u yourusername --password-stdin` |
| **Scoped npm package** | An npm package prefixed with your username (`@yourusername/package-name`) to guarantee it does not collide with any other package in the global registry | `@billjr99/hello-agent` can only be published by `billjr99` |
| **`npm pack --dry-run`** | A command that shows you exactly which files would be included in your published package, without actually publishing anything — the "check before you ship" command | Run this before every `npm publish` to make sure no credentials or scratch files are accidentally included |

---

# Part I: The Registry Mental Model

In this part, you will learn what registries are, how artifacts are named and versioned, and why the naming conventions matter for users who depend on your published work. The mental model you build here applies to every registry — GHCR, Docker Hub, npm, and PyPI all follow the same principles.

## 1. Registries, Names, and Tags

Shipping a Docker image is like publishing a recipe that anyone can run in their own kitchen, guaranteed to taste the same every time — as long as you package the recipe with all its ingredients and label the jar precisely. The registry is the cookbook store; the name and tag on the image are the title and edition of the recipe. Without that precision, a collaborator who `docker pull`s your image might get last week's broken version, or nothing at all.

**A registry is a server that stores versioned, named artifacts and serves them to anyone (or anyone authorized) who asks.** You have been a consumer all semester: every `docker pull` and `npm install` was a registry transaction. Today you become a producer, and the producer's first job is naming. Container images are named `registry/namespace/name:tag`:

```
ghcr.io/yourusername/agent-eval:0.1.0     # GHCR: namespace is your GitHub username
docker.io/yourusername/agent-eval:0.1.0   # Docker Hub (the docker.io prefix is implied by default)
```

The **tag** after the colon is a version label, and `latest` is just a tag like any other — it carries no magic beyond convention. If you publish only `latest` and then ship a breaking change, every user who runs `docker pull yourusername/agent-eval` gets the breaking version with no warning. npm packages are named `package-name` or, better for coursework, **scoped** under your username as `@yourusername/package-name`, which guarantees no collision with any other package in the global namespace.

**Versions follow semver.** The convention `MAJOR.MINOR.PATCH` (like `1.4.2`) encodes a promise to your users: patch bumps fix bugs without changing behavior, minor bumps add features while remaining backward-compatible, major bumps may break consumers who rely on the previous behavior. Registries treat published versions as immutable — npm will refuse to republish a version number you already used — which is why the discipline matters from your very first `0.1.0`.

## 2. Authentication: Tokens, Not Passwords

Every registry authenticates with **tokens** you generate, scope, and can revoke — never your account password. For GHCR, create a GitHub Personal Access Token with the `write:packages` scope (Settings → Developer settings → Personal access tokens); for Docker Hub, an access token from Account Settings → Security; for npm, `npm login` handles it interactively (with publish requiring a one-time password if you enable 2FA, which you should). The handling rules from the shell module apply with full force: tokens live in environment variables or password managers, never in code, never in Dockerfiles, never in anything committed to a repository.

---

## Model 1: Read the Name

Understanding what a registry name tells you before you pull anything is a foundational skill — and a safety habit. A malformed or unexpected tag can mean you are running old code, someone else's code, or a private image you cannot actually access.

### Critical Thinking Questions

**Question 1.** Decode `ghcr.io/billjr99/mcpproxy:0.3.1` into its four parts and state what each part tells a stranger before they pull anything.

[[___ Your answer here ___]]

*Hint:* The four parts are: registry hostname, namespace (who published it), image name (what it is), and tag (which version). For each part, write one sentence explaining what information it conveys and what you would do differently if any part were unfamiliar or unexpected.

**Question 2.** A teammate publishes only `latest` tags, ever. Describe the failure that hits their users the day a breaking change ships, and the one-line habit that prevents it.

[[___ Your answer here ___]]

*Hint:* If a user has `yourusername/tool:latest` running in production and the teammate ships a breaking change that replaces the `latest` tag, what happens the next time the user restarts their container? Is there any warning? What would pinning to a specific version tag like `0.3.1` have protected them from?

**Question 3.** Why does npm's refusal to ever republish a version number protect *you* as a consumer? Connect to the reproducibility requirements of your course labs.

[[___ Your answer here ___]]

*Hint:* Imagine you `npm install @someone/tool@1.2.3` in your project and it works perfectly. Six months later, a collaborator runs the same install command on a fresh machine. What does npm's immutability guarantee ensure about what they get? What would be possible if publishers could overwrite existing versions with different code?

---

# Part II: Publishing Container Images

In this part, you will publish a container image to GHCR and Docker Hub using the same four-step process that professional teams use in production. Pay attention to the visibility step — it is the most common reason a first publish appears to "fail."

## 3. To GHCR, Step by Step

GHCR is the natural home for course images because it lives beside your code — in the same GitHub account, with the same permissions model, and visible on the same repository page. From zero:

```bash
# 1. Authenticate — the PAT must have the write:packages scope
#    Store your PAT in the CR_PAT environment variable (never type it directly)
echo $CR_PAT | docker login ghcr.io -u yourusername --password-stdin

# 2. Build with the full registry name as the image name
#    (or tag an image you have already built locally)
docker build -t ghcr.io/yourusername/agent-eval:0.1.0 .
#    Alternative if already built:
#    docker tag agent-eval:0.1.0 ghcr.io/yourusername/agent-eval:0.1.0

# 3. Push to the registry
docker push ghcr.io/yourusername/agent-eval:0.1.0

# 4. Verify from a clean slate, simulating what a stranger would experience
docker rmi ghcr.io/yourusername/agent-eval:0.1.0   # remove local copy
docker pull ghcr.io/yourusername/agent-eval:0.1.0   # pull as a stranger would
```

One GHCR-specific step trips everyone the first time: new packages default to **private**. Visit the package's page on GitHub (your profile → Packages tab), open Package settings, and change visibility to public if you intend `docker pull` to work without authentication. While you are there, link the package to its source repository; consumers deserve to find your Dockerfile and understand what they are running.

## 4. To Docker Hub

Identical commands, different namespace, after creating a free account at hub.docker.com:

```bash
# Interactive login — use your Docker Hub access token as the password, not your account password
docker login

# Tag the image with your Docker Hub namespace (no registry prefix — Docker Hub is the default)
docker tag agent-eval:0.1.0 yourusername/agent-eval:0.1.0

# Push to Docker Hub
docker push yourusername/agent-eval:0.1.0
```

Docker Hub is where unqualified names resolve — a plain `docker pull nginx` pulls from Docker Hub — which gives it broader reach among users outside GitHub. GHCR gives you co-location with code and shared permissions with your repository. Publishing to both costs one extra `tag` and `push`, and many projects do exactly that.

[[MC]]
After pushing a new image to GHCR for the first time, a classmate reports that docker pull fails for everyone but you. The most likely cause is:
- ( ) GHCR requires a 24-hour propagation period
- ( ) The image tag must be latest for public pulls
- (x) New GHCR packages default to private visibility, and the package settings have not been changed to public
- ( ) Docker Hub credentials are interfering

---

# Part III: Publishing to npm

## 5. A Package from Zero

An npm package is a directory with a `package.json`; everything else is detail. A minimal, honest CLI utility that works as a real publishable package:

```bash
# Create the directory and initialize the package with your scoped username
mkdir hello-agent && cd hello-agent
npm init --scope=@yourusername -y      # scoped to your username: collision-proof
```

```json
{
  "name": "@yourusername/hello-agent",
  "version": "0.1.0",
  "description": "Prints a structured greeting; a CS357 publishing exercise.",
  "bin": { "hello-agent": "./index.js" },
  "files": ["index.js", "README.md"],
  "license": "MIT"
}
```

```javascript
#!/usr/bin/env node
// index.js
// The shebang line above (#!/usr/bin/env node) makes this file executable as a CLI command
try {
  const name = process.argv[2] || "world";
  // process.argv[2] is the first argument after "node index.js" or "hello-agent"
  console.log(JSON.stringify({ greeting: `hello, ${name}`, from: "CS357" }));
} catch (e) {
  // Course exception pattern: log for you, clean message for the user
  console.error(`[hello-agent:main] ${e}`);
  console.error(e.stack);
  process.exit(1);
}
```

Three `package.json` fields deserve special attention. **`bin`** is what makes `npx @yourusername/hello-agent` work as a terminal command — the same mechanism that installed every agent CLI tool you have used this semester. **`files`** is an explicit allowlist of what gets included in the published package; without it, npm will include everything in the directory, including your scratch notes, log files, and worse. **`license`** is not decoration: unlicensed code is legally unusable, and MIT is the course default unless you have a specific reason to choose otherwise.

## 6. Dry Run, Publish, Verify

```bash
# Step 1: Log in (once per machine — use your npm access token when prompted for a password)
npm login

# Step 2: See EXACTLY what would ship — read this output carefully before proceeding
npm pack --dry-run
# This lists every file that would be included in the published tarball

# Step 3: Publish (--access public is required for scoped packages on the first publish)
npm publish --access public

# Step 4: Verify as a stranger would — from a different directory or machine
npx @yourusername/hello-agent Bill
# Expected output: {"greeting":"hello, Bill","from":"CS357"}

# Step 5: Ship a fix
npm version patch                  # bumps 0.1.0 -> 0.1.1, edits package.json, creates a git tag
npm publish                        # publish the new version (no --access needed after first time)
```

`npm pack --dry-run` is the publish gate in command form: it lists every file about to go public, and reading that list before every publish is the habit that prevents the credential-in-a-tarball incidents you find in security news every year. Make it a reflex: dry run, read every line, then publish.

## 7. Automating with CI (and Why the Gate Stays Human)

Once publishing works by hand, a GitHub Actions workflow can automate it on every tagged release. The container pattern, from the course stack's own deployment:

```yaml
# .github/workflows/publish.yml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}   # automatically provided by GitHub Actions

- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}
    # github.ref_name is the tag you pushed (e.g., v0.2.0)
```

The npm equivalent swaps in `npm ci && npm publish` with an `NPM_TOKEN` stored as a repository secret. Notice what triggers the workflow: a *tag you push deliberately* — not every commit — so the human decision to publish survives the automation. That design is the AI-maker module's CI lesson and the governance assignment's publication gate, implemented in seven lines of YAML.

## 8. Publishing Responsibly

Four habits that separate professional publishing from littering:

**A README that answers three questions** — what is this, how do I install it, how do I use it in thirty seconds — ships with every package. A package without a README forces every user to read your source code before they can decide whether your package solves their problem.

**Secrets audits precede every push**: run `npm pack --dry-run` and scan the file list, then run `grep -r "key\|token\|password\|secret" .` over the files that would ship. One slip here is permanent.

**You publish only what you may**: course materials, datasets with usage restrictions, and other people's code all carry terms. A public registry is the worst place to discover you misread a license — after millions of people have cached your tarball.

**Unpublishing barely exists**: npm restricts unpublish after 72 hours and package mirrors cache everything. The moment of `push` is effectively irreversible, which is exactly why it sits behind a confirmation gate in our governance framework and in this course's rules.

---

## Model 2: The Pre-Publish Review

A teammate's `npm pack --dry-run` output includes: `index.js`, `README.md`, `notes/todo.md`, `config.json`, and `.env.example`.

Before every publish, the Recorder writes down the team's ruling on each file. The Manager ensures the team reaches genuine agreement on the investigation item before moving on.

### Critical Thinking Questions

**Question 4.** Rule on each file: ship it, exclude it, or investigate it first — with one clause of reasoning for each. Which one demands investigation, and what specifically are you looking for inside it?

[[___ Your answer here ___]]

*Hint:* `index.js` and `README.md` are almost certainly correct to ship — they are the package's executable and documentation. `notes/todo.md` is almost certainly wrong to ship — it is internal scratch material. `.env.example` requires judgment: is it an example with placeholder values, or does it contain real values with "example" in the name? `config.json` is the one that demands investigation: open it and look for any real endpoint URLs, API keys, or environment-specific values.

**Question 5.** Write the `files` allowlist that produces the correct tarball, and explain why the allowlist beats an ignore-list for safety.

[[___ Your answer here ___]]

*Hint:* An allowlist says "only ship these specific files." An ignore-list (like `.npmignore`) says "ship everything except these." Which approach is safer when you add a new file to the directory — one that you might forget to add to an ignore-list? Write the exact `"files"` array you would put in `package.json`.

**Question 6.** The publish succeeds and, two days later, the teammate realizes `config.json` held a real endpoint URL they would rather not share. Enumerate their actual options, honestly, and the lesson about gates.

[[___ Your answer here ___]]

*Hint:* npm does allow `npm unpublish` within 72 hours — but mirrors and caches may already have the package. After 72 hours, unpublish requires contacting npm support and is not guaranteed. What does this tell you about the irreversibility of publishing? What is the lesson about confirming the file list before you publish rather than after?

---

> **⚠️ Common Misconception:** Students often assume that because a file is listed in `.npmignore`, it is definitely excluded from the published package. The safer mental model is the reverse: use the `"files"` allowlist in `package.json` to explicitly declare what *is* included, and treat everything else as excluded. With an allowlist, a new file you add to the directory is excluded by default — you must consciously add it. With an ignore-list, a new file is included by default — you must consciously exclude it. The allowlist is safer precisely because the default is to exclude rather than to include, which means the cost of forgetting is "file is missing from the package" rather than "credential is published to npm."

---

# Part IV: Practice

## 9. Exercises

**Exercise 1.** First image, two homes. Containerize a trivial service (the Docker module's Dockerfile suffices), publish it to GHCR, make it public, and pull it from a teammate's machine. Optionally mirror it to Docker Hub.

*What to do:* Follow the four-step GHCR process from Section 3. After pushing, change the package visibility to public in GitHub Settings. Have a teammate confirm they can `docker pull` without being logged in.

*Starter hint:*

```bash
# Build and push
docker build -t ghcr.io/yourusername/hello-cs357:0.1.0 .
echo $CR_PAT | docker login ghcr.io -u yourusername --password-stdin
docker push ghcr.io/yourusername/hello-cs357:0.1.0

# Teammate verifies (on their machine, not logged in to your account)
docker pull ghcr.io/yourusername/hello-cs357:0.1.0
docker run --rm ghcr.io/yourusername/hello-cs357:0.1.0
```

*You've succeeded when:* A teammate can run `docker pull ghcr.io/yourusername/hello-cs357:0.1.0` from a fresh terminal without any credentials and get the image. Submit the image name, the commands you ran, and the teammate's pull transcript.

**Exercise 2.** First package. Publish a scoped npm package with a working `bin`, a real README, and a `files` allowlist. Have a teammate verify with `npx`.

*What to do:* Follow Sections 5 and 6 exactly. Before publishing, run `npm pack --dry-run` and submit that output as evidence you reviewed what would ship.

*Starter hint:*

```bash
# In your package directory
npm pack --dry-run   # read every line before proceeding
npm publish --access public
# Teammate verifies:
npx @yourusername/hello-agent "CS357 classmate"
```

*You've succeeded when:* A teammate can run `npx @yourusername/hello-agent` and receive the expected JSON output. Submit the dry-run output you reviewed before publishing.

**Exercise 3.** Version walk. Make a fix, bump with `npm version patch`, republish, and demonstrate that both the old and new versions remain installable by exact version number.

*What to do:* Edit `index.js` to change the output slightly. Run `npm version patch` (this edits `package.json` and creates a git tag), then `npm publish`. Then install each version explicitly.

*Starter hint:*

```bash
npm version patch     # bumps 0.1.0 -> 0.1.1
npm publish
# Verify both versions are installable
npm install @yourusername/hello-agent@0.1.0   # old version
npm install @yourusername/hello-agent@0.1.1   # new version
```

*You've succeeded when:* You can run both versions and observe different outputs. Write two sentences explaining what npm's version immutability guarantees for your users.

**Exercise 4.** CI release. Add the tag-triggered GHCR workflow to your image's repository, push a `v0.2.0` tag, and verify the GitHub Action published the image.

*What to do:* Create `.github/workflows/publish.yml` with the workflow from Section 7. Push a tag to trigger it.

*Starter hint:*

```bash
git tag v0.2.0
git push origin v0.2.0   # this triggers the workflow
# Then go to your repository's Actions tab to watch it run
# After it completes, verify:
docker pull ghcr.io/yourusername/hello-cs357:v0.2.0
```

*You've succeeded when:* The Actions tab shows a successful run triggered by your tag, and the image is pullable from GHCR. Identify in one sentence where the human gate lives in your pipeline (hint: it is not in the YAML).

**Exercise 5.** Audit exchange. Trade `npm pack --dry-run` outputs (or image layer listings via `docker history`) with another team and perform the pre-publish review on each other's artifacts.

*What to do:* Share your dry-run output with another team. They review it using the Model 2 framework (ship / exclude / investigate). You review theirs. Each team reports back anything concerning.

*Starter hint:* For Docker images: `docker history ghcr.io/otherteam/their-image:0.1.0` shows the layers and the commands that built each layer. Look for any `COPY` or `ADD` commands that might have included sensitive files.

*You've succeeded when:* Each team has submitted a written review of the other's artifact. Catching nothing after honest effort is also a valid result — but you must document that you looked.

---

# Part V: Python Package Publishing with pip

## Python Package Publishing with pip

Container images and npm packages are not the only way to ship Python software. The Python ecosystem has its own artifact format — the **wheel** — and its own registry — **PyPI** — that lets anyone install your code with a single `pip install`. This section walks through the full pip publishing pipeline from a `pyproject.toml` file to a live package on TestPyPI, with specific attention to the versioning tradeoffs that matter for rapidly-changing agent tooling.

---

### The pyproject.toml Structure

A modern Python package is defined by a single `pyproject.toml` file. The file has three sections you need to understand before publishing anything.

**`[build-system]`** tells pip which backend to use to turn your source code into a wheel:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

`hatchling` is the build backend. It reads the rest of `pyproject.toml` and knows how to produce a `.whl` file without any additional configuration. Other popular backends include `setuptools` and `flit`; the syntax is identical, only the backend name changes.

**`[project]`** is the package metadata that appears on PyPI and that `pip install` reads to resolve dependencies:

```toml
[project]
name = "my-agent"
version = "0.1.0"
description = "A local LLM research agent for CS357."
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
]
```

Every field here is a promise to your users. `name` must be globally unique on PyPI. `dependencies` are installed automatically when a user runs `pip install my-agent`, so list exactly what your code imports — no more, no less.

**`[project.scripts]`** creates command-line entry points that are installed into the user's PATH:

```toml
[project.scripts]
ask = "my_agent:main"
```

After `pip install my-agent`, a user can type `ask "What is photosynthesis?"` in any terminal and Python will call the `main()` function in the `my_agent` module. This is the same mechanism that makes `pytest`, `black`, and `ruff` available as terminal commands after you `pip install` them.

---

### The Build Pipeline

```bash
# Install the build frontend (one-time setup)
pip install build

# Produce both a wheel and a source distribution
python -m build
```

This command creates two files in a `dist/` directory:

```
dist/
  my_agent-0.1.0-py3-none-any.whl     # the wheel
  my_agent-0.1.0.tar.gz               # the source distribution (sdist)
```

A **wheel** (`.whl`) is a pre-built binary archive. `pip install` unpacks it directly with no compilation step, which makes installs fast and reproducible. A **source distribution** (`.tar.gz`) contains the raw source code and the build configuration; pip must run the build backend to install it, which requires the build tools to be available on the target machine. Wheels are preferred for distribution; sdists are the fallback for platforms where a pre-built wheel does not exist.

---

### TestPyPI vs. PyPI: Always Test First

PyPI is permanent. A version you publish cannot be unpublished after 72 hours, and mirrors cache everything immediately. **TestPyPI** (`test.pypi.org`) is a separate, identical registry used exclusively for testing the upload pipeline. Publishing to TestPyPI first lets you catch metadata errors, dependency conflicts, and `pyproject.toml` mistakes without polluting the real index.

```bash
# Upload to TestPyPI (safe; does not affect the real PyPI)
pip install twine
twine upload --repository testpypi dist/*
```

Twine will prompt for your TestPyPI username and password, or you can use an API token (recommended — generate one at https://test.pypi.org/manage/account/token/).

Installing from TestPyPI requires telling pip where to look, because TestPyPI is not in pip's default search path:

```bash
pip install --index-url https://test.pypi.org/simple/ my-agent
```

Note: if your package has dependencies from the real PyPI (like `requests`), add `--extra-index-url https://pypi.org/simple/` so pip can find them:

```bash
pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  my-agent
```

---

### Versioning: SemVer vs. Date-Based

The choice of versioning scheme communicates promises to your users.

**Semantic versioning (SemVer)** uses `MAJOR.MINOR.PATCH` and encodes a compatibility promise: patch bumps (`0.1.0` → `0.1.1`) fix bugs without changing the public API; minor bumps (`0.1.0` → `0.2.0`) add features while staying backward-compatible; major bumps (`0.1.0` → `1.0.0`) may break consumers who depend on the previous behavior. SemVer is the right choice for a stable library used by other code.

**Date-based versioning** (e.g., `2026.06.1`) encodes the release date rather than a compatibility promise. It is common for agent tooling that iterates rapidly and does not yet have a stable API — it tells users "this was released on this date" without implying backward compatibility. The tradeoff is that users cannot tell from the version number alone whether a new release will break their code.

For course labs, start with SemVer at `0.1.0` (the `0.x` range signals that the API is not yet stable), and bump to `1.0.0` only when you are ready to commit to a stable interface.

---

### Runnable Example: A Minimal pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-agent"
version = "0.1.0"
description = "A local LLM agent for CS357 with a CLI entry point."
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
]

[project.scripts]
# After pip install, users can run: ask "What is photosynthesis?"
ask = "my_agent:main"
```

After saving this file and running `python -m build`, verify the wheel exists:

```bash
ls dist/
# my_agent-0.1.0-py3-none-any.whl
# my_agent-0.1.0.tar.gz
```

---

### Critical Thinking Questions

**Question A.** What is the semantic difference between a wheel (`.whl`) and a source distribution (`.tar.gz`)? Describe a situation where a user's machine would receive the sdist instead of the wheel, and what additional tools must be present on that machine for the install to succeed.

[[___ Your answer here ___]]

*Hint: A wheel is pre-built and unpacked directly. A source distribution must be built on the target machine. What does "building" require that "unpacking" does not?*

[[MC]]
A project's API changes in a way that breaks all existing callers — for example, a function that previously returned a string now returns a list. Which version bump is appropriate under SemVer?
- ( ) Patch: `0.1.0` → `0.1.1`
- ( ) Minor: `0.1.0` → `0.2.0`
- (x) Major: `0.1.0` → `1.0.0`
- ( ) Date-based: `0.1.0` → `2026.06.1`

---

## Reflection Prompt

Publishing converts your work from something you control into something the world caches forever, in exchange for the chance that it helps someone.

**Personal level:** After shipping your first real artifacts today, what standard do you want your published name attached to? What does it mean to put your username on something that anyone can download and run?

**Technical level:** What single habit from this module most protects you from the irreversibility of publishing? How would you explain it to a new developer joining your team who has never published anything before?

**Societal level:** The free tier of GHCR and npm makes publishing essentially zero-cost for anyone with an internet connection. What does it mean for software quality — and software safety — that publishing barriers are now this low? Who benefits, and who bears the risk?

Write a combined reflection of 150–200 words addressing at least two of the three levels.

[[___ Your reflection here ___]]

---

→ Coming Up Next: Now that you can publish artifacts, the next activity looks at deploying them as live services — specifically using Cloudflare Workers and Pages to host your AI tools at a public URL without managing any servers.

---

## 10. Further Reading

- GitHub Docs, "Working with the Container registry": the GHCR authentication and visibility reference.
- npm Docs, "Creating and publishing scoped public packages" and the `package.json` reference.
- Docker Docs, "docker build-push-action" examples for CI publishing.
