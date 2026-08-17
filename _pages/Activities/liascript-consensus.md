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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Self-consistency** | Running the same question through a model many times and picking the most common answer, because correct reasoning tends to cluster while errors scatter. | Asking 9 agents to solve an arithmetic problem and keeping the answer that 7 of them agree on. |
| **Embedding** | Converting text into a list of numbers that captures meaning, so that sentences with similar meanings land close together in that number-space. | "Simmer the tomatillos" and "boil them briefly" get similar number-lists even though the words differ. |
| **Cosine similarity** | A way to measure how "pointing in the same direction" two meaning-vectors are, used here to decide whether two agent answers say basically the same thing. | Two salsa recipes score 0.92 similarity because they both emphasize roasting and cilantro. |
| **Clustering** | Grouping items so that similar ones end up in the same bucket without being told in advance how many buckets to make. | Agglomerative clustering groups the six recipe drafts into three buckets: roasted, boiled, and raw. |
| **Synthesizer agent** | A separate agent whose only job is to read the cluster summaries and write one merged output, running at low temperature to stay accurate rather than creative. | The synthesizer reads "4 of 6 agents roast" and "3 of 6 use jalapeño" and writes a single coherent recipe. |
| **Temperature** | A number that controls how random a model's word choices are: 0 means always pick the most likely word, 1.0 means sample more adventurously. | Drafters run at temperature 1.0 to produce diverse ideas; the synthesizer runs at 0.2 to commit reliably. |

---

# Part I: From Voting to Synthesis

In this section you will move from the simple majority vote from the debate activity to a more powerful idea: clustering answers by meaning and synthesizing a merged result. The tomatillo salsa example makes this concrete — you will see why exact-match voting fails on paragraph answers and how embedding similarity solves that problem.

## Model 1: The Tomatillo Question

Think of a jury deliberation. Twelve jurors each hear the same evidence and independently form an opinion; the jury room is where they find the shared view. Today's agents play the same role: each starts from the same question, produces a different answer because of temperature-driven randomness, and then a synthesizer finds the shared position — except our "jury room" is an algorithm, not a room. This matters because the same technique can be applied to any question where multiple independent drafts are better than one: code review, medical triage summaries, or research literature.

**Self-consistency (vote on the answer).** Sample $k$ independent chains at moderate temperature, extract each final answer, return the mode. For questions with short checkable answers, accuracy rises with $k$ because the correct answer tends to be reached by *many distinct reasoning paths* while errors scatter:

$$
\hat{y} = \arg\max_{y} \sum_{i=1}^{k} \mathbb{1}[y_i = y]
$$

**Clustered consensus (vote on the meaning).** When answers are paragraphs rather than tokens, exact-match voting fails ("simmer the tomatillos" and "boil them briefly" should count together). Embed the $k$ drafts, cluster by cosine similarity, and treat the largest cluster as the consensus *position* — the same machinery as our RAG-quality clustering, now aimed at agent outputs.

**Synthesis (write the merged view).** A synthesizer agent receives the cluster representatives, with their support counts, and drafts a single output that preserves majority positions while noting genuine disagreements. Crucially, the synthesizer's context is *small*: cluster summaries, not all $k$ transcripts.

Five agents at temperature 1.0 propose tomatillo salsa recipes. Three roast the tomatillos, one boils them, one uses them raw; four include cilantro; opinions split on jalapeño versus serrano.

| Agent | Cooking technique | Chile | Key aromatics | Cluster |
|---|---|---|---|---|
| Agent 1 | Roasts under broiler until charred | Jalapeño | Cilantro, white onion, garlic | A |
| Agent 2 | Roasts in dry skillet | Serrano | Cilantro, white onion | A |
| Agent 3 | Roasts on open flame | Jalapeño | Cilantro, garlic, lime | A |
| Agent 4 | Boils for 10 minutes | Jalapeño | Cilantro, cumin | B |
| Agent 5 | Uses raw, no heat | Serrano | Cilantro, avocado, lime | C |

### Critical Thinking Questions

1. Group the five recipes into clusters by their *load-bearing* choice (the one that fundamentally changes the dish). Which choice is load-bearing and which is garnish-level, and how would embeddings see the difference — or fail to?

   > *Hint: Ask yourself: if you swapped jalapeño for serrano, would the dish taste radically different? What if you swapped raw for roasted? The answer tells you which dimension is load-bearing.*

2. Write, in two sentences, the synthesis you would want: it should commit where the majority is strong and disclose where it is split.

   > *Hint: The majority (3 of 5) agrees on roasting. The chile choice is evenly split. Your synthesis should say something definite about cooking method and something candid about the chile.*

3. Exact-match voting on full recipe texts would yield five singleton "answers." State precisely why, in terms of the difference between *string* identity and *semantic* identity.

   > *Hint: "Roast under the broiler" and "char over an open flame" are different strings but close meanings. Exact-match treats them as completely different answers even though they express the same culinary decision.*

With the conceptual case for clustering established, Part II shows the implementation so you can see exactly how embeddings and agglomerative clustering (grouping by similarity without knowing the number of groups in advance) make this work in code.

---

# Part II: Implementation

In this section you will read the full sample-cluster-synthesize pipeline and run it on the tomatillo question. The questions that follow ask you to connect the code's design choices — especially the temperature settings and the distance threshold — back to the theory from Part I.

## Model 2: Sample, Cluster, Synthesize

In a courtroom, the bailiff does not ask jurors to write identical sentences — the foreperson synthesizes a verdict that reflects where the group actually landed. The code below does the same: it collects $k$ drafts (the "testimony"), groups them by semantic similarity (the "deliberation"), and has a synthesizer agent write the verdict. Pay attention to the two different temperature settings — they encode the explore-versus-exploit logic we saw in the debate module.

---

## Code Cell

The code below runs in three stages: (1) it samples six diverse recipe drafts at high temperature, (2) it converts each draft to an embedding vector and groups similar drafts into clusters using agglomerative clustering (which builds groups bottom-up by merging the most similar pairs first), and (3) it passes the cluster summaries to a synthesizer that writes a single merged recipe. Notice that the synthesizer's context is small — it never sees all six original drafts, only the cluster representatives.

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

### Critical Thinking Questions

4. How many clusters formed, and does the largest correspond to a recognizable culinary position (for example, roasted versus boiled)? Quote the phrase that anchored the biggest cluster.

   > *Hint: Run the code and inspect the printed cluster labels. Look at the first 100 characters of each cluster's representative draft to identify its culinary stance.*

5. The synthesizer runs at temperature 0.2 while the drafters ran at 1.0. Map this onto the explore-exploit schedule from the debate module, and explain why the synthesis step must not be creative.

   > *Hint: High temperature = exploration (new ideas). Low temperature = exploitation (committing to the best known answer). At which stage do you want new ideas, and at which stage do you want reliability?*

6. The `distance_threshold=0.45` silently decides what counts as "the same opinion." Lower it to 0.25 and raise it to 0.7; report how the cluster structure, and therefore the consensus, changes. Who, in a deployed system, should own that number?

   > *Hint: A lower threshold is stricter — only very similar texts merge. A higher threshold is looser — nearly anything merges. Think about who is harmed if the threshold is set wrong: whose minority opinion gets absorbed into the majority?*

[[MC]]
Compared with simple majority voting, embedding-clustered consensus is principally designed to handle:
- ( ) Questions with one-token answers
- (x) Long-form answers where semantically equivalent positions are phrased differently
- ( ) Models that cannot follow JSON formats
- ( ) Deterministic generation at temperature 0

> **⚠️ Common Misconception:** Many students assume that more agents always means better answers. In reality, consensus amplifies whatever the model already believes most often. If the underlying model has a systematic bias — for example, always preferring certain cooking techniques that are over-represented in its training data — running more agents just makes that bias louder, not quieter. Consensus is a tool for aggregating diverse *reasoning paths* toward a correct answer, not for discovering truths the model does not already know.

Part III builds on this misconception warning by examining the conditions under which consensus actively misleads, and what to do about it in your own systems.

---

# Part III: Limits and Synthesis

In this section you will examine the situations where consensus makes results worse rather than better, and you will connect those limits to the *Training Data and Bias* activity. This is also where you will bridge today's work directly into your Multi-Agent Patterns Lab design.

## Model 3: When Consensus Misleads

Consensus aggregates the model's *distribution*, so it amplifies whatever that distribution over-represents: popular framings, mainstream defaults, training-data majorities. For factual questions this is usually a feature; for questions of taste, values, or contested policy, "the average of six samples" can erase legitimate minority positions — a theme we take up squarely in the *Training Data and Bias* activity. A candid synthesis discloses dissent rather than dissolving it.

---

## Exercises

1. *Self-consistency curve.*

   *What to do:* On your 10-problem arithmetic set from the debate exercises, plot accuracy versus $k \in \{1, 3, 5, 9\}$ samples with majority vote.

   *Starter hint:* Write a function `majority_vote(question, k)` that calls your `llm` function $k$ times, extracts the numeric answer from each response with a regex, and returns `Counter(answers).most_common(1)[0][0]`.

   *You've succeeded when:* You can show a plot where accuracy increases with $k$ and can identify the approximate $k$ where adding more samples stops improving accuracy meaningfully. Report the cost in API calls per correct answer at that optimal $k$.

2. *Consensus versus debate.*

   *What to do:* Run the tomatillo question through the two-round debate from the *Multi-Agent Debate* activity and today's cluster-synthesize pipeline at equal call budgets. Have a neighboring team blind-rank the two outputs and your single-shot baseline.

   *Starter hint:* Keep call counts equal by adjusting $k$ in the consensus pipeline so it matches the total LLM calls the debate pipeline makes. Blind-ranking means the other team cannot know which output came from which method.

   *You've succeeded when:* You have a ranking from the neighboring team and can articulate one structural reason why the winning method beat the loser on this specific question type.

3. *Dissent preservation.*

   *What to do:* Modify the synthesizer prompt so that any position held by at least one-third of agents must appear in the output. Demonstrate on a question where your agents genuinely split.

   *Starter hint:* Before calling the synthesizer, compute the fraction of agents in each cluster. Pass that fraction to the synthesizer prompt: "The following minority position is held by X of Y agents and must appear in your output: ..."

   *You've succeeded when:* You can show that a cluster holding exactly one-third of the vote still appears explicitly in the synthesized output, and the output does not misrepresent the minority as the majority position.

4. *Multi-Agent Patterns Lab bridge.*

   *What to do:* Sketch the architecture you will submit for the Multi-Agent Patterns Lab: where debate fits, where consensus fits, and the exact JSON each stage passes to the next.

   *Starter hint:* Draw two boxes (debate stage, consensus stage) and label each arrow between them with a Python dict showing the keys and value types that travel across it.

   *You've succeeded when:* A teammate who has not seen your Multi-Agent Patterns Lab plan can read your sketch and accurately describe what each stage receives and produces.

---

## Reflection Prompt

*Personal:* Committees, juries, and peer review all aggregate noisy human judgments. Which of today's three strategies (vote, cluster, synthesize) does each most closely resemble, and what does that comparison reveal about how much you would trust each process with a decision affecting you personally?

*Technical:* The `distance_threshold` parameter is a design decision with real consequences for whose opinions get merged and whose get preserved. Describe the technical steps you would take to choose this threshold responsibly for a deployed system — what data would you need, and how would you validate your choice?

*Societal:* Consensus systems used in hiring, lending, or criminal justice would amplify whatever majority opinion exists in training data. Name a specific domain where you would argue consensus-based AI should be prohibited entirely, and explain what human institution should replace it.

---

→ Coming Up Next: We move from aggregating agent *outputs* to organizing agents into deliberate *teams* — assigning roles, managing shared state, and designing the handoffs between specialists.

## Further Reading

- Wang et al. "Self-Consistency Improves Chain of Thought Reasoning in Language Models." *ICLR* (2023).
- Surowiecki. *The Wisdom of Crowds* (2004). The independence condition, in human form.
- Du et al. "Improving Factuality and Reasoning through Multiagent Debate." (2023), for the contrast case.
