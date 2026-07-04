---
layout: assignment
permalink: /Assignments/DataCards
title: "CS357: Foundations of Artificial Intelligence - Assignment: Writing Model Cards and Datasheets for Your Agent"

info:
  coursenum: CS357
  points: 100
  goals:
    - To apply the Datasheet for Datasets framework (Gebru et al.) to a real dataset with section-by-section specificity sufficient for an informed deployment decision
    - To write a model card (Mitchell et al.) for a model used in the course that clearly distinguishes in-scope from out-of-scope uses and identifies bias risks with named populations and mechanisms
    - To identify and document bias risks with evidence-based reasoning naming the affected population, the specific output that exhibits the bias, and the likely training-data mechanism
    - To analyze realistic misuse scenarios and propose specific, implementable technical and policy controls traceable to the documentation
  rubric:
    - weight: 25
      description: Datasheet Completeness
      preemerging: Fewer than 3 sections addressed
      beginning: At least 6 sections present but answers are one-line bullet points that would not give a deployer enough information to assess risk
      progressing: At least 6 sections with substantive answers of 2-4 sentences each addressing the key Gebru et al. questions, with at least one unknown item noted but not explained
      proficient: At least 6 of the 7 sections are answered with enough specificity that a deployer could make an informed decision without additional research — naming who created the dataset, on whose behalf, under what license, what the instances represent, how data was collected, what preprocessing was applied, and whether any regulated categories are present; at least 2 genuinely unknown items are flagged with an explanation of what harm could result from deploying without that information; total word count is at least 500 words across all sections
    - weight: 25
      description: Model Card Quality
      preemerging: Fewer than 4 sections present
      beginning: All required sections present but Ethical Considerations is a single sentence and the Intended Use section does not distinguish in-scope from out-of-scope uses
      progressing: All sections present with substantive content; Ethical Considerations identifies bias risks but does not name the affected population or the specific output behavior; Intended Use lists use cases but out-of-scope uses are vague
      proficient: All required sections are complete; the Intended Use section names at least two specific out-of-scope uses concrete enough that a deployer could recognize them (e.g., "not intended for medical diagnosis" rather than "not for high-stakes decisions"); Ethical Considerations contains the same two bias risks addressed in the Bias and Limitations criterion with the same depth — named group, named output behavior, named mechanism; the Training Data section explicitly references the datasheet from Part 2 and notes at least one known gap identified there; total word count is at least 400 words
    - weight: 25
      description: Bias and Limitations
      preemerging: No bias discussion
      beginning: Bias mentioned generically without naming an affected population, specific output behavior, or mechanism — for example, "the model may exhibit gender bias"
      progressing: Two bias risks identified with a named affected population and plausible reasoning, but the specific output behavior or mechanism for at least one is not specified
      proficient: Two bias risks are fully specified — each names the affected group, describes the specific model output that exhibits the bias (e.g., "disproportionate use of masculine pronouns when completing sentences about surgeons regardless of context"), and explains the likely mechanism in terms of training data distribution; at least one risk is supported by a published citation or by empirical testing the student conducted with results described; the severity of each risk is calibrated by describing the real-world context in which it would cause harm
    - weight: 25
      description: Unintended Use Analysis
      preemerging: No misuse scenarios provided
      beginning: One scenario provided with no controls, or scenarios are theatrical rather than realistic
      progressing: Three scenarios provided with partial controls — at least one names what in the documentation would alert a deployer, but the proposed controls are generic rather than specific to the system
      proficient: Three distinct, realistic misuse scenarios are provided — each names a plausible bad actor with a realistic goal, points to the specific section and language in the model card or datasheet that would alert a careful deployer, and proposes a specific implementable control that is either (a) a technical control naming the mechanism (e.g., input filtering against a regex for HIPAA-regulated terms, rate limiting to N requests per user per hour) or (b) a policy control naming the enforcement mechanism (e.g., a terms-of-service clause requiring human clinical review before acting on any output, with a named audit role)
  readings:
    - rtitle: "Data Cards Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-datacards.md"
    - rtitle: "Bias in Data Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-biasdata.md"

