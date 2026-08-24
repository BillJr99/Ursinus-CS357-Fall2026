<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-localai.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-localai.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Running Your Own AI: Ollama, OpenWebUI, and Private Local Models

Every model you have talked to so far, in this course or anywhere else, has run on someone else's server.  Today that stops.  Today every team stands up a complete, private AI stack on its own hardware: **Ollama** to serve models, **OpenWebUI** for a chat interface, and the **REST API** that our agents will call for the rest of the semester.  We move from **why local $\rightarrow$ installation $\rightarrow$ model selection and quantization $\rightarrow$ talking to the API from Python**.

> **Before class: the 10-minute pre-install checklist**
>
> 1.  Download and install Ollama at home: https://ollama.com/download
> 2.  Run `ollama pull llama3.2` (about a 2 GB download) while you are on a good connection.
> 3.  Bring the output of `ollama list` to class.
>
> In class we verify installs, fix stragglers, and explore.  If your install failed or the download would not finish, do not worry; that is exactly what today's session is for.  The Docker/OpenWebUI step (step 5 of the install checklist below) is optional today.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Today is a hands-on build day: the Manager keeps the install moving, the Recorder logs every command and error, the Presenter demos your working stack at the end, and the Reflector notes friction points to share.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| Ollama | A free, open-source program that downloads AI model files and serves them as a local web API on your own machine, with no account or internet connection required during use | Running `ollama run llama3.2 "Say hello"` on your laptop and getting an answer in seconds |
| OpenWebUI | A browser-based chat interface that connects to your local Ollama server, giving you the look and feel of a commercial chatbot with full privacy | Browsing to `http://localhost:3000` and chatting with a model that never sends data outside your machine |
| REST API | A standard way for programs to communicate over a network using web addresses (URLs) and JSON data; here, the way your Python code talks to Ollama | Calling `requests.post("http://localhost:11434/api/chat", json={...})` to send a prompt and receive a response |
| Quantization | A technique that reduces the storage size of a model by representing each number with fewer bits, trading a small amount of accuracy for the ability to run on ordinary hardware | A 4-bit quantized 8B-parameter model takes roughly 4 GB instead of 16 GB at full precision |
| Parameter count | The number of numerical values (weights) that define a model's learned behavior, roughly correlated with capability, but also with memory and speed requirements | llama3.2 has ~3 billion parameters; larger models like llama3:70b have 70 billion |
| Tokens per second | A measure of how fast a model generates output; each "token" is roughly a word or word-piece, so 10 tokens per second is roughly 10 words per second | You will measure this today by timing a 100-word generation against your system's hardware |
| Temperature | A setting you control, not something baked into the model, that decides how much the model varies its wording. Near 0 it gives you nearly the same answer every time; near 1 it wanders. It is one of several *sampling parameters* (`top-p` is another) that sit between the model and the text you read | The **Advanced Params** panel in OpenWebUI, and the `options` block of your Python call. Section 3c has you turn it yourself; *Why Different Answers Every Time?* explains what it does to the math |
| `host.docker.internal` | A hostname Docker resolves, from inside a container, to the machine the container is running on. Inside a container, `localhost` means the container itself | An agent in a container reaching your laptop's Ollama at `http://host.docker.internal:11434` instead of `localhost` |
| API key (OpenWebUI) | A token you generate on your own OpenWebUI server that identifies you to it. It authenticates you to software on your machine; it is not a payment credential, and Ollama needs none at all | The `OPENWEBUI_API_KEY` you mint in Section 3b and use for the rest of the semester |

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Part I, why local at all: the four reasons, and which one is yours |
| 10-20 | Pull a model and get one response back on your own machine |
| 20-55 | Part II, the build: OpenWebUI, the connection troubleshooting in 3a, your API key, the API call, and the temperature dial |
| 55-70 | Compare answers across two models on the same prompt |
| 70-75 | Reflection prompt, and what to post before next session |

---
# Part I: Why Run Models Locally?

