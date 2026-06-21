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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Source layer** | The read-only zone where raw material lands exactly as it arrives — articles, transcripts, papers, exports — and is never edited | Dropping a PDF of a research paper into `raw/papers/` without changing a word of it |
| **Wiki layer** | The structured Markdown knowledge base that the LLM both reads and writes — organized into entity pages, concept pages, and hub indexes that grow as sources accumulate | The agent creates `wiki/research/transformers/attention-mechanisms.md` after processing three attention papers |
| **Schema layer** | The instruction file (`AGENTS.md`) that tells the LLM how to manage the wiki: what page types exist, how to link between pages, when to merge versus create, and how to handle conflicting sources | `AGENTS.md` specifies: "Each paper gets exactly one page under `wiki/papers/` with sections: claim, method, evidence, limitations, relevance" |
| **Lint (wiki lint)** | A periodic sweep where the LLM reads the entire wiki looking for contradictions, orphaned pages, stale claims, and broken links — then either repairs them conservatively or flags them for human review | The lint pass finds that `wiki/research/topic-A.md` claims X while `wiki/research/topic-B.md` claims not-X, and flags the conflict |
| **RAG (Retrieval-Augmented Generation)** | An architecture where a large corpus is chunked, embedded as vectors, and searched at query time — the nearest chunks are retrieved and passed to the LLM as context | Your RAG pipeline from earlier in the semester: embed all course documents, retrieve the most relevant chunks for each question |
| **Compounding knowledge** | The property of a well-maintained wiki where each new source makes previous sources more useful, because the wiki accumulates cross-links and synthesized understanding rather than just adding more raw text | After 20 papers, asking "what are the open problems in X?" returns a synthesis of all 20 papers' limitations sections — better than any single paper |

---

# Part I: The Pattern

## 1. Three Layers and a Linter

Think of a well-curated wiki like a well-organized research notebook that writes its own index. When you finish reading a paper, you do not just file it away — you update your notes on the concept it addresses, add a cross-reference from the authors' names, and flag where it contradicts something you read last week. That is exactly what Karpathy's pattern automates: the LLM does the filing, cross-referencing, and contradiction-flagging, so you spend your time reading and asking questions rather than updating notes.

Karpathy's gist describes a deliberately simple architecture in three layers, and you will recognize all of them. The **Source layer** is read-only raw material: articles, transcripts, papers, exports, dropped in as they arrive and never edited (your `raw/`). The **Wiki layer** is the structured Markdown knowledge base the LLM reads *and writes*: entity pages, concept pages, cross-links, hub indexes, continuously grown and reorganized as sources accumulate (your `wiki/`). The **Schema layer** is the instruction file telling the LLM how to manage the wiki: what page types exist, how to link, when to merge versus create, how to handle conflicts between sources (your `AGENTS.md`, which the second brain module modeled directly on this gist). The inversion is the insight: **you stop being the person who writes and organizes notes and become the person who curates sources and asks questions**, while the LLM does the grunt work it genuinely does not mind — updating a dozen pages and every link among them without forgetting one.

The gist adds one maintenance idea worth adopting verbatim: **lint**. Periodically, the LLM sweeps the whole wiki looking for contradictions between pages, orphaned notes that nothing links to, stale claims superseded by newer sources, and broken links, and either repairs them or files them for your review. A knowledge base with a linter is a living system; one without is the same pile of notes you already abandoned in three other apps.

## 2. Wiki Versus RAG: A Real Architectural Choice

You built a RAG pipeline in this course: chunk the corpus, embed the chunks, retrieve the nearest few at query time, answer from fragments. Karpathy's pattern takes a pointed alternative position for the *personal* scale: rather than fragmenting knowledge into chunks and hoping retrieval reassembles the right ones, **maintain a curated, compressed wiki small enough that large portions of it fit in a long context window**, and let the model reason over connected pages rather than disconnected shards. The trade-offs are honest in both directions, and you have the vocabulary to weigh them now:

| Dimension | RAG | Wiki (Karpathy pattern) |
|-----------|-----|------------------------|
| **Scale** | Handles corpora of millions of documents — far more than any context window can hold | Tops out at personal-to-team scale — a few thousand pages, not millions |
| **Curation cost** | Minimal — chunk and embed automatically; no synthesis required | Ongoing — each new source triggers a synthesis pass (in agent tokens, mostly) |
| **Query quality** | Depends on embedding quality and chunking strategy; retrieved chunks may lack connective tissue | Reasons over connected pages with cross-links intact; better for questions that span multiple topics |
| **Human browsability** | The embedded chunks are not human-readable in the traditional sense | The wiki *is* your Obsidian vault — you can browse it like a normal notebook |
| **Knowledge compounding** | Scales by adding more chunks; knowledge accumulates but does not synthesize | Knowledge genuinely compounds — later sources make earlier pages more useful |
| **Model error propagation** | A retrieval miss is an isolated failure | A synthesis error can propagate to many pages before lint catches it |

One more honest caution from the pattern's critics: the wiki is only as good as the model maintaining it, since a weak model can propagate a source's error into five confident pages. This is why the schema's preserve-uncertainty rules and the lint pass are load-bearing rather than decorative.

---

## Model 1: Choose the Architecture

Understanding the wiki-versus-RAG trade-off is not about memorizing which is better — it depends entirely on scale, curation capacity, and what kinds of questions you need to answer. Work through the concrete cases below to develop your judgment.

### Critical Thinking Questions

**Question 1.** For each corpus, choose wiki, RAG, or a hybrid, with the deciding factor named: (a) your own 200 accumulated course and research notes; (b) the full text of 40,000 arXiv papers; (c) your team's project decision log; (d) a professor's 30 years of mixed-format files, mostly never to be read again.

[[___ Your answer here ___]]

*Hint:* For (a): Is 200 notes curate-able? What kinds of questions would you want to ask across them? For (b): Does a context window exist that could hold meaningful portions of 40,000 papers? For (c): Is a decision log small enough to curate, and would you benefit from cross-links between decisions? For (d): If most files will never be read again, is the synthesis cost of a wiki justified?

**Question 2.** The wiki's "compression" is lossy by design: synthesis discards source detail. Where does the pattern park the lost detail, and what does that imply about the one rule the Source layer must never break?

[[___ Your answer here ___]]

*Hint:* The lost detail stays in the Source layer — the raw files are never deleted or modified. If a wiki page turns out to be wrong (synthesis error, conflicting sources), you need the original source to adjudicate. What happens if you delete or modify files in `raw/`? Why is the "never edit the source layer" rule the one rule that makes the whole system trustworthy?

**Question 3.** Connect lint to a course concept: which evaluation idea from our LLM-as-judge unit is lint the knowledge-base version of, and what is its reward-hacking analog (an agent that makes lint pass without making the wiki true)?

[[___ Your answer here ___]]

*Hint:* In the LLM-as-judge unit, we discussed the risk of an agent optimizing for the judge's rubric rather than for the underlying quality being measured. Lint is a judge: it checks for contradictions, orphans, and broken links. What would it look like for an agent to "pass lint" by making superficial changes that resolve the reported errors without actually making the wiki more accurate? What would a reward-hacking lint-passer do?

---

> **⚠️ Common Misconception:** Students often assume that more sources automatically make the wiki better. This is only true if the agent synthesizes them faithfully and the lint pass catches errors. A wiki maintained by a weak model with no lint pass can become *less* reliable as sources accumulate, because each synthesis error gets cross-linked into more and more pages. The discipline is not in adding sources — it is in the schema and the lint pass that keep the synthesis honest.

---

# Part II: The Use-Case Tour

## 3. What a Living Vault Is Actually For

The pattern earns its keep through daily uses, each of which is just the same loop (drop into `raw/`, agent synthesizes into `wiki/`, you ask questions) pointed at a different corner of your life. The key insight is that the loop is always the same — what changes is the naming convention, the page skeleton, and the standing prompt. Six use cases that work, with the conventions that make each one click.

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

Each teammate picks one use case from the tour (no duplicates within a team). The goal is to arrive at conventions specific enough that you could hand them to someone else — or to the agent — and they would know exactly what to do.

### Critical Thinking Questions

**Question 4.** Specify your use case's conventions in four lines: the `raw/` drop convention (where and how to drop sources), the `wiki/` directory and page-naming scheme, the page skeleton (what sections every page in this use case has), and the one standing prompt that maintains it. The Recorder collects all four sets.

[[___ Your conventions here ___]]

*Hint:* Be specific enough that the conventions are mechanical. "Drop papers in `raw/papers/` with the filename format `lastname2026-shorttitle.pdf`" is specific. "Put papers somewhere" is not. The page skeleton should specify exact section headings — if someone reads two pages from your use case, they should always see the same structure.

**Question 5.** Name the question you most want your corner to answer in December, and verify your conventions actually capture the inputs that question requires. Work backward from the question to the inputs, and check that your `raw/` drop convention and page skeleton would make those inputs available.

[[___ Your answer here ___]]

*Hint:* If your December question is "which papers in my research wiki disagree about approach X?" then your page skeleton must have a section for each paper's position on approach X. If the skeleton just says "summary," the agent has no way to record positions in a comparable, queryable way. Work backward from the question to the required structure.

**Question 6.** Identify the privacy boundary your use case skirts closest to (journaling and meeting notes are the most sensitive), and write the inclusion rule you will follow, in one enforceable sentence.

[[___ Your inclusion rule here ___]]

*Hint:* An enforceable inclusion rule specifies what types of content are and are not included, without relying on judgment calls in the moment. "I will include all meeting notes" is not enforceable (what about notes from meetings where sensitive personnel decisions were discussed?). "I will include meeting notes only from meetings where all attendees are aware their notes may be processed by an AI system" is enforceable — you can check it before every drop.

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

**Exercise 1.** Schema extension. Add your Model 2 conventions and the lint specification to `AGENTS.md`, committed through Obsidian sync.

*What to do:* Open `AGENTS.md` in your vault. Add a new section titled `## Use-Case: [Your Use Case Name]` with the four convention lines from Question 4. Add a `## Lint Specification` section with the lint behavior described in Step 1 above.

*Starter hint:*

```markdown
## Use-Case: Research Wiki

**raw/ convention:** Drop papers as `raw/papers/lastname2026-shorttitle.pdf`. No edits after dropping.

**wiki/ convention:** One page per paper at `wiki/papers/lastname2026-shorttitle.md`. Concept pages at `wiki/research/<topic>/<concept>.md`.

**Page skeleton:**
### Claim
### Method
### Evidence
### Limitations
### Relevance to My Projects
### Source: [link to raw/]

**Standing prompt:** "Process any unprocessed files in raw/papers/ into wiki/papers/ using the skeleton above, then thread each paper into relevant concept pages under wiki/research/."
```

*You've succeeded when:* `AGENTS.md` includes your full use-case section and lint specification, committed to the repository, and the structure is specific enough that someone who has never seen your vault could follow it without asking you questions.

Submit the diff of your `AGENTS.md` changes.

**Exercise 2.** Seed and ingest. Execute Steps 2 and 4 with real sources, and submit the agent's commit log, one resulting wiki page, and the answer to your December question's nearest present-day approximation with the wiki pages it cited.

*What to do:* Drop three real sources into `raw/`. Run the ingestion prompt from Step 2 against hermes. Then run the query prompt from Step 4 with the closest approximation of your December question that is answerable now.

*Starter hint:* Use the exact ingestion prompt from Step 2 above, substituting your GitHub username. After the agent commits, pull in Obsidian and verify the new wiki pages appear. Then run: *"Using the vault per AGENTS.md, answer from wiki/ first: [your question]. If raw/ holds newer relevant material, update the wiki before answering."*

*You've succeeded when:* The agent's response to your question cites specific wiki pages by path (not raw files), and those pages exist in your repository with the correct skeleton structure.

**Exercise 3.** Paper pipeline. Ingest two related papers using the fixed skeleton, then ask the cross-paper question: "Where do these two papers disagree, and what evidence would settle the disagreement?" Evaluate the answer's groundedness against the pages, using your judge-calibration instincts from earlier in the semester.

*What to do:* Drop two papers on the same topic into `raw/papers/`. Run the ingestion prompt. Then run the cross-paper question. For each claim in the answer, check: is there a sentence in the corresponding wiki page that supports it?

