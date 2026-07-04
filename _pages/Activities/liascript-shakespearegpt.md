# Shakespeare GPT: How Language Models Learn to Write
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-shakespearegpt.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-shakespearegpt.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Shakespeare GPT: How Language Models Learn to Write

Every time a language model generates a word, it is doing something your phone's autocomplete has done for years — but at a scale and depth that produces startlingly human-like text. Today we build a character-level language model from scratch in Python, poke at the mechanisms that make it work and fail, and then compare it to a real local LLM running on your machine. The arc: **n-gram intuition → building the model → experimenting with temperature → comparing outputs with a local model → what "learning" actually means**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

Before diving in, orient yourself with the vocabulary you will use throughout today's activity.

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **n-gram** | A sequence of n items (characters, words) used to predict the next item based on what came before. A bigram uses the previous 1 item; a trigram uses the previous 2. | In "ROMEO", a bigram model records "R→O" once; a trigram records "RO→M" once. |
| **Character-level model** | A language model that treats individual characters (not words) as its basic units, allowing it to generate any text including made-up words. | Our Python model treats "R", "O", "M", "E", "O", ":" each as separate tokens. |
| **Probability distribution** | A set of probabilities over all possible next tokens that sum to 1.0 — the model's "belief" about what comes next. | After "th", the model might assign: "e"→0.55, "a"→0.18, "i"→0.14, others→0.13. |
| **Temperature** | A parameter that controls how peaked or flat the probability distribution is before sampling; low temperature = more predictable, high temperature = more random. | At T=0.3 the model almost always picks "e" after "th"; at T=2.0 it sometimes picks "x". |
| **Backoff** | When a model can't find the exact context in its training data, it "backs off" to a shorter context — e.g., falling back from trigram to bigram to unigram. | If "ZOM" never appears in the training text, the model falls back to any key ending in "M". |
| **Perplexity** | A measure of how surprised the model is by test data; lower perplexity = better predictions. | A trigram model trained on Shakespeare should have lower perplexity on Shakespeare than a bigram model does. |
| **Token** | The basic unit a model reads and writes; in a character-level model, every letter, space, and punctuation mark is a separate token. | The 10-character string "soft! wha" contains 10 tokens in a character-level model. |
| **Logit** | The raw score the model assigns to each possible next token before converting to probabilities with softmax. | A neural LM's output layer might produce logit 4.5 for "e" and -0.5 for "z" after "th". |

---

# Part I: The n-gram Intuition

## 1. Autocomplete by Counting

The simplest possible language model is a lookup table: scan through the training text, count which characters follow which character sequences, and store the counts. At generation time, look up the current context, turn the counts into probabilities, and sample the next character. This is an **n-gram model** — "n" refers to the total window size including the character you are predicting.

Think of building the model like a scribe who reads a book while keeping a tally sheet. Every time they see the letter "R" followed by "O" they make a tally mark in the "R → O" column. When asked to generate text, they roll a weighted die whose faces are labeled with all the characters they have seen after "R", with the most-tallied characters on the bigger faces.

**A concrete bigram table for "to be or not to be":**

| Context | Next character | Count | Probability |
|---------|----------------|-------|-------------|
| t | o | 2 | 2/3 ≈ 0.67 |
| t | (space) | 1 | 1/3 ≈ 0.33 |
| o | (space) | 3 | 3/4 = 0.75 |
| o | r | 1 | 1/4 = 0.25 |
| b | e | 2 | 1.00 |
| (space) | b | 2 | 2/4 = 0.50 |
| (space) | o | 1 | 1/4 = 0.25 |
| (space) | n | 1 | 1/4 = 0.25 |

Notice that every "b" in the training phrase is followed by "e," so the model is completely certain that "e" must come after "b" — a consequence of the tiny training set. On Shakespeare's full works this certainty evaporates because "b" appears in many more contexts ("by", "brave", "blood", …).

---

### Critical Thinking Questions

