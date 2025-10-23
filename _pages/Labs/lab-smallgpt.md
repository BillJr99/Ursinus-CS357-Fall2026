---
layout: assignment
permalink: Labs/SmallGPT
title: "Lab: Building a Small GPT from Scratch"

info:
  points: 100
  goals:
    - Understand the autoregressive language modeling objective and cross-entropy loss.
    - Implement a minimal GPT incrementally of bigram baseline to causal self-attention to multi-head to Transformer blocks.
    - Train on Tiny Shakespeare and generate samples; reason about scaling laws, context length, and overfitting.
  rubric:
    - weight: 30
      description: Implementation
      preemerging: Provides a working implementation aligned to the assignment specification with simple tests.
      beginning: Implements the core functionality accurately and demonstrates usage on representative inputs.
      progressing: Implements the full specification with clear structure, tests, and discussion of edge cases.
      proficient: Delivers a robust, well-structured implementation with comprehensive tests and justified design choices.
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
      progressing: Maintains consistent style, meaningful names, and explanatory docs where non-trivial.
      proficient: Exhibits clean architecture, thoughtful abstractions, and thorough documentation throughout.
    - weight: 10
      description: Design Report
      preemerging: Summarizes goals, approach, and evaluation setup.
      beginning: Explains design decisions and trade-offs with small-scale results.
      progressing: Details design rationale, experiments, and limitations with supporting figures/tables.
      proficient: Delivers a concise, well-structured report with justified choices and actionable future work.
    - weight: 10
      description: Submission Completeness
      preemerging: Provides required artifacts and basic run instructions.
      beginning: Includes all artifacts with clear run instructions and parameters.
      progressing: Includes scripts, configs, and reproducible steps with sample data.
      proficient: Provides a fully reproducible package with results, seeds, and validation notes.

tags:
  - ai
---

# Lab: Building a Small GPT from Scratch (Step-by-Step Tutorial)

This guided lab walks through the construction of a miniature decoder-only Transformer (a “small GPT”) and derives the key equations along the way. We proceed from a **bigram baseline** to a stack of **Transformer blocks** with causal self-attention, then train on the **Tiny Shakespeare** dataset and generate samples.

---

## References

This lab is heavily derived from Andrej Karpathy's tutorial and materials 

