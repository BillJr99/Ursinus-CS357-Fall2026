---
layout: default-standard
permalink: /Tutorials/TokensEmbeddingsAttention
title: 'CS357: Foundations of Artificial Intelligence - Tokens, Embeddings, and Attention: How Models Represent Meaning'
info:
  coursenum: CS357
  purpose: "To open the model at the point that pays off soonest: how text becomes numbers, how those numbers carry meaning, and how the words around a token change what it means."
tags:
- tokenization
- embeddings
- attention
---

{% include mathjax.html %}

# CS357: Foundations of Artificial Intelligence - Tokens, Embeddings, and Attention: How Models Represent Meaning

## Purpose

To open the model at the point that pays off soonest: how text becomes numbers, how those numbers carry meaning, and how the words around a token change what it means.

## About This Tutorial

So far the model has been a box you send text to.  This tutorial opens the box in the one place that pays off soonest: how text becomes numbers, and how those numbers carry meaning.  Your agents will soon need to search documents by meaning rather than by keyword, and everything that makes that possible is here.

Three ideas, each built on the one before it.  A **token** is a piece of text a model can read.  An embedding turns a piece of text into a point in space, so that closeness means similarity.  Attention lets the tokens around a token adjust its meaning, which is what makes a modern language model modern.  Part I shows how a tokenizer learns its rules and checks the result against a production tokenizer.  Sections 2 through 2c cover embeddings, attention, and what attention costs you.  Part II builds a working semantic search engine in twenty lines.  The final Part carries one prompt end to end through a toy transformer, from token ids through a single weight update.

This article explains the mechanisms and shows the worked examples.  The by-hand practice that goes with it (tokenizing a phrase with toy merge rules, computing cosine similarity on paper, one full attention step with three tokens, and a browser cell that checks your arithmetic) lives in the companion article at [{{ site.baseurl }}/Tutorials/AIByHand]({{ site.baseurl }}/Tutorials/AIByHand).  Read this article first, then work the companion's models on paper.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|------|--------------------------|----------------------|
| **Token** | The smallest chunk of text a model reads: roughly three quarters of a word on average, so "hamburger" is one token but "cheeseburger" might be two.  Tokens are the puzzle pieces text is cut into. | `l` `o` `w` `est</w>`: four tokens for "lowest" under the toy merge rules in Part I |
| **Tokenizer** | The algorithm that cuts text into tokens, usually by starting with characters and merging frequent pairs (byte-pair encoding, or BPE). | Merging `e`+`s` -> `es`, then `es`+`t` -> `est` |
| **Embedding** | A list of numbers (a vector) that represents the meaning of a piece of text.  It is like a GPS coordinate for meaning: similar meanings land near each other in this numerical space. | `"the dog ran"` -> `(1, 2, 2)` in a toy 3-D space |
| **Cosine Similarity** | A score from -1 to 1 measuring how similar two meaning-vectors are: the cosine of the angle between them.  A score of 1 means "same direction, same meaning"; 0 means "unrelated." | `cos(a, b) = 1.0` when `b` is a scaled copy of `a` |
| **Context Window** | The maximum number of tokens a model can read at once: its working memory.  A 4,000-token window holds roughly 3,000 English words. | A 4,000-token budget is about a six-page double-spaced essay |
| **Semantic Search** | Finding documents by meaning rather than by exact keyword match, by comparing embedding vectors. | Querying "when can I get help from my professor" finds "Office hours for CS357 are Tuesday and Thursday mornings" |
| **Attention** | The mechanism that lets each token's meaning be adjusted by the tokens around it, instead of being fixed by a lookup table.  Each token asks every other token "how relevant are you to me?" and blends in a share of their meaning accordingly. | Section 2b: the vector for "bank" moves toward the financial sense when "loan" is standing next to it |
| **Query, key, value** | The three roles every token plays in attention.  The query is what this token is looking for, the key is what it offers as a match, and the value is the content it contributes if it is selected.  A library search: your search term, the index cards, and the books. | The three vectors defined in Section 2b |
| **Transformer** | The neural-network architecture that stacks attention many times over, and the thing the "T" in GPT stands for.  Every model you have talked to this semester is one. | One layer of the arithmetic in Section 2b, which a real model repeats billions of times a second |

---

# Part I: From Characters to Tokens

Models read tokens, not words.  This Part shows how a tokenizer cuts text into tokens, how it learned its cutting rules, and why those rules explain failures that look like reasoning failures but are not.  It also explains why your chat budget is measured in tokens rather than words or characters.

## 1.  Tokenization

Every message you send to a model is first chopped into tokens: not words, not letters, but something in between.  The model never sees the letter "e" inside "cheeseburger"; it sees whatever token the tokenizer carved out.  That is why models struggle to count letters, why long numbers trip them up, and why your chat budget is measured in tokens.  Reading by token is like reading a book one syllable at a time instead of one word at a time: the chunks you use change which patterns you notice.  The analogy stops there, because a tokenizer's chunks follow frequency, not sound.

A tokenizer is the algorithm that cuts text into tokens.  It splits text into subword units drawn from a fixed vocabulary.  Most tokenizers build that vocabulary by byte-pair encoding (BPE), a compression method: start with individual characters, repeatedly merge the most frequent adjacent pair into a single token, and stop at a target vocabulary size (often 30,000 to 200,000 entries).  Common words become single tokens.  Rare words shatter into pieces, so "unhappiness" may become `un` + `happiness` and "Collegeville" may become three fragments.

