---
layout: textbook
permalink: /Tutorials/RAGFromZero
title: 'CS357: Foundations of Artificial Intelligence - RAG From Zero: Chunk, Embed, Retrieve, Ground, and Measure'
info:
  coursenum: CS357
  purpose: "To practice retrieval-augmented generation one step at a time on a small corpus, measure it with a golden set written before indexing, see what retrieval changes by switching it off, and then try the same pipeline on a corpus you choose."
  eyebrow: "Tutorial"
  numbering: false
tags:
- rag
- retrieval
- evaluation
- chroma
- langflow
---

{% include mathjax.html %}

## About This Tutorial

Retrieval-augmented generation (RAG) has five moving parts: cut documents into chunks, turn each chunk into an embedding, retrieve the chunks closest to a question, ground the answer in what was retrieved, and measure whether any of it worked.  This tutorial builds each part on its own, prints what it produces, and then measures the whole pipeline.  You can do it on its own, before or after the [RAG Knowledge Base lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RAGKnowledgeBase), and nothing here is collected or graded.
{: .tb-lede}

Part I is the core.  It runs on any machine with Python 3 and no extra packages, because two pieces are labeled stand-ins: a word-count "embedding" and a sentence-copying "model."  Part II replaces both with the real ones on the code path (Chroma and a Pydantic AI agent, as in the lab), and Part III does the same on the no-code path (a Langflow flow).  **You need only one of Parts II and III;** doing both is optional.  Part IV points the pipeline at a corpus you choose.  Every part uses the same measurement: a golden set, recall@k, a grounding check, and a question asked with retrieval switched off.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|---|---|---|
| **Chunk** | A piece of a document that is stored and searched on its own.  Here, one paragraph. | Cell 2, twelve chunks with IDs like `membership-1` |
| **Embedding** | A list of numbers that places text with similar meaning close together, so a search can match meaning rather than exact words | Cell 3 (a word-count stand-in); Chroma's embedding model in Part II; `nomic-embed-text` in Part III |
| **Retrieve (top $$k$$)** | Embed the question and return the $$k$$ closest chunks, best first, each labeled with its source file | Cell 3, `search_notes` |
| **Grounded answer** | An answer whose claims all appear in a retrieved passage from the file it names | Cells 4 and 5 |
| **Abstention** | Saying "I could not find that in your notes" when the passages do not hold the answer | The last golden question |
| **Golden set** | A fixed list of questions, each with the phrase only the right passage contains and the fact a right answer states, written before you index anything | Cell 1 |
| **Recall@k** | The share of answerable golden questions whose evidence appears somewhere in the top $$k$$ chunks.  It measures the retriever, not the answer. | Cell 5 |
| **Retrieval off** | The same question, model, and rules with no passages supplied, so you can see what retrieval changed | Cell 4, `measure.py`, and step 6 of Part III |
{: .tb-full}

---

# Part I: The Whole Pipeline in Plain Python

These five cells use only the Python standard library.  Paste them in order into one file, such as `rag_zero.py`, and run `python3 rag_zero.py`, or paste them one at a time into a Python session.  Each cell uses what the cells above it built.  The corpus and the stand-ins come from the *RAG Worked Example* session, so if you did that session, the numbers will look familiar.

## 1.  Write the Golden Set First

The corpus is four short files about an invented bicycle co-op.  Before any code indexes them, we write the test: six questions, each with an **evidence phrase** that only the right passage contains and the fact a right answer must state.  One question has no answer in the notes, so the test can tell whether the system knows when to stop.  We name evidence by phrase rather than by chunk ID because chunk IDs change when the chunking changes, and a phrase does not.

