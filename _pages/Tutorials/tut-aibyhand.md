---
layout: default-standard
permalink: /Tutorials/AIByHand
title: 'CS357: Foundations of Artificial Intelligence - AI by Hand: Tokens, Cosine, Attention, Softmax, and a Forward Pass'
info:
  coursenum: CS357
  purpose: "To do every core computation of a language model on paper, one step per line, and then confirm each result in Python."
tags:
- ai-by-hand
- fundamentals
- softmax
- embeddings
- attention
---

{% include mathjax.html %}

# CS357: Foundations of Artificial Intelligence - AI by Hand: Tokens, Cosine, Attention, Softmax, and a Forward Pass

## Purpose

To do every core computation of a language model on paper, one step per line, and then confirm each result in Python.

## About This Tutorial

Every model you use this semester does five things with numbers: it cuts text into tokens, it compares vectors with a dot product, it mixes vectors with attention, it turns scores into probabilities with softmax, and it pushes inputs through weights in a forward pass.  Each of those is arithmetic you can do on paper in a few minutes.  This article collects every by-hand model from the course in one place, works each one with every intermediate step written out, and gives you a short Python snippet to check your answer.  The concept articles at [Tokens, Embeddings, and Attention]({{ site.baseurl }}/Tutorials/TokensEmbeddingsAttention) and [Sampling and Temperature]({{ site.baseurl }}/Tutorials/SamplingAndTemperature) explain why these computations matter; this one is where you do them.

Work each part with a pencil and a calculator before you read the answers.  A result you did not commit to on paper is not a prediction, and the moment your paper disagrees with the machine is the most useful moment on this page: find which step drifted.  If you want a printable version of the forward-pass practice, the [Neural Network by Hand worksheet (PDF)]({{ site.baseurl }}/files/activity-neuralnets/nn_by_hand_quadratic_full.pdf) extends Part 5 to a full network with a training pass.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|:-----|:------------------------|:------------------------|
| **Token** | The smallest chunk of text a model reads, roughly three quarters of an English word on average.  Common words are one token; rare words shatter into pieces. | `the` + `th` + `ing` for "the thing" under the toy merge rules in Part 1 |
| **Byte-pair encoding (BPE)** | The algorithm that builds a tokenizer: start with single characters and repeatedly merge the most frequent adjacent pair until the vocabulary is full. | Learning the merge `es` + `t` -> `est` from a four-word corpus in Part 1 |
| **Embedding** | A list of numbers (a vector) that represents the meaning of a piece of text, so that similar meanings land near each other. | "the dog ran" -> $$(1, 2, 2)$$ in a toy three-dimensional space in Part 2 |
| **Cosine similarity** | The cosine of the angle between two vectors: 1 means the same direction, 0 means unrelated, -1 means opposite.  It ignores length. | $$\cos(\mathbf{a}, \mathbf{b}) = 1.000$$ when $$\mathbf{b}$$ is a scaled copy of $$\mathbf{a}$$ in Part 2 |
| **Attention** | The mechanism that lets each token's vector be adjusted by the tokens around it: a dot product for relevance, a softmax for weights, and a weighted sum of values. | The vector for "bank" moving toward "loan" in Part 3 |
| **Query, key, value** | The three roles each token plays in attention: what it is looking for, what it offers as a match, and what content it contributes if chosen. | The three columns of the toy table in Part 3 |
| **Logit** | A raw, unbounded score the model assigns to each candidate token before softmax. | Paris $$z = 5$$, Lyon $$z = 2$$, banana $$z = -1$$ in Part 4 |
| **Softmax** | The function that turns a list of logits into probabilities that sum to 1 by exponentiating each score and dividing by the total. | $$e^{5} / (e^{5} + e^{2} + e^{-1}) \approx 0.950$$ in Part 4 |
| **Temperature** | A number that divides every logit before softmax.  Below 1 it sharpens the distribution; above 1 it flattens it. | $$P(\text{Paris})$$ moving from 0.998 at $$T = 0.5$$ to 0.786 at $$T = 2$$ in Part 4 |
| **ReLU** | The Rectified Linear Unit, $$\text{ReLU}(z) = \max(0, z)$$: positive values pass through, negatives become zero. | Hidden neuron $$h_2$$ computing $$-0.5$$ and outputting $$0$$ in Part 5 |
| **Forward pass** | One complete flow of numbers from inputs, through every layer's weights and activations, to the output. | Input $$(1.0, 1.0)$$ flowing to output $$2.0$$ in Part 5 |

---

## Part 1: Tokenize by Hand

A tokenizer cuts text into pieces from a fixed vocabulary by applying a list of merge rules, in order, to a string of characters.

> **Why this matters:** The model never sees the letter "e" inside "cheeseburger"; it sees whatever token the tokenizer carved out.  That is why models struggle to count letters, why long numbers trip them up, and why your context budget is measured in tokens rather than words.

### Worked Example: "the thing" with four merge rules

You are given four merge rules, to be applied in this order: `t`+`h` -> `th`, `th`+`e` -> `the`, `i`+`n` -> `in`, `in`+`g` -> `ing`.  Tokenize the phrase "the thing".  The toy rules say nothing about spaces, so treat the space as a boundary that no merge crosses.

1.  Start with every character as its own token: `t h e` and `t h i n g`.
2.  Apply `t`+`h` -> `th` everywhere it fits: `th e` and `th i n g`.
3.  Apply `th`+`e` -> `the`: `the` and `th i n g`.
4.  Apply `i`+`n` -> `in`: `the` and `th in g`.
5.  Apply `in`+`g` -> `ing`: `the` and `th ing`.
6.  No rule merges `th` with `ing`, so stop.

The result is three tokens: `the`, `th`, `ing`.  The common word "the" became one token and the less common word "thing" stayed in two pieces, because the merge table happened to contain `the` but not `thing`.

Recap: a tokenizer is a fixed list of merges applied left to right, and the output depends only on which merges the list contains.  Words the list knows well become single tokens; everything else is spelled out in fragments.

### Worked Example: where the merge rules come from (BPE)

Real tokenizers learn their merge rules with byte-pair encoding (BPE), and the learning rule is: repeatedly merge the most frequent adjacent pair.  Here is the whole algorithm on a four-word corpus, with `</w>` marking the end of a word.

```
low </w>      5
lower </w>    2
newest </w>   6
widest </w>   3
```

