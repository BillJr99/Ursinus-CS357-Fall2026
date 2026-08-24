<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-llmanatomy.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-llmanatomy.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Anatomy of an LLM Request: One Prompt, End to End, by Hand

You have met every stage of a language model separately: tokens and embeddings, attention, sampling, training loss.  This activity threads them together.  We take **one** tiny prompt, **"the cat"**, and carry it (with real numbers you can check on paper) all the way from raw text to a single predicted next token, and then take one step of the training that gave the model its weights.  Nothing is a black box here: every matrix is small enough to multiply by hand, and a code cell at the end reproduces every number.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  The Manager keeps the team moving through the five stages in order; skipping ahead breaks the running example.  The Recorder writes down every intermediate vector exactly as computed, because each stage's output is the next stage's input.  The Presenter prepares a two-minute "trace the token" walkthrough for the class.  The Reflector notes which stage the team found least intuitive and why.  After class, please respond to the reflective prompt on your own in your notebook.

This activity is a **synthesis**.  Each stage has a deeper standalone activity: `liascript-tokensembeddings.md` (tokens/embeddings), `liascript-attentiontransformers.md` (attention by hand), `liascript-textgen2nn.md` (the forward pass and ReLU), `liascript-samplinggeneration.md` (sampling), and `liascript-llmpretraining.md` (loss and perplexity).  Here we do not re-derive them; we connect them with one consistent set of numbers.

---

## Key Concepts

| Term | Plain-English Definition | Where It Appears Today |
|------|--------------------------|------------------------|
| **Token** | A chunk of text mapped to an integer id from a fixed vocabulary | "the" -> id 0, "cat" -> id 1 |
| **Embedding** | The learned vector a token id looks up, the model's numeric "meaning" for that token | id 1 ("cat") -> $(0, 1)$ |
| **Positional encoding** | A vector added to an embedding to tell the model *where* in the sequence the token sits | position 1 adds $(1, 0)$ |
| **Q/K/V projection** | Three learned matrices $W_Q, W_K, W_V$ that turn each token vector into a **query**, a **key**, and a **value** | $q = x\,W_Q$, and $q,k,v$ all differ from $x$ |
| **Attention score** | The dot product of one token's query with another token's key, "how relevant is that token to me?" | key·query $= 2$ and $3$ |
| **Softmax** | Turns a vector of scores into a probability distribution (positive, sums to 1) | scores $\to (0.3302, 0.6698)$ |
| **Context vector** | The attention-weighted sum of value vectors, one token's view of the whole sequence so far | $(0.6698, 1.0)$ |
| **Feed-forward network (FFN)** | A small per-token neural network (linear -> ReLU) applied after attention | $(0.6698,1.0) \to (1.6698, 1.0)$ |
| **Unembedding / logits** | A matrix that scores the final vector against every vocabulary token, producing one **logit** per token | 5 logits, one per word |
| **Cross-entropy loss** | How surprised the model is by the correct next token: $-\log p(\text{target})$ | $-\log(0.5791) = 0.5464$ |
| **Gradient descent step** | Nudge a weight opposite its gradient so the loss goes down | one entry of $W_U$: $1.0 \to 1.3514$ |

Throughout we use **2-dimensional** vectors and a **5-word vocabulary** so the arithmetic fits on a napkin.  Real models use thousands of dimensions and vocabularies of 100,000+ tokens, but *every operation is exactly the one you will do here, just larger.*

---

# Part I: From Text to Vectors

In this part, you turn the prompt into numbers, the only thing a neural network can process.

## Model 1: Tokenize, Embed, and Add Position

Our toy vocabulary has five tokens, each with an integer id and a learned 2-D embedding:

| Token | id | Embedding |
|---|---|---|
| the | 0 | $(1, 0)$ |
| cat | 1 | $(0, 1)$ |
| sat | 2 | $(1, 1)$ |
| ran | 3 | $(-1, 1)$ |
| mat | 4 | $(1, -1)$ |

**Step 1: Tokenize.**  The prompt **"the cat"** becomes the id sequence $[0, 1]$.

**Step 2: Embed.**  Look up each id's row: "the" $\to (1, 0)$, "cat" $\to (0, 1)$.

