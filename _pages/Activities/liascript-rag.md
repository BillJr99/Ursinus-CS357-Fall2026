<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-rag.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-rag.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# Foundations of AI: Document Retrieval and Retrieval-Augmented Generation (RAG)

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals:**

- Define **document retrieval** and contrast with pure prompting.  
- Explain the pipeline of **retrieval-augmented generation (RAG)**.  
- Derive the **vector embedding search** process mathematically.  
- Explain the meaning of **top-k retrieval** and how it impacts answer quality.  
- Show how retrieved docs are inserted into the **context window** of an LLM.  
- Implement a **toy RAG pipeline** in Python with FAISS/Chroma.  
- Evaluate RAG: accuracy, latency, hallucination reduction.  
- Discuss **limitations and risks**: stale corpora, biased data, prompt injection.  

---

## 1) Why Retrieval?

- Pure LLM prompting: relies only on pretrained knowledge.  
- Problem: **staleness** (cutoff date), **hallucinations**.  
- Retrieval: **ground model outputs** in external sources.  
- Combines **semantic search** + **generation**.  

**Key Idea:** Instead of asking an LLM to recall facts, *retrieve them from a curated knowledge base* and insert into the LLM’s **context window** so the answer is **grounded**.  

---

## 2) The RAG Pipeline

```
User Query → Embed → Vector Search → Retrieved Docs (top-k) → Prompt Augmentation → LLM Generation → Answer
```

Steps:
1. Encode query $q$ into vector $v_q$.  
2. Search nearest neighbors in embedding DB.  
3. Retrieve top-k passages.  
4. Concatenate retrieved text into LLM context window.  
5. Generate grounded answer.  

---

## 3) Embedding Search Mathematics

- Embedding function: $f: \mathcal{X}\to\mathbb{R}^d$.  
- For query $q$ and doc $d_i$:

$$
sim(q,d_i) = \frac{f(q)\cdot f(d_i)}{\|f(q)\|\,\|f(d_i)\|} \quad (\text{cosine similarity}).
$$

- Retrieval = find **top-k** docs with maximum similarity.  
- Top-k = return the k highest scoring docs; larger k → more coverage, but risks adding irrelevant/noisy context.  

---

## 4) Incorporation into Context Window

- Once docs are retrieved, they are **prepended or appended** into the LLM input.  
- Example augmented prompt:

```
System: You are a helpful assistant.
User: Question: Where is Ursinus College located?
Retrieved Documents: [“Ursinus College is in Collegeville, PA.”]
```

- The LLM sees both the **question** and the **retrieved documents** in its context window.  
- Limitations: if too many documents are inserted, the model may exceed token limits or truncate older context.  

---

## 5) Example: Minimal RAG in Python

```python
from openai import OpenAI
import faiss, numpy as np

client = OpenAI()

# Toy corpus
corpus = [
    "The capital of France is Paris.",
    "The Pythagorean theorem states a^2 + b^2 = c^2.",
    "Ursinus College is in Collegeville, PA."
]

# Embed
embs = [client.embeddings.create(model="text-embedding-3-small", input=doc).data[0].embedding for doc in corpus]

index = faiss.IndexFlatL2(len(embs[0]))
index.add(np.array(embs, dtype=np.float32))

query = "Where is Ursinus College located?"
q_emb = client.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding
D,I = index.search(np.array([q_emb], dtype=np.float32), k=2)
retrieved = [corpus[i] for i in I[0]]

# Augment prompt with retrieved context
messages = [
    {"role": "system", "content": "Answer using the retrieved documents."},
    {"role": "user", "content": f"Docs: {retrieved}\nQuestion: {query}"}
]

resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
print(resp.choices[0].message.content)
```

---

## 5b) Creating a Vector Database in Python

- **Step 1:** Choose a DB (FAISS, Chroma, Weaviate, Pinecone).
- **Step 2:** Embed documents into vectors.
- **Step 3:** Store embeddings + metadata in the vectordb.

