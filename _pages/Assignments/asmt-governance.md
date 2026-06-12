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

This written assignment produces the governance document for your final project's agent team: the same document you will defend during your project's in-class governance discussion, and a writing genre (enforceable policy) you will encounter for the rest of your career.

## Instructions

1. Author a governance document for your project system using the eight-section skeleton from class: purpose and scope; system description; permitted and prohibited uses; human oversight; data handling; evaluation and monitoring; accountability and incident response; review and sunset.
2. Import, rather than restate, your existing artifacts: the agent design table (system description), the data-flow audit and local-first memo (data handling), the harness and disaggregation protocol (evaluation), and your pre-mortem (each predicted failure receives a binding clause).
3. Apply the **third-party test** to every sentence before submitting: could an outsider determine, from evidence, whether the clause was followed? Apply the **"who, specifically" test** to every responsibility.
4. Map your system onto the four NIST AI RMF functions, naming the artifact that performs each, and argue your system's plausible EU AI Act risk tier if it were deployed for real users in an educational setting.
5. Exchange documents with another team for the structured peer review and red-team exercise from class. Include the review you received, close the loophole found, and write a one-paragraph revision memo.

## Deliverables

- **The governance document** (approximately four to six pages), in markdown or PDF, committed to your project repository as `GOVERNANCE.md`.
- **The peer review packet**: the structured review you received, your red-team loophole and patch, and your revision memo.

## Submission Instructions

Submit the PDF (or a repository link plus PDF export) along with the peer review packet as a single ZIP or combined PDF.

## Reflection Prompts

- Which clause was hardest to make enforceable, and what does that difficulty reveal about the underlying value?
- Your incident-response section names an owner. If your system harmed a user tomorrow, would you want to be that owner? What would change in your design if the answer is no?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
