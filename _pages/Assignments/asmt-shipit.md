---
layout: assignment
permalink: /Assignments/ShipIt
title: "CS357: Foundations of Artificial Intelligence - Ship It: Build, Test, and Publish One Artifact"

info:
  coursenum: CS357
  points: 100
  goals:
    - To carry one artifact from specification through testing and continuous integration to public publication
    - To practice the AI maker discipline in your chosen track, with the agent generating and the human specifying, verifying, and owning
    - To publish responsibly to a real registry or hosting platform (GHCR, Docker Hub, npm, or Cloudflare) with the human gate observed
    - To document the artifact for strangers with a readme and a disclosed AI contribution statement
  rubric:
    - weight: 30
      description: Specification and Verification Discipline
      preemerging: No specification preceded generation, and no systematic verification followed it
      beginning: A vague specification exists, with verification limited to the happy path
      progressing: A concrete specification (failing tests in Track A; an acceptance checklist with a stranger test in Track B) preceded generation, with verification evidence for most criteria
      proficient: The specification preceded generation and is submitted in its original form, every criterion has verification evidence, at least one deliberate misuse case is covered, and one specification gap discovered mid-project is documented with its repair
    - weight: 25
      description: Continuous Integration
      preemerging: No automated checking exists
      beginning: A CI workflow exists but does not run the project's real checks
      progressing: CI runs the real checks on every push, with one demonstrated red and one demonstrated green run
      proficient: CI runs the real checks on every push with demonstrated red and green runs, publication is gated on green plus a deliberate human act (a tag or merge), and the writeup identifies exactly where the human gate lives in the pipeline
    - weight: 25
      description: Publication Quality
      preemerging: Nothing was published, or the publication is broken for strangers
      beginning: The artifact is published but a stranger cannot use it from the public record alone
      progressing: The artifact is published, installable or reachable by a stranger, with versioning and a readme, with a minor gap such as missing license or visibility friction
      proficient: The artifact is published with semantic versioning, a license, a readme answering what, install, and use in thirty seconds, a pre-publication audit documented (dry run output or layer listing reviewed), and a verified stranger installation or visit by a classmate
    - weight: 20
      description: Writeup, AI Disclosure, and Submission
      preemerging: An incomplete submission is provided
      beginning: The submission is provided but the AI contribution statement or human-centric design evidence is missing
      progressing: The submission is complete with an AI contribution statement and design evidence, with at least superficial responses to the reflection prompts
      proficient: The submission is complete, the AI contribution statement honestly delineates agent work from human work, the human-centric design evidence covers the persona and at least one failure path, and the reflection prompts receive thoughtful answers
  readings:
    - rtitle: "The AI Maker Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-aimaker.md"
    - rtitle: "Publishing Your Work Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-publishing.md"
    - rtitle: "Hosting with Cloudflare Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-cloudflare.md"

tags:
  - publishing
  - ci
  - maker
  - individual

---

In this individual assignment you will carry one artifact — chosen by you — from a written specification through building with an AI agent, testing, continuous integration, and public publication under your own name. This is the maker's full arc compressed into one real, public, small artifact. By the end, something you built will exist in the world, installable or reachable by anyone, with your name on it. The rubric rewards discipline, not scope: a small, finished, well-tested, well-documented artifact earns more than an ambitious one that does not run. **Choose one track and one artifact**, and observe the standing course rule throughout: agents may prepare every step, but a human (you) runs every publish or deploy command.

---

## What a Strong Submission Looks Like

A strong submission has these qualities:

- **The specification preceded the artifact — with a timestamp to prove it.** The dated specification file is submitted in its original form, before any agent-generated code touches it. The rubric rewards the original spec even if it was imperfect; discovering and documenting a spec gap is a graded deliverable, not a failure.
- **CI is wired to reality, not a placeholder.** The GitHub Actions workflow runs the project's actual tests (or actual accessibility/content checks for Track B), not `echo "tests pass"`. The submission includes links or screenshots of one red run and one green run — the red run proves the CI was not trivially passing before the code worked.
- **A classmate confirmed it works cold.** The "stranger test" is documented: a classmate's GitHub username or name, what they installed or visited, and their one-line confirmation that it worked from the public record alone. This is not optional — it is what "published" means.
- **The AI contribution statement is honest and specific.** A weak statement says "I used AI to help build this." A strong statement says: "The agent generated the initial `handler.js` function and all three test files. I wrote the `config.json` schema and the README, and I rewrote the error handling in lines 44–62 of `handler.js` after the agent's version silently swallowed exceptions. I verified every test manually before pushing."

