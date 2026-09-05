<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Hallucinations and Evaluating Agent Outputs

A model that writes fluently can be fluently wrong.  Last session, in *The Karpathy Loop and the Gauntlet Loop: Iterating With an Agent*, you judged each round of an agent's work by reading it.  Today you learn why reading is not enough, and you build the first tool that replaces it.  A **hallucination** is a model output that is confident and fluent but false.  This module explains why next-token prediction produces hallucinations, sorts them into three types that need three different fixes, and builds your first evaluation harness: a program that scores a model on questions with known answers.  An agent you cannot measure is an agent you cannot trust or improve.  For background, the *Why Different Answers Every Time?  Sampling, Temperature, and Generation* tutorial (https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/SamplingAndTemperature) showed that a model samples plausible continuations, and plausible is not the same as true.

Today the OpenCode Studio lab is due, and I hand out the Local Agent lab and the Stakeholder Brief.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| Hallucination | A model output that is confident and fluent but false.  The model is not making a mistake the way a person does; it is doing what training rewarded, which is to produce plausible text, and plausible text is not always true | A fabricated but well-formatted academic citation, complete with volume, issue, and page numbers |
| Factual hallucination | The model asserts something false about the world, with no source document in play | Claiming that a real journal published a specific article that does not exist |
| Faithfulness hallucination | The model contradicts, or adds to, a source document you gave it.  This is the type that retrieval-augmented systems produce most often | Summarizing a paragraph and adding a detail that was not in the original text |
| Reasoning error | The model has the right facts but combines them with bad logic and reaches a wrong conclusion | Knowing that the speed of sound is 343 m/s but computing travel time by multiplying instead of dividing |
| Evaluation harness | A program that runs a model on a fixed set of questions with known answers, scores the responses automatically, and records the results so that anyone can rerun them | The `tasks` list and scoring loop in today's code cell |
| Exact-match accuracy | A metric that scores 1 when the response contains the correct answer string and 0 otherwise.  Simple and objective, but strict about phrasing | Scoring "The answer is Canberra" as correct when the gold answer is "canberra" (substring match), but failing "the Australian capital" even though it is correct |

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget, and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | The three prompts you brought: triage real confidently-wrong answers, not invented ones |
| 10-25 | Part I, why models hallucinate, mechanism first |
| 25-45 | Part II, build the tiny evaluation harness |
| 45-70 | Part IIb, design the benchmark your evaluation work will keep needing |
| 70-75 | Reflection prompt, and the benchmark sketch you keep |

---
# Part I: Why Models Hallucinate

Hallucination is not a bug that someone can patch.  It is a predictable result of how language models are trained.  In this part you learn the mechanism, then sort hallucinations into three types.  Each type calls for a different fix.

## 1.  Fluency Is the Objective, Truth Is Not

Training rewards text that sounds right, and nothing in the training objective checks whether the text is true.  Picture a writing student who earns credit whenever an essay *sounds* expert: correct grammar, confident tone, the right vocabulary.  That student soon writes convincing prose on topics they know nothing about, because the grade never depended on the facts.  A language model is that student at enormous scale.  It learns to predict what text tends to follow other text, not to verify the claims in that text.  The analogy stops here: the student could look the facts up if asked, while the model has no separate store of verified facts to consult.

In symbols, training maximizes the probability of each next token given the tokens before it, $\max \sum_t \log P(x_t \mid x_{<t})$, and that expression never mentions truth.  When the context looks like confident factual writing, the most probable continuation is more confident factual-sounding text, whether or not a real fact stands behind it.

Hallucinations cluster where training data is thin.  Specific citations, niche biographies, exact recent statistics, and obscure local facts appear rarely in the training set.  The model fills the gap by interpolating between patterns it has seen, and interpolation between facts is often fiction.  This tells you *where* to be suspicious, which is more useful than distrusting everything the model says.

Three types of hallucination call for three different fixes.  A *factual hallucination* asserts something false about the world; the fix is retrieval or tool use.  A *faithfulness hallucination* contradicts, or adds to, a source document you supplied; the fix is strict grounding instructions and retrieval-augmented generation.  A *reasoning error* combines correct facts with invalid logic; the fix is chain-of-thought prompting or a critique agent.  Each of these fixes is a topic in the coming weeks.