1. A bigram table for "to be or not to be" records contexts of length 1. A **trigram** table records contexts of length 2 (e.g., "to" → " ", "o " → "b", " b" → "e"). What does the trigram table add that the bigram table does not have? Why does this matter for generating coherent text?

   > *Hint: Trigrams track 2-character contexts instead of 1. In "to be or not to be", the trigram "to" appears before " " (a space) each time it appears. Track what comes after 2-character pairs vs. 1-character ones. Consider how knowing the previous two characters helps you predict whether a "t" is the start of "to" vs. the end of "not".*

2. [[MC]] A character-level bigram model trained on Shakespeare is asked to generate text starting from "Z". It has never seen "Z" in training. The most likely behavior is:
   - ( ) It generates the most common Shakespeare character ("e") regardless of context
   - (x) It crashes or backs off to a random character, since "Z" has no bigram entry
   - ( ) It generates "ounds" because it learned "Z" is usually followed by sounds
   - ( ) It refuses to generate anything

   > **⚠️ Common Misconception:** Students often assume the model has "knowledge" that lets it handle unseen inputs gracefully. An n-gram model is a lookup table — if the key doesn't exist, there is no entry. This is why modern neural language models vastly outperform n-gram models on rare or unseen contexts: they can *interpolate* from learned representations rather than failing on a lookup miss. The neural model has seen every character; the n-gram model has only seen the specific sequences that appeared in training.

3. The phrase "ROMEO:" appears many times in *Romeo and Juliet*. Would a bigram model trained only on that play generate "ROMEO:" correctly? What would it need to generate the word "JULIET" correctly, and why does the answer differ?

   > *Hint: "ROMEO:" requires the model to learn the 6 bigram transitions R→O, O→M, M→E, E→O, O→:. Each of these transitions must appear in training. "JULIET" requires J→U, U→L, L→I, I→E, E→T. Does the letter "J" appear frequently enough in Shakespeare's text that these transitions are well-estimated?*

---

# Part II: Build It in Python

## 2. From Tallies to Text

The code below implements the n-gram model in about 30 lines of Python. Read through it before running. Pay attention to:

- `build_ngram_model`: scans the text character by character, recording which character follows each context window of size n-1.
- `generate_text`: looks up the current context, applies temperature scaling to the counts, and samples. The **backoff** step handles contexts not seen in training.
- The temperature scaling line: `c ** (1.0 / temperature)`. At T=1 this is a no-op (counts unchanged). At T=0.3 it raises counts to the power 1/0.3 ≈ 3.3, which amplifies differences. At T=2.0 it raises counts to the 0.5 power (square root), which compresses differences.

---

## Code Cell

```python
from collections import defaultdict, Counter
import random

SHAKESPEARE_SAMPLE = """
ROMEO: But, soft! what light through yonder window breaks?
It is the east, and Juliet is the sun.
Arise, fair sun, and kill the envious moon,
Who is already sick and pale with grief,
That thou her maid art far more fair than she.
""" * 8  # repeat to get more training data

def build_ngram_model(text, n=3):
    model = defaultdict(Counter)
    for i in range(len(text) - n + 1):
        context = text[i:i+n-1]
        next_char = text[i+n-1]
        model[context][next_char] += 1
    return model

def generate_text(model, seed, length=200, temperature=1.0):
    n = len(list(model.keys())[0]) + 1
    output = seed
    context = seed[-(n-1):]

    for _ in range(length):
        if context not in model:
            # Backoff: find a key ending with same character
            fallbacks = [k for k in model if k.endswith(context[-1])]
            if not fallbacks:
                break
            context = random.choice(fallbacks)

        candidates = model[context]
        chars = list(candidates.keys())
        counts = list(candidates.values())

        # Temperature scaling
        scaled = [c ** (1.0 / temperature) for c in counts]
        total = sum(scaled)
        probs = [s / total for s in scaled]

        next_char = random.choices(chars, weights=probs)[0]
        output += next_char
        context = (context + next_char)[-(n-1):]

    return output

# Test all four modes
bigram_model = build_ngram_model(SHAKESPEARE_SAMPLE, n=2)
trigram_model = build_ngram_model(SHAKESPEARE_SAMPLE, n=3)

print("=== Bigram (T=1.0) ===")
print(generate_text(bigram_model, "RO", temperature=1.0))
print("\n=== Trigram (T=1.0) ===")
print(generate_text(trigram_model, "ROM", temperature=1.0))
print("\n=== Trigram (T=0.3, conservative) ===")
print(generate_text(trigram_model, "ROM", temperature=0.3))
print("\n=== Trigram (T=2.0, chaotic) ===")
print(generate_text(trigram_model, "ROM", temperature=2.0))
```

