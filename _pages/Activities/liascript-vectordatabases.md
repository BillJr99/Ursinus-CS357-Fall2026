<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-vectordatabases.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-vectordatabases.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Vector Databases: How Agents Search for Meaning

A RAG pipeline is only as fast as its retrieval step. An embedding model turns every chunk of text into a high-dimensional float array — commonly 1536 numbers — and a **vector database** stores millions of those arrays so that the nearest neighbors of any query can be found in milliseconds rather than seconds. This module unpacks **the approximate nearest-neighbor problem $\rightarrow$ distance metrics and when to use them $\rightarrow$ the full retrieval pipeline $\rightarrow$ failure modes you will encounter in practice**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| Embedding | A list of numbers (a vector) that encodes the meaning of text, so that similar meanings produce similar number lists. | The sentence "dog bites man" and "canine attacks person" produce vectors that are very close together in 1536-dimensional space. |
| Vector Database | A specialized database optimized for storing millions of these number lists and finding the ones closest to a query vector in milliseconds. | Chroma, Qdrant, Pinecone — each stores embeddings and returns the top-k nearest neighbors on demand. |
| Approximate Nearest Neighbor (ANN) | A fast search strategy that finds vectors very close to the query, accepting a small chance of missing the single absolute closest match in exchange for huge speedups. | HNSW returns results 100–1000x faster than checking every stored vector, with ~95% recall in practice. |
| Cosine Similarity | A distance measure that ignores how long each vector is and measures only the angle between them — capturing "same direction = same meaning." | Two sentences about "stock market crashes" score high cosine similarity even if one is short and one is long. |
| Metadata Filter | A structured condition (like a SQL WHERE clause) applied alongside the vector search to restrict results by category, date, author, or other fields. | Search for documents about "GLP-1 drugs" published after 2024-01-01 in the "clinical" collection. |
| Hybrid Search | A search strategy that combines dense embedding retrieval (finds semantically similar text) with sparse keyword retrieval (finds exact word matches) and merges the two ranked lists. | Searching for "FDA 21 CFR Part 11" benefits from both: semantics to find related regulations, exact match to find the specific part number. |

---

# Part I: Why Brute Force Fails

In this part, you will see why checking every vector in a million-document database is computationally infeasible and how two approximate nearest-neighbor algorithms — HNSW and IVF — solve the problem through clever indexing.

## 1. The Scale Problem

Searching a vector database is like finding the most similar song in a music library — not by song title, but by how it *sounds*. If you had 1 million songs and had to listen to each one to decide which is most similar to your query, it would take forever. ANN indexes are the equivalent of organizing songs by genre, tempo, and key so you can jump straight to the right neighborhood.

An embedding vector for a single sentence is a point in $\mathbb{R}^{1536}$. At query time, a RAG system must find the $k$ stored vectors closest to the query vector. The naive approach is to compute the distance from the query to every stored vector. For 1 million documents, each at 1536 dimensions, that is $1536 \times 10^6 \approx 1.5 \times 10^9$ floating-point operations per query — enough to take several seconds on a single CPU, unacceptable for an interactive assistant.

**Approximate nearest-neighbor (ANN) search** accepts a small chance of missing the true nearest neighbor in exchange for a 100x to 1000x speedup. Two algorithms dominate production systems:

- **HNSW (Hierarchical Navigable Small World — an approximate nearest-neighbor index that organizes vectors into a multi-layer graph so search can navigate quickly from coarse to fine-grained neighborhoods):** builds a multi-layer graph where each node connects to its approximate nearest neighbors. Search navigates from a coarse top layer downward, greedily jumping toward the query. Think of it as a subway map where express lines get you close quickly, then local stops get you to the exact station.
- **IVF (Inverted File Index):** partitions the vector space into $n$ clusters (Voronoi cells) at index time. At query time only the nearest few cluster centroids are searched. Think of it as dividing a library into sections: you check the "Science" section, not every shelf.

---

## Model 1: Distance Metrics

Not all distance functions measure the same thing. Choose the wrong one and semantically similar documents rank below dissimilar ones. Think of this like choosing the right ruler: a protractor measures angles, a tape measure measures length — both are "distance" tools but answer different questions.