Tokenization explains several odd model behaviors.  Counting letters in a word is hard when the model never sees individual letters.  Arithmetic on long numbers is hard when digits group unpredictably.  And the context window (the model's working memory) is measured in tokens, which is why a 4,000-token budget holds roughly 3,000 English words.  A rough rule of thumb: one token is about three quarters of an English word, or about four characters.

### How a Tokenizer Learns Its Merge Rules

Real tokenizers learn their merge rules, and the learning rule is short: repeatedly merge the most frequent adjacent pair.  Here is the whole algorithm on a four-word corpus.

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

`e s` and `s t` tie at 9.  Break the tie by order encountered and merge **`e s` -> `es`**:

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

**Merge 3.**  Recount.  `est </w>` occurs 9 times.  Merge **`est </w>` -> `est</w>`**:

```
l o w </w>            5
l o w e r </w>        2
n e w est</w>         6
w i d est</w>         3
```

Three merges in, the learned merge table is `[es, est, est</w>]`.  Notice what it discovered without being told: `est` is an English suffix.  Nobody supplied a morphology rule.  Frequency did it.

### Encoding a Word the Tokenizer Has Never Seen

This step explains the failures the course keeps invoking.  Take the learned merge table above, in order, and encode **`lowest`**, a word that never appeared in the training corpus.

| Stage | Sequence | Rule applied |
|---|---|---|
| start | `l o w e s t </w>` | split to characters |
| after merge 1 | `l o w es t </w>` | `e s` -> `es` |
| after merge 2 | `l o w est </w>` | `es t` -> `est` |
| after merge 3 | `l o w est</w>` | `est </w>` -> `est</w>` |
| final | **`l` `o` `w` `est</w>`** | no more rules apply |

Four tokens, for a word the model has never seen.  It sees a prefix spelled out letter by letter plus a suffix it knows well.

Now ask a model how many `r`s are in *strawberry*.  A production tokenizer splits it into something like `str` `aw` `berry`: three chunks, and not one of them is a letter.  The model is not looking at `s-t-r-a-w-b-e-r-r-y`; it is looking at three opaque ids.  Counting letters inside a token is not a reasoning failure.  It is an input representation failure: the information was destroyed before the model ever saw it.  The same mechanism explains why models are shaky at rhyming, at reversing strings, and at arithmetic on long numbers.

### Check It Against a Real Tokenizer

Hand-tracing is the point, but seeing where the toy diverges from production is worth fifteen lines.

> **Runs on your machine, not here.**  This cell needs the `tiktoken` package, which you install in your course container rather than in the page.  Copy it there and run it.

```python
# pip install tiktoken
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")

for word in ["lowest", "strawberry", "Collegeville", "CS357", "internationalization"]:
    ids = enc.encode(word)
    pieces = [enc.decode([i]) for i in ids]
    print(f"{word:22s} -> {len(ids)} tokens  {pieces}")
```

Run it and compare against the `lowest` trace above.  Two things to notice: common words are single tokens while rare ones shatter, and the split points frequently land mid-morpheme.  The tokenizer optimizes for frequency, not for meaning.  That gap is where a surprising share of model weirdness lives.

Remember two things from this Part.  A tokenizer's vocabulary is learned by counting, so frequent pairs become single tokens and rare words break into pieces.  Whatever the tokenizer destroys (letters inside a token, digit groupings) is invisible to the model no matter how well it reasons.

### Questions to Work Through

1.  Why do frequent character pairs deserve dedicated tokens?  Connect your answer to compression.

   *Hint:* If "th" appears in thousands of words, how many fewer tokens do you need to store a typical English text if "th" is one token instead of two?  Think of it as a ZIP file for language.

2.  Before you run the tiktoken cell, predict which is more tokens: "internationalization" or "the cat sat on the mat".  Justify your prediction, then run the cell (add the second phrase to the list) and check.

   *Hint:* "internationalization" is a single rare word, and rare words shatter into many subword pieces.  The second phrase has six common words.  Estimate both with the three-quarters-of-a-word rule.

---

## 2.  Embeddings: Meaning as Geometry

An embedding is a list of numbers that stands for the meaning of a piece of text, placed so that similar meanings land close together.  Once text is tokenized, the model still needs a way to know that "dog" and "puppy" are related while "dog" and "tax return" are not.  The solution is to map every piece of text to a point in a high-dimensional space: a map where meaning is location.  Words with similar meanings land near each other, the way cities in the same region are physically close.  The map analogy stops at the number of axes: a road map has two, and an embedding space has hundreds.  This one idea powers search engines, recommendation systems, and the retrieval pipelines your agents will use in the *Retrieval-Augmented Generation with Chroma* activity.

Formally, an embedding maps a token, sentence, or document to a vector $$\mathbf{v} \in \mathbb{R}^d$$, a list of $$d$$ numbers with $$d$$ commonly between 384 and 4096, such that semantically similar texts map to nearby vectors.  The standard similarity measure is **cosine similarity**, the cosine of the angle between two vectors:

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert}
$$

The numerator is the dot product: multiply matching entries and add the products.  Each $$\lVert \mathbf{a} \rVert$$ in the denominator is a vector's length (its norm).  The result ranges from $$-1$$ (opposite meaning) through $$0$$ (unrelated) to $$1$$ (identical direction, so identical meaning).  Embedding models are trained so that paraphrases score high and unrelated texts score low.  This single idea powers semantic search, clustering, and recommendation.

> **Common Misconception:** A high cosine similarity score does NOT mean the two sentences share the same words, that one logically implies the other, or that either is factually true.  It only means the embedding model placed them in a similar direction in meaning-space; they are topically close.  Two completely wrong sentences about the same topic can score 0.95 with each other.

Remember two things from this section.  An embedding is a point, and cosine similarity measures the angle between two points as seen from the origin, ignoring their lengths.  Similar direction means similar topic, and nothing more.

### Questions to Work Through

3.  Let $$\mathbf{a} = (1, 2, 2)$$ stand for "the dog ran" and $$\mathbf{b} = (2, 4, 4)$$ stand for "a dog was running", so $$\mathbf{b} = 2\mathbf{a}$$ exactly.  What does cosine similarity say about vectors that differ only in magnitude, and why is that a desirable property for comparing a short query with a long document?

   *Hint:* A short question like "parking rules?" and a long parking policy document might have similar meanings but very different lengths.  Should length penalize similarity?  What does the division by the norms accomplish?

Check yourself.  Two sentences receive embeddings with cosine similarity 0.92.  The best interpretation is:

- The sentences share at least 92 percent of their words
- The embedding model places them in nearly the same direction, suggesting closely related meaning
- One sentence logically entails the other
- Both sentences are factually true

<details markdown="1"><summary>Answer</summary>

The embedding model places them in nearly the same direction, suggesting closely related meaning.  Cosine similarity says nothing about shared words, entailment, or truth.

</details>

---

## 2b.  When One Vector Is Not Enough: Attention

Section 2 rests on an assumption worth challenging: that a word *has* an embedding.  One word, one vector, looked up in a table.