---

### Critical Thinking Questions

4. Run the bigram and trigram generators at T=1.0. The trigram output looks more "Shakespearean." Why? What does having a longer context (n=3 vs. n=2) allow the model to capture?

   > *Hint: A bigram model of "is the sun" sees "i→s", "s→ ", " →t", "t→h", "h→e", "e→ ", " →s", "s→u", "u→n". A trigram model sees "is→ ", "s →t", " t→h", "th→e", "he→ ", "e →s", " s→u", "su→n". How does tracking two-character contexts reduce the chance of generating nonsense sequences like "sts" or "ehe"?*

5. At T=0.3, the trigram model generates very similar text on every run. At T=2.0, it generates different text each time, often nonsensical. Explain the mechanism: what changes in the probability distribution when you raise or lower the temperature?

   > *Hint: Look at the temperature scaling step: `counts[i] ** (1/T)`. At T=0.3, the exponent is 1/0.3 ≈ 3.3 — raising counts to the 3rd power makes the winner MUCH more dominant over second place. If "e" has count 10 and "a" has count 2, at T=0.3 their scaled values are 10^3.3 ≈ 2000 vs. 2^3.3 ≈ 10. At T=2.0, the exponent is 0.5 — taking the square root of 10 gives 3.16 and of 2 gives 1.41, much closer together.*

6. [[MC]] Increasing n (from bigram to trigram to 10-gram) always improves the quality of generated text.
   - ( ) True — more context is always better
   - (x) False — at very high n, the model memorizes training examples and can't generalize
   - ( ) True, but only up to n=5
   - ( ) False — n-gram models always generate random text regardless of n

   > **⚠️ Common Misconception:** Students often expect that "more context" monotonically improves a statistical model. At very high n, most contexts appear only once or zero times in training data — the model has essentially memorized the training text verbatim. Generation then either exactly reproduces training sequences (when a context was seen) or breaks immediately into the backoff case (when it was not). The sweet spot for character-level n-gram models on literary text is typically n=4 to n=6.

7. Our backoff strategy chooses a random key that ends with the same last character. This is a crude approximation of what more sophisticated language models do. What information does this strategy throw away, and what would a smarter backoff do instead?

   > *Hint: The backoff ignores all but the last character of the context. A smarter strategy, called "Kneser-Ney smoothing," estimates how likely each next character is given progressively shorter suffixes of the context, and blends those estimates with interpolation weights. What contextual information is lost by our random-fallback approach?*

---

# Part III: Compare to a Real Local LLM

## 3. What a Million Parameters Buys You

Our n-gram model required no training — just counting. Its "knowledge" is entirely contained in the frequency tables, which can be inspected and modified directly. A local LLM like `llama3.2` or `mistral` encodes the same basic idea (predict the next token) but with hundreds of millions of parameters that were adjusted over billions of training examples.

Run the Shakespeare continuation prompt below through a local model via Ollama. Compare the outputs carefully.

---

## Code Cell

