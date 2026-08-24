<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-tokensembeddings.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-tokensembeddings.md

import: https://raw.githubusercontent.com/LiaTemplates/Pyodide/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tokens, Embeddings, and Attention: How Agents Represent and Mix Meaning

So far the model has been a box you send text to.  Today we open it, and we open it in the one place that pays off soonest: **how text becomes numbers, and how those numbers carry meaning**.  Your agents will shortly need to *search* documents by meaning rather than by keyword, and everything that makes that possible is here.

Three ideas, each built on the one before it: **tokens** (how text is cut into pieces a model can read), **embeddings** (how a piece of text becomes a point in space, so that closeness means similarity), and **attention** (how a token's meaning is adjusted by the tokens around it, which is what makes a modern language model modern).  We do all three with arithmetic small enough to check by hand, then use the result to build a working search engine in twenty lines.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Token** | The smallest chunk of text a model reads: roughly ¾ of a word on average, so "hamburger" is one token but "cheeseburger" might be two. Think of tokens as puzzle pieces that text is cut into. | `the` + `thing` -> 2 tokens using our toy rules |
| **Tokenizer** | The algorithm that cuts text into tokens, usually by starting with characters and merging frequent pairs (byte-pair encoding, or BPE). | Merging `t`+`h` -> `th`, then `th`+`e` -> `the` |
| **Embedding** | A list of numbers (a vector) that represents the *meaning* of a piece of text. It's like a GPS coordinate for meaning: similar meanings land near each other in this numerical space. | `"the dog ran"` -> `(1, 2, 2)` in a toy 3-D space |
| **Cosine Similarity** | A score from −1 to 1 measuring how similar two meaning-vectors are; specifically, the cosine of the angle between them. A score of 1 means "same direction = same meaning"; 0 means "unrelated." | `cos(a, b) = 1.0` when `b` is just a scaled copy of `a` |
| **Context Window** | The maximum number of tokens a model can read at once: its "working memory." A 4,000-token window holds roughly 3,000 English words. | A 4,000-token budget ≈ a 6-page double-spaced essay |
| **Semantic Search** | Finding documents by *meaning* rather than exact keyword match. Powered by comparing embedding vectors. | Querying "when can I get help from my professor" finds "Office hours for CS357 are Tuesday and Thursday mornings" |
| **Attention** | The mechanism that lets each token's meaning be adjusted by the tokens around it, instead of being fixed by a lookup table. Each token asks every other token "how relevant are you to me?" and blends in a share of their meaning accordingly | Section 2b: watching the vector for "bank" move toward the financial sense when "loan" is standing next to it |
| **Query, key, value** | The three roles every token plays in attention. The **query** is what this token is looking for, the **key** is what it offers as a match, and the **value** is the content it contributes if it is selected. A library search: your search term, the index cards, and the books | The three columns of the toy table in Model 3 |
| **Transformer** | The neural-network architecture that stacks attention many times over, and the thing the "T" in GPT stands for. Every model you have talked to this semester is one | The thing the by-hand arithmetic in Section 2b does once and a real model does billions of times a second |

---

## Today's 75 Minutes

Three ideas, each built on the one before it, each worked by hand before any code runs.

| | What you do | Roughly |
|---|---|---|
| **Part I** | Cut text into tokens by hand with real merge rules, then check yourself against a real tokenizer | 20 min |
| **&sect;2 and Model 2** | Turn meaning into geometry, and compute cosine similarity on paper | 15 min |
| **&sect;2b and Model 3** | The idea attention exists to solve, then one full attention step by hand | 20 min |
| **Demo and Try It Yourself** | Predict the numbers, run the cell in your browser, then break it three ways | 10 min |
| **&sect;2c and Part II** | What the arithmetic costs you, and a twenty-line semantic search engine | 10 min |
| **Part III** | Exercises and reflection | take-home |
| **Extension** | Self-paced: one prompt end to end by hand, from tokenizing through the weight update | self-paced |

That is seventy-five minutes, and it is the densest session of the term.  Saying so is more useful than pretending otherwise.

If the room runs long, Part II is the part to finish on your own.  It is the least by-hand of the four and the most self-explanatory from the code, and its questions are answerable from a run you do at home.  **Do not skip Model 3.**  Everything after this session that involves a language model rests on the arithmetic in it, and it is the one piece you will not reconstruct from reading later.

Bring the printed *Neural Network by Hand* worksheet, or a tablet you can write on.

---

# Part I: From Characters to Tokens

In this part, you will tokenize a short phrase by hand using a simplified rule set and discover why models struggle with tasks that seem trivially easy for humans, like counting the letters in a word.  Understanding tokenization also explains why your chat budget is measured in tokens, not words or characters.

## 1.  Tokenization

**Why this matters:** Every time you send a message to an AI, the first thing it does is chop your text into tokens, not words, not letters, but something in between.  This matters because the model never sees the letter "e" inside "cheeseburger"; it sees whatever token the tokenizer carved out.  That is why models struggle to count letters, why long numbers trip them up, and why your chat budget is measured in tokens rather than words.  It's like the difference between reading a book word-by-word versus reading it one syllable at a time: the chunks you use change what patterns you notice.

Models do not read words; they read tokens.  A tokenizer (the algorithm that cuts text into tokens) splits text into subword units drawn from a fixed vocabulary, typically built by byte-pair encoding (BPE, a compression algorithm that starts with individual characters and repeatedly merges the most frequent adjacent pair into a single token): begin with characters, repeatedly merge the most frequent adjacent pair, and stop at a target vocabulary size (often 30,000 to 200,000 entries).  Common words become single tokens; rare words shatter into pieces, so "unhappiness" may become `un` + `happiness` and "Collegeville" may become three fragments.

Tokenization explains odd model behaviors.  Counting letters in a word is hard when the model never sees individual letters; arithmetic on long numbers is hard when digits group unpredictably; and the *context window* (the model's working memory) is measured in tokens, which is why a 4,000-token budget holds roughly 3,000 English words.  A rough rule of thumb: **1 token ≈ ¾ of an English word**, or about 4 characters.

---

## Model 1: Tokenize by Hand

Given the toy merge rules (`t`+`h`->`th`, `th`+`e`->`the`, `i`+`n`->`in`, `in`+`g`->`ing`), tokenize: "the thing".

### Critical Thinking Questions

1.  Apply the merges step by step.  How many tokens result?  The Recorder shows the merge sequence.

   > *Hint: Start with every character as its own token: `t h e   t h i n g`.  Then apply each merge rule left-to-right, in order, as many times as it applies.  Count what remains.*

2.  Why do frequent character pairs deserve dedicated tokens?  Connect your answer to compression.

   > *Hint: If "th" appears in thousands of words, how many fewer tokens do you need to store a typical English text if "th" is one token instead of two?  Think of it like a ZIP file for language.*

3.  Predict which is more tokens: "internationalization" or "the cat sat on the mat".  Justify before checking intuition against the class.

   > *Hint: "internationalization" is a single rare word; rare words shatter into many subword pieces.  The second phrase has 6 common words.  Which do you expect has more tokens?  Try to estimate using the ¾-word rule.*

### Worked Example: where those merge rules came from (BPE, by hand)

The four merge rules above were handed to you.  Real tokenizers *learn* them, and the learning rule is almost embarrassingly simple: **repeatedly merge the most frequent adjacent pair.**  Here is the whole algorithm on a four-word corpus.

**Corpus** (word, frequency), with `</w>` marking a word end:

```
low </w>      5
lower </w>    2
newest </w>   6
widest </w>   3
```

**Step 0: start from characters.**  The initial vocabulary is every character: `l o w e r n s t i d </w>`.

```
l o w </w>            5
l o w e r </w>        2
n e w e s t </w>      6
w i d e s t </w>      3
```

**Merge 1.**  Count every adjacent pair across the corpus, weighted by word frequency:

| Pair | Where it occurs | Count |
|---|---|---|
| `e s` | newest (6), widest (3) | **9** |
| `s t` | newest (6), widest (3) | 9 |
| `l o` | low (5), lower (2) | 7 |
| `o w` | low (5), lower (2) | 7 |
| `w e` | newest (6) | 6 |

`e s` and `s t` tie at 9; break the tie by order encountered and merge **`e s` -> `es`**:

```
l o w </w>            5
l o w e r </w>        2
n e w es t </w>       6
w i d es t </w>       3
```

**Merge 2.**  Recount.  Now `es t` occurs 6 + 3 = **9**, the new maximum.  Merge **`es t` -> `est`**:

```
l o w </w>            5
l o w e r </w>        2
n e w est </w>        6
w i d est </w>        3
```

**Merge 3.**  Recount. `est </w>` occurs 9 times.  Merge **`est </w>` -> `est</w>`**:

```
l o w </w>            5
l o w e r </w>        2
n e w est</w>         6
w i d est</w>         3
```

Three merges in, the learned merge table is `[es, est, est</w>]`, and notice what it discovered without being told: **`est` is an English suffix.**  Nobody supplied a morphology rule.  Frequency did it.

### Worked Example: encoding a word the tokenizer has never seen

This is the step that explains the failures the course keeps invoking.  Take the learned merge table above, in order, and encode **`lowest`**, a word that never appeared in the training corpus.

| Stage | Sequence | Rule applied |
|---|---|---|
| start | `l o w e s t </w>` | split to characters |
| after merge 1 | `l o w es t </w>` | `e s` -> `es` |
| after merge 2 | `l o w est </w>` | `es t` -> `est` |
| after merge 3 | `l o w est</w>` | `est </w>` -> `est</w>` |
| final | **`l` `o` `w` `est</w>`** | no more rules apply |

Four tokens, and the model has never seen this word.  It sees a prefix spelled out letter by letter plus a suffix it knows well.

**Now the punchline.**  Ask a model how many `r`s are in *strawberry*.  A production tokenizer splits it into something like `str` `aw` `berry`: three chunks, and **not one of them is a letter**.  The model is not looking at `s-t-r-a-w-b-e-r-r-y`; it is looking at three opaque IDs.  Counting letters inside a token is not a reasoning failure, it is an *input representation* failure: the information was destroyed before the model ever saw it.  The same mechanism explains why models are shaky at rhyming, at reversing strings, and at arithmetic on long numbers.

### Check it against a real tokenizer

Hand-tracing is the point, but seeing where the toy diverges from production is worth fifteen lines:

```python  liascript
# pip install tiktoken
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")

for word in ["lowest", "strawberry", "Collegeville", "CS357", "internationalization"]:
    ids = enc.encode(word)
    pieces = [enc.decode([i]) for i in ids]
    print(f"{word:22s} -> {len(ids)} tokens  {pieces}")
```

Run it and compare against your hand trace.  Two things to notice: common words are single tokens while rare ones shatter, and the split points frequently land *mid-morpheme*; the tokenizer optimizes for frequency, not for meaning.  That gap is where a surprising share of model weirdness lives.


---

## 2.  Embeddings: Meaning as Geometry

**Why this matters:** Once text is tokenized, the model still needs a way to understand that "dog" and "puppy" are related while "dog" and "tax return" are not.  The solution is to map every piece of text to a point in a high-dimensional space; think of it as a map where meaning is location.  Words with similar meanings land near each other on the map, just like cities in the same region are physically close.  This single idea powers search engines, recommendation systems, and the retrieval pipelines our agents will use in the *Retrieval-Augmented Generation with Chroma* activity.

**An embedding maps a token, sentence, or document to a vector** $\mathbf{v} \in \mathbb{R}^d$ (with $d$ commonly 384 to 4096; that is, a list of 384 to 4096 numbers) such that *semantically similar texts map to nearby vectors*.  The standard similarity measure is **cosine similarity** (the cosine of the angle between two vectors):

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert}
$$

which ranges from $-1$ (opposite meaning) through $0$ (unrelated) to $1$ (identical direction/meaning).  Embedding models are trained so that paraphrases score high and unrelated texts score low; this single idea powers semantic search, clustering, recommendation, and the retrieval pipelines our agents will use in the *Retrieval-Augmented Generation with Chroma* activity.

---

## Model 2: Cosine by Hand

Let $\mathbf{a} = (1, 2, 2)$ for "the dog ran" and $\mathbf{b} = (2, 4, 4)$ for "a dog was running", and $\mathbf{c} = (2, -1, 0)$ for "quarterly tax filing."

### Critical Thinking Questions

4.  Compute $\cos(\mathbf{a}, \mathbf{b})$ and $\cos(\mathbf{a}, \mathbf{c})$ by hand (AI by Hand style: show the dot products and norms).  The Recorder writes the full arithmetic.

   > *Hint: The dot product $\mathbf{a} \cdot \mathbf{b} = (1)(2) + (2)(4) + (2)(4)$. The norm $\lVert \mathbf{a} \rVert = \sqrt{1^2 + 2^2 + 2^2}$. Divide the dot product by the product of the two norms.*

5. $\mathbf{b} = 2\mathbf{a}$ exactly.  What does cosine similarity say about vectors that differ only in magnitude, and why is that a desirable property for comparing a short query with a long document?

   > *Hint: A short question like "parking rules?" and a long parking policy document might have similar meanings but very different lengths.  Should length penalize similarity?  What does the division by the norms accomplish?*

> **Common Misconception:** A high cosine similarity score does NOT mean the two sentences share the same words, that one logically implies the other, or that either is factually true.  It only means the embedding model placed them in a similar *direction* in meaning-space; they are topically close.  Two completely wrong sentences about the same topic can score 0.95 with each other.

Two sentences receive embeddings with cosine similarity 0.92.  The best interpretation is:

[( )] The sentences share at least 92 percent of their words
[(X)] The embedding model places them in nearly the same direction, suggesting closely related meaning
[( )] One sentence logically entails the other
[( )] Both sentences are factually true

---

## 2b.  When One Vector Is Not Enough: Attention

Everything in Section 2 rests on an assumption worth challenging: that a word *has* an embedding.  One word, one vector, looked up in a table.

Consider "bank."

> The **bank** was steep and muddy.
> The **bank** approved the loan.

Same five letters, two unrelated meanings.  A lookup table gives them one vector, which must therefore be wrong at least half the time.  Something has to let the surrounding words change what a word means, and that something is **attention**.  It is the single idea that separates the models you are using this semester from the word-vector methods that came before them.

### The idea, before the arithmetic

Each token gets three vectors instead of one, playing three roles:

- a **query** $\mathbf{q}$: *what am I looking for?*
- a **key** $\mathbf{k}$: *what do I offer as a match?*
- a **value** $\mathbf{v}$: *what content do I contribute if I am chosen?*

Think of a library search.  Your search term is the query.  The index cards are the keys.  The books are the values.  To find out how relevant token $j$ is to token $i$, take the **dot product** $\mathbf{q}_i \cdot \mathbf{k}_j$ (the same operation from the numerator of cosine similarity in Section 2, one line of arithmetic you already know).  Run those relevance scores through **softmax** so they become weights that sum to 1, then build the token's new meaning as a weighted blend of everyone's values.

That is the whole mechanism, and it is written compactly as:

$$
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right) V
$$

where $Q$, $K$, and $V$ stack every token's query, key, and value into matrices, and $\sqrt{d_k}$ (the square root of the vector length) divides the scores to keep them from growing large enough to make softmax saturate.  A **transformer** stacks this operation dozens of times, in parallel "heads," with small neural networks in between.  That is the architecture; you are about to do one layer of it by hand.

---

## Model 3: Attention by Hand

Three tokens, two dimensions, all arithmetic visible.  The vectors below are already projected into their three roles:

| token | $\mathbf{q}$ | $\mathbf{k}$ | $\mathbf{v}$ |
|-------|------|------|------|
| river | (1, 0) | (1, 0) | (1, 1) |
| bank  | (1, 1) | (0, 1) | (2, 0) |
| loan  | (0, 1) | (1, 1) | (0, 2) |

We compute the new representation of **bank**, using $\mathbf{q}_{\text{bank}} = (1,1)$ and $d_k = 2$, so $\sqrt{d_k} \approx 1.41$.

**Step 1, relevance: dot the query against every key.**

- vs. river, $\mathbf{k} = (1,0)$: $\;1{\times}1 + 1{\times}0 = \mathbf{1}$
- vs. bank, $\mathbf{k} = (0,1)$: $\;1{\times}0 + 1{\times}1 = \mathbf{1}$
- vs. loan, $\mathbf{k} = (1,1)$: $\;1{\times}1 + 1{\times}1 = \mathbf{2}$

