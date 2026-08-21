<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-tokensembeddings.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-tokensembeddings.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Tokens and Embeddings: How Agents Represent Meaning

In the *Connecting Agents to the World: MCP and APIs* activity our agents learned to reach external tools; now we open the hood for the first time, on demand: our agents will soon need to *search* documents by meaning, and that requires understanding **tokens** (how text becomes numbers) and **embeddings** (how meaning becomes geometry). We move from **tokenization $\rightarrow$ vectors $\rightarrow$ cosine similarity $\rightarrow$ computing semantic search by hand and in code**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Token** | The smallest chunk of text a model reads — roughly ¾ of a word on average, so "hamburger" is one token but "cheeseburger" might be two. Think of tokens as puzzle pieces that text is cut into. | `the` + `thing` -> 2 tokens using our toy rules |
| **Tokenizer** | The algorithm that cuts text into tokens, usually by starting with characters and merging frequent pairs (byte-pair encoding, or BPE). | Merging `t`+`h` -> `th`, then `th`+`e` -> `the` |
| **Embedding** | A list of numbers (a vector) that represents the *meaning* of a piece of text. It's like a GPS coordinate for meaning: similar meanings land near each other in this numerical space. | `"the dog ran"` -> `(1, 2, 2)` in a toy 3-D space |
| **Cosine Similarity** | A score from −1 to 1 measuring how similar two meaning-vectors are — specifically, the cosine of the angle between them. A score of 1 means "same direction = same meaning"; 0 means "unrelated." | `cos(a, b) = 1.0` when `b` is just a scaled copy of `a` |
| **Context Window** | The maximum number of tokens a model can read at once — its "working memory." A 4,000-token window holds roughly 3,000 English words. | A 4,000-token budget ≈ a 6-page double-spaced essay |
| **Semantic Search** | Finding documents by *meaning* rather than exact keyword match. Powered by comparing embedding vectors. | Querying "when can I get help from my professor" finds "Office hours for CS357 are Tuesday and Thursday mornings" |

---

# Part I: From Characters to Tokens

In this part, you will tokenize a short phrase by hand using a simplified rule set and discover why models struggle with tasks that seem trivially easy for humans — like counting the letters in a word. Understanding tokenization also explains why your chat budget is measured in tokens, not words or characters.

## 1. Tokenization

**Why this matters:** Every time you send a message to an AI, the first thing it does is chop your text into tokens — not words, not letters, but something in between. This matters because the model never sees the letter "e" inside "cheeseburger"; it sees whatever token the tokenizer carved out. That is why models struggle to count letters, why long numbers trip them up, and why your chat budget is measured in tokens rather than words. It's like the difference between reading a book word-by-word versus reading it one syllable at a time: the chunks you use change what patterns you notice.

**Models do not read words; they read tokens.** A tokenizer (the algorithm that cuts text into tokens) splits text into subword units drawn from a fixed vocabulary, typically built by byte-pair encoding (BPE — a compression algorithm that starts with individual characters and repeatedly merges the most frequent adjacent pair into a single token): begin with characters, repeatedly merge the most frequent adjacent pair, and stop at a target vocabulary size (often 30,000 to 200,000 entries). Common words become single tokens; rare words shatter into pieces, so "unhappiness" may become `un` + `happiness` and "Collegeville" may become three fragments.

