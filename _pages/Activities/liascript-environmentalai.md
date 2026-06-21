# Environmental Impact and the Carbon Cost of Intelligence
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-environmentalai.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-environmentalai.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Environmental Impact and the Carbon Cost of Intelligence

The discourse around AI rarely foregrounds what it costs the planet to run. Energy consumption, water usage, and embodied carbon in hardware are not edge considerations; at the scale of contemporary model training and inference, they are material. Today you develop the quantitative literacy to reason about these costs, the design vocabulary to reduce them, and the critical framework to resist the optimism that efficiency gains automatically reduce aggregate impact. The goal is not guilt but judgment: knowing when AI use is worth its cost and when a smaller or local tool would serve equally well.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Manager ensures the team works through the quantitative models rather than skimming them; the Recorder captures the team's carbon audit numbers and design decisions; the Presenter prepares to explain the Jevons paradox argument to the class; the Reflector watches for moments when the team's reasoning becomes motivated (defending AI use rather than evaluating it) and names it. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Orders of Magnitude

## 1. What It Costs to Train and Infer

**Training** a large language model is a one-time but enormous energy expenditure. Estimates for GPT-3 (175B parameters) place training energy at approximately 1,287 MWh and carbon emissions at roughly 500 tonnes of CO$_2$ equivalent — comparable to the lifetime emissions of five average American cars or about 125 transatlantic flights. GPT-4-scale models are estimated to require substantially more, though developers do not publish precise figures. These numbers are order-of-magnitude estimates; the actual figure depends heavily on the regional carbon intensity of the electrical grid where training runs.

**Inference** at scale often exceeds training in total impact because it recurs with every query. A single ChatGPT prompt is estimated to consume roughly ten times the energy of a Google search. With hundreds of millions of queries per day, inference energy becomes the dominant term. Water usage compounds this: Microsoft reported in 2023 that its data centers consumed approximately 1.7 liters of water (for cooling) per 20–50 ChatGPT prompts. Water stress in regions hosting large data centers is a real externality, not a hypothetical one.

**Embodied carbon** — the emissions from manufacturing GPUs, servers, networking equipment, and undersea cables — is typically excluded from carbon accounting for AI systems. Estimates suggest embodied carbon may represent 50–80% of a data center's lifetime carbon footprint for hardware-intensive workloads. A GPU's fabrication at advanced process nodes involves energy-intensive lithography and chemical processes; the supply chain spans continents. Ignoring embodied carbon systematically understates the cost of "upgrading to a more efficient model."

---

## Model 1: Carbon Cost Comparison

| Action | Estimated CO$_2$ equivalent | Approximate real-world equivalent |
|---|---|---|
| Training a GPT-3-scale model | ~500 tonnes | Lifetime emissions of ~5 American passenger cars |
| Training a GPT-4-scale model | ~1,000–10,000 tonnes (estimated) | 250–2,500 transatlantic flights |
| 1 million ChatGPT-style queries | ~0.5 tonnes | Driving a gasoline car ~2,000 km |
| 1 AI image generation (diffusion model) | ~0.003 kg | Charging a smartphone once |
| 1 standard email (no attachment) | ~0.000004 kg | 1 second of a 60W light bulb |
| A laptop running for 8 hours | ~0.07 kg | 700 emails or ~23 AI image generations |
| 1 hour of video streaming | ~0.036 kg | Comparable to a laptop at moderate load |

*Note: All figures are order-of-magnitude estimates that vary by grid carbon intensity, hardware generation, and methodology. Treat them as rough anchors for proportional reasoning, not precise measurements.*

### Critical Thinking Questions

1. The table spans roughly nine orders of magnitude from a single email to GPT-4-scale training. Which comparison is most surprising to you, and why? What does the surprise reveal about your prior mental model of AI energy costs?
2. A company argues that switching from a 70B-parameter model to a 7B-parameter model for a customer service chatbot running 10 million queries per month has a larger carbon impact than switching its data center to renewable energy. Construct a rough quantitative argument for or against this claim using the proportional reasoning the table supports.
3. "Embodied carbon" is excluded from most AI carbon footprints. Why might organizations have an incentive to exclude it? Name two design or procurement decisions that would reduce embodied carbon and explain why they are not standard practice.

---

# Part II: Right-Sizing and the Local-First Principle

