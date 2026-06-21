---
layout: assignment
permalink: /Assignments/PhilosophyEssay
title: "CS357: Foundations of Artificial Intelligence - Written Assignment: Does It Matter If Machines Understand?"

info:
  coursenum: CS357
  points: 100
  goals:
    - To engage with foundational philosophical arguments about machine understanding and intelligence
    - To connect philosophical positions to practical implications for AI system design and deployment
    - To argue for a position with evidence from both philosophy and observed AI behavior
    - To examine the ethical implications of the position you take
  rubric:
    - weight: 25
      description: Philosophical Engagement
      preemerging: Named philosophical positions are absent or mischaracterized
      beginning: At least one named position is cited but engagement is superficial, restating the argument without analyzing it
      progressing: At least two named philosophical positions are cited and analyzed with reasonable accuracy; the essay shows awareness of objections to at least one position
      proficient: At least two named philosophical positions are cited, accurately characterized, and critically analyzed; the essay engages with a substantive objection to each and explains why the objection does or does not succeed, demonstrating genuine understanding rather than summary
    - weight: 25
      description: Argument Quality and Evidence
      preemerging: The essay does not arrive at a position, or the position is contradicted by the evidence presented
      beginning: A position is stated but the supporting argument is a string of assertions without evidence or logical structure
      progressing: The essay arrives at a clear position with a coherent argument; evidence is drawn from the readings but not always deployed precisely to support the specific claim being made
      proficient: The essay arrives at a clear, specific position defended by a logically structured argument; evidence from at least two readings is deployed precisely to support specific claims; the strongest counterargument is identified and addressed directly rather than dismissed
    - weight: 25
      description: Practical Implications
      preemerging: No connection is made between the philosophical argument and AI deployment or design
      beginning: A connection to a deployment scenario is mentioned but not developed
      progressing: The philosophical position is connected to a concrete AI deployment scenario with a plausible implication for design or practice
      proficient: The philosophical position is connected to a concrete AI deployment scenario with a specific, non-obvious implication for design or practice; the implication is one that would lead to different decisions than the opposing position would recommend, and the essay closes with one actionable guidance statement for CS357 students
    - weight: 25
      description: Writing Quality and Originality
      preemerging: The essay is largely a paraphrase of the readings without original analysis
      beginning: The essay contains original sentences but the argument structure is borrowed from a single source
      progressing: The essay is largely original with clear organization; prose is readable though some passages are imprecise or overlong
      proficient: The essay is original in argument and expression, precisely written at the right level of technicality for a CS audience without philosophy background, well-organized with a clear thesis in the introduction and a payoff in the conclusion, and between 1000 and 1500 words excluding references
  readings:
    - rtitle: "Turing, Computing Machinery and Intelligence (1950)"
      rlink: "https://doi.org/10.1093/mind/LIX.236.433"
    - rtitle: "Searle, Minds, Brains, and Programs (1980)"
      rlink: "https://doi.org/10.1017/S0140525X00005756"
    - rtitle: "Weizenbaum, Computer Power and Human Reason (1976), Chapter 6"
      rlink: "https://archive.org/details/computerpowerhum00weiz"
    - rtitle: "Mitchell, Artificial Intelligence: A Guide for Thinking Humans (2019), Chapter 8"
      rlink: "https://melaniemitchell.me/aibook/"

tags:
  - philosophy
  - ethics
  - written

---

Long before large language models existed, philosophers argued over whether any machine could genuinely understand language, experience consciousness, or be held accountable for its actions. Those arguments are no longer merely academic: the systems we build in this course process natural language, generate explanations, and take actions with real consequences. Whether or not those systems "really" understand turns out to matter — for how we design them, how we deploy them, and what obligations we take on when we do.

This assignment asks you to engage seriously with one of those foundational questions and arrive at a position that has consequences for your practice as an AI practitioner.

---

## How to Approach This Assignment

- **Pick the prompt you find genuinely interesting.** This sounds obvious, but it matters: the difference between an essay that earns proficient and one that earns beginning is almost always the difference between a student who is actually trying to answer the question and one who is trying to fill 1,000 words. Read all four prompts before choosing.
- **Argue, don't summarize.** Every paragraph should be doing one of these things: (a) presenting your thesis, (b) presenting a philosophical position that supports or challenges it, (c) objecting to that position, (d) explaining why the objection does or does not succeed, or (e) connecting your argument to a deployment scenario. If a paragraph is just describing what Turing or Searle said, cut it or transform it into analysis.
- **Define your terms early and use them consistently.** "Understanding," "consciousness," "intelligence," and "awareness" mean different things in different philosophical traditions. Choose one meaning for each term, state it in your introduction, and use it consistently throughout. Swapping definitions mid-essay is the single most common source of logical errors in philosophy papers.
- **Your conclusion should surprise a reader who read only your introduction.** A good philosophical essay does not end where it began — it arrives somewhere the introduction pointed toward but did not fully reveal.

