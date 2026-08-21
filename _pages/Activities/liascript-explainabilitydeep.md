<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-explainabilitydeep.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Explainability in Depth: SHAP, LIME, Attention, and the Limits of Interpretation

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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **SHAP (SHapley Additive exPlanations)** | A method from game theory that assigns each input feature a numerical score representing how much it contributed to a specific model prediction, fairly divided across all features | For a loan denial, SHAP might report: income contributed −0.4 (pushed toward denial), employment type contributed +0.2 (pushed toward approval) |
| **LIME (Local Interpretable Model-Agnostic Explanations)** | A method that explains one prediction by creating slightly modified versions of the input, seeing how the model's output changes, and fitting a simple linear model to those changes | For a spam classifier, LIME might find that removing the word "prize" causes the spam score to drop by 0.6 |
| **Attention weights** | Numbers inside a transformer model that indicate how much each word "paid attention to" each other word when generating output, sometimes displayed as heat maps over text | Highlighted tokens in a transformer output, where bright highlighting means high attention weight |
| **Faithfulness** | Whether an explanation actually describes what the model computed internally, not just what sounds plausible to a human reader | A faithful explanation of a spam decision correctly identifies that "free money" drove the decision; an unfaithful one invents a sensible-sounding but incorrect reason |
| **Chain-of-thought (CoT)** | A prompting technique where a model is asked to write out its reasoning step by step before giving a final answer, making its "thinking" visible, though that thinking may not perfectly reflect the model's internal computation | "Step 1: The applicant's income is below the threshold... Step 2: Therefore, I recommend denial." |
| **Post-hoc rationalization** | When a model (or person) produces a plausible-sounding explanation for a decision that was actually driven by different factors; the explanation is constructed after the fact rather than being the actual reasoning | A model correctly classifies a sentence as negative but "explains" it by highlighting words that are not actually responsible for the prediction |

---

## Model 1: Why Explainability and What It Is Not

Think of SHAP values like a restaurant receipt that shows exactly which ingredients cost what, not just the total bill. Without the receipt, you can see that dinner cost $47 but you cannot dispute the charge for the lobster bisque you never ordered. Explainability tools give us that receipt for AI decisions: they do not change what the model computed, but they let us see which inputs drove the outcome. The challenge (and this is the central tension of this entire activity) is that the receipt can be wrong without looking wrong.

Explainability (XAI, Explainable Artificial Intelligence) has become a central concern in AI deployment for three distinct reasons:

1. **Regulatory compliance**: The EU AI Act (Article 13) and the EU GDPR "right to explanation" (Article 22) require that automated systems affecting people be explainable to those they affect. In the US, fair lending regulations require that credit denials be explained to applicants in plain language.
2. **Debugging failures**: When a model makes an error, developers need to understand *why* to fix it. Without explanation tools, a neural network is effectively a black box: you can observe inputs and outputs but not the reasoning in between.
3. **User trust**: Users are more likely to act on a model's recommendation (and more likely to notice when it is wrong) if they understand the basis for the recommendation.

A critical distinction: **"explanation" does not equal "understanding."** Post-hoc explanation methods describe a model's *behavior* (what inputs mattered for this prediction), but they do not reveal the model's *internal computation*, and they do not establish *causality*. An explanation can be accurate about behavior and still be misleading about cause.