tags:
  - documentation
  - bias
  - transparency
  - model-cards
  - datasheets

---

## Overview
Documentation is not bureaucracy — it is the primary mechanism by which future deployers, researchers, regulators, and users understand what an AI system is and is not designed for. This assignment asks you to write real documentation for systems you have actually used in this course.

---

## How to Approach This Assignment

- **Write for a reader who has never seen your system.** The goal of a datasheet and model card is to give a future engineer, regulator, or user enough information to make an informed decision. Write every section as if the reader cannot just "Google it."
- **"Unknown" is a legitimate answer — but it must be explained.** If you do not know who funded the dataset, write "unknown" and then explain what the absence of this information implies for someone trying to use the data responsibly. One thoughtful "unknown with explanation" is worth more than ten confident answers with no sourcing.
- **The bias section is the hardest and most important part.** Most first drafts say something like "the model may exhibit gender bias." That earns beginning. A proficient answer names the affected group, names the specific kind of output that exhibits the bias (e.g., "gendered pronoun completion," "lower confidence scores for non-native-English speakers"), and proposes the likely mechanism (e.g., "training corpus over-represents English-language web content from North American sources").
- **Your misuse scenarios should be realistic, not theatrical.** "A terrorist uses the model to design a bioweapon" is less useful than "a hiring manager deploys the model to screen resumes without disclosing AI use, violating state transparency laws."

> **Common Pitfall: Writing "unknown" for every unknown item without explaining why it's unknown or why that matters.** Unknown provenance is not neutral — it is a red flag that a deployer needs to investigate. For each unknown, ask: "What harm could happen if this information is absent and the system is deployed anyway?" Write that harm down.

**Recommended time budget:**
- Part 1 (Subject Selection): 15 minutes
- Part 2 (Datasheet): 90 minutes
- Part 3 (Model Card): 75 minutes
- Part 4 (Unintended Use Analysis): 45 minutes
- Reflection + polish: 15 minutes

**What proficient work looks like:** A student working at the proficient level writes a datasheet where you could hand any section to someone who has never heard of the dataset and they would know what it is, who made it, and what risks to be cautious about — without needing to look anything up.

---

## Part 1: Choose Your Subject (ungraded — setup)

**What this part is testing:** Nothing — it is setup. But your choice here determines how interesting your later sections can be. A richer choice makes Parts 2–4 easier to write and earns higher marks.

> **Getting Started Hint:** Option 1 (a pretrained model like Llama 3 or Mistral) is the best choice if you have run one of these models locally in the course — you can write from firsthand experience about its outputs, and its training datasets (The Pile, RedPajama, Common Crawl) are well-documented with published research you can cite. Option 2 (an agent you built) is the best choice if your agent used a specialized knowledge base or made tool calls with a specific dataset — you can speak to the data directly because you configured it. Option 3 (the RAG knowledge base) is the best choice if the documents you indexed have interesting provenance questions (who wrote them? when? is the information still current?). Avoid choosing a subject where you cannot answer at least 5 of the 7 datasheet sections with something more than "unknown."

Select one of the following as your documentation subject:
1. **A pretrained model you ran locally** (Llama 3, Mistral, Hermes, Phi-3, Gemma): you will write the datasheet for a training dataset it likely used (e.g., The Pile, RedPajama, Common Crawl) and the model card for the model itself.
2. **An agent you built in the course** (coding agent, MCP agent, RAG agent): you will write the datasheet for the data your agent accesses or was configured with, and a model card that treats your agent system as the "model."
3. **The RAG knowledge base from the RAG lab**: write the datasheet for the documents you indexed and a model card for the retrieval-augmented system.

State your choice in a one-paragraph **subject description** at the top of your submission.

> **Scope check:** Your subject description should be approximately 100–150 words. It should name the specific dataset and model you are documenting (not just the category), and explain in one sentence why you chose this subject.

---

## Part 2: Datasheet for Datasets (Gebru et al.)

**What this part is testing:** Whether you can answer the Gebru et al. framework questions with the specificity needed for a real deployer to make an informed decision — not just what the dataset contains, but who made it, why, under what constraints, and what risks remain unknown.

