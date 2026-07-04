---
layout: assignment
permalink: /Assignments/RAGKnowledgeBase
title: "CS357: Foundations of Artificial Intelligence - Lab 2: A RAG Knowledge Base of Your Own"

info:
  coursenum: CS357
  points: 100
  goals:
    - To construct a complete retrieval-augmented generation pipeline over a personal document corpus using Chroma and a local model
    - To make and defend chunking decisions empirically by comparing at least two strategies with recall@k metrics
    - To evaluate retrieval quality with recall at k and grounding quality with a citation audit
    - To implement and demonstrate honest abstention when the corpus does not contain an answer
  rubric:
    - weight: 30
      description: Pipeline Implementation
      preemerging: The pipeline fails to index or query due to major issues, or the program fails to run
      beginning: The pipeline runs but fails on test questions due to one or more minor issues
      progressing: The pipeline indexes and answers correctly with citations, but a component such as abstention or configuration is fragile or incomplete
      proficient: The pipeline indexes, retrieves, answers with cited bracketed source numbers, and abstains with the designated phrase when no chunk is relevant; a screenshot or log shows all three behaviors (answer-with-citation, abstention, and the bare-model hallucination contrast); configuration is externalized and exceptions are handled with located messages and tracebacks
    - weight: 25
      description: Chunking Strategy and Justification
      preemerging: A single arbitrary chunking is used without discussion
      beginning: A chunking choice is stated but not compared against an alternative
      progressing: Two chunking strategies are compared on a small question set with results reported
      proficient: At least two chunking strategies are compared on a defined question set; recall@k is reported for k in {1,3,5} for each strategy in a table; the shipped choice is defended with a specific numeric comparison (e.g., "strategy A achieves recall@3 of 0.80 vs. 0.60 for strategy B on our question set")
    - weight: 25
      description: Evaluation and Citation Audit
      preemerging: No evaluation is provided
      beginning: Informal trials are described without a protocol or metric
      progressing: A question set with recall at k and an answer accuracy measure is evaluated, with limited citation auditing
      proficient: A question set of at least ten questions is evaluated with recall@k and answer accuracy; every citation in a sample of at least ten answers is audited by hand for faithfulness; a faithfulness rate (e.g., "9/10 citations correctly supported the claim") is reported; any failures are shown verbatim and classified using the hallucination taxonomy from class
    - weight: 10
      description: Code Quality and Documentation
      preemerging: Code commenting and structure are absent, or code structure departs significantly from best practice
      beginning: Code commenting and structure is limited in ways that reduce the readability of the program
      progressing: Code documentation is present that re-states the explicit code definitions
      proficient: Every non-trivial function has a docstring; all network, embedding, and database operations are wrapped in exception handlers that print a located message (e.g., [lab2:query_corpus]) followed by a traceback; model name, chunk size, overlap, top-k, and abstention threshold are read from a JSON config file rather than hardcoded
    - weight: 10
      description: Writeup, Reflection, and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup, a pair programming log with at least two timestamped role swaps, a corpus datasheet covering sources, time range, representation gaps, and known limitations, and reflection answers that each cite a specific experimental result from the lab rather than restating the prompt
  readings:
    - rtitle: "RAG Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-rag.md"
    - rtitle: "RAG Quality Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ragquality.md"
    - rtitle: "Chroma Documentation"
      rlink: "https://docs.trychroma.com"

tags:
  - rag
  - embeddings
  - local-ai

---

In this lab, you and your partner will build a question-answering system over a corpus that matters to *you*: your own course notes, a student organization's documents, a hobby wiki you maintain, or a set of public campus documents. The system must answer questions with citations when the corpus supports an answer, and say so honestly when it does not. This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

---

## Before You Start

**Prerequisite concepts** — complete these activities before writing any code:

- [RAG Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-rag.md) — the index/retrieve/generate pipeline
- [RAG Quality Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ragquality.md) — recall@k, faithfulness, and abstention

**Tools to install:**

```bash
# Chroma vector database (pure Python, no server needed for this lab)
pip install chromadb

# Sentence transformers for local embeddings (no API key required)
pip install sentence-transformers

# Requests for Ollama calls (already installed if you did Lab 1)
pip install requests
```

**Health check** — run this after installation. If you see `ok` on each line, you are ready:

