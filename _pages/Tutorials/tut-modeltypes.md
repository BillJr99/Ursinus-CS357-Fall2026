---
layout: default-standard
permalink: /Tutorials/ModelTypes
title: 'CS357: Foundations of Artificial Intelligence - Model Types and the Model Lifecycle'
info:
  coursenum: CS357
  purpose: "To read a model picker correctly: base, instruct, reasoning, and vision are labels for where a model stopped along a training pipeline, not marketing adjectives."
tags:
- models
- lifecycle
- reasoning
---
# CS357: Foundations of Artificial Intelligence - Model Types and the Model Lifecycle

## Purpose

To read a model picker correctly: base, instruct, reasoning, and vision are labels for where a model stopped along a training pipeline, not marketing adjectives.

## About This Tutorial

When you open a model picker and see names like *base*, *instruct*, *reasoning*, or *vision*, those are not marketing adjectives; they are labels for **where a model stopped along a training pipeline**.  Every one of them begins life as the same thing: a next-token predictor.  What separates a chatbot from a "thinking" model from a model that can read a screenshot is which additional training stages were applied, and in what order.  This tutorial is the **hub** that ties together pieces the course teaches separately (pretraining, alignment, fine-tuning, and multimodality) into one lifecycle you can reason about.  When you need the mechanics of any single stage, we point you to the deep-dive activity that covers it.

Our arc: **pretraining $\rightarrow$ supervised fine-tuning $\rightarrow$ preference alignment $\rightarrow$ reasoning training $\rightarrow$ multimodal training**, and then a taxonomy that lets you *choose* the right model type for a task instead of guessing.

## Key Concepts

| Term | Plain-English Definition | Where It Shows Up Today |
|------|--------------------------|-------------------------|
| **Base model** | A raw next-token predictor produced by pretraining; it *continues* text but does not reliably follow instructions | The starting point of the lifecycle in Part I |
| **Instruct / chat model** | A base model further trained on example (instruction, response) pairs so it answers rather than autocompletes | The model you talk to in most chat apps |
| **Preference alignment** | Adjusting a model toward responses humans prefer, via RLHF or DPO | The polish step that makes answers helpful and safe |
| **Reasoning model** | A model trained (often by RL on checkable answers) to generate a long intermediate chain of thought before its final answer | The "thinking" models in Part II |
| **Chain-of-thought (CoT)** | Intermediate reasoning written out as generated tokens, which condition the tokens that follow | The mechanism behind "think step by step" |
| **Test-time compute** | Spending more inference tokens/time on a single query to get a better answer | The cost/quality dial in Part II |
| **Vision / multimodal model** | A model with an image encoder that projects pixels into the token stream, trained on image-text pairs | The short tour in Part III |

---

# Part I: The Model Lifecycle

In this part you build one clean mental model: a single pipeline of training stages, where **each stage produces a recognizable *kind* of model**.  Understanding the pipeline is what lets you read a model card and know what you are getting.

## 1.  From Base Model to Assistant

**Why this matters:** People often talk about "the model" as if there were one artifact.  In reality, the model you use is a *snapshot* taken after a specific sequence of training stages.  Knowing which stages ran tells you what the model is good at, how it will behave, and what it will cost.

The pipeline, stage by stage:

**Pretraining (-> a *base* model).**  The model is trained on a huge corpus to predict the next token.  This is where nearly all world knowledge and language ability is absorbed.  The output is a *base* model: fluent, knowledgeable, but not obedient; ask it a question and it may continue your question rather than answer it.  The mechanics of tokenization, the next-token objective, and scaling are covered in depth in the pretraining activity.

**Supervised fine-tuning / instruction tuning (-> an *instruct/chat* model).**  The base model is trained further on curated (instruction, response) pairs written or vetted by humans.  This teaches the *format* of being helpful: read a request, produce a direct, useful answer.  The result is an *instruct* or *chat* model, the kind most applications talk to.

**Preference alignment (-> a better-behaved instruct model).**  Even a well-instruction-tuned model produces answers of uneven quality.  Alignment methods, **RLHF** (reinforcement learning from human feedback) and its simpler cousin **DPO** (direct preference optimization), nudge the model toward responses humans rate higher and away from unhelpful or unsafe ones.  The RL and RLHF/DPO mechanics are covered in the RLHF activity.

