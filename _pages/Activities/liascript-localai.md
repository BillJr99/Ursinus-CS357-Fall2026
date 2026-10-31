<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-localai.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-localai.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Running Your Own AI: Ollama, OpenWebUI, and Private Local Models

Every model you have talked to so far, in this course or anywhere else, has run on someone else's server.  Today that stops.  Today every team stands up a complete, private AI stack on its own hardware: **Ollama** to serve models, **OpenWebUI** for a chat interface, and the **REST API** that our agents will call for the rest of the semester.  We move from **why local → installation → model selection and quantization → talking to the API from Python**.

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
| Conversation history file | A file, here `history.json`, where your program saves the message list after every turn and reads it back at startup.  It is the only memory a local chatbot has | Deleting `history.json` in Step 2 and watching the model forget your name |
| Permission gate | A check in your code, on the only path that runs a command, that a model's reply cannot skip | The `Type YES to allow it` prompt in Step 5 |

---

## Today's Plan

Anything marked self-paced is for outside class, and nothing graded assumes it.

1. Part I, why local at all: the four reasons, and which one is yours
2. Section 3 and 3a: the install checklist and the `curl` probe, so every team has a model answering
3. Part IIb, the five steps: prompt, remember, iterate, skill, command
4. Section 3c, the temperature dial
5. Reflection prompt, and what to post before next session

Sections 3b (the OpenWebUI API key), 3d (pointing opencode at Ollama), and the two-model comparison are self-paced.  Do them before the Local Agent lab needs them.  Section 4 is the idea behind Steps 2 and 3, so read it if Step 2 surprises you.

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

Do this today, while OpenWebUI is in front of you, because the later labs assume you already have it and none of them stops to explain where it comes from.

In OpenWebUI: **Settings -> Account -> API Keys -> Create new key.**  Copy it somewhere you will find again, and store it as an environment variable rather than pasting it into a notebook you might share:

```
export OPENWEBUI_API_KEY="sk-your-key-here"      # macOS, Linux, WSL
setx OPENWEBUI_API_KEY "sk-your-key-here"        # Windows, native shell
```

Two things to be clear about, because "API key" usually means "bill":

- **This key is yours, from your own server.**  It authenticates you to software running on your own machine.  It is not a payment credential, nothing is metered, and no request leaves your network because of it.
- **Ollama takes no key at all.**  Talking to port 11434 directly needs no authentication, which is a real difference between the two routes and one you will use later when you want the simplest possible client.

You will need this key in the *Local Agent* lab and in the OpenWebUI agent tutorials.  Having it now costs a minute; not having it costs the first fifteen minutes of a lab.

> **You've succeeded when** `curl http://localhost:11434/api/tags` returns JSON, and, if you set up OpenWebUI, `[ -n "$OPENWEBUI_API_KEY" ] && echo set` prints `set`.  Check a key that way rather than echoing it: a key you print is a key in your scrollback, your shell history, and any screenshot you paste into the course channel.

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

You will meet the mathematics of that pick in the *Why Different Answers Every Time?  Sampling, Temperature, and Generation* tutorial (https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/SamplingAndTemperature).  Today you just need to find the dial and feel what it does.

### Where the dial lives

You already have three places to set it, and they are all the same setting:

| Where | How to set it |
|-------|---------------|
| **OpenWebUI**, per conversation | Open a chat, click the **controls** icon at the top right, expand **Advanced Params**, and drag **Temperature**. It applies to that chat from that point on. |
| **OpenWebUI**, per model | **Workspace &rarr; Models &rarr;** (your model) **&rarr; Advanced Params**. This becomes the default for every new chat with that model, which is how you build an "always answers the same way" assistant. |
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

## 3d.  Point opencode at Your Local Model

You installed opencode in *Your AI Workbench* and pointed it at a model there.  Now that you have built the server yourself, it is worth seeing the wiring from this side, because the same three lines are how you will add every other model you pull.

