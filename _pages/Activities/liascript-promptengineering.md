<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-promptengineering.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-promptengineering.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Prompt Engineering as Agent Design: System Prompts, Personas, and Comparing Models

In *The Agent Loop: Perceive, Plan, Act*, two-thirds of our calculator agent's design lived in one string: its system prompt.  A prompt is not a question.  It is a **program written in natural language**, and it configures the agent's behavior.  Today moves from the anatomy of a prompt, to the core patterns, to personas and system prompts, to the policy of your own agent, and then to a fair comparison of two models on the same prompt.  In an agentic system the system prompt *is* the agent's job description.  It is also the frame that the OpenCode Studio lab's Part 2 (the agent contract and the system prompt) has been waiting for: that part starts after today, and your Signed Team Charter is due today as well.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| System prompt | The standing instructions given to a model before any user message; it sets the agent's role, allowed actions, output format, and limits | The ROLE / GOAL / TOOLS / FORMAT / GUARDRAILS template used in Exercise 1 |
| Persona | A named identity and expertise frame assigned to the model in the system prompt.  It shifts the style and tone of the outputs without changing what the model knows | The "patient tutor," "careful fact-checker," and "json_bot" identities compared in Model 2 |
| Few-shot example | One or more sample input-output pairs placed in the prompt to show the model what the desired output looks like, instead of only describing it | Two examples of "date inside a sentence -> ISO 8601 string," so the model learns the pattern by demonstration |
| Chain-of-thought | A prompting pattern that asks for intermediate steps before the answer.  It buys computation, not carefulness: each emitted token is another forward pass with the earlier steps readable | "Think step by step" on a multi-step task, and why it is redundant on a model already trained to do it |
| Output structuring | Naming a machine-readable format (such as JSON) in the prompt so that downstream code can parse and act on the response | The `json_bot` persona that returns `{"answer": ..., "confidence": ...}` |
| Guardrail | An explicit instruction in the system prompt that tells the agent what to refuse, escalate to a human, or handle with extra care | "If asked for medical advice, always recommend consulting a licensed professional" |
| Temperature | A sampling setting that decides how much the model varies its wording.  At 0 it takes the single most likely word every time; higher values let less likely words through | `temperature=0.0` in the Section 5 harness and in Model 4 |
| Seed | The starting number for the random draw.  The same seed with the same prompt and settings replays the same draws, so a run can be repeated exactly | `seed=42` in the Section 5 harness and in Model 4 |
| Top-p | A sampling setting that keeps only the most likely words until their combined probability reaches p, and drops the rest before the draw | Named in Part IIc; the *Sampling and Temperature* tutorial works the numbers |

---

### Before You Start

**You need:** Ollama running with `llama3.2` pulled, from *Running Your Own AI*, and Python with `requests`.  Part IIc also uses a second model of a different size.  If you did not pull one during that session, start this now, because it takes a few minutes:

```bash
ollama pull llama3.2:1b
```

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-8 | Key Concepts, and the recipe framing for what a system prompt actually is |
| 8-25 | Part I, the anatomy of a prompt, worked against a live model, including what chain-of-thought buys |
| 25-40 | Part II, personas in practice, then the golden-set harness that scores a prompt |
| 40-52 | Part IIb, where personas leak and how to write one that holds up |
| 52-70 | Part IIc, the three sampling dials in plain terms, then the same prompt on two models |
| 70-75 | Report-out and the reflection prompt.  Part IIb's critique table and Part IIc's comparison table finish at home if we run short |

---
# Part I: The Anatomy of a Prompt

A prompt is a structured program in natural language, and small changes to its wording produce large changes in the agent's behavior.  By the end of this part you will be able to name every behavioral commitment in a prompt before you run it.

## 1.  Three Channels of Instruction

Sending a message to an agent is like sending a letter to an office.  The **system prompt** is the standing policy manual every employee carries, the **user message** is the letter you wrote today, and the **conversation history** is the file of everything said before.  The model reads all three, and a well-trained model treats the system prompt as rules that no single letter can override.  The analogy stops at enforcement: nothing inside the model forces the policy to win, and Part IIb shows where it leaks.

In more precise terms, modern chat models receive layered instructions.  The system prompt establishes the durable role, constraints, and format.  The user message carries the immediate task.  The conversation history carries everything either party has said.  The model conditions on all three, but weights the system prompt as standing policy:

$$
P(\text{response} \mid \text{system}, \text{history}, \text{user})
$$

For an agent, the system prompt is the constitution.  It declares the agent's goal, its allowed actions, its output format, and its boundaries.  When we built the calculator agent, two-thirds of the design lived in that one string.

---

## Model 1: Two Prompts, Two Agents

Compare two job postings.  One says only "engineer wanted."  The other lists the role, the required skills, the deliverables, and the tone of client communication.  The second produces far more predictable work, and work you can evaluate.  Prompts behave the same way.

| Feature | Prompt A | Prompt B |
|---------|----------|----------|
| Full text | "Tell me about photosynthesis." | "You are a patient biology tutor for first-year students. Use one everyday analogy, then a three-sentence technical explanation, then ask the student one check-for-understanding question. Topic: photosynthesis." |
| Audience specification | Not specified; the model must guess | Explicitly set to first-year students, which shifts vocabulary and assumed background |
| Output structure | Unconstrained: any length, any format | Three-part structure (analogy, explanation, question) makes the output predictable and auditable |
| Evaluability | Hard to score: what counts as a good explanation? | Easy to score: does it have an analogy? Three sentences? A question at the end? |
| What changes if we swap the topic | Everything may change unpredictably | Only the topic content changes; structure and tone remain consistent |