**Tokenization explains odd model behaviors.** Counting letters in a word is hard when the model never sees individual letters; arithmetic on long numbers is hard when digits group unpredictably; and the *context window* (the model's working memory) is measured in tokens, which is why a 4,000-token budget holds roughly 3,000 English words. A rough rule of thumb: **1 token ≈ ¾ of an English word**, or about 4 characters.

---

## Model 1: Tokenize by Hand

Given the toy merge rules (`t`+`h`->`th`, `th`+`e`->`the`, `i`+`n`->`in`, `in`+`g`->`ing`), tokenize: "the thing".

### Critical Thinking Questions

1. Apply the merges step by step. How many tokens result? The Recorder shows the merge sequence.

   > *Hint: Start with every character as its own token: `t h e   t h i n g`. Then apply each merge rule left-to-right, in order, as many times as it applies. Count what remains.*

2. Why do frequent character pairs deserve dedicated tokens? Connect your answer to compression.

   > *Hint: If "th" appears in thousands of words, how many fewer tokens do you need to store a typical English text if "th" is one token instead of two? Think of it like a ZIP file for language.*

3. Predict which is more tokens: "internationalization" or "the cat sat on the mat". Justify before checking intuition against the class.

   > *Hint: "internationalization" is a single rare word — rare words shatter into many subword pieces. The second phrase has 6 common words. Which do you expect has more tokens? Try to estimate using the ¾-word rule.*

### Worked Example: where those merge rules came from (BPE, by hand)

The four merge rules above were handed to you. Real tokenizers *learn* them, and the learning rule is almost embarrassingly simple: **repeatedly merge the most frequent adjacent pair.** Here is the whole algorithm on a four-word corpus.

**Corpus** (word, frequency), with `</w>` marking a word end:

```
low </w>      5
lower </w>    2
newest </w>   6
widest </w>   3
```

**Step 0 — start from characters.** The initial vocabulary is every character: `l o w e r n s t i d </w>`.

```
l o w </w>            5
l o w e r </w>        2
n e w e s t </w>      6
w i d e s t </w>      3
```

**Merge 1.** Count every adjacent pair across the corpus, weighted by word frequency:

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

**Merge 2.** Recount. Now `es t` occurs 6 + 3 = **9**, the new maximum. Merge **`es t` -> `est`**:

```
l o w </w>            5
l o w e r </w>        2
n e w est </w>        6
w i d est </w>        3
```

**Merge 3.** Recount. `est </w>` occurs 9 times. Merge **`est </w>` -> `est</w>`**:

```
l o w </w>            5
l o w e r </w>        2
n e w est</w>         6
w i d est</w>         3
```

Three merges in, the learned merge table is `[es, est, est</w>]` — and notice what it discovered without being told: **`est` is an English suffix.** Nobody supplied a morphology rule. Frequency did it.

### Worked Example: encoding a word the tokenizer has never seen

This is the step that explains the failures the course keeps invoking. Take the learned merge table above, in order, and encode **`lowest`** — a word that never appeared in the training corpus.

| Stage | Sequence | Rule applied |
|---|---|---|
| start | `l o w e s t </w>` | split to characters |
| after merge 1 | `l o w es t </w>` | `e s` -> `es` |
| after merge 2 | `l o w est </w>` | `es t` -> `est` |
| after merge 3 | `l o w est</w>` | `est </w>` -> `est</w>` |
| final | **`l` `o` `w` `est</w>`** | no more rules apply |

Four tokens, and the model has never seen this word. It sees a prefix spelled out letter by letter plus a suffix it knows well.

**Now the punchline.** Ask a model how many `r`s are in *strawberry*. A production tokenizer splits it into something like `str` `aw` `berry` — three chunks, and **not one of them is a letter**. The model is not looking at `s-t-r-a-w-b-e-r-r-y`; it is looking at three opaque IDs. Counting letters inside a token is not a reasoning failure, it is an *input representation* failure: the information was destroyed before the model ever saw it. The same mechanism explains why models are shaky at rhyming, at reversing strings, and at arithmetic on long numbers.

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

Run it and compare against your hand trace. Two things to notice: common words are single tokens while rare ones shatter, and the split points frequently land *mid-morpheme* — the tokenizer optimizes for frequency, not for meaning. That gap is where a surprising share of model weirdness lives.


---

## 2. Embeddings: Meaning as Geometry

**Why this matters:** Once text is tokenized, the model still needs a way to understand that "dog" and "puppy" are related while "dog" and "tax return" are not. The solution is to map every piece of text to a point in a high-dimensional space — think of it as a map where meaning is location. Words with similar meanings land near each other on the map, just like cities in the same region are physically close. This single idea powers search engines, recommendation systems, and the retrieval pipelines our agents will use in the *Retrieval-Augmented Generation with Chroma* activity.

**An embedding maps a token, sentence, or document to a vector** $\mathbf{v} \in \mathbb{R}^d$ (with $d$ commonly 384 to 4096 — that is, a list of 384 to 4096 numbers) such that *semantically similar texts map to nearby vectors*. The standard similarity measure is **cosine similarity** (the cosine of the angle between two vectors):

$$
\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert}
$$

