<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-aiscience.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# AI for Scientific Discovery: AlphaFold, Drug Discovery, and the Reproducibility Crisis

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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Prediction vs. explanation** | Prediction tells you *what* will happen; explanation tells you *why*, and science ultimately needs both | AlphaFold predicts a protein's 3D shape with high accuracy but does not explain the chemical forces that drive it to fold that way |
| **Reproducibility** | The ability of an independent team to run the same experiment and reach the same conclusions, the bedrock of scientific trust | A drug trial published in *Nature* should be replicable by a lab in Japan using the same protocol; an LLM-assisted analysis should be replicable with the same prompt and model version |
| **Data contamination** | When test questions or answers appear in the training data, making benchmark scores artificially high; the model "memorized" the test rather than learned to generalize | A model trained on internet text that included all of HumanEval's 164 coding problems will score perfectly on that benchmark without being a good general programmer |
| **Prompt sensitivity** | The finding that slightly different phrasings of the same question can produce substantially different LLM outputs, meaning published AI-assisted results may not reproduce with even minor prompt changes | "Summarize the limitations of this study" vs. "What are this paper's weaknesses?" may produce different emphasis and different omissions |
| **Provenance** | A complete record of where data came from, how it was processed, and which model version produced which output, necessary for auditing AI-assisted research | A provenance log for an LLM-assisted literature review would include: exact model ID and version date, the exact prompt text, the temperature setting, and a timestamp for each run |
| **AI research pipeline** | A multi-step automated workflow where an AI agent performs literature search, data extraction, analysis, and interpretation, with humans supervising rather than doing each step | A team uses an agent to query PubMed, extract findings from 500 abstracts, and generate a draft systematic review, then human experts review and validate the draft |

---

## Model 1: What AI Can Do for Science

Imagine a scientific puzzle that has stumped researchers for 50 years: figuring out what shape a protein takes when it folds. Every protein in your body is a chain of amino acids, and the shape it folds into determines what it does: whether it carries oxygen, fights infection, or signals cells to divide. Determining that shape experimentally took years of work per protein. AlphaFold solved it for 200 million proteins in months. That is not incremental progress; it is a phase transition in what science can do. But it also illustrates a deep question: when an AI finds an answer without telling you *why* the answer is right, does that count as scientific understanding?

Over the past decade, AI has moved from a tool for analyzing data to an active participant in the scientific process itself. The landmark example is **AlphaFold2**, developed by DeepMind and published in *Nature* in 2021. Protein structure determines protein function; prior to AlphaFold, determining a single protein's 3D structure experimentally could take years. AlphaFold predicted structures for over 200 million proteins (essentially the entire known protein universe) in months.

Yet the achievement also illustrates an important tension: **prediction is not the same as explanation**. AlphaFold tells you *what* a protein looks like; it does not tell you *why* it folds that way, nor does it reveal the biochemical mechanism. This distinction matters for drug discovery, where understanding mechanism is often as important as knowing structure.

The table below surveys AI applications across scientific domains:

| Case Study | Scientific Domain | What AI Did | Key Limitation | Status in 2026 |
|------------|------------------|-------------|----------------|----------------|
| **AlphaFold2** (DeepMind, 2021) | Structural biology | Predicted 3D protein structures for 200M+ proteins at near-experimental accuracy, a task that previously required X-ray crystallography taking years per protein | Predicts structure, not dynamics or function; does not explain the folding mechanism or how the protein moves in a living cell | The AlphaFold Protein Structure Database is freely available and actively used in drug discovery pipelines worldwide |
| **GNoME** (DeepMind, 2023) | Materials science | Discovered 2.2 million new stable crystal structures (potential new materials for batteries, semiconductors, and superconductors), of which ~380,000 are potentially synthesizable | Stability prediction does not guarantee synthesizability in a real lab, usefulness for any application, or safety of manufacture | Researchers are actively working to synthesize and test the most promising candidates; results are mixed so far |
| **Med-PaLM 2** (Google, 2023) | Medical Q&A | Achieved "expert" level on USMLE (US Medical Licensing Exam) questions, the same exam human doctors must pass to practice | Hallucination risk remains high for clinical use; not approved for clinical decision-making; lacks patient history, physical exam findings, and clinical context | Used for medical education and information retrieval; not deployed for clinical decisions; several specialized medical LLMs are in FDA review |
| **Generative models for molecules** | Drug discovery | Generate candidate drug molecules with specified properties (target binding affinity, low toxicity, oral bioavailability), orders of magnitude faster than traditional computational chemistry | High false-positive rate: most AI-generated candidates that look good in simulation fail in wet-lab validation; no model reliably predicts in-vivo behavior | Insilico Medicine received approval to start Phase 1 human trials for an AI-designed drug (INS018_055) in 2023, the first such trial in history |
| **LLMs for literature review** | All scientific domains | Summarize papers, extract key findings, identify research gaps, and suggest connections across thousands of documents faster than any human team could read them | Hallucinate citations; miss methodological nuance; cannot assess statistical quality; do not flag conflicts of interest or funding bias | Major journals (Nature, Science, ICML) now require disclosure of LLM use in manuscript preparation; some require authors to verify all AI-generated citations manually |

### Critical Thinking Questions

**Question 1.** AlphaFold2 predicted the structures of over 200 million proteins. A biochemist might say "we now know these structures" while a philosopher of science might say "we have predictions, not knowledge." What is the difference between *predicting* a structure and *understanding* why it takes that structure? Does the distinction matter for science?

*Hint:* Think about what you would need to know to *design* a protein with a specific shape, rather than just predict the shape of an existing one. Prediction lets you look up an answer; understanding lets you derive new answers. For drug discovery, does it matter whether you understand *why* a protein binds to a drug molecule, or is knowing *that* it binds sufficient?

**Question 2.** AlphaFold finds a pattern (the mapping from amino acid sequence to 3D structure) without providing a mechanistic explanation. What is the difference between finding a pattern and explaining why it exists? Give an example from another domain where finding a pattern was useful even without a complete explanation.

*Hint:* In the 1800s, doctors noticed that handwashing reduced surgical mortality (a pattern), decades before germ theory explained *why*. The pattern was useful even without the explanation. Can you think of a situation where acting on AlphaFold's predictions without understanding the mechanism could cause a problem? What would happen if a drug candidate looked good based on predicted structure but the mechanism made it dangerous in ways the structure prediction didn't capture?

**Question 3.** Identify one scientific domain *not* listed in the table where AI has not yet made major inroads. Hypothesize at least two reasons why AI has been slower to impact that domain; consider data availability, interpretability requirements, validation difficulty, or regulatory constraints.

