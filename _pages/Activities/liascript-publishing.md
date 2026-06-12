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

# Part I: The Registry Mental Model

## 1. Registries, Names, and Tags

**A registry is a server that stores versioned, named artifacts and serves them to anyone (or anyone authorized) who asks.** You have been a consumer all semester: every `docker pull` and `npm install` was a registry transaction. Today you become a producer, and the producer's first job is naming. Container images are named `registry/namespace/name:tag`:

```
ghcr.io/yourusername/agent-eval:0.1.0     # GHCR: namespace is your GitHub username
docker.io/yourusername/agent-eval:0.1.0   # Docker Hub (the docker.io is implied)
```

The **tag** after the colon is a version label, and `latest` is just a tag like any other with no magic beyond convention. npm packages are named `package-name` or, better for coursework, **scoped** under your username as `@yourusername/package-name`, which guarantees no collision with the global namespace.

**Versions follow semver.** The convention `MAJOR.MINOR.PATCH` (like `1.4.2`) encodes a promise: patch bumps fix bugs, minor bumps add features compatibly, major bumps may break consumers. Registries treat published versions as immutable (npm will refuse to republish a version number you already used), which is why the discipline matters from your very first `0.1.0`.

## 2. Authentication: Tokens, Not Passwords

Every registry authenticates with **tokens** you generate, scope, and can revoke, never your account password. For GHCR, create a GitHub Personal Access Token with the `write:packages` scope (Settings, Developer settings, Personal access tokens); for Docker Hub, an access token from Account Settings, Security; for npm, `npm login` handles it interactively (with publish requiring a one-time password if you enable 2FA, which you should). The handling rules from the shell module apply with force: tokens live in environment variables or password managers, never in code, never in Dockerfiles, never in anything committed.

---

## Model 1: Read the Name

### Critical Thinking Questions

1. Decode `ghcr.io/billjr99/mcpproxy:0.3.1` into its four parts and state what each part tells a stranger before they pull anything.
2. A teammate publishes only `latest` tags, ever. Describe the failure that hits *their users* the day a breaking change ships, and the one-line habit that prevents it.
3. Why does npm's refusal to ever republish a version number protect *you* as a consumer? Connect to the reproducibility requirements of your course labs.

---

# Part II: Publishing Container Images

## 3. To GHCR, Step by Step

GHCR is the natural home for course images because it lives beside your code. From zero:

```bash
# 1. Authenticate (the PAT has write:packages scope; CR_PAT holds it)
echo $CR_PAT | docker login ghcr.io -u yourusername --password-stdin

# 2. Build with the full registry name, or tag an existing image
docker build -t ghcr.io/yourusername/agent-eval:0.1.0 .
#    (or) docker tag agent-eval:0.1.0 ghcr.io/yourusername/agent-eval:0.1.0

# 3. Push
docker push ghcr.io/yourusername/agent-eval:0.1.0

# 4. Verify from a clean slate, as a stranger would
docker rmi ghcr.io/yourusername/agent-eval:0.1.0
docker pull ghcr.io/yourusername/agent-eval:0.1.0
```

One GHCR-specific step trips everyone: new packages default to **private**. Visit the package's page on GitHub (your profile, Packages tab), open Package settings, and change visibility to public if you intend `docker pull` to work without authentication. Link the package to its source repository there too; consumers deserve to find your Dockerfile.

## 4. To Docker Hub

Identical verbs, different namespace, after creating a free account at hub.docker.com:

```bash
docker login                       # interactive; use your access token as the password
docker tag agent-eval:0.1.0 yourusername/agent-eval:0.1.0
docker push yourusername/agent-eval:0.1.0
```

Docker Hub is where unqualified names resolve (a plain `docker pull nginx` means Docker Hub), which gives it reach; GHCR gives you co-location with code and shared permissions with your repository. Publishing to both costs one extra `tag` and `push`, and many projects do exactly that.

[[MC]]
After pushing a new image to GHCR for the first time, a classmate reports that docker pull fails for everyone but you. The most likely cause is:
- ( ) GHCR requires a 24-hour propagation period
- ( ) The image tag must be latest for public pulls
- (x) New GHCR packages default to private visibility, and the package settings have not been changed to public
- ( ) Docker Hub credentials are interfering

---

# Part III: Publishing to npm

## 5. A Package from Zero

An npm package is a directory with a `package.json`; everything else is detail. A minimal, honest CLI utility:

