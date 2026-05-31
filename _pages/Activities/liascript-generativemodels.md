<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-generativemodels.md or locally if deployed via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-generativemodels.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# Foundations of AI: Generative Models

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals:**

- Define **generative models** and distinguish them from discriminative models.  
- Describe common families: **Bayesian models, autoregressive models, VAEs, GANs, diffusion**.  
- Derive likelihood-based training for generative models.  
- Explore applications: text generation, image synthesis, protein folding.  
- Discuss risks: hallucinations, bias amplification, misuse in disinformation.  
- Reflect on ethical considerations: authorship, creativity, and responsibility.  

**Additional outcomes (after today):**

- Compute and interpret **perplexity**, **negative log-likelihood**, **FID**, and **reconstruction error**.  
- Derive the **ELBO** and implement the **reparameterization trick**.  
- Explain the connection between **cross-entropy** and **maximum likelihood**.  
- Write compact **PyTorch** prototypes for AR, VAE, GAN, and diffusion training loops.

**Notation:**

- Random variables in italics (e.g., $x, z$). Vectors bold (e.g., $\mathbf{x}$).  
- Expectations: $\mathbb{E}_{x\sim p}[\cdot]$. KL: $\mathrm{KL}(p\,\Vert\,q)$.  
- Log-likelihood: $\ell(\theta) = \sum_{i=1}^N \log p_\theta(x^{(i)})$.

---

## Generative vs. Discriminative Models

- **Discriminative model**: learns $p(y \mid x)$  
  Examples: logistic regression, neural classifiers.

- **Generative model**: learns $p(x)$ or $p(x,y)$  
  Examples: language models that generate text, VAEs & GANs that synthesize images.

![Discriminative vs. Generative](https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/Discriminative_vs_Generative_Neural_Networks.png

**Think–Pair–Share:**  
Why might learning $p(x)$ be *harder* than learning $p(y\mid x)$?  

{{1}}

### Mathematical framing

- **Maximum Likelihood (ML):** Given data $\mathcal{D}=\{x^{(i)}\}_{i=1}^N$, fit parameters $\theta$ by  
  $$\hat{\theta} \;=\; \arg\max_{\theta} \sum_{i=1}^N \log p_\theta(x^{(i)}).$$

- Equivalent to minimizing **cross-entropy** between the true data distribution $p^\star$ and the model $p_\theta$:  
  $$\mathcal{H}(p^\star, p_\theta) = \mathbb{E}_{x \sim p^\star}[-\log p_\theta(x)].$$

- This is equivalent to minimizing **KL divergence**:  
  $$\mathrm{KL}\!\big(p^\star \parallel p_\theta\big) = \sum_x p^\star(x) \log \frac{p^\star(x)}{p_\theta(x)}.$$

---

## A First Example: Language Modeling

Consider predicting the next word in a sentence.

- **Bigram model**:  
  $$p(w_t \mid w_{t-1}) = \frac{\text{count}(w_{t-1}, w_t)}{\text{count}(w_{t-1})}$$  

- Generalize to **n-gram models**.  

- Limitation: **context window** is fixed, sparsity is severe.  

**Python: minimal bigram model (toy corpus)**

```python
from collections import defaultdict, Counter
import random

corpus = """
the quick brown fox jumps over the lazy dog . the quick blue bird sings .
the quick fox is quick .
""".lower().split()

# Build bigram counts
bigram = defaultdict(Counter)
for w1, w2 in zip(corpus[:-1], corpus[1:]):
    bigram[w1][w2] += 1

def sample_next(w1):
    ctr = bigram.get(w1, None)
    if not ctr:
        return random.choice(list(set(corpus)))
    total = sum(ctr.values())
    r = random.random() * total
    cum = 0
    for w, c in ctr.items():
        cum += c
        if r <= cum:
            return w

def generate(seed="the", max_len=12):
    out = [seed]
    for _ in range(max_len-1):
        out.append(sample_next(out[-1]))
    return " ".join(out)

print(generate("the"))
```

---

## Generative Deep Models

### Autoregressive Models
- Predict the next token given history:  
  $$p(x) = \prod_{t=1}^T p(x_t \mid x_{<t})$$
- Examples: GPT, PixelRNN.  

**Transformer attention (single head):**

$$\text{Attn}(Q,K,V) \;=\; \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}} + M\right)V$$

where $M$ is a **causal mask** ensuring the model cannot attend to future tokens.  

**Training challenge:**  
- *Teacher forcing*: model always conditions on ground-truth prefixes.  
- *Exposure bias*: during inference, must condition on its own mistakes.  

**Python (tiny causal Transformer):**

