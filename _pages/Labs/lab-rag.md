---
layout: assignment
permalink: Labs/RAG
title: "Lab: Retrieval Augmented Generation"
 
info:
  points: 100
  goals:
    - Explain the RAG paradigm and contrast it with pure parametric LLM generation.
    - Configure a Custom GPT in ChatGPT to perform file-based retrieval and produce transparent, source-grounded responses.
    - Implement a local, reproducible RAG pipeline in Python using Ollama or Open‑WebUI with embeddings, a vector index, and a generator model.
    - Ingest a personal corpus; perform text chunking; create embeddings; build a FAISS (or fallback) index; and implement top‑k retrieval.
    - "Empirically demonstrate tradeoffs: (a) sampling many documents vs. too few (vary top‑k and chunk size) and (b) context‑window limits with large documents."
    - Evaluate answer quality, faithfulness, and usability; document failure modes and mitigations.
    - Produce a reflective report comparing Hosted (Custom GPT) vs. Local (Ollama/Open‑WebUI) RAG from technical, ethical, and human‑centered perspectives.
  rubric:
    - weight: 20
      description: Human-Centric Design
      preemerging: Demonstrates the modality in a simple scenario with clear user affordances.
      beginning: Incorporates the modality with recognizable signifiers and mostly clear interaction flow.
      progressing: Enables smooth interaction using the modality with minor ambiguities identified via testing.
      proficient: Delivers a modality-first experience with clear signifiers and refined interaction informed by testing.
    - weight: 20
      description: Design Report
      preemerging: Summarizes the approach and how the modality fits the use case.
      beginning: Describes design choices and modality integration with rationale from one stakeholder perspective.
      progressing: Documents stakeholder-informed rationale, evaluation methods, and design revisions.
      proficient: Provides a structured report with multi-stakeholder feedback, test evidence, and justified revisions.
    - weight: 30
      description: Algorithm Implementation
      preemerging: Implements a working pipeline on provided inputs with clear control flow.
      beginning: Handles typical inputs reliably and articulates constraints and thresholds.
      progressing: Implements a robust algorithm expected to generalize beyond test inputs with justification.
      proficient: Implements and explains a robust algorithm with evidence of generalization and careful parameterization.
    - weight: 20
      description: Code Quality and Documentation
      preemerging: Provides readable structure and basic inline explanations at key points.
      beginning: Organizes modules and documents decisions that aid readability and maintenance.
      progressing: Uses clear abstractions, docstrings, and style conventions consistently.
      proficient: Demonstrates clean architecture, high-quality documentation, and consistent adherence to style guides.
    - weight: 10
      description: Writeup and Submission
      preemerging: Includes a brief README describing how to run and evaluate the program.
      beginning: Submits all required components with a README and responses to most prompts.
      progressing: Submits a complete package with README, answers, and notes on known limitations.
      proficient: Submits a fully complete package with clear instructions, answers, and validation notes.
 
tags:
  - rag
---
 
# Overview
Retrieval‑Augmented Generation (RAG) combines non‑parametric retrieval over an external corpus with parametric generation by an LLM. In this lab you will:
 
1. Configure a **Custom GPT** in ChatGPT that uses your files for retrieval and produces citation‑backed answers.
2. Build a **local RAG** with Python using **Ollama** or **Open‑WebUI** (OpenAI‑compatible API), including chunking, embeddings, a vector index, retrieval, and response synthesis.
3. Run **experiments** that (a) vary the number of sampled documents (top‑k) and (b) push the **context window** using at least one very large document to observe truncation and quality effects.
4. Submit your **configuration/code**, **chat transcripts**, and a **reflective report** on benefits/drawbacks of RAG.
 
> **Use your own corpus** (e.g., course notes, policies, papers, manuals). Avoid sensitive or restricted data.
 
---
 
# Background (Concise)
- **Why RAG?** Reduced hallucinations, up‑to‑date domain knowledge, controllability, and inspectability via citations.
- **Key knobs:** chunk size/overlap, embedding model, index (e.g., FAISS), similarity metric, top‑k, optional re‑ranker, prompt/citation style, and **context window**.
- **Typical failure modes:** missed retrieval (low recall), irrelevant chunks (low precision), shallow synthesis across too many snippets, context truncation, and weak or absent source attributions.
 
