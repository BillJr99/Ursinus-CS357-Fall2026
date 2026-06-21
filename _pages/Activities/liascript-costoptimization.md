# Cost Optimization: Token Budgets, Caching, and Model Routing
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-costoptimization.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-costoptimization.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Cost Optimization: Token Budgets, Caching, and Model Routing

Running an LLM once in a notebook is cheap; running one **a million times a day for a production product** is not. Cost optimization is not optional once a system leaves a classroom. Today you learn the full cost structure of LLM inference, how to control it through caching and token budgets, and how model routing lets you spend frontier-model money only when you actually need frontier-model quality. The arc: **cost anatomy $\rightarrow$ token budgets $\rightarrow$ prompt and semantic caching $\rightarrow$ model routing $\rightarrow$ batching and right-sizing $\rightarrow$ building a cost model**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Recorder maintains running cost estimates as the activity progresses; the Reflector tracks every assumption the team makes. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Cost of a Token

## 1. How LLM Inference Is Priced

Every hosted LLM API charges by the token. The pricing structure has two parts: **input tokens** (everything in the prompt, including system prompt and context) and **output tokens** (every token the model generates). The asymmetry is important: **output tokens typically cost two to four times more than input tokens** at the same provider. The reason is computational: reading a token into the attention mechanism is a forward-pass matrix multiply; generating a token requires sampling from a probability distribution and feeding the result back as the next input — a sequential process that cannot be parallelized across tokens and must allocate KV-cache memory per token for the entire context length.

Context length also affects cost: a model processing a 128K-token context pays the full attention computation across all positions for every generated token, which scales as $O(n^2)$ with naive attention and $O(n)$ with linear approximations — but even the best implementations charge per input token, so a long context multiplies your bill.

**Token budget management** is the discipline of explicitly constraining an agent before it runs: you may use at most $T_{\text{in}}$ input tokens and at most $T_{\text{out}}$ output tokens. Providers like Anthropic expose a `max_tokens` parameter for output; some extended thinking APIs additionally allow a `budget_tokens` cap on chain-of-thought. Setting these guards prevents runaway agentic loops from burning your entire monthly budget on one stuck task.

---

## Model 1: Token Cost Breakdown

The table below uses approximate 2025 prices for reference. Actual prices vary by provider, model, and tier. "Local (Ollama)" has zero per-token cost but nonzero electricity, hardware amortization, and opportunity cost of GPU time.

| Operation | Approx. Tokens | Cost @ GPT-4 class ($15/$60 per 1M in/out) | Cost @ Local (Ollama) |
|---|---|---|---|
| System prompt (200 words) | ~270 input | ~$0.004 | $0.00 |
| One user turn (50 words) | ~67 input | ~$0.001 | $0.00 |
| One agent response (150 words) | ~200 output | ~$0.012 | $0.00 |
| 10-turn conversation (no caching) | ~3,370 total | ~$0.095 | $0.00 |
| Embedding 1,000 documents (200 words each) | ~270,000 input | ~$4.05 (embed rate) | $0.00 |

### Critical Thinking Questions

1. The 10-turn conversation charges input tokens for the entire history on every turn. If turn 10 includes turns 1–9 as history, how many times does turn 1's content get charged as an input token? Generalize to $n$ turns.
2. Why does a 200-word response cost three times more per token than a 200-word input, even though both are "200 words"?
3. A team's agent uses a 500-token system prompt, issues 100 tool calls per session, and each tool call returns 200 tokens of context. Estimate the input token cost per session. What is the dominant term?

---

# Part II: Caching Strategies

## 2. Prompt Caching

**Prompt caching** is a provider-level optimization where a static prefix of your prompt — typically your system prompt — is cached on the provider's inference servers after the first call. Subsequent requests that share that identical prefix do not pay the full compute cost to process it through every attention layer; they pay a lower "cache read" price (Anthropic charges cache-read tokens at roughly one-tenth the cost of fresh input tokens). To maximize cache utilization:

- Place **static content first**: system prompt, background documents, rules, personas — anything identical across requests.
- Place **dynamic content last**: the user's specific message, the current date, retrieved documents that vary per query.
- Keep the prefix **long enough to matter**: caching a 10-token prefix saves negligible money; caching a 2,000-token system prompt plus a 4,000-token policy document saves significantly.
- Avoid **cache-busting prefixes**: if you prepend the current timestamp to your system prompt, every request is a cache miss.

Google's Gemini API uses "Context Caching," where you upload a document once and reference it by ID; Anthropic uses automatic prefix caching. The mechanism differs; the principle is the same — pay once, reuse many times.

## 3. Semantic Caching

**Semantic caching** goes further: it caches LLM *responses* keyed not by exact prompt text but by semantic similarity. A user asking "What is the capital of France?" and another asking "Which city is the capital of France?" should return the same cached answer. Implementations like **GPTCache** and **Redis Semantic Cache** embed the incoming query, search a vector store for similar past queries above a similarity threshold, and return the stored response if the threshold is met — without calling the LLM at all.

The tradeoff is engineering cost and precision risk: a semantic cache may surface a stale or slightly-wrong answer when the similarity threshold is too loose. The correct architecture uses semantic caching only for queries where a slightly-varied-but-correct answer is acceptable, and falls through to the LLM for queries requiring freshness or precision.

