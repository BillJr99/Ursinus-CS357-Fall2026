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

Cloud AI tokens are like taxi rides — you don't notice the meter until the bill arrives. Running an LLM once in a notebook is cheap; running one **a million times a day for a production product** is not. Cost optimization is not optional once a system leaves a classroom. Today you learn the full cost structure of LLM inference, how to control it through caching and token budgets, and how model routing lets you spend frontier-model money only when you actually need frontier-model quality. The arc: **cost anatomy $\rightarrow$ token budgets $\rightarrow$ prompt and semantic caching $\rightarrow$ model routing $\rightarrow$ batching and right-sizing $\rightarrow$ building a cost model**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Recorder maintains running cost estimates as the activity progresses; the Reflector tracks every assumption the team makes. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Token** | The basic unit an LLM reads and writes — roughly equivalent to about 3/4 of an English word on average. "Hello, world!" is approximately 4 tokens. | A 200-word response costs roughly 270 output tokens, which is the most expensive kind. |
| **Input tokens vs. output tokens** | Input tokens are everything the model reads (your system prompt, the user's message, retrieved documents). Output tokens are everything the model generates (its response). Output tokens cost 2-4x more per token. | A 500-token system prompt sent with every request costs you input-token prices each time; a 200-token response costs output-token prices, which are higher. |
| **Prompt caching** | A provider feature that stores a static prefix of your prompt on their servers, so repeated requests that share that prefix are charged at a deeply discounted "cache read" rate instead of full input price. | Your 2,000-token system prompt, sent once and cached, costs ~10% as much on every subsequent request. |
| **Semantic caching** | Caching AI responses by meaning rather than exact text, so that "What is the capital of France?" and "Which city is France's capital?" return the same stored answer without calling the LLM again. | A tool like GPTCache embeds incoming queries and retrieves a cached response if the similarity score is high enough. |
| **Model routing** | Automatically directing each incoming query to the cheapest model tier capable of answering it correctly, rather than always using the most powerful (and most expensive) model. | Sending "What is 2+2?" to a tiny local model, and sending "Debug this 500-line Python traceback" to a large frontier model. |
| **Token budget** | An explicit cap set before the model runs, limiting how many input and/or output tokens it may use. Prevents runaway agentic loops from consuming your entire monthly credit in one stuck task. | Setting `max_tokens=500` in your API call to ensure responses stay short and costs stay predictable. |

---

# Part I: The Cost of a Token

In this part, you will build a mental model of how LLM API costs accumulate — including why output tokens cost more than input tokens and why long conversations have disproportionately high costs — so that every architectural decision you make later has a price tag attached.

## Model 1: Token Cost Breakdown

Every hosted LLM API charges by the token. The pricing structure has two parts: **input tokens** (everything in the prompt, including system prompt and context) and **output tokens** (every token the model generates). The asymmetry is important: **output tokens typically cost two to four times more than input tokens** at the same provider.

The reason is computational: reading a token into the attention mechanism is a forward-pass matrix multiply; generating a token requires sampling from a probability distribution and feeding the result back as the next input — a sequential process that cannot be parallelized across tokens and must allocate KV-cache memory (the stored key-value pairs from prior tokens that the attention mechanism needs to re-use) per token for the entire context length.

Context length also affects cost: a model processing a 128K-token context pays the full attention computation across all positions for every generated token, which scales as $O(n^2)$ with naive attention. Even the best implementations charge per input token, so a long context multiplies your bill proportionally.

**Token budget management** is the discipline of explicitly constraining an agent before it runs: you may use at most $T_{\text{in}}$ input tokens and at most $T_{\text{out}}$ output tokens. Providers like Anthropic expose a `max_tokens` parameter for output; some extended thinking APIs additionally allow a `budget_tokens` cap on chain-of-thought. Setting these guards prevents runaway agentic loops from burning your entire monthly budget on one stuck task.

The table below uses approximate 2025 prices for reference. Actual prices vary by provider, model, and tier. "Local (Ollama)" has zero per-token cost but nonzero electricity, hardware amortization, and opportunity cost of GPU time.

| Operation | Approx. Tokens | Cost @ GPT-4 class ($15/$60 per 1M in/out) | Cost @ Local (Ollama) | In Our Course |
|---|---|---|---|---|
| System prompt (200 words) | ~270 input tokens | ~$0.004 per call — negligible once, expensive at scale. | $0.00 per call | Every agent session starts with at least one system prompt; multiply by your daily query count. |
| One user turn (50 words) | ~67 input tokens | ~$0.001 per turn | $0.00 per turn | Each student question to a tutoring agent is roughly this size. |
| One agent response (150 words) | ~200 output tokens | ~$0.012 per response — note this is 3x the input price per token. | $0.00 per response | A single helpful reply to a student question. |
| 10-turn conversation (no caching) | ~3,370 total tokens | ~$0.095 for the full conversation | $0.00 | A typical back-and-forth help session with a homework agent. |
| Embedding 1,000 documents (200 words each) | ~270,000 input tokens | ~$4.05 at embedding rates (cheaper than chat) | $0.00 | Building a RAG knowledge base from a course's reading list. |

### Critical Thinking Questions

1. The 10-turn conversation charges input tokens for the entire conversation history on every turn. If turn 10 includes turns 1-9 as history, how many times does turn 1's content get charged as an input token over the course of the full conversation? Generalize this to $n$ turns and explain why this pattern makes long conversations disproportionately expensive.

   *Hint:* On turn 2, turn 1 is in the history. On turn 3, turns 1 and 2 are in the history. Keep going. How many times total does turn 1 appear across all 10 turns?

2. Why does a 200-word response cost three times more per token than a 200-word input, even though both contain "200 words" of text? Explain the computational reason in your own words.

   *Hint:* Think about what the GPU has to do differently when reading existing text versus generating new text one token at a time.

3. A team's agent uses a 500-token system prompt, issues 100 tool calls per session, and each tool call returns 200 tokens of retrieved context. Estimate the total input token cost per session. Which component dominates the total cost, and what does that reveal about where to focus your optimization effort?

   *Hint:* Multiply each component: (system prompt tokens) × (number of turns) + (tool context tokens) × (number of tool calls). Which term is largest?

With the cost anatomy understood, Part II introduces the two main techniques for paying less per request: caching static prompt prefixes at the provider level, and recognizing semantically duplicate queries before they ever reach the model.

---

# Part II: Caching Strategies

In this part, you will learn how prompt caching and semantic caching work, when each applies, and how to structure your prompts so the provider's cache actually gets used — because a cache-busting prefix in the wrong place can eliminate your entire caching benefit.

## Model 2: Prompt Caching and Semantic Caching

**Prompt caching** is a provider-level optimization where a static prefix of your prompt — typically your system prompt — is cached on the provider's inference servers after the first call. Subsequent requests that share that identical prefix pay a lower "cache read" price (Anthropic charges cache-read tokens at roughly one-tenth the cost of fresh input tokens). To maximize cache utilization:

- Place **static content first**: system prompt, background documents, rules, personas — anything identical across requests.
- Place **dynamic content last**: the user's specific message, the current date, retrieved documents that vary per query.
- Keep the prefix **long enough to matter**: caching a 10-token prefix saves negligible money; caching a 2,000-token system prompt plus a 4,000-token policy document saves significantly.
- Avoid **cache-busting prefixes**: if you prepend the current timestamp to your system prompt, every request is a cache miss — the cache never gets used because the prefix is never identical twice.

**Semantic caching** goes further: it caches LLM *responses* keyed not by exact prompt text but by semantic similarity. A user asking "What is the capital of France?" and another asking "Which city is the capital of France?" should return the same cached answer. Implementations like **GPTCache** and **Redis Semantic Cache** embed the incoming query, search a vector store for similar past queries above a similarity threshold, and return the stored response if the threshold is met — without calling the LLM at all.

The tradeoff is engineering cost and precision risk: a semantic cache may surface a stale or slightly-wrong answer when the similarity threshold is too loose. The correct architecture uses semantic caching only for queries where a slightly-varied-but-correct answer is acceptable, and falls through to the LLM for queries requiring freshness or precision.

**Caching ROI Example.** A system receives 10,000 queries per day. The system prompt is 500 tokens and is identical for all users. Without caching: $10{,}000 \times 500 \times \$0.000015 = \$75$/day just for the system prompt prefix. With prompt caching (cache-read at $0.0000015$): $\$7.50$/day — a 90% reduction on that portion alone. If semantic caching additionally catches 20% of queries as duplicates, those 2,000 queries cost $0, saving the full output token cost for 2,000 responses.

> **Two layers, same idea.** The **prompt caching** here is a *billing* feature of a hosted API — you are charged less for a shared prefix. There is a distinct but related optimization one layer down, inside the inference engine itself: **prefix caching** in a serving stack like vLLM reuses the shared prefix's *KV cache* in GPU memory so its prefill is never recomputed, cutting time-to-first-token rather than your bill. If you self-host, you get the serving-layer version; if you call a hosted API, you get the billing-layer version. See Part IV of *Serving LLMs in Production* (`liascript-llmserving.md`) for how serving-layer prefix caching works and why PagedAttention makes it possible.

A production agent has a 2,000-token system prompt that is identical for all users. To minimize cost, you should:

[(X)] Use a provider that supports prompt caching, structure the system prompt as a static prefix, and ensure it appears at the start of every request so it maximizes cache hit rate
[( )] Reduce the system prompt to 10 tokens — shorter prompts always produce lower costs regardless of caching behavior
[( )] Switch to a local model — local inference has zero per-token cost, so a 2,000-token system prompt has no cost impact
[( )] Place the user's dynamic message first in the prompt, then append the static system prompt — this maximizes context available to the model for each query

---

> **Common Misconception:** "Switching to a local model (like Ollama) eliminates AI costs entirely."
>
> A local model eliminates per-token API fees, but not cost. You still pay for: the GPU or cloud compute instance to run the model (a decent GPU costs $0.50-$2.00/hour on cloud providers), electricity, the engineering time to set up and maintain the local inference stack, and the opportunity cost of GPU time that could serve other tasks. For low-volume projects, a local model often costs *more* when you account for idle GPU time. The breakeven analysis depends on your query volume — which is exactly what the cost model in Part IV is designed to compute.

Caching reduces the cost of repeated work; Part III introduces model routing, which reduces cost on novel work by matching each query to the cheapest model tier capable of answering it correctly.

---

# Part III: Model Routing

In this part, you will apply the right-sizing principle to a routing decision table and design a classifier that dispatches queries to the appropriate model tier — the same pattern used in production systems that serve millions of queries per day.

## Model 3: Right-Sizing and the Routing Decision

**Right-sizing** is the principle that you should deploy the minimum model capable of performing the task correctly. A 405-billion-parameter frontier model answering "What is 2+2?" wastes money, latency, and GPU cycles that could serve another user. A 3-billion-parameter model writing a novel technical specification will likely produce something inadequate. The art is in building a **routing function** that classifies incoming queries and dispatches them to the appropriate model tier.

Routing architectures take several forms:
- **Classifier-first**: a tiny, fast, cheap model (or a rules-based classifier) reads the query and outputs a label: `trivial`, `medium`, `complex`, `sensitive`. Each label maps to a model tier.
- **Confidence-based**: a small model attempts the task and also predicts its own confidence. If confidence exceeds a threshold, return the result; otherwise escalate to a larger model.
- **Cost-capped**: every query goes to the small model first; the orchestrator escalates only if the small model's answer fails a quality check (a property test or LLM-as-judge score).

| Query Type | Correct Route | Why This Route Is Right | Cost Savings vs. Always Using Frontier |
|---|---|---|---|
| "What is the capital of France?" | Fast or tiny model (e.g., Phi-4 running locally) | Pure factual retrieval — no multi-step reasoning required; any model with basic world knowledge can answer correctly. | ~99% savings — a tiny model costs almost nothing per query. |
| "Debug this 500-line Python traceback" | Large frontier model (e.g., Claude Opus, GPT-4) | Requires multi-step reasoning over long context; understanding of the full call stack and interaction between modules. | No savings — this query genuinely requires frontier capability. |
| "Is this email spam?" | Dedicated binary classifier, not an LLM at all | A fine-tuned classifier is 100-1000x cheaper than an LLM and often more accurate for this single-purpose task. | ~99.9% savings — LLMs are dramatically over-engineered for binary classification at scale. |
| "Write a technical specification for a microservices API" | Large frontier model | Open-ended generation requiring coherent, technically accurate long-form structure; small models produce vague or incomplete specs. | No savings — frontier quality is genuinely needed. |
| "Translate this sentence to Spanish" | Medium model or specialized translation model | Translation does not require frontier-level reasoning; specialized translation models (e.g., NLLB) often outperform general LLMs at lower cost. | ~80% savings depending on translation volume. |
| "What year was Lincoln born?" | Retrieval + tiny model | The answer lives in a lookup table; generation is effectively one token; retrieval is faster and more reliable than LLM recall. | ~95% savings — retrieval is cheap; generation is minimal. |

### Critical Thinking Questions

4. Design a routing function for a customer-support agent that handles billing questions, technical troubleshooting, and general product questions. What features of the incoming query text would your classifier use to assign a route? What happens to the user experience if the classifier mis-classifies a complex billing dispute as a simple product question?

   *Hint:* Consider features like: presence of numbers or account references (billing), presence of error messages or version numbers (technical), question length, presence of emotional language (escalation needed). What's the cost of a wrong classification in each direction?

5. What is the risk of routing a complex query to the wrong (cheaper) tier? How would you detect in production that mis-routing is happening frequently? What specific metric would you monitor, and what threshold would trigger an alarm?

   *Hint:* If the small model frequently produces answers that the user immediately follows up on with "that's not right" or "can you try again," that's a signal of mis-routing. What would you log to detect this pattern?

6. A confidence-based router relies on the small model's self-reported confidence score to decide whether to escalate. Why might this be unreliable — and what alternative signal could you use instead to decide when to escalate to a larger model?

   *Hint:* LLMs are known to be poorly calibrated — they are often very confident when wrong. What could you check about the *output itself* (rather than the model's confidence score) to decide if it looks trustworthy?

Routing handles the per-query cost; Part IV closes the loop with batching for non-interactive workloads and a cost formula that lets you project your system's expenses before you deploy it.

---

# Part IV: Batching, Streaming, and Building a Cost Model

In this part, you will distinguish batching from streaming (they are often confused), learn when each is appropriate, and build a cost model that projects your agent's monthly expenditure across three usage scenarios.

## Model 4: Batching, Streaming, and the Cost Formula

**Batching** accumulates multiple requests and submits them together. Most providers offer a batch API at 50% of the standard price; the tradeoff is latency: batch jobs may take minutes to hours to complete. Batching is appropriate for workloads that are **not latency-sensitive**: nightly document processing, bulk embedding generation, offline evaluation runs. It is inappropriate for a user waiting at a screen for a chat response.

**Streaming** reduces *time-to-first-token* by returning tokens to the user as they are generated rather than waiting for the full response to complete before sending anything. Streaming does not reduce the total number of tokens generated and does not reduce cost. It improves perceived responsiveness and allows the UI to begin rendering before the response is complete — which feels faster even when the total time is the same.

Before deploying any agent system, build a **cost model**: a spreadsheet or script that estimates daily expenditure given realistic usage assumptions. The structure:

$$
\text{daily cost} = Q \times (T_{\text{in}} \times P_{\text{in}} + T_{\text{out}} \times P_{\text{out}})
$$

where $Q$ is queries per day, $T_{\text{in}}$ is average input tokens per query, $T_{\text{out}}$ is average output tokens per query, and $P_{\text{in}}$, $P_{\text{out}}$ are the per-token prices in dollars. Add separate terms for cache miss rate (what fraction of requests are not cached), embedding costs (a separate cheaper rate), and tool-call overhead (extra tokens from retrieved context). Then ask: at what query scale does cost become unsustainable, and at what scale does switching to local inference pay off?

### Critical Thinking Questions

7. At what query volume does semantic caching become worth the engineering cost of building and maintaining it? What factors beyond raw query volume matter in this decision?

   *Hint:* Consider: How repetitive are your queries? (A homework helper gets many unique questions; a FAQ bot gets many repeated ones.) What is the risk of serving a slightly stale cached answer? What is the engineering cost of building the cache correctly?

8. A team proposes to reduce cost by streaming responses to users and canceling the generation mid-stream once the user stops reading or scrolls away. What practical and ethical complications does this introduce, even though it would save money?

   *Hint:* Think about what happens if the user missed the most important part of the response (which might be in the second paragraph). Think also about the billing model — does canceling generation mid-stream actually stop the charge, or has the compute already been done?

9. Build a cost model for a hypothetical Ursinus College tutoring agent. Assume: 200 student queries per day, each with a 300-token system prompt, a 100-token student question, and a 250-token answer. Estimate the monthly cost at GPT-4 pricing ($15/$60 per million input/output tokens). Then estimate the cost with a local model running on a GPU that costs $0.50/hour. At what query volume per day does local inference become cheaper than the API?

   *Starter hint:* Run this script and compare the two monthly cost figures — the crossover point where local inference becomes cheaper depends entirely on how fully you can utilize the GPU.
   ```python
   # Cost model for Ursinus tutoring agent
   queries_per_day = 200
   system_prompt_tokens = 300   # input
   question_tokens = 100        # input
   answer_tokens = 250          # output

   price_input_per_million = 15.00   # GPT-4 class
   price_output_per_million = 60.00  # GPT-4 class (4x input)

   input_per_query = system_prompt_tokens + question_tokens
   output_per_query = answer_tokens

   cost_per_query = (
       (input_per_query / 1_000_000) * price_input_per_million +
       (output_per_query / 1_000_000) * price_output_per_million
   )

   daily_cost = queries_per_day * cost_per_query
   monthly_cost = daily_cost * 30
   print(f"Monthly API cost: ${monthly_cost:.2f}")

   # Local model: GPU runs 24/7 regardless of query volume
   gpu_cost_per_hour = 0.50
   monthly_gpu_cost = gpu_cost_per_hour * 24 * 30
   print(f"Monthly local GPU cost: ${monthly_gpu_cost:.2f}")
   ```

   *You've succeeded when:* You can state the monthly API cost, the monthly local GPU cost, and the query volume per day at which local inference becomes cheaper — and explain why the crossover point depends heavily on GPU utilization.

---

## Exercises

1. *Token budget audit.*

   *What to do:* Take your final project agent and instrument it to log the number of input and output tokens used in each API call. Run 10 representative queries through your agent. Calculate the average cost per query and project it to a daily and monthly cost assuming 500 queries/day. Identify the single largest contributor to token cost and propose one specific change to reduce it.

   *Starter hint:* Most LLM APIs return token usage in the response object. For Anthropic: `response.usage.input_tokens` and `response.usage.output_tokens`. For OpenAI: `response.usage.prompt_tokens` and `response.usage.completion_tokens`. Log these to a CSV file and compute averages across your 10 runs.

   *You've succeeded when:* You have a table showing per-call token counts for all 10 runs, a projected monthly cost, and a specific actionable proposal (e.g., "shorten the system prompt from 800 to 300 tokens by removing the detailed formatting rules") with an estimated savings percentage.

2. *Caching design.*

   *What to do:* For your final project, identify which parts of your prompt are static (identical on every call) and which are dynamic (vary per user or per query). Redesign your prompt structure so that all static content appears first. Estimate the cache hit rate you would achieve if prompt caching were enabled, and calculate the monthly savings.

   *Starter hint:* Draw a diagram of your current prompt structure showing: [SYSTEM PROMPT] -> [RETRIEVED CONTEXT] -> [USER MESSAGE]. Mark each section as Static (same every call) or Dynamic (changes per call). Static content that appears before any dynamic content is cacheable; dynamic content anywhere in the prefix breaks caching for everything after it.

   *You've succeeded when:* You can produce an annotated prompt diagram, a cache-hit-rate estimate with reasoning, and a dollar-amount monthly savings estimate using the formula from Model 4.

3. *Cost model spreadsheet.*

   *What to do:* Build a cost model for your final project as a Python script or spreadsheet. The model should accept as parameters: queries per day, average input tokens, average output tokens, cache hit rate, and per-token prices. It should output: cost per query, daily cost, monthly cost, and the query volume at which switching to a local model becomes cheaper. Run the model for three scenarios: current usage, 10x growth, and 100x growth.

   *Starter hint:* Use the formula from Model 4: `daily_cost = Q * ((T_in * P_in) + (T_out * P_out))`. Add a cache term: `effective_input_cost = T_in * ((1 - cache_hit_rate) * P_in + cache_hit_rate * P_cache_read)`. Present results in a table with one column per scenario.

   *You've succeeded when:* Your model produces a three-scenario table, correctly applies the cache discount, and identifies the crossover point where local inference becomes cheaper with a brief written explanation of what drives that crossover.

---

-> Coming Up Next: Cost is one constraint on how we build AI systems. The next module examines another: the cognitive science of how humans and AI systems make decisions — and what happens when those processes collide.

## Further Reading

- Anthropic. *Prompt Caching* (API documentation, 2024).
- Zhuang et al. *GPTCache: An Open-Source Semantic Cache for LLM Applications* (2023).
- Ong et al. *RouteLLM: Learning to Route LLMs with Preference Data* (2024).
- OpenAI. *Batch API* (documentation, 2024).

> **From the Environmental Cost of Inference session.** Right-sizing is the same decision this activity makes on dollars, made on watts; the matrix below is that session's version.

## Model 2: Right-Sizing Decision Matrix

| Task | Appropriate Model Scale | Rationale for Scale Choice | Local vs. Cloud Preference | Environmental Trade-off |
|---|---|---|---|---|
| Classify incoming email as spam or not spam | Fine-tuned small model (1B parameters or fewer) | Binary classification is a well-defined, low-complexity task with massive labeled data available for fine-tuning to high accuracy | Local or edge; no real-time cloud round-trip needed | Highest environmental benefit from right-sizing; frontier model here is ~100x over-powered |
| Summarize a 10-page PDF | Mid-size model (7B-13B parameters) | Requires coherent abstractive reasoning but the document fits in context and 7B models handle it well | Local is viable on consumer hardware; cloud for convenience | Local on a modern laptop adds ~0.07 kg/8h; cloud call at ~0.0005 kg is lower for a single summary |
| Generate a photorealistic logo | Diffusion model (specialized architecture) | Image synthesis requires a different architecture from text; quality depends heavily on model scale and fine-tuning | Cloud typical; GPU requirements for quality generation are high | Per-image cost is low; volume at production scale becomes significant |
| Debug a 500-line codebase with cross-file dependencies | Large model (30B+ parameters) with code specialization | Complex multi-step reasoning across a large context window; rare error patterns benefit from extensive training data | Cloud preferred; local possible on high-end hardware | Justified higher cost because smaller models fail measurably on this task class |
| Answer a trivia question | Any scale, including very small models | Low reasoning demand; factual recall; fast response is more important than depth | Local sufficient; cloud API call is unnecessary overhead for this task | Largest unnecessary expense: routing simple factual queries to frontier models |
| Transcribe and summarize a 2-hour lecture | Specialized speech model plus a lightweight summarizer | Two-model pipeline; transcription model is heavily optimized for audio; summarizer is a lightweight text task | Local is fully feasible; privacy argument is strong for lecture content | Demonstrates that task decomposition can reduce energy relative to a single large model |

### Critical Thinking Questions

4. The right-sizing matrix does not include a column for accuracy. Construct the missing argument: under what conditions does using a smaller model for a task impose a *social* cost that must be weighed against the carbon benefit?

   *Hint: Consider a medical triage task or a hiring screening task where the smaller model's error rate is meaningfully higher. Who bears the cost of those errors? Are those costs visible in the same accounting that makes the carbon benefit visible? Is there a way to measure both in the same units?*

5. The "local-first" principle is often presented as unambiguously better. Identify two scenarios where local inference has *worse* environmental impact than a well-managed cloud inference endpoint, and explain why.

   *Hint: Think about what happens when many individual users each run a model on their own hardware versus one highly optimized cloud endpoint serving the same workload. Think about hardware utilization rates, cooling efficiency, and renewable energy purchasing. When does centralization have an environmental advantage?*

6. You are advising a nonprofit organization that does document analysis for human rights investigations — processing thousands of witness testimonies in multiple languages. They currently use a frontier cloud API. What model-choice and deployment recommendations would you make, and how would you weigh privacy, accuracy, cost, and carbon against each other?

   *Hint: Start by listing the constraints: the testimonies are highly sensitive (privacy argument for local), multi-language capability is required (accuracy constraint), the organization has limited budget (cost constraint), and the work matters (accuracy cost of a wrong inference is high). Where do these constraints converge, and where do they conflict?*

A development team wants to reduce the carbon footprint of their AI-powered customer support system. Which intervention is most likely to produce the largest reduction in inference-time carbon emissions?

[( )] Switching from Python to a compiled language for the API wrapper — runtime efficiency gains in the surrounding code are in the microsecond range, whereas the model forward pass dominates at the millisecond-to-second scale; the wrapper is not the bottleneck
[( )] Adding a caching layer that serves identical responses to repeated queries without re-running the model — caching is a meaningful lever but only eliminates compute for exact or near-duplicate queries; a customer support system with diverse question phrasing will still run the full model for the majority of requests
[(X)] Replacing a 70B-parameter frontier model with a fine-tuned 7B-parameter model that achieves equivalent accuracy on the support domain — a 10x reduction in model size directly cuts inference compute by roughly 10x
[( )] Purchasing carbon offsets equal to the service's measured emissions — offsets shift accounting responsibility but do not reduce the actual energy the model consumes per query; the compute load and its direct energy draw remain identical

---

*Parts I and II focused on choices you can make as an individual developer. Part III zooms out to ask: what happens when everyone makes those choices — and whether efficiency gains collectively reduce impact or accidentally increase it.*

