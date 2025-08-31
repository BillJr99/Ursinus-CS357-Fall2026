<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2025/blob/gh-pages/_pages/Activities/liascript-neuralnets.md or locally if deployed via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2025/gh-pages/_pages/Activities/liascript-neuralnets.md (liascript renderer is required to share classroom backend)

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
        
script: |
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js"
      onload="renderMathInElement(document.body);"></script>        
-->

# Foundations of AI: Neural Networks

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals:**

- Explain the computational model of an artificial neuron and the role of activation functions.
- Derive gradient-based learning rules and implement a minibatch training loop.
- Distinguish between under/over-parameterization and diagnose bias/variance.
- Apply regularization (\(\ell_2\), dropout, early stopping) and normalization (batch/layer norm).
- Evaluate models using accuracy, precision/recall, ROC-AUC, calibration, and confusion matrices.
- Reflect on ethical considerations: dataset bias, fairness, interpretability, and reproducibility.
- Work through a full backpropagation derivation (single hidden layer) and reason about convergence.

---

## What Is a Neural Network?

A **neural network (NN)** is a parameterized function \( f_\theta: \mathbb{R}^d \to \mathbb{R}^k \) composed of affine maps and nonlinearities. In its simplest form:

\[
\hat{y} = f_\theta(x) = W_2\,\sigma(W_1 x + b_1) + b_2
\]

where \(\sigma\) is an activation function applied elementwise. Key ideas:

- **Representation**: Depth and width govern function expressivity.
- **Learning**: Parameters \(\theta=(W,b)\) are learned by minimizing an empirical risk via gradient descent.
- **Generalization**: Performance on unseen data depends on hypothesis class, regularization, and data distribution.

---

## The Artificial Neuron & Activation Functions

**Neuron**: \(z = w^\top x + b\), \(a = \sigma(z)\)

- **Sigmoid**: \(\sigma(z)=1/(1+e^{-z})\). Pros: smooth probability-like output. Cons: saturation, vanishing gradients.
- **Tanh**: zero-centered; also saturates.
- **ReLU**: \(\max(0,z)\); sparse activations; can "die".
- **Leaky/Parametric ReLU, GELU**: mitigate dead ReLUs and improve gradient flow.
- **Softmax** for multiclass probabilities: \(p_i = \frac{e^{z_i}}{\sum_j e^{z_j}}\).

**Universal Approximation**: A single hidden layer with a non-polynomial activation can approximate continuous functions on compact sets to arbitrary precision (Cybenko, 1989; Hornik, 1991).

---

## Chain Rule & Backprop (One-Hidden-Layer)

We analyze a scalar-in, scalar-out network with one hidden neuron (generalizes to many):

- Net input to hidden: \( z = w\,x + b \)
- Hidden activation: \( h = f(z) \) (e.g., ReLU, tanh, sigmoid)
- Output: \( \hat{y} = v\,h + c \)
- Loss (per-example MSE): \( L = \tfrac{1}{2}(y - \hat{y})^2 \)

**Gradients**

\[
\frac{\partial L}{\partial \hat{y}} = \hat{y}-y,\quad
\frac{\partial L}{\partial v} = (\hat{y}-y)h,\quad
\frac{\partial L}{\partial c} = (\hat{y}-y)
\]

\[
\frac{\partial L}{\partial h} = (\hat{y}-y)v,\quad
\frac{\partial L}{\partial z} = (\hat{y}-y)v\,f'(z)
\]

\[
\boxed{\frac{\partial L}{\partial w} = (\hat{y}-y)v\,f'(z)\,x},\qquad
\boxed{\frac{\partial L}{\partial b} = (\hat{y}-y)v\,f'(z)}
\]

---

## Convergence: What It Looks Like

- **Empirical risk** typically **decreases** over epochs; validation loss should decrease then stabilize.  
- **Learning rate** controls step size; too large → divergence/oscillation; too small → slow progress.  
- **Stochasticity** (minibatches) adds noise that can **help escape shallow minima**.

---

## Notebook Overview: Linear Function Estimator (Single-Layer)

**What the code does**

- Generates synthetic linear data \(y = a^\star x + b^\star + \epsilon\).
- Defines a single-layer linear model \(\hat{y} = w x + b\) (no hidden layer).
- Uses MSE loss and gradient descent/Adam to recover \(w,b\).
- Plots training loss and compares learned vs. true line.

**Math performed**

- Forward: \(\hat{y}_i = w x_i + b\)  
- Loss: \( \mathcal{L} = \frac{1}{n}\sum_i (y_i - \hat{y}_i)^2 \)  
- Gradients:
  \[
  \frac{\partial \mathcal{L}}{\partial w} = -\frac{2}{n}\sum_i x_i(y_i-\hat{y}_i),\qquad
  \frac{\partial \mathcal{L}}{\partial b} = -\frac{2}{n}\sum_i (y_i-\hat{y}_i)
  \]

**Key takeaways**

- Closed-form solution exists (OLS), but gradient descent sets up for neural nets.
- Visualizes convex loss surface and stable convergence with proper \(\eta\).

---

## Open Colab: Linear Function Estimator (Single-Layer)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BillJr99/Ursinus-CS357-Fall2025/blob/gh-pages/files/notebooks/LinearFunctionEstimatorNN.ipynb)

---

## Notebook Overview: Linear Function Estimator (Multi-Layer)

**What the code does**

- Extends to a small MLP: \( \hat{y} = W_2\,\sigma(W_1 x + b_1) + b_2 \).
- Still fits (possibly) linear or piecewise-linear mappings depending on \(\sigma\).
- Compares optimizers (SGD vs. Adam) and capacity (hidden width).

**Math performed**

- Forward pass as above; MSE loss.  
- Backprop (vectorized):
  \[
  \delta^{(2)} = \hat{y}-y,\quad
  \frac{\partial \mathcal{L}}{\partial W^{(2)}}=\delta^{(2)}h^\top,\quad
  \delta^{(1)}=(W^{(2)})^\top\delta^{(2)}\odot \sigma'(z^{(1)}),\quad
  \frac{\partial \mathcal{L}}{\partial W^{(1)}}=\delta^{(1)}x^\top
  \]

**Key takeaways**

- With nonlinearity, depth increases expressivity even on simple data.
- Proper initialization (He/Glorot) and learning-rate choice are critical.

---

## Open Colab: Linear Function Estimator (Multi-Layer)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BillJr99/Ursinus-CS357-Fall2025/blob/gh-pages/files/notebooks/LinearFunctionEstimatorMultiLayerNN.ipynb)

---

## Notebook Overview: Nonlinear Function Estimator (MLP)

**What the code does**

- Samples from a nonlinear target (e.g., \(y=\sin(2\pi x)+\epsilon\)).
- Trains an MLP with hidden width \(m\) and activation \(\sigma\) to approximate it.
- Compares bias/variance by sweeping \(m\) and plotting validation error.

**Math performed**

- Forward: \( h=\sigma(W^{(1)}x+b^{(1)}),\ \hat{y}=W^{(2)}h+b^{(2)} \).  
- Regularization: weight decay adds \(\lambda\lVert W\rVert_2^2\) to the loss.  
- Early stopping monitors validation loss \( \mathcal{L}_{val} \).

**Key takeaways**

- Under/overfitting emerges as a function of capacity and regularization.
- Visualization of residuals clarifies where model misses the target.

---

## Open Colab: Nonlinear Function Estimator (MLP)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BillJr99/Ursinus-CS357-Fall2025/blob/gh-pages/files/notebooks/NonLinearFunctionEstimatorMultiLayerNN.ipynb)

---

## Notebook Overview: MNIST NN from Scratch

**What the code does**

- Implements a 2-layer NN *without* deep-learning libraries (NumPy only).  
- Builds forward and manual backprop; verifies gradients with finite differences.  
- Trains on MNIST; reports accuracy and confusion matrix.

**Math performed**

- Cross-entropy with softmax:
  \[
  p=\mathrm{softmax}(z),\quad \mathcal{L} = -\sum_{c} y_c\log p_c
  \]
- Gradient for logits \(z\): \(\frac{\partial \mathcal{L}}{\partial z}=p-y\).  
- Backprop through layers as in vectorized derivation.

**Key takeaways**

- Ground-up implementation cements understanding of gradient flow.  
- Numerical gradient checks are powerful debugging tools.

---

## Open Colab: MNIST NN from Scratch

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BillJr99/Ursinus-CS357-Fall2025/blob/gh-pages/files/notebooks/Simple_MNIST_NN_from_scratch.ipynb)

---

## Notebook Overview: Credit Score Feature Weight Estimator

**What the code does**

- Trains a logistic/linear model to estimate feature weights for credit scoring.  
- Evaluates performance and fairness across subgroups (e.g., parity metrics).  
- Visualizes coefficients and calibration/reliability.

**Math performed**

- Logistic regression: \( p(y=1\mid x)=\sigma(w^\top x + b) \), BCE loss.  
- Calibration: compares predicted \(p\) to empirical frequency; ECE bins probabilities.  
- Fairness metrics: disparate impact \(=\frac{\Pr[\hat{y}=1\,|\,A=1]}{\Pr[\hat{y}=1\,|\,A=0]}\), etc.

**Key takeaways**

- Feature weights offer interpretability; beware confounding and leakage.  
- Fairness evaluation is multi-metric; no single score suffices.

---

## Open Colab: Credit Score Feature Weight Estimator

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BillJr99/Ursinus-CS357-Fall2025/blob/gh-pages/files/notebooks/CreditScoreFeatureWeightEstimator.ipynb)

---

## Practical Convergence Considerations

- **Initialization**: He/Glorot to preserve variance layer-to-layer.  
- **Normalization**: BatchNorm/LayerNorm stabilize gradients.  
- **Scheduler**: Warmup + cosine or step decay often help.  
- **Regularization**: Weight decay & dropout prevent overfit.  
- **Diagnostics**: Track gradient norms; watch for exploding/vanishing.  
- **Reproducibility**: Set seeds; log hyperparameters & versions.

---

## Studio: Guided Exercises

1. **Fit & Diagnose** (Linear vs. Nonlinear): Train both linear and 2-layer MLPs on the same dataset; compare bias/variance.  
2. **Regularize**: Add dropout and weight decay; plot validation curves across hyperparameters.  
3. **Fairness Lens**: Using the credit dataset, compute metrics by subgroup; discuss tradeoffs among fairness criteria.  
4. **Interpret**: Apply gradient-based saliency or SHAP to your MNIST model; report insights and limitations.

**Deliverable**: A short report (2–3 pages) with methods, results, and ethical analysis.

---

## References & Further Reading

- Goodfellow, Bengio, Courville. *Deep Learning*. MIT Press.  
- Bishop. *Pattern Recognition and Machine Learning*.  
- Cybenko (1989), Hornik (1991): Universal approximation.  
- Zhang et al. (2017): Understanding Deep Learning Requires Re-thinking generalization.  
- Dosovitskiy et al. (2021): An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale