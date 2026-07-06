---
layout: assignment
permalink: /Assignments/AICoach
title: "CS357: Foundations of Artificial Intelligence - Lab: Build Your Own AI Coach"

info:
  coursenum: CS357
  purpose: "To turn the provider-agnostic API pattern from the Chess AI Coach into your own working application, so you can integrate a language model into real software safely, portably, and with structured output you can actually use."
  tilt:
    task: "Build a small interactive application in a domain of your choice and add an AI coaching or tutoring layer that calls a language model through one provider-agnostic function, uses at least one structured-JSON feature, and exposes no API key."
    criteria: "Assessed on a working interactive core, a portable AI integration, disciplined prompt-and-parse for structured output, correct API-key handling, and an honest reflection; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To integrate a language model into an application through a single provider-agnostic API call that can switch between a local and a cloud provider without rewriting the app
    - To engineer prompts for both prose and structured JSON output, and to parse structured replies defensively so a malformed reply degrades instead of crashing
    - To handle API keys so that no secret is ever committed or exposed to the client, and to explain the production backend-proxy pattern in your own words
    - To design an application whose core functionality degrades gracefully when the AI is unavailable
  rubric:
    - weight: 25
      description: Working Interactive Core
      preemerging: The artifact does not run, or there is no interactive turn/action loop for a user to engage with
      beginning: The artifact runs but the interaction is incomplete or its state is frequently wrong (invalid actions allowed, actions not recorded)
      progressing: The artifact runs and tracks state correctly for the common cases, with minor gaps in edge cases or input validation
      proficient: The artifact runs cleanly, enforces its own rules, tracks state correctly including edge cases, and a new user can complete a full sequence of turns or actions without reaching a broken state
    - weight: 25
      description: Provider-Agnostic AI Integration
      preemerging: There is no working call to a language model, or the provider and endpoint are hardcoded in a way that cannot be changed
      beginning: A single call to one provider works, but the code cannot switch providers or endpoints without substantial rewriting
      progressing: A single dispatch function calls the model and the base URL or model can be changed, but at least one provider path is untested or partially broken
      proficient: One dispatch function routes every model call through fetch or requests, works against a local OpenAI-compatible server or a cloud provider, and switching the base_url and model is demonstrated or clearly documented
    - weight: 20
      description: Prompt Engineering and Structured Output
      preemerging: Prompts are absent or produce unusable output, and no structured output is attempted
      beginning: Prompts produce prose, but the one structured-output feature does not reliably parse or crashes on a malformed reply
      progressing: At least one feature requests and parses JSON with a prompt that specifies the format, but parsing lacks a fallback for malformed replies
      proficient: At least one feature requests JSON with a precise format example, strips wrappers such as code fences, parses defensively with a fallback, and defaults every field so a bad reply degrades instead of crashing
    - weight: 15
      description: API Key Security and Documentation
      preemerging: A real key is committed to the repository or hardcoded in the source
      beginning: No key is committed, but keys are handled ad hoc and the write-up does not address the exposure risk
      progressing: Keys come from user input or an environment variable and a .gitignore is present, but the write-up only partially explains the client-side risk or the production pattern
      proficient: No secret is committed anywhere; keys come from user input or an environment variable with a .gitignore; and the write-up correctly explains the client-side-key exposure risk and the backend-proxy or keyless-local-model production pattern
    - weight: 15
      description: Reflection and Write-Up
      preemerging: The write-up is missing or does not describe the design
      beginning: The write-up lists what was built but does not reflect on the AI's behavior or limitations
      progressing: The write-up explains the design and gives some honest assessment of what the AI does well and poorly, and partly addresses the two standard closing questions
      proficient: The write-up clearly explains the design decisions, honestly assesses where the AI helps and where it is unreliable, names concrete limitations, and answers both standard closing questions
  readings:
    - rtitle: "Building an AI Chess Coach: LLM API Calls in a Real Web App (this lab's worked example)"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-chessaicoach.md"
    - rtitle: "RESTful LLM Access: The api/v1 Paradigm (prerequisite)"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-restllmapi.md"

tags:
  - ai
  - api
  - web
  - security

---

You have seen a language model wired into a real, working program: the [Chess AI Coach](/files/apps/chess-ai-coach.html). It plays a full game with pure local logic and then *layers* a language model on top for commentary, an evaluation number, and an Elo estimate — routed through one provider-agnostic function, parsed defensively, with the API key never leaving the user's browser.

Now you build your own. The domain is up to you; the **architecture** is the point. You will reuse the exact pattern from the tutorial: a working interactive core, a single dispatch function that talks to a language model, at least one structured-JSON feature, and airtight key handling.

---

## Overview

