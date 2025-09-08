---
layout: assignment
permalink: Labs/CustomChatbot
title: "Lab: Custom Chatbot"

info:
  points: 100
  goals:
    - Explain the role of system instructions (a.k.a. “system prompts”) in shaping a chatbot’s behavior and outputs.
    - Customize a “classic” hosted chatbot (ChatGPT) using Custom Instructions to control role, tone, boundaries, and safety.
    - Translate the same persona and guardrails into a local Python chatbot powered by Ollama and an open model.
    - Compare behavior across platforms using a small, task-oriented evaluation protocol and error analysis.
    - Instrument your Python chatbot with configuration files, logging, and reproducible runs.
    - Reflect on ethical, privacy, and safety considerations when deploying persona-constrained chatbots.
  rubric:
    - weight: 30
      description: Implementation
      preemerging: Provides a working hosted (ChatGPT) customization and a minimal Python+Ollama chatbot; basic instructions to run.
      beginning: Both versions follow the stated persona; Python app loads a system prompt from config and maintains multi-turn state.
      progressing: Adds guardrails (e.g., content checks/refusals), configurable parameters (temperature/model), and transcripts/logging.
      proficient: Robust implementation with clean CLI, modular design (prompt loader, safety layer, logger), and reproducible runs on sample tasks.
    - weight: 30
      description: Behavioral Correctness, Prompting & Reasoning
      preemerging: Explains the intended behavior and provides a few example interactions.
      beginning: Shows that the persona, tone, and boundaries are realized on typical tasks; includes brief rationale for design choices.
      progressing: Uses a structured evaluation set with pass/fail criteria and error taxonomy; iterates on prompt to reduce failure modes.
      proficient: Presents principled prompting (role, objectives, constraints, demonstrations), insightful failure analysis, and explains trade-offs (e.g., creativity vs. consistency).
    - weight: 20
      description: Code Quality and Documentation
      preemerging: Readable code with comments and a short README.
      beginning: Functions/modules with docstrings; configuration separated from code (e.g., YAML/JSON system prompt).
      progressing: Consistent style, clear abstractions (chat loop, safety filter, logger), and inline rationale for nontrivial choices.
      proficient: Clean architecture with tests or checks; well-documented configuration, dependencies, and reproducibility notes.
    - weight: 10
      description: Design Report
      preemerging: Summarizes goals, approach, and basic results.
      beginning: Justifies prompt structure and guardrails with examples.
      progressing: Details experiments, limitations, and comparisons across platforms with supporting tables/figures.
      proficient: Concise, well-structured report with justified choices, ethical reflection, and prioritized future work.
    - weight: 10
      description: Submission Completeness
      preemerging: Required artifacts present; minimal run instructions.
      beginning: All artifacts with clear run steps and parameters.
      progressing: Includes scripts/configs, sample data, and transcripts for both platforms.
      proficient: Fully reproducible package with seeds (if applicable), config snapshots, and verification notes.

tags:
  - ai
---

# Overview

In this lab you will (1) **shape** the behavior of a classic hosted chatbot by changing its system-level instructions, and (2) **recreate** the same persona locally in Python using **Ollama** and an open model. You will then **evaluate** and **reflect** on differences in controllability, safety, and fidelity across platforms.

---

## Part A — Customize a “classic” chatbot (ChatGPT)

> Goal: Use system-level instructions to create a persona-constrained assistant and validate its behavior on representative tasks.

### A1. Access and where to edit instructions

- **ChatGPT Custom Instructions.** In ChatGPT, open the user menu ➝ **Custom Instructions**. The two fields (“What would you like ChatGPT to know about you” and “How would you like it to respond”) act as a persistent pre-amble that conditions responses in new chats.  
- (Optional) **Projects** provide per-project instructions that supersede your global Custom Instructions. Useful if you keep course work separate from personal settings.

> If students lack ChatGPT access, you may substitute the OpenAI Playground’s **System message** field in a new chat; the concept is the same (hosted system pre-amble).

### A2. Draft a first persona (system instructions template)

Create a new document `system_prompt.md` and draft your initial instructions using the following scaffold:

```
Role & Identity
- You are "<assistant name>", a <domain> assistant for <audience>. You are <tone> (e.g., concise, supportive), and you never <forbidden behavior>.

Objectives
- Primary: <what the assistant is optimizing for>.
- Secondary: <nice-to-haves>.

Boundaries & Safety
- Decline: <topics or requests to refuse>.
- Red Team Notes: watch for <prompt-injection patterns>, <hallucination risks>, <privacy issues>.
- If unsure: ask one clarifying question, then proceed cautiously.

Style & Format
- Default style: <paragraph/bullets/code>.
- Output format when asked for code: fenced code blocks; include minimal runnable example.
- Cite assumptions explicitly and list any limitations at the end.

Working Norms
- Always show step-by-step reasoning **privately**; present only final, concise answers to the user.
- When refusing: provide a brief rationale and a safe alternative.
- Keep responses under <N> tokens unless asked for more.

Demonstrations (few-shot)
- User: <short, representative request #1> 
- Assistant: <ideal response #1>
- User: <short, representative request #2>
- Assistant: <ideal response #2>
```

Paste an adapted version into ChatGPT **Custom Instructions** (“How would you like it to respond?”). Keep a copy in your repository as the source of truth.

