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

This individual assignment is the maker's full arc compressed into one small, real, public artifact: you will specify it, build it with an agent, test it, put it under continuous integration, and publish it under your own name. Small and finished beats ambitious and abandoned; the rubric rewards discipline, not scope. **Choose one track and one artifact**, and observe the standing course rule throughout: agents may prepare every step, but a human (you) runs every publish or deploy command.

## Choose Your Track and Artifact

**Track A (software engineering background).** Choose one: a container image published to GHCR (a small useful service, such as a rubric-checking API or a markdown linter for course conventions); a scoped npm package with a working `bin` (a CLI utility you actually wanted); or a Cloudflare Worker API (the gateway-facade pattern is a strong choice). Your specification instrument is a failing test suite written before implementation.

**Track B (maker track, no coding background assumed).** Choose one: a static site deployed to Cloudflare Pages (a project page, a resource hub, an interactive explainer built with an agent); or a simple Cloudflare Worker built entirely through agent collaboration (a JSON API for something you care about). Your specification instruments are an acceptance checklist written before generation and the five-questions instruction to your agent.

Artifacts must be original, must not include course-restricted materials or anyone's personal data, and must carry a license. If your idea touches credentials, payments, or other people's private information, redesign or consult the instructor first; recognizing that boundary is part of the assignment.

## Stage 1: Specify (submit before building)

Write and date your specification: Track A's failing tests or Track B's checklist, plus a one-paragraph persona (who uses this, on what device, under what pressure) and explicit behavior for at least one misuse case (empty input, absurd input, the wrong button). Post it to the assignment thread before generation begins; the timestamp is part of the grade.

## Stage 2: Build and Verify

Work with your agent against the specification (Track A: "make these tests pass without modifying them"; Track B: iterate against the checklist with bug reports in the what-I-did, what-I-expected, what-happened form). Keep the transcript or session log. Verify every criterion, run your misuse case, and for Track B conduct the silent stranger test and log it. Document one specification gap you discovered and how you repaired the spec, not just the artifact.

## Stage 3: Continuous Integration

Add the automated check appropriate to your artifact (a GitHub Actions test workflow for Track A; a preview-deployment-plus-checklist pipeline, or an Actions-driven build check, for Track B). Demonstrate one red run and one green run, and arrange the pipeline so publication requires green **and** a deliberate human act. State in your writeup, in one sentence, where the human gate lives.

## Stage 4: Publish

Conduct the pre-publication audit from the publishing module (the `npm pack --dry-run` review, the image layer listing, or the deploy-directory review), then publish: push the image and set visibility, `npm publish --access public`, `wrangler deploy`, or `wrangler pages deploy`. Versioning is semantic and starts at 0.1.0; ship at least one subsequent patch release so the version walk is demonstrated. A classmate must then install or visit your artifact cold, from the public record alone, and confirm it works; their one-line confirmation goes in your submission.

## Deliverables

Submit a ZIP (or repository link plus PDF) containing: the dated specification; the build transcript or session log; verification evidence for every criterion including the misuse case (and the stranger-test log for Track B); the CI workflow with red and green run links or screenshots; the pre-publication audit artifact; the public URL or registry name with install instructions; the classmate confirmation; a readme suitable for strangers; and an **AI contribution statement** honestly delineating what the agent produced, what you wrote or changed, and what you verified. Ensure reproducibility by pinning versions and listing software version information.

## Reflection Prompts

- Where in this project did the agent's output most need you, and what would have shipped if you had not been paying attention there?
- Publication is effectively irreversible. Describe the moment you ran the publish command: what had to be true for you to feel entitled to run it, and is that standard now portable to bigger things?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
