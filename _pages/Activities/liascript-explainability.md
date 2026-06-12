# Explainability and Human-Centric Design
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-explainability.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-explainability.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Explainability and Human-Centric Design

The final design lecture asks the question your demo audience will ask next week: *why should I trust this?* **Explainability** is the engineering of justified trust: surfacing evidence, exposing reasoning, communicating uncertainty, and designing the human's role on purpose. We move from **kinds of explanation $\rightarrow$ what agents can honestly show $\rightarrow$ calibration $\rightarrow$ human-centric design heuristics for your demos**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today's models work directly on your project artifacts; bring a current transcript from your own system. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: What Counts as an Explanation

## 1. Three Honest Artifacts and One Caution

**Traces.** An agent's ReAct transcript (thoughts, tool calls, observations) is a genuine causal record of *what the system did*: which tools ran, with which inputs, returning which evidence. Traces are the workhorse of agent explainability, and you have been generating them since week 1.

**Citations.** A RAG answer that quotes its retrieved chunk lets a human verify the claim against the source *without trusting the model at all*. Verifiability is stronger than persuasiveness, which is why your Lab 2 grounding instructions matter more than eloquence.

**Uncertainty.** A system that says "low confidence" when it is more often wrong is *calibrated*. Calibration is measurable: bucket outputs by stated confidence and compare each bucket's claimed probability with its observed accuracy; the gap is the **calibration error**:

$$
\text{ECE} = \sum_b \frac{n_b}{N} \, \bigl| \text{acc}(b) - \text{conf}(b) \bigr|
$$

**The caution.** A model's *prose self-explanation* ("I concluded X because Y") is generated text, not a readout of computation; it can be a plausible story rather than the actual cause. Treat narrated reasoning as a claim to verify (against the trace, the citation, the tool log), not as ground truth. The honest hierarchy: tool logs > citations > traces > narrated rationale.

---

## Model 1: Audit Your Own Transcript

Each team examines one real transcript from its project system.

### Critical Thinking Questions

1. Classify every explanatory element in your transcript into the four categories above. Which categories are absent entirely?
2. Find one narrated rationale and attempt to verify it against harder evidence in the same transcript. Does the story check out?
3. Your demo audience includes non-programmers. Which single artifact (trace, citation, confidence) would most increase *their* justified trust, and how will you render it on screen?

---

# Part II: Designing the Human In

## 2. Heuristics for Human-Centric Agents

**Match autonomy to verifiability.** Where outputs are cheap to verify (a draft to read), grant autonomy; where verification is expensive or harm irreversible (sending, deleting, submitting), insert the human *before* the action, exactly your confirmation-gate taxonomy.

**Design for appropriate reliance, not maximal trust.** The failure modes are symmetric: over-reliance (rubber-stamping the agent) and under-reliance (ignoring a good tool). Friction is a design material: a confirmation that *shows the evidence* recruits the human's judgment; a bare "OK?" dialog trains them to click through.

**Disclose the system's nature.** Users deserve to know they are interacting with an AI system, what data it uses, and where its competence ends, which your governance document already commits you to; the design task is making the disclosure *legible*, not buried.

**Fail loudly and usefully.** "Not in my documents" (your Lab 2 abstention) beat a fluent guess; a good failure message names what was attempted and what the human can do next.

[[MC]]
An agent drafts emails and a human clicks approve. Over months, approvals become automatic and an erroneous email ships. The design lever that most directly targets this failure is:
- ( ) A larger model so errors stop occurring
- ( ) Removing the human gate since it added no value
- (x) Redesigning the confirmation to surface the evidence and anomalies that warrant attention, restoring active judgment
- ( ) Logging the human's click for accountability

---

## Model 2: The Confirmation Screen

Sketch (on paper) the confirmation screen your project shows a human before its most consequential action.

### Critical Thinking Questions

4. What evidence appears on your screen, and in what order? Apply the honest hierarchy from Part I.
5. What would make a busy user *stop* on the rare bad case while letting routine cases flow? Name one anomaly signal your system can compute (low retrieval similarity, judge disagreement, low confidence) and surface it.
6. Run the calibration exercise on your own system: for ten outputs where it stated confidence, compute the ECE buckets. Is your agent honest about what it knows?

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Trace viewer.* Add to your project the simplest possible "why" affordance: a collapsible pane showing the trace and citations behind each answer. Screenshot before and after.
2. *Abstention audit.* Construct five questions your system should refuse or qualify. Report its abstention rate and rewrite one prompt or policy to fix the worst failure.
3. *Demo dry run.* Deliver your 90-second explainability story (what the system shows, why a stranger should calibrate trust correctly) to another team. Collect and address one objection.
4. *Reliance experiment design.* Sketch a small study (n = 8 classmates) measuring over- and under-reliance on your system: task, conditions, and the one metric you would report. You need not run it; designing it is the point, and it is publishable thinking.

---

## Reflection Prompt

In your notebook: recall a system (human or machine) you trust appropriately: enough to use, alert to its limits. What earned that calibration: experience, transparency, accountability, or something else? Which of those can your project realistically offer its users by demo day?

---

## 4. Further Reading

- Doshi-Velez and Kim. "Towards a Rigorous Science of Interpretable Machine Learning." (2017).
- Amershi et al. "Guidelines for Human-AI Interaction." *CHI* (2019). Eighteen heuristics worth printing.
- Guo et al. "On Calibration of Modern Neural Networks." *ICML* (2017), source of the ECE formulation.
