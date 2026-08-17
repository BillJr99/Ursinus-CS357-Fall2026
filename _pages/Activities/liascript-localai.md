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

The prompts we engineered in the *Prompt Engineering as Agent Design: Personas and System Prompts* activity have so far run against someone else's server. Today every team stands up a complete, private AI stack on its own hardware: **Ollama** to serve models, **OpenWebUI** for a chat interface, and the **REST API** that our agents will call for the rest of the semester. We move from **why local $\rightarrow$ installation $\rightarrow$ model selection and quantization $\rightarrow$ talking to the API from Python**.

> **Before class: the 10-minute pre-install checklist**
>
> 1. Download and install Ollama at home: https://ollama.com/download
> 2. Run `ollama pull llama3.2` (about a 2 GB download) while you are on a good connection.
> 3. Bring the output of `ollama list` to class.
>
> In class we verify installs, fix stragglers, and explore. If your install failed or the download would not finish, do not worry — that is exactly what today's session is for. The Docker/OpenWebUI step (step 5 of the install checklist below) is optional today.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is a hands-on build day: the Manager keeps the install moving, the Recorder logs every command and error, the Presenter demos your working stack at the end, and the Reflector notes friction points to share. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| Ollama | A free, open-source program that downloads AI model files and serves them as a local web API on your own machine, with no account or internet connection required during use | Running `ollama run llama3.2 "Say hello"` on your laptop and getting an answer in seconds |
| OpenWebUI | A browser-based chat interface that connects to your local Ollama server, giving you the look and feel of a commercial chatbot with full privacy | Browsing to `http://localhost:3000` and chatting with a model that never sends data outside your machine |
| REST API | A standard way for programs to communicate over a network using web addresses (URLs) and JSON data — here, the way your Python code talks to Ollama | Calling `requests.post("http://localhost:11434/api/chat", json={...})` to send a prompt and receive a response |
| Quantization | A technique that reduces the storage size of a model by representing each number with fewer bits, trading a small amount of accuracy for the ability to run on ordinary hardware | A 4-bit quantized 8B-parameter model takes roughly 4 GB instead of 16 GB at full precision |
| Parameter count | The number of numerical values (weights) that define a model's learned behavior — roughly correlated with capability, but also with memory and speed requirements | llama3.2 has ~3 billion parameters; larger models like llama3:70b have 70 billion |
| Tokens per second | A measure of how fast a model generates output — each "token" is roughly a word or word-piece, so 10 tokens per second is roughly 10 words per second | You will measure this today by timing a 100-word generation against your system's hardware |

---

# Part I: Why Run Models Locally?

In this part, you will understand the privacy, cost, and capability tradeoffs that motivate running AI models on your own hardware — so that when you choose between local and cloud inference for the rest of the semester, you can justify that choice with specific reasons.

## 1. The Case for Local

Before we get to installation, consider why running AI locally matters. Imagine a doctor who needs to draft a clinical summary using patient records, or a researcher analyzing confidential survey responses. Sending those prompts to a cloud service means the data leaves the institution — potentially violating privacy law. A local model solves this by never letting the data leave the machine at all. At the same time, local models have real limitations: a model that fits on a laptop is far smaller than a frontier cloud model, and knowing which tasks each handles well is a core practitioner skill.

**Privacy.** Prompts sent to a hosted service leave your machine; prompts to a local model never do. For work involving student records, health information, unpublished research, or anything covered by FERPA or an IRB protocol, local inference is often the only responsible choice.

**Cost and control.** A local model has no per-token bill, no rate limits, and no surprise deprecations. You choose the model, pin the version, and reproduce results months later — which connects directly to scientific reproducibility.

**The tradeoff is capability.** Part of becoming a practitioner is learning *which tasks small local models do well* (formatting, extraction, drafting, classification, retrieval-augmented generation over your own documents) and which still demand frontier capability (complex multi-step reasoning, broad world knowledge, subtle creative tasks).

---

## 2. What a Model File Is

A model you download is a tensor (a large multi-dimensional array — think of it as a very large spreadsheet of numbers) of learned numerical weights plus metadata that tells Ollama how to run it. Its size is governed by two numbers: the parameter count $N$ (how many individual weights the model has) and the **quantization level** (the number of bits — the units of computer storage — used to store each weight):

$$
\text{size} \approx N_{\text{params}} \times \frac{\text{bits}}{8} \text{ bytes}
$$

An 8-billion-parameter model at 4-bit quantization occupies roughly $8\text{B} \times 0.5 = 4$ GB. Quantization trades a small amount of accuracy for the ability to run on commodity hardware — it is the reason local AI is practical at all on student laptops.

[[MC]]
A team wants to run a 70B-parameter model quantized to 4 bits on a laptop with 16 GB of RAM. The approximate memory needed for weights alone is:
- ( ) About 8 GB, so it fits comfortably
- (x) About 35 GB, so it does not fit; choose a smaller model or a machine with more RAM
- ( ) About 70 GB regardless of quantization
- ( ) Quantization makes memory use independent of parameter count

