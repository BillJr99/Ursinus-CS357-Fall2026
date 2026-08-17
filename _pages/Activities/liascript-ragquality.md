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

The RAG pipeline from the *Retrieval-Augmented Generation with Chroma* activity worked because our "documents" were single tidy sentences; real documents are messy, and **how you cut them up determines what you can find**. This module develops the engineering of retrieval quality: **chunking strategies $\rightarrow$ measuring retrieval $\rightarrow$ semantic clustering of a corpus $\rightarrow$ reranking** — the same levers you will tune in the RAG Knowledge Base Lab.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Chunk** | A piece of a document that gets its own embedding and its own slot in the vector database. The art is choosing the right size — too big and the embedding blurs across topics; too small and the chunk loses its context. | A 200-token excerpt from the student handbook parking section |
| **Fixed-Size Chunking** | Splitting a document every N tokens regardless of sentence or paragraph boundaries. Simple and predictable, but can cut a sentence in half. | Splitting the handbook every 500 tokens, with 50-token overlap between adjacent chunks |
| **Overlap** | The number of tokens repeated between adjacent chunks to avoid losing information at chunk boundaries. A 50-token overlap means the last 50 tokens of chunk 1 are also the first 50 tokens of chunk 2. | With chunk size 200 and overlap 50, a fact straddling a boundary appears intact in at least one chunk |
| **Recall@k** | The fraction of questions for which the correct chunk appears somewhere in the top-k retrieved results. Measures whether your retrieval system finds the right content at all, before the model sees it. | recall@3 = 0.80 means 80% of questions had the right chunk somewhere in the top 3 results |
| **Reranker** | A second-stage model that takes the top-k retrieval candidates and re-scores them for relevance to the specific query. The first stage retrieves broadly (high recall); the reranker filters precisely (high precision). | A local model scoring each chunk 0–10 for relevance, then re-ordering the list |
| **Semantic Clustering** | Grouping document chunks by the similarity of their embeddings, revealing what topics your corpus actually contains without reading every chunk manually. | K-means on normalized embeddings groups parking, dining, and housing chunks into 3 clusters |

---

# Part I: Chunking

## 1. The Goldilocks Problem

In this Part you will explore why the size of text chunks matters enormously for retrieval quality, examine three splitting strategies, and develop a principled hybrid policy you can apply to your own documents in the RAG Knowledge Base Lab.

**Why this matters:** Imagine searching a book using only its table of contents (chapters as chunks) versus searching it word by word (sentences as chunks). The table of contents gives you chapters that might be 50 pages long — your embedding has to summarize 50 pages into one vector, which blurs the meaning across dozens of topics. Individual sentences are precise but often meaningless in isolation: "He approved the request" tells you nothing about *who*, *what*, or *why*. Good chunking finds the passage-length sweet spot that is semantically self-contained and focused enough to embed meaningfully. It is the most impactful tuning knob in any real RAG system.

**Chunks too large** dilute the embedding (one vector must summarize many topics) and waste precious context window space. **Chunks too small** orphan their meaning ("He approved the request" retrieves nothing useful without knowing who *he* is). Practical systems balance three strategies:

| Strategy | How It Works | Best For | Trade-Off |
|----------|-------------|----------|-----------|
| **Fixed-size** | Split every N tokens, with overlap O tokens repeated between adjacent chunks (e.g., chunks of 200 tokens with 50-token overlap) | Simple documents where you want predictable chunk counts and easy tuning | Ignores sentence and paragraph structure; can split a key sentence across two chunks even with overlap |
| **Structural** | Split on natural document boundaries — headings, paragraph breaks, bullet items — respecting how the author organized the content | Well-structured documents like policies, manuals, or textbooks with clear sections | One section might be 50 tokens and another 2,000 tokens, creating uneven retrieval quality |
| **Semantic** | Split where the embedding similarity between consecutive sentences drops sharply — detecting topic shifts algorithmically | Long documents with many topic shifts where structural markers are sparse | More complex to implement; requires embedding every sentence before chunking |

Overlap repairs boundary damage: with chunk size 200 and overlap 50, a fact straddling a boundary appears intact in at least one chunk. The cost is index size inflation by a factor of roughly $\frac{n}{n - o}$ — so a 200-token chunk with 50-token overlap inflates the index by $\frac{200}{150} \approx 1.33$ times.

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

