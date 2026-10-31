---
layout: textbook
permalink: /Tutorials/OfflineRAGFineTuning
title: "CS357: Foundations of Artificial Intelligence - Offline RAG and LoRA, End to End: Build, Reopen, Fine-Tune, and Compare on Your Own Machine"
info:
  coursenum: CS357
  purpose: "To build a retrieval-augmented system and a LoRA adapter that both run with the network unplugged, and to compare a base model, RAG, LoRA, and the two together on held-out questions, so that the difference between giving a model evidence and changing its weights is something you have measured rather than something you were told."
  eyebrow: "Tutorial"
  numbering: false
tags:
- rag
- fine-tuning
- lora
- offline
- ollama
- chroma
---

## About This Tutorial

The [RAG deck]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-rag.md) built retrieval in memory and measured it, and its self-paced fine-tuning extension explained LoRA on paper.  This tutorial does both for real, on one machine, with no network after setup.  You will index a small handbook into a vector store that survives a restart, answer questions with citations or an honest abstention, put the same retrieval behind a [Pydantic AI]({{ site.baseurl }}/Tutorials/PydanticAI) agent, train a LoRA adapter on a CPU, reload it in a fresh process, and compare four systems on questions none of them trained on.
{: .tb-lede}

Two sentences carry the whole tutorial.  **RAG changes what the model reads; it never changes the model.**  **LoRA changes the model; the change only exists while the adapter is loaded or merged.**  Everything below is a way of watching those two sentences hold, and of watching neither one make a small model truthful.

| You will need | CPU track (everything here) | Suitable-hardware track (optional) |
|---|---|---|
| Disk | about 6.5 GB: 1.6 GB Python packages (CPU PyTorch is 0.8 GB), 4.2 GB of Ollama models, 0.7 GB for the SmolLM2-360M base, plus 1.5 GB if you merge | add 2 to 10 GB per larger base model |
| Memory | 8 GB RAM minimum; training peaked at 3.8 GB and inference at 2.5 GB | a GPU with at least 8 GB of VRAM for 0.5B to 3B models; QLoRA needs NVIDIA CUDA |
| Time, measured on a 4-core CPU with no GPU | indexing seconds; one RAG answer 5 to 45 s; LoRA training about 95 s (4 epochs, 21 examples); the four-way comparison about 2 minutes | depends on the model and GPU |
{: .tb-full}

---

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|---|---|---|
| **Prompt-only generation** | The model answers from its weights alone | Section F, the `base` condition |
| **RAG** | Retrieval-augmented generation: retrieve passages, put them in the prompt, then generate.  The weights never change. | Sections B and C |
| **Embedding model** | A model that turns text into a vector for searching.  It never writes the answer. | `nomic-embed-text` |
| **Generator** | The model that writes the answer | `llama3.2`, `qwen2.5:3b`, SmolLM2 |
| **Fine-tuning** | Continuing training so the weights change | Section D |
| **LoRA** | Low-Rank Adaptation: freeze the base weights and train two small matrices per layer; the update is $$W + \frac{\alpha}{r}BA$$ | Section D |
| **QLoRA** | Quantized LoRA: LoRA on a base model loaded in 4-bit precision, to fit larger models in less GPU memory.  The adapter itself is still trained in higher precision. | Section E |
| **Adapter** | The saved LoRA matrices, a few megabytes, useless without the exact base model they were trained on | `adapters/makerspace-format/` |
| **Merge** | Adding the adapter into a copy of the base weights, producing a full-size model with no adapter | Section D |
| **Online stage / offline stage** | Downloading everything once, then running with the network unavailable | Section A |
{: .tb-full}

---

## Section A: An Honest Offline Setup

"Offline" means two separate stages, and mixing them up is the most common way an "offline" system quietly phones home.

### Stage 1, online, once

Make a project folder and run these with the network available:

```bash
mkdir offline-rag && cd offline-rag
python -m venv .venv && source .venv/bin/activate
pip install "chromadb==1.5.9" "ollama==0.6.3" "requests" \
            "pydantic-ai-slim[openai,mcp]==2.54.0" \
            "transformers==5.19.0" "peft==0.21.2" "accelerate==1.15.0"
pip install "torch==2.14.1" --index-url https://download.pytorch.org/whl/cpu   # CPU build; skip on a GPU machine

ollama pull nomic-embed-text      # embeddings, 274 MB, Apache-2.0
ollama pull llama3.2              # generator, 2.0 GB, Llama 3.2 Community License
ollama pull qwen2.5:3b            # tool-calling generator for Section C, 1.9 GB, Qwen Research License (check its terms before any commercial use)

export HF_HOME="$PWD/hf_home"     # keep the Hugging Face cache inside the project
python - <<'EOF'
from huggingface_hub import snapshot_download
snapshot_download("HuggingFaceTB/SmolLM2-360M-Instruct",           # Apache-2.0
                  revision="a10cc1512eabd3dde888204e902eca88bddb4951")
EOF
```

The `revision` is a commit hash, so a later update to the model on the Hub cannot change what you trained on.  Read each model's license on its model page before you use it outside class: Apache-2.0 for SmolLM2 and `nomic-embed-text`, the Llama 3.2 Community License for `llama3.2`, and the Qwen Research License for `qwen2.5:3b`.

### Stage 2, offline, every time after

```bash
export HF_HOME="$PWD/hf_home" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OLLAMA_NO_CLOUD=1           # set before `ollama serve`; disables Ollama's cloud features
```

`HF_HUB_OFFLINE=1` makes every Hugging Face call read the local cache or fail; the scripts also pass `local_files_only=True`, so they cannot download even if you forget the variable.  Chroma is opened with `anonymized_telemetry=False`.  When we tested Ollama 0.40 without `OLLAMA_NO_CLOUD=1`, its log showed it trying to reach `ollama.com` for model recommendations; with the variable set, those attempts stopped.

Nothing downloads silently in this stage.  A missing asset fails with a message that names it.  For example, asking for a model that was never cached:

```text
OSError: We couldn't connect to 'https://huggingface.co' to load the files, and couldn't find them in the cached files.
```

### Configuration and a preflight check

All settings live in `config.json`, so changing a model or a path never means editing code:

```json
{
  "ollama_url": "http://localhost:11434",
  "embed_model": "nomic-embed-text",
  "chat_model": "llama3.2",
  "chroma_path": "./chroma_db",
  "collection": "makerspace",
  "corpus_dir": "./corpus",
  "chunk_chars": 400,
  "top_k": 3,
  "max_distance": 0.55,
  "log_level": "INFO"
}
```

