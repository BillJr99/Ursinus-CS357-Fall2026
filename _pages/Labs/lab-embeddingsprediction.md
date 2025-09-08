---
layout: assignment
permalink: Labs/EmbeddingsPrediction
title: "Lab: Embeddings and Prediction"

info:
  points: 100
  goals:
    - Explain and contrast how vector embeddings underpin predictive models (as features) versus generative systems (as retrieval signals), including the role of cosine vs. dot-product similarity and L2 normalization.
    - Construct an end-to-end pipeline that transforms raw text into sentence embeddings and uses them for supervised prediction (binary classification) and retrieval-augmented explanation.
    - Implement, train, and evaluate a linear classifier on fixed embeddings using principled metrics (accuracy, macro-F1), with a confusion matrix and error analysis.
    - Build a k-NN semantic index over embeddings and retrieve neighbors for a query to inform a templated “generative” rationale.
    - Visualize the embedding space via dimensionality reduction and interpret structure relative to labels.
    - Perform a small ablation (e.g., normalization on/off, cosine vs. Euclidean) and justify design choices with empirical evidence.
    - Deliver a fully reproducible artifact (requirements, seeds, saved vectors/model, run instructions).

  rubric:
    - weight: 30
      description: Implementation
      preemerging: End-to-end code runs and produces embeddings with a single predictive result and a basic retrieval demo.
      beginning: Clean modular code; trains a classifier on embeddings; builds a k-NN index; shows retrieval examples.
      progressing: Adds ablations (e.g., normalization vs. none, cosine vs. Euclidean); includes visualization; saves artifacts.
      proficient: Robust, well-structured pipeline with CLI or notebook sections; reproducibility (seeds, reqs); clear modularity enabling further experiments.
    - weight: 30
      description: Algorithmic Correctness and Reasoning
      preemerging: Describes why embeddings help; reports one metric (e.g., accuracy).
      beginning: Explains model choice, similarity metric, and train/test split; reports multiple metrics and interprets them.
      progressing: Conducts error analysis (e.g., confusion matrix, hardest examples) and ties errors to embedding properties.
      proficient: Provides principled comparisons and sound conclusions about design choices (e.g., effect of normalization, model capacity limits) with evidence.
    - weight: 20
      description: Code Quality and Documentation
      preemerging: Functions with docstrings and inline comments for non-obvious steps.
      beginning: Consistent style, meaningful names, and usage instructions; exceptions handled with informative messages.
      progressing: Thoughtful abstractions (data, encode, train, eval, retrieve, generate); type hints; clear logging.
      proficient: Excellent readability and maintainability; clear separation of concerns; thorough docstrings; concise, instructive comments.
    - weight: 10
      description: Design Report
      preemerging: Summarizes goals, approach, and data; includes a brief result.
      beginning: Justifies metric choices and distance metrics; shows at least one visualization.
      progressing: Presents ablations, limitations, and qualitative retrieval cases with discussion.
      proficient: Well-structured narrative connecting theory → design → results → implications; actionable future work.
    - weight: 10
      description: Submission Completeness
      preemerging: Script/notebook, sample data, and run instructions.
      beginning: Includes requirements file, fixed seeds, and saved artifacts (e.g., vectors, model).
      progressing: Reproducible steps (commands), figures, and a short report (PDF/Markdown).
      proficient: Turn-key reproducibility; validated results; neat packaging of code, data, and report.

tags:
  - rag
  - embeddings
  - classification
  - visualization
---

# Overview

**Embeddings** map discrete objects (e.g., text) into points in a continuous vector space so that semantic proximity corresponds to geometric proximity. In **predictive** settings, fixed embeddings serve as features for classical learners (e.g., Logistic Regression). In **generative** settings, embeddings power **retrieval-augmented generation (RAG)**: we retrieve semantically similar items to condition or inform a response.

This lab guides you through a complete miniature pipeline:

1. Build a tiny labeled text dataset.
2. Compute sentence embeddings.
3. Train and evaluate a classifier on those embeddings.
4. Construct a k-NN semantic index and retrieve neighbors for a query.
5. Compose a simple templated “generative” explanation using retrieved context.
6. Visualize embedding geometry and run a small ablation.

---

## Deliverables

- **Code**: a single notebook or script (`lab_embeddings.py` or `.ipynb`) implementing the full pipeline.
- **Artifacts**: saved embeddings (`.npy`/`.parquet`), trained model (`.pkl`), and a figure (`.png`) of the 2‑D projection.
- **Report** (2–4 pages): motivation, design, metrics, visualization, error analysis, and 1–2 ablations.
- **Instructions**: `README.md` with environment setup, commands, and expected outputs.

