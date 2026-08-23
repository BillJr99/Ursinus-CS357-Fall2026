<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-ragquality.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-ragquality.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# RAG Quality: Chunking, Clustering, and Reranking

The RAG pipeline from the *Retrieval-Augmented Generation with Chroma* activity worked because our "documents" were single tidy sentences; real documents are messy, and **how you cut them up determines what you can find**. This module develops the engineering of retrieval quality: **chunking strategies $\rightarrow$ measuring retrieval $\rightarrow$ semantic clustering of a corpus $\rightarrow$ reranking**, the same levers you will tune in the RAG Knowledge Base Lab.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Chunk** | A piece of a document that gets its own embedding and its own slot in the vector database. The art is choosing the right size: too big and the embedding blurs across topics; too small and the chunk loses its context. | A 200-token excerpt from the student handbook parking section |
| **Fixed-Size Chunking** | Splitting a document every N tokens regardless of sentence or paragraph boundaries. Simple and predictable, but can cut a sentence in half. | Splitting the handbook every 500 tokens, with 50-token overlap between adjacent chunks |
| **Overlap** | The number of tokens repeated between adjacent chunks to avoid losing information at chunk boundaries. A 50-token overlap means the last 50 tokens of chunk 1 are also the first 50 tokens of chunk 2. | With chunk size 200 and overlap 50, a fact straddling a boundary appears intact in at least one chunk |
| **Recall@k** | The fraction of questions for which the correct chunk appears somewhere in the top-k retrieved results. Measures whether your retrieval system finds the right content at all, before the model sees it. | recall@3 = 0.80 means 80% of questions had the right chunk somewhere in the top 3 results |
| **Reranker** | A second-stage model that takes the top-k retrieval candidates and re-scores them for relevance to the specific query. The first stage retrieves broadly (high recall); the reranker filters precisely (high precision). | A local model scoring each chunk 0-10 for relevance, then re-ordering the list |
| **Semantic Clustering** | Grouping document chunks by the similarity of their embeddings, revealing what topics your corpus actually contains without reading every chunk manually. | K-means on normalized embeddings groups parking, dining, and housing chunks into 3 clusters |

---

# Part I: Chunking

## 1. The Goldilocks Problem

In this Part you will explore why the size of text chunks matters enormously for retrieval quality, examine three splitting strategies, and develop a principled hybrid policy you can apply to your own documents in the RAG Knowledge Base Lab.

**Why this matters:** Imagine searching a book using only its table of contents (chapters as chunks) versus searching it word by word (sentences as chunks). The table of contents gives you chapters that might be 50 pages long; your embedding has to summarize 50 pages into one vector, which blurs the meaning across dozens of topics. Individual sentences are precise but often meaningless in isolation: "He approved the request" tells you nothing about *who*, *what*, or *why*. Good chunking finds the passage-length sweet spot that is semantically self-contained and focused enough to embed meaningfully. It is the most impactful tuning knob in any real RAG system.

**Chunks too large** dilute the embedding (one vector must summarize many topics) and waste precious context window space. **Chunks too small** orphan their meaning ("He approved the request" retrieves nothing useful without knowing who *he* is). Practical systems balance three strategies:

| Strategy | How It Works | Best For | Trade-Off |
|----------|-------------|----------|-----------|
| **Fixed-size** | Split every N tokens, with overlap O tokens repeated between adjacent chunks (e.g., chunks of 200 tokens with 50-token overlap) | Simple documents where you want predictable chunk counts and easy tuning | Ignores sentence and paragraph structure; can split a key sentence across two chunks even with overlap |
| **Structural** | Split on natural document boundaries (headings, paragraph breaks, bullet items) respecting how the author organized the content | Well-structured documents like policies, manuals, or textbooks with clear sections | One section might be 50 tokens and another 2,000 tokens, creating uneven retrieval quality |
| **Semantic** | Split where the embedding similarity between consecutive sentences drops sharply, detecting topic shifts algorithmically | Long documents with many topic shifts where structural markers are sparse | More complex to implement; requires embedding every sentence before chunking |

Overlap repairs boundary damage: with chunk size 200 and overlap 50, a fact straddling a boundary appears intact in at least one chunk. The cost is index size inflation by a factor of roughly $\frac{n}{n - o}$, so a 200-token chunk with 50-token overlap inflates the index by $\frac{200}{150} \approx 1.33$ times.

---

## Model 1: Cut This Document

Consider a 12-page student handbook with sections on housing, dining, conduct, and parking, where the parking rules paragraph begins with "Exceptions to the above:".

### Critical Thinking Questions

