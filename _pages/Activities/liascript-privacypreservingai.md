<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-privacypreservingai.md

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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Personally Identifiable Information (PII)** | Any data that could identify a specific person, either alone or when combined with other information, such as a name, phone number, or medical diagnosis | A Slack message containing an employee's salary or health condition |
| **Differential Privacy (ε)** | A mathematical guarantee that adding or removing one person's data from a dataset changes the output by at most a small, controlled amount, controlled by the privacy budget ε (epsilon) | Adding calibrated noise to a hospital's patient count so you can see trends without knowing if any one patient was included |
| **Federated Learning** | A training approach where the model travels to the data rather than the data traveling to the model; each participant trains locally and shares only weight updates, never raw records | Hospitals in five states each train on their own patient notes; only gradient updates are aggregated centrally |
| **Memorization / Extraction Attack** | A technique in which an attacker sends carefully crafted prompts to an LLM and recovers verbatim text from the training corpus, including private records the model was never meant to reveal | Researchers prompting GPT-2 to reproduce real SSH private keys and home addresses from its training data |
| **PII Scrubbing** | The process of automatically detecting and removing or replacing personal information before it reaches an LLM or is stored in logs | Replacing "John Smith, SSN 555-12-3456" with "[PERSON_NAME], [SSN]" before sending a support ticket to a model |
| **Machine Unlearning** | An emerging research area focused on making a trained model "forget" a specific person's data without retraining the entire model from scratch | Approximately removing a deleted user's support conversations from a fine-tuned customer service model |

---

## Model 1: Why Privacy and AI Conflict

Think of AI training data like a sponge: once you soak up water, you can't easily squeeze out just one drop. An LLM trained on private data absorbs personal information into billions of parameters spread across the entire model; there is no simple "delete this person's data" button. Differential privacy is like adding just enough noise to a survey that you can't tell what any one person answered, but the average is still accurate; the model learns useful patterns without memorizing individual secrets. This tension between *learning from data* and *protecting the people that data describes* is the central problem of privacy-preserving AI.

### The Training Data Problem

Large language models are trained on massive corpora scraped from the internet and licensed datasets. These corpora often contain **personally identifiable information (PII)**: email addresses, phone numbers, home addresses, medical records, financial information, and personal narratives. When the model trains on this data, it can **memorize** specific examples, not in an explicit lookup-table way, but as statistical patterns that can be elicited through targeted prompts.

**Carlini et al. (2021)** demonstrated this concretely: by prompting GPT-2 with prefixes extracted from the training corpus, they were able to extract:
- Full names combined with phone numbers
- Specific email addresses
- Home addresses of private individuals
- SSH private keys
- Unique identifiers from internal documents

This is not a bug; it is an emergent consequence of training on private data at scale.

### A Concrete Before/After Scrubbing Example

**Before scrubbing (raw support ticket):**
> "Hi, I'm Sarah Johnson, DOB 03/14/1987. My SSN is 555-12-3456 and I need help with account 7734-2291. I've been dealing with this since my surgery at Phoenixville Hospital last March."

**After scrubbing (what the model actually receives):**
> "Hi, I'm [PERSON_NAME], DOB [DATE]. My [SSN] and I need help with account [ACCOUNT_NUMBER]. I've been dealing with this since my [MEDICAL_EVENT] at [HEALTHCARE_FACILITY] last [DATE]."

Notice that the last sentence still implies a health event and a hospital; a regex looking for Social Security number patterns would miss it entirely. This is why scrubbing is harder than it looks.

### Privacy Attack Taxonomy

