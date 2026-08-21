<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-promptengineering.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-promptengineering.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Prompt Engineering as Agent Design: Personas and System Prompts

In *The Agent Loop: Perceive, Plan, Act* activity, two-thirds of our calculator agent's design lived in one string: its system prompt. A prompt is not a question; it is a **program written in natural language** that configures an agent's behavior. This module moves from **anatomy of a prompt $\rightarrow$ core patterns $\rightarrow$ personas and system prompts $\rightarrow$ designing the policy of your own agent**, because in an agentic system the system prompt *is* the agent's job description.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| System prompt | The standing instructions given to a model before any user message; it sets the agent's role, allowed actions, output format, and limits | The ROLE / GOAL / TOOLS / FORMAT / GUARDRAILS template used in Exercise 1 |
| Persona | A named identity and expertise frame assigned to the model via the system prompt, which shifts the style and tone of its outputs without changing its underlying knowledge | The "patient tutor," "careful fact-checker," and "json_bot" identities compared in Model 2 |
| Few-shot example | One or more sample input-output pairs included in the prompt to show the model exactly what the desired format looks like, rather than only describing it in words | Showing the model two examples of "date inside a sentence -> ISO 8601 string" so it learns the pattern from demonstration |
| Chain-of-thought | A prompting technique that asks the model to write out intermediate reasoning steps before giving a final answer, which often improves accuracy on multi-step problems | Adding "think step by step" to a math prompt and observing whether accuracy improves |
| Output structuring | Specifying a machine-readable format (such as JSON) in the prompt so that downstream code can parse and act on the model's response reliably | The `json_bot` persona that returns `{"answer": ..., "confidence": ...}` |
| Guardrail | An explicit instruction in the system prompt telling the agent what topics to refuse, escalate to a human, or handle with extra caution | "If asked for medical advice, always recommend consulting a licensed professional" |

---

# Part I: The Anatomy of a Prompt

In this part, you will learn that a prompt is not just a question but a structured program in natural language, and that small changes to its wording produce large changes in the agent's behavior. By the end, you will be able to identify every behavioral commitment embedded in a prompt before you even run it.

## 1. Three Channels of Instruction

Think of sending a message to an agent like addressing a letter: the **system prompt** is the standing policy manual the agent always carries with it, the **user message** is the specific letter you wrote today, and the **conversation history** is the file of everything said before. The model reads all three, but treats the system prompt as the rules that cannot be overridden by any single letter.

**Modern chat models receive layered instructions.** The **system prompt** establishes durable role, constraints, and format. The **user message** carries the immediate task. The **conversation history** carries everything either party has said. The model conditions on all three, but well-trained models weight the system prompt as standing policy:

$$
P(\text{response} \mid \text{system}, \text{history}, \text{user})
$$

**For an agent, the system prompt is the constitution.** It declares the agent's goal, its allowed actions, its output format, and its boundaries. When we built the calculator agent, two-thirds of the design lived in that one string.

---

## Model 1: Two Prompts, Two Agents

Before examining the table below, consider two job postings: one that says only "engineer wanted," and one that lists the role, required skills, expected deliverables, and tone of client communication. The second produces far more predictable, evaluable work. Prompts work exactly the same way.

| Feature | Prompt A | Prompt B |
|---------|----------|----------|
| Full text | "Tell me about photosynthesis." | "You are a patient biology tutor for first-year students. Use one everyday analogy, then a three-sentence technical explanation, then ask the student one check-for-understanding question. Topic: photosynthesis." |
| Audience specification | Not specified; the model must guess | Explicitly set to first-year students, which shifts vocabulary and assumed background |
| Output structure | Unconstrained: any length, any format | Three-part structure (analogy, explanation, question) makes the output predictable and auditable |
| Evaluability | Hard to score: what counts as a good explanation? | Easy to score: does it have an analogy? Three sentences? A question at the end? |
| What changes if we swap the topic | Everything may change unpredictably | Only the topic content changes; structure and tone remain consistent |

### Critical Thinking Questions

1. List every behavioral commitment Prompt B makes that Prompt A leaves to chance.

   > *Hint: Go through Prompt B word by word and ask: does this constrain length, tone, structure, audience, or format? Every constraint is a behavioral commitment.*

2. Which prompt makes the output easier to *evaluate*? Why does specifying format make quality measurable?

   > *Hint: If you wanted to write a program that checks whether the response is good, what would it look for in Prompt A's output versus Prompt B's output?*

