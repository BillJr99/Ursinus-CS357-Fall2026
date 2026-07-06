---
layout: assignment
permalink: /Assignments/Explainability
title: "CS357: Foundations of Artificial Intelligence - Lab: AI Explainability with SHAP and LIME"

info:
  coursenum: CS357
  purpose: "To open the black box of a model's decisions with SHAP and LIME and judge honestly whether post-hoc explanations can justify a high-stakes outcome."
  tilt:
    task: "Generate SHAP and LIME explanations for a credit-scoring model, compare where they disagree, and write a jargon-free, regulation-grade denial statement."
    criteria: "Assessed on the SHAP visualizations, the LIME comparison, and the ethical and regulatory analysis of feature proxies; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To generate SHAP global explanations (beeswarm and bar plots) that rank feature importance across the full test set and identify counterintuitive directions of influence
    - To generate SHAP local explanations (waterfall and force plots) that trace how individual features pushed a single prediction away from the base rate
    - To generate a LIME local explanation for the same prediction and compare it to SHAP, identifying at least one feature where the two methods disagree on direction or magnitude and explaining why mechanistically
    - To classify each model feature as a legitimate predictor, a proxy variable for a protected characteristic, or both, using SHAP importance as supporting evidence
    - To write a jargon-free denial explanation statement of approximately 150 words grounded in SHAP waterfall output, meeting the meaningful information requirement of EU AI Act Article 13 for high-risk AI systems
    - To evaluate whether post-hoc explanations from SHAP and LIME are sufficient to justify high-stakes credit decisions, citing specific limitations of each method
  rubric:
    - weight: 30
      description: SHAP Implementation
      preemerging: SHAP not computed or code errors prevent any output
      beginning: SHAP values computed but only one visualization type produced (e.g., bar plot only), with no distinction made between global and local explanations
      progressing: Global beeswarm or bar plot generated and at least one local waterfall or force plot generated for the high-income denial case; visualizations saved to disk but not captioned or interpreted in the writeup
      proficient: All four visualizations saved (shap_beeswarm.png, shap_bar.png, shap_waterfall_NNN.png, shap_force_NNN.html); writeup captions each with the student's own interpretation distinguishing what the global plots show across the full test set from what the local plots show for a single prediction; at least one feature identified where the direction of influence (beeswarm color and position) is counterintuitive, with a mechanistic explanation grounded in the training data
    - weight: 30
      description: LIME Implementation
      preemerging: LIME not run or lime_explanation_NNN.html not produced
      beginning: LIME run for a prediction but not the same case used for SHAP local explanations, preventing side-by-side comparison
      progressing: LIME explanation generated for the same high-income denial case as the SHAP local explanation; comparison table in writeup lists direction labels for at least 3 features but does not identify any disagreement or explain it mechanistically
      proficient: LIME explanation generated for the same case as the SHAP waterfall; comparison table covers at least 5 features with direction labels for both methods; at least one feature where SHAP and LIME disagree on direction or magnitude is identified with a mechanistic explanation (e.g., LIME approximates locally while SHAP decomposes the true model output); student states which method they would use to explain the denial to the applicant and justifies the choice with specific reference to each method's properties
    - weight: 25
      description: Ethical and Regulatory Analysis
      preemerging: No ethical analysis attempted
      beginning: One or more features described as "biased" without distinguishing whether the feature is a legitimate predictor, a proxy variable, or both
      progressing: At least two of the three flagged features (zip_code_income_percentile, age, num_late_payments) analyzed with a statement about legitimate predictor status and proxy risk, but without citing SHAP importance values or addressing what additional investigation would be needed to confirm disparate impact
      proficient: All three flagged features analyzed with (a) a classification as legitimate predictor, proxy variable, or both, (b) the feature's mean absolute SHAP value cited as evidence of its influence, and (c) a statement of what additional analysis (e.g., disparate impact testing across demographic groups) would be required; student writes an approximately 150-word denial explanation statement grounded in the SHAP waterfall for the high-income denial case that contains no technical jargon (no mention of SHAP, model, algorithm, or numerical SHAP values), names the top three denial factors in plain language, and includes one actionable suggestion for the applicant — meeting the meaningful information standard of EU AI Act Article 13 for high-risk AI systems
    - weight: 15
      description: Writeup and Reflection
      preemerging: No writeup
      beginning: Writeup describes what outputs were produced without interpreting what they mean about the model's behavior
      progressing: Writeup interprets at least two visualization types and notes one limitation of either SHAP or LIME
      proficient: Writeup interprets all four SHAP visualization types (global beeswarm, global bar, local waterfall, local force plot) with explicit distinctions between global and local scope; compares SHAP and LIME on at least two dimensions (e.g., model-specificity, feature representation as conditions vs. contributions, stability across runs); and addresses what additional documentation beyond a SHAP waterfall plot would be required for a court-facing credit denial explanation
  readings:
    - rtitle: "Explainability Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-explainability.md"
    - rtitle: "Explainability in Depth Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-explainabilitydeep.md"
    - rtitle: "Bias in Data Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-biasdata.md"
    - rtitle: "Data Cards Assignment"
      rlink: "https://www.billmongan.com/Ursinus-CS357/Assignments/DataCards"

