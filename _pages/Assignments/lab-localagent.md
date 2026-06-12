---
layout: assignment
permalink: /Assignments/LocalAgent
title: "CS357: Foundations of Artificial Intelligence - Lab 1: Your First Local Agent"

info:
  coursenum: CS357
  points: 100
  goals:
    - To implement the perceive, plan, act loop against a locally hosted language model
    - To design a system prompt that establishes a persona, tools, output format, and guardrails
    - To add a tool to an agent and parse structured actions safely
    - To evaluate agent behavior empirically, including failure modes and step budgets
    - To practice pair programming with driver and navigator roles
  rubric:
    - weight: 35
      description: Agent Loop Implementation
      preemerging: The agent loop fails to run due to major issues, or the program fails to run at all
      beginning: The agent loop runs but fails on the test goals due to one or more minor issues
      progressing: The agent loop runs correctly on the test goals, but would fail in a general case due to a minor issue such as fragile action parsing or a missing step budget
      proficient: A correct agent loop runs the test goals, enforces a step budget, parses actions robustly, and would be reasonably expected to handle the general case
    - weight: 20
      description: System Prompt and Persona Design
      preemerging: The system prompt is absent or does not constrain behavior
      beginning: The system prompt establishes a role but omits tools, format, or guardrails
      progressing: The system prompt addresses role, goal, tools, format, and guardrails with minor gaps
      proficient: The system prompt fully specifies role, goal, tools, format, and guardrails, and the writeup justifies each element with evidence from transcripts
    - weight: 20
      description: Evaluation and Failure Analysis
      preemerging: No evaluation is provided
      beginning: A few informal trials are described without a protocol
      progressing: A small task set with a defined metric is evaluated, with limited failure analysis
      proficient: A task set with a defined metric and fixed protocol is evaluated, at least two failure modes are documented with transcripts, and a mitigation is proposed and tested for one of them
    - weight: 15
      description: Code Quality and Documentation
      preemerging: Code commenting and structure are absent, or code structure departs significantly from best practice
      beginning: Code commenting and structure is limited in ways that reduce the readability of the program
      progressing: Code documentation is present that re-states the explicit code definitions
      proficient: Code is documented at non-trivial points in a manner that enhances the readability of the program, exceptions are handled with located error messages and tracebacks, and configuration is externalized
    - weight: 10
      description: Writeup, Reflection, and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup describing the solution, the pair programming log, and thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Agent Loop Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentloop.md"
    - rtitle: "Prompt Engineering Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-promptengineering.md"
    - rtitle: "Ollama API Documentation"
      rlink: "https://github.com/ollama/ollama/blob/main/docs/api.md"

tags:
  - agents
  - prompting
  - local-ai

---

In this lab, you and a partner will build a working agent from first principles: a loop, a prompt, a tool, and an evaluation. This lab is completed in **pairs using driver/navigator roles**: the driver types while the navigator reviews, questions, and consults documentation, and you must **swap roles at least every 30 minutes**, keeping a brief log of swap times and who held each role.

## Part 1: The Loop

Implement an agent loop in Python against your local Ollama server that:

1. Accepts a goal string and a configurable step budget (externalize the budget, model name, and temperature into a JSON configuration file).
2. Maintains a message history (memory) across steps.
3. Prompts the model to respond in a structured Thought/Action/Final Answer format.
4. Parses actions, executes them, and appends observations to memory.
5. Terminates on a final answer or budget exhaustion, reporting which occurred.

Wrap all network and parsing operations in exception handlers that print a located message (for example, `[lab1:run_agent] {e}`) followed by a traceback, and never silently swallow an error.

## Part 2: A Persona and Two Tools

Design an agent with a clear job: a campus study-skills coach, a recipe assistant, a workout planner, or a concept of your own (clear it with me if it touches sensitive domains). Write a complete system prompt with the five elements from class: ROLE, GOAL, TOOLS, FORMAT, GUARDRAILS.

Equip the agent with **two tools** of your design (for example, a calculator and a date utility, or a unit converter and a lookup table). At least one tool must take an argument that the model constructs. **In your writeup, explain how your system prompt advertises each tool to the model, and show one transcript where the model uses each tool correctly.**

## Part 3: Evaluate It

Construct a task set of at least eight goals with known correct outcomes, following the protocol from class: fixed temperature, fixed seed, defined metric. Report your agent's accuracy. Then:

- Document at least two distinct failure modes with transcripts (for example, an action parse failure, a tool misuse, a hallucinated final answer, or a budget exhaustion on a solvable task).
- Choose one failure mode, implement a mitigation (a prompt change, a parser hardening, a budget adjustment), and re-run the evaluation. **Report the accuracy before and after, and explain why the mitigation worked or did not.**

## Deliverables

Submit a ZIP containing your code, your JSON configuration file, your task set and results (CSV or markdown table), transcripts for the documented failures, your pair programming log, and a readme writeup (approximately two pages) describing your design, your evaluation, and your findings. Ensure reproducibility by fixing random seeds and listing software version information.

## Reflection Prompts

Answer in your readme:

- Where in your code does the agent perceive, plan, act, and remember? Point to line numbers.
- Your agent's "thoughts" shaped its actions. Describe one transcript where the stated reasoning and the chosen action did not match, if you observed one, and what that implies about trusting narrated reasoning.
- How did the driver/navigator structure change the code you wrote compared with working alone?
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
