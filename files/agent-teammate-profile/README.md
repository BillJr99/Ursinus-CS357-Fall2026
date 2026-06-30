# Agent Teammate Profile (CTP2 Case Study)

When you bring an autonomous agent onto a project, treat it like onboarding a new
teammate: give it a **charter** (what it is here to do and the lines it must not
cross), a **how-I-work** (how it should operate day to day), and a **resume**
(what it is actually good at). Together these three short documents are an
**agent teammate profile**. They are plain Markdown, version-controlled next to
your code, and read by the agent at the start of a session — the same mechanism
as `AGENTS.md` / `CLAUDE.md` (see `liascript-aidevenv.md`), but organized around
the human metaphor of hiring.

This is the artifact set from the course's **CTP2 case study**: the instructor's
own agent teammate, paired with the hardened "yolo mode" container in
`files/agent-yolo-container/` so the teammate can be run autonomously and safely.

## The three documents

| File | Human analogy | Answers the question |
|------|---------------|----------------------|
| `CHARTER.md`     | Job description + company handbook | *Why is this agent here, and what must it never do?* |
| `HOW-I-WORK.md`  | Working-style / team norms doc      | *How should it operate — cadence, communication, review?* |
| `RESUME.md`      | Resume / CV                         | *What is it good at, and where are its limits?* |

## How to use them

1. Copy the three templates in this directory into your project (or keep them
   here and mount them read-only — `run.sh` mounts this folder to
   `/workspace/.profile` automatically).
2. Fill in every `<bracketed>` prompt. Delete guidance you don't need.
3. Point your agent's context file at them, e.g. in `AGENTS.md` / `CLAUDE.md`:
   `Read .profile/CHARTER.md, .profile/HOW-I-WORK.md, and .profile/RESUME.md
   before doing anything.`
4. A filled, real-world version lives in `example/` — read it after you draft
   your own, not before.

## Why this matters for safety

The charter is where you write the **non-negotiable guardrails** that survive
even when you turn off per-action prompts. Running an agent in yolo mode without
a charter is running it with no job description and no handbook — don't.