```bash
python -c "import chromadb; print('chromadb ok')"
python -c "from sentence_transformers import SentenceTransformer; print('sentence_transformers ok')"
python -c "import requests; r = requests.get('http://localhost:11434/api/tags'); print('ollama ok' if r.ok else 'ollama NOT running')"
```

Expected output:

```
chromadb ok
sentence_transformers ok
ollama ok
```

If `ollama NOT running`, start the server with `ollama serve` in a separate terminal.

**Estimated time budget:**

| Part | Task | Estimated time |
|------|------|----------------|
| Part 1 | Curate and document corpus | 45–60 min |
| Part 2 | Index with intent | 60–90 min |
| Part 3 | Grounded generation | 60–75 min |
| Part 4 | Citation audit | 30–45 min |
| Writeup | Readme, datasheet, reflection | 30–45 min |

---

## Part 1: Curate and Document Your Corpus

Assemble a corpus of at least 15 documents or pages (markdown, text, or extracted PDF text). **You may not use any document containing another person's private information**; if your corpus involves anything sensitive, the local-only nature of this pipeline is your friend, and your writeup must say so explicitly. Write a half-page **datasheet**: sources, time range, who and what is represented, who and what is absent, and known limitations.

### Step-by-step guide

**Step 1: Collect your documents.**

Good corpus ideas:
- Your notes from another class (15+ lecture note files)
- A student club's public meeting minutes
- Wikipedia articles on a hobby topic you know well (so you can verify answers)
- Ursinus College's public website pages, saved as text

Place all files in a folder, e.g., `corpus/`. Each file should be plain text or markdown. If you have PDFs, extract their text first:

```bash
pip install pymupdf
python -c "
import fitz, pathlib
for pdf in pathlib.Path('corpus_pdfs').glob('*.pdf'):
    doc = fitz.open(pdf)
    text = '\n'.join(page.get_text() for page in doc)
    pathlib.Path('corpus/' + pdf.stem + '.txt').write_text(text)
    print(f'Extracted {pdf.name}: {len(text)} chars')
"
```

**Step 2: Verify your corpus size.**

```bash
python -c "
import pathlib
files = list(pathlib.Path('corpus').glob('*.txt')) + list(pathlib.Path('corpus').glob('*.md'))
total_chars = sum(f.stat().st_size for f in files)
print(f'Files: {len(files)} | Total characters: {total_chars:,}')
"
```

Expected output (your numbers will differ):

```
Files: 18 | Total characters: 142,350
```

You need at least 15 files. If you have fewer, add more documents before proceeding.

**Step 3: Write your corpus datasheet (half page in your readme).**

Answer these questions in prose:
- **Sources**: Where did each document come from? What URL or file path?
- **Time range**: When were these documents written or last updated?
- **Who and what is represented**: What topics, people, or events appear?
- **Who and what is absent**: What related topics are NOT covered? Who would find this corpus unhelpful?
- **Known limitations**: Are any documents incomplete, low-quality, or potentially outdated?

### Troubleshooting — Part 1

**PDF extraction produces garbled text (especially from scanned PDFs)**
Scanned PDFs require OCR; `pymupdf` only extracts embedded text. Try `pip install pytesseract` and Tesseract OCR for scanned documents, or choose different source documents.

**Fewer than 15 usable files after extraction**
Wikipedia is a reliable fallback. Use `pip install wikipedia-api` and download 15+ related articles programmatically.

**File encoding errors when reading**
Always open files with `encoding="utf-8", errors="replace"` to handle non-ASCII characters gracefully.

---

> **Checkpoint: Before moving to Part 2, make sure you can answer:**
> 1. How many documents are in your corpus, and what is their total character count?
> 2. Name one topic that your corpus covers well and one topic a user might ask about that your corpus cannot answer. (You will use both in Part 3.)
> 3. What does your corpus datasheet reveal about potential blind spots in the answers your system will give?

---

## Part 2: Index with Intent

Implement indexing with **two chunking strategies** (for example, fixed-size with overlap versus paragraph-structural), with chunk parameters externalized in a JSON configuration file. Build a question set of at least ten questions whose answers you have located by hand (note the source chunk for each). Report **recall@k** for $k \in \{1, 3, 5\}$ under both strategies, and choose your shipped configuration with a quantitative defense.

### Step-by-step guide

**Step 1: Create your configuration file.**

