<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-datacards.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-datacards.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Dataset Documentation: Model Cards and Datasheets

An AI system is only as trustworthy as the data it was trained on and the documentation that describes its behavior. Yet for most of the industry's history, models have shipped with no documentation at all — no description of what they can do, what they cannot do, who they were designed for, or what biases they may carry. This activity introduces two foundational documentation frameworks: **Datasheets for Datasets** (Gebru et al., 2018) and **Model Cards** (Mitchell et al., 2019). These frameworks establish what responsible disclosure looks like for the data and models that power AI systems — including the agents you build in this course.

---

## Directions and Group Roles

Work in your POGIL team of four with clearly assigned roles:

- **Manager**: Keeps the group on task and on time; ensures everyone contributes before moving on.
- **Recorder**: Documents the group's answers and posts the final responses to the Class Activity Questions discussion board.
- **Presenter**: Speaks for the group during debrief; articulates areas of genuine disagreement or alternative interpretations.
- **Reflector**: Monitors group process and captures lessons learned for the reflection prompt.

Consider each model and its questions individually before discussing with your group. The goal is to build a shared mental model, not to reach consensus quickly.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|:-----|:------------------------|:------------------------|
| **Datasheet for Datasets** | A standardized documentation template — proposed by Timnit Gebru and colleagues in 2018 — that accompanies a dataset and answers structured questions about where it came from, how it was collected, what it may be used for, and who can access it. Modeled after the technical data sheets that accompany electronic components. | Filling in the "Composition" section forces you to count how many instances are in each demographic category — which is precisely what the 2015 image classifier team failed to do before they discovered their model labeled people with harmful categories. |
| **Model Card** | A standardized documentation template — proposed by Margaret Mitchell and colleagues in 2019 — that accompanies a trained AI model and describes its intended use, performance across subgroups, ethical considerations, and known limitations. Now required by many enterprise procurement policies and published by major AI labs. | The Hermes-3 model card on HuggingFace includes some sections but omits others — identifying those gaps is one of today's exercises. |
| **Provenance** | The documented history of where data came from: who collected it, when, from what sources, with what consent, and through what transformations. Without provenance, you cannot audit a dataset for legal compliance or bias. | A dataset scraped from Reddit in 2019 has provenance — but if the scraping methodology was never recorded, the provenance is incomplete and cannot be used for a regulatory audit. |
| **Sampling Bias** | A systematic error that occurs when the data collection process over-represents some groups and under-represents others, causing a model trained on that data to perform worse on underrepresented groups. | The 2015 image classifier was trained on data scraped from platforms where white users predominated, so darker-skinned faces were underrepresented — leading to harmful misclassifications discovered after public deployment. |
| **Right to Erasure** | A right under GDPR (Article 17) that allows individuals to request that their personal data be deleted from a dataset or system. Technically challenging for AI because it may require removing data from training sets and retraining the model. | If a user whose posts appear in a customer service transcript dataset requests deletion under GDPR, compliance may require retraining the model — a process that can cost tens of thousands of dollars. |
| **Disaggregated Evaluation** | Reporting model performance separately for different demographic subgroups (by age, gender, language, race, etc.) rather than only reporting an overall average. An aggregate accuracy of 92% can hide 65% accuracy for a minority subgroup. | A model card that reports "overall accuracy: 92%" without disaggregation may be hiding the fact that accuracy for non-native English speakers is 71%. |

---

## Model 1: Why Documentation Matters

> **Why this matters:** Think of a datasheet as a nutrition label for AI. You would not serve food at a school cafeteria without knowing the ingredients — especially if students have allergies. Yet for most of the last decade, AI systems were deployed at scale with no equivalent disclosure. The failures that resulted were not random: they were predictable from the training data's properties, but no one looked because no one was required to document those properties.

