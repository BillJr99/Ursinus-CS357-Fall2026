---
layout: assignment
permalink: /Assignments/Governance
title: "CS357: Foundations of Artificial Intelligence - Written Assignment: Governance and Policy"

info:
  coursenum: CS357
  points: 100
  goals:
    - To author a complete, enforceable governance document for an agentic system of your own design
    - To convert values into mechanisms with scopes, prohibitions, gates, logs, owners, and remedies
    - To situate a system within external frameworks including the NIST AI Risk Management Framework and the EU AI Act risk tiers
    - To withstand and incorporate adversarial peer review
  rubric:
    - weight: 35
      description: Enforceability and Mechanism Design
      preemerging: The document states values without mechanisms
      beginning: Some sections contain mechanisms, but most clauses fail the third party test
      progressing: Most clauses are checkable from evidence, with named owners and concrete gates, with some decorative language remaining
      proficient: Substantially every clause passes the third party test, with specific scopes, prohibitions, human oversight gates tied to the irreversible action taxonomy, logging, named ownership, timelines, and remedies
    - weight: 25
      description: Framework Integration
      preemerging: External frameworks are not referenced
      beginning: Frameworks are name checked without substantive mapping
      progressing: The system is mapped onto the NIST functions or an EU AI Act risk tier with reasonable justification
      proficient: The system is mapped onto all four NIST functions with named artifacts for each, its plausible EU AI Act tier is argued with reference to the education provisions, and the document identifies which obligation would bind first if deployed beyond the classroom
    - weight: 25
      description: Completeness and Technical Grounding
      preemerging: Multiple required sections are missing
      beginning: All eight sections are present but several are generic rather than specific to the system
      progressing: All eight sections are present and specific, importing the design table, data flow audit, and evaluation harness with minor gaps
      proficient: All eight sections are present, specific, and technically grounded, the data handling section addresses regulated categories accurately, the evaluation section names the actual harness, metrics, disaggregation, and schedule, and the pre mortem predictions each receive a binding clause
    - weight: 15
      description: Peer Review Response and Submission
      preemerging: An incomplete submission is provided
      beginning: The document is submitted without evidence of peer review or revision
      progressing: Peer review feedback is included and at least one identified loophole is closed
      proficient: The structured peer review is included verbatim, every flagged sentence is addressed, the red team loophole is documented and closed, and a one paragraph revision memo summarizes what changed and why
  readings:
    - rtitle: "Governance Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-governance.md"
    - rtitle: "NIST AI Risk Management Framework"
      rlink: "https://www.nist.gov/itl/ai-risk-management-framework"
    - rtitle: "EU AI Act, Annex III"
      rlink: "https://artificialintelligenceact.eu/"

tags:
  - governance
  - ethics
  - written

---

In this assignment you will author a governance document for your final project's agent team — the same document you will defend during your in-class governance discussion. Governance writing is a professional genre you will encounter for the rest of your career: every organization deploying AI is expected to have one, regulators increasingly require it, and a vague or aspirational governance document is worse than useless because it creates false confidence. By the end of this assignment you will know the difference between a value and a mechanism, and you will have written a document that could be handed to an auditor rather than framed on a wall. The two tests you will apply throughout — the third-party test and the "who specifically" test — are the same ones real compliance teams use.

---

## What a Strong Submission Looks Like

A strong governance document has these qualities:

- **Every clause passes the third-party test.** An outsider who has never seen your system can read a clause and determine, from available evidence, whether it was followed. A strong clause: "The system logs every agent invocation to `logs/agent_audit.jsonl` with a timestamp, agent name, input hash, and output hash. Logs are retained for 90 days and reviewed weekly by the designated Evaluator role." A weak clause: "The system will be monitored to ensure responsible use."
- **Every responsibility has a named owner with a timeline.** A strong clause: "If a user reports a harmful output, the Scribe role notifies the Coordinator within 24 hours; the Coordinator investigates within 72 hours and either patches the system or escalates to the instructor." A weak clause: "The team will address any issues that arise."
- **The framework mapping is substantive, not decorative.** A strong NIST mapping names the specific artifact (a file, a log, a test, a human review step) that performs each function. A weak mapping says "we GOVERN by having good norms" without naming anything concrete.
- **The peer review resulted in a real change.** The revision memo names the specific loophole that was found, quotes the original clause, quotes the patched clause, and explains why the patch closes the loophole.

---

## The Two Tests

Apply these tests to every sentence before submitting:

**The Third-Party Test:** Could an outsider determine, from evidence (logs, artifacts, outputs), whether this clause was followed? If the answer is "only if they asked us," the clause fails.

**The "Who Specifically" Test:** Does every assignment of responsibility name a specific role (Coordinator, Evaluator, Scribe) rather than "the team" or "we"? Diffuse responsibility means no one is responsible.

