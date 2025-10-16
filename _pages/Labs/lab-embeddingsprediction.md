---
layout: assignment
permalink: Labs/EmbeddingsPrediction
title: "Lab: Embeddings and Prediction"

info:
  points: 100
  goals:
    - Explain how embeddings encode semantic meaning for predictive and retrieval tasks.
    - "Implement an end-to-end pipeline: upload data, compute embeddings, train a classifier, and retrieve neighbors."
    - Demonstrate cosine similarity as a measure of closeness between texts, with examples.
    - Visualize embedding spaces and interpret clusters relative to labels.
    - Understand algorithms used (Logistic Regression, PCA, k-NN) and their role in the pipeline.
    - Experiment with embedding models, distance metrics, and classifiers to test robustness.
    - Deliver a reproducible notebook with sample data, saved artifacts, and explanatory commentary.

  rubric:
    - weight: 30
      description: Implementation
      preemerging: Code runs and produces embeddings for input texts.
      beginning: Uploads a file, computes embeddings, and trains a basic classifier.
      progressing: Includes retrieval, similarity checks, and plots of embedding space.
      proficient: Provides ablations, visualization, and a well-structured notebook with reproducibility.
    - weight: 20
      description: Algorithmic Correctness and Reasoning
      preemerging: Reports accuracy only.
      beginning: Explains model choice and similarity metric; reports accuracy and F1.
      progressing: Includes confusion matrix, similarity demos, and error analysis.
      proficient: Provides principled comparisons of normalization, distance metrics, and interprets results.
    - weight: 20
      description: Code Quality and Documentation
      preemerging: Functions are provided with comments.
      beginning: Clear, modular code with meaningful names.
      progressing: Includes type hints, abstractions, and error handling.
      proficient: Excellent readability, modularity, and clear instructional comments.
    - weight: 10
      description: Design Report
      preemerging: Short summary of approach and results.
      beginning: Includes metrics and at least one visualization.
      progressing: Includes ablations, limitations, and discussion of retrieval.
      proficient: Clear narrative linking theory, design, results, and implications.
    - weight: 10
      description: Report and Reflection
      preemerging: Submits a brief summary with minimal detail, lacking connection to generative AI or similarity.
      beginning: Provides a dataset and experiment summary with some discussion of similarity and its role in predictions.
      progressing: Explains how similarity underpins retrieval and prediction; connects to concrete experimental results; includes thoughtful error analysis.
      proficient: Offers a well-structured, critical reflection linking similarity, embeddings, and generative AI prediction. Clearly articulates how their findings connect to broader concepts of text prediction, RAG, and user-facing AI systems.
    - weight: 10
      description: Submission Completeness
      preemerging: Notebook and sample data included.
      beginning: Requirements and fixed seeds included.
      progressing: Artifacts saved and reproducible.
      proficient: Turn-key reproducibility with neat packaging of code, data, and report.

tags:
  - embeddings
  - classification
  - visualization
  - retrieval
---

# Lab: Embeddings and Prediction

## Purpose

This lab teaches how to transform raw text into **vector embeddings** and then use them in different machine learning contexts:  
- As **features for prediction** with classifiers like Logistic Regression.  
- As **signals for retrieval** to find similar documents.  
- As **points in a space** that can be visualized and interpreted.  

You will upload a dataset of short text samples, encode them as embeddings, train a classifier, retrieve similar entries, compute pairwise similarity, and plot the results.

---

## Sample CSV to Upload

Save the following into a file named **`sample_data.csv`**. Upload it when prompted in the notebook. It has two columns: `text` and `label` (1 = positive, 0 = negative).

```csv
text,label
Love the battery life and the keyboard feel.,1
The screen is bright and colors are accurate.,1
Excellent build quality; runs fast and cool.,1
Setup was straightforward; documentation is clear.,1
Great value for the price, would recommend.,1
Battery drains quickly and the fan is noisy.,0
Screen flickers under load; colors look washed out.,0
Feels cheap; performance is sluggish and hot.,0
Setup was confusing; the docs are incomplete.,0
Overpriced for what it offers; would not recommend.,0
```

---

## Environment Setup

Install the required libraries:

```python
!pip install sentence-transformers scikit-learn pandas numpy matplotlib tqdm umap-learn faiss-cpu
```

---

## Steps

Each step includes: **What to Do, How to Do It, What It Does, How It Works.**

### Step 1: Upload and Read a File

```python
import pandas as pd
from google.colab import files

uploaded = files.upload()
filename = next(iter(uploaded))
df = pd.read_csv(filename)
print(df.head())
```