opencode reads one file, `opencode.json`, from either of two places.  A copy at a repository root configures that project; a copy in your home directory configures every project you open.  The two are merged rather than one replacing the other, so you can add a provider in one place without restating anything in the other.

| System | Project | Global |
|---|---|---|
| macOS, Linux, WSL2 Ubuntu | `opencode.json` at the repository root | `~/.config/opencode/opencode.json` |
| Windows | `opencode.json` at the repository root | `%USERPROFILE%\.config\opencode\opencode.json` |

The block that registers the server you just started:

```json
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "llama3.2": { "name": "llama3.2 (local)" }
      }
    }
  }
}
```

Three things to notice, because they answer the three questions this block always raises.  `npm` names the adapter that speaks the endpoint's dialect, and Ollama serves an OpenAI-compatible API, which is why the generic adapter works.  `baseURL` is `localhost` when opencode runs on this machine and `http://host.docker.internal:11434/v1` when it runs inside the course container, for the reason you met in the Docker session.  And there is **no API key**, because Ollama takes none; this is the same point Section 3b makes from the other direction.

A provider key and a model key join with a slash, so the block above defines `ollama/llama3.2`, which is the identifier `/models` lists and `--model` accepts.

Adding a provider is a file edit in every case.  The desktop application and the TUI both read this file, and neither offers a form for adding one: the TUI's `/models` selects among providers already defined, and `/connect` stores a credential for a service that needs one, which Ollama does not.  Restart opencode after editing, then type `/models` and look for your provider.

The full walkthrough, with every platform and the rest of the file, is End-to-End OpenCode Setup at https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OpenCodeSetup, which is today's reading for the lab being handed out.

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

   > *Hint: Think about writing the messages list to disk (as JSON) after each turn and reloading it on startup.*  *Step 2 in Part IIb builds exactly this.*

> **Common Misconception:** It is tempting to think the model "remembers" your conversation the way a person does.  It does not.  Between calls the server keeps *nothing*; the illusion of memory comes entirely from your client resending the full `messages` list each time.  When the list grows too long for the context window, that memory silently starts to fall off the front, exactly the problem the *Memory and the Small Context Window* activity later solves with summarization.

---

# Part IIb: Build It in Five Small Steps

In this part, you will write the program that runs a model, one small piece at a time.  Each step is its own file.  Each file runs by itself, adds exactly one idea to the file before it, and marks the new lines with `# NEW`.  Run each file and see it work before you open the next one.

| Step | File | The one new idea | What it looks like in opencode |
|---|---|---|---|
| 1 | `step1_prompt.py` | Send a prompt from code and read the reply | Typing a message in the TUI |
| 2 | `step2_remember.py` | Save the conversation to a file, so it survives a restart | `.ai/MEMORY.md` in the `instructions` list |
| 3 | `step3_iterate.py` | Loop: read, send, save, repeat | The chat session itself |
| 4 | `step4_skill.py` | Read a `SKILL.md` and put its rules in the system prompt | `.agents/skills/` |
| 5 | `step5_command.py` | Let the model ask for a command, and ask the person before it runs | `"bash": {"*": "ask"}` in `opencode.json` |

By the end, you will have written the core of every coding agent you have used this term.  opencode does each of these five things; now you will know how, because you did it yourself.

> **Setup, once.**  Make a folder for today, `cd` into it, and check that Ollama answers: `curl http://localhost:11434/api/tags`.  If that prints JSON, you are ready.  If it prints "connection refused," go back to Section 3a before you write any code.

---

## 4a.  Step 1: Prompt

Every agent starts with one function: send messages, get a message back.  We write `chat()` once, here, and it never changes again.  Every later step reuses it exactly.