1.  Start from characters: `l o w </w>` (5), `l o w e r </w>` (2), `n e w e s t </w>` (6), `w i d e s t </w>` (3).
2.  Count every adjacent pair, weighted by word frequency.  `e s` occurs in newest (6) and widest (3) for a count of 9; `s t` also scores 9; `l o` and `o w` score 7; `w e` scores 6.
3.  `e s` and `s t` tie at 9.  Break the tie by the order encountered and merge `e s` -> `es`.  The corpus becomes `n e w es t </w>` and `w i d es t </w>` (the first two words are unchanged).
4.  Recount.  `es t` now occurs 9 times, the new maximum.  Merge `es t` -> `est`.
5.  Recount.  `est </w>` occurs 9 times.  Merge `est </w>` -> `est</w>`.

Three merges in, the learned merge table is `[es, est, est</w>]`.  Nobody supplied a rule that `est` is an English suffix; frequency discovered it.

### Worked Example: encoding a word the tokenizer has never seen

Take the learned merge table above, in order, and encode `lowest`, a word that never appeared in the training corpus.

| Stage | Sequence | Rule applied |
|---|---|---|
| start | `l o w e s t </w>` | split to characters |
| after merge 1 | `l o w es t </w>` | `e s` -> `es` |
| after merge 2 | `l o w est </w>` | `es t` -> `est` |
| after merge 3 | `l o w est</w>` | `est </w>` -> `est</w>` |
| final | `l` `o` `w` `est</w>` | no more rules apply |

Four tokens for a word the model has never seen: a prefix spelled out letter by letter plus a suffix it knows well.  Now ask a model how many `r`s are in *strawberry*.  A production tokenizer splits it into something like `str` `aw` `berry`, and not one of those pieces is a letter.  The model is looking at three opaque IDs, not at `s-t-r-a-w-b-e-r-r-y`.  Counting letters inside a token is an input representation failure, not a reasoning failure: the information was destroyed before the model saw it.  The same mechanism explains why models are shaky at rhyming, at reversing strings, and at arithmetic on long numbers.

Recap: BPE learns merges from frequency alone, and it encodes unseen words by applying those merges in order until none fit.  Whatever the tokenizer cannot merge, the model sees as separate fragments, and whatever it does merge, the model cannot see inside.

### Check it against a real tokenizer

> **Runs on your machine, not here.**  This cell needs the `tiktoken` library, which is installed in your course container rather than in the page.  Copy it there and run it.

```python
# pip install tiktoken
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")

for word in ["lowest", "strawberry", "Collegeville", "CS357", "internationalization"]:
    ids = enc.encode(word)
    pieces = [enc.decode([i]) for i in ids]
    print(f"{word:22s} -> {len(ids)} tokens  {pieces}")
```

Compare the output against your hand trace.  Two things to notice: common words are single tokens while rare ones shatter, and the split points frequently land mid-morpheme, because the tokenizer optimizes for frequency, not for meaning.

### Questions to Work Through

1.  Apply the four toy merges to "the thing" step by step.  How many tokens result, and which ones?

2.  Why do frequent character pairs deserve dedicated tokens?  Connect your answer to compression.

3.  Predict which costs more tokens: "internationalization" or "the cat sat on the mat".  Justify your prediction before you run the tiktoken cell.

### Answers

1.  Three tokens: `the`, `th`, `ing`.  The merge sequence is `t h e t h i n g` -> `th e th i n g` -> `the th i n g` -> `the th in g` -> `the th ing`.  No rule joins `th` and `ing`, so "thing" stays split.

2.  If "th" appears in thousands of words, storing it as one token instead of two halves the token count for every one of those occurrences.  A merge table is a compression codebook, the same idea as a ZIP file giving a short code to a byte string it sees often: spend one vocabulary slot on a frequent pair and save a token every time it appears.

3.  Expect the six-word sentence to cost more.  Each of its words is common, so each is one token, for about six in total.  The long rare word shatters, but into a handful of well-known pieces (`international` + `ization`, or similar), which is fewer than six.  Word count and character count are poor predictors of token count; frequency in the training corpus is what decides.  Run the tiktoken cell to see the exact split.

---

## Part 2: Cosine by Hand

Cosine similarity measures the angle between two vectors, so it reports direction (meaning) and ignores length.

> **Why this matters:** Once text is a vector, the model needs a way to say that "dog" and "puppy" are related while "dog" and "tax return" are not.  Cosine similarity is that measure, and it is the comparison every semantic search and every retrieval pipeline in this course runs.

An embedding maps a token, sentence, or document to a vector $$\mathbf{v} \in \mathbb{R}^d$$ (a list of $$d$$ numbers, with $$d$$ commonly 384 to 4096) such that semantically similar texts map to nearby vectors.  The standard similarity measure is the cosine of the angle between two vectors:

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert}
$$

The numerator is the dot product (multiply matching entries, then add).  Each norm in the denominator is the vector's length (square each entry, add, take the square root).  The result ranges from $$-1$$ (opposite direction) through $$0$$ (unrelated) to $$1$$ (identical direction).

### Worked Example: three sentences in a toy space

Let $$\mathbf{a} = (1, 2, 2)$$ stand for "the dog ran", $$\mathbf{b} = (2, 4, 4)$$ for "a dog was running", and $$\mathbf{c} = (2, -1, 0)$$ for "quarterly tax filing".

Compute $$\cos(\mathbf{a}, \mathbf{b})$$:

1.  Dot product: $$\mathbf{a} \cdot \mathbf{b} = (1)(2) + (2)(4) + (2)(4) = 2 + 8 + 8 = 18$$.
2.  Norm of $$\mathbf{a}$$: $$\lVert \mathbf{a} \rVert = \sqrt{1^2 + 2^2 + 2^2} = \sqrt{1 + 4 + 4} = \sqrt{9} = 3$$.
3.  Norm of $$\mathbf{b}$$: $$\lVert \mathbf{b} \rVert = \sqrt{2^2 + 4^2 + 4^2} = \sqrt{4 + 16 + 16} = \sqrt{36} = 6$$.
4.  Divide: $$\cos(\mathbf{a}, \mathbf{b}) = 18 / (3 \times 6) = 18 / 18 = 1.000$$.

Compute $$\cos(\mathbf{a}, \mathbf{c})$$:

1.  Dot product: $$\mathbf{a} \cdot \mathbf{c} = (1)(2) + (2)(-1) + (2)(0) = 2 - 2 + 0 = 0$$.
2.  Norm of $$\mathbf{c}$$: $$\lVert \mathbf{c} \rVert = \sqrt{2^2 + (-1)^2 + 0^2} = \sqrt{4 + 1 + 0} = \sqrt{5} \approx 2.236$$.
3.  Divide: $$\cos(\mathbf{a}, \mathbf{c}) = 0 / (3 \times 2.236) = 0.000$$.

The two dog sentences score a perfect 1.000 because $$\mathbf{b} = 2\mathbf{a}$$ points in exactly the same direction, and the tax sentence scores 0.000 because its vector is perpendicular to $$\mathbf{a}$$.

Recap: the dot product rewards vectors that point the same way, and dividing by both norms removes any credit for length.  Two vectors that differ only by a scale factor always score exactly 1.

### Worked Example: cosine similarity in four dimensions

This is Problem 2 from the *Prompt Patterns and AI by Hand* assignment, now worked in full.  Let $$\mathbf{a} = (2, 1, 0, 2)$$ and $$\mathbf{b} = (1, 1, 1, 1)$$.

1.  Dot product: $$\mathbf{a} \cdot \mathbf{b} = (2)(1) + (1)(1) + (0)(1) + (2)(1) = 2 + 1 + 0 + 2 = 5$$.
2.  Sum of squares for $$\mathbf{a}$$: $$2^2 + 1^2 + 0^2 + 2^2 = 4 + 1 + 0 + 4 = 9$$, so $$\lVert \mathbf{a} \rVert = \sqrt{9} = 3$$.
3.  Sum of squares for $$\mathbf{b}$$: $$1^2 + 1^2 + 1^2 + 1^2 = 4$$, so $$\lVert \mathbf{b} \rVert = \sqrt{4} = 2$$.
4.  Divide: $$\cos(\mathbf{a}, \mathbf{b}) = 5 / (3 \times 2) = 5 / 6 \approx 0.833$$.

Second calculation: compute $$\cos(\mathbf{a}, 3\mathbf{a})$$.

1.  Scale: $$3\mathbf{a} = (6, 3, 0, 6)$$.
2.  Dot product: $$\mathbf{a} \cdot 3\mathbf{a} = (2)(6) + (1)(3) + (0)(0) + (2)(6) = 12 + 3 + 0 + 12 = 27$$.
3.  Norm of $$3\mathbf{a}$$: $$\sqrt{36 + 9 + 0 + 36} = \sqrt{81} = 9$$.
4.  Divide: $$\cos(\mathbf{a}, 3\mathbf{a}) = 27 / (3 \times 9) = 27 / 27 = 1.000$$.

The result is exactly 1 for any scale factor $$s > 0$$, not only for 3: the numerator is $$\mathbf{a} \cdot s\mathbf{a} = s \lVert \mathbf{a} \rVert^2$$ and the denominator is $$\lVert \mathbf{a} \rVert \cdot s \lVert \mathbf{a} \rVert = s \lVert \mathbf{a} \rVert^2$$, so they cancel.  This is why a two-line query and a two-page document can still score high against each other: the embedding of a long document is not penalized for being "bigger", only for pointing a different way.

**Python verification:**

```python
import numpy as np

a = np.array([2.0, 1.0, 0.0, 2.0])
b = np.array([1.0, 1.0, 1.0, 1.0])

def cosine_sim(x, y):
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))

print(f"cos(a, b) = {cosine_sim(a, b):.3f}")
print(f"cos(a, 3a) = {cosine_sim(a, 3*a):.3f}")
```

Expected output:

```
cos(a, b) = 0.833
cos(a, 3a) = 1.000
```

Recap: every cosine computation is the same four lines (dot product, two norms, divide), and the only place to make an error is arithmetic.  If your paper says anything other than 0.833 and 1.000, recheck the sum of squares first; it is the step most often miscopied.

> **Common Misconception:** A high cosine score does not mean the two sentences share the same words, that one logically implies the other, or that either is factually true.  It only means the embedding model placed them in a similar direction in meaning-space.  Two completely wrong sentences about the same topic can score 0.95 with each other.

### Questions to Work Through

1.  $$\mathbf{b} = 2\mathbf{a}$$ exactly.  What does cosine similarity say about vectors that differ only in magnitude, and why is that a desirable property when comparing a short query with a long document?

2.  Two sentences receive embeddings with cosine similarity 0.92.  Which is the best interpretation?

    - The sentences share at least 92 percent of their words
    - The embedding model places them in nearly the same direction, suggesting closely related meaning
    - One sentence logically entails the other
    - Both sentences are factually true

3.  $$\cos(\mathbf{a}, \mathbf{c})$$ came out exactly 0.  What does a score of 0 mean geometrically, and is it the same as "opposite meaning"?

### Answers

1.  Cosine similarity reports 1.000 for any two vectors that point the same way, regardless of length, because the division by both norms cancels every scale factor.  A short question like "parking rules?" and a long parking policy document can have the same meaning and very different lengths; cosine lets them match on direction without penalizing the document for being long.

2.  The embedding model places them in nearly the same direction, suggesting closely related meaning.  Cosine says nothing about shared words, logical entailment, or truth.

3.  A score of 0 means the vectors are perpendicular: the dot product is zero, so neither has any component along the other's direction.  That is "unrelated", not "opposite".  Opposite meaning corresponds to a score near $$-1$$, where the vectors point in reverse directions.

---

## Part 3: Attention by Hand

Attention rebuilds each token's vector as a weighted average of every token's value vector, where the weights come from a softmax over dot products.

> **Why this matters:** A lookup table gives "bank" one vector, which is wrong at least half the time ("the bank was steep" versus "the bank approved the loan").  Attention lets the surrounding words move a token's meaning, and it is the single idea that separates the models you use this semester from the word-vector methods that came before them.

Each token gets three vectors instead of one, playing three roles: a query $$\mathbf{q}$$ (what am I looking for?), a key $$\mathbf{k}$$ (what do I offer as a match?), and a value $$\mathbf{v}$$ (what content do I contribute if I am chosen?).  Think of a library search: your search term is the query, the index cards are the keys, and the books are the values.  The analogy stops there, because in attention every book contributes a share, weighted by how well its card matched.  To find how relevant token $$j$$ is to token $$i$$, take the dot product $$\mathbf{q}_i \cdot \mathbf{k}_j$$ (the same operation as the numerator of cosine similarity in Part 2).  Run those relevance scores through softmax so they become weights that sum to 1, then build the token's new vector as a weighted blend of everyone's values.  Written compactly:

$$
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right) V
$$

Here $$Q$$, $$K$$, and $$V$$ stack every token's query, key, and value into matrices, and $$\sqrt{d_k}$$ (the square root of the vector length) divides the scores to keep them from growing large enough to saturate the softmax.  A transformer stacks this operation dozens of times, in parallel "heads", with small neural networks in between.  You are about to do one layer of it by hand.

### Worked Example: the new vector for "bank" in "river bank loan"

Three tokens, two dimensions, all arithmetic visible.  The vectors below are already projected into their three roles.

| token | $$\mathbf{q}$$ | $$\mathbf{k}$$ | $$\mathbf{v}$$ |
|-------|------|------|------|
| river | (1, 0) | (1, 0) | (1, 1) |
| bank  | (1, 1) | (0, 1) | (2, 0) |
| loan  | (0, 1) | (1, 1) | (0, 2) |

Compute the new representation of **bank**, using $$\mathbf{q}_{\text{bank}} = (1, 1)$$ and $$d_k = 2$$, so $$\sqrt{d_k} \approx 1.41$$.

Step 1, relevance: dot the query against every key.

1.  Against river, $$\mathbf{k} = (1, 0)$$: $$1 \times 1 + 1 \times 0 = 1$$.
2.  Against bank, $$\mathbf{k} = (0, 1)$$: $$1 \times 0 + 1 \times 1 = 1$$.
3.  Against loan, $$\mathbf{k} = (1, 1)$$: $$1 \times 1 + 1 \times 1 = 2$$.

Raw scores $$[1, 1, 2]$$.  "loan" is already the most relevant, and so far you have only multiplied and added.

Step 2, scale: divide each score by $$\sqrt{2} \approx 1.41$$.

1.  $$1 / 1.41 \approx 0.71$$
2.  $$1 / 1.41 \approx 0.71$$
3.  $$2 / 1.41 \approx 1.41$$

Scaled scores $$[0.71, 0.71, 1.41]$$.

Step 3, softmax: raise $$e \approx 2.718$$ to each score, then divide each by the total.

1.  $$e^{0.71} \approx 2.03$$
2.  $$e^{0.71} \approx 2.03$$
3.  $$e^{1.41} \approx 4.10$$
4.  Total: $$2.03 + 2.03 + 4.10 = 8.16$$
5.  Weights: $$2.03 / 8.16 \approx 0.25$$, $$2.03 / 8.16 \approx 0.25$$, $$4.10 / 8.16 \approx 0.50$$

"bank" gives half its attention to "loan" and a quarter each to "river" and to itself.

Step 4, blend the values with those weights.

$$
\text{new\_bank} = 0.25(1, 1) + 0.25(2, 0) + 0.50(0, 2) = (0.25, 0.25) + (0.50, 0) + (0, 1.00) = (0.75,\; 1.25)
$$

Read the result.  Without context, `bank` was $$(2, 0)$$: all first dimension, no second.  After one layer of attention it is $$(0.75, 1.25)$$: the second dimension, contributed almost entirely by `loan`, now dominates.  Context moved the meaning, and it moved it by arithmetic you did on paper.

Recap: attention is four steps, dot product, scale, softmax, weighted sum, and none of them is more than multiplication and addition plus one exponential.  The weights decide how much each neighbor contributes, and the values decide what it contributes.

### Demo: Check Your Arithmetic Against the Machine

Before you run this, write down your three raw scores, your three softmax weights, and your new `bank` vector.  Then hold the machine to your numbers.

```python
import numpy as np

q = {"river": np.array([1., 0.]), "bank": np.array([1., 1.]), "loan": np.array([0., 1.])}
k = {"river": np.array([1., 0.]), "bank": np.array([0., 1.]), "loan": np.array([1., 1.])}
v = {"river": np.array([1., 1.]), "bank": np.array([2., 0.]), "loan": np.array([0., 2.])}
tokens = ["river", "bank", "loan"]

def softmax(z):
    e = np.exp(z - z.max())          # subtract the max for numerical stability
    return e / e.sum()

scores  = np.array([q["bank"] @ k[t] for t in tokens]) / np.sqrt(2)
weights = softmax(scores)
new_bank = sum(w * v[t] for w, t in zip(weights, tokens))

print("raw/scaled scores :", np.round(scores, 3))
print("softmax weights   :", np.round(weights, 3))
print("new bank vector   :", np.round(new_bank, 3))
```

Expected output:

```
raw/scaled scores : [0.707 0.707 1.414]
softmax weights   : [0.248 0.248 0.503]
new bank vector   : [0.745 1.255]
```

Your paper and the output agree to two decimal places.  The small gap between 0.25 and 0.248, or between 0.75 and 0.745, comes from rounding $$\sqrt{2}$$ to 1.41 on paper; the machine carries more digits.  If your numbers are off by more than that, find which of the four steps drifted.

### Try It Yourself

1.  **Delete a word.**  Remove `"river"` from `tokens` and run again.  The softmax now normalizes over two tokens instead of three.  Predict the direction the new `bank` vector moves before you run it, then check.  You've succeeded when you can say in one sentence why dropping an unrelated word still changed `bank`, and what that implies about padding a prompt with filler.

2.  **Change the query.**  Compute the new representation of `river` instead of `bank`, by swapping `q["bank"]` for `q["river"]` in the `scores` line.  Which token does `river` lean on, and does that match your intuition about the sentence?  You've succeeded when you can point at the specific dot product that made the difference.

3.  **Break the scaling.**  Delete the `/ np.sqrt(2)` and run again.  Now multiply every vector by 10 and run both versions.  Watch what the unscaled softmax does to the weights.  You've succeeded when you can explain what $$\sqrt{d_k}$$ is protecting against, using the numbers you saw rather than the formula.

> **Common Misconception:** "Attention means the model is focusing the way a person does."  The name is a metaphor for a weighted average, nothing more.  Every token attends to every other token every time, with a weight; none is ignored, and none is being concentrated on.  What you computed above is the entire phenomenon: dot products, a softmax, and a weighted sum.

### Questions to Work Through

1.  Redo Steps 1 through 3 for the sentence "bank loan", with `river` removed entirely.  There are now two softmax inputs instead of three, so the weights must sum to 1 over two tokens.  Does "bank" lean differently?