---
 
# Part A — Hosted RAG with **Custom GPT** in ChatGPT
 
## A1. Create the Custom GPT
1. In ChatGPT, go to **Explore → Create a GPT**.
2. **Name:** `RAG‑Assistant (YourName)`.
3. **Instructions** (paste into the GPT’s *system* instructions):
   ```
   You are a retrieval‑augmented assistant. Always:
   - Answer strictly based on the provided files unless explicitly asked to generalize.
   - Cite the specific file names (and sections if possible) used for each answer.
   - When unsure or when retrieval is weak, say so and propose clarifying queries.
   - Prefer concise, well‑structured answers with short quotes (≤2 sentences per quote).
   - When multiple sources disagree, summarize the disagreement and cite each source.
   ```
4. **Knowledge:** Enable **Knowledge** and **upload 10–30 documents** from your corpus, including **≥1 large document** (e.g., a 50+ page PDF).
5. **Capabilities:** Web browsing is optional (not required here).
6. **Actions:** None required.
 
## A2. Test Prompts (Sampling & Synthesis)
Run the following, saving outputs (screenshots or exports):
- “**List the top three documents** most relevant to this query; provide a one‑sentence rationale for each, then answer with citations. Query: *[your query]*”
- “**Answer and cite at least k distinct files** if relevant; if not, explain why fewer suffice.” (Run with k = 1, 3, 5).
- “**If you used more than 2 passages**, briefly summarize how you synthesized them.”
- “**When information is missing or contradictory**, show both and state uncertainty.”
 
Vary your **corpus composition** (add/remove files) and observe how breadth (number of cited files) and answer quality change.
 
## A3. Probing Context Limits (Hosted)
Ask questions that **require widely separated passages** from your long document (e.g., “Compare assumptions in Chapter 2 with results in Appendix C; cite both.”). Note whether the assistant cites both locations and whether content appears truncated or generic. Record observations.
 
## A4. Artifacts to Submit (Part A)
- The **Custom GPT instructions** you used (copy/paste).
- A short **description of the corpus** (file count, types, presence of a large doc).
- **Three transcripts or screenshots** from A2 and at least **one** from A3.
- A brief **note on observed failure modes** (e.g., missed citations, truncation).
 
---
 
# Part B — Local RAG in Python (Ollama or Open‑WebUI)
You will implement a minimal yet complete RAG stack locally:
- **Embeddings:** via Ollama’s OpenAI‑compatible `/v1/embeddings` (e.g., `nomic‑embed‑text`) **or** Hugging Face `sentence-transformers`.
- **Index:** FAISS (CPU) with cosine similarity. Provide a fallback to scikit‑learn `NearestNeighbors` if FAISS is unavailable.
- **Generator:** an LLM served by **Ollama** (e.g., `llama3.1:8b`) or proxied by **Open‑WebUI** using an OpenAI‑compatible `/v1/chat/completions` endpoint.
 
> **Model suggestions:** `nomic‑embed‑text` for embeddings; `llama3.1:8b` or similar for generation. Use what runs on your hardware.
 
## B1. Environment
Create a fresh environment and install dependencies:
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install faiss-cpu numpy pandas tiktoken pypdf tqdm openai scikit-learn sentence-transformers
```
Start **Ollama** (and pull models as needed):
```bash
# Install Ollama from https://ollama.com; then:
ollama pull llama3.1:8b
ollama pull nomic-embed-text
# (Optional) If using Open‑WebUI, start it and set its OpenAI‑compatible endpoint.
```
Set environment variables (choose one base URL):
```bash
# Ollama’s OpenAI‑compatible API
export OPENAI_API_KEY="ollama"              # any non-empty string
export OPENAI_BASE_URL="http://localhost:11434/v1"
 
