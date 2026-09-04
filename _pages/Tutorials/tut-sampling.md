---
layout: default-standard
permalink: /Tutorials/SamplingAndTemperature
title: 'CS357: Foundations of Artificial Intelligence - Why Different Answers Every Time? Sampling, Temperature, and Generation'
info:
  coursenum: CS357
  purpose: "To explain why the same prompt gives different answers: a language model computes a probability distribution over the next token, the system samples from it, and temperature reshapes that distribution before the draw."
tags:
- sampling
- temperature
- reasoning-models
---

{% include mathjax.html %}

# CS357: Foundations of Artificial Intelligence - Why Different Answers Every Time? Sampling, Temperature, and Generation

## Purpose

To explain why the same prompt gives different answers: a language model computes a probability distribution over the next token, the system samples from it, and temperature reshapes that distribution before the draw.

## About This Tutorial

You have already turned this dial twice.  In *Running Your Own AI* you set temperature to 0, then to 1, and watched six answers to the same prompt.  In the *Agent Loop* activity you pinned it to 0 so the loop's parser would find the same strings every run.  You know what the dial does.  This tutorial explains what it is.

The short answer, and the resolution of the mystery your team formed hypotheses about in *Welcome: What Is AI, and What Is an Agent?*: a language model computes a **probability distribution over the next word-piece (token)**, and the system samples from it, rolling a weighted die at each step.  Temperature is the number that reshapes the die before the roll.

The tutorial moves from next-token prediction → softmax and temperature → top-k and top-p → experiments on your own stack → reasoning models, and it connects every knob to agent design.  The last step changes the shape of the story.  Every dial before it decides *what* gets sampled.  Reasoning models are the first thing you meet that changes *how much computation happens at all*.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|------|--------------------------|--------------------------|
| **Token** | A unit of text (roughly a word, a word-part, or a punctuation mark) that the model reads and writes one at a time | The sentence "The cat sat." is four tokens: "The", " cat", " sat", "." |
| **Softmax** | A function that turns the model's raw scores (logits) into probabilities that add up to 1.0, so the scores can be compared and read as chances | Turning logits of (5, 2, -1) for (Paris, Lyon, banana) into probabilities near (0.95, 0.05, 0.001) |
| **Temperature** | The dial you turned in *Running Your Own AI*, stated precisely: a number that sets how peaked or flat the probability distribution is.  Low temperature makes the most likely token nearly certain; high temperature lets unlikely tokens compete | The same `temperature` you passed in `options` and dragged in OpenWebUI's Advanced Params, worked by hand in the companion *AI by Hand* tutorial |
| **Top-k sampling** | Keeps only the k highest-probability tokens before sampling and discards the long tail of unlikely options | With k=5, only the five most probable next words are considered, even if the vocabulary holds 50,000 |
| **Top-p (nucleus) sampling** | Keeps the smallest group of tokens whose combined probability reaches a threshold p, so the group size adapts to how confident the model is at each step | With p=0.9, if Paris alone has probability 0.92, only Paris is kept; if the top 10 words share 0.9 probability, all 10 are kept |
| **Greedy decoding** | Always picking the single most probable next token, equivalent to temperature = 0.  Deterministic, but sometimes repetitive, and the locally best pick is not always the globally best one | An agent with temperature=0.0 that always picks the same action regardless of context |
| **Test-time compute** | Computation spent while answering rather than while training.  A fixed-depth model can spend more of it only by emitting more tokens, so the length of what a model writes is the amount of thinking it does | A model that writes two hundred words of steps before its answer has run two hundred more forward passes than one that answers immediately |
| **Reasoning (thinking) model** | A model additionally trained with reinforcement learning against automatically checkable outcomes, so it writes a long intermediate reasoning stream before its answer and learns to backtrack and self-check | `deepseek-r1` emitting its work between `<think>` tags in Part III, catching its own misreading of a discount problem |

---

## Part I: Generation as Repeated Prediction

In this part you work out how a language model converts raw scores into a probability distribution and then samples from it.  That resolves the mystery from *Welcome: What Is AI, and What Is an Agent?* of why identical prompts produce different outputs.  The math here (softmax and temperature) returns every time you tune an agent's behavior for the rest of the semester.

### 1.  One Token at a Time

Autocomplete on your phone suggests the next word from what you have typed so far.  A language model does the same thing, with two differences.  It assigns a probability to every word in its entire vocabulary (often 50,000 or more) instead of offering three suggestions, and it repeats the pick for every single word in its response.  One early wrong pick can send the whole response in a surprising direction.  That is why the same prompt can produce different responses on different runs.

A language model is a next-token predictor.  Given the tokens so far, it outputs a raw score for every token $$i$$ in its vocabulary.  That score is called a *logit* (pronounced "low-jit", short for log-odds unit), a plain number with no fixed range, written $$z_i$$.  The **softmax** function then converts the scores to probabilities.  Softmax squashes any set of numbers into values that sum to 1.0:

$$
P(i) = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}
$$

The system samples one token from this distribution, appends it to the text, and repeats until a stop token appears.  Generation is a loop of single predictions, one word-piece at a time, so one early sampling choice can steer the entire continuation.  This is the test of your hypotheses from the *Welcome* activity: the randomness lives in the sampling step, not in the model weights, which stay fixed.

Temperature $$T$$ reshapes the distribution.  As $$T \to 0$$, the highest-scoring token dominates and sampling approaches deterministic *greedy decoding* (always picking the top word).  As $$T$$ grows, the distribution flattens and less likely tokens gain probability.  Temperature does not add knowledge; it redistributes confidence across the existing options.

The by-hand work for this formula lives in the companion tutorial, [AI by Hand]({{ site.baseurl }}/Tutorials/AIByHand).  There you compute the probability of Paris, Lyon, and banana at three temperatures with a calculator, argue for the temperature an agent's reasoning step should use, and then sweep temperature across a five-token distribution in the browser while watching the entropy climb.  Work through it before Part IIb if you want the numbers behind the shapes you are about to measure.  The rest of this tutorial does not depend on it.

Two things to remember from this section.  Generation is a loop of single-token predictions, and the randomness comes from sampling, not from the weights.  Temperature reshapes the distribution before each draw without adding any knowledge to it.

---

### 2.  Truncation: Top-k and Top-p

Temperature reshapes the whole distribution; **truncation** removes options from consideration entirely.  Top-k sampling keeps only the $$k$$ highest-probability tokens and renormalizes the remaining probabilities to sum to 1.0.  Top-p (nucleus) sampling keeps the smallest group of tokens whose combined probability reaches the threshold $$p$$:

$$
V_p = \text{smallest } V' \text{ such that } \sum_{i \in V'} P(i) \ge p
$$

Top-p has one advantage over top-k: it adapts to the model's confidence.  When the model is very sure (one word has probability 0.95), the nucleus is that one word.  When many continuations are plausible (ten words each with probability 0.09), the nucleus widens to include all of them.  In practice, creative writing tasks often use higher temperature (0.7-1.0) with top-p near 0.9, while agentic control steps that must output exact tool calls use temperature near 0.0.

A distribution assigns probabilities: Paris 0.90, Lyon 0.06, Marseille 0.03, banana 0.01.  With top-p $$= 0.95$$, which tokens are in the candidate set?

- Paris only (0.90 already exceeds 0.95 minus a rounding edge)
- Paris and Lyon (0.90 + 0.06 = 0.96, which first reaches or exceeds 0.95)
- Paris, Lyon, and Marseille
- All four tokens

<details markdown="1"><summary>Answer</summary>

Paris and Lyon (0.90 + 0.06 = 0.96, which first reaches or exceeds 0.95)

</details>

### 3.  Other Common Generation Parameters

Temperature, top-k, and top-p decide *which* token to pick.  A few other parameters shape *how much* the model generates and *what it avoids*.  You pass all of them the same way, inside the Ollama `options` dictionary, and they map to top-level fields on OpenAI-compatible endpoints.

| Parameter (Ollama) | OpenAI-API name | What it does | Reach for it when |
|--------------------|-----------------|--------------|-------------------|
| `num_predict` | `max_tokens` | Caps how many tokens the model may generate before it must stop. | You want to bound length, latency, or cost, or cut off a run-on answer. |
| `repeat_penalty` | `frequency_penalty` / `presence_penalty` | Down-weights tokens the model has already produced, discouraging loops and repetition. | The model gets stuck repeating a word or phrase, especially at low temperature. |
| `stop` | `stop` | A list of strings that, when generated, immediately end the response. | You want the model to halt at a delimiter: e.g. `"\n\n"`, `"</answer>"`, or a role tag. |
| `seed` | `seed` | Fixes the random draw so a given prompt + settings reproduces the same output (see Exercise 1). | You need reproducible experiments or tests. |

Two notes on the penalties.  Ollama exposes a single `repeat_penalty` (a multiplier, typically 1.0-1.3).  The OpenAI API splits the idea into `frequency_penalty` (scales with how *often* a token has appeared) and `presence_penalty` (a flat penalty once a token appears *at all*).  Both attack the same failure, degenerate repetition, from slightly different angles.

The cell below exercises three of these knobs: a short `num_predict` cap, a `repeat_penalty` to break loops, and a `stop` sequence.

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

{% raw %}
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
{% endraw %}

