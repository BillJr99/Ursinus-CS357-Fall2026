# The Local Model Landscape: Llama, Mistral, Phi, Gemma, and Friends
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-localmodels.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-localmodels.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Local Model Landscape: Llama, Mistral, Phi, Gemma, and Friends

The assumption that useful AI requires an API call to a remote server is no longer true. A modern laptop can run a genuinely capable language model offline, and a mid-range workstation can run models that outperform GPT-3. This module maps **why you would run locally $\rightarrow$ the major model families and their strengths $\rightarrow$ quantization as the hardware equalizer $\rightarrow$ how to match models to tasks**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Why Local?

## 1. The Case for Running Locally

Sending text to a commercial API means your text leaves your machine, traverses the internet, is processed on someone else's hardware, and the interaction may be logged. For many applications this is entirely acceptable. For others it is a blocking problem.

**Privacy and data residency.** Medical notes, legal work product, personal financial records, and protected student information (FERPA) cannot be casually sent to a third-party API. Running locally means the data never leaves the machine or the network perimeter.

**Cost at scale.** API pricing is per-token. For a high-volume application processing millions of documents, a locally-hosted model on leased GPU hardware often becomes cheaper than API calls within weeks.

**Latency and offline operation.** A locally-running model has no network round-trip. Embedded devices, field research equipment, and air-gapped systems may have no internet connection at all.

**Regulatory compliance.** EU AI Act, HIPAA, and sector-specific regulations impose controls on where data can be processed. Local deployment gives direct control.

**Customization.** Open-weight models can be fine-tuned, quantized, and modified in ways a closed API cannot be.

---

## 2. The Major Model Families (2024–2025)