which ranges from $-1$ (opposite meaning) through $0$ (unrelated) to $1$ (identical direction/meaning). Embedding models are trained so that paraphrases score high and unrelated texts score low; this single idea powers semantic search, clustering, recommendation, and the retrieval pipelines our agents will use in the *Retrieval-Augmented Generation with Chroma* activity.

---

## Model 2: Cosine by Hand

Let $\mathbf{a} = (1, 2, 2)$ for "the dog ran" and $\mathbf{b} = (2, 4, 4)$ for "a dog was running", and $\mathbf{c} = (2, -1, 0)$ for "quarterly tax filing."

### Critical Thinking Questions

4. Compute $\cos(\mathbf{a}, \mathbf{b})$ and $\cos(\mathbf{a}, \mathbf{c})$ by hand (AI by Hand style: show the dot products and norms). The Recorder writes the full arithmetic.

   > *Hint: The dot product $\mathbf{a} \cdot \mathbf{b} = (1)(2) + (2)(4) + (2)(4)$. The norm $\lVert \mathbf{a} \rVert = \sqrt{1^2 + 2^2 + 2^2}$. Divide the dot product by the product of the two norms.*

5. $\mathbf{b} = 2\mathbf{a}$ exactly. What does cosine similarity say about vectors that differ only in magnitude, and why is that a desirable property for comparing a short query with a long document?

   > *Hint: A short question like "parking rules?" and a long parking policy document might have similar meanings but very different lengths. Should length penalize similarity? What does the division by the norms accomplish?*

> **Common Misconception:** A high cosine similarity score does NOT mean the two sentences share the same words, that one logically implies the other, or that either is factually true. It only means the embedding model placed them in a similar *direction* in meaning-space — they are topically close. Two completely wrong sentences about the same topic can score 0.95 with each other.

Two sentences receive embeddings with cosine similarity 0.92. The best interpretation is:

[( )] The sentences share at least 92 percent of their words
[(X)] The embedding model places them in nearly the same direction, suggesting closely related meaning
[( )] One sentence logically entails the other
[( )] Both sentences are factually true

---

# Part II: Semantic Search in Code

In this part, you will use a real embedding model (a neural network that converts text to vectors) to build a tiny search engine that finds documents by meaning rather than by matching exact words. This is the retrieval foundation that your agents will use in the next module to access documents they were never trained on.

## 3. A Search Engine in Twenty Lines

Ollama serves embedding models too. We embed a handful of campus FAQ sentences and search them by meaning, not keywords. The code below first calls the embedding model to convert each document to a vector (a list of numbers representing its meaning), stores all the vectors in a matrix, and then finds the closest match to any new query using cosine similarity.

---

## Code Cell

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

## Model 3: Probing the Geometry

### Critical Thinking Questions

6. Neither query shares a single content word with its best match. Identify exactly which line of code performed the "understanding," and what it computes mathematically.

   > *Hint: Look at the line `sims = D @ q / ...`. `D @ q` is a matrix-vector product — what does each entry of the result represent? Which earlier formula from Model 2 does this implement?*

7. Craft a query that retrieves the *wrong* document with high confidence. What does the failure reveal about what embeddings capture and what they miss (negation, numbers, proper names)?

   > *Hint: Try something like "the library is NOT open on weekends" — does the negation change the retrieved document? Try a query with a specific number that doesn't appear in any document. What does that tell you about what the embedding "remembers"?*

8. The matrix-vector product `D @ q` computes all similarities at once. For one million documents, what becomes expensive, and what data structure might help? (This previews vector databases.)

   > *Hint: With 1 million documents each having 768 numbers, how many multiplications does one search require? (Multiply 1,000,000 × 768.) What if you could organize the vectors spatially so you only had to check a fraction of them?*

---

# Part III: Synthesis and Practice

In this part, you will extend the search engine to reveal the geometry of meaning — building similarity matrices, testing the classic king-man+woman=queen analogy, and auditing how token counts constrain what you can fit in an agent's context window.

## 4. Exercises