Write a datasheet addressing at least **6 of the following 7 sections**. For each section, answer the key questions from the original Gebru et al. (2021) framework. Minimum 500 words total across all sections.

### Motivation

- For what purpose was the dataset created?
- Who created the dataset, and on whose behalf?
- Who funded the creation?

**EXAMPLE — Motivation section for ImageNet (use a different dataset; this is for illustration only):**

> *ImageNet was created to support large-scale visual object recognition research. It was created by Fei-Fei Li and colleagues at Stanford University, with collection coordinated through Princeton University, on behalf of the academic computer vision research community. Funding came from the National Science Foundation, Google, and Microsoft Research. The dataset was not created with commercial deployment in mind; it was explicitly designed as a research benchmark. This matters for deployers: using ImageNet-pretrained models in commercial contexts imports assumptions baked in during academic benchmarking that may not hold outside the lab.*

*EXAMPLE — replace with your own dataset's Motivation section.*

> **Getting Started Hint:** For well-known datasets (Common Crawl, The Pile, RedPajama), the original paper describing the dataset will contain much of this information. Search "[dataset name] paper" or "[dataset name] datasheet" — many large datasets now publish their own datasheets. For your own RAG knowledge base or agent data, you are the creator; answer these questions as honestly as you can about your own choices.

### Composition
- What do the instances represent?
- How many instances are there?
- Is there a label or target? If so, what is it?
- Does the dataset contain data that might be considered confidential?
- Does the dataset contain data that might be considered sensitive?

### Collection Process
- How was the data collected?
- Was the data directly observed, reported by subjects, or inferred?
- Who performed the data collection?

### Preprocessing / Cleaning / Labeling
- Was any preprocessing done? What?
- Was the raw data saved? Is it accessible?
- Is the software used for preprocessing available?

### Uses
- Has the dataset been used for any tasks already?
- What other tasks could it be used for?
- Is there anything about the composition, collection process, or preprocessing that might impact future uses?

### Distribution
- How is the dataset distributed?
- When was it released? Under what license?
- Were any third parties involved in the distribution?

### Maintenance
- Who is maintaining the dataset?
- Is there an erratum? Will the dataset be updated? On what schedule?
- Will older versions continue to be supported?

**Flag at least 2 items across any section that are genuinely unknown or unverifiable for your dataset, and explain why the absence of this information is a risk.**

> **Scope check:** Your datasheet should be at least 500 words total across all sections. Each section should have at least 2–4 substantive sentences, not just a single line per bullet point.

---

## Part 3: Model Card (Mitchell et al.)

**What this part is testing:** Whether you can write the kind of documentation that would allow a responsible deployer to decide whether a model is appropriate for their use case — including the uncomfortable sections like ethical considerations and caveats.

Write a model card with all of the following sections. Minimum 400 words total.

### Model Details
Name, version, type, training date (if known), contact, license.

### Intended Use
Primary use cases, intended users, out-of-scope uses. Be specific: "not intended for medical diagnosis" is better than "not for high-stakes decisions."

### Factors
Relevant groups (demographic, linguistic, domain) where performance may vary.

### Metrics
What metrics were used to evaluate the model? Why were these metrics chosen?

### Evaluation Data
What data was used for evaluation? Is it representative of intended use?

### Training Data
Summary of training data (reference your datasheet from Part 2). Note any known gaps.

### Quantitative Analyses
Report any disaggregated performance metrics you can find or infer (e.g., accuracy by language, accuracy on technical vs. casual prompts in your own testing).

### Ethical Considerations

Identify **at least 2 specific bias risks**. For each, state: which group is affected, what the model output looks like when the bias manifests, and the likely mechanism.

**EXAMPLE — Ethical Considerations section showing the depth expected (for a generic large language model — replace with your own model):**

> *Bias Risk 1: Occupational gender bias. When prompted to complete sentences about professionals in fields like "The surgeon walked into the room and [blank]," the model disproportionately uses masculine pronouns (he/him) regardless of context, even when no gender has been specified. The likely mechanism is that the training corpus (primarily English-language web text) over-represents historical news and professional writing in which surgeons, executives, and engineers were predominantly male, so the model learned these statistical associations. This affects users who interact with the model in professional writing contexts and may reinforce occupational stereotypes at scale.*

