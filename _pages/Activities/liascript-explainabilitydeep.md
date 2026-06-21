# Explainability in Depth: SHAP, LIME, Attention, and the Limits of Interpretation

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-explainabilitydeep.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

**CS357: Foundations of Artificial Intelligence / Agentic AI**
Ursinus College

---

## POGIL Roles

In this activity, your team will work together using the following roles. Rotate roles with each new activity.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the team on task and on time; ensures everyone contributes; calls for consensus before moving on |
| **Recorder** | Writes down the team's agreed answers; manages the shared document or whiteboard |
| **Presenter** | Speaks for the team during class discussion; summarizes findings to the class |
| **Reflector** | Monitors team process; notes what is working and what is not; leads the Reflection section |

> Before starting, confirm your roles aloud. If your team has fewer than 4 members, one person may take two roles (e.g., Manager + Reflector).

---

## Model 1: Why Explainability and What It Is Not

Explainability (XAI — Explainable Artificial Intelligence) has become a central concern in AI deployment for three distinct reasons:

1. **Regulatory compliance**: The EU AI Act (Article 13) and the EU GDPR "right to explanation" (Article 22) require that automated systems affecting people be explainable to the people they affect. In the US, fair lending regulations require that credit denials be explained to applicants.
2. **Debugging failures**: When a model makes an error, developers need to understand *why* to fix it. Without explanation tools, a neural network is effectively a black box — you can observe inputs and outputs but not the reasoning in between.
3. **User trust**: Users are more likely to act on a model's recommendation — and more likely to notice when it is wrong — if they understand the basis for the recommendation.

A critical distinction: **"explanation" does not equal "understanding."** Post-hoc explanation methods describe a model's *behavior* — what inputs mattered for this prediction — but they do not reveal the model's *internal computation*, and they do not establish *causality*. An explanation can be accurate about behavior and still be misleading about cause.

| Explanation Type | What It Says | What It Does Not Say | Example Tool | Best For |
|-----------------|-------------|---------------------|-------------|----------|
| **Feature attribution** | Which input features contributed most (positively or negatively) to this prediction | Whether changing those features would change the prediction; why those features matter | SHAP, LIME, integrated gradients | Tabular data; structured inputs; debugging feature importance |
| **Counterfactual** | "If feature X had been Y instead, the prediction would have been Z" — minimal change to flip the outcome | Why the model learned to use feature X; whether the counterfactual is actionable or realistic | DiCE, Wachter et al. | Recourse (telling a user how to get a different outcome); fairness auditing |
| **Rule extraction** | A simple rule or decision tree that approximates the model's behavior globally or locally | Whether the rule is complete; the model may behave differently outside the rule's coverage | Anchors (Ribeiro), decision tree surrogates | Auditing; regulatory documentation; non-technical stakeholders |
| **Natural language** | A prose explanation of the reasoning in human-readable form, as produced by a chain-of-thought LLM | Whether the prose actually reflects the model's computation (faithfulness); may be plausible but post-hoc | GPT-4 CoT, Claude CoT | User-facing explanations; interactive Q&A about decisions |

### Critical Thinking Questions

**Question 1.** A SHAP explanation says "feature X (applicant's zip code) contributed +0.35 to this loan denial prediction." A loan officer interprets this as: "If I change the applicant's zip code, their loan application will be approved." Is this interpretation correct? What is the difference between a feature contributing to a prediction and that feature *causing* the prediction?

[[___ Your answer here ___]]

**Question 2.** Feature attribution methods produce **local** explanations (why did the model make this particular prediction for this particular instance?) and can also aggregate to **global** explanations (what does the model rely on overall?). Explain in your own words why a feature that ranks as highly important globally might be unimportant — or even irrelevant — for a specific individual prediction.

[[___ Your answer here ___]]

**Question 3.** A healthcare provider explains an AI diagnosis system to a patient by showing them a bar chart of which symptoms contributed to the diagnosis. The chart is technically accurate. Give one specific reason why this accurate explanation might still mislead the patient, and describe what additional context would be necessary for the explanation to be genuinely useful.

[[___ Your answer here ___]]

---

## Model 2: SHAP, LIME, and Attention Weights

Three explanation techniques dominate practical XAI for machine learning models. Each has a different theoretical basis, different computational cost, and different failure modes.

**SHAP (SHapley Additive exPlanations)** — Lundberg & Lee, 2017

SHAP assigns each feature a "Shapley value" — a concept from cooperative game theory that measures each player's fair contribution to the coalition's total payoff. Applied to ML: each feature is a "player," the prediction is the "payoff," and the Shapley value is the feature's average marginal contribution across all possible subsets of features.

SHAP satisfies four desirable properties:
- **Efficiency**: Feature attributions sum to the prediction (minus the baseline)
- **Symmetry**: Two features that always contribute equally get equal attributions
- **Dummy**: A feature that never changes the prediction gets attribution zero
- **Additivity**: Attributions for an ensemble equal the sum of attributions for each constituent model

Key limitation: exact Shapley values require evaluating the model on all 2^n feature subsets — exponential in the number of features. SHAP approximates this using sampling and model-specific shortcuts (e.g., TreeSHAP for tree models is exact and efficient; KernelSHAP for black-box models approximates).

