<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agenteconomics.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Economics of AI Agents: Pricing, Incentives, and Market Dynamics

CS357 - Foundations of Artificial Intelligence / Agentic AI | Ursinus College

---

## POGIL Roles

This activity uses the **POGIL** (Process Oriented Guided Inquiry Learning) structure. Before beginning, assign one role to each group member:

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task, ensures everyone contributes, watches the clock |
| **Recorder** | Documents the group's answers and reasoning in writing |
| **Presenter** | Speaks for the group during class discussion, summarizes findings |
| **Reflector** | Monitors group process, notes what is working and what is not, leads the Reflection section |

> Rotate roles across activities so everyone practices each one.

---

## Model 1: How AI Is Priced and Why It Matters

AI services are priced on a **per-token** basis, where a token is roughly 0.75 words of text. Pricing structures vary dramatically across the model landscape, and choosing the wrong tier for an application can mean either overpaying or under-performing.

**Model Tier Pricing Comparison**

| Tier | Example | Price / 1M Input Tokens | Price / 1M Output Tokens | Latency | Capability | Who Pays |
|------|---------|------------------------|--------------------------|---------|------------|----------|
| Open-source local | Llama 3 8B (self-hosted) | ~$0 (electricity + hardware amortized) | ~$0 | Low on good GPU; high on CPU | Good for common tasks | Individual / org pays hardware |
| Small cloud | GPT-4o mini, Gemini Flash | $0.10–$0.40 | $0.40–$1.60 | Very low | Strong for structured tasks | Developer / end user |
| Mid cloud | GPT-4o, Claude Sonnet | $2–$5 | $8–$15 | Low | Strong across most tasks | Developer / enterprise |
| Frontier cloud | GPT-4.5, Claude Opus | $15–$75 | $75–$150 | Moderate | Best available capability | Enterprise / research |
| Fine-tuned | Custom fine-tune on mid model | Base + training cost (~$2–$10/run) | 10–30% markup over base | Similar to base | Specialized domain | Enterprise pays training + inference |

**The Cost Cliff**

A 10x jump in capability often corresponds to a 100x jump in per-token cost. This is not linear. Choosing the right model for the task is itself an engineering skill.

**Total Cost of Ownership (TCO)** for an AI application goes beyond the API bill:

- **API costs**: per-token charges, rate limit tiers
- **Infrastructure**: servers, load balancers, monitoring dashboards
- **Engineering**: prompt engineering, evaluation harness, integration work
- **Evaluation**: human raters, automated benchmarks, regression testing
- **Monitoring**: drift detection, latency SLOs, error rate tracking

### Critical Thinking Questions

**Question 1.** A user sends 10 messages per day, averaging 500 input tokens and 200 output tokens per message. Calculate their monthly cost (30 days) for each of the five model tiers in the table. Show your work. At what usage scale does the open-source local option reach break-even compared to the small cloud tier, if the hardware costs $2,000 upfront and uses $15/month in electricity?

[[___ Your answer here ___]]

> Calculation guide: Daily tokens = 10 × 500 + 10 × 200 = 7,000 tokens/day. Monthly = 210,000 tokens. Divide into millions and multiply by price. For break-even: solve for N months where (hardware + N × $15) = N × (cloud monthly cost).

---

**Question 2.** Open-source local models have a sticker price of $0. But the question asked about "non-monetary costs." What does running a local model require that a cloud API call does not? List at least four non-monetary costs and assess their magnitude.

[[___ Your answer here ___]]

> Consider: GPU expertise, setup time, maintenance, security patching, prompt engineering for each new model version, lack of customer support, time to evaluate new models as they release.

---

**Question 3.** Context caching is a pricing feature offered by some providers: if the same system prompt or document is sent in multiple requests, the provider discounts subsequent requests that reuse the cached prefix. How does this change the economics of a RAG (Retrieval-Augmented Generation) system that frequently retrieves the same documents?

[[___ Your answer here ___]]

> If 80% of queries retrieve the same top-5 documents, caching those documents could reduce input token costs substantially. What architecture change enables this?

---

## Model 2: Incentive Misalignment in AI Markets

Markets create incentives that may not align with users' actual needs. In AI, this misalignment appears in multiple forms.

### The Benchmark Gaming Problem

AI companies publish performance numbers on standardized benchmarks:

- **MMLU** (Massive Multitask Language Understanding): 57-subject knowledge test
- **HumanEval**: 164 programming problems
- **MATH**: competition-level mathematics
- **HellaSwag**, **ARC**, **WinoGrande**: reasoning and common sense