**Reasoning training (-> a *reasoning* model).**  Optionally, the model is trained with reinforcement learning on problems that have **checkable** answers (math, code, logic puzzles), rewarding it when a long, correct chain of thought leads to the right final answer.  The model learns to *spend tokens thinking* before it commits.  The result is a *reasoning* model.  This is Part II.

**Multimodal training (-> a *vision/multimodal* model).**  Separately (and often layered on top of an instruct model), a **vision encoder** is trained and connected via a **projection layer** so that images become tokens the language model can attend to, using image-text pairs.  The result is a *vision* or *multimodal* model.  This is Part III, with the deep dive in the multimodal agents activity.

A key idea: these stages are **cumulative and modular**.  A reasoning model is still an instruct model underneath; a vision model is usually an aligned instruct model with an image path bolted on.  "Model type" is really "how far down the pipeline this snapshot was taken, and which optional branches it took."

---

## The Training Pipeline

Read the pipeline top to bottom.  Each row is a training stage; the "Model type produced" column names what you get if training *stops* there.

| Stage | What it optimizes | Model type produced | Deep-dive activity |
|-------|-------------------|---------------------|--------------------|
| Pretraining | Next-token prediction on a huge corpus | **Base** model (fluent, not obedient) | *LLM Pretraining* |
| Supervised fine-tuning | Imitating good (instruction -> response) pairs | **Instruct / chat** model | *Fine-Tuning vs. RAG* |
| Preference alignment (RLHF / DPO) | Matching human preference rankings | Aligned **instruct** model | *RL and RLHF* |
| Reasoning training (RL on verifiable rewards) | Long chains of thought that reach correct answers | **Reasoning** model | Part II (below) |
| Multimodal training (encoder + projection) | Aligning image tokens with text on image-text pairs | **Vision / multimodal** model | *Multimodal Agents* |

```text
                    +-------------+
   huge text corpus | PRETRAINING |--> base model (autocomplete)
                    `-------------+
                           |  supervised fine-tuning
                           v
                     instruct / chat model
                           |  RLHF / DPO
                           v
                   aligned instruct model -------+
                     |                            |  + vision encoder
   RL on checkable   |                            |  + projection layer
   answers           v                            v
              reasoning model              vision / multimodal model