Notice that `chat()` takes a *list* of messages, not a single string.  That choice costs nothing now and pays off in Step 2.  The server address comes from the `OLLAMA_URL` environment variable, so the same file works on your laptop and inside a container.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into a file in your course folder and run it there.  If you run it inside a container, first run `export OLLAMA_URL=http://host.docker.internal:11434` (Section 3a explains why).

```python
import os, requests

# In a container, set OLLAMA_URL=http://host.docker.internal:11434 (Section 3a explains why)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

def chat(messages, temperature=0.7):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]        # {"role": "assistant", "content": "..."}
    except Exception as e:
        print(f"[step1:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

reply = chat([{"role": "user", "content": "In one sentence, what is a local model?"}])
print(reply["content"])
```

Run it with `python step1_prompt.py`.

- *You've succeeded when*: one sentence prints.  If you see `[step1:chat]` and a connection error, the server is not where the code looked; the probe in Section 3a tells you which of the three causes it is.

---

## 4b.  Step 2: Remember, by Saving a File

Section 4 showed that the server remembers nothing.  Your `messages` list is the memory.  But that list lives in your program, and when the program exits, the memory is gone.  The fix is ordinary file I/O: write the list to `history.json` after each turn, and read it back when the program starts.

This file takes its message from the command line, so you can run it twice and watch the second run remember the first.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into a file in your course folder and run it there.  If you run it inside a container, first run `export OLLAMA_URL=http://host.docker.internal:11434` (Section 3a explains why).

```python
import os, sys, json, requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
HISTORY = "history.json"                                   # NEW: the memory lives here

def chat(messages, temperature=0.7):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]
    except Exception as e:
        print(f"[step2:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

def load_history():                                        # NEW
    try:
        with open(HISTORY, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role": "system", "content": "You are a concise assistant."}]

def save_history(messages):                                # NEW
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

messages = load_history()
messages.append({"role": "user", "content": " ".join(sys.argv[1:]) or "Hello!"})
reply = chat(messages)
messages.append(reply)
save_history(messages)                                     # NEW: write it down before we exit
print(reply["content"])
print(f"[{HISTORY} now holds {len(messages)} messages]")
```

Run it three times:

```bash
python step2_remember.py "My name is Sam.  Please remember it."
python step2_remember.py "What is my name?  One word."
rm history.json          # Windows PowerShell: Remove-Item history.json
python step2_remember.py "What is my name?  One word."
```

Open `history.json` in your editor between runs.  That file is the model's entire memory of you, and you can read it, edit it, or delete it.

- *You've succeeded when*: the second run answers "Sam," and the run after the `rm` does not know your name.

> **Common Misconception:** "The model remembered me."  It did not.  Your program read a file and sent its contents back.  Delete the file and the "memory" is gone, because it was never in the model.  This is the same mechanism as the `.ai/MEMORY.md` file you listed in `opencode.json` for the OpenCode Studio lab: the harness reads a file and sends it along.

---

## 4c.  Step 3: Iterate with a Loop

Running the program once per message is clumsy.  A loop does the same four moves over and over: read a line, append it, send the whole list, append and save the reply.  That loop is the chat window of every chatbot you have used.

We also add two commands of our own.  `/forget` deletes the memory file, and `/quit` exits.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into a file in your course folder and run it there.  If you run it inside a container, first run `export OLLAMA_URL=http://host.docker.internal:11434` (Section 3a explains why).

```python
import os, json, requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
HISTORY = "history.json"

def chat(messages, temperature=0.7):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]
    except Exception as e:
        print(f"[step3:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

def load_history():
    try:
        with open(HISTORY, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role": "system", "content": "You are a concise assistant."}]

def save_history(messages):
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

messages = load_history()
print("Type a message.  /forget erases the memory file, /quit exits.")
while True:                                                # NEW: the loop
    user_text = input("you> ").strip()
    if user_text == "/quit":
        break
    if user_text == "/forget":
        if os.path.exists(HISTORY):
            os.remove(HISTORY)
        messages = load_history()
        print("[memory erased]")
        continue
    messages.append({"role": "user", "content": user_text})
    reply = chat(messages)
    messages.append(reply)                                 # delete this line to see amnesia
    save_history(messages)
    print("model>", reply["content"])
```

