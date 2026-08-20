<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Hallucinations and Evaluating Agent Outputs

In the *Why Different Answers Every Time? Sampling, Temperature, and Generation* activity we saw that a model samples plausible continuations — and a model that writes fluently can be fluently wrong. This module names the phenomenon of **hallucination**, explains *why* next-token prediction produces it, and builds our first **evaluation harness** — because an agent we cannot measure is an agent we cannot trust or improve. We move from **mechanism $\rightarrow$ taxonomy $\rightarrow$ measurement $\rightarrow$ mitigation previews**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| Hallucination | A model output that is confident and fluent but factually wrong — not a "mistake" in the human sense, but a consequence of optimizing for plausibility rather than truth | A fabricated but well-formatted academic citation complete with volume, issue, and page numbers |
| Factual hallucination | A specific type: the model asserts something about the world that is simply false, with no source document to contradict | Claiming that a real journal published a specific article that does not exist |
| Faithfulness hallucination | A specific type: the model contradicts or invents beyond a source document it was given — the type most likely to occur in retrieval-augmented systems | Summarizing a paragraph by adding a detail that was not in the original text |
| Reasoning error | A specific type: the model uses correct facts but combines them incorrectly to reach a wrong conclusion | Knowing that the speed of sound is 343 m/s but calculating travel time by multiplying instead of dividing |
| Evaluation harness | A program that runs a model on a fixed set of questions with known correct answers, computes a score automatically, and records the results in a reproducible way | The `tasks` list and scoring loop in today's code cell |
| Exact-match accuracy | A metric that scores 1 for a response containing the correct answer string and 0 otherwise — simple and objective, but strict about phrasing | Scoring "The answer is Canberra" as correct if the gold answer is "canberra" (substring match), but failing "the Australian capital" even though it is correct |

---

# Part I: Why Models Hallucinate

In this part, you will learn why hallucination (a model producing confident but false output) is not a bug that can be patched, but a predictable consequence of how language models are trained — and you will build a taxonomy of three hallucination types that each call for a different fix.

## 1. Fluency Is the Objective, Truth Is Not

Before we look at the mechanism, consider a thought experiment. Imagine training a student to pass a writing class by rewarding them whenever their essays *sounded* like expert writing — correct grammar, confident tone, appropriate vocabulary. That student would quickly learn to produce convincing prose even on topics they know nothing about, because the reward never checked whether the facts were true. Language models face the same dynamic at a massive scale: they are trained to predict what text tends to follow other text, not to verify whether the claims in that text match reality.

**The training objective rewards plausible continuation.** A model is optimized to maximize the probability of the next token given context, $\max \sum_t \log P(x_t \mid x_{<t})$. Nothing in that objective references truth; it references *what text tends to follow other text in the training data*. When the context resembles confident factual writing, the most probable continuation is more confident factual-sounding text — whether or not any real fact supports it.

**Hallucinations cluster where training data is thin.** Specific citations, niche biographies, exact recent statistics, and obscure local facts sit in low-density regions of the training distribution. The model interpolates between patterns it has seen, and interpolation between facts is often fiction. This insight predicts *where* to be suspicious — which is more useful than blanket distrust of everything a model says.

**A useful taxonomy for deciding what to do about it.** *Factual hallucination*: asserting false statements about the world (fix: retrieval, tool use). *Faithfulness hallucination*: contradicting or inventing beyond a provided source (fix: strict grounding instructions, retrieval-augmented generation). *Reasoning error*: correct facts combined by invalid logic (fix: chain-of-thought, critique agents). Each type calls for a different mitigation, and each mitigation is a topic in the coming weeks.

---

## Model 1: The Confident Citation

Imagine this scenario: a student asks a local model for three peer-reviewed sources on a niche topic in coastal ecology and receives the following response: "See Hartman, R. (2018). *Tidal Dynamics of Inland Estuaries*, Journal of Coastal Research, 34(2), 211-228." The journal exists and publishes real research. The article does not exist. The author name appears in the model's training data in other contexts. Every piece of the citation looks individually plausible — that is why it is hard to catch without checking.

### Critical Thinking Questions

1. Explain, using the training objective described above, why every *individual component* of this citation (author format, journal name, year, page range) looks plausible even though the *complete citation* is fabricated.

   > *Hint: The model has seen thousands of correctly formatted citations. It learned what citation text looks like by pattern — author, year, title in italics, journal name, volume, issue, pages. It can reproduce that pattern perfectly while inventing every specific value.*

