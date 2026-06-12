# Project Studio and Gallery Walk
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

Today the classroom becomes a studio: structured work time, a formal **gallery walk** peer review, and a release-readiness checklist that converts feedback into your final sprint's backlog. The arc: **stand-up $\rightarrow$ gallery walk $\rightarrow$ triage $\rightarrow$ release checklist**.

---

## Directions and Group Roles

Project roles (rotated by sprint) are in effect today: **Coordinator**, **Builder(s)**, **Evaluator**, **Scribe**. The Scribe maintains today's living document: stand-up notes, every piece of gallery feedback verbatim, and the triaged backlog you leave with.

---

## 1. Stand-Up (10 minutes)

Each team answers, in two minutes at the board, exactly four questions: What works end-to-end today? What is the riskiest unfinished piece? What did your evaluation harness report this week (a number, not an adjective)? What do you need from the instructor or another team? Stand-ups are status synchronization, not performance; the discipline is *saying the number*.

---

## 2. Gallery Walk Protocol (40 minutes)

Stations: each team's system runs live with its one-page architecture diagram and its current evaluation table beside it. Half of each team hosts; half walks (swap at the midpoint).

Walkers leave structured feedback on cards, one card per station, with exactly three fields:

- **Strength**: one specific thing that works, named precisely ("the citation pane made the RAG answer checkable in one glance").
- **Question**: one genuine question the demo raised, ideally about a seam, a failure mode, or governance ("what happens when retrieval returns nothing?").
- **Risk**: the one thing most likely to fail on demo day, stated kindly and concretely.

Hosts demonstrate honestly: at least one *known failure case* must be shown at every station. A demo that hides its failure modes is rehearsing a deception, and your governance documents say otherwise.

### Critical Thinking Questions

1. As a walker: across all stations, which *pattern* from Unit 3 appeared most often, and where did you see one misapplied (a planner where a pipeline would do)?
2. As a host: which visitor question exposed something your team had not considered? The Scribe records it verbatim; it likely belongs in your report's limitations section.
3. Which team's explainability affordance (trace, citation, confidence display) would you steal, and how would it fit your system?

---

## 3. Triage (20 minutes)

Teams cluster their feedback cards and sort every item into exactly one bucket: **Fix before demo** (breaks the core story), **Disclose at demo** (real, acknowledged, out of scope), or **Future work** (report material). The discipline is the second bucket: mature engineering names its known defects. The Scribe converts bucket one into assigned, dated backlog items on the spot.

---

## 4. Release Readiness Checklist

Before demo day, every team verifies and the Evaluator signs off:

1. The end-to-end happy path runs from a fresh start in under 3 minutes.
2. The evaluation table (your harness, your metrics, monolith baseline comparison) is current and in the repository.
3. The governance document's sections 3 through 7 match what the system actually does today.
4. One failure case is rehearsed and its disclosure worded.
5. Every teammate can deliver the 90-second explainability story solo.
6. Reproducibility: seeds fixed, model versions pinned and listed, setup steps written down and tested by the teammate who did not write them.

---

## Reflection Prompt

In your notebook: compare the feedback you received today with the feedback your own critique agents give in your system. Which was more actionable, and what does the comparison teach you about the rubrics you wrote for your machines?

---

## 5. Further Reading

- Your project specification's presentation rubric, reread tonight.
- Amershi et al. "Guidelines for Human-AI Interaction." *CHI* (2019), for last-mile demo polish.