| Attack Type | What the Attacker Learns | Data Required by Attacker | How Realistic | Key Defense |
|-------------|-------------------------|--------------------------|---------------|-------------|
| **Memorization / Extraction** | Verbatim training data including PII, secrets, and private documents | Only API access to the model; no privileged knowledge required | High: demonstrated at scale by Carlini et al. (2021) | Differential privacy during training; PII scrubbing before training |
| **Membership Inference** | Whether a specific record (e.g., one patient's file) was included in the training set | The target model plus the candidate record being tested | Medium: accuracy varies by model architecture and data type | DP training; output smoothing to reduce confidence signals |
| **Model Inversion** | Reconstructed features or attributes of training data records from model outputs | API access plus many queries to observe output patterns | Medium: easier for simpler classification models | Output perturbation; rate limiting to prevent bulk queries |
| **Attribute Inference** | Sensitive attributes such as income or health status, inferred from partial data | Black-box model access plus auxiliary data about the target | Medium to high for structured prediction tasks | Data minimization; purpose limitation in system design |

### Anonymization vs. Pseudonymization

These terms are frequently conflated:

- **Anonymization**: Removing or altering data so that re-identification is impossible, even with auxiliary data. True anonymization is extremely difficult; most "anonymized" datasets have been re-identified using publicly available auxiliary information (e.g., Netflix viewing histories re-identified using IMDb ratings).
- **Pseudonymization**: Replacing identifiers such as names and Social Security numbers with pseudonyms such as arbitrary IDs. Re-identification is possible if the pseudonym mapping is exposed or if enough quasi-identifiers remain. The GDPR treats pseudonymized data as still being personal data subject to regulation.

### Critical Thinking Questions

**Question 1.** Your company decides to fine-tune a frontier LLM on your internal Slack messages and email threads to build an internal knowledge assistant. What memorization risk does this create? Who could be harmed, and under what circumstances?

[[___ Your answer here ___]]

> *Hint:* Think about what kinds of information live in workplace messages: performance reviews, salary discussions, medical leave requests, customer complaints, legal advice. Now imagine an employee (or an attacker who gains access to the assistant) crafting a prompt like "What did my manager say about my raise?" or "Summarize discussions about the Henderson contract." What is the attack surface, and who could exploit it?

---

**Question 2.** A user interacts with your AI agent over a long conversation, sharing personal details (health symptoms, relationship problems, financial worries). At the next session, the agent does not remember any of it. The user is surprised and upset. Name one scenario where this "forgetting" violates reasonable expectations, and one where it protects the user.

[[___ Your answer here ___]]

> *Hint:* Compare a therapist to a search engine. A therapist who forgets everything you said last week would be alarming; continuity of care depends on memory. A search engine that forgets your queries protects you from having a permanent record of your most private moments. Does an AI agent feel more like a therapist or a search engine to the user? Does context matter: what if the user shared something they later regretted, like suicidal thoughts? Does forgetting protect or harm them in that case?

---

**Question 3.** A dataset vendor says "we anonymized all user data before including it in our training corpus." What questions should you ask before trusting that claim? What is the difference between anonymization and pseudonymization in this context, and why does it matter for privacy guarantees?

[[___ Your answer here ___]]

> *Hint:* Start by asking: what quasi-identifiers remain after anonymization? A person's age, zip code, and gender together can identify most individuals in the US. What auxiliary datasets could an attacker use to re-identify people: public voter rolls, social media, news articles? Were rare individuals (people with unusual diagnoses, unusual names) more exposed than common ones? Was a formal privacy model such as k-anonymity, l-diversity, or differential privacy applied, and if so, what were its parameters?

---

Now that you understand how and why private information leaks from AI systems, you are ready to study the technical defenses (and their specific limitations) that engineers use to reduce those risks.

## Model 2: Privacy-Preserving Techniques

If Model 1 was about understanding the threat, Model 2 is about the defenses. None of these techniques is a silver bullet: differential privacy reduces statistical leakage but costs model accuracy; federated learning keeps raw data local but is vulnerable to gradient inversion; PII scrubbing catches obvious identifiers but misses contextual ones. Real privacy protection requires combining all three layers, just as a bank uses locked vaults, security cameras, and access logs together rather than relying on any one alone.

### Differential Privacy (DP)

Differential privacy provides a **formal mathematical guarantee**: any two datasets that differ by exactly one individual's record will produce outputs that are statistically indistinguishable up to a factor controlled by the **privacy budget ε (epsilon)**.

Formally: a mechanism M satisfies ε-differential privacy if, for all adjacent datasets D and D' and all outputs S:

**Pr[M(D) ∈ S] ≤ e^ε × Pr[M(D') ∈ S]**

In plain English: if you were in the dataset and I ran the mechanism, you could not tell whether your data was included or not, up to a factor of e^ε. Smaller ε means a tighter guarantee, but also more noise added, which reduces accuracy.

| Privacy Budget (ε) | Privacy Guarantee | Accuracy Impact | Practical Meaning |
|-------------------|-------------------|-----------------|-------------------|
| ε = 0.1 | Very strong: nearly indistinguishable with or without your data | Severe accuracy loss on complex tasks | Appropriate for aggregate statistics on very large datasets; rarely usable for LLM fine-tuning |
| ε = 1.0 | Strong: a common target for sensitive health and financial applications | Moderate accuracy loss, often acceptable for simpler tasks | The gold standard for high-stakes deployments when achievable |
| ε = 10 | Weak: a formal guarantee exists but the bound is loose | Minimal accuracy loss, close to non-private baseline | Used when some formal guarantee is required but accuracy is paramount |
| ε = ∞ | No privacy guarantee whatsoever | No accuracy loss | Mathematically equivalent to not using DP at all |

### Federated Learning (FL)

In traditional training, all data is sent to a central server. In federated learning:

1. A global model is distributed to N clients (individual devices, hospitals, or partner organizations)
2. Each client trains locally on their private data, computing gradient updates relative to the current global model
3. Only gradient updates (mathematical vectors describing how to improve the model) are sent to an aggregation server; raw data never leaves the client
4. The server aggregates updates (typically by weighted averaging) to produce an improved global model
5. The improved global model is redistributed to clients and the process repeats

**Key Properties:**

- Raw data never leaves the client's premises
- The aggregated model incorporates learning from all clients' private data
- **Gradient inversion attacks** (Zhu et al., 2019) demonstrated that an honest-but-curious aggregation server can sometimes reconstruct training images or text from gradient updates alone, so federated learning does not provide perfect privacy by itself

**FL is strongest when combined with DP** (adding calibrated noise to gradient updates before sharing) and **secure aggregation** (cryptographic techniques that prevent the server from seeing any individual client's update).

### PII Scrubbing

Three approaches to removing PII from text before training or inference:

1. **Regex patterns**: Fast and cheap; reliably catches structured PII such as phone numbers in standard formats, Social Security numbers, email addresses, and credit card numbers. Misses unstructured PII such as names embedded in natural prose or addresses in non-standard formats.
2. **NER (Named Entity Recognition) models**: ML models such as spaCy and Microsoft Presidio that detect entities including PERSON, LOCATION, ORG, and DATE. Better recall than regex on natural language text, but introduces false positives (flagging common words as names) and still misses domain-specific PII such as employee badge numbers or patient MRN codes.
3. **LLM-based redaction**: Use a language model to identify and replace PII in context, including implicit PII conveyed by context rather than by explicit identifiers. Most accurate but most expensive; introduces a dependency on the very technology whose outputs may contain PII.

**Comparison of Privacy-Preserving Techniques**

| Technique | What It Protects | Implementation Complexity | Accuracy Cost | Practical Limitation |
|-----------|-----------------|--------------------------|---------------|---------------------|
| Differential Privacy | Statistical inference about whether any individual's record was in the training set | High: requires careful noise calibration per query type | Moderate to severe depending on ε and task complexity | Extremely hard to apply meaningfully to large language models; ε values achievable at LLM scale are often too loose to provide strong guarantees |
| Federated Learning | Raw data leaving the client's premises or network | High: requires distributed infrastructure, an aggregation protocol, and synchronization across clients | Low to moderate: non-IID data distributions across clients can harm model quality | Gradient inversion attacks undermine privacy guarantees; communication overhead slows training; client dropout creates uneven updates |
| PII Scrubbing | Verbatim PII appearing in training data or in real-time prompts and responses | Low to medium: regex is easy to implement; NER models require setup; LLM-based scrubbing requires an additional model call | Low if recall is high: scrubbing accurate PII tokens does not degrade model utility | Cannot remove all forms of re-identifiable information; implicit PII conveyed through context requires semantic understanding to detect |

> **Common Misconception:** Many people assume that "anonymizing" a dataset before training fully protects privacy. In practice, anonymization is nearly impossible to achieve for rich text data. Clinical notes, support tickets, and personal narratives contain combinations of rare details (unusual diagnoses, specific events, distinctive writing styles) that remain re-identifiable even after named entities are removed. Differential privacy is the only technique that provides a *formal* guarantee, and even then, the guarantee's strength depends entirely on the ε value chosen and the size of the dataset.

### Critical Thinking Questions

**Question 4.** A hospital wants to fine-tune a clinical NLP model. They are choosing between ε = 0.1 and ε = 10 for differential privacy. They are optimizing for early detection of rare diseases from clinical notes, where accuracy is critical. Which value would you recommend, and what trade-off are you accepting? Is there a better approach than a binary choice between these two values?

[[___ Your answer here ___]]

> *Hint:* ε = 0.1 adds so much noise that the model may be unable to learn patterns for rare diseases; if only 5 patients in the dataset have the rare condition, the noise swamps the signal. ε = 10 provides a formal guarantee that is technically valid but practically loose. Are there better alternatives? Consider training on high-quality synthetic patient data generated from a separately privacy-protected model, using federated learning without DP on already-aggregated statistics, or carefully limiting what the model is allowed to output even if training is less private.

---

**Question 5.** In 2019, Zhu et al. demonstrated that a malicious or curious aggregation server in a federated learning setup could reconstruct training images from gradient updates, a **gradient inversion attack**. How does this change your assessment of federated learning as a privacy solution for medical imaging? What defenses exist, and what do they cost?

[[___ Your answer here ___]]

> *Hint:* The three main defenses are: (1) Adding DP noise to each client's gradient updates before they are sent to the server; this works but reduces model accuracy and requires tuning ε for the gradient space, not the output space. (2) Gradient compression, dropping or quantizing small gradient values, which reduces the information available for reconstruction but also slows convergence. (3) Secure aggregation using cryptographic protocols such as homomorphic encryption or secure multiparty computation; the server receives only the sum of all gradients, never individual updates, but this requires significant computational overhead. What does each defense cost in model quality, infrastructure complexity, or training time?

---

**Question 6.** You are scrubbing PII from a dataset of customer support chat transcripts before using them for fine-tuning. A customer's message says: "I've been dealing with this since my surgery last March, and my doctor at Phoenixville Hospital said...". A regex for names and Social Security numbers does not flag this message at all. What categories of PII does this sentence contain, and what scrubbing approach would catch them?

[[___ Your answer here ___]]

> *Hint:* This sentence contains: (1) implied health information, the customer had surgery, which is sensitive medical data; (2) the name of a healthcare facility, which narrows location and implies the patient has a relationship with that institution; (3) an approximate date, which combined with other data could help identify the individual. An NER model would likely catch "Phoenixville Hospital" as an ORG entity and "last March" as a DATE. An LLM-based scrubber is the only approach likely to recognize that "my surgery" is itself a health disclosure that should be redacted. What does it even mean to "remove PII" when the information is implied by context rather than stated explicitly as a named field?

---

### Multiple Choice Question

A hospital wants to fine-tune a large language model on patient clinical notes to build a discharge summary assistant. They want to do this without transmitting patient data to the model vendor. The most appropriate privacy-preserving approach is:

[[ ]] Anonymize the notes by removing patient names and dates of birth, then send the anonymized data to the vendor for fine-tuning on their servers
[[x]] Use federated learning: keep patient notes within the hospital's own network, fine-tune a local copy of the model, and share only gradient updates (not patient data) with the aggregation infrastructure
[[ ]] Use the vendor's public cloud API and include patient notes in system prompts, relying on the vendor's terms of service to protect confidentiality
[[ ]] Apply differential privacy only at inference time by adding noise to model outputs, leaving the training data and process unrestricted

> **Why this answer?** Federated learning keeps raw patient data on-premises, which is the core requirement when data cannot leave the institution. Anonymization is insufficient because clinical notes often contain re-identifiable combinations of rare diagnoses, facility names, and dates; removing names alone does not prevent re-identification. Passing Protected Health Information (PHI) through a vendor's API in system prompts almost certainly violates the HIPAA Business Associate Agreement requirements that govern how vendors may use that data. Inference-time DP adds noise to outputs but does not address training data exposure at all; the model was already trained on private data before any DP is applied.

---

With the theoretical defenses in hand, you are ready to apply them in the concrete operational context of a real AI agent system, where PII enters through user inputs, can be echoed back in outputs, and must be managed through a layered logging and deletion policy.

## Model 3: Practical PII Handling for Agents

### The Three-Layer Defense

When an AI agent processes user inputs and produces outputs, PII can enter and leak at multiple points. A robust system defends at every layer:

**Layer 1 - Input Scrubbing**: Before the user's message is sent to the LLM, detect and redact PII. Replace identified items with typed placeholders: `[PERSON_NAME]`, `[PHONE_NUMBER]`, `[SSN]`. Maintain a session-scoped mapping table if the agent needs to dereference the placeholder later (for example, to address the user by their name in a response without the LLM itself storing the name).

**Layer 2 - Output Scrubbing**: After the LLM generates a response, scan for potential memorized PII (email addresses, phone numbers, names from training data) before returning the response to the user. Log flagged instances for human review, and consider blocking the response if high-confidence PII is detected.

**Layer 3 - Logging Policy**: Define explicitly what the agent system retains and for how long:
- What conversation data is stored and where? (User device, company servers, third-party logging provider)
- For how long is it retained? (Session only, 30 days, indefinitely)
- Who is authorized to access it? (Engineering, support, legal, no one)
- Under what conditions is it deleted? (User request via GDPR Article 17, session end, time-based expiration)

### The Right to Be Forgotten and Model Weights

GDPR Article 17 grants individuals the right to erasure, the right to have their personal data deleted. For most databases, this is operationally straightforward: delete the row and cascade deletions to backup tables. For AI models, it is deeply problematic:

- If a person's data was included in training, their information is encoded into **billions of parameters distributed across the entire model**, not stored as a retrievable record
- There is no "delete" button on a weight matrix
- **Machine unlearning** is an active research field focused on approximate techniques: fine-tuning the model to reduce the statistical influence of a specific data point without full retraining. Current approaches include gradient ascent on the data to be forgotten and selective weight perturbation.
- No approach is currently both computationally efficient and formally verifiable; the model cannot certify that the data's influence has been fully removed

### Relevant Regulations

- **GDPR** (European Union, effective 2018): Mandates data minimization, purpose limitation, the right to erasure, data protection by design and by default, and mandatory breach notification within 72 hours of discovery
- **CCPA** (California Consumer Privacy Act, effective 2020): Grants California residents the right to know what personal data is collected, the right to delete it, the right to opt out of its sale, and protection against discrimination for exercising those rights
- Both regulations apply to AI systems that process data belonging to EU or California residents, regardless of where the AI company is physically located

### Critical Thinking Questions

**Question 7.** A user asks your customer service agent: "Can you check the status of my order? My name is Sarah Johnson, my account number is 7734-2291, and my Social Security Number is 555-12-3456." The SSN was almost certainly included by accident. Write a step-by-step response protocol: what should the agent do, in order, and what should it say to the user?

[[___ Your answer here ___]]

> *Hint:* A reasonable protocol involves these steps: (1) Detect the SSN *before* it reaches the LLM using a pre-processing layer; this means the LLM never sees the raw SSN. (2) Redact the SSN in any stored log immediately and irreversibly. (3) Complete the actual task (order status lookup) using only the account number, which is the appropriate identifier for this task. (4) Decide what to tell the user: do you warn them that you detected a sensitive number and did not store it? Do you recommend they contact support through a more secure channel? Be specific about the wording of the response.

---

**Question 8.** A user requests deletion of their data under GDPR. Your company confirms it has deleted their account record from the production database, the conversation logs, and all backups. However, a fine-tuned model was trained on their support conversations six months ago and is actively serving production traffic. Is the GDPR obligation satisfied? What practical options exist for handling model-weight-embedded personal data?

[[___ Your answer here ___]]

> *Hint:* The legal question is whether personal data "encoded in model weights" constitutes personal data in the GDPR sense: the model cannot reproduce the person's exact conversations verbatim (usually), but their information influenced the weights. The UK Information Commissioner's Office (ICO) has begun addressing this question. Practical options include: (1) approximate machine unlearning, fine-tune the model on a dataset that excludes the person's data; (2) full retraining without the person's data, which is expensive; (3) documenting to the user that weight-embedded data cannot be deleted with current technology and describing what was deleted; or (4) designing from the start not to include personal data in fine-tuning datasets. Which of these is most defensible legally? Most practically achievable?

---

**Question 9.** Design a three-rule PII handling policy for the AI agent you built in this course. Each rule should specify: (a) what category of data it covers, (b) what specific action is taken when that data is detected, and (c) how compliance with the rule is verified or monitored automatically. Write the rules in formal policy language.

[[___ Your answer here ___]]

> *Hint:* Use this structure as a template: "Rule 1: No user input containing [category, e.g., Social Security numbers matching the regex pattern \d{3}-\d{2}-\d{4}] SHALL be transmitted to the LLM inference endpoint without prior redaction by [mechanism, e.g., the pre-processing PII filter module]. Compliance SHALL be verified by [automated test / audit log review / canary injection of synthetic PII in CI/CD pipeline]." Write three rules covering at least three different categories of risk.

---

## Exercises

**Exercise 1.**

*What to do:* Install the spaCy library and its `en_core_web_sm` model (or use a language model via API). Prepare five sample texts containing different forms of PII: (1) only structured PII such as phone numbers and email addresses; (2) names and locations; (3) implied health information such as diagnoses or medication names; (4) financial information such as account numbers; (5) implicit PII conveyed through context rather than explicit identifiers. Run NER-based PII detection on each text. Compare the tool's detections against your own manual labeling.

*Starter hint:* For text 5, use something like: "I've been dealing with the same issue since my procedure at Children's Hospital of Philadelphia last February, when Dr. Martinez first prescribed the medication." The NER model will detect some entities; you should manually label everything that a privacy officer would want redacted.

*You've succeeded when:* You have a table showing tool detections vs. your manual labels for all five texts, computed precision and recall for each text, and written at least two hypotheses explaining specific false negatives (things you labeled as PII that the tool missed).

---

**Exercise 2.**

*What to do:* Read Carlini et al. (2021), "Extracting Training Data from Large Language Models." Write a 400-word summary covering: (a) what specific types of data they extracted and from which model; (b) the method they used to generate candidate extractions and rank them by likelihood of being memorized; (c) what fraction of their top-ranked extractions were confirmed as verbatim training data; and (d) what mitigation reduced the attack's effectiveness.

*Starter hint:* Pay attention to their "membership inference" scoring method; they use the model's own perplexity scores to rank likely memorized sequences. What does it mean that the model itself can be used to identify what it memorized?

*You've succeeded when:* Your summary is 400 words, includes at least one direct quotation from the paper with a page or section citation, and explicitly addresses all four points above in your own words.

---

**Exercise 3.**

*What to do:* Draft a data retention policy for a RAG-based knowledge base agent similar to the one built in this course's lab. The policy must address five points: (a) what data is stored at each stage (user queries, retrieved document chunks, model responses, user feedback); (b) the retention period for each data type and the reasoning behind it; (c) who is authorized to access each data type and under what conditions; (d) the deletion mechanism and how a user can request deletion; and (e) how the policy is enforced technically, not just administratively.

*Starter hint:* Start by listing every location where data could be stored: client browser, application server, vector database, LLM API provider logs, monitoring/observability platform, and backup systems. A complete policy must address all of these, not just the ones you directly control.

*You've succeeded when:* Your policy is at least 400 words written in formal policy language (use "SHALL," "MUST," "MUST NOT"), addresses all five points above, and would be credible to a privacy officer reviewing it before a product launch.

---

## Reflection Prompt

**Personal:** Think about an AI system you personally use that processes your private data: a voice assistant, a health app, a chatbot. Do you know what data it retains, for how long, and who can access it? Has knowing or not knowing this changed how you use it?

**Technical:** Every technique in this activity (differential privacy, federated learning, PII scrubbing) reduces privacy violations rather than eliminating them. DP provides a mathematical bound, not a guarantee that no harm occurs. FL keeps raw data on-premises but gradient leakage remains possible. PII scrubbing catches detectable identifiers but not implicit re-identification risk. Is there a fundamentally different technical approach that could achieve stronger guarantees, or is some residual privacy risk unavoidable for capable AI?

**Societal:** What would it mean for AI to genuinely respect privacy as a fundamental right rather than as a compliance checkbox? Is "privacy by design" achievable in practice for large-scale AI systems? If some privacy violation is an unavoidable cost of capable AI, who should decide what that cost is, and who should bear it? Should the people whose data was used to train the model have any say in how it is deployed?

Write at least 200 words addressing at least two of the three levels above.

[[___ Your reflection here ___]]

---

-> Coming Up Next: In the next activity, we examine how models are deployed on real hardware, including the tradeoffs between running AI in the cloud versus running it locally on devices that never connect to the internet at all.

## Further Reading

- Carlini, N. et al. (2021). *Extracting Training Data from Large Language Models.* Proceedings of USENIX Security 2021. https://arxiv.org/abs/2012.07805

- McMahan, H. B. et al. (2017). *Communication-Efficient Learning of Deep Networks from Decentralized Data.* Proceedings of AISTATS 2017. https://arxiv.org/abs/1602.05629

- Dwork, C. & Roth, A. (2014). *The Algorithmic Foundations of Differential Privacy.* Foundations and Trends in Theoretical Computer Science. https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf

- Zhu, L. et al. (2019). *Deep Leakage from Gradients.* NeurIPS 2019. https://arxiv.org/abs/1906.08935

- European Parliament. (2016). *General Data Protection Regulation (GDPR).* https://gdpr-info.eu/

- Microsoft Presidio. (2023). *Open-source PII detection and anonymization framework.* https://github.com/microsoft/presidio