```python
# Example using ChromaDB
import chromadb
from openai import OpenAI

client = OpenAI()
chroma = chromadb.Client()

# Create / connect to a collection
collection = chroma.create_collection("my_docs")

# Add some documents with IDs
docs = [
    "Deep learning models use backpropagation.",
    "Vector databases store embeddings for fast search.",
    "Ursinus College is in Collegeville, PA."
]

embs = [
    client.embeddings.create(model="text-embedding-3-small", input=doc).data[0].embedding
    for doc in docs
]

collection.add(documents=docs, embeddings=embs, ids=[f"doc{i}" for i in range(len(docs))])

print("VectorDB created with 3 documents.")
```

---

## 5c) Querying / Prompting the Vector Database

- Query workflow: embed → nearest neighbor search → retrieve top-k.
- Retrieved passages are injected into the LLM prompt to ground its answer.

```python
query = "Where is Ursinus College?"
q_emb = client.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding

# Retrieve top-2 similar docs
results = collection.query(query_embeddings=[q_emb], n_results=2)
retrieved = results["documents"][0]

print("Retrieved:", retrieved)

# Feed into LLM with retrieved context
messages = [
  {"role": "system", "content": "Answer using the retrieved docs."},
  {"role": "user", "content": f"Docs: {retrieved}\nQuestion: {query}"}
]

resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
print(resp.choices[0].message.content)
```

---

## 5d) Bulk Ingestion: Add a Directory of Documents to a Vector DB

**Goal:** Walk a directory tree, load files, chunk text, embed, and store with metadata.

**Assumptions**
- You have an OpenAI API key set (e.g., `OPENAI_API_KEY`).
- Install deps (choose one DB backend):
  - `pip install chromadb pypdf openai`  *(Chroma)*
  - `pip install faiss-cpu pypdf openai` *(FAISS)*

```python
# Bulk ingestion with CHROMA (local, simple)
import os, glob, re
from typing import List, Dict
import chromadb
from pypdf import PdfReader
from openai import OpenAI

# ---------- Configuration ----------
DATA_DIR = "./docs"        # directory containing .txt, .md, .pdf
COLLECTION_NAME = "course_corpus"
MODEL_EMB = "text-embedding-3-small"
CHUNK_SIZE = 800           # ~800 characters per chunk
CHUNK_OVERLAP = 120        # overlap to preserve context between chunks
# -----------------------------------

client = OpenAI()
chroma = chromadb.Client()
collection = chroma.get_or_create_collection(COLLECTION_NAME)

def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def read_pdf_file(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for p in reader.pages:
        pages.append(p.extract_text() or "")
    return "\n".join(pages)

def load_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".txt", ".md", ".markdown"]:
        return read_text_file(path)
    elif ext == ".pdf":
        return read_pdf_file(path)
    else:
        return ""  # unsupported type (you can extend for .docx, .html, etc.)

def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> List[str]:
    text = re.sub(r"\s+\n", "\n", text)           # normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)        # collapse excessive blank lines
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0: start = 0
        if start >= len(text): break
    return [c.strip() for c in chunks if c.strip()]

def embed_texts(texts: List[str]) -> List[List[float]]:
    # Batch in small groups to be gentle on rate limits
    embeddings = []
    BATCH = 64
    for i in range(0, len(texts), BATCH):
        batch = texts[i:i+BATCH]
        resp = client.embeddings.create(model=MODEL_EMB, input=batch)
        embeddings.extend([d.embedding for d in resp.data])
    return embeddings

# Attach metadata to each document, like the original file path for provenance
def path_to_meta(path: str) -> Dict:
    return {
        "path": os.path.abspath(path),
        "filename": os.path.basename(path),
        "ext": os.path.splitext(path)[1].lower(),
    }

# Walk directory, load, chunk, embed, and add to Chroma
paths = []
for ext in ("**/*.txt", "**/*.md", "**/*.markdown", "**/*.pdf"):
    paths += glob.glob(os.path.join(DATA_DIR, ext), recursive=True)

doc_texts, doc_ids, metadatas = [], [], []
for p in paths:
    raw = load_document(p)
    if not raw.strip():
        continue
    chunks = chunk_text(raw)
    for j, ch in enumerate(chunks):
        doc_texts.append(ch)
        doc_ids.append(f"{p}::chunk{j}")
        metadatas.append(path_to_meta(p))

# Embed and store
if doc_texts:
    embs = embed_texts(doc_texts)
    collection.add(documents=doc_texts, embeddings=embs, metadatas=metadatas, ids=doc_ids)
    print(f"Ingested {len(doc_texts)} chunks from {len(paths)} files into Chroma collection '{COLLECTION_NAME}'.")
else:
    print("No documents found to ingest.")
```