tags:
  - explainability
  - shap
  - lime
  - bias
  - ethics
---

Black-box AI makes decisions. Explainability tools open the box — partially. This lab applies two widely deployed techniques (SHAP and LIME) to a synthetic credit scoring model, then asks you to evaluate whether the explanations they produce are sufficient for real-world use. The answer, you will discover, is nuanced.

This lab is completed in **pairs using driver/navigator roles**: the driver types while the navigator reviews, questions, and consults documentation, and you must **swap roles at least every 30 minutes**, keeping a brief log of swap times and who held each role.

---

## Before You Start

**Why credit scoring?** Credit scoring is a regulated domain governed by the Equal Credit Opportunity Act (ECOA) in the United States and classified as a high-risk AI system under the EU AI Act. It requires that denied applicants receive an explanation. It also has features that are simultaneously legitimate predictors of repayment and historically correlated proxies for protected characteristics like race and ethnicity. This combination — regulated, high-stakes, and riddled with proxy variables — makes credit scoring an ideal domain for studying what explainability tools can and cannot do.

**Prerequisite concepts** — make sure you have completed these activities before writing any code:

- [Explainability Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-explainability.md) — what explainability means and when it matters
- [Explainability in Depth Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-explainabilitydeep.md) — SHAP and LIME mechanics
- [Bias in Data Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-biasdata.md) — proxy variables and disparate impact

**Tools to install:**

```bash
pip install shap lime scikit-learn matplotlib pandas numpy
```

No Ollama or network access is required for this lab. Everything runs locally on a synthetic dataset you generate in Part 1.

If you would like an alternate starter path for the dataset and model, the [Credit Score Feature Weight Estimator notebook](/files/notebooks/CreditScoreFeatureWeightEstimator.ipynb) trains a small, fully transparent linear credit-scoring model whose feature weights you can read directly — a useful warm-up baseline before applying SHAP and LIME to this lab's model.

**Health check** — run this before writing any lab code:

```python
import shap, lime, sklearn
print(f"shap={shap.__version__}  lime={lime.__version__}  sklearn={sklearn.__version__}")
```

Expected output (versions may vary):

```
shap=0.44.1  lime=0.2.0.1  sklearn=1.4.2
```

If `import shap` raises a `ImportError` related to compilation, try:

```bash
pip install shap --no-binary shap
```

**Estimated time budget:**

| Part | Task | Estimated time |
|------|------|----------------|
| Part 1 | Train the Model | 20–30 min |
| Part 2 | SHAP Global and Local Explanations | 50–70 min |
| Part 3 | LIME Local Explanation | 30–40 min |
| Part 4 | Side-by-Side Comparison | 20–30 min |
| Part 5 | Ethical and Regulatory Analysis | 30–40 min |
| Writeup | Readme and reflection | 30–45 min |

---

## Part 1: Train a Credit Scoring Model

You will generate a synthetic dataset of 2,000 loan applicants and train a Random Forest classifier to predict approval. The dataset is designed to mimic real-world structure: most features are legitimate predictors of creditworthiness, but one (`zip_code_income_percentile`) is a deliberate proxy variable — a stand-in for neighborhood wealth that correlates with race and ethnicity in historical US data.

### Step 1: Generate the dataset and train the model.

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import shap
import lime
import lime.lime_tabular
import matplotlib
matplotlib.use("Agg")  # use non-interactive backend for saving files
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

np.random.seed(42)
N = 2000