### A3. Quick validation protocol (hosted)

In a fresh chat (so your new instructions apply), run **three tasks** that exercise the persona:

1. **On-distribution**: a task your assistant should excel at.
2. **Boundary test**: a request it should **refuse** or safely reframe.
3. **Ambiguity**: a task requiring clarifying questions.

Save the conversation transcripts (copy/paste or export) as `hosted_runs/*.md`. Note failures, confusions, or style drift.

---

## Part B — Build the same chatbot locally in Python with Ollama

> Goal: Implement a local, reproducible chatbot that loads your `system_prompt.md`, maintains dialogue state, and enforces basic guardrails.

### B1. Install and verify Ollama

- **Install** Ollama for your OS (macOS, Linux, Windows). After installation, Ollama runs a local server on `localhost:11434`.  
- **Pull a model**, e.g., a small Llama or Gemma variant that fits your machine:
  ```bash
  ollama pull llama3.1:8b
  # or
  ollama pull gemma2:2b
  ```

### B2. Python environment

Create a virtual environment and install the client:

```bash
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install --upgrade pip ollama
```

### B3. Minimal, configurable chat loop (starter)

Create `chatbot.py`:

```python
import argparse, time, json, pathlib
import ollama

def load_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")

def now_ms() -> int:
    return int(time.time() * 1000)

def main():
    p = argparse.ArgumentParser(description="Local persona chatbot (Ollama)")
    p.add_argument("--model", default="llama3.1:8b", help="Ollama model tag")
    p.add_argument("--system", default="system_prompt.md", help="Path to system instructions")
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--log", default="runs/local_log.jsonl", help="Transcript log path")
    args = p.parse_args()

    system_prompt = load_text(pathlib.Path(args.system))
    messages = [{"role": "system", "content": system_prompt}]

    pathlib.Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    print("Type /exit to quit.\n")

    while True:
        user = input("You: ").strip()
        if user.lower() in {"/exit", "quit", "q"}:
            break

        # Basic safety prefilter (example: block PII or disallowed topics)
        if any(term in user.lower() for term in ["social security", "ssn", "credit card"]):
            print("Bot: I can’t assist with sensitive personal data. Please revise the request.")
            continue

        messages.append({"role": "user", "content": user})

        t0 = now_ms()
        resp = ollama.chat(
            model=args.model,
            messages=messages,
            options={"temperature": args.temperature},
        )
        dt = now_ms() - t0
        reply = resp["message"]["content"]

        print(f"Bot ({dt} ms): {reply}\n")
        messages.append({"role": "assistant", "content": reply})

        # Append structured log
        with open(args.log, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "ts": t0, "ms": dt, "model": args.model,
                "exchange": {"user": user, "assistant": reply}
            }) + "\n")

if __name__ == "__main__":
    main()
```

### B4. Reproducible runs

1. **Warm-up**:  
   ```bash
   ollama run llama3.1:8b -p "Say hello."
   ```
2. **Run your bot**:  
   ```bash
   python chatbot.py --model llama3.1:8b --temperature 0.2
   ```
3. **Collect transcripts** from at least **10 prompts** across three categories (on-distribution, boundary, ambiguity). Save the resulting `runs/local_log.jsonl`.

---

## Part C — Prompt engineering & guardrails (both platforms)

### C1. Strengthen your system prompt

Iterate on your `system_prompt.md` to include:

- **Role/Objective**: who you are and what you optimize.
- **Constraints/Refusals**: topics you will not cover and how to redirect.
- **Style Contract**: formatting rules (e.g., code fences, citations, brevity).
- **Few-shot demonstrations** to anchor behavior on tricky intents.

For hosted ChatGPT, encode this in **Custom Instructions**; for Python, keep `system_prompt.md` as your single source of truth (copied verbatim into the `system` role).

### C2. Add a basic safety layer (Python)

Extend the pre-filter to catch:
- Prompt-injection markers (e.g., “ignore previous instructions”).
- Disallowed topics (define your own list).
- Potential PII patterns (simple regexes).

On match, return a **brief refusal** plus a **safe alternative** that still helps the user.

---

## Part D — Evaluation & error analysis

1. **Mini-benchmark.** Create a CSV or Markdown table with at least **12 prompts** spanning:
   - 6 **core** tasks (what your persona should excel at),
   - 3 **boundary** tests (should refuse or reframe),
   - 3 **ambiguity** tests (should ask a clarifying question first).

2. **Run on both systems** (hosted ChatGPT and local Python). Record outputs, latency (rough timing is fine), and any violations of the style/constraints contract.

3. **Analyze**:
   - Where did behavior diverge? (e.g., verbosity, refusal style, hallucinations)
   - Did your guardrails trigger appropriately?
   - What prompt edits improved outcomes? (Show before/after diffs for two cases.)

Include a **one-page report** with a table summarizing pass/fail per item and short rationales.

---

## What to Submit

1. **Code & Config**
   - `chatbot.py` (or Jupyter notebook)
   - `system_prompt.md` (the same text used in both platforms)
   - `requirements.txt` (e.g., `ollama`)

2. **Transcripts**
   - Hosted ChatGPT (`hosted_runs/*.md`)
   - Local Ollama (`runs/local_log.jsonl`)

3. **Design Report** (PDF or Markdown, ~1–2 pages)