Raw scores $[1, 1, 2]$. "loan" is already the most relevant, and we have done nothing but multiply and add.

**Step 2, scale.**  Divide each by $\sqrt{2} \approx 1.41$: $[0.71,\; 0.71,\; 1.41]$.

**Step 3, softmax.**  Raise $e \approx 2.718$ to each score, then divide by the total:

$e^{0.71} \approx 2.03$, $e^{0.71} \approx 2.03$, $e^{1.41} \approx 4.10$; total $8.16$.

Weights: $[\,0.25,\; 0.25,\; 0.50\,]$. "bank" gives half its attention to "loan" and a quarter each to "river" and itself.

**Step 4, blend the values.**

$$
\text{new\_bank} = 0.25(1,1) + 0.25(2,0) + 0.50(0,2) = (0.25,0.25) + (0.50,0) + (0,1.00) = (0.75,\; 1.25)
$$

**Read the result.**  Without context, `bank` was $(2, 0)$: all first-dimension, no second.  After one layer of attention it is $(0.75, 1.25)$: the second dimension, contributed almost entirely by `loan`, now dominates.  Context *moved the meaning*, and it moved it by arithmetic you just did on paper.

### Critical Thinking Questions

6.  Redo Steps 1 through 3 for the sentence **"bank loan"**, with `river` removed entirely.  There are now two softmax inputs instead of three, so the weights must sum to 1 over two tokens.  Does "bank" lean differently?

   > *Hint: The raw scores are the same two numbers as before; only the denominator of the softmax changes.  Predict the direction of the change before you compute it.*