The most common way AI systems fail in deployment is not because the model made a random error — it is because the model was trained on data that did not represent the deployment context, and no one knew. This failure pattern is called **undocumented dataset risk**: the training data has properties (bias, staleness, skewed provenance, missing consent) that are unknown to the team deploying the model, so they cannot account for those properties in their system design.

| Risk Category | Documented Dataset — What You Can Do | Undocumented Dataset — What Actually Happens |
|:--------------|:--------------------------------------|:---------------------------------------------|
| **Bias** | Known demographics and sampling strategy allow auditors to check for disparate impact before deployment, identify underrepresented groups, and supplement the data or add evaluation tests targeting those groups | Bias is discovered after deployment, often through public user harm; by that time the system may have made thousands of harmful decisions; remediation is costly, slow, and reputationally damaging |
| **Legal** | License, consent, and copyright information is on record; legal review can proceed before launch; the team knows which data can be used commercially and which cannot | Legal exposure is unknown until a lawsuit or regulator inquiry arrives; data may need to be deleted and the model retrained from scratch; fines and takedowns arrive as surprises |
| **Reproducibility** | Dataset version number, collection date, and preprocessing steps are logged; future teams can replicate results, compare against baselines, and detect if the model's behavior has drifted | Results cannot be reproduced; different teams reach different conclusions from "the same" experiment; you cannot tell if a new model version is actually better because you cannot reconstruct the original evaluation conditions |
| **Auditability** | Regulators, courts, and third-party auditors can inspect the data provenance trail and verify that the system was built responsibly; you can demonstrate compliance under the EU AI Act's High Risk conformity assessment | Auditability is impossible without provenance; regulatory penalties increase when you cannot demonstrate due diligence; litigation discovery becomes the first time anyone maps what data went into the system |

**Real failure pattern**: In 2015, a major tech company's image classifier labeled photographs of Black people with animal-related categories. Postmortem analysis revealed the training set underrepresented darker skin tones because the web scrape that created it oversampled images from predominantly white-user platforms. No datasheet existed. No one had documented the sampling strategy, so no one caught the problem during development. The harm was discovered by the public, not the team — and by then, the model had been deployed at scale.

### Critical Thinking Questions

1. The failure pattern above resulted from a sampling bias in the web scraping process. If the team had been required to complete a Datasheet for Datasets before training, at which specific section of the datasheet would the bias have been most likely to surface? Explain what specific question the datasheet would have forced them to ask, and what answer they would have had to honestly provide.

   *Hint:* Look at the Datasheet sections in Model 2. The "Composition" section asks about the distribution of instances across categories. The "Collection Process" section asks about the data source and how it was gathered. Which question, answered honestly, would have exposed the demographic imbalance?

2. The "Legal" row says undocumented datasets create unknown legal exposure. Identify two specific ways a training dataset scraped from the public internet might create legal liability, even if the scraping itself was technically possible under the website's terms of service. Name the specific legal frameworks that govern each type of liability.

   *Hint:* Think separately about (a) the intellectual property rights of the people who created the content being scraped, and (b) the personal information of the people who appear in or wrote that content. What law governs each?

3. A classmate argues: "Our course RAG agent doesn't train a model — it just retrieves documents. So we don't need to document the dataset." Evaluate this argument systematically. Are there documentation obligations for a retrieval corpus that is not used for model training? What harms could arise from an undocumented RAG corpus that are different from, but analogous to, the harms from undocumented training data?

   *Hint:* What if the RAG corpus contains documents that are copyrighted? What if it contains documents that were written in 2018 and are now factually outdated? What if it overrepresents one viewpoint on a contested topic? Would a datasheet for the corpus help you identify any of these problems before deployment?

---

## Model 2: The Datasheet for Datasets Framework

> **Why this matters:** The Datasheet for Datasets framework works like a standardized intake form at a doctor's office — it forces you to ask the same structured questions about every dataset so that nothing important is omitted. Without a template, teams document whatever they happen to think of, which means they consistently skip the questions that are hardest to answer but most important for identifying risk.

