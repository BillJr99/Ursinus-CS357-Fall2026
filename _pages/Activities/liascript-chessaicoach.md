<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-chessaicoach.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-chessaicoach.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Building an AI Chess Coach: LLM API Calls in a Real Web App

This module dissects a complete, working web app (the **Chess AI Coach**) to show exactly how a language model gets wired into real software through **API calls**. We move from **what the app is $\rightarrow$ the three-layer architecture $\rightarrow$ one function that talks to three different providers $\rightarrow$ prompt engineering and structured JSON output for coaching $\rightarrow$ keeping your API keys safe $\rightarrow$ wiring the AI into the user interface**.

The app is a single self-contained HTML file. You can open it, read every line, and change it. Everything you learned in the [RESTful LLM Access](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-restllmapi.md) activity (the `/v1/chat/completions` payload, the `choices[0].message.content` response path, provider portability) reappears here, this time in JavaScript running inside a browser instead of Python in a notebook.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Single-file app** | An entire application (markup, styles, logic) in one `.html` file that runs by opening it in a browser | `chess-ai-coach.html` loads React and Babel from a CDN and needs no build step |
| **`fetch`** | The browser's built-in function for making HTTP requests from JavaScript; the front-end equivalent of Python's `requests` | `await fetch("https://api.anthropic.com/v1/messages", { method: "POST", ... })` |
| **Provider-agnostic dispatcher** | One function that accepts a prompt and routes it to whichever AI provider the user selected, hiding the per-provider differences | `callTextModel(providerConfig, prompt)` handles Anthropic, OpenAI, and Open WebUI |
| **System vs. user content** | The instruction framing ("you are a chess coach") versus the specific request (this position, this move) | The coaching prompt states the coach's role, then supplies the FEN and move |
| **Structured output** | Asking the model to answer as parseable JSON instead of prose, so the program can use the value | `{"eval": 0.5}` for the evaluation bar; `{"elo": 1200, "label": "Intermediate"}` |
| **FEN / SAN** | Standard text encodings of a chess **position** (FEN) and a single **move** (SAN), the tokens we hand the model | `rnbqkbnr/pppppppp/... w KQkq - 0 1`; `Nf3`, `O-O`, `exd5` |
| **Client-side key exposure** | The risk that an API key placed in browser code is visible to anyone using or inspecting that browser | The key shows up in the browser's Network tab on every request |
| **Backend proxy** | A small server you own that holds the secret key and forwards browser requests to the provider | Browser -> your `/api/coach` endpoint -> provider; the key never leaves your server |
| **Graceful degradation** | The app stays fully usable when the optional AI is unavailable | With no provider configured, the board still plays against a local engine |

---

### Before You Start

**What you need:** Ollama running locally. Section 0 lets you try the finished app before building anything.

**What you will have at the end:** a working chess coach that explains moves, built from API calls you can read end to end.

Work through the sections in order; each one builds on the last, and the code blocks are meant to be run as you reach them, not read past.

---

## 0. Try the App First

Before reading any code, **play the app** so the rest of the activity has something concrete to attach to.