Consider "bank."

> The **bank** was steep and muddy.
> The **bank** approved the loan.

Same five letters, two unrelated meanings.  A lookup table gives them one vector, which must therefore be wrong at least half the time.  Something has to let the surrounding words change what a word means, and that something is attention.  It is the single idea that separates the models you are using this semester from the word-vector methods that came before them.

### The Idea Before the Arithmetic

Each token gets three vectors instead of one, playing three roles:

- a **query** $$\mathbf{q}$$: *what am I looking for?*
- a **key** $$\mathbf{k}$$: *what do I offer as a match?*
- a **value** $$\mathbf{v}$$: *what content do I contribute if I am chosen?*

Think of a library search.  Your search term is the query.  The index cards are the keys.  The books are the values.  The analogy stops at the last step: a library search hands you one book, and attention hands you a blend of every book, weighted by how well each index card matched.

To find out how relevant token $$j$$ is to token $$i$$, take the dot product $$\mathbf{q}_i \cdot \mathbf{k}_j$$, the same operation as the numerator of cosine similarity in Section 2.  Run those relevance scores through softmax (raise $$e$$ to each score, then divide by the total) so they become weights that sum to 1.  Then build the token's new meaning as a weighted blend of everyone's values.

That is the whole mechanism, and it is written compactly as:

$$
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right) V
$$

where $$Q$$, $$K$$, and $$V$$ stack every token's query, key, and value into matrices, and $$\sqrt{d_k}$$ (the square root of the vector length) divides the scores to keep them from growing large enough to make softmax saturate.  A transformer stacks this operation dozens of times, in parallel "heads," with small neural networks in between.  That is the architecture.  The companion article has you do one layer of it by hand with three tokens, and the final Part of this article runs it inside a complete request.

> **Common Misconception:** "Attention means the model is focusing, or paying attention, the way a person does."  The name is a metaphor for a weighted average, nothing more.  Every token attends to every other token every time, with a weight; none of them is ignored, and none of them is being concentrated on.  Dot products, a softmax, and a weighted sum are the entire phenomenon.

Remember two things from this section.  Attention replaces one fixed vector per word with a blend that depends on the neighbors, so "bank" next to "loan" ends up nearer the financial sense.  The blend weights come from query-key dot products passed through softmax.

### Questions to Work Through

4.  A token's query is scored against every key, including its own.  Why is it useful for a token to attend to itself at all, rather than only to its neighbors?

5.  Compare the cosine-similarity formula in Section 2 with the attention relevance score $$\mathbf{q}_i \cdot \mathbf{k}_j$$.  Both start with a dot product.  Name the one thing cosine does that attention's relevance score does not, and suggest why attention might not want it.

   *Hint:* Cosine divides by the two norms.  What is that division for, and what would you lose if a token's "loudness" could no longer affect how much others attend to it?

Check yourself.  In one attention step for the sentence "river bank loan", which quantity decides *how much* `bank` is influenced by `loan`?

- The value vector $$\mathbf{v}_{\text{loan}}$$
- The softmax weight computed from the dot product of `bank`'s query with `loan`'s key
- The order of the tokens in the sentence
- The dimension $$d_k$$

<details markdown="1"><summary>Answer</summary>

The softmax weight computed from the dot product of `bank`'s query with `loan`'s key.  The value vector is *what* `loan` contributes; the weight is *how much* of it gets blended in.

</details>

---

## 2c.  What This Arithmetic Already Costs You

The attention mechanism is not a mathematical curiosity.  It sets the budget you have to work with for the rest of the semester, and three consequences of it will shape every agent you build.

**The context window is the attention span, literally.**  Attention compares every token with every other token, so $$n$$ tokens cost $$n^2$$ scores; doubling the context quadruples the work.  That is why context windows are finite, why long prompts are slow on your laptop, and why the *small context window principle* we adopt in *Memory and the Small Context Window Principle* is a computational fact rather than a matter of taste.  Grow a prompt from 2,000 tokens to 8,000 and the attention work per layer grows by a factor of 16, because $$8000^2 / 2000^2 = 16$$.

Position matters, and not evenly.  Models attend most reliably to the beginning and the end of a long context and are measurably worse at material buried in the middle, an effect usually called *lost in the middle*.  This is why we put an agent's standing instructions and the current question at the edges of a prompt, with retrieved evidence in between, once we start building retrieval pipelines.

Depth is fixed, so the number of dependent steps is fixed.  Attention lets any token look at any other token, which is a powerful thing and is not the same as computing.  A stack of layers gives the model a set number of operations that can depend on each other before it has to commit to a token, and that number was frozen when the model was trained.  A problem needing more dependent steps than the stack has does not get more; the model answers anyway.  Hold onto this, because *Why Different Answers Every Time?* shows you the one way out of it.  The way out is not a bigger context or better attention.  It is the model writing intermediate results into its own context and reading them back on the next pass.

> **Common Misconception: "More context is always better."**  Three things say otherwise, and you have now seen all three.  The cost is quadratic, so a longer prompt is not a free improvement.  The middle of a long prompt is the least reliable part of it.  And every extra token competes for the same finite attention budget, so filler dilutes the signal from the tokens that mattered.  Retrieve only what is relevant, place it deliberately, and keep prompts as short as the task allows.

Remember two things from this section.  Attention cost grows with the square of the prompt length, and the middle of a long prompt is the part the model reads worst.  Both facts argue for short, deliberately arranged prompts.

### Questions to Work Through

6.  This section states that growing a prompt from 2,000 tokens to 8,000 multiplies the attention work per layer by 16.  Show where 16 comes from, then connect that number to a cost or latency you have already noticed on your own machine.

---

# Part II: Semantic Search in Code

This Part uses a real embedding model (a neural network that converts text to vectors) to build a tiny search engine that finds documents by meaning rather than by matching exact words.  This is the retrieval foundation that your agents will use in the next module to access documents they were never trained on.

## 3.  A Search Engine in Twenty Lines

Ollama serves embedding models too.  The code below embeds a handful of campus FAQ sentences and searches them by meaning, not keywords.  It first calls the embedding model to convert each document to a vector (a list of numbers representing its meaning), stores all the vectors in a matrix, and then finds the closest match to any new query using cosine similarity.

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