Gebru et al. (2018) proposed a standard template for dataset documentation, analogous to datasheets for electronic components. Each datasheet answers a structured set of questions so that anyone who uses the dataset knows what it contains, where it came from, how it was processed, and what it may or may not be used for.

| Section | Core Question to Answer | Why This Section Matters |
|:--------|:------------------------|:-------------------------|
| **Motivation** | Who created the dataset, for what specific purpose, and with whose funding? Is there a particular task or model the dataset was designed to support? | Reveals whether the dataset's original purpose matches your intended use — a dataset created for sentiment analysis may be inappropriate for medical text classification even if both involve text |
| **Composition** | What kinds of instances does the dataset contain (text, images, structured records, audio)? How many total instances? What is the distribution across categories, demographics, labels, or languages? Is any sensitive information (health data, financial records, faces) present? | Forces enumeration of demographic representation, which is precisely what would have caught the 2015 image classifier bias before deployment |
| **Collection Process** | How was the data collected — web scraping, surveys, sensors, human annotation? Over what time period? Were the data subjects aware their data was being collected? Was consent obtained, and if so in what form? | Determines legal exposure and ethical soundness; "publicly visible" does not mean "consented to collection and redistribution" |
| **Preprocessing/Cleaning** | What preprocessing was applied before release — tokenization, deduplication, filtering of offensive content, anonymization? What was removed and why? Is the raw unprocessed data available alongside the processed version? | Without this section, users cannot reconstruct what the data looked like before cleaning, cannot replicate results, and cannot evaluate whether the filtering introduced new biases |
| **Uses** | What tasks is this dataset appropriate for? What tasks should it NOT be used for, and why? Are there potential harms from specific misuses that the creators are aware of? | Provides the "out of scope" warning that enables downstream developers to make informed decisions rather than assuming the dataset is general-purpose |
| **Distribution** | Under what license is the dataset released? Are there export restrictions, consent limitations, or platform terms of service that restrict redistribution? Does distribution comply with applicable privacy law (GDPR, CCPA, HIPAA)? | The most commonly incomplete section — and the one with the largest legal consequences when missing |
| **Maintenance** | Who is responsible for the dataset going forward? How will errors or newly discovered harms be corrected? Will the dataset be updated as the world changes? Is there a mechanism for data subjects to request removal of their data? | Without a maintenance plan, datasets become stale, incorrect, and non-compliant with privacy rights laws like GDPR's right to erasure (Article 17 of the EU's General Data Protection Regulation, which gives EU residents the legal right to demand their personal data be deleted) |

A team publishes a dataset of 50,000 customer service chat transcripts scraped from a public online forum. The transcripts contain real user complaints and agent responses. The team's datasheet includes the file format, total size, and a sample of ten transcripts. Which of the following is the MOST serious omission from their datasheet?

[( )] They did not include information about the compression format and file encoding used — format details are minor technical metadata that do not affect legal or ethical risk
[(X)] They did not document consent, licensing, or whether users of the public forum agreed to have their messages collected and redistributed — the Distribution section is absent, leaving legal and ethical exposure unaddressed
[( )] They did not include a performance benchmark proving this dataset improves model accuracy — dataset documentation is about provenance and fitness, not about proving downstream model improvements
[( )] They omitted the dataset's collection date — while the date matters for staleness, it is far less critical than missing consent and licensing documentation

> **Common Misconception:** Many developers assume that if data is "public" — visible without a login, indexed by search engines — then collecting, storing, and redistributing it is legally and ethically unproblematic. In reality, "publicly visible" is a technical fact about accessibility. "Consent to redistribution" is a legal and ethical fact about what rights the data subject granted. A comment posted on a public forum is visible to anyone who visits, but the person who wrote it did not necessarily consent to having it scraped, stored permanently in a dataset, used to train a commercial AI, or redistributed globally under a CC0 license. The Distribution section of the Datasheet is where this distinction must be addressed.