1. Download or open [`chess-ai-coach.html`](https://www.billmongan.com/Ursinus-CS357/files/apps/chess-ai-coach.html).
2. Because browsers restrict `fetch` from `file://` pages, serve the folder with a tiny local web server and open it over `http://`:

## Code Cell

```bash
# From the folder that contains chess-ai-coach.html
python -m http.server 8000
# then open http://localhost:8000/chess-ai-coach.html
```

3. Leave the provider set to **Local only** and play a few moves. The board enforces full chess rules and a computer opponent replies, **with no AI and no API key at all.** Keep that in mind: the language model is an *addition*, not the engine.

---

# Part I: What We're Building and the Three-Layer Architecture

In this part you build a mental map of the app before touching the AI. The single most useful habit when adding AI to software is knowing **which parts are deterministic program logic and which parts call the model**, because they fail, cost, and get tested in completely different ways.

## 1. The App at a Glance

The Chess AI Coach lets you play a full game against a built-in computer opponent, and (if you connect a language model) it adds a coaching layer on top:

- **Per-move commentary**: after each move, the model judges it (good / inaccurate / mistake / blunder) in the context of the whole game.
- **An evaluation bar**: a number, positive for White, that fills a meter beside the board.
- **An Elo estimate**: a calibrated guess at each side's playing strength based on the moves so far.
- **PGN and analysis export**: the game and all commentary saved to a text file.

Every one of those features is optional. The board, the legal-move enforcement, the computer opponent, and a fallback evaluation all run **locally in the browser** with no network calls.

## 2. Three Layers, Cleanly Separated

The file is organized into three layers, and the separation is deliberate:

$$
\underbrace{\text{Chess Engine}}_{\text{pure logic}} \;\;\rightarrow\;\; \underbrace{\text{React UI}}_{\text{display + input}} \;\;\leftarrow\;\; \underbrace{\text{AI Layer}}_{\text{API calls}}
$$

| Layer | What it does | Representative functions | Needs the network? |
|---|---|---|---|
| **Chess engine** | Enforces the rules, generates legal moves, plays the computer's move, scores a position | `initialState`, `legalMoves`, `applyMove`, `minimax`, `computerMove`, `evaluate`, `boardToFEN`, `moveToSAN`, `buildPGN` | No, pure, deterministic |
| **React UI** | Draws the board, handles clicks and drags, shows commentary and meters | the `ChessAICoach` component and its `useState`/`useEffect` hooks | No |
| **AI layer** | Turns a position into a prompt, calls a provider, parses the reply | `callTextModel`, `getAICommentary`, `getAIEvaluation`, `getSideAIElo` | **Yes, this is where the API calls live** |

The engine is the kind of code you can unit-test exhaustively: given this board, `legalMoves` must return exactly these moves. The AI layer is the opposite: it calls a probabilistic model over the network, so it can be slow, cost money, fail, or return something unexpected. **Keeping them apart means a bug in the coach can never make the board illegal, and the game never depends on a server being reachable.**

---

## Model 1: Locating the Seams

Open `chess-ai-coach.html` and skim the top-level function names. Group them into the three layers above.

### Critical Thinking Questions

1. `evaluate(state)` (local, in the engine) and `getAIEvaluation(providerConfig, fen)` (in the AI layer) both produce a single number describing who is winning. Why does the app keep **both**, and when does each one run?

   > *Hint: Look at the `useEffect` that sets `evalScore`. When no provider is configured (`!aiEnabled`), it uses `evaluate(gameState) / 100`. When a provider is configured, it calls `getAIEvaluation` and falls back to `evaluate` if the call throws. One is free, instant, and deterministic; the other needs a working API call.*

2. The function `boardToFEN(state)` belongs to the engine, but the AI layer depends on it heavily. What is the FEN string *for*, and why is it the natural thing to send to a language model instead of, say, the raw 8×8 JavaScript array?

   > *Hint: FEN is a compact, standard, text encoding of a position. Models have seen enormous amounts of FEN in training; a nested JS array is not something a model reads fluently, and it would waste tokens. Text-in, text-out; the engine speaks the model's language by exporting FEN and SAN.*

3. Suppose the Anthropic API is down for an hour. Trace what a user can and cannot do in the app during that hour. Which layer is affected?

   > *Hint: Only the AI layer makes network calls. The engine and UI keep working, so the user can still play full games against the local computer; they just lose commentary, the AI evaluation, and the Elo estimate. This is graceful degradation, and it is a direct consequence of the layering.*

Which group of functions makes the HTTP requests to a language-model provider?

[( )] `legalMoves`, `applyMove`, `minimax`
[( )] `boardToFEN`, `moveToSAN`, `buildPGN`
[(X)] `callTextModel`, `getAICommentary`, `getAIEvaluation`
[( )] `handleSquareClick`, `handleDragStart`

> **Common Misconception:** "The AI plays the chess." It does not. The **computer opponent** is the local `minimax` search in the engine layer: pure code, no network. The **language model** only *comments on* moves and *estimates* numbers. You could delete every AI function and still have a working chess game. Conflating "the program that plays" with "the model that talks" is the first confusion to clear up.

---

# Part II: The Provider-Agnostic AI Layer

This is the heart of the activity. You will see how one function, `callTextModel`, sends the same prompt to **Anthropic, OpenAI, or a local Open WebUI / Ollama server**, differing only in URL, headers, and where the reply text sits in the response. This is the browser-JavaScript version of the provider portability you built in Python in the REST activity.

## 3. One Function, Three Providers

Everywhere else in the app, code that needs the model calls a single function:

```js
const text = await callTextModel(providerConfig, prompt, { maxTokens: 350, temperature: 0.2 });
```

`providerConfig` is a plain object assembled from the UI (which provider is selected, plus the relevant key/URL/model). `callTextModel` reads `providerConfig.provider` and branches. Its skeleton is:

## Code Cell

```js
async function callTextModel(providerConfig, prompt, { maxTokens = 500, temperature = 0.2 } = {}) {
  const provider = providerConfig.provider;
  if (provider === "anthropic") { /* POST to api.anthropic.com/v1/messages */ }
  if (provider === "openai")    { /* POST to api.openai.com/v1/chat/completions */ }
  if (provider === "openwebui") { /* POST to <baseUrl>/api/chat/completions */ }
  throw new Error("Unsupported AI provider.");
}
```

Notice the shape: **the rest of the app never knows or cares which provider is active.** Adding a fourth provider later means adding one more branch here and nothing else changes. That is the whole point of a dispatcher.

## 4. Anthropic: `POST https://api.anthropic.com/v1/messages`

Anthropic's Messages API uses its own endpoint and header names. Here is the branch, annotated:

## Code Cell

```js
if (provider === "anthropic") {
  if (!providerConfig.anthropicKey) throw new Error("Enter an Anthropic API key.");
  const model = providerConfig.anthropicModel || DEFAULT_MODELS.anthropic;

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": providerConfig.anthropicKey,          // <-- auth header (NOT "Authorization")
      "anthropic-version": "2023-06-01",                 // <-- required API version pin
      "anthropic-dangerous-direct-browser-access": "true" // <-- opt-in to call from a browser (see Part IV)
    },
    body: JSON.stringify({
      model,
      max_tokens: maxTokens,
      temperature,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  const data = await res.json().catch(async () => ({ raw: await res.text() }));
  if (!res.ok || data?.error) throw new Error(data?.error?.message || data?.raw || res.statusText);

  // Anthropic returns a "content" array of blocks; join their text.
  return data?.content?.map(block => block?.text || "").join("").trim() || "";
}
```

Three things to note: the auth header is **`x-api-key`** (not `Authorization: Bearer`); a **version** header is mandatory; and the reply text lives at **`data.content[].text`**, an array of content blocks, not a single string.

## 5. OpenAI: `POST https://api.openai.com/v1/chat/completions`

The OpenAI branch uses the same `/v1/chat/completions` shape you already know from the REST activity:

## Code Cell

```js
if (provider === "openai") {
  if (!providerConfig.openaiKey) throw new Error("Enter an OpenAI API key.");
  const model = providerConfig.openaiModel || DEFAULT_MODELS.openai;

  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "authorization": `Bearer ${providerConfig.openaiKey}`, // <-- Bearer-token auth
    },
    body: JSON.stringify({
      model,
      messages: [{ role: "user", content: prompt }],
      max_completion_tokens: maxTokens,
      temperature,
    }),
  });

  const data = await res.json().catch(async () => ({ raw: await res.text() }));
  if (!res.ok || data?.error) throw new Error(data?.error?.message || data?.raw || res.statusText);

  return extractOpenAIText(data).trim(); // reads choices[0].message.content, defensively
}
```

The reply lives at **`choices[0].message.content`**. The app wraps that access in a small helper, `extractOpenAIText`, that tolerates a few response shapes instead of crashing on an unexpected one:

## Code Cell

```js
function extractOpenAIText(data) {
  if (typeof data?.output_text === "string" && data.output_text) return data.output_text;
  const msg = data?.choices?.[0]?.message;
  if (typeof msg?.content === "string") return msg.content;
  if (Array.isArray(msg?.content)) return msg.content.map(part => part?.text || part?.content || "").join("");
  return "";
}
```

## 6. Open WebUI / Local: `POST <baseUrl>/api/chat/completions`

The third branch targets a **local, OpenAI-compatible server** (Open WebUI in front of Ollama, or Ollama directly). Because it speaks the same protocol as OpenAI, the response parsing is *identical*; only the URL changes, and the key is optional:

## Code Cell

```js
if (provider === "openwebui") {
  const baseUrl = normalizeBaseUrl(providerConfig.openWebUIUrl); // trims trailing slashes
  if (!baseUrl) throw new Error("Enter an Open WebUI base URL.");
  if (!providerConfig.openWebUIModel) throw new Error("Choose an Open WebUI model.");

  const res = await fetch(baseUrl + "/api/chat/completions", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "authorization": providerConfig.openWebUIKey ? `Bearer ${providerConfig.openWebUIKey}` : "",
    },
    body: JSON.stringify({
      model: providerConfig.openWebUIModel,
      messages: [{ role: "user", content: prompt }],
      max_tokens: maxTokens,
      temperature,
    }),
  });

  const data = await res.json().catch(async () => ({ raw: await res.text() }));
  if (!res.ok || data?.error) throw new Error(data?.error?.message || data?.raw || res.statusText);

  return extractOpenAIText(data).trim(); // same choices[0].message.content path as OpenAI
}
```

The app can even **discover** which models a local server has, via a `GET /api/models` call in `fetchOpenWebUIModels`, the same "list models before you use one" pattern from the REST activity's `/v1/models`.

Here is the whole idea, reduced to a **runnable Python cell** you can execute against your own local Ollama right now. It is the same request the browser makes (same endpoint shape, same `messages` array, same `choices[0].message.content` parse), just in Python:

## Code Cell

```python
import requests

def chat_completion(base_url, model, messages, api_key="ollama", temperature=0.2):
    """One request that works against ANY OpenAI-compatible server (Ollama, Open WebUI, cloud)."""
    endpoint = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {"model": model, "messages": messages, "stream": False, "temperature": temperature}
    try:
        r = requests.post(endpoint, json=payload, headers=headers, timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]   # <-- the shared response path
    except Exception as e:
        import traceback; traceback.print_exc()
        return None

reply = chat_completion(
    base_url="http://localhost:11434/v1",   # local Ollama; swap to point anywhere
    model="llama3.2",
    messages=[{"role": "user", "content": "In one sentence, what does a chess coach do?"}],
)
print(reply)
```

---

## Model 2: Same Prompt, Three Response Shapes

The request bodies are nearly identical; the **auth** and the **reply location** differ. That table is the entire practical difference a developer must remember:

| | Anthropic | OpenAI | Open WebUI / Ollama |
|---|---|---|---|
| **URL** | `api.anthropic.com/v1/messages` | `api.openai.com/v1/chat/completions` | `<baseUrl>/api/chat/completions` |
| **Auth header** | `x-api-key: <key>` + `anthropic-version` | `Authorization: Bearer <key>` | `Authorization: Bearer <key>` *(optional)* |
| **Prompt goes in** | `messages: [{role, content}]` | `messages: [{role, content}]` | `messages: [{role, content}]` |
| **Reply text is at** | `data.content[].text` | `data.choices[0].message.content` | `data.choices[0].message.content` |
| **Needs a paid key?** | Yes | Yes | No (local model) |

### Critical Thinking Questions

4. A student copies the OpenAI branch, changes the URL to Anthropic's, and keeps `Authorization: Bearer <key>` and `data.choices[0].message.content`. Predict the two distinct failures they will hit and how each would appear at runtime.

   > *Hint: (1) Auth: Anthropic ignores `Authorization` and wants `x-api-key` plus `anthropic-version`, so the request is rejected with an auth/version error before any reply. (2) Parsing: even with a valid reply, `choices` does not exist on an Anthropic response (the text is under `content[].text`), so `choices[0]` throws. Same lesson as the REST activity's "empty response" bug, one layer up.*

5. The Open WebUI branch and the OpenAI branch parse the response with the **same** `extractOpenAIText` helper. What property of Open WebUI makes that reuse correct, and what would you have to change to add a provider that does *not* share it?

   > *Hint: Open WebUI is OpenAI-compatible; it returns the same `choices[0].message.content` structure. A non-compatible provider (like Anthropic) needs its own parse branch, which is exactly why the Anthropic branch has its own `content[].text` line instead of calling `extractOpenAIText`.*

6. `callTextModel` throws a specific `Error` (e.g. "Enter an Anthropic API key.") before it ever calls `fetch` when the key is missing. Why check first instead of letting the provider return a 401?

   > *Hint: A local guard gives a clear, instant, actionable message and avoids a pointless network round-trip (and a confusing provider-specific error body). Validate what you can locally; only spend a network call on things only the server can decide.*

In a response from `POST https://api.anthropic.com/v1/messages`, where is the model's reply text?

[( )] `data.choices[0].message.content`
[(X)] `data.content[0].text` (an array of content blocks)
[( )] `data.output_text` only
[( )] `data.message.content`

> **Common Misconception:** "If it's the same prompt, it's the same response object." No. Providers agree on very little beyond "send messages, get a completion." The **request** can look almost identical while the **response shape** and the **auth headers** differ. Write one small parse function per response family (OpenAI-style, Anthropic-style) and route to the right one; never assume `choices[0]` exists.

---

# Part III: Prompt Engineering and Structured Output for Coaching

Now that the pipe exists, what do we push through it? Two different jobs: **prose commentary** (free text a human reads) and **structured values** (JSON the program uses to drive a meter or a badge). They demand different prompting.

## 7. The Coach Commentary Prompt

`getAICommentary` builds the prompt that produces the sentence-or-two after each move. Read how much context it assembles, and the guardrails it sets:

## Code Cell

```js
async function getAICommentary(providerConfig, beforeFen, afterFen, san, pgnSoFar, eloEst) {
  const prompt = `You are an expert chess coach. The player is White (estimated ~${eloEst} Elo).

You are analyzing the move that was just played, in the context of the entire game so far.

Full PGN so far (ending with the move being analyzed):
${pgnSoFar || "(opening)"}

Position BEFORE the move (FEN):
${beforeFen}

Move just played:
${san}

Position AFTER the move (FEN):
${afterFen}

Analyze ONLY the move just played, but do so in the context of the whole game so far.
Judge whether it is good, inaccurate, a mistake, or a blunder.
If it is suboptimal, name a better move for this turn and explain why.
Do NOT mention, predict, recommend, or hint at any future moves, replies, or continuations.
Keep the answer to 2-4 sentences.
Be encouraging but honest.`;

  return callTextModel(providerConfig, prompt, { maxTokens: 350, temperature: 0.2 });
}
```

Design decisions worth copying:

- **Role framing first** ("You are an expert chess coach") sets the voice.
- **Concrete state, not vibes**: it passes the FEN *before* and *after*, the move in SAN, and the whole game's PGN. The model reasons about the actual position, not a vague description.
- **Explicit scope limits**: "Analyze ONLY the move just played" and "Do NOT predict future moves." Without these, models happily volunteer whole opening lines, which would spoil the game and often be wrong.
- **A length cap and a low `temperature` (0.2)**: coaching should be steady and repeatable, not creative.

You can prove the prompt matters with a runnable cell, the same coach prompt, against your local model:

## Code Cell

```python
# Reuses chat_completion(...) from Part II.
fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"  # after 1.e4 e5
coach_prompt = f"""You are an expert chess coach. Analyze ONLY the move just played, in 2-3 sentences.
Position after the move (FEN): {fen}
Move just played: e5
Judge it as good, inaccurate, a mistake, or a blunder. Do not predict future moves."""

print(chat_completion(
    base_url="http://localhost:11434/v1", model="llama3.2",
    messages=[{"role": "user", "content": coach_prompt}],
))
```

## 8. Structured Output: Asking for JSON You Can Use

The evaluation bar and the Elo meter cannot use a paragraph; they need a **number**. So those prompts demand JSON and the code parses it. Here is the evaluation call, start to finish:

## Code Cell

```js
async function getAIEvaluation(providerConfig, fen) {
  const prompt = `You are a chess engine. Given this FEN, estimate the evaluation from White's` +
    ` perspective as a single number (positive = White advantage, negative = Black advantage).` +
    ` Respond ONLY with a JSON object like {"eval": 0.5} where the number is in pawns. FEN: ${fen}`;

  const text = await callTextModel(providerConfig, prompt, { maxTokens: 120, temperature: 0 });

  // Models often wrap JSON in ```json fences or add stray words. Strip fences, then parse safely.
  const parsed = safeJsonParse(text.replace(/```json|```/g, "").trim(), {});
  return typeof parsed.eval === "number" ? parsed.eval : 0;   // fall back to 0 if anything is off
}