**Caching ROI Example.** A system receives 10,000 queries per day. The system prompt is 500 tokens and is identical for all users. Without caching: $10{,}000 \times 500 \times \$0.000015 = \$75$/day just for the system prompt prefix. With prompt caching (cache-read at $0.0000015$): $\$7.50$/day — a 90% reduction on that portion alone. If semantic caching additionally catches 20% of queries as duplicates, those 2,000 queries cost $0, saving the output token cost for 2,000 responses.

[[MC]]
A production agent has a 2,000-token system prompt that is identical for all users. To minimize cost, you should:
- (x) Use a provider that supports prompt caching, structure the system prompt as a static prefix, and ensure it appears at the start of every request so it maximizes cache hit rate
- ( ) Reduce the system prompt to 10 tokens regardless of what is lost
- ( ) Switch to a local model, which has no per-token cost but ignore the infrastructure cost
- ( ) Batch all requests into once-per-hour jobs so the cache stays warm

---

# Part III: Model Routing

## 4. Right-Sizing and the Routing Decision

**Right-sizing** is the principle that you should deploy the minimum model capable of performing the task correctly. A 405-billion-parameter frontier model answering "What is 2+2?" wastes money, latency, and GPU cycles that could serve another user. A 3-billion-parameter model writing a novel technical specification will likely produce something inadequate. The art is in building a **routing function** that classifies incoming queries and dispatches them to the appropriate model tier.

Routing architectures take several forms:
- **Classifier-first**: a tiny, fast, cheap model (or a rules-based classifier) reads the query and outputs a label: `trivial`, `medium`, `complex`, `sensitive`. Each label maps to a model.
- **Confidence-based**: a small model attempts the task and also predicts its own confidence. If confidence exceeds a threshold, return the result; otherwise escalate to a larger model.
- **Cost-capped**: every query goes to the small model first; the orchestrator escalates only if the small model's answer fails a quality check.

## Model 2: Model Routing Decision Table

| Query Type | Correct Route | Why |
|---|---|---|
| "What is the capital of France?" | Fast/tiny model (e.g., Phi-4 locally) | Factual retrieval, no reasoning required |
| "Debug this 500-line Python traceback" | Large model (e.g., Claude Opus, GPT-4) | Multi-step reasoning over long context |
| "Is this email spam?" | Dedicated classifier, not an LLM | LLMs are over-engineered for binary classification at scale |
| "Write a technical specification for a microservices API" | Large model | Open-ended generation requiring coherent long-form structure |
| "Translate this sentence to Spanish" | Medium model or specialized translation model | Translation does not require frontier reasoning |
| "What year was Lincoln born?" | Retrieval + tiny model | Answer lives in a lookup table; generation is one token |

### Critical Thinking Questions

4. Design a routing function for a customer-support agent that handles billing questions, technical troubleshooting, and general product questions. What features of the incoming query would your classifier use? What happens if it mis-classifies?
5. What is the risk of routing a complex query to the wrong (cheaper) tier? How would you detect that this is happening in production? What metric would you monitor?
6. A confidence-based router uses the small model's self-reported confidence. Why might this be unreliable, and what alternative signal could you use to decide when to escalate?

---

# Part IV: Batching, Streaming, and Building a Cost Model

## 5. Batching and Streaming

**Batching** accumulates multiple requests and submits them together. Most providers offer a batch API at 50% of the standard price; the tradeoff is latency: batch jobs may take minutes to hours. Batching is appropriate for workloads that are **not latency-sensitive**: nightly document processing, bulk embedding generation, offline evaluation runs. It is not appropriate for a user waiting for a chat response.

**Streaming** reduces *time-to-first-token* by returning tokens as they are generated rather than waiting for the full response. Streaming does not reduce the total number of tokens generated and does not reduce cost. It improves perceived responsiveness and allows the UI to begin rendering before the response is complete.

## 6. Building a Cost Model

Before deploying any agent system, build a **cost model**: a spreadsheet or script that estimates daily expenditure given usage assumptions. The structure:

$$
\text{daily cost} = Q \times (T_{\text{in}} \times P_{\text{in}} + T_{\text{out}} \times P_{\text{out}})
$$

where $Q$ is queries per day, $T_{\text{in}}$ is average input tokens per query, $T_{\text{out}}$ is average output tokens per query, and $P_{\text{in}}$, $P_{\text{out}}$ are the per-token prices. Add terms for cache miss rate, embedding costs, and tool-call overhead. Then ask: at what scale does the cost become unsustainable, and at what scale does switching to local inference pay off?

### Critical Thinking Questions

7. At what query volume does semantic caching become worth the engineering cost of building and maintaining it? What factors besides query volume matter in this decision?
8. A team proposes to reduce cost by streaming responses to users and canceling the generation once the user stops reading. What practical and ethical complications does this introduce?
9. Build a cost model for a hypothetical Ursinus College tutoring agent that handles 200 student queries per day, each with a 300-token system prompt, a 100-token question, and a 250-token answer. Estimate monthly cost at GPT-4 pricing, then at a local model. What does the breakeven analysis look like if the local GPU costs $0.50/hour to run?

---

## Reflection Prompt

In your notebook: your team is launching a product. The investor wants to keep the monthly LLM bill under $500. You are projecting 5,000 queries per day. Walk through the specific combination of strategies — caching, routing, batching, model selection — you would implement in priority order, and explain why that order.

---

## Further Reading

- Anthropic. *Prompt Caching* (API documentation, 2024).
- Zhuang et al. *GPTCache: An Open-Source Semantic Cache for LLM Applications* (2023).
- Ong et al. *RouteLLM: Learning to Route LLMs with Preference Data* (2024).
- OpenAI. *Batch API* (documentation, 2024).