**Step 3: Add positional encoding.**  Attention alone cannot tell "the cat" from "cat the," so we add a position vector.  Use $\text{pos}_0 = (0,0)$ and $\text{pos}_1 = (1,0)$:

$$x_{\text{the}} = (1,0) + (0,0) = (1, 0) \qquad x_{\text{cat}} = (0,1) + (1,0) = (1, 1)$$

These two vectors, $x_{\text{the}} = (1,0)$ and $x_{\text{cat}} = (1,1)$, are the model's input.  Every later stage operates on them.

### Critical Thinking Questions

1.  The tokens "the" and "cat" have embeddings $(1,0)$ and $(0,1)$, orthogonal vectors.  In one sentence, what would it mean geometrically if two tokens had *identical* embeddings, and why would that be a problem?

   > *Hint: Embeddings are the model's only handle on meaning.  If two different words map to the same vector, can any later stage ever tell them apart?*

2.  We added position *after* embedding.  Show what $x_{\text{cat}}$ would be if "cat" appeared in position 0 instead of position 1.  Why does the model need this, given that attention (next part) treats its inputs as an unordered set?

   > *Hint: $\text{pos}_0 = (0,0)$. Recompute $(0,1) + \text{pos}_0$. If two orderings produced identical vectors, could the model ever distinguish "dog bites man" from "man bites dog"?*

Why does a transformer add a positional encoding to the token embedding before attention?

[( )] To make the vectors longer so they carry more information
[(X)] Because attention itself is order-agnostic, so without position the model cannot tell "the cat" from "cat the"
[( )] To convert the token id into a probability
[( )] To reduce the size of the vocabulary

---

# Part II: Attention - Query, Key, Value, and the Weighted Sum

In this part, you compute how the last token, "cat," gathers information from the tokens before it.  This is the mechanism at the heart of every transformer.

## Model 2: Project Each Token into a Query, a Key, and a Value

A token's input vector plays three different roles, so the model learns three matrices to produce three different views of it.  Using our (row-vector) convention $q = x\,W_Q$:

$$W_Q = \begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix} \quad W_K = \begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix} \quad W_V = \begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}$$

Apply them to each input vector.  For the **query** of "cat" ($x_{\text{cat}} = (1,1)$):

$$q_{\text{cat}} = (1,1)\begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix} = (1\cdot 0 + 1\cdot 1,\; 1\cdot 1 + 1\cdot 0) = (1, 1)$$

Doing this for all tokens and all three matrices:

| | query $q$ | key $k$ | value $v$ |
|---|---|---|---|
| the $(1,0)$ | $(0, 1)$ | $(1, 1)$ | $(0, 1)$ |
| cat $(1,1)$ | $(1, 1)$ | $(1, 2)$ | $(1, 1)$ |

Notice that $q$, $k$, and $v$ are all **different** from the input $x$ and from each other; that is the whole point of the projection.  The query asks "what am I looking for?"; the key advertises "what do I offer?"; the value is "what I actually contribute if attended to."

### Critical Thinking Questions

1.  Verify by hand that $k_{\text{cat}} = (1, 2)$ by multiplying $x_{\text{cat}} = (1,1)$ by $W_K$. Show the two dot products.

   > *Hint: The first component is $(1,1)$ dotted with the first column of $W_K$, which is $(1,0)$. The second uses the second column $(1,1)$.*

2.  If $W_Q$, $W_K$, and $W_V$ were all the identity matrix, what would $q$, $k$, and $v$ equal?  Explain why that would waste the model's expressive power.

   > *Hint: The identity leaves a vector unchanged.  If all three roles were the same vector, could a token ever "look for" something different from what it "advertises"?*

## Model 3: Attention Scores, Softmax, and the Context Vector

The last token, "cat," now asks every token (including itself; causal attention lets a token attend to itself and everything before it) how relevant it is, by dotting its query with each key.

**Step 1: Scores.**  With $q_{\text{cat}} = (1,1)$:

$$\text{score}_{\text{the}} = k_{\text{the}} \cdot q_{\text{cat}} = (1,1)\cdot(1,1) = 2 \qquad \text{score}_{\text{cat}} = k_{\text{cat}} \cdot q_{\text{cat}} = (1,2)\cdot(1,1) = 3$$

