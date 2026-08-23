<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-explainability.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-explainability.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Explainability and Human-Centric Design

Fresh from the *Governance and Policy Writing* and *Environmental Impact and the Carbon Cost of Intelligence* session, the final design lecture asks the question your Demo Day audience will ask: *why should I trust this?* **Explainability** is the engineering of justified trust: surfacing evidence, exposing reasoning, communicating uncertainty, and designing the human's role on purpose. We move from **kinds of explanation $\rightarrow$ what agents can honestly show $\rightarrow$ calibration $\rightarrow$ human-centric design heuristics for your demos**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today's models work directly on your project artifacts; bring a current transcript from your own system. After class, respond to the reflective prompt individually in your notebook.

---

### Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Explainability** | The property of an AI system that allows users and overseers to understand *why* the system produced a particular output, not just *what* the output was. | An agent that says "I found this answer in document X, paragraph 3" is more explainable than one that says "The answer is 42." |
| **Calibration** | The property of a system whose stated confidence matches its actual accuracy: when it says 80% confidence, it should be right about 80% of the time. A system is miscalibrated if it says "I'm confident" and is wrong half the time. | Checking whether your model's high-confidence answers are more accurate than its low-confidence answers is a calibration check. |
| **ReAct Trace** | A log of an agent's reasoning steps: each thought it had, each tool it called, the inputs it provided, and the output it received. The trace is a genuine causal record of what happened. | A ReAct trace for a research agent might show: Thought: "I need to find the author." Action: search("author of Frankenstein"). Observation: "Mary Shelley." |
| **Over-Reliance** | The failure mode where a human defers to an AI system's output without exercising independent judgment, treating AI as always correct rather than as one source of evidence to verify. | A student who copies a chatbot's answer without checking whether the cited paper actually exists is exhibiting over-reliance. |
| **Under-Reliance** | The failure mode where a human ignores or discounts a reliable AI system's output, losing the benefit of the tool entirely. | Dismissing a well-calibrated AI-assisted diagnosis tool because "I don't trust computers" when the system is demonstrably more accurate than unaided judgment. |
| **Expected Calibration Error (ECE)** | A number measuring how far off a model's stated confidence is from its actual accuracy, averaged across all confidence levels. An ECE of 0 means perfectly calibrated; higher is worse. | If your agent claims 90% confidence on 10 outputs but gets 6 right, its ECE contribution from that bucket is large; it was overconfident. |

---

# Part I: What Counts as an Explanation

In this Part, you will examine what kinds of evidence an AI system can honestly offer to support its outputs, and learn why some evidence is stronger than others. This matters because your demo audience will need a real reason to trust your system, and "it sounds right" is not one.

## 1. Three Evidence Artifacts and One Caution

Think about the last time you trusted a recommendation: from a friend, a review site, or a search engine. What made you trust it? Probably: you could see *why* the recommendation was made (evidence), you could verify it yourself (citations), and you had a sense of how reliable the source usually is (calibration). AI explainability engineering is about building exactly those three properties into your systems, so users have a real basis for trust, not just a confident-sounding answer.

**Traces.** An agent's ReAct transcript (ReAct standing for "Reason + Act," a prompting pattern that interleaves a model's thoughts with tool calls and their results) is a genuine causal record of *what the system did*: which tools ran, with which inputs, returning which evidence. Traces are the workhorse of agent explainability, and you have been generating them since *The Agent Loop: Perceive, Plan, Act* activity.

**Citations.** A RAG answer that quotes its retrieved chunk lets a human verify the claim against the source *without trusting the model at all*. Verifiability is stronger than persuasiveness, which is why your RAG Knowledge Base Lab grounding instructions matter more than eloquence.

**Uncertainty.** A system that says "low confidence" when it is more often wrong is *calibrated* (meaning its stated confidence matches its real accuracy; so an 80%-confident system is correct roughly 80% of the time). Calibration is measurable: bucket outputs by stated confidence and compare each bucket's claimed probability with its observed accuracy; the gap is the **calibration error** (ECE, Expected Calibration Error, a single number summarizing how far confidence deviates from accuracy across all confidence levels):

$$
\text{ECE} = \sum_b \frac{n_b}{N} \, \bigl| \text{acc}(b) - \text{conf}(b) \bigr|
$$

**The caution.** A model's *prose self-explanation* ("I concluded X because Y") is generated text, not a readout of computation; think of it like a student who writes a confident essay about a process they do not fully understand. It can be a plausible story rather than the actual cause. Treat narrated reasoning as a claim to verify (against the trace, the citation, the tool log), not as ground truth. The evidence hierarchy: tool logs > citations > traces > narrated rationale.

---

## Model 1: Audit Your Own Transcript

Why this matters: when your project demos in front of classmates, faculty, or future employers, the first question is almost always "how do I know this is right?" You need a real answer, not "trust me." The audit you conduct today gives you that answer, or reveals that you need to build better explanatory infrastructure before the demo.

Each team examines one real transcript from its project system.