In this part, you will understand the privacy, cost, and capability tradeoffs that motivate running AI models on your own hardware, so that when you choose between local and cloud inference for the rest of the semester, you can justify that choice with specific reasons.

## 1.  The Case for Local

Before we get to installation, consider why running AI locally matters.  Imagine a doctor who needs to draft a clinical summary using patient records, or a researcher analyzing confidential survey responses.  Sending those prompts to a cloud service means the data leaves the institution, potentially violating privacy law.  A local model solves this by never letting the data leave the machine at all.  At the same time, local models have real limitations: a model that fits on a laptop is far smaller than a frontier cloud model, and knowing which tasks each handles well is a core practitioner skill.

**Privacy.**  Prompts sent to a hosted service leave your machine; prompts to a local model never do.  For work involving student records, health information, unpublished research, or anything covered by FERPA or an IRB protocol, local inference is often the only responsible choice.

**Cost and control.**  A local model has no per-token bill, no rate limits, and no surprise deprecations.  You choose the model, pin the version, and reproduce results months later, which connects directly to scientific reproducibility.

The tradeoff is capability.  Part of becoming a practitioner is learning *which tasks small local models do well* (formatting, extraction, drafting, classification, retrieval-augmented generation over your own documents) and which still demand frontier capability (complex multi-step reasoning, broad world knowledge, subtle creative tasks).

---

## 2.  What a Model File Is

A model you download is a tensor (a large multi-dimensional array; think of it as a very large spreadsheet of numbers) of learned numerical weights plus metadata that tells Ollama how to run it.  Its size is governed by two numbers: the parameter count $N$ (how many individual weights the model has) and the **quantization level** (the number of bits, the units of computer storage, used to store each weight):

$$
\text{size} \approx N_{\text{params}} \times \frac{\text{bits}}{8} \text{ bytes}
$$

An 8-billion-parameter model at 4-bit quantization occupies roughly $8\text{B} \times 0.5 = 4$ GB. Quantization trades a small amount of accuracy for the ability to run on commodity hardware; it is the reason local AI is practical at all on student laptops.

A team wants to run a 70B-parameter model quantized to 4 bits on a laptop with 16 GB of RAM. The approximate memory needed for weights alone is:

[( )] About 8 GB, so it fits comfortably
[(X)] About 35 GB, so it does not fit; choose a smaller model or a machine with more RAM
[( )] About 70 GB regardless of quantization
[( )] Quantization makes memory use independent of parameter count

> **Common Misconception:** Many people assume that a "4-bit" model is four times worse than a "16-bit" model, or that quantization destroys accuracy.  In practice, the perceptual quality difference between 4-bit and 16-bit versions of the same model is often surprisingly small for everyday language tasks; the main practical impact is speed and memory, not correctness.  The serious quality drop typically happens at 2-bit or below.  Choose quantization based on what fits in your RAM, not based on a fear of "lower quality."

---

# Part II: The Build

In this part, you will install and configure your own local AI stack (Ollama to serve models and optionally OpenWebUI for a chat interface) and verify that your Python code can talk to it over a local network connection.  Every step is hands-on: the goal by the end of class is a working system you can call from your own scripts.

## 3.  Install Checklist

Follow this sequence as a team; the Recorder logs each step's outcome, including the exact error message if a step fails.  A failed step is not a problem; it is data.  Record the error verbatim, write down your hypothesis for the cause, and test the hypothesis before asking for help.  This troubleshooting protocol is itself a course outcome.

```
1. Install Ollama:        https://ollama.com/download
2. Pull a small model:    ollama pull llama3.2
3. Sanity check (CLI):    ollama run llama3.2 "Say hello in five words."
4. Confirm the API:       curl http://localhost:11434/api/tags
5. (Optional) OpenWebUI:  docker run -d -p 3000:8080 \
     -v open-webui:/app/backend/data \
     --name open-webui ghcr.io/open-webui/open-webui:main
6. Browse to http://localhost:3000 and connect it to Ollama.
7. (If you set up OpenWebUI) Mint an API key: Settings -> Account -> API Keys.
```

