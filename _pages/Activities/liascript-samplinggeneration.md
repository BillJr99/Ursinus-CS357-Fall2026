<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-samplinggeneration.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-samplinggeneration.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Why Different Answers Every Time?  Sampling, Temperature, and Generation

You have already turned this dial twice.  In *Running Your Own AI* you set temperature to 0, then to 1, and watched six answers to the same prompt; in the *Agent Loop* activity you pinned it to 0 so the loop's parser would find the same strings every run.  You know what it *does*.  Today you find out what it *is*.

The short answer, and the resolution of the mystery your teams formed hypotheses about back in *Welcome: What Is AI, and What Is an Agent?*: a language model computes a **probability distribution over the next word-piece (token)**, and the system **samples** from it, rolling a weighted die at each step.  Temperature is the number that reshapes the die before the roll.

We move from **next-token prediction $\rightarrow$ softmax and temperature $\rightarrow$ top-k and top-p $\rightarrow$ experiments on our own stack**, and we connect every knob to agent design.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| Token | A unit of text (roughly a word, a word-part, or a punctuation mark) that the model reads and writes one at a time | The sentence "The cat sat." is four tokens: "The", " cat", " sat", "." |
| Softmax | A mathematical function that converts raw model scores (called logits) into a probability distribution that adds up to 1.0, making the scores comparable and interpretable | Turning logits of (5, 2, -1) for (Paris, Lyon, banana) into probabilities like (0.95, 0.05, 0.001) |
| Temperature | The dial you turned in *Running Your Own AI*, stated precisely: a number that controls how "peaked" or "flat" the probability distribution is. Low temperature makes the most likely token nearly certain; high temperature makes unlikely tokens more competitive | The same `temperature` you passed in `options` and dragged in OpenWebUI's Advanced Params, now worked by hand in Model 1 |
| Top-k sampling | A technique that keeps only the k highest-probability tokens before sampling, discarding the long tail of unlikely options | With k=5, only the five most probable next words are considered, even if there are 50,000 in the vocabulary |
| Top-p (nucleus) sampling | A technique that keeps the smallest group of tokens whose combined probability reaches a threshold p, adapting to how confident the model is at each step | With p=0.9, if Paris alone has probability 0.92, only Paris is kept; if the top 10 words share 0.9 probability, all 10 are kept |
| Greedy decoding | The strategy of always picking the single most probable next token, equivalent to temperature = 0; deterministic but sometimes repetitive or locally optimal but globally suboptimal | An agent with temperature=0.0 that always picks the same action regardless of context |

---

# Part I: Generation as Repeated Prediction

In this part, you will work out by hand how a language model converts raw scores into a probability distribution and then samples from it, resolving the mystery from the *Welcome: What Is AI, and What Is an Agent?* activity of why identical prompts produce different outputs.  The math here (softmax and temperature) will recur every time you tune an agent's behavior for the rest of the semester.

## 1.  One Token at a Time

Before we look at the math, consider how autocomplete on your phone works: it suggests the next word based on what you have typed.  A language model does exactly the same thing, but instead of a fixed list of three suggestions, it assigns a probability to every word in its entire vocabulary (often 50,000 or more), then picks one, and repeats this process for every single word in its response.  That is why a single early "wrong pick" can send the whole response in a surprising direction, and why the same prompt can produce different responses on different runs.

A language model is a next-token predictor.  Given the tokens so far, it outputs a raw score (called a *logit*, pronounced "low-jit," short for log-odds unit, just a number with no fixed range) $z_i$ for every token $i$ in its vocabulary, then converts scores to probabilities with the **softmax** function (a formula that squashes any set of numbers into values that sum to 1.0):

$$
P(i) = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}
$$

The system samples one token from this distribution, appends it to the text, and repeats until a stop token appears.  Generation is a loop of single predictions (one word-piece at a time) which means a single early sampling choice can steer the entire continuation.  This is the test of your hypotheses from the *Welcome* activity: the randomness lives in the *sampling step*, not in the model weights, which stay fixed.

Temperature $T$ reshapes the distribution.  As $T \to 0$, the highest-scoring token dominates and sampling approaches deterministic *greedy decoding* (always picking the top word).  As $T$ grows, the distribution flattens and less-likely tokens gain probability.  Temperature does not add knowledge; it redistributes confidence across the existing options.

---

## Model 1: Temperature by Hand

Suppose the model's logits (raw scores) for the next word after "The capital of France is" are: Paris $z=5$, Lyon $z=2$, banana $z=-1$. We will compute what temperature does to the probability of each word.

### Critical Thinking Questions

1.  Compute (calculator permitted) $P(\text{Paris})$ at $T=1$. Now recompute at $T=0.5$ and at $T=2$. The Recorder tabulates all three values in a single table with columns for $T$ and rows for each word.

   > *Hint: For each temperature, compute $e^{z/T}$ for all three words, add those three values together to get the denominator, then divide each word's $e^{z/T}$ by the denominator.  For Paris at T=1: $e^5 \approx 148.4$, $e^2 \approx 7.4$, $e^{-1} \approx 0.37$, sum $\approx 156.1$, so $P(\text{Paris}) \approx 148.4 / 156.1 \approx 0.951$.*

2.  At which temperature does "banana" have the best relative chance of being selected?  Generalize: what does increasing temperature do to the *tail* of the distribution (the words that started out with very low scores)?

   > *Hint: Compare the ratio $P(\text{banana}) / P(\text{Paris})$ at $T=1$ versus $T=2$. Does the gap shrink or grow as temperature rises?*

3.  An agent inside a loop must output exactly `calc(...)` or `Final Answer:`.  Using your calculated table, argue for the temperature you would set for an agent's reasoning step, and identify what could still go wrong even at $T=0$.

   > *Hint: Even at $T=0$ (greedy decoding), the model always picks the top token, but what if the top token is part of a malformed tool call?  Greedy does not guarantee correctness, only consistency.*

---

## 2.  Truncation: Top-k and Top-p

Temperature reshapes the whole distribution; **truncation** removes the options the model considers entirely.  **Top-k** sampling keeps only the $k$ highest-probability tokens and renormalizes the remaining probabilities to sum to 1.0.  **Top-p (nucleus) sampling** keeps the smallest group of tokens whose combined probability reaches the threshold $p$:

$$
V_p = \text{smallest } V' \text{ such that } \sum_{i \in V'} P(i) \ge p
$$

