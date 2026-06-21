<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-hardwarequantization.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Hardware Behind AI: GPUs, Quantization, and Running Models at the Edge

CS357 - Foundations of Artificial Intelligence / Agentic AI | Ursinus College

---

## POGIL Roles

This activity uses the **POGIL** (Process Oriented Guided Inquiry Learning) structure. Before beginning, assign one role to each group member:

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task, ensures everyone contributes, watches the clock |
| **Presenter** | Speaks for the group during class discussion, summarizes findings |
| **Recorder** | Documents the group's answers and reasoning in writing |
| **Reflector** | Monitors group process, notes what is working and what is not, leads the Reflection section |

> Rotate roles across activities so everyone practices each one.

---

## Model 1: Why Hardware Matters for AI Agents

### GPU vs. CPU for Matrix Multiplication

Neural network inference is dominated by one operation: **matrix multiplication**. A transformer forward pass consists almost entirely of multiplying large matrices of weights by vectors of activations, repeatedly, across dozens or hundreds of layers.

**Why GPUs win at this:**

- A modern CPU has 8–32 cores optimized for sequential, branching tasks
- A modern GPU has thousands of simpler cores optimized for massively parallel arithmetic
- For a matrix multiply of dimension N×N, the GPU can compute all N² products in parallel, while the CPU must serialize most of them

However, **raw FLOPS is often not the bottleneck**. The real constraint is **memory bandwidth** — the rate at which weights can be streamed from VRAM into compute units. A GPU may be capable of 312 TFLOPS but can only feed data at 2 TB/s, creating a bandwidth wall. Most LLM inference runs at 5–15% of peak FLOPS utilization for this reason.

**VRAM is a hard limit.** The entire model must fit in GPU VRAM (or be offloaded across devices, at a significant latency penalty). A model with P parameters stored at FP16 (2 bytes/parameter) requires 2P bytes of VRAM:

- 7B parameters × 2 bytes = **14 GB VRAM**
- 13B parameters × 2 bytes = **26 GB VRAM**
- 70B parameters × 2 bytes = **140 GB VRAM**

Plus overhead for the KV cache (key-value cache for attention), activations, and runtime buffers, the actual requirement is typically 10–20% higher.

### Hardware Landscape

| Hardware | VRAM | Peak FLOPS (FP16) | Cost Estimate | Models That Fit (FP16) |
|----------|------|-------------------|---------------|------------------------|
| Consumer GPU (RTX 4090) | 24 GB | ~82 TFLOPS | ~$1,600 | 7B (tight), 13B (no) |
| Workstation GPU (A100 80GB SXM) | 80 GB | ~312 TFLOPS | ~$10,000–$15,000 | Up to ~40B (tight) |
| Cloud (H100 SXM) | 80 GB | ~989 TFLOPS FP8 | ~$2–4/hr cloud rental | Up to ~40B; multi-GPU for 70B+ |
| Apple Silicon (M3 Ultra) | 192 GB unified | ~17 TFLOPS GPU (Neural Engine: ~60 TOPS) | ~$5,000–$10,000 | Up to 70B+ at FP16 |
| TPU v4 (Google Cloud) | 32 GB per chip (multi-chip pods) | ~275 TFLOPS (bfloat16) | Variable pod pricing | Large models via pods |

**Unified memory (Apple Silicon):** Apple's M-series chips use a shared memory architecture where the CPU, GPU, and Neural Engine all access the same physical DRAM. There is no separate VRAM limit — the entire system memory (up to 192 GB on M3 Ultra) is available to the GPU. This fundamentally changes what is runnable on consumer hardware.

### Critical Thinking Questions

**Question 1.** VRAM capacity and memory bandwidth are both constraints on LLM inference, but they matter at different phases. Explain why **memory bandwidth** is typically the binding constraint during inference (token generation), while **VRAM capacity** is the binding constraint during model loading. Under what conditions would the FLOPS ceiling become the binding constraint?

[[___ Your answer here ___]]