1. *Similarity matrix.* Embed eight sentences of your team's choosing spanning two obvious topics. Compute the full 8×8 cosine similarity matrix, render it as a heatmap, and verify that the block structure matches the topics.

   - *What to do:* Choose 4 sentences about Topic A (e.g., dining) and 4 about Topic B (e.g., parking). Call `embed()` on each, build the 8×8 matrix using the cosine formula, and visualize with `matplotlib` using `imshow`.
   - *Starter hint:* `matrix[i][j] = np.dot(vecs[i], vecs[j]) / (np.linalg.norm(vecs[i]) * np.linalg.norm(vecs[j]))`. For the heatmap: `plt.imshow(matrix, vmin=-1, vmax=1, cmap='coolwarm')`.
   - *You've succeeded when:* The top-left 4×4 block and bottom-right 4×4 block show high similarity (warm colors), while the off-diagonal blocks show low similarity (cool colors).

2. *Analogy probe.* Test the classic claim that embedding arithmetic captures analogy: compare $\cos(\text{embed}(\text{"king"}) - \text{embed}(\text{"man"}) + \text{embed}(\text{"woman"}),\ \text{embed}(\text{"queen"}))$ against unrelated words. Report whether your sentence-level model exhibits the effect, and hypothesize why or why not.

   - *What to do:* Compute the four embeddings, do the vector arithmetic, then compare the result to `embed("queen")` using cosine similarity. Also compare it to `embed("table")` as a baseline.
   - *Starter hint:* `analogy_vec = embed("king") - embed("man") + embed("woman")`. Then `cosine(analogy_vec, embed("queen"))` vs `cosine(analogy_vec, embed("table"))`.
   - *You've succeeded when:* You can report the two similarity scores and explain why sentence-level models may show a weaker analogy effect than word-level models like Word2Vec.

3. *Token budget audit.* Estimate the token count of your team charter document at four characters per token, then explain how that figure constrains stuffing it into an agent's prompt every turn. (We address this properly in the memory module.)

   - *What to do:* Count the total characters in your charter (or any document of at least 500 words), divide by 4 to estimate tokens, and compare that figure to a 4,000-token context window.
   - *Starter hint:* `token_estimate = len(document_text) / 4`. If your context window is 4,000 tokens and your system prompt costs 300 tokens and each user turn costs ~50 tokens, how many turns can fit alongside the full charter?
   - *You've succeeded when:* You can state the charter's token estimate, the percentage of the context window it occupies, and one concrete consequence for an agent that carries the full charter every turn.

---

## Reflection Prompt

*Personal:* Think about a time you searched for something online and the search engine found exactly what you meant even though you used different words than the page used. How does that experience connect to what embeddings are doing mathematically?

*Technical:* In your notebook: meaning, for an embedding model, is location in a high-dimensional space learned from co-occurrence patterns in text. Name one aspect of meaning in your favorite discipline (a poem's irony, a proof's elegance, a primary source's provenance) that you suspect geometry cannot capture, and explain why co-occurrence statistics would fail to encode it.

*Societal:* Embedding models encode the statistical patterns of whatever text they were trained on, including that text's biases. If a job-application screening system uses embeddings to find "similar" resumes to high-performing employees, what kinds of historical bias might get amplified? Who is harmed, and what safeguard would you design?

---

## -> Coming Up Next

In the *Retrieval-Augmented Generation with Chroma* activity, we put embeddings to work at scale: instead of searching five sentences, we will index thousands of document chunks in a **vector database** (Chroma) and use that index to give our agents access to up-to-date information they were never trained on — a technique called Retrieval-Augmented Generation (RAG).

---

## 5. Further Reading

- [Sentence Prediction with BERT notebook](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/notebooks/Sentence_Prediction_with_BERT.ipynb) — a runnable companion that uses BERT's masked-token predictions to see contextual embeddings in action.
- Tom Yeh. *AI by Hand*, embedding and dot-product worksheets.
- Jay Alammar. "The Illustrated Word2Vec" (online). A visual introduction to embedding geometry.
- Reimers and Gurevych. "Sentence-BERT." *EMNLP* (2019). How sentence-level embeddings are trained.