The key advantage of top-p over top-k is that top-p **adapts to the model's confidence**: when the model is very sure (one word has probability 0.95), the nucleus contains just that word; when many continuations are plausible (ten words each with probability 0.09), the nucleus widens to include all of them.  In practice, creative writing tasks often favor higher temperature (0.7-1.0) combined with top-p near 0.9, while agentic control steps that must output exact tool calls favor temperature near 0.0.

A distribution assigns probabilities: Paris 0.90, Lyon 0.06, Marseille 0.03, banana 0.01.  With top-p $= 0.95$, the candidate set is:

[( )] Paris only (0.90 already exceeds 0.95 minus a rounding edge)
[(X)] Paris and Lyon (0.90 + 0.06 = 0.96, which first reaches or exceeds 0.95)
[( )] Paris, Lyon, and Marseille
[( )] All four tokens


## 3.  Other Common Generation Parameters

Temperature, top-k, and top-p decide *which* token to pick.  A few other parameters shape *how much* the model generates and *what it avoids*.  You pass all of them the same way (inside the Ollama `options` dictionary) and they map to top-level fields on OpenAI-compatible endpoints.

| Parameter (Ollama) | OpenAI-API name | What it does | Reach for it when |
|--------------------|-----------------|--------------|-------------------|
| `num_predict` | `max_tokens` | Caps how many tokens the model may generate before it must stop. | You want to bound length, latency, or cost, or cut off a run-on answer. |
| `repeat_penalty` | `frequency_penalty` / `presence_penalty` | Down-weights tokens the model has already produced, discouraging loops and repetition. | The model gets stuck repeating a word or phrase, especially at low temperature. |
| `stop` | `stop` | A list of strings that, when generated, immediately end the response. | You want the model to halt at a delimiter: e.g. `"\n\n"`, `"</answer>"`, or a role tag. |
| `seed` | `seed` | Fixes the random draw so a given prompt + settings reproduces the same output (see Exercise 1). | You need reproducible experiments or tests. |

Two notes on the penalties: Ollama exposes a single `repeat_penalty` (a multiplier, typically 1.0-1.3), while the OpenAI API splits the idea into `frequency_penalty` (scales with how *often* a token has appeared) and `presence_penalty` (a flat penalty once a token appears *at all*).  Both attack the same failure (degenerate repetition) from slightly different angles.

The cell below exercises three of these knobs: a short `num_predict` cap, a `repeat_penalty` to break loops, and a `stop` sequence.

## Code Cell

```python
import requests

def generate(prompt, **options):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": options,
            "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[sampling:generate] {e}")
        import traceback; traceback.print_exc()
        return ""

# 1. num_predict caps the length (here, a deliberately short answer).
print("--- num_predict=12 ---")
print(generate("List the planets of the solar system.", temperature=0.0, num_predict=12))

# 2. repeat_penalty discourages the model from looping on the same token.
print("\n--- repeat_penalty=1.3 ---")
print(generate("Say the word 'buffalo' and then keep going.", temperature=0.8, repeat_penalty=1.3))

# 3. stop ends generation as soon as the string appears.
print("\n--- stop at first newline ---")
print(generate("Write a numbered list of three fruits.", temperature=0.0, stop=["\n"]))
```

> **Note:** On an OpenAI-compatible endpoint (including OpenWebUI's `/api/chat/completions`), these move out of the `options` dict to the top level of the request body, and `num_predict` becomes `max_tokens`.

> **Common Misconception:** The `top_k` in this activity is a **sampling** parameter; it limits which *next tokens* the model may choose from.  It is a completely different knob from the `top_k` (often written `k` or `n_results`) you will meet in **Retrieval-Augmented Generation**, where it means "how many *document chunks* to retrieve."  Same name, different layer of the system: one truncates a probability distribution over the vocabulary; the other sets the size of a search result set.  See the *Retrieval-Augmented Generation with Chroma* activity, where retrieval `k` is tuned.

---

# Part II: Experiments on Your Stack

In this part, you will run a controlled experiment that makes the theory from Part I visible: you will sample the same prompt eight times at three different temperatures and count how often the answers diverge.  This turns an intuitive observation into a measurable, reproducible result.

## 4.  Measuring Variability

We quantify "how different are the answers" by sampling the same prompt multiple times and counting how many distinct outputs appear.  This turns an intuitive observation ("it seems to vary a lot at high temperature") into a measurable result.

---

The code below asks the model to name a single animal eight times at each of three temperature settings and uses a `Counter` (a Python dictionary that counts occurrences) to tally how many distinct answers appear.  A temperature of 0.0 should produce the same answer every time; higher temperatures should spread answers across more options.

## Code Cell

```python
import requests
from collections import Counter

def chat(prompt, temperature, model="llama3.2", top_p=0.9):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": temperature, "top_p": top_p, "seed": -1},
            "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[sampling:chat] {e}")
        import traceback; traceback.print_exc()
        return ""

prompt = "Name one animal. Respond with a single word."
for T in [0.0, 0.7, 1.5]:
    answers = Counter(chat(prompt, T) for _ in range(8))
    print(f"T={T}: {dict(answers)}")
```

---

## Model 2: Reading the Results

Examine the counter output for each temperature.  Notice which temperatures produce the same answer eight times, which produce two or three variations, and which produce eight completely different answers.

### Critical Thinking Questions

4.  At $T=0.0$, did all eight runs produce the same answer?  If any runs differed, propose where residual non-determinism could enter a real serving system; consider hardware-level floating-point rounding, batching multiple requests together, and whether your Ollama server truly respects seed=-1.

   > *Hint: Even "deterministic" floating-point arithmetic can give slightly different results on different CPU/GPU hardware due to the order of operations in parallel computation.  A production model server may batch several requests together, which changes the arithmetic order.*

5.  Sketch (or describe) the shape of a graph with temperature on the x-axis and "number of distinct answers out of 8 runs" on the y-axis.  Where is the knee of the curve for your model, the temperature at which answers begin to diverge noticeably?

   > *Hint: Plot three points: T=0, T=0.7, T=1.5.  Is the transition gradual or sudden?  Does the knee appear closer to 0 or closer to 1?*

6.  Repeat the experiment with the prompt "Write the first line of a poem about autumn."  Should an agent that *drafts creative text* and an agent that *routes requests to tools* share the same temperature setting?  Assign each a specific temperature value and write one sentence defending each choice.

   > *Hint: For the routing agent, think about what happens if "route to weather tool" becomes "route to music tool" just because of random sampling.  For the creative agent, think about what "always the same first line" means for a poem generator.*

---

---

# Part IIb: Tuning the Dials on Purpose

You have seen what temperature does to one distribution.  Now turn the dial systematically, record what happens, and build a parameter policy you can defend: which settings for which task, and why.  This is the part you will actually reuse, because every lab from here on asks you to pick these numbers.

## Softmax and Temperature, Revisited Visually

### The Math With Real Numbers

We will work through a concrete 5-token example and trace what happens to each token's probability as we change temperature.  This is the same math from the Sampling activity; now we measure the *entropy* of the resulting distribution so we can connect the numeric output to a single summary quantity.

The softmax with temperature is:

$$
P(i) = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}
$$