Read the code in three pieces.  `embed` sends one string to Ollama and returns its vector, or a zero vector if the call fails.  `D` stacks the five document vectors as rows of a matrix.  `search` embeds the query, computes cosine similarity against every row at once, and prints the top `k` matches with their scores.

Remember two things from this Part.  Semantic search is cosine similarity between a query vector and a matrix of document vectors, and nothing else.  The "understanding" is in the embedding model; the search code is arithmetic.

### Questions to Work Through

7.  Neither query shares a single content word with its best match.  Identify exactly which line of code performed the "understanding," and what it computes mathematically.

   *Hint:* Look at the line `sims = D @ q / ...`.  `D @ q` is a matrix-vector product; what does each entry of the result represent?  Which formula from Section 2 does this implement?

8.  Craft a query that retrieves the *wrong* document with high confidence.  What does the failure reveal about what embeddings capture and what they miss (negation, numbers, proper names)?

   *Hint:* Try something like "the library is NOT open on weekends"; does the negation change the retrieved document?  Try a query with a specific number that does not appear in any document.  What does that tell you about what the embedding "remembers"?

9.  The matrix-vector product `D @ q` computes all similarities at once.  For one million documents, what becomes expensive, and what data structure might help?  (This previews vector databases.)

   *Hint:* With one million documents each holding 768 numbers, how many multiplications does one search require?  (Multiply 1,000,000 by 768.)  What if you could organize the vectors spatially so you only had to check a fraction of them?

---

# Part III: Synthesis and Practice

These exercises extend the search engine to reveal the geometry of meaning: building similarity matrices, testing the classic king minus man plus woman equals queen analogy, and auditing how token counts constrain what you can fit in an agent's context window.

## Exercises

1.  *Similarity matrix.*  Embed eight sentences of your choosing spanning two obvious topics.  Compute the full 8x8 cosine similarity matrix, render it as a heatmap, and verify that the block structure matches the topics.

   - *What to do:* Choose 4 sentences about Topic A (e.g., dining) and 4 about Topic B (e.g., parking).  Call `embed()` on each, build the 8x8 matrix using the cosine formula, and visualize with `matplotlib` using `imshow`.
   - *Starter hint:* `matrix[i][j] = np.dot(vecs[i], vecs[j]) / (np.linalg.norm(vecs[i]) * np.linalg.norm(vecs[j]))`.  For the heatmap: `plt.imshow(matrix, vmin=-1, vmax=1, cmap='coolwarm')`.
   - *You've succeeded when:* The top-left 4x4 block and bottom-right 4x4 block show high similarity (warm colors), while the off-diagonal blocks show low similarity (cool colors).

2.  *Analogy probe.*  Test the classic claim that embedding arithmetic captures analogy: compare $$\cos(\text{embed}(\text{"king"}) - \text{embed}(\text{"man"}) + \text{embed}(\text{"woman"}),\ \text{embed}(\text{"queen"}))$$ against unrelated words.  Report whether your sentence-level model exhibits the effect, and hypothesize why or why not.

   - *What to do:* Compute the four embeddings, do the vector arithmetic, then compare the result to `embed("queen")` using cosine similarity.  Also compare it to `embed("table")` as a baseline.
   - *Starter hint:* `analogy_vec = embed("king") - embed("man") + embed("woman")`.  Then `cosine(analogy_vec, embed("queen"))` vs `cosine(analogy_vec, embed("table"))`.
   - *You've succeeded when:* You can report the two similarity scores and explain why sentence-level models may show a weaker analogy effect than word-level models like Word2Vec.

3.  *Token budget audit.*  Estimate the token count of your team charter document at four characters per token, then explain how that figure constrains stuffing it into an agent's prompt every turn.  (We address this properly in the memory module.)

   - *What to do:* Count the total characters in your charter (or any document of at least 500 words), divide by 4 to estimate tokens, and compare that figure to a 4,000-token context window.
   - *Starter hint:* `token_estimate = len(document_text) / 4`.  If your context window is 4,000 tokens and your system prompt costs 300 tokens and each user turn costs about 50 tokens, how many turns can fit alongside the full charter?
   - *You've succeeded when:* You can state the charter's token estimate, the percentage of the context window it occupies, and one concrete consequence for an agent that carries the full charter every turn.

---

## Reflection Prompt

*Personal:* Think about a time you searched for something online and the search engine found exactly what you meant even though you used different words than the page used.  How does that experience connect to what embeddings are doing mathematically?