---

## Environment Setup

Create and activate a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install sentence-transformers scikit-learn pandas numpy matplotlib tqdm
# optional extras for advanced work
pip install umap-learn faiss-cpu
```

Create a **minimal `requirements.txt`**:

```text
sentence-transformers
scikit-learn
pandas
numpy
matplotlib
tqdm
# optional
umap-learn
faiss-cpu
```

Set a **fixed seed** for reproducibility (`SEED = 42` in code).

---

# Tutorial: Step-by-Step (Well‑Annotated Python)

> You may place this in a single file (e.g., `lab_embeddings.py`) or in a notebook. The code is deliberately verbose and pedagogical.

```python
#!/usr/bin/env python
"""
Lab: Embeddings and Prediction (tutorial script)

This script demonstrates:
  1) Building a tiny labeled dataset
  2) Computing sentence embeddings
  3) Training a classifier on embeddings
  4) k-NN retrieval over embeddings
  5) A simple, templated "generative" explanation using retrieved context
  6) Visualization and small ablations

Run:
  python lab_embeddings.py

Dependencies:
  sentence-transformers, scikit-learn, pandas, numpy, matplotlib, tqdm
"""

import os
import sys
import json
import math
import traceback
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

import numpy as np
import pandas as pd
from tqdm import tqdm

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Embedding model (Small, fast, widely used)
from sentence_transformers import SentenceTransformer


SEED = 42
RNG = np.random.RandomState(SEED)


def set_global_seed(seed: int = SEED) -> None:
    """Set seeds for reproducibility."""
    np.random.seed(seed)


@dataclass
class Example:
    text: str
    label: int  # 0 = negative, 1 = positive


def build_toy_reviews() -> pd.DataFrame:
    """
    Construct a tiny labeled dataset of product-like reviews.
    In practice, replace/extend with your own domain data.
    """
    positive = [
        "Love the battery life and the keyboard feel.",
        "The screen is bright and colors are accurate.",
        "Excellent build quality; runs fast and cool.",
        "Setup was straightforward; documentation is clear.",
        "Great value for the price, would recommend.",
        "The model generalizes well on my test set.",
        "Impressive latency reduction after the update.",
        "Support team was responsive and helpful.",
        "The drone hovered very steadily in windy conditions.",
        "The interface is intuitive and polished.",
    ]
    negative = [
        "Battery drains quickly and the fan is noisy.",
        "Screen flickers under load; colors look washed out.",
        "Feels cheap; performance is sluggish and hot.",
        "Setup was confusing; the docs are incomplete.",
        "Overpriced for what it offers; would not recommend.",
        "The model overfits badly; validation loss skyrockets.",
        "Latency increased; the patch introduced regressions.",
        "Support is unresponsive and dismissive.",
        "The drone lost GPS lock repeatedly and drifted.",
        "The interface is clunky and inconsistent.",
    ]

    rows = [Example(t, 1) for t in positive] + [Example(t, 0) for t in negative]
    RNG.shuffle(rows)

    df = pd.DataFrame([{"text": r.text, "label": r.label} for r in rows])
    return df