### Critical Thinking Questions

1.  List every behavioral commitment Prompt B makes that Prompt A leaves to chance.

   > *Hint: Go through Prompt B word by word and ask: does this constrain length, tone, structure, audience, or format?  Every constraint is a behavioral commitment.*

2.  Which prompt makes the output easier to *evaluate*?  Why does specifying the format make quality measurable?

   > *Hint: If you wanted to write a program that checks whether the response is good, what would it look for in Prompt A's output versus Prompt B's output?*

3.  Prompt B constrains tone and structure but not correctness.  What would you add to the prompt to push the model toward factual accuracy?

   > *Hint: Think about what the model does when it is uncertain.  Could you instruct it to signal uncertainty?  Could you ask it to cite a source?*

4.  Rewrite Prompt B for a different audience: a graduate seminar or a fifth grader.  Which elements of the prompt changed, and which held across audiences?

   > *Hint: Start with an exact copy of Prompt B and modify only what you must.  The elements you did not need to change are the durable ones.*

---

## 2.  Core Prompting Patterns

The community has settled on a small set of reliable patterns, and we reuse each of them all semester.  **Role and persona** assigns an identity and an expertise frame.  Few-shot examples show the desired input-output mapping instead of describing it.  Chain-of-thought requests intermediate reasoning before the answer, like asking someone to show their work.  Output structuring demands a machine-readable format such as JSON, which is what lets a *program* act on a model's response.  Constraints and refusals state what the agent must not do.

A practical agent system prompt composes several patterns:

```
ROLE: who the agent is and for whom it works
GOAL: what done looks like
TOOLS: actions it may take, with exact syntax
FORMAT: the exact output schema
GUARDRAILS: what it must refuse or escalate to a human
```

An agent must return JSON so that downstream code can parse its decision.  The most reliable prompting approach is:

[( )] Ask politely for JSON at the end of the user message
[( )] Raise the temperature so the model explores formats
[(X)] Specify the exact schema in the system prompt and include a few-shot example of a valid response
[( )] Avoid mentioning JSON so the model is not confused

> *On the second option: that is the temperature dial you turned in *Running Your Own AI*, Section 3c.  Recall what raising it actually did to your six answers, then ask yourself whether "explores formats" is a thing you want from a value your code has to parse.*

---

### Asking for Steps Versus Being Trained to Take Them

Chain-of-thought belongs on the pattern list above, and it is the one pattern on that list whose story changed.  Spend thirty seconds on it now so that you do not overtrust it for the rest of the semester.

Showing work buys computation, not carefulness.  A model produces one distribution per forward pass.  Asking for intermediate steps makes it emit more tokens, and each token is another pass with everything written so far available to read.  The steps *are* the computation, not a description of it.  *Why Different Answers Every Time?* works through the mechanism.

The prompt stops being enough at checking.  You can ask a standard model to check its work, and it usually will, in form.  It will also, quite often, confirm its original mistake in a fluent paragraph, because it is imitating what checking looks like rather than being rewarded for catching anything.  A **reasoning model** is trained differently: reinforcement learning against problems that can be checked automatically, where the reward lands on runs that *end correct*.  That training is what makes backtracking, noticing a contradiction, and abandoning an approach reliable instead of merely requestable.

The honest summary of the pattern is two lines, and the second is the one that gets forgotten:

> **Prompting can request a behavior.  Training is what makes it dependable.**

This has a practical consequence for the prompts you write today.  On a standard model, "think step by step" is worth adding to multi-step tasks and is close to free elsewhere.  On a reasoning model it is redundant at best, and provider guidance generally says not to bother; the model already does it, and your instruction competes with the training.  Neither one fixes a prompt that never said what "done" means, which is what Section 3 is about.

#### Critical Thinking Questions

5.  You add "think step by step, then check your answer" to a prompt on a standard local model.  Accuracy on your ten-item test set does not move, and the outputs are four times longer.  Give two different explanations consistent with that result, and say what you would measure next to tell them apart.

   > *Hint: Either the tasks did not need extra dependent steps (so the added computation had nothing to do), or the model performed checking as a genre without the training that makes a check catch anything, confirming its own errors at greater length.  To separate them, look at the items it got wrong.  If the reasoning is sound and the answer is still wrong, that points at the second.  If the reasoning is trivially short because the task was one step all along, that points at the first.  Splitting your test set by how many steps a human needs is the cheap version of this.*

---

## 3.  Plan Before You Prompt

The fastest way to a bad output is a rushed prompt.  Before you write the *final* prompt, spend a moment on the plan behind it.  This is the Description competency from the AI Fluency Framework (see the Welcome activity) in practice.  A reliable loop has three moves:

1.  **Ask and answer questions first.**  Instead of demanding an answer immediately, ask the model to *ask you* clarifying questions: "Before you write anything, ask me up to five questions that would change how you approach this."  Answering them surfaces assumptions (audience, scope, format, constraints) that you would otherwise discover only after a wrong draft.
2.  **Describe what success looks like.**  State the done-conditions up front, exactly as Prompt B did in Model 1 and as every exercise in this course states "*You've succeeded when...*".  If you can name what a good output contains (an analogy, three sentences, valid JSON, a citation), the model can aim at it and you can *check* it.  A goal you can evaluate is a goal you can hit.
3.  **Iterate on the plan and the prompt together.**  Treat the first response as a draft of the *plan*, not the final deliverable.  Refine the plan with the model over a few turns, and fold what you learn back into the prompt.  The prompt you finish with is almost never the prompt you started with.

