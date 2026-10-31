<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-ragworkshop.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-ragworkshop.md

import: https://raw.githubusercontent.com/LiaTemplates/Pyodide/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# RAG Worked Example: Build the Pipeline Together

*RAG: Building and Measuring a Knowledge Base* gave you the pieces: the open-book insight, a pipeline in fifty lines, chunking, and recall@k.  Today we put them together and build one small, complete knowledge base end to end, in the order the [RAG Knowledge Base lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RAGKnowledgeBase) asks for it: **ingest → chunk → embed → retrieve → generate → measure**.  Every step prints its intermediate output, so you can see exactly what the next step receives.  The first half runs in this page.  Part II runs the same corpus through the lab's own code on your machine (or, on the no-code route, through the lab's Langflow flow) and measures both the same way.  In class we check that one route works, and you finish Part II on your own.  The last twenty minutes are a clinic for your Final Project Proposal.

The corpus is four short files about an invented bicycle co-op.  Every fact in them is synthetic, so you can change and test against them freely.  The measurement at the end is the habit the lab's Step 4 depends on: a golden set written before you tune anything, recall@k for the retriever, and a grounding check for the answer.

**Today:** the [Tools and MCP lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/ToolsMCP) and your team's Intra-Team Check-In (Norming into Performing) are due, and I hand out the [RAG Knowledge Base lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RAGKnowledgeBase) (due Thursday, November 12) and the [Literature Review](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/LitReview).  For the lab's corpus, you may use your team's stakeholder material (interview notes, your partner's public documents, your evidence folder), so that the lab also moves your project forward.  If you do, use only material your partner agreed to share, and leave out personal details about the people you interviewed.  Your team's [Final Project Proposal](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/FinalProjectProposal) is due Thursday.

---

## Directions and Group Roles

Work in your POGIL (Process Oriented Guided Inquiry Learning) team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  This is a build-along session.  One laptop per team runs the cells in this page.  In Part II, one laptop runs the same corpus on the lab's route and compares its answer with Part I's.  The Manager calls each checkpoint and asks for a prediction before the cell runs.  The Recorder keeps the team's golden set and the two results tables.  The Presenter reports the one number that changed most between the two chunkings.  The Reflector notes every place where the stand-in in this page and the real model on the machine disagreed.  In the Proposal Clinic, the Manager keeps time for the twenty minutes and takes the card's lines in order.  The Recorder writes the card and adds it to your decision log.  The Presenter brings line 2 to me, and the Reflector checks line 4 against your charter's meeting cadence.  After class, answer the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Where You See It Today |
|---|---|---|
| **Ingest** | Read the documents you chose into the program, each with its file name, so every later step can say where a passage came from | Step 1, the `CORPUS` of four files |
| **Chunk** | A piece of a document stored and searched on its own.  The lab's `index.py` makes one chunk per paragraph | Step 2, twelve chunks with stable IDs like `membership-1` |
| **Embedding** | A list of numbers that places text with similar meaning close together, so a search can match meaning rather than exact words | Step 3; a word-count stand-in in this page, Chroma's embedding model on your machine |
| **Retrieve** | Embed the question and return the $k$ closest chunks, best first, each labeled with its source file | Step 4, `search_notes` |
| **Grounded answer** | An answer whose every claim appears in a retrieved passage from the file it names, or an abstention when the passages do not contain the answer | Step 5 and the `grounded` check in Step 6 |
| **Golden set** | A small, fixed set of questions with the passage each should find and the fact a right answer states, written before any tuning | Step 6, six questions including one the notes cannot answer |
| **Recall@k** | The share of answerable golden questions whose evidence appears somewhere in the top $k$ retrieved chunks | Step 6, 0.60 at $k=1$ before the fix, 0.80 after |

---

### Before You Start

**Have ready:** the lab's code-route setup from its *Before You Start* section (a virtual environment with `pydantic-ai-slim[openai]==2.54.0` and `chromadb==1.5.9`, and `ollama pull qwen2.5:3b`), or, for the no-code route, Langflow with `llama3.2` and `nomic-embed-text` pulled.  Part I needs nothing; its cells run in this page.  Part II needs one of the two routes on one laptop per team.

**Run the cells in order.**  Each cell uses what the cell before it built.  If a cell reports a `NameError`, run the cells above it first.

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.

