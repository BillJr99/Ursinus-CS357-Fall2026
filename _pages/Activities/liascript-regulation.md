# AI Regulation: EU AI Act, NIST AI RMF, and Sector Rules
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-regulation.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-regulation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# AI Regulation: EU AI Act, NIST AI RMF, and Sector Rules

Building an agent that works is only half the challenge. Deploying it legally and responsibly requires understanding the regulatory landscape that governs where and how AI can be used. This activity covers the three most influential frameworks you will encounter: the **EU AI Act** (the world's first comprehensive AI law), the **NIST AI Risk Management Framework** (the leading voluntary standard in the United States), and **sector-specific rules** in healthcare, finance, education, and law enforcement. By the end of this activity, you will be able to classify an agent system by risk tier, apply the NIST RMF functions to a real project, and identify the compliance obligations your own course agents may carry.

---

## Directions and Group Roles

Work in your POGIL team of four with clearly assigned roles:

- **Manager**: Keeps the group on task and on time; ensures everyone contributes before moving on.
- **Recorder**: Documents the group's answers and posts the final responses to the Class Activity Questions discussion board.
- **Presenter**: Speaks for the group during debrief; articulates areas of genuine disagreement or alternative interpretations.
- **Reflector**: Monitors group process and captures lessons learned for the reflection prompt.

Consider each model and its questions individually before discussing with your group. The goal is to build a shared mental model, not to reach consensus quickly.

---

## Model 1: The EU AI Act Risk Pyramid

The EU AI Act (entered into force August 2024, with phased enforcement through 2027) classifies AI systems into four tiers based on the risk they pose to health, safety, and fundamental rights. Requirements and prohibitions are tied to the tier, not to the technology.

| Tier | Examples | What Is Required or Banned | Do Any Course Agents Fall Here? |
|:-----|:---------|:--------------------------|:-------------------------------|
| **Unacceptable Risk** (banned) | Social scoring by governments; real-time remote biometric identification in public spaces; AI that exploits psychological vulnerabilities; predictive policing based solely on profiling | These systems are **prohibited**. They may not be deployed in the EU under any circumstances. | Almost certainly not — but an agent that builds behavioral profiles of users for coercive purposes would qualify. |
| **High Risk** | AI in medical devices; CV-screening and hiring systems; credit scoring; critical infrastructure management; biometric categorization; AI used in education to evaluate students; autonomous vehicles | **Conformity assessment** before deployment; risk management system; data governance; technical documentation; human oversight measures; accuracy, robustness, and cybersecurity requirements; registration in an EU database | A course agent that automatically grades student work or screens internship applications would likely qualify. |
| **Limited Risk** | General-purpose chatbots; AI-generated content systems; deepfake generators | **Transparency obligations**: users must be informed they are interacting with AI; AI-generated content must be labeled | Most of our course chatbots and RAG agents fall here — you must disclose AI involvement. |
| **Minimal Risk** | Spam filters; AI-powered video games; recommendation engines for streaming | No mandatory requirements beyond general EU law | Course agents used only for internal research and not interacting with real users fall here. |

**GPAI Models** (General Purpose AI, such as large foundation models): The EU AI Act introduces specific obligations for GPAI model providers — transparency, copyright documentation, and safety evaluations for "systemic risk" models (above a compute threshold). This affects providers like Anthropic and Meta, not student developers, but it shapes which APIs you can legally use in commercial products.

### Critical Thinking Questions

1. The EU AI Act bans "AI systems that deploy subliminal techniques beyond a person's consciousness to distort their behavior." A personalized recommendation agent that learns which emotional framing makes a user most likely to click is not explicitly listed as banned. Make the argument both for and against classifying it as Unacceptable Risk.

2. The High Risk tier requires "appropriate human oversight measures." For a course agent that drafts feedback on student assignments, describe what a meaningful human oversight measure would look like in practice. What would make oversight merely formal (checkbox compliance) versus substantive?

3. The Limited Risk tier requires that users be informed they are interacting with AI. If a course agent is deployed as a website chat widget and the welcome message says "Hi, I'm Aria, your academic advisor," what specifically must change to comply with the EU AI Act?

---

## Model 2: NIST AI Risk Management Framework

The NIST AI Risk Management Framework (AI RMF 1.0, released January 2023) is a voluntary framework organized around four core functions. Unlike the EU AI Act, it does not mandate specific outcomes; instead it provides a structured process for identifying and managing AI risk. It is widely adopted in the U.S. federal government and is increasingly referenced in industry contracts.

| Function | What It Means | Key Activities | Example Artifact |
|:---------|:--------------|:--------------|:----------------|
| **Govern** | Establish organizational policies, roles, and culture for AI risk management | Define who is accountable for AI systems; set risk tolerance; establish review processes | AI use policy document; roles and responsibilities matrix |
| **Map** | Identify and categorize the risks posed by a specific AI system in its deployment context | Enumerate stakeholders and harms; classify the system (similar to EU AI Act tiers); document intended and unintended uses | Risk register; use-case inventory; stakeholder impact assessment |
| **Measure** | Quantify and evaluate identified risks using metrics, testing, and ongoing monitoring | Evaluate accuracy, bias, robustness, and explainability; run red-team exercises; track metrics in production | Evaluation report; bias audit results; SLA dashboard |
| **Manage** | Respond to measured risks through controls, mitigations, and contingency plans | Implement technical controls; accept, transfer, or avoid residual risks; maintain incident response plans | Risk treatment plan; incident response runbook; decommission checklist |

The four functions are not a linear sequence — they form a cycle. Measurement findings feed back into Governance decisions; new Governance policies trigger new Mapping exercises.

### Critical Thinking Questions

4. Apply the NIST RMF **Map** function to a course coding agent that can read and execute student-submitted Python files. Identify at least three distinct stakeholder groups and one potential harm for each stakeholder group.

5. The **Measure** function includes evaluating "bias." For a coding agent that gives feedback on student code, what would bias mean in this context, and how would you measure it? Be specific about what data you would collect and what statistical test you would apply.

6. The NIST RMF is voluntary in the U.S. A classmate argues: "If it's voluntary, companies can just ignore it and there are no consequences." Give two reasons why a company might adopt the NIST RMF even without a legal mandate.

---

## Model 3: Sector-Specific Rules

General frameworks like the EU AI Act and NIST RMF establish broad principles, but specific industries have their own regulatory bodies and rules that layer on top of — or conflict with — the general frameworks.

| Sector | Applicable Rules | Key AI-Specific Implications | What Compliance Looks Like in Practice |
|:-------|:----------------|:-----------------------------|:--------------------------------------|
| **Healthcare** | HIPAA (U.S.); FDA Software as a Medical Device (SaMD) guidance; EU MDR for medical devices | AI that processes protected health information (PHI) is subject to HIPAA. AI that functions as a medical device (diagnoses, treats, or prevents disease) requires FDA clearance or approval under SaMD guidance. | Business associate agreements with AI vendors; PHI de-identification before model training; FDA 510(k) clearance for diagnostic AI; post-market surveillance |
| **Finance** | SR 11-7 Model Risk Management (U.S. Federal Reserve); EU AI Act (credit scoring is High Risk) | All models used for credit decisions must be validated by an independent team; model performance must be monitored over time; "black box" models face heightened scrutiny | Model inventory; independent validation report; champion/challenger testing; ongoing performance monitoring; documentation of model limitations |
| **Education** | FERPA (U.S.); state student privacy laws; proposed NIST AI in Education guidance | Student education records (grades, transcripts, disciplinary records) are protected and cannot be shared without consent. AI vendors accessing student data must sign data sharing agreements. | Data processing agreements with AI vendors; consent workflows for minors; audit trails for automated grade-affecting decisions |
| **Law Enforcement** | EU AI Act Unacceptable Risk tier (real-time remote biometric ID in public); ACLU / civil rights litigation risk in U.S. | Real-time facial recognition in public spaces is banned in the EU. Predictive policing systems based solely on AI profiling are banned. In the U.S., there is no federal ban but significant litigation risk. | EU: do not deploy. U.S.: legal review; human override required; disparate impact testing; public disclosure policies |

[[MC]]
A startup builds a chatbot that screens job applications by analyzing resumes and ranking candidates before a human recruiter reviews the shortlist. Under the EU AI Act, this system is most accurately classified as:

- ( ) Minimal risk — it just chats with uploaded documents and a human reviews the results anyway
- ( ) Limited risk — it requires only a transparency notice telling applicants they interacted with AI
- (x) High risk — AI systems used in employment and worker management, including CV-screening and candidate ranking, are explicitly listed in Annex III of the EU AI Act as High Risk, regardless of whether a human reviews the output
- ( ) Unacceptable risk — automated hiring decisions are banned

### Critical Thinking Questions

7. A student team wants to deploy a health information chatbot for their senior capstone project. The chatbot will answer general health questions using a public medical knowledge base and will be tested with real Ursinus students as users. Identify the specific regulatory obligations that apply and describe what the team must do before launching.

8. The finance sector's SR 11-7 guidance requires "independent model validation" — the team that validates a model must be separate from the team that built it. Why might this principle be valuable for AI agents in any sector, not just finance? What would independent validation look like for a student-built advising agent?

9. FERPA protects student education records. If a course agent is given read access to a grade database to answer student questions about their own grades, identify two FERPA obligations the deployment must satisfy and one scenario in which the agent could inadvertently violate FERPA even with good intentions.

---

## Exercises

1. **EU AI Act classification.** For each of the following agent systems from the course, assign an EU AI Act risk tier (Unacceptable / High / Limited / Minimal) and write a one-paragraph justification: (a) the RAG agent that answers questions about course readings, (b) the coding agent that reviews student code and gives feedback, (c) a hypothetical agent that recommends mental health resources based on student chat patterns, (d) an agent that schedules campus events based on historical attendance data, (e) an agent that predicts which students are at risk of dropping a course.

2. **NIST RMF risk register.** Using the four NIST RMF functions as column headers (Govern / Map / Measure / Manage), sketch a one-page risk register for the course RAG agent. For each function, list one specific risk, one activity to address it, and one artifact that would document your response.

3. **GDPR enforcement research.** Find one real enforcement action taken by a European data protection authority (DPA) under GDPR that involved AI, automated decision-making, or algorithmic profiling. Write a one-paragraph summary of: what the company did, which GDPR article was violated, what the fine or remedy was, and what lesson it has for developers building agents today.

---

## Reflection Prompt

In your notebook: if you publish an open-source agent on GitHub and someone else later deploys it in a high-risk context you never intended — say, screening job applications at a Fortune 500 company — who bears legal and moral responsibility for compliance failures? Consider the roles of: the original developer, the company deploying it, the vendor providing the underlying LLM, and the regulatory framework that governs the deployment context.

---

## Further Reading

- EU AI Act full text (Regulation 2024/1689): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689
- NIST AI RMF 1.0: https://airc.nist.gov/RMF
- FDA AI/ML-Based Software as a Medical Device: https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-software-medical-device
- Federal Reserve SR 11-7 Model Risk Management Guidance: https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm
- Future of Privacy Forum. "Student Privacy and AI." https://fpf.org/
