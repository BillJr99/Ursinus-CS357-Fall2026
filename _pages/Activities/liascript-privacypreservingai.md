<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-privacypreservingai.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Privacy-Preserving AI: Federated Learning, Differential Privacy, and PII Scrubbing

CS357 - Foundations of Artificial Intelligence / Agentic AI | Ursinus College

---

## POGIL Roles

This activity uses the **POGIL** (Process Oriented Guided Inquiry Learning) structure. Before beginning, assign one role to each group member:

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task, ensures everyone contributes, watches the clock |
| **Recorder** | Documents the group's answers and reasoning in writing |
| **Presenter** | Speaks for the group during class discussion, summarizes findings |
| **Reflector** | Monitors group process, notes what is working and what is not, leads the Reflection section |

> Rotate roles across activities so everyone practices each one.

---

## Model 1: Why Privacy and AI Conflict

### The Training Data Problem

Large language models are trained on massive corpora scraped from the internet and licensed datasets. These corpora often contain **personally identifiable information (PII)**: email addresses, phone numbers, home addresses, medical records, financial information, and personal narratives. When the model trains on this data, it can **memorize** specific examples — not in an explicit lookup-table way, but as statistical patterns that can be elicited through targeted prompts.

**Carlini et al. (2021)** demonstrated this concretely: by prompting GPT-2 with prefixes extracted from the training corpus, they were able to extract:
- Full names combined with phone numbers
- Specific email addresses
- Home addresses of private individuals
- SSH private keys
- Unique identifiers from internal documents

This is not a bug — it is an emergent consequence of training on private data at scale.

### Privacy Attack Taxonomy

| Attack Type | What the Attacker Learns | Data Required by Attacker | How Realistic | Key Defense |
|-------------|-------------------------|--------------------------|---------------|-------------|
| **Memorization / Extraction** | Verbatim training data (PII, secrets, documents) | Only API access to the model | High — demonstrated at scale | Differential privacy during training, PII scrubbing before training |
| **Membership Inference** | Whether a specific record was in the training set | The target model + the candidate record | Medium — accuracy varies by model and data type | DP training, output smoothing |
| **Model Inversion** | Features or attributes of training data records from model outputs | API access + many queries | Medium — easier for simpler models | Output perturbation, rate limiting |
| **Attribute Inference** | Sensitive attributes (income, health status) given partial data | Black-box model access + auxiliary data | Medium to high in structured prediction tasks | Data minimization, purpose limitation |

### Anonymization vs. Pseudonymization

These terms are frequently conflated:

- **Anonymization**: Removing or altering data so that re-identification is impossible, even with auxiliary data. True anonymization is extremely difficult — most "anonymized" datasets have been re-identified using publicly available auxiliary information.
- **Pseudonymization**: Replacing identifiers (names, SSNs) with pseudonyms (arbitrary IDs). Re-identification is possible if the pseudonym mapping is exposed or if enough quasi-identifiers remain. GDPR treats pseudonymized data as still being personal data.

### Critical Thinking Questions

**Question 1.** Your company decides to fine-tune a frontier LLM on your internal Slack messages and email threads to build an internal knowledge assistant. What memorization risk does this create? Who could be harmed, and under what circumstances?

[[___ Your answer here ___]]

> Consider: What is in those messages? Performance reviews, salary discussions, medical leave requests, customer complaints? Who might prompt the model in a way that extracts specific messages? What is the attack surface?

---

**Question 2.** A user interacts with your AI agent over a long conversation, sharing personal details (health symptoms, relationship problems, financial worries). At the next session, the agent does not remember any of it. The user is surprised and upset. Name one scenario where this "forgetting" violates reasonable expectations, and one where it protects the user.

[[___ Your answer here ___]]

> Hint: Is there a difference between a therapist forgetting and a search engine forgetting? What expectations does each context create? What if the user shared something they later regretted — does forgetting protect or harm them?

---

**Question 3.** A dataset vendor says "we anonymized all user data before including it in our training corpus." What questions should you ask before trusting that claim? What is the difference between anonymization and pseudonymization in this context, and why does it matter for privacy guarantees?

[[___ Your answer here ___]]

> Key questions: What quasi-identifiers remain? What auxiliary datasets could be used for re-identification? Were rare individuals more exposed than common ones? Was a formal privacy model (k-anonymity, l-diversity, differential privacy) used?