```python
import torch, torch.nn as nn, torch.nn.functional as F

class TinyAR(nn.Module):
    def __init__(self, vocab, d=128, n=2, nhead=4, block=128):
        super().__init__()
        self.stoi = {ch:i for i,ch in enumerate(vocab)}
        self.itos = {i:ch for ch,i in self.stoi.items()}
        self.embed = nn.Embedding(len(vocab), d)
        layer = nn.TransformerEncoderLayer(d, nhead, dim_feedforward=4*d, batch_first=True)
        self.enc = nn.TransformerEncoder(layer, n)
        self.pos = nn.Parameter(torch.randn(1, block, d)*0.01)
        self.lm = nn.Linear(d, len(vocab))
        self.block = block

    def forward(self, x):
        B,T = x.size()
        h = self.embed(x) + self.pos[:,:T]
        mask = torch.triu(torch.ones(T,T)*float('-inf'), diagonal=1)
        h = self.enc(h, mask=mask)
        return self.lm(h)

    def encode(self, s): return torch.tensor([[self.stoi[c] for c in s]], dtype=torch.long)
    def decode(self, idxs): return ''.join(self.itos[int(i)] for i in idxs)

    @torch.no_grad()
    def generate(self, prompt, max_new=50, temperature=1.0):
        x = self.encode(prompt)
        for _ in range(max_new):
            x_in = x[:,-self.block:]
            logits = self.forward(x_in)[:,-1,:]/temperature
            probs = F.softmax(logits, dim=-1)
            x = torch.cat([x, torch.multinomial(probs, num_samples=1)], dim=1)
        return prompt + self.decode(x[0, len(prompt):])
```

---

### Variational Autoencoders (VAEs)

- Latent variable model:  
  $$p_\theta(x) = \int p_\theta(x \mid z) p(z)\,dz, \quad p(z)=\mathcal{N}(0,I)$$

- **Problem:** $\log p_\theta(x)$ intractable due to integral.

- **Solution:** Introduce variational posterior $q_\phi(z\mid x)$ and derive the **ELBO**:
  $$\log p_\theta(x) = \mathbb{E}_{q_\phi(z\mid x)}[\log p_\theta(x\mid z)] - \mathrm{KL}\!\left(q_\phi(z\mid x)\,\Vert\,p(z)\right) + \mathrm{KL}\!\left(q_\phi(z\mid x)\,\Vert\,p_\theta(z\mid x)\right).$$

- Dropping the last nonnegative term yields the **Evidence Lower Bound (ELBO):**
  $$\mathcal{L}_{\text{ELBO}}(\theta,\phi;x) = \mathbb{E}_{q_\phi(z\mid x)}[\log p_\theta(x\mid z)] - \mathrm{KL}\!\left(q_\phi(z\mid x)\,\Vert\,p(z)\right).$$

**Reparameterization trick:** sample $z = \mu_\phi(x) + \sigma_\phi(x) \odot \epsilon, \; \epsilon \sim \mathcal{N}(0,I)$ to allow gradients to flow.

**PyTorch snippet (VAE skeleton):**

```python
class VAE(nn.Module):
    def __init__(self, dim_in=784, dim_latent=20, hidden=400):
        super().__init__()
        self.fc1 = nn.Linear(dim_in, hidden)
        self.fc_mu = nn.Linear(hidden, dim_latent)
        self.fc_logvar = nn.Linear(hidden, dim_latent)
        self.fc_dec = nn.Linear(dim_latent, hidden)
        self.fc_out = nn.Linear(hidden, dim_in)

    def encode(self, x):
        h = torch.relu(self.fc1(x))
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5*logvar)
        eps = torch.randn_like(std)
        return mu + eps*std

    def decode(self, z):
        h = torch.relu(self.fc_dec(z))
        return torch.sigmoid(self.fc_out(h))

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar
```

---

### Generative Adversarial Networks (GANs)

- **Minimax game:**
  $$\min_G \max_D \; \mathbb{E}_{x\sim p_{data}}[\log D(x)] + \mathbb{E}_{z\sim p(z)}[\log(1-D(G(z)))]$$

- Generator $G(z)$: maps noise to fake samples.  
- Discriminator $D(x)$: outputs probability that $x$ is real.  

**Challenges:**
- Mode collapse: $G$ produces limited diversity.  
- Training instability: $D$ vs. $G$ may oscillate.  

**Variants:** WGAN (Wasserstein GAN), DCGAN, StyleGAN.

**PyTorch training loop (simplified):**

```python
for real,_ in dataloader:
    # Train discriminator
    z = torch.randn(batch, latent_dim)
    fake = G(z).detach()
    loss_D = - (torch.log(D(real)) + torch.log(1 - D(fake))).mean()
    loss_D.backward()
    optD.step()

    # Train generator
    z = torch.randn(batch, latent_dim)
    fake = G(z)
    loss_G = - torch.log(D(fake)).mean()
    loss_G.backward()
    optG.step()
```

