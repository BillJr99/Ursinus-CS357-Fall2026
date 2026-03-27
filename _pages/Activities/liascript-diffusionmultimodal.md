<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-diffusionmultimodal.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-diffusionmultimodal.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# Foundations of AI: Diffusion & Multimodal AI

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals**

- Build intuition for **denoising diffusion** as learning the time-reversal of a Markov noising process.
- Derive the **forward (q)** and **reverse (p_θ)** processes and the **variational training objective**.
- Implement a **minimal diffusion model** (PyTorch) on grayscale digits with a tiny U-Net.
- Understand **classifier-free guidance**, **noise schedules**, and **sampling**.
- Explain **Latent Diffusion** (VAE encoder/decoder) and **text conditioning via cross-attention** (CLIP/Transformer).
- Survey **multimodality**: text↔image, image↔audio, and video; discuss safety, watermarking, and attribution.

---

## Slide Map (You Are Here)

1. Intuition  
2. Forward diffusion $q(x_t\mid x_{t-1})$  
3. Closed-form $q(x_t\mid x_0)$  
4. Reverse model $p_\theta(x_{t-1}\mid x_t)$  
5. Variational objective and the **simple loss**  
6. Sinusoidal time embeddings  
7. Tiny U-Net architecture  
8. Training loop  
9. Sampling loop  
10. Classifier-free guidance  
11. Latent diffusion & cross-attention  
12. Multimodal extensions  
13. Ethics & governance  

---

## 1) Intuition: Denoising as Time-Reversal

We define a **noising** chain that gradually corrupts data $x_0$ until it becomes nearly Gaussian noise $x_T$. The model learns the **reverse** denoising steps.

- Forward (known): add small Gaussian noise each step.  
- Reverse (unknown): predict how to remove a bit of noise at each step.

If we can learn the reverse transitions well, we can start from pure noise and **generate** new samples by denoising.

---

## 2) Forward Diffusion (Known) — $q(x_t\mid x_{t-1})$

Choose a variance schedule $\{\beta_t\}_{t=1}^T$ with $0<\beta_t<1$. Define

$$
q(x_t\mid x_{t-1}) := \mathcal{N}\big(\sqrt{1-\beta_t}\,x_{t-1},\; \beta_t\,I\big).
$$

Let $\alpha_t := 1-\beta_t$ and $\bar{\alpha}_t := \prod_{s=1}^t \alpha_s$.
Using composition of Gaussians,

$$
q(x_t\mid x_0) = \mathcal{N}\big(\sqrt{\bar{\alpha}_t}\,x_0,\; (1-\bar{\alpha}_t)I\big).
$$

This admits a one-shot sampling form:

$$
\boxed{x_t = \sqrt{\bar{\alpha}_t}\,x_0 + \sqrt{1-\bar{\alpha}_t}\,\varepsilon,\quad \varepsilon\sim\mathcal{N}(0,I).}
$$

---

## 3) Reverse Process (Learned) — $p_\theta(x_{t-1}\mid x_t)$

We parameterize the reverse as a Gaussian with mean and fixed variance:

$$
p_\theta(x_{t-1}\mid x_t) := \mathcal{N}\big(\mu_\theta(x_t,t),\; \sigma_t^2 I\big).
$$

A popular parameterization predicts the added noise $\varepsilon$ directly via a network $\varepsilon_\theta(x_t, t)$, leading to

$$
\mu_\theta(x_t,t) = \frac{1}{\sqrt{\alpha_t}}\Big(x_t - \frac{\beta_t}{\sqrt{1-\bar{\alpha}_t}}\,\varepsilon_\theta(x_t,t)\Big),\quad \sigma_t^2=\tilde{\beta}_t.
$$

Here $\tilde{\beta}_t$ is a closed-form variance from the forward chain.

---

## 4) Training Objective — Variational Lower Bound

Start from a variational bound on $\log p_\theta(x_0)$. After algebra and standard approximations, one recovers the **simple loss**:

$$
\boxed{\mathcal{L}_{\text{simple}}(\theta) = \mathbb{E}_{t\sim \mathcal{U}\{1..T\},\;x_0\sim p_{\text{data}},\;\varepsilon\sim\mathcal{N}(0,I)}\big[\,\lVert \varepsilon - \varepsilon_\theta(x_t,t)\rVert^2\big]} \\
\text{with } x_t = \sqrt{\bar{\alpha}_t}\,x_0 + \sqrt{1-\bar{\alpha}_t}\,\varepsilon.
$$

Interpretation: the network learns to predict **the exact noise** that produced $x_t$ from $x_0$.

---

## 5) Sinusoidal Time Embeddings

We embed discrete timestep $t\in\{1..T\}$ as a vector using sinusoids (as in Transformers):

$$
\mathrm{emb}[2k] = \sin\!\Big(\frac{t}{10000^{2k/d}}\Big),\quad
\mathrm{emb}[2k{+}1] = \cos\!\Big(\frac{t}{10000^{2k/d}}\Big).
$$