def load_embedder(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Load a sentence-transformers model. This returns fixed embeddings for text.
    """
    try:
        model = SentenceTransformer(model_name)
        return model
    except Exception as e:
        print(f"[load_embedder] Error loading model '{model_name}': {e}")
        traceback.print_exc()
        raise


def compute_embeddings(texts: List[str],
                       model: SentenceTransformer,
                       normalize: bool = True) -> np.ndarray:
    """
    Encode a list of texts into embeddings.

    Args:
        texts: raw texts
        model: loaded sentence-transformers model
        normalize: if True, L2-normalize vectors (recommended for cosine similarity)
    """
    try:
        vecs = model.encode(texts, show_progress_bar=False)
        vecs = np.asarray(vecs, dtype=np.float32)
        if normalize:
            # L2-normalization yields unit vectors; cosine similarity reduces to dot product
            norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12
            vecs = vecs / norms
        return vecs
    except Exception as e:
        print(f"[compute_embeddings] Failed to encode texts: {e}")
        traceback.print_exc()
        raise


def train_classifier(X: np.ndarray, y: np.ndarray, C: float = 1.0) -> LogisticRegression:
    """
    Train a simple linear classifier on top of fixed embeddings.
    Logistic Regression works well with cosine-normalized vectors.
    """
    clf = LogisticRegression(
        C=C,
        solver="liblinear",
        random_state=SEED,
        class_weight=None  # try 'balanced' if dataset is skewed
    )
    clf.fit(X, y)
    return clf


def evaluate_classifier(clf: LogisticRegression, X: np.ndarray, y: np.ndarray, label_names=("neg", "pos")) -> Dict[str, Any]:
    """
    Compute accuracy, macro-F1, confusion matrix, and a classification report.
    """
    yhat = clf.predict(X)
    acc = accuracy_score(y, yhat)
    f1 = f1_score(y, yhat, average="macro")
    cm = confusion_matrix(y, yhat)
    report = classification_report(y, yhat, target_names=label_names, digits=3)
    return {"acc": acc, "f1_macro": f1, "cm": cm, "report": report}


def build_knn_index(X: np.ndarray, metric: str = "cosine", n_neighbors: int = 5) -> NearestNeighbors:
    """
    Build a simple k-NN index using scikit-learn.
    - Use metric='cosine' with normalized vectors (recommended).
    """
    knn = NearestNeighbors(n_neighbors=n_neighbors, metric=metric, algorithm="auto")
    knn.fit(X)
    return knn


def retrieve_neighbors(knn: NearestNeighbors, X_query: np.ndarray, texts: List[str], labels: List[int], k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve top-k nearest neighbors for each query vector.
    Returns list of dicts per query, each with neighbors and distances.
    """
    distances, indices = knn.kneighbors(X_query, n_neighbors=k, return_distance=True)
    results = []
    for qi in range(X_query.shape[0]):
        neighbors = []
        for rank, (idx, dist) in enumerate(zip(indices[qi], distances[qi])):
            neighbors.append({
                "rank": int(rank + 1),
                "index": int(idx),
                "text": texts[idx],
                "label": int(labels[idx]),
                "distance": float(dist)
            })
        results.append({"query_id": qi, "neighbors": neighbors})
    return results


def templated_explanation(query_text: str, retrieved: List[Dict[str, Any]]) -> str:
    """
    Compose a simple, deterministic explanation using retrieved neighbors.
    This is NOT an LLM; it's a pedagogical "generative" template showing how
    retrieval informs a response.

    You may replace this with an LLM call conditioned on the retrieved texts
    in your extended solution (e.g., via Ollama/OpenAI).
    """
    if not retrieved:
        return f"Query: {query_text}\nNo similar examples found."
    neigh = retrieved[0]["neighbors"]
    pos_votes = sum(1 for n in neigh if n["label"] == 1)
    neg_votes = len(neigh) - pos_votes
    verdict = "positive" if pos_votes >= neg_votes else "negative"

    lines = [
        f"Query: {query_text}",
        f"Prediction by neighbor voting: **{verdict.upper()}** (pos={pos_votes}, neg={neg_votes})",
        f"Most similar examples (cosine distances):"
    ]
    for n in neigh[:3]:
        lbl = "POS" if n["label"] == 1 else "NEG"
        lines.append(f"  - [{lbl}] d={n['distance']:.3f}: {n['text']}")
    lines.append("Explanation: The retrieved examples share key phrases and sentiment cues; "
                 "neighbor voting yields the final prediction. Replace this template with an LLM-based "
                 "generator to produce richer natural-language rationales (RAG).")
    return "\n".join(lines)


def plot_embedding_pca(X: np.ndarray, y: np.ndarray, out_path: str = "embeddings_pca.png") -> None:
    """
    Project embeddings to 2D with PCA and save a scatter plot.
    """
    pca = PCA(n_components=2, random_state=SEED)
    Z = pca.fit_transform(X)
    plt.figure(figsize=(6, 5))
    # Colors are default; 0=neg, 1=pos; markers to distinguish
    for label, marker in [(0, "x"), (1, "o")]:
        mask = (y == label)
        plt.scatter(Z[mask, 0], Z[mask, 1], label=f"label={label}", marker=marker, alpha=0.8)
        # Note: do not set explicit colors; keep defaults.
    plt.title("PCA of Sentence Embeddings")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    print(f"[plot] Saved: {out_path}")


def ablation_normalization(texts: List[str], labels: np.ndarray, model: SentenceTransformer) -> Dict[str, Dict[str, float]]:
    """
    Compare with/without L2 normalization, keeping everything else fixed.
    """
    results = {}
    for normalize in (True, False):
        X = compute_embeddings(texts, model, normalize=normalize)
        X_tr, X_te, y_tr, y_te = train_test_split(X, labels, test_size=0.3, random_state=SEED, stratify=labels)
        clf = train_classifier(X_tr, y_tr, C=1.0)
        eval_te = evaluate_classifier(clf, X_te, y_te)
        results["normalize=" + str(normalize)] = {"acc": eval_te["acc"], "f1_macro": eval_te["f1_macro"]}
    return results


def main():
    set_global_seed()

    # 1) Data
    df = build_toy_reviews()
    print(f"[data] {len(df)} examples")
    print(df.sample(5, random_state=SEED))

    # 2) Encoder
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embedder = load_embedder(model_name=model_name)

    # 3) Embeddings (normalized for cosine)
    texts = df["text"].tolist()
    labels = df["label"].astype(int).to_numpy()
    X = compute_embeddings(texts, embedder, normalize=True)

    # 4) Split, Train
    X_train, X_test, y_train, y_test, texts_train, texts_test = train_test_split(
        X, labels, texts, test_size=0.3, random_state=SEED, stratify=labels
    )
    clf = train_classifier(X_train, y_train, C=1.0)

    # 5) Evaluate
    eval_tr = evaluate_classifier(clf, X_train, y_train)
    eval_te = evaluate_classifier(clf, X_test, y_test)
    print("[eval][train]", eval_tr)
    print("[eval][test]", eval_te)
    print("[report][test]\n" + eval_te["report"])

    # 6) Retrieval (k-NN) and templated explanation
    knn = build_knn_index(X, metric="cosine", n_neighbors=5)

    # Choose a test example as a 'query'
    query_idx = 0
    query_text = texts[query_idx]
    X_query = X[query_idx:query_idx+1]
    retrieved = retrieve_neighbors(knn, X_query, texts, labels.tolist(), k=5)
    explanation = templated_explanation(query_text, retrieved)
    print("\n[templated explanation]\n" + explanation)

    # 7) Visualization
    plot_embedding_pca(X, labels, out_path="embeddings_pca.png")

    # 8) Ablation: normalization on/off
    ab_results = ablation_normalization(texts, labels, embedder)
    import json as _json
    print("[ablation] normalization results:", _json.dumps(ab_results, indent=2))

    # 9) Save artifacts
    os.makedirs("artifacts", exist_ok=True)
    np.save("artifacts/embeddings.npy", X)
    # Save data table
    try:
        df.to_parquet("artifacts/data.parquet")
    except Exception:
        df.to_csv("artifacts/data.csv", index=False)
    # Save model
    import pickle
    with open("artifacts/logreg.pkl", "wb") as f:
        pickle.dump(clf, f)
    print("[save] artifacts saved to ./artifacts")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[main] {e}")
        traceback.print_exc()
```

---

## Conceptual Notes

- **Cosine vs. dot product**: With L2-normalized vectors, cosine similarity equals the dot product. Normalization makes magnitude differences irrelevant, focusing on direction (semantic content). Without normalization, large-magnitude vectors can dominate dot products.
- **Why linear models on embeddings?** Sentence-transformer embeddings already encode nonlinear structure; a linear separator in embedding space is often sufficient for many tasks.
- **k-NN retrieval**: With normalized vectors, use cosine distance (1 − cosine similarity). Neighbor voting offers an interpretable baseline and provides context for an explanation step.
- **Visualization**: PCA gives a quick linear projection; UMAP provides a nonlinear view (often more cluster‑separable but with tunable hyperparameters).

---

## What to Submit

1. **Code** (script or notebook) implementing the pipeline.
2. **Artifacts** (`artifacts/embeddings.npy`, `artifacts/logreg.pkl`, `embeddings_pca.png`, and saved data table).
3. **Report** (2–4 pages) including: goals, data, metrics, confusion matrix, hardest examples, ablation (e.g., normalization and/or metric), and a short discussion of implications and limitations.
4. **Reproducibility**: include `requirements.txt`, fixed seeds, and a short `README.md` with clear run instructions.

### Suggested README structure

```text
# Lab: Embeddings and Prediction
## Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Run
python lab_embeddings.py

## Outputs
- artifacts/embeddings.npy
- artifacts/logreg.pkl
- embeddings_pca.png
- Console metrics and explanation
```

---

## Extensions (Optional / Extra Credit)

- Swap in a different embedding model (e.g., `all-mpnet-base-v2`) and compare results.
- Try **Euclidean** distance vs. **cosine** in k-NN and report differences.
- Use **FAISS** for faster retrieval on larger datasets.
- Replace the `templated_explanation` with a lightweight local LLM call (e.g., via **Ollama**) conditioned on retrieved neighbors (RAG).
- Add **calibration** checks (e.g., reliability plots) for the classifier.
- Explore **class imbalance** handling (e.g., `class_weight='balanced'`).

---

## Academic Integrity

Cite any external datasets or code you adapt. If you extend with LLM calls, document prompts and parameters. Keep sensitive data out of your repository.
