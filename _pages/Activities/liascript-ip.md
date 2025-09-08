<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/liascript-ip.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ip.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/liascript/CodeRunner/master/style.css
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# Foundations of AI: Intellectual Property, Data Provenance, and Copyright

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals:**

- Understand what **data provenance** means in AI contexts.  
- Explore the role of **copyright law** in data collection, training, and model outputs.  
- Examine key legal debates (fair use, transformative works, derivative content).  
- Investigate how **datasets are built** and why provenance tracking matters.  
- Evaluate **licensing strategies** (open data, Creative Commons, opt-in datasets).  
- Discuss ethical considerations: ownership, consent, attribution, and labor.  

---

## 1) What is Data Provenance?

- **Data provenance**: the record of where data originated, how it was collected, and how it has been transformed.  
- Analogy: provenance in art — knowing the chain of custody gives credibility.  
- In AI:
  - Important for **attribution**.  
  - Essential for **auditing bias**.  
  - Supports **reproducibility** of research.  

---

## 2) Copyright in AI Training Data

- **Copyright** protects creative works (text, music, images, code).  
- Key question: *Is it legal to train LLMs on copyrighted data scraped from the web?*  
- Legal debates:
  - **Fair use** (U.S.) vs. **fair dealing** (EU/UK).  
  - Authors and artists argue unauthorized scraping is exploitation.  
  - AI developers argue training is *transformative use* (not a substitute for original works).  

**Example:** Ongoing lawsuits (e.g., authors vs. OpenAI and Meta) argue that using books without permission violates copyright.  

---

## 3) Outputs as Derivative Works

- Are AI-generated outputs themselves **derivative works**?  
- If a model memorizes passages verbatim → risk of copyright violation.  
- If a model generalizes patterns → often claimed as transformative.  

Mathematically, if training corpus is $D=\{x_1,\dots,x_n\}$ and model samples $y\sim p_\theta$, then:

$$
P(y) \neq \delta(y - x_i) \quad \text{for all } i
$$

If $y$ reproduces an exact $x_i$, $y$ may be infringing. Otherwise, legality depends on interpretation.  

---

## 4) Tracking Provenance

- **Metadata & licensing tags** in datasets (e.g., LAION includes URL sources).  
- **Data documentation**: datasheets for datasets (Gebru et al.).  
- **Provenance-aware RAG**: retrieval pipelines that cite original sources.  
- **Watermarking**: cryptographically mark model outputs for provenance tracing.  

---

## 5) Code Demo: Provenance-Aware Retrieval

```python
from openai import OpenAI
import faiss, numpy as np

client = OpenAI()

# Corpus with source metadata
corpus = [
    {"text": "The capital of France is Paris.", "source": "https://en.wikipedia.org/wiki/Paris"},
    {"text": "Ursinus College is located in Collegeville, Pennsylvania.", "source": "https://www.ursinus.edu"},
    {"text": "The Pythagorean theorem states a^2 + b^2 = c^2.", "source": "https://mathworld.wolfram.com/PythagoreanTheorem.html"}
]

# Embed texts
texts = [c["text"] for c in corpus]
embs = [client.embeddings.create(model="text-embedding-3-small", input=t).data[0].embedding for t in texts]

index = faiss.IndexFlatL2(len(embs[0]))
index.add(np.array(embs, dtype=np.float32))

query = "Where is Ursinus College located?"
q_emb = client.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding
D,I = index.search(np.array([q_emb], dtype=np.float32), k=2)

retrieved = [corpus[i] for i in I[0]]

context = "\n".join([f"Source: {r['source']} | Text: {r['text']}" for r in retrieved])

messages = [
    {"role": "system", "content": "Answer using the provided documents. Always cite the sources explicitly."},
    {"role": "user", "content": f"Docs:\n{context}\nQuestion: Where is Ursinus College located?"}
]

resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
print(resp.choices[0].message.content)
```

---

## 6) Practical Considerations

- **Scalability:**
  - Millions of documents → need ANN (Approximate Nearest Neighbor) methods (e.g., FAISS, ScaNN).  
  - Tradeoff between retrieval accuracy and latency.  

- **Dynamic updates:**
  - Need to refresh indices as new documents arrive.  
  - Avoid training–serving skew.  

- **Evaluation:**
  - Precision@k, Recall@k for retrieval.  
  - End-to-end task metrics: exact match, BLEU, ROUGE, factuality.

---

## 7) Ethical & Societal Concerns

- **Copyright & licensing:** scraped data may violate rights.  
- **Attribution:** should models cite sources automatically?  
- **Transparency:** users must know whether info is retrieved vs. generated.  
- **Misinformation risk:** retrieved but outdated or biased documents may mislead.  

**Reflection Prompt:**  
Imagine your AI tutor retrieves content from the web. How would you ensure (a) **accuracy**, (b) **fair attribution**, and (c) **ethical use of sources**?  

{{1}}

---

## References & Further Reading

- Gebru et al. (2018). *Datasheets for Datasets*.  
- Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP*.  
- Karpukhin et al. (2020). *Dense Passage Retrieval*.  
- Creative Commons (https://creativecommons.org/).  
- Mitchell, *Artificial Intelligence: A Guide for Thinking Humans* (Ch. 14).  

---