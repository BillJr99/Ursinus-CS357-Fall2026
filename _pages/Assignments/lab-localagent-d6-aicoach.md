---
layout: assignment
permalink: /Assignments/LocalAgent/Direction6
title: "CS357 Lab: Local Agent, Direction 6: Build Your Own AI Coach"
---

> **Grading:** This page is one of the directions for the [Local Agent Lab]({{ site.baseurl }}/Assignments/LocalAgent).  It carries no points of its own.  I grade the core and the direction together with the Local Agent Lab rubric on the core lab page.

> **Rather not write the code?**  [Direction 0: The OpenWebUI Route]({{ site.baseurl }}/Assignments/LocalAgent/Direction0) reaches the same objectives for the Local Agent Lab with no code to author; you build and evaluate the same system as configuration instead.  Take whichever direction appeals to you.  I give the same credit for either one.

> **What this direction requires**
>
> - **Accounts:** none on the recommended path.  A local OpenAI-compatible server (Ollama or Open WebUI) needs no key.
> - **API costs:** none on the local path.  A cloud provider key is optional, never required, and must never be committed to your repository.
> - **Installs / disk:** nothing beyond the core lab for a Python app (`requests`).  A single-file browser app needs no installs at all.
> - **Hardware:** any machine that runs the core lab.
> - **No-cost fallback:** built in.  Part 2 recommends the keyless local-server route as the starting point.
> - **Pace yourself:** this sits on top of the core lab.  Spend more than half of your time on the non-AI core.  The app has to work before you add the model, and that ordering is the point of the direction, not a suggestion.

---


Build a small application around the single language-model call from the core lab.  The application is an AI coach: an interactive program that runs entirely on its own logic, with a language model layered on top for commentary and structured output.  Every model call goes through one provider-agnostic function, every model reply is parsed defensively, and the API key never reaches the client.  The domain is up to you.  The architecture is what I grade.

You have already seen this pattern in a working program: the [Chess AI Coach]({{ site.baseurl }}/files/apps/chess-ai-coach.html).  It plays a full game of chess with local logic alone.  It then adds a language model for move commentary, an evaluation number, and an Elo estimate.  Every one of those calls goes through one function that can talk to any provider, every reply is parsed defensively, and the key never leaves the user's browser.

Now you build your own.  You will reuse the same four pieces from that tutorial: a working interactive core, a single function that talks to the model, at least one feature that asks for structured JSON, and key handling that never leaks.

---

#### Overview

Build a small AI coach or tutor for a domain you choose, and connect a language model to it through API calls.  Your app must do two things well.  First, it must work as an ordinary interactive program without any AI.  Second, it must add an AI layer that improves it.  Some directions students have taken:

- **A simpler game with a coach**: Tic-Tac-Toe, Connect Four, Reversi/Othello, Nim, or Mancala, with the model commenting on each move and estimating skill.
- **A writing coach**: paste a paragraph; the model returns targeted feedback plus a structured `{"clarity": 1-5, "issues": [...]}` score.
- **A code reviewer**: submit a short function; the model flags issues in prose and returns a structured severity rating.
- **A language-drill tutor**: vocabulary or grammar practice where the model grades an answer and returns `{"correct": true/false, "hint": "..."}`.

Any domain works as long as it has a real interactive core (the user takes turns or actions, and the program tracks state) and the AI adds coaching, grading, or commentary on top.  Write it as a single-file browser app in the style of the tutorial, or as a small Python program or notebook.  The language and stack are your choice.

---

#### What a Strong Submission Looks Like

- The core runs and is correct on its own.  Unplugging the AI leaves a usable program.
- Exactly one function makes every model call.  Pointing it at a different provider is a one-line change or a config edit, not a rewrite.
- At least one feature asks the model for JSON and uses the parsed value to drive something (a score, a badge, a meter, a branch).
- There is no API key anywhere in your repository, and your write-up explains why your key-handling choice is safe.

---

#### Part 1: Choose Your Domain and Build the Interactive Core

Pick a domain and build the non-AI core first.  This is the ordering the tutorial insists on: make the app work fully without the model, then add the model as an enhancement.

Your core must:

- Present a state the user can act on (a board, a text box, a prompt).
- Accept a user action and update the state correctly, rejecting invalid actions.
- Be playable or usable from start to finish with the AI turned off.

> **Getting Started Hint:** If you choose a game, keep the rules simple (Tic-Tac-Toe or Connect Four) so your time goes into the AI integration rather than a rules engine.  The Chess AI Coach spends hundreds of lines on chess rules.  You do not need to.

---

#### Part 2: Add the Provider-Agnostic AI Layer

Write one function that every AI feature calls.  It is the equivalent of `callTextModel` in the tutorial.  It takes a prompt (and options) and returns the model's text.  Inside, it selects the provider and knows that provider's URL, auth header, and response path.

That is what a provider-agnostic API call means: the rest of your program asks for the model's answer to a prompt and never learns which company or server produced it.  Change the base URL and the model name, and the same function talks to a different provider.

Support at least one provider end to end, and structure the function so that a second provider is a small addition.  The recommended, keyless starting point is a local OpenAI-compatible server (Ollama or Open WebUI), exactly as in the [REST activity]({{ site.baseurl }}/Tutorials/RESTLLMAPI):

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

Each piece of that function has one job.  `base_url` and `model` choose the server and the model.  `headers` carries the content type and the key (Ollama ignores the key, but the header shape matches the cloud providers).  `payload` is the request body in the OpenAI chat format.  The last line pulls the reply text out of the response.

