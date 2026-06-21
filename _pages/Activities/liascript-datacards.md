# Dataset Documentation: Model Cards and Datasheets
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

## Model 1: Why Documentation Matters

The most common way AI systems fail in deployment is not because the model made a random error — it is because the model was trained on data that did not represent the deployment context, and no one knew. This failure pattern is called **undocumented dataset risk**: the training data has properties (bias, staleness, skewed provenance, missing consent) that are unknown to the team deploying the model, so they cannot account for those properties in their system design.

| Risk Category | Documented Dataset | Undocumented Dataset |
|:--------------|:------------------|:--------------------|
| **Bias** | Known demographics and sampling strategy allow auditors to check for disparate impact before deployment | Bias is discovered after deployment, often through user harm; remediation is costly and public |
| **Legal** | License, consent, and copyright information is on record; legal review can proceed before launch | Legal exposure is unknown; takedowns and fines discovered post-launch; data may need to be deleted and model retrained |
| **Reproducibility** | Dataset version, collection date, and preprocessing steps are logged; results can be replicated and compared | Results cannot be reproduced; different teams reach different conclusions from "the same" experiment |
| **Auditability** | Regulators, courts, and third-party auditors can inspect the data provenance trail | Auditability is impossible without provenance; regulatory penalties increase; litigation discovery is damaging |

**Real failure pattern**: In 2015, a major tech company's image classifier labeled photographs of Black people with animal-related categories. Postmortem analysis revealed the training set underrepresented darker skin tones because the web scrape that created it oversampled images from predominantly white-user platforms. No datasheet existed. No one had documented the sampling strategy, so no one caught the problem during development. The harm was discovered by the public.

### Critical Thinking Questions

1. The failure pattern above resulted from a sampling bias in web scraping. If the team had been required to complete a Datasheet for Datasets before training, at which section would the bias have been most likely to surface? Explain what question the Datasheet would have forced them to ask.

2. The "Legal" row says undocumented datasets create unknown legal exposure. Identify two specific ways a training dataset scraped from the public internet might create legal liability, even if the scraping was technically possible. Which legal frameworks govern each one?

3. A classmate argues: "Our course RAG agent doesn't train a model — it just retrieves documents. So we don't need to document the dataset." Evaluate this argument. Are there documentation obligations for a retrieval corpus that is not used for training?

---

## Model 2: The Datasheet for Datasets Framework

Gebru et al. (2018) proposed a standard template for dataset documentation, analogous to datasheets for electronic components. Each datasheet answers a structured set of questions so that anyone who uses the dataset knows what it contains, where it came from, how it was processed, and what it may or may not be used for.

| Section | Core Question to Answer |
|:--------|:------------------------|
| **Motivation** | Who created the dataset, for what purpose, and with whose funding? Is there a specific task the dataset was designed to support? |
| **Composition** | What kinds of instances does the dataset contain (text, images, structured records)? How many instances? What is the distribution across categories, demographics, or labels? Is any sensitive information present? |
| **Collection Process** | How was the data collected — scraping, surveys, sensors, human annotation? Over what time period? Were the data subjects aware their data was being collected? |
| **Preprocessing/Cleaning** | What preprocessing was applied (tokenization, deduplication, filtering)? What was removed and why? Is the raw data available alongside the processed version? |
| **Uses** | What tasks is the dataset appropriate for? What uses should it NOT be used for, and why? Are there potential harms from misuse? |
| **Distribution** | Under what license is the dataset released? Are there export restrictions, consent limitations, or terms of service that restrict redistribution? Does distribution comply with applicable privacy law? |
| **Maintenance** | Who is responsible for the dataset going forward? How will errors be corrected? Will it be updated? Is there a mechanism for data subjects to request removal? |

[[MC]]
A team publishes a dataset of 50,000 customer service chat transcripts scraped from a public online forum. The transcripts contain real user complaints and agent responses. The team's datasheet includes the file format, total size, and a sample of ten transcripts. Which of the following is the MOST serious omission from their datasheet?

- ( ) They did not include information about the compression format and file encoding used
- (x) They did not document consent, licensing, or whether users of the public forum agreed to have their messages collected and redistributed — the Distribution section is absent, leaving legal and ethical exposure unaddressed
- ( ) They did not include a benchmark comparison showing their dataset improves model performance
- ( ) They did not list the exact file sizes for each individual transcript

### Critical Thinking Questions

4. The **Collection Process** section asks whether data subjects were aware their data was being collected. For the customer service transcript dataset above, the posts were publicly visible. Does "publicly visible" mean "consented to collection and redistribution"? What distinction matters here?

