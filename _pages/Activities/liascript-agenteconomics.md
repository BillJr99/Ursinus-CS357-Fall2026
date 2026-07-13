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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Token** | The basic unit of AI pricing — roughly 0.75 words, or about 4 characters of English text; models process input tokens and produce output tokens, and you pay for both | "Hello, how are you?" is approximately 6 tokens; a typical paragraph of 100 words is approximately 133 tokens |
| **Total Cost of Ownership (TCO)** | The true all-in cost of running an AI application, including not just the API bill but also infrastructure, engineering time, evaluation, and monitoring | A course assistant that costs $50/month in API fees may cost $5,000/month once you add the engineering hours to maintain prompts, run evaluations, and handle edge cases |
| **Benchmark contamination** | When test questions from a published benchmark appear in a model's training data, inflating its benchmark score beyond its genuine capability | A model trained on internet text that included HumanEval's 164 coding problems will score well on HumanEval without being a good general programmer |
| **Data flywheel** | A self-reinforcing competitive advantage where more users generate more data, which improves the model, which attracts more users | ChatGPT's 100M users generate millions of interaction signals per day; a startup with 1,000 users cannot collect enough signal to compete, even with access to similar base models |
| **Principal-agent problem** | A conflict of interest between the person giving instructions (the principal) and the entity carrying them out (the agent) who has different incentives | An AI company (agent) is hired to provide users (principals) with useful answers, but the company is also rewarded for engagement — so it may optimize for time-on-app rather than task completion |
| **Vendor lock-in** | When switching from one AI provider to another becomes very costly due to integration depth, proprietary formats, or deprecated alternatives | A team that spent six months fine-tuning prompts and evaluation pipelines for GPT-4 faces enormous switching costs if OpenAI doubles the price or deprecates the model |

---

## Model 1: How AI Is Priced and Why It Matters

Think of AI pricing like a cell phone plan with no unlimited data — every word you send and every word you receive gets counted and billed. Choosing the right "plan" for your application is itself an engineering decision, not just an accounting one. A model that is 10x more expensive might be only 20% better on your task; or it might be 10x better and worth every cent. Understanding how pricing works is how you make that call without guessing.

AI services are priced on a **per-token** basis, where a token is roughly 0.75 words of text. Pricing structures vary dramatically across the model landscape, and choosing the wrong tier for an application can mean either overpaying by 100x or under-performing on capability.

**Model Tier Pricing Comparison (approximate 2025–2026 rates)**

| Tier | Example | Price / 1M Input Tokens | Price / 1M Output Tokens | Latency | Capability | Who Pays |
|------|---------|------------------------|--------------------------|---------|------------|----------|
| Open-source local | Llama 3 8B (self-hosted on your own GPU) | ~$0 API cost (but electricity + hardware amortized) | ~$0 API cost | Very low on a good GPU; can be slow on CPU | Strong for common tasks; weaker than frontier models on nuanced reasoning | Individual or organization pays hardware and electricity; no per-token fee |
| Small cloud | GPT-4o mini, Gemini Flash 1.5 | $0.10–$0.40 per million input tokens | $0.40–$1.60 per million output tokens | Very low — responses typically in under 1 second | Strong for structured extraction, classification, simple Q&A | Developer or end user pays per call; no upfront hardware cost |
| Mid cloud | GPT-4o, Claude Sonnet 3.7 | $2–$5 per million input tokens | $8–$15 per million output tokens | Low — typically 1–3 seconds for moderate response length | Strong across most tasks including complex reasoning, code generation, analysis | Developer or enterprise pays per call; this is the most common tier for production applications |
| Frontier cloud | GPT-4.5, Claude Opus | $15–$75 per million input tokens | $75–$150 per million output tokens | Moderate — may be 5–30 seconds for long responses | Best available capability on the most demanding tasks — complex multi-step reasoning, nuanced judgment | Enterprise or research; typically justified only for tasks where the capability gap is large and the per-task value is high |
| Fine-tuned | Custom fine-tune on a mid-tier model (e.g., GPT-4o fine-tune) | Base model price + training cost (~$2–$10 per training run) | 10–30% markup over the base model's output price | Similar to the base model | Specialized domain knowledge; consistent format adherence; reduced system prompt length needed | Enterprise pays both training costs (one-time or periodic) and inference costs (per-token, ongoing) |

**The Cost Cliff**

A 10x jump in capability often corresponds to a 100x jump in per-token cost. This is not linear. Choosing the right model for the task is itself an engineering skill — using a frontier model for a task a small model handles well is like using a sports car to deliver groceries.

**Worked Example: Calculating Monthly API Cost**

Suppose your course chatbot serves 50 students. Each student asks 5 questions per day, with an average of 400 input tokens (system prompt + conversation history + question) and 200 output tokens (the answer) per exchange.

- Daily tokens: 50 students × 5 questions × (400 input + 200 output) = 150,000 input tokens + 75,000 output tokens
- Monthly tokens (30 days): 4,500,000 input tokens + 2,250,000 output tokens

| Tier | Monthly Input Cost | Monthly Output Cost | Monthly Total |
|------|-------------------|---------------------|---------------|
| Small cloud ($0.15 input / $0.60 output per 1M tokens) | 4.5 × $0.15 = **$0.68** | 2.25 × $0.60 = **$1.35** | **~$2.03/month** |
| Mid cloud ($3.00 input / $12.00 output per 1M tokens) | 4.5 × $3.00 = **$13.50** | 2.25 × $12.00 = **$27.00** | **~$40.50/month** |
| Frontier cloud ($30 input / $100 output per 1M tokens) | 4.5 × $30 = **$135** | 2.25 × $100 = **$225** | **~$360/month** |

The same application costs $2/month on a small model or $360/month on a frontier model — a 180x difference. For a student course assistant where the questions are well-scoped, the small model may perform acceptably at 1% of the cost.

**Total Cost of Ownership (TCO)** for an AI application goes beyond the API bill:

- **API costs**: per-token charges, rate limit tier fees
- **Infrastructure**: servers, load balancers, monitoring dashboards, logging systems
- **Engineering**: prompt engineering, evaluation harness development, integration work
- **Evaluation**: human raters, automated benchmarks, regression testing to catch capability regressions
- **Monitoring**: drift detection, latency SLO tracking, error rate dashboards

### Critical Thinking Questions

**Question 1.** Using the worked example above as a template, calculate the monthly API cost for a user who sends 10 messages per day, averaging 500 input tokens and 200 output tokens per message, for a full 30-day month. Compute the cost for the small cloud tier and the mid cloud tier. Then calculate: at what usage scale (number of months of cloud API use) does a $2,000 GPU running local inference break even vs. the small cloud tier, if the GPU uses $15/month in electricity?

*Starter hint:* Step 1 — Daily tokens: 10 messages × (500 input + 200 output) = 7,000 tokens. Monthly: 210,000 input tokens + 60,000 output tokens = 0.21M input + 0.06M output. Step 2 — Multiply by the price per 1M tokens for each tier. Step 3 — For break-even: total local cost = hardware ($2,000) + N months × electricity ($15). Total cloud cost = N months × monthly cloud bill. Set them equal and solve for N. Which tier makes local inference competitive faster?

**Question 2.** Open-source local models have a sticker price of $0 per API call. But the question asked about "non-monetary costs." What does running a local model actually require that a cloud API call does not? List at least four non-monetary costs and assess their magnitude.

*Hint:* Think through the full lifecycle: initial setup (GPU selection, driver installation, model download, serving framework configuration — easily 8–40 hours of engineering time), ongoing maintenance (model updates, security patches, serving framework upgrades), operational expertise (understanding GPU memory limits, batching, quantization tradeoffs), support (no vendor support — you file GitHub issues and wait), and opportunity cost (the engineering hours spent on infrastructure could have been spent building the application itself). How do these costs compare for a solo student developer vs. a team of five?

**Question 3.** Context caching is a pricing feature offered by some providers: if the same system prompt or long document is sent in multiple requests, the provider discounts subsequent requests that reuse the cached prefix. How does this change the economics of a RAG (Retrieval-Augmented Generation) system that frequently retrieves the same documents?

*Hint:* In a RAG system, each query retrieves relevant chunks from a knowledge base and appends them to the prompt. If 80% of queries retrieve the same top-5 documents (a common pattern for FAQ-style knowledge bases), caching those documents reduces the effective input token cost of 80% of your queries — sometimes by 50–90%. What architecture change enables caching? (Hint: the cached content must be at the beginning of the prompt, before the per-query content.) How does this interact with your break-even calculation from Question 1?

---

With a firm grasp of how token pricing and total costs shape what you build, you are ready to examine why even well-priced AI products may still optimize for the wrong goals.

## Model 2: Incentive Misalignment in AI Markets

Markets create incentives that may not align with users' actual needs. Think of how social media platforms optimize for engagement (time-on-app) rather than wellbeing (what's actually good for users). The two are correlated but not identical — and the gap between them causes real harm. AI has analogous incentive misalignments, and understanding them makes you a more skeptical consumer of model claims and a more thoughtful builder.

### The Benchmark Gaming Problem

AI companies publish performance numbers on standardized benchmarks:

- **MMLU** (Massive Multitask Language Understanding): 14,000 multiple-choice questions across 57 subjects — tests broad factual knowledge
- **HumanEval**: 164 programming problems in Python — tests code generation ability
- **MATH**: 12,500 competition-level math problems — tests mathematical reasoning
- **HellaSwag**, **ARC**, **WinoGrande**: tests of commonsense reasoning, causal understanding, and disambiguation

Companies optimize heavily for these benchmarks — sometimes inadvertently including benchmark data in training sets (known as **benchmark contamination**), sometimes designing training procedures specifically to improve benchmark scores without improving general capability. The result: benchmark numbers can be misleading guides to real-world usefulness.

A striking example: several leading models achieved near-perfect scores on GSM8K (grade-school math) while failing basic arithmetic when problems were slightly rephrased, strongly suggesting the models had seen the test problems during training.

### The Moat Dilemma

Open-source models (Llama, Mistral, Phi, Qwen) commoditize capabilities that were previously proprietary. But large companies have a structural advantage: the **data flywheel**.

- More users → more interaction data → better fine-tuning signal → better model → more users

This advantage is invisible in benchmarks but real in deployment. A company with 100 million users can collect more "what worked / what didn't" signal in a week than a startup can in a year. Benchmarks measure capability at a point in time; the flywheel measures trajectory over time.

### The Principal-Agent Problem in AI Services

Three principals have stakes in how an AI system behaves, with different goals:

| Principal | What They Actually Want | What They Measure | What They Will Trade Off | How They Protect Their Interests |
|-----------|------------------------|-------------------|--------------------------|----------------------------------|
| **User** | Accurate, useful answers that help them complete real tasks and make better decisions | Task completion rate, trust, time saved, whether they come back with harder questions | Will accept some errors if the system is generally useful and they know to verify important outputs | Switching to a competitor, giving low ratings, sharing negative experiences publicly |
| **Company** | Revenue, user retention, growth metrics that satisfy investors | Daily active users, session length (engagement), conversion rate (free to paid), Net Promoter Score | May accept lower accuracy on edge cases if core engagement increases; may optimize for perceived quality rather than actual quality | Faces competition; must respond to reputation damage; may face regulatory pressure |
| **Regulator** | Safety, non-discrimination, transparency, accountability when things go wrong | Incident reports, audit trail completeness, demographic parity in outcomes, explainability of decisions | May accept lower capability if risk is reduced; may require documentation overhead that slows development | Fines, enforcement actions, mandatory audits, usage restrictions |

These goals conflict. A system optimized purely for engagement may maximize time-on-app rather than task completion. A system optimized for regulatory compliance may be overly restrictive. The user is often the least powerful principal — they have the least information about how the system was optimized.

> ⚠️ **Common Misconception:** Many students assume that "state of the art on benchmarks" means "best for my use case." This is almost never true. Benchmarks measure performance on curated test sets; your use case has different distributions of questions, different error tolerances, and different capability requirements. A model that scores 90% on MMLU might perform worse on your specific domain than a model that scores 80% on MMLU but was trained on domain-relevant data. Always evaluate models on your actual task before choosing.

### Critical Thinking Questions

**Question 4.** A model company claims "our model achieves state-of-the-art results on HumanEval." Before accepting this claim for your coding agent project, what questions should you ask? List at least five, ranked by importance.

*Hint:* Your five most important questions, in rough priority order: (1) Were HumanEval problems in the training data, and how do you know? (2) What is the pass@1 rate vs. pass@10 rate — a model that can solve a problem given 10 tries is very different from one that gets it right the first time? (3) What programming language distribution was tested — Python-only models may fail on JavaScript or TypeScript? (4) How does it perform on problems released after the training cutoff — a proxy for whether benchmark performance is genuine? (5) Has this result been independently replicated by a third party not affiliated with the company?

**Question 5.** Explain how a model company might rationally choose to make a model more **engaging** rather than more **accurate**. What business metrics would support that choice, and what harms could result?

*Hint:* An engaging but less accurate model might: be more confident (less hedging — users find uncertainty annoying), generate longer responses (more apparent "value" per query), be more agreeable and validating (sycophancy — users prefer being agreed with), or produce more entertaining framing even for mundane questions. Which business metrics reward each of these behaviors? (DAU? Session length? Rating scores?) What specific harms does each cause in a course assistant context?

**Question 6.** Compare the incentive structures created by two pricing models: (a) flat monthly subscription ($20/month regardless of use), and (b) per-token usage pricing (pay for what you use). How does each model change what the company is rewarded for optimizing?

*Hint:* For subscription: the company's revenue is fixed once you subscribe, so they are rewarded for keeping you subscribed — which means making you feel value, preventing churn, and beating competitors on overall satisfaction. For per-token: the company is rewarded for volume — every additional query generates revenue, so they are rewarded for making the model useful enough that you query it more often. Does per-token pricing create any incentive to make responses longer than necessary? Does subscription pricing create any incentive to reduce quality if users don't notice?

---

### Multiple Choice Question

A startup claims their new model beats GPT-4 on every published benchmark. The single most important follow-up question before adopting it for a production application is:

[[MC]]
- ( ) What GPU cluster did they use to train it?
- ( ) Are the model weights available as open-source?
- (x) Were the benchmark test sets included in the model's training or fine-tuning data, making benchmark scores potentially inflated beyond genuine capability?
- ( ) Did the model achieve these scores on a single benchmark run, or were the results averaged across multiple evaluation runs?

---

Understanding these market-level misalignments prepares you to make more deliberate design and business-model choices as you architect and commercialize your own AI agents.

## Model 3: Agent Economics for Builders

### Build vs. Buy Decision

When building an AI agent, the core architecture decision is:

1. **Fine-tune a base model**: Pay for training, own the weights, customize deeply. Best for proprietary data, specialized tasks, strict latency requirements, or cases where the system prompt would otherwise be very long.
2. **Use an API**: Pay per call, no maintenance burden, easy to upgrade to new model versions. Best for prototyping, variable load, tasks where frontier capability matters and budget allows it.
3. **Build on open-source**: Pay engineering time to deploy and maintain infrastructure. Best for data privacy requirements, cost at high scale, or regulatory constraints on data leaving your infrastructure.

**Total Cost Comparison (Illustrative, 1M queries/month)**

| Approach | Year 1 Cost Drivers | Year 3 Cost Drivers | Vendor Risk | Control Level | Best For |
|----------|---------------------|---------------------|-------------|---------------|----------|
| Fine-tuned proprietary API | High training cost (one-time or per-version) + ongoing per-token API fees | Moderate — training costs amortize, but API price changes and model deprecations are real risks | High — locked to one provider's base model; if they deprecate the fine-tuning capability, you lose your customization | Partial — you own the fine-tuning data and training; you do not own the base weights | Specialized domains with proprietary training data and moderate scale |
| Cloud API only (no fine-tuning) | Moderate per-token fees — easy to estimate and scale | High if usage grows — per-token costs scale linearly with volume; a 10x user growth = 10x API bill | Moderate — model deprecation happens (GPT-3, Codex, and text-davinci-003 have all been retired); API breaking changes require engineering fixes | Low — prompt-only customization; no ownership of model behavior | Prototypes, early-stage products, applications where frontier capability matters more than cost |
| Open-source self-hosted | High upfront engineering + GPU infrastructure cost; typically 3–6 months to reach production quality | Moderate — infrastructure costs only; no per-token fees; model upgrades are a choice, not mandatory | Low (model community) — depends on the open-source community remaining active; no support contract; security patching is your responsibility | Full — you own everything; can modify, distill, or deploy however you choose | High-scale applications, privacy-sensitive data, regulatory environments where data cannot leave your infrastructure |

**Vendor Lock-in Risks for API-Based Agents**

These risks are real and have already happened to production systems:

- **Model deprecation**: GPT-3 (2020–2023), Codex (2021–2023), text-davinci-003 (2022–2024) — all retired with 6 months notice or less; teams that had not abstracted their model calls had to rewrite integration code under time pressure
- **Price increases**: OpenAI raised prices for several model tiers in 2023; a system budgeted for $500/month became a $2,000/month system without any usage change
- **API changes**: Rate limit restructuring, context window changes, content policy updates, and output format changes have all required emergency engineering fixes in production systems
- **Capability regressions**: Model updates sometimes make models *worse* at specific tasks even while improving average performance; without an evaluation harness, you may not notice until users complain

### Revenue Models for Agent Products

| Revenue Model | What the Company Gets Paid For | What This Incentivizes the Company to Optimize | Risk for Users |
|--------------|-------------------------------|------------------------------------------------|----------------|
| Per-seat SaaS (flat monthly fee per user) | Keeping each user subscribed month after month — they pay whether they use it or not | Retention — users must feel enough ongoing value to renew; the company wins by making the product genuinely useful over time | Users who don't use it much still pay; company has weak incentive to optimize for heavy-use efficiency |
| Per-token usage pricing (pay for what you use) | Raw volume of tokens processed — more queries = more revenue | Token throughput — making the product useful enough that users query it frequently; may inadvertently incentivize longer responses than necessary | Users face unpredictable bills; power users pay much more than light users for the same subscription-style access |
| Outcome-based pricing (pay per task completed) | Successful task completions — company only earns when the user succeeds | Task completion quality — most aligned with user goals of any model; company wins only when the user wins | Hard to define "completed" for complex tasks; gaming risk (marking tasks complete before they fully are); requires verification infrastructure |

### Critical Thinking Questions

**Question 7.** A research group uses GPT-4 via the OpenAI API for a year-long computational linguistics project. Midway through, the API pricing doubles and the specific model version they depend on is deprecated with 90 days notice. What mitigation strategies should they have had in place from the start? List at least four.

*Starter hint:* (1) Budget reserves — a line item for API cost variance of 2x, treating the original estimate as a floor not a ceiling. (2) Model abstraction layer — a single configuration file that specifies which model to use, so swapping models requires changing one line rather than rewriting every API call in the codebase. (3) Evaluation harness — a suite of test cases with expected outputs, so you can evaluate a replacement model in hours rather than weeks. (4) Open-source fallback plan — identify which open-source model you would switch to and test it at the start of the project, even if you don't deploy it. (5) Data portability — store all prompts, inputs, and outputs in a provider-agnostic format. Now add your own mitigation not listed here.