---

### Diffusion Models

- Add Gaussian noise gradually: $x_T \sim \mathcal{N}(0,I)$, then learn to reverse the process.
- Forward process:
  $$q(x_t \mid x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t} x_{t-1}, \beta_t I)$$
- Model learns $p_\theta(x_{t-1} \mid x_t)$ to denoise.

- **Applications:** Stable Diffusion, DALL·E, Imagen.  
- Strength: high fidelity, controllable generation.  
- Limitation: computationally expensive sampling (many steps).  

**Training loss (simplified):**
  $$\mathcal{L}(\theta) = \mathbb{E}_{t, x_0, \epsilon}[ \|\epsilon - \epsilon_\theta(x_t,t)\|^2 ]$$

---

## Studio: Hands-On Generative Modeling

1. **N-gram Text Generation**  
   - Try the [Bigram Word Generator](https://colab.research.google.com/github/BillJr99/Ursinus-CS357/blob/gh-pages/files/notebooks/Bigram_Word_Generator.ipynb).  
   - What kinds of outputs does it produce?   

2. **Image Generation Demo**  
   - Use [DALL·E](https://openai.com/dall-e) or [Stable Diffusion web demo](https://stability.ai/).  
   - Prompt: “A robot dreaming of a surreal cityscape in watercolor.”  
   - Share results with peers.  

3. **Compare with Discriminative Task**  
   - Train a classifier (MNIST digit recognition).  
   - Contrast what “generation” vs. “classification” looks like.  

---

## Ethical & Societal Considerations

- **Authorship & originality**: Who owns generated content?  
- **Bias & fairness**: Generative models can reproduce stereotypes.  
- **Misinformation**: Deepfakes, synthetic text in politics.  
- **Sustainability**: Training large generative models requires massive energy.  
- **Alignment**: How can we ensure generated content aligns with human values?  

**Discussion Prompt:**  
Is a generative model *creative*? Or is it merely remixing?  

{{2}}

---

## References & Further Reading

- Goodfellow et al., *Deep Learning* (2016) — Chapter on generative models.  
- Kingma & Welling (2014), *Auto-Encoding Variational Bayes*.  
- Goodfellow et al. (2014), *Generative Adversarial Nets*.  
- Ho et al. (2020), *Denoising Diffusion Probabilistic Models*.  
- Mitchell, *Artificial Intelligence: A Guide for Thinking Humans* (Ch. 9).  

---


### Variational Autoencoders (VAEs)

- Latent variable model:  
  $$p_\theta(x) = \int p_\theta(x \mid z) p(z)\,dz, \quad p(z)=\mathcal{N}(0,I)$$

- **Problem:** $\log p_\theta(x)$ is intractable due to the integral.

- **Solution:** Introduce variational posterior $q_\phi(z\mid x)$ and derive the **Evidence Lower Bound (ELBO):**  

  $$\log p_\theta(x) \geq \mathbb{E}_{q_\phi(z\mid x)}[\log p_\theta(x\mid z)] - \mathrm{KL}(q_\phi(z\mid x)\,\Vert\,p(z))$$

- **Reparameterization trick:** sample $z = \mu_\phi(x) + \sigma_\phi(x) \odot \epsilon$, with $\epsilon \sim \mathcal{N}(0,I)$ to allow gradient backpropagation.

**PyTorch sketch:**

```python
class VAE(nn.Module):
    def __init__(self, input_dim=784, hidden_dim=400, z_dim=20):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc_mu = nn.Linear(hidden_dim, z_dim)
        self.fc_logvar = nn.Linear(hidden_dim, z_dim)
        self.fc_dec1 = nn.Linear(z_dim, hidden_dim)
        self.fc_dec2 = nn.Linear(hidden_dim, input_dim)

    def encode(self, x):
        h = F.relu(self.fc1(x))
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5*logvar)
        eps = torch.randn_like(std)
        return mu + eps*std

    def decode(self, z):
        h = F.relu(self.fc_dec1(z))
        return torch.sigmoid(self.fc_dec2(h))

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar

def elbo_loss(x, recon_x, mu, logvar):
    BCE = F.binary_cross_entropy(recon_x, x, reduction='sum')
    KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return BCE + KLD
```

---

### Generative Adversarial Networks (GANs)

- **Two-player minimax game:**  
  $$\min_G \max_D \; \mathbb{E}_{x\sim p_{data}}[\log D(x)] + \mathbb{E}_{z\sim p(z)}[\log(1-D(G(z)))]$$

- **Generator $G(z)$:** learns to map noise to realistic data.  
- **Discriminator $D(x)$:** learns to distinguish real vs. generated.  
- **Nash equilibrium:** when $p_g(x) = p_{data}(x)$.

**Training instability issues:** mode collapse, vanishing gradients.  
**Variants:** WGAN (Earth-Mover distance), DCGAN (CNN architectures), StyleGAN.

**PyTorch sketch:**

```python
class Generator(nn.Module):
    def __init__(self, z_dim=100, hidden_dim=128, img_dim=784):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(z_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, img_dim),
            nn.Tanh()
        )
    def forward(self, z):
        return self.net(z)

class Discriminator(nn.Module):
    def __init__(self, img_dim=784, hidden_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(img_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.net(x)
```

**Training loop (sketch):**

```python
z = torch.randn(batch_size, z_dim)
fake = G(z)
loss_D = -torch.mean(torch.log(D(real)) + torch.log(1 - D(fake.detach())))
loss_G = -torch.mean(torch.log(D(fake)))
```

---

### Diffusion Models

- **Forward process (diffusion):** gradually add Gaussian noise to data:  
  $$q(x_t \mid x_{t-1}) = \mathcal{N}(\sqrt{1-\beta_t}\,x_{t-1}, \beta_t I)$$

- **Reverse process (denoising):** learn $p_\theta(x_{t-1}\mid x_t)$.  

- At inference, start from noise $x_T \sim \mathcal{N}(0,I)$ and iteratively denoise.  

- **Objective (simplified):** train $\epsilon_\theta(x_t, t)$ to predict noise $\epsilon$.  
  $$L_{\text{simple}} = \mathbb{E}_{x,\epsilon,t}\big[\|\epsilon - \epsilon_\theta(x_t, t)\|^2\big]$$

**PyTorch sketch (simplified 1D):**

```python
class SimpleDenoiser(nn.Module):
    def __init__(self, dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim+1, 256),
            nn.ReLU(),
            nn.Linear(256, dim)
        )
    def forward(self, x_t, t):
        # Concatenate timestep embedding
        t_embed = t.unsqueeze(1).float()/1000
        return self.net(torch.cat([x_t, t_embed], dim=1))
```

**Key insight:** Diffusion turns generation into a sequence of denoising steps, often yielding **high-fidelity, diverse samples** (e.g., Stable Diffusion, DALL·E 3).



---

## Comparative Synthesis & Applications

### Comparing Model Families

| Model Type | Factorization / Idea | Strengths | Weaknesses | Applications |
|------------|----------------------|-----------|------------|--------------|
| **Autoregressive (AR)** | $p(x)=\prod_t p(x_t \mid x_{<t})$ | Exact likelihood, straightforward training | Slow sampling, exposure bias | Language models (GPT), PixelRNN |
| **VAE** | Latent $z$ with ELBO training | Efficient latent representation, structured priors | Blurry samples, KL collapse | Representation learning, anomaly detection |
| **GAN** | Generator vs. discriminator game | Sharp high-fidelity samples | Mode collapse, unstable training | Image synthesis (faces, art), data augmentation |
| **Diffusion** | Denoising from noise | High diversity, state-of-art image quality | Computationally expensive sampling | Text-to-image (Stable Diffusion, DALL·E), audio, video |

### Key Connections

- **AR vs. VAE:** AR maximizes exact likelihood, VAEs approximate it via ELBO.  
- **GAN vs. likelihood-based:** GANs bypass explicit likelihood, focusing on realism via a discriminator.  
- **Diffusion as AR in noise space:** iterative refinement instead of direct sampling.  

### Real-World Impact

- **Language:** GPT models power assistants, summarization, code generation.  
- **Vision:** GANs (StyleGAN) create photorealistic faces; Diffusion models dominate creative image generation.  
- **Science:** AlphaFold (structure prediction) combines generative modeling with domain knowledge.  
- **Cross-modal:** Text-to-audio, text-to-3D, video synthesis are emerging from diffusion + transformers.  

### Broader Considerations

- **Ethics:** Creative ownership, misuse for disinformation, representation biases.  
- **Sustainability:** Diffusion & LLMs require massive compute and energy.  
- **Future directions:** Smaller, more efficient models; controllability; alignment with human values.  

**Final Discussion Prompt:**  
Which model family do you think best balances *expressiveness*, *efficiency*, and *safety* for the future of AI?  

{{2}}

---

## References & Further Reading

- Goodfellow et al., *Deep Learning* (2016) — Chapter on generative models.  
- Kingma & Welling (2014), *Auto-Encoding Variational Bayes*.  
- Goodfellow et al. (2014), *Generative Adversarial Nets*.  
- Ho et al. (2020), *Denoising Diffusion Probabilistic Models*.  
- Mitchell, *Artificial Intelligence: A Guide for Thinking Humans* (Ch. 9).  

---