# OR, Open‑WebUI’s OpenAI‑compatible API
# export OPENAI_API_KEY="local"
# export OPENAI_BASE_URL="http://localhost:3000/v1"
```
 
## B2. Project Layout
```
rag-local/
  corpus/                # put your .txt/.md/.pdf here (≥10 docs, include ≥1 large)
  rag_config.yaml        # small config (models, chunk size, top-k, budgets)
  build_index.py
  chat_rag.py
  requirements.txt
  README.md
  results/
    runs.csv             # experiment logs (top-k, tokens, citations)
```
 
## B3. Configuration (example `rag_config.yaml`)
```yaml
embedding_model: "nomic-embed-text"      # or "sentence-transformers/all-MiniLM-L6-v2"
generator_model: "llama3.1:8b"
chunk_chars: 900
chunk_overlap: 150
top_k: 5
max_context_tokens: 3500   # budget for retrieved text in the final prompt
max_output_tokens: 512
similarity: "cosine"
cite_k: 5
```
 
## B4. Index Building (`build_index.py`)
```python
"""
Builds a FAISS index from documents in ./corpus.
- Extracts text (txt/md/pdf), chunks into overlapping windows.
- Computes embeddings (Ollama/Open‑WebUI via OpenAI API OR sentence-transformers fallback).
- Persists FAISS index and metadata.
"""
from __future__ import annotations
import os, json, glob, math, uuid, pickle, pathlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
 
import numpy as np
from tqdm import tqdm
 
# Embeddings backends
USE_OPENAI_COMPAT = bool(os.getenv("OPENAI_BASE_URL"))
 
if USE_OPENAI_COMPAT:
    from openai import OpenAI
    client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY", "ollama"))
else:
    from sentence_transformers import SentenceTransformer
    sbert = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
 
# Optional FAISS; fallback to sklearn if unavailable
try:
    import faiss  # type: ignore
    HAVE_FAISS = True
except Exception:
    from sklearn.neighbors import NearestNeighbors
    HAVE_FAISS = False
 
try:
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
except Exception:
    enc = None
 
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None
 
@dataclass
class Chunk:
    doc_id: str
    chunk_id: int
    text: str
    source: str
    start_char: int
    end_char: int
 
def read_text(path: str) -> str:
    ext = pathlib.Path(path).suffix.lower()
    if ext in {".txt", ".md"}:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    if ext == ".pdf" and PdfReader:
        out = []
        pdf = PdfReader(path)
        for p in pdf.pages:
            try:
                out.append(p.extract_text() or "")
            except Exception:
                out.append("")
        return "\n".join(out)
    return ""
 
def chunk_text(text: str, chunk_chars=900, overlap=150) -> List[Tuple[int, int, str]]:
    spans = []
    i = 0
    n = len(text)
    while i < n:
        j = min(i + chunk_chars, n)
        spans.append((i, j, text[i:j]))
        i = j - overlap
        if i < 0: i = 0
    return spans
 
def embed_texts(texts: List[str], model_name: str) -> np.ndarray:
    if USE_OPENAI_COMPAT:
        # OpenAI-compatible embeddings (Ollama / Open‑WebUI)
        vecs = []
        for t in texts:
            emb = client.embeddings.create(input=t, model=model_name)
            vecs.append(np.array(emb.data[0].embedding, dtype=np.float32))
        return np.vstack(vecs)
    else:
        # Sentence-Transformers fallback (CPU-friendly)
        emb = sbert.encode(texts, convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True)
        return emb.astype(np.float32)
 
