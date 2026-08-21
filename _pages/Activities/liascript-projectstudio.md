<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-projectstudio.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-projectstudio.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Project Studio and Gallery Walk

With the bias, explainability, and governance work of the last three weeks behind you, today the classroom becomes a studio: structured work time, a formal **gallery walk** peer review, and a release-readiness checklist that converts feedback into your final sprint's backlog. The arc: **stand-up $\rightarrow$ gallery walk $\rightarrow$ triage $\rightarrow$ release checklist**.

---

## Directions and Group Roles

Project roles (rotated by sprint) are in effect today: **Coordinator**, **Builder(s)**, **Evaluator**, **Scribe**. The Scribe maintains today's living document: stand-up notes, every piece of gallery feedback verbatim, and the triaged backlog you leave with.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Stand-up** | A brief, structured team status check (each person answers the same fixed questions in two minutes or less) designed to surface blockers and share numbers, not to impress anyone | "The evaluation harness reports 73% tool-call accuracy on our test set. The riskiest unfinished piece is the citation pane." |
| **Gallery walk** | A peer review format where teams rotate between each other's live demos and leave structured written feedback, the academic equivalent of a design critique or code review | Walkers leave one index card per station with exactly three fields: Strength, Question, Risk |
| **Triage** | Sorting all feedback into exactly three buckets based on severity and scope: the discipline of deciding what must be fixed, what must be disclosed, and what must be deferred | Feedback: "The retrieval returns empty results for short queries" -> Fix before demo |
| **Release-readiness checklist** | A concrete, signed-off list of verifiable conditions that must be true before a system is shown publicly, borrowed from software engineering's definition-of-done practice | Six items, each checkable with a yes/no answer, signed off by the Evaluator |
| **Known failure case** | A defect or limitation that the team has identified, documented, and can demonstrate on demand, as opposed to a hidden failure discovered by someone else during the demo | "When the knowledge base has fewer than three documents, the system returns a hallucinated citation" |
| **Reproducibility** | The property that another person following your written setup steps, on a fresh machine, gets the same results you do; requires fixed seeds, pinned model versions, and documented steps | Teammate who did not write the setup document successfully runs the system from scratch using only the README |

---

In this first section, each team answers four fixed questions in two minutes, no more. You will use the stand-up to surface the current state of your project: real metrics, real blockers, and the single riskiest unfinished piece. Getting this right before the gallery walk helps you direct visitors toward the things that most need feedback.

## Model 1: Stand-Up and Readiness Assessment

Stand-ups exist to surface the truth quickly. The instinct to say "it's going pretty well" instead of "the evaluation harness reports 41%" is understandable but counterproductive; the whole point of a stand-up is to get the real number into the room so the team and instructor can help. Think of it as a 120-second system health check: inputs (what you did), outputs (what the numbers say), and blockers (what is in the way).

### 1. Stand-Up (10 minutes)

Each team answers, in two minutes at the board, exactly four questions: What works end-to-end today? What is the riskiest unfinished piece? What did your evaluation harness report this week (a number, not an adjective)? What do you need from the instructor or another team? Stand-ups are status synchronization, not performance; the discipline is *saying the number*.

### Critical Thinking Questions

**Question 1.** Your team's evaluation harness reports a metric (e.g., 68% retrieval precision, 3.2/5 average response quality). Before the stand-up, your Coordinator says "let's say it's around 70%; sounds better." What is wrong with this approach, and what is the actual function of reporting the exact number?

[[___ Your answer here ___]]

*Hint:* Who else in the room might be able to help your team improve that metric if they know the exact number? What decisions (about where to spend the final sprint) depend on the accurate number? Consider also: if the number is 68% and the threshold for a good demo is 75%, rounding to "around 70%" hides the gap that needs to be closed.

**Question 2.** "The riskiest unfinished piece" requires the team to have already thought about failure modes. List three categories of risk that are common in AI systems but often go unmentioned in student project stand-ups, and explain why each one is hard to surface without explicitly asking for it.

[[___ Your answer here ___]]

*Hint:* Think about risks that are not visible until something goes wrong: latency (the system is slow on long documents), edge cases (what happens when the user asks a question the system was not designed for), and dependency risks (what if the external API the system relies on changes its pricing or rate limits before demo day)?

---

*You have surfaced your team's blockers and metrics in the stand-up. Now it is time to leave your station and critically evaluate other teams' work, and to host visitors to your own. The gallery walk format gives everyone structured roles and a specific three-field card to fill out, so no feedback is wasted on vague praise.*

## Model 2: Gallery Walk Protocol

The gallery walk is structured exactly so that you get useful feedback rather than polite feedback. The card format forces specificity: "good job on the UI" does not help anyone; "the citation pane made the RAG answer checkable in one glance" is a named strength that can be preserved and built on. Similarly, "the demo looked fine" is not a risk assessment; "the system fails silently when retrieval returns nothing" is a named risk with a clear fix path.

