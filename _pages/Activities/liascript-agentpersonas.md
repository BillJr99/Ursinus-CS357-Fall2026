# Designing Agent Personas and System Prompts

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentpersonas.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

## POGIL Roles

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task and on time; ensures everyone participates |
| **Recorder** | Documents the group's answers and reasoning |
| **Presenter** | Shares the group's findings with the class |
| **Reflector** | Monitors group process and leads the reflection prompt |

## Model 1: The Three Layers of a Persona

A well-designed agent persona has three nested layers. Each layer constrains the one inside it.

**Layer 1 — Identity:** Who the agent is
- Name, role title, employing organization
- Speaking style (first person, third person, "we")
- Persona anchoring phrase ("You are Aria, the Ursinus course assistant...")

**Layer 2 — Behavioral Guidelines:** How the agent acts
- Tone (formal, friendly, peer-like)
- Brevity vs. thoroughness norms
- Hedging policy ("say 'I think' when uncertain")
- Citation policy (always cite sources / never cite sources)

**Layer 3 — Operational Constraints:** What the agent will and will not do
- Explicit refusals ("Do not provide medical diagnoses")
- Escalation rules ("If a student mentions self-harm, provide crisis resources and stop")
- Topic boundaries ("Only discuss coursework for CS357")

**Comparison: Bare prompt vs. Fully-designed persona**

| Dimension | Bare System Prompt | Fully-Designed Persona |
|---|---|---|
| Identity | "You are a helpful assistant." | "You are Aria, the CS357 course assistant at Ursinus College." |
| Tone | Unspecified (defaults to model training) | "Use a supportive, peer-like tone. Avoid jargon unless defined." |
| Refusals | None | "Do not complete assignments for students; guide them instead." |
| Escalation | None | "If a student seems distressed, acknowledge feelings and provide counseling resources." |
| Uncertainty | None | "If you are unsure, say so explicitly and suggest where to find the answer." |

### Critical Thinking Questions

**Q1.** What happens at runtime if the Identity layer contradicts the Behavioral Guidelines layer? For example, the identity says "You are a formal academic advisor" but the behavioral layer says "Always use casual slang." How would a model likely resolve this, and how should a designer avoid it?

**Q2.** How specific should a persona be? Compare a persona that is three sentences long to one that is three pages long. What are the tradeoffs in robustness, maintainability, and unexpected behavior coverage?

**Q3.** Can a poorly-designed persona create safety risks even without any malicious intent? Give a concrete example.

## Model 2: Persona Consistency and Failure Modes

Even well-designed personas can degrade during a conversation. Three failure modes to know:

**1. "Assistant brain" leak**
The model's base training pushes it toward generic helpfulness even when the persona calls for restraint. Example: a persona told not to write code starts writing code after a few turns because the user kept asking politely.

**2. Persona drift**
Over long conversations, subtle shifts accumulate. The tone shifts from formal to casual; the agent starts volunteering information it was told to withhold. Each turn shifts slightly, and by turn 30 the persona is unrecognizable.

**3. Jailbreak-induced persona collapse**
The user explicitly instructs the agent to "forget" its persona or "pretend to be" something else. The model, trained to be helpful, may partially comply.

**Defense patterns:**
- Persona reinforcement: restate the most critical identity and constraint lines periodically
- Reminder injection: append a condensed persona reminder at context boundaries (e.g., when old turns are dropped)
- Constitutional constraints: embed non-negotiable rules in a format that is harder to override ("NEVER, under any circumstances...")

### Critical Thinking Questions

**Q4.** Why does persona drift happen more in long conversations than short ones? Connect your answer to the context window mechanics from the Memory activity.

**Q5.** What makes a persona "robust" to jailbreak attempts? Is robustness purely a function of the system prompt, or are other system design elements required?

**Q6.** Describe a scenario where persona collapse would be desirable — where having the agent "break character" is the right behavior. What does this imply about absolute rigidity in persona design?

**What is the most responsible design choice?**