1. A fixed 500-token chunker splits mid-sentence between "the above" rules and the exceptions. Describe the wrong answer a RAG system would confidently give about parking, and which chunking strategy prevents it.

   > *Hint: The exception chunk starts with "Exceptions to the above:" but the "above" rules are in the previous chunk. If a student asks "Are there exceptions to the parking rule?", the system retrieves the exceptions chunk but the model cannot know what rule is being excepted. What answer might it fabricate? Which chunking strategy keeps the rule and its exceptions together?*

2. Structural chunking yields one enormous "conduct" chunk. What goes wrong at *embedding* time (when the vector is created), and what goes wrong at *prompt assembly* time (when the chunk is pasted into the prompt)?

   > *Hint: At embedding time: one vector has to represent 3,000 tokens covering academic honesty, social conduct, residence hall policies, and disciplinary procedures. What happens to the "meaning direction" of that vector? At prompt assembly: if this chunk is retrieved, how much of your 4,000-token context window does it consume?*

3. Propose a hybrid policy for the handbook (one sentence per rule), and have the Recorder write it as if it were documentation for the RAG Knowledge Base Lab.

   > *Hint: A hybrid policy might say: "Use structural splits on section headings first, then apply fixed-size chunking with 50-token overlap within any structural chunk larger than 400 tokens, with a minimum chunk size of 100 tokens." Write this as a numbered specification your lab partner could implement.*

---

# Part II: Measuring and Improving Retrieval

## 2. Retrieval Metrics

In this Part you will learn how to measure whether your retrieval system is actually working, understand the recall@k metric (the fraction of questions for which the right chunk appears in the top-k results), and see how a reranker can raise precision without sacrificing recall.

**Why this matters:** You cannot improve what you cannot measure. Before tuning chunk size, overlap, or any other parameter, you need a metric that tells you whether retrieval is actually working. Recall@k is that metric: for a set of test questions where you know the right answer, does the right chunk appear in the top k results? If recall@3 is 0.50, half your questions will get the wrong chunk and therefore a potentially hallucinated answer, regardless of how good your language model is. Generation quality has a ceiling imposed by retrieval quality, and this section gives you the tools to find and raise that ceiling.

For a question set with labeled relevant chunks, **recall@k** asks how often the right chunk appears in the top $k$ results:

$$
\text{recall@}k = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}\left[\text{relevant}_i \cap \text{top-}k_i \neq \emptyset\right]
$$

Read this as: for each of $N$ questions, check whether the relevant chunk appears anywhere in the top $k$ retrieved results (1 if yes, 0 if no), then average across all questions. A score of 1.0 means every question had its answer chunk in the top $k$; a score of 0.5 means half did.

A two-stage design retrieves generously then filters precisely: a fast vector search proposes, say, 20 candidates (achieving high recall; the right chunk is almost certainly in there), and a **reranker** (a slower model scoring each query-chunk pair directly) reorders them so the truly relevant chunk rises into the top 3 that actually fit the prompt (achieving high precision). Even an LLM prompted with "Rate the relevance of this passage to this question from 0 to 10" makes a serviceable reranker, our first taste of models evaluating text for other models.

A system has recall@20 of 0.95 but recall@3 of 0.50, and the prompt only fits 3 chunks. The highest-leverage fix is:

[( )] A larger generation model
[( )] Smaller chunks with more overlap
[(X)] A reranking stage between retrieval and prompt assembly
[( )] Raising the temperature of the generator

---

## 3. Seeing Your Corpus: Semantic Clustering

**Why this matters:** Before you build a RAG system over a large document collection, you need to understand what you have. How many distinct topics does your corpus cover? Are there entire subjects with no coverage? Are there many near-duplicate chunks that waste index space and confuse retrieval? Clustering the embeddings gives you an automatic map of your corpus's topic structure, the same way a heat map of a city shows you where neighborhoods cluster, without reading every street address.

Embeddings let us *map* a document collection before querying it. Clustering chunk vectors (k-means on normalized embeddings approximates clustering by cosine similarity) reveals the topics your corpus actually contains, exposes duplicates, and flags off-topic contamination.

---

