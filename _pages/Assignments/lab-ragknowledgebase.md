---
layout: assignment
permalink: /Assignments/RAGKnowledgeBase
title: "CS357: Foundations of Artificial Intelligence - Lab 2: A RAG Knowledge Base of Your Own"

info:
  coursenum: CS357
  points: 100
  goals:
    - To construct a complete retrieval-augmented generation pipeline over a personal document corpus using Chroma and a local model
    - To make and defend chunking decisions empirically
    - To evaluate retrieval quality with recall at k and grounding quality with a citation audit
    - To implement honest abstention when the corpus does not contain an answer
  rubric:
    - weight: 30
      description: Pipeline Implementation
      preemerging: The pipeline fails to index or query due to major issues, or the program fails to run
      beginning: The pipeline runs but fails on test questions due to one or more minor issues
      progressing: The pipeline indexes and answers correctly with citations, but a component such as abstention or configuration is fragile or incomplete
      proficient: The pipeline indexes, retrieves, answers with citations, and abstains honestly, with configuration externalized and exceptions handled with located messages and tracebacks
    - weight: 25
      description: Chunking Strategy and Justification
      preemerging: A single arbitrary chunking is used without discussion
      beginning: A chunking choice is stated but not compared against an alternative
      progressing: Two chunking strategies are compared on a small question set with results reported
      proficient: At least two chunking strategies are compared on a defined question set, recall at k is reported for each, and the shipped choice is defended quantitatively
    - weight: 25
      description: Evaluation and Citation Audit
      preemerging: No evaluation is provided
      beginning: Informal trials are described without a protocol or metric
      progressing: A question set with recall at k and an answer accuracy measure is evaluated, with limited citation auditing
      proficient: A question set is evaluated with recall at k and answer accuracy, every citation in a sample of at least ten answers is audited by hand for faithfulness, and a faithfulness rate is reported with examples of any failures
    - weight: 10
      description: Code Quality and Documentation
      preemerging: Code commenting and structure are absent, or code structure departs significantly from best practice
      beginning: Code commenting and structure is limited in ways that reduce the readability of the program
      progressing: Code documentation is present that re-states the explicit code definitions
      proficient: Code is documented at non-trivial points in a manner that enhances the readability of the program
    - weight: 10
      description: Writeup, Reflection, and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup, the pair programming log, a corpus datasheet, and thoughtful answers to the reflection prompts
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

## Part 1: Curate and Document Your Corpus

Assemble a corpus of at least 15 documents or pages (markdown, text, or extracted PDF text). **You may not use any document containing another person's private information**; if your corpus involves anything sensitive, the local-only nature of this pipeline is your friend, and your writeup must say so explicitly. Write a half-page **datasheet**: sources, time range, who and what is represented, who and what is absent, and known limitations.

## Part 2: Index with Intent

Implement indexing with **two chunking strategies** (for example, fixed-size with overlap versus paragraph-structural), with chunk parameters externalized in a JSON configuration file. Build a question set of at least ten questions whose answers you have located by hand (note the source chunk for each). Report **recall@k** for $k \in \{1, 3, 5\}$ under both strategies, and choose your shipped configuration with a quantitative defense.

## Part 3: Grounded Generation

Implement the query path: embed the question, retrieve top-k, assemble a prompt that instructs the model to answer **only** from the provided context, to cite bracketed source numbers, and to reply with a designated abstention phrase when the context is insufficient. Demonstrate:

- Five answered questions with correct citations.
- Two honest abstentions on questions your corpus cannot answer.
- One before/after comparison showing the bare model hallucinating where your RAG system either answers correctly or abstains.

## Part 4: Audit

For at least ten answered questions, audit each citation by hand: does the cited chunk actually support the claim? Report a **faithfulness rate** and show any failures verbatim, classified using the hallucination taxonomy from class.

## Deliverables

Submit a ZIP containing your code, JSON configuration, corpus (or a pointer plus a sample if it is large), datasheet, question set with labels, evaluation results (CSV or table), audit results, pair log, and a readme writeup of approximately two pages. Ensure reproducibility by fixing random seeds and listing software version information.

## Reflection Prompts

- Which failure did you find more often: retrieval fetching the wrong chunk, or generation misusing a correct chunk? What does that imply about where to invest next?
- Your corpus datasheet names who is absent from your documents. How could that absence shape the answers your system gives?
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
