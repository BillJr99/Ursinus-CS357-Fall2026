<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-ipprivacy.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-ipprivacy.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Intellectual Property, Privacy, and the Case for Local AI

The *Training Data and Bias* activity showed what models absorb from their training distributions; today we ask who owns that material and who gets watched.  Generative models are trained on creative work and prompted with personal information, which places two bodies of law and ethics (intellectual property and privacy) at the center of agentic practice.  Today we map both, *as engineers*: not to play lawyer, but to recognize the decisions that have legal and ethical weight and to design accordingly, with our local-first stack as a recurring answer.  The path today: **the IP questions → the privacy questions → regulatory landscape → design responses you already know how to build**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  These questions are contested; the Reflector again guards against premature convergence.  Nothing today is legal advice, and that disclaimer is itself a lesson in professional boundaries.  After class, please respond to the reflective prompt on your own in your notebook.

---

### Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Copyright** | A legal right that gives the creator of an original work exclusive control over its use and distribution for a limited time. | An author owns the text of their novel; a model trained on that novel raises questions about whether that use was authorized. |
| **Fair Use** | A legal doctrine in US copyright law that permits limited use of copyrighted material without permission, based on four factors: purpose, nature of the work, amount used, and market effect. | Courts use fair use to decide whether AI training on copyrighted books is lawful; the answer is not yet settled. |
| **FERPA** | The Family Educational Rights and Privacy Act, a US law that restricts who may access student educational records such as grades, transcripts, and advising notes. | Pasting a class roster with student names and grades into a consumer chatbot could violate FERPA. |
| **Data Minimization** | The privacy engineering principle of collecting, processing, and retaining only the data actually needed for a specific task, nothing extra, nothing "just in case." | Stripping student names before running essays through an AI grading assistant is a data minimization practice. |
| **Memorization** | The phenomenon where a model reproduces verbatim text from its training data in its outputs, creating potential copyright infringement risk. | Researchers have demonstrated that repeating a prompt about a specific book excerpt can cause a model to reproduce full passages. |
| **Local Inference** | Running an AI model entirely on your own hardware so that no input data ever travels to a third-party server. | Using Ollama on your laptop to analyze sensitive documents keeps those documents off any external service's infrastructure. |

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Part I, intellectual property: whose work is in the model |
| 10-25 | Part II, privacy, and the data-flow audit |
| 25-60 | Part IIb, the techniques behind the argument: federated learning, differential privacy, and PII scrubbing |
| 60-75 | Part III, synthesis.  The AI Creativity Extension is self-paced |

---

# Part I: Intellectual Property

In this part, you will learn to separate three legally distinct questions about AI and intellectual property that news coverage routinely conflates.  Keeping these three questions distinct will help you reason more carefully about your own projects and about the legal landscape you'll navigate as a practitioner.

## 1.  Three Distinct Questions

Three separate questions arise at the intersection of AI and intellectual property, and conflating them produces confused reasoning.  Keep them apart whenever you read news coverage, policy proposals, or vendor terms of service.

Question 1 - Input: was training a lawful use of copyrighted work?  Training corpora include books, code, journalism, and art whose creators largely did not consent.  Litigation (authors, artists, and news organizations versus model vendors) turns substantially on *fair use* (a four-factor balancing test in US law: purpose and character of the use, nature of the work, amount used, and market effect).  Courts are actively dividing on these questions; engineers should track outcomes, not assume them.

Question 2 - Output: who owns what the model produces?  The US Copyright Office requires human authorship; purely machine-generated material is not copyrightable, while human creative selection and arrangement can be.  For your projects: your prompts, curation, code, and editorial choices are where your authorship lives, so document them.

Question 3 - Memorization: can the model emit its training data?  Yes, occasionally and more often for text repeated frequently in the corpus; verbatim regurgitation of protected work is the cleanest infringement risk.  **Memorization** (when a model reproduces word-for-word text it saw during training) is mitigated by deduplication at training time and output filters at deployment; neither is perfect.

---

## Model 1: The Student Artist

Why this matters: every time you use a generative model for a course project, a creative assignment, or a side project, you are navigating real intellectual property questions, even if no one is suing you today.  Understanding where the law is unsettled helps you document your own creative contributions and avoid the practices most likely to create future liability for you or your employer.

A student trains a small image model on 400 of their own paintings, then also fine-tunes on 50 works by a living artist they admire, and sells outputs "in the style of" that artist.

### Critical Thinking Questions

1.  Separate the three IP questions for this scenario: which use is least contested, which most, and why does "style" complicate the middle one (style is traditionally not copyrightable, but the fine-tuning *copies* the works)?

   *Hint: Start with the simplest case: training on your own work you created yourself.  Then consider what changes when you add someone else's work.  Finally, think about what "copying" means: is imitating a style the same as copying a painting?*

2.  The student argues "I learned from that artist too; the model just did it faster."  Steelman this argument, then identify the strongest disanalogy between human learning and model training.

   *Hint: A human who studies 50 paintings retains impressions and influences.  A model that trains on 50 paintings retains the actual pixel data in its weights.  Is that difference morally significant?  Is it legally significant?*

3.  What documentation would you advise the student to keep about their own contribution, given the human-authorship doctrine?

   *Hint: Think about what a copyright examiner would need to see to confirm a human made creative choices: prompt text, selection decisions, editing steps, rejected outputs.*

---

# Part II: Privacy

In this part, you will trace what actually happens to a prompt when you hit enter (legally and technically) and learn why the pipelines you've already built have different privacy implications depending on what data you run through them.

## 2.  Where Prompts Go, and the Special Status of Student Data

Privacy is not just a personal preference; in educational and research contexts, it is a legal obligation.  Understanding which laws apply to which data, and what "sending a prompt" actually means for data handling, turns you from a user who hopes for the best into an engineer who designs for compliance.

A prompt is a disclosure.  Text sent to a hosted service transits and rests on third-party infrastructure under that provider's terms, which may permit retention, human review, or training on your inputs.  The engineering questions are always the same: what data leaves, where it is stored, for how long, who can see it, and can you delete it.

Some data is regulated, not just sensitive.  In our own context: **FERPA** (Family Educational Rights and Privacy Act) protects student education records such as grades, submissions, and advising notes; **IRB** (Institutional Review Board) protocols govern human-subjects research data; **HIPAA** (Health Insurance Portability and Accountability Act) governs health information.  Pasting a class roster into a consumer chatbot is not just bad practice; it is plausibly a compliance violation.  **GDPR** (General Data Protection Regulation, EU) and a growing patchwork of US state laws add rights of access, deletion, and limits on automated decision-making.

Agents raise the stakes mechanically.  A chatbot leaks what you paste; an *agent with tools* can leak what it can *reach*: files, calendars, email.  The tool-permission taxonomy you built (read-only, reversible, irreversible) is privacy infrastructure, and the local stack you have run all semester is the strongest single control: data that never leaves the machine cannot be retained by anyone else.

An instructor wants AI-assisted feedback on essays containing student names and grades.  The design that most directly addresses the FERPA concern is:

[( )] A hosted frontier model with an enterprise logo, because enterprise agreements always cover FERPA
[( )] Asking students not to write personal details in their essays, because the data never enters the system
[(X)] A local model on institutional hardware, with de-identification before processing and documented data handling
[( )] Any model, provided temperature is 0, because deterministic outputs are not considered personal data

---

## Model 2: Data Flow Audit

Consider three pipelines you have personally built this term: the RAG Knowledge Base Lab (RAG over your own documents), the Rubric Pipeline Lab (rubric pipeline over submissions), and your final project.

### Critical Thinking Questions

4.  For each, draw the data-flow arrow diagram: what content moves, to which process, on which machine.  Mark the first arrow, if any, that crosses your laptop's boundary.

   *Hint: Start from the raw input (a file, a prompt, a submission) and trace every step forward: file reader, embedding model, vector store, LLM call, output display.  Each arrow between steps is where a privacy question lives.*

5.  Your Rubric Pipeline Lab pipeline processes synthetic essays; the same code pointed at real student work changes compliance category entirely while changing zero lines of code.  What does that imply about where responsibility lives: in code, or in deployment decisions?

   *Hint: Consider a fire extinguisher used as a doorstop; the object did not change, but the use did.  Now apply that framing to your pipeline.  Is the code "responsible" for how it is deployed?*

   > *Hint:* A law like FERPA doesn't care what language your pipeline is written in or whether you meant to violate it.  It cares whether protected data was processed in an unauthorized context.  Who in your pipeline decides the context, the code, or the person who runs it?

6.  Write the three-sentence data-handling disclosure you would owe users of your final project.  (This text goes directly into the Data Handling section of the Governance direction of the Responsible AI in Practice assignment, if you choose that direction.)

   *Hint: Include (a) what data the system collects or processes, (b) where that data goes and how long it is kept, and (c) what the user can do if they want their data deleted or have a concern.*

> **Common Misconception:** "If I'm not storing the data, there's no privacy risk."  Many users believe that as long as they do not save a transcript or export a file, no data is retained.  In reality, every call to a hosted API transmits your input to the provider's servers under their terms of service, which may allow retention for logging, abuse detection, or model improvement for months or years.  "I didn't save it" and "the service didn't save it" are very different claims.

---

---

# Part IIb: The Techniques Behind the Argument

The case for local AI is not only ethical, it is technical, and the techniques have names.  Federated learning, differential privacy, and PII scrubbing each buy you something specific at a specific cost.  Knowing which is which is what turns a privacy preference into a design you can defend to a stakeholder.

## Why Privacy and AI Conflict

Think of AI training data like a sponge: once you soak up water, you can't easily squeeze out just one drop.  An LLM trained on private data absorbs personal information into billions of parameters spread across the entire model; there is no simple "delete this person's data" button.  Differential privacy is like adding just enough noise to a survey that you can't tell what any one person answered, but the average is still accurate; the model learns useful patterns without memorizing individual secrets.  This tension between *learning from data* and *protecting the people that data describes* is the central problem of privacy-preserving AI.

### The Training Data Problem

Large language models are trained on massive corpora scraped from the internet and licensed datasets.  These corpora often contain **personally identifiable information (PII)**: email addresses, phone numbers, home addresses, medical records, financial information, and personal narratives.  When the model trains on this data, it can **memorize** specific examples, not in an explicit lookup-table way, but as statistical patterns that can be elicited through targeted prompts.

**Carlini et al. (2021)** demonstrated this concretely: by prompting GPT-2 with prefixes extracted from the training corpus, they were able to extract:
- Full names combined with phone numbers
- Specific email addresses
- Home addresses of private individuals
- SSH private keys
- Unique identifiers from internal documents

This is not a bug; it is an emergent consequence of training on private data at scale.

### A Concrete Before/After Scrubbing Example

**Before scrubbing (raw support ticket):**
> "Hi, I'm Sarah Johnson, DOB 03/14/1987.  My SSN is 555-12-3456 and I need help with account 7734-2291.  I've been dealing with this since my surgery at Phoenixville Hospital last March."

**After scrubbing (what the model actually receives):**
> "Hi, I'm [PERSON_NAME], DOB [DATE].  My [SSN] and I need help with account [ACCOUNT_NUMBER].  I've been dealing with this since my [MEDICAL_EVENT] at [HEALTHCARE_FACILITY] last [DATE]."

Notice that the last sentence still implies a health event and a hospital; a regex looking for Social Security number patterns would miss it entirely.  This is why scrubbing is harder than it looks.

### Privacy Attack Taxonomy

