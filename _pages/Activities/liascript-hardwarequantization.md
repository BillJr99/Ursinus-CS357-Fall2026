<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-hardwarequantization.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Hardware Behind AI: GPUs, Quantization, and Running Models at the Edge

CS357 - Foundations of Artificial Intelligence / Agentic AI | Ursinus College

---

## POGIL Roles

This activity uses the **POGIL** (Process Oriented Guided Inquiry Learning) structure.  Before beginning, assign one role to each group member:

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task, ensures everyone contributes, watches the clock |
| **Presenter** | Speaks for the group during class discussion, summarizes findings |
| **Recorder** | Documents the group's answers and reasoning in writing |
| **Reflector** | Monitors group process, notes what is working and what is not, leads the Reflection section |

> Rotate roles across activities so everyone practices each one.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **VRAM (Video RAM)** | The dedicated memory on a GPU that must hold the entire model during inference; if the model does not fit, it cannot run at full speed | A 70B parameter model at FP16 requires 140 GB of VRAM; a single RTX 4090 has only 24 GB |
| **Memory Bandwidth** | How fast data can be moved from VRAM into the GPU's compute cores; often the actual bottleneck during token generation, not raw compute speed | An H100 has ~3.35 TB/s bandwidth; an RTX 4090 has ~1 TB/s |
| **Quantization** | Reducing the number of bits used to store each model weight, shrinking the model in exchange for a small accuracy penalty | Quantizing from FP16 (2 bytes/weight) to Q4 (0.5 bytes/weight) cuts a 70B model from 140 GB to ~35 GB |
| **Perplexity** | A measure of how "surprised" a language model is when it reads a test document; lower means better; used to quantify quality loss from quantization | A Q4_K_M model has roughly 1.5% higher perplexity than the FP16 baseline for a 7B model |
| **Unified Memory** | An architecture (used by Apple Silicon) where the CPU, GPU, and Neural Engine all share the same physical RAM pool, so there is no separate VRAM limit | An M3 Ultra with 192 GB of RAM can load a 70B model at Q4 that would be impossible on any single NVIDIA consumer GPU |
| **Edge Inference** | Running an AI model locally on a device (laptop, workstation, embedded system) rather than sending queries to a remote cloud server | A rural clinic running a clinical documentation assistant on a local Mac Mini because there is no reliable internet connection |

---

## Model 1: Why Hardware Matters for AI Agents

Every transformer forward pass is essentially one massive matrix multiplication after another.  The hardware underneath determines not just how fast that runs, but whether it runs at all.  Quantization is like compressing a photo from RAW to JPEG: you lose a little quality, but the file is 8-16× smaller and loads instantly in a browser where the RAW file would time out.  Understanding these hardware constraints is not optional trivia: it is what lets you decide whether your agent can run offline on a Raspberry Pi, on a laptop at a clinic without internet, or only on a rented GPU in a data center.

The following section explains why GPUs dominate AI inference and what the actual bottleneck is during token generation; the answer is more subtle than "GPUs are faster."

### GPU vs. CPU for Matrix Multiplication

Neural network inference is dominated by one operation: **matrix multiplication**.  A transformer forward pass consists almost entirely of multiplying large matrices of weights by vectors of activations, repeatedly, across dozens or hundreds of layers.

**Why GPUs win at this:**

- A modern CPU has 8-32 cores optimized for sequential, branching tasks such as database queries or operating system scheduling
- A modern GPU has thousands of simpler cores optimized for massively parallel arithmetic, exactly what matrix multiplication requires
- For a matrix multiply of dimension N×N, the GPU can compute many products simultaneously, while the CPU must handle far fewer in parallel

However, **raw FLOPS (floating-point operations per second) is often not the bottleneck**.  The real constraint during token generation is **memory bandwidth**, the rate at which model weights can be streamed from VRAM into the compute cores.  A GPU may be rated at 312 TFLOPS but can only feed data at 2 TB/s, creating a bandwidth wall.  Most LLM inference runs at only 5-15% of peak FLOPS utilization for exactly this reason.