1. **Colab Notebook**: *Building a GPT*, which this lab mirrors in structure and pedagogy: [https://colab.research.google.com/drive/1HVqR-4OIM4m9Y1vH2rHMwpW3kTsMBrHj](https://colab.research.google.com/drive/1HVqR-4OIM4m9Y1vH2rHMwpW3kTsMBrHj)
2. **Zero-to-Hero Syllabus** (Transformers/Attention overview): [https://karpathy.ai/zero-to-hero.html](https://karpathy.ai/zero-to-hero.html)  
3. **Video**: *Let’s build GPT: from scratch, in code, spelled out*: [https://www.youtube.com/watch?v=kCc8FmEb1nY](https://www.youtube.com/watch?v=kCc8FmEb1nY)

---

## Learning Objectives

1. Formalize the **autoregressive language modeling** objective and **cross-entropy** loss.
2. Implement and understand **causal masking** for next-token prediction.
3. Build **self-attention** (Q, K, V, Softmax) with the **scale** factor $1/\sqrt{d_k}$.
4. Compose multi-head attention, feedforward MLP, residual connections, and LayerNorm into a **Transformer block**.
5. Train a small GPT on Tiny Shakespeare and analyze samples, losses, and overfitting behavior.

---

## What You Submit

- `small_gpt.py` (or a single notebook) containing the **complete, runnable program** composed of the code chunks below.
- A short **Design Report** (≤ 2 pages): design choices, training curves (loss), sample generations, one small ablation (e.g., fewer heads or shorter block size).
- Reproducibility: Python/pip/conda environment, seed, and exact commands.

---

# Part 0 — Setup, Data, and Notation

We model a character sequence $x_1, x_2, \dots, x_T$ and train to maximize the **autoregressive** likelihood
$$
p_\theta(x_1,\dots,x_T)=\prod_{t=1}^{T} p_\theta(x_t \mid x_{<t}).
$$
Equivalently, we **minimize** the **negative log-likelihood (NLL)** or **cross-entropy**:
$$
\mathcal{L}(\theta) = - \sum_{t=1}^{T} \log p_\theta(x_t \mid x_{<t}).
$$

We use Tiny Shakespeare (∼1 MB). We’ll work at **character level** for simplicity. (See the Colab for this exact dataset and a reference implementation.)【8†source】

```python
# ===== Part 0: Setup and Data =====
import os, math, random, urllib.request, sys
import torch
import torch.nn as nn
from torch.nn import functional as F

# Reproducibility
SEED = 1337
random.seed(SEED); torch.manual_seed(SEED)

# Download dataset if missing
if not os.path.exists('input.txt'):
    urllib.request.urlretrieve(
        'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt',
        'input.txt'
    )

with open('input.txt', 'r', encoding='utf-8') as f:
    text = f.read()

print("Dataset length (chars):", len(text))
print("Preview:\\n", text[:250])
```

**Tokenization (char-level):** build **stoi**/**itos** (string↔index) mappings and helpers.

```python
# Build vocabulary over unique characters
chars = sorted(list(set(text)))
vocab_size = len(chars)
stoi = {ch:i for i,ch in enumerate(chars)}
itos = {i:ch for i,ch in enumerate(chars)}

def encode(s: str):
    return [stoi[c] for c in s]

def decode(ixs):
    return ''.join(itos[i] for i in ixs)

# Encode the entire corpus as a 1D tensor of ints
data = torch.tensor(encode(text), dtype=torch.long)

# Train/val split
n = int(0.9 * len(data))
train_data = data[:n]
val_data   = data[n:]

print("Vocab size:", vocab_size)
```

**Batching with context windows:** We train with **fixed context length** $T$ (aka `block_size`). For each batch, we sample start indices and slice sequences $x_{t:t+T}$ and targets $x_{t+1:t+T+1}$.

```python
# Data loader for fixed-length contexts
device = 'cuda' if torch.cuda.is_available() else 'cpu'

block_size = 32   # max context length
batch_size = 64   # sequences per batch

def get_batch(split: str):
    src = train_data if split == 'train' else val_data
    ix = torch.randint(len(src) - block_size - 1, (batch_size,))
    x = torch.stack([src[i:i+block_size]     for i in ix])
    y = torch.stack([src[i+1:i+block_size+1] for i in ix])
    return x.to(device), y.to(device)
```

> **Why fixed-length context?** GPT attends over a sliding window of the past $T$ tokens. Computationally, self-attention scales as $O(T^2)$ in both memory and compute due to the attention matrix.

---

# Part 1 — Bigram Baseline (Sanity Check)

**Idea:** predict $x_{t+1}$ directly from $x_t$. This is crude but gives a runnable baseline. Implementation: an **embedding lookup** into a table of **logits** over the vocabulary. This matches the companion notebook’s first stage.【8†source】

Mathematically, logits for the next token are:
$$
\ell = E[x_t] \in \mathbb{R}^{V}\quad\Rightarrow\quad p(x_{t+1}=j\mid x_t)=\mathrm{softmax}(\ell)_j.
$$

```python
# ===== Part 1: Bigram Language Model =====
class BigramLM(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        # Each token maps to a length-V vector of logits for next token
        self.token_embedding_table = nn.Embedding(vocab_size, vocab_size)

    def forward(self, idx, targets=None):
        # idx: (B, T) integers
        logits = self.token_embedding_table(idx)      # (B, T, V)
        if targets is None:
            loss = None
        else:
            B, T, V = logits.size()
            loss = F.cross_entropy(logits.view(B*T, V), targets.view(B*T))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            logits, _ = self(idx)               # (B, T, V)
            logits = logits[:, -1, :]           # last time step
            probs = F.softmax(logits, dim=-1)   # (B, V)
            next_idx = torch.multinomial(probs, num_samples=1)  # sample
            idx = torch.cat([idx, next_idx], dim=1)
        return idx

# Quick smoke test
bigram = BigramLM(vocab_size).to(device)
xb, yb = get_batch('train')
with torch.no_grad():
    _, loss0 = bigram(xb, yb)
print("Bigram CE (untrained):", float(loss0))
```

**Train the baseline (briefly):**

```python
def train_model(model, steps=500, lr=1e-2):
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    model.train()
    for s in range(steps):
        xb, yb = get_batch('train')
        logits, loss = model(xb, yb)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if s % 100 == 0:
            print(f"step {s}: loss {loss.item():.4f}")
    return model

bigram = train_model(bigram, steps=500, lr=1e-2)
ctx = torch.zeros((1,1), dtype=torch.long, device=device)
sample = bigram.generate(ctx, max_new_tokens=300)[0].tolist()
print(decode(sample))
```

> Expect gibberish. This stage validates your data pipeline and objective before building attention (cf. the Colab’s baseline stage)【8†source】.

---

# Part 2 — From Weighted Averages to Self-Attention

**Goal:** understand how **self-attention** computes a contextualized representation at each position. For token features $x_t \in \mathbb{R}^d$, define:
- **Queries** $Q = X W_Q$,
- **Keys** $K = X W_K$,
- **Values** $V = X W_V$.

The (causal) attention weights from position $t$ to $s \le t$ are:
$$
\alpha_{t,s} = \mathrm{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}} + M\right)_{t,s},
$$
where $M$ applies **$-\infty$** above the diagonal to enforce causality (no peeking ahead). The output is
$$
\mathrm{Attn}(X) = \alpha V.
$$

**Why the scale $1/\sqrt{d_k}$?** Keeps dot-product variance near 1 so Softmax doesn’t saturate when $d_k$ grows, stabilizing training (as explained in the lecture and syllabus).

**Toy matrix view (one head):**

```python
# ===== Part 2: Toy attention with masking =====
torch.manual_seed(SEED)
B, T, C = 2, 5, 4  # batch, time, channels
x = torch.randn(B, T, C)

# Construct a lower-triangular (causal) mask
mask = torch.tril(torch.ones(T, T))
mask_bool = mask == 0

# Example: simple averaging of all previous positions (including self)
wei = torch.ones(T, T)
wei = wei.masked_fill(mask_bool, float('-inf'))
wei = F.softmax(wei, dim=-1)  # (T, T)

out = wei @ x[0]              # (T, C) -- for a single batch element
print("Causal average at each position:\n", out)
```

> This mirrors the companion notebook’s pedagogical build-up from averaging to softmax attention【8†source】.

---

# Part 3 — Single-Head Causal Self-Attention

We now implement a **single attention head** as a PyTorch module.

```python
# ===== Part 3: Single Causal Self-Attention Head =====
class CausalSelfAttentionHead(nn.Module):
    def __init__(self, n_embd, head_size, block_size, dropout=0.0):
        super().__init__()
        self.key   = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))
        self.dropout = nn.Dropout(dropout)
        self.head_size = head_size

    def forward(self, x):
        B, T, C = x.size()
        K = self.key(x)                  # (B, T, H)
        Q = self.query(x)                # (B, T, H)
        # Scaled dot-product attention
        wei = Q @ K.transpose(-2, -1)    # (B, T, T)
        wei = wei * (1.0 / math.sqrt(self.head_size))
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        V = self.value(x)                # (B, T, H)
        out = wei @ V                    # (B, T, H)
        return out
```

---

# Part 4 — Multi-Head + FeedForward + Residual + LayerNorm

**Multi-head**: concatenate $h$ heads along the channel dimension, then project back to $n_{\text{emb}}$.  
**FeedForward (MLP)**: position-wise MLP, typically $4\times$ expansion with nonlinearity.  
**Pre-LN Residual Block**: use LayerNorm before each sub-layer; residual connections stabilize deep stacks.

```python
# ===== Part 4: MHA, MLP, and Block =====
class MultiHeadAttention(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout=0.0):
        super().__init__()
        assert n_embd % n_head == 0
        head_size = n_embd // n_head
        self.heads = nn.ModuleList([
            CausalSelfAttentionHead(n_embd, head_size, block_size, dropout=dropout)
            for _ in range(n_head)
        ])
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)  # (B, T, C)
        out = self.proj(out)
        out = self.dropout(out)
        return out

class FeedForward(nn.Module):
    def __init__(self, n_embd, dropout=0.0):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)

class Block(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout=0.0):
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)
        self.sa  = MultiHeadAttention(n_embd, n_head, block_size, dropout=dropout)
        self.ln2 = nn.LayerNorm(n_embd)
        self.ff  = FeedForward(n_embd, dropout=dropout)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ff(self.ln2(x))
        return x
```

---

# Part 5 — Positional Embeddings and the GPT Shell

Self-attention is permutation-invariant, so we inject order via **positional embeddings** $\pi_t\in\mathbb{R}^{n_{\text{emb}}}$ and add them to token embeddings.

```python
# ===== Part 5: GPT (decoder-only) =====
class SmallGPT(nn.Module):
    def __init__(self, vocab_size, n_embd=128, n_head=4, n_layer=4,
                 block_size=block_size, dropout=0.1):
        super().__init__()
        self.block_size = block_size
        self.token_embedding = nn.Embedding(vocab_size, n_embd)
        self.pos_embedding   = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[
            Block(n_embd, n_head, block_size, dropout=dropout)
            for _ in range(n_layer)
        ])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)
        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
        if isinstance(m, nn.Linear) and m.bias is not None:
            nn.init.zeros_(m.bias)

    def forward(self, idx, targets=None):
        B, T = idx.size()
        assert T <= self.block_size, "Sequence length exceeds block size"
        tok = self.token_embedding(idx)                      # (B, T, C)
        pos = self.pos_embedding(torch.arange(T, device=idx.device))  # (T, C)
        x = tok + pos                                        # (B, T, C)
        x = self.blocks(x)                                   # (B, T, C)
        x = self.ln_f(x)                                     # (B, T, C)
        logits = self.lm_head(x)                             # (B, T, V)

        loss = None
        if targets is not None:
            B, T, V = logits.size()
            loss = F.cross_entropy(logits.view(B*T, V), targets.view(B*T))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens):
        self.eval()
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            next_idx = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, next_idx], dim=1)
        return idx
```

---

# Part 6 — Training Loop, Evaluation, and Sampling

We use **AdamW** and periodically estimate the train/val loss. This mirrors the training skeleton in the companion notebook【8†source】.

```python
# ===== Part 6: Training utilities =====
def estimate_loss(model, eval_iters=200):
    model.eval()
    out = {}
    with torch.no_grad():
        for split in ['train', 'val']:
            losses = torch.zeros(eval_iters, device=device)
            for k in range(eval_iters):
                xb, yb = get_batch(split)
                _, loss = model(xb, yb)
                losses[k] = loss
            out[split] = losses.mean().item()
    model.train()
    return out

# Hyperparameters (tune as desired)
n_embd   = 128
n_head   = 4
n_layer  = 4
dropout  = 0.1
max_iters     = 3000
eval_interval = 200
learning_rate = 3e-4

gpt = SmallGPT(vocab_size, n_embd, n_head, n_layer, block_size, dropout).to(device)
optimizer = torch.optim.AdamW(gpt.parameters(), lr=learning_rate)

for step in range(max_iters):
    xb, yb = get_batch('train')
    logits, loss = gpt(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

    if step % eval_interval == 0 or step == max_iters - 1:
        est = estimate_loss(gpt, eval_iters=100)
        print(f"step {step}: train {est['train']:.4f}, val {est['val']:.4f}")
```

**Generate text:**

```python
# ===== Sampling =====
start = torch.zeros((1,1), dtype=torch.long, device=device)  # BOS as index 0 is enough here
with torch.no_grad():
    out = gpt.generate(start, max_new_tokens=500)[0].tolist()
print(decode(out))
```

> As you scale $n_{\text{emb}}$, heads, layers, and training steps, quality improves—but watch validation loss to avoid overfitting on Tiny Shakespeare.

---

# Part 7 — Sanity Checks & Ablations

1. **Ablate**: Reduce $n_{\text{emb}}$, $n_{\text{head}}$, or $n_{\text{layer}}$. Observe loss and sample quality.
2. **Context length**: Try `block_size = 64` or `128`. Expect better long-range coherence at higher compute cost $O(T^2)$.
3. **Dropout**: Increase to regularize.
4. **Learning rate**: Too high → divergence; too low → slow learning.

---

# Part 8 — Full Program (All Pieces Together)

Copy this **single script** into `small_gpt.py` to run end-to-end. It reproduces the cumulative code above.

```python
#!/usr/bin/env python3
# small_gpt.py — Minimal decoder-only Transformer (Tiny Shakespeare)
import os, math, random, urllib.request
import torch
import torch.nn as nn
from torch.nn import functional as F

# ---- Repro ----
SEED = 1337
random.seed(SEED); torch.manual_seed(SEED)

# ---- Data ----
if not os.path.exists('input.txt'):
    urllib.request.urlretrieve(
        'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt',
        'input.txt'
    )
with open('input.txt', 'r', encoding='utf-8') as f:
    text = f.read()

chars = sorted(list(set(text)))
vocab_size = len(chars)
stoi = {ch:i for i,ch in enumerate(chars)}
itos = {i:ch for i,ch in enumerate(chars)}
def encode(s): return [stoi[c] for c in s]
def decode(ixs): return ''.join(itos[i] for i in ixs)
data = torch.tensor(encode(text), dtype=torch.long)

n = int(0.9 * len(data))
train_data = data[:n]
val_data   = data[n:]

device = 'cuda' if torch.cuda.is_available() else 'cpu'
block_size = 32
batch_size = 64

def get_batch(split):
    src = train_data if split == 'train' else val_data
    ix = torch.randint(len(src) - block_size - 1, (batch_size,))
    x = torch.stack([src[i:i+block_size]     for i in ix])
    y = torch.stack([src[i+1:i+block_size+1] for i in ix])
    return x.to(device), y.to(device)

# ---- Model components ----
class CausalSelfAttentionHead(nn.Module):
    def __init__(self, n_embd, head_size, block_size, dropout=0.0):
        super().__init__()
        self.key   = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))
        self.dropout = nn.Dropout(dropout)
        self.head_size = head_size

    def forward(self, x):
        B, T, C = x.size()
        K = self.key(x); Q = self.query(x); V = self.value(x)
        wei = Q @ K.transpose(-2, -1) * (1.0 / math.sqrt(self.head_size))
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        return wei @ V

class MultiHeadAttention(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout=0.0):
        super().__init__()
        assert n_embd % n_head == 0
        head_size = n_embd // n_head
        self.heads = nn.ModuleList([
            CausalSelfAttentionHead(n_embd, head_size, block_size, dropout) for _ in range(n_head)
        ])
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.dropout(self.proj(out))

class FeedForward(nn.Module):
    def __init__(self, n_embd, dropout=0.0):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4*n_embd),
            nn.ReLU(),
            nn.Linear(4*n_embd, n_embd),
            nn.Dropout(dropout),
        )
    def forward(self, x): return self.net(x)

class Block(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout=0.0):
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)
        self.sa  = MultiHeadAttention(n_embd, n_head, block_size, dropout)
        self.ln2 = nn.LayerNorm(n_embd)
        self.ff  = FeedForward(n_embd, dropout)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ff(self.ln2(x))
        return x

class SmallGPT(nn.Module):
    def __init__(self, vocab_size, n_embd=128, n_head=4, n_layer=4, block_size=32, dropout=0.1):
        super().__init__()
        self.block_size = block_size
        self.token_embedding = nn.Embedding(vocab_size, n_embd)
        self.pos_embedding   = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head, block_size, dropout) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)
        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, mean=0.0, std=0.02)
        if isinstance(m, nn.Linear) and m.bias is not None:
            nn.init.zeros_(m.bias)

    def forward(self, idx, targets=None):
        B, T = idx.size()
        tok = self.token_embedding(idx)
        pos = self.pos_embedding(torch.arange(T, device=idx.device))
        x = tok + pos
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)
        loss = None
        if targets is not None:
            B, T, V = logits.size()
            loss = F.cross_entropy(logits.view(B*T, V), targets.view(B*T))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens):
        self.eval()
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            next_idx = torch.multinomial(probs, num_samples=1)
            idx = torch.cat([idx, next_idx], dim=1)
        return idx

# ---- Train ----
device = 'cuda' if torch.cuda.is_available() else 'cpu'
gpt = SmallGPT(vocab_size, n_embd=128, n_head=4, n_layer=4, block_size=block_size, dropout=0.1).to(device)
optimizer = torch.optim.AdamW(gpt.parameters(), lr=3e-4)
max_iters, eval_interval = 3000, 200

def get_batch(split):
    src = train_data if split == 'train' else val_data
    ix = torch.randint(len(src) - block_size - 1, (batch_size,))
    x = torch.stack([src[i:i+block_size]     for i in ix])
    y = torch.stack([src[i+1:i+block_size+1] for i in ix])
    return x.to(device), y.to(device)

@torch.no_grad()
def estimate_loss(model, iters=100):
    model.eval()
    out = {}
    for split in ['train', 'val']:
        losses = torch.zeros(iters, device=device)
        for k in range(iters):
            xb, yb = get_batch(split)
            _, loss = model(xb, yb)
            losses[k] = loss
        out[split] = losses.mean().item()
    model.train()
    return out

for step in range(max_iters):
    xb, yb = get_batch('train')
    logits, loss = gpt(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

    if step % eval_interval == 0 or step == max_iters - 1:
        est = estimate_loss(gpt, iters=100)
        print(f"step {step}: train {est['train']:.4f}, val {est['val']:.4f}")

# ---- Sample ----
start = torch.zeros((1,1), dtype=torch.long, device=device)
out = gpt.generate(start, max_new_tokens=500)[0].tolist()
print(decode(out))
```

---