Two things to remember from this section.  The model is rewarded for sounding right, not for being right.  Its errors concentrate where its training data is thin, so that is where you check hardest.

---

## Model 1: The Confident Citation

A student asks a local model for three peer-reviewed sources on a niche topic in coastal ecology.  The model answers: "See Hartman, R. (2018).  *Tidal Dynamics of Inland Estuaries*, Journal of Coastal Research, 34(2), 211-228."  The journal is real and publishes real research.  The article does not exist.  The author's name appears in the training data in other contexts.  Every part of the citation looks plausible on its own, and that is why it is hard to catch without checking.

### Critical Thinking Questions

1.  Use the training objective from Section 1 to explain why every *individual part* of this citation (author format, journal name, year, page range) looks plausible even though the *whole citation* is fabricated.

   > *Hint: The model has seen thousands of correctly formatted citations.  It learned the pattern: author, year, title in italics, journal name, volume, issue, pages.  It can reproduce that pattern perfectly while inventing every specific value.*

2.  Which category does this citation fall into: factual, faithfulness, or reasoning?  Suppose you had given the model a PDF of real papers to read before asking for citations.  Would that change the category of errors you expect?

   > *Hint: Without a source document, the model generates from memory (or from pattern).  With a source document, any error in summarizing that document is a faithfulness error.  Could the model still produce factual errors about the world beyond the document?*

3.  Propose a verification step that a student (or an automated agent) could run before trusting any citation.  What specific tool or data source would the agent need?

   > *Hint: Several databases index academic papers: Google Scholar, CrossRef, PubMed, Semantic Scholar.  A verification agent could call one of these APIs with the DOI or title and check whether the paper exists.  What happens if the paper exists but the page numbers are wrong?*

---

## 2.  Evaluation Foundations

An evaluation needs three things.  A **task set** is a list of inputs with known correct outputs.  A metric is a function that turns a model output and a correct answer into a score.  A protocol fixes the model version, parameters, and seed so that anyone can reproduce the results and compare them over time.  For factual question answering, the simplest metric is exact-match accuracy: the fraction of items the model gets right, $\text{accuracy} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\hat{y}_i = y_i]$, where $\hat{y}_i$ is the model's answer, $y_i$ is the known answer, and $\mathbb{1}[\cdot]$ is 1 when the condition holds and 0 otherwise (Python's `int(condition)`).  Exact match is harsh on purpose: a correct answer phrased differently scores zero.  That harshness is why we will later recruit *another model* as a judge (an LLM-as-evaluator), and why we must then evaluate the judge too.

A team reports that their agent "seems pretty accurate" after trying a few questions.  The most important missing element of a real evaluation is:

[( )] A larger language model with more parameters
[( )] Higher temperature for greater response diversity
[(X)] A fixed task set with known answers, a clearly defined metric, and a reproducible protocol with fixed model and parameters
[( )] A faster computer to run more experiments

---

# Part II: Building a Tiny Evaluation Harness

"It seems pretty good" is not an engineering standard.  In this part you write a minimal evaluation harness.  By the end you have a scaffold you can reuse to evaluate any agent you build this semester.

## 3.  Measure Before You Trust

Before you trust an agent in a real application, you need to know where it succeeds and where it fails, as a number rather than an impression.  The code below is a minimal version of the evaluation infrastructure behind every published benchmark in AI research.  It is short enough to read in five minutes and still reveals real patterns.

---

The harness runs five fixed questions through the model at temperature 0.0 with a fixed random seed, so the results repeat from run to run.  For each question it checks whether the correct answer appears anywhere in the model's response and prints PASS or FAIL.  Read the code before you run it.  You will be asked to critique both the scoring rule and the task set.

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

Read the PASS/FAIL output line by line.  Before you talk with your group, form your own hypothesis about each result: why did the model pass or fail this particular question?

### Critical Thinking Questions

4.  The scoring rule is `gold in pred`, a substring check.  It passes when the correct answer appears anywhere in the model's response.  Construct a specific model answer that is *factually wrong* yet scores PASS, and a specific model answer that is *factually correct* yet scores FAIL.  What does this teach about the relationship between metrics and truth?

   > *Hint: For a wrong-but-PASS example: the question is "What is 17 * 24?" and the gold is "408."  What if the model outputs "408 is not actually correct; the real answer is 412"?  For a right-but-FAIL example: gold is "mary shelley" and the model outputs "Mary Wollstonecraft Shelley"; does the substring check pass?*