**Why this matters:** You cannot improve what you cannot measure. Before tuning chunk size, overlap, or any other parameter, you need a metric that tells you whether retrieval is actually working. Recall@k is that metric: for a set of test questions where you know the right answer, does the right chunk appear in the top k results? If recall@3 is 0.50, half your questions will get the wrong chunk and therefore a potentially hallucinated answer — regardless of how good your language model is. Generation quality has a ceiling imposed by retrieval quality, and this section gives you the tools to find and raise that ceiling.

For a question set with labeled relevant chunks, **recall@k** asks how often the right chunk appears in the top $k$ results:

$$
\text{recall@}k = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}\left[\text{relevant}_i \cap \text{top-}k_i \neq \emptyset\right]
$$

Read this as: for each of $N$ questions, check whether the relevant chunk appears anywhere in the top $k$ retrieved results (1 if yes, 0 if no), then average across all questions. A score of 1.0 means every question had its answer chunk in the top $k$; a score of 0.5 means half did.

A two-stage design retrieves generously then filters precisely: a fast vector search proposes, say, 20 candidates (achieving high recall — the right chunk is almost certainly in there), and a **reranker** (a slower model scoring each query-chunk pair directly) reorders them so the truly relevant chunk rises into the top 3 that actually fit the prompt (achieving high precision). Even an LLM prompted with "Rate the relevance of this passage to this question from 0 to 10" makes a serviceable reranker — our first taste of models evaluating text for other models.

[[MC]]
A system has recall@20 of 0.95 but recall@3 of 0.50, and the prompt only fits 3 chunks. The highest-leverage fix is:
- ( ) A larger generation model
- ( ) Smaller chunks with more overlap
- (x) A reranking stage between retrieval and prompt assembly
- ( ) Raising the temperature of the generator

---

## 3. Seeing Your Corpus: Semantic Clustering

**Why this matters:** Before you build a RAG system over a large document collection, you need to understand what you have. How many distinct topics does your corpus cover? Are there entire subjects with no coverage? Are there many near-duplicate chunks that waste index space and confuse retrieval? Clustering the embeddings gives you an automatic map of your corpus's topic structure, the same way a heat map of a city shows you where neighborhoods cluster — without reading every street address.

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

The code cell above clusters your corpus and draws the map. Before you trust a map, it is worth knowing how it was drawn — and k-means is simple enough to do on paper. Here is one full iteration on four chunk embeddings, reduced to two dimensions so the arithmetic stays visible.

Four chunks, with their (toy, 2-D) embeddings:

| Chunk | Vector | Roughly about |
|---|---|---|
| A | $(1.0,\; 1.0)$ | course policies |
| B | $(1.5,\; 2.0)$ | grading policy |
| C | $(5.0,\; 4.0)$ | RAG implementation |
| D | $(6.0,\; 5.0)$ | vector databases |

**Step 1 — initialize.** Pick $k = 2$ and seed the centroids at two of the points: $c_1 = (1,1)$, $c_2 = (6,5)$.

**Step 2 — assign each point to its nearest centroid** (Euclidean distance):

| Chunk | $d$ to $c_1$ | $d$ to $c_2$ | Assigned |
|---|---|---|---|
| A | $0.00$ | $6.40$ | **cluster 1** |
| B | $\sqrt{0.5^2 + 1^2} = 1.12$ | $5.41$ | **cluster 1** |
| C | $\sqrt{4^2 + 3^2} = 5.00$ | $\sqrt{1^2+1^2} = 1.41$ | **cluster 2** |
| D | $6.40$ | $0.00$ | **cluster 2** |

**Step 3 — recompute each centroid as the mean of its members:**

- $c_1 = \left(\frac{1.0 + 1.5}{2},\; \frac{1.0 + 2.0}{2}\right) = (1.25,\; 1.50)$
- $c_2 = \left(\frac{5.0 + 6.0}{2},\; \frac{4.0 + 5.0}{2}\right) = (5.50,\; 4.50)$

**Step 4 — repeat.** Reassign with the new centroids: nothing changes, so the algorithm has **converged** after one iteration. Two clusters, and they correspond to something real — policy chunks and implementation chunks — which nobody labeled.

**What this tells you about your own corpus map.** Three things worth carrying into Model 2:

1. **The clusters are an artifact of $k$, not a fact about your documents.** We chose $k = 2$. Choose $k = 4$ on this data and you get four singleton clusters, each perfectly "coherent" and completely useless. When the map looks clean, ask whether $k$ made it clean.
2. **The seeds matter.** Had we seeded at B and C instead, the first assignment would differ, and on messier data the final clustering can differ too. This is why production implementations use k-means++ seeding and run several times.
3. **Distance here is Euclidean, but retrieval usually ranks by cosine.** On *normalized* vectors the two give the same ordering — which is exactly why the pipeline normalizes embeddings before clustering. If you ever cluster un-normalized vectors, long documents drift away from the origin and form their own cluster purely because they are long, not because they are about anything in particular.