### Critical Thinking Questions

4. The **Collection Process** section asks whether data subjects were aware their data was being collected. For the customer service transcript dataset above, the posts were publicly visible on a forum. Does "publicly visible" mean "consented to collection and redistribution"? Articulate the precise legal and ethical distinction that matters here, and give one example of a collection scenario that would clearly cross the line from acceptable to unacceptable even on a public platform.

   *Hint:* Consider the difference between someone visiting a public library and reading a book versus photocopying every book in the library and selling the copies commercially. Both involve publicly accessible content — but they are not the same act. What is the analogue for data collection?

5. The **Uses** section asks what a dataset should NOT be used for. Suppose the customer service transcripts are used to fine-tune a model for a completely different company's customer service bot in a different industry. Identify two specific problems that might arise from this use, and draft a concrete "not to be used for" statement that would appear in the Uses section to prevent this misuse.

   *Hint:* Think about domain mismatch: the language, topics, and user expectations in one company's customer service domain may not transfer to another. Also think about the data subjects: the users who posted on the original forum interacted with Company A's agent. Did they implicitly consent to their words being used to build Company B's commercial product?

6. The **Maintenance** section asks whether data subjects can request removal. Under GDPR Article 17, EU residents have a "right to erasure." If a user whose posts appear in this dataset requests deletion of all their data, describe the specific technical challenges that arise — particularly if the dataset has already been used to fine-tune a model. What would "compliance" require, technically and legally?

   *Hint:* Removing a row from a CSV file is easy. But what if the model has already "learned" from that data — the gradient updates are baked into the model weights? Can you "untrain" a model on a specific example? What does the current state of machine unlearning research say about this?

---

## Model 3: Model Cards

> **Why this matters:** A model card is the document a deployer needs to answer the question "should I use this model for my specific application?" Without it, deployers are guessing — and the consequences of a wrong guess in a high-stakes domain (hiring, healthcare, education) fall on the people the model affects, not the developer who deployed it. Publishing a model card is the minimum act of professional responsibility for anyone who releases a model for others to use.

Mitchell et al. (2019) proposed **Model Cards** as the model-level analogue to Datasheets for Datasets — a standardized document that accompanies a trained model and describes its intended use, performance across subgroups, and ethical considerations. Model Cards are now published by major AI labs (Google, HuggingFace, Anthropic) and are increasingly required by enterprise procurement policies.

| Section | What to Include | Why It Matters to Deployers |
|:--------|:----------------|:----------------------------|
| **Model Details** | Basic facts: model name, version number, type (LLM, image classifier, etc.), training completion date, developer organization, contact information for questions, license | Without this section, deployers cannot verify which version they are using, cannot contact the developer about bugs, and cannot determine if the license permits their use case |
| **Intended Use** | The primary use cases the model was designed and evaluated for; the intended user population; the specific languages, domains, and deployment contexts the model was built to handle | Tells deployers whether this model was actually designed for their use case, or whether they are applying it outside its tested domain |
| **Out-of-Scope Use** | An explicit list of uses the model is NOT designed for; uses known to produce poor or unsafe results; uses that are ethically inappropriate given the model's training and evaluation history | The most important section for preventing misuse — if this section is missing, deployers assume the model is general-purpose and apply it everywhere |
| **Factors** | Demographic or environmental factors that affect model performance; which subgroups were included in evaluation; critically, which subgroups were NOT evaluated and why | Tells deployers where they need to conduct their own evaluation before deploying to populations not tested by the original developers |
| **Metrics** | Which metrics were used to evaluate performance; why these specific metrics were chosen over alternatives; known limitations of the chosen metrics and what they fail to capture | Without this section, a deployer cannot know if "92% accuracy" means 92% on the subpopulation they care about, or 92% averaged over a distribution that does not match their users |
| **Evaluation Data** | What dataset was used for evaluation; how it was split into train/validation/test; whether the evaluation distribution is representative of the actual deployment distribution | A model evaluated on data from 2021 may behave differently in 2026 on topics that have changed; a model evaluated on U.S. English may perform differently on British English or code-switching text |
| **Training Data** | Reference to the dataset used for training, with a Datasheet link if available; known limitations and gaps in the training data that may affect deployed behavior | Connects back to the Datasheet for Datasets; without this section, deployers cannot assess bias or legal risk in the underlying training data |
| **Quantitative Analyses** | Disaggregated evaluation results (results reported separately for each demographic group, not just a single overall average that can hide poor performance on subgroups) — performance broken down by subgroup, domain, language, or demographic — not just aggregate averages | The section where "92% accuracy" becomes "92% overall, 71% for non-native English speakers, 88% for medical domain" — the disaggregated numbers tell the real story |
| **Ethical Considerations** | Known risks from using the model; populations that may be harmed by specific use cases; mitigation measures the developer has implemented; residual risks the deployer must address | Transfers risk-awareness to the deployer; without this section, deployers cannot make an informed decision about whether the residual risks are acceptable for their context |
| **Caveats and Recommendations** | What deployers should know before deploying; recommended additional testing in the deployer's specific context; known gaps in the evaluation that the deployer should fill | A practical "read before deploying" checklist — often the most actionable section for teams making deployment decisions |