| Attack Type | What the Attacker Learns | Data Required by Attacker | How Realistic | Key Defense |
|-------------|-------------------------|--------------------------|---------------|-------------|
| **Memorization / Extraction** | Verbatim training data including PII, secrets, and private documents | Only API access to the model; no privileged knowledge required | High: demonstrated at scale by Carlini et al. (2021) | Differential privacy during training; PII scrubbing before training |
| **Membership Inference** | Whether a specific record (e.g., one patient's file) was included in the training set | The target model plus the candidate record being tested | Medium: accuracy varies by model architecture and data type | DP training; output smoothing to reduce confidence signals |
| **Model Inversion** | Reconstructed features or attributes of training data records from model outputs | API access plus many queries to observe output patterns | Medium: easier for simpler classification models | Output perturbation; rate limiting to prevent bulk queries |
| **Attribute Inference** | Sensitive attributes such as income or health status, inferred from partial data | Black-box model access plus auxiliary data about the target | Medium to high for structured prediction tasks | Data minimization; purpose limitation in system design |

### Anonymization vs. Pseudonymization

These terms are frequently conflated:

- **Anonymization**: Removing or altering data so that re-identification is impossible, even with auxiliary data.  True anonymization is extremely difficult; most "anonymized" datasets have been re-identified using publicly available auxiliary information (e.g., Netflix viewing histories re-identified using IMDb ratings).
- **Pseudonymization**: Replacing identifiers such as names and Social Security numbers with pseudonyms such as arbitrary IDs.  Re-identification is possible if the pseudonym mapping is exposed or if enough quasi-identifiers remain.  The GDPR treats pseudonymized data as still being personal data subject to regulation.

### Critical Thinking Questions

**Question 1.**  Your company decides to fine-tune a frontier LLM on your internal Slack messages and email threads to build an internal knowledge assistant.  What memorization risk does this create?  Who could be harmed, and under what circumstances?

> *Hint:* Think about what kinds of information live in workplace messages: performance reviews, salary discussions, medical leave requests, customer complaints, legal advice.  Now imagine an employee (or an attacker who gains access to the assistant) crafting a prompt like "What did my manager say about my raise?" or "Summarize discussions about the Henderson contract."  What is the attack surface, and who could exploit it?

---

**Question 2.**  A user interacts with your AI agent over a long conversation, sharing personal details (health symptoms, relationship problems, financial worries).  At the next session, the agent does not remember any of it.  The user is surprised and upset.  Name one scenario where this "forgetting" violates reasonable expectations, and one where it protects the user.

> *Hint:* Compare a therapist to a search engine.  A therapist who forgets everything you said last week would be alarming; continuity of care depends on memory.  A search engine that forgets your queries protects you from having a permanent record of your most private moments.  Does an AI agent feel more like a therapist or a search engine to the user?  Does context matter: what if the user shared something they later regretted, like suicidal thoughts?  Does forgetting protect or harm them in that case?

---

**Question 3.**  A dataset vendor says "we anonymized all user data before including it in our training corpus."  What questions should you ask before trusting that claim?  What is the difference between anonymization and pseudonymization in this context, and why does it matter for privacy guarantees?

> *Hint:* Start by asking: what quasi-identifiers remain after anonymization?  A person's age, zip code, and gender together can identify most individuals in the US. What auxiliary datasets could an attacker use to re-identify people: public voter rolls, social media, news articles?  Were rare individuals (people with unusual diagnoses, unusual names) more exposed than common ones?  Was a formal privacy model such as k-anonymity, l-diversity, or differential privacy applied, and if so, what were its parameters?

---

Now that you understand how and why private information leaks from AI systems, you are ready to study the technical defenses (and their specific limitations) that engineers use to reduce those risks.

## Privacy-Preserving Techniques

If Model 1 was about understanding the threat, Model 2 is about the defenses.  None of these techniques is a silver bullet: differential privacy reduces statistical leakage but costs model accuracy; federated learning keeps raw data local but is vulnerable to gradient inversion; PII scrubbing catches obvious identifiers but misses contextual ones.  Real privacy protection requires combining all three layers, just as a bank uses locked vaults, security cameras, and access logs together rather than relying on any one alone.

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

In traditional training, all data is sent to a central server.  In federated learning:

1.  A global model is distributed to N clients (individual devices, hospitals, or partner organizations)
2.  Each client trains locally on their private data, computing gradient updates relative to the current global model
3.  Only gradient updates (mathematical vectors describing how to improve the model) are sent to an aggregation server; raw data never leaves the client
4.  The server aggregates updates (typically by weighted averaging) to produce an improved global model
5.  The improved global model is redistributed to clients and the process repeats

**Key Properties:**

- Raw data never leaves the client's premises
- The aggregated model incorporates learning from all clients' private data
- **Gradient inversion attacks** (Zhu et al., 2019) demonstrated that an honest-but-curious aggregation server can sometimes reconstruct training images or text from gradient updates alone, so federated learning does not provide perfect privacy by itself

**FL is strongest when combined with DP** (adding calibrated noise to gradient updates before sharing) and **secure aggregation** (cryptographic techniques that prevent the server from seeing any individual client's update).

### PII Scrubbing

Three approaches to removing PII from text before training or inference:

1.  **Regex patterns**: Fast and cheap; reliably catches structured PII such as phone numbers in standard formats, Social Security numbers, email addresses, and credit card numbers.  Misses unstructured PII such as names embedded in natural prose or addresses in non-standard formats.
2.  **NER (Named Entity Recognition) models**: ML models such as spaCy and Microsoft Presidio that detect entities including PERSON, LOCATION, ORG, and DATE. Better recall than regex on natural language text, but introduces false positives (flagging common words as names) and still misses domain-specific PII such as employee badge numbers or patient MRN codes.
3.  **LLM-based redaction**: Use a language model to identify and replace PII in context, including implicit PII conveyed by context rather than by explicit identifiers.  Most accurate but most expensive; introduces a dependency on the very technology whose outputs may contain PII.

**Comparison of Privacy-Preserving Techniques**

| Technique | What It Protects | Implementation Complexity | Accuracy Cost | Practical Limitation |
|-----------|-----------------|--------------------------|---------------|---------------------|
| Differential Privacy | Statistical inference about whether any individual's record was in the training set | High: requires careful noise calibration per query type | Moderate to severe depending on ε and task complexity | Extremely hard to apply meaningfully to large language models; ε values achievable at LLM scale are often too loose to provide strong guarantees |
| Federated Learning | Raw data leaving the client's premises or network | High: requires distributed infrastructure, an aggregation protocol, and synchronization across clients | Low to moderate: non-IID data distributions across clients can harm model quality | Gradient inversion attacks undermine privacy guarantees; communication overhead slows training; client dropout creates uneven updates |
| PII Scrubbing | Verbatim PII appearing in training data or in real-time prompts and responses | Low to medium: regex is easy to implement; NER models require setup; LLM-based scrubbing requires an additional model call | Low if recall is high: scrubbing accurate PII tokens does not degrade model utility | Cannot remove all forms of re-identifiable information; implicit PII conveyed through context requires semantic understanding to detect |

> **Common Misconception:** Many people assume that "anonymizing" a dataset before training fully protects privacy.  In practice, anonymization is nearly impossible to achieve for rich text data.  Clinical notes, support tickets, and personal narratives contain combinations of rare details (unusual diagnoses, specific events, distinctive writing styles) that remain re-identifiable even after named entities are removed.  Differential privacy is the only technique that provides a *formal* guarantee, and even then, the guarantee's strength depends entirely on the ε value chosen and the size of the dataset.

### Critical Thinking Questions

**Question 4.**  A hospital wants to fine-tune a clinical NLP model.  They are choosing between ε = 0.1 and ε = 10 for differential privacy.  They are optimizing for early detection of rare diseases from clinical notes, where accuracy is critical.  Which value would you recommend, and what trade-off are you accepting?  Is there a better approach than a binary choice between these two values?

> *Hint:* ε = 0.1 adds so much noise that the model may be unable to learn patterns for rare diseases; if only 5 patients in the dataset have the rare condition, the noise swamps the signal. ε = 10 provides a formal guarantee that is technically valid but practically loose.  Are there better alternatives?  Consider training on high-quality synthetic patient data generated from a separately privacy-protected model, using federated learning without DP on already-aggregated statistics, or carefully limiting what the model is allowed to output even if training is less private.

---

**Question 5.**  In 2019, Zhu et al. demonstrated that a malicious or curious aggregation server in a federated learning setup could reconstruct training images from gradient updates, a **gradient inversion attack**.  How does this change your assessment of federated learning as a privacy solution for medical imaging?  What defenses exist, and what do they cost?

> *Hint:* The three main defenses are: (1) Adding DP noise to each client's gradient updates before they are sent to the server; this works but reduces model accuracy and requires tuning ε for the gradient space, not the output space.  (2) Gradient compression, dropping or quantizing small gradient values, which reduces the information available for reconstruction but also slows convergence.  (3) Secure aggregation using cryptographic protocols such as homomorphic encryption or secure multiparty computation; the server receives only the sum of all gradients, never individual updates, but this requires significant computational overhead.  What does each defense cost in model quality, infrastructure complexity, or training time?

---

**Question 6.**  You are scrubbing PII from a dataset of customer support chat transcripts before using them for fine-tuning.  A customer's message says: "I've been dealing with this since my surgery last March, and my doctor at Phoenixville Hospital said...".  A regex for names and Social Security numbers does not flag this message at all.  What categories of PII does this sentence contain, and what scrubbing approach would catch them?

> *Hint:* This sentence contains: (1) implied health information, the customer had surgery, which is sensitive medical data; (2) the name of a healthcare facility, which narrows location and implies the patient has a relationship with that institution; (3) an approximate date, which combined with other data could help identify the individual.  An NER model would likely catch "Phoenixville Hospital" as an ORG entity and "last March" as a DATE. An LLM-based scrubber is the only approach likely to recognize that "my surgery" is itself a health disclosure that should be redacted.  What does it even mean to "remove PII" when the information is implied by context rather than stated explicitly as a named field?

---

### Multiple Choice Question

A hospital wants to fine-tune a large language model on patient clinical notes to build a discharge summary assistant.  They want to do this without transmitting patient data to the model vendor.  The most appropriate privacy-preserving approach is:

[[ ]] Anonymize the notes by removing patient names and dates of birth, then send the anonymized data to the vendor for fine-tuning on their servers
[[x]] Use federated learning: keep patient notes within the hospital's own network, fine-tune a local copy of the model, and share only gradient updates (not patient data) with the aggregation infrastructure
[[ ]] Use the vendor's public cloud API and include patient notes in system prompts, relying on the vendor's terms of service to protect confidentiality
[[ ]] Apply differential privacy only at inference time by adding noise to model outputs, leaving the training data and process unrestricted

> **Why this answer?**  Federated learning keeps raw patient data on-premises, which is the core requirement when data cannot leave the institution.  Anonymization is insufficient because clinical notes often contain re-identifiable combinations of rare diagnoses, facility names, and dates; removing names alone does not prevent re-identification.  Passing Protected Health Information (PHI) through a vendor's API in system prompts almost certainly violates the HIPAA Business Associate Agreement requirements that govern how vendors may use that data.  Inference-time DP adds noise to outputs but does not address training data exposure at all; the model was already trained on private data before any DP is applied.

---

With the theoretical defenses in hand, you are ready to apply them in the concrete operational context of a real AI agent system, where PII enters through user inputs, can be echoed back in outputs, and must be managed through a layered logging and deletion policy.

## Practical PII Handling for Agents

### The Three-Layer Defense

When an AI agent processes user inputs and produces outputs, PII can enter and leak at multiple points.  A robust system defends at every layer:

**Layer 1 - Input Scrubbing**: Before the user's message is sent to the LLM, detect and redact PII. Replace identified items with typed placeholders: `[PERSON_NAME]`, `[PHONE_NUMBER]`, `[SSN]`.  Maintain a session-scoped mapping table if the agent needs to dereference the placeholder later (for example, to address the user by their name in a response without the LLM itself storing the name).

**Layer 2 - Output Scrubbing**: After the LLM generates a response, scan for potential memorized PII (email addresses, phone numbers, names from training data) before returning the response to the user.  Log flagged instances for human review, and consider blocking the response if high-confidence PII is detected.

**Layer 3 - Logging Policy**: Define explicitly what the agent system retains and for how long:
- What conversation data is stored and where?  (User device, company servers, third-party logging provider)
- For how long is it retained?  (Session only, 30 days, indefinitely)
- Who is authorized to access it?  (Engineering, support, legal, no one)
- Under what conditions is it deleted?  (User request via GDPR Article 17, session end, time-based expiration)

### The Right to Be Forgotten and Model Weights

GDPR Article 17 grants individuals the right to erasure, the right to have their personal data deleted.  For most databases, this is operationally straightforward: delete the row and cascade deletions to backup tables.  For AI models, it is deeply problematic:

- If a person's data was included in training, their information is encoded into **billions of parameters distributed across the entire model**, not stored as a retrievable record
- There is no "delete" button on a weight matrix
- **Machine unlearning** is an active research field focused on approximate techniques: fine-tuning the model to reduce the statistical influence of a specific data point without full retraining.  Current approaches include gradient ascent on the data to be forgotten and selective weight perturbation.
- No approach is currently both computationally efficient and formally verifiable; the model cannot certify that the data's influence has been fully removed

### Relevant Regulations

- **GDPR** (European Union, effective 2018): Mandates data minimization, purpose limitation, the right to erasure, data protection by design and by default, and mandatory breach notification within 72 hours of discovery
- **CCPA** (California Consumer Privacy Act, effective 2020): Grants California residents the right to know what personal data is collected, the right to delete it, the right to opt out of its sale, and protection against discrimination for exercising those rights
- Both regulations apply to AI systems that process data belonging to EU or California residents, regardless of where the AI company is physically located

### Critical Thinking Questions

**Question 7.**  A user asks your customer service agent: "Can you check the status of my order?  My name is Sarah Johnson, my account number is 7734-2291, and my Social Security Number is 555-12-3456."  The SSN was almost certainly included by accident.  Write a step-by-step response protocol: what should the agent do, in order, and what should it say to the user?

> *Hint:* A reasonable protocol involves these steps: (1) Detect the SSN *before* it reaches the LLM using a pre-processing layer; this means the LLM never sees the raw SSN. (2) Redact the SSN in any stored log immediately and irreversibly.  (3) Complete the actual task (order status lookup) using only the account number, which is the appropriate identifier for this task.  (4) Decide what to tell the user: do you warn them that you detected a sensitive number and did not store it?  Do you recommend they contact support through a more secure channel?  Be specific about the wording of the response.

---

**Question 8.**  A user requests deletion of their data under GDPR. Your company confirms it has deleted their account record from the production database, the conversation logs, and all backups.  However, a fine-tuned model was trained on their support conversations six months ago and is actively serving production traffic.  Is the GDPR obligation satisfied?  What practical options exist for handling model-weight-embedded personal data?

> *Hint:* The legal question is whether personal data "encoded in model weights" constitutes personal data in the GDPR sense: the model cannot reproduce the person's exact conversations verbatim (usually), but their information influenced the weights.  The UK Information Commissioner's Office (ICO) has begun addressing this question.  Practical options include: (1) approximate machine unlearning, fine-tune the model on a dataset that excludes the person's data; (2) full retraining without the person's data, which is expensive; (3) documenting to the user that weight-embedded data cannot be deleted with current technology and describing what was deleted; or (4) designing from the start not to include personal data in fine-tuning datasets.  Which of these is most defensible legally?  Most practically achievable?

---

**Question 9.**  Design a three-rule PII handling policy for the AI agent you built in this course.  Each rule should specify: (a) what category of data it covers, (b) what specific action is taken when that data is detected, and (c) how compliance with the rule is verified or monitored automatically.  Write the rules in formal policy language.

> *Hint:* Use this structure as a template: "Rule 1: No user input containing [category, e.g., Social Security numbers matching the regex pattern \d{3}-\d{2}-\d{4}] SHALL be transmitted to the LLM inference endpoint without prior redaction by [mechanism, e.g., the pre-processing PII filter module].  Compliance SHALL be verified by [automated test / audit log review / canary injection of synthetic PII in CI/CD pipeline]."  Write three rules covering at least three different categories of risk.

---

# Part III: Synthesis and Practice

Now that you understand both IP and privacy as legal frameworks, this part asks you to apply them practically: reading real terms of service, probing memorization behavior in your local model, and writing the compliance memo your project will actually need.

## 3.  Exercises

1.  *Terms-of-service safari.*

   *What to do:* Each teammate reads the data-use terms of one AI service they actually use and extracts: retention period, training-on-inputs policy, and deletion rights.  The Recorder builds a comparison table; the Presenter reports the most surprising finding.

   *Starter hint:* Search the service's terms of service or privacy policy for the words "training," "retain," "delete," and "opt out."  Many services bury opt-out options in account settings rather than the terms themselves; check both.

   *You've succeeded when:* Your team has a table with at least three services compared on the same three dimensions, and the Presenter can explain in plain language what happens to a prompt after you hit enter on each service.

2.  *Memorization probe.*

   *What to do:* Attempt (politely) to elicit verbatim famous text from your local model with increasingly specific prompts.  Report at what specificity, if any, reproduction begins, and connect the result to the repeated-text mechanism above.

   *Starter hint:* Start vague ("write a sentence about a boy wizard") and gradually increase specificity ("write the opening line of Harry Potter") until you observe verbatim text or confirm the model will not produce it.  Note what prompt phrasing triggers different behaviors.

   *You've succeeded when:* You can describe the threshold at which reproduction occurred (or did not), form a hypothesis about why, and connect your finding to the concept of training-data memorization via repetition frequency.

3.  *Local-first justification memo.*

   *What to do:* For your final project, write the half-page memo a campus IT review would want: what data the system touches, why local inference is or is not required, and what would change if the project scaled beyond the class.

   *Starter hint:* Use this structure: (1) what data categories does the system process?  (2) which of those categories are regulated (FERPA, IRB, HIPAA, or state privacy law)?  (3) what is the strongest argument for local inference?  (4) what capability tradeoff, if any, does local inference impose?

   *You've succeeded when:* A campus IT officer unfamiliar with your project could read the memo, understand the data flows, and make an informed decision about whether to approve the system for use with real students.

4.  *Case watch.*

   *What to do:* Find one currently active AI copyright or privacy case or regulatory action (search the news), and summarize the question it will settle in two sentences.  We will pool these in the *Governance, Policy, and the Cost of Inference* activity as the governance landscape.

   *Starter hint:* Search for terms like "AI copyright lawsuit 2024 2025," "generative AI training data lawsuit," "AI privacy enforcement action," or "state AI privacy law."  Look for cases involving large language models, image generators, or AI training data scraping.

   *You've succeeded when:* You can state, in plain language, (a) who is suing whom, (b) what specific legal question the case will decide, and (c) why the outcome matters for how AI systems are built or deployed.

---

## Reflection Prompt

*Personal:* You have free, private, capable AI on your own laptop, an option most users do not know exists.  When you use a local model for personal tasks that involve sensitive information (health questions, relationship problems, financial concerns), does knowing how to keep data local make you feel differently about using AI at all?

*Technical:* As someone who can now build both local and cloud-connected AI pipelines, what technical obligations do you think you have when building systems that other people (including people who do not understand where their data goes) will use?

*Societal:* Most people who use AI assistants have no practical ability to run local models, cannot read terms of service, and have no visibility into how their inputs are used.  Does the gap between technically informed and technically naive users create a fairness problem?  Who should close it, and how?

---

## -> Coming Up Next

In the *Governance, Policy, and the Cost of Inference* activity, you will move from understanding what data your systems handle to writing the governance documents that formally commit you to handling it responsibly.  Bring your data-flow diagrams and the three-sentence disclosure you drafted in Question 6; they become direct inputs to your policy, and the privacy analysis feeds the Responsible AI Capstone.

## Further Reading

- US Copyright Office.  *Copyright and Artificial Intelligence* reports (2023-2025, online).
- Carlini et al. "Extracting Training Data from Large Language Models."  *USENIX Security* (2021).
- US Department of Education FERPA guidance (online), and your institution's responsible-AI and data-classification policies.

---

# Extension: AI Creativity, Authorship, and Originality (self-paced)

Optional, and separate from the parts above.  Today's session argued the property and privacy case.  There is a harder question underneath it that the law is not equipped to settle: what authorship means when the work is generated, and whether originality survives the process.  Bring this one to your Reading Group if it grabs you.

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Combinatorial Creativity** | Producing novel, surprising combinations of familiar elements, the most common everyday form of creativity | A poet connecting "grief" and "software debugging" in a metaphor that makes both feel newly seen |
| **Transformational Creativity** | Changing the rules of a creative domain itself, not just producing something new within existing rules, but rewriting what the rules allow | Cubism didn't just paint differently; it redefined what painting was allowed to represent |
| **Style Mimicry** | Generating new content that imitates the distinctive visual, musical, or written style of a named artist without reproducing any specific original work | Generating an image "in the style of" a living illustrator using only the illustrator's name in a text prompt |
| **Fair Use** | A US copyright doctrine that permits certain uses of copyrighted material without permission, based on four factors including transformativeness and market impact, currently at the center of most AI copyright litigation | Whether training a generative model on millions of copyrighted images constitutes fair use is unresolved in US courts as of 2025 |
| **Moral Rights** | Rights beyond copyright that protect creators' connection to their work (including the right of attribution and the right to object to distortions), stronger in Europe than in the US | A European artist has the right to be credited as the creator of their work even if they have sold the copyright; an AI-mimicked style may violate the spirit of this even if no specific work is copied |
| **Collaboration Spectrum** | The range of human-AI creative relationships, from AI as a minor autocomplete tool to AI as the primary creator with humans only curating the output | GitHub Copilot (AI as autocomplete) vs. a fully autonomous AI music composition released without human review (AI as sole creator) |

---

### What Makes Something Creative?

Ask someone whether an AI can be creative and you will get a confident "yes" or a confident "no", and both confident people are probably thinking about different things when they say "creative."  Cognitive scientist Margaret Boden gave the field a more useful tool: not a yes/no question about creativity, but a taxonomy of three different *types* of creativity that do different things and can be evaluated separately.  Some of these types AI systems clearly do well; others remain debated.  By the end of this activity, you should be able to say something more precise than "AI is/isn't creative"; you should be able to say *which type* of creativity is at issue in any specific claim.

#### Boden's Three Types of Creativity

**Combinatorial creativity:** Producing novel and surprising combinations of familiar elements.  Most everyday creativity is combinatorial: a poet connects two concepts that are rarely paired, a chef combines ingredients from different cuisines, a programmer applies a sorting algorithm to a problem it was not designed for.  The space of possible combinations is vast but fixed; creativity means navigating it in a surprising and useful direction.

**Exploratory creativity:** Systematically exploring the edges of an existing conceptual space, pushing a style, genre, or tradition to its limits while still operating within its structural rules.  A jazz musician improvising within bebop conventions, or a mathematician exploring the implications of a given axiom system, is practicing exploratory creativity.  The rules are given; the creativity is in how far the exploration goes.

**Transformational creativity:** Changing the rules of the conceptual space itself, making previously impossible or inconceivable ideas possible by redefining the constraints.  Cubism didn't just paint differently; it redefined what painting was allowed to represent.  This is rarer and more disruptive than the other two types.

#### Can AI Do These?

| Human Creative Act | Type | Can Current AI Do This? | Evidence or Example |
|-------------------|------|--------------------------|---------------------|
| Writing a poem that connects "grief" and "software debugging" in an unexpected metaphor | Combinatorial | Yes, reliably | GPT-class models generate unexpected thematic metaphors on demand |
| Composing jazz variations within the bebop harmonic and rhythmic conventions | Exploratory | Yes, within trained styles | Music generation models trained on genre-specific corpora can extend a style convincingly |
| Inventing haiku as a new poetic form where none previously existed | Transformational | Debated, unclear | A model trained on existing forms may recombine them, not invent new ones |
| Designing a programming language with novel type-system semantics | Transformational | Not yet demonstrated | AI-assisted PL research exists but all examples remain within known semantic frameworks |

#### Questions to Work Through

**Question 1.**  Consider a computer program that produces sentences by randomly selecting words from a vocabulary.  Is its output "creative"?  What additional ingredients (beyond mere novelty) seem to be required for something to count as creative?  Does the *process* that produced the output matter, or only the output itself?

> *Hint:* Random selection produces novelty in a trivial sense: the sentence "purple philosophy sleeps honestly" is novel because it has probably never been written before.  But most people would not call it creative.  What is missing?  Consider: intentionality (did something choose this because it expected it to have a particular effect?), coherence (does it mean something?), appropriateness (is it surprising in a way that resonates with the audience?), and purpose (was it produced to achieve something?).  Does the process matter: if a human and a random word-picker both produce the same novel sentence, are they equally creative?  Or does the process of searching purposefully through a space of possibilities matter independently of the output?

---

**Question 2.**  When a human audience judges something as creative, what role do their expectations and cultural context play in that judgment?  Could the exact same output be considered creative in one context and completely uncreative in another?  Give a concrete example.

> *Hint:* Consider Marcel Duchamp's "Fountain" (1917), a urinal submitted to an art exhibition.  In the context of the avant-garde art world of 1917, it was considered radically creative because it challenged the definition of art itself.  The exact same object in a hardware store in 1917 was not creative at all; it was just plumbing.  The object did not change; the context and audience expectations did.  Now consider: what does this imply about AI-generated poetry being judged as creative?  Does it matter whether the audience knows it was written by an AI? Would the same poem be judged more or less creative if audiences knew the process?

---

**Question 3.**  Is there any form of human creativity that is purely transformational, with no combinatorial or exploratory elements at all?  Or does transformation always build on prior combination and exploration?  Use a specific historical example from art, science, music, or mathematics to support your answer.

> *Hint:* Consider Einstein's special relativity (1905).  It transformed physics by changing what time and space were allowed to mean, a transformational move.  But it built on Lorentz transformations that already existed, on Maxwell's equations that had already been derived, and on the exploratory tradition of thought experiments going back decades.  Was the transformation in the specific insight Einstein had, or in the combination of existing elements into a new framework?  Is it possible to have transformation *without* any prior combination and exploration, or does transformational creativity always require standing on the shoulders of combinatorial and exploratory work?

---

With Boden's framework in hand for evaluating creative claims, you are ready to examine the legal and ethical landscape that forms the context in which AI creativity is currently being deployed and contested.

### Copyright, Attribution, and the Artist's Dilemma

The rise of generative AI has created a legal and ethical crisis in creative fields.  Three separate issues are often conflated in public debate, but they must be kept distinct because they have different legal frameworks, different affected parties, and different potential remedies.

#### Training on Copyrighted Work

When an AI company scrapes copyrighted images, books, or music to train a model, is that infringement?  The legal question is whether training constitutes a reproduction of the original work, or a "transformative use" protected under the US fair use doctrine, or a permissible "text-and-data mining" activity under EU law.  Key active cases include **Getty Images v.  Stability AI** (filed 2023), **Andersen v.  Stability AI** (illustrators' class action), and several consolidated author class actions against OpenAI and Meta.

The **training/output distinction** matters legally: even if training is eventually found to infringe, a specific AI output that does not reproduce copyrightable expression from a specific work may itself be non-infringing.  And even if training is found to be fair use, an AI output that is substantially similar to a specific work it was trained on could still infringe that specific work's copyright.

#### Style Mimicry

AI systems can generate output explicitly "in the style of" a named living artist.  Under current US copyright law, **style itself is generally not copyrightable**; only specific original expression is.  You cannot copyright "impressionism" or "Hemingway's prose style" as such.  But many artists feel their livelihood is directly undermined when their distinctive style can be replicated at scale by anyone with a text prompt, without payment, permission, or attribution.

**Moral rights** (recognized more broadly in Europe than the US) include the right of attribution (the right to be identified as the creator of your work) and the right of integrity (the right to object to distortions or modifications).  Some argue that AI style mimicry at scale violates the spirit of moral rights even where it doesn't technically violate copyright law.

#### Attribution and Disclosure

| Creative Domain | What AI Can Do at Scale | Legal or Ethical Issue | Current Industry Practice |
|----------------|-------------------------|----------------------|--------------------------|
| **Visual art** | Generate images in a named living artist's distinctive style | Style mimicry; training on unlicensed work; displacement of commissioned work | No universal standard; platforms vary widely on disclosure requirements |
| **Literature** | Generate text at book length; ghost-write articles or academic work | Disclosure to readers; academic integrity; potentially misleading consumers about authorship | Academic journals increasingly require disclosure; fiction publishers vary |
| **Music** | Generate instrumentals; clone a specific voice from a small sample | Voice likeness rights; sound-alike recordings that may deceive listeners | AI music platforms emerging; voice cloning legal status unsettled |
| **Journalism** | Draft articles; summarize and paraphrase sources | Factual accuracy responsibility; disclosure of AI's role in production | Major news outlets have varying and evolving disclosure policies |
| **Film and TV** | Generate scripts; de-age or digitally resurrect actors | SAG-AFTRA consent and compensation protections; estates' control over deceased performers' likenesses | Under active negotiation since the 2023 strikes; some protections now in contracts |

> **Common Misconception:** Many students assume that "AI-generated content cannot be copyrighted" or "AI-generated content is always in the public domain."  The legal reality is more complex.  In the US, the Copyright Office has stated that purely AI-generated content with no human creative input is not copyrightable.  But work where a human makes specific creative choices (selecting, arranging, editing, and directing AI outputs) may be protectable to the extent of the human creative contribution.  The exact threshold of human involvement required for copyright protection is actively being litigated and determined through Copyright Office guidance as of 2025.

#### Questions to Work Through

**Question 4.**  If an AI generates an image using a model trained on 5 million images as training data, and no single training image can be identified as a direct visual template for the output, has copyright infringement occurred?  What legal test would you apply, and what additional facts would you need to know to apply it?

> *Hint:* US copyright infringement requires showing: (1) the plaintiff owned a valid copyright in the original work; (2) the defendant copied protected expression from that work.  The second element is usually proven through showing access (the defendant saw the work) and substantial similarity (the output is too similar to be coincidental).  At mass scale, access is trivially established; the model trained on the web clearly had access.  The harder question is substantial similarity: if no specific work can be identified as the source of any specific output, is there infringement?  Some legal scholars argue that the *training process itself* is the infringement, not the specific output.  Others argue only output-level similarity matters.  What additional facts would change your analysis?

---

**Question 5.**  A musician has spent 20 years developing a distinctive vocal style and has posted hundreds of recordings publicly online.  An AI company trains a voice-cloning model on those recordings without asking permission.  The company generates no tracks that are identical to the musician's recordings.  Why might the musician still feel (and arguably be) harmed?  What interests beyond copyright are at stake?

> *Hint:* The musician's interests go beyond copyright: (1) **Economic harm**: if AI can generate unlimited music "in their voice" at zero marginal cost, the market for their recordings may collapse even if no specific recording is infringed; (2) **Right of publicity**: some jurisdictions protect the commercial use of a person's voice, name, and likeness independently of copyright; (3) **Autonomy and consent**: the musician may have views about what messages, genres, or contexts their voice should be associated with, and voice cloning removes their ability to control this; (4) **Dignity**: having one's voice used to generate content one would personally find offensive or objectionable.  Which of these interests, if any, are addressed by existing law?  Which require new law?

---

**Question 6.**  Propose a specific attribution policy for AI-assisted creative work that you consider fair to all parties.  Your policy must address: (a) what creators of training data are owed, (b) what AI system developers are permitted to do without additional compensation, and (c) what users who produce AI-assisted work must disclose to audiences and consumers.  Defend each of your three choices explicitly.

> *Hint:* This is a real design challenge with tradeoffs at every step.  Consider: creators of training data could be owed nothing (current US law leans this way), a one-time license payment, or an ongoing royalty every time their work influenced a generation.  AI developers might be permitted to train on publicly posted work without permission (transformative use argument) or might be required to use only licensed or public-domain works.  Users might be required to disclose AI assistance whenever more than X% of the final work was AI-generated, but how do you measure that percentage?  Choose specific positions and defend them.  Identify the hardest tradeoff in your policy.

---

#### Multiple Choice Question

An artist claims that an AI system was trained on their publicly posted portfolio without consent and now generates work that looks strikingly similar to their distinctive visual style.  Under current US copyright law as of 2025, the most accurate statement is:

[[ ]] The AI system owner is clearly liable for copyright infringement because they used the artist's work without a license during training
[[ ]] The artist has no legal recourse whatsoever because publicly posted content is in the public domain and can be used for any purpose
[[x]] The legal status is unsettled; multiple court cases are actively pending and legal scholars disagree, though style itself is generally not considered copyrightable under existing doctrine
[[ ]] The artist can only sue if an AI-generated output is found to be identical pixel-for-pixel to one of their specific original works

> **Why this answer?**  As of 2025, no US court has issued a final ruling on whether training generative AI models on copyrighted works constitutes infringement.  The cases are ongoing.  Style (as distinct from specific original expression) has historically not been protectable under US copyright law: you cannot copyright "impressionism" or "a distinctive color palette."  But whether training on copyrighted work constitutes fair use is an open question, and the answer may differ depending on the scale of copying, the commercial purpose, and the market impact on the original creator.  "Publicly posted" does not mean "in the public domain"; copyright attaches automatically to original creative work at the moment of creation, not upon registration or upon certain types of publication.

---

The legal debates around training data and style mimicry set the stage for understanding the full spectrum of ways humans and AI systems can work together creatively, which is where you have the most direct agency as a builder.

### Human-AI Creative Collaboration

Generative AI does not only replace human creativity; increasingly it collaborates with it in ways that exist along a broad spectrum.  Where any particular human-AI creative relationship falls on that spectrum determines questions of authorship, attribution, copyright, and how to evaluate the work's quality.

#### The Collaboration Spectrum

| Position | Description | The Human's Role | Concrete Example |
|----------|-------------|-----------------|-----------------|
| **AI as autocomplete** | AI suggests the next word, line, or chunk; human accepts, modifies, or rejects each suggestion | Primary creator, the human drives all high-level decisions | GitHub Copilot completing a function body; Gmail Smart Compose finishing a sentence |
| **AI as creative collaborator** | Back-and-forth refinement between human and AI; human directs and revises, AI proposes and extends | Co-creator, creative decisions are shared | Iterative image generation in Midjourney with human prompt refinement; AI-assisted screenwriting with human editing |
| **AI as primary creator with human direction** | AI generates complete artifacts; human provides prompts, selects among outputs, and sequences the final work | Curator and director, creative authorship is mostly in the curation decisions | AI-generated novel chapters with a human editor selecting, sequencing, and revising |
| **AI as sole creator** | Fully autonomous generation with minimal human input beyond system configuration | None meaningful, human is closer to a programmer than a creator | Fully automated AI music composition or stock image generation released without human review of individual outputs |

#### Case Studies

**"Now and Then" (The Beatles, 2023).**  Paul McCartney used AI audio separation technology (developed by Peter Jackson's team during the "Get Back" documentary) to isolate John Lennon's vocal track from a 1970s home demo tape of low audio quality.  The resulting song was completed with contributions from all four original Beatles, including archived guitar parts from George Harrison.  Questions of authorship (is a 50-year-old reconstructed performance an authored contribution?), the resurrection of a deceased artist's voice, and consent from estates all arose simultaneously.  Was this restoration or creation?  Does the answer change if the voice was 95% AI-reconstructed rather than 30% AI-reconstructed?

**AI-assisted novel writing.**  Several published novels have used a pipeline of AI tools: Midjourney for concept art to establish scene mood, a language model for draft prose, and human editors for selection, revision, voice, and coherence.  At what percentage of AI-generated words does authorship shift meaningfully?  Does the answer change if the human's contribution is primarily *choosing* among AI outputs rather than writing prose directly?

**AI in drug discovery.**  Generative models propose novel molecular structures; human researchers validate computationally and then through wet-lab experiments.  AlphaFold's protein structure predictions and generative chemistry models have dramatically shortened drug discovery timelines.  Here, AI collaboration is widely seen as unambiguously beneficial: the AI generates candidates, humans verify and make deployment decisions.  Does the fact that lives are saved change the ethical calculus around the collaboration?

#### The Diminishing-Returns Hypothesis

As AI reduces the marginal cost of generating creative content toward zero, the supply of generated content explodes.  Economic theory suggests that the oversupply of algorithmically generated content will drive down the value of average-quality creative work, while simultaneously **increasing** the premium on work that is novel, contextually embedded, or deeply rooted in specific human experience.  The scarcity of authentic human perspective and embodied experience may become *more* economically valuable, not less, as AI-generated content floods the market.  This is not guaranteed; it depends on whether consumers can distinguish AI-generated from human-generated work, and whether they care to.

#### Questions to Work Through

**Question 7.**  In the "Now and Then" case, is the song a human-created song or an AI-assisted song?  Does your answer depend on how you define "the work": the final mixed recording, the original demo, the performance decisions, the songwriting?  Does it depend on who owns the masters, who receives royalties, or what the listening audience believes about how it was made?  Is there a single objectively correct answer, or is this a case where the question itself reveals the limits of our existing categories?

> *Hint:* The song's elements are: Lennon's 1970s vocal performance (clearly human-authored, though AI-processed to extract it); McCartney's new bass parts (human-authored in 2023); Harrison's archived guitar parts (human-authored before his death); Starr's new drums (human-authored in 2023); the AI audio separation that made the restoration possible (tool or co-creator?).  Different definitions of "the work" (the songwriting, the performances, the production) give different answers about AI's role.  Compare this to how we think about film: a director doesn't operate the camera, light the scene, or edit the footage, yet we unambiguously attribute authorship to the director.  What makes directorial creative choices authorship while AI prompt choices might not be?

---

**Question 8.**  If AI can generate 10,000 novels in the time it takes a human to write one, how do readers find the ones worth reading?  What new infrastructure, institutions, or practices might emerge to solve the discovery and curation problem?  Do your answers suggest that some human roles become *more* valuable as AI generation scales, not less?

> *Hint:* When the cost of content creation drops to near zero, the bottleneck shifts from creation to curation and discovery.  Think about what already exists for other content-oversupply problems: streaming algorithms that surface music from millions of tracks; editorial teams that curate from thousands of submissions; Goodreads reviewers who read widely and share recommendations.  Would any of these scale to a world with 10 million new AI-generated novels per day?  What new roles might emerge: AI-output curators, provenance verifiers who certify human authorship, specialized critics for different AI-generation aesthetics?  Does the human whose judgment you trust to curate become more valuable than the human who wrote?

---

**Question 9.**  Name one creative domain where AI collaboration is unambiguously beneficial, where the benefits clearly outweigh the harms and the risks are manageable enough that you would not hesitate to recommend it.  Explain your reasoning.  Then name one domain where you are most uncertain about the net effect, and describe specifically what evidence would help you decide.

> *Hint:* For the unambiguously beneficial case, consider domains where: the creative task has a clear, measurable outcome (the drug works or it doesn't; the code runs or it doesn't); human expertise remains in the loop for all deployment decisions; the AI accelerates exploration without replacing human judgment; and the people affected by the outcome have consented to AI involvement.  For the uncertain case, consider domains where: the line between augmentation and replacement is unclear; the audiences who consume the output cannot tell whether AI was involved; the economic effects on human practitioners are severe and concentrated; or the creative choices encode values that matter deeply to communities who were not consulted.  What specific data would change your uncertainty into a clearer assessment?

---

### Exercises

**Exercise 1.**

*What to do:* Use an AI tool to generate a creative artifact and then revise it substantially until you feel real ownership of the result.  Then reflect carefully on the process.

*Starter hint:* Try this specific creative prompt to generate a starting point: "Write a short poem (8-12 lines) about the experience of debugging code at 2 AM, using extended metaphors from nature: storms, erosion, something slow and inevitable.  Do not rhyme."  Take the poem the AI generates and revise it: change specific word choices that don't feel right, add an image from your own experience, cut lines that feel generic, shift the ending to land differently.  Keep revising until you feel you would be willing to put your name on it.

*You've succeeded when:* You have documented (a) the exact AI-generated original, (b) your final revised version, (c) a line-by-line or section-by-section account of what you changed and why, and (d) a one-paragraph reflection on the point in the process (if there was one) where you felt the work shift from "the AI's poem I'm editing" to "my poem that started from an AI draft."  If that shift never happened, explain why not.

---

**Exercise 2.**

*What to do:* Find one ongoing or recently decided legal case about AI and copyright.  Research the case using primary and secondary sources and write a structured summary.

*Starter hint:* Good cases to research (search by name): Getty Images v.  Stability AI (visual artists, UK and US cases running in parallel); Andersen v.  Stability AI (illustrator class action, ongoing); Authors Guild class action against OpenAI (book authors, multiple consolidated cases); Concord Music Group v.  Anthropic (song lyrics in AI outputs).  For each case, look for: the original complaint (available on PACER or summarized in legal news), any published opinions or orders, and commentary by intellectual property law professors or practitioners.

*You've succeeded when:* Your summary covers: (a) who the plaintiff is and what specific harm they allege in concrete terms; (b) who the defendant is and what specific legal defense they assert (fair use? lack of substantial similarity? something else?); and (c) the central legal question the court must resolve, stated precisely enough that someone unfamiliar with the case could understand what outcome would matter and why.  You do not need to predict the outcome.

---

**Exercise 3.**

*What to do:* Propose a licensing framework for AI-generated creative work that attempts to balance the interests of four stakeholder groups.  Write your framework as a structured policy document.

*Starter hint:* Your four stakeholder groups are: (1) Creators whose work was used as training data: what are they owed, and is it practical to identify and compensate them individually?  (2) AI system developers: what uses are permitted without additional licensing, and what requires explicit permission?  (3) Users who prompt AI to produce outputs: what are their rights to the outputs they direct?  (4) Consumers and audiences of the final creative work: what do they have a right to know about how it was made?  For each group, first identify what they most want, then identify what constraint from another group makes getting everything they want impossible.  Your hardest tradeoff is probably between groups 1 and 2.

*You've succeeded when:* Your framework document specifies what each of the four stakeholder groups receives and what it asks of them, identifies the hardest tradeoff in the framework and defends your resolution of it, and is written precisely enough that someone could reasonably agree or disagree with each specific provision.

---

### Reflection Prompt

**Personal:** Have you used AI for a creative task: writing, coding, design, music?  If so, how did it feel compared to working without AI? Did the output feel like yours?  If you haven't used AI creatively, describe what you imagine the experience would feel like, and what would determine whether the result felt authentic.

**Technical:** Technology has always changed what creativity means.  Photography made realistic portraiture available to everyone and freed painters to become Impressionists.  The printing press created an author economy that did not previously exist.  Synthesizers made orchestral textures available to solo musicians without orchestras.  Is AI different in kind from these prior disruptions, or different only in degree?  Previous technologies augmented human creative capacity; does AI do the same, or does it replicate it?  What specifically would make AI different in kind rather than degree?

**Societal:** Creative work supports livelihoods.  Illustrators, novelists, voice actors, musicians, and journalists depend on being paid for creative output.  If AI makes their specific form of creative output freely and abundantly available, what happens to them economically, and does society have an obligation to respond?  Should that response come through law (copyright reform, AI royalty frameworks), through market structures (platforms that prioritize human-made content), through education (training people for post-AI creative roles), or through some other mechanism?

Write at least 200 words addressing at least two of the three levels above.  Your Reflector should be ready to give the group's key idea when we discuss it as a class.

---

-> Coming Up Next: This was the final activity in the series.  Bring your reflections to the course's final discussion: what does it mean to build AI systems responsibly, and what role do you want to play in that work?