A weak submission has CI that passes immediately with no red run, a readme that only an author could follow, and an AI contribution statement that could apply to any project.

---

## Choose Your Track and Artifact

**Track A (software engineering background).** Choose one:
- A container image published to GHCR — a small useful service such as a rubric-checking API or a markdown linter for course conventions
- A scoped npm package with a working `bin` — a CLI utility you actually want to exist
- A Cloudflare Worker API — the gateway-facade pattern is a strong choice

Your specification instrument is a **failing test suite written before implementation**. The agent's job is to make the tests pass without modifying them.

**Track B (maker track, no coding background assumed).** Choose one:
- A static site deployed to Cloudflare Pages — a project page, a resource hub, or an interactive explainer built with an agent
- A simple Cloudflare Worker built entirely through agent collaboration — a JSON API for something you care about

Your specification instruments are an **acceptance checklist written before generation** and the five-questions instruction to your agent (what it should do, what it must not do, who will use it, what counts as working, and what the edge cases are).

Artifacts must be original, must not include course-restricted materials or anyone's personal data, and must carry a license. If your idea touches credentials, payments, or other people's private information, redesign or consult the instructor first — recognizing that boundary is part of the assignment.

---

## Stage 1: Specify (submit before building)

Write and date your specification before generation begins. The timestamp is part of the grade — post it to the assignment thread or commit it to the repository before any agent-generated code exists.

**Track A specification:**
Write your failing test suite. Tests should cover: the happy path, at least one edge case (empty input, malformed input), and at least one deliberate misuse case (input designed to trigger an error or unexpected behavior). Include a `spec.md` describing what the artifact should do in plain English — one paragraph per major feature.

**Track B specification:**
Write your acceptance checklist. Each item should be a falsifiable statement: "The page loads in under 3 seconds on a standard wifi connection," not "The page is fast." Also write: a one-paragraph persona (who uses this, on what device, under what pressure) and explicit expected behavior for at least one misuse case (what happens when someone submits an empty form, clicks an unexpected button, or uses the artifact in an unintended way).

**Both tracks:** State in your specification what "done" means — the specific condition under which you would consider this artifact ready to publish. You will compare your shipped artifact against this standard in the writeup.

---

## Stage 2: Build and Verify

Work with your agent against the specification.

**Track A:** Instruct your agent: "Make these tests pass without modifying the test files." Keep the conversation log or session notes. When the agent generates code, read it before running it. Verify every test passes. Run your misuse case. If you modify any agent-generated code, note what you changed and why.

**Track B:** Iterate against your checklist. For each failed checklist item, file a bug report in the agent conversation in what-I-did / what-I-expected / what-happened form. When all items pass, conduct the **silent stranger test**: give a classmate the public URL and nothing else. Watch (or ask them to document) what they do, where they get confused, and whether they complete the primary task without help. Log their experience.

**Both tracks:** Document one specification gap you discovered during building — a criterion you forgot to specify, a behavior you assumed but did not state, or a constraint you discovered mid-build. Show the original spec, the gap, and how you repaired the spec (not just the artifact).

---

## Stage 3: Continuous Integration

Add the automated check appropriate to your artifact.

**Track A:** A GitHub Actions workflow (`.github/workflows/ci.yml`) that installs dependencies, runs your test suite, and reports pass/fail on every push to `main` and every pull request.

**Track B:** A preview-deployment-plus-checklist pipeline, or an Actions-driven build check that verifies the site builds without errors and key content is present.

