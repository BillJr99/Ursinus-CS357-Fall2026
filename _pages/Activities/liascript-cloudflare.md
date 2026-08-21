<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-cloudflare.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-cloudflare.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Hosting with Cloudflare: Workers, Pages, and Wrangler

Your local stack is private by design, which is its virtue and its limit: nothing on `localhost` can be shown to a collaborator, demoed at a poster session, or used by anyone else. **Cloudflare's developer platform** fills that gap with a generous free tier: **Pages** hosts static sites, **Workers** runs serverless code at the edge, and **Wrangler** is the CLI that drives both from your terminal. This tutorial goes from no account to a deployed, secret-bearing API. The arc: **the platform map $\rightarrow$ Wrangler from zero $\rightarrow$ your first Worker $\rightarrow$ secrets and configuration $\rightarrow$ a Pages site $\rightarrow$ what belongs at the edge versus at home $\rightarrow$ automating the deploy safely (CI, secrets, and guardrails)**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisites: the shell module, Node.js 20+, a free Cloudflare account (dash.cloudflare.com), and the publishing module's mindset: **deploying is publishing, so a human runs every deploy command**, our external-publication gate again. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Cloudflare Worker** | A JavaScript (or TypeScript or Python) function that runs on Cloudflare's global network in response to HTTP requests: no server to rent or manage, no container to keep alive | `wrangler deploy` publishes your `src/index.js` as a live API endpoint at `https://hello-worker.yourname.workers.dev` |
| **Cloudflare Pages** | A hosting service for static websites (HTML, CSS, JavaScript) that deploys instantly from a directory or a GitHub repository | `wrangler pages deploy ./dist` publishes your built project at `https://cs357-demo.pages.dev` |
| **Wrangler** | The official CLI tool for working with Cloudflare Workers and Pages; it scaffolds projects, runs them locally, deploys them, and manages secrets | `npx wrangler dev` starts a local version of your Worker at `localhost:8787` |
| **`wrangler.toml`** | The configuration file for a Cloudflare Worker project; sets the Worker's name, entry point, and pinned runtime version | `name = "hello-worker"` sets the subdomain; `compatibility_date` pins runtime behavior |
| **Worker secret** | A sensitive value (API key, token) stored on Cloudflare's servers and injected into the Worker at runtime, never written to any file or repository | `npx wrangler secret put UPSTREAM_API_KEY`, the value is entered interactively and stored server-side only |
| **Edge network** | Cloudflare's globally distributed set of data centers that run Workers close to whoever is making the request, reducing latency by running code near the user rather than in one central location | A request from a user in Tokyo is handled by a Cloudflare data center in Asia, not by a server in Virginia |
| **CI/CD pipeline** | Continuous Integration / Continuous Deployment, an automated sequence (build, test, deploy) that a service like **GitHub Actions** runs whenever code changes, so shipping is a repeatable pipeline rather than a person typing commands | A push to `main` triggers a workflow that runs your tests and then calls your deploy script, no human retyping `wrangler deploy` |
| **Deploy script vs. workflow** | The **workflow** (YAML) *orchestrates*: it says when to run and in what order. The **deploy script** (`deploy.sh`) holds the actual deploy *logic*, so it is testable and runnable locally, not trapped inside CI-only YAML | `deploy.yml` checks out the code and runs `./deploy.sh`; `deploy.sh` is the same script you can run on your laptop |
| **GitHub secret vs. variable** | A **secret** is an encrypted value (a token) that CI injects into the run and masks in logs; a **variable** is a plain, non-sensitive value visible in the UI. Secrets can be scoped to a repository or, more tightly, to an **environment** | `CLOUDFLARE_API_TOKEN` is an environment secret; `WORKER_NAME` is a plain variable |
| **Log masking** | CI automatically replaces any registered secret value with `***` in the log output, but only if you never deliberately print it. `echo "$TOKEN"` or `set -x` can still leak it around the mask | The token appears as `***` in the Actions log unless a careless `echo` reveals its characters |
| **OIDC / federated token** | A short-lived, per-run identity token the CI provider mints and signs. The cloud trusts it by verifying the **signature** against the provider's **public keys**, plus the **`audience`** and **`subject`** claims; no long-lived key is ever stored | GitHub issues a token whose `subject` says "repo X, branch `main`, environment `production`"; AWS verifies it and hands back credentials that expire in minutes |
| **Least privilege** | Grant an identity exactly the permissions it needs and no more: a deploy token scoped to "edit Workers on this one account," never an all-powerful Global API Key | A scoped Cloudflare API token can deploy a Worker but cannot read your billing or delete your DNS |
| **Deployment guardrail** | A control that governs *who* can deploy, *from where*, and *with whose approval*: environment protection with required reviewers, an actor allowlist, a branch restriction, or a concurrency/rate limit | The workflow refuses to deploy unless the actor is on the allowlist, the branch is `main`, and a reviewer approves the `production` environment |
| **Idempotent / non-interactive script** | A script that produces the same end state whether run once or five times, and that never pauses for keyboard input, mandatory in CI, where there is no human to answer a prompt | `deploy.sh` creates the KV namespace only if it does not already exist, and passes assume-yes flags so nothing waits on `read` |

---

### Before You Start

**What you need:** A free Cloudflare account and Node 20+ for `wrangler`. No credit card, and everything here fits the free tier.

**What you will have at the end:** a Worker and a Pages site deployed to a public URL you own.

Work through the sections in order; each one builds on the last, and the code blocks are meant to be run as you reach them, not read past.

---

# Part I: The Platform and the Tool

In this part, you will map the three nouns that make up Cloudflare's developer platform and install Wrangler, the CLI that drives all of them, because understanding what each service does and does not do is the prerequisite for placing the right thing in the right place.

## 1. The Map

Workers are like serverless microwave ovens: they heat your code on demand, you do not manage the kitchen. When a request comes in, Cloudflare runs your function on the nearest server, returns the result, and the function stops running. You pay nothing for idle time, you never SSH into a machine, and Cloudflare handles TLS certificates, load balancing, and global distribution automatically. The free tier handles enough requests per day to cover any course project comfortably.

Three nouns cover the platform for our purposes:

A **Worker** is a JavaScript (or TypeScript, or Python) function that runs on Cloudflare's edge network in response to HTTP requests: no server to rent, no container to babysit, scaling and TLS handled for you, with a free tier (currently on the order of one hundred thousand requests per day) that comfortably covers any course project.

**Pages** hosts static sites (HTML, CSS, JS, your built React app) on the same network, free for ordinary use, and can attach Workers-style functions for the dynamic bits.

Around them sit storage primitives you may eventually want, of which **KV** (a key-value store bindable into a Worker, like a simple database your Worker can read and write) is the one worth knowing exists today.