3. Prompt B constrains tone and structure but not correctness. What would you add to the prompt to push the model toward factual accuracy?

   > *Hint: Think about what the model does when it is uncertain. Could you instruct it to signal uncertainty? Could you ask it to cite a source?*

4. Rewrite Prompt B for a different audience: a graduate seminar or a fifth grader. Which elements of the prompt changed and which proved durable across audiences?

   > *Hint: Start with an exact copy of Prompt B and modify only what you must. The elements you did not need to change are the "durable" ones.*

---

## 2. Core Prompting Patterns

The community has converged on a small set of reliable patterns, each of which we will reuse all semester. **Role and persona** assigns an identity and expertise frame. **Few-shot examples** show the desired input-output mapping rather than describing it. **Chain-of-thought** requests intermediate reasoning before the answer, like asking someone to "show your work." **Output structuring** demands a machine-readable format such as JSON, which is what allows a *program* to act on a model's response. **Constraints and refusals** state what the agent must not do.

A practical agent system prompt composes several patterns:

```
ROLE: who the agent is and for whom it works
GOAL: what done looks like
TOOLS: actions it may take, with exact syntax
FORMAT: the exact output schema
GUARDRAILS: what it must refuse or escalate to a human
```

An agent must return JSON so that downstream code can parse its decision. The most reliable prompting approach is:

[( )] Ask politely for JSON at the end of the user message
[( )] Raise the temperature so the model explores formats
[(X)] Specify the exact schema in the system prompt and include a few-shot example of a valid response
[( )] Avoid mentioning JSON so the model is not confused

> *On the second option: that is the temperature dial you turned in *Running Your Own AI*, Section 3b. Recall what raising it actually did to your six answers, then ask yourself whether "explores formats" is a thing you want from a value your code has to parse.*

---

## 3. Plan Before You Prompt

The fastest way to a bad output is a rushed prompt. Before you write the *final* prompt, spend a moment on the plan behind it; this is the **Description** competency from the AI Fluency Framework (see the Welcome activity) in action. A reliable loop has three moves:

1. **Ask and answer questions first.** Instead of demanding an answer immediately, ask the model to *ask you* clarifying questions: "Before you write anything, ask me up to five questions that would change how you approach this." Answering them surfaces assumptions (audience, scope, format, constraints) that you would otherwise discover only after a wrong draft.
2. **Describe what success looks like.** State the done-conditions up front, exactly as Prompt B did in Model 1 and as every exercise in this course states "*You've succeeded when...*". If you can name what a good output contains (an analogy, three sentences, valid JSON, a citation) the model can aim at it and you can *check* it. A goal you can evaluate is a goal you can hit.
3. **Iterate on the plan and the prompt together.** Treat the first response as a draft of the *plan*, not the final deliverable. Refine the plan with the model over a few turns, and fold what you learn back into the prompt. The prompt you finish with is almost never the prompt you started with.

This is the Delegation competency from the Welcome activity's at-home AI Fluency reading, put into practice: converse to define success, then plan the work before executing it.

> **Tip:** Plan -> describe success -> iterate. Ask the model what it needs to know, tell it what "done" looks like, and refine both the plan and the prompt before you commit to a full run.

*This plan-first, describe-success, iterate practice draws on the Description competency of The AI Fluency Framework. Copyright 2025 Rick Dakan, Joseph Feller, and Anthropic. Released under the CC BY-NC-SA 4.0 license.*

---

# Part II: Personas in Practice

In this part, you will assign three different persona instructions (identities given to the model via the system prompt) to the same underlying model and observe how each shifts the style and format of the output, without changing the model's weights at all. This matters because understanding personas helps you design agents that behave consistently and avoids the trap of thinking a more authoritative persona produces more accurate answers.

## 4. Personas Shape Distributions, Not Souls

Before we run the code, try this thought experiment: if you ask a knowledgeable friend the same question while they are in "professor mode" versus "texting a friend mode," you get different vocabularies, different structures, maybe different levels of hedging, but the same underlying facts. A model persona works similarly. It shifts the *style* of the output by making certain patterns more likely, not by granting the model new knowledge.

**A persona does not create knowledge; it reweights it.** Telling a model it is a cautious pharmacist shifts the distribution of its outputs toward hedged, safety-conscious language present in its training data. This is powerful and potentially misleading: a persona can also reweight toward confident-sounding error. Personas should therefore be paired with *epistemic instructions* such as "say so when you are unsure," and we will measure whether models obey them.

