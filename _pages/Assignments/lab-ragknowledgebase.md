---
layout: assignment
permalink: /Assignments/RAGKnowledgeBase
title: "CS357: Foundations of Artificial Intelligence - Lab: RAG Knowledge Base"

info:
  coursenum: CS357
  purpose: "To give an agent you run grounded, citable memory over a corpus you care about, including the honesty to abstain when the answer is not there."
  tilt:
    task: "Build a RAG pipeline over your own corpus with Chroma and a local model, compare chunking strategies by recall@k, and audit its citations and abstention."
    criteria: "Assessed on the citing, abstaining pipeline, an empirical chunking comparison, and a hand-audited evaluation of retrieval and citations; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To construct a complete retrieval-augmented generation pipeline over a personal document corpus using Chroma and a local model
    - To make and defend chunking decisions empirically by comparing at least two strategies with recall@k metrics
    - To evaluate retrieval quality with recall at k and grounding quality with a citation audit
    - To implement and demonstrate abstention when the corpus does not contain an answer
    - To apply parameter-efficient fine-tuning (LoRA/QLoRA) to a local model using a real dataset and a modern training toolchain (Unsloth or hand-rolled transformers/peft/trl)
    - To export a fine-tuned model to GGUF and run it locally in Ollama, making a model you trained a first-class citizen of your local-first stack
    - To instrument training with loss curves and evaluate output quality before and after fine-tuning
    - To understand the trade-offs between fine-tuning, RAG, and prompting for knowledge injection
    - To document a fine-tuned model with a model card and identify potential bias shifts
    - To implement a Monte Carlo retirement simulation that draws annual returns from a configurable normal distribution and records portfolio paths across 1,000 simulations
    - To generate a labeled two-panel visualization showing simulated paths with median and percentile bands, and a histogram of final balances
    - To construct a multimodal API request that encodes a PNG image as a base64 string, packages it in the correct Ollama JSON payload, and parses the structured text response
    - To conduct a two-turn conversation with a multimodal model using a structured prompt that specifies role, required response sections, and audience assumptions
    - To compare AI-generated quantitative claims against ground-truth statistics and identify specific numerical errors with verbatim AI excerpts
    - To evaluate the sensitivity of simulation outcomes to parameter changes and explain the compounding effect of return mean and volatility on the outcome distribution
    - To propose a user-facing guardrail that limits over-reliance on AI numerical claims in financial contexts
  rubric:
    - weight: 30
      description: Pipeline Implementation
      preemerging: The pipeline (code or flow) fails to index or query due to major issues, or the program or flow fails to run
      beginning: The pipeline (code or flow) runs but fails on test questions due to one or more minor issues
      progressing: The pipeline indexes and answers correctly with citations, but a component such as abstention or configuration is fragile or incomplete
      proficient: The pipeline — whether hand-coded or built as a Langflow flow — indexes, retrieves, answers with cited bracketed source numbers, and abstains with the designated phrase when no chunk is relevant; a screenshot or log shows all three behaviors (answer-with-citation, abstention, and the bare-model hallucination contrast); configuration is externalized and exceptions are handled with located messages and tracebacks, or, on the flow route, the exported flow JSON plus documented node settings serve as the externalized configuration
    - weight: 25
      description: Chunking Strategy and Justification
      preemerging: A single arbitrary chunking is used without discussion
      beginning: A chunking choice is stated but not compared against an alternative
      progressing: Two chunking strategies (in code, or as two flow configurations) are compared on a small question set with results reported
      proficient: At least two chunking strategies — implemented in code or as two Langflow configurations with different splitter settings — are compared on a defined question set; recall@k is reported for k in {1,3,5} for each strategy in a table; the shipped choice is defended with a specific numeric comparison (e.g., "strategy A achieves recall@3 of 0.80 vs. 0.60 for strategy B on our question set")
    - weight: 25
      description: Evaluation and Citation Audit
      preemerging: No evaluation is provided
      beginning: Informal trials are described without a protocol or metric
      progressing: A question set with recall at k and an answer accuracy measure is evaluated, with limited citation auditing
      proficient: A question set of at least ten questions is evaluated with recall@k and answer accuracy; every citation in a sample of at least ten answers is audited by hand for faithfulness; a faithfulness rate (e.g., "9/10 citations correctly supported the claim") is reported; any failures are shown verbatim and classified using the hallucination taxonomy from class
    - weight: 10
      description: Code Quality and Documentation
      preemerging: Code or configuration documentation and structure are absent, or the work departs significantly from best practice
      beginning: Code or configuration documentation is limited in ways that reduce the readability and reproducibility of the work
      progressing: Documentation is present that re-states the explicit code or configuration definitions
      proficient: Every non-trivial function has a docstring; all network, embedding, and database operations are wrapped in exception handlers that print a located message (e.g., [lab2:query_corpus]) followed by a traceback; model name, chunk size, overlap, top-k, and abstention threshold are read from a JSON config file rather than hardcoded; on the Langflow route this row is earned by configuration quality — the two exported flow JSONs, documented node settings (model, chunk size, overlap, top-k), and setup notes sufficient to reproduce both flows exactly
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
    - rtitle: "Fine-Tuning vs. RAG"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-finetuningvsrag.md"
    - rtitle: "Unsloth — Fine-Tuning Notebooks and Ollama/GGUF Export (Direction 1)"
      rlink: "https://unsloth.ai/docs/get-started/unsloth-notebooks"
    - rtitle: "Unsloth — Fine-tune Llama 3 and Use in Ollama (Direction 1 tutorial)"
      rlink: "https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/tutorial-how-to-finetune-llama-3-and-use-in-ollama"
    - rtitle: "Running Local Models"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-localmodels.md"
    - rtitle: "Data Cards and Model Cards"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-datacards.md"
    - rtitle: "Sampling, Temperature, and Generation Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-samplinggeneration.md"
    - rtitle: "Evaluating Agent Outputs Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md"
    - rtitle: "Multimodal Agents Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multimodalagents.md"

tags:
  - rag
  - embeddings
  - local-ai
  - fine-tuning
  - lora
  - local-models
  - evaluation
  - multimodal
  - simulation
  - visualization

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

# Requests for Ollama calls (already installed if you did the Local Agent Lab)
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

This lab runs across a multi-week window (see the course schedule for the assigned and due dates). Budget your weeks: aim to have the core pipeline working early — and if a break falls inside your window, front-load — so the direction work and audit are not compressed into the final days. The **RAG Quality Checkup lab**, begun in the mid-window studio session, is a scaffold for this lab: its recall@k measurements, citation audit, and regression harness are this lab's evaluation work done early — carry its results (and its winning chunking configuration) straight back in here.

| Component | Estimated time |
|-----------|----------------|
| Core Parts 1–4 (corpus and datasheet; indexing; grounded generation; citation audit) | 4–5 hours |
| Your chosen direction (see Choose Your Direction below) | 3–5 hours |
| Writeup, learning log, and packaging | included above |
| **Total** | **≈ 8–10 hours** |

(Direction 0, the low-code Langflow route, is estimated at 7–9 hours on its own — but it *replaces* the coding of core Parts 2–3 rather than adding to it, so the lab total stays ≈ 8–10 hours.)

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

Implement indexing with **two chunking strategies** (for example, fixed-size with overlap versus paragraph-structural), with chunk parameters externalized in a JSON configuration file. Build a question set of at least ten questions whose answers you have located by hand (note the source chunk for each). Report **recall@k** for $$k \in \{1, 3, 5\}$$ under both strategies, and choose your shipped configuration with a quantitative defense.

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

```yaml
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
- Two abstentions on questions your corpus cannot answer.
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

## Chunking Strategy Comparison: The Full Walkthrough

In this section your team implements three chunking strategies, runs the same five test questions through all three, and fills in a results table. No external libraries are needed — the retrieval function uses a simple word-frequency cosine similarity (a score between 0 and 1 measuring how much vocabulary two texts share) so the comparison is purely about chunking.

---

### Sample Document

Copy this 400-word excerpt into a string variable called `DOCUMENT`. It covers the history of artificial intelligence and contains facts that span paragraph boundaries — ideal for exposing chunking edge cases.

```python
DOCUMENT = """
The field of artificial intelligence was formally founded at the Dartmouth Conference in 1956,
where John McCarthy, Marvin Minsky, Claude Shannon, and others gathered to explore whether
machines could be made to simulate human intelligence. The participants were optimistic,
predicting that a significant portion of human intellectual activity could be replicated
within a single generation. This optimism led to substantial government funding throughout
the late 1950s and 1960s, particularly from the United States Department of Defense.

Early AI research focused on symbolic reasoning and rule-based systems. Programs like the
Logic Theorist, created by Allen Newell and Herbert Simon in 1956, could prove mathematical
theorems by manipulating symbols according to formal rules. The General Problem Solver,
which followed in 1957, attempted to model human problem-solving strategies using means-ends
analysis. These systems demonstrated that computers could perform tasks previously thought
to require human intelligence, though they struggled with the complexity of real-world problems.

The first AI winter arrived in the 1970s when researchers encountered fundamental limitations.
Minsky and Papert's 1969 book Perceptrons demonstrated mathematical limitations of single-layer
neural networks, dampening enthusiasm for connectionist approaches. Meanwhile, combinatorial
explosion made symbolic AI intractable for realistic problem sizes. Funding from DARPA and
other agencies dried up as promises went unmet, and the field entered a period of reduced
activity and skepticism known as the AI winter.

The expert systems era of the 1980s briefly revived interest. Programs like MYCIN, which
diagnosed bacterial infections and recommended antibiotics, and XCON, which configured
computer hardware for Digital Equipment Corporation, demonstrated genuine commercial value.
XCON alone saved DEC an estimated forty million dollars per year by the mid-1980s. These
systems encoded human expertise as thousands of if-then rules and could outperform novices
in narrow domains, but they were brittle: any question outside the rule set produced no answer.

The rise of machine learning in the 1990s and 2000s shifted the paradigm from hand-coded
rules to systems that learned patterns from data. The availability of larger datasets,
faster processors, and algorithms like support vector machines and boosting made it possible
to achieve high accuracy on tasks like handwriting recognition and email spam filtering
without explicit programming of rules. This data-driven approach would eventually culminate
in the deep learning revolution of the 2010s.
"""
```

---

### Three Chunking Functions

Each function below implements one splitting strategy and returns a list of strings (the chunks). You will pass these chunk lists to the retrieval function in the next section.

```python
def chunk_fixed_size(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split text into fixed-character windows with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]  # drop any empty strings from trailing whitespace


def chunk_by_sentence(text: str, n_sentences: int = 3, overlap: int = 1) -> list[str]:
    """Split text into groups of n_sentences, with overlap sentences between groups."""
    import re
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    chunks = []
    step = max(1, n_sentences - overlap)
    for i in range(0, len(sentences), step):
        group = sentences[i:i + n_sentences]
        if group:
            chunks.append(" ".join(group))
    return chunks