**Wrangler** is the command-line interface to all of it: it scaffolds projects, runs them locally, deploys them, and manages secrets, which makes it the `docker` of this module. The framing for our course: the local stack is where private things live; Cloudflare is where *shareable, non-sensitive* things go, and deciding which is which is a governance exercise you have already trained for.

## 2. Wrangler from Zero

The following commands install Wrangler, connect it to your Cloudflare account, and confirm the connection. Run them in order; `wrangler login` will open a browser tab to complete authorization.

```bash
# Install Wrangler globally (or use npx wrangler to run without installing)
npm install -g wrangler

# Confirm it is installed
wrangler --version

# Log in - this opens a browser tab; authorize Cloudflare to connect to your account
wrangler login

# Confirm your account is connected
wrangler whoami
```

`wrangler login` stores an OAuth credential on your machine, scoped to your Cloudflare account. On shared machines (like a lab computer), run `wrangler logout` when you are finished, the same hygiene rule as any other credential.

With the platform map clear and Wrangler installed, Part II walks you from zero to a deployed Worker, a complete round trip from laptop to public URL in under ten minutes.

---

# Part II: Your First Worker

In this part, you will scaffold, run locally, and deploy a JSON API Worker, then add secrets using the pattern that keeps keys out of your repository, so you understand both what a Worker is and how to keep it secure before you build anything real.

## 3. Scaffold, Run Locally, Read the Config

These commands scaffold a new Worker project from the official template and start the local development server. The local server hot-reloads on every save, so you can edit and test without redeploying.

```bash
# Create a new Worker project from the official template
npm create cloudflare@latest hello-worker
# When prompted: choose "Hello World" Worker, JavaScript, skip git questions if unsure

# Enter the project directory
cd hello-worker

# Start the local development server (hot-reload: edit, save, test, repeat)
npx wrangler dev
# Your Worker runs at http://localhost:8787 - open it in a browser or use curl
```

`wrangler dev` runs your Worker in a faithful local simulation with live reload: edit, save, curl, repeat, the same inner loop as everything else this semester. The project's identity lives in its configuration file (`wrangler.toml`, or `wrangler.jsonc` in newer scaffolds; same keys, different syntax):

```toml
name = "hello-worker"            # becomes the subdomain: hello-worker.<you>.workers.dev
main = "src/index.js"            # the entry point file that Cloudflare runs
compatibility_date = "2026-06-01"  # pins runtime behavior to a specific date
```

That `compatibility_date` line deserves a pause: it is the platform's version-pinning mechanism, freezing runtime semantics as of a specific date so future Cloudflare platform updates cannot silently change your deployed behavior. This is the same reproducibility instinct as pinning an image tag; you are saying "run my code against the platform as it existed on this date."

## 4. The Code Shape, and a Real Example

A Worker exports a `fetch` handler: an HTTP request comes in, your function runs, an HTTP response goes out. Everything else is your logic. Here is a complete, production-quality example with routing and error handling:

The following Worker exports a `fetch` handler with three routes and error handling. Read the comments inside the code; they explain what each piece does and why it is structured this way.

```javascript
// src/index.js: a tiny JSON API with three routes and error handling
export default {
  async fetch(request, env, ctx) {
    try {
      // Parse the incoming request URL to check the path
      const url = new URL(request.url);

      // Route 1: health check, useful for confirming the Worker is running
      if (url.pathname === "/health") {
        return Response.json({ ok: true, at: new Date().toISOString() });
      }

      // Route 2: greeting, reads a query parameter (?name=Alice)
      if (url.pathname === "/greet") {
        const name = url.searchParams.get("name") || "world";
        return Response.json({ greeting: `hello, ${name}`, course: "CS357" });
      }

      // Default: return a 404 for any path we do not handle
      return Response.json({ error: "not found" }, { status: 404 });

    } catch (e) {
      // Course exception pattern: log details for you, clean message for the caller
      console.error(`[hello-worker:fetch] ${e}`);
      return Response.json({ error: "internal error" }, { status: 500 });
    }
  },
};
```

Note the `env` parameter: this is where secrets and configuration variables arrive from Cloudflare, covered in the next section. The `ctx` parameter provides lifecycle hooks for advanced patterns like waiting for a background task to finish before the Worker shuts down.

## 5. Deploy, Then Secrets

The following commands deploy your Worker to Cloudflare's global network and immediately test all three routes. The first `wrangler deploy` command may prompt you to confirm; this is the human gate before publishing to a public URL.

```bash
# Deploy to Cloudflare's network (prompts to confirm, then shows the live URL)
npx wrangler deploy
# Output: Deployed hello-worker -> https://hello-worker.<your-subdomain>.workers.dev

# Test your live Worker immediately with curl
curl https://hello-worker.<your-subdomain>.workers.dev/greet?name=Bill
# Expected: {"greeting":"hello, Bill","course":"CS357"}

curl https://hello-worker.<your-subdomain>.workers.dev/health
# Expected: {"ok":true,"at":"2026-06-21T..."}

curl https://hello-worker.<your-subdomain>.workers.dev/anything-else
# Expected: {"error":"not found"} with HTTP status 404
```

That is the entire distance from laptop to public URL. Now the part everyone gets wrong without instruction:

**Configuration that is not secret** (model names, feature flags, environment names) goes in the config file's `[vars]` table. This is visible in your repository and committed to version control, intentionally, since it is not sensitive.

**Secrets** (API keys, tokens, passwords) go through Wrangler's secret store and *never* touch any file:

```bash
# The value is entered interactively (not typed on the command line where it could appear in shell history)
# It goes directly to Cloudflare's secure storage, not to any local file
npx wrangler secret put UPSTREAM_API_KEY
```

```toml
# wrangler.toml (committed to your repository; only non-sensitive values here)
[vars]
MODEL_NAME = "claude-3-5-sonnet-20241022"    # safe to commit: not a secret
ENVIRONMENT = "production"                    # safe to commit: not a secret
```

```javascript
// In the handler, secrets and vars both arrive on the env object, same syntax, different storage
const key = env.UPSTREAM_API_KEY;            // secret: stored by wrangler secret put, never in files
const model = env.MODEL_NAME;                // plain var: stored in wrangler.toml, committed to repo
```

For local development, secrets go in a `.dev.vars` file (same syntax as a `.env` file). Add `.dev.vars` to `.gitignore` in the same breath as creating it.

To watch your live Worker's logs in real time (like `docker logs -f` but for the cloud):

```bash
npx wrangler tail    # streams live log output from your deployed Worker
```

A teammate puts an API key in the [vars] section of wrangler.toml "because env reads both the same way." The flaw is:

[( )] Workers cannot read vars at runtime; only secrets injected at deploy time are accessible via the `env` object
[(X)] wrangler.toml is committed to the repository, so the key becomes part of the project's public record; secrets must go through wrangler secret put, which stores them server-side only
[( )] vars and secrets are both stored server-side by Cloudflare, so committing the key to `wrangler.toml` has no security implication
[( )] Secrets are faster to read than vars because they are stored in Cloudflare's KV store with lower latency

With a live Worker API deployed and secrets stored correctly, Part III shows how to host your static frontend on Pages and (most importantly) draw the line between what belongs at the edge and what must stay on localhost.

---

# Part III: Pages, and Drawing the Line

In this part, you will deploy a static site to Pages and apply the governance principle that has run throughout this course: every component should live where its data handling and sensitivity requirements dictate, not where it is most convenient to put it.

## 6. A Pages Site in Two Commands

Anything static (a project landing page, a built React artifact, your team's demo write-up, a visualization) deploys to Pages directly from a local directory:

```bash
# Build your static site first (if needed), then deploy the output directory
npx wrangler pages deploy ./dist --project-name=cs357-demo
# Output: -> https://cs357-demo.pages.dev

# Every subsequent deploy creates a new version with a unique preview URL:
# -> https://abc123.cs357-demo.pages.dev  (preview link for this specific deploy)
# -> https://cs357-demo.pages.dev         (stable production URL, always latest)
```

The first run creates the project on Cloudflare; later runs create new deployments, each with a unique preview URL alongside the stable production URL. This gives you free per-version review links; share the preview URL with a teammate to get feedback before promoting to production.

The alternative, equally legitimate path is Git integration through the Cloudflare dashboard: connect your repository, set the build command (`npm run build` or similar), and every push to `main` triggers a new deployment, with the human gate moving to the merge decision.

Custom domains, if you have one, attach to either Workers or Pages through the Cloudflare dashboard in a few clicks, TLS included and automatic.

## 7. What Belongs at the Edge

Workers are like serverless microwave ovens: fast, on-demand, zero management, but you would not try to bake a roast in a microwave. The edge is the right place for fast, stateless, public-facing code; it is the wrong place for heavy computation, large files, or anything subject to your data-handling agreements.

The edge is the right home for the **shareable shell**:
- Demo frontends and project documentation pages
- Thin public APIs that return static or lightweight responses
- A **gateway facade** in front of an LLM provider: the Worker holds the provider's API key as a secret and proxies requests from the browser, so the key never ships to a browser client where it could be extracted

The local stack remains the right home for **inference and data**:
- Model serving and anything computationally expensive
- Anything touching course data subject to our data-handling rules
- Agent workloads that need filesystem access, persistent state, or long-running computation

A clean pattern for course project demos combines both: a Pages frontend, a Worker holding one API key as a secret and proxying to a rate-limited provider free tier, and the heavyweight private work staying on localhost. Your governance document should be able to point at each component and say explicitly why it lives where it lives.

---

## Model 1: Placement Review

A team proposes: (a) their project's documentation site built from Markdown, (b) a Worker that accepts student-submitted essays and forwards them to a cloud LLM for scoring, (c) their RAG knowledge base built from a professor's licensed course materials.

Before ruling, the Manager ensures the team has named the deciding principle for each component, not just an intuition.

### Critical Thinking Questions

**Question 1.** Rule on each placement (edge, local, or "redesign first"), with the deciding principle named for each. Draw on the data-handling and licensing commitments from earlier modules.

[[___ Your answer here ___]]

*Hint:* For (a): Is documentation sensitive? Does it contain anything you would not want publicly indexed? For (b): Who owns the essay content? What are the privacy implications of forwarding student work to a third-party cloud service? Does the professor whose course this is know about and consent to this data flow? For (c): What does "licensed course materials" mean for redistribution through a public API endpoint?

**Question 2.** For (b), the team argues the Worker holds no data since it only forwards. What two questions does our governance framework still require them to answer before deploying?

[[___ Your answer here ___]]

*Hint:* "We don't store it" is a claim about *your* system, but what about the third-party LLM provider the Worker forwards to? Also: the essay author (the student) - did they consent to having their work sent to a cloud service for automated scoring? These are the two questions.

**Question 3.** Sketch the hybrid architecture that lets the team demo publicly while keeping (c) entirely local. Which single secret exists, and where does it live?

[[___ Your answer here ___]]

*Hint:* The public part (Pages frontend + Worker gateway) handles user requests and authenticates to an LLM provider. The private part (local RAG system) handles the knowledge base. But the Worker needs to call something: what is the architecture if the heavy RAG work must stay on a local machine? Where does the one secret that bridges the gap live, and how is it protected?

---

> **Common Misconception:** Students often assume that because a Worker is serverless (no server to manage, no container to maintain), it is also stateless in the sense that nothing persists between users or between requests. This is true for in-memory variables (each request gets a fresh execution context), but Cloudflare provides persistent storage primitives like KV that Workers can bind to. More importantly, the distinction between "does not persist" and "does not store" is crucial for governance: a Worker that forwards data to a third-party LLM provider does not store data itself, but it does transmit data to a service that may log, train on, or retain it. "We use a Worker, so we don't store data" is not a complete data-handling answer; it is the beginning of one.

---

# Part IV: Automating the Deploy - Safely

In this part, you will turn the manual `wrangler deploy` from Part II into an automated CI/CD pipeline, and, more importantly, keep it *safe*: deploy logic in a script rather than trapped in YAML, cloud credentials that are scoped and short-lived, and guardrails that decide who may deploy, from which branch, with whose approval. Everything here is vendor-neutral in principle; we use **GitHub Actions + Cloudflare** as the concrete example, and note where a cloud like AWS does it differently.

> **Before you begin:** everything in this part uses **your own sandbox account** and throwaway projects. **Never commit a token, API key, or password to a repository**, not even in a branch, not even briefly. If you create any `.env`, `.dev.vars`, or credentials file while following along, add it to `.gitignore` *before* you `git add` anything. A real secret in git history is compromised even after you delete it.

## 8. The Human Gate Moves Into the Pipeline

Every deploy in this course so far has ended with *you* typing `wrangler deploy` and confirming the prompt, the "a human runs every deploy" governance gate. Automation does not delete that gate; it **moves it into the pipeline**. Instead of trusting that a person eyeballed the command, we encode the checks (right branch, allowed person, reviewer approval) as rules the pipeline enforces on every run.

The first principle of a safe pipeline is **where the deploy logic lives**. A tempting mistake is to write all the deploy steps as inline commands in the workflow YAML. That code is then trapped: you cannot run it on your laptop, you cannot unit-test it, and every fix requires a full CI round trip. Instead, put the logic in a **deploy script** the workflow merely *orchestrates*.

The following `deploy.sh` is the entire deploy logic. Read the top three lines and the comments: it fails fast, it reads the token *from the environment* (never a hardcoded string), and it never prints the token.

```bash
#!/usr/bin/env bash
# deploy.sh - the deploy LOGIC. The workflow only decides WHEN to run this.
# Runs identically on your laptop and in CI, which makes it testable.
set -euo pipefail          # -e: stop on any error  -u: error on unset var  -o pipefail: catch errors mid-pipe

# The token arrives in the environment (from `wrangler secret`-style CI injection),
# NOT as a command-line argument and NOT hardcoded here. Fail loudly if it is missing.
: "${CLOUDFLARE_API_TOKEN:?CLOUDFLARE_API_TOKEN is not set}"

WORKER_NAME="${WORKER_NAME:-<YOUR-WORKER-NAME>}"   # TODO: set via a plain (non-secret) variable

echo "Deploying ${WORKER_NAME}..."   # safe: prints the NAME, never the token

# Idempotent + non-interactive: wrangler reads CLOUDFLARE_API_TOKEN from the env automatically.
# </dev/null guarantees no step can block waiting for keyboard input in CI.
npx wrangler deploy --name "${WORKER_NAME}" </dev/null

echo "Deploy complete."
```

The workflow that runs it is short, because the logic is elsewhere:

```yaml
# .github/workflows/deploy.yml  (skeleton; full guarded version appears in Section 11)
- name: Deploy
  run: ./deploy.sh          # <- the workflow orchestrates; the script does the work
  env:
    CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}   # injected, then masked in logs
    WORKER_NAME: ${{ vars.WORKER_NAME }}                        # plain, non-secret variable
```

## Model 2: The CI Deploy Pipeline

A push (or a manual dispatch) sets off a chain of steps. The security of the whole thing is not in any one step; it is in the **gates** the request must pass before the deploy step ever runs. Study where each gate sits.

```text
   Developer                         GitHub Actions runner                    Cloudflare
   ---------                         ---------------------                    ----------
   git push  -------------->  +-------------------------------+
   (or manual  workflow_      |  GATE 1: branch == main?       |  no -> stop
    dispatch)                 |  GATE 2: actor on allowlist?   |  no -> stop
                              |  GATE 3: environment reviewer  |  no -> wait for approval
                              |          approved "production"?|
                              `---------------+---------------+
                                              | all gates pass
                                              v
                              +-------------------------------+
                              |  inject CLOUDFLARE_API_TOKEN   |   (masked as *** in logs)
                              |  run ./deploy.sh               | -----------> wrangler deploy -> live Worker
                              `-------------------------------+
```

The deploy step at the bottom is trivial; it is one script call. Everything valuable is the three gates above it, and each is a separate control you configure once and the pipeline enforces forever.

### Critical Thinking Questions

**Question 4.** In Part II, the safety of a deploy rested on a human seeing the `wrangler deploy` confirmation prompt and choosing to proceed. In the pipeline above, that prompt is gone (the script runs non-interactively). For each of the three gates, name *which part of the old human judgment it replaces*: what was the person implicitly checking that the gate now checks explicitly?

[[___ Your answer here ___]]

*Hint:* When a careful person ran a deploy by hand, they implicitly confirmed three things: that they were on the right branch (not a half-finished feature), that *they personally* were authorized to ship, and (on a team) that someone had signed off. Map each of those to Gate 1, Gate 2, and Gate 3.

**Question 5.** A teammate argues it is simpler to put all the deploy commands directly in the workflow YAML and skip the `deploy.sh` file. Give two concrete costs of that choice: one about testing/debugging and one about what happens when the deploy breaks at 11pm before a demo.

[[___ Your answer here ___]]

*Hint:* If the logic is only in YAML, how do you reproduce a failure on your own machine? How many push-wait-read-log cycles does each one-character fix take, versus editing and re-running a script locally?

---

## 9. Secrets in CI: Injected, Masked, Never Printed

In Part II, `wrangler secret put` stored a secret on Cloudflare for the *running Worker*. CI needs a different secret: the **deploy credential** the pipeline uses to *authenticate to Cloudflare in the first place*. That is the `CLOUDFLARE_API_TOKEN`, and it lives in GitHub's encrypted secret store, never in the repository.

GitHub gives you three places to put values, and choosing correctly is the whole game:

| Where | Sensitive? | Scope | Use it for |
|-------|-----------|-------|------------|
| **Repository secret** | Yes (encrypted, masked) | Every workflow in the repo | A credential many workflows share |
| **Environment secret** | Yes (encrypted, masked) | Only jobs targeting that environment (e.g. `production`), *and* only after the environment's protection rules pass | The deploy token: tie it to the protected `production` environment so approval is required to use it |
| **Variable** | No (plain, visible) | Repo or environment | Non-secret config: the Worker name, the account subdomain |

**The one rule that prevents most leaks:** a registered secret is automatically masked as `***` in logs, *unless you print it yourself*. These two lines defeat the mask and leak the token into a world-readable log:

```bash
echo "Deploying with token $CLOUDFLARE_API_TOKEN"   # NEVER - prints the secret verbatim
set -x                                               # DANGEROUS in a script that touches secrets:
                                                     #    it echoes every command with its expanded values
```

Instead, prove a secret arrived without revealing it, the same discipline as Exercise 2, now for CI:

```bash
# Confirms the token is present without exposing a single character of it
if [ -n "${CLOUDFLARE_API_TOKEN:-}" ]; then
  echo "CLOUDFLARE_API_TOKEN is set (length ${#CLOUDFLARE_API_TOKEN})."
else
  echo "CLOUDFLARE_API_TOKEN is missing." >&2; exit 1
fi
```

And local development still uses `.dev.vars` / `.env`, which are **git-ignored**, always:

```bash
# .gitignore - add these the moment the files could exist, before your first git add
.dev.vars
.env
*.local
```

Your deploy script needs the Cloudflare token, and you want a required reviewer to approve every production deploy. The correct place to store the token is:

[( )] Hardcoded in `deploy.sh` so the script is self-contained and works anywhere
[( )] A plain repository *variable*, so teammates can see it is configured
[(X)] A repository *environment secret* attached to a protected `production` environment, so it is encrypted, masked in logs, and only usable after the environment's approval rule passes
[( )] In `wrangler.toml`'s `[vars]` table, since the Worker reads everything from `env` anyway

## 10. Least Privilege and Short-Lived Credentials

A deploy identity should be able to do exactly one thing: deploy. The classic failure is using an all-powerful credential (Cloudflare's **Global API Key** or an AWS root/administrator key), "just to get it working," and never tightening it. If that credential leaks from a CI log or a compromised dependency, the blast radius is your entire account.

**Cloudflare, concretely:** create a **scoped API token** (dashboard -> My Profile -> API Tokens) from a template limited to *Edit Cloudflare Workers*, restricted to the one account you deploy to. It can publish your Worker; it cannot read billing, touch DNS, or delete other projects. A practical workflow is **verify-broad-then-tighten**: if you are unsure which permissions a deploy needs, start slightly broad, confirm the deploy works, then remove permissions until it *just* stops working and add the last one back.

**The transferable principle: short-lived beats long-lived.** A scoped token is still a *long-lived* secret sitting in a store. The stronger pattern, supported by clouds like AWS, is **OIDC federation**: the CI provider mints a fresh, signed identity token *for that one run*, and the cloud exchanges it for credentials that expire in minutes. **No key is ever stored.** Here is how the trust actually works:

```text
  GitHub Actions run                          Identity Provider          Cloud (AWS STS)
  ------------------                          (token.actions.           ---------------
                                               githubusercontent.com)
  1. job requests an OIDC token  ----------->  mints + SIGNS a token
     (id-token: write)                          with claims:
                                                  aud = sts.amazonaws.com
                                                  sub = repo:ORG/REPO:
                                                        environment:production
  2. present signed token  ----------------------------------------->  a) fetch provider PUBLIC KEYS (JWKS)
                                                                        b) verify SIGNATURE  -> forged? reject
                                                                        c) check AUDIENCE matches      reject if not
                                                                        d) check SUBJECT matches the
                                                                           role's trust policy         reject if not
                                                                              | all checks pass
                                                                              v
  3. <---------------------  short-lived credentials (expire in minutes) <- assume-role
```

Three claims do the security work, and **the identity provider (not your workflow) stamps them**, which is why they cannot be forged:

- **Signature:** the cloud verifies the token against the provider's *public* keys (its JWKS). Anyone can fetch the public keys, but only the provider holds the private key, so a token it did not mint fails verification.
- **`audience` (`aud`):** who the token is *for*. Binding it to the specific cloud endpoint stops a token minted for one service from being replayed against another.
- **`subject` (`sub`):** *which* workload this is, encoded as `repo:ORG/REPO:ref:refs/heads/main` or `repo:ORG/REPO:environment:production`. The cloud's trust policy pins the exact subject it will accept.

The **classic, dangerous mistake** is a loose subject scope. A trust policy that accepts `repo:ORG/*` (or worse, `*`) will hand production credentials to *any* repository (or any branch, or a pull request from a fork). Pin the subject to the exact repo **and** branch/environment you deploy from:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "// TODO pin the EXACT repo + environment, never a wildcard": "",
        "token.actions.githubusercontent.com:sub": "repo:<ORG>/<REPO>:environment:production"
      }
    }
  }]
}
```

And the *permission* policy the role grants should be least-privilege too, only the actions the deploy performs, never `"Action": "*"`:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:PutObject", "cloudfront:CreateInvalidation"],
    "Resource": ["arn:aws:s3:::<YOUR-SITE-BUCKET>/*", "arn:aws:cloudfront::<ACCOUNT_ID>:distribution/<DIST_ID>"]
  }]
}
```