*Technical:* In your notebook: meaning, for an embedding model, is location in a high-dimensional space learned from co-occurrence patterns in text.  Name one aspect of meaning in your favorite discipline (a poem's irony, a proof's elegance, a primary source's provenance) that you suspect geometry cannot capture, and explain why co-occurrence statistics would fail to encode it.

*Societal:* Embedding models encode the statistical patterns of whatever text they were trained on, including that text's biases.  If a job-application screening system uses embeddings to find "similar" resumes to high-performing employees, what kinds of historical bias might get amplified?  Who is harmed, and what safeguard would you design?

---

# Part IV: Anatomy of an LLM Request

Nothing in Parts I through III assumes what follows.  It is here because at some point you will want to see the whole path at once: one prompt taken end to end by hand, from tokenizing through embedding, attention, the feed-forward block, sampling, loss, and the weight update.  The earlier Parts took that path in pieces.  This Part stitches the pieces back together.  Come back to it when the pieces stop feeling separate.

## Key Concepts for This Part

| Term | Plain-English Definition | Where It Appears in This Part |
|------|--------------------------|-------------------------------|
| **Token** | A chunk of text mapped to an integer id from a fixed vocabulary | "the" -> id 0, "cat" -> id 1 |
| **Embedding** | The learned vector a token id looks up, the model's numeric "meaning" for that token | id 1 ("cat") -> $$(0, 1)$$ |
| **Positional encoding** | A vector added to an embedding to tell the model *where* in the sequence the token sits | position 1 adds $$(1, 0)$$ |
| **Q/K/V projection** | Three learned matrices $$W_Q, W_K, W_V$$ that turn each token vector into a query, a key, and a value | $$q = x\,W_Q$$, and $$q,k,v$$ all differ from $$x$$ |
| **Attention score** | The dot product of one token's query with another token's key, "how relevant is that token to me?" | key times query $$= 2$$ and $$3$$ |
| **Softmax** | Turns a vector of scores into a probability distribution (positive, sums to 1) | scores $$\to (0.3302, 0.6698)$$ |
| **Context vector** | The attention-weighted sum of value vectors, one token's view of the whole sequence so far | $$(0.6698, 1.0)$$ |
| **Feed-forward network (FFN)** | A small per-token neural network (linear -> ReLU) applied after attention | $$(0.6698,1.0) \to (1.6698, 1.0)$$ |
| **Unembedding / logits** | A matrix that scores the final vector against every vocabulary token, producing one logit per token | 5 logits, one per word |
| **Cross-entropy loss** | How surprised the model is by the correct next token: $$-\log p(\text{target})$$ | $$-\log(0.5791) = 0.5464$$ |
| **Gradient descent step** | Nudge a weight opposite its gradient so the loss goes down | one entry of $$W_U$$: $$1.0 \to 1.3514$$ |

Throughout we use 2-dimensional vectors and a 5-word vocabulary so the arithmetic fits on a napkin.  Real models use thousands of dimensions and vocabularies of 100,000+ tokens, but every operation is exactly the one you will do here, only larger.

---

## From Text to Vectors

This section turns the prompt into numbers, the only thing a neural network can process.

### Tokenize, Embed, and Add Position

Our toy vocabulary has five tokens, each with an integer id and a learned 2-D embedding:

| Token | id | Embedding |
|---|---|---|
| the | 0 | $$(1, 0)$$ |
| cat | 1 | $$(0, 1)$$ |
| sat | 2 | $$(1, 1)$$ |
| ran | 3 | $$(-1, 1)$$ |
| mat | 4 | $$(1, -1)$$ |

**Step 1: Tokenize.**  The prompt "the cat" becomes the id sequence $$[0, 1]$$.

**Step 2: Embed.**  Look up each id's row: "the" $$\to (1, 0)$$, "cat" $$\to (0, 1)$$.

**Step 3: Add positional encoding.**  Attention alone cannot tell "the cat" from "cat the," so we add a position vector.  Use $$\text{pos}_0 = (0,0)$$ and $$\text{pos}_1 = (1,0)$$:

$$
x_{\text{the}} = (1,0) + (0,0) = (1, 0) \qquad x_{\text{cat}} = (0,1) + (1,0) = (1, 1)
$$

These two vectors, $$x_{\text{the}} = (1,0)$$ and $$x_{\text{cat}} = (1,1)$$, are the model's input.  Every later stage operates on them.

### Questions to Work Through

10.  The tokens "the" and "cat" have embeddings $$(1,0)$$ and $$(0,1)$$, orthogonal vectors.  In one sentence, what would it mean geometrically if two tokens had *identical* embeddings, and why would that be a problem?

   *Hint:* Embeddings are the model's only handle on meaning.  If two different words map to the same vector, can any later stage ever tell them apart?

11.  We added position *after* embedding.  Show what $$x_{\text{cat}}$$ would be if "cat" appeared in position 0 instead of position 1.  Why does the model need this, given that attention (next section) treats its inputs as an unordered set?

   *Hint:* $$\text{pos}_0 = (0,0)$$.  Recompute $$(0,1) + \text{pos}_0$$.  If two orderings produced identical vectors, could the model ever distinguish "dog bites man" from "man bites dog"?

Check yourself.  Why does a transformer add a positional encoding to the token embedding before attention?

- To make the vectors longer so they carry more information
- Because attention itself is order-agnostic, so without position the model cannot tell "the cat" from "cat the"
- To convert the token id into a probability
- To reduce the size of the vocabulary

<details markdown="1"><summary>Answer</summary>

Because attention itself is order-agnostic, so without position the model cannot tell "the cat" from "cat the".

</details>

---

## Attention: Query, Key, Value, and the Weighted Sum

This section computes how the last token, "cat," gathers information from the tokens before it.  This is the mechanism at the center of every transformer.

### Project Each Token into a Query, a Key, and a Value

A token's input vector plays three different roles, so the model learns three matrices to produce three different views of it.  Using our (row-vector) convention $$q = x\,W_Q$$:

$$
W_Q = \begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix} \quad W_K = \begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix} \quad W_V = \begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}
$$

Apply them to each input vector.  For the query of "cat" ($$x_{\text{cat}} = (1,1)$$):

$$
q_{\text{cat}} = (1,1)\begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix} = (1\cdot 0 + 1\cdot 1,\; 1\cdot 1 + 1\cdot 0) = (1, 1)
$$

Doing this for all tokens and all three matrices:

| | query $$q$$ | key $$k$$ | value $$v$$ |
|---|---|---|---|
| the $$(1,0)$$ | $$(0, 1)$$ | $$(1, 1)$$ | $$(0, 1)$$ |
| cat $$(1,1)$$ | $$(1, 1)$$ | $$(1, 2)$$ | $$(1, 1)$$ |

Notice that $$q$$, $$k$$, and $$v$$ are all different from the input $$x$$ and from each other; that is the whole point of the projection.  The query asks "what am I looking for?"; the key advertises "what do I offer?"; the value is "what I contribute if attended to."

### Questions to Work Through

12.  Verify by hand that $$k_{\text{cat}} = (1, 2)$$ by multiplying $$x_{\text{cat}} = (1,1)$$ by $$W_K$$.  Show the two dot products.

   *Hint:* The first component is $$(1,1)$$ dotted with the first column of $$W_K$$, which is $$(1,0)$$.  The second uses the second column $$(1,1)$$.

13.  If $$W_Q$$, $$W_K$$, and $$W_V$$ were all the identity matrix, what would $$q$$, $$k$$, and $$v$$ equal?  Explain why that would waste the model's expressive power.

   *Hint:* The identity leaves a vector unchanged.  If all three roles were the same vector, could a token ever "look for" something different from what it "advertises"?

### Attention Scores, Softmax, and the Context Vector

The last token, "cat," now asks every token how relevant it is, by dotting its query with each key.  That includes itself: causal attention lets a token attend to itself and everything before it.

**Step 1: Scores.**  With $$q_{\text{cat}} = (1,1)$$:

$$
\text{score}_{\text{the}} = k_{\text{the}} \cdot q_{\text{cat}} = (1,1)\cdot(1,1) = 2 \qquad \text{score}_{\text{cat}} = k_{\text{cat}} \cdot q_{\text{cat}} = (1,2)\cdot(1,1) = 3
$$

**Step 2: Scale** by $$\sqrt{d_k} = \sqrt{2} \approx 1.4142$$ (this keeps scores from growing with dimension; see Section 2b):

$$
\frac{2}{\sqrt 2} = 1.4142 \qquad \frac{3}{\sqrt 2} = 2.1213
$$

**Step 3: Softmax** turns the two scaled scores into attention weights:

$$
e^{1.4142} = 4.1132, \quad e^{2.1213} = 8.3421, \quad \text{sum} = 12.4554
$$

$$
\alpha_{\text{the}} = \frac{4.1132}{12.4554} = 0.3302 \qquad \alpha_{\text{cat}} = \frac{8.3421}{12.4554} = 0.6698
$$

**Step 4: Weighted sum of values** gives the context vector for "cat":

$$
\text{context} = 0.3302\,(0,1) + 0.6698\,(1,1) = (0.6698,\; 0.3302 + 0.6698) = (0.6698,\; 1.0)
$$

The vector $$(0.6698, 1.0)$$ is "cat," now aware of the token before it.  That is the one vector attention produces, and it flows into the next section.

### Questions to Work Through

14.  "cat" put weight $$0.6698$$ on itself and $$0.3302$$ on "the."  Explain what it would mean if the attention weights had come out $$(0.5, 0.5)$$ instead.  What in the scores would have to be true?

   *Hint:* Equal softmax weights require equal scaled scores.  What would that say about how relevant "the" and "cat" are to the query?

15.  The scaled scores differ by about $$0.707$$, yet the softmax weights differ by roughly a factor of two ($$0.33$$ vs $$0.67$$).  Why does softmax exaggerate a modest gap in scores?

   *Hint:* Softmax exponentiates before normalizing.  What does $$e^x$$ do to a difference of $$0.707$$ in the exponent?

16.  This is where the $$O(n^2)$$ cost of context length comes from (see Section 2c and the *Memory and the Small Context Window Principle* activity).  With 2 tokens we computed 2 scores.  How many query-key scores would a 1,000-token prompt need for its last token, and for *all* tokens?

   *Hint:* The last token dots against all prior keys.  Summed over every token attending to every prior token, the total grows like $$n^2$$.

Check yourself.  The context vector $$(0.6698, 1.0)$$ for "cat" is computed as:

- The average of the query, key, and value vectors
- The token embedding of "cat" with its position removed
- The softmax-weighted sum of the value vectors, using attention weights from the query-key scores
- The largest of the two attention scores

<details markdown="1"><summary>Answer</summary>

The softmax-weighted sum of the value vectors, using attention weights from the query-key scores.

</details>

---

## From Vector to Token

This section turns the context vector into an actual next-word prediction.

### Feed-Forward, Logits, Softmax, Sample

**Step 1: Feed-forward network.**  After attention, each token passes through a small per-token network: a linear layer then a ReLU (which replaces negatives with 0).  With

$$
W_1 = \begin{bmatrix} 1 & 0 \\ 1 & 1 \end{bmatrix}, \quad b_1 = (0, 0), \qquad z = \text{context}\,W_1 + b_1
$$

$$
z = (0.6698\cdot 1 + 1.0\cdot 1,\; 0.6698\cdot 0 + 1.0\cdot 1) = (1.6698,\; 1.0)
$$

Both components here are positive, so $$h = \text{ReLU}(z) = (1.6698, 1.0)$$ passes through unchanged.  (For a case where ReLU clips a negative to zero, see the fully worked 2-2-1 network in [From Text Generation to a Neural Network]({{ site.baseurl }}/Tutorials/TextGenToNN).)

**Step 2: Unembedding to logits.**  A matrix $$W_U$$ (one row per vocabulary token, here reusing the embedding directions) scores $$h$$ against every token: $$\text{logit}_i = W_{U,i} \cdot h$$.

| Token | row of $$W_U$$ | logit $$= \text{row}\cdot(1.6698, 1.0)$$ |
|---|---|---|
| the | $$(1, 0)$$ | $$1.6698$$ |
| cat | $$(0, 1)$$ | $$1.0000$$ |
| **sat** | $$(1, 1)$$ | $$\mathbf{2.6698}$$ |
| ran | $$(-1, 1)$$ | $$-0.6698$$ |
| mat | $$(1, -1)$$ | $$0.6698$$ |

**Step 3: Softmax over the vocabulary** turns logits into next-token probabilities:

$$
e^{1.6698}=5.3109,\; e^{1.0}=2.7183,\; e^{2.6698}=14.4365,\; e^{-0.6698}=0.5118,\; e^{0.6698}=1.9538
$$

The sum is $$24.9313$$, giving:

| the | cat | **sat** | ran | mat |
|---|---|---|---|---|
| $$0.2130$$ | $$0.1090$$ | $$\mathbf{0.5791}$$ | $$0.0205$$ | $$0.0784$$ |

**Step 4: Sample.**  At temperature 0 (greedy) the model emits the argmax: "sat."  The full request "the cat" -> "sat" is complete.  (Temperature and top-p reshape this distribution before sampling; see the *Why Different Answers Every Time?  Sampling, Temperature, and Generation* activity.)

> **Common Misconception:** It is tempting to picture the model "looking up" the answer to "the cat" in some stored table of sentences.  It does no such thing.  There is no sentence "the cat sat" stored anywhere.  The model holds only weights: the embedding rows, the projection matrices $$W_Q, W_K, W_V$$, the FFN weights, and the unembedding $$W_U$$.  Given "the cat," it *computes* a fresh probability distribution over its entire vocabulary every single time, through exactly the matrix operations above.  "sat" is not retrieved; it is the token that wins an arithmetic competition.

### Questions to Work Through

17.  "sat" won with probability $$0.5791$$, but "the" had a healthy $$0.2130$$.  At a high temperature, roughly what happens to the gap between these two, and how could that change which token is sampled?

   *Hint:* Temperature divides the logits before softmax.  Dividing by a number bigger than 1 flattens the distribution; does that make an upset more or less likely?

