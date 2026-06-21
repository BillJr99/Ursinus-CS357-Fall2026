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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| Prompting | Giving the AI model written instructions, examples, or context within a single request — no code changes, no training, just better text. | Writing a system prompt that says "You are a helpful HR assistant. Always cite the policy section number." |
| RAG (Retrieval-Augmented Generation) | Connecting the AI to an external knowledge source (like a document database) so it can look up relevant information before answering — the model's weights never change. | Before answering "What is our PTO policy?", the system fetches the relevant section of the employee handbook and includes it in the prompt. |
| Fine-Tuning | Continuing the model's training on your own data so the model's internal weights permanently change — it behaves differently on every future call, even without special prompts. | Training `llama3.1:8b` on 800 examples of correctly formatted legal contract summaries so it always produces that format. |
| LoRA (Low-Rank Adaptation) | A parameter-efficient fine-tuning method that trains only tiny "adapter" matrices (about 0.1% of the total parameters) instead of updating the entire model — dramatically reducing GPU cost. | Fine-tuning a 7B model with LoRA requires a single A100 GPU for a few hours instead of a multi-GPU cluster for days. |
| QLoRA | LoRA combined with 4-bit quantization of the frozen base model weights — enables fine-tuning 7B models on a single consumer GPU with 24 GB of VRAM. | Students at Ursinus can run QLoRA fine-tuning on a rented Lambda Labs A100 instance for roughly $3–5. |
| Context Window | The maximum amount of text (measured in tokens, where 1 token ≈ 0.75 words) that a model can read in a single request — determines whether "just paste the whole document in" is even possible. | GPT-4o has a 128K token context window — about 96,000 words. A 500-page policy manual (~200,000 words) still exceeds it. |

---

# Part I: The Ladder

## 1. Three Ways to Specialize a Model

This is the "hire an expert vs. give your generalist a textbook" decision — and just like in real life, hiring a full specialist is expensive, slow, and permanent. Sometimes the right answer is to give your generalist a great textbook (RAG), or better instructions (prompting), and only bring in the specialist when those genuinely cannot work.

The three approaches differ in *where the specialization lives* — in the prompt at inference time, in retrieved text at inference time, or in the model weights permanently.

**Prompting** gives the model instructions, examples, and context within a single call. Zero-shot prompting provides instructions only; few-shot adds 2–10 worked examples; chain-of-thought prompts the model to reason step by step before answering. Prompting is free, instant, and reversible — but is bounded by the context window and by what the base model already knows. A model that has never seen clinical trial reports cannot be prompted into reliable clinical summarization.

**RAG** injects retrieved information at inference time. The model receives the same prompt, but now the prompt includes relevant documents fetched from an external index. The model's weights never change. RAG excels when knowledge is dynamic (daily news, live databases), external (proprietary documents the base model never saw), or too large for any context window. Its costs are operational: embedding, indexing, retrieval latency, and the complexity of the pipeline.

**Fine-tuning** adjusts the model's weights on a task-specific dataset. The change is permanent: a fine-tuned model behaves differently on every subsequent call, without any special prompt. Fine-tuning can teach style, format, vocabulary, and domain behavior that prompting cannot reliably achieve. It is also the most expensive and least reversible option. **PEFT (Parameter-Efficient Fine-Tuning)** methods such as LoRA and QLoRA reduce cost dramatically by freezing most weights and training only small adapter matrices — more on this below.

The practical rule: **start at the top of the ladder**. Reach for fine-tuning only after prompting and RAG have been genuinely tried and found insufficient.

---

## Model 1: The Decision Framework

Use this table as a diagnostic. Each row is a question to ask before choosing an approach; the answers point you toward the right rung. Work through the rows in order — like a flowchart where each answer narrows your options.

| Diagnostic Question | If Yes | If No |
|---|---|---|
| Does the base model already know the domain well enough to answer correctly with good instructions? | Start with prompting or RAG — you may not need anything more expensive | Consider fine-tuning or domain-adaptive pre-training to inject the domain knowledge |
| Is the knowledge dynamic, updated frequently, or stored in proprietary documents the model has never seen? | Use RAG — it reads your documents at query time without retraining | Fine-tuning may be appropriate — bake the stable knowledge into model weights |
| Do you need citations or source attribution in the output so users can verify claims? | Use RAG — retrieved chunks naturally serve as citations | Either prompting or fine-tuning; hallucinated citations are a serious risk without retrieval |
| Is the required output format or style highly specific and must be perfectly consistent across thousands of calls (e.g., a fixed JSON schema, a precise legal format)? | Fine-tuning (or strong few-shot prompting as a first attempt) — format training is one of fine-tuning's clearest wins | Prompting or RAG is likely sufficient for moderate format requirements |
| Do you have labeled input-output pairs for the task (hundreds to thousands of examples)? | Fine-tuning is technically feasible — you have the data required | Use prompting or RAG for now; invest in data collection if fine-tuning becomes necessary |
| Is cost or latency the primary constraint — does every extra millisecond or fraction of a cent matter? | Prompting (cheapest per call, lowest latency, no infrastructure) | Fine-tuning or RAG if quality justifies the added cost and complexity |