`preflight.py` checks the pinned packages, that Ollama is answering on `localhost`, and that both models are present.  It never downloads anything; it tells you what to fetch during the online stage.

```python
# preflight.py: check every local asset before the offline stage. It never downloads anything.
import importlib.metadata as md
import sys

import requests

from rag_common import CFG

PINNED = {"chromadb": "1.5.9", "ollama": "0.6.3", "pydantic-ai-slim": "2.54.0"}
problems = []

for pkg, want in PINNED.items():
    try:
        have = md.version(pkg)
        if have != want:
            problems.append(f"{pkg} is {have}, the tutorial was tested with {want}")
    except md.PackageNotFoundError:
        problems.append(f"{pkg} is not installed; install it during the online stage")

try:
    tags = requests.get(f"{CFG['ollama_url']}/api/tags", timeout=5).json()
    have = {m["name"].split(":")[0] for m in tags["models"]} | {m["name"] for m in tags["models"]}
    for model in (CFG["embed_model"], CFG["chat_model"]):
        if model not in have:
            problems.append(f"Ollama has no {model}; run `ollama pull {model}` during the online stage")
except Exception as e:
    problems.append(f"cannot reach Ollama at {CFG['ollama_url']} ({type(e).__name__}); start `ollama serve`")

if problems:
    print("PREFLIGHT FAILED:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("preflight ok: packages pinned, Ollama local, both models present")
```

### How we verified "offline"

We ran the whole offline stage inside a Linux network namespace with no external interface (`unshare -rn`), so `localhost` worked and nothing else did.  Inside it, `curl https://huggingface.co` failed to resolve, and preflight, indexing, retrieval, generation, the Pydantic AI agent, and the LoRA reload all succeeded, as did an MCP (Model Context Protocol) tool call from Part 8 of the Pydantic AI tutorial.  On your own machine, the honest equivalent is to turn off Wi-Fi and unplug the cable, then run the steps again.  Google Colab is not an offline fallback: it is someone else's computer on the internet.

---

## Section B: Local RAG, From Files to a Cited Answer

### The corpus

Four short Markdown files describe the invented Skippack Creek Makerspace.  Every fact in them is synthetic, so you can share, change, and test against them freely.  Never build a tutorial corpus, or a training set, from student records or private notes.

```text
corpus/
  hours.md        open hours, key fobs, guests
  equipment.md    laser cutter training and materials, 3D printer filament and reservations
  membership.md   prices, pausing, orientation
  safety.md       glasses, shoes, injury reports, first aid
```

Here is `corpus/equipment.md`, the file Section F changes:

```markdown
# Equipment

The laser cutter requires a 90-minute safety training before first use. Training is offered on Wednesdays at 6pm.

The laser cutter may cut wood, acrylic, cardboard, and leather. It must never cut PVC or vinyl, because they release chlorine gas.

The 3D printers use PLA and PETG filament. Members bring their own filament or buy it at the front desk for $0.05 per gram.

Each member may reserve a 3D printer for at most four hours per day.
```

The other three files are just as short.  Save them beside it so that your runs match the ones below.  The distances you see may still differ slightly in the second or third decimal place.  `corpus/hours.md`:

```markdown
# Hours and Access

The Skippack Creek Makerspace is open Monday through Friday from 10am to 9pm, and Saturday from 9am to 5pm. It is closed on Sundays.

Members enter with a key fob. A lost key fob costs $15 to replace at the front desk.

A member may sign in at most two guests at a time, and guests must stay with the member.
```

`corpus/membership.md`:

```markdown
# Membership

A standard membership costs $45 per month. Students with a current ID pay $20 per month.

A member may pause a membership for up to three months per year at no charge.

Every new member takes an orientation tour, which covers the fire exits, the first aid kits, and the tool sign-out sheet.
```

`corpus/safety.md`:

```markdown
# Safety

Safety glasses are required in the wood shop at all times. Closed-toe shoes are required in every shop area.

Report every injury, however small, to the front desk on the day it happens.

The first aid kit hangs in the hallway outside the wood shop.
```

### One shared module

The embedding function is named explicitly, in one place.  A collection must be queried with the same embedding model that built it, so the model's name is also stored in the collection's metadata.  The store lives on disk at `./chroma_db`.

```python
# rag_common.py: configuration, the embedding function, and the persistent store, in one place.
import json
import logging
import traceback
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

CFG = json.loads(Path("config.json").read_text())
logging.basicConfig(level=CFG["log_level"], format="%(levelname)s %(message)s")
log = logging.getLogger("rag")
logging.getLogger("httpx").setLevel(logging.WARNING)


def open_collection():
    """Open (or create) the on-disk collection, with the embedding model named explicitly."""
    try:
        client = chromadb.PersistentClient(path=CFG["chroma_path"],
                                           settings=Settings(anonymized_telemetry=False))
        embed = OllamaEmbeddingFunction(url=CFG["ollama_url"], model_name=CFG["embed_model"])
        return client.get_or_create_collection(
            CFG["collection"], embedding_function=embed,
            metadata={"hnsw:space": "cosine", "embed_model": CFG["embed_model"]})
    except Exception as e:
        print(f"[rag_common:open_collection] {e}")
        traceback.print_exc()
        raise
```

### Ingest: chunk, label, embed, store, and rerun safely

```python
# ingest.py: load, chunk, embed, and store. Safe to rerun: same text, same ID, no duplicates.
import hashlib
import sys
import traceback
from pathlib import Path

from rag_common import CFG, log, open_collection


def chunks(text: str, size: int):
    """Paragraph chunks, merged until they reach about `size` characters."""
    out, buf = [], ""
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        if buf and len(buf) + len(para) > size:
            out.append(buf)
            buf = ""
        buf = f"{buf}\n\n{para}".strip()
    if buf:
        out.append(buf)
    return out


def ingest():
    col = open_collection()
    for path in sorted(Path(CFG["corpus_dir"]).glob("*.md")):
        doc = path.stem
        pieces = chunks(path.read_text(), CFG["chunk_chars"])
        ids = [f"{doc}-{i}" for i in range(len(pieces))]                 # stable source IDs
        hashes = [hashlib.sha256(p.encode()).hexdigest()[:12] for p in pieces]

        existing = col.get(where={"source": doc}, include=["metadatas"])
        old = dict(zip(existing["ids"], (m["sha"] for m in existing["metadatas"])))
        stale = [i for i in old if i not in ids]
        if stale:
            col.delete(ids=stale)                                         # the document got shorter
        changed = [k for k, (i, h) in enumerate(zip(ids, hashes)) if old.get(i) != h]
        if changed:
            col.upsert(ids=[ids[k] for k in changed],
                       documents=[pieces[k] for k in changed],
                       metadatas=[{"source": doc, "chunk": k, "sha": hashes[k], "path": path.name}
                                  for k in changed])
        log.info("%s: %d chunks, %d embedded, %d unchanged, %d removed",
                 doc, len(ids), len(changed), len(ids) - len(changed), len(stale))
    print(f"collection {CFG['collection']!r} now holds {col.count()} chunks")


if __name__ == "__main__":
    try:
        ingest()
    except Exception as e:
        print(f"[ingest:main] {e}")
        traceback.print_exc()
        sys.exit(1)
```

