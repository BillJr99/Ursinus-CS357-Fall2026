<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-rag.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-rag.md

import: https://raw.githubusercontent.com/LiaTemplates/Pyodide/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# RAG: Building and Measuring a Knowledge Base

**Retrieval-augmented generation (RAG)** hands the model the right evidence at the moment it needs it.  The evaluation harness from the *Hallucinations and Evaluating Agent Outputs* activity showed that local models hallucinate (confidently make up facts) where their training data is thin.  The [*Tokens, Embeddings, and Attention*](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/TokensEmbeddingsAttention) tutorial gave you semantic search.  RAG combines the two.  On Tuesday, *How I AI* asked when handing an agent your whole `wiki/` folder stops working; today is the answer.  You build the pipeline in about fifty lines of Python with Chroma and Ollama, and then you learn the two things that decide whether it works on real documents: where the chunk boundaries go, and how to measure whether retrieval found the right chunk (recall@k).  We move from **the open-book insight → a working pipeline in code → chunking → measuring retrieval**.

The [RAG Knowledge Base lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RAGKnowledgeBase) is handed out at the next session, *RAG Worked Example: Build the Pipeline Together* (Tuesday, November 3), which builds the lab's pipeline end to end on both of its routes, a Pydantic AI agent in code and a Langflow flow without code, and measures it.  The lab is due Thursday, November 12.  The [Tools and MCP lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/ToolsMCP) is due at that same next session.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, respond to the reflective prompt on your own in your notebook.

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
| **Chunk** | A piece of a document that gets its own embedding and its own slot in the vector database. Too big and the embedding blurs across topics; too small and the chunk loses its context. | A 200-token excerpt from the student handbook parking section |
| **Overlap** | The number of tokens repeated between adjacent chunks so that a fact straddling a boundary appears intact in at least one chunk. | Chunk size 200 with overlap 50 |
| **Recall@k** | The fraction of test questions for which the correct chunk appears somewhere in the top-k retrieved results. It measures whether retrieval finds the right content at all, before the model sees it. | recall@3 = 0.80 means 80% of questions had the right chunk somewhere in the top 3 |
| **Golden set** | A small, fixed set of questions with the chunk (and answer) each one should find, written before you tune anything, so every configuration is scored against the same test. | The five questions in Model 4 |

---

## Today's Plan

Anything marked self-paced is for outside class, and nothing graded assumes it.

1. Part I, the open-book exam insight (Model 1)
2. Part II, build it in code: chunk, embed, store, retrieve, generate, and the abstention test (Model 2)
3. Part III, chunking: where the boundaries go and what they cost you (Model 3)
4. Part IV, measuring retrieval: score a golden set by hand, then compute recall@k (Model 4), and what a reranker adds
5. Reflection prompt.  The Langflow and Pydantic AI routes, which Tuesday's worked example builds in class, and the remaining Extensions are self-paced

---
# Part I: The Open-Book Exam Insight

## 1.  Parameters Versus Context

In this Part you will distinguish the two kinds of memory a language model has (the knowledge baked into its parameters during training versus the text currently in its prompt) and see why RAG turns a hard "closed-book" question into a much easier "open-book" one.

**Why this matters:** Ask someone a trivia question about an obscure historical event.  If they do not know it, they either admit ignorance or make something up, and AI models make something up convincingly.  RAG is the equivalent of saying "look it up in the encyclopedia first, then answer."  The model goes from guessing to reading and summarizing, which is a job it does much better.

A model has two memories.  *Parametric memory* (from "parameters," the numbers learned during training) is whatever was baked into the weights: vast, fuzzy, frozen in time.  *Contextual memory* is whatever sits in the prompt right now: small, precise, current.  Hallucination (the model confidently stating something false) is what happens when we ask parametric memory for precision it does not have.  RAG converts the question from a closed-book exam into an open-book one:

$$
\text{answer} = \text{LLM}(\text{query} + \text{retrieve}(\text{query}, \mathcal{D}))
$$

where $\mathcal{D}$ is your document collection and $\text{retrieve}$ selects the top-$k$ chunks (passages) by embedding similarity, the same cosine machinery from the tokens and embeddings tutorial.

> **Common Misconception:** The retrieval `top_k` / `k` here (how many *document chunks* to fetch, set as `n_results` in the code below) is a different knob from the **sampling `top_k`** decoding parameter in the [*Sampling, Temperature, and Generation*](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/SamplingAndTemperature) tutorial.  Same name, different layer: sampling `top_k` truncates the model's probability distribution over the *next token*; retrieval `k` sets the size of the *search result set* pasted into the prompt.  Turning up retrieval `k` gives the model more to read; it has nothing to do with how randomly it writes.

The pipeline has two phases.  *Indexing* (once): split documents into chunks, embed each chunk, store the vectors in a vector database.  *Query* (every question): embed the question, find the nearest chunks, paste them into the prompt with instructions to answer *only* from the provided context, and cite which chunk supports each claim.

---

## Model 1: Pipeline Tracing

A student asks a campus RAG system, "Can first-year students bring cars?"  The system retrieves a parking policy chunk and a housing FAQ chunk, then answers with a citation.

### Critical Thinking Questions

1.  Walk the question through both phases: which steps happened months ago at indexing time, and which steps happen right now at query time?

   > *Hint: Indexing steps read documents and store vectors: work done once before any user asks a question.  Query steps happen in real time after the user sends a message.  Sort each step: (a) embed the parking policy, (b) embed the user's question, (c) run cosine similarity search, (d) paste chunks into a prompt, (e) split the handbook into chunks, (f) generate the answer.*

2.  The model answers correctly, citing the parking chunk.  Is this *parametric* or *contextual* memory at work?  How can you tell from the citation?

   > *Hint: If the answer came from parametric memory, could the model cite a specific numbered source?  Citations in RAG point to retrieved text that was placed in the prompt; which type of memory is that?*

3.  Suppose the policy changed last week and the index is stale (out of date).  Where exactly does the wrong answer enter the pipeline, and which component is at fault: the model, the retriever, or the index?

   > *Hint: The model answered faithfully from the context it was given.  The retriever found the most similar chunk.  The chunk it found contained old information.  Which component produced that old chunk?*

---

# Part II: Building It

## 2.  A Complete Local RAG System

In this Part you will implement the two-phase RAG pipeline in Python using Chroma as the vector database and Ollama as the language model.  You will see how the indexing phase and query phase from Part I map onto real function calls, and you will test what happens when the answer is not in the index.

Chroma is an embeddable vector database (a library that stores embeddings and performs nearest-neighbor search, installable as a Python package).  Install it with `pip install chromadb`.  Everything below runs on your laptop; no data leaves the room.

The code has two phases.  The **indexing phase** (run once) creates the collection and stores an embedding for each document.  The **query phase** (run per question) embeds the user's question, finds the closest document chunks, and asks the model to answer using only those chunks.

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

**Why this matters:** The second query ("What time does the bookstore close?") tests an important design decision: what should the system do when the right answer is not in the index?  A bare language model will often invent a plausible answer ("The bookstore closes at 5pm on weekdays").  A well-designed RAG system says it does not know.  That difference, between confident invention and abstention, is what makes RAG trustworthy for high-stakes uses like medical information, legal research, or campus policy.

### Critical Thinking Questions

4.  The second question has no answer in the index.  Compare the system's behavior with what the bare model does (try it by calling `chat(question)` directly).  Which hallucination category from the *Hallucinations and Evaluating Agent Outputs* activity did the RAG instructions convert into abstention?

   > *Hint: Run `chat("What time does the bookstore close?")` without any context and observe the response.  Then look at the line in `rag_answer` that contains the phrase "not in my documents"; what instruction creates the abstention behavior?*

5.  Identify the precise line of the prompt that creates that abstention behavior.  What happens if you delete it?  Test and report.

   > *Hint: The key phrase is "If the context does not contain the answer, say 'not in my documents'."  Remove that phrase from the prompt string, re-run the bookstore question, and observe whether the model now invents an answer.*

6.  Set `k=1` and ask a question whose answer spans two documents.  What failure occurs, and what does it suggest about choosing $k$?

   > *Hint: Create a question like "Can I get food after working out at the gym?"; the answer involves both the dining hours doc and the athletics doc.  With `k=1`, only one chunk fits in the prompt.  What does the model say?*

> **Common Misconception:** RAG does not teach the model new facts, and it does not fine-tune or update the model in any way.  The model's weights are unchanged.  RAG places text in the prompt for the model to read and summarize, the same way you could hand a book to someone who has never seen it and ask them questions from it.  The intelligence is in the language model; the facts come from your documents.  So RAG is only as accurate as your documents, and if your documents contain errors, the model will faithfully repeat them.

**Three ways to change an answer.**  Keep these apart, because people often blur them:

| | Prompt only | RAG | Fine-tuning (LoRA) |
|---|---|---|---|
| What changes | Only the words you send | The text placed in the prompt, chosen by a search | The model's weights, through a small trained adapter |
| Do the generator's weights change? | No | No | Yes, but only while the adapter is loaded or merged |
| Which models are involved | One generator | An **embedding model** that searches (here `nomic-embed-text`) and a separate **generator** that writes (here `llama3.2`) | The generator, plus an adapter trained for that exact base model |
| A fact changes | Edit the prompt | Re-index one document | Collect data and train again |
| Good at | Instructions and examples | Specific, current, citable facts | Format, tone, and when to refuse |
| Guarantees the answer is true? | No | No: the model can still misread a correct passage | No: it can state a trained fact confidently and wrongly |

The embedding model never writes an answer, and the generator never searches; RAG works only because both sit in one pipeline.  The Extension on fine-tuning at the end of this page covers the third column, and *Offline RAG and LoRA, End to End* (https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OfflineRAGFineTuning) builds all three on one machine and compares them on held-out questions.

The single most important reason RAG reduces factual hallucination is that it:

[( )] Increases the model's parameter count at query time
[(X)] Moves the burden of factual precision from parametric memory to text supplied in the context
[( )] Lowers the sampling temperature automatically
[( )] Fine-tunes the model on your documents

---

# Part III: Chunking

## 3.  The Goldilocks Problem

**How you cut a document into chunks determines what you can find.**  The pipeline in Part II worked because our "documents" were single tidy sentences.  Real documents are messy: long, overlapping, poorly organized.  In this Part you will see why the size of text chunks matters for retrieval quality, examine three splitting strategies, and write a hybrid policy you can apply to your own documents in the RAG Knowledge Base lab.

**Why this matters:** Compare searching a book by its table of contents (chapters as chunks) with searching it sentence by sentence (sentences as chunks).  A chapter might run 50 pages; one embedding has to summarize all 50 into a single vector, which blurs the meaning across dozens of topics.  A sentence is precise but often meaningless alone: "He approved the request" tells you nothing about *who*, *what*, or *why*.  Good chunking finds the passage-length sweet spot: self-contained enough to stand alone and focused enough to embed well.  It is the highest-value tuning knob in any real RAG system.