```python
# Cell 1: the corpus, and the golden set written before anything is indexed.
CORPUS = {   # four invented files about a bicycle co-op; every fact in them is synthetic
    "hours.md": """# Hours

The co-op workshop is open Tuesday and Thursday from 4pm to 8pm, and Saturday from 10am to 2pm.

The workshop is closed on college holidays. Volunteers post closures on the front door.""",
    "membership.md": """# Membership

A semester membership costs $15 and includes unlimited stand time. Students with a college ID pay $10.

Every member completes a 30-minute orientation before using a repair stand.""",
    "tools.md": """# Tools

Truing stands and wheel tools stay in the workshop. Members may borrow a pump or a tire lever overnight for a $5 deposit.

The parts washer uses citrus degreaser only. Never pour solvent into the parts washer.""",
    "safety.md": """# Safety

Safety glasses are required whenever anyone is cutting a cable or a chain.

Report any injury to the shift volunteer, who records it in the incident binder before the shift ends.""",
}

GOLDEN = [   # (question, a phrase only the right passage contains, the fact a right answer states)
    ("How much does a membership cost for a student?", "pay $10",               "$10"),
    ("When is the workshop open on Saturday?",          "Saturday from 10am",    "10am to 2pm"),
    ("Can I take a pump home overnight?",                "borrow a pump",         "$5"),
    ("What do I need before using a repair stand?",     "30-minute orientation", "orientation"),
    ("Who do I tell if I get hurt?",                     "Report any injury",     "shift volunteer"),
    ("Does the co-op sell new bikes?",                   None,                    None),
]
print(f"{len(CORPUS)} files, {len(GOLDEN)} golden questions, "
      f"{sum(1 for _, ev, _ in GOLDEN if ev is None)} the notes cannot answer")
```

You should see `4 files, 6 golden questions, 1 the notes cannot answer`.  Notice that the questions use different words from the notes ("hurt" against "injury," "take home" against "borrow").  That is on purpose: real users do not phrase questions the way the documents are written.

## 2.  Chunk

The lab's `index.py` splits each file on blank lines, so one paragraph becomes one chunk, with the ID `{file stem}-{paragraph number}` and the file name kept beside the text.  This cell does the same, then checks that each evidence phrase lands in exactly one chunk.

```python
# Cell 2: chunk the way the lab's index.py does, one chunk per blank-line paragraph.
def paragraph_chunks(corpus):
    rows = []
    for name in sorted(corpus):
        paragraphs = [p.strip() for p in corpus[name].split("\n\n") if p.strip()]
        for i, p in enumerate(paragraphs):
            rows.append({"id": f"{name.rsplit('.', 1)[0]}-{i}", "source": name, "text": p})
    return rows

chunks = paragraph_chunks(CORPUS)
print(f"Indexed {len(chunks)} chunks from {len(CORPUS)} files.")
for c in chunks[:4]:
    print(f"  {c['id']:<13} {c['text'][:55]!r}")
for question, evidence, fact in GOLDEN:   # each evidence phrase should be in exactly one chunk
    if evidence:
        print(f"  {evidence!r:<24} is in {[c['id'] for c in chunks if evidence in c['text']]}")
```

You should see:

```text
Indexed 12 chunks from 4 files.
  hours-0       '# Hours'
  hours-1       'The co-op workshop is open Tuesday and Thursday from 4p'
  hours-2       'The workshop is closed on college holidays. Volunteers '
  membership-0  '# Membership'
  'pay $10'                is in ['membership-1']
  'Saturday from 10am'     is in ['hours-1']
  'borrow a pump'          is in ['tools-1']
  '30-minute orientation'  is in ['membership-2']
  'Report any injury'      is in ['safety-2']
```

Each heading on its own line became a chunk of its own: `hours-0` is just `# Hours`.

## 3.  Embed and Retrieve

On your machine, Chroma embeds each chunk when you store it and embeds the question when you search.  Here, `toy_embed` stands in for that: it counts the words left after dropping common ones, and `cosine` compares two of those counts (1.0 for the same words in the same proportions, 0.0 for no shared words).  A real embedding model handles different wording far better than word counts do, and Cell 5 shows where the stand-in fails because of it.

```python
# Cell 3: a stand-in embedding, cosine similarity, and a top-k search.
import math
import re

STOP = {"a", "an", "the", "to", "on", "of", "is", "are", "and", "or", "for", "from", "with",
        "in", "it", "do", "does", "i", "my", "can", "what", "when", "how", "who", "before",
        "any", "anyone", "every", "much", "may", "must", "whenever", "only", "stay"}

def toy_embed(text):
    """A word-count stand-in for a real embedding: same text in, same vector out."""
    words = [w for w in re.findall(r"[a-z0-9$-]+", text.lower()) if w not in STOP]
    words = [w[:-1] if len(w) > 4 and w.endswith("s") and not w.endswith("ss") else w
             for w in words]          # a crude plural rule: "costs" and "cost" match
    vec = {}
    for w in words:
        vec[w] = vec.get(w, 0) + 1
    return vec

def cosine(u, v):
    dot = sum(u[w] * v.get(w, 0) for w in u)
    nu = math.sqrt(sum(x * x for x in u.values()))
    nv = math.sqrt(sum(x * x for x in v.values()))
    return dot / (nu * nv) if nu and nv else 0.0

def build_index(rows):
    return [dict(row, vec=toy_embed(row["text"])) for row in rows]

def search_notes(index, query, k=3):
    """The k closest chunks to the query, best first, as (id, score, row)."""
    q = toy_embed(query)
    ranked = sorted(index, key=lambda row: (-cosine(q, row["vec"]), row["id"]))
    return [(row["id"], round(cosine(q, row["vec"]), 3), row) for row in ranked[:k]]

index = build_index(chunks)
question = "When is the workshop open on Saturday?"
print("Q:", question, "->", toy_embed(question))
for cid, score, row in search_notes(index, question):
    print(f"  {cid:<13} {score:.3f}  [{row['source']}] {row['text'][:45]!r}")
```

You should see:

```text
Q: When is the workshop open on Saturday? -> {'workshop': 1, 'open': 1, 'saturday': 1}
  hours-1       0.548  [hours.md] 'The co-op workshop is open Tuesday and Thursd'
  hours-2       0.192  [hours.md] 'The workshop is closed on college holidays. V'
  tools-1       0.160  [tools.md] 'Truing stands and wheel tools stay in the wor'
```

The right chunk is first.  The other two share only the word "workshop," and they were returned anyway: a search always returns $$k$$ chunks, whether or not they are relevant.

## 4.  Ground the Answer, With Retrieval Off and On

The prompt below is the lab's grounding prompt, word for word: answer only from the passages, name the file for each fact, and abstain with a fixed sentence when the passages do not hold the answer.  The prompt is the whole of what the model sees, so the cell prints it.  `ask` can switch retrieval off, which sends the same rules and question with no passages.

```python
# Cell 4: the grounding prompt, a stand-in model, and the same question with retrieval off and on.
PROMPT = """Answer questions about the user's notes, using ONLY the passages below.
Name the source file for each fact.
If the passages do not contain the answer, say: I could not find that in your notes.

Passages:
{context}

Question: {question}"""

def build_prompt(question, hits):
    context = "\n\n".join(f"[{row['source']}] {row['text']}" for _, _, row in hits)
    return PROMPT.format(context=context, question=question)

def stand_in_model(question, hits, min_score=0.2):
    """Not a language model: it copies the best-matching sentence of the top passage and
    names its file, or abstains.  It can only copy, so with no passages it must abstain."""
    if not hits or hits[0][1] < min_score:
        return "I could not find that in your notes."
    q = toy_embed(question)
    best_row = hits[0][2]
    sentences = re.split(r"(?<=[.!?])\s+", best_row["text"])
    sentence = max(sentences, key=lambda s: cosine(q, toy_embed(s)))
    return f"{sentence} [{best_row['source']}]"

def ask(question, retrieval=True, k=3):
    hits = search_notes(index, question, k) if retrieval else []
    return build_prompt(question, hits), stand_in_model(question, hits)

question, evidence, _ = GOLDEN[1]
for retrieval in (False, True):
    prompt, answer = ask(question, retrieval)
    print(f"=== retrieval {'on' if retrieval else 'off'}: {len(prompt)} characters, "
          f"evidence in prompt: {evidence in prompt} ===")
    print(prompt)
    print("ANSWER:", answer, "\n")
```

You should see the retrieval-off prompt (254 characters, `evidence in prompt: False`, an empty `Passages:` section) answered with `I could not find that in your notes.`, then the retrieval-on prompt (594 characters, `evidence in prompt: True`) answered with:

```text
ANSWER: The co-op workshop is open Tuesday and Thursday from 4pm to 8pm, and Saturday from 10am to 2pm. [hours.md]
```

The stand-in abstained with retrieval off because it can only copy, and there was nothing to copy.  A language model is not limited that way: with no passages it can still write an answer from what it learned in training.  That is the comparison Parts II and III run on a real model, and it is the clearest way to see what retrieval adds.

## 5.  Measure: Recall@k, Grounding, and Abstention

Three checks, each owned by a different part of the pipeline.  **Recall@k** checks the retriever: is the evidence phrase in any of the top $$k$$ chunks?

$$
\text{recall@}k = \frac{\text{answerable questions whose evidence is in the top } k}{\text{answerable questions}}
$$

**Right** checks the answer against the fact in the golden set.  **Grounded** checks that every content word of the answer appears in a retrieved passage from the file the answer names.  The unanswerable question is left out of recall, since it has no evidence to find, and gets its own verdict: did the system abstain?

```python
# Cell 5: measure the retriever (recall@k), the answer (right, grounded), and abstention.
def recall_at_k(index, k):
    """The share of answerable questions whose evidence is somewhere in the top k chunks."""
    answerable = [(q, ev) for q, ev, _ in GOLDEN if ev]
    found = [any(ev in row["text"] for _, _, row in search_notes(index, q, k)) for q, ev in answerable]
    return sum(found) / len(found)

def grounded(answer, hits):
    """Every content word of the answer appears in a retrieved passage from the file it names."""
    named = [row for _, _, row in hits if f"[{row['source']}]" in answer]
    if not named:
        return False
    claim = toy_embed(answer.split(" [")[0])
    passages = toy_embed(" ".join(row["text"] for row in named))
    return all(w in passages for w in claim)

def report(index, label):
    print(f"== {label}: {len(index)} chunks ==")
    print("  recall@1 = %.2f   recall@3 = %.2f" % (recall_at_k(index, 1), recall_at_k(index, 3)))
    for q, ev, fact in GOLDEN:
        hits = search_notes(index, q)
        answer = stand_in_model(q, hits)
        if ev is None:
            verdict = "abstained" if answer.startswith("I could not") else "ANSWERED (should abstain)"
        elif answer.startswith("I could not"):
            verdict = "abstained (should answer)"
        else:
            right = fact.lower() in answer.lower()
            verdict = ("right" if right else "WRONG") + (", grounded" if grounded(answer, hits) else ", NOT grounded")
        print(f"  {q[:46]:<46} {verdict}")

report(index, "paragraph chunks")

# Grounding checks the answer against the file it names, not against the truth.
hits = search_notes(index, GOLDEN[0][0])
for reply in ["Students with a college ID pay $10. [membership.md]",
              "Students pay $8 per semester. [membership.md]",
              "Students with a college ID pay $10. [tools.md]"]:
    print(f"  grounded={str(grounded(reply, hits)):<5}  {reply}")
```

You should see:

```text
== paragraph chunks: 12 chunks ==
  recall@1 = 0.60   recall@3 = 0.80
  How much does a membership cost for a student? WRONG, grounded
  When is the workshop open on Saturday?         right, grounded
  Can I take a pump home overnight?              right, grounded
  What do I need before using a repair stand?    right, grounded
  Who do I tell if I get hurt?                   abstained (should answer)
  Does the co-op sell new bikes?                 abstained
  grounded=True   Students with a college ID pay $10. [membership.md]
  grounded=False  Students pay $8 per semester. [membership.md]
  grounded=False  Students with a college ID pay $10. [tools.md]
```

Read it row by row.  The membership answer is grounded and wrong: the bare heading `membership-0` won rank 1 on the single word "membership," and the stand-in copied it faithfully.  The injury question is a retrieval miss, because "tell" and "hurt" share no words with "Report any injury"; a real embedding model is built to place "hurt" near "injury," so this miss belongs to the stand-in.  The three hand-written replies show what grounding catches (an invented amount, and a right fact credited to the wrong file) and why "right" and "grounded" stay separate words.

### Questions to Work Through

1.  For the membership question, which component owns the failure: the chunker, the retriever, or the generator?  Point at the line of output that tells you.
2.  **Predict:** if you fold each heading into the paragraphs under it, so no chunk is a bare heading, will recall@1 go up, down, or stay the same?  Will the membership answer become right?  Write both predictions down before you try Exercise 1.
3.  `stand_in_model` abstains when the top score is below `min_score`.  Why can a score threshold not be the whole abstention policy?  Look at the score of the top hit for "Does the co-op sell new bikes?" with `search_notes(index, "Does the co-op sell new bikes?")`.
4.  **Predict:** a real model with retrieval off is asked "When is the workshop open on Saturday?" under rules that say to name a source file.  What will it do: abstain, guess a time, or guess a time and name a file?  Write it down before Part II or Part III.

---

# Part II: The Code Path (Chroma and Pydantic AI)

> These scripts talk to Chroma on disk and to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Run them in your course container or on your own machine.
{: .tb-warning data-title="Runs on your machine, not here"}

Part II uses the lab's code, models, and versions.  Set up once:

```bash
python -m venv .venv && source .venv/bin/activate
pip install "pydantic-ai-slim[openai]==2.54.0" "chromadb==1.5.9"
ollama pull qwen2.5:3b
```

Then save the co-op corpus as a `corpus/` folder.  This cell needs nothing but Python, and Part IV reuses `load_corpus` for your own files.

```python
# Cell 6: save the co-op files as corpus/, or load your own corpus/ folder in place of CORPUS.
from pathlib import Path

def save_corpus(corpus, folder="corpus"):
    Path(folder).mkdir(exist_ok=True)
    for name, text in corpus.items():
        Path(folder, name).write_text(text + "\n", encoding="utf-8")

def load_corpus(folder="corpus"):
    files = sorted(Path(folder).glob("*.md")) + sorted(Path(folder).glob("*.txt"))
    return {p.name: p.read_text(encoding="utf-8") for p in files}

if not Path("corpus").exists():
    save_corpus(CORPUS)          # first run: write the co-op files so Parts II and III can use them
CORPUS = load_corpus()
print(sorted(CORPUS), "->", len(paragraph_chunks(CORPUS)), "chunks")
```

You should see `['hours.md', 'membership.md', 'safety.md', 'tools.md'] -> 12 chunks`, and a `corpus` folder with four files.

## 6.  Index and Ask

1.  **Chunk and embed.**  Save the lab's [`index.py`](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RAGKnowledgeBase#step-2-index-it) next to `corpus/` and run `python index.py`.  It makes the same paragraph chunks as Cell 2 and stores them in a Chroma collection named `notes`, which embeds each one with Chroma's own embedding model.  You should see `Indexed 12 chunks from 4 files.`  The first run downloads that embedding model once.
2.  **Retrieve and generate.**  Save the lab's [`rag_agent.py`](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RAGKnowledgeBase#step-3-give-an-agent-a-search-tool) and run `python rag_agent.py "When is the workshop open on Saturday?"`.  You should see a `[tool call] search_notes(...)` line, a `[tool result]` line that begins with a file name in brackets, and an answer that names a file.  The agent's instructions carry the same three rules as Cell 4's prompt, and its `search_notes` tool returns the top three passages, like `k=3` above.

