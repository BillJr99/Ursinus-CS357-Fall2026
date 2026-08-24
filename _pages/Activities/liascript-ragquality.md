<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-ragquality.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-ragquality.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# RAG Quality: Chunking, Clustering, and Reranking

The RAG pipeline from the *Retrieval-Augmented Generation with Chroma* activity worked because our "documents" were single tidy sentences; real documents are messy, and **how you cut them up determines what you can find**.  This module develops the engineering of retrieval quality: **chunking strategies $\rightarrow$ measuring retrieval $\rightarrow$ semantic clustering of a corpus $\rightarrow$ reranking**, the same levers you will tune in the RAG Knowledge Base Lab.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

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

## 1.  The Goldilocks Problem

In this Part you will explore why the size of text chunks matters enormously for retrieval quality, examine three splitting strategies, and develop a principled hybrid policy you can apply to your own documents in the RAG Knowledge Base Lab.

**Why this matters:** Imagine searching a book using only its table of contents (chapters as chunks) versus searching it word by word (sentences as chunks).  The table of contents gives you chapters that might be 50 pages long; your embedding has to summarize 50 pages into one vector, which blurs the meaning across dozens of topics.  Individual sentences are precise but often meaningless in isolation: "He approved the request" tells you nothing about *who*, *what*, or *why*.  Good chunking finds the passage-length sweet spot that is semantically self-contained and focused enough to embed meaningfully.  It is the most impactful tuning knob in any real RAG system.

**Chunks too large** dilute the embedding (one vector must summarize many topics) and waste precious context window space.  **Chunks too small** orphan their meaning ("He approved the request" retrieves nothing useful without knowing who *he* is).  Practical systems balance three strategies:

| Strategy | How It Works | Best For | Trade-Off |
|----------|-------------|----------|-----------|
| **Fixed-size** | Split every N tokens, with overlap O tokens repeated between adjacent chunks (e.g., chunks of 200 tokens with 50-token overlap) | Simple documents where you want predictable chunk counts and easy tuning | Ignores sentence and paragraph structure; can split a key sentence across two chunks even with overlap |
| **Structural** | Split on natural document boundaries (headings, paragraph breaks, bullet items) respecting how the author organized the content | Well-structured documents like policies, manuals, or textbooks with clear sections | One section might be 50 tokens and another 2,000 tokens, creating uneven retrieval quality |
| **Semantic** | Split where the embedding similarity between consecutive sentences drops sharply, detecting topic shifts algorithmically | Long documents with many topic shifts where structural markers are sparse | More complex to implement; requires embedding every sentence before chunking |

Overlap repairs boundary damage: with chunk size 200 and overlap 50, a fact straddling a boundary appears intact in at least one chunk.  The cost is index size inflation by a factor of roughly $\frac{n}{n - o}$, so a 200-token chunk with 50-token overlap inflates the index by $\frac{200}{150} \approx 1.33$ times.

---

## Model 1: Cut This Document

Consider a 12-page student handbook with sections on housing, dining, conduct, and parking, where the parking rules paragraph begins with "Exceptions to the above:".

### Critical Thinking Questions

1.  A fixed 500-token chunker splits mid-sentence between "the above" rules and the exceptions.  Describe the wrong answer a RAG system would confidently give about parking, and which chunking strategy prevents it.

   > *Hint: The exception chunk starts with "Exceptions to the above:" but the "above" rules are in the previous chunk.  If a student asks "Are there exceptions to the parking rule?", the system retrieves the exceptions chunk but the model cannot know what rule is being excepted.  What answer might it fabricate?  Which chunking strategy keeps the rule and its exceptions together?*

2.  Structural chunking yields one enormous "conduct" chunk.  What goes wrong at *embedding* time (when the vector is created), and what goes wrong at *prompt assembly* time (when the chunk is pasted into the prompt)?

   > *Hint: At embedding time: one vector has to represent 3,000 tokens covering academic honesty, social conduct, residence hall policies, and disciplinary procedures.  What happens to the "meaning direction" of that vector?  At prompt assembly: if this chunk is retrieved, how much of your 4,000-token context window does it consume?*

3.  Propose a hybrid policy for the handbook (one sentence per rule), and have the Recorder write it as if it were documentation for the RAG Knowledge Base Lab.

   > *Hint: A hybrid policy might say: "Use structural splits on section headings first, then apply fixed-size chunking with 50-token overlap within any structural chunk larger than 400 tokens, with a minimum chunk size of 100 tokens."  Write this as a numbered specification your lab partner could implement.*

---

# Part II: Measuring and Improving Retrieval

## 2.  Retrieval Metrics

In this Part you will learn how to measure whether your retrieval system is actually working, understand the recall@k metric (the fraction of questions for which the right chunk appears in the top-k results), and see how a reranker can raise precision without sacrificing recall.

**Why this matters:** You cannot improve what you cannot measure.  Before tuning chunk size, overlap, or any other parameter, you need a metric that tells you whether retrieval is actually working.  Recall@k is that metric: for a set of test questions where you know the right answer, does the right chunk appear in the top k results?  If recall@3 is 0.50, half your questions will get the wrong chunk and therefore a potentially hallucinated answer, regardless of how good your language model is.  Generation quality has a ceiling imposed by retrieval quality, and this section gives you the tools to find and raise that ceiling.

For a question set with labeled relevant chunks, **recall@k** asks how often the right chunk appears in the top $k$ results:

$$
\text{recall@}k = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}\left[\text{relevant}_i \cap \text{top-}k_i \neq \emptyset\right]
$$

Read this as: for each of $N$ questions, check whether the relevant chunk appears anywhere in the top $k$ retrieved results (1 if yes, 0 if no), then average across all questions.  A score of 1.0 means every question had its answer chunk in the top $k$; a score of 0.5 means half did.

A two-stage design retrieves generously then filters precisely: a fast vector search proposes, say, 20 candidates (achieving high recall; the right chunk is almost certainly in there), and a **reranker** (a slower model scoring each query-chunk pair directly) reorders them so the truly relevant chunk rises into the top 3 that actually fit the prompt (achieving high precision).  Even an LLM prompted with "Rate the relevance of this passage to this question from 0 to 10" makes a serviceable reranker, our first taste of models evaluating text for other models.

A system has recall@20 of 0.95 but recall@3 of 0.50, and the prompt only fits 3 chunks.  The highest-leverage fix is:

[( )] A larger generation model
[( )] Smaller chunks with more overlap
[(X)] A reranking stage between retrieval and prompt assembly
[( )] Raising the temperature of the generator

---

## 3.  Seeing Your Corpus: Semantic Clustering

**Why this matters:** Before you build a RAG system over a large document collection, you need to understand what you have.  How many distinct topics does your corpus cover?  Are there entire subjects with no coverage?  Are there many near-duplicate chunks that waste index space and confuse retrieval?  Clustering the embeddings gives you an automatic map of your corpus's topic structure, the same way a heat map of a city shows you where neighborhoods cluster, without reading every street address.

Embeddings let us *map* a document collection before querying it.  Clustering chunk vectors (k-means on normalized embeddings approximates clustering by cosine similarity) reveals the topics your corpus actually contains, exposes duplicates, and flags off-topic contamination.

---