**Chunks too large** dilute the embedding (one vector must summarize many topics) and waste context window space.  **Chunks too small** orphan their meaning ("He approved the request" retrieves nothing useful without knowing who *he* is).  Practical systems balance three strategies:

| Strategy | How It Works | Best For | Trade-Off |
|----------|-------------|----------|-----------|
| **Fixed-size** | Split every N tokens, with overlap O tokens repeated between adjacent chunks (e.g., chunks of 200 tokens with 50-token overlap) | Simple documents where you want predictable chunk counts and easy tuning | Ignores sentence and paragraph structure; can split a key sentence across two chunks even with overlap |
| **Structural** | Split on natural document boundaries (headings, paragraph breaks, bullet items) respecting how the author organized the content | Well-structured documents like policies, manuals, or textbooks with clear sections | One section might be 50 tokens and another 2,000 tokens, creating uneven retrieval quality |
| **Semantic** | Split where the embedding similarity between consecutive sentences drops sharply, detecting topic shifts algorithmically | Long documents with many topic shifts where structural markers are sparse | More complex to implement; requires embedding every sentence before chunking |

Overlap repairs boundary damage: with chunk size 200 and overlap 50, a fact straddling a boundary appears intact in at least one chunk.  The cost is a bigger index, because every overlapped token is embedded and stored twice; at those settings the index grows by about a third.

The lab's `index.py` uses the structural strategy at its simplest: it splits each file on blank lines, so one paragraph becomes one chunk.  Its no-code route uses Langflow's recursive character splitter, a fixed-size strategy that prefers to break at paragraph and sentence boundaries.

---

## Model 3: Cut This Document

Consider a 12-page student handbook with sections on housing, dining, conduct, and parking, where the parking rules paragraph begins with "Exceptions to the above:".

### Critical Thinking Questions

7.  A fixed 500-token chunker splits mid-sentence between "the above" rules and the exceptions.  Describe the wrong answer a RAG system would confidently give about parking, and which chunking strategy prevents it.

   > *Hint: The exception chunk starts with "Exceptions to the above:" but the "above" rules are in the previous chunk.  If a student asks "Are there exceptions to the parking rule?", the system retrieves the exceptions chunk but the model cannot know what rule is being excepted.  What answer might it fabricate?  Which chunking strategy keeps the rule and its exceptions together?*

8.  Structural chunking yields one enormous "conduct" chunk.  What goes wrong at *embedding* time (when the vector is created), and what goes wrong at *prompt assembly* time (when the chunk is pasted into the prompt)?

   > *Hint: At embedding time: one vector has to represent 3,000 tokens covering academic honesty, social conduct, residence hall policies, and disciplinary procedures.  What happens to the "meaning direction" of that vector?  At prompt assembly: if this chunk is retrieved, how much of your 4,000-token context window does it consume?*

9.  Propose a hybrid policy for the handbook (one sentence per rule), and have the Recorder write it as if it were documentation for the RAG Knowledge Base lab.

   > *Hint: A hybrid policy might say: "Use structural splits on section headings first, then apply fixed-size chunking with 50-token overlap within any structural chunk larger than 400 tokens, with a minimum chunk size of 100 tokens."  Write this as a numbered specification your lab partner could implement.*

---

# Part IV: Measuring Retrieval

## 4.  Recall@k and the Golden Set

In this Part you will learn how to measure whether your retrieval system is working, using recall@k, and see how a reranker can raise precision without giving up recall.

**Why this matters:** You cannot improve what you cannot measure.  Before tuning chunk size, overlap, or any other parameter, you need a metric that tells you whether retrieval is working.  If recall@3 is 0.50, half your questions get the wrong chunk and therefore a possibly hallucinated answer, no matter how good your language model is.  Generation quality has a ceiling set by retrieval quality, and this Part gives you the tool to find that ceiling.

**Recall@k**, in plain terms: take a set of test questions where you have already located the chunk that answers each one.  That set is your **golden set**, and you write it before you tune anything, so every configuration you try is scored against the same test.  For each question, retrieve the top $k$ chunks and check whether the right chunk is among them: score 1 if it is, 0 if it is not.  Recall@k is the average of those scores:

$$
\text{recall@}k = \frac{1}{|Q|} \sum_{q \in Q} \mathbb{1}\left[\text{gold}(q) \in \text{top}_k(q)\right]
$$

A score of 1.0 means every question had its answer chunk in the top $k$; a score of 0.5 means half did.  Recall@k says nothing about whether the generated answer was right.  It tells you whether the model was ever *given* the evidence it needed, which is the first thing to check when an answer is wrong.

## Model 4: Score This Retrieval

A retriever over the five campus documents from Part II returned the three chunks below for each of five golden-set questions, best match first.  The last column is the chunk a person marked as the one that answers the question.

| Question | Retrieved (rank 1, 2, 3) | Gold chunk |
|---|---|---|
| Q1. Can a first-year student keep a car on campus? | doc0, doc3, doc4 | doc0 |
| Q2. When does the library close on a Tuesday? | doc1, doc2, doc0 | doc1 |
| Q3. Who has to sign off before I register for classes? | doc0, doc3, doc1 | doc3 |
| Q4. Can I eat dinner at 7:30 on a Wednesday? | doc1, doc4, doc2 | doc2 |
| Q5. Do I need my ID card to use the gym? | doc0, doc1, doc3 | doc4 |

Score recall@1, recall@2, and recall@3 by hand before you run the cell.  Then run it and check your arithmetic.

```python
retrieved = {
    "Q1": ["doc0", "doc3", "doc4"],
    "Q2": ["doc1", "doc2", "doc0"],
    "Q3": ["doc0", "doc3", "doc1"],
    "Q4": ["doc1", "doc4", "doc2"],
    "Q5": ["doc0", "doc1", "doc3"],
}
gold = {"Q1": "doc0", "Q2": "doc1", "Q3": "doc3", "Q4": "doc2", "Q5": "doc4"}

def recall_at_k(retrieved, gold, k):
    """The share of questions whose gold chunk appears in the top k."""
    hits = [gold[q] in retrieved[q][:k] for q in gold]
    return sum(hits) / len(hits)

for k in (1, 2, 3):
    misses = [q for q in gold if gold[q] not in retrieved[q][:k]]
    print(f"recall@{k} = {recall_at_k(retrieved, gold, k):.2f}   missed: {misses}")
```
@Pyodide.eval

You should see recall@1 = 0.40, recall@2 = 0.60, and recall@3 = 0.80, with Q5 missed at every $k$.

### Critical Thinking Questions

10.  Q5 asks about "the gym" and its gold chunk says "the Floy Lewis Bakes Center."  Using what you know about embeddings, explain why this question is the one that misses at every $k$, and name one change to the *chunk* (not to the retriever) that would likely fix it.

    > *Hint: Vocabulary mismatch.  The question and the chunk describe the same place in words that rarely appear together.  What could you add to the chunk's text so that a search for "gym" lands near it?*

11.  The prompt in Part II fits two chunks (`k=2`).  Raising $k$ to 3 lifts recall from 0.60 to 0.80 in this table.  Name what that extra 0.20 costs at generation time, and say how you would decide whether to pay it.

    > *Hint: Every extra chunk is more text for the generator to read, and the most relevant chunk can land in the middle.  Which measurement would tell you whether answers got better, not just whether retrieval did?*

A two-stage design retrieves generously and then filters precisely.  A fast vector search proposes, say, 20 candidates (high recall; the right chunk is almost certainly in there), and a **reranker** (a slower model that scores each query-chunk pair directly) reorders them so the truly relevant chunk rises into the top 3 that fit the prompt (high precision).  Even an LLM prompted with "Rate the relevance of this passage to this question from 0 to 10" makes a serviceable reranker, our first taste of models evaluating text for other models.

A system has recall@20 of 0.95 but recall@3 of 0.50, and the prompt only fits 3 chunks.  The highest-leverage fix is:

[( )] A larger generation model
[( )] Smaller chunks with more overlap
[(X)] A reranking stage between retrieval and prompt assembly
[( )] Raising the temperature of the generator

Recall@k measures the retriever.  The other half of the measurement is **grounding**: does each claim in the answer actually appear in the chunk it cites?  Tuesday's worked example measures both on one small corpus, recall@k with the function above and grounding with a citation check, and the lab's five-question transcript asks you to note, for every answer, whether its named source actually says it.

---

# Part V: Synthesis and Practice

## 5.  Exercises

