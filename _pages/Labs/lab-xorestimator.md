---
layout: assignment
permalink: Labs/XOREstimator
title: "Lab: XOR Formula Estimator (Step‑by‑Step Tutorial)"

info:
  points: 100
  goals:
    - Understand why XOR is not linearly separable and how a small NN solves it.
    - Read weights/biases from an interactive model (TensorFlow Playground) to derive an explicit formula.
    - Fit a linear estimator to XOR, evaluate failure modes, and reason about feature engineering.
  rubric:
    - weight: 30
      description: Implementation
      preemerging: Provides a working implementation aligned to the assignment specification with simple tests.
      beginning: Implements the core functionality accurately and demonstrates usage on representative inputs.
      progressing: Implements the full specification with clear structure, tests, and discussion of edge cases.
      proficient: Delivers a robust, well‑structured implementation with comprehensive tests and justified design choices.
    - weight: 30
      description: Algorithmic Correctness and Reasoning
      preemerging: Explains the algorithmic approach and verifies outputs on basic cases.
      beginning: Explains design decisions and validates outputs on typical cases with reasoning.
      progressing: Provides correctness arguments and empirical checks across varied cases.
      proficient: Presents clear correctness reasoning and evidence of generalization with insightful error analysis.
    - weight: 20
      description: Code Quality and Documentation
      preemerging: Organizes code into readable units with brief inline comments.
      beginning: Uses functions/modules and docstrings to clarify behavior and interfaces.
      progressing: Maintains consistent style, meaningful names, and explanatory docs where non‑trivial.
      proficient: Exhibits clean architecture, thoughtful abstractions, and thorough documentation throughout.
    - weight: 10
      description: Design Report
      preemerging: Summarizes goals, approach, and evaluation setup.
      beginning: Explains design decisions and trade‑offs with small‑scale results.
      progressing: Details design rationale, experiments, and limitations with supporting figures/tables.
      proficient: Delivers a concise, well‑structured report with justified choices and actionable future work.
    - weight: 10
      description: Submission Completeness
      preemerging: Provides required artifacts and basic run instructions.
      beginning: Includes all artifacts with clear run instructions and parameters.
      progressing: Includes scripts, configs, and reproducible steps with sample data.
      proficient: Provides a fully reproducible package with results, seeds, and validation notes.

tags:
  - ai
---

# Overview

In this lab we will walk through training a neural network to learn the bitwise XOR function using three stages:

1. **Playground Walkthrough (no coding):** Train a tiny NN on XOR in TensorFlow Playground and **read off** the weights.
2. **From Weights → Formula:** Use those weights to write an explicit formula for \(Z = \operatorname{XOR}(A_1, A_2)\) via hidden neurons.
3. **Linear Estimator (coding):** Fit a **linear** model to the XOR truth table; evaluate performance vs. the NN, and discuss why checking **two accuracies** is useful.

---

## The XOR Function

The **exclusive OR (XOR)** is a classic logical function that outputs **true (1)** when exactly one of its two inputs is true, and **false (0)** otherwise. It is often denoted as:

\[
Z = A_1 \oplus A_2
\]

where \(A_1, A_2 \in \{0,1\}\).

XOR is fundamental in AI and machine learning because it is **not linearly separable**: no single straight line (or hyperplane) can perfectly classify XOR in the input space. This property makes it a canonical example for demonstrating the need for **nonlinear models** and **hidden layers** in neural networks.

### XOR Truth Table

| \(A_1\) | \(A_2\) | \(Z = A_1 \oplus A_2\) |
|---------|---------|-------------------------|
|    0    |    0    |            0            |
|    0    |    1    |            1            |
|    1    |    0    |            1            |
|    1    |    1    |            0            |

### Key Observations
- XOR outputs **1** when inputs differ, **0** when they are the same.
- A single linear classifier cannot solve XOR.
- Adding nonlinear transformations or hidden units allows a neural network to represent XOR correctly.

---

## Stage 1 — TensorFlow Playground: Solve XOR and Read the Weights (no coding)