18.  The unembedding gave "sat" the highest logit because its direction $$(1,1)$$ aligns best with $$h = (1.6698, 1.0)$$.  Which token was *least* likely, and what about its direction explains that?

   *Hint:* Look for the row whose dot product with $$(1.6698, 1.0)$$ is most negative.  Which direction points "against" $$h$$?

Check yourself.  The five logits are converted into the five next-token probabilities by:

- Dividing each logit by the number of tokens
- Applying softmax across the whole vocabulary so the values are positive and sum to 1
- Keeping only the largest logit and setting the rest to 0
- Multiplying each logit by its embedding

<details markdown="1"><summary>Answer</summary>

Applying softmax across the whole vocabulary so the values are positive and sum to 1.

</details>

---

## How the Weights Got Their Values

Every number above (the embeddings, the projection matrices, the unembedding) started as random noise and was learned.  This section takes one step of that learning, so you can see how a weight changes.

### Loss, Gradient, and One Step of Descent

Suppose the correct next token really is "sat."  During training we ask: how surprised was the model?  That is the **cross-entropy loss**, the negative log probability of the true token:

$$
L = -\log p(\text{sat}) = -\log(0.5791) = 0.5464
$$

Lower is better; a perfect model would put probability 1 on "sat" for a loss of 0.  To improve, we nudge each weight in the direction that reduces $$L$$.  A convenient fact about cross-entropy after softmax is that the gradient of the loss with respect to each logit is

$$
\frac{\partial L}{\partial \text{logit}_i} = p_i - y_i
$$

where $$y_i = 1$$ for the true token and $$0$$ otherwise.  For "sat": $$p_{\text{sat}} - 1 = 0.5791 - 1 = -0.4209$$ (negative, meaning we should *raise* this logit).

Now pick one weight to update: the first entry of the "sat" row of the unembedding, $$W_U[\text{sat},0]$$, currently $$1.0$$.  Since $$\text{logit}_{\text{sat}} = W_U[\text{sat}] \cdot h$$, the chain rule gives

$$
\frac{\partial L}{\partial W_U[\text{sat},0]} = (p_{\text{sat}} - 1)\cdot h_0 = (-0.4209)(1.6698) = -0.7029
$$

Take a gradient-descent step (learning rate $$\eta = 0.5$$), moving *opposite* the gradient:

$$
W_U[\text{sat},0] \leftarrow 1.0 - 0.5\,(-0.7029) = 1.0 + 0.3514 = 1.3514
$$

Did it help?  Recompute that one logit: $$\text{logit}_{\text{sat}} = 1.3514\cdot 1.6698 + 1.0\cdot 1.0 = 3.2566$$ (up from $$2.6698$$).  Re-running softmax, $$p_{\text{sat}}$$ rises from $$0.5791$$ to $$0.7121$$, and the loss drops from $$0.5464$$ to $$0.3395$$.  One weight, one step, and the model is measurably less surprised by "sat."  Training is this same step, repeated across every weight and billions of examples.

### Questions to Work Through

19.  The gradient $$p_i - y_i$$ for the true token "sat" was negative ($$-0.4209$$), while for a wrong token like "the" it would be positive ($$+0.2130$$).  Explain how the sign tells gradient descent to *raise* the correct token's logit but *lower* a wrong token's.

   *Hint:* Gradient descent moves opposite the gradient.  A negative gradient means subtracting a negative, which raises the weight.  What does a positive gradient do?

20.  We used learning rate $$\eta = 0.5$$.  Predict qualitatively what happens to $$W_U[\text{sat},0]$$ and the loss if $$\eta$$ were enormous, say $$50$$.  Why do practitioners keep the learning rate small?

   *Hint:* The step size is $$\eta$$ times the gradient.  A giant step can overshoot the minimum entirely; the loss can go *up*.  What is the risk of stepping too far?

21.  We updated only one of the ten-plus weights in this model.  If we instead updated *every* weight by its own gradient in the same step, would the loss drop by more or less than the $$0.5464 \to 0.3395$$ we saw?  Why?

   *Hint:* Each weight's update independently reduces the loss (to first order).  What happens when many small improvements combine?

Check yourself.  After one gradient-descent step on $$W_U[\text{sat},0]$$, the loss went from $$0.5464$$ to $$0.3395$$.  This happened because:

- The model looked up the correct answer and memorized it
- The weight moved opposite its gradient, raising the "sat" logit and thus $$p(\text{sat})$$, which lowers $$-\log p(\text{sat})$$
- Softmax was disabled after training
- The learning rate was set to zero

<details markdown="1"><summary>Answer</summary>

The weight moved opposite its gradient, raising the "sat" logit and thus $$p(\text{sat})$$, which lowers $$-\log p(\text{sat})$$.

</details>

---

### Code Cell: Reproduce Every Number

The cell below runs the entire request (embed, project, attend, feed-forward, unembed, softmax, sample) and then the single training step, printing each intermediate value.  Compare every line to your by-hand work; they should match to rounding.  It also does a numerical gradient check: it perturbs $$W_U[\text{sat},0]$$ slightly and confirms the measured slope of the loss equals the analytic gradient $$-0.7029$$.

> **Predict first.**  This cell recomputes every number in the walkthrough above.  Pick any three of them from your own paper trace, write them down, and check those three against the output rather than skimming the whole thing.  Three numbers you verified are worth more than a page you nodded at.

This cell runs in your browser, so there is nothing to install.  Change the numbers and run it again as often as you like.

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
{% include pyrun.html %}

---

### Exercises

**Exercise 1: Change the prompt to "the mat."**

- *What to do*: Keep every matrix the same, but start from "the mat" instead of "the cat."  Recompute $$x_{\text{mat}}$$ (remember position 1 adds $$(1,0)$$), then $$q_{\text{mat}}, k$$, the attention scores against both tokens, the context vector, the FFN output, and the five logits.  Which token does the model predict now?
- *Starter hint*: $$x_{\text{mat}} = (1,-1) + (1,0) = (2,-1)$$.  Push it through exactly the steps in the two sections above.  You can check yourself by editing `E` or the input in the code cell.
- *You've succeeded when*: You have a full by-hand trace ending in a predicted token, and the code cell confirms your logits.