**Step 2: Scale** by $\sqrt{d_k} = \sqrt{2} \approx 1.4142$ (this keeps scores from growing with dimension; see `liascript-attentiontransformers.md`):

$$\frac{2}{\sqrt 2} = 1.4142 \qquad \frac{3}{\sqrt 2} = 2.1213$$

**Step 3: Softmax** turns the two scaled scores into attention weights:

$$e^{1.4142} = 4.1132, \quad e^{2.1213} = 8.3421, \quad \text{sum} = 12.4554$$
$$\alpha_{\text{the}} = \frac{4.1132}{12.4554} = 0.3302 \qquad \alpha_{\text{cat}} = \frac{8.3421}{12.4554} = 0.6698$$

**Step 4: Weighted sum of values** gives the context vector for "cat":

$$\text{context} = 0.3302\,(0,1) + 0.6698\,(1,1) = (0.6698,\; 0.3302 + 0.6698) = (0.6698,\; 1.0)$$

The vector $(0.6698, 1.0)$ is "cat," now aware of the token before it.  That is the one number attention produces, and it flows into Part III.

### Critical Thinking Questions

1.  "cat" put weight $0.6698$ on itself and $0.3302$ on "the."  Explain what it would mean if the attention weights had come out $(0.5, 0.5)$ instead.  What in the scores would have to be true?

   > *Hint: Equal softmax weights require equal scaled scores.  What would that say about how relevant "the" and "cat" are to the query?*

2.  The scaled scores differ by about $0.707$, yet the softmax weights differ by roughly a factor of two ($0.33$ vs $0.67$).  Why does softmax exaggerate a modest gap in scores?

   > *Hint: Softmax exponentiates before normalizing.  What does $e^x$ do to a difference of $0.707$ in the exponent?*

3.  This is where the $O(n^2)$ cost of context length comes from (see `liascript-memorycontext.md`).  With 2 tokens we computed 2 scores.  How many query·key scores would a 1,000-token prompt need for its last token, and for *all* tokens?

   > *Hint: The last token dots against all prior keys.  Summed over every token attending to every prior token, the total grows like $n^2$.*

The context vector $(0.6698, 1.0)$ for "cat" is computed as:

[( )] The average of the query, key, and value vectors
[( )] The token embedding of "cat" with its position removed
[(X)] The softmax-weighted sum of the **value** vectors, using attention weights from the query·key scores
[( )] The largest of the two attention scores

---

# Part III: From Vector to Token

In this part, you turn the context vector into an actual next-word prediction.

## Model 4: Feed-Forward, Logits, Softmax, Sample

**Step 1: Feed-forward network.**  After attention, each token passes through a small per-token network: a linear layer then a ReLU. With

$$W_1 = \begin{bmatrix} 1 & 0 \\ 1 & 1 \end{bmatrix}, \quad b_1 = (0, 0), \qquad z = \text{context}\,W_1 + b_1$$
$$z = (0.6698\cdot 1 + 1.0\cdot 1,\; 0.6698\cdot 0 + 1.0\cdot 1) = (1.6698,\; 1.0)$$

ReLU replaces negatives with 0.  Both components here are positive, so $h = \text{ReLU}(z) = (1.6698, 1.0)$ passes through unchanged.  (For a case where ReLU actually clips a negative to zero, see the fully worked 2-2-1 network in `liascript-textgen2nn.md`.)

**Step 2: Unembedding to logits.**  A matrix $W_U$ (one row per vocabulary token, here reusing the embedding directions) scores $h$ against every token: $\text{logit}_i = W_{U,i} \cdot h$.

| Token | row of $W_U$ | logit $= \text{row}\cdot(1.6698, 1.0)$ |
|---|---|---|
| the | $(1, 0)$ | $1.6698$ |
| cat | $(0, 1)$ | $1.0000$ |
| **sat** | $(1, 1)$ | $\mathbf{2.6698}$ |
| ran | $(-1, 1)$ | $-0.6698$ |
| mat | $(1, -1)$ | $0.6698$ |

**Step 3: Softmax over the vocabulary** turns logits into next-token probabilities:

$$e^{1.6698}=5.3109,\; e^{1.0}=2.7183,\; e^{2.6698}=14.4365,\; e^{-0.6698}=0.5118,\; e^{0.6698}=1.9538$$

