<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-benchmarking.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Benchmark Design: How We Know If AI Systems Work

CS357 - Foundations of Artificial Intelligence / Agentic AI | Ursinus College

---

## POGIL Roles

This activity uses the **POGIL** (Process Oriented Guided Inquiry Learning) structure. Assign one role to each group member before beginning.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the group on task, monitors time, ensures everyone contributes, and moves the group to the next question when ready |
| **Recorder** | Writes down the group's agreed answers and keeps a record of key decisions and reasoning |
| **Spokesperson** | Presents the group's answers during class discussion and asks the instructor clarifying questions on behalf of the group |
| **Reflector** | Monitors group process, notes what is working and what is not, and leads the end-of-activity reflection |

> Rotate roles across activities so everyone practices each one.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Benchmark** | A standardized test used to measure a specific AI capability — not unlike a standardized exam for students, but for models | MMLU tests knowledge across 57 academic subjects; HumanEval tests Python code generation from docstrings |
| **Benchmark Saturation** | When state-of-the-art models score so high on a benchmark that it no longer distinguishes between them — like a class where everyone gets 100% so the test tells you nothing about who is best | Frontier models now score above 90% on MMLU, making it nearly useless for comparing top models |
| **Benchmark Contamination** | When the test questions appeared in a model's training data, so high scores reflect memorization rather than genuine ability | HumanEval examples have been found in common pretraining corpora, inflating coding benchmark scores |
| **Inter-Rater Reliability** | The degree to which two independent human annotators agree on the correct answer for benchmark items — low agreement means the items are ambiguous or subjective | If two experts only agree 55% of the time on whether an answer is "safe," the benchmark items need revision |
| **Ecological Validity** | How well a benchmark's tasks reflect what the AI system actually needs to do in the real world | A benchmark that tests multiple-choice medical knowledge may have low ecological validity for a system that must write clinical notes |
| **LLM-as-Judge** | Using a language model to score other language models' outputs automatically, instead of (expensive) human evaluation | Using GPT-4 to rate whether a student-facing chatbot's explanation is accurate and age-appropriate |

---

## Model 1: What Makes a Good Benchmark?

A benchmark that frontier models ace is like a test that everyone gets 100% on — it no longer measures anything. This is the central problem of modern AI evaluation: our best models are improving faster than we can design meaningful tests. At the same time, a benchmark that is too hard or too narrow may fail for different reasons — it may measure the wrong things, or measure the right things in the wrong way. Designing a good benchmark is genuinely difficult, and understanding why helps you use benchmark results more skeptically and critically.

A **benchmark** is a standardized test used to measure AI system capability. Not all benchmarks are equally trustworthy. A good benchmark has five key properties:

1. **Validity** — It actually measures the capability we care about, not a proxy or shortcut that happens to correlate with performance on easy examples.
2. **Reliability** — It produces consistent results across repeated evaluations of the same system.
3. **Coverage** — It spans the target domain broadly enough to be representative of real-world variation in that domain.
4. **Difficulty Calibration** — It is not so easy that all systems score near 100%, nor so hard that all systems score near 0%. A well-calibrated benchmark spreads scores across a useful range.
5. **Contamination Resistance** — The test data was not seen during model training, so scores reflect genuine capability rather than memorization of test answers.

### Historical Benchmarks and Saturation

Over time, frontier AI models have scored so highly on once-challenging benchmarks that those benchmarks are no longer informative for comparing leading systems. This is called **benchmark saturation**.

| Benchmark | What It Measures | Year Released | Approximate Frontier Model Score | Why Scores Are No Longer Informative |
|-----------|-----------------|---------------|----------------------------------|--------------------------------------|
| **ImageNet** | Visual object classification across 1,000 categories | 2009 | 99%+ accuracy on the standard test set | Effectively solved; top models have surpassed human-level performance for years |
| **MMLU** | Multidisciplinary knowledge spanning 57 academic subjects from medicine to law to history | 2020 | Above 90% for leading models | Near-saturation and suspected training contamination make it unreliable for distinguishing top systems |
| **HumanEval** | Python code generation from function docstrings, verified by running test cases | 2021 | Above 95% for leading code models | Examples appear in pretraining corpora; scores likely inflated by memorization |
| **MATH** | Competition-level mathematics problems requiring multi-step symbolic reasoning | 2021 | 70–90% for leading models | Partial saturation; the hardest problems remain challenging but easier problems are saturated |
| **BIG-Bench** | Over 200 diverse tasks designed to exceed model capabilities at release time | 2022 | Mixed — hardest tasks remain; many easier tasks saturated | Designed as a "living" benchmark but still subject to contamination as corpora grow |

