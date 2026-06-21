<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-aieducation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# AI in Education: Opportunity, Disruption, and the Integrity Question

CS357 - Foundations of Artificial Intelligence / Agentic AI | Ursinus College

---

## POGIL Roles

This activity uses the **POGIL** (Process Oriented Guided Inquiry Learning) structure. Before beginning, assign one role to each group member:

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task, ensures everyone contributes, watches the clock |
| **Recorder** | Documents the group's answers and reasoning in writing |
| **Presenter** | Speaks for the group during class discussion, summarizes findings |
| **Reflector** | Monitors group process, notes what is working and what is not, leads the Reflection section |

> Rotate roles across activities so everyone practices each one.

---

## Model 1: What AI Is Changing in Education

AI is entering education in at least three distinct functional roles. Each role creates opportunities and introduces risks that are not always symmetrical — they often benefit different stakeholders.

**The Three Roles of AI in Education**

| Role | Opportunity It Creates | Risk It Creates | Example Tool | Who Benefits | Who May Be Harmed |
|------|----------------------|-----------------|--------------|--------------|-------------------|
| **Tutor** | 24/7 personalized explanations, adaptive pacing, immediate feedback | Over-reliance, shallow engagement, equity gaps in access | Khanmigo, Synthesis, AI tutors | Students with reliable devices/internet | Students without devices, connectivity, or digital literacy |
| **Content Generator** | Rapid lesson plan drafting, differentiated materials at scale, quiz generation | Homogenization of curriculum, reduced teacher agency, low-quality outputs at scale | Diffit, MagicSchool, ChatGPT | Teachers with high workloads | Students who need locally relevant, culturally responsive content |
| **Evaluator** | Immediate feedback on writing, scalable assessment at low cost | False positives, bias against non-native speakers, "teaching to the detector" | Turnitin AI, GPTZero, Grammarly | Administrators seeking scalability | Students flagged incorrectly; teachers who lose judgment authority |

### Critical Thinking Questions

**Question 1.** Personalized AI tutoring could theoretically help students in under-resourced schools receive the kind of individual attention previously available only to students with private tutors. What infrastructure would need to exist before this benefit could actually reach those students?

[[___ Your answer here ___]]

> Think about: reliable internet, device ownership, teacher training, language support, and whether AI tutors can account for home environments. What would it cost to provide that infrastructure, and who would pay?

---

**Question 2.** If AI can generate lesson plans, differentiated worksheets, and quiz questions on demand, what does the teacher's role become? Does this represent a reduction of the teacher's professional value, or a transformation of it?

[[___ Your answer here ___]]

> Consider: What does a skilled teacher do that a content generator cannot? How does this parallel other automation transitions (e.g., spreadsheets replacing manual bookkeeping)?

---

**Question 3.** Look at the "Who Benefits / Who May Be Harmed" column of the table. Notice that the same tool often helps one group while disadvantaging another. Who currently has meaningful access to high-quality AI tutoring tools, and who does not? What would equitable access require?

[[___ Your answer here ___]]

> Research prompt for your group: Khanmigo requires a Khan Academy account. GPT-4 access requires a paid subscription. What does free tier vs. paid tier mean for educational equity?

---

## Model 2: Academic Integrity in the Age of LLMs

### The Detection Arms Race

AI writing detectors attempt to identify AI-generated text by measuring statistical properties (token probability distributions, perplexity, burstiness). However, this has produced an escalating arms race:

- **AI detectors** (GPTZero, Turnitin AI, Winston AI) flag text with low perplexity and uniform sentence structure
- **Paraphrasing tools** (QuillBot, manual rewriting, style transfer prompts) restructure AI output to evade detectors
- **False positive problem**: legitimate human writing — especially by non-native English speakers, writers using formal register, or students writing in constrained academic style — is flagged as AI-generated

A 5% false positive rate sounds small. It is not small when applied to a classroom.

### Rethinking Assessment

Rather than investing in detection (which is losing the arms race), many educators argue the better design move is to create AI-resistant assessments — or assessments where AI assistance is part of the assignment, explicitly governed.