Each chunk gets a **stable source ID** (`equipment-0`) and a hash of its text.  Rerunning compares hashes, so unchanged chunks are skipped and changed ones are re-embedded with `upsert`, which replaces rather than duplicates.  If a document gets shorter, its leftover chunk IDs are deleted.  The first two runs:

```text
$ python ingest.py
INFO equipment: 2 chunks, 2 embedded, 0 unchanged, 0 removed
INFO hours: 1 chunks, 1 embedded, 0 unchanged, 0 removed
INFO membership: 1 chunks, 1 embedded, 0 unchanged, 0 removed
INFO safety: 1 chunks, 1 embedded, 0 unchanged, 0 removed
collection 'makerspace' now holds 5 chunks
$ python ingest.py
INFO equipment: 2 chunks, 0 embedded, 2 unchanged, 0 removed
...
collection 'makerspace' now holds 5 chunks
```

Five chunks after two runs: no duplicates.  Close the terminal, reboot if you like, and run `ask.py` below without ingesting again; it reopens the same files on disk.  If you ever change `embed_model`, delete `chroma_db` and ingest from scratch, because vectors from two different embedding models are not comparable.

### Ask: show the evidence, then answer or abstain

```python
# ask.py: retrieve, show the evidence, then answer with citations or abstain.
import sys
import traceback

import requests

from rag_common import CFG, open_collection

PROMPT = """Answer the question using only the sources below. Cite the source ID in square
brackets after each fact, like [equipment-0]. If the sources do not contain the answer,
reply exactly: not in my documents.

Sources:
{sources}

Question: {question}"""


def retrieve(question: str):
    col = open_collection()
    hits = col.query(query_texts=[question], n_results=CFG["top_k"])   # the query is embedded too
    rows = zip(hits["ids"][0], hits["documents"][0], hits["distances"][0])
    return [(i, d, dist) for i, d, dist in rows]


def generate(question: str, evidence):
    sources = "\n\n".join(f"[{i}] {doc}" for i, doc, _ in evidence)
    r = requests.post(f"{CFG['ollama_url']}/api/chat", timeout=300, json={
        "model": CFG["chat_model"], "stream": False,
        "options": {"temperature": 0.0, "seed": 42},
        "messages": [{"role": "user", "content": PROMPT.format(sources=sources, question=question)}]})
    r.raise_for_status()
    return r.json()["message"]["content"]


def ask(question: str) -> str:
    evidence = retrieve(question)
    print("Retrieved evidence (smaller distance = closer):")
    for i, doc, dist in evidence:
        print(f"  [{i}] d={dist:.3f}  {doc[:90]!r}")
    kept = [e for e in evidence if e[2] <= CFG["max_distance"]]
    if not kept:
        return "not in my documents (nothing retrieved was close enough)"
    return generate(question, kept)


if __name__ == "__main__":
    try:
        print("\nAnswer:", ask(" ".join(sys.argv[1:]) or "When is laser cutter training?"))
    except Exception as e:
        print(f"[ask:main] {e}")
        traceback.print_exc()
        sys.exit(1)
```

The script prints the retrieved evidence **before** the model sees it, so you can always tell a retrieval failure from a generation failure.  Three runs with `llama3.2`:

```text
$ python ask.py "When is laser cutter training?"
Retrieved evidence (smaller distance = closer):
  [equipment-0] d=0.202  '# Equipment\n\nThe laser cutter requires a 90-minute safety training before first use. Train'
  [safety-0] d=0.462  '# Safety\n\nSafety glasses are required in the wood shop at all times. Closed-toe shoes are '
  [hours-0] d=0.479  '# Hours and Access\n\nThe Skippack Creek Makerspace is open Monday through Friday from 10am '

Answer: The laser cutter requires a 90-minute safety training before first use, which is offered on Wednesdays at 6pm. [equipment-0]

$ python ask.py "Can I cut PVC on the laser cutter?"
  [equipment-0] d=0.289  ...
Answer: Not in my documents.

$ python ask.py "Does the makerspace have a welding station?"
  [equipment-0] d=0.396  ...
Answer: not in my documents.
```

The first answer is right and cited.  The third is a correct abstention.  The second is the interesting one: retrieval found the right chunk at a small distance, the sentence "It must never cut PVC" was in the prompt, and the model still abstained.  **That is a generation failure, and no amount of retrieval tuning would fix it.**  Notice also that the welding question's best match (0.396) was well inside the 0.55 cutoff, so the distance threshold did not catch it; the prompt's abstention instruction did.  A distance cutoff is a coarse filter, not an abstention policy.

### Updating a fact

Edit `corpus/equipment.md` so training is on **Thursdays**, and ingest again:

```text
$ python ingest.py
INFO equipment: 2 chunks, 1 embedded, 1 unchanged, 0 removed
...
$ python ask.py "When is laser cutter training?"
Answer: The laser cutter requires a 90-minute safety training before first use, which is offered on Thursdays at 6pm. [equipment-0]
```

One chunk re-embedded, the answer changed, and no model was retrained.  That is the main practical argument for RAG over fine-tuning when facts change, and Section F tests it.

---

## Section C: The Same RAG System Through Pydantic AI

This section reuses `common.py` from the [Pydantic AI tutorial]({{ site.baseurl }}/Tutorials/PydanticAI) (put it beside these files, or keep the `sys.path` line below pointing at it).  Its default model is `qwen2.5:3b`, because Path 2 depends on tool calling and `qwen2.5:3b` calls tools far more reliably than `llama3.2`; Sections B and F keep `llama3.2` and SmolLM2, which never need to call a tool.  This section shows two designs.  **Path 1** keeps retrieval in your code, before the model is called, so it works with any model.  **Path 2** offers retrieval as a typed tool and lets the model decide when to search, which only works with a model that calls tools reliably.