Entropy of the resulting distribution is:

$$
H = -\sum_i P(i) \log P(i)
$$

High entropy means the distribution is flat: the model is uncertain.  Low entropy means the distribution is peaked: the model is confident.

---

### Code Cell

```python
import math

def softmax_temp(logits, temperature):
    scaled = [l / temperature for l in logits]
    max_l = max(scaled)
    exp_vals = [math.exp(l - max_l) for l in scaled]
    total = sum(exp_vals)
    return [e / total for e in exp_vals]

def entropy(probs):
    return -sum(p * math.log(p + 1e-10) for p in probs)

# Toy example: 5 tokens with raw logit scores
VOCAB = ["Paris", "Lyon", "London", "banana", "croissant"]
LOGITS = [4.5, 2.1, 1.8, 0.3, -0.5]

print(f"{'T':>5}  {'Paris':>8}  {'Lyon':>8}  {'London':>8}  {'banana':>8}  {'croissant':>10}  {'entropy':>8}")
print("-" * 72)
for T in [0.1, 0.5, 1.0, 1.5, 2.0]:
    probs = softmax_temp(LOGITS, T)
    H = entropy(probs)
    print(f"{T:>5.1f}  " + "  ".join(f"{p:>8.4f}" for p in probs) + f"  {H:>8.4f}")
```

**Expected output (approximate):**

```
    T     Paris      Lyon    London    banana  croissant   entropy
------------------------------------------------------------------------
  0.1    1.0000    0.0000    0.0000    0.0000     0.0000    0.0000
  0.5    0.9927    0.0065    0.0007    0.0001     0.0000    0.0405
  1.0    0.8778    0.0838    0.0330    0.0050     0.0005    0.4673
  1.5    0.7468    0.1413    0.0826    0.0227     0.0066    0.7893
  2.0    0.6406    0.1687    0.1148    0.0528     0.0231    1.0183
```

---

#### Critical Thinking Questions

1.  At T=0.1, Paris has probability ≈1.000.  At T=2.0, Paris has probability ≈0.64.  The **logits** did not change between runs; only T changed.  What is the mathematical mechanism by which temperature reshinks Paris's dominance?  Walk through the exponent step for Paris at T=0.1 vs. T=2.0.

   > *Hint: At T=0.1, the scaled logit for Paris is 4.5/0.1 = 45.  For banana it is 0.3/0.1 = 3.  The difference is 42 log-units; $e^{42}$ is astronomically large compared to $e^3$. At T=2.0, Paris becomes 4.5/2.0 = 2.25, banana becomes 0.3/2.0 = 0.15, a difference of only 2.1 log-units.  The ratio $e^{2.1} \approx 8$ is much less extreme.*

2.  Entropy measures how unpredictable the distribution is.  As temperature increases from 0.1 to 2.0, entropy:
   [( )] Decreases, because the distribution becomes more random
   [(X)] Increases, because a flatter distribution is harder to predict
   [( )] Stays the same, because the logits are fixed
   [( )] Increases then decreases after a peak at T=1.0

3.  Top-k=3 applied to the 5-token example above keeps only Paris, Lyon, and London (the three highest-probability tokens) and renormalizes.  Top-p=0.90 at T=1.0 would keep only Paris (≈0.88 ≥ 0.90, approximately) and stop.  But at T=2.0, top-p=0.90 would need to include Paris, Lyon, and London to accumulate at least 0.90 of the total probability mass.  Why does the same top-p threshold require more tokens at higher temperature?

   > *Hint: The threshold is based on cumulative probability, not a count.  At T=1.0, Paris alone captures nearly 0.88 of the mass; you need very few tokens to reach 0.90.  At T=2.0, Paris captures only 0.64, so you must add Lyon (0.17), and still need London (0.11) to push past 0.90.  The flatter distribution distributes mass across more tokens, so you need more of them to reach the same cumulative threshold.*

4.  A classmate claims: "I should always use top-p instead of top-k because top-p adapts to the model's confidence."  Give one situation where top-k might be preferable, and explain why.

   > *Hint: Consider a task where you want to strictly limit the vocabulary size for safety or efficiency reasons, for example, generating a list where you only ever want one of five predefined options.  Top-p might include 3 tokens when the distribution is flat or 1 when it is peaked.  Top-k enforces a fixed budget regardless.*

---

## Real Model Experiments

### A Systematic Sweep

We now run a structured experiment: four task types × four temperature settings × three repetitions.  This gives you 48 data points to analyze.  The Manager assigns one task row to each team member for the first sweep; then you rotate and check each other's rows.

Fill in the observation table as you go.  The Recorder keeps the table and posts it to the discussion board.

---

### Code Cell

```python
import requests
import json
import time

def query(prompt, model="llama3.2", temperature=1.0, top_p=0.9, top_k=40):
    try:
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False,
                  "options": {"temperature": temperature,
                              "top_p": top_p,
                              "top_k": top_k}},
            timeout=120)
        return r.json()["response"].strip()
    except Exception as e:
        print(f"[query] {e}")
        return ""

TEST_PROMPTS = {
    "factual": "What is the capital of France? Answer in one word.",
    "creative": "Write the first line of a science fiction novel.",
    "code":     "Write a Python one-liner that reverses a string.",
    "list":     "Name three programming languages. Answer as a comma-separated list.",
}

TEMPERATURES = [0.0, 0.5, 1.0, 1.5]

for task, prompt in TEST_PROMPTS.items():
    print(f"\n=== {task.upper()} ===")
    for T in TEMPERATURES:
        outputs = []
        for _ in range(3):
            outputs.append(query(prompt, temperature=T))
            time.sleep(0.5)
        print(f"T={T}: {outputs}")
```