Try this conversation: tell it your favorite color, ask it back, type `/forget`, and ask again.  Then comment out the line marked `delete this line to see amnesia`, restart, and hold a three-turn conversation.

- *You've succeeded when*: the model recalls your color before `/forget` and cannot after it.  With the marked line removed, the model loses track even inside one session, because its own replies never reach the next request.

> **Watch out.**  A small model can miss a fact that is plainly in its history.  In our testing, a 0.5-billion-parameter model answered "What is my favorite color?" with a lecture about colors, one line after being told the answer.  That is a capability limit, not a bug in your loop.  Check `history.json`: if the fact is in the file, your code did its job.

---

## 4d.  Step 4: Use a Skill

A skill is a Markdown file of instructions.  In Step 4 we write one, read it from disk, strip its front matter, and put its body into the system prompt.  This is Route 3 from the *Skills* session: a skill turned into a string.

First, create the skill.  This one has rules you can see in every reply, so you can tell at a glance whether it loaded.

```bash
mkdir -p .agents/skills/terse-helper
cat > .agents/skills/terse-helper/SKILL.md <<'EOF'
---
name: terse-helper
description: Answer in at most two sentences, and end every answer with a "Next step:" line.
---
# Terse Helper

1.  Answer in at most two sentences.
2.  End every answer with one line that starts with "Next step:".
3.  If you do not know, say "I don't know" rather than guessing.
EOF
ls .agents/skills/terse-helper/SKILL.md
```

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into a file in your course folder and run it there.  If you run it inside a container, first run `export OLLAMA_URL=http://host.docker.internal:11434` (Section 3a explains why).

```python
import os, json, requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
HISTORY = "history.json"
SKILL = os.path.join(".agents", "skills", "terse-helper", "SKILL.md")   # NEW

def chat(messages, temperature=0.7):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]
    except Exception as e:
        print(f"[step4:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

def strip_front_matter(text):                              # NEW: same helper as the Persona Pipeline
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text.strip()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:]).strip()
    return text.strip()

def load_skill(path):                                      # NEW: a skill is a file we read
    try:
        with open(path, encoding="utf-8") as f:
            return strip_front_matter(f.read())
    except FileNotFoundError as e:
        print(f"[step4:load_skill] no skill at {path}: {e}")
        return ""

def load_history():
    try:
        with open(HISTORY, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role": "system", "content": ""}]

def save_history(messages):
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

messages = load_history()
system = "You are a concise assistant."
skill = load_skill(SKILL)
if skill:
    system += "\n\nFollow these rules exactly:\n\n" + skill  # NEW: the skill joins the system prompt
messages[0] = {"role": "system", "content": system}        # re-read on every start
print(f"[skill loaded: {bool(skill)}]  /quit exits.")
while True:
    user_text = input("you> ").strip()
    if user_text == "/quit":
        break
    messages.append({"role": "user", "content": user_text})
    reply = chat(messages)
    messages.append(reply)
    save_history(messages)
    print("model>", reply["content"])
```

The `strip_front_matter` helper is the same one the Persona Pipeline uses.  Note that the program rebuilds the system prompt on every start, so an edit to `SKILL.md` takes effect the next time you run it, even with an old `history.json`.

- *You've succeeded when*: the program prints `[skill loaded: True]`, and every answer is short and ends with a `Next step:` line.  Rename the skill folder, restart, and watch the `Next step:` line disappear.

> **Common Misconception:** "The skill decides when it applies."  Not here.  In opencode, the `description` is the trigger, and the body loads only when a request matches it.  Our program pastes the body into the system prompt, so it applies to every turn.  We turned a skill into a system prompt.  That is the trade the *Skills* session named: the instructions are always present, and they are never selective.