| Minutes | What we do |
|---|---|
| 0-5 | The corpus, and the golden set written before anything runs |
| 5-15 | Part I, Steps 1 and 2: ingest and chunk (Checkpoint 1) |
| 15-25 | Part I, Steps 3 and 4: embed and retrieve (Checkpoint 2) |
| 25-33 | Part I, Step 5: the grounded prompt and the answer (Checkpoint 3) |
| 33-48 | Part I, Step 6: measure recall@k and grounding, then fix the chunking and measure again (Checkpoint 4) |
| 48-53 | Part II, the same corpus on your machine: one laptop per team confirms that the lab's code route or Langflow flow answers one golden-set question (Checkpoint 5).  The rest of Part II is self-paced lab work |
| 53-73 | Proposal Clinic: one card per team, four lines |
| 73-75 | The lab handout, and what to have ready for Thursday |

Part III, the exercise on a golden set for your own lab corpus, is self-paced.

---
# Part I: The Whole Pipeline, One Step at a Time

The cells in this Part run in the page, so nothing here needs Ollama.  Two pieces are stand-ins, and both are labeled: a word-count "embedding" in Step 3, and a sentence-copying "model" in Step 5.  They keep every intermediate value small enough to read.  Part II replaces both with the real ones from the lab and runs the same measurement.

## The Corpus and the Golden Set

Write the test before you build the thing it tests.  Here are the six questions the pipeline must handle, written against the four files below before any code runs.  Each answerable question names a phrase that only the right passage contains, and the fact a right answer must state.  Writing the evidence as a phrase rather than as a chunk ID matters: when you change the chunking later today, chunk IDs change, and a phrase does not.

| Question | Evidence phrase (only the right passage has it) | A right answer states |
|---|---|---|
| How much does a membership cost for a student? | `pay $10` | $10 |
| When is the workshop open on Saturday? | `Saturday from 10am` | 10am to 2pm |
| Can I take a pump home overnight? | `borrow a pump` | $5 |
| What do I need before using a repair stand? | `30-minute orientation` | orientation |
| Who do I tell if I get hurt? | `Report any injury` | shift volunteer |
| Does the co-op sell new bikes? | none: the notes do not say | an abstention |

The last row is the lab's "one question your notes do not answer."  A golden set without one cannot tell you whether the system knows when to stop.

## Step 1 and Step 2: Ingest and Chunk

**Goal:** every file read in with its name, and split into chunks with stable IDs, exactly as the lab's `index.py` does it: one chunk per paragraph, separated by blank lines, with the ID `{file stem}-{paragraph number}` and the file name kept beside the text.

```python
# Steps 1 and 2: ingest a small corpus and chunk it the way the lab's index.py does.
CORPUS = {   # four invented files; every fact in them is synthetic
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

def paragraph_chunks(corpus):
    """The lab's index.py rule: one chunk per blank-line-separated paragraph."""
    rows = []
    for name in sorted(corpus):
        paragraphs = [p.strip() for p in corpus[name].split("\n\n") if p.strip()]
        for i, p in enumerate(paragraphs):
            rows.append({"id": f"{name.rsplit('.', 1)[0]}-{i}", "source": name, "text": p})
    return rows

chunks = paragraph_chunks(CORPUS)
print(f"Indexed {len(chunks)} chunks from {len(CORPUS)} files.")
for c in chunks:
    print(f"  {c['id']:<13} {c['source']:<14} {c['text'][:55]!r}")
```
@Pyodide.eval

**You should see:**

```text
Indexed 12 chunks from 4 files.
  hours-0       hours.md       '# Hours'
  hours-1       hours.md       'The co-op workshop is open Tuesday and Thursday from 4p'
  hours-2       hours.md       'The workshop is closed on college holidays. Volunteers '
  membership-0  membership.md  '# Membership'
  membership-1  membership.md  'A semester membership costs $15 and includes unlimited '
  ...
  tools-2       tools.md       'The parts washer uses citrus degreaser only. Never pour'
```

> **Checkpoint 1.**  The lab's Step 2 asks you to predict what chunk a heading on its own line becomes.  Here is the answer: `hours-0`, `membership-0`, `safety-0`, and `tools-0` are each a bare heading.  Before Step 4, predict whether a bare heading will help or hurt a search for "How much does a membership cost for a student?"  Write the prediction down.

