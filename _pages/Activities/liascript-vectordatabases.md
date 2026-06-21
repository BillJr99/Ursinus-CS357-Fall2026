# Vector Databases: How Agents Search for Meaning
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

# Part I: Why Brute Force Fails

## 1. The Scale Problem

An embedding vector for a single sentence is a point in $\mathbb{R}^{1536}$. At query time, a RAG system must find the $k$ stored vectors closest to the query vector. The naive approach is to compute the distance from the query to every stored vector. For 1 million documents, each at 1536 dimensions, that is $1536 \times 10^6 \approx 1.5 \times 10^9$ floating-point operations per query — enough to take several seconds on a single CPU, unacceptable for an interactive assistant.

**Approximate nearest-neighbor (ANN) search** accepts a small chance of missing the true nearest neighbor in exchange for a 100x to 1000x speedup. Two algorithms dominate production systems:

- **HNSW (Hierarchical Navigable Small World):** builds a multi-layer graph where each node connects to its approximate nearest neighbors. Search navigates from a coarse top layer downward, greedily jumping toward the query. Think of it as a subway map where express lines get you close quickly, then local stops get you to the exact station.
- **IVF (Inverted File Index):** partitions the vector space into $n$ clusters (Voronoi cells) at index time. At query time only the nearest few cluster centroids are searched. Think of it as dividing a library into sections: you check the "Science" section, not every shelf.

---

## Model 1: Distance Metrics

Not all distance functions measure the same thing. Choose the wrong one and semantically similar documents rank below dissimilar ones.

| Scenario | Best Metric | Why |
|---|---|---|
| Finding semantically similar sentences | Cosine similarity | Direction encodes meaning; vectors from the same model are already unit-normalized in most libraries |
| Finding documents of similar "importance" where magnitude carries signal | L2 (Euclidean) distance | Magnitude differences are meaningful; two vectors far from the origin but close in angle are genuinely different |
| Maximum inner product search (e.g., retrieval for recommendation) | Dot product | Relevance can be decomposed as magnitude × angle; used in recommendation where popularity interacts with similarity |
| Comparing images embedded by a CLIP model with known unit norms | Cosine or dot product (equivalent when norms are 1) | Normalization makes them identical; use whichever the library exposes natively |

### Critical Thinking Questions

1. Most text embedding models (such as `nomic-embed-text` and OpenAI `text-embedding-3-small`) return L2-normalized vectors, meaning every vector has magnitude 1. Show algebraically that for unit vectors, cosine similarity and dot product are identical. Why does this simplification matter for implementation?
2. You index 50,000 legal briefs and 50,000 social media posts in the same collection. A query about "contract breach" retrieves a mix of both. What property of the embedding space caused this, and which metadata filter would you add to the ANN query to fix it?
3. HNSW builds its graph at index time. What is the trade-off when you set the number of neighbors per node very high versus very low? Consider index-build time, query time, and recall.

---

# Part II: The Retrieval Pipeline

## 2. From Query to Answer

Every RAG query traverses a fixed sequence of steps. Understanding the owner of each step is essential for debugging: when the answer is wrong, you need to know whether to blame the embedding model, the ANN index, the metadata filter, or the language model.

## Model 2: Pipeline Tracing

| Step | Component | Input | Output |
|---|---|---|---|
| 1. Query arrives | Application layer | Raw user question | String |
| 2. Query is embedded | Embedding model (e.g., `nomic-embed-text`) | String | Float array (1536-dim) |
| 3. ANN search | Vector database index (HNSW or IVF) | Query vector, $k$ | Candidate document IDs with distances |
| 4. Metadata filter applied | Vector database filter engine | Candidate IDs, filter expression | Filtered subset of IDs |
| 5. Top-$k$ documents returned | Vector database | Filtered IDs | Document text + metadata |
| 6. LLM generates with docs in context | Language model | Prompt = question + retrieved chunks | Answer string |

### Critical Thinking Questions

4. A user asks "What were the 2024 FDA guidelines on GLP-1 drugs?" Your index was built in January 2024 and the guidelines were published in September 2024. At which step does the failure occur? What is the fix, and what is its operational cost?
5. Your system retrieves the correct documents at step 5, but the LLM's answer contradicts them. Which step is at fault? What experiment would you run to confirm this before changing the prompt?
6. Metadata filters at step 4 operate *after* ANN search, not before. Why is pre-filtering expensive, and what architectural pattern (called "filtered ANN") is used by databases like Qdrant to make it efficient?

---

# Part III: The Ecosystem and Failure Modes

## 3. Choosing a Vector Database

The market has converged on a handful of architectures, each with a distinct operational profile.

