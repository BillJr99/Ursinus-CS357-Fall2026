# Serving LLMs in Production: Latency, Cost, and Throughput
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-llmserving.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-llmserving.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Serving LLMs in Production: Latency, Cost, and Throughput

Once a model is trained and running locally, the next challenge is *serving* it efficiently: balancing how fast users get their first response, how cheaply the system runs, and how many requests it can handle simultaneously — and these three goals trade off in ways that every AI practitioner must understand.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Manager keeps the team on pace through the three Parts; the Recorder captures every numerical estimate and result from the code cells; the Presenter prepares a two-minute summary of the throughput findings for the class discussion; the Reflector tracks every assumption the team makes and flags the one they are least confident about. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **TTFT (Time to First Token)** | The elapsed time from when a request is submitted until the very first output token arrives — this is what determines how long the user waits before they see *anything* appear on screen | A streaming chatbot with TTFT of 500ms feels snappy; one with TTFT of 3s feels broken |
| **TPOT (Time Per Output Token)** | The average time between successive output tokens once generation has started — this controls the *pace* of streaming text and whether reading feels natural | At 40 ms/token the text appears faster than a person can comfortably read; at 200 ms/token it feels sluggish |
| **Prefill phase** | The step where the model processes all input tokens (prompt, system prompt, retrieved context) in parallel using the GPU — this phase is fast per-token but its wall-clock time scales with prompt length | A 2,000-token prompt takes roughly 4× longer to prefill than a 500-token prompt |
| **Decode phase** | The step where the model generates output tokens one at a time, each token fed back as the next input — this phase is inherently sequential and cannot be parallelized within a single request | Generating 200 tokens takes 200 sequential forward passes through the model |
| **KV cache** | A memory buffer that stores the key and value tensors computed during the prefill phase so they do not need to be recomputed for every new output token — the primary mechanism that makes generation fast enough to be practical | Without KV cache, generating token 200 would re-read all 199 previous tokens; with it, only the new token's attention is computed |
| **Continuous batching** | A scheduling strategy where the serving engine adds new requests to a running batch as soon as slots open up, rather than waiting for all requests in a batch to finish before accepting new ones | A request that finishes after 50 tokens frees its GPU slot for a new request immediately, rather than waiting for the slowest request in the batch to reach its limit |
| **Static batching** | A simpler scheduling strategy where a fixed group of requests is processed together from start to finish, with no new requests admitted until all members of the batch complete | A batch of 8 requests runs to completion; a 1-token request and a 500-token request finish in the same batch wall-clock time (the maximum) |
| **Throughput** | The total number of tokens the serving system generates per second across all requests — the measure of how efficiently the hardware is utilized | A batch of 8 simultaneous requests may achieve 800 tokens/sec total while a single request achieves only 120 tokens/sec |
| **PagedAttention** | A KV-cache memory-management scheme that stores the cache in small fixed-size *blocks* that can live anywhere in GPU memory, mapped through a block table — the same trick an operating system uses for virtual memory | Instead of one 2,048-token contiguous reservation per request, the cache is 128 blocks of 16 tokens each, allocated only as the sequence grows |
| **Memory fragmentation** | Wasted GPU memory that exists but cannot be used: *internal* (reserved-but-unfilled space inside a request's block), *external* (gaps between allocations too small to reuse), and *redundant duplication* (the same system prompt cached separately per request) | A request reserves 2,048 tokens but uses 500; the other 1,500 are internally fragmented — present but unavailable to anyone else |
| **Prefix caching** | Reusing the already-computed KV cache for a shared prompt prefix (e.g., a common system prompt) across requests, so its prefill is computed once and pointed to, not recomputed | Ten chat requests share a 400-token system prompt; with prefix caching the prefill for those 400 tokens runs once, not ten times |
| **Chunked prefill** | A scheduling strategy that breaks a long prefill into smaller chunks and interleaves them with ongoing decode steps, so decode latency does not stall behind a big prompt | A 4,000-token prompt is prefilled 512 tokens at a time between decode steps, keeping other users' tokens flowing |
| **Speculative decoding** | A latency optimization where a small *draft* model proposes several tokens and the large model verifies them in one forward pass — output is mathematically identical to the large model alone | The draft model guesses "the cat sat on the"; the large model confirms 4 of 5 guesses in a single pass instead of five |

---

# Part I: Latency Metrics — TTFT, TPOT, and What Users Actually Feel

In this part, you will learn to distinguish the two latency metrics that govern user experience for LLM applications, understand why each one matters differently depending on the use case, and build intuition for the prefill/decode split that underlies both.

## Model 1: Latency Tradeoffs by Use Case

Not all latency is equal. A user in a streaming chat conversation notices the time until the first word appears (TTFT) far more acutely than the exact pace of subsequent tokens. A batch summarization job running overnight does not care about TTFT at all — it cares about throughput and total job completion time. A code autocomplete tool (which must complete before the developer types the next character) cares about both simultaneously.

The table below maps five realistic use cases to the metric that dominates user experience.

| Use Case | Primary Metric | Why | Acceptable Target |
|---|---|---|---|
| **Streaming chat assistant** | TTFT | Users interpret a blank screen as broken or slow; once text starts flowing, most tolerate moderate TPOT | TTFT < 500 ms feels interactive |
| **Code autocomplete (inline)** | TTFT + TPOT both | The suggestion must appear before the developer moves on; it must complete fast enough to be useful | Total time < 200 ms end-to-end |
| **Overnight batch summarizer** | Throughput (tokens/sec) | No human is watching; the goal is total documents processed per hour per dollar | TTFT irrelevant; maximize tokens/hour |
| **Voice assistant** | TTFT (strict) | Text-to-speech cannot begin until the first sentence is available; silence feels like a crash | TTFT < 300 ms to first sentence |
| **Document-grounded Q&A (RAG)** | TTFT + total latency | The retrieval step already adds latency before generation begins; users expect a complete answer, not streaming | TTFT < 1 s; complete in < 5 s |

### Why Prefill Dominates TTFT

During the **prefill phase**, the model reads every input token in a single parallel forward pass — one matrix multiply across the full prompt. This is GPU-efficient (parallelism is high) but takes real wall-clock time proportional to prompt length. A 4,000-token RAG prompt with retrieved documents takes roughly 8× longer to prefill than a 500-token chat turn. Every millisecond of prefill adds directly to TTFT.

During the **decode phase**, the model generates tokens one at a time. Each step is fast in isolation (the KV cache eliminates recomputation of prior tokens) but cannot be parallelized within a single stream. TPOT is roughly constant per request and set by model size and hardware — making it more predictable than TTFT.

The practical implication: **to improve TTFT, shorten prompts or use a smaller model; to improve TPOT, use faster hardware or quantize the model further.** These levers are mostly independent.

### Critical Thinking Questions

1. A startup is building a real-time voice assistant where the model's text output is immediately spoken aloud. Their current TTFT is 800 ms and TPOT is 30 ms/token. Which metric should they optimize first, and why? What architectural change would you investigate first?

   > *Hint: Think about what "text-to-speech" requires before it can produce any sound. Also consider: does the TTS engine need the full response or just the first sentence?*

2. A research team runs a nightly batch job that summarizes 10,000 academic papers. Their single-request TTFT is 2 seconds and their throughput at batch size 1 is 80 tokens/sec. Which metric is irrelevant for their use case, and what should they optimize instead?

   > *Hint: If no human is watching the output appear, what cost matters? If their GPU is idle 70% of the time between requests, what does that suggest about their batch size?*

3. The prefill phase for a 500-token prompt takes 120 ms on a given GPU. Estimate the prefill time for a 4,000-token RAG prompt on the same hardware. If TPOT is 25 ms and the response is 150 tokens, what is the total end-to-end latency for each case?

   > *Hint: Prefill time scales roughly linearly with prompt length for transformer models (each token attends to all prior tokens, so work is proportional to $n$). Decode time is simply TPOT × output tokens. Add them.*

[[MC]]
A product team is building a streaming chat assistant where the model's response appears word-by-word in a chat bubble. A user complains "the response takes forever to start but then comes out fast." Which metric is the primary problem?
- (x) TTFT — the time to first token is too high, causing the perceived "blank" period before text begins
- ( ) TPOT — tokens are arriving too slowly once generation begins, making the text crawl
- ( ) Throughput — the system is handling too many concurrent users, starving this user's request
- ( ) Context length — the user's prompt is too long, causing a timeout before the response begins

> **⚠️ Common Misconception:** Many practitioners treat "latency" as a single number and optimize it uniformly. In reality, TTFT and TPOT are controlled by different system components — TTFT depends heavily on prompt length, model prefill speed, and queue wait time; TPOT depends on model size, quantization level, and hardware memory bandwidth. Reducing one does not necessarily reduce the other. Always measure both separately before deciding where to invest engineering effort.

---

# Part II: KV Cache and Batching — Making the GPU Work Harder

In this part, you will understand why the KV cache is the central mechanism that makes LLM generation practical, contrast static and continuous batching strategies, and run a simulation that shows concretely how throughput scales with batch size.

## Model 2: The KV Cache — Compute Once, Reuse Always

During the decode phase, the attention mechanism needs the key (K) and value (V) tensors for every previous token in the sequence to compute the next token's attention scores. Without a cache, generating token $t$ would require re-reading and re-computing the K and V tensors for tokens $1$ through $t-1$ — meaning the work to generate a 200-token response would be proportional to $1 + 2 + 3 + \ldots + 200 = 20{,}100$ forward passes instead of 200.

The **KV cache** eliminates this redundancy. After the prefill phase computes K and V for all input tokens, those tensors are stored in GPU memory. Each decode step appends the new token's K and V tensors to the cache, then reads the full cache for the attention computation. The critical tradeoff: **KV cache consumes GPU memory proportional to context length × number of layers × head dimension**, and this memory is unavailable for model weights or other requests. A 128K-context request on a large model can consume dozens of gigabytes of KV cache alone.

This memory pressure is why **batch size and context length are in tension**: more simultaneous requests means more KV caches, which means less memory per request, which means shorter maximum context each request can use.

## Model 3: Static vs. Continuous Batching

**Static batching** is simple: collect a fixed number of requests into a batch, run them together from first token to last token, then collect the next batch. The flaw is that requests within a batch have different natural lengths — a 10-token response and a 500-token response finish at different times, but in static batching, the 10-token request's GPU slot sits idle for the remaining 490 steps, waiting for the slowest request to finish.

**Continuous batching** (also called iteration-level scheduling) treats each forward pass as a separate scheduling opportunity. As soon as any request in the current batch finishes (or pauses waiting for input), its slot is freed and the next waiting request is slotted in — within the same forward pass. This keeps GPU utilization high because the hardware is never idling on finished-but-not-cleared requests.

The code cell below simulates both strategies with a simple Python scheduler. It is not a real inference engine — it uses wall-clock time estimates from empirical measurements — but it captures the structural difference in how slots are managed and what effect that has on throughput.

## Code Cell: Batching Scheduler Simulation

The following simulation models a queue of requests with different prompt lengths and response budgets. It estimates total wall-clock time and throughput (tokens/sec) for batch sizes of 1, 4, and 8 under both static and continuous batching strategies. Read the comments carefully — they explain each assumption made.

```python
import math
import random

# ──────────────────────────────────────────────────────────────
# Simulation parameters — adjust these to model your hardware
# ──────────────────────────────────────────────────────────────

# Empirical estimates for a mid-range GPU (e.g., RTX 3090) with a ~7B model at 4-bit
PREFILL_MS_PER_TOKEN = 0.25    # ms per input token during prefill (parallel, fast)
DECODE_MS_PER_TOKEN  = 12.0    # ms per output token during decode (sequential, slower)
# Batching reduces effective per-token decode time because the GPU is better utilized:
BATCH_SPEEDUP = {1: 1.0, 4: 0.45, 8: 0.28}  # multiplier on DECODE_MS_PER_TOKEN

random.seed(42)

# Generate a realistic queue of 32 requests with varied prompt/response lengths
requests = []
for i in range(32):
    prompt_tokens  = random.randint(50, 800)   # short chat to long RAG prompt
    output_tokens  = random.randint(30, 300)   # brief answer to detailed response
    requests.append({"id": i, "prompt": prompt_tokens, "output": output_tokens})

total_output_tokens = sum(r["output"] for r in requests)

# ──────────────────────────────────────────────────────────────
# Static batching: process requests in fixed-size batches.
# Each batch runs until the *slowest* request finishes.
# ──────────────────────────────────────────────────────────────
def static_batching(requests, batch_size, decode_speedup):
    total_ms = 0.0
    for batch_start in range(0, len(requests), batch_size):
        batch = requests[batch_start : batch_start + batch_size]
        # Prefill: the batch's slowest (longest) prompt sets the wall-clock prefill time
        max_prefill_tokens = max(r["prompt"] for r in batch)
        prefill_ms = max_prefill_tokens * PREFILL_MS_PER_TOKEN
        # Decode: the batch runs until the longest output finishes
        max_output_tokens = max(r["output"] for r in batch)
        decode_ms = max_output_tokens * DECODE_MS_PER_TOKEN * decode_speedup
        total_ms += prefill_ms + decode_ms
    return total_ms

# ──────────────────────────────────────────────────────────────
# Continuous batching: model each forward pass as a scheduling
# event. Finished requests free their slot immediately.
# This is a simplified token-step simulation.
# ──────────────────────────────────────────────────────────────
def continuous_batching(requests, batch_size, decode_speedup):
    queue = list(requests)          # waiting to start
    active = []                     # currently in a batch slot
    completed_tokens = {}           # tokens generated so far per request id
    total_ms = 0.0

    # Seed initial batch
    while len(active) < batch_size and queue:
        r = queue.pop(0)
        # Prefill this request immediately
        total_ms += r["prompt"] * PREFILL_MS_PER_TOKEN
        completed_tokens[r["id"]] = 0
        active.append(r)

    # Simulate token-by-token decode steps
    while active:
        step_ms = DECODE_MS_PER_TOKEN * decode_speedup
        total_ms += step_ms
        finished = []
        for r in active:
            completed_tokens[r["id"]] += 1
            if completed_tokens[r["id"]] >= r["output"]:
                finished.append(r)
        for r in finished:
            active.remove(r)
            # Immediately slot in next waiting request (continuous batching)
            if queue:
                new_r = queue.pop(0)
                total_ms += new_r["prompt"] * PREFILL_MS_PER_TOKEN
                completed_tokens[new_r["id"]] = 0
                active.append(new_r)

    return total_ms

# ──────────────────────────────────────────────────────────────
# Run and report
# ──────────────────────────────────────────────────────────────
print(f"{'Strategy':<25} {'Batch':>5} {'Time (s)':>10} {'Throughput (tok/s)':>20}")
print("-" * 65)

for bs in [1, 4, 8]:
    speedup = BATCH_SPEEDUP[bs]

    static_ms = static_batching(requests, bs, speedup)
    static_tps = total_output_tokens / (static_ms / 1000.0)
    print(f"{'Static batching':<25} {bs:>5} {static_ms/1000:>10.2f} {static_tps:>20.1f}")

    cont_ms = continuous_batching(requests, bs, speedup)
    cont_tps = total_output_tokens / (cont_ms / 1000.0)
    print(f"{'Continuous batching':<25} {bs:>5} {cont_ms/1000:>10.2f} {cont_tps:>20.1f}")

print()
print(f"Total output tokens across all 32 requests: {total_output_tokens}")
print()
print("Observation: Larger batch sizes improve throughput but do NOT")
print("directly improve any individual request's TTFT or TPOT.")
```

### Critical Thinking Questions

1. In the simulation output, continuous batching at batch size 8 should outperform static batching at batch size 8. Explain in your own words *why* — what is happening at the slot level that the static scheduler wastes?

   > *Hint: Imagine a batch of 8 requests where one finishes after 30 output tokens and the others need 300. In static batching, what is the 30-token request's GPU slot doing during the remaining 270 decode steps?*

2. The simulation uses `BATCH_SPEEDUP` coefficients to model reduced per-token decode time at larger batch sizes. Why does batching reduce the effective decode time per token? What hardware property does this exploit?

   > *Hint: GPUs execute operations in parallel across many cores. A single request uses only a fraction of available GPU cores; multiple requests in the same batch allow more cores to be active simultaneously, amortizing the per-step overhead.*

3. Modify `PREFILL_MS_PER_TOKEN` to 2.0 (simulating a larger model) and re-run. Which strategy benefits more from this change, and at which batch sizes? What does this tell you about when continuous batching's advantage is largest relative to static batching?

   > *Hint: With a longer prefill time, the "wasted slot" time in static batching is the same absolute amount, but now a larger fraction of total wall-clock time. Does continuous batching's slot-reuse help more when prefill is long or when decode is long?*

[[MC]]
A serving system uses static batching with a fixed batch size of 8. One request in the current batch generates only 5 output tokens; the other 7 requests each need 400 output tokens. During the decode phase, after the 5-token request finishes, what happens to its GPU slot?
- ( ) It is immediately assigned to the next waiting request in the queue
- ( ) It is used to speed up the remaining 7 requests by distributing their decode work
- (x) It sits idle until all 7 remaining requests finish their 400 tokens, then the entire batch is cleared
- ( ) The serving engine automatically switches to continuous batching for the remainder of this batch

> **⚠️ Common Misconception:** Students often assume that "increasing batch size always improves user experience." Batch size is a throughput knob, not a latency knob. Increasing batch size increases the total number of tokens the system generates per second across all requests, which reduces cost and improves hardware utilization — but it can *increase* TTFT for individual requests, because a newly arriving request may have to wait in the queue for a batch slot to open. The user-level perception is: the system handles more total load, but individual responses may start later. Choose batch size based on your service's primary objective.

---

# Part III: Cost Modeling — Local vs. Hosted, Small vs. Large

In this part, you will build a concrete cost model for LLM inference, compare the economics of local and hosted deployment, and design a simple routing policy that minimizes cost while maintaining quality.

## Model 4: The Economics of Inference

Running a model has two fundamentally different cost structures depending on where it runs.

**Hosted models** charge per token. The bill arrives with the request — no upfront investment, no idle cost, but the per-token price is non-zero and accumulates quickly at scale. The cost to serve one million output tokens from a large hosted model is in the range of tens to hundreds of dollars depending on provider and model tier.

**Local models** have zero marginal cost per token once the hardware is running — but the hardware itself has a fixed cost (purchase price, depreciation, electricity) that must be amortized over the model's usage. A developer running Ollama on a personal laptop pays in opportunity cost (the GPU cannot do other things) and electricity, not per-token fees. An organization running a dedicated GPU server pays hardware amortization plus power plus cooling.

The crossover point — where local becomes cheaper than hosted — depends on **utilization rate**: how many tokens per day the system generates. Low utilization favors hosted (you only pay for what you use); high sustained utilization favors local (you pay a fixed cost regardless of volume).

## Model 5: When to Route to a Smaller Model

**Model routing** directs each incoming query to the cheapest model tier capable of handling it correctly. The key insight is that not all queries need frontier capability. Factual lookup, format extraction, translation, and short summarization tasks often perform identically on small and large models; complex multi-step reasoning, ambiguous open-ended generation, and tasks requiring broad world knowledge are where large models earn their cost premium.

A routing policy needs three components: a **classifier** that predicts query difficulty, a **threshold** that determines when to escalate to the larger model, and **feedback** from user ratings or LLM-as-judge to calibrate the classifier over time.

## Exercises

**Exercise 1: Cost Comparison Worksheet**

A startup serves a customer-support chatbot. It handles 500,000 user turns per day. Each turn has an average input of 400 tokens (system prompt + history + user message) and an average output of 150 tokens. They are choosing between three deployment options:

| Option | Input cost (per 1M tokens) | Output cost (per 1M tokens) | Fixed cost/month |
|---|---|---|---|
| Hosted large model | $3.00 | $12.00 | $0 |
| Hosted small model | $0.25 | $0.80 | $0 |
| Local GPU server (7B model at 4-bit) | $0 | $0 | $2,400 (hardware + power amortized) |

- *What to do*: Compute the monthly cost for each option. Assume 30 days per month and that the local model can handle 100% of queries at acceptable quality (an optimistic assumption the team should validate). Then compute the cost if the startup routes 70% of queries to the small hosted model and 30% to the large hosted model (a routing policy).
- *Starter hint*: Monthly tokens = 500,000 turns/day × 30 days × (400 input + 150 output) tokens/turn. For the routing policy, apply 70/30 to each model's per-token price separately.
- *You've succeeded when*: You have a table with four rows (three single-model options plus the routing policy) showing monthly cost, and you can identify the crossover utilization level at which local becomes cheaper than the small hosted model.

**Exercise 2: Routing Policy Design**

Design a simple routing policy for the following scenario: a homework-help agent that receives a mix of (a) factual lookup questions ("What year did World War I end?"), (b) multi-step math problems, and (c) open-ended essay feedback requests.

- *What to do*: Propose a classifier that routes each query type to a specific model tier (you may use "small local," "medium hosted," and "large hosted" as your three tiers). Describe the signal your classifier uses (keywords, prompt length, task type), the expected accuracy of each routing decision, and the cost consequence of a misclassification (routing a complex task to the small model, or a simple task to the large model).
- *Starter hint*: Think about what signals correlate with query difficulty. Prompt length is a weak but free signal. Presence of mathematical notation, code, or multi-part instructions is a stronger signal. Can you write three `if/elif/else` rules that capture 80% of cases correctly?
- *You've succeeded when*: Your policy has explicit rules, estimated routing accuracy for each query type, and a sentence explaining what happens to the user experience when the classifier makes the most likely error for each type.

**Exercise 3: The Full Stack Cost Model**

You are advising a research lab that wants to deploy an internal document Q&A system for 20 researchers who each submit approximately 50 queries per day. Queries average 1,200 tokens of input (system prompt + retrieved chunks + question) and 300 tokens of output. The lab has one older GPU server (16 GB VRAM) available, which can run a 7B model at 4-bit quantization with TPOT of 40 ms/token and no per-token cost, or they can use a hosted API.

- *What to do*: Compute the monthly cost for (a) hosted large model, (b) hosted small model, and (c) local GPU server. Identify whether the local server's VRAM is sufficient for the average request's KV cache — a 1,200-token input context with a 7B model at 4-bit uses approximately 400 MB of KV cache per concurrent request. With 16 GB VRAM and ~4 GB of model weights, estimate the maximum number of concurrent requests the local server can handle. Given 20 researchers, estimate whether this is a bottleneck.
- *Starter hint*: Monthly queries = 20 researchers × 50 queries/day × 30 days = 30,000 queries. For KV cache capacity: available VRAM = 16 GB − 4 GB weights = 12 GB; at 400 MB per concurrent request, max concurrent = floor(12,000 MB / 400 MB). For peak concurrency estimation, assume researchers work 8 hours per day uniformly.
- *You've succeeded when*: You have a monthly cost comparison table, a maximum concurrent request estimate for the local server, and a one-sentence recommendation for whether the lab should use local or hosted inference for this use case.

---

# Part IV: PagedAttention — Managing KV Cache Memory

Part II established *why* the KV cache exists — it trades memory for compute so decode does not re-read every prior token. This part answers the question that immediately follows: once you commit to caching, **how do you lay that cache out in GPU memory** for hundreds of concurrent requests of wildly different lengths? The answer, from the vLLM project, is to borrow the oldest idea in operating systems — virtual memory paging — and apply it to the KV cache. This part shows the waste that motivated it, the mechanism itself, and the four knobs you actually turn in a deployment.

## Model 6: The Naive Allocation Problem

Start with the memory budget. Model weights are the fixed cost of being open for business. A 13-billion-parameter model at FP16 (2 bytes per parameter) needs roughly **26 GB** just for its weights. On a 40 GB GPU that is about **65% of the card gone before a single user connects** — see the VRAM sizing math in `liascript-hardwarequantization.md` for where that number comes from. Everything else — the KV cache for *every* active request — has to fit in the remaining ~35%.

Traditional serving systems manage that 35% badly, in three distinct ways:

| Fragmentation type | What it is | Concrete example |
|---|---|---|
| **Internal** | Each request pre-reserves a *contiguous* block sized for the maximum possible output length, then leaves most of it empty | Max context 2,048 tokens, but the average user sends 200 and gets 300 back → ~1,500 tokens of cache reserved and empty, per request |
| **External** | Requests of different lengths finish and free their blocks, leaving gaps too small or too scattered to reuse | 500 tokens of free memory exists in total, but no single contiguous 500-token region → a new request cannot be admitted |
| **Redundant duplication** | The same system prompt is prefilled and cached separately for every concurrent request | 100 requests sharing one 400-token system prompt store 100 copies of its KV cache |

The published PagedAttention research measured the result: traditional systems waste roughly **60–80% of the KV-cache memory** — the very memory that determines how many users you can serve at once. The pattern should feel familiar: it is exactly the internal/external fragmentation that motivated paged virtual memory in operating systems half a century ago.

### Critical Thinking Questions

1. A request reserves a contiguous 2,048-token block but generates only 250 tokens before the user closes the tab. How much of that block is internally fragmented, and why can no *other* request use it even though the GPU has "free" memory?

   > *Hint: Internal fragmentation is reserved-but-unfilled space inside one request's own allocation. What makes the leftover unavailable is that it was committed to this request up front. How many tokens are wasted here?*

2. Your GPU reports 900 tokens' worth of free KV-cache memory, but a new request needing a 600-token contiguous block is rejected. Which fragmentation type is responsible, and what OS concept is this identical to?

   > *Hint: Free memory exists but not in one usable piece. This is the same reason an OS with plenty of free RAM can still fail a large contiguous `malloc` before virtual memory paging solved it.*

3. A customer-support deployment gives all 100 concurrent users the same 500-token system prompt. Estimate the KV-cache memory wasted to redundant duplication versus storing that prefix once. What later optimization in this activity eliminates exactly this waste?

   > *Hint: 99 redundant copies of a 500-token prefill. Which of the four tuning knobs in Model 8 is designed for shared prefixes?*

[[MC]]
A serving system pre-allocates a contiguous block sized to the maximum context length for every request. A user sends a 200-token prompt and gets a 300-token answer, well under the 2,048-token maximum. What is the ~1,500 tokens of unused reserved space called?
- ( ) External fragmentation — the gaps are between allocations
- (x) Internal fragmentation — the waste is reserved-but-unfilled space inside the request's own block
- ( ) Redundant duplication — the same content is stored twice
- ( ) A KV cache miss — the tokens were evicted and must be recomputed

## Model 7: PagedAttention — Virtual Memory for the KV Cache

PagedAttention applies the operating-system insight directly. Instead of one contiguous reservation per request, it breaks the KV cache into small **fixed-size blocks** — by default **16 tokens each** — that can live *anywhere* in GPU memory, non-contiguous, and are allocated **on demand** as the sequence actually grows. A lightweight **block table** maps each request's *logical* block addresses (what the attention computation sees as a continuous sequence) to the *physical* block addresses where they really sit in VRAM. This is precisely the logical-page-to-physical-page mapping in an OS page table.

| | Contiguous pre-allocation (naive) | Paged blocks (PagedAttention) |
|---|---|---|
| **Unit of allocation** | One block sized to max context, per request | Many 16-token blocks, allocated as needed |
| **Placement in VRAM** | Must be one contiguous region | Anywhere; non-contiguous is fine |
| **When allocated** | Up front, at request admission | On demand, as tokens are generated |
| **Internal fragmentation** | Up to (max length − actual length) per request | At most 15 tokens in the last partial block |
| **Shared prefixes** | Impossible — each block is private | Two requests can point their block tables at the *same* physical blocks |

Two consequences fall out of this design. First, internal fragmentation drops from "up to thousands of tokens per request" to "at most 15 tokens in the final partial block." Second — and this is what enables prefix caching in the next model — because logical blocks map through a table to physical blocks, **two different requests can map their logical blocks to the *same* physical blocks**, so a shared system prompt is stored once and pointed to many times, exactly like copy-on-write shared pages in an OS.

### Critical Thinking Questions

1. Explain, in your own words, what the block table maps and why that indirection is what makes non-contiguous allocation possible. What is the exact operating-system structure it mirrors?

   > *Hint: The attention math needs to see a continuous sequence of tokens; the physical blocks are scattered. What sits between "logical position" and "physical location" to reconcile the two?*

2. With a block size of 16 tokens, what is the *maximum* internal fragmentation for any single request under PagedAttention, regardless of how long the request is? Contrast this with the naive scheme's worst case.

   > *Hint: Only the last block can be partially filled. If a request ends mid-block, how many token-slots at most are wasted? Compare to reserving 2,048 tokens for a 300-token answer.*

3. PagedAttention lets two requests' block tables point at the same physical blocks. Which of the three fragmentation problems from Model 6 does that directly eliminate, and what OS mechanism is it analogous to?

   > *Hint: Think about the 100 users sharing one system prompt. What OS feature lets multiple processes share one physical copy of read-only memory?*

[[MC]]
In PagedAttention, what does the block table map?
- ( ) Token IDs to their embedding vectors
- ( ) Model weights to GPU cores
- (x) A request's logical block addresses to the physical block addresses in VRAM where the KV data actually sits
- ( ) Prompts to cached responses

> **⚠️ Common Misconception:** Students often conclude that PagedAttention makes token generation *faster*. It does not speed up the per-token math at all — attention over a paged cache runs at essentially the same speed as over a contiguous one. What PagedAttention removes is *wasted memory*. By reclaiming the 60–80% of KV-cache memory lost to fragmentation, it lets you fit far more concurrent requests on the same GPU. Higher throughput comes from **serving more requests at once**, not from any individual request running faster. Memory efficiency is the lever; concurrency is the payoff.

## Model 8: Four Knobs You Actually Tune

PagedAttention and continuous batching are built into modern serving engines (vLLM and its descendants). What a practitioner *configures* is a small set of knobs on top of them. These are the four worth knowing, roughly in order of how often you reach for them.

| Knob | What it does | Default & guidance |
|---|---|---|
| **`gpu_memory_utilization`** | The fraction of remaining VRAM (after weights) handed to the KV cache | Default **0.9**. Push toward **0.95** on stable, predictable workloads to pack in more concurrent requests; pull back to **0.8** if you see out-of-memory errors under bursty load. Benchmark before committing. |
| **Prefix caching** | Hashes each KV block by its token content so requests that share a prefix (system prompt, RAG boilerplate, few-shot examples) point to the same cached blocks — prefill is computed once | Enable for RAG pipelines, multi-turn chat, and coding agents, where **75–95%** prefix-hit rates are common. Time-to-first-token drops sharply because the shared prefill is skipped entirely. This is the fragmentation-fix from Model 7 turned into a feature. |
| **Chunked prefill** | Breaks a long prefill into chunks and interleaves them with ongoing decode steps, so a big incoming prompt does not stall everyone else's streaming | Enable for throughput-heavy, mixed workloads; production reports cite **~50%** throughput gains. Tune `max_num_batched_tokens` upward alongside it. |
| **Speculative decoding** | A small draft model proposes several tokens; the large model verifies them in one forward pass. Output is *mathematically identical* to the large model alone | Reach for it when **interactive latency matters more than raw throughput**. The gains shrink at very high concurrency, because a full batch already keeps the GPU busy — there is no idle compute for the draft model to exploit. |

The unifying idea: the first three knobs are all about **using the KV-cache memory that PagedAttention freed up more effectively** (pack more, reuse more, stall less), while speculative decoding attacks a different resource — the GPU compute that sits *idle* between memory reads during decode.

### Critical Thinking Questions

1. You are running a RAG assistant where every request begins with the same 1,200-token instruction-and-context preamble. Which knob gives you the biggest time-to-first-token win, and why does the win scale with how many requests share that preamble?

   > *Hint: Which knob is about not recomputing a shared prefix? If the prefill for those 1,200 tokens is computed once instead of per request, what happens to TTFT as concurrency rises?*

2. A deployment sets `gpu_memory_utilization` to 0.95 and runs fine for a week, then starts throwing out-of-memory errors during a traffic spike. Explain the tradeoff and give a specific remediation.

   > *Hint: A higher fraction packs more requests but leaves less headroom for bursts. What value does the guidance suggest under OOM-under-burst conditions?*

3. Speculative decoding's benefit "shrinks at very high concurrency." Connect this to the prefill/decode split from Part I: what resource is the draft model exploiting during decode, and why does a full batch erase that opportunity?

   > *Hint: Decode is memory-bound, so the GPU's compute units are partly idle between memory reads. The draft model fills that idle compute. What happens to idle compute when the batch is already large enough to saturate the GPU?*

[[MC]]
Which tuning knob most directly eliminates the *redundant duplication* waste identified in Model 6 (the same system prompt cached separately per request)?
- ( ) `gpu_memory_utilization` — it changes how much VRAM the cache may use
- (x) Prefix caching — shared prefixes are hashed and stored once, then pointed to
- ( ) Chunked prefill — it interleaves prefill with decode
- ( ) Speculative decoding — a draft model proposes tokens

> **⚠️ Common Misconception:** It is tempting to treat `gpu_memory_utilization` as a "make it faster" dial and crank it to the maximum. It is really a **risk/packing tradeoff**. A higher value admits more concurrent requests (better throughput) but leaves less slack to absorb sudden bursts; when a spike arrives with no headroom, the engine hits out-of-memory and *drops* requests — worse than running slightly under-packed. The right value is workload-specific and found by benchmarking, not by maximizing.

---

## Reflection Prompt

**Personal**: The optimization metrics in this activity — TTFT, TPOT, throughput, cost — are all engineering abstractions. But they map directly to user experience: the frustration of a blank screen, the satisfaction of text that flows as fast as you read. Which metric do you find you care about most as a *user* of AI systems, and did this activity change how you think about why that experience feels the way it does?

**Technical**: The tension between TTFT and throughput is a recurring pattern in computer systems: serving a single user fast versus serving many users efficiently. Where else in computer science have you seen this latency/throughput tradeoff appear? How does the solution in LLM serving (continuous batching, KV cache reuse) compare to solutions in those other domains?

**Societal**: The cost analysis in Part III shows that local inference becomes economically favorable at high utilization, but requires upfront capital investment. What does this imply for who gets to run AI "at cost"? Small startups and individuals pay per-token to hosted providers; large organizations with capital can buy hardware and achieve near-zero marginal cost. Is this an equitable distribution of access? Who does the per-token pricing model benefit and who does it disadvantage?

---

## → Coming Up Next

We have a model running efficiently in production — but what happens when a user or adversary deliberately tries to break it? In the next activity we turn from performance engineering to security engineering: how to find failures in LLM systems before deployment through systematic red-teaming.

---

## 4. Further Reading

- Kwon et al. "Efficient Memory Management for Large Language Model Serving with PagedAttention." SOSP 2023. (The paper that introduced vLLM and continuous KV cache paging — the source for Part IV's fragmentation and block-table material.)
- Agrawal et al. "SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills." arXiv 2023. (Explains the prefill/decode imbalance and chunked scheduling — the mechanism behind the chunked-prefill knob in Model 8.)
- vLLM project documentation: https://docs.vllm.ai (Reference for production LLM serving with continuous batching, prefix caching, and the tuning knobs in Model 8.)
- "KV Cache and PagedAttention explained" (video): https://www.youtube.com/watch?v=o0gkdZBtwEg (A short, accessible walkthrough of the two mechanisms and the four tuning knobs covered in Part IV.)
- This activity pairs with `liascript-localai.md` (running Ollama locally) and `liascript-cloudflare.md` (hosting inference behind a gateway facade).

> **Citation**: AI Engineering from Scratch, Phase 17. Pairs with `liascript-localai.md` and `liascript-cloudflare.md`.
