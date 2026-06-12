# RAG Quality: Chunking, Clustering, and Reranking
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-ragquality.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ragquality.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# RAG Quality: Chunking, Clustering, and Reranking

Yesterday's RAG pipeline worked because our "documents" were single tidy sentences; real documents are messy, and **how you cut them up determines what you can find**. This module develops the engineering of retrieval quality: **chunking strategies $\rightarrow$ measuring retrieval $\rightarrow$ semantic clustering of a corpus $\rightarrow$ reranking**, the same levers you will tune in Lab 2.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Chunking

## 1. The Goldilocks Problem

**Chunks too large** dilute the embedding (one vector must summarize many topics) and waste precious context window. **Chunks too small** orphan their meaning ("He approved the request" retrieves nothing useful without knowing who *he* is). Practical systems balance three strategies: **fixed-size** chunks of $n$ tokens with overlap $o$ (simple, structure-blind), **structural** chunks split on headings and paragraphs (respects authorship), and **semantic** chunks split where embedding similarity between consecutive sentences drops (respects topic shifts).

Overlap repairs boundary damage: with chunk size 200 and overlap 50, a fact straddling a boundary appears intact in at least one chunk. The cost is index size inflation by a factor of roughly $\frac{n}{n - o}$.

---

## Model 1: Cut This Document

Consider a 12-page student handbook with sections on housing, dining, conduct, and parking, where the parking rules paragraph begins with "Exceptions to the above:".

### Critical Thinking Questions

1. A fixed 500-token chunker splits mid-sentence between "the above" rules and the exceptions. Describe the wrong answer a RAG system would confidently give about parking, and which chunking strategy prevents it.
2. Structural chunking yields one enormous "conduct" chunk. What goes wrong at *embedding* time, and what goes wrong at *prompt assembly* time?
3. Propose a hybrid policy for the handbook (one sentence per rule), and have the Recorder write it as if it were documentation for Lab 2.

---

# Part II: Measuring and Improving Retrieval

## 2. Retrieval Metrics

Generation quality cannot exceed retrieval quality, so we measure retrieval directly. For a question set with labeled relevant chunks, **recall@k** asks how often the right chunk appears in the top $k$:

$$
\text{recall@}k = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}\left[\text{relevant}_i \cap \text{top-}k_i \neq \emptyset\right]
$$

A two-stage design retrieves generously then filters precisely: a fast vector search proposes, say, 20 candidates (high recall), and a **reranker**, a slower model scoring each query-chunk pair directly, reorders them so the truly relevant rise into the top 3 that fit the prompt (high precision). Even an LLM with the prompt "Rate the relevance of this passage to this question from 0 to 10" makes a serviceable reranker, our first taste of models evaluating text for other models.

[[MC]]
A system has recall@20 of 0.95 but recall@3 of 0.50, and the prompt only fits 3 chunks. The highest-leverage fix is:
- ( ) A larger generation model
- ( ) Smaller chunks with more overlap
- (x) A reranking stage between retrieval and prompt assembly
- ( ) Raising the temperature of the generator

---

## 3. Seeing Your Corpus: Semantic Clustering

Embeddings let us *map* a document collection before querying it. Clustering chunk vectors (k-means on normalized embeddings approximates clustering by cosine) reveals the topics your corpus actually contains, exposes duplicates, and flags off-topic contamination.

---

## Code Cell

```python
import numpy as np
import requests
from sklearn.cluster import KMeans

np.random.seed(42)

def embed(text):
    try:
        r = requests.post("http://localhost:11434/api/embeddings",
                          json={"model": "nomic-embed-text", "prompt": text}, timeout=120)
        return np.array(r.json()["embedding"])
    except Exception as e:
        print(f"[ragquality:embed] {e}")
        import traceback; traceback.print_exc()
        return np.zeros(768)

chunks = [
    "First-year students may not park on campus without a waiver.",
    "Visitor parking is available in Lot A for up to two hours.",
    "Parking permits renew each August through the portal.",
    "The dining hall offers vegan stations at lunch and dinner.",
    "Meal swipes reset on Sunday at midnight.",
    "Guest meal passes can be purchased at the Wismer desk.",
    "Quiet hours in residence halls begin at 10pm on weeknights.",
    "Room selection for returning students occurs in March.",
]

X = np.array([embed(c) for c in chunks])
X = X / np.linalg.norm(X, axis=1, keepdims=True)   # normalize so k-means ~ cosine

km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X)
for label in sorted(set(km.labels_)):
    print(f"--- cluster {label} ---")
    for c, l in zip(chunks, km.labels_):
        if l == label:
            print("  ", c)
```

---

## Model 2: Reading the Map

### Critical Thinking Questions

4. Did the clusters recover the human topics (parking, dining, housing)? Identify any chunk the algorithm placed surprisingly, and hypothesize what feature of its wording caused it.
5. Why must we normalize the vectors before k-means if we intend cosine geometry? (Hint: what does k-means minimize?)
6. Describe two concrete uses of this cluster map when curating the knowledge base for Lab 2: one for finding *gaps*, one for finding *duplicates*.

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Chunking shootout.* Take one real page of a campus document. Index it three ways (fixed 100 tokens, fixed 300 with overlap 75, paragraph-structural). For five questions, report which indexing wins recall@2, and explain the winner.
2. *Build a reranker.* Wrap your local model in a relevance-scoring prompt, rerank 10 retrieved candidates for three questions, and report rank changes of the truly relevant chunk.
3. *Recall curve.* For your Lab 2 corpus draft, plot recall@k for $k \in \{1, 2, 3, 5, 10\}$, and choose the $k$ you will ship, defending the choice in two sentences that mention both context budget and accuracy.

---

## Reflection Prompt

In your notebook: chunking is an editorial act, since someone decides where meaning begins and ends. When you index a document written by someone else, what obligations do you have to preserve its meaning, and how would you check whether your pipeline honored them?

---

## 5. Further Reading

- Chroma documentation on collections and querying: https://docs.trychroma.com
- Nils Reimers. "Retrieve and Re-Rank" (Sentence-Transformers documentation, online).
- Liu et al. "Lost in the Middle." *TACL* (2024), on why chunk *placement* in the prompt also matters.