> **Checkpoint:** Before moving on, confirm that changing only `base_url` and `model` sends your prompt to a different server.  That single property is what "provider-agnostic" means, and it is worth 25 points.

---

#### Part 3: Add at Least One Structured-Output Feature

Add a feature that asks the model for JSON and uses the value in your program.  Follow the tutorial's three-part discipline: ask precisely, clean the text, and never trust the parse.

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

Read `score_answer` in three steps.  The prompt asks for JSON and shows the exact shape it wants.  The `cleaned` line strips the code fences that models often wrap around JSON.  The return statement supplies a default for every field, so a missing or garbled reply produces a usable value instead of a crash.

Your feature must keep working when the model returns something malformed.  Show a sensible default, not a stack trace.

---

#### Part 4: Secure Your Keys

This part is graded, and a committed key is an automatic pre-emerging on that row.  Follow the rules from Part IV of the tutorial:

- Never hardcode a key in your source, and never commit one.  Add any secrets file to `.gitignore`.
- Get keys from user input (a field the user fills in at runtime) or from an environment variable (`os.environ[...]`), never from a literal in the code.
- If you use a local model (Ollama or Open WebUI), there is no cloud key to leak.  This is the simplest safe choice.
- In your write-up, explain in your own words why putting a cloud key directly in browser JavaScript is unsafe for a public deployment, and what the backend-proxy pattern does about it.  A backend proxy is a small server you control: the browser sends requests to it, and it adds the key and forwards them to the provider, so the key never reaches the browser.

> **Common Pitfall:** `type="password"` on an input, or base64-encoding the key in your JavaScript, does not protect it.  The key is still sent over the network and visible in the browser's DevTools.  Masking is not protection.

---

#### Common Pitfalls

- **The AI is load-bearing.**  If your app is unusable without the model, you skipped Part 1.  The core must stand alone.
- **Copy-paste provider mismatch.**  Reusing OpenAI's `choices[0].message.content` parse against Anthropic's `content[].text` response is the classic "empty response" bug.  Write one parse per response family.
- **Assuming clean JSON.**  Models add prose and code fences.  Strip, parse defensively, and default every field.
- **A key in Git history.**  Deleting a key in a later commit does not remove it from history.  Never commit it in the first place.  Use `.gitignore` from the start.

---

#### Reflection Prompts

Answer these in your write-up:

- **Design.**  What is your domain, and what does the AI add on top of the core?  Where does your single AI-call function live, and how would you point it at a different provider?
- **Structured output.**  Which feature uses JSON, and what happens in your code when the model returns a malformed reply?  Give the actual default your app falls back to.
- **Security.**  Where does your key live, and why is that safe?  If you deployed this for the whole class to use at once, what would you change?
- **Honesty about the AI.** Give one thing your AI coach does well and one thing it does poorly or unreliably.  How would a user know which is which?
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment?  If so, who?  Regardless, do you certify that this submission represents your own original work?  Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did it take you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

#### Submission Checklist

- [ ] An interactive core that runs and is correct **with the AI turned off**.
- [ ] One provider-agnostic function that makes every model call, with the base URL and model changeable without a rewrite.
- [ ] At least one feature that requests JSON and parses it defensively, with a demonstrated fallback on a malformed reply.
- [ ] **No API key committed anywhere**, a `.gitignore` covering any secrets, and keys sourced from user input or an environment variable.
- [ ] A short write-up answering every reflection prompt above, including the security explanation and both closing questions.
- [ ] Instructions to run your app (commands, and which provider/model you tested against).

---

#### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| The model's JSON will not parse | You asked for JSON in prose and hoped | Use the provider's structured-output mode, or a schema plus a few-shot example. Then still parse defensively: this is the *Tools and MCP* lesson, applied |
| Occasionally the JSON parses and the value is nonsense (a score of 47 out of 5) | Parsing is not validation | Range-check every parsed value before it drives anything. A badge driven by an unvalidated number is a bug waiting for a demo |
| The app breaks when the model is slow or unreachable | The AI layer is load-bearing rather than additive | Fix the architecture, not the timeout: the core must remain usable with the model off. Test by pointing the dispatch function at nothing |
| Switching providers means editing several files | More than one place makes model calls | Consolidate into the single dispatch function. This is the requirement, and it is worth doing before you go further |
| The API key ends up in the repository | It was inlined for testing and committed | Rotate the key immediately, then remove it from history. Prefer the keyless local-server route, which is why it is recommended |
| The commentary is bland and identical every turn | The prompt gets the state but not the *situation* | Pass what changed and why it matters, not just the current state. Compare a prompt with and without it and keep both in your writeup |

#### Self-Check Before You Submit

- [ ] The interactive core is correct and **usable with the AI turned off**, and I have run it that way.
- [ ] Invalid user actions are rejected by the core, not by the model.
- [ ] **Exactly one** function makes every model call.
- [ ] Pointing it at a different provider is a one-line change or a config edit; I can say what that line is.
- [ ] At least one feature asks for **JSON** and uses the parsed value to drive something visible.
- [ ] Parsed values are **validated**, not merely parsed.
- [ ] There is **no API key** anywhere in the repository, and the writeup explains why my key handling is safe.
- [ ] The writeup shows a before-and-after of one prompt change that improved the coaching.
- [ ] The writeup names one thing the coach gets confidently wrong, and how a user would notice.