| Scenario | Best Metric | Why | When to Use |
|---|---|---|---|
| Finding semantically similar sentences in a text retrieval system | Cosine similarity | Direction encodes meaning; vectors from the same model are already unit-normalized in most libraries, so magnitude differences are irrelevant. | Default choice for all text embedding retrieval — use this unless you have a specific reason not to. |
| Finding documents of similar "importance" where magnitude carries signal | L2 (Euclidean) distance | Magnitude differences are meaningful; two vectors far from the origin but close in angle are genuinely different in quantity or intensity, not just topic. | Image embeddings where pixel intensity matters; word count or frequency embeddings where raw size is meaningful. |
| Maximum inner product search for recommendation | Dot product | Relevance decomposes as magnitude × angle; used when popularity or frequency should interact with semantic similarity. | Recommendation systems where a popular item (high magnitude) should rank higher than an obscure but equally relevant item. |
| Comparing images embedded by a CLIP model with known unit norms | Cosine or dot product (equivalent when norms are 1) | Normalization makes them identical; use whichever the library exposes natively to avoid unnecessary computation. | Any embedding model that explicitly states it returns unit-normalized vectors, including `text-embedding-3-small` and `nomic-embed-text`. |

### Critical Thinking Questions

1. Most text embedding models (such as `nomic-embed-text` and OpenAI `text-embedding-3-small`) return L2-normalized vectors, meaning every vector has magnitude 1. Show algebraically that for unit vectors, cosine similarity and dot product are identical. Why does this simplification matter for implementation?

   *Hint:* Cosine similarity is defined as $\frac{u \cdot v}{||u|| \cdot ||v||}$. What happens to the denominator when both vectors have magnitude 1?

2. You index 50,000 legal briefs and 50,000 social media posts in the same collection. A query about "contract breach" retrieves a mix of both. What property of the embedding space caused this, and which metadata filter would you add to the ANN query to fix it?

   *Hint:* Both document types use the word "breach" but in very different contexts. The embedding model was trained on mixed text. What structured field (stored alongside the vectors, not in the vectors) would let you restrict results to one document type?

3. HNSW builds its graph at index time. What is the trade-off when you set the number of neighbors per node very high versus very low? Consider index-build time, query time, and recall.

   *Hint:* More neighbors per node means more edges in the graph. During search, more edges means more paths to explore. During index construction, more edges means more distance calculations per inserted node.

---

> With the distance metrics and indexing algorithms understood, Part II traces a complete RAG query from the user's question all the way to the LLM's answer — step by step, showing where each type of failure can occur.

# Part II: The Retrieval Pipeline

In this part, you will trace a complete RAG query through six pipeline steps — embedding, ANN search, metadata filtering, and LLM generation — and learn to diagnose which step is responsible when the answer comes out wrong.

## 2. From Query to Answer

Every RAG query traverses a fixed sequence of steps — like an assembly line where each station transforms the work piece and hands it to the next. Understanding who owns each step is essential for debugging: when the answer is wrong, you need to pinpoint whether to blame the embedding model, the ANN index, the metadata filter, or the language model.

## Model 2: Pipeline Tracing

| Step | Component | Input | Output | What Can Go Wrong Here |
|---|---|---|---|---|
| 1. Query arrives | Application layer | Raw user question typed by the user | Plain text string | Query is ambiguous, misspelled, or in a different language than the indexed documents. |
| 2. Query is embedded | Embedding model (e.g., `nomic-embed-text` — install: `ollama pull nomic-embed-text`) | Text string | Float array (1536-dim) | Using a different embedding model than was used at index time causes a "dialect mismatch" — vectors are incomparable. |
| 3. ANN search | Vector database index (HNSW or IVF) | Query vector, $k$ (how many results to return) | Candidate document IDs with distances | If $k$ is too small, the correct document is excluded before the filter even runs. |
| 4. Metadata filter applied | Vector database filter engine | Candidate IDs, filter expression (e.g., `{"year": {"$gte": 2024}}`) | Filtered subset of IDs | Overly strict filters remove the correct document; overly loose filters let irrelevant documents through. |
| 5. Top-$k$ documents returned | Vector database | Filtered IDs | Document text + metadata | If chunks are too long, they waste context window space; if too short, they lack the context the LLM needs to answer. |
| 6. LLM generates with docs in context | Language model (e.g., `claude-sonnet-4-5`, `llama3.1:8b`) | Prompt = system instructions + retrieved chunks + user question | Answer string | LLM ignores the retrieved text and hallucinates from parametric memory; "lost in the middle" effect buries the relevant chunk. |