---

## 5e) Querying the Ingested Vector DB

- **top-k retrieval:** trade-off between coverage (higher k) and noise/latency.
- **temperature:** keep low (e.g., 0.0–0.3) for grounded answers that hew closely to retrieved evidence.
- **Citations:** include file paths/IDs from metadata for transparency.

```python
from openai import OpenAI
client = OpenAI()

QUESTION = "Summarize what our corpus says about Ursinus College."

# 1) Embed query
q_emb = client.embeddings.create(model="text-embedding-3-small", input=QUESTION).data[0].embedding

# 2) Retrieve top-k
TOP_K = 4
res = collection.query(query_embeddings=[q_emb], n_results=TOP_K)

retrieved_docs = res["documents"][0]
retrieved_meta = res["metadatas"][0]

for i, (doc, meta) in enumerate(zip(retrieved_docs, retrieved_meta), start=1):
    print(f"\n--- Hit {i} ---")
    print(meta.get("path", meta))
    print(doc[:500] + ("..." if len(doc) > 500 else ""))

# 3) Compose grounded prompt for the LLM
context_block = "\n\n".join(retrieved_docs)
messages = [
    {"role": "system", "content": "Answer concisely and cite file paths when relevant."},
    {"role": "user", "content": f"Context:\n{context_block}\n\nQuestion: {QUESTION}\nIf you cite, reference the file paths shown above."},
]

resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.2)
print("\n\n=== MODEL ANSWER ===\n", resp.choices[0].message.content)
```

---

## 5f) Practical Tips

- **Pre-processing:** normalize whitespace; strip boilerplate/headers; consider language detection if your corpus is multilingual.
- **Chunk size:** 600–1200 characters (or ~200–400 tokens) often works well; tune for your domain and model.
- **Overlap:** 10–20% overlap preserves context at chunk boundaries.
- **Deduplication:** hash chunks (minhash/shingling) to avoid redundant storage.
- **Metadata:** include source path, title, section headings, dates; this enables filtered retrieval (e.g., only ext=".pdf").
- **Refreshing the DB:** re-embed/re-index when documents change; consider background jobs and versioning.
- **Security:** never index secrets; respect file permissions; beware prompt-injection in retrieved content—sanitize or constrain model behavior.

---

## 6) Evaluation of RAG

- **Accuracy:** grounded vs. hallucinated answers.  
- **Coverage:** recall of relevant docs.  
- **Latency:** retrieval + generation overhead.  
- **Faithfulness metrics:** e.g., citation precision/recall.  

---

## 7) Limitations & Risks

- **Stale corpora:** outdated indexes yield obsolete answers.  
- **Biases:** retrieval amplifies training corpus biases.  
- **Prompt injection:** malicious docs may poison LLM output.  
- **Context window limits:** too many docs = truncation.  

---

## 8) Variants & Extensions

- **HyDE (Hypothetical Document Embeddings):** generate hypothetical doc before retrieval.  
- **Memory-Augmented RAG:** maintain personalized corpora.  
- **Structured RAG:** retrieval from knowledge graphs/databases.  
- **Agentic RAG:** multi-step querying + tool use.  

---

## 9) Ethical & Governance Issues

- Who curates the document corpus?  
- Should users be told when an answer is retrieved vs. generated?  
- Risks of misinformation if retrieved docs are low quality.  
- Governance: licensing, attributions, transparency.  

**Discussion Prompt:**
- If you deploy RAG in education, what safeguards are needed to ensure students receive accurate, fair, and up-to-date info?  

{{1}}

---

## References & Further Reading

- Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP*.  
- Izacard & Grave (2020). *Leveraging Passage Retrieval with Generative Models*.  
- Karpukhin et al. (2020). *Dense Passage Retrieval for Open-Domain QA*.  
- Gao et al. (2022). *Retrieval-Augmented Language Model Pre-Training*.  
- Mitchell, *Artificial Intelligence: A Guide for Thinking Humans* (Ch. 14).  
- Boden, *Philosophy of Artificial Intelligence* (Ch. 13).  

---
