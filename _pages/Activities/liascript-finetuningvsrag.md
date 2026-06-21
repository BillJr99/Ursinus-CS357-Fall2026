# Fine-Tuning, RAG, and Prompting: Choosing the Right Approach
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-finetuningvsrag.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-finetuningvsrag.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Fine-Tuning, RAG, and Prompting: Choosing the Right Approach

Every practical AI deployment faces the same question: **how do you specialize a general-purpose model for a specific task?** There are exactly three levers — prompting, retrieval-augmented generation, and fine-tuning — and they sit on a ladder ordered by cost, complexity, and permanence. Most practitioners reach for the expensive rungs first and regret it. This module builds **the decision framework $\rightarrow$ the cost reality $\rightarrow$ parameter-efficient fine-tuning $\rightarrow$ when to combine approaches**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Ladder

## 1. Three Ways to Specialize a Model

The three approaches differ in *where the specialization lives* — in the prompt at inference time, in retrieved text at inference time, or in the model weights permanently.

**Prompting** gives the model instructions, examples, and context within a single call. Zero-shot prompting provides instructions only; few-shot adds 2–10 worked examples; chain-of-thought prompts the model to reason step by step before answering. Prompting is free, instant, and reversible — but is bounded by the context window and by what the base model already knows. A model that has never seen clinical trial reports cannot be prompted into reliable clinical summarization.

**RAG** injects retrieved information at inference time. The model receives the same prompt, but now the prompt includes relevant documents fetched from an external index. The model's weights never change. RAG excels when knowledge is dynamic (daily news, live databases), external (proprietary documents the base model never saw), or too large for any context window. Its costs are operational: embedding, indexing, retrieval latency, and the complexity of the pipeline.

**Fine-tuning** adjusts the model's weights on a task-specific dataset. The change is permanent: a fine-tuned model behaves differently on every subsequent call, without any special prompt. Fine-tuning can teach style, format, vocabulary, and domain behavior that prompting cannot reliably achieve. It is also the most expensive and least reversible option. **PEFT (Parameter-Efficient Fine-Tuning)** methods such as LoRA and QLoRA reduce cost dramatically by freezing most weights and training only small adapter matrices — more on this below.

The practical rule: **start at the top of the ladder**. Reach for fine-tuning only after prompting and RAG have been genuinely tried and found insufficient.

---

## Model 1: The Decision Framework

Use this table as a diagnostic. Each row is a question to ask before choosing an approach; the answers point you toward the right rung.

| Diagnostic Question | If Yes | If No |
|---|---|---|
| Does the base model already know the domain well enough? | Start with prompting or RAG | Consider fine-tuning or domain-adaptive pre-training |
| Is the knowledge dynamic, updated frequently, or proprietary? | RAG | Fine-tuning (knowledge can be baked in statically) |
| Do you need citations or source attribution in the output? | RAG | Either prompting or fine-tuning |
| Is the required output format or style highly specific and consistent (e.g., structured JSON, a particular tone, a fixed schema)? | Fine-tuning (or strong few-shot prompting first) | Prompting or RAG likely sufficient |
| Do you have labeled input-output pairs for the task (hundreds to thousands)? | Fine-tuning is feasible | Prompting or RAG; collect data before committing to fine-tune |
| Is cost or latency the primary constraint? | Prompting (cheapest, fastest) | Fine-tuning or RAG if quality justifies cost |

### Critical Thinking Questions

1. A startup wants to build a customer support bot that answers questions about their product documentation, which is updated every sprint (roughly every two weeks). Walk through the decision table row by row and justify your final recommendation.
2. A legal firm wants every contract summary the model produces to follow a precise seven-section structure with mandatory fields. They have 2,000 existing human-written summaries in that format. Walk through the decision table for this case. Does the answer change if they only have 50 examples? Why?
3. "The model already knows how to write code, so we just need to prompt it." A team makes this argument to avoid fine-tuning their coding assistant. Describe a concrete scenario where this reasoning fails — where the gap between base model behavior and desired behavior is too large for prompting to close.

---

# Part II: Cost and the LoRA Shortcut

## 2. The Cost Reality

The order-of-magnitude cost differences between approaches are often underappreciated. These figures are rough but directionally correct as of 2025.

| Approach | Typical Cost per Task | One-Time Setup Cost | Infrastructure | Data Requirement |
|---|---|---|---|---|
| Prompting (API) | Fractions of a cent to a few cents | None beyond prompt engineering | None (managed API) | None |
| RAG (API + vector DB) | Fractions of a cent + small infra | Hours to days of pipeline engineering | Vector DB, embedding service | Source documents only |
| Fine-tuning (small model, LoRA) | Fractions of a cent after training | $10–$200 per training run on cloud GPU | GPU (A100/H100), storage | Hundreds to thousands of labeled pairs |
| Fine-tuning (large model, full) | Fractions of a cent after training | $1,000–$50,000 per training run | Multi-GPU cluster | Thousands to millions of labeled pairs |
| Pre-training from scratch | Fractions of a cent after training | $1,000,000+ | Massive GPU cluster, months | Billions of tokens of curated text |

The "cents after training" row for fine-tuning is deceptive: the inference cost per call is low, but the up-front training cost is paid once per model version. If the domain or data changes, you re-pay that cost.

## Model 2: Same Task, Three Approaches

Consider a concrete deployment: **an HR policy assistant that answers questions about a company's internal policy document**.