function safeJsonParse(text, fallback) {
  try { return JSON.parse(text); } catch { return fallback; }
}
```

Three defenses stacked together make this robust:

1. **Ask precisely**: "Respond ONLY with a JSON object like `{"eval": 0.5}`" and `temperature: 0`.
2. **Clean the text**: strip ```` ```json ```` fences the model may add.
3. **Never trust the parse**: `safeJsonParse` returns a fallback instead of throwing, and the code then checks that `parsed.eval` is actually a number before using it.

The Elo estimator (`getSideAIElo`) does the same for `{"elo": 1200, "label": "Intermediate"}`, with `parsed.elo || 1200` and `parsed.label || "Unknown"` as fallbacks.

## 9. Async Orchestration and the Stale-Closure Trap

After you move, the app wants **two** independent AI answers: commentary and a fresh Elo estimate. They don't depend on each other, so it fires them together with `Promise.all` and waits once:

## Code Cell

```js
const [c, elo] = await Promise.all([
  getAICommentary(currentProviderConfig, beforeFen, afterFen, san, pgnSoFar, eloEstimate.elo),
  getAIElo(currentProviderConfig, afterFen, newSans),
]);
setCommentary(c);
setEloEstimate(elo);
```

One subtlety specific to long-lived UI code: the move handler is an `async` function that may still be awaiting a slow API call when you change the provider dropdown. If it read the provider from the React render that created it, it could use **stale** settings. The app avoids this by reading the *current* config from a ref at call time:

## Code Cell

```js
const currentProviderConfig = providerConfigRef.current; // always the latest, even mid-await
const currentAIEnabled = aiEnabledRef.current;
// ...a useEffect keeps providerConfigRef.current in sync whenever the settings change.
```

---

## Model 3: Tracing One Move Through the AI Layer

You are White. You play `Nf3`. Walk the sequence the app performs (see `executeMove`).

| Step | What happens | Layer |
|---|---|---|
| 1 | `moveToSAN` names the move `"Nf3"`; `applyMove` produces the new state | Engine |
| 2 | UI updates instantly: piece moves, move list appends | React UI |
| 3 | If AI is enabled: `Promise.all` fires `getAICommentary` **and** `getAIElo` | AI layer |
| 4 | Each builds a prompt (FEN + SAN + PGN), calls `callTextModel` -> `fetch` | AI layer |
| 5 | Replies parsed (prose as text; Elo as JSON) and shown | AI layer |
| 6 | The **local** `minimax` picks Black's reply and the board updates | Engine |

### Critical Thinking Questions

7. Steps 1-2 (engine + UI) finish in well under a millisecond; steps 3-5 (AI) can take several seconds. The app updates the board *before* awaiting the AI. Why is that ordering a deliberate UX decision, not an accident?

   > *Hint: The move is already legal and known; there is no reason to make the human wait on a network call to see their own move. Render the certain, cheap result immediately; stream in the slow, uncertain AI result when it arrives. Never block a deterministic UI update on a probabilistic network call.*

