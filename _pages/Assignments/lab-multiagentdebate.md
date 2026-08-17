---
layout: assignment
permalink: /Assignments/MultiAgentDebate
title: "CS357: Foundations of Artificial Intelligence - Lab: Multi-Agent Patterns (Critique, Refine, Debate, Consensus)"

info:
  coursenum: CS357
  purpose: "To orchestrate multiple agents through the four patterns that make agent systems more reliable than a single call - critique, refine, debate, and consensus - and to learn empirically when aggregation improves answers and when correlated errors defeat it."
  tilt:
    task: "Implement a generator/critic/refine loop, then multi-agent debate and embedding-clustered consensus, and compare all of them against a single-shot baseline at matched call budgets."
    criteria: "Assessed on the debate loop, the consensus pipeline, and a matched-budget comparison that surfaces a correlated failure; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To implement multi-agent debate with independent first rounds and peer-informed revision rounds using configurable agents, rounds, and temperature schedules
    - To implement stochastic consensus with normalized-embedding clustering and a synthesis agent that receives cluster summaries
    - To compare debate, consensus, and single-shot baselines at matched call budgets on a labeled task set
    - To identify and explain correlated failure modes that aggregation cannot repair and propose a non-LLM remedy
  rubric:
    - weight: 20
      description: "Part A: Critique and Refine Loop"
      preemerging: "No generator/critic/refine loop, or the critic does not influence the next generation."
      beginning: "A loop exists but runs a fixed number of rounds with no stopping rule, so it cannot tell improvement from churn."
      progressing: "The loop runs generator, critic, and refiner with a stated stopping rule, and a transcript shows an output changing in response to a critique."
      proficient: "As progressing, and the writeup shows a case where the critic was wrong and says how you could tell - plus what the loop cost in extra calls for the quality it bought."
    - weight: 25
      description: Debate Implementation
      preemerging: The debate fails to run due to major issues, or the program fails to run
      beginning: The debate runs but fails on test questions due to one or more minor issues
      progressing: The debate runs correctly with configurable agents and rounds and majority vote aggregation, with a fragile component such as answer extraction
      proficient: "The debate runs correctly with configurable agents, rounds, and temperature schedule; answer extraction anchors on a required ANSWER: line and handles its absence with a located error message; both majority-vote and judge-agent aggregation are available; a transcript of at least one complete 3-agent, 2-round debate is included in the submission"
    - weight: 20
      description: Consensus Implementation
      preemerging: The consensus pipeline fails to run due to major issues
      beginning: Drafts are sampled but clustering or synthesis is missing or incorrect
      progressing: The pipeline samples, clusters by embedding similarity with normalized vectors, and synthesizes from cluster representatives, with a minor issue
      proficient: The pipeline samples k high-temperature drafts, clusters with cosine distance over normalized embeddings and a justified threshold, synthesizes using one representative per cluster with its support count, discloses close disagreements in one line, and the synthesizer receives cluster summaries rather than all k transcripts; a demonstration on a long-form question is included
    - weight: 20
      description: Comparative Evaluation
      preemerging: No evaluation is provided
      beginning: Conditions are compared anecdotally without matched budgets or a protocol
      progressing: Debate, consensus, and single shot baselines are compared on a labeled task set with accuracy and call counts reported
      proficient: All conditions are compared at matched call budgets on a labeled task set of at least ten items; accuracy and model-call count are reported per condition in a table; at least one correlated failure is documented with all agents' verbatim responses showing agreement on the wrong answer; the writeup explains specifically why no aggregation strategy could have repaired it and names one non-LLM addition that would
    - weight: 10
      description: Code Quality and Documentation
      preemerging: Code commenting and structure are absent, or code structure departs significantly from best practice
      beginning: Code commenting and structure is limited in ways that reduce the readability of the program
      progressing: Code documentation is present that re-states the explicit code definitions
      proficient: Every non-trivial function has a docstring; all model calls and embedding operations are wrapped in exception handlers that print a located message (e.g., [lab4:debate_round]) followed by a traceback; number of agents, rounds, temperature schedule, and distance threshold are read from a JSON config file rather than hardcoded
    - weight: 5
      description: Writeup, Reflection, and Submission
      preemerging: An incomplete submission is provided
      beginning: The program is submitted, but not according to the directions in one or more ways
      progressing: The program is submitted according to the directions with a minor omission, with at least superficial responses to the reflection prompts
      proficient: The program is submitted according to the directions, including a readme writeup, a pair log with at least two timestamped role swaps, and reflection answers that each cite a specific accuracy figure, transcript excerpt, or named failure mode from the lab rather than restating the prompt
  readings:
    - rtitle: "Multi-Agent Debate Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multiagentdebate.md"
    - rtitle: "Stochastic Consensus Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-consensus.md"

tags:
  - multi-agent
  - agents
  - evaluation

---

In this lab, you and your partner will build and rigorously compare the two aggregation architectures from class: **debate** (agents see and rebut each other) and **stochastic consensus** (independent samples, clustered by meaning, merged by synthesis). This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

**See the course schedule for the assigned and due dates.**

---

## Before You Start

**Prerequisite concepts** — complete these activities before writing any code:

- [Multi-Agent Debate Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multiagentdebate.md) — independent rounds, peer-informed revision, majority vote
- [Stochastic Consensus Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-consensus.md) — sampling, embedding clustering, synthesis

**Tools to install:**

```bash
# Sentence transformers for embedding clustering (Part 2)

## This lab has two halves

Critique-and-refine and debate-and-consensus used to be two separate 100-point labs due eight days apart. They are the same family of idea - *use more than one model call to get a better answer* - so they are now **one lab with one grade**.

**Part A - Critique and Refine.** Build the generator/critic/refine loop and its stopping rule. The full step-by-step specification lives on its own page so this one stays readable: **[Critique and Refine](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/CritiqueRefine)**. Do Part A first; the debate work in Part B reuses its scaffolding, and a critic you can already trust is what makes a debate round worth reading.

**Part B - Debate and Consensus.** Everything below on this page.

Both halves are submitted together, once, against the single rubric in this assignment. There is no separate Critique-and-Refine deadline.


pip install sentence-transformers scikit-learn numpy

# Requests for Ollama calls
pip install requests

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

**Health check:**

```bash
python -c "
from sentence_transformers import SentenceTransformer
import numpy as np
model = SentenceTransformer('all-MiniLM-L6-v2')
vecs = model.encode(['hello world', 'hi there', 'the sky is blue'])
# Normalize
norms = np.linalg.norm(vecs, axis=1, keepdims=True)
normed = vecs / norms
print('Embedding shape:', vecs.shape)
print('Cosine similarity (should be ~0.7 for similar sentences):')
print(normed[0] @ normed[1])
"
```

Expected output:

```
Embedding shape: (3, 384)
Cosine similarity (should be ~0.7 for similar sentences):
0.6843...
```

**Estimated time budget:**

| Part | Task | Estimated time |
|------|------|----------------|
| Part 1 | Debate | 60–90 min |
| Part 2 | Consensus | 60–75 min |
| Part 3 | The Shootout | 60–75 min |
| Part 4 | Threshold Sensitivity | 30–45 min |
| Writeup | Readme and reflection | 30–45 min |

---

## Part 1: Debate

Implement a configurable debate (number of agents, number of rounds, temperature schedule, all externalized in JSON configuration): independent answers in round one, peer-informed revisions in later rounds, and aggregation by both majority vote and an optional judge agent. Answer extraction must tolerate formatting drift (anchor on a required `ANSWER:` line and handle its absence gracefully with a located error message).

### Step-by-step guide

**Step 1: Create your configuration file.**

```json
{
  "model": "llama3.2",
  "ollama_url": "http://localhost:11434/api/chat",
  "debate": {
    "num_agents": 3,
    "num_rounds": 2,
    "temperature_schedule": [0.7, 0.4],
    "seed_base": 100
  },
  "consensus": {
    "num_samples": 6,
    "sample_temperature": 0.8,
    "synthesizer_temperature": 0.1,
    "distance_threshold": 0.3,
    "embed_model": "all-MiniLM-L6-v2"
  }
}
```

The `temperature_schedule` list has one temperature per round. If there are more rounds than entries, repeat the last entry.

**Step 2: Implement the per-agent generation function.**

```python
import requests
import json
import re
import traceback

def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def agent_respond(question, agent_id, round_num, peer_answers, config):
    """
    Generate one agent's response for the given round.
    round_num: 1-indexed
    peer_answers: list of (agent_id, answer_text) from the previous round (empty for round 1)
    Returns the full response text.
    """
    schedule = config["debate"]["temperature_schedule"]
    temp = schedule[min(round_num - 1, len(schedule) - 1)]
    seed = config["debate"]["seed_base"] + agent_id * 100 + round_num

    if round_num == 1:
        # Independent first round
        user_content = (
            f"Question: {question}\n\n"
            f"Think through this carefully and provide your answer. "
            f"End your response with a line in exactly this format:\n"
            f"ANSWER: <your answer here>"
        )
    else:
        # Peer-informed revision round
        peer_section = "\n\n".join(
            f"Agent {pid} said:\n{ans}" for pid, ans in peer_answers
        )
        user_content = (
            f"Question: {question}\n\n"
            f"Here are the answers from the other agents in the previous round:\n\n"
            f"{peer_section}\n\n"
            f"Review their reasoning. You may revise your answer if you find their arguments convincing, "
            f"or maintain your position with a rebuttal. "
            f"End your response with a line in exactly this format:\n"
            f"ANSWER: <your answer here>"
        )

    messages = [{"role": "user", "content": user_content}]
    payload = {
        "model": config["model"],
        "messages": messages,
        "stream": False,
        "options": {"temperature": temp, "seed": seed}
    }

    try:
        response = requests.post(config["ollama_url"], json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab4:agent_respond:agent{agent_id}:round{round_num}] {e}")
        traceback.print_exc()
        raise
```

**Step 3: Implement answer extraction with graceful fallback.**

```python
def extract_answer(response_text, agent_id, round_num):
    """
    Extract the ANSWER: line from a response.
    Returns the answer string, or None if not found (with a located warning).
    """
    match = re.search(r"ANSWER:\s*(.+)", response_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    else:
        print(f"[lab4:extract_answer] WARNING: Agent {agent_id}, round {round_num} — no ANSWER: line found. Full response: {response_text[:200]!r}")
        return None
```

**Step 4: Implement the full debate loop.**

```python
def run_debate(question, config):
    """
    Run a full multi-agent debate.
    Returns (final_answers_by_agent, all_round_transcripts, total_calls).
    """
    num_agents = config["debate"]["num_agents"]
    num_rounds = config["debate"]["num_rounds"]
    total_calls = 0

    # round_answers[round][agent_id] = (full_response, extracted_answer)
    round_answers = {}

    for round_num in range(1, num_rounds + 1):
        print(f"\n=== Debate Round {round_num} ===")
        round_answers[round_num] = {}

        for agent_id in range(num_agents):
            # Peer answers: all agents from previous round except self
            if round_num == 1:
                peer_answers = []
            else:
                peer_answers = [
                    (pid, extract_answer(data[0], pid, round_num - 1) or "(no answer)")
                    for pid, data in round_answers[round_num - 1].items()
                    if pid != agent_id
                ]

            response = agent_respond(question, agent_id, round_num, peer_answers, config)
            answer = extract_answer(response, agent_id, round_num)
            round_answers[round_num][agent_id] = (response, answer)
            total_calls += 1
            print(f"  Agent {agent_id}: ANSWER = {answer}")

    # Final answers from last round
    final_answers = {
        agent_id: data[1]
        for agent_id, data in round_answers[num_rounds].items()
        if data[1] is not None
    }

    return final_answers, round_answers, total_calls
```

**Step 5: Implement majority vote aggregation.**

```python
from collections import Counter

def majority_vote(final_answers):
    """
    Return the most common answer among the agents.
    In case of a tie, return the lexicographically first answer.
    """
    if not final_answers:
        return None
    counts = Counter(final_answers.values())
    return counts.most_common(1)[0][0]
```

**Step 6: Run a smoke test.**

```python
if __name__ == "__main__":
    config = load_config()
    question = "What is 15% of 240?"
    final_answers, transcripts, calls = run_debate(question, config)
    winner = majority_vote(final_answers)
    print(f"\nFinal answers: {final_answers}")
    print(f"Majority vote: {winner}")
    print(f"Total model calls: {calls}")
```

Expected output:

```
=== Debate Round 1 ===
  Agent 0: ANSWER = 36
  Agent 1: ANSWER = 36
  Agent 2: ANSWER = 34

=== Debate Round 2 ===
  Agent 0: ANSWER = 36
  Agent 1: ANSWER = 36
  Agent 2: ANSWER = 36

Final answers: {0: '36', 1: '36', 2: '36'}
Majority vote: 36
Total model calls: 6
```

### Troubleshooting — Part 1

**`ANSWER:` is never found even though it appears in the raw output**
The model may be outputting `Answer:` (capitalized differently) or `**ANSWER:**` (with markdown bold). Update the regex to be case-insensitive (already done in the template with `re.IGNORECASE`) and strip markdown: `response_text = re.sub(r'\*+', '', response_text)`.

**Agents always agree on round 1 (no diversity)**
Your seeds may be too similar or the temperature is too low. Try `seed_base: 0` and `temperature_schedule: [0.9, 0.5]`. For factual questions, even high temperature may produce agreement — try more subjective questions for testing diversity.

**One agent's response is cut off mid-sentence**
The model hit its context window. Shorten the peer_section by taking only the extracted ANSWER lines from peers (not their full reasoning): `f"Agent {pid} answered: {ans}"`.

---

> **Checkpoint: Before moving to Part 2, make sure you can answer:**
> 1. What is the purpose of sharing peer answers in rounds 2+ rather than keeping agents independent for all rounds? What risk does peer-sharing introduce?
> 2. What happens in your code if `extract_answer` returns None for one agent in the final round? How does your majority vote handle it?
> 3. Run a 3-agent, 2-round debate on an arithmetic question. Did any agent change their answer between rounds? If so, was it because they were persuaded by correct reasoning or simply by social pressure?

---

## Part 2: Consensus

### The Consensus Pattern (from the Consensus activity)

The consensus activity is now a supplemental (self-paced) resource rather than a scheduled class session, so before you build anything, here is the core idea it teaches. **Stochastic consensus** exploits the fact that a language model at high temperature is a *sampler*, not an oracle: ask it the same question six times and you get six different drafts drawn from a distribution of plausible answers. Individually, any one draft might be idiosyncratic or wrong. But if you group the drafts by *meaning* — not by exact wording — the sizes of the groups tell you something no single draft can: which positions the model keeps returning to (high support) and which are one-off flukes (low support).

The grouping step is where embeddings come in. An embedding model maps each draft to a vector such that drafts with similar meaning land close together, even when they share few words. By normalizing those vectors and clustering them with cosine distance, "six drafts" becomes "three positions, with support counts of 3, 2, and 1." A final low-temperature **synthesizer** then receives one representative draft per cluster (plus its support count) — never all six raw transcripts — and writes a single answer that follows the majority and *discloses* any close disagreement instead of papering over it. That disclosure rule is the pattern's honesty mechanism: when the samples genuinely split, the user deserves to know.

The whole pipeline looks like this:

```
question ──> sample k drafts at high temperature      (k model calls)
                    │
                    ▼
             embed each draft ──> normalize vectors
                    │
                    ▼
             cluster by cosine distance (threshold)
                    │
                    ▼
      one representative per cluster + support count
                    │
                    ▼
             synthesizer at low temperature            (1 model call)
                    │
                    ▼
   single answer, majority-following, close-disagreement disclosed
```

Notice the two dials you will experiment with in this lab: the **sampling temperature** (how diverse the drafts are) and the **distance threshold** (how aggressively meanings are merged — the subject of Part 4). For the full treatment, including the in-class tomatillo salsa example and why *independence* between samples matters, work through the [Stochastic Consensus Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-consensus.md) — it is strongly recommended before you start this part.

Implement the sample, cluster, synthesize pipeline: $$k$$ high-temperature drafts, embedding clustering over normalized vectors with cosine geometry, and a low-temperature synthesizer that receives one representative per cluster with its support count, follows the majority on conflicts, and **discloses any close disagreement in one line**. Demonstrate the pipeline on a long-form question with no single correct answer (the in-class tomatillo salsa question is a fine starting point; choose your own analogous question too).

### Step-by-step guide

**Step 1: Sample k drafts independently.**

```python
def sample_drafts(question, config):
    """
    Sample k independent drafts at high temperature.
    Returns list of draft strings.
    """
    k = config["consensus"]["num_samples"]
    temp = config["consensus"]["sample_temperature"]
    drafts = []

    for i in range(k):
        seed = config["debate"]["seed_base"] + i  # different seed per sample
        messages = [{"role": "user", "content": question}]
        payload = {
            "model": config["model"],
            "messages": messages,
            "stream": False,
            "options": {"temperature": temp, "seed": seed}
        }
        try:
            response = requests.post(config["ollama_url"], json=payload, timeout=60)
            response.raise_for_status()
            draft = response.json()["message"]["content"]
            drafts.append(draft)
            print(f"  Sample {i+1}/{k}: {draft[:80]}...")
        except Exception as e:
            print(f"[lab4:sample_drafts:sample{i}] {e}")
            traceback.print_exc()
            raise

    return drafts
```

**Step 2: Embed and cluster the drafts.**

> **This code is provided complete — copy it as-is.** You are not expected to write embedding or clustering internals with one semester of Python behind you; `sentence-transformers` and scikit-learn's `AgglomerativeClustering` do that work. Your job in this step is to *call* this function and *interpret* what it returns: which drafts landed in which cluster, which cluster has the most support, and whether the grouping matches your own reading of the drafts.

```python
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering

def cluster_drafts(drafts, config):
    """
    Embed drafts, normalize vectors, cluster by cosine distance.
    Returns (labels, embeddings, cluster_representatives).
    labels[i] = cluster ID for draft i.
    cluster_representatives: dict {cluster_id: (representative_draft, support_count)}
    """
    embed_model_name = config["consensus"]["embed_model"]
    threshold = config["consensus"]["distance_threshold"]

    embed_model = SentenceTransformer(embed_model_name)
    embeddings = embed_model.encode(drafts)

    # Normalize to unit vectors so cosine distance = 1 - dot product
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normed = embeddings / norms

    # Cosine distance = 1 - cosine_similarity
    # AgglomerativeClustering with metric='cosine' requires precomputed or use distance_threshold
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=threshold,
        metric="cosine",
        linkage="average"
    )
    labels = clustering.fit_predict(normed)

    # Find representative (draft closest to cluster centroid) and support count
    cluster_ids = set(labels)
    representatives = {}
    for cid in cluster_ids:
        indices = [i for i, l in enumerate(labels) if l == cid]
        support = len(indices)
        # Centroid of normalized vectors
        centroid = normed[indices].mean(axis=0)
        centroid /= np.linalg.norm(centroid)
        # Draft closest to centroid
        similarities = [normed[i] @ centroid for i in indices]
        best_idx = indices[int(np.argmax(similarities))]
        representatives[cid] = (drafts[best_idx], support)

    print(f"\nClustering: {len(drafts)} drafts -> {len(cluster_ids)} clusters (threshold={threshold})")
    for cid, (rep, support) in sorted(representatives.items()):
        print(f"  Cluster {cid} (support={support}): {rep[:80]}...")

    return labels, normed, representatives
```

**Interpretation questions (answer these in your readme after running the provided clustering code):**

1. Print `labels` next to the first 80 characters of each draft. Read the drafts in each cluster yourself: do the groupings match *your* judgment of which drafts say the same thing? Name one pair the clusterer grouped that you would not have, or vice versa.
2. Which cluster has the highest support count, and in one sentence, what position does its representative draft take?
3. The representative is the draft closest to the cluster centroid. Look at the representative chosen for your largest cluster — is it also the draft you would have picked as the "most typical" of that group? Why might the centroid-nearest draft differ from the best-written draft?

**Step 3: Synthesize from cluster representatives.**

```python
def synthesize(question, representatives, config):
    """
    Build a context from cluster representatives and synthesize a final answer.
    Returns the synthesized answer string.
    """
    # Sort by support (descending) so the synthesizer sees majority first
    sorted_clusters = sorted(representatives.items(), key=lambda x: -x[1][1])
    total_support = sum(s for _, (_, s) in sorted_clusters)

    context_parts = []
    for cid, (rep, support) in sorted_clusters:
        pct = support / total_support * 100
        context_parts.append(f"[Cluster {cid}, support={support}/{total_support} ({pct:.0f}%)]\n{rep}")

    context = "\n\n---\n\n".join(context_parts)
    majority_support = sorted_clusters[0][1][1]
    close_disagreement = len(sorted_clusters) > 1 and (majority_support / total_support) < 0.6

    system_prompt = (
        "You are a synthesizer. You receive several response clusters from independent samples. "
        "Each cluster is labeled with its support count. "
        "Your job:\n"
        "1. Follow the majority position on any factual conflicts.\n"
        "2. If there is a close disagreement (majority < 60% of samples), disclose it in one sentence at the end.\n"
        "3. Produce a single coherent, well-written response. Do not just concatenate the clusters.\n\n"
        + ("NOTE: There is a close disagreement among the samples. Disclose it." if close_disagreement else "")
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Question: {question}\n\nClusters:\n\n{context}"}
    ]
    payload = {
        "model": config["model"],
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": config["consensus"]["synthesizer_temperature"],
            "seed": config["debate"]["seed_base"]
        }
    }
    try:
        response = requests.post(config["ollama_url"], json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab4:synthesize] {e}")
        traceback.print_exc()
        raise

def run_consensus(question, config):
    """Full sample-cluster-synthesize pipeline."""
    print(f"\n=== Sampling {config['consensus']['num_samples']} drafts ===")
    drafts = sample_drafts(question, config)

    print("\n=== Clustering ===")
    labels, embeddings, representatives = cluster_drafts(drafts, config)

    print("\n=== Synthesizing ===")
    synthesis = synthesize(question, representatives, config)

    total_calls = config["consensus"]["num_samples"] + 1  # samples + synthesizer
    return synthesis, drafts, labels, representatives, total_calls
```

**Step 4: Demonstrate on a long-form question.**

```python
long_form_q = "What makes a great study group, and what are the biggest pitfalls to avoid?"
synthesis, drafts, labels, reps, calls = run_consensus(long_form_q, config)
print(f"\n=== SYNTHESIZED ANSWER ({calls} model calls) ===\n{synthesis}")
```

Expected output (abbreviated):

```
=== Sampling 6 drafts ===
  Sample 1/6: A great study group needs clear goals and...
  ...

=== Clustering ===
Clustering: 6 drafts -> 3 clusters (threshold=0.3)
  Cluster 0 (support=3): A great study group needs clear goals...
  Cluster 1 (support=2): The key ingredients are...
  Cluster 2 (support=1): Study groups work best when...

=== Synthesizing ===

=== SYNTHESIZED ANSWER (7 model calls) ===
A great study group combines clear shared goals, consistent meeting times, and mutual accountability...
Note: there was minor disagreement about whether size or structure matters more.
```

### Troubleshooting — Part 2

**`AgglomerativeClustering` raises `ValueError: The number of samples is too small`**
This happens if `n_samples < 2`. Make sure `num_samples >= 2` in your config. For clustering to be meaningful, use at least 5 samples.

**All drafts end up in one giant cluster**
Your `distance_threshold` is too large. Decrease it from 0.3 to 0.15 and re-run. If everything is still one cluster, your question may produce very uniform answers — try a more open-ended question that generates diverse responses.

**All drafts end up in separate clusters (no merging)**
Your `distance_threshold` is too small. Increase it from 0.3 to 0.5. This is common with very short drafts (under 50 words) because their embedding geometry is more spread out.

---

> **Checkpoint: Before moving to Part 3, make sure you can answer:**
> 1. Why do we normalize the embedding vectors before computing cosine distance? What goes wrong if we skip normalization?
> 2. What is the purpose of the support count in the synthesizer's context? What would happen if you gave the synthesizer all 6 raw drafts instead of one representative per cluster?
> 3. What does it mean for a question to be "too easy" for stochastic consensus? What kind of question would produce maximum cluster diversity?

---

## Part 3: The Shootout

Construct a labeled task set of at least ten questions with checkable answers (arithmetic word problems with traps work well). At **matched call budgets**, compare:

1. Single shot (one agent, one sample).
2. Self-consistency (sample $$k$$, majority vote, no debate rounds).
3. Full debate (your Part 1 system).

Report accuracy and total model calls per condition. Then find and document at least one **correlated failure**: a question where every agent agrees on the same wrong answer. Explain, using the independence argument from class, why no aggregation strategy could have saved you, and what non-LLM addition (a tool, retrieval) would.

### Step-by-step guide

**Step 1: Build your labeled task set.**

Good task types for this comparison:
- Arithmetic word problems where one step is easy to get wrong (e.g., a percentage of a percentage)
- Multi-step logic puzzles with a common false shortcut
- Questions with a well-known but incorrect folk belief as a trap

```python
SHOOTOUT_TASKS = [
    {"id": "S01", "question": "A shirt costs $40 and is on sale for 25% off. You also have a coupon for 10% off the sale price. What is the final price?", "answer": "27.00"},
    {"id": "S02", "question": "If you fold a piece of paper in half 10 times, how many layers thick is it?", "answer": "1024"},
    {"id": "S03", "question": "A store buys a jacket for $60 and marks the price up by 50%. During a sale, the marked-up price is then reduced by 50%. What is the sale price?", "answer": "45.00"},
    {"id": "S04", "question": "Three friends split a $75 dinner bill evenly, and then each person adds a $5 tip of their own. How much does each person pay in total?", "answer": "30.00"},
    {"id": "S05", "question": "A town's population of 8,000 grows by 10% one year and then shrinks by 10% the next year. What is the population after both years?", "answer": "7920"},
    {"id": "S06", "question": "How many bones are in the typical adult human body?", "answer": "206"},
    {"id": "S07", "question": "What is the capital city of Australia?", "answer": "Canberra"},
    {"id": "S08", "question": "In what year did humans first walk on the Moon?", "answer": "1969"},
    {"id": "S09", "question": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost, in cents?", "answer": "5"},
    {"id": "S10", "question": "A patch of lily pads doubles in size every day. It covers the entire lake after 48 days. After how many days did it cover half the lake?", "answer": "47"},
]
# S03-S05 are arithmetic word problems with a trap step; S06-S08 are short factual
# questions with verifiable answers; S09-S10 are classic reasoning puzzles where the
# intuitive-but-wrong answer (10 cents; 24 days) is a well-known misconception --
# good candidates for a correlated failure, where every agent agrees on the same
# wrong answer. Feel free to swap in questions of your own, keeping this mix.
```

**Step 2: Run all three conditions at matched call budgets.**

For a budget of B=6 calls per question:
- Single shot: 1 call (use the remaining 5 as wasted budget — or run 6 single shots and majority-vote them as "self-consistency")
- Self-consistency: 6 samples, majority vote
- Full debate: 3 agents × 2 rounds = 6 calls

```python
import csv

def single_shot(question, config, seed_offset=0):
    """One call, no aggregation."""
    messages = [{"role": "user", "content": f"{question}\n\nEnd your response with: ANSWER: <your answer>"}]
    payload = {
        "model": config["model"],
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.2, "seed": config["debate"]["seed_base"] + seed_offset}
    }
    r = requests.post(config["ollama_url"], json=payload, timeout=60)
    text = r.json()["message"]["content"]
    return extract_answer(text, "single", 1)

def self_consistency(question, config, k=6):
    """Sample k answers and take majority vote."""
    answers = []
    for i in range(k):
        ans = single_shot(question, config, seed_offset=i)
        if ans:
            answers.append(ans)
    if not answers:
        return None
    return Counter(answers).most_common(1)[0][0]

results = []
for task in SHOOTOUT_TASKS:
    q, expected = task["question"], task["answer"]
    print(f"\n=== {task['id']} ===")

    # Single shot
    ss_answer = single_shot(q, config)
    ss_correct = expected.lower() in (ss_answer or "").lower()

    # Self-consistency (6 samples = 6 calls)
    sc_answer = self_consistency(q, config, k=6)
    sc_correct = expected.lower() in (sc_answer or "").lower()

    # Full debate (3 agents × 2 rounds = 6 calls)
    final_answers, transcripts, debate_calls = run_debate(q, config)
    debate_answer = majority_vote(final_answers)
    debate_correct = expected.lower() in (debate_answer or "").lower()

    print(f"  Single shot: {ss_answer} ({'CORRECT' if ss_correct else 'WRONG'})")
    print(f"  Self-consistency: {sc_answer} ({'CORRECT' if sc_correct else 'WRONG'})")
    print(f"  Debate: {debate_answer} ({'CORRECT' if debate_correct else 'WRONG'})")

    results.append({
        "id": task["id"], "expected": expected,
        "single_answer": ss_answer, "single_correct": ss_correct, "single_calls": 1,
        "sc_answer": sc_answer, "sc_correct": sc_correct, "sc_calls": 6,
        "debate_answer": debate_answer, "debate_correct": debate_correct, "debate_calls": debate_calls,
    })

# Print summary
for condition, calls_key, correct_key in [
    ("Single shot", "single_calls", "single_correct"),
    ("Self-consistency", "sc_calls", "sc_correct"),
    ("Debate", "debate_calls", "debate_correct"),
]:
    acc = sum(r[correct_key] for r in results) / len(results)
    avg_calls = sum(r[calls_key] for r in results) / len(results)
    print(f"{condition}: accuracy={acc:.1%}, avg_calls={avg_calls:.1f}")
```

Expected output format:

```
Single shot: accuracy=60.0%, avg_calls=1.0
Self-consistency: accuracy=70.0%, avg_calls=6.0
Debate: accuracy=80.0%, avg_calls=6.0
```

**Step 3: Document a correlated failure.**

Find a question in your task set (or add one) where all agents agree on the same wrong answer. Paste all agents' verbatim `ANSWER:` lines alongside the correct answer in your readme. Then explain in your writeup: why does aggregation fail here, and what non-LLM resource (a calculator, a lookup, retrieval from a factual source) would fix it?

### Troubleshooting — Part 3

**Self-consistency and debate produce identical results on every task**
For debate to outperform self-consistency, some agents need to change their mind in revision rounds. This requires questions where initial diversity exists. Add more word problems with common arithmetic pitfalls — single-step questions rarely produce diversity.

**All three conditions fail on the same questions (not just correlated failure)**
Your task set may be too hard for the model you are using. Add some easier questions to get a spread of correct/incorrect answers, so the comparison has signal. If everything is wrong, you cannot see which method is better.

**One agent never produces an ANSWER: line**
Check the temperature and seed for that agent. At very high temperature (>1.0) the model output can be incoherent. Cap temperatures at 0.9 in your `temperature_schedule`.

---

> **Checkpoint: Before moving to Part 4, make sure you can answer:**
> 1. On your task set, which condition had the best accuracy? Did it also have the highest call count? What does that tradeoff imply about deployment decisions?
> 2. Describe your correlated failure in one sentence. Why could neither majority vote nor debate fix it?
> 3. Name the non-LLM resource that would fix your correlated failure. How would you integrate it into your existing agent architecture (think back to the Local Agent Lab's tool pattern)?

---

## Part 4: Threshold Sensitivity

Vary the clustering `distance_threshold` across at least three values and report how the cluster structure, and therefore the synthesized consensus, changes on your long-form question. Conclude with one paragraph: who should own this parameter in a deployed system, and how would you document its setting?

### Step-by-step guide

**Step 1: Run consensus at three threshold values.**

```python
long_form_q = "What makes a great study group, and what are the biggest pitfalls to avoid?"
thresholds = [0.1, 0.3, 0.5]  # tight, medium, loose

for threshold in thresholds:
    config["consensus"]["distance_threshold"] = threshold
    synthesis, drafts, labels, reps, calls = run_consensus(long_form_q, config)
    num_clusters = len(set(labels))
    print(f"\n=== Threshold = {threshold} ===")
    print(f"Clusters: {num_clusters}")
    print(f"Synthesis (first 200 chars): {synthesis[:200]}...")
```

Expected output pattern:

```
=== Threshold = 0.1 ===
Clusters: 6   <- each draft is its own cluster
Synthesis (first 200 chars): There were 6 distinct perspectives on what makes a great study group...

=== Threshold = 0.3 ===
Clusters: 3   <- moderate merging
Synthesis (first 200 chars): A great study group combines clear goals (supported by 3 samples)...

=== Threshold = 0.5 ===
Clusters: 1   <- everything merged
Synthesis (first 200 chars): A great study group needs...
```

**Step 2: Tabulate and write your conclusion.**

In your readme, create a table:

| Threshold | Clusters | Synthesis character |
|-----------|----------|---------------------|
| 0.1 | 6 | Highly fragmented; all views presented equally |
| 0.3 | 3 | Balanced; majority position emerges |
| 0.5 | 1 | Over-merged; diversity lost |

Then answer: who should own this parameter — the system developer, the deployer, or the end user? What documentation would help them choose a value?

### Troubleshooting — Part 4

**All thresholds produce the same number of clusters**
Your drafts may be nearly identical (low diversity from sampling). Increase `sample_temperature` to 0.9 or 1.0, or use a more open-ended question. You can also inspect the actual pairwise cosine distances with `1 - (normed @ normed.T)` to see what distances you are working with.

**Threshold 0.1 produces fewer clusters than threshold 0.3**
This is unexpected — a lower threshold should produce more (tighter) clusters. Check that you are using `distance_threshold` as an upper bound for merging (not a lower bound). With `AgglomerativeClustering`, lower threshold = more clusters.

---

> **Checkpoint: Before writing your deliverables, make sure you can answer:**
> 1. At what threshold did the synthesizer produce the most useful response on your long-form question? Why?
> 2. What is the danger of setting the threshold too low? What is the danger of setting it too high?
> 3. If you were deploying this system for a company's internal knowledge base, who would you recommend owns the threshold parameter, and what guidance would you write in the documentation?

---

## Deliverables

Submit a ZIP containing your code, JSON configuration, task set with labels, comparison results (CSV or table), debate and consensus transcripts for at least two questions each, the correlated failure analysis, pair log, and a readme writeup of approximately two pages. Ensure reproducibility by fixing random seeds where determinism is intended and listing software version information.

## Learning Log

Keep a metacognitive learning log for this lab in your readme: in the spirit of multiple means of action and expression, you may respond to each prompt in prose, in bullet points, or with an annotated diagram — whichever best conveys your thinking. (Prompt 4 adapts the AI-Assisted Learning Template by Marc Watkins.)

1. **What I built.** One paragraph, in plain language that a friend outside of computer science could follow (this is deliberate practice in writing for multiple audiences).
2. **What surprised me.**
3. **What I verified and how.** Evidence, not vibes.
4. **How I used AI during this lab**, and what I learned from that use.
5. **What I'd tell the next student** before they start.
6. **One open question I still have.**

### Lab-specific prompts

- Debate and consensus spend extra computation to buy reliability. Name one decision in your own life where you would pay that cost and one where you would not. Map each onto a condition from your shootout (single-shot, self-consistency, or debate), and explain what feature of the task — not just the cost — drives the choice.
- Your synthesizer "follows the majority." Name a real scenario — in medicine, law, or public policy — where the majority of experts can all be wrong in the same direction, and explain what mechanism (not more samples) would be needed to catch that error.
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

## Extension Challenges

These are optional and carry no extra credit.

**Challenge 1 (moderate): Implement a judge agent.**
Instead of majority vote, add an aggregation option that sends all final-round debate answers to a judge agent (a separate model call) that chooses the best answer and explains why. Compare the judge's accuracy to majority vote on your task set. Does the judge ever pick the minority answer — and when it does, is it usually right or wrong?

**Challenge 2 (harder): Adaptive sampling.**
In the consensus pipeline, start with 3 samples. If all 3 land in one cluster, you are done. If they span more than 2 clusters, sample 3 more. Continue until either a clear majority cluster exists or you hit a call budget of 9. Measure whether adaptive sampling reduces average cost while maintaining accuracy compared to always sampling 6.

**Challenge 3 (hardest): Cross-architecture comparison.**
Run the same 10-task shootout using a second model available via `ollama pull` (e.g., `mistral` or `phi3`). Compare both models across all three conditions. Do the two models have different correlated failure patterns? Does combining agents from two different model families reduce correlated failures compared to using the same model for all agents?