> *Bias Risk 2: Language quality and fluency bias. The model produces measurably lower-quality outputs (shorter, less coherent, more likely to switch to English mid-response) when prompted in lower-resource languages such as Swahili, Bengali, or Yoruba, compared to English, Spanish, or French. The likely mechanism is training data imbalance: Common Crawl and similar corpora contain orders of magnitude more English-language content than most African and South Asian languages. This systematically disadvantages users in those language communities.*

*EXAMPLE — replace with your own model's ethical considerations.*

### Caveats and Recommendations
What should deployers know that isn't captured elsewhere? What monitoring is recommended?

> **Getting Started Hint:** For the Ethical Considerations section, do not start by asking "is this model biased?" Start by asking: "Who uses this model, and in what contexts could the model's outputs disadvantage some users more than others?" Then work backward to the mechanism. If you have run the model yourself, try prompting it with questions about different demographic groups and observe whether the outputs differ in quality, tone, or content.

> **Scope check:** Your model card should be at least 400 words total. The Ethical Considerations section alone should be at least 150 words.

---

## Part 4: Unintended Use Analysis

**What this part is testing:** Whether you can think adversarially about your own system — anticipating misuse by actors with different goals than the intended users, and designing safeguards into the documentation itself.

Write a **1-page section** identifying 3 realistic misuse scenarios. For each scenario:

1. **Describe the misuse**: who is the bad actor, what do they want to achieve, how do they use your model/agent?
2. **What in the documentation alerts a careful deployer**: point to the specific section (Intended Use, Ethical Considerations, etc.) and quote or paraphrase the warning.
3. **Propose one control**: it must be either (a) a technical control (input filtering, access control, rate limiting, sandboxing) or (b) a policy control (terms of service clause, audit requirement, human review gate). Be specific.

> **Getting Started Hint:** The best misuse scenarios are ones that are *just plausible enough to actually happen* — not sci-fi, not obviously illegal. Think about who might use your system in an unintended context, at unintended scale, or with unintended trust. A retrieval-augmented system built on medical literature could be misused by a non-clinician treating it as a diagnostic tool. A coding agent could be misused to generate malicious scripts. A customer service chatbot could be misused to phish users by imitating it.

> **Scope check:** Your response to this part should be approximately 400–500 words — roughly one paragraph per scenario plus the three components for each.

---

## Common Mistakes

- **Writing "unknown" for every unknown item without explaining why it's unknown or why that matters.** Unknown provenance is a red flag, not a neutral absence. For each unknown, identify the specific risk it creates.
- **Writing a model card that only describes the intended use without specifying out-of-scope uses.** The most valuable line in a model card is often "this model should NOT be used for X." Be specific about the X.
- **Treating the bias section as a checkbox.** "This model may exhibit bias" is a sentence that says nothing. Name the group, the output, and the mechanism — all three.
- **Writing misuse scenarios that are implausible or theatrical.** Misuse scenarios should be realistic enough that the proposed control is actually warranted. If the scenario requires a nation-state adversary with extraordinary resources, the control you propose will not match.
- **Ignoring the interaction between the datasheet and the model card.** These two documents are meant to work together — the model card's Training Data section should explicitly reference your datasheet. If your datasheet identified an unknown or a risk, that risk should appear somewhere in the model card's Ethical Considerations or Caveats section.

---

## Reflection Prompts

- Model cards are voluntary. A competitor who publishes a thorough card exposes weaknesses a more secretive competitor hides. What market incentive problem does this create? How might it be solved (contractually, legally, or through standards)? (1 paragraph. Consider analogies to financial disclosure requirements or pharmaceutical labeling — industries that faced similar incentive problems.)
- Writing the bias section in Part 3: did it change how you think about using the system yourself? Why or why not? (2–3 sentences. This reflection matters because documentation is not just for others — it is a practice that changes how you see the systems you build.)
- If collaboration beyond your own occurred, identify it. Do you certify this represents your original work? Please identify any portions not originally written by you.
- Approximately how many hours did this assignment take?