```json
{
  "corpus_dir": "corpus",
  "model": "llama3.2",
  "embed_model": "all-MiniLM-L6-v2",
  "temperature": 0.1,
  "seed": 42,
  "top_k": 3,
  "abstention_phrase": "I don't have enough information in my knowledge base to answer that.",
  "chunking": {
    "strategy": "fixed",
    "chunk_size": 500,
    "overlap": 50
  }
}
```

**Step 2: Implement the two chunking strategies.**

```python
def chunk_fixed(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping fixed-size chunks.
    Returns a list of (chunk_text, start_char) tuples.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append((text[start:end], start))
        start += chunk_size - overlap
    return chunks

def chunk_by_paragraph(text, min_size=100, max_size=1000):
    """
    Split text on blank lines, then merge short paragraphs until min_size is met.
    Returns a list of (chunk_text, paragraph_index) tuples.
    """
    raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    idx = 0
    for para in raw_paragraphs:
        current = (current + "\n\n" + para).strip() if current else para
        if len(current) >= min_size:
            chunks.append((current[:max_size], idx))
            current = current[max_size:]
            idx += 1
    if current:
        chunks.append((current, idx))
    return chunks
```

**Step 3: Build the Chroma index.**

```python
import chromadb
from sentence_transformers import SentenceTransformer
import pathlib
import json

def build_index(config, strategy="fixed"):
    """
    Load all documents from corpus_dir, chunk them, embed them, and store in Chroma.
    Returns (collection, embed_model, chunk_metadata_list).
    """
    embed_model = SentenceTransformer(config["embed_model"])
    client = chromadb.Client()

    collection_name = f"lab2_{strategy}"
    # Delete existing collection if re-running
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
    collection = client.create_collection(collection_name)

    all_chunks = []
    all_ids = []
    all_metadatas = []

    corpus_path = pathlib.Path(config["corpus_dir"])
    doc_files = list(corpus_path.glob("*.txt")) + list(corpus_path.glob("*.md"))

    for doc_file in doc_files:
        text = doc_file.read_text(encoding="utf-8", errors="replace")

        if strategy == "fixed":
            cfg = config["chunking"]
            chunks = chunk_fixed(text, cfg["chunk_size"], cfg["overlap"])
        else:
            chunks = chunk_by_paragraph(text)

        for i, (chunk_text, position) in enumerate(chunks):
            chunk_id = f"{doc_file.stem}_{strategy}_{i}"
            all_chunks.append(chunk_text)
            all_ids.append(chunk_id)
            all_metadatas.append({
                "source": doc_file.name,
                "position": position,
                "strategy": strategy
            })

    # Embed in batches to avoid memory issues
    batch_size = 64
    all_embeddings = []
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i+batch_size]
        embeddings = embed_model.encode(batch).tolist()
        all_embeddings.extend(embeddings)
        print(f"  Embedded {min(i+batch_size, len(all_chunks))}/{len(all_chunks)} chunks")

    collection.add(
        documents=all_chunks,
        embeddings=all_embeddings,
        ids=all_ids,
        metadatas=all_metadatas
    )

    print(f"Indexed {len(all_chunks)} chunks using strategy='{strategy}'")
    return collection, embed_model, list(zip(all_ids, all_chunks, all_metadatas))
```

Expected output:

```
  Embedded 64/312 chunks
  Embedded 128/312 chunks
  ...
  Embedded 312/312 chunks
Indexed 312 chunks using strategy='fixed'
```

**Step 4: Define your ten questions and their ground-truth source chunks.**

Before running any retrieval, locate each answer by hand in your corpus. Record the source file and approximate position. This is your ground truth.

```python
# question_set.py
QUESTIONS = [
    {
        "id": "Q01",
        "question": "What is the main topic covered in lecture 3?",
        "answer_in_source": "lecture03.txt",  # file where the answer lives
        "answer_text_snippet": "gradient descent"  # short string that appears in the answer chunk
    },
    # TODO: Add Q02 through Q10 covering different documents
    # Include at least 2 questions your corpus CANNOT answer (for abstention testing in Part 3)
]
```

**Step 5: Compute recall@k for both strategies.**