## 7.  Measure, Then Switch Retrieval Off

Save this as `measure.py` beside `rag_agent.py` and run `python measure.py`.  It imports the lab's `agent`, `collection`, and `model` (the file's `__main__` guard keeps the import from asking a question), computes recall@1 and recall@3 against Chroma, asks every golden question, and then asks one question twice: once with a `closed_book` agent that has the same model and rules but no search tool, and once with the real agent.

```python
# measure.py: score the lab's index and agent on the golden set, then compare retrieval off and on.
import traceback

from pydantic_ai import Agent, UsageLimits
from rag_agent import agent, collection, model   # all three are defined at the top of rag_agent.py

GOLDEN = [   # the same golden set as Cell 1; rewrite it for your own corpus
    ("How much does a membership cost for a student?", "pay $10", "$10"),
    ("When is the workshop open on Saturday?", "Saturday from 10am", "10am to 2pm"),
    ("Can I take a pump home overnight?", "borrow a pump", "$5"),
    ("What do I need before using a repair stand?", "30-minute orientation", "orientation"),
    ("Who do I tell if I get hurt?", "Report any injury", "shift volunteer"),
    ("Does the co-op sell new bikes?", None, None),
]

closed_book = Agent(   # the same model and rules, but no search tool: retrieval off
    model,
    instructions=(
        "Answer questions about the user's notes. Name the source file for each fact. "
        "If you cannot answer from the notes, say: I could not find that in your notes."
    ),
    model_settings={"temperature": 0.0, "seed": 42},
)


def top_k(question, k):
    """The k passages Chroma returns for a question, as plain text."""
    try:
        hits = collection.query(query_texts=[question], n_results=k)
    except Exception as e:
        print("[measure:top_k]", e)
        traceback.print_exc()
        raise
    return hits["documents"][0]


def recall_at_k(k):
    answerable = [(q, ev) for q, ev, _ in GOLDEN if ev]
    return sum(any(ev in text for text in top_k(q, k)) for q, ev in answerable) / len(answerable)


def ask(which, question):
    """Run one agent once; return its answer and the search results it was given."""
    try:
        result = which.run_sync(question, usage_limits=UsageLimits(request_limit=4))
    except Exception as e:
        print("[measure:ask]", e)
        traceback.print_exc()
        raise
    returned = [str(part.content) for message in result.all_messages()
                for part in message.parts if part.part_kind == "tool-return"]
    return result.output, "\n".join(returned)


if __name__ == "__main__":
    print(f"recall@1 = {recall_at_k(1):.2f}   recall@3 = {recall_at_k(3):.2f}")
    for question, evidence, fact in GOLDEN:
        answer, returned = ask(agent, question)
        abstained = "could not find" in answer.lower()
        right = abstained if fact is None else (fact.lower() in answer.lower() and not abstained)
        print(f"\nQ: {question}\n  searched={bool(returned)}  right={right}\n  A: {answer}")
    question = GOLDEN[1][0]
    for label, which in (("OFF", closed_book), ("ON", agent)):
        answer, returned = ask(which, question)
        print(f"\nretrieval {label}  searched={bool(returned)}\n  Q: {question}\n  A: {answer}")
```

The script checks what a machine can check: recall, whether the agent searched, and whether the answer holds the right fact or abstains when it should.  It cannot check that the file an answer names actually says the claim.  That check is yours: for each answer, open the named file and write one line saying whether it supports the answer.  Exact wording depends on the model, so your answers will not match anyone else's word for word.

### Questions to Work Through

5.  Compare `recall@1` from Chroma with the 0.60 from Cell 5.  Did Chroma's embedding model find the injury passage that the stand-in missed?  Did the bare heading still cost the membership question rank 1?
6.  Check your prediction from Question 4 against the `retrieval OFF` answer.  If it named a file, does that file exist in `corpus/`?
7.  The closed-book agent has the abstention sentence in its instructions.  What does its answer tell you about whether instructions alone can make a model abstain?
{: start="5"}