8. `getAIEvaluation` strips ```` ```json ```` fences before calling `JSON.parse`. Give a concrete model output that would make `JSON.parse` throw *without* that strip, and explain why `safeJsonParse` still keeps the app alive even if the strip missed something.

   > *Hint: A reply like ` ```json\n{"eval": 0.3}\n``` ` is not valid JSON because of the fence lines; `JSON.parse` throws on the backticks. `safeJsonParse` wraps the parse in try/except and returns the fallback `{}`, so the app shows a neutral eval instead of crashing.*

9. Suppose the Elo call succeeds but returns `{"label": "Intermediate"}` with no `elo` field. What number ends up on the meter, and which line of code decided that?

   > *Hint: `parsed.elo || 1200` supplies `1200` when `elo` is missing/falsy. Defensive defaults on every field mean a partially-malformed structured response degrades to something sensible instead of `undefined` reaching the UI.*

Why does `getAIEvaluation` call `safeJsonParse` instead of `JSON.parse` directly?

[( )] `safeJsonParse` is faster than `JSON.parse`
[(X)] So a malformed or fenced model reply returns a fallback instead of throwing and breaking the render
[( )] Because the model can only output JavaScript objects, never strings
[( )] To convert the number from pawns to centipawns

> **Common Misconception:** "If I ask for JSON, I get JSON." Language models are *usually* obedient but never guaranteed. They add prose, wrap output in code fences, or drop a field. Treat every structured reply as untrusted input: constrain the prompt, strip known wrappers, parse defensively, and default every field. Robust structured output is 20% prompt and 80% parsing discipline.

---

# Part IV: Securing Your API Keys

This part is not optional polish; it is the difference between a safe project and a leaked credential that runs up someone else's bill. The rules are simple; the failures are expensive.

## 10. The Golden Rule: Never Commit or Hardcode a Key

A key like `sk-REPLACE_ME...` is a password. The two ways students most often leak one:

- **Hardcoding it** in the source: `const key = "sk-abc123..."`; now it's in your Git history forever, even if you delete it later.
- **Committing a config file** that contains it.

How the Chess AI Coach avoids both: the key is only ever **typed into a password field** and held in React state (`useState`) for the session. It is never written to disk, never hardcoded, and there is nothing to commit. Close the tab and it's gone. In a project with a build step, the equivalent discipline is: read keys from **environment variables** and add your `.env` file to **`.gitignore`** so it can never be committed.

## 11. The Client-Side Exposure Problem

Here is the uncomfortable truth about the app's Anthropic branch. It calls `api.anthropic.com` **directly from the browser**, and Anthropic makes you opt in with a header literally named:

```
anthropic-dangerous-direct-browser-access: true
```

The word "dangerous" is doing real work. When the browser makes the call, **the key travels from the user's browser and is visible in that browser's DevTools -> Network tab** on every request. Think about who can see it in each situation:

- **You, running the app locally, typing your own key**: fine. The key stays on your machine, in your browser, used only by you. This is the app's intended use.
- **You deploy the app to a public URL and hardcode your key so visitors don't need one**: a disaster. Every visitor can open DevTools and copy your key, then spend your money. **Never do this.**

`type="password"` on the input only hides the characters from someone looking over your shoulder. It does **nothing** to hide the key from the network layer or from other scripts on the page.

## 12. The Production Pattern: A Backend Proxy

For any app real users will touch, the key belongs on a **server you control**, never in the browser:

```
   Browser (no key)            Your backend (holds key)          Provider
  +---------------+   POST    +----------------------+  POST   +----------+
  |  chess UI     | --------> |  /api/coach          | ------> | Anthropic|
  |  fetch("/api")|           |  key = os.environ[...] |         | / OpenAI |
  `---------------+ <-------- `----------------------+ <------ `----------+
        reply                        reply
```

