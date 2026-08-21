<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-llmpretraining.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-llmpretraining.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# How LLMs Are Built: Tokenization, Pre-Training, and Scaling

The LLMs powering today's AI applications are not magic; they are the result of well-understood engineering decisions made during construction: how text is cut into pieces, what objective the model is trained to optimize, how many parameters and how much data are needed, and how weights are compressed for deployment. This activity traces the full construction path from **tokenization $\rightarrow$ byte-pair encoding by hand $\rightarrow$ causal vs. masked language modeling $\rightarrow$ cross-entropy loss in code $\rightarrow$ Chinchilla scaling laws $\rightarrow$ quantization for deployment**, building enough mechanical understanding to make informed choices about which models to use and how.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

| Role | Responsibility |
|------|----------------|
| **Manager** | Keeps the group on task and on time; ensures everyone participates |
| **Recorder** | Documents the group's answers and reasoning |
| **Presenter** | Shares the group's findings with the class |
| **Reflector** | Monitors group process and leads the reflection prompt |

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Tokenization** | The process of splitting raw text into discrete units (tokens) that a model can process: neither individual characters nor whole words, but learned subword units | "unhappiness" -> `un` + `happiness` (2 tokens); "the" -> `the` (1 token) |
| **Byte-Pair Encoding (BPE)** | A tokenization algorithm that starts with individual characters and repeatedly merges the most frequently occurring adjacent pair into a single new token, a compression algorithm applied to language | Starting with `l o w e r`, if `e r` is the most frequent pair, merge to `l o w er`; repeat until vocabulary reaches target size |
| **Vocabulary** | The fixed set of tokens a model knows: typically 30,000 to 200,000 entries; any text in the world can be encoded using these tokens (unknown characters fall back to byte-level tokens) | GPT-4 uses a vocabulary of ~100,000 tokens built by BPE on web text |
| **Causal Language Modeling (CLM)** | The GPT-style pre-training objective: given all previous tokens, predict the next token. Called "causal" because each token can only attend to tokens before it | Given "The cat sat on the", predict "mat"; each position predicts its successor |
| **Masked Language Modeling (MLM)** | The BERT-style pre-training objective: randomly mask 15% of tokens and predict the masked tokens from surrounding context in both directions | "The [MASK] sat on the mat" -> predict "cat" using both left and right context |
| **Cross-Entropy Loss** | The standard loss function for next-token prediction: measures how surprised the model was by the actual next token; lower is better, zero would mean perfect prediction with 100% confidence | If the model assigned 1% probability to the correct next token, cross-entropy = −log(0.01) ≈ 4.6; if it assigned 90%, cross-entropy = −log(0.9) ≈ 0.1 |
| **Chinchilla Scaling Laws** | Empirical findings from DeepMind (2022) showing that model size (parameters) and training data (tokens) should scale together at roughly a 1:20 ratio; training a model on 20× tokens per parameter maximizes performance for a given compute budget | A 7B-parameter model is "Chinchilla optimal" when trained on ~140B tokens; training it on only 1B tokens wastes the model's capacity |
| **Quantization** | Compressing model weights from high-precision floating-point (float32, 32 bits per number) to lower-precision integers (int8 or int4, 8 or 4 bits per number), trading a small accuracy loss for a large reduction in memory and inference speed | A 7B model in float32 requires ~28 GB of GPU memory; in int4 it requires ~4 GB, small enough to run on a laptop GPU |
| **Perplexity** | A measurement of how well a language model predicts a test set: the geometric mean of the inverse probability the model assigns to each token; lower is better | A perplexity of 10 means the model is, on average, as confused as if it had to choose uniformly among 10 equally likely options at each step |
| **Bits per Parameter** | The number of bits used to store each model weight: float32 = 32 bits, float16 = 16 bits, int8 = 8 bits, int4 = 4 bits; lower bits per parameter = smaller model file but potentially lower quality | A 7B int4 model uses 4 × 7,000,000,000 = 28 billion bits = ~3.5 GB; the same model in float32 uses 28 GB |

---

### Before You Start

**What you need:** Python 3.10+. No GPU, no training run; everything here is small enough to watch.

**What you will have at the end:** a tokenizer you built by hand and a concrete sense of what pre-training actually optimizes.

Work through the sections in order; each one builds on the last, and the code blocks are meant to be run as you reach them, not read past.

---

# Part I: Tokenization - Why We Don't Just Split on Spaces

In this part, you will work through the BPE algorithm by hand on a small example, understand why vocabulary size is a fundamental design tradeoff, and see concretely why tokenization causes models to struggle with letter-counting, arithmetic, and non-English text. These limitations directly affect how you design prompts, structure RAG chunks, and choose which model to use for a given task.

