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

Your local stack is private by design, which is its virtue and its limit: nothing on `localhost` can be shown to a collaborator, demoed at a poster session, or used by anyone else. **Cloudflare's developer platform** fills that gap with a generous free tier: **Pages** hosts static sites, **Workers** runs serverless code at the edge, and **Wrangler** is the CLI that drives both from your terminal. This tutorial goes from no account to a deployed, secret-bearing API. The arc: **the platform map $\rightarrow$ Wrangler from zero $\rightarrow$ your first Worker $\rightarrow$ secrets and configuration $\rightarrow$ a Pages site $\rightarrow$ what belongs at the edge versus at home**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisites: the shell module, Node.js 20+, a free Cloudflare account (dash.cloudflare.com), and the publishing module's mindset: **deploying is publishing, so a human runs every deploy command**, our external-publication gate again. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Cloudflare Worker** | A JavaScript (or TypeScript or Python) function that runs on Cloudflare's global network in response to HTTP requests — no server to rent or manage, no container to keep alive | `wrangler deploy` publishes your `src/index.js` as a live API endpoint at `https://hello-worker.yourname.workers.dev` |
| **Cloudflare Pages** | A hosting service for static websites (HTML, CSS, JavaScript) that deploys instantly from a directory or a GitHub repository | `wrangler pages deploy ./dist` publishes your built project at `https://cs357-demo.pages.dev` |
| **Wrangler** | The official CLI tool for working with Cloudflare Workers and Pages — it scaffolds projects, runs them locally, deploys them, and manages secrets | `npx wrangler dev` starts a local version of your Worker at `localhost:8787` |
| **`wrangler.toml`** | The configuration file for a Cloudflare Worker project — sets the Worker's name, entry point, and pinned runtime version | `name = "hello-worker"` sets the subdomain; `compatibility_date` pins runtime behavior |
| **Worker secret** | A sensitive value (API key, token) stored on Cloudflare's servers and injected into the Worker at runtime — never written to any file or repository | `npx wrangler secret put UPSTREAM_API_KEY` — the value is entered interactively and stored server-side only |
| **Edge network** | Cloudflare's globally distributed set of data centers that run Workers close to whoever is making the request — reducing latency by running code near the user rather than in one central location | A request from a user in Tokyo is handled by a Cloudflare data center in Asia, not by a server in Virginia |

---

# Part I: The Platform and the Tool

In this part, you will map the three nouns that make up Cloudflare's developer platform and install Wrangler, the CLI that drives all of them — because understanding what each service does and does not do is the prerequisite for placing the right thing in the right place.

## 1. The Map

Workers are like serverless microwave ovens — they heat your code on demand, you do not manage the kitchen. When a request comes in, Cloudflare runs your function on the nearest server, returns the result, and the function stops running. You pay nothing for idle time, you never SSH into a machine, and Cloudflare handles TLS certificates, load balancing, and global distribution automatically. The free tier handles enough requests per day to cover any course project comfortably.

Three nouns cover the platform for our purposes:

A **Worker** is a JavaScript (or TypeScript, or Python) function that runs on Cloudflare's edge network in response to HTTP requests: no server to rent, no container to babysit, scaling and TLS handled for you, with a free tier (currently on the order of one hundred thousand requests per day) that comfortably covers any course project.

**Pages** hosts static sites (HTML, CSS, JS, your built React app) on the same network, free for ordinary use, and can attach Workers-style functions for the dynamic bits.

Around them sit storage primitives you may eventually want, of which **KV** (a key-value store bindable into a Worker, like a simple database your Worker can read and write) is the one worth knowing exists today.

**Wrangler** is the command-line interface to all of it: it scaffolds projects, runs them locally, deploys them, and manages secrets, which makes it the `docker` of this module. The honest framing for our course: the local stack is where private things live; Cloudflare is where *shareable, non-sensitive* things go, and deciding which is which is a governance exercise you have already trained for.