> Hint: During generation, the model weights must be streamed through the compute units for every token — this is bandwidth-bound. But first the weights must fit in VRAM at all — this is a capacity constraint. FLOPS dominate when the batch size is large (parallel inference for many users). What batch size makes a GPU "compute-bound" vs. "memory-bound"?

---

**Question 2.** A 7B parameter model at FP16 requires approximately 14 GB of VRAM (model weights alone, before KV cache). A laptop GPU has 16 GB of VRAM.

(a) Can the 7B model fit at FP16 with a reasonable KV cache for a 4K context window?

(b) If you quantize to Q4 (approximately 0.5 bytes/parameter), what is the model's footprint?

(c) How does this change the answer?

Show your calculations.

[[___ Your answer here ___]]

> KV cache for a 7B model at 4K context is roughly 1–2 GB additional. At FP16: 14 GB weights + ~1.5 GB KV cache ≈ 15.5 GB — tight but possible. At Q4: 7B × 0.5 bytes = 3.5 GB weights + same KV cache ≈ 5 GB total — comfortable.

---

**Question 3.** A developer argues: "Apple Silicon is not a serious AI workstation because it cannot match an H100 in FLOPS." A second developer argues: "For local inference of models up to 70B, Apple Silicon is better than any single consumer NVIDIA GPU." Evaluate both claims. Which models would run better on an M3 Ultra (192 GB unified) than on an RTX 4090 (24 GB VRAM), and vice versa?

[[___ Your answer here ___]]

