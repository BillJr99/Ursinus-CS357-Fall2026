---
layout: assignment
permalink: /Assignments/PromptPatterns
title: "CS357: Foundations of Artificial Intelligence - Written Assignment: Prompt Patterns and AI by Hand"

info:
  coursenum: CS357
  points: 100
  goals:
    - To design and document reusable prompt patterns including personas, few-shot examples, and structured output
    - To demonstrate empirically how prompt elements change model behavior
    - To compute softmax with temperature and a cosine similarity by hand, in the AI by Hand tradition
    - To connect by-hand mathematics to observed sampling and retrieval behavior
  rubric:
    - weight: 35
      description: Prompt Pattern Portfolio
      preemerging: Few or no patterns are presented, or patterns lack any demonstration
      beginning: Patterns are presented but demonstrations are missing or do not isolate the pattern's effect
      progressing: All required patterns are presented with before and after demonstrations, with limited analysis of why each works
      proficient: All required patterns are presented with controlled before and after demonstrations, and each is analyzed with reference to the distributional behavior of language models
    - weight: 35
      description: AI by Hand Worked Problems
      preemerging: Worked problems are missing or fundamentally incorrect
      beginning: Worked problems contain arithmetic or conceptual errors, or omit intermediate steps
      progressing: Worked problems are correct with all intermediate steps shown, with a minor omission
      proficient: Worked problems are correct with all intermediate steps shown, and each is verified in code with matching results and a sentence connecting the math to observed model behavior
    - weight: 20
      description: Analysis and Synthesis
      preemerging: Little or no written analysis is provided
      beginning: Analysis restates results without interpretation
      progressing: Analysis interprets results and connects at least one finding to course concepts
      proficient: Analysis interprets results, connects findings to sampling theory and persona effects, and proposes one testable hypothesis for future investigation
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The work is submitted, but not according to the directions in one or more ways
      progressing: The work is submitted according to the directions with a minor omission or correction needed
      proficient: The work is submitted according to the directions, well organized, with thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Prompt Engineering Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-promptengineering.md"
    - rtitle: "Sampling and Generation Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-samplinggeneration.md"
    - rtitle: "AI by Hand, Tom Yeh"
      rlink: "https://www.scribd.com/document/726922630/AI-by-Hand-Vol-1"

tags:
  - prompting
  - written
  - ai

---

This written assignment has two complementary halves: a portfolio demonstrating that you can *engineer* model behavior with prompts, and a set of by-hand computations demonstrating that you understand *why* the knobs you turned behave as they do.

## Part 1: Prompt Pattern Portfolio

For each of the following four patterns, present (a) a baseline prompt, (b) the pattern-enhanced prompt, (c) the two outputs from your local model at identical sampling settings, and (d) a short paragraph analyzing the difference and the mechanism behind it.

1. **Persona and role.** Design a persona for a domain you know well, and show a question where the persona materially changes the response.
2. **Few-shot examples.** Choose a formatting or transformation task the bare model performs inconsistently, and show that two or three examples stabilize it.
3. **Structured output.** Demand a JSON schema and demonstrate that a Python `json.loads` call succeeds on the output across five runs. Report the parse success rate before and after the pattern.
4. **Guardrails.** Add a refusal or escalation instruction and demonstrate one case where it triggers correctly and one attempted circumvention, with the outcome.

Use a fixed temperature and seed for all comparisons so the pattern, not the sampling, explains the difference, and state your protocol at the top of the portfolio.

## Part 2: AI by Hand

Complete both problems with all intermediate steps shown (handwritten and scanned, or typeset, your choice), then verify each in a short Python snippet.

1. **Softmax with temperature.** Given logits $z = (4, 2, 1)$ for tokens A, B, and C, compute the full probability distribution at $T = 1$, $T = 0.5$, and $T = 2$. Show the exponentials, the normalizing sums, and the final probabilities to three decimal places. In two sentences, state what your numbers demonstrate about temperature and the tail of the distribution.
2. **Cosine similarity.** Given $\mathbf{a} = (2, 1, 0, 2)$ and $\mathbf{b} = (1, 1, 1, 1)$, compute the dot product, both norms, and the cosine similarity. Then compute the similarity of $\mathbf{a}$ with $3\mathbf{a}$ and explain in one sentence why the result is what it is, and why that property matters for comparing texts of different lengths.

## Deliverables

Submit a single PDF containing the portfolio, the worked problems with verification code and outputs, and your reflections. Ensure reproducibility by fixing random seeds and listing software version information.

## Reflection Prompts

- Which pattern produced the largest behavioral change for the smallest prompt change, and why do you think that is?
- After computing softmax by hand, restate in your own words where the "randomness" in a language model lives.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