---

## Model 2: Privacy-Preserving Techniques

### Differential Privacy (DP)

Differential privacy provides a **formal mathematical guarantee**: any two datasets that differ by exactly one individual's record will produce outputs that are statistically indistinguishable up to a factor controlled by the **privacy budget ε (epsilon)**.

Formally: a mechanism M satisfies ε-differential privacy if, for all adjacent datasets D and D' and all outputs S:

**Pr[M(D) ∈ S] ≤ e^ε × Pr[M(D') ∈ S]**

Smaller ε = stronger privacy = more noise added = lower accuracy.

| Privacy Budget (ε) | Privacy Guarantee | Accuracy Impact | Practical Meaning |
|-------------------|-------------------|-----------------|-------------------|
| ε = 0.1 | Very strong | Severe accuracy loss | Adds so much noise that aggregate statistics are rough estimates |
| ε = 1.0 | Strong | Moderate accuracy loss | Common target for sensitive domains (health, finance) |
| ε = 10 | Weak | Minimal accuracy loss | Near-original accuracy; formal guarantee exists but is loose |
| ε = ∞ | No privacy guarantee | No accuracy loss | Equivalent to no DP at all |

### Federated Learning (FL)

In traditional training, all data is sent to a central server. In federated learning:

1. A global model is distributed to N clients (devices, hospitals, organizations)
2. Each client trains locally on their private data, computing gradient updates
3. Only gradient updates (not raw data) are sent to an aggregation server
4. The server aggregates updates (typically by averaging) to improve the global model
5. The improved global model is redistributed and the process repeats

**Key Properties:**

- Raw data never leaves the client
- The aggregated model incorporates learning from all clients
- **Gradient inversion attacks** (Zhu et al., 2019) demonstrated that in some settings, an honest-but-curious server can reconstruct training images from gradient updates — so FL does not provide perfect privacy by itself

**FL is strongest when combined with DP** (adding noise to gradient updates before sharing) and **secure aggregation** (cryptographic techniques that prevent the server from seeing individual updates).

### PII Scrubbing

Three approaches to removing PII from text before training or inference:

1. **Regex patterns**: Fast, cheap, catches structured PII (phone numbers, SSNs, emails, credit card numbers). Misses unstructured PII (names, addresses in varied formats).
2. **NER (Named Entity Recognition) models**: ML models (spaCy, Presidio) that detect entities including PERSON, LOCATION, ORG, DATE. Better recall than regex on natural language, but adds false positives and misses domain-specific PII.
3. **LLM-based redaction**: Use a language model to identify and replace PII in context. Most accurate but most expensive; introduces a dependency on the very technology whose outputs may contain PII.

**Comparison of Privacy-Preserving Techniques**

| Technique | What It Protects | Implementation Complexity | Accuracy Cost | Practical Limitation |
|-----------|-----------------|--------------------------|---------------|---------------------|
| Differential Privacy | Statistical inference about individual records | High (requires careful noise calibration) | Moderate to severe, depending on ε | Hard to apply to large language models; ε is often too loose to be meaningful |
| Federated Learning | Raw data leaving client premises | High (distributed infrastructure, aggregation protocol) | Low to moderate | Gradient inversion attacks; communication overhead; non-IID data across clients |
| PII Scrubbing | Verbatim PII in training data or prompts | Low to medium (regex easy; NER harder; LLM-based expensive) | Low (if recall is high) | Cannot remove all forms of re-identifiable information; misses implicit PII |

### Critical Thinking Questions

**Question 4.** A hospital wants to fine-tune a clinical NLP model. They are choosing between ε=0.1 and ε=10 for differential privacy. They are optimizing for early detection of rare diseases from clinical notes, where accuracy is critical. Which value would you recommend, and what trade-off are you accepting? Is there a better approach than binary choice?

[[___ Your answer here ___]]

> Consider: ε=0.1 may add so much noise that the model cannot learn rare disease patterns. ε=10 provides a very loose guarantee. Are there alternatives — like training on synthetic data, using FL without DP on aggregated updates, or limiting what the model can output?

---

**Question 5.** In 2019, Zhu et al. demonstrated that a malicious or curious aggregation server in a federated learning setup could reconstruct training images from gradient updates — a **gradient inversion attack**. How does this change your assessment of federated learning as a privacy solution for medical imaging? What defenses exist?

[[___ Your answer here ___]]

> Defenses: Adding DP noise to gradients before sharing. Gradient compression (dropping small gradients, which reduces attack signal). Secure aggregation (server only sees the sum, not individual updates). What does each defense cost in model quality or infrastructure?

---

**Question 6.** You are scrubbing PII from a dataset of customer support chat transcripts before using them for fine-tuning. A customer's message says: "I've been dealing with this since my surgery last March, and my doctor at Phoenixville Hospital said…". A regex for names and SSNs does not flag this. What categories of PII does it contain, and what scrubbing approach would catch them?

[[___ Your answer here ___]]

> This message contains: implied health information, a named healthcare facility, and an implied approximate date and location. NER would catch the facility name; an LLM-based scrubber might catch the health implication. What does "removing PII" mean when the PII is implied by context rather than stated explicitly?

---

### Multiple Choice Question

A hospital wants to fine-tune a large language model on patient clinical notes to build a discharge summary assistant. They want to do this without transmitting patient data to the model vendor. The most appropriate privacy-preserving approach is:

[[ ]] Anonymize the notes by removing patient names and dates of birth, then send to the vendor for fine-tuning
[[x]] Use federated learning: keep patient notes within the hospital's own network, fine-tune a local copy of the model, and share only gradient updates (not patient data) with the aggregation infrastructure
[[ ]] Use the vendor's public cloud API and include patient notes in system prompts, relying on the vendor's terms of service
[[ ]] Apply differential privacy only at inference time (add noise to model outputs), leaving training data unrestricted

> **Why this answer?** Federated learning keeps raw patient data on-premises, which is the core requirement when data cannot leave the institution. Anonymization is insufficient because clinical notes often contain re-identifiable combinations of rare diagnoses, facility names, and dates. System-prompt use of PHI likely violates HIPAA Business Associate Agreement requirements. Inference-time DP does not address training data exposure at all.

---

## Model 3: Practical PII Handling for Agents

### The Three-Layer Defense

When an AI agent processes user inputs and produces outputs, PII can enter and leak at multiple points:

**Layer 1 — Input Scrubbing**: Before the user's message is sent to the LLM, detect and redact PII. Replace with typed placeholders: `[PERSON_NAME]`, `[PHONE_NUMBER]`, `[SSN]`. Maintain a session-scoped mapping if the agent needs to dereference the placeholder later.

**Layer 2 — Output Scrubbing**: After the LLM generates a response, scan for potential memorized PII (email addresses, phone numbers, names) before returning to the user. Log flagged instances for review.

**Layer 3 — Logging Policy**: Define what the agent system retains:
- What conversation data is stored and where?
- For how long? (Retention period)
- Who can access it? (Access control)
- When is it deleted? (Deletion triggers: user request, session end, time-based)

### The Right to Be Forgotten and Model Weights

GDPR Article 17 grants individuals the right to erasure — the right to have their personal data deleted. For most databases, this is straightforward: delete the row. For AI models, it is deeply problematic:

- If a person's data was included in training, their information is encoded into **billions of parameters distributed across the entire model**
- There is no "delete" button on a weight matrix
- **Machine unlearning** is an active research field: approximate techniques that fine-tune the model to reduce the influence of a specific data point, without full retraining
- No approach is currently both efficient and formally verifiable

### Relevant Regulations

- **GDPR** (EU): Data minimization, purpose limitation, right to erasure, data protection by design, mandatory breach notification within 72 hours
- **CCPA** (California): Right to know what data is collected, right to delete, right to opt out of sale, non-discrimination for exercising rights
- Both apply to AI systems that process EU/California residents' data, regardless of where the AI company is located

### Critical Thinking Questions

**Question 7.** A user asks your customer service agent: "Can you check the status of my order? My name is Sarah Johnson, my account number is 7734-2291, and my Social Security Number is 555-12-3456." The SSN was almost certainly included by accident. What should the agent do, in order? Write a step-by-step response protocol.

[[___ Your answer here ___]]

> Consider: (1) Detect the SSN before it reaches the LLM. (2) Redact it in the stored log immediately. (3) Complete the task using only the account number. (4) Respond to the user — do you tell them you detected sensitive data? Do you warn them? Do you ask them to contact support through a more secure channel?

---

**Question 8.** A user requests deletion of their data under GDPR. Your company confirms it has deleted their account from the database, the conversation logs, and all backups. However, a fine-tuned model was trained on their support conversations six months ago. Is the GDPR obligation satisfied? What options exist for handling model-weight-embedded personal data?

[[___ Your answer here ___]]

> Consider: Is the data "identifiable" if it is encoded in weights rather than stored as a record? The ICO (UK Information Commissioner's Office) has begun addressing this question. What are the practical options: approximate unlearning, retraining without the data, disclosure to the user that weight-embedded data cannot be deleted, or something else?

---

**Question 9.** Design a three-rule PII handling policy for the AI agent you built in this course. Each rule should specify: (a) what it covers, (b) what action is taken, and (c) how compliance is verified or monitored. Write the rules in formal policy language.

[[___ Your answer here ___]]

> Example structure: "Rule 1: No user input containing [category] SHALL be transmitted to the LLM without prior redaction by [mechanism]. Compliance shall be verified by [automated test / audit log / human review]."

---

## Exercises

**Exercise 1.** Install the spaCy library and its `en_core_web_sm` model, or use a language model via API. Prepare five sample texts containing different forms of PII (one with only structured PII like phone numbers; one with names and locations; one with health information; one with financial information; one with implicit PII through context). Run NER-based PII detection on each. Compare the tool's detections against your manual labeling. Compute precision and recall. What did it miss and why?

> Deliverable: The five texts, the tool's output, your manual labels, and a precision/recall analysis with at least one hypothesis about why errors occurred.

---

**Exercise 2.** Read Carlini et al. (2021), "Extracting Training Data from Large Language Models." Write a 400-word summary covering: (a) what specific data they extracted and from which model, (b) the method they used to generate candidate extractions and rank them, (c) what fraction of their top-ranked extractions were actually verbatim training data, and (d) what mitigation reduced the attack's effectiveness.

> Deliverable: 400-word summary with at least one direct quotation from the paper and a citation.

---

**Exercise 3.** Draft a data retention policy for a RAG-based knowledge base agent (similar to the lab in this course). The policy should specify: (a) what data is stored at each stage (user queries, retrieved chunks, model responses, user feedback), (b) the retention period for each data type and the justification, (c) who is authorized to access each data type, (d) the deletion mechanism and how a user can request deletion, and (e) how the policy is enforced technically.

> Deliverable: A formatted policy document of at least 400 words, written in formal policy language suitable for review by a privacy officer.

---

## Reflection Prompt

Every technique in this activity — differential privacy, federated learning, PII scrubbing — reduces privacy violations rather than eliminating them. DP provides a mathematical bound, not a guarantee that no harm occurs. FL keeps raw data on-premises, but gradient leakage remains possible. PII scrubbing catches detectable identifiers but not implicit re-identification risk.

What would it mean for AI to genuinely respect privacy as a fundamental right, rather than as a compliance checkbox? Is "privacy by design" achievable in practice for large-scale AI systems? And if not — if some privacy violation is an unavoidable cost of capable AI — who should decide what that cost is, and who should bear it?

Write at least 200 words.

[[___ Your reflection here ___]]

---

## Further Reading

- Carlini, N. et al. (2021). *Extracting Training Data from Large Language Models.* Proceedings of USENIX Security 2021. https://arxiv.org/abs/2012.07805

- McMahan, H. B. et al. (2017). *Communication-Efficient Learning of Deep Networks from Decentralized Data.* Proceedings of AISTATS 2017. https://arxiv.org/abs/1602.05629

- Dwork, C. & Roth, A. (2014). *The Algorithmic Foundations of Differential Privacy.* Foundations and Trends in Theoretical Computer Science. https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf

- Zhu, L. et al. (2019). *Deep Leakage from Gradients.* NeurIPS 2019. https://arxiv.org/abs/1906.08935

- European Parliament. (2016). *General Data Protection Regulation (GDPR).* https://gdpr-info.eu/

- Microsoft Presidio. (2023). *Open-source PII detection and anonymization framework.* https://github.com/microsoft/presidio
