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

The evaluation harness from the *Hallucinations and Evaluating Agent Outputs* activity showed that local models hallucinate (confidently make up facts) where their training data is thin, and the *Tokens and Embeddings: How Agents Represent Meaning* activity gave us semantic search; **retrieval-augmented generation (RAG)** combines the two, handing the model the right evidence at the right moment. We move from **the open-book insight $\rightarrow$ the RAG pipeline $\rightarrow$ a working pipeline with Chroma and Ollama $\rightarrow$ grounded answers with citations**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Parametric Memory** | Facts the model "knows" because they were baked into its weights (numerical parameters) during training — vast but frozen. Like a student who memorized the textbook but cannot look anything up mid-exam. | The model knows general facts about parking regulations but not Ursinus's specific policy |
| **Contextual Memory** | Whatever text is currently in the model's prompt — small but precise and up-to-date. Like an open-book exam where you can read the exact policy. | The parking policy chunk we paste into the prompt before asking the question |
| **RAG (Retrieval-Augmented Generation)** | A technique that fetches the most relevant document chunks at query time and places them in the prompt, converting a closed-book question into an open-book one. | Our `rag_answer()` function retrieves the parking policy chunk before asking the model |
| **Vector Database** | A database specialized for storing and searching embeddings (meaning-vectors). It can find the most similar vectors to a query extremely fast, even across millions of documents. | Chroma (`chromadb`) stores our campus FAQ embeddings and finds the nearest match |
| **Indexing Phase** | The one-time setup work: split documents into chunks, embed each chunk, and store the vectors. Done once; the index is reused for every query. | `col.add(documents=docs, embeddings=..., ids=...)` in the code below |
| **Query Phase** | What happens per question: embed the question, find nearest chunks, paste them into the prompt, generate a cited answer. | `rag_answer("Can a first-year student keep a car on campus?")` |

---

# Part I: The Open-Book Exam Insight

## 1. Parameters Versus Context

In this Part you will distinguish the two kinds of memory a language model has — the knowledge baked into its parameters during training versus the text currently in its prompt — and understand why RAG (Retrieval-Augmented Generation) turns a hard "closed-book" question into a much easier "open-book" one.

**Why this matters:** Imagine asking someone a trivia question about an obscure historical event. If they do not know it, they will either admit ignorance or make something up — and AI models tend to make something up convincingly. RAG is the equivalent of saying "here, look it up in the encyclopedia first, then answer." The model goes from guessing to reading and summarizing, which is a job it is much better at. This single insight is why RAG has become the most widely deployed AI engineering technique of the past three years.

**A model has two memories.** *Parametric memory* (from "parameters," the numbers learned during training) is whatever was baked into the weights during training: vast, fuzzy, frozen in time. *Contextual memory* is whatever sits in the prompt right now: small, precise, current. Hallucination (the model confidently stating something false) is what happens when we ask parametric memory for precision it does not have. RAG converts the question from a closed-book exam into an open-book one:

$$
\text{answer} = \text{LLM}(\text{query} + \text{retrieve}(\text{query}, \mathcal{D}))
$$

where $\mathcal{D}$ is your document collection and $\text{retrieve}$ selects the top-$k$ chunks (passages) by embedding similarity — exactly the cosine machinery from the tokens and embeddings module.

> **⚠️ Common Misconception:** The retrieval `top_k` / `k` here (how many *document chunks* to fetch, set as `n_results` in the code below) is a different knob from the **sampling `top_k`** decoding parameter from the *Sampling, Temperature, and Generation* activity. Same name, different layer: sampling `top_k` truncates the model's probability distribution over the *next token*; retrieval `k` sets the size of the *search result set* pasted into the prompt. Turning up retrieval `k` gives the model more to read; it has nothing to do with how randomly it writes.

**The pipeline has two phases.** *Indexing* (once): split documents into chunks, embed each chunk, store vectors in a vector database. *Query* (every question): embed the question, find nearest chunks, paste them into the prompt with instructions to answer *only* from the provided context, and cite which chunk supports each claim.

---

## Model 1: Pipeline Tracing

A student asks a campus RAG system, "Can first-year students bring cars?" The system retrieves a parking policy chunk and a housing FAQ chunk, then answers with a citation.

### Critical Thinking Questions

1. Walk the question through both phases: which steps happened months ago at indexing time, and which steps happen right now at query time?

   > *Hint: Indexing steps involve reading documents and storing vectors — work done once before any user ever asks a question. Query steps happen in real time after the user sends their message. Sort each step: (a) embed the parking policy, (b) embed the user's question, (c) run cosine similarity search, (d) paste chunks into a prompt, (e) split the handbook into chunks, (f) generate the answer.*

2. The model answers correctly, citing the parking chunk. Is this *parametric* or *contextual* memory at work? How can you tell from the citation?

   > *Hint: If the answer came from parametric memory, would the model be able to cite a specific numbered source? Citations in RAG point to retrieved text that was placed in the prompt — which type of memory is that?*

3. Suppose the policy changed last week and the index is stale (out of date). Where exactly does the wrong answer enter the pipeline, and which component is at fault: the model, the retriever, or the index?

   > *Hint: The model answered faithfully from the context it was given. The retriever found the most similar chunk. The chunk it found just contained old information. Which component produced that old chunk?*

---

# Part II: Building It

## 2. A Complete Local RAG System

In this Part you will implement the two-phase RAG pipeline in Python using Chroma as the vector database and Ollama as the language model. You will see exactly how the indexing phase and query phase from Part I map onto real function calls — and you will test what happens when the answer is not in the index.

Chroma is an embeddable vector database (a library that stores embeddings and performs nearest-neighbor search, installable as a Python package). Install with `pip install chromadb`. Everything below runs on your laptop; no data leaves the room.

The code below is split into two phases. The **indexing phase** (run once) creates the collection and stores embeddings for each document. The **query phase** (run per question) embeds the user's question, finds the closest document chunks, and asks the model to answer using only those chunks.

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

**Why this matters:** The second query ("What time does the bookstore close?") tests a critical design decision: what should the system do when the right answer simply is not in the index? A bare language model will often invent a plausible-sounding answer ("The bookstore closes at 5pm on weekdays"). RAG, if designed well, will say it does not know. That difference — between confident invention and abstention — is the core of what makes RAG trustworthy for high-stakes applications like medical information, legal research, or campus policy.

### Critical Thinking Questions

4. The second question has no answer in the index. Compare the system's behavior with what the bare model would do (try it by calling `chat(question)` directly). Which hallucination category from the *Hallucinations and Evaluating Agent Outputs* activity did the RAG instructions just convert into abstention?

   > *Hint: Run `chat("What time does the bookstore close?")` without any context and observe the response. Then look at the line in `rag_answer` that contains the phrase "not in my documents" — what instruction creates the abstention behavior?*

5. Identify the precise line of the prompt that creates that abstention behavior. What happens if you delete it? Test and report.

   > *Hint: The key phrase is "If the context does not contain the answer, say 'not in my documents'." Remove that phrase from the prompt string, re-run the bookstore question, and observe whether the model now invents an answer.*

6. Set `k=1` and ask a question whose answer spans two documents. What failure occurs, and what does it suggest about choosing $k$?

   > *Hint: Create a question like "Can I get food after working out at the gym?" — the answer involves both the dining hours doc and the athletics doc. With `k=1`, only one chunk fits in the prompt. What does the model say?*

> **⚠️ Common Misconception:** RAG does not teach the model new facts, and it does not fine-tune or update the model in any way. The model's weights are completely unchanged. RAG simply places text in the prompt that the model then reads and summarizes — the same way you could hand a book to someone who has never seen it and ask them to answer questions from it. The intelligence is in the language model; the facts come from your documents. This means RAG is only as accurate as your documents, and if your documents contain errors, the model will faithfully repeat those errors.

[[MC]]
The single most important reason RAG reduces factual hallucination is that it:
- ( ) Increases the model's parameter count at query time
- (x) Moves the burden of factual precision from parametric memory to text supplied in the context
- ( ) Lowers the sampling temperature automatically
- ( ) Fine-tunes the model on your documents

---

# Part III: Synthesis and Practice

## 3. Exercises

In this Part you apply the RAG pipeline to real documents you choose, stress-test it for both citation quality and failure cases, and connect the results back to the evaluation framework from the *Hallucinations and Evaluating Agent Outputs* activity. These exercises build directly toward the RAG Knowledge Base Lab.

