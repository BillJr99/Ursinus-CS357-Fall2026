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

### Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Governance** | The set of written rules, structures, and processes that decide what an AI system may do, who is accountable for its behavior, and how problems are detected and fixed — before harm occurs. | A university's policy stating that an AI advising tool may suggest course plans but may not register students for classes is a governance document. |
| **EU AI Act** | A 2024 European Union law that classifies AI systems by risk level and imposes different obligations depending on how much harm a system could cause, from bans on the most dangerous uses to transparency requirements for lower-risk ones. | An AI system used in college admissions falls in the Act's "high-risk" category and requires detailed documentation, human oversight, and accuracy testing. |
| **NIST AI RMF** | The National Institute of Standards and Technology AI Risk Management Framework, a voluntary US guideline that organizes AI risk work into four functions: Govern, Map, Measure, and Manage. | A team completing a pre-mortem (Map), running disaggregated evaluations (Measure), and assigning a named project owner (Govern) is implementing the NIST framework. |
| **Third-Party Test** | A practical check for whether a policy clause is real: could an independent outside party examine evidence and determine whether the clause was actually followed? If not, the clause is decoration, not policy. | "We will be fair" fails the test. "Every Friday the evaluation harness runs 40 tasks and any group accuracy gap above 5 points opens an incident" passes the test. |
| **Sunset Clause** | A provision in a policy that specifies when the policy must be revisited or when the system must be retired if conditions change, preventing outdated rules from governing a changed system indefinitely. | "This policy expires 12 months after deployment and must be renewed following a new impact assessment" is a sunset clause. |
| **Incident Response** | A documented procedure specifying exactly what steps are taken, by whom, and on what timeline when an AI system produces a harmful or unexpected output. | "Within 24 hours of a user harm report, the project owner disables the tool and opens a tracked issue; within 5 business days a root-cause analysis is posted" is an incident response process. |

---

# Part I: From Values to Mechanisms

In this part, you will learn to distinguish policy language that merely sounds good from policy language that actually commits someone to a specific, checkable action. This is the single most important skill in this activity — everything else builds on it.

## 1. Governance Is Engineering with Words

A value statement like "our system is fair and transparent" sounds meaningful but commits no one to any specific action. Governance converts values into *mechanisms* that can actually be checked and enforced. Think of it the same way you think about writing tests for code: a test that says "the function should work correctly" is useless; a test that says "given input X, output Y is returned within 200ms" is enforceable. The same logic applies to AI governance policy.

**A value is not a policy.** "Our agent is fair and transparent" commits no one to anything; a policy converts values into *mechanisms*: scopes, prohibitions, gates, logs, owners, and remedies. The test of a policy clause is operational: could a third party determine, from evidence, whether it was followed? Every clause failing that test is decoration.

**The risk-tiered pattern.** Mature frameworks classify uses by risk and scale obligations accordingly. The **EU AI Act** (a 2024 European law regulating AI systems by the potential harm they could cause) bans a small set of practices, imposes heavy obligations (documentation, human oversight, accuracy reporting) on "high-risk" systems such as those used in education admissions and grading, and lighter transparency duties elsewhere. The **NIST AI Risk Management Framework** (a voluntary US guideline) organizes the work as four functions: *Govern* (assign accountability), *Map* (know your system and context), *Measure* (evaluate, disaggregate, monitor), and *Manage* (mitigate, respond, document). Notice how much of NIST's *Measure* you can already execute: harnesses, disaggregated metrics, judge audits, citation checks.

**Accountability has names in it.** Policies designate an owner per system, an escalation path, and an incident process. "The team is responsible" means no one is.

---

## Model 1: Toothless Versus Enforceable

Why this matters: when you build a real AI system — even a class project — someone will eventually ask "who is accountable if this produces a harmful output?" Learning to write clauses that survive the third-party test now prepares you to answer that question with documentation rather than apologies.

Clause A: "The advising agent should be used responsibly and its suggestions taken with appropriate caution."

Clause B: "The advising agent may draft degree-plan suggestions but may not submit registrations. Every suggestion shown to a student must display the data sources used. The CS department chair owns this system; suspected errors are reported via the form at [link] and acknowledged within 5 business days. Logs of all suggestions are retained for one semester and audited each January against the disaggregation protocol in Appendix B."

