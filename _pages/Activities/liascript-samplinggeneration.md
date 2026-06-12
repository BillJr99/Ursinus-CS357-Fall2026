# Why Different Answers Every Time? Sampling, Temperature, and Generation
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

In week 1 we observed a deterministic computer producing different answers to identical prompts, and your teams formed hypotheses. Today we resolve the mystery: a language model computes a **probability distribution over the next token**, and the system **samples** from it. We move from **next-token prediction $\rightarrow$ softmax and temperature $\rightarrow$ top-k and top-p $\rightarrow$ experiments on our own stack**, and we connect every knob to agent design.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Generation as Repeated Prediction

## 1. One Token at a Time

**A language model is a next-token predictor.** Given the tokens so far, it outputs a score (a *logit*) $z_i$ for every token $i$ in its vocabulary, then converts scores to probabilities with the **softmax**:

$$
P(i) = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}
$$

The system samples one token from this distribution, appends it, and repeats until a stop token. Generation is a loop of predictions, which means a single early sampling choice can steer the entire continuation. This is your hypothesis test from week 1: the randomness lives in the *sampling step*, not in the model weights.

**Temperature $T$ reshapes the distribution.** As $T \to 0$, the largest logit dominates and sampling approaches deterministic *greedy* decoding. As $T$ grows, the distribution flattens and unlikely tokens gain probability. Temperature does not add knowledge; it redistributes confidence.

---

## Model 1: Temperature by Hand

Suppose the model's logits for the next word after "The capital of France is" are: Paris $z=5$, Lyon $z=2$, banana $z=-1$.

### Critical Thinking Questions

1. Compute (calculator permitted) $P(\text{Paris})$ at $T=1$. Now recompute at $T=0.5$ and at $T=2$. The Recorder tabulates all three.
2. At which temperature does "banana" have the best chance? Generalize: what does temperature do to the *tail* of the distribution?
3. An agent inside a loop must output exactly `calc(...)` or `Final Answer:`. Using your table, argue for the temperature you would set, and identify what could still go wrong even at $T=0$.

---

## 2. Truncation: Top-k and Top-p

Temperature reshapes; **truncation removes**. **Top-k** sampling keeps only the $k$ highest-probability tokens and renormalizes. **Top-p (nucleus)** sampling keeps the smallest set of tokens whose cumulative probability reaches $p$:

$$
V_p = \text{smallest } V' \text{ such that } \sum_{i \in V'} P(i) \ge p
$$

Top-p adapts to the situation: when the model is confident, the nucleus is tiny; when many continuations are plausible, the nucleus widens. In practice, creative tasks favor higher temperature with top-p near $0.9$, while agentic control steps favor temperature near $0$.

[[MC]]
A distribution gives Paris 0.90, Lyon 0.06, Marseille 0.03, banana 0.01. With top-p $= 0.95$, the candidate set is:
- ( ) Paris only
- (x) Paris and Lyon
- ( ) Paris, Lyon, and Marseille
- ( ) All four tokens

---

# Part II: Experiments on Your Stack

## 3. Measuring Variability

We quantify "how different are the answers" by sampling repeatedly and counting distinct outputs.

---

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

### Critical Thinking Questions

4. At $T=0.0$, did all eight runs agree? If not, propose where residual nondeterminism could enter a real serving stack (consider batching, hardware arithmetic, and seeds).
5. Plot (or sketch) distinct-answer count versus temperature. Where is the knee of the curve for your model?
6. Repeat with the prompt "Write the first line of a poem about autumn." Should an agent that *drafts creative text* and an agent that *routes requests to tools* share a temperature? Assign each a setting and defend it.

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Seeded reproducibility.* Ollama accepts a fixed `seed` option. Demonstrate that a fixed seed with fixed parameters reproduces output exactly, and explain why reproducibility matters for grading, science, and debugging agents.
2. *Sampling policy table.* For your future final-project agent team, draft a table assigning temperature and top-p to each role (planner, critic, writer, judge) with one-sentence justifications.
3. *Hypothesis closure.* Return to your team's week 1 hypotheses about nondeterminism. The Recorder writes one paragraph stating which were confirmed, refuted, or refined, with evidence from today.

---

## Reflection Prompt

In your notebook: people often describe high-temperature output as more "creative." Having seen the math, do you accept that word? What is the difference, if any, between creativity and well-managed randomness?

---

## 5. Further Reading

- Ari Holtzman et al. "The Curious Case of Neural Text Degeneration." *ICLR* (2020). The paper that introduced nucleus sampling.
- Tom Yeh. *AI by Hand*, softmax worksheets.
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 3.
