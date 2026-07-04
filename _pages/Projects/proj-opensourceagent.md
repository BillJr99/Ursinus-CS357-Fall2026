---
layout: project
permalink: /Projects/OpenSourceAgent
title: "CS357: Foundations of Artificial Intelligence - Project: Build and Publish an Open-Source Agent"

info:
  coursenum: CS357
  points: 100
  goals:
    - To identify a verifiable gap in the agent tooling ecosystem, define a minimum viable scope achievable in the semester, and build an artifact that is genuinely useful to real users
    - To practice the full software lifecycle from design through implementation, testing, documentation, and publication to a public registry
    - To engage with open-source community norms by posting to a relevant forum, responding substantively to feedback, and maintaining a CONTRIBUTING.md with bug reporting and test execution instructions
    - To apply the course's governance and safety principles in a published GOVERNANCE.md that names what the agent does, what it must never be used for, who is responsible, and what known limitations could cause harm
    - To ground the artifact in the team's Stakeholder Brief and Literature Review, follow the Project Thread process standards, and communicate the result to technical and non-technical audiences using the Open Questions to assess growth (Goals 11, 12, 13, 14, 15)
  rubric:
    - weight: 17
      description: Design and Usefulness
      preemerging: The project idea is vague or duplicates an existing well-documented tool with no clear improvement; no evidence of gap verification
      beginning: A problem is identified and a target user is named, but the gap is asserted rather than verified with evidence (no linked community post, GitHub issue, or unanswered Stack Overflow question), or the scope is too large to complete in the semester
      progressing: The proposal identifies a genuine gap with at least one piece of linked evidence, names concrete target users with realistic use cases, and defines a minimum viable scope; the README makes the value proposition clear to a stranger but the stretch goals are vague or the closest alternative is not named
      proficient: The proposal identifies a gap that a stranger can independently verify — linking at least one community post, GitHub issue, or Stack Overflow question where a real person asked for what is being built; names the closest existing alternative and states the specific gap it does not fill; defines two to three user personas with realistic, specific use cases; sets a one-sentence minimum viable scope that is achievable before submission; names two to three specific stretch goals; the final README makes a compelling case to a user who has never heard of the course, with no jargon without definition
    - weight: 21
      description: Implementation and Code Quality
      preemerging: The core functionality does not work; code is absent or fails to run from a fresh checkout
      beginning: The project runs but contains hard-coded credentials or paths in committed files, lacks error handling for common failure modes, or implements only trivial functionality with no non-trivial features
      progressing: The core functionality works and implements at least one non-trivial feature; configuration is externalized to environment variables or a config file; exceptions are caught with located messages naming the file and line; code is readable but inconsistently organized across files
      proficient: The core functionality works reliably on a clean machine by following the README; at least one non-trivial feature (streaming responses, token-level authentication, persistent memory across sessions, or multiple integrated tools with error recovery) is fully implemented; all configuration is externalized with documented defaults and no hard-coded values in any committed file; exceptions are handled with located tracebacks; code is organized so a stranger can navigate it in under 5 minutes; model versions and random seeds are pinned in configuration
    - weight: 17
      description: Testing and CI
      preemerging: No tests exist; CI is absent or never ran
      beginning: One or two unit tests exist but CI is absent or consistently failing; LLM-dependent behavior is entirely untested
      progressing: Unit tests cover deterministic components with meaningful assertions; CI runs on every push; at least one LLM-dependent property test exists but the property is weakly specified (e.g., "output is not empty") rather than naming a structural behavioral contract
      proficient: All deterministic functions have unit tests with meaningful assertions (not "it ran without error" but "the output matches the expected JSON schema"); at least three property tests cover LLM-dependent components — each property test names a clearly stated behavioral contract that a stranger could read and understand, such as "every response includes a source citation", "the output is valid JSON matching the named schema", or "the agent declines requests containing the word 'illegal'" — all three properties must be non-trivially specified; CI runs the full suite on every push and the badge is green on the submission SHA
    - weight: 17
      description: Documentation and Publication
      preemerging: README is absent or consists of the project title only; the project is not published to any registry
      beginning: README exists but the quickstart requires more than 15 commands or fails on a clean machine; CONTRIBUTING.md is absent; governance statement is missing
      progressing: README quickstart works in under 10 minutes on a clean machine; CONTRIBUTING.md explains how to report bugs and how to run tests locally; governance statement exists but is generic (does not name specific prohibitions or a specific responsible person)
      proficient: README quickstart works in 5 commands or fewer on a clean machine — verified by a classmate cold-following it with the result documented; README contains a one-sentence description, the quickstart, a configuration reference for every env var with its type and default, at least two worked examples showing realistic usage, the registry package link, and the CI badge; CONTRIBUTING.md covers bug reporting (what to include and where to file), PR submission (branch naming, test requirements, review expectations), local test execution (exact commands from a clean checkout), and a one-paragraph code of conduct; the artifact is live and installable via the standard registry install command; license choice is justified in one paragraph naming what the choice means for potential users
    - weight: 13
      description: Governance, Safety, and Community Engagement
      preemerging: No governance statement published; project was not submitted to any registry or community; no community interaction occurred
      beginning: A governance statement exists in the repository but was not published or is not linked from the README; the project was pushed to GitHub but not submitted to a registry; a community post was made but no response to feedback occurred or the post misrepresents the artifact's capabilities
      progressing: GOVERNANCE.md is published and linked from the README; project is installable from at least one registry; at least one community post was made in an appropriate forum and at least one response was received, but engagement with feedback was superficial ("Thanks!")
      proficient: GOVERNANCE.md is published in the repository and contains four specific elements — what the agent does and does not do (scope), what the agent must never be used for with a stated reason for each prohibition, who is responsible and how to reach them, and known limitations that could cause harm if a user assumes they are not present; the project is findable and installable from at least one public registry (npm, PyPI, Docker Hub, or MCP marketplace); a community post accurately describing the artifact was made in an appropriate forum (r/LocalLLaMA, r/MachineLearning, a relevant Discord, or HN Show HN); at least one response was received and the student engaged with it substantively — acknowledging the substance of the feedback and either incorporating it, explaining why not, or filing an issue — with the exchange documented in the submission report with a screenshot or link
    - weight: 15
      description: Stakeholder Grounding, Multi-Audience Communication, and Process Quality (Goals 11, 12, 13, 14, 15)
      preemerging: The artifact shows no connection to the team's Stakeholder Brief or Literature Review, the presentation addresses only a technical audience, and no Project Thread process artifacts (decision log, signatures, AI-use disclosures) are present
      beginning: The gap is verified only against generic community posts with no connection to the Brief and Literature Review, or the Demo Day presentation lacks a non-technical stakeholder-facing segment or a disseminable artifact, or process artifacts are spotty across milestones
      progressing: The proposal integrates the Stakeholder Brief and Literature Review and Demo Day includes both technical and stakeholder-facing segments with a disseminable artifact, with minor gaps such as a thin multidisciplinary reflection, an incomplete GANTT-style timeline, or one milestone missing its AI-use disclosure
      proficient: The proposal integrates the Stakeholder Brief and Literature Review, connecting the verified ecosystem gap to the stakeholder problem and the gap the review identified (Goals 11, 12); process is visible throughout — decision log and role assignments are current, every team document names a primary author per section, every progress report carries all members' signatures, and an AI-use disclosure accompanies each milestone (Goal 13); Demo Day includes the live technical demo, a non-technical stakeholder-facing segment in plain language, and a disseminable artifact (poster, one-pager, or public project page) presenting the stakeholder context and a multidisciplinary reflection on how disciplines beyond CS shaped the design (Goal 14); the individual reflection uses the Open Questions to describe specific new understandings and growth (Goal 15); milestone work shows approach, professionalism/process, and product, and the grade record supports combining team output with individual contribution and individual understanding