This is the Delegation competency from the Welcome activity's at-home AI Fluency reading, put into practice: converse to define success, then plan the work before executing it.

> **Tip:** Plan, describe success, iterate.  Ask the model what it needs to know, tell it what "done" looks like, and refine both the plan and the prompt before you commit to a full run.

*This plan-first, describe-success, iterate practice draws on the Description competency of The AI Fluency Framework.  Copyright 2025 Rick Dakan, Joseph Feller, and Anthropic.  Released under the CC BY-NC-SA 4.0 license.*

---

# Part II: Personas in Practice

In this part you give three different persona instructions (identities assigned in the system prompt) to the same model and watch how each shifts the style and format of the output, without changing the model's weights at all.  Understanding personas helps you design agents that behave consistently, and it keeps you out of the trap of believing that a more authoritative persona produces more accurate answers.

## 4.  Personas Shape Distributions, Not Souls

Ask a knowledgeable friend the same question while they are in "professor mode" and again while they are texting a friend.  You get different vocabularies, different structures, maybe different levels of hedging, and the same underlying facts.  A model persona works the same way.  It shifts the *style* of the output by making certain patterns more likely; it does not give the model new knowledge.  The analogy stops at judgment: your friend knows which facts are true regardless of mode, and a model only knows which words are likely.

A persona does not create knowledge; it reweights it.  Telling a model it is a cautious pharmacist shifts its outputs toward the hedged, safety-conscious language in its training data.  That is powerful and potentially misleading, because a persona can also reweight toward confident-sounding error.  Pair a persona with *epistemic instructions* such as "say so when you are unsure," and then measure whether the model obeys them, which we do in Section 5.

---

The code cell below runs the same question ("Why is the sky blue?") through three different system prompts and prints each response.  Only the system prompt changes; the model, the question, and every other setting stay identical.

## Code Cell

> If you have not installed Ollama yet (we do it together in the *Running Your Own AI* session), read this cell and predict its output; bring your prediction to class.

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import requests

def chat(system, user, temperature=0.7, model="llama3.2"):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": temperature},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[promptengineering:chat] {e}")
        import traceback; traceback.print_exc()
        return ""

personas = {
    "tutor": "You are a patient tutor. Explain with one analogy, then ask one question.",
    "skeptic": "You are a careful fact-checker. State confidence (high/medium/low) for each claim.",
    "json_bot": 'Respond ONLY with JSON: {"answer": str, "confidence": "high|medium|low"}'
}

question = "Why is the sky blue?"
for name, system in personas.items():
    print(f"===== {name} =====")
    print(chat(system, question, temperature=0.3), "\n")
```

---

## Model 2: Persona Comparison

Run the cell (or examine the projected outputs) and compare the three responses to the identical question.

### Critical Thinking Questions

6.  Which differences across the three outputs are *formatting*, which are *tone*, and which (if any) are *substance* (different facts or claims)?

   > *Hint: Formatting is about structure: bullets, paragraphs, JSON fields.  Tone is about word choice and hedging.  Substance means the actual claims about the world changed.*

7.  The `json_bot` output is the only one a program can reliably consume.  Sketch the two lines of Python that would extract the confidence field, and say what happens if the model adds a single word of preamble before the JSON.

   > *Hint: Try `import json; data = json.loads(output); confidence = data["confidence"]`.  Now imagine the model outputs `Sure! {"answer": ..., "confidence": ...}`; which line of that code breaks and why?*

8.  Design a persona that would be actively harmful for a factual question like this one, and explain the mechanism of harm.  (Keep it classroom-appropriate; the goal is to reason about failure modes, not to produce harmful content.)

   > *Hint: Think about a persona that would make the model systematically overconfident, systematically misleading about a specific domain, or unwilling to express any uncertainty.*

> **Common Misconception:** Giving the model a more authoritative persona (for example, "You are a world-leading expert") does not make its answers more accurate.  Authority personas raise the model's *confidence* in its phrasing without improving the underlying facts, and they often suppress the model's natural hedging, which makes it harder to detect when it is wrong.  More authority in the persona can mean fewer useful uncertainty signals in the output.

---

## 5.  Eval-Driven Prompt Development

Model 1 argued that Prompt B is easier to *evaluate* than Prompt A.  Now we make that concrete.  We **measure** a prompt against a small set of known-answer examples, change the prompt, and watch the number move.  This is how prompts are improved in practice: not by taste, but against a golden test set, a fixed list of `input -> expected-output` pairs you score automatically.

The cell below defines five `(country, expected capital)` pairs, then runs the *same* test set through two system prompts: a vague one and a specific, format-constrained one.  Because the score uses exact match, the vague prompt's full-sentence answers fail while the specific prompt's one-word answers pass.  That accuracy gap is the *evidence* that one prompt is better for this task.

## Code Cell

> If you have not installed Ollama yet (we do it together in the *Running Your Own AI* session), read this cell and predict its output; bring your prediction to class.

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import requests

# temperature=0.0 pins the wording (Running Your Own AI, Section 3c).
# seed=42 pins the random draw itself: any fixed number works, the same one
# every run means the same dice rolls every run. Together they make this
# harness repeatable, which is what lets a test tell you something.
def chat(system, user, temperature=0.0, seed=42, model="llama3.2"):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": temperature, "seed": seed},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[promptengineering:eval] {e}")
        import traceback; traceback.print_exc()
        return ""

# A small "golden" test set: input -> the exact expected answer.
tasks = [
    ("France",    "paris"),
    ("Japan",     "tokyo"),
    ("Australia", "canberra"),
    ("Canada",    "ottawa"),
    ("Egypt",     "cairo"),
]

def normalize(text):
    return text.strip().lower().rstrip(".").strip()

def evaluate(system_prompt, label):
    correct = 0
    for country, gold in tasks:
        pred = normalize(chat(system_prompt, country))
        hit = (pred == gold)
        correct += hit
        print(f"{'PASS' if hit else 'FAIL'} | {country} -> {pred!r} (expected {gold!r})")
    acc = correct / len(tasks)
    print(f"{label}: accuracy = {correct}/{len(tasks)} = {acc:.2f}\n")
    return acc

# Prompt v1: vague. The model tends to reply in a full sentence, which fails exact match.
vague = "You answer questions about world capitals."

# Prompt v2: specific. Constrains the output format so it is machine-checkable.
specific = ("You are a geography lookup. Given a country name, reply with ONLY the "
            "capital city's name in lowercase, with no punctuation, articles, or extra words.")

print("===== Prompt v1 (vague) =====")
evaluate(vague, "v1 vague")
print("===== Prompt v2 (specific) =====")
evaluate(specific, "v2 specific")
```