```bash
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
try {
  const name = process.argv[2] || "world";
  console.log(JSON.stringify({ greeting: `hello, ${name}`, from: "CS357" }));
} catch (e) {
  console.error(`[hello-agent:main] ${e}`);
  console.error(e.stack);
  process.exit(1);
}
```

Three fields deserve attention. `bin` is what makes `npx @yourusername/hello-agent` work as a command, the same mechanism that installed every agent CLI in this course. `files` is an allowlist of what ships; without it you may publish your scratch files, logs, and worse (this is the cleaner inverse of `.npmignore`). `license` is not decoration; unlicensed code is unusable code, and MIT is the course default unless you have reasons.

## 6. Dry Run, Publish, Verify

```bash
npm login                          # once per machine
npm pack --dry-run                 # SHOWS exactly what would ship; read it
npm publish --access public       # scoped packages need --access public the first time
npx @yourusername/hello-agent Bill # verify as a stranger
npm version patch                  # 0.1.0 -> 0.1.1 (edits package.json, makes a git tag)
npm publish                        # ship the fix
```

`npm pack --dry-run` is the publish gate in command form: it lists every file about to go public, and reading that list before every publish is the habit that prevents the credential-in-a-tarball incidents you can find in any year's security news.

## 7. Automating with CI (and Why the Gate Stays Human)

Once publishing works by hand, a GitHub Actions workflow can do it on every tagged release. The container pattern, from the course stack's own deployment:

```yaml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}
```

The npm analog swaps in `npm ci && npm publish` with an `NPM_TOKEN` repository secret. Notice what triggers it: a *tag you push deliberately*, not every commit, so the human gate survives automation as the decision to tag. That design is the AI-maker module's CI lesson and the governance assignment's publication gate, implemented in seven lines of YAML.

## 8. Publishing Responsibly

Four habits, briefly, that separate professional publishing from littering. **A README that answers three questions** (what is this, how do I install it, how do I use it in thirty seconds) ships with everything. **Secrets audits precede every push**: the dry-run file list, plus a `grep` for `key`, `token`, and `password` over what ships. **You publish only what you may**: course materials, datasets with licenses, and other people's code all carry terms, and a public registry is the worst place to discover you misread them. **Unpublishing barely exists**: npm restricts unpublish after 72 hours and mirrors cache everything, so the moment of `push` is effectively irreversible, which is exactly why it sits behind a confirmation gate in our governance framework and in this course's rules.

---

## Model 2: The Pre-Publish Review

A teammate's `npm pack --dry-run` output includes `index.js`, `README.md`, `notes/todo.md`, `config.json`, and `.env.example`.

### Critical Thinking Questions

4. Rule on each file: ship, exclude, or investigate first, with one clause of reasoning each. Which one demands the investigation, and what are you looking for inside it?
5. Write the `files` allowlist that produces the correct tarball, and explain why the allowlist beats an ignore-list for safety.
6. The publish succeeds and, two days later, the teammate realizes `config.json` held a real endpoint URL they would rather not share. Enumerate their actual options, honestly, and the lesson about gates.

---

# Part IV: Practice

## 9. Exercises

1. *First image, two homes.* Containerize a trivial service (the Docker module's Dockerfile suffices), publish it to GHCR, make it public, and pull it from a teammate's machine. Optionally mirror it to Docker Hub. Submit the names, the commands, and the teammate's pull transcript.
2. *First package.* Publish a scoped npm package with a working `bin`, a real README, and a `files` allowlist. A teammate verifies with `npx`. Submit the dry-run output you reviewed before publishing.
3. *Version walk.* Make a fix, bump with `npm version patch`, republish, and demonstrate that both versions remain installable by exact version. Two sentences on what immutability buys your users.
4. *CI release.* Add the tag-triggered GHCR workflow to your image's repository, push a `v0.2.0` tag, and verify the action published it. Identify, in one sentence, where the human gate lives in your pipeline.
5. *Audit exchange.* Trade dry-run outputs (or image layer listings via `docker history`) with another team and perform the pre-publish review on each other's artifacts. Report anything caught; catching nothing after honest effort is also a result.

---

## Reflection Prompt

In your notebook: publishing converts your work from something you control into something the world caches forever, in exchange for the chance that it helps someone. After shipping your first real artifacts today, what standard do you want your published name attached to, and what single habit from this module most protects it?

---

## 10. Further Reading

- GitHub Docs, "Working with the Container registry": the GHCR authentication and visibility reference.
- npm Docs, "Creating and publishing scoped public packages" and the `package.json` reference.
- Docker Docs, "docker build-push-action" examples for CI publishing.