5.  Add two questions to the `tasks` list where you predict the model will hallucinate (use the thin-training-data principle) and two where you predict it will answer correctly.  Run them.  Did your theory of where models fail predict the results?

   > *Hint: Good hallucination-prone questions involve specific local people or events, very recent information (post-2023), exact statistics like population figures or distances, or niche academic citations.  Good reliable questions involve widely published historical dates, famous authors, and capital cities of large countries.*

6.  We fixed temperature to 0.0 and seed to 42.  Rerun the harness once without changing any parameters and confirm that you get identical results.  Then explain in one sentence each why a grader, a scientist, and a software debugger each need this reproducibility.

   > *Hint: A grader needs it so that "running the eval again" gives the same score.  A scientist needs it so that a published result can be independently replicated.  A debugger needs it so that a bug observed in one run appears again in the next run.*

> **Common Misconception:** Many students assume that a model that answers a factual question wrong "does not know" the answer and will always fail that question.  In fact the same model with the same weights can answer the same question correctly at one temperature setting and fail it at another, or answer differently when the question is rephrased.  This is why evaluation needs a *fixed protocol*.  We do not hold parameters and phrasing constant because we distrust the model.  We hold them constant because the model's behavior depends on them, and we cannot learn anything unless they stay put.

---

---

# Part IIb: Designing the Benchmark You Are About to Need

Triaging bad answers one at a time does not scale.  A benchmark turns "it seems better" into a number you can defend, and you will need a real one soon.  The RAG Quality Checkup pathway of the *RAG Knowledge Base* lab opens by asking you for a ten-item golden set, with a prediction and a rationale per item, and every evaluation after that builds on it.  Sketch it here while today's failure modes are fresh.  Exercise 1 at the end of this session turns the sketch into the set you keep.

## What Makes a Good Benchmark?

A benchmark that frontier models ace is like a test everyone scores 100% on: it no longer measures anything.  This is the central problem of modern AI evaluation.  The best models improve faster than we can design meaningful tests.  A benchmark that is too hard or too narrow fails for a different reason: it measures the wrong thing, or the right thing in the wrong way.  Designing a good benchmark is hard, and knowing why helps you read benchmark results with the right amount of skepticism.

A **benchmark** is a standardized test that measures what an AI system can do.  Not all benchmarks deserve the same trust.  A good benchmark has five properties:

1.  *Validity*: It measures the capability you care about, not a proxy or shortcut that happens to correlate with performance on easy examples.
2.  *Reliability*: It gives consistent results when you evaluate the same system repeatedly.
3.  *Coverage*: It spans the target domain widely enough to represent real-world variation in that domain.
4.  *Difficulty calibration*: It is neither so easy that every system scores near 100% nor so hard that every system scores near 0%.  A well-calibrated benchmark spreads scores across a useful range.
5.  *Contamination resistance*: The test data was not seen during training, so scores reflect capability rather than memorized answers.

### Historical Benchmarks and Saturation

Over time, frontier models have scored so high on once-hard benchmarks that those benchmarks no longer separate the leading systems.  This is called benchmark saturation.

| Benchmark | What It Measures | Year Released | Approximate Frontier Model Score | Why Scores Are No Longer Informative |
|-----------|-----------------|---------------|----------------------------------|--------------------------------------|
| **ImageNet** | Visual object classification across 1,000 categories | 2009 | 99%+ accuracy on the standard test set | Effectively solved; top models have surpassed human-level performance for years |
| **MMLU** | Multidisciplinary knowledge spanning 57 academic subjects from medicine to law to history | 2020 | Above 90% for leading models | Near-saturation and suspected training contamination make it unreliable for distinguishing top systems |
| **HumanEval** | Python code generation from function docstrings, verified by running test cases | 2021 | Above 95% for leading code models | Examples appear in pretraining corpora; scores likely inflated by memorization |
| **MATH** | Competition-level mathematics problems requiring multi-step symbolic reasoning | 2021 | 70-90% for leading models | Partial saturation; the hardest problems remain challenging but easier problems are saturated |
| **BIG-Bench** | Over 200 diverse tasks designed to exceed model capabilities at release time | 2022 | Mixed: hardest tasks remain; many easier tasks saturated | Designed as a "living" benchmark but still subject to contamination as corpora grow |

