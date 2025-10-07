<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-transformers.md or locally if deployed via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-transformers.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# Foundations of AI: Transformers & Attention

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals**

- Motivate sequence modeling: limitations of n-grams and RNN/LSTM architectures.
- Derive **scaled dot-product attention** and its gradients with respect to $Q,K,V$.
- Work a **step-by-step numerical example** of attention on a short sequence.
- Explain **multi-head attention**, **positional encoding**, **layer normalization**, residual connections, and **feed-forward networks**.
- Implement a minimal **Transformer block** and a tiny **causal language model** in Python.
- Analyze computational complexity and memory of attention; contrast with recurrence and convolution.
- Discuss broader impacts: scaling laws, compute and energy, data ethics, bias/fairness, copyright, safety.

---

## Sequence Modeling: The Problem


Natural language and many real-world datasets are **sequential**:


- Sentences are ordered words.
- Time-series data evolve over time.
- Music, speech, and DNA are sequential.

---

## Traditional Approaches

- **n-gram models** scale poorly with context length; sparsity and combinatorics dominate.
- **Recurrent neural networks (RNNs/LSTMs/GRUs)** process tokens sequentially:
  $$
  h_t = f(W_{xh} x_t + W_{hh} h_{t-1} + b_h), \quad \hat{y}_t = g(W_{hy} h_t + b_y).
  $$
  Backpropagation through time (BPTT) multiplies many Jacobians:
  $$
  \frac{\partial \mathcal{L}}{\partial h_t} = \sum_{k\ge t} \left( \prod_{i=t+1}^{k} \frac{\partial h_i}{\partial h_{i-1}} \right) \frac{\partial \mathcal{L}}{\partial h_k},
  $$
  leading to **vanishing/exploding gradients** for long-range dependencies.

- **Attention** replaces recurrence with *content-based addressing*—each token can directly “look at” any other token in the sequence in parallel.

---


## The Transformer Breakthrough


*Attention Is All You Need* (Vaswani et al., 2017):
  
- Remove recurrence entirely.
- Use **attention** for all-to-all dependency capture.
- Fully parallelizable over sequence length.
- Scales with data and compute.


<a title="dvgodoy, CC BY 4.0 &lt;https://creativecommons.org/licenses/by/4.0&gt;, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:Transformer,_full_architecture.png"><img width="512" alt="Illustrations for the Transformer, and attention mechanism. Transformer, full architecture." src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Transformer%2C_full_architecture.png/512px-Transformer%2C_full_architecture.png?20240806034211"></a>

---

## Open Colab: Attention Computation

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BillJr99/Ursinus-CS357/blob/gh-pages/files/notebooks/Attention.ipynb)

---

## Scaled Dot-Product Attention (Forward)

Given a length-$n$ sequence and model dimension $d_{\text{model}}$:

- Query matrix $Q \in \mathbb{R}^{n \times d_k}$  
- Key matrix $K \in \mathbb{R}^{n \times d_k}$  
- Value matrix $V \in \mathbb{R}^{n \times d_v}$

The attention output is
$$
\mathrm{Attn}(Q,K,V) \;=\; A V \quad \text{with} \quad A = \mathrm{softmax}\!\left(\tfrac{1}{\sqrt{d_k}}\, Q K^\top \right).
$$

- The softmax is applied **row-wise** to $Z = \tfrac{1}{\sqrt{d_k}} QK^\top \in \mathbb{R}^{n\times n}$.  
- $A_{ij}$ is the weight that token $i$ assigns to token $j$.  
- The scale $1/\sqrt{d_k}$ stabilizes gradients for large $d_k$.

**Complexity**: computing $QK^\top$ costs $O(n^2 d_k)$; applying $A$ to $V$ costs $O(n^2 d_v)$ → overall **quadratic in sequence length**.

---

## Derivatives for Attention (Backward)

Let $O = \mathrm{Attn}(Q,K,V) = A V$ and suppose we have upstream gradient $G_O = \partial \mathcal{L}/\partial O \in \mathbb{R}^{n \times d_v}$. We derive $G_V, G_A, G_Z, G_Q, G_K$.

1. **Through the value multiply** $O = A V$:
$$
G_V \;=\; A^\top G_O, \qquad G_A \;=\; G_O V^\top.
$$

2. **Through the softmax** $A = \mathrm{softmax}(Z)$ (row-wise). For each row $i$,
$$
\frac{\partial \mathcal{L}}{\partial z_i} \;=\; J(a_i)^\top \frac{\partial \mathcal{L}}{\partial a_i}, \quad
J(a_i) \equiv \frac{\partial a_i}{\partial z_i} = \mathrm{diag}(a_i) - a_i a_i^\top.
$$
Stacking all rows gives
$$
G_Z \;=\; \mathrm{SoftmaxBackward}(A, G_A) \in \mathbb{R}^{n\times n},
$$
where $\left[G_Z\right]_{i:} = J(a_i)^\top \left[G_A\right]_{i:}$.

3. **Through the scaled dot-product** $Z = \tfrac{1}{\sqrt{d_k}}\, QK^\top$:
$$
G_Q \;=\; \frac{1}{\sqrt{d_k}}\, G_Z K, \qquad
G_K \;=\; \frac{1}{\sqrt{d_k}}\, G_Z^\top Q.
$$

These equations are the basis for efficient fused kernels in modern libraries.

---

## Python: Numpy Reference Implementation (Forward/Backward)

```python
import numpy as np

def softmax_rows(Z):
    Zmax = Z.max(axis=1, keepdims=True)
    expZ = np.exp(Z - Zmax)
    return expZ / expZ.sum(axis=1, keepdims=True)

def softmax_backward(A, dA):
    n = A.shape[0]
    dZ = np.empty_like(A)
    for i in range(n):
        ai = A[i:i+1, :]
        dai = dA[i:i+1, :]
        a_dot_v = (ai @ dai.T)
        dZ[i:i+1, :] = ai * (dai - a_dot_v)
    return dZ

def attention_forward(Q, K, V):
    dk = Q.shape[1]
    Z = (Q @ K.T) / np.sqrt(dk)
    A = softmax_rows(Z)
    O = A @ V
    cache = (Q, K, V, A, Z, dk)
    return O, cache

def attention_backward(dO, cache):
    Q, K, V, A, Z, dk = cache
    dV = A.T @ dO
    dA = dO @ V.T
    dZ = softmax_backward(A, dA)
    dQ = (dZ @ K) / np.sqrt(dk)
    dK = (dZ.T @ Q) / np.sqrt(dk)
    return dQ, dK, dV
```

---

## Worked Example: 3-Token Sequence


Suppose $n=3$, $d=2$, $d_k=d_v=2$. Let


$$
X = \begin{bmatrix}1 & 0 \\ 0 & 1 \\ 1 & 1\end{bmatrix}, \quad W^Q=W^K=W^V=I.
$$


So:
$$ Q=K=V=X. $$


### Step 1: Compute scores
$$ Z = QK^T = \begin{bmatrix}
1 & 0 \\
0 & 1 \\
1 & 1
\end{bmatrix} \begin{bmatrix}
1 & 0 & 1 \\
0 & 1 & 1
\end{bmatrix}
= \begin{bmatrix}
1 & 0 & 1 \\
0 & 1 & 1 \\
1 & 1 & 2
\end{bmatrix} $$


### Step 2: Scale by $\sqrt{d_k}=\sqrt{2}$
$$ Z' = Z/\sqrt{2} $$


### Step 3: Apply softmax row-wise
Take row 1: $[1,0,1]/\sqrt{2} = [0.707, 0, 0.707]$.
Exponentiate and normalize:
$$ e^{0.707}=2.028, \ e^0=1.0. $$
So row 1 weights = $[2.028, 1.0, 2.028]/(2.028+1+2.028) \approx [0.40, 0.20, 0.40]$.


Do the same for rows 2 and 3.


### Step 4: Multiply by $V$
Compute $O = AV$, where $V=X$. Each output token is a weighted mixture of the value vectors.

---

## Three-Token Example in Python


```python
import torch, math


X = torch.tensor([[1.0,0.0], [0.0,1.0], [1.0,1.0]])
Q = K = V = X


d_k = Q.size(-1)
Z = Q @ K.T / math.sqrt(d_k)
A = torch.softmax(Z, dim=-1)
O = A @ V


print("Scores Z:\n", Z)
print("Attention Weights A:\n", A)
print("Output O:\n", O)
```


Check that $O$ indeed produces mixtures of input vectors.

---

## Positional Encoding (Sinusoidal)

Without recurrence, the model needs a notion of order. **Sinusoidal encodings** inject position information additively:

$$
\begin{aligned}
\mathrm{PE}(pos, 2i) &= \sin\!\left( \frac{pos}{10000^{2i/d_{\text{model}}}} \right),\\\\
\mathrm{PE}(pos, 2i+1) &= \cos\!\left( \frac{pos}{10000^{2i/d_{\text{model}}}} \right).
\end{aligned}
$$

```python
import numpy as np

def sinusoidal_positional_encoding(n, d_model):
    pos = np.arange(n)[:, None]
    i = np.arange(d_model)[None, :]
    angle_rates = 1.0 / (10000 ** ((2*(i//2)) / d_model))
    angles = pos * angle_rates
    pe = np.zeros((n, d_model), dtype=np.float32)
    pe[:, 0::2] = np.sin(angles[:, 0::2])
    pe[:, 1::2] = np.cos(angles[:, 1::2])
    return pe

for i in range(n):
ai = A[i:i+1, :] # (1, n)
dai = G_A[i:i+1, :] # (1, n)
a_dot_v = (ai @ dai.T) # (1, 1)
G_Z[i:i+1, :] = ai * (dai - a_dot_v)
G_Q = G_Z @ K / np.sqrt(d_k)
G_K = G_Z.T @ Q / np.sqrt(d_k)


print("
[Backward for L=sum(O)]")
print("dL/dV=
", G_V)
print("dL/dQ=
", G_Q)
print("dL/dK=
", G_K)
```


**Tips:**
- Keep matrices tiny (e.g., n<=5, d_k,d_v<=4).
- Try symmetric vs. asymmetric Q and K to see how A changes.
- Toggle `use_causal_mask=True` to watch weights above the diagonal disappear.


---


## Interactive Exercise: Softmax–Jacobian Sandbox


Explore how the softmax Jacobian transforms upstream gradients.


```python
import numpy as np


# EDIT: logits and upstream gradient (per row)
logits = np.array([2.0, 1.0, -0.5, 0.0], dtype=np.float64)
dA = np.array([0.5, -0.3, 0.2, 0.1], dtype=np.float64)


# softmax
lmax = logits.max()
expz = np.exp(logits - lmax)
a = expz / expz.sum()


# Jacobian-vector product: J(a)^T @ dA = (diag(a) - a a^T) @ dA
Jv = a * (dA - a @ dA)


# Full Jacobian (for inspection)
J = np.diag(a) - np.outer(a, a)


print("softmax(a)=", a)
print("Row-sum check:", a.sum())
print("
Jv = (diag(a) - a a^T) dA =
", Jv)
print("
Full Jacobian J = diag(a) - a a^T =
", J)
print("Symmetry check (J^T == J):", np.allclose(J.T, J))
print("Positive semi-definite? eigenvalues >= 0 ->", np.linalg.eigvalsh(J))
```


Try making one logit much larger than the others; observe that J becomes nearly singular and the gradient concentrates on the max entry (why does this make training brittle without the 1/sqrt(d_k) scaling?).

---

## Multi-Head Self-Attention (MHA)

**Idea:** project inputs into $h$ subspaces (heads), perform attention in each, then concatenate and project back:

$$
\mathrm{MHA}(X) = \mathrm{Concat}(\mathrm{head}_1,\ldots,\mathrm{head}_h)W^O
$$

Multiple attention heads capture different relational patterns:


$$ \text{MHA}(X) = \text{Concat}(\text{head}_1, ..., \text{head}_h) W^O $$


$$ \text{head}_j = \text{Attention}(XW_j^Q, XW_j^K, XW_j^V) $$


Each head has its own projection matrices $W_j^Q,W_j^K,W_j^V$.

```python
import torch
import torch.nn as nn
import math

class MultiHeadSelfAttention(nn.Module):
    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_head = d_model // num_heads
        self.Wq = nn.Linear(d_model, d_model, bias=False)
        self.Wk = nn.Linear(d_model, d_model, bias=False)
        self.Wv = nn.Linear(d_model, d_model, bias=False)
        self.Wo = nn.Linear(d_model, d_model, bias=False)

    def forward(self, X, mask: torch.Tensor | None = None):
        B, T, C = X.shape
        q = self.Wq(X).view(B, T, self.num_heads, self.d_head).transpose(1, 2)
        k = self.Wk(X).view(B, T, self.num_heads, self.d_head).transpose(1, 2)
        v = self.Wv(X).view(B, T, self.num_heads, self.d_head).transpose(1, 2)

        attn_scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)
        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float('-inf'))
        A = torch.softmax(attn_scores, dim=-1)
        out = A @ v
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.Wo(out)
```

---

## Transformer Block

A block combines:
- Multi-head self-attention (MHA)
- Residual + LayerNorm
- Feedforward network
- Residual + LayerNorm


```python
class TransformerBlock(nn.Module):
def __init__(self, d_model, num_heads, d_ff):
super().__init__()
self.attn = MultiHeadSelfAttention(d_model, num_heads)
self.ffn = nn.Sequential(
nn.Linear(d_model, d_ff),
nn.ReLU(),
nn.Linear(d_ff, d_model)
)
self.norm1 = nn.LayerNorm(d_model)
self.norm2 = nn.LayerNorm(d_model)


def forward(self, x):
attn_out = self.attn(x, x, x)
x = self.norm1(x + attn_out)
ff_out = self.ffn(x)
x = self.norm2(x + ff_out)
return x
```

---

## Tiny GPT-style Model (Toy)

A toy model using these components:

- Character-level tokenizer.
- Embeddings + positional encodings.
- Several Transformer blocks.
- Linear projection to vocab logits.
- Trained with next-token prediction:
$$ \mathcal{L}(\theta) = -\sum_{t=1}^T \log p_\theta(x_t \mid x_{<t}). $$
- Includes tokenizer, causal mask, and generation.

```python
class TinyTokenizer:
    def __init__(self, text: str):
        chars = sorted(set(text))
        self.stoi = {ch: i for i, ch in enumerate(chars)}
        self.itos = {i: ch for ch, i in self.stoi.items()}

    def encode(self, s: str):
        return [self.stoi[ch] for ch in s]

    def decode(self, ids):
        return "".join(self.itos[i] for i in ids)
```

```python
def causal_mask(T: int, device="cpu"):
    return torch.tril(torch.ones(T, T, device=device)).unsqueeze(0).unsqueeze(0)
```

```python
class TinyGPT(nn.Module):
    def __init__(self, vocab_size: int, d_model=128, num_heads=4, d_ff=256, n_layers=2, block_size=64):
        super().__init__()
        self.block_size = block_size
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(block_size, d_model)
        self.blocks = nn.ModuleList([TransformerBlock(d_model, num_heads, d_ff) for _ in range(n_layers)])
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        pos = torch.arange(0, T, device=idx.device).unsqueeze(0)
        x = self.tok_emb(idx) + self.pos_emb(pos)
        mask = causal_mask(T, device=idx.device)
        for block in self.blocks:
            x = block(x, mask)
        x = self.ln_f(x)
        logits = self.head(x)
        loss = None
        if targets is not None:
            loss = nn.functional.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss
```

---

## A Worked Example
- Understand next-token prediction as probabilistic inference.
- Connect embeddings, attention, and feed-forward networks to the final hidden state **h**.
- See how **h** is projected into vocabulary space to yield logits and probabilities.
- Work through concrete, step-by-step numerical examples.

> Source of raw material for these slides: adapted from course notes/transcript 【8†source】.

---

### 1. The Big Picture: Next-Token Prediction
- LLMs model a conditional distribution over tokens:
  
  $$ P(w_t \mid w_1,\dots,w_{t-1}) $$
  
- Pipeline (at a high-level):
  1. Tokenize $w_1,\dots,w_{t-1}$
  2. Embed tokens + add positional information
  3. Pass through stacked Transformer layers (self-attention + FFN)
  4. Extract final hidden state $h$ for position $t$
  5. Project $h$ onto vocabulary → logits → softmax → probabilities

---

### 2. Embeddings & Contextualization
- Each token $w_i$ maps to an embedding $x_i = E[w_i]$.
- Positional signal $p_i$ is added: $z_i = x_i + p_i$.
- Through layers, each $z_i$ becomes **contextualized**, ultimately yielding a final vector $h$ at the prediction position.

---

### 3. Scoring Candidates: Linear Projection + Softmax
- Each vocabulary token $j$ has an output embedding $v_j$.
- Score (logit) for token $j$:
  
  $$ \ell_j = h^\top v_j + b_j \quad (\text{often } b_j=0) $$
  
- Convert to probabilities with softmax:
  
  $$ P(j \mid \text{context}) = \frac{e^{\ell_j}}{\sum_k e^{\ell_k}} $$

- Dot-product is the standard score; cosine similarity is a normalized variant and gives similar rankings when norms are comparable.

---

### 4. Toy Example A: Dot-Product Softmax (Vocabulary of 3)
**Context:** “The cat chased the” → final hidden state (toy 3D):
  
$ h = [0.9,\; 0.1,\; 0.2] $

**Output embeddings:**
- $ v_{\text{dog}} = [0.8, 0.1, 0.3] $
- $ v_{\text{car}} = [0.1, 0.9, 0.1] $
- $ v_{\text{banana}} = [0.0, 0.2, 0.9] $

**Logits (dot products):**
- $ \ell_{\text{dog}} = 0.79 $
- $ \ell_{\text{car}} = 0.20 $
- $ \ell_{\text{banana}} = 0.20 $

**Softmax (shift by max = 0.79):**
- $ P(\text{dog}) \approx 0.474 $
- $ P(\text{car}) \approx 0.263 $
- $ P(\text{banana}) \approx 0.263 $

**Takeaway:** “dog” is most probable continuation given the context.

---

### 5. Toy Example B: Cosine Similarity View
- Cosine similarity:
  
  $$ \cos(h, v) = \frac{h^\top v}{\|h\|\,\|v\|} $$
  
- With the same vectors as in Example A, cosines rank **dog** highest.
- In practice, logit = dot-product; with L2-normalized rows and $h$, this becomes cosine-scoring.

---

### 6. How the Model Computes $h$: Self-Attention
**Per layer, per token $i$:**
- Queries/Keys/Values:
  
  $ Q_i = W_Q z_i,\;\; K_i = W_K z_i,\;\; V_i = W_V z_i $

- Attention weights for token $i$ attending to token $j$:
  
  $$ \alpha_{ij} = \text{softmax}_j \!\left(\frac{Q_i \cdot K_j}{\sqrt{d_k}}\right) $$

- Context update:
  
  $$ \tilde{z}_i = \sum_j \alpha_{ij} V_j $$

- Then residual + layer norm; then an FFN (e.g., GELU MLP); repeat across many layers.
- At the last layer, take the representation at position $t$ as $h$.

---

### 7. Numerical Attention Walkthrough (Toy 2D)
**Embeddings (2D):**
- $ \text{The}_1 : [0.1, 0.2] $
- $ \text{cat} : [0.9, 0.1] $
- $ \text{chased} : [0.8, 0.7] $
- $ \text{the}_2 : [0.2, 0.1] $

Assume $Q=K=V=I$ (identity) to keep numbers simple.
Compute attention for **the\_2** over all tokens (including itself):

- Raw scores (scaled dot products, $d_k=2$):
  - to **The\_1**: ≈ 0.028
  - to **cat**: ≈ 0.135
  - to **chased**: ≈ 0.163
  - to **the\_2** (self): ≈ 0.035

- Softmax weights:
  - **The\_1**: ≈ 0.23
  - **cat**: ≈ 0.26
  - **chased**: ≈ 0.27
  - **the\_2**: ≈ 0.24

- Weighted sum (context vector for **the\_2**):
  $ \tilde{z}_{\text{the}_2} \approx [0.521,\; 0.285] $

**Interpretation:** attention emphasized **cat** and **chased**, pulling in animal/action context.

---

### 8. From $\tilde{z}$ to $h$: FFN & Residuals
- Residual connection + LayerNorm:
  
  $ z' = \text{LayerNorm}(z + \tilde{z}) $
- Feed-Forward Network (per token):
  
  $ \text{FFN}(z') = W_2\,\sigma(W_1 z' + b_1) + b_2 $
- After multiple layers, the final vector at the prediction position becomes $h$.

**Intuition:** attention mixes relevant tokens; FFN builds higher-order features; residual/normalization stabilize and preserve signal.

---

### 9. Step 4 in Detail: Projecting $h$ to Vocabulary
- Let $V \in \mathbb{R}^{d \times |\mathcal{V}|}$ be the (possibly weight-tied) output matrix whose columns are $v_j$.
- The model computes a vector of logits:
  
  $$ \ell = V^\top h \quad (\text{plus optional bias } b) $$

- Softmax converts $\ell$ to a probability distribution over the vocabulary.
- **Why this works:** tokens whose embeddings align with $h$ (large dot product) receive high probability.

---

### 10. End-to-End Mini Example (2D)
Assume after FFN/LayerNorm, the final hidden state is $ h \approx [0.6, 0.3] $.  
Use tiny vocab embeddings:

- $ v_{\text{dog}} = [0.8, 0.3] \Rightarrow \ell_{\text{dog}} = 0.57 $
- $ v_{\text{car}} = [0.1, 0.9] \Rightarrow \ell_{\text{car}} = 0.33 $
- $ v_{\text{banana}} = [0.0, 0.8] \Rightarrow \ell_{\text{banana}} = 0.24 $

Softmax (shift by max $=0.57$):
- $ P(\text{dog}) \approx 0.40 $
- $ P(\text{car}) \approx 0.31 $
- $ P(\text{banana}) \approx 0.29 $

**Result:** model most likely continues with **dog**.

---

### 11. Decoding & Temperature
- **Greedy (argmax):** pick $\arg\max_j P(j)$.
- **Sampling:** draw from the distribution to encourage diversity.
- **Top-$k$:** sample only from the $k$ highest-probability tokens.
- **Top-$p$ (nucleus):** sample from the smallest set whose cumulative mass ≥ $p$.
- **Temperature $\tau$:** scale logits by $1/\tau$ before softmax.
  - $\tau < 1$: sharper distribution (more deterministic).
  - $\tau > 1$: flatter distribution (more diverse).

---

### 12. Practical Notes & Perspectives
- **Weight tying:** input and output embeddings are often shared → parameter efficiency and improved consistency.
- **Multi-head attention:** different heads specialize (syntax, semantics, dependencies).
- **Normalization choices:** LayerNorm variants and placement (pre/post) affect training stability.
- **Calibration:** output biases and temperature control can calibrate probabilities in deployment.
- **Limitations:** vocabulary granularity (subwords), exposure bias under teacher forcing, long-context challenges.

---

### 13. Quick Exercises (Optional)
1. Recompute Example A with a new hidden state $h' = [0.7, 0.2, 0.1]$. How do the probabilities change?
2. In the 2D attention example, change $Q=K=V$ from identity to a nontrivial matrix and verify how the weights shift.
3. Experiment with $\tau = 0.7$ vs. $\tau = 2.0$ on Example A logits and compare $P(\text{dog})$.

---

## Societal & Ethical Implications


- **Bias amplification**: models reflect training data biases.
- **Misinformation**: plausible but false text generation.
- **Environmental costs**: training consumes vast energy.
- **Intellectual property**: models may memorize copyrighted data.
- **Access and equity**: who controls large-scale AI?


**Discussion:**
- Should training datasets be open or regulated?
- How to ensure transparency and fairness?
- What is the role of AI in education, research, and governance?

---

## Key Takeaways


- Attention enables direct modeling of dependencies without recurrence.
- We derived forward and backward passes for scaled dot-product attention.
- Worked through a **3-token numerical example** in math and Python.
- Built up to multi-head attention and a Transformer block.
- Discussed how scaling leads to LLMs, and the societal implications.

---

## Summary

- Attention = parallel, long-range context.
- Derivations: forward & backward.
- Built blocks: MHA, TransformerBlock, toy GPT.
- Impacts: fairness, safety, sustainability.