*Starter hint:* A well-grounded answer cites specific page paths and section headings: "According to `wiki/papers/smith2025-attention.md#Limitations`, the method does not generalize to...". An ungrounded answer synthesizes from memory: "In general, these approaches differ in...". The former is what you are looking for.

*You've succeeded when:* You can label each sentence in the cross-paper answer as "grounded" (supported by a specific wiki page section) or "ungrounded" (synthesized without traceable support), and at least 80% of the answer's substantive claims are grounded.

**Exercise 4.** First lint. Plant one contradiction and one orphan page deliberately, run the lint pass, and grade the agent's report and repairs.

*What to do:* Edit one wiki page to say something that contradicts another page on the same topic. Create a new wiki page with no links to it from any other page (the orphan). Then run the lint pass: *"Run the lint pass specified in AGENTS.md. Report what you found and what you changed. Flag anything you were unsure about rather than applying a repair automatically."*

*Starter hint:* Good lint behavior: finds both the contradiction and the orphan, repairs the orphan by adding a link from the most relevant hub page, flags the contradiction for human review with both conflicting statements quoted. Bad lint behavior: silently resolves the contradiction by deleting one claim (bulldoze), or misses either the contradiction or the orphan.

*You've succeeded when:* You can write a two-sentence verdict: what the lint pass correctly found and fixed, and what it missed or handled incorrectly. "It correctly identified the orphan and linked it from the topic hub. It found the contradiction but silently deleted one claim instead of flagging it — a conservative repair would have flagged it instead."

**Exercise 5.** Schedule it. Build the n8n nightly-ingest workflow, let it run twice, and submit evidence that both runs behaved correctly.

*What to do:* In n8n, create a scheduled workflow that runs the ingestion prompt against hermes each night. Let it run on two consecutive nights. After each run, check: (a) did it commit new wiki pages? (b) do the pages have the correct metadata entries? (c) did Obsidian sync pull them?

*Starter hint:* The n8n workflow has three nodes: Schedule trigger (set to nightly), HTTP Request to the hermes API (with the ingestion prompt as the body), and a Slack/email notification with the agent's summary. The verification checklist from Step 4 is your success criterion.

*You've succeeded when:* You can show two consecutive run logs with commits visible on GitHub, Obsidian sync pulling the pages on both mornings, and no metadata violations. The checklist from Step 4 is your verification document — submit it filled in for both runs.

---

## Reflection Prompt

Karpathy's framing puts you in the editor's chair while the model writes, which is either the freeing end of note-taking drudgery or the outsourcing of the very synthesis that made notes valuable to write, depending on whom you ask.

**Personal level:** After running the loop yourself, which is it for you? Which kinds of pages do you want to keep writing by hand precisely because the writing is the thinking? Is there knowledge that becomes less yours if you let a model synthesize it?

**Technical level:** The wiki pattern makes a bet that long-context reasoning over connected pages is better than retrieval-augmented generation over embedded chunks, at personal scale. After this activity, do you believe that bet? What would change your mind — what evidence would convince you that RAG is better for your use case?

**Societal level:** Karpathy's pattern is explicitly personal — it is a tool for individual knowledge workers. But the same pattern could be applied to organizational knowledge at scale: a company's entire institutional memory maintained and queried by an LLM. What would be gained, and what would be lost, if institutional knowledge were managed this way? Who holds the schema layer, and what happens if they leave?

Write a combined reflection of 150–250 words addressing at least two of the three levels. The Reflector should be prepared to share which pages the team agreed to keep writing by hand.

[[___ Your reflection here ___]]

---

→ Coming Up Next: This is the final activity in the sequence. Return to your project repository and apply what you have built — the vault, the wiki, the published artifacts, and the deployed services — to your final project report and demo preparation.

---

## 6. Further Reading

- Andrej Karpathy, the LLM Wiki gist (gist.github.com/karpathy, April 2026): the pattern in its author's words; short, read it whole.
- W. Mongan, "A Private AI Knowledge Base" (billmongan.com, May 2026): the vault architecture this module builds on, including the AGENTS.md schema in full.
- Your own RAG lab writeup, reread: the strongest way to internalize the wiki-versus-RAG trade is to argue it against your own prior work.