Build a small **AI coach or tutor** for a domain you choose, and wire a language model into it through API calls. Your app must do two things well: work as an ordinary interactive program *without* any AI, and then add an AI layer that enhances it. Some directions students have taken:

- **A simpler game with a coach** — Tic-Tac-Toe, Connect Four, Reversi/Othello, Nim, or Mancala, with the model commenting on each move and estimating skill.
- **A writing coach** — paste a paragraph; the model returns targeted feedback plus a structured `{"clarity": 1-5, "issues": [...]}` score.
- **A code reviewer** — submit a short function; the model flags issues in prose and returns a structured severity rating.
- **A language-drill tutor** — vocabulary or grammar practice where the model grades an answer and returns `{"correct": true/false, "hint": "..."}`.

Any domain is acceptable as long as it has a genuine **interactive core** (a user takes turns or actions and state is tracked) and the AI adds **coaching, grading, or commentary** on top. You may write it as a single-file browser app in the style of the tutorial, or as a small Python program/notebook — your choice of language and stack.

---

## What a Strong Submission Looks Like

- The core runs and is correct on its own; unplugging the AI leaves a usable program.
- Exactly one function makes every model call, and pointing it at a different provider is a one-line change or a config edit — not a rewrite.
- At least one feature asks the model for **JSON** and uses the parsed value to drive something (a score, a badge, a meter, a branch).
- There is **no API key anywhere in your repository**, and your write-up can explain why your key-handling choice is safe.

---

## Part 1: Choose Your Domain and Build the Interactive Core

Pick a domain and implement the non-AI core first. This is deliberately the same ordering the tutorial preaches: **make the app fully work without the model, then add the model as an enhancement.**

Your core must:

- Present a state the user can act on (a board, a text box, a prompt).
- Accept a user action and update state correctly, rejecting invalid actions.
- Be playable/usable start to finish with the AI turned off.

> **Getting Started Hint:** If you choose a game, keep the rules simple (Tic-Tac-Toe or Connect Four) so your time goes into the AI integration, not a rules engine. The Chess AI Coach spends hundreds of lines on chess rules; you do not need to.

---

## Part 2: Add the Provider-Agnostic AI Layer

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

## Part 3: Add at Least One Structured-Output Feature

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

## Part 4: Secure Your Keys

This is graded, and a committed key is an automatic pre-emerging on that row. Follow the rules from Part IV of the tutorial:

- **Never** hardcode a key in your source, and **never** commit one. Add any secrets file to `.gitignore`.
- Get keys from **user input** (a field the user fills in at runtime) or from an **environment variable** (`os.environ[...]`), never from a literal in the code.
- If you use a **local model** (Ollama / Open WebUI), there is no cloud key to leak — this is the simplest safe choice.
- In your write-up, explain in your own words **why** putting a cloud key directly in browser JavaScript is unsafe for a public deployment, and what the **backend-proxy** pattern does about it.

> **Common Pitfall:** `type="password"` on an input, or base64-encoding the key in your JavaScript, does **not** protect it — the key is still sent over the network and visible in the browser's DevTools. Masking is not protection.

---

## Common Pitfalls

- **The AI is load-bearing.** If your app is unusable without the model, you have skipped Part 1. The core must stand alone.
- **Copy-paste provider mismatch.** Reusing OpenAI's `choices[0].message.content` parse against Anthropic's `content[].text` response is the classic "empty response" bug. One parse per response family.
- **Assuming clean JSON.** Models add prose and code fences. Strip, parse defensively, default every field.
- **A key in Git history.** Deleting a key in a later commit does not remove it from history. Never commit it in the first place; use `.gitignore` from the start.

---

## Reflection Prompts

Answer these in your write-up:

- **Design.** What is your domain, and what does the AI add on top of the core? Where does your single AI-call function live, and how would you point it at a different provider?
- **Structured output.** Which feature uses JSON, and what happens in your code when the model returns a malformed reply? Give the actual default your app falls back to.
- **Security.** Where does your key live, and why is that safe? If you deployed this for the whole class to use at once, what would you change?
- **Honesty about the AI.** Give one thing your AI coach does genuinely well and one thing it does poorly or unreliably. How would a user know which is which?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? Regardless, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did it take you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

## Submission Checklist

- [ ] An interactive core that runs and is correct **with the AI turned off**.
- [ ] One provider-agnostic function that makes every model call, with the base URL and model changeable without a rewrite.
- [ ] At least one feature that requests JSON and parses it defensively, with a demonstrated fallback on a malformed reply.
- [ ] **No API key committed anywhere**, a `.gitignore` covering any secrets, and keys sourced from user input or an environment variable.
- [ ] A short write-up answering every reflection prompt above, including the security explanation and both closing questions.
- [ ] Instructions to run your app (commands, and which provider/model you tested against).