5. The **Uses** section asks what a dataset should NOT be used for. Suppose the customer service transcripts are used to fine-tune a model for a different company's customer service bot. What problems might arise from this use, and what would a responsible "not to be used for" statement say?

6. The **Maintenance** section asks whether data subjects can request removal. Under GDPR, individuals have a "right to erasure." If a user whose posts appear in this dataset requests deletion, what technical challenges arise in complying — especially if the dataset has already been used for training?

---

## Model 3: Model Cards

Mitchell et al. (2019) proposed **Model Cards** as the model-level analogue to Datasheets for Datasets — a standardized document that accompanies a trained model and describes its intended use, performance across subgroups, and ethical considerations. Model Cards are now published by major AI labs (Google, Hugging Face, Anthropic) and are increasingly required by enterprise procurement policies.

Key sections of a Model Card:

| Section | What to Include |
|:--------|:----------------|
| **Model Details** | Basic facts: name, version, type (LLM, classifier, etc.), training date, developer organization, contact, license |
| **Intended Use** | Primary intended use cases; intended users; languages, domains, or contexts the model was designed for |
| **Out-of-Scope Use** | Explicit list of uses the model is NOT designed for; uses that are known to produce poor results; uses that are ethically inappropriate |
| **Factors** | Demographic or environmental factors that affect model performance; what subgroups were evaluated; what subgroups were NOT evaluated |
| **Metrics** | Which metrics were used to evaluate performance; why these metrics were chosen; any limitations of the chosen metrics |
| **Evaluation Data** | What dataset was used for evaluation; how it was split; whether it is representative of the deployment distribution |
| **Training Data** | Reference to the dataset (with Datasheet if available); known limitations of the training data |
| **Quantitative Analyses** | Disaggregated evaluation results (performance broken down by subgroup, domain, language, etc.) |
| **Ethical Considerations** | Known risks; populations that may be harmed; mitigation measures in place |
| **Caveats and Recommendations** | What users should know before deploying; recommended additional testing; known gaps |

**Course connection**: The Hermes-3 model used in the local AI lab is an open-weight model. Its HuggingFace page includes a partial model card. As part of the exercise below, you will fill in the sections that are missing or incomplete.

### Critical Thinking Questions

7. The **Intended Use** section of a model card should include "intended users." If Hermes-3 is intended for "research and personal use," and a student deploys it as a public-facing academic advising chatbot at a university, what gap does this create between intended and actual use — and why does that gap matter?

8. The **Factors** section asks which subgroups were NOT evaluated. For a language model trained primarily on English text, list three subgroups of users whose experience with the model is likely to be worse than the average benchmark score would predict.

9. A classmate reads a model card that says "Ethical Considerations: this model may produce harmful content in adversarial settings." They conclude the model card discharges the developer's ethical responsibility — the warning is right there. Evaluate this argument. What does the warning accomplish, and what does it fail to accomplish?

---

## Exercises

1. **Intended use authoring.** For one of the agents you built this semester, write the **Intended Use** and **Out-of-Scope Use** sections of a Model Card. Be specific: name the intended user population, the domain, the deployment context, and at least three concrete out-of-scope uses with explanations of why each is out of scope.

2. **Composition section for the RAG lab.** The course RAG lab collected a corpus of documents to answer questions. Identify what documents were in that corpus, draft the **Composition** section of a Datasheet for that corpus (number of documents, types, domain, known gaps in coverage, sensitive content, if any), and identify the most significant documentation gap you cannot fill because the information was never recorded.

3. **Model card critique.** Find a published model card on HuggingFace for any model with more than 10,000 downloads. Read the model card and identify at least two gaps, ambiguities, or missing sections relative to the Mitchell et al. framework. For each gap, explain what a user would need to know that the model card does not tell them, and what harm could result from the gap.

---

## Reflection Prompt

In your notebook: should model cards be legally required, the way nutrition labels are required on food packages? Consider both sides. What incentives does voluntary disclosure create — and for whom? What incentives does mandatory disclosure create — and for whom? If you were advising a government body writing an AI transparency law, what would you recommend requiring, and what would you leave voluntary?

---

## Further Reading

- Gebru et al. "Datasheets for Datasets." *Communications of the ACM* 64(12), 2021. https://dl.acm.org/doi/10.1145/3458723
- Mitchell et al. "Model Cards for Model Reporting." *FAccT 2019*. https://dl.acm.org/doi/10.1145/3287560.3287596
- Hugging Face Model Cards documentation: https://huggingface.co/docs/hub/model-cards
- Pushkarna et al. "Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI." *FAccT 2022*.
- Google. "Know Your Data." https://knowyourdata.withgoogle.com/