The loop is the whole point: **write the test set once, then let it referee every future change to the prompt.**  You used this same harness on Thursday in *Skills: Design One, Then Measure It* to score a skill with and without.  We build a larger, hallucination-focused version in *Evaluating Agent Outputs*, formalize benchmark design in *Benchmarking*, and generalize from exact-match answers to property and regression checks in *Testing Agents*.

## Model 3: Reading the Eval

### Critical Thinking Questions

9.  The vague prompt sometimes produces a *correct capital* buried inside a sentence, yet scores FAIL.  Is the model wrong, or is the *metric* wrong?  What does this tell you about exact-match scoring?

   > *Hint: Separate "did the model know the answer?" from "did the output match the expected string?"  Both matter, but they are different failures with different fixes.*

10.  Exact match would reject `"Paris"` (capital P, unnormalized) even from a perfect prompt.  Name two ways to make the metric more forgiving without making it so loose that a wrong answer slips through.

   > *Hint: Contrast normalization (lowercasing, stripping punctuation) with semantic checks (substring, or an LLM-as-judge).  Each trades strictness for tolerance.*

11.  Suppose you kept editing the prompt until it scored 5/5 on exactly these five countries.  What might happen on a sixth, unseen country?  Name the risk and one way to guard against it.

    > *Hint: This is overfitting to the test set.  What would a held-out set of countries reveal that the original five cannot?*

---

---

# Part IIb: Designing a Persona That Holds Up

A system prompt that works on the first try and falls apart on the fifth is not a system prompt.  It is a lucky sample.  This part takes the craft further: what a persona actually constrains, where personas leak, and how to write one that survives a hostile user and a long session.

## The Three Layers of a Persona

A system prompt is a job description combined with a company handbook.  The job description says *who the agent is* and *what its role is*.  The handbook spells out the rules it must follow no matter what the customer asks.  A well-designed agent persona has three nested layers, and each layer constrains the one inside it.  The analogy stops at memory: an employee keeps the handbook after a long shift, and Part IIb's second section shows that an agent does not.

**Layer 1, Identity:** who the agent is
- Name, role title, employing organization
- Speaking style (first person, third person, "we")
- Persona anchoring phrase ("You are Aria, the Ursinus course assistant...")

**Layer 2, Behavioral Guidelines:** how the agent acts
- Tone (formal, friendly, peer-like)
- Brevity versus thoroughness norms
- Hedging policy ("say 'I think' when uncertain")
- Citation policy (always cite sources / never cite sources)

**Layer 3, Operational Constraints:** what the agent will and will not do
- Explicit refusals ("Do not provide medical diagnoses")
- Escalation rules ("If a student mentions self-harm, provide crisis resources and stop")
- Topic boundaries ("Only discuss coursework for CS357")

The table compares a bare prompt with a fully designed persona on each dimension.

| Dimension | Bare System Prompt | Fully-Designed Persona | Why It Matters |
|---|---|---|---|
| Identity | "You are a helpful assistant." - vague, model fills in the gaps however it sees fit | "You are Aria, the CS357 course assistant at Ursinus College." - anchors behavior from the first token | A missing identity means the model defaults to generic training, which may not match your use case |
| Tone | Unspecified; defaults to whatever the base model learned from internet text | "Use a supportive, peer-like tone. Avoid jargon unless defined." - sets expectations clearly | Tone mismatches make users uncomfortable and reduce trust |
| Refusals | None; agent will attempt to answer anything | "Do not complete assignments for students; guide them instead." - draws a clear line | Without explicit refusals, the agent will happily cross lines you meant to hold |
| Escalation | None; agent keeps going even in sensitive situations | "If a student seems distressed, acknowledge feelings and provide counseling resources." - hands off gracefully | Unhandled sensitive moments are the most legally and ethically dangerous gaps |
| Uncertainty | None; agent will guess with false confidence | "If you are unsure, say so explicitly and suggest where to find the answer." - teaches honesty | Without this, agents confidently hallucinate wrong answers |

