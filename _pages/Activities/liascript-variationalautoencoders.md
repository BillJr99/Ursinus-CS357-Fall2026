<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-variationalautoencoders.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-variationalautoencoders.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# Foundations of AI: Variational Autoencoders (VAEs)

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals:**

- Explain the architecture of a **Variational Autoencoder** and how it extends classical autoencoders.  
- Derive the **Evidence Lower Bound (ELBO)** and explain the role of the **reparameterization trick** in enabling gradient-based learning.  
- Implement a **basic VAE** in Python (PyTorch) and train it on MNIST digits.  
- Visualize and interpret the **latent space** learned by a VAE.  
- Compare VAEs to other generative models (GANs, diffusion); discuss tradeoffs.  
- Reflect on ethical implications: hallucination, representation, and the “AI psychosis” framing.  

---

## From Autoencoders to Variational Autoencoders

- **Autoencoder (AE):**
  - Encoder $f_\phi(x) \to z$, Decoder $g_\theta(z) \to \hat{x}$.  
  - Objective: minimize $\lVert x - \hat{x} \rVert^2$ or binary cross-entropy.  

- **Limitation:**  
  - Latent space is often irregular or fragmented.  
  - Interpolation between latent codes may not correspond to valid data.  

- **Variational Autoencoder (VAE):**  
  - Encoder outputs **distribution parameters** $(\mu, \sigma^2)$.  
  - Sample latent variable $z$ from $q_\phi(z \mid x)$.  
  - Regularize $q_\phi(z \mid x)$ toward prior $p(z)$ (usually $\mathcal{N}(0,I)$).  

---

## Probabilistic Formulation

We want to maximize the data likelihood:

$$
p_\theta(x) = \int p_\theta(x \mid z) p(z) \, dz
$$

- $p(z)$ = prior (Gaussian).  
- $p_\theta(x \mid z)$ = decoder likelihood.  
- $q_\phi(z \mid x)$ = encoder approximate posterior.  

---

## The Evidence Lower Bound (ELBO)

The log likelihood is intractable:

$$
\log p_\theta(x) = \log \int p_\theta(x \mid z) p(z) dz
$$

Introduce variational distribution $q_\phi(z|x)$:

$$
\log p_\theta(x) \geq \mathbb{E}_{z \sim q_\phi(z|x)}[\log p_\theta(x|z)] - D_{KL}(q_\phi(z|x) \parallel p(z))
$$

This is the **ELBO**, optimized during training.  
- First term: reconstruction accuracy.  
- Second term: encourages latent distributions to stay close to prior.  

---

## The Reparameterization Trick

Naïve sampling blocks gradients. Solution:

$$
z \sim q_\phi(z|x) = \mathcal{N}(\mu_\phi(x), \sigma_\phi(x)^2 I)
$$

Reparameterize:

$$
z = \mu_\phi(x) + \sigma_\phi(x) \odot \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)
$$

This allows gradients to flow through $\mu_\phi$ and $\sigma_\phi$ while $\epsilon$ handles randomness.  

---

## VAE Architecture Diagram

```
Input x --> [Encoder f_φ] --> μ(x), logσ²(x)
          --> [Reparameterization: μ + σ ⊙ ε] = z
          --> [Decoder g_θ] --> reconstruction x̂
```

---

## VAE Training in PyTorch

```python
import torch
from torch import nn, optim
from torchvision import datasets, transforms

# Encoder
class Encoder(nn.Module):
    def __init__(self, latent_dim=2):
        super().__init__()
        self.fc1 = nn.Linear(784, 400)
        self.fc_mu = nn.Linear(400, latent_dim)
        self.fc_logvar = nn.Linear(400, latent_dim)
        self.relu = nn.ReLU()
    def forward(self, x):
        h = self.relu(self.fc1(x))
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar

# Decoder
class Decoder(nn.Module):
    def __init__(self, latent_dim=2):
        super().__init__()
        self.fc1 = nn.Linear(latent_dim, 400)
        self.fc_out = nn.Linear(400, 784)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    def forward(self, z):
        h = self.relu(self.fc1(z))
        return self.sigmoid(self.fc_out(h))

# Reparameterization
def reparameterize(mu, logvar):
    std = torch.exp(0.5*logvar)
    eps = torch.randn_like(std)
    return mu + eps * std

# VAE
class VAE(nn.Module):
    def __init__(self, latent_dim=2):
        super().__init__()
        self.encoder = Encoder(latent_dim)
        self.decoder = Decoder(latent_dim)
    def forward(self, x):
        mu, logvar = self.encoder(x)
        z = reparameterize(mu, logvar)
        recon = self.decoder(z)
        return recon, mu, logvar

# Loss (ELBO)
def vae_loss(recon_x, x, mu, logvar):
    BCE = nn.functional.binary_cross_entropy(recon_x, x, reduction='sum')
    KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return BCE + KLD

# Training loop
transform = transforms.Compose([transforms.ToTensor(), lambda x: x.view(-1)])
train_loader = torch.utils.data.DataLoader(
    datasets.MNIST('./data', train=True, download=True, transform=transform),
    batch_size=128, shuffle=True)

model = VAE(latent_dim=2)
optimizer = optim.Adam(model.parameters(), lr=1e-3)

def train(epoch):
    model.train()
    total_loss = 0
    for x, _ in train_loader:
        x = x.view(-1, 784)
        optimizer.zero_grad()
        recon, mu, logvar = model(x)
        loss = vae_loss(recon, x, mu, logvar)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch}, Avg loss: {total_loss / len(train_loader.dataset):.4f}")

for epoch in range(1, 6):
    train(epoch)
```

---

## Visualizing the Latent Space

- Use a **2D latent space** for visualization.  
- Encode MNIST digits to obtain $z = \mu_\phi(x)$.  
- Plot embeddings colored by digit label.  
- Interpolate between latent vectors → smooth morphing of digits.  

!?[VAE Latent Space Interpolation Example](https://upload.wikimedia.org/wikipedia/commons/3/3a/VAE_example.png)

---

## Comparing Generative Models

- **VAEs:** Probabilistic, interpretable latent space, reconstructions sometimes blurry.  
- **GANs:** Sharp images, but unstable training and mode collapse.  
- **Diffusion models:** High fidelity, iterative and computationally expensive, state-of-the-art for images.  

**Discussion:** Which tradeoffs matter most for your applications (e.g. scientific models vs. art)?  

{{1}}

---

## Ethical & Societal Considerations

Reading: *The Emerging Problem of AI Psychosis* (Psychology Today)【28:0†syllabus.md】

- **Hallucination:** VAEs can generate plausible but false samples.  
- **Latent misalignment:** Distorted representations may produce nonsensical or biased outputs.  
- **Anthropomorphism:** Comparing model failure to "psychosis" may mislead; real mental health conditions differ fundamentally.  
- **Responsibility:** Who is accountable for harmful synthetic outputs?  

**Reflection Prompt:**
- In what ways does the latent representation resemble a “dream world”?  
- Is it accurate to describe failure as “AI psychosis,” or is that an ethical misstep?  

{{2}}

---

## References & Further Reading

- Kingma & Welling (2014), *Auto-Encoding Variational Bayes*.  
- Doersch (2016), *Tutorial on Variational Autoencoders*.  
- Rezende et al. (2014), *Stochastic Backpropagation and Approximate Inference in Deep Generative Models*.  
- Mitchell, *Artificial Intelligence: A Guide for Thinking Humans* (Ch. 11–12).  
- Boden, *Philosophy of Artificial Intelligence* (Ch. 15).  
- Psychology Today (2025). *The Emerging Problem of AI Psychosis*.  

---