<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-temperatureexplorer.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-temperatureexplorer.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Temperature and Sampling Explorer: Hands-On Parameter Tuning

In the Sampling, Temperature, and Generation activity we worked through the math: softmax, logits, top-k, top-p. Today we *experiment*. We observe what temperature, top-k, and top-p actually do to a local model's outputs on a variety of tasks, build a structured dataset of observations, and develop practical intuition for when to use which settings. By the end you will be able to specify generation parameters for a new task with a principled argument — not just a guess.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Temperature** | Controls the shape of the probability distribution before sampling; T->0 = greedy/deterministic, T->∞ = uniform random. | Setting T=0.0 for a code-generation task to get reproducible output. |
| **Top-k sampling** | Keeps only the k highest-probability tokens, discards the rest before sampling — fixing the candidate set size regardless of how confident the model is. | With k=3 and candidates [Paris, Lyon, London, banana, croissant], only [Paris, Lyon, London] are considered. |
| **Top-p (nucleus) sampling** | Keeps the smallest set of tokens that together account for at least p of the total probability mass — adapting the candidate set size to the model's confidence at each step. | With p=0.90 and Paris having probability 0.92, only Paris is kept; if the top five tokens are each 0.18, all five are kept. |
| **Entropy** | A measure of uncertainty in the distribution; high entropy = flat distribution = unpredictable outputs; low entropy = peaked distribution = predictable outputs. | At T=0.1 the entropy is near 0 (nearly certain); at T=2.0 the entropy is high (many tokens are competitive). |
| **Greedy decoding** | Always picking the single most probable token; equivalent to T=0; deterministic but can produce repetitive or locally-optimal-but-globally-suboptimal outputs. | Setting temperature=0 and getting the same "Paris" every time for the capital-of-France question. |
| **Repetition penalty** | A technique that reduces the probability of tokens that have already appeared in the output, preventing the model from looping endlessly on common phrases. | Without a repetition penalty, some models at T=0 produce "the the the the..."; a penalty of 1.1 suppresses this. |

---

### Before You Start

**What you need:** Python 3.10+; Ollama only for the optional live comparison.

**What you will have at the end:** a felt sense of what temperature and top-p actually do, from numbers you computed.

Work through the sections in order — each one builds on the last, and the code blocks are meant to be run as you reach them, not read past.

---

# Part I: Softmax and Temperature, Revisited Visually

## 1. The Math With Real Numbers

We will work through a concrete 5-token example and trace what happens to each token's probability as we change temperature. This is the same math from the Sampling activity — now we measure the *entropy* of the resulting distribution so we can connect the numeric output to a single summary quantity.

The softmax with temperature is:

$$
P(i) = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}
$$

Entropy of the resulting distribution is:

$$
H = -\sum_i P(i) \log P(i)
$$

High entropy means the distribution is flat — the model is uncertain. Low entropy means the distribution is peaked — the model is confident.

---

## Code Cell

```python
import math

def softmax_temp(logits, temperature):
    scaled = [l / temperature for l in logits]
    max_l = max(scaled)
    exp_vals = [math.exp(l - max_l) for l in scaled]
    total = sum(exp_vals)
    return [e / total for e in exp_vals]

def entropy(probs):
    return -sum(p * math.log(p + 1e-10) for p in probs)

# Toy example: 5 tokens with raw logit scores
VOCAB = ["Paris", "Lyon", "London", "banana", "croissant"]
LOGITS = [4.5, 2.1, 1.8, 0.3, -0.5]

print(f"{'T':>5}  {'Paris':>8}  {'Lyon':>8}  {'London':>8}  {'banana':>8}  {'croissant':>10}  {'entropy':>8}")
print("-" * 72)
for T in [0.1, 0.5, 1.0, 1.5, 2.0]:
    probs = softmax_temp(LOGITS, T)
    H = entropy(probs)
    print(f"{T:>5.1f}  " + "  ".join(f"{p:>8.4f}" for p in probs) + f"  {H:>8.4f}")
```

**Expected output (approximate):**

```
    T     Paris      Lyon    London    banana  croissant   entropy
------------------------------------------------------------------------
  0.1    1.0000    0.0000    0.0000    0.0000     0.0000    0.0000
  0.5    0.9927    0.0065    0.0007    0.0001     0.0000    0.0405
  1.0    0.8778    0.0838    0.0330    0.0050     0.0005    0.4673
  1.5    0.7468    0.1413    0.0826    0.0227     0.0066    0.7893
  2.0    0.6406    0.1687    0.1148    0.0528     0.0231    1.0183
```

---

### Critical Thinking Questions

1. At T=0.1, Paris has probability ≈1.000. At T=2.0, Paris has probability ≈0.64. The **logits** did not change between runs — only T changed. What is the mathematical mechanism by which temperature reshinks Paris's dominance? Walk through the exponent step for Paris at T=0.1 vs. T=2.0.

   > *Hint: At T=0.1, the scaled logit for Paris is 4.5/0.1 = 45. For banana it is 0.3/0.1 = 3. The difference is 42 log-units — $e^{42}$ is astronomically large compared to $e^3$. At T=2.0, Paris becomes 4.5/2.0 = 2.25, banana becomes 0.3/2.0 = 0.15, a difference of only 2.1 log-units. The ratio $e^{2.1} \approx 8$ is much less extreme.*

2. Entropy measures how unpredictable the distribution is. As temperature increases from 0.1 to 2.0, entropy:
   [( )] Decreases, because the distribution becomes more random
   [(X)] Increases, because a flatter distribution is harder to predict
   [( )] Stays the same, because the logits are fixed
   [( )] Increases then decreases after a peak at T=1.0

3. Top-k=3 applied to the 5-token example above keeps only Paris, Lyon, and London (the three highest-probability tokens) and renormalizes. Top-p=0.90 at T=1.0 would keep only Paris (≈0.88 ≥ 0.90, approximately) and stop. But at T=2.0, top-p=0.90 would need to include Paris, Lyon, and London to accumulate at least 0.90 of the total probability mass. Why does the same top-p threshold require more tokens at higher temperature?

   > *Hint: The threshold is based on cumulative probability, not a count. At T=1.0, Paris alone captures nearly 0.88 of the mass — you need very few tokens to reach 0.90. At T=2.0, Paris captures only 0.64, so you must add Lyon (0.17), and still need London (0.11) to push past 0.90. The flatter distribution distributes mass across more tokens, so you need more of them to reach the same cumulative threshold.*

4. A classmate claims: "I should always use top-p instead of top-k because top-p adapts to the model's confidence." Give one situation where top-k might be preferable, and explain why.

   > *Hint: Consider a task where you want to strictly limit the vocabulary size for safety or efficiency reasons — for example, generating a list where you only ever want one of five predefined options. Top-p might include 3 tokens when the distribution is flat or 1 when it is peaked. Top-k enforces a fixed budget regardless.*

---

# Part II: Real Model Experiments

## 2. A Systematic Sweep

We now run a structured experiment: four task types × four temperature settings × three repetitions. This gives you 48 data points to analyze. The Manager assigns one task row to each team member for the first sweep; then you rotate and check each other's rows.

Fill in the observation table as you go. The Recorder keeps the table and posts it to the discussion board.

---

## Code Cell

```python
import requests
import json
import time

def query(prompt, model="llama3.2", temperature=1.0, top_p=0.9, top_k=40):
    try:
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False,
                  "options": {"temperature": temperature,
                              "top_p": top_p,
                              "top_k": top_k}},
            timeout=120)
        return r.json()["response"].strip()
    except Exception as e:
        print(f"[query] {e}")
        return ""

TEST_PROMPTS = {
    "factual": "What is the capital of France? Answer in one word.",
    "creative": "Write the first line of a science fiction novel.",
    "code":     "Write a Python one-liner that reverses a string.",
    "list":     "Name three programming languages. Answer as a comma-separated list.",
}

TEMPERATURES = [0.0, 0.5, 1.0, 1.5]

for task, prompt in TEST_PROMPTS.items():
    print(f"\n=== {task.upper()} ===")
    for T in TEMPERATURES:
        outputs = []
        for _ in range(3):
            outputs.append(query(prompt, temperature=T))
            time.sleep(0.5)
        print(f"T={T}: {outputs}")
```

---

## Observation Table (Recorder fills this in)

| Task | T=0.0 (run 1, 2, 3) | T=0.5 (run 1, 2, 3) | T=1.0 (run 1, 2, 3) | T=1.5 (run 1, 2, 3) | Consistent? |
|------|---------------------|---------------------|---------------------|---------------------|-------------|
| factual | | | | | |
| creative | | | | | |
| code | | | | | |
| list | | | | | |

"Consistent?" column: yes (all 3 identical) / partial (2/3 same) / no (all different).

---

### Critical Thinking Questions

5. At T=0.0, you ran the factual question three times and (likely) got the same answer all three times. Is this because the model "knows" the right answer, or because it always picks the highest-probability token? How would you design an experiment to tell the difference?

   > *Hint: Ask the model a factual question where the correct answer is less well-known — for example, "What is the capital of Burkina Faso?" Does it still give a consistent answer at T=0? Is that answer correct? A model that always gives the same wrong answer at T=0 is being consistent, not knowledgeable.*

6. For the code generation task, what happened at T=1.5? Did the generated Python still run without a syntax error? Why might high temperature be more harmful for code generation than for creative writing?

   > *Hint: In creative writing, any plausible continuation is acceptable — there is no "correct" first line for a science fiction novel. In Python code, a single misplaced character (a wrong parenthesis, a misspelled keyword, an incorrect indentation level) causes a syntax error and the code fails entirely. High temperature makes rare characters more likely at every step, which is fine for prose but catastrophic for code that must exactly match a grammar.*

7. A developer wants their customer service chatbot to give exactly the same answer to the same question every time. They should set temperature=0 and top_k=1.
   [(X)] True — T=0 and top_k=1 both force greedy decoding, giving deterministic outputs on most hardware
   [( )] False — there is no way to make an LLM deterministic
   [( )] True, but only top_k=1 is needed; temperature has no additional effect
   [( )] False — even at T=0, the model might generate different outputs due to random seeding

   > **Common Misconception:** "Lower temperature = better answers." This is not true as a general rule. For creative tasks, low temperature produces repetitive, generic outputs — the model keeps generating the most statistically common continuation, which tends to be bland. For factual tasks, low temperature reduces hallucination risk but can also prevent the model from adapting its phrasing to the user's question. Temperature is a tool you choose to match the task; there is no universally correct setting. The question is always: *how much variation is acceptable, and how much randomness does the task benefit from?*

8. The list task (naming three programming languages) showed variation at T=1.5. The same three languages will appear at T=0.0 almost every time. What does the variation at high temperature tell you about what the model "believes" about popular programming languages?

   > *Hint: At T=0, the model always picks the single highest-probability token at each step, which means the highest-probability language name starts the list. At T=1.5, languages with lower (but non-negligible) probability start appearing. The variation shows you the shape of the model's distribution over programming language names — not just the single most-common one.*

---

# Part III: Task-Parameter Matching

## 3. Building a Parameter Policy

Now that you have empirical data, use it to build a principled parameter guide. The table below lists five deployment scenarios. Two are filled in as examples; your team fills in the remaining three.

| Task | Recommended Temperature | Recommended top_p | Recommended top_k | Reasoning |
|------|------------------------|-------------------|-------------------|-----------|
| Legal document summarization | 0.1-0.2 | 0.85 | 20 | Faithfulness to source is paramount; variation is a liability. Low T keeps output close to the most-probable (most-supported) summary; tight top_p and top_k prevent hallucinated details. |
| Marketing tagline generation (10 options) | 1.0-1.3 | 0.95 | 50 | We *want* diverse, creative outputs — the whole point is to explore many options. High T and wide nucleus give the model room to be surprising. We will pick the best option ourselves. |
| Extracting JSON fields from a form | | | | |
| Writing a first-draft blog post intro | | | | |
| Answering student quiz questions with explanation | | | | |

---

### Critical Thinking Questions

9. For the JSON extraction task, argue for or against using top_p=0.50 (very narrow nucleus). What risk does a very narrow nucleus introduce that a slightly wider one (top_p=0.85) avoids?

   > *Hint: With top_p=0.50, if the model is uncertain between two valid JSON field names (e.g., "first_name" vs. "firstName"), one of them might be excluded from the nucleus. The model is forced to pick from the remaining tokens, which might be syntactically invalid. A slightly wider nucleus keeps both plausible options available. The risk of going too narrow is that you exclude correct options when the model is genuinely uncertain about the right answer.*

10. A team member proposes using temperature=0 for *all* tasks in a production agent to ensure reproducibility. What two specific failure modes does this introduce that a moderate temperature (T=0.3-0.5) would mitigate?

    > *Hint: (1) Repetition loops: at T=0 without a repetition penalty, the model can get stuck generating the same token forever because the highest-probability token never changes. (2) Failure to rephrase: if the exact highest-probability phrasing is ambiguous or does not match the user's context, the model cannot adapt — it always produces the same phrasing. A small temperature allows the model to occasionally deviate from the single most likely token and avoid both of these traps.*

11. You are running a Q&A system over a medical reference database. The system retrieves relevant passages (RAG) and asks the model to answer based only on those passages. For the generation step, you should:
   [( )] Use high temperature (T=1.5) to ensure creative, comprehensive answers
   [(X)] Use low temperature (T=0.1-0.3) and low top_p to keep the answer close to the retrieved evidence
   [( )] Use top_k=1 to guarantee the model only repeats the retrieved text verbatim
   [( )] Temperature does not matter when using RAG, since the retrieved context constrains the answer

---

# Part IV: Build Your Own Parameter Guide

## 4. Three Personas, Three Policies

Your team's final deliverable for today is a one-page parameter guide for three deployment personas. Each persona should specify temperature, top_p, top_k, and one "edge case" where you would push toward the boundary of the recommended range.

**Persona 1: Creative Writing Assistant.** Helps users brainstorm novel ideas, character names, plot twists, and opening lines.

**Persona 2: Coding Helper.** Suggests function implementations, explains errors, and writes unit tests. Users expect working code.

**Persona 3: Factual Q&A Bot.** Answers student questions about course content. Users expect accuracy; a wrong answer confidently stated is worse than no answer.

For each persona, fill in:

- Temperature range (e.g., 0.8-1.2)
- top_p setting
- top_k setting
- One scenario where you would go toward the *lower* bound of your temperature range
- One scenario where you would go toward the *upper* bound of your temperature range
- One parameter you would *not* change for this persona and why

The Presenter shares the team's guide with the class. The Reflector identifies where the three guides conflict and what that conflict reveals about parameter trade-offs.

---

## Code Cell

```python
import requests
import time

def query(prompt, model="llama3.2", temperature=1.0, top_p=0.9, top_k=40):
    try:
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False,
                  "options": {"temperature": temperature,
                              "top_p": top_p,
                              "top_k": top_k}},
            timeout=120)
        return r.json()["response"].strip()
    except Exception as e:
        print(f"[query] {e}")
        return ""

# Verify your parameter policies by running the same prompt across your recommended ranges

PERSONAS = {
    "creative_assistant": {
        "prompt": "Suggest an unusual name for a villain in a science fiction novel.",
        "low_t": 0.7, "high_t": 1.3,
        "top_p": 0.95, "top_k": 50,
    },
    "coding_helper": {
        "prompt": "Write a Python function that returns the nth Fibonacci number using recursion.",
        "low_t": 0.1, "high_t": 0.5,
        "top_p": 0.85, "top_k": 20,
    },
    "factual_qa": {
        "prompt": "In what year did World War II end?",
        "low_t": 0.0, "high_t": 0.3,
        "top_p": 0.80, "top_k": 10,
    },
}

for persona, cfg in PERSONAS.items():
    print(f"\n=== {persona.upper()} ===")
    for label, T in [("low-T", cfg["low_t"]), ("high-T", cfg["high_t"])]:
        outputs = [query(cfg["prompt"], temperature=T,
                         top_p=cfg["top_p"], top_k=cfg["top_k"])
                   for _ in range(3)]
        print(f"T={T} ({label}): {outputs}")
        time.sleep(1)
```

---

### Critical Thinking Questions

12. Run the coding helper at T=0.5 (low end) and T=0.5 with top_k=5 (very restricted). Do you notice a difference in output quality? What does restricting top_k further do to code that restricts temperature alone does not?

    > *Hint: Temperature reshapes the whole probability distribution; top_k discards the long tail entirely. In code generation, the long tail includes both rare variable names (which might be acceptable) and invalid syntax tokens (which are never acceptable). Restricting top_k aggressively prevents the model from ever selecting an obviously wrong token, even if temperature would have given it a small but nonzero chance.*

13. A student on your team argues: "We should just use T=0 for all three personas and add a post-processing step to paraphrase or diversify the output." What are the advantages of this approach? What does it lose compared to sampling with appropriate temperature?

    > *Hint: Advantages: reproducibility, debuggability, and the safety of greedy outputs for factual tasks. What it loses: the diversity comes from a second model pass, which introduces its own parameters, cost, and failure modes. The original model's rich probability distribution — which encodes "second-best" and "third-best" options that are linguistically plausible — is thrown away at T=0 before the paraphraser ever sees it.*

---

## Reflection Prompt

**Personal:** Did any experiment produce a result that surprised you? Before today, what was your intuition about what temperature controls — did you think of it as "creativity" or "randomness" or something else? After running the experiments, has your intuition changed, and if so, how?

**Technical:** If temperature controls randomness, why does setting T=0 not guarantee the model gives the correct answer to a factual question? Describe a concrete example from today's experiments (or construct one) where T=0 produced an incorrect but highly confident answer, and explain in terms of probability distributions why that happened.

**Societal:** A medical information chatbot is set to T=0 to minimize hallucination. A creative writing assistant is set to T=1.5. Both decisions seem reasonable for their respective tasks — but what specific risks does *each* setting introduce that the *other* does not? Consider: a T=0 medical bot that is consistently wrong about one rare drug interaction vs. a T=1.5 creative assistant that occasionally produces offensive content. Who is harmed in each scenario, and who bears responsibility?

---

-> **Coming Up Next:** Now that you can reason about output distributions and control them deliberately, the next challenge is getting models to produce *structured* outputs — JSON, tool calls, and typed fields — with high reliability. Agents that call tools need the model to produce exactly the right JSON format, not just approximately correct prose. We will see why low temperature is necessary but not sufficient for reliable tool calls, and what additional techniques (constrained decoding, function calling fine-tunes) close the gap.

---

## Further Reading

- Holtzman et al. "The Curious Case of Neural Text Degeneration." *ICLR* 2020. The paper that introduced nucleus (top-p) sampling and demonstrated that greedy and beam search produce degenerate text.
- Ari Holtzman. "The Distribution of Next Tokens Is Not the Distribution of Good Continuations." (blog post, 2023). A deeper dive into why sampling is harder than it looks.
- Jurafsky and Martin. *Speech and Language Processing*, Chapter 3. Background on language model probabilities and perplexity.
- Ollama documentation: https://ollama.com/docs — parameter reference for temperature, top_p, top_k, and repeat_penalty.
