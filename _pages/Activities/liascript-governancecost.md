<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-governancecost.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-governancecost.md

import: https://raw.githubusercontent.com/LiaTemplates/Pyodide/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Governance, Policy, and the Cost of Inference

A policy section is only as good as the mechanism that enforces it.  You have built agents that retrieve, decide, judge, and act; governance is deciding in advance, in writing, what they may do, who answers when they err, and how anyone would know.  Today you learn to write policy that a stranger could check from the logs, and you put numbers behind the section most policies leave out: what the system costs to run, in energy, water, dollars, and tokens.  You leave with two enforceable sections of your final project's governance one-pager, one about data and one about cost and routing.

Due today: the Multi-Agent Patterns lab ([Multi-Agent Debate](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate)).

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Today ends in a drafting workshop with structured peer review.  The Manager keeps the team working the numbers in Part II rather than skimming them; the Recorder types the two policy sections and logs the team's estimates before anyone opens the worked answers; the Presenter prepares to explain one mechanism the team could not make concrete; the Reflector watches for moments when the team defends its AI use instead of evaluating it, and names them.  After class, answer the reflection prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Governance** | The set of written rules, structures, and processes that decide what an AI system may do, who is accountable for its behavior, and how problems are detected and fixed, before harm occurs. | A university's policy stating that an AI advising tool may suggest course plans but may not register students for classes is a governance document. |
| **Third-Party Test** | A practical check for whether a policy clause is real: could an independent outside party examine evidence and determine whether the clause was actually followed? If not, the clause is decoration, not policy. | "We will be fair" fails the test. "Every Friday the evaluation harness runs 40 tasks and any group accuracy gap above 5 points opens an incident" passes the test. |
| **NIST AI RMF** | The National Institute of Standards and Technology AI Risk Management Framework, a voluntary US guideline that organizes AI risk work into four functions: Govern, Map, Measure, and Manage. | A team completing a pre-mortem (Map), running disaggregated evaluations (Measure), and assigning a named project owner (Govern) is implementing the NIST framework. |
| **EU AI Act** | A 2024 European Union law that classifies AI systems by risk level and imposes different obligations depending on how much harm a system could cause, from bans on the most dangerous uses to transparency requirements for lower-risk ones. | An AI system used in college admissions falls in the Act's "high-risk" category and requires detailed documentation, human oversight, and accuracy testing. |
| **Incident Response** | A documented procedure specifying exactly what steps are taken, by whom, and on what timeline when an AI system produces a harmful or unexpected output. | "Within 24 hours of a user harm report, the project owner disables the tool and opens a tracked issue; within 5 business days a root-cause analysis is posted" is an incident response process. |
| **Sunset Clause** | A provision in a policy that specifies when the policy must be revisited or when the system must be retired if conditions change, preventing outdated rules from governing a changed system indefinitely. | "This policy expires 12 months after deployment and must be renewed following a new impact assessment" is a sunset clause. |
| **Inference Carbon Cost** | The emissions produced by running a trained model to answer user queries. Because inference happens billions of times, its total impact often exceeds the one-time training cost. | A single ChatGPT-style query is estimated to use about ten times the energy of a Google search; at hundreds of millions of queries per day, inference dominates. |
| **Embodied Carbon** | The greenhouse gas emissions produced by manufacturing the hardware (GPUs, servers, cables) that AI runs on, *before* the hardware is even switched on. | Embodied carbon may represent 50-80% of a data center's lifetime footprint for hardware-intensive workloads, but it is almost never included in AI carbon estimates. |
| **Model Right-Sizing** | Choosing the smallest model that achieves adequate accuracy for a specific task, rather than defaulting to the most capable (and most energy-intensive) model available. | Using a 7B-parameter local model to summarize documents instead of a 70B frontier API, when accuracy is comparable, reduces inference energy by roughly 10x. |
| **Jevons Paradox** | The historical observation that improvements in the efficiency of using a resource tend to increase total resource consumption rather than decrease it, because efficiency lowers cost per use and expands the range of economically viable applications. | Fuel-efficient cars led to more total driving; energy-efficient LEDs led to more total light-hours. The same dynamic may apply to more efficient AI models. |
| **Thinking tokens** | The intermediate stream a reasoning model emits before answering. Billed and burned as *output* tokens, the expensive kind, so extended thinking can multiply the cost of an unchanged reply many times over. | The 21x row in Section 7, where the user sees the same 150-word answer. |

---

### Before You Start

Bring your project's pre-mortem and data-flow audit.  They are the raw material for the two sections you draft in Part III, and Model 2 asks you to map them onto the NIST functions.  Nothing needs installing today; the one code cell runs in the browser.

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Part I, from values to mechanisms: the third-party test and Model 1 |
| 10-25 | Part I, the eight sections, frameworks meet your project, and safety controls in one page |
| 25-50 | Part II, the cost of inference: orders of magnitude, estimate then check, Jevons, and what you can do about it |
| 50-70 | Part III, the drafting workshop: write two sections, then trade them |
| 70-75 | Report out one mechanism you could not make concrete |

---

# Part I: From Values to Mechanisms

In this part you learn to tell policy language that sounds good from policy language that commits someone to a specific, checkable action.  Everything else today builds on that distinction.

## 1.  Governance Is Engineering with Words

A value is not a policy.  "Our agent is fair and transparent" commits no one to anything.  A policy converts values into *mechanisms*: scopes, prohibitions, gates, logs, owners, and remedies.  Think of it the way you think about tests for code: "the function should work correctly" is useless, while "given input X, output Y is returned within 200ms" is enforceable.  The test of a policy clause is the same: could a third party determine, from evidence, whether it was followed?  Every clause that fails that test is decoration.

Mature frameworks classify uses by risk and scale obligations to match.  The **EU AI Act** (a 2024 European law regulating AI systems by the potential harm they could cause) bans a small set of practices, imposes heavy obligations (documentation, human oversight, accuracy reporting) on "high-risk" systems such as those used in education admissions and grading, and lighter transparency duties elsewhere.  The NIST AI Risk Management Framework (a voluntary US guideline) organizes the work as four functions: *Govern* (assign accountability), *Map* (know your system and context), *Measure* (evaluate, disaggregate, monitor), and *Manage* (mitigate, respond, document).  Notice how much of NIST's *Measure* you can already execute: harnesses, disaggregated metrics, judge audits, citation checks.

Accountability has names in it.  Policies designate an owner per system, an escalation path, and an incident process.  "The team is responsible" means no one is.

---

## Model 1: Toothless Versus Enforceable

When you build a real AI system, even a class project, someone will eventually ask who is accountable if it produces a harmful output.  Clauses that survive the third-party test let you answer with documentation rather than apologies.

Clause A: "The advising agent should be used responsibly and its suggestions taken with appropriate caution."

Clause B: "The advising agent may draft degree-plan suggestions but may not submit registrations.  Every suggestion shown to a student must display the data sources used.  The CS department chair owns this system; suspected errors are reported via the form at [link] and acknowledged within 5 business days.  Logs of all suggestions are retained for one semester and audited each January against the disaggregation protocol in Appendix B."

### Critical Thinking Questions

1.  Before you discuss, each person predicts how many sentences in Clause B pass the **third-party test** (could an independent outside party examine evidence and determine whether this clause was followed, without asking anyone what it means?).  Then apply the test to each sentence of both clauses.  Which sentences are checkable from evidence, and which are not?

   *Hint: For each sentence, ask: if I gave this sentence to an outside auditor along with all of the system's logs, could they determine with certainty whether the clause was followed or violated?  If the answer requires judgment about what "responsible" means, the clause fails the test.*

2.  Identify in Clause B the scope, the prohibition, the transparency duty, the owner, the remedy, and the audit.  Which single element, if deleted, most weakens the rest?

   *Hint: Try removing each element one at a time and ask what breaks.  If there is no owner, who fixes problems?  If there is no audit, how does anyone know if the transparency duty is being met?  If there is no remedy, what incentivizes compliance?*

3.  Under the EU AI Act's logic, why would an advising agent that *recommends* differ in risk tier from one that *registers*?  Connect to the irreversible-action taxonomy you built in the tool-use module.

   *Hint: Think about what a student can do after a bad recommendation versus after a bad registration.  Can they undo it?  How much does it cost to fix?  How quickly must it be fixed to avoid serious harm?*

---

## 2.  The Eight Sections

A governance document is an engineering artifact: it specifies what your system does, who is accountable for it, and what happens when things go wrong.  If you cannot fill a section, that gap is itself a finding: something about your system is unspecified.

Your governance one-pager for the final project uses this skeleton, each section earning its place by the third-party test:

1.  **Purpose and scope**: what the system does, for whom, and explicitly what is out of scope.
2.  **System description**: agents, models, tools, data flows (your design table and audit, imported).
3.  **Permitted and prohibited uses**: concrete, with the prohibition list as specific as the permission list.
4.  **Human oversight**: which actions require confirmation, who confirms, and what the human sees before deciding.
5.  **Data handling**: what is collected, where it lives, how long it is retained, and which regulated categories it touches (FERPA, IRB).
6.  **Evaluation and monitoring**: metrics, disaggregation plan, audit schedule, and the harness that produces the data.
7.  **Accountability and incident response**: the owner by name or role, the reporting path, and response timelines measured in hours or days.
8.  **Review and sunset**: when the policy is re-examined and the conditions under which the system is retired.

Notice what the list does not have: a section on what the system costs to run.  Part II supplies the numbers for one, and Part III has you write it, because a policy that governs an agent's behavior and says nothing about its footprint is incomplete.

A team writes: "Section 6: We will continuously evaluate the system for quality and bias."  The revision that survives the third-party test is:

[( )] "We will evaluate rigorously and transparently using best-practice methods."
[( )] "Evaluation is a core value of our team and we take it seriously."
[(X)] "Each Friday the harness in /eval runs the 40-item task set; per-group accuracy and judge-human agreement are posted to the repository; any group gap exceeding 5 points opens an incident."
[( )] "Users are encouraged to report problems and we will respond appropriately."

---

## Model 2: Frameworks Meet Your Project

Your pre-mortem and data-flow audit are the artifact to read here.  Lay them next to the NIST functions and the eight sections and find what is already written and what is missing.

### Critical Thinking Questions

4.  Map your project onto NIST's four functions: for each of Govern, Map, Measure, and Manage, name the artifact you have already produced this semester that does that work, and the one artifact still missing.

   > *Hint:* Govern = who owns this and what are they accountable for?  Map = what does the system do and who is affected?  Measure = how do you know if it's working or failing?  Manage = what do you do when something goes wrong?  Match each function to something you have actually built, written, or run this semester: your rubric pipeline, your pre-mortem, your data flow diagram, your test harness all count.