| Explanation Type | What It Says | What It Does Not Say | Example Tool | Best For |
|-----------------|-------------|---------------------|-------------|----------|
| **Feature attribution** | Which input features contributed most (positively or negatively) to this prediction, expressed as numerical scores | Whether changing those features would actually change the prediction; why the model learned to use those features in the first place | SHAP, LIME, integrated gradients | Tabular data; structured inputs; debugging which features the model relies on |
| **Counterfactual** | "If feature X had been Y instead, the prediction would have changed to Z", the minimum change needed to flip the outcome | Why the model learned to use feature X at all; whether the suggested counterfactual change is realistic or actionable for the affected person | DiCE, Wachter et al. | Recourse (telling a user concretely how to get a different outcome); fairness auditing |
| **Rule extraction** | A simple rule or decision tree that approximates the model's behavior globally or for a specific input region | Whether the rule covers all cases; the model may behave very differently outside the rule's coverage area | Anchors (Ribeiro), decision tree surrogates | Regulatory documentation; auditing; communicating with non-technical stakeholders |
| **Natural language** | A prose explanation of the reasoning in human-readable form, as produced by a chain-of-thought LLM | Whether the prose actually reflects what the model computed (faithfulness); it may be coherent and confident but still post-hoc | GPT-4 CoT, Claude CoT | User-facing explanations; interactive Q&A about decisions |

### Critical Thinking Questions

**Question 1.** A SHAP explanation says "feature X (applicant's zip code) contributed +0.35 to this loan denial prediction." A loan officer interprets this as: "If I change the applicant's zip code, their loan application will be approved." Is this interpretation correct? What is the difference between a feature *contributing* to a prediction and that feature *causing* the prediction?

[[___ Your answer here ___]]

*Hint:* Consider two scenarios. In Scenario A, the model learned that certain zip codes correlate with lower credit scores in the training data, and zip code is a proxy for income. In Scenario B, the zip code genuinely causes a different risk assessment. The SHAP value cannot tell these apart. Also consider: if an applicant actually moved zip codes, would the model's prediction necessarily change by exactly +0.35?

**Question 2.** Feature attribution methods produce **local** explanations (why did the model make this particular prediction for this particular instance?) and can also aggregate to **global** explanations (what does the model rely on overall?). Explain in your own words why a feature that ranks as highly important globally might be unimportant (or even irrelevant) for a specific individual prediction.

[[___ Your answer here ___]]

*Hint:* Think about a credit model where "annual income" is the most important feature globally; it matters for most predictions. Now imagine a specific applicant who has extremely poor credit history: the credit history feature alone already drives the prediction to "deny." For this particular applicant, does income matter at all, even though it matters globally?

**Question 3.** A healthcare provider explains an AI diagnosis system to a patient by showing them a bar chart of which symptoms contributed to the diagnosis. The chart is technically accurate. Give one specific reason why this accurate explanation might still mislead the patient, and describe what additional context would be necessary for the explanation to be genuinely useful.

[[___ Your answer here ___]]

*Hint:* Consider scale. The chart shows that "fever" contributed +0.12 and "fatigue" contributed +0.08. These numbers are accurate but what do they mean to a patient? Is +0.12 large or small? What is the baseline? What additional information would a patient need to judge whether the diagnosis is reliable?

Now that we understand what explanations are supposed to do and where they fall short conceptually, we can examine the three most widely-used techniques in detail and evaluate each one's specific strengths and failure modes.

---

## Model 2: SHAP, LIME, and Attention Weights

Three explanation techniques dominate practical XAI for machine learning models. Each has a different theoretical basis, different computational cost, and different failure modes. To make this concrete, here is a tiny worked example using SHAP numbers so you can see what these values actually look like in practice before diving into the theory.

**Worked SHAP Example (sentiment classifier):**

