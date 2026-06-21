# AI for Scientific Discovery: AlphaFold, Drug Discovery, and the Reproducibility Crisis

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-aiscience.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

**CS357: Foundations of Artificial Intelligence / Agentic AI**
Ursinus College

---

## POGIL Roles

In this activity, your team will work together using the following roles. Rotate roles with each new activity.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the team on task and on time; ensures everyone contributes; calls for consensus before moving on |
| **Recorder** | Writes down the team's agreed answers; manages the shared document or whiteboard |
| **Presenter** | Speaks for the team during class discussion; summarizes findings to the class |
| **Reflector** | Monitors team process; notes what is working and what is not; leads the Reflection section |

> Before starting, confirm your roles aloud. If your team has fewer than 4 members, one person may take two roles (e.g., Manager + Reflector).

---

## Model 1: What AI Can Do for Science

Over the past decade, AI has moved from a tool for analyzing data to an active participant in the scientific process itself. The landmark example is **AlphaFold2**, developed by DeepMind and published in *Nature* in 2021. Protein structure determines protein function; prior to AlphaFold, determining a single protein's 3D structure experimentally could take years. AlphaFold predicted structures for over 200 million proteins — essentially the entire known protein universe — in months.

Yet the achievement also illustrates an important tension: **prediction is not the same as explanation**. AlphaFold tells you *what* a protein looks like; it does not tell you *why* it folds that way, nor does it reveal the biochemical mechanism. This distinction matters for drug discovery, where understanding mechanism is often as important as knowing structure.

The table below surveys AI applications across scientific domains:

| Case Study | Scientific Domain | What AI Did | Key Limitation |
|------------|------------------|-------------|----------------|
| **AlphaFold2** (DeepMind, 2021) | Structural biology | Predicted 3D protein structures for 200M+ proteins at near-experimental accuracy | Predicts structure, not dynamics or function; does not explain folding mechanism |
| **GNoME** (DeepMind, 2023) | Materials science | Discovered 2.2 million new stable crystal structures, of which ~380,000 are potentially synthesizable | Stability prediction does not guarantee synthesizability or usefulness |
| **Med-PaLM 2** (Google, 2023) | Medical Q&A | Achieved "expert" level on medical licensing exam questions | Hallucination risk; not approved for clinical use; lacks patient context |
| **Generative models for molecules** | Drug discovery | Generate candidate drug molecules with desired properties (e.g., binding affinity, low toxicity) | High false-positive rate; most generated candidates fail in wet-lab validation |
| **LLMs for literature review** | All domains | Summarize papers, extract findings, identify research gaps across thousands of documents | Hallucinate citations; miss nuance; cannot assess methodological quality |

### Critical Thinking Questions

**Question 1.** AlphaFold2 predicted the structures of over 200 million proteins. A biochemist might say "we now know these structures" while a philosopher of science might say "we have predictions, not knowledge." What is the difference between *predicting* a structure and *understanding* why it takes that structure? Does the distinction matter for science?

[[___ Your answer here ___]]

**Question 2.** AlphaFold finds a pattern — the mapping from amino acid sequence to 3D structure — without providing a mechanistic explanation. What is the difference between finding a pattern and explaining why it exists? Give an example from another domain where finding a pattern was useful even without a complete explanation.

[[___ Your answer here ___]]

**Question 3.** Identify one scientific domain *not* listed in the table where AI has not yet made major inroads. Hypothesize at least two reasons why AI has been slower to impact that domain (consider: data availability, interpretability requirements, validation difficulty, or regulatory constraints).

[[___ Your answer here ___]]

---

## Model 2: Reproducibility, Provenance, and Trust

Science depends on reproducibility: an experiment should be replicable by an independent team. AI introduces new reproducibility challenges on top of existing ones.

The **reproducibility crisis** in science — particularly in psychology and biomedicine — was already severe before AI: researchers found that many published findings could not be replicated. Contributing causes include **p-hacking** (testing many hypotheses and reporting only the significant ones), **publication bias** (journals preferring positive results), and the **garden of forking paths** (many defensible analytical choices that each slightly bias results).

AI adds three new dimensions to this crisis:

| Reproducibility Risk | What Goes Wrong | How to Detect | How to Mitigate |
|---------------------|-----------------|---------------|-----------------|
| **Training data contamination** | Test data appears in training data; model "memorizes" answers rather than generalizing; inflated benchmark scores | Check for data overlap between train/test splits; use held-out evaluation sets not released publicly | Time-based splits (train before date X, test after); independent benchmark curation; model auditing |
| **Prompt sensitivity** | Slight rewording of a prompt produces substantially different outputs; published results may not reproduce with minor prompt variations | Systematically vary prompts and report variance; include exact prompt text in methods section | Report exact prompts and model version; run multiple prompt phrasings; use prompt templates |
| **Stochastic output** | Same prompt + same model → different outputs across runs due to temperature/sampling; reported results reflect one run | Run multiple times; report mean and variance; use deterministic decoding (temperature=0) when appropriate | Set seed and temperature; report number of runs; publish all outputs, not just best |

### Critical Thinking Questions

**Question 4.** A research team uses an LLM to help analyze qualitative interview data. The LLM assigns themes to each interview excerpt. Should the LLM be listed as a co-author on the resulting paper? What criteria would you use to make this decision, and how does your answer change depending on how central the LLM's contribution was?

