<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-rag.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-rag.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Retrieval-Augmented Generation with Chroma

The evaluation harness from the *Hallucinations and Evaluating Agent Outputs* activity showed that local models hallucinate (confidently make up facts) where their training data is thin, and the *Tokens, Embeddings, and Attention* activity gave us semantic search; **retrieval-augmented generation (RAG)** combines the two, handing the model the right evidence at the right moment.  We move from **the open-book insight $\rightarrow$ the RAG pipeline $\rightarrow$ a working pipeline with Chroma and Ollama $\rightarrow$ grounded answers with citations**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Parametric Memory** | Facts the model "knows" because they were baked into its weights (numerical parameters) during training: vast but frozen. Like a student who memorized the textbook but cannot look anything up mid-exam. | The model knows general facts about parking regulations but not Ursinus's specific policy |
| **Contextual Memory** | Whatever text is currently in the model's prompt: small but precise and up-to-date. Like an open-book exam where you can read the exact policy. | The parking policy chunk we paste into the prompt before asking the question |
| **RAG (Retrieval-Augmented Generation)** | A technique that fetches the most relevant document chunks at query time and places them in the prompt, converting a closed-book question into an open-book one. | Our `rag_answer()` function retrieves the parking policy chunk before asking the model |
| **Vector Database** | A database specialized for storing and searching embeddings (meaning-vectors). It can find the most similar vectors to a query extremely fast, even across millions of documents. | Chroma (`chromadb`) stores our campus FAQ embeddings and finds the nearest match |
| **Indexing Phase** | The one-time setup work: split documents into chunks, embed each chunk, and store the vectors. Done once; the index is reused for every query. | `col.add(documents=docs, embeddings=..., ids=...)` in the code below |
| **Query Phase** | What happens per question: embed the question, find nearest chunks, paste them into the prompt, generate a cited answer. | `rag_answer("Can a first-year student keep a car on campus?")` |

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Part I, the open-book exam insight |
| 10-35 | Part II, build it: chunk, embed, store, retrieve, generate |
| 35-60 | Part IIb, how the search actually finds anything: distance metrics and the retrieval pipeline |
| 60-70 | The failure modes, against a query you deliberately break |
| 70-75 | Reflection prompt.  The vector-database ecosystem survey is at home |

---
# Part I: The Open-Book Exam Insight

## 1.  Parameters Versus Context

In this Part you will distinguish the two kinds of memory a language model has (the knowledge baked into its parameters during training versus the text currently in its prompt) and understand why RAG (Retrieval-Augmented Generation) turns a hard "closed-book" question into a much easier "open-book" one.

**Why this matters:** Imagine asking someone a trivia question about an obscure historical event.  If they do not know it, they will either admit ignorance or make something up, and AI models tend to make something up convincingly.  RAG is the equivalent of saying "here, look it up in the encyclopedia first, then answer."  The model goes from guessing to reading and summarizing, which is a job it is much better at.  This single insight is why RAG has become the most widely deployed AI engineering technique of the past three years.

A model has two memories.  *Parametric memory* (from "parameters," the numbers learned during training) is whatever was baked into the weights during training: vast, fuzzy, frozen in time.  *Contextual memory* is whatever sits in the prompt right now: small, precise, current.  Hallucination (the model confidently stating something false) is what happens when we ask parametric memory for precision it does not have.  RAG converts the question from a closed-book exam into an open-book one:

$$
\text{answer} = \text{LLM}(\text{query} + \text{retrieve}(\text{query}, \mathcal{D}))
$$

where $\mathcal{D}$ is your document collection and $\text{retrieve}$ selects the top-$k$ chunks (passages) by embedding similarity, exactly the cosine machinery from the tokens and embeddings module.

> **Common Misconception:** The retrieval `top_k` / `k` here (how many *document chunks* to fetch, set as `n_results` in the code below) is a different knob from the **sampling `top_k`** decoding parameter from the *Sampling, Temperature, and Generation* activity.  Same name, different layer: sampling `top_k` truncates the model's probability distribution over the *next token*; retrieval `k` sets the size of the *search result set* pasted into the prompt.  Turning up retrieval `k` gives the model more to read; it has nothing to do with how randomly it writes.

The pipeline has two phases.  *Indexing* (once): split documents into chunks, embed each chunk, store vectors in a vector database.  *Query* (every question): embed the question, find nearest chunks, paste them into the prompt with instructions to answer *only* from the provided context, and cite which chunk supports each claim.

---

## Model 1: Pipeline Tracing

A student asks a campus RAG system, "Can first-year students bring cars?"  The system retrieves a parking policy chunk and a housing FAQ chunk, then answers with a citation.

### Critical Thinking Questions

1.  Walk the question through both phases: which steps happened months ago at indexing time, and which steps happen right now at query time?

   > *Hint: Indexing steps involve reading documents and storing vectors: work done once before any user ever asks a question.  Query steps happen in real time after the user sends their message.  Sort each step: (a) embed the parking policy, (b) embed the user's question, (c) run cosine similarity search, (d) paste chunks into a prompt, (e) split the handbook into chunks, (f) generate the answer.*

2.  The model answers correctly, citing the parking chunk.  Is this *parametric* or *contextual* memory at work?  How can you tell from the citation?

   > *Hint: If the answer came from parametric memory, would the model be able to cite a specific numbered source?  Citations in RAG point to retrieved text that was placed in the prompt; which type of memory is that?*

3.  Suppose the policy changed last week and the index is stale (out of date).  Where exactly does the wrong answer enter the pipeline, and which component is at fault: the model, the retriever, or the index?

   > *Hint: The model answered faithfully from the context it was given.  The retriever found the most similar chunk.  The chunk it found just contained old information.  Which component produced that old chunk?*

---

# Part II: Building It

## 2.  A Complete Local RAG System

In this Part you will implement the two-phase RAG pipeline in Python using Chroma as the vector database and Ollama as the language model.  You will see exactly how the indexing phase and query phase from Part I map onto real function calls, and you will test what happens when the answer is not in the index.

Chroma is an embeddable vector database (a library that stores embeddings and performs nearest-neighbor search, installable as a Python package).  Install with `pip install chromadb`.  Everything below runs on your laptop; no data leaves the room.

The code below is split into two phases.  The **indexing phase** (run once) creates the collection and stores embeddings for each document.  The **query phase** (run per question) embeds the user's question, finds the closest document chunks, and asks the model to answer using only those chunks.

---

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import requests
import chromadb

def embed(text):
    try:
        r = requests.post("http://localhost:11434/api/embeddings",
                          json={"model": "nomic-embed-text", "prompt": text}, timeout=120)
        return r.json()["embedding"]
    except Exception as e:
        print(f"[rag:embed] {e}")
        import traceback; traceback.print_exc()
        return []

def chat(prompt):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": 0.0, "seed": 42},
            "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[rag:chat] {e}")
        import traceback; traceback.print_exc()
        return ""

# --- Indexing phase (run once) ---
docs = [
    "Parking: First-year resident students may not bring vehicles to campus without a hardship waiver.",
    "Library: The Myrin Library is open 8am to midnight Monday through Thursday during the semester.",
    "Dining: Wismer Center serves continuous dining from 7am to 8pm on weekdays.",
    "Advising: Each student is assigned a faculty advisor; registration requires advisor approval.",
    "Athletics: The Floy Lewis Bakes Center is open to all students with a valid ID.",
]

client = chromadb.Client()
col = client.create_collection("campus")
col.add(documents=docs,
        embeddings=[embed(d) for d in docs],
        ids=[f"doc{i}" for i in range(len(docs))])

# --- Query phase (run per question) ---
def rag_answer(question, k=2):
    hits = col.query(query_embeddings=[embed(question)], n_results=k)
    context = "\n".join(f"[{i}] {d}" for i, d in enumerate(hits["documents"][0]))
    prompt = (f"Answer using ONLY the context below. Cite the bracketed source number. "
              f"If the context does not contain the answer, say 'not in my documents'.\n\n"
              f"Context:\n{context}\n\nQuestion: {question}")
    return chat(prompt), context

answer, ctx = rag_answer("Can a first-year student keep a car on campus?")
print("RETRIEVED:\n", ctx, "\n\nANSWER:\n", answer)