```

### Questions to Work Through

**Q1.**  A colleague downloads a "base" model and is frustrated that when they type "What is the capital of France?" it responds with "What is the capital of Germany?  What is the capital of Spain?" instead of answering.  Using the pipeline above, explain exactly which training stage they are missing and why the base model behaves this way.

> *Hint: Pretraining optimizes only next-token prediction on raw text.  In web text, a question is very often followed by *more questions* (quizzes, lists), not by an answer.  The base model is faithfully continuing the pattern it learned.  The missing stage is supervised fine-tuning / instruction tuning, which teaches the model that an instruction should be followed by a helpful response, not by more instructions.*

**Q2.**  Argue for or against this claim: "A reasoning model and a vision model are fundamentally different architectures."  Use the modular view of the pipeline in your answer.

> *Hint: Both usually start from the same aligned instruct model, same transformer backbone.  A reasoning model adds a *training* stage (RL on checkable answers) that changes behavior, not architecture.  A vision model adds *components* (an image encoder and a projection layer) that feed extra tokens into the same backbone.  So "fundamentally different architectures" overstates it: they are the same core model with different optional branches attached.  The interesting differences are in training data and objective, not a from-scratch redesign.*

---

# Part II: What "Thinking" Means

This is the part the rest of the course does not cover head-on, so we go slowly.  The goal is to demystify "thinking" and "reasoning" models: what they actually do, when the extra cost is worth it, and what misconception to avoid.

## 2.  Chain-of-Thought and Reasoning Models

**Why this matters:** "Reasoning" models are marketed as if the model literally sits and ponders.  That framing leads to bad decisions: paying premium prices for tasks that gain nothing, or distrusting the visible "thinking" as if it were a transcript of a mind.  A precise picture lets you choose deliberately.

Chain-of-thought is just generated tokens.  When a model "reasons," it is doing the *only* thing it can do: generating tokens, one at a time, left to right.  The trick is that the intermediate tokens it generates ("First, let me find the total... that's 12... now divide by 3...") become part of the context for the *next* tokens.  The model is, in effect, writing notes to itself that it then reads.  More reasoning tokens means more intermediate results the final-answer tokens can condition on.  There is no separate "thinking module"; the reasoning *is* text the model produces and then attends to.

**Bust the misconception.**  The model does not "ponder" in silence and then speak.  It has no hidden scratchpad of thought that exists apart from tokens.  When we say a model "thinks longer," we mean **it generates more tokens before emitting the final answer**, and those tokens change the probability distribution over what comes next.  If you prevent it from writing intermediate steps, you remove the very mechanism that was helping it.

**What makes a "reasoning" model.**  A plain instruct model *can* be prompted to think step by step.  A **reasoning model** has been *trained*, typically with reinforcement learning on problems whose answers can be automatically checked (math, code, logic), to produce long, useful chains of thought *by default* and to keep them on track toward a correct final answer.  It has learned that spending tokens on reasoning pays off, and how to structure that reasoning.  (This is the same RL-on-rewards machinery as the RLHF activity, but here the reward is "did you get the verifiable answer right?" rather than "did a human prefer this?")

**Visible vs. hidden ("thinking") tokens.**  Many reasoning models separate their output into a *thinking* segment and a *final answer*.  Some products hide the thinking tokens from the user (you are billed for them but do not see them); others show them.  Either way, those tokens are generated, they consume compute, and they condition the answer.

**Test-time compute.**  The dial that reasoning models turn is **test-time compute**: spending more inference tokens/time on a single query to get a better answer.  This is different from training-time compute (spent once, up front).  Test-time compute is paid *every query*.  For hard problems, letting the model generate more reasoning tokens improves accuracy.  For easy problems, it mostly burns money and latency.

**When reasoning models earn their cost:** multi-step math, program synthesis and debugging, planning problems, anything where a single misstep cascades and where the answer can be checked or self-corrected.

**When they do not:** simple factual lookups, short rewrites, classification, and latency-sensitive chat.  Here a fast instruct model is cheaper and often just as accurate, and the reasoning model's long internal monologue adds seconds and cost for no benefit.

---

## The Test-Time Compute Dial

| Query | Does more reasoning help? | Better choice | Why |
|-------|---------------------------|---------------|-----|
| "What's the capital of France?" | No | Fast instruct model | Single-fact lookup; extra tokens change nothing |
| "A train leaves at 2:15 going 60 mph..." | Yes | Reasoning model | Multi-step; intermediate results must be tracked |
| "Fix this failing function and explain the bug" | Yes | Reasoning model | Errors cascade; self-checking pays off |
| "Rephrase this sentence more politely" | No | Fast instruct model | One-shot transformation; latency matters |
| "Plan a 5-stop trip within budget and time" | Yes | Reasoning model | Constraint satisfaction over many steps |

The code cell below makes the mechanism concrete.  It sends the *same* arithmetic-heavy word problem to a local model two ways: once asking for the answer directly, and once asking it to think step by step first.  Watch how the number of intermediate tokens can change the final answer.  Uses the course's `chat(messages)` convention over an OpenAI-compatible local endpoint; run it locally against your running model.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python

# Direct answer vs. "think step by step" against a LOCAL model.

# Shows that generating reasoning tokens can change the final answer.

# Uses an OpenAI-compatible local endpoint (Ollama's /v1, LiteLLM, etc.).

import requests

BASE_URL = "http://localhost:11434/v1/chat/completions"  # OpenAI-compatible
MODEL    = "llama3.2"
API_KEY  = "ollama"  # local servers ignore this, but the header must exist

def chat(messages, temperature=0.0):
    """Send a message list to a local OpenAI-compatible server; return the reply text."""
    try:
        r = requests.post(
            BASE_URL,
            headers={"Authorization": f"Bearer {API_KEY}",
                     "Content-Type": "application/json"},
            json={"model": MODEL, "messages": messages,
                  "temperature": temperature},
            timeout=180,
        )
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[modeltypes:chat] {e}")
        return ""

# A problem that rewards tracking intermediate results.
problem = (
    "A class has 3 rows of desks. The first row has 7 desks, the second "
    "has 5 more than the first, and the third has twice as many as the "
    "second. If 4 desks are broken and removed, how many usable desks remain?"
)

# --- Condition A: force a DIRECT answer (few / no reasoning tokens) ---
direct = chat([
    {"role": "system",
     "content": "Answer with ONLY the final number. No explanation."},
    {"role": "user", "content": problem},
])

# --- Condition B: ask for a chain of thought BEFORE the answer ---
reasoned = chat([
    {"role": "system",
     "content": "Think step by step. Show each intermediate count, "
                "then write 'ANSWER:' followed by the final number."},
    {"role": "user", "content": problem},
])

print("=== DIRECT (minimal reasoning tokens) ===")
print(direct.strip(), "\n")
print("=== STEP BY STEP (many reasoning tokens) ===")
print(reasoned.strip(), "\n")

# Correct answer, for your reference while grading the two conditions:

#   row1 = 7 ; row2 = 7 + 5 = 12 ; row3 = 2 * 12 = 24

#   total = 7 + 12 + 24 = 43 ; usable = 43 - 4 = 39
print("Ground truth: 39")
print()
print("=== STUDENT EXERCISES ===")
print("1. Run several times. Does DIRECT ever get 39? Does STEP BY STEP?")
print("2. The reasoning tokens are what the model 'reads back' to itself.")
print("   Delete the intermediate steps from B's prompt and re-run.")
print("3. Try an easy prompt ('capital of France'). Do the reasoning")
print("   tokens change the answer, or only the latency and token cost?")
```