**Both tracks:**
- Demonstrate one **red run**: a commit that intentionally fails at least one check. Include the link or screenshot.
- Demonstrate one **green run**: the commit that makes all checks pass. Include the link or screenshot.
- Arrange the pipeline so that publication to the public registry requires CI green **plus** a deliberate human act (pushing a tag, merging to a release branch, or running a manual publish step). In your writeup, state in exactly one sentence where the human gate lives.

---

## Stage 4: Publish

Before publishing, conduct the pre-publication audit:
- **npm:** Run `npm pack --dry-run` and review the file listing. Verify no secrets, no test fixtures, no node_modules are included.
- **Container image:** Run `docker image inspect <image>` and review the layer listing. Verify no credentials or private data are in any layer.
- **Cloudflare:** Review the deploy directory listing before `wrangler deploy`. Verify no `.env` files or private keys are staged.

Document the audit output in your submission — this is not just a checklist item, it is evidence of the professional discipline the course requires.

Then publish:
- `npm publish --access public` (npm)
- `docker push` and set visibility to public (GHCR)
- `wrangler deploy` or `wrangler pages deploy` (Cloudflare)

**Versioning:** Start at `0.1.0`. Ship at least one subsequent patch release (`0.1.1`) so the version walk is demonstrated. Use semantic versioning: patch for bug fixes, minor for new features.

**Stranger confirmation:** A classmate must install or visit your artifact from the public record alone — no setup instructions from you, no personal help. They should use only your README. Their one-line confirmation ("I ran `npm install -g your-package` and `your-package --help` worked — [GitHub username]") goes in your submission.

---

## Deliverables

Submit a ZIP (or repository link plus PDF) containing:

1. The dated specification (original form, before generation)
2. The build transcript or session log (conversation with the agent, or commit history)
3. Verification evidence for every specification criterion, including the misuse case
4. For Track B: the stranger-test log (what your classmate did, where they got confused, what you changed as a result)
5. The CI workflow file and links or screenshots of one red run and one green run
6. The pre-publication audit artifact (the dry-run output, layer listing, or deploy directory review)
7. The public URL or registry name with install instructions
8. The classmate confirmation (one line, with their name or username)
9. A README suitable for strangers (what, install, use — answerable in 30 seconds)
10. An **AI contribution statement** honestly delineating what the agent produced, what you wrote or changed, and what you verified

Ensure reproducibility by pinning dependency versions and listing software version information (Node version, npm version, Docker version, or Wrangler version as applicable).

---

## Frequently Asked Questions

**Q: My CI keeps failing because of a flaky network call in my tests. What should I do?**
A: Mock the network call in tests. The specification discipline the course teaches requires tests that are deterministic. If a test depends on an external service, it should be mocked in the test suite and tested against the real service only in a separate integration test step that is clearly labeled as potentially flaky. Document the decision in your writeup.

**Q: What counts as a "deliberate misuse case"?**
A: An input or user action that is wrong, adversarial, or outside the happy path. Examples: an empty input field, an input that is 10,000 characters long, a file of the wrong type, a sequence of requests that tries to exhaust a rate limit. The requirement is that your specification named the case and your testing shows what the artifact does when it happens.

**Q: Do I really need to publish to a public registry? Can I just push to a private GitHub repo?**
A: No. The "stranger confirmation" criterion requires a classmate to install or visit from the public record alone, which means the artifact must be publicly accessible. A private repository does not satisfy this requirement.

**Q: Can my classmate "confirm it works" by email instead of in the submission?**
A: Include the confirmation in your submission, not just in email. Quote their exact words and identify them by name or GitHub username. The confirmation should describe what they did, not just say "it worked."

**Q: My Track B artifact is a static site. Do I still need to demonstrate CI?**
A: Yes. Even a static site can have automated checks: a build step that verifies the HTML is valid, a link checker, a content check that confirms key pages exist. The CI requirement applies to both tracks. Cloudflare Pages has built-in GitHub Actions integration that makes this straightforward.

---

## Reflection Prompts

- Where in this project did the agent's output most need you, and what would have shipped if you had not been paying attention there?
- Publication is effectively irreversible. Describe the moment you ran the publish command: what had to be true for you to feel entitled to run it, and is that standard now portable to bigger things?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