The code below embeds eight campus-policy chunks using a local model, then runs k-means clustering (a method that groups items into k groups by finding the assignments that minimize total distance to each group's center) on the normalized embedding vectors.  After running it, you will read the cluster output and judge whether the algorithm found the same topic structure a human would draw.

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

The code cell above clusters your corpus and draws the map.  Before you trust a map, it is worth knowing how it was drawn, and k-means is simple enough to do on paper.  Here is one full iteration on four chunk embeddings, reduced to two dimensions so the arithmetic stays visible.

Four chunks, with their (toy, 2-D) embeddings:

| Chunk | Vector | Roughly about |
|---|---|---|
| A | $(1.0,\; 1.0)$ | course policies |
| B | $(1.5,\; 2.0)$ | grading policy |
| C | $(5.0,\; 4.0)$ | RAG implementation |
| D | $(6.0,\; 5.0)$ | vector databases |

**Step 1: initialize.**  Pick $k = 2$ and seed the centroids at two of the points: $c_1 = (1,1)$, $c_2 = (6,5)$.

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

**Step 4: repeat.**  Reassign with the new centroids: nothing changes, so the algorithm has **converged** after one iteration.  Two clusters, and they correspond to something real (policy chunks and implementation chunks) which nobody labeled.

**What this tells you about your own corpus map.**  Three things worth carrying into Model 2:

1.  **The clusters are an artifact of $k$, not a fact about your documents.**  We chose $k = 2$. Choose $k = 4$ on this data and you get four singleton clusters, each perfectly "coherent" and completely useless.  When the map looks clean, ask whether $k$ made it clean.
2.  **The seeds matter.**  Had we seeded at B and C instead, the first assignment would differ, and on messier data the final clustering can differ too.  This is why production implementations use k-means++ seeding and run several times.
3.  **Distance here is Euclidean, but retrieval usually ranks by cosine.**  On *normalized* vectors the two give the same ordering, which is exactly why the pipeline normalizes embeddings before clustering.  If you ever cluster un-normalized vectors, long documents drift away from the origin and form their own cluster purely because they are long, not because they are about anything in particular.


## Model 2: Reading the Map

**Why this matters:** The clusters the algorithm produces may or may not match the categories a human would draw.  When they do not match, the mismatch is a window into what the embedding model actually "hears" in the text, and that is valuable information for predicting where your retrieval system will succeed and where it will fail.

### Critical Thinking Questions

4.  Did the clusters recover the human topics (parking, dining, housing)?  Identify any chunk the algorithm placed surprisingly, and hypothesize what feature of its wording caused it.

   > *Hint: "Room selection for returning students occurs in March" is about housing.  But does it share vocabulary with other housing chunks?  What words might cause it to cluster with a different group?  Look at overlapping words between the surprise chunk and the cluster it joined.*

5.  Why must we normalize the vectors before k-means if we intend cosine geometry?  Think about what k-means minimizes.

   > *Hint: K-means minimizes Euclidean distance (straight-line distance in space) to cluster centroids.  Cosine similarity ignores vector length and only measures direction.  If two vectors point in the same direction but one is 10 times longer, cosine similarity says they are identical (score 1.0), but Euclidean distance says they are far apart.  Normalizing (setting all vectors to length 1) makes Euclidean distance proportional to cosine distance.*

6.  Describe two concrete uses of this cluster map when curating the knowledge base for the RAG Knowledge Base Lab: one use for finding *gaps* in your corpus, and one for finding *duplicates*.

   > *Hint: For gaps: if your corpus has 3 clusters but your users' questions span 5 topics, what does that tell you?  For duplicates: if one cluster contains 12 chunks and they all say nearly the same thing in slightly different words, what is the problem for retrieval and for prompt assembly?*

> **Common Misconception:** Many students assume that adding more documents always improves a RAG system.  In practice, adding off-topic, contradictory, or near-duplicate documents hurts retrieval quality.  A search engine that returns 20 near-identical parking regulations when you ask about dining hours is retrieving with high recall but low precision.  Corpus *quality* and *coverage* matter more than corpus *size*, and clustering is one of the best tools for auditing both.

---

# Part III: Synthesis and Practice

With the theory of recall and reranking established, this hands-on section puts chunking strategies head-to-head on a real document so you can see the performance differences numerically rather than hypothetically.

## Hands-On: Chunking Strategy Comparison

The full 30-minute build (the sample document, three chunking functions, cosine retrieval, the five test questions, and the results table) now lives on the **[RAG Knowledge Base lab](https://www.billmongan.com/Ursinus-CS357/Assignments/RAGKnowledgeBase)**, which is handed out today and is where you run the comparison for credit.

Today we stay on the *judgment*: where a chunk boundary belongs, and what recall@k does and does not tell you.

## 4.  Exercises

In this Part you apply everything from Parts I and II to real documents: run a chunking shootout on a campus policy page, build and test a reranker using your local model, plot a recall curve, and choose a retrieval configuration you can defend with numbers.

1.  *Chunking shootout.*  Take one real page of a campus document.  Index it three ways (fixed 100 tokens no overlap, fixed 300 tokens with 75-token overlap, paragraph-structural).  For five questions with known answers, report which indexing strategy wins recall@2, and explain the winner.

   - *What to do:* Choose a real campus policy page (parking, dining, honor code, etc.).  Implement three versions of the chunker and create three separate Chroma collections.  For 5 questions where you know which paragraph contains the answer, run all three and check whether the answer paragraph appears in the top 2 results.
   - *Starter hint:* For fixed chunking: `chunks = [text[i:i+n] for i in range(0, len(text), n-overlap)]`.  For paragraph structural: `chunks = [p.strip() for p in text.split('\n\n') if p.strip()]`.  Count recall@2 as: for each of 5 questions, 1 if the right chunk is in position 1 or 2, else 0.  Divide by 5.
   - *You've succeeded when:* You have a table with 3 rows (one per chunking strategy) and 5 question columns (1 = retrieved, 0 = not), plus a recall@2 score for each strategy and a one-sentence explanation of why the winner worked best for this particular document.

2.  *Build a reranker.*  Wrap your local model in a relevance-scoring prompt, rerank 10 retrieved candidates for three questions, and report the rank change of the truly relevant chunk.

   - *What to do:* Retrieve the top 10 chunks for 3 questions using your Chroma collection.  For each chunk, call the model with a prompt like: "On a scale of 0 to 10, how relevant is the following passage to the question '{question}'?  Passage: '{chunk}'.  Reply with only a number."  Sort by score and report the new rank of the chunk you know is correct.
   - *Starter hint:* `def rerank_score(question, chunk): return int(chat(f"Rate relevance 0-10 of this passage to '{question}': '{chunk}'. Reply only with a number."))`.  Call this for each of your 10 candidates, sort descending, and report where the correct chunk landed before and after reranking.
   - *You've succeeded when:* For at least 2 of 3 questions, the correct chunk's rank improves after reranking (e.g., moved from position 4 to position 1), and you can explain in one sentence why the initial vector search placed it lower.

3.  *Recall curve.*  For your RAG Knowledge Base Lab corpus draft, plot recall@k for $k \in \{1, 2, 3, 5, 10\}$, and choose the $k$ you will ship, defending the choice in two sentences that mention both context budget and accuracy.

   - *What to do:* Build a small evaluation set of 10 questions with labeled relevant chunks.  Run your Chroma search with n_results=10 for each question.  Compute recall@k for each k value by checking whether the correct chunk appears in the top k.  Plot the resulting curve with `matplotlib`.
   - *Starter hint:* `recall_at_k = [sum(1 for q in eval_set if correct_chunk[q] in top_k_results[q][:k]) / len(eval_set) for k in [1,2,3,5,10]]`.  Then `plt.plot([1,2,3,5,10], recall_at_k)`.
   - *You've succeeded when:* You have a plotted recall curve showing recall@k for k in {1,2,3,5,10}, and your written justification explicitly trades off "more chunks = higher recall but fewer prompt tokens remaining for the answer" against the accuracy you need for your application.

---

## Reflection Prompt

*Personal:* Think about a time someone summarized or quoted something you wrote or said, and the summary changed the meaning.  How does that experience connect to what happens when a large chunk is embedded into a single vector?

*Technical:* In your notebook: chunking is an editorial act: someone (or some algorithm) decides where meaning begins and ends.  When you index a document written by someone else, what obligations do you have to preserve its meaning, and how would you check whether your pipeline honored them?

*Societal:* A law firm deploys RAG over a corpus of 10,000 legal documents to help paralegals find relevant precedents.  The chunking strategy splits some court opinions mid-sentence, occasionally separating the holding (the decision) from its reasoning.  Who is harmed if the system retrieves the holding without the reasoning?  What audit process would you require before deploying such a system?

---

## -> Coming Up Next

We now have a RAG system that can find and deliver relevant information.  Next session, *How I AI*, turns that instinct on your own notes: a vault of plain files an agent can read, with the zone boundaries and contract that make it safe to let one write there.  Its Part III is an open studio, so bring your pipeline-in-progress and your stuck points.  The theory behind all of it, why an agent needs external memory at all, follows the session after in *Memory and the Small Context Window Principle*.

---

## 5.  Further Reading

- Chroma documentation on collections and querying: https://docs.trychroma.com
- Nils Reimers.  "Retrieve and Re-Rank" (Sentence-Transformers documentation, online).
- Liu et al. "Lost in the Middle."  *TACL* (2024), on why chunk *placement* in the prompt also matters.

---

# Extension: Fine-Tuning, RAG, and Prompting (self-paced)

Optional, and not assumed by anything above.  You now know how to make retrieval work well.  The next question your project will force on you is whether retrieval was the right tool at all, or whether the job wanted a better prompt or an actually fine-tuned model.  This section gives you the decision framework and the cost model behind it.

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| Prompting | Giving the AI model written instructions, examples, or context within a single request; no code changes, no training, just better text. | Writing a system prompt that says "You are a helpful HR assistant. Always cite the policy section number." |
| RAG (Retrieval-Augmented Generation) | Connecting the AI to an external knowledge source (like a document database) so it can look up relevant information before answering; the model's weights never change. | Before answering "What is our PTO policy?", the system fetches the relevant section of the employee handbook and includes it in the prompt. |
| Fine-Tuning | Continuing the model's training on your own data so the model's internal weights permanently change; it behaves differently on every future call, even without special prompts. | Training `llama3.1:8b` on 800 examples of correctly formatted legal contract summaries so it always produces that format. |
| LoRA (Low-Rank Adaptation) | A parameter-efficient fine-tuning method that trains only tiny "adapter" matrices (about 0.1% of the total parameters) instead of updating the entire model, dramatically reducing GPU cost. | Fine-tuning a 7B model with LoRA requires a single A100 GPU for a few hours instead of a multi-GPU cluster for days. |
| QLoRA | LoRA combined with 4-bit quantization of the frozen base model weights; enables fine-tuning 7B models on a single consumer GPU with 24 GB of VRAM. | Students at Ursinus can run QLoRA fine-tuning on a rented Lambda Labs A100 instance for roughly $3-5. |
| Context Window | The maximum amount of text (measured in tokens, where 1 token ≈ 0.75 words) that a model can read in a single request; determines whether "just paste the whole document in" is even possible. | GPT-4o has a 128K token context window, about 96,000 words. A 500-page policy manual (~200,000 words) still exceeds it. |

---

## The Ladder

In this part, you will learn the three fundamental ways to specialize a language model (prompting, RAG, and fine-tuning) and build a diagnostic framework for choosing among them.  Understanding which lever to reach for first will save your team weeks of unnecessary work.

### Three Ways to Specialize a Model

This is the "hire an expert vs. give your generalist a textbook" decision, and just like in real life, hiring a full specialist is expensive, slow, and permanent.  Sometimes the right answer is to give your generalist a great textbook (RAG), or better instructions (prompting), and only bring in the specialist when those cannot work.

The three approaches differ in *where the specialization lives*: in the prompt at inference time, in retrieved text at inference time, or in the model weights permanently.

**Prompting** gives the model instructions, examples, and context within a single call.  Zero-shot prompting provides instructions only; few-shot adds 2-10 worked examples; chain-of-thought prompts the model to reason step by step before answering.  Prompting is free, instant, and reversible, but is bounded by the context window and by what the base model already knows.  A model that has never seen clinical trial reports cannot be prompted into reliable clinical summarization.

**RAG** injects retrieved information at inference time.  The model receives the same prompt, but now the prompt includes relevant documents fetched from an external index.  The model's weights never change.  RAG excels when knowledge is dynamic (daily news, live databases), external (proprietary documents the base model never saw), or too large for any context window.  Its costs are operational: embedding, indexing, retrieval latency, and the complexity of the pipeline.

**Fine-tuning** adjusts the model's weights on a task-specific dataset.  The change is permanent: a fine-tuned model behaves differently on every subsequent call, without any special prompt.  Fine-tuning can teach style, format, vocabulary, and domain behavior that prompting cannot reliably achieve.  It is also the most expensive and least reversible option.  **PEFT (Parameter-Efficient Fine-Tuning)** methods such as LoRA and QLoRA reduce cost dramatically by freezing most weights and training only small adapter matrices; more on this below.

The practical rule: **start at the top of the ladder**.  Reach for fine-tuning only after you have really tried prompting and RAG and found them insufficient.

---

### The Decision Framework

Use this table as a diagnostic.  Each row is a question to ask before choosing an approach; the answers point you toward the right rung.  Work through the rows in order, like a flowchart where each answer narrows your options.

| Diagnostic Question | If Yes | If No |
|---|---|---|
| Does the base model already know the domain well enough to answer correctly with good instructions? | Start with prompting or RAG; you may not need anything more expensive | Consider fine-tuning or domain-adaptive pre-training to inject the domain knowledge |
| Is the knowledge dynamic, updated frequently, or stored in proprietary documents the model has never seen? | Use RAG; it reads your documents at query time without retraining | Fine-tuning may be appropriate; bake the stable knowledge into model weights |
| Do you need citations or source attribution in the output so users can verify claims? | Use RAG; retrieved chunks naturally serve as citations | Either prompting or fine-tuning; hallucinated citations are a serious risk without retrieval |
| Is the required output format or style highly specific and must be perfectly consistent across thousands of calls (e.g., a fixed JSON schema, a precise legal format)? | Fine-tuning (or strong few-shot prompting as a first attempt); format training is one of fine-tuning's clearest wins | Prompting or RAG is likely sufficient for moderate format requirements |
| Do you have labeled input-output pairs for the task (hundreds to thousands of examples)? | Fine-tuning is technically feasible; you have the data required | Use prompting or RAG for now; invest in data collection if fine-tuning becomes necessary |
| Is cost or latency the primary constraint, does every extra millisecond or fraction of a cent matter? | Prompting (cheapest per call, lowest latency, no infrastructure) | Fine-tuning or RAG if quality justifies the added cost and complexity |

#### Questions to Work Through

1.  A startup wants to build a customer support bot that answers questions about their product documentation, which is updated every sprint (roughly every two weeks).  Walk through the decision table row by row and justify your final recommendation.

   *Hint:* Pay special attention to the "Is the knowledge dynamic?" row.  What does "updated every two weeks" mean for an approach that requires retraining (days of work) vs. an approach that requires re-indexing (minutes of work)?

2.  A legal firm wants every contract summary the model produces to follow a precise seven-section structure with mandatory fields.  They have 2,000 existing human-written summaries in that format.  Walk through the decision table for this case.  Does the answer change if they only have 50 examples?  Why?

   *Hint:* Fine-tuning for format typically requires at least a few hundred examples to be reliable.  With 50 examples, few-shot prompting (including 3-5 examples directly in the prompt) may actually outperform a poorly-fitted fine-tuned model.

3.  "The model already knows how to write code, so we just need to prompt it."  A team makes this argument to avoid fine-tuning their coding assistant.  Describe a concrete scenario where this reasoning fails, where the gap between base model behavior and desired behavior is too large for prompting to close.

   *Hint:* Think about a company-specific internal library with custom APIs that the base model has never seen (because it's proprietary).  No amount of prompting teaches the model what `acme_corp.billing.create_invoice(customer_id, line_items)` does.

---

## Cost and the LoRA Shortcut

In this part, you will compare the true costs of prompting, RAG, and fine-tuning, and learn how LoRA dramatically reduces the GPU memory and compute needed for fine-tuning, making it accessible for small teams and individuals.

### The Cost Reality

The order-of-magnitude cost differences between approaches are often underappreciated.  These figures are rough but directionally correct as of 2025.  Think of it like building a house: you can rent a furnished apartment immediately (prompting), move into a place and add your own furniture (RAG), or custom-build from scratch (fine-tuning); each has very different upfront and ongoing costs.

| Approach | Typical Cost per Query | One-Time Setup Cost | Infrastructure Needed | Data Requirement |
|---|---|---|---|---|
| Prompting (API call to GPT-4o or Claude) | $0.003-$0.05 per 1,000-token call depending on model | None beyond prompt engineering time | None: uses a managed API | None: just write better instructions |
| RAG (API + Chroma/Qdrant vector DB) | $0.001-$0.02 per query (embedding + retrieval + smaller LLM call) | Hours to days of pipeline engineering | Vector DB (free locally, ~$50/mo cloud for small scale), embedding service | Source documents only; no labeled pairs needed |
| Fine-tuning (small model, LoRA on `llama3.1:8b`) | $0.0001-$0.001 per call after training (self-hosted inference) | $10-$200 per training run on a rented A100 GPU | GPU for training (A100/H100 rented on Lambda Labs), storage for weights | 200-2,000 labeled input-output pairs |
| Fine-tuning (large model, full weight update) | $0.0001-$0.001 per call after training (self-hosted inference) | $1,000-$50,000 per training run on multi-GPU cluster | Multi-GPU cluster, distributed training framework (DeepSpeed, FSDP) | Thousands to millions of labeled pairs |
| Pre-training from scratch | Fractions of a cent per call after training | $1,000,000+ for a competitive model | Massive GPU cluster, months of compute | Billions of tokens of curated text |

The "low cost per call after training" for fine-tuning is deceptive: the inference cost is low, but the up-front training cost is paid once per model version.  If the domain or data changes, you re-pay that cost.

### Same Task, Three Approaches

Consider a concrete deployment: **an HR policy assistant that answers questions about a company's internal policy document**.  This is exactly the kind of task where the choice of approach has real, measurable consequences.

| Dimension | Prompting: Paste Full Doc in Context | RAG: Chunk, Embed, Retrieve | Fine-Tuning: Train on Q&A Pairs |
|---|---|---|---|
| Implementation effort | Include entire policy in the system prompt; takes minutes to set up | Index policy chunks in a vector DB; retrieve on each query; takes hours to set up (`pip install chromadb`, embed chunks, build query pipeline) | Generate Q&A pairs from the doc, fine-tune a base model like `llama3.1:8b` with LoRA; takes days |
| How it handles policy updates | Immediately: just update the prompt text with the new policy content | With re-indexing, which takes minutes to hours depending on document size | Must retrain, which takes hours to days and costs GPU compute |
| Cost per user query | Higher token cost because the entire policy is in every prompt (e.g., a 50-page doc = ~25,000 tokens × $0.005/1K = $0.125 per call) | Moderate: retrieval + smaller context (typically 1,000-3,000 tokens per call) | Very low per call after training, but training itself costs $20-$200 upfront |
| Can handle 500-page policy? | No: a 500-page document exceeds even 128K-token context windows | Yes: only the relevant 3-5 chunks are retrieved per query | Yes, but generating Q&A pairs for 500 pages and training costs significant time and money |
| Provides citations? | Possible with careful prompting ("Always cite the section number") but not guaranteed | Natural: the retrieved chunk itself is the citation and can be shown to the user | Generally not: knowledge is embedded opaquely in weights, so the model cannot point to its source |
| Output style consistency | Moderate: varies with how the user phrases their question | Moderate: same retrieval quality, but LLM generation still varies | High: style, format, and phrasing learned during training appear consistently in every response |

> **Common Misconception:** Many teams jump straight to fine-tuning because it sounds like the most "AI-native" solution.  In reality, for a task like the HR policy assistant, **RAG almost always outperforms fine-tuning** because policy documents change frequently (defeating fine-tuning's static knowledge) and citations matter (defeating fine-tuning's opaque knowledge).  Fine-tuning wins for style/format, not for factual recall of changing documents.

#### Questions to Work Through

4.  The HR policy document is 50 pages.  Prompting is eliminated by context window limits.  Between RAG and fine-tuning, which approach provides better freshness when a policy changes, and why does the answer matter operationally for an HR department?

   *Hint:* When a policy changes, which approach requires re-indexing (minutes) vs. retraining (hours/days)?  Think about the HR team's perspective: if the maternity leave policy changes tomorrow, how quickly can each approach reflect that change?

5.  A product manager argues: "Let's fine-tune the model on HR Q&A pairs so we don't need the vector database."  What hidden assumption does this argument make about the stability of the policy, and what happens at the next policy revision?

   *Hint:* The argument assumes the Q&A pairs will remain accurate indefinitely.  What happens when a policy changes and the fine-tuned model confidently gives the old (now wrong) answer?

6.  Describe a hybrid approach that combines RAG *and* fine-tuning.  What does each layer contribute, and what would justify the additional complexity and cost?

   *Hint:* Think of RAG as responsible for "what information to use" and fine-tuning as responsible for "how to format and present the answer."  A model fine-tuned on 2,000 HR Q&A pairs will always respond in the right format and tone; RAG ensures the specific policy content it uses is always current.

---

### LoRA: Fine-Tuning Without Full Weight Updates

Full fine-tuning updates every parameter in the model: for a 7B-parameter model, that is 7 billion floating-point numbers to store gradients for and update.  LoRA (Low-Rank Adaptation) sidesteps this by observing that the *update* to each weight matrix during fine-tuning tends to be low-rank: it lives in a small subspace of the full parameter space.

LoRA freezes all original weights and adds two small matrices per layer.  For a weight matrix $W \in \mathbb{R}^{d \times k}$, LoRA trains $A \in \mathbb{R}^{d \times r}$ and $B \in \mathbb{R}^{r \times k}$ where $r \ll d, k$ (typically $r = 4$, $8$, or $16$).  During inference, the layer computes $Wx + ABx$, the original output plus a learned correction.  Installation: `pip install peft transformers` (the PEFT library from Hugging Face implements LoRA).

### LoRA Illustrated

The diagram below shows how LoRA adds two tiny matrices (A and B) alongside the frozen original weight matrix W. Look for how small r is compared to d and k; that small rank is what makes LoRA's memory savings so dramatic.

```
Original Layer (frozen):          LoRA Correction (trained):
+---------------------+           +---+   +---------------------+
|                     |           | A |   |                     |
|   W  (d × k)        |    +      |   | × |   B  (r × k)        |
|   7B total params   |           |d×r|   |   r << d            |
`---------------------+           `---+   `---------------------+
  Gradient: not computed             Gradient: computed for A, B only
  Storage: unchanged                 Storage: ~0.1% of original
```

At rank $r = 8$ for a 7B model, LoRA trains roughly 4-8 million parameters instead of 7 billion, a 99.9% reduction in trainable parameters.  **QLoRA** combines LoRA with 4-bit quantization of the frozen base weights, enabling fine-tuning of 7B models on a single consumer GPU with 24 GB of VRAM.

**Real cost example:** Fine-tuning `llama3.1:8b` with QLoRA on 800 JSON-formatting examples using a rented Lambda Labs A100 instance costs approximately $1.60 (0.8 hours × $2/hour).  The resulting adapter file (the A and B matrices) is roughly 40 MB, compared to the 16 GB base model.

A team wants to fine-tune a 7B model to always respond in a structured JSON format for a data extraction task.  They have 800 labeled examples and a single A100 GPU (40 GB).  Which approach is most appropriate?

[( )] Full fine-tuning (update all 7B parameters), because format changes require updating every layer of the model to take effect consistently
[(X)] LoRA or QLoRA (freeze the base weights, train small adapter matrices), sufficient for format adaptation at a fraction of the compute cost
[( )] RAG; retrieve the JSON schema from a vector database at each call so the model always sees the expected format
[( )] Pre-training from scratch on JSON-formatted text corpora, since the base model has no concept of structured output

---

> Now that you understand both the decision logic and the cost structure, Part III gives you hands-on practice applying these ideas to real products and calculating concrete break-even points.

## Synthesis and Practice

In this part, you will apply the decision framework and cost model to real AI products you already use, calculate when self-hosted fine-tuning beats API calls on price, and practice constructing training datasets for a fine-tuning pipeline.

### Exercises

1.  *Approach audit.*  Identify three AI products you use regularly (a search assistant, a coding tool, a customer service bot).  For each, hypothesize whether the specialization is achieved via prompting, RAG, fine-tuning, or some combination.  List the evidence that informs your hypothesis.

   *What to do:* For each product, answer: Does it know about recent events?  (RAG or prompting.)  Does it refuse certain topics?  (Prompting/fine-tuning.)  Does it always output in a specific format?  (Fine-tuning.)  Does it cite sources?  (RAG.)

   *Starter hint:* GitHub Copilot likely uses a combination: a code-specialized base model (fine-tuning on code) plus in-context retrieval of your open files (prompting/RAG).  What evidence do you see for this in its behavior?

   *You've succeeded when:* You have a table with three products, a hypothesis for each, and at least two observable behaviors that support each hypothesis.

2.  *Cost model.*  You process 10,000 user queries per day.  Compare the monthly cost of: (a) GPT-4o via API at $5/1M input tokens with a 2,000-token average prompt vs. (b) a locally-hosted fine-tuned `llama3.1:8b` model on a rented A100 at $2/hour.

   *What to do:* Calculate (a) monthly API cost: 10,000 queries/day × 30 days × 2,000 tokens × ($5 / 1,000,000).  Calculate (b) monthly GPU cost: 720 hours/month × $2/hour.  Add the one-time training cost.  Find the break-even query volume.

   *Starter hint:* At 10,000 queries/day, GPT-4o API cost ≈ $3,000/month.  A dedicated A100 ≈ $1,440/month.  But what happens at 500 queries/day?  The A100 is always on; the API charges per query.  Build a simple Python calculation: `api_cost = queries_per_day * 30 * avg_tokens * price_per_token`.

   *You've succeeded when:* You have a break-even query volume (queries/day at which the two approaches cost the same) and a recommendation for a startup with 500 queries/day vs. 50,000 queries/day.

3.  *LoRA parameter count.*  A transformer layer has a query projection matrix $W_Q \in \mathbb{R}^{4096 \times 4096}$. If LoRA is applied with rank $r = 16$, how many parameters does LoRA add to this single matrix (count $A$ and $B$ together)?  What fraction of the original matrix does this represent?

   *What to do:* $A$ has shape $4096 \times 16$ and $B$ has shape $16 \times 4096$. Count total LoRA parameters.  Original $W_Q$ has $4096 \times 4096 = 16{,}777{,}216$ parameters.

   *Starter hint:* $|A| = 4096 \times 16 = 65{,}536$. $|B| = 16 \times 4096 = 65{,}536$. Total LoRA = $131{,}072$. Fraction = $131{,}072 / 16{,}777{,}216 \approx 0.78\%$. A real 7B model has ~32 such layers, each with multiple projection matrices (Q, K, V, O).

   *You've succeeded when:* You have the exact parameter counts and fractions, and you can explain why this means LoRA training needs ~100x less GPU memory than full fine-tuning.

4.  *Dataset construction.*  You are fine-tuning a model to extract structured fields (name, date, amount, counterparty) from procurement contracts.  Design a data collection strategy for 500 training examples.

   *What to do:* Identify (a) the source of raw documents, (b) how you generate ground-truth labels, and (c) what quality checks you apply before training.

   *Starter hint:* Format each training example as a JSON pair: `{"input": "<contract text>", "output": {"name": "Acme Corp", "date": "2024-03-15", "amount": 45000.00, "counterparty": "Ursinus College"}}`.  Quality checks: verify all four fields are present in every example; confirm dates parse correctly; have a human review 10% of examples for accuracy.

   *You've succeeded when:* You have a written data collection plan with source, labeling method, quality checks, and a 5-example sample dataset in the correct format.

---

### Reflection Prompt

*Personal:* Think of a skill you had to learn from a book vs. one you learned by doing.  How does that map to the RAG (look it up every time) vs. fine-tuning (internalize it permanently) distinction?  When is "always looking it up" actually better than "memorizing it"?

*Technical:* Fine-tuning bakes knowledge permanently into weights, making the model's reasoning opaque.  RAG keeps knowledge external and attributable, but adds a pipeline that can fail in its own ways.  As AI systems are deployed in high-stakes domains (medicine, law, finance), which property matters more (opaque internalized knowledge or transparent retrieved knowledge) and who should get to decide that for a given deployment?

*Societal:* LoRA makes fine-tuning accessible to individuals and small organizations who previously could not afford it.  A chemistry student can now fine-tune an open-weight model on synthesis procedures; a political campaign can fine-tune a model on persuasive messaging.  What new capabilities does democratized fine-tuning enable that are beneficial, and what risks does it introduce that did not exist when fine-tuning required millions of dollars?

---

-> Coming Up Next: Now that you understand when to fine-tune, the next module explores the landscape of open-weight local models (Llama, Mistral, Phi, Gemma) and how to choose the right one for your hardware and task, including how quantization lets you run a 7B model on a laptop.

---

---

# Extension: Synthetic Data (self-paced)

Optional, and independent of the parts above.  Once you start evaluating a retrieval pipeline you run short of test data, and the obvious move is to have a model generate more.  That move is more dangerous than it looks, because the evaluation and the thing being evaluated end up sharing an author.  Read this before you generate a test set you intend to trust.

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Synthetic Data** | Data that is artificially generated rather than collected from real-world events or people, created by rules, simulation, or generative AI models | GPT-3.5 generating 52,000 instruction-response pairs to train Stanford's Alpaca model at a cost of ~$500, replacing expensive human labeling |
| **Instruction Tuning** | Fine-tuning a language model on thousands of (instruction, response) pairs so it learns to follow natural language commands rather than just predict the next token | Training a base model on synthetic examples like "Summarize the following paragraph: ..." and the expected response |
| **Model Collapse** | The phenomenon where models trained on AI-generated data across multiple generations progressively lose the rare and diverse patterns found in real human data, like a photocopy of a photocopy getting blurrier each time | After 10 generations of synthetic-to-synthetic training, models produce only the most common, central outputs and fail on unusual inputs |
| **Self-Instruct** | A pipeline in which a model uses a small seed set of human-written examples to generate new instruction-response pairs, then uses those to generate more, bootstrapping a large dataset from a small one | Stanford Alpaca generated 52K examples from 175 human seeds using this approach |
| **Evol-Instruct** | An approach to synthetic data generation that takes simple instructions and iteratively rewrites them to be harder, more constrained, or more nuanced, evolving easy examples into hard ones | Transforming "Write a function that sorts a list" into "Write a function that sorts a list without any built-in sort functions, in O(n log n) time, with an explanation of the algorithm" |
| **Sim-to-Real Gap** | The difference in difficulty between a task in a controlled simulation and the same task in messy real-world conditions; data generated in clean simulation may not prepare an agent for real-world variation | An agent trained on clean, synthetic customer service dialogues that struggles with real user queries that include typos, implicit assumptions, and mid-conversation topic changes |

---

### Why Synthetic Data?

The key insight behind synthetic data is that data labeling is often the bottleneck, not compute.  A radiologist who can label 20 chest X-rays per day costs ~$300,000 per year and produces roughly 5,000 labeled examples annually.  A single GPU running a generative model can produce thousands of synthetic medical descriptions per hour.  The question is not whether this is useful (it obviously is), but whether synthetic data is a complete substitute for real data, a dangerous shortcut, or something in between.  As you will see in this activity, the answer depends entirely on what you are generating, how carefully you filter it, and whether you have any real data to validate against.

#### The Data Scarcity Problem

High-quality labeled data is the fuel of modern machine learning, but it is expensive, slow, or sometimes impossible to obtain:

- **Medical data** requires expert annotation by radiologists, pathologists, or clinicians; IRB approval; and patient de-identification.  A single labeled CT scan dataset may cost hundreds of thousands of dollars to produce.
- **Legal data** is often confidential and jurisdiction-specific.  Training a legal reasoning model requires annotated case law that cannot be freely shared even among researchers.
- **Specialized domains** such as semiconductor design, drug interaction prediction, and rare language translation have few practitioners and even fewer labeled examples.
- **Future scenarios** do not yet exist: you cannot collect data about how an agent should handle a new type of cyberattack before that attack type is publicly known.

**Synthetic data** is artificially generated data.  It can be generated by hand-coded rules, by physics simulations, or (increasingly) by generative AI models.  The goal is to fill gaps where real data is scarce, expensive, or impossible to obtain.

#### Four Use Cases for Synthetic Data

| Use Case | What Synthetic Data Generates | Real-World Benefit | Key Risk | Example in Practice |
|----------|------------------------------|-------------------|-----------|--------------------|
| **Instruction tuning** | Diverse (instruction, response) pairs covering many task types at scale | Scale fine-tuning to produce capable assistant models without expensive human labeling for each example | The model learns the generator model's biases, errors, and blindspots; mode collapse reduces diversity over iterations | Stanford Alpaca (2023), 52,000 examples from GPT-3.5 at a cost of ~$500 |
| **Adversarial robustness** | Edge-case prompts and scenarios the model would rarely encounter in normal operation | Better robustness to unusual inputs, jailbreak attempts, and distribution shift | Synthetic adversarial examples may not cover the specific adversarial strategies real attackers actually use | Red-teaming augmentation in model safety pipelines |
| **Privacy preservation** | Statistically similar fake records that replace real patient, user, or financial records | Share sensitive datasets safely in research collaborations without exposing individual records | Residual privacy leakage if the synthetic distribution closely mirrors specific real records | Synthetic patient record generation for medical AI research |
| **Simulation environments** | Agent training scenarios such as customer service dialogues, code review sessions, or tool-use chains | Scale agent training to millions of scenarios without real user interactions or risks | Sim-to-real gap: the agent learns behaviors that work in clean simulation but fail on the messy variation in real deployments | OpenAI Codex training included synthetic verified code problems |

#### Questions to Work Through

**Question 1.**  Consider this thought experiment: you use an AI model (generation 1) to generate synthetic training data.  You train a new model (generation 2) on that data.  You use generation 2 to generate more synthetic data.  You train generation 3.  Can you repeat this indefinitely and keep improving, or does something eventually go wrong?

> *Hint:* Think about what information is preserved and what is lost at each step.  The generation-1 model's outputs capture the common, high-probability patterns in its training data well, but rare patterns (unusual phrasing, low-frequency facts, edge cases) appear only occasionally in its outputs.  When generation 2 trains on generation 1's outputs, it sees fewer examples of those rare patterns.  Generation 3 sees even fewer.  Each generation drifts toward the most common, central outputs and loses the tails of the distribution.  Is this a problem?  It depends on what the rare patterns represent: if they are noise, losing them is fine; if they are linguistically or factually important edge cases, losing them is harmful.

---

**Question 2.**  Shumailov et al. (2023) describe "model collapse", a phenomenon observed when models are trained on AI-generated data across multiple generations.  What specific property of real-world data distributions do they argue is progressively lost?  Why does this matter for the quality of a model trained many generations deep in a synthetic pipeline?

> *Hint:* The property being lost is the **tails of the distribution**: the rare, unusual, low-frequency patterns.  Real human language and real-world scenarios include enormous diversity: people with unusual accents, unusual names, unusual situations, unusual combinations of facts.  A model trained on real data sees this diversity.  A model trained on synthetic data generated by another model sees only what that model generates frequently.  After several generations, the model becomes a caricature: it handles the common cases well but is brittle on anything unusual.  For an agent deployed in the real world, "unusual" is exactly what you need to handle, because it is often the unusual cases that matter most (rare medical conditions, unusual legal situations, edge-case security scenarios).

---

**Question 3.**  Name one domain where using synthetic data for AI training is clearly acceptable with low risk and high benefit.  Name one domain where it is clearly problematic with high risk of harm from distribution mismatch or bias amplification.  Justify both choices with specific reasoning.

> *Hint:* Clearly acceptable: generating synthetic examples for a game-playing agent where the simulation is the real environment and there is no real-world deployment risk; the agent will only ever operate in the game world.  Clearly problematic: generating synthetic medical training data for a diagnostic AI where the synthetic data reflects the biases and gaps of the generator model, and those biases map onto real patient harm.  The key distinction is: how severe are the consequences of distribution mismatch?  In a game, the worst case is the agent loses.  In medicine, the worst case is a misdiagnosis.

---

### Generating Synthetic Instruction Data

The most widely used form of synthetic data for LLM fine-tuning is **instruction-following data**: pairs of (instruction, response) that teach a model to respond helpfully to natural language requests rather than simply predicting the next token in a document.

#### Self-Instruct (Wang et al., 2022)

Self-Instruct is the pipeline behind several influential open-source instruction-tuned models.  It works as a bootstrapping loop (a self-improving cycle where each iteration generates new data that feeds the next iteration, growing a large dataset from a small starting set):

1.  Start with a **seed set** of roughly 175 human-written instruction examples covering a range of task types.
2.  Prompt a large model (originally GPT-3) to generate new instructions by analogy with randomly sampled examples from the seed set: "Here are 8 example instructions.  Generate 4 more that are different in task type and topic."
3.  For each new instruction, prompt the same model to generate a high-quality response.
4.  Apply **quality filters**: remove exact duplicates, near-duplicates (by cosine similarity), toxic content, and low-quality or incoherent responses.
5.  Add the surviving instances to the growing dataset.
6.  Return to step 2, now sampling from the full (and growing) dataset rather than just the original seeds.

Stanford's **Alpaca** model (2023) applied this pipeline: it used GPT-3.5 to generate 52,000 instruction-response pairs from 175 human-written seeds, at a cost of approximately $500 in API fees.  The resulting model was competitive with early GPT-3.5 on many tasks despite being 10× smaller, a remarkable demonstration of the efficiency of synthetic instruction tuning.

#### Evol-Instruct (WizardLM, Xu et al., 2023)

Evol-Instruct takes a different approach: rather than generating new instructions from scratch, it **evolves** existing simple instructions into progressively harder ones through iterative rewriting.  Each evolution step applies one of several transformations:

- **Add constraints:** "Write a function that sorts a list" -> "Write a function that sorts a list without using any built-in sorting functions or the sorted() built-in, in O(n log n) time."
- **Deepen complexity:** "Explain photosynthesis" -> "Explain photosynthesis at the biochemical level, addressing specifically whether recent research on quantum coherence in light-harvesting complexes changes the classical explanation."
- **Require multi-step reasoning:** Single-step questions become chains of reasoning with explicit intermediate conclusions required.

The result is a dataset with a natural difficulty gradient, which is particularly valuable for training models to handle challenging queries rather than just easy ones.

#### Quality Filtering Pipeline

The diagram below shows how raw generated pairs flow through a series of filters before being added to the training set.  Read it left-to-right: each arrow represents a filter that reduces the quantity of data but improves its quality; the loop at the bottom is where generation and filtering cycle repeatedly.

```
seed_instructions
    -> generate_variants(LLM)
    -> filter_quality(judge_LLM_or_rules)
    -> deduplicate(exact + semantic_similarity)
    -> measure_diversity(embedding_spread)
    -> add_to_dataset
    -> loop
```

**Quality filter criteria, each generated pair must pass all of these:**

- **Length check:** The response is not trivially short (one word) or obviously padded with filler content.
- **Coherence check:** The response actually addresses the instruction rather than drifting to an unrelated topic.
- **Non-duplication check:** Cosine similarity (a number between 0 and 1 measuring how semantically similar two pieces of text are; values above 0.9 mean the texts are nearly identical in meaning) to existing dataset items is below a threshold (typically 0.7-0.8) so the dataset remains diverse.
- **Safety check:** The instruction and response do not contain toxic, harmful, or inappropriate content.

> **Common Misconception:** Generating more synthetic data is not the same as generating *better* synthetic data.  A common error is to generate enormous quantities of synthetic instruction data and assume that more is always better.  In practice, quality filters are more important than quantity: a dataset of 10,000 high-quality, diverse, well-filtered examples typically produces better fine-tuning results than 100,000 low-quality or highly redundant examples.  The Alpaca model demonstrated this: 52,000 carefully generated examples from a seed of 175 produced a capable model.  Simply running the generation loop for 10 more hours to produce 500,000 examples would not have produced a model 10× better, and might have introduced more mode collapse.

#### Questions to Work Through

**Question 4.**  If you use GPT-4 to generate synthetic instruction-tuning data and then fine-tune a smaller model on that data, you are arguably distilling GPT-4's knowledge and reasoning patterns into the smaller model.  But are you also distilling GPT-4's biases, factual errors, and blindspots?  How would you detect whether this happened?

> *Hint:* GPT-4 has documented biases: it may handle certain demographic groups differently in certain contexts, may have gaps in knowledge of non-English languages and non-Western culture, and may generate factually wrong information with high confidence in low-frequency topic areas.  If your fine-tuning data was generated entirely by GPT-4 and your fine-tuned model shows the same systematic patterns of error or bias that GPT-4 shows (making the same factual mistakes, having the same gaps), that is strong evidence of bias distillation.  How would you specifically test for this?  What reference dataset of known-correct, diverse, and culturally representative examples would you compare against?

---

**Question 5.**  How would you measure whether your synthetic instruction dataset is sufficiently diverse to train a well-rounded model?  Describe at least two concrete metrics you could compute before starting fine-tuning, and explain what threshold or warning sign would lead you to generate more data or adjust your generation pipeline.

> *Hint:* (1) **Embedding-space coverage**: embed all instructions using a sentence embedding model; compute the average pairwise cosine distance.  Low average distance (instructions cluster tightly) means low diversity; the generation pipeline is producing variations on the same few themes.  A diverse dataset should show a spread of embedding clusters covering many task types.  (2) **Task-type distribution**: categorize each instruction by task type (question answering, summarization, code generation, translation, classification, etc.) and measure the entropy of the distribution.  A dataset dominated by one or two task types will produce a model that is strong on those types and weak on others.  What fraction of your target capability surface should each task type cover?

---

**Question 6.**  Generating more synthetic data is cheap once the pipeline is set up; API costs are relatively low and generation can run in parallel.  At what point do you get diminishing returns from adding more synthetic examples to a training set?  What factors determine that threshold?

> *Hint:* Diminishing returns set in when: (1) the new synthetic examples are not adding new patterns; they are high-similarity duplicates of existing examples, adding no new information to the model; (2) the quality of new examples decreases as the generation loop continues (later generations of the self-instruct loop tend to produce lower-quality examples because the model starts generating less natural instructions); (3) the model has already saturated the capability that the synthetic data is targeting; additional examples of the same task type produce no measurable improvement on that task.  The threshold depends on the target capability's complexity: simple tasks saturate quickly (the model can summarize after a few thousand examples); complex multi-step reasoning tasks may benefit from hundreds of thousands of diverse examples.

---

#### Multiple Choice Question

A research team trains a model entirely on AI-generated text.  They then use that model to generate more training data for the next model version and repeat this process 10 times.  The most likely outcome, based on current research, is:

[[ ]] Each generation produces a progressively better model because the LLM pipeline iteratively refines and distills errors; more cycles means higher quality, like proofreading a document repeatedly
[[ ]] The models converge to a stable quality level after a few generations because the distribution self-corrects, similar to how a population reaches equilibrium
[[x]] Model quality degrades over generations as rare but important patterns in the real-world data distribution are progressively lost from the synthetic outputs, a phenomenon called model collapse
[[ ]] The model learns to generate more creative and diverse output as it samples from an expanding, self-improving distribution; synthetic training data inherently increases diversity with each generation

> **Why this answer?**  Shumailov et al. (2023) demonstrated model collapse empirically: when models are trained on outputs of previous models, the tails of the distribution (rare but important patterns) are systematically underrepresented in the training data of each subsequent generation.  The model becomes progressively more "average," handling common cases well but becoming brittle and unreliable on unusual inputs.  This is why real-world data anchoring is critical: mixing some proportion of real human-generated data into each generation's training set significantly slows or prevents collapse.

---

### Synthetic Data for Agent Training

Instruction-response pairs are the simplest form of synthetic data for LLMs, but agents require something more complex: **trajectories**, sequences of observations, decisions, tool calls, and outcomes that represent a complete task-solving episode.

#### Synthetic Trajectories

An agent trajectory is a sequence of tuples: `(observation₁, action₁, result₁, observation₂, action₂, result₂, ...)` continuing until the task is complete or abandoned.

Generating synthetic trajectories allows agent training to scale beyond what human demonstration collection alone can support:

- **Verified code problems:** Generate a programming problem, generate a candidate solution, execute the solution in a sandboxed environment, and use pass/fail against test cases as ground-truth labels.  OpenAI's Codex training pipeline included synthetic problems with verified solutions generated this way, at a scale impossible to achieve with human demonstrators.
- **Customer service dialogues:** Generate a synthetic customer persona, a synthetic initial complaint or question, and a range of synthetic agent responses.  Have a judge model rate each response on helpfulness and policy compliance.  This provides training signal without accessing real user data that might contain PII.
- **Tool-use chains:** Generate tasks that require specific sequences of tool calls (look up a weather forecast, then look up a transit schedule, then combine them to recommend departure time), execute those chains in a sandboxed environment, and label complete trajectories by whether the task was accomplished correctly.

#### Synthetic Evaluation Sets: The "LLM Generates Its Own Exam" Pattern

A practical technique for rapidly building evaluation benchmarks for new domains:

1.  Prompt a capable model: "Generate 20 challenging questions about [domain] that require [specific capability].  For each question, also provide the correct answer."
2.  Filter the generated pairs for quality, accuracy, and non-duplication.
3.  Use the resulting pairs as a benchmark to evaluate a fine-tuned model on that domain.

**Critical pitfall, self-evaluation inflation:** A model performs systematically better on questions it generated than on questions generated by humans or by a different model.  The model "knows" the style and framing of its own questions and can answer them more easily.  This inflates apparent capability on the synthetic benchmark compared to real-world performance.  Always validate a synthetic evaluation set against a sample of real human-written questions in the same domain before relying on it for deployment decisions.

#### Questions to Work Through

**Question 7.**  If you fine-tune a model on synthetic data, then use that fine-tuned model to generate more synthetic data for the next training round, and repeat: how do you prevent the model from progressively reinforcing its own errors?  Describe at least one specific structural safeguard you would build into the pipeline.

> *Hint:* The core danger is error amplification: if the fine-tuned model has a systematic error (always recommending the wrong medication dose, always getting a specific logic pattern wrong), it will generate synthetic data that reflects that error, and the next model will learn the error even more strongly.  Structural safeguards include: (1) **Real data anchoring**: always include a fixed proportion of human-verified real data in each training round, so the model cannot drift arbitrarily far from reality; (2) **Verification gating**: for domains where outputs can be automatically checked (code that runs, math answers that can be verified, logical proofs that can be checked), only include synthetic examples in the next training round if the output passes an automatic correctness check; (3) **Diversity filtering**: use embedding-based deduplication at each round to prevent the pipeline from collapsing to a narrow mode.

---

**Question 8.**  What is the difference between **synthetic** data and **augmented** data?  Give a concrete example of each in the context of a text-classification task for classifying customer support tickets by urgency.  Does the distinction matter for how you evaluate the resulting model?

> *Hint:* **Augmented data** is derived from real data through transformations that preserve the label: taking a real support ticket classified as "urgent" and paraphrasing it, translating it, or adding typos.  The result is a new example that is artificial, but it is grounded in a real human-written ticket with a verified label.  **Synthetic data** is generated from scratch without reference to any specific real example: prompting a model to "write an example urgent customer support ticket about a missed delivery."  The distinction matters for evaluation because: if you evaluate on augmented data, you are testing whether the model generalizes to variations of real examples; if you evaluate on synthetic data, you are testing whether the model handles the generator's idea of what an urgent ticket looks like, which may not match real urgent tickets.

---

**Question 9.**  Design a quality filter for synthetic instruction data.  Specify exactly three criteria that every generated (instruction, response) pair must satisfy before it is added to the training set.  For each criterion, explain how you would test it automatically and what failure rate you would tolerate before revising the generation pipeline.

> *Hint:* Criterion 1: **Relevance**, the response must address the instruction rather than drift to an unrelated topic.  Test automatically by checking whether the top 3 most important noun phrases from the instruction appear in the response (simple heuristic) or by embedding both instruction and response and checking cosine similarity (more robust).  Tolerate at most 5% failure rate before revisiting the generation prompt.  Criterion 2: **Minimum length**, the response must be at least 50 characters and at most 2,000 characters for the task types in your dataset.  Test by character count.  Tolerate at most 10% failure rate (responses that are too short are often low-quality; responses that are too long may be padded).  Criterion 3: **Non-toxicity**, the instruction and response must not contain harmful, discriminatory, or violating content.  Test using a toxicity classifier.  Tolerate 0% failure rate; any toxic generation indicates a problem with the generation prompt that must be fixed immediately.

---

### Exercises

**Exercise 1.**

*What to do:* Using a local model or API access, generate 20 synthetic instruction-tuning examples for a domain of your choice (options: cooking, Python debugging, academic writing, local Ursinus College history, or anything else that interests you).  Apply at least 2 quality filters from the pipeline described in Model 2.

*Starter hint:* Use this generation prompt structure: "You are generating instruction-tuning data for a language model assistant.  Generate 5 (instruction, response) pairs for the domain of [your domain].  Each instruction should be a specific, realistic task a user might ask.  Each response should be accurate, helpful, and 2-4 sentences long.  Format your output as a JSON array."  Run this prompt 4 times to get 20 candidates.  Then apply your filters: (1) remove any response shorter than 50 words; (2) remove any pair where the response does not mention any key term from the instruction.

*You've succeeded when:* You know how many of your 20 generated examples passed both filters, you have read the examples that failed and identified the most common failure mode, and you have written a one-paragraph reflection on what the failure pattern tells you about the limitations of this generation approach.

---

**Exercise 2.**

*What to do:* Research the original Stanford Alpaca dataset (2023).  Investigate its generation, its known problems, and how successor datasets addressed those problems.

*Starter hint:* Start with the Alpaca GitHub repository and the Stanford CRFM blog post about the project.  Then search for "Alpaca limitations" or "instruction tuning quality critique 2023."  Look specifically for: (1) What specific quality issues were found in the Alpaca dataset after release (factual errors, low diversity in certain task types, specific language bias)?  (2) How did Alpaca-GPT4 (which used GPT-4 as the generator instead of GPT-3.5) address those issues?  (3) How did the OpenHermes dataset go further, and what tradeoffs did it introduce?

*You've succeeded when:* Your response answers all three questions with specific details (not vague generalities), cites at least three sources, and concludes with your own assessment: given what you now know about Alpaca's limitations, would you use it as the sole fine-tuning dataset for a production application?  Why or why not?

---

**Exercise 3.**

*What to do:* Choose a specialized agent you care about (in healthcare, legal assistance, scientific research, or education) and design a synthetic data generation pipeline for training or fine-tuning that agent.

*Starter hint:* For a healthcare agent that helps patients prepare questions for doctor appointments, your pipeline might look like: (1) generate synthetic patient profiles (age range, chronic conditions from a controlled list, medication list from drug databases); this avoids using real patient data; (2) generate synthetic "preparing for appointment" instruction-response pairs where the instruction is a patient's concern and the response is the kind of question they should ask their doctor; (3) verify each response against a clinical terminology check (does it use accurate medical language?); (4) filter for empathetic tone using a sentiment classifier.  What are the three biggest risks in this specific pipeline?

*You've succeeded when:* Your pipeline design specifies: (a) the type of synthetic data to generate with a concrete example; (b) the generation pipeline in pseudocode or a labeled diagram; (c) your quality filtering approach with at least 2 specific filters; and (d) the 3 biggest risks and your mitigation strategy for each.

---

### Reflection Prompt

**Personal:** Think about content you have created: social media posts, papers, code, artwork.  If that content was scraped and used to generate synthetic training data for an AI model, which in turn trained another model, and so on for 10 generations, what of your original "voice" or style would remain after 10 iterations?  Does that matter to you, and why or why not?

**Technical:** Using AI to generate training data for AI creates a feedback loop.  The first generation is trained on human-created data.  The second is trained partly on AI-generated data.  The tenth generation may be trained almost entirely on AI-generated data.  At what point does "synthetic" become indistinguishable from "real"?  If a synthetic dataset is statistically identical to a real one on every measurable dimension, does the distinction still matter?  What might be lost in the unmeasured dimensions, and who would notice?

**Societal:** High-quality labeled data has historically been expensive, which meant that only well-resourced labs and companies could train capable AI systems.  Synthetic data generation is cheap, which could democratize AI training.  But synthetic data pipelines also require access to capable generator models (which are themselves owned by a small number of companies) and significant compute.  Does synthetic data democratize AI, or does it just shift the barrier from "who can label data" to "who can afford API access to generate data"?  What would democratized AI training require?

Write at least 200 words addressing at least two of the three levels above.  Please have your Reflector ready to share your group's key idea during class discussion.

---

-> Coming Up Next: In the next activity, we examine what it means for AI to be "creative", and whether creativity requires something that generative models fundamentally cannot have.