```python
# rag_agent.py: the same RAG system through Pydantic AI, first explicit, then as a typed tool.
import sys
import traceback
from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, NativeOutput, RunContext, UsageLimits

sys.path.insert(0, "../pai")
from common import make_model, show_trace  # noqa: E402
from ask import retrieve  # noqa: E402


class RAGAnswer(BaseModel):
    answer: str = Field(description="One or two sentences, or 'not in my documents'")
    citations: list[str] = Field(description="Source IDs such as equipment-0 that support the answer")


@dataclass
class Evidence:
    ids: set[str]


# Path 1: retrieval happens in your code, before the model is called. No tool calling needed.
explicit = Agent(make_model(), output_type=NativeOutput(RAGAnswer), deps_type=Evidence, retries=2,
                 instructions="Answer only from the sources in the prompt. Cite their IDs. "
                              "If they do not contain the answer, answer 'not in my documents' with no citations.",
                 model_settings={"temperature": 0.0, "seed": 42})


@explicit.output_validator
def citations_were_retrieved(ctx: RunContext[Evidence], out: RAGAnswer) -> RAGAnswer:
    unknown = [c for c in out.citations if c not in ctx.deps.ids]
    if unknown:
        raise ModelRetry(f"You cited {unknown}, which were not retrieved. Cite only: {sorted(ctx.deps.ids)}")
    abstained = out.answer.lower().startswith("not in my documents")
    if abstained and out.citations:
        raise ModelRetry("An abstention cites nothing. Remove the citations or answer the question.")
    if not abstained and not out.citations:
        raise ModelRetry("An answer needs at least one citation, or say 'not in my documents'.")
    return out   # structurally sound. Whether the cited text SUPPORTS the answer is still unchecked.


def ask_explicit(question: str) -> RAGAnswer:
    evidence = retrieve(question)
    for i, doc, dist in evidence:
        print(f"  evidence [{i}] d={dist:.3f} {doc[:70]!r}")
    sources = "\n\n".join(f"[{i}] {doc}" for i, doc, _ in evidence)
    result = explicit.run_sync(f"Sources:\n{sources}\n\nQuestion: {question}",
                               deps=Evidence({i for i, _, _ in evidence}),
                               usage_limits=UsageLimits(request_limit=3))
    return result.output


# Path 2: retrieval as a tool the model decides to call. Needs a model that calls tools reliably.
@dataclass
class Library:
    seen: set[str]


tooled = Agent(make_model(), deps_type=Library,
               instructions="Call search before answering any question about the makerspace. "
                            "Answer from what search returns and cite the IDs in square brackets. "
                            "If search finds nothing relevant, say 'not in my documents'.",
               model_settings={"temperature": 0.0, "seed": 42})


@tooled.tool
def search(ctx: RunContext[Library], query: str) -> str:
    """Searches the makerspace handbook and returns the closest passages with their IDs."""
    hits = retrieve(query)
    ctx.deps.seen.update(i for i, _, _ in hits)
    return "\n\n".join(f"[{i}] {doc}" for i, doc, _ in hits)


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "Can the laser cutter cut PVC?"
    try:
        print("Path 1, explicit retrieval:")
        print(" ", ask_explicit(q))
        print("Path 2, retrieval as a tool:")
        lib = Library(seen=set())
        result = tooled.run_sync(q, deps=lib, usage_limits=UsageLimits(request_limit=4, tool_calls_limit=2))
        print(" ", result.output)
        print("  IDs the tool actually returned:", sorted(lib.seen))
        show_trace(result.all_messages())
    except Exception as e:
        print(f"[rag_agent:main] {e}")
        traceback.print_exc()
        sys.exit(1)
```

The output validator in Path 1 checks two structural rules: every cited ID was actually retrieved, and an abstention cites nothing.  What it cannot check is whether the cited text **supports** the answer.  Our test with the default `qwen2.5:3b` (`python rag_agent.py "How much does filament cost?"`) shows the gap:

```text
Path 1, explicit retrieval:
  evidence [membership-0] d=0.464 '# Membership\n\nA standard membership costs $45 per month. Students with'
  evidence [equipment-0] d=0.475 '# Equipment\n\nThe laser cutter requires a 90-minute safety training bef'
  evidence [equipment-1] d=0.542 'Each member may reserve a 3D printer for at most four hours per day.'
  answer='Members bring their own filament or buy it at the front desk for $0.05 per gram.' citations=['equipment-1']
```

The answer is correct.  The citation was retrieved, so it passes validation.  It is also wrong: the filament sentence is in `equipment-0`, and `equipment-1` is about reservations.  **A valid citation is not a supporting citation.**  Checking support takes a second step: a person, a string match against the cited chunk, or an LLM judge from the *Critique, Consensus, and the LLM Judge* session, each with its own error rate.

The two models also split on the PVC question, the one `llama3.2` got wrong in Section B:

| `"Can the laser cutter cut PVC?"` | `llama3.2` | `qwen2.5:3b` |
|---|---|---|
| Path 1 (explicit retrieval) | `not in my documents`, no citations: wrong abstention | "may not cut PVC or vinyl ...", cites `equipment-0`: correct |
| Path 2 (retrieval tool) | called `search("laser cutter PVC")`, answered correctly, no IDs in the text | called `search`, answered correctly, no IDs in the text |
{: .tb-full}

Path 2 makes the model's search visible in the trace (`[tool-call] search({"query":"laser cutter PVC"})`), bounded by `request_limit=4` and `tool_calls_limit=2`.  It also lost the citations, because nothing in a free-text answer forces them.  If your model will not call the tool at all (Part 7 of the Pydantic AI tutorial shows `llama3.2` writing a tool call as text), use Path 1.  Do not quietly switch to a hosted model to make Path 2 work; that ends the offline guarantee.

---

## Section D: LoRA on Your Own Machine

### What the adapter is supposed to learn

Fine-tuning is good at **behavior** (a format, a tone, when to refuse) and unreliable at **facts**, especially facts that change.  This adapter is trained to answer makerspace questions in one line, as `ANSWER: <answer> [source-id]`, or `ANSWER: not in my documents`.  The training data contains some handbook facts, including the old Wednesday training day, so Section F can see what memorized facts do after the handbook changes.