---

## 3a.  When It Says "Connection Refused"

Nearly every failure in this session is one of three things, and none of them means your install is broken.  Work them in this order, because the fix for each one is different and guessing wastes the class period.

**One: you are asking the wrong machine.**  `localhost` means "the computer this program is running on."  If your Python is running on your laptop and Ollama is on your laptop, `localhost` is right and you can stop reading.  But the moment either side moves into a container, `localhost` inside that container means *the container*, where nothing is listening, and you get a connection refused that looks exactly like a dead server.

| Where your code runs | The address for Ollama |
|---|---|
| Directly on your laptop | `http://localhost:11434` |
| Inside a Docker container | `http://host.docker.internal:11434` |

**Two: Ollama is listening, but only to itself.**  By default Ollama binds to `127.0.0.1`, which accepts connections from your own machine and nothing else, so a container cannot reach it even with the right hostname.  Restart it as:

```
OLLAMA_HOST=0.0.0.0 ollama serve
```

Know what you just traded.  Any machine that can reach yours on port 11434 can now use your models.  That is fine on your own laptop; think twice on shared campus wifi, and turn it back when you are done.

**Three: on Linux, that hostname does not exist yet.**  Docker Desktop on macOS and Windows provides `host.docker.internal` automatically.  Docker Engine on Linux does not, and you have to ask for it:

```
docker run --add-host=host.docker.internal:host-gateway ...
```

> **Prove where the problem is before you change anything.**  This one command separates a network problem from a configuration problem, which is the distinction that decides which of the three fixes above you need:
>
> ```
> curl http://localhost:11434/api/tags
> ```
>
> JSON back means the server is fine and the problem is on the client side.  A refused connection means the server is not reachable from where you are asking, and you are in case one, two, or three.  Run the same `curl` from *inside* your container (`docker exec -it <name> curl ...`) and the answer usually becomes obvious.

The containerized case is worked end to end in *Terminal and Filesystem Isolation for Agent Safety*, and the agent-CLI side of it in *Agentic CLI Tools*, if you want the full version later.

## 3b.  Mint Your API Key Now

Do this today, while OpenWebUI is in front of you, because three later labs assume you already have it and none of them stops to explain where it comes from.

In OpenWebUI: **Settings -> Account -> API Keys -> Create new key.**  Copy it somewhere you will find again, and store it as an environment variable rather than pasting it into a notebook you might share:

```
export OPENWEBUI_API_KEY="sk-your-key-here"      # macOS, Linux, WSL
setx OPENWEBUI_API_KEY "sk-your-key-here"        # Windows, native shell
```

Two things to be clear about, because "API key" usually means "bill":

- **This key is yours, from your own server.**  It authenticates you to software running on your own machine.  It is not a payment credential, nothing is metered, and no request leaves your network because of it.
- **Ollama takes no key at all.**  Talking to port 11434 directly needs no authentication, which is a real difference between the two routes and one you will use later when you want the simplest possible client.

You will need this key in the *Local Agent* lab and in the OpenWebUI agent tutorials.  Having it now costs a minute; not having it costs the first fifteen minutes of a lab.

> **You've succeeded when** `curl http://localhost:11434/api/tags` returns JSON, and, if you set up OpenWebUI, `echo $OPENWEBUI_API_KEY` prints a key that starts with `sk-`.

---

The code cell below sends a single message to your locally running Ollama server using Python's `requests` library (a standard tool for making web requests).  If Ollama is running correctly, it will respond with a confirmation message.  The second block lists every model currently downloaded on your machine.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

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

1.  Which resource saturates during generation: CPU, GPU, memory (RAM), or disk?  What does that tell you about where the primary bottleneck of local inference lies on your hardware?

   > *Hint: If you have a GPU, watch GPU memory utilization.  If you do not, the model falls back to CPU. Either way, something will peg near 100%; that resource is your bottleneck.*