| Assessment Type | AI Can Do It? | AI-Resistant Variant | What It Actually Measures |
|----------------|---------------|---------------------|--------------------------|
| Take-home essay | Yes (easily) | In-class oral defense of the essay | Depth of understanding, ability to reason aloud |
| Multiple choice quiz | Yes (often) | Explanation of wrong answers / think-aloud | Conceptual clarity, not pattern matching |
| Code submission | Yes | Live code walkthrough, modification under observation | Ability to read, explain, and extend code |
| Lab report | Partially | Process log (timestamped notes, failed attempts) | Scientific reasoning, not just clean results |
| Research paper | Yes | Annotated bibliography + recorded literature discussion | Source evaluation, synthesis, judgment |

### Critical Thinking Questions

**Question 4.** A class of 30 students is assessed using an AI detector with a published 5% false positive rate. In expectation, how many innocent students will be flagged? What are the consequences for those students, and how should an instructor respond to a positive detection result?

[[___ Your answer here ___]]

> Compute: 30 × 0.05 = 1.5 students expected to be falsely accused per assessment. What does it feel like to be that student? What burden of proof applies?

---

**Question 5.** Research has shown that AI detectors disproportionately flag writing by non-native English speakers. Why might this be? What does this mean for using AI detectors in a diverse classroom or in international contexts?

[[___ Your answer here ___]]

> Hint: Non-native English writers often use more formulaic, lower-perplexity sentence structures as a learned safety strategy. AI detectors are calibrated on native English corpora. What statistical property is being measured, and who does the calibration disadvantage?

---

**Question 6.** Design an assessment for this course (CS357) that could not be completed on a student's behalf by an AI, even a very capable one. Be specific: what does the student have to do, what does the AI lack, and what would you as an instructor actually be measuring?

[[___ Your answer here ___]]

> Promising directions: oral defense, live debugging under time pressure, personal narrative tied to specific lab failures, real-time extension of their own code with justification.

---

### Multiple Choice Question

A student uses an LLM to brainstorm a list of possible thesis arguments for a paper, selects one they find compelling, and then writes all the prose themselves without copying any AI-generated sentences. Under most current academic integrity policies, this is:

[[ ]] Always plagiarism because AI was involved at any point in the process
[[ ]] Always acceptable because no text was copied from the AI
[[x]] Potentially acceptable or not depending on the specific policy, the instructor's guidance, and whether disclosure was required — illustrating why blanket "no AI" or "AI is fine" policies are insufficient
[[ ]] Irrelevant to integrity concerns because AI cannot generate genuinely good ideas

> **Why this answer?** Academic integrity policies are currently inconsistent, evolving, and often written before LLM brainstorming was a common practice. The same action may be permitted by one instructor and prohibited by another. This is a policy design problem, not just a student behavior problem. What would a better policy look like?

---

## Model 3: Designing for Learning, Not Just Output

### Bloom's Taxonomy Revisited Under AI

Bloom's Revised Taxonomy (Anderson & Krathwohl, 2001) arranges cognitive tasks from lower-order to higher-order:

**Remember → Understand → Apply → Analyze → Evaluate → Create**

A common argument is: "AI can handle the lower levels, so education should focus on the higher levels." But this argument collapses quickly on inspection: current LLMs can Analyze, Evaluate, and Create competently in many domains. What does that leave?

The answer may lie not in which cognitive level, but in **what the cognitive work is about**:

- **Metacognition**: thinking about your own thinking, knowing what you don't know
- **Judgment under uncertainty**: knowing when to trust AI output and when to verify it
- **Personal meaning-making**: connecting content to your own experience in ways that require you, not a token predictor
- **Ethical reasoning in context**: applying values to specific situations with real stakes

### The Metacognitive Layer

Learning to use AI well is itself a skill — and it is increasingly a professional one. This includes:

1. **Prompting**: articulating what you want precisely enough to get useful output
2. **Evaluating AI output**: knowing when the model is hallucinating, oversimplifying, or confidently wrong
3. **Knowing when to trust vs. verify**: domain-specific calibration of AI reliability
4. **Iteration**: refining based on AI feedback, not just accepting first output

### Critical Thinking Questions

**Question 7.** Take one of the written assignments from this course (or a CS course you have taken). Redesign it so that AI assistance does not trivialize the assessment — but do not simply ban AI. Instead, design the assignment so that a student who uses AI well and critically learns more than one who does not use it at all.

[[___ Your answer here ___]]

> Consider: What is the assignment actually trying to build in the student? What must the student contribute that no tool can?

---

**Question 8.** If "using AI well" is a learning outcome, what would you put on a rubric for it? What behaviors distinguish a student who uses AI as a shortcut from one who uses it as a thinking partner?

[[___ Your answer here ___]]

> Possible rubric dimensions: prompt specificity, critical evaluation of AI output, evidence of revision, integration of personal judgment, citation of AI use.

---

**Question 9.** This course's AI use policies were written at a particular moment in time. How should they evolve? Who should be involved in revising them, and on what timeline?

[[___ Your answer here ___]]

> Consider: students, instructors, department, accreditation bodies, industry partners. Who has standing to shape these policies? What happens when industry norms outpace institutional ones?

---

## Exercises

**Exercise 1.** Locate the academic integrity policy for this course (in the syllabus or course handbook). Read it carefully. Identify **two scenarios** it does not clearly cover — situations where a reasonable student could be uncertain whether AI use is permitted. Propose specific policy language that would fill each gap without being either too permissive or too restrictive.

> Deliverable: two scenario descriptions + two proposed policy additions, written in formal policy language.

---

**Exercise 2.** Take an essay prompt from this course (or create a plausible one). Submit it to an LLM and save the output. Then rewrite the result from scratch, replacing the AI's perspective with your own — your actual examples, your actual reasoning, your actual conclusions. When you are done, write a short reflection: What did you change, and why? What did the AI miss about your perspective that you had to add?

> Deliverable: the AI output, your rewritten version, and a 200-word reflection on what changed.

---

**Exercise 3.** Design a grading rubric for a process-based AI assignment. The assignment asks students to use an LLM to help solve a problem, but grades them on their prompting strategy, their critical evaluation of the AI's responses, their decision to accept or reject AI suggestions, and the quality of their final revision — not just the final output itself.

> Deliverable: a rubric with at least 4 criteria, 3 performance levels each, and a brief justification for why each criterion captures genuine learning.

---

## Reflection Prompt

You will graduate into a world where AI is a ubiquitous professional tool — present in writing, coding, analysis, design, and decision-making across nearly every field.

What does "knowing how to do it yourself" mean in that world? Is there still value in building skills that AI can perform? If so, where does that value come from — economic utility, cognitive development, personal identity, something else? And if not, what does education need to become?

Write at least 200 words. Be honest about your own uncertainty.

[[___ Your reflection here ___]]

---

## Further Reading

- Mollick, E. & Mollick, L. (2023). *Using AI to Implement Effective Teaching Strategies in Classrooms: Five Strategies, Including Spaced Practice, Retrieval Practice, Interleaving, Concrete Examples, and Dual Coding.* SSRN. https://doi.org/10.2139/ssrn.4391243

- Liang, W. et al. (2023). *GPT Detectors Are Biased Against Non-Native English Writers.* arXiv:2304.02819. https://arxiv.org/abs/2304.02819

- Anderson, L. W. & Krathwohl, D. R. (Eds.). (2001). *A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom's Taxonomy of Educational Objectives.* Addison Wesley Longman.

- Fishman, T. (2009). *We Know It When We See It Is Not Good Enough: Toward a Standard Definition of Plagiarism That Transcends Theft, Fraud, Kidnapping, and Copyrightism.* 4th Asia Pacific Conference on Educational Integrity.

- UNESCO. (2023). *Guidance for Generative AI in Education and Research.* UNESCO Publishing. https://unesdoc.unesco.org/ark:/48223/pf0000386693