7.  In Step 1, `bank`'s query scored 1 against its own key, the same score it gave `river`.  Why is it useful for a token to attend to itself at all, rather than only to its neighbors?

8.  Look at Section 2's cosine-similarity formula and Step 1 here.  Both start with a dot product.  Name the one thing cosine does that attention's relevance score does not, and suggest why attention might not want it.

   > *Hint: Cosine divides by the two norms.  What is that division for, and what would you lose if a token's "loudness" could no longer affect how much others attend to it?*

9.  The context window from the Key Concepts table is bounded by this arithmetic.  Every token computes a score against every other token, so $n$ tokens cost $n^2$ scores.  If you grow a prompt from 2,000 tokens to 8,000, by what factor does the attention work grow?  Connect that number to a cost or latency you have already noticed on your own machine.

> **Common Misconception:** "Attention means the model is focusing, or paying attention, the way a person does."  The name is a metaphor for a weighted average, nothing more.  Every token attends to every other token every time, with a weight; none of them is ignored, and none of them is being concentrated on.  What you computed above is the entire phenomenon: dot products, a softmax, and a weighted sum.

In the calculation above, which quantity decided *how much* `bank` was influenced by `loan`?

[( )] The value vector $\mathbf{v}_{\text{loan}} = (0,2)$
[(X)] The softmax weight 0.50, computed from the dot product of `bank`'s query with `loan`'s key
[( )] The order of the tokens in the sentence
[( )] The dimension $d_k = 2$