**LIME (Local Interpretable Model-Agnostic Explanations)** — Ribeiro, Singh, Guestrin, 2016

LIME explains a single prediction by:
1. Generating a neighborhood of perturbed versions of the input (e.g., randomly masking words in text)
2. Querying the black-box model on each perturbed version
3. Fitting a simple interpretable model (e.g., linear regression) to this local neighborhood
4. Reporting the simple model's coefficients as the explanation

LIME is fast and model-agnostic (works with any model). Key limitations:
- **Instability**: different random samples of the neighborhood can produce different explanations for the same input — especially in high-dimensional spaces. Running LIME twice on the same instance may yield different feature rankings.
- **Locality only**: the explanation is valid only in the local neighborhood; it says nothing about the model's global behavior.

**Attention Weights**

Transformer-based models (including GPT and BERT) compute attention weights — scalars indicating how much each token "attends to" each other token when generating the next token. Displaying high-attention tokens as highlighted text has become a common form of explanation.

Critical finding: **Jain & Wallace (2019), "Attention is not Explanation"** showed that attention weights are often uncorrelated with feature importance as measured by other methods, and that alternative attention distributions (producing very different highlighted tokens) can produce the same prediction. High attention does not imply causal importance.

| Method | Faithfulness | Stability | Speed | Human Interpretability |
|--------|-------------|-----------|-------|----------------------|
| **SHAP** | High (for tree models); approximation for others | High (deterministic given sampling seed) | Slow for large models (KernelSHAP); fast for trees (TreeSHAP) | Medium — requires understanding of value ranges and baseline |
| **LIME** | Medium — local surrogate may not capture true boundary | Low — random sampling means different runs give different results | Fast | High — linear coefficients are intuitive |
| **Attention** | Low — not reliably correlated with causal importance | Medium — deterministic for same input, but sensitivity to tokenization | Very fast (computed during inference) | High — visual highlighting is immediately intuitive, but misleading |

### Critical Thinking Questions

**Question 4.** A SHAP explanation for a sentiment classifier shows that the word "not" received a Shapley value of +0.4 toward a *positive* sentiment prediction for the sentence "This film is not bad." What might this result indicate about what the model learned? Is this a sign the model is working correctly or incorrectly? How would you investigate further?

[[___ Your answer here ___]]

**Question 5.** LIME's instability means that running the same explanation twice may produce different results. In a high-stakes application — for example, a hiring algorithm explaining why a candidate was rejected — why is this instability a serious problem for the *legal* defensibility of the explanation, even if each individual LIME run is locally accurate?

[[___ Your answer here ___]]

**Question 6.** A transformer model is classifying a court document and must determine whether the phrase "not guilty" supports a positive or negative classification. The attention visualization shows high attention weights on the token "not." Based on the Jain & Wallace finding, is this evidence that the model is correctly identifying "not" as the critical negation token, or is it not? Explain what additional experiment you would run to determine whether the model is truly sensitive to the word "not."

[[___ Your answer here ___]]

---

A medical AI system explains its recommendation for a cancer screening referral by highlighting which regions of a patient's medical scan were most important, using LIME to generate the highlighted regions. A radiologist reviewing the recommendation should treat this explanation as:

- ( ) Definitive evidence identifying which anatomical features caused the AI's diagnosis
- ( ) A complete substitute for their own clinical analysis, since the AI has quantified the evidence
- (x) A plausible but potentially unstable local approximation that should complement — and may usefully direct — their clinical judgment, but cannot replace it
- ( ) Proof that the model is unbiased and has no spurious correlations in its training data

---

## Model 3: Explanations for LLMs and Agents

Traditional XAI methods (SHAP, LIME, attention) were developed for discriminative models (classifiers, regressors) with fixed-length inputs and numeric outputs. Large language models and agents raise new explanation challenges.

**Chain-of-thought (CoT) as a built-in explanation**

When an LLM is prompted to "think step by step," it produces a reasoning trace alongside its answer. This feels like a natural explanation of the model's reasoning. However, research has cast doubt on the **faithfulness** of CoT traces:

- Studies have shown that models sometimes produce a different answer when CoT is removed, suggesting the reasoning trace *does* influence the output — but only sometimes.
- More troubling, models can produce plausible-sounding but factually incorrect reasoning chains that nonetheless lead to the correct answer — or worse, lead to an incorrect answer while sounding confident and coherent.
- Turpin et al. (2023) showed that LLM reasoning can be influenced by **sycophantic biases** and **anchoring** to irrelevant information in the prompt, while the CoT does not acknowledge this influence.

This raises the possibility that CoT is sometimes **post-hoc rationalization**: the model had already "decided" (or had already computed an answer in its forward pass), and the CoT trace is constructed to justify that decision rather than to reveal the true computational path.

**Faithfulness vs. Plausibility**

- A **faithful** explanation accurately describes what the model actually computed.
- A **plausible** explanation sounds reasonable and coherent to a human reader.

