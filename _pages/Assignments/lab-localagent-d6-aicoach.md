---
layout: assignment
permalink: /Assignments/LocalAgent/Direction6
title: "CS357 Lab: Local Agent, Direction 6: Build Your Own AI Coach"
---

> **Grading:** This page is one of the directions for the [Local Agent Lab](/Assignments/LocalAgent). It carries no separate point value and no rubric of its own — your combined core + direction work is graded with the Local Agent Lab rubric on the core lab page.

> **What this direction requires**
>
> - **Accounts:** none required on the recommended path — a local OpenAI-compatible server (Ollama or Open WebUI) needs no key.
> - **API costs:** none on the local path. A cloud provider key is optional, never required — and must never be committed to your repository.
> - **Installs / disk:** nothing beyond the core lab for a Python app (`requests`); a single-file browser app needs no installs at all.
> - **Hardware:** any machine that runs the core lab.
> - **No-cost fallback:** built in — Part 2 recommends the keyless local-server route as the starting point.

---


Take the single language-model call at the heart of the core lab and build a real application around it. You will construct an AI coach whose interactive core works entirely on its own logic and then layers a language model on top for commentary and structured output — routed through one provider-agnostic function, parsed defensively, with the API key never exposed to the client. The domain is up to you; the architecture is the point.

You have seen a language model wired into a real, working program: the [Chess AI Coach](/files/apps/chess-ai-coach.html). It plays a full game with pure local logic and then *layers* a language model on top for commentary, an evaluation number, and an Elo estimate — routed through one provider-agnostic function, parsed defensively, with the API key never leaving the user's browser.

Now you build your own. The domain is up to you; the **architecture** is the point. You will reuse the exact pattern from the tutorial: a working interactive core, a single dispatch function that talks to a language model, at least one structured-JSON feature, and airtight key handling.

---

#### Overview

Build a small **AI coach or tutor** for a domain you choose, and wire a language model into it through API calls. Your app must do two things well: work as an ordinary interactive program *without* any AI, and then add an AI layer that enhances it. Some directions students have taken:

- **A simpler game with a coach** — Tic-Tac-Toe, Connect Four, Reversi/Othello, Nim, or Mancala, with the model commenting on each move and estimating skill.
- **A writing coach** — paste a paragraph; the model returns targeted feedback plus a structured `{"clarity": 1-5, "issues": [...]}` score.
- **A code reviewer** — submit a short function; the model flags issues in prose and returns a structured severity rating.
- **A language-drill tutor** — vocabulary or grammar practice where the model grades an answer and returns `{"correct": true/false, "hint": "..."}`.

Any domain is acceptable as long as it has a genuine **interactive core** (a user takes turns or actions and state is tracked) and the AI adds **coaching, grading, or commentary** on top. You may write it as a single-file browser app in the style of the tutorial, or as a small Python program/notebook — your choice of language and stack.

---

#### What a Strong Submission Looks Like

- The core runs and is correct on its own; unplugging the AI leaves a usable program.
- Exactly one function makes every model call, and pointing it at a different provider is a one-line change or a config edit — not a rewrite.
- At least one feature asks the model for **JSON** and uses the parsed value to drive something (a score, a badge, a meter, a branch).
- There is **no API key anywhere in your repository**, and your write-up can explain why your key-handling choice is safe.

---

#### Part 1: Choose Your Domain and Build the Interactive Core

Pick a domain and implement the non-AI core first. This is deliberately the same ordering the tutorial preaches: **make the app fully work without the model, then add the model as an enhancement.**

Your core must:

- Present a state the user can act on (a board, a text box, a prompt).
- Accept a user action and update state correctly, rejecting invalid actions.
- Be playable/usable start to finish with the AI turned off.

> **Getting Started Hint:** If you choose a game, keep the rules simple (Tic-Tac-Toe or Connect Four) so your time goes into the AI integration, not a rules engine. The Chess AI Coach spends hundreds of lines on chess rules; you do not need to.

---

#### Part 2: Add the Provider-Agnostic AI Layer

Write **one** function that every AI feature calls — the equivalent of `callTextModel` in the tutorial. It takes a prompt (and options) and returns the model's text. Internally it selects the provider and knows each one's URL, auth header, and response path.

At minimum, support **one** provider end to end; structure the function so a second provider is a small addition. A recommended, keyless starting point is a **local OpenAI-compatible server** (Ollama or Open WebUI), exactly as in the [REST activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-restllmapi.md):

```python
import requests

def call_text_model(base_url, model, prompt, api_key="ollama", temperature=0.2):
    endpoint = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {"model": model,
               "messages": [{"role": "user", "content": prompt}],
               "stream": False, "temperature": temperature}
    r = requests.post(endpoint, json=payload, headers=headers, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
```

> **Checkpoint:** Before moving on, confirm that changing only `base_url` and `model` sends your prompt to a different server. That single property is what "provider-agnostic" means, and it is worth 25 points.

---

#### Part 3: Add at Least One Structured-Output Feature

Add a feature that asks the model for **JSON** and uses the value in your program. Follow the tutorial's three-part discipline: ask precisely, clean the text, and never trust the parse.

```python
import json

def safe_json_parse(text, fallback):
    try:
        return json.loads(text)
    except Exception:
        return fallback

def score_answer(call, user_answer):
    prompt = ('Grade this answer. Respond ONLY with JSON like '
              '{"correct": true, "hint": "one short tip"}. Answer: ' + user_answer)
    raw = call(prompt)                      # your provider-agnostic function
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    parsed = safe_json_parse(cleaned, {})
    return {
        "correct": bool(parsed.get("correct", False)),   # default every field
        "hint": parsed.get("hint", "No hint available."),
    }
```

Your feature must keep working when the model returns something malformed — show a sensible default, not a stack trace.

---

#### Part 4: Secure Your Keys

This is graded, and a committed key is an automatic pre-emerging on that row. Follow the rules from Part IV of the tutorial:

- **Never** hardcode a key in your source, and **never** commit one. Add any secrets file to `.gitignore`.
- Get keys from **user input** (a field the user fills in at runtime) or from an **environment variable** (`os.environ[...]`), never from a literal in the code.
- If you use a **local model** (Ollama / Open WebUI), there is no cloud key to leak — this is the simplest safe choice.
- In your write-up, explain in your own words **why** putting a cloud key directly in browser JavaScript is unsafe for a public deployment, and what the **backend-proxy** pattern does about it.

> **Common Pitfall:** `type="password"` on an input, or base64-encoding the key in your JavaScript, does **not** protect it — the key is still sent over the network and visible in the browser's DevTools. Masking is not protection.

---

#### Common Pitfalls

- **The AI is load-bearing.** If your app is unusable without the model, you have skipped Part 1. The core must stand alone.
- **Copy-paste provider mismatch.** Reusing OpenAI's `choices[0].message.content` parse against Anthropic's `content[].text` response is the classic "empty response" bug. One parse per response family.
- **Assuming clean JSON.** Models add prose and code fences. Strip, parse defensively, default every field.
- **A key in Git history.** Deleting a key in a later commit does not remove it from history. Never commit it in the first place; use `.gitignore` from the start.

---

#### Reflection Prompts

Answer these in your write-up:

- **Design.** What is your domain, and what does the AI add on top of the core? Where does your single AI-call function live, and how would you point it at a different provider?
- **Structured output.** Which feature uses JSON, and what happens in your code when the model returns a malformed reply? Give the actual default your app falls back to.
- **Security.** Where does your key live, and why is that safe? If you deployed this for the whole class to use at once, what would you change?
- **Honesty about the AI.** Give one thing your AI coach does genuinely well and one thing it does poorly or unreliably. How would a user know which is which?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? Regardless, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did it take you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

#### Submission Checklist

- [ ] An interactive core that runs and is correct **with the AI turned off**.
- [ ] One provider-agnostic function that makes every model call, with the base URL and model changeable without a rewrite.
- [ ] At least one feature that requests JSON and parses it defensively, with a demonstrated fallback on a malformed reply.
- [ ] **No API key committed anywhere**, a `.gitignore` covering any secrets, and keys sourced from user input or an environment variable.
- [ ] A short write-up answering every reflection prompt above, including the security explanation and both closing questions.
- [ ] Instructions to run your app (commands, and which provider/model you tested against).