2.  Time a 100-word generation using Python's `time` module.  Estimate tokens per second, and compare that rate to a hosted service you have used.  What kinds of agent designs does slow generation penalize most?

   > *Hint: An agent that makes five tool calls in a loop pays the generation cost five times.  Multiply your tokens-per-second by 5 × (average tokens per step) to estimate wall-clock time for a full run.*

3.  Disconnect from the network and repeat a prompt.  Articulate precisely what data left your machine during the offline run.  Why does the answer to this question matter for the FERPA and IRB scenarios in Section 1?

   > *Hint: With the network disconnected, the only data path is between your CPU/GPU and RAM. Nothing leaves the machine.  Compare that to what would happen with a cloud API call.*

4.  Pull a second model of a different size (for example, `ollama pull llama3.2:1b`) and pose the same reasoning question to both.  The Recorder captures both full outputs for the class comparison.

   > *Hint: Choose a question that requires multi-step reasoning, such as a simple math word problem or a question about cause and effect.  Single-word-answer questions will not reveal quality differences between model sizes.*

---

## 3c.  Turn the Dial: Temperature in Your Own Chatbot

You have just run a model that is *yours*.  That means the settings that shape its answers are yours too, and the most consequential one is **temperature**.

Here is the whole idea in one sentence: at each step the model produces a ranked list of candidate next words, and temperature decides whether it always takes the top one or sometimes reaches further down the list.  **Near 0 it always takes the top candidate**, so the same prompt gives you very nearly the same answer every time.  **Near 1 it reaches down**, so the wording varies from run to run.  Nothing about the model changes; only how its output is picked.

You will meet the mathematics of that pick in *Why Different Answers Every Time?  Sampling, Temperature, and Generation*.  Today you just need to find the dial and feel what it does.

### Where the dial lives

You already have three places to set it, and they are all the same setting:

| Where | How to set it |
|-------|---------------|
| **OpenWebUI**, per conversation | Open a chat, click the **controls** icon at the top right, expand **Advanced Params**, and drag **Temperature**. It applies to that chat from that point on. |
| **OpenWebUI**, per model | **Workspace &rarr; Models &rarr;** (your model) **&rarr; Advanced Params**. This becomes the default for every new chat with that model, which is how you build a "always answers the same way" assistant. |
| **The Ollama CLI** | Inside an `ollama run llama3.2` session, type `/set parameter temperature 0` and press Enter, then keep chatting. |
| **Your Python code** | The `"options": {"temperature": ...}` block you already sent in the code cell above. |

That last row is the point worth pausing on: the `temperature=0.7` your Python helper has been passing all along, and the slider in the OpenWebUI sidebar, are the *same knob*.  The chatbot is not a different kind of thing from your script; it is a friendlier front end onto the identical API call.

### Do this now (about ten minutes)

1.  Pick one prompt with room to vary. `"Write two sentences of advice for a first-year college student."` works well.  A prompt with one right answer (`"What is 7 times 8?"`) will not show you anything.
2.  Set temperature to **0**.  Send your prompt **three times**, starting a fresh chat each time so nothing carries over.  The Recorder pastes all three answers into the team log.
3.  Set temperature to **1**.  Send the same prompt **three more times**, fresh chat each time.  Log those too.
4.  Now compare the two sets of three, on two separate questions: *how much did the **wording** change?* and *how much did the **advice itself** change?*

> **You've succeeded when** your log shows six answers, and your team can state in one sentence what changed between the two groups and what stayed the same.

### Critical Thinking Questions

1.  At temperature 0, were your three answers identical, or merely very similar?  If they differed at all, what does that tell you about "deterministic" as a promise a system makes to you?

   > *Hint: Other things besides temperature can move: which machine served the request, how the numbers round on your hardware.  Temperature 0 buys you a great deal of repeatability, not a guarantee.*

2.  At temperature 1, did the model's **facts and recommendations** change, or only its phrasing?  Try a prompt where you can check the facts.  Which kind of change would worry you more in a system a stranger depends on?

