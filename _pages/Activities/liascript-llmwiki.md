# The LLM Wiki: Karpathy's Pattern and a Vault Full of Use Cases
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-llmwiki.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmwiki.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The LLM Wiki: Karpathy's Pattern and a Vault Full of Use Cases

In April 2026, Andrej Karpathy published a short gist describing how he uses LLMs to build and maintain **personal knowledge bases**: not a product, not a framework, just a pattern, and one that lands squarely on the vault you built in the second brain module. His one-line summary of the division of labor: *the editor is the IDE, the LLM is the programmer, and the wiki is the codebase.* This module studies the pattern, contrasts it with the RAG architecture you built earlier this semester, and then tours the use cases that make the system earn its keep daily (a research wiki, journaling, meeting notes, raw paper summaries, and more), ending with the complete technical setup wired to hermes. The arc: **the pattern and its three layers $\rightarrow$ wiki versus RAG $\rightarrow$ the use-case tour $\rightarrow$ the full setup, end to end**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisite: the second brain module, with your vault standing; this module assumes the three-zone structure, the gitless sync, and the `AGENTS.md` contract and builds use cases on top of them. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Pattern

## 1. Three Layers and a Linter

Karpathy's gist describes a deliberately simple architecture in three layers, and you will recognize all of them. The **Source layer** is read-only raw material: articles, transcripts, papers, exports, dropped in as they arrive and never edited (your `raw/`). The **Wiki layer** is the structured Markdown knowledge base the LLM reads *and writes*: entity pages, concept pages, cross-links, hub indexes, continuously grown and reorganized as sources accumulate (your `wiki/`). The **Schema layer** is the instruction file telling the LLM how to manage the wiki: what page types exist, how to link, when to merge versus create, how to handle conflicts between sources (your `AGENTS.md`, which the second brain module modeled directly on this gist). The inversion is the insight: **you stop being the person who writes and organizes notes and become the person who curates sources and asks questions**, while the LLM does the grunt work it genuinely does not mind, updating a dozen pages and every link among them without forgetting one.

The gist adds one maintenance idea worth adopting verbatim: **lint**. Periodically, the LLM sweeps the whole wiki looking for contradictions between pages, orphaned notes nothing links to, stale claims superseded by newer sources, and broken links, and either repairs them or files them for your review. A knowledge base with a linter is a living system; one without is the same pile of notes you already abandoned in three other apps.

## 2. Wiki Versus RAG: A Real Architectural Choice

You built a RAG pipeline in this course: chunk the corpus, embed the chunks, retrieve the nearest few at query time, answer from fragments. Karpathy's pattern takes a pointed alternative position for the *personal* scale: rather than fragmenting knowledge into chunks and hoping retrieval reassembles the right ones, **maintain a curated, compressed wiki small enough that large portions of it fit in a long context window**, and let the model reason over connected pages rather than disconnected shards. The trade-offs are honest in both directions, and you have the vocabulary to weigh them: RAG scales to corpora no context window will ever hold and needs no curation pass, but pays in fragmentation, retrieval misses, and chunks stripped of their connective tissue; the wiki pays an ongoing synthesis cost (in agent tokens, mostly) and tops out at personal-to-team scale, but buys coherent cross-page reasoning, human browsability (it is *also* your Obsidian vault), and knowledge that compounds instead of accumulating. One more honest caution from the pattern's critics: the wiki is only as good as the model maintaining it, since a weak model can propagate a source's error into five confident pages, which is why the schema's preserve-uncertainty rules and the lint pass are load-bearing rather than decorative.

---

## Model 1: Choose the Architecture

### Critical Thinking Questions