---

The code cell below runs the same question ("Why is the sky blue?") through three different system prompts (persona instructions) and prints each response side by side. Notice that only the system prompt changes; the model, the question, and all other settings stay identical.

## Code Cell

> If you have not installed Ollama yet (we do it together in the *Running Your Own AI* session), read this cell and predict its output; bring your prediction to class.

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

Run the cell (or examine projected outputs) and compare the three responses to the identical question.

### Critical Thinking Questions

5. Which differences across the three outputs are *formatting*, which are *tone*, and which (if any) are *substance* (different facts or claims)?

   > *Hint: Formatting is about structure: bullets, paragraphs, JSON fields. Tone is about word choice and hedging. Substance means the actual claims about the world changed.*

6. The `json_bot` output is the only one a program can reliably consume. Sketch the two lines of Python that would extract the confidence field, and identify what happens if the model adds a single word of preamble before the JSON.

   > *Hint: Try `import json; data = json.loads(output); confidence = data["confidence"]`. Now imagine the model outputs `Sure! {"answer": ..., "confidence": ...}`; which line of that code breaks and why?*

7. Design a persona that would be actively harmful for a factual question like this one, and explain the mechanism of harm. (Keep it classroom-appropriate; the goal is to reason about failure modes, not to produce harmful content.)

   > *Hint: Think about a persona that would make the model systematically overconfident, systematically misleading about a specific domain, or unwilling to express any uncertainty.*

> **Common Misconception:** A common assumption is that giving the model a more authoritative persona (for example, "You are a world-leading expert") makes its answers more accurate. In reality, authority personas tend to increase the model's *confidence* in its phrasing without improving the underlying facts, and they often suppress the model's natural hedging, making it harder to detect when it is wrong. More authority in the persona can mean less useful uncertainty signals in the output.

---

## 5. Eval-Driven Prompt Development

Model 1 argued that Prompt B is easier to *evaluate* than Prompt A. Now we make that concrete: we **measure** a prompt against a small set of known-answer examples, then change the prompt and watch the number move. This is how prompts are improved in practice: not by taste, but by a **golden test set**: a fixed list of `input -> expected-output` pairs you score automatically.

The cell below defines five `(country, expected capital)` pairs, then runs the *same* test set through two different system prompts: a vague one and a specific, format-constrained one. Because the score uses exact match, the vague prompt's full-sentence answers fail while the specific prompt's one-word answers pass. That accuracy gap is the *evidence* that one prompt is better for this task.

## Code Cell

> If you have not installed Ollama yet (we do it together in the *Running Your Own AI* session), read this cell and predict its output; bring your prediction to class.