## Model 2: Reading the Map

**Why this matters:** The clusters the algorithm produces may or may not match the categories a human would draw. When they do not match, the mismatch is a window into what the embedding model actually "hears" in the text — and that is valuable information for predicting where your retrieval system will succeed and where it will fail.

### Critical Thinking Questions

4. Did the clusters recover the human topics (parking, dining, housing)? Identify any chunk the algorithm placed surprisingly, and hypothesize what feature of its wording caused it.

   > *Hint: "Room selection for returning students occurs in March" is about housing. But does it share vocabulary with other housing chunks? What words might cause it to cluster with a different group? Look at overlapping words between the surprise chunk and the cluster it joined.*

5. Why must we normalize the vectors before k-means if we intend cosine geometry? Think about what k-means minimizes.

   > *Hint: K-means minimizes Euclidean distance (straight-line distance in space) to cluster centroids. Cosine similarity ignores vector length and only measures direction. If two vectors point in the same direction but one is 10 times longer, cosine similarity says they are identical (score 1.0), but Euclidean distance says they are far apart. Normalizing (setting all vectors to length 1) makes Euclidean distance proportional to cosine distance.*

6. Describe two concrete uses of this cluster map when curating the knowledge base for the RAG Knowledge Base Lab: one use for finding *gaps* in your corpus, and one for finding *duplicates*.

   > *Hint: For gaps: if your corpus has 3 clusters but your users' questions span 5 topics, what does that tell you? For duplicates: if one cluster contains 12 chunks and they all say nearly the same thing in slightly different words, what is the problem for retrieval and for prompt assembly?*

> **⚠️ Common Misconception:** Many students assume that adding more documents always improves a RAG system. In practice, adding off-topic, contradictory, or near-duplicate documents hurts retrieval quality. A search engine that returns 20 near-identical parking regulations when you ask about dining hours is retrieving with high recall but low precision. Corpus *quality* and *coverage* matter more than corpus *size*, and clustering is one of the best tools for auditing both.

---

# Part III: Synthesis and Practice

With the theory of recall and reranking established, this hands-on section puts chunking strategies head-to-head on a real document so you can see the performance differences numerically rather than hypothetically.

## Hands-On: Chunking Strategy Comparison (30 minutes)

In this section your team implements three chunking strategies, runs the same five test questions through all three, and fills in a results table. No external libraries are needed — the retrieval function uses a simple word-frequency cosine similarity (a score between 0 and 1 measuring how much vocabulary two texts share) so the comparison is purely about chunking.

---

### Sample Document

Copy this 400-word excerpt into a string variable called `DOCUMENT`. It covers the history of artificial intelligence and contains facts that span paragraph boundaries — ideal for exposing chunking edge cases.

```python
DOCUMENT = """
The field of artificial intelligence was formally founded at the Dartmouth Conference in 1956,
where John McCarthy, Marvin Minsky, Claude Shannon, and others gathered to explore whether
machines could be made to simulate human intelligence. The participants were optimistic,
predicting that a significant portion of human intellectual activity could be replicated
within a single generation. This optimism led to substantial government funding throughout
the late 1950s and 1960s, particularly from the United States Department of Defense.

Early AI research focused on symbolic reasoning and rule-based systems. Programs like the
Logic Theorist, created by Allen Newell and Herbert Simon in 1956, could prove mathematical
theorems by manipulating symbols according to formal rules. The General Problem Solver,
which followed in 1957, attempted to model human problem-solving strategies using means-ends
analysis. These systems demonstrated that computers could perform tasks previously thought
to require human intelligence, though they struggled with the complexity of real-world problems.

The first AI winter arrived in the 1970s when researchers encountered fundamental limitations.
Minsky and Papert's 1969 book Perceptrons demonstrated mathematical limitations of single-layer
neural networks, dampening enthusiasm for connectionist approaches. Meanwhile, combinatorial
explosion made symbolic AI intractable for realistic problem sizes. Funding from DARPA and
other agencies dried up as promises went unmet, and the field entered a period of reduced
activity and skepticism known as the AI winter.

The expert systems era of the 1980s briefly revived interest. Programs like MYCIN, which
diagnosed bacterial infections and recommended antibiotics, and XCON, which configured
computer hardware for Digital Equipment Corporation, demonstrated genuine commercial value.
XCON alone saved DEC an estimated forty million dollars per year by the mid-1980s. These
systems encoded human expertise as thousands of if-then rules and could outperform novices
in narrow domains, but they were brittle: any question outside the rule set produced no answer.

The rise of machine learning in the 1990s and 2000s shifted the paradigm from hand-coded
rules to systems that learned patterns from data. The availability of larger datasets,
faster processors, and algorithms like support vector machines and boosting made it possible
to achieve high accuracy on tasks like handwriting recognition and email spam filtering
without explicit programming of rules. This data-driven approach would eventually culminate
in the deep learning revolution of the 2010s.
"""
```

