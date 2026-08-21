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

This half-session shares the day with the *Governance and Policy Writing* activity — the policies you draft there need numbers behind them, and today supplies the numbers. The discourse around AI rarely foregrounds what it costs the planet to run. Energy consumption, water usage, and embodied carbon in hardware are not edge considerations; at the scale of contemporary model training and inference, they are material. Today you develop the quantitative literacy to reason about these costs, the design vocabulary to reduce them, and the critical framework to resist the optimism that efficiency gains automatically reduce aggregate impact. The goal is not guilt but judgment: knowing when AI use is worth its cost and when a smaller or local tool would serve equally well.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Manager ensures the team works through the quantitative models rather than skimming them; the Recorder captures the team's carbon audit numbers and design decisions; the Presenter prepares to explain the Jevons paradox argument to the class; the Reflector watches for moments when the team's reasoning becomes motivated (defending AI use rather than evaluating it) and names it. After class, respond to the reflective prompt individually in your notebook.

---

### Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Training Carbon Cost** | The total greenhouse gas emissions produced by running the compute needed to train a large AI model from scratch, measured in kilograms or tonnes of CO$_2$ equivalent. | Training GPT-3 once is estimated to have produced roughly 500 tonnes of CO$_2$eq — similar to five car lifetimes of emissions. |
| **Inference Carbon Cost** | The emissions produced by running a trained model to answer user queries. Because inference happens billions of times, its total impact often exceeds the one-time training cost. | A single ChatGPT-style query is estimated to use about ten times the energy of a Google search; at hundreds of millions of queries per day, inference dominates. |
| **Embodied Carbon** | The greenhouse gas emissions produced by manufacturing the hardware (GPUs, servers, cables) that AI runs on — *before* the hardware is even switched on. | Embodied carbon may represent 50-80% of a data center's lifetime footprint for hardware-intensive workloads, but it is almost never included in AI carbon estimates. |
| **Model Right-Sizing** | Choosing the smallest model that achieves adequate accuracy for a specific task, rather than defaulting to the most capable (and most energy-intensive) model available. | Using a 7B-parameter local model to summarize documents instead of a 70B frontier API, when accuracy is comparable, reduces inference energy by roughly 10x. |
| **Jevons Paradox** | The historical observation that improvements in the efficiency of using a resource tend to increase total resource consumption rather than decrease it, because efficiency lowers cost per use and expands the range of economically viable applications. | Fuel-efficient cars led to more total driving; energy-efficient LEDs led to more total light-hours. The same dynamic may apply to more efficient AI models. |
| **Grid Carbon Intensity** | The amount of CO$_2$ emitted per unit of electricity in a given region at a given time, determined by the mix of energy sources (coal, gas, solar, wind, hydro, nuclear) on the local grid. | The same AI inference job run in Iceland (near-zero-carbon geothermal electricity) versus a coal-heavy region can differ by a factor of 50 in carbon impact. |

---

# Part I: Orders of Magnitude

In this Part, you will build a concrete, numerical sense of how much energy and carbon different AI workloads produce — from a single query to a full model training run. The goal is not guilt but judgment: once you know the proportions, you can make smarter choices about which tools to reach for.

## 1. What It Costs to Train and Infer

Most people who use AI daily have a rough sense that large models require a lot of computation, but almost no intuition for what that means in carbon terms. Developing that intuition — even approximately — is what allows you to make design decisions that are grounded in reality rather than either dismissiveness ("it's just electricity") or paralysis ("AI is destroying the planet"). The goal is proportional reasoning: knowing which choices matter and which are noise.

**Training** a large language model is a one-time but enormous energy expenditure. Estimates for GPT-3 (175B parameters) place training energy at approximately 1,287 MWh and carbon emissions at roughly 500 tonnes of CO$_2$ equivalent — comparable to the lifetime emissions of five average American cars or about 125 transatlantic flights. GPT-4-scale models are estimated to require substantially more, though developers do not publish precise figures. These numbers are order-of-magnitude estimates; the actual figure depends heavily on the regional carbon intensity — the grams of CO$_2$ emitted per kilowatt-hour of electricity generated, which swings from near-zero in Iceland's geothermal grid to several hundred grams in coal-heavy regions — of the electrical grid where training runs.

**Inference** at scale often exceeds training in total impact because it recurs with every query. A single ChatGPT prompt is estimated to consume roughly ten times the energy of a Google search. With hundreds of millions of queries per day, inference energy becomes the dominant term. Water usage compounds this: Microsoft reported in 2023 that its data centers consumed approximately 1.7 liters of water (for cooling) per 20-50 ChatGPT prompts. Water stress in regions hosting large data centers is a real externality, not a hypothetical one.

