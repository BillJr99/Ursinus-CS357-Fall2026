---
layout: assignment
permalink: /Assignments/Regulation
title: "CS357: Foundations of Artificial Intelligence - Assignment: Mapping a Real AI System to the Regulatory Landscape"

info:
  coursenum: CS357
  purpose: "To practice the rigorous thinking a compliance officer or auditor performs, by mapping a real, deployed AI system onto the regulatory frameworks that increasingly govern it."
  tilt:
    task: "Select a real deployed AI system and classify it under the EU AI Act, map it onto the NIST AI RMF's four functions, identify the sector-specific rules it triggers, and build a structured risk register."
    criteria: "Assessed in four equal parts — the accuracy of your EU AI Act classification, your NIST AI RMF mapping, the sector-specific rules you identify, and a complete risk register with implementable mitigations; see the rubric below for the full breakdown."
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

---

## How to Approach This Assignment

- **Think like an auditor, not a critic.** Your job is not to argue that a system is good or bad — it is to map it accurately onto existing frameworks. Stay close to publicly available evidence.
- **Read the Annex III categories before you pick your system.** Many students choose a system, write two paragraphs about it, and then discover it does not fit neatly anywhere. Skimming Annex III first will save you time and produce a better choice.
- **Concrete beats vague everywhere in this assignment.** "The system may cause bias" earns progressing. "The system may produce disparate rejection rates for candidates from non-English-speaking backgrounds, violating Article 10's data governance requirements" earns proficient.
- **Unknown information is data, not a gap.** If a company does not publish its model card, that absence tells you something about its Govern function. Say so explicitly.

> **Common Pitfall: Classifying a system as "minimal risk" without actually checking the Annex III categories.** Many systems that look benign — a resume screener, a credit-scoring tool, a medical symptom checker — are explicitly listed in Annex III as high-risk. Before you assign a tier, work through the Annex III checklist item by item. If your system does not appear there AND is not a GPAI model, then minimal risk may be correct. But you must show that you checked.

**Recommended time budget:**
- Part 1 (System Selection): 30 minutes
- Part 2 (EU AI Act Classification): 60 minutes
- Part 3 (NIST RMF Mapping): 75 minutes
- Part 4 (Risk Register): 60 minutes
- Reflection + polish: 15 minutes

**What proficient work looks like:** A student working at the proficient level picks a system with interesting regulatory ambiguity (not an obvious high-risk or obvious minimal-risk case), cites specific articles and annex numbers rather than paraphrasing the framework in general terms, and writes mitigations specific enough that an engineer could actually implement them.

---

> **Glossary — key terms used in this assignment:**
> - **EU AI Act**: The European Union's binding regulation on AI systems, in force from 2024. It creates a risk pyramid (unacceptable → high → limited → minimal) and imposes compliance obligations based on risk tier.
> - **Annex III**: The list of high-risk AI application categories in the EU AI Act. Includes systems used in biometric identification, critical infrastructure, education, employment, essential services (credit, insurance), law enforcement, migration, and administration of justice.
> - **GPAI (General Purpose AI)**: AI models — typically large foundation models — that can serve many tasks. The EU AI Act has a separate obligation tier for GPAI providers, including transparency and copyright compliance requirements. Models with systemic risk (above a compute threshold) face additional obligations.
> - **NIST AI RMF**: The National Institute of Standards and Technology AI Risk Management Framework. Voluntary in the US. Organizes AI risk management into four functions: Govern, Map, Measure, and Manage.

---

## Part 1: Select and Describe a System (10%)

**What this part is testing:** Whether you can identify a system with enough regulatory complexity to make the later parts substantive, and whether you can describe it precisely at the level of what decisions it influences.

> **Getting Started Hint:** A good system choice has at least one of the following: it makes or significantly influences decisions about employment, credit, education, healthcare, or justice (those are Annex III categories); it is deployed in the EU or by a company with EU operations; or it uses a foundation model that might qualify as GPAI. A bad choice is a system so generic that every answer is "unknown" or so obviously high-risk that classification requires no analysis. Systems like COMPAS (criminal risk) and HireVue (hiring) are rich choices. Systems like "a chatbot on a retail website" are harder to write 400 words about.

Choose one real AI system currently deployed. Examples (pick one, or propose your own):
- GitHub Copilot (developer tool)
- Google Health AI / Med-PaLM (medical decision support)
- Workday Skills Cloud (HR / employment screening)
- COMPAS (criminal risk assessment, used in US courts)
- ChatGPT Enterprise (knowledge work)
- An AI hiring screener (HireVue, Pymetrics, etc.)