---

## Demo: Check Your Arithmetic Against the Machine

You just did one layer of attention on paper.  Now watch the machine do the same thing, and hold it to your numbers.

**Before you press Run, write down your predictions.**  From Model 3 you should already have: the three raw scores, the three softmax weights, and the new `bank` vector.  Put them on paper now.  A prediction you did not commit to is not a prediction.

This cell runs in your browser, so there is nothing to install and no server involved.  Change the numbers and run it again as often as you like.

```python
import numpy as np

q = {"river": np.array([1., 0.]), "bank": np.array([1., 1.]), "loan": np.array([0., 1.])}
k = {"river": np.array([1., 0.]), "bank": np.array([0., 1.]), "loan": np.array([1., 1.])}
v = {"river": np.array([1., 1.]), "bank": np.array([2., 0.]), "loan": np.array([0., 2.])}
tokens = ["river", "bank", "loan"]

def softmax(z):
    e = np.exp(z - z.max())          # subtract the max for numerical stability
    return e / e.sum()

scores  = np.array([q["bank"] @ k[t] for t in tokens]) / np.sqrt(2)
weights = softmax(scores)
new_bank = sum(w * v[t] for w, t in zip(weights, tokens))

print("raw/scaled scores :", np.round(scores, 3))
print("softmax weights   :", np.round(weights, 3))
print("new bank vector   :", np.round(new_bank, 3))
```
@Pyodide.eval

Your paper and the output should agree to two decimal places.  If they do not, the disagreement is the most useful thing on this page: find which of the four steps drifted.

### Try It Yourself

1.  **Delete a word.**  Remove `"river"` from `tokens` and run again.  The softmax now normalizes over two tokens instead of three.  Predict the direction the new `bank` vector moves *before* you run it, then check.  This is question 6 above, done in code.

   *You've succeeded when* you can say in one sentence why dropping an unrelated word still changed `bank`, and what that implies about padding a prompt with filler.

2.  **Change the query.**  Compute the new representation of `river` instead of `bank`, by swapping `q["bank"]` for `q["river"]` in the `scores` line.  Which token does `river` lean on, and does that match your intuition about the sentence?

   *You've succeeded when* you can point at the specific dot product that made the difference.

3.  **Break the scaling.**  Delete the `/ np.sqrt(2)` and run again.  Now multiply every vector by 10 and run both versions.  Watch what the unscaled softmax does to the weights.

   *You've succeeded when* you can explain what $\sqrt{d_k}$ is protecting against, using the numbers you just saw rather than the formula.

---

## 2c.  What This Arithmetic Already Costs You

The attention mechanism is not a mathematical curiosity.  It sets the budget you have to work with for the rest of the semester, and two consequences of it will shape every agent you build.

**The context window is the attention span, literally.**  Attention compares every token with every other token, so $n$ tokens cost $n^2$ scores; doubling the context quadruples the work.  That is why context windows are finite, why long prompts are slow on your laptop, and why the *small context window principle* we adopt in *Memory and the Small Context Window Principle* is a computational fact rather than a matter of taste.  Grow a prompt from 2,000 tokens to 8,000 and the attention work per layer grows by a factor of 16, because $8000^2 / 2000^2 = 16$.

**Position matters, and not evenly.**  Models attend most reliably to the beginning and the end of a long context and are measurably worse at material buried in the middle, an effect usually called *lost in the middle*.  This is why we put an agent's standing instructions and the current question at the edges of a prompt, with retrieved evidence in between, once we start building retrieval pipelines.

**Depth is fixed, so the number of dependent steps is fixed.**  Attention lets any token look at any other token, which is a genuinely powerful thing and is not the same as computing.  A stack of layers gives the model a set number of operations that can *depend on each other* before it has to commit to a token, and that number was frozen when the model was trained.  A problem needing more dependent steps than the stack has does not get more; the model answers anyway.  Hold onto this, because *Why Different Answers Every Time?* shows you the one way out of it, and the way out is not a bigger context or better attention: it is the model writing intermediate results into its own context and reading them back on the next pass.

> **Common Misconception: "More context is always better."**  Three things say otherwise, and you have now seen all three.  The cost is quadratic, so a longer prompt is not a free improvement.  The middle of a long prompt is the least reliable part of it.  And every extra token competes for the same finite attention budget, so filler actively dilutes the signal from the tokens that mattered.  Retrieve only what is relevant, place it deliberately, and keep prompts as short as the task allows.

---

# Part II: Semantic Search in Code

In this part, you will use a real embedding model (a neural network that converts text to vectors) to build a tiny search engine that finds documents by meaning rather than by matching exact words.  This is the retrieval foundation that your agents will use in the next module to access documents they were never trained on.

## 3.  A Search Engine in Twenty Lines