data = {
    "age":                       np.random.randint(18, 75, N),
    "income_annual":             np.random.lognormal(10.8, 0.5, N).clip(15_000, 250_000),
    "credit_history_years":      np.clip(np.random.gamma(3, 4, N), 0, 35).astype(int),
    "debt_to_income_ratio":      np.random.beta(2, 5, N),
    "num_late_payments":         np.random.poisson(1.2, N),
    "loan_amount_requested":     np.random.lognormal(10.1, 0.6, N).clip(1_000, 150_000),
    "employment_years":          np.clip(np.random.gamma(4, 3, N), 0, 45).astype(int),
    "has_savings_account":       np.random.choice([0, 1], N, p=[0.35, 0.65]),
    "num_credit_accounts":       np.random.poisson(3.5, N).clip(0, 15),
    "zip_code_income_percentile": np.random.uniform(0, 100, N),  # proxy variable!
}
df = pd.DataFrame(data)

# Approval score function.
# zip_code_income_percentile is included deliberately as a confound
# (it influences the label even though it is a protected proxy in practice).
score = (
    np.log1p(df["income_annual"]) * 0.40
    + df["credit_history_years"] * 0.20
    - df["debt_to_income_ratio"] * 4.00
    - df["num_late_payments"] * 0.60
    + df["employment_years"] * 0.08
    + df["has_savings_account"] * 1.20
    + df["num_credit_accounts"] * 0.15
    + df["zip_code_income_percentile"] * 0.03   # <-- proxy contribution
    + np.where((df["age"] >= 25) & (df["age"] <= 55), 1.5, -0.3)
    + np.random.normal(0, 0.8, N)
)
df["approved"] = (score > score.median()).astype(int)

FEATURES = [c for c in df.columns if c != "approved"]
X = df[FEATURES]
y = df["approved"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=200, max_depth=8, random_state=42, n_jobs=-1
)
model.fit(X_train, y_train)

print(f"Test accuracy:          {model.score(X_test, y_test):.3f}")
print(f"Approval rate (all):    {y.mean():.1%}")
print(f"Approval rate (test):   {y_test.mean():.1%}")
print(f"Training set size:      {len(X_train)}")
print(f"Test set size:          {len(X_test)}")
```

**Expected output:**

```
Test accuracy:          0.791
Approval rate (all):    50.0%
Approval rate (test):   50.2%
Training set size:      1500
Test set size:          500
```

Your accuracy may vary slightly depending on library versions, but should be in the 0.76–0.82 range. If it falls below 0.70, check that `np.random.seed(42)` appears before the dataset generation block.

### Troubleshooting — Part 1

**`ValueError: Input contains NaN`**
The `clip` calls in the dataset generation should prevent NaN values. If you see this error, add `print(df.isna().sum())` to identify which feature contains NaN, then trace back to the generation step for that feature.

**Training is very slow**
Set `n_jobs=-1` to use all available cores (already included above). If the machine still takes more than 2 minutes, reduce `n_estimators` to 100.

**Approval rate is not near 50%**
This happens if `np.random.seed(42)` was not called before the data generation. Check that the seed line comes before the `data = {...}` block, not after.

---

> **Checkpoint: Before moving to Part 2, make sure you can answer:**
> 1. What is a Random Forest, and why is it called a "black box" model even though it is made up of interpretable decision trees?
> 2. The dataset has a 50% approval rate by construction. Is a model with 79% accuracy on a balanced dataset performing well? What is the baseline accuracy of always predicting the majority class?
> 3. Which feature in this dataset is the deliberate proxy variable, and what real-world characteristic does it stand in for?

---

## Part 2: SHAP Global and Local Explanations

SHAP (SHapley Additive exPlanations) uses game-theoretic Shapley values to assign each feature a contribution to each individual prediction. The global summary aggregates these contributions across many predictions to show overall model behavior. The local force plot shows the reasoning behind a single prediction.

### Step 1: Compute SHAP values.

```python
def compute_shap_values(model, X_train, X_test):
    """
    Compute SHAP values for the test set using TreeExplainer.

    TreeExplainer is optimized for tree-based models like Random Forest
    and runs in polynomial time rather than exponential time.

    Returns:
        explainer: fitted shap.TreeExplainer
        shap_values: array of shape (n_test, n_features, n_classes) for multi-class,
                     or (n_test, n_features) for binary (we use the approval class)
    """
    print("Computing SHAP values (this may take 30-60 seconds)...")
    explainer = shap.TreeExplainer(model, X_train)
    shap_values = explainer(X_test)
    print(f"SHAP values shape: {shap_values.values.shape}")
    return explainer, shap_values
