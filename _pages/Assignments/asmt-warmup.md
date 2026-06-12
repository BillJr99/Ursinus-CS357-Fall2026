---
layout: assignment
permalink: /Assignments/Warmup
title: "CS357: Foundations of Artificial Intelligence - Warmup"

info:
  coursenum: CS357
  points: 25
  goals:
    - To set up the course toolchain and verify a working local AI environment
    - To establish a baseline reflection on your prior experiences and beliefs about AI agents
    - To form and charter your semester team
  rubric:
    - weight: 40
      description: Environment Setup and Verification
      preemerging: Little or no evidence that the environment was attempted
      beginning: Some components installed, but the verification transcript is missing or incomplete
      progressing: Ollama installed and verified with a transcript, with a minor omission such as a missing model listing or version information
      proficient: Ollama installed and verified with a complete transcript including model listing, version information, and a successful Python API call
    - weight: 40
      description: Reflection Essay
      preemerging: The reflection is missing or does not address the prompts
      beginning: The reflection addresses some prompts superficially
      progressing: The reflection addresses all prompts with specific examples, with limited connection to the course themes
      proficient: The reflection addresses all prompts with specific personal examples and makes a thoughtful connection to agency, trust, or responsibility
    - weight: 20
      description: Team Charter and Submission
      preemerging: An incomplete submission is provided
      beginning: The submission is provided but the team charter is missing or does not address role rotation
      progressing: The submission is complete with a charter that addresses roles and communication, with a minor omission
      proficient: The submission is complete, including a team charter covering role rotation, communication norms, and disagreement resolution
  readings:
    - rtitle: "Welcome Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-welcomeagents.md"
    - rtitle: "Mitchell, Prologue and Chapter 1"

tags:
  - intro
  - ai
  - agents

---

The purpose of this warmup is to make sure your tools work before the labs depend on them, to capture a snapshot of your current thinking about AI that we will revisit at the end of the semester, and to launch your team.

## Part 1: Tool Setup

Install [Ollama](https://ollama.com/download) on your own machine (or a lab machine if yours cannot run it; see me if you are unsure). Then:

1. Pull a small model: `ollama pull llama3.2`
2. Run a CLI sanity check: `ollama run llama3.2 "Say hello in five words."`
3. Verify the REST API responds: `curl http://localhost:11434/api/tags`
4. From Python, send one chat request using the `requests` library, as we did in class, and print the response.

Capture a transcript (copy-paste or screenshots) of all four steps, including the output of `ollama --version` and your operating system. **If any step fails, document the error verbatim, your hypothesis about the cause, and what you tried**; a well-documented failure with a follow-up plan earns full credit for that step.

## Part 2: Baseline Reflection

In approximately one page, address the following. There are no wrong answers; this is a baseline, not a quiz.

1. Describe your experiences with AI tools to date: which you use, for what, and one moment when an AI output surprised you (pleasantly or otherwise).
2. Define, in your own words as of today, what makes a system an "agent."
3. Name one task you would happily delegate to an AI agent and one you would not, and articulate the difference.
4. What is one thing you hope to be able to build by December?

## Part 3: Team Charter

With your assigned team, draft a one-page charter covering: how you will rotate the four POGIL roles, how you will communicate outside class, your norms for preparing before meetings, and how you will resolve technical and interpersonal disagreements. All members sign (typed names suffice).

## Deliverables

Submit a single PDF or markdown file containing your setup transcript, reflection, and team charter (one charter per team is fine; submit it with each member's individual work).

Please also answer the following questions in your submission:

- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