These can come apart: an explanation can be highly plausible (it sounds like good reasoning) while being unfaithful (the model's actual prediction was driven by a different feature entirely).

**Practical XAI for agents**

When an *agent* — not just a classifier — is making decisions, explanation requirements change:

- **Logging tool choices with rationales**: the agent should record not just what tool it called but why it chose that tool over alternatives
- **Confidence calibration**: an agent should output calibrated uncertainty (e.g., "I estimate 70% confidence this is the correct document") rather than always sounding maximally certain
- **Uncertainty quantification**: agents should recognize and communicate when they are operating outside their reliable range, rather than confidently producing plausible-sounding hallucinations

### Critical Thinking Questions

**Question 7.** Design a checklist — intended for a non-technical user (e.g., a manager reviewing an AI recommendation) — for evaluating whether a chain-of-thought explanation from an LLM is trustworthy. Your checklist should have at least five items and each item should be actionable (the user can actually check it without needing to understand model internals). Focus on what observable properties of the explanation should raise or lower trust.

[[___ Your checklist here ___]]

**Question 8.** If chain-of-thought reasoning is sometimes a post-hoc rationalization — that is, the model's "decision" was effectively made before the reasoning trace was generated — what does this imply for using CoT as an **accountability mechanism**? Specifically: if a company relies on CoT traces as evidence that their AI system "showed its reasoning" to regulators, is that evidence meaningful? What would a more rigorous accountability mechanism look like?

[[___ Your answer here ___]]

**Question 9.** For a SHAP or LIME explanation, we can in principle test faithfulness by intervening on features (actually removing or changing them) and observing whether the model's prediction changes as the explanation predicts. What would "ground truth" look like for evaluating the faithfulness of a CoT explanation from an LLM? Describe a specific experiment or test that would provide evidence — even if imperfect evidence — that a CoT trace is faithful rather than post-hoc rationalization.

[[___ Your answer here ___]]

---

## Exercises

**Exercise 1.** Using an accessible sentiment analysis model (e.g., via the `transformers` library in Python or a public API), run the model on five sentences you construct — including at least one sentence with negation (e.g., "not bad"), one with sarcasm, and one that is straightforwardly positive. If SHAP is available for your chosen model, generate explanations for each. If not, use the model's output probabilities and your knowledge of the input to reason about feature importance. Report: (a) the sentence, (b) the prediction, (c) the explanation, (d) whether the explanation matches your intuition, and (e) one follow-up question the explanation raises.

[[___ Your answer here ___]]

**Exercise 2.** Find a published paper, blog post, or news article that cites attention maps or attention weights as evidence that a model is interpretable, has learned meaningful structure, or can be trusted. Evaluate the claim against the Jain & Wallace (2019) critique. Is the cited use of attention weights justified? What alternative evidence of meaningful learned structure would be more convincing? Write 150–200 words.

[[___ Your answer here ___]]

**Exercise 3.** Review three or more chain-of-thought outputs from a recent agent run in this course (or from a publicly available agent transcript). For each reasoning step in the CoT trace, ask: "Could the model have reached this conclusion without this step — for example, by pattern-matching on surface features of the input?" Flag any steps that appear to be rationalizations rather than necessary reasoning, and explain your reasoning. Report your findings for at least two complete CoT traces.

[[___ Your answer here ___]]

---

## Reflection Prompt

The EU AI Act and similar regulations are establishing a **"right to explanation"** for automated decisions that significantly affect people — credit denials, parole recommendations, hiring decisions, medical triage. This right is grounded in the belief that if people understand why a decision was made, they can contest unfair decisions and hold systems accountable.

But this activity has shown that explanations can be **unfaithful** (LIME instability, CoT rationalization), **misleading** (attention is not explanation), or **technically correct but practically incomprehensible** to non-experts.

If explanations can be systematically unfaithful, does the legal "right to explanation" genuinely protect the people it is meant to protect — or does it give them false assurance that a decision was made fairly and transparently? Write a personal reflection of 150–250 words. The Reflector should be prepared to share the team's position on this question with the class.

[[___ Your reflection here ___]]

---

## Further Reading

- Ribeiro, M. T., Singh, S., and Guestrin, C. (2016). "'Why Should I Trust You?': Explaining the Predictions of Any Classifier." *KDD 2016*. [LIME paper]
- Lundberg, S. M., and Lee, S.-I. (2017). "A Unified Approach to Interpreting Model Predictions." *NeurIPS 2017*. [SHAP paper]
- Jain, S., and Wallace, B. C. (2019). "Attention is not Explanation." *NAACL 2019*.
- Wachter, S., Mittelstadt, B., and Russell, C. (2017). "Counterfactual Explanations Without Opening the Black Box: Automated Decisions and the GDPR." *Harvard Journal of Law & Technology*, 31(2).
- Turpin, M., Michael, J., Perez, E., and Bowman, S. (2023). "Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting." *NeurIPS 2023*.
- European Parliament and Council (2024). "EU Artificial Intelligence Act." *Official Journal of the European Union*. (Articles 13 and 14 on transparency and human oversight.)
- Doshi-Velez, F., and Kim, B. (2017). "Towards A Rigorous Science of Interpretable Machine Learning." *arXiv:1702.08608*.