**Course connection**: The Hermes-3 model used in the local AI lab is an open-weight model. Its HuggingFace page includes a partial model card. As part of the exercise below, you will identify which sections are missing or incomplete.

### Critical Thinking Questions

7. The **Intended Use** section of a model card should specify the intended user population and deployment context. If a model card says "intended for research and personal use," and a student deploys it as a public-facing academic advising chatbot at a university serving 1,500 students, describe the specific gap between intended and actual use. Explain concretely why that gap matters — what could go wrong that the intended-use evaluation would not have caught?

   *Hint:* "Research" use typically means a technically sophisticated user who knows how to interpret model errors. "Personal use" typically means an individual using the tool for themselves. An academic advising chatbot serves non-technical users who may act on the model's output without questioning it — and serves them at scale, not individually. What failure modes are specific to that population and scale?

8. The **Factors** section asks which subgroups were NOT evaluated. For a language model trained primarily on English-language internet text, identify three specific subgroups of Ursinus College students whose experience with the model is likely to be worse than the aggregate benchmark score would predict — and for each, explain the specific mechanism by which their experience would differ.

   *Hint:* Think about students for whom English is not their first language, students whose academic disciplines use specialized vocabularies not well-represented in general internet text, and students with communication styles (formal vs. informal) that differ from the text the model trained on. For each group, what specific failure mode would you expect?

9. A classmate reads a model card that contains the sentence "Ethical Considerations: this model may produce harmful content in adversarial settings." They conclude that the model card discharges the developer's ethical responsibility — after all, the warning is right there in the document. Evaluate this argument carefully: what does the warning accomplish, and what does it fail to accomplish? What would a more substantive ethical considerations section look like?

   *Hint:* A warning that says "may produce harmful content" tells the deployer almost nothing actionable. What would they need to know to actually decide whether to deploy? Think about specificity: what types of harmful content, under what conditions, with what frequency, affecting which populations? What mitigation did the developer implement, and what residual risk remains?

---

## Exercises

1. **Intended use authoring.**

   *What to do:* For one of the agents you built this semester, write the **Intended Use** and **Out-of-Scope Use** sections of a Model Card. Be specific: name the intended user population, the deployment context, the domain, the languages and formats supported, and at least three concrete out-of-scope uses with a one-sentence explanation of why each is out of scope.

   *Starter hint:* Start by describing your agent as narrowly as possible — not "a helpful assistant" but "a retrieval-augmented Q&A agent designed to answer questions about CS357 course readings for Ursinus College students enrolled in Fall 2026, responding in English, using documents from the course syllabus as its knowledge base." Then for out-of-scope uses, ask: what would break if someone tried to use this outside that narrow description? Would it work in Spanish? For students at another university with different course materials? For medical questions? Each "no" is an out-of-scope use.

   *You've succeeded when:* A classmate who has never seen your agent can read your Intended Use section and understand exactly who should use it and for what — and can read the Out-of-Scope section and understand at least three specific contexts where they should not deploy it.

