<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-mlfoundations.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-mlfoundations.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Traditional Machine Learning Foundations

The agents, RAG pipelines, and embedding models we have built so far all rest on a foundation of **traditional machine learning** — the supervised and unsupervised techniques, evaluation frameworks, and statistical thinking that the field developed long before transformers, and that still drive many production systems today.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task and ensures everyone has spoken before the group commits to an answer |
| **Recorder** | Takes notes and posts the group's answers to the discussion board |
| **Presenter** | Reports the group's findings and disagreements during debrief |
| **Reflector** | Watches group process and leads the reflection prompt at the end |

---

## Key Concepts

| Term | Plain-English Definition | Course-Context Example |
|------|--------------------------|------------------------|
| **Supervised Learning** | Learning a mapping from inputs to outputs using labeled training examples — the right answers are provided in advance | Training a model on (email text → spam/not-spam) labels; similar to how we fine-tuned a classifier in the embeddings unit |
| **Regression** | A supervised task where the output is a continuous number | Predicting the relevance score of a retrieved document given a query — a number, not a category |
| **Classification** | A supervised task where the output is one of a fixed set of categories | Routing an agent's incoming message to the correct tool: "arithmetic", "search", or "none" |
| **Bias-Variance Tradeoff** | The tension between a model that is too simple (high bias, misses real patterns) and one that memorizes training data (high variance, fails on new inputs) | An agent planner that always recommends the same tool is high-bias; one that changes plan every run is high-variance |
| **Cross-Validation** | A technique for estimating how well a model generalizes, by repeatedly training on one part of the data and testing on a held-out part | Before deploying a retrieval ranker, we estimate its precision/recall on data it has never seen |
| **Ensemble Methods** | Combining predictions from multiple models so that their errors partially cancel out | Random forests (many decision trees) often outperform a single tree, just as an agent team outperforms a single agent |

---

# Part I: Supervised Learning Fundamentals

In this part, you will build a precise vocabulary for supervised learning and identify the key design choices that determine whether a model will generalize to new data. These ideas underpin every classifier and ranker we encounter for the rest of the course.

## 1. The Supervised Learning Setup

A supervised learning algorithm receives a **training set**

$$
\mathcal{D} = \{(x_1, y_1), (x_2, y_2), \ldots, (x_n, y_n)\}
$$

where each $x_i$ is an **input** (a feature vector) and each $y_i$ is the corresponding **label** (what we want to predict). The algorithm searches for a function $f$ such that $f(x) \approx y$ on new, unseen inputs — not just on the training data. Doing well only on training data is called **overfitting**.

Two broad families of supervised tasks:

- **Regression**: $y \in \mathbb{R}$ (predict a number)
- **Classification**: $y \in \{c_1, c_2, \ldots, c_k\}$ (predict a category)

The **hypothesis class** (the family of functions we search over) determines what patterns the model *can* learn. A linear model can only draw a line (or hyperplane); a decision tree carves the input space into axis-aligned rectangles; a neural network can approximate much more complex shapes.

### Critical Thinking Questions

1. We said the goal is to do well on *new, unseen* inputs — not just on the training set. Why is performance on the training set an unreliable guide to real-world usefulness?

   > *Hint: Think about what the model can do during training that it cannot do at deployment. If the model simply memorizes every $(x_i, y_i)$ pair, what does it do when it sees an $x$ that was not in the training set?*

2. In the RAG unit, we built a retriever that scored documents given a query. Identify the input $x$, the label $y$, and the hypothesis class for a simple **supervised retrieval ranker**. Is this a regression or classification problem?

   > *Hint: What information do you hand the model? What do you want it to produce? If the output is a relevance score from 0 to 10, is that a number or a category?*

3. An agent that routes incoming user messages to tools (calculator, web search, or no tool) is a classification model. List three features of the user message that might serve as informative inputs $x$.

   > *Hint: Think about words, sentence structure, punctuation, and what those signals correlate with. "What is 42 × 17?" looks very different from "Who wrote Hamlet?"*

4. A teammate proposes training the routing classifier on data collected from last semester's agent logs. Identify one reason this training data might be **biased** in a way that hurts the model's performance when deployed this semester.

   > *Hint: What changed between semesters? What kinds of queries might be underrepresented in last semester's logs?*

### Multiple Choice

[[MC]]
Which of the following is the clearest example of a **regression** problem?
- ( ) Deciding whether a support ticket should go to the billing team or the technical team
- (x) Predicting how long (in minutes) a user will spend on a course activity given their prior engagement statistics
- ( ) Labeling each sentence in an essay as "thesis", "evidence", or "analysis"
- ( ) Identifying which of five tools an agent should invoke for a given query

---

# Part II: Bias, Variance, and Model Evaluation

