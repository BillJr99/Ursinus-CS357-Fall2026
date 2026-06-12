# Hosting with Cloudflare: Workers, Pages, and Wrangler
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

# Part I: The Platform and the Tool

## 1. The Map

Three nouns cover the platform for our purposes. A **Worker** is a JavaScript (or TypeScript, or Python) function that runs on Cloudflare's edge network in response to HTTP requests: no server to rent, no container to babysit, scaling and TLS handled for you, with a free tier (currently on the order of one hundred thousand requests per day) that comfortably covers any course project. **Pages** hosts static sites (HTML, CSS, JS, your built React app) on the same network, free for ordinary use, and can attach Workers-style functions for the dynamic bits. Around them sit storage primitives you may eventually want, of which **KV** (a key-value store bindable into a Worker) is the one worth knowing exists today.

**Wrangler** is the command-line interface to all of it: it scaffolds projects, runs them locally, deploys them, and manages secrets, which makes it the `docker` of this module. The honest framing for our course: the local stack is where private things live; Cloudflare is where *shareable, non-sensitive* things go, and deciding which is which is a governance exercise you have already trained for.

## 2. Wrangler from Zero

```bash
npm install -g wrangler          # install (or use npx wrangler per-command)
wrangler --version               # verify
wrangler login                   # opens a browser; authorize once
wrangler whoami                  # confirm the account
```

`wrangler login` stores an OAuth credential on your machine, scoped to your account; on shared machines, `wrangler logout` when finished, the same hygiene as any other credential.

---

# Part II: Your First Worker

## 3. Scaffold, Run Locally, Read the Config

```bash
npm create cloudflare@latest hello-worker
# Choose: "Hello World" Worker, JavaScript, no git questions you are unsure of
cd hello-worker
npx wrangler dev                 # local dev server, default http://localhost:8787
```

`wrangler dev` runs your Worker in a faithful local simulation with live reload: edit, save, curl, repeat, the same inner loop as everything else this semester. The project's identity lives in its configuration file (`wrangler.toml`, or `wrangler.jsonc` in newer scaffolds; same keys, different syntax):

```toml
name = "hello-worker"            # becomes the subdomain: hello-worker.<you>.workers.dev
main = "src/index.js"            # the entry point
compatibility_date = "2026-06-01"  # pins runtime behavior to a date: reproducibility!
```

That `compatibility_date` line deserves a pause: it is the platform's version-pinning mechanism, freezing runtime semantics as of a date so future platform changes cannot silently alter your deployed behavior, the same reproducibility instinct as a pinned image tag.

## 4. The Code Shape, and a Real Example

A Worker exports a `fetch` handler: request in, response out, and everything else is your logic:

```javascript
// src/index.js: a tiny JSON API with routing and honest error handling
export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url);

      if (url.pathname === "/health") {
        return Response.json({ ok: true, at: new Date().toISOString() });
      }

      if (url.pathname === "/greet") {
        const name = url.searchParams.get("name") || "world";
        return Response.json({ greeting: `hello, ${name}`, course: "CS357" });
      }

      return Response.json({ error: "not found" }, { status: 404 });
    } catch (e) {
      console.error(`[hello-worker:fetch] ${e}`);
      return Response.json({ error: "internal error" }, { status: 500 });
    }
  },
};
```

Note the course exception pattern surviving the platform change: a located log line for you, a clean message for the user, never a silent swallow. The `env` parameter is where secrets and bindings arrive, next section.

## 5. Deploy, Then Secrets

```bash
npx wrangler deploy
#  Deployed hello-worker -> https://hello-worker.<your-subdomain>.workers.dev
curl https://hello-worker.<your-subdomain>.workers.dev/greet?name=Bill
```

That is the entire distance from laptop to public URL. Now the part everyone gets wrong without instruction: **configuration that is not secret** (model names, feature flags) goes in the config file's `[vars]` table, visible in your repository, while **secrets** (API keys, tokens) go through Wrangler's secret store and *never* touch the file:

```bash
npx wrangler secret put UPSTREAM_API_KEY     # prompts; value goes to Cloudflare, not to disk
```

```javascript
// In the handler, both arrive on env:
const key = env.UPSTREAM_API_KEY;            // secret, set via wrangler secret put
const model = env.MODEL_NAME;                // plain var, set in wrangler.toml [vars]
```