### Critical Thinking Questions

**Question 1.**  Frontier models now score above 90% on MMLU, which covers 57 academic subjects from medicine to law to history.  Does that mean AI systems understand most of what humans know?  Give at least two specific reasons the score might overstate real understanding.

> *Hint:* MMLU is multiple-choice with four options per question.  A model scores around 25% by random guessing, and higher scores can come from recognizing patterns in the answer choices or from memorizing the phrasing of questions that appeared in training data.  Consider the gap between getting a multiple-choice question right and being able to explain the concept, apply it to a new situation, or recognize when it does not apply.  What would a question look like that a model could ace on MMLU but fail in a real clinical or legal setting?

---

**Question 2.**  What is "benchmark contamination," and why is it so hard to prevent when training data is collected from the internet at scale?

> *Hint:* Benchmark contamination happens when the test questions (or very similar questions) appear somewhere in the model's training data.  The model then "answers" by recalling rather than by reasoning.  The internet is enormous, and the crawlers that collect training data index it constantly: benchmark papers are posted on arXiv, test questions are discussed on Reddit, and answers are posted on Hugging Face forums.  Even a benchmark released after a model's training cutoff may have had its items written and shared informally before that date.  How would you detect whether contamination has occurred for a specific benchmark?

---

**Question 3.**  Name one cognitive skill or real-world capability that you consider important for an AI agent and that you believe no published benchmark tests well.  Explain specifically why existing benchmarks miss it.

> *Hint:* Consider capabilities that matter for the agents you have built in this course: knowing when to stop and ask for clarification instead of proceeding on an assumption, noticing when a tool call failed silently rather than loudly, or calibrating confidence (saying "I'm not sure" when uncertain rather than producing a confident wrong answer).  How would you design a benchmark item that tests one of these?  What makes its ground-truth label hard to write?

---

## Designing Your Own Benchmark

A valid benchmark takes more than a list of questions.  The six steps below protect benchmark quality, and each one can fail in a way that invalidates the results.

*Step 1: Define the capability.*  State in precise, testable terms what you are measuring.  "Common sense" is too vague to write items for.  "Detecting when a stated action violates an unstated social norm in a given cultural context" is specific enough that two independent researchers could agree on whether a given item tests it.

*Step 2: Choose the instance format.*  Multiple choice, free response, code generation, ranking, or binary classification.  Each format has tradeoffs.  Multiple choice is easy to score automatically but open to option-elimination strategies.  Free response reflects real use better but needs expensive human evaluation or an LLM judge.

*Step 3: Write instances with known answers.*  Every item needs a ground-truth answer that does not depend on the model's output.  For subjective items, collect independent human judgments and use a majority vote or expert review.

*Step 4: Calibrate difficulty.*  Aim for a spread: about 20-30% easy items, 40-50% medium items, and 20-30% hard items.  Pilot with human participants before you finalize the set.  What feels hard to the researcher may be trivial for the model, or the reverse.

*Step 5: Establish inter-rater reliability.*  Have several independent humans answer every item.  If humans disagree often on an item, the item is ambiguous and you should revise or remove it.  Inter-rater agreement is usually measured with Cohen's kappa (κ) or percent agreement; κ below 0.6 is generally considered too low for a published benchmark.

*Step 6: Resist contamination.*  Do not publish the whole test set.  Release training and validation splits publicly for model development and keep the test split private.  Release only aggregate scores, not per-item results, so that nobody can reverse-engineer the test items.

### Common Bias Traps in Benchmark Design

- *Selection bias:* Items come from a narrow slice of the domain.  For example, a "global knowledge" benchmark built mostly from Western English-language news sources underrepresents non-Western knowledge.
- *Cultural specificity:* Correct answers assume cultural knowledge or social norms that are not shared by everyone who will use the AI system.
- *Language complexity confound:* Items test reading difficulty instead of the target capability.  A model that fails a medical question because of a tangled sentence, not because it lacks medical knowledge, is telling you about language processing, not domain knowledge.