> **⚠️ Common Misconception:** Many people assume that a "4-bit" model is four times worse than a "16-bit" model, or that quantization destroys accuracy. In practice, the perceptual quality difference between 4-bit and 16-bit versions of the same model is often surprisingly small for everyday language tasks — the main practical impact is speed and memory, not correctness. The serious quality drop typically happens at 2-bit or below. Choose quantization based on what fits in your RAM, not based on a fear of "lower quality."

---

# Part II: The Build

In this part, you will install and configure your own local AI stack — Ollama to serve models and optionally OpenWebUI for a chat interface — and verify that your Python code can talk to it over a local network connection. Every step is hands-on: the goal by the end of class is a working system you can call from your own scripts.

## 3. Install Checklist

Follow this sequence as a team; the Recorder logs each step's outcome, including the exact error message if a step fails. A failed step is not a problem — it is data. Record the error verbatim, write down your hypothesis for the cause, and test the hypothesis before asking for help. This troubleshooting protocol is itself a course outcome.

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

---

The code cell below sends a single message to your locally running Ollama server using Python's `requests` library (a standard tool for making web requests). If Ollama is running correctly, it will respond with a confirmation message. The second block lists every model currently downloaded on your machine.

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

While a long generation runs, open your system monitor (Activity Monitor on macOS, Task Manager on Windows, or `htop` on Linux) and watch which resources spike.

### Critical Thinking Questions

1. Which resource saturates during generation — CPU, GPU, memory (RAM), or disk? What does that tell you about where the primary bottleneck of local inference lies on your hardware?

   > *Hint: If you have a GPU, watch GPU memory utilization. If you do not, the model falls back to CPU. Either way, something will peg near 100% — that resource is your bottleneck.*

2. Time a 100-word generation using Python's `time` module. Estimate tokens per second, and compare that rate to a hosted service you have used. What kinds of agent designs does slow generation penalize most?

   > *Hint: An agent that makes five tool calls in a loop pays the generation cost five times. Multiply your tokens-per-second by 5 × (average tokens per step) to estimate wall-clock time for a full run.*

3. Disconnect from the network and repeat a prompt. Articulate precisely what data left your machine during the offline run. Why does the answer to this question matter for the FERPA and IRB scenarios in Section 1?

   > *Hint: With the network disconnected, the only data path is between your CPU/GPU and RAM. Nothing leaves the machine. Compare that to what would happen with a cloud API call.*

4. Pull a second model of a different size (for example, `ollama pull llama3.2:1b`) and pose the same reasoning question to both. The Recorder captures both full outputs for the class comparison.

   > *Hint: Choose a question that requires multi-step reasoning, such as a simple math word problem or a question about cause and effect. Single-word-answer questions will not reveal quality differences between model sizes.*

---

## 4. Multi-Turn Conversations: Managing the Message List

The call above sends a single message and forgets it instantly. A real conversation remembers what came before — and here is the key idea: **the Ollama server is stateless.** It does not remember your last turn. *You* remember, by keeping a running `messages` list and re-sending the whole thing on every call. Each turn you append the user's message, send the full list, then append the assistant's reply back onto it. The growing list *is* the conversation's memory.

The cell below holds a three-turn conversation. Notice that `chat()` now takes the entire `messages` list, and that after each reply we append the assistant's message (`r.json()["message"]`) verbatim, so the next turn can see it.

## Code Cell

```python
import requests

def chat(messages, model="llama3.2", temperature=0.7):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        return r.json()["message"]        # the whole assistant message dict
    except Exception as e:
        print(f"[localai:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

# The conversation state we manage by hand:
messages = [{"role": "system", "content": "You are a concise assistant."}]

def say(user_text):
    messages.append({"role": "user", "content": user_text})   # 1. append the user turn
    reply = chat(messages)                                     # 2. send the WHOLE history
    messages.append(reply)                                     # 3. append the reply back on
    print("USER:", user_text)
    print("ASSISTANT:", reply["content"], "\n")

say("My name is Sam and I am planning a trip to Iceland.")
say("What is one thing I should pack?")     # note: this turn never says 'Iceland'...
say("Remind me — what is my name?")         # ...yet the model still knows, from the resent history

print(f"[the message list now holds {len(messages)} entries]")
```

The last question never mentions Iceland or the name Sam, yet the model answers correctly — because the entire prior exchange rode along in the `messages` list. Delete the `messages.append(reply)` line and the model goes amnesiac.

**The same pattern through OpenWebUI.** If you put OpenWebUI in front of Ollama, its OpenAI-compatible endpoint accepts the *identical* growing `messages` array — only the URL, an `Authorization: Bearer <key>` header, and the response path change:

```python
# r = requests.post("http://localhost:3000/api/chat/completions",
#                   headers={"Authorization": f"Bearer {API_KEY}"},
#                   json={"model": "llama3.2", "messages": messages})
# reply = r.json()["choices"][0]["message"]   # OpenWebUI/OpenAI nests it under choices[0]
```

Everything else — append the user turn, resend the whole list, append the reply — stays the same.