Ollama serves embedding models too.  We embed a handful of campus FAQ sentences and search them by meaning, not keywords.  The code below first calls the embedding model to convert each document to a vector (a list of numbers representing its meaning), stores all the vectors in a matrix, and then finds the closest match to any new query using cosine similarity.

---

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import requests
import numpy as np

np.random.seed(42)

def embed(text, model="nomic-embed-text"):
    try:
        r = requests.post("http://localhost:11434/api/embeddings",
                          json={"model": model, "prompt": text}, timeout=120)
        return np.array(r.json()["embedding"])
    except Exception as e:
        print(f"[embeddings:embed] {e}")
        import traceback; traceback.print_exc()
        return np.zeros(768)

docs = [
    "The library is open until midnight on weekdays.",
    "Students may park in Lot G with a valid permit.",
    "The dining hall serves brunch on Saturdays and Sundays.",
    "Office hours for CS357 are Tuesday and Thursday mornings.",
    "Intramural soccer registration closes Friday.",
]

D = np.array([embed(d) for d in docs])

def search(query, k=2):
    q = embed(query)
    sims = D @ q / (np.linalg.norm(D, axis=1) * np.linalg.norm(q))
    for i in np.argsort(-sims)[:k]:
        print(f"{sims[i]:.3f}  {docs[i]}")