> **Common Misconception:** Many people treat published leaderboard rankings as objective truth about which AI system is "best."  In practice, every benchmark embeds assumptions about what matters, what counts as correct, and whose knowledge and values define the right answer.  A model that ranks first on HumanEval may rank fifth on a benchmark of multi-turn agent behavior.  A model that aces MMLU may fall well behind on tasks that need careful uncertainty calibration.  A benchmark ranking tells you about performance on *that benchmark under those conditions*, not about general intelligence or real-world usefulness.

### Critical Thinking Questions

**Question 4.**  You want to benchmark an AI agent's ability to "understand safety constraints."  That phrase is ambiguous in several ways.  Describe how you would turn it into a concrete, testable benchmark.  What specific behaviors would your items probe, and how would you write items with clear ground-truth answers?

> *Hint:* Break "safety constraints" into specific testable behaviors: refusing a clearly harmful request, correctly deciding whether a borderline request falls inside or outside stated guidelines, declining and explaining why rather than failing silently, and not being tricked by rephrasing or role-play framing.  For each behavior, write a concrete item: an input prompt and the ground-truth answer (does the agent comply or refuse, and does it give a good explanation?).  How do you handle cases where experts disagree on whether the request is harmful?

---

**Question 5.**  What is inter-rater reliability, and why does it matter for benchmark validity?  If two independent human annotators agree on only 60% of your benchmark items when labeling the correct answer, what does this tell you about those items?  What should you do about it?

> *Hint:* Inter-rater reliability measures how consistently independent people assign the same label to the same item.  If two annotators agree only 60% of the time, the items are ambiguous: the "correct" answer depends on interpretation rather than on fact.  That is a problem for three reasons: (1) some ground-truth labels may be wrong; (2) different runs of the benchmark may score the same model differently depending on whose label was used; (3) a model that "fails" these items may have chosen a different but equally valid interpretation.  What do you do: revise the ambiguous items, add a third annotator to break ties, or remove the items entirely?

---

**Question 6.**  For an adversarial robustness benchmark (where the agent is tested on prompts designed to cause failures), what would a "floor" item look like?  What would a "ceiling" item look like?  Why does a useful benchmark need both?

> *Hint:* A floor item is one that even a weak or badly configured agent should handle correctly.  If an agent fails it, the agent has a basic capability gap, not an adversarial robustness problem.  A ceiling item is one that even the best current system struggles with.  Without floor items you cannot tell a broken agent from one that only breaks under sophisticated attacks.  Without ceiling items you cannot measure room for improvement.  How would you write a concrete floor item and a concrete ceiling item for an agent that should refuse harmful requests?

---

### Multiple Choice Question

A benchmark is released publicly with all test examples included in the paper and available for download.  After one year, state-of-the-art models score 97% on it.  The most important caveat when interpreting this result is:

[[ ]] Benchmark difficulty is fixed at design time; a 97% score proves the benchmark was always trivially easy, not that models improved through contamination or genuine capability gains
[[ ]] A state-of-the-art score on a benchmark means the underlying real-world capability has been fully solved; leaderboard performance directly predicts deployment quality in production
[[x]] Models may have been trained on or fine-tuned using the published test examples, artificially inflating scores beyond what genuine capability would achieve
[[ ]] The 3% failure rate is evenly distributed across all input categories; a 97% average accuracy implies the system is reliably correct for every subgroup and edge case

> **Why this answer?**  When a benchmark is published with every test example available, those examples can end up in the training data of future models, either through the pretraining corpus (if the paper predates the training cutoff) or through deliberate fine-tuning on benchmark items.  A 97% score on a contaminated benchmark shows that the model answers those specific questions well, not that it has learned the underlying capability.  The benchmark has become a memorization test rather than a capability test.

---

## Evaluation Beyond Accuracy

Benchmark accuracy is one signal, and it is rarely enough on its own to decide a real deployment.  Real-world AI evaluation combines several methods, each with its own strengths and failure modes.

### Human Evaluation

Human evaluators judge model outputs directly.  Three common formats:

- *Pairwise preference:* Show two model responses side by side and ask a human which is better.  Used heavily in RLHF training and in platforms like Chatbot Arena (lmsys.org).  Pairwise judgments are more reliable than absolute ratings because they avoid the anchoring effects of rating scales.
- *Likert scales:* Rate an output from 1 to 5 on several dimensions such as helpfulness, safety, and fluency.  Useful for profiling several quality dimensions at once.
- *Task completion rate:* Give a human a goal and have them use the agent to reach it; measure whether they succeed within a set number of turns.  This is close to real use.