3.  In the *Agent Loop* activity, `run_agent` pinned `temperature=0.0` while the plain `chat` helper defaulted to `0.7`.  Now that you have watched both settings behave, restate in your own words why the loop wanted the pinned one.

   > *Hint: The loop searches the model's text for the exact strings `Final Answer:` and `calc(...)`.*

4.  Suppose you are building the campus advising assistant your team keeps sketching.  Would you ship it at 0, at 1, or somewhere between?  Name the failure you are trading away, and the one you are accepting.

> **Common Misconception:** Temperature is not a "creativity" slider, and it is certainly not an "accuracy" slider.  A model at temperature 0 will state a wrong fact just as confidently as one at temperature 1; it will simply state the *same* wrong fact every time.  Turning temperature down makes a system **repeatable**, which makes it testable.  It does not make it right.

---

## 4.  Multi-Turn Conversations: Managing the Message List

The call above sends a single message and forgets it instantly.  A real conversation remembers what came before, and here is the key idea: **the Ollama server is stateless.**  It does not remember your last turn.  *You* remember, by keeping a running `messages` list and re-sending the whole thing on every call.  Each turn you append the user's message, send the full list, then append the assistant's reply back onto it.  The growing list *is* the conversation's memory.

The cell below holds a three-turn conversation.  Notice that `chat()` now takes the entire `messages` list, and that after each reply we append the assistant's message (`r.json()["message"]`) verbatim, so the next turn can see it.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

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
say("Remind me, what is my name?")         # ...yet the model still knows, from the resent history