### Critical Thinking Questions

1. Classify every explanatory element in your transcript into the four categories above (trace step, citation, uncertainty signal, narrated rationale). Which categories are absent entirely?

   *Hint: Go line by line through your transcript. Every "I think" or "I believe" is narrated rationale. Every tool call and its output is a trace step. Every document quote is a citation. A statement like "I'm not sure about this" is an uncertainty signal. Count what you find in each category.*

2. Find one narrated rationale and attempt to verify it against harder evidence in the same transcript. Does the story check out?

   *Hint: If the model says "I concluded X because the document says Y," find the place in the transcript where it actually retrieved the document. Does the retrieved text actually say Y? If it does not, you have found a case where the narrated rationale is a confabulation, a plausible-sounding story that does not match the actual evidence.*

3. Your demo audience includes non-programmers. Which single artifact (trace, citation, confidence) would most increase *their* justified trust, and how will you render it on screen?

   *Hint: Think about what a non-programmer can actually evaluate. They cannot check whether a trace step is logically correct. But they can click a link to a source document and read it. They can understand "I'm 70% confident in this answer." Choose the artifact that gives them something to do with it, not just something to look at.*

---

*With your team's transcript analyzed, you now know what your system currently shows users. In Part II you will apply that knowledge to design the human-facing side: when should a user see evidence, when should they confirm an action, and how do you avoid training them to click through without reading?*

# Part II: Designing the Human In

In this Part, you will move from analyzing what your system *can* show to deciding what it *should* show, and designing the moment when a human is asked to intervene. The goal is not maximum transparency but appropriate transparency: enough for users to trust the right things and question the right things.

## 2. Heuristics for Human-Centric Agents

The goal is not to make users trust your system more; it is to make them trust it *appropriately*: more on easy, well-evidenced tasks; less on difficult, uncertain ones. That asymmetric calibration is what separates a tool people use well from one they either blindly follow into errors or never use at all. Every heuristic below is a design choice that moves your system toward appropriate reliance.

**Match autonomy to verifiability.** Where outputs are cheap to verify (a draft to read), grant autonomy; where verification is expensive or harm irreversible (sending, deleting, submitting), insert the human *before* the action, exactly your confirmation-gate taxonomy.

**Design for appropriate reliance, not maximal trust.** The failure modes are symmetric: over-reliance (rubber-stamping the agent) and under-reliance (ignoring a good tool). Friction is a design material: a confirmation that *shows the evidence* recruits the human's judgment; a bare "OK?" dialog trains them to click through.

**Disclose the system's nature.** Users deserve to know they are interacting with an AI system, what data it uses, and where its competence ends. Your governance document already commits you to this; the design task is making the disclosure *legible*: prominent, plain-language, not buried in a footer.

**Fail loudly and usefully.** "Not in my documents" (your RAG Knowledge Base Lab abstention) beats a fluent guess; a good failure message names what was attempted and what the human can do next.

An agent drafts emails and a human clicks "approve" before each one is sent. Over months, approvals become automatic (the human stops reading them) and an erroneous email ships. The design lever that most directly targets this failure is:

[( )] Replacing the model with a more capable one; model accuracy is not the issue; the failure is that the human stopped engaging, not that the model stopped being right
[( )] Removing the human gate entirely since it added no value; this eliminates oversight and makes the system fully autonomous, which does not address the root cause of inattention
[(X)] Redesigning the confirmation to surface the evidence and anomalies that warrant attention, restoring active judgment
[( )] Logging the human's click for accountability and compliance; logging creates an audit trail after the fact but does nothing to prevent the next rubber-stamp approval from shipping another error

---

## Model 2: The Confirmation Screen

Sketch (on paper) the confirmation screen your project shows a human before its most consequential action.

### Critical Thinking Questions

4. What evidence appears on your screen, and in what order? Apply the evidence hierarchy from Part I.

   *Hint: The most trustworthy evidence goes first. If your system retrieved a document, show the specific passage. If it ran a tool, show what the tool returned. Put the model's narrated summary at the bottom, not the top; it is the least verifiable item.*

5. What would make a busy user *stop* on the rare bad case while letting routine cases flow? Name one anomaly signal your system can compute (low retrieval similarity, judge disagreement, low confidence) and surface it visually.

   *Hint: Think about how email spam filters work: routine messages flow through; suspicious ones get flagged. What is the equivalent of a spam flag for your system? When is the model less certain than usual, and how would you show that on the confirmation screen without alarming users on every click?*

6. Run the calibration exercise on your own system: for ten outputs where it stated confidence, compute the ECE buckets. Is your agent honest about what it knows?

   *Hint: Collect 10 outputs with stated confidence levels. For each, mark whether it was correct. Group them by confidence level (e.g., high/medium/low). In each group, compare the average stated confidence to the actual accuracy rate. If your "high confidence" outputs are only right 40% of the time, your system is overconfident.*