## 2. Wrangler from Zero

The following commands install Wrangler, connect it to your Cloudflare account, and confirm the connection. Run them in order — `wrangler login` will open a browser tab to complete authorization.

```bash
# Install Wrangler globally (or use npx wrangler to run without installing)
npm install -g wrangler

# Confirm it is installed
wrangler --version

# Log in — this opens a browser tab; authorize Cloudflare to connect to your account
wrangler login

# Confirm your account is connected
wrangler whoami
```

`wrangler login` stores an OAuth credential on your machine, scoped to your Cloudflare account. On shared machines (like a lab computer), run `wrangler logout` when you are finished — the same hygiene rule as any other credential.

With the platform map clear and Wrangler installed, Part II walks you from zero to a deployed Worker — a complete round trip from laptop to public URL in under ten minutes.

---

# Part II: Your First Worker

In this part, you will scaffold, run locally, and deploy a JSON API Worker, then add secrets using the pattern that keeps keys out of your repository — so you understand both what a Worker is and how to keep it secure before you build anything real.

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
# Your Worker runs at http://localhost:8787 — open it in a browser or use curl
```

`wrangler dev` runs your Worker in a faithful local simulation with live reload: edit, save, curl, repeat — the same inner loop as everything else this semester. The project's identity lives in its configuration file (`wrangler.toml`, or `wrangler.jsonc` in newer scaffolds — same keys, different syntax):

```toml
name = "hello-worker"            # becomes the subdomain: hello-worker.<you>.workers.dev
main = "src/index.js"            # the entry point file that Cloudflare runs
compatibility_date = "2026-06-01"  # pins runtime behavior to a specific date
```

That `compatibility_date` line deserves a pause: it is the platform's version-pinning mechanism, freezing runtime semantics as of a specific date so future Cloudflare platform updates cannot silently change your deployed behavior. This is the same reproducibility instinct as pinning an image tag — you are saying "run my code against the platform as it existed on this date."

## 4. The Code Shape, and a Real Example

A Worker exports a `fetch` handler: an HTTP request comes in, your function runs, an HTTP response goes out. Everything else is your logic. Here is a complete, production-quality example with routing and error handling:

The following Worker exports a `fetch` handler with three routes and honest error handling. Read the comments inside the code — they explain what each piece does and why it is structured this way.

```javascript
// src/index.js: a tiny JSON API with three routes and honest error handling
export default {
  async fetch(request, env, ctx) {
    try {
      // Parse the incoming request URL to check the path
      const url = new URL(request.url);

      // Route 1: health check — useful for confirming the Worker is running
      if (url.pathname === "/health") {
        return Response.json({ ok: true, at: new Date().toISOString() });
      }

      // Route 2: greeting — reads a query parameter (?name=Alice)
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

Note the `env` parameter: this is where secrets and configuration variables arrive from Cloudflare — covered in the next section. The `ctx` parameter provides lifecycle hooks for advanced patterns like waiting for a background task to finish before the Worker shuts down.

## 5. Deploy, Then Secrets

The following commands deploy your Worker to Cloudflare's global network and immediately test all three routes. The first `wrangler deploy` command may prompt you to confirm — this is the human gate before publishing to a public URL.

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

**Configuration that is not secret** (model names, feature flags, environment names) goes in the config file's `[vars]` table. This is visible in your repository and committed to version control — intentionally, since it is not sensitive.

**Secrets** (API keys, tokens, passwords) go through Wrangler's secret store and *never* touch any file:

```bash
# The value is entered interactively (not typed on the command line where it could appear in shell history)
# It goes directly to Cloudflare's secure storage, not to any local file
npx wrangler secret put UPSTREAM_API_KEY
```

```toml
# wrangler.toml (committed to your repository — only non-sensitive values here)
[vars]
MODEL_NAME = "claude-3-5-sonnet-20241022"    # safe to commit: not a secret
ENVIRONMENT = "production"                    # safe to commit: not a secret
```

```javascript
// In the handler, secrets and vars both arrive on the env object — same syntax, different storage
const key = env.UPSTREAM_API_KEY;            // secret: stored by wrangler secret put, never in files
const model = env.MODEL_NAME;                // plain var: stored in wrangler.toml, committed to repo
```

For local development, secrets go in a `.dev.vars` file (same syntax as a `.env` file). Add `.dev.vars` to `.gitignore` in the same breath as creating it.

To watch your live Worker's logs in real time (like `docker logs -f` but for the cloud):

```bash
npx wrangler tail    # streams live log output from your deployed Worker
```

[[MC]]
A teammate puts an API key in the [vars] section of wrangler.toml "because env reads both the same way." The flaw is:
- ( ) Workers cannot read vars at runtime — only secrets injected at deploy time are accessible via the `env` object
- (x) wrangler.toml is committed to the repository, so the key becomes part of the project's public record; secrets must go through wrangler secret put, which stores them server-side only
- ( ) vars and secrets are both stored server-side by Cloudflare, so committing the key to `wrangler.toml` has no security implication
- ( ) Secrets are faster to read than vars because they are stored in Cloudflare's KV store with lower latency

With a live Worker API deployed and secrets stored correctly, Part III shows how to host your static frontend on Pages and — most importantly — draw the line between what belongs at the edge and what must stay on localhost.

---

# Part III: Pages, and Drawing the Line

In this part, you will deploy a static site to Pages and apply the governance principle that has run throughout this course: every component should live where its data handling and sensitivity requirements dictate, not where it is most convenient to put it.

## 6. A Pages Site in Two Commands

Anything static — a project landing page, a built React artifact, your team's demo write-up, a visualization — deploys to Pages directly from a local directory:

```bash
# Build your static site first (if needed), then deploy the output directory
npx wrangler pages deploy ./dist --project-name=cs357-demo
# Output: -> https://cs357-demo.pages.dev

# Every subsequent deploy creates a new version with a unique preview URL:
# -> https://abc123.cs357-demo.pages.dev  (preview link for this specific deploy)
# -> https://cs357-demo.pages.dev         (stable production URL, always latest)
```

The first run creates the project on Cloudflare; later runs create new deployments, each with a unique preview URL alongside the stable production URL. This gives you free per-version review links — share the preview URL with a teammate to get feedback before promoting to production.

The alternative, equally legitimate path is Git integration through the Cloudflare dashboard: connect your repository, set the build command (`npm run build` or similar), and every push to `main` triggers a new deployment — with the human gate moving to the merge decision.

Custom domains, if you have one, attach to either Workers or Pages through the Cloudflare dashboard in a few clicks, TLS included and automatic.

## 7. What Belongs at the Edge

Workers are like serverless microwave ovens — fast, on-demand, zero management — but you would not try to bake a roast in a microwave. The edge is the right place for fast, stateless, public-facing code; it is the wrong place for heavy computation, large files, or anything subject to your data-handling agreements.

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

Before ruling, the Manager ensures the team has named the deciding principle for each component — not just an intuition.

### Critical Thinking Questions

**Question 1.** Rule on each placement — edge, local, or "redesign first" — with the deciding principle named for each. Draw on the data-handling and licensing commitments from earlier modules.

[[___ Your answer here ___]]

*Hint:* For (a): Is documentation sensitive? Does it contain anything you would not want publicly indexed? For (b): Who owns the essay content? What are the privacy implications of forwarding student work to a third-party cloud service? Does the professor whose course this is know about and consent to this data flow? For (c): What does "licensed course materials" mean for redistribution through a public API endpoint?

**Question 2.** For (b), the team argues the Worker holds no data since it only forwards. What two questions does our governance framework still require them to answer before deploying?

[[___ Your answer here ___]]

*Hint:* "We don't store it" is a claim about *your* system, but what about the third-party LLM provider the Worker forwards to? Also: the essay author (the student) — did they consent to having their work sent to a cloud service for automated scoring? These are the two questions.

**Question 3.** Sketch the hybrid architecture that lets the team demo publicly while keeping (c) entirely local. Which single secret exists, and where does it live?

[[___ Your answer here ___]]

*Hint:* The public part (Pages frontend + Worker gateway) handles user requests and authenticates to an LLM provider. The private part (local RAG system) handles the knowledge base. But the Worker needs to call something — what is the architecture if the heavy RAG work must stay on a local machine? Where does the one secret that bridges the gap live, and how is it protected?

---

> **⚠️ Common Misconception:** Students often assume that because a Worker is serverless — no server to manage, no container to maintain — it is also stateless in the sense that nothing persists between users or between requests. This is true for in-memory variables (each request gets a fresh execution context), but Cloudflare provides persistent storage primitives like KV that Workers can bind to. More importantly, the distinction between "does not persist" and "does not store" is crucial for governance: a Worker that forwards data to a third-party LLM provider does not store data itself, but it does transmit data to a service that may log, train on, or retain it. "We use a Worker, so we don't store data" is not a complete data-handling answer — it is the beginning of one.

---

## Exercises

**Exercise 1.** Hello, edge. Scaffold, run locally, and deploy the JSON Worker from Section 4. Submit the public URL and the `curl` outputs for all three routes, including the 404.

*What to do:* Follow Sections 3–5 exactly. After `wrangler deploy`, test all three routes with `curl` and copy the outputs.

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

**Exercise 2.** Secret discipline. Add a secret via `wrangler secret put` and a plain var via the config file; have the Worker prove — without revealing the secret's value — that both arrived. Explain your proof method in one sentence.

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
# Output includes a unique preview URL — share that for review
```

*You've succeeded when:* Your site is accessible at a `*.pages.dev` URL that a teammate can open in their browser.

**Exercise 4.** The facade. Build a gateway-facade Worker: it accepts a prompt as a query parameter or POST body, calls an LLM provider's free tier using a key held as a Worker secret, and returns the completion. Demonstrate that the browser-visible network requests contain no API key.

*What to do:* Store your LLM provider's API key with `wrangler secret put`. In the Worker, use `fetch()` to call the provider API with `env.YOUR_API_KEY`. Use browser DevTools → Network tab to show that the key does not appear in any outgoing or incoming request visible to the browser.

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

*You've succeeded when:* The browser DevTools Network tab shows requests to your `workers.dev` URL only — the LLM provider API call is invisible to the browser, and the key is not in any response.

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

---

## Reflection Prompt

Deployment used to be the moat that separated people with servers from everyone else, and this module reduced it to a login and a one-word command.

**Personal level:** What does it feel like to have a public URL for something you built? Does knowing it is public change how carefully you wrote the code, checked the secrets, or tested the error paths?

**Technical level:** Cloudflare Workers enforce a strict sandbox: no filesystem, short execution time limits, no persistent state within a request. How do these constraints shape what you can build at the edge versus what must stay local? Are these constraints a limitation or a feature?

**Societal level:** What does it mean for who gets to ship software that deploying a live global API now costs nothing and takes one command? What new bottleneck — skill, judgment, trust, governance — replaces the old bottleneck of "do you have a server"? Where does this course sit relative to that new bottleneck?

Write a combined reflection of 150–200 words addressing at least two of the three levels.

[[___ Your reflection here ___]]

---

→ Coming Up Next: In the Project Studio, you will take everything built and published this semester and prepare it for the final gallery walk — including rehearsing failure cases and triaging feedback into your final sprint.

---

## 9. Further Reading

- Cloudflare Workers documentation (developers.cloudflare.com/workers): the Get Started path and the `fetch` handler reference.
- Cloudflare Pages documentation: direct upload versus Git integration.
- The Wrangler command reference: `dev`, `deploy`, `secret`, `tail`, `pages deploy`, `delete`.