```

### Step 2: Generate global visualizations.

```python
def plot_shap_global(shap_values, X_test, output_dir="."):
    """
    Generate and save two global SHAP visualizations:
    1. Beeswarm plot: each dot is one prediction; position shows SHAP value,
       color shows feature value (red = high, blue = low).
    2. Bar plot: mean absolute SHAP value per feature, a ranked importance list.
    """
    # For binary classification, shap_values has shape (n, features, 2).
    # We take index [..., 1] to get SHAP values for the "approved" class.
    sv = shap_values[..., 1] if shap_values.values.ndim == 3 else shap_values

    # Beeswarm plot (global summary)
    plt.figure(figsize=(10, 7))
    shap.plots.beeswarm(sv, max_display=10, show=False)
    plt.title("SHAP Beeswarm: Feature Impact on Approval Probability", fontsize=13)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/shap_beeswarm.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_dir}/shap_beeswarm.png")

    # Bar plot (mean |SHAP| importance)
    plt.figure(figsize=(9, 6))
    shap.plots.bar(sv, max_display=10, show=False)
    plt.title("SHAP Mean Absolute Value: Overall Feature Importance", fontsize=13)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/shap_bar.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_dir}/shap_bar.png")
```

### Step 3: Find an interesting local case to explain.

You want to find a test-set applicant who was **denied despite high income** — this is the kind of case that raises questions for an applicant and is most informative for your comparison analysis in Part 4.

```python
def find_interesting_cases(X_test, y_test, model):
    """
    Identify test cases that are counterintuitive:
    - high_income_denial: applicant in top income quartile who was denied
    - low_income_approval: applicant in bottom income quartile who was approved

    Returns:
        dict mapping case label to integer index in X_test.
    """
    predictions = model.predict(X_test)
    income_q75 = X_test["income_annual"].quantile(0.75)
    income_q25 = X_test["income_annual"].quantile(0.25)

    # High income but denied
    denial_mask = (
        (predictions == 0)
        & (X_test["income_annual"] > income_q75)
    )
    high_income_denial_idx = X_test[denial_mask].index[0]

    # Low income but approved
    approval_mask = (
        (predictions == 1)
        & (X_test["income_annual"] < income_q25)
    )
    low_income_approval_idx = X_test[approval_mask].index[0]

    cases = {
        "high_income_denial": high_income_denial_idx,
        "low_income_approval": low_income_approval_idx,
    }

    for label, idx in cases.items():
        row = X_test.loc[idx]
        pred = predictions[X_test.index.get_loc(idx)]
        print(f"\n{label} (index {idx}):")
        print(f"  Prediction: {'Approved' if pred == 1 else 'Denied'}")
        print(f"  Income: ${row['income_annual']:,.0f}")
        print(f"  Credit history: {row['credit_history_years']} years")
        print(f"  Debt-to-income: {row['debt_to_income_ratio']:.2f}")
        print(f"  Late payments:  {row['num_late_payments']}")

    return cases
```

### Step 4: Generate local explanations for the denial case.

```python
def plot_shap_local(shap_values, X_test, case_idx, output_dir="."):
    """
    Generate and save two local SHAP visualizations for a single prediction:
    1. Waterfall plot: shows how each feature pushed the prediction away
       from the expected value (base rate) toward the final score.
    2. Force plot: a horizontal version of the waterfall, easier to share
       with non-technical audiences.

    Args:
        case_idx: integer index into X_test (from find_interesting_cases).
    """
    sv = shap_values[..., 1] if shap_values.values.ndim == 3 else shap_values
    pos = X_test.index.get_loc(case_idx)

    # Waterfall plot
    plt.figure(figsize=(10, 6))
    shap.plots.waterfall(sv[pos], max_display=10, show=False)
    plt.title(f"SHAP Waterfall: Denial Explanation (index {case_idx})", fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/shap_waterfall_{case_idx}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_dir}/shap_waterfall_{case_idx}.png")

    # Force plot (saved as HTML — open in a browser)
    # TODO: Generate a force plot for the same case using shap.plots.force()
    # and save it to shap_force_{case_idx}.html
    # Hint: shap.save_html(filename, shap.plots.force(sv[pos]))
    force_html = shap.plots.force(sv[pos])
    shap.save_html(f"{output_dir}/shap_force_{case_idx}.html", force_html)
    print(f"Saved: {output_dir}/shap_force_{case_idx}.html  (open in browser)")