---

### Observation Table (Recorder fills this in)

| Task | T=0.0 (run 1, 2, 3) | T=0.5 (run 1, 2, 3) | T=1.0 (run 1, 2, 3) | T=1.5 (run 1, 2, 3) | Consistent? |
|------|---------------------|---------------------|---------------------|---------------------|-------------|
| factual | | | | | |
| creative | | | | | |
| code | | | | | |
| list | | | | | |

"Consistent?" column: yes (all 3 identical) / partial (2/3 same) / no (all different).

---

#### Critical Thinking Questions

5.  At T=0.0, you ran the factual question three times and (likely) got the same answer all three times.  Is this because the model "knows" the right answer, or because it always picks the highest-probability token?  How would you design an experiment to tell the difference?

   > *Hint: Ask the model a factual question where the correct answer is less well-known: for example, "What is the capital of Burkina Faso?"  Does it still give a consistent answer at T=0?  Is that answer correct?  A model that always gives the same wrong answer at T=0 is being consistent, not knowledgeable.*

6.  For the code generation task, what happened at T=1.5?  Did the generated Python still run without a syntax error?  Why might high temperature be more harmful for code generation than for creative writing?

   > *Hint: In creative writing, any plausible continuation is acceptable; there is no "correct" first line for a science fiction novel.  In Python code, a single misplaced character (a wrong parenthesis, a misspelled keyword, an incorrect indentation level) causes a syntax error and the code fails entirely.  High temperature makes rare characters more likely at every step, which is fine for prose but catastrophic for code that must exactly match a grammar.*

7.  A developer wants their customer service chatbot to give exactly the same answer to the same question every time.  They should set temperature=0 and top_k=1.
   [(X)] True; T=0 and top_k=1 both force greedy decoding, giving deterministic outputs on most hardware
   [( )] False; there is no way to make an LLM deterministic
   [( )] True, but only top_k=1 is needed; temperature has no additional effect
   [( )] False; even at T=0, the model might generate different outputs due to random seeding

   > **Common Misconception:** "Lower temperature = better answers."  This is not true as a general rule.  For creative tasks, low temperature produces repetitive, generic outputs; the model keeps generating the most statistically common continuation, which tends to be bland.  For factual tasks, low temperature reduces hallucination risk but can also prevent the model from adapting its phrasing to the user's question.  Temperature is a tool you choose to match the task; there is no universally correct setting.  The question is always: *how much variation is acceptable, and how much randomness does the task benefit from?*

8.  The list task (naming three programming languages) showed variation at T=1.5.  The same three languages will appear at T=0.0 almost every time.  What does the variation at high temperature tell you about what the model "believes" about popular programming languages?

   > *Hint: At T=0, the model always picks the single highest-probability token at each step, which means the highest-probability language name starts the list.  At T=1.5, languages with lower (but non-negligible) probability start appearing.  The variation shows you the shape of the model's distribution over programming language names, not just the single most-common one.*

---

## Task-Parameter Matching

### Building a Parameter Policy

Now that you have empirical data, use it to build a principled parameter guide.  The table below lists five deployment scenarios.  Two are filled in as examples; your team fills in the remaining three.

| Task | Recommended Temperature | Recommended top_p | Recommended top_k | Reasoning |
|------|------------------------|-------------------|-------------------|-----------|
| Legal document summarization | 0.1-0.2 | 0.85 | 20 | Faithfulness to source is paramount; variation is a liability. Low T keeps output close to the most-probable (most-supported) summary; tight top_p and top_k prevent hallucinated details. |
| Marketing tagline generation (10 options) | 1.0-1.3 | 0.95 | 50 | We *want* diverse, creative outputs; the whole point is to explore many options. High T and wide nucleus give the model room to be surprising. We will pick the best option ourselves. |
| Extracting JSON fields from a form | | | | |
| Writing a first-draft blog post intro | | | | |
| Answering student quiz questions with explanation | | | | |

---

#### Critical Thinking Questions

9.  For the JSON extraction task, argue for or against using top_p=0.50 (very narrow nucleus).  What risk does a very narrow nucleus introduce that a slightly wider one (top_p=0.85) avoids?

   > *Hint: With top_p=0.50, if the model is uncertain between two valid JSON field names (e.g., "first_name" vs. "firstName"), one of them might be excluded from the nucleus.  The model is forced to pick from the remaining tokens, which might be syntactically invalid.  A slightly wider nucleus keeps both plausible options available.  The risk of going too narrow is that you exclude correct options when the model is uncertain about the right answer.*

10.  A team member proposes using temperature=0 for *all* tasks in a production agent to ensure reproducibility.  What two specific failure modes does this introduce that a moderate temperature (T=0.3-0.5) would mitigate?

    > *Hint: (1) Repetition loops: at T=0 without a repetition penalty, the model can get stuck generating the same token forever because the highest-probability token never changes. (2) Failure to rephrase: if the exact highest-probability phrasing is ambiguous or does not match the user's context, the model cannot adapt; it always produces the same phrasing. A small temperature allows the model to occasionally deviate from the single most likely token and avoid both of these traps.*

11.  You are running a Q&A system over a medical reference database.  The system retrieves relevant passages (RAG) and asks the model to answer based only on those passages.  For the generation step, you should:
   [( )] Use high temperature (T=1.5) to ensure creative, comprehensive answers
   [(X)] Use low temperature (T=0.1-0.3) and low top_p to keep the answer close to the retrieved evidence
   [( )] Use top_k=1 to guarantee the model only repeats the retrieved text verbatim
   [( )] Temperature does not matter when using RAG, since the retrieved context constrains the answer

---

## Build Your Own Parameter Guide

### Three Personas, Three Policies

Your team's final deliverable for today is a one-page parameter guide for three deployment personas.  Each persona should specify temperature, top_p, top_k, and one "edge case" where you would push toward the boundary of the recommended range.

**Persona 1: Creative Writing Assistant.**  Helps users brainstorm novel ideas, character names, plot twists, and opening lines.

**Persona 2: Coding Helper.**  Suggests function implementations, explains errors, and writes unit tests.  Users expect working code.