---

### Three Chunking Functions

Each function below implements one splitting strategy and returns a list of strings (the chunks). You will pass these chunk lists to the retrieval function in the next section.

```python
def chunk_fixed_size(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split text into fixed-character windows with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]  # drop any empty strings from trailing whitespace


def chunk_by_sentence(text: str, n_sentences: int = 3, overlap: int = 1) -> list[str]:
    """Split text into groups of n_sentences, with overlap sentences between groups."""
    import re
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    chunks = []
    step = max(1, n_sentences - overlap)
    for i in range(0, len(sentences), step):
        group = sentences[i:i + n_sentences]
        if group:
            chunks.append(" ".join(group))
    return chunks


def chunk_by_paragraph(text: str) -> list[str]:
    """Split text on blank lines, treating each paragraph as one chunk."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs
```

---

### Retrieval with Simple Cosine Similarity

This function computes retrieval using word-frequency vectors so you can run the comparison without embedding infrastructure. For production RAG, you would replace this with actual embeddings from a local model.

```python
def cosine_sim(a: str, b: str) -> float:
    """Compute cosine similarity between two strings using word frequency vectors."""
    words = list(set(a.split() + b.split()))
    va = [a.split().count(w) for w in words]
    vb = [b.split().count(w) for w in words]
    dot = sum(x * y for x, y in zip(va, vb))
    mag_a = sum(x * x for x in va) ** 0.5
    mag_b = sum(x * x for x in vb) ** 0.5
    return dot / (mag_a * mag_b + 1e-9)


def retrieve(chunks: list[str], query: str, top_k: int = 3) -> list[str]:
    """Return the top_k chunks most similar to query by cosine similarity."""
    scored = [(cosine_sim(query.lower(), c.lower()), c) for c in chunks]
    return [c for _, c in sorted(scored, reverse=True)[:top_k]]
```

> **Note:** For real RAG, use a local embedding model (e.g., `nomic-embed-text` via Ollama) in place of word-frequency cosine similarity. The word-frequency approach works for this classroom comparison because the test questions deliberately use vocabulary from the document.

---

### Five Test Questions

Use these questions to evaluate all three chunking strategies. For each question, run `retrieve(chunks, question, top_k=2)` and check whether any of the returned chunks actually contain the answer.

```python
QUESTIONS = [
    # Q1: answer is contained within a single paragraph
    "Who were the founders of artificial intelligence at the Dartmouth Conference?",
    # Q2: answer requires connecting two adjacent sentences in different paragraphs
    "What mathematical limitation did Minsky and Papert demonstrate, and when?",
    # Q3: answer uses a specific number that appears mid-paragraph
    "How much money did XCON save Digital Equipment Corporation per year?",
    # Q4: answer is in the last paragraph, using different vocabulary than the question
    "What algorithmic approaches enabled high accuracy on spam filtering?",
    # Q5: answer spans a paragraph boundary between the expert systems era and ML era
    "What limitation did expert systems have compared to machine learning systems?",
]

# Run the comparison
for strategy_name, chunks in [
    ("Fixed (300 chars, overlap=50)", chunk_fixed_size(DOCUMENT)),
    ("By Sentence (3 sent, overlap=1)", chunk_by_sentence(DOCUMENT)),
    ("By Paragraph", chunk_by_paragraph(DOCUMENT)),
]:
    print(f"\n=== {strategy_name} ({len(chunks)} chunks) ===")
    for i, q in enumerate(QUESTIONS, 1):
        results = retrieve(chunks, q, top_k=2)
        print(f"  Q{i}: {q[:60]}...")
        for j, r in enumerate(results, 1):
            print(f"    [{j}] {r[:100].strip()}...")
```

---

### Results Table

Fill in this table after running the comparison. Mark each cell **Y** (the relevant chunk appeared in the top 2 results) or **N** (it did not).