5.  Would your project be "high-risk" under the EU AI Act's education provisions if deployed for real students rather than a class demo?  What single design change most reduces its tier?

   *Hint: The EU AI Act's Annex III lists education systems that "determine access to, assignment to, or advancement of persons in educational institutions."  Does your system make, recommend, or inform any of those decisions?  If so, what would you remove or add to change that?*

6.  Your pre-mortem predicted a specification gap, an irreversible action, and a global invariant.  Write the policy clause (one sentence each) that addresses each prediction.

   *Hint: A specification-gap clause should say what happens when the agent encounters a request it was not designed to handle.  An irreversible-action clause should name the action, require human confirmation, and name the confirming party.  A global-invariant clause should specify what the system must always do (or never do) regardless of user instruction.*

> **Common Misconception:** "Governance is something we add after the system works."  Many teams treat governance documentation as a final step before submission, something to write once the code is done.  In practice, writing a governance document *first* surfaces design requirements you would otherwise miss: who is accountable forces you to define ownership; what is prohibited forces you to define scope; how you audit forces you to build the logging infrastructure.  Teams that write governance last typically discover they built an unsupervised, unauditable system.

---

## 3.  Alignment and Safety Controls in One Page

You cannot write credible policy about a system whose control mechanisms you cannot name, so here is the short version.  Today's models got their behavior from two training methods.  Reinforcement Learning from Human Feedback (RLHF) collects human preference labels between pairs of responses, trains a reward model to predict those preferences, and fine-tunes the model to score well on it.  Annotator biases become model biases, and the model can learn to game the reward: raters preferred confident-sounding answers, so the model learned to sound confident even when wrong.  Constitutional AI (CAI) replaces most of that labeling with a written set of principles the model critiques its own outputs against.  The constitution is readable and auditable, but whoever writes it decides whose values are encoded.  Neither method removes human judgment; RLHF hides it in thousands of unrecorded annotator choices and CAI moves it into a document.

The consequence for your policy: training gives you the model's intent, not its enforcement.  Enforcement comes from controls you add around the model, and they stack, like physical security at a building: a sign on the door is easy but weak, a lock is stronger, a guard stronger still, a vault with dual keys strongest.

| Control | Implementation Cost | Bypass Difficulty | What It Covers | Example |
|---|---|---|---|---|
| **System prompt constraints** | Very low: add text to the system prompt | Low: prompt injection or roleplay framing can bypass it | Broad but weak; sets the intent without enforcing it mechanically | "Do not share other students' data or grades with anyone" |
| **Output filtering** | Low: a regex or classifier runs on every response before it reaches the user | Medium: requires knowing what patterns to block; misses novel attacks | Specific patterns that can be described precisely, like PII or profanity | Block any output matching a social security number regex pattern |
| **Input filtering** | Low-medium: a classifier screens user messages before they reach the model | Medium: known attack patterns are blocked; novel ones slip through | Known attack patterns like prompt injection markers | Reject any message containing "ignore previous instructions" |
| **Sandboxed execution** | High: requires container orchestration and security engineering | High: the agent literally cannot affect things outside the sandbox | Code and tool misuse that could affect external systems | Run all agent-invoked Python code in an isolated container with no network access |
| **Human review queue** | Very high: requires staffing and workflow design | Near-impossible: a human sees the output before it reaches the user | All high-risk outputs; highest coverage, highest cost | Route any query containing mental health keywords to a counselor before responding |

These controls are complementary, not alternatives; a production system layers several (defense in depth).  For your one-pager, the rule is simple: a clause that relies only on a system-prompt sentence fails the third-party test, because nothing checks it.  Name the control that does.

---

# Part II: The Cost of Inference

The eight sections govern what an agent may do.  This part is about something they have to govern too: what it costs to run, in energy, water, dollars, and tokens.  You build a numerical sense of those costs, from a single query to a training run, so the section you write in Part III has numbers behind it.  The goal is not guilt but judgment: knowing when AI use is worth its cost and when a smaller or local tool would serve as well.

## 4.  Orders of Magnitude

Most people who use AI daily know that large models need a lot of computation and have no intuition for what that means in carbon.  Rough proportions are enough to ground design decisions in something other than dismissiveness ("it's just electricity") or paralysis ("AI is destroying the planet").  The skill is proportional reasoning: knowing which choices matter and which are noise.