The browser calls **your** endpoint. Your server reads the key from an environment variable and adds it to the provider request. The secret never leaves your server; users never see it; and you can add rate limits and logging in one place. A minimal proxy is only a few lines:

## Code Cell

```python
# minimal_proxy.py  - run with a real key in the environment, e.g.
#   export PROVIDER_API_KEY="sk-...."   (never commit this)
import os, requests
from flask import Flask, request, jsonify

app = Flask(__name__)
API_KEY = os.environ["PROVIDER_API_KEY"]  # <-- from the environment, NOT the source code

@app.post("/api/coach")
def coach():
    user_prompt = request.get_json()["prompt"]
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},   # key added server-side
        json={"model": "gpt-4.1-mini",
              "messages": [{"role": "user", "content": user_prompt}]},
        timeout=120,
    )
    data = r.json()
    return jsonify({"text": data["choices"][0]["message"]["content"]})
```

The **local-model escape hatch** sidesteps the whole problem: point the app at Open WebUI / Ollama and there is *no cloud key to leak*. That is a big reason this course leans on local models, and why the app supports them as a first-class provider.

---

## Model 4: Where Should the Key Live?

Three deployment scenarios. For each, decide where the key should live.

| Scenario | Who uses it | Safe place for the key |
|---|---|---|
| A. You experiment on your own laptop | Only you | In the browser session (typed into the field), fine |
| B. A shared classroom instance for 20 students | Many people | On a backend, **or** use a keyless local model |
| C. A public website anyone can visit | The whole internet | On a backend proxy; **never** in the browser |