Companies optimize heavily for these benchmarks — sometimes inadvertently including benchmark data in training sets (known as **data contamination**), sometimes designing training procedures specifically to improve benchmark scores without improving general capability. The result: benchmark numbers can be misleading guides to real-world usefulness.

### The Moat Dilemma

Open-source models (Llama, Mistral, Phi) commoditize capabilities that were previously proprietary. But large companies have a structural advantage: the **data flywheel**.

- More users → more interaction data → better fine-tuning signal → better model → more users

This advantage is invisible in benchmarks but real in deployment. A company with 100 million users can collect more "what worked / what didn't" signal in a week than a startup can in a year.

### The Principal-Agent Problem in AI Services

Three principals have stakes in how an AI system behaves, with different goals:

| Principal | What They Want | What They Measure | What They'll Trade Off |
|-----------|---------------|-------------------|----------------------|
| **User** | Accurate, honest, useful answers | Task completion, trust, time saved | Will accept some errors if system is generally useful |
| **Company** | Revenue, retention, growth | Daily active users, session length, conversion, NPS | May accept lower accuracy if engagement increases |
| **Regulator** | Safety, non-discrimination, transparency | Incident reports, audit trails, demographic parity | May accept lower capability if risk is reduced |

These goals conflict. A system optimized purely for engagement may maximize time-on-app rather than task completion. A system optimized for regulatory compliance may be overly restrictive. The user is often the least powerful principal.

### Critical Thinking Questions

**Question 4.** A model company claims "our model achieves state-of-the-art results on HumanEval." Before accepting this claim for your coding agent project, what questions should you ask? List at least five, ranked by importance.

[[___ Your answer here ___]]

> Key questions: Were HumanEval problems in the training data? What is the pass@1 vs. pass@k rate? What language subset? What problem difficulty distribution? How does it compare on problems released after the training cutoff? Has it been independently replicated?

---

**Question 5.** Explain how a model company might rationally choose to make a model more **engaging** rather than more **accurate**. What business metrics would support that choice, and what harms could result?

[[___ Your answer here ___]]

> An engaging but inaccurate model might: be more confident (less hedging), generate longer responses (more "value"), be more agreeable (sycophancy), or produce more entertaining but less reliable content. Which business metrics reward each of these?

---

**Question 6.** Compare the incentive structures created by two pricing models: (a) flat monthly subscription, and (b) per-token usage pricing. How does each model change what the company is rewarded for optimizing?

[[___ Your answer here ___]]

> Subscription: company is rewarded for retention — users who feel value and stay. Per-token: company is rewarded for volume — users who send more tokens. Does this change what "better" means for model quality?

---

### Multiple Choice Question

A startup claims their new model beats GPT-4 on every published benchmark. The single most important follow-up question before adopting it for a production application is:

[[ ]] What GPU cluster did they use to train it?
[[ ]] Is the model weights available as open-source?
[[x]] Were the benchmark test sets included in the model's training or fine-tuning data, making benchmark scores potentially inflated?
[[ ]] Is the CEO a graduate of a prestigious technical university?

> **Why this answer?** Benchmark contamination — the inclusion of benchmark test questions in training data — is the most common way benchmark scores become misleading. It does not require intentional fraud; large internet-scraped training corpora frequently contain benchmark problems. Independent evaluation on held-out or post-cutoff data is the appropriate check.

---

## Model 3: Agent Economics for Builders

### Build vs. Buy Decision

When building an AI agent, the core architecture decision is:

1. **Fine-tune a base model**: Pay for training, own the weights, customize deeply. Best for proprietary data, specialized tasks, strict latency requirements.
2. **Use an API**: Pay per call, no maintenance, easy to upgrade. Best for prototyping, variable load, tasks where frontier capability matters.
3. **Build on open-source**: Pay engineering time to deploy and maintain. Best for data privacy requirements, cost at high scale, regulatory constraints on data leaving your infrastructure.

**Total Cost Comparison (Illustrative, 1M queries/month)**

| Approach | Year 1 Cost | Year 3 Cost | Vendor Risk | Control |
|----------|------------|------------|-------------|---------|
| Fine-tuned proprietary | High (training) + Medium (API) | Medium | Locked to one provider's base model | Partial |
| Cloud API only | Medium (per-token) | High (if scale grows) | Deprecation, price changes, API changes | Low |
| Open-source self-hosted | High (engineering + GPU) | Medium (infrastructure only) | Model community health, support burden | Full |

**Vendor lock-in risks** for API-based agents include:

- **Model deprecation**: The model version you depend on is retired (this has happened to GPT-3, Codex, and others)
- **Price increases**: Per-token costs increase; at scale this is an existential budget risk
- **API changes**: Breaking changes in API structure, rate limits, or content policies

### Revenue Models for Agent Products

| Revenue Model | Incentive Created | Risk |
|--------------|-------------------|------|
| Per-seat SaaS (monthly fee per user) | Company incentivized to maximize users, not usage | Users may not use it enough to get value |
| Per-token usage | Company incentivized to maximize token throughput | Users may avoid the product due to unpredictable costs |
| Outcome-based (pay per task completed) | Company incentivized to complete tasks, aligning with user goals | Hard to define "completed"; gaming risk |

### Critical Thinking Questions

**Question 7.** A research group uses GPT-4 via the OpenAI API for a year-long computational linguistics project. Midway through, the API pricing doubles and the specific model version they depend on is deprecated. What mitigation strategies should they have had in place from the start? List at least four.

[[___ Your answer here ___]]

> Consider: budget reserves, model abstraction layers (so swapping models requires changing one config line, not rewriting code), evaluation harnesses (so you can test a new model quickly), open-source fallback options, and data portability.

---

**Question 8.** Design a pricing model for the coding agent you built in this course, imagining you are commercializing it. What does your model incentivize the company to do? Does it align company incentives with user value? How would you detect misalignment early?

[[___ Your answer here ___]]

> Consider: per-task pricing (pay when a bug is fixed), subscription pricing (pay monthly for access), freemium (basic free, advanced paid). Each creates different incentives for what the company optimizes.

---

**Question 9.** If AI inference becomes a true commodity — where all frontier models are essentially equivalent and cost approaches zero — what changes in the AI industry? Who wins, who loses, and what new competitive advantages become important?

[[___ Your answer here ___]]

> Consider: data moats, distribution advantages, integration depth, domain expertise, trust brands, regulatory relationships. What does it mean for CS graduates entering this market?

---

## Exercises

**Exercise 1.** Recall the RAG knowledge base lab from this course. Estimate the token cost of running that system at 1,000 queries per day for a full month. Assume an average of 800 input tokens per query (system prompt + retrieved chunks + user question) and 300 output tokens per response. Compute the monthly cost for two different API tiers from Model 1's table, and identify any cost reduction strategies (caching, smaller model for retrieval, batching) that would apply.

> Deliverable: A cost table with monthly totals and at least two cost-reduction proposals with estimated savings.

---

**Exercise 2.** Find a documented real-world example of a model that performed worse in actual deployment than its benchmark scores predicted. (The GPT-4 code interpreter, early Copilot hallucinations, and medical AI systems are possible starting points.) Write a 300-word case study explaining: what the benchmark showed, what deployment revealed, and what caused the gap.

> Deliverable: 300-word case study with citations.

---

**Exercise 3.** Sketch the complete incentive structure for a "freemium" AI writing tool: users get 10,000 tokens/month free, then pay $20/month for unlimited access. For each of the following stakeholders, describe what they want and what the pricing model incentivizes the company to deliver to them: (a) free-tier users, (b) paid-tier users, (c) the company's investors. Where do these interests conflict?

> Deliverable: A 3-stakeholder incentive analysis and at least two identified conflict points.

---

## Reflection Prompt

If AI capabilities become a commodity — indistinguishable across providers, cheap to access, widely available — then raw AI capability is no longer a competitive differentiator for either companies or individuals.

What will differentiate AI products in that world? And more personally: what skills, knowledge, and judgment will differentiate a CS graduate who understands AI deeply from one who merely knows how to call an API? Does commodity AI raise or lower the value of understanding how it works?

Write at least 200 words. You are encouraged to be specific about your own career assumptions.

[[___ Your reflection here ___]]

---

## Further Reading

- Bessen, J. (2019). *AI and Jobs: The Role of Demand.* NBER Working Paper No. 24235. https://www.nber.org/papers/w24235

- Liang, P. et al. (2022). *Holistic Evaluation of Language Models (HELM).* arXiv:2211.09110. https://arxiv.org/abs/2211.09110

- Srivastava, A. et al. (2022). *Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models (BIG-bench).* arXiv:2206.04615. https://arxiv.org/abs/2206.04615

- Biderman, S. et al. (2024). *Lessons from the Trenches on Reproducible Evaluation of Language Models.* arXiv:2405.14782. https://arxiv.org/abs/2405.14782

- Anthropic. (2024). *Claude Model Pricing.* https://www.anthropic.com/pricing

- OpenAI. (2024). *Deprecated Models Policy.* https://platform.openai.com/docs/deprecations