```python
def recall_at_k(collection, embed_model, questions, k=3):
    """
    For each question, retrieve top-k chunks and check if the ground-truth
    snippet appears in any of the retrieved chunks.
    Returns recall as a float.
    """
    hits = 0
    for q in questions:
        if q.get("unanswerable"):
            continue  # skip abstention questions for recall measurement
        query_embedding = embed_model.encode([q["question"]]).tolist()
        results = collection.query(query_embeddings=query_embedding, n_results=k)
        retrieved_docs = results["documents"][0]
        found = any(q["answer_text_snippet"].lower() in doc.lower() for doc in retrieved_docs)
        if found:
            hits += 1
    answerable = [q for q in questions if not q.get("unanswerable")]
    return hits / len(answerable) if answerable else 0.0

# Run for both strategies and all three k values
config = json.load(open("config.json"))
for strategy in ["fixed", "paragraph"]:
    print(f"\nStrategy: {strategy}")
    collection, embed_model, _ = build_index(config, strategy=strategy)
    for k in [1, 3, 5]:
        recall = recall_at_k(collection, embed_model, QUESTIONS, k=k)
        print(f"  recall@{k} = {recall:.2f}")
```

Expected output (your numbers will differ):

```
Strategy: fixed
  recall@1 = 0.50
  recall@3 = 0.80
  recall@5 = 0.90

Strategy: paragraph
  recall@1 = 0.60
  recall@3 = 0.70
  recall@5 = 0.80
```

In your readme, present these numbers in a table and defend your choice of strategy with a specific quantitative comparison.

### Troubleshooting — Part 2

**`chromadb` raises `ValueError: Embedding function is required`**
You are passing embeddings manually via `collection.add(embeddings=...)`, which is correct. Make sure you are NOT also passing `embedding_function` when creating the collection — one or the other, not both.

**`recall@1 = 0.0` for every question with fixed chunking**
Your chunk_size may be too small, causing answers to be split across chunks. Try chunk_size=800 or chunk_size=1000. Also verify your `answer_text_snippet` actually appears in the source file (run `grep -n "your snippet" corpus/yourfile.txt`).

**SentenceTransformer download is slow or fails**
The `all-MiniLM-L6-v2` model (~80 MB) downloads from HuggingFace on first run. If your internet is slow, pre-download it: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"` while on a fast connection, and it will be cached for later runs.

---

> **Checkpoint: Before moving to Part 3, make sure you can answer:**
> 1. What is a vector embedding and why is it more useful for semantic search than exact keyword matching?
> 2. How many chunks did your corpus produce under each strategy? Why might one strategy produce more chunks than the other?
> 3. What happens if you query the collection before adding any documents? (Test it and record the error.)

---

## Part 3: Grounded Generation

Implement the query path: embed the question, retrieve top-k, assemble a prompt that instructs the model to answer **only** from the provided context, to cite bracketed source numbers, and to reply with a designated abstention phrase when the context is insufficient. Demonstrate:

- Five answered questions with correct citations.
- Two honest abstentions on questions your corpus cannot answer.
- One before/after comparison showing the bare model hallucinating where your RAG system either answers correctly or abstains.

### Step-by-step guide

**Step 1: Implement the query-and-generate function.**

```python
import requests
import traceback

def query_rag(question, collection, embed_model, config, ollama_url="http://localhost:11434/api/chat"):
    """
    Retrieve top-k chunks for question, build a grounded prompt, and generate an answer.
    Returns (answer_text, retrieved_chunks_with_metadata).
    """
    # Step 1: Embed the question
    q_embedding = embed_model.encode([question]).tolist()

    # Step 2: Retrieve top-k
    k = config["top_k"]
    results = collection.query(query_embeddings=q_embedding, n_results=k)
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Step 3: Build the grounded prompt
    context_parts = []
    for i, (chunk, meta) in enumerate(zip(chunks, metadatas), start=1):
        context_parts.append(f"[{i}] (source: {meta['source']})\n{chunk}")
    context = "\n\n".join(context_parts)

    abstention_phrase = config["abstention_phrase"]

    system_prompt = f"""You are a helpful assistant that answers questions strictly from the provided context.

RULES:
1. Answer ONLY using information from the numbered context passages below.
2. Cite the source number in brackets after every claim, like this: "The sky is blue [1]."
3. If the context does not contain enough information to answer the question, respond with exactly:
   {abstention_phrase}
4. Do not add information from your training data. Do not speculate.

CONTEXT:
{context}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    payload = {
        "model": config["model"],
        "messages": messages,
        "stream": False,
        "options": {"temperature": config["temperature"], "seed": config["seed"]}
    }

    try:
        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        answer = response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab2:query_rag] {e}")
        traceback.print_exc()
        raise

    return answer, list(zip(chunks, metadatas))
```