### Critical Thinking Questions

**Question 1.** Frontier models now score above 90% on MMLU, which covers 57 academic subjects from medicine to law to history. Does that mean AI systems understand most things humans know? What are at least two specific reasons the score might overstate actual understanding?

[[___ Your answer here ___]]

> *Hint:* MMLU is multiple-choice — there are only four answer options for each question. A model can score around 25% by random guessing, and higher scores can come from recognizing patterns in answer choices or from memorizing the specific phrasing of questions that appeared in training data. Think about the difference between getting a multiple-choice question right and actually being able to explain the concept, apply it to a new situation, or recognize when it doesn't apply. What would a question look like that a model could ace on MMLU but completely fail in a real clinical or legal context?

---

**Question 2.** What is "benchmark contamination," and why is it especially difficult to prevent when training data is collected from the internet at scale?

[[___ Your answer here ___]]

> *Hint:* Benchmark contamination happens when the test questions (or very similar questions) appear somewhere in the model's training data. The model then "answers" by recalling the answer rather than by reasoning. The internet is enormous and constantly indexed by crawlers used for training data: academic benchmark papers are posted on arXiv, test questions are discussed on Reddit, answers are posted on Hugging Face forums. Even a benchmark released after a model's training cutoff may have had its items written and shared informally before that date. How would you detect whether contamination has occurred for a specific benchmark?

---

**Question 3.** Name one cognitive skill or real-world capability that you consider important for an AI agent and that you believe no existing published benchmark adequately tests. Explain specifically why existing benchmarks miss it.

[[___ Your answer here ___]]

> *Hint:* Think about capabilities that matter for the agents you've built in this course: knowing when to stop and ask for clarification instead of proceeding with an assumption, recognizing when a tool call failed silently rather than loudly, or calibrating confidence appropriately (saying "I'm not sure" when genuinely uncertain rather than generating a confident-sounding wrong answer). How would you design a benchmark item that tests one of these capabilities? What makes it hard to create ground-truth labels for?

---

## Model 2: Designing Your Own Benchmark

Creating a valid benchmark requires more than writing a list of questions. The following six-step process helps ensure benchmark quality — and each step can fail in a way that invalidates the results.

**Step 1 — Define the capability:** State in precise, testable terms what you are measuring. "Common sense" is too vague to design items for. "Detecting when a stated action violates an unstated social norm in a given cultural context" is specific enough that two independent researchers could agree on whether a given item tests it.

**Step 2 — Choose the instance format:** Multiple choice, free response, code generation, ranking, binary classification. Each format has tradeoffs: multiple choice is easy to score automatically but susceptible to option-elimination strategies; free response has higher ecological validity but requires expensive human evaluation or an LLM judge.

**Step 3 — Write instances with known answers:** Every item needs a ground-truth answer that does not depend on the model's output. For subjective items, collect independent human judgments and use majority vote or expert review.

**Step 4 — Calibrate difficulty:** Aim for a spread of difficulty: approximately 20–30% easy items, 40–50% medium items, and 20–30% hard items. Pilot with human participants to calibrate before finalizing — what feels hard to the researcher may be trivial to the model or vice versa.

**Step 5 — Establish inter-rater reliability:** Have multiple independent humans answer every item. If humans disagree frequently on a given item, the item is ambiguous and should be revised or removed. Inter-rater agreement is typically measured with Cohen's kappa (κ) or percent agreement; κ below 0.6 is generally considered insufficient for a published benchmark.

**Step 6 — Resist contamination:** Do not publish the test set in its entirety. Release training and validation splits publicly for model development; keep the test split private. Release only aggregate scores, not per-item results, to prevent reverse-engineering of the test items.

### Common Bias Traps in Benchmark Design

- **Selection bias:** Items are drawn from a narrow slice of the domain — for example, a "global knowledge" benchmark built primarily from Western English-language news sources systematically underrepresents non-Western knowledge.
- **Cultural specificity:** Correct answers assume cultural knowledge or social norms that are not universal across the populations that will use the AI system.
- **Language complexity confound:** Items that test reading difficulty rather than the target capability — a model that fails a medical knowledge question because of complex sentence structure, not because it lacks medical knowledge, is telling you something about language processing, not domain knowledge.