2. Which category of the hallucination taxonomy does this citation fall into — factual, faithfulness, or reasoning? If you had given the model a PDF of real papers to read before asking for citations, would that change the category of errors you would expect?

   > *Hint: Without a source document, the model is generating from memory (or from pattern). With a source document, any errors in summarizing that document would be faithfulness errors. Could it still produce factual errors about the world beyond the document?*

3. Propose a verification step that a student — or an automated agent — could run before trusting any citation. What specific tool or data source would the agent need access to?

   > *Hint: Think about what databases index academic papers — Google Scholar, CrossRef, PubMed, Semantic Scholar. A verification agent could call one of these APIs with the DOI or title and check whether the paper exists. What happens if the paper exists but the page numbers are wrong?*

---

## 2. Evaluation Foundations

To evaluate an agent we need three things: a **task set** (inputs with known correct outputs), a **metric** (a function that turns a model output and a correct answer into a score), and a **protocol** (fixed model version, parameters, and seed so that results are reproducible and comparable over time). For factual question answering, the simplest metric is **exact-match accuracy**:

$$
\text{accuracy} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\hat{y}_i = y_i]
$$

where $\hat{y}_i$ is the model's predicted answer and $y_i$ is the known correct answer. The indicator function $\mathbb{1}[\cdot]$ (read as "1 if the condition is true, 0 otherwise" — equivalent to Python's `int(condition)`) counts correct answers. Exact match is intentionally harsh — a correct answer phrased differently scores zero — which previews why we will later recruit *another model* as a judge (an LLM-as-evaluator), and why we must then evaluate the judge itself.

A team reports that their agent "seems pretty accurate" after trying a few questions. The most important missing element of a real evaluation is:

[( )] A larger language model with more parameters
[( )] Higher temperature for greater response diversity
[(X)] A fixed task set with known answers, a clearly defined metric, and a reproducible protocol with fixed model and parameters
[( )] A faster computer to run more experiments

---

# Part II: Building a Tiny Evaluation Harness

In this part, you will write a minimal evaluation harness (a program that runs a model on a fixed set of questions with known answers and reports a score) — because "it seems pretty good" is not an engineering standard. By the end, you will have a reusable scaffold for evaluating any agent you build this semester.

## 3. Measure Before You Trust

Before we can trust an agent in a real application, we need to know where it succeeds and where it fails — not a general impression, but a number. The code below is a minimal version of the evaluation infrastructure that underlies every published benchmark in AI research. It is small enough to read in five minutes and powerful enough to reveal real patterns.

---

The code below runs a fixed list of five questions through the model (at temperature 0.0 and a fixed random seed so results are reproducible), checks whether the correct answer appears anywhere in the model's response, and prints a PASS or FAIL for each. Read it carefully before running: you will be asked to critique both the scoring rule and the task set.

## Code Cell

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

Examine the PASS/FAIL output line by line. Before discussing with your group, form your own hypothesis about each result: why did the model pass or fail this particular question?

### Critical Thinking Questions

