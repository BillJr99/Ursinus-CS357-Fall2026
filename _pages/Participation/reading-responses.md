---
layout: assignment
permalink: /Participation/ReadingResponses
title: "CS357: Foundations of Artificial Intelligence - Reading Responses and Discussion Prompts"

info:
  coursenum: CS357
  points: 10
  submission: "Post brief responses to the class discussion board before the marked sessions. These are low-stakes preparation, assessed as part of the 10% Class Activities and Participation component."
  goals:
    - To engage each reading or result actively before class, connecting it to systems you run yourself
    - To arrive at discussion days and student-led Reading Group sessions ready to contribute
    - To give presenters an engaged audience and earn participation as a member of it
  rubric:
    - weight: 30
      description: "Takeaway — the single most important claim or result, in your own words"
      preemerging: "No takeaway, or the response only restates the title or a whole-thing summary."
      beginning: "A takeaway is present but is a broad summary rather than the one claim that matters, or is copied wording."
      progressing: "Identifies the single most important claim or result in your own words, accurately."
      proficient: "Identifies the key claim precisely and in your own words, and signals why it is the one that matters over the others."
    - weight: 25
      description: "Question — a real, answerable question the reading raised"
      preemerging: "No question, or a question answered directly by the text (recall only)."
      beginning: "An open question, but generic — it could be asked of almost any reading."
      progressing: "A genuine question specific to this reading: something you doubt, something unresolved, or something you would test."
      proficient: "A sharp question that names the assumption or evidence in doubt and suggests how it could be resolved or tested."
    - weight: 30
      description: "Connection to your own system — tie the reading to something you run or could run"
      preemerging: "No connection to a system you operate."
      beginning: "A vague gesture at relevance with no specific system, configuration, or decision named."
      progressing: "Ties the reading to a concrete system you run or could run (local model, RAG corpus, MCP server, agent eval) and names one thing it would change."
      proficient: "Names the specific change and its consequence — how you would reconfigure, chunk, scope, or evaluate differently, and what it would cost or risk."
    - weight: 15
      description: "Timeliness and engagement — posted before the marked session, ready to contribute"
      preemerging: "Not posted, or posted after the session."
      beginning: "Posted, but so late or thin that it does not prepare you to contribute."
      progressing: "Posted before the session in the three-sentence form, ready to bring to discussion."
      proficient: "Posted before the session and framed so a presenter or peer could build on it directly in the room."

tags:
  - resource
  - exercises

---

An agent you have only read about is one you cannot yet debug, and a paper you have only skimmed is one you cannot yet discuss. A reading response is a short note — three or four sentences — that you write *before* a discussion day or a classmate's Reading Group session, so that you arrive with something to say and the conversation starts from real engagement rather than a cold open. This page explains how to write one, how they earn participation, and gives a bank of reading-linked prompts for each unit.

## Purpose

Reading responses do two things. They make you an active reader — turning a passive skim into a takeaway, a question, and a connection — and they make you a good audience, which is half of what a seminar-style discussion needs. When a classmate leads a Reading Group session, their session is only as good as the room; your response is how you hold up your end, and it is part of your participation grade.

## How to Write a Reading Response

Keep it to three or four sentences, posted to the discussion board before the marked session. A strong response has three moves:

1. **One takeaway.** The single most important claim or result, in your own words — not a summary of the whole thing.
2. **One question.** A real question the reading raised for you: something you doubt, something unresolved, or something you would test.
3. **One connection to your own system.** This is the move that matters most in this course: tie the reading to something you run or could run yourself. Does this change how you would configure your local model, chunk your RAG corpus, scope an MCP server's permissions, or evaluate an agent's output? The goal of the course is fluency operating your own AI stack, and reading responses are where reading becomes that fluency.

## Reading Responses for Student-Led Reading Group Sessions

When a classmate leads a [Reading Group](Assignments/ReadingGroup) discussion, the audience has a defined job, and doing it earns participation. Before the session, post a brief response to the presenter's source (or, if it is circulated same-day, come with one genuine question ready). During the session, engage: build on the presenter's framing, offer a counter-view, or connect their source to something we have built. Leading a session remains separately available for extra credit; being a strong audience member is ordinary, expected participation — and it is what makes the student-led sessions worth holding.

## Reading-Linked Prompts, by Unit

Use these when a reading response is due, or any time you want to prepare a unit actively. Each ties the reading to a system you operate.

### The Agent Loop and Local Models

- After setting up a local model, write what changed in your mental model of "using AI" once the model was running on your own machine, with no network. What became possible, and what became your responsibility?
- Name one task you would trust a local 7B model with and one you would not, and say what the difference is.

### Prompting, Sampling, and Generation

- Change one sampling parameter (temperature or top-p) on a prompt you care about and report what shifted. What does the change tell you about why the model is not a database?
- Write a system prompt that makes a local model refuse a task it should refuse. What did you have to say, and how brittle is it?

### Tokens, Embeddings, and RAG

- Chunk a small corpus two different ways and describe how retrieval quality changed. Which failure did each chunking cause?
- Find one query where your RAG pipeline retrieved the right passage but the model still answered wrongly. Whose fault was it — retrieval or generation — and how do you know?

### Memory, Tools, and MCP

- For a tool or MCP server you wired up, write the smallest set of permissions it actually needs. What is the blast radius if its token leaks?
- Describe one thing your agent got wrong because its context window was full of the wrong things. What would you evict?

### Multi-Agent Orchestration and Evaluation

- Run the same task through a single agent and through a critique-and-refine pair. Where did the second design help, and where did it just cost tokens?
- Write one rubric criterion precise enough that an LLM-as-judge and a human would grade it the same way. Why is that hard?

### Responsibility, Bias, Privacy, and Environmental Impact

- For a reading on bias, governance, or environmental cost, name one design choice *you* would make differently in a system you deploy, and what it would cost you.
- Take a claim from the reading and steelman the strongest objection to it, anchored in something concrete — a dataset, a benchmark, or a deployment you know.

## See also

- [Reading Group Discussion Leader]({{ site.baseurl }}/Assignments/ReadingGroup) — leading a session, and the audience's role.