tags:
  - project
  - open-source
  - agents
  - governance
  - community

---

<!-- Project Thread integration: original rubric weights before the Stakeholder Grounding / Multi-Audience Communication / Process Quality row was added were 20 / 25 / 20 / 20 / 15. -->

> **The Project Thread:** This track is the final stage of the semester-long [Project Thread](/Projects/PBLThread). Your proposal must build on your team's [Stakeholder Brief](/Assignments/StakeholderBrief) and [Literature Review](/Assignments/LitReview) — the gap your artifact fills should serve the community your stakeholder belongs to — your team operates under its signed charter and the [Team Playbook](/Projects/PBLThread), and Demo Day (wk15.0) addresses both technical and non-technical audiences. See the Thread hub for the semester map and assessment philosophy.

## Project Overview

This project track is for students who want to build something that outlasts the semester: a published, documented, reusable agent or agent component that real users could discover, install, and run. The deliverable is not a demo or a course submission — it is a **software artifact with a community presence**. By the end of the project, you will have a published package on a public registry, a README that a stranger could follow, a CI badge, a governance statement, and at least one authentic exchange with a real community member who responded to your post about it. You will practice the full lifecycle from identifying a gap in the ecosystem through shipping to a registry and responding to real feedback.

This is an **individual or pair project**. Pairs must document individual contributions clearly. Tasks touching sensitive data or making outbound API calls on behalf of users require instructor approval and must include a governance statement addressing those specific risks.