> ⚠️ **Common Misconception:** Many people treat published leaderboard rankings as objective ground truth about which AI system is "best." In practice, every benchmark embeds assumptions about what matters, what counts as correct, and whose knowledge and values define the right answer. A model that ranks first on HumanEval may rank fifth on a benchmark of multi-turn agent behavior. A model that aces MMLU may be significantly outperformed on tasks requiring careful uncertainty calibration. Benchmark rankings tell you about performance on *that specific benchmark under those specific conditions* — not about general intelligence or real-world usefulness.

### Critical Thinking Questions

**Question 4.** You want to benchmark an AI agent's ability to "understand safety constraints." That phrase is ambiguous in several ways. Describe how you would turn it into a concrete, testable benchmark. What specific behaviors would your instances probe, and how would you write items that have clear ground-truth answers?

[[___ Your answer here ___]]

> *Hint:* Break "safety constraints" into specific testable behaviors: refusing a clearly harmful request, correctly identifying when a borderline request falls within or outside stated guidelines, gracefully declining and explaining why rather than silently failing, not being tricked by rephrasing or role-play framing. For each behavior, write a concrete item: an input prompt, and the ground-truth answer (does the agent comply or refuse, and does it give a good explanation?). How do you handle cases where experts disagree on whether the request is harmful?

---

**Question 5.** What is inter-rater reliability and why does it matter for benchmark validity? If two independent human annotators agree on only 60% of your benchmark items when labeling the correct answer, what does this tell you about those items? What should you do about it?

[[___ Your answer here ___]]

> *Hint:* Inter-rater reliability measures how consistently independent people assign the same label to the same item. If two annotators only agree 60% of the time, it means the items are ambiguous — the "correct" answer depends on interpretation rather than on objective fact. This is a problem because: (1) the ground-truth labels may be wrong for some items; (2) different runs of the benchmark may give different scores to the same model depending on which annotator's label was used; (3) a model that "fails" these items may simply have chosen a different but equally valid interpretation. What do you do — revise the ambiguous items, add a third annotator to break ties, or remove the items entirely?

---

**Question 6.** For an adversarial robustness benchmark (where the agent is tested on prompts specifically designed to cause failures), what would a "floor" item look like? What would a "ceiling" item look like? Why does having both matter for a useful benchmark?

[[___ Your answer here ___]]

> *Hint:* A floor item is one that even a weak or poorly-configured agent should handle correctly — if an agent fails this, you know it has a fundamental capability gap rather than just an adversarial robustness problem. A ceiling item is one that even the best current system struggles with. Without floor items, you cannot distinguish a badly-broken agent from one that is simply not robust to sophisticated attacks. Without ceiling items, you cannot measure room for improvement. How would you write a concrete floor item and a concrete ceiling item for adversarial robustness in the context of an agent that should refuse harmful requests?

---

### Multiple Choice Question

A benchmark is released publicly with all test examples included in the paper and available for download. After one year, state-of-the-art models score 97% on it. The most important caveat when interpreting this result is:

[[ ]] Benchmark difficulty is fixed at design time — a 97% score proves the benchmark was always trivially easy, not that models improved through contamination or genuine capability gains
[[ ]] A state-of-the-art score on a benchmark means the underlying real-world capability has been fully solved — leaderboard performance directly predicts deployment quality in production
[[x]] Models may have been trained on or fine-tuned using the published test examples, artificially inflating scores beyond what genuine capability would achieve
[[ ]] The 3% failure rate is evenly distributed across all input categories — a 97% average accuracy implies the system is reliably correct for every subgroup and edge case

> **Why this answer?** When a benchmark is published with all test examples publicly available, those examples can appear in the training data of future models — either in the original pretraining corpus if the paper predates the training cutoff, or through deliberate fine-tuning on benchmark items. A 97% score on a contaminated benchmark tells you the model is good at answering those specific questions, not that it has genuinely mastered the underlying capability. The benchmark has become a memorization test rather than a capability test.

---

## Model 3: Evaluation Beyond Accuracy

Accuracy on a benchmark is one signal, but it is rarely sufficient on its own for making real-world deployment decisions. Real-world AI evaluation combines multiple methods, each with distinct strengths and failure modes.

### Human Evaluation

Human evaluators assess model outputs directly. Common formats:

- **Pairwise preference:** Show two model responses side by side; ask a human evaluator which is better. Used extensively in RLHF training and in platforms like Chatbot Arena (lmsys.org). Pairwise judgments are more reliable than absolute ratings because they avoid the anchoring effects of rating scales.
- **Likert scales:** Rate output on a 1–5 scale across multiple dimensions such as helpfulness, safety, and fluency. Useful for profiling multiple quality dimensions at once.
- **Task completion rate:** Give a human evaluator a goal and have them use the agent to achieve it; measure whether they succeed within a given number of turns. High ecological validity.