### Critical Thinking Questions

10. In scenario C, a teammate suggests "we'll just obfuscate the key by base64-encoding it in the JavaScript so nobody can read it." Explain precisely why this does not work.

    > *Hint: Anything the browser can decode to make the request, an attacker can also decode; the browser must send the real key over the wire, so it appears decoded in the Network tab regardless of how it was stored in the source. Obfuscation is not encryption; the secret still reaches the client. The only fix is to not send the secret to the client at all.*

11. Scenario B has two safe options. Compare them: what does the backend-proxy option buy you that the keyless-local-model option does not, and vice versa?

    > *Hint: The proxy lets you use powerful cloud models while centralizing the key, rate limits, and logging, at the cost of running a server and paying per call. The local model needs no key and no per-call cost and keeps data on-premises, at the cost of hardware and (often) lower capability. Different tradeoffs, both avoid a client-side secret.*

12. The app stores the key in `useState`, not in `localStorage`. Why is that a safer default for a browser app, even for personal use?

    > *Hint: `useState` lives only in memory for the tab's lifetime, so the key vanishes when the tab closes and never persists to disk where other scripts or a shared machine's next user could read it. `localStorage` would survive restarts and be readable by any script on the origin, more exposure for no real benefit here.*

In a safe public deployment, where does the provider API key live?

[( )] In the JavaScript, base64-encoded so it's hard to read
[( )] In the browser's `localStorage`, cleared on logout
[(X)] On a backend server you control, read from an environment variable
[( )] In a hidden HTML input with `type="password"`

> **Common Misconception:** "`type='password'` protects the key." It only masks the characters on screen. The key is still in memory, still sent over the network in plain view of the Network tab, and still readable by any script on the page. Masking ≠ protecting. The real protections are: keep the key off the client entirely (backend proxy) or use a provider that needs no key (local model).

---

# Part V: Wiring the AI into the User Interface

The final layer is glue: React state that holds the provider settings (never keys in code), and the move handler that decides *whether* and *when* to call the model.

## 13. Provider Config State and `executeMove`

The provider settings are ordinary React state (a dropdown value plus the relevant fields), assembled into `providerConfig` and handed to the AI functions. The move handler branches on whether AI is configured:

## Code Cell

```jsx
// Is any provider actually ready to use?
const aiEnabled =
  (provider === "anthropic" && !!anthropicKey.trim()) ||
  (provider === "openai"    && !!openaiKey.trim()) ||
  (provider === "openwebui" && !!openWebUIUrl.trim() && !!openWebUIModel);

// Inside executeMove, after the move is already applied and drawn:
if (currentAIEnabled) {
  setCommentaryLoading(true);
  try {
    const [c, elo] = await Promise.all([ getAICommentary(...), getAIElo(...) ]);
    setCommentary(c);
    setEloEstimate(elo);
  } catch (e) {
    setCommentary(`AI request failed: ${e.message}`); // errors become visible, not silent
  } finally {
    setCommentaryLoading(false);
  }
} else {
  setCommentary(`You played ${san}. Configure a provider for AI analysis.`);
}
```

Notice the `try/catch/finally`: a failed API call turns into a **visible message** and the loading spinner always clears. Silent failures are the worst failures in AI features, because the user can't tell "the model is thinking" from "the model is broken."

## 14. Graceful Degradation, One More Time

Because `aiEnabled` gates every model call, the app has a complete fallback path:

- **Evaluation bar**: `getAIEvaluation` when enabled; local `evaluate()` otherwise.
- **Commentary**: model prose when enabled; a plain "you played Nf3" note otherwise.
- **Play**: always the local engine, never touched by the AI at all.

