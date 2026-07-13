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

In April 2026, Andrej Karpathy published a short gist describing how he uses LLMs to build and maintain **personal knowledge bases**: not a product, not a framework, just a pattern, and one that lands squarely on the vault you built in the second brain module. His one-line summary of the division of labor: *the editor is the IDE, the LLM is the programmer, and the wiki is the codebase.* This module studies the pattern, contrasts it with the RAG architecture you built earlier this semester, and then tours the use cases that make the system earn its keep daily (a research wiki, journaling, meeting notes, raw paper summaries, and more), ending with the complete technical setup wired to hermes. The arc: **the pattern and its three layers → wiki versus RAG → the use-case tour → the full setup, end to end**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Prerequisite: the second brain module, with your vault standing; this module assumes the three-zone structure, the gitless sync, and the `AGENTS.md` contract and builds use cases on top of them. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Source layer** | The read-only zone where raw material lands exactly as it arrives — articles, transcripts, papers, exports — and is never edited after it is dropped in | Dropping a PDF of a research paper into `raw/papers/` without changing a single word of it |
| **Wiki layer** | The structured Markdown knowledge base that the LLM both reads and writes — organized into entity pages, concept pages, and hub indexes that grow and interlink as sources accumulate over time | The agent creates `wiki/research/transformers/attention-mechanisms.md` after processing three attention papers and links it from the relevant hub page |
| **Schema layer** | The instruction file (`AGENTS.md`) that tells the LLM exactly how to manage the wiki: what page types exist, how to link between pages, when to merge a new finding into an existing page versus create a new one, and how to handle conflicting sources | `AGENTS.md` specifies: "Each paper gets exactly one page under `wiki/papers/` with sections: claim, method, evidence, limitations, relevance" |
| **Lint (wiki lint)** | A periodic sweep where the LLM reads the entire wiki looking for contradictions between pages, orphaned pages that nothing links to, stale claims superseded by newer sources, and broken links — then either repairs them conservatively or flags them for human review | The lint pass finds that `wiki/research/topic-A.md` claims X while `wiki/research/topic-B.md` claims the opposite, and flags the conflict for you to resolve |
| **RAG (Retrieval-Augmented Generation)** | An architecture where a large corpus is broken into chunks, embedded as vectors, and searched at query time — the nearest chunks are retrieved and passed to the LLM as context for answering a question | Your RAG pipeline from earlier in the semester: embed all course documents into a vector store, retrieve the most relevant chunks for each question at query time |
| **Compounding knowledge** | The property of a well-maintained wiki where each new source makes all previous sources more useful, because the wiki accumulates cross-links and synthesized understanding rather than just appending more raw text | After ingesting 20 papers, asking "what are the open problems in X?" returns a synthesis drawing on all 20 papers' limitations sections — something no single paper or single chat session could provide |

---

# Part I: The Pattern

In this part, you will learn Karpathy's three-layer wiki architecture and understand why it differs from the RAG pipeline you built earlier — setting up the architectural choice you will reason through in Part II.

## 1. Three Layers and a Linter

Think of a well-curated wiki like a well-organized research notebook that writes its own index. When you finish reading a paper, you do not just file it away — you update your notes on the concept it addresses, add a cross-reference from the authors' names, and flag where it contradicts something you read last week. That is exactly what Karpathy's pattern automates: the LLM does the filing, cross-referencing, and contradiction-flagging, so you spend your time reading and asking questions rather than updating notes.

Karpathy's gist describes a deliberately simple architecture in three layers, and you will recognize all of them. The **Source layer** is read-only raw material: articles, transcripts, papers, exports, dropped in as they arrive and never edited (your `raw/`). The **Wiki layer** is the structured Markdown knowledge base the LLM reads *and writes*: entity pages, concept pages, cross-links, hub indexes, continuously grown and reorganized as sources accumulate (your `wiki/`). The **Schema layer** is the instruction file telling the LLM how to manage the wiki: what page types exist, how to link, when to merge versus create, how to handle conflicts between sources (your `AGENTS.md`, which the second brain module modeled directly on this gist). The inversion is the insight: **you stop being the person who writes and organizes notes and become the person who curates sources and asks questions**, while the LLM does the grunt work it genuinely does not mind — updating a dozen pages and every link among them without forgetting one.

The gist adds one maintenance idea worth adopting verbatim: **lint**. Periodically, the LLM sweeps the whole wiki looking for contradictions between pages, orphaned notes that nothing links to, stale claims superseded by newer sources, and broken links, and either repairs them or files them for your review. A knowledge base with a linter is a living system; one without is the same pile of notes you already abandoned in three other apps.