```

### Step 5: Wire Part 2 together and run.

```python
if __name__ == "__main__":
    explainer, shap_values = compute_shap_values(model, X_train, X_test)
    plot_shap_global(shap_values, X_test)
    cases = find_interesting_cases(X_test, y_test, model)
    denial_idx = cases["high_income_denial"]
    plot_shap_local(shap_values, X_test, denial_idx)
```

**Expected console output (index numbers will differ):**

```
Computing SHAP values (this may take 30-60 seconds)...
SHAP values shape: (500, 10, 2)

high_income_denial (index 214):
  Prediction: Denied
  Income: $138,420
  Credit history: 1 years
  Debt-to-income: 0.58
  Late payments:  4

low_income_approval (index 87):
  Prediction: Approved
  Income: $22,104
  Credit history: 14 years
  Debt-to-income: 0.11
  Late payments:  0

Saved: shap_beeswarm.png
Saved: shap_bar.png
Saved: shap_waterfall_214.png
Saved: shap_force_214.html
```

In the **beeswarm plot**, look for which features show the widest horizontal spread — those are the most influential. Red dots that extend far right push toward approval; red dots that extend far left push toward denial. In the **waterfall plot** for the denial case, features with red bars pushed toward denial; features with blue bars pushed toward approval. Read the waterfall from bottom to top: the base rate (expected approval probability) is at the bottom, and each feature adds or subtracts until you arrive at the final predicted probability at the top.

### Troubleshooting — Part 2

**SHAP force plots are blank when viewed in Jupyter**
Add `shap.initjs()` at the top of your notebook cell. For script-based workflows, the HTML file approach in Step 4 is more reliable.

**`IndexError` in `plot_shap_local` when accessing `sv[pos]`**
The `pos` variable from `X_test.index.get_loc(case_idx)` gives a positional index. If `X_test` was reset-indexed, `case_idx` and `pos` will be the same. If the original DataFrame index was retained, they may differ. Add `print(f"case_idx={case_idx}, pos={pos}")` to diagnose.

**SHAP values are all near zero**
This usually means `explainer(X_test)` was called with `check_additivity=True` (the default) and the model is not tree-based. Confirm `model` is a `RandomForestClassifier`, not a pipeline wrapper.

---

> **Checkpoint: Before moving to Part 3, make sure you can answer:**
> 1. Look at the beeswarm plot. Which feature has the largest average impact on approval probability? Is that the same feature you would have predicted before running SHAP?
> 2. In the waterfall plot for the high-income denial case, which feature contributed most to the denial? Does this make intuitive sense given the applicant's data (late payments, debt ratio)?
> 3. What does the base rate (the bottom value in the waterfall) represent? How would you describe it to someone who has never seen a SHAP plot?

---

## Part 3: LIME Local Explanation

LIME (Local Interpretable Model-agnostic Explanations) works differently from SHAP. Rather than decomposing the model's exact output, LIME perturbs the input around a specific example, runs many perturbed versions through the model, and fits a simple linear model to the results. The linear model's coefficients are the "explanation." This makes LIME model-agnostic but also approximate — it is explaining a local linear approximation, not the model's true behavior.

### Step 1: Set up the LIME explainer.

```python
def build_lime_explainer(X_train, feature_names, class_names=("Denied", "Approved")):
    """
    Build a LIME tabular explainer fit to the training distribution.

    Args:
        X_train: training feature DataFrame (used to estimate feature distributions).
        feature_names: list of column names.
        class_names: tuple of class label strings for display.

    Returns:
        lime.lime_tabular.LimeTabularExplainer
    """
    return lime.lime_tabular.LimeTabularExplainer(
        training_data=X_train.values,
        feature_names=feature_names,
        class_names=class_names,
        mode="classification",
        random_state=42,
    )
