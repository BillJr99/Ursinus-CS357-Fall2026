<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-attentiontransformers.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-attentiontransformers.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Attention and Transformers, Conceptually and by Hand

The embeddings from the *Tokens and Embeddings: How Agents Represent Meaning* activity give each token a meaning vector; today's **attention** lets every token *update* its meaning by looking at its neighbors, which is how "bank" near "river" differs from "bank" near "loan." We work **use-inspired**: enough mechanism to reason about agent behavior, computed once **by hand** in the AI by Hand tradition, then verified in NumPy. The arc is **the disambiguation problem → queries, keys, values → a worked 3-token example → what this explains about context windows**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

Before diving in, orient yourself with the vocabulary you will use throughout today's activity. Each term below has a plain-English definition and a pointer to where you will encounter it.

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Token** | A chunk of text (roughly a word or word-piece) that the model processes as a single unit | "river", "bank", and "loan" are the three tokens in Model 1 |
| **Embedding** | A list of numbers (a vector) that encodes the meaning of a token | The query, key, and value vectors in the Model 1 table |
| **Dot product** | A single number computed by multiplying matching entries of two vectors and adding the results; large values mean the vectors point in similar directions | $\mathbf{q}_{\text{bank}} \cdot \mathbf{k}_{\text{loan}} = 1\times1 + 1\times1 = 2$ |
| **Softmax** | A function that turns a list of raw scores into a list of weights that sum to 1, so they can be used as probabilities | Converts scaled scores [0.71, 0.71, 1.41] into attention weights [0.25, 0.25, 0.50] |
| **Attention weight** | How much one token "looks at" another; a higher weight means more influence on the updated meaning | "bank" attends to "loan" with weight 0.50 in the full three-token sentence |
| **Context window** | The maximum number of tokens a model can consider at once; bounded by the $O(n^2)$ cost of attention | Growing a prompt from 2 k to 8 k tokens multiplies attention cost by 16× |

---

# Part I: The Idea of Attention

In this Part, you will learn why a static word-meaning table is not enough for language understanding, and you will work through the attention calculation by hand using a three-token example. By the end, you will have computed exactly how context shifts the meaning of an ambiguous word — and you will understand the arithmetic that every large language model repeats billions of times per second.

## 1. Context Changes Meaning

**Why attention matters — the short version.** Think of attention as how the model decides which words to "look at" when building the meaning of each token — like a musician who simultaneously glances at the sheet music *and* the conductor, blending both signals into every note they play. The model does the same thing in every layer: each token briefly "consults" every other token and blends in a little of their meaning, weighted by relevance.

**Static embeddings are not enough.** The token "bank" deserves different vectors in "river bank" and "bank loan," yet a lookup table gives it one. Attention solves this by letting each token form a new representation as a **weighted average of all tokens' values**, with weights determined by relevance.

**Queries, keys, and values.** Each token's embedding $\mathbf{x}_i$ is projected into three roles: a **query** $\mathbf{q}_i$ ("what am I looking for?"), a **key** $\mathbf{k}_i$ ("what do I offer as a match?"), and a **value** $\mathbf{v}_i$ ("what content do I contribute if selected?"). Think of it like a library search: the query is your search term, the keys are the index cards, and the values are the actual book contents. Relevance of token $j$ to token $i$ is the dot product $\mathbf{q}_i \cdot \mathbf{k}_j$, normalized across all $j$ by softmax:

$$
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right) V
$$

Breaking the formula down symbol by symbol:

- $Q$ is the matrix of all query vectors (one row per token).
- $K$ is the matrix of all key vectors (one row per token).
- $K^\top$ means we transpose $K$ so we can multiply it against $Q$.
- $QK^\top$ produces a grid of dot products — every token's query against every token's key.
- $d_k$ is the dimension of the key vectors (2 in today's toy example).
- $\sqrt{d_k}$ is the square root of that dimension; dividing by it keeps the numbers from getting too large and squashing the softmax into a near-zero gradient.
- $\text{softmax}(\cdots)$ converts the scaled dot products into weights that sum to 1.
- Multiplying by $V$ (the value matrix) blends each token's content according to those weights.

The $\sqrt{d_k}$ keeps dot products from growing with dimension and saturating (pushing to extreme values) the softmax. A **transformer** (the neural network architecture underlying GPT, Claude, and nearly every modern LLM) stacks this operation (in parallel "heads," interleaved with small neural networks) dozens of times; **causal masking** (blocking each token from attending to any token that comes later in the sequence) during generation prevents tokens from attending to the future.

---

## Model 1: Attention by Hand

**Why this model matters.** The three-token sentence "river bank loan" is a perfect stress-test for a word-sense system: "bank" could be a financial institution or a riverbank, and only context can tell us which. By computing attention by hand, you will see exactly how the surrounding tokens shift the meaning of "bank" — the same arithmetic that runs inside every large language model you have used. Think of it as opening the hood: the engine turns out to be repeated dot products, divisions, and weighted sums.

Use a 2-dimensional toy with three tokens, with these (already-projected) vectors:

| token | $\mathbf{q}$ | $\mathbf{k}$ | $\mathbf{v}$ |
|-------|------|------|------|
| river | (1, 0) | (1, 0) | (1, 1) |
| bank  | (1, 1) | (0, 1) | (2, 0) |
| loan  | (0, 1) | (1, 1) | (0, 2) |

Compute the new representation of **bank** ($d_k = 2$, so divide scores by $\sqrt{2} \approx 1.41$).

### Worked Example: All Arithmetic Shown

Follow these four steps exactly. The Critical Thinking Questions will then ask you to repeat the process and extend it.

---

**Step 1 — Raw dot products: $\mathbf{q}_{\text{bank}} \cdot \mathbf{k}_j$ for each $j$**

A dot product of two 2-dimensional vectors $(a_1, a_2)$ and $(b_1, b_2)$ is computed as $a_1 \times b_1 + a_2 \times b_2$. We use $\mathbf{q}_{\text{bank}} = (1, 1)$ as our query and compare it against every token's key vector.

- **vs. river** — $\mathbf{k}_{\text{river}} = (1, 0)$:

  $1 \times 1 + 1 \times 0 = 1 + 0 = \mathbf{1}$

- **vs. bank** (itself) — $\mathbf{k}_{\text{bank}} = (0, 1)$:

  $1 \times 0 + 1 \times 1 = 0 + 1 = \mathbf{1}$

- **vs. loan** — $\mathbf{k}_{\text{loan}} = (1, 1)$:

  $1 \times 1 + 1 \times 1 = 1 + 1 = \mathbf{2}$

Raw scores: $[1, \; 1, \; 2]$

---

**Step 2 — Scale by $\sqrt{d_k}$**

We have $d_k = 2$ (the dimension of the key vectors), so $\sqrt{d_k} = \sqrt{2} \approx 1.41$.

Dividing each raw score by 1.41:

- river: $1 \div 1.41 \approx \mathbf{0.71}$
- bank: $1 \div 1.41 \approx \mathbf{0.71}$
- loan: $2 \div 1.41 \approx \mathbf{1.41}$

Scaled scores: $[0.71, \; 0.71, \; 1.41]$

*Why divide at all?* In higher-dimensional spaces, dot products naturally grow larger (more terms to add), which can push softmax outputs toward 0 or 1 and make learning unstable. Dividing by $\sqrt{d_k}$ keeps the scale in a comfortable range regardless of dimension.

---

**Step 3 — Softmax: convert scores to weights**

Softmax raises $e$ (Euler's number, $\approx 2.718$) to the power of each score, then divides each result by their sum. This guarantees all weights are positive and sum to exactly 1.

Compute $e^s$ for each scaled score $s$:

- river: $e^{0.71} \approx \mathbf{2.03}$
- bank: $e^{0.71} \approx \mathbf{2.03}$
- loan: $e^{1.41} \approx \mathbf{4.10}$

Sum: $2.03 + 2.03 + 4.10 = \mathbf{8.16}$

Divide each by the sum to get the attention weights:

- $w_{\text{river}} = 2.03 \div 8.16 \approx \mathbf{0.25}$
- $w_{\text{bank}} = 2.03 \div 8.16 \approx \mathbf{0.25}$
- $w_{\text{loan}} = 4.10 \div 8.16 \approx \mathbf{0.50}$

Attention weights: $[0.25, \; 0.25, \; 0.50]$

"bank" attends to "loan" with the highest weight (0.50) — twice as much as to either of the other tokens.

---

**Step 4 — Weighted sum of value vectors**

The new representation of "bank" is a blend of all three value vectors, weighted by the attention weights we just computed. Each value vector is multiplied by its weight entry-by-entry, then the results are added together.

Value vectors: $\mathbf{v}_{\text{river}} = (1,1)$, $\mathbf{v}_{\text{bank}} = (2,0)$, $\mathbf{v}_{\text{loan}} = (0,2)$.

$$
\text{new\_bank} = 0.25 \times (1,1) \;+\; 0.25 \times (2,0) \;+\; 0.50 \times (0,2)
$$

Computing each scaled vector:

- $0.25 \times (1,1) = (0.25, \; 0.25)$
- $0.25 \times (2,0) = (0.50, \; 0.00)$
- $0.50 \times (0,2) = (0.00, \; 1.00)$

Adding the first components: $0.25 + 0.50 + 0.00 = \mathbf{0.75}$

Adding the second components: $0.25 + 0.00 + 1.00 = \mathbf{1.25}$

$$
\text{new\_bank} \approx (0.75, \; 1.25)
$$

**Interpretation.** Compare this to $\mathbf{v}_{\text{bank}} = (2, 0)$ — the static embedding with no context. The new vector has a *much* larger second component (1.25 vs. 0) and a smaller first component (0.75 vs. 2). The second dimension was contributed heavily by the "loan" token (whose value vector is $(0, 2)$), meaning the financial sense of "bank" has been pulled into the representation by the surrounding context. This is the core mechanism of transformer-based language models: static meaning updated by weighted context.

---

### Critical Thinking Questions

1. Compute the three raw scores $\mathbf{q}_{\text{bank}} \cdot \mathbf{k}_j$ for $j \in \{\text{river}, \text{bank}, \text{loan}\}$. The Recorder shows each dot product.

   *Hint:* Dot product of $(a_1, a_2)$ and $(b_1, b_2)$ is $a_1 b_1 + a_2 b_2$. You can check your answers against the Worked Example above — all three raw scores are computed there step by step.

2. Divide by $\sqrt{2}$ and apply softmax (calculator permitted; two decimal places suffice). Which token receives the most attention from "bank"?

   *Hint:* First divide each raw score by 1.41. Then compute $e^s$ for each scaled score $s$, sum those values, and divide each $e^s$ by the sum. The token with the largest resulting weight receives the most attention.

3. Form the weighted sum of the value vectors. Compare the result with $\mathbf{v}_{\text{bank}}$ alone: in what direction did context pull the meaning of "bank"?

   *Hint:* Multiply each value vector by its attention weight from CTQ 2, then add the three resulting vectors component-by-component. Compare the first and second components of the result to $(2, 0)$.

4. Suppose the sentence were "bank loan" without "river." Recompute the weights over just two tokens. Does "bank" now lean differently? This is contextualization in action.

   *Hint:* Repeat Steps 1–3 from the Worked Example, but only include $j \in \{\text{bank}, \text{loan}\}$. Raw scores are still $\mathbf{q}_{\text{bank}} \cdot \mathbf{k}_j$; there are now only two softmax inputs, so the weights must sum to 1 over two tokens instead of three.

---

## Code Cell

```python
import numpy as np

np.random.seed(42)

q = {"river": np.array([1., 0.]), "bank": np.array([1., 1.]), "loan": np.array([0., 1.])}
k = {"river": np.array([1., 0.]), "bank": np.array([0., 1.]), "loan": np.array([1., 1.])}
v = {"river": np.array([1., 1.]), "bank": np.array([2., 0.]), "loan": np.array([0., 2.])}
tokens = ["river", "bank", "loan"]

def softmax(z):
    e = np.exp(z - z.max())
    return e / e.sum()

scores = np.array([q["bank"] @ k[t] for t in tokens]) / np.sqrt(2)
weights = softmax(scores)
new_bank = sum(w * v[t] for w, t in zip(weights, tokens))

print("scores :", np.round(scores, 3))
print("weights:", np.round(weights, 3))
print("new bank representation:", np.round(new_bank, 3))
# Check this against your by-hand computation: they should match.
```

---

*You have just computed the mechanism inside every transformer layer. Part II connects that mechanism to the practical constraints you will hit when building and deploying agents — especially the context window limit and the "lost in the middle" effect.*

# Part II: What Attention Explains About Agents

## 2. Consequences You Have Already Met

**Why this matters for the agents you will build.** The attention mechanism is not just a mathematical curiosity — it directly sets the budget you have to work with when deploying a language-model agent. Think of the musician analogy again: the musician can only see so much sheet music at once. A transformer's "sheet music" is its context window (the maximum number of tokens the model can consider in one pass), and the cost of attention determines exactly how large that window can be. Understanding this constraint is what separates an agent that works in production from one that runs out of memory on the first long document.

**The context window is the attention span, literally.** Attention compares every token with every other, costing $O(n^2)$ in sequence length $n$; doubling context quadruples this work. This is why context windows are finite, why long contexts are slow on your laptop, and why the *small context window principle* we adopt in the *Memory and the Small Context Window Principle* activity is not merely aesthetic but computational.

**Position matters.** Models attend most reliably to the beginning and end of long contexts (the "lost in the middle" effect), which is why we will place an agent's instructions and the current question at the edges of the prompt, with retrieved evidence in between.

[[MC]]
An agent's prompt grows from 2,000 to 8,000 tokens. Since attention compares every token with every other token, the computation per layer grows by approximately a factor of:
- ( ) 2 — as if attention grew linearly with the number of tokens
- ( ) 4 — as if only the number of tokens doubled and cost doubled with it
- (x) 16 — because 8,000² ÷ 2,000² = 64,000,000 ÷ 4,000,000 = 16; the cost is quadratic ($O(n^2)$)
- ( ) It does not grow; attention is constant-time

> **⚠️ Common Misconception: "More context is always better"**
>
> It is tempting to assume that giving a model a longer context — more background, more examples, more retrieved documents — always improves its answers. The attention mechanism reveals why this is not true. First, the computational cost grows as $O(n^2)$: quadrupling the context length multiplies the attention work by 16×. Second, the "lost in the middle" effect shows that models reliably extract information from the *beginning* and *end* of long prompts but often miss material buried in the middle. Third, every extra token competes for the finite "attention budget" of each query token, potentially diluting the signal from the most relevant parts of the prompt. The practical lesson: be selective. Retrieve only what is relevant, place it strategically, and keep prompts as short as the task allows.

---

*Part II connected attention arithmetic to practical agent constraints. Part III asks you to apply both: compute attention for a second token, experiment with masking, and reason about scaling — the three skills that will recur whenever you tune a prompt or choose a retrieval strategy.*

---

# Part III: Synthesis and Practice

> Work through the full matrix below at home; it is the same arithmetic as Model 1, carried out for every pair of words.

## Worked Example: the full $QK^\top$ matrix

Model 1 computed one row — the query for "bank." Exercise 1 asks you to do "river." Here is the whole matrix at once, because seeing all three rows together is what makes the mechanism click: **attention is not a special operation applied to one token, it is the same operation applied to every token in parallel.**

Queries $\mathbf{q}$: river $(1,0)$, bank $(1,1)$, loan $(1,1)$.
Keys $\mathbf{k}$: river $(1,0)$, bank $(0,1)$, loan $(1,1)$.
Values $\mathbf{v}$: river $(1,1)$, bank $(2,0)$, loan $(0,2)$.

**Raw scores $QK^\top$** (each cell is $\mathbf{q}_{\text{row}} \cdot \mathbf{k}_{\text{col}}$):

| $\mathbf{q} \downarrow$ / $\mathbf{k} \rightarrow$ | river | bank | loan |
|---|---|---|---|
| **river** | 1 | 0 | 1 |
| **bank** | 1 | 1 | 2 |
| **loan** | 1 | 1 | 2 |

**Scaled by $\sqrt{d_k} = \sqrt{2} \approx 1.414$:**

| | river | bank | loan |
|---|---|---|---|
| **river** | 0.71 | 0.00 | 0.71 |
| **bank** | 0.71 | 0.71 | 1.41 |
| **loan** | 0.71 | 0.71 | 1.41 |

**Softmax, row by row** (each row sums to 1 — that is what makes it a distribution over "where do I look"):

| | river | bank | loan | → new vector |
|---|---|---|---|---|
| **river** | 0.40 | 0.20 | 0.40 | $(0.80,\; 1.20)$ |
| **bank** | 0.25 | 0.25 | 0.50 | $(0.74,\; 1.26)$ |
| **loan** | 0.25 | 0.25 | 0.50 | $(0.74,\; 1.26)$ |

Check the "river" row against Exercise 1: $e^{0.71} = 2.03$, $e^{0} = 1.00$, $e^{0.71} = 2.03$, sum $= 5.06$, so weights $2.03/5.06 = 0.40$, $1.00/5.06 = 0.20$, $0.40$. Then $0.40(1,1) + 0.20(2,0) + 0.40(0,2) = (0.80, 1.20)$.

**Three things this matrix shows that a single row cannot.**

1. **The matrix is not symmetric.** Row "river" gives "bank" a weight of 0.20, but row "bank" gives "river" 0.25. Attention is *directional* — "what does A want from B" is a different question from "what does B want from A" — because queries and keys are different projections. This is the single most common misconception about attention.

2. **"bank" and "loan" have identical rows.** They started with identical query vectors $(1,1)$, so they attend identically and end up with the same output. Nothing in this toy distinguishes them — which is exactly why real models use *many* attention heads with *different* learned projections, so that different heads can separate tokens this head cannot.

3. **Every row is $O(n)$ work and there are $n$ rows.** That is the $O(n^2)$ cost of self-attention, visible as the literal area of the table. Double the context length and the table quadruples. This is the whole economic argument for retrieval instead of just pasting more text into the prompt.



## 3. Exercises

1. **Second token by hand.** Repeat Model 1 for the token "river." Which neighbor does it attend to most, and does the answer match your linguistic intuition?

   *What to do:* Use $\mathbf{q}_{\text{river}} = (1, 0)$ as the query. Compute the dot product of $(1, 0)$ against $\mathbf{k}_{\text{river}} = (1,0)$, $\mathbf{k}_{\text{bank}} = (0,1)$, and $\mathbf{k}_{\text{loan}} = (1,1)$. Scale by $\sqrt{2}$, apply softmax, then form the weighted sum of the three value vectors.

   *Starter hint:* Raw scores for "river": $\mathbf{q}_{\text{river}} \cdot \mathbf{k}_{\text{river}} = 1\times1+0\times0=1$; $\mathbf{q}_{\text{river}} \cdot \mathbf{k}_{\text{bank}} = 1\times0+0\times1=0$; $\mathbf{q}_{\text{river}} \cdot \mathbf{k}_{\text{loan}} = 1\times1+0\times1=1$. Scale and softmax those three values, then blend the value vectors with the resulting weights.

   *You've succeeded when:* You can state which token "river" attends to most (or tie between which two), report the numeric attention weights, and give a one-sentence linguistic justification for whether the result makes sense.

2. **Mask experiment.** In the code cell, zero out (set to $-\infty$ before softmax) the score from "bank" to "loan," simulating a causal mask where "loan" is in the future. Report how the new representation changes.

   *What to do:* Modify the code cell so that after computing `scores`, you set `scores[2] = -np.inf` (index 2 is "loan"). Re-run `softmax` and the weighted sum. Print and compare the new representation to the unmasked version.

   *Starter hint:* In softmax, $e^{-\infty} = 0$, so a masked token receives exactly zero attention weight. The remaining weights will re-normalize over "river" and "bank" only. Mathematically, the masked two-token softmax uses only scores $[0.71, 0.71]$, which are equal, giving weights $[0.50, 0.50]$; the new bank vector is then $0.50 \times (1,1) + 0.50 \times (2,0) = (1.50, 0.50)$.

   *You've succeeded when:* You can report the exact new representation $(1.50, 0.50)$ (or close, accounting for rounding), explain why it differs from $(0.75, 1.25)$, and state in one sentence what causal masking prevents a model from doing during generation.

3. **Scaling sketch.** Tabulate $n^2$ for $n \in \{1\text{k}, 4\text{k}, 32\text{k}, 128\text{k}\}$ tokens, and use the table to argue, in three sentences, why retrieval (fetching only relevant text) beats ever-longer contexts for an agent searching a large document base.

   *What to do:* Fill in a four-row table with columns $n$ and $n^2$. Express $n^2$ in millions or billions for readability (e.g., 1 k tokens → $10^6$ pairs). Then write three sentences connecting the numbers to the retrieval argument.

   *Starter hint:* $1\text{k}^2 = 1{,}000{,}000$; $4\text{k}^2 = 16{,}000{,}000$; $32\text{k}^2 = 1{,}024{,}000{,}000$; $128\text{k}^2 = 16{,}384{,}000{,}000$. The ratio between consecutive rows is 16× each time you double twice. Retrieval lets you reduce $n$ to only the relevant chunk before the model ever sees it.

   *You've succeeded when:* Your table has four correct rows, your three sentences quantify (not just mention) the growth, and they explain why even a 128 k-token context window does not replace a good retrieval strategy for large document bases.

4. **Head hypothesis.** Real models use many attention heads in parallel. Propose two different relations (for example, syntax vs. coreference) that separate heads might specialize in, and design a sentence that would distinguish them.

   *What to do:* Choose two linguistic relationships (e.g., subject–verb agreement; pronoun–antecedent coreference; modifier–noun attachment; temporal ordering). For each, describe what pattern an attention head specializing in that relationship would show — which tokens would have high attention weights to which. Then write a single English sentence where the two patterns point to *different* pairs of tokens.

   *Starter hint:* In a sentence like "The tall woman who won the race finished first," subject–verb agreement links "woman" ↔ "finished," while coreference links "who" ↔ "woman." A head tracking agreement would show "finished" attending strongly to "woman"; a head tracking coreference would show "who" attending strongly to "woman." Design a sentence where those two target tokens are as far apart as possible to make the distinction clear.

   *You've succeeded when:* You have named two distinct linguistic relations, described the expected attention pattern for each, and provided a sentence where the two patterns visibly diverge (different source–target token pairs).

---

## Reflection Prompt

In your notebook, reflect at three levels after computing attention by hand:

**Personal.** Has your intuition about "the AI reads my prompt" changed? Write two or three sentences contrasting how you imagined the process before with the weighted-average reality you now understand. What surprised you most about the arithmetic?

**Technical.** Think about the two-head analogy from Exercise 4. If a model runs eight attention heads in parallel — each potentially specializing in a different linguistic relation — and stacks this 96 layers deep (as in a large production model), how does that change your estimate of what the model "knows" vs. what it "computes"? Write two or three sentences.

**Societal.** The "lost in the middle" effect means that, in a long prompt, evidence buried in the center may be underweighted regardless of its relevance. Describe one real-world scenario (legal document review, medical record summarization, or another domain you care about) where this bias could lead to a consequential error. Who would be harmed, and what design practice could mitigate it?

---

→ **Coming Up Next:** The next session turns to sampling — how the model converts the scores this machinery produces into an actual choice of next token. If you want the rest of the stack now (positional encodings, feed-forward sublayers, layer normalization, and end-to-end training with next-token prediction), it is worked end to end by hand in the [Anatomy of an LLM](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmanatomy.md) reference. We will also revisit the agent architecture from the *Memory and the Small Context Window Principle* activity and quantify, using today's $O(n^2)$ insight, why retrieval-augmented generation (RAG) is not optional for production agents working over large corpora.

---

## 4. Further Reading

- [Attention notebook](/files/notebooks/Attention.ipynb) — a runnable companion that computes dot-product attention by hand on a sentence with an ambiguous word, mirroring today's worked example.
- Vaswani et al. "Attention Is All You Need." *NeurIPS* (2017). The transformer paper.
- Tom Yeh. *AI by Hand*, attention worksheets (today's models follow this style).
- Jay Alammar. "The Illustrated Transformer" (online).
- Liu et al. "Lost in the Middle: How Language Models Use Long Contexts." *TACL* (2024).