answer, ctx = rag_answer("What time does the bookstore close?")
print("\nRETRIEVED:\n", ctx, "\n\nANSWER:\n", answer)
```

---

## Model 2: Grounding in Action

**Why this matters:** The second query ("What time does the bookstore close?") tests a critical design decision: what should the system do when the right answer simply is not in the index?  A bare language model will often invent a plausible-sounding answer ("The bookstore closes at 5pm on weekdays").  RAG, if designed well, will say it does not know.  That difference (between confident invention and abstention) is the core of what makes RAG trustworthy for high-stakes applications like medical information, legal research, or campus policy.

### Critical Thinking Questions

4.  The second question has no answer in the index.  Compare the system's behavior with what the bare model would do (try it by calling `chat(question)` directly).  Which hallucination category from the *Hallucinations and Evaluating Agent Outputs* activity did the RAG instructions just convert into abstention?

   > *Hint: Run `chat("What time does the bookstore close?")` without any context and observe the response.  Then look at the line in `rag_answer` that contains the phrase "not in my documents"; what instruction creates the abstention behavior?*

5.  Identify the precise line of the prompt that creates that abstention behavior.  What happens if you delete it?  Test and report.

   > *Hint: The key phrase is "If the context does not contain the answer, say 'not in my documents'."  Remove that phrase from the prompt string, re-run the bookstore question, and observe whether the model now invents an answer.*

6.  Set `k=1` and ask a question whose answer spans two documents.  What failure occurs, and what does it suggest about choosing $k$?

   > *Hint: Create a question like "Can I get food after working out at the gym?"; the answer involves both the dining hours doc and the athletics doc.  With `k=1`, only one chunk fits in the prompt.  What does the model say?*

> **Common Misconception:** RAG does not teach the model new facts, and it does not fine-tune or update the model in any way.  The model's weights are completely unchanged.  RAG simply places text in the prompt that the model then reads and summarizes, the same way you could hand a book to someone who has never seen it and ask them to answer questions from it.  The intelligence is in the language model; the facts come from your documents.  This means RAG is only as accurate as your documents, and if your documents contain errors, the model will faithfully repeat those errors.

The single most important reason RAG reduces factual hallucination is that it:

[( )] Increases the model's parameter count at query time
[(X)] Moves the burden of factual precision from parametric memory to text supplied in the context
[( )] Lowers the sampling temperature automatically
[( )] Fine-tunes the model on your documents

---

---

# Part IIb: How the Search Actually Finds Anything

Chroma made retrieval look like one function call.  Underneath it is a distance metric, an index, and a set of tradeoffs that decide whether your pipeline stays fast at ten documents and at ten million.  You need this to debug retrieval when it starts returning the wrong thing, which it will.

## Why Brute Force Fails

In this part, you will see why checking every vector in a million-document database is computationally infeasible and how two approximate nearest-neighbor algorithms (HNSW and IVF) solve the problem through clever indexing.

### The Scale Problem

Searching a vector database is like finding the most similar song in a music library, not by song title, but by how it *sounds*.  If you had 1 million songs and had to listen to each one to decide which is most similar to your query, it would take forever.  ANN indexes are the equivalent of organizing songs by genre, tempo, and key so you can jump straight to the right neighborhood.

An embedding vector for a single sentence is a point in $\mathbb{R}^{1536}$. At query time, a RAG system must find the $k$ stored vectors closest to the query vector.  The naive approach is to compute the distance from the query to every stored vector.  For 1 million documents, each at 1536 dimensions, that is $1536 \times 10^6 \approx 1.5 \times 10^9$ floating-point operations per query, enough to take several seconds on a single CPU, unacceptable for an interactive assistant.

**Approximate nearest-neighbor (ANN) search** accepts a small chance of missing the true nearest neighbor in exchange for a 100x to 1000x speedup.  Two algorithms dominate production systems:

- **HNSW (Hierarchical Navigable Small World, an approximate nearest-neighbor index that organizes vectors into a multi-layer graph so search can navigate quickly from coarse to fine-grained neighborhoods):** builds a multi-layer graph where each node connects to its approximate nearest neighbors.  Search navigates from a coarse top layer downward, greedily jumping toward the query.  Think of it as a subway map where express lines get you close quickly, then local stops get you to the exact station.
- **IVF (Inverted File Index):** partitions the vector space into $n$ clusters (Voronoi cells) at index time.  At query time only the nearest few cluster centroids are searched.  Think of it as dividing a library into sections: you check the "Science" section, not every shelf.

---

### Distance Metrics

Not all distance functions measure the same thing.  Choose the wrong one and semantically similar documents rank below dissimilar ones.  Think of this like choosing the right ruler: a protractor measures angles, a tape measure measures length; both are "distance" tools but answer different questions.

| Scenario | Best Metric | Why | When to Use |
|---|---|---|---|
| Finding semantically similar sentences in a text retrieval system | Cosine similarity | Direction encodes meaning; vectors from the same model are already unit-normalized in most libraries, so magnitude differences are irrelevant. | Default choice for all text embedding retrieval; use this unless you have a specific reason not to. |
| Finding documents of similar "importance" where magnitude carries signal | L2 (Euclidean) distance | Magnitude differences are meaningful; two vectors far from the origin but close in angle are different in quantity or intensity, not just topic. | Image embeddings where pixel intensity matters; word count or frequency embeddings where raw size is meaningful. |
| Maximum inner product search for recommendation | Dot product | Relevance decomposes as magnitude × angle; used when popularity or frequency should interact with semantic similarity. | Recommendation systems where a popular item (high magnitude) should rank higher than an obscure but equally relevant item. |
| Comparing images embedded by a CLIP model with known unit norms | Cosine or dot product (equivalent when norms are 1) | Normalization makes them identical; use whichever the library exposes natively to avoid unnecessary computation. | Any embedding model that explicitly states it returns unit-normalized vectors, including `text-embedding-3-small` and `nomic-embed-text`. |

#### Critical Thinking Questions

1.  Most text embedding models (such as `nomic-embed-text` and OpenAI `text-embedding-3-small`) return L2-normalized vectors, meaning every vector has magnitude 1.  Show algebraically that for unit vectors, cosine similarity and dot product are identical.  Why does this simplification matter for implementation?

   *Hint:* Cosine similarity is defined as $\frac{u \cdot v}{||u|| \cdot ||v||}$. What happens to the denominator when both vectors have magnitude 1?

2.  You index 50,000 legal briefs and 50,000 social media posts in the same collection.  A query about "contract breach" retrieves a mix of both.  What property of the embedding space caused this, and which metadata filter would you add to the ANN query to fix it?

   *Hint:* Both document types use the word "breach" but in very different contexts.  The embedding model was trained on mixed text.  What structured field (stored alongside the vectors, not in the vectors) would let you restrict results to one document type?

3.  HNSW builds its graph at index time.  What is the trade-off when you set the number of neighbors per node very high versus very low?  Consider index-build time, query time, and recall.

   *Hint:* More neighbors per node means more edges in the graph.  During search, more edges means more paths to explore.  During index construction, more edges means more distance calculations per inserted node.

---

## The Retrieval Pipeline

In this part, you will trace a complete RAG query through six pipeline steps (embedding, ANN search, metadata filtering, and LLM generation) and learn to diagnose which step is responsible when the answer comes out wrong.

### From Query to Answer

Every RAG query traverses a fixed sequence of steps, like an assembly line where each station transforms the work piece and hands it to the next.  Understanding who owns each step is essential for debugging: when the answer is wrong, you need to pinpoint whether to blame the embedding model, the ANN index, the metadata filter, or the language model.

### Pipeline Tracing

| Step | Component | Input | Output | What Can Go Wrong Here |
|---|---|---|---|---|
| 1. Query arrives | Application layer | Raw user question typed by the user | Plain text string | Query is ambiguous, misspelled, or in a different language than the indexed documents. |
| 2. Query is embedded | Embedding model (e.g., `nomic-embed-text`; install: `ollama pull nomic-embed-text`) | Text string | Float array (1536-dim) | Using a different embedding model than was used at index time causes a "dialect mismatch"; vectors are incomparable. |
| 3. ANN search | Vector database index (HNSW or IVF) | Query vector, $k$ (how many results to return) | Candidate document IDs with distances | If $k$ is too small, the correct document is excluded before the filter even runs. |
| 4. Metadata filter applied | Vector database filter engine | Candidate IDs, filter expression (e.g., `{"year": {"$gte": 2024}}`) | Filtered subset of IDs | Overly strict filters remove the correct document; overly loose filters let irrelevant documents through. |
| 5. Top-$k$ documents returned | Vector database | Filtered IDs | Document text + metadata | If chunks are too long, they waste context window space; if too short, they lack the context the LLM needs to answer. |
| 6. LLM generates with docs in context | Language model (e.g., `claude-sonnet-4-5`, `llama3.1:8b`) | Prompt = system instructions + retrieved chunks + user question | Answer string | LLM ignores the retrieved text and hallucinates from parametric memory; "lost in the middle" effect buries the relevant chunk. |

> **Common Misconception:** Many beginners assume that if the LLM gives a wrong answer, the problem must be with the LLM itself.  In practice, **the retrieval step fails far more often than the generation step**.  A perfect LLM cannot produce a correct answer if Step 3 or 4 returned the wrong documents.  Always check what was actually retrieved (Step 5's output) before debugging the LLM.

#### Critical Thinking Questions

4.  A user asks "What were the 2024 FDA guidelines on GLP-1 drugs?"  Your index was built in January 2024 and the guidelines were published in September 2024.  At which step does the failure occur?  What is the fix, and what is its operational cost?

   *Hint:* The failure happens at Step 3: the correct document was never indexed, so ANN search cannot return it.  The fix involves re-running the indexing pipeline.  How often would you need to do this for a regulatory database?

5.  Your system retrieves the correct documents at step 5, but the LLM's answer contradicts them.  Which step is at fault?  What experiment would you run to confirm this before changing the prompt?

   *Hint:* Before changing anything, print the exact retrieved chunks and compare them to the LLM's answer.  If the chunks clearly contain the correct answer and the LLM ignores them, you have isolated Step 6 as the culprit.

6.  Metadata filters at step 4 operate *after* ANN search, not before.  Why is pre-filtering expensive, and what architectural pattern (called "filtered ANN") is used by databases like Qdrant to make it efficient?

   *Hint:* Pre-filtering means scanning the entire metadata table before doing any vector math.  Qdrant's filtered ANN uses a different strategy: it builds separate HNSW graphs per metadata partition so that filters can be applied during graph traversal rather than after it.

---

## The Ecosystem and Failure Modes

In this part, you will compare six production vector databases by architecture and operational profile, and study the four most common retrieval failure signatures (semantic mismatch, hallucination, stale index, and "lost in the middle") so you can diagnose them from their symptoms.

### Choosing a Vector Database

The market has converged on a handful of architectures, each with a distinct operational profile.  Choosing the wrong one is like choosing a cargo ship when you need a speedboat; technically works but painfully slow to get started.

| Database | Architecture | Hosted? | Strengths | Best For | Installation |
|---|---|---|---|---|---|
| Chroma | Embedded (in-process) or client-server | Self-host or embedded | Minimal setup, Pythonic API, zero infrastructure overhead | Prototyping, local development, courses; you can be running in 5 minutes | `pip install chromadb` |
| Qdrant | Rust core, client-server | Self-host or Qdrant Cloud | Rich payload filters, very fast queries, production-grade reliability | Production RAG systems where metadata filters are complex and performance matters | `pip install qdrant-client` then `docker run -p 6333:6333 qdrant/qdrant` |
| Weaviate | Go, distributed | Self-host or Weaviate Cloud | GraphQL API, native hybrid search, multimodal support | Hybrid (dense + sparse) search, enterprise deployments with complex schemas | `pip install weaviate-client` |
| pgvector | Postgres extension | Wherever Postgres runs | SQL and vector queries in a single database, familiar tooling for backend teams | Teams already running Postgres who want to add vector search without a new database | `CREATE EXTENSION vector;` in Postgres |
| Pinecone | Managed SaaS, serverless | Cloud only (no self-hosting) | Zero infrastructure management, automatic scaling | Startups that need managed infrastructure and want to avoid DevOps overhead | `pip install pinecone` (API key required) |
| Milvus | Distributed, C++ + Python | Self-host or Zilliz Cloud | Billion-scale capacity, multi-tenancy, GPU acceleration | Very large corpora (100M+ documents), enterprise deployments at scale | `pip install pymilvus` then Docker Compose setup |

**Hybrid search** combines dense (embedding) retrieval with sparse (BM25/keyword) retrieval.  Dense search finds semantically related text even when exact words differ; sparse search finds documents that contain the literal query terms, which dense search can miss for rare names, part numbers, or acronyms.  Systems like Weaviate and Qdrant run both in parallel and merge the ranked lists with a fusion algorithm (Reciprocal Rank Fusion is common).

### Failure Mode Analysis

Vector search fails in predictable ways.  Knowing the failure signature helps you diagnose quickly instead of chasing the wrong culprit.

| Failure | Cause | How to Detect | Fix |
|---|---|---|---|
| Semantic mismatch: the retrieved documents are topically wrong | Query and document use different vocabulary for the same concept (e.g., query says "layoffs," documents say "workforce reductions"); the embedding model treats them as distant because they rarely co-occur in training text | Recall@k falls below 0.6 on a labeled evaluation set; a human reviewer looks at the top-5 retrieved chunks and they are clearly off-topic | Add hybrid search to catch keyword matches; expand the query with synonyms before embedding; or switch to a domain-specific embedding model |
| Hallucination about retrieved content: the LLM contradicts its own retrieved text | The LLM ignores the retrieved chunks and draws on parametric memory instead, especially when the retrieved content conflicts with what it learned during training | The LLM's answer contradicts text that is clearly present in the retrieved chunks; a citation check fails | Strengthen the grounding instruction in the system prompt ("Answer only using the provided documents"); lower temperature to 0; use a model with stronger instruction-following |
| Stale index: correct answer exists in the source but is never retrieved | Documents updated or added after the index was last built are invisible to retrieval; the index is a snapshot, not a live view | The correct answer exists in the source database but is never returned even with broad queries | Build an incremental indexing pipeline that detects changes (file modification time, hash comparison, or a change data capture stream from the database) and re-embeds only changed documents |
| Lost in the middle: the correct chunk is retrieved but the LLM ignores it | The relevant chunk is retrieved and placed in the middle of a long context window; research shows LLMs attend most strongly to the beginning and end of their context | Faithfulness score drops as $k$ increases past 5; manual inspection shows the correct chunk is present in the context but the LLM's answer ignores it | Apply a reranker (e.g., `pip install rerankers`) to place the highest-scoring chunk first in the context; reduce $k$ to 3-5; summarize the context before generation |

You are choosing between cosine similarity and L2 distance for a text retrieval system.  Your embedding model outputs unit-normalized vectors.  Which statement is correct?

[( )] L2 distance should be preferred because it accounts for vector magnitude; magnitude carries additional signal about document importance that cosine similarity discards
[(X)] Cosine similarity and L2 distance produce identical rankings when vectors are unit-normalized, so either works; cosine is typically the default for text
[( )] L2 distance is always faster to compute than cosine similarity because it avoids the normalization step in the cosine formula
[( )] Cosine similarity cannot be used with approximate nearest-neighbor indexes because ANN algorithms like HNSW require a Euclidean distance metric

---

# Part III: Synthesis and Practice

## 3.  Exercises

In this Part you apply the RAG pipeline to real documents you choose, stress-test it for both citation quality and failure cases, and connect the results back to the evaluation framework from the *Hallucinations and Evaluating Agent Outputs* activity.  These exercises build directly toward the RAG Knowledge Base Lab.

1.  *Your own corpus.*  Replace the five documents with ten sentences from a syllabus, club constitution, or campus page of your choosing.  Demonstrate one question answered correctly with citation and one abstention.

   - *What to do:* Find a real document (your CS357 syllabus, a club's bylaws, the college's honor code).  Extract 10 meaningful sentences.  Index them in Chroma.  Ask five questions; at least two should be unanswerable from your documents.
   - *Starter hint:* Copy your chosen sentences into the `docs` list, replacing the campus FAQ. Make sure each sentence is self-contained (contains enough context to be understood in isolation; avoid sentences like "As stated above, the deadline is...").
   - *You've succeeded when:* You can show one output where the model correctly cites a source number, and one output where it says "not in my documents" for a question whose answer does not appear in your ten sentences.

2.  *Eval rematch.*  Rerun the evaluation harness you built in the *Hallucinations and Evaluating Agent Outputs* activity, now routed through `rag_answer`, after adding documents containing the answers.  Report accuracy before and after; quantify the lift.

   - *What to do:* Take the question-answer pairs from your *Hallucinations and Evaluating Agent Outputs* evaluation.  For each question that the bare model got wrong, add a document containing the correct answer to the Chroma index.  Run the same questions through `rag_answer` and compare accuracy scores.
   - *Starter hint:* Your accuracy metric from that evaluation harness was (correct answers / total questions).  Run it twice: once with the bare model, once with RAG. The "lift" is `accuracy_rag - accuracy_bare`.  Report both numbers and the lift.
   - *You've succeeded when:* You have a table showing at least 5 questions with the bare model's answer, the RAG answer, and a correct/incorrect label for each, plus the two accuracy scores and the lift.

3.  *Citation audit.*  Ask five questions and verify each citation by hand: does the cited chunk actually support the claim?  Compute a faithfulness rate (number of faithful citations divided by total citations).

   - *What to do:* For each of five questions, read the model's answer, find its cited source numbers (e.g., "[0]"), look up those document indices in the `docs` list, and judge: does the cited document actually say what the model claims it says?
   - *Starter hint:* A citation is "faithful" if a human reading the cited chunk would agree it supports the specific claim the model made.  It is "unfaithful" if the model invented a detail not present in the chunk, even if the chunk is topically related.  Your faithfulness rate = faithful citations / total citations.
   - *You've succeeded when:* You have a table of 5 questions, each model answer, each citation, your judgment (faithful/unfaithful), and a final faithfulness rate with one sentence explaining what that rate means for trust in this system.

4.  *Failure taxonomy.*  Find one *retrieval* failure (the right answer exists in the index, but the wrong chunk was fetched) and one *generation* failure (the right chunk was fetched, but the model produced the wrong answer anyway).  Label which component owns each bug.

   - *What to do:* Print both `ctx` (retrieved context) and `answer` for each of your test questions.  For retrieval failure: find a case where the retrieved chunk does NOT contain the answer but the answer IS in another document in `docs`.  For generation failure: find a case where the retrieved chunk DOES contain the answer but the model's final answer contradicts or ignores the chunk.
   - *Starter hint:* Retrieval failures often happen when a question uses very different vocabulary from the relevant document (vocabulary mismatch).  Generation failures often happen with complex multi-step reasoning or when the model's parametric memory contradicts the context.
   - *You've succeeded when:* You can show the `ctx` and `answer` for each failure case, explain which component (retriever or generator) produced the bug, and suggest one fix for each.

---

## Reflection Prompt

*Personal:* RAG lets a small private model answer questions about *your* documents without those documents ever leaving your machine.  Identify one collection of documents in your life (notes, club records, family archive) you would index, and one you would refuse to index even locally.  What distinguishes them?

*Technical:* In your notebook: the `rag_answer` function instructs the model to say "not in my documents" rather than guess.  But what if a user needs an answer and it is not in the index?  Design a fallback strategy that is more helpful than silence but less dangerous than hallucination.

*Societal:* Institutions (hospitals, courts, schools) could use RAG to give staff instant access to policy documents.  Name one benefit and one risk of a hospital deploying RAG over its clinical guidelines.  Who would need to audit the system, and how often?

---

## -> Coming Up Next

Our RAG system worked because our "documents" were clean, single-sentence facts.  Real documents are messy: long, overlapping, poorly organized.  The *RAG Quality: Chunking, Clustering, and Reranking* activity takes this up next: how you cut documents into chunks determines what you can find, and we will build the tools to measure and improve retrieval quality, the same levers you will tune in the RAG Knowledge Base Lab.

---

## 4.  Further Reading

- Patrick Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."  *NeurIPS* (2020).  The original RAG paper.
- Chroma documentation: https://docs.trychroma.com
- Melanie Mitchell.  *AI: A Guide for Thinking Humans*, Chapter 4.