## 1. The Limits of Naive Tokenization

**Why this matters:** Tokenization is the first thing that happens to any text you send to an LLM, and it shapes everything downstream: what patterns the model can recognize, how long your context window actually is in practice, why the model cannot spell words reliably, and why languages with different scripts receive worse service from models trained primarily on English. Understanding tokenization is not a detour into implementation details; it is essential context for making good decisions about model selection, prompt design, and RAG chunk sizing.

Why not just split text on spaces? Three problems:

**Rare words explode the vocabulary.** If each unique word in the training corpus gets its own token, a vocabulary trained on Wikipedia alone would need over a million entries. This makes the embedding table enormous and forces the model to learn a separate representation for every inflected form of every word: "walk", "walks", "walked", "walking" all get separate tokens with no shared structure.

**Out-of-vocabulary (OOV) words become impossible.** In a word-level vocabulary, any word not seen during training cannot be represented at all. A model trained on English Wikipedia has no token for a company name coined in 2024, a user's misspelling, or text in another language.

**Character-level tokenization solves OOV but creates other problems.** With character-level tokens, every string is representable, but the sequence length explodes (the sentence "Hello!" becomes six tokens instead of one or two), the model must learn to model long-range dependencies across hundreds of characters, and the vocabulary must include every possible Unicode character.

**Subword tokenization** (the approach used by BPE, WordPiece, and Unigram) strikes a balance: frequent words get their own token; rare words are split into recognizable subword pieces; and the vocabulary stays manageable (typically 30,000-200,000 entries). The tradeoff is that the model's "view" of text is neither character-level nor word-level, causing surprising behaviors: "9.11 > 9.9" may confuse the model because "9", ".", "11" and "9", ".", "9" are processed as separate tokens with no inherent numeric magnitude.

---

## Model 1: BPE Step by Step

We will run BPE from scratch on a tiny corpus. BPE starts with individual characters (plus a special end-of-word marker `</w>`) and repeatedly merges the most frequent adjacent pair until the vocabulary reaches the desired size.

**Toy corpus** (each word shown with frequency):

| Word | Frequency |
|------|-----------|
| low | 5 |
| lower | 2 |
| newest | 6 |
| widest | 3 |

**Initial character vocabulary:** { l, o, w, e, r, n, s, t, i, d, `</w>` }

**Initial token sequences** (each character is a separate token, `</w>` marks end of word):

```
l o w </w>          × 5
l o w e r </w>      × 2
n e w e s t </w>    × 6
w i d e s t </w>    × 3
```

**BPE Iteration 1:** Count all adjacent pairs across all occurrences:
- `e s` appears in "newest" (×6) + "widest" (×3) = 9 times, most frequent
- Merge `e s` -> `es`. New sequences:

```
l o w </w>          × 5
l o w e r </w>      × 2
n e w es t </w>     × 6
w i d es t </w>     × 3
```

**BPE Iteration 2:** Count again:
- `es t` appears in "newest" (×6) + "widest" (×3) = 9 times, most frequent
- Merge `es t` -> `est`. New sequences:

```
l o w </w>          × 5
l o w e r </w>      × 2
n e w est </w>      × 6
w i d est </w>      × 3
```

**BPE Iteration 3:** Count again:
- `l o` appears in "low" (×5) + "lower" (×2) = 7 times, most frequent
- Merge `l o` -> `lo`. Continue until vocabulary reaches target size.

### Critical Thinking Questions

**Q1.** After Iteration 3, what is the token sequence for "lowest" if it appears in the corpus? Using the merged pairs computed above, apply them in order: first check if `es` can be merged, then `est`, then `lo`. Show the full merge sequence step by step.

> *Hint: Start with `l o w e s t </w>`. Check: is `e s` a merged pair? Yes, merge to get `l o w es t </w>`. Is `es t` a merged pair? Yes, merge to get `l o w est </w>`. Is `l o` a merged pair? Yes, merge to get `lo w est </w>`. Final sequence: `lo`, `w`, `est`, `</w>`, four tokens.*

**Q2.** The word "Collegeville" does not appear in the training corpus. Walk through how BPE would tokenize it using only the character vocabulary defined above plus any merges computed so far. What happens to characters like capital "C" that were never in the training vocabulary at all?

> *Hint: BPE tokenizers handle unseen characters by falling back to byte-level representations: every byte (0x00 through 0xFF) is in the vocabulary, so any Unicode character can be encoded as one or more byte tokens. For "C", the tokenizer would likely emit the byte for the ASCII code 67. What does this mean for the model's ability to reason about proper nouns?*