Strengths: humans catch what automatic metrics miss, such as tone, appropriateness, safety edge cases that no keyword filter triggers, and whether an answer is useful in context.

Limitations: human evaluation is expensive (professional evaluators cost $10-50 per hour), slow (days to weeks for large studies), subject to annotator bias, and inconsistent across annotators and over time as annotator pools and guidelines change.

### Automatic Evaluation Metrics

| Metric | What It Measures | Key Blind Spot | When to Use It |
|--------|-----------------|----------------|----------------|
| **BLEU** | N-gram word overlap between the model's output and a reference answer | Does not capture meaning; penalizes valid paraphrases heavily | Machine translation as a rough filter; not suitable for open-ended generation |
| **ROUGE** | Recall-oriented n-gram overlap, common in summarization evaluation | Same blind spot as BLEU: surface overlap, not semantic accuracy | Summarization pipeline monitoring as a sanity check |
| **BERTScore** | Semantic similarity using contextual embeddings rather than exact word matches | Can miss factual errors; two sentences can be semantically similar but factually opposite | More reliable than BLEU/ROUGE for generation quality; still misses factual accuracy |
| **G-Eval / LLM-as-Judge** | A language model scores another model's output on a defined rubric | Inherits the judge model's biases, blind spots, and style preferences; expensive per evaluation | Rapid large-scale evaluation when human evaluation budget is limited |

### Live / Production Evaluation

- *Canary queries:* Fixed test prompts inserted silently and regularly into real production traffic.  The agent's response to each canary is scored automatically.  Canaries catch quality regressions before many real users notice them.
- *A/B testing:* Route a fraction of real users (say, 5%) to a new model version and the rest to the current version.  Compare outcome metrics such as task completion rate, escalation rate (how often users give up and contact a human), and explicit feedback (thumbs up or down).

### Critical Thinking Questions

**Question 7.**  When is human evaluation worth the extra cost and time compared to automatic metrics?  Describe a specific scenario where relying only on automatic metrics would give a dangerously misleading picture of agent quality.

> *Hint:* Consider an agent whose outputs score well on BERTScore (semantically similar to the reference answers) but are subtly wrong in a dangerous way.  For example, a medical information agent names the right drug but gives the wrong dosage, or a legal information agent names the right law but misapplies it to the user's situation.  BERTScore rates these outputs highly because they contain the right words in roughly the right semantic neighborhood.  What would a human evaluator catch that BERTScore misses?

---

**Question 8.**  An agent scores 90% on your benchmark but gets poor user satisfaction ratings (2.1 out of 5 stars) in production.  Name at least two explanations for this gap.  What would you investigate first, and what data would help you find the cause?

> *Hint:* Possible explanations: (1) the benchmark tests a different capability than users need in production, so it was valid for development but does not reflect real use; (2) the benchmark has single-turn items but production needs multi-turn dialogue; (3) the 90% hides a systematic failure on the query types most common in production; (4) the agent is technically correct but communicates in a way users find unhelpful (too long, too short, wrong tone).  Start by looking at the queries where users rated the agent poorly and compare them to the benchmark item distribution: are those failure cases well represented in the benchmark?

---

**Question 9.**  Design a three-metric evaluation plan for a coding agent that helps students debug Python programs.  For each metric, specify (a) exactly what it measures, (b) how it is collected (automatically, through human review, or through user interaction), and (c) what score or threshold would raise a concern serious enough to halt deployment.

> *Hint:* Consider three layers.  (1) A correctness metric: does the agent's suggested fix make the student's code pass its test cases?  You can verify this automatically by running the suggested code in a sandbox.  (2) A pedagogical quality metric: does the agent explain *why* the fix works, not only what to change?  This probably needs human evaluation or an LLM judge with a rubric.  (3) A safety metric: does the agent avoid writing the complete solution for the student (which undermines learning) while still helping enough to be useful?  What threshold on each metric would make you say "this agent is not ready for students"?

---

# Part III: Synthesis and Practice

In this part you build your own benchmark: a task set for a domain your team knows well, which you verify now and reuse all semester.  Every later module that compares techniques will run on it, so the care you put in now pays off repeatedly.

## 4.  Exercises