```

### Step 2: Generate a LIME explanation for the same denial case.

```python
def explain_with_lime(lime_explainer, model, X_test, case_idx,
                      num_samples=2000, output_dir="."):
    """
    Produce a LIME explanation for a single prediction and save the output.

    Uses the same case_idx as the SHAP local explanation in Part 2 so that
    the two methods can be compared side by side.

    Returns:
        lime.explanation.Explanation
    """
    pos = X_test.index.get_loc(case_idx)
    instance = X_test.values[pos]

    print(f"Generating LIME explanation for index {case_idx} "
          f"(num_samples={num_samples})...")

    explanation = lime_explainer.explain_instance(
        data_row=instance,
        predict_fn=model.predict_proba,
        num_features=10,
        num_samples=num_samples,
        labels=(1,),  # explain probability of "Approved" class
    )

    # Save as HTML for visual inspection
    html_path = f"{output_dir}/lime_explanation_{case_idx}.html"
    explanation.save_to_file(html_path)
    print(f"Saved: {html_path}  (open in browser)")

    # Print the feature weights to console
    print(f"\nLIME feature weights for index {case_idx} (class: Approved):")
    print(f"{'Feature':<30} {'Weight':>10}")
    print("-" * 42)
    for feature, weight in explanation.as_list(label=1):
        direction = "  -> approval" if weight > 0 else "  -> denial"
        print(f"{feature:<30} {weight:>+10.4f}{direction}")

    return explanation
```

### Step 3: Add Part 3 to your main block.

```python
    lime_explainer = build_lime_explainer(X_train, FEATURES)
    lime_exp = explain_with_lime(lime_explainer, model, X_test, denial_idx)
```

**Expected console output (index 214 example — your weights will differ):**

```
Generating LIME explanation for index 214 (num_samples=2000)...
Saved: lime_explanation_214.html  (open in browser)