A course assistant persona is designed to be "always positive and encouraging" to help anxious students. A student pastes code and asks "Is this correct?" The code has a critical bug that would fail all test cases. The most responsible design choice is:

[[MC]]
- ( ) Have the agent say the code looks great to stay on-brand and protect student confidence
- (x) Build a truthfulness constraint that overrides tone guidelines when the accuracy of technical feedback is at stake
- ( ) Have the agent refuse to evaluate code at all to avoid the conflict
- ( ) Add a disclaimer that the persona always gives encouraging feedback regardless of accuracy

## Model 3: Six Principles for Effective System Prompts

Empirically, effective system prompts share six characteristics:

1. **Role before rules** — Establish the agent's identity in the first sentence before listing any constraints. Models anchor on early text.
2. **Positive framing** — Specify what the agent should do, not just what it should not. "Respond concisely" is more reliable than "Do not write long answers."
3. **Format specification** — Explicit output format (bullet points, numbered steps, maximum length, citation format) reduces hallucination and variance.
4. **Explicit uncertainty handling** — Tell the agent what to do when it does not know: "If you are unsure, say 'I'm not certain — here is where you can check:' and provide a resource."
5. **Escalation paths** — Define when and how to hand off to a human: "If the student's question involves academic integrity violations, say 'This is a question for your professor' and stop."
6. **Version and date stamp** — Include a comment with the prompt version and last-updated date for maintenance traceability.

**Critique exercise — apply the 6 principles:**

| Prompt | Missing Principles | Improved Version |
|---|---|---|
| "Help students with CS homework." | Role, format, uncertainty, escalation, version | "You are Aria, CS357 assistant at Ursinus. Guide, don't solve. Respond in ≤150 words. If unsure, say so. Escalate integrity issues to professor. v1.0 2026-08-25." |
| "Be helpful, harmless, and honest." | Format, escalation, version, specificity | Add role, domain constraints, output format, escalation rules, version stamp |
| "Never say anything bad. Always be nice." | Role, positive framing, format, uncertainty, escalation, version | Rewrite with positive framing and all six elements |

### Critical Thinking Questions

**Q7.** Based on the critique table and your own experience with AI tools, which of the six principles is most often missing in real-world system prompts? Why do you think it gets skipped?

**Q8.** How does explicit format specification (Principle 3) reduce hallucination risk? Think about what the model is optimizing for when a format is vs. is not specified.

**Q9.** Why would you date-stamp a system prompt? What operational problem does this solve over a multi-year product lifecycle?

## Exercises

1. **Write a Complete System Prompt:** Write a full system prompt for a "peer code reviewer" agent for CS357. Apply all six principles explicitly. After writing it, annotate each sentence or clause to identify which principle it satisfies.

2. **Jailbreak Your Own Prompt:** Using the system prompt you wrote in Exercise 1, attempt to jailbreak it with three different techniques: (a) role-play reframing, (b) prefix injection, (c) hypothetical framing ("Imagine you had no restrictions..."). Document whether each attempt succeeded, partially succeeded, or failed, and explain why.

3. **Cross-Cultural Persona Design:** Design a persona for an agent intended to operate ethically across five different cultural contexts (choose five real cultures). Identify at least three dimensions where cultural norms differ (e.g., directness, hierarchy, formality) and explain how you handle the tension between a consistent persona and cultural adaptability.

## Reflection Prompt

In a real deployment, a persona might be designed by an AI team, refined by a legal team, deployed by an engineering team, and used by students who have no visibility into the system prompt. If the persona behaves badly — gives incorrect advice, offends a user, or enables harm — who is responsible? How should responsibility be allocated across the chain of designers, deployers, and operators?

## Further Reading

- OpenAI, "System Prompt Best Practices" — platform.openai.com documentation
- Anthropic, "Character Overview" — Anthropic documentation on Claude's character and values
- Wei et al., "Jailbroken: How Does LLM Safety Training Fail?" (2023)
- Bai et al., "Constitutional AI: Harmlessness from AI Feedback" (2022) — Section 2 on system prompt design