**Q3.** A vocabulary size of 32,000 is common for English-only models; multilingual models often use 250,000 or more. Explain the two competing pressures that determine the "right" vocabulary size, and predict what happens to non-English languages when a large model trained primarily on English uses a 32,000-token vocabulary built from English text.

> *Hint: Pressure 1 toward larger vocabulary: more tokens means each token corresponds to a longer, more meaningful text unit, reducing sequence length and the model's memory burden for long-range dependencies. Pressure 2 toward smaller vocabulary: each vocabulary entry requires a row in the embedding table; a larger vocabulary means more parameters and more training data needed per entry to learn a good representation. For non-English: if your 32,000-token vocabulary was built from English BPE merges, a Korean or Arabic sentence of 10 characters might require 30+ tokens because no Korean merges were learned.*

**Q4.** A student claims: "The tokenizer is just a preprocessing step; once the model is trained, tokenization doesn't affect model behavior, only input format." Identify two concrete model behaviors that are directly caused by tokenization choices, not by the model architecture or training data.

> *Hint: Think about (1) the model's ability to count letters in a word: if "strawberry" is tokenized as `straw` + `berry`, the model never sees the individual letters, making "how many r's are in strawberry?" hard to answer by inspection. (2) Think about arithmetic: "123456789" might be tokenized as "123" + "456" + "789" (three tokens), so adding two large numbers requires the model to reason across token boundaries in a non-obvious way.*

**Which of the following correctly describes what BPE merges at each step?**

[( )] The two tokens that appear most often anywhere in the vocabulary, regardless of position
[( )] The longest repeated substring in the training corpus
[(X)] The most frequently occurring adjacent pair of tokens in the current tokenized corpus, merging them into a single new token
[( )] The pair of tokens with the smallest combined length in characters

---

# Part II: Pre-Training Objectives and Scaling

In this part, you will understand the two dominant pre-training objectives for large language models, causal language modeling (GPT-style) and masked language modeling (BERT-style), implement the CLM cross-entropy loss by hand in code, and learn how Chinchilla scaling laws and quantization shape real decisions about which models to train and how to deploy them.

## 2. What the Model is Trained to Do