LIME feature weights for index 214 (class: Approved):
Feature                        Weight
------------------------------------------
num_late_payments > 2.00       -0.2341  -> denial
debt_to_income_ratio > 0.45    -0.1887  -> denial
credit_history_years <= 2.00   -0.1653  -> denial
income_annual > 105000.00      +0.1122  -> approval
employment_years <= 3.00       -0.0894  -> denial
has_savings_account = 0        -0.0712  -> denial
```

Note that LIME reports features as **conditions** (ranges) rather than raw values, because it fits a linear model on perturbed binarized inputs. SHAP reports exact contributions. This is one of the key structural differences you will analyze in Part 4.

### Troubleshooting — Part 3

**LIME is very slow (more than 5 minutes)**
Reduce `num_samples` from 2000 to 500. Accuracy of the local approximation will decrease slightly, but the explanation will still be useful for comparison purposes. Record the `num_samples` value you used in your writeup.

**LIME weights are all very small (less than 0.01)**
This usually means the model's predicted probability for this instance is very close to the base rate, so perturbations do not change the output much. Try `find_interesting_cases` with a stricter filter (top decile for income, not just top quartile) to find a case with a more decisive prediction.

**`ValueError: All LIME feature weights are NaN`**
This can happen if `X_train.values` contains integer columns that LIME interprets as categorical. Add `.astype(float)` when passing to `LimeTabularExplainer`.

---

> **Checkpoint: Before moving to Part 4, make sure you can answer:**
> 1. LIME reports features as conditions like `num_late_payments > 2.00` rather than the raw feature name. Why does LIME discretize features this way?
> 2. If you ran LIME on the same instance twice with the same `random_state`, would you get identical results? What if you changed `num_samples`? Why?
> 3. Compare the top denial factor from LIME with the top denial factor from the SHAP waterfall. Are they the same feature?

---

## Part 4: Side-by-Side Comparison

For the same high-income denial case, compile a comparison table of the two explanation methods. You will complete this table manually using the output you have already generated.

### Step 1: Build the comparison table.

In your writeup, create a table with the following structure (fill in the Direction and Agreement columns from your output):

| Feature | SHAP contribution direction | LIME contribution direction | Agreement? |
|---------|-----------------------------|-----------------------------|------------|
| `num_late_payments` | | | |
| `debt_to_income_ratio` | | | |
| `credit_history_years` | | | |
| `income_annual` | | | |
| `zip_code_income_percentile` | | | |
| `employment_years` | | | |

For each row, record whether SHAP and LIME agree on the **direction** of the feature's influence (pushes toward approval or toward denial). Use your SHAP waterfall values and your LIME weight table.

### Step 2: Identify and explain one disagreement.

Find at least one feature where SHAP and LIME **disagree on direction or magnitude** and write a mechanistic explanation. Useful starting points:

- Did one method flag `zip_code_income_percentile` as influential while the other ranked it low?
- Did one method show `income_annual` pushing toward denial (because the model penalizes high-income applicants with poor credit more sharply) while the other showed it pushing toward approval?

A mechanistic explanation is one that traces the disagreement to a property of how each method works — not just "they gave different numbers."

### Step 3: Choose which explanation you would present to the applicant.

You are a loan officer. The applicant was denied and is asking why. Write one paragraph (5–8 sentences) answering:

- Which method's output — SHAP or LIME — would you use as the basis for your explanation to the applicant, and why?
- What would you leave out, and why?
- What would you add that neither method provides?

There is no single correct answer. The goal is to justify your choice with specific reference to the properties of each method.

---

> **Checkpoint: Before moving to Part 5, make sure you can answer:**
> 1. What is one structural reason why SHAP and LIME might disagree on the importance of a feature, even if both methods are implemented correctly?
> 2. If you had to explain this denial in court, which method's output would be easier to defend? Why?
> 3. Did either method produce an explanation that would be immediately understandable to a loan applicant with no statistics background? What would you need to change?

---

## Part 5: Ethical and Regulatory Analysis

This part asks you to apply what you have learned about explainability to the harder question: do these explanations justify the decisions?

### Step 1: Analyze three features for regulatory concern.

For each of the three features below, write a 3–5 sentence analysis covering: (a) whether it is a legitimate predictor of credit risk, (b) whether it could function as a proxy for a protected characteristic, and (c) what additional investigation you would need to confirm or rule out disparate impact.

**Feature 1: `zip_code_income_percentile`**

This variable was deliberately included in the scoring function with a small positive weight. In the United States, zip code income is correlated with race and ethnicity due to the historical effects of redlining. Using it — even with a small coefficient — can produce disparate impact on minority applicants even when race is not included in the model.

Look at your SHAP beeswarm plot and your bar plot. How important is this feature globally? Does its importance surprise you given how small its coefficient (0.03) is in the score function?

**Feature 2: `age`**

The score function includes a penalty for applicants outside the 25–55 age range. Age is a protected characteristic under ECOA for applicants over 40. Consider: does SHAP show age as a high-importance feature? In which direction does it push predictions for older applicants?

**Feature 3: `num_late_payments`**

This is a legitimate predictor — late payments are a direct signal of credit behavior. But late payments are also correlated with income shocks, which are more common in lower-income and minority communities. Is there a difference between a feature being a legitimate predictor and it being a fair one?

### Step 2: Identify one counterintuitive direction of influence.

Look at your global beeswarm plot. Find one feature where the direction of influence (red = high feature value pushing right = toward approval) is the **opposite** of what you would naively expect, and write a 3–5 sentence explanation of why the model might have learned that relationship from this data.

For example: you might expect `loan_amount_requested` to always push toward denial (larger loans are riskier), but the model might approve larger loan requests from applicants with strong credit histories because those applicants self-select. This is a spurious correlation in the training data, not a causal relationship.

### Step 3: Write a denial explanation statement.

Write a **150-word denial explanation statement** as if you were a loan officer writing to a denied applicant. Requirements:

- Must be based on the SHAP waterfall output for your `high_income_denial` case
- Must identify the top three factors that contributed to the denial
- Must avoid technical jargon (do not mention SHAP, model, or algorithm)
- Must not include any numerical SHAP values (translate them into plain language)
- Must include a statement about how the applicant could strengthen a future application

This exercise mimics the explanation requirement in EU AI Act Article 13 for high-risk AI systems, which requires that affected individuals receive "meaningful information about the logic involved" and "the significance and the envisaged consequences of such processing."

```
[Write your statement here in the readme — approximately 150 words]
```

### Step 4: Add the regulatory analysis to your main output.

```python
def print_regulatory_summary(shap_values, X_test, feature_names):
    """
    Print a summary of SHAP importance for the three features under regulatory scrutiny.
    """
    sv = shap_values[..., 1] if shap_values.values.ndim == 3 else shap_values
    mean_abs_shap = np.abs(sv.values).mean(axis=0)
    importance = sorted(
        zip(feature_names, mean_abs_shap), key=lambda x: x[1], reverse=True
    )

    print("\nGlobal SHAP importance (mean |SHAP|):")
    print(f"{'Rank':<6} {'Feature':<30} {'Mean |SHAP|':>12}")
    print("-" * 50)
    for rank, (name, val) in enumerate(importance, 1):
        flag = " <-- regulatory concern" if name in (
            "zip_code_income_percentile", "age"
        ) else ""
        print(f"{rank:<6} {name:<30} {val:>12.4f}{flag}")