**Question 8.** Design a pricing model for the coding agent you built in this course, imagining you are commercializing it. What does your model incentivize the company to do? Does it align company incentives with user value? How would you detect misalignment early?

*Starter hint:* Consider three options: (1) Per-task pricing — $0.10 per bug fixed or test passed (outcome-aligned but requires defining "fixed"); (2) Subscription pricing — $15/month for 100 queries (simple but may not align with how students actually use it); (3) Freemium — 20 free queries/month, then $5/10 queries (optimizes for converting free users, may create frustrating cutoffs). For each, ask: what does a bad actor inside the company do to maximize revenue under this model? Is that behavior harmful to users? What metric would you track to detect that behavior early?

**Question 9.** If AI inference becomes a true commodity — where all frontier models are essentially equivalent and cost approaches zero — what changes in the AI industry? Who wins, who loses, and what new competitive advantages become important?

*Hint:* When a core technology commoditizes, competition shifts to adjacent layers. When electricity commoditized, competition moved to appliances and infrastructure. When cloud computing commoditized, competition moved to developer experience and managed services. If raw AI capability commoditizes: data moats (proprietary training data that competitors can't replicate) become critical; distribution advantages (being embedded in products people already use) matter more than model quality; domain expertise (knowing which questions to ask the model and how to validate its answers in a specific domain) differentiates practitioners; trust brands (users who trust one provider's safety and reliability will pay a premium even for equivalent capability) persist. As a CS graduate entering this market in 2026–2027, which of these advantages can you build?

---

## Exercises

**Exercise 1: RAG Cost Estimation**

*What to do:* Recall the RAG knowledge base lab from this course. Estimate the token cost of running that system at 1,000 queries per day for a full month. Assume an average of 800 input tokens per query (system prompt + retrieved chunks + user question) and 300 output tokens per response. Compute the monthly cost for two different API tiers from Model 1's table, and identify any cost reduction strategies (caching, smaller model for retrieval, batching) that would apply.

*Starter hint:* Step 1 — Monthly input tokens: 1,000 queries/day × 30 days × 800 tokens = 24,000,000 input tokens = 24M tokens. Monthly output tokens: 1,000 × 30 × 300 = 9,000,000 = 9M tokens. Step 2 — Apply the small cloud price ($0.15 input / $0.60 output per 1M): input = 24 × $0.15 = $3.60; output = 9 × $0.60 = $5.40; total = $9/month. Apply the mid cloud price ($3.00 input / $12.00 output per 1M): input = 24 × $3.00 = $72; output = 9 × $12.00 = $108; total = $180/month. Step 3 — For cost reduction: if you cache the system prompt (say 300 tokens) across all queries with a 90% cache hit rate, you save 0.9 × 300 × 30,000 = 8.1M tokens of input. At mid cloud prices, that's $24.30/month saved. Calculate your full cost table with and without caching.

*You've succeeded when:* You have a cost table showing monthly totals for two tiers, at least two cost-reduction strategies with estimated savings, and a recommendation for which tier to use based on the application's value (a course assistant budget vs. a commercial product budget).

**Exercise 2: Benchmark vs. Deployment Gap Case Study**

*What to do:* Find a documented real-world example of a model that performed worse in actual deployment than its benchmark scores predicted. Write a 300-word case study explaining: what the benchmark showed, what deployment revealed, and what caused the gap.