### Questions to Work Through

**Q3.**  A student says: "The reasoning model pauses and *thinks* about the problem, then tells me the answer; the thinking is separate from the words."  Correct this using the mechanics of token generation.  What is the thinking *made of*, and what would happen if you forbade the model from producing intermediate tokens?

> *Hint: The "thinking" is not separate from the words; it *is* words (tokens) the model generates and then attends to when producing later tokens.  There is no hidden pondering apart from token generation.  If you forbid intermediate tokens (e.g., "answer with only the number"), you remove the mechanism that let the model track intermediate results, and accuracy on multi-step problems typically drops.  This is exactly what Condition A in the code cell demonstrates.*

**Q4.**  Test-time compute is paid *per query*, unlike training compute which is paid once.  Given that, describe a realistic product where always routing to a reasoning model would be a poor engineering decision, and propose a routing rule that uses reasoning only when it earns its cost.

> *Hint: A customer-support chat that mostly answers "where's my order?" and "reset my password" is latency-sensitive and dominated by simple lookups; routing every message to a slow, expensive reasoning model would raise cost and hurt response time for no accuracy gain.  A better rule: classify incoming queries (cheap instruct model or a simple heuristic) and only escalate multi-step, high-stakes, or checkable-answer queries (billing disputes, math, code) to the reasoning model.  This is the test-time compute dial applied as a routing policy.*

---

# Part III: What Makes a Model a "Vision" Model

This part is deliberately short; the full treatment lives in the multimodal agents activity.  The goal here is only to place vision models in the same lifecycle picture as everything else.

## 3.  Images Become Tokens

**Why this matters:** "Vision model" sounds like a different species.  In the lifecycle view it is not; it is an instruct model with an extra input path.

**Modality fusion.**  A vision (or *multimodal*) model keeps the same transformer language backbone but adds two pieces: an **image encoder** that turns pixels into a grid of vectors, and a **projection layer** that maps those vectors into the same space as text tokens.  The result is that an image enters the model as a sequence of "image tokens" sitting right alongside the text tokens.  The language model attends across both; that is *modality fusion*.

**Trained on image-text pairs.**  To make those image tokens meaningful, the model is trained on large collections of images paired with captions or descriptions, learning to align "what the picture shows" with "how we describe it in words."  After this, a **vision-language model (VLM)** can read photos, charts, documents, screenshots, and UI states, and reason about them in text.

**Why it matters for agents.**  A VLM lets an agent perceive things that are not conveniently available as text: a scanned invoice, a diagram, an error dialog, the current screen.  But image tokens are lossy: fine print, exact pixel positions, and dense tables can be misread.  For the mechanics of VLMs, document pipelines, the modality bottleneck, and grounding, work through the multimodal agents activity linked in Further Reading.

### Questions to Work Through