For local dev, secrets go in a `.dev.vars` file that you add to `.gitignore` immediately, in the same breath as creating it. Tail a live Worker's logs with `npx wrangler tail`, the cloud sibling of `docker logs -f`.

[[MC]]
A teammate puts an API key in the [vars] section of wrangler.toml "because env reads both the same way." The flaw is:
- ( ) Workers cannot read vars at runtime
- (x) wrangler.toml is committed to the repository, so the key becomes part of the project's public record; secrets must go through wrangler secret put, which stores them server-side only
- ( ) vars are limited to 32 characters
- ( ) Secrets are faster to read than vars

---

# Part III: Pages, and Drawing the Line

## 6. A Pages Site in Two Commands

Anything static (a project landing page, a built React artifact, your team's demo write-up) deploys to Pages directly from a directory:

```bash
npx wrangler pages deploy ./dist --project-name=cs357-demo
#  -> https://cs357-demo.pages.dev
```

The first run creates the project; later runs create new deployments, each with a unique preview URL alongside the stable production one, which gives you free per-version review links for teammates. The alternative, equally legitimate path is Git integration through the Cloudflare dashboard: connect the repository, set the build command, and every push deploys, with the human gate moving to the merge. Custom domains, if you have one, attach to either Workers or Pages through the dashboard in a few clicks, TLS included.

## 7. What Belongs at the Edge

The architectural judgment, since this course has trained you for exactly this decision. The edge is the right home for the **shareable shell**: demo frontends, project documentation, thin public APIs, and notably a *gateway facade* in front of an LLM provider that holds the provider key as a Worker secret so the key never ships to a browser. The local stack remains the right home for **inference and data**: model serving, anything touching course data subject to our data-handling rules, and agent workloads with filesystem access. A clean pattern for project demos combines them: a Pages frontend, a Worker holding one secret and proxying to a rate-limited provider free tier, and the heavyweight private work staying home. Your governance document should be able to point at each component and say why it lives where it lives.

---

## Model 1: Placement Review

A team proposes: (a) their project's documentation site, (b) a Worker that accepts student-submitted essays and forwards them to a cloud LLM for scoring, (c) their RAG knowledge base built from a professor's licensed course materials.

### Critical Thinking Questions

1. Rule on each placement (edge, local, or "redesign first") with the deciding principle named, drawing on the data-handling and licensing commitments from earlier modules.
2. For (b), the team argues the Worker holds no data since it only forwards. What two questions does our governance framework still require them to answer before deploying?
3. Sketch the hybrid architecture that lets the team demo publicly while keeping (c) entirely local. Which single secret exists, and where does it live?

---

## 8. Exercises

1. *Hello, edge.* Scaffold, run locally, and deploy the JSON Worker above. Submit the public URL and the `curl` outputs for all three routes, including the 404.
2. *Secret discipline.* Add a secret via `wrangler secret put` and a plain var via the config file; have the Worker prove (without revealing the secret's value!) that both arrived. Explain your proof method in one sentence.
3. *Pages deploy.* Deploy any static artifact you have built this semester to Pages and share the URL with your team for review via a preview deployment.
4. *The facade.* Build the gateway-facade Worker: it accepts a prompt, calls an LLM provider's free tier using a key held as a Worker secret, and returns the completion. Demonstrate that the browser-visible code contains no key. (This Worker is a strong Ship It assignment candidate.)
5. *Teardown drill.* Delete one deployed Worker (`npx wrangler delete`) and confirm the URL dies. Reversibility audits are part of publishing maturity; report what was and was not recoverable.

---

## Reflection Prompt

In your notebook: deployment used to be the moat that separated people with servers from everyone else, and this module reduced it to a login and a one-word command. What does that collapse mean for who gets to ship software, and what new bottleneck (skill, judgment, trust) replaces the old one? Where does this course sit relative to that new bottleneck?

---

## 9. Further Reading

- Cloudflare Workers documentation (developers.cloudflare.com/workers): the Get Started path and the `fetch` handler reference.
- Cloudflare Pages documentation: direct upload versus Git integration.
- The Wrangler command reference: `dev`, `deploy`, `secret`, `tail`, `pages deploy`.