| Database | Architecture | Hosted? | Strengths | Best For |
|---|---|---|---|---|
| Chroma | Embedded (in-process) or client-server | Self-host or embedded | Minimal setup, Pythonic API, zero infra | Prototyping, local development, courses |
| Qdrant | Rust, client-server | Self-host or cloud | Rich payload filters, fast, production-grade | Production RAG with complex metadata |
| Weaviate | Go, distributed | Self-host or cloud | GraphQL API, hybrid search, multimodal | Hybrid search, enterprise deployments |
| pgvector | Postgres extension | Wherever Postgres runs | SQL + vectors in one query, familiar tooling | Teams that already run Postgres, joining with relational data |
| Pinecone | Managed SaaS, serverless | Cloud only | Zero infra management, autoscaling | Startups needing managed infra |
| Milvus | Distributed, C++ + Python | Self-host or cloud | Billion-scale, multi-tenancy | Very large corpora, enterprise scale |

**Hybrid search** combines dense (embedding) retrieval with sparse (BM25/keyword) retrieval. Dense search finds semantically related text even when exact words differ; sparse search finds documents that contain the literal query terms, which dense search can miss for rare names, part numbers, or acronyms. Systems like Weaviate and Qdrant run both in parallel and merge the ranked lists with a fusion algorithm (Reciprocal Rank Fusion is common).

## Model 3: Failure Mode Analysis

Vector search fails in predictable ways. Knowing the failure signature helps you diagnose quickly.

| Failure | Cause | How to Detect | Fix |
|---|---|---|---|
| Semantic mismatch | Query and document use different vocabulary for the same concept (e.g., query says "layoffs," documents say "workforce reductions") | Recall@k falls below 0.6 on a labeled eval set; retrieved chunks are topically wrong | Hybrid search; query expansion with synonyms; domain-specific embedding model |
| Hallucination about retrieved content | LLM ignores retrieved chunks and draws on parametric memory | Answer contradicts the retrieved text; citation check fails | Strengthen grounding prompt; lower temperature; use a model with better instruction-following |
| Stale index | Documents updated after index build are invisible to retrieval | Correct answer exists in the source but is never retrieved | Incremental indexing pipeline with change detection; TTL on document embeddings |
| Lost in the middle | Relevant chunk is retrieved and placed in the middle of a long context; LLM attends to beginning and end, ignores middle | Faithfulness score drops as $k$ increases past 5; manual inspection shows correct chunk present but unused | Reranking to place most relevant chunk first; reduce $k$; summarize context before generation |

[[MC]]
You are choosing between cosine similarity and L2 distance for a text retrieval system. Your embedding model outputs unit-normalized vectors. Which statement is correct?
- ( ) L2 distance should be preferred because it accounts for vector magnitude
- (x) Cosine similarity and L2 distance produce identical rankings when vectors are unit-normalized, so either works; cosine is typically the default for text
- ( ) L2 distance is always faster to compute than cosine similarity
- ( ) Cosine similarity cannot be used with approximate nearest-neighbor indexes

---

# Part IV: Synthesis and Practice

## Exercises

1. *Metric experiment.* Using your Chroma collection from the RAG activity, manually compute cosine similarity and L2 distance between the query embedding and the top-3 retrieved document embeddings. Verify that the ranking order is the same. Report any floating-point discrepancies.
2. *Metadata filter design.* You are building a legal research assistant over 10,000 court opinions. Each document has metadata fields: `court` (string), `year` (integer), `jurisdiction` (string), `case_type` (string). Write three example ANN queries in natural language and specify the metadata filter expression for each.
3. *Hybrid search evaluation.* Index 20 documents. For five queries containing proper nouns (names, acronyms, product codes), compare dense-only retrieval vs. a hybrid approach where you also search for the exact query string. Report which queries benefit most from sparse matching and why.
4. *Failure injection.* Deliberately create a stale index scenario: add five new documents to the source corpus without re-indexing. Demonstrate that queries about those documents fail, then fix the pipeline and show successful retrieval.

---

## Reflection Prompt

In your notebook: vector databases trade exact correctness for speed — the ANN in "ANN search" means you might miss the true nearest neighbor. Identify a real application domain where missing the single most relevant document would be an acceptable trade-off, and one where it would not be. What does this tell you about the difference between "sufficiently good retrieval" and "correct retrieval"?

---

## Further Reading

- Johnson, Douze, and Jégou. "Billion-scale similarity search with GPUs." *IEEE Transactions on Big Data* (2021). The paper behind the FAISS library that underlies many vector DBs.
- Malkov and Yashunin. "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs." *IEEE TPAMI* (2020). The HNSW algorithm.
- Qdrant documentation on filtered search: https://qdrant.tech/documentation/concepts/filtering/
- Liu et al. "Lost in the Middle: How Language Models Use Long Contexts." *TACL* (2024).