## Step 3 and Step 4: Embed and Retrieve

**Goal:** a vector for every chunk, and a search that returns the three closest chunks to a question, best first, each labeled with its file.  On your machine, Chroma embeds each chunk for you when you call `upsert`, and `collection.query(query_texts=[...], n_results=3)` embeds the question and searches.  In this page, `toy_embed` counts the words that remain after dropping common words, and `cosine` compares two of those counts.  A real embedding model does far better on wording that differs, and Step 6 shows where the stand-in fails because of it.

```python
# Steps 3 and 4: embed every chunk, then retrieve the top k for a question.
import math
import re

STOP = {"a", "an", "the", "to", "on", "of", "is", "are", "and", "or", "for", "from", "with",
        "in", "it", "do", "does", "i", "my", "can", "what", "when", "how", "who", "before",
        "any", "anyone", "every", "much", "may", "must", "whenever", "only", "stay"}

def toy_embed(text):
    """A bag-of-words stand-in for a real embedding: same text in, same vector out."""
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
    """The lab's search tool, in miniature: the k closest chunks, best first."""
    q = toy_embed(query)
    ranked = sorted(index, key=lambda row: (-cosine(q, row["vec"]), row["id"]))
    return [(row["id"], round(cosine(q, row["vec"]), 3), row) for row in ranked[:k]]

index = build_index(chunks)
print("Vector for membership-1:", next(r["vec"] for r in index if r["id"] == "membership-1"))
print()
question = "How much does a membership cost for a student?"
print("Q:", question, "->", toy_embed(question))
for cid, score, row in search_notes(index, question):
    print(f"  {cid:<13} {score:.3f}  [{row['source']}] {row['text'][:50]!r}")
```
@Pyodide.eval

**You should see:**

```text
Vector for membership-1: {'semester': 1, 'membership': 1, 'cost': 1, '$15': 1, 'include': 1, 'unlimited': 1, 'stand': 1, 'time': 1, 'student': 1, 'college': 1, 'id': 1, 'pay': 1, '$10': 1}

Q: How much does a membership cost for a student? -> {'membership': 1, 'cost': 1, 'student': 1}
  membership-0  0.577  [membership.md] '# Membership'
  membership-1  0.480  [membership.md] 'A semester membership costs $15 and includes unlim'
  hours-0       0.000  [hours.md] '# Hours'
```

> **Checkpoint 2.**  Check your prediction from Checkpoint 1.  The bare heading `membership-0` outranks the passage that answers the question, because a one-word chunk that shares one word with a three-word question scores $1/\sqrt{3} \approx 0.577$.  Then notice the third hit: `hours-0` scored 0.000 and was returned anyway.  Retrieval always returns $k$ chunks, relevant or not.  What in Step 5 has to handle that?

## Step 5: Generate a Grounded Answer

**Goal:** the retrieved passages and the question assembled into the lab's grounding prompt, then an answer that names its file, or an abstention.  The prompt below is the lab's no-code prompt (Step N3) word for word; the code route puts the same three rules into the agent's `instructions`.  The prompt is the whole of what the model sees, so print it.

```python
# Step 5: build the grounded prompt, then generate.  In this page a stand-in plays the model.
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
    """Not a language model: it copies the best-matching sentence and names its file,
    or abstains, so the page can show every step.  On your machine, the agent writes this."""
    best_id, best_score, best_row = hits[0]
    if best_score < min_score:
        return "I could not find that in your notes."
    q = toy_embed(question)
    sentences = re.split(r"(?<=[.!?])\s+", best_row["text"])
    sentence = max(sentences, key=lambda s: cosine(q, toy_embed(s)))
    return f"{sentence} [{best_row['source']}]"

for question in ["How much does a membership cost for a student?",
                 "Does the co-op sell new bikes?"]:
    hits = search_notes(index, question)
    print(build_prompt(question, hits))
    print("ANSWER:", stand_in_model(question, hits))
    print("-" * 60)
```
@Pyodide.eval

**You should see** the full prompt for each question, then:

```text
ANSWER: # Membership [membership.md]
...
ANSWER: I could not find that in your notes.
```