def l2_normalize(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
    return x / n
 
def main():
    import yaml
    cfg = yaml.safe_load(open("rag_config.yaml"))
    emb_model = cfg.get("embedding_model", "nomic-embed-text")
    chunk_chars = cfg.get("chunk_chars", 900)
    overlap = cfg.get("chunk_overlap", 150)
 
    files = sorted(glob.glob("corpus/*"))
    all_chunks: List[Chunk] = []
    for f in files:
        text = read_text(f)
        spans = chunk_text(text, chunk_chars, overlap)
        doc_id = str(uuid.uuid4())
        for k, (a, b, t) in enumerate(spans):
            if t.strip():
                all_chunks.append(Chunk(doc_id, k, t, os.path.basename(f), a, b))
 
    texts = [c.text for c in all_chunks]
    X = embed_texts(texts, emb_model)
    X = l2_normalize(X)
 
    meta = [asdict(c) for c in all_chunks]
 
    if HAVE_FAISS:
        dim = X.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(X)
        faiss.write_index(index, "results/index.faiss")
        np.save("results/embeddings.npy", X)
    else:
        # Fallback: serialize raw vectors and use sklearn in query code
        np.save("results/embeddings.npy", X)
 
    with open("results/meta.pkl", "wb") as f:
        pickle.dump(meta, f)
 
    print(f"Indexed {len(all_chunks)} chunks from {len(files)} files.")
 
if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    main()
```
 
## B5. Retrieval + Chat (`chat_rag.py`)
```python
"""
Simple RAG chat over a FAISS (or sklearn) index with budgeted context.
- Vary top_k to study sampling.
- Enforce a max_context_tokens budget to demonstrate truncation.
- Print citations with (source, chunk_id, char_span).
"""
from __future__ import annotations
import os, pickle, math, json
from typing import List, Dict, Any, Tuple
 
import numpy as np
from tqdm import tqdm
 
USE_OPENAI_COMPAT = bool(os.getenv("OPENAI_BASE_URL"))
from openai import OpenAI
client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY", "ollama"))
 
# Optional FAISS; fallback to sklearn
try:
    import faiss  # type: ignore
    HAVE_FAISS = True
    index = faiss.read_index("results/index.faiss")
except Exception:
    HAVE_FAISS = False
    index = None
    from sklearn.neighbors import NearestNeighbors
    X = np.load("results/embeddings.npy")
    nn = NearestNeighbors(n_neighbors=50, metric="cosine").fit(X)
 
try:
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
except Exception:
    enc = None
 
def token_len(s: str) -> int:
    if enc is None:
        return max(1, len(s) // 4)  # crude fallback
    return len(enc.encode(s))
 
def embed_query(q: str, model_name="nomic-embed-text") -> np.ndarray:
    e = client.embeddings.create(input=q, model=model_name)
    return np.array(e.data[0].embedding, dtype=np.float32)
 
def retrieve(q: str, top_k: int, emb_model: str, meta: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    qv = embed_query(q, emb_model).astype(np.float32)
    qv = qv / (np.linalg.norm(qv) + 1e-12)
    if HAVE_FAISS:
        D, I = index.search(qv.reshape(1, -1), top_k)
        idxs = I[0].tolist()
        scores = D[0].tolist()
    else:
        dists, idxs = nn.kneighbors(qv.reshape(1, -1), n_neighbors=top_k, return_distance=True)
        scores = [1 - d for d in dists[0].tolist()]  # convert to similarity
 
    out = []
    for i, s in zip(idxs, scores):
        c = dict(meta[i])
        c["score"] = float(s)
        out.append(c)
    return out
 
def build_prompt(user_q: str, contexts: List[Dict[str, Any]], max_ctx_tokens: int) -> Tuple[str, List[Dict[str, Any]]]:
    header = (
        "You are a retrieval‑augmented assistant. Use ONLY the context to answer. "
        "Cite sources like [source:chunk_id:start-end]. If insufficient, say so.\n\n"
    )
    blocks, used = [], []
    budget = max_ctx_tokens - token_len(header) - token_len(user_q) - 100  # reserve space
    for c in contexts:
        tag = f"[{c['source']}:{c['chunk_id']}:{c['start_char']}-{c['end_char']}]"
        block = f"{tag}\n{c['text']}\n"
        if token_len(block) <= budget:
            blocks.append(block)
            used.append(c)
            budget -= token_len(block)
        else:
            # stop adding; budget exceeded
            break
    prompt = header + "\n".join(blocks) + "\nUser question: " + user_q
    return prompt, used
 
def chat_once(user_q: str, *, emb_model="nomic-embed-text", gen_model="llama3.1:8b",
              top_k=5, max_context_tokens=3500, max_output_tokens=512) -> Dict[str, Any]:
    meta = pickle.load(open("results/meta.pkl", "rb"))
    contexts = retrieve(user_q, top_k, emb_model, meta)
    prompt, used = build_prompt(user_q, contexts, max_context_tokens)
 
    resp = client.chat.completions.create(
        model=gen_model,
        messages=[{"role":"user", "content": prompt}],
        temperature=0.2,
        max_tokens=max_output_tokens
    )
    answer = resp.choices[0].message.content
    out = {
        "query": user_q,
        "top_k": top_k,
        "ctx_candidates": len(contexts),
        "ctx_used": len(used),
        "tokens_prompt_est": token_len(prompt),
        "answer": answer,
        "citations": [(c["source"], c["chunk_id"], c["start_char"], c["end_char"]) for c in used]
    }
    print(json.dumps(out, indent=2)[:2000])
    return out
 
if __name__ == "__main__":
    import yaml, csv, time
    cfg = yaml.safe_load(open("rag_config.yaml"))
    runs = []
    user_q = input("Enter your query: ").strip()
    for k in [1, 3, 5, 10]:
        r = chat_once(
            user_q,
            emb_model=cfg.get("embedding_model", "nomic-embed-text"),
            gen_model=cfg.get("generator_model", "llama3.1:8b"),
            top_k=k,
            max_context_tokens=cfg.get("max_context_tokens", 3500),
            max_output_tokens=cfg.get("max_output_tokens", 512),
        )
        r["time"] = time.time()
        runs.append(r)
    os.makedirs("results", exist_ok=True)
    with open("results/runs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=runs[0].keys())
        w.writeheader(); w.writerows(runs)
    print("Wrote results/runs.csv")
```
 
## B6. Experiments
1. **Sampling (top‑k):** For a demanding query that logically spans multiple files, run `chat_rag.py` with `k ∈ {1,3,5,10}`. Compare:
   - number of contexts **used** vs. **candidate**,
   - prompt token estimate,
   - distinct sources cited,
   - qualitative answer quality.
2. **Context window limits:** Include a **very large document** in `corpus/`. Re‑run with `top_k=10` and a small `max_context_tokens` (e.g., 1200), then larger (e.g., 3500). Observe **which chunks are dropped** and whether the answer quality degrades or becomes generic.
3. **Chunk size sensitivity (optional):** Rebuild the index with different `chunk_chars` (e.g., 400 vs. 900 vs. 1500). Discuss recall vs. precision tradeoffs.
 
Record findings (tables or bullet points). You may include simple quantitative proxies (e.g., number of cited sources, coverage of gold passages if available).
 
## B7. Artifacts to Submit (Part B)
- `rag_config.yaml`, `build_index.py`, `chat_rag.py`, and any helper modules.
- A **README** with environment setup and run instructions, including your base URL and models.
- `results/runs.csv` plus short notes/screenshots illustrating truncation effects.
- **Chat transcripts** (or excerpts) for at least two different queries.
 
---
 
# Deliverables (All Parts)
1. **Part A (Hosted/Custom GPT)**
   - GPT **instructions** you used.
   - **Corpus description** and rationale (including one large document).
   - **Transcripts/screenshots** demonstrating sampling and context‑limit behavior.
2. **Part B (Local RAG)**
   - Code + config; `results/runs.csv` summarizing experiments.
   - Two or more **chat transcripts** with citations.
3. **Reflective Report (≈2–4 pages)**
   - **Benefits & drawbacks** of RAG compared to pure parametric generation.
   - **Hosted vs. Local**: setup effort, latency, quality, privacy, controllability, transparency.
   - **Human‑centered considerations**: affordances (what the user sees), uncertainty language, citation presentation, accessibility, and failure‑mode mitigations.
   - **Empirical observations**: when increasing top‑k helped/hurt; when context limits forced truncation; which chunk sizes worked best and why.
   - **Ethics & data governance**: provenance, licensing, private data risks, and auditing.
 
---
 
# Grading & Logistics
- Follow the rubric in the front matter. Your submission should make it straightforward to verify your experiments.
- **Reproducibility:** include exact model names/versions, base URL, OS, and hardware (CPU/GPU, RAM).
- **Academic integrity:** attribute third‑party libraries, and cite any external sources in your report.
- **Accessibility:** if you include figures, provide alt‑text or captions that summarize key points.
 
Good luck, and have fun exploring grounded, human‑centered RAG! 
