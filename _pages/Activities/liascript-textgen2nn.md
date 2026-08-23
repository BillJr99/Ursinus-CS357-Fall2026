<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-textgen2nn.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-textgen2nn.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# From Text Generation to a Neural Network

You have sampled from a softmax, tuned temperature, and measured cosine similarity between embeddings, but so far the "model" between the prompt and the logits has been a mysterious box. Today we open that box. We move from **the generation loop as a pipeline $\rightarrow$ a neural network you can compute entirely by hand $\rightarrow$ visualizing what the numbers inside are doing $\rightarrow$ the bridge: an embedding IS a learned representation**.

**Purpose (why we are doing this):** Every agent you build this semester rides on a forward pass: numbers multiplied by weights, summed, squashed, repeated. If you can trace one forward pass by hand, then "the model computed logits" stops being magic words and becomes arithmetic you can audit, debug, and question. **Task:** trace one short prompt through every stage of the generation loop with real (tiny) numbers, then compute a complete 2-2-1 neural network forward pass by hand and verify it in code. **Criteria for success:** your trace table matches the Python verification to two decimal places, and you can state in one sentence where the neural network lives inside the generation loop.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Generation Loop** | The repeating cycle a language model runs: tokenize the text so far, compute a probability distribution for the next token, sample one token, append it, and repeat until a stop token. | Tracing the prompt "The sky is" through every stage to produce the word "blue" |
| **Logit** | A raw, unbounded score the network assigns to each vocabulary token before softmax converts scores to probabilities. | Logits (4.0, 2.5, 1.0, 0.5, -1.0) for the five candidate words in Model 1 |
| **Weight** | A learned number inside the network that multiplies an input. The network's entire "knowledge" is stored in its weights, which are fixed at generation time. | $w_{11} = 0.5$ in the tiny network of Model 2 |
| **Bias (neuron bias)** | A learned number added after the weighted sum, shifting a neuron's activation threshold. (Distinct from data bias, which we study in the bias unit.) | $b_1 = -0.5$ in the hidden layer of Model 2 |
| **ReLU** | The Rectified Linear Unit activation function: $\text{ReLU}(z) = \max(0, z)$. It passes positive values through unchanged and clips negatives to zero, giving the network its non-linearity. | Hidden neuron $h_2$ computes a pre-activation of $-0.5$ and outputs $0$ |
| **Forward Pass** | One complete flow of numbers from inputs, through every layer's weights and activations, to outputs. Generation runs one forward pass per token generated. | The trace table in Model 2: inputs $(1.0, 2.0)$ flow to output $3.25$ |
| **Embedding** | A learned vector of numbers representing a token. It is literally the first layer of the network: a lookup table of weights, trained like every other weight. | Token id 464 mapped to the 4-number vector $(0.2, -1.1, 0.7, 0.3)$ |
| **Activation** | The output value of a neuron after its activation function, the "signal" that layer sends forward. Visualizing activations shows what the network responds to. | $h = (2.0, 0.0)$ in the trace table; the heatmaps in Model 3 |

Notice that each concept above appears in at least two forms today: in the Key Concepts table (words), in a diagram or trace table (pictures and numbers), and in runnable Python (code). If one representation does not click, use another; they all describe the same thing.

---

### Before You Start

**What you need:** Python 3.10+, or a notebook if you prefer. No prior neural-network background assumed.

**What you will have at the end:** a forward pass you traced by hand, connected to the code that does the same thing.

Work through the sections in order; each one builds on the last, and the code blocks are meant to be run as you reach them, not read past.

---

# Part I: The Generation Loop as a Pipeline

In this Part you will lay out every stage between typing a prompt and reading a response, as a pipeline diagram, and then push one short prompt through the whole pipeline with actual small numbers. By the end you will be able to point to exactly one box in the diagram and say "that is the neural network."

## 1. The Pipeline

**Why this matters:** In the sampling activity we studied the *last two* stages of generation (softmax and sampling) in isolation. But an agent's behavior (good, bad, or biased) is shaped by every stage. When you later debug an agent that tokenizes a course code strangely, or ask why two paraphrases retrieve the same document, you will be reasoning about specific stages of this pipeline.

Here is the entire loop, drawn as a pipeline. Read it top to bottom; the arrow at the bottom loops back to the top.

```
 prompt text            "The sky is"
      |
      v
 [ tokenizer ]          splits text into known word-pieces
      |
      v
 token ids              [464, 6766, 318]        (one integer per token)
      |
      v
 [ embedding lookup ]   each id indexes a row in a big learned table
      |
      v
 embedding vectors      464 -> ( 0.2, -1.1,  0.7,  0.3)
                        6766 -> ( 1.4,  0.5, -0.2,  0.9)
                        318 -> (-0.3,  0.8,  1.1, -0.6)
      |
      v
 [ transformer layers ] many layers of weighted sums + non-linearities;
      |                 each token's vector is updated using *attention*
      |                 to every other token's vector
      v
 contextual vector      ( 0.9,  0.4, -0.7,  1.2)   for the LAST position
      |
      v
 [ output layer ]       one weighted sum per vocabulary word
      |
      v
 logits                 blue: 4.0   clear: 2.5   night: 1.0
                        green: 0.5  the: -1.0
      |
      v
 [ softmax(T) ]         exponentiate scaled logits, normalize to sum to 1
      |
      v
 probabilities (T=1)    blue: 0.763  clear: 0.170  night: 0.038
                        green: 0.023 the: 0.005
      |
      v
 [ sample ]             roll the weighted die  -->  "blue"
      |
      v
 [ append ]             text is now "The sky is blue"
      |
      +--------------------> loop back to [ tokenizer ]
```

The numbers in this diagram are illustrative but real: you can check the softmax row yourself. At $T = 1$: $e^{4.0} \approx 54.598$, $e^{2.5} \approx 12.182$, $e^{1.0} \approx 2.718$, $e^{0.5} \approx 1.649$, $e^{-1.0} \approx 0.368$; the sum is $\approx 71.516$, and $54.598 / 71.516 \approx 0.763$, exactly the temperature math from the sampling activity, now placed in context as the *second-to-last* stage of a longer machine.

**So how does this become a neural net?** Look at the three middle boxes: **embedding lookup**, **transformer layers**, and **output layer**. Those three boxes *are* the neural network; everything else (tokenizer, softmax, sampling, appending) is ordinary deterministic code wrapped around it. The embedding table is a layer of learned weights. Each transformer layer is (at heart) weighted sums of its inputs passed through non-linear functions, the same recipe you will compute by hand in Part II, just with millions of neurons instead of two. The output layer is one more weighted sum per vocabulary word, producing the logits. A "large language model" is a very large stack of the small thing you are about to build, run once per generated token.

---

## Model 1: One Prompt, Every Stage

The table below traces the prompt "The sky is" through one full turn of the loop, with a toy 5-word candidate vocabulary and 4-number embeddings so that every value fits on paper.

| Stage | Input | Output | Who computes it? |
|-------|-------|--------|------------------|
| Tokenizer | "The sky is" | ids [464, 6766, 318] | deterministic code |
| Embedding lookup | id 318 | vector $(-0.3, 0.8, 1.1, -0.6)$ | the network (learned table) |
| Transformer layers | all three embedding vectors | contextual vector $(0.9, 0.4, -0.7, 1.2)$ | the network (learned weights) |
| Output layer | contextual vector | logits $(4.0, 2.5, 1.0, 0.5, -1.0)$ | the network (learned weights) |
| Softmax, $T=1$ | logits | probabilities $(0.763, 0.170, 0.038, 0.023, 0.005)$ | deterministic formula |
| Sample | probabilities | "blue" | random draw |
| Append | "The sky is" + "blue" | "The sky is blue" | deterministic code |

### Critical Thinking Questions

1. Exactly one stage in the table involves randomness. Name it, and list two stages that are *learned* (their behavior was set by training) but perfectly deterministic at generation time.

   > *Hint: "Learned" and "random" are different properties. The embedding table and transformer weights were shaped by training, but at generation time they are frozen numbers; the same input always produces the same logits. Which single stage rolls a die?*

2. Recompute the softmax row at $T = 0.5$ (calculator permitted): the scaled logits become $(8, 5, 2, 1, -2)$. Show that $P(\text{blue})$ rises to about $0.949$. Which *earlier* pipeline stage is completely unaffected by this change, and why does that matter for reproducibility?

   > *Hint: $e^{8} \approx 2980.958$, $e^{5} \approx 148.413$, $e^{2} \approx 7.389$, $e^{1} \approx 2.718$, $e^{-2} \approx 0.135$; the sum is $\approx 3139.614$. Temperature is applied after the logits are computed; do the weights, embeddings, or logits change when you change $T$?*

3. The loop appends "blue" and runs again. Explain, using the diagram, why the *entire network* must run again for the next token, and why generating a 200-token answer therefore costs roughly 200 forward passes. (The Recorder writes the group's one-sentence explanation.)

   > *Hint: The next-token distribution depends on the tokens so far. After appending "blue," the input to the tokenizer has changed, so every downstream stage receives different values. Nothing from the previous pass can simply be reused for the new final position (production systems cache parts of it, but a new forward pass still occurs).*

In the generation pipeline, the neural network proper consists of which stages?

[( )] Tokenizer, softmax, and sampling
[(X)] Embedding lookup, transformer layers, and output layer
[( )] Only the transformer layers
[( )] The whole pipeline, including the random sampling step

> **Common Misconception:** Students often believe the tokenizer is part of the neural network, or that it is learned by gradient descent along with the weights. It is not: the tokenizer is a fixed, deterministic program (built once, before training, from corpus statistics) that converts text to integers. If the tokenizer splits "CS357" into strange pieces, no amount of temperature tuning will fix it; the problem is upstream of the network entirely.

---

# Part II: A Forward Pass by Numbers

In this Part you will compute every number in a tiny neural network (two inputs, two hidden ReLU neurons, one output) entirely by hand, then verify your arithmetic in Python. This is the same computation as one slice of the transformer box in Part I, small enough to own completely.

## 2. The Tiny Network

**Why this matters:** "The model computed logits" is only meaningful if you know what computing means here: multiply inputs by weights, add a bias, apply a non-linearity, repeat per layer. Doing it by hand once (every multiplication visible) is the difference between believing this and knowing it. The extended by-hand practice for this skill (a full network fitting a quadratic, with more neurons and a backward pass) is on the printable worksheet: [Neural Network by Hand worksheet (PDF)](https://www.billmongan.com/Ursinus-CS357/files/activity-neuralnets/nn_by_hand_quadratic_full.pdf).

Here is the network, in both picture and formula form (two representations of one object; check each against the other):

```
  inputs        hidden layer (ReLU)         output (linear)

   x1 ---w11=0.5---> (h1)
     \              /  b1=-0.5  \
      w21=1.0      /             v1=1.5
       \          /               \
        \        /                 (y)  + c=0.25
        /\      /                 /
       /  \    /               v2=2.0
   x2 -w12=1.0                  /
     \                         /
      w22=-1.0 ----> (h2) ----
                    b2=+0.5
```

$$
h_1 = \text{ReLU}(0.5\,x_1 + 1.0\,x_2 - 0.5) \qquad
h_2 = \text{ReLU}(1.0\,x_1 - 1.0\,x_2 + 0.5)
$$

$$
y = 1.5\,h_1 + 2.0\,h_2 + 0.25
$$

---

## Model 2: The Trace Table

We push the input $\mathbf{x} = (1.0, 2.0)$ through the network. Every arithmetic step appears in the table; nothing is hidden.

| Step | Computation | Value |
|------|-------------|-------|
| $h_1$ pre-activation | $0.5(1.0) + 1.0(2.0) + (-0.5) = 0.5 + 2.0 - 0.5$ | $2.0$ |
| $h_1$ activation | $\text{ReLU}(2.0) = \max(0, 2.0)$ | $2.0$ |
| $h_2$ pre-activation | $1.0(1.0) + (-1.0)(2.0) + 0.5 = 1.0 - 2.0 + 0.5$ | $-0.5$ |
| $h_2$ activation | $\text{ReLU}(-0.5) = \max(0, -0.5)$ | $0.0$ |
| output | $1.5(2.0) + 2.0(0.0) + 0.25 = 3.0 + 0 + 0.25$ | $3.25$ |

So this network maps $(1.0, 2.0) \mapsto 3.25$. Notice that $h_2$ "died" for this input: its pre-activation was negative, so ReLU clipped it to zero and its outgoing weight $v_2 = 2.0$ contributed nothing.

### Critical Thinking Questions

4. Repeat the full trace by hand for $\mathbf{x} = (2.0, 1.0)$: same table format, all five rows. (You should get $y = 5.5$, with *both* hidden neurons active.) The Recorder writes the completed table.

   > *Hint: $h_1$ pre-activation is $0.5(2.0) + 1.0(1.0) - 0.5 = 1.5$; $h_2$ pre-activation is $1.0(2.0) - 1.0(1.0) + 0.5 = 1.5$. Both are positive, so ReLU passes both through. Then $y = 1.5(1.5) + 2.0(1.5) + 0.25$.*

5. Compare your two traces. The inputs $(1,2)$ and $(2,1)$ contain the same two numbers, yet the outputs differ ($3.25$ vs $5.5$) and *different neurons are active*. What does this tell you about how a ReLU network processes its input; is it applying one fixed formula, or switching between formulas?

   > *Hint: When $h_2$ is clipped to zero, the network's output formula is effectively $y = 1.5 h_1 + 0.25$; when both neurons are active, it is a different linear formula. ReLU networks are piecewise linear: the pattern of which neurons are on/off selects which linear piece applies. More neurons means more pieces means more expressive functions.*

6. Trace $\mathbf{x} = (0.0, 0.0)$. Even with all-zero inputs, the output is not zero. Which parameters are responsible, and what would the network lose if all biases were removed?

   > *Hint: With zero inputs, all weight terms vanish, leaving only biases: $h_1 = \text{ReLU}(-0.5) = 0$, $h_2 = \text{ReLU}(0.5) = 0.5$, $y = 2.0(0.5) + 0.25 = 1.25$. Without biases, every neuron's decision boundary would be forced through the origin; could the network then represent a function like $y = x_1 + 5$?*

In the trace for $\mathbf{x} = (1.0, 2.0)$, hidden neuron $h_2$ output $0.0$ because:

[( )] Its incoming weights were zero
[( )] The input $x_2$ was too large for the network to represent
[(X)] Its pre-activation ($-0.5$) was negative and ReLU clips negative values to zero
[( )] The output weight $v_2$ was too small

---

## Code Cell: Verify Your Hand Trace

The code below implements the exact network above using plain Python lists (no libraries needed), prints every intermediate value in trace-table order, and checks the three inputs from the Model and questions. Your hand values and the printed values must match to two decimal places.

```python
W1 = [[0.5, 1.0],    # weights into h1
      [1.0, -1.0]]   # weights into h2
b1 = [-0.5, 0.5]
V  = [1.5, 2.0]      # weights into output
c  = 0.25

def relu(z):
    return max(0.0, z)

def forward(x, verbose=True):
    pre = [W1[j][0]*x[0] + W1[j][1]*x[1] + b1[j] for j in range(2)]
    h   = [relu(p) for p in pre]
    y   = V[0]*h[0] + V[1]*h[1] + c
    if verbose:
        print(f"x = {x}")
        for j in range(2):
            print(f"  h{j+1}: pre = {W1[j][0]}*{x[0]} + {W1[j][1]}*{x[1]} + {b1[j]} = {pre[j]:+.2f}"
                  f"  -> ReLU -> {h[j]:.2f}")
        print(f"  y  = {V[0]}*{h[0]:.2f} + {V[1]}*{h[1]:.2f} + {c} = {y:.2f}\n")
    return y

for x in [(1.0, 2.0), (2.0, 1.0), (0.0, 0.0)]:
    forward(list(x))
```

If any line disagrees with your hand trace, find the first row where they diverge; that row contains the arithmetic slip. This is exactly how you will debug real models later: compare expected and actual values layer by layer, top to bottom.

For extended by-hand practice (a wider network approximating $y = x^2$, including the training (backward) pass) work through the printable worksheet: [nn_by_hand_quadratic_full.pdf](https://www.billmongan.com/Ursinus-CS357/files/activity-neuralnets/nn_by_hand_quadratic_full.pdf).

---

# Part III: Seeing Inside the Network

In this Part you will visualize the tiny network's weights and activations as heatmaps, the same technique, scaled up, that researchers use to inspect real language models. A picture of a weight matrix is a second representation of the same numbers you multiplied by hand in Part II.

## 3. What a Neural-Network Visualizer Shows

**Why this matters:** A network's weights are just a grid of numbers, and a grid of numbers is an image waiting to happen. Neural-network visualizers (in the spirit of tools like TensorFlow Playground or the "nviz"-style activation viewers) show three things: (1) the **weights**, which inputs each neuron amplifies (bright) or suppresses (dark/negative); (2) the **activations**, which neurons actually fire for a given input; and (3) how activations *change* as the input changes, revealing which features of the input each neuron has learned to detect. For our 2-2-1 network the pictures are small enough to check against your hand trace; for a real model the same pictures have millions of cells, but the reading skill is identical.

## Model 3: Weight and Activation Heatmaps

The code below draws three heatmaps: the hidden-layer weight matrix $W_1$ (rows = hidden neurons, columns = inputs), the output weights $V$, and the hidden activations for the two inputs you traced by hand. Compare each cell to a number you already computed.

## Code Cell

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

W1 = [[0.5, 1.0], [1.0, -1.0]]
b1 = [-0.5, 0.5]
V  = [[1.5, 2.0]]

def relu(z): return max(0.0, z)
def hidden(x):
    return [relu(W1[j][0]*x[0] + W1[j][1]*x[1] + b1[j]) for j in range(2)]

acts = [hidden([1.0, 2.0]), hidden([2.0, 1.0])]

fig, axes = plt.subplots(1, 3, figsize=(10, 3))
panels = [
    (W1,   "W1: input -> hidden weights", ["x1", "x2"], ["h1", "h2"]),
    (V,    "V: hidden -> output weights", ["h1", "h2"], ["y"]),
    (acts, "hidden activations per input", ["h1", "h2"], ["x=(1,2)", "x=(2,1)"]),
]
for ax, (M, title, cols, rows) in zip(axes, panels):
    im = ax.imshow(M, cmap="coolwarm", vmin=-2, vmax=2)
    ax.set_title(title, fontsize=9)
    ax.set_xticks(range(len(cols)), cols)
    ax.set_yticks(range(len(rows)), rows)
    for i, row in enumerate(M):
        for j, val in enumerate(row):
            ax.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.8)
plt.tight_layout()
plt.savefig("tiny_net_viz.png", dpi=120)
print("wrote tiny_net_viz.png -- open it and compare each cell to your trace table")
```

### Critical Thinking Questions

7. In the $W_1$ heatmap, one cell is strongly negative ($w_{22} = -1.0$). Using your Part II traces, describe in plain English what that negative weight makes neuron $h_2$ *detect* about the input. (Consider: when is $h_2$ active, when $x_1 > x_2$, or when $x_1 < x_2$?)

   > *Hint: $h_2$'s pre-activation is $x_1 - x_2 + 0.5$. It fires when $x_1 - x_2 > -0.5$, i.e., roughly when $x_1$ is at least as large as $x_2$. A neuron with one positive and one negative incoming weight is computing a comparison between its inputs. Real networks are full of such learned comparisons.*

8. The activation heatmap has a cell that is exactly $0.0$ for input $(1, 2)$ but $1.5$ for input $(2, 1)$. A visualizer scaled to a real model would show thousands of such cells switching on and off per token. Why is this on/off *pattern* (not just the final output) useful to someone auditing a model's behavior?

   > *Hint: From question 5, the active/inactive pattern selects which linear formula the network applies. Two inputs producing the same output through different activation patterns are being processed by different "reasoning paths." Auditors look for neurons or patterns that activate on protected attributes, foreshadowing our explainability lab.*

Hands-on follow-ups (each opens in Google Colab; run top to bottom and watch the loss curves and weight visualizations evolve):

- [LinearFunctionEstimatorNN.ipynb](https://www.billmongan.com/Ursinus-CS357/files/notebooks/LinearFunctionEstimatorNN.ipynb), a single neuron learns a line; watch the weight and bias converge.
- [LinearFunctionEstimatorMultiLayerNN.ipynb](https://www.billmongan.com/Ursinus-CS357/files/notebooks/LinearFunctionEstimatorMultiLayerNN.ipynb), the same task with a hidden layer, like today's 2-2-1 network.
- [NonLinearFunctionEstimatorMultiLayerNN.ipynb](https://www.billmongan.com/Ursinus-CS357/files/notebooks/NonLinearFunctionEstimatorMultiLayerNN.ipynb), why the hidden layer plus ReLU matters: fitting a curve a single neuron cannot.
- [Simple_MNIST_NN_from_scratch.ipynb](https://www.billmongan.com/Ursinus-CS357/files/notebooks/Simple_MNIST_NN_from_scratch.ipynb), the same forward-pass arithmetic, scaled to 784 inputs, recognizing handwritten digits with no ML library.

---

# Part IV: The Bridge - Representation = Learned Embedding

In this Part you will connect Part I's embedding stage to Part II's hidden layer and see that they are the same kind of object: a learned representation. This closes the loop between the generation pipeline and the arithmetic you just did by hand.

## 4. An Embedding IS a Learned Representation

**Why this matters:** In the tokens-and-embeddings activity, embeddings were handed to you as given: "words become vectors, similar words have similar vectors." Now you can say *where those vectors come from*. The embedding table in Part I's pipeline is a layer of the network, a grid of weights, initialized randomly and adjusted by training exactly like $w_{11}$ and $b_1$ in your tiny network. And your tiny network's hidden layer built a representation too: it re-described the input $(1.0, 2.0)$ as the activation vector $(2.0, 0.0)$, a new coordinate system ("how much weighted-sum-pattern 1 is present, how much comparison-pattern 2 is present") that makes the output layer's job easy. An embedding is the same move applied to words: a learned re-description of a token that makes next-token prediction easy. **Representation = learned embedding**, whether the input is a pair of numbers or the word "sky."

## Model 4: Cosine Similarity, Revisited Inside the Network

Suppose training has produced these 4-number embeddings (the same kind of vectors flowing through Part I's pipeline):

| Token | Embedding |
|-------|-----------|
| "cat" | $(0.9, 0.2, -0.3, 0.1)$ |
| "kitten" | $(0.8, 0.3, -0.2, 0.0)$ |
| "carburetor" | $(-0.4, 0.7, 0.9, -0.5)$ |

Using the cosine similarity formula from the tokens-and-embeddings activity, $\cos(\text{cat}, \text{kitten}) \approx 0.982$ while $\cos(\text{cat}, \text{carburetor}) \approx -0.424$.

### Critical Thinking Questions

9. Verify $\cos(\text{cat}, \text{kitten}) \approx 0.982$ by hand: compute the dot product, both norms, and the ratio. (Calculator permitted; the Recorder writes all intermediate values.)

   > *Hint: dot product $= 0.72 + 0.06 + 0.06 + 0.0 = 0.84$; $\|\text{cat}\| = \sqrt{0.95} \approx 0.9747$; $\|\text{kitten}\| = \sqrt{0.77} \approx 0.8775$; then $0.84 / (0.9747 \times 0.8775) \approx 0.982$.*

10. Nobody typed these vectors in; they emerged from training on next-token prediction. Propose a mechanism: *why* would training push "cat" and "kitten" close together? What do those two tokens share that "carburetor" does not?

    > *Hint: "cat" and "kitten" appear in similar contexts ("the ___ purred", "fed the ___"). If two tokens need similar next-token predictions, the network's loss is lowest when their embeddings (the inputs to all downstream layers) are similar. Similar use pressures similar representation.*

11. Connect all four Parts in two sentences (Presenter reports out): where in the Part I pipeline does the Part II arithmetic happen, and where in the pipeline do the Part IV vectors live?

    > *Hint: The Part II forward pass is what happens inside the "transformer layers" and "output layer" boxes (many times over); the Part IV embedding vectors are the output of the "embedding lookup" box, and the hidden activations of Part II are the same kind of object one layer deeper.*

Which statement best captures the "bridge" of Part IV?

[( )] Embeddings are computed by the softmax stage at generation time
[( )] Embeddings are hand-designed lookup tables curated by linguists
[(X)] An embedding table is a layer of learned weights, so an embedding is a learned representation, the same kind of re-description a hidden layer performs
[( )] Embeddings are random vectors that change on every forward pass

---

# Part V: Synthesis and Practice

## Exercises

1. *Complete forward-pass practice.*

   - *What to do:* Work at least the first forward-pass problem of the printable worksheet [nn_by_hand_quadratic_full.pdf](https://www.billmongan.com/Ursinus-CS357/files/activity-neuralnets/nn_by_hand_quadratic_full.pdf) by hand, showing a trace table in exactly the Model 2 format. Then adapt today's code cell to verify it.
   - *Starter hint:* Copy the `forward` function and replace `W1`, `b1`, `V`, and `c` with the worksheet's values; add a loop over the worksheet's inputs.
   - *You've succeeded when:* Every row of your hand table matches the printed verification to two decimal places, and any discrepancy you found is annotated with the arithmetic slip that caused it.

2. *Break the network.*

   - *What to do:* Find an input $(x_1, x_2)$ with both coordinates between $-3$ and $3$ for which *both* hidden neurons output zero. Report the network's output for every such input and explain why it is constant.
   - *Starter hint:* You need $0.5 x_1 + 1.0 x_2 \le 0.5$ AND $1.0 x_1 - 1.0 x_2 \le -0.5$ simultaneously. Try $(-2, 0)$ or $(-1, -1)$. When all hidden activations are zero, what is left of the output formula?
   - *You've succeeded when:* You have at least two qualifying inputs, both produce output $c = 0.25$, and you can state the general principle (a dead layer makes the network output its bias, ignoring the input entirely).

3. *Temperature meets the pipeline.*

   - *What to do:* Using the Part I logits $(4.0, 2.5, 1.0, 0.5, -1.0)$, compute the full five-word distribution at $T = 2$ by hand, then verify in Python. Add a row to the Model 1 trace table showing how the pipeline's output changes while every upstream stage stays identical.
   - *Starter hint:* Scaled logits at $T=2$ are $(2.0, 1.25, 0.5, 0.25, -0.5)$. Exponentiate, sum, divide, the same three moves as always.
   - *You've succeeded when:* Your distribution sums to 1.000 (within rounding), $P(\text{blue})$ has dropped noticeably below $0.763$, and you can say which pipeline stages produced identical values across all three temperatures.

4. *Notebook scale-up.*

   - *What to do:* Run [Simple_MNIST_NN_from_scratch.ipynb](https://www.billmongan.com/Ursinus-CS357/files/notebooks/Simple_MNIST_NN_from_scratch.ipynb) end to end. Find the line(s) implementing the forward pass and annotate (in a Markdown cell) which line corresponds to each row of your Model 2 trace table.
   - *Starter hint:* Look for a matrix multiplication followed by a ReLU (or similar) function; that is $h = \text{ReLU}(W x + b)$ vectorized. The 2-2-1 structure becomes 784-10-10, but the rows of your trace table map one-to-one onto lines of code.
   - *You've succeeded when:* Your annotated notebook identifies the pre-activation, activation, and output computations, and the model trains to above 80% accuracy.

---

## Reflection Prompt

*Personal:* Today a "language model" resolved into arithmetic you can do by hand. Did opening the box make the technology feel more trustworthy to you, less, or differently trustworthy? Name one belief about AI you held two weeks ago that a trace table would have corrected.

*Technical:* Where does the randomness enter the generation pipeline, and (just as importantly) where does it NOT? List every stage from Part I's diagram in two columns (deterministic / random), and explain why setting temperature to zero changes the *sampling* column but leaves every weight, embedding, and logit untouched.

*Societal:* An embedding is a learned representation, and it is learned from human-written text. If the training text associates certain occupations more often with certain groups of people, where in today's pipeline does that association come to live, and why won't adjusting temperature remove it? (We will measure exactly this in the bias unit.)

---

## -> Coming Up Next

You can now trace a forward pass and point to where representations live. Next we ask what happens *between* the embedding lookup and the logits at scale: attention, the mechanism that lets every token's vector consult every other token's vector, and later, how those millions of weights get their values in the first place (training).

---

## 5. Further Reading

- Tom Yeh. *AI by Hand*, neural network and softmax worksheets.
- 3Blue1Brown. "But what is a neural network?" (video series on neural networks, gradient descent, and transformers).
- Michael Nielsen. *Neural Networks and Deep Learning*, Chapter 1. http://neuralnetworksanddeeplearning.com/chap1.html
- Andrej Karpathy. "The spelled-out intro to neural networks and backpropagation: building micrograd." (video).
- Melanie Mitchell. *AI: A Guide for Thinking Humans*, Chapter 2.
