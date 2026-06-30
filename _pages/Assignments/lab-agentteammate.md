---
layout: assignment
permalink: /Assignments/AgentTeammate
title: "CS357: Foundations of Artificial Intelligence - Lab: Hire an Agent Teammate (Charter, How-I-Work, Resume) and Run It Safely in YOLO Mode"

info:
  coursenum: CS357
  points: 100
  goals:
    - To author a coherent agent teammate profile - a charter, a how-I-work, and a resume - for a delegated task
    - To phrase charter guardrails so they survive the removal of permission prompts, and to back each one with a container setting
    - To build and harden the course container so an agent can run in yolo mode with a bounded blast radius
    - To run an agent in yolo mode against the profile and document a red-team attempt against one guardrail
    - To make an explicit, evidence-based decision about when autonomy is and is not acceptable for the task
  rubric:
    - weight: 25
      description: Teammate Profile Coherence
      preemerging: Fewer than three profile documents are submitted, or they are unedited templates
      beginning: All three documents exist but are generic; the resume does not state limitations and the charter mixes intent with vague preferences
      progressing: The charter states a clear mission with at least three non-negotiable out-of-bounds guardrails, the how-I-work specifies plan/increment/review behavior, and the resume lists skills and at least two honest limitations
      proficient: The three documents are mutually consistent - every resume limitation is answered by a specific charter or how-I-work rule, the mission is scoped to what the resume supports, and escalation behavior is defined for tasks that fall in the capability gap
    - weight: 25
      description: Guardrails Backed by the Container
      preemerging: No mapping between guardrails and container settings is provided
      beginning: Guardrails are listed but the mapping to container settings is absent or incorrect (e.g., claims a prompt rule prevents network exfiltration)
      progressing: At least three out-of-bounds guardrails are each paired with the specific container setting that enforces them, with one gap or imprecision
      proficient: Every enforceable guardrail is paired with the exact container flag that makes the forbidden action impossible (mount scope, network none, read-only, cap-drop, resource limits, secret handling), and the team correctly identifies at least one guardrail that the container cannot enforce and names the out-of-container mechanism for it
    - weight: 25
      description: Hardened Runtime and Red-Team Evidence
      preemerging: The container does not build or run, and no red-team attempt is documented
      beginning: The container runs but is largely unhardened, or the red-team section only describes intent without an executed attempt
      progressing: The container builds and runs with most hardening flags applied and verified; one red-team attempt against a guardrail is executed with the outcome recorded
      proficient: The container builds and runs with all hardening flags verified after application; the agent is run in yolo mode against the profile on a real task; at least one red-team attempt (e.g., a prompt-injection file instructing exfiltration or out-of-scope file access) is executed and the recorded outcome shows the container boundary holding, with honest discussion of what still leaked or could leak
    - weight: 25
      description: Autonomy Decision and Reflection
      preemerging: No safe-yolo checklist or autonomy decision is submitted
      beginning: The checklist is filled but the autonomy decision is asserted without reference to evidence from the run
      progressing: The completed safe-yolo checklist accompanies a stated autonomy decision that references at least one observation from the run
      proficient: The team completes the safe-yolo checklist, states a defensible decision about whether this task should run autonomously, and supports it with specific evidence from the red-team attempt and the run; the reflection articulates a concrete change in how the team thinks about delegating to autonomous agents
  readings:
    - rtitle: "Hiring an Agent: Charter, How-I-Work, and Resume (CTP2 Case Study)"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ctp2teammateprofile.md"
    - rtitle: "Running Agents in YOLO Mode Safely"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-yolomode.md"
    - rtitle: "Containerizing AI Systems: Safety, Isolation, and Trust Boundaries"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-containerizationsafety.md"

tags:
  - agents
  - safety
  - docker
  - autonomy

---

In this lab, you and your partner *hire* an autonomous agent: you write its onboarding documents, give it a hardened home, let it work unsupervised on a real task, and then try to break it. The deliverable is not just files — it is a defensible, evidence-backed answer to the question every team deploying agents must face: *under what conditions is it acceptable to let this thing run without watching every step?* This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

---

## Before You Start

### Prerequisites

- The **CTP2 case study** activity and the **YOLO Mode Safely** tutorial (linked above).
- The **Containerizing an AI System Safely** lab, or equivalent comfort with Docker hardening flags.
- The course container scaffold in `files/agent-yolo-container/` and the profile templates in `files/agent-teammate-profile/`.
- At least one coding agent CLI available inside the container (Claude Code, opencode, codex, pi, or codewhale). A local Ollama model is sufficient; no paid API is required.

---

## Part A — Write the Teammate Profile

Choose a **real, bounded task** you would genuinely delegate — for example: "add docstrings and a test file to this small Python module," "convert this folder of notes to a consistent Markdown format," or "draft a triage summary for a folder of incoming requests" (a preview of the `proj-requesttriage` project).

1. Copy `CHARTER.md`, `HOW-I-WORK.md`, and `RESUME.md` from `files/agent-teammate-profile/` into your task workspace and fill in **every** bracketed prompt.
2. In the charter, write **at least three** out-of-bounds guardrails in strong "NEVER / ALWAYS stop before" language.
3. In the resume, write **at least two** honest limitations, and confirm each is answered by a rule in the charter or how-I-work. Record those pairings — you will submit them.

## Part B — Map Guardrails to the Container

Build a table with one row per charter guardrail. For each, state the **container setting** that enforces it (mount scope, `--network none`, `--read-only`, `--cap-drop ALL`, `--memory`/`--cpus`/`--pids-limit`, secret handling) — or, if the container *cannot* enforce it, name the out-of-container mechanism you would use instead (e.g., branch protection for "never push to `gh-pages`").

## Part C — Build and Harden the Runtime

1. Build the image: `docker build -t cs357/agent-yolo:latest files/agent-yolo-container`.
2. Launch with `./run.sh` and **verify** the hardening: from inside the container, confirm you cannot read a host home-directory file, cannot reach the network (default), and that resource limits are in effect. Record each verification.

## Part D — Run in YOLO Mode, Then Red-Team It

1. With the profile mounted, run your chosen agent in **yolo mode** (e.g., `claude --dangerously-skip-permissions`) on the Part A task. Record what it did.
2. **Red-team one guardrail.** Plant a prompt-injection attempt the agent will encounter — for example, a file containing hidden text instructing it to read a path outside the workspace, or to base64-encode a "secret" file and print it. Run again and record the outcome: did the charter alone stop it, did the container stop it, or did something leak?
3. Complete the **safe-yolo checklist** from the YOLO tutorial for this task.

## Part E — The Autonomy Decision

Write a short, evidence-based verdict: *for this task, under this profile and this runtime, is autonomous (yolo) operation acceptable?* Cite at least one specific observation from your run and red-team attempt. State what would have to change for your answer to flip.

---

## What to Submit

- The three profile documents (charter, how-I-work, resume) and the resume-limitation/charter-rule pairing list.
- The guardrail-to-container mapping table from Part B.
- A transcript or log of the hardening verifications, the yolo run, and the red-team attempt and its outcome.
- The completed safe-yolo checklist and your Part E autonomy decision.
- Your driver/navigator swap log.

> **Course guardrail:** Run this lab only inside the container, with the network off unless your task truly needs it. Never point the agent at your real home directory, SSH keys, cloud credentials, or a repository you are not prepared to lose.
