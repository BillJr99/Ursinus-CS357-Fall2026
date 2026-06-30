---
layout: project
permalink: /Projects/RequestTriage
title: "CS357: Foundations of Artificial Intelligence - Project: Request Intake and Triage Agent"

info:
  coursenum: CS357
  points: 100
  goals:
    - To build an intake-and-triage system that ingests unstructured requests, classifies them, detects missing information, and routes them to the right destination using LangChain and/or Microsoft Power Automate
    - To design the system so an agent handles the reversible first pass while a human gate guards the consequential routing decision
    - To evaluate triage quality against a fixed labeled request set with defined metrics and a baseline, and to document failure modes with transcripts
    - To produce a governance document that names what the system does, what it must never do, how personal data is handled, and where the human gate sits
  rubric:
    - weight: 25
      description: Problem Framing and Design
      preemerging: The workflow is vague, or the system is a single prompt with no triage structure; no target workflow or users are named
      beginning: A target intake workflow and its users are named, but the triage stages (classify, detect gaps, route) are not clearly separated and the tool choice (LangChain vs Power Automate) is unjustified
      progressing: The proposal names a concrete intake workflow, defines the request categories and routing destinations, separates the classify / gap-detect / route stages, and justifies the LangChain and/or Power Automate choice; the human-gate placement is stated
      proficient: The proposal names a concrete intake workflow with realistic example requests, defines a complete category taxonomy with routing destinations and required-field lists per category, cleanly separates classify / gap-detect / route stages with schema-shaped outputs, justifies the code-first vs low-code choice (or the hybrid split) against the workflow's real constraints, and places a human gate on the consequential step with a stated confidence/priority trigger
    - weight: 25
      description: Implementation Quality
      preemerging: The system does not run from a fresh start; core triage does not function
      beginning: The system runs but produces free-text rather than structured output, has hard-coded values, or implements only classification with no gap detection or routing
      progressing: The system ingests requests, classifies them, detects at least one class of missing information, and produces a structured (schema-validated) routing decision; configuration is externalized; errors are handled with located messages
      proficient: The system runs reliably from documented setup; it ingests requests from a defined channel, classifies them, detects missing required fields per category, and emits a schema-validated routing decision consumed by deterministic plumbing (ticket/row/notification); all configuration is externalized with no hard-coded values; the human gate is implemented (low-confidence or high-priority requests are flagged for review rather than silently actioned); model versions and seeds are pinned
    - weight: 20
      description: Evaluation and Analysis
      preemerging: No systematic evaluation is provided
      beginning: Informal trials are described without a labeled set, metric, or baseline
      progressing: A fixed labeled request set with defined metrics (e.g., classification accuracy, gap-detection recall) is evaluated against a simple baseline, with numeric results and some failure analysis
      proficient: A fixed labeled request set (finalized early) is evaluated against a stated baseline (e.g., keyword routing) with a protocol a stranger could reproduce; metrics are numeric and disaggregated by category where applicable; gap-detection is measured with recall (the costly miss) explicitly reported; at least three failure modes are documented with transcripts, and at least one mitigation is implemented and re-measured with before/after numbers
    - weight: 15
      description: Governance, Privacy, and the Human Gate
      preemerging: No governance document; personal data handling and the human gate are unaddressed
      beginning: A governance statement exists but is generic and does not address the personal data in real requests or specify the human gate
      progressing: GOVERNANCE.md names what the system does and must never do, identifies the human gate, and addresses data handling at a high level
      proficient: GOVERNANCE.md names scope, explicit prohibitions with reasons, the responsible person, and known limitations; it addresses how requests containing personal data are stored, logged, and retained (including what is kept out of traces, echoing the observability privacy rule); the human gate is documented with its trigger condition and what the reviewer sees at the moment of decision; the deployed behavior matches the document
    - weight: 15
      description: Presentation and Report
      preemerging: The presentation or report is missing
      beginning: The presentation shows only the happy path; the report restates code without design rationale or evaluation
      progressing: The presentation demonstrates the system including one failure case; the report covers design, evaluation results, and limitations
      proficient: The presentation demonstrates the live system including a rehearsed failure disclosure and the human gate in action, shows the evaluation table with the baseline side by side, and has every team member speaking; the report covers design rationale tied to named course patterns, evaluation with baseline and failure transcripts, the governance summary, and (for pairs) individual contribution statements
  readings:
    - rtitle: "Workflow Automation for Intake and Triage Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-workflowautomation.md"
    - rtitle: "Human-in-the-Loop Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-humanintheloop.md"
    - rtitle: "Agent Frameworks Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentframeworks.md"

tags:
  - project
  - agents
  - workflow-automation
  - governance

---

## Project Overview

This project track tackles a problem nearly every organization has: a steady flood of unstructured requests — emails, form submissions, channel messages — that someone has to read, understand, classify, check for missing details, and route to whoever can act. You will build a **request intake and triage agent** that does the reversible first pass (classify, detect gaps, recommend a route) while a **human gate** guards the consequential decision (actually assigning the work). You may build it code-first with **LangChain**, low-code with **Microsoft Power Automate**, or as a hybrid where Power Automate handles the plumbing and a LangChain/hosted model handles the judgment.

This is an **individual or pair project**; pairs must document individual contributions. Use a **synthetic or fully anonymized** request set — do not use real submissions that contain other people's personal information. Any version that ingests real requests or sends outbound messages on someone's behalf requires instructor approval and a governance statement addressing those specific risks.

## Suggested Scope

A minimum viable system: ingest a folder or feed of example requests; classify each into a defined taxonomy; detect at least one class of missing required information per category; emit a schema-validated routing decision; and flag low-confidence or high-priority requests for human review instead of auto-actioning them. Stretch goals: a real connector (Outlook/Teams/Forms/SharePoint or an email inbox), a feedback loop that learns from reviewer corrections, an observability trace (LangSmith) of each triage decision, or a gap-detection step that auto-drafts the "we need more info" reply for a human to approve.

> This project pairs naturally with the course's safety and explainability material: a triage agent is exactly where "recommend and route, with a human gate on the consequential step" earns its keep. Keep the agent on the reversible work; keep a person on the decision that affects someone.