---

## Example Project: Ollama MCP Server for Course Feedback

To calibrate the expected level of ambition and documentation quality, here is a fully worked example at the proficient level.

**Artifact:** An MCP (Model Context Protocol) server that wraps a local Ollama instance and exposes it as a tool to Claude Desktop. This fills a real gap: at the time of the project, Ollama has no official MCP server, and several posts in the r/LocalLLaMA community ask for one.

**Gap verification:** The student searched npm and PyPI for "ollama mcp server" and found zero results. They searched r/LocalLLaMA and found three posts from the past month asking for exactly this. They linked these in their proposal.

**Minimum viable scope:** The server handles a single `generate` tool call, accepts `model` and `prompt` as parameters, streams the response back, and exits cleanly on error. That's it.

**Non-trivial feature implemented:** Streaming. Instead of waiting for the full response, the server streams tokens back to the client as they arrive, which makes it feel responsive for interactive use.

**Three property tests:**
1. "If the model name is not in `ollama list`, the server returns an error message containing the string 'model not found' rather than crashing."
2. "Every successful response is a valid JSON object with a `content` string field."
3. "If the Ollama server is not running, the server returns an error within 5 seconds rather than hanging indefinitely."

**Community engagement:** The student posted to r/LocalLLaMA with the title "I built an MCP server for Ollama — feedback welcome." Three people responded. One found a bug (the server crashed when Ollama returned an empty stream). The student filed an issue, fixed it, released `v1.0.1`, and replied with the fix link. That exchange is documented in the submission.

---

## Getting Started: First 5 Steps

1. **Find the gap before committing to a scope.** Before writing a single line of code, search npm, PyPI, Docker Hub, and the MCP marketplace for tools that do what you are thinking of building. Read the r/LocalLLaMA "weekly tools" threads. If something already exists and does the job well, find a different gap or a specific improvement you can make.
2. **Verify the gap is real, not imagined.** Find at least one community post, GitHub issue, or Stack Overflow question where a real person asked for what you are planning to build. Link it in your proposal. This is the difference between "I think people want this" and "people have asked for this."
3. **Define your minimum viable scope on day one.** The MVP is the smallest version that is genuinely useful. Write it as a one-sentence definition: "The MVP is an MCP server that handles a single `generate` call to a local Ollama model and returns the response." Everything beyond that is a stretch goal.
4. **Set up the repository structure before writing code.** Create: `src/` (or the appropriate source directory), `tests/`, `docs/`, `.github/workflows/ci.yml`, `README.md`, `CONTRIBUTING.md`, `GOVERNANCE.md`, `LICENSE`. Writing code into a properly organized repo is easier than reorganizing a finished project.
5. **Write your first test before your first function.** Pick the most important behavior of your artifact — the one that, if it doesn't work, nothing works — and write a test for it before the implementation exists. The test will fail (red). That failure is the starting point.