| Chunking Strategy | Num Chunks | Q1 Relevant? | Q2 Relevant? | Q3 Relevant? | Q4 Relevant? | Q5 Relevant? | Recall@2 |
|---|---|---|---|---|---|---|---|
| Fixed (300 chars, overlap=50) | | | | | | | /5 |
| By Sentence (3 sent, overlap=1) | | | | | | | /5 |
| By Paragraph | | | | | | | /5 |

---

### Critical Thinking Questions

9. Fixed-size chunking sometimes splits a sentence mid-phrase. Find one example where this hurt retrieval in your results table. What was the symptom — which question failed, and what did the returned chunks contain instead of the answer?

   > *Hint: Look for a question where the answer spans a character-boundary cut. For example, if chunk N ends with "the participants were" and chunk N+1 begins with "optimistic, predicting...", neither chunk alone answers a question about the founders' predictions. Print a few boundary regions of the fixed chunks to see exactly where cuts landed.*

[[MC]]
You increase `chunk_size` from 100 characters to 1000 characters (keeping overlap=0). Which of the following best describes the trade-off?
- ( ) Fewer chunks means faster embedding but always better retrieval precision
- (x) Larger chunks improve the chance that a multi-sentence answer is intact in one chunk, but each chunk's embedding blurs across more topics, reducing precision for focused queries
- ( ) Larger chunks always increase recall@k regardless of the query
- ( ) Chunk size affects only storage cost, not retrieval quality

> *Hint: Think about the Goldilocks Problem from Part I. A 1000-character chunk might span three different topics. Its embedding vector must summarize all three topics at once. When a user asks about just one of those topics, the chunk may rank lower than a smaller, more focused chunk — even though the answer is physically present inside it.*

10. If `overlap=0` and `chunk_size=100`, a fact that starts at character 95 and ends at character 110 will be split across two chunks and may be incomplete in both. If `overlap=90` and `chunk_size=100`, that same fact appears in many chunks — but what is the cost of very large overlap?

    > *Hint: Calculate how many chunks a 1000-character document produces with chunk_size=100 and overlap=90 versus overlap=0. Every chunk must be embedded and stored. What happens to index size? What happens to retrieval when many nearly identical chunks all rank highly for the same query?*

11. Sentence-based chunking preserves meaning better than fixed-size. But sentences in legal contracts can be 200 words long, and a single contract clause might span 10 such sentences. What chunking strategy would you use for legal documents, and why?

    > *Hint: Consider a hybrid: use structural splits on numbered clauses or headings first (which legal documents typically have), then apply sentence-based chunking within any clause that exceeds a maximum character count. This gives you semantically coherent units at the clause level without risking 2000-word chunks for complex clauses.*

> **⚠️ Common Misconception:** Students often assume that smaller chunks always give better retrieval because they are more "targeted." But very small chunks lose the surrounding context that the similarity function needs to judge relevance. A chunk containing only the words "the act" scores low against almost any query — there is no context for which act, when, or why it matters. The retrieval model (whether word-frequency or a neural embedding) needs enough surrounding text to understand what the chunk is about. A practical lower bound is roughly one complete sentence; a practical upper bound is roughly one focused paragraph.

---

---

**🛑 In-class work stops here.** The exercises below are homework and going-deeper material — attempt them before the related lab.

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

*Technical:* In your notebook: chunking is an editorial act — someone (or some algorithm) decides where meaning begins and ends. When you index a document written by someone else, what obligations do you have to preserve its meaning, and how would you check whether your pipeline honored them?

*Societal:* A law firm deploys RAG over a corpus of 10,000 legal documents to help paralegals find relevant precedents. The chunking strategy splits some court opinions mid-sentence, occasionally separating the holding (the decision) from its reasoning. Who is harmed if the system retrieves the holding without the reasoning? What audit process would you require before deploying such a system?

---

## → Coming Up Next

We now have a RAG system that can find and deliver relevant information. The next challenge is that agents need to *remember* context across many turns of a conversation — and the context window is not infinite. The *Memory and the Small Context Window Principle* activity addresses this next: how agents manage, compress, and retrieve their own history without drowning in their past.

---

## 5. Further Reading

- Chroma documentation on collections and querying: https://docs.trychroma.com
- Nils Reimers. "Retrieve and Re-Rank" (Sentence-Transformers documentation, online).
- Liu et al. "Lost in the Middle." *TACL* (2024), on why chunk *placement* in the prompt also matters.