---

## 4e.  Step 5: Execute a Command, With Permission

Until now, the model could only talk.  In Step 5 it can act.  We give it a protocol, "reply `RUN: <command>` to run a command," and our code watches for that line.  When it appears, the code shows the command to the person and runs it only if they type `YES`.  The command's output goes back to the model as an Observation, and the model answers with what it saw.

Two lines in `run_command` carry the safety.  `shlex.split` turns the string into a list of arguments, and `subprocess.run` gets that list with no shell.  There is no shell to interpret `|`, `;`, `&&`, or `>`, so a model cannot chain a second command onto the first.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into a file in your course folder and run it there.  If you run it inside a container, first run `export OLLAMA_URL=http://host.docker.internal:11434` (Section 3a explains why).

```python
import os, re, json, shlex, subprocess, requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
HISTORY = "history.json"
SKILL = os.path.join(".agents", "skills", "terse-helper", "SKILL.md")
TOOL_RULE = ("You can ask to run one shell command.  To do that, reply with exactly one line: "
             "RUN: <command>.  You will then receive its output as an Observation.  "
             "Otherwise, answer normally.")                # NEW: tell the model the protocol

def chat(messages, temperature=0.7):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json={
            "model": MODEL, "stream": False,
            "options": {"temperature": temperature},
            "messages": messages}, timeout=120)
        r.raise_for_status()
        return r.json()["message"]
    except Exception as e:
        print(f"[step5:chat] {e}")
        import traceback; traceback.print_exc()
        return {"role": "assistant", "content": ""}

def strip_front_matter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text.strip()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:]).strip()
    return text.strip()

def load_skill(path):
    try:
        with open(path, encoding="utf-8") as f:
            return strip_front_matter(f.read())
    except FileNotFoundError as e:
        print(f"[step5:load_skill] no skill at {path}: {e}")
        return ""

def load_history():
    try:
        with open(HISTORY, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role": "system", "content": ""}]

def save_history(messages):
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

def run_command(cmd):                                      # NEW: the one place a command runs
    try:
        done = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=20)
        return f"exit code {done.returncode}\n{done.stdout}{done.stderr}"[:2000]
    except Exception as e:
        print(f"[step5:run_command] {e}")
        import traceback; traceback.print_exc()
        return f"the command failed to start: {e}"

messages = load_history()
system = "You are a concise assistant.\n\n" + TOOL_RULE
skill = load_skill(SKILL)
if skill:
    system += "\n\nFollow these rules exactly:\n\n" + skill
messages[0] = {"role": "system", "content": system}
print(f"[skill loaded: {bool(skill)}]  /quit exits.")
while True:
    user_text = input("you> ").strip()
    if user_text == "/quit":
        break
    messages.append({"role": "user", "content": user_text})
    reply = chat(messages)
    messages.append(reply)
    match = re.search(r"^\s*RUN:\s*(.+)$", reply["content"], re.MULTILINE)
    if match:                                              # NEW: the permission gate
        cmd = match.group(1).strip().strip("`")
        print(f"[the model wants to run]  {cmd}")
        if input("Type YES to allow it: ").strip() == "YES":
            observation = run_command(cmd)
        else:
            observation = "The user declined to run that command."
        print(f"[observation]  {observation}")
        messages.append({"role": "user", "content": f"Observation: {observation}"})
        reply = chat(messages)                             # let the model use what it saw
        messages.append(reply)
    save_history(messages)
    print("model>", reply["content"])
