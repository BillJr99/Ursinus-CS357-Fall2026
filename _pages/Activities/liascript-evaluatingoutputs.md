<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Hallucinations and Evaluating Agent Outputs

In the *Why Different Answers Every Time?  Sampling, Temperature, and Generation* activity we saw that a model samples plausible continuations, and a model that writes fluently can be fluently wrong.  This module names the phenomenon of **hallucination**, explains *why* next-token prediction produces it, and builds our first **evaluation harness**, because an agent we cannot measure is an agent we cannot trust or improve.  We move from **mechanism $\rightarrow$ taxonomy $\rightarrow$ measurement $\rightarrow$ mitigation previews**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| Hallucination | A model output that is confident and fluent but factually wrong, not a "mistake" in the human sense, but a consequence of optimizing for plausibility rather than truth | A fabricated but well-formatted academic citation complete with volume, issue, and page numbers |
| Factual hallucination | A specific type: the model asserts something about the world that is simply false, with no source document to contradict | Claiming that a real journal published a specific article that does not exist |
| Faithfulness hallucination | A specific type: the model contradicts or invents beyond a source document it was given, the type most likely to occur in retrieval-augmented systems | Summarizing a paragraph by adding a detail that was not in the original text |
| Reasoning error | A specific type: the model uses correct facts but combines them incorrectly to reach a wrong conclusion | Knowing that the speed of sound is 343 m/s but calculating travel time by multiplying instead of dividing |
| Evaluation harness | A program that runs a model on a fixed set of questions with known correct answers, computes a score automatically, and records the results in a reproducible way | The `tasks` list and scoring loop in today's code cell |
| Exact-match accuracy | A metric that scores 1 for a response containing the correct answer string and 0 otherwise, simple and objective, but strict about phrasing | Scoring "The answer is Canberra" as correct if the gold answer is "canberra" (substring match), but failing "the Australian capital" even though it is correct |

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | The three prompts you brought: triage real confidently-wrong answers, not invented ones |
| 10-25 | Part I, why models hallucinate, mechanism first |
| 25-45 | Part II, build the tiny evaluation harness |
| 45-70 | Part IIb, design the benchmark the Golden-Set Lab asks you for |
| 70-75 | Reflection prompt, and the lab handout |

---
# Part I: Why Models Hallucinate

In this part, you will learn why hallucination (a model producing confident but false output) is not a bug that can be patched, but a predictable consequence of how language models are trained, and you will build a taxonomy of three hallucination types that each call for a different fix.

## 1.  Fluency Is the Objective, Truth Is Not

Before we look at the mechanism, consider a thought experiment.  Imagine training a student to pass a writing class by rewarding them whenever their essays *sounded* like expert writing: correct grammar, confident tone, appropriate vocabulary.  That student would quickly learn to produce convincing prose even on topics they know nothing about, because the reward never checked whether the facts were true.  Language models face the same dynamic at a massive scale: they are trained to predict what text tends to follow other text, not to verify whether the claims in that text match reality.

The training objective rewards plausible continuation.  A model is optimized to maximize the probability of the next token given context, $\max \sum_t \log P(x_t \mid x_{<t})$. Nothing in that objective references truth; it references *what text tends to follow other text in the training data*.  When the context resembles confident factual writing, the most probable continuation is more confident factual-sounding text, whether or not any real fact supports it.

Hallucinations cluster where training data is thin.  Specific citations, niche biographies, exact recent statistics, and obscure local facts sit in low-density regions of the training distribution.  The model interpolates between patterns it has seen, and interpolation between facts is often fiction.  This insight predicts *where* to be suspicious, which is more useful than blanket distrust of everything a model says.

A useful taxonomy for deciding what to do about it.  *Factual hallucination*: asserting false statements about the world (fix: retrieval, tool use).  *Faithfulness hallucination*: contradicting or inventing beyond a provided source (fix: strict grounding instructions, retrieval-augmented generation).  *Reasoning error*: correct facts combined by invalid logic (fix: chain-of-thought, critique agents).  Each type calls for a different mitigation, and each mitigation is a topic in the coming weeks.

---

## Model 1: The Confident Citation

Imagine this scenario: a student asks a local model for three peer-reviewed sources on a niche topic in coastal ecology and receives the following response: "See Hartman, R. (2018).  *Tidal Dynamics of Inland Estuaries*, Journal of Coastal Research, 34(2), 211-228."  The journal exists and publishes real research.  The article does not exist.  The author name appears in the model's training data in other contexts.  Every piece of the citation looks individually plausible; that is why it is hard to catch without checking.

### Critical Thinking Questions

1.  Explain, using the training objective described above, why every *individual component* of this citation (author format, journal name, year, page range) looks plausible even though the *complete citation* is fabricated.

   > *Hint: The model has seen thousands of correctly formatted citations.  It learned what citation text looks like by pattern: author, year, title in italics, journal name, volume, issue, pages.  It can reproduce that pattern perfectly while inventing every specific value.*

2.  Which category of the hallucination taxonomy does this citation fall into: factual, faithfulness, or reasoning?  If you had given the model a PDF of real papers to read before asking for citations, would that change the category of errors you would expect?

   > *Hint: Without a source document, the model is generating from memory (or from pattern).  With a source document, any errors in summarizing that document would be faithfulness errors.  Could it still produce factual errors about the world beyond the document?*

3.  Propose a verification step that a student (or an automated agent) could run before trusting any citation.  What specific tool or data source would the agent need access to?

   > *Hint: Think about what databases index academic papers: Google Scholar, CrossRef, PubMed, Semantic Scholar.  A verification agent could call one of these APIs with the DOI or title and check whether the paper exists.  What happens if the paper exists but the page numbers are wrong?*

---

## 2.  Evaluation Foundations

To evaluate an agent we need three things: a **task set** (inputs with known correct outputs), a **metric** (a function that turns a model output and a correct answer into a score), and a **protocol** (fixed model version, parameters, and seed so that results are reproducible and comparable over time).  For factual question answering, the simplest metric is **exact-match accuracy**:

$$
\text{accuracy} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\hat{y}_i = y_i]
$$

where $\hat{y}_i$ is the model's predicted answer and $y_i$ is the known correct answer.  The indicator function $\mathbb{1}[\cdot]$ (read as "1 if the condition is true, 0 otherwise"; equivalent to Python's `int(condition)`) counts correct answers.  Exact match is intentionally harsh (a correct answer phrased differently scores zero) which previews why we will later recruit *another model* as a judge (an LLM-as-evaluator), and why we must then evaluate the judge itself.

A team reports that their agent "seems pretty accurate" after trying a few questions.  The most important missing element of a real evaluation is:

[( )] A larger language model with more parameters
[( )] Higher temperature for greater response diversity
[(X)] A fixed task set with known answers, a clearly defined metric, and a reproducible protocol with fixed model and parameters
[( )] A faster computer to run more experiments

---

# Part II: Building a Tiny Evaluation Harness

In this part, you will write a minimal evaluation harness (a program that runs a model on a fixed set of questions with known answers and reports a score), because "it seems pretty good" is not an engineering standard.  By the end, you will have a reusable scaffold for evaluating any agent you build this semester.

## 3.  Measure Before You Trust

Before we can trust an agent in a real application, we need to know where it succeeds and where it fails, not a general impression, but a number.  The code below is a minimal version of the evaluation infrastructure that underlies every published benchmark in AI research.  It is small enough to read in five minutes and powerful enough to reveal real patterns.

---

The code below runs a fixed list of five questions through the model (at temperature 0.0 and a fixed random seed so results are reproducible), checks whether the correct answer appears anywhere in the model's response, and prints a PASS or FAIL for each.  Read it carefully before running: you will be asked to critique both the scoring rule and the task set.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import requests

def chat(prompt, model="llama3.2"):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": 0.0, "seed": 42},
            "messages": [{"role": "user",
                          "content": prompt + " Respond with only the answer, no explanation."}]},
            timeout=120)
        return r.json()["message"]["content"].strip().lower()
    except Exception as e:
        print(f"[evaluating:chat] {e}")
        import traceback; traceback.print_exc()
        return ""

tasks = [
    ("What is the capital of Australia?", "canberra"),
    ("What year did the Apollo 11 mission land on the Moon?", "1969"),
    ("Who wrote the novel Frankenstein?", "mary shelley"),
    ("What is 17 * 24?", "408"),
    ("In what year was Ursinus College founded?", "1869"),
]

correct = 0
for q, gold in tasks:
    pred = chat(q)
    hit = gold in pred
    correct += hit
    print(f"{'PASS' if hit else 'FAIL'} | {q} -> {pred!r} (expected {gold!r})")

print(f"\naccuracy = {correct}/{len(tasks)} = {correct/len(tasks):.2f}")
```

---

## Model 2: Interrogating the Harness

Examine the PASS/FAIL output line by line.  Before discussing with your group, form your own hypothesis about each result: why did the model pass or fail this particular question?

### Critical Thinking Questions

4.  Our scoring rule is `gold in pred` (a substring check; it passes if the correct answer appears anywhere in the model's response).  Construct a specific model answer that is *factually wrong* yet scores as PASS, and a specific model answer that is *factually correct* yet scores as FAIL. What does this teach about the relationship between metrics and truth?

   > *Hint: For a wrong-but-PASS example: the question is "What is 17 * 24?" and the gold is "408."  What if the model outputs "408 is not actually correct; the real answer is 412"?  For a right-but-FAIL example: gold is "mary shelley" and the model outputs "Mary Wollstonecraft Shelley"; does the substring check pass?*

5.  Add two questions to the `tasks` list where you predict the model will hallucinate (based on the "thin training data" principle) and two where you predict it will answer correctly.  Run them.  Was your theory of where models fail predictive?

   > *Hint: Good hallucination-prone questions involve: specific local people or events, very recent information (post-2023), exact statistics like population figures or distances, or niche academic citations.  Good reliable questions involve: widely published historical dates, famous authors, capital cities of large countries.*

6.  We fixed temperature to 0.0 and seed to 42.  Rerun the harness once without changing any parameters and confirm you get identical results.  Then explain in one sentence each why a grader, a scientist, and a software debugger each need this reproducibility property.

   > *Hint: A grader needs it so that "running the eval again" gives the same score.  A scientist needs it so that a published result can be independently replicated.  A debugger needs it so that a bug observed in one run will appear again in the next run.*

> **Common Misconception:** Many students assume that if a model gives a wrong answer on a factual question, it "does not know" the answer and will always fail that question.  In reality, the same model with the same weights can answer the same question correctly at one temperature setting and fail it at another, or answer it differently in different phrasings of the same question.  This is why evaluation requires a *fixed protocol*, not because we distrust the model, but because the model's behavior is sensitive to parameters and phrasing, and we need to hold those constant to learn anything meaningful.

---

---

# Part IIb: Designing the Benchmark You Are About to Need

Triaging bad answers one at a time does not scale, and the Golden-Set Lab handed out today asks you to build something that does.  A benchmark is how you turn "it seems better" into a number you can defend.  This part is about designing one that measures what you actually care about.

### What Makes a Good Benchmark?

A benchmark that frontier models ace is like a test that everyone gets 100% on; it no longer measures anything.  This is the central problem of modern AI evaluation: our best models are improving faster than we can design meaningful tests.  At the same time, a benchmark that is too hard or too narrow may fail for different reasons: it may measure the wrong things, or measure the right things in the wrong way.  Designing a good benchmark is difficult, and understanding why helps you use benchmark results more skeptically and critically.

A **benchmark** is a standardized test used to measure AI system capability.  Not all benchmarks are equally trustworthy.  A good benchmark has five key properties:

1.  **Validity**: It actually measures the capability we care about, not a proxy or shortcut that happens to correlate with performance on easy examples.
2.  **Reliability**: It produces consistent results across repeated evaluations of the same system.
3.  **Coverage**: It spans the target domain broadly enough to be representative of real-world variation in that domain.
4.  **Difficulty Calibration**: It is not so easy that all systems score near 100%, nor so hard that all systems score near 0%. A well-calibrated benchmark spreads scores across a useful range.
5.  **Contamination Resistance**: The test data was not seen during model training, so scores reflect genuine capability rather than memorization of test answers.

#### Historical Benchmarks and Saturation

Over time, frontier AI models have scored so highly on once-challenging benchmarks that those benchmarks are no longer informative for comparing leading systems.  This is called **benchmark saturation**.

| Benchmark | What It Measures | Year Released | Approximate Frontier Model Score | Why Scores Are No Longer Informative |
|-----------|-----------------|---------------|----------------------------------|--------------------------------------|
| **ImageNet** | Visual object classification across 1,000 categories | 2009 | 99%+ accuracy on the standard test set | Effectively solved; top models have surpassed human-level performance for years |
| **MMLU** | Multidisciplinary knowledge spanning 57 academic subjects from medicine to law to history | 2020 | Above 90% for leading models | Near-saturation and suspected training contamination make it unreliable for distinguishing top systems |
| **HumanEval** | Python code generation from function docstrings, verified by running test cases | 2021 | Above 95% for leading code models | Examples appear in pretraining corpora; scores likely inflated by memorization |
| **MATH** | Competition-level mathematics problems requiring multi-step symbolic reasoning | 2021 | 70-90% for leading models | Partial saturation; the hardest problems remain challenging but easier problems are saturated |
| **BIG-Bench** | Over 200 diverse tasks designed to exceed model capabilities at release time | 2022 | Mixed: hardest tasks remain; many easier tasks saturated | Designed as a "living" benchmark but still subject to contamination as corpora grow |

#### Critical Thinking Questions

**Question 1.**  Frontier models now score above 90% on MMLU, which covers 57 academic subjects from medicine to law to history.  Does that mean AI systems understand most things humans know?  What are at least two specific reasons the score might overstate actual understanding?

> *Hint:* MMLU is multiple-choice; there are only four answer options for each question.  A model can score around 25% by random guessing, and higher scores can come from recognizing patterns in answer choices or from memorizing the specific phrasing of questions that appeared in training data.  Think about the difference between getting a multiple-choice question right and actually being able to explain the concept, apply it to a new situation, or recognize when it doesn't apply.  What would a question look like that a model could ace on MMLU but completely fail in a real clinical or legal context?

---

**Question 2.**  What is "benchmark contamination," and why is it especially difficult to prevent when training data is collected from the internet at scale?

> *Hint:* Benchmark contamination happens when the test questions (or very similar questions) appear somewhere in the model's training data.  The model then "answers" by recalling the answer rather than by reasoning.  The internet is enormous and constantly indexed by crawlers used for training data: academic benchmark papers are posted on arXiv, test questions are discussed on Reddit, answers are posted on Hugging Face forums.  Even a benchmark released after a model's training cutoff may have had its items written and shared informally before that date.  How would you detect whether contamination has occurred for a specific benchmark?

---

**Question 3.**  Name one cognitive skill or real-world capability that you consider important for an AI agent and that you believe no existing published benchmark adequately tests.  Explain specifically why existing benchmarks miss it.

> *Hint:* Think about capabilities that matter for the agents you've built in this course: knowing when to stop and ask for clarification instead of proceeding with an assumption, recognizing when a tool call failed silently rather than loudly, or calibrating confidence appropriately (saying "I'm not sure" when it is uncertain rather than generating a confident-sounding wrong answer).  How would you design a benchmark item that tests one of these capabilities?  What makes it hard to create ground-truth labels for?

---

### Designing Your Own Benchmark

Creating a valid benchmark requires more than writing a list of questions.  The following six-step process helps ensure benchmark quality, and each step can fail in a way that invalidates the results.

**Step 1 - Define the capability:** State in precise, testable terms what you are measuring.  "Common sense" is too vague to design items for.  "Detecting when a stated action violates an unstated social norm in a given cultural context" is specific enough that two independent researchers could agree on whether a given item tests it.

**Step 2 - Choose the instance format:** Multiple choice, free response, code generation, ranking, binary classification.  Each format has tradeoffs: multiple choice is easy to score automatically but susceptible to option-elimination strategies; free response has higher ecological validity but requires expensive human evaluation or an LLM judge.

**Step 3 - Write instances with known answers:** Every item needs a ground-truth answer that does not depend on the model's output.  For subjective items, collect independent human judgments and use majority vote or expert review.

**Step 4 - Calibrate difficulty:** Aim for a spread of difficulty: approximately 20-30% easy items, 40-50% medium items, and 20-30% hard items.  Pilot with human participants to calibrate before finalizing; what feels hard to the researcher may be trivial to the model or vice versa.

**Step 5 - Establish inter-rater reliability:** Have multiple independent humans answer every item.  If humans disagree frequently on a given item, the item is ambiguous and should be revised or removed.  Inter-rater agreement is typically measured with Cohen's kappa (κ) or percent agreement; κ below 0.6 is generally considered insufficient for a published benchmark.

**Step 6 - Resist contamination:** Do not publish the test set in its entirety.  Release training and validation splits publicly for model development; keep the test split private.  Release only aggregate scores, not per-item results, to prevent reverse-engineering of the test items.

#### Common Bias Traps in Benchmark Design

- **Selection bias:** Items are drawn from a narrow slice of the domain, for example, a "global knowledge" benchmark built primarily from Western English-language news sources systematically underrepresents non-Western knowledge.
- **Cultural specificity:** Correct answers assume cultural knowledge or social norms that are not universal across the populations that will use the AI system.
- **Language complexity confound:** Items that test reading difficulty rather than the target capability: a model that fails a medical knowledge question because of complex sentence structure, not because it lacks medical knowledge, is telling you something about language processing, not domain knowledge.

> **Common Misconception:** Many people treat published leaderboard rankings as objective ground truth about which AI system is "best."  In practice, every benchmark embeds assumptions about what matters, what counts as correct, and whose knowledge and values define the right answer.  A model that ranks first on HumanEval may rank fifth on a benchmark of multi-turn agent behavior.  A model that aces MMLU may be significantly outperformed on tasks requiring careful uncertainty calibration.  Benchmark rankings tell you about performance on *that specific benchmark under those specific conditions*, not about general intelligence or real-world usefulness.

#### Critical Thinking Questions

**Question 4.**  You want to benchmark an AI agent's ability to "understand safety constraints."  That phrase is ambiguous in several ways.  Describe how you would turn it into a concrete, testable benchmark.  What specific behaviors would your instances probe, and how would you write items that have clear ground-truth answers?

> *Hint:* Break "safety constraints" into specific testable behaviors: refusing a clearly harmful request, correctly identifying when a borderline request falls within or outside stated guidelines, gracefully declining and explaining why rather than silently failing, not being tricked by rephrasing or role-play framing.  For each behavior, write a concrete item: an input prompt, and the ground-truth answer (does the agent comply or refuse, and does it give a good explanation?).  How do you handle cases where experts disagree on whether the request is harmful?

---

**Question 5.**  What is inter-rater reliability and why does it matter for benchmark validity?  If two independent human annotators agree on only 60% of your benchmark items when labeling the correct answer, what does this tell you about those items?  What should you do about it?

> *Hint:* Inter-rater reliability measures how consistently independent people assign the same label to the same item.  If two annotators only agree 60% of the time, it means the items are ambiguous: the "correct" answer depends on interpretation rather than on objective fact.  This is a problem because: (1) the ground-truth labels may be wrong for some items; (2) different runs of the benchmark may give different scores to the same model depending on which annotator's label was used; (3) a model that "fails" these items may simply have chosen a different but equally valid interpretation.  What do you do: revise the ambiguous items, add a third annotator to break ties, or remove the items entirely?

---

**Question 6.**  For an adversarial robustness benchmark (where the agent is tested on prompts specifically designed to cause failures), what would a "floor" item look like?  What would a "ceiling" item look like?  Why does having both matter for a useful benchmark?

> *Hint:* A floor item is one that even a weak or poorly-configured agent should handle correctly; if an agent fails this, you know it has a fundamental capability gap rather than just an adversarial robustness problem.  A ceiling item is one that even the best current system struggles with.  Without floor items, you cannot distinguish a badly-broken agent from one that is simply not robust to sophisticated attacks.  Without ceiling items, you cannot measure room for improvement.  How would you write a concrete floor item and a concrete ceiling item for adversarial robustness in the context of an agent that should refuse harmful requests?

---

#### Multiple Choice Question

A benchmark is released publicly with all test examples included in the paper and available for download.  After one year, state-of-the-art models score 97% on it.  The most important caveat when interpreting this result is:

[[ ]] Benchmark difficulty is fixed at design time; a 97% score proves the benchmark was always trivially easy, not that models improved through contamination or genuine capability gains
[[ ]] A state-of-the-art score on a benchmark means the underlying real-world capability has been fully solved; leaderboard performance directly predicts deployment quality in production
[[x]] Models may have been trained on or fine-tuned using the published test examples, artificially inflating scores beyond what genuine capability would achieve
[[ ]] The 3% failure rate is evenly distributed across all input categories; a 97% average accuracy implies the system is reliably correct for every subgroup and edge case

> **Why this answer?**  When a benchmark is published with all test examples publicly available, those examples can appear in the training data of future models, either in the original pretraining corpus if the paper predates the training cutoff, or through deliberate fine-tuning on benchmark items.  A 97% score on a contaminated benchmark tells you the model is good at answering those specific questions, not that it has genuinely mastered the underlying capability.  The benchmark has become a memorization test rather than a capability test.

---

### Evaluation Beyond Accuracy

Accuracy on a benchmark is one signal, but it is rarely sufficient on its own for making real-world deployment decisions.  Real-world AI evaluation combines multiple methods, each with distinct strengths and failure modes.

#### Human Evaluation

Human evaluators assess model outputs directly.  Common formats:

- **Pairwise preference:** Show two model responses side by side; ask a human evaluator which is better.  Used extensively in RLHF training and in platforms like Chatbot Arena (lmsys.org).  Pairwise judgments are more reliable than absolute ratings because they avoid the anchoring effects of rating scales.
- **Likert scales:** Rate output on a 1-5 scale across multiple dimensions such as helpfulness, safety, and fluency.  Useful for profiling multiple quality dimensions at once.
- **Task completion rate:** Give a human evaluator a goal and have them use the agent to achieve it; measure whether they succeed within a given number of turns.  High ecological validity.

**Strengths:** Captures qualities that automatic metrics miss: tone, appropriateness, safety edge cases that don't trigger keyword filters, and the usefulness of an answer in context.

**Limitations:** Expensive (professional evaluators cost $10-50 per hour), slow (days to weeks for large-scale studies), subject to annotator bias, and inconsistent across annotators and over time as annotator pools and guidelines evolve.

#### Automatic Evaluation Metrics

| Metric | What It Measures | Key Blind Spot | When to Use It |
|--------|-----------------|----------------|----------------|
| **BLEU** | N-gram word overlap between the model's output and a reference answer | Does not capture meaning; penalizes valid paraphrases heavily | Machine translation as a rough filter; not suitable for open-ended generation |
| **ROUGE** | Recall-oriented n-gram overlap, common in summarization evaluation | Same blind spot as BLEU: surface overlap, not semantic accuracy | Summarization pipeline monitoring as a sanity check |
| **BERTScore** | Semantic similarity using contextual embeddings rather than exact word matches | Can miss factual errors; two sentences can be semantically similar but factually opposite | More reliable than BLEU/ROUGE for generation quality; still misses factual accuracy |
| **G-Eval / LLM-as-Judge** | A language model scores another model's output on a defined rubric | Inherits the judge model's biases, blind spots, and style preferences; expensive per evaluation | Rapid large-scale evaluation when human evaluation budget is limited |

#### Live / Production Evaluation

- **Canary queries** (hidden "decoy" test prompts inserted silently into live production traffic to catch quality regressions before users notice them): Fixed test prompts inserted into real production traffic anonymously and regularly.  The agent's response to each canary is automatically scored.  Catches quality regressions before they affect large numbers of real users.
- **A/B testing:** Route a fraction of real users (say, 5%) to a new model version and the rest to the current version; compare outcome metrics such as task completion rate, escalation rate (how often users give up and contact a human), and explicit feedback (thumbs up/down).

#### Critical Thinking Questions

**Question 7.**  When is human evaluation worth the extra cost and time compared to automatic metrics?  Describe a specific, concrete scenario where relying solely on automatic metrics would give a dangerously misleading assessment of agent quality.

> *Hint:* Consider an agent that produces outputs that score well on BERTScore (semantically similar to reference answers) but that are subtly wrong in a dangerous way, for example, a medical information agent that correctly identifies the drug name but gives the wrong dosage, or a legal information agent that correctly identifies the relevant law but misapplies it to the user's specific situation.  BERTScore would rate these outputs highly because they contain the right words in roughly the right semantic neighborhood.  What would a human evaluator catch that BERTScore misses?

---

**Question 8.**  An agent achieves 90% accuracy on your benchmark but receives poor user satisfaction ratings (2.1 out of 5 stars) in production.  Name at least two explanations for this gap.  What would you investigate first, and what data would help you diagnose the specific cause?

> *Hint:* Possible explanations include: (1) the benchmark tests a different capability than what users actually need in production: the benchmark was valid for development but lacks ecological validity; (2) the benchmark has single-turn items but production requires multi-turn dialogue; (3) the 90% accuracy hides a systematic failure on the specific types of queries most common in production; (4) the agent is technically correct but communicates in a way that users find unhelpful (too verbose, too terse, wrong tone).  Start by looking at the specific queries where users rated the agent poorly and comparing them to the benchmark item distribution: are those failure cases well-represented in the benchmark?

---

**Question 9.**  Design a three-metric evaluation plan for a coding agent that helps students debug Python programs.  For each metric, specify: (a) exactly what it measures, (b) how it is collected (automatically, through human review, or through user interaction), and (c) what score or threshold would trigger a concern serious enough to halt deployment.

> *Hint:* Consider three different layers: (1) A correctness metric: does the agent's suggested fix actually make the student's code pass its test cases?  This can be verified automatically by running the suggested code in a sandbox.  (2) A pedagogical quality metric: does the agent explain *why* the fix works, not just what to change?  This likely requires human evaluation or an LLM judge with a rubric.  (3) A safety / harm-avoidance metric: does the agent avoid simply writing the complete solution for the student (undermining learning) while still being helpful enough to be useful?  What threshold on each metric would make you say "this agent is not ready for students"?

---

# Part III: Synthesis and Practice

In this part, you will build your own benchmark, a domain-specific task set your team designs, verifies, and will reuse throughout the semester.  Getting this right now pays dividends in every future module that compares techniques.

## 4.  Exercises

1.  *Benchmark sketch.*

   - *What to do*: Draft a 10-item task set for a domain your team knows well: a sport, a fandom, a local community, a scientific field.  Specify: the 10 questions, the gold answers, the metric you will use (exact match, substring, or something else), and the full protocol (which model, what temperature, what seed).
   - *Starter hint*: Choose a domain where you can verify the correct answers independently (you know them from experience or can check a reliable source).  Make at least two questions "thin training data" questions where you expect the model to struggle.  Save this task set; you will reuse it to evaluate retrieval-augmented generation in the *Retrieval-Augmented Generation with Chroma* activity and your project agents at the end of the semester.
   - *You've succeeded when*: Your task set has 10 questions with verified gold answers, a written metric definition, and a written protocol, specific enough that a teammate could run it without asking you any questions.

2.  *Calibration probe.*

   - *What to do*: Modify the system prompt to append "State your confidence as high, medium, or low" to each question.  Run the 5-item task set and record both accuracy and confidence for each item.  Compute accuracy separately within each confidence bucket (high / medium / low).
   - *Starter hint*: Change the prompt in `chat()` to include `" Respond with only the answer and your confidence (high/medium/low), no explanation."` Then parse the confidence out of each response before scoring.  A well-calibrated model should have higher accuracy in its "high" confidence bucket than in its "low" bucket.
   - *You've succeeded when*: You have a two-column table (confidence, accuracy) and a one-sentence verdict: is this model's confidence informative, misleading, or uncorrelated with its actual accuracy?

3.  *Mitigation preview.*

   - *What to do*: For each of the three hallucination taxonomy categories (factual, faithfulness, reasoning error), name the course topic that most directly addresses it, and write one sentence explaining the connection.
   - *Starter hint*: You have not built any of these yet; this is a prediction, and one sentence each is all you need to make it.  **Retrieval-augmented generation** hands the model the relevant source text before it answers, so it can quote instead of recall (the *Retrieval-Augmented Generation with Chroma* activity, in two weeks).  **Tool use** lets the model call a real function for facts it should not be recalling at all, like today's date or an arithmetic result (*Tool Use and Function Calling*, next session).  **Critique agents and debate** put a second model, or several, in the path to challenge the first one's answer before you see it (*Critique and Refine* and *Multi-Agent Debate*, later in the term).  Match each to the hallucination type it addresses most directly, and say what it does *not* fix.
   - *You've succeeded when*: You have three pairings, each with a one-sentence justification that explains the *mechanism* of why that technique addresses that hallucination type, not just that they are both in the course.

---

## Reflection Prompt

*Personal*: Describe one time you (or someone you observed) accepted an AI output that turned out to be wrong: a hallucinated fact, a fabricated citation, a confidently stated number that was off.  Using today's taxonomy, classify the failure: was it factual hallucination, faithfulness hallucination, or a reasoning error?  What was it about the response that made it seem credible?

*Technical*: The evaluation harness today used a human-written list of questions with known correct answers.  Identify the three biggest limitations of that approach for evaluating a real agent deployed in a production system.  For each limitation, name a technique (from today or from common sense) that would partially address it.

*Societal*: Identify the cheapest check that would have caught the error you described in the Personal reflection, for example, a web search, a database lookup, or a second model review.  Why was that check not performed at the time?  What does it cost (in time, effort, or money) to add systematic fact-checking to every AI output?  Who should bear that cost: the model developer, the deploying organization, or the end user?

---

-> Coming Up Next: You just predicted which techniques fix which hallucinations.  Next session we build the first one: in *Tool Use and Function Calling*, the agent stops recalling facts it should be looking up and calls a real function instead, which is the mitigation your Exercise 3 matched to fabricated specifics.  The evaluation harness pattern you built here returns in the RAG Knowledge Base Lab's retrieval evaluation and the Rubric Pipeline Lab's rubric pipeline.

## 5.  Further Reading

- Ziwei Ji et al. "Survey of Hallucination in Natural Language Generation."  *ACM Computing Surveys* (2023).
- Melanie Mitchell.  *AI: A Guide for Thinking Humans*, Chapter 3.
- Lin, Hilton, and Evans.  "TruthfulQA: Measuring How Models Mimic Human Falsehoods."  *ACL* (2022).