The second answer is right: the co-op notes never mention selling bikes, and the stand-in abstained because nothing it retrieved scored above `min_score`.  The first answer is useless, and the prompt shows why: the passage that holds `$10` was in the prompt, but the stand-in copied from the top passage, the bare heading.  On your machine a language model reads all three passages and may well do better, which is exactly why you measure rather than assume.

> **Checkpoint 3.**  Point at the line of the printed prompt the model needs for the first question, and the line it should ignore.  Then say which component, if any, was at fault for the useless answer: the chunker, the retriever, or the generator.

## Step 6: Measure Recall@k and Grounding

**Goal:** two numbers and a verdict per question, from the golden set you wrote first.  `recall_at_k` checks whether the evidence phrase appears in any of the top $k$ chunks; it measures the retriever.  `grounded` checks whether every content word of the answer appears in a retrieved passage from the file the answer names; it measures whether the answer stayed inside its evidence.  Neither one alone tells you the answer was right, so the report checks that too.

```python
# Step 6: measure.  A golden set, written before any tuning, scored two ways.
GOLDEN = [   # (question, a phrase only the right passage contains, the fact a right answer states)
    ("How much does a membership cost for a student?", "pay $10",              "$10"),
    ("When is the workshop open on Saturday?",          "Saturday from 10am",   "10am to 2pm"),
    ("Can I take a pump home overnight?",                "borrow a pump",        "$5"),
    ("What do I need before using a repair stand?",     "30-minute orientation", "orientation"),
    ("Who do I tell if I get hurt?",                     "Report any injury",    "shift volunteer"),
    ("Does the co-op sell new bikes?",                   None,                   None),
]

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
        print(f"  {q[:46]:<46} top3={[cid for cid, _, _ in hits]}  {verdict}")

report(index, "paragraph chunks, as the lab's index.py makes them")

# Grounding is a check on the answer, not on the retriever.  Three replies to the first question:
hits = search_notes(index, GOLDEN[0][0])
for reply in ["Students with a college ID pay $10. [membership.md]",
              "Students pay $8 per semester. [membership.md]",
              "Students with a college ID pay $10. [tools.md]"]:
    print(f"  grounded={str(grounded(reply, hits)):<5}  {reply}")
```
@Pyodide.eval

**You should see:**

```text
== paragraph chunks, as the lab's index.py makes them: 12 chunks ==
  recall@1 = 0.60   recall@3 = 0.80
  How much does a membership cost for a student? top3=['membership-0', 'membership-1', 'hours-0']  WRONG, grounded
  When is the workshop open on Saturday?         top3=['hours-1', 'hours-2', 'tools-1']  right, grounded
  Can I take a pump home overnight?              top3=['tools-1', 'hours-0', 'hours-1']  right, grounded
  What do I need before using a repair stand?    top3=['membership-2', 'membership-1', 'tools-1']  right, grounded
  Who do I tell if I get hurt?                   top3=['hours-0', 'hours-1', 'hours-2']  abstained (should answer)
  Does the co-op sell new bikes?                 top3=['hours-1', 'hours-0', 'hours-2']  abstained
  grounded=True   Students with a college ID pay $10. [membership.md]
  grounded=False  Students pay $8 per semester. [membership.md]
  grounded=False  Students with a college ID pay $10. [tools.md]
```

Read the report row by row.  Recall@1 is 0.60 because two of the five answerable questions do not have their evidence at rank 1: the membership question lost rank 1 to a bare heading, and the injury question found nothing, because "tell" and "hurt" share no words with "Report any injury."  That second miss is a vocabulary mismatch, and it belongs to the stand-in embedding; a real embedding model is built to place "hurt" near "injury."  The three hand-written replies at the bottom show what grounding catches: an invented amount, and a correct fact attributed to the wrong file.  It does not catch a fact copied faithfully from the wrong sentence, which is why the report keeps "right" and "grounded" as separate words.

Now fix the chunking, and measure again with the same golden set.