```

Run it twice:

1.  Ask "How many Python files are in this folder?  Use a command."  Read the proposed command before you type `YES`.
2.  Ask "What is in this folder?  Use a command."  This time, type `no`.

When we tested this with `llama3.2`, the model's first proposal was `ls | grep python`.  With no shell, `ls` received `|`, `grep`, and `python` as file names and failed.  The model read the error and explained it.  That failure is the design working: the pipe was never interpreted.

- *You've succeeded when*: an approved command runs and its output appears as `[observation]`, and a declined command never runs, and the model is told so.

> **Common Misconception:** "I told the model to ask before running anything, so it will."  An instruction in the prompt is a request.  The `input("Type YES...")` line is a gate: it sits in the only code path that can run a command, so the model cannot talk its way past it.  This is the same distinction as the permission block in `opencode.json`.  The rule lives in the prompt, and the gate lives in the tool path.

> **Windows note.**  `dir` and `type` are built into the Windows shell and are not programs, so with no shell they fail to start.  Run this step in your course container or WSL, or ask for commands that are real programs, such as `python --version`.

---

## Model: Five Steps, One Agent

### Critical Thinking Questions

8.  Step 1's `chat()` never changed in Steps 2 through 5.  What did change in each step?  Name the one data structure every step reads or writes.

   > *Hint: Look at what flows into `chat()` each time.*

9.  In Step 2, you deleted `history.json` and the model forgot your name.  Where, exactly, did the model's "memory" live, and who controls it?  What does that tell you about a hosted chatbot that "remembers" you?

   > *Hint: Somebody's program is saving a file like yours.  Whose disk is it on?*

10. The Step 4 skill loads on every turn.  Describe a request where that hurts, and say what opencode does differently.

   > *Hint: Ask the terse helper to write a 500-word essay.*

11. In Step 5, find the one line that makes the permission gate a gate rather than a request.  What would change if you deleted it and added "Always ask the user before running a command" to `TOOL_RULE` instead?

   > *Hint: Who reads `TOOL_RULE`, and who runs the `if`?*

12. `run_command` uses `shlex.split` with no shell.  Give one command a model could propose that is dangerous even without a pipe or a semicolon.  What second gate would stop it without asking the person every time?

   > *Hint: `rm -rf ~` needs no shell.  Compare an allowlist of programs with a prompt that says "be careful."  The tutorial below builds the allowlist.*

> **Put it together.**  The tutorial *Building a Local Agent From Scratch* composes all five steps into one program, `tiny_agent.py`, with its settings in `config.json`, an allowlist in front of the `YES` prompt, and a limit on commands per turn: https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/LocalAgentFromScratch.  Part 0 of the Local Agent lab asks you to hand in your five step files.

---

# Part III: Synthesis and Practice

In this part, you will probe your local model across five different task types to build a concrete capability map, a table showing where it succeeds and where it fails.  This map is your baseline for the rest of the semester as you add tools, retrieval, and multi-agent techniques.

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

   - *What to do*: Draw a box-and-arrow diagram showing the full data flow from OpenWebUI to Ollama to the model weights and back, plus your Python script as a separate entry point.  Label which component owns the system prompt, the sampling parameters (the temperature you turned in Section 3c, plus its sibling `top-p`), and the model weights.
   - *Starter hint*: Your diagram should have at least four boxes: OpenWebUI (or your Python script), the Ollama process, the model weights file on disk, and the GPU or CPU memory where inference actually runs.  Arrows should show the direction of data flow for both the input prompt and the output response.
   - *You've succeeded when*: Someone who was not in class today could read your diagram and correctly answer: "Where does the system prompt live?  Where do the weights live?  What does Ollama actually do?"

---

## Reflection Prompt

*Personal*: You now own a working AI stack that costs nothing per query and shares nothing with anyone outside your machine.  Did anything about the installation process surprise you?  Was it harder or easier than expected?  What mental model did you have before about "where AI lives," and how has that changed?

*Technical*: You now have a tool that can run privately on your laptop.  Identify one project (academic, personal, or professional) that becomes newly possible for you because privacy and cost are no longer barriers.  Describe what you would build and what the remaining obstacle is.

*Societal*: Local AI puts the full capability of a language model in the hands of any individual with a modern laptop, with no oversight, no logging, and no terms of service enforcement.  What are two benefits and two risks of that shift in power from institutions to individuals?  Who benefits most from local AI, and who might be harmed?

---

-> Coming Up Next: Your model is running and you have turned your first dial on it.  In *Skills: Design One, Then Measure It*, you work on the instructions the agent reads before it produces anything, and measure whether they changed the output.  Keep this stack running, because the OpenCode Studio lab handed out today drives opencode against the model you just stood up, and *Prompt Engineering as Agent Design* edits system prompts against this same live model, where the temperature slider from Section 3c is one of the things we vary.  (*Why* that dial behaves the way it does gets its full treatment in *Why Different Answers Every Time?  Sampling, Temperature, and Generation*.)

## 6.  Further Reading

- [The Local Model Landscape: Llama, Mistral, Phi, Gemma, and their relatives, for deciding what to pull next](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/LocalModels)
- [The Hardware Behind AI: GPUs, quantization, and running models at the edge, which explains the inference speeds you see today](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Hardware)
- [End-to-End OpenCode Setup: install, opencode.json at both scopes, providers and authentication, AGENTS.md, permissions, a skill, a plugin, and GitHub by CLI and MCP, on every platform.  The reference for today's lab handout](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/OpenCodeSetup)
- [Building a Local Agent From Scratch: Prompt, Remember, Iterate, Skill, Command](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/LocalAgentFromScratch)
- Ollama documentation: https://ollama.com and https://github.com/ollama/ollama/blob/main/docs/api.md (see the `/api/chat` `messages` array for multi-turn conversations)
- OpenWebUI documentation: https://docs.openwebui.com
- Melanie Mitchell.  *AI: A Guide for Thinking Humans*, Chapter 3.
- Building a Local Agent From Scratch: Prompt, Remember, Iterate, Skill, Command, the five steps of Part IIb composed into one program: https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/LocalAgentFromScratch
- Python `subprocess` documentation, on why a list of arguments with no shell is the safe default: https://docs.python.org/3/library/subprocess.html#security-considerations

---

# Extension: Putting the Agent in a Box (self-paced)

Optional, and nothing above assumes it.  You now have a model running privately on your own machine.  The obvious next step is to let something *use* it without supervision, and that is where the question changes from "can it?" to "what is it allowed to touch?"

## The idea, in plain language

A coding agent is a program that reads your files, writes new ones, and runs commands, all on its own judgment.  That is useful, and it is also a strange thing to hand a stranger.  The usual answer is to watch it closely and approve each step, which works until you get tired.

The better answer is to change what is reachable rather than to watch harder.  You put the agent in a container, which is a boxed-off copy of an operating system, and you decide in advance exactly two things:

1.  **Which folder it can see.**  One project directory, and nothing above it.  Not your home folder, not your SSH keys, not your other courses.  Files that were never handed to the box do not exist as far as the agent is concerned.
2.  **Which model it can talk to.**  Ollama, running on your laptop, on the other side of a single address.  No API key, no account, no request leaving your machine.

Then the interesting question stops being "do I trust this agent?" and becomes "what is the worst thing that can happen inside this box?"  That is a question with an actual answer, and you chose it yourself.

> **Why this is different from just being careful.**  Care is a thing you have to keep supplying.  A boundary is a thing you set once, and it holds while you are tired, distracted, or asleep.  The agent cannot read a file you did not mount, no matter how convincingly something in its input asks it to.

## What it looks like to run

Two commands, once the model is running.  The first builds the box, the second opens the agent inside it:

```bash
docker build -t course-pi-ollama .
docker run --rm -it --user "$(id -u):$(id -g)" \
  --add-host=host.docker.internal:host-gateway \
  -v "$PWD:/workspace" -w /workspace \
  -e PI_OLLAMA_MODEL=llama3.2 course-pi-ollama