In this Part you apply the pipeline and the measurements to real documents you choose.  These exercises build directly toward the RAG Knowledge Base lab, on either route: run them in Python, or in a Langflow flow (the Extension below and Tuesday's worked example show the canvas).

1.  *Your own corpus.*  Replace the five documents with ten sentences from a syllabus, club constitution, or campus page of your choosing.  Demonstrate one question answered correctly with a citation and one abstention.

   - *What to do:* Find a real document (your CS357 syllabus, a club's bylaws, the college's honor code).  Extract 10 meaningful sentences.  Index them in Chroma.  Ask five questions; at least two should be unanswerable from your documents.
   - *Starter hint:* Copy your chosen sentences into the `docs` list, replacing the campus FAQ.  Make sure each sentence is self-contained (contains enough context to be understood in isolation; avoid sentences like "As stated above, the deadline is...").
   - *You've succeeded when:* You can show one output where the model correctly cites a source number, and one output where it says "not in my documents" for a question whose answer does not appear in your ten sentences.

2.  *Citation audit.*  Ask five questions and verify each citation by hand: does the cited chunk support the claim?  Compute a faithfulness rate (number of faithful citations divided by total citations).

   - *What to do:* For each of five questions, read the model's answer, find its cited source numbers (e.g., "[0]"), look up those document indices in the `docs` list, and judge: does the cited document say what the model claims it says?
   - *Starter hint:* A citation is "faithful" if a human reading the cited chunk would agree it supports the specific claim the model made.  It is "unfaithful" if the model invented a detail not present in the chunk, even if the chunk is topically related.
   - *You've succeeded when:* You have a table of 5 questions, each model answer, each citation, your judgment (faithful/unfaithful), and a final faithfulness rate with one sentence explaining what that rate means for trust in this system.

3.  *Failure taxonomy.*  Find one *retrieval* failure (the right answer exists in the index, but the wrong chunk was fetched) and one *generation* failure (the right chunk was fetched, but the model produced the wrong answer anyway).  Label which component owns each bug.

   - *What to do:* Print both `ctx` (retrieved context) and `answer` for each of your test questions.  For a retrieval failure: find a case where the retrieved chunk does NOT contain the answer but the answer IS in another document in `docs`.  For a generation failure: find a case where the retrieved chunk DOES contain the answer but the model's final answer contradicts or ignores the chunk.
   - *Starter hint:* Retrieval failures often happen when a question uses very different vocabulary from the relevant document (vocabulary mismatch, as in Q5 of Model 4).  Generation failures often happen with multi-step reasoning or when the model's parametric memory contradicts the context.
   - *You've succeeded when:* You can show the `ctx` and `answer` for each failure case, explain which component (retriever or generator) produced the bug, and suggest one fix for each.

4.  *Chunking shootout.*  Take one real page of a campus document.  Index it three ways (fixed 100 tokens no overlap, fixed 300 tokens with 75-token overlap, paragraph-structural).  For five questions with known answers, report which indexing strategy wins recall@2, and explain the winner.

   - *What to do:* Implement three versions of the chunker and create three separate Chroma collections.  For 5 questions where you know which paragraph contains the answer, run all three and check whether the answer paragraph appears in the top 2 results.
   - *Starter hint:* For fixed chunking: `chunks = [text[i:i+n] for i in range(0, len(text), n-overlap)]`.  For paragraph structural: `chunks = [p.strip() for p in text.split('\n\n') if p.strip()]`.  Score each configuration with `recall_at_k` from Model 4.
   - *You've succeeded when:* You have a table with 3 rows (one per chunking strategy) and 5 question columns (1 = retrieved, 0 = not), plus a recall@2 score for each strategy and a one-sentence explanation of why the winner worked best for this particular document.

5.  *Recall curve.*  For a draft of your RAG Knowledge Base lab corpus, plot recall@k for $k \in \{1, 2, 3, 5, 10\}$, and choose the $k$ you will ship, defending the choice in two sentences that mention both context budget and accuracy.

   - *What to do:* Build a golden set of 10 questions with labeled relevant chunks.  Run your Chroma search with `n_results=10` for each question, and compute recall@k for each $k$.
   - *Starter hint:* `[recall_at_k(retrieved, gold, k) for k in (1, 2, 3, 5, 10)]`, then `plt.plot([1, 2, 3, 5, 10], curve)`.
   - *You've succeeded when:* You have a plotted recall curve and a written justification that explicitly trades off "more chunks, higher recall" against "fewer prompt tokens remaining for the answer."

6.  *Build a reranker.*  Wrap your local model in a relevance-scoring prompt, rerank 10 retrieved candidates for three questions, and report the rank change of the truly relevant chunk.

   - *What to do:* Retrieve the top 10 chunks for 3 questions.  For each chunk, call the model with a prompt like: "On a scale of 0 to 10, how relevant is the following passage to the question '{question}'?  Passage: '{chunk}'.  Reply with only a number."  Sort by score and report the new rank of the chunk you know is correct.
   - *Starter hint:* Parse the reply with `int(...)` inside a `try`, and treat an unparseable reply as 0 so one bad reply cannot crash the ranking.
   - *You've succeeded when:* For at least 2 of 3 questions, the correct chunk's rank improves after reranking, and you can explain in one sentence why the initial vector search placed it lower.

---

## Reflection Prompt

*Personal:* RAG lets a small private model answer questions about *your* documents without those documents ever leaving your machine.  Identify one collection of documents in your life (notes, club records, family archive) you would index, and one you would refuse to index even locally.  What distinguishes them?

*Technical:* In your notebook: chunking is an editorial act, in which someone (or some algorithm) decides where meaning begins and ends.  When you index a document written by someone else, what obligations do you have to preserve its meaning, and how would you check, with a number, whether your pipeline honored them?  Then: the `rag_answer` function instructs the model to say "not in my documents" rather than guess.  Design a fallback that is more helpful than silence but less dangerous than hallucination.

*Societal:* A law firm deploys RAG over 10,000 legal documents to help paralegals find relevant precedents.  The chunking strategy splits some court opinions mid-sentence, occasionally separating the holding (the decision) from its reasoning.  Who is harmed if the system retrieves the holding without the reasoning?  What audit, run how often and by whom, would you require before deploying such a system?

---

## -> Coming Up Next

In *RAG Worked Example: Build the Pipeline Together* (Tuesday, November 3) we build one complete knowledge base end to end, exactly the way the RAG Knowledge Base lab asks: ingest a small folder of documents, chunk it, embed it, retrieve, generate a grounded answer that names its source, and then measure recall@k and grounding on that corpus, showing the intermediate output at every step.  We build it twice, as the lab's Pydantic AI agent and as its Langflow flow, and the lab is handed out at the end.  Have today's `recall_at_k` function and your hybrid chunking policy from Question 9 ready.

---

## 6.  Further Reading

- Patrick Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."  *NeurIPS* (2020).  The original RAG paper.
- Chroma documentation: https://docs.trychroma.com
- Nils Reimers.  "Retrieve and Re-Rank" (Sentence-Transformers documentation, online).
- Liu et al. "Lost in the Middle."  *TACL* (2024), on why chunk *placement* in the prompt also matters.
- *Offline RAG and LoRA, End to End*, which rebuilds today's pipeline with a persistent Chroma store that survives a restart, runs with the network unplugged, puts it behind a Pydantic AI agent, and then trains and compares a LoRA adapter: https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OfflineRAGFineTuning
- Melanie Mitchell.  *AI: A Guide for Thinking Humans*, Chapter 4.

---

# Extension: The Same Pipeline Without Code (self-paced)

The same pipeline can be built on a Langflow canvas instead of in Python.  The RAG Knowledge Base lab's code route uses Pydantic AI, and its no-code route is this canvas, for the same credit.  Tuesday's worked example builds the lab's flow in class; this Extension builds it once on the five campus documents from Part II, if you want to try the canvas before then.

Langflow is a visual editor for language-model pipelines: each step is a node you configure in a side panel and wire to the next by dragging a connection.  The [*Visual Agents*](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/VisualAgents) tutorial walks through the install and a first flow; that tutorial carries the exact node names for its version of Langflow.  On the canvas, the code cell above becomes three nodes:

| Node | What it does | The code it replaces | The setting you carry over |
|---|---|---|---|
| **Index** | Loads your document files, splits them into chunks, embeds each chunk with `nomic-embed-text`, and stores the vectors in a Chroma collection | The `docs` list, `embed()`, and `col.add(...)` | Chunk size and overlap (our five one-sentence documents are one chunk each; a real corpus needs a splitter) |
| **Retrieve** | Embeds the incoming question and pulls the nearest chunks from the same Chroma collection | `col.query(query_embeddings=..., n_results=k)` | Top-k, the same number as `k=2` in `rag_answer` |
| **Generate** | Fills a prompt template with the retrieved chunks and the question, then sends it to `llama3.2` on your local Ollama | The prompt string and `chat()` | The grounding instruction ("answer using ONLY the context") and the abstention phrase |

Nothing about the pipeline changes.  The chunk size, the top-k, the model name, and the prompt are the same decisions; they live in node settings instead of variables.  The canvas makes the retrieval step visible (the playground shows which chunks the Retrieve node handed forward, which is what you print as `ctx` in code), and it hides the error handling that `embed()` and `chat()` wrap around every network call.  Whichever route you take in the lab, the graded work is the same: an index over documents you chose, answers that name their sources, an abstention when the answer is not there, and one question asked with retrieval switched off.


## Build It on the Canvas

The four steps below rebuild Part II's cell on the canvas.  Node names shift a little between Langflow versions; the dataflow is what matters, and the [*Visual Agents*](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/VisualAgents) tutorial shows the same wiring with screenshots.

### Step A: Install and Launch Langflow

Langflow runs as a local web server: `langflow run` starts it, and you work in it through your browser.  The first install pulls a couple of gigabytes of dependencies, so start it before class if you can.

```bash
pip install langflow
langflow run
ollama pull nomic-embed-text
```

> **You should see.** A "Langflow is running" banner in the terminal, the canvas at `http://localhost:7860`, and `nomic-embed-text` and `llama3.2` in the output of `ollama list`.

> **If it fails.** A dependency-resolver error from `pip install langflow` usually means your Python is too new or too old; create a fresh virtual environment on Python 3.11 or 3.12 and install there.  If `localhost:7860` refuses to connect, the server is still starting, so wait for the banner.

### Step B: The Index Path

Create a **New Flow** from a **Blank Canvas**.  Save the five campus sentences from Part II in a file named `campus.txt`, one per paragraph, and wire:

1.  **File**: upload `campus.txt`.
2.  **Text Splitter** (the recursive character splitter): chunk size 200, overlap 0, so each sentence stays one chunk, as in Part II.
3.  **Ollama Embeddings**: model `nomic-embed-text`, Base URL `http://localhost:11434`.
4.  **Chroma**: name the collection `campus`, with the File and Ollama Embeddings outputs wired in.

> **You should see.** Running the Chroma node finishes without an error, and its inspection view lists five stored chunks.

### Step C: The Query Path

On the same canvas, wire the per-question path:

1.  **Chat Input** to the **Chroma** node's search input (the same collection, with the same **Ollama Embeddings** node wired in for the question), with the number of results set to 2, our `k`.
2.  **Prompt**: paste the template below.  Wire the search results into `{context}` and the Chat Input into `{question}`.
3.  **Ollama**: model `llama3.2`, temperature 0, Base URL `http://localhost:11434`.
4.  **Chat Output**.

```text
Answer using ONLY the context below. Cite the bracketed source number.
If the context does not contain the answer, say 'not in my documents'.

Context:
{context}

Question: {question}
```

> **If it fails.** A connection refusal at run time means a node's Base URL is wrong or Ollama is not running.  An answer with no context in it means the search results are not wired into `{context}`.

### Step D: Ask the Same Two Questions

Open the **Playground** and ask Part II's two questions: "Can a first-year student keep a car on campus?" and "What time does the bookstore close?"

> **You should see.** The car question answered from the parking chunk, and "not in my documents" for the bookstore.  Open the inspection view on the search step to see which chunks it handed forward: that is the canvas version of printing `ctx`.

### Questions to Work Through

1.  Question 5 asked you to delete the abstention phrase and watch the model invent a bookstore closing time.  Which of the three nodes holds that phrase on the canvas, and what would you change to run the same experiment there?

   > *Hint: The prompt template is a setting of one node.  The experiment is the same edit in a different text box.*

2.  Question 6 asked you to set `k=1`.  Name the node and the setting that corresponds to `k`, and explain why changing it does not require re-indexing the documents.

   > *Hint: Top-k is read at query time, after the index exists.  Which phase from Part I does the Index node belong to, and which phase does the Retrieve node belong to?*

---

# Extension: The Same Pipeline as a Pydantic AI Agent (self-paced)

Part II decided, in our code, that every question gets a retrieval step.  An agent can make that decision itself.  We give it the search as a **tool**, exactly like the tools in the *Tool Use* session, and the instructions tell it to search before it answers.  This is the shape the RAG Knowledge Base lab's code route uses, and Tuesday's worked example builds the lab's version in class; here it runs on the five campus documents from Part II.

Pydantic AI is the agent framework from [*Pydantic AI From the Loop Up*](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/PydanticAI).  Install it with `pip install "pydantic-ai-slim[openai]==2.54.0"` and pull a model that calls tools reliably with `ollama pull qwen2.5:3b`.

## Code Cell: RAG as a Tool

> **Runs on your machine, not here.**  Run it in the same session as the Part II cell: it reuses `embed()` and the `col` collection you built there.

```python
import os
import traceback

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from pydantic_ai import Agent, UsageLimits
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider

model = OpenAIChatModel("qwen2.5:3b", provider=OllamaProvider(base_url="http://localhost:11434/v1"))

agent = Agent(
    model,
    instructions=("Answer questions about campus. Always call search_documents first, answer only from "
                  "what it returns, and cite the bracketed document id. If the passages do not contain "
                  "the answer, say 'not in my documents'."),
    model_settings={"temperature": 0.0, "seed": 42},
)


@agent.tool_plain
def search_documents(query: str) -> str:
    """Searches the campus documents and returns the two most relevant passages with their ids.

    Args:
        query: What to search for, in plain words.
    """
    try:
        hits = col.query(query_embeddings=[embed(query)], n_results=2)   # the Part II collection
    except Exception as e:
        print(f"[rag:search_documents] {e}")
        traceback.print_exc()
        raise
    return "\n".join(f"[{i}] {d}" for i, d in zip(hits["ids"][0], hits["documents"][0]))


for question in ["Can a first-year student keep a car on campus?", "What time does the bookstore close?"]:
    try:
        result = agent.run_sync(question, usage_limits=UsageLimits(request_limit=4))
    except Exception as e:
        print(f"[rag:agent] {e}")
        traceback.print_exc()
        continue
    calls = [p for m in result.all_messages() for p in m.parts if p.part_kind == "tool-call"]
    print(f"Q: {question}\n  tool calls: {[c.args for c in calls]}\n  A: {result.output}\n")
```

Two things moved.  The prompt-building in `rag_answer` is gone: the agent receives the passages as the tool's result instead of as text we pasted into its prompt.  And the retrieval step is now the model's choice, which is why the code prints the tool calls.  An agent that answers without calling `search_documents` is answering from memory, and the printout is how you would catch it.

### Questions to Work Through

1.  Run the cell and read the `tool calls` line for each question.  Did the agent search before answering both times?  If it skipped the search on one, what in the instructions or the docstring would you change?

   > *Hint: The model chooses tools from their descriptions.  A docstring that says when to use the tool is part of the prompt.*

2.  In Part II, our code always retrieved.  Here the model decides.  Name one question where letting the model decide is better, and one where it is worse.

   > *Hint: Think about a greeting, and about a question that sounds general but has a campus-specific answer.*

---

# Extension: Seeing Your Corpus with Semantic Clustering (self-paced)

**Why this matters:** Before you build a RAG system over a large document collection, you need to know what you have.  How many distinct topics does your corpus cover?  Are there subjects with no coverage?  Are there many near-duplicate chunks that waste index space and confuse retrieval?  Clustering the embeddings gives you an automatic map of the corpus's topic structure, the way a heat map of a city shows where neighborhoods cluster without your reading every street address.

Embeddings let us *map* a document collection before querying it.  Clustering chunk vectors (k-means on normalized embeddings approximates clustering by cosine similarity) reveals the topics your corpus contains, exposes duplicates, and flags off-topic contamination.

---

The code below embeds eight campus-policy chunks with a local model, then runs k-means clustering (a method that groups items into k groups by finding the assignments that minimize total distance to each group's center) on the normalized embedding vectors.  After running it, you will read the cluster output and judge whether the algorithm found the same topic structure a human would draw.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

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
        print(f"[rag:cluster_embed] {e}")
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

Two cautions before you trust the map.  The clusters are an artifact of $k$ as much as a fact about your documents: we chose 3, and choosing 8 on this data gives eight singleton clusters, each perfectly "coherent" and useless.  And the code normalizes the vectors first because k-means measures straight-line distance while retrieval ranks by cosine; on normalized vectors the two agree, and on un-normalized vectors long documents drift into their own cluster because they are long, not because they are about anything.

## Reading the Map

**Why this matters:** The clusters the algorithm produces may or may not match the categories a human would draw.  When they do not match, the mismatch is a window into what the embedding model "hears" in the text, and that tells you where your retrieval system will succeed and where it will fail.

### Questions to Work Through

1.  Did the clusters recover the human topics (parking, dining, housing)?  Identify any chunk the algorithm placed surprisingly, and hypothesize what feature of its wording caused it.

   > *Hint: "Room selection for returning students occurs in March" is about housing.  But does it share vocabulary with other housing chunks?  What words might cause it to cluster with a different group?  Look at overlapping words between the surprise chunk and the cluster it joined.*

2.  Why must we normalize the vectors before k-means if we intend cosine geometry?  Think about what k-means minimizes.

   > *Hint: K-means minimizes Euclidean distance (straight-line distance in space) to cluster centroids.  Cosine similarity ignores vector length and only measures direction.  If two vectors point in the same direction but one is 10 times longer, cosine similarity says they are identical (score 1.0), but Euclidean distance says they are far apart.  Normalizing (setting all vectors to length 1) makes Euclidean distance proportional to cosine distance.*

3.  Describe two concrete uses of this cluster map when curating the knowledge base for the RAG Knowledge Base lab: one use for finding *gaps* in your corpus, and one for finding *duplicates*.

   > *Hint: For gaps: if your corpus has 3 clusters but your users' questions span 5 topics, what does that tell you?  For duplicates: if one cluster contains 12 chunks and they all say nearly the same thing in slightly different words, what is the problem for retrieval and for prompt assembly?*

> **Common Misconception:** Many students assume that adding more documents always improves a RAG system.  In practice, adding off-topic, contradictory, or near-duplicate documents hurts retrieval quality.  A search engine that returns 20 near-identical parking regulations when you ask about dining hours is retrieving with high recall but low precision.  Corpus *quality* and *coverage* matter more than corpus *size*, and clustering is one of the best tools for auditing both.

---

# Extension: How the Search Finds Anything (self-paced)

Optional, and not assumed by anything above.  Chroma made retrieval look like one function call.  Underneath it is a distance metric, an index, and a set of tradeoffs that decide whether your pipeline stays fast at ten documents and at ten million.  You need this to debug retrieval when it starts returning the wrong thing, which it will.

## Why Brute Force Fails

In this part, you will see why checking every vector in a million-document database does not scale, and how two approximate nearest-neighbor algorithms (HNSW and IVF) solve the problem with indexing.

### The Scale Problem

Searching a vector database is like finding the most similar song in a music library, not by title, but by how it *sounds*.  If you had 1 million songs and had to listen to each one to decide which is most similar to your query, it would take forever.  ANN indexes are the equivalent of organizing songs by genre, tempo, and key so you can jump straight to the right neighborhood.

An embedding vector for a single sentence is a point in $\mathbb{R}^{d}$, where $d$ is 768 for `nomic-embed-text` (the model in our pipeline) and 1536 for OpenAI's `text-embedding-3-small`.  At query time, a RAG system must find the $k$ stored vectors closest to the query vector.  The naive approach computes the distance from the query to every stored vector.  For 1 million documents at 768 dimensions, that is $768 \times 10^6 \approx 7.7 \times 10^8$ multiply-adds per query, and about 3 GB of float32 vectors to stream through memory.  On a single CPU core that is a fraction of a second to about a second per query, with memory bandwidth as the bottleneck.  That may be tolerable for one user, but it does not scale to many concurrent queries or to a corpus ten or a hundred times larger.

**Approximate nearest-neighbor (ANN) search** accepts a small chance of missing the true nearest neighbor in exchange for a 100x to 1000x speedup.  Two algorithms dominate production systems:

- **HNSW (Hierarchical Navigable Small World, an approximate nearest-neighbor index that organizes vectors into a multi-layer graph so search can move quickly from coarse to fine-grained neighborhoods):** builds a multi-layer graph where each node connects to its approximate nearest neighbors.  Search starts at a coarse top layer and works downward, greedily jumping toward the query.  Think of it as a subway map where express lines get you close quickly, then local stops get you to the exact station.
- **IVF (Inverted File Index):** partitions the vector space into $n$ clusters (Voronoi cells) at index time.  At query time only the nearest few cluster centroids are searched.  Think of it as dividing a library into sections: you check the "Science" section, not every shelf.

---

### Distance Metrics

Distance functions do not all measure the same thing.  Choose the wrong one and semantically similar documents rank below dissimilar ones.  It is like choosing a ruler: a protractor measures angles, a tape measure measures length; both are "distance" tools that answer different questions.

| Scenario | Best Metric | Why | When to Use |
|---|---|---|---|
| Finding semantically similar sentences in a text retrieval system | Cosine similarity | Direction encodes meaning; vectors from the same model are already unit-normalized in most libraries, so magnitude differences are irrelevant. | Default choice for all text embedding retrieval; use this unless you have a specific reason not to. |
| Finding documents of similar "importance" where magnitude carries signal | L2 (Euclidean) distance | Magnitude differences are meaningful; two vectors far from the origin but close in angle are different in quantity or intensity, not just topic. | Image embeddings where pixel intensity matters; word count or frequency embeddings where raw size is meaningful. |
| Maximum inner product search for recommendation | Dot product | Relevance decomposes as magnitude × angle; used when popularity or frequency should interact with semantic similarity. | Recommendation systems where a popular item (high magnitude) should rank higher than an obscure but equally relevant item. |
| Comparing images embedded by a CLIP model with known unit norms | Cosine or dot product (equivalent when norms are 1) | Normalization makes them identical; use whichever the library exposes natively to avoid unnecessary computation. | Any embedding model that explicitly states it returns unit-normalized vectors, including `text-embedding-3-small` and `nomic-embed-text`. |

#### Critical Thinking Questions

1.  Most text embedding models (such as `nomic-embed-text` and OpenAI `text-embedding-3-small`) return L2-normalized vectors, meaning every vector has magnitude 1.  Show algebraically that for unit vectors, cosine similarity and dot product are identical.  Why does this simplification matter for implementation?

   *Hint:* Cosine similarity is defined as $\frac{u \cdot v}{||u|| \cdot ||v||}$.  What happens to the denominator when both vectors have magnitude 1?

2.  You index 50,000 legal briefs and 50,000 social media posts in the same collection.  A query about "contract breach" retrieves a mix of both.  What property of the embedding space caused this, and which metadata filter would you add to the ANN query to fix it?

   *Hint:* Both document types use the word "breach" but in very different contexts.  The embedding model was trained on mixed text.  What structured field (stored alongside the vectors, not in the vectors) would let you restrict results to one document type?

3.  HNSW builds its graph at index time.  What is the trade-off when you set the number of neighbors per node very high versus very low?  Consider index-build time, query time, and recall.

   *Hint:* More neighbors per node means more edges in the graph.  During search, more edges means more paths to explore.  During index construction, more edges means more distance calculations per inserted node.

---

## The Retrieval Pipeline

In this part, you will trace a complete RAG query through six pipeline steps (including embedding, ANN search, metadata filtering, and LLM generation) and learn to diagnose which step is responsible when the answer comes out wrong.

### From Query to Answer

Every RAG query passes through a fixed sequence of steps, like an assembly line where each station transforms the work piece and hands it to the next.  Knowing who owns each step is what makes debugging possible: when the answer is wrong, you need to find out whether to blame the embedding model, the ANN index, the metadata filter, or the language model.

### Pipeline Tracing

| Step | Component | Input | Output | What Can Go Wrong Here |
|---|---|---|---|---|
| 1. Query arrives | Application layer | Raw user question typed by the user | Plain text string | Query is ambiguous, misspelled, or in a different language than the indexed documents. |
| 2. Query is embedded | Embedding model (e.g., `nomic-embed-text`; install: `ollama pull nomic-embed-text`) | Text string | Float array (768-dim for `nomic-embed-text`) | Using a different embedding model than was used at index time causes a "dialect mismatch"; vectors are incomparable. |
| 3. ANN search | Vector database index (HNSW or IVF) | Query vector, $k$ (how many results to return) | Candidate document IDs with distances | If $k$ is too small, the correct document is excluded before the filter even runs. |
| 4. Metadata filter applied | Vector database filter engine | Candidate IDs, filter expression (e.g., `{"year": {"$gte": 2024}}`) | Filtered subset of IDs | Overly strict filters remove the correct document; overly loose filters let irrelevant documents through. |
| 5. Top-$k$ documents returned | Vector database | Filtered IDs | Document text + metadata | If chunks are too long, they waste context window space; if too short, they lack the context the LLM needs to answer. |
| 6. LLM generates with docs in context | Language model (e.g., `claude-sonnet-5-5`, `llama3.1:8b`) | Prompt = system instructions + retrieved chunks + user question | Answer string | LLM ignores the retrieved text and hallucinates from parametric memory; "lost in the middle" effect buries the relevant chunk. |

> **Common Misconception:** Many beginners assume that if the LLM gives a wrong answer, the problem must be the LLM itself.  **Check retrieval first.**  A perfect LLM cannot produce a correct answer if Step 3 or 4 returned the wrong documents.  Always check what was retrieved (Step 5's output) before debugging the LLM.

#### Critical Thinking Questions

4.  A user asks "What were the 2024 FDA guidelines on GLP-1 drugs?"  Your index was built in January 2024 and the guidelines were published in September 2024.  At which step does the failure occur?  What is the fix, and what is its operational cost?

   *Hint:* The failure happens at Step 3: the correct document was never indexed, so ANN search cannot return it.  The fix involves re-running the indexing pipeline.  How often would you need to do this for a regulatory database?

5.  Your system retrieves the correct documents at step 5, but the LLM's answer contradicts them.  Which step is at fault?  What experiment would you run to confirm this before changing the prompt?

   *Hint:* Before changing anything, print the exact retrieved chunks and compare them to the LLM's answer.  If the chunks clearly contain the correct answer and the LLM ignores them, you have isolated Step 6 as the culprit.

6.  Metadata filters at step 4 operate *after* ANN search, not before.  Why is pre-filtering expensive, and what architectural pattern (called "filtered ANN") is used by databases like Qdrant to make it efficient?

   *Hint:* Pre-filtering means scanning the entire metadata table before doing any vector math.  Qdrant's filtered ANN uses a different strategy: its filterable HNSW index adds extra graph links for indexed payload (metadata) values, so the graph stays connected under a filter and the filter can be applied during graph traversal rather than after it.

---

## The Ecosystem and Failure Modes

In this part, you will compare six production vector databases by architecture and operational profile, and study the four most common retrieval failure signatures (semantic mismatch, hallucination, stale index, and "lost in the middle") so you can diagnose them from their symptoms.

### Choosing a Vector Database

The market has converged on a handful of architectures, each with a distinct operational profile.  Choosing the wrong one is like choosing a cargo ship when you need a speedboat; it works, but it is painfully slow to get started.

| Database | Architecture | Hosted? | Strengths | Best For | Installation |
|---|---|---|---|---|---|
| Chroma | Embedded (in-process) or client-server | Self-host or embedded | Minimal setup, Pythonic API, zero infrastructure overhead | Prototyping, local development, courses; you can be running in 5 minutes | `pip install chromadb` |
| Qdrant | Rust core, client-server | Self-host or Qdrant Cloud | Rich payload filters, very fast queries, production-grade reliability | Production RAG systems where metadata filters are complex and performance matters | `pip install qdrant-client` then `docker run -p 6333:6333 qdrant/qdrant` |
| Weaviate | Go, distributed | Self-host or Weaviate Cloud | GraphQL API, native hybrid search, multimodal support | Hybrid (dense + sparse) search, enterprise deployments with complex schemas | `pip install weaviate-client` |
| pgvector | Postgres extension | Wherever Postgres runs | SQL and vector queries in a single database, familiar tooling for backend teams | Teams already running Postgres who want to add vector search without a new database | `CREATE EXTENSION vector;` in Postgres |
| Pinecone | Managed SaaS, serverless | Cloud only (no self-hosting) | Zero infrastructure management, automatic scaling | Startups that need managed infrastructure and want to avoid DevOps overhead | `pip install pinecone` (API key required) |
| Milvus | Distributed, C++ + Python | Self-host or Zilliz Cloud | Billion-scale capacity, multi-tenancy, GPU acceleration | Very large corpora (100M+ documents), enterprise deployments at scale | `pip install pymilvus` then Docker Compose setup |

**Hybrid search** combines dense (embedding) retrieval with sparse (BM25/keyword) retrieval.  Dense search finds semantically related text even when the exact words differ; sparse search finds documents that contain the literal query terms, which dense search can miss for rare names, part numbers, or acronyms.  Systems like Weaviate and Qdrant run both in parallel and merge the ranked lists with a fusion algorithm (Reciprocal Rank Fusion is common).

### Failure Mode Analysis

Vector search fails in predictable ways.  Knowing the failure signature helps you diagnose quickly instead of chasing the wrong culprit.

| Failure | Cause | How to Detect | Fix |
|---|---|---|---|
| Semantic mismatch: the retrieved documents are topically wrong | Query and document use different vocabulary for the same concept (e.g., query says "layoffs," documents say "workforce reductions"); the embedding model treats them as distant because they rarely co-occur in training text | Recall@k falls below 0.6 on a labeled evaluation set; a human reviewer looks at the top-5 retrieved chunks and they are clearly off-topic | Add hybrid search to catch keyword matches; expand the query with synonyms before embedding; or switch to a domain-specific embedding model |
| Hallucination about retrieved content: the LLM contradicts its own retrieved text | The LLM ignores the retrieved chunks and draws on parametric memory instead, especially when the retrieved content conflicts with what it learned during training | The LLM's answer contradicts text that is clearly present in the retrieved chunks; a citation check fails | Strengthen the grounding instruction in the system prompt ("Answer only using the provided documents"); lower temperature to 0; use a model with stronger instruction-following |
| Stale index: correct answer exists in the source but is never retrieved | Documents updated or added after the index was last built are invisible to retrieval; the index is a snapshot, not a live view | The correct answer exists in the source database but is never returned even with broad queries | Build an incremental indexing pipeline that detects changes (file modification time, hash comparison, or a change data capture stream from the database) and re-embeds only changed documents |
| Lost in the middle: the correct chunk is retrieved but the LLM ignores it | The relevant chunk is retrieved and placed in the middle of a long context window; Liu et al., "Lost in the Middle: How Language Models Use Long Contexts" (TACL 2024; arXiv 2307.03172), found that LLMs use information at the beginning and end of their context most reliably | Faithfulness score drops as $k$ increases past 5; manual inspection shows the correct chunk is present in the context but the LLM's answer ignores it | Apply a reranker (e.g., `pip install rerankers`) to place the highest-scoring chunk first in the context; reduce $k$ to 3-5; summarize the context before generation |

You are choosing between cosine similarity and L2 distance for a text retrieval system.  Your embedding model outputs unit-normalized vectors.  Which statement is correct?

[( )] L2 distance should be preferred because it accounts for vector magnitude; magnitude carries additional signal about document importance that cosine similarity discards
[(X)] Cosine similarity and L2 distance produce identical rankings when vectors are unit-normalized, so either works; cosine is typically the default for text
[( )] L2 distance is always faster to compute than cosine similarity because it avoids the normalization step in the cosine formula
[( )] Cosine similarity cannot be used with approximate nearest-neighbor indexes because ANN algorithms like HNSW require a Euclidean distance metric

---

# Extension: RAG Records With Pydantic: Valid Is Not Faithful (self-paced)

## What Was Retrieved, and What Was Answered

This activity's pipeline retrieves chunks and asks the model to answer only from them, citing what it used.  Two Pydantic records (run `pip install pydantic` once) make that contract checkable: one for each retrieved chunk, and one for the answer, which must either cite something or say it abstained.  A bag-of-words count stands in for the embedding so the cell runs anywhere.

## Code Cell: Retrieval, Answer, Citation Check

```python
# P9: the RAG deck's pipeline with a toy embedding, and Pydantic records for what was
# retrieved and what the model answered.
import math
import re
import traceback
from pydantic import BaseModel, Field, ValidationError, model_validator

DOCS = [   # the RAG deck's five campus documents
    "Parking: First-year resident students may not bring vehicles to campus without a hardship waiver.",
    "Library: The Myrin Library is open 8am to midnight Monday through Thursday during the semester.",
    "Dining: Wismer Center serves continuous dining from 7am to 8pm on weekdays.",
    "Advising: Each student is assigned a faculty advisor; registration requires advisor approval.",
    "Athletics: The Floy Lewis Bakes Center is open to all students with a valid ID.",
]
STOP = {"a", "an", "the", "to", "on", "of", "is", "can", "may", "with", "and", "from", "all", "keep", "bring", "what", "does", "time"}
SYN = {"car": "vehicles", "cars": "vehicles"}   # the kind of thing a real embedding learns

def toy_embed(text):
    """Bag of words: a stand-in for a real embedding.  Same text in, same vector out."""
    words = [SYN.get(w, w) for w in re.findall(r"[a-z0-9-]+", text.lower()) if w not in STOP]
    v = {}
    for w in words:
        v[w] = v.get(w, 0) + 1
    return v

def cosine(u, v):
    dot = sum(u[w] * v.get(w, 0) for w in u)
    nu = math.sqrt(sum(x * x for x in u.values()))
    nv = math.sqrt(sum(x * x for x in v.values()))
    return dot / (nu * nv) if nu and nv else 0.0

class RetrievedChunk(BaseModel):
    id: str
    score: float = Field(ge=0.0, le=1.0)
    text: str

class RAGAnswer(BaseModel):
    answer: str
    citations: list[str]        # chunk ids, such as ["doc0"]
    abstained: bool

    @model_validator(mode="after")
    def abstain_or_cite(self):
        if not self.abstained and not self.citations:
            raise ValueError("an answer that does not abstain must cite at least one chunk")
        return self

# --- Indexing phase (once) ---
INDEX = [(f"doc{i}", toy_embed(d), d) for i, d in enumerate(DOCS)]

# --- Query phase (per question) ---
def retrieve(question, k=2):
    q = toy_embed(question)
    ranked = sorted(INDEX, key=lambda row: -cosine(q, row[1]))[:k]
    return [RetrievedChunk(id=i, score=round(cosine(q, v), 3), text=t) for i, v, t in ranked]

def check_citations(ans, hits):
    """The model may cite only chunks it was actually given."""
    given = {h.id for h in hits}
    bad = [c for c in ans.citations if c not in given]
    return "citations OK" if not bad else f"UNFAITHFUL: cited {bad}, was given {sorted(given)}"

# Three replies a model might give, written by hand so the checks are visible.
for question, model_reply in [
    ("Can a first-year student keep a car on campus?",
     '{"answer": "No, not without a hardship waiver [doc0].", "citations": ["doc0"], "abstained": false}'),
    ("What time does the bookstore close?",
     '{"answer": "not in my documents", "citations": [], "abstained": true}'),
    ("What time does the bookstore close?",
     '{"answer": "The bookstore closes at 5pm.", "citations": ["doc3"], "abstained": false}'),
]:
    hits = retrieve(question)
    print("Q:", question)
    for h in hits:
        print(f"   {h.id}  {h.score:.3f}  {h.text[:60]}")
    try:
        ans = RAGAnswer.model_validate_json(model_reply)
        print("   ->", ans.answer, "|", check_citations(ans, hits))
    except ValidationError as e:
        print(f"[pydantic_tut:p9] {e.errors()[0]['msg']}")
        traceback.print_exc()
```

You should see three questions, each with its two retrieved chunks and a verdict:

```text
Q: Can a first-year student keep a car on campus?
   doc0  0.474  Parking: First-year resident students may not bring vehicles
   doc3  0.144  Advising: Each student is assigned a faculty advisor; regist
   -> No, not without a hardship waiver [doc0]. | citations OK
Q: What time does the bookstore close?
   doc0  0.000  Parking: First-year resident students may not bring vehicles
   doc1  0.000  Library: The Myrin Library is open 8am to midnight Monday th
   -> not in my documents | citations OK
Q: What time does the bookstore close?
   doc0  0.000  Parking: First-year resident students may not bring vehicles
   doc1  0.000  Library: The Myrin Library is open 8am to midnight Monday th
   -> The bookstore closes at 5pm. | UNFAITHFUL: cited ['doc3'], was given ['doc0', 'doc1']
```

The third reply passes validation: it is well-formed and it cites a chunk.  It is still unfaithful, because it cites `doc3`, which the retriever never gave it.  The citation check catches it because it compares the answer with the retrieval, which is something a schema alone cannot do.  Notice also the bookstore scores of 0.000: retrieval returns `k` chunks even when none of them is relevant.

### Questions to Work Through

7.  The car question matches `doc0` only because of the one synonym entry, `car` to `vehicles`.  Remove it and predict the scores.  What does a real embedding do that this stand-in cannot?

8.  Add a rule to `RAGAnswer` or to `retrieve` that would have made the bookstore question abstain on its own.  Which one is the right place for it, and why?

    *Hint:* One of the two knows the scores.

---

# Extension: Fine-Tuning, RAG, and Prompting (self-paced)

Optional, and not assumed by anything above.  You now know how to make retrieval work well.  The next question your project will force on you is whether retrieval was the right tool at all, or whether the job wanted a better prompt or a fine-tuned model.  This section gives you the decision framework and the cost model behind it.

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| Prompting | Giving the AI model written instructions, examples, or context within a single request; no code changes, no training, just better text. | Writing a system prompt that says "You are a helpful HR assistant. Always cite the policy section number." |
| RAG (Retrieval-Augmented Generation) | Connecting the AI to an external knowledge source (like a document database) so it can look up relevant information before answering; the model's weights never change. | Before answering "What is our PTO policy?", the system fetches the relevant section of the employee handbook and includes it in the prompt. |
| Fine-Tuning | Continuing the model's training on your own data so the model's weights change; it behaves differently on every future call, even without special prompts.  With LoRA, the change lives in a separate adapter file and takes effect only while that adapter is loaded or merged into the weights. | Training `llama3.1:8b` on 800 examples of correctly formatted legal contract summaries so it always produces that format. |
| LoRA (Low-Rank Adaptation) | A parameter-efficient fine-tuning method that trains only tiny "adapter" matrices (about 0.1% of the total parameters) instead of updating the entire model, cutting GPU cost by orders of magnitude. | Fine-tuning a 7B model with LoRA requires a single A100 GPU for a few hours instead of a multi-GPU cluster for days. |
| QLoRA | LoRA combined with 4-bit quantization of the frozen base model weights, while the small adapter still trains in 16-bit precision; enables fine-tuning 7B models on a single consumer GPU with 24 GB of VRAM. | Students at Ursinus can run QLoRA fine-tuning on a rented Lambda Labs A100 instance for roughly $3-5. |
| Context Window | The maximum amount of text (measured in tokens, where 1 token ≈ 0.75 words) that a model can read in a single request; determines whether "just paste the whole document in" is even possible. | GPT-4o has a 128K token context window, about 96,000 words. A 500-page policy manual (~200,000 words) still exceeds it. |

---

## The Ladder: Prompting, RAG, and Fine-Tuning

In this part, you will learn the three basic ways to specialize a language model (prompting, RAG, and fine-tuning) and build a diagnostic for choosing among them.  Knowing which lever to reach for first will save your team weeks of unnecessary work.

### Three Ways to Specialize a Model

This is the "hire an expert or give your generalist a textbook" decision, and as in real life, hiring a full specialist is expensive, slow, and permanent.  Often the right answer is to give your generalist a great textbook (RAG), or better instructions (prompting), and bring in the specialist only when those cannot work.

The three approaches differ in *where the specialization lives*: in the prompt at inference time, in retrieved text at inference time, or in the model weights permanently.

**Prompting** gives the model instructions, examples, and context within a single call.  Zero-shot prompting provides instructions only; few-shot adds 2-10 worked examples; chain-of-thought prompts the model to reason step by step before answering.  Prompting is free, instant, and reversible, but it is bounded by the context window and by what the base model already knows.  A model that has never seen clinical trial reports cannot be prompted into reliable clinical summarization.

**RAG** injects retrieved information at inference time.  The model receives the same prompt, but now the prompt includes relevant documents fetched from an external index.  The model's weights never change.  RAG excels when knowledge is dynamic (daily news, live databases), external (proprietary documents the base model never saw), or too large for any context window.  Its costs are operational: embedding, indexing, retrieval latency, and the complexity of the pipeline.

**Fine-tuning** adjusts the model's weights on a task-specific dataset.  The change is permanent: a fine-tuned model behaves differently on every subsequent call, without any special prompt.  Fine-tuning can teach style, format, vocabulary, and domain behavior that prompting cannot reliably achieve.  It is also the most expensive and least reversible option.  **PEFT (Parameter-Efficient Fine-Tuning)** methods such as LoRA and QLoRA cut the cost by freezing most weights and training only small adapter matrices; more on this below.

The practical rule: **start at the top of the ladder**.  Reach for fine-tuning only after you have tried prompting and RAG and found them insufficient.

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

   *Hint:* Pay special attention to the "Is the knowledge dynamic?" row.  What does "updated every two weeks" mean for an approach that requires retraining (days of work) versus an approach that requires re-indexing (minutes of work)?

2.  A legal firm wants every contract summary the model produces to follow a precise seven-section structure with mandatory fields.  They have 2,000 existing human-written summaries in that format.  Walk through the decision table for this case.  Does the answer change if they only have 50 examples?  Why?

   *Hint:* Fine-tuning for format typically requires at least a few hundred examples to be reliable.  With 50 examples, few-shot prompting (including 3-5 examples directly in the prompt) may outperform a poorly-fitted fine-tuned model.

3.  "The model already knows how to write code, so we just need to prompt it."  A team makes this argument to avoid fine-tuning their coding assistant.  Describe a concrete scenario where this reasoning fails, where the gap between base model behavior and desired behavior is too large for prompting to close.

   *Hint:* Think about a company-specific internal library with custom APIs that the base model has never seen (because it is proprietary).  No amount of prompting teaches the model what `acme_corp.billing.create_invoice(customer_id, line_items)` does.

---

## Cost and the LoRA Shortcut

In this part, you will compare the true costs of prompting, RAG, and fine-tuning, and learn how LoRA cuts the GPU memory and compute needed for fine-tuning far enough that small teams and individuals can afford it.

### The Cost Reality

The order-of-magnitude cost differences between approaches are often underappreciated.  These figures are rough but directionally correct as of 2025.  Think of it like housing: you can rent a furnished apartment immediately (prompting), move into a place and add your own furniture (RAG), or custom-build from scratch (fine-tuning); each has very different upfront and ongoing costs.

| Approach | Typical Cost per Query | One-Time Setup Cost | Infrastructure Needed | Data Requirement |
|---|---|---|---|---|
| Prompting (API call to GPT-4o or Claude) | $0.003-$0.05 per 1,000-token call depending on model | None beyond prompt engineering time | None: uses a managed API | None: just write better instructions |
| RAG (API + Chroma/Qdrant vector DB) | $0.001-$0.02 per query (embedding + retrieval + smaller LLM call) | Hours to days of pipeline engineering | Vector DB (free locally, ~$50/mo cloud for small scale), embedding service | Source documents only; no labeled pairs needed |
| Fine-tuning (small model, LoRA on `llama3.1:8b`) | $0.0001-$0.001 per call after training (self-hosted inference) | $10-$200 per training run on a rented A100 GPU | GPU for training (A100/H100 rented on Lambda Labs), storage for weights | 200-2,000 labeled input-output pairs |
| Fine-tuning (large model, full weight update) | $0.0001-$0.001 per call after training (self-hosted inference) | $1,000-$50,000 per training run on multi-GPU cluster | Multi-GPU cluster, distributed training framework (DeepSpeed, FSDP) | Thousands to millions of labeled pairs |
| Pre-training from scratch | Fractions of a cent per call after training | $1,000,000+ for a competitive model | Massive GPU cluster, months of compute | Billions of tokens of curated text |

The "low cost per call after training" for fine-tuning is deceptive: the inference cost is low, but the up-front training cost is paid once per model version.  If the domain or data changes, you pay that cost again.

### Same Task, Three Approaches

Consider a concrete deployment: **an HR policy assistant that answers questions about a company's internal policy document**.  This is the kind of task where the choice of approach has measurable consequences.

| Dimension | Prompting: Paste Full Doc in Context | RAG: Chunk, Embed, Retrieve | Fine-Tuning: Train on Q&A Pairs |
|---|---|---|---|
| Implementation effort | Include entire policy in the system prompt; takes minutes to set up | Index policy chunks in a vector DB; retrieve on each query; takes hours to set up (`pip install chromadb`, embed chunks, build query pipeline) | Generate Q&A pairs from the doc, fine-tune a base model like `llama3.1:8b` with LoRA; takes days |
| How it handles policy updates | Immediately: just update the prompt text with the new policy content | With re-indexing, which takes minutes to hours depending on document size | Must retrain, which takes hours to days and costs GPU compute |
| Cost per user query | Higher token cost because the entire policy is in every prompt (e.g., a 50-page doc = ~25,000 tokens × $0.005/1K = $0.125 per call) | Moderate: retrieval + smaller context (typically 1,000-3,000 tokens per call) | Very low per call after training, but training itself costs $20-$200 upfront |
| Can handle 500-page policy? | No: a 500-page document exceeds even 128K-token context windows | Yes: only the relevant 3-5 chunks are retrieved per query | Yes, but generating Q&A pairs for 500 pages and training costs significant time and money |
| Provides citations? | Possible with careful prompting ("Always cite the section number") but not guaranteed | Natural: the retrieved chunk itself is the citation and can be shown to the user | Generally not: knowledge is embedded opaquely in weights, so the model cannot point to its source |
| Output style consistency | Moderate: varies with how the user phrases their question | Moderate: same retrieval quality, but LLM generation still varies | High: style, format, and phrasing learned during training appear consistently in every response |

> **Common Misconception:** Many teams jump straight to fine-tuning because it sounds like the most "AI-native" solution.  For a task like the HR policy assistant, **RAG almost always outperforms fine-tuning**, because policy documents change frequently (defeating fine-tuning's static knowledge) and citations matter (defeating fine-tuning's opaque knowledge).  Fine-tuning wins for style and format, not for factual recall of changing documents.

#### Questions to Work Through

4.  The HR policy document is 50 pages, about 25,000 tokens.  That fits in many current context windows, but resending it with every query is costly and slow, and a clause buried in the middle of a long context is easy for the model to miss, so set prompting aside.  Between RAG and fine-tuning, which approach provides better freshness when a policy changes, and why does the answer matter operationally for an HR department?

   *Hint:* When a policy changes, which approach requires re-indexing (minutes) versus retraining (hours or days)?  Think about the HR team's perspective: if the maternity leave policy changes tomorrow, how quickly can each approach reflect that change?

5.  A product manager argues: "Let's fine-tune the model on HR Q&A pairs so we don't need the vector database."  What hidden assumption does this argument make about the stability of the policy, and what happens at the next policy revision?

   *Hint:* The argument assumes the Q&A pairs will remain accurate indefinitely.  What happens when a policy changes and the fine-tuned model confidently gives the old (now wrong) answer?

6.  Describe a hybrid approach that combines RAG *and* fine-tuning.  What does each layer contribute, and what would justify the additional complexity and cost?

   *Hint:* Think of RAG as responsible for "what information to use" and fine-tuning as responsible for "how to format and present the answer."  A model fine-tuned on 2,000 HR Q&A pairs will always respond in the right format and tone; RAG ensures the specific policy content it uses is always current.

---

### LoRA: Fine-Tuning Without Full Weight Updates

Full fine-tuning updates every parameter in the model: for a 7B-parameter model, that is 7 billion floating-point numbers to store gradients for and update.  LoRA (Low-Rank Adaptation) sidesteps this by observing that the *update* to each weight matrix during fine-tuning tends to be low-rank: it lives in a small subspace of the full parameter space.

LoRA freezes all original weights and adds two small matrices per layer.  For a weight matrix $W \in \mathbb{R}^{d \times k}$, LoRA trains $A \in \mathbb{R}^{d \times r}$ and $B \in \mathbb{R}^{r \times k}$ where $r \ll d, k$ (typically $r = 4$, $8$, or $16$).  During inference, the layer computes $Wx + \frac{\alpha}{r}ABx$, the original output plus a learned correction scaled by a constant $\alpha$ that you choose (often $2r$).  Installation: `pip install peft transformers` (the PEFT library from Hugging Face implements LoRA).

### LoRA Illustrated

The diagram below shows how LoRA adds two tiny matrices (A and B) alongside the frozen original weight matrix W.  Look for how small r is compared to d and k; that small rank is what makes LoRA's memory savings so large.

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

At rank $r = 8$ for a 7B model, LoRA trains roughly 4-8 million parameters instead of 7 billion, a 99.9% reduction in trainable parameters.  The exact share depends on the model and on which matrices get adapters: on a 360M-parameter model with adapters on all four attention projections, rank 8 trains 1.6 million parameters, about 0.45%.  **QLoRA** combines LoRA with 4-bit quantization of the frozen base weights, enabling fine-tuning of 7B models on a single consumer GPU with 24 GB of VRAM.  Only the frozen base is stored in 4 bits.  The adapter matrices and their gradients stay in 16-bit precision, so QLoRA saves memory on the part that does not train.  QLoRA's 4-bit loading (the `bitsandbytes` library) needs an NVIDIA GPU; plain LoRA on a small model runs on a CPU.

**Real cost example:** Fine-tuning `llama3.1:8b` with QLoRA on 800 JSON-formatting examples using a rented Lambda Labs A100 instance costs approximately $1.60 (0.8 hours × $2/hour).  The resulting adapter file (the A and B matrices) is roughly 40 MB, compared to the 16 GB base model.

A team wants to fine-tune a 7B model to always respond in a structured JSON format for a data extraction task.  They have 800 labeled examples and a single A100 GPU (40 GB).  Which approach is most appropriate?

[( )] Full fine-tuning (update all 7B parameters), because format changes require updating every layer of the model to take effect consistently
[(X)] LoRA or QLoRA (freeze the base weights, train small adapter matrices), sufficient for format adaptation at a fraction of the compute cost
[( )] RAG; retrieve the JSON schema from a vector database at each call so the model always sees the expected format
[( )] Pre-training from scratch on JSON-formatted text corpora, since the base model has no concept of structured output

### An Adapter Only Matters When It Is Loaded

Training produces an **adapter**: a folder holding the A and B matrices and a small config file, a few megabytes, with no copy of the base model inside it.  It only works with the exact base model it was trained on.  At inference you do one of two things:

- **Load it** on top of the base model (`PeftModel.from_pretrained(base, adapter_dir)`).  The base weights in memory stay unchanged, and you can switch the adapter off to compare (`with model.disable_adapter():`).
- **Merge it** (`model.merge_and_unload()`), which adds $\frac{\alpha}{r}AB$ into $W$ once and produces an ordinary full-size model with no adapter at all.

Neither result runs in Ollama directly.  Ollama runs GGUF files, so a fine-tuned model has to be converted, or imported as an adapter for a base architecture Ollama supports.  The *Offline RAG and LoRA* tutorial covers that export.  Until you have done it, treat a PEFT adapter as something only Transformers can load.

**Neither RAG nor LoRA makes a model truthful.**  RAG changes what the model reads, and the model can still misread a correct passage.  LoRA changes how the model writes, and it can learn a confident format faster than it learns facts.  A fine-tuned citation format attached to a wrong answer looks more trustworthy, not less.

### Adapter Off, Adapter On

Once you have trained the adapter in *Offline RAG and LoRA, End to End*, this comparison takes about five minutes.

1. Look at the adapter folder: `adapter_config.json` and `adapter_model.safetensors`, about 6 MB, beside a base model of about 700 MB.
2. Run `python infer_lora.py` from that tutorial.  The same base model in memory answers one question twice, with the adapter bypassed and with it active.
3. Ask yourself: the weights in memory did not change between the two answers, so what did?  Then: the adapter was trained on the Saturday hours, so is the right answer evidence that it *knows* the handbook, or that it memorized one line?
4. Read the four-way comparison table from that tutorial's Section F.  It shows that LoRA learned the format, while only retrieval knew the changed fact.

The full reproduction is in *Offline RAG and LoRA, End to End* (https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OfflineRAGFineTuning), Sections D to F: training on a CPU in under two minutes, reloading in a fresh process, merging, and a held-out comparison of a base model, RAG, LoRA, and both.  Nothing in it is graded.

---

> Now that you have the decision logic and the cost structure, the exercises below apply them to real products and to concrete break-even points.

## Synthesis and Practice

In this part, you will apply the decision framework and cost model to AI products you already use, calculate when self-hosted fine-tuning beats API calls on price, and practice constructing training datasets for a fine-tuning pipeline.

### Exercises

1.  *Approach audit.*  Identify three AI products you use regularly (a search assistant, a coding tool, a customer service bot).  For each, hypothesize whether the specialization comes from prompting, RAG, fine-tuning, or some combination.  List the evidence that informs your hypothesis.

   *What to do:* For each product, answer: Does it know about recent events?  (RAG or prompting.)  Does it refuse certain topics?  (Prompting/fine-tuning.)  Does it always output in a specific format?  (Fine-tuning.)  Does it cite sources?  (RAG.)

   *Starter hint:* GitHub Copilot likely uses a combination: a code-specialized base model (fine-tuning on code) plus in-context retrieval of your open files (prompting/RAG).  What evidence do you see for this in its behavior?

   *You've succeeded when:* You have a table with three products, a hypothesis for each, and at least two observable behaviors that support each hypothesis.

2.  *Cost model.*  You process 10,000 user queries per day.  Compare the monthly cost of: (a) GPT-4o via API at $5/1M input tokens with a 2,000-token average prompt versus (b) a locally-hosted fine-tuned `llama3.1:8b` model on a rented A100 at $2/hour.

   *What to do:* Calculate (a) monthly API cost: 10,000 queries/day × 30 days × 2,000 tokens × ($5 / 1,000,000).  Calculate (b) monthly GPU cost: 720 hours/month × $2/hour.  Add the one-time training cost.  Find the break-even query volume.

   *Starter hint:* At 10,000 queries/day, GPT-4o API cost ≈ $3,000/month.  A dedicated A100 ≈ $1,440/month.  But what happens at 500 queries/day?  The A100 is always on; the API charges per query.  Build a simple Python calculation: `api_cost = queries_per_day * 30 * avg_tokens * price_per_token`.

   *You've succeeded when:* You have a break-even query volume (queries/day at which the two approaches cost the same) and a recommendation for a startup with 500 queries/day versus 50,000 queries/day.

3.  *LoRA parameter count.*  A transformer layer has a query projection matrix $W_Q \in \mathbb{R}^{4096 \times 4096}$.  If LoRA is applied with rank $r = 16$, how many parameters does LoRA add to this single matrix (count $A$ and $B$ together)?  What fraction of the original matrix does this represent?

   *What to do:* $A$ has shape $4096 \times 16$ and $B$ has shape $16 \times 4096$.  Count total LoRA parameters.  Original $W_Q$ has $4096 \times 4096 = 16{,}777{,}216$ parameters.

   *Starter hint:* $|A| = 4096 \times 16 = 65{,}536$.  $|B| = 16 \times 4096 = 65{,}536$.  Total LoRA = $131{,}072$.  Fraction = $131{,}072 / 16{,}777{,}216 \approx 0.78\%$.  A real 7B model has ~32 such layers, each with multiple projection matrices (Q, K, V, O).

   *You've succeeded when:* You have the exact parameter counts and fractions, and you can explain why this means LoRA training needs ~100x less GPU memory than full fine-tuning.

4.  *Dataset construction.*  You are fine-tuning a model to extract structured fields (name, date, amount, counterparty) from procurement contracts.  Design a data collection strategy for 500 training examples.

   *What to do:* Identify (a) the source of raw documents, (b) how you generate ground-truth labels, and (c) what quality checks you apply before training.

   *Starter hint:* Format each training example as a JSON pair: `{"input": "<contract text>", "output": {"name": "Acme Corp", "date": "2024-03-15", "amount": 45000.00, "counterparty": "Ursinus College"}}`.  Quality checks: verify all four fields are present in every example; confirm dates parse correctly; have a human review 10% of examples for accuracy.

   *You've succeeded when:* You have a written data collection plan with source, labeling method, quality checks, and a 5-example sample dataset in the correct format.

---

### Reflection Prompt

*Personal:* Think of a skill you had to learn from a book and one you learned by doing.  How does that map to the RAG (look it up every time) versus fine-tuning (internalize it permanently) distinction?  When is "always looking it up" better than "memorizing it"?

*Technical:* Fine-tuning bakes knowledge permanently into weights, making the model's reasoning opaque.  RAG keeps knowledge external and attributable, but adds a pipeline that can fail in its own ways.  As AI systems are deployed in high-stakes domains (medicine, law, finance), which property matters more (opaque internalized knowledge or transparent retrieved knowledge), and who should get to decide that for a given deployment?

*Societal:* LoRA makes fine-tuning accessible to individuals and small organizations who previously could not afford it.  A chemistry student can now fine-tune an open-weight model on synthesis procedures; a political campaign can fine-tune a model on persuasive messaging.  What new capabilities does democratized fine-tuning enable that are beneficial, and what risks does it introduce that did not exist when fine-tuning required millions of dollars?

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

Data labeling, not compute, is often the bottleneck.  A radiologist who can label 20 chest X-rays per day costs ~$300,000 per year and produces roughly 5,000 labeled examples annually.  A single GPU running a generative model can produce thousands of synthetic medical descriptions per hour.  That this is useful is obvious; the open question is whether synthetic data is a complete substitute for real data, a dangerous shortcut, or something in between.  As you will see in this section, the answer depends entirely on what you are generating, how carefully you filter it, and whether you have any real data to validate against.

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
| **Adversarial robustness** | Edge-case prompts and scenarios the model would rarely encounter in normal operation | Better resistance to unusual inputs, jailbreak attempts, and distribution shift | Synthetic adversarial examples may not cover the specific adversarial strategies real attackers use | Red-teaming augmentation in model safety pipelines |
| **Privacy preservation** | Statistically similar fake records that replace real patient, user, or financial records | Share sensitive datasets safely in research collaborations without exposing individual records | Residual privacy leakage if the synthetic distribution closely mirrors specific real records | Synthetic patient record generation for medical AI research |
| **Simulation environments** | Agent training scenarios such as customer service dialogues, code review sessions, or tool-use chains | Scale agent training to millions of scenarios without real user interactions or risks | Sim-to-real gap: the agent learns behaviors that work in clean simulation but fail on the messy variation in real deployments | A scripted user model playing customers so a support agent can practice thousands of conversations |

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

Stanford's **Alpaca** model (2023) applied this pipeline: it used GPT-3.5 to generate 52,000 instruction-response pairs from 175 human-written seeds, at a cost of approximately $500 in API fees.  In the team's own small blind comparison, the resulting 7B model performed about as well as the model that generated its data, a demonstration of how far a cheap synthetic dataset can go.

#### Evol-Instruct (WizardLM, Xu et al., 2023)

Evol-Instruct takes a different approach: rather than generating new instructions from scratch, it **evolves** existing simple instructions into progressively harder ones through iterative rewriting.  Each evolution step applies one of several transformations:

- **Add constraints:** "Write a function that sorts a list" -> "Write a function that sorts a list without using any built-in sorting functions or the sorted() built-in, in O(n log n) time."
- **Deepen complexity:** "Explain photosynthesis" -> "Explain photosynthesis at the biochemical level, addressing specifically whether recent research on quantum coherence in light-harvesting complexes changes the classical explanation."
- **Require multi-step reasoning:** Single-step questions become chains of reasoning with explicit intermediate conclusions required.

The result is a dataset with a natural difficulty gradient, which is particularly valuable for training models to handle challenging queries rather than just easy ones.

#### Quality Filtering Pipeline

The diagram below shows how raw generated pairs flow through a series of filters before being added to the training set.  Read it left-to-right: each arrow is a filter that reduces the quantity of data but improves its quality; the loop at the bottom is where generation and filtering cycle repeatedly.

```
seed_instructions
    -> generate_variants(LLM)
    -> filter_quality(judge_LLM_or_rules)
    -> deduplicate(exact + semantic_similarity)
    -> measure_diversity(embedding_spread)
    -> add_to_dataset
    -> loop
```

**Quality filter criteria (each generated pair must pass all of these):**

- **Length check:** The response is not trivially short (one word) or obviously padded with filler content.
- **Coherence check:** The response addresses the instruction rather than drifting to an unrelated topic.
- **Non-duplication check:** Cosine similarity (a number between -1 and 1 measuring how semantically similar two pieces of text are; for typical text embeddings the observed values are usually positive, and values above 0.9 mean the texts are nearly identical in meaning) to existing dataset items is below a threshold (typically 0.7-0.8) so the dataset remains diverse.
- **Safety check:** The instruction and response do not contain toxic, harmful, or inappropriate content.

> **Common Misconception:** Generating more synthetic data is not the same as generating *better* synthetic data.  A common error is to generate enormous quantities of synthetic instruction data and assume that more is always better.  In practice, quality filters matter more than quantity: Zhou et al.'s LIMA (2023) fine-tuned a 65B LLaMA model on only 1,000 carefully curated examples and reported answers competitive with models tuned on far larger instruction sets.  Running the generation loop for 10 more hours to produce 500,000 examples would not have produced a model 10× better, and might have introduced more mode collapse (repetitive, low-diversity outputs, as distinct from the multi-generation *model collapse* defined above).

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

Synthetic trajectories let agent training scale beyond what human demonstration collection alone can support:

- **Verified code problems:** Generate a programming problem, generate a candidate solution, execute the solution in a sandboxed environment, and use pass/fail against test cases as ground-truth labels.
- **Customer service dialogues:** Generate a synthetic customer persona, a synthetic initial complaint or question, and a range of synthetic agent responses.  Have a judge model rate each response on helpfulness and policy compliance.  This provides training signal without accessing real user data that might contain PII.
- **Tool-use chains:** Generate tasks that require specific sequences of tool calls (look up a weather forecast, then look up a transit schedule, then combine them to recommend departure time), execute those chains in a sandboxed environment, and label complete trajectories by whether the task was accomplished correctly.

#### Synthetic Evaluation Sets: The "LLM Generates Its Own Exam" Pattern

A practical technique for rapidly building evaluation benchmarks for new domains:

1.  Prompt a capable model: "Generate 20 challenging questions about [domain] that require [specific capability].  For each question, also provide the correct answer."
2.  Filter the generated pairs for quality, accuracy, and non-duplication.
3.  Use the resulting pairs as a benchmark to evaluate a fine-tuned model on that domain.

**Critical pitfall: self-evaluation inflation.** A model performs systematically better on questions it generated than on questions generated by humans or by a different model.  The model "knows" the style and framing of its own questions and can answer them more easily.  This inflates apparent capability on the synthetic benchmark compared to real-world performance.  Always validate a synthetic evaluation set against a sample of real human-written questions in the same domain before relying on it for deployment decisions.

#### Questions to Work Through

**Question 7.**  If you fine-tune a model on synthetic data, then use that fine-tuned model to generate more synthetic data for the next training round, and repeat: how do you prevent the model from progressively reinforcing its own errors?  Describe at least one specific structural safeguard you would build into the pipeline.

> *Hint:* The core danger is error amplification: if the fine-tuned model has a systematic error (always recommending the wrong medication dose, always getting a specific logic pattern wrong), it will generate synthetic data that reflects that error, and the next model will learn the error even more strongly.  Structural safeguards include: (1) **Real data anchoring**: always include a fixed proportion of human-verified real data in each training round, so the model cannot drift arbitrarily far from reality; (2) **Verification gating**: for domains where outputs can be automatically checked (code that runs, math answers that can be verified, logical proofs that can be checked), only include synthetic examples in the next training round if the output passes an automatic correctness check; (3) **Diversity filtering**: use embedding-based deduplication at each round to prevent the pipeline from collapsing to a narrow mode.

---

**Question 8.**  What is the difference between **synthetic** data and **augmented** data?  Give a concrete example of each in the context of a text-classification task for classifying customer support tickets by urgency.  Does the distinction matter for how you evaluate the resulting model?

> *Hint:* **Augmented data** is derived from real data through transformations that preserve the label: taking a real support ticket classified as "urgent" and paraphrasing it, translating it, or adding typos.  The result is a new example that is artificial, but it is grounded in a real human-written ticket with a verified label.  **Synthetic data** is generated from scratch without reference to any specific real example: prompting a model to "write an example urgent customer support ticket about a missed delivery."  The distinction matters for evaluation because: if you evaluate on augmented data, you are testing whether the model generalizes to variations of real examples; if you evaluate on synthetic data, you are testing whether the model handles the generator's idea of what an urgent ticket looks like, which may not match real urgent tickets.

---

**Question 9.**  Design a quality filter for synthetic instruction data.  Specify exactly three criteria that every generated (instruction, response) pair must satisfy before it is added to the training set.  For each criterion, explain how you would test it automatically and what failure rate you would tolerate before revising the generation pipeline.

> *Hint:* Criterion 1: **Relevance**, the response must address the instruction rather than drift to an unrelated topic.  Test automatically by checking whether the top 3 most important noun phrases from the instruction appear in the response (simple heuristic) or by embedding both instruction and response and checking cosine similarity (more reliable).  Tolerate at most 5% failure rate before revisiting the generation prompt.  Criterion 2: **Minimum length**, the response must be at least 50 words and at most 300 words for the task types in your dataset.  Test by word count.  Tolerate at most 10% failure rate (responses that are too short are often low-quality; responses that are too long may be padded).  Criterion 3: **Non-toxicity**, the instruction and response must not contain harmful, discriminatory, or violating content.  Test using a toxicity classifier.  Tolerate 0% failure rate; any toxic generation indicates a problem with the generation prompt that must be fixed immediately.

---

### Exercises

**Exercise 1.**

*What to do:* Using a local model or API access, generate 20 synthetic instruction-tuning examples for a domain of your choice (options: cooking, Python debugging, academic writing, local Ursinus College history, or anything else that interests you).  Apply at least 2 quality filters from the Quality Filtering Pipeline above.

*Starter hint:* Use this generation prompt structure: "You are generating instruction-tuning data for a language model assistant.  Generate 5 (instruction, response) pairs for the domain of [your domain].  Each instruction should be a specific, realistic task a user might ask.  Each response should be accurate, helpful, and 3-5 sentences (at least 50 words) long.  Format your output as a JSON array."  Run this prompt 4 times to get 20 candidates.  Then apply your filters: (1) remove any response shorter than 50 words; (2) remove any pair where the response does not mention any key term from the instruction.

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

Write at least 200 words addressing at least two of the three levels above.  