### The data, split three ways

```python
# lora_data.py: a small synthetic dataset, split three ways, with the test facts kept out of training.
import json
import random

SYSTEM = "You answer questions about the Skippack Creek Makerspace in one line."
FORMAT = 'Reply as "ANSWER: <answer> [source-id]", or "ANSWER: not in my documents".'

# (question, answer, source) -- every fact below is invented for this tutorial
TRAIN_FACTS = [
    ("What days is the makerspace open?", "Monday through Saturday; it is closed on Sundays", "hours-0"),
    ("What are the weekday hours?", "10am to 9pm, Monday through Friday", "hours-0"),
    ("What are the Saturday hours?", "9am to 5pm", "hours-0"),
    ("How much does a lost key fob cost?", "$15 at the front desk", "hours-0"),
    ("How many guests can a member sign in?", "at most two at a time", "hours-0"),
    ("How much is a standard membership?", "$45 per month", "membership-0"),
    ("How much do students pay?", "$20 per month with a current ID", "membership-0"),
    ("Can I pause my membership?", "yes, for up to three months per year at no charge", "membership-0"),
    ("What does the orientation tour cover?", "fire exits, first aid kits, and the tool sign-out sheet", "membership-0"),
    ("When is laser cutter training?", "Wednesdays at 6pm", "equipment-0"),      # this fact changes later
]
UNANSWERABLE_TRAIN = ["Is there a welding station?", "Who founded the makerspace?",
                      "Is parking free?", "Do you sell soldering irons?"]

# Held out: never seen in training, so a correct answer cannot come from memorized pairs.
TEST = [
    {"q": "Can the laser cutter cut PVC?", "gold": "no", "source": "equipment-0", "kind": "answerable"},
    {"q": "How much does filament cost?", "gold": "0.05", "source": "equipment-0", "kind": "answerable"},
    {"q": "How long can I reserve a 3D printer?", "gold": "four hours", "source": "equipment-1", "kind": "answerable"},
    {"q": "Where is the first aid kit?", "gold": "hallway", "source": "safety-0", "kind": "answerable"},
    {"q": "Are safety glasses required in the wood shop?", "gold": "yes", "source": "safety-0", "kind": "answerable"},
    {"q": "Is there a sauna?", "gold": None, "source": None, "kind": "unanswerable"},
    {"q": "What is the Wi-Fi password?", "gold": None, "source": None, "kind": "unanswerable"},
    {"q": "When is laser cutter training?", "gold": "thursdays", "source": "equipment-0", "kind": "changed"},
]


def example(q, a, src):
    target = f"ANSWER: {a} [{src}]" if src else "ANSWER: not in my documents"
    return {"messages": [{"role": "system", "content": f"{SYSTEM} {FORMAT}"},
                         {"role": "user", "content": q},
                         {"role": "assistant", "content": target}]}


def build():
    # Split by fact, not by row, so a paraphrase never lands on the other side of the split.
    groups = [[example(q, a, s), example("Quick question: " + q.lower(), a, s)] for q, a, s in TRAIN_FACTS]
    groups += [[example(q, None, None)] for q in UNANSWERABLE_TRAIN]
    random.Random(42).shuffle(groups)
    val_groups, train_groups = groups[:2], groups[2:]
    train = [r for g in train_groups for r in g]
    validation = [r for g in val_groups for r in g]
    json.dump({"train": train, "validation": validation, "test": TEST}, open("lora_data.json", "w"), indent=1)
    print(f"train={len(train)} validation={len(validation)} test={len(TEST)}")
    rows = train + validation
    train_qs = {r["messages"][1]["content"].lower().removeprefix("quick question: ") for r in rows}
    leaked = [t["q"] for t in TEST if t["q"].lower() in train_qs and t["kind"] != "changed"]
    assert not leaked, f"test questions leaked into training: {leaked}"


if __name__ == "__main__":
    build()
```

```text
$ python lora_data.py
train=21 validation=3 test=8
```

The split is **by fact**, not by row.  Our first version split by row, and a paraphrase of a training question landed in validation; validation loss then fell to 0.04, which looked like success and was really memorization showing up on both sides of the split.  After grouping, validation loss tells a different story, as the training run below shows.  The eight test questions are never trained on (the assertion enforces it), with one deliberate exception: the changed-fact question, whose *old* answer is in training on purpose.

### Training

The hyperparameters live in `lora_config.json`:

```json
{
  "base_model": "HuggingFaceTB/SmolLM2-360M-Instruct",
  "revision": "a10cc1512eabd3dde888204e902eca88bddb4951",
  "adapter_dir": "./adapters/makerspace-format",
  "r": 8,
  "alpha": 16,
  "dropout": 0.05,
  "target_modules": [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj"
  ],
  "epochs": 4,
  "batch_size": 4,
  "learning_rate": 0.001,
  "max_new_tokens": 48,
  "seed": 42
}
```