```python
# The fix: fold each heading into the paragraphs under it, so no chunk is a bare heading.
def heading_chunks(corpus):
    rows = []
    for name in sorted(corpus):
        heading, i = "", 0
        for p in [p.strip() for p in corpus[name].split("\n\n") if p.strip()]:
            if p.startswith("#"):
                heading = p.lstrip("# ").strip()      # remember it; do not store it alone
                continue
            rows.append({"id": f"{name.rsplit('.', 1)[0]}-{i}", "source": name,
                         "text": f"{heading}: {p}" if heading else p})
            i += 1
    return rows

report(build_index(heading_chunks(CORPUS)), "each heading folded into its paragraphs")
fixed = build_index(heading_chunks(CORPUS))
q = GOLDEN[0][0]
print("\nTop passage now:", search_notes(fixed, q)[0][2]["text"])
print("Answer:", stand_in_model(q, search_notes(fixed, q)))
```
@Pyodide.eval

**You should see:**

```text
== each heading folded into its paragraphs: 8 chunks ==
  recall@1 = 0.80   recall@3 = 0.80
  How much does a membership cost for a student? top3=['membership-0', 'membership-1', 'hours-0']  WRONG, grounded
  ...
Top passage now: Membership: A semester membership costs $15 and includes unlimited stand time. Students with a college ID pay $10.
Answer: Membership: A semester membership costs $15 and includes unlimited stand time. [membership.md]
```

Recall@1 rose from 0.60 to 0.80 with no change to the retriever: `membership-0` is now the passage that answers the question, and its heading travels with it.  The golden set did not need editing, because it names evidence by phrase, not by chunk ID.  The membership answer is still wrong, and now the fault has moved: retrieval found the right passage and the answer is grounded in it, but the stand-in copied the `$15` sentence instead of the `$10` sentence.  That is a generation failure, and no amount of retrieval tuning would fix it.

**Checkpoint 4.**  Fill in this table from the two reports, and have the Recorder keep it for Part II.

| Chunking | Chunks | recall@1 | recall@3 | Right | Grounded | Correct abstentions |
|---|---|---|---|---|---|---|
| Paragraph (lab default) | 12 | | | of 5 | of 5 | of 1 |
| Heading folded in | 8 | | | of 5 | of 5 | of 1 |

### Common Mistakes

- **Writing the golden set after looking at the answers.**  A golden set written after you have seen what the pipeline returns measures your agreement with it, not its quality.  Write the questions, evidence, and facts first, as above.
- **Naming gold evidence by chunk ID.**  `membership-1` became `membership-0` the moment the chunking changed.  Name evidence by a phrase only the right passage contains.
- **Counting the unanswerable question in recall.**  It has no evidence to find.  `recall_at_k` scores only the answerable questions; the abstention gets its own verdict.
- **Treating grounded as correct.**  The membership answer was grounded and wrong.  Check the fact separately, as the lab's Step 4 does: "was it right, and does the file it named actually say that?"
- **Tuning two things at once.**  Change the chunking or the number of results, not both, and rerun the same golden set after each change.
- **Leaving bare headings in the index.**  They win searches on one shared word and carry no answer.  Fold them into the paragraphs below them, or drop them.

---
# Part II: The Same Corpus on Your Machine

> **In class: five minutes.**  One laptop per team saves the corpus, runs the route you chose, and asks one golden-set question.  If the answer names its source file, you have the first row of Checkpoint 5.  The rest of this part is self-paced lab work.

Now replace both stand-ins.  Save the four co-op files as a `corpus/` folder, then follow the lab on the route you chose.  The measurement is the same on both routes: the golden set from Part I, recall@3, and a right-and-grounded check on every answer.

```python
# save_corpus.py: write the four co-op files into corpus/ for the lab's code or Langflow.
from pathlib import Path

Path("corpus").mkdir(exist_ok=True)
for name, text in CORPUS.items():          # paste the CORPUS dictionary from Step 1 above this loop
    Path("corpus", name).write_text(text + "\n", encoding="utf-8")
print(sorted(p.name for p in Path("corpus").iterdir()))
```

## Code Route: The Lab's `index.py` and `rag_agent.py`, Then a Measurement Script

> **Runs on your machine, not here.**  These scripts talk to Chroma on disk and to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.