print(f"[the message list now holds {len(messages)} entries]")
```

The last question never mentions Iceland or the name Sam, yet the model answers correctly, because the entire prior exchange rode along in the `messages` list.  Delete the `messages.append(reply)` line and the model goes amnesiac.

**The same pattern through OpenWebUI.** If you put OpenWebUI in front of Ollama, its OpenAI-compatible endpoint accepts the *identical* growing `messages` array; only the URL, an `Authorization: Bearer <key>` header, and the response path change:

> **Runs on your machine, not here.**  This cell makes network calls that the page sandbox blocks.  Copy it into your course container and run it there.

```python
# r = requests.post("http://localhost:3000/api/chat/completions",
#                   headers={"Authorization": f"Bearer {API_KEY}"},
#                   json={"model": "llama3.2", "messages": messages})
# reply = r.json()["choices"][0]["message"]   # OpenWebUI/OpenAI nests it under choices[0]
```

Everything else (append the user turn, resend the whole list, append the reply) stays the same.

## Model: The Growing Context

### Critical Thinking Questions

5.  Every turn resends the *entire* history, so a 20-turn chat re-sends turns 1-19 again on turn 20.  As the conversation grows, what happens to the number of tokens processed (and therefore the time and cost) per turn?

   > *Hint: If each turn adds roughly the same number of tokens, the total sent by turn $N$ grows like $1 + 2 + \dots + N$. Is that linear or quadratic in $N$?*

6.  Every model has a fixed **context window** (a maximum number of tokens it can read at once).  What happens when your growing `messages` list exceeds it?  Name two strategies to stay under the limit without simply deleting the earliest turns outright.

   > *Hint: You could drop old turns, or you could replace them with a short summary.  Which one preserves more of what mattered?*

7.  The server is stateless, but your Python process holds the `messages` list in memory.  If the program crashes mid-conversation, the history is gone.  What would you add to make a conversation survive a restart?

   > *Hint: Think about writing the messages list to disk (as JSON) after each turn and reloading it on startup.*

> **Common Misconception:** It is tempting to think the model "remembers" your conversation the way a person does.  It does not.  Between calls the server keeps *nothing*; the illusion of memory comes entirely from your client resending the full `messages` list each time.  When the list grows too long for the context window, that memory silently starts to fall off the front, exactly the problem the *Memory and the Small Context Window* activity later solves with summarization.

---

# Part III: Synthesis and Practice

In this part, you will probe your local model across five different task types to build a concrete capability map, a table showing where it succeeds and where it fails.  This map will serve as your baseline for the rest of the semester as you add tools, retrieval, and multi-agent techniques.

## 5.  Exercises

1.  *Capability map.*

   - *What to do*: As a team, test your local model on five task types: (a) summarize a paragraph, (b) extract key facts into JSON, (c) solve an arithmetic word problem, (d) answer a question about a recent event (post-training-cutoff), and (e) write a short creative passage.  Build a table of pass / partial / fail with one sentence of evidence for each cell.
   - *Starter hint*: For the recent-event question, choose something that happened in 2025 or 2026.  For extraction, give the model a paragraph and ask for `{"name": ..., "date": ..., "location": ...}`; check whether the JSON is valid.
   - *You've succeeded when*: Your table has five rows, a clear pass/partial/fail verdict for each, and you can identify which failure type (knowledge cutoff, format compliance, reasoning) explains each failing cell.

2.  *Quantization estimate.*

   - *What to do*: Using the formula from Section 2, compute the approximate weight-only storage size for models with 1B, 8B, and 70B parameters at both 4-bit and 16-bit quantization.  Mark which fit in your laptop's RAM.
   - *Starter hint*: Plug into $\text{size} = N \times \frac{\text{bits}}{8}$ bytes, then convert to GB by dividing by $10^9$. For example, 1B parameters at 4-bit: $1 \times 10^9 \times 0.5 = 0.5$ GB.
   - *You've succeeded when*: You have a 3-by-2 table (three model sizes by two quantization levels) with sizes in GB and a checkmark or cross next to each based on your laptop's actual RAM.

3.  *Stack diagram.*

   - *What to do*: Draw a box-and-arrow diagram showing the full data flow from OpenWebUI to Ollama to the model weights and back, plus your Python script as a separate entry point.  Label which component owns the system prompt, the sampling parameters (the temperature you turned in Section 3b, plus its sibling `top-p`), and the model weights.
   - *Starter hint*: Your diagram should have at least four boxes: OpenWebUI (or your Python script), the Ollama process, the model weights file on disk, and the GPU or CPU memory where inference actually runs.  Arrows should show the direction of data flow for both the input prompt and the output response.
   - *You've succeeded when*: Someone who was not in class today could read your diagram and correctly answer: "Where does the system prompt live?  Where do the weights live?  What does Ollama actually do?"

---

## Reflection Prompt

*Personal*: You now own a working AI stack that costs nothing per query and shares nothing with anyone outside your machine.  Did anything about the installation process surprise you, was it harder or easier than expected?  What mental model did you have before about "where AI lives," and how has that changed?

*Technical*: You now have a tool that can run privately on your laptop.  Identify one project (academic, personal, or professional) that becomes newly possible for you because privacy and cost are no longer barriers.  Describe what you would build and what the remaining obstacle is.

*Societal*: Local AI puts the full capability of a language model in the hands of any individual with a modern laptop, with no oversight, no logging, and no terms of service enforcement.  What are two benefits and two risks of that shift in power from institutions to individuals?  Who benefits most from local AI, and who might be harmed?

---

-> Coming Up Next: Your model is running and you have turned your first dial on it.  Next, in *Prompt Engineering as Agent Design*, we work on the other half of the control surface: the words.  Bring this stack, because that session edits system prompts against a live model and the temperature slider from Section 3b is one of the things we vary.  (*Why* that dial behaves the way it does gets its full treatment in *Why Different Answers Every Time?  Sampling, Temperature, and Generation*.)

## 6.  Further Reading

- Ollama documentation: https://ollama.com and https://github.com/ollama/ollama/blob/main/docs/api.md (see the `/api/chat` `messages` array for multi-turn conversations)
- OpenWebUI documentation: https://docs.openwebui.com
- Melanie Mitchell.  *AI: A Guide for Thinking Humans*, Chapter 3.