1. For each corpus, choose wiki, RAG, or a hybrid, with the deciding factor named: (a) your own 200 accumulated course and research notes; (b) the full text of 40,000 arXiv papers; (c) your team's project decision log; (d) a professor's 30 years of mixed-format files, mostly never to be read again.
2. The wiki's "compression" is lossy by design: synthesis discards source detail. Where does the pattern park the lost detail, and what does that imply about the one rule the Source layer must never break?
3. Connect lint to a course concept: which evaluation idea from our LLM-as-judge unit is lint the knowledge-base version of, and what is its reward-hacking analog (an agent that makes lint pass without making the wiki true)?

---

# Part II: The Use-Case Tour

## 3. What a Living Vault Is Actually For

The pattern earns its keep through daily uses, each of which is just the same loop (drop into `raw/`, agent synthesizes into `wiki/`, you ask questions) pointed at a different corner of your life. Six that work, with the conventions that make each one click.

**The research wiki** is the canonical use and Karpathy's own: every paper, post, and talk on a topic you care about goes to `raw/`; the agent maintains concept pages, technique pages, and people pages under `wiki/research/<topic>/`, cross-linked, with disagreements between sources explicitly surfaced. After a dozen sources, asking *"what are the open problems in X according to my wiki, and which sources disagree?"* returns an answer no single chat session could give, because the wiki *is* accumulated reasoning, not a transcript.

**Raw paper summaries** deserve their own convention even inside the research use: each paper gets one page (`wiki/papers/lastname2026-shorttitle.md`) with a fixed skeleton (claim, method, evidence, limitations, relevance to your projects, link back to the PDF in `raw/`), and the agent additionally threads each paper into the relevant concept pages. The fixed skeleton is what makes fifty paper pages *comparable*, which is what makes the literature-review question answerable.

**Journaling** runs the loop on your own life: a daily note (`wiki/journal/2026-06-11.md`, written by you, or dictated through voicebox from the stack) captures what happened and what you are thinking; weekly, the agent synthesizes a review page (themes, open loops, mood arc if you want it) and links forward into project pages. The payoff question, months later: *"when did I first get uneasy about the approach we abandoned in May, and why?"* Your journal knows; now it can answer.

**Meeting notes** are the workplace version: raw notes or transcripts (a Zoom export, an open-notebook capture) land in `raw/meetings/`; the agent produces a structured page per meeting (decisions, action items with owners, open questions) under `wiki/meetings/`, *and updates the affected project pages*, which is the step human note-takers always skip and the one that makes the system trustworthy. Standing prompt: *"process new meeting transcripts; any action item assigned to me also gets appended to wiki/projects/<project>/todo.md."* Apply the course's data-handling judgment here: meetings involving others' sensitive information may not belong in your vault at all, and that call is yours, made in advance, not the agent's.

**People and collaboration pages** (a lightweight CRM): a page per collaborator under `wiki/people/`, maintained by the agent from meeting notes and correspondence you choose to ingest, recording shared projects, commitments, and context, so that *"what did I promise Jason, and when?"* has an answer with provenance.

**Course and project memory** rounds out the set for this class specifically: your CS357 project's decision log, experiment results, and gallery-walk feedback all flow through `raw/` into `wiki/projects/cs357/`, giving your team a queryable institutional memory and giving your final report a source it can cite against itself.

[[MC]]
The fixed page skeleton for paper summaries (claim, method, evidence, limitations, relevance) primarily buys:
- ( ) Shorter pages
- (x) Comparability across many papers, so synthesis questions spanning the literature can be answered structurally rather than by rereading
- ( ) Compliance with Obsidian's format requirements
- ( ) Faster PDF parsing

---

## Model 2: Design Your Corner

Each teammate picks one use case from the tour (no duplicates within a team).

### Critical Thinking Questions

4. Specify your use case's conventions in four lines: the `raw/` drop convention, the `wiki/` directory and page-naming scheme, the page skeleton, and the one standing prompt that maintains it. The Recorder collects all four sets.
5. Name the question you most want your corner to answer in December, and verify your conventions actually capture the inputs that question requires. (Working backward from the question is the design method.)
6. Identify the privacy boundary your use case skirts closest to (journaling and meeting notes are the spicy ones), and write the inclusion rule you will follow, in one enforceable sentence.