- **What It Does:** Loads your dataset into memory.  
- **How It Works:** Colab prompts you for a file; pandas parses it.  

---

### Step 2: Load an Embedding Model

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
```

- **What It Does:** Loads a pretrained sentence embedding model.  
- **How It Works:** Maps text into dense vectors where semantic similarity corresponds to closeness.  

---

### Step 3: Compute Embeddings

```python
import numpy as np

def compute_embeddings(texts, normalize=True):
    vecs = model.encode(texts, show_progress_bar=True)
    vecs = np.asarray(vecs, dtype=np.float32)
    if normalize:
        norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12
        vecs = vecs / norms
    return vecs

X = compute_embeddings(df["text"].tolist(), normalize=True)
y = df["label"].to_numpy()
```

- **What It Does:** Converts text into fixed-length vectors.  
- **How It Works:** Transformer model encodes meaning; normalization makes cosine similarity reliable.  

---

### Step 4: Train a Classifier

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

clf = LogisticRegression(solver="liblinear", random_state=42)
clf.fit(X_train, y_train)
```

- **What It Does:** Learns to classify positive vs. negative.  
- **How It Works:** Logistic Regression computes weights on embedding dimensions and outputs probabilities.  

---

### Step 5: Evaluate the Classifier

```python
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

y_pred = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Macro-F1:", f1_score(y_test, y_pred, average="macro"))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nReport:\n", classification_report(y_test, y_pred))
```

- **What It Does:** Computes metrics.  
- **How It Works:** Compares predictions to true labels.  

---

### Step 6: Query with Nearest Neighbors

```python
from sklearn.neighbors import NearestNeighbors

knn = NearestNeighbors(n_neighbors=3, metric="cosine")
knn.fit(X)

query_text = "This product is fast and reliable."
X_query = compute_embeddings([query_text])

distances, indices = knn.kneighbors(X_query)
for i, idx in enumerate(indices[0]):
    print(f"Neighbor {i+1}: {df.iloc[idx]['text']} (label={df.iloc[idx]['label']}, d={distances[0][i]:.3f})")
```

- **What It Does:** Finds nearest neighbors of a query.  
- **How It Works:** k-NN searches embedding space with cosine distance.  

---

### Step 7: Compare Document Similarities

```python
from numpy import dot
from numpy.linalg import norm

i, j = 0, 1
sim = dot(X[i], X[j]) / (norm(X[i]) * norm(X[j]))
print("Text A:", df.iloc[i]["text"])
print("Text B:", df.iloc[j]["text"])
print("Cosine Similarity:", sim)
```

- **What It Does:** Measures similarity between two reviews.  
- **How It Works:** Cosine similarity compares the angle between two embedding vectors.  

---

### Step 8: Visualize the Embedding Space

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

pca = PCA(n_components=2, random_state=42)
Z = pca.fit_transform(X)

plt.figure(figsize=(6,5))
plt.scatter(Z[:,0], Z[:,1], c=y, cmap="coolwarm", s=80)
plt.title("PCA of Embeddings")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.show()
```

- **What It Does:** Projects embeddings to 2D and plots them.  
- **How It Works:** PCA finds directions of maximum variance in high-dimensional space.  

---

### Step 9: Comparing the Effect of Normalized Features

```python
for normalize in [True, False]:
    X_tmp = compute_embeddings(df["text"].tolist(), normalize=normalize)
    X_train, X_test, y_train, y_test = train_test_split(X_tmp, y, test_size=0.3, random_state=42)
    clf = LogisticRegression(solver="liblinear", random_state=42).fit(X_train, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"normalize={normalize}: Accuracy={acc:.3f}")
