# Governance and Policy Writing
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-governance.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-governance.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Governance and Policy Writing

You have built agents that retrieve, decide, judge, and act; **governance** is the discipline of deciding, in advance and in writing, what they may do, who is accountable when they err, and how anyone would know. Today you learn to *write* policy, a genre with teeth, because your final project requires a governance document and your careers will require many more. The arc: **what governance is $\rightarrow$ frameworks in the wild $\rightarrow$ the anatomy of an enforceable policy $\rightarrow$ drafting workshop**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today culminates in a drafting workshop with structured peer review; bring your project's pre-mortem and data-flow audit, which become raw material. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: From Values to Mechanisms

## 1. Governance Is Engineering with Words

**A value is not a policy.** "Our agent is fair and transparent" commits no one to anything; a policy converts values into *mechanisms*: scopes, prohibitions, gates, logs, owners, and remedies. The test of a policy clause is operational: could a third party determine, from evidence, whether it was followed? Every clause failing that test is decoration.

**The risk-tiered pattern.** Mature frameworks classify uses by risk and scale obligations accordingly. The **EU AI Act** bans a small set of practices, imposes heavy obligations (documentation, human oversight, accuracy reporting) on "high-risk" systems such as those used in education admissions and grading, and lighter transparency duties elsewhere. The **NIST AI Risk Management Framework** organizes the work as four functions: *Govern* (assign accountability), *Map* (know your system and context), *Measure* (evaluate, disaggregate, monitor), and *Manage* (mitigate, respond, document). Notice how much of NIST's *Measure* you can already execute: harnesses, disaggregated metrics, judge audits, citation checks.

**Accountability has names in it.** Policies designate an owner per system, an escalation path, and an incident process. "The team is responsible" means no one is.

---

## Model 1: Toothless Versus Enforceable

Clause A: "The advising agent should be used responsibly and its suggestions taken with appropriate caution."
Clause B: "The advising agent may draft degree-plan suggestions but may not submit registrations. Every suggestion shown to a student must display the data sources used. The CS department chair owns this system; suspected errors are reported via the form at [link] and acknowledged within 5 business days. Logs of all suggestions are retained for one semester and audited each January against the disaggregation protocol in Appendix B."

### Critical Thinking Questions

1. Apply the third-party test to each sentence of both clauses: which are checkable from evidence?
2. Identify in Clause B the scope, the prohibition, the transparency duty, the owner, the remedy, and the audit. Which single element, if deleted, most weakens the rest?
3. Under the EU AI Act's logic, why would an advising agent that *recommends* differ in risk tier from one that *registers*? Connect to the irreversible-action taxonomy you built in the tool-use module.

---

# Part II: The Anatomy of Your Policy

## 2. The Eight Sections

Your governance document (for the written assignment and your project) uses this skeleton, each section earning its place by the third-party test:

1. **Purpose and scope**: what the system does, for whom, and explicitly what is out of scope.
2. **System description**: agents, models, tools, data flows (your design table and audit, imported).
3. **Permitted and prohibited uses**: concrete, with the prohibition list as specific as the permission list.
4. **Human oversight**: which actions require confirmation, who confirms, and what the human sees.
5. **Data handling**: what is collected, where it lives, retention, and the regulated categories touched (FERPA, IRB).
6. **Evaluation and monitoring**: metrics, disaggregation, audit schedule, and the harness that produces them.
7. **Accountability and incident response**: the owner by name or role, the reporting path, response timelines.
8. **Review and sunset**: when the policy is re-examined and the conditions under which the system is retired.

[[MC]]
A team writes: "Section 6: We will continuously evaluate the system for quality and bias." The revision that survives the third-party test is:
- ( ) "We will evaluate rigorously and transparently."
- ( ) "Evaluation is a core value of our team."
- (x) "Each Friday the harness in /eval runs the 40-item task set; per-group accuracy and judge-human agreement are posted to the repository; any group gap exceeding 5 points opens an incident."
- ( ) "Users are encouraged to report problems."

---

## Model 2: Frameworks Meet Your Project

### Critical Thinking Questions

4. Map your project onto NIST's four functions: for each of Govern, Map, Measure, and Manage, name the artifact you have already produced this semester that does that work, and the one artifact still missing.
5. Would your project be "high-risk" under the EU AI Act's education provisions if deployed for real students rather than a class demo? What single design change most reduces its tier?
6. Your pre-mortem predicted a specification gap, an irreversible action, and a global invariant. Write the policy clause (one sentence each) that addresses each prediction.

---

# Part III: Drafting Workshop

## 3. Exercises

1. *Draft sections 3 and 4.* In class, write your project's permitted/prohibited uses and human-oversight sections in full, enforceable prose. The Recorder types; everyone argues.
2. *Structured peer review.* Exchange drafts with another team. Reviewers apply exactly two tests to every sentence: the third-party test, and the "who, specifically" test. Return the draft with each failing sentence flagged. (This is the gallery-walk protocol applied to prose.)
3. *Red-team the prohibition list.* For the other team's section 3, devise one use that violates the policy's *intent* while complying with its *letter*. The drafting team must then close the gap. Reward hacking, you will notice, is not only for models.
4. *Incident drill.* Write the first three steps your team executes when a user reports your agent gave a harmful answer, with owners and timestamps. If you cannot name the owner, your section 7 is not done.

---

## Reflection Prompt

In your notebook: you have now been a builder, an evaluator, an auditor, and a policy author for the same class of systems. Which role felt most natural, which most uncomfortable, and which do you believe the world is shortest of right now? Defend the last answer in two sentences.

---

## 4. Further Reading

- NIST. *AI Risk Management Framework 1.0* (2023, online), especially the Govern function.
- European Union. *AI Act* (2024), Annex III on high-risk systems, including education uses.
- Your institution's acceptable-use and responsible-AI policies, read now with an author's eye.