> **Common Misconception:** "A more detailed explanation always means a more trustworthy system." More words do not mean more transparency. A long, fluent paragraph explaining an AI's reasoning can be entirely confabulated, generated to sound plausible rather than to accurately describe the computation. The evidence hierarchy (tool logs > citations > traces > narrated rationale) matters precisely because length and fluency are not measures of accuracy. A single cited source the user can verify is worth more than three paragraphs of confident prose.

---

*You have now designed your confirmation screen and stress-tested your system's calibration. In Part III you will build real artifacts: a trace viewer, an abstention audit, and a demo dry-run. These convert today's analysis into deployable components.*

# Part III: Synthesis and Practice

In this Part, you will translate the analysis from Parts I and II into deployable artifacts: a trace viewer, an abstention audit, and a rehearsed demo story. Building these now means your system will be demonstrably explainable by demo day, not just theoretically so.

## 3. Exercises

1. *Trace viewer.*

   *What to do:* Add to your project the simplest possible "why" affordance: a collapsible pane showing the trace and citations behind each answer. Screenshot before and after.

   *Starter hint:* The minimum viable version is a styled `<details>` HTML element (or equivalent in your framework) that collapses by default and shows the raw ReAct trace when expanded. You do not need to make it beautiful; you need to make the evidence accessible. Add citation links to any retrieved document chunk.

   *You've succeeded when:* A user who receives an answer can click one element, see the tool calls and retrieved passages that produced it, and verify the answer against the sources, without reading any code.

2. *Abstention audit.*

   *What to do:* Construct five questions your system should refuse or qualify. Report its abstention rate and rewrite one prompt or policy to fix the worst failure.

   *Starter hint:* Design questions that are clearly outside your system's scope (out-of-domain topics), questions with no correct answer in your documents, and questions that require information your system does not have access to. For each, record whether the system abstained, qualified, or confidently confabulated. The confabulations are your highest-priority fixes.

   *You've succeeded when:* You can state the abstention rate across your five test cases, identify the pattern in the failures, and show a revised prompt or policy that improves the rate on at least one case, with evidence from a re-run.

3. *Demo dry run.*

   *What to do:* Deliver your 90-second explainability story (what the system shows, why a stranger should calibrate trust correctly) to another team. Collect and address one objection.

   *Starter hint:* Your story should cover three things: (1) what the system does when it is confident and correct; (2) what it does when it is uncertain; and (3) what it does when it cannot answer. If you cannot describe all three, your system is not ready for demo. Practice with someone who has not seen your project.

   *You've succeeded when:* The other team raises at least one objection you had not considered, and you can describe the design change (or disclosed limitation) that addresses it.

4. *Reliance experiment design.*

   *What to do:* Sketch a small study (n = 8 classmates) measuring over- and under-reliance on your system: task, conditions, and the one metric you would report. You need not run it; designing it is the point.

   *Starter hint:* Over-reliance studies typically compare performance with versus without AI assistance on tasks where the AI is sometimes wrong. Under-reliance studies measure whether users ignore correct AI outputs. A simple design: give 8 people 10 questions with your system's answers visible. Introduce 3 wrong answers. Measure: what fraction of participants caught the wrong answers (over-reliance check) and what fraction used correct AI answers they initially doubted (under-reliance check)?

   *You've succeeded when:* Your design specifies the task, the participant assignment, the AI conditions, and the one metric you would report, clearly enough that another researcher could replicate the study from your description.

---

## Reflection Prompt

*Personal:* Recall a system (human or machine) you trust appropriately: enough to use, but alert to its limits. What earned that calibration? Was it experience with the system over time, explicit transparency about how it works, accountability when it failed, or something else?

*Technical:* Which of the four explainability artifacts (tool logs, citations, traces, narrated rationale) does your project currently produce, and which is it missing? What would you need to add to make your system's outputs fully verifiable by someone who cannot see the source code?

*Societal:* Most users of AI systems have no access to traces, citations, or calibration scores. They see a confident answer. What obligations do AI builders have to surface explainability in ways that non-technical users can actually act on? Who is responsible for closing the gap between what AI systems *can* explain and what they *do* explain?

> *Hint:* Consider the analogy to nutritional labeling on food: the information exists but must be mandated and formatted to be actionable. Who mandated food labels, and what did the industry argue before it was required? Now ask: which stakeholder (developer, deployer, regulator, user) has the most leverage to close the explainability gap for AI, and which has the least incentive to do so voluntarily?

---

## -> Coming Up Next

The *Project Studio and Gallery Walk* sessions and Demo Day are next: dedicated build time, then the demos themselves. The explainability sections you drafted today feed directly into your final governance document and into the demo your audience will interrogate.

## Further Reading

- Doshi-Velez and Kim. "Towards a Rigorous Science of Interpretable Machine Learning." (2017).
- Amershi et al. "Guidelines for Human-AI Interaction." *CHI* (2019). Eighteen heuristics worth printing.
- Guo et al. "On Calibration of Modern Neural Networks." *ICML* (2017), source of the ECE formulation.