> **Note:** On an OpenAI-compatible endpoint (including OpenWebUI's `/api/chat/completions`), these move out of the `options` dict to the top level of the request body, and `num_predict` becomes `max_tokens`.

> **Common Misconception:** The `top_k` in this tutorial is a **sampling** parameter; it limits which *next tokens* the model may choose from.  It is a different knob from the `top_k` (often written `k` or `n_results`) you will meet in Retrieval-Augmented Generation (RAG), where it means "how many *document chunks* to retrieve."  Same name, different layer of the system: one truncates a probability distribution over the vocabulary; the other sets the size of a search result set.  See the *Retrieval-Augmented Generation with Chroma* activity, where retrieval `k` is tuned.

Two things to remember from this part.  Truncation (top-k and top-p) removes candidates before the draw, and top-p adapts its cut to the model's confidence while top-k does not.  The remaining parameters (`num_predict`, `repeat_penalty`, `stop`, `seed`) control length, repetition, stopping, and reproducibility rather than which token wins.

---

## Part II: Experiments on Your Stack

In this part you run a controlled experiment that makes the theory from Part I visible.  You sample the same prompt eight times at three different temperatures and count how often the answers diverge.  That turns an intuitive observation into a measurable, reproducible result.

### 4.  Measuring Variability

To quantify "how different are the answers," sample the same prompt several times and count how many distinct outputs appear.  This converts the impression "it seems to vary a lot at high temperature" into a number.

The code below asks the model to name a single animal eight times at each of three temperature settings.  It uses a `Counter` (a Python dictionary that counts occurrences) to tally how many distinct answers appear.  A temperature of 0.0 should produce the same answer every time; higher temperatures should spread answers across more options.

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

{% raw %}
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
{% endraw %}

---

### Model 2: Reading the Results

Examine the counter output for each temperature.  Notice which temperatures produce the same answer eight times, which produce two or three variations, and which produce eight different answers.

### Questions to Work Through

1.  At $$T=0.0$$, did all eight runs produce the same answer?  If any runs differed, propose where residual non-determinism could enter a real serving system.  Consider hardware-level floating-point rounding, batching multiple requests together, and whether your Ollama server truly respects `seed=-1`.

   > *Hint: Even "deterministic" floating-point arithmetic can give slightly different results on different CPU/GPU hardware because of the order of operations in parallel computation.  A production model server may batch several requests together, which changes the arithmetic order.*

2.  Sketch (or describe) the shape of a graph with temperature on the x-axis and "number of distinct answers out of 8 runs" on the y-axis.  Where is the knee of the curve for your model, the temperature at which answers begin to diverge noticeably?

   > *Hint: Plot three points: T=0, T=0.7, T=1.5.  Is the transition gradual or sudden?  Does the knee appear closer to 0 or closer to 1?*

3.  Repeat the experiment with the prompt "Write the first line of a poem about autumn."  Should an agent that *drafts creative text* and an agent that *routes requests to tools* share the same temperature setting?  Assign each a specific temperature value and write one sentence defending each choice.

   > *Hint: For the routing agent, think about what happens if "route to weather tool" becomes "route to music tool" because of random sampling.  For the creative agent, think about what "always the same first line" means for a poem generator.*

Two things to remember from this part.  Counting distinct outputs across repeated runs is the simplest honest measurement of variability.  The knee of that curve is model-specific, so measure it on your own stack rather than assuming a number.

---

## Part IIb: Tuning the Dials on Purpose

You have seen what temperature does to one distribution.  Now turn the dial systematically, record what happens, and build a parameter policy you can defend: which settings for which task, and why.  This is the part you will reuse, because every lab from here on asks you to pick these numbers.  The five-token temperature and entropy sweep that opens this work in class is in the *AI by Hand* companion linked in Part I.

### Real Model Experiments: A Systematic Sweep

The experiment is four task types × four temperature settings × three repetitions, which gives you 48 data points to analyze.  If you work in a team, take one task row each for the first sweep, then rotate and check each other's rows.  Fill in the observation table as you go and post it to the discussion board.

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

{% raw %}
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
{% endraw %}

#### Observation Table

| Task | T=0.0 (run 1, 2, 3) | T=0.5 (run 1, 2, 3) | T=1.0 (run 1, 2, 3) | T=1.5 (run 1, 2, 3) | Consistent? |
|------|---------------------|---------------------|---------------------|---------------------|-------------|
| factual | | | | | |
| creative | | | | | |
| code | | | | | |
| list | | | | | |

"Consistent?" column: yes (all 3 identical) / partial (2/3 same) / no (all different).

### Questions to Work Through

4.  At T=0.0, you ran the factual question three times and (likely) got the same answer all three times.  Is this because the model "knows" the right answer, or because it always picks the highest-probability token?  How would you design an experiment to tell the difference?

   > *Hint: Ask the model a factual question where the correct answer is less well known, for example "What is the capital of Burkina Faso?"  Does it still give a consistent answer at T=0?  Is that answer correct?  A model that always gives the same wrong answer at T=0 is being consistent, not knowledgeable.*

5.  For the code generation task, what happened at T=1.5?  Did the generated Python still run without a syntax error?  Why might high temperature be more harmful for code generation than for creative writing?

   > *Hint: In creative writing, any plausible continuation is acceptable; there is no "correct" first line for a science fiction novel.  In Python code, a single misplaced character (a wrong parenthesis, a misspelled keyword, an incorrect indentation level) causes a syntax error and the code fails entirely.  High temperature makes rare characters more likely at every step, which is fine for prose but catastrophic for code that must match a grammar exactly.*

6.  A developer wants their customer service chatbot to give exactly the same answer to the same question every time.  They should set temperature=0 and top_k=1.

   - True; T=0 and top_k=1 both force greedy decoding, giving deterministic outputs on most hardware
   - False; there is no way to make a large language model (LLM) deterministic
   - True, but only top_k=1 is needed; temperature has no additional effect
   - False; even at T=0, the model might generate different outputs due to random seeding

   <details markdown="1"><summary>Answer</summary>

   True; T=0 and top_k=1 both force greedy decoding, giving deterministic outputs on most hardware

   </details>

   > **Common Misconception:** "Lower temperature = better answers."  This is not true as a general rule.  For creative tasks, low temperature produces repetitive, generic outputs; the model keeps generating the most statistically common continuation, which tends to be bland.  For factual tasks, low temperature reduces hallucination risk but can also stop the model from adapting its phrasing to the user's question.  Temperature is a tool you choose to match the task; there is no universally correct setting.  The question is always: *how much variation is acceptable, and how much randomness does the task benefit from?*

7.  The list task (naming three programming languages) showed variation at T=1.5.  The same three languages will appear at T=0.0 almost every time.  What does the variation at high temperature tell you about what the model "believes" about popular programming languages?

   > *Hint: At T=0, the model always picks the single highest-probability token at each step, so the highest-probability language name starts the list.  At T=1.5, languages with lower (but non-negligible) probability start appearing.  The variation shows you the shape of the model's distribution over programming language names, not only the single most common one.*

### Task-Parameter Matching: Building a Parameter Policy

Now that you have data, use it to build a principled parameter guide.  The table below lists five deployment scenarios.  Two are filled in as examples; you fill in the remaining three.

| Task | Recommended Temperature | Recommended top_p | Recommended top_k | Reasoning |
|------|------------------------|-------------------|-------------------|-----------|
| Legal document summarization | 0.1-0.2 | 0.85 | 20 | Faithfulness to source is paramount; variation is a liability. Low T keeps output close to the most-probable (most-supported) summary; tight top_p and top_k prevent hallucinated details. |
| Marketing tagline generation (10 options) | 1.0-1.3 | 0.95 | 50 | We *want* diverse, creative outputs; the whole point is to explore many options. High T and wide nucleus give the model room to be surprising. We will pick the best option ourselves. |
| Extracting JSON fields from a form | | | | |
| Writing a first-draft blog post intro | | | | |
| Answering student quiz questions with explanation | | | | |

### Questions to Work Through

8.  For the JSON extraction task, argue for or against using top_p=0.50 (very narrow nucleus).  What risk does a very narrow nucleus introduce that a slightly wider one (top_p=0.85) avoids?

   > *Hint: With top_p=0.50, if the model is uncertain between two valid JSON field names (e.g., "first_name" vs. "firstName"), one of them might be excluded from the nucleus.  The model is forced to pick from the remaining tokens, which might be syntactically invalid.  A slightly wider nucleus keeps both plausible options available.  The risk of going too narrow is that you exclude correct options when the model is uncertain about the right answer.*

9.  A team member proposes using temperature=0 for *all* tasks in a production agent to ensure reproducibility.  What two specific failure modes does this introduce that a moderate temperature (T=0.3-0.5) would mitigate?

   > *Hint: (1) Repetition loops: at T=0 without a repetition penalty, the model can get stuck generating the same token forever because the highest-probability token never changes.  (2) Failure to rephrase: if the exact highest-probability phrasing is ambiguous or does not match the user's context, the model cannot adapt; it always produces the same phrasing.  A small temperature lets the model occasionally deviate from the single most likely token and avoid both traps.*

10.  You are running a Q&A system over a medical reference database.  The system retrieves relevant passages (RAG) and asks the model to answer based only on those passages.  For the generation step, you should:

    - Use high temperature (T=1.5) to ensure creative, comprehensive answers
    - Use low temperature (T=0.1-0.3) and low top_p to keep the answer close to the retrieved evidence
    - Use top_k=1 to guarantee the model only repeats the retrieved text verbatim
    - Temperature does not matter when using RAG, since the retrieved context constrains the answer

    <details markdown="1"><summary>Answer</summary>

    Use low temperature (T=0.1-0.3) and low top_p to keep the answer close to the retrieved evidence

    </details>

### Build Your Own Parameter Guide: Three Personas, Three Policies

Your deliverable for this part is a one-page parameter guide for three deployment personas.  Each persona specifies temperature, top_p, top_k, and one "edge case" where you would push toward the boundary of the recommended range.

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

If you work in a team, share the guide with the class and note where the three guides conflict.  The conflicts show you the parameter trade-offs.

The cell below checks your policies by running the same prompt across the recommended ranges.

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

{% raw %}
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
{% endraw %}

### Questions to Work Through

11.  Run the coding helper at T=0.5 (low end) and at T=0.5 with top_k=5 (very restricted).  Do you notice a difference in output quality?  What does restricting top_k further do to code that restricting temperature alone does not?

    > *Hint: Temperature reshapes the whole probability distribution; top_k discards the long tail entirely.  In code generation, the long tail includes both rare variable names (which might be acceptable) and invalid syntax tokens (which are never acceptable).  Restricting top_k aggressively stops the model from ever selecting an obviously wrong token, even one that temperature would have given a small but nonzero chance.*

12.  A student on your team argues: "We should just use T=0 for all three personas and add a post-processing step to paraphrase or diversify the output."  What are the advantages of this approach?  What does it lose compared to sampling with appropriate temperature?

    > *Hint: Advantages: reproducibility, debuggability, and the safety of greedy outputs for factual tasks.  What it loses: the diversity comes from a second model pass, which introduces its own parameters, cost, and failure modes.  The original model's rich probability distribution (which encodes "second-best" and "third-best" options that are linguistically plausible) is thrown away at T=0 before the paraphraser ever sees it.*

Two things to remember from this part.  There is no universally correct temperature; the right setting depends on how much variation the task can tolerate and how much it benefits from.  Write the policy down with a reason for each number, because you will be asked to defend those numbers in every lab that follows.

---

## Part III: When the Model Thinks Before It Answers

Everything so far has treated generation as one loop: predict a distribution, sample a token, append it, repeat.  Every dial you tuned reshapes that distribution.  None of them changes how much computation the model spends on a hard question versus an easy one.  This part is about the models that changed exactly that, and about why it is a deeper change than any dial.

### 6.  The Fixed-Compute Problem

Ask a standard model "what is 2+2" and ask it to prove a claim about prime numbers.  Count the work it does before its first output token.

It is the same.  A transformer runs its input through a fixed stack of layers, the same number every time, and produces one distribution.  Attention is what lets it mix information across the sequence inside that stack, and *Tokens, Embeddings, and Attention* showed you that mixing arithmetic by hand.  What attention does not give it is more steps when the problem is harder.  The depth was frozen when the model was trained.

So a fixed-depth model has exactly one way to spend more computation on a hard problem: write more tokens.  Each token it emits is appended to the context and read back on the next pass, so the tokens it has already written become a place to store partial results.  The context window stops being only an input and starts being a scratchpad the model can write to and read from.

That is the whole idea, stated in one line because it is the line that separates the two kinds of model:

> **Attention decides what a fixed amount of computation looks at.  Generated tokens decide how much computation happens at all.**

This is why "show your work" prompting was always more than a stylistic preference.  When you ask a standard model to reason step by step, you are not asking it to be more careful; you are giving it permission to use more forward passes on your problem.  The steps are the computation.

### Questions to Work Through

13.  A classmate says: "Chain-of-thought prompting works because the model explains itself, and explaining forces clarity, the same way it does for people."  Using the paragraph above, give a different explanation of why it works that does not depend on the model understanding its own explanation.

    > *Hint: Every emitted token is another full pass through the network, with all previously emitted tokens available in context.  Ten tokens of "steps" is ten more passes and a written record of intermediate results the model can attend to.  The mechanism is extra serial computation plus external storage, not introspection.  A useful test of the two theories: nonsense filler tokens sometimes help a little on some tasks, which the clarity theory does not predict at all.*

14.  Attention lets any token look at any other token in one pass.  If a model can already look anywhere, why can it not simply "look at" the answer to a hard multi-step problem in that same pass?

    > *Hint: Looking is not the same as computing.  Attention retrieves and mixes what is present; it does not run a sequence of dependent operations.  A problem that requires step B to use the result of step A needs those steps to happen in order, and a fixed stack of layers gives you a fixed number of dependent steps per token.  Writing A down as tokens is what makes B's pass able to use A's result.*

---

### 7.  What a Reasoning Model Actually Changes

A **reasoning model** (sometimes called a thinking model) takes the scratchpad idea and builds it into the model rather than leaving it to your prompt.  Four things change.  Be precise about which is which, because only two of them are new mechanisms and the other two are consequences.

It emits a separate reasoning segment before its answer.  The model produces a long internal stream, then an answer.  Some providers hide the stream and show a summary; local models generally show it.  Structurally this is still next-token prediction; the stream is marked off as not-the-answer.

It was trained on outcomes, not on imitation.  This is the substantive change.  A standard model is trained mostly to predict human-written text, so its "reasoning" looks like reasoning humans wrote down.  A reasoning model is additionally trained with reinforcement learning (RL) against problems that can be automatically checked: a math answer that is right or wrong, code that passes or fails its tests.  The training signal rewards reasoning that reaches the right answer, not reasoning that reads well.

Behaviors appear that imitation does not produce.  Because the reward is the outcome, the model learns moves that a text-imitator has little reason to learn: noticing a contradiction partway through, backtracking, discarding an approach and starting a different one, re-checking an answer against the original question.  Human-written solutions usually show the clean path, not the abandoned ones, so these behaviors are hard to learn by imitation and natural to learn from outcomes.

A new dial appears, and it is a different kind of dial.  Reasoning models expose something like a *thinking budget* or *reasoning effort*.  Notice what kind of quantity that is.  Temperature, top-k, and top-p all reshape a distribution; they change what gets sampled.  A thinking budget changes how much computation runs before an answer exists.  You have spent this whole tutorial on shape dials.  This is the first amount dial you have met.

> **Watch out!**  The parameter guide you built in Part IIb does not transfer to these models unchanged.  Providers commonly advise leaving temperature at its default for reasoning models rather than driving it to 0, because the RL training already tuned the reasoning stream, and pinning it to greedy decoding tends to produce loops and worse answers rather than more reliable ones.  Check the model card before you apply your low-temperature-for-facts rule here.

### Model 5: Two Transcripts, Same Question

Here are two responses to the same question: a shirt costs 40 dollars after a 20% discount; what was the original price?  Read both before answering anything.

**Model A (standard, temperature 0.2):**

```text
The original price was $48.
```

**Model B (reasoning model, thinking shown):**

```text
<think>
Let me set up. Let x be the original price.
20% off means the customer pays 80% of x.
So 0.8x = 40, and x = 40 / 0.8 = 50.
Let me check: 20% of 50 is 10, and 50 - 10 = 40. That matches.
Wait, I should double-check I did not read this as "20% of 40".
20% of 40 is 8, giving 48. But the discount applies to the ORIGINAL price,
not the sale price, so 48 is the wrong reading. x = 50 is correct.
</think>
The original price was $50.
```

### Questions to Work Through

15.  Model A is wrong, and it is wrong in a specific way that Model B explicitly considers and rejects.  Name the error, and explain what in Model B's transcript caught it.

    > *Hint: Model A applied the 20% to the sale price (40 + 20% of 40 = 48) instead of solving for the price the discount was taken from.  Model B catches it by checking its answer against the problem statement and then, separately, by naming the wrong reading and testing it.  That second move, considering an alternative interpretation and ruling it out, is a backtracking behavior, and it is the kind of thing outcome-based training rewards and imitation training rarely teaches.*

16.  A team member concludes: "So reasoning models are just standard models with 'think step by step' glued to the front of every prompt."  Give one thing in Model B's transcript that prompting alone would not reliably produce, and say why the training difference matters.

    > *Hint: The self-correction ("Wait, I should double-check...") is the honest answer.  You can ask a standard model to check its work and it often will, in form, and still confirm its original mistake, because it is imitating what checking looks like rather than being rewarded for catching errors.  Outcome-based RL rewards the run that ends correct, which makes an actual catch worth something.  Prompting can request the behavior; training is what makes it reliable.*

17.  Which statement best describes why a reasoning model can be more capable than an attention-based model that does not produce a reasoning stream?

    - Its attention mechanism compares more token pairs, so it sees more of the context at once
    - Its emitted tokens act as external memory across many forward passes, so the number of dependent computation steps is no longer capped by the model's fixed depth
    - It has more parameters, and capability scales with parameter count
    - It samples at a lower temperature, so it makes fewer random mistakes

    <details markdown="1"><summary>Answer</summary>

    Its emitted tokens act as external memory across many forward passes, so the number of dependent computation steps is no longer capped by the model's fixed depth

    </details>

    > *Hint: The first option describes attention, which is real but is not the change: attention already compares every pair.  The third confuses this with model size; a reasoning model can be small.  The fourth is a shape dial, not an amount dial.  The second is the mechanism: a fixed-depth network gets a bounded number of dependent steps per token, and writing intermediate results into the context lifts that bound.*

---

### 8.  The Honest Limits

Take the claim seriously enough to bound it, because "the model thinks now" invites more belief than the mechanism supports.

It is still next-token prediction.  Nothing in the previous sections stopped being true.  There is a distribution, a sample, and an append, and the model can still be confidently wrong.  It has more chances to catch itself, not a different relationship with truth.

The visible thinking is not a guaranteed transcript of the computation.  The reasoning stream is generated text, produced by the same mechanism as the answer.  Research on chain-of-thought faithfulness finds cases where a model's stated reasoning does not match what drove its answer: it can be swayed by a hint and then write a chain that never mentions the hint.  Read a reasoning trace as evidence about the model's process, useful and often revealing, and not as a log of it.

Thinking cannot supply information the model does not have.  A budget of ten thousand reasoning tokens will not tell it your registrar's add/drop deadline.  Problems gated on *evidence* need retrieval; problems gated on *steps* are the ones extra computation helps.  Sorting your problems into those two piles is one of the more useful habits this course can leave you with, and the retrieval module is the other half of it.

It costs latency and tokens, and the cost is not small.  A reasoning stream can be many times longer than the answer, and you pay for all of it in time on your own hardware.  For classification, extraction, formatting, and routing, that spend buys nothing.

Small local models get less out of it than the headlines suggest.  The distilled reasoning models you can run on a laptop do show the behaviors, and they show them less reliably than their large counterparts.  Measure on your own tasks rather than assuming the benchmark result transfers to your machine.

> **Common Misconception: "More thinking is always better."**  Extra inference time helps when an iteration introduces something new: a checked intermediate result, a rejected alternative, a caught contradiction.  It does nothing when the model restates itself at greater length, and on easy problems it can talk itself out of a correct first answer.  The question is never "did it think longer" but "did the thinking introduce evidence the earlier pass did not have."  You will meet that same question again in *The Critique and Refine Pattern*, where the deliberation happens outside the model and you get to inspect every step of it.

### Try It Yourself

If you have a reasoning-capable model pulled locally, this takes about ten minutes and answers the question for your hardware rather than in general.

> **Runs on your machine, not here.**  This talks to Ollama at `localhost:11434`.  Run `ollama list` first; if you have no reasoning model, `ollama pull deepseek-r1:7b` gets one that emits its thinking between `<think>` tags.  Compare against any standard model you already have.

{% raw %}
```python
import re
import time

import requests


def ask(model, prompt, timeout=300):
    """Return (thinking, answer, elapsed_seconds) for one non-streaming call."""
    started = time.time()
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        r.raise_for_status()
        text = r.json().get("response", "")
    except Exception as e:
        print(f"[ask:{model}] {e}")
        return "", "", time.time() - started
    # Reasoning models emit their scratchpad between <think> tags; standard
    # models have none, so thinking comes back empty and the split still works.
    think = "\n".join(re.findall(r"<think>(.*?)</think>", text, flags=re.S)).strip()
    answer = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    return think, answer, time.time() - started


PROBLEMS = [
    ("discount",  "A shirt costs $40 after a 20% discount. What was the original price?"),
    ("easy",      "What is the capital of France? Answer with the city name only."),
    ("ordering",  "Sort these by size, smallest first: a grain of sand, a car, a bacterium, a house."),
]

MODELS = ["llama3.2", "deepseek-r1:7b"]   # edit to match your `ollama list`

for name, prompt in PROBLEMS:
    print(f"\n=== {name} ===")
    for model in MODELS:
        think, answer, elapsed = ask(model, prompt)
        print(f"  {model:<16} {elapsed:6.1f}s  "
              f"thinking={len(think.split()):>4} words  answer={answer[:60]!r}")
```
{% endraw %}

Record three things for each problem: which model got it right, how long each took, and how many words of thinking were spent.  Then answer the question that matters: on which problems did the thinking earn its cost?  The "easy" row is in there deliberately.  If a reasoning model spends two hundred words to say "Paris," you have measured the trade-off yourself rather than taking anyone's word for it.

Two things to remember from this part.  A fixed-depth model buys more computation only by writing more tokens, and a reasoning model is trained on outcomes so that its extra tokens reliably include checks and backtracking.  The thinking budget is an amount dial, not a shape dial, and it costs time that easy problems do not repay.

---

## Part IV: Synthesis and Practice

In this part you apply the sampling vocabulary to real design decisions (choosing temperature and top-p settings for different agent roles) and close the loop on the hypotheses your team formed in the *Welcome: What Is AI, and What Is an Agent?* activity.

> Work through the worked example at home.  It shows the renormalization step that most explanations of top-k and top-p leave out.

### Worked Example: top-k and top-p, including the step everyone skips

The multiple-choice question in Part I handed you a finished distribution and asked only which tokens fall inside the nucleus.  That is the easy half.  The half that matters, and the one that silently changes what your agent emits, is **renormalization**: after you throw tokens away, the survivors no longer sum to 1, so you have to divide by what is left.

Start from the logits of the *AI by Hand* example, Paris $$z=5$$, Lyon $$z=2$$, banana $$z=-1$$, and add Marseille $$z=1$$.

**Step 1: softmax at $$T=1$$.**

| Token | $$z$$ | $$e^{z}$$ | $$P = e^z / \sum$$ |
|---|---|---|---|
| Paris | 5 | 148.41 | 0.9007 |
| Lyon | 2 | 7.389 | 0.0448 |
| Marseille | 1 | 2.718 | 0.0165 |
| banana | −1 | 0.368 | 0.0022 |
| | | **158.89** | **0.9642** |

(The probabilities shown are rounded; they sum to 1 before rounding.)

**Step 2: top-k with $$k = 2$$.**  Keep Paris and Lyon.  Discard the rest.

Surviving mass: $$0.9007 + 0.0448 = 0.9455$$.  This is not 1, so it is not yet a distribution.  Divide each survivor by the surviving mass:

| Token | $$P$$ before | $$P$$ after renormalizing |
|---|---|---|
| Paris | 0.9007 | $$0.9007 / 0.9455 =$$ **0.9526** |
| Lyon | 0.0448 | $$0.0448 / 0.9455 =$$ **0.0474** |
| | | sum = **1.0000** yes |

Notice that Paris's probability *went up* (from 0.9007 to 0.9526) without its logit changing at all.  Truncation is not a neutral filter; it redistributes the discarded mass onto the survivors, proportionally.  Every token you cut makes the leaders more likely.

**Step 3: top-p with $$p = 0.9$$, same distribution.**  Accumulate from the top until you reach $$p$$:

| Token | $$P$$ | Running total | In the nucleus? |
|---|---|---|---|
| Paris | 0.9007 | 0.9007 | yes, and 0.9007 ≥ 0.9, so we stop |
| Lyon | 0.0448 | - | no |

The nucleus is Paris alone.  Renormalizing a single survivor gives $$0.9007 / 0.9007 = 1.0$$; the sampler is now deterministic, at a temperature you never set to zero.

This is the whole lesson.  On the *same* distribution, $$k=2$$ leaves Lyon a 4.7% chance and $$p=0.9$$ leaves it none.  Top-p adapts to confidence: when the model is sure, the nucleus collapses to one token; when it is unsure, the nucleus widens.  Top-k does not adapt; $$k=2$$ keeps exactly two candidates whether the model is certain or hopelessly torn.

On the distribution above, you set top-p = 0.95 instead of 0.9.  What is Lyon's probability after renormalization?

- 0.0448, unchanged; renormalization only affects the top token
- 0.0474; the nucleus is {Paris, Lyon} with mass 0.9455, and 0.0448 / 0.9455 = 0.0474
- 0.05, because top-p rounds the nucleus to the threshold
- 0; Lyon falls outside any nucleus below p = 0.99

<details markdown="1"><summary>Answer</summary>

0.0474; the nucleus is {Paris, Lyon} with mass 0.9455, and 0.0448 / 0.9455 = 0.0474

</details>

> **Watch out!**  Because truncation renormalizes, top-k and top-p interact with temperature in ways that are easy to get backwards.  Raising temperature flattens the distribution, which *widens* the top-p nucleus (more tokens are needed to reach $$p$$), so turning temperature up while leaving top-p fixed increases randomness twice over.  For an agent that must emit an exact tool call, this compounding is exactly what you do not want.

> **Common Misconception:** Students often assume that top-p = 0.9 means "keep the top 90% of tokens by count", for example keeping 45,000 out of 50,000 vocabulary entries.  In reality, top-p keeps the *smallest set of tokens* needed to reach 90% of the *total probability mass*.  Because probability mass is extremely concentrated in the top few tokens, top-p = 0.9 typically keeps only 5-50 tokens, not thousands.  The long tail of the vocabulary collectively holds very little probability.

Two things to remember from this example.  Truncation always renormalizes, so cutting tokens makes the survivors more likely than their logits alone would say.  Top-p and temperature compound, because a flatter distribution needs more tokens to reach the same threshold.

---

## Exercises

1.  **Seeded reproducibility.**

   *What to do:* Set the `seed` option to a fixed integer (for example, 42) and run the same prompt five times.  Confirm that all five outputs are identical.  Then change the seed to 99 and show that a different (but again consistent) output results.  Explain in writing why reproducibility matters for grading, science, and agent debugging.

   *Starter hint:* Change `"seed": -1` in the Part II code cell to `"seed": 42`.  Run the cell twice and compare.  Then change to `"seed": 99` and run again.  If outputs differ within the same seed, note whether your Ollama version and hardware support seeded inference.

   *You've succeeded when:* You have side-by-side outputs for seed=42 (five identical runs) and seed=99 (a different but consistent output), plus a two-sentence explanation of why reproducibility matters in each of the three named contexts.

2.  **Sampling policy table.**

   *What to do:* For your future final-project agent team, draft a table assigning temperature and top-p values to each of four agent roles: planner, critic, writer, and judge.  Provide a one-sentence justification for each assignment.

   *Starter hint:* Start with extremes: the planner and critic need to make consistent, structured decisions (low temperature), while the writer benefits from variety (higher temperature).  The judge needs to be consistent but not robotic.  Fill in the middle ground.

   *You've succeeded when:* Your table has four rows, two columns of parameters, and four one-sentence justifications that reference this tutorial's vocabulary (distribution, determinism, nucleus, and so on).

3.  **Hypothesis closure.**

   *What to do:* Return to the hypotheses your team formed in the *Welcome* activity about why identical prompts produced different outputs.  Write one paragraph for each hypothesis: confirmed, refuted, or refined, with specific evidence from the temperature experiments in this tutorial.

   *Starter hint:* Common week-1 hypotheses include "the model stores different versions," "time-of-day affects the server," "the model re-reads the internet," or "there is a random element in the generation."  Map each to the sampling explanation.

   *You've succeeded when:* Every hypothesis from the *Welcome* activity has been addressed in writing, and each verdict (confirmed / refuted / refined) is backed by a specific observation from your temperature experiments.

---

## Reflection Prompt

**Personal level:** People often describe high-temperature output as more "creative" and low-temperature output as more "correct."  Having seen the math, do you accept the word "creative" as a description of what high temperature does?  What intuitions about creativity does the sampling framing fit well, and which does it miss?

**Technical level:** You are designing an agent that writes first drafts of cover letters and then evaluates them for tone consistency with a company's stated values.  What temperature would you set for the drafting step versus the evaluation step, and why?  Would you use top-p, top-k, or neither for the evaluation step?

**Societal level:** The randomness in language model generation means that the same question can produce very different answers for different users at the same moment.  What are the fairness implications of this variability, for example in a system that uses AI to screen job applications or answer student questions?  Should production systems for high-stakes decisions use temperature 0?

---

## Further Reading

- Ari Holtzman et al. "The Curious Case of Neural Text Degeneration."  *ICLR* (2020).  The paper that introduced nucleus sampling.
- Tom Yeh.  *AI by Hand*, softmax worksheets.
- Melanie Mitchell.  *AI: A Guide for Thinking Humans*, Chapter 3.
- Ollama parameter reference (the `options` block: `temperature`, `top_k`, `top_p`, `repeat_penalty`, `num_predict`, `seed`, `stop`): https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values and the API docs at https://github.com/ollama/ollama/blob/main/docs/api.md

---

## Extension: Deterministic and Probabilistic Computing (self-paced)

Nothing above depends on this section.  It is here because the dial you turned in this tutorial has a consequence that outlives it: every program you have written until now returned the same answer for the same input, and this one does not.  That break is worth sitting with, along with automation bias, which is the human half of the same problem.

### Key Concepts

| Term | Definition |
|---|---|
| Deterministic | A system that always produces the same output for the same input |
| Probabilistic / stochastic | A system that samples from a probability distribution, so outputs vary across runs |
| Automation bias | The tendency to over-rely on automated systems, accepting their outputs without independent verification |
| Calibration | A system is calibrated if its stated confidence matches its actual accuracy rate; e.g., a calibrated model that says "80% confidence" is correct 80% of the time |
| Cognitive offloading | Delegating mental work to an external tool or system, reducing cognitive effort at the cost of reduced engagement with the result |

### Before You Start

**What you need:** Nothing installed; this one is discussion and paper first.  Python only if you run the optional demo.

**What you will have at the end:** a working rule for telling deterministic systems from probabilistic ones, and why that changes how you test them.

Work these in sequence.  Each section assumes the one before it, and the code blocks are meant to be executed, not skimmed.

### Why This Matters

Most software you have used behaves predictably: the same input always produces the same output.  AI systems built on large language models deliberately do not.  Understanding why, and what that means for how you interpret and rely on AI outputs, is one of the most practically important ideas in this course.

This extension connects to the sampling and generation material above.  You classify computing systems as deterministic or probabilistic, examine the cognitive trap called *automation bias*, and reason about the specific dangers that arise when people treat probabilistic AI outputs as reliable ground truth.

**Estimated time:** 45-60 minutes

---

### Two Kinds of Computation

In this section you classify computing systems as deterministic or probabilistic and build intuition for why the distinction matters before you meet it in AI.

#### Deterministic Systems

A **deterministic** program always produces exactly the same output given the same input and the same starting state.  There is no randomness; the result is fully predictable.

```python
def add(a, b):
    return a + b

# Always returns 5, no exceptions, no surprises.
print(add(2, 3))
```
{% include pyrun.html %}

Database queries, sorting algorithms, cryptographic hashes, and arithmetic are all deterministic.  This predictability is a feature: it makes these systems easy to test, debug, and trust because you can verify them exhaustively.

Deterministic systems have three key properties:

1.  Reproducibility: run it again, get the same answer.
2.  Verifiability: you can prove correctness by checking every possible input (for finite input spaces).
3.  Debuggability: the bug that produced output X will always produce output X under the same conditions, which makes it findable.

#### Probabilistic Systems

A **probabilistic** (or *stochastic*) program intentionally samples from a probability distribution, so the output varies across runs even with identical input.

```python
import random

def flip_coin():
    return random.choice(["heads", "tails"])

# Could return either, by design.
print(flip_coin())
```
{% include pyrun.html %}

Randomness is not a bug here; it is a feature.  Probabilistic systems are used when we want to explore a space of possibilities, when the real-world phenomenon being modeled is inherently uncertain, or when avoiding predictability is itself valuable (cryptography, game fairness).

Examples outside AI: Monte Carlo retirement simulations, weather forecast models, network routing under load, randomized algorithms in competitive programming.

#### Questions to Work Through

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

- Run 2; it is factually wrong, yet it is presented in the same confident, authoritative prose as the correct answer.  A user cannot tell the difference from the output alone.
- Run 1; consistent outputs suggest the model has memorized rather than understood, which is worse than variance.
- Both are equally dangerous because any AI output should be distrusted.
- Neither; this question is too simple for an LLM to get wrong, so the scenario is unrealistic.

<details markdown="1"><summary>Answer</summary>

Run 2; it is factually wrong, yet it is presented in the same confident, authoritative prose as the correct answer.  A user cannot tell the difference from the output alone.

</details>

> In practice, the same kind of confident-sounding error occurs on far less checkable claims (legal citations, medical statistics, historical dates) where most readers cannot spot the mistake.

**Bridge to the next section:** Now that you can classify systems as deterministic or probabilistic, the next section examines a cognitive trap that makes probabilistic systems especially risky: the human tendency to treat computed outputs as authoritative regardless of whether the system is reliable.

---

### Automation Bias: Why Humans Trust Machines

In this section you examine the research on *automation bias* (the tendency to over-rely on automated systems) and classify the specific failure modes it produces.

#### Automation Bias Defined

**Automation bias** (Parasuraman & Manzey, 2010) is the tendency for humans to over-rely on automated decision aids in two ways:

1.  Omission errors: the human skips manual checks they would have performed without the automated aid, because the machine's output feels sufficient.
2.  Commission errors: the human acts on an incorrect automated recommendation without questioning it, because they defer to the machine's apparent authority.

Automation bias arises even among trained experts, even when the automated system has a known error rate, and even when stakes are high.  In a landmark study, Skitka et al. (1999) found that experienced pilots failed to detect autopilot errors at significantly higher rates when an automation aid was present, *even after being explicitly warned that the aid was imperfect*.

> **Common Misconception:** Automation bias is a problem only for non-technical or "tech-naive" users.  Research consistently shows that trained professionals (pilots, radiologists, financial analysts, software engineers) exhibit automation bias at similar or higher rates than non-experts, precisely because their professional workflow incorporates these tools and they have learned to trust them.

#### A Taxonomy of Trust Failure Modes

Not all trust miscalibration looks the same.  The following four modes each cause a different kind of harm:

| Mode | Description | Example |
|---|---|---|
| **Under-trust** | Human ignores a correct automated recommendation | Dismissing a correct fraud alert because "it feels fine" |
| **Over-trust / automation bias** | Human accepts an incorrect automated recommendation | Following GPS directions into a lake |
| **Complacency** | Human stops monitoring an automated system once it is running | Autopilot disengages silently; pilot doesn't notice for 90 seconds |
| **Skill fade** | Long-term loss of the ability to perform the task manually after years of automation | Unable to navigate without GPS after a decade of relying on it |

#### Questions to Work Through

**Q4.**  In 2023, the attorneys representing a client in *Mata v. Avianca, Inc.* submitted a federal court brief that cited six legal precedent cases, all of which were entirely fictional cases generated by a chatbot.  Neither attorney independently verified any citation.  The judge sanctioned both attorneys.

Which failure mode from the taxonomy above best describes what happened?  What would "appropriately calibrated trust" have looked like?

> *Hint:* Attorneys have a professional and ethical obligation to verify every citation before submitting a brief.  The question is not whether they trusted the tool, but why the trust was not bounded by the verification step they knew was required.

**Q5.**  A hospital deploys an AI system that flags potential drug interactions for nursing review.  A nurse, disagreeing with a specific flag based on her clinical experience, overrides it without documenting her reasoning.

Is this automation bias, appropriate expert judgment, or something else?  What information would you need to determine which?

> *Hint:* Both under-trust and over-trust are errors.  The right answer depends on: the nurse's track record vs. the AI's precision and recall on this flag type, whether the patient is harmed by the override, and whether lack of documentation creates institutional risk regardless of outcome.

**Q6.**  Which of the following best explains why automation bias persists even when humans consciously know that a system is fallible?

- Checking automated outputs requires effortful cognition.  The brain conserves effort when it perceives a trusted external source, a process psychologists call "cognitive offloading."  This is adaptive in most contexts but becomes dangerous when the trusted source is unreliable.
- Humans inherently distrust their own judgment and will always prefer any external signal over their own reasoning.
- Automation bias has been largely debunked; modern users who understand AI do not exhibit it.
- Trained users never exhibit automation bias; only untrained or non-expert users do.

<details markdown="1"><summary>Answer</summary>

Checking automated outputs requires effortful cognition.  The brain conserves effort when it perceives a trusted external source, a process psychologists call "cognitive offloading."  This is adaptive in most contexts but becomes dangerous when the trusted source is unreliable.

</details>

**Bridge to the next section:** You have now seen that humans over-trust automated systems even when they know better.  The next section asks: what happens when the automated system is not only fallible but *cannot* signal its own uncertainty?  That combination (probabilistic outputs delivered with authoritative-looking confidence) is what makes LLMs distinctively risky.

---

### The Danger When Probabilistic Meets Authoritative

In this section you combine the two previous sections to reason about the failure mode that is specific to large language models: high-confidence-sounding outputs from an inherently probabilistic system, consumed by users who are primed to over-trust.

#### The Confidence-Calibration Gap

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

#### Three Compounding Risk Factors

When probabilistic AI outputs are treated as authoritative, three factors compound to make the problem worse than it would be with any other unreliable information source:

| Risk Factor | Why It Matters |
|---|---|
| **Surface credibility** | Well-formed prose, plausible structure, and specific-sounding details make false claims hard to distinguish from true ones without independent verification. Fabricated citations look like real citations. |
| **Volume** | AI can generate hundreds of plausible-sounding claims per minute. The cognitive load to verify each one is multiplicatively larger than the cost to generate them. |
| **Domain opacity** | Many high-stakes AI use cases (medical, legal, scientific, financial) are precisely the domains where most users lack the expertise to evaluate the output independently. The highest-stakes domains have the lowest baseline for catching errors. |

#### Questions to Work Through

**Q7.**  Design a concise "sanity check" protocol (at most four steps) that a student should apply before using any piece of AI-generated information in a graded assignment.  Be specific; avoid vague steps like "check if it's right."

> *Hint:* Think about: (1) Is this the kind of claim that *can* be verified with a primary source?  (2) What would happen if it were wrong?  (3) How would I explain to an instructor that I verified this?

**Q8.**  A classmate argues: "This problem will go away once AI systems always display explicit confidence scores on every output."  Do you agree?  What risk factors from the Three Compounding Risk Factors table would still remain even if confidence scores were perfect?

> *Hint:* Think about calibration: does "80% confidence" mean the model is right 80% of the time on this type of claim?  Who would check?  And consider: does a confidence score on each sentence solve the volume problem, or does reading 200 scores per document add another layer of cognitive load?

**Q9.**  Match each real-world scenario to the primary risk factor from the Three Compounding Risk Factors table (Surface Credibility, Volume, or Domain Opacity) that makes it most dangerous:

| Scenario | Primary Risk Factor |
|---|---|
| A student submits a 15-source bibliography; three citations are AI-generated and fictional, but formatted correctly and plausibly titled | |
| A content moderation system flags 40,000 posts per hour; human reviewers approve AI decisions without reading flagged content because the queue never clears | |
| An AI-generated radiology summary misidentifies a lesion; the reviewing radiologist, who is not an AI expert, assumes the AI output reflects ground truth | |

**Q10.**  Which design change most directly reduces automation bias without requiring users to become AI experts?

- Displaying explicit uncertainty language ("I am not confident about this; please verify"), requiring confirmation before high-stakes outputs are acted upon, and showing alternative responses alongside the primary one, so the user perceives the system as offering options, not delivering verdicts.
- Making the AI system fully deterministic, so it always gives the same answer and users know what to expect.
- Increasing the AI's accuracy to 99%; at that threshold, automation bias becomes statistically acceptable.
- Removing AI from high-stakes domains entirely until the technology is perfect.

<details markdown="1"><summary>Answer</summary>

Displaying explicit uncertainty language ("I am not confident about this; please verify"), requiring confirmation before high-stakes outputs are acted upon, and showing alternative responses alongside the primary one, so the user perceives the system as offering options, not delivering verdicts.

</details>

---

### Synthesis: Discussion

Agree on answers to the following with your team, or write them yourself if you are working alone:

1.  In one sentence, complete this argument: "It is specifically dangerous to treat probabilistic AI outputs as authoritative because ___."

2.  Name one domain *outside of AI* where deterministic outputs are treated as more authoritative than they deserve to be.

3.  State one concrete habit you will adopt after this extension to protect yourself from automation bias when using AI tools in this course or professionally.

4.  *Challenge question:* Could an AI system be designed that is both probabilistic *and* well-calibrated in its expressed confidence?  What would that require, and why don't current LLMs do it?