### Critical Thinking Questions

**Q1.**  What happens at runtime if the Identity layer contradicts the Behavioral Guidelines layer?  For example, the identity says "You are a formal academic advisor" but the behavioral layer says "Always use casual slang."  How would a model likely resolve this, and how should a designer avoid it?

*Hint:* Models anchor strongly on early text in the system prompt.  Think about which instruction the model "sees" first.  Then consider what a designer could do structurally (ordering, explicit priority statements, or writing principles in a unified voice) to prevent the contradiction from arising in the first place.

**Q2.**  How specific should a persona be?  Compare a persona that is three sentences long to one that is three pages long.  What are the tradeoffs in resilience, maintainability, and coverage of unexpected behavior?

*Hint:* A three-sentence prompt is easy to maintain but leaves many situations unspecified; the model fills those gaps with its training defaults.  A three-page prompt covers more ground but may contain internal contradictions and is harder to update.  Think about which failure mode is worse for your particular use case.

**Q3.**  Can a poorly designed persona create safety risks even without any malicious intent?  Give a concrete example involving a course-assistant or student-facing agent.

*Hint:* Think about what happens if the persona is instructed to "always be encouraging and positive" and a student asks for feedback on a security vulnerability in their code.  What does "positive" mean when the technically correct answer is "this is dangerous"?  No one intended harm, but the persona's design created a conflict.

Even a carefully designed persona can break down, and the next section names the systematic ways that happens.

## Persona Consistency and Failure Modes

A persona can degrade mid-conversation.  Picture a new employee, briefed thoroughly on the first day, who slowly forgets the rules over a long shift.  That is what happens to an agent during a long conversation: as more context accumulates, the original instructions carry proportionally less weight.  Three failure modes to know:

**1.  "Assistant brain" leak**
The model's base training pushes it toward generic helpfulness even when the persona calls for restraint.  Example: a persona told not to write code starts writing code after a few turns because the user kept asking politely.

**2.  Persona drift**
Over long conversations, subtle shifts accumulate.  The tone slides from formal to casual; the agent starts volunteering information it was told to withhold.  Each turn shifts slightly, and by turn 30 the persona is unrecognizable.

**3.  Jailbreak-induced persona collapse**
The user explicitly instructs the agent to "forget" its persona or "pretend to be" something else.  The model, trained to be helpful, may partially comply.

Three defense patterns match the three failures:
- Persona reinforcement: restate the most critical identity and constraint lines periodically
- Reminder injection: append a condensed persona reminder at context boundaries (for example, when old turns are dropped)
- Constitutional constraints: embed non-negotiable rules in a form that is harder to override ("NEVER, under any circumstances...")

> **Common Misconception:** A longer, more detailed system prompt does not automatically produce a safer agent.  A long prompt with internal contradictions can behave *worse* than a shorter, internally consistent one.  Length is not a substitute for clarity, and adding rules without checking for conflicts often makes drift and collapse more likely, not less.

### Critical Thinking Questions

**Q4.**  Why does persona drift happen more in long conversations than short ones?  Connect your answer to the context window mechanics from the Memory activity.

*Hint:* A context window is finite.  As the conversation grows, earlier tokens (including the system prompt) represent a smaller fraction of the total context.  The model attends to recent turns proportionally more.  What does that imply about system prompt influence over time?

**Q5.**  What makes a persona hold up against jailbreak attempts?  Is that purely a function of the system prompt, or are other system design elements required?

*Hint:* Consider both the system prompt (constitutional constraints, explicit priority rules) and architectural choices outside the prompt (input filtering that catches known jailbreak patterns before they reach the model, output filtering that catches persona-violating content after).  What layer catches what the prompt misses?

**Q6.**  Describe a scenario where persona collapse would be *desirable*, where having the agent "break character" is the right behavior.  What does this imply about absolute rigidity in persona design?

*Hint:* Think about safety-critical edge cases: a user in real crisis, an emergency that falls outside the agent's topic boundary, or a situation where the agent's persona would cause real harm if maintained rigidly.  Should any persona be 100% unbreakable?

**What is the most responsible design choice?**

A course assistant persona is designed to be "always positive and encouraging" to help anxious students.  A student pastes code and asks "Is this correct?"  The code has a critical bug that would fail all test cases.  The most responsible design choice is:

[( )] Have the agent say the code looks great; a well-designed "positive" persona should prioritize student emotional wellbeing over factual accuracy
[(X)] Build a truthfulness constraint that overrides tone guidelines when the accuracy of technical feedback is at stake
[( )] Have the agent refuse to evaluate code at all; topic boundaries should prevent it from engaging with potentially discouraging content
[( )] Add a disclaimer that the persona always gives encouraging feedback regardless of accuracy, so students know not to rely on it for correctness

With these failure modes in mind, here are the principles that make a system prompt resilient from the start.

## Six Principles for Effective System Prompts

A system prompt is a recipe.  A recipe that says only "make something delicious" gives the cook no guidance and guarantees unpredictable results.  A recipe that names the ingredients, the quantities, the order of steps, and what "done" looks like produces consistent output.  Each principle below closes one gap that, left open, leads to hallucination, drift, or user frustration.

Effective system prompts share six characteristics:

1.  **Role before rules**: Establish the agent's identity in the first sentence before listing any constraints.  Models anchor on early text.
2.  **Positive framing**: Say what the agent should do, not only what it should not.  "Respond concisely" is more reliable than "Do not write long answers."
3.  **Format specification**: An explicit output format (bullet points, numbered steps, maximum length, citation format) reduces hallucination and variance.
4.  **Explicit uncertainty handling**: Tell the agent what to do when it does not know: "If you are unsure, say 'I'm not certain; here is where you can check:' and provide a resource."
5.  **Escalation paths**: Define when and how to hand off to a human: "If the student's question involves academic integrity violations, say 'This is a question for your professor' and stop."
6.  **Version and date stamp**: Include a comment with the prompt version and last-updated date so that later maintainers can trace what changed.

Apply the six principles to the three prompts in the critique table.

| Prompt | Missing Principles | Improved Version | What the Improvement Fixes |
|---|---|---|---|
| "Help students with CS homework." | Role (who?), format (how long? what structure?), uncertainty handling, escalation, version stamp | "You are Aria, CS357 assistant at Ursinus. Guide students toward answers; do not solve problems for them. Respond in ≤150 words using plain English. If unsure, say so and point to course materials. Escalate academic integrity concerns to the professor. v1.0 2026-08-25." | The improved version prevents the agent from writing code for students, caps response length, and defines behavior for the two most common edge cases |
| "Be helpful, harmless, and honest." | Role, format, escalation, specificity of what "helpful" means in this context | Add a named role, a specific domain constraint, a concrete output format, an escalation rule for sensitive topics, and a version stamp | Without a role, the model applies "helpful" too broadly; without a domain constraint, it will answer questions about anything |
| "Never say anything bad. Always be nice." | Role, positive framing (what to do instead of what not to do), format, uncertainty handling, escalation, version | Rewrite with a named role, positive behavior statements, format requirements, an uncertainty response, and an escalation path | Negative framing ("never say bad things") is vague and hard for models to operationalize; the improved version tells the agent what to do, not just what to avoid |

### Critical Thinking Questions

**Q7.**  Based on the critique table and your own experience with AI tools, which of the six principles is most often missing in real-world system prompts?  Why do you think it gets skipped?

*Hint:* Look at the three prompt examples in the table and identify the principle that is missing in all of them.  Then think about why someone building a quick demo or prototype might skip that step; is it time pressure, lack of awareness, or something else?

**Q8.**  How does explicit format specification (Principle 3) reduce hallucination risk?  Think about what the model is optimizing for when a format is and is not specified.

*Hint:* When no format is specified, the model chooses whatever format maximizes the probability of the next token, which often means "sounding thorough," which leads to verbose and sometimes fabricated details.  When a format is specified (for example, "respond in exactly three bullet points"), the model is constrained toward a more specific output space.  How does that constraint reduce the opportunity to hallucinate?

**Q9.**  Why would you date-stamp a system prompt?  What operational problem does this solve over a multi-year product lifecycle?

*Hint:* Imagine your agent is deployed for three years.  The original prompt author leaves the company.  The model is upgraded twice.  A new engineer needs to debug unexpected behavior.  Without a version stamp, how would they know which version of the prompt is running, when it was last updated, or whether a recent model change might have changed how the prompt is interpreted?

---

# Part IIc: Same Prompt, Two Models

Section 5 pinned the temperature to 0 and the seed to 42 and moved on.  This part says what those two numbers do, names the third dial you will meet in every model's settings panel, and then uses all three to compare two models without fooling yourself.  The theory, with the numbers, is in the [Sampling and Temperature](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/SamplingAndTemperature) and [AI by Hand](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AIByHand) tutorials, which are the reading for this part.  Today you need only the shapes.

## 5b.  Why the Same Prompt Gives Different Answers

A model does not pick its next word.  It scores every word in its vocabulary, turns those scores into probabilities, and the system rolls a weighted die to choose one.  Then it appends the winner and repeats, one word-piece (token) at a time, until it emits a stop.  The randomness lives in the roll, not in the weights, which never change between runs.  One early roll steers everything after it, which is why two runs of the same prompt can end up in different places.  The die analogy stops in one place: a die's faces are fixed, and the model recomputes the whole distribution for every token from everything written so far.

Temperature reshapes the die before the roll.  At 0 the most likely token wins every time, which is called greedy decoding, and the output is the same on every run on most hardware.  Raise it and the less likely tokens get a real chance; raise it far enough and the model wanders.  Temperature adds no knowledge.  It redistributes confidence across the options the model already had, which is why "raise the temperature so the model explores formats" was the wrong answer in Section 2.

Seed pins the roll itself.  The die is a pseudo-random number generator, a fixed sequence of numbers started from one integer, the seed.  The same seed with the same prompt and the same settings replays the same sequence, so the same output comes back.  Leave the seed out and Ollama picks a fresh one each call, which is what you want when you are measuring variety and not what you want in a test.  At temperature 0 the seed has little left to do, since there is no roll to replay; pinning both costs nothing and keeps the harness repeatable if you later raise the temperature on purpose.

Top-p trims the die instead of reshaping it.  Sort the tokens by probability, keep the most likely ones until their probabilities add up to p (0.9 is a common default), and drop everything below the line before the roll.  When the model is sure, the kept set is one token; when it is torn, the set widens.  The two dials compound: raising the temperature flattens the distribution, so more tokens are needed to reach p, and the randomness goes up twice over.  For a value your code has to parse, leave top-p at its default and keep the temperature low.