---

# Part III: The No-Code Path (Langflow)

> Langflow and Ollama run on your own laptop.  Node names shift a little between Langflow versions; the dataflow is what matters.  The [Visual Agents](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/VisualAgents) tutorial walks through the canvas with more detail.
{: .tb-warning data-title="Runs on your machine, not here"}

Steps 1 to 4 follow the lab's Steps N1 to N3, using the `corpus/` folder from Cell 6.  Steps 5 and 6 add the measurement and the retrieval-off comparison.

1.  **Install and launch (lab Step N1).**  Run `pip install langflow`, then `langflow run`, then `ollama pull llama3.2` and `ollama pull nomic-embed-text`.  The canvas opens at `http://localhost:7860`.  If `pip` reports a dependency-resolver error, make a fresh virtual environment on Python 3.11 or 3.12 and install there.
2.  **Index path (lab Step N2).**  Create a **New Flow** from a **Blank Canvas**.  Wire **File** (upload the four files in `corpus/`) to **Text Splitter** (the recursive character splitter, chunk size 1000, overlap 100) to **Chroma** (collection `notes`), with an **Ollama Embeddings** node (model `nomic-embed-text`, Base URL `http://localhost:11434`) wired into Chroma's embedding input.  Read the stored chunk count in the Chroma node's inspection view.
3.  **Query path (lab Step N2).**  Wire **Chat Input** to the same Chroma node's search input, with the number of results set to 3.  Send the search results to a **Prompt** node, then to **Ollama** (model `llama3.2`, temperature 0, Base URL `http://localhost:11434`), then to **Chat Output**.
4.  **Ground (lab Step N3).**  Paste Cell 4's `PROMPT` text into the Prompt node, from `Answer questions` through `Question: {question}`.  Wire the search results into `{context}` and the Chat Input into `{question}`.
5.  **Measure.**  Ask each golden question in a fresh **Playground** session.  For each one, open the search step's inspection view and copy the three chunks it returned into a spreadsheet beside the question.  Mark 1 in a recall@3 column if the evidence phrase appears in any of the three, and average that column over the five answerable questions.  Then mark each answer right or wrong, and grounded or not, by reading the passage from the file it names.
6.  **Retrieval off.**  Disconnect the search results from the Prompt's `{context}`, so it arrives empty, and ask "When is the workshop open on Saturday?" in a fresh session.  Then reconnect it and ask again.  Write down both answers.

Record every node setting in a readme as you go (models, Base URL, chunk size, overlap, number of results, temperature, prompt text).  On this path that list takes the place of the code.

### Questions to Work Through

8.  **Predict** before you read the Chroma node's count: each co-op file is shorter than 1000 characters.  Will the splitter store twelve chunks, as Cell 2 did, or some other number?
9.  The canvas uses `nomic-embed-text` and `llama3.2`; the code path uses Chroma's default embedding model and `qwen2.5:3b`.  If your recall@3 differs from a classmate's on the other path, which differences could explain it, and how would you test one at a time?
{: start="8"}

---

# Part IV: Try It on a Corpus You Choose

The co-op corpus is small and invented so that you can check every answer.  The next step is a corpus you know well enough to check by hand: your own course notes, the documentation for a tool you use, a club's handbook, or the public pages of an organization you care about.  Your team's project material is one option, if your partner agreed to share it and you leave out personal details about anyone you interviewed.  Do not index anything you would not want stored in a file on disk, such as passwords, health records, or other people's messages.

