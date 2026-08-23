<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-regulation.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-regulation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# AI Regulation: EU AI Act, NIST AI RMF, and Sector Rules

Building an agent that works is only half the challenge.  Deploying it legally and responsibly requires understanding the regulatory landscape that governs where and how AI can be used.  This activity covers the three most influential frameworks you will encounter: the **EU AI Act** (the world's first comprehensive AI law), the **NIST AI Risk Management Framework** (the leading voluntary standard in the United States), and **sector-specific rules** in healthcare, finance, education, and law enforcement.  By the end of this activity, you will be able to classify an agent system by risk tier, apply the NIST RMF functions to a real project, and identify the compliance obligations your own course agents may carry.

---

## Directions and Group Roles

Work in your POGIL team of four with clearly assigned roles:

- **Manager**: Keeps the group on task and on time; ensures everyone contributes before moving on.
- **Recorder**: Documents the group's answers and posts the final responses to the Class Activity Questions discussion board.
- **Presenter**: Speaks for the group during debrief; articulates where the group disagreed or read things differently.
- **Reflector**: Monitors group process and captures lessons learned for the reflection prompt.

Take each model and its questions individually first, then bring them to your group.  You are after a shared mental model here, so please don't rush to consensus.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|:-----|:------------------------|:------------------------|
| **EU AI Act** | The world's first comprehensive law specifically governing AI systems, passed by the European Union in 2024. It classifies AI by risk level and assigns mandatory requirements or outright bans depending on the tier. | A student project that automatically grades assignments might fall under the High Risk tier because it makes consequential decisions about students' academic records. |
| **Risk Tier** | The EU AI Act's four-level classification system that determines what rules apply to a given AI system, from Minimal Risk (no requirements) to Unacceptable Risk (banned outright). The tier is based on potential harm, not the underlying technology. | A spam filter is Minimal Risk. A CV-screening tool for hiring is High Risk. A government social scoring system is Unacceptable Risk and is banned. |
| **NIST AI RMF** | The National Institute of Standards and Technology AI Risk Management Framework, a voluntary structured process used widely in U.S. federal agencies and industry to identify, measure, and respond to AI risks. It does not mandate specific outcomes; it provides a structured process. | A team using NIST RMF would create a risk register (Map), run bias audits (Measure), and write an incident response plan (Manage) before deploying a student-facing agent. |
| **HIPAA** | The Health Insurance Portability and Accountability Act, a U.S. federal law that protects the privacy of individually identifiable health information (called Protected Health Information, or PHI). | An agent that reads patient intake forms or suggests diagnoses must comply with HIPAA and cannot send that data to an external LLM API without a signed Business Associate Agreement. |
| **FERPA** | The Family Educational Rights and Privacy Act, a U.S. federal law that protects student education records (grades, transcripts, disciplinary records) and restricts who can access them without student consent. | A course agent given read access to a grade database must be configured so it only returns a student's own grades, never another student's records. |
| **Conformity Assessment** | The EU AI Act's required process for High Risk AI systems before they can be deployed, similar to a building permit for a skyscraper. The developer must document the system, assess its risks, and either self-certify or have a third party audit it. | A company deploying an AI hiring tool in the EU must complete conformity assessment, register the system in the EU database, and implement human oversight before any job applicant is ever evaluated. |

---

## Model 1: The EU AI Act Risk Pyramid

> **Why this matters:** The EU AI Act is like a building code for AI systems: you do not build a skyscraper however you like, and you do not deploy AI however you like either.  The law assigns different requirements based on how much harm a system could cause.  Even if you are a student in Pennsylvania, the EU AI Act affects you: any agent you deploy that could be accessed by EU residents, or any commercial product you build in the future, must comply.  Understanding the tier structure now lets you design with compliance in mind from the start.

The EU AI Act (entered into force August 2024, with phased enforcement through 2027) classifies AI systems into four tiers based on the risk they pose to health, safety, and fundamental rights.  Requirements and prohibitions are tied to the tier, not to the technology.

| Tier | Real-World Examples | What the Law Requires or Bans | Do Any Course Agents Fall Here? |
|:-----|:--------------------|:------------------------------|:-------------------------------|
| **Unacceptable Risk** (banned outright) | A city government using AI to score citizens' "social trustworthiness" and restrict their access to services based on the score; a retailer using real-time facial recognition cameras to scan shoppers in a public mall; a chatbot that uses hidden emotional manipulation to pressure elderly users into purchases | These systems are **completely prohibited** in the EU. No conformity assessment, no exception, no matter how the operator argues the benefits outweigh the harms. | Almost certainly not in this course, but an agent that builds behavioral profiles of users for coercive purposes, or that monitors and rates students' social behavior to affect their standing, would qualify. |
| **High Risk** | An AI system that screens resumes and ranks job applicants before a human recruiter reviews them; software that scores loan applications and creditworthiness; a tool that recommends which students should be flagged for additional academic support; an AI used in a medical device to detect tumors in X-rays | Before deployment: complete a conformity assessment; implement a risk management system; maintain technical documentation; register the system in the EU database; implement meaningful human oversight; ensure accuracy and robustness testing; document data governance practices | A course agent that automatically grades student work, or one that predicts which students are at risk of failing, would likely fall here; these make consequential decisions about individuals. |
| **Limited Risk** | A general-purpose chatbot like ChatGPT or a customer service bot; an AI that generates marketing copy or synthetic images; a deepfake video generator | Transparency obligations only: users must be clearly told they are talking with an AI; AI-generated content must be labeled as such; the system need not justify its decisions, but it must not pretend to be human | Most of the course chatbots and RAG agents fall here; you must disclose AI involvement in every deployment, including the welcome message. |
| **Minimal Risk** | A spam filter that flags unwanted email; an AI opponent in a video game; a Netflix recommendation algorithm suggesting what to watch next | No mandatory requirements beyond ordinary EU consumer and product law; deploy and iterate freely | Course agents used only internally for research, never shown to real users outside the course, generally fall here. |

**GPAI Models** (General Purpose AI, such as large foundation models): The EU AI Act introduces specific obligations for GPAI model providers: transparency, copyright documentation, and safety evaluations for "systemic risk" models (above a compute threshold).  This affects providers like Anthropic and Meta, not student developers, but it shapes which APIs you can legally use in commercial products.

### Critical Thinking Questions

1.  The EU AI Act bans "AI systems that deploy subliminal techniques beyond a person's consciousness to distort their behavior in a way that causes or is likely to cause harm."  A personalized recommendation agent that learns which emotional framing makes a user most likely to click on content is not explicitly listed as banned.  Make the argument both for and against classifying it as Unacceptable Risk, drawing on the language of the definition above.

   *Hint:* The key phrase is "subliminal": below conscious awareness.  If the recommendation logic is disclosed to users, does that change whether it qualifies?  What if the emotional framing exploits fear or social comparison in ways users would not endorse if they understood the mechanism?

2.  The High Risk tier requires "appropriate human oversight measures."  For a course agent that drafts written feedback on student assignments, describe what a meaningful human oversight measure would look like in practice.  Then describe what would make oversight merely formal (a checkbox the instructor clicks without reading) versus substantive (oversight that could actually catch and correct errors).

   *Hint:* Think about the difference between an instructor who reviews the AI feedback before a student sees it versus an instructor who clicks "approve" on a hundred pieces of feedback in five minutes because they trust the system.  What design choices would make substantive review easier?

3.  The Limited Risk tier requires that users be clearly informed they are interacting with an AI. A course agent is deployed as a chat widget on the college website with the welcome message "Hi, I'm Aria, your academic advisor; how can I help you today?"  Identify every specific element of this deployment that would need to change to comply with the EU AI Act, and explain what the compliant version would say.

   *Hint:* The name "Aria" sounds human.  The phrase "your academic advisor" implies a professional relationship.  The welcome message contains no AI disclosure.  The law requires disclosure to be clear and prominent, not buried in terms of service.  What would a compliant version of this welcome message look like?

---

## Model 2: NIST AI Risk Management Framework

> **Why this matters:** If the EU AI Act is the law, NIST AI RMF is the instruction manual for being a responsible AI developer everywhere else.  In the U.S. federal government and in most large companies, NIST RMF compliance is either required by contract or expected as a sign of professional maturity.  Learning to apply its four functions now means you will already speak the language that employers use when they say "we need to manage AI risk."

The NIST AI Risk Management Framework (AI RMF 1.0, released January 2023) is a voluntary framework organized around four core functions.  Unlike the EU AI Act, it does not mandate specific outcomes; instead it provides a structured process for identifying and managing AI risk.  It is widely adopted in the U.S. federal government and is increasingly referenced in industry contracts.

| Function | What It Means in Plain English | Key Activities | Example Artifact You Would Produce |
|:---------|:-------------------------------|:--------------|:-----------------------------------|
| **Govern** | Establish organizational policies, roles, and culture for AI risk management: decide in advance who is accountable and what your risk tolerance is before problems arise | Define who is accountable for each AI system and what happens if it causes harm; set the organization's risk tolerance level; establish review processes; create training requirements for staff who deploy AI | A written AI use policy document for your team; a roles and responsibilities matrix that names who approves new agent deployments |
| **Map** | For a specific AI system in its specific deployment context, identify and categorize all the ways it could cause harm, before it is deployed | Enumerate every stakeholder group affected by the system, including groups who never interact with it directly; list potential harms for each stakeholder; classify the system using a risk framework (similar to EU AI Act tiers); document all intended uses and foreseeable unintended uses | A risk register listing harms, likelihoods, and severities; a stakeholder impact assessment; a use-case inventory |
| **Measure** | Quantify and evaluate the identified risks using data, testing, and ongoing monitoring; do not just describe risks, measure them | Evaluate accuracy and error rates; audit for demographic bias; test robustness against adversarial inputs; run red-team exercises; track performance metrics in production over time | An evaluation report with disaggregated results by subgroup; bias audit results with statistical significance; an SLA dashboard showing live metrics |
| **Manage** | Respond to measured risks through controls, mitigations, and contingency plans; close the loop between measurement and action | Implement technical controls (input filters, output validators, rate limits); formally accept, transfer, or avoid residual risks you cannot eliminate; maintain an incident response plan for when something goes wrong; plan for decommissioning | A risk treatment plan documenting each mitigation; an incident response runbook; a decommission checklist for when the agent is retired |

The four functions are not a linear sequence; they form a cycle.  Measurement findings feed back into Governance decisions; new Governance policies trigger new Mapping exercises.

> **Common Misconception:** Many students assume "voluntary framework" means "optional in practice."  In reality, the NIST AI RMF is increasingly referenced in U.S. federal procurement contracts, state laws, and corporate vendor requirements.  A startup that ignores NIST RMF may find itself ineligible to sell to government agencies or large enterprises, even without any direct legal mandate.

### Critical Thinking Questions

4.  Apply the NIST RMF **Map** function to a course coding agent that can read and execute student-submitted Python files.  Identify at least three distinct stakeholder groups (including at least one group that does not directly interact with the agent), and for each stakeholder group identify one specific potential harm they could experience.

   *Hint:* Obvious stakeholders are students and instructors.  Who else might be affected?  Think about other students whose code might be compared or shared, the institution's IT infrastructure if the agent can execute arbitrary code, or the course graders who must act on the agent's feedback.

5.  The **Measure** function includes evaluating "bias."  For a coding agent that gives feedback on student code, what would bias mean in this specific context; what would it look like if the agent were biased?  Then describe how you would measure it: what data would you need to collect, what statistical comparison would you run, and what threshold would indicate a problem worth addressing?

   *Hint:* Bias in a code review agent might mean it gives harsher feedback to code that uses variable names in certain languages, or that it rates code quality differently based on stylistic choices that correlate with student background.  To measure it, you would need outcome data disaggregated by some student attribute, but which attribute, and how would you get that data ethically?

6.  The NIST RMF is voluntary in the U.S. A classmate argues: "If it's voluntary, companies can just ignore it and there are no consequences."  Give two concrete, specific reasons why a company building AI products might adopt the NIST RMF even without a legal mandate to do so.

   *Hint:* Think about what happens when something goes wrong.  Who decides whether the company acted responsibly?  Also think about who the company's customers are and what those customers require in their vendor contracts.

---

## Model 3: Sector-Specific Rules

> **Why this matters:** Knowing the EU AI Act and NIST RMF is necessary but not sufficient.  Each industry sector has its own regulatory body and its own rules that layer on top of the general frameworks.  A healthcare AI application must comply with the EU AI Act *and* HIPAA *and* FDA device regulations simultaneously.  Understanding sector rules now will prevent you from deploying an agent into a regulated industry and discovering (after launch) that you needed a federal clearance.

General frameworks like the EU AI Act and NIST RMF establish broad principles, but specific industries have their own regulatory bodies and rules that layer on top of (or sometimes conflict with) the general frameworks.

| Sector | Applicable Rules | Key AI-Specific Implication | What Compliance Looks Like in Practice |
|:-------|:----------------|:----------------------------|:--------------------------------------|
| **Healthcare** | HIPAA (U.S.); FDA Software as a Medical Device (SaMD) guidance; EU Medical Device Regulation (MDR) | Any AI system that processes individually identifiable health information is subject to HIPAA, even if it just reads a patient's name and diagnosis to answer a scheduling question. Any AI that diagnoses, treats, or prevents disease functions as a medical device and requires FDA clearance or approval before patients can use it. | Before launch: sign Business Associate Agreements (BAA, a contract required under HIPAA that obligates a vendor to protect any health data they access on your behalf) with every AI vendor; de-identify or obtain consent for any PHI used in training; obtain FDA 510(k) clearance for diagnostic functions; implement post-market surveillance to monitor the AI's clinical performance over time |
| **Finance** | Federal Reserve SR 11-7 Model Risk Management guidance; EU AI Act (credit scoring is explicitly High Risk) | Every model used to make or support credit decisions must be validated by an independent team, not the team that built it. Black-box models face heightened scrutiny and must provide explainable reasoning for adverse decisions so applicants can contest them. | Build and maintain a model inventory; conduct independent validation by a separate team; run champion/challenger testing where the new model competes against the old one on live traffic; document all model limitations explicitly in the model card |
| **Education** | FERPA (U.S.); state student privacy laws (e.g., California SOPIPA); proposed NIST AI in Education guidance | Student education records (grades, transcripts, disciplinary actions, course enrollment) are protected and cannot be accessed or shared without student consent. Any AI vendor that accesses student data must sign a data sharing agreement and is limited in how it can use that data. | Sign data processing agreements with all AI vendors before granting data access; implement consent workflows for students who are minors; maintain audit trails for any automated decision that could affect a grade or academic standing |
| **Law Enforcement** | EU AI Act Unacceptable Risk tier (real-time remote biometric ID in public spaces); ACLU litigation risk in U.S.; state-level bans in some U.S. cities | Real-time facial recognition in public spaces (like scanning a crowd at a train station to identify wanted persons) is banned in the EU. Predictive policing systems that rely solely on AI profiling (without individualized suspicion) are also banned in the EU. The U.S. has no federal ban but faces significant civil rights litigation risk. | In the EU: do not deploy these systems, period. In the U.S.: require legal review before any deployment; mandate a human decision-maker who can override any AI flag; conduct disparate impact testing disaggregated by race; publish public disclosure policies describing how the system is used |

A startup builds a chatbot that screens job applications by analyzing resumes and ranking candidates before a human recruiter reviews the shortlist.  Under the EU AI Act, this system is most accurately classified as:

[( )] Minimal risk; because a human reviews the shortlist, the AI is only a tool assisting a human decision, which removes it from higher risk tiers
[( )] Limited risk; the system only needs a transparency disclosure telling applicants an AI was involved, since the recruiter makes the final decision
[(X)] High risk; AI systems used in employment and worker management, including CV-screening and candidate ranking, are explicitly listed in Annex III of the EU AI Act as High Risk, regardless of whether a human reviews the output
[( )] Unacceptable risk; any automated screening that affects employment decisions without individual consent is banned under the manipulation provisions

### Critical Thinking Questions

7.  A student team wants to deploy a health information chatbot for their senior capstone project.  The chatbot will answer general health questions using a public medical knowledge base and will be tested with real Ursinus students as users.  Identify the specific regulatory obligations that apply to this deployment, and describe the concrete steps the team must complete before any student user accesses the chatbot.

   *Hint:* Does the chatbot process Protected Health Information?  Even general health questions from identifiable students could constitute PHI if the responses are tied to a specific person's health inquiry.  Does the chatbot "diagnose" anything, or does it only provide general information?  Where is the line between health information and medical advice, and why does that line matter for FDA regulation?

8.  The finance sector's SR 11-7 guidance requires "independent model validation": the team that validates a model must be organizationally separate from the team that built it.  Explain why this principle might be valuable for AI agents in any sector, not just finance.  Then describe what independent validation would look like for a student-built academic advising agent at Ursinus.

   *Hint:* Why might the team that built a system be poorly positioned to find its flaws?  Think about cognitive bias, incentives, and what "independent" actually requires: does it mean a different student, a different class, or a different institution?

9.  FERPA protects student education records.  If a course agent is given read access to a grade database to answer student questions about their own grades, identify two specific FERPA obligations the deployment must satisfy.  Then describe one concrete scenario in which the agent could inadvertently violate FERPA even with good intentions and even if the code appears correct.

   *Hint:* FERPA violations often happen at the boundaries of legitimate use, not from malicious access, but from a student asking a question that sounds innocent but causes the system to return information about someone else.  Can you construct a natural-sounding question that might trick a naive agent into doing this?

---

## Exercises

1.  **EU AI Act classification.**

   *What to do:* For each of the following agent systems from the course, assign an EU AI Act risk tier (Unacceptable / High / Limited / Minimal) and write a one-paragraph justification citing specific tier criteria: (a) the RAG agent that answers questions about course readings, (b) the coding agent that reviews student code and gives feedback, (c) a hypothetical agent that recommends mental health resources based on student chat patterns, (d) an agent that schedules campus events based on historical attendance data, (e) an agent that predicts which students are at risk of dropping a course.

   *Starter hint:* For each system, ask yourself: (1) Does it make a consequential decision about an individual person, one that affects their rights, opportunities, or wellbeing?  (2) Is it in a sector explicitly listed in Annex III (the EU AI Act's enumerated list of High Risk application domains, including employment, education, healthcare, law enforcement, critical infrastructure)?  (3) Does it deploy any manipulation technique?  Systems (c) and (e) are the most complex cases; work through those carefully.  For (c), consider whether recommending mental health resources constitutes providing medical advice.

   *You've succeeded when:* Each classification is supported by at least one specific criterion from the EU AI Act text, and the justifications for borderline cases (b), (c), and (e) acknowledge the arguments on both sides before reaching a conclusion.

2.  **NIST RMF risk register.**

   *What to do:* Using the four NIST RMF functions as column headers (Govern / Map / Measure / Manage), create a one-page risk register for the course RAG agent.  For each function column, identify one specific risk, one activity to address it, and one artifact that would document the team's response.

   *Starter hint:* Here is a starter row to show the format; fill in the remaining three columns with different risks: **Govern** | Risk: No one is accountable if the agent produces harmful output | Activity: Assign a named "AI owner" who reviews all deployment decisions | Artifact: Roles and responsibilities document signed by the team.  Now complete Map, Measure, and Manage with distinct risks specific to a RAG agent (think about retrieval quality, hallucination, and data freshness as potential risk sources).

   *You've succeeded when:* Each cell contains a specific, concrete entry, not a generic statement like "check for bias" but a specific risk (e.g., "the retrieval corpus contains outdated advising policies from 2019") and a specific artifact (e.g., "corpus freshness audit report with dates of all source documents").

3.  **GDPR enforcement research.**

   *What to do:* Find one real enforcement action taken by a European data protection authority (DPA) under GDPR that involved AI, automated decision-making, or algorithmic profiling.  Write a one-paragraph summary covering: what the company did, which GDPR article was violated, what the fine or remedy was, and what lesson the enforcement action carries for developers building agents today.

   *Starter hint:* Search the GDPR Enforcement Tracker at https://www.enforcementtracker.com/; filter by "automated decision-making" or "profiling" to find relevant cases.  Notable cases have involved credit scoring algorithms, behavioral advertising profiles, and AI hiring tools.  Pick a case you find interesting rather than the most famous one.

   *You've succeeded when:* Your paragraph identifies the specific GDPR article violated (e.g., Article 22 on automated individual decision-making, or Article 5 on data minimization), gives the actual fine amount, and draws a specific lesson that applies to one of the agent systems you have built this semester.

---

## Reflection Prompt

**Personal level:** Have you ever interacted with an automated decision-making system (a scholarship algorithm, a loan application screener, a social media content ranker) without knowing it was AI? How did you feel when you learned (or imagined learning) that a machine was making a consequential decision about you?  How does that experience change how you think about building AI systems for others?

**Technical level:** If you publish an open-source agent on GitHub and someone else later deploys it in a high-risk context you never intended (say, screening job applications at a Fortune 500 company) who bears legal and moral responsibility for compliance failures?  Consider the roles of: the original developer, the company deploying it, the vendor providing the underlying LLM, and the regulatory framework that governs the deployment context.

**Societal level:** The EU AI Act bans certain AI applications outright (social scoring, real-time biometric surveillance in public spaces).  The United States has no equivalent federal ban.  What values are expressed by each approach?  Which approach do you think better serves the public, and what evidence would change your mind?

---

-> **Coming Up Next:** In the next activity, we examine how to document the data and models that power agents (using Datasheets for Datasets and Model Cards) so that regulators, auditors, and future developers can verify that compliance obligations were met.

---

## Further Reading

- EU AI Act full text (Regulation 2024/1689): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689
- NIST AI RMF 1.0: https://airc.nist.gov/RMF
- FDA AI/ML-Based Software as a Medical Device: https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-software-medical-device
- Federal Reserve SR 11-7 Model Risk Management Guidance: https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm
- Future of Privacy Forum.  "Student Privacy and AI." https://fpf.org/