2.  In Step 1, `bank`'s query scored 1 against its own key, the same score it gave `river`.  Why is it useful for a token to attend to itself at all, rather than only to its neighbors?

3.  Both cosine similarity (Part 2) and attention's relevance score start with a dot product.  Name the one thing cosine does that attention's score does not, and suggest why attention might not want it.

4.  Every token computes a score against every other token, so $$n$$ tokens cost $$n^2$$ scores.  If you grow a prompt from 2,000 tokens to 8,000, by what factor does the attention work grow?

5.  In the worked example, which quantity decided how much `bank` was influenced by `loan`?

    - The value vector $$\mathbf{v}_{\text{loan}} = (0, 2)$$
    - The softmax weight 0.50, computed from the dot product of `bank`'s query with `loan`'s key
    - The order of the tokens in the sentence
    - The dimension $$d_k = 2$$

### Answers

1.  The raw scores are the same two numbers, 1 (against itself) and 2 (against loan); scaled, $$[0.71, 1.41]$$.  Exponentials: $$e^{0.71} \approx 2.03$$ and $$e^{1.41} \approx 4.10$$, total $$6.13$$.  Weights: $$2.03 / 6.13 \approx 0.33$$ and $$4.10 / 6.13 \approx 0.67$$.  New vector: $$0.33(2, 0) + 0.67(0, 2) = (0.66, 1.34)$$.  "bank" leans harder toward "loan" than before, because the quarter of the weight that went to `river` is now split between the two remaining tokens.  Dropping an unrelated word still changed the result, which is the sense in which filler in a prompt dilutes the tokens that matter.

2.  Self-attention keeps the token's own content in the blend.  Without it, the new vector for `bank` would be built entirely from its neighbors and would lose its own identity; a token with no relevant neighbor also needs somewhere to place its weight so that it does not get overwritten by noise.

3.  Cosine divides by the two norms; attention's score does not.  That division makes cosine ignore length.  Attention keeps length, so a token with a larger key can attract more attention: its "loudness" is a learned property the model can use.  The $$\sqrt{d_k}$$ scaling is a fixed constant applied to every score, not a per-token normalization, so it does not take that ability away.

4.  By a factor of 16, because $$8000^2 / 2000^2 = 64{,}000{,}000 / 4{,}000{,}000 = 16$$.  This is why long prompts are slow on your laptop and why context windows are finite.

5.  The softmax weight 0.50, computed from the dot product of `bank`'s query with `loan`'s key.  The value vector says what `loan` contributes; the weight says how much.

---

## Part 4: Softmax and Temperature by Hand

Softmax turns raw scores into probabilities that sum to 1, and temperature divides the scores first, which sharpens or flattens the result.

> **Why this matters:** A language model outputs a logit for every token in its vocabulary, then samples one token from the softmax of those logits, appends it, and repeats.  The randomness lives in the sampling step, not in the weights.  Temperature is the dial you turned in *Running Your Own AI*, and this is what it is.

Given the tokens so far, the model outputs a raw score (a logit, $$z_i$$) for every token $$i$$ in its vocabulary, then converts scores to probabilities with softmax at temperature $$T$$:

$$
P(i) = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}
$$

As $$T \to 0$$ the highest-scoring token dominates and sampling approaches greedy decoding (always the top token).  As $$T$$ grows, the distribution flattens and less likely tokens gain probability.  Temperature does not add knowledge; it redistributes confidence across the existing options.

### Worked Example: Paris, Lyon, banana

Suppose the logits for the next word after "The capital of France is" are Paris $$z = 5$$, Lyon $$z = 2$$, banana $$z = -1$$.  For each temperature, divide every logit by $$T$$, exponentiate, add the three results to get the denominator, then divide each exponential by that denominator.

At $$T = 1$$:

1.  Scaled logits: $$5 / 1 = 5$$, $$2 / 1 = 2$$, $$-1 / 1 = -1$$.
2.  Exponentials: $$e^{5} \approx 148.4132$$, $$e^{2} \approx 7.3891$$, $$e^{-1} \approx 0.3679$$.
3.  Sum: $$148.4132 + 7.3891 + 0.3679 = 156.1702$$.
4.  Probabilities: $$148.4132 / 156.1702 \approx 0.950$$, $$7.3891 / 156.1702 \approx 0.047$$, $$0.3679 / 156.1702 \approx 0.002$$.

At $$T = 0.5$$:

1.  Scaled logits: $$5 / 0.5 = 10$$, $$2 / 0.5 = 4$$, $$-1 / 0.5 = -2$$.
2.  Exponentials: $$e^{10} \approx 22026.4658$$, $$e^{4} \approx 54.5982$$, $$e^{-2} \approx 0.1353$$.
3.  Sum: $$22026.4658 + 54.5982 + 0.1353 = 22081.1993$$.
4.  Probabilities: $$22026.4658 / 22081.1993 \approx 0.998$$, $$54.5982 / 22081.1993 \approx 0.002$$, $$0.1353 / 22081.1993 \approx 0.000$$.

At $$T = 2$$:

1.  Scaled logits: $$5 / 2 = 2.5$$, $$2 / 2 = 1$$, $$-1 / 2 = -0.5$$.
2.  Exponentials: $$e^{2.5} \approx 12.1825$$, $$e^{1} \approx 2.7183$$, $$e^{-0.5} \approx 0.6065$$.
3.  Sum: $$12.1825 + 2.7183 + 0.6065 = 15.5073$$.
4.  Probabilities: $$12.1825 / 15.5073 \approx 0.786$$, $$2.7183 / 15.5073 \approx 0.175$$, $$0.6065 / 15.5073 \approx 0.039$$.

| Temperature | P(Paris) | P(Lyon) | P(banana) | Sum |
|---|---|---|---|---|
| T = 0.5 | 0.998 | 0.002 | 0.000 | 1.000 |
| T = 1.0 | 0.950 | 0.047 | 0.002 | 1.000 |
| T = 2.0 | 0.786 | 0.175 | 0.039 | 1.000 |

Recap: the logits never changed; only the divisor did.  Halving the temperature doubled every scaled logit, which widened the gaps between exponentials and pushed Paris toward certainty, while doubling it shrank the gaps and let banana climb from 0.2 percent to 3.9 percent.

### Worked Example: three tokens, three temperatures