**Embodied carbon** — the emissions from manufacturing GPUs, servers, networking equipment, and undersea cables, *before* any of them are even switched on — is typically excluded from carbon accounting for AI systems. Estimates suggest embodied carbon may represent 50-80% of a data center's lifetime carbon footprint for hardware-intensive workloads. A GPU's fabrication at advanced process nodes involves energy-intensive lithography and chemical processes; the supply chain spans continents. Ignoring embodied carbon systematically understates the cost of "upgrading to a more efficient model."

---

## Model 1: Carbon Cost Comparison

Why this matters: every time you choose which model to use for a task — a frontier API versus a local quantized model versus a fine-tuned small model — you are making an environmental decision, whether or not you think of it that way. The table below gives you the proportional anchors to make that choice with some quantitative grounding rather than pure convenience. As you read it, look for the ratio between the smallest and largest entries — that span of nine orders of magnitude is the key intuition to carry into the design decisions in Part II.

| Action | Estimated CO$_2$ equivalent | Approximate real-world equivalent | Engineering implication |
|---|---|---|---|
| Training a GPT-3-scale model | ~500 tonnes | Lifetime emissions of ~5 American passenger cars | Training runs are high-stakes, one-time costs; fine-tuning existing models is far cheaper |
| Training a GPT-4-scale model | ~1,000-10,000 tonnes (estimated) | 250-2,500 transatlantic flights | Undisclosed costs from frontier labs mean independent accountability is not possible |
| 1 million ChatGPT-style queries | ~0.5 tonnes | Driving a gasoline car ~2,000 km | At scale, inference dominates; caching repeated queries is a significant lever |
| 1 AI image generation (diffusion model) | ~0.003 kg | Charging a smartphone once | Individually small, but frequency and user base scale this rapidly |
| 1 standard email (no attachment) | ~0.000004 kg | 1 second of a 60W light bulb | Baseline for comparison; AI queries are several thousand times more expensive |
| A laptop running for 8 hours | ~0.07 kg | 700 emails or ~23 AI image generations | Local inference shares the laptop's base consumption; no additional cooling overhead |
| 1 hour of video streaming | ~0.036 kg | Comparable to a laptop at moderate load | Streaming infrastructure is already at data-center scale; AI inference is an additional load |

*Note: All figures are order-of-magnitude estimates that vary by grid carbon intensity, hardware generation, and methodology. Treat them as rough anchors for proportional reasoning, not precise measurements.*

### Critical Thinking Questions

1. The table spans roughly nine orders of magnitude from a single email to GPT-4-scale training. Which comparison is most surprising to you, and why? What does the surprise reveal about your prior mental model of AI energy costs?

   *Hint: Before answering, make a prediction: rank the five most expensive items in the table from memory. Then check your ranking against the actual figures. The gap between your prediction and reality is exactly the mental model this question is probing.*

2. A company argues that switching from a 70B-parameter model to a 7B-parameter model for a customer service chatbot running 10 million queries per month has a larger carbon impact than switching its data center to renewable energy. Construct a rough quantitative argument for or against this claim using the proportional reasoning the table supports.

   *Hint: A 70B model uses roughly 10x the compute of a 7B model at inference. 10 million queries per month is roughly 330,000 queries per day. Use the per-query estimate from the table to compute monthly carbon for each model. Then compare to what "switching to renewable energy" would actually change — it changes the carbon intensity of the same electricity, not the amount used.*

3. "Embodied carbon" is excluded from most AI carbon footprints. Why might organizations have an incentive to exclude it? Name two design or procurement decisions that would reduce embodied carbon and explain why they are not standard practice.

   *Hint: Think about who controls what gets counted in a carbon report. Consider: if embodied carbon is excluded, what appears to happen to the carbon cost of "upgrading to a newer, more efficient GPU generation"? What are the economic incentives that push against hardware longevity and repairability?*

The central proportional insight of Model 1 is that:

[( )] Training is always the dominant carbon cost of a deployed model, so one-time training decisions matter most
[(X)] Inference, repeated millions or billions of times, often exceeds the one-time training cost in total impact
[( )] A single AI query and a single email have roughly comparable carbon costs
[( )] Embodied carbon is negligible compared to the electricity a model consumes

### Team Exercise: Estimate, Then Check

A campus helpdesk deploys a cloud chatbot that handles **3,000 queries per day, every day of a 30-day month**. Using only your intuition first — no arithmetic yet — each team writes down an estimate of the deployment's **monthly electricity use (in kWh)** and **monthly cooling-water use (in liters)**. The Recorder logs both estimates before anyone opens the worked numbers.