1. *Your own corpus.* Replace the five documents with ten sentences from a syllabus, club constitution, or campus page of your choosing. Demonstrate one question answered correctly with citation and one abstention.

   - *What to do:* Find a real document (your CS357 syllabus, a club's bylaws, the college's honor code). Extract 10 meaningful sentences. Index them in Chroma. Ask five questions — at least two should be unanswerable from your documents.
   - *Starter hint:* Copy your chosen sentences into the `docs` list, replacing the campus FAQ. Make sure each sentence is self-contained (contains enough context to be understood in isolation — avoid sentences like "As stated above, the deadline is...").
   - *You've succeeded when:* You can show one output where the model correctly cites a source number, and one output where it says "not in my documents" for a question whose answer genuinely does not appear in your ten sentences.

2. *Eval rematch.* Rerun the evaluation harness you built in the *Hallucinations and Evaluating Agent Outputs* activity, now routed through `rag_answer`, after adding documents containing the answers. Report accuracy before and after; quantify the lift.

   - *What to do:* Take the question-answer pairs from your *Hallucinations and Evaluating Agent Outputs* evaluation. For each question that the bare model got wrong, add a document containing the correct answer to the Chroma index. Run the same questions through `rag_answer` and compare accuracy scores.
   - *Starter hint:* Your accuracy metric from that evaluation harness was (correct answers / total questions). Run it twice: once with the bare model, once with RAG. The "lift" is `accuracy_rag - accuracy_bare`. Report both numbers and the lift.
   - *You've succeeded when:* You have a table showing at least 5 questions with the bare model's answer, the RAG answer, and a correct/incorrect label for each, plus the two accuracy scores and the lift.

3. *Citation audit.* Ask five questions and verify each citation by hand: does the cited chunk actually support the claim? Compute a faithfulness rate (number of faithful citations divided by total citations).

   - *What to do:* For each of five questions, read the model's answer, find its cited source numbers (e.g., "[0]"), look up those document indices in the `docs` list, and judge: does the cited document actually say what the model claims it says?
   - *Starter hint:* A citation is "faithful" if a human reading the cited chunk would agree it supports the specific claim the model made. It is "unfaithful" if the model invented a detail not present in the chunk, even if the chunk is topically related. Your faithfulness rate = faithful citations / total citations.
   - *You've succeeded when:* You have a table of 5 questions, each model answer, each citation, your judgment (faithful/unfaithful), and a final faithfulness rate with one sentence explaining what that rate means for trust in this system.

4. *Failure taxonomy.* Find one *retrieval* failure (the right answer exists in the index, but the wrong chunk was fetched) and one *generation* failure (the right chunk was fetched, but the model produced the wrong answer anyway). Label which component owns each bug.

   - *What to do:* Print both `ctx` (retrieved context) and `answer` for each of your test questions. For retrieval failure: find a case where the retrieved chunk does NOT contain the answer but the answer IS in another document in `docs`. For generation failure: find a case where the retrieved chunk DOES contain the answer but the model's final answer contradicts or ignores the chunk.
   - *Starter hint:* Retrieval failures often happen when a question uses very different vocabulary from the relevant document (vocabulary mismatch). Generation failures often happen with complex multi-step reasoning or when the model's parametric memory contradicts the context.
   - *You've succeeded when:* You can show the `ctx` and `answer` for each failure case, explain which component (retriever or generator) produced the bug, and suggest one fix for each.

---

## Reflection Prompt

*Personal:* RAG lets a small private model answer questions about *your* documents without those documents ever leaving your machine. Identify one collection of documents in your life (notes, club records, family archive) you would index, and one you would refuse to index even locally. What distinguishes them?

*Technical:* In your notebook: the `rag_answer` function instructs the model to say "not in my documents" rather than guess. But what if a user needs an answer and it genuinely is not in the index? Design a fallback strategy that is more helpful than silence but less dangerous than hallucination.

*Societal:* Institutions (hospitals, courts, schools) could use RAG to give staff instant access to policy documents. Name one benefit and one risk of a hospital deploying RAG over its clinical guidelines. Who would need to audit the system, and how often?

---

## → Coming Up Next

Our RAG system worked because our "documents" were clean, single-sentence facts. Real documents are messy — long, overlapping, poorly organized. The *RAG Quality: Chunking, Clustering, and Reranking* activity takes this up next: how you cut documents into chunks determines what you can find, and we will build the tools to measure and improve retrieval quality — the same levers you will tune in the RAG Knowledge Base Lab.

---

## 4. Further Reading

- Patrick Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *NeurIPS* (2020). The original RAG paper.
- Chroma documentation: https://docs.trychroma.com
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 4.