The sum is $24.9313$, giving:

| the | cat | **sat** | ran | mat |
|---|---|---|---|---|
| $0.2130$ | $0.1090$ | $\mathbf{0.5791}$ | $0.0205$ | $0.0784$ |

**Step 4: Sample.**  At temperature 0 (greedy) the model emits the argmax: **"sat."**  The full request "the cat" -> "sat" is complete.  (Temperature and top-p reshape this distribution before sampling; see `liascript-samplinggeneration.md`.)

### Critical Thinking Questions

1.  "sat" won with probability $0.5791$, but "the" had a healthy $0.2130$. At a high temperature, roughly what happens to the gap between these two, and how could that change which token is sampled?

   > *Hint: Temperature divides the logits before softmax.  Dividing by a number bigger than 1 flattens the distribution; does that make an upset more or less likely?*

2.  The unembedding gave "sat" the highest logit because its direction $(1,1)$ aligns best with $h = (1.6698, 1.0)$. Which token was *least* likely, and what about its direction explains that?

   > *Hint: Look for the row whose dot product with $(1.6698, 1.0)$ is most negative.  Which direction points "against" $h$?*

The five logits are converted into the five next-token probabilities by:

[( )] Dividing each logit by the number of tokens
[(X)] Applying softmax across the whole vocabulary so the values are positive and sum to 1
[( )] Keeping only the largest logit and setting the rest to 0
[( )] Multiplying each logit by its embedding

> **Common Misconception:** It is tempting to picture the model "looking up" the answer to "the cat" in some stored table of sentences.  It does no such thing.  There is no sentence "the cat sat" stored anywhere.  The model holds only **weights**: the embedding rows, the projection matrices $W_Q, W_K, W_V$, the FFN weights, and the unembedding $W_U$. Given "the cat," it *computes* a fresh probability distribution over its entire vocabulary every single time, through exactly the matrix operations above.  "sat" is not retrieved; it is the token that wins an arithmetic competition.

---

# Part IV: How the Weights Got Their Values

Every number above (the embeddings, the projection matrices, the unembedding) started as random noise and was *learned*.  This part takes one step of that learning, so you can see how a weight changes.

## Model 5: Loss, Gradient, and One Step of Descent

Suppose the correct next token really is **"sat."**  During training we ask: how surprised was the model?  That is the **cross-entropy loss**, the negative log probability of the true token:

$$L = -\log p(\text{sat}) = -\log(0.5791) = 0.5464$$

Lower is better; a perfect model would put probability 1 on "sat" for a loss of 0.  To improve, we nudge each weight in the direction that reduces $L$. A wonderful fact about cross-entropy after softmax is that the gradient of the loss with respect to each logit is simply

$$\frac{\partial L}{\partial \text{logit}_i} = p_i - y_i$$

where $y_i = 1$ for the true token and $0$ otherwise.  For "sat": $p_{\text{sat}} - 1 = 0.5791 - 1 = -0.4209$ (negative, meaning we should *raise* this logit).

Now pick **one** weight to update: the first entry of the "sat" row of the unembedding, $W_U[\text{sat},0]$, currently $1.0$. Since $\text{logit}_{\text{sat}} = W_U[\text{sat}] \cdot h$, the chain rule gives

$$\frac{\partial L}{\partial W_U[\text{sat},0]} = (p_{\text{sat}} - 1)\cdot h_0 = (-0.4209)(1.6698) = -0.7029$$

Take a gradient-descent step (learning rate $\eta = 0.5$), moving *opposite* the gradient:

$$W_U[\text{sat},0] \leftarrow 1.0 - 0.5\,(-0.7029) = 1.0 + 0.3514 = 1.3514$$

Did it help?  Recompute just that logit: $\text{logit}_{\text{sat}} = 1.3514\cdot 1.6698 + 1.0\cdot 1.0 = 3.2566$ (up from $2.6698$).  Re-running softmax, $p_{\text{sat}}$ rises from $0.5791$ to $0.7121$, and the loss **drops** from $0.5464$ to $0.3395$. One weight, one step, and the model is measurably less surprised by "sat."  Training is this same step, repeated across every weight and billions of examples.

### Critical Thinking Questions