This is Problem 1 from the *Prompt Patterns and AI by Hand* assignment, now worked in full.  Tokens A, B, and C have logits $$z = (4, 2, 1)$$.  Compute the full distribution at $$T = 0.5$$, $$T = 1$$, and $$T = 2$$.

At $$T = 0.5$$:

1.  Scaled logits: $$4 / 0.5 = 8$$, $$2 / 0.5 = 4$$, $$1 / 0.5 = 2$$.
2.  Exponentials: $$e^{8} \approx 2980.9580$$, $$e^{4} \approx 54.5982$$, $$e^{2} \approx 7.3891$$.
3.  Sum: $$2980.9580 + 54.5982 + 7.3891 = 3042.9453$$.
4.  Probabilities: $$2980.9580 / 3042.9453 \approx 0.980$$, $$54.5982 / 3042.9453 \approx 0.018$$, $$7.3891 / 3042.9453 \approx 0.002$$.

At $$T = 1$$:

1.  Scaled logits: $$4$$, $$2$$, $$1$$ (unchanged).
2.  Exponentials: $$e^{4} \approx 54.5982$$, $$e^{2} \approx 7.3891$$, $$e^{1} \approx 2.7183$$.
3.  Sum: $$54.5982 + 7.3891 + 2.7183 = 64.7056$$.
4.  Probabilities: $$54.5982 / 64.7056 \approx 0.844$$, $$7.3891 / 64.7056 \approx 0.114$$, $$2.7183 / 64.7056 \approx 0.042$$.

At $$T = 2$$:

1.  Scaled logits: $$4 / 2 = 2$$, $$2 / 2 = 1$$, $$1 / 2 = 0.5$$.
2.  Exponentials: $$e^{2} \approx 7.3891$$, $$e^{1} \approx 2.7183$$, $$e^{0.5} \approx 1.6487$$.
3.  Sum: $$7.3891 + 2.7183 + 1.6487 = 11.7561$$.
4.  Probabilities: $$7.3891 / 11.7561 \approx 0.629$$, $$2.7183 / 11.7561 \approx 0.231$$, $$1.6487 / 11.7561 \approx 0.140$$.

| Temperature | P(A) | P(B) | P(C) | Sum |
|---|---|---|---|---|
| T = 0.5 | 0.980 | 0.018 | 0.002 | 1.000 |
| T = 1.0 | 0.844 | 0.114 | 0.042 | 1.000 |
| T = 2.0 | 0.629 | 0.231 | 0.140 | 1.000 |

What the numbers demonstrate: as temperature decreases toward zero, the probability of the highest-logit token climbs toward 1 and the others toward 0, because dividing by a small $$T$$ stretches the gaps between logits and the exponential turns a larger gap into a much larger ratio.  As temperature increases, the same gaps shrink and the distribution flattens toward uniform.

**Python verification:**

```python
import numpy as np

logits = np.array([4.0, 2.0, 1.0])

for T in [0.5, 1.0, 2.0]:
    scaled = logits / T
    exp_scaled = np.exp(scaled)
    probs = exp_scaled / exp_scaled.sum()
    print(f"T={T}: {probs.round(3)}")
```

Expected output:

```
T=0.5: [0.98  0.018 0.002]
T=1.0: [0.844 0.114 0.042]
T=2.0: [0.629 0.231 0.14 ]
```

Recap: each row is the same three operations, divide, exponentiate, normalize, and each row sums to 1.000.  If a row of yours does not sum to 1, the denominator was copied wrong; if a row sums to 1 but the values differ, an exponential was.

### Softmax and Temperature, Revisited Visually

The same math scales to more tokens, and a sweep across temperatures makes the shape of the change visible.  To summarize each distribution with one number, compute its entropy:

$$
H = -\sum_i P(i) \log P(i)
$$

High entropy means the distribution is flat and the model is uncertain.  Low entropy means the distribution is peaked and the model is confident.

Before you run the sweep below, sketch on paper what you expect to happen to the probability of `Paris` and to the entropy as temperature climbs from 0.1 to 2.0.  Draw the shape of the curve, not only the direction.  Then run it and check your sketch against the table.

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

Expected output:

```
    T     Paris      Lyon    London    banana   croissant   entropy
------------------------------------------------------------------------
  0.1    1.0000    0.0000    0.0000    0.0000     0.0000    0.0000
  0.5    0.9872    0.0081    0.0045    0.0002     0.0000    0.0783
  1.0    0.8477    0.0769    0.0570    0.0127     0.0057    0.5856
  1.5    0.6832    0.1379    0.1129    0.0415     0.0244    1.0025
  2.0    0.5666    0.1707    0.1469    0.0694     0.0465    1.2332
```

Notice the line `exp_vals = [math.exp(l - max_l) ...]`.  Subtracting the largest scaled logit before exponentiating does not change the probabilities (the factor $$e^{-\max}$$ appears in both numerator and denominator and cancels), but it keeps $$e^{45}$$ from overflowing at $$T = 0.1$$.  The attention demo in Part 3 does the same thing.

Recap: temperature reshapes one fixed set of logits, and entropy rises monotonically with it.  At $$T = 0.1$$ the model is effectively greedy; at $$T = 2.0$$ nearly half of the probability mass has left `Paris`.

### Questions to Work Through

1.  At $$T = 0.1$$, Paris has probability 1.000.  At $$T = 2.0$$, Paris has probability 0.567.  The logits did not change between runs; only $$T$$ changed.  Walk through the exponent step for Paris and banana at $$T = 0.1$$ and at $$T = 2.0$$ to show the mechanism.

2.  As temperature increases from 0.1 to 2.0, entropy:

    - Decreases, because the distribution becomes more random
    - Increases, because a flatter distribution is harder to predict
    - Stays the same, because the logits are fixed
    - Increases then decreases after a peak at $$T = 1.0$$

3.  Top-p (nucleus) sampling keeps the smallest set of tokens whose cumulative probability reaches $$p$$, then renormalizes.  Using the sweep table, work out how many tokens top-p = 0.90 keeps at $$T = 1.0$$ and at $$T = 2.0$$.  Why does the same threshold require more tokens at higher temperature?

4.  A classmate claims: "I should always use top-p instead of top-k because top-p adapts to the model's confidence."  Give one situation where top-k might be preferable, and explain why.

5.  An agent inside a loop must output exactly `calc(...)` or `Final Answer:`.  Using the Paris table, argue for the temperature you would set for an agent's reasoning step, and identify what could still go wrong even at $$T = 0$$.