> **Common Misconception:** "OIDC is complicated, so a stored token must be the simpler and therefore safer choice." The opposite is usually true. A stored long-lived token is a standing liability: it can leak, and until someone notices and rotates it, an attacker has your access. An OIDC token is minted per run, expires in minutes, and is bound by its subject to one repository and branch. The *setup* is a bit more involved; the *ongoing risk* is far lower. Cloudflare's Wrangler flow uses a scoped API token today, so you still hold one carefully-scoped secret, but the direction every mature pipeline moves is: smallest scope, shortest life, no key at rest.

### Critical Thinking Questions

**Question 6.** An OIDC trust policy is set to accept subject `repo:<ORG>/*`. Describe a concrete attack: what could a student who creates *any* new repository under that organization do, and what exactly did the wildcard give them that a pinned subject would not?

[[___ Your answer here ___]]

*Hint:* If the cloud accepts a token from *any* repo in the org, then the security no longer depends on *which* code is deploying. What could someone put in a brand-new repo's workflow, and whose credentials would it run with?

**Question 7.** Explain why the cloud verifying the token's signature against the provider's *public* keys is enough to trust it, even though those public keys are, by definition, public and anyone can read them. What does the provider hold that no one else does?

[[___ Your answer here ___]]

*Hint:* Signatures are made with a private key and checked with the matching public key. Reading the public key lets you *verify* a signature; it does not let you *create* one. Who is the only party that can produce a signature the public key will accept?