---

## Common Pitfalls

1. **Building a wrapper that wraps something that already exists.** An MCP server for the OpenAI API has been built many times. A scoped, opinionated wrapper for a specific use case (e.g., an MCP server for Ollama that enforces a local-only policy and refuses to send data to any external endpoint) is different. The test: would the README say something different from the READMEs of the three closest alternatives?
2. **Treating documentation as the last step.** The most common submission gap is a README that the author can follow but a stranger cannot. Write the quickstart section first, on day one, before you have built anything. It will describe what you intend to build. Update it as you build. The final README should be the document you would want to find if you discovered this tool on npm for the first time.
3. **Writing property tests that always pass.** A property test that says "the output is a string" will always pass unless the program crashes. A property test that says "the output is a valid JSON object with a `content` key that is a non-empty string, and the value of `content` contains at least one sentence-ending punctuation mark" is a real behavioral contract.
4. **Posting to the community and not following up.** Community engagement is graded on quality, not just occurrence. "Thanks!" in response to a bug report is not engagement. Engagement means: read the feedback, acknowledge its substance, and either incorporate it, explain why you chose not to, or file an issue for future work. The conversation is the deliverable.
5. **Choosing a license without understanding what it means.** MIT means anyone can use your code in a closed-source commercial product without attribution. AGPL means anyone who runs your code as a service must open-source their modifications. Apache 2.0 includes a patent grant that matters if you ever file patents. Read the first page of each before choosing. The justification paragraph is graded.

---

## Stage 1: Proposal (due week 10)

Identify a gap: an agent, tool, MCP server, or agent pattern that does not exist or is not done well. Write a two-page proposal containing all of the following.

**Proposal Checklist:**

By the end of Stage 1, you will have submitted a 2-page proposal covering:

- **What the artifact does:** One paragraph that a stranger with no course context can understand. No jargon without definition.
- **Who would use it:** Two to three **user personas** with realistic, specific use cases. Not "developers in general" but "a CS professor who wants to let students query their local Ollama instance through Claude Desktop without setting up API keys."
- **How they would install it:** The exact sequence of commands from a clean machine to a working demo. If you cannot write this on day one, your scope is undefined.
- **What makes it better than what already exists:** Name the closest alternative and the specific gap your project fills. Show evidence the gap is real (link the community post, the GitHub issue, or the unanswered Stack Overflow question).
- **Minimum viable scope:** The smallest version that is genuinely useful, achievable before the end of the semester. One sentence.
- **Stretch goals:** Two to three extensions that would make the project more capable if time allows.
- **Governance sketch:** Who is responsible for the deployed artifact? What must the artifact never be used for? What risk should the instructor know about before approving?
- **Stakeholder grounding:** How the verified ecosystem gap connects to your [Stakeholder Brief](/Assignments/StakeholderBrief) and [Literature Review](/Assignments/LitReview) — the problem in the stakeholder's terms, the gap your review identified, and who in the stakeholder's community would adopt this artifact (Goals 11, 12)
- **Implementation-and-assessment sketch:** Who holds which role at each stage, how progress will be assessed at each stage boundary, and a shared GANTT-style timeline mapping Stages 2 through 4 to weeks with named owners (Goal 13)

---

## Stage 2: Implementation (weeks 10 through 13)

Build the core functionality following the design-first discipline from class: write the interface before the implementation, and write at least one test before each non-trivial function.

**Implementation requirements:**

- Core functionality works on a clean machine by following the README
- At least one **non-trivial feature** is fully implemented: streaming responses, token-level authentication, persistent memory across sessions, or multiple integrated tools with error recovery
- **Unit tests** for all deterministic components with meaningful assertions (not "it ran without error" — "the output matches the expected JSON schema")
- **At least three property tests** for LLM-dependent components. A property test asserts a structural property of the output that should always hold — not an accuracy test, but a behavioral contract:

| Property Test Example | Why It Is a Good Property |
|---|---|
| "Every response includes a source citation" | Tests a structural requirement, not accuracy |
| "The output is valid JSON matching the schema" | Verifiable without knowing the "correct" answer |
| "The agent declines requests containing the word 'illegal'" | Tests a safety behavior, not quality |
| "Response time is under 30 seconds on the CI runner" | Tests a reliability property |

- **GitHub Actions CI** that installs dependencies, runs the test suite, and reports pass/fail on every pull request and push to main. The CI badge must be green on the submission SHA.
- Configuration externalized to environment variables or a config file with documented defaults; no hard-coded API keys or paths in any committed file
- Model versions and random seeds pinned in configuration so results are reproducible

**Stage 2 checkpoint:** By the end of week 11, you have a running MVP (core feature only), at least 3 tests (1 unit + 2 property), and CI set up with a green run on the MVP.

---

## Stage 3: Documentation (weeks 13 through 14)

Documentation is not optional polish — it is the primary interface between your artifact and the community that will use it. The rubric grades documentation as heavily as implementation.

**README.md** (required contents):
- A one-sentence description of what the artifact does
- A quickstart: the user reaches a working demo in **5 commands or fewer** on a clean machine (this constraint forces clarity)
- A configuration reference: every environment variable and config option, its type, its default, and what happens if it is omitted
- At least two worked examples showing realistic usage (not just `--help` output)
- A link to the published registry package
- The CI badge (copy the Markdown from your GitHub Actions workflow page)

**CONTRIBUTING.md** (required contents):
- How to report a bug: what information to include, where to file it
- How to submit a pull request: branch naming convention, test requirements, review expectations
- How to run the test suite locally: exact commands from a clean checkout
- Code of conduct: one paragraph minimum

**GOVERNANCE.md** (required contents):
- What the agent does and what it does not do (scope, in plain English)
- What the agent must never be used for, with reasoning for each prohibition
- Who is responsible for the deployed artifact and how to reach them
- How users should report harms or unexpected behavior
- Known limitations that could cause harm if a user assumes they are not present

**LICENSE**: Choose one of MIT, Apache 2.0, or AGPL. Justify your choice in one paragraph in the README. The justification must name what the choice means for potential users — not just which license "sounds right."

**Stage 3 checkpoint:** By the end of week 13, your README quickstart works in 5 or fewer commands on a classmate's clean machine. Test this by having a classmate follow it cold and documenting the result.

---

## Stage 4: Publication and Community Engagement (week 14 through 15)

### Publication Checklist

Before publishing, verify:
- [ ] Repository is on GitHub with proper directory structure (source, tests, docs, CI at top level)
- [ ] No credentials, API keys, or private paths are committed anywhere in the git history
- [ ] The published version matches the submission commit SHA
- [ ] The package is installable from a clean machine using the registry's standard install command

Publish to at least one registry:
- **npm** (for JavaScript/TypeScript tools or MCP servers): `npm publish --access public`
- **PyPI** (for Python packages): `python -m twine upload dist/*`
- **Docker Hub** (for containerized services): `docker push username/image:tag` and set to public
- **MCP plugin marketplace** if applicable

Tag the submission commit `v1.0.0`. This is the version a user would install.

### Community Engagement

Post to at least one relevant community:
- r/LocalLLaMA (local models and agent tools)
- r/MachineLearning or r/learnprogramming (for educational tools)
- A relevant Discord server (Ollama Discord, LangChain Discord, etc.)
- Hacker News in **Show HN** format: "Show HN: [What it does] – [link]"

**The post must:** accurately describe what the artifact does, link to the repository, and be honest about limitations. Do not oversell.

**Engagement requirement:** When you receive feedback — an issue, a comment, a question — respond substantively. "Thanks!" is not a response. Engagement means: acknowledge the substance of the feedback and either incorporate it, explain why you chose not to, or open a follow-up issue. Document the interaction in your submission: include a screenshot or link to the post, the feedback received, and your response.

