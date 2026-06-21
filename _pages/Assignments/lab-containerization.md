---
layout: assignment
permalink: /Assignments/Containerization
title: "CS357: Foundations of Artificial Intelligence - Lab: Containerizing an AI System Safely"

info:
  coursenum: CS357
  points: 100
  goals:
    - To apply Docker security hardening principles to a multi-container AI system
    - To design and enforce a trust boundary between an AI agent and the host system
    - To document and test the threat model for a containerized AI deployment
    - To implement safety controls including resource limits, read-only mounts, and non-root execution
  rubric:
    - weight: 30
      description: Security Configuration
      preemerging: The hardened compose file is missing or substantially identical to the baseline insecure configuration
      beginning: At least one hardening measure is applied (e.g., non-root user or read-only filesystem) but the others are absent or incorrectly configured
      progressing: At least four of the six hardening steps are correctly applied and verified, with a minor gap such as a missing resource limit or an overly broad capability grant
      proficient: All six hardening steps are correctly applied, verified after each step, and expressed in a complete docker-compose.yml with secrets managed outside of environment variables and capabilities minimized to only what is required
    - weight: 25
      description: Threat Model and Documentation
      preemerging: No threat model table is submitted, or it lists threats without describing attacks or defenses
      beginning: The threat model covers two or fewer threats with superficial attack descriptions and no residual risk analysis
      progressing: The threat model covers all four required threats with plausible attack vectors and stated defenses, with residual risk identified for at least two threats
      proficient: The threat model covers all four threats with specific, realistic attack vectors, defenses that map to the actual hardening steps applied, and honest residual risk assessments that distinguish what the container boundary cannot prevent
    - weight: 25
      description: Testing and Verification
      preemerging: No testing artifacts are submitted beyond a description of intent
      beginning: Ad hoc tests are shown but there is no systematic progression from baseline to hardened and the red team exercise is absent
      progressing: Baseline behavior is documented, hardening is verified after at least three steps, and a red team exercise was attempted with results recorded
      proficient: Baseline capabilities are documented with specific examples, each hardening step is verified immediately after application, the red team exercise demonstrates at least one attempted unsafe action against the hardened container with the outcome recorded, and the security runbook addresses all three required procedures
    - weight: 20
      description: Reflection and Analysis
      preemerging: No pair log or security runbook is submitted
      beginning: The runbook is submitted but covers only one procedure, and reflection prompts receive answers that do not reference specific lab findings
      progressing: The runbook covers secret rotation and log auditing, the pair log shows at least two role swaps, and reflection answers reference specific observations from the lab
      proficient: The runbook covers all three procedures with actionable steps, the pair log shows regular swaps with timestamps, and reflection answers articulate a specific change in how the pair thinks about trust boundaries in AI deployments
  readings:
    - rtitle: "Docker from Zero Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-docker.md"
    - rtitle: "The Local Agent Stack Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md"

tags:
  - docker
  - security
  - infrastructure
  - agents

---

In this lab, you and your partner will take a deliberately insecure AI agent container, document what it can do in that state, and then harden it step by step until it operates under the principle of least privilege. The goal is not to memorize flags — it is to understand *why* each boundary exists and what threat it addresses. This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

## Part 1: Baseline (Insecure) Deployment

Deploy a simple AI agent container — use the Hermes agent, a provided LLM-calling Python script, or another option approved by the instructor — with **no security hardening**: running as root, with the host home directory bind-mounted, and with privileged or default access. Document exactly what the agent can access in this configuration (files visible, network reachable, system calls available). Then, carefully and in a test environment only, demonstrate one unsafe action the agent could take if it were misbehaving (for example: reading a file outside the intended workspace, or listing environment variables containing secrets). Capture the output and document it as the baseline.

## Part 2: Hardening Step by Step

Apply each of the following hardening measures **one at a time**, verifying the container behavior after each step before moving to the next. Do not batch them — the goal is to observe the effect of each measure in isolation.

- **a.** Add a non-root user (`USER agent` in the Dockerfile or `user:` in compose) and verify the effective UID inside the container.
- **b.** Make the filesystem read-only (`read_only: true`) with a `tmpfs` mount at `/tmp` for scratch space, and verify that writes outside `/tmp` are rejected.
- **c.** Drop all Linux capabilities (`cap_drop: [ALL]`) then add back only what the agent requires (`cap_add:`), and verify the agent still functions.
- **d.** Restrict network access so the container can only reach the services it legitimately needs (use a named network and remove default bridge access), and verify that connections to unauthorized hosts fail.
- **e.** Add resource limits for CPU (`cpus:`), memory (`mem_limit:`), and process count (`pids_limit:`), and verify the limits are enforced.
- **f.** Move any secrets from environment variables to Docker secrets (`secrets:` in compose and `/run/secrets/` in the container), and verify that `docker inspect` no longer reveals the secret value.

## Part 3: Threat Modeling

Complete the **threat model table** for your hardened deployment. For each of the following four threats, describe the specific attack vector, the defense you applied in Part 2 that addresses it, and the residual risk that remains even after hardening: prompt injection leading to unauthorized file access, data exfiltration via outbound network calls, resource exhaustion (CPU/memory/fork bomb), and secret theft via environment variable inspection.

Then perform a **red team exercise**: attempt to make your hardened container take an action it should not be able to take. Suggested approaches include crafting a prompt that attempts to read outside the workspace, attempting an outbound connection to a host not in the allowed network, or trying to write to the read-only filesystem. Record exactly what you tried, what the container did, and what that tells you about the residual risk.

## Part 4: Compose and Document

Express the complete hardened deployment as a `docker-compose.yml` with all security settings from Part 2 included. Then write a **security runbook** covering three procedures: how to update a Docker secret without restarting the full stack, how to rotate credentials when a secret is suspected compromised, and how to audit container logs to detect anomalous agent behavior.

## Deliverables

Submit a ZIP containing: the baseline compose file with documentation of what the insecure agent could access, the hardened compose file with all security settings, the threat model table, red team exercise notes with outcomes, the security runbook, and the pair log with role-swap timestamps.

## Reflection Prompts

- Which hardening step had the most surprising effect on the agent's behavior, and why?
- The container boundary is not a complete security guarantee. Name one class of attack that your hardening does not prevent, and describe what additional control would be needed.
- How does the principle of least privilege apply differently to an AI agent than to a traditional web server?
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