## 2. Wiki Versus RAG: A Real Architectural Choice

You built a RAG pipeline in this course: chunk the corpus, embed the chunks, retrieve the nearest few at query time, answer from fragments. Karpathy's pattern takes a pointed alternative position for the *personal* scale: rather than fragmenting knowledge into chunks and hoping retrieval reassembles the right ones, **maintain a curated, compressed wiki small enough that large portions of it fit in a long context window**, and let the model reason over connected pages rather than disconnected shards. The trade-offs are honest in both directions, and you have the vocabulary to weigh them now:

| Dimension | RAG | Wiki (Karpathy pattern) |
|-----------|-----|------------------------|
| **Scale** | Handles corpora of millions of documents — far more than any context window can hold, making it the only viable choice at large corpus scale | Tops out at personal-to-team scale — a few thousand pages, not millions; beyond that, curation cost becomes prohibitive |
| **Curation cost** | Minimal — chunk and embed automatically with no synthesis required; new documents are immediately available after indexing | Ongoing — each new source triggers a synthesis pass (mostly in agent tokens) to update concept pages, create cross-links, and resolve conflicts |
| **Query quality** | Depends on embedding quality and chunking strategy; retrieved chunks may be stripped of the connective tissue that gives them meaning in context | Reasons over connected pages with cross-links intact; better for questions that span multiple topics or require understanding relationships between ideas |
| **Human browsability** | The embedded chunks are not human-readable in a traditional sense — you cannot simply browse a vector store the way you browse a folder | The wiki *is* your Obsidian vault — you can browse it like a normal notebook, share pages with collaborators, and read it without running any queries |
| **Knowledge compounding** | Scales by adding more chunks; knowledge accumulates in the index but does not synthesize — each query starts fresh from retrieval | Knowledge genuinely compounds — later sources make earlier pages more useful, because the wiki records how ideas relate, not just what the ideas are |
| **Model error propagation** | A retrieval miss is an isolated failure that affects only one query | A synthesis error can propagate to many cross-linked pages before the lint pass catches it, making the schema's preserve-uncertainty rules load-bearing |

One more honest caution from the pattern's critics: the wiki is only as good as the model maintaining it, since a weak model can propagate a source's error into five confident pages. This is why the schema's preserve-uncertainty rules and the lint pass are load-bearing rather than decorative.

---

## Model 1: Choose the Architecture

Understanding the wiki-versus-RAG trade-off is not about memorizing which is better — it depends entirely on scale, curation capacity, and what kinds of questions you need to answer. Think of it like choosing between a card catalog (RAG: fast lookup, scales to any library size) and a personal research notebook (wiki: slower to maintain, but lets you see how your ideas connect). Work through the concrete cases below to develop your judgment about which tool fits which situation.

### Critical Thinking Questions

**Question 1.** For each corpus below, choose wiki, RAG, or a hybrid, and name the single most important deciding factor that drove your choice: (a) your own 200 accumulated course and research notes; (b) the full text of 40,000 arXiv papers; (c) your team's project decision log for a semester-long project; (d) a professor's 30 years of mixed-format files, most of which were never intended to be searched again.

*Hint:* For (a): Is 200 notes small enough to curate and synthesize? What kinds of cross-topic questions would you want to ask? For (b): Does any context window exist that could hold meaningful portions of 40,000 papers? What does that imply about your only option for scale? For (c): Is a semester decision log small enough to maintain as a wiki, and would you benefit from explicit links between related decisions? For (d): If most files will never be read again, is the per-source synthesis cost of a wiki justified — or would you rather pay only when you query?

**Question 2.** The wiki's "compression" is lossy by design: when the agent synthesizes a source into wiki pages, it necessarily discards some of the source's detail in favor of the structure the schema requires. Where does the pattern park the lost detail so it is not gone forever, and what does that imply about the one rule the Source layer must never break?

*Hint:* The lost detail stays permanently in the Source layer — the original raw files are never deleted or modified. If a wiki page turns out to be wrong (because of a synthesis error or a conflict between sources), you need to be able to return to the original source to adjudicate. Ask yourself: what happens to the system's trustworthiness if someone edits or deletes a file in `raw/`? The answer makes clear why "never edit the source layer" is the one rule that everything else depends on.

**Question 3.** Connect lint to a course concept: which evaluation idea from our LLM-as-judge unit is lint the knowledge-base version of, and what is lint's reward-hacking analog — that is, what would an agent do if it were optimizing for "making lint pass" rather than "making the wiki true"?