*Hint:* Consider domains like: theoretical mathematics (proving theorems requires not just getting the right answer but showing every step of the proof rigorously), longitudinal epidemiology (studying how diseases develop over decades requires data that doesn't exist yet), or ethnography (qualitative social science relies on human presence and relationship-building in ways that are hard to replicate). Pick one and give two specific reasons AI has been slow to enter it.

---

Now that you have seen what AI can accomplish in scientific discovery, you are equipped to examine how these same tools introduce new reproducibility risks that the scientific community must grapple with.

## Model 2: Reproducibility, Provenance, and Trust

Science depends on reproducibility: an experiment should be replicable by an independent team. AI introduces new reproducibility challenges on top of existing ones.

Think about what reproducibility means in traditional science: you publish your method, your data, and your results, and another lab follows your method with their own data and sees if they get the same answer. Now imagine the "method" includes a prompt sent to a model that may have been updated, retrained, or deprecated by the time the second lab tries to replicate. The very instrument you used has changed. That is a new class of reproducibility problem that science has never faced before.

The **reproducibility crisis** in science (particularly in psychology and biomedicine) was already severe before AI: researchers found that many published findings could not be replicated. Contributing causes include **p-hacking** (testing many hypotheses and reporting only the significant ones), **publication bias** (journals preferring positive results), and the **garden of forking paths** (many defensible analytical choices that each slightly bias results).

AI adds three new dimensions to this crisis:

| Reproducibility Risk | What Goes Wrong | How to Detect | How to Mitigate | Real Example |
|---------------------|-----------------|---------------|-----------------|--------------|
| **Training data contamination** | Test data appears in the training corpus; the model "memorized" answers rather than learned to generalize; benchmark scores are artificially inflated beyond what genuine capability would produce | Check for statistical overlap between training data and benchmark test sets; use evaluation sets that were held out and never publicly released; test on problems released after the model's training cutoff | Time-based train/test splits (train on data before date X, test on data after); independent benchmark curation by parties without access to training data; model auditing by third parties | Multiple MMLU benchmark studies found evidence that top-scoring models had seen MMLU questions during training |
| **Prompt sensitivity** | Slightly rewording a prompt produces substantially different outputs; results published in a paper may not reproduce when someone uses slightly different phrasing, even with the same model | Systematically vary prompts and report the variance across phrasings; include the exact prompt text verbatim in the methods section | Report exact prompts and model version; run multiple prompt phrasings and report variance; use standardized prompt templates; have a second researcher reproduce results with the published prompt before submission | Studies comparing GPT-4 performance on clinical questions found 10-20% variance depending on whether the question included clinical context or was phrased as abstract knowledge |
| **Stochastic output** | Same prompt plus same model produces different outputs across runs due to temperature or sampling randomness; a published result reflects one lucky or unlucky draw | Run the same prompt multiple times; report mean and variance across runs; compare deterministic (temperature=0) vs. sampled outputs | Set temperature to 0 for reproducibility-critical analyses; set and report the random seed; report the number of runs; publish all outputs, not just the best or average | A landmark AI-assisted medical imaging study did not report the number of inference runs; replication found 15% variance in classification results across runs |

> **Common Misconception:** Many students assume that using an AI tool in research is equivalent to using any other software tool: as long as you name the tool, reproducibility is satisfied. This is wrong. With traditional software (R, Python, MATLAB), running the same code on the same data gives the same result. With LLMs, the same prompt on the same model with the same data gives a *different* result every run unless you explicitly set temperature=0 and a fixed seed. And even then, model updates between submission and replication can change results. Naming the tool is necessary but not sufficient for reproducibility.

### Critical Thinking Questions

**Question 4.** A research team uses an LLM to help analyze qualitative interview data. The LLM assigns themes to each interview excerpt. Should the LLM be listed as a co-author on the resulting paper? What criteria would you use to make this decision, and how does your answer change depending on how central the LLM's contribution was?

*Hint:* Traditional authorship criteria (ICMJE guidelines) require that an author make a substantial intellectual contribution, draft or critically revise the work, approve the final version, and be accountable for all aspects of the work. An LLM cannot be held accountable, cannot approve a final version, and cannot respond to post-publication critique. But the contribution may have been substantial. How do you acknowledge the contribution honestly without misrepresenting authorship?

**Question 5.** Traditional scientific citations allow readers to look up the source. How do you cite a model that may have been retrained, updated, or deprecated between submission and publication of a paper? What information would a citation for an LLM-assisted analysis need to include to be meaningful to future readers?

*Hint:* Think about what a citation needs to accomplish: it lets readers find and verify the source. For an LLM, future readers need to know: which model (name and version), the exact prompt used, the date the analysis was run, the temperature and sampling settings, and how many runs were conducted. Is there a standard format for this? (Look up how Nature and arXiv handle LLM citations in their 2023-2024 policies.)

**Question 6.** In classical experimental science, "replication" means re-running the experiment under the same conditions. If the model used in a study is stochastic (produces different outputs each run), what does "replication" mean? Is it possible to replicate an AI-assisted study in the traditional scientific sense? What standard would you propose instead?

*Hint:* Consider proposing a new standard rather than abandoning replication. For example: "replication" for AI-assisted studies means running the exact published prompt on the exact model version (frozen, archived) and finding that the distribution of outputs across N runs overlaps substantially with the published result. What infrastructure would need to exist to make this possible: model versioning APIs, archived model weights, standardized prompt registries?

---

A research team publishes results from an LLM-assisted literature review. An independent replication team runs the same prompts six months later, using what they believe is the same model, and reaches different conclusions on several key findings. The most scientifically responsible response is:

[( )] Declare the original paper fraudulent, since the results cannot be reproduced
[( )] Ask the journal to retract the original paper until the model provider can guarantee identical outputs across all future runs of the same prompt
[(X)] Report both runs in full, document exact prompt versions and model IDs (including version dates), and rigorously analyze where and why the outputs diverged, treating the divergence itself as a scientific finding about model stability
[( )] Average the conclusions of the two runs and publish a correction

---

Understanding the reproducibility challenges of individual LLM calls sets the stage for examining what happens when those calls are chained together into a multi-step automated research pipeline.

## Model 3: The Agent as Research Assistant

Increasingly, researchers are deploying agents (not just single LLM calls) to assist with the research pipeline. A typical AI-assisted research pipeline might look like this:

1. **Literature search**: Agent queries Semantic Scholar API or PubMed for papers matching a topic
2. **Summary extraction**: Agent reads abstracts and full texts, extracts key findings, methods, and limitations
3. **Hypothesis generation**: Agent proposes new research questions or connections across papers
4. **Code generation for analysis**: Agent writes Python/R code to run statistical analyses on a dataset
5. **Result interpretation**: Agent interprets output and suggests conclusions

At every step, there are points where human judgment remains essential, and points where an undetected error could propagate silently through all downstream steps.

Think about a game of telephone: if someone mishears the first word, every person who passes it on amplifies the error. In a research pipeline, an error in step 2 (extraction) that goes undetected will corrupt step 3 (hypotheses), which will corrupt step 4 (analysis design), which will corrupt step 5 (conclusions). The earlier the error, the more damage it does. Human checkpoints between steps exist to break the telephone chain.

### Critical Thinking Questions

**Question 7.** Review the five-step pipeline above. At which step would an undetected error be most dangerous to the validity of the final result? Explain why an error at that step is particularly hard to catch and why its consequences are most severe.

*Hint:* Think about where errors are most likely to compound: a mistake in an early step that looks plausible will be silently carried forward into every downstream step. Step 2 (summary extraction) is particularly dangerous: a hallucinated finding extracted from a paper will appear to have a citation, look credible, and be built upon in step 3 and step 4 without anyone noticing it was never in the paper. How would you catch that?

**Question 8.** Imagine this pipeline is being used to assist in a systematic review for a clinical trial, a study that will inform treatment decisions for patients. What specific safeguards would you add at each step of the pipeline to ensure the integrity of the review? Be concrete: name at least one safeguard per step.

*Starter hint:* Step 1: Have a human reviewer verify that the search query returns the expected set of known landmark papers before proceeding. Step 2: Randomly sample 10% of extracted findings and verify them against the source document manually. Step 3: Have domain experts assess whether proposed hypotheses are clinically plausible before proceeding to analysis. Step 4: Run the generated code on synthetic data with known answers before running it on real data. Step 5: Have a statistician independently review the agent's interpretation before it is included in the review. Now fill in the remaining gaps and refine these starting points.

*You've succeeded when:* Each of the five pipeline steps has at least one specific, named safeguard, not just "have a human review it" but what specifically the human reviews, what they check against, and what happens if they find a problem.

**Question 9.** Design a "reproducibility protocol" for AI-assisted research. Describe exactly three steps a researcher must take (at the time of conducting the research, not at publication) to ensure that another team could reproduce their AI-assisted findings five years later. Each step should be specific and actionable.

*Starter hint:* Step 1 (at research time): Create a frozen snapshot; record the exact model name, version identifier, API endpoint, temperature, seed, and the date of every API call in a structured log file. Step 2 (at research time): Store all raw LLM outputs (not just the summaries you used) in a version-controlled repository so the full distribution of outputs is available for reanalysis. Step 3 (at research time): Run a mini-replication immediately; re-run your key prompts with temperature=0 three times and document any variance before you finalize your conclusions. Now refine these into a protocol another researcher could follow without further guidance.

---

## Exercises

**Exercise 1: LLM Summary Accuracy Audit**

*What to do:* Choose a paper in a domain that interests you (biology, chemistry, psychology, economics, etc.) and use a publicly accessible LLM to generate a summary of its abstract. Read the abstract yourself and compare carefully. Identify at least two factual errors, omissions, or distortions in the AI-generated summary.

*Starter hint:* Use Google Scholar to find a recent paper with an accessible abstract. Paste the abstract into an LLM and ask: "Summarize the key findings, methods, and limitations of this abstract." Then read the original abstract sentence by sentence, checking each claim in the AI summary. Look specifically for: numbers that are wrong or imprecise, claims that weren't in the abstract, limitations that were omitted, and conclusions that go beyond what the abstract actually said.

*You've succeeded when:* You have a table with at least two rows in this format: (a) the AI's claim, (b) what the paper actually says, (c) the type of error (fabrication, omission, misattribution, oversimplification), and a one-sentence explanation of why each error matters for a researcher relying on the summary.

**Exercise 2: Provenance Record Design**

*What to do:* Design a five-step provenance record for an AI-assisted experiment. For each step, specify: (a) what information must be logged, (b) when it must be logged (before, during, or after the step), and (c) in what format it should be stored so it is both human-readable and machine-parseable.

*Starter hint:* Think about what a future auditor would need to reproduce your work. For model calls: the model name and version, the exact prompt (verbatim, not paraphrased), the temperature and seed settings, the timestamp, and the full raw output. For human decisions: who made the decision, when, and what criteria they used. Consider using JSON for machine-parseability alongside a plain-English summary. What fields would your JSON record include for a single LLM API call?

*You've succeeded when:* Your provenance record has five steps, each with all three elements specified, and a sample JSON snippet showing what the log entry for at least one step would look like.

**Exercise 3: AlphaFold Prediction vs. Explanation Analysis**

*What to do:* Read the abstract of Jumper et al. (2021) "Highly accurate protein structure prediction with AlphaFold" (*Nature*, 596, 583-589). Write a 150-200 word analysis distinguishing: (a) what biological *insight* the paper claims to provide, (b) what it only *predicts* without explaining, and (c) what scientific questions about protein biology it leaves unanswered.

*Starter hint:* The abstract is freely available at nature.com. When reading it, ask: Does the paper claim to explain *why* proteins fold the way they do, or only to predict *what* shape they take? Does it address protein dynamics (how the shape changes over time), or only static structure? Does it explain how mutations in amino acid sequence affect folding, or only predict the folded shape of a given sequence? Each of these is a boundary between prediction and explanation.

*You've succeeded when:* Your analysis has clearly separated (a), (b), and (c) with specific examples from the abstract for each, and your conclusion addresses whether the prediction-without-explanation limitation matters for any specific downstream scientific or medical application.

---

## Reflection Prompt

**Personal level:** Have you ever used an AI tool to help with a research task (summarizing a source, finding information, or checking facts) and then discovered the AI got something wrong? Looking back, was the error a hallucination, an omission, or a distortion? What would a provenance protocol have made easier to detect?

**Technical level:** AI can identify patterns in data that no human could find by reading papers or running experiments at human speed. AlphaFold found the pattern from sequence to structure across hundreds of millions of proteins. Does the ability to find patterns at that scale make AI a *good scientist*? Consider what science requires beyond pattern-matching: hypothesis formation, mechanistic explanation, experimental design, peer review, and the ability to know when you are wrong.

**Societal level:** If AI-assisted research produces results that turn out to be wrong (because of prompt sensitivity, data contamination, or undetected hallucination), who is responsible? The researchers who used the tool? The company that built it? The journal that published it without requiring reproducibility checks? What institutional changes to peer review and publication standards would you propose to address AI-specific reproducibility risks?

-> Coming Up Next: In the Agent Economics activity, we will look at the financial and market forces that shape which AI tools get built, how they are priced, and what incentives those economics create for the companies that deploy them.

---

## Further Reading

- Jumper, J., Evans, R., et al. (2021). "Highly accurate protein structure prediction with AlphaFold." *Nature*, 596, 583-589.
- Nature editorial (2023). "Tools such as ChatGPT threaten transparent science; here are our ground rules for their use." *Nature*, 613, 612.
- Kapoor, S., and Narayanan, A. (2023). "Leakage and the Reproducibility Crisis in ML-based Science." *Patterns*, 4(9).
- Ioannidis, J. P. A. (2005). "Why Most Published Research Findings Are False." *PLOS Medicine*, 2(8).
- Merchant, A., et al. (2023). "Scaling deep learning for materials discovery." *Nature*, 624, 80-85. [GNoME paper]
- Singhal, K., et al. (2023). "Large language models encode clinical knowledge." *Nature*, 620, 172-180. [Med-PaLM 2]