In this part, you will see why the training-set score is not enough, learn how cross-validation gives a more honest estimate of generalization, and run a live comparison of a single decision tree (prone to high variance) against a random forest (an ensemble that reduces it).

## 2. The Bias-Variance Tradeoff

Every prediction error can be decomposed into three sources:

$$
\text{Expected Error} = \text{Bias}^2 + \text{Variance} + \text{Irreducible Noise}
$$

- **Bias** is systematic error: the model's assumptions prevent it from fitting the true pattern, even with infinite data. A linear model fit to a curved relationship has high bias.
- **Variance** is sensitivity to the specific training set: small changes in which examples you train on produce large changes in the model. A deep decision tree that memorizes training examples has high variance.
- **Irreducible noise** is the part of the error that no model can remove — inherent randomness or missing information in the data.

The tradeoff: increasing model complexity tends to decrease bias but increase variance. Regularization, pruning, and ensemble methods are all techniques for finding a better operating point on this tradeoff.

### Critical Thinking Questions

1. A decision tree grown without any depth limit achieves 100% accuracy on training data but 62% on a held-out test set. Which source of error dominates? Explain.

   > *Hint: 100% training accuracy means the tree memorized every training example. What does that tell you about how it handles small fluctuations in the training set?*

2. A linear classifier achieves 71% accuracy on training data and 70% on test data. Is this evidence of bias, variance, or neither? What would you try next?

   > *Hint: When training and test performance are nearly identical but both are low, the model is not overfitting. What is it doing instead? What does that imply about the relationship between the features and the labels?*

3. Random forests reduce variance by training many decision trees on **bootstrap samples** (random subsets of the training data, drawn with replacement) and averaging their predictions. Explain in one sentence why averaging across many high-variance models can produce a lower-variance result.

   > *Hint: If each tree makes a different random error, what happens to those errors when you average many trees together? Think about what averaging does to random noise.*

> **Common Misconception:** It is tempting to think that a model with higher training accuracy is always better. In practice, a model that achieves 99% training accuracy and 65% test accuracy has **overfit** — it learned the noise in the training data rather than the true pattern. Always report test or cross-validation accuracy when comparing models. Training accuracy alone tells you almost nothing about real-world performance.

## 3. Cross-Validation and Ensemble Methods in Practice

Run the code cell below. It loads the Iris dataset (150 flower samples, three species, four numeric features), compares a decision tree against a random forest using 5-fold cross-validation, and reports the mean accuracy and standard deviation for each.

---

```python
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report
import numpy as np

# Load data
iris = load_iris()
X, y = iris.data, iris.target
feature_names = iris.feature_names
class_names = iris.target_names

print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(class_names)} classes")
print(f"Classes: {list(class_names)}")
print(f"Features: {list(feature_names)}\n")

# Train/test split for a final hold-out evaluation
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Training set: {X_train.shape[0]} samples")
print(f"Test set:     {X_test.shape[0]} samples\n")

# --- Decision Tree ---
dt = DecisionTreeClassifier(random_state=42)
dt_cv_scores = cross_val_score(dt, X_train, y_train, cv=5, scoring="accuracy")
dt.fit(X_train, y_train)
dt_test_acc = dt.score(X_test, y_test)

print("=== Decision Tree (no depth limit) ===")
print(f"  5-fold CV accuracy: {dt_cv_scores.mean():.3f} ± {dt_cv_scores.std():.3f}")
print(f"  Hold-out test accuracy: {dt_test_acc:.3f}")
print()

# --- Random Forest ---
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf_cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring="accuracy")
rf.fit(X_train, y_train)
rf_test_acc = rf.score(X_test, y_test)

print("=== Random Forest (100 trees) ===")
print(f"  5-fold CV accuracy: {rf_cv_scores.mean():.3f} ± {rf_cv_scores.std():.3f}")
print(f"  Hold-out test accuracy: {rf_test_acc:.3f}")
print()

# Detailed report on the test set for the random forest
y_pred = rf.predict(X_test)
print("=== Random Forest — Test Set Classification Report ===")
print(classification_report(y_test, y_pred, target_names=class_names))

# Feature importances from the forest
importances = rf.feature_importances_
ranked = np.argsort(importances)[::-1]
print("=== Feature Importances (Random Forest) ===")
for i in ranked:
    print(f"  {feature_names[i]:<30s}  {importances[i]:.4f}")
```

### Code Analysis Questions

1. The code uses `stratify=y` in `train_test_split`. Look up or reason about what this does. Why is stratification important when one class has fewer examples than the others?

   > *Hint: Iris has 50 examples per class, so stratification matters less here — but imagine a fraud-detection dataset where 98% of examples are "not fraud." Without stratification, what might your test set accidentally contain?*