1.  The gradient $p_i - y_i$ for the true token "sat" was **negative** ($-0.4209$), while for a wrong token like "the" it would be **positive** ($+0.2130$).  Explain how the sign tells gradient descent to *raise* the correct token's logit but *lower* a wrong token's.

   > *Hint: Gradient descent moves opposite the gradient.  A negative gradient means subtracting a negative, which raises the weight.  What does a positive gradient do?*

2.  We used learning rate $\eta = 0.5$. Predict qualitatively what happens to $W_U[\text{sat},0]$ and the loss if $\eta$ were enormous, say $50$. Why do practitioners keep the learning rate small?

   > *Hint: The step size is $\eta$ times the gradient.  A giant step can overshoot the minimum entirely; the loss can go *up*.  What is the risk of stepping too far?*

3.  We updated only one of the ten-plus weights in this model.  If we instead updated *every* weight by its own gradient in the same step, would the loss drop by more or less than the $0.5464 \to 0.3395$ we saw?  Why?

   > *Hint: Each weight's update independently reduces the loss (to first order).  What happens when many small improvements combine?*

After one gradient-descent step on $W_U[\text{sat},0]$, the loss went from $0.5464$ to $0.3395$. This happened because:

[( )] The model looked up the correct answer and memorized it
[(X)] The weight moved opposite its gradient, raising the "sat" logit and thus $p(\text{sat})$, which lowers $-\log p(\text{sat})$
[( )] Softmax was disabled after training
[( )] The learning rate was set to zero

---

## Code Cell: Reproduce Every Number

The cell below runs the entire request (embed, project, attend, feed-forward, unembed, softmax, sample) and then the single training step, printing each intermediate value.  Compare every line to your by-hand work; they should match to rounding.  It also does a **numerical gradient check**: it perturbs $W_U[\text{sat},0]$ slightly and confirms the measured slope of the loss equals the analytic gradient $-0.7029$.

```python
import numpy as np
np.set_printoptions(precision=4, suppress=True)
vocab = ["the", "cat", "sat", "ran", "mat"]

# --- Part I: embeddings + positions ---
E = {"the":[1,0], "cat":[0,1], "sat":[1,1], "ran":[-1,1], "mat":[1,-1]}
pos = {0:np.array([0.,0]), 1:np.array([1.,0])}
x_the = np.array(E["the"], float) + pos[0]     # (1,0)
x_cat = np.array(E["cat"], float) + pos[1]     # (1,1)
X = np.stack([x_the, x_cat])
print("x_the =", x_the, "  x_cat =", x_cat)

# --- Part II: Q/K/V projections (row-vector convention q = x @ W) ---
W_Q = np.array([[0.,1],[1,0]])   # swap
W_K = np.array([[1.,1],[0,1]])   # shear
W_V = np.array([[0.,1],[1,0]])   # swap
q, k, v = X @ W_Q, X @ W_K, X @ W_V
print("q =", q.tolist(), " k =", k.tolist(), " v =", v.tolist())

# attention for the last token "cat"
q_cat = q[1]
scores = k @ q_cat
scaled = scores / np.sqrt(2)
ex = np.exp(scaled); alpha = ex / ex.sum()
context = alpha @ v
print("scores =", scores, " scaled =", np.round(scaled,4))
print("attention weights =", np.round(alpha,4), " context =", np.round(context,4))

# --- Part III: FFN -> logits -> softmax -> sample ---
W1 = np.array([[1.,0],[1,1]]); b1 = np.array([0.,0])
h = np.maximum(context @ W1 + b1, 0.0)          # ReLU
W_U = np.array([[1.,0],[0,1],[1,1],[-1,1],[1,-1]])
logits = W_U @ h
p = np.exp(logits - logits.max()); p = p / p.sum()
print("h =", np.round(h,4))
print("logits =", dict(zip(vocab, np.round(logits,4))))
print("probs  =", dict(zip(vocab, np.round(p,4))))
print("PREDICTION:", vocab[int(np.argmax(logits))])

# --- Part IV: cross-entropy loss + one gradient step on W_U[sat,0] ---
target = vocab.index("sat")
L = -np.log(p[target])
dz = p.copy(); dz[target] -= 1                  # dL/dlogit = p - y
grad = dz[target] * h[0]                         # dL/dW_U[sat,0]
eta = 0.5
new_w = W_U[target,0] - eta * grad
print("\nloss =", round(float(L),4), "  grad dL/dW_U[sat,0] =", round(float(grad),4))
print("W_U[sat,0]: %.4f -> %.4f" % (W_U[target,0], new_w))

# effect of the update
W_U2 = W_U.copy(); W_U2[target,0] = new_w
lg2 = W_U2 @ h; p2 = np.exp(lg2 - lg2.max()); p2 /= p2.sum()
print("logit_sat: %.4f -> %.4f" % (logits[target], lg2[target]))
print("p_sat: %.4f -> %.4f   loss: %.4f -> %.4f"
      % (p[target], p2[target], L, -np.log(p2[target])))

# numerical gradient check
eps = 1e-5
def loss_at(w):
    Wc = W_U.copy(); Wc[target,0] = w
    lg = Wc @ h; pp = np.exp(lg - lg.max()); pp /= pp.sum()
    return -np.log(pp[target])
num = (loss_at(W_U[target,0]+eps) - loss_at(W_U[target,0]-eps)) / (2*eps)
print("numerical grad = %.4f   analytic grad = %.4f  (match!)" % (num, grad))
```

---

## Exercises

**Exercise 1: Change the prompt to "the mat."**

- *What to do*: Keep every matrix the same, but start from "the mat" instead of "the cat."  Recompute $x_{\text{mat}}$ (remember position 1 adds $(1,0)$), then $q_{\text{mat}}, k$, the attention scores against both tokens, the context vector, the FFN output, and the five logits.  Which token does the model predict now?
- *Starter hint*: $x_{\text{mat}} = (1,-1) + (1,0) = (2,-1)$. Push it through exactly the steps in Parts II-III. You can check yourself by editing `E`/the input in the code cell.
- *You've succeeded when*: You have a full by-hand trace ending in a predicted token, and the code cell confirms your logits.

**Exercise 2: Make the model *more* confident in "sat."**

- *What to do*: Instead of updating only $W_U[\text{sat},0]$, also update $W_U[\text{sat},1]$ by one gradient step (its gradient is $(p_{\text{sat}}-1)\cdot h_1$).  Recompute $\text{logit}_{\text{sat}}$, $p(\text{sat})$, and the loss after updating *both* entries.  Did the loss drop more than updating one weight did?
- *Starter hint*: $h_1 = 1.0$, so the second gradient is $(-0.4209)(1.0) = -0.4209$. Update both entries of the "sat" row, then recompute $\text{logit}_{\text{sat}} = W_U[\text{sat}]\cdot h$.
- *You've succeeded when*: You can state the new loss and explain, in one sentence, why updating more weights reduced it further.

**Exercise 3: Break position and observe.**

- *What to do*: Set both positional encodings to $(0,0)$ so "the cat" and "cat the" become indistinguishable to attention.  Recompute the context vector for the last token under both orderings and show they are now identical.  Explain in two sentences what capability the model has lost.
- *Starter hint*: With $\text{pos}_0 = \text{pos}_1 = (0,0)$, the input vectors depend only on which words are present, not their order.  Compute the last token's context for "the cat" and for "cat the."
- *You've succeeded when*: You have shown the two context vectors are equal and connected that to why positional encodings exist.

---

## Reflection Prompt

**Personal**: Before this activity, "the model predicts the next token" may have felt like magic or memory.  Now that you have carried one prompt through every matrix multiply by hand, has your mental picture changed?  Which single stage most changed how you think about what a language model *is*?

**Technical**: Every stage here was a matrix multiply followed by a simple nonlinearity (softmax or ReLU).  In your notebook, describe how the *same five stages* scale to a real model with thousands of dimensions and a 100,000-token vocabulary.  What stays exactly the same, and what only changes in size?

**Societal**: You saw that the model stores no sentences, only weights it computes from.  Yet those weights were *learned from human text* whose patterns, biases, and gaps are baked into the embeddings and projection matrices you multiplied.  If "sat" won an arithmetic competition decided by learned weights, what does that imply about who is responsible for a model's outputs, and about the data those weights were trained on?

---

## -> Coming Up Next