**Exercise 2: Make the model *more* confident in "sat."**

- *What to do*: Instead of updating only $$W_U[\text{sat},0]$$, also update $$W_U[\text{sat},1]$$ by one gradient step (its gradient is $$(p_{\text{sat}}-1)\cdot h_1$$).  Recompute $$\text{logit}_{\text{sat}}$$, $$p(\text{sat})$$, and the loss after updating *both* entries.  Did the loss drop more than updating one weight did?
- *Starter hint*: $$h_1 = 1.0$$, so the second gradient is $$(-0.4209)(1.0) = -0.4209$$.  Update both entries of the "sat" row, then recompute $$\text{logit}_{\text{sat}} = W_U[\text{sat}]\cdot h$$.
- *You've succeeded when*: You can state the new loss and explain, in one sentence, why updating more weights reduced it further.

**Exercise 3: Break position and observe.**

- *What to do*: Set both positional encodings to $$(0,0)$$ so "the cat" and "cat the" become indistinguishable to attention.  Recompute the context vector for the last token under both orderings and show they are now identical.  Explain in two sentences what capability the model has lost.
- *Starter hint*: With $$\text{pos}_0 = \text{pos}_1 = (0,0)$$, the input vectors depend only on which words are present, not their order.  Compute the last token's context for "the cat" and for "cat the."
- *You've succeeded when*: You have shown the two context vectors are equal and connected that to why positional encodings exist.

---

### Reflection Prompt

**Personal**: Before this Part, "the model predicts the next token" may have felt like a trick or a lookup.  Now that you have carried one prompt through every matrix multiply by hand, has your mental picture changed?  Which single stage most changed how you think about what a language model *is*?

**Technical**: Every stage here was a matrix multiply followed by a simple nonlinearity (softmax or ReLU).  In your notebook, describe how the *same five stages* scale to a real model with thousands of dimensions and a 100,000-token vocabulary.  What stays exactly the same, and what only changes in size?

**Societal**: You saw that the model stores no sentences, only weights it computes from.  Yet those weights were *learned from human text* whose patterns, biases, and gaps are baked into the embeddings and projection matrices you multiplied.  If "sat" won an arithmetic competition decided by learned weights, what does that imply about who is responsible for a model's outputs, and about the data those weights were trained on?

---

### Going Deeper: The Full $$QK^\top$$ Matrix, By Hand

Section 2b described one row of attention: the query for "bank" in the sentence "river bank loan."  The companion article computes that row by hand and then asks you to do "river."  Here is the whole matrix at once, because seeing all three rows together is what makes the mechanism click: attention is not a special operation applied to one token.  It is the same operation applied to every token in parallel.

Queries $$\mathbf{q}$$: river $$(1,0)$$, bank $$(1,1)$$, loan $$(1,1)$$.
Keys $$\mathbf{k}$$: river $$(1,0)$$, bank $$(0,1)$$, loan $$(1,1)$$.
Values $$\mathbf{v}$$: river $$(1,1)$$, bank $$(2,0)$$, loan $$(0,2)$$.

**Raw scores $$QK^\top$$** (each cell is $$\mathbf{q}_{\text{row}} \cdot \mathbf{k}_{\text{col}}$$):

| $$\mathbf{q} \downarrow$$ / $$\mathbf{k} \rightarrow$$ | river | bank | loan |
|---|---|---|---|
| **river** | 1 | 0 | 1 |
| **bank** | 1 | 1 | 2 |
| **loan** | 1 | 1 | 2 |

**Scaled by $$\sqrt{d_k} = \sqrt{2} \approx 1.414$$:**

| | river | bank | loan |
|---|---|---|---|
| **river** | 0.71 | 0.00 | 0.71 |
| **bank** | 0.71 | 0.71 | 1.41 |
| **loan** | 0.71 | 0.71 | 1.41 |

**Softmax, row by row** (each row sums to 1; that is what makes it a distribution over "where do I look"):

| | river | bank | loan | -> new vector |
|---|---|---|---|---|
| **river** | 0.40 | 0.20 | 0.40 | $$(0.80,\; 1.20)$$ |
| **bank** | 0.25 | 0.25 | 0.50 | $$(0.74,\; 1.26)$$ |
| **loan** | 0.25 | 0.25 | 0.50 | $$(0.74,\; 1.26)$$ |

Check the "river" row: $$e^{0.71} = 2.03$$, $$e^{0} = 1.00$$, $$e^{0.71} = 2.03$$, sum $$= 5.06$$, so weights $$2.03/5.06 = 0.40$$, $$1.00/5.06 = 0.20$$, $$0.40$$.  Then $$0.40(1,1) + 0.20(2,0) + 0.40(0,2) = (0.80, 1.20)$$.

Three things this matrix shows that a single row cannot.

1.  **The matrix is not symmetric.**  Row "river" gives "bank" a weight of 0.20, but row "bank" gives "river" 0.25.  Attention is *directional* ("what does A want from B" is a different question from "what does B want from A") because queries and keys are different projections.  This is the single most common misconception about attention.

2.  **"bank" and "loan" have identical rows.**  They started with identical query vectors $$(1,1)$$, so they attend identically and end up with the same output.  Nothing in this toy distinguishes them, which is exactly why real models use *many* attention heads with *different* learned projections, so that different heads can separate tokens this head cannot.

3.  **Every row is $$O(n)$$ work and there are $$n$$ rows.**  That is the $$O(n^2)$$ cost of self-attention, visible as the literal area of the table.  Double the context length and the table quadruples.  This is the whole economic argument for retrieval instead of pasting more text into the prompt.

---

## Further Reading

- [Sentence Prediction with BERT notebook]({{ site.baseurl }}/files/notebooks/Sentence_Prediction_with_BERT.ipynb), a runnable companion that uses BERT's masked-token predictions to see contextual embeddings in action.
- Tom Yeh.  *AI by Hand*, embedding and dot-product worksheets.
- Jay Alammar.  "The Illustrated Word2Vec" (online).  A visual introduction to embedding geometry.
- Reimers and Gurevych.  "Sentence-BERT." *EMNLP* (2019).  How sentence-level embeddings are trained.