2. Cross-validation reports a mean accuracy **and** a standard deviation. The decision tree's standard deviation is typically higher than the random forest's. What does a high standard deviation across folds tell you about the model's variance?

   > *Hint: Each fold uses a slightly different subset of training data. If the model's score swings widely between folds, what does that tell you about how sensitive it is to which examples it trains on?*

3. The random forest exposes `feature_importances_`. If `petal length (cm)` ranks highest, what does that mean in plain English — and why might that be more useful than the model's accuracy number alone?

   > *Hint: Feature importance tells you which inputs the model is actually using to make decisions. How might a teacher or scientist use this information differently from a software engineer?*

4. The Iris dataset is small and clean. List two ways in which a real-world classification problem (for example, routing agent messages to tools) would make this evaluation harder to trust.

   > *Hint: Think about class imbalance, distribution shift between training and deployment, label noise, and missing features.*

---

# Part III: Synthesis and Practice

In this part, you will connect the ML concepts from Parts I and II to the AI systems you have already built, and practice applying them to new design problems.

## 4. Exercises

1. *Connecting to RAG.*

   The retrieval step in a RAG pipeline scores each candidate document against the user's query and returns the top-$k$. Suppose you want to replace the cosine-similarity ranker with a **supervised** ranker trained on (query, document, relevance-label) triples.

   - Identify the input features $x$ you would extract from the query-document pair.
   - Identify the label $y$ (is this regression or classification?).
   - Propose how you would collect training data. What are the risks of using implicit signals (e.g., did the user click on the result?) instead of explicit human ratings?
   - Explain how cross-validation would let you compare your supervised ranker to the original cosine-similarity baseline before deploying it.

2. *Diagnosing a teammate's model.*

   A teammate trained a decision tree to classify user intent (question / command / greeting) and reports: "Training accuracy = 98%, validation accuracy = 61%." Write a two-paragraph diagnosis. Name the problem, explain its cause in terms of bias and variance, and propose two concrete remedies (e.g., limiting tree depth, collecting more data, switching to an ensemble). For each remedy, predict whether it primarily reduces bias or variance.

3. *Design a feature set.*

   You are building a classifier that, given a user message, predicts whether an agent should call a web-search tool, a calculator tool, or no tool at all. The message is plain text.

   - List at least five features you would extract from the message text (e.g., presence of a question mark, average word length). For each, explain why it might be predictive.
   - Identify one feature that could introduce **demographic bias** — systematically performing worse for some groups of users — and explain the mechanism.
   - Describe how you would use a held-out evaluation set to detect that bias before deployment.

---

## Reflection Prompt

*Personal*: Before this activity, did you think of "machine learning" and "AI" as the same thing? After seeing how much of RAG, embeddings, and agent routing reduces to supervised classification or regression, has your mental model changed? Describe one concrete thing that shifted.

*Technical*: Cross-validation gave us an honest estimate of model performance without wasting data on a fixed test set. Describe one situation where cross-validation would give an *overly optimistic* estimate — that is, where even CV accuracy would not reliably predict real-world performance.

> *Hint: Think about what assumption cross-validation makes about the relationship between your training data and the data you will see at deployment. What could violate that assumption?*

*Societal*: The bias-variance tradeoff is a mathematical concept, but "bias" in ML also refers to unfair treatment of groups. Are these two uses of the word connected, or is the shared vocabulary a coincidence? Give an example where high model bias (in the statistical sense) correlates with demographic bias (in the fairness sense).

---

→ **Coming Up Next:** Now that we understand how models learn from labeled data, we turn to what happens when labels are absent — in the next activity we explore **unsupervised learning**: clustering, dimensionality reduction, and how embedding spaces (which we built from scratch in an earlier unit) are trained without explicit labels.

## 5. Further Reading

- James, Witten, Hastie, and Tibshirani. *An Introduction to Statistical Learning* (2nd ed.), Chapters 2–8. The standard graduate reference for supervised ML; freely available online.
- Hastie, Tibshirani, and Friedman. *The Elements of Statistical Learning* (2nd ed.), Chapter 7 (Model Assessment and Selection). The theoretical grounding for bias-variance and cross-validation.
- Breiman, Leo. "Random Forests." *Machine Learning* 45 (2001): 5–32. The original paper; remarkably readable.
- Google Machine Learning Crash Course — [Overfitting](https://developers.google.com/machine-learning/crash-course/overfitting/overfitting). Short, visual introduction to the bias-variance tradeoff.
- Sculley et al. "Hidden Technical Debt in Machine Learning Systems." *NeurIPS* (2015). Why clean evaluation pipelines matter in production.

---

> **Acknowledgment:** Concepts in this activity were adapted from the following open-source educational resources (not reproduced verbatim):
> - [ML Course](https://github.com/ML-course/master), CC0 License
> - [AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch), MIT License — Phase 2 (ML Fundamentals)
>
> All text, questions, and exercises are original course materials.