Then compute it properly from the figures in this Part: take a ChatGPT-style query at roughly **3 Wh** (about ten times a ~0.3 Wh web search) and cooling water at roughly **1.7 liters per 35 prompts** (the midpoint of the reported 20-50 prompt range). Compare against the worked numbers below.

<details>
<summary>Worked numbers (open only after both estimates are recorded)</summary>

- Queries per month: 3,000 × 30 = **90,000 queries**
- Electricity: 90,000 × 3 Wh = 270,000 Wh ≈ **270 kWh per month** (roughly a US household's electricity for about a week and a half)
- Water: (90,000 ÷ 35) × 1.7 L ≈ **4,400 liters per month** (about 29 full bathtubs)

</details>

Finally, each team identifies its **largest gap** — the quantity (energy or water) where the estimate missed by the biggest factor — and explains *why* the intuition was off: which anchor was missing, and which figure from Model 1 would have corrected it?

---

*Now that you have the proportional anchors from Part I, Part II translates them into practical design decisions: which model should you use, where should it run, and what engineering levers actually move the needle?*

# Part II: Right-Sizing and the Local-First Principle

In this Part, you will apply the numbers from Part I to concrete design choices — specifically, how to match the model you use to the actual difficulty of the task. This is the single highest-leverage skill for reducing AI environmental cost in your own work.

## 2. Choosing the Right Tool for the Task

The single most impactful design decision for reducing AI environmental cost is not caching, not scheduling, and not carbon offsets — it is choosing the right-sized model (the smallest model that does the job adequately) for the task in the first place. A frontier model applied to a task that a smaller model handles equally well is pure waste. But "right-sizing" is not something most developers learn as a skill, because it requires intentional evaluation rather than defaulting to the most capable available option.

**Model right-sizing** is the practice of matching model capability to task requirements. Using a 100B-parameter frontier model to classify whether an email is spam, when a fine-tuned 100M-parameter model achieves the same accuracy, is waste — in energy, latency, and cost. The principle sounds obvious but is routinely violated because frontier APIs are convenient, benchmarks reward capability, and the marginal cost of a larger model is invisible to the developer while the capability gain is visible.

**The local-first principle** holds that a model running on a user's device consumes no data center energy, produces no inference-time cloud emissions, and eliminates the water cost of remote cooling. For many tasks — summarization, code assistance, question answering on local documents — a 7B or 13B-parameter quantized model running on a consumer GPU or Apple Silicon chip is competitive with much larger cloud models. The choice of "local vs. cloud" is therefore not only a privacy decision but an environmental one.

**Caching and batching** are further levers: caching the responses to common queries eliminates redundant computation; batching multiple inference requests reduces per-query overhead. These are standard software engineering practices applied to an unusually energy-visible workload.

**Grid carbon intensity** varies dramatically by region and time of day. The same computation performed in Iceland (near-zero-carbon geothermal grid) versus coal-heavy regions can differ by a factor of 50 or more in carbon impact. Schedulable workloads (batch inference, retraining runs) can be routed to lower-carbon regions or shifted to hours when renewable supply peaks. This is operationally feasible; it is not widely practiced.

---


> **Right-sizing, in detail.** The full decision matrix for matching a model's size to a task lives in the optional activity [Cost Optimization](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-costoptimization.md). The principle for today: the smallest model that passes your golden set is the right one, on carbon as on cost.

# Part III: Jevons Paradox and Systemic Risk

## 3. Why Efficiency Gains May Not Reduce Impact

Individual-level good decisions (use a smaller model, cache more queries, choose renewable energy) can add up to a collective outcome that is worse than if no one had tried to be efficient. This counterintuitive result — efficiency enables expansion — is one of the most important structural patterns in the history of technology, and there is no strong reason to expect AI to be exempt from it. The goal of this section is not pessimism but accurate forecasting: knowing that the paradox exists allows you to design interventions that guard against it.

**Jevons paradox** (William Stanley Jevons, 1865) observed that the introduction of more efficient steam engines in Victorian England did not reduce coal consumption — it increased it, because efficiency lowered the cost per unit of work, expanding the range of economically viable uses and the scale of deployment. The paradox is named after economist William Stanley Jevons, who documented it in *The Coal Question* (1865). It has been documented repeatedly across energy history: fuel-efficient cars increase vehicle miles traveled; LED lighting increases total light-hours consumed; efficient home appliances are purchased in larger numbers.

Applied to AI: as models become more capable and cheaper to run, the range of tasks to which they are applied expands. A 10x efficiency improvement that is met with a 20x increase in use produces a net doubling of total consumption. There is no empirical reason to expect AI to be exempt from this pattern; there are strong economic incentives that push toward it.

**The Green AI movement** (Schwartz et al., 2019) proposed reporting efficiency metrics alongside accuracy: energy consumed per FLOP, accuracy per watt, CO$_2$ per benchmark point. The goal is to make efficiency visible in the research community's incentive structure rather than allowing capability benchmarks alone to drive architectural choices. Adoption has been partial.

---

## Model 3: Carbon Audit — One Student's AI Week

Sofia is a CS student working on a capstone project for one week. Her AI use includes: 120 chat queries for coding assistance (frontier model API); 15 image generations for a presentation; 3 hours of code-completion suggestions via IDE plugin (frontier model); 2 documents summarized via a web interface; and one fine-tuned local model running on her laptop for 4 hours to experiment with a custom classifier.

| Activity | Queries or Duration | Estimated CO$_2$eq | Notes on the Estimate |
|---|---|---|---|
| Chat coding queries via frontier API | 120 queries | ~0.06 kg | Using ~0.5g per query as the working estimate; varies by model and grid |
| Image generations via cloud diffusion model | 15 images | ~0.045 kg | Using ~3g per generation; diffusion models are more compute-intensive per output than text |
| IDE code completion via frontier model | 3 hours continuous | ~0.03 kg | Estimate based on typical autocomplete query rate; continuous use adds up quickly |
| Document summarization via web interface | 2 documents | ~0.001 kg | Lightweight inference for short summarization tasks; cloud overhead dominates |
| Local model experiment on laptop | 4 hours of local inference | ~0.035 kg | Grid electricity cost with no data center cooling overhead; comparable to frontier API queries |

### Critical Thinking Questions

7. Sofia's week totals approximately 0.17 kg CO$_2$eq. Scaled to 10,000 students at a university using AI at similar rates, the weekly institutional footprint is approximately 1.7 tonnes. Contextualize this against the university's other energy expenditures (heating, lighting, transportation) and argue whether it is negligible, significant, or depends on what you count.

   *Hint: A university's total annual carbon footprint is typically in the thousands to tens of thousands of tonnes. 1.7 tonnes per week scales to ~85 tonnes per year just from student AI use. Is that significant? Compare to the carbon cost of one transatlantic flight, one heated building for a semester, or the embodied carbon of a new server rack.*

8. Apply Jevons paradox directly: if a future tool reduces Sofia's per-query cost by 80%, predict what happens to her total AI carbon footprint over a semester. What behavioral or policy intervention could prevent the paradox from operating?

   *Hint: An 80% cost reduction means the same task now costs 1/5 as much. If Sofia currently self-limits her AI use based partly on cost (conscious or not), what happens when that constraint is removed? What would "usage caps," "carbon budgets," or "efficiency labels" look like as policy interventions? Would any of them work?*

9. The local model experiment used roughly the same carbon as the frontier cloud queries for much longer work. What does this suggest about the conditions under which local inference is genuinely lower-carbon, and when the comparison goes the other way?

   *Hint: The local model ran for 4 hours; the frontier queries took much less time. What drove the local cost? Now imagine Sofia ran the same experiment but used 10x more cloud queries. Which direction does the comparison shift? What variables determine the crossover point?*

> **Common Misconception:** "Switching to renewable energy at the data center makes AI carbon-neutral." Renewable energy purchases do not eliminate energy consumption — they offset it with generation elsewhere on the grid. The actual energy demand, water use for cooling, and embodied carbon in hardware remain unchanged. "100% renewable" cloud providers are making a true but partial claim: they are purchasing renewable energy credits, which is better than not doing so, but it is not the same as using zero carbon. Meaningful carbon reduction requires reducing the energy consumption itself, not only changing its source on paper.

According to Jevons paradox, a 10x improvement in model inference efficiency will most likely:

[( )] Reduce total AI energy consumption by roughly 10x
[( )] Leave total consumption unchanged, because usage patterns are fixed
[(X)] Lower the cost per use and expand the range of viable uses, potentially increasing total consumption
[( )] Affect training costs only, since inference is already efficient

---

# Part IV: Synthesis

In this Part, you will apply the proportional reasoning, design vocabulary, and systemic thinking from Parts I–III to your own project and practice context. The goal is to leave with a concrete number, a specific substitution proposal, and a policy recommendation you could actually hand to an engineering team.

## Exercises

1. *Personal carbon audit.*

   *What to do:* Estimate your own AI-related carbon footprint for the past week using the proportional reasoning tools from Model 1. Identify the single largest contributor and one specific substitution you could make with less than 5% reduction in the quality of your work.

   *Starter hint:* List every AI tool you used in the past week (chatbots, image generators, code assistants, voice assistants). Estimate the number of queries for each. Use the per-query figures from Model 1 to calculate totals. The largest contributor is your highest-volume, highest-cost-per-query combination. For the substitution, ask: could a local model or a smaller API model have handled that use case? What would you lose?

   *You've succeeded when:* You have a specific number (in grams of CO$_2$eq) for your weekly AI footprint, a clear identification of the dominant source, and a substitution proposal with an estimate of the accuracy or convenience trade-off.

2. *Right-sizing your project.*

   *What to do:* For your course project, evaluate whether the model you are using is right-sized for the task. If you are using a frontier API, identify a smaller model that could plausibly achieve adequate performance and outline the evaluation you would need to run to confirm it.

   *Starter hint:* Identify the specific subtask in your pipeline that uses the most compute (usually the largest model call). Look at the output quality requirements for that task. Research whether a 7B or 13B model has been benchmarked on similar tasks. Outline: what 10 test cases would you use to compare the models, what metric would you use, and what accuracy threshold would be "good enough"?

   *You've succeeded when:* You can name a specific smaller model, describe the evaluation protocol that would confirm its adequacy, and estimate the carbon reduction (as a fraction of current inference cost) if you switched.

3. *Policy brief.*

   *What to do:* In 200 words, write a recommendation to a technology organization about one concrete policy change (scheduling, model selection, caching, disclosure, or another lever) that would reduce their AI carbon footprint. State what you would measure to confirm it worked and how you would guard against Jevons paradox undermining the gain.

   *Starter hint:* Choose a specific lever from this activity (e.g., "route all batch inference jobs to off-peak hours when renewable supply peaks on the regional grid"). State the expected reduction mechanism, the metric you would track (e.g., kg CO$_2$eq per 1,000 queries), the monitoring period, and the behavioral or policy guardrail that prevents increased usage from consuming the savings.

   *You've succeeded when:* Your brief could be handed to an engineering team and turned into a concrete project: it names the intervention, the measurement, the timeline, and the anti-Jevons safeguard.

---

## Reflection Prompt

Record your responses to all three levels in your reflection:

*Personal:* Look at your personal carbon audit results. Did the numbers change how you feel about your own AI use this semester — or did you find yourself rationalizing the usage you already had? Either answer is informative. What would it take for the numbers to actually change your behavior?

*Technical:* Jevons paradox suggests that the engineers most committed to efficiency may be the ones who inadvertently drive the largest increases in total consumption, because they make expansion economically rational. Is there a version of your course project that fits this pattern? What would you need to believe about how it gets deployed to conclude that it reduces, rather than increases, aggregate environmental impact?

*Societal:* The organizations best positioned to reduce AI's environmental impact (large cloud providers, frontier model developers) are the same organizations with the strongest financial incentives to increase AI use. What governance mechanisms — regulatory, market-based, or professional — could align those incentives with aggregate carbon reduction? Is there a precedent from another industry that suggests such mechanisms can work?

> *Hint:* Consider the history of automotive fuel-economy standards (CAFE standards in the US): automakers resisted, lobbied, and then ultimately innovated when the regulation held. Ask: what would the AI equivalent look like — mandatory energy-per-inference disclosure, a carbon cost embedded in API pricing, or an industry reporting standard? Which of those is most likely to survive political and market pressure, and which is most likely to trigger a Jevons rebound?

---

## → Coming Up Next

The *Explainability and Human-Centric Design* activity is next: how systems earn justified trust from the humans who use them. The carbon analysis you practiced today feeds directly into Written Assignment 3's Direction E, where you quantify and defend the environmental posture of a deployment.

## Further Reading

- Patterson, D. et al. "Carbon Emissions and Large Neural Network Training." *arXiv* 2104.10350 (2021). The most cited quantitative analysis of training costs.
- Schwartz, R. et al. "Green AI." *Communications of the ACM* 63(12): 54-63 (2020). The case for efficiency metrics alongside accuracy.
- Strubell, E., Ganesh, A., and McCallum, A. "Energy and Policy Considerations for Deep Learning in NLP." *ACL* (2019). The paper that put training carbon costs on the NLP community's radar.
- Jevons, W.S. *The Coal Question.* Macmillan (1865), Chapter 7. Readable in excerpt; the original paradox argument is clearer than most secondary accounts.