**Persona 3: Factual Q&A Bot.**  Answers student questions about course content.  Users expect accuracy; a wrong answer confidently stated is worse than no answer.

For each persona, fill in:

- Temperature range (e.g., 0.8-1.2)
- top_p setting
- top_k setting
- One scenario where you would go toward the *lower* bound of your temperature range
- One scenario where you would go toward the *upper* bound of your temperature range
- One parameter you would *not* change for this persona and why

The Presenter shares the team's guide with the class.  The Reflector identifies where the three guides conflict and what that conflict reveals about parameter trade-offs.

---

### Code Cell

```python
import requests
import time

def query(prompt, model="llama3.2", temperature=1.0, top_p=0.9, top_k=40):
    try:
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False,
                  "options": {"temperature": temperature,
                              "top_p": top_p,
                              "top_k": top_k}},
            timeout=120)
        return r.json()["response"].strip()
    except Exception as e:
        print(f"[query] {e}")
        return ""

# Verify your parameter policies by running the same prompt across your recommended ranges

PERSONAS = {
    "creative_assistant": {
        "prompt": "Suggest an unusual name for a villain in a science fiction novel.",
        "low_t": 0.7, "high_t": 1.3,
        "top_p": 0.95, "top_k": 50,
    },
    "coding_helper": {
        "prompt": "Write a Python function that returns the nth Fibonacci number using recursion.",
        "low_t": 0.1, "high_t": 0.5,
        "top_p": 0.85, "top_k": 20,
    },
    "factual_qa": {
        "prompt": "In what year did World War II end?",
        "low_t": 0.0, "high_t": 0.3,
        "top_p": 0.80, "top_k": 10,
    },
}

for persona, cfg in PERSONAS.items():
    print(f"\n=== {persona.upper()} ===")
    for label, T in [("low-T", cfg["low_t"]), ("high-T", cfg["high_t"])]:
        outputs = [query(cfg["prompt"], temperature=T,
                         top_p=cfg["top_p"], top_k=cfg["top_k"])
                   for _ in range(3)]
        print(f"T={T} ({label}): {outputs}")
        time.sleep(1)
```

---

#### Critical Thinking Questions

12.  Run the coding helper at T=0.5 (low end) and T=0.5 with top_k=5 (very restricted).  Do you notice a difference in output quality?  What does restricting top_k further do to code that restricts temperature alone does not?

    > *Hint: Temperature reshapes the whole probability distribution; top_k discards the long tail entirely. In code generation, the long tail includes both rare variable names (which might be acceptable) and invalid syntax tokens (which are never acceptable). Restricting top_k aggressively prevents the model from ever selecting an obviously wrong token, even if temperature would have given it a small but nonzero chance.*

13.  A student on your team argues: "We should just use T=0 for all three personas and add a post-processing step to paraphrase or diversify the output."  What are the advantages of this approach?  What does it lose compared to sampling with appropriate temperature?

    > *Hint: Advantages: reproducibility, debuggability, and the safety of greedy outputs for factual tasks. What it loses: the diversity comes from a second model pass, which introduces its own parameters, cost, and failure modes. The original model's rich probability distribution (which encodes "second-best" and "third-best" options that are linguistically plausible) is thrown away at T=0 before the paraphraser ever sees it.*

---

# Part III: Synthesis and Practice

> Work through this at home.  It shows the renormalization step that most explanations of top-k and top-p leave out.

### Worked Example: top-k and top-p, including the step everyone skips

The multiple-choice item above hands you a finished distribution and asks only which tokens fall inside the nucleus.  That is the easy half.  The half that actually matters (and the one that silently changes what your agent emits) is **renormalization**: after you throw tokens away, the survivors no longer sum to 1, so you have to divide by what is left.

Start from the same logits as Model 1: Paris $z=5$, Lyon $z=2$, banana $z=-1$, and add Marseille $z=1$.

**Step 1: softmax at $T=1$.**

| Token | $z$ | $e^{z}$ | $P = e^z / \sum$ |
|---|---|---|---|
| Paris | 5 | 148.41 | 0.9007 |
| Lyon | 2 | 7.389 | 0.0448 |
| Marseille | 1 | 2.718 | 0.0165 |
| banana | −1 | 0.368 | 0.0022 |
| | | **158.89** | **0.9642** |

(The probabilities shown are rounded; they sum to 1 before rounding.)

**Step 2: top-k with $k = 2$.** Keep Paris and Lyon.  Discard the rest.

Surviving mass: $0.9007 + 0.0448 = 0.9455$. **This is not 1, so it is not yet a distribution.**  Divide each survivor by the surviving mass:

| Token | $P$ before | $P$ after renormalizing |
|---|---|---|
| Paris | 0.9007 | $0.9007 / 0.9455 = $ **0.9526** |
| Lyon | 0.0448 | $0.0448 / 0.9455 = $ **0.0474** |
| | | sum = **1.0000** yes |

Notice Paris's probability *went up* (from 0.9007 to 0.9526) without its logit changing at all.  Truncation is not a neutral filter; it redistributes the discarded mass onto the survivors, proportionally.  Every token you cut makes the leaders more likely.

**Step 3: top-p with $p = 0.9$, same distribution.**  Accumulate from the top until you reach $p$:

| Token | $P$ | Running total | In the nucleus? |
|---|---|---|---|
| Paris | 0.9007 | 0.9007 | yes, and 0.9007 ≥ 0.9, so we stop |
| Lyon | 0.0448 | - | no |

The nucleus is **Paris alone**.  Renormalizing a single survivor gives $0.9007 / 0.9007 = 1.0$; the sampler is now deterministic, at a temperature you never set to zero.

This is the whole lesson.  On the *same* distribution, $k=2$ leaves Lyon a 4.7% chance and $p=0.9$ leaves it none.  Top-p adapts to confidence: when the model is sure, the nucleus collapses to one token; when it is unsure, the nucleus widens.  Top-k does not adapt; $k=2$ keeps exactly two candidates whether the model is certain or hopelessly torn.

On the distribution above, you set top-p = 0.95 instead of 0.9.  What is Lyon's probability after renormalization?

[( )] 0.0448, unchanged; renormalization only affects the top token
[(X)] 0.0474; the nucleus is {Paris, Lyon} with mass 0.9455, and 0.0448 / 0.9455 = 0.0474
[( )] 0.05, because top-p rounds the nucleus to the threshold
[( )] 0; Lyon falls outside any nucleus below p = 0.99