---

## 11. Guardrails: Who May Deploy, From Where, With Whose Approval

With credentials scoped, the last layer is governance: constraining *who* can trigger a deploy and *under what conditions*. Four guardrails, from simplest to strongest:

- **Branch restriction**: deploy only from a trusted branch, so an unreviewed feature branch can never reach production. (`on: push: branches: [main]`, and/or check `github.ref` in the job.)
- **Actor allowlist**: the job runs only if the triggering user is on an explicit list, binding deploys to specific people. (`if: contains(fromJSON('["<USER1>","<USER2>"]'), github.actor)`.)
- **Environment protection + required reviewers**: target a named `environment:` (e.g. `production`); a listed reviewer must approve before the job proceeds, and the environment's secrets are unavailable until they do. **Caveat, phrased to stay true over time:** the availability of required-reviewer protection depends on your repository's visibility and your account's plan tier; on some tiers it is limited to public repositories. Treat it as "check what your repo/plan supports right now," not a fixed guarantee.
- **Manual dispatch vs. auto-trigger**: `workflow_dispatch` requires a person to click *Run* (or call the API), keeping a human in the loop; a `push` trigger deploys automatically on every merge. Choose deliberately: auto-trigger is convenient but removes the last manual checkpoint, so it belongs *only* behind the gates above.
- **Rate / concurrency limit**: a `concurrency:` group cancels or queues overlapping runs so two deploys cannot race, and prevents a rapid series of pushes from stampeding the deploy.

Here is the full guarded workflow, the skeleton from Section 8 with every gate wired in. Every `<PLACEHOLDER>` is a TODO you fill in for your own repo.