Write **two paragraphs**: (a) what the system does and who the end users are; (b) what data it processes and what decisions it influences or makes. Cite at least one primary source (company documentation, research paper, or investigative reporting).

> **Scope check:** Your response to this part should be approximately 200–250 words across the two paragraphs, plus one citation.

---

## Part 2: EU AI Act Classification (30%)

**What this part is testing:** Whether you can apply a legal framework precisely — not just name the tier but cite the specific provision that places your system there.

Classify the system using the EU AI Act risk pyramid:

| Tier | Definition | Your System? |
|------|-----------|-------------|
| Unacceptable Risk | Banned outright | --- |
| High Risk | Requires conformity assessment, human oversight, transparency | ? |
| Limited Risk | Requires transparency notice to users | ? |
| Minimal Risk | No mandatory requirements | ? |

**EXAMPLE table (for an email spam filter — replace with your own system):**

| Tier | Definition | Email Spam Filter |
|------|-----------|------------------|
| Unacceptable Risk | Banned outright | No — does not perform real-time biometric surveillance or social scoring |
| High Risk | Requires conformity assessment, human oversight, transparency | No — spam filtering does not appear in Annex III categories |
| Limited Risk | Requires transparency notice to users | Arguably yes — users may not know an AI is classifying their email |
| Minimal Risk | No mandatory requirements | Most likely — no Annex III match, no GPAI designation |

*EXAMPLE ROW — replace with your own system's analysis.*

Justify your classification with:
1. Direct reference to the Act's **Annex III** categories (for High Risk) or the **General Purpose AI** provisions (for foundation models)
2. An explanation if the system spans multiple tiers
3. **Three specific compliance obligations** that would apply under the Act (e.g., "Article 13 transparency: users must be informed they are interacting with an AI system")

If your system is a General Purpose AI model, address the GPAI Tier obligations separately.

> **Getting Started Hint:** Search the EU AI Act text for your system's domain keyword (e.g., "employment," "credit," "biometric"). If you find a match in Annex III, the system is high-risk and you must work through the specific article that defines its obligations. If you do not find a match and the system is not a large foundation model, work through the limited vs. minimal distinction by asking: "Is a human interacting with this system in a way that might cause them to think they are interacting with another human, or is the AI making a recommendation the user might not know is AI-generated?"

> **Scope check:** Your response to this part should be approximately 350–450 words, including the completed table and the three compliance obligations with article citations.

---

## Part 3: NIST AI RMF Mapping (30%)

**What this part is testing:** Whether you can connect an abstract framework to concrete organizational practices and identify evidence-based gaps — not just name the four functions but populate them with specifics from your chosen system.

The NIST AI Risk Management Framework defines four functions. Complete the following table:

| Function | What It Means | What the Developer Likely Does | One Gap You Can Infer | One Artifact That Would Fill the Gap |
|----------|--------------|-------------------------------|----------------------|-------------------------------------|
| Govern | Policies, accountability structures | | | |
| Map | Identify context, stakeholders, risks | | | |
| Measure | Define, collect, and interpret risk metrics | | | |
| Manage | Prioritize and act on risks | | | |

**EXAMPLE table row (for a hypothetical "AI-powered customer service chatbot" — replace with your own system):**

| Function | What It Means | What the Developer Likely Does | One Gap You Can Infer | One Artifact That Would Fill the Gap |
|----------|--------------|-------------------------------|----------------------|-------------------------------------|
| Govern | Policies, accountability structures | Has a published responsible AI policy; designates a Chief AI Officer | The policy does not specify who is accountable when the chatbot gives incorrect legal or medical information | An accountability matrix (RACI chart) naming the team responsible for flagging and reviewing high-stakes chatbot outputs |

*EXAMPLE ROW — replace with your own system's analysis across all four functions.*

Base your "likely does" column on publicly available information (documentation, model cards, press releases, lawsuits, or academic papers). If you cannot find evidence, say so explicitly rather than guessing.

> **Getting Started Hint:** Start by searching "[system name] model card," "[system name] responsible AI," and "[system name] audit" or "[system name] lawsuit." Lawsuits and investigative journalism articles are often more informative than company press releases for identifying gaps. If you find nothing for a function, write "No public evidence found" in the "likely does" column — that itself is a finding worth analyzing.

