<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-promptengineering.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-promptengineering.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/liascript/CodeRunner/master/style.css
        https://cdn.jsdelivr.net/gh/liascript/CodeRunner/master/animations.css
        https://cdn.jsdelivr.net/gh/liascript/CodeRunner/master/lia.css
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# Foundations of AI: Prompting & Context Engineering

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals:**

- Define **prompting** and **context engineering** in large language models (LLMs).  
- Explore **prompt design techniques**: zero-shot, few-shot, and chain-of-thought prompting.  
- Analyze how **context windows** and **token limits** constrain LLM capabilities.  
- Experiment with **system prompts, role assignment, and style control**.  
- Compare prompting to fine-tuning in terms of **capability, flexibility, and cost**.  
- Discuss **ethical concerns**: prompt injection, jailbreaks, and human–AI collaboration.  

---

## What is Prompting?

- **Prompting**: The process of providing instructions, examples, or context to guide an AI model’s output.  
- LLMs do not have persistent memory; they respond based on the **current input context window**.  
- Effective prompts structure the model’s reasoning and output format.  

**Example (Zero-Shot):**

```
Translate this sentence into French:
"The cat sits on the mat."
```

Model output → *"Le chat est assis sur le tapis."*

---

## Few-Shot Prompting

Few-shot prompting provides **examples** within the prompt.

**Example:**

```
Translate English to French:
Dog → Chien
House → Maison
Book → Livre
Car →
```

Model output → *"Voiture"*

- Few-shot prompts help models generalize by showing the desired mapping style.  
- But long prompts reduce the available space in the context window.  

---

## Chain-of-Thought (CoT) Prompting

Encourage models to explain reasoning explicitly.

**Example:**

```
Q: If there are 3 cars and each car has 4 wheels, how many wheels are there in total?
A:
```

Model output:
```
Each car has 4 wheels. There are 3 cars. So total wheels = 3 × 4 = 12.
```

- CoT helps models **reduce errors** on multi-step reasoning.  
- However, it can also lead to **hallucinated reasoning** if the model over-explains incorrectly.  

---

## Context Windows & Token Limits

- LLMs process a fixed-length context of tokens: typically 2k–128k tokens.  
- Longer context enables recalling more history, but increases **memory and compute cost**.  
- When context is exceeded, older tokens are dropped.  
- Careful **prompt engineering** helps allocate limited context effectively.  

**Activity:**  
Imagine you are designing a tutoring bot for a multi-step math problem. How would you decide what to keep in the context vs. what to omit?  

{{1}}

---

## System Prompts & Role Assignment

- **System prompt**: establishes global behavior of the model. Example: *“You are a helpful math tutor who explains concepts step by step.”*  
- **Role prompting**: explicitly telling the model to adopt a persona, e.g., *“You are a critical reviewer.”*  
- System messages are often hidden from the user; role prompting can be shown or user-adjusted.  

---

## Prompt Engineering vs. Fine-Tuning

- **Prompting**
  - Cheap, flexible.  
  - Works with general-purpose models.  
  - Limited by context window and susceptibility to **prompt injection** attacks.  

- **Fine-Tuning**
  - Involves retraining on domain-specific data.  
  - More expensive, requires infrastructure.  
  - Produces **permanent, domain-specific behavior**.  

**Discussion Prompt:**
- For education-focused AI systems, when is it preferable to rely on clever prompts vs. investing in fine-tuning a model?  

{{2}}

---

## Hands-On: Prompt Engineering Playground

### Zero-Shot vs Few-Shot

Try this Python snippet:

```python
from openai import OpenAI

client = OpenAI()

prompt_zero = "Translate this sentence into Spanish: The dog runs fast."

prompt_few = "Translate English to Spanish.\nCat → Gato\nHouse → Casa\nTree → Árbol\nDog →"

resp0 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt_zero}]
)

resp1 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt_few}]
)

print("Zero-shot:", resp0.choices[0].message.content)
print("Few-shot:", resp1.choices[0].message.content)
```

---

### Chain-of-Thought Prompting

```python
prompt_cot = "Q: A store sells pencils at 2 for $1. If I buy 7 pencils, how much do I pay?\nA: Let's reason step by step."

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt_cot}]
)

print(resp.choices[0].message.content)
```

- Try prompting with and without the phrase *"Let's think step by step"* and compare reasoning quality.  

---

## Multimodal Prompting

- Modern models (e.g., **CLIP**, **GPT‑4V**, **Stable Diffusion**) accept **text, images, or both**.  
- **Cross‑modal embeddings** allow text to condition image generation.  
- Example: *“Generate a spectrogram of a bird song and then synthesize the corresponding audio.”*  

**Activity:**  
- Use [Stable Diffusion](https://stability.ai/) to generate an image from a text prompt.  
- Try changing the wording slightly — how does it alter the output?  
- Try providing both text *and* an image (if supported) to steer generation.  

---

## Ethical & Societal Considerations

Reading: *The Emerging Problem of AI Psychosis* (Psychology Today)【28:0†syllabus.md】

- **Prompt injection**: malicious inputs that hijack a model’s behavior.  
- **Jailbreaking**: adversarial prompts to bypass safeguards.  
- **Hallucination risk**: VAEs and diffusion models may generate plausible but false information.  
- **Authorship and originality**: Who owns multimodal creations? What about training on copyrighted data?  
- **Safety**: AI‑generated media can amplify misinformation or harmful stereotypes.  

**Discussion Prompt:**  
What responsibilities do developers, educators, and users have in shaping how generative and multimodal AI tools are applied?  

{{3}}

---

## References & Further Reading

- Vaswani et al. (2017). *Attention is All You Need* (Transformers).  
- Ho, Jain, Abbeel (2020). *Denoising Diffusion Probabilistic Models*.  
- Rombach et al. (2022). *High‑Resolution Image Synthesis with Latent Diffusion Models*.  
- Radford et al. (2021). *Learning Transferable Visual Models From Natural Language Supervision (CLIP)*.  
- Mitchell, *Artificial Intelligence: A Guide for Thinking Humans* (Ch. 13).  
- Psychology Today (2025). *The Emerging Problem of AI Psychosis*【28:0†syllabus.md】.  

---