If you receive no responses within one week of posting, post to a second community and document the attempt.

**Stage 4 checkpoint:** By submission, your package is installable from the registry, your CI badge is green, and you have at least one documented community exchange with a substantive response.

---

## Submission Deliverables (final class meeting and exam slot)

1. **The repository:** Public GitHub repo running from a fresh start following the README, with CI green on the submission SHA. Tag the submission commit `v1.0.0`.
2. **The published package:** A live URL on npm, PyPI, Docker Hub, or the MCP marketplace where the artifact is installable.
3. **The report** (3 to 5 pages):
   - What gap you identified and how you verified it was real
   - Key design decisions and their tradeoffs
   - Evaluation results from your property tests (pass rate, any failures found)
   - Documentation strategy and the result of the classmate quickstart test
   - License choice and justification
   - Governance rationale: why the prohibitions you chose are the right ones
   - Community engagement summary with evidence (screenshot or link, feedback received, your response)
   - Individual contribution statement
4. **The presentation** (8 minutes plus questions):
   - Live demo of the happy path
   - One known limitation or failure mode, disclosed honestly
   - Property test results (what you tested, what you found)
   - 60-second governance statement addressed to the audience as potential users
   - A **non-technical, stakeholder-facing segment** (plain language, no unexplained jargon): the stakeholder context — whose problem this serves and in their terms — what the artifact does for that community, what it must not be used for, and a brief **multidisciplinary reflection** on how disciplines beyond CS shaped the design (Goal 14)
5. **The disseminable artifact:** a poster, one-pager, or public project page (a well-crafted public README landing page qualifies) suitable for sharing with your stakeholder's community: the stakeholder context, what the artifact does, its limits, and how to get it (Goal 14)

---

## Frequently Asked Questions

**Q: I am not a strong programmer. Can I complete this project?**
A: Yes. The minimum viable scope is intentionally small, and the course teaches the design-first, agent-assisted workflow explicitly. The rubric grades design, documentation, governance, and community engagement — not just code. A simple MCP server that is extremely well-documented, tested, and published with a clear governance statement earns more than a complex one that is hard to install.

**Q: What if I build something and then discover it already exists?**
A: This is exactly why the proposal requires gap verification. If you discover a very close alternative mid-project, you have two options: pivot to a specific improvement or scoped variant that is meaningfully different, or document the gap closure as a finding (sometimes discovering that the gap has been filled is the research contribution). Do not submit work that you know duplicates an existing well-maintained tool without an explicit differentiation argument.

**Q: How specific do the property tests need to be?**
A: Specific enough that a failure would actually indicate a problem. A test that says "the output is not empty" will pass even if the output is garbage. A test that says "the output is a JSON object with a 'citations' key that is a list of at least one string" will fail if the agent forgets to include citations. The rubric rewards tests with clearly stated properties that a stranger could read and understand without asking you what they mean.

**Q: Can I build on an existing open-source project instead of starting from scratch?**
A: Yes, if you make a meaningful contribution and the original project's license permits it. Document clearly what was pre-existing and what you added. The rubric grades your contribution, not the base project.

**Q: What if my community post gets no responses?**
A: Post to a second community, document the attempt, and note in your submission that you did not receive engagement. The rubric rewards authentic engagement; it does not penalize you for a community that is slow to respond. If you post honestly and substantively and receive no response, that is itself a finding about the community.

---

## Reflection Prompts

Answer individually in your contribution statement:

- What gap did you find, and how did you verify it was real rather than imagined?
- Which engineering decision are you most proud of, and which would you make differently?
- What did community feedback teach you that you did not expect?
- Using the four Open Questions (*What should matter to me? How should we live together? How can we understand the world? What will I do?*), describe one specific new understanding and one area of growth or skill development from the Project Thread — from formation survey to Demo Day (Goal 15).
- Do you certify that your contribution statement accurately represents your own work? Please identify any and all portions of the project that were not originally created by you.
- Approximately how many hours did the project take you personally?