---

## Instructions

### Step 1: Author the Governance Document

Write a governance document of approximately four to six pages covering the eight required sections below. For each section, the description tells you what it must contain. Import, rather than restate, your existing artifacts from earlier assignments: the agent design table from the Design Before You Build assignment, the data-flow diagram, the pre-mortem table, and the evaluation plan.

#### Section 1: Purpose and Scope
State what this document governs, who it applies to, and what it does not cover. Identify the system by name and describe its deployment context in one paragraph.

**Must include:** The specific system, its intended use cases (enumerated), and at least two explicit out-of-scope uses that someone might mistakenly assume are permitted.

#### Section 2: System Description
Summarize the agent architecture. Import your agent design table here by reference or by inclusion. Identify the topology (pipeline, router, blackboard, planner, or hybrid) and state which agent holds which capability.

**Must include:** A reference to your design table (or the table itself), the topology type with a one-sentence rationale, and the model versions and temperature settings for each agent.

#### Section 3: Permitted and Prohibited Uses
List specific permitted uses and specific prohibited uses. Each prohibited use must include the reason it is prohibited and the mechanism that enforces the prohibition.

**Must include:** At least three permitted uses (with their conditions) and at least three prohibited uses (with mechanisms, not just labels). Example mechanism: "Prohibited: processing transcripts containing protected health information. Enforcement: the system checks the first 500 characters of any uploaded document against a regex pattern for HIPAA-regulated terms; if a match is found, the system refuses to process the document and displays a message directing the user to an appropriate tool."

#### Section 4: Human Oversight
Identify every action in the system that is consequential or irreversible, and name the human gate that must occur before that action is taken.

**Must include:** The irreversible action taxonomy from class applied to your system (at minimum: what does the system do that cannot be undone, and what must a human confirm before it proceeds?). Name the role responsible for the confirmation and describe what information the human sees at the moment of decision.

#### Section 5: Data Handling
Describe what data the system collects, stores, or transmits. Address regulated categories explicitly: does the system ever process health, financial, biometric, or minors' data? State retention periods, access controls, and deletion procedures.

**Must include:** A data inventory (even if brief), explicit statements about each regulated category (either "this system does not process X" or "this system processes X under the following controls"), and a deletion procedure with a timeline.

#### Section 6: Evaluation and Monitoring
Name the evaluation harness, the metrics it tracks, the disaggregation protocol (which subgroups, if any, are analyzed separately), and the schedule for re-evaluation after deployment.

**Must include:** The actual metrics from your evaluation plan (not "we will evaluate performance"), the frequency of re-evaluation, and the threshold at which a metric failure triggers review.

#### Section 7: Accountability and Incident Response
Define what constitutes an incident. Name the role responsible for detecting, reporting, and responding to each type of incident. State the response timeline for each severity level.

**Must include:** At least two severity levels with distinct response timelines, a named role for each step of the response procedure, and a binding clause for each failure mode predicted in your pre-mortem.

#### Section 8: Review and Sunset
State when and how this document will be reviewed, who reviews it, and under what conditions the system will be sunset (taken out of service).

**Must include:** A review schedule (e.g., "reviewed at the end of each sprint and at the end of the project"), conditions that trigger an immediate review (e.g., a new model version, a reported incident), and the condition under which the system is shut down.

---

### Step 2: Map Your System to External Frameworks

#### NIST AI Risk Management Framework

Map your system onto all four NIST AI RMF functions. For each function, name the specific artifact or activity in your project that performs it:

| NIST Function | What It Requires | Your System's Artifact or Activity |
|---|---|---|
| **GOVERN** | Policies, culture, and accountability structures | |
| **MAP** | Context, risk identification, affected populations | |
| **MEASURE** | Metrics, testing, and trustworthiness assessment | |
| **MANAGE** | Controls, incident response, residual risk | |

#### EU AI Act Risk Classification

Argue your system's plausible risk tier if it were deployed for real users in an educational setting. The tiers are: unacceptable risk (banned), high risk (Annex III), limited risk (transparency obligations), and minimal risk. Your argument must:
- Name the tier you believe applies
- Cite the specific Annex III category, if applicable, and explain why it does or does not apply
- Name the obligation that would bind first if the system were deployed beyond the classroom

---

### Step 3: Peer Review and Red Team

Exchange your governance document with another team. That team will:
1. Apply the third-party test to every sentence and flag any that fail (use inline comments or a separate list)
2. Find one loophole — a way to use the system in a harmful or unintended way that is not explicitly prohibited or gated

You will receive the same treatment. Include the following in your submission:
- The peer review you received, verbatim (as an appendix or inline comments)
- A description of the loophole they found, quoted from their review
- Your patch: the revised clause that closes the loophole, with the original clause shown for comparison
- A one-paragraph revision memo summarizing what changed and why