## 2. Choosing the Right Tool for the Task

**Model right-sizing** is the practice of matching model capability to task requirements. Using a 100B-parameter frontier model to classify whether an email is spam, when a fine-tuned 100M-parameter model achieves the same accuracy, is waste — in energy, latency, and cost. The principle sounds obvious but is routinely violated because frontier APIs are convenient, benchmarks reward capability, and the marginal cost of a larger model is invisible to the developer while the capability gain is visible.

**The local-first principle** holds that a model running on a user's device consumes no data center energy, produces no inference-time cloud emissions, and eliminates the water cost of remote cooling. For many tasks — summarization, code assistance, question answering on local documents — a 7B or 13B-parameter quantized model running on a consumer GPU or Apple Silicon chip is competitive with much larger cloud models. The choice of "local vs. cloud" is therefore not only a privacy decision but an environmental one.

**Caching and batching** are further levers: caching the responses to common queries eliminates redundant computation; batching multiple inference requests reduces per-query overhead. These are standard software engineering practices applied to an unusually energy-visible workload.

**Grid carbon intensity** varies dramatically by region and time of day. The same computation performed in Iceland (near-zero-carbon geothermal grid) versus coal-heavy regions can differ by a factor of 50 or more in carbon impact. Schedulable workloads (batch inference, retraining runs) can be routed to lower-carbon regions or shifted to hours when renewable supply peaks. This is operationally feasible; it is not widely practiced.

---

## Model 2: Right-Sizing Decision Matrix

| Task | Appropriate Model Scale | Rationale | Local vs. Cloud Preference |
|---|---|---|---|
| Classify incoming email as spam / not spam | Fine-tuned small model (≤1B parameters) | Binary classification; well-defined signal; massive labeled data available | Local or edge; no real-time cloud needed |
| Summarize a 10-page PDF | Mid-size model (7B–13B parameters) | Requires coherent abstractive reasoning; document fits in context | Local viable on consumer hardware; cloud for convenience |
| Generate a photorealistic logo | Diffusion model (specialized) | Image synthesis requires a different architecture from text; scale matters for quality | Cloud typical; GPU requirements are high |
| Debug a 500-line codebase with cross-file dependencies | Large model (30B+ parameters) with code specialization | Complex multi-step reasoning; large context window; rare error patterns | Cloud preferred; local possible on high-end hardware |
| Answer a trivia question | Any scale, including very small | Low reasoning demand; factual recall; fast response more important than depth | Local sufficient; API call is unnecessary overhead |
| Transcribe and summarize a 2-hour lecture | Specialized speech model + summarizer | Two-model pipeline; first model is heavily optimized; summarizer is lightweight | Local feasible; privacy argument strong |

### Critical Thinking Questions

4. The right-sizing matrix does not include a column for accuracy. Construct the missing argument: under what conditions does using a smaller model for a task impose a *social* cost that must be weighed against the carbon benefit?
5. The "local-first" principle is often presented as unambiguously better. Identify two scenarios where local inference has *worse* environmental impact than a well-managed cloud inference endpoint, and explain why.
6. You are advising a nonprofit organization that does document analysis for human rights investigations — processing thousands of witness testimonies in multiple languages. They currently use a frontier cloud API. What model-choice and deployment recommendations would you make, and how would you weigh privacy, accuracy, cost, and carbon against each other?

[[MC]]
A development team wants to reduce the carbon footprint of their AI-powered customer support system. Which intervention is most likely to produce the largest reduction in inference-time carbon emissions?
- ( ) Switching from Python to a compiled language for the API wrapper
- ( ) Adding a caching layer that serves identical responses to repeated queries without re-running the model
- (x) Replacing a 70B-parameter frontier model with a fine-tuned 7B-parameter model that achieves equivalent accuracy on the support domain
- ( ) Moving the service from HTTP to WebSockets

---

# Part III: Jevons Paradox and Systemic Risk

## 3. Why Efficiency Gains May Not Reduce Impact

**Jevons paradox** (William Stanley Jevons, 1865) observed that the introduction of more efficient steam engines in Victorian England did not reduce coal consumption — it increased it, because efficiency lowered the cost per unit of work, expanding the range of economically viable uses and the scale of deployment. The paradox has been documented repeatedly across energy history: fuel-efficient cars increase vehicle miles traveled; LED lighting increases total light-hours consumed; efficient home appliances are purchased in larger numbers.