1.  Put five to twenty `.md` or `.txt` files in a fresh `corpus/` folder.
2.  **Before you index anything,** rewrite `GOLDEN` in Cell 1: four questions your notes answer (worded differently from the notes), one they do not answer, and one you expect to be hard.  Pick evidence phrases of three to five words.
3.  In Cell 1, replace the `CORPUS = {...}` dictionary with `CORPUS = load_corpus()`, and paste `from pathlib import Path` and the `load_corpus` function from Cell 6 above that line.  Run Part I again.  Cell 2's evidence check should show exactly one chunk for each phrase; if a phrase is in two chunks, or none, choose a different phrase now, before you look at any answers.
4.  Run the same golden set on your path: `measure.py` with your `GOLDEN` (delete `chroma_db` and rerun `index.py` first), or the Langflow spreadsheet with your files uploaded.

Part I's stand-in will do worse on your corpus than a real embedding model, because it can only match exact words.  That is fine: Part I tells you whether your golden set is well formed, and Part II or III tells you how the real pipeline does.

---

## Exercises

Everything below is optional.  Each one ends with a check you apply yourself.

1.  **Fold the headings in.**

    *What to do:* Write `heading_chunks(corpus)`, which remembers each heading line instead of storing it, and prefixes it to every paragraph below it (`"Membership: A semester membership costs..."`).  Run `report(build_index(heading_chunks(CORPUS)), "headings folded")` with the same golden set.

    *Starter hint:* Loop over the paragraphs as `paragraph_chunks` does.  When a paragraph starts with `#`, save `p.lstrip("# ").strip()` and `continue`.  The *RAG Worked Example* session has a version to compare against once yours runs.

    *You've succeeded when:* you can report recall@1 before and after, check it against your prediction from Question 2, and say which component owns the membership answer now.

2.  **Tune abstention.**

    *What to do:* Rerun the stand-in on all six golden questions with `min_score` set to 0.1, 0.2, 0.3, and 0.5, and record the verdicts in a table.

    *Starter hint:* `stand_in_model(q, search_notes(index, q), min_score=m)` for each question `q` and threshold `m`.

    *You've succeeded when:* you can name the threshold where the unanswerable question first gets answered, the threshold where an answerable question first gets an abstention, and explain why no single threshold is right for every corpus.

3.  **Retrieval off on your own corpus.**

    *What to do:* Ask two of your own golden questions with retrieval off and on, on your path from Part II or III.

    *Starter hint:* On the code path, change `question = GOLDEN[1][0]` at the bottom of `measure.py`.  On the canvas, repeat step 6 of Part III.

    *You've succeeded when:* you have both answers for both questions, and one sentence on what retrieval changed and one on what it did not.

---

## Reflection Prompt

*Personal:* The golden set made you decide what a right answer was before you saw any answers.  Where in your own work do you judge results only after seeing them, and what would change if you wrote the test first?

*Technical:* The membership answer was grounded and wrong.  Design one more automatic check that would have caught it, and say what it would cost you in false alarms.

*Societal:* With retrieval off, a model may still answer confidently.  If a tool built on your corpus were used by people who cannot see whether retrieval ran, what should it show them so they can tell an answer from the notes from an answer from training?

---

## Further Reading

- [Lab: RAG Knowledge Base](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RAGKnowledgeBase), whose `index.py`, `rag_agent.py`, grounding prompt, and Langflow steps Parts II and III use.
- [RAG: Building and Measuring a Knowledge Base](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-rag.md), for parametric and contextual memory, chunking strategies, and rerankers.
- [RAG Worked Example: Build the Pipeline Together](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-ragworkshop.md), the in-class build of the same co-op corpus.
- [Offline RAG and LoRA, End to End](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OfflineRAGFineTuning), for a persistent index that is safe to rebuild, a distance cutoff, and a comparison of RAG with fine-tuning.
- [Pydantic AI From the Loop Up](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/PydanticAI), for the agent and tool calls in `rag_agent.py`, and [Visual Agents](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/VisualAgents), for the Langflow canvas.
- [Memory and the Small Context Window Principle](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/MemoryAndContext), on why fetching a few passages beats carrying everything.
- Patrick Lewis et al.  "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."  *NeurIPS* (2020).
- Chroma documentation: https://docs.trychroma.com, and Langflow documentation: https://docs.langflow.org