> **Common Pitfall: Using "AI" and "consciousness" interchangeably without defining your terms.** Turing, Searle, and Weizenbaum are all talking about related but distinct things: Turing is asking about behavioral indistinguishability; Searle is asking about intentionality (genuine meaning); Weizenbaum is asking about appropriate delegation (what machines should be asked to do, regardless of what they can do). If you mix these up, your essay will argue past itself. Define what you mean by "understanding" in your first paragraph and stick to it.

**Recommended time budget:**
- Reading and annotation: 90 minutes
- Choosing a prompt and outlining: 30 minutes
- First draft: 90 minutes
- Revision (argument tightening, evidence deployment): 45 minutes
- Final proofread: 15 minutes

**What proficient work looks like:** A proficient essay takes a position that someone could reasonably disagree with, engages seriously with the strongest objection to that position (not a straw man), and closes with an implication specific enough that a student in CS357 would do something differently in their next project because of it.

---

## Thinking Through the Prompts: A Quick-Start Guide to the Philosophers

Before you choose a prompt, read these three-sentence summaries of each philosopher's core position. These are not substitutes for reading the texts — they are starting points so you are not beginning cold.

**Alan Turing (1950):** Turing argues that the question "can machines think?" is too philosophically loaded to be useful. He proposes replacing it with a behavioral test: if a machine can carry on a conversation that a human judge cannot distinguish from a human's conversation, then the machine is, for practical purposes, thinking. His key move is to say that the inability to distinguish behavior is sufficient — we should not require access to the internal experience, because we do not require that of other humans either.

**John Searle (1980):** Searle argues that behavioral indistinguishability is not sufficient for understanding. His Chinese Room thought experiment imagines a person in a room who manipulates Chinese symbols according to formal rules, producing outputs that look like fluent Chinese conversation — but the person (and therefore the room) does not understand Chinese. Searle's claim: syntax (the manipulation of symbols by rules) is not sufficient for semantics (genuine meaning). A system that passes the Turing Test might be doing exactly what the room does — and still understand nothing.

**Joseph Weizenbaum (1976):** Weizenbaum created ELIZA, one of the first conversational AI programs, and was disturbed by how readily users formed emotional attachments to it. His argument is not primarily about whether machines can understand, but about what we should ask them to do: some human activities — therapy, judgment, care — require genuine human understanding and empathy, and delegating them to machines, even capable ones, is a moral failure regardless of the machine's internal states. The question is not just "can it?" but "should we?"

---

## Suggested Essay Structure

This structure is a suggestion, not a requirement. Use it if you are unsure how to organize your argument; deviate from it if your argument calls for a different shape.

1. **Introduction** (~150 words): State your thesis (the position you will argue for) and the scope of your essay (which prompt, which philosophers you will engage with). Do not start with "Since the dawn of time..." or a dictionary definition. Start with the tension that makes your question interesting.
2. **Position A — with objection** (~250 words): Present the first philosophical position you are engaging with. Characterize it accurately. Then raise the strongest objection to it. Explain whether the objection succeeds.
3. **Position B — with objection** (~250 words): Present the second philosophical position. Characterize it accurately. Then raise the strongest objection to it. Explain whether the objection succeeds.
4. **Your position** (~200 words): State which position you find more convincing, and why. Engage with the strongest argument on the other side — do not just dismiss it.
5. **Practical implication** (~100 words): Connect your position to a specific AI deployment scenario. What would a developer or deployer do differently if they accepted your position?
6. **Conclusion** (~100 words): Restate your thesis in light of the argument you have made. Close with the one actionable implication for CS357 students.

---

> **What NOT to Do**
>
> - **Do not write a summary of the readings.** If your essay could be replaced by a Wikipedia article about Searle or Turing, it is not doing the required philosophical work. Every paragraph must be advancing your argument, not reporting what others argued.
> - **Do not conclude "both sides have merit."** This is the most common way to avoid doing philosophy. You must arrive at a position — a claim that someone could reasonably disagree with. "It depends on context" is also not a position unless you specify the conditions under which each conclusion holds and explain why those conditions matter more than the others.
> - **Do not use AI to generate your argument.** An AI-generated philosophical argument will look like a competent summary of the positions and a hedge at the end. It will not look like a student who has genuinely wrestled with a question and arrived at a view. The rubric specifically rewards originality of argument — not originality of prose style, but originality of the position and the reasoning behind it.