Open this preset link to the XOR dataset:

<https://playground.tensorflow.org/#activation=tanh&batchSize=10&dataset=xor&regDataset=reg-plane&learningRate=0.03&regularizationRate=0&noise=0&networkShape=4,2&seed=0.40997&showTestData=false&discretize=false&percTrainData=50&x=true&y=true&xTimesY=false&xSquared=false&ySquared=false&cosX=false&sinX=false&cosY=false&sinY=false&collectStats=false&problem=classification&initZero=false&hideText=false>

**Instructions**

1. Click **Play** and let it train until training loss stabilizes (or accuracy \(> 0.95\)).  
2. **Pause** training. Click on each hidden neuron to view its **incoming weights** (from \(A_1\) and \(A_2\)) and its **bias**. Record these in your notes:  
   \(h_j = \tanh(w_{j1} A_1 + w_{j2} A_2 + b_j)\).
3. Click the output neuron to view **outgoing weights** \(v_j\) from hidden neurons and output bias \(c\). Record:  
   \(\hat{Z} = \sigma\!\big(\sum_j v_j h_j + c\big)\).
4. Sketch the **decision regions** you see. Which hidden neurons carve out which quadrants? How does the output combine them to realize XOR?

**Checkpoint (report briefly):**
- Write the specific numeric formula you observed (fill in your \(w_{j1}, w_{j2}, b_j, v_j, c\)).
- Explain (in words) how two perpendicular hidden hyperplanes make XOR possible.

---

## Stage 2 — From Weights to an Explicit XOR Formula (derivation, light algebra)

We now turn the Playground parameters into an explicit function that maps \((A_1, A_2) \in \{0,1\}^2\) to \(Z\in\{0,1\}\).

**Given** your recorded parameters:

- Hidden units: \(h_j = \tanh(w_{j1} A_1 + w_{j2} A_2 + b_j)\).
- Output: \(\hat{Z} = \sigma\!\Big(\sum_j v_j h_j + c\Big)\).

**Tasks**

1. Substitute \(A_1, A_2\in\{0,1\}\) and compute \(h_j\) for the **four truth‑table inputs**:  
   \((0,0), (0,1), (1,0), (1,1)\).
2. Evaluate \(\hat{Z}\) for all four inputs and threshold at 0.5 to obtain predicted bits. Confirm XOR is realized.
3. (Optional) Use the **sign approximation** for \(\tanh\) to reason geometrically: the hidden neurons implement two half‑planes that, when linearly combined, produce XOR.

**Deliverable:** A concise **formula** filled with your numeric weights, plus a **table** of the four evaluations.

---

## Stage 3 — Linear Function Estimator on XOR (coding)

In this part you will train a **linear model** \(\hat{Z} = w_1 A_1 + w_2 A_2 + b\) on the XOR truth table and evaluate it. You may refer back to the earlier **Linear Function Estimator** lab for gradient descent patterns.

### 3.1 Data: XOR Truth Table

```python
import numpy as np

# Truth table (A1, A2) -> Z = XOR(A1, A2)
X_tt = np.array([
    [0., 0.],
    [0., 1.],
    [1., 0.],
    [1., 1.],
], dtype=np.float64)
Z_tt = np.array([0., 1., 1., 0.], dtype=np.float64)
```

### 3.2 Linear Estimator (MSE fit)

```python
# Initialize parameters
rng = np.random.default_rng(0)
w = rng.normal(size=(2,))
b = rng.normal()

# Training hyperparameters
lr = 0.1
steps = 2000

for t in range(steps):
    # forward
    yhat = X_tt @ w + b                   # (4,)
    err = yhat - Z_tt
    loss = np.mean(err**2)

    # backward (d/dw MSE): 2/N X^T (yhat - y)
    grad_w = 2.0/len(X_tt) * (X_tt.T @ err)
    grad_b = 2.0/len(X_tt) * err.sum()

    # update
    w -= lr * grad_w
    b -= lr * grad_b

print({"w": w, "b": b, "loss": loss})
print(f"Linear formula: Z_hat = {w[0]:.3f}*A1 + {w[1]:.3f}*A2 + {b:.3f}")
```

