---
layout: assignment
permalink: /Assignments/CodingAgents
title: "CS357: Foundations of Artificial Intelligence - Lab: Coding Agents in Practice"

info:
  coursenum: CS357
  points: 100
  goals:
    - To use a coding agent (OpenCode or Claude Code) to implement a feature from a written spec
    - To design an agent system prompt that constrains the coding agent's behavior appropriately
    - To evaluate coding agent output for correctness, style, security, and test coverage
    - To document the agent's decision-making process and review its diffs before accepting
  rubric:
    - weight: 30
      description: Task Execution and Spec Fidelity
      preemerging: The agent was run without a written spec, or the resulting code does not match the spec in major ways
      beginning: A spec exists and the agent produced code, but significant gaps remain between the spec and the implementation and no follow-up iteration was attempted
      progressing: The agent produced code that matches most of the spec after at least one iteration, with a minor mismatch or missing error case remaining
      proficient: The final code faithfully implements every requirement in the spec, including error cases and testing criteria, and the connection between each spec requirement and the corresponding code is traceable
    - weight: 25
      description: Review and Diff Analysis
      preemerging: Diffs were accepted without review, or no critique document was produced
      beginning: A critique document exists but identifies only surface issues (e.g., formatting) and the follow-up prompt does not address substantive problems
      progressing: The critique identifies at least one correctness issue and one security or completeness issue, and the follow-up prompt addresses both, with a minor gap remaining
      proficient: Every proposed change is reviewed line by line, the critique document clearly categorizes findings (correct, wrong, missing, security risk), the follow-up prompt is precise, and the second diff shows measurable improvement
    - weight: 25
      description: Safety and Constraint Design
      preemerging: No system prompt was written to constrain the agent, or the system prompt is so vague it provides no actual constraints
      beginning: A system prompt exists with at least one constraint, but the agent violated it and the violation was not noticed or addressed
      progressing: The system prompt defines file scope, library choices, and at least one prohibition, and violations (if any) are identified in the critique document
      proficient: The system prompt defines file scope, library choices, and explicit prohibitions (e.g., no external network calls, must include tests), all constraints are verified against the agent trace, and any constraint violations are documented and remediated
    - weight: 20
      description: Documentation and Reflection
      preemerging: No pair log or annotated diff is submitted
      beginning: Artifacts are submitted but annotations are minimal and reflection prompts receive one-sentence answers
      progressing: The annotated diff identifies most significant changes with comments, the pair log shows at least two role swaps, and reflection prompts are answered with specific examples
      proficient: Every diff annotation explains the why not just the what, the pair log shows regular swaps with timestamps, the scanner output is included and addressed, and reflection answers demonstrate a changed mental model about coding agents
  readings:
    - rtitle: "Coding Agents Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-codingagents.md"
    - rtitle: "The Local Agent Stack Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md"

tags:
  - agents
  - coding
  - security
  - testing

---

In this lab, you and your partner will use a coding agent to implement a real feature from a written specification, then critically review, iterate, and harden the result. The skill being assessed is not whether the agent produces working code on the first try — it is whether you can evaluate, constrain, and direct it to reach a trustworthy outcome. This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

## Part 1: Design First (Before Any Agent Interaction)

Before the agent writes a single line, you write the specification. Produce a one-page written spec for a small program: **a REST API endpoint that takes a search query and returns summarized results from a local knowledge base**. Your spec must include the function signature, expected inputs and outputs with types, all error cases (empty query, no results, malformed input), and explicit testing criteria (what a passing test suite must cover).

Then write the **system prompt** you will give the coding agent. The system prompt must define which files the agent is allowed to touch, which libraries it must use (and which it must not), and at least one explicit prohibition (e.g., no external network calls, no hardcoded credentials, must include unit tests). Submit both the spec and the system prompt before running the agent.

## Part 2: First Agent Run

Run the coding agent (OpenCode, Claude Code in a container, or an equivalent tool approved by the instructor) with your spec as the task prompt and your system prompt as the system context. Capture the **full agent trace**: every file it reads, every edit it proposes, and every command it runs.

Do not accept any changes yet. Save the raw diff for Part 3 review. If the agent asks for clarification, answer only with information that was in your original spec — do not expand the spec mid-run.

## Part 3: Diff Review and Critique

Review every line of the proposed diff. Produce a **critique document** that categorizes each finding: what the agent did correctly, what is incorrect or broken, what is missing relative to the spec, and what poses a security or safety risk. Be specific — cite line numbers.

Write a follow-up prompt to the agent that addresses each substantive issue you found. Run the second agent iteration, capture its trace, and review the new diff. Note what improved and what (if anything) the agent got wrong again.

## Part 4: Verification and Hardening

Accept the final diff. Run the tests the agent wrote — do they pass, and do they actually cover the testing criteria in your spec? Add at least **two tests the agent missed**. Then run a linter (e.g., `flake8` or `eslint`) and a security scanner (e.g., `bandit` for Python or `npm audit` for Node) against the final code. Document every finding and address any high-severity issues.

## Deliverables

Submit a ZIP containing: your spec document, your system prompt, the first diff with inline annotations, the critique document, the second diff, the final accepted code, test output showing passing tests, linter and scanner output, and the pair log with role-swap timestamps.

## Reflection Prompts

- What did the coding agent do well that surprised you?
- Where did it make assumptions you had not anticipated, and how did those assumptions affect the output?
- How did your system prompt constrain its behavior — and what slipped through the constraints anyway?
- Would you trust this code in production? What specifically would need to change before you would?
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
