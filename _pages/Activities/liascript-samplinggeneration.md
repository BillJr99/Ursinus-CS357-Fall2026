<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-samplinggeneration.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-samplinggeneration.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Why Different Answers Every Time? Sampling, Temperature, and Generation

In week 1 we observed a deterministic computer producing different answers to identical prompts, and your teams formed hypotheses. Today we resolve the mystery: a language model computes a **probability distribution over the next word-piece (token)**, and the system **samples** from it — rolling a weighted die at each step. We move from **next-token prediction $\rightarrow$ softmax and temperature $\rightarrow$ top-k and top-p $\rightarrow$ experiments on our own stack**, and we connect every knob to agent design.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| Token | A unit of text — roughly a word, a word-part, or a punctuation mark — that the model reads and writes one at a time | The sentence "The cat sat." is four tokens: "The", " cat", " sat", "." |
| Softmax | A mathematical function that converts raw model scores (called logits) into a probability distribution that adds up to 1.0 — making the scores comparable and interpretable | Turning logits of (5, 2, -1) for (Paris, Lyon, banana) into probabilities like (0.95, 0.05, 0.001) |
| Temperature | A number that controls how "peaked" or "flat" the probability distribution is — low temperature makes the most likely token nearly certain, high temperature makes unlikely tokens more competitive | Setting `temperature=0.0` in the agent loop to get the same tool-call format every time |
| Top-k sampling | A technique that keeps only the k highest-probability tokens before sampling, discarding the long tail of unlikely options | With k=5, only the five most probable next words are considered, even if there are 50,000 in the vocabulary |
| Top-p (nucleus) sampling | A technique that keeps the smallest group of tokens whose combined probability reaches a threshold p, adapting to how confident the model is at each step | With p=0.9, if Paris alone has probability 0.92, only Paris is kept; if the top 10 words share 0.9 probability, all 10 are kept |
| Greedy decoding | The strategy of always picking the single most probable next token, equivalent to temperature = 0 — deterministic but sometimes repetitive or locally optimal but globally suboptimal | An agent with temperature=0.0 that always picks the same action regardless of context |

---

# Part I: Generation as Repeated Prediction

In this part, you will work out by hand how a language model converts raw scores into a probability distribution and then samples from it — resolving the mystery from week 1 of why identical prompts produce different outputs. The math here (softmax and temperature) will recur every time you tune an agent's behavior for the rest of the semester.

## 1. One Token at a Time

Before we look at the math, consider how autocomplete on your phone works: it suggests the next word based on what you have typed. A language model does exactly the same thing, but instead of a fixed list of three suggestions, it assigns a probability to every word in its entire vocabulary (often 50,000 or more), then picks one — and repeats this process for every single word in its response. That is why a single early "wrong pick" can send the whole response in a surprising direction, and why the same prompt can produce different responses on different runs.

**A language model is a next-token predictor.** Given the tokens so far, it outputs a raw score (called a *logit* — pronounced "low-jit," short for log-odds unit — just a number with no fixed range) $z_i$ for every token $i$ in its vocabulary, then converts scores to probabilities with the **softmax** function (a formula that squashes any set of numbers into values that sum to 1.0):

$$
P(i) = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}
$$

The system samples one token from this distribution, appends it to the text, and repeats until a stop token appears. Generation is a loop of single predictions — one word-piece at a time — which means a single early sampling choice can steer the entire continuation. This is your hypothesis test from week 1: the randomness lives in the *sampling step*, not in the model weights, which stay fixed.

**Temperature $T$ reshapes the distribution.** As $T \to 0$, the highest-scoring token dominates and sampling approaches deterministic *greedy decoding* (always picking the top word). As $T$ grows, the distribution flattens and less-likely tokens gain probability. Temperature does not add knowledge; it redistributes confidence across the existing options.

---

## Model 1: Temperature by Hand

Suppose the model's logits (raw scores) for the next word after "The capital of France is" are: Paris $z=5$, Lyon $z=2$, banana $z=-1$. We will compute what temperature does to the probability of each word.

### Critical Thinking Questions