```python
import requests

SHAKESPEARE_PROMPT = """Continue the following passage in Shakespeare's style:

ROMEO: But, soft! what light through yonder window breaks?
It is the east, and Juliet is the sun.
Arise, fair"""

def query_local(prompt, model="llama3.2", temperature=1.0):
    try:
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False,
                  "options": {"temperature": temperature}},
            timeout=120)
        return r.json()["response"].strip()
    except Exception as e:
        print(f"[query_local] {e}")
        return ""

# Compare outputs at two temperatures
print("=== Local model, T=0.3 ===")
print(query_local(SHAKESPEARE_PROMPT, temperature=0.3))
print("\n=== Local model, T=1.0 ===")
print(query_local(SHAKESPEARE_PROMPT, temperature=1.0))

# Also run our n-gram model for side-by-side comparison
from collections import defaultdict, Counter
import random

SHAKESPEARE_SAMPLE = """
ROMEO: But, soft! what light through yonder window breaks?
It is the east, and Juliet is the sun.
Arise, fair sun, and kill the envious moon,
Who is already sick and pale with grief,
That thou her maid art far more fair than she.
""" * 8

def build_ngram_model(text, n=3):
    model = defaultdict(Counter)
    for i in range(len(text) - n + 1):
        context = text[i:i+n-1]
        next_char = text[i+n-1]
        model[context][next_char] += 1
    return model

def generate_text(model, seed, length=200, temperature=1.0):
    n = len(list(model.keys())[0]) + 1
    output = seed
    context = seed[-(n-1):]
    for _ in range(length):
        if context not in model:
            fallbacks = [k for k in model if k.endswith(context[-1])]
            if not fallbacks:
                break
            context = random.choice(fallbacks)
        candidates = model[context]
        chars = list(candidates.keys())
        counts = list(candidates.values())
        scaled = [c ** (1.0 / temperature) for c in counts]
        total = sum(scaled)
        probs = [s / total for s in scaled]
        next_char = random.choices(chars, weights=probs)[0]
        output += next_char
        context = (context + next_char)[-(n-1):]
    return output

trigram_model = build_ngram_model(SHAKESPEARE_SAMPLE, n=3)
print("\n=== n-gram trigram, T=1.0 ===")
print(generate_text(trigram_model, "Ari", temperature=1.0))
```

---

### Critical Thinking Questions

8. Compare the vocabulary of the n-gram output to the local model output. The local model can generate words that never appeared in the small training excerpt — the n-gram model cannot. Where does the local model's broader vocabulary come from?

   > *Hint: Our n-gram model was trained on the 8× repeated excerpt above — about 1,600 characters. The local model was trained on billions of tokens from books, web pages, and other sources. The n-gram model's vocabulary is physically bounded by the characters and sequences in those 1,600 characters.*

9. The local model maintains pronouns, verb tense, and iambic rhythm across multiple lines. The n-gram model breaks down after one or two "words" (which it does not even represent as words — just character sequences). What structural information does the n-gram model entirely lack?

   > *Hint: Our model has no concept of "word", "sentence", "line", or "speaker turn." It sees characters. The local model was trained to predict tokens (subwords) and learned from countless examples of dialogue, poetry, and plays that certain patterns follow certain others at the word and sentence level.*

10. [[MC]] Both the n-gram model and the local LLM pick the next token by sampling from a probability distribution. The key difference in HOW that distribution is computed is:
    - ( ) The LLM uses higher n (longer context) but the same counting approach
    - ( ) The LLM uses a different sampling method (beam search instead of random sampling)
    - (x) The LLM uses learned neural network weights that can interpolate over unseen contexts; the n-gram model uses a lookup table that fails on unseen keys
    - ( ) There is no meaningful difference — they are the same algorithm at different scales

11. Give the n-gram model the seed "ZZZ" — three characters that almost certainly never appear in Shakespeare. What happens? Then give the local model the prompt "Continue this Shakespearean text: ZZZ". What does the local model do, and why can it handle this where the n-gram model cannot?

    > *Hint: The n-gram model's backoff will fire immediately, since "ZZ" has no entry. The local model maps every possible sequence of characters to a position in its embedding space, and that space was learned from a huge corpus — so even "ZZZ" gets a representation it can reason from, even if it has never seen that exact sequence.*