4. Our scoring rule is `gold in pred` (a substring check — it passes if the correct answer appears anywhere in the model's response). Construct a specific model answer that is *factually wrong* yet scores as PASS, and a specific model answer that is *factually correct* yet scores as FAIL. What does this teach about the relationship between metrics and truth?

   > *Hint: For a wrong-but-PASS example: the question is "What is 17 * 24?" and the gold is "408." What if the model outputs "408 is not actually correct; the real answer is 412"? For a right-but-FAIL example: gold is "mary shelley" and the model outputs "Mary Wollstonecraft Shelley" — does the substring check pass?*

5. Add two questions to the `tasks` list where you predict the model will hallucinate (based on the "thin training data" principle) and two where you predict it will answer correctly. Run them. Was your theory of where models fail predictive?

   > *Hint: Good hallucination-prone questions involve: specific local people or events, very recent information (post-2023), exact statistics like population figures or distances, or niche academic citations. Good reliable questions involve: widely published historical dates, famous authors, capital cities of large countries.*

6. We fixed temperature to 0.0 and seed to 42. Rerun the harness once without changing any parameters and confirm you get identical results. Then explain in one sentence each why a grader, a scientist, and a software debugger each need this reproducibility property.

   > *Hint: A grader needs it so that "running the eval again" gives the same score. A scientist needs it so that a published result can be independently replicated. A debugger needs it so that a bug observed in one run will appear again in the next run.*

> **⚠️ Common Misconception:** Many students assume that if a model gives a wrong answer on a factual question, it "does not know" the answer and will always fail that question. In reality, the same model with the same weights can answer the same question correctly at one temperature setting and fail it at another, or answer it differently in different phrasings of the same question. This is why evaluation requires a *fixed protocol* — not because we distrust the model, but because the model's behavior is genuinely sensitive to parameters and phrasing, and we need to hold those constant to learn anything meaningful.

---

# Part III: Synthesis and Practice

In this part, you will build your own benchmark — a domain-specific task set your team designs, verifies, and will reuse throughout the semester. Getting this right now pays dividends in every future module that compares techniques.

## 4. Exercises

1. *Benchmark sketch.*

   - *What to do*: Draft a 10-item task set for a domain your team knows well — a sport, a fandom, a local community, a scientific field. Specify: the 10 questions, the gold answers, the metric you will use (exact match, substring, or something else), and the full protocol (which model, what temperature, what seed).
   - *Starter hint*: Choose a domain where you can verify the correct answers independently (you know them from experience or can check a reliable source). Make at least two questions "thin training data" questions where you expect the model to struggle. Save this task set — you will reuse it to evaluate retrieval-augmented generation in the *Retrieval-Augmented Generation with Chroma* activity and your project agents at the end of the semester.
   - *You've succeeded when*: Your task set has 10 questions with verified gold answers, a written metric definition, and a written protocol — specific enough that a teammate could run it without asking you any questions.

2. *Calibration probe.*

   - *What to do*: Modify the system prompt to append "State your confidence as high, medium, or low" to each question. Run the 5-item task set and record both accuracy and confidence for each item. Compute accuracy separately within each confidence bucket (high / medium / low).
   - *Starter hint*: Change the prompt in `chat()` to include `" Respond with only the answer and your confidence (high/medium/low), no explanation."` Then parse the confidence out of each response before scoring. A well-calibrated model should have higher accuracy in its "high" confidence bucket than in its "low" bucket.
   - *You've succeeded when*: You have a two-column table (confidence, accuracy) and a one-sentence verdict: is this model's confidence informative, misleading, or uncorrelated with its actual accuracy?

3. *Mitigation preview.*

   - *What to do*: For each of the three hallucination taxonomy categories (factual, faithfulness, reasoning error), name the course topic that most directly addresses it, and write one sentence explaining the connection.
   - *Starter hint*: The three topics to match are: retrieval-augmented generation (the *Retrieval-Augmented Generation with Chroma* activity), tool use / external APIs (the *Tool Use and Function Calling* activity), and critique agents / multi-agent debate (the *Critique and Refine* and *Multi-Agent Debate* activities). Match each to the hallucination type it addresses most directly.
   - *You've succeeded when*: You have three pairings, each with a one-sentence justification that explains the *mechanism* of why that technique addresses that hallucination type — not just that they are both in the course.

---

## Reflection Prompt

*Personal*: Describe one time you (or someone you observed) accepted an AI output that turned out to be wrong — a hallucinated fact, a fabricated citation, a confidently stated number that was off. Using today's taxonomy, classify the failure: was it factual hallucination, faithfulness hallucination, or a reasoning error? What was it about the response that made it seem credible?

*Technical*: The evaluation harness today used a human-written list of questions with known correct answers. Identify the three biggest limitations of that approach for evaluating a real agent deployed in a production system. For each limitation, name a technique (from today or from common sense) that would partially address it.

*Societal*: Identify the cheapest check that would have caught the error you described in the Personal reflection — for example, a web search, a database lookup, or a second model review. Why was that check not performed at the time? What does it cost (in time, effort, or money) to add systematic fact-checking to every AI output? Who should bear that cost — the model developer, the deploying organization, or the end user?

---

→ Coming Up Next: In the *Connecting Agents to the World: MCP and APIs* activity we give agents a standard way to discover and call external tools — one of the mitigations previewed today. The evaluation harness pattern you built here returns in the RAG Knowledge Base Lab's retrieval evaluation and the Rubric Pipeline Lab's rubric pipeline.

## 5. Further Reading

- Ziwei Ji et al. "Survey of Hallucination in Natural Language Generation." *ACM Computing Surveys* (2023).
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 3.
- Lin, Hilton, and Evans. "TruthfulQA: Measuring How Models Mimic Human Falsehoods." *ACL* (2022).
