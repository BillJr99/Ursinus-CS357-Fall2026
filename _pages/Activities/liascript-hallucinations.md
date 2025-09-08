<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/liascript-hallucinations.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/liascript-hallucinations.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/liascript/CodeRunner/master/style.css
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# Foundations of AI: Hallucinations in Generative Models

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals:**

- Define **hallucination** in generative AI systems.  
- Distinguish between types: factual errors, fabricated sources, logical inconsistencies.  
- Explore **causes**: probabilistic text generation, training data gaps, alignment trade-offs.  
- Demonstrate hallucinations with simple examples.  
- Analyze strategies for **detection and mitigation** (RAG, citations, self-checking, guardrails).  
- Discuss **ethical and societal implications** of hallucinated outputs.  

---

## 1) What Are Hallucinations?

- Hallucinations are outputs that are **fluent but false**.  
- Unlike bias (systematic error), hallucinations are often **unpredictable and ad hoc**.  
- Can occur in text, images, or multimodal generations.  

**Example:**
- Prompt: *“Who won the Nobel Prize in Physics in 2025?”*  
- Model (trained to 2023): *“Dr. Jane Doe for quantum gravity”* (fabricated).  

---

## 2) Types of Hallucinations

1. **Factual Hallucination**: model states incorrect facts.  
2. **Source Hallucination**: cites nonexistent papers or URLs.  
3. **Logical Hallucination**: flawed reasoning chains.  
4. **Multimodal Hallucination**: image depicts impossible objects (e.g., “two suns in the sky”).  

---

## 3) Why Do Hallucinations Happen?

- LLMs optimize **next-token likelihood**, not truth.  
- **Training data gaps**: model interpolates beyond seen facts.  
- **Temperature/sampling**: higher randomness increases risk.  
- **Alignment trade-offs**: optimizing helpfulness and creativity may reduce factuality.  

Mathematically:

$$
P(y|x) = \prod_t P(y_t | y_{<t}, x)
$$

Even if $P$ is locally likely, the global sequence may be untrue.  

---

## 4) Demonstration: Fabricated Sources

```python
from openai import OpenAI
client = OpenAI()

query = "Give me 2 academic references on unicorn biology."
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": query}]
)
print(resp.choices[0].message.content)
```

- Likely output: fabricated authors, journals.  
- Shows models “fill in” plausible references.  

---

## 5) Mitigation Strategies

- **Retrieval-Augmented Generation (RAG):** ground outputs in external docs.  
- **Citations with verification:** require outputs to include links that are checked.  
- **Self-check prompts:** “Double-check the above answer for factual errors.”  
- **Calibration:** expose uncertainty; avoid overconfidence.  
- **Post-hoc filtering:** detect and flag hallucinations with classifiers.  

---

## 6) Activity: Spot the Hallucination

- Provide students with 3 model-generated answers.  
- Ask: which facts are correct, which are hallucinated?  
- Verify using search or trusted sources.  

**Deliverable:** short explanation of how hallucinations were identified.  

{{1}}

---

## 7) Ethical & Societal Implications

- **Misinformation:** hallucinations spread quickly in social media.  
- **Accountability:** who is responsible for false claims?  
- **Trust erosion:** repeated hallucinations reduce confidence in AI tools.  
- **Anthropomorphism risk:** framing errors as “psychosis” vs. statistical prediction.  

**Discussion Prompt:**
- Should AI systems be required to clearly signal uncertainty in outputs?  

{{2}}

---

## 8) References & Further Reading

- Ji et al. (2023). *Survey of Hallucination in Natural Language Generation*.  
- Shuster et al. (2021). *Retrieval-Enhanced Transformer Models*.  
- Mitchell, *Artificial Intelligence: A Guide for Thinking Humans* (Ch. 14).  
- Psychology Today (2025). *The Emerging Problem of AI Psychosis*.  

---
