# Tokens and Embeddings: How Agents Represent Meaning
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-tokensembeddings.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-tokensembeddings.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tokens and Embeddings: How Agents Represent Meaning

We open the hood for the first time, on demand: our agents will soon need to *search* documents by meaning, and that requires understanding **tokens** (how text becomes numbers) and **embeddings** (how meaning becomes geometry). We move from **tokenization $\rightarrow$ vectors $\rightarrow$ cosine similarity $\rightarrow$ computing semantic search by hand and in code**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: From Characters to Tokens

## 1. Tokenization

**Models do not read words; they read tokens.** A tokenizer splits text into subword units drawn from a fixed vocabulary, typically built by byte-pair encoding (BPE): begin with characters, repeatedly merge the most frequent adjacent pair, and stop at a target vocabulary size (often 30,000 to 200,000 entries). Common words become single tokens; rare words shatter into pieces, so "unhappiness" may become `un` + `happiness` and "Collegeville" may become three fragments.

**Tokenization explains odd model behaviors.** Counting letters in a word is hard when the model never sees letters; arithmetic on long numbers is hard when digits group unpredictably; and the *context window* is measured in tokens, which is why a 4,000-token budget holds roughly 3,000 English words.

---

## Model 1: Tokenize by Hand

Given the toy merge rules (`t`+`h`$\to$`th`, `th`+`e`$\to$`the`, `i`+`n`$\to$`in`, `in`+`g`$\to$`ing`), tokenize: "the thing".

### Critical Thinking Questions

1. Apply the merges step by step. How many tokens result? The Recorder shows the merge sequence.
2. Why do frequent character pairs deserve dedicated tokens? Connect your answer to compression.
3. Predict which is more tokens: "internationalization" or "the cat sat on the mat". Justify before checking intuition against the class.

---

## 2. Embeddings: Meaning as Geometry

**An embedding maps a token, sentence, or document to a vector** $\mathbf{v} \in \mathbb{R}^d$ (with $d$ commonly 384 to 4096) such that *semantically similar texts map to nearby vectors*. The standard similarity measure is **cosine similarity**, the cosine of the angle between vectors:

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert}
$$

which ranges from $-1$ (opposite) through $0$ (unrelated) to $1$ (identical direction). Embedding models are trained so that paraphrases score high and unrelated texts score low; this single idea powers semantic search, clustering, recommendation, and the retrieval pipelines our agents will use next week.

---

## Model 2: Cosine by Hand

Let $\mathbf{a} = (1, 2, 2)$ for "the dog ran" and $\mathbf{b} = (2, 4, 4)$ for "a dog was running", and $\mathbf{c} = (2, -1, 0)$ for "quarterly tax filing."

### Critical Thinking Questions

4. Compute $\cos(\mathbf{a}, \mathbf{b})$ and $\cos(\mathbf{a}, \mathbf{c})$ by hand (AI by Hand style: show the dot products and norms). The Recorder writes the full arithmetic.
5. $\mathbf{b} = 2\mathbf{a}$ exactly. What does cosine similarity say about vectors that differ only in magnitude, and why is that a desirable property for comparing a short query with a long document?

[[MC]]
Two sentences receive embeddings with cosine similarity 0.92. The best interpretation is:
- ( ) The sentences share at least 92 percent of their words
- (x) The embedding model places them in nearly the same direction, suggesting closely related meaning
- ( ) One sentence logically entails the other
- ( ) Both sentences are factually true

---

# Part II: Semantic Search in Code

## 3. A Search Engine in Twenty Lines

Ollama serves embedding models too. We embed a handful of campus FAQ sentences and search them by meaning, not keywords.

---

## Code Cell

```python
import requests
import numpy as np

np.random.seed(42)

def embed(text, model="nomic-embed-text"):
    try:
        r = requests.post("http://localhost:11434/api/embeddings",
                          json={"model": model, "prompt": text}, timeout=120)
        return np.array(r.json()["embedding"])
    except Exception as e:
        print(f"[embeddings:embed] {e}")
        import traceback; traceback.print_exc()
        return np.zeros(768)

docs = [
    "The library is open until midnight on weekdays.",
    "Students may park in Lot G with a valid permit.",
    "The dining hall serves brunch on Saturdays and Sundays.",
    "Office hours for CS357 are Tuesday and Thursday mornings.",
    "Intramural soccer registration closes Friday.",
]

D = np.array([embed(d) for d in docs])

def search(query, k=2):
    q = embed(query)
    sims = D @ q / (np.linalg.norm(D, axis=1) * np.linalg.norm(q))
    for i in np.argsort(-sims)[:k]:
        print(f"{sims[i]:.3f}  {docs[i]}")

search("when can I get help from my professor")
print()
search("where do I leave my car")
```

---

## Model 3: Probing the Geometry

### Critical Thinking Questions

6. Neither query shares a single content word with its best match. Identify exactly which line of code performed the "understanding," and what it computes mathematically.
7. Craft a query that retrieves the *wrong* document with high confidence. What does the failure reveal about what embeddings capture and what they miss (negation, numbers, names)?
8. The matrix-vector product `D @ q` computes all similarities at once. For one million documents, what becomes expensive, and what data structure might help? (This previews vector databases.)

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Similarity matrix.* Embed eight sentences of your team's choosing spanning two obvious topics. Compute the full 8x8 cosine matrix, render it as a heatmap, and verify that the block structure matches the topics.
2. *Analogy probe.* Test the classic claim that embedding arithmetic captures analogy: compare $\cos(\text{embed}(\text{"king"}) - \text{embed}(\text{"man"}) + \text{embed}(\text{"woman"}),\ \text{embed}(\text{"queen"}))$ against unrelated words. Report whether your sentence-level model exhibits the effect, and hypothesize why or why not.
3. *Token budget audit.* Estimate the token count of your team charter document at four characters per token, then explain how that figure constrains stuffing it into an agent's prompt every turn. (We address this properly in the memory module.)

---

## Reflection Prompt

In your notebook: meaning, for an embedding model, is location in a high-dimensional space learned from co-occurrence. Name one aspect of meaning in *your* favorite discipline (a poem's irony, a proof's elegance, a primary source's provenance) that you suspect geometry cannot capture, and say why.

---

## 5. Further Reading

- Tom Yeh. *AI by Hand*, embedding and dot-product worksheets.
- Jay Alammar. "The Illustrated Word2Vec" (online). A visual introduction to embedding geometry.
- Reimers and Gurevych. "Sentence-BERT." *EMNLP* (2019). How sentence-level embeddings are trained.