---

# Part IV: Concept Synthesis

## 4. Pulling It Together

Both models convert context into a probability distribution over next tokens. The n-gram model does it by counting; the LLM does it by propagating input through hundreds of layers of learned matrix multiplications. The counting approach is fully interpretable (you can read the table) but brittle. The neural approach is opaque but generalizes.

### Critical Thinking Questions

12. A 5-gram model trained on Romeo and Juliet has a fixed character vocabulary drawn entirely from that play. What would happen if you gave it the prompt "Write a Python function"? What specifically would break first?

    > *Hint: The backtick character ` does not appear in Shakespeare. Neither does the underscore _. What happens in the `generate_text` function when the backoff fires and also fails — i.e., when even the fallback set is empty? Trace through the code.*

13. We used `random.choices(chars, weights=probs)` to sample the next character. If instead you always chose the character with the highest probability (greedy decoding), how would the generated text differ? Under what circumstances might greedy decoding produce worse text than temperature sampling?

    > *Hint: Greedy decoding is equivalent to T→0. The model always picks the single most probable character. In a small training corpus, one character might dominate every context because it appeared there most often — not because it is linguistically correct in all cases. What happens when the greedy choice locks the model into a repetitive loop?*

14. Perplexity is defined as $e^{-\frac{1}{N}\sum_{i} \log P(\text{char}_i)}$ — roughly, how surprised the model is by each character in a test text, on average. Without computing exact numbers, predict: would a trigram model have lower or higher perplexity than a bigram model on a held-out Shakespeare passage? What about a 20-gram model on the same passage?

    > *Hint: The trigram has more context and should predict more accurately on passages similar to its training data (lower perplexity). The 20-gram model has so much context that it can't find many matches in training — it will frequently hit the backoff case or fail entirely, making it worse on held-out data even though it performs perfectly on training data. This is the classic overfitting story.*

---

## Reflection Prompt

**Personal:** Did building this model change how you think about what it means to "learn" from text? Before today, would you have said our n-gram model "understands" Shakespeare? Would you say it now? What criterion would you use to decide?

**Technical:** A 5-gram character model trained on Romeo and Juliet has a fixed vocabulary of the characters Shakespeare used. If you gave it the prompt "Write a Python function to sort a list", what would happen at each step — from the first character through the first backoff failure? Be specific about which line of `generate_text` would be responsible for each behavior.

**Societal:** Character-level language models are the conceptual ancestor of modern LLMs. Knowing that a modern LLM is "just" a much larger, more sophisticated version of the same next-token prediction mechanism — does this change how much you trust its outputs? What does the n-gram model's brittleness on unseen inputs tell you about risks in the LLM case, even though the LLM is far more capable?

---

→ **Coming Up Next:** Our n-gram model predicts the next character by looking at a fixed-size window. Transformers replaced this by learning to attend to *any* previous position in the input, weighted by relevance — not just the last n-1 characters. In the next session we compute attention by hand and see exactly why this makes the model so much better at long-range dependencies like matching "Arise" with "sun" two lines later.

---

## Further Reading

- [Bigram Word Generator notebook](/files/notebooks/Bigram_Word_Generator.ipynb) — a runnable companion that builds a word-level bigram model, plots next-word histograms, and generates text by sampling or argmax.
- Jurafsky and Martin. *Speech and Language Processing*, Chapter 3 (n-gram language models). Available free online at web.stanford.edu/~jurafsky/slp3/.
- Andrej Karpathy. "The Unreasonable Effectiveness of Recurrent Neural Networks" (blog post, 2015). Shows character-level LM outputs at various training stages.
- Andrej Karpathy. *makemore* (GitHub). A step-by-step series building exactly this kind of character-level model up to a full transformer.
- Shannon, C.E. "A Mathematical Theory of Communication." *Bell System Technical Journal* (1948). The original n-gram language model paper.