**Strengths:** Captures qualities that automatic metrics miss — tone, appropriateness, safety edge cases that don't trigger keyword filters, and the genuine usefulness of an answer in context.

**Limitations:** Expensive (professional evaluators cost $10–50 per hour), slow (days to weeks for large-scale studies), subject to annotator bias, and inconsistent across annotators and over time as annotator pools and guidelines evolve.

### Automatic Evaluation Metrics

| Metric | What It Measures | Key Blind Spot | When to Use It |
|--------|-----------------|----------------|----------------|
| **BLEU** | N-gram word overlap between the model's output and a reference answer | Does not capture meaning; penalizes valid paraphrases heavily | Machine translation as a rough filter; not suitable for open-ended generation |
| **ROUGE** | Recall-oriented n-gram overlap, common in summarization evaluation | Same blind spot as BLEU — surface overlap, not semantic accuracy | Summarization pipeline monitoring as a sanity check |
| **BERTScore** | Semantic similarity using contextual embeddings rather than exact word matches | Can miss factual errors; two sentences can be semantically similar but factually opposite | More reliable than BLEU/ROUGE for generation quality; still misses factual accuracy |
| **G-Eval / LLM-as-Judge** | A language model scores another model's output on a defined rubric | Inherits the judge model's biases, blind spots, and style preferences; expensive per evaluation | Rapid large-scale evaluation when human evaluation budget is limited |

### Live / Production Evaluation

- **Canary queries** (hidden "decoy" test prompts inserted silently into live production traffic to catch quality regressions before users notice them): Fixed test prompts inserted into real production traffic anonymously and regularly. The agent's response to each canary is automatically scored. Catches quality regressions before they affect large numbers of real users.
- **A/B testing:** Route a fraction of real users (say, 5%) to a new model version and the rest to the current version; compare outcome metrics such as task completion rate, escalation rate (how often users give up and contact a human), and explicit feedback (thumbs up/down).

### Critical Thinking Questions

**Question 7.** When is human evaluation worth the extra cost and time compared to automatic metrics? Describe a specific, concrete scenario where relying solely on automatic metrics would give a dangerously misleading assessment of agent quality.

[[___ Your answer here ___]]

> *Hint:* Consider an agent that produces outputs that score well on BERTScore (semantically similar to reference answers) but that are subtly wrong in a dangerous way — for example, a medical information agent that correctly identifies the drug name but gives the wrong dosage, or a legal information agent that correctly identifies the relevant law but misapplies it to the user's specific situation. BERTScore would rate these outputs highly because they contain the right words in roughly the right semantic neighborhood. What would a human evaluator catch that BERTScore misses?

---

**Question 8.** An agent achieves 90% accuracy on your benchmark but receives poor user satisfaction ratings (2.1 out of 5 stars) in production. Name at least two explanations for this gap. What would you investigate first, and what data would help you diagnose the specific cause?

[[___ Your answer here ___]]

> *Hint:* Possible explanations include: (1) the benchmark tests a different capability than what users actually need in production — the benchmark was valid for development but lacks ecological validity; (2) the benchmark has single-turn items but production requires multi-turn dialogue; (3) the 90% accuracy hides a systematic failure on the specific types of queries most common in production; (4) the agent is technically correct but communicates in a way that users find unhelpful (too verbose, too terse, wrong tone). Start by looking at the specific queries where users rated the agent poorly and comparing them to the benchmark item distribution — are those failure cases well-represented in the benchmark?

---

**Question 9.** Design a three-metric evaluation plan for a coding agent that helps students debug Python programs. For each metric, specify: (a) exactly what it measures, (b) how it is collected (automatically, through human review, or through user interaction), and (c) what score or threshold would trigger a concern serious enough to halt deployment.

[[___ Your answer here ___]]

> *Hint:* Consider three different layers: (1) A correctness metric — does the agent's suggested fix actually make the student's code pass its test cases? This can be verified automatically by running the suggested code in a sandbox. (2) A pedagogical quality metric — does the agent explain *why* the fix works, not just what to change? This likely requires human evaluation or an LLM judge with a rubric. (3) A safety / harm-avoidance metric — does the agent avoid simply writing the complete solution for the student (undermining learning) while still being helpful enough to be useful? What threshold on each metric would make you say "this agent is not ready for students"?

---

## Exercises

**Exercise 1.**