### Answers

1.  At $$T = 0.1$$, Paris's scaled logit is $$4.5 / 0.1 = 45$$ and banana's is $$0.3 / 0.1 = 3$$, a gap of 42; $$e^{42}$$ is astronomically larger than $$e^{3}$$, so banana's share rounds to zero.  At $$T = 2.0$$, Paris becomes $$4.5 / 2 = 2.25$$ and banana $$0.3 / 2 = 0.15$$, a gap of 2.1; $$e^{2.1} \approx 8.2$$, so Paris is only about eight times as likely as banana.  Temperature changes the gaps, and the exponential turns gaps into ratios.

2.  Increases, because a flatter distribution is harder to predict.  The table confirms it: entropy climbs from 0.0000 to 1.2332 with no peak.

3.  At $$T = 1.0$$, Paris alone is 0.8477, below 0.90, so top-p adds Lyon for a cumulative 0.9246 and keeps two tokens.  At $$T = 2.0$$, Paris is 0.5666, plus Lyon is 0.7373, plus London is 0.8842, plus banana is 0.9536, so it keeps four tokens.  The threshold is on cumulative probability, not on a count.  A flatter distribution spreads mass across more tokens, so more of them are needed to reach the same total.

4.  Top-k is preferable when you want a fixed budget regardless of the model's confidence: for example, generating a field that must be one of five predefined options, where you want at most five candidates whether the distribution is flat or peaked.  Top-p might admit three tokens on one step and thirty on the next.

5.  Set $$T$$ near 0 (greedy decoding) for the reasoning step, because at $$T = 0.5$$ the top token already has 0.998 of the probability and at $$T = 0$$ it has all of it, so the parser sees the same string every run.  What can still go wrong: greedy guarantees consistency, not correctness.  If the model's top-scoring continuation is a malformed tool call, $$T = 0$$ produces that same malformed call every time.

---

## Part 5: A Forward Pass by Numbers

A forward pass multiplies inputs by weights, adds a bias, applies ReLU, and repeats the same pattern at the next layer until an output falls out.

> **Why this matters:** Every agent you build rides on a forward pass: numbers multiplied by weights, summed, squashed, repeated.  If you can trace one by hand, "the model computed logits" stops being a phrase and becomes arithmetic you can audit.  The [From Text Generation to a Neural Network]({{ site.baseurl }}/Tutorials/TextGenToNN) article places this network inside the generation loop; this part is where you compute it.

### Worked Example: a 2-2-1 network on two inputs

This is Problem 3 from the *Prompt Patterns and AI by Hand* assignment, now worked in full.  A tiny network has 2 inputs, 2 hidden ReLU neurons, and 1 linear output:

$$
h_1 = \text{ReLU}(2.0\,x_1 - 1.0\,x_2 - 0.5) \qquad h_2 = \text{ReLU}(-1.0\,x_1 + 1.0\,x_2 - 0.5)
$$

$$
y = 2.0\,h_1 + 1.0\,h_2 + 1.0
$$

where $$\text{ReLU}(z) = \max(0, z)$$.  Read each hidden equation as: multiply each input by its weight, add the products, add the bias, then clip at zero.

Trace for $$\mathbf{x} = (1.0, 1.0)$$:

| Step | Computation | Result |
|:-----|:------------|:-------|
| $$h_1$$ pre-activation | $$2.0(1.0) + (-1.0)(1.0) + (-0.5) = 2.0 - 1.0 - 0.5$$ | $$0.5$$ |
| $$h_1$$ activation | $$\text{ReLU}(0.5) = \max(0, 0.5)$$ | $$0.5$$ |
| $$h_2$$ pre-activation | $$(-1.0)(1.0) + 1.0(1.0) + (-0.5) = -1.0 + 1.0 - 0.5$$ | $$-0.5$$ |
| $$h_2$$ activation | $$\text{ReLU}(-0.5) = \max(0, -0.5)$$, clipped to zero | $$0.0$$ |
| output $$y$$ | $$2.0(0.5) + 1.0(0.0) + 1.0 = 1.0 + 0.0 + 1.0$$ | $$2.0$$ |

Neuron $$h_1$$ is active and $$h_2$$ is clipped.

Trace for $$\mathbf{x} = (0.0, 2.0)$$:

| Step | Computation | Result |
|:-----|:------------|:-------|
| $$h_1$$ pre-activation | $$2.0(0.0) + (-1.0)(2.0) + (-0.5) = 0.0 - 2.0 - 0.5$$ | $$-2.5$$ |
| $$h_1$$ activation | $$\text{ReLU}(-2.5) = \max(0, -2.5)$$, clipped to zero | $$0.0$$ |
| $$h_2$$ pre-activation | $$(-1.0)(0.0) + 1.0(2.0) + (-0.5) = 0.0 + 2.0 - 0.5$$ | $$1.5$$ |
| $$h_2$$ activation | $$\text{ReLU}(1.5) = \max(0, 1.5)$$ | $$1.5$$ |
| output $$y$$ | $$2.0(0.0) + 1.0(1.5) + 1.0 = 0.0 + 1.5 + 1.0$$ | $$2.5$$ |

Now $$h_2$$ is active and $$h_1$$ is clipped.  The active-neuron pattern flipped between the two inputs, which demonstrates that a ReLU network is piecewise linear: each input selects which neurons are switched on, and the switched-on set determines which linear formula the output follows.

**Python verification:**

```python
W1 = [[2.0, -1.0], [-1.0, 1.0]]
b1 = [-0.5, -0.5]
V, c = [2.0, 1.0], 1.0

def forward(x):
    pre = [W1[j][0]*x[0] + W1[j][1]*x[1] + b1[j] for j in range(2)]
    h = [max(0.0, p) for p in pre]
    y = V[0]*h[0] + V[1]*h[1] + c
    print(f"x={x}  pre={pre}  h={h}  y={y}")

forward([1.0, 1.0])
forward([0.0, 2.0])
```

Expected output:

```
x=[1.0, 1.0]  pre=[0.5, -0.5]  h=[0.5, 0.0]  y=2.0
x=[0.0, 2.0]  pre=[-2.5, 1.5]  h=[0.0, 1.5]  y=2.5
```

Each row of `W1` holds one hidden neuron's two input weights, `b1` holds the two hidden biases, `V` holds the output weights, and `c` is the output bias.  The `pre` list is the pre-activation column of your trace table and `h` is the activation column.