**Q5.**  Using the encoder-plus-projection picture, explain why a vision model can *describe* a photo of a page of text but may still misread a specific serial number on it, while a plain text model given the same characters as text would not.  What does this tell you about when to use OCR before the model versus feeding the image directly?

> *Hint: The image encoder compresses the whole page into a limited grid of image tokens, so fine detail (a long serial number, tiny print) can be blurred or lost before the language backbone ever sees it; the model reasons over a lossy summary, not the exact glyphs.  A text model handed the actual characters has them exactly.  Practical implication: for exact-transcription tasks, run OCR (or a text extraction step) first and feed the *text*; feed the raw image when you need layout, visual context, or content OCR can't capture (charts, UI state, handwriting).*

---

# Part IV: Choosing a Model - A Taxonomy

Now we turn the lifecycle into a decision tool.  The point of naming model types is to *pick* one on purpose.

## Base vs. Instruct vs. Reasoning vs. Vision

| Model type | How it is trained | Good at | How to recognize / choose it | Cost trade-off |
|------------|-------------------|---------|------------------------------|----------------|
| **Base** | Pretraining only (next-token prediction) | Text completion, as a starting point for further fine-tuning | Named "base" or "pretrained"; ignores instructions, continues text | Cheapest to run, but rarely what an app wants directly |
| **Instruct / chat** | + supervised fine-tuning + RLHF/DPO alignment | Following instructions, dialogue, drafting, classification, most everyday tasks | Named "instruct", "chat", or "-it"; answers your question directly | Balanced; the sensible default for most tasks |
| **Reasoning** | + RL on verifiable rewards (long correct chains of thought) | Multi-step math, code, logic, planning, self-checking | Named "reasoning", "thinking", or "-o"/"-R" style; emits or hides a long think phase | Highest per-query cost and latency (pays test-time compute every call); worth it only for hard, checkable problems |
| **Vision / multimodal** | Instruct model + image encoder + projection, trained on image-text pairs | Reading images, documents, charts, screenshots, UI | Named "vision", "-V", or "multimodal"; accepts image inputs | Higher cost than text-only; image tokens are lossy on fine detail |

The decision, in one line: **default to a fast instruct model; escalate to a reasoning model only when the task is hard, multi-step, and checkable; reach for a vision model only when the input really is an image.**  Fine-tuning a model of any of these types for your own data or domain is a further choice; the fine-tuning-vs-RAG activity covers when to fine-tune, when to retrieve, and the LoRA shortcut.

---

## Reflection Prompt

**Personal:** Think about a task you actually did with an AI tool in the last week.  Which model type did it call for: instruct, reasoning, or vision?  Did the tool you used match the task, or did it over- or under-serve it (slow and expensive for a trivial ask, or too shallow for a hard one)?

**Technical:** You are designing a feature that must answer thousands of user questions per hour, a small fraction of which are hard multi-step problems.  Sketch a routing policy that spends test-time compute wisely: how would you cheaply detect the hard fraction, and what would you route to the reasoning model versus a fast instruct model?

**Responsible use:** Reasoning models cost more money, more energy, and more latency *every single query*.  When is paying that premium justified, and when is it wasteful (even harmful) to default to the "smartest" model?  Consider a case where the right responsible choice is the *cheaper* model, and articulate the principle you would give a team: "reach for the reasoning model when ___, and stop reaching for it when ___."

---

## Further Reading

These four activities are the deep dives this hub connects.  Open any of them when you need the mechanics behind a stage of the lifecycle:

- [How LLMs Are Built: Tokenization, Pre-Training, and Scaling]({{ site.baseurl }}/Tutorials/LLMPretraining), the *pretraining -> base model* stage in full.
- [From Rewards to Preferences: Reinforcement Learning and RLHF]({{ site.baseurl }}/Tutorials/RLHF), RL, RLHF, and DPO, the machinery behind *alignment* and *reasoning* training.
- [Fine-Tuning, RAG, and Prompting: Choosing the Right Approach](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-ragquality.md), how to specialize any model type, including the LoRA shortcut.
- [Multimodal Agents: Vision, Documents, and Code as First-Class Inputs]({{ site.baseurl }}/Tutorials/MultimodalAgents), the deep dive on *vision/multimodal* models, the modality bottleneck, and grounding.