This provides a smooth representation of time for the network.

---

## 6) Tiny U-Net for $\varepsilon_\theta$

A minimal U-Net suffices for small images (e.g., 28×28): downsample → bottleneck → upsample, with skip connections. We inject the time embedding at each block (FiLM/affine modulation or concatenation).

---

## 7) Minimal PyTorch Implementation (Pedagogical)

```python
import math, torch
from torch import nn, optim
from torchvision import datasets, transforms

# ---------- Utilities ----------

def make_beta_schedule(T=1000, beta_start=1e-4, beta_end=0.02):
    return torch.linspace(beta_start, beta_end, T)

class SinusoidalTimeEmbedding(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
    def forward(self, t):
        device = t.device
        half = self.dim // 2
        freqs = torch.exp(
            -math.log(10000) * torch.arange(0, half, device=device).float() / half
        )
        args = t.float().unsqueeze(1) * freqs.unsqueeze(0)
        emb = torch.cat([torch.sin(args), torch.cos(args)], dim=1)
        if self.dim % 2 == 1:
            emb = torch.nn.functional.pad(emb, (0,1))
        return emb

# ---------- Tiny UNet ----------
class Block(nn.Module):
    def __init__(self, in_ch, out_ch, time_dim):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1), nn.GroupNorm(4, out_ch), nn.SiLU(),
            nn.Conv2d(out_ch, out_ch, 3, padding=1), nn.GroupNorm(4, out_ch), nn.SiLU(),
        )
        self.time = nn.Linear(time_dim, out_ch)
    def forward(self, x, t):
        h = self.conv(x)
        # FiLM-style conditioning
        time_emb = self.time(t)[:, :, None, None]
        return h + time_emb

class TinyUNet(nn.Module):
    def __init__(self, time_dim=128):
        super().__init__()
        self.time_emb = SinusoidalTimeEmbedding(time_dim)
        self.inc = Block(1, 32, time_dim)
        self.down = nn.Conv2d(32, 64, 4, stride=2, padding=1)
        self.mid = Block(64, 64, time_dim)
        self.up = nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1)
        self.out = nn.Conv2d(32, 1, 3, padding=1)
    def forward(self, x, t):
        t_emb = self.time_emb(t)
        h1 = self.inc(x, t_emb)
        h2 = torch.silu(self.down(h1))
        h3 = self.mid(h2, t_emb)
        h4 = torch.silu(self.up(h3))
        h = h4 + h1  # skip
        eps = self.out(h)
        return eps

# ---------- Diffusion Core ----------
class Diffusion(nn.Module):
    def __init__(self, T=200, beta_start=1e-4, beta_end=0.02):
        super().__init__()
        betas = make_beta_schedule(T, beta_start, beta_end)
        alphas = 1. - betas
        alpha_bars = torch.cumprod(alphas, dim=0)
        self.register_buffer('betas', betas)
        self.register_buffer('alphas', alphas)
        self.register_buffer('alpha_bars', alpha_bars)
        self.T = T
    def q_sample(self, x0, t, noise=None):
        if noise is None:
            noise = torch.randn_like(x0)
        sqrt_ab = torch.sqrt(self.alpha_bars[t])[:, None, None, None]
        sqrt_1mab = torch.sqrt(1 - self.alpha_bars[t])[:, None, None, None]
        return sqrt_ab * x0 + sqrt_1mab * noise

# ---------- Training Loop ----------
class DDPM(nn.Module):
    def __init__(self, model, diffusion):
        super().__init__()
        self.model = model
        self.diffusion = diffusion
    def training_step(self, x0):
        B = x0.size(0)
        t = torch.randint(0, self.diffusion.T, (B,), device=x0.device)
        noise = torch.randn_like(x0)
        xt = self.diffusion.q_sample(x0, t, noise)
        eps_pred = self.model(xt, t)
        return torch.mean((noise - eps_pred)**2)

# Data (MNIST in [-1,1])
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Lambda(lambda x: x*2-1)
])
train_loader = torch.utils.data.DataLoader(
    datasets.MNIST('./data', train=True, download=True, transform=transform),
    batch_size=128, shuffle=True
)

# Instantiate
net = TinyUNet(time_dim=128)
diff = Diffusion(T=200)
trainer = DDPM(net, diff)
opt = optim.Adam(net.parameters(), lr=2e-4)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
net.to(device)

for epoch in range(1, 6):
    total = 0.0
    for x, _ in train_loader:
        x = x.to(device)
        opt.zero_grad()
        loss = trainer.training_step(x)
        loss.backward()
        opt.step()
        total += loss.item() * x.size(0)
    print(f"epoch {epoch}: mse={total/len(train_loader.dataset):.4f}")
```

---

## 8) Sampling (Ancestral) from Noise

Given $x_T\sim\mathcal{N}(0,I)$, iterate $t=T,\dots,1$:

$$
\mu_\theta(x_t,t) = \frac{1}{\sqrt{\alpha_t}}\left(x_t - \frac{\beta_t}{\sqrt{1-\bar{\alpha}_t}}\,\varepsilon_\theta(x_t,t)\right),\quad
\sigma_t^2=\tilde{\beta}_t.
$$

```python
@torch.no_grad()
def sample(net, diff, n=16):
    net.eval()
    device = next(net.parameters()).device
    x = torch.randn(n, 1, 28, 28, device=device)
    for t in reversed(range(diff.T)):
        tt = torch.full((n,), t, device=device, dtype=torch.long)
        eps = net(x, tt)
        beta_t = diff.betas[tt][:, None, None, None]
        alpha_t = diff.alphas[tt][:, None, None, None]
        abar_t = diff.alpha_bars[tt][:, None, None, None]
        mu = (1/torch.sqrt(alpha_t)) * (x - (beta_t/torch.sqrt(1-abar_t)) * eps)
        if t > 0:
            z = torch.randn_like(x)
            sigma = torch.sqrt(beta_t)
            x = mu + sigma * z
        else:
            x = mu
    return (x.clamp(-1,1)+1)/2  # back to [0,1]
```

---

## 9) Classifier-Free Guidance (CFG)

For conditional generation (e.g., text), train the model with conditions **dropped** at random with probability $p$ (use a special null token). At sampling time, predict two noises and blend:

$$
\hat{\varepsilon}_\theta = (1+w)\,\varepsilon_\theta(x_t,t,\text{cond}) - w\,\varepsilon_\theta(x_t,t,\varnothing),\quad w\ge 0.
$$

This increases adherence to condition at the cost of diversity.

---

## 10) Latent Diffusion = \(\text{VAE}^{-1}\circ\text{U-Net}\circ\text{VAE}\)

**Latent Diffusion Models (LDM)** first compress the image to a lower-dimensional latent $z$ using a pretrained **VAE encoder** $E$. Diffusion runs in latent space, then a **VAE decoder** $D$ maps back to pixels:

$$
\text{image} \xrightarrow{E} z \xrightarrow{\text{diffusion}} z' \xrightarrow{D} \hat{\text{image}}.
$$

Benefits: faster training/sampling; U-Net operates on smaller feature maps.

---

## 11) Text Conditioning via Cross-Attention (CLIP/Transformer)

- Encode the text prompt with a Transformer/CLIP text encoder to get token embeddings.
- Insert **cross-attention** layers in the U-Net so image features attend to text features at each resolution.
- With CFG, drop text sometimes during training to enable unconditional branch.

---

## 12) Multimodality Beyond Text↔Image

- **Image→Audio** (sonification): condition a diffusion audio decoder on visual embeddings.
- **Audio→Image**: condition the U-Net on learned audio features.
- **Video**: add temporal convolutions/attention; sample in time and space; use 3D U-Nets.
- **Masked editing / inpainting**: keep pixels under mask fixed; diffuse only in unmasked regions.

---

## 13) Practical Tips & Diagnostics

- **Schedules**: cosine schedules often outperform linear for perceptual quality.
- **Parameterizations**: predict $\varepsilon$, $x_0$, or velocity $v$ (flow matching); choose consistent loss.
- **EMA** of weights stabilizes sampling.
- **Metrics**: FID, CLIPScore, human eval.
- **Debug**: overfit on a single batch to ensure loss can go to near 0; visualize denoising trajectories.

---

## 14) Ethics, Safety, and Governance

- **Deepfakes & misinformation**: mandate provenance (watermarking, signed metadata).
- **Consent & licensing**: ensure training data has appropriate rights.
- **Bias**: prompts can amplify stereotypes; evaluate across demographics.
- **Civic harms**: election manipulation, harassment; apply rate limits and content filters.
- **Attribution**: credit styles/datasets; disclose AI usage.

**Prompt:** Propose a policy for diffusion use in your research lab that addresses data rights, disclosure, and harm mitigation.

{{1}}

---

## 15) Studio Checklist (In-Class)

1. Train the tiny U-Net for 1–2 epochs; confirm decreasing MSE.
2. Generate 4×4 samples; inspect quality.
3. Swap linear for cosine schedule; compare.
4. Implement CFG stub with a dummy "class" condition.
5. (Stretch) Add a second down/up stage to the U-Net.

**Deliverable:** short lab note with samples and observations on schedule & guidance.

---

## References (selected)

- Ho, Jain, Abbeel (2020). *Denoising Diffusion Probabilistic Models*.
- Dhariwal & Nichol (2021). *Diffusion Models Beat GANs on Image Synthesis*.
- Rombach et al. (2022). *High-Resolution Image Synthesis with Latent Diffusion Models*.
- Saharia et al. (2022). *Imagen*.
- Radford et al. (2021). *CLIP*.

---