**Why this matters:** The pre-training objective determines what the model is good at by default. CLM models (GPT, LLaMA, Claude's base) are trained to generate (to complete text forward in time) which makes them naturally suited to dialogue, code generation, and open-ended text tasks. MLM models (BERT, RoBERTa) are trained to fill gaps (to predict masked content from bidirectional context) which makes them suited to classification, named entity recognition, and sentence-level understanding tasks where the full sentence is known at inference time. Choosing the wrong model family for a task is one of the most common architecture mistakes in applied AI projects.

**Causal Language Modeling (CLM)** trains the model to predict the next token given all previous tokens. For a sequence of tokens $x_1, x_2, \ldots, x_T$, the training loss is:

$$\mathcal{L}_{\text{CLM}} = -\frac{1}{T} \sum_{t=1}^{T} \log P(x_t \mid x_1, x_2, \ldots, x_{t-1})$$

This is a sum of cross-entropy losses at each position: how surprised was the model by the actual next token, given everything before it? Lower loss = the model was less surprised = it assigned higher probability to the correct token.

A key property of CLM: each token can only "see" tokens before it (this is enforced by a **causal attention mask** in the transformer). This is why CLM is well-suited to generation: at inference time, the model generates one token at a time, left to right, exactly as it was trained.

**Masked Language Modeling (MLM)** randomly masks a fraction (typically 15%) of input tokens and trains the model to reconstruct them from the surrounding context in *both* directions. Because MLM uses bidirectional context, MLM models (like BERT) cannot straightforwardly generate text; they see the whole sequence during training, so at inference time they cannot generate one token at a time without seeing future tokens they are supposed to generate.

MLM models excel at tasks where the full input is known: classifying whether an email is spam (the full email is available), finding the named entities in a sentence (the full sentence is available), or scoring a sentence's grammatical acceptability.

---

## Model 2: Cross-Entropy Loss by Hand

Given the four-character sequence "abbc" tokenized at the character level (tokens: `a`, `b`, `b`, `c`), and the following (toy) model probabilities:

| Position | Previous context | True next token | $P(\text{true token})$ | $-\log P$ |
|----------|-----------------|-----------------|------------------------|-----------|
| $t=1$ | (start) | a | 0.5 | 0.693 |
| $t=2$ | a | b | 0.6 | 0.511 |
| $t=3$ | a, b | b | 0.4 | 0.916 |
| $t=4$ | a, b, b | c | 0.7 | 0.357 |

### Critical Thinking Questions

**Q5.** Compute the average cross-entropy loss for this sequence by summing the $-\log P$ column and dividing by 4. Show your arithmetic. Then compute the **perplexity** as $e^{\mathcal{L}}$ where $\mathcal{L}$ is the average loss. What does this perplexity value mean intuitively: how many equally likely choices is the model effectively considering at each step?

> *Hint: Sum the four values in the $-\log P$ column: $0.693 + 0.511 + 0.916 + 0.357 = 2.477$. Divide by 4: $\mathcal{L} = 0.619$. Perplexity = $e^{0.619} \approx 1.86$. Intuitively: at each step, the model is as uncertain as if choosing uniformly among 1.86 equally likely options. For a model with random chance over 256 characters, perplexity would be 256. Lower = better.*

**Q6.** At position $t=3$, the model assigned only $P=0.4$ to the true next token `b`, even though `b` appeared immediately before. What does this suggest about the model's ability to use recent context? Name one architectural feature of transformers that would help the model assign higher probability to repeating recent tokens.

> *Hint: A high-quality language model should recognize that "bb" is a frequent pattern in some vocabularies and that the second `b` should be predicted with high probability given the first `b` just appeared. The attention mechanism in a transformer allows the model to directly attend to the previous `b` token. What happens to this ability if the context window is very short? What about if the model has only seen `b` rarely during pre-training?*

**Q7.** Compare CLM and MLM training objectives: which one can be used to generate new text, and why can the other one not? Use the mechanics of the attention mask to explain your answer, not just "CLM is generative."

> *Hint: CLM uses a causal attention mask: position $t$ can only attend to positions $\leq t$. At inference time, you have positions 1 through $t-1$ and want to predict position $t$; the mask exactly matches this setup, so CLM can generate autoregressively. MLM has no causal mask: position $t$ attends to all positions including $t+1, t+2, ..., T$. At inference time, if you want to generate position $t$, you do not yet have positions $t+1$ through $T$; the MLM training setup assumed you did.*

---

## 3. Cross-Entropy Loss in Code

**Why this matters:** The cross-entropy loss function is the engine of pre-training; it is the single number that gradient descent minimizes across trillions of tokens, and every capability an LLM develops is a side effect of minimizing this loss. Implementing it from scratch on a small character-level corpus makes the training loop demystified: there is no magic, only a repeated computation of "how surprised was the model by the actual next token, and which direction should we nudge the weights to be less surprised?"

The code below implements a character-level tokenizer and computes the CLM cross-entropy loss manually: no neural network, just the loss function itself applied to random "model probabilities" to illustrate the mechanics.

## Code Cell

```python
# Character-level CLM cross-entropy loss, manual implementation
# This shows exactly what a language model's training objective computes
# No neural network needed: we use random "model probabilities" to illustrate

import math
import random

random.seed(42)

# -----------------------------------------------------------------------
# Step 1: Build a character-level vocabulary from a small corpus
# -----------------------------------------------------------------------
corpus = "the cat sat on the mat the cat napped"
chars = sorted(set(corpus))
vocab = {ch: i for i, ch in enumerate(chars)}
vocab_size = len(vocab)
id_to_char = {i: ch for ch, i in vocab.items()}

print(f"Corpus: '{corpus}'")
print(f"Vocabulary ({vocab_size} characters): {chars}\n")

# -----------------------------------------------------------------------
# Step 2: Tokenize the corpus into a sequence of integer token IDs
# -----------------------------------------------------------------------
tokens = [vocab[ch] for ch in corpus]
print(f"Token sequence (first 20): {tokens[:20]}")
print(f"Decoded: {''.join(id_to_char[t] for t in tokens[:20])}\n")

# -----------------------------------------------------------------------
# Step 3: Compute CLM cross-entropy loss manually
# For each position t, we need P(true_token | context).
# Instead of a real model, we simulate two "models":
#   - random_model: assigns uniform probability to all vocab entries
#   - better_model: assigns higher probability to more frequent tokens
# -----------------------------------------------------------------------

# Compute token frequencies for the "better model"
from collections import Counter
freq = Counter(tokens)
total = sum(freq.values())
better_probs = {tok: (freq[tok] / total) for tok in range(vocab_size)}
# Uniform probabilities for the random model
uniform_prob = 1.0 / vocab_size

def clm_loss(token_sequence, model_type="uniform"):
    """Compute average cross-entropy loss for a token sequence under CLM."""
    total_loss = 0.0
    n = 0
    for t in range(1, len(token_sequence)):  # start at t=1 (first "next token")
        true_token = token_sequence[t]
        if model_type == "uniform":
            p = uniform_prob
        elif model_type == "frequency":
            p = better_probs[true_token]
        else:
            raise ValueError("Unknown model type")
        # Cross-entropy for this position: -log(P(true_token))
        loss_t = -math.log(p + 1e-10)  # add small epsilon to avoid log(0)
        total_loss += loss_t
        n += 1
    avg_loss = total_loss / n
    perplexity = math.exp(avg_loss)
    return avg_loss, perplexity

loss_uniform, ppl_uniform = clm_loss(tokens, model_type="uniform")
loss_freq,    ppl_freq    = clm_loss(tokens, model_type="frequency")

print("=== CLM Cross-Entropy Loss Comparison ===\n")
print(f"Uniform model (random guessing among {vocab_size} chars):")
print(f"  Average loss: {loss_uniform:.4f}   Perplexity: {ppl_uniform:.2f}")
print()
print(f"Frequency model (always assigns P = token_frequency):")
print(f"  Average loss: {loss_freq:.4f}   Perplexity: {ppl_freq:.2f}")
print()
print(f"Theoretical minimum loss for uniform model: log({vocab_size}) = {math.log(vocab_size):.4f}")
print()

# -----------------------------------------------------------------------
# Step 4: Show a few positions in detail
# -----------------------------------------------------------------------
print("=== Per-position loss (first 10 positions, frequency model) ===\n")
print(f"{'t':>4}  {'Context (last 5 chars)':25}  {'True next':>10}  {'P(true)':>8}  {'-log P':>8}")
print("-" * 65)
context_len = 5
for t in range(1, min(11, len(tokens))):
    ctx_tokens = tokens[max(0, t - context_len):t]
    ctx_str = ''.join(id_to_char[tok] for tok in ctx_tokens)
    true_tok = tokens[t]
    true_char = id_to_char[true_tok]
    p = better_probs[true_tok]
    loss_t = -math.log(p + 1e-10)
    print(f"{t:>4}  {repr(ctx_str):25}  {repr(true_char):>10}  {p:>8.4f}  {loss_t:>8.4f}")

print()
print("=== STUDENT EXERCISES ===")
print("1. The frequency model does NOT use the context — it just uses global token frequency.")
print("   A real LM would use context. How would 'the' in 'on the' vs 'sat the' differ?")
print()
print("2. Modify the corpus string above and re-run. How does a repeated pattern")
print("   (e.g., 'the cat the cat the cat') change the perplexity?")
print()
print("3. Compute the perplexity of a PERFECT model that assigns P=1.0 to every")
print("   correct token. What is -log(1.0)? What is e^0? What does perfect perplexity look like?")
```

---

## Model 3: Understanding the Training Signal

### Critical Thinking Questions

**Q8.** In the code output, the "frequency model" achieves lower loss than the "uniform model" even though neither model uses the actual preceding context. What does this tell you about what a language model learns in the very early stages of pre-training — before it has learned any syntax or semantics — just from the token frequency distribution?

> *Hint: The frequency model is essentially learning "some characters appear more often than others" — the unigram distribution of the language. This alone gives lower perplexity than random. Real language models progress through stages: first they learn unigram frequencies (the most common characters/words), then bigram patterns (common two-token sequences), then longer-range dependencies (grammar, facts, reasoning). Each stage corresponds to a reduction in training loss.*

**Q9.** A student runs the code on a corpus consisting entirely of the repeated string "ababababab". Predict (without running it): what perplexity does the frequency model achieve on this corpus, and what perplexity would a perfect context-aware model achieve? What is the ratio?

> *Hint: In "ababab...", the tokens `a` and `b` each have frequency 0.5. The frequency model assigns P=0.5 to every token, giving loss = -log(0.5) ≈ 0.693 and perplexity ≈ 2.0 (as if choosing between 2 equal options). A perfect context-aware model knows "after `a` comes `b` and after `b` comes `a`" with certainty, so it assigns P=1.0 to every token, giving loss = 0 and perplexity = 1. What does this ratio (2.0 vs 1.0) tell you about how much information is in the local context that the frequency model is ignoring?*

**Q10.** The training loss computed by the code is an average over all positions in the sequence. During actual LLM pre-training on trillions of tokens, the gradient of this loss with respect to model weights is computed and used to update the weights. What would you expect to observe if you plotted training loss vs. training step for a real LLM? Specifically, where does the loss decrease fastest, where does it plateau, and what does "overfitting" look like for a model trained on a fixed dataset?

> *Hint: Loss decreases rapidly at first as the model learns basic patterns (token frequencies, common bigrams), then more slowly as it learns grammar and common phrases, then very slowly as it learns rare facts and precise reasoning. Overfitting looks like: training loss continues decreasing while validation loss (on held-out text) stops decreasing or increases. For LLMs trained on datasets of hundreds of billions of tokens, overfitting is rare — the model never sees each example more than once.*

**Which of the following is the pre-training objective used by GPT-style (autoregressive) language models like GPT-4 and LLaMA?**

[( )] Masked Language Modeling — randomly masking 15% of tokens and predicting them from bidirectional context
[( )] Sequence-to-sequence with encoder-decoder attention — mapping an input sentence to an output sentence
[(X)] Causal Language Modeling — predicting the next token given all previous tokens, with a causal attention mask preventing access to future positions
[( )] Contrastive learning — training the model to assign similar embeddings to semantically related text pairs

---

## 4. Chinchilla Scaling Laws and Quantization

**Why this matters:** The decision of how large a model to train and how much data to train it on is one of the most consequential engineering decisions in LLM development — it determines cost, capability, and deployment requirements. Chinchilla scaling laws give a principled answer to "how much data per parameter?" And quantization determines whether the resulting model can run on your hardware at all. Both topics directly affect practical choices you will make when selecting or deploying models for course projects.

**Chinchilla Scaling Laws.** In 2022, DeepMind published a landmark study (Hoffmann et al., "Training Compute-Optimal Large Language Models") that found previous large models (including GPT-3) were significantly *undertrained*. The study varied model size and training data volume while holding total compute constant, and found that model performance depends roughly equally on model size $N$ (parameters) and training data $D$ (tokens):

$$N_{\text{optimal}} \approx \frac{C}{2 \cdot 20}$$, $$D_{\text{optimal}} \approx 20 \cdot N$$

where $C$ is the total compute budget. The rule of thumb: **train on approximately 20 tokens of data per model parameter**. A model with 7 billion parameters is "Chinchilla optimal" when trained on roughly 140 billion tokens. GPT-3 (175B parameters) was trained on ~300B tokens — far fewer than the Chinchilla-optimal ~3.5 trillion tokens.

The practical implication: many modern open-source models (LLaMA-2, Mistral, Gemma) are trained on 2-6 trillion tokens despite having only 7B-13B parameters — they are intentionally "overtrained" relative to the original Chinchilla formulas, because smaller well-trained models are cheaper to deploy even if training is more expensive.

**Quantization.** Full-precision models store each weight as a 32-bit floating-point number (float32). Running a 70B-parameter model in float32 requires 70B × 4 bytes = 280 GB of GPU memory — far beyond any single consumer GPU (which typically has 8-24 GB). Quantization maps float32 values to lower-precision integers:

- **float16 / bfloat16** (16 bits): halves memory; negligible accuracy loss; widely supported
- **int8** (8 bits): quarters memory; small accuracy loss on most tasks; requires calibration
- **int4** (4 bits): reduces memory by 8×; more accuracy loss, especially for smaller models; enables running 7B models on laptops

The intuition: float32 can represent values between roughly $-3.4 \times 10^{38}$ and $3.4 \times 10^{38}$ with fine precision. int8 maps this range to just 256 discrete values. For LLM weights, most weight values cluster near zero and vary smoothly — the "rounding" from float32 to int8 or int4 loses precision but usually preserves the relative ordering of weights that matters for model output. The exception: very small models and outlier weights (which exist in larger models) are more sensitive to quantization.

---

## Model 4: Scaling and Quantization Decision Table

| Situation | Model Parameters | Training Tokens | Chinchilla Verdict | Deployment Format | Reason |
|-----------|-----------------|-----------------|--------------------|--------------------|--------|
| Pre-2022 LLMs (GPT-3) | 175B | 300B | Severely undertrained (optimal: ~3.5T tokens) | float16, multi-GPU | Large N, not enough D |
| LLaMA-3 8B | 8B | 15T | Overtrained for inference efficiency (optimal: ~160B tokens) | int4, single GPU | Small N, massive D — great for deployment |
| BERT-base | 110M | 16B | Well-trained for era | float32, CPU feasible | Smaller model, lower data era |
| Chinchilla (original) | 70B | 1.4T | Exactly optimal | float16, multi-GPU | Reference point for scaling law |

### Critical Thinking Questions

**Q11.** A research team has a compute budget equivalent to training a 10B-parameter model on 500B tokens. Using the Chinchilla rule of thumb ($D_{\text{optimal}} = 20 \times N$), is this training run compute-optimal? If not, what should they change — reduce model size to fit more training, or increase model size and train on fewer tokens?

> *Hint: Chinchilla optimal for 10B parameters requires 10B × 20 = 200B tokens. The team plans to use 500B tokens — they are training on 2.5× more tokens than Chinchilla optimal for this model size. The model is being "overtrained" for Chinchilla optimality, but as the LLaMA example shows, this is often intentional to get a smaller, faster inference model. Alternatively: what size model would be Chinchilla optimal for 500B tokens? $N = 500B / 20 = 25B$ parameters. So a 25B model trained on 500B tokens would be compute-optimal.*

**Q12.** A student wants to run a 13B-parameter model locally on a laptop with 16 GB of unified memory. Calculate the memory required in float32, float16, and int4. Which format(s) fit in 16 GB? State any approximation you use.

> *Hint: Memory = parameters × bytes per parameter. float32: 13B × 4 bytes = 52 GB. float16: 13B × 2 bytes = 26 GB. int4: 13B × 0.5 bytes = 6.5 GB. Only int4 fits in 16 GB. (Note: this calculation is for weights only; actual inference also requires memory for activations and KV cache, but weights dominate for typical prompt lengths.)*

**Q13.** Why do larger models tend to be *more* robust to quantization than smaller models? Hint: consider what happens to the relative importance of any single weight when there are 70B weights versus 7B weights.

> *Hint: In a 70B-parameter model, each individual weight has a smaller fractional influence on the output — the computation is distributed across many more parameters. Rounding a weight from its float32 value to the nearest int4 value introduces absolute error of at most $\approx \Delta/2$ where $\Delta$ is the quantization step size, but the relative effect on the output scales with $1/N$. Additionally, redundancy in large models means the network can "compensate" for rounding errors in some weights using other weights. Tiny models (1B-3B) have less redundancy and are more sensitive to quantization-induced errors.*

---

# Part III: Synthesis — Connecting Tokenization, Pre-Training, and Scaling to Course Concepts

In this part, you will apply the technical concepts from Parts I and II to concrete decisions you will face when building AI applications: how tokenization affects RAG chunk sizing, how scaling laws inform the choice between hosted and local models, and how quantization changes the accessibility of LLMs across hardware tiers. These connections bridge the "how LLMs are built" material to the "how to use them wisely" practice that runs throughout this course.

## 5. Exercises

**1. Tokenization, Chunk Size, and RAG Quality**

*What to do:* In RAG (Retrieval-Augmented Generation), a document is split into chunks, each chunk is embedded, and the most relevant chunks are retrieved for each query. Tokenization directly affects optimal chunk size and retrieval quality. Your task: (a) using the rule of thumb that 1 token ≈ 4 characters ≈ 0.75 words, estimate the token count for a chunk of 512 characters. (b) A RAG system is configured with a chunk size of 512 characters. Describe one failure mode caused by splitting on character count (rather than token count or sentence boundaries). (c) Explain how tokenizer behavior for a non-English language (e.g., Chinese characters, which have no spaces) affects the choice of chunk size for a multilingual RAG system. (d) Propose a chunking strategy that is robust to these issues.

*Starter hint:* For (a): 512 characters / 4 characters per token ≈ 128 tokens per chunk. For (b): splitting at exactly 512 characters might split a sentence in the middle of a word, producing a broken token at the chunk boundary that gets a different embedding than it would have in complete context. For (c): Chinese text has no spaces, so character count is a poor proxy for semantic content — a 512-character Chinese chunk might contain 512 complete words, while a 512-character English chunk contains ~85 words. For (d): consider splitting on sentence boundaries detected by a tokenizer-aware splitter, with a maximum token count rather than character count.

*You've succeeded when:* Your answer gives a numerical token estimate for (a), identifies a specific downstream effect on retrieval quality for (b), explains the specific mechanism by which non-English tokenization differs for (c), and proposes a chunking strategy for (d) that names a specific splitting strategy (not just "split better") and explains which tokenization failure mode it addresses.

**2. Scaling Laws and the Hosted vs. Local Model Decision**

*What to do:* You are advising a small nonprofit that wants to deploy an AI assistant to help with grant writing. They have a budget of $200/month for API costs and one developer with a laptop (16 GB RAM). Using Chinchilla scaling intuition and quantization knowledge from this activity, walk through the following: (a) what does the Chinchilla result imply about the relative capability of a 7B model trained on 2T tokens versus a 70B model trained on 200B tokens — which should perform better on general tasks? (b) if the hosted API option is GPT-4o-mini at $0.15/million input tokens and the local option is a Llama-3-8B model in int4, estimate how many grant-writing queries (average 2,000 input tokens) they can afford per month via API vs. local (unlimited, but constrained by laptop RAM and speed). (c) which option do you recommend and why — what factors beyond raw cost matter for their use case?

*Starter hint:* For (a): Chinchilla says the 7B model trained on 2T tokens (= 285 tokens per parameter) is much better-trained than the 70B model on 200B tokens (= 2.9 tokens per parameter, massively undertrained). For (b): $200 at $0.15/M tokens = 1.33 billion input tokens / 2,000 tokens per query ≈ 665,000 queries — far more than a small nonprofit needs. The local 8B int4 model requires 4 GB, fits in 16 GB RAM, but runs at perhaps 10-30 tokens/second on a laptop CPU — viable for a low-throughput use case. For (c): consider data privacy (grant data may be confidential), reliability (API has uptime guarantees; local requires maintenance), and latency.

*You've succeeded when:* Your answer includes a correct Chinchilla-based capability comparison for (a), specific numerical estimates with arithmetic shown for (b), and a recommendation for (c) that addresses at least three factors (cost, privacy, reliability, latency, or capability).

**3. Quantization, Accessibility, and AI Equity**

*What to do:* The ability to run LLMs locally depends on hardware — specifically GPU memory and CPU speed. Quantization has dramatically lowered the hardware requirements for running frontier-adjacent models. Analyze the following: (a) a 7B model in float32 requires ~28 GB of VRAM; the same model in int4 requires ~4 GB. What percentage of consumer laptops sold in the past two years can run the float32 version? The int4 version? (Research or estimate based on typical integrated graphics memory.) (b) a researcher in a country with unreliable internet and no access to cloud GPU credits needs to use an LLM for medical literature summarization. What deployment strategy (model size, quantization, pre-training data) would you recommend, and why does the tokenizer choice matter for this use case? (c) a company argues that releasing only quantized open-source models (not float32 weights) is good because it lowers the barrier to use. A critic argues it is bad because it limits what researchers can do with the weights. Adjudicate this debate by identifying one specific research or application capability that requires float32 weights and one that int4 fully enables.

*Starter hint:* For (a): most consumer laptops with integrated graphics have 0 GB of dedicated VRAM — they use shared system RAM. A MacBook Pro M3 has 16-96 GB of unified memory that can be used for models; a Windows laptop with a dedicated GPU typically has 4-8 GB VRAM, plus system RAM for CPU inference. For (b): consider models with strong multilingual coverage trained on diverse data (e.g., a model with a 250K-vocabulary multilingual tokenizer), and int4 quantization for local inference. For (c): float32 is needed for fine-tuning (gradients need full precision); int4 is sufficient for inference on standard tasks.

*You've succeeded when:* Your answer gives a specific (even if estimated) percentage for (a) with a stated assumption about typical hardware, recommends a specific model family or tokenizer property for (b) rather than a generic "multilingual model," and identifies a concrete research capability for the float32 case and a concrete application for the int4 case in (c).

---

## Reflection Prompt

**Personal:** Think about a text you have written in a language other than English, or a domain with unusual vocabulary (chemistry, legal language, music notation, code). Based on what you now know about BPE and vocabulary building from web text, predict how a standard English-trained LLM would likely tokenize a sentence from that domain. Would the tokenization be efficient (few tokens per word) or inefficient (many tokens per word)? What does this predict about that LLM's performance on tasks in that domain?

**Technical:** The cross-entropy loss function treats every token position equally — predicting "the" correctly at position 47 earns the same reward as predicting a rare technical term correctly at position 48. Some researchers argue that LLMs should be trained with higher loss weights on informative tokens (named entities, numbers, domain terms) and lower weights on common function words. In your notebook: design a simple re-weighting scheme — how would you decide which tokens are "more important," and what training challenges would your scheme introduce?

**Societal:** The Chinchilla scaling laws imply that models trained on more data are more capable. Most of that data comes from the internet — disproportionately English, disproportionately from wealthy countries, and disproportionately from text-producing activities (social media, news, academia) rather than from oral traditions, local languages, or under-resourced communities. Who benefits most from the capabilities unlocked by Chinchilla-scale training, and who is most likely to receive worse model performance due to being underrepresented in the training corpus? What would a training data collection strategy that took equity seriously look like?

---

## -> Coming Up Next

In the next activity we look inside the transformer itself — how the attention mechanism learns to route information between tokens, why deeper models learn different things than shallower ones, and how the architecture choices made during pre-training shape which capabilities emerge and which remain out of reach.

---

## 6. Further Reading

- Sennrich, Haddow, and Birch. "Neural Machine Translation of Rare Words with Subword Units." *ACL* (2016). The original BPE tokenization paper.
- Hoffmann et al. "Training Compute-Optimal Large Language Models." DeepMind (2022). The Chinchilla scaling laws paper.
- Dettmers et al. "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale." *NeurIPS* (2022). The foundational int8 quantization paper for LLMs.
- Radford et al. "Language Models are Unsupervised Multitask Learners." OpenAI (2019). The GPT-2 paper, which clearly describes the CLM pre-training objective.
- Devlin et al. "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." *NAACL* (2019). The MLM pre-training paper.

> **Sources:** This activity draws on material from *AI Engineering from Scratch*, Phase 10 (LLMs from Scratch), supplemented by the primary papers listed above.