*Hint:* In the LLM-as-judge unit, we discussed the risk of an agent optimizing for the judge's rubric rather than for the underlying quality the rubric is meant to measure. Lint is a judge: it checks for contradictions, orphaned pages, and broken links. What would it look like for an agent to "pass lint" by making superficial changes that resolve the reported errors without actually making the wiki more accurate? For example, an agent could "resolve" a contradiction by deleting one of the conflicting claims — lint passes, but the wiki is now worse. What is the analog to Goodhart's Law here?

---

> With the architectural trade-offs mapped out, Part II tours the six concrete use cases that make the wiki pattern earn its place in a daily workflow — each one is just the same three-layer loop aimed at a different corner of your life or work.

# Part II: The Use-Case Tour

In this part, you will explore six concrete use cases — research wikis, journaling, meeting notes, and more — and design the specific naming conventions and page skeletons that make each one queryable months later.

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
- ( ) Shorter pages — consistent structure does not reduce page length; it organizes content into the same sections regardless of paper length
- (x) Comparability across many papers, so synthesis questions spanning the literature can be answered structurally rather than by rereading
- ( ) Compliance with Obsidian's internal format requirements — Obsidian imposes no required heading structure; the skeleton is a schema choice, not a tool requirement
- ( ) Faster PDF parsing — the skeleton is applied after parsing, not during; it affects how results are stored, not how fast the source is read

---

## Model 2: Design Your Corner

Each teammate picks one use case from the tour (no duplicates within a team). The goal is to arrive at conventions specific enough that you could hand them to someone else — or to the agent — and they would know exactly what to do without asking you any clarifying questions. Think of this like writing a recipe: a recipe that says "add some flour" is useless, but one that says "add 2 cups of all-purpose flour, sifted" is something a stranger can follow. Your conventions need to be that specific.

### Critical Thinking Questions

**Question 4.** Specify your use case's conventions in four lines: (a) the `raw/` drop convention — where to put sources and what to name them; (b) the `wiki/` directory path and page-naming scheme — what the folder structure looks like and how individual pages are named; (c) the page skeleton — the exact section headings that every page in this use case must contain; and (d) the one standing prompt that the agent runs to process new sources and maintain the wiki. The Recorder collects all four sets from the team.

*Hint:* Be specific enough that the conventions are mechanical and leave no room for interpretation. "Drop papers in `raw/papers/` with the filename format `lastname2026-shorttitle.pdf`" is specific enough that anyone can follow it. "Put papers somewhere" is not. The page skeleton should list exact section headings (using Markdown `##` syntax), because if two pages in the same use case have different headings, the agent cannot answer comparative questions structurally.

**Question 5.** Name the one question you most want your corner of the wiki to be able to answer by December, and then work backward from that question to verify that your conventions from Question 4 actually capture all the inputs that question requires. If your conventions do not capture the required inputs, revise them until they do.

*Hint:* If your December question is "which papers in my research wiki disagree about approach X?" then your page skeleton must have a section that explicitly records each paper's position on approach X — not just a general "summary" section, because a summary might or might not mention the paper's stance on X. Work backward from the question to the required data, then check that the required data appears in your skeleton. If it does not, add a section for it.

**Question 6.** Identify the privacy boundary your use case comes closest to crossing — journaling and meeting notes are the most sensitive, since they often contain information about other people who have not consented to being in your AI-maintained vault — and write down the one inclusion rule you will follow, stated as a single enforceable sentence.

*Hint:* An enforceable inclusion rule is one you can check before every single drop, without relying on judgment calls made under time pressure. "I will include all meeting notes" is not enforceable, because it does not handle the edge case of a meeting where sensitive personnel or legal matters were discussed. "I will include meeting notes only from meetings where all attendees were told in advance that notes may be processed by an AI system, and where no HR, legal, or confidential business matters were discussed" is enforceable — you can check every item on that list before dropping a file into `raw/`.

---

> **⚠️ Common Misconception:** Many students assume that adding more sources to the vault automatically makes it more useful and reliable. This is only true if the agent synthesizes them faithfully and the lint pass catches errors promptly. A wiki maintained by a model that is not well-prompted, or one that runs without a lint pass, can actually become *less* reliable as sources accumulate — because each synthesis error gets cross-linked into more and more pages, making the error harder to trace and correct. The discipline is not in adding sources. The discipline is in writing a precise schema (the `AGENTS.md` contract) and running lint regularly to keep the synthesis honest. More sources with a weak schema is worse than fewer sources with a strong one.

---

> With your use-case conventions designed, Part III walks you through the four setup steps that wire those conventions into a living system — from extending the schema to scheduling the nightly ingestion loop.

# Part III: The Setup, End to End