```

Add a call to this function in your main block:

```python
    print_regulatory_summary(shap_values, X_test, FEATURES)
```

**Expected output:**

```
Global SHAP importance (mean |SHAP|):
Rank   Feature                        Mean |SHAP|
--------------------------------------------------
1      income_annual                      0.0832
2      credit_history_years               0.0714
3      debt_to_income_ratio               0.0641
4      num_late_payments                  0.0588
5      age                                0.0423 <-- regulatory concern
6      employment_years                   0.0391
7      zip_code_income_percentile         0.0312 <-- regulatory concern
8      loan_amount_requested              0.0287
9      has_savings_account                0.0241
10     num_credit_accounts                0.0198
```

Notice that `zip_code_income_percentile` appears in the middle of the ranking — it is not the top feature, but it is not negligible either. A model auditor would flag this: the feature has measurable influence, and its influence cannot be separated from its role as a proxy variable without additional analysis.

### Troubleshooting — Part 5

**SHAP importance ranking differs significantly from what you expected**
This is expected. SHAP importance is not the same as the coefficient in the score function that generated the labels. Random Forests can learn non-linear interactions that amplify or suppress the influence of a feature relative to its linear weight.

**`zip_code_income_percentile` appears at rank 1 or 2**
If the proxy variable ranks very high, it may be because your random seed produced a dataset where it correlates strongly with the outcome. In a real audit, this would be a serious finding. Note it in your writeup.

**The denial explanation statement is hard to write without jargon**
Start from the bottom of the waterfall: which features had the largest negative (red) bars? Name those features in plain language. For `num_late_payments`, you might write "your recent payment history shows multiple missed or late payments." Work each feature this way before worrying about length.

---

> **Checkpoint: You have succeeded at this lab when:**
> - Four SHAP visualizations are saved to disk (beeswarm, bar, waterfall, force plot)
> - One LIME HTML explanation is saved to disk
> - Your comparison table covers at least 5 features with direction labels and one disagreement identified with a mechanistic explanation
> - Your regulatory analysis covers all three flagged features
> - Your denial explanation statement is approximately 150 words, jargon-free, and based on the SHAP waterfall output

---

## Reflection Prompts

Answer in your readme:

1. SHAP tells you which features influenced the model's decision. Does it tell you whether those features *should* have influenced the decision? What additional step — outside of SHAP — would you need to answer that question?
2. You wrote a denial explanation using SHAP output. Would a non-technical loan applicant understand it as written? What would need to change to make it genuinely useful to someone with no statistics background?
3. The `zip_code_income_percentile` feature was included deliberately as a proxy variable. Did SHAP flag it as globally important? What does this tell you about what SHAP detects and what it does not detect about fairness?
4. LIME and SHAP sometimes disagreed on which features were most influential for the same prediction. Given that disagreement, which method would you trust more, and under what circumstances would you switch your answer?
5. A court requires that a credit denial be explained. Is a SHAP waterfall plot — as-is — sufficient evidence, or would you need additional documentation? What would you add?
6. If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
7. Approximately how many hours did this lab take?

---

## Submission Checklist

Submit a ZIP file containing all of the following. Items marked with a checkbox must be present for the submission to be graded.

- [ ] `credit_explainability.py` — complete model training, SHAP, LIME, and regulatory analysis code
- [ ] `shap_beeswarm.png` — global beeswarm plot
- [ ] `shap_bar.png` — global bar importance plot
- [ ] `shap_waterfall_NNN.png` — local waterfall plot for the high-income denial case (replace NNN with your case index)
- [ ] `shap_force_NNN.html` — local force plot for the same case (open in browser to verify it renders)
- [ ] `lime_explanation_NNN.html` — LIME explanation for the same case
- [ ] `readme.md` — writeup covering: (1) interpretation of all four SHAP visualizations with at least one counterintuitive finding, (2) LIME vs. SHAP comparison table with at least one disagreement explained mechanistically, (3) regulatory analysis of the three flagged features, (4) the 150-word denial explanation statement, (5) answers to all reflection prompts
- [ ] `pair_log.txt` — driver/navigator swap log with timestamps and roles