Suppose we have a simple model that predicts sentiment on a scale from 0 (very negative) to 1 (very positive). The *baseline* prediction (the model's output when given no features at all) is 0.5 (neutral). For the sentence "The film was absolutely terrible," the model outputs 0.12 (negative). SHAP might report:

| Word/Feature | SHAP Value | Interpretation |
|---|---|---|
| "terrible" | −0.28 | Strongly pushed prediction toward negative |
| "absolutely" | −0.08 | Moderately amplified the negativity |
| "film" | +0.02 | Tiny push toward positive (films tend to get reviewed positively) |
| "was", "The" | ~0.00 each | Essentially irrelevant to this prediction |

**Check the efficiency property:** 0.5 (baseline) + (−0.28) + (−0.08) + 0.02 + 0.00 + 0.00 ≈ 0.16 ≈ 0.12 (actual prediction). The values sum correctly. This is the "receipt" quality of SHAP: the numbers tell you exactly how much each ingredient contributed to the final total.

---

**SHAP (SHapley Additive exPlanations)**, Lundberg & Lee, 2017

SHAP assigns each feature a "Shapley value", a concept from cooperative game theory that measures each player's fair contribution to the coalition's total payoff. Applied to ML: each feature is a "player," the prediction is the "payoff," and the Shapley value is the feature's average marginal contribution across all possible subsets of features.

SHAP satisfies four desirable properties:
- **Efficiency**: Feature attributions sum to the prediction minus the baseline; you get a complete accounting of every unit of prediction
- **Symmetry**: Two features that always contribute equally to any combination receive equal attributions; no favoritism
- **Dummy**: A feature that never changes the prediction regardless of context gets attribution zero; no credit for irrelevant features
- **Additivity**: Attributions for an ensemble model equal the sum of attributions for each constituent model; the math composes cleanly

Key limitation: exact Shapley values require evaluating the model on all 2^n feature subsets, exponential in the number of features. For a model with 20 features that means over one million evaluations. SHAP approximates this using sampling and model-specific shortcuts (e.g., TreeSHAP for decision tree models is exact and efficient; KernelSHAP for any black-box model approximates using a weighted linear regression over random feature subsets).

**LIME (Local Interpretable Model-Agnostic Explanations)**, Ribeiro, Singh, Guestrin, 2016

LIME explains a single prediction by:
1. Generating a neighborhood of perturbed versions of the input (e.g., randomly masking words in text, zeroing out features in tabular data)
2. Querying the black-box model on each perturbed version to observe how the output changes
3. Fitting a simple interpretable model (e.g., linear regression) to this local neighborhood of input-output pairs
4. Reporting the simple model's coefficients as the explanation; the coefficient for each feature is its estimated local importance

LIME is fast and model-agnostic (works with any model you can query). Key limitations:
- **Instability**: Different random samples of the neighborhood can produce different explanations for the same input, especially in high-dimensional spaces. Running LIME twice on the same instance may yield different feature rankings, which is a serious problem for reproducibility.
- **Locality only**: The explanation is valid only in the local neighborhood around this specific input; it says nothing about the model's global behavior or how it would respond to larger changes.

**Attention Weights**

Transformer-based models (including GPT and BERT) compute attention weights, scalars indicating how much each token "attends to" each other token when generating the next token. Displaying high-attention tokens as highlighted text has become a popular and visually intuitive form of explanation.

Critical finding: **Jain & Wallace (2019), "Attention is not Explanation"** showed that attention weights are often uncorrelated with feature importance as measured by other methods, and that alternative attention distributions (producing very different highlighted tokens) can produce the same model prediction. High attention does not imply causal importance; a token can receive high attention for reasons unrelated to why the model made the prediction it did.

| Method | Faithfulness | Stability | Speed | Human Interpretability |
|--------|-------------|-----------|-------|----------------------|
| **SHAP** | High for tree models (exact); approximation errors possible for black-box models (KernelSHAP) | High: deterministic given a fixed sampling seed | Slow for large models (KernelSHAP can take minutes per prediction); fast for tree models (TreeSHAP runs in milliseconds) | Medium: requires understanding of what the numerical values mean relative to the baseline |
| **LIME** | Medium: the local linear surrogate may not accurately capture the true decision boundary, especially in nonlinear regions | Low: random sampling means different runs produce different results for the same input | Fast: typically seconds per prediction | High: linear coefficients are intuitive ("this word made it 30% more likely to be spam") |
| **Attention** | Low: Jain & Wallace (2019) showed attention is not reliably correlated with causal feature importance | Medium: deterministic for the same input and tokenization, but sensitive to minor input changes | Very fast: computed during inference with no extra cost | High: visual heat-map highlighting is immediately intuitive, but this intuitiveness can be actively misleading |

### Critical Thinking Questions

**Question 4.** A SHAP explanation for a sentiment classifier shows that the word "not" received a Shapley value of +0.4 toward a *positive* sentiment prediction for the sentence "This film is not bad." What might this result indicate about what the model learned? Is this a sign the model is working correctly or incorrectly? How would you investigate further?

[[___ Your answer here ___]]

*Hint:* One possibility is that the model correctly learned that "not bad" is a positive construction, but another possibility is that the model learned "not" predicts positive reviews because phrases like "not only good, but excellent" appear frequently in positive training data. How would you distinguish between these two explanations? What test sentences would help you figure out whether the model truly understands negation?

**Question 5.** LIME's instability means that running the same explanation twice may produce different results. In a high-stakes application (for example, a hiring algorithm explaining why a candidate was rejected) why is this instability a serious problem for the *legal* defensibility of the explanation, even if each individual LIME run is locally accurate?

[[___ Your answer here ___]]

*Hint:* Imagine two candidates with identical applications both receive rejections. Candidate A receives an explanation citing "insufficient years of experience." Candidate B receives an explanation citing "educational background." If the instability of LIME means explanations vary between runs even for the same input, what does this imply about whether the explanations can be used as evidence in a legal challenge? What would a lawyer argue?

**Question 6.** A transformer model is classifying a court document and must determine whether the phrase "not guilty" supports a positive or negative classification. The attention visualization shows high attention weights on the token "not." Based on the Jain & Wallace finding, is this evidence that the model is correctly identifying "not" as the critical negation token, or is it not? Explain what additional experiment you would run to determine whether the model is truly sensitive to the word "not."

[[___ Your answer here ___]]

*Hint:* Jain & Wallace showed you can sometimes swap in completely different attention distributions and get the same model output. So high attention on "not" does not prove "not" caused the prediction. What would you do to directly test whether "not" matters? Consider: what happens to the prediction if you replace "not guilty" with just "guilty"? What if you replace "not" with a synonym like "absolutely not"?

The limitations of SHAP, LIME, and attention weights become even more pronounced when the model being explained is itself generating language (as LLMs do) rather than simply classifying an input.

---

> **Common Misconception:** Students often assume that because attention weights are produced by the model itself (not by an external approximation method like LIME), they must be more faithful to the model's true reasoning than SHAP or LIME. This is backwards. SHAP and LIME, despite being external approximations, are specifically designed and evaluated for faithfulness. Attention weights were designed for the model to function correctly, not to explain itself to humans. The fact that a mechanism is internal to the model does not make it a reliable explanation of the model's decisions.

---

A medical AI system explains its recommendation for a cancer screening referral by highlighting which regions of a patient's medical scan were most important, using LIME to generate the highlighted regions. A radiologist reviewing the recommendation should treat this explanation as:

[( )] Definitive evidence identifying which anatomical features caused the AI's diagnosis; LIME explanations point to what the model attended to, which is not the same as what anatomically caused the finding
[( )] A complete substitute for their own clinical analysis, since the AI has quantified the evidence; quantification creates an appearance of precision that the underlying LIME instability does not support
[(X)] A plausible but potentially unstable local approximation that should complement (and may usefully direct) their clinical judgment, but cannot replace it
[( )] Proof that the model is unbiased and has no spurious correlations in its training data; explanation methods describe behavior on individual inputs; they do not audit whether training data contained biased patterns

> *Hint:* Recall that LIME generates a local approximation by perturbing the input; running it on a different random seed would produce a different highlighted region. "Definitive evidence" requires a level of stability and causal connection that LIME does not provide. The last option conflates explanation (what the model attended to) with fairness (whether the model learned spurious patterns); these are separate questions.

---

## Model 3: Explanations for LLMs and Agents

Traditional XAI methods (SHAP, LIME, attention) were developed for discriminative models (classifiers and regressors) with fixed-length inputs and numeric outputs. Large language models and agents raise entirely new explanation challenges, because now the thing being "explained" is a sequence of reasoning steps in natural language, and the question is not just "which word mattered" but "did the model actually reason the way it claims to have reasoned?"

**Chain-of-thought (CoT) as a built-in explanation**

When an LLM is prompted to "think step by step," it produces a reasoning trace alongside its answer. This feels like a natural explanation of the model's reasoning, and unlike SHAP or LIME, it requires no external approximation. However, research has cast doubt on the **faithfulness** of CoT traces:

- Studies have shown that models sometimes produce a different answer when CoT is removed, suggesting the reasoning trace does influence the output, but only sometimes, and inconsistently.
- More troubling: models can produce plausible-sounding but factually incorrect reasoning chains that nonetheless lead to the correct answer, or worse, incorrect reasoning that leads to a wrong answer while sounding confident and coherent.
- Turpin et al. (2023) showed that LLM reasoning can be influenced by **sycophantic biases** (agreeing with what the prompt implies the user wants) and **anchoring** to irrelevant information in the prompt, while the CoT trace does not acknowledge this influence at all.

This raises the possibility that CoT is sometimes **post-hoc rationalization**: the model had already "decided" (computed a strong candidate answer in its forward pass), and the CoT trace is constructed to justify that decision rather than to reveal the actual computational path.

**Faithfulness vs. Plausibility**

- A **faithful** explanation accurately describes what the model actually computed: if the explanation says "word X caused a negative prediction," removing word X should change the prediction.
- A **plausible** explanation sounds reasonable and coherent to a human reader; it follows logical form and uses the right vocabulary.

These can come apart: an explanation can be highly plausible (it reads like good reasoning) while being unfaithful (the model's prediction was actually driven by a completely different feature). This is the core danger: unfaithful explanations look just like faithful ones to a human reader.

**Practical XAI for agents**

When an *agent* (not just a classifier) is making decisions, explanation requirements change substantially:

- **Logging tool choices with rationales**: the agent should record not just what tool it called but why it chose that tool over the alternatives it had available, so auditors can reconstruct the decision process
- **Confidence calibration**: an agent should output calibrated uncertainty (e.g., "I estimate 70% confidence this is the correct document") rather than always sounding maximally certain, so users can calibrate how much to trust individual outputs
- **Uncertainty quantification**: agents should recognize and communicate when they are operating outside their reliable range, rather than confidently producing plausible-sounding hallucinations with the same tone they use for well-grounded claims

### Critical Thinking Questions

**Question 7.** Design a checklist, intended for a non-technical user (e.g., a manager reviewing an AI recommendation), for evaluating whether a chain-of-thought explanation from an LLM is trustworthy. Your checklist should have at least five items and each item should be actionable (the user can actually check it without needing to understand model internals). Focus on what observable properties of the explanation should raise or lower trust.

[[___ Your checklist here ___]]

*Hint:* Think about: Does the reasoning mention specific evidence, or just general principles? Does the conclusion follow from the stated steps, or does it appear to jump ahead? Does the model acknowledge uncertainty anywhere, or does every step sound equally confident? If you ask the same question twice (or ask it a slightly different way), do you get the same reasoning and the same conclusion? Does the reasoning change if you push back on one of its steps?

**Question 8.** If chain-of-thought reasoning is sometimes a post-hoc rationalization (that is, the model's "decision" was effectively made before the reasoning trace was generated), what does this imply for using CoT as an **accountability mechanism**? Specifically: if a company relies on CoT traces as evidence that their AI system "showed its reasoning" to regulators, is that evidence meaningful? What would a more rigorous accountability mechanism look like?

[[___ Your answer here ___]]

*Hint:* If the CoT trace does not necessarily reflect how the decision was made, what does it actually prove? Think about what a regulator is actually trying to verify when they ask for an explanation. What would be a stronger form of evidence, something that is harder to fabricate or rationalize after the fact?

**Question 9.** For a SHAP or LIME explanation, we can in principle test faithfulness by intervening on features (actually removing or changing them) and observing whether the model's prediction changes as the explanation predicts. What would "ground truth" look like for evaluating the faithfulness of a CoT explanation from an LLM? Describe a specific experiment or test that would provide evidence (even if imperfect evidence) that a CoT trace is faithful rather than post-hoc rationalization.

[[___ Your answer here ___]]

*Hint:* Consider what happens if you take the CoT trace and surgically remove or modify one step: does the conclusion change? What if you present the model with a situation where the "correct" answer and the "answer implied by the user's tone" are different: does the CoT honestly acknowledge the conflict, or does it rationalize toward the answer the user seems to want? This kind of perturbation experiment is the closest analog to SHAP's feature-removal test.

---

## Exercises

**Exercise 1.** Using an accessible sentiment analysis model (e.g., via the `transformers` library in Python or a public API), run the model on five sentences you construct, including at least one sentence with negation (e.g., "not bad"), one with sarcasm, and one that is straightforwardly positive. If SHAP is available for your chosen model, generate explanations for each. If not, use the model's output probabilities and your knowledge of the input to reason about feature importance.

*What to do:* Install `transformers` and `shap` (or use a free Colab notebook). Run a sentiment model on your five sentences. Use `shap.Explainer` on the model, or if SHAP is not available, compare model outputs after manually replacing words to estimate importance.

*Starter hint:* The code below loads a pre-trained sentiment model and runs SHAP to produce token-level attributions; look for which words receive negative SHAP values (pushing toward "negative") versus positive ones, and notice whether the attributions match your intuition about why the sentence has that sentiment:

```python
# Install: pip install transformers shap
from transformers import pipeline
import shap

# Load a sentiment model
sentiment = pipeline("sentiment-analysis",
                     model="distilbert-base-uncased-finetuned-sst-2-english")

sentences = [
    "This movie was not bad at all.",   # negation
    "Oh sure, the service was fantastic.",  # sarcasm
    "I absolutely loved every minute of this film.",  # straightforward positive
    "The plot was confusing but the acting saved it.",  # mixed
    "It was fine."  # ambiguous
]

# Get predictions
results = [sentiment(s)[0] for s in sentences]

# Get SHAP explanations (may take a minute)
explainer = shap.Explainer(sentiment)
shap_values = explainer(sentences)
shap.plots.text(shap_values[0])  # display explanation for first sentence
```

*You've succeeded when:* You have a table showing each sentence, its prediction, its SHAP-attributed words, and at least one case where the attribution surprises you or raises a follow-up question you write down.

[[___ Your answer here ___]]

**Exercise 2.** Find a published paper, blog post, or news article that cites attention maps or attention weights as evidence that a model is interpretable, has learned meaningful structure, or can be trusted. Evaluate the claim against the Jain & Wallace (2019) critique. Is the cited use of attention weights justified? What alternative evidence of meaningful learned structure would be more convincing? Write 150-200 words.

*What to do:* Search Google Scholar or a general web search for "attention visualization model interpretability" and find a concrete example that makes a specific claim about what the attention weights prove. Then apply the Jain & Wallace critique directly: does the article distinguish between "high attention" and "causal importance"?

*Starter hint:* Search for phrases like "attention heat map shows the model focuses on X" and look for whether the author then claims this means the model "understands" or "uses" X. That specific claim is the one to evaluate.

*You've succeeded when:* You have identified the specific claim made about attention weights, stated whether Jain & Wallace's finding undermines it (and how), and proposed a more rigorous form of evidence that would have been more convincing.

[[___ Your answer here ___]]

**Exercise 3.** Review three or more chain-of-thought outputs from a recent agent run in this course (or from a publicly available agent transcript). For each reasoning step in the CoT trace, ask: "Could the model have reached this conclusion without this step, for example, by pattern-matching on surface features of the input?" Flag any steps that appear to be rationalizations rather than necessary reasoning, and explain your reasoning.

*What to do:* Find or generate three CoT outputs from an LLM. For each step in the reasoning trace, write a brief note: "This step seems necessary because \_\_\_" or "This step could be a rationalization because \_\_\_." Look especially for steps that (a) restate the question, (b) draw conclusions that do not follow from previous steps, or (c) introduce new information not in the input.

*Starter hint:* Run the same question twice and compare the CoT traces. If the reasoning steps change significantly between runs but the final answer stays the same, that is evidence the reasoning is not strictly necessary; the model could arrive at the answer without it.

*You've succeeded when:* You have flagged at least two specific steps across your sample as potential rationalizations, with a concrete reason for each flag, and you have at least one step you are confident is genuine reasoning, with an explanation of why.

[[___ Your answer here ___]]

---

## Reflection Prompt

The EU AI Act and similar regulations are establishing a **"right to explanation"** for automated decisions that significantly affect people: credit denials, parole recommendations, hiring decisions, medical triage. This right is grounded in the belief that if people understand why a decision was made, they can contest unfair decisions and hold systems accountable.

But this activity has shown that explanations can be **unfaithful** (LIME instability, CoT rationalization), **misleading** (attention is not explanation), or **technically correct but practically incomprehensible** to non-experts.

**Personal level:** Think about a decision that affected you (a grade, an acceptance, a recommendation) where you were told a reason but suspected the real reason was different. How did that feel? What would you have needed to actually trust the explanation?

**Technical level:** If explanations can be systematically unfaithful, does the legal "right to explanation" genuinely protect the people it is meant to protect, or does it give them false assurance that a decision was made fairly and transparently? What would a technically stronger version of the right to explanation require?

**Societal level:** Who benefits if explanation requirements are easy to satisfy with plausible-but-unfaithful explanations? What incentives do companies face, and how might the law need to evolve to create the right incentives?

Write a combined reflection of 150-250 words addressing at least two of the three levels. The Reflector should be prepared to share the team's position on whether current explanation requirements provide genuine protection.

[[___ Your reflection here ___]]

---

-> Coming Up Next: Now that we understand how to explain individual decisions, we turn to publishing and deploying AI systems, which raises its own set of accountability questions about what it means to put an AI system into the world where others will use it.

---

## Further Reading

- [Credit Score Feature Weight Estimator notebook](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/notebooks/CreditScoreFeatureWeightEstimator.ipynb), a runnable companion that trains a fully transparent linear credit-scoring model and reads its feature weights out as an equation, the baseline against which SHAP and LIME explanations are judged.
- Ribeiro, M. T., Singh, S., and Guestrin, C. (2016). "'Why Should I Trust You?': Explaining the Predictions of Any Classifier." *KDD 2016*. [LIME paper]
- Lundberg, S. M., and Lee, S.-I. (2017). "A Unified Approach to Interpreting Model Predictions." *NeurIPS 2017*. [SHAP paper]
- Jain, S., and Wallace, B. C. (2019). "Attention is not Explanation." *NAACL 2019*.
- Wachter, S., Mittelstadt, B., and Russell, C. (2017). "Counterfactual Explanations Without Opening the Black Box: Automated Decisions and the GDPR." *Harvard Journal of Law & Technology*, 31(2).
- Turpin, M., Michael, J., Perez, E., and Bowman, S. (2023). "Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting." *NeurIPS 2023*.
- European Parliament and Council (2024). "EU Artificial Intelligence Act." *Official Journal of the European Union*. (Articles 13 and 14 on transparency and human oversight.)
- Doshi-Velez, F., and Kim, B. (2017). "Towards A Rigorous Science of Interpretable Machine Learning." *arXiv:1702.08608*.