```

Or ask opencode to do it, from the folder holding the Dockerfile:

```text
Build the image in this folder as course-pi-ollama, then run it with --rm, my own
uid and gid, host.docker.internal mapped to the host gateway, this folder mounted
at /workspace as the working directory, and PI_OLLAMA_MODEL set to llama3.2.  Show
me the command before you run it.
```

Ask for the command before the run.  A container invocation is mostly flags, and the flags are the whole lesson here.

`--rm` is the part worth noticing.  It throws the container away when you exit.  The work stays, because the work is in your project folder; the machine it ran on is disposable.  If the agent makes a mess of its own environment, the mess is gone the next time you start.

## One thing that will trip you up

Your model is not where the agent expects.  Inside a container, `localhost` means *the container*, not your laptop, so an agent that dials `localhost:11434` is calling a phone number in the wrong building.  Section 3a of this deck already showed you the connection-refused version of this problem; the containerized version has the same cause and the same fix.  Ollama also has to be started in a way that accepts the call at all:

```bash
OLLAMA_CONTEXT_LENGTH=8192 OLLAMA_HOST=0.0.0.0 ollama serve
```

Or ask opencode to do it:

```text
Restart Ollama so it listens on all interfaces and serves an 8192-token context:
OLLAMA_HOST=0.0.0.0 and OLLAMA_CONTEXT_LENGTH=8192.  Tell me first whether an
ollama process is already running, because the old one has to stop first.
```

The second setting is the familiar one from Section 3a.  The first is new, and it is the one that will stop you cold: the agent setup below refuses to start if the model has less than 8192 tokens of working memory, and Ollama hands out 4096 by default.  That refusal is deliberate, and the reason is worth reading.

## The other thing it insists on

The setup also will not start without an instruction file called a *skill* sitting in your project, which the next class session is about.  Download it and unzip it into `.agents/skills/` at the top of whatever project you point the agent at.  That is the same directory next session uses for the skills you write yourself, and both tools read it, so you only ever learn one path:

```bash
mkdir -p .agents/skills
curl -fsSL -o smo.skill https://www.billmongan.com/Ursinus-CS357-Fall2026/files/small-model-orchestrator.skill
unzip -q smo.skill -d .agents/skills/ && rm smo.skill
ls .agents/skills/small-model-orchestrator/SKILL.md
```

Or ask opencode to do it:

```text
Create a .agents/skills folder here, download
https://www.billmongan.com/Ursinus-CS357-Fall2026/files/small-model-orchestrator.skill,
unzip it into .agents/skills, delete the archive, and then confirm that
.agents/skills/small-model-orchestrator/SKILL.md exists.  Tell me the exact path you find.
```

Make it report the path rather than say it succeeded, for the reason the next paragraph gives.

That last line is the check that matters.  You are looking for `SKILL.md` exactly one folder deep, at `.agents/skills/small-model-orchestrator/SKILL.md`.  Some unzip tools add an extra folder named after the archive, and if yours did, move the inner folder up one level.  On Windows, download it as `smo.zip` and use `Expand-Archive -Path smo.zip -DestinationPath .agents\skills`, because `Expand-Archive` refuses any other extension.

## Where to go next

The full build, every flag explained, both the Windows and the macOS/Linux commands, and the honest accounting of what running as root costs you:

- [One Script Instead of an Image, and What That Convenience Costs](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/FilesystemIsolation#one-script-instead-of-an-image-and-what-that-convenience-costs)

The files, ready to download:

- [run-pi-ollama.sh](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/pi-ollama/run-pi-ollama.sh), for macOS, Linux, and WSL
- [run-pi-ollama.ps1](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/pi-ollama/run-pi-ollama.ps1), for Windows PowerShell
- [Dockerfile](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/pi-ollama/Dockerfile), the version that never runs as root
- [README.md](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/pi-ollama/README.md), the quickstart with a troubleshooting table
