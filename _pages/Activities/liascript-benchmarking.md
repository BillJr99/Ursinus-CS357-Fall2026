# Benchmark Design: How We Know If AI Systems Work

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-benchmarking.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

## POGIL Roles

This activity uses the POGIL (Process Oriented Guided Inquiry Learning) structure. Assign one role to each group member before beginning.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the group on task, monitors time, ensures everyone contributes, moves the group to the next question when ready |
| **Recorder** | Writes down the group's agreed answers, keeps a record of key decisions and reasoning |
| **Spokesperson** | Presents the group's answers during class discussion, asks the instructor clarifying questions on behalf of the group |
| **Reflector** | Monitors group process, notes what is working and what is not, leads the end-of-activity reflection |

---

## Model 1: What Makes a Good Benchmark?

A **benchmark** is a standardized test used to measure AI system capability. Not all benchmarks are equally trustworthy. A good benchmark has five key properties:

1. **Validity** — It actually measures the capability we care about, not a proxy or shortcut.
2. **Reliability** — It produces consistent results across repeated evaluations.
3. **Coverage** — It spans the target domain broadly enough to be representative.
4. **Difficulty Calibration** — It is not so easy that all systems score near 100%, nor so hard that all systems score near 0%.
5. **Contamination Resistance** — The test data was not seen during model training, so scores reflect genuine capability rather than memorization.

### Historical Benchmarks and Saturation

Over time, frontier AI models have scored so highly on once-challenging benchmarks that those benchmarks are no longer informative. This is called **benchmark saturation**.

| Benchmark | What It Measures | Year Released | Frontier Model Score (approx.) | Why Scores Are No Longer Informative |
|-----------|-----------------|---------------|-------------------------------|--------------------------------------|
| **ImageNet** | Visual object classification | 2009 | 99%+ accuracy | Effectively solved; human-level performance surpassed |
| **MMLU** | Multidisciplinary knowledge (57 subjects) | 2020 | >90% | Saturation and suspected training contamination |
| **HumanEval** | Python coding from docstrings | 2021 | >95% | Examples appear to be present in pretraining corpora |
| **MATH** | Competition mathematics | 2021 | ~70–90% | Specialized reasoning; partial saturation with large models |
| **BIG-Bench** | 200+ diverse tasks | 2022 | Partially challenging | Hardest tasks remain; easier tasks saturated |

### Critical Thinking Questions

**Question 1.** Frontier models now score above 90% on MMLU, which covers 57 academic subjects from medicine to law to history. Does that mean AI systems understand most things humans know? What are at least two reasons the score might overstate actual understanding?

[[___ Your answer here ___]]

**Question 2.** What is "benchmark contamination," and why is it especially difficult to prevent when training data is collected from the internet at scale?

[[___ Your answer here ___]]

**Question 3.** Name one cognitive skill or capability you consider important that you believe no existing benchmark adequately tests. Explain why existing benchmarks miss it.

[[___ Your answer here ___]]

---

## Model 2: Designing Your Own Benchmark

Creating a valid benchmark requires more than writing a list of questions. The following six-step process helps ensure benchmark quality.

**Step 1 — Define the capability:** State in precise terms what you are measuring. "Common sense" is too vague. "Detecting when a stated action violates an unstated social norm in a given cultural context" is specific enough to design items for.

**Step 2 — Choose the instance format:** Multiple choice, free response, code generation, ranking, binary classification. Each has tradeoffs for automatic scoring vs. ecological validity.

**Step 3 — Write instances with known answers:** Every item needs a ground-truth answer that does not depend on the model's output. For subjective items, collect human judgments.

**Step 4 — Calibrate difficulty:** Aim for a spread: approximately 20–30% easy items, 40–50% medium items, 20–30% hard items. Pilot with humans to calibrate.

**Step 5 — Establish inter-rater reliability:** Have multiple independent humans answer every item. If humans disagree frequently, the item is ambiguous and should be revised or removed. Inter-rater agreement is typically measured with Cohen's kappa or percent agreement.

**Step 6 — Resist contamination:** Do not publish the test set. Publish the training and validation splits publicly; keep the test split private. Release only aggregate scores, not per-item results.

### Common Bias Traps in Benchmark Design

- **Selection bias:** Items are drawn from a narrow slice of the domain (e.g., Western news sources for a "global knowledge" benchmark).
- **Cultural specificity:** Correct answers assume knowledge or norms that are not universal.
- **Language complexity confound:** Items that test language difficulty rather than the target capability — high reading level masks whether a model actually knows the content.

### Critical Thinking Questions

**Question 4.** You want to benchmark an agent's ability to "understand safety constraints." That phrase is ambiguous. Describe how you would turn it into a concrete, testable benchmark. What specific behaviors would your instances probe?

[[___ Your answer here ___]]

**Question 5.** What is inter-rater reliability and why does it matter for benchmark validity? If two human annotators agree 60% of the time on your benchmark items, what does that suggest about the items?

[[___ Your answer here ___]]