```python
# train_lora.py: freeze the base model, train a small LoRA adapter, save only the adapter.
import json
import math
import os
import sys
import time
import traceback

os.environ.setdefault("HF_HUB_OFFLINE", "1")          # never download during training
import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

CFG = json.load(open("lora_config.json"))
torch.manual_seed(CFG["seed"])


def encode(tok, row):
    """Token ids for the whole chat, with labels only on the assistant's reply."""
    prompt = tok.apply_chat_template(row["messages"][:-1], tokenize=False, add_generation_prompt=True)
    full = tok.apply_chat_template(row["messages"], tokenize=False)
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    f_ids = tok(full, add_special_tokens=False)["input_ids"]
    labels = [-100] * len(p_ids) + f_ids[len(p_ids):]      # -100 = ignored by the loss
    return f_ids, labels


def batches(tok, rows, size):
    for i in range(0, len(rows), size):
        enc = [encode(tok, r) for r in rows[i:i + size]]
        width = max(len(ids) for ids, _ in enc)
        pad = tok.pad_token_id
        yield (torch.tensor([ids + [pad] * (width - len(ids)) for ids, _ in enc]),
               torch.tensor([[1] * len(ids) + [0] * (width - len(ids)) for ids, _ in enc]),
               torch.tensor([lab + [-100] * (width - len(lab)) for _, lab in enc]))


def mean_loss(model, tok, rows):
    model.eval()
    with torch.no_grad():
        losses = [model(input_ids=x, attention_mask=m, labels=y).loss.item() for x, m, y in batches(tok, rows, 4)]
    model.train()
    return sum(losses) / len(losses)


def main():
    data = json.load(open("lora_data.json"))
    tok = AutoTokenizer.from_pretrained(CFG["base_model"], revision=CFG["revision"], local_files_only=True)
    tok.pad_token = tok.pad_token or tok.eos_token
    base = AutoModelForCausalLM.from_pretrained(CFG["base_model"], revision=CFG["revision"],
                                                local_files_only=True, dtype=torch.float32)
    lora = LoraConfig(r=CFG["r"], lora_alpha=CFG["alpha"], lora_dropout=CFG["dropout"],
                      target_modules=CFG["target_modules"], task_type="CAUSAL_LM")
    model = get_peft_model(base, lora)          # base weights frozen; only A and B train
    model.print_trainable_parameters()

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=CFG["learning_rate"])
    print(f"before training: validation loss {mean_loss(model, tok, data['validation']):.3f}")
    start = time.time()
    for epoch in range(CFG["epochs"]):
        for x, m, y in batches(tok, data["train"], CFG["batch_size"]):
            loss = model(input_ids=x, attention_mask=m, labels=y).loss
            loss.backward()
            opt.step()
            opt.zero_grad()
        val = mean_loss(model, tok, data["validation"])
        print(f"epoch {epoch + 1}: train loss {loss.item():.3f}  validation loss {val:.3f}  "
              f"({time.time() - start:.0f}s)")
        if math.isnan(val):
            sys.exit("validation loss is NaN; lower the learning rate")

    model.save_pretrained(CFG["adapter_dir"])     # writes adapter_config.json + adapter weights only
    print("saved adapter to", CFG["adapter_dir"])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[train_lora:main] {e}")
        traceback.print_exc()
        sys.exit(1)
```

What each piece does:

- `local_files_only=True` and `HF_HUB_OFFLINE=1`: training cannot download anything.
- `apply_chat_template`: the tokenizer wraps each conversation in exactly the special tokens the model was instruction-tuned with.  If you skip it, the model trains on text shaped unlike anything it will see at inference time, when it answers new questions.
- `labels = [-100] * len(prompt)`: the loss counts only the assistant's reply, so the model learns to answer rather than to repeat questions.
- `get_peft_model` freezes all 362 million base weights and adds rank-8 matrices to the four attention projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`) in every layer.  `lora_alpha=16` scales the update by $$\alpha/r = 2$$, and `lora_dropout=0.05` drops a few adapter inputs during training to reduce overfitting.

```text
$ python train_lora.py
trainable params: 1,638,400 || all params: 363,459,520 || trainable%: 0.4508
before training: validation loss 2.988
epoch 1: train loss 0.327  validation loss 2.599  (27s)
epoch 2: train loss 0.020  validation loss 2.214  (50s)
epoch 3: train loss 0.014  validation loss 2.063  (72s)
epoch 4: train loss 0.003  validation loss 2.060  (94s)
saved adapter to ./adapters/makerspace-format
```

Fewer than half a percent of the weights trained.  Training loss fell to almost nothing while validation loss, on facts the adapter never saw, only fell from 2.99 to 2.06.  When we let it run to eight epochs, validation loss rose again (2.43, 2.48, 2.47, 2.57) while training loss kept falling: textbook overfitting, which is why the config stops at four.  Twenty-one examples can teach a format.  They cannot teach a handbook.

The saved folder holds `adapter_config.json` and `adapter_model.safetensors`, 6.4 MB in all.  It does not contain the base model.  PEFT (Hugging Face's Parameter-Efficient Fine-Tuning library) prints a warning when saving offline ("Could not find a config file ... will assume that the vocabulary was not modified"); it is harmless here, because we did not add tokens.

### Reloading in a fresh process

Training an adapter and loading one are different jobs.  Anyone with the same base model revision can load your adapter without training anything:

```python
# infer_lora.py: a fresh process loads the base model, attaches the saved adapter, and compares.
import json
import os
import sys
import traceback

os.environ.setdefault("HF_HUB_OFFLINE", "1")
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from lora_data import FORMAT, SYSTEM

CFG = json.load(open("lora_config.json"))


def load(with_adapter=True):
    tok = AutoTokenizer.from_pretrained(CFG["base_model"], revision=CFG["revision"], local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(CFG["base_model"], revision=CFG["revision"],
                                                 local_files_only=True, dtype=torch.float32)
    if with_adapter:
        model = PeftModel.from_pretrained(model, CFG["adapter_dir"])   # the adapter must be loaded to matter
    return tok, model.eval()


def generate(tok, model, question, context=""):
    user = f"Sources:\n{context}\n\nQuestion: {question}" if context else question
    msgs = [{"role": "system", "content": f"{SYSTEM} {FORMAT}"}, {"role": "user", "content": user}]
    ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=CFG["max_new_tokens"], do_sample=False,
                             pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()


if __name__ == "__main__":
    try:
        tok, model = load()
        for q in ["What are the Saturday hours?", "Is there a sauna?"]:
            print(f"Q: {q}")
            print(f"  adapter on : {generate(tok, model, q)}")
            with model.disable_adapter():                              # same weights, adapter bypassed
                print(f"  adapter off: {generate(tok, model, q)}")
    except Exception as e:
        print(f"[infer_lora:main] {e}")
        traceback.print_exc()
        sys.exit(1)
```

```text
$ python infer_lora.py
Q: What are the Saturday hours?
  adapter on : ANSWER: 9am to 5pm [hours-0]
  adapter off: Saturday hours: 10:00 AM - 6:00 PM
Q: Is there a sauna?
  adapter on : ANSWER: not in my documents
  adapter off: ANSWER: not in my documents
```

Same process, same base weights in memory, different answers.  With the adapter bypassed, the base model invented Saturday hours.  With it active, the model used the format and recalled a fact that was in its training data.  The sauna question shows the other half: the base model already abstains on some questions, so an abstention after training is not, by itself, evidence that training worked.

### Merging, and why Ollama is a separate step

```python
# merge_lora.py: fold the adapter into a copy of the base weights, and check nothing changed.
import json
import os
import sys
import traceback

os.environ.setdefault("HF_HUB_OFFLINE", "1")
from infer_lora import CFG, generate, load

OUT = "./merged/makerspace-360m"

try:
    tok, model = load(with_adapter=True)
    q = "What are the Saturday hours?"
    before = generate(tok, model, q)
    merged = model.merge_and_unload()          # W <- W + (alpha/r) * B @ A, then drop the adapter
    after = generate(tok, merged, q)
    print("adapter attached:", before)
    print("merged weights  :", after)
    merged.save_pretrained(OUT)
    tok.save_pretrained(OUT)
    size = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)) / 1e6
    print(f"saved a full {size:.0f} MB model to {OUT} (the adapter alone was a few MB)")