**Checkpoint:** Does the **linear** model achieve zero error on the four truth‑table points? Why/why not? (Recall: XOR is **not** linearly separable.)

### 3.3 Evaluate Two Accuracies (why this matters)

1. **Generalization accuracy** on *new random test points* sampled from \(\{0,1\}^2\).
2. **Self‑consistency accuracy**: Feed the **original truth‑table inputs** through your **trained Playground NN** *without labels* and compare its predictions with the ground truth.

```python
# 1) Accuracy on random test points
num_tests = 200
X_test = np.stack([rng.integers(0, 2, size=num_tests), rng.integers(0, 2, size=num_tests)], axis=1).astype(float)
Z_true = (X_test[:,0] != X_test[:,1]).astype(float)
Z_lin = (X_test @ w + b >= 0.5).astype(float)
acc_lin_random = (Z_lin == Z_true).mean()
print("Linear accuracy on random XOR test points:", acc_lin_random)

# 2) Accuracy of the trained NN on the original truth table
# (You will manually enter the NN’s formula from Stage 2 into a function.)

def nn_playground_predict(A1, A2):
    # TODO: Replace the placeholders with your recorded weights from Stage 1.
    # Example with H hidden units, tanh in hidden, sigmoid at output.
    # h_j = tanh(wj1*A1 + wj2*A2 + bj); Z_hat = sigmoid(sum_j vj*h_j + c)
    # Fill: wj1, wj2, bj, vj, c using your Playground values.
    raise NotImplementedError

# Evaluate on the four truth-table points
from math import isclose
sig_nn = []
for a1, a2, z in zip(X_tt[:,0], X_tt[:,1], Z_tt):
    # TODO: zhat = nn_playground_predict(a1, a2)
    # TODO: sig_nn.append( (zhat >= 0.5) == (z == 1.0) )
    pass

# TODO: acc_nn_truth = np.mean(sig_nn)
# print("NN accuracy on original truth-table inputs:", acc_nn_truth)
```

**Questions to answer in your report**
- Why is it useful to compute **both** accuracies? What might it mean if the linear model’s random‑test accuracy is high but the NN’s truth‑table accuracy is low (or vice versa)? Consider overfitting, calibration thresholds (0.5), and numerical quirks.
- If your NN and linear accuracies differ, which model’s behavior do you trust more for XOR, and why?

---

## (Optional) Stage 4 — Make Linear Work via Feature Engineering

Add the interaction feature \(A_1\cdot A_2\) (or a nonlinear basis) so that a linear model in the **augmented** space can fit XOR.

```python
X_aug = np.c_[X_tt, (X_tt[:,0]*X_tt[:,1])]

# Re‑fit linear model on augmented features
w = rng.normal(size=(3,))
b = rng.normal()
for t in range(2000):
    yhat = X_aug @ w + b
    err = yhat - Z_tt
    grad_w = 2.0/len(X_aug) * (X_aug.T @ err)
    grad_b = 2.0/len(X_aug) * err.sum()
    w -= 0.1 * grad_w
    b -= 0.1 * grad_b

pred = (X_aug @ w + b >= 0.5).astype(float)
print("Augmented‑linear accuracy on XOR truth table:", (pred == Z_tt).mean())
print(f"Augmented formula: Z_hat = {w[0]:.3f}*A1 + {w[1]:.3f}*A2 + {w[2]:.3f}*(A1*A2) + {b:.3f}")
```

**Reflection:** What does this say about **representation** vs. **learning**? How does the NN implicitly learn useful features that make XOR linearly solvable at the output layer?

---

# What to Submit

1. **Notes** with your recorded Playground weights, explicit formula, and truth‑table evaluation.  
2. **Code** for Stage 3 (and Stage 4 if you attempt it).  
3. A **short report** (1–2 pages) answering the Checkpoint questions and discussing accuracy differences and their meaning.