**Step 2: Run and display results for five answerable questions.**

```python
config = json.load(open("config.json"))
collection, embed_model, _ = build_index(config, strategy="fixed")  # use your chosen strategy

answerable_questions = [q for q in QUESTIONS if not q.get("unanswerable")][:5]

for q_item in answerable_questions:
    print(f"\nQ: {q_item['question']}")
    answer, retrieved = query_rag(q_item["question"], collection, embed_model, config)
    print(f"A: {answer}")
    print(f"Retrieved from: {[m['source'] for _, m in retrieved]}")
```

Expected output format (your content will differ):

```
Q: What is the main topic covered in lecture 3?
A: Lecture 3 covers gradient descent and its role in optimizing neural network weights [1].
Retrieved from: ['lecture03.txt', 'lecture02.txt', 'lecture04.txt']
```

**Step 3: Run two abstention questions.**

```python
unanswerable = [q for q in QUESTIONS if q.get("unanswerable")][:2]
for q_item in unanswerable:
    print(f"\nQ: {q_item['question']}")
    answer, _ = query_rag(q_item["question"], collection, embed_model, config)
    print(f"A: {answer}")
    abstained = config["abstention_phrase"] in answer
    print(f"Abstained correctly: {abstained}")
```

Expected output:

```
Q: What year was the Ursinus College library built?
A: I don't have enough information in my knowledge base to answer that.
Abstained correctly: True
```

**Step 4: Show the bare-model hallucination contrast.**

Ask the bare model (no context) the same question where your RAG system gives a correct answer:

```python
def query_bare_model(question, config, ollama_url="http://localhost:11434/api/chat"):
    messages = [{"role": "user", "content": question}]
    payload = {"model": config["model"], "messages": messages, "stream": False,
               "options": {"temperature": config["temperature"], "seed": config["seed"]}}
    r = requests.post(ollama_url, json=payload, timeout=60)
    return r.json()["message"]["content"]

example_q = answerable_questions[0]["question"]
print(f"Question: {example_q}")
print(f"\nBare model answer:\n{query_bare_model(example_q, config)}")
print(f"\nRAG answer:\n{query_rag(example_q, collection, embed_model, config)[0]}")
```

Include this comparison verbatim in your readme.

### Troubleshooting — Part 3

**The model ignores the abstention instruction and answers anyway**
Smaller models sometimes override instructions when they have training-data knowledge. Make the instruction more direct: add "You MUST respond with exactly that phrase and nothing else if the context is insufficient." If it still fails, add a post-processing check in Python: if no `[1]`, `[2]`, etc. bracket appears in the answer and the abstention phrase is absent, override the answer with the abstention phrase and log a warning.

**Citations like `[1]` appear in the answer but the wrong chunk is cited**
This is a retrieval quality issue, not a generation issue. Check your recall@k from Part 2 — if recall@3 is below 0.5, the relevant chunk is not reaching the model. Try increasing `top_k` to 5 or switching chunking strategy.

**The model's answer is cut off mid-sentence**
The context may be too long for the model's context window. Reduce `top_k` from 3 to 2, or reduce `chunk_size` in your config. You can also add `"num_ctx": 4096` to the Ollama options dict to explicitly set the context window size.

---

> **Checkpoint: Before moving to Part 4, make sure you can answer:**
> 1. What is the role of the system prompt's "RULES" section in preventing hallucination? What would happen if you removed Rule 4?
> 2. In your before/after comparison, what specific false claim did the bare model make? What training-data pattern likely caused it?
> 3. How would you modify your pipeline to support a follow-up question ("Tell me more about that") while maintaining citation grounding?

---

## Part 4: Audit

For at least ten answered questions, audit each citation by hand: does the cited chunk actually support the claim? Report a **faithfulness rate** and show any failures verbatim, classified using the hallucination taxonomy from class.

### Step-by-step guide

**Step 1: Build an audit table.**

For each of your ten questions, record:

| Q# | Question | Answer excerpt | Citation # | Chunk cited | Faithful? | Failure type |
|----|----------|----------------|------------|-------------|-----------|--------------|
| Q01 | What is ...? | "Gradient descent is ..." [1] | 1 | "lecture03: Gradient descent is a method..." | Yes | — |
| Q02 | ... | ... | ... | ... | No | Fabrication |

**Step 2: Classify any failures using the taxonomy from class.**

The taxonomy has four categories:
- **Fabrication**: The cited chunk exists but does not contain the claimed fact; the model invented it.
- **Conflation**: The cited chunk is about a related but different topic; the model merged two concepts.
- **Extrapolation**: The chunk implies but does not state the claim; the model over-inferred.
- **Wrong citation**: The fact is correct and appears in the corpus, but it is in a different chunk than cited.

**Step 3: Compute and report your faithfulness rate.**

```python
# Example audit results — fill this in from your hand-audit table
audit_results = [
    {"q_id": "Q01", "faithful": True, "failure_type": None},
    {"q_id": "Q02", "faithful": False, "failure_type": "Extrapolation"},
    # ... add all 10
]

faithful_count = sum(1 for r in audit_results if r["faithful"])
print(f"Faithfulness rate: {faithful_count}/{len(audit_results)} = {faithful_count/len(audit_results):.1%}")
failures = [r for r in audit_results if not r["faithful"]]
for f in failures:
    print(f"  {f['q_id']}: {f['failure_type']}")
```

Include your completed audit table and faithfulness rate in your readme.

### Troubleshooting — Part 4

**Every citation appears faithful, making the audit trivial**
Your question set may be too simple. Add at least two questions that require synthesizing information from multiple chunks — these are most likely to produce conflation or extrapolation errors.

**You cannot find the cited chunk in your collection**
Use `collection.get(ids=["chunk_id"])` to retrieve a specific chunk by its ID. The chunk IDs are in the `metadatas` list returned by `query_rag`.

**The model sometimes cites `[1]` when the relevant information was in `[2]`**
This is a "wrong citation" failure. It is worth noting separately from fabrication — the answer may be correct even though the citation number is wrong. Count these as failures in your faithfulness rate but classify them accurately.

---

> **Checkpoint: Before writing your deliverables, make sure you can answer:**
> 1. What was your faithfulness rate? Is it higher or lower than you expected?
> 2. Which failure type (fabrication, conflation, extrapolation, wrong citation) appeared most often in your audit, and what does that suggest about where to add safeguards?
> 3. Which failure did you find more often overall: retrieval fetching the wrong chunk, or generation misusing a correct chunk?

---

## Deliverables

Submit a ZIP containing your code, JSON configuration, corpus (or a pointer plus a sample if it is large), datasheet, question set with labels, evaluation results (CSV or table), audit results, pair log, and a readme writeup of approximately two pages. Ensure reproducibility by fixing random seeds and listing software version information.

## Reflection Prompts

- Which failure did you find more often: retrieval fetching the wrong chunk, or generation misusing a correct chunk? What does that imply about where to invest next — better retrieval, or a stricter generation prompt?
- Your corpus datasheet names who is absent from your documents. Give a concrete example of a question where that absence would cause your system to either abstain incorrectly (the answer exists somewhere but not in your corpus) or answer incorrectly (the corpus contains a biased or incomplete view). What would you add to the corpus to fix it?
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

## Extension Challenges

These are optional and carry no extra credit.

**Challenge 1 (moderate): Add re-ranking.**
After retrieving top-k=10 chunks, re-rank them by asking the model: "Does this passage answer the question: [question]? Answer yes or no." Keep only the top 3 "yes" passages. Measure whether re-ranking improves your recall@3 on your question set.

**Challenge 2 (harder): Implement hybrid search.**
Combine your embedding-based retrieval with BM25 keyword search (install `rank_bm25`). For each query, retrieve the top-5 from each method, merge the lists (deduplicating by chunk ID), and pass the union to the model. Report whether hybrid search improves recall@3 over either method alone.

**Challenge 3 (hardest): Add source freshness metadata.**
Add a `last_modified` timestamp to each chunk's metadata (from the file's `mtime`). Modify your generation prompt to prefer recent sources when two chunks conflict. Demonstrate this on a question where you have two versions of a document with different information.
