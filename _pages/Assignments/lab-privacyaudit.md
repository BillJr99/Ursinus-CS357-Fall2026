---
layout: assignment
permalink: /Assignments/PrivacyAudit
title: "CS357: Foundations of Artificial Intelligence - Lab: Privacy Audit for an AI Agent"

info:
  coursenum: CS357
  points: 100
  goals:
    - To identify and classify PII exposure risks in a deployed agent system
    - To implement PII scrubbing at agent input and output boundaries
    - To design a data retention and logging policy for agent systems
    - To evaluate the tension between privacy and agent utility
  rubric:
    - weight: 25
      description: PII Discovery and Risk Classification
      preemerging: No PII identified in the agent system
      beginning: PII categories listed without risk analysis
      progressing: PII identified at each system boundary with likelihood and impact estimates
      proficient: Comprehensive PII inventory at all system boundaries (input, output, logs, RAG data), each with GDPR/CCPA category, likelihood, impact, and a concrete scenario where it leaks
    - weight: 25
      description: PII Scrubbing Implementation
      preemerging: No scrubbing implemented
      beginning: Regex-based scrubbing for one PII category only
      progressing: NER or LLM-based scrubbing for at least 3 PII categories with accuracy measurement
      proficient: Multi-layer scrubbing (input + output), accuracy table for each category (precision/recall on test sentences), and at least one false positive and one false negative are documented and analyzed
    - weight: 25
      description: Logging and Retention Policy
      preemerging: No logging policy designed
      beginning: A policy exists but does not address retention periods or access control
      progressing: Policy covers what to log, how long to keep it, and who can access it
      proficient: Policy covers all elements plus right-to-erasure procedure, audit trail design, and a threat model for log data (who would attack the logs and why)
    - weight: 25
      description: Utility-Privacy Trade-off Analysis
      preemerging: Trade-off not discussed
      beginning: Trade-off acknowledged generically
      progressing: Two specific agent features are analyzed for how privacy controls degrade their utility
      proficient: At least three features analyzed with quantified utility degradation where possible, a recommendation for which controls to implement and which to skip based on threat model, and a section on informed consent design for the agent
  readings:
    - rtitle: "Privacy-Preserving AI"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-privacypreservingai.md"
    - rtitle: "Intellectual Property and Privacy"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ipprivacy.md"

tags:
  - privacy
  - pii
  - gdpr
  - security

---

## Overview

Every agent system processes sensitive data: user queries that contain names and medical details, RAG indexes that contain internal documents, logs that capture full conversation history. This lab asks you to audit an agent system you have built (the RAG agent, MCP agent, or coding agent from prior labs) for privacy risks, implement mitigations, and write a data governance policy.

## Part 1: PII Inventory (25%)

Map every place in your agent where user or third-party data flows:

- **Input**: What does the user send? Can it contain PII? (Assume yes.)
- **System prompt**: Does it contain any PII (names of users, company data)?
- **RAG index**: What documents did you index? Do they contain PII?
- **Tool call inputs/outputs**: If your agent calls external tools, what data do those calls transmit?
- **Logs**: What does your logging capture? Where is it stored?
- **Model weights / fine-tuning data**: If you fine-tuned, what was in the dataset?

Create a **PII Inventory Table**:

| Location | PII Category (GDPR) | Example | Likelihood of Exposure | Impact if Leaked | GDPR/CCPA Category |
|----------|-------------------|---------|----------------------|-----------------|-------------------|

Include at least 6 rows. Use the GDPR special category taxonomy (health, biometric, financial, etc.) where applicable.

## Part 2: Implement PII Scrubbing (25%)

Implement a PII scrubbing layer for at least the **input** and **output** boundaries of your agent. Choose at least one of:

**Option A: NER-based scrubbing with spaCy**

```python
import spacy
nlp = spacy.load("en_core_web_sm")

def scrub_pii(text: str) -> str:
    doc = nlp(text)
    result = text
    for ent in reversed(doc.ents):
        if ent.label_ in ["PERSON", "ORG", "GPE", "DATE", "PHONE", "EMAIL"]:
            result = result[:ent.start_char] + f"[{ent.label_}]" + result[ent.end_char:]
    return result
```

**Option B: LLM-based scrubbing**

Use a fast local model (or regex + NER combination) with a system prompt: "Replace all PII in the following text with [CATEGORY] placeholders. Return only the scrubbed text."

**Option C: Regex patterns for structured PII**

```python
import re

EMAIL   = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
SSN     = r'\b\d{3}-\d{2}-\d{4}\b'
PHONE   = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
CC      = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
```

**Evaluation**: Test your scrubber on 20 sentences (10 with PII, 10 without). Report precision, recall, and F1. Analyze one false positive and one false negative.

## Part 3: Design a Data Retention Policy (25%)

Write a 1–2 page data retention policy for your agent with these required sections:

**What We Collect**: Enumerate every piece of data the agent stores (query text, responses, session IDs, user identifiers, timestamps, tool call logs, RAG retrieval logs).

**Why We Collect It** (purpose limitation): For each data type, state the specific purpose. If you cannot state a purpose, the data should not be collected.

**Retention Periods**: How long is each data type kept? Provide specific durations and the rationale.

**Access Control**: Who can read agent logs? Under what conditions? (Developers? Security team? No one after N days?)

**Right to Erasure Procedure**: What does a user have to do to get their data deleted? What exactly gets deleted, and what is technically infeasible to delete (e.g., conversation data baked into a fine-tuned model)?

**Log Threat Model**: Who would want to attack your logs, and why? What do they gain from them? At minimum consider: data broker, corporate spy, malicious insider.

## Part 4: Utility-Privacy Trade-off Analysis (25%)

Identify at least **three agent features** that become less useful when privacy controls are applied. For each:

1. Name the feature (e.g., "conversation continuity across sessions," "personalized responses based on user history," "debugging with full query logs")
2. Describe how the privacy control degrades it (e.g., "deleting logs after 24 hours means we cannot reproduce and fix bugs from yesterday")
3. Quantify the degradation if possible (e.g., "without session memory, users must re-explain context on every session, adding ~150 tokens per conversation")
4. State your recommendation: implement the control anyway, skip it, or find a middle ground?

Also write a one-paragraph **informed consent design**: what would you tell users before they use your agent, in plain language, about what data you collect and how to opt out?

## Deliverables

Submit a ZIP containing:

- Annotated agent code with scrubbing layers
- PII Inventory Table (CSV or markdown)
- Scrubbing evaluation table (20 sentences, precision/recall/F1)
- Data Retention Policy document (markdown)
- Utility-Privacy Trade-off Analysis (markdown)
- Reflection answers

## Reflection Prompts

- Your scrubber had false positives (scrubbed text that wasn't PII). How do you weigh the cost of over-scrubbing (losing useful context) against under-scrubbing (leaking PII)?
- GDPR's "right to be forgotten" is technically difficult for AI systems. Write one paragraph explaining the problem to a non-technical regulator, and one paragraph proposing a realistic compliance approach.
- How many hours did this lab take?
