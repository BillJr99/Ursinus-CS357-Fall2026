---
layout: assignment
permalink: /Assignments/DataCards
title: "CS357: Foundations of Artificial Intelligence - Assignment: Writing Model Cards and Datasheets for Your Agent"

info:
  coursenum: CS357
  points: 100
  goals:
    - To apply the Datasheet for Datasets framework (Gebru et al.) to a real dataset
    - To write a model card (Mitchell et al.) for a model used in the course
    - To identify and document bias risks with evidence-based reasoning
    - To analyze realistic misuse scenarios and propose technical and policy controls
  rubric:
    - weight: 25
      description: Datasheet Completeness
      preemerging: Fewer than 3 sections addressed
      beginning: 6 sections present but answers are one-line
      progressing: 6 sections with substantive answers, some key questions from the framework answered
      proficient: All 7 sections answered with specific details, at least 2 genuinely unknown items flagged and explained, minimum 500 words
    - weight: 25
      description: Model Card Quality
      preemerging: Fewer than 4 sections
      beginning: All sections present but Ethical Considerations is a single sentence
      progressing: All sections with substantive content
      proficient: All sections complete, Ethical Considerations identifies 2 specific bias risks with supporting reasoning, Intended Use section clearly distinguishes in-scope from out-of-scope uses, minimum 400 words
    - weight: 25
      description: Bias and Limitations
      preemerging: No bias discussion
      beginning: Bias mentioned generically without specifics
      progressing: Two bias risks identified with plausible reasoning
      proficient: Two bias risks are specific (which population, which output, what mechanism), at least one is supported by a citation or empirical reference, and the risk's severity is calibrated
    - weight: 25
      description: Unintended Use Analysis
      preemerging: No misuse scenarios
      beginning: One scenario with no controls
      progressing: Three scenarios with partial controls
      proficient: Three distinct misuse scenarios, each with what in the card would alert a deployer, and a specific technical or policy control that is implementable
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
Documentation is not bureaucracy --- it is the primary mechanism by which future deployers, researchers, regulators, and users understand what an AI system is and is not designed for. This assignment asks you to write real documentation for systems you have actually used in this course.

## Part 1: Choose Your Subject (ungraded --- setup)
Select one of the following as your documentation subject:
1. **A pretrained model you ran locally** (Llama 3, Mistral, Hermes, Phi-3, Gemma): you will write the datasheet for a training dataset it likely used (e.g., The Pile, RedPajama, Common Crawl) and the model card for the model itself.
2. **An agent you built in the course** (coding agent, MCP agent, RAG agent): you will write the datasheet for the data your agent accesses or was configured with, and a model card that treats your agent system as the "model."
3. **The RAG knowledge base from the RAG lab**: write the datasheet for the documents you indexed and a model card for the retrieval-augmented system.

State your choice in a one-paragraph **subject description** at the top of your submission.

## Part 2: Datasheet for Datasets (Gebru et al.)
Write a datasheet addressing at least **6 of the following 7 sections**. For each section, answer the key questions from the original Gebru et al. (2021) framework. Minimum 500 words total across all sections.

### Motivation
- For what purpose was the dataset created?
- Who created the dataset, and on whose behalf?
- Who funded the creation?

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

## Part 3: Model Card (Mitchell et al.)
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

### Caveats and Recommendations
What should deployers know that isn't captured elsewhere? What monitoring is recommended?

## Part 4: Unintended Use Analysis
Write a **1-page section** identifying 3 realistic misuse scenarios. For each scenario:

1. **Describe the misuse**: who is the bad actor, what do they want to achieve, how do they use your model/agent?
2. **What in the documentation alerts a careful deployer**: point to the specific section (Intended Use, Ethical Considerations, etc.) and quote or paraphrase the warning.
3. **Propose one control**: it must be either (a) a technical control (input filtering, access control, rate limiting, sandboxing) or (b) a policy control (terms of service clause, audit requirement, human review gate). Be specific.

## Reflection Prompts

- Model cards are voluntary. A competitor who publishes a thorough card exposes weaknesses a more secretive competitor hides. What market incentive problem does this create? How might it be solved (contractually, legally, or through standards)?
- Writing the bias section in Part 3: did it change how you think about using the system yourself? Why or why not?
- If collaboration beyond your own occurred, identify it. Do you certify this represents your original work? Please identify any portions not originally written by you.
- Approximately how many hours did this assignment take?