```

- **What It Does:** Compares normalized vs. unnormalized embeddings.  
- **How It Works:** Normalization changes geometry of similarity, often improving cosine metrics.  

---

## Experiments to Try (Step by Step)

These experiments extend the core lab. For each, you will:  
1. Add some code to experiment with additional features
2. Run it and observe the output.  
3. Reflect on what the result means.  

---

### 1. Data Exploration

**Goal:** Understand your dataset before using embeddings.

**Steps:**
1. Count how many examples have label = 1 and label = 0.  
   *Hint:* Use `df['label'].value_counts()`.  
2. Compute the average length of the text (number of words).  
   *Hint:* Apply a function to `df['text']` that splits on spaces and gets length.  
3. Find the most common words.  
   *Hint:* Use `collections.Counter` on all words across the dataset.  

**Reflection:** Does your dataset have balanced labels? Do certain words dominate one class?

---

### 2. Embedding Models

**Goal:** See how changing the embedding model changes results.

**Steps:**
1. Replace `"all-MiniLM-L6-v2"` with `"all-mpnet-base-v2"` in your `SentenceTransformer` call.  
2. Recompute embeddings and rerun the classifier and retrieval steps.  
3. Compare performance and neighbor quality between the two models.

**Reflection:** Which model performed better? Did neighbors retrieved by the larger model feel more semantically accurate?

---

### 3. Interactive Similarity Demo

**Goal:** Act like an AI user: type a query and see which documents are most similar.

**Steps:**
1. Add a cell with `input("Enter a text query: ")` to collect custom text.  
2. Embed the query text with `compute_embeddings`.  
3. Compute cosine similarity between this query vector and **all dataset embeddings**.  
   *Hint:* If embeddings are normalized, cosine similarity is just a dot product.  
4. Sort the results and print the **top 3 most similar documents**, showing the text, label, and similarity score.

**Skeleton Code:**
```python
user_query = input("Enter a text query: ")
X_query = compute_embeddings([user_query])

sims = X @ X_query.T  # cosine similarity if normalized
sims = sims.flatten()
top_indices = sims.argsort()[::-1][:3]

for idx in top_indices:
    print(f"Doc: {df.iloc[idx]['text']} | Label={df.iloc[idx]['label']} | Similarity={sims[idx]:.3f}")
```

**Reflection:** Did the top documents feel relevant to your query? From a user’s perspective, does this retrieval feel convincing?

---

### 4. Similarity Checks

**Goal:** Test the intuition behind embeddings.

**Steps:**
1. Pick two texts you think are very close in meaning.  
2. Pick two texts you think are very different.  
3. Compute cosine similarity for both pairs.  

**Reflection:** Did the model agree with your intuition? Where did it surprise you?

---

### 5. Classifier Alternatives

**Goal:** Try different models on embeddings.

**Steps:**
1. Replace Logistic Regression with SVM (`from sklearn.svm import SVC`).  
2. Optionally, try k-NN as a classifier (`from sklearn.neighbors import KNeighborsClassifier`).  
3. Train and evaluate using the same metrics.

**Reflection:** Which classifier gave the best results? Why do you think that happened?

---

### 6. Retrieval Variants

**Goal:** See how changing distance metrics and k affects results.

**Steps:**
1. In the k-NN setup, change `metric="cosine"` to `metric="euclidean"`.  
2. Change `n_neighbors` from 3 to 5.  
3. Run retrieval again.

**Reflection:** Did the neighbors retrieved change meaningfully? Which metric seemed better for this dataset?

---

### 9. Error Analysis

**Goal:** Look at mistakes and think critically about them.

**Steps:**
1. After evaluation, collect the examples where the classifier was wrong.  
   *Hint:* Compare `y_pred` to `y_test` and select mismatches.  
2. Print out the text, true label, and predicted label for a few cases.  

**Reflection:** Why did the classifier get these wrong? Did the embeddings miss nuance, or was the dataset too small/noisy?

---

---

## Final Report and Reflection

After completing the experiments, write a **short report (2–4 pages)** that explains what you found and what you learned. Your report should include both **technical observations** and **conceptual reflections**.

### What to Include

1. **Dataset Summary**  
   - Describe the dataset you worked with (size, labels, examples).  
   - Note any preprocessing or modifications you made.

2. **Experiment Results**  
   - Summarize your key results:  
     - Classifier accuracy and F1 score.  
     - Examples of similarity scores (high vs. low).  
     - How your results changed with/without normalization.  

3. **Error Analysis**  
   - Show examples of misclassified texts.  
   - Suggest why the model may have failed in these cases.  
   - Discuss whether the errors are due to data, embeddings, or model choice.

4. **Generative AI Connection**  
   - Reflect on how the similarity you measured between documents relates to how **generative AI predicts text**.  
   - Consider:  
     - When you input a query, the system finds vectors that are close in embedding space.  
     - Generative models use this similarity to retrieve context and to decide “what comes next” in text prediction.  
     - How does neighbor voting (your k-NN demo) resemble what happens in retrieval-augmented generation (RAG)?  
     - What are the limitations of this approach?  

5. **Personal Reflection**  
   - In your own words, explain how embeddings make **prediction** and **generation** possible.  
   - What did you learn about the role of similarity?  
   - How might this shape your understanding of AI systems you use every day (like ChatGPT, search, or recommendation engines)?

---

**Deliverable:** Upload your report (PDF or Markdown) along with your code and figures.  