## Model: The Growing Context

### Critical Thinking Questions

5. Every turn resends the *entire* history, so a 20-turn chat re-sends turns 1–19 again on turn 20. As the conversation grows, what happens to the number of tokens processed — and therefore the time and cost — per turn?

   > *Hint: If each turn adds roughly the same number of tokens, the total sent by turn $N$ grows like $1 + 2 + \dots + N$. Is that linear or quadratic in $N$?*

6. Every model has a fixed **context window** (a maximum number of tokens it can read at once). What happens when your growing `messages` list exceeds it? Name two strategies to stay under the limit without simply deleting the earliest turns outright.

   > *Hint: You could drop old turns, or you could replace them with a short summary. Which one preserves more of what mattered?*

7. The server is stateless, but your Python process holds the `messages` list in memory. If the program crashes mid-conversation, the history is gone. What would you add to make a conversation survive a restart?

   > *Hint: Think about writing the messages list to disk (as JSON) after each turn and reloading it on startup.*

> **⚠️ Common Misconception:** It is tempting to think the model "remembers" your conversation the way a person does. It does not. Between calls the server keeps *nothing*; the illusion of memory comes entirely from your client resending the full `messages` list each time. When the list grows too long for the context window, that memory silently starts to fall off the front — exactly the problem the *Memory and the Small Context Window* activity later solves with summarization.

---

# Part III: Synthesis and Practice

In this part, you will probe your local model across five different task types to build a concrete capability map — a table showing where it succeeds and where it fails. This map will serve as your baseline for the rest of the semester as you add tools, retrieval, and multi-agent techniques.

## 5. Exercises

1. *Capability map.*

   - *What to do*: As a team, test your local model on five task types: (a) summarize a paragraph, (b) extract key facts into JSON, (c) solve an arithmetic word problem, (d) answer a question about a recent event (post-training-cutoff), and (e) write a short creative passage. Build a table of pass / partial / fail with one sentence of evidence for each cell.
   - *Starter hint*: For the recent-event question, choose something that happened in 2025 or 2026. For extraction, give the model a paragraph and ask for `{"name": ..., "date": ..., "location": ...}` — check whether the JSON is valid.
   - *You've succeeded when*: Your table has five rows, a clear pass/partial/fail verdict for each, and you can identify which failure type (knowledge cutoff, format compliance, reasoning) explains each failing cell.

2. *Quantization estimate.*

   - *What to do*: Using the formula from Section 2, compute the approximate weight-only storage size for models with 1B, 8B, and 70B parameters at both 4-bit and 16-bit quantization. Mark which fit in your laptop's RAM.
   - *Starter hint*: Plug into $\text{size} = N \times \frac{\text{bits}}{8}$ bytes, then convert to GB by dividing by $10^9$. For example, 1B parameters at 4-bit: $1 \times 10^9 \times 0.5 = 0.5$ GB.
   - *You've succeeded when*: You have a 3-by-2 table (three model sizes by two quantization levels) with sizes in GB and a checkmark or cross next to each based on your laptop's actual RAM.

3. *Stack diagram.*

   - *What to do*: Draw a box-and-arrow diagram showing the full data flow from OpenWebUI to Ollama to the model weights and back, plus your Python script as a separate entry point. Label which component owns the system prompt, the sampling parameters (temperature, top-p), and the model weights.
   - *Starter hint*: Your diagram should have at least four boxes: OpenWebUI (or your Python script), the Ollama process, the model weights file on disk, and the GPU or CPU memory where inference actually runs. Arrows should show the direction of data flow for both the input prompt and the output response.
   - *You've succeeded when*: Someone who was not in class today could read your diagram and correctly answer: "Where does the system prompt live? Where do the weights live? What does Ollama actually do?"

---

## Reflection Prompt

*Personal*: You now own a working AI stack that costs nothing per query and shares nothing with anyone outside your machine. Did anything about the installation process surprise you — was it harder or easier than expected? What mental model did you have before about "where AI lives," and how has that changed?

*Technical*: You now have a tool that can run privately on your laptop. Identify one project — academic, personal, or professional — that becomes newly possible for you because privacy and cost are no longer barriers. Describe what you would build and what the remaining obstacle is.

*Societal*: Local AI puts the full capability of a language model in the hands of any individual with a modern laptop, with no oversight, no logging, and no terms of service enforcement. What are two benefits and two risks of that shift in power from institutions to individuals? Who benefits most from local AI, and who might be harmed?

---

→ Coming Up Next: Our models are running. In the *Tool Use and Function Calling* activity we give them structured, machine-readable ways to act on the world — and the local stack you built today is the foundation for the Local Agent Lab. (The question of why the same prompt gives different answers gets its full treatment in the *Why Different Answers Every Time? Sampling, Temperature, and Generation* activity.)

## 6. Further Reading

- Ollama documentation: https://ollama.com and https://github.com/ollama/ollama/blob/main/docs/api.md (see the `/api/chat` `messages` array for multi-turn conversations)
- OpenWebUI documentation: https://docs.openwebui.com
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 3.