except Exception as e:
    print(f"[merge_lora:main] {e}")
    traceback.print_exc()
    sys.exit(1)
```

```text
adapter attached: ANSWER: 9am to 5pm [hours-0]
merged weights  : ANSWER: 9am to 5pm [hours-0]
saved a full 1451 MB model to ./merged/makerspace-360m (the adapter alone was a few MB)
```

Merging computes $$W + \frac{\alpha}{r}BA$$ once and saves an ordinary model: the same answers, no PEFT needed at inference, and 1.45 GB instead of 6.4 MB.  You cannot point Ollama at either folder and expect it to work.  Ollama runs GGUF files (the single-file model format used by llama.cpp), and importing a fine-tuned model means converting it to GGUF with llama.cpp's tools for that architecture, or using Ollama's own adapter import, which supports only some base architectures and requires the adapter to match the base exactly ([Ollama: importing a model](https://docs.ollama.com/import)).  Unsloth's [Fine-tune Llama 3 and Use in Ollama](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/tutorial-how-to-finetune-llama-3-and-use-in-ollama) guide walks through that export for a supported Llama base.  Until you have converted and tested a PEFT adapter, treat it as something only Hugging Face Transformers can load.

---

## Section E: Hardware Tracks

**CPU track, which is everything above.**  A laptop with 8 GB of RAM can run all of Sections A to D and F.  Our measurements came from 4 CPU cores and 15 GB of RAM with no GPU: training peaked at 3.8 GB of RAM, inference at 2.5 GB, and four epochs took about 95 seconds.  The smaller `HuggingFaceTB/SmolLM2-135M-Instruct` (revision `12fd25f77366fa6b3b4b768ec3050bf629380bac`, Apache-2.0, 260 MB) trains several times faster if your machine is slower; expect worse answers.

**Suitable-hardware track.**  Useful LoRA training on a 0.5B to 3B instruction model (for example `Qwen/Qwen2.5-0.5B-Instruct` or `Qwen2.5-1.5B-Instruct`, Apache-2.0) wants a GPU with at least 8 GB of VRAM and a few hundred to a few thousand examples.  QLoRA loads the base in 4-bit through `bitsandbytes`, which needs an NVIDIA GPU with CUDA; it cuts the memory for the base weights to roughly a quarter, while the adapter still trains in 16-bit.  We did not test this track for this tutorial, so treat its numbers as starting points, and see the [PEFT LoRA guide](https://huggingface.co/docs/peft/main/en/developer_guides/lora).

**What not to expect.**  A mini PC or a laptop CPU will not produce a useful fine-tune of a 7B or 8B model in an afternoon.  If you have no suitable hardware, the honest options are the tiny CPU demonstration above, or **loading** an adapter someone else trained for the exact base revision you have (the lab's "provided adapter" path).  Loading is not training: it shows what an adapter does, not that you can make one.  And a hosted notebook such as Colab is a perfectly good place to train, but it is a cloud service, so it is never the offline fallback.

---

## Section F: Comparing No Adaptation, RAG, LoRA, and Both

### The design

Every condition uses one base model (SmolLM2-360M-Instruct at the pinned revision), one prompt template, greedy decoding (always choosing the single most likely next token), and `max_new_tokens=48`.  The only things that change are whether retrieved sources are in the prompt and whether the adapter is active:

| Condition | Sources in prompt | Adapter |
|---|---|---|
| `base` | no | off |
| `base+RAG` | top 3 from Chroma | off |
| `LoRA` | no | on |
| `LoRA+RAG` | top 3 from Chroma | on |

The eight held-out questions cover five **answerable** facts not in the training data, two **unanswerable** questions, and one **changed** fact: the handbook now says Thursdays, while the adapter was trained on Wednesdays.  Run it after the Thursday edit and re-ingest from Section B.

```python
# compare.py: one base model, four conditions, the same held-out questions and decoding settings.
import json
import re
import os
import resource
import sys
import time
import traceback

os.environ.setdefault("HF_HUB_OFFLINE", "1")
from ask import retrieve
from infer_lora import generate, load

DATA = json.load(open("lora_data.json"))["test"]


def score(case, reply, retrieved_ids):
    text = reply.lower()
    abstained = "not in my documents" in text
    cited = [c for c in retrieved_ids if f"[{c}]" in reply]
    row = {"format_ok": reply.startswith("ANSWER:"), "abstained": abstained,
           "recall@3": None if case["source"] is None else case["source"] in retrieved_ids}
    if case["kind"] == "unanswerable":
        row["correct"] = abstained
        row["citation_ok"] = None
    else:
        row["correct"] = bool(re.search(rf"\b{re.escape(case['gold'])}\b", text)) and not abstained
        row["citation_ok"] = bool(cited) and case["source"] in cited   # cites the chunk that holds the fact
    return row


def run(condition, tok, model):
    rows, start = [], time.time()
    for case in DATA:
        evidence = retrieve(case["q"]) if "RAG" in condition else []
        context = "\n".join(f"[{i}] {d}" for i, d, _ in evidence)
        if "LoRA" in condition:
            reply = generate(tok, model, case["q"], context)
        else:
            with model.disable_adapter():
                reply = generate(tok, model, case["q"], context)
        rows.append({"q": case["q"], "kind": case["kind"], "reply": reply,
                     **score(case, reply, [i for i, _, _ in evidence])})
    return rows, time.time() - start


