# Running Your Own AI: Ollama, OpenWebUI, and Private Local Models
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-localai.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-localai.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Running Your Own AI: Ollama, OpenWebUI, and Private Local Models

Today every team stands up a complete, private AI stack on its own hardware: **Ollama** to serve models, **OpenWebUI** for a chat interface, and the **REST API** that our agents will call for the rest of the semester. We move from **why local $\rightarrow$ installation $\rightarrow$ model selection and quantization $\rightarrow$ talking to the API from Python**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is a hands-on build day: the Manager keeps the install moving, the Recorder logs every command and error, the Presenter demos your working stack at the end, and the Reflector notes friction points to share. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Why Run Models Locally?

## 1. The Case for Local

**Privacy.** Prompts sent to a hosted service leave your machine; prompts to a local model never do. For work involving student records, health information, unpublished research, or anything covered by FERPA or an IRB protocol, local inference is often the only responsible choice.

**Cost and control.** A local model has no per-token bill, no rate limits, and no surprise deprecations. You choose the model, pin the version, and reproduce results later, which connects directly to scientific reproducibility.

**The tradeoff is capability.** A model that fits on a laptop is far smaller than a frontier hosted model. Part of becoming a practitioner is learning *which tasks small local models do well* (formatting, extraction, drafting, classification, RAG over your own documents) and which still demand frontier capability.

---

## 2. What a Model File Is

A model you download is a tensor of learned weights plus metadata. Its size is governed by parameter count and **quantization**, the number of bits used to store each weight:

$$
\text{size} \approx N_{\text{params}} \times \frac{\text{bits}}{8} \text{ bytes}
$$

An 8-billion-parameter model at 4-bit quantization occupies roughly $8\text{B} \times 0.5 = 4$ GB. Quantization trades a small amount of accuracy for the ability to run on commodity hardware; it is the reason local AI is possible at all.

[[MC]]
A team wants to run a 70B-parameter model quantized to 4 bits on a laptop with 16 GB of RAM. The approximate memory needed for weights alone is:
- ( ) About 8 GB, so it fits comfortably
- (x) About 35 GB, so it does not fit; choose a smaller model
- ( ) About 70 GB regardless of quantization
- ( ) Quantization makes memory use independent of parameter count

---

# Part II: The Build

## 3. Install Checklist

Follow this sequence as a team; the Recorder logs each step's outcome.

```
1. Install Ollama:        https://ollama.com/download
2. Pull a small model:    ollama pull llama3.2
3. Sanity check (CLI):    ollama run llama3.2 "Say hello in five words."
4. Confirm the API:       curl http://localhost:11434/api/tags
5. (Optional) OpenWebUI:  docker run -d -p 3000:8080 \
     -v open-webui:/app/backend/data \
     --name open-webui ghcr.io/open-webui/open-webui:main
6. Browse to http://localhost:3000 and connect it to Ollama.
```

If a step fails, that is data, not defeat: record the error verbatim, hypothesize a cause, and test the hypothesis before asking for help. (This troubleshooting protocol is itself a course outcome.)

---

## Code Cell

```python
import requests

def chat(prompt, model="llama3.2", temperature=0.7):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": temperature},
            "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[localai:chat] {e}")
        import traceback; traceback.print_exc()
        return ""

print(chat("In one sentence, confirm you are running locally."))

# List the models your server currently has
try:
    tags = requests.get("http://localhost:11434/api/tags", timeout=10).json()
    for m in tags.get("models", []):
        print(m["name"], round(m["size"] / 1e9, 2), "GB")
except Exception as e:
    print(f"[localai:tags] {e}")
    import traceback; traceback.print_exc()
```

---

## Model: Reading the Hardware

While a long generation runs, open your system monitor (Activity Monitor, Task Manager, or `htop`).

### Critical Thinking Questions

1. Which resource saturates during generation: CPU, GPU, memory, or disk? What does that tell you about where the bottleneck of local inference lies?
2. Time a 100-word generation. Estimate tokens per second, and compare with a hosted service. What kinds of agent designs does slow generation penalize most?
3. Disconnect from the network and repeat a prompt. Articulate, precisely, what data left your machine. Why does this matter for the FERPA and IRB scenarios in Section 1?
4. Pull a second model of a different size (for example, `ollama pull llama3.2:1b`) and pose the same reasoning question to both. The Recorder captures both outputs for the class comparison.

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Capability map.* As a team, test your local model on five task types (summarize, extract to JSON, arithmetic word problem, recent-events question, creative writing). Build a table of pass/fail with one-sentence evidence each. Which failures could retrieval fix? (Foreshadowing week 5.)
2. *Quantization estimate.* Using the formula in Section 2, estimate weight sizes for 1B, 8B, and 70B models at 4-bit and 16-bit quantization, and mark which fit in your laptop's RAM.
3. *Stack diagram.* Draw the boxes and arrows from OpenWebUI to Ollama to the model file to your Python script. Label which component owns the system prompt, the sampling parameters, and the weights.

---

## Reflection Prompt

In your notebook: you now own a working AI stack that costs nothing per query and shares nothing with anyone. What is one project, personal or academic, that becomes possible for you now that privacy is no longer a barrier? What still stops you?

---

## 5. Further Reading

- Ollama documentation: https://ollama.com and https://github.com/ollama/ollama/blob/main/docs/api.md
- OpenWebUI documentation: https://docs.openwebui.com
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 3.