**Question 6.** For an adversarial robustness benchmark (where the agent is tested on prompts designed to cause failures), what would a "floor" item look like? What would a "ceiling" item look like? Why does having both matter?

[[___ Your answer here ___]]

### Check Your Understanding

A benchmark is released publicly with all test examples included in the paper. After one year, state-of-the-art models score 97%. The most important caveat when interpreting this result is:

- ( ) The benchmark must have been too easy from the start
- ( ) All AI problems in this domain are now solved
- (x) Models may have been trained on or fine-tuned using the published test examples, artificially inflating scores
- ( ) A 97% score means the remaining 3% of failures are unimportant

---

## Model 3: Evaluation Beyond Accuracy

Accuracy on a benchmark is one signal, but it is rarely sufficient. Real-world AI evaluation uses a combination of methods.

### Human Evaluation

Human evaluators assess model outputs directly. Common formats:

- **Pairwise preference:** Show two responses; ask which is better. Used in RLHF and in Chatbot Arena.
- **Likert scales:** Rate on a 1–5 scale across dimensions (helpfulness, safety, fluency).
- **Task completion rate:** Give a human a goal; have them use the agent; measure whether they succeed.

**Strengths:** High ecological validity; captures qualities automatic metrics miss (tone, safety edge cases, appropriateness).

**Limitations:** Expensive, slow, subject to annotator bias, inconsistent across annotators and over time.

### Automatic Evaluation Metrics

| Metric | What It Measures | Key Blind Spot |
|--------|-----------------|----------------|
| **BLEU** | N-gram overlap between output and reference | Does not capture meaning; penalizes paraphrase |
| **ROUGE** | Recall-oriented n-gram overlap (common in summarization) | Same blind spot as BLEU |
| **BERTScore** | Semantic similarity using embeddings | Can miss factual errors; embedding similarity ≠ factual accuracy |
| **G-Eval** | LLM-as-judge scoring on defined rubric | Inherits the judge model's biases; expensive |

### Live / Production Evaluation

- **Canary queries:** Fixed test prompts inserted into real traffic anonymously. Catches regressions before users notice.
- **A/B testing:** Route a fraction of real users to new model version; compare outcome metrics (task completion, escalation rate, thumbs-up rate).

### Critical Thinking Questions

**Question 7.** When is human evaluation worth the extra cost and time compared to automatic metrics? Describe a specific scenario where automatic metrics would give a dangerously misleading score.

[[___ Your answer here ___]]

**Question 8.** An agent achieves 90% accuracy on your benchmark but receives poor user satisfaction ratings in production. What are at least two explanations for that gap? What would you investigate first?

[[___ Your answer here ___]]

**Question 9.** Design a 3-metric evaluation plan for a coding agent that helps students debug Python programs. Specify: (a) what each metric measures, (b) how it is collected, and (c) what score would trigger concern.

[[___ Your answer here ___]]

---

## Exercises

**Exercise 1.** Write 10 benchmark instances for one specific capability of an agent you have built or designed in this course. Include 3 easy items, 4 medium items, and 3 hard items. Provide a complete answer key with the correct answer for each item. Label each item with its difficulty level and a one-sentence justification.

**Exercise 2.** Run your 10 benchmark instances through a real AI agent (can be an API-based model or a local model). Compute the accuracy score. Identify at least one pattern in the failures — what do the wrong answers have in common? What does the pattern tell you about the agent's capability gap?

**Exercise 3.** Find a published benchmark that has been publicly criticized for contamination, cultural bias, or saturation. (Suggestions: MMLU, HellaSwag, WinoGrande, GSM8K — or find your own.) Summarize: (a) the specific criticism, (b) any response from the original authors, and (c) whether a successor benchmark has been proposed and how it addresses the problem.

---

## Reflection Prompt

Every benchmark embeds assumptions — about what intelligence is, what tasks matter, whose knowledge counts, and what "correct" means. These assumptions are made by the people who design the benchmark, who have their own cultural contexts, disciplinary training, and incentives.

> **Who should decide what goes into the benchmarks that judge AI systems, and why does it matter?** Consider: what happens if AI systems are evaluated primarily on benchmarks designed by a small group of researchers at large technology companies? What perspectives might be systematically missing?

Write at least one paragraph responding to this prompt. Your Reflector should share your group's key idea during class discussion.

[[___ Your reflection here ___]]

---

## Further Reading

- Liang, P. et al. "Holistic Evaluation of Language Models" (HELM, 2022). Stanford CRFM. Introduces a comprehensive framework for multi-metric, multi-scenario LLM evaluation.

- Srivastava, A. et al. "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-Bench, 2022). Proposes 204 diverse tasks to resist saturation.

- Raji, I. D. et al. "AI and the Everything in the Whole Wide World Benchmark" (NeurIPS 2021 Datasets and Benchmarks Track). Critically examines how benchmark design choices shape what AI systems are built to optimize.

- Hendrycks, D. et al. "Measuring Massive Multitask Language Understanding" (MMLU, 2020). The original MMLU paper — read alongside subsequent critiques for a complete picture.