```yaml
# .github/workflows/deploy.yml
name: deploy

on:
  workflow_dispatch:                 # manual: a human (or an authorized skill) clicks/calls Run
    inputs:
      environment:
        description: "Target environment"
        default: production
  push:
    branches: [main]                 # GATE 1 (branch): auto-deploy only from main

concurrency:                         # rate/serialize: no overlapping production deploys
  group: deploy-production
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production          # GATE 3: required-reviewer approval + environment secrets
    # GATE 2 (actor allowlist): only these users may actually run the deploy
    if: contains(fromJSON('["<YOUR-GH-USERNAME>"]'), github.actor)
    permissions:
      contents: read
      id-token: write                # only needed for the OIDC path (Section 10)
    steps:
      - uses: actions/checkout@<PINNED_SHA_OR_TAG>   # TODO: pin the action version
      - uses: actions/setup-node@<PINNED_SHA_OR_TAG>
        with:
          node-version: "20"
      - name: Deploy
        run: ./deploy.sh             # the workflow orchestrates; the script does the work
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}   # environment secret, masked
          WORKER_NAME: ${{ vars.WORKER_NAME }}                        # plain variable
```

## 12. Automation-Safe Scripts: No Prompts, No Hangs

The `wrangler deploy` you ran in Part II paused for a confirmation, the human gate. In CI there is no human, and a script that waits for input does not fail cleanly: it **hangs the runner** until the job times out (minutes of wasted CI), or it silently consumes piped input meant for something else.

Two rules make a script CI-safe:

- **Never wait for input.** Pass assume-yes flags (`--yes`, `--force`, or the tool's non-interactive mode), set `CI=true` where the tool honors it, and redirect stdin from nothing with `</dev/null` so any accidental prompt gets EOF and the command proceeds or fails instead of blocking.
- **Be idempotent.** Running the script twice must reach the same end state: create-if-not-exists, not create-and-crash-if-it-exists. A re-run after a flaky network should be harmless.

```bash
# Hangs forever in CI; there is no one to press a key:
read -p "Deploy to production? [y/N] " ok      # blocks on stdin; the runner waits, then times out

# Non-interactive and idempotent:
npx wrangler deploy --name "$WORKER_NAME" </dev/null   # </dev/null => any stray prompt gets EOF

# Idempotent setup, create the KV namespace only if it is absent:
if ! npx wrangler kv namespace list </dev/null | grep -q "$KV_TITLE"; then
  npx wrangler kv namespace create "$KV_TITLE" </dev/null
fi
```

> **How to recognize the failure:** a CI job that "just sits there" and eventually hits its time limit, with the log frozen on a step that *would* have asked a question, is almost always a script blocked on a prompt. The fix is upstream: remove the interactive `read`, add the assume-yes flag, or append `</dev/null`.

## 13. A Claude Skill That Requests the Deploy - But Cannot Bypass the Gates

You can let an agent *initiate* a deploy without giving it any power to bypass your guardrails. The key idea: a skill only **requests** a run via `workflow_dispatch`; the guardrails from Section 11 (branch, actor allowlist, environment approval) are enforced **server-side by the pipeline**, so the request is powerless unless it satisfies them.

A minimal Claude skill is a folder with a `SKILL.md` describing when and how to invoke the workflow:

```markdown
---
name: deploy-worker
description: Request a production deploy of the course Worker by dispatching the
  guarded GitHub Actions workflow. Use only when the user explicitly asks to deploy.
---

# deploy-worker

To request a deploy, dispatch the workflow on the `main` branch:

    gh workflow run deploy.yml --ref main -f environment=production

This only *requests* a deploy. The pipeline still enforces, server-side:
  - branch must be `main`
  - the triggering actor must be on the workflow's allowlist
  - a required reviewer must approve the `production` environment

If any gate fails, the run stops or waits; the skill cannot override it.
Never put a token in this skill or in the command; the workflow reads the
CLOUDFLARE_API_TOKEN environment secret itself.
```

This is the whole security lesson in miniature: **the skill can ask, but the environment decides.** Convenience (an agent kicks off the deploy) and control (a human still approves production, from the right branch, as an allowed actor) are not in tension; the guardrails let you have both.

---

## 14. Code Review and Spending CI Credits Wisely

Two practical realities sit on top of everything above: *someone (or something) reviews the change before it ships*, and *every CI run costs something*. Both are levers you control.

**Automated code review: a second reviewer, not the only one.** Tools like **GitHub Copilot code review** can be attached to a pull request to post inline comments automatically (flagging likely bugs, missing error handling, or style issues) either on every PR or on request (`@` the reviewer, or click *Request review*). Used well, it is a fast first pass that catches easy problems before a human spends attention on them. Two rules keep it honest:

- **It is advisory, not authoritative.** An AI reviewer can be confidently wrong, miss a real defect, or comment on the wrong thing. It does **not** replace the human required-reviewer gate from Section 11; treat its comments as suggestions you verify, exactly as you would a classmate's review. For a *security-sensitive* change (a new secret, a widened token scope, an OIDC trust policy), a human still signs off.
- **Never let a bot's approval satisfy a protection rule.** Required-reviewer approval on the `production` environment should require a *person*. An automated review comment is input to that person's decision, not a substitute for it.

**Automatic vs. manual runs: CI time is metered.** CI providers bill by the minute (GitHub Actions consumes a monthly allowance of runner minutes; private-repo minutes are limited, and some runners cost a multiplier). A workflow set to run on *every* push to *every* branch can quietly burn that allowance, and slow everyone down. The same triggering controls that made deploys *safe* also make them *cheap*:

- **Manual dispatch for expensive jobs.** Put costly workflows (full deploys, large test matrices, browser E2E) behind `workflow_dispatch` so they run when a person asks, not on every commit. This is the credit-saving twin of the human gate.
- **Scope automatic triggers.** Restrict `push`/`pull_request` triggers to the branches and paths that matter, so a docs-only edit does not trigger a full build:

```yaml
on:
  push:
    branches: [main]                 # not every branch
    paths: ["src/**", "deploy.sh"]   # skip runs when only docs/images change
  workflow_dispatch:                 # expensive path stays manual/on-demand
```

- **Cancel superseded runs.** A `concurrency` group with `cancel-in-progress: true` stops an older run when a newer commit arrives, so you are not paying for a build that is already obsolete (use this for *test/CI* jobs; keep `cancel-in-progress: false` for the *deploy* job so a live deploy is never interrupted mid-flight):

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true           # newer push cancels the older, still-running CI
```

- **Trim what runs.** Skip redundant jobs with `if:` conditions, keep the test matrix as small as it can be, and cache dependencies so each run does less work.

The through-line of this whole part holds here too: **automatic where it is cheap and safe, manual where it is expensive or consequential.** You are deciding, per workflow, how much to trade convenience for control and cost.

Your team's full deploy workflow is burning the month's Actions minutes because it runs on every push to every branch. The change that saves the most credits *without* weakening the production safety gates is:

[( )] Delete the required-reviewer rule on the `production` environment so runs stop waiting
[( )] Hardcode the Cloudflare token so runs skip the secret-fetch step
[(X)] Restrict the trigger to `main` (plus `paths` filters) and move the full deploy behind `workflow_dispatch`, so it runs on demand rather than on every commit
[( )] Give every teammate admin so anyone can cancel runs manually

### Critical Thinking Question

**Question 8.** GitHub Copilot code review comments on a pull request that widens an OIDC trust policy's subject to `repo:<ORG>/*`, and marks the PR as reviewed. Your `production` environment also requires a human reviewer. Explain why the automated review is useful here but must **not** be what unblocks the deploy, and describe the split of responsibility between the bot and the human reviewer.

[[___ Your answer here ___]]

*Hint:* What is the bot good at (spotting the wildcard, fast, on every PR) versus what does accountability for shipping a credential change require (a person who understands the blast radius and can be answerable for the decision)? Recall the wildcard risk from Question 6.

---

## Exercises

**Exercise 1.** Hello, edge. Scaffold, run locally, and deploy the JSON Worker from Section 4. Submit the public URL and the `curl` outputs for all three routes, including the 404.

*What to do:* Follow Sections 3-5 exactly. After `wrangler deploy`, test all three routes with `curl` and copy the outputs.

*Starter hint:*

```bash
npm create cloudflare@latest hello-worker
cd hello-worker
# Replace src/index.js with the three-route example from Section 4
npx wrangler dev                  # test locally first
# curl http://localhost:8787/health
# curl http://localhost:8787/greet?name=yourname
# curl http://localhost:8787/anything
npx wrangler deploy               # deploy when local tests pass
```

*You've succeeded when:* You can share a URL that returns `{"ok":true,...}` from `/health`, a greeting from `/greet?name=X`, and a proper 404 JSON from any other path.

**Exercise 2.** Secret discipline. Add a secret via `wrangler secret put` and a plain var via the config file; have the Worker prove (without revealing the secret's value) that both arrived. Explain your proof method in one sentence.

*What to do:* Add a `GREETING_PREFIX` variable to `[vars]` in `wrangler.toml`. Add a `SECRET_SUFFIX` via `wrangler secret put`. Update the Worker to use both in its response. The response should show that both values arrived without echoing the secret itself.

*Starter hint:*

```javascript
// Prove the secret arrived without revealing it:
return Response.json({
  greeting: `${env.GREETING_PREFIX} ${name}`,
  secret_present: env.SECRET_SUFFIX !== undefined,   // true/false, not the value
  secret_length: env.SECRET_SUFFIX?.length           // length proves it arrived, not the content
});
```

*You've succeeded when:* The response shows `"secret_present": true` and the correct `secret_length`, but the actual secret value never appears in the output.

**Exercise 3.** Pages deploy. Deploy any static artifact you have built this semester to Pages and share the URL with your team for review via a preview deployment.

*What to do:* Use the built output from any previous project (or create a minimal `index.html`). Run `wrangler pages deploy ./your-output-dir --project-name=cs357-yourname`. Share the preview URL (not the production URL) for teammate review.

*Starter hint:*

```bash
# Minimal example if you have no existing static output
mkdir my-site && echo "<h1>CS357 Project Demo</h1>" > my-site/index.html
npx wrangler pages deploy ./my-site --project-name=cs357-yourname
# Output includes a unique preview URL, share that for review
```

*You've succeeded when:* Your site is accessible at a `*.pages.dev` URL that a teammate can open in their browser.

**Exercise 4.** The facade. Build a gateway-facade Worker: it accepts a prompt as a query parameter or POST body, calls an LLM provider's free tier using a key held as a Worker secret, and returns the completion. Demonstrate that the browser-visible network requests contain no API key.

*What to do:* Store your LLM provider's API key with `wrangler secret put`. In the Worker, use `fetch()` to call the provider API with `env.YOUR_API_KEY`. Use browser DevTools -> Network tab to show that the key does not appear in any outgoing or incoming request visible to the browser.

*Starter hint:*

```javascript
// The Worker calls the LLM API on the server side; the browser never sees the key
if (url.pathname === "/complete") {
  const prompt = url.searchParams.get("prompt") || "Say hello from CS357";
  const response = await fetch("https://api.your-llm-provider.com/v1/complete", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.LLM_API_KEY}`,  // key stays on Cloudflare's servers
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ prompt, max_tokens: 100 })
  });
  const result = await response.json();
  return Response.json({ completion: result.choices[0].text });
}
```

*You've succeeded when:* The browser DevTools Network tab shows requests to your `workers.dev` URL only; the LLM provider API call is invisible to the browser, and the key is not in any response.

**Exercise 5.** Teardown drill. Delete one deployed Worker with `npx wrangler delete` and confirm the URL no longer responds. Report what was and was not recoverable after deletion.

*What to do:* Create a second minimal Worker (to avoid deleting your main one), deploy it, confirm it works, then delete it. Check whether the URL returns an error or times out. Check whether the Worker's logs and secrets are also gone.

*Starter hint:*

```bash
# Deploy a throwaway Worker
npm create cloudflare@latest throwaway-worker
cd throwaway-worker && npx wrangler deploy

# Confirm it works
curl https://throwaway-worker.<your-subdomain>.workers.dev/

# Delete it
npx wrangler delete --name throwaway-worker

# Confirm deletion
curl https://throwaway-worker.<your-subdomain>.workers.dev/  # should fail
```

*You've succeeded when:* You can describe what happens at the URL after deletion, whether the secrets stored via `wrangler secret put` are also deleted, and one sentence on what "reversibility" means for deployed Workers.

**Exercise 6.** Break-it-down: audit a flawed pipeline. The workflow and script below contain **five** distinct security or automation defects. Find each one, name why it is dangerous, and write the corrected line.

*What to do:* Read the two files carefully. For each defect, write: (1) the offending line, (2) the risk in one sentence, (3) the fix. There are five.

*Starter hint:* The five categories to hunt for are: a hardcoded secret, an over-broad credential, a missing who/where guardrail, a secret leaked to the logs, and a script that will hang in CI. Look for one of each.

```yaml
# .github/workflows/deploy.yml  (DELIBERATELY FLAWED, do not copy)
on:
  push:                                   # (defect) which branches? any branch can deploy
jobs:
  deploy:
    runs-on: ubuntu-latest                # (defect) no environment, no actor check
    steps:
      - uses: actions/checkout@main
      - run: |
          echo "token is $CLOUDFLARE_API_TOKEN"   # (defect) prints the secret past the mask
          ./deploy.sh
        env:
          CLOUDFLARE_API_TOKEN: cf_live_9s8d7f6g5h4j3k2l1   # (defect) hardcoded secret in the repo
```

```bash
# deploy.sh  (DELIBERATELY FLAWED, do not copy)
set -x                                    # (defect) echoes every command + expanded secret
read -p "Deploy now? [y/N] " ok           # (defect) hangs forever in CI, no human to answer
npx wrangler deploy --api-token GLOBAL_KEY # (over-broad: a global key, not a scoped token)
```

*You've succeeded when:* You have listed all five defects with a fix for each, and can explain (in one sentence) which single defect you would fix *first* if you could only fix one, and why.

**Exercise 7.** Add one guardrail. Starting from the guarded workflow in Section 11, wire in **one** guardrail end-to-end and prove it works: an actor allowlist, a branch restriction, **or** environment required-reviewer approval. If you have no Cloudflare account, use the **simulated-deploy fallback** (replace the deploy step with `run: echo "would deploy ${WORKER_NAME}"`) so you still exercise the trigger, secret injection, and guardrail without a cloud bill.

*What to do:* Create a minimal repo with `deploy.yml`. Add your chosen guardrail. Then *demonstrate the block*: trigger the workflow in a way that should be refused (wrong branch, disallowed actor, or unapproved environment) and capture the run showing it stopped or waited; then trigger it correctly and show it proceeds.

*Starter hint:* The easiest to demonstrate quickly is the branch restriction or the actor allowlist: push from a non-`main` branch, or have a teammate (not on the allowlist) trigger it, and screenshot the skipped/blocked job. The simulated deploy step keeps everything free:

```yaml
      - name: Deploy (simulated)
        run: echo "would deploy ${WORKER_NAME} - real wrangler deploy goes here"
        env:
          WORKER_NAME: ${{ vars.WORKER_NAME }}
```

*You've succeeded when:* You can show one run that was correctly *refused* by your guardrail and one that was correctly *allowed*, and explain which human judgment the guardrail replaced.

**Exercise 8.** The skill that asks, the pipeline that decides. Author a minimal `deploy-worker` Claude skill (Section 13) that dispatches your guarded workflow, then show that the guardrail still holds even though an agent initiated the run.

*What to do:* Write the `SKILL.md` with the `gh workflow run` invocation. Use it to request a deploy under a condition your guardrail forbids (e.g. the skill runs as a non-allowlisted actor, or targets a branch other than `main`). Capture the result.

*Starter hint:* The point is not that the skill succeeds; it is that the skill **cannot bypass** the gates. Requesting a deploy that violates a guardrail should be stopped by the pipeline exactly as a human request would be. Never place a token in the skill or the command.

*You've succeeded when:* You can show the skill *requesting* a deploy, the pipeline *enforcing* the guardrail server-side, and can state in one sentence why "the skill can ask, but the environment decides" is the safe division of authority.

---

### Self-Check Before You Ship

Run this checklist against your pipeline before you call it done. Every box should be checked.

| yes | Check | Why it matters |
|---|-------|----------------|
| [ ] | No secret, token, or key appears anywhere in the repo (or its git history) | A committed secret is compromised even after deletion |
| [ ] | The deploy credential is a **scoped** token (or OIDC role), never a Global/root key | Limits the blast radius if it ever leaks |
| [ ] | The token is stored as a GitHub **secret** (ideally environment-scoped), not a variable or a file | Encrypted, masked in logs, gated by the environment |
| [ ] | No `echo` of the secret and no `set -x` in scripts that touch it | Both defeat automatic log masking |
| [ ] | At least one guardrail is active: branch restriction, actor allowlist, or reviewer approval | Constrains who deploys, from where, with whose sign-off |
| [ ] | The deploy script is **non-interactive** (assume-yes / `</dev/null`) and **idempotent** | It cannot hang the runner, and a re-run is harmless |
| [ ] | Deploy logic lives in a **script** the workflow calls, runnable and testable locally | Not trapped in CI-only YAML |
| [ ] | `.dev.vars` / `.env` are in `.gitignore` | Local secrets never reach the repo |

---

## Reflection Prompt

Deployment used to be the moat that separated people with servers from everyone else, and this module reduced it to a login and a one-word command.

**Personal level:** What does it feel like to have a public URL for something you built? Does knowing it is public change how carefully you wrote the code, checked the secrets, or tested the error paths?

**Technical level:** Cloudflare Workers enforce a strict sandbox: no filesystem, short execution time limits, no persistent state within a request. How do these constraints shape what you can build at the edge versus what must stay local? Are these constraints a limitation or a feature?

**Societal level:** What does it mean for who gets to ship software that deploying a live global API now costs nothing and takes one command? What new bottleneck (skill, judgment, trust, governance) replaces the old bottleneck of "do you have a server"? Where does this course sit relative to that new bottleneck?

Write a combined reflection of 150-200 words addressing at least two of the three levels.

[[___ Your reflection here ___]]

---

-> Coming Up Next: In the Project Studio, you will take everything built and published this semester and prepare it for the final gallery walk, including rehearsing failure cases and triaging feedback into your final sprint.

---

## 15. Further Reading

- Cloudflare Workers documentation (developers.cloudflare.com/workers): the Get Started path and the `fetch` handler reference.
- Cloudflare Pages documentation: direct upload versus Git integration.
- The Wrangler command reference: `dev`, `deploy`, `secret`, `tail`, `pages deploy`, `delete`.
- Cloudflare CI/CD with GitHub Actions and scoped API tokens (developers.cloudflare.com/workers -> "CI/CD" and "Create API token"): the concrete deploy-from-Actions path used in Part IV.
- GitHub Actions, "Security hardening for GitHub Actions" (docs.github.com): using secrets, avoiding secret leakage in logs, and pinning action versions.
- GitHub Actions, "About security hardening with OpenID Connect" and "Configuring OIDC in AWS" (docs.github.com): how the signed per-run token, `audience`, and `subject` claims work, and how to pin the `sub` to your repo/branch/environment.
- GitHub, "Using environments for deployment" and "Reviewing deployments" (docs.github.com): environment protection rules and required reviewers (availability varies by repository visibility and plan tier; check what applies to yours).
- Claude Code, Agent Skills documentation (docs.anthropic.com): the `SKILL.md` format used by the deploy-request skill in Section 13.
- GitHub Copilot, "Using GitHub Copilot code review" (docs.github.com): requesting automatic or on-demand AI review on pull requests, and its limitations as an advisory (not authoritative) reviewer.
- GitHub Actions, "About billing for GitHub Actions" and "Usage limits, billing, and administration" (docs.github.com): how runner minutes are metered and how private-repo/runner multipliers affect cost.
- GitHub Actions, workflow trigger reference (`on:`, `paths`/`branches` filters, `workflow_dispatch`) and "Control the concurrency of workflows" (docs.github.com): the credit-saving controls in Section 14.
