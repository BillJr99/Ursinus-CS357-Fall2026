---
layout: assignment
permalink: /Assignments/PromptPatterns
title: "CS357: Foundations of Artificial Intelligence - Written Assignment: Prompt Patterns and AI by Hand"

info:
  coursenum: CS357
  points: 100
  goals:
    - To design and document reusable prompt patterns including personas, few-shot examples, and structured output
    - To demonstrate empirically how prompt elements change model behavior
    - To compute softmax with temperature and a cosine similarity by hand, in the AI by Hand tradition
    - To connect by-hand mathematics to observed sampling and retrieval behavior
  rubric:
    - weight: 35
      description: Prompt Pattern Portfolio
      preemerging: Few or no patterns are presented, or patterns lack any demonstration
      beginning: Patterns are presented but demonstrations are missing or do not isolate the pattern's effect
      progressing: All required patterns are presented with before and after demonstrations, with limited analysis of why each works
      proficient: All required patterns are presented with controlled before and after demonstrations, and each is analyzed with reference to the distributional behavior of language models
    - weight: 35
      description: AI by Hand Worked Problems
      preemerging: Worked problems are missing or fundamentally incorrect
      beginning: Worked problems contain arithmetic or conceptual errors, or omit intermediate steps
      progressing: Worked problems are correct with all intermediate steps shown, with a minor omission
      proficient: Worked problems are correct with all intermediate steps shown, and each is verified in code with matching results and a sentence connecting the math to observed model behavior
    - weight: 20
      description: Analysis and Synthesis
      preemerging: Little or no written analysis is provided
      beginning: Analysis restates results without interpretation
      progressing: Analysis interprets results and connects at least one finding to course concepts
      proficient: Analysis interprets results, connects findings to sampling theory and persona effects, and proposes one testable hypothesis for future investigation
    - weight: 10
      description: Writeup and Submission
      preemerging: An incomplete submission is provided
      beginning: The work is submitted, but not according to the directions in one or more ways
      progressing: The work is submitted according to the directions with a minor omission or correction needed
      proficient: The work is submitted according to the directions, well organized, with thoughtful answers to the reflection prompts
  readings:
    - rtitle: "Prompt Engineering Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-promptengineering.md"
    - rtitle: "Sampling and Generation Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-samplinggeneration.md"
    - rtitle: "AI by Hand, Tom Yeh"
      rlink: "https://www.scribd.com/document/726922630/AI-by-Hand-Vol-1"

tags:
  - prompting
  - written
  - ai

---

In this assignment you will build a portfolio of four reusable prompt patterns and work two mathematics problems by hand that explain why those patterns work. This connects your prompting practice to the underlying theory covered in class: temperature controls probability sharpness, cosine similarity drives retrieval, and personas shift the sampling distribution. By the end, you will be able to construct prompts with documented, reproducible effects and explain the statistical reason each pattern produces the change it does. These skills transfer directly to building production agents, where prompt patterns are engineering decisions that must be justified and tested.

---

## What a Strong Submission Looks Like

A strong submission has these qualities:

- **Controlled comparisons.** The baseline and pattern-enhanced prompts differ in exactly one thing — the pattern being studied. The temperature and seed are fixed and stated. The reader can reproduce both outputs.
- **Mechanism, not description.** The analysis does not just say "the persona made it more formal." It says: "Adding a persona likely shifts the probability distribution toward domain vocabulary by conditioning on tokens that would appear in texts written by an expert in this field. This is consistent with the increase in technical terminology we observed in the output."
- **Clean math with verification.** Every intermediate step is shown. The Python verification produces the same numbers to three decimal places. If there is a discrepancy, the student explains it (for example: floating-point rounding in the built-in `math.exp` vs. the manual calculation).

A weak submission shows two outputs side by side and says "the persona made it better" without explaining what "better" means or why the pattern caused it. It also omits intermediate steps in the math or skips the Python verification.

---

## Experimental Protocol (State This at the Top of Your Portfolio)

Before presenting any pattern, state your protocol in one paragraph:
- What model you used (name and version)
- What temperature and seed you fixed for all comparisons
- How you ran the model (Ollama CLI, Python `requests`, Jupyter notebook)
- How you ensured both prompts were otherwise identical

Use a fixed temperature and seed for all comparisons so the pattern — not the sampling — explains the difference.

---

## Part 1: Prompt Pattern Portfolio

For each of the four patterns below, produce a **pattern entry** with the following structure:

### Pattern Entry Template

**Pattern Name:**

**Baseline Prompt** (copy-paste verbatim):
> [your baseline prompt here]

**Baseline Output** (copy-paste verbatim, truncated to 150 words if long):
> [model output here]

**Pattern-Enhanced Prompt** (copy-paste verbatim, with the pattern change highlighted or labeled):
> [your enhanced prompt here]

**Pattern-Enhanced Output** (copy-paste verbatim, truncated to 150 words if long):
> [model output here]

**Analysis** (2-3 paragraphs): What changed between the outputs? Why did the pattern cause that change, in terms of probability distributions, token conditioning, or sampling behavior? What would a second controlled experiment be needed to confirm your hypothesis?

---

### Pattern 1: Persona and Role

Choose a domain you know well (your major, a hobby, a job). Design a persona for an expert in that domain. Show a question where the persona materially changes the response — not just the tone, but the content, vocabulary, or structure of the answer.

Write 2-3 paragraphs in your analysis: (1) Describe the specific change you observed. (2) Explain why conditioning on a persona shifts what tokens the model predicts. (3) Name one scenario where a persona would be harmful to include.

### Pattern 2: Few-Shot Examples

Choose a formatting or transformation task that the bare model performs inconsistently — for example, converting informal meeting notes into bullet-point action items, or transforming verbose sentences into telegraphic ones. Show that providing two or three input-output examples in the prompt stabilizes the output format across five runs. Report: what format did the model produce without examples (describe the variation), and what format did it produce with examples (describe the consistency)?

Write 2-3 paragraphs in your analysis: (1) What specifically became consistent? (2) Why do examples work — what are they doing to the model's context? (3) Is there a task where few-shot examples could introduce bias rather than reducing it?

### Pattern 3: Structured Output

Demand a JSON schema from the model and demonstrate that a Python `json.loads()` call succeeds on the output across five runs. Run the bare prompt five times and report the parse success rate. Run the schema-constrained prompt five times and report the parse success rate. Present this as a simple table:

| Run | Bare Prompt Parseable? | Schema Prompt Parseable? |
|-----|------------------------|--------------------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| **Success rate** | **/5** | **/5** |

Write 2-3 paragraphs in your analysis: (1) What was the success rate difference? (2) Why does requesting JSON not guarantee valid JSON? (3) What would you add to your prompt or your post-processing code to make the success rate reach 5/5 reliably?

### Pattern 4: Guardrails

Add a refusal or escalation instruction to a system prompt — for example: "If the user asks for medical advice, respond: 'I am not a medical professional. Please consult a doctor.' Do not attempt to answer medical questions." Demonstrate: (a) one case where the guardrail triggers correctly, and (b) one attempted circumvention — a prompt that tries to get the model to answer anyway — and report the outcome.

Write 2-3 paragraphs in your analysis: (1) Did the circumvention succeed or fail? (2) What does this reveal about the robustness of instruction-following versus the robustness of value-trained refusal? (3) Under what conditions would you trust a guardrail like this for a production system?

---

## Part 2: AI by Hand

Complete both problems with all intermediate steps shown. Handwritten and scanned, or typeset, your choice. After each problem, paste a short Python snippet that verifies your result.

### Problem 1: Softmax with Temperature

**Setup:** You have three tokens A, B, and C with logits $z = (4, 2, 1)$.

**Task:** Compute the full softmax probability distribution $P(T)$ at three temperature settings: $T = 1$, $T = 0.5$, and $T = 2$.

The formula is:
$$P_i(T) = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}$$

**Show all of the following for each temperature:**
1. The scaled logits $z_i / T$ for each token
2. The exponentials $e^{z_i / T}$ for each token (to four decimal places)
3. The normalizing sum $\sum_j e^{z_j / T}$
4. The final probability for each token (to three decimal places)

Then fill in this summary table:

| Temperature | P(A) | P(B) | P(C) | Sum |
|---|---|---|---|---|
| T = 0.5 | | | | 1.000 |
| T = 1.0 | | | | 1.000 |
| T = 2.0 | | | | 1.000 |

**Write two sentences** stating what your numbers demonstrate about temperature and the sharpness of the distribution. Specifically: what happens to the probability of the highest-logit token as temperature decreases toward zero?

**Python verification:**
```python
import numpy as np

logits = np.array([4.0, 2.0, 1.0])

for T in [0.5, 1.0, 2.0]:
    scaled = logits / T
    exp_scaled = np.exp(scaled)
    probs = exp_scaled / exp_scaled.sum()
    print(f"T={T}: {probs.round(3)}")
```

Paste your output and confirm it matches your hand calculation.

### Problem 2: Cosine Similarity

**Setup:** You have two vectors: $\mathbf{a} = (2, 1, 0, 2)$ and $\mathbf{b} = (1, 1, 1, 1)$.

**Task:** Compute the cosine similarity between $\mathbf{a}$ and $\mathbf{b}$.

The formula is:
$$\cos(\mathbf{a}, \mathbf{b}) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \cdot \|\mathbf{b}\|}$$

**Show all of the following:**
1. The dot product $\mathbf{a} \cdot \mathbf{b}$ (element-by-element multiplication and sum)
2. The norm $\|\mathbf{a}\| = \sqrt{\sum_i a_i^2}$ (show the sum of squares)
3. The norm $\|\mathbf{b}\|$ (show the sum of squares)
4. The cosine similarity (to three decimal places)

**Second calculation:** Now compute $\cos(\mathbf{a},\ 3\mathbf{a})$. Work it out by hand and show why the result is exactly 1.000. Then write one sentence explaining why this property matters for comparing document embeddings of different lengths.

**Python verification:**
```python
import numpy as np

a = np.array([2.0, 1.0, 0.0, 2.0])
b = np.array([1.0, 1.0, 1.0, 1.0])

def cosine_sim(x, y):
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))

print(f"cos(a, b) = {cosine_sim(a, b):.3f}")
print(f"cos(a, 3a) = {cosine_sim(a, 3*a):.3f}")
```

Paste your output and confirm it matches.

---

## Analysis and Synthesis

After completing both parts, write one to two paragraphs addressing all three questions:

1. Which pattern produced the largest behavioral change for the smallest prompt change, and why do you think that is? Ground your answer in the mathematics — what did adding that pattern do to the tokens the model was predicting?
2. After computing softmax by hand, restate in your own words where the "randomness" in a language model lives. Is the randomness in the network weights, in the logits, or in the sampling step? What does temperature control specifically?
3. Propose one testable hypothesis about prompt patterns or model behavior that you could investigate with a controlled experiment. State the hypothesis, the independent variable, the dependent variable, and how you would measure it.

---

## Frequently Asked Questions

**Q: Do I need to run every prompt five times for all four patterns, or just for the JSON one?**
A: Five runs are explicitly required only for Pattern 3 (structured output). For Patterns 1, 2, and 4, you need at least one baseline output and one pattern-enhanced output under fixed settings. If you want to show consistency, running more is better, but the rubric requires controlled comparison, not a large-scale experiment.

**Q: My Python verification gives slightly different numbers than my hand calculation. Is that a problem?**
A: Minor floating-point differences (for example, 0.843 vs. 0.8427) are expected and acceptable. Explain the source of the discrepancy in one sentence. If the difference is larger than 0.01, recheck your hand calculation — a larger gap indicates an arithmetic error.

**Q: My guardrail was bypassed in Pattern 4. Should I hide that?**
A: No — report it honestly. A circumvention that succeeds is more interesting than one that fails, and your analysis of why it succeeded is what earns points. Documenting a real limitation is better than pretending the guardrail is robust.

**Q: Can I use a model other than llama3.2?**
A: Yes, as long as you name the model and version. The rubric grades your analysis and methodology, not your choice of model.

**Q: Do I need to typeset the math in LaTeX?**
A: No. Handwritten and scanned is explicitly accepted. If you type it, any legible format (plain text with exponents noted as `e^x`, Markdown with LaTeX, a Word document) is fine. What matters is that every intermediate step is visible.

---

## Deliverables

Submit a single PDF containing:
- Your stated experimental protocol
- All four pattern entries (baseline prompt, enhanced prompt, both outputs, analysis)
- Both worked math problems with all intermediate steps shown
- The Python verification snippets and their output
- Your analysis and synthesis (one to two paragraphs)
- Your reflection responses
- Software version information (model name and version, Python version, Ollama version)

---

## Reflection Prompts

- Which pattern produced the largest behavioral change for the smallest prompt change, and why do you think that is?
- After computing softmax by hand, restate in your own words where the "randomness" in a language model lives.
- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