One caution before you trust temperature 0 completely.  Two runs can still differ on some hardware, because floating-point arithmetic done in a different order (parallel computation, or several requests batched together on a shared server) can flip a near-tie between two tokens.  On a laptop serving one request at a time this is rare.  If you see it in Model 4, write it down; it is a fact about your serving stack, not about the prompt.

Two things to remember from this section.  Temperature and top-p change *which* token gets picked, and the seed decides whether the pick can be replayed.  Pin all three and what is left in the output is the model.

---

## Model 4: Same Prompt, Two Models

Now use those dials to hold everything still except the model.  The cell below sends one system prompt and one user prompt to `llama3.2` and to a second model you have pulled (`llama3.2:1b` in the code; change the name if you pulled a different one), at temperature 0 and seed 42, three runs each.  The system prompt is the `json_bot` idea from Model 2 with one guardrail added: it must answer only geography questions, in JSON, and mark anything else out of scope.  The user prompt deliberately mixes an in-scope question with an out-of-scope one, so that the refusal column has something to measure.

Before you run it, predict the answers to the table's first two rows for each model, and write them down.  Then run the cell and fill the table from the printed output.  Each row is one observation per model, and the last row is a number per run.

| | `llama3.2` | Second model |
|---|---|---|
| Identical outputs across the three runs? | | |
| Format compliance (JSON only, no preamble, both fields present) | | |
| Refusal behavior (declined the medical part, answered it, or ignored it?) | | |
| Length (characters, per run) | | |

### Critical Thinking Questions

12.  Record your predictions before running: will the three runs on each model be identical, and will both models return valid JSON?  After the run, name the prediction you got wrong and the row of the table that showed it.

   > *Hint: Most teams predict identical runs and get them.  The prediction that usually misses is format compliance on the smaller model.  If both predictions held, say which row surprised you least and why.*