1.  *Benchmark sketch.*

   - *What to do*: Draft a 10-item task set for a domain your team knows well: a sport, a fandom, a local community, a scientific field.  Specify the 10 questions, the gold answers, the metric you will use (exact match, substring, or something else), and the full protocol (which model, what temperature, what seed).
   - *Starter hint*: Choose a domain where you can verify the correct answers on your own (you know them from experience or can check a reliable source).  Make at least two questions "thin training data" questions where you expect the model to struggle.  Save this task set.  It is the seed of the ten-item golden set the RAG Quality Checkup pathway of the *RAG Knowledge Base* lab asks you to finish, and you will reuse it to evaluate retrieval-augmented generation in the *RAG Knowledge Base: Code and No-Code Routes* activity and your project agents at the end of the semester.
   - *You've succeeded when*: Your task set has 10 questions with verified gold answers, a written metric definition, and a written protocol, specific enough that a teammate could run it without asking you any questions.

2.  *Calibration probe.*

   - *What to do*: Change the prompt so that each question also asks, "State your confidence as high, medium, or low."  Run the 5-item task set and record both accuracy and confidence for each item.  Compute accuracy separately within each confidence bucket (high / medium / low).
   - *Starter hint*: Change the prompt in `chat()` to include `" Respond with only the answer and your confidence (high/medium/low), no explanation."` Then parse the confidence out of each response before scoring.  A well-calibrated model has higher accuracy in its "high" confidence bucket than in its "low" bucket.
   - *You've succeeded when*: You have a two-column table (confidence, accuracy) and a one-sentence verdict: is this model's confidence informative, misleading, or unrelated to its actual accuracy?

3.  *Mitigation preview.*

   - *What to do*: For each of the three hallucination categories (factual, faithfulness, reasoning error), name the course topic that addresses it most directly, and write one sentence explaining the connection.
   - *Starter hint*: You have not built any of these yet; this is a prediction, and one sentence each is all you need.  **Retrieval-augmented generation** hands the model the relevant source text before it answers, so it can quote instead of recall (the *RAG Knowledge Base: Code and No-Code Routes* activity, in two weeks).  Tool use lets the model call a real function for facts it should not be recalling at all, like today's date or an arithmetic result (*Tool Use and Function Calling*, next session).  Critique agents and debate put a second model, or several, in the path to challenge the first one's answer before you see it (*Critique, Consensus, and the LLM Judge*, later in the term).  Match each to the hallucination type it addresses most directly, and say what it does *not* fix.
   - *You've succeeded when*: You have three pairings, each with a one-sentence justification that explains the *mechanism* by which that technique addresses that hallucination type, not only that both appear in the course.

---

## Reflection Prompt

*Personal*: Describe one time you (or someone you observed) accepted an AI output that turned out to be wrong: a hallucinated fact, a fabricated citation, a confidently stated number that was off.  Using today's taxonomy, classify the failure: factual hallucination, faithfulness hallucination, or reasoning error?  What about the response made it seem credible?

*Technical*: Today's evaluation harness used a human-written list of questions with known correct answers.  Identify the three biggest limitations of that approach for evaluating a real agent in a production system.  For each limitation, name a technique (from today or from common sense) that would partly address it.

*Societal*: Identify the cheapest check that would have caught the error you described in the Personal reflection, for example a web search, a database lookup, or a second model's review.  Why was that check not performed at the time?  What does it cost (in time, effort, or money) to add systematic fact-checking to every AI output?  Who should bear that cost: the model developer, the deploying organization, or the end user?

---

-> Coming Up Next: You just predicted which techniques fix which hallucinations.  Next session we build the first one.  In *Tool Use and Function Calling*, the agent stops recalling facts it should be looking up and calls a real function instead, which is the mitigation your Exercise 3 matched to fabricated specifics.  The evaluation harness pattern you built today returns in the RAG Knowledge Base lab's retrieval evaluation and in the Rubric Pipeline lab's rubric pipeline.

## 5.  Further Reading

- Ziwei Ji et al. "Survey of Hallucination in Natural Language Generation."  *ACM Computing Surveys* (2023).
- Melanie Mitchell.  *AI: A Guide for Thinking Humans*, Chapter 3.
- Lin, Hilton, and Evans.  "TruthfulQA: Measuring How Models Mimic Human Falsehoods."  *ACL* (2022).
