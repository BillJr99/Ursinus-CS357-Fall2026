# Stochastic Multi-Agent Consensus
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-consensus.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-consensus.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Stochastic Multi-Agent Consensus

Debate ends in a vote or a verdict; **consensus** ends in a *synthesis* that no single agent proposed. Today we treat sampling randomness as a resource: many stochastic drafts, clustered by meaning, merged by a synthesizer, evaluated against the field. Our running demonstration is delightfully concrete: several agents argue about, and then converge on, the best **tomatillo salsa recipe**. We move from **self-consistency $\rightarrow$ embedding-clustered consensus $\rightarrow$ synthesis $\rightarrow$ when consensus is the wrong goal**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: From Voting to Synthesis

## 1. Three Aggregation Strategies

**Self-consistency (vote on the answer).** Sample $k$ independent chains at moderate temperature, extract each final answer, return the mode. For questions with short checkable answers, accuracy rises with $k$ because the correct answer tends to be reached by *many distinct reasoning paths* while errors scatter:

$$
\hat{y} = \arg\max_{y} \sum_{i=1}^{k} \mathbb{1}[y_i = y]
$$

**Clustered consensus (vote on the meaning).** When answers are paragraphs rather than tokens, exact-match voting fails ("simmer the tomatillos" and "boil them briefly" should count together). Embed the $k$ drafts, cluster by cosine similarity, and treat the largest cluster as the consensus *position*, the same machinery as our RAG-quality clustering, now aimed at agent outputs.

**Synthesis (write the merged view).** A synthesizer agent receives the cluster representatives, with their support counts, and drafts a single output that preserves majority positions while noting genuine disagreements. Crucially, the synthesizer's context is *small*: cluster summaries, not all $k$ transcripts.

---

## Model 1: The Tomatillo Question

Five agents at temperature 1.0 propose tomatillo salsa recipes. Three roast the tomatillos, one boils them, one uses them raw; four include cilantro; opinions split on jalapeño versus serrano.

### Critical Thinking Questions

1. Group the five recipes into clusters by their *load-bearing* choice. Which choice is load-bearing and which is garnish-level, and how would embeddings see the difference (or fail to)?
2. Write, in two sentences, the synthesis you would want: it should commit where the majority is strong and disclose where it is split.
3. Exact-match voting on full recipe texts would yield five singleton "answers." State precisely why, in terms of the difference between *string* identity and *semantic* identity.

---

# Part II: Implementation

## 2. Sample, Cluster, Synthesize

---

## Code Cell

```python
import numpy as np
import requests
from sklearn.cluster import AgglomerativeClustering

np.random.seed(42)

def llm(system, user, temperature=1.0):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": temperature},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=180)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[consensus:llm] {e}")
        import traceback; traceback.print_exc()
        return ""

def embed(text):
    try:
        r = requests.post("http://localhost:11434/api/embeddings",
                          json={"model": "nomic-embed-text", "prompt": text}, timeout=120)
        return np.array(r.json()["embedding"])
    except Exception as e:
        print(f"[consensus:embed] {e}")
        import traceback; traceback.print_exc()
        return np.zeros(768)

QUESTION = "In 60 words, give your best tomatillo salsa method: cooking technique, chile, and key aromatics."

# 1. Sample k diverse drafts
k = 6
drafts = [llm("You are a confident home cook with strong opinions.", QUESTION) for _ in range(k)]

# 2. Cluster by meaning
X = np.array([embed(d) for d in drafts])
X = X / np.linalg.norm(X, axis=1, keepdims=True)
labels = AgglomerativeClustering(n_clusters=None, distance_threshold=0.45,
                                 metric="cosine", linkage="average").fit_predict(X)
clusters = {}
for d, l in zip(drafts, labels):
    clusters.setdefault(l, []).append(d)
for l, ds in clusters.items():
    print(f"--- cluster {l} ({len(ds)} drafts) ---\n{ds[0][:100]}...\n")

# 3. Synthesize from cluster representatives, weighted by support
summary = "\n\n".join(f"[position supported by {len(ds)} of {k} agents]\n{ds[0]}"
                      for ds in clusters.values())
consensus = llm("Merge these positions into ONE recipe. Follow the majority on conflicts, "
                "and add one line noting any close disagreement.", summary, temperature=0.2)
print("=== CONSENSUS ===\n", consensus)
```

---

## Model 2: Anatomy of the Consensus

### Critical Thinking Questions

4. How many clusters formed, and does the largest correspond to a recognizable culinary position (for example, roasted versus boiled)? Quote the phrase that anchored the biggest cluster.
5. The synthesizer runs at temperature 0.2 while the drafters ran at 1.0. Map this onto the explore-exploit schedule from the debate module, and explain why the synthesis step must not be creative.
6. The `distance_threshold=0.45` silently decides what counts as "the same opinion." Lower it to 0.25 and raise it to 0.7; report how the cluster structure, and therefore the consensus, changes. Who, in a deployed system, should own that number?

[[MC]]
Compared with simple majority voting, embedding-clustered consensus is principally designed to handle:
- ( ) Questions with one-token answers
- (x) Long-form answers where semantically equivalent positions are phrased differently
- ( ) Models that cannot follow JSON formats
- ( ) Deterministic generation at temperature 0

---

# Part III: Limits and Synthesis

## 3. When Consensus Misleads

Consensus aggregates the model's *distribution*, so it amplifies whatever that distribution over-represents: popular framings, mainstream defaults, training-data majorities. For factual questions this is usually a feature; for questions of taste, values, or contested policy, "the average of six samples" can erase legitimate minority positions, a theme we take up squarely in the bias module next week. The honest synthesis discloses dissent rather than dissolving it.

---

## 4. Exercises

1. *Self-consistency curve.* On your 10-problem arithmetic set from the debate exercises, plot accuracy versus $k \in \{1, 3, 5, 9\}$ samples with majority vote. Where does the curve flatten, and what does each additional point of accuracy cost in calls?
2. *Consensus versus debate.* Run the tomatillo question through yesterday's two-round debate and today's cluster-synthesize pipeline at equal call budgets. Have a neighboring team blind-rank the two outputs and your single-shot baseline.
3. *Dissent preservation.* Modify the synthesizer prompt so that any position held by at least one third of agents must appear in the output. Demonstrate on a question where your agents genuinely split.
4. *Lab 4 bridge.* Sketch the architecture you will submit for Lab 4: where debate fits, where consensus fits, and the exact JSON each stage passes to the next.

---

## Reflection Prompt

In your notebook: committees, juries, and peer review all aggregate noisy human judgments. Which of today's three strategies (vote, cluster, synthesize) does each resemble, and what does the comparison suggest about when you would *not* want an AI consensus to settle a question that affects you?

---

## 5. Further Reading

- Wang et al. "Self-Consistency Improves Chain of Thought Reasoning in Language Models." *ICLR* (2023).
- Surowiecki. *The Wisdom of Crowds* (2004). The independence condition, in human form.
- Du et al. "Improving Factuality and Reasoning through Multiagent Debate." (2023), for the contrast case.