### Critical Thinking Questions

1. Apply the **third-party test** (could an independent outside party examine evidence and determine whether this clause was actually followed, without asking anyone to interpret what it means?) to each sentence of both clauses. Which sentences are checkable from evidence, and which are not?

   *Hint: For each sentence, ask: if I gave this sentence to an outside auditor along with all of the system's logs, could they determine with certainty whether the clause was followed or violated? If the answer requires judgment about what "responsible" means, the clause fails the test.*

2. Identify in Clause B the scope, the prohibition, the transparency duty, the owner, the remedy, and the audit. Which single element, if deleted, most weakens the rest?

   *Hint: Try removing each element one at a time and ask what breaks. If there is no owner, who fixes problems? If there is no audit, how does anyone know if the transparency duty is being met? If there is no remedy, what incentivizes compliance?*

3. Under the EU AI Act's logic, why would an advising agent that *recommends* differ in risk tier from one that *registers*? Connect to the irreversible-action taxonomy you built in the tool-use module.

   *Hint: Think about what a student can do after a bad recommendation versus after a bad registration. Can they undo it? How much does it cost to fix? How quickly must it be fixed to avoid serious harm?*

---

# Part II: The Anatomy of Your Policy

Now that you can distinguish real policy from decoration, this part gives you the structure for your project's governance document. Every section has a specific job; if you can't fill a section, that gap tells you something important about your system design.

## 2. The Eight Sections

A governance document is not a formality — it is an engineering artifact that specifies what your system does, who is accountable for it, and what happens when things go wrong. Every section below earns its place because it answers a question that cannot be answered any other way. If you cannot fill a section, that gap is itself a finding: something about your system is unspecified.

Your governance document (for the written assignment and your project) uses this skeleton, each section earning its place by the third-party test:

1. **Purpose and scope**: what the system does, for whom, and explicitly what is out of scope.
2. **System description**: agents, models, tools, data flows (your design table and audit, imported).
3. **Permitted and prohibited uses**: concrete, with the prohibition list as specific as the permission list.
4. **Human oversight**: which actions require confirmation, who confirms, and what the human sees before deciding.
5. **Data handling**: what is collected, where it lives, how long it is retained, and which regulated categories it touches (FERPA, IRB).
6. **Evaluation and monitoring**: metrics, disaggregation plan, audit schedule, and the harness that produces the data.
7. **Accountability and incident response**: the owner by name or role, the reporting path, and response timelines measured in hours or days.
8. **Review and sunset**: when the policy is re-examined and the conditions under which the system is retired.

[[MC]]
A team writes: "Section 6: We will continuously evaluate the system for quality and bias." The revision that survives the third-party test is:
- ( ) "We will evaluate rigorously and transparently using best-practice methods."
- ( ) "Evaluation is a core value of our team and we take it seriously."
- (x) "Each Friday the harness in /eval runs the 40-item task set; per-group accuracy and judge-human agreement are posted to the repository; any group gap exceeding 5 points opens an incident."
- ( ) "Users are encouraged to report problems and we will respond appropriately."

---

## Model 2: Frameworks Meet Your Project

### Critical Thinking Questions

4. Map your project onto NIST's four functions: for each of Govern, Map, Measure, and Manage, name the artifact you have already produced this semester that does that work, and the one artifact still missing.

   > *Hint:* Govern = who owns this and what are they accountable for? Map = what does the system do and who is affected? Measure = how do you know if it's working or failing? Manage = what do you do when something goes wrong? Match each function to something you have actually built, written, or run this semester — your rubric pipeline, your pre-mortem, your data flow diagram, your test harness all count.

5. Would your project be "high-risk" under the EU AI Act's education provisions if deployed for real students rather than a class demo? What single design change most reduces its tier?

   *Hint: The EU AI Act's Annex III lists education systems that "determine access to, assignment to, or advancement of persons in educational institutions." Does your system make, recommend, or inform any of those decisions? If so, what would you remove or add to change that?*