def chunk_by_paragraph(text: str) -> list[str]:
    """Split text on blank lines, treating each paragraph as one chunk."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs
```

---

### Retrieval with Simple Cosine Similarity

This function computes retrieval using word-frequency vectors so you can run the comparison without embedding infrastructure. For production RAG, you would replace this with actual embeddings from a local model.

```python
def cosine_sim(a: str, b: str) -> float:
    """Compute cosine similarity between two strings using word frequency vectors."""
    words = list(set(a.split() + b.split()))
    va = [a.split().count(w) for w in words]
    vb = [b.split().count(w) for w in words]
    dot = sum(x * y for x, y in zip(va, vb))
    mag_a = sum(x * x for x in va) ** 0.5
    mag_b = sum(x * x for x in vb) ** 0.5
    return dot / (mag_a * mag_b + 1e-9)


def retrieve(chunks: list[str], query: str, top_k: int = 3) -> list[str]:
    """Return the top_k chunks most similar to query by cosine similarity."""
    scored = [(cosine_sim(query.lower(), c.lower()), c) for c in chunks]
    return [c for _, c in sorted(scored, reverse=True)[:top_k]]
```

> **Note:** For real RAG, use a local embedding model (e.g., `nomic-embed-text` via Ollama) in place of word-frequency cosine similarity. The word-frequency approach works for this classroom comparison because the test questions deliberately use vocabulary from the document.

---

### Five Test Questions

Use these questions to evaluate all three chunking strategies. For each question, run `retrieve(chunks, question, top_k=2)` and check whether any of the returned chunks actually contain the answer.

```python
QUESTIONS = [
    # Q1: answer is contained within a single paragraph
    "Who were the founders of artificial intelligence at the Dartmouth Conference?",
    # Q2: answer requires connecting two adjacent sentences in different paragraphs
    "What mathematical limitation did Minsky and Papert demonstrate, and when?",
    # Q3: answer uses a specific number that appears mid-paragraph
    "How much money did XCON save Digital Equipment Corporation per year?",
    # Q4: answer is in the last paragraph, using different vocabulary than the question
    "What algorithmic approaches enabled high accuracy on spam filtering?",
    # Q5: answer spans a paragraph boundary between the expert systems era and ML era
    "What limitation did expert systems have compared to machine learning systems?",
]

# Run the comparison
for strategy_name, chunks in [
    ("Fixed (300 chars, overlap=50)", chunk_fixed_size(DOCUMENT)),
    ("By Sentence (3 sent, overlap=1)", chunk_by_sentence(DOCUMENT)),
    ("By Paragraph", chunk_by_paragraph(DOCUMENT)),
]:
    print(f"\n=== {strategy_name} ({len(chunks)} chunks) ===")
    for i, q in enumerate(QUESTIONS, 1):
        results = retrieve(chunks, q, top_k=2)
        print(f"  Q{i}: {q[:60]}...")
        for j, r in enumerate(results, 1):
            print(f"    [{j}] {r[:100].strip()}...")
```

---

### Results Table

Fill in this table after running the comparison. Mark each cell **Y** (the relevant chunk appeared in the top 2 results) or **N** (it did not).

| Chunking Strategy | Num Chunks | Q1 Relevant? | Q2 Relevant? | Q3 Relevant? | Q4 Relevant? | Q5 Relevant? | Recall@2 |
|---|---|---|---|---|---|---|---|
| Fixed (300 chars, overlap=50) | | | | | | | /5 |
| By Sentence (3 sent, overlap=1) | | | | | | | /5 |
| By Paragraph | | | | | | | /5 |

---

### Critical Thinking Questions

9. Fixed-size chunking sometimes splits a sentence mid-phrase. Find one example where this hurt retrieval in your results table. What was the symptom — which question failed, and what did the returned chunks contain instead of the answer?

   > *Hint: Look for a question where the answer spans a character-boundary cut. For example, if chunk N ends with "the participants were" and chunk N+1 begins with "optimistic, predicting...", neither chunk alone answers a question about the founders' predictions. Print a few boundary regions of the fixed chunks to see exactly where cuts landed.*

You increase `chunk_size` from 100 characters to 1000 characters (keeping overlap=0). Which of the following best describes the trade-off?

- Fewer chunks means faster embedding but always better retrieval precision
- Larger chunks improve the chance that a multi-sentence answer is intact in one chunk, but each chunk's embedding blurs across more topics, reducing precision for focused queries
- Larger chunks always increase recall@k regardless of the query
- Chunk size affects only storage cost, not retrieval quality

<details><summary>Answer</summary>

Larger chunks improve the chance that a multi-sentence answer is intact in one chunk, but each chunk's embedding blurs across more topics, reducing precision for focused queries

</details>

> *Hint: Think about the Goldilocks Problem from Part I. A 1000-character chunk might span three different topics. Its embedding vector must summarize all three topics at once. When a user asks about just one of those topics, the chunk may rank lower than a smaller, more focused chunk — even though the answer is physically present inside it.*

10. If `overlap=0` and `chunk_size=100`, a fact that starts at character 95 and ends at character 110 will be split across two chunks and may be incomplete in both. If `overlap=90` and `chunk_size=100`, that same fact appears in many chunks — but what is the cost of very large overlap?

    > *Hint: Calculate how many chunks a 1000-character document produces with chunk_size=100 and overlap=90 versus overlap=0. Every chunk must be embedded and stored. What happens to index size? What happens to retrieval when many nearly identical chunks all rank highly for the same query?*

11. Sentence-based chunking preserves meaning better than fixed-size. But sentences in legal contracts can be 200 words long, and a single contract clause might span 10 such sentences. What chunking strategy would you use for legal documents, and why?

    > *Hint: Consider a hybrid: use structural splits on numbered clauses or headings first (which legal documents typically have), then apply sentence-based chunking within any clause that exceeds a maximum character count. This gives you semantically coherent units at the clause level without risking 2000-word chunks for complex clauses.*

> **⚠️ Common Misconception:** Students often assume that smaller chunks always give better retrieval because they are more "targeted." But very small chunks lose the surrounding context that the similarity function needs to judge relevance. A chunk containing only the words "the act" scores low against almost any query — there is no context for which act, when, or why it matters. The retrieval model (whether word-frequency or a neural embedding) needs enough surrounding text to understand what the chunk is about. A practical lower bound is roughly one complete sentence; a practical upper bound is roughly one focused paragraph.

---

---

**🛑 In-class work stops here.** The exercises below are homework and going-deeper material — attempt them before the related lab.


## Deliverables

> **Bring to class.** Carry your pipeline-in-progress and your stuck points into the *Studio: Local Agent Stack Clinic* session — the studio is open build time, and it is only as useful as the problems you bring to it.

Submit a ZIP containing your code, JSON configuration, corpus (or a pointer plus a sample if it is large), datasheet, question set with labels, evaluation results (CSV or table), audit results, pair log, and a readme writeup of approximately two pages. Ensure reproducibility by fixing random seeds and listing software version information.

## Learning Log

Keep a metacognitive learning log for this lab in your readme: in the spirit of multiple means of action and expression, you may respond to each prompt in prose, in bullet points, or with an annotated diagram — whichever best conveys your thinking. (Prompt 4 adapts the AI-Assisted Learning Template by Marc Watkins.)

1. **What I built.** One paragraph, in plain language that a friend outside of computer science could follow (this is deliberate practice in writing for multiple audiences).
2. **What surprised me.**
3. **What I verified and how.** Evidence, not vibes.
4. **How I used AI during this lab**, and what I learned from that use.
5. **What I'd tell the next student** before they start.
6. **One open question I still have.**

### Lab-specific prompts

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

---

## Choose Your Direction

Everyone completes core Part 1 (corpus and datasheet) and core Part 4 (citation audit). Beyond that, you choose **one** direction below. You do not do more than one. Pick the direction that most interests you, and carry your RAG Knowledge Base Lab corpus, config discipline, and evaluation habits into it.

**Direction 0 is different in kind from the other two.** It is the low-code route through the middle of the lab itself: it **replaces the coding of core Parts 2–3** (indexing and grounded generation) with a visual Langflow build that meets the same requirements — two compared chunking configurations, recall@k, citations, and abstention. Core Part 1 (corpus curation + datasheet) and core Part 4 (citation audit) remain required for everyone, whichever direction you choose. Directions 1 and 2, by contrast, are extensions you complete **after** finishing core Parts 1–4 in code.

The **single 100-point grade for this lab covers your core RAG work plus your chosen direction together** — the graded rubric above still governs your score, and its rows credit a pipeline whether it is hand-coded or built as a flow. Treat the "What proficient work looks like" bullets (or the deliverables list, for Direction 0) in your chosen direction as the standard your work should meet, and fold your direction's deliverables into the same submission ZIP and readme as the core lab.

Choose one:

- **Direction 0: The Langflow Route (low-code)** — build the same RAG pipeline visually on a Langflow canvas over your own corpus: two chunking configurations compared by recall@k, grounded and abstaining answers, no pipeline code authorship. Estimated 7–9 hours (replacing core Parts 2–3, not adding to them).
- **Direction 1: Hands-On Fine-Tuning with LoRA and QLoRA** — instead of retrieving knowledge at query time, bake domain knowledge into the weights, and decide from evidence whether that was worth it compared to your RAG pipeline. GPU or free-Colab or provided-adapter paths available — see the requirements box at its top.
- **Direction 2: Multimodal AI and Monte Carlo Simulation** — turn from text retrieval to images, and probe where a multimodal model reads a chart confidently but wrongly, using a simulation you build as ground truth. Fully local and free (~4.7 GB model pull).

---

<details markdown="1">
<summary><strong>Direction 0: The Langflow Route (low-code)</strong></summary>

This direction is the low-code route through the heart of the lab. You will build the same retrieval-augmented pipeline the core lab specifies — your corpus, chunked and embedded into Chroma, retrieved and answered with citations and abstention — but you will build it **visually in Langflow**, wiring components on a canvas instead of authoring Python. The requirements do not soften: you still compare two chunking configurations empirically, still report recall@k, still force grounding and abstention, and still audit your citations by hand. What changes is the medium.

**What this replaces and what it does not.** Direction 0 replaces the *coding* of core Parts 2–3 (indexing and grounded generation). Core Part 1 — corpus curation and the datasheet — and core Part 4 — the citation audit — remain required and unchanged; you complete them exactly as written, using your Langflow pipeline's answers as the audit material. The writeup expectations are the core lab's.

> **What this direction requires**
>
> - **Accounts:** none.
> - **API costs:** none — the flow runs entirely against your local Ollama server.
> - **Installs / disk:** Langflow (`pip install langflow`, or `uv pip install langflow` for a faster install — expect roughly five minutes and a couple of GB of dependencies), plus the `nomic-embed-text` embedding model in Ollama (~270 MB pull).
> - **Hardware:** any machine that runs the core lab.
> - **No-cost fallback:** this *is* the no-cost, low-code route.

**Estimated time: 7–9 hours** (in place of core Parts 2–3, so the lab total stays ≈ 8–10 hours).

Background material: the [Visual Agent Building with Langflow activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-visualagents.md), especially Part IV's hands-on build — this direction extends that 30-minute build to the full lab standard.

#### Part A: Install and Launch Langflow

```bash
pip install langflow        # or: uv pip install langflow (faster resolver)
langflow run
```

The install takes about five minutes and pulls a large dependency set. When the server banner appears, browse to `http://localhost:7860`. Also pull the embedding model your flow will use:

```bash
ollama pull nomic-embed-text
```

Confirm Ollama is running (`ollama list` shows `llama3.2` and `nomic-embed-text`) before building anything — every model component in your flow points at `http://localhost:11434`.

> **Troubleshooting the install:** if `pip install langflow` fails with a dependency-resolver error, create a fresh virtual environment on Python 3.11/3.12 and install there. If `http://localhost:7860` refuses to connect, the server may still be starting — the first launch is slow; watch the terminal for the "Langflow is running" banner. If a component errors with a connection refusal at runtime, its Base URL is wrong or Ollama is not running.

#### Part B: Build the RAG Flow on the Canvas

Create a **New Flow → Blank Canvas** and wire the pipeline over the corpus you curated in core Part 1 (upload your actual corpus files — not a toy document):

- **Ingest path:** **File** loader (upload your corpus documents) → **Text Splitter** (RecursiveCharacterTextSplitter; set the chunk size and overlap you will defend in Part C) → **Ollama Embeddings** (Model `nomic-embed-text`, Base URL `http://localhost:11434`) → **Chroma** (ingest mode; name the collection and note the persist directory).
- **Query path:** **Chat Input** → **Retriever** over the same Chroma collection (with **Ollama Embeddings** wired in for query embedding; set top-k to match your config) → **Prompt** node with your grounding-and-citation instructions and a `{context}` variable → **Ollama** chat model (`llama3.2`, temperature 0.1, Base URL `http://localhost:11434`) → **Chat Output**.

Component names vary slightly across Langflow versions; the dataflow is what matters, and the Part IV steps in the visual agents activity walk through the same wiring. Run the flow in the playground and confirm an in-corpus question comes back answered with context before moving on. Record every node setting (model, chunk size, overlap, top-k, temperature) in a config notes file — these are your externalized configuration for the rubric.

#### Part C: The Chunking Comparison — Two Flow Configurations

The core lab's empirical chunking requirement, on canvas. Build **two configurations** of your flow that differ only in the Text Splitter's settings (for example, 500 characters with 50 overlap versus 1,000 characters with 100 overlap, or a small-chunk versus large-chunk regime that mimics the fixed-versus-paragraph contrast). Duplicate the flow rather than editing in place, and give each Chroma collection a distinct name so the two indexes cannot contaminate each other.

Then take the **same ten retrieval queries** the core lab requires — ten questions whose answering chunk you have located by hand in your corpus — and run all ten through **both** configurations. For each query, inspect which chunks the retriever returned (the playground's inspection view shows each node's output; this visibility is the point of the canvas) and record whether the relevant document appeared in the top k, for k in {1, 3, 5}.

**Recall@k, in one sentence: the count (reported as a fraction) of queries whose relevant document appears among the top k retrieved chunks.** Fill in the recall table for both configurations:

| Configuration | recall@1 | recall@3 | recall@5 |
|---------------|----------|----------|----------|
| Flow A (chunk=___, overlap=___) | /10 | /10 | /10 |
| Flow B (chunk=___, overlap=___) | /10 | /10 | /10 |

Defend your shipped choice with a specific numeric comparison, exactly as the rubric's chunking row requires.

#### Part D: Grounding and Abstention

Craft the Prompt node so the model **must** cite the retrieved chunks and **must** abstain otherwise. A starting template (tighten it for your corpus):

```text
You answer questions using ONLY the numbered context passages below.
Cite the passage number in brackets, like [1], after every claim.
If the context does not contain the answer, reply exactly:
"I don't have enough information in my knowledge base to answer that."

Context:
{context}
```

Demonstrate it with **three in-corpus queries** (answers with citations) and **two out-of-corpus queries** (clean abstentions), and save all five transcripts. If the model answers an out-of-corpus question from its own general knowledge instead of abstaining, that is a real finding — tighten the prompt, re-run, and report both versions.

#### Part E: Citation Audit and Writeup

Complete core Part 4 unchanged: audit every citation in a sample of at least ten answers from your shipped flow by hand, report a faithfulness rate, and classify failures with the hallucination taxonomy from class. The playground's node-inspection view makes it easy to see exactly which chunk text the model was given — use it to check each bracketed citation against its source chunk. The writeup, datasheet, learning log, and pair log requirements are identical to the core lab; add one paragraph on what the canvas made easier and what it hid from you compared with the code your classmates wrote.

#### Direction 0 Deliverables

Fold these into the standard RAG Knowledge Base Lab submission ZIP:

- **Exported flow JSON × 2** — both chunking configurations (⋯ menu → Export Flow), plus your node-settings config notes.
- **Query/recall table** — the ten queries, their hand-located source chunks, and the completed recall@k table for both configurations with your defended choice.
- **Transcripts** — the three in-corpus and two out-of-corpus grounding/abstention runs, and the answers used in your citation audit.
- **Datasheet** — from core Part 1 (shared requirement).
- **Writeup** — core-lab scope, including the faithfulness rate and failure classification from the audit and the canvas-versus-code paragraph.

</details>

---

<details markdown="1">
<summary><strong>Direction 1: Hands-On Fine-Tuning with LoRA and QLoRA</strong></summary>

This direction takes the opposite approach to knowledge injection from the one you just built. In the core lab, your RAG system kept knowledge *outside* the model and retrieved it at query time. Here you will adapt a local model by **baking** domain knowledge into a small set of trainable weights using **LoRA** (Low-Rank Adaptation — a technique that adds a tiny number of trainable parameters to a frozen base model, making fine-tuning feasible on consumer hardware). You will use a real domain-specific dataset, instrument training with loss tracking, evaluate output quality, and document the result with a model card — and then, crucially, decide whether fine-tuning earned its keep versus the RAG pipeline from the core lab.

> **What this direction requires**
>
> - **Accounts:** a free Hugging Face account. If you use a gated Llama base model, you must also accept the model license on its Hugging Face page and log in with `huggingface-cli`; the non-gated bases in the table below need no license step. A Google account if you take the free Colab path.
> - **API costs:** none — training runs on your own GPU or on Google Colab's free tier; nothing is billed.
> - **Installs / disk:** the training toolchain (`unsloth`, or `transformers`+`peft`+`trl`) in Colab or locally, plus a few GB of disk for model weights and the exported GGUF.
> - **Hardware:** a CUDA GPU with roughly 6–8 GB of VRAM — **or no GPU at all**, using one of the two no-GPU paths below.
> - **No-cost fallback:** Google Colab's free T4 tier runs every step of this direction; if Colab is unavailable to you, the provided-artifact variant below skips training entirely and still earns full credit.

**Time budget:** expect 2–3 hours of active work, with training running in the background (or none at all on the provided-artifact variant).

##### No GPU? Two paths, both full credit

1. **Colab path (the default no-GPU route).** Everything in this direction runs on Google Colab's free T4 GPU: follow the "If using Google Colab with Unsloth (recommended)" setup cell below, then work through Steps A–D exactly as written in the notebook. A 3.8B–8B model with QLoRA fits comfortably in the free tier's ~15 GB of VRAM in a 15–60 minute training run. Download the exported GGUF at the end of Step C.5 and finish the Ollama deployment on your own machine.

2. **Provided-artifact variant (only if Colab is unavailable to you).** Skip training and start from a published adapter: search the Hugging Face Hub for a public LoRA adapter for `llama3.2` — any published llama3.2 LoRA adapter works; pick one whose model card describes its training domain, and cite it — and download it. Then perform **only the deployment and evaluation half** of this direction: the GGUF merge (Step C.5, merging the downloaded adapter instead of one you trained), the `Modelfile`, the `ollama create` / `ollama run` deployment, and the full before/after evaluation of Step C comparing the base model against the adapted model. **This variant earns full credit, with the evaluation weighted more heavily** in place of the training run: extend your before/after comparison to at least 15 prompts (rather than 10), and include the regression analysis, since the evaluation is your primary evidence. The model card (Step D) is still required — document the adapter's provenance, dataset, and license in place of your own training details. This path preserves the direction's deployment and evaluation learning objectives; the loss-curve deliverable is waived for it.

#### Before You Start

##### Prerequisite Checklist

- [ ] GPU access confirmed: your own GPU, Google Colab free tier (T4), or a cloud VM — or the provided-artifact variant chosen (no GPU needed)
- [ ] Python 3.10 or later (`python --version`)
- [ ] If using a Llama model: HuggingFace account and accepted model license at `meta-llama/Meta-Llama-3-8B-Instruct`
- [ ] HuggingFace CLI installed and logged in (if downloading gated models)

##### Environment Setup

You have a choice of training toolchain within this direction — both are acceptable, and you must pick one:

- **Toolchain A (recommended default): [Unsloth](https://unsloth.ai/).** Unsloth wraps `transformers`/`peft`/`trl` with a faster, lower-memory training path (a 7B model fits comfortably on a free Colab T4 in a 15–60 minute run) and — crucially for this course — exports your fine-tuned model **directly to GGUF so it runs in Ollama**, closing the local-first loop you have used all semester. Start from an official [Unsloth notebook](https://unsloth.ai/docs/get-started/unsloth-notebooks) for your base model and adapt it.
- **Toolchain B (see-the-internals alternative): raw `transformers` + `peft` + `trl`.** If you would rather wire the `LoraConfig`, `BitsAndBytesConfig`, and `SFTTrainer` by hand to see exactly what Unsloth abstracts, use the hand-rolled script in Step B. You then convert to GGUF with `llama.cpp` at the end (Step C.5).

Whichever toolchain you pick, the graded work is identical: a converging training run, a before/after evaluation, a model card, **and your fine-tuned model answering a prompt from inside Ollama.**

**If using Google Colab with Unsloth (recommended):** Create a new notebook, set Runtime > Change runtime type > T4 GPU, and run this setup cell first:

```python
# Cell 1: Google Colab Setup (Unsloth)
# Runtime > Change runtime type > T4 GPU

import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "unsloth"])

# Verify GPU is available
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB" if torch.cuda.is_available() else "")
print("Setup complete!")
```

Expected output:

```
CUDA available: True
GPU: Tesla T4
VRAM: 15.8 GB
Setup complete!
```

**If using local hardware:** Run in your terminal:

```bash
pip install unsloth          # Toolchain A (recommended)
# or, for Toolchain B (hand-rolled):
# pip install transformers peft datasets bitsandbytes accelerate trl
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"
```

##### Quick Sanity Check — Confirm Model Downloads Work

```python
# Run this before starting the first step to confirm your HuggingFace access
from transformers import AutoTokenizer

# Use a small, freely available model for the sanity check
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-3-mini-4k-instruct", trust_remote_code=True)
tokens = tokenizer("Hello, world!")
print(f"Tokenizer OK. Token IDs: {tokens['input_ids']}")
```

Expected output:

```
Tokenizer OK. Token IDs: [1, 15043, 29892, 3186, 29991]
```

If you see `OSError: Can't load tokenizer`, check your internet connection and that you are logged into HuggingFace (`huggingface-cli login`).

**Recommended base models (choose one based on your hardware):**

| Model | Size | Min VRAM | Notes |
|-------|------|----------|-------|
| `microsoft/phi-3-mini-4k-instruct` | 3.8B | 6 GB | Best for free Colab T4 |
| `meta-llama/Meta-Llama-3-8B-Instruct` | 8B | 8 GB with QLoRA | Requires HuggingFace token |
| `mistralai/Mistral-7B-Instruct-v0.3` | 7B | 8 GB with QLoRA | Good quality, open weights |

#### Step A: Choose a Domain Dataset

**Why this matters:** The dataset you choose determines everything — what your model learns, what biases it might amplify, and how you can measure success. A natural choice is a dataset in the *same domain as your RAG Knowledge Base Lab corpus*, so your before/after comparison speaks directly to the RAG-versus-fine-tuning question. Choosing a well-structured dataset is the difference between training that converges and training that produces nonsense.

1. **Choose one of the following datasets,** or propose your own (get instructor approval first):

   | Dataset | HuggingFace ID | Domain | Format |
   |---------|----------------|--------|--------|
   | Medical Q&A | `medalpaca/medical_meadow_medical_flashcards` | Medical | instruction/output |
   | Python codegen | `iamtarun/python_code_instructions_18k_alpaca` | Code | instruction/input/output |
   | Legal reasoning | `nguha/legalbench` | Legal | varies by subset |
   | Science questions | `sciq` | Science | question/answer/support |

2. **Load and inspect your dataset:**

```python
# dataset_inspect.py
from datasets import load_dataset

# TODO: replace with your chosen dataset ID
DATASET_ID = "sciq"  # change this

dataset = load_dataset(DATASET_ID)
print(f"Dataset splits: {list(dataset.keys())}")
print(f"Train size: {len(dataset['train'])}")
print(f"\nFirst example:\n{dataset['train'][0]}")
```

Expected output (for `sciq`):

```
Dataset splits: ['train', 'validation', 'test']
Train size: 11679

First example:
{'question': 'What type of force keeps planets in orbit?', 
 'distractor3': 'electromagnetic', 'distractor1': 'nuclear', 
 'distractor2': 'friction', 'correct_answer': 'gravitational',
 'support': 'Gravitational force keeps planets in orbit around the Sun.'}
```

3. **Format the dataset for instruction tuning.** Models trained with SFTTrainer expect a single string per example in a consistent instruction format. Here is a starter formatter — adapt it for your dataset's field names:

```python
# dataset_format.py
from datasets import load_dataset

# TODO: replace with your dataset ID
DATASET_ID = "sciq"

dataset = load_dataset(DATASET_ID)

def format_example(example: dict) -> dict:
    """Convert a raw dataset row into an instruction-tuning string.
    TODO: adapt the field names below to match your chosen dataset."""
    # Example for sciq:
    instruction = example.get("question", "")
    # TODO: replace 'correct_answer' with the answer field in your dataset
    answer = example.get("correct_answer", example.get("output", ""))
    # TODO: include supporting context if available in your dataset
    context = example.get("support", "")

    if context:
        text = f"### Instruction:\n{instruction}\n\n### Context:\n{context}\n\n### Response:\n{answer}"
    else:
        text = f"### Instruction:\n{instruction}\n\n### Response:\n{answer}"

    return {"text": text}

# Apply formatting and create train/validation split
formatted = dataset["train"].map(format_example)

# TODO: adjust split sizes based on your dataset size
# Use 90% train, 10% validation if no validation split exists
if "validation" not in dataset:
    split = formatted.train_test_split(test_size=0.1, seed=42)
    train_data = split["train"]
    val_data = split["test"]
else:
    train_data = formatted
    val_data = dataset["validation"].map(format_example)

print(f"Train examples: {len(train_data)}")
print(f"Validation examples: {len(val_data)}")
print(f"\nFormatted example:\n{train_data[0]['text'][:300]}")
```

4. **Write the dataset section of your model card** (`model_card.md`). Include: source URL, number of examples, format (instruction/input/output or chat turns), your train/validation split sizes, and one known limitation of the dataset.

> **Checkpoint:** Before moving on, verify that your formatted dataset has a `text` field, that the formatted string contains `### Instruction:` and `### Response:` sections, and that you have a validation split with at least 100 examples.

> **Troubleshooting:** If `load_dataset` hangs, you may be behind a firewall that blocks HuggingFace CDN — try `load_dataset(..., cache_dir="/tmp/hf_cache")` or download the dataset manually. If the field names in `format_example` don't match your dataset, print `dataset['train'][0].keys()` to see what fields are available. If the formatted text is empty for some rows, those rows likely have `None` values — add `if not instruction or not answer: return None` and call `.filter(lambda x: x is not None)` after mapping.

#### Step B: Fine-Tune with LoRA / QLoRA

**Why this matters:** LoRA does not modify the original model weights at all — it learns two small matrices (called A and B, with rank `r`) that approximate the weight update. This means you can fine-tune a 7B model on a consumer GPU with 8–16 GB of VRAM. **QLoRA** adds 4-bit quantization on top, cutting VRAM usage roughly in half again.

**Toolchain A (Unsloth, recommended).** Adapt an official [Unsloth notebook](https://unsloth.ai/docs/get-started/unsloth-notebooks) for your base model. The core is only a few lines — Unsloth loads the model already 4-bit-quantized and attaches the LoRA adapters for you:

```python
# train_unsloth.py — LoRA/QLoRA fine-tuning with Unsloth
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

MODEL_ID = "unsloth/Phi-3-mini-4k-instruct"   # TODO: your base model (Unsloth 4-bit variant)
MAX_SEQ = 512

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_ID, max_seq_length=MAX_SEQ, load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(
    model, r=8, lora_alpha=16, lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # TODO: justify
)

# TODO: load and format your dataset into a "text" field, as in Toolchain B below
dataset = load_dataset("sciq")
def format_example(ex):
    return {"text": f"### Instruction:\n{ex.get('question','')}\n\n### Response:\n{ex.get('correct_answer','')}"}
train_data = dataset["train"].map(format_example)

trainer = SFTTrainer(
    model=model, tokenizer=tokenizer, train_dataset=train_data,
    dataset_text_field="text", max_seq_length=MAX_SEQ,
    args=TrainingArguments(
        output_dir="./lora-finetuned", num_train_epochs=1,
        per_device_train_batch_size=4, gradient_accumulation_steps=4,
        learning_rate=2e-4, fp16=True, logging_steps=10, warmup_ratio=0.03,
        report_to="none",
    ),
)
print("Starting training..."); trainer.train()
model.save_pretrained("./lora-finetuned")  # LoRA adapters; GGUF export happens in Step C.5
```

You still own every hyperparameter above and must justify `r`, `learning_rate`, and `target_modules` in your writeup — Unsloth speeds the run, it does not make the choices for you.

**Toolchain B (hand-rolled, see-the-internals alternative).** Create `train.py` and fill in every `# TODO`. This wires the same LoRA/QLoRA setup by hand so you can see what Unsloth abstracts:

```python
# train.py — LoRA/QLoRA fine-tuning with SFTTrainer
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer
from datasets import load_dataset

# ── Configuration ─────────────────────────────────────────────────────────────
# TODO: set to your chosen model
MODEL_ID = "microsoft/phi-3-mini-4k-instruct"
# TODO: set to your chosen dataset (or "local" if you saved it)
DATASET_ID = "sciq"
OUTPUT_DIR = "./lora-finetuned"

# LoRA hyperparameters — these are your starting point, justify your choices
LORA_R = 8           # rank: higher = more capacity, more VRAM. Try 8 or 16.
LORA_ALPHA = 16      # typically 2× rank
LORA_DROPOUT = 0.05  # regularization
# TODO: adjust target_modules for your model family
# Phi-3 / LLaMA family: ["q_proj", "v_proj"] or ["q_proj", "k_proj", "v_proj", "o_proj"]
TARGET_MODULES = ["q_proj", "v_proj"]

# ── 4-bit Quantization (QLoRA) — comment out if you have enough VRAM ─────────
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# ── Load model and tokenizer ──────────────────────────────────────────────────
print(f"Loading {MODEL_ID}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token  # required for batch training

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,  # remove this line if not using QLoRA
    device_map="auto",
    trust_remote_code=True,
)

# ── Apply LoRA adapters ───────────────────────────────────────────────────────
lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    target_modules=TARGET_MODULES,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ── Load and format dataset ───────────────────────────────────────────────────
# TODO: replace with your formatted dataset loading
# If you saved it locally: dataset = load_from_disk("./formatted_dataset")
dataset = load_dataset(DATASET_ID)

def format_example(example):
    # TODO: adapt field names to your dataset
    instruction = example.get("question", "")
    answer = example.get("correct_answer", example.get("output", ""))
    return {"text": f"### Instruction:\n{instruction}\n\n### Response:\n{answer}"}

train_data = dataset["train"].map(format_example)
val_data = dataset.get("validation", dataset["train"].select(range(500))).map(format_example)

# ── Training arguments ────────────────────────────────────────────────────────
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=1,          # TODO: increase to 2-3 if you have time/VRAM
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,          # TODO: justify your choice in the writeup
    fp16=True,
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=50,
    save_steps=100,
    warmup_ratio=0.03,
    report_to="none",            # change to "wandb" if you want W&B tracking
)

# ── Train ─────────────────────────────────────────────────────────────────────
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
    eval_dataset=val_data,
    dataset_text_field="text",
    max_seq_length=512,
)

print("Starting training...")
trainer.train()
trainer.save_model(OUTPUT_DIR)
print(f"Model saved to {OUTPUT_DIR}")
```

2. **Run training** and watch the loss output:

```bash
python train.py
```

Expected training output (your exact numbers will differ, but the pattern should show decreasing loss):

```
trainable params: 4,194,304 || all params: 3,825,160,192 || trainable%: 0.1097
Starting training...
{'loss': 2.3421, 'learning_rate': 0.0002, 'epoch': 0.01}
{'loss': 1.8834, 'learning_rate': 0.00019, 'epoch': 0.05}
{'loss': 1.5201, 'learning_rate': 0.00018, 'epoch': 0.10}
{'loss': 1.3012, 'learning_rate': 0.00015, 'epoch': 0.20}
{'loss': 1.1478, 'learning_rate': 0.00010, 'epoch': 0.40}
{'eval_loss': 1.2341, 'epoch': 0.40}
...
Model saved to ./lora-finetuned
```

A healthy training run shows loss decreasing from roughly 2.3 toward 1.1 over 200 steps. If loss is stuck above 2.0 or oscillates wildly, see troubleshooting below.

3. **Plot your loss curve.** After training, add this cell to your notebook or script:

```python
# plot_loss.py
import json
import matplotlib.pyplot as plt

# Load training logs (saved by Trainer in output_dir/trainer_state.json)
with open("./lora-finetuned/trainer_state.json") as f:
    state = json.load(f)

train_steps = [e["step"] for e in state["log_history"] if "loss" in e]
train_loss  = [e["loss"] for e in state["log_history"] if "loss" in e]
eval_steps  = [e["step"] for e in state["log_history"] if "eval_loss" in e]
eval_loss   = [e["eval_loss"] for e in state["log_history"] if "eval_loss" in e]

plt.figure(figsize=(10, 5))
plt.plot(train_steps, train_loss, label="Training loss", color="blue")
plt.plot(eval_steps, eval_loss, label="Validation loss", color="orange", linestyle="--")
plt.xlabel("Steps")
plt.ylabel("Loss")
plt.title("Training vs. Validation Loss")
plt.legend()
plt.grid(True)
plt.savefig("loss_curve.png", dpi=150)
plt.show()
print("Saved loss_curve.png")
```

4. **Annotate the curve** in your writeup: Does loss converge? Is there overfitting (training loss keeps falling but validation loss rises or plateaus)? Justify at least one hyperparameter choice (why you chose your value of `r`, number of epochs, or learning rate).

> **Checkpoint:** Before moving on, verify that `./lora-finetuned/` directory exists and contains adapter files, that `loss_curve.png` was saved, and that training loss decreased from the first logged step to the last.

> **Troubleshooting:** If you get `CUDA out of memory`, reduce `per_device_train_batch_size` to 2 or 1, and increase `gradient_accumulation_steps` to keep effective batch size the same. If loss is `nan` from step 1, your learning rate is too high — try `1e-4` or `5e-5`. If `target_modules` raises a `ValueError` saying the module does not exist, print `[name for name, _ in model.named_modules()]` to see the actual module names in your model. If training takes longer than 2 hours on Colab, reduce the dataset to 2000 examples with `train_data = train_data.select(range(2000))`.

#### Step C: Evaluate Before and After

**Why this matters:** Without systematic evaluation, fine-tuning is a black box — you spent hours training, but do you actually know if the model improved? This step builds the habit of measuring before you ship, exactly as you did with recall@k and the citation audit in the core lab.

1. **Load both the base model and your fine-tuned model** for comparison:

```python
# evaluate_models.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# TODO: set to your model ID
MODEL_ID = "microsoft/phi-3-mini-4k-instruct"
LORA_PATH = "./lora-finetuned"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

def load_base_model():
    return AutoModelForCausalLM.from_pretrained(
        MODEL_ID, device_map="auto", trust_remote_code=True, torch_dtype=torch.float16
    )

def load_finetuned_model(base_model):
    return PeftModel.from_pretrained(base_model, LORA_PATH)

def generate(model, prompt: str, max_new_tokens: int = 200) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    # Return only the newly generated tokens, not the prompt
    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)
```

2. **Run 10 test prompts** (not seen during training) through both models:

```python
# Add to evaluate_models.py

# TODO: write 10 test prompts relevant to your chosen domain
# These must NOT be from the training set
TEST_PROMPTS = [
    "### Instruction:\nWhat is the primary mechanism of action of beta-blockers?\n\n### Response:",
    "### Instruction:\nExplain the difference between supervised and unsupervised learning.\n\n### Response:",
    # TODO: add 8 more prompts
]

import csv

base_model = load_base_model()
ft_model = load_finetuned_model(load_base_model())

rows = []
for i, prompt in enumerate(TEST_PROMPTS):
    print(f"Prompt {i+1}/{len(TEST_PROMPTS)}...")
    base_out = generate(base_model, prompt)
    ft_out = generate(ft_model, prompt)

    # TODO: manually rate each pair and fill in 'improvement' and 'notes'
    rows.append({
        "prompt": prompt[:80],
        "base_output": base_out[:200],
        "finetuned_output": ft_out[:200],
        "improvement": "?",  # fill in: Y / N / Partial
        "notes": ""
    })

with open("eval_comparison.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["prompt","base_output","finetuned_output","improvement","notes"])
    writer.writeheader()
    writer.writerows(rows)

print("Saved eval_comparison.csv — open it and fill in the improvement and notes columns.")
```

3. **Compute at least one quantitative metric.** Choose one:

   **Option A — Perplexity on held-out test set (lower is better):**

   ```python
   # perplexity.py
   import torch
   import math

   def compute_perplexity(model, tokenizer, texts: list[str], max_length: int = 512) -> float:
       model.eval()
       total_loss = 0
       total_tokens = 0
       for text in texts:
           inputs = tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True).to(model.device)
           with torch.no_grad():
               outputs = model(**inputs, labels=inputs["input_ids"])
           total_loss += outputs.loss.item() * inputs["input_ids"].shape[1]
           total_tokens += inputs["input_ids"].shape[1]
       return math.exp(total_loss / total_tokens)

   # TODO: load test texts from your dataset
   test_texts = ["### Instruction:\n...\n\n### Response:\n..."]  # replace with real test set

   base_ppl = compute_perplexity(base_model, tokenizer, test_texts)
   ft_ppl   = compute_perplexity(ft_model,   tokenizer, test_texts)
   print(f"Base model perplexity:        {base_ppl:.2f}")
   print(f"Fine-tuned model perplexity:  {ft_ppl:.2f}")
   print(f"Improvement: {((base_ppl - ft_ppl) / base_ppl * 100):.1f}%")
   ```

   Expected output (numbers will vary):
   ```
   Base model perplexity:        24.31
   Fine-tuned model perplexity:  11.87
   Improvement: 51.2%
   ```

   **Option B — Task accuracy (for MCQ datasets):**
   ```python
   # For sciq or similar: compare model's top predicted answer to correct_answer
   # TODO: implement for your dataset
   ```

   **Option C — LLM-as-judge score (1–5):**
   ```python
   # Use an LLM-as-judge, or write a simple one here
   # TODO: call your judge on each of the 10 test prompts
   ```

4. **Document at least one regression** in your writeup — a prompt where the base model was better. This is expected and important to be honest about.

5. **Compare against your RAG pipeline.** Take two or three of the questions your RAG system answered from your corpus, and ask the fine-tuned model the same questions with no retrieval. Which approach answered more faithfully? Which hallucinated? Record the head-to-head so your recommendation (below) rests on evidence, not intuition.

> **Checkpoint:** Before moving on, verify that `eval_comparison.csv` has 10 rows, that you have manually filled in the `improvement` column for each row, and that your quantitative metric (perplexity, accuracy, or judge score) has been computed for both base and fine-tuned models.

> **Troubleshooting:** If the fine-tuned model produces repetitive output (same phrase repeated over and over), add `repetition_penalty=1.2` to the `generate()` call. If both models produce identical output, the LoRA adapter may not have loaded correctly — check that `PeftModel.from_pretrained` is pointing to the correct directory and that `adapter_config.json` exists there. If perplexity of the fine-tuned model is higher than the base model, the model may have overfit — check your loss curve for a rising validation loss.

#### Step C.5: Export to GGUF and Run Your Model in Ollama

**Why this matters:** All semester your agents have talked to **Ollama**. A fine-tuned model that only runs inside a Colab notebook is not yet part of your stack. This step closes the loop: you convert your adapted model to **GGUF** (the quantized file format Ollama loads) and run *your own model* locally, exactly like the stock models you have been using. This is the payoff of a local-first course — the model you trained becomes a first-class citizen of the same runtime.

1. **Merge and export to GGUF.**
   - **Toolchain A (Unsloth):** Unsloth exports GGUF in one call. After training:
     ```python
     # Merge LoRA into the base weights and write a quantized GGUF
     model.save_pretrained_gguf("my-finetuned-gguf", tokenizer, quantization_method="q4_k_m")
     # Produces my-finetuned-gguf/*.gguf
     ```
   - **Toolchain B (hand-rolled):** merge the adapter, then convert with `llama.cpp`:
     ```bash
     # After merging PeftModel into the base model and saving to ./merged-model:
     git clone https://github.com/ggerganov/llama.cpp
     python llama.cpp/convert_hf_to_gguf.py ./merged-model --outfile my-finetuned.gguf --outtype q4_k_m
     ```
2. **Download the `.gguf` file** to the machine running Ollama (from Colab: `from google.colab import files; files.download(...)`, or save to Google Drive).
3. **Write a `Modelfile`** that points Ollama at your GGUF and sets the chat template/system prompt you trained against:
   ```
   FROM ./my-finetuned.gguf
   SYSTEM "You are a domain assistant fine-tuned for <your domain>."
   PARAMETER temperature 0.7
   ```
4. **Register and run it:**
   ```bash
   ollama create my-finetuned -f Modelfile
   ollama run my-finetuned "Ask a question from your domain here"
   ```
5. **Capture the transcript.** Include a terminal screenshot or log of `ollama run my-finetuned` answering one in-domain prompt. This transcript is a required deliverable — it is the evidence that your fine-tuned model actually runs in your local stack.

> **Troubleshooting:** If `ollama create` fails to parse the GGUF, confirm the file finished downloading (compare byte sizes) and that your Ollama version supports the quantization you chose (`q4_k_m` is widely supported). If the model loads but answers in gibberish, your `Modelfile` chat template likely does not match the instruction format you trained on — set a `TEMPLATE` block matching your `### Instruction / ### Response` format.

#### Step D: Model Card and Reflection

**Why this matters:** A model without documentation is a liability. The model card format (from Mitchell et al. 2019) is the industry standard for responsible AI deployment — every major model on HuggingFace uses it. Writing one forces you to articulate what your model does, what it does not do, and what could go wrong — the same discipline as the corpus datasheet in the core lab.

1. **Create `model_card.md`** with all eight required sections. Use this template:

```markdown
# Model Card: [Your Model Name]

## Model Details
- **Base model:** [model ID]
- **Fine-tuning method:** LoRA (r=[your r], alpha=[your alpha], target_modules=[your modules])
- **Training dataset:** [dataset name and size]
- **Training duration:** [steps, epochs, wall-clock time]
- **Developer:** [your name]
- **Date:** [date]

## Intended Use
**Primary use case:** [what this model is for, e.g., "answering medical flashcard questions"]

**Out-of-scope use cases:**
- TODO: list at least 2 uses this model should NOT be used for
- Example: "Clinical diagnosis or treatment decisions"

## Factors
- **Relevant factors:** [language, domain, question type, etc.]
- **Evaluation factors:** [what variables you held constant and which you varied]

## Metrics
- **Evaluation metric(s):** [perplexity / accuracy / LLM-as-judge]
- **Threshold for acceptable performance:** [what number would you be happy with?]

## Training Data
[Reference Step A. Include: source, size, format, train/val split, known limitations]

## Quantitative Analyses
[Reference Step C table. Include your before/after metric values.]

| Metric | Base Model | Fine-Tuned Model | Change |
|--------|-----------|------------------|--------|
| Perplexity | X | Y | -Z% |
| Qualitative improvement rate | X/10 | Y/10 | +N |

## Ethical Considerations
**Bias risks:**
- TODO: identify at least one bias that your chosen dataset might introduce or amplify
- Example: "The medical_meadow dataset skews toward Western clinical practice. The fine-tuned model may perform poorly on questions about traditional or non-Western medicine."

**Privacy risks:** [does the training data contain PII?]

## Caveats
- TODO: list at least 2 known limitations of your fine-tuned model
- Example: "Performance degrades on questions longer than 200 tokens"
```

2. **Answer the reflection prompts** in your writeup, including the fine-tuning-versus-RAG recommendation below.

> **Checkpoint:** Before submitting, verify that `model_card.md` has all eight sections and that the Ethical Considerations section names a specific bias risk tied to your chosen dataset.

> **Troubleshooting:** If you are unsure what biases your dataset introduces, search for published papers or datasheets about your chosen dataset — most HuggingFace datasets have a "Dataset Card" tab that discusses known biases and limitations.

#### Direction 1 Extension Challenges (optional)

These challenges push this direction from a working fine-tune to a research-grade experiment.

**Extension 1: LoRA rank ablation.** Train three versions of your model with `r=4`, `r=8`, and `r=16`. Plot all three loss curves on the same axes. Does increasing rank improve final loss? Does it improve perplexity on the test set? How does it affect VRAM usage? Report all three in a table.

**Extension 2: LoRA vs QLoRA memory comparison.** Train once with 4-bit quantization (QLoRA) and once without. Use `torch.cuda.max_memory_allocated()` after training to measure peak VRAM. How much memory did quantization save? Did it hurt final model quality?

**Extension 3: Few-shot prompting vs. fine-tuning.** Take 10 of your training examples and put them directly into the base model's context window as few-shot examples. Compare the few-shot base model's output quality to your fine-tuned model on the test set. When does fine-tuning win, and when does few-shot prompting match it with far less effort?

#### Direction 1 Deliverables

Fold these into your RAG Knowledge Base Lab submission ZIP and readme:

- `train.py`/`train_unsloth.py` or Colab notebook (`.ipynb`) — runnable training script (note which toolchain you used)
- `dataset_format.py` — dataset loading and formatting code
- `evaluate_models.py` — comparison script
- `loss_curve.png` — annotated training/validation loss plot
- `eval_comparison.csv` — before/after comparison table (10 rows)
- Quantitative metric results (printed output, screenshot, or CSV)
- `Modelfile` and a terminal transcript/screenshot of `ollama run my-finetuned` answering an in-domain prompt (evidence your model runs in Ollama)
- `model_card.md` — complete model card with all 8 sections
- A section in your `writeup.md` covering reflection answers, hyperparameter justifications, and your fine-tuning-versus-RAG recommendation

#### What proficient work looks like (Direction 1)

- Training runs with a loss curve, a quantitative before/after metric (perplexity or a task-specific metric), a before/after comparison table, and at least one hyperparameter choice justified with evidence.
- The fine-tuned model is exported to GGUF and demonstrably runs in Ollama via a `Modelfile`, with a transcript of it answering an in-domain prompt.
- The dataset is described with source, size, format, and any cleaning applied; a validation set is used to catch overfitting; and at least one dataset limitation is named.
- Evaluation is systematic with a defined metric, honestly reports at least one regression (something the fine-tuned model does worse), and delivers a defended recommendation for whether fine-tuning was worth it versus RAG and prompting.
- The model card is complete across all eight sections, the bias-risk section identifies at least one bias shift the fine-tuning introduced or amplified, and the reflection answers are substantive and grounded in your own results.

#### Direction 1 Reflection Prompts

- You spent hours fine-tuning a model on 1,000 examples. A colleague says "just put those examples in the system prompt instead." Evaluate that suggestion: when would they be right, and when would fine-tuning be worth the effort?
- You built a RAG system in the core lab and a fine-tuned model here for related knowledge. For your specific domain, which one would you deploy, and what evidence from your two evaluations drives that choice?
- Your fine-tuned model may now perform better in your domain but worse on general questions. Who is responsible for communicating that trade-off to users?
- How many hours did this direction take?

</details>

---

<details markdown="1">
<summary><strong>Direction 2: Multimodal AI and Monte Carlo Simulation</strong></summary>

This direction turns from text retrieval to images. In the core lab you audited whether a model faithfully used *text* you retrieved; here you will audit whether a **multimodal** model faithfully reads *a chart*. You will build a Monte Carlo retirement simulation that you generate, send its chart to a local vision model, and discover that AI image analysis is impressively capable at pattern recognition but surprisingly fragile on numerical precision — and that the difference matters enormously when the output might influence someone's financial decisions. The ground-truth-versus-AI-claim audit is the same muscle you built in the core lab's citation audit, applied to pixels instead of passages.

This direction is completed in **pairs using driver/navigator roles**: the driver types while the navigator reviews, questions, and consults documentation, and you must **swap roles at least every 30 minutes**, keeping a brief log of swap times and who held each role.

> **What this direction requires**
>
> - **Accounts:** none.
> - **API costs:** none — the vision model runs locally in Ollama.
> - **Installs / disk:** `numpy`, `matplotlib`, and `requests`, plus the `llava` multimodal model (~4.7 GB pull; smaller alternatives such as `moondream`, `bakllava`, or `llava-phi3` also work).
> - **Hardware:** any machine that runs the core lab; the 4.7 GB model is happiest with 8 GB of RAM or more. Pull it before the day you need it.
> - **No-cost fallback:** not needed — fully local and free.

#### Before You Start

**Why Monte Carlo?** A spreadsheet gives you one future. Monte Carlo simulation gives you a thousand. Instead of projecting a single "expected" outcome, we draw thousands of possible annual returns from a statistical distribution, let each one play out over a 40-year career, and look at the spread of endings. That spread — not the center — is what matters when you are making a decision whose consequences will compound for decades. This is why financial planners use simulation rather than a single formula, and it is why the visualization you generate will be more informative than any average.

**Prerequisite concepts** — make sure you have completed these activities before writing any code:

- [Sampling, Temperature, and Generation Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-samplinggeneration.md) — stochastic sampling and output distributions
- [Evaluating Agent Outputs Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md) — how to critically assess AI-generated content
- [Multimodal Agents Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multimodalagents.md) — sending images to local vision models

**Tools to install:**

```bash
pip install numpy matplotlib requests
```

**Verify your multimodal model is available:**

```bash
ollama pull llava
ollama list
```

Expected output:

```
NAME               ID              SIZE    MODIFIED
llava:latest       8dd30f6b0cb1    4.7 GB  2 minutes ago
```

If `llava` is not available on your machine, any of the following will work: `moondream`, `bakllava`, `llava-phi3`. Update the `"model"` key in your config file to match whichever you pull.

**Verify the API responds:**

```bash
curl http://localhost:11434/api/tags
```

Expected output (abbreviated):

```json
{"models":[{"name":"llava:latest", ...}]}
```

**Estimated time budget:**

| Part | Task | Estimated time |
|------|------|----------------|
| Step A | Simulation Engine | 50–70 min |
| Step B | Multimodal Integration | 40–60 min |
| Step C | Parameter Sensitivity | 25–35 min |
| Step D | Critical Analysis | 20–30 min |
| Writeup | Readme and reflection | 30–45 min |

#### Step A: The Simulation Engine

You will write a Python script that simulates 1,000 possible futures for a person who starts saving at age 25 and retires at 65. Each simulated year draws a random annual return from a normal distribution, applies it to the portfolio, and records the resulting balance. The output is a two-panel chart saved to disk. Keep the same config-file discipline you used in the core lab — externalizing parameters is what makes the sensitivity analysis in Step C a one-file edit.

##### Step A.1: Create your configuration file.

Create `config.json` in your project root. Externalizing parameters here means you can run Step C's sensitivity analysis by editing one file rather than hunting through your code.

```json
{
  "starting_age": 25,
  "retirement_age": 65,
  "life_expectancy": 90,
  "starting_savings": 10000,
  "monthly_contribution": 500,
  "annual_return_mean": 0.07,
  "annual_return_std": 0.12,
  "inflation_rate": 0.025,
  "num_simulations": 1000,
  "model": "llava",
  "ollama_url": "http://localhost:11434"
}
```

##### Step A.2: Write the simulation function.

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import base64
import io
import requests
import json
import traceback


def load_config(path="config.json"):
    """Load simulation and model parameters from a JSON config file."""
    with open(path) as f:
        return json.load(f)


def simulate_retirement(cfg):
    """
    Run a Monte Carlo retirement simulation.

    Draws annual returns from N(annual_return_mean, annual_return_std) for each
    simulated year of a career, applying monthly contributions each year.

    Returns:
        np.ndarray of shape (num_simulations, years_to_retirement), where each
        row is one simulated portfolio path and each column is the end-of-year balance.
    """
    years = cfg["retirement_age"] - cfg["starting_age"]
    results = np.zeros((cfg["num_simulations"], years))

    for sim in range(cfg["num_simulations"]):
        balance = cfg["starting_savings"]
        for year in range(years):
            # TODO: Add annual contribution (monthly_contribution * 12)
            balance += cfg["monthly_contribution"] * 12

            # TODO: Draw a random annual return from a normal distribution
            #       using annual_return_mean and annual_return_std.
            #       Hint: np.random.normal(mean, std)
            annual_return = np.random.normal(
                cfg["annual_return_mean"], cfg["annual_return_std"]
            )

            # TODO: Apply the return to the balance.
            balance *= (1 + annual_return)

            # TODO: Clip balance at 0 — a portfolio cannot go negative.
            balance = max(balance, 0)

            results[sim, year] = balance

    return results
```

##### Step A.3: Write the visualization function.

```python
def plot_simulation(balances, cfg):
    """
    Create a labeled two-panel visualization of simulation results.

    Left panel: all simulated portfolio paths (light gray) plus median (blue)
    and 10th/90th percentile bands (red dashed).

    Right panel: histogram of final balances at retirement, with vertical
    lines at the median and at $1 million.

    Saves the figure to retirement_simulation.png and also returns a
    base64-encoded PNG string for sending to the multimodal model.

    Returns:
        str: base64-encoded PNG image.
    """
    ages = list(range(cfg["starting_age"] + 1, cfg["retirement_age"] + 1))
    median_path = np.median(balances, axis=0)
    p10_path = np.percentile(balances, 10, axis=0)
    p90_path = np.percentile(balances, 90, axis=0)
    final_balances = balances[:, -1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- Left panel: portfolio paths ---
    # TODO: Plot each simulated path in light gray with alpha=0.05
    for path in balances:
        ax1.plot(ages, path, color="gray", alpha=0.05, linewidth=0.5)

    # TODO: Plot median in solid blue, labeled "Median"
    ax1.plot(ages, median_path, color="blue", linewidth=2, label="Median")

    # TODO: Plot 10th percentile in red dashed, labeled "10th / 90th percentile"
    ax1.plot(ages, p10_path, color="red", linewidth=1.5, linestyle="--",
             label="10th / 90th percentile")

    # TODO: Plot 90th percentile in red dashed (same label so it shares the legend entry)
    ax1.plot(ages, p90_path, color="red", linewidth=1.5, linestyle="--")

    # TODO: Label x-axis ("Age"), y-axis ("Portfolio Balance"), add title and legend
    ax1.set_xlabel("Age", fontsize=12)
    ax1.set_ylabel("Portfolio Balance", fontsize=12)
    ax1.set_title(
        f"Monte Carlo Retirement Simulation\n"
        f"{cfg['num_simulations']:,} paths | "
        f"${cfg['monthly_contribution']:,}/mo contribution | "
        f"Mean return {cfg['annual_return_mean']:.0%}",
        fontsize=11
    )
    ax1.legend(fontsize=10)

    # TODO: Format the y-axis as currency using mticker.FuncFormatter
    ax1.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
    )

    # --- Right panel: final balance histogram ---
    # TODO: Plot a histogram of final_balances with 50 bins
    ax2.hist(final_balances, bins=50, color="steelblue", edgecolor="white", alpha=0.8)

    # TODO: Add a vertical line at the median final balance (blue, solid)
    ax2.axvline(np.median(final_balances), color="blue", linewidth=2,
                label=f"Median: ${np.median(final_balances):,.0f}")

    # TODO: Add a vertical line at $1,000,000 (green, dashed)
    ax2.axvline(1_000_000, color="green", linewidth=1.5, linestyle="--",
                label="$1 Million milestone")

    ax2.set_xlabel("Final Balance at Retirement", fontsize=12)
    ax2.set_ylabel("Number of Simulations", fontsize=12)
    ax2.set_title("Distribution of Final Balances at Age 65", fontsize=11)
    ax2.legend(fontsize=10)
    ax2.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M")
    )

    plt.tight_layout()
    plt.savefig("retirement_simulation.png", dpi=150, bbox_inches="tight")
    print("Saved: retirement_simulation.png")

    # Encode as base64 for the multimodal model API
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
```

##### Step A.4: Add a statistics summary.

```python
def save_statistics(balances, cfg, path="simulation_stats.txt"):
    """
    Compute and save key statistics from the simulation to a text file.
    """
    final = balances[:, -1]
    prob_million = (final >= 1_000_000).mean()

    lines = [
        f"Simulation parameters:",
        f"  Monthly contribution: ${cfg['monthly_contribution']:,}",
        f"  Mean annual return:   {cfg['annual_return_mean']:.1%}",
        f"  Return std dev:       {cfg['annual_return_std']:.1%}",
        f"  Number of paths:      {cfg['num_simulations']:,}",
        f"",
        f"Final balance at retirement (age {cfg['retirement_age']}):",
        f"  10th percentile: ${np.percentile(final, 10):>12,.0f}",
        f"  Median (50th):   ${np.median(final):>12,.0f}",
        f"  90th percentile: ${np.percentile(final, 90):>12,.0f}",
        f"  Mean:            ${final.mean():>12,.0f}",
        f"",
        f"Probability of reaching $1 million: {prob_million:.1%}",
    ]

    text = "\n".join(lines)
    print(text)
    with open(path, "w") as f:
        f.write(text)
    print(f"Saved: {path}")
    return text
```

##### Step A.5: Wire Step A together and run a smoke test.

```python
if __name__ == "__main__":
    cfg = load_config()
    np.random.seed(42)

    print("Running simulation...")
    balances = simulate_retirement(cfg)

    print("Generating visualization...")
    image_b64 = plot_simulation(balances, cfg)

    print("Computing statistics...")
    stats_text = save_statistics(balances, cfg)
```

**Expected output when Step A is complete:**

```
Running simulation...
Generating visualization...
Saved: retirement_simulation.png
Computing statistics...
Simulation parameters:
  Monthly contribution: $500
  Mean annual return:   7.0%
  Return std dev:       12.0%
  Number of paths:      1,000

Final balance at retirement (age 65):
  10th percentile: $      341,208
  Median (50th):   $    1,042,577
  90th percentile: $    2,847,031
  Mean:            $    1,298,451

Probability of reaching $1 million: 53.2%
Saved: simulation_stats.txt
```

Your exact numbers will vary by random seed. The two-panel PNG should show: (left) a fan of gray paths narrowing to a few wide-spread outcomes at age 65, with a visible median line and two outer dashed bands; (right) a right-skewed histogram of final balances with a vertical median line and a $1M milestone line.

##### Troubleshooting — Step A

**`ValueError: could not broadcast input array from shape...` in `simulate_retirement`**
Check that `results` is indexed as `results[sim, year]` and that `year` runs from `0` to `years - 1`. Off-by-one errors here cause shape mismatches.

**Chart y-axis shows scientific notation instead of dollar amounts**
The `FuncFormatter` must be assigned *after* `ax1` is populated. If you call it before plotting, matplotlib may overwrite it. Move the formatter call to just before `plt.tight_layout()`.

**Simulation runs but all paths converge to zero**
The balance clip at zero combined with a very negative return draw can zero out a portfolio early. Check that you are adding the contribution *before* applying the return, and that `annual_return_std` is not set unreasonably high in your config.

> **Checkpoint: Before moving to Step B, make sure you can answer:**
> 1. What does the width of the fan (the gap between the 10th and 90th percentile lines) represent in plain English? How would you expect it to change if you doubled `num_simulations`?
> 2. Why does the histogram in the right panel skew right rather than form a symmetric bell curve?
> 3. If `starting_savings` were $0, what would change in the simulation? In the chart? Test it.

#### Step B: Connecting to a Multimodal Model

You will send the PNG you just generated to a local multimodal model via the Ollama API and conduct a two-turn conversation about the chart.

##### Step B.1: Write the API call function.

```python
def ask_multimodal_model(image_b64, question, cfg):
    """
    Send an image and a text question to a local multimodal model via Ollama.

    Args:
        image_b64: base64-encoded PNG string (from plot_simulation).
        question:  text prompt to accompany the image.
        cfg:       config dict containing 'model' and 'ollama_url'.

    Returns:
        str: the model's text response, or an error message.
    """
    payload = {
        "model": cfg["model"],
        "prompt": question,
        "images": [image_b64],
        "stream": False,
    }
    try:
        url = cfg["ollama_url"] + "/api/generate"
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        print(f"[montecarlo:ask_multimodal_model] {e}")
        traceback.print_exc()
        raise
```

##### Step B.2: Write the two-turn conversation.

The first turn sends a structured prompt that tells the model its role, what to look at, how to format its response, and what audience to assume. The second turn presses it on a specific quantitative claim.

```python
def run_analysis_conversation(image_b64, cfg):
    """
    Conduct a two-turn conversation with the multimodal model about the chart.

    Turn 1: structured analysis with four required sections.
    Turn 2: follow-up pressing the model to estimate a specific probability.

    Returns:
        tuple: (response_turn1: str, response_turn2: str)
    """
    initial_prompt = (
        "You are a financial educator analyzing a Monte Carlo retirement simulation "
        "chart for a college student audience with no prior finance background.\n\n"
        "The chart has two panels:\n"
        "- Left panel: 1,000 simulated portfolio paths from age 25 to 65, with a "
        "solid blue median line and two red dashed lines showing the 10th and 90th "
        "percentile bounds.\n"
        "- Right panel: a histogram of final portfolio balances at age 65, with a "
        "vertical blue line at the median and a vertical green dashed line at $1 million.\n\n"
        "Please analyze the chart and respond in exactly four numbered sections:\n"
        "1. What the spread of paths (the gap between the dashed red lines) tells us "
        "about retirement savings risk.\n"
        "2. Your estimate of what percentage of simulations ended above $1 million, "
        "based on the histogram.\n"
        "3. One specific, actionable insight for a 25-year-old starting their career.\n"
        "4. One limitation of this simulation that a tool deployer should disclose to users."
    )

    print("=== Turn 1: Initial Analysis ===")
    response1 = ask_multimodal_model(image_b64, initial_prompt, cfg)
    print(response1)

    # TODO: Formulate a follow-up question that presses the model on a specific
    # quantitative claim from its Turn 1 response.
    # The suggested follow-up below asks it to show its reasoning for the percentage
    # estimate — this is where numerical precision often breaks down.
    followup = (
        "Based specifically on the histogram in the right panel, walk me through your "
        "reasoning for the percentage estimate you gave in section 2. What visual "
        "features of the histogram did you use, and how confident are you in that number?"
    )

    print("\n=== Turn 2: Follow-Up ===")
    response2 = ask_multimodal_model(image_b64, followup, cfg)
    print(response2)

    # Save both turns to a file for your writeup
    with open("model_responses.txt", "w") as f:
        f.write("=== Turn 1 ===\n")
        f.write(response1 + "\n\n")
        f.write("=== Turn 2 ===\n")
        f.write(response2 + "\n")
    print("\nSaved: model_responses.txt")

    return response1, response2
```

##### Step B.3: Add Step B to your main block.

Extend the `if __name__ == "__main__":` block from Step A:

```python
    print("\nRunning multimodal analysis...")
    response1, response2 = run_analysis_conversation(image_b64, cfg)
```

**Example of a good AI response (Turn 1):** The model might correctly observe that the fan widens dramatically after age 40, that the histogram is right-skewed indicating many paths cluster below the median, and offer a concrete suggestion like "increasing monthly contributions by even $100 reduces your worst-case (10th percentile) outcome significantly." These are pattern-level observations that vision models handle well.

**Example of a flawed AI response (Turn 1, section 2):** A model might state: *"Based on the histogram, approximately 68% of simulations reached $1 million by retirement."* If your statistics file shows the true probability is 53%, this is a fabricated number — the model estimated from visual impression rather than counting. This is the kind of specific, confident numerical claim that looks authoritative but is wrong, and is exactly what Step D asks you to analyze — the same hallucination-hunting you did against text in the core lab's citation audit, now against pixels.

##### Troubleshooting — Step B

**`KeyError: 'response'` from the API call**
The `/api/generate` endpoint returns `{"response": "..."}` for non-chat completions. The `/api/chat` endpoint returns `{"message": {"content": "..."}}`. Make sure you are using `/api/generate` in `ask_multimodal_model`, not `/api/chat`.

**Model returns an empty string or very short response**
Add `"Describe the image in detail before analyzing it."` as the first sentence of your prompt. Some vision models require an explicit grounding instruction before they will engage with the analytical questions.

**Image is too large and the request times out**
Add a resize step before encoding: `fig.savefig(buf, ...)` then `from PIL import Image; img = Image.open(buf); img = img.resize((800, 600)); ...` and re-encode. Alternatively, lower the `dpi` parameter in `fig.savefig` to `100`.

**`ollama pull llava` fails or the model is not recognized**
Try `ollama pull moondream` (smaller, faster) or `ollama pull bakllava`. Update `"model"` in `config.json` to match.

> **Checkpoint: Before moving to Step C, make sure you can answer:**
> 1. What specific percentage did the model report for simulations reaching $1 million? What does your statistics file say the true value is? Are they the same?
> 2. In Turn 2, did the model's confidence in its estimate increase, decrease, or stay the same? What does this tell you about using follow-up questioning as a verification strategy?
> 3. Look at the model's response to section 4 (simulation limitations). Did it identify any limitation that you had not already considered?

#### Step C: Parameter Sensitivity

Run your simulation under three configurations and record the results. Edit `config.json` between runs, or write a loop that overrides specific keys programmatically.

| Configuration | `annual_return_mean` | `annual_return_std` | Label |
|---------------|----------------------|----------------------|-------|
| Pessimistic | 0.04 | 0.15 | Poor market, high volatility |
| Baseline | 0.07 | 0.12 | Historical average (default) |
| Optimistic | 0.10 | 0.08 | Strong market, lower volatility |

For each configuration, record in your writeup:

- Median final balance
- Probability of reaching $1 million
- 10th percentile (worst-case) balance
- 90th percentile (best-case) balance

Then answer: which parameter change had a larger effect on the median — raising the mean return from 0.07 to 0.10, or lowering the standard deviation from 0.12 to 0.08? Use numbers from your runs, not intuition.

**To automate the three runs:**

```python
def run_sensitivity_analysis(base_cfg):
    """Run the simulation under three parameter configurations and print a comparison table."""
    scenarios = [
        {"label": "Pessimistic",  "annual_return_mean": 0.04, "annual_return_std": 0.15},
        {"label": "Baseline",     "annual_return_mean": 0.07, "annual_return_std": 0.12},
        {"label": "Optimistic",   "annual_return_mean": 0.10, "annual_return_std": 0.08},
    ]

    print(f"\n{'Scenario':<14} {'Median':>14} {'P(>$1M)':>10} {'10th pct':>14} {'90th pct':>14}")
    print("-" * 70)

    for scenario in scenarios:
        cfg = {**base_cfg, **scenario}
        np.random.seed(42)
        balances = simulate_retirement(cfg)
        final = balances[:, -1]
        print(
            f"{scenario['label']:<14} "
            f"${np.median(final):>13,.0f} "
            f"{(final >= 1_000_000).mean():>9.1%} "
            f"${np.percentile(final, 10):>13,.0f} "
            f"${np.percentile(final, 90):>13,.0f}"
        )
```

**Expected output (your numbers will vary slightly):**

```
Scenario       Median   P(>$1M)       10th pct       90th pct
----------------------------------------------------------------------
Pessimistic    $  314,042       4.2%   $   73,501   $  877,209
Baseline       $1,042,577      53.2%   $  341,208   $2,847,031
Optimistic     $2,891,044      89.7%   $1,201,330   $5,912,448
```

> **Checkpoint: Before moving to Step D, make sure you can answer:**
> 1. Between the pessimistic and baseline scenarios, the median more than tripled. What does this tell you about the compounding effect of even a moderate improvement in average returns over 40 years?
> 2. The pessimistic scenario has a higher `annual_return_std` than the baseline. How does higher volatility affect the 10th percentile differently than the median? Why?
> 3. If a user only saw the optimistic chart and made contribution decisions based on it, what harm could result?

#### Step D: Critical Analysis

This is the most important part of this direction. In Steps A–C you built a tool. Now you evaluate what happens when AI interprets that tool's output — the same audit discipline as the core lab, moved from retrieved text to a rendered chart.

##### Step D.1: Read the chart yourself first.

Before re-reading the model's responses, look at your baseline chart and note:

- Approximately what percentage of paths appear to end above $1 million (your best visual estimate)
- Where roughly the median falls
- Whether the 10th percentile line ever reaches zero during the accumulation years
- Whether the histogram distribution is symmetric, right-skewed, or left-skewed

Write down your estimates. Do not change them after reading the model's responses.

##### Step D.2: Compare to the model's Turn 1 response.

Identify **three specific differences** between what you read from the chart and what the model reported. For each difference, record:

- The exact AI output excerpt (copy-paste from `model_responses.txt`)
- Whether the AI was correct, approximately correct, or wrong
- Your best explanation for why the discrepancy occurred

At least one of your three differences must be a case where the model was **wrong or imprecise** about a number, not just phrased something differently.

##### Step D.3: Propose a prompt engineering improvement.

For the one numerical error you identified, propose a single change to the `initial_prompt` in `run_analysis_conversation` that would have reduced the chance of that error. Implement it, re-run Step B, and record whether the response improved.

Useful strategies to try:
- Adding an explicit disclaimer: *"If you cannot read a precise number from the chart, say 'approximately' and give a range."*
- Asking the model to reason step by step before stating a number: *"Before giving a percentage, describe what you see in the histogram bin by bin."*
- Restricting the scope: *"Only comment on what is visually unambiguous. Flag anything that requires precise numerical reading as uncertain."*

##### Step D.4: Address the deployment question.

Write a 2–3 sentence **guardrail statement** you would add to a financial planning tool that uses this AI chart interpretation feature. The statement should appear to the user before they see the AI's analysis, and should protect against over-reliance on numerical claims that the AI cannot read precisely.

> **Checkpoint: You have succeeded at this direction when:**
> - Your simulation produces a labeled two-panel PNG and a statistics text file
> - The multimodal model provides a four-section analysis with at least one follow-up exchange
> - You have identified at least one specific numerical error in the AI's response with an exact AI output excerpt
> - You have proposed and tested a prompt engineering change
> - Your sensitivity analysis table covers all three configurations with four statistics each

#### Step E: The Simulation as a Tool — Function-Calling Extension

In Steps A–D, the model only *interpreted* an experiment you designed. This extension inverts the relationship, bridging this direction to the **Tool Use and Function Calling** session: you wrap your simulation as a tool with a JSON schema, and the model **chooses the parameters**, asks your code to invoke the tool, and then interprets the visualization the tool produced. The model never executes anything — it can only request; your code runs the simulation and returns the results.

A fully worked, runnable version of this part (including canned offline responses for machines without Ollama) is in the [companion notebook]({{ site.baseurl }}/files/notebooks/MonteCarloRetirement.ipynb).

**Note on models:** `llava` does not support function calling. Use a tool-capable model for the parameter-selection turn (`ollama pull llama3.1`, or `qwen2.5`), and keep `llava` for the vision turn.

##### Step E.1: Wrap the simulation as a tool.

Refactor your Step A code into a single callable with an agent-friendly signature. The new `stock_allocation` parameter blends an equity-like return distribution (mean 8%, std 15%) with a bond-like one (mean 3%, std 5%), giving the agent a genuinely meaningful lever to reason about.

```python
def run_retirement_sim(years=40, annual_contribution=6000, stock_allocation=0.8,
                       n_paths=1000, seed=42):
    """
    Run a Monte Carlo retirement simulation and return summary statistics
    plus the path to a saved two-panel chart.

    stock_allocation: fraction 0.0-1.0 in stocks; the remainder in bonds.
    Blend: mean = alloc*0.08 + (1-alloc)*0.03, std = alloc*0.15 + (1-alloc)*0.05.

    Returns:
        dict with keys: median, p10, p90, mean, prob_million, years,
        annual_contribution, stock_allocation, n_paths, seed, chart_path.
    """
    # TODO: build a cfg dict from these arguments (reuse your Step A functions),
    #       call simulate_retirement and plot_simulation, and return the stats dict.
```

##### Step E.2: Write the tool's JSON schema.

The schema — not your Python code — is the tool's entire interface from the agent's point of view. Every name, description, and bound you write here shapes what parameters the model will choose.

```python
RETIREMENT_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_retirement_sim",
        "description": ("Run a Monte Carlo retirement savings simulation and return "
                        "summary statistics plus a saved two-panel chart."),
        "parameters": {
            "type": "object",
            "properties": {
                "years": {"type": "integer", "minimum": 1, "maximum": 60,
                          "description": "Years of saving before retirement."},
                "annual_contribution": {"type": "number", "minimum": 0,
                          "description": "Dollars contributed per year."},
                "stock_allocation": {"type": "number", "minimum": 0.0, "maximum": 1.0,
                          "description": "Fraction of the portfolio in stocks; higher raises both expected return and volatility."},
                "n_paths": {"type": "integer", "minimum": 100, "maximum": 10000,
                          "description": "Number of Monte Carlo paths (1000 recommended)."},
                "seed": {"type": "integer", "description": "Random seed for reproducibility."}
            },
            "required": ["years", "annual_contribution", "stock_allocation"]
        }
    }
}
```

##### Step E.3: Drive the agent loop.

Give the tool-capable model a plain-English goal plus the schema via Ollama's `/api/chat` endpoint with a `tools` array; it responds with a *tool call* — a function name and a JSON object of arguments it selected. Your code executes `run_retirement_sim` with those arguments, then sends the resulting chart to `llava` (and the exact stats dict back in the prompt) for interpretation.

```python
goal = ("I am 25 and want to know whether contributing $500 a month with a fairly "
        "aggressive portfolio gives me a good chance of retiring at 65 with over "
        "$1 million. Choose appropriate parameters, run the simulation, and "
        "interpret the results for me.")

payload = {
    "model": "llama3.1",
    "messages": [
        {"role": "system", "content": "You are a retirement planning assistant. Use the "
         "simulation tool, choosing parameters that faithfully reflect the user's situation."},
        {"role": "user", "content": goal},
    ],
    "tools": [RETIREMENT_TOOL_SCHEMA],
    "stream": False,
}
# TODO: POST to /api/chat, read message["tool_calls"][0]["function"],
#       invoke run_retirement_sim(**arguments), and save the goal, the tool call,
#       the tool result, and the interpretation to tool_call_transcript.txt.
```

##### Step E.4: Critique the agent (exercise).

The agent has now done two things a human analyst would do: chosen the experiment's inputs and narrated its output. Audit **both** against `simulation_stats.txt` and the tool's returned stats dict:

1. **Parameter choices.** The user said "$500 a month" and "retire at 65" starting at 25. Did the model's `annual_contribution` equal $500 × 12? Did `years` equal 40? Is the chosen `stock_allocation` a defensible reading of "fairly aggressive," and did the model justify it anywhere? Record each as correct, approximately correct, or wrong, quoting the tool call verbatim from `tool_call_transcript.txt`.
2. **Interpretation.** Compare the model's narrative to the tool's exact `prob_million` and to the ground truth in `simulation_stats.txt`. Does its qualitative language ("roughly three-quarters," "more likely than not") match the actual number? Quote the exact sentence and the exact statistic side by side, exactly as you did in Step D.
3. **Compounding risk.** In 2–3 sentences: when the same agent both picks the parameters and interprets the results, how can an early mistranslation (a wrong contribution, an unjustified allocation) compound into a confident but misleading recommendation — and which single check from steps 1–2 would you automate as a guardrail?

> **Checkpoint: You have completed Step E when:**
> - Your `run_retirement_sim` tool runs from a single call and returns the stats dict plus a chart path
> - The model selected parameters via a tool call (not prose), and your transcript captures the goal, the call, the tool result, and the interpretation
> - Your critique covers at least one judgment of the agent's parameter choices and one of its interpretation, each backed by a verbatim excerpt and a ground-truth number

#### Direction 2 Deliverables

Fold these into your RAG Knowledge Base Lab submission ZIP and readme:

- `montecarlo.py` — complete simulation, visualization, and multimodal analysis code
- `config.json` — your baseline configuration file
- `retirement_simulation.png` — the two-panel chart from your baseline run
- `simulation_stats.txt` — the statistics summary from your baseline run
- `model_responses.txt` — both turns of the AI conversation from your baseline run
- `sensitivity_results.txt` or equivalent — the three-scenario comparison table
- `tool_call_transcript.txt` — the Step E tool-calling transcript: the user goal, the model's tool call (name and arguments), the tool's returned statistics, and the model's interpretation
- Step E critique (in the readme) — the agent's parameter choices and its interpretation each audited against `simulation_stats.txt` and the tool's stats dict, with verbatim excerpts
- A section in your readme writeup covering: (1) sensitivity analysis with all three scenarios and four statistics each, (2) critical analysis with three AI/human comparison items including at least one AI error with verbatim excerpt, (3) the prompt engineering change you tested and whether it helped, (4) your guardrail statement for deployment
- `pair_log.txt` — driver/navigator swap log with timestamps and roles

#### What proficient work looks like (Direction 2)

- The simulation is configurable via a JSON config file; the visualization includes the median, 10th and 90th percentile bands, and the final-balance histogram, with a text summary of key statistics saved alongside the image, and edge cases are handled.
- The multimodal integration sends a valid base64-encoded PNG in the `images` array to `/api/generate`, parses the response from `response.json()["response"]`, runs a structured Turn 1 (role, four numbered sections, audience) plus a Turn 2 that presses a specific quantitative claim, and saves both turns.
- The comparative analysis names three specific AI-versus-human differences, with at least one showing a wrong or imprecise number backed by a verbatim AI excerpt alongside the true value from `simulation_stats.txt`, tests one prompt-engineering change and reports whether it helped, and (if the tool-calling extension is attempted) audits both the agent's parameter choices and its interpretation.
- The writeup tabulates the four statistics for all three sensitivity scenarios, states which parameter change moved the median more, judges AI interpretation quality with a verbatim excerpt, and delivers a 2–3 sentence plain-language user-facing guardrail.

#### Direction 2 Reflection Prompts

1. What does the spread of simulation paths tell you that a single projected number (like "you will have $800,000 at retirement") does not? Point to a specific visual feature of your chart that would disappear if you replaced the simulation with a single-path projection.
2. The AI reported a specific probability from the histogram. How would you verify whether it was right? What tools would you need, and what does this verification challenge tell you about using AI for quantitative analysis of charts?
3. In the core lab you audited citations against text; here you audited a number against a chart. What was harder to verify — a text citation or a number read from an image — and why?
4. In Step C, the pessimistic and optimistic scenarios produced dramatically different outcomes despite both using "reasonable" parameters. What does this imply about how a financial planning tool should present parameter uncertainty to a non-expert user?
5. If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
6. Approximately how many hours did this direction take?

</details>