---

# Part III: The Setup, End to End

## 4. From Standing Vault to Living Wiki

Everything below assumes the second brain module's foundation (private repository, gitless sync with your PAT, three zones, `AGENTS.md` with the metadata protocol). The LLM Wiki additions are four steps.

**Step 1: extend the schema.** Append a use-case section to `AGENTS.md` declaring your conventions from Model 2, the lint specification (sweep for contradictions, orphans, staleness, broken links; repair conservatively; write a report to the repository root; flag ambiguous repairs for human review rather than applying them), and the page-skeleton definitions. The schema layer is where the pattern lives; an undocumented convention does not exist.

**Step 2: seed the wiki.** Drop three to five real sources into `raw/` (a paper PDF, a meeting transcript, last week's journal entries) and run the ingestion prompt against hermes:

```
Clone https://github.com/YOURUSERNAME/Obsidian-Vault using the token in
GITHUB_TOKEN, read AGENTS.md completely, and process all unprocessed material
in raw/ into the wiki per the schema, including the use-case conventions and
the sync metadata protocol. Commit atomically and summarize what you built.
```

**Step 3: schedule the loop.** Manual runs work; the system sings when n8n (from the agent stack) runs the ingestion nightly and the lint weekly, each as a scheduled workflow that launches the agent with the prompt above (the lint variant swaps in *"run the lint pass specified in AGENTS.md"*). Your vault now updates while you sleep, and Obsidian's morning sync delivers the results.

**Step 4: use it.** The query prompt, which is also the habit: *"Using the vault per AGENTS.md, answer from wiki/ first: <your question>. If raw/ holds newer relevant material, update the wiki before answering."* That update-before-answering clause is the compounding mechanism: every question that finds a gap leaves the wiki better than it found it.

Verification matrix, in the agent stack module's spirit: after the first scheduled run, confirm (a) new wiki pages exist on GitHub with their metadata entries in the same commits, (b) Obsidian pulls them on sync, (c) a query prompt cites wiki pages rather than re-deriving from raw, and (d) the lint report exists and is honest.

## 5. Exercises

1. *Schema extension.* Add your Model 2 conventions and the lint specification to `AGENTS.md`, committed through Obsidian sync. Submit the diff.
2. *Seed and ingest.* Execute Steps 2 and 4 with real sources, and submit the agent's commit log, one resulting wiki page, and the answer to your December question's nearest present-day approximation, with the wiki pages it cited.
3. *Paper pipeline.* Ingest two related papers using the fixed skeleton, then ask the cross-paper question ("where do these two disagree, and what evidence would settle it?"). Evaluate the answer's groundedness against the pages, using your judge-calibration instincts.
4. *First lint.* Plant one contradiction and one orphan page deliberately, run the lint pass, and grade the agent's report and repairs (did it fix conservatively and flag, or bulldoze?). Two-sentence verdict.
5. *Schedule it.* Build the n8n nightly-ingest workflow, let it run twice, and submit evidence both runs behaved (commits, sync, no metadata violations). Note what you checked to convince yourself, because that checklist is your monitoring design.

---

## Reflection Prompt

In your notebook: Karpathy's framing puts you in the editor's chair while the model writes, which is either the freeing end of note-taking drudgery or the outsourcing of the very synthesis that made notes valuable to write, depending on whom you ask. After running the loop yourself, which is it for you, and which kinds of pages do you want to keep writing by hand precisely because the writing is the thinking?

---

## 6. Further Reading

- Andrej Karpathy, the LLM Wiki gist (gist.github.com/karpathy, April 2026): the pattern in its author's words; short, read it whole.
- W. Mongan, "A Private AI Knowledge Base" (billmongan.com, May 2026): the vault architecture this module builds on, including the AGENTS.md schema in full.
- Your own RAG lab writeup, reread: the strongest way to internalize the wiki-versus-RAG trade is to argue it against your own prior work.