This is the template for adding AI to *any* existing app: **make the app fully work without the model first, then layer the model on as an enhancement that fails safe.**

---

## Exercises

1. *Add a fourth provider.*

   - *What to do*: Add a new branch to `callTextModel` for another OpenAI-compatible server (for example a second local endpoint, or a hosted gateway). Reuse `extractOpenAIText` for parsing. Add it to the provider `<select>` and the `aiEnabled` check.
   - *Starter hint*: Copy the `openwebui` branch, change the base URL source, and add `<option value="myprovider">`. Because it's OpenAI-compatible, the response parse is unchanged; that's the payoff of the dispatcher pattern.
   - *You've succeeded when*: Selecting your new provider and making a move produces commentary, and **no code outside `callTextModel`, the dropdown, and `aiEnabled` had to change.**

2. *Add a structured-output feature.*

   - *What to do*: Write `getOpeningName(providerConfig, pgnSoFar)` that asks the model to name the opening and return `{"opening": "...", "confidence": 0.0-1.0}`. Parse it with the strip-fences-then-`safeJsonParse` pattern and display it above the board.
   - *Starter hint*: Model your prompt on `getAIEvaluation`: demand JSON with an example, use `temperature: 0`, strip fences, and default both fields (`parsed.opening || "Unknown"`, `parsed.confidence ?? 0`).
   - *You've succeeded when*: A recognizable opening (e.g. after `1. e4 e5 2. Nf3`) is named, and a garbled reply shows "Unknown" instead of crashing the app.

3. *Swap the coach's persona.*

   - *What to do*: Change the role sentence in `getAICommentary` (e.g. "You are a terse grandmaster" vs. "You are a warm beginner-friendly coach") and compare the commentary on the same three moves.
   - *Starter hint*: Only the first line of the prompt needs to change. Keep the scope guardrails ("analyze only this move; no future moves") so the comparison is fair.
   - *You've succeeded when*: You can describe, with examples, how the persona line changed tone and detail without changing correctness.

4. *Move the key server-side.*

   - *What to do*: Stand up the `minimal_proxy.py` from Part IV (or a Node equivalent), set the key in an environment variable, and add a fifth provider branch whose base URL is your proxy, so the browser sends **no key at all**.
   - *Starter hint*: The browser branch becomes `fetch("http://localhost:5000/api/coach", { method: "POST", body: JSON.stringify({ prompt }) })`. Confirm in DevTools -> Network that no key appears on the browser request.
   - *You've succeeded when*: Commentary works, and inspecting the browser's outgoing request shows a prompt but **no API key** anywhere.

---

## Reflection Prompt

*Personal*: Before reading this app, did "the AI analyzed my move" feel like magic? Now that you have seen it is an HTTP POST with a carefully worded prompt and a defensive JSON parse, has your sense of what these features *are* changed? What still feels non-obvious?

*Technical*: In your notebook, design the configuration and secret-handling for a version of this app that your whole class could use at once. Where does the key live? Which provider(s) do you support and why? Sketch the request path from a student's browser to the model and back, and mark every place a secret must **not** appear.

*Societal*: The app estimates a player's Elo from their moves and shows it back to them in real time. What are the risks of software that continuously scores a person's skill and reports it? Who might be discouraged or misjudged by a wrong estimate, and what responsibilities does a developer have when a model's confident-looking number is actually a rough guess?

---

## -> Coming Up Next

You now have the full pattern for adding a language model to real software: isolate the AI layer, dispatch across providers, engineer prompts for prose and for structured JSON, parse defensively, and keep secrets off the client. In the **Build Your Own AI Coach** lab you will apply exactly this pattern to a domain of your choosing (a simpler game, a writing tutor, a code reviewer), reusing the provider-agnostic call, the structured-output discipline, and the key-security rules you practiced here.

---

## Further Reading

- Anthropic. "Messages API Reference." *docs.anthropic.com*. The `/v1/messages` endpoint, the `x-api-key`/`anthropic-version` headers, and the `content[]` block response shape used in the Anthropic branch.
- OpenAI. "Chat Completions API Reference." *platform.openai.com/docs/api-reference/chat*. The `/v1/chat/completions` request and the `choices[0].message.content` response reused by the OpenAI and Open WebUI branches.
- Open WebUI. *Open WebUI Documentation*. `docs.openwebui.com`. The OpenAI-compatible `/api/chat/completions` and `/api/models` endpoints the local branch targets.
- OWASP. "Secrets Management Cheat Sheet." *cheatsheetseries.owasp.org*. Why secrets must not ship to clients, and the backend-proxy pattern from Part IV.
- Prior activity: [RESTful LLM Access: The api/v1 Paradigm](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-restllmapi.md). The Python foundation this activity builds on.