### Critical Thinking Questions

1. A startup wants to build a customer support bot that answers questions about their product documentation, which is updated every sprint (roughly every two weeks). Walk through the decision table row by row and justify your final recommendation.

   *Hint:* Pay special attention to the "Is the knowledge dynamic?" row. What does "updated every two weeks" mean for an approach that requires retraining (days of work) vs. an approach that requires re-indexing (minutes of work)?

2. A legal firm wants every contract summary the model produces to follow a precise seven-section structure with mandatory fields. They have 2,000 existing human-written summaries in that format. Walk through the decision table for this case. Does the answer change if they only have 50 examples? Why?

   *Hint:* Fine-tuning for format typically requires at least a few hundred examples to be reliable. With 50 examples, few-shot prompting (including 3–5 examples directly in the prompt) may actually outperform a poorly-fitted fine-tuned model.

3. "The model already knows how to write code, so we just need to prompt it." A team makes this argument to avoid fine-tuning their coding assistant. Describe a concrete scenario where this reasoning fails — where the gap between base model behavior and desired behavior is too large for prompting to close.

   *Hint:* Think about a company-specific internal library with custom APIs that the base model has never seen (because it's proprietary). No amount of prompting teaches the model what `acme_corp.billing.create_invoice(customer_id, line_items)` does.

---

# Part II: Cost and the LoRA Shortcut

## 2. The Cost Reality

The order-of-magnitude cost differences between approaches are often underappreciated. These figures are rough but directionally correct as of 2025. Think of it like building a house: you can rent a furnished apartment immediately (prompting), move into a place and add your own furniture (RAG), or custom-build from scratch (fine-tuning) — each has very different upfront and ongoing costs.

| Approach | Typical Cost per Query | One-Time Setup Cost | Infrastructure Needed | Data Requirement |
|---|---|---|---|---|
| Prompting (API call to GPT-4o or Claude) | $0.003–$0.05 per 1,000-token call depending on model | None beyond prompt engineering time | None — uses a managed API | None — just write better instructions |
| RAG (API + Chroma/Qdrant vector DB) | $0.001–$0.02 per query (embedding + retrieval + smaller LLM call) | Hours to days of pipeline engineering | Vector DB (free locally, ~$50/mo cloud for small scale), embedding service | Source documents only — no labeled pairs needed |
| Fine-tuning (small model, LoRA on `llama3.1:8b`) | $0.0001–$0.001 per call after training (self-hosted inference) | $10–$200 per training run on a rented A100 GPU | GPU for training (A100/H100 rented on Lambda Labs), storage for weights | 200–2,000 labeled input-output pairs |
| Fine-tuning (large model, full weight update) | $0.0001–$0.001 per call after training (self-hosted inference) | $1,000–$50,000 per training run on multi-GPU cluster | Multi-GPU cluster, distributed training framework (DeepSpeed, FSDP) | Thousands to millions of labeled pairs |
| Pre-training from scratch | Fractions of a cent per call after training | $1,000,000+ for a competitive model | Massive GPU cluster, months of compute | Billions of tokens of curated text |

The "low cost per call after training" for fine-tuning is deceptive: the inference cost is low, but the up-front training cost is paid once per model version. If the domain or data changes, you re-pay that cost.

## Model 2: Same Task, Three Approaches

Consider a concrete deployment: **an HR policy assistant that answers questions about a company's internal policy document**. This is exactly the kind of task where the choice of approach has real, measurable consequences.

| Dimension | Prompting: Paste Full Doc in Context | RAG: Chunk, Embed, Retrieve | Fine-Tuning: Train on Q&A Pairs |
|---|---|---|---|
| Implementation effort | Include entire policy in the system prompt — takes minutes to set up | Index policy chunks in a vector DB; retrieve on each query — takes hours to set up (`pip install chromadb`, embed chunks, build query pipeline) | Generate Q&A pairs from the doc, fine-tune a base model like `llama3.1:8b` with LoRA — takes days |
| How it handles policy updates | Immediately — just update the prompt text with the new policy content | With re-indexing, which takes minutes to hours depending on document size | Must retrain, which takes hours to days and costs GPU compute |
| Cost per user query | Higher token cost because the entire policy is in every prompt (e.g., a 50-page doc = ~25,000 tokens × $0.005/1K = $0.125 per call) | Moderate: retrieval + smaller context (typically 1,000–3,000 tokens per call) | Very low per call after training, but training itself costs $20–$200 upfront |
| Can handle 500-page policy? | No — a 500-page document exceeds even 128K-token context windows | Yes — only the relevant 3–5 chunks are retrieved per query | Yes — but generating Q&A pairs for 500 pages and training costs significant time and money |
| Provides citations? | Possible with careful prompting ("Always cite the section number") but not guaranteed | Natural — the retrieved chunk itself is the citation and can be shown to the user | Generally not — knowledge is embedded opaquely in weights, so the model cannot point to its source |
| Output style consistency | Moderate — varies with how the user phrases their question | Moderate — same retrieval quality, but LLM generation still varies | High — style, format, and phrasing learned during training appear consistently in every response |

> **⚠️ Common Misconception:** Many teams jump straight to fine-tuning because it sounds like the most "AI-native" solution. In reality, for a task like the HR policy assistant, **RAG almost always outperforms fine-tuning** because policy documents change frequently (defeating fine-tuning's static knowledge) and citations matter (defeating fine-tuning's opaque knowledge). Fine-tuning wins for style/format, not for factual recall of changing documents.

### Critical Thinking Questions

4. The HR policy document is 50 pages. Prompting is eliminated by context window limits. Between RAG and fine-tuning, which approach provides better freshness when a policy changes, and why does the answer matter operationally for an HR department?

   *Hint:* When a policy changes, which approach requires re-indexing (minutes) vs. retraining (hours/days)? Think about the HR team's perspective: if the maternity leave policy changes tomorrow, how quickly can each approach reflect that change?

5. A product manager argues: "Let's fine-tune the model on HR Q&A pairs so we don't need the vector database." What hidden assumption does this argument make about the stability of the policy, and what happens at the next policy revision?

   *Hint:* The argument assumes the Q&A pairs will remain accurate indefinitely. What happens when a policy changes and the fine-tuned model confidently gives the old (now wrong) answer?

6. Describe a hybrid approach that combines RAG *and* fine-tuning. What does each layer contribute, and what would justify the additional complexity and cost?

   *Hint:* Think of RAG as responsible for "what information to use" and fine-tuning as responsible for "how to format and present the answer." A model fine-tuned on 2,000 HR Q&A pairs will always respond in the right format and tone; RAG ensures the specific policy content it uses is always current.

---

## 3. LoRA: Fine-Tuning Without Full Weight Updates

Full fine-tuning updates every parameter in the model — for a 7B-parameter model, that is 7 billion floating-point numbers to store gradients for and update. LoRA (Low-Rank Adaptation) sidesteps this by observing that the *update* to each weight matrix during fine-tuning tends to be low-rank: it lives in a small subspace of the full parameter space.

**LoRA freezes all original weights and adds two small matrices per layer.** For a weight matrix $W \in \mathbb{R}^{d \times k}$, LoRA trains $A \in \mathbb{R}^{d \times r}$ and $B \in \mathbb{R}^{r \times k}$ where $r \ll d, k$ (typically $r = 4$, $8$, or $16$). During inference, the layer computes $Wx + ABx$ — the original output plus a learned correction. Installation: `pip install peft transformers` (the PEFT library from Hugging Face implements LoRA).

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

**Real cost example:** Fine-tuning `llama3.1:8b` with QLoRA on 800 JSON-formatting examples using a rented Lambda Labs A100 instance costs approximately $1.60 (0.8 hours × $2/hour). The resulting adapter file (the A and B matrices) is roughly 40 MB, compared to the 16 GB base model.

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

   *What to do:* For each product, answer: Does it know about recent events? (RAG or prompting.) Does it refuse certain topics? (Prompting/fine-tuning.) Does it always output in a specific format? (Fine-tuning.) Does it cite sources? (RAG.)

   *Starter hint:* GitHub Copilot likely uses a combination: a code-specialized base model (fine-tuning on code) plus in-context retrieval of your open files (prompting/RAG). What evidence do you see for this in its behavior?

   *You've succeeded when:* You have a table with three products, a hypothesis for each, and at least two observable behaviors that support each hypothesis.

2. *Cost model.* You process 10,000 user queries per day. Compare the monthly cost of: (a) GPT-4o via API at $5/1M input tokens with a 2,000-token average prompt vs. (b) a locally-hosted fine-tuned `llama3.1:8b` model on a rented A100 at $2/hour.

   *What to do:* Calculate (a) monthly API cost: 10,000 queries/day × 30 days × 2,000 tokens × ($5 / 1,000,000). Calculate (b) monthly GPU cost: 720 hours/month × $2/hour. Add the one-time training cost. Find the break-even query volume.

   *Starter hint:* At 10,000 queries/day, GPT-4o API cost ≈ $3,000/month. A dedicated A100 ≈ $1,440/month. But what happens at 500 queries/day? The A100 is always on; the API charges per query. Build a simple Python calculation: `api_cost = queries_per_day * 30 * avg_tokens * price_per_token`.

   *You've succeeded when:* You have a break-even query volume (queries/day at which the two approaches cost the same) and a recommendation for a startup with 500 queries/day vs. 50,000 queries/day.

3. *LoRA parameter count.* A transformer layer has a query projection matrix $W_Q \in \mathbb{R}^{4096 \times 4096}$. If LoRA is applied with rank $r = 16$, how many parameters does LoRA add to this single matrix (count $A$ and $B$ together)? What fraction of the original matrix does this represent?

   *What to do:* $A$ has shape $4096 \times 16$ and $B$ has shape $16 \times 4096$. Count total LoRA parameters. Original $W_Q$ has $4096 \times 4096 = 16{,}777{,}216$ parameters.

   *Starter hint:* $|A| = 4096 \times 16 = 65{,}536$. $|B| = 16 \times 4096 = 65{,}536$. Total LoRA = $131{,}072$. Fraction = $131{,}072 / 16{,}777{,}216 \approx 0.78\%$. A real 7B model has ~32 such layers, each with multiple projection matrices (Q, K, V, O).

   *You've succeeded when:* You have the exact parameter counts and fractions, and you can explain why this means LoRA training needs ~100x less GPU memory than full fine-tuning.

4. *Dataset construction.* You are fine-tuning a model to extract structured fields (name, date, amount, counterparty) from procurement contracts. Design a data collection strategy for 500 training examples.

   *What to do:* Identify (a) the source of raw documents, (b) how you generate ground-truth labels, and (c) what quality checks you apply before training.

   *Starter hint:* Format each training example as a JSON pair: `{"input": "<contract text>", "output": {"name": "Acme Corp", "date": "2024-03-15", "amount": 45000.00, "counterparty": "Ursinus College"}}`. Quality checks: verify all four fields are present in every example; confirm dates parse correctly; have a human review 10% of examples for accuracy.

   *You've succeeded when:* You have a written data collection plan with source, labeling method, quality checks, and a 5-example sample dataset in the correct format.

---

## Reflection Prompt

*Personal:* Think of a skill you had to learn from a book vs. one you learned by doing. How does that map to the RAG (look it up every time) vs. fine-tuning (internalize it permanently) distinction? When is "always looking it up" actually better than "memorizing it"?

*Technical:* Fine-tuning bakes knowledge permanently into weights, making the model's reasoning opaque. RAG keeps knowledge external and attributable, but adds a pipeline that can fail in its own ways. As AI systems are deployed in high-stakes domains (medicine, law, finance), which property matters more — opaque internalized knowledge or transparent retrieved knowledge — and who should get to decide that for a given deployment?

*Societal:* LoRA makes fine-tuning accessible to individuals and small organizations who previously could not afford it. A chemistry student can now fine-tune an open-weight model on synthesis procedures; a political campaign can fine-tune a model on persuasive messaging. What new capabilities does democratized fine-tuning enable that are beneficial, and what risks does it introduce that did not exist when fine-tuning required millions of dollars?

---

→ Coming Up Next: Now that you understand when to fine-tune, the next module explores the landscape of open-weight local models (Llama, Mistral, Phi, Gemma) and how to choose the right one for your hardware and task — including how quantization lets you run a 7B model on a laptop.

---

## Further Reading

- Hu et al. "LoRA: Low-Rank Adaptation of Large Language Models." *ICLR* (2022). The original LoRA paper.
- Dettmers et al. "QLoRA: Efficient Finetuning of Quantized LLMs." *NeurIPS* (2023). QLoRA enabling consumer-GPU fine-tuning.
- Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *NeurIPS* (2020).
- Anthropic prompt engineering guide: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