The code below embeds eight campus-policy chunks using a local model, then runs k-means clustering (a method that groups items into k groups by finding the assignments that minimize total distance to each group's center) on the normalized embedding vectors. After running it, you will read the cluster output and judge whether the algorithm found the same topic structure a human would draw.

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


### Worked Example: one k-means iteration, by hand

The code cell above clusters your corpus and draws the map. Before you trust a map, it is worth knowing how it was drawn, and k-means is simple enough to do on paper. Here is one full iteration on four chunk embeddings, reduced to two dimensions so the arithmetic stays visible.

Four chunks, with their (toy, 2-D) embeddings:

| Chunk | Vector | Roughly about |
|---|---|---|
| A | $(1.0,\; 1.0)$ | course policies |
| B | $(1.5,\; 2.0)$ | grading policy |
| C | $(5.0,\; 4.0)$ | RAG implementation |
| D | $(6.0,\; 5.0)$ | vector databases |

**Step 1: initialize.** Pick $k = 2$ and seed the centroids at two of the points: $c_1 = (1,1)$, $c_2 = (6,5)$.

**Step 2: assign each point to its nearest centroid** (Euclidean distance):

| Chunk | $d$ to $c_1$ | $d$ to $c_2$ | Assigned |
|---|---|---|---|
| A | $0.00$ | $6.40$ | **cluster 1** |
| B | $\sqrt{0.5^2 + 1^2} = 1.12$ | $5.41$ | **cluster 1** |
| C | $\sqrt{4^2 + 3^2} = 5.00$ | $\sqrt{1^2+1^2} = 1.41$ | **cluster 2** |
| D | $6.40$ | $0.00$ | **cluster 2** |

**Step 3: recompute each centroid as the mean of its members:**

- $c_1 = \left(\frac{1.0 + 1.5}{2},\; \frac{1.0 + 2.0}{2}\right) = (1.25,\; 1.50)$
- $c_2 = \left(\frac{5.0 + 6.0}{2},\; \frac{4.0 + 5.0}{2}\right) = (5.50,\; 4.50)$

**Step 4: repeat.** Reassign with the new centroids: nothing changes, so the algorithm has **converged** after one iteration. Two clusters, and they correspond to something real (policy chunks and implementation chunks) which nobody labeled.

**What this tells you about your own corpus map.** Three things worth carrying into Model 2:

1. **The clusters are an artifact of $k$, not a fact about your documents.** We chose $k = 2$. Choose $k = 4$ on this data and you get four singleton clusters, each perfectly "coherent" and completely useless. When the map looks clean, ask whether $k$ made it clean.
2. **The seeds matter.** Had we seeded at B and C instead, the first assignment would differ, and on messier data the final clustering can differ too. This is why production implementations use k-means++ seeding and run several times.
3. **Distance here is Euclidean, but retrieval usually ranks by cosine.** On *normalized* vectors the two give the same ordering, which is exactly why the pipeline normalizes embeddings before clustering. If you ever cluster un-normalized vectors, long documents drift away from the origin and form their own cluster purely because they are long, not because they are about anything in particular.


## Model 2: Reading the Map

**Why this matters:** The clusters the algorithm produces may or may not match the categories a human would draw. When they do not match, the mismatch is a window into what the embedding model actually "hears" in the text, and that is valuable information for predicting where your retrieval system will succeed and where it will fail.

### Critical Thinking Questions

4. Did the clusters recover the human topics (parking, dining, housing)? Identify any chunk the algorithm placed surprisingly, and hypothesize what feature of its wording caused it.

   > *Hint: "Room selection for returning students occurs in March" is about housing. But does it share vocabulary with other housing chunks? What words might cause it to cluster with a different group? Look at overlapping words between the surprise chunk and the cluster it joined.*

5. Why must we normalize the vectors before k-means if we intend cosine geometry? Think about what k-means minimizes.

   > *Hint: K-means minimizes Euclidean distance (straight-line distance in space) to cluster centroids. Cosine similarity ignores vector length and only measures direction. If two vectors point in the same direction but one is 10 times longer, cosine similarity says they are identical (score 1.0), but Euclidean distance says they are far apart. Normalizing (setting all vectors to length 1) makes Euclidean distance proportional to cosine distance.*

6. Describe two concrete uses of this cluster map when curating the knowledge base for the RAG Knowledge Base Lab: one use for finding *gaps* in your corpus, and one for finding *duplicates*.

   > *Hint: For gaps: if your corpus has 3 clusters but your users' questions span 5 topics, what does that tell you? For duplicates: if one cluster contains 12 chunks and they all say nearly the same thing in slightly different words, what is the problem for retrieval and for prompt assembly?*

> **Common Misconception:** Many students assume that adding more documents always improves a RAG system. In practice, adding off-topic, contradictory, or near-duplicate documents hurts retrieval quality. A search engine that returns 20 near-identical parking regulations when you ask about dining hours is retrieving with high recall but low precision. Corpus *quality* and *coverage* matter more than corpus *size*, and clustering is one of the best tools for auditing both.

---

# Part III: Synthesis and Practice

With the theory of recall and reranking established, this hands-on section puts chunking strategies head-to-head on a real document so you can see the performance differences numerically rather than hypothetically.

## Hands-On: Chunking Strategy Comparison

The full 30-minute build (the sample document, three chunking functions, cosine retrieval, the five test questions, and the results table) now lives on the **[RAG Knowledge Base lab](https://www.billmongan.com/Ursinus-CS357/Assignments/RAGKnowledgeBase)**, which is handed out today and is where you run the comparison for credit.

Today we stay on the *judgment*: where a chunk boundary belongs, and what recall@k does and does not tell you.

## 4. Exercises

In this Part you apply everything from Parts I and II to real documents: run a chunking shootout on a campus policy page, build and test a reranker using your local model, plot a recall curve, and choose a retrieval configuration you can defend with numbers.

1. *Chunking shootout.* Take one real page of a campus document. Index it three ways (fixed 100 tokens no overlap, fixed 300 tokens with 75-token overlap, paragraph-structural). For five questions with known answers, report which indexing strategy wins recall@2, and explain the winner.

   - *What to do:* Choose a real campus policy page (parking, dining, honor code, etc.). Implement three versions of the chunker and create three separate Chroma collections. For 5 questions where you know which paragraph contains the answer, run all three and check whether the answer paragraph appears in the top 2 results.
   - *Starter hint:* For fixed chunking: `chunks = [text[i:i+n] for i in range(0, len(text), n-overlap)]`. For paragraph structural: `chunks = [p.strip() for p in text.split('\n\n') if p.strip()]`. Count recall@2 as: for each of 5 questions, 1 if the right chunk is in position 1 or 2, else 0. Divide by 5.
   - *You've succeeded when:* You have a table with 3 rows (one per chunking strategy) and 5 question columns (1 = retrieved, 0 = not), plus a recall@2 score for each strategy and a one-sentence explanation of why the winner worked best for this particular document.

2. *Build a reranker.* Wrap your local model in a relevance-scoring prompt, rerank 10 retrieved candidates for three questions, and report the rank change of the truly relevant chunk.

   - *What to do:* Retrieve the top 10 chunks for 3 questions using your Chroma collection. For each chunk, call the model with a prompt like: "On a scale of 0 to 10, how relevant is the following passage to the question '{question}'? Passage: '{chunk}'. Reply with only a number." Sort by score and report the new rank of the chunk you know is correct.
   - *Starter hint:* `def rerank_score(question, chunk): return int(chat(f"Rate relevance 0-10 of this passage to '{question}': '{chunk}'. Reply only with a number."))`. Call this for each of your 10 candidates, sort descending, and report where the correct chunk landed before and after reranking.
   - *You've succeeded when:* For at least 2 of 3 questions, the correct chunk's rank improves after reranking (e.g., moved from position 4 to position 1), and you can explain in one sentence why the initial vector search placed it lower.

3. *Recall curve.* For your RAG Knowledge Base Lab corpus draft, plot recall@k for $k \in \{1, 2, 3, 5, 10\}$, and choose the $k$ you will ship, defending the choice in two sentences that mention both context budget and accuracy.

   - *What to do:* Build a small evaluation set of 10 questions with labeled relevant chunks. Run your Chroma search with n_results=10 for each question. Compute recall@k for each k value by checking whether the correct chunk appears in the top k. Plot the resulting curve with `matplotlib`.
   - *Starter hint:* `recall_at_k = [sum(1 for q in eval_set if correct_chunk[q] in top_k_results[q][:k]) / len(eval_set) for k in [1,2,3,5,10]]`. Then `plt.plot([1,2,3,5,10], recall_at_k)`.
   - *You've succeeded when:* You have a plotted recall curve showing recall@k for k in {1,2,3,5,10}, and your written justification explicitly trades off "more chunks = higher recall but fewer prompt tokens remaining for the answer" against the accuracy you need for your application.

---

## Reflection Prompt

*Personal:* Think about a time someone summarized or quoted something you wrote or said, and the summary changed the meaning. How does that experience connect to what happens when a large chunk is embedded into a single vector?

*Technical:* In your notebook: chunking is an editorial act: someone (or some algorithm) decides where meaning begins and ends. When you index a document written by someone else, what obligations do you have to preserve its meaning, and how would you check whether your pipeline honored them?

*Societal:* A law firm deploys RAG over a corpus of 10,000 legal documents to help paralegals find relevant precedents. The chunking strategy splits some court opinions mid-sentence, occasionally separating the holding (the decision) from its reasoning. Who is harmed if the system retrieves the holding without the reasoning? What audit process would you require before deploying such a system?

---

## -> Coming Up Next

We now have a RAG system that can find and deliver relevant information. Next session, *How I AI*, turns that instinct on your own notes: a vault of plain files an agent can read, with the zone boundaries and contract that make it safe to let one write there. Its Part III is an open studio, so bring your pipeline-in-progress and your stuck points. The theory behind all of it, why an agent needs external memory at all, follows the session after in *Memory and the Small Context Window Principle*.

---

## 5. Further Reading

- Chroma documentation on collections and querying: https://docs.trychroma.com
- Nils Reimers. "Retrieve and Re-Rank" (Sentence-Transformers documentation, online).
- Liu et al. "Lost in the Middle." *TACL* (2024), on why chunk *placement* in the prompt also matters.