> **Watch out!**  Because truncation renormalizes, **top-k and top-p interact with temperature in ways that are easy to get backwards.**  Raising temperature flattens the distribution, which *widens* the top-p nucleus (more tokens are needed to reach $p$), so turning temperature up while leaving top-p fixed increases randomness twice over.  For an agent that must emit an exact tool call, this compounding is exactly what you do not want.


> **Common Misconception:** Students often assume that top-p = 0.9 means "keep the top 90% of tokens by count", for example, keeping 45,000 out of 50,000 vocabulary entries.  In reality, top-p keeps the *smallest set of tokens* needed to reach 90% of the *total probability mass*.  Because probability mass is extremely concentrated in the top few tokens, top-p = 0.9 typically keeps only 5-50 tokens, not thousands.  The long tail of the vocabulary collectively holds very little probability.

---


In this part, you will apply the sampling vocabulary to real design decisions (choosing temperature and top-p settings for different agent roles) and close the loop on the hypotheses your team formed in the *Welcome: What Is AI, and What Is an Agent?* activity.

## 5.  Exercises

1.  *Seeded reproducibility.*

   - *What to do*: Set the `seed` option to a fixed integer (for example, 42) and run the same prompt five times.  Confirm that all five outputs are identical.  Then change the seed to 99 and show that a different (but again consistent) output results.  Explain in writing why reproducibility matters for grading, science, and agent debugging.
   - *Starter hint*: Change `"seed": -1` in the code cell to `"seed": 42`.  Run the cell twice and compare.  Then change to `"seed": 99` and run again.  If outputs differ within the same seed, note whether your Ollama version and hardware support seeded inference.
   - *You've succeeded when*: You have side-by-side outputs for seed=42 (five identical runs) and seed=99 (a different but consistent output), plus a two-sentence explanation of why reproducibility matters in each of the three named contexts.

2.  *Sampling policy table.*

   - *What to do*: For your future final-project agent team, draft a table assigning temperature and top-p values to each of four agent roles: planner, critic, writer, and judge.  Provide a one-sentence justification for each assignment.
   - *Starter hint*: Start with extremes: the planner and critic need to make consistent, structured decisions (low temperature), while the writer benefits from variety (higher temperature).  The judge needs to be consistent but not robotic.  Fill in the middle ground.
   - *You've succeeded when*: Your table has four rows, two columns of parameters, and four one-sentence justifications that reference today's vocabulary (distribution, determinism, nucleus, etc.).

3.  *Hypothesis closure.*

   - *What to do*: Return to the hypotheses your team formed in the *Welcome* activity about why identical prompts produced different outputs.  The Recorder writes one paragraph for each hypothesis: confirmed, refuted, or refined, with specific evidence from today's experiment.
   - *Starter hint*: Common week-1 hypotheses include "the model stores different versions," "time-of-day affects the server," "the model re-reads the internet," or "there is a random element in the generation."  Map each to today's sampling explanation.
   - *You've succeeded when*: Every hypothesis from the *Welcome* activity has been addressed in writing, and each verdict (confirmed / refuted / refined) is backed by a specific observation from today's temperature experiments.

---

## Reflection Prompt

*Personal*: People often describe high-temperature output as more "creative" and low-temperature output as more "correct."  Having seen the math, do you accept the word "creative" as a description of what high temperature does?  What intuitions about creativity does the sampling framing fit well, and which does it miss?

*Technical*: You are designing an agent that writes first drafts of cover letters and then evaluates them for tone consistency with a company's stated values.  What temperature would you set for the drafting step versus the evaluation step, and why?  Would you use top-p, top-k, or neither for the evaluation step?

*Societal*: The randomness in language model generation means that the same question can produce very different answers for different users at the same moment.  What are the fairness implications of this variability, for example, in a system that uses AI to screen job applications or answer student questions?  Should production systems for high-stakes decisions use temperature 0?

---

-> Coming Up Next: We know how models generate text, but how do we know whether what they generate is *correct*?  In the *Hallucinations and Evaluating Agent Outputs* activity we build our first evaluation harness, measure hallucination rates, and learn why "it seems pretty good" is not good enough.

## 6.  Further Reading

- Ari Holtzman et al. "The Curious Case of Neural Text Degeneration."  *ICLR* (2020).  The paper that introduced nucleus sampling.
- Tom Yeh.  *AI by Hand*, softmax worksheets.
- Melanie Mitchell.  *AI: A Guide for Thinking Humans*, Chapter 3.
- Ollama parameter reference (the `options` block: `temperature`, `top_k`, `top_p`, `repeat_penalty`, `num_predict`, `seed`, `stop`): https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values and the API docs at https://github.com/ollama/ollama/blob/main/docs/api.md

---

# Extension: Deterministic and Probabilistic Computing (self-paced)

Nothing above depends on this section.  It is here because the dial you turned today has a consequence that outlives the session: every program you have written until now returned the same answer for the same input, and this one does not.  That break is worth sitting with, along with automation bias, which is the human half of the same problem.

#### Before You Start

**What you need:** Nothing installed; this one is discussion and paper first.  Python only if you run the optional demo.

**What you will have at the end:** a working rule for telling deterministic systems from probabilistic ones, and why that changes how you test them.

Work these in sequence.  Each section assumes the one before it, and the code blocks are meant to be executed, not skimmed.

---

### Overview and Roles

Most software you have used behaves predictably: the same input always produces the same output.  AI systems built on large language models deliberately do not.  Understanding *why* (and what that means for how you interpret and rely on AI outputs) is one of the most practically important ideas in this course.

This activity connects to the **sampling and generation** material from earlier in the term.  You will classify computing systems as deterministic or probabilistic, examine the cognitive trap called *automation bias*, and reason about the specific dangers that arise when people treat probabilistic AI outputs as reliable ground truth.

**Estimated time:** 45-60 minutes

**Team roles (rotate for each Part):**

- **Manager**: Keeps the group on task and on time.
- **Recorder**: Writes down the group's agreed answers.
- **Presenter**: Shares the group's findings with the class.
- **Reflector**: Notes what surprised the group and what questions remain.

---

## Two Kinds of Computation

In this part, you will classify computing systems as deterministic or probabilistic and build intuition for why the distinction matters before you encounter it in AI.

### Deterministic Systems