search("when can I get help from my professor")
print()
search("where do I leave my car")
```

---

## Model 4: Probing the Geometry

### Critical Thinking Questions

10.  Neither query shares a single content word with its best match.  Identify exactly which line of code performed the "understanding," and what it computes mathematically.

   > *Hint: Look at the line `sims = D @ q / ...`. `D @ q` is a matrix-vector product; what does each entry of the result represent?  Which earlier formula from Model 2 does this implement?*

11.  Craft a query that retrieves the *wrong* document with high confidence.  What does the failure reveal about what embeddings capture and what they miss (negation, numbers, proper names)?

   > *Hint: Try something like "the library is NOT open on weekends"; does the negation change the retrieved document?  Try a query with a specific number that doesn't appear in any document.  What does that tell you about what the embedding "remembers"?*

12.  The matrix-vector product `D @ q` computes all similarities at once.  For one million documents, what becomes expensive, and what data structure might help?  (This previews vector databases.)

   > *Hint: With 1 million documents each having 768 numbers, how many multiplications does one search require?  (Multiply 1,000,000 × 768.)  What if you could organize the vectors spatially so you only had to check a fraction of them?*

---

# Part III: Synthesis and Practice

In this part, you will extend the search engine to reveal the geometry of meaning: building similarity matrices, testing the classic king-man+woman=queen analogy, and auditing how token counts constrain what you can fit in an agent's context window.

## 4.  Exercises

1.  *Similarity matrix.*  Embed eight sentences of your team's choosing spanning two obvious topics.  Compute the full 8×8 cosine similarity matrix, render it as a heatmap, and verify that the block structure matches the topics.

   - *What to do:* Choose 4 sentences about Topic A (e.g., dining) and 4 about Topic B (e.g., parking).  Call `embed()` on each, build the 8×8 matrix using the cosine formula, and visualize with `matplotlib` using `imshow`.
   - *Starter hint:* `matrix[i][j] = np.dot(vecs[i], vecs[j]) / (np.linalg.norm(vecs[i]) * np.linalg.norm(vecs[j]))`.  For the heatmap: `plt.imshow(matrix, vmin=-1, vmax=1, cmap='coolwarm')`.
   - *You've succeeded when:* The top-left 4×4 block and bottom-right 4×4 block show high similarity (warm colors), while the off-diagonal blocks show low similarity (cool colors).

2.  *Analogy probe.*  Test the classic claim that embedding arithmetic captures analogy: compare $\cos(\text{embed}(\text{"king"}) - \text{embed}(\text{"man"}) + \text{embed}(\text{"woman"}),\ \text{embed}(\text{"queen"}))$ against unrelated words.  Report whether your sentence-level model exhibits the effect, and hypothesize why or why not.

   - *What to do:* Compute the four embeddings, do the vector arithmetic, then compare the result to `embed("queen")` using cosine similarity.  Also compare it to `embed("table")` as a baseline.
   - *Starter hint:* `analogy_vec = embed("king") - embed("man") + embed("woman")`.  Then `cosine(analogy_vec, embed("queen"))` vs `cosine(analogy_vec, embed("table"))`.
   - *You've succeeded when:* You can report the two similarity scores and explain why sentence-level models may show a weaker analogy effect than word-level models like Word2Vec.

3.  *Token budget audit.*  Estimate the token count of your team charter document at four characters per token, then explain how that figure constrains stuffing it into an agent's prompt every turn.  (We address this properly in the memory module.)

   - *What to do:* Count the total characters in your charter (or any document of at least 500 words), divide by 4 to estimate tokens, and compare that figure to a 4,000-token context window.
   - *Starter hint:* `token_estimate = len(document_text) / 4`.  If your context window is 4,000 tokens and your system prompt costs 300 tokens and each user turn costs ~50 tokens, how many turns can fit alongside the full charter?
   - *You've succeeded when:* You can state the charter's token estimate, the percentage of the context window it occupies, and one concrete consequence for an agent that carries the full charter every turn.

---

## Reflection Prompt

*Personal:* Think about a time you searched for something online and the search engine found exactly what you meant even though you used different words than the page used.  How does that experience connect to what embeddings are doing mathematically?

*Technical:* In your notebook: meaning, for an embedding model, is location in a high-dimensional space learned from co-occurrence patterns in text.  Name one aspect of meaning in your favorite discipline (a poem's irony, a proof's elegance, a primary source's provenance) that you suspect geometry cannot capture, and explain why co-occurrence statistics would fail to encode it.

*Societal:* Embedding models encode the statistical patterns of whatever text they were trained on, including that text's biases.  If a job-application screening system uses embeddings to find "similar" resumes to high-performing employees, what kinds of historical bias might get amplified?  Who is harmed, and what safeguard would you design?

---

## -> Coming Up Next

Next session hands the workbench to a coding agent in *Coding Agents: OpenCode, Spec-First Development, and Reading the Diff*, and the session after that asks why a model gives a different answer every time, which is a question about the *last* step of the pipeline you started tracing today.

The geometry itself returns in *Retrieval-Augmented Generation with Chroma*, where instead of searching five sentences we index thousands of document chunks in a **vector database** and use that index to give agents access to information they were never trained on.

---

## 5.  Further Reading

- [Sentence Prediction with BERT notebook](https://www.billmongan.com/Ursinus-CS357/files/notebooks/Sentence_Prediction_with_BERT.ipynb), a runnable companion that uses BERT's masked-token predictions to see contextual embeddings in action.
- Tom Yeh.  *AI by Hand*, embedding and dot-product worksheets.
- Jay Alammar.  "The Illustrated Word2Vec" (online).  A visual introduction to embedding geometry.
- Reimers and Gurevych.  "Sentence-BERT." *EMNLP* (2019).  How sentence-level embeddings are trained.

---

# Extension: Anatomy of an LLM Request (self-paced)

Nothing in Parts I through III assumes what follows, and none of it is required to finish today's work.  It is here because at some point you will want to see the whole path at once: one prompt taken end to end by hand, from tokenizing through embedding, attention, the feed-forward block, sampling, loss, and the weight update.  Today we took that path in pieces.  This is the piece-by-piece walk stitched back together.  Come back to it when the pieces stop feeling separate.

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

## From Text to Vectors

In this part, you turn the prompt into numbers, the only thing a neural network can process.

### Tokenize, Embed, and Add Position

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

#### Questions to Work Through

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

## Attention - Query, Key, Value, and the Weighted Sum

In this part, you compute how the last token, "cat," gathers information from the tokens before it.  This is the mechanism at the heart of every transformer.

### Project Each Token into a Query, a Key, and a Value

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

#### Questions to Work Through

1.  Verify by hand that $k_{\text{cat}} = (1, 2)$ by multiplying $x_{\text{cat}} = (1,1)$ by $W_K$. Show the two dot products.

   > *Hint: The first component is $(1,1)$ dotted with the first column of $W_K$, which is $(1,0)$. The second uses the second column $(1,1)$.*

2.  If $W_Q$, $W_K$, and $W_V$ were all the identity matrix, what would $q$, $k$, and $v$ equal?  Explain why that would waste the model's expressive power.

   > *Hint: The identity leaves a vector unchanged.  If all three roles were the same vector, could a token ever "look for" something different from what it "advertises"?*

### Attention Scores, Softmax, and the Context Vector

The last token, "cat," now asks every token (including itself; causal attention lets a token attend to itself and everything before it) how relevant it is, by dotting its query with each key.

**Step 1: Scores.**  With $q_{\text{cat}} = (1,1)$:

$$\text{score}_{\text{the}} = k_{\text{the}} \cdot q_{\text{cat}} = (1,1)\cdot(1,1) = 2 \qquad \text{score}_{\text{cat}} = k_{\text{cat}} \cdot q_{\text{cat}} = (1,2)\cdot(1,1) = 3$$

**Step 2: Scale** by $\sqrt{d_k} = \sqrt{2} \approx 1.4142$ (this keeps scores from growing with dimension; see *Attention and Transformers*):

$$\frac{2}{\sqrt 2} = 1.4142 \qquad \frac{3}{\sqrt 2} = 2.1213$$

**Step 3: Softmax** turns the two scaled scores into attention weights:

$$e^{1.4142} = 4.1132, \quad e^{2.1213} = 8.3421, \quad \text{sum} = 12.4554$$
$$\alpha_{\text{the}} = \frac{4.1132}{12.4554} = 0.3302 \qquad \alpha_{\text{cat}} = \frac{8.3421}{12.4554} = 0.6698$$

**Step 4: Weighted sum of values** gives the context vector for "cat":

$$\text{context} = 0.3302\,(0,1) + 0.6698\,(1,1) = (0.6698,\; 0.3302 + 0.6698) = (0.6698,\; 1.0)$$

The vector $(0.6698, 1.0)$ is "cat," now aware of the token before it.  That is the one number attention produces, and it flows into Part III.

#### Questions to Work Through

1.  "cat" put weight $0.6698$ on itself and $0.3302$ on "the."  Explain what it would mean if the attention weights had come out $(0.5, 0.5)$ instead.  What in the scores would have to be true?

   > *Hint: Equal softmax weights require equal scaled scores.  What would that say about how relevant "the" and "cat" are to the query?*

2.  The scaled scores differ by about $0.707$, yet the softmax weights differ by roughly a factor of two ($0.33$ vs $0.67$).  Why does softmax exaggerate a modest gap in scores?

   > *Hint: Softmax exponentiates before normalizing.  What does $e^x$ do to a difference of $0.707$ in the exponent?*

3.  This is where the $O(n^2)$ cost of context length comes from (see the *Memory and the Small Context Window Principle* activity).  With 2 tokens we computed 2 scores.  How many query·key scores would a 1,000-token prompt need for its last token, and for *all* tokens?

   > *Hint: The last token dots against all prior keys.  Summed over every token attending to every prior token, the total grows like $n^2$.*

The context vector $(0.6698, 1.0)$ for "cat" is computed as:

[( )] The average of the query, key, and value vectors
[( )] The token embedding of "cat" with its position removed
[(X)] The softmax-weighted sum of the **value** vectors, using attention weights from the query·key scores
[( )] The largest of the two attention scores

---

## From Vector to Token

In this part, you turn the context vector into an actual next-word prediction.

### Feed-Forward, Logits, Softmax, Sample

**Step 1: Feed-forward network.**  After attention, each token passes through a small per-token network: a linear layer then a ReLU. With

$$W_1 = \begin{bmatrix} 1 & 0 \\ 1 & 1 \end{bmatrix}, \quad b_1 = (0, 0), \qquad z = \text{context}\,W_1 + b_1$$
$$z = (0.6698\cdot 1 + 1.0\cdot 1,\; 0.6698\cdot 0 + 1.0\cdot 1) = (1.6698,\; 1.0)$$

ReLU replaces negatives with 0.  Both components here are positive, so $h = \text{ReLU}(z) = (1.6698, 1.0)$ passes through unchanged.  (For a case where ReLU actually clips a negative to zero, see the fully worked 2-2-1 network in [From Text Generation to a Neural Network](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/TextGenToNN).)

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

**Step 4: Sample.**  At temperature 0 (greedy) the model emits the argmax: **"sat."**  The full request "the cat" -> "sat" is complete.  (Temperature and top-p reshape this distribution before sampling; see the *Why Different Answers Every Time?  Sampling, Temperature, and Generation* activity.)

#### Questions to Work Through

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

## How the Weights Got Their Values

Every number above (the embeddings, the projection matrices, the unembedding) started as random noise and was *learned*.  This part takes one step of that learning, so you can see how a weight changes.

### Loss, Gradient, and One Step of Descent

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

#### Questions to Work Through

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

### Code Cell: Reproduce Every Number

The cell below runs the entire request (embed, project, attend, feed-forward, unembed, softmax, sample) and then the single training step, printing each intermediate value.  Compare every line to your by-hand work; they should match to rounding.  It also does a **numerical gradient check**: it perturbs $W_U[\text{sat},0]$ slightly and confirms the measured slope of the loss equals the analytic gradient $-0.7029$.

> **Predict first.**  This cell recomputes every number in the walkthrough above.  Pick any three of them from your own paper trace, write them down, and check those three against the output rather than skimming the whole thing.  Three numbers you actually verified are worth more than a page you nodded at.


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
@Pyodide.eval

---

### Exercises

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

### Reflection Prompt

**Personal**: Before this activity, "the model predicts the next token" may have felt like magic or memory.  Now that you have carried one prompt through every matrix multiply by hand, has your mental picture changed?  Which single stage most changed how you think about what a language model *is*?

**Technical**: Every stage here was a matrix multiply followed by a simple nonlinearity (softmax or ReLU).  In your notebook, describe how the *same five stages* scale to a real model with thousands of dimensions and a 100,000-token vocabulary.  What stays exactly the same, and what only changes in size?

**Societal**: You saw that the model stores no sentences, only weights it computes from.  Yet those weights were *learned from human text* whose patterns, biases, and gaps are baked into the embeddings and projection matrices you multiplied.  If "sat" won an arithmetic competition decided by learned weights, what does that imply about who is responsible for a model's outputs, and about the data those weights were trained on?

---

### Going Deeper: The Full $QK^\top$ Matrix, By Hand

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