*What to do:* Write 10 benchmark instances for one specific capability of an agent you have built or designed in this course. Each instance needs an input, a ground-truth answer, a difficulty label (easy, medium, or hard), and a one-sentence justification of the difficulty rating. Aim for 3 easy, 4 medium, and 3 hard items.

*Starter hint:* Choose a narrow, specific capability — not "can the agent answer questions" but something like "can the agent correctly identify when a tool call has returned an error rather than a valid result" or "can the agent recognize when a user question is ambiguous and ask for clarification rather than assuming." Narrow capabilities are easier to write clear ground-truth labels for.

*You've succeeded when:* You have 10 complete instances with inputs, ground-truth answers, difficulty labels, and justifications. Share your hardest item with another group and see if they agree on the ground-truth answer — if they don't, you've found an inter-rater reliability problem to fix.

---

**Exercise 2.**

*What to do:* Run your 10 benchmark instances through a real AI agent (API-based or local model). Record the agent's response to each instance and score it against your ground-truth answer. Compute the accuracy score. Then identify at least one pattern in the failures.

*Starter hint:* Be consistent in your scoring: decide in advance exactly what counts as correct (exact match, semantic equivalence, partial credit?). After scoring, look at the wrong answers as a group — do they share a common property? Are all the wrong answers on medium-difficulty items? Are they all the same type of error (misidentifying the tool status, always asking for clarification even when the question is clear)? A pattern suggests a systematic capability gap rather than random noise.

*You've succeeded when:* You have a scored result for all 10 items, a computed accuracy percentage, and a written paragraph describing at least one specific pattern in the failures and your hypothesis about what capability gap it reveals.

---

**Exercise 3.**

*What to do:* Find a published benchmark that has been publicly criticized for contamination, cultural bias, or saturation. Suggested starting points: MMLU (training contamination concerns), HellaSwag (cultural and linguistic specificity), WinoGrande (annotation artifacts), GSM8K (arithmetic memorization concerns), or find your own through a web search.

*Starter hint:* Search for "[benchmark name] contamination critique" or "[benchmark name] cultural bias" on Google Scholar or in AI conference proceedings. The NeurIPS Datasets and Benchmarks track often publishes critiques. Also check if the original benchmark paper has received response papers or if the original authors have posted follow-up work acknowledging limitations.

*You've succeeded when:* Your response summarizes: (a) the specific criticism with at least one concrete example of the problem; (b) any response from the original authors or the broader research community; and (c) whether a successor benchmark has been proposed and specifically how it addresses the identified problem. Include at least two cited sources.

---

## Reflection Prompt

**Personal:** Think about a standardized test you have taken — a school exam, the SAT or ACT, a driver's license test. Did it accurately measure what you actually know or can do? What did it miss? Now apply the same critical lens to AI benchmarks: what might a benchmark miss about what an AI system is actually capable of — or incapable of?

**Technical:** Every benchmark embeds assumptions about what intelligence is, what tasks matter, whose knowledge counts, and what "correct" means. These assumptions are made by the researchers who design the benchmark, who have their own cultural contexts, disciplinary training, and institutional incentives. What would it mean to design a benchmark that is genuinely fair across different cultures, languages, and domains? Is that achievable?

**Societal:** What happens if AI systems are primarily evaluated on benchmarks designed by a small group of researchers at large technology companies? Whose priorities get encoded in those benchmarks? What capabilities get optimized for, and what capabilities get ignored? Who should have a voice in deciding what goes into the benchmarks that shape AI development?

Write at least 200 words addressing at least two of the three levels above. Your Reflector should be prepared to share your group's key idea during class discussion.

[[___ Your reflection here ___]]

---

→ Coming Up Next: In the next activity, we move from evaluating agents in controlled tests to debugging them when they fail in the wild — a very different and more difficult problem.

## Further Reading

- Liang, P. et al. "Holistic Evaluation of Language Models" (HELM, 2022). Stanford CRFM. Introduces a comprehensive framework for multi-metric, multi-scenario LLM evaluation that goes beyond single-number accuracy scores.

- Srivastava, A. et al. "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-Bench, 2022). Proposes 204 diverse tasks specifically designed to resist saturation; includes discussion of contamination controls.

- Raji, I. D. et al. "AI and the Everything in the Whole Wide World Benchmark" (NeurIPS 2021 Datasets and Benchmarks Track). A critical examination of how benchmark design choices shape what AI systems are built and optimized to do.

- Hendrycks, D. et al. "Measuring Massive Multitask Language Understanding" (MMLU, 2020). The original MMLU paper — read alongside subsequent critiques and contamination analyses for a complete picture of its strengths and limitations.
