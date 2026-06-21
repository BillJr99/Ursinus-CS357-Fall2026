---
layout: assignment
permalink: /Assignments/Regulation
title: "CS357: Foundations of Artificial Intelligence - Assignment: Mapping a Real AI System to the Regulatory Landscape"

info:
  coursenum: CS357
  points: 100
  goals:
    - To classify a real AI system under the EU AI Act risk pyramid with justification
    - To apply the NIST AI Risk Management Framework's four functions to a real deployment
    - To identify sector-specific regulatory requirements relevant to an AI system
    - To write a structured AI risk register with technical and social risks
  rubric:
    - weight: 25
      description: System Selection & Classification
      preemerging: No system identified or misclassified with no justification
      beginning: System described but EU AI Act classification is unsupported
      progressing: Classification is correct with partial Annex III reference
      proficient: Classification is precise with direct Annex III or GPAI citation and three specific compliance obligations identified
    - weight: 25
      description: NIST AI RMF Mapping
      preemerging: NIST AI RMF not applied
      beginning: Two of four functions addressed superficially
      progressing: All four functions addressed with one gap and one mitigation each
      proficient: All four functions mapped to concrete artifacts or practices, gaps are evidence-based, mitigations are specific and actionable
    - weight: 25
      description: Sector-Specific Rules
      preemerging: No sector rules identified
      beginning: One rule mentioned without analysis
      progressing: One sector covered with two specific requirements
      proficient: At least two applicable regulatory touchpoints identified with specific provisions, and the interaction between EU AI Act and sector rules is explained
    - weight: 25
      description: Risk Register
      preemerging: No risk register
      beginning: A list of risks with no structure
      progressing: Structured register with likelihood/impact but regulatory touchpoints missing
      proficient: 5-row register with all columns complete, one technical risk, one fairness risk, one legal risk, and mitigations that are implementable rather than generic
  readings:
    - rtitle: "AI Regulation Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-regulation.md"
    - rtitle: "Ethical Frameworks Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ethicalframeworks.md"

tags:
  - regulation
  - governance
  - ethics
  - eu-ai-act
  - nist

---

## Overview
This assignment asks you to take the regulatory frameworks from class and apply them to a real, deployed AI system. The goal is not to find a "bad" system to criticize, but to practice the rigorous thinking a compliance officer, auditor, or governance lead must perform.

## Part 1: Select and Describe a System (10%)
Choose one real AI system currently deployed. Examples (pick one, or propose your own):
- GitHub Copilot (developer tool)
- Google Health AI / Med-PaLM (medical decision support)
- Workday Skills Cloud (HR / employment screening)
- COMPAS (criminal risk assessment, used in US courts)
- ChatGPT Enterprise (knowledge work)
- An AI hiring screener (HireVue, Pymetrics, etc.)

Write **two paragraphs**: (a) what the system does and who the end users are; (b) what data it processes and what decisions it influences or makes. Cite at least one primary source (company documentation, research paper, or investigative reporting).

## Part 2: EU AI Act Classification (30%)
Classify the system using the EU AI Act risk pyramid:

| Tier | Definition | Your System? |
|------|-----------|-------------|
| Unacceptable Risk | Banned outright | --- |
| High Risk | Requires conformity assessment, human oversight, transparency | ? |
| Limited Risk | Requires transparency notice to users | ? |
| Minimal Risk | No mandatory requirements | ? |

Justify your classification with:
1. Direct reference to the Act's **Annex III** categories (for High Risk) or the **General Purpose AI** provisions (for foundation models)
2. An explanation if the system spans multiple tiers
3. **Three specific compliance obligations** that would apply under the Act (e.g., "Article 13 transparency: users must be informed they are interacting with an AI system")

If your system is a General Purpose AI model, address the GPAI Tier obligations separately.

## Part 3: NIST AI RMF Mapping (30%)
The NIST AI Risk Management Framework defines four functions. Complete the following table:

| Function | What It Means | What the Developer Likely Does | One Gap You Can Infer | One Artifact That Would Fill the Gap |
|----------|--------------|-------------------------------|----------------------|-------------------------------------|
| Govern | Policies, accountability structures | | | |
| Map | Identify context, stakeholders, risks | | | |
| Measure | Define, collect, and interpret risk metrics | | | |
| Manage | Prioritize and act on risks | | | |

Base your "likely does" column on publicly available information (documentation, model cards, press releases, lawsuits, or academic papers). If you cannot find evidence, say so explicitly rather than guessing.

## Part 4: Risk Register (30%)
Write a structured AI risk register with exactly 5 rows:

| Risk ID | Risk Description | Likelihood (H/M/L) | Impact (H/M/L) | Regulatory Touchpoint | Proposed Mitigation |
|---------|-----------------|-------------------|----------------|----------------------|---------------------|
| R-01 | | | | | |
| R-02 | | | | | |
| R-03 | | | | | |
| R-04 | | | | | |
| R-05 | | | | | |

**Requirements:**
- At least one risk must be **technical** (e.g., model accuracy failure, adversarial attack)
- At least one must be **social/fairness-related** (e.g., disparate impact on a protected group)
- At least one must be **legal/compliance** (e.g., GDPR right to explanation, sector rule violation)
- Mitigations must be specific (not "monitor the system" --- say *what* to monitor, *how*, and *by whom*)

## Reflection Prompts

- The EU AI Act was written primarily for systems used in the EU. If your system is deployed globally, which jurisdiction's rules govern it, and how do conflicts between legal systems get resolved?
- The NIST AI RMF is voluntary in the US. What market incentives might cause a company to adopt it anyway? What might cause them to ignore it?
- If collaboration beyond your own occurred, identify it. Do you certify this represents your original work? Please identify any portions not originally written by you.
- Approximately how many hours did this assignment take?