> The M3 Ultra wins on: models between 24GB and 192GB in size (which don't fit in an RTX 4090 at all). The RTX 4090 wins on: raw FLOPS for smaller models that fit in 24 GB, and any task requiring CUDA ecosystem libraries. The H100 wins on: batch inference, training, throughput at scale. When does each choice make sense?

---

## Model 2: Quantization: Getting More from Less

### Number Format Basics

Neural networks store weights as floating-point or integer numbers. The precision of the format determines both the memory footprint and the computational cost:

| Format | Bits per Weight | Bytes per Weight | Notes |
|--------|----------------|------------------|-------|
| FP32 | 32 | 4 | Standard training precision; rarely used for inference |
| FP16 | 16 | 2 | Common inference precision; good accuracy |
| BF16 | 16 | 2 | Same size as FP16; different exponent range; preferred for training stability |
| INT8 | 8 | 1 | Integer quantization; well-supported on modern GPUs |
| INT4 / Q4 | 4 | 0.5 | Half the size of INT8; meaningful accuracy penalty begins |
| Q3 | 3 | 0.375 | Significant accuracy degradation for most tasks |
| Q2 | 2 | 0.25 | Severe degradation; typically unusable for general tasks |

### GGUF Format and Practical Quantization

The **GGUF format** (used by llama.cpp) is the dominant format for local inference. It supports:

- **Mixed precision**: different layers can use different quantization levels (important layers like attention can remain at higher precision)
- **GPU offloading**: layers can be split across CPU RAM and VRAM, enabling models larger than VRAM alone
- **Named quantization variants**: Q4_K_M, Q5_K_M, etc., where K indicates key-layer higher precision and M/S indicate medium/small variant

**Perplexity** measures how "surprised" a language model is by a held-out text corpus — lower is better. It is the standard metric for quantization quality loss.

**VRAM Requirements and Quality for a 7B Model**

| Format | Bits/Weight | Model Size (7B) | Perplexity Increase vs. FP16 | Notes |
|--------|------------|-----------------|------------------------------|-------|
| FP16 | 16 | ~14 GB | Baseline (0%) | Reference quality |
| BF16 | 16 | ~14 GB | ~0% | Equivalent to FP16 for inference |
| Q8_0 | 8 | ~7 GB | ~0.1% | Nearly lossless; recommended if VRAM allows |
| Q6_K | 6 | ~5.5 GB | ~0.3% | Excellent quality |
| Q5_K_M | 5 | ~4.8 GB | ~0.6% | Very good quality |
| Q4_K_M | 4 | ~4.1 GB | ~1.5% | **Practical sweet spot**: good quality, fits in small VRAM |
| Q3_K_M | 3 | ~3.3 GB | ~4–6% | Noticeable quality loss on complex reasoning |
| Q2_K | 2 | ~2.7 GB | ~15–30% | Significant degradation; specialized use only |

### Quantization-Aware Training vs. Post-Training Quantization

- **Post-Training Quantization (PTQ)**: Apply quantization to a trained FP16/FP32 model after training is complete. Fast and cheap, but accuracy loss grows at aggressive bit depths. This is what GGUF quantization does.

- **Quantization-Aware Training (QAT)**: Simulate quantization noise during training, allowing the model to adapt. Produces significantly better accuracy at low bit depths (INT4, INT2). Requires access to training infrastructure and significant compute. Used by QLoRA and similar methods.

### Critical Thinking Questions

**Question 4.** You have a GPU with 8 GB of VRAM. You want to run a 13B parameter model. Using the formula (model size ≈ parameters × bytes/weight + KV cache overhead ≈ 15% extra):

(a) What is the VRAM requirement at Q8?
(b) At Q4_K_M?
(c) At Q3_K_M?
(d) Which quantization level(s) fit in 8 GB, and what quality trade-off are you accepting?

Show your calculations.

[[___ Your answer here ___]]

> Formulas: Q8: 13B × 1 byte = 13 GB + 15% ≈ 15 GB. Q4: 13B × 0.5 byte = 6.5 GB + 15% ≈ 7.5 GB. Q3: 13B × 0.375 = 4.9 GB + 15% ≈ 5.6 GB. Q4 just fits with minimal KV cache; Q3 fits more comfortably but at greater quality cost.

---

**Question 5.** Suppose Q2 quantization reduces a model's size by approximately 16x compared to FP32, but increases perplexity by 30%. Identify two specific use cases where this trade-off is acceptable, and two where it is not. Justify each case by identifying what the task requires that perplexity increase either does or does not damage.

[[___ Your answer here ___]]

> Acceptable: (1) Simple keyword extraction where the task is pattern-matching, not generation quality. (2) On an extremely resource-constrained device where Q2 is the only option. Not acceptable: (1) Medical question answering where confident wrong answers cause harm. (2) Code generation where subtle logical errors in output are hard to catch.

---

**Question 6.** Perplexity is the standard benchmark for quantization quality, but it is a proxy metric — it measures how well the model predicts tokens in a reference corpus, not how well it performs on real tasks. Name two tasks where a model with higher perplexity might actually perform better than a lower-perplexity model. What does this suggest about using perplexity as the sole quality criterion for quantization decisions?

[[___ Your answer here ___]]

> Consider: A model fine-tuned to be more decisive might have higher perplexity (less probability spread over multiple correct tokens) but better task performance. A coding model fine-tuned on code might have higher perplexity on natural language benchmarks but better performance on programming tasks. What should you measure instead of, or in addition to, perplexity?

---

### Multiple Choice Question

A research team wants to deploy a 70B parameter model for offline inference on a MacBook Pro with Apple Silicon and 32 GB of unified memory. The full FP16 model requires approximately 140 GB. The team's best option is:

[[ ]] Run it at FP32 precision — the model clearly fits comfortably within 32 GB
[[ ]] It is impossible to run a 70B parameter model on any consumer hardware
[[x]] Quantize to Q4 (approximately 0.5 bytes/parameter, yielding ~35 GB) or Q3 (~26 GB), which fits within 32 GB unified memory with acceptable quality for most use cases
[[ ]] Run FP16 on the CPU, disabling GPU acceleration to avoid VRAM limitations

> **Why this answer?** At Q4, 70B × 0.5 bytes = 35 GB — slightly over 32 GB. Q3_K_M brings it to approximately 26 GB, fitting comfortably. Apple Silicon's unified memory architecture means the GPU can access all system memory, so the 32 GB limit applies to the whole model including KV cache. FP32 would require 280 GB. CPU-only inference is technically possible but would produce unacceptably slow token generation (often <1 token/second).

---

## Model 3: Edge Deployment and Agent Implications

### Edge vs. Cloud Inference

| Dimension | Edge (Local) | Cloud |
|-----------|-------------|-------|
| Latency | Sub-millisecond to model; no network round-trip | 50–500ms network overhead minimum |
| Privacy | Data never leaves device | Data transmitted to third-party servers |
| Connectivity | Works offline | Requires internet |
| Cost at scale | Hardware amortized; electricity only marginal cost | Per-query cost; can be high at volume |
| Model size | Constrained by local hardware | Effectively unlimited (multi-GPU clusters) |
| Updates | Manual model update required | Transparent upgrades by provider |

**Use cases where edge is the correct choice:**

- **Medical devices** in operating rooms or ambulances where network reliability cannot be guaranteed and patient data cannot leave the facility
- **Field robotics** operating in GPS-denied, connectivity-denied environments (deep mining, ocean floor, disaster zones)
- **Offline enterprise** in manufacturing facilities with air-gapped networks for industrial security
- **Air-gapped classified environments** where regulatory requirements prohibit external network connections — exactly the kind of environment the containerization lab in this course targeted

### Hardware-Aware Agent Design

Deploying an agent to edge hardware requires explicit hardware-aware design decisions:

1. **Model selection**: Choose the largest model that fits within VRAM/memory at an acceptable quantization level, given the target hardware
2. **Context management**: Long contexts consume large KV caches. If the hardware cannot fit a 32K context at the target model size, the agent must implement context compression, summarization, or sliding window techniques
3. **Streaming**: For user-facing applications, streaming tokens as they are generated dramatically reduces perceived latency even when throughput is low
4. **Batching**: For non-interactive workloads, batching multiple queries together improves hardware utilization

### The Local Inference Stack

Three tools dominate local LLM inference:

- **llama.cpp**: C++ inference engine for GGUF models. Handles mixed-precision loading, CPU+GPU offloading, Metal (Apple), CUDA, and ROCm backends. The foundation under most local inference tools.
- **Ollama**: A wrapper around llama.cpp providing a simple REST API, model management, and easy model pulls (similar to Docker for models). Used in this course's agent lab.
- **LM Studio**: A GUI frontend for llama.cpp. Provides a chat interface and an OpenAI-compatible API endpoint. Useful for non-technical users and rapid experimentation.

All three load GGUF models, handle GPU offloading of as many layers as fit in VRAM (leaving the rest on CPU RAM), and manage the context buffer.

### Critical Thinking Questions

**Question 7.** You are designing the hardware and software stack for a local AI agent deployment in a rural primary care clinic with no reliable internet connection. The clinic sees 40 patients per day and needs the agent to help with clinical documentation (SOAP note drafting, ICD-10 code lookup, medication interaction checking). Design the hardware selection process: what model size do you target, what hardware do you specify, what quantization do you use, and how do you justify the cost?

[[___ Your answer here ___]]

> Consider: 40 patients/day is not high throughput — this is a latency-sensitive, sequential workload. What model capability do you need for clinical documentation? What is the minimum VRAM to run a capable medical-domain model? What are the power constraints in a clinic? How does HIPAA interact with your hardware choice? Is a Mac Mini with M2 Pro (32GB) a reasonable clinical edge device?

---

**Question 8.** Your agent application needs a 32K token context window to process long documents, but your GPU only has 8 GB of VRAM. Running a model large enough for quality output at 32K context would require 20+ GB. List three distinct technical strategies for operating within this constraint, and identify the trade-off each imposes on agent behavior.

[[___ Your answer here ___]]

> Strategies: (1) Context compression / summarization — periodically summarize and truncate conversation history. Trade-off: loses verbatim earlier content. (2) RAG instead of long context — retrieve relevant chunks rather than processing the whole document. Trade-off: retrieval quality determines what the model "sees." (3) CPU offloading — run part of the model on CPU RAM (slower but larger effective memory). Trade-off: significant latency increase. (4) Use a smaller model that fits at 32K context. Trade-off: lower capability.

---

**Question 9.** Running large models locally requires significant hardware: a capable edge system might consume 65–200W continuously. A cloud API call offloads that energy cost — but to a large data center that may or may not use renewable energy. Compare the environmental impact of (a) running a Q4 70B model on a 150W Apple Silicon system for 8 hours/day, (b) making equivalent API calls to a cloud provider. What information would you need to make this comparison accurately, and what does your analysis suggest for sustainable AI agent deployment?

[[___ Your answer here ___]]

> Information needed: local energy source (grid mix vs. renewables), cloud provider's reported PUE (Power Usage Effectiveness) and renewable percentage, number of tokens per hour for each option, whether the local device is idle otherwise (marginal vs. total power). There is no universal answer — local can be greener or dirtier than cloud depending on your grid. What does this imply for where you should physically locate AI inference workloads?

---

## Exercises

**Exercise 1.** Calculate the VRAM requirements for the following configurations, using the formula: VRAM ≈ (parameters × bytes/weight) × 1.15 (to account for KV cache and runtime overhead at modest context lengths). Present your results in a table with columns: Model, Format, Bytes/Weight, Base VRAM, Total with Overhead, Fits in RTX 4090 (24 GB)?

Models: Llama 3 8B and Llama 3 70B. Formats: FP16, INT8, Q4_K_M. That is six configurations total.

> Deliverable: A completed 6-row table, your calculation for each row, and a written conclusion identifying which configurations are viable on a single RTX 4090.

---

**Exercise 2.** If you have access to a system with Ollama installed, run the same prompt through at least two quantization levels of the same base model (e.g., `ollama run llama3:8b` and `ollama run llama3:8b-instruct-q4_K_M`, or equivalent). Use a moderately complex prompt — a math word problem, a code debugging task, or a multi-step reasoning question. Compare:

(a) The quality of the output (correctness, coherence, completeness)
(b) Tokens per second (reported in Ollama's output)
(c) Whether the quality difference would matter for your intended use case

If you do not have access to a system with Ollama, compare two publicly available model cards that report both quantization levels and evaluation results for the same base model.

> Deliverable: The prompt used, both outputs, a quality comparison, a speed comparison, and a use-case recommendation.

---

**Exercise 3.** Research one real-world edge AI deployment from the following domains: medical device inference (e.g., FDA-cleared AI diagnostic tools), autonomous agricultural machinery (precision agriculture AI), or industrial robotics in air-gapped facilities. Write a 400-word case study identifying:

(a) What hardware the system runs on and why
(b) What model capability is required and how it is achieved within hardware constraints
(c) Why cloud inference was unsuitable for this application (latency, connectivity, regulation, or all three)
(d) What the deployment taught engineers about edge AI constraints

> Deliverable: 400-word case study with at least two cited sources.

---

## Reflection Prompt

One of the central tensions in AI is between **centralization and decentralization**. Cloud AI concentrates compute, data, and capability in the hands of a small number of large companies. Edge AI — running models locally on devices individuals and organizations own — distributes that capability outward.

Does widespread local model inference democratize AI, or does it just shift who controls it? A rural clinic with a local model is less dependent on OpenAI — but is now dependent on NVIDIA for GPUs, Qualcomm or Apple for edge chips, and Meta or another organization for open model weights. Is that better?

And at the individual level: if a CS graduate can deploy capable AI on a $2,000 workstation, what does that mean for who can build AI-powered products, who can afford to, and who benefits from the resulting distribution of AI capability?

Write at least 200 words.

[[___ Your reflection here ___]]

---

## Further Reading

- llama.cpp GitHub Repository. (2023–present). *High-performance LLM inference in C/C++.* https://github.com/ggerganov/llama.cpp

- Dettmers, T. et al. (2023). *QLoRA: Efficient Finetuning of Quantized LLMs.* NeurIPS 2023. https://arxiv.org/abs/2305.14314

- Gholami, A. et al. (2021). *A Survey of Quantization Methods for Efficient Neural Network Inference.* In Low-Power Computer Vision. https://arxiv.org/abs/2103.13630

- Frantar, E. et al. (2022). *GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers.* arXiv:2210.17323. https://arxiv.org/abs/2210.17323

- Ollama Documentation. (2024). https://ollama.com/docs

- Apple. (2023). *Apple Silicon Machine Learning Research: Unified Memory Architecture.* https://developer.apple.com/metal/pytorch/