*Starter hint:* Several well-documented cases exist: (1) Early GitHub Copilot hallucinated function signatures and API calls that did not exist, despite strong HumanEval scores — the benchmark tested generating complete functions; real-world code required knowing which libraries existed and were installed. (2) Medical AI systems (IBM Watson for Oncology) showed strong performance on curated cancer cases but generated unsafe treatment recommendations on real patients — the training data was carefully curated by experts; deployment data was messy and context-heavy. (3) GPT-4 showed strong performance on the bar exam but gave confidently wrong answers on straightforward estate planning questions when tested by practicing lawyers. For each, explain which of the benchmark limitations from Model 2 (contamination, distribution mismatch, capability vs. reliability gap) best explains the deployment failure.

*You've succeeded when:* Your 300-word case study identifies the specific benchmark(s) cited, the specific deployment failure observed, and gives a mechanistic explanation — not just "the AI was wrong" but why the benchmark failed to predict the deployment failure.

**Exercise 3: Freemium Incentive Analysis**

*What to do:* Sketch the complete incentive structure for a "freemium" AI writing tool: users get 10,000 tokens/month free, then pay $20/month for unlimited access. For each of the following stakeholders, describe what they want and what the pricing model incentivizes the company to deliver to them: (a) free-tier users, (b) paid-tier users, (c) the company's investors. Where do these interests conflict?

*Starter hint:* Free-tier users want: maximum value within the 10,000-token limit. The company wants: to deliver just enough value to hook them but create enough friction at the limit to make $20/month feel worthwhile. Paid-tier users want: unlimited, high-quality access with no surprises. The company wants: to retain them at $20/month with minimal additional cost — which means not over-delivering so much that free users never convert. Investors want: growth in paid subscribers, which means optimizing the free-to-paid conversion rate — which may mean making the free tier frustratingly limited. Where specifically do these three sets of interests create conflicting pressures on product design? What specific product decisions (limit size, limit reset period, features locked to paid tier) reveal the company's priority among these three?

*You've succeeded when:* You have a three-part stakeholder analysis, at least two specific identified conflicts (not just "they want different things" but which specific product decisions create the conflict), and a brief recommendation for how a company could reduce the conflict while remaining profitable.

---

## Reflection Prompt

**Personal level:** Think about the AI tools you use personally — for this course, for other courses, or in daily life. Do you know how they are priced? Do you know what the company is optimizing for? Has your understanding of incentive misalignment from today's activity changed how you think about any specific tool you use? Be specific.

**Technical level:** If AI capabilities become a commodity — indistinguishable across providers, cheap to access, widely available — then raw AI capability is no longer a competitive differentiator for either companies or individuals. What will differentiate AI products in that world? And more personally: what skills, knowledge, and judgment will differentiate a CS graduate who understands AI deeply from one who merely knows how to call an API? Does commodity AI raise or lower the value of understanding how it works?

**Societal level:** The economics of AI development — high upfront costs, data flywheel advantages, vendor lock-in — tend to concentrate AI capability in a small number of very large companies. Does this concentration concern you? What are the risks of having most of the world's foundational AI infrastructure controlled by three or four companies? What policy mechanisms might address concentration risks, and what tradeoffs would they involve?

→ Coming Up Next: Return to the course project to apply today's pricing analysis to your own system — estimate your token costs, identify your principal-agent dynamics, and choose a monetization model for your agent.

---

## Further Reading

- Bessen, J. (2019). *AI and Jobs: The Role of Demand.* NBER Working Paper No. 24235. https://www.nber.org/papers/w24235

- Liang, P. et al. (2022). *Holistic Evaluation of Language Models (HELM).* arXiv:2211.09110. https://arxiv.org/abs/2211.09110

- Srivastava, A. et al. (2022). *Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models (BIG-bench).* arXiv:2206.04615. https://arxiv.org/abs/2206.04615

- Biderman, S. et al. (2024). *Lessons from the Trenches on Reproducible Evaluation of Language Models.* arXiv:2405.14782. https://arxiv.org/abs/2405.14782

- Anthropic. (2024). *Claude Model Pricing.* https://www.anthropic.com/pricing

- OpenAI. (2024). *Deprecated Models Policy.* https://platform.openai.com/docs/deprecations