"Open-weight" means the model weights are publicly downloadable; the training code and data may or may not be open. This is distinct from "open source" in the traditional sense. Licensing varies: Llama 3 permits commercial use with restrictions (no using Meta's models to improve competing foundation models); Mistral models use Apache 2.0; Phi-4 uses MIT. Always check the license for your use case.

| Family | Creator | Size Range | License | Notable Strengths |
|---|---|---|---|---|
| Llama 3.x | Meta | 1B, 3B, 8B, 70B, 405B | Meta Llama 3 Community License | General-purpose; strong instruction-following; broad ecosystem of fine-tunes |
| Mistral 7B / Mixtral | Mistral AI | 7B; 8×7B MoE; 8×22B MoE | Apache 2.0 | Mistral 7B punches above its weight; Mixtral uses sparse MoE (only 2 of 8 experts active per token) for large-model quality at smaller inference cost |
| Phi-3 / Phi-4 | Microsoft | 3.8B, 7B, 14B | MIT | Exceptional reasoning per parameter; trained on high-quality "textbook-like" data; strong math and logic |
| Gemma 3 | Google DeepMind | 1B, 4B, 12B, 27B | Gemma Terms of Use | Multilingual; vision-capable variants; long context (128K) |
| Qwen 2.5 | Alibaba | 0.5B–72B | Apache 2.0 (most sizes) | Strongest multilingual; specialized Qwen2.5-Coder and Qwen2.5-Math variants |
| DeepSeek-R1 | DeepSeek AI | 1.5B–671B (distilled: 7B, 14B, 70B) | MIT | Explicit chain-of-thought reasoning; competitive with proprietary reasoning models; distilled versions run locally |
| Hermes series | Nous Research | Varies (built on Llama/Mistral) | Inherits base model license | Fine-tuned for function calling, tool use, and structured outputs; widely used in agentic pipelines |

**Sparse Mixture of Experts (MoE):** Mixtral's architecture routes each token through only 2 of 8 expert feed-forward networks. The model has 46.7B total parameters but uses only ~12.9B per token. This gives large-model quality at small-model inference cost — but requires loading all 46.7B parameters into memory.

---

## 3. Quantization: Fitting Large Models on Real Hardware

A model stored in 32-bit (F32) floating point uses 4 bytes per parameter. A 7B-parameter model at F32 requires 28 GB — more than most GPUs have. **Quantization** reduces the number of bits used per weight.

- **F16 / BF16:** 16 bits per weight. Half the memory of F32, negligible quality loss. Still 14 GB for a 7B model.
- **Q8:** 8 bits per weight. ~7 GB for a 7B model. Quality loss is minimal and generally imperceptible.
- **Q5 / Q5_K_M:** 5 bits per weight. ~4.5 GB for 7B. Small but measurable quality reduction on difficult tasks.
- **Q4 / Q4_K_M:** 4 bits per weight. ~4 GB for 7B. Perceptible quality loss on reasoning-heavy tasks; often acceptable for summarization and chat.
- **Q2 / Q3:** 2–3 bits per weight. Significant quality degradation; use only when memory is severely constrained.

The suffix `_K_M` in GGUF quantization names (used by Ollama and llama.cpp) refers to a mixed-precision scheme: some layers (particularly attention) are kept at higher precision, while feed-forward layers are quantized more aggressively. This recovers quality compared to uniform quantization.

---

# Part II: Hardware and Task Matching

## Model 1: Hardware Requirements

These are practical minimums for comfortable (not just technically possible) inference. "Speed (CPU)" assumes a modern laptop CPU with no GPU acceleration and 8-bit quantization.

| Model Size | Min RAM (no GPU) | Min VRAM (GPU inference) | Approx. Speed (tokens/s, CPU) | Approximate GGUF File Size (Q4) |
|---|---|---|---|---|
| 1–3B params | 4 GB | 2–3 GB | 20–60 tok/s | 1–2 GB |
| 7–8B params | 8 GB | 5–6 GB | 8–20 tok/s | 4–5 GB |
| 13–14B params | 16 GB | 8–10 GB | 4–10 tok/s | 8–9 GB |
| 30–34B params | 32 GB | 20–24 GB | 1–4 tok/s | 18–20 GB |
| 70B params | 64 GB | 40–48 GB | 0.5–2 tok/s | 38–42 GB |

Ollama manages model download, quantization selection, and GPU/CPU layer splitting automatically. Common commands:

```
ollama pull phi4             # downloads Phi-4 (default quantization)
ollama pull llama3.2:3b      # downloads Llama 3.2 3B
ollama run qwen2.5-coder:7b  # downloads and starts an interactive session
ollama list                  # shows locally cached models
```

### Critical Thinking Questions

1. You have a laptop with 16 GB of RAM and no discrete GPU. Which models from the table can you run at Q4 quantization? At Q8? What is the quality trade-off of choosing Q4 over Q8 for a legal document summarization task?
2. A 7B model running on a CPU at 10 tokens/second takes roughly 30 seconds to generate a 300-token response. A 70B model accessed via API generates the same response in 3 seconds. For an interactive chat application, which is preferable? Does the answer change for a batch processing pipeline running overnight?
3. Mixtral 8×7B has 46.7B total parameters but activates only ~12.9B per token. Does it fit in the "7–8B" hardware row or the "30–34B" row of the table above? Justify your answer by thinking about what hardware operation determines memory requirements versus compute requirements.

---

## Model 2: Task-to-Model Matching

Choosing a model is an engineering decision, not just a capability question. Smaller, specialized models often outperform larger general models on specific tasks while using far less hardware.

| Task | Recommended Model | Why | Alternative |
|---|---|---|---|
| Quick factual Q&A on a known domain | Llama 3.2 3B (with RAG) | Low latency; RAG compensates for small model's limited parametric knowledge | Phi-4 mini |
| Code generation (Python, JavaScript) | Qwen2.5-Coder 7B | Specialized code training; strong HumanEval benchmarks; fits on 8 GB RAM | DeepSeek-Coder-V2-Lite |
| Multi-step mathematical reasoning | DeepSeek-R1 distill (7B or 14B) | Explicit chain-of-thought; reasoning traces visible in output | Phi-4 14B |
| Function calling / tool use | Hermes-3-Llama-3.1-8B | Fine-tuned specifically for JSON function call output format; reliable schema adherence | Qwen2.5 7B (has native tool calling) |
| Long document summarization | Gemma 3 12B | 128K context window; strong multilingual coverage | Llama 3.1 8B (128K context) |
| Creative writing / narrative | Llama 3 70B (if hardware allows) | Larger models show qualitatively better creative coherence and style variety | Mistral 7B |
| Multilingual support (non-English) | Qwen 2.5 7B | Strongest multilingual training across East Asian, Arabic, and European languages | Gemma 3 |

---

## Model 3: Generic Model vs. Function-Calling Model

The difference between a generic model and a function-calling-optimized model is not just output quality — it is structural reliability. Agentic pipelines that call tools depend on the model producing parseable JSON, not prose.

**Scenario:** A weather agent exposes this tool:

```
get_weather(city: str) -> dict
Returns: {"city": str, "temp_c": float, "condition": str}
```

**User query:** "What's the weather like in Philadelphia right now?"

---

**Generic model output (e.g., base Llama 3.1 8B without function-calling fine-tune):**

```
To check the weather in Philadelphia, I would call the get_weather function
with the city parameter set to "Philadelphia". This would return a dictionary
containing the temperature in Celsius and the current weather conditions.
Would you like me to proceed with that call?
```

This is prose *describing* a function call. An agent framework trying to parse this for an actionable tool invocation will fail or require brittle regex extraction.

---

**Function-calling-optimized model output (e.g., Hermes-3-Llama-3.1-8B):**

```json
{
  "tool_call": {
    "name": "get_weather",
    "arguments": {
      "city": "Philadelphia"
    }
  }
}
```

This is valid JSON conforming to the tool schema. The agent framework can parse, validate, and execute it directly. The difference is not intelligence — it is format training.

[[MC]]
Q4 quantization of a 7B language model means:
- (x) Each model weight is stored using 4 bits instead of 16 or 32 bits, reducing file size by roughly 4–8x with modest quality loss on complex tasks
- ( ) The model has been trained on four quantiles of the training data distribution
- ( ) The model runs exactly 4 times faster with no quality loss whatsoever
- ( ) Only the 4 outermost layers of the model are quantized; the rest remain at full precision

---

# Part III: Synthesis and Practice

## Exercises

1. *Model selection audit.* Using `ollama list` and `ollama pull`, download two models you can run on your available hardware. For the same five prompts (one factual, one creative, one code, one reasoning, one multilingual), run both models and rate the outputs on a 1–5 scale. Report which model wins each task and whether the result matches the recommendations in Model 2.
2. *Quantization comparison.* Pull the same base model at two quantization levels (e.g., `qwen2.5:7b-instruct-q4_K_M` and `qwen2.5:7b-instruct-q8_0`). Ask a math reasoning problem that requires multi-step arithmetic. Report the answer, any visible reasoning errors, and the generation speed in tokens/second for each quantization. Does the quality difference justify the memory difference for this task?
3. *Function calling stress test.* Using Hermes or a Qwen2.5 model with tool-calling support, define a tool with three parameters (one optional). Send 10 queries: 5 that should trigger the tool and 5 that should not. Report the success rate of (a) correct tool invocation when appropriate, (b) correct abstention when the tool is not needed, and (c) schema conformance on successful calls.
4. *Privacy scenario analysis.* Your institution wants to use an AI assistant to help staff draft responses to student FERPA requests. The assistant must read student record excerpts. Identify every point in a cloud-API-based pipeline where student data would leave institutional control, and describe how a local model deployment with Ollama changes the data flow diagram.

---

## Reflection Prompt

In your notebook: open-weight models make powerful AI accessible without ongoing API costs or data sharing, but they also make powerful AI accessible without the safety interventions commercial providers apply. Identify one beneficial use case enabled by local open-weight models that would be difficult or impossible with a commercial API, and one risk that local deployment introduces compared to a managed API. What does this suggest about who should bear responsibility for AI safety as models become more widely deployable?

---

## Further Reading

- Touvron et al. "Llama 2: Open Foundation and Fine-Tuned Chat Models." arXiv:2307.09288 (2023). Representative of the Llama family design philosophy.
- Jiang et al. "Mistral 7B." arXiv:2310.06825 (2023). The Mistral 7B architecture and benchmark results.
- Microsoft Research. "Phi-3 Technical Report." arXiv:2404.14219 (2024). Small model, large capability through data curation.
- Ollama model library: https://ollama.com/library
- GGUF quantization format documentation: https://github.com/ggerganov/llama.cpp/blob/master/docs/gguf.md
