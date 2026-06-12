# Attention and Transformers, Conceptually and by Hand
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

Yesterday's embeddings give each token a meaning vector; today's **attention** lets every token *update* its meaning by looking at its neighbors, which is how "bank" near "river" differs from "bank" near "loan." We work **use-inspired**: enough mechanism to reason about agent behavior, computed once **by hand** in the AI by Hand tradition, then verified in NumPy. The arc is **the disambiguation problem $\rightarrow$ queries, keys, values $\rightarrow$ a worked 3-token example $\rightarrow$ what this explains about context windows**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Idea of Attention

## 1. Context Changes Meaning

**Static embeddings are not enough.** The token "bank" deserves different vectors in "river bank" and "bank loan," yet a lookup table gives it one. Attention solves this by letting each token form a new representation as a **weighted average of all tokens' values**, with weights determined by relevance.

**Queries, keys, and values.** Each token's embedding $\mathbf{x}_i$ is projected into three roles: a **query** $\mathbf{q}_i$ (what am I looking for?), a **key** $\mathbf{k}_i$ (what do I offer?), and a **value** $\mathbf{v}_i$ (what content do I contribute?). Relevance of token $j$ to token $i$ is the dot product $\mathbf{q}_i \cdot \mathbf{k}_j$, normalized across all $j$ by softmax:

$$
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right) V
$$

The $\sqrt{d_k}$ keeps dot products from growing with dimension and saturating the softmax. A **transformer** stacks this operation (in parallel "heads," interleaved with small neural networks) dozens of times; **causal masking** during generation prevents tokens from attending to the future.

---

## Model 1: Attention by Hand

Use a 2-dimensional toy with three tokens, with these (already-projected) vectors:

| token | $\mathbf{q}$ | $\mathbf{k}$ | $\mathbf{v}$ |
|-------|------|------|------|
| river | (1, 0) | (1, 0) | (1, 1) |
| bank  | (1, 1) | (0, 1) | (2, 0) |
| loan  | (0, 1) | (1, 1) | (0, 2) |

Compute the new representation of **bank** ($d_k = 2$, so divide scores by $\sqrt{2} \approx 1.41$).

### Critical Thinking Questions

1. Compute the three raw scores $\mathbf{q}_{\text{bank}} \cdot \mathbf{k}_j$ for $j \in \{\text{river}, \text{bank}, \text{loan}\}$. The Recorder shows each dot product.
2. Divide by $\sqrt{2}$ and apply softmax (calculator permitted; two decimal places suffice). Which token receives the most attention from "bank"?
3. Form the weighted sum of the value vectors. Compare the result with $\mathbf{v}_{\text{bank}}$ alone: in what direction did context pull the meaning of "bank"?
4. Suppose the sentence were "bank loan" without "river." Recompute the weights over just two tokens. Does "bank" now lean differently? This is contextualization in action.

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

# Part II: What Attention Explains About Agents

## 2. Consequences You Have Already Met

**The context window is the attention span, literally.** Attention compares every token with every other, costing $O(n^2)$ in sequence length $n$; doubling context quadruples this work. This is why context windows are finite, why long contexts are slow on your laptop, and why the *small context window principle* we adopt for agents in week 6 is not merely aesthetic but computational.

**Position matters.** Models attend most reliably to the beginning and end of long contexts (the "lost in the middle" effect), which is why we will place an agent's instructions and the current question at the edges of the prompt, with retrieved evidence in between.

[[MC]]
An agent's prompt grows from 2,000 to 8,000 tokens. The attention computation per layer grows by approximately a factor of:
- ( ) 2
- ( ) 4
- (x) 16
- ( ) It does not grow; attention is constant-time

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Second token by hand.* Repeat Model 1 for the token "river." Which neighbor does it attend to most, and does the answer match your linguistic intuition?
2. *Mask experiment.* In the code cell, zero out (set to $-\infty$ before softmax) the score from "bank" to "loan," simulating a causal mask where "loan" is in the future. Report how the new representation changes.
3. *Scaling sketch.* Tabulate $n^2$ for $n \in \{1\text{k}, 4\text{k}, 32\text{k}, 128\text{k}\}$ tokens, and use the table to argue, in three sentences, why retrieval (fetching only relevant text) beats ever-longer contexts for an agent searching a large document base.
4. *Head hypothesis.* Real models use many attention heads in parallel. Propose two different relations (for example, syntax vs. coreference) that separate heads might specialize in, and design a sentence that would distinguish them.

---

## Reflection Prompt

In your notebook: having computed attention by hand, has your mental model of "the AI reads my prompt" changed? Write two or three sentences contrasting how you imagined it before with the weighted-average reality.

---

## 4. Further Reading

- Vaswani et al. "Attention Is All You Need." *NeurIPS* (2017). The transformer paper.
- Tom Yeh. *AI by Hand*, attention worksheets (today's models follow this style).
- Jay Alammar. "The Illustrated Transformer" (online).
- Liu et al. "Lost in the Middle: How Language Models Use Long Contexts." *TACL* (2024).