---

## Instructions

Write a 1000–1500 word essay (excluding references) on **one** of the following prompts. Choose the prompt you find most genuinely interesting; the best essays come from writers who actually want to answer the question.

---

### Prompt A

*"Searle's Chinese Room argument decisively shows that large language models do not understand language. Even if that is true, does it matter for how we deploy them?"*

Engage with Searle's original argument and at least one serious objection to it (for example, the Systems Reply or the Robot Reply). Then shift the question: grant for the sake of argument that Searle is right and LLMs do not understand. What follows for deployment? Does a system need to understand in order to be useful, trustworthy, or dangerous? Arrive at a position.

---

### Prompt B

*"The ELIZA effect — the human tendency to anthropomorphize AI systems — is not a bug but a feature: it makes AI systems more usable and more effective. Evaluate this claim."*

Engage with Weizenbaum's original concern about ELIZA and the broader literature on anthropomorphism in HCI and AI. Consider: what does "more usable" mean and for whom? Are there tasks where anthropomorphism improves outcomes, and tasks where it is actively dangerous? Arrive at a position that does not simply say "it depends" — identify the conditions under which each conclusion holds and explain why those conditions matter more than the others.

---

### Prompt C

*"If we cannot determine from behavior alone whether an AI system is conscious or sentient, what ethical stance should we take toward it?"*

Engage with the problem of other minds as it applies to AI systems, and with at least one framework for moral status (for example: sentience-based, interests-based, relational). Consider the asymmetry between the cost of wrongly treating a non-conscious system as conscious versus wrongly treating a conscious system as non-conscious. Arrive at a position and defend it against the strongest objection.

---

### Prompt D

*"Accountability requires understanding. Therefore, AI agents cannot be held accountable for their actions. Evaluate."*

Engage with what accountability requires — intent, understanding, or something else — drawing on at least one philosophical source and at least one AI deployment scenario where the question of accountability arose (for example: autonomous vehicle liability, content moderation errors, or AI-assisted medical decisions). Does the premise hold? Does the conclusion follow? Who *is* accountable if the agent is not, and is that answer satisfying?

---

## Requirements

Whichever prompt you choose, your essay must:

1. Engage with **at least two named philosophical positions or arguments**, with citation. You may draw from the required readings or from other sources you find; sources must be real and retrievable.
2. Connect the philosophical argument to **at least one concrete AI deployment scenario** — a real system, a realistic hypothetical, or a case from the news. The connection must be substantive, not decorative.
3. **Arrive at a position.** "Both sides have merit" is not a position. Your conclusion must be a claim that someone could reasonably disagree with.
4. Close with **one implication for CS357 students**: one thing a student building or deploying an AI system should do differently because of the position you have argued for.

---

## Common Mistakes

- **Using "AI" and "consciousness" interchangeably without defining your terms.** These are different concepts. Define what you mean by "understanding" in your first paragraph and hold to that definition.
- **Summarizing the philosophers rather than arguing with them.** The rubric rewards philosophical engagement, which means raising objections, explaining why they succeed or fail, and arriving at a view. Description earns beginning; analysis earns proficient.
- **Concluding "both sides have merit" or "it depends."** These are placeholders, not positions. Force yourself to make a claim someone could disagree with.
- **Writing a practical implication that is trivially obvious.** "We should be careful when deploying AI in high-stakes contexts" is not an implication — it follows from almost any philosophical position. Your implication should be specific enough that it would lead to a different decision than the opposing position would recommend.
- **Deploying evidence decoratively rather than precisely.** Quoting Searle in your introduction and Turing in your conclusion without connecting them to your argument earns beginning. Quoting a specific passage and then explaining exactly how it supports or undermines a specific claim in your argument earns proficient.

---

## A Note on AI Use

You may use AI tools for brainstorming or grammar checking, but the argument must be your own. An essay that summarizes AI-generated positions without genuine engagement will not satisfy the philosophical engagement or originality criteria. If you use an AI tool, note it briefly at the end of your essay and describe how you used it.

---

## Submission Instructions

Submit a single PDF. Include a references section at the end (not counted in the word count). Word count must appear at the top of the first page.

- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did it take you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