| Dimension | Prompting: Paste Full Doc in Context | RAG: Chunk, Embed, Retrieve | Fine-Tuning: Train on Q&A Pairs |
|---|---|---|---|
| Implementation | Include entire policy in the system prompt | Index policy chunks in a vector DB; retrieve on each query | Generate Q&A pairs from the doc; fine-tune a base model |
| Works when doc changes | Yes, immediately (just update the prompt) | Yes, with re-indexing (minutes to hours) | No — must retrain (hours to days) |
| Cost | Higher token cost per call (large context) | Moderate (retrieval + smaller context) | Low per-call after training; training cost up front |
| Handles 500-page policy? | No — exceeds context window | Yes | Yes — but Q&A pair generation is expensive |
| Provides citations | Possible with prompting instructions | Natural (retrieved chunks are the citation) | Generally not — knowledge is opaque in weights |
| Output consistency | Moderate — varies with phrasing | Moderate | High — style and format baked in |

### Critical Thinking Questions

4. The HR policy document is 50 pages. Prompting is eliminated by context window limits. Between RAG and fine-tuning, which approach provides better freshness when a policy changes, and why does the answer matter operationally for an HR department?
5. A product manager argues: "Let's fine-tune the model on HR Q&A pairs so we don't need the vector database." What hidden assumption does this argument make about the stability of the policy, and what happens at the next policy revision?
6. Describe a hybrid approach that combines RAG *and* fine-tuning. What does each layer contribute, and what would justify the additional complexity and cost?

---

## 3. LoRA: Fine-Tuning Without Full Weight Updates

Full fine-tuning updates every parameter in the model — for a 7B-parameter model, that is 7 billion floating-point numbers to store gradients for and update. LoRA (Low-Rank Adaptation) sidesteps this by observing that the *update* to each weight matrix during fine-tuning tends to be low-rank: it lives in a small subspace of the full parameter space.

**LoRA freezes all original weights and adds two small matrices per layer.** For a weight matrix $W \in \mathbb{R}^{d \times k}$, LoRA trains $A \in \mathbb{R}^{d \times r}$ and $B \in \mathbb{R}^{r \times k}$ where $r \ll d, k$ (typically $r = 4$, $8$, or $16$). During inference, the layer computes $Wx + ABx$ — the original output plus a learned correction.

## Model 3: LoRA Illustrated

```
Original Layer (frozen):          LoRA Correction (trained):
┌─────────────────────┐           ┌───┐   ┌─────────────────────┐
│                     │           │ A │   │                     │
│   W  (d × k)        │    +      │   │ × │   B  (r × k)        │
│   7B total params   │           │d×r│   │   r << d            │
└─────────────────────┘           └───┘   └─────────────────────┘
  Gradient: not computed             Gradient: computed for A, B only
  Storage: unchanged                 Storage: ~0.1% of original
```

At rank $r = 8$ for a 7B model, LoRA trains roughly 4–8 million parameters instead of 7 billion — a 99.9% reduction in trainable parameters. **QLoRA** combines LoRA with 4-bit quantization of the frozen base weights, enabling fine-tuning of 7B models on a single consumer GPU with 24 GB of VRAM.

[[MC]]
A team wants to fine-tune a 7B model to always respond in a structured JSON format for a data extraction task. They have 800 labeled examples and a single A100 GPU (40 GB). Which approach is most appropriate?
- ( ) Full fine-tuning — update all 7B parameters — because the format change requires deep behavioral modification
- (x) LoRA or QLoRA — freeze the base weights, train small adapter matrices — sufficient for format adaptation at a fraction of the compute cost
- ( ) RAG — retrieve the format specification from a vector database on each call
- ( ) Pre-training from scratch on JSON-formatted text corpora

---

# Part III: Synthesis and Practice

## Exercises

1. *Approach audit.* Identify three AI products you use regularly (a search assistant, a coding tool, a customer service bot). For each, hypothesize whether the specialization is achieved via prompting, RAG, fine-tuning, or some combination. List the evidence that informs your hypothesis.
2. *Cost model.* You process 10,000 user queries per day. Compare the monthly cost of: (a) GPT-4o via API at $5/1M input tokens with a 2,000-token average prompt vs. (b) a locally-hosted fine-tuned Llama 3.1 8B model on a rented A100 at $2/hour. At what query volume does local fine-tuning become cheaper?
3. *LoRA parameter count.* A transformer layer has a query projection matrix $W_Q \in \mathbb{R}^{4096 \times 4096}$. If LoRA is applied with rank $r = 16$, how many parameters does LoRA add to this single matrix (count $A$ and $B$ together)? What fraction of the original matrix does this represent?
4. *Dataset construction.* You are fine-tuning a model to extract structured fields (name, date, amount, counterparty) from procurement contracts. Design a data collection strategy for 500 training examples: what is the source of the raw documents, how do you generate the labels, and what quality checks do you apply?

---

## Reflection Prompt

In your notebook: fine-tuning bakes knowledge permanently into weights, making the model's reasoning opaque. RAG keeps knowledge external and attributable, but adds a pipeline that can fail in its own ways. As AI systems are deployed in high-stakes domains (medicine, law, finance), which property matters more — opaque internalized knowledge or transparent retrieved knowledge — and who should get to decide that for a given deployment?

---

## Further Reading

- Hu et al. "LoRA: Low-Rank Adaptation of Large Language Models." *ICLR* (2022). The original LoRA paper.
- Dettmers et al. "QLoRA: Efficient Finetuning of Quantized LLMs." *NeurIPS* (2023). QLoRA enabling consumer-GPU fine-tuning.
- Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *NeurIPS* (2020).
- Anthropic prompt engineering guide: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
