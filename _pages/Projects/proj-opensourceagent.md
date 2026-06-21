---
layout: project
permalink: /Projects/OpenSourceAgent
title: "CS357: Foundations of Artificial Intelligence - Project: Build and Publish an Open-Source Agent"

info:
  coursenum: CS357
  points: 100
  goals:
    - To build an agent or agent component that is genuinely useful to others, documented for reuse, and published openly
    - To practice the full software lifecycle from design through implementation, testing, documentation, and publication
    - To engage with open-source community norms including licensing, contribution guides, and issue tracking
    - To apply the course's governance and safety principles to a publicly-deployed artifact that real users may run
  rubric:
    - weight: 20
      description: Design and Usefulness
      preemerging: The project idea is vague or duplicates an existing well-documented tool with no clear improvement; the proposal does not identify a real user need
      beginning: A problem is identified and a target user is named, but the scope is either too large to complete or too small to be genuinely useful; the README does not make the value clear to a stranger
      progressing: The proposal identifies a genuine gap, names concrete target users with realistic use cases, and defines a minimum viable scope; the README makes the value proposition clear but the stretch goals are vague
      proficient: The proposal identifies a gap that a stranger can verify exists, defines personas with realistic usage scenarios, sets a minimum viable scope that is achievable in the semester, and names specific stretch goals; the README makes a compelling case to a user who has never heard of the course
    - weight: 25
      description: Implementation and Code Quality
      preemerging: The core functionality does not work; code is absent or fails to run from a fresh checkout
      beginning: The project runs but contains hard-coded credentials or paths, lacks error handling, and implements only trivial functionality with no non-trivial features
      progressing: The core functionality works and implements at least one non-trivial feature; configuration is externalized; exceptions are caught with located messages; code is readable but inconsistently organized
      proficient: The core functionality works reliably; at least one non-trivial feature (streaming, authentication, persistent memory, or multiple tools) is fully implemented; configuration is externalized with documented defaults; exceptions are handled with located tracebacks; code is organized so a stranger can navigate it; model versions and seeds are pinned
    - weight: 20
      description: Testing and CI
      preemerging: No tests exist; CI is absent
      beginning: One or two unit tests exist but CI is absent or failing; LLM-dependent behavior is untested
      progressing: Unit tests cover the deterministic components; CI runs on every push; at least one LLM-dependent property test exists but the property is weakly specified
      proficient: Deterministic functions have unit tests with meaningful assertions; at least three property tests cover LLM-dependent components with clearly stated properties (e.g., "response always contains a citation", "output is valid JSON"); CI runs the full suite on every push and the badge is green on the submission SHA
    - weight: 20
      description: Documentation and Publication
      preemerging: README is absent or consists of the project title only; the project is not published
      beginning: README exists but quickstart requires more than 15 commands or fails on a clean machine; no CONTRIBUTING.md; governance statement is missing
      progressing: README quickstart works in under 10 minutes; CONTRIBUTING.md explains how to report bugs and run tests; governance statement exists but is generic or incomplete
      proficient: README quickstart works in under 5 commands on a clean machine; CONTRIBUTING.md covers bug reporting, PR submission, and local test execution; governance statement names what the agent does, what it does not do, what it must never be used for, and who is responsible; license is chosen and justified in writing
    - weight: 15
      description: Governance, Safety, and Community Engagement
      preemerging: No governance statement; project was not published to any registry or community; no community interaction occurred
      beginning: A governance statement exists but was not published; the project was pushed to GitHub but not submitted to a registry or community forum
      progressing: Governance statement is published in the repository; project is submitted to at least one registry; at least one community post was made but no response to feedback occurred
      proficient: Governance statement is published and specific; project is findable via at least one registry (npm, PyPI, Docker Hub, or MCP marketplace); a community post in an appropriate forum (Reddit, Discord, or HN) received at least one response and the student engaged with it authentically and thoughtfully

tags:
  - project
  - open-source
  - agents
  - governance
  - community

---

# Overview

This project track is for students who want to build something that outlasts the semester: a published, documented, reusable agent or agent component that real users could discover, install, and run. The deliverable is not a demo; it is a **software artifact with a community presence**. You will practice the full lifecycle from identifying a gap in the ecosystem through shipping to a registry and responding to feedback.

Choose a scope that is achievable in the time available but genuinely useful: an MCP server that wraps an API no one has packaged yet, an agent that solves a narrow task extremely well, a reusable prompt-caching middleware, a model-routing library, or an evaluation harness for a domain your team knows. The test of scope is the README: if a stranger in the relevant community would star the repository and actually use it, the scope is right.

This is an **individual or pair project**. Pairs must document individual contributions clearly. Tasks touching sensitive data or making outbound API calls on behalf of users require instructor approval and must include a governance statement that addresses those specific risks.

---

## Stage 1: Proposal (due week 10)

Identify a gap: an agent, tool, MCP server, or agent pattern that does not exist or is not done well. Write a two-page proposal containing:

**Checklist:**
- What the artifact does, in one paragraph that a stranger with no course context can understand.
- Who would use it: two to three **user personas** with realistic use cases (not "developers in general").
- How they would install it: the exact sequence of commands from a clean machine to a working demo.
- What makes it better than what already exists: name the closest alternative and the specific gap.
- **Minimum viable scope**: the smallest version that is genuinely useful, achievable before the end of the semester.
- **Stretch goals**: two to three extensions that would make the project more capable if time allows.
- **Governance sketch**: who is responsible, what the artifact must never be used for, and what risk the instructor should know about before approving.

---

## Stage 2: Implementation (weeks 10 through 13)

Build the core functionality following the design-first discipline from class: write the interface before the implementation, and write at least one test before each non-trivial function.

**Requirements:**
- Core functionality works on a clean machine by following the README.
- At least one **non-trivial feature** is fully implemented: streaming responses, token-level authentication, persistent memory across sessions, or multiple integrated tools with error recovery.
- **Unit tests** for all deterministic components, with meaningful assertions (not just "it ran without error").
- **At least three property tests** for LLM-dependent components. A property test asserts a structural property of the output that should always hold — for example: "every response includes a source citation," "the output is valid JSON matching the schema," "the agent declines requests containing the word 'illegal.'" These are not accuracy tests; they are behavioral contracts.
- **GitHub Actions CI** that installs dependencies, runs the test suite, and reports pass/fail on every pull request and push to main.
- Configuration externalized to environment variables or a config file with documented defaults; no hard-coded API keys or paths.
- Model versions and random seeds pinned in configuration so results are reproducible.

---

## Stage 3: Documentation (weeks 13 through 14)

Documentation is not optional polish — it is the primary interface between your artifact and the community that will use it.

**Required documents:**

**README.md** containing:
- A one-sentence description of what the artifact does.
- A quickstart: the user should reach a working demo in five commands or fewer on a clean machine.
- A configuration reference: every environment variable and config option, its type, its default, and what happens if it is omitted.
- At least two worked examples showing realistic usage.
- A link to the published registry package.

**CONTRIBUTING.md** containing:
- How to report a bug: what information to include, where to file it.
- How to submit a pull request: branch naming, test requirements, review expectations.
- How to run the test suite locally: exact commands from a clean checkout.
- Code of conduct (one paragraph minimum).

**Governance statement** (in GOVERNANCE.md or a dedicated README section) containing:
- What the agent does and what it does not do (scope).
- What the agent must never be used for (explicit prohibitions with reasoning).
- Who is responsible for the deployed artifact and how to reach them.
- How users should report harms or unexpected behavior.
- Known limitations that could cause harm if a user assumes they are not present.

**License**: choose a license and justify the choice in writing (one paragraph in the README). Consider: MIT (permissive, maximum adoption), Apache 2.0 (permissive with patent grant), AGPL (copyleft, requires open-sourcing derivative services). Your choice signals intent; the justification demonstrates that you made a principled decision.

---

## Stage 4: Publication and Community Engagement (week 14 through 15)

**Publication checklist:**
- Repository is on GitHub with a proper directory structure (source, tests, docs, CI configuration visible at the top level).
- Package is published to at least one registry: **npm** (for JavaScript/TypeScript tools or MCP servers), **PyPI** (for Python packages), **Docker Hub** (for containerized services), or the **MCP plugin marketplace** if applicable. The published version matches the submission SHA.
- The published package is installable from a clean machine using the registry's standard install command.

**Community engagement:**
- Post to at least one relevant community: a subreddit (r/LocalLLaMA, r/MachineLearning, r/learnprogramming for an educational tool), a Discord server, or Hacker News in Show HN format.
- The post must accurately describe what the artifact does and link to the repository. Do not oversell.
- When you receive feedback — an issue, a comment, a question — respond thoughtfully. "Thanks!" is not a response. Engagement means acknowledging the substance of the feedback and either incorporating it, explaining why you didn't, or opening a follow-up issue.
- Document the interaction in your submission: include a screenshot or link to the post, the feedback received, and your response.

---

## Submission Deliverables (final class meeting and exam slot)

1. **The repository**: public GitHub repo running from a fresh start following the README, with CI green on the submission SHA. Tag the submission commit `v1.0.0`.
2. **The published package**: a live URL on npm, PyPI, Docker Hub, or the MCP marketplace where the artifact is installable.
3. **The report** (three to five pages): what gap you identified and why, design decisions and tradeoffs, evaluation results from your property tests, documentation strategy, license justification, governance rationale, community engagement summary (with evidence), and individual contribution statement.
4. **The presentation** (8 minutes plus questions): live demo of the happy path and one known limitation, the property test results, and a 60-second governance statement addressed to the audience as if they were potential users.

---

## Reflection Prompts

Answer individually in your contribution statement:

- What gap did you find, and how did you verify it was real rather than imagined?
- Which engineering decision are you most proud of, and which would you make differently?
- What did community feedback teach you that you did not expect?
- Do you certify that your contribution statement accurately represents your own work? Please identify any and all portions of the project that were not originally created by you.
- Approximately how many hours did the project take you personally?
