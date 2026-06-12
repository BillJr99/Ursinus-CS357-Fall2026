# Hallucinations and Evaluating Agent Outputs
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

A model that writes fluently can be fluently wrong. This module names the phenomenon of **hallucination**, explains *why* next-token prediction produces it, and builds our first **evaluation harness**, because an agent we cannot evaluate is an agent we cannot trust. We move from **mechanism $\rightarrow$ taxonomy $\rightarrow$ measurement $\rightarrow$ mitigation previews**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Why Models Hallucinate

## 1. Fluency Is the Objective, Truth Is Not

**The training objective rewards plausible continuation.** A model is optimized to maximize the probability of the next token given context, $\max \sum_t \log P(x_t \mid x_{<t})$. Nothing in that objective references truth; it references *what text tends to follow other text*. When the context resembles confident factual writing, the most probable continuation is more confident factual-sounding writing, whether or not a fact exists to support it.

**Hallucinations cluster where training data is thin.** Specific citations, niche biographies, exact numbers, and recent events sit in low-density regions of the training distribution; the model interpolates, and interpolation between facts is often fiction. This insight predicts *where* to be suspicious, which is more useful than blanket distrust.

**A useful taxonomy.** *Factual hallucination*: asserting false statements about the world. *Faithfulness hallucination*: contradicting or inventing beyond a provided source (the kind RAG is designed to expose). *Reasoning error*: correct facts combined invalidly. Each type calls for a different mitigation.

---

## Model 1: The Confident Citation

A student asks a local model for sources on a niche topic and receives: "See Hartman, R. (2018). *Tidal Dynamics of Inland Estuaries*, Journal of Coastal Research, 34(2), 211-228." The journal exists; the article does not.

### Critical Thinking Questions

1. Explain, using the training objective above, why every *part* of this citation looks right even though the *whole* is fabricated.
2. Which taxonomy category does this fall into? Would providing the model a PDF of real sources change the category of any remaining errors?
3. Propose a verification step a student (or an agent) could run automatically before trusting any citation. What tool would it require?

---

## 2. Evaluation Foundations

To evaluate an agent we need three things: a **task set** (inputs with known correct outputs where possible), a **metric**, and a **protocol** (fixed model, parameters, and seed, so results are reproducible). For factual question answering, the simplest metric is exact-match accuracy:

$$
\text{accuracy} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\hat{y}_i = y_i]
$$

Exact match is harsh (a correct answer phrased differently scores zero), which previews why we will later recruit *another model* as a judge, and why we must then evaluate the judge.

[[MC]]
A team reports that their agent "seems pretty accurate" after trying a few questions. The most important missing element of a real evaluation is:
- ( ) A larger language model
- ( ) Higher temperature for diversity
- (x) A fixed task set with known answers, a defined metric, and a reproducible protocol
- ( ) A faster computer

---

# Part II: Building a Tiny Evaluation Harness

## 3. Measure Before You Trust

---

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

### Critical Thinking Questions

4. Our scoring rule is `gold in pred`, a substring check. Construct a model answer that is *wrong* yet scores as correct, and one that is *right* yet scores as incorrect. What does this teach about metric design?
5. Add two questions where you predict the model will hallucinate (thin training data, per Section 1) and two where it will not. Run them. Was your *theory of where models fail* predictive?
6. We fixed temperature 0 and seed 42. Rerun once to confirm identical results, then explain in one sentence why a grader, a scientist, and a debugger each need this property.

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Benchmark sketch.* Draft a 10-item task set for a domain your team knows well (a sport, a fandom, a hometown). Specify the metric and the protocol. Save it: you will reuse it to evaluate RAG in week 5 and your project agents in November.
2. *Calibration probe.* Append "State your confidence as high, medium, or low" to each task. Compute accuracy *within each confidence bucket*. Is the model's confidence informative?
3. *Mitigation preview.* For each taxonomy category in Section 1, name the upcoming course topic (retrieval, tool use, critique agents) that most directly addresses it, and justify the pairing in one sentence each.

---

## Reflection Prompt

In your notebook: describe one time you (or someone you observed) accepted an AI output that turned out to be wrong. Using today's taxonomy, classify the failure, and identify the cheapest check that would have caught it.

---

## 5. Further Reading

- Ziwei Ji et al. "Survey of Hallucination in Natural Language Generation." *ACM Computing Surveys* (2023).
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 3.
- Lin, Hilton, and Evans. "TruthfulQA: Measuring How Models Mimic Human Falsehoods." *ACL* (2022).