1. Compute (calculator permitted) $P(\text{Paris})$ at $T=1$. Now recompute at $T=0.5$ and at $T=2$. The Recorder tabulates all three values in a single table with columns for $T$ and rows for each word.

   > *Hint: For each temperature, compute $e^{z/T}$ for all three words, add those three values together to get the denominator, then divide each word's $e^{z/T}$ by the denominator. For Paris at T=1: $e^5 \approx 148.4$, $e^2 \approx 7.4$, $e^{-1} \approx 0.37$, sum $\approx 156.1$, so $P(\text{Paris}) \approx 148.4 / 156.1 \approx 0.951$.*

2. At which temperature does "banana" have the best relative chance of being selected? Generalize: what does increasing temperature do to the *tail* of the distribution (the words that started out with very low scores)?

   > *Hint: Compare the ratio $P(\text{banana}) / P(\text{Paris})$ at $T=1$ versus $T=2$. Does the gap shrink or grow as temperature rises?*

3. An agent inside a loop must output exactly `calc(...)` or `Final Answer:`. Using your calculated table, argue for the temperature you would set for an agent's reasoning step, and identify what could still go wrong even at $T=0$.

   > *Hint: Even at $T=0$ (greedy decoding), the model always picks the top token — but what if the top token is part of a malformed tool call? Greedy does not guarantee correctness, only consistency.*

---

## 2. Truncation: Top-k and Top-p

Temperature reshapes the whole distribution; **truncation** removes the options the model considers entirely. **Top-k** sampling keeps only the $k$ highest-probability tokens and renormalizes the remaining probabilities to sum to 1.0. **Top-p (nucleus) sampling** keeps the smallest group of tokens whose combined probability reaches the threshold $p$:

$$
V_p = \text{smallest } V' \text{ such that } \sum_{i \in V'} P(i) \ge p
$$

The key advantage of top-p over top-k is that top-p **adapts to the model's confidence**: when the model is very sure (one word has probability 0.95), the nucleus contains just that word; when many continuations are plausible (ten words each with probability 0.09), the nucleus widens to include all of them. In practice, creative writing tasks often favor higher temperature (0.7-1.0) combined with top-p near 0.9, while agentic control steps that must output exact tool calls favor temperature near 0.0.

[[MC]]
A distribution assigns probabilities: Paris 0.90, Lyon 0.06, Marseille 0.03, banana 0.01. With top-p $= 0.95$, the candidate set is:
- ( ) Paris only (0.90 already exceeds 0.95 minus a rounding edge)
- (x) Paris and Lyon (0.90 + 0.06 = 0.96, which first reaches or exceeds 0.95)
- ( ) Paris, Lyon, and Marseille
- ( ) All four tokens

> **⚠️ Common Misconception:** Students often assume that top-p = 0.9 means "keep the top 90% of tokens by count" — for example, keeping 45,000 out of 50,000 vocabulary entries. In reality, top-p keeps the *smallest set of tokens* needed to reach 90% of the *total probability mass*. Because probability mass is extremely concentrated in the top few tokens, top-p = 0.9 typically keeps only 5-50 tokens, not thousands. The long tail of the vocabulary collectively holds very little probability.

---

# Part II: Experiments on Your Stack

In this part, you will run a controlled experiment that makes the theory from Part I visible: you will sample the same prompt eight times at three different temperatures and count how often the answers diverge. This turns an intuitive observation into a measurable, reproducible result.

## 3. Measuring Variability

We quantify "how different are the answers" by sampling the same prompt multiple times and counting how many distinct outputs appear. This turns an intuitive observation ("it seems to vary a lot at high temperature") into a measurable result.

---

The code below asks the model to name a single animal eight times at each of three temperature settings and uses a `Counter` (a Python dictionary that counts occurrences) to tally how many distinct answers appear. A temperature of 0.0 should produce the same answer every time; higher temperatures should spread answers across more options.

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

Examine the counter output for each temperature. Notice which temperatures produce the same answer eight times, which produce two or three variations, and which produce eight completely different answers.

### Critical Thinking Questions

4. At $T=0.0$, did all eight runs produce the same answer? If any runs differed, propose where residual non-determinism could enter a real serving system — consider hardware-level floating-point rounding, batching multiple requests together, and whether your Ollama server truly respects seed=-1.

   > *Hint: Even "deterministic" floating-point arithmetic can give slightly different results on different CPU/GPU hardware due to the order of operations in parallel computation. A production model server may batch several requests together, which changes the arithmetic order.*