**Training** a large language model is a one-time but enormous expenditure.  Estimates for GPT-3 (175B parameters) place training energy at approximately 1,287 MWh and carbon emissions at roughly 500 tonnes of CO$_2$ equivalent, comparable to the lifetime emissions of five average American cars or about 125 transatlantic flights.  GPT-4-scale models need substantially more, though developers do not publish precise figures.  The actual figure depends heavily on the grid carbon intensity (the grams of CO$_2$ emitted per kilowatt-hour, which swings from near-zero on Iceland's geothermal grid to several hundred grams in coal-heavy regions) where training runs.

Inference at scale often exceeds training in total impact because it recurs with every query.  A single ChatGPT prompt is estimated to consume roughly ten times the energy of a Google search; with hundreds of millions of queries per day, inference becomes the dominant term.  Water compounds this: Microsoft reported in 2023 that its data centers consumed approximately 1.7 liters of cooling water per 20-50 ChatGPT prompts.  Water stress in regions hosting large data centers is a real externality.

Embodied carbon (the emissions from manufacturing GPUs, servers, networking equipment, and undersea cables, before any of them are switched on) is usually excluded from AI carbon accounting.  Estimates put it at 50-80% of a data center's lifetime footprint for hardware-intensive workloads.  Ignoring it systematically understates the cost of "upgrading to a more efficient model."

---

## Model 3: Carbon Cost Comparison

Every time you choose which model to use for a task (a frontier API, a local quantized model, a fine-tuned small model) you make an environmental decision, whether or not you think of it that way.  The table gives you proportional anchors for that choice.  As you read it, look for the ratio between the smallest and largest entries; that span of nine orders of magnitude is the intuition to carry into Section 5.

| Action | Estimated CO$_2$ equivalent | Approximate real-world equivalent | Engineering implication |
|---|---|---|---|
| Training a GPT-3-scale model | ~500 tonnes | Lifetime emissions of ~5 American passenger cars | Training runs are high-stakes, one-time costs; fine-tuning existing models is far cheaper |
| Training a GPT-4-scale model | ~1,000-10,000 tonnes (estimated) | 250-2,500 transatlantic flights | Undisclosed costs from frontier labs mean independent accountability is not possible |
| 1 million ChatGPT-style queries | ~0.5 tonnes | Driving a gasoline car ~2,000 km | At scale, inference dominates; caching repeated queries is a significant lever |
| 1 AI image generation (diffusion model) | ~0.003 kg | Charging a smartphone once | Individually small, but frequency and user base scale this rapidly |
| 1 standard email (no attachment) | ~0.000004 kg | 1 second of a 60W light bulb | Baseline for comparison; AI queries are several thousand times more expensive |
| A laptop running for 8 hours | ~0.07 kg | 700 emails or ~23 AI image generations | Local inference shares the laptop's base consumption; no additional cooling overhead |
| 1 hour of video streaming | ~0.036 kg | Comparable to a laptop at moderate load | Streaming infrastructure is already at data-center scale; AI inference is an additional load |

*Note: All figures are order-of-magnitude estimates that vary by grid carbon intensity, hardware generation, and methodology.  Treat them as rough anchors for proportional reasoning, not precise measurements.*

### Critical Thinking Questions

7.  Before reading the table closely, rank the five most expensive items from memory.  Then check your ranking against the figures.  Which comparison surprised you most, and what does the surprise reveal about your prior mental model of AI energy costs?

   *Hint: The gap between your prediction and reality is exactly the mental model this question is probing.*

8.  A company argues that switching from a 70B-parameter model to a 7B-parameter model for a customer service chatbot running 10 million queries per month has a larger carbon impact than switching its data center to renewable energy.  Construct a rough quantitative argument for or against this claim using the proportional reasoning the table supports.

   *Hint: A 70B model uses roughly 10x the compute of a 7B model at inference. 10 million queries per month is roughly 330,000 queries per day.  Use the per-query estimate from the table to compute monthly carbon for each model.  Then compare to what "switching to renewable energy" would actually change; it changes the carbon intensity of the same electricity, not the amount used.*

9.  "Embodied carbon" is excluded from most AI carbon footprints.  Why might organizations have an incentive to exclude it?  Name two design or procurement decisions that would reduce embodied carbon and explain why they are not standard practice.

   *Hint: Think about who controls what gets counted in a carbon report.  Consider: if embodied carbon is excluded, what appears to happen to the carbon cost of "upgrading to a newer, more efficient GPU generation"?  What are the economic incentives that push against hardware longevity and repairability?*

The central proportional insight of Model 3 is that:

[( )] Training is always the dominant carbon cost of a deployed model, so one-time training decisions matter most
[(X)] Inference, repeated millions or billions of times, often exceeds the one-time training cost in total impact
[( )] A single AI query and a single email have roughly comparable carbon costs
[( )] Embodied carbon is negligible compared to the electricity a model consumes

### Team Exercise: Estimate, Then Check

A campus helpdesk deploys a cloud chatbot that handles **3,000 queries per day, every day of a 30-day month**.  Using only your intuition first (no arithmetic yet) each team writes down an estimate of the deployment's monthly electricity use (in kWh) and monthly cooling-water use (in liters).  The Recorder logs both estimates before anyone opens the worked numbers.

Then compute it properly from the figures in this Part: take a ChatGPT-style query at roughly 3 Wh (about ten times a ~0.3 Wh web search) and cooling water at roughly 1.7 liters per 35 prompts (the midpoint of the reported 20-50 prompt range).  Compare against the worked numbers below.

<details>
<summary>Worked numbers (open only after both estimates are recorded)</summary>

- Queries per month: 3,000 × 30 = **90,000 queries**
- Electricity: 90,000 × 3 Wh = 270,000 Wh ≈ **270 kWh per month** (roughly a US household's electricity for about a week and a half)
- Water: (90,000 ÷ 35) × 1.7 L ≈ **4,400 liters per month** (about 29 full bathtubs)

</details>

Finally, each team identifies its largest gap, the quantity (energy or water) where the estimate missed by the biggest factor, and explains *why* the intuition was off: which anchor was missing, and which figure from Model 3 would have corrected it?

---

## 5.  Right-Sizing and the Local-First Principle

The design decision that most reduces AI environmental cost is not caching, scheduling, or offsets.  It is choosing the smallest model that does the job adequately in the first place.  A frontier model applied to a task a smaller model handles equally well is waste in energy, latency, and cost.  Most developers never learn right-sizing as a skill, because it requires deliberate evaluation rather than defaulting to the most capable option.

**Model right-sizing** matches model capability to task requirements.  Using a 100B-parameter frontier model to classify whether an email is spam, when a fine-tuned 100M-parameter model reaches the same accuracy, is waste.  The principle sounds obvious and is routinely violated: frontier APIs are convenient, benchmarks reward capability, and the marginal cost of a larger model is invisible to the developer while the capability gain is visible.

The local-first principle holds that a model running on a user's device consumes no data center energy, produces no inference-time cloud emissions, and eliminates the water cost of remote cooling.  For many tasks (summarization, code assistance, question answering on local documents) a 7B or 13B-parameter quantized model on a consumer GPU or Apple Silicon chip competes with much larger cloud models.  "Local vs. cloud" is therefore an environmental decision as well as a privacy one.

Grid carbon intensity varies by region and time of day.  The same computation in Iceland versus a coal-heavy region can differ by a factor of 50 or more in carbon impact.  Schedulable workloads (batch inference, retraining runs) can be routed to lower-carbon regions or shifted to hours when renewable supply peaks.  This is feasible and rarely practiced.  The principle for your policy: the smallest model that passes your golden set is the right one, on carbon as on cost.

---

## 6.  Jevons Paradox: Why Efficiency Gains May Not Reduce Impact

Individually good decisions (use a smaller model, cache more queries, choose renewable energy) can add up to a collective outcome worse than if no one had tried to be efficient.  Efficiency enables expansion.  This is one of the most durable structural patterns in the history of technology, and there is no strong reason to expect AI to be exempt.  Knowing the paradox exists lets you design interventions that guard against it.

**Jevons paradox** is named for economist William Stanley Jevons, who documented in *The Coal Question* (1865) that more efficient steam engines in Victorian England did not reduce coal consumption; they increased it, because efficiency lowered the cost per unit of work, expanding the range of economically viable uses and the scale of deployment.  The pattern recurs across energy history: fuel-efficient cars increase vehicle miles traveled; LED lighting increases total light-hours consumed; efficient appliances are bought in larger numbers.

Applied to AI: as models become more capable and cheaper to run, the range of tasks they are applied to expands.  A 10x efficiency improvement met with a 20x increase in use produces a net doubling of total consumption.  There are strong economic incentives that push toward exactly this.

The Green AI movement (Schwartz et al., 2019) proposed reporting efficiency metrics alongside accuracy: energy per FLOP, accuracy per watt, CO$_2$ per benchmark point, so that efficiency is visible in the research community's incentive structure.  Adoption has been partial.

---

## Model 4: Carbon Audit, One Student's AI Week

Sofia is a CS student working on a capstone project for one week.  Her AI use includes: 120 chat queries for coding assistance (frontier model API); 15 image generations for a presentation; 3 hours of code-completion suggestions via IDE plugin (frontier model); 2 documents summarized via a web interface; and one fine-tuned local model running on her laptop for 4 hours to experiment with a custom classifier.

| Activity | Queries or Duration | Estimated CO$_2$eq | Notes on the Estimate |
|---|---|---|---|
| Chat coding queries via frontier API | 120 queries | ~0.06 kg | Using ~0.5g per query as the working estimate; varies by model and grid |
| Image generations via cloud diffusion model | 15 images | ~0.045 kg | Using ~3g per generation; diffusion models are more compute-intensive per output than text |
| IDE code completion via frontier model | 3 hours continuous | ~0.03 kg | Estimate based on typical autocomplete query rate; continuous use adds up quickly |
| Document summarization via web interface | 2 documents | ~0.001 kg | Lightweight inference for short summarization tasks; cloud overhead dominates |
| Local model experiment on laptop | 4 hours of local inference | ~0.035 kg | Grid electricity cost with no data center cooling overhead; comparable to frontier API queries |

### Critical Thinking Questions

10.  Before you total the table, predict which row is largest and which is smallest.  Sofia's week totals approximately 0.17 kg CO$_2$eq.  Scaled to 10,000 students at a university using AI at similar rates, the weekly institutional footprint is approximately 1.7 tonnes.  Set this against the university's other energy expenditures (heating, lighting, transportation) and argue whether it is negligible, significant, or depends on what you count.

   *Hint: A university's total annual carbon footprint is typically in the thousands to tens of thousands of tonnes. 1.7 tonnes per week scales to ~85 tonnes per year just from student AI use.  Is that significant?  Compare to the carbon cost of one transatlantic flight, one heated building for a semester, or the embodied carbon of a new server rack.*

11.  Apply Jevons paradox directly: if a future tool reduces Sofia's per-query cost by 80%, predict what happens to her total AI carbon footprint over a semester.  What behavioral or policy intervention could prevent the paradox from operating?

   *Hint: An 80% cost reduction means the same task now costs 1/5 as much.  If Sofia currently self-limits her AI use based partly on cost (conscious or not), what happens when that constraint is removed?  What would "usage caps," "carbon budgets," or "efficiency labels" look like as policy interventions?  Would any of them work?*

12.  The local model experiment used roughly the same carbon as the frontier cloud queries for much longer work.  What does this suggest about the conditions under which local inference is actually lower-carbon, and when the comparison goes the other way?

   *Hint: The local model ran for 4 hours; the frontier queries took much less time.  What drove the local cost?  Now imagine Sofia ran the same experiment but used 10x more cloud queries.  Which direction does the comparison shift?  What variables determine the crossover point?*

> **Common Misconception:** "Switching to renewable energy at the data center makes AI carbon-neutral."  Renewable energy purchases do not eliminate energy consumption; they offset it with generation elsewhere on the grid.  The actual energy demand, water use for cooling, and embodied carbon in hardware remain unchanged.  "100% renewable" cloud providers are making a true but partial claim: they are purchasing renewable energy credits, which is better than not doing so, but it is not the same as using zero carbon.  Meaningful carbon reduction requires reducing the energy consumption itself, not only changing its source on paper.

According to Jevons paradox, a 10x improvement in model inference efficiency will most likely:

[( )] Reduce total AI energy consumption by roughly 10x
[( )] Leave total consumption unchanged, because usage patterns are fixed
[(X)] Lower the cost per use and expand the range of viable uses, potentially increasing total consumption
[( )] Affect training costs only, since inference is already efficient

---

## 7.  What You Can Do About It

The audit tells you what a week costs.  This section is the response: the moves that cut both the bill and the footprint, so you can argue for them on either ground.  Each one is also something a policy can require, which is why Part III asks you for a cost and routing section.

**Tokens.**  Hosted APIs charge by the token, and output tokens cost two to four times more than input tokens because the model generates them one at a time and cannot parallelize the work.  Every turn of a conversation resends the whole history as input, so long conversations cost far more than their length suggests.  Set `max_tokens` (and `budget_tokens` where the API offers it) before an agent runs, so a stuck loop cannot spend the month's budget on one task.  A budget you set in code is a clause an auditor can check.

**Thinking tokens.**  A reasoning model buys more computation only by emitting more tokens before the answer, and those tokens are billed and burned at the output rate.  Take a 150-word reply, about 200 output tokens, and let the model think first:

| What the model does | Output tokens | Cost @ $60/1M out | Multiple |
|---|---|---|---|
| Answers directly | ~200 | ~$0.012 | 1x |
| Thinks briefly, then answers | ~1,200 | ~$0.072 | 6x |
| Thinks at length, then answers | ~4,200 | ~$0.252 | 21x |

The user sees the same 150-word reply in every row.  Running locally does not make this free; it makes it invisible, moved to your electricity bill and your GPU's service life.  Extra inference time is worth its energy when an iteration adds something the previous one lacked: a checked result, a rejected alternative, a caught contradiction.  When the model restates itself at greater length, you have paid twenty-one times over for a longer way of being equally right or equally wrong.

**Caching.**  Prompt caching is a provider-level feature: a static prefix of your prompt (typically the system prompt) is cached after the first call, and later requests sharing that identical prefix pay a lower cache-read price, roughly one-tenth the cost of fresh input tokens.  To get the benefit, put static content first (system prompt, rules, background documents), put dynamic content last (the user's message, the date, retrieved passages), keep the prefix long enough to matter, and never prepend a timestamp, which turns every request into a cache miss.  Semantic caching goes further and returns a stored response when a new query is similar enough to a past one, without calling the model at all; use it only where a slightly varied but correct answer is acceptable.

**Routing.**  Right-sizing has two dials: which model, and how much thinking.  They are independent, and a small model asked to think at length can cost more than a large one answering directly.  A routing function therefore emits two decisions.  Three common shapes: classifier-first (a tiny model or rule labels the query `trivial`, `medium`, `complex`, or `sensitive`, and each label maps to a tier), confidence-based (a small model answers and escalates when its confidence is low, which is unreliable because models are poorly calibrated), and cost-capped (every query goes to the small model first and escalates only if the answer fails a quality check such as a property test or a judge score).

**Batching and streaming.**  Batching submits requests together, usually at half price, with minutes-to-hours latency; it fits nightly document processing, bulk embedding, and offline evaluation, not a user at a screen.  Streaming returns tokens as they are generated; it improves perceived responsiveness and changes the cost not at all.

### Right-Sizing Decision Matrix

| Task | Appropriate Model Scale | Rationale for Scale Choice | Local vs. Cloud Preference | Environmental Trade-off |
|---|---|---|---|---|
| Classify incoming email as spam or not spam | Fine-tuned small model (1B parameters or fewer) | Binary classification is a well-defined, low-complexity task with massive labeled data available for fine-tuning to high accuracy | Local or edge; no real-time cloud round-trip needed | Highest environmental benefit from right-sizing; frontier model here is ~100x over-powered |
| Summarize a 10-page PDF | Mid-size model (7B-13B parameters) | Requires coherent abstractive reasoning but the document fits in context and 7B models handle it well | Local is viable on consumer hardware; cloud for convenience | Local on a modern laptop adds ~0.07 kg/8h; cloud call at ~0.0005 kg is lower for a single summary |
| Generate a photorealistic logo | Diffusion model (specialized architecture) | Image synthesis requires a different architecture from text; quality depends heavily on model scale and fine-tuning | Cloud typical; GPU requirements for quality generation are high | Per-image cost is low; volume at production scale becomes significant |
| Debug a 500-line codebase with cross-file dependencies | Large model (30B+ parameters) with code specialization | Complex multi-step reasoning across a large context window; rare error patterns benefit from extensive training data | Cloud preferred; local possible on high-end hardware | Justified higher cost because smaller models fail measurably on this task class |
| Answer a trivia question | Any scale, including very small models | Low reasoning demand; factual recall; fast response is more important than depth | Local sufficient; cloud API call is unnecessary overhead for this task | Largest unnecessary expense: routing simple factual queries to frontier models |
| Transcribe and summarize a 2-hour lecture | Specialized speech model plus a lightweight summarizer | Two-model pipeline; transcription model is heavily optimized for audio; summarizer is a lightweight text task | Local is fully feasible; privacy argument is strong for lecture content | Demonstrates that task decomposition can reduce energy relative to a single large model |

A development team wants to reduce the carbon footprint of their AI-powered customer support system.  Which intervention is most likely to produce the largest reduction in inference-time carbon emissions?

[( )] Switching from Python to a compiled language for the API wrapper; runtime efficiency gains in the surrounding code are in the microsecond range, whereas the model forward pass dominates at the millisecond-to-second scale; the wrapper is not the bottleneck
[( )] Adding a caching layer that serves identical responses to repeated queries without re-running the model; caching is a meaningful lever but only eliminates compute for exact or near-duplicate queries; a customer support system with diverse question phrasing will still run the full model for the majority of requests
[(X)] Replacing a 70B-parameter frontier model with a fine-tuned 7B-parameter model that achieves equivalent accuracy on the support domain; a 10x reduction in model size directly cuts inference compute by roughly 10x
[( )] Purchasing carbon offsets equal to the service's measured emissions; offsets shift accounting responsibility but do not reduce the actual energy the model consumes per query; the compute load and its direct energy draw remain identical

### Critical Thinking Questions

13.  A team enables extended thinking across their entire support agent because it improved answers on the hardest ten percent of tickets.  Using the thinking-token table, estimate what that decision costs them on the other ninety percent, and propose a change that keeps the gain and drops most of the cost.

   *Hint:* If ninety percent of tickets did not need it, most of the added spend bought nothing, and the multiple is large enough that the waste can exceed the entire original bill.  The change is a routing decision, not a capability decision: classify first, and spend thinking only on the tickets that a cheap signal says are hard.

14.  Your reasoning model runs locally, so the per-token cost is zero.  Give two reasons the environmental argument in this session still applies, and one reason it applies *more* strongly than it would to a hosted call.

   *Hint:* Electricity and hardware amortization are the two obvious ones, and neither disappears because no invoice arrives.  The stronger case: a consumer GPU is typically less energy-efficient per token than a datacenter accelerator running batched inference, so the same generation can cost more joules locally than remotely even though it costs fewer dollars.

15.  The right-sizing matrix has no column for accuracy.  Construct the missing argument: under what conditions does using a smaller model for a task impose a *social* cost that must be weighed against the carbon benefit?

   *Hint: Consider a medical triage task or a hiring screening task where the smaller model's error rate is meaningfully higher.  Who bears the cost of those errors?  Are those costs visible in the same accounting that makes the carbon benefit visible?  Is there a way to measure both in the same units?*

## Code Cell

A cost section needs a number, so build the model that produces one.  This script prices a hypothetical Ursinus College tutoring agent at 200 queries per day against a GPU rented by the hour.  Before you run it, predict which monthly figure is larger.  Then change `queries_per_day` until the two lines cross, and explain why the crossover depends on how fully the GPU is used.

```python
# Cost model for Ursinus tutoring agent
queries_per_day = 200
system_prompt_tokens = 300   # input
question_tokens = 100        # input
answer_tokens = 250          # output

price_input_per_million = 15.00   # GPT-4 class
price_output_per_million = 60.00  # GPT-4 class (4x input)

input_per_query = system_prompt_tokens + question_tokens
output_per_query = answer_tokens

cost_per_query = (
    (input_per_query / 1_000_000) * price_input_per_million +
    (output_per_query / 1_000_000) * price_output_per_million
)

daily_cost = queries_per_day * cost_per_query
monthly_cost = daily_cost * 30
print(f"Monthly API cost: ${monthly_cost:.2f}")

# Local model: GPU runs 24/7 regardless of query volume
gpu_cost_per_hour = 0.50
monthly_gpu_cost = gpu_cost_per_hour * 24 * 30
print(f"Monthly local GPU cost: ${monthly_gpu_cost:.2f}")
```
@Pyodide.eval

---

# Part III: Drafting Workshop

Your policy has a structure, your project is mapped onto real frameworks, and you have numbers for what inference costs.  Now write.  Each team drafts two sections of its final project's governance one-pager, one about data (section 5) and one about cost and routing, then trades them and reads the other team's draft the way an auditor would.

## 8.  Exercises

1.  *Draft the data-handling section.*

   *What to do:* Write section 5 in full, enforceable prose: what the system collects, where each item lives, how long it is retained, which regulated categories it touches (FERPA, IRB), who can read it, and which log proves each claim.  The Recorder types; everyone argues.

   *Starter hint:* Start from your data-flow audit.  Every arrow in it is a sentence here: "Student questions are sent to the hosted API and are not stored by us after the session; the request log at `logs/requests.jsonl` retains only a hash of the question and the timestamp, for 30 days, then the nightly job deletes it."  If an arrow has no sentence, your audit found a gap.

   *You've succeeded when:* An outside auditor could read section 5 and determine, from your system's logs and configuration, whether any violation occurred, without asking you what you meant.

2.  *Draft the cost and routing section.*

   *What to do:* Write the section the eight-section skeleton does not have.  State which model tier each stage of your pipeline uses and why, the default position of the thinking dial, the per-session token or dollar budget and the parameter that enforces it, what you measure (kg CO$_2$eq per 1,000 queries, dollars per day, or both), who reads that number and how often, and the guard that keeps a cheaper query from becoming more queries.

   *Starter hint:* Use the right-sizing matrix and the Model 4 numbers.  A clause like "we use the smallest model that passes the golden set; the set lives in `/eval` and the routing table in `config/routing.yaml`; `max_tokens` is 1,024 for every call; the Recorder posts monthly cost and query count to the repository" passes the test.  "We will be mindful of cost" does not.  For the anti-Jevons guard, name a cap, a budget, or a review trigger tied to query growth.

   *You've succeeded when:* The section names a model, a budget, a metric, an owner, a schedule, and a guard, and each of them is checkable from a file or a log.

3.  *Structured peer review.*

   *What to do:* Exchange drafts with another team.  Reviewers apply exactly two tests to every sentence: the third-party test, and the "who, specifically" test.  Return the draft with each failing sentence flagged.

   *Starter hint:* Mark every sentence that contains the words "we will," "the team," "regularly," "appropriately," or "as needed" as a likely failure.  These words almost always indicate that a specific actor, schedule, or threshold has been omitted.

   *You've succeeded when:* You return a draft with every vague clause flagged and a specific suggested revision for at least three of them, a concrete alternative rather than criticism alone.

4.  *Red-team the letter against the intent.*

   *What to do:* For the other team's cost section, devise one use that violates the policy's *intent* while complying with its *letter*.  The drafting team must then close the gap.

   *Starter hint:* Look for underspecified dials.  If the policy says "no frontier model by default," ask whether thinking may be on for every call, whether a retry loop can escalate without limit, or whether a batch job counts.  If the data section says "we do not store questions," ask what the request log contains.  Reward hacking, you will notice, is not only for models.

   *You've succeeded when:* You have identified a real gap (a use that violates intent but passes a literal reading) and the drafting team has written a revised clause that closes it.

5.  *Incident drill (if time remains).*

   *What to do:* Write the first three steps your team executes when a user reports your agent gave a harmful answer, with owners and timestamps.

   *Starter hint:* Step 1 names who receives the report and the window in which they acknowledge it.  Step 2 says what they do immediately (disable the system, preserve logs, notify a supervisor).  Step 3 says what analysis is required and by when.  If you cannot name the owner, your section 7 is not done.

   *You've succeeded when:* A new team member who has never seen your project could read your three steps and execute them correctly in a real incident, without asking anyone for clarification.

---

## Reflection Prompt

*Personal:* Which of the four roles (builder, evaluator, auditor, policy author) felt most natural to you today, and which felt most uncomfortable?  Then look at the numbers from Part II.  Did they change how you feel about your own AI use this semester, or did you find yourself rationalizing the usage you already had?  Either answer is informative.

*Technical:* The sections you wrote commit you, in writing, to a data retention schedule, a model tier, a token budget, and a measurement someone posts on a schedule.  What would it mean to enforce those commitments on yourself and your team after the course ends?  And is there a version of your project that fits the Jevons pattern, where making it efficient is exactly what makes expansion rational?

*Societal:* The organizations best positioned to reduce AI's environmental impact (large cloud providers, frontier model developers) are the same organizations with the strongest financial incentives to increase AI use.  What governance mechanisms (regulatory, market-based, or professional) could align those incentives with aggregate carbon reduction?  Consider the history of automotive fuel-economy standards: automakers resisted, lobbied, and then innovated when the regulation held.  What would the AI equivalent look like, and does the person writing it need the technical background to make the third-party test meaningful?

---

-> Coming Up Next: *Evaluation Workshop II: Run Your Rubric Against Your Project* (Thursday, November 19) takes section 6 of your one-pager, the evaluation and monitoring section, and makes it real: you run your own rubric against your project's outputs and find out whether the harness your policy promises produces the evidence the policy needs.  Bring today's two sections; the workshop tests whether their measurements are ones you can actually take.

## Further Reading

- NIST. *AI Risk Management Framework 1.0* (2023, online), especially the Govern function.
- European Union.  *AI Act* (2024), Annex III on high-risk systems, including education uses.
- Patterson, D. et al. "Carbon Emissions and Large Neural Network Training."  *arXiv* 2104.10350 (2021).  The most cited quantitative analysis of training costs.
- Schwartz, R. et al. "Green AI." *Communications of the ACM* 63(12): 54-63 (2020).  The case for efficiency metrics alongside accuracy.
- Strubell, E., Ganesh, A., and McCallum, A. "Energy and Policy Considerations for Deep Learning in NLP." *ACL* (2019).  The paper that put training carbon costs on the NLP community's radar.
- Jevons, W.S. *The Coal Question.*  Macmillan (1865), Chapter 7.  Readable in excerpt; the original paradox argument is clearer than most secondary accounts.
- [AI for Accessibility](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AIAccessibility), a self-paced tutorial: if your project touches a community partner with access needs, your data and oversight sections have another audience, and this is where to start.
- Your institution's acceptable-use and responsible-AI policies, read now with an author's eye.
