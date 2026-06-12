---
layout: assignment
permalink: /Assignments/AgentStack
title: "CS357: Foundations of Artificial Intelligence - Lab: Composing the Local Agent Stack"

info:
  coursenum: CS357
  points: 100
  goals:
    - To deploy a multi-container local AI stack with an inference backend, a unified gateway, a frontend, a tool service, and an agent
    - To wire containers to host services and to each other using host.docker.internal with correct platform flags
    - To express the stack declaratively with docker compose, a port table, and per-service identity directories
    - To verify the stack systematically with a wiring matrix and document failures with honest postmortems
  rubric:
    - weight: 35
      description: Stack Deployment
      preemerging: The stack fails to start due to major issues, or fewer than three tiers are represented
      beginning: The stack starts but one or more required services is misconfigured or unreachable
      progressing: All five tiers run (inference, gateway, frontend, tool, agent) with identity directories and a port table, with a fragile element such as a hardcoded path or a missing restart policy
      proficient: All five tiers run from a documented setup with per-service identity directories, a complete port table with no collisions, restart policies chosen deliberately, and configuration externalized rather than hardcoded
    - weight: 25
      description: Wiring and the host.docker.internal Discipline
      preemerging: Containers cannot reach the host or each other
      beginning: Some connections work but localhost and host.docker.internal are confused in one or more configs
      progressing: All required connections work, with the Linux extra hosts flag applied where needed, with a minor gap such as an undocumented connection
      proficient: All connections work and are documented as a diagram or table, every container that reaches the host declares the host alias correctly for its platform, and the team can explain from first principles why each URL is what it is
    - weight: 25
      description: Verification Matrix and Postmortems
      preemerging: No systematic verification is attempted
      beginning: A few ad hoc curl checks are shown without organization
      progressing: A wiring matrix tests each service from the host and at least one connection from inside a container, with an end-to-end completion demonstrated
      proficient: The wiring matrix covers host-side liveness for every service, container-side reachability for every cross-container dependency, and an end-to-end chat completion through the full chain, and at least one real failure encountered during the lab is documented with a three-line postmortem (symptom, cause, fix)
    - weight: 15
      description: Compose File, Writeup, and Submission
      preemerging: An incomplete submission is provided
      beginning: The submission is provided but the compose file is missing or does not reflect the running stack
      progressing: The compose file reproduces the core stack with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The compose file reproduces the stack from a fresh start, the readme documents setup in under a page, the pair log is included, and the reflection prompts receive thoughtful answers
  readings:
    - rtitle: "The Local Agent Stack Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md"
    - rtitle: "Docker from Zero Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-docker.md"

tags:
  - docker
  - infrastructure
  - agents

---

In this lab, you and your partner will stand up a working local AI stack: one service from every tier of the course architecture, wired together correctly, verified systematically, and reproducible from a compose file. This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**. The skill being graded is not typing commands; it is the wiring discipline that makes two dozen services coexist, demonstrated on five.

## Part 1: Plan Before Pulling

Before any container starts, produce the **port table** for your five chosen services (one per tier: an inference backend such as ollama or lmstudio; the llmproxy gateway; a frontend such as open-webui; a tool such as searxng or surrealdb; and an agent such as hermes, agent0, or freebuff), checking image defaults and resolving every collision on paper. Create the identity directory tree under `$HOME/agents/`. Submit the table and the `mkdir` line as your Part 1 artifact; the lab's most common failure (port collision at midnight) is prevented here or not at all.

## Part 2: The Core Chain (scaffolded; verify each link before adding the next)

2a. Stand up the inference backend and verify from the host (`curl` its API; for ollama, `/api/tags` listing at least two pulled small models).

2b. Stand up llmproxy as a compose service with its routing YAML pointing at the backend via `host.docker.internal` (with `extra_hosts` on Linux). Verify the `/models` endpoint from the host.

2c. Stand up the frontend with a published port and a bind-mounted data directory, connect it to the gateway through its settings, and complete a chat in the browser that round-trips the full chain.

## Part 3: Tool and Agent

3a. Add your tool service on its planned port (remapping where the image default collides), and verify it from *inside* another container via `host.docker.internal`, demonstrating you understand whose localhost is whose.

3b. Add your agent with its identity directory and the host alias flag, give it one small task in the shared workspace, then destroy and recreate the container to demonstrate identity persistence.

## Part 4: Verify, Break, and Declare

4a. Build the **wiring matrix**: host-side liveness checks for all five services, container-side reachability for every cross-container dependency, and one end-to-end chat completion via `curl` against the gateway. Submit the commands and outputs as a table.

4b. **Break it on purpose**: remove the host-alias flag (or substitute `localhost` in one config), capture the exact symptom, restore it, and write the three-line postmortem. If you hit a *real* unplanned failure during the lab, you may substitute its postmortem and we will all be happier for it.

4c. Express the reproducible core (gateway, frontend, and tool at minimum) as one `docker-compose.yml`, and demonstrate `down` followed by `up -d` restores the working stack with data intact.

## Deliverables

Submit a ZIP containing your port table, compose file and configuration files (tokens and keys redacted), the wiring matrix with outputs, the postmortem, the pair log, and a readme of approximately one page. Ensure reproducibility by pinning image tags where stability matters and listing software version information.

## Reflection Prompts

- Which connection in your stack took longest to get right, and what diagnostic step would have found it faster?
- Your stack now runs capable agents entirely on hardware you control. Name one governance obligation that this locality satisfies automatically and one it quietly transfers onto you.
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