6. Your pre-mortem predicted a specification gap, an irreversible action, and a global invariant. Write the policy clause (one sentence each) that addresses each prediction.

   *Hint: A specification-gap clause should say what happens when the agent encounters a request it was not designed to handle. An irreversible-action clause should name the action, require human confirmation, and name the confirming party. A global-invariant clause should specify what the system must always do (or never do) regardless of user instruction.*

> **Common Misconception:** "Governance is something we add after the system works." Many teams treat governance documentation as a final step before submission — something to write once the code is done. In practice, writing a governance document *first* surfaces design requirements you would otherwise miss: who is accountable forces you to define ownership; what is prohibited forces you to define scope; how you audit forces you to build the logging infrastructure. Teams that write governance last typically discover they built an unsupervised, unauditable system.

---

# Part III: Drafting Workshop

Now that your policy has a structure and you've mapped your project onto real frameworks, this workshop turns those materials into actual written policy — and then tests it against peer review and adversarial reading.

## 3. Exercises

1. *Draft sections 3 and 4.*

   *What to do:* In class, write your project's permitted/prohibited uses and human-oversight sections in full, enforceable prose. The Recorder types; everyone argues.

   *Starter hint:* For permitted uses, list specific tasks the system was designed for (e.g., "The agent may draft feedback comments on student code submissions"). For prohibited uses, be equally specific (e.g., "The agent may not assign grades, submit grades to the registrar, or send emails to students directly"). For human oversight, name every action that requires a human to see evidence and click confirm before proceeding.

   *You've succeeded when:* An outside auditor could read sections 3 and 4 and determine, from your system's logs, whether any violation occurred — without having to ask you what you meant.

2. *Structured peer review.*

   *What to do:* Exchange drafts with another team. Reviewers apply exactly two tests to every sentence: the third-party test, and the "who, specifically" test. Return the draft with each failing sentence flagged.

   *Starter hint:* Mark every sentence that contains the words "we will," "the team," "regularly," "appropriately," or "as needed" as a likely failure. These words almost always indicate that a specific actor, schedule, or threshold has been omitted.

   *You've succeeded when:* You return a draft with every vague clause flagged and a specific suggested revision for at least three of them — not just criticism but a concrete alternative.

3. *Red-team the prohibition list.*

   *What to do:* For the other team's section 3, devise one use that violates the policy's *intent* while complying with its *letter*. The drafting team must then close the gap.

   *Starter hint:* Look for underspecified actions. If the policy says "the agent may not send emails," ask whether it can schedule emails, draft emails that a human then sends, or forward existing emails. Each of these is a plausible gap. Reward hacking, you will notice, is not only for models.

   *You've succeeded when:* You have identified a genuine gap (a use case that violates intent but passes a literal reading) and the drafting team has written a revised clause that closes it.

4. *Incident drill.*

   *What to do:* Write the first three steps your team executes when a user reports your agent gave a harmful answer, with owners and timestamps.

   *Starter hint:* Step 1 should include who receives the report and within what time window they must acknowledge it. Step 2 should specify what they do immediately (disable the system? preserve logs? notify a supervisor?). Step 3 should specify what analysis is required and when it must be completed. If you cannot name the owner, your section 7 is not done.

   *You've succeeded when:* A new team member who has never seen your project could read your three steps and execute them correctly in a real incident — without asking anyone for clarification.

---

## Reflection Prompt

*Personal:* Which of the four roles (builder, evaluator, auditor, policy author) felt most natural to you during this course? Which felt most uncomfortable?

*Technical:* The governance document you are writing commits you, in writing, to specific evaluation schedules, data handling practices, and incident response times. What would it mean to actually enforce those commitments on yourself and your team after the course ends?

*Societal:* The world is arguably most short of one of these four roles right now. Which is it, and why? Consider who currently writes AI governance policy for large organizations and whether those people have the technical background to make the third-party test meaningful.

---

## → Coming Up Next

In the next activity, you will examine what it means for an AI system to be *explainable* — how a system earns justified trust rather than assumed trust. The governance document you are drafting today will need an explainability section, and the design heuristics from the next session will tell you how to write it.

## Further Reading

- NIST. *AI Risk Management Framework 1.0* (2023, online), especially the Govern function.
- European Union. *AI Act* (2024), Annex III on high-risk systems, including education uses.
- Your institution's acceptable-use and responsible-AI policies, read now with an author's eye.