You now understand a single forward pass and a single training step.  Two threads open from here.  First: *why does the same prompt sometimes give different answers?*, that is sampling and temperature (`liascript-samplinggeneration.md`), acting on the very probability distribution you just computed.  Second: *how is this pass run efficiently for thousands of users at once?*, that is KV caching, batching, and PagedAttention (`liascript-llmserving.md`), which optimize exactly the attention computation from Part II.

---

## Going Deeper: The Full $QK^\top$ Matrix, By Hand

Model 1 computed one row, the query for "bank."  Exercise 1 asks you to do "river."  Here is the whole matrix at once, because seeing all three rows together is what makes the mechanism click: **attention is not a special operation applied to one token, it is the same operation applied to every token in parallel.**

Queries $\mathbf{q}$: river $(1,0)$, bank $(1,1)$, loan $(1,1)$.
Keys $\mathbf{k}$: river $(1,0)$, bank $(0,1)$, loan $(1,1)$.
Values $\mathbf{v}$: river $(1,1)$, bank $(2,0)$, loan $(0,2)$.

**Raw scores $QK^\top$** (each cell is $\mathbf{q}_{\text{row}} \cdot \mathbf{k}_{\text{col}}$):

| $\mathbf{q} \downarrow$ / $\mathbf{k} \rightarrow$ | river | bank | loan |
|---|---|---|---|
| **river** | 1 | 0 | 1 |
| **bank** | 1 | 1 | 2 |
| **loan** | 1 | 1 | 2 |

**Scaled by $\sqrt{d_k} = \sqrt{2} \approx 1.414$:**

| | river | bank | loan |
|---|---|---|---|
| **river** | 0.71 | 0.00 | 0.71 |
| **bank** | 0.71 | 0.71 | 1.41 |
| **loan** | 0.71 | 0.71 | 1.41 |

**Softmax, row by row** (each row sums to 1; that is what makes it a distribution over "where do I look"):

| | river | bank | loan | -> new vector |
|---|---|---|---|---|
| **river** | 0.40 | 0.20 | 0.40 | $(0.80,\; 1.20)$ |
| **bank** | 0.25 | 0.25 | 0.50 | $(0.74,\; 1.26)$ |
| **loan** | 0.25 | 0.25 | 0.50 | $(0.74,\; 1.26)$ |

Check the "river" row against Exercise 1: $e^{0.71} = 2.03$, $e^{0} = 1.00$, $e^{0.71} = 2.03$, sum $= 5.06$, so weights $2.03/5.06 = 0.40$, $1.00/5.06 = 0.20$, $0.40$. Then $0.40(1,1) + 0.20(2,0) + 0.40(0,2) = (0.80, 1.20)$.

**Three things this matrix shows that a single row cannot.**

1.  **The matrix is not symmetric.**  Row "river" gives "bank" a weight of 0.20, but row "bank" gives "river" 0.25.  Attention is *directional* ("what does A want from B" is a different question from "what does B want from A") because queries and keys are different projections.  This is the single most common misconception about attention.

2.  **"bank" and "loan" have identical rows.**  They started with identical query vectors $(1,1)$, so they attend identically and end up with the same output.  Nothing in this toy distinguishes them, which is exactly why real models use *many* attention heads with *different* learned projections, so that different heads can separate tokens this head cannot.

3.  **Every row is $O(n)$ work and there are $n$ rows.**  That is the $O(n^2)$ cost of self-attention, visible as the literal area of the table.  Double the context length and the table quadruples.  This is the whole economic argument for retrieval instead of just pasting more text into the prompt.


## Further Reading

- This activity synthesizes five companions, each going deeper on one stage: `liascript-tokensembeddings.md`, `liascript-attentiontransformers.md`, `liascript-textgen2nn.md`, `liascript-samplinggeneration.md`, and `liascript-llmpretraining.md`.
- Vaswani et al. "Attention Is All You Need."  NeurIPS 2017.  The paper that introduced the transformer architecture whose forward pass you just traced.
- Tom Yeh.  *AI by Hand.*  Worksheets that compute attention, feed-forward layers, and softmax by hand at the same scale used here.
- 3Blue1Brown, "But what is a GPT? / Attention in transformers" (video series).  Visual, animated companions to the matrix operations in Parts II-III.