> **Scope check:** Your response to this part should fill all four rows of the table with substantive entries (not single words). Plan for 3–5 sentences per row across the last three columns, approximately 400–500 words total.

---

## Part 4: Risk Register (30%)

**What this part is testing:** Whether you can write structured, actionable risk documentation at a level a real engineering team could use — not a list of vague concerns but a register with calibrated likelihood, impact, and implementable mitigations.

Write a structured AI risk register with exactly 5 rows:

| Risk ID | Risk Description | Likelihood (H/M/L) | Impact (H/M/L) | Regulatory Touchpoint | Proposed Mitigation |
|---------|-----------------|-------------------|----------------|----------------------|---------------------|
| R-01 | | | | | |
| R-02 | | | | | |
| R-03 | | | | | |
| R-04 | | | | | |
| R-05 | | | | | |

**EXAMPLE rows (for a hypothetical AI hiring screener — replace with your own system):**

| Risk ID | Risk Description | Likelihood (H/M/L) | Impact (H/M/L) | Regulatory Touchpoint | Proposed Mitigation |
|---------|-----------------|-------------------|----------------|----------------------|---------------------|
| R-01 | Model trained on historical hiring data produces lower scores for candidates from HBCUs, creating disparate impact on Black applicants | H | H | EU AI Act Art. 10 (data governance); US EEOC adverse impact doctrine | Conduct annual adverse impact analysis by race and school type; require human review for any candidate within 5 points of the score threshold |
| R-02 | Third-party video analysis component (facial expression scoring) is discontinued, breaking the pipeline | M | H | EU AI Act Art. 9 (risk management system for high-risk AI) | Maintain a fallback pipeline using only resume text scoring; include SLA in vendor contract requiring 90-day deprecation notice |

*EXAMPLE ROWS — replace with your own system's risks.*

**Requirements:**
- At least one risk must be **technical** (e.g., model accuracy failure, adversarial attack)
- At least one must be **social/fairness-related** (e.g., disparate impact on a protected group)
- At least one must be **legal/compliance** (e.g., GDPR right to explanation, sector rule violation)
- Mitigations must be specific (not "monitor the system" — say *what* to monitor, *how*, and *by whom*)

> **Getting Started Hint:** For each row, ask yourself three questions in order: (1) What could go wrong? (2) Who is harmed and how seriously? (3) What existing law or standard already speaks to this failure mode? If you cannot answer question 3, that itself is a regulatory gap worth noting in your risk register.

> **Scope check:** Your response to this part is the completed 5-row table. Every cell must contain substantive text — single words like "bias" or "high" without context will not earn proficient credit.

---

## Common Mistakes

- **Writing "TBD" or "unknown" for every NIST gap without explaining what the unknown tells you.** The absence of a public model card or audit report is itself evidence about the Govern function — say so.
- **Classifying a system as minimal risk without checking Annex III.** Many systems that seem innocuous (hiring tools, loan scorers, student assessment software) are explicitly named in Annex III as high-risk. Work through the list before you assign a tier.
- **Confusing the EU AI Act with GDPR.** These are two separate regulations. The EU AI Act governs AI system design and deployment; GDPR governs data processing and privacy. Your system may be subject to both, and they have different obligations.
- **Writing mitigations that are not implementable.** "Ensure fairness" is not a mitigation. "Run a quarterly disparate impact analysis broken down by gender and race, reviewed by the ethics board, with a remediation protocol triggered if the 4/5ths rule is violated" is a mitigation.
- **Describing only the intended use case when classifying risk.** The EU AI Act classifies systems by their potential to cause harm in the worst plausible use, not just the best-case intended use. Consider how a bad actor — or a well-meaning but careless deployer — could use your system.

---

## Reflection Prompts

- The EU AI Act was written primarily for systems used in the EU. If your system is deployed globally, which jurisdiction's rules govern it, and how do conflicts between legal systems get resolved? (2–3 sentences. This matters because many US-headquartered companies are now restructuring their global AI compliance programs to meet EU standards by default.)
- The NIST AI RMF is voluntary in the US. What market incentives might cause a company to adopt it anyway? What might cause them to ignore it? (1 paragraph. Think about enterprise procurement requirements, liability exposure, and industry reputation — not just altruism.)
- If collaboration beyond your own occurred, identify it. Do you certify this represents your original work? Please identify any portions not originally written by you.
- Approximately how many hours did this assignment take?