---

## Document Skeleton

Use the following as your structural skeleton. You may add subsections, but do not omit any numbered section:

```
# Governance Document: [System Name]
Version 1.0 | Date: [date] | Authors: [team members and roles]

## 1. Purpose and Scope
## 2. System Description
## 3. Permitted and Prohibited Uses
## 4. Human Oversight
## 5. Data Handling
## 6. Evaluation and Monitoring
## 7. Accountability and Incident Response
## 8. Review and Sunset

## Appendix A: NIST AI RMF Mapping
## Appendix B: EU AI Act Classification Argument
## Appendix C: Peer Review (verbatim)
## Appendix D: Revision Memo
```

---

## Frequently Asked Questions

**Q: My system is very simple — a two-agent pipeline for summarizing course readings. Does it really need a full governance document?**
A: Yes, and the simplicity makes it easier, not harder. Governance is not proportional to complexity; it is proportional to consequence. A summarizer that a student uses instead of reading the actual text has real consequences. Your governance document will be shorter and simpler than a high-risk system's, but it still needs all eight sections.

**Q: What is a "loophole" in the context of the peer review?**
A: A loophole is a use or behavior that is harmful or unintended but not explicitly prohibited or gated by your document. For example: a system that prohibits "processing medical records" but does not explicitly prohibit "processing a diary entry that describes health conditions" has a loophole. A system that requires human approval for sending emails but does not require approval for drafting them has a loophole (the draft could be sent by accident).

**Q: How do I handle the EU AI Act if my system is clearly minimal risk?**
A: Argue the minimal risk classification explicitly. Name the Annex III categories and explain why your system does not fall into any of them. Do not simply state "our system is low risk." A minimal-risk argument that engages with the specific Annex III language is more credible than one that does not.

**Q: My pre-mortem from the Design Before You Build assignment had six risks. Do all six need to appear in Section 7 as binding clauses?**
A: Yes. The rubric requires that "the pre-mortem predictions each receive a binding clause." If a risk does not have a corresponding governance clause, either add the clause or explain in your revision memo why the risk is accepted rather than mitigated.

**Q: Can I commit the governance document to the project repo instead of submitting it as a separate PDF?**
A: Yes — the instructions require it to be committed as `GOVERNANCE.md`. Submit the repository link plus a PDF export as your formal submission.

---

## Deliverables

- **The governance document** (approximately four to six pages), in markdown or PDF, committed to your project repository as `GOVERNANCE.md`
- **The peer review packet**: the structured review you received (verbatim), your red-team loophole patch, and your revision memo

Submit the PDF (or a repository link plus PDF export) along with the peer review packet as a single ZIP or combined PDF.

---

## Part 0 (Warm-Up, Ungraded): Policy Clause Workshop

Before writing your full governance document, this warm-up develops your policy writing muscle with a focused 30-minute exercise.

**The Hospital Sepsis AI Scenario**

Read this abbreviated incident report:

> A regional hospital deployed an AI clinical decision support tool to flag patients at high risk for sepsis. It was validated at 87% accuracy on a 2019 pilot. In production, nurses began treating the AI's "low risk" flag as authoritative, skipping their own assessments. Eighteen months later, an internal audit found the tool performed at 62% accuracy for patients over 75 and for non-English-speaking patients. Two sentinel events (serious patient harm) occurred.

**Your Task (30 minutes):**

1. **Identify two NIST AI RMF gaps** in the hospital's approach. Map each to one of the four NIST functions (Map, Measure, Manage, Govern) and write one sentence explaining what that function would have caught.

2. **Write one policy clause** (≤100 words) that would have prevented the primary failure. Your clause must specify:
   - **Scope**: who and what it applies to
   - **Requirement**: what must happen (be specific)
   - **Enforcement**: what happens if it is violated
   - **Exception**: one valid exception to prevent over-application

   **Example format** (for a different domain — write your own):
   > *"Automated resume-screening tools shall flag all candidates rejected by the AI for human review before any rejection letter is sent. Reviews shall be logged with the reviewer's name and reasoning. Violations by hiring managers shall be escalated to the Chief People Officer within 48 hours. Exception: internal transfer applications are exempt from this requirement."*

3. **Stress-test your clause**: identify one way it could be gamed (met in letter but not spirit) and write a one-sentence amendment to close the gap.

This warm-up is not graded but must be completed and submitted with your main assignment; your instructor will provide brief written feedback before your full governance document is due.

---

## Reflection Prompts

- Which clause was hardest to make enforceable, and what does that difficulty reveal about the underlying value?
- Your incident-response section names an owner. If your system harmed a user tomorrow, would you want to be that owner? What would change in your design if the answer is no?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