1.  **Ingest, chunk, and embed.**  Save the lab's `index.py` from its Step 2 next to `corpus/` and run `python index.py`.  You should see `Indexed 12 chunks from 4 files.`, the same twelve paragraph chunks as Step 2 above, now embedded by Chroma's own embedding model.
2.  **Retrieve and generate.**  Save the lab's `rag_agent.py` from its Step 3 and run `python rag_agent.py "How much does a membership cost for a student?"`.  You should see a `[tool call] search_notes(...)` line, a `[tool result]` line that begins with a file name in brackets, and an answer that names a file.
3.  **Measure.**  Save the script below as `measure.py` in the same folder and run `python measure.py`.  It imports `collection` and `agent` from `rag_agent.py` (the file's `__main__` guard keeps the import from asking a question), computes recall@1 and recall@3 against Chroma, then asks the agent each golden question and checks the answer.

```python
# measure.py: score the lab's index and agent against the golden set from Part I.
import traceback

from pydantic_ai import UsageLimits
from rag_agent import agent, collection   # both are defined at the top of rag_agent.py

GOLDEN = [   # (question, evidence phrase, fact a right answer states); rewrite for your own corpus
    ("How much does a membership cost for a student?", "pay $10", "$10"),
    ("When is the workshop open on Saturday?", "Saturday from 10am", "10am to 2pm"),
    ("Can I take a pump home overnight?", "borrow a pump", "$5"),
    ("What do I need before using a repair stand?", "30-minute orientation", "orientation"),
    ("Who do I tell if I get hurt?", "Report any injury", "shift volunteer"),
    ("Does the co-op sell new bikes?", None, None),
]


def top_k(question, k):
    """The k passages Chroma returns for a question, as (source file, text) pairs."""
    try:
        hits = collection.query(query_texts=[question], n_results=k)
    except Exception as e:
        print("[measure:top_k]", e)
        traceback.print_exc()
        raise
    return [(meta["source"], text) for text, meta in zip(hits["documents"][0], hits["metadatas"][0])]


def recall_at_k(k):
    answerable = [(q, ev) for q, ev, _ in GOLDEN if ev]
    return sum(any(ev in text for _, text in top_k(q, k)) for q, ev in answerable) / len(answerable)


def ask(question):
    """Run the agent once; return its answer and the tool results it was given."""
    try:
        result = agent.run_sync(question, usage_limits=UsageLimits(request_limit=4))
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
        answer, returned = ask(question)
        searched = bool(returned)
        abstained = "could not find" in answer.lower()
        names_returned_file = any(f"[{source}]" in returned and source in answer
                                  for source in ("hours.md", "membership.md", "tools.md", "safety.md"))
        right = abstained if fact is None else (fact.lower() in answer.lower() and not abstained)
        print(f"\nQ: {question}\n  searched={searched}  right={right}  "
              f"names a file it was given={names_returned_file}\n  A: {answer}")
```

The script automates what a machine can check: whether the agent searched, whether the answer contains the right fact or abstains when it should, and whether it names a file that the search actually returned.  It cannot check that the named file *says* the claim; that is the lab's one-line human check per question, and it stays yours.

> **Checkpoint 5 (code route).**  Add a row for Chroma to the Checkpoint 4 table.  Did Chroma's embedding model find the injury passage that the stand-in missed?  Did the bare headings still cost you rank 1 on the membership question?  If recall@1 is below recall@3, fold the headings into their paragraphs in `index.py` (the `heading_chunks` rule from Step 6), delete `chroma_db`, rerun `index.py`, and measure again.

## No-Code Route: The Lab's Langflow Flow

1.  **Ingest, chunk, and embed.**  Follow the lab's Steps N1 and N2: **File** (upload the four files in `corpus/`) to **Text Splitter** (chunk size 1000, overlap 100) to **Chroma** (collection `notes`), with **Ollama Embeddings** (`nomic-embed-text`) wired into Chroma.  Read the stored chunk count in the Chroma node's inspection view.  Each co-op file is shorter than 1000 characters, so predict the count before you look: is it twelve, like `index.py`, or something else?
2.  **Retrieve and generate.**  Wire the query path from Step N2 with the number of results set to 3, and paste the Step N3 prompt (the same prompt Step 5 printed) into the **Prompt** node.
3.  **Measure.**  Ask each golden question in a fresh **Playground** session.  For each one, open the search step's inspection view and copy the three chunks it returned into a spreadsheet beside the question.  Mark a 1 in the recall@3 column if the evidence phrase appears in any of the three, and compute recall@3 as the column's average over the five answerable questions.  Then mark each answer right or wrong, and grounded or not by reading the passage from the file it names.

> **Checkpoint 5 (no-code route).**  Add a row for Langflow to the Checkpoint 4 table.  How did a 1000-character splitter treat the bare headings, and what did that do to recall?  The node settings you used, written in your readme, are the no-code route's equivalent of `index.py`.

---
# Part III: Exercise and Wrap-Up

## Exercise: A Golden Set for Your Own Corpus (self-paced)

- *What to do*: Choose the five to twenty files you will index for the lab, and before you index them, write a golden set of six questions in the Part I format: four your notes answer (worded differently from the notes), one they do not, and one you expect to be hard because the wording differs.  Then index the corpus on your route and fill in one row of the Checkpoint 4 table for it.
- *Starter hint*: Choose evidence phrases of three to five words that appear in exactly one passage.  Search your files for each phrase before you commit to it; a phrase that appears twice will mark the wrong passage as found.
- *You've succeeded when*: You have a golden set written before indexing, a recall@3 for your own corpus, and one sentence naming the question that failed and which component (chunker, retriever, or generator) owned the failure.

This exercise does the lab's Step 1 and Step 4 in the right order.  Three of your six questions can be the lab's three golden questions.  The lab's writeup question about what you would change if your notes doubled in size now has an answer you can measure.

## Reflection Prompt

*Personal:* The golden set made you decide what a right answer was before you saw any answers.  Where else in your own work do you judge results after seeing them, and what would change if you wrote the test first?

*Technical:* Grounding and correctness came apart twice today: a grounded answer that copied the wrong sentence, and a correct fact attributed to the wrong file.  Design one more automatic check that would have caught the first case, and say what it would cost you in false alarms.

*Societal:* An office deploys a knowledge base like this one over its policies and reports "recall@3 of 0.95."  What should a person relying on its answers ask before trusting that number: about the golden set, about who wrote it, and about which questions it left out?

---

# Proposal Clinic

Your team's [Final Project Proposal](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/FinalProjectProposal) is due Thursday.  Use these twenty minutes to settle what is still open while I am in the room to help.  Fill in one card per team, with four lines:

1.  **Direction.**  The direction you are choosing, and the one you nearly chose instead.
2.  **Blocker.**  The one open question that is blocking your proposal.
3.  **Authors.**  The primary author of each proposal section.
4.  **Weekly meeting.**  Your team's meeting day and time, and who owns the first agenda.  This starts your [weekly team note](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/PBLThread#one-weekly-team-note), where every [Team Playbook](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/PBLThread#the-team-playbook) practice lives.

While you write, I circulate and answer line 2 on the spot.  Before you leave, put the card in your team note as its first entry.

---

-> Coming Up Next: *Agents That Talk, Observability, and Handoff Protocols* (Thursday) puts two agents on either end of a shared channel, a GitHub issue thread and a shared folder, and then asks how anyone can see what each one did: logs, traces, and a written handoff protocol.  Your team's Final Project Proposal is due at that session.  The trace you write there is the observability version of today's measurement: identifiers and numbers, kept for every run.

## Further Reading

- [Offline RAG and LoRA, End to End: Sections D to F train a LoRA adapter on a CPU and compare a base model, RAG, LoRA, and both on held-out questions.  The comparison is optional; the measurement steps are the ones today's worked example uses](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OfflineRAGFineTuning)
- [RAG From Zero](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/RAGFromZero), each step of today's pipeline on its own, in Python and in Langflow, with a retrieval-off comparison.
- The [RAG Knowledge Base lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RAGKnowledgeBase), whose steps this session followed in order.
- *Offline RAG and LoRA, End to End*, Section B: the same ingest-and-ask pipeline with a persistent index, stable chunk IDs, content hashes that make re-ingesting safe, and a distance cutoff, plus a worked case of a retrieval success and a generation failure on the same question: https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OfflineRAGFineTuning
- [Pydantic AI From the Loop Up](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/PydanticAI), for the agent and tool calls in `rag_agent.py`, and [Visual Agents](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/VisualAgents), for the Langflow wiring.
- [RAG: Building and Measuring a Knowledge Base](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-rag.md), for chunking strategies, recall@k, and the self-paced Extensions on rerankers and vector indexes.
