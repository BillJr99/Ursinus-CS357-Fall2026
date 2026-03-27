<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/liascript-bias.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/liascript-bias.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# Foundations of AI: Bias in AI Systems

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals:**

- Define **bias** in the context of machine learning and AI.  
- Identify sources of bias: data, algorithms, feedback loops, deployment.  
- Demonstrate bias with concrete examples (word embeddings, facial recognition, text generation).  
- Explore **mathematical formulations** of fairness and bias.  
- Analyze strategies for **bias detection, measurement, and mitigation**.  
- Reflect on **societal and ethical implications**.  

---

## 1) What is Bias?

- **Statistical bias:** systematic deviation from ground truth.  
- **Social bias:** reflects inequities and stereotypes from human data.  
- In AI, bias manifests in outputs that systematically disadvantage or misrepresent groups.  

**Example:** A hiring model trained on historical data may disadvantage women if the training set underrepresents female applicants.  

---

## 2) Sources of Bias

1. **Data Bias**  
   - Sampling bias: under/over-representation.  
   - Label bias: annotators’ preconceptions.  
   - Historical bias: reflects existing inequalities.  

2. **Algorithmic Bias**  
   - Model choices may amplify correlations.  
   - Regularization may favor majority classes.  

3. **Feedback Loops**  
   - Biased outputs reinforce themselves when fed back into training data.  

4. **Deployment Bias**  
   - Model used in settings it was not designed for.  

---

## 3) Mathematical Measures of Fairness

For binary classification with groups A and B:

- **Demographic Parity:**
$$
P(\hat{Y}=1 | A) = P(\hat{Y}=1 | B)
$$

- **Equal Opportunity:**
$$
P(\hat{Y}=1 | Y=1, A) = P(\hat{Y}=1 | Y=1, B)
$$

- **Calibration:**
$$
P(Y=1 | \hat{P}=p, A) = P(Y=1 | \hat{P}=p, B)
$$

These definitions often **conflict**; one cannot optimize all at once.  

---

## 4) Demonstration: Word Embedding Bias

- Word2Vec/GloVe embeddings learn semantic relationships.  
- Bias emerges: e.g., *man → computer programmer* is closer than *woman → computer programmer*.  

```python
from gensim.models import KeyedVectors

# Example (requires pretrained embedding file)
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
print(model.most_similar(positive=['woman', 'king'], negative=['man']))
```

- Output often returns *queen*, but analogies may reveal stereotypes.  

---

## 5) Case Studies

- **Facial Recognition:** higher error rates for darker-skinned and female faces (Buolamwini & Gebru, 2018).  
- **Search Engines:** autocomplete and ad delivery reflect gender/racial stereotypes.  
- **LLMs:** may generate biased completions reflecting training corpora.  

---

## 6) Bias Mitigation Strategies

- **Data:** balance datasets, debias labels, audit sources.  
- **Algorithms:** adversarial debiasing, reweighting, fair regularization.  
- **Post-processing:** adjust thresholds, equalize outcomes.  
- **Governance:** audits, transparency reports, ethics review boards.  

---

## 7) Ethical & Societal Implications

- Bias in AI systems can reinforce systemic inequalities.  
- Need to balance **fairness metrics** with context-specific considerations.  
- Anthropomorphizing bias: AI is not malicious; bias comes from human systems.  

**Discussion Prompt:**  
How should AI practitioners weigh trade-offs between accuracy and fairness when they conflict?  

{{1}}

---

## 8) Activity: Bias Audit

- Select a dataset (e.g., text, images, tabular).  
- Train a simple classifier.  
- Measure demographic parity and equal opportunity.  
- Propose a mitigation strategy.  

**Deliverable:** short report with findings and reflections.  

---

## References & Further Reading

- Buolamwini & Gebru (2018). *Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification*.  
- Barocas, Hardt, Narayanan (2019). *Fairness and Machine Learning*.  
- Mehrabi et al. (2021). *A Survey on Bias and Fairness in Machine Learning*.  
- Mitchell, *Artificial Intelligence: A Guide for Thinking Humans* (Ch. 8).  
- Psychology Today (2025). *The Emerging Problem of AI Psychosis*.  

---