5. Sketch (or describe) the shape of a graph with temperature on the x-axis and "number of distinct answers out of 8 runs" on the y-axis. Where is the knee of the curve for your model — the temperature at which answers begin to diverge noticeably?

   > *Hint: Plot three points: T=0, T=0.7, T=1.5. Is the transition gradual or sudden? Does the knee appear closer to 0 or closer to 1?*

6. Repeat the experiment with the prompt "Write the first line of a poem about autumn." Should an agent that *drafts creative text* and an agent that *routes requests to tools* share the same temperature setting? Assign each a specific temperature value and write one sentence defending each choice.

   > *Hint: For the routing agent, think about what happens if "route to weather tool" becomes "route to music tool" just because of random sampling. For the creative agent, think about what "always the same first line" means for a poem generator.*

---

# Part III: Synthesis and Practice

In this part, you will apply the sampling vocabulary to real design decisions — choosing temperature and top-p settings for different agent roles — and close the loop on the hypotheses your team formed in week 1.

## 4. Exercises

1. *Seeded reproducibility.*

   - *What to do*: Set the `seed` option to a fixed integer (for example, 42) and run the same prompt five times. Confirm that all five outputs are identical. Then change the seed to 99 and show that a different (but again consistent) output results. Explain in writing why reproducibility matters for grading, science, and agent debugging.
   - *Starter hint*: Change `"seed": -1` in the code cell to `"seed": 42`. Run the cell twice and compare. Then change to `"seed": 99` and run again. If outputs differ within the same seed, note whether your Ollama version and hardware support seeded inference.
   - *You've succeeded when*: You have side-by-side outputs for seed=42 (five identical runs) and seed=99 (a different but consistent output), plus a two-sentence explanation of why reproducibility matters in each of the three named contexts.

2. *Sampling policy table.*

   - *What to do*: For your future final-project agent team, draft a table assigning temperature and top-p values to each of four agent roles: planner, critic, writer, and judge. Provide a one-sentence justification for each assignment.
   - *Starter hint*: Start with extremes — the planner and critic need to make consistent, structured decisions (low temperature), while the writer benefits from variety (higher temperature). The judge needs to be consistent but not robotic. Fill in the middle ground.
   - *You've succeeded when*: Your table has four rows, two columns of parameters, and four one-sentence justifications that reference today's vocabulary (distribution, determinism, nucleus, etc.).

3. *Hypothesis closure.*

   - *What to do*: Return to your team's week 1 hypotheses about why identical prompts produced different outputs. The Recorder writes one paragraph for each hypothesis: confirmed, refuted, or refined — with specific evidence from today's experiment.
   - *Starter hint*: Common week-1 hypotheses include "the model stores different versions," "time-of-day affects the server," "the model re-reads the internet," or "there is a random element in the generation." Map each to today's sampling explanation.
   - *You've succeeded when*: Every hypothesis from week 1 has been addressed in writing, and each verdict (confirmed / refuted / refined) is backed by a specific observation from today's temperature experiments.

---

## Reflection Prompt

*Personal*: People often describe high-temperature output as more "creative" and low-temperature output as more "correct." Having seen the math, do you accept the word "creative" as a description of what high temperature does? What intuitions about creativity does the sampling framing fit well, and which does it miss?

*Technical*: You are designing an agent that writes first drafts of cover letters and then evaluates them for tone consistency with a company's stated values. What temperature would you set for the drafting step versus the evaluation step, and why? Would you use top-p, top-k, or neither for the evaluation step?

*Societal*: The randomness in language model generation means that the same question can produce very different answers for different users at the same moment. What are the fairness implications of this variability — for example, in a system that uses AI to screen job applications or answer student questions? Should production systems for high-stakes decisions use temperature 0?

---

→ Coming Up Next: We know how models generate text — but how do we know whether what they generate is *correct*? In the next activity we build our first evaluation harness, measure hallucination rates, and learn why "it seems pretty good" is not good enough.

## 5. Further Reading

- Ari Holtzman et al. "The Curious Case of Neural Text Degeneration." *ICLR* (2020). The paper that introduced nucleus sampling.
- Tom Yeh. *AI by Hand*, softmax worksheets.
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 3.