In this part, you will extend your AGENTS.md schema, seed the wiki with real sources, and schedule the nightly ingestion loop — by the end, your vault will update itself while you sleep.

## 4. From Standing Vault to Living Wiki

Everything below assumes the second brain module's foundation (private repository, gitless sync with your PAT, three zones, `AGENTS.md` with the metadata protocol). The LLM Wiki additions are four steps.

**Step 1: extend the schema.** Append a use-case section to `AGENTS.md` declaring your conventions from Model 2, the lint specification (sweep for contradictions, orphans, staleness, broken links; repair conservatively; write a report to the repository root; flag ambiguous repairs for human review rather than applying them), and the page-skeleton definitions. The schema layer is where the pattern lives; an undocumented convention does not exist.

**Step 2: seed the wiki.** Drop three to five real sources into `raw/` (a paper PDF, a meeting transcript, last week's journal entries) and run the ingestion prompt against hermes:

The prompt below tells hermes to clone your vault, read AGENTS.md, and process every unprocessed file in raw/ — run this once and watch the wiki/ directory fill with structured pages.

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

*What to do:* Open `AGENTS.md` in your vault. Add a new section titled `## Use-Case: [Your Use Case Name]` with the four convention lines from Question 4 — raw drop convention, wiki directory and naming scheme, page skeleton with exact section headings, and the standing prompt. Then add a `## Lint Specification` section with the lint behavior described in Step 1 above (sweep targets, conservative repair policy, report location, and the flag-rather-than-apply rule for ambiguous cases).

*Starter hint:* The example below shows the exact Markdown structure your use-case section should follow — copy the skeleton and fill in your own conventions, replacing "Research Wiki" with your chosen use case.

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

*You've succeeded when:* `AGENTS.md` in your repository includes your full use-case section and lint specification, the commit is visible on GitHub, and the conventions are specific enough that a teammate who has never seen your vault could follow them without asking you any clarifying questions. Submit the diff of your `AGENTS.md` changes.

---

**Exercise 2.** Seed and ingest. Execute Steps 2 and 4 with real sources, and submit the agent's commit log, one resulting wiki page, and the answer to your December question's nearest present-day approximation with the wiki pages it cited.

*What to do:* Drop three real sources that belong to your use case into the appropriate `raw/` subfolder. Run the ingestion prompt from Step 2 against hermes, substituting your GitHub username. After the agent commits, pull the repository in Obsidian and verify the new wiki pages appear with the correct skeleton structure. Then run the query prompt from Step 4 using the closest approximation of your December question that you can answer now with the sources you have seeded.

*Starter hint:* Use the exact ingestion prompt from Step 2 above, substituting your GitHub username. After the agent commits, pull in Obsidian and verify the new wiki pages appear. Then run: *"Using the vault per AGENTS.md, answer from wiki/ first: [your question]. If raw/ holds newer relevant material, update the wiki before answering."* The answer should cite specific wiki page paths, not raw file paths.

*You've succeeded when:* The agent's response to your question cites specific wiki pages by their full path (for example, `wiki/papers/smith2025-attention.md`) rather than raw files, and those pages exist in your repository with the correct skeleton section headings from Question 4.

---

**Exercise 3.** Paper pipeline. Ingest two related papers using the fixed skeleton convention, then ask the cross-paper synthesis question: "Where do these two papers disagree with each other, and what additional evidence would be needed to settle the disagreement?" Evaluate the quality and groundedness of the answer using your judge-calibration instincts from earlier in the semester.

*What to do:* Drop two papers on the same topic into `raw/papers/`. Run the ingestion prompt to create both wiki pages and thread them into the relevant concept pages. Then run the cross-paper question. For each substantive claim in the answer, check whether there is a specific sentence in the corresponding wiki page section that supports it.

*Starter hint:* A well-grounded answer cites specific page paths and section headings, such as: "According to `wiki/papers/smith2025-attention.md#Limitations`, the method does not generalize beyond the domain it was trained on, while `wiki/papers/jones2025-scaling.md#Evidence` shows the opposite pattern in a multi-domain setting." An ungrounded answer synthesizes from the model's general knowledge: "In general, these approaches tend to differ in their generalization behavior." The former is what you are looking for.

*You've succeeded when:* You can label each substantive sentence in the cross-paper answer as either "grounded" (traceable to a specific section of a specific wiki page) or "ungrounded" (synthesized without a traceable source), and at least 80% of the answer's substantive claims are grounded in your wiki pages.

---

**Exercise 4.** First lint. Deliberately plant one contradiction and one orphan page in your wiki, run the lint pass, and grade the agent's lint report and repairs.

*What to do:* Edit one existing wiki page to assert something that directly contradicts a claim on another page about the same topic. Then create a new wiki page that is not linked from any other page (the orphan). Run the lint pass with this prompt: *"Run the lint pass specified in AGENTS.md. Report everything you found and describe every change you made. Flag anything you were unsure about rather than applying a repair automatically."* Then compare the report to what you planted.

*Starter hint:* Good lint behavior looks like this: the agent finds both the contradiction and the orphan, repairs the orphan by adding a link from the most relevant hub or concept page, and flags the contradiction for human review with both conflicting statements quoted verbatim — rather than silently picking one. Bad lint behavior: silently resolving the contradiction by deleting one of the claims without flagging it (bulldozing), or failing to find either the contradiction or the orphan entirely.

*You've succeeded when:* You can write a two-sentence verdict that specifically names what the lint pass got right and what it missed or mishandled. For example: "The agent correctly identified the orphan page and linked it from the topic hub index. It found the contradiction but silently deleted one claim rather than flagging it — the schema requires flag-and-report, not silent deletion, so this is a repair policy violation."

---

**Exercise 5.** Schedule it. Build the n8n nightly-ingest workflow, let it run on two consecutive nights, and submit evidence that both runs completed correctly.

*What to do:* In n8n, create a scheduled workflow that fires each night and runs the ingestion prompt against hermes. After each of two consecutive nights, check the following: (a) did the run produce a new commit on GitHub with wiki pages and metadata entries? (b) do the new pages have the correct skeleton structure? (c) did Obsidian sync pull the new pages by the next morning? (d) are there any metadata protocol violations in the commit?

*Starter hint:* A minimal n8n workflow for this has three nodes: a Schedule trigger (set to nightly at a time you will remember to check), an HTTP Request node that calls the hermes API with the ingestion prompt as the request body, and a notification node (Slack message or email) that forwards the agent's summary so you know each morning what the agent did overnight. The verification checklist from Step 4 above is your success criterion — treat each item on the checklist as a row in your submission.

*You've succeeded when:* You can show two consecutive run logs with commits visible on GitHub timestamped on two different nights, Obsidian pulling the new pages on both mornings, no metadata violations in either commit, and a filled-in verification checklist from Step 4 covering both runs. The checklist itself is your monitoring design — submit it as part of your response.

---

## Reflection Prompt

Karpathy's framing puts you in the editor's chair while the model writes, which is either the freeing end of note-taking drudgery or the outsourcing of the very synthesis that made notes valuable to write, depending on whom you ask.

**Personal level:** After running the loop yourself, which is it for you — liberation or loss? Which kinds of pages do you want to keep writing by hand, precisely because the writing is the thinking and the thinking is the point? Is there knowledge that becomes less *yours* if you let a model synthesize it — and if so, how do you recognize it in advance?

**Technical level:** The wiki pattern makes a concrete bet: that long-context reasoning over a curated, connected set of pages is better than retrieval-augmented generation over embedded chunks, at personal scale. After this activity, do you believe that bet for your use case? What specific evidence from today's exercises supports your view? What evidence would change your mind — what result would convince you that RAG is actually the better choice for your particular use case?

**Societal level:** Karpathy's pattern is explicitly personal — it is a tool for individual knowledge workers who maintain their own vault. But the same pattern could be applied to organizational knowledge at scale: a company's entire institutional memory, maintained and queried by an LLM agent operating on a shared schema. What would be gained by doing that, and what would be irreversibly lost? Who holds the schema layer in an organizational setting, and what happens to the institution's knowledge when that person leaves?

Write a combined reflection of 150–250 words addressing at least two of the three levels above. The Reflector should be prepared to share which pages the team agreed to keep writing by hand, and why.

---

→ Coming Up Next: This is the final activity in the sequence. Return to your project repository and apply what you have built — the vault, the wiki, the published artifacts, and the deployed services — to your final project report and demo preparation. Carry your `AGENTS.md` schema, your first lint report, and the answer from Exercise 2 into that project work as evidence of a living system.

---

## 6. Further Reading

- Andrej Karpathy, the LLM Wiki gist (gist.github.com/karpathy, April 2026): the pattern in its author's words; it is short and worth reading in full before you extend your schema.
- W. Mongan, "A Private AI Knowledge Base" (billmongan.com, May 2026): the vault architecture this module builds on, including the complete `AGENTS.md` schema that the second brain module introduced.
- Your own RAG lab writeup, reread with fresh eyes: the strongest way to internalize the wiki-versus-RAG trade-off is to argue it against your own prior work — take the position that your RAG pipeline was wrong for your use case and see how far the argument holds.
