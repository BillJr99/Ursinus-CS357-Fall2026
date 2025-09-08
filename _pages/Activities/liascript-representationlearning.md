<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-representationlearning.md or locally if deployed via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-representationlearning.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Foundations of AI: Representation Learning

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**By the end of this lecture you will be able to:**

- Motivate representation learning and define desiderata (invariance, sufficiency, disentanglement, robustness).
- Derive **PCA** from first principles (variance maximization and reconstruction error) and connect it to the **SVD**; implement PCA and whitening **from scratch**.
- Build and train **autoencoders** (linear ↔ PCA, sparse, denoising) and compute their gradients.
- Explain and implement a toy **contrastive learning** objective (InfoNCE), including gradients for cosine similarity and temperature scaling.
- Understand **probabilistic PCA** and the **VAE** objective (ELBO, reparameterization trick) at a conceptual and mathematical level.
- Analyze the geometry of learned embeddings (isotropy, normalization) and reflect on ethical & societal implications (bias, privacy, spurious correlations).

---

## 0. Motivation: Why Representations?

A **representation** $z = f_\theta(x)$ maps raw input $x$ to features $z$ that make downstream tasks (classification, retrieval, control) easier.

**Desiderata:**
- **Invariant** to nuisance factors (e.g., translation, pitch, lighting).
- **Sufficient** for the task (retain signal, discard noise).
- **Compact** and **structured** (promote generalization, compositionality).
- **Stable** under small perturbations (robustness).

> We will start with linear methods (PCA), then add neural parameterizations (autoencoders), then move to self/contrastive supervision.

---

## 1. Linear Foundations: PCA

### 1.1 Set‑up

Let $X \in \mathbb{R}^{n\times d}$ be **row‑centered** (subtract the column means). The empirical covariance is
$$
\Sigma = \frac{1}{n} X^\top X \in \mathbb{R}^{d\times d}.
$$
We seek a $k$‑dimensional representation $Z = X W$, where $W \in \mathbb{R}^{d\times k}$ has orthonormal columns ($W^\top W = I_k$).

### 1.2 PCA as **variance maximization**

Maximize projected variance:
$$
\max_{W^\top W = I_k} \; \mathrm{tr}(W^\top \Sigma W).
$$
**Derivation (sketch).** Using Lagrange multipliers with $\Lambda$ for the orthonormality constraint,
$$
\mathcal{L}(W,\Lambda) = \mathrm{tr}(W^\top \Sigma W) - \mathrm{tr}\big(\Lambda (W^\top W - I)\big).
$$
Setting $\partial \mathcal{L}/\partial W = 0$ yields $\Sigma W = W \Lambda$. Thus the columns of $W$ are **eigenvectors** of $\Sigma$, and we choose the top $k$ by eigenvalues.

### 1.3 PCA as **reconstruction error minimization**

Find the best rank‑$k$ linear autoencoder (orthogonal projector $P = W W^\top$):
$$
\min_{W^\top W = I_k}\; \lVert X - X W W^\top \rVert_F^2.
$$
This is solved by the same top‑$k$ eigenvectors. Objective equivalence follows from $\lVert X \rVert_F^2 - \mathrm{tr}(W^\top \Sigma W)$.

### 1.4 Connection to the **SVD**

$X = U\, S\, V^\top$ with singular values $s_1 \ge \cdots \ge s_{\min(n,d)}$. Then $\Sigma = V \,(S^2/n)\, V^\top$. Top PCA directions are the first $k$ columns of $V$, and the explained variance ratios are $s_i^2 / \sum_j s_j^2$.

### 1.5 PCA & Whitening — **from scratch (NumPy)**

```python
import numpy as np

def pca_fit(X, k):
    Xc = X - X.mean(axis=0, keepdims=True)              # center
    C = (Xc.T @ Xc) / Xc.shape[0]                       # covariance
    eigvals, eigvecs = np.linalg.eigh(C)                # symmetric → eigh
    idx = np.argsort(eigvals)[::-1]
    eigvals, eigvecs = eigvals[idx], eigvecs[:, idx]
    W = eigvecs[:, :k]                                  # principal directions
    Z = Xc @ W                                          # principal components
    return Z, W, eigvals[:k], Xc

def pca_whiten(Z, eigvals, eps=1e-5):
    return Z / np.sqrt(eigvals + eps)

# Example usage (toy):
X = np.random.randn(200, 5) @ np.array([[2,0,0,0,0], [0,1.5,0,0,0], [0,0,1,0,0], [0,0,0,0.2,0], [0,0,0,0,0.1]])
Z, W, evals, Xc = pca_fit(X, k=2)
Z_white = pca_whiten(Z, evals)
X_recon = (Z @ W.T) + X.mean(axis=0, keepdims=True)
```

**Checkpoint.** Verify that $W^\top W = I$ (up to numerical error). Compare reconstruction error as $k$ varies. Plot explained variance.

---

## 2. Autoencoders (AEs)

### 2.1 Linear AE ≈ PCA

One‑hidden‑layer **linear** AE with MSE and tied weights ($W_2 = W_1^\top$):
$$
\hat{x} = W^\top (W x + b_1) + b_2, \quad \mathcal{L}(x) = \lVert x - \hat{x} \rVert_2^2.
$$
With centered data and proper constraints, solutions align with PCA subspaces.

### 2.2 Nonlinear AE and gradients

Let $h = \phi(W_1 x + b_1)$, $\hat{x} = W_2 h + b_2$, loss $\mathcal{L} = \lVert x - \hat{x} \rVert^2$.
Backprop:
$$
\frac{\partial \mathcal{L}}{\partial W_2} = 2 (\hat{x} - x) h^\top,\quad
\frac{\partial \mathcal{L}}{\partial b_2} = 2 (\hat{x} - x),
$$
$$
\delta_h = W_2^\top (\hat{x} - x) \odot \phi'(W_1 x + b_1),\quad
\frac{\partial \mathcal{L}}{\partial W_1} = \delta_h x^\top,\quad
\frac{\partial \mathcal{L}}{\partial b_1} = \delta_h.
$$

### 2.3 Variants

- **Undercomplete**: $\dim(h) < \dim(x)$, forces compression.
- **Sparse AE**: penalty on activations; e.g., KL sparsity with target $\rho$ and average activation $\hat{\rho}_j$:
  $$
  \Omega_\text{sparse} = \beta \sum_j \big[\rho \log\tfrac{\rho}{\hat{\rho}_j} + (1-\rho)\log\tfrac{1-\rho}{1-\hat{\rho}_j}\big].
  $$
- **Denoising AE**: corrupt input $\tilde{x} = x + \epsilon$ (or masking); train to reconstruct $x$ from $\tilde{x}$.

### 2.4 Minimal PyTorch AE (pedagogical)

```python
import torch, torch.nn as nn

class AE(nn.Module):
    def __init__(self, d_in=784, d_h=64):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(d_in, d_h), nn.ReLU())
        self.dec = nn.Sequential(nn.Linear(d_h, d_in))
    def forward(self, x):
        h = self.enc(x)
        xhat = self.dec(h)
        return xhat, h

# toy training loop (X: [N, d])
model = AE(100, 16)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
for step in range(500):
    x = torch.randn(64, 100)
    xhat, _ = model(x)
    loss = ((xhat - x)**2).mean()
    opt.zero_grad(); loss.backward(); opt.step()
```

**Checkpoint.** Add Gaussian noise to inputs and observe denoising. Try $L_1$ penalty on $h$ to encourage sparsity.

---

## 3. Geometry of Embeddings

- **Centering & $\ell_2$‑normalization**: $z \leftarrow (z - \mu)/\lVert z - \mu \rVert$; improves cosine similarity stability.
- **Isotropy**: Encodings should not collapse to a subspace; whitening or decorrelation losses can help.
- **BatchNorm/LayerNorm**: normalize across batch or features to stabilize optimization; affects representation scale and distribution.

---

## 4. Contrastive Learning (InfoNCE)

### 4.1 Setup

Create two augmentations $x_i^{(1)}, x_i^{(2)}$ of the same sample $x_i$. Encode $z_i^{(1)} = g(f(x_i^{(1)}))$, $z_i^{(2)} = g(f(x_i^{(2)}))$ and **pull** positives together while **pushing** other samples (negatives) apart.

Define cosine similarity $s(u,v) = \frac{u^\top v}{\lVert u \rVert\, \lVert v \rVert}$ and temperature $\tau>0$.

### 4.2 InfoNCE loss

For an anchor $i$ and its positive $j$:
$$
\mathcal{L}_i = - \log \frac{\exp\big(s(z_i, z_j)/\tau\big)}{\sum_{k=1}^N \exp\big(s(z_i, z_k)/\tau\big)}.
$$

**Gradient wrt $z_i$ (sketch).** Let $p_k = \mathrm{softmax}(s(z_i, z_k)/\tau)$ over $k$. Using $\partial s(u,v)/\partial u = \frac{v}{\lVert u \rVert\lVert v \rVert} - \frac{u\,(u^\top v)}{\lVert u \rVert^3\lVert v \rVert}$,
$$
\frac{\partial \mathcal{L}_i}{\partial z_i} = \sum_k p_k \, \frac{\partial s(z_i, z_k)}{\partial z_i} - \frac{\partial s(z_i, z_j)}{\partial z_i}.
$$
Smaller $\tau$ → sharper distribution.

### 4.3 Toy PyTorch skeleton

```python
import torch, torch.nn as nn, torch.nn.functional as F

def cosine_sim(a, b, eps=1e-8):
    a = F.normalize(a, dim=-1)
    b = F.normalize(b, dim=-1)
    return a @ b.T

class MLPProj(nn.Module):
    def __init__(self, d_in=100, d_h=128, d_out=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, d_h), nn.ReLU(), nn.Linear(d_h, d_out))
    def forward(self, x):
        return self.net(x)

# toy batch of positive pairs
x1 = torch.randn(256, 100)
x2 = x1 + 0.05*torch.randn_like(x1)    # simple augmentation
enc = MLPProj(100, 128, 64)
z1 = enc(x1); z2 = enc(x2)

# InfoNCE
sim = cosine_sim(z1, z2)               # (B,B)
T = 0.1
labels = torch.arange(sim.size(0))
logits = sim / T
loss = F.cross_entropy(logits, labels)
loss.backward()
```

**Checkpoint.** Replace the naive augmentation with two different transformations (e.g., noise & masking). Try different $\tau$ values and observe training stability.

---

## 5. Metric Learning: Triplet Loss (brief)

Given anchor $a$, positive $p$, negative $n$, embedding $f_\theta$ and margin $m>0$:
$$
\mathcal{L}_\text{triplet} = \max\big\{0, \lVert f(a)-f(p) \rVert_2^2 - \lVert f(a)-f(n) \rVert_2^2 + m \big\}.
$$
**Hard mining** accelerates but risks collapse—balance with batch diversity and normalization.

---

## 6. Probabilistic Views

### 6.1 Probabilistic PCA (PPCA)

Generative model: $z \sim \mathcal{N}(0,I_k)$, $x \mid z \sim \mathcal{N}(W z + \mu, \sigma^2 I)$. The marginal is $x \sim \mathcal{N}(\mu, WW^\top + \sigma^2 I)$. MLE recovers PCA subspace (up to rotation); EM or closed‑form solutions exist.

### 6.2 Variational Autoencoder (VAE) — the ELBO

We introduce encoder $q_\phi(z\mid x)$ and decoder $p_\theta(x\mid z)$. The evidence lower bound (ELBO):
$$
\log p_\theta(x) \ge \underbrace{\mathbb{E}_{q_\phi(z\mid x)}[\log p_\theta(x\mid z)]}_{\text{reconstruction}} - \underbrace{\mathrm{KL}\big(q_\phi(z\mid x)\;\Vert\; p(z)\big)}_{\text{regularization}}.
$$
**Reparameterization:** $z = \mu_\phi(x) + \sigma_\phi(x) \odot \epsilon$, $\epsilon \sim \mathcal{N}(0,I)$, makes gradients low‑variance and backprop‑friendly.

---

## 7. Ethics & Societal Impacts of Learned Representations

- **Bias & Fairness:** Encoders can latch onto spurious correlations, leading to disparate error rates. Evaluate with disaggregated metrics; consider adversarial or counterfactual de‑biasing.
- **Privacy:** Membership inference and inversion attacks may recover training data from embeddings; explore differential privacy and feature noise.
- **Security & Robustness:** Adversarial examples exploit representation geometry; certify or detect with Lipschitz constraints and randomized smoothing.
- **Accountability:** Prefer representations that support **attribution** (e.g., RAG with citations) and interpretability for high‑stakes use.

---

## 8. Practice & Exercises (guided)

1. **PCA from scratch** on a 2D toy dataset: compute eigenvectors, project, and reconstruct. Plot explained variance.  
2. **Linear AE vs. PCA**: train a linear AE with tied weights; verify alignment of subspaces with PCA.  
3. **Denoising AE**: train on noisy inputs; measure PSNR/SSIM improvement.  
4. **Contrastive toy**: train InfoNCE with two augmentations; visualize embedding clusters via PCA/TSNE of $z$.  
5. **Triplet loss** on synthetic classes; examine intra/inter‑class distances.

**Stretch:** Implement **whitening** in the contrastive head and quantify its effect on retrieval recall@k.

---

## 9. Appendix: Finite‑Difference Gradient Checks

To validate backprop, compare analytical gradients $g$ with numerical $g_{\text{num}}$ via
$$
\frac{\lVert g - g_{\text{num}} \rVert}{\max(1, \lVert g \rVert, \lVert g_{\text{num}} \rVert)} < 10^{-6}.
$$

```python
def finite_diff(f, x, eps=1e-5):
    g = np.zeros_like(x)
    for i in range(x.size):
        xp = x.copy(); xm = x.copy()
        xp[i] += eps; xm[i] -= eps
        g[i] = (f(xp) - f(xm)) / (2*eps)
    return g
```

---

## Key Takeaways

- PCA formalizes linear representation learning; autoencoders generalize it with neural parameterizations and priors (sparsity, denoising).
- Contrastive objectives shape geometry through similarity, temperature, and negatives; normalization and whitening matter.
- Probabilistic formulations (PPCA, VAE) clarify reconstruction vs. regularization and enable principled generative modeling.
- Ethical practice requires testing representations for bias, privacy leakage, and robustness before deployment.