A **deterministic** program always produces exactly the same output given the same input and the same starting state.  There is no randomness; the result is fully predictable.

```python
def add(a, b):
    return a + b

# Always returns 5, no exceptions, no surprises.
print(add(2, 3))
```

Database queries, sorting algorithms, cryptographic hashes, and arithmetic are all deterministic.  This predictability is a feature: it makes these systems easy to test, debug, and trust because you can verify them exhaustively.

#### Three key properties of deterministic systems:

1.  **Reproducibility**: Run it again, get the same answer.
2.  **Verifiability**: You can prove correctness by checking every possible input (for finite input spaces).
3.  **Debuggability**: The bug that produced output X will always produce output X under the same conditions, making it findable.

---

### Probabilistic Systems

A **probabilistic** (or *stochastic*) program intentionally samples from a probability distribution, so the output varies across runs even with identical input.

```python
import random

def flip_coin():
    return random.choice(["heads", "tails"])

# Could return either, by design.
print(flip_coin())
```

Randomness is not a bug here; it is a feature.  Probabilistic systems are used when we want to explore a space of possibilities, when the real-world phenomenon being modeled is inherently uncertain, or when avoiding predictability is itself valuable (cryptography, game fairness).

Examples outside AI: Monte Carlo retirement simulations, weather forecast models, network routing under load, randomized algorithms in competitive programming.

---

### Questions

**Q1.**  Classify each of the following as **deterministic (D)** or **probabilistic (P)**.  For each, briefly explain why.

| System | D or P? | Why? |
|---|---|---|
| Python's `sorted([3, 1, 2])` | | |
| Rolling a die in a board-game simulator | | |
| A search engine returning results for "best pizza" | | |
| SHA-256 hash of a file | | |
| A 10-day weather forecast model | | |
| `SELECT * FROM students WHERE grade = 'A'` | | |
| An LLM generating the next token at temperature = 0.7 | | |

> *Hint:* Ask yourself: "If I run this again with exactly the same input, am I guaranteed the same output?"  Be careful with the search engine; the answer may surprise you.

**Q2.**  A classmate argues: "LLMs aren't really random; they just look at patterns in training data and output the most likely word."  What is accurate about this claim, and what is it missing?

> *Hint:* Recall what the temperature parameter does.  Even at temperature = 0, many production implementations produce slightly different results across runs because of floating-point rounding and GPU non-determinism.  The model samples from a distribution; it does not look up a deterministic answer.

**Q3.**  The table below shows two outputs from the same prompt ("What is the capital of France?") submitted to the same model twice.  Which output is more dangerous from a user-trust perspective, and why?

| Run | Output |
|---|---|
| Run 1 | "The capital of France is Paris." |
| Run 2 | "The capital of France is Lyon, though Paris serves as the main administrative hub." |

[(X)] Run 2; it is factually wrong, yet it is presented in the same confident, authoritative prose as the correct answer.  A user cannot tell the difference from the output alone.
[( )] Run 1; consistent outputs suggest the model has memorized rather than understood, which is worse than variance.
[( )] Both are equally dangerous because any AI output should be distrusted.
[( )] Neither; this question is too simple for an LLM to get wrong, so the scenario is unrealistic.

> In practice, the same kind of confident-sounding error occurs on far less checkable claims (legal citations, medical statistics, historical dates) where most readers cannot spot the mistake.

---

**Bridge to Part II:** Now that you can classify systems as deterministic or probabilistic, Part II examines a cognitive trap that makes probabilistic systems especially risky: the human tendency to treat computed outputs as authoritative regardless of whether the system is reliable.

---

## Automation Bias - Why Humans Trust Machines

In this part, you will examine the research on *automation bias* (the tendency to over-rely on automated systems) and classify the specific failure modes it produces.

### Automation Bias Defined

**Automation bias** (Parasuraman & Manzey, 2010) is the tendency for humans to over-rely on automated decision aids in two ways:

1.  **Omission errors**: The human skips manual checks they would have performed without the automated aid, because the machine's output feels sufficient.
2.  **Commission errors**: The human acts on an incorrect automated recommendation without questioning it, because they defer to the machine's apparent authority.

Automation bias arises even among trained experts, even when the automated system has a known error rate, and even when stakes are high.  In a landmark study, Skitka et al. (1999) found that experienced pilots failed to detect autopilot errors at significantly higher rates when an automation aid was present, *even after being explicitly warned that the aid was imperfect*.

> **Common Misconception:** Automation bias is a problem only for non-technical or "tech-naive" users.  Research consistently shows that trained professionals (pilots, radiologists, financial analysts, software engineers) exhibit automation bias at similar or higher rates than non-experts, precisely because their professional workflow incorporates these tools and they have learned to trust them.

---

### A Taxonomy of Trust Failure Modes

Not all trust miscalibration looks the same.  The following four modes each cause a different kind of harm:

| Mode | Description | Example |
|---|---|---|
| **Under-trust** | Human ignores a correct automated recommendation | Dismissing a correct fraud alert because "it feels fine" |
| **Over-trust / automation bias** | Human accepts an incorrect automated recommendation | Following GPS directions into a lake |
| **Complacency** | Human stops monitoring an automated system once it is running | Autopilot disengages silently; pilot doesn't notice for 90 seconds |
| **Skill fade** | Long-term loss of the ability to perform the task manually after years of automation | Unable to navigate without GPS after a decade of relying on it |

---

### Questions

**Q4.**  In 2023, the attorneys representing a client in *Mata v.  Avianca, Inc.* submitted a federal court brief that cited six legal precedent cases, all of which were entirely fictional cases generated by a chatbot.  Neither attorney independently verified any citation.  The judge sanctioned both attorneys.

Which failure mode from the taxonomy above best describes what happened?  What would "appropriately calibrated trust" have looked like?

> *Hint:* Attorneys have a professional and ethical obligation to verify every citation before submitting a brief.  The question is not whether they trusted the tool, but why the trust was not bounded by the verification step they knew was required.

**Q5.**  A hospital deploys an AI system that flags potential drug interactions for nursing review.  A nurse, disagreeing with a specific flag based on her clinical experience, overrides it without documenting her reasoning.

Is this automation bias, appropriate expert judgment, or something else?  What information would you need to determine which?

> *Hint:* Both under-trust and over-trust are errors.  The right answer depends on: the nurse's track record vs. the AI's precision and recall on this flag type, whether the patient is harmed by the override, and whether lack of documentation creates institutional risk regardless of outcome.

**Q6.**  Which of the following best explains why automation bias persists even when humans consciously know that a system is fallible?

[(X)] Checking automated outputs requires effortful cognition.  The brain conserves effort when it perceives a trusted external source, a process psychologists call "cognitive offloading."  This is adaptive in most contexts but becomes dangerous when the trusted source is unreliable.
[( )] Humans inherently distrust their own judgment and will always prefer any external signal over their own reasoning.
[( )] Automation bias has been largely debunked; modern users who understand AI do not exhibit it.
[( )] Trained users never exhibit automation bias; only untrained or non-expert users do.

---

**Bridge to Part III:** You have now seen that humans over-trust automated systems even when they know better.  Part III asks: what happens when the automated system is not just fallible but *cannot* signal its own uncertainty?  That combination (probabilistic outputs delivered with authoritative-looking confidence) is what makes LLMs distinctively risky.

---

## The Danger When Probabilistic Meets Authoritative

In this part, you will synthesize Parts I and II to reason about the failure mode that is specific to large language models: high-confidence-sounding outputs from an inherently probabilistic system, consumed by users who are primed to over-trust.

### The Confidence-Calibration Gap

Most probabilistic systems explicitly communicate their uncertainty.  A weather app shows "70% chance of rain."  A spam filter says "94% confidence."  A Bayesian classifier outputs a posterior distribution.

LLMs typically do not.  They generate fluent, confident-sounding prose regardless of whether the underlying probability distribution is sharply peaked (the model is, in some sense, "sure") or flat (it is guessing).

Read the following two outputs.  Both come from the same model in the same fluent style:

```yaml
User: What is the boiling point of water at sea level?
AI:   The boiling point of water at sea level is 100°C (212°F).

User: Who won the 1987 Ursinus College intramural chess tournament?
AI:   The 1987 Ursinus College intramural chess tournament was won by
      Michael Chen, a junior majoring in mathematics.
```

The first answer is verifiable and correct.  The second is almost certainly fabricated, but the model delivers both in identical, authoritative prose with no hedging, no uncertainty signal, and no difference in tone.

> **Common Misconception:** If an AI "sounds confident," it probably is correct.  In fact, the fluency and grammatical correctness of an LLM's output are driven by the language modeling objective (predict the next plausible token), not by the accuracy of the underlying claim.  A model can generate a perfectly grammatical, confidently phrased, completely false sentence.

---

### Three Compounding Risk Factors

When probabilistic AI outputs are treated as authoritative, three factors compound to make the problem worse than it would be with any other unreliable information source:

| Risk Factor | Why It Matters |
|---|---|
| **Surface credibility** | Well-formed prose, plausible structure, and specific-sounding details make false claims hard to distinguish from true ones without independent verification. Fabricated citations look like real citations. |
| **Volume** | AI can generate hundreds of plausible-sounding claims per minute. The cognitive load to verify each one is multiplicatively larger than the cost to generate them. |
| **Domain opacity** | Many high-stakes AI use cases (medical, legal, scientific, financial) are precisely the domains where most users lack the expertise to evaluate the output independently. The highest-stakes domains have the lowest baseline for catching errors. |

---

### Questions

**Q7.**  Design a concise "sanity check" protocol (at most four steps) that a student should apply before using any piece of AI-generated information in a graded assignment.  Be specific; avoid vague steps like "check if it's right."

> *Hint:* Think about: (1) Is this the kind of claim that *can* be verified with a primary source?  (2) What would happen if it were wrong?  (3) How would I explain to an instructor that I verified this?

**Q8.**  A classmate argues: "This problem will go away once AI systems always display explicit confidence scores on every output."  Do you agree?  What risk factors from Model 6 would still remain even if confidence scores were perfect?

> *Hint:* Think about calibration: does "80% confidence" mean the model is right 80% of the time on this type of claim?  Who would check?  And consider: does a confidence score on each sentence solve the volume problem, or does reading 200 scores per document just add another layer of cognitive load?

**Q9.**  Match each real-world scenario to the primary risk factor from Model 6 (Surface Credibility, Volume, or Domain Opacity) that makes it most dangerous:

| Scenario | Primary Risk Factor |
|---|---|
| A student submits a 15-source bibliography; three citations are AI-generated and fictional, but formatted correctly and plausibly titled | |
| A content moderation system flags 40,000 posts per hour; human reviewers approve AI decisions without reading flagged content because the queue never clears | |
| An AI-generated radiology summary misidentifies a lesion; the reviewing radiologist, who is not an AI expert, assumes the AI output reflects ground truth | |

**Q10.**  Which design change most directly reduces automation bias without requiring users to become AI experts?

[(X)] Displaying explicit uncertainty language ("I am not confident about this; please verify"), requiring confirmation before high-stakes outputs are acted upon, and showing alternative responses alongside the primary one, so the user perceives the system as offering options, not delivering verdicts.
[( )] Making the AI system fully deterministic, so it always gives the same answer and users know what to expect.
[( )] Increasing the AI's accuracy to 99%; at that threshold, automation bias becomes statistically acceptable.
[( )] Removing AI from high-stakes domains entirely until the technology is perfect.

---

## Synthesis: Discussion

Before your Presenter shares with the class, agree on answers to the following as a group:

1.  In one sentence, complete this argument: "It is specifically dangerous to treat probabilistic AI outputs as authoritative because ___."

2.  Name one domain *outside of AI* where deterministic outputs are treated as more authoritative than they deserve to be.

3.  State one concrete habit you will adopt after today to protect yourself from automation bias when using AI tools in this course or professionally.

4.  *Challenge question:* Could an AI system be designed that is both probabilistic *and* well-calibrated in its expressed confidence?  What would that require, and why don't current LLMs do it?

---

## Key Concepts

| Term | Definition |
|---|---|
| Deterministic | A system that always produces the same output for the same input |
| Probabilistic / stochastic | A system that samples from a probability distribution, so outputs vary across runs |
| Automation bias | The tendency to over-rely on automated systems, accepting their outputs without independent verification |
| Calibration | A system is calibrated if its stated confidence matches its actual accuracy rate; e.g., a calibrated model that says "80% confidence" is correct 80% of the time |
| Cognitive offloading | Delegating mental work to an external tool or system, reducing cognitive effort at the cost of reduced engagement with the result |

---
