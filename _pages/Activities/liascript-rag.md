# Retrieval-Augmented Generation with Chroma
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-rag.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-rag.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Retrieval-Augmented Generation with Chroma

Our evaluation harness showed that local models hallucinate where their training data is thin; **retrieval-augmented generation (RAG)** attacks that problem by handing the model the right evidence at the right moment. We move from **the open-book insight $\rightarrow$ the RAG pipeline $\rightarrow$ a working pipeline with Chroma and Ollama $\rightarrow$ grounded answers with citations**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Open-Book Exam Insight

## 1. Parameters Versus Context

**A model has two memories.** *Parametric memory* is whatever was baked into the weights during training: vast, fuzzy, frozen in time. *Contextual memory* is whatever sits in the prompt right now: small, precise, current. Hallucination is what happens when we ask parametric memory for precision it does not have. RAG converts the question from a closed-book exam into an open-book one:

$$
\text{answer} = \text{LLM}(\text{query} + \text{retrieve}(\text{query}, \mathcal{D}))
$$

where $\mathcal{D}$ is your document collection and $\text{retrieve}$ selects the top-$k$ chunks by embedding similarity, exactly the cosine machinery from week 4.

**The pipeline has two phases.** *Indexing* (once): split documents into chunks, embed each chunk, store vectors in a vector database. *Query* (every question): embed the question, find nearest chunks, paste them into the prompt with instructions to answer *only* from the provided context, and cite which chunk supports each claim.

---

## Model 1: Pipeline Tracing

A student asks a campus RAG system, "Can first-year students bring cars?" The system retrieves a parking policy chunk and a housing FAQ chunk, then answers with a citation.

### Critical Thinking Questions

1. Walk the question through both phases: which steps happened months ago at indexing, and which happen at query time?
2. The model answers correctly, citing the parking chunk. Is this *parametric* or *contextual* memory at work? How can you tell from the citation?
3. Suppose the policy changed last week and the index is stale. Where exactly does the wrong answer enter the pipeline, and which component is at fault: the model, the retriever, or the index?

---

# Part II: Building It

## 2. A Complete Local RAG System

Chroma is an embeddable vector database: a library that stores embeddings and performs nearest-neighbor search. Install with `pip install chromadb`. Everything below runs on your laptop; no data leaves the room.

---

## Code Cell

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

### Critical Thinking Questions

4. The second question has no answer in the index. Compare the system's behavior with what the bare model would do (try it!). Which hallucination category from week 3 did the RAG instructions just convert into honest abstention?
5. Identify the precise line of the prompt that creates that abstention behavior. What happens if you delete it? Test and report.
6. Set `k=1` and ask a question whose answer spans two documents. What failure occurs, and what does it suggest about choosing $k$?

[[MC]]
The single most important reason RAG reduces factual hallucination is that it:
- ( ) Increases the model's parameter count at query time
- (x) Moves the burden of factual precision from parametric memory to text supplied in the context
- ( ) Lowers the sampling temperature automatically
- ( ) Fine-tunes the model on your documents

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Your own corpus.* Replace the five documents with ten sentences from a syllabus, club constitution, or campus page of your choosing. Demonstrate one question answered correctly with citation and one honest abstention.
2. *Eval rematch.* Rerun your week 3 evaluation harness, now routed through `rag_answer`, after adding documents containing the answers. Report accuracy before and after; quantify the lift.
3. *Citation audit.* Ask five questions and verify each citation by hand: does the cited chunk actually support the claim? Compute a faithfulness rate. (This metric returns in the LLM-as-judge module.)
4. *Failure taxonomy.* Find one *retrieval* failure (right answer exists, wrong chunk fetched) and one *generation* failure (right chunk fetched, wrong answer produced). Label which component owns each bug.

---

## Reflection Prompt

In your notebook: RAG lets a small private model answer questions about *your* documents without those documents ever leaving your machine. Identify one collection of documents in your life (notes, club records, family archive) you would index, and one you would refuse to index even locally. What distinguishes them?

---

## 4. Further Reading

- Patrick Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *NeurIPS* (2020). The original RAG paper.
- Chroma documentation: https://docs.trychroma.com
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 4.
