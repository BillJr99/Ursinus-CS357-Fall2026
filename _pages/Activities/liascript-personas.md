<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-personas.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-personas.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# Foundations of AI: Personas and Configurations

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals:**

- Define **personas** in LLM interaction and explain how they shape responses.  
- Explore **configuration parameters** (temperature, top-k, top-p, etc.) and their effect on creativity vs. determinism.  
- Demonstrate how **system messages** and **configuration settings** combine to establish conversational style.  
- Build **customized chatbot personas** by combining role instructions and parameter settings.  
- Discuss the ethical challenges of **identity, anthropomorphism, and transparency** in persona design.  

---

## What is a Persona?

- A **persona** is a crafted identity assigned to an AI system.  
- Determines **tone, style, domain expertise, and behavior**.  
- Example: *“You are a supportive math tutor who explains concepts step by step.”*  

Personas can:
- Improve user experience by aligning with task goals.  
- Risk misleading users into anthropomorphizing the AI.  

---

## System vs. User vs. Developer Prompts

- **System prompt**: establishes baseline persona.  
- **User prompt**: request from the user.  
- **Developer prompt**: hidden instructions shaping behavior.  

**Example (Combined):**
- System: *“You are a concise medical assistant.”*  
- Developer: *“Never provide diagnosis; only suggest seeking medical attention.”*  
- User: *“I have a headache. What should I do?”*  

---

## Configurations: Temperature & Sampling

- **Temperature (τ):** controls randomness in token sampling.  
  - Low τ (≈0.2): deterministic, repetitive answers.  
  - High τ (≈1.0): creative, varied outputs.  

- **Top-k Sampling:** restricts sampling to the top-k most likely tokens.  
- **Top-p (nucleus) Sampling:** restricts to smallest set of tokens whose cumulative probability ≥ p.  

---

## Code Demo: Configurations in Practice

```python
from openai import OpenAI
client = OpenAI()

system_msg = {"role": "system", "content": "You are a Shakespearean playwright."}

prompt = {"role": "user", "content": "Write a line about the moon."}

resp_lowT = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[system_msg, prompt],
    temperature=0.2
)

resp_highT = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[system_msg, prompt],
    temperature=1.0
)

print("Low temperature:", resp_lowT.choices[0].message.content)
print("High temperature:", resp_highT.choices[0].message.content)
```

---

## Combining Personas with Configurations

**Persona Example:**
- System: *“You are an optimistic motivational coach.”*  
- τ=0.9, top-p=0.95 → more **creative, energetic outputs**.  

**Alternate Persona:**
- System: *“You are a precise legal analyst.”*  
- τ=0.2, top-k=10 → more **consistent, careful outputs**.  

---

## Activity: Persona Swap

Try configuring:
1. A **teacher persona**: patient, step-by-step, low τ.  
2. A **poet persona**: whimsical, metaphorical, high τ.  

Observe:
- How do answers differ to the same factual question?  
- What risks arise if the poet persona gives factual answers in a serious domain?  

{{1}}

---

## Building a Custom Chatbot

1. Choose a **domain** (e.g., medicine, law, education).  
2. Define a **persona description** (system message).  
3. Select **configuration values** (τ, top-k, top-p).  
4. Evaluate chatbot performance on sample queries.  
5. Compare personas across domains.  

**Deliverable (Lab):** Design a chatbot persona aligned with your project’s theme. 【77:0†syllabus.md】

---

## Ethical Considerations

- **Anthropomorphism:** Users may treat the persona as a real being.  
- **Transparency:** Should users be told when they are interacting with a persona?  
- **Responsibility:** Who is accountable if a persona gives harmful advice?  
- **Bias reinforcement:** Personas may inadvertently amplify stereotypes.  

**Reflection Prompt:**
- Imagine designing a medical chatbot. What persona choices and configuration settings could balance empathy with safety?  

{{2}}

---

## References & Further Reading

- Mitchell, *Artificial Intelligence: A Guide for Thinking Humans* (Ch. 13).  
- Boden, *Philosophy of Artificial Intelligence* (Ch. 11).  
- HuggingFace Blog: *The Curious Case of Sampling Strategies in Language Models*.  
- The Verge (2024). *You are a helpful mail assistant, and other Apple Intelligence instructions*.  
- Psychology Today (2025). *The Emerging Problem of AI Psychosis*.  

---