[[___ Your answer here ___]]

**Question 5.** Traditional scientific citations allow readers to look up the source. How do you cite a model that may have been retrained, updated, or deprecated between submission and publication of a paper? What information would a citation for an LLM-assisted analysis need to include to be meaningful to future readers?

[[___ Your answer here ___]]

**Question 6.** In classical experimental science, "replication" means re-running the experiment under the same conditions. If the model used in a study is stochastic (produces different outputs each run), what does "replication" mean? Is it possible to replicate an AI-assisted study in the traditional scientific sense? What standard would you propose instead?

[[___ Your answer here ___]]

---

A research team publishes results from an LLM-assisted literature review. An independent replication team runs the same prompts six months later, using what they believe is the same model, and reaches different conclusions on several key findings. The most scientifically responsible response is:

- ( ) Declare the original paper fraudulent, since the results cannot be reproduced
- ( ) Declare LLMs categorically unusable for scientific research
- (x) Report both runs in full, document exact prompt versions and model IDs (including version dates), and rigorously analyze where and why the outputs diverged
- ( ) Average the conclusions of the two runs and publish a correction

---

## Model 3: The Agent as Research Assistant

Increasingly, researchers are deploying agents — not just single LLM calls — to assist with the research pipeline. A typical AI-assisted research pipeline might look like this:

1. **Literature search**: Agent queries Semantic Scholar API or PubMed for papers matching a topic
2. **Summary extraction**: Agent reads abstracts and full texts, extracts key findings, methods, and limitations
3. **Hypothesis generation**: Agent proposes new research questions or connections across papers
4. **Code generation for analysis**: Agent writes Python/R code to run statistical analyses on a dataset
5. **Result interpretation**: Agent interprets output and suggests conclusions

At every step, there are points where human judgment remains essential — and points where an undetected error could propagate silently through all downstream steps.

### Critical Thinking Questions

**Question 7.** Review the five-step pipeline above. At which step would an undetected error be most dangerous to the validity of the final result? Explain why an error at that step is particularly hard to catch and why its consequences are most severe.

[[___ Your answer here ___]]

**Question 8.** Imagine this pipeline is being used to assist in a systematic review for a clinical trial — a study that will inform treatment decisions for patients. What specific safeguards would you add at each step of the pipeline to ensure the integrity of the review? Be concrete: name at least one safeguard per step.

[[___ Your answer here ___]]

**Question 9.** Design a "reproducibility protocol" for AI-assisted research. Describe exactly three steps a researcher must take — at the time of conducting the research, not at publication — to ensure that another team could reproduce their AI-assisted findings five years later. Each step should be specific and actionable.

[[___ Your answer here ___]]

---

## Exercises

**Exercise 1.** Choose a paper in a domain that interests you (biology, chemistry, psychology, economics, etc.) and use a publicly accessible LLM to generate a summary of its abstract. Read the abstract yourself and compare carefully. Identify at least two factual errors, omissions, or distortions in the AI-generated summary. Report your findings in the format: (a) the AI's claim, (b) what the paper actually says, (c) the type of error (fabrication, omission, misattribution, oversimplification).

[[___ Your answer here ___]]

**Exercise 2.** Design a five-step provenance record for an AI-assisted experiment. For each step, specify: (a) what information must be logged, (b) when it must be logged (before, during, or after the step), and (c) in what format it should be stored so it is both human-readable and machine-parseable. Consider model versions, prompts, outputs, timestamps, and human review decisions.

[[___ Your answer here ___]]

**Exercise 3.** Read the abstract of Jumper et al. (2021) "Highly accurate protein structure prediction with AlphaFold" (*Nature*, 596, 583–589). Write a 150–200 word analysis distinguishing: (a) what biological *insight* the paper claims to provide, (b) what it only *predicts* without explaining, and (c) what scientific questions about protein biology it leaves unanswered.

[[___ Your answer here ___]]

---

## Reflection Prompt

AI can identify patterns in data that no human could find by reading papers or running experiments at human speed. AlphaFold found the pattern from sequence to structure across hundreds of millions of proteins. Does the ability to find patterns at that scale make AI a *good scientist*?

Consider: What does science require beyond pattern-matching? Think about hypothesis formation, mechanistic explanation, experimental design, peer review, and the ability to know when you are wrong. Write a personal reflection of 150–250 words. The Reflector on your team should be prepared to share one key point with the class.

[[___ Your reflection here ___]]

---

## Further Reading

- Jumper, J., Evans, R., et al. (2021). "Highly accurate protein structure prediction with AlphaFold." *Nature*, 596, 583–589.
- Nature editorial (2023). "Tools such as ChatGPT threaten transparent science; here are our ground rules for their use." *Nature*, 613, 612.
- Kapoor, S., and Narayanan, A. (2023). "Leakage and the Reproducibility Crisis in ML-based Science." *Patterns*, 4(9).
- Ioannidis, J. P. A. (2005). "Why Most Published Research Findings Are False." *PLOS Medicine*, 2(8).
- Merchant, A., et al. (2023). "Scaling deep learning for materials discovery." *Nature*, 624, 80–85. [GNoME paper]
- Singhal, K., et al. (2023). "Large language models encode clinical knowledge." *Nature*, 620, 172–180. [Med-PaLM 2]
