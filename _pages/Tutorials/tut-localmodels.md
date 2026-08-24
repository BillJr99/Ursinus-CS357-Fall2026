---
layout: default-standard
permalink: /Tutorials/LocalModels
title: 'CS357: Foundations of Artificial Intelligence - The Local Model Landscape'
info:
  coursenum: CS357
  purpose: "To map the major open-weight model families (Llama, Mistral, Phi, Gemma, and their relatives) so that you can choose what to pull next instead of guessing."
tags:
- local-ai
- models
- ollama
---

# CS357: Foundations of Artificial Intelligence - The Local Model Landscape

## Purpose

To map the major open-weight model families (Llama, Mistral, Phi, Gemma, and their relatives) so that you can choose what to pull next instead of guessing.

## About This Tutorial

The assumption that useful AI requires an API call to a remote server is no longer true.  A modern laptop can run a capable language model offline, and a mid-range workstation can run models that outperform GPT-3.  This module maps **why you would run locally $\rightarrow$ the major model families and their strengths $\rightarrow$ quantization as the hardware equalizer $\rightarrow$ how to match models to tasks**.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|---|---|---|
| Open-Weight Model | A language model whose trained weight files are publicly downloadable; anyone can run, modify, or fine-tune it without paying per call. "Open-weight" does not necessarily mean open-source; licenses vary. | Llama 3.1 8B, Mistral 7B, and Phi-4 are all open-weight models available through Ollama. |
| Quantization | A technique that stores each model weight using fewer bits (e.g., 4 bits instead of 32), reducing file size and RAM requirements at the cost of a small quality decrease. | A 7B model at full precision (F32) needs 28 GB of RAM; the same model at Q4 quantization fits in 4 GB. |
| GGUF | The file format used by llama.cpp (the engine under Ollama) to store quantized models. GGUF files encode both the model weights and the quantization metadata in a single file. | Running `ollama pull llama3.2:3b` downloads a GGUF file to `~/.ollama/models/`. |
| Ollama | A free, open-source tool (install from https://ollama.com) that manages downloading, running, and serving local LLMs through a simple CLI and REST API compatible with the OpenAI API format. | `ollama run phi4` downloads Phi-4 and starts an interactive chat session in your terminal. |
| Mixture of Experts (MoE) | A model architecture where each input token is routed to only a subset of "expert" networks instead of the full model, giving large-model capability at lower per-token compute cost. | Mixtral 8×7B has 46.7B total parameters but activates only ~12.9B per token. |
| Function Calling | The ability of a model to produce structured JSON that specifies which tool to call and with what arguments, required for reliable agentic pipelines. | Hermes-3-Llama-3.1-8B outputs `{"tool_call": {"name": "get_weather", "arguments": {"city": "Philadelphia"}}}` instead of describing the call in prose. |

---

### Before You Start

**What you need:** Ollama installed.  Disk space is the real constraint: budget 2-5 GB per model you pull.

**What you will have at the end:** a considered choice of local model for your own machine, defended against alternatives.

Please work through the sections in order.  Each one builds on the last, and the code blocks are there to be run as you reach them.

---

# Part I: Why Local?

In this part, you will examine the five reasons an organization might choose to run AI locally rather than through a cloud API, and identify which reason applies to which context, because "local is more private" is true but incomplete as a decision rationale.

## 1.  The Case for Running Locally

Running AI on your own hardware is like owning vs. renting: you pay more upfront (hardware or setup time), but you control everything: what runs, who sees your data, and how much you pay at scale.  Renting (an API) is cheaper to start and someone else handles maintenance, but every document you send leaves your hands.

Sending text to a commercial API means your text leaves your machine, traverses the internet, is processed on someone else's hardware, and the interaction may be logged.  For many applications this is entirely acceptable.  For others it is a blocking problem.

**Privacy and data residency.**  Medical notes, legal work product, personal financial records, and protected student information (FERPA) cannot be casually sent to a third-party API. Running locally means the data never leaves the machine or the network perimeter.  Example: a hospital using a local `llama3.1:8b` model to assist with discharge summary drafts ensures patient data stays within HIPAA boundaries.

**Cost at scale.**  API pricing is per-token.  For a high-volume application processing millions of documents, a locally-hosted model on leased GPU hardware often becomes cheaper than API calls within weeks.  Example: at $5/1M tokens (GPT-4o pricing), processing 10 million 1,000-token documents costs $50,000 in API fees, vs. roughly $1,440/month for a dedicated A100.

**Latency and offline operation.**  A locally-running model has no network round-trip.  Embedded devices, field research equipment, and air-gapped systems may have no internet connection at all.  Example: a search-and-rescue team using a local `phi4` model on a laptop to analyze maps and reports in the field.

**Regulatory compliance.**  EU AI Act, HIPAA, and sector-specific regulations impose controls on where data can be processed.  Local deployment gives direct control over data flows and audit trails.

**Customization.**  Open-weight models can be fine-tuned, quantized, and modified in ways a closed API cannot be.  You can run a model entirely offline, modify its system prompt at the binary level, or build it into a product you ship without ongoing API costs.

---

## 2.  The Major Model Families (2024-2025)

"Open-weight" means the model weights are publicly downloadable; the training code and data may or may not be open.  This is distinct from "open source" in the traditional sense.  Licensing varies: Llama 3 permits commercial use with restrictions (no using Meta's models to improve competing foundation models); Mistral models use Apache 2.0; Phi-4 uses MIT. Always check the license for your use case.

| Family | Creator | Size Range | License | Notable Strengths | Ollama Install Command |
|---|---|---|---|---|---|
| Llama 3.x | Meta | 1B, 3B, 8B, 70B, 405B | Meta Llama 3 Community License (commercial use allowed with restrictions) | Best general-purpose balance of capability and ecosystem support; huge number of fine-tunes available; strong instruction-following at every size | `ollama pull llama3.2:3b` or `ollama pull llama3.1:8b` |
| Mistral 7B / Mixtral | Mistral AI | 7B; 8×7B MoE; 8×22B MoE | Apache 2.0 (fully permissive, including commercial use) | Mistral 7B punches above its weight class on benchmarks; Mixtral uses sparse MoE so only 2 of 8 experts activate per token, giving large-model quality at smaller inference cost | `ollama pull mistral:7b` or `ollama pull mixtral:8x7b` |
| Phi-3 / Phi-4 | Microsoft | 3.8B, 7B, 14B | MIT (fully permissive) | Exceptional reasoning capability per parameter; trained on high-quality "textbook-like" synthetic data; strongest small model for math and logic tasks | `ollama pull phi4` or `ollama pull phi3:mini` |
| Gemma 3 | Google DeepMind | 1B, 4B, 12B, 27B | Gemma Terms of Use (free for research and commercial use with attribution) | Strong multilingual performance; vision-capable variants; 128K context window for long-document tasks | `ollama pull gemma3:4b` or `ollama pull gemma3:12b` |
| Qwen 2.5 | Alibaba | 0.5B-72B | Apache 2.0 for most sizes | Strongest multilingual performance across East Asian, Arabic, and European languages; specialized Qwen2.5-Coder and Qwen2.5-Math variants exceed general models on those tasks | `ollama pull qwen2.5:7b` or `ollama pull qwen2.5-coder:7b` |
| DeepSeek-R1 | DeepSeek AI | 1.5B-671B (distilled: 7B, 14B, 70B) | MIT | Explicit chain-of-thought reasoning in output; competitive with proprietary reasoning models; distilled versions run locally and are significantly better at multi-step math than same-size general models | `ollama pull deepseek-r1:7b` or `ollama pull deepseek-r1:14b` |
| Hermes series | Nous Research | Varies (built on Llama/Mistral base) | Inherits base model license | Fine-tuned specifically for function calling, tool use, and structured JSON outputs; widely used in production agentic pipelines where schema adherence is critical | `ollama pull hermes3:8b` |

**Sparse Mixture of Experts (MoE):** Mixtral's architecture routes each token through only 2 of 8 expert feed-forward networks.  The model has 46.7B total parameters but uses only ~12.9B per token.  This gives large-model quality at small-model inference cost, but requires loading all 46.7B parameters into memory.

---

## 3.  Quantization: Fitting Large Models on Real Hardware

A model stored in 32-bit (F32) floating point uses 4 bytes per parameter.  A 7B-parameter model at F32 requires 28 GB, more than most GPUs have.  **Quantization** (compressing model weights from 32-bit floats to 4 or 8-bit integers, trading a small accuracy loss for dramatic memory savings) reduces the number of bits used per weight.  Think of it like compressing a photo: a 4K RAW image and a JPEG of the same scene look nearly identical for most purposes, but the JPEG is 50x smaller.  Similarly, a Q4 model and an F32 model give very similar answers for most tasks, but the Q4 model fits in a fraction of the memory.

- **F16 / BF16:** 16 bits per weight.  Half the memory of F32, negligible quality loss.  Still 14 GB for a 7B model.  Used by most GPU inference when quality is the top priority.
- **Q8:** 8 bits per weight.  Roughly 7 GB for a 7B model.  Quality loss is minimal and generally imperceptible on standard benchmarks.  Good choice when you have the RAM.
- **Q5 / Q5_K_M:** 5 bits per weight.  Roughly 4.5 GB for 7B. Small but measurable quality reduction on difficult reasoning tasks.  Good balance for systems with 8 GB RAM.
- **Q4 / Q4_K_M:** 4 bits per weight.  Roughly 4 GB for 7B. Perceptible quality loss on multi-step reasoning and math; often acceptable for summarization, Q&A, and chat.  The most common format for laptop deployment.
- **Q2 / Q3:** 2-3 bits per weight.  Significant quality degradation; use only when memory is severely constrained and the task is simple.

The suffix `_K_M` in GGUF quantization names (used by Ollama and llama.cpp) refers to a mixed-precision scheme: some layers (particularly attention) are kept at higher precision, while feed-forward layers are quantized more aggressively.  This recovers quality compared to uniform quantization at the same average bit count.

With the model families and quantization levels mapped, Part II applies that knowledge concretely: which models can your specific hardware run, and which model is the right choice for each task category?

---

# Part II: Hardware and Task Matching

In this part, you will match hardware specifications to model sizes, choose models for specific task types, and observe the concrete difference between a generic model and a function-calling-optimized model, a difference that determines whether your agent pipeline works reliably or fails unpredictably.

## Hardware Requirements

These are practical minimums for comfortable (not just technically possible) inference.  "Speed (CPU)" assumes a modern laptop CPU with no GPU acceleration and 8-bit quantization.

| Model Size | Min RAM (CPU inference) | Min VRAM (GPU inference) | Approx. Speed (tokens/s, CPU) | Approx. GGUF File Size (Q4) | Who Can Run This |
|---|---|---|---|---|---|
| 1-3B params | 4 GB RAM | 2-3 GB VRAM | 20-60 tok/s (fast enough for real-time chat) | 1-2 GB | Any student laptop made after 2018 |
| 7-8B params | 8 GB RAM | 5-6 GB VRAM | 8-20 tok/s (slightly slower than human reading speed) | 4-5 GB | Most student laptops; MacBook with M-series chip runs this well |
| 13-14B params | 16 GB RAM | 8-10 GB VRAM | 4-10 tok/s (usable for non-interactive tasks) | 8-9 GB | Higher-end laptops and desktops with dedicated GPU |
| 30-34B params | 32 GB RAM | 20-24 GB VRAM | 1-4 tok/s (slow for interactive use) | 18-20 GB | Workstations with RTX 3090/4090 |
| 70B params | 64 GB RAM | 40-48 GB VRAM | 0.5-2 tok/s (batch processing only) | 38-42 GB | Servers with dual A100s or large unified-memory Macs (M2 Ultra) |

Ollama manages model download, quantization selection, and GPU/CPU layer splitting automatically.  Common commands:

The following commands cover the full Ollama workflow: pulling a model, starting an interactive session, and querying via the Python SDK. Run `ollama list` after pulling to confirm the model downloaded correctly before starting a session.

```

# Install Ollama from https://ollama.com (macOS/Linux/Windows supported)

ollama pull phi4                  # downloads Phi-4 (default Q4 quantization, ~9 GB)
ollama pull llama3.2:3b           # downloads Llama 3.2 3B (fast, ~2 GB)
ollama run qwen2.5-coder:7b       # downloads and starts an interactive session
ollama run deepseek-r1:7b         # reasoning model with visible chain-of-thought
ollama list                       # shows locally cached models and their sizes
ollama ps                         # shows currently running models

# Use Ollama with the OpenAI Python SDK (same API format):

# pip install openai

# client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# response = client.chat.completions.create(model="llama3.2:3b", messages=[...])
```

### Questions to Work Through

1.  You have a laptop with 16 GB of RAM and no discrete GPU. Which models from the table can you run at Q4 quantization?  At Q8?  What is the quality trade-off of choosing Q4 over Q8 for a legal document summarization task?

   *Hint:* At Q4, a 7B model uses ~4 GB and a 13B model uses ~8 GB. At Q8, a 7B model uses ~7 GB and a 13B model uses ~14 GB. Legal summarization requires faithfulness to source material: which quantization level is more likely to miss a key clause?

2.  A 7B model running on a CPU at 10 tokens/second takes roughly 30 seconds to generate a 300-token response.  A 70B model accessed via API generates the same response in 3 seconds.  For an interactive chat application, which is preferable?  Does the answer change for a batch processing pipeline running overnight?

   *Hint:* Interactive chat users typically abandon after 15-20 seconds of waiting.  Batch processing doesn't have a human waiting; it just runs overnight.  Consider both speed and cost (API charges per token; local runs free after hardware is paid for).

3.  Mixtral 8×7B has 46.7B total parameters but activates only ~12.9B per token.  Does it fit in the "7-8B" hardware row or the "30-34B" row of the table above?  Justify your answer by thinking about what hardware operation determines memory requirements versus compute requirements.

   *Hint:* Memory requirements are set by how much you need to *store* (all 46.7B parameters must be loaded into RAM).  Compute requirements are set by how much you need to *calculate* per token (~12.9B active parameters).  Which row is about storage and which is about speed?

---

## Task-to-Model Matching

Choosing a model is an engineering decision, not just a capability question.  Smaller, specialized models often outperform larger general models on specific tasks while using far less hardware.

The table below maps task categories to recommended models.  Use it as a starting point, not a final answer; run two models against your actual task and let the output quality guide the final choice.

| Task | Recommended Model | Why | Alternative | How to Start |
|---|---|---|---|---|
| Quick factual Q&A on a known domain | Llama 3.2 3B (with RAG) | Low latency at 30-60 tok/s; RAG compensates for small model's limited parametric knowledge; fits on any laptop | Phi-4 mini (even stronger reasoning at similar size) | `ollama pull llama3.2:3b` |
| Code generation (Python, JavaScript) | Qwen2.5-Coder 7B | Specialized code training; top HumanEval benchmarks at 7B size; fits in 8 GB RAM | DeepSeek-Coder-V2-Lite (fast, Apache 2.0) | `ollama pull qwen2.5-coder:7b` |
| Multi-step mathematical reasoning | DeepSeek-R1 distill (7B or 14B) | Explicit chain-of-thought reasoning traces visible in output; significantly outperforms general models of same size on math | Phi-4 14B (strong math, no visible reasoning) | `ollama pull deepseek-r1:14b` |
| Function calling / tool use for agents | Hermes-3-Llama-3.1-8B | Fine-tuned specifically for JSON function call output format; reliable schema adherence in agentic pipelines | Qwen2.5 7B (has native tool calling built in) | `ollama pull hermes3:8b` |
| Long document summarization | Gemma 3 12B | 128K context window handles very long documents; strong multilingual coverage | Llama 3.1 8B (also has 128K context, slightly smaller) | `ollama pull gemma3:12b` |
| Creative writing / narrative | Llama 3 70B (if hardware allows) | Larger models show qualitatively better creative coherence, vocabulary variety, and plot structure | Mistral 7B (surprisingly strong creative writing for its size) | `ollama pull llama3.1:70b` (requires 64 GB RAM) |
| Multilingual support (non-English) | Qwen 2.5 7B | Strongest multilingual training across East Asian, Arabic, and European languages | Gemma 3 (strong multilingual, long context) | `ollama pull qwen2.5:7b` |

---

## Generic Model vs. Function-Calling Model

The difference between a generic model and a function-calling-optimized model is not just output quality; it is structural reliability.  Agentic pipelines that call tools depend on the model producing parseable JSON, not prose.  Think of it like the difference between someone who can describe how to fill out a form vs. someone who actually fills it out correctly.

The two outputs below come from the same user query sent to two different models.  Read them carefully; the difference is not intelligence or fluency, it is whether the output is machine-parseable or just prose that describes what a machine call would look like.

**Scenario:** A weather agent exposes this tool:

```python

# Tool definition (this is what the agent framework sends to the model)
def get_weather(city: str) -> dict:
    """
    Fetches current weather for a city.
    Returns: {"city": str, "temp_c": float, "condition": str}
    """
    ...
```

**User query:** "What's the weather like in Philadelphia right now?"

---

**Generic model output (e.g., base `llama3.1:8b` without function-calling fine-tune):**

```
To check the weather in Philadelphia, I would call the get_weather function
with the city parameter set to "Philadelphia". This would return a dictionary
containing the temperature in Celsius and the current weather conditions.
Would you like me to proceed with that call?
```

This is prose *describing* a function call.  An agent framework trying to parse this for an actionable tool invocation will fail or require brittle regex extraction.

---

**Function-calling-optimized model output (e.g., `hermes3:8b` via `ollama pull hermes3:8b`):**

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

This is valid JSON conforming to the tool schema.  The agent framework can parse, validate, and execute it directly.  The difference is not intelligence; it is format training.  Hermes-3 was explicitly fine-tuned on thousands of examples of correct tool-call JSON so the output format is highly reliable.

> **Common Misconception:** Many beginners assume that a more capable (larger) general model will automatically be better at function calling than a smaller specialized model.  In practice, **a 7B model fine-tuned for function calling (like Hermes-3) reliably outperforms a 70B general model** on structured tool-call tasks.  The 70B model is smarter but doesn't reliably produce the right JSON structure.  Use the right tool for the job.

Q4 quantization of a 7B language model means:

- Each model weight is stored using 4 bits instead of 16 or 32 bits, reducing file size by roughly 4-8x with modest quality loss on complex tasks
- The model has been trained on a dataset where only 4 quantiles (25th, 50th, 75th, 100th percentile) of examples are included; "Q4" refers to a training data selection strategy
- The model runs exactly 4 times faster and outputs identical results; lower precision removes rounding errors that slow down computation without affecting outputs
- Only the 4 outermost transformer layers are quantized to 1-bit precision; the inner layers remain at full FP16; this is how mixed-precision quantization works

<details markdown="1"><summary>Answer</summary>

Each model weight is stored using 4 bits instead of 16 or 32 bits, reducing file size by roughly 4-8x with modest quality loss on complex tasks

</details>

With hardware matching and model selection understood, Part III gives you hands-on practice pulling and comparing real models so that your model choice for the final project is grounded in direct observation rather than benchmark numbers alone.

---

# Part III: Synthesis and Practice

Next you will pull and compare real models on your own hardware, test the quantization tradeoff on a concrete task, and analyze the privacy implications of local versus cloud data flows, the three exercises that turn this module's concepts into deployable decisions.

## Exercises

1.  *Model selection audit.*  Using `ollama list` and `ollama pull`, download two models you can run on your available hardware.  For the same five prompts (one factual, one creative, one code, one reasoning, one multilingual), run both models and rate the outputs on a 1-5 scale.  Report which model wins each task and whether the result matches the recommendations in Model 2.

   *What to do:* Choose two models that fit your RAM (use the hardware table).  Run each model with `ollama run <model>` and type the same five prompts.  Use the same prompt text for both models; do not rephrase.

   *Starter hint:*
   ```bash
   # Pull two models that fit your hardware
   ollama pull llama3.2:3b        # ~2 GB, runs on any laptop
   ollama pull phi4               # ~9 GB, needs 16 GB RAM

   # Run each model interactively
   ollama run llama3.2:3b

   # Or query via Python (pip install openai)
   from openai import OpenAI
   client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

   prompts = [
       "What year did the Berlin Wall fall, and what caused it?",  # factual
       "Write the opening paragraph of a short story set in a lighthouse.",  # creative
       "Write a Python function that checks if a string is a palindrome.",  # code
       "If a train leaves Philadelphia at 9 AM at 60 mph heading to NYC (95 miles away), and another leaves NYC at 9:30 AM at 80 mph, when do they meet?",  # reasoning
       "Translate 'Good morning, I hope you have a wonderful day' into Spanish, French, and Japanese.",  # multilingual
   ]
   for prompt in prompts:
       response = client.chat.completions.create(
           model="llama3.2:3b",
           messages=[{"role": "user", "content": prompt}]
       )
       print(response.choices[0].message.content)
   ```

   *You've succeeded when:* You have a 5×2 comparison table (5 tasks × 2 models) with a 1-5 rating and a one-sentence justification for each cell.  Discuss whether the results surprised you.

2.  *Quantization comparison.*  Pull the same base model at two quantization levels (e.g., `qwen2.5:7b-instruct-q4_K_M` and `qwen2.5:7b-instruct-q8_0`).  Ask a math reasoning problem that requires multi-step arithmetic.  Report the answer, any visible reasoning errors, and the generation speed in tokens/second for each quantization.  Does the quality difference justify the memory difference for this task?

   *What to do:* Use `ollama pull qwen2.5:7b-instruct-q4_K_M` and `ollama pull qwen2.5:7b-instruct-q8_0`.  Run the same math problem with both.  Time each response using Python's `time` module.

   *Starter hint:*
   ```python
   import time
   from openai import OpenAI

   client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
   problem = """A store sells apples for $0.75 each and oranges for $1.20 each.
   Maria buys 8 apples and 5 oranges. She pays with a $20 bill.
   How much change does she receive? Show your work step by step."""

   for model in ["qwen2.5:7b-instruct-q4_K_M", "qwen2.5:7b-instruct-q8_0"]:
       start = time.time()
       response = client.chat.completions.create(
           model=model,
           messages=[{"role": "user", "content": problem}]
       )
       elapsed = time.time() - start
       text = response.choices[0].message.content
       tokens = response.usage.completion_tokens
       print(f"\n=== {model} ===")
       print(f"Answer: {text}")
       print(f"Speed: {tokens/elapsed:.1f} tok/s, Total tokens: {tokens}")
   ```

   *You've succeeded when:* You can report the correct answer ($7.60 change), identify whether either model made an arithmetic error, and state whether the speed difference (typically 1.5-2x) justifies the memory difference (7 GB vs. 4 GB) for this task.

3.  *Function calling stress test.*  Using `hermes3:8b` or a Qwen2.5 model with tool-calling support (`ollama pull qwen2.5:7b`), define a tool with three parameters (one optional).  Send 10 queries: 5 that should trigger the tool and 5 that should not.  Report the success rate of (a) correct tool invocation when appropriate, (b) correct abstention when the tool is not needed, and (c) schema conformance on successful calls.

   *What to do:* Define a simple `search_database(query: str, limit: int, filter_category: str = None)` tool in your system prompt.  Send 5 queries that require database search and 5 general questions.  Parse the JSON output and count successes.

   *Starter hint:*
   ```python
   SYSTEM = """You have access to one tool:
   search_database(query: str, limit: int, filter_category: str = None)
   - Searches a product database and returns matching items.
   - query: the search terms (required)
   - limit: max results to return, 1-20 (required)
   - filter_category: optional category filter, e.g. "electronics" or "clothing"

   When a user asks about products, respond ONLY with a JSON tool call:
   {"tool_call": {"name": "search_database", "arguments": {...}}}
   For other questions, respond normally in plain text."""

   tool_queries = [
       "Find me blue running shoes under $100",        # should call tool
       "Show me 5 laptops with 16GB RAM",              # should call tool
       "What gaming keyboards do you have?",           # should call tool
       "I need 3 birthday gift ideas for a 10-year-old", # should call tool
       "Search for wireless earbuds, max 10 results",  # should call tool
   ]
   non_tool_queries = [
       "What is the capital of France?",               # should NOT call tool
       "How do I write a Python function?",            # should NOT call tool
       "What time is it in Tokyo right now?",          # should NOT call tool
       "Can you write me a haiku about autumn?",       # should NOT call tool
       "Explain how photosynthesis works.",            # should NOT call tool
   ]
   ```

   *You've succeeded when:* You have a 10-row result table showing each query, whether the model called the tool or not, whether that was correct, and (for tool calls) whether the JSON was valid and schema-conformant.  A good function-calling model should score 8-10/10.

4.  *Privacy scenario analysis.*  Your institution wants to use an AI assistant to help staff draft responses to student FERPA requests.  The assistant must read student record excerpts.  Identify every point in a cloud-API-based pipeline where student data would leave institutional control, and describe how a local model deployment with Ollama changes the data flow diagram.

   *What to do:* Draw (or describe in text) the data flow for (a) a pipeline using the OpenAI API and (b) a pipeline using `ollama run llama3.1:8b` on a campus server.  Mark every point where data crosses institutional boundaries.

   *Starter hint:* In the cloud API pipeline, data leaves institutional control at: (1) the HTTPS request to api.openai.com, (2) OpenAI's servers where inference occurs, (3) OpenAI's logging infrastructure (if enabled).  In the Ollama pipeline, if the server runs on campus hardware connected only to the campus network, data never leaves institutional control.  What firewall rules would you add to enforce this?

   *You've succeeded when:* You have two data flow diagrams (or detailed descriptions) with each data-crossing point labeled, and a written explanation of which FERPA requirements each pipeline does and does not satisfy.

---

## Reflection Prompt

*Personal:* Have you ever used a tool or app that processed your personal information (health, finances, messages) on a remote server without you realizing it?  How did that feel when you found out?  How does the option to run AI locally change your relationship to AI tools?

*Technical:* Open-weight models make powerful AI accessible without ongoing API costs or data sharing, but they also make powerful AI accessible without the safety interventions commercial providers apply.  Identify one beneficial use case enabled by local open-weight models that would be difficult or impossible with a commercial API, and one risk that local deployment introduces compared to a managed API.

*Societal:* What does it mean for AI governance and regulation when capable models can be downloaded for free and run by anyone with a laptop?  Identify one policy lever (a licensing requirement, a usage disclosure rule, a technical standard) that could address a specific risk of locally-run open-weight models without unnecessarily restricting beneficial uses.  Who should implement that lever: national governments, AI developers, platform providers, or end users?

---

## Where This Goes Next

Now that you can run models locally, the next module examines the security implications of deploying AI agents: what happens when an agent with tool access is manipulated by malicious input, and how to build defenses.

---

## Further Reading

- Touvron et al. "Llama 2: Open Foundation and Fine-Tuned Chat Models." arXiv:2307.09288 (2023).  Representative of the Llama family design philosophy.
- Jiang et al. "Mistral 7B." arXiv:2310.06825 (2023).  The Mistral 7B architecture and benchmark results.
- Microsoft Research.  "Phi-3 Technical Report." arXiv:2404.14219 (2024).  Small model, large capability through data curation.
- Ollama model library: https://ollama.com/library
- GGUF quantization format documentation: https://github.com/ggerganov/llama.cpp/blob/master/docs/gguf.md