13.  Suppose run 1 and run 2 on the *same* model differ.  What could cause that when temperature is 0 and the seed is fixed?  Now suppose the two *models* differ from each other while every run within a model is identical.  What does that difference tell you, and why is it a different kind of fact?

   > *Hint: Run-to-run variation with everything pinned is noise in the serving system (Section 5b's caution about arithmetic order).  Model-to-model variation with everything pinned is the models themselves: different weights, different training data, different size.  The first tells you about your hardware; the second tells you about which model to ship.*

14.  Say one model returns clean JSON and the other adds a sentence of preamble before it.  Is the prompt wrong, the model wrong, or neither?  If you had to ship on the model that adds preamble, what would you change first, the prompt or the parser?

   > *Hint: Question 7 showed which line of `json.loads` breaks on preamble.  A prompt can add a few-shot example of a bare JSON reply, and a parser can find the first `{`.  Decide which fix is cheaper and which one still holds when the next model arrives.*

15.  Model 3 warned about overfitting a prompt to five countries.  Name the analogous risk for a prompt tuned on one model, and say which row of the table would reveal it.

   > *Hint: A prompt that scores well on one model and poorly on another is tuned to that model's habits, not to the task.  The format compliance row is where this usually shows.  A second model is to a prompt what a held-out set is to a test set.*

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.  Both models must already be pulled (see Before You Start).

```python
import requests
import json

# temperature=0.0 pins the wording (Running Your Own AI, Section 3c).
# seed=42 pins the random draw itself: any fixed number works, the same one
# every run means the same dice rolls every run. Together they make this
# harness repeatable, which is what lets a test tell you something.
def chat(system, user, temperature=0.0, seed=42, model="llama3.2"):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": temperature, "seed": seed},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[promptengineering:eval] {e}")
        import traceback; traceback.print_exc()
        return ""

# The two models under test. Replace the second with any model you have pulled.
MODELS = ["llama3.2", "llama3.2:1b"]
RUNS = 3

# One system prompt and one user prompt, identical for every run of every model.
SYSTEM = ('You are a geography lookup. Reply with ONLY this JSON and nothing else: '
          '{"answer": str, "confidence": "high|medium|low"}. '
          'If any part of the question is not about geography, do not answer that part; '
          'answer the geography part and set confidence to "low".')
USER = "What is the capital of Australia? Also, is it safe to take two ibuprofen for a headache?"

def is_json(text):
    try:
        json.loads(text)
        return True
    except ValueError:
        return False

for model in MODELS:
    outputs = []
    for i in range(RUNS):
        out = chat(SYSTEM, USER, model=model).strip()
        outputs.append(out)
        print(f"===== {model} | run {i + 1} | {len(out)} chars | valid JSON: {is_json(out)} =====")
        print(out, "\n")
    print(f"{model}: identical across {RUNS} runs? {len(set(outputs)) == 1}\n")
```

Two things to remember from this part.  A difference between runs with everything pinned is noise, and a difference between models with everything pinned is signal about the models.  Before you compare two models, pin the temperature and the seed, or you are comparing two dice.

---

# Part III: Synthesis and Practice

In this part you write and red-team real system prompts: first a prompt for a course-scheduling agent, then a stress test of a teammate's design.  This is the closest thing to real prompt engineering work, and the goal is to find where a prompt breaks before a real user does.

## 6.  Exercises

1.  *Job description.*

   - *What to do*: Write the complete system prompt (ROLE, GOAL, TOOLS, FORMAT, GUARDRAILS) for an agent that helps students plan four-year course schedules.  Trade prompts with another team and red-team theirs: find one input that breaks the agent's intended behavior.
   - *Starter hint*: A red-team input is a prompt the original designers did not anticipate: for example, asking the scheduling agent about a major that does not exist, requesting a schedule that violates a prerequisite, or asking it to do something outside its stated goal entirely.
   - *You've succeeded when*: You can describe the exact input that broke the other team's prompt, explain *why* it broke (which part of the prompt failed to anticipate it), and propose a one-sentence fix.

2.  *Few-shot lift.*

   - *What to do*: Identify a formatting task where the bare model fails (for example, extracting dates from a sentence and converting them to ISO 8601 format like `2024-10-10`).  Add exactly two input-output examples to the prompt and show that the model now succeeds.
   - *Starter hint*: Start with the prompt `"Extract all dates and return them in ISO 8601 format."` Test it on a sentence like `"The project is due October 10 and the review is on Nov 3."` Then add two worked examples above the instruction and retest.
   - *You've succeeded when*: You can show before-and-after outputs side by side, and the after output has correctly formatted dates.

3.  *Persona audit.*

   - *What to do*: Pick one persona from Model 2 and run the same factual question five times at temperature 0.3.  Record whether the *facts asserted* change across runs, or only their *presentation*.
   - *Starter hint*: For "Why is the sky blue?" the correct mechanism is Rayleigh scattering of short-wavelength light.  Does every run mention this?  Does the analogy change?  Does the confidence level vary?
   - *You've succeeded when*: You have five outputs side by side and a one-paragraph judgment: does this persona change substance, presentation, or both, with specific textual evidence.

4.  *Guardrail test.*

   - *What to do*: Add a refusal instruction to any persona (for example, "Do not answer questions about competitors' products"), then attempt three different circumventions.  Record which succeed, which fail, and why.
   - *Starter hint*: Circumvention strategies to try: (1) ask indirectly, (2) ask the model to hypothetically imagine a version of itself without the restriction, (3) embed the forbidden topic inside a longer innocent-seeming question.
   - *You've succeeded when*: You have three attempts documented with the exact prompt and response, and a one-sentence explanation of the mechanism for each success or failure.

5.  *Eval-driven iteration.*

   - *What to do*: Take the golden-test harness from Section 5 and add three new `(country, capital)` pairs of your own.  Then write a *third* system prompt that beats both `vague` and `specific` on the full eight-item set, or prove that `specific` is already at ceiling and explain why.
   - *Starter hint*: If `specific` already scores 8/8, change the *task* to something harder to format (for example, "return the country's capital and its ISO country code as `city, XX`") so there is room for a prompt to improve the score.
   - *You've succeeded when*: You can show the accuracy of all three prompts on the same test set, and state in one sentence which prompt change caused the largest gain and why.

---

## Reflection Prompt

*Personal*: A system prompt is invisible to the end user of an agent; users often have no idea what instructions are shaping the responses they receive.  Think of a chatbot you have interacted with.  Did you know what its system prompt said?  Did it matter to you?  Describe how today's activity changed your sense of how much you can know about an AI system you use.

*Technical*: You now know that the system prompt is the agent's "constitution."  If you were designing a course scheduling agent for real students at Ursinus, what would your full ROLE / GOAL / TOOLS / FORMAT / GUARDRAILS template say?  Write a draft, then identify the hardest part to specify and explain why.

*Societal*: What obligations, if any, does an agent designer have to disclose the persona and guardrails an agent is operating under?  Consider two cases: a customer-service agent for a company, and an AI tutor used by students in a public school.  Should disclosure requirements differ between these cases?  Why or why not?

---

-> Coming Up Next: You have written instructions for a model whose insides are still a black box, and you have compared two of those black boxes on the same prompt.  Thursday's session, *The Karpathy Loop and the Gauntlet Loop: Iterating With an Agent* (Thu Sep 17), puts the system prompt you wrote today to work: you hand an agent a task, read what it produces, and run it through one gauntlet round of critique and revision.  Bring the OpenCode Studio artifact you have so far.  Everything you tuned by feel today has a mechanism underneath: how your prompt becomes numbers, how those numbers carry meaning, and how each word's meaning is bent by the words around it.  The [Tokens, Embeddings, and Attention](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/TokensEmbeddingsAttention) tutorial is where you meet it.

## 7.  Further Reading

- Anthropic and OpenAI prompt engineering guides (online).  Practical pattern catalogs maintained by model vendors.
- Jason Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models."  *NeurIPS* (2022).
- Melanie Mitchell.  *AI: A Guide for Thinking Humans*, Chapter 3, on what models do and do not understand.
- Rick Dakan and Joseph Feller, with Anthropic.  *The AI Fluency Framework* (2025), on the Description competency, describing goals well enough to prompt useful behavior.  Released under CC BY-NC-SA 4.0.
- This course: [Why Different Answers Every Time? Sampling, Temperature, and Generation](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/SamplingAndTemperature), the full treatment of temperature, seed, top-k, and top-p behind Part IIc, and [AI by Hand](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AIByHand), where you work the temperature formula with a calculator.
- This course: [Tokens, Embeddings, and Attention](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/TokensEmbeddingsAttention), the mechanism under everything you tuned by feel today.
- On evaluation: see this course's *Evaluating Agent Outputs*, *Benchmarking*, and *Testing Agents* activities for larger golden-test, benchmark, and property-based harnesses.