2. **Composition section for the RAG lab.**

   *What to do:* The course RAG lab used a corpus of documents to answer questions. Identify the documents in that corpus and draft the **Composition** section of a Datasheet for that corpus. Include: total number of documents, document types (PDF, HTML, plain text), domain (academic, legal, news, etc.), known gaps in coverage, whether any sensitive content is present, and the most significant documentation gap you cannot fill because the information was never recorded at collection time.

   *Starter hint:* The Composition section should answer: "If I were a new team member who had never seen this corpus, what would I need to know to decide whether it is appropriate for my use case?" Count and categorize what you have. Then ask honestly: what don't you know about this corpus that you wish you did? The "most significant documentation gap" is usually something you only notice when you try to fill in the template and find you cannot.

   *You've succeeded when:* Your Composition section contains at least five specific factual entries (not vague descriptions) and identifies at least one documentation gap with an explanation of what risk that gap creates for future users of the corpus.

3. **Model card critique.**

   *What to do:* Find a published model card on HuggingFace for any model with more than 10,000 downloads. Read the model card carefully and identify at least two gaps, ambiguities, or missing sections relative to the Mitchell et al. framework. For each gap, write a two-sentence explanation of what a deployer would need to know that the card does not tell them, and what specific harm could result from deploying without that information.

   *Starter hint:* Go to https://huggingface.co/models and sort by downloads. Open the model card for a popular model and go through the Mitchell et al. sections systematically — Intended Use, Out-of-Scope Use, Factors, Metrics, Evaluation Data, Training Data, Quantitative Analyses, Ethical Considerations, Caveats. Most popular model cards are missing or vague on at least three of these. Focus on the gaps that would actually matter to someone making a deployment decision, not just formatting issues.

   *You've succeeded when:* Each identified gap is linked to a specific deployment scenario where the missing information would lead a reasonable deployer to make a worse decision than if the information had been provided.

---

## Reflection Prompt

**Personal level:** Have you ever made a decision based on information you later discovered was incomplete, biased, or from an undocumented source? How did it feel when you discovered the gap? How does that experience connect to what users of undocumented AI systems experience?

**Technical level:** Should model cards be legally required, the way nutrition labels are required on food packages? Consider both sides. What incentives does voluntary disclosure create — and for whom? What incentives does mandatory disclosure create — and for whom? If you were advising a government body writing an AI transparency law, what would you recommend requiring, and what would you leave voluntary?

**Societal level:** Model cards and datasheets shift information from AI developers to AI deployers and ultimately to the public. But reading and evaluating a model card requires technical expertise that most end users do not have. Who should be responsible for translating model card information into terms that affected communities — patients, job applicants, students — can actually use to protect their interests?

---

-> **Coming Up Next:** In the next activity, we look at how to take an agent from a developer's laptop to a production deployment — examining the infrastructure choices, state persistence patterns, and CI/CD pipelines that keep agents running reliably at scale.

---

## Further Reading

- Gebru et al. "Datasheets for Datasets." *Communications of the ACM* 64(12), 2021. https://dl.acm.org/doi/10.1145/3458723
- Mitchell et al. "Model Cards for Model Reporting." *FAccT 2019*. https://dl.acm.org/doi/10.1145/3287560.3287596
- Hugging Face Model Cards documentation: https://huggingface.co/docs/hub/model-cards
- Pushkarna et al. "Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI." *FAccT 2022*.
- Google. "Know Your Data." https://knowyourdata.withgoogle.com/