def main():
    tok, model = load(with_adapter=True)
    report = {}
    for condition in ["base", "base+RAG", "LoRA", "LoRA+RAG"]:
        rows, seconds = run(condition, tok, model)
        report[condition] = rows
        n = len(rows)
        ok = lambda k: sum(1 for r in rows if r[k]) 
        cites = [r["citation_ok"] for r in rows if r["citation_ok"] is not None]
        print(f"{condition:9s} correct {ok('correct')}/{n}  format {ok('format_ok')}/{n}  "
              f"cited-right {sum(cites)}/{len(cites)}  {seconds:.0f}s")
    json.dump(report, open("compare_report.json", "w"), indent=1)
    print("peak RSS MB", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[compare:main] {e}")
        traceback.print_exc()
        sys.exit(1)
```

### Our results

We measured these on the CPU track with the four-epoch adapter, and every answer here comes from SmolLM2-360M (`llama3.2` plays no part):

| Condition | Answerable correct (of 5) | Unanswerable, abstained (of 2) | Changed fact (Thursdays) | `ANSWER:` format (of 8) | Cites the chunk that holds the fact (of 6) | Retrieval recall@3 (of 6) | Time for 8 questions |
|---|---|---|---|---|---|---|---|
| `base` | 0 | 1 | no: "the 15th of each month" | 7 | 0 | n/a | 12 s |
| `base+RAG` | 2 | 0 | **yes**: "Thursdays at 6pm" | 7 | 0 | 6 | 27 s |
| `LoRA` | 0 | 2 | no: "Monday at 7pm" | 8 | 0 | n/a | 16 s |
| `LoRA+RAG` | 4 | 0 | no: "Monday through Friday at 6pm; Saturday at 9pm" | 8 | 0 | 6 | 37 s |
{: .tb-full}

Peak memory was 2.5 GB.  Retrieval recall@3 counts a question as found when the chunk holding its answer is among the 3 chunks retrieved.  Retrieval found the right chunk for every answerable and changed question, so every miss in the RAG rows is a generation miss.

### What the numbers do and do not show

Read the replies in `compare_report.json`, not just the totals.  Scoring here is a crude whole-word match against a short gold answer, so read every row the scorer marked before you trust a count.

- **The adapter learned the format.**  Every `LoRA` and `LoRA+RAG` reply started with `ANSWER:`.  That is the behavior the training data actually taught.
- **The adapter did not learn the handbook.**  Without retrieval, the `LoRA` condition answered held-out questions with confident, well-formatted inventions: "$0.00 per foot [wires-0]" for filament, citing a source that does not exist, and "30 days at no charge" for a printer reservation.  With retrieval, it cited real chunks but swapped them: the filament answer cited `equipment-1` and the reservation answer cited `equipment-0`, the reverse of where those facts are.  Format is not truth, and a fine-tuned citation format makes a wrong answer look more trustworthy.
- **The changed fact.**  Only the system that read the new handbook could know about Thursday, and only `base+RAG` said it.  The adapter had been trained on "Wednesdays at 6pm," yet the `LoRA` condition answered "Monday at 7pm": it did not even recall its own training fact reliably.  In an earlier run trained for eight epochs, the adapter did reproduce "Wednesdays at 6pm," and it kept saying Wednesday even with the Thursday chunk in its prompt.  Updating a fact in RAG took one re-ingest; updating it in an adapter takes new data and new training, and the old fact can keep winning.
- **Neither guarantees factuality.**  With the right sources in the prompt, the 360M model still said the laser cutter "may cut PVC," and both RAG conditions answered "yes" to the sauna question instead of abstaining.  The adapter-only condition abstained on both unanswerable questions, but it also abstained on three answerable ones, so its abstentions say more about caution than about knowledge.
- **Resource use.**  Adding RAG roughly doubled the time per question (embedding the query, plus a longer prompt).  Training cost about 95 seconds once; inference with an adapter attached costs almost nothing extra.

Eight questions on one small model are a demonstration, not an evaluation.  Before claiming that any condition is better, use a golden set written before any tuning, as in *RAG: Building and Measuring a Knowledge Base* and the *RAG Worked Example*: more questions, several seeds or models, and the same scoring for every condition.

---

## Exercises

1.  *Break retrieval on purpose.*
   - *What to do*: Set `chunk_chars` to 80, delete `chroma_db`, re-ingest, and rerun Section B's three questions.
   - *Starter hint*: Look at the evidence lines before the answers.
   - *You've succeeded when*: you can point to one answer that changed because of retrieval, not generation.

2.  *Check support, not just validity.*
   - *What to do*: Add a check to `rag_agent.py` that each cited chunk contains at least one content word of the answer.
   - *Starter hint*: Fetch the cited chunk's text with `open_collection().get(ids=[...])`.
   - *You've succeeded when*: the filament answer above is flagged, and you can name one correct answer your check would wrongly flag.

3.  *Train for the setting you use.*
   - *What to do*: Add training examples whose user message includes a `Sources:` block, and retrain.
   - *Starter hint*: Use only training facts in those sources, so the test stays held out.
   - *You've succeeded when*: you have rerun `compare.py` and can say whether `LoRA+RAG` changed, with the replies to back it up.

4.  *Measure overfitting.*
   - *What to do*: Set `epochs` to 8 and record validation loss after each epoch.
   - *Starter hint*: Compare against the four-epoch numbers above.
   - *You've succeeded when*: you can say which epoch you would stop at, and why training loss alone could not tell you.

---

## Reflection

*Personal*: Before this tutorial, which would you have reached for first to make a model "know" your course handbook, fine-tuning or RAG?  Did the comparison change that?

*Technical*: Name one task where you would choose LoRA over RAG, and the measurement that would convince you it was the right call.

*Societal*: A fine-tuned model that cites sources in the right format looks trustworthy even when the source does not exist.  Who is harmed when a format is mistaken for evidence, and whose job is it to check?

---

## Where This Goes Next

The [RAG Knowledge Base lab]({{ site.baseurl }}/Assignments/RAGKnowledgeBase) asks you to index your own corpus and query it through a Pydantic AI agent with a retrieval tool.  This tutorial goes further, into a persistent offline index and the full LoRA route, for when you want more than the lab asks.  The fine-tuning extension of the [RAG deck]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-rag.md) has the ladder of prompting, RAG, and fine-tuning that these measurements illustrate.

## Further Reading

- Chroma: [clients and persistence](https://docs.trychroma.com/docs/run-chroma/clients), [embedding functions](https://docs.trychroma.com/docs/embeddings/embedding-functions), [Ollama embeddings](https://docs.trychroma.com/integrations/embedding-models/ollama), [updating data](https://docs.trychroma.com/docs/collections/update-data)
- Hugging Face: [PEFT LoRA guide](https://huggingface.co/docs/peft/main/en/developer_guides/lora), [Hub environment variables, including offline mode](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables), [SmolLM2-360M-Instruct model card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct)
- Ollama: [importing models and adapters](https://docs.ollama.com/import), [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility)
- Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models," 2021, [arXiv:2106.09685](https://arxiv.org/abs/2106.09685); Dettmers et al., "QLoRA: Efficient Finetuning of Quantized LLMs," 2023, [arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