### 2. Gallery Walk Protocol (40 minutes)

Stations: each team's system runs live with its one-page architecture diagram and its current evaluation table beside it. Half of each team hosts; half walks (swap at the midpoint).

Walkers leave structured feedback on cards, one card per station, with exactly three fields:

- **Strength**: one specific thing that works, named precisely ("the citation pane made the RAG answer checkable in one glance").
- **Question**: one genuine question the demo raised, ideally about a seam, a failure mode, or governance ("what happens when retrieval returns nothing?").
- **Risk**: the one thing most likely to fail on demo day, stated kindly and concretely.

Hosts demonstrate honestly: at least one *known failure case* (a defect or limitation your team has already identified, documented, and can reproduce on demand, the opposite of a surprise discovered mid-demo) must be shown at every station. A demo that hides its failure modes is rehearsing a deception, and your governance documents say otherwise.

### Critical Thinking Questions

**Question 3.** As a walker: across all stations, which *pattern* from Unit 3 appeared most often, and where did you see one misapplied (a planner where a pipeline would do)?

[[___ Your answer here ___]]

*Hint:* Recall the patterns from Unit 3: pipeline, planner, parallel specialist, self-critique, and human-in-the-loop. A "planner where a pipeline would do" means a team added dynamic task-planning overhead to a sequence of steps that is always the same; the planner adds cost and complexity without adding flexibility. Look for systems where the agents always take the same steps in the same order: that is a pipeline, not a planner problem.

**Question 4.** As a host: which visitor question exposed something your team had not considered? The Scribe records it verbatim; it likely belongs in your report's limitations section.

[[___ Your answer here ___]]

*Hint:* Questions that expose unconsidered failure modes often come from users who tried to use your system in a way you did not design for. Did any walker try to paste a very long input, ask about a topic outside your training data, or ask what happens when the system is wrong? The question that makes you say "we actually don't know" is the most valuable one.

**Question 5.** Which team's explainability affordance (trace, citation, confidence display) would you steal, and how would it fit your system?

[[___ Your answer here ___]]

*Hint:* Explainability affordances are the parts of a system that help users understand *why* it said what it said. A trace shows the reasoning steps; a citation shows which source the answer came from; a confidence display shows how certain the model is. Think specifically: if you integrated the affordance you admired into your own system, what would need to change in your architecture to support it?

---

> **Common Misconception:** Students sometimes treat the gallery walk card format as a formality and write vague feedback ("nice work," "interesting approach") to avoid seeming critical. This defeats the purpose of the exercise. Vague positive feedback gives the receiving team nothing to act on. The most useful feedback you can give is a concrete risk or a genuine question, something the team can investigate and either fix or explicitly disclose. Kindness and specificity are not opposites.

---

*You have collected feedback cards from every station. Triage is the step where raw feedback becomes a concrete action plan: which feedback demands a fix, which demands a disclosure, and which can safely wait.*

## 3. Triage (20 minutes)

Teams cluster their feedback cards and sort every item into exactly one bucket: **Fix before demo** (breaks the core story), **Disclose at demo** (real, acknowledged, out of scope), or **Future work** (report material). The discipline is the second bucket: mature engineering names its known defects rather than hoping nobody notices. The Scribe converts bucket one into assigned, dated backlog items on the spot.

### Triage Exercise

For each piece of feedback your team received, the Coordinator calls it out, the team reaches consensus on the bucket, and the Scribe records:
- The feedback (verbatim)
- The bucket (Fix / Disclose / Future)
- If Fix: who owns it and when it will be done
- If Disclose: the exact wording of the disclosure (one sentence, honest and specific)

[[___ Your triage table here ___]]

*Hint:* The hardest items to triage are the ones where the team disagrees about whether something is "core" or "peripheral." The test: if this failure happens during the demo and you have not disclosed it, does it undermine the audience's understanding of what the system does? If yes, it is Disclose at minimum, Fix if there is time.

---

*With your backlog triaged and your disclosures drafted, the final step is a formal readiness check. The Evaluator's sign-off is only valid if each "Yes" comes with evidence (a time, a link, a run result), not just confidence.*

## 4. Release Readiness Checklist

Before demo day, every team verifies and the Evaluator signs off on each item. "Yes" requires evidence (a number, a transcript, a test run), not just belief.

| Item | Check | Evidence Required |
|------|-------|-------------------|
| 1. The end-to-end happy path runs from a fresh start in under 3 minutes | Yes / No | Time it, with a teammate watching the clock |
| 2. The evaluation table (harness, metrics, monolith baseline comparison) is current and in the repository | Yes / No | Link to the file in the repository; confirm the date on the most recent run |
| 3. The governance document's sections 3 through 7 match what the system actually does today | Yes / No | Read sections 3-7 aloud and check each claim against the current system |
| 4. One failure case is rehearsed and its disclosure is worded | Yes / No | The Scribe can read the disclosure wording from the triage table |
| 5. Every teammate can deliver the 90-second explainability story solo | Yes / No | Each teammate delivers it once to the rest of the team before leaving today |
| 6. Reproducibility: seeds fixed, model versions pinned and listed, setup steps tested by the teammate who did not write them | Yes / No | The teammate who did not write the README has successfully set up the system from scratch |