VRAM is a hard limit.  The entire model must fit in GPU VRAM (or be offloaded across multiple devices, at a significant latency penalty).  A model with P parameters stored at FP16 (2 bytes per parameter) requires exactly 2×P bytes of VRAM:

- 7B parameters × 2 bytes = **14 GB VRAM** (fits on an RTX 4090's 24 GB with room for the KV cache)
- 13B parameters × 2 bytes = **26 GB VRAM** (exceeds a single RTX 4090; requires an A100 or Apple Silicon with enough unified memory)
- 70B parameters × 2 bytes = **140 GB VRAM** (requires multiple A100s, an H100 with NVLink, or quantization to fit on consumer hardware)

Plus overhead for the KV cache (key-value cache for attention), activations, and runtime buffers, the actual requirement is typically 10-20% higher than the weight-only calculation.  That KV-cache overhead is not a fixed 10-20%; it grows with every concurrent request and every token of context, and it is where most serving inefficiency hides.  For *how* the non-weight VRAM is actually managed (fragmentation, PagedAttention, and the tuning knobs that decide how many users a card can serve), see Part IV of the companion activity *Serving LLMs in Production* (`liascript-llmserving.md`).

### Hardware Landscape

Use the table below to determine which hardware tier can run which model sizes.  The "Models That Fit at FP16" column assumes no quantization; with Q4 quantization, each model fits on hardware with roughly one-quarter the VRAM listed.

| Hardware | VRAM | Peak FLOPS (FP16) | Approximate Cost | Models That Fit at FP16 |
|----------|------|-------------------|------------------|-------------------------|
| Consumer GPU (RTX 4090) | 24 GB | ~82 TFLOPS | ~$1,600 retail | 7B (tight with KV cache), 13B (does not fit) |
| Workstation GPU (A100 80 GB SXM) | 80 GB | ~312 TFLOPS | ~$10,000-$15,000 | Up to ~40B parameters (tight); 70B requires multi-GPU |
| Cloud (H100 SXM) | 80 GB | ~989 TFLOPS (FP8 mode) | ~$2-4/hour cloud rental | Up to ~40B single GPU; 70B+ via NVLink multi-GPU |
| Apple Silicon (M3 Ultra) | 192 GB unified memory | ~17 TFLOPS GPU core (Neural Engine: ~60 TOPS) | ~$5,000-$10,000 | 70B+ at FP16; entire system memory is available to the GPU |
| TPU v4 (Google Cloud) | 32 GB per chip in multi-chip pods | ~275 TFLOPS (bfloat16) | Variable pod pricing | Large models via multi-chip pods; primarily for training |

**Unified memory (Apple Silicon):** Apple's M-series chips use a shared memory architecture where the CPU, GPU, and Neural Engine all access the same physical DRAM pool.  There is no separate VRAM limit; the entire system memory (up to 192 GB on an M3 Ultra) is available to the GPU. This fundamentally changes what is runnable on consumer hardware: a 70B model that is impossible on any single NVIDIA consumer GPU can run on a Mac Studio.

### Critical Thinking Questions

**Question 1.**  VRAM capacity and memory bandwidth are both constraints on LLM inference, but they matter at different phases.  Explain why **memory bandwidth** is typically the binding constraint during inference (token-by-token generation), while **VRAM capacity** is the binding constraint during model loading.  Under what conditions would the raw FLOPS ceiling become the binding constraint instead?

[[___ Your answer here ___]]

> *Hint:* During generation, the model weights must be streamed through the compute units for every single token; this is a bandwidth-bound operation because the GPU keeps re-reading all those weights.  But before generation can even begin, the weights must fit in VRAM at all; this is a capacity constraint.  FLOPS become the dominant limit when you batch many users' queries together (large batch size), so the GPU is doing more work per memory read.  What batch size makes a GPU "compute-bound" rather than "memory-bound," and why does a single-user local deployment almost never reach that threshold?

---

**Question 2.**  A 7B parameter model at FP16 requires approximately 14 GB of VRAM for weights alone.  A laptop GPU has 16 GB of VRAM. Using the formulas below, show your calculations:

- FP16 weight size: parameters × 2 bytes
- Q4 weight size: parameters × 0.5 bytes
- KV cache for a 7B model at 4K context: approximately 1.5 GB additional

(a) Can the 7B model fit in 16 GB at FP16 with a 4K-context KV cache?

(b) If you quantize to Q4 (0.5 bytes per parameter), what is the total VRAM footprint including the KV cache?

(c) How does quantization change what you can run on this laptop GPU?

[[___ Your answer here ___]]

> *Hint:* At FP16: 7B × 2 bytes = 14 GB weights + 1.5 GB KV cache = 15.5 GB total.  With 16 GB VRAM, this is technically possible but dangerously tight; any additional overhead from the runtime or a longer context will cause out-of-memory errors.  At Q4: 7B × 0.5 bytes = 3.5 GB weights + 1.5 GB KV cache = 5 GB total.  This fits comfortably with room to spare for longer contexts or runtime buffers.

---

**Question 3.**  A developer argues: "Apple Silicon is not a serious AI workstation because it cannot match an H100 in FLOPS." A second developer argues: "For local inference of models up to 70B parameters, Apple Silicon is better than any single consumer NVIDIA GPU." Evaluate both claims carefully.  Which specific models and use cases would run better on an M3 Ultra (192 GB unified memory) than on an RTX 4090 (24 GB VRAM), and which would run better on the RTX 4090?

[[___ Your answer here ___]]

> *Hint:* The M3 Ultra wins decisively for any model between about 12 GB and 192 GB in size, models that simply do not fit on the RTX 4090 at all.  The RTX 4090 wins for smaller models (7B at Q4 or FP16) that fit comfortably in 24 GB, because its CUDA compute and bandwidth are faster than Apple's GPU cores for that workload.  The H100 wins for everything involving large batch sizes, training, or multi-user throughput at scale.  When does each choice make sense in practice?

---

## Model 2: Quantization - Getting More from Less

### Number Format Basics

The table below lists every precision format you will encounter in this course.  The key column is "Bytes per Weight"; multiply it by the number of model parameters to get the minimum VRAM required to load the model.

Neural networks store weights as floating-point or integer numbers.  The precision of the format determines both the memory footprint and the computational cost:

| Format | Bits per Weight | Bytes per Weight | In Our Course |
|--------|----------------|------------------|---------------|
| FP32 | 32 | 4 bytes | Standard training precision; almost never used for inference because it costs twice as much memory as FP16 with no benefit at inference time |
| FP16 | 16 | 2 bytes | Common inference precision; what "full precision" means in the context of this course's Ollama labs |
| BF16 | 16 | 2 bytes | Same memory footprint as FP16 but with a different exponent range that reduces overflow during training; preferred for fine-tuning |
| INT8 | 8 | 1 byte | Integer quantization; well-supported on modern NVIDIA GPUs; about half the memory of FP16 with minimal quality loss |
| INT4 / Q4 | 4 | 0.5 bytes | The "practical sweet spot" for local inference; the format used by most Ollama and llama.cpp models you've run in labs |
| Q3 | 3 | 0.375 bytes | Noticeable quality degradation on complex reasoning and multi-step tasks |
| Q2 | 2 | 0.25 bytes | Severe degradation; only useful in extreme memory-constrained situations where any output is better than none |

**The core math you need to know:**

- 70B model at FP16: 70,000,000,000 × 2 bytes = **140 GB**, requires multiple data center GPUs
- 70B model at Q4: 70,000,000,000 × 0.5 bytes = **35 GB**, fits on an M3 Ultra (192 GB unified memory)
- 70B model at Q3: 70,000,000,000 × 0.375 bytes = **26 GB**, fits on a Mac Studio M3 Ultra with 32 GB RAM

### GGUF Format and Practical Quantization

The **GGUF format** (used by llama.cpp and Ollama, the tools you use in this course) is the dominant format for local inference.  It supports:

- **Mixed precision**: different layers can use different quantization levels; important layers such as attention can remain at higher precision while less critical layers are quantized more aggressively
- **GPU offloading**: model layers can be split between CPU RAM and VRAM, enabling models larger than VRAM alone could hold (at the cost of slower token generation)
- **Named quantization variants**: Q4_K_M, Q5_K_M, etc., where K means key-layers (attention) are kept at higher precision, and M/S indicate medium/small variant within that tier

**Perplexity** measures how "surprised" a language model is when reading a held-out text corpus; lower perplexity means better predictions, closer to the original model quality.  It is the standard metric for quantization quality loss.

**VRAM Requirements and Quality for a 7B Model**

The table below shows the quality-versus-size tradeoff for a 7B model at each quantization level.  The "Perplexity Increase" column is the key: a 1.5% increase (Q4_K_M) is typically invisible in conversation; a 15% increase (Q2_K) is often noticeable.

| Format | Bits/Weight | Model Size (7B) | Perplexity Increase vs. FP16 | Notes |
|--------|------------|-----------------|------------------------------|-------|
| FP16 | 16 | ~14 GB | Baseline (0%) | Reference quality: what "full precision" means |
| BF16 | 16 | ~14 GB | ~0% | Equivalent to FP16 for inference purposes |
| Q8_0 | 8 | ~7 GB | ~0.1% increase | Nearly lossless; recommended if VRAM allows |
| Q6_K | 6 | ~5.5 GB | ~0.3% increase | Excellent quality with meaningful size reduction |
| Q5_K_M | 5 | ~4.8 GB | ~0.6% increase | Very good quality; a strong choice when 8 GB of VRAM is available |
| Q4_K_M | 4 | ~4.1 GB | ~1.5% increase | **The practical sweet spot**: good quality, fits in 6-8 GB VRAM, used in most course labs |
| Q3_K_M | 3 | ~3.3 GB | ~4-6% increase | Noticeable quality loss on complex multi-step reasoning and code generation |
| Q2_K | 2 | ~2.7 GB | ~15-30% increase | Significant degradation; only use when no better option exists |

### Quantization-Aware Training vs. Post-Training Quantization

- **Post-Training Quantization (PTQ)**: Apply quantization to an already-trained FP16 or FP32 model after training is complete.  Fast and cheap; this is exactly what GGUF/llama.cpp quantization does to the models you pull with Ollama.  Accuracy loss grows as you push to lower bit depths.

- **Quantization-Aware Training (QAT)**: Simulate quantization noise *during* training, so the model learns to compensate for the precision loss while still at full precision.  Produces significantly better accuracy at very low bit depths (INT4, INT2).  Requires access to training infrastructure and significant compute; used in techniques like QLoRA that allow fine-tuning quantized models.

> **Common Misconception:** Many students assume that quantization always makes models noticeably worse.  In practice, Q4_K_M gives roughly 1.5% higher perplexity than the FP16 baseline for a 7B model, a difference that is often imperceptible in conversation, coding assistance, and most practical tasks.  The sharp quality cliff only occurs at Q2 and below.  For most use cases in this course, Q4_K_M is the correct starting point: it cuts memory requirements by 4× compared to FP16 while preserving the vast majority of model quality.

### Critical Thinking Questions

**Question 4.**  You have a GPU with 8 GB of VRAM. You want to run a 13B parameter model.  Using the formula: VRAM required ≈ (parameters × bytes/weight) × 1.15 (to account for KV cache and runtime overhead at modest context lengths):

(a) What is the VRAM requirement at Q8 (1 byte/weight)?  Show your calculation.

(b) What is the VRAM requirement at Q4_K_M (0.5 bytes/weight)?  Show your calculation.

(c) What is the VRAM requirement at Q3_K_M (0.375 bytes/weight)?  Show your calculation.

(d) Which quantization level(s) fit in 8 GB? What quality trade-off are you accepting for each one that fits?

[[___ Your answer here ___]]

> *Hint:* Q8: 13B × 1 byte = 13 GB × 1.15 overhead = **14.95 GB**, does not fit in 8 GB. Q4_K_M: 13B × 0.5 bytes = 6.5 GB × 1.15 = **7.47 GB**, fits, with about 500 MB to spare for a modest context.  Q3_K_M: 13B × 0.375 bytes = 4.875 GB × 1.15 = **5.6 GB**, fits comfortably with room for a larger context.  Q4_K_M is the sweet spot: it fits in 8 GB and accepts only ~1.5% perplexity increase.  Q3_K_M fits more comfortably but costs 4-6% perplexity.

---

**Question 5.**  Q2 quantization reduces a 70B model's VRAM requirement from 140 GB (FP16) to approximately 17.5 GB, an 8× reduction.  However, it increases perplexity by roughly 15-30%. Identify two specific use cases where this trade-off is acceptable, and two where it is not.  For each case, identify what the task requires that either tolerates or cannot tolerate the perplexity increase.

[[___ Your answer here ___]]

> *Hint:* Acceptable: (1) A retrieval-augmented search interface where the model only needs to select which retrieved passage is most relevant; this is a classification-like task where the exact wording of the output matters less than the selection decision.  (2) An extremely resource-constrained embedded device where Q2 is the only way to run any LLM at all, and even a degraded model is more useful than no model.  Not acceptable: (1) Medical question-answering where a confidently stated but subtly wrong answer could lead to patient harm.  (2) Code generation where subtle logic errors are difficult for a non-expert user to detect and could introduce security vulnerabilities.

---

**Question 6.**  Perplexity is the standard benchmark for quantization quality, but it is a proxy metric: it measures how well the model predicts tokens in a reference corpus, not how well it performs on actual tasks.  Name two tasks where a model with higher perplexity might actually perform better than a lower-perplexity model on real benchmarks.  What does this suggest about using perplexity as the sole quality criterion for quantization decisions?

[[___ Your answer here ___]]

> *Hint:* A model fine-tuned to be more decisive and direct (such as an instruction-tuned assistant) may have higher perplexity on a general text corpus because it assigns high probability to one specific answer rather than spreading probability across many plausible completions, but it performs better on instruction-following tasks.  A coding model fine-tuned on Python code will have higher perplexity on a natural language benchmark but dramatically better performance on HumanEval.  What should you measure instead of, or in addition to, perplexity when making quantization decisions for a specific deployment?

---

### Multiple Choice Question

A research team wants to deploy a 70B parameter model for offline inference on a MacBook Pro with Apple Silicon and 32 GB of unified memory.  The full FP16 model requires approximately 140 GB. The team's best option is:

[[ ]] Run it at FP32 precision; the 32 GB unified memory is ample for a 32-bit 70B model since Apple Silicon shares all system memory with the GPU
[[ ]] It is impossible to run a 70B parameter model on consumer hardware; only data center GPUs with 80+ GB of dedicated VRAM can load models this size
[[x]] Quantize to Q4 (approximately 0.5 bytes/parameter, yielding ~35 GB) or Q3 (~26 GB), which fits within 32 GB unified memory with acceptable quality for most use cases
[[ ]] Run FP16 on the CPU only; on Apple Silicon, CPU inference bypasses the VRAM limitation because the CPU accesses system memory directly

> **Why this answer?**  At Q4, 70B × 0.5 bytes = 35 GB, slightly over the 32 GB limit, so Q3_K_M at approximately 26 GB is the better choice.  Apple Silicon's unified memory architecture means the GPU accesses all system memory, so the 32 GB applies to the combined model and KV cache budget.  FP32 would require 280 GB, nearly 9× the available memory.  CPU-only inference is technically possible but produces token generation rates often below 1 token per second, making it impractical for interactive use.

---

## Model 3: Edge Deployment and Agent Implications

### Edge vs. Cloud Inference

The table below compares edge and cloud inference across six dimensions.  As you read it, identify which dimension matters most for the rural clinic scenario in Question 7; not every row is equally important for every deployment.

| Dimension | Edge (Local Device) | Cloud (Remote Server) |
|-----------|---------------------|-----------------------|
| Latency | Sub-millisecond network overhead; first token appears almost immediately | 50-500 ms network round-trip minimum; longer under high server load |
| Privacy | All data stays on the local device; no transmission to third parties | User data is transmitted to the cloud provider's servers for each query |
| Connectivity | Works completely offline with no internet connection required | Requires a reliable internet connection for every query |
| Cost at scale | Hardware cost is amortized over time; ongoing cost is electricity only | Per-query pricing that can add up significantly at volume |
| Model size | Constrained by local hardware; VRAM or unified memory sets a hard ceiling | Effectively unlimited; providers run multi-GPU clusters for very large models |
| Updates | Requires manual model download and update by the operator | Model upgrades happen transparently on the provider's side |

**Use cases where edge deployment is the correct architectural choice:**

- **Medical devices** in operating rooms or ambulances where network reliability cannot be guaranteed and patient data cannot leave the facility under HIPAA constraints
- **Field robotics** operating in connectivity-denied environments such as deep mining operations, ocean floor surveys, or disaster response zones
- **Offline enterprise** in manufacturing facilities with air-gapped industrial networks where connecting to the internet would create unacceptable security exposure
- **Air-gapped classified environments** where regulatory requirements explicitly prohibit external network connections, the exact scenario the containerization lab in this course targeted

### Hardware-Aware Agent Design

Deploying an agent to edge hardware requires making explicit hardware-aware design decisions before writing a single line of agent code:

1.  **Model selection**: Choose the largest model that fits within VRAM or unified memory at an acceptable quantization level, for the target hardware.  Do not assume you can run the same model that works in cloud development.
2.  **Context management**: Long contexts consume large KV caches.  If the hardware cannot fit a 32K context at the target model size and quantization level, the agent must implement context compression, conversation summarization, or a sliding window approach.
3.  **Streaming**: For user-facing applications, streaming tokens as they are generated dramatically reduces *perceived* latency even when raw throughput is low; the user sees the first words almost immediately rather than waiting for the full response.
4.  **Batching**: For non-interactive background workloads such as document processing, batching multiple queries improves GPU utilization and throughput.

### The Local Inference Stack

Three tools dominate local LLM inference, and you have used at least one of them in this course:

- **llama.cpp**: A C++ inference engine for GGUF models.  Handles mixed-precision loading, CPU+GPU layer offloading, and Metal (Apple), CUDA, and ROCm hardware backends.  The foundation underlying most local inference tools.
- **Ollama**: A wrapper around llama.cpp providing a simple REST API, model management, and model pulls similar to Docker image pulls.  Used in this course's agent lab; when you run `ollama run llama3`, you are using this stack.
- **LM Studio**: A GUI frontend for llama.cpp providing a chat interface and an OpenAI-compatible API endpoint.  Useful for non-technical users and rapid experimentation without command-line interaction.

All three tools load GGUF models, handle GPU offloading of as many layers as fit in VRAM (leaving the rest on CPU RAM), and manage the context buffer automatically.

### Critical Thinking Questions

**Question 7.**  You are designing the hardware and software stack for a local AI agent deployment in a rural primary care clinic with no reliable internet connection.  The clinic sees 40 patients per day and needs the agent to assist with clinical documentation: SOAP note drafting, ICD-10 code lookup, and medication interaction checking.  Design the hardware selection process: what model size do you target, what specific hardware do you specify, what quantization level do you use, and how do you justify the cost to the clinic administrator?

[[___ Your answer here ___]]

> *Hint:* 40 patients per day is a sequential, latency-sensitive workload; the bottleneck is response quality and speed for one user at a time, not throughput for many simultaneous users.  For clinical documentation, you likely need a model with strong instruction-following and medical domain knowledge, probably 7B-13B at minimum, ideally larger.  Consider a Mac Mini M2 Pro (32 GB unified memory, ~$1,300) running a 13B Q4_K_M model (~7.5 GB footprint).  How does HIPAA interact with your hardware choice: can data ever leave the device?  Is a Mac Mini a defensible clinical edge device, or does it need to be a specialized medical-grade computer?

---

**Question 8.**  Your agent application requires a 32K token context window to process long clinical documents, but your GPU has only 8 GB of VRAM. Running a model large enough for quality output at 32K context would require 20+ GB. List three distinct technical strategies for operating within this constraint, and identify the specific trade-off each strategy imposes on the agent's behavior and output quality.

[[___ Your answer here ___]]

> *Hint:* (1) **Context compression and summarization**: periodically summarize earlier conversation turns and replace them with a compact summary, then truncate the full history.  Trade-off: the agent loses verbatim access to specific details from earlier in the conversation.  (2) **RAG (Retrieval-Augmented Generation) instead of long context**: chunk the document into passages, embed them, and retrieve the most relevant passages for each query.  Trade-off: retrieval quality determines what the model "sees"; relevant passages may be missed.  (3) **CPU offloading**: load the layers that don't fit in VRAM into CPU RAM, processing them on the CPU. Trade-off: significant latency increase because CPU-to-GPU data transfer is slow.  (4) Use a smaller model that fits within 8 GB at 32K context.  Trade-off: lower reasoning capability across all tasks.

---

**Question 9.**  Running a Q4 70B model on a 150W Apple Silicon system for 8 hours per day consumes about 1.2 kWh daily.  A cloud API call offloads the energy cost, but to a large data center that may or may not run on renewable energy.  Compare the environmental impact of these two deployment strategies.  What information would you need to make this comparison accurately, and what does your analysis suggest for sustainable AI agent deployment?

[[___ Your answer here ___]]

> *Hint:* To compare fairly, you need: the local power grid's carbon intensity (g CO₂ per kWh) for your region, the cloud provider's reported Power Usage Effectiveness (PUE, a measure of how efficiently the data center uses energy) and their renewable energy percentage, the number of tokens generated per hour for each option, and whether the local device is otherwise idle (in which case the inference is a marginal cost on top of base power draw).  There is no universal answer: running a model on solar-powered local hardware in a sunny region may have lower carbon footprint than a coal-powered data center, or vice versa.  What does this imply for where AI inference workloads should physically be located?

---

## Exercises

**Exercise 1.**

*What to do:* Calculate the VRAM requirements for six configurations using the formula: VRAM ≈ (parameters × bytes/weight) × 1.15.  Present your results in a completed table.

Models: Llama 3 8B and Llama 3 70B. Formats for each: FP16 (2 bytes/weight), INT8 (1 byte/weight), Q4_K_M (0.5 bytes/weight).

| Model | Format | Bytes/Weight | Base VRAM | ×1.15 Overhead | Total VRAM | Fits in RTX 4090 (24 GB)? |
|-------|--------|-------------|-----------|----------------|------------|--------------------------|
| Llama 3 8B | FP16 | 2.0 | ? | ? | ? | ? |
| Llama 3 8B | INT8 | 1.0 | ? | ? | ? | ? |
| Llama 3 8B | Q4_K_M | 0.5 | ? | ? | ? | ? |
| Llama 3 70B | FP16 | 2.0 | ? | ? | ? | ? |
| Llama 3 70B | INT8 | 1.0 | ? | ? | ? | ? |
| Llama 3 70B | Q4_K_M | 0.5 | ? | ? | ? | ? |

*Starter hint:* Start with Llama 3 8B at FP16: 8B × 2 bytes = 16 GB, then × 1.15 = 18.4 GB. Does that fit on an RTX 4090 with 24 GB? Yes, with about 5.6 GB to spare for KV cache and context.  Now work through the remaining five rows the same way.

*You've succeeded when:* Your table has all six rows completed with shown calculations, the "Fits in RTX 4090?" column is correctly answered for all six, and you have written a two-sentence conclusion identifying which configurations are viable for single-GPU consumer deployment.

---

**Exercise 2.**

*What to do:* If you have access to a system with Ollama installed, run the same moderately complex prompt through at least two quantization levels of the same base model.  A good test prompt is a multi-step math word problem, a code debugging task, or a question that requires synthesizing information from multiple steps.  Compare the outputs on quality, correctness, and speed.

*Starter hint:* Try: `ollama run llama3.2:3b` and `ollama run llama3.2:3b-instruct-q4_K_M` (or equivalent available models on your system).  Use the prompt: "A store sells apples for $1.20 each and oranges for $0.85 each.  If I buy 7 apples and 5 oranges and pay with a $20 bill, how much change do I receive?  Show your work step by step."  Record the tokens-per-second figure that Ollama prints at the end of each response.

If you do not have Ollama access, find two published model cards that report both quantization levels and evaluation results (such as MMLU or HumanEval scores) for the same base model, and compare the reported results.

*You've succeeded when:* You have recorded the exact prompt used, both full outputs, a written comparison of output quality and correctness, the tokens-per-second for each, and a one-paragraph recommendation: for your specific test task, which quantization level would you use in production, and why?

---

**Exercise 3.**

*What to do:* Research one real-world edge AI deployment from one of these domains: FDA-cleared medical device inference (diagnostic imaging AI), autonomous agricultural machinery with offline AI, or industrial robotics in an air-gapped manufacturing facility.  Write a 400-word case study.

*Starter hint:* Search for "FDA 510k clearance AI inference embedded" or "autonomous tractor AI edge compute" or "manufacturing AI air-gapped."  Look for technical blog posts, academic papers, or press releases that discuss the hardware and constraints.  You want to find a case where the engineers explicitly discussed *why* cloud inference was unsuitable.

*You've succeeded when:* Your 400-word case study covers all four points: (a) what specific hardware the system runs on and why that hardware was chosen; (b) what model capability was required and how it was achieved within the hardware constraints; (c) why cloud inference was specifically unsuitable for this application; and (d) what the deployment revealed about real-world edge AI constraints that surprised the engineering team.  Include at least two cited sources.

---

## Reflection Prompt

**Personal:** Think about the AI tools you use day-to-day: voice assistants on your phone, code completion in your editor, chatbots in your browser.  Do you know whether those models run locally on your device or remotely in a data center?  Does it matter to you, and would it change how you use them if you knew?

**Technical:** One of the central tensions in AI deployment is between **centralization and decentralization**.  Cloud AI concentrates compute, data, and capability in the hands of a small number of large companies.  Edge AI distributes that capability outward to individuals and organizations.  Does widespread local model inference democratize AI, or does it just shift the dependency, from cloud providers to GPU manufacturers and open-weight model developers?

> *Hint:* Consider who manufactures the GPUs running Ollama, who trained the open-weight models you download, and whether the open-weight license gives you the right to modify the model weights or just to use them.

**Societal:** A rural clinic with a local model is less dependent on OpenAI, but is now dependent on NVIDIA for GPUs, Qualcomm or Apple for edge chips, and Meta or another organization for open model weights.  Is that a meaningful improvement?  And at the individual level: if a CS graduate can deploy a capable 70B model on a $2,000 workstation, what does that mean for who can build AI-powered products and who can afford to?

Write at least 200 words addressing at least two of the three levels above.

[[___ Your reflection here ___]]

---

-> Coming Up Next: In the next activity, we examine how we know whether an AI system is actually good at what it claims to do: the science and politics of benchmarking.

## Further Reading

- llama.cpp GitHub Repository.  (2023-present).  *High-performance LLM inference in C/C++.* https://github.com/ggerganov/llama.cpp

- Dettmers, T. et al. (2023).  *QLoRA: Efficient Finetuning of Quantized LLMs.*  NeurIPS 2023. https://arxiv.org/abs/2305.14314

- Gholami, A. et al. (2021).  *A Survey of Quantization Methods for Efficient Neural Network Inference.*  In Low-Power Computer Vision. https://arxiv.org/abs/2103.13630

- Frantar, E. et al. (2022).  *GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers.* arXiv:2210.17323. https://arxiv.org/abs/2210.17323

- Ollama Documentation.  (2024). https://ollama.com/docs

- Apple.  (2023).  *Apple Silicon Machine Learning Research: Unified Memory Architecture.* https://developer.apple.com/metal/pytorch/