```python
import requests

# temperature=0.0 pins the wording (Running Your Own AI, Section 3b).
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

The loop is the whole point: **write the test set once, then let it referee every future change to the prompt.** We build a larger, hallucination-focused version of this harness in the *Evaluating Agent Outputs* activity, formalize benchmark design in *Benchmarking*, and generalize from exact-match answers to property and regression checks in *Testing Agents*.

## Model 3: Reading the Eval

### Critical Thinking Questions

8. The vague prompt sometimes produces a *correct capital* buried inside a sentence, yet scores FAIL. Is the model wrong, or is the *metric* wrong? What does this tell you about exact-match scoring?

   > *Hint: Separate "did the model know the answer?" from "did the output match the expected string?" Both matter, but they are different failures with different fixes.*

9. Exact match would reject `"Paris"` (capital P, unnormalized) even from a perfect prompt. Name two ways to make the metric more forgiving without making it so loose that a wrong answer slips through.

   > *Hint: Contrast normalization (lowercasing, stripping punctuation) with semantic checks (substring, or an LLM-as-judge). Each trades strictness for robustness.*

10. Suppose you kept editing the prompt until it scored 5/5 on exactly these five countries. What might happen on a sixth, unseen country? Name the risk and one way to guard against it.

    > *Hint: This is overfitting to the test set. What would a held-out set of countries reveal that the original five cannot?*

---

# Part III: Synthesis and Practice

In this part, you will write and red-team real system prompts: first designing one for a course-scheduling agent, then stress-testing a teammate's design. This is the closest thing to real prompt engineering work: the goal is to discover where a prompt breaks before a real user does.

## 6. Exercises

1. *Job description.*

   - *What to do*: Write the complete system prompt (ROLE, GOAL, TOOLS, FORMAT, GUARDRAILS) for an agent that helps students plan four-year course schedules. Trade prompts with another team and red-team theirs: find one input that breaks the agent's intended behavior.
   - *Starter hint*: A red-team input is a prompt the original designers did not anticipate: for example, asking the scheduling agent about a major that does not exist, requesting a schedule that violates a prerequisite, or asking it to do something outside its stated goal entirely.
   - *You've succeeded when*: You can describe the exact input that broke the other team's prompt, explain *why* it broke (which part of the prompt failed to anticipate it), and propose a one-sentence fix.

2. *Few-shot lift.*

   - *What to do*: Identify a formatting task where the bare model fails (for example, extracting dates from a sentence and converting them to ISO 8601 format like `2024-10-10`). Add exactly two input-output examples to the prompt and show that the model now succeeds.
   - *Starter hint*: Start with the prompt `"Extract all dates and return them in ISO 8601 format."` Test it on a sentence like `"The project is due October 10 and the review is on Nov 3."` Then add two worked examples above the instruction and retest.
   - *You've succeeded when*: You can show before-and-after outputs side by side, and the after output has correctly formatted dates.

3. *Persona audit.*

   - *What to do*: Pick one persona from Model 2 and run the same factual question five times at temperature 0.3. Record whether the *facts asserted* change across runs, or only their *presentation*.
   - *Starter hint*: For "Why is the sky blue?" the correct mechanism is Rayleigh scattering of short-wavelength light. Does every run mention this? Does the analogy change? Does the confidence level vary?
   - *You've succeeded when*: You have five outputs side by side and a one-paragraph judgment: does this persona change substance, presentation, or both, with specific textual evidence.

4. *Guardrail test.*

   - *What to do*: Add a refusal instruction to any persona (for example, "Do not answer questions about competitors' products"), then attempt three different circumventions. Record which succeed, which fail, and why.
   - *Starter hint*: Circumvention strategies to try: (1) ask indirectly, (2) ask the model to hypothetically imagine a version of itself without the restriction, (3) embed the forbidden topic inside a longer innocent-seeming question.
   - *You've succeeded when*: You have three attempts documented with the exact prompt and response, and a one-sentence explanation of the mechanism for each success or failure.

5. *Eval-driven iteration.*

   - *What to do*: Take the golden-test harness from Section 5 and add three new `(country, capital)` pairs of your own. Then write a *third* system prompt that beats both `vague` and `specific` on the full eight-item set, or prove that `specific` is already at ceiling and explain why.
   - *Starter hint*: If `specific` already scores 8/8, change the *task* to something harder to format (for example, "return the country's capital and its ISO country code as `city, XX`") so there is room for a prompt to improve the score.
   - *You've succeeded when*: You can show the accuracy of all three prompts on the same test set, and state in one sentence which prompt change caused the largest gain and why.

---

## Reflection Prompt

*Personal*: A system prompt is invisible to the end user of an agent; users often have no idea what instructions are shaping the responses they receive. Think of a chatbot you have interacted with. Did you know what its system prompt said? Did it matter to you? Describe how today's activity changed your sense of how much you can know about an AI system you use.

*Technical*: You now know that the system prompt is the agent's "constitution." If you were designing a course scheduling agent for real students at Ursinus, what would your full ROLE / GOAL / TOOLS / FORMAT / GUARDRAILS template say? Write a draft, then identify the hardest part to specify and explain why.

*Societal*: What obligations, if any, does an agent designer have to disclose the persona and guardrails an agent is operating under? Consider two cases: a customer-service agent for a company, and an AI tutor used by students in a public school. Should disclosure requirements differ between these cases? Why or why not?

---

-> Coming Up Next: We have been calling a model running somewhere on a server. In the *Running Your Own AI: Ollama, OpenWebUI, and Private Local Models* activity, we take full control by installing and running AI models entirely on our own hardware: no cloud, no per-token fees, and no data leaving our machines.

## 7. Further Reading

- Anthropic and OpenAI prompt engineering guides (online). Practical pattern catalogs maintained by model vendors.
- Jason Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *NeurIPS* (2022).
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 3, on what models do and do not understand.
- Rick Dakan and Joseph Feller, with Anthropic. *The AI Fluency Framework* (2025), on the Description competency, describing goals well enough to prompt useful behavior. Released under CC BY-NC-SA 4.0.
- On evaluation: see this course's *Evaluating Agent Outputs*, *Benchmarking*, and *Testing Agents* activities for larger golden-test, benchmark, and property-based harnesses.