Applied to AI: as models become more capable and cheaper to run, the range of tasks to which they are applied expands. A 10x efficiency improvement that is met with a 20x increase in use produces a net doubling of total consumption. There is no empirical reason to expect AI to be exempt from this pattern; there are strong economic incentives that push toward it.

**The Green AI movement** (Schwartz et al., 2019) proposed reporting efficiency metrics alongside accuracy: energy consumed per FLOP, accuracy per watt, CO$_2$ per benchmark point. The goal is to make efficiency visible in the research community's incentive structure rather than allowing capability benchmarks alone to drive architectural choices. Adoption has been partial.

---

## Model 3: Carbon Audit — One Student's AI Week

Sofia is a CS student working on a capstone project for one week. Her AI use includes: 120 chat queries for coding assistance (frontier model API); 15 image generations for a presentation; 3 hours of code-completion suggestions via IDE plugin (frontier model); 2 documents summarized via a web interface; and one fine-tuned local model running on her laptop for 4 hours to experiment with a custom classifier.

| Activity | Queries / Duration | Estimated CO$_2$eq | Notes |
|---|---|---|---|
| Chat coding queries (frontier API) | 120 queries | ~0.06 kg | ~0.5g per query estimate |
| Image generations | 15 images | ~0.045 kg | ~3g per generation |
| IDE code completion (frontier) | 3 hours continuous | ~0.03 kg | Estimate based on query rate |
| Document summarization (web) | 2 documents | ~0.001 kg | Lightweight inference |
| Local model experiment | 4 hours on laptop | ~0.035 kg | Grid electricity, no cooling overhead |

### Critical Thinking Questions

7. Sofia's week totals approximately 0.17 kg CO$_2$eq. Scaled to 10,000 students at a university using AI at similar rates, the weekly institutional footprint is approximately 1.7 tonnes. Contextualize this against the university's other energy expenditures (heating, lighting, transportation) and argue whether it is negligible, significant, or depends on what you count.
8. Apply Jevons paradox directly: if a future tool reduces Sofia's per-query cost by 80%, predict what happens to her total AI carbon footprint over a semester. What behavioral or policy intervention could prevent the paradox from operating?
9. The local model experiment used roughly the same carbon as the frontier cloud queries for much longer work. What does this suggest about the conditions under which local inference is genuinely lower-carbon, and when the comparison goes the other way?

---

# Part IV: Synthesis

## Exercises

1. *Personal carbon audit.* Estimate your own AI-related carbon footprint for the past week using the proportional reasoning tools from Model 1. Identify the single largest contributor and one specific substitution you could make with less than 5% reduction in the quality of your work.
2. *Right-sizing your project.* For your course project, evaluate whether the model you are using is right-sized for the task. If you are using a frontier API, identify a smaller model that could plausibly achieve adequate performance and outline the evaluation you would need to run to confirm it.
3. *Policy brief.* In 200 words, write a recommendation to a technology organization about one concrete policy change (scheduling, model selection, caching, disclosure, or another lever) that would reduce their AI carbon footprint. State what you would measure to confirm it worked and how you would guard against Jevons paradox undermining the gain.

---

## Reflection Prompt

In your notebook: Jevons paradox suggests that the engineers most committed to efficiency may be the ones who inadvertently drive the largest increases in total consumption, because they make expansion economically rational. Is there a version of your technical work — including the course project you are building — that fits this pattern? What would you need to believe about how it gets deployed to conclude that it reduces, rather than increases, aggregate environmental impact?

---

## Further Reading

- Patterson, D. et al. "Carbon Emissions and Large Neural Network Training." *arXiv* 2104.10350 (2021). The most cited quantitative analysis of training costs.
- Schwartz, R. et al. "Green AI." *Communications of the ACM* 63(12): 54–63 (2020). The case for efficiency metrics alongside accuracy.
- Strubell, E., Ganesh, A., and McCallum, A. "Energy and Policy Considerations for Deep Learning in NLP." *ACL* (2019). The paper that put training carbon costs on the NLP community's radar.
- Jevons, W.S. *The Coal Question.* Macmillan (1865), Chapter 7. Readable in excerpt; the original paradox argument is clearer than most secondary accounts.