Recap: a forward pass is a trace table, and every cell is a multiply, an add, or a $$\max$$.  The only decision the network makes is which neurons the input switches on, and the biases decide where those switches sit.

### Questions to Work Through

1.  Trace the network for $$\mathbf{x} = (0.0, 0.0)$$.  What does the result tell you about the role of the biases?

2.  Find an input for which both hidden neurons are active, and compute $$y$$ for it.

3.  In the generation loop (tokenize, embed, run the network, produce logits, softmax, sample), between which two stages does this forward pass live, and which stages from Parts 1 and 4 sit on either side of it?

### Answers

1.  With zero inputs every weight term vanishes, leaving only biases: $$h_1 = \text{ReLU}(-0.5) = 0$$, $$h_2 = \text{ReLU}(-0.5) = 0$$, and $$y = 2.0(0) + 1.0(0) + 1.0 = 1.0$$.  The output is the output bias alone.  Without biases, every neuron's decision boundary would pass through the origin and the network could not represent a function like $$y = x_1 + 5$$.

2.  $$h_1$$ needs $$2x_1 - x_2 > 0.5$$ and $$h_2$$ needs $$-x_1 + x_2 > 0.5$$.  The input $$\mathbf{x} = (2.0, 3.0)$$ satisfies both: $$h_1$$ pre-activation $$4.0 - 3.0 - 0.5 = 0.5$$, so $$h_1 = 0.5$$; $$h_2$$ pre-activation $$-2.0 + 3.0 - 0.5 = 0.5$$, so $$h_2 = 0.5$$; $$y = 2.0(0.5) + 1.0(0.5) + 1.0 = 2.0$$.  Any input in the wedge where both inequalities hold works.

3.  The forward pass sits between the embedding lookup and the logits.  Tokenization (Part 1) and the embedding lookup feed it; its output is the vector of logits that softmax with temperature (Part 4) turns into probabilities.  Attention (Part 3) is one of the layers inside it.

---

## Exercises

1.  **Encode two words with the learned merge table.**

   *What to do:* Using the merge table `[es, est, est</w>]` from Part 1, encode `slowest` and `widest`, showing the sequence after each merge as in the `lowest` table.

   *You've succeeded when:* `slowest` ends as five tokens (`s` `l` `o` `w` `est</w>`) and `widest` ends as four (`w` `i` `d` `est</w>`), and you can say why the prefix of each word is spelled letter by letter while the suffix is one token.

2.  **Cosine on a new pair.**

   *What to do:* Compute $$\cos(\mathbf{u}, \mathbf{w})$$ for $$\mathbf{u} = (3, 4)$$ and $$\mathbf{w} = (4, 3)$$ by hand, showing the dot product, both norms, and the ratio.  Then verify it with the `cosine_sim` function from Part 2.

   *You've succeeded when:* Your paper says $$24 / (5 \times 5) = 0.960$$ and Python prints `0.960`.

3.  **Softmax and a shift.**

   *What to do:* Compute the softmax of logits $$(3, 1, 0)$$ at $$T = 1$$ and at $$T = 0.5$$, one step per line, then compare your table to the $$(4, 2, 1)$$ table in Part 4.

   *You've succeeded when:* Both of your rows match the Part 4 rows exactly, and you can explain in one sentence why subtracting the same constant from every logit leaves the probabilities unchanged (the same fact that lets the sweep code subtract `max_l`).

4.  **Attention for a different token.**

   *What to do:* Using the table in Part 3, compute the new representation of `loan` (query $$(0, 1)$$) with all four steps shown, then confirm it by changing the query in the demo code.

   *You've succeeded when:* Your scaled scores are $$[0, 0.71, 0.71]$$, your weights are about $$[0.20, 0.40, 0.40]$$, and the new vector is $$(1.00, 1.00)$$ to two decimals.

5.  **The printable worksheet.**

   *What to do:* Print the [Neural Network by Hand worksheet (PDF)]({{ site.baseurl }}/files/activity-neuralnets/nn_by_hand_quadratic_full.pdf) and work its forward pass and training step on paper.  Then adapt the `forward` function from Part 5 to check every value.

   *You've succeeded when:* Every number on your worksheet matches the code to two decimal places, and you can name the one step in the worksheet that Part 5 does not include.

---

## Reflection Prompt

**Personal level:** Which of the five computations surprised you most when you did it on paper: that a tokenizer is only a list of merges, that attention is a weighted average, that temperature is a division, or that a forward pass is a trace table?  What did you believe the model was doing before?

**Technical level:** Every computation on this page runs on fixed numbers.  Name the one place in the whole generation loop where randomness enters, and explain why setting temperature to 0 there does not make the model correct, only consistent.

**Societal level:** The vectors in Part 2 were invented for the example.  Real embeddings are learned from human-written text, including that text's biases.  If a resume-screening system ranks applicants by cosine similarity to current high performers, which of the four lines of the cosine computation is where historical bias enters, and what safeguard would you design?

---

## Further Reading

- [Neural Network by Hand worksheet (PDF)]({{ site.baseurl }}/files/activity-neuralnets/nn_by_hand_quadratic_full.pdf), the printable forward-pass and training-step worksheet that extends Part 5.
- Tom Yeh.  *AI by Hand*, Volume 1: https://www.scribd.com/document/726922630/AI-by-Hand-Vol-1.  Softmax, embedding, dot-product, and attention worksheets in the same style as this article.
- [Tokens, Embeddings, and Attention]({{ site.baseurl }}/Tutorials/TokensEmbeddingsAttention), the companion concept article for Parts 1 through 3.
- [Sampling and Temperature]({{ site.baseurl }}/Tutorials/SamplingAndTemperature), the companion concept article for Part 4.
- [From Text Generation to a Neural Network]({{ site.baseurl }}/Tutorials/TextGenToNN), which places the Part 5 network inside the generation loop.
- [Sentence Prediction with BERT notebook](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/notebooks/Sentence_Prediction_with_BERT.ipynb), a runnable companion that shows contextual embeddings in action.
- Jay Alammar.  "The Illustrated Word2Vec" (online).  A visual introduction to embedding geometry.
- Reimers and Gurevych.  "Sentence-BERT." *EMNLP* (2019).  How sentence-level embeddings are trained.
- Ari Holtzman et al.  "The Curious Case of Neural Text Degeneration."  *ICLR* (2020).  The paper that introduced nucleus sampling.
