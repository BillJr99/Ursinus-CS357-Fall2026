<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-rag.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-rag.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/liascript/CodeRunner/master/style.css
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
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

!?[RAG pipeline workflow diagram](https://raw.githubusercontent.com/BillJr99/Ursinus-Boilerplate-Assets/main/img/rag_pipeline.png)

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