> **⚠️ Common Misconception:** Many beginners assume that if the LLM gives a wrong answer, the problem must be with the LLM itself. In practice, **the retrieval step fails far more often than the generation step**. A perfect LLM cannot produce a correct answer if Step 3 or 4 returned the wrong documents. Always check what was actually retrieved (Step 5's output) before debugging the LLM.

### Critical Thinking Questions

4. A user asks "What were the 2024 FDA guidelines on GLP-1 drugs?" Your index was built in January 2024 and the guidelines were published in September 2024. At which step does the failure occur? What is the fix, and what is its operational cost?

   *Hint:* The failure happens at Step 3 — the correct document was never indexed, so ANN search cannot return it. The fix involves re-running the indexing pipeline. How often would you need to do this for a regulatory database?

5. Your system retrieves the correct documents at step 5, but the LLM's answer contradicts them. Which step is at fault? What experiment would you run to confirm this before changing the prompt?

   *Hint:* Before changing anything, print the exact retrieved chunks and compare them to the LLM's answer. If the chunks clearly contain the correct answer and the LLM ignores them, you have isolated Step 6 as the culprit.

6. Metadata filters at step 4 operate *after* ANN search, not before. Why is pre-filtering expensive, and what architectural pattern (called "filtered ANN") is used by databases like Qdrant to make it efficient?

   *Hint:* Pre-filtering means scanning the entire metadata table before doing any vector math. Qdrant's filtered ANN uses a different strategy: it builds separate HNSW graphs per metadata partition so that filters can be applied during graph traversal rather than after it.

---

> Having traced every step of the retrieval pipeline, Part III surveys the major vector database options and catalogs the four failure modes you will encounter most often in production — so you can recognize and fix them quickly.

# Part III: The Ecosystem and Failure Modes

In this part, you will compare six production vector databases by architecture and operational profile, and study the four most common retrieval failure signatures — semantic mismatch, hallucination, stale index, and "lost in the middle" — so you can diagnose them from their symptoms.

## 3. Choosing a Vector Database

The market has converged on a handful of architectures, each with a distinct operational profile. Choosing the wrong one is like choosing a cargo ship when you need a speedboat — technically works but painfully slow to get started.

| Database | Architecture | Hosted? | Strengths | Best For | Installation |
|---|---|---|---|---|---|
| Chroma | Embedded (in-process) or client-server | Self-host or embedded | Minimal setup, Pythonic API, zero infrastructure overhead | Prototyping, local development, courses — you can be running in 5 minutes | `pip install chromadb` |
| Qdrant | Rust core, client-server | Self-host or Qdrant Cloud | Rich payload filters, very fast queries, production-grade reliability | Production RAG systems where metadata filters are complex and performance matters | `pip install qdrant-client` then `docker run -p 6333:6333 qdrant/qdrant` |
| Weaviate | Go, distributed | Self-host or Weaviate Cloud | GraphQL API, native hybrid search, multimodal support | Hybrid (dense + sparse) search, enterprise deployments with complex schemas | `pip install weaviate-client` |
| pgvector | Postgres extension | Wherever Postgres runs | SQL and vector queries in a single database, familiar tooling for backend teams | Teams already running Postgres who want to add vector search without a new database | `CREATE EXTENSION vector;` in Postgres |
| Pinecone | Managed SaaS, serverless | Cloud only (no self-hosting) | Zero infrastructure management, automatic scaling | Startups that need managed infrastructure and want to avoid DevOps overhead | `pip install pinecone` (API key required) |
| Milvus | Distributed, C++ + Python | Self-host or Zilliz Cloud | Billion-scale capacity, multi-tenancy, GPU acceleration | Very large corpora (100M+ documents), enterprise deployments at scale | `pip install pymilvus` then Docker Compose setup |

**Hybrid search** combines dense (embedding) retrieval with sparse (BM25/keyword) retrieval. Dense search finds semantically related text even when exact words differ; sparse search finds documents that contain the literal query terms, which dense search can miss for rare names, part numbers, or acronyms. Systems like Weaviate and Qdrant run both in parallel and merge the ranked lists with a fusion algorithm (Reciprocal Rank Fusion is common).

## Model 3: Failure Mode Analysis

Vector search fails in predictable ways. Knowing the failure signature helps you diagnose quickly instead of chasing the wrong culprit.

| Failure | Cause | How to Detect | Fix |
|---|---|---|---|
| Semantic mismatch: the retrieved documents are topically wrong | Query and document use different vocabulary for the same concept (e.g., query says "layoffs," documents say "workforce reductions") — the embedding model treats them as distant because they rarely co-occur in training text | Recall@k falls below 0.6 on a labeled evaluation set; a human reviewer looks at the top-5 retrieved chunks and they are clearly off-topic | Add hybrid search to catch keyword matches; expand the query with synonyms before embedding; or switch to a domain-specific embedding model |
| Hallucination about retrieved content: the LLM contradicts its own retrieved text | The LLM ignores the retrieved chunks and draws on parametric memory instead, especially when the retrieved content conflicts with what it learned during training | The LLM's answer contradicts text that is clearly present in the retrieved chunks; a citation check fails | Strengthen the grounding instruction in the system prompt ("Answer only using the provided documents"); lower temperature to 0; use a model with stronger instruction-following |
| Stale index: correct answer exists in the source but is never retrieved | Documents updated or added after the index was last built are invisible to retrieval — the index is a snapshot, not a live view | The correct answer exists in the source database but is never returned even with broad queries | Build an incremental indexing pipeline that detects changes (file modification time, hash comparison, or a change data capture stream from the database) and re-embeds only changed documents |
| Lost in the middle: the correct chunk is retrieved but the LLM ignores it | The relevant chunk is retrieved and placed in the middle of a long context window; research shows LLMs attend most strongly to the beginning and end of their context | Faithfulness score drops as $k$ increases past 5; manual inspection shows the correct chunk is present in the context but the LLM's answer ignores it | Apply a reranker (e.g., `pip install rerankers`) to place the highest-scoring chunk first in the context; reduce $k$ to 3–5; summarize the context before generation |

You are choosing between cosine similarity and L2 distance for a text retrieval system. Your embedding model outputs unit-normalized vectors. Which statement is correct?

[( )] L2 distance should be preferred because it accounts for vector magnitude — magnitude carries additional signal about document importance that cosine similarity discards
[(X)] Cosine similarity and L2 distance produce identical rankings when vectors are unit-normalized, so either works; cosine is typically the default for text
[( )] L2 distance is always faster to compute than cosine similarity because it avoids the normalization step in the cosine formula
[( )] Cosine similarity cannot be used with approximate nearest-neighbor indexes because ANN algorithms like HNSW require a Euclidean distance metric

---

> With the ecosystem surveyed and failure modes cataloged, Part IV gives you hands-on practice with the tools — computing distances, filtering metadata, comparing search strategies, and deliberately injecting failures so you can practice fixing them.

# Part IV: Synthesis and Practice

In this part, you will apply everything from the previous parts through four hands-on exercises: computing distance metrics by hand, designing metadata filters, comparing hybrid search to dense-only retrieval, and deliberately breaking then fixing a stale index.

## Exercises

1. *Metric experiment.* Using your Chroma collection from the RAG activity, manually compute cosine similarity and L2 distance between the query embedding and the top-3 retrieved document embeddings. Verify that the ranking order is the same. Report any floating-point discrepancies.

   *What to do:* Install Chroma (`pip install chromadb`) and retrieve embeddings for a query and its top-3 results. Compute both metrics in Python: `cosine = dot(q, d) / (norm(q) * norm(d))` and `l2 = sqrt(sum((q - d)**2))`.

   *Starter hint:* The code below retrieves the embeddings for a query and its top-3 results, then computes both cosine similarity and L2 distance for each pair. Watch the numerical relationship at the end: for unit-normalized vectors, `L2² = 2(1 - cosine)` should hold for every pair.
   ```python
   import chromadb
   import numpy as np

   client = chromadb.Client()
   collection = client.get_collection("my_docs")

   # Query and get embeddings back
   results = collection.query(
       query_texts=["What is the capital of France?"],
       n_results=3,
       include=["embeddings", "documents", "distances"]
   )
   q_emb = np.array(results["embeddings"][0][0])  # query embedding
   doc_embs = [np.array(e) for e in results["embeddings"][0]]  # top-3 doc embeddings

   for i, d_emb in enumerate(doc_embs):
       cosine = np.dot(q_emb, d_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(d_emb))
       l2 = np.linalg.norm(q_emb - d_emb)
       print(f"Doc {i+1}: cosine={cosine:.4f}, L2={l2:.4f}")
   ```

   *You've succeeded when:* The ranking order (Doc 1 closest, Doc 3 farthest) is identical for both metrics, confirming the algebraic equivalence for unit-normalized vectors. Note the numerical relationship: $L2^2 = 2(1 - \text{cosine})$ for unit vectors.

2. *Metadata filter design.* You are building a legal research assistant over 10,000 court opinions. Each document has metadata fields: `court` (string), `year` (integer), `jurisdiction` (string), `case_type` (string). Write three example ANN queries in natural language and specify the metadata filter expression for each.

   *What to do:* For each query, write (a) the natural language user question, (b) the embedding query text, and (c) the Chroma/Qdrant filter dict that restricts results by metadata.

   *Starter hint:*
   ```python
   # Example filter for Chroma
   results = collection.query(
       query_texts=["breach of fiduciary duty by corporate officers"],
       n_results=5,
       where={"$and": [{"jurisdiction": "federal"}, {"year": {"$gte": 2020}}]}
   )
   # Qdrant equivalent uses Filter(must=[FieldCondition(...), FieldCondition(...)])
   ```

   *You've succeeded when:* You have three queries with distinct filter combinations, and you can explain why each filter improves precision (fewer irrelevant results) without destroying recall (still finds the right cases).

3. *Hybrid search evaluation.* Index 20 documents. For five queries containing proper nouns (names, acronyms, product codes), compare dense-only retrieval vs. a hybrid approach where you also search for the exact query string. Report which queries benefit most from sparse matching and why.

   *What to do:* Use Weaviate or Qdrant (both support hybrid search natively). Run the same 5 queries in dense-only mode and hybrid mode. Compare Precision@3 for each.

   *Starter hint:*
   ```python
   # Qdrant hybrid search example
   from qdrant_client import QdrantClient
   from qdrant_client.models import SparseVector, NamedSparseVector

   # Hybrid search combines dense (embedding) + sparse (BM25) scores
   results = client.query_points(
       collection_name="docs",
       prefetch=[
           models.Prefetch(query=dense_vector, using="dense", limit=10),
           models.Prefetch(query=sparse_vector, using="sparse", limit=10),
       ],
       query=models.FusionQuery(fusion=models.Fusion.RRF),  # Reciprocal Rank Fusion
       limit=3
   )
   ```

   *You've succeeded when:* You can identify at least two queries where hybrid search returns higher Precision@3 than dense-only, and explain why (the proper noun or acronym appears literally in the matching document and the dense embedding fails to bridge the vocabulary gap).

4. *Failure injection.* Deliberately create a stale index scenario: add five new documents to the source corpus without re-indexing. Demonstrate that queries about those documents fail, then fix the pipeline and show successful retrieval.

   *What to do:* Create a Chroma collection with 10 documents. Add 5 new documents to a source folder but do not re-embed or re-add them. Run queries that should return one of the new documents and confirm failure. Then run the indexing step and confirm success.

   *Starter hint:*
   ```python
   # Step 1: Index original 10 docs
   collection.add(documents=original_docs, ids=[str(i) for i in range(10)])

   # Step 2: Add new docs to source folder but NOT to the collection
   # ... (write 5 new files to disk) ...

   # Step 3: Query — this will fail to return new docs
   results = collection.query(query_texts=["topic only in new docs"], n_results=3)
   print("Before re-index:", results["documents"])  # should be empty or wrong

   # Step 4: Fix — detect new files and index them
   new_docs = load_new_files()  # your function to read the new files
   collection.add(documents=new_docs, ids=[str(i) for i in range(10, 15)])

   # Step 5: Query again — now succeeds
   results = collection.query(query_texts=["topic only in new docs"], n_results=3)
   print("After re-index:", results["documents"])  # should show correct new doc
   ```

   *You've succeeded when:* You have a before/after comparison showing the query fails (returns irrelevant documents or empty results) before re-indexing and succeeds after.

---

## Reflection Prompt

*Personal:* Think of a time you searched for something online and the search engine returned results that were "close but wrong" — the right topic, wrong specifics, or the right words but wrong context. How does that experience map to the failure modes in Model 3? Which failure mode best describes what happened to you?

*Technical:* Vector databases trade exact correctness for speed — the ANN in "ANN search" means you might miss the true nearest neighbor. Identify a real application domain where missing the single most relevant document would be an acceptable trade-off (e.g., product recommendations), and one where it would not be (e.g., medical symptom lookup). What does this tell you about the difference between "sufficiently good retrieval" and "correct retrieval"?

*Societal:* A legal aid organization uses a RAG system to help low-income clients understand their rights. The vector database indexes case law that is five years old. When a client asks about a recently changed eviction law, the system confidently returns outdated information. Who bears responsibility — the organization that deployed the system, the developers who built it, or the AI companies whose tools were used? What governance structures would you put in place?

---

→ Coming Up Next: Now that you understand how agents store and retrieve information from vector databases, the next module examines how you decide *which* approach to use for specializing a model: fine-tuning (changing model weights), RAG (adding a retrieval pipeline), or prompting (giving the model better instructions).

---

## Further Reading

- Johnson, Douze, and Jégou. "Billion-scale similarity search with GPUs." *IEEE Transactions on Big Data* (2021). The paper behind the FAISS library that underlies many vector DBs.
- Malkov and Yashunin. "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs." *IEEE TPAMI* (2020). The HNSW algorithm.
- Qdrant documentation on filtered search: https://qdrant.tech/documentation/concepts/filtering/
- Liu et al. "Lost in the Middle: How Language Models Use Long Contexts." *TACL* (2024).