The Evaluator signs off only when all six items are Yes with evidence. Partial checklists are not done.

[[___ Evaluator sign-off and notes here ___]]

---

## Exercises

**Exercise 1.** Write your team's stand-up answers in complete sentences (not bullet fragments) as if you were delivering them to the class. Then compare the written version to what you actually said out loud. Which version is clearer? What does the gap tell you about how well your team communicates technical status?

*What to do:* Each team member writes their answer to all four stand-up questions individually. Then compare answers as a team. Where do your answers disagree about the riskiest item or the metric? Disagreements are informative.

*Starter hint:* A well-formed stand-up answer for question 3 ("what did your evaluation harness report?") looks like: "Our harness evaluated 50 test queries. Tool-call accuracy was 74%. Citation accuracy was 61%. Both are lower than our target of 80%." Not: "The results were okay, around 70% or so."

*You've succeeded when:* All four questions have written answers with specific numbers or named artifacts; no adjectives substituting for measurements.

[[___ Your stand-up answers here ___]]

**Exercise 2.** Write the one-sentence disclosure for each item in your "Disclose at demo" bucket. The sentence must be honest, specific, and kind; it should prepare the audience for the limitation without apologizing for the entire system.

*What to do:* For each Disclose item from the triage, draft one sentence in this form: "This system [does X well] but [does not handle Y because Z], and we plan to [address it / leave it as future work]."

*Starter hint:* A good disclosure: "The system accurately retrieves answers from documents up to 50 pages but does not yet handle documents with tables or figures, which we identified as out of scope for this semester." A bad disclosure: "Sometimes it doesn't work very well with some files."

*You've succeeded when:* Each disclosure names the specific limitation, explains why it exists, and gives the audience enough context to adjust their evaluation accordingly.

[[___ Your disclosure sentences here ___]]

**Exercise 3.** Rehearse the 90-second explainability story. Each teammate delivers it to the rest of the team. The team rates each delivery on three criteria: Does it name what the system does? Does it explain why the system's answer can be trusted (or what its limits are)? Does it avoid jargon that a non-CS audience would not understand?

*What to do:* Set a timer for 90 seconds. Each teammate delivers the story individually. After each delivery, the Reflector gives one piece of specific feedback on the three criteria.

*Starter hint:* A well-structured 90-second story: (1) What does the system do, in one sentence? (2) Here is a concrete example: [show it]. (3) Here is how you can tell whether its answer is reliable: [show the explainability affordance]. (4) Here is one thing it does not do well: [state the disclosure].

*You've succeeded when:* Every teammate can deliver all four components in 90 seconds or less, and the team agrees that the disclosure and the trust affordance both come across clearly.

[[___ Your team's delivery notes here ___]]

---

## Reflection Prompt

**Personal level:** Compare the feedback you received today with the feedback your own critique agents give in your system. Which was more actionable, human peer feedback or automated evaluation? What does that comparison teach you about what human judgment adds that automated metrics cannot capture?

> *Hint:* Think about the kinds of feedback a gallery walker might give that your automated evaluation harness cannot: "I didn't understand what I was supposed to do with this interface" or "the failure case you showed made me trust the system more, not less." What category of signal is that, and can it be quantified? How would you even design an automated test for it?

**Technical level:** The release-readiness checklist asks you to test your own setup steps using the teammate who did not write them. Why is this the right person to run the test? What category of errors does this catch that the author of the steps cannot catch?

**Societal level:** The gallery walk requires showing a known failure case at every station. In commercial AI deployments, failure cases are rarely demonstrated publicly. What are the incentives that lead companies to hide failure modes, and what would it take (regulation, liability, cultural norms) to make candid failure disclosure the default rather than the exception?

> *Hint:* Consider the analogy to drug side-effect disclosures, which are now legally required on packaging and in ads. Before that regulation, pharmaceutical companies also had strong incentives to minimize discussion of side effects. What changed? Was it a high-profile failure, regulatory action, litigation, or cultural pressure? Which of those vectors seems most plausible for AI, and which actor (government, courts, journalists, or the public) would most likely trigger it?

Write a combined reflection of 150-200 words addressing at least two of the three levels. The Reflector should be prepared to share the team's most surprising piece of gallery feedback with the class.

[[___ Your reflection here ___]]

---

-> Coming Up Next: Demo Day. Work through the [Demo Day Guide](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/FinalProject#demo-day-external-guests-and-technical-interview-practice) with your team; it turns today's triaged backlog and release-readiness checklist into your final presentation plan.

---

## 5. Further Reading

- Your project specification's presentation rubric, reread tonight.
- Amershi et al. "Guidelines for Human-AI Interaction." *CHI* (2019), for last-mile demo polish.
