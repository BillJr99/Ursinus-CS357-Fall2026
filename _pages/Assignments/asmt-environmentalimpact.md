---
layout: assignment
permalink: /Assignments/EnvironmentalImpact
title: "CS357: Foundations of Artificial Intelligence - Written Assignment: The Carbon Cost of Intelligence"

info:
  coursenum: CS357
  purpose: "To make the energy and carbon cost of AI concrete — measuring it in your own use and your project, then confronting whether efficiency gains actually reduce total consumption."
  tilt:
    task: "Keep a one-week personal AI carbon audit, estimate your final project's per-session and at-scale footprint, propose prioritized design changes, and argue a defended position on the Jevons paradox."
    criteria: "Assessed in four equal parts — a grounded personal carbon audit, a traceable project footprint analysis, prioritized design recommendations with honest capability trade-offs, and a well-argued Jevons-paradox analysis; see the rubric below for the full breakdown."
  points: 100
  goals:
    - To quantify the approximate energy and carbon cost of different AI operations
    - To analyze the environmental trade-offs between cloud-hosted and locally-run AI
    - To propose concrete design choices that reduce environmental impact without sacrificing capability
    - To engage with the Jevons paradox and rebound effects in technology adoption
  rubric:
    - weight: 25
      description: Personal Carbon Audit
      preemerging: No usage log is provided, or estimates are not grounded in reference values
      beginning: A usage log is present but incomplete, or carbon estimates are provided without showing the reference values or conversion steps used
      progressing: A complete one-week log is provided with reasonable estimates derived from reference values; the comparison to non-AI activities is present but the activities chosen are not meaningfully comparable
      proficient: A complete one-week log is provided, every estimate cites the reference value and conversion steps used, the comparison to at least three non-AI activities of similar daily frequency is calibrated and clearly contextualized, and the reflection identifies at least one surprising finding from the data
    - weight: 25
      description: Project Environmental Analysis
      preemerging: No environmental analysis of the final project is attempted
      beginning: The analysis names the project's agents and models but does not estimate call counts or CO2eq
      progressing: Agent call counts per session and approximate CO2eq per session are estimated with reasonable assumptions stated; the 1000-user annual projection is present but the top hot spots are not clearly justified
      proficient: Agent call counts per session are justified with a worked example, CO2eq per session and the 1000-user annual projection are calculated with all assumptions stated and traceable, the top three environmental hot spots are identified and ranked with quantitative support, and at least one hot spot reflects a design choice the team could realistically change
    - weight: 25
      description: Design Recommendations
      preemerging: No redesign recommendations are provided
      beginning: Recommendations are present but are generic ("use a smaller model") without specifics tied to the project
      progressing: Three concrete changes are proposed and tied to the project design, with estimated reductions; the capability trade-off is acknowledged but not analyzed
      proficient: Three concrete, project-specific changes are proposed with estimated percentage reductions justified by the analysis, the capability cost of each change is analyzed honestly with at least one change shown to have negligible capability impact, and the recommendations are prioritized
    - weight: 25
      description: Critical Analysis of Jevons Paradox
      preemerging: The Jevons paradox is not addressed or is mischaracterized
      beginning: Both positions are stated but not argued; the student does not arrive at a defended position
      progressing: Both positions are argued with at least one piece of evidence each; a position is stated but the supporting reasoning is underdeveloped
      proficient: Both positions are argued with specific, relevant evidence drawn from technology history or AI specifically; the student's own position is stated clearly, defended with reasoning that engages with the strongest counterargument, and connected to at least one implication for how AI systems should be designed or regulated
  readings:
    - rtitle: "Strubell et al., Energy and Policy Considerations for Deep Learning in NLP (2019)"
      rlink: "https://arxiv.org/abs/1906.02629"
    - rtitle: "Patterson et al., Carbon Emissions and Large Neural Network Training (2021)"
      rlink: "https://arxiv.org/abs/2104.10350"
    - rtitle: "Luccioni et al., Power Hungry Processing: Watts Driving the Cost of AI Deployment? (2023)"
      rlink: "https://arxiv.org/abs/2311.16863"
    - rtitle: "Jevons, The Coal Question (1865), Chapter 7 summary"
      rlink: "https://www.econlib.org/library/YPDBooks/Jevons/jvnCQ.html"

tags:
  - ethics
  - environment
  - written

---

Every query you send to a language model consumes electricity, and electricity has a carbon cost that varies by model size, inference provider, and grid energy mix. This assignment asks you to measure that cost for your own behavior, analyze it for your final project, propose design changes that reduce it, and then grapple with the uncomfortable question of whether efficiency improvements actually reduce total energy use at all.

---

## How to Approach This Assignment

- **Calibrated reasoning over false precision.** The reference values below are order-of-magnitude estimates, not precise measurements. Your job is not to compute an exact number — it is to show your work clearly enough that someone could check your assumptions and understand where the uncertainty lies. Round to one or two significant figures and explain your choices.
- **Choose comparisons that are actually comparable.** The most common mistake in Part 1 is comparing AI energy use to a one-time event (a flight, a steak dinner) rather than a daily habit. Compare your week of AI use to a week's worth of activities that have a similar cadence to your AI use — not to the single most dramatic thing you can think of.
- **Start the usage log on Day 1 of the assignment week.** Students who try to reconstruct their usage from memory at the end of the week produce much weaker logs than students who record in real time. Set a phone reminder or keep a tab open.
- **The Jevons Paradox section rewards intellectual honesty.** The goal is not to arrive at the "right" answer — it is to engage seriously with a genuine tension in the evidence. The strongest essays are ones where the student acknowledges the best evidence against their position before explaining why they still hold it.

> **Common Pitfall: Comparing AI energy use to a flight (a one-time event) rather than a daily habit (comparable to daily AI use).** A single transatlantic flight emits roughly 1,000,000 g CO2eq. Your entire week of AI use probably emits between 1 and 50 g CO2eq. That comparison is technically accurate but deeply misleading — it makes AI look trivial when the relevant question is: what does this habit cost at scale, over a year, across millions of users? Compare AI use to other daily habits: streaming video, driving to class, eating lunch.

**Recommended time budget:**
- Part 1 (Usage log, ongoing): 5 minutes/day × 7 days = 35 minutes of logging; 45 minutes of analysis and writing
- Part 2 (Project Environmental Analysis): 60 minutes
- Part 3 (Redesign for Efficiency): 45 minutes
- Part 4 (Jevons Paradox): 60 minutes
- Reflection + polish: 15 minutes

**What proficient work looks like:** A student working at the proficient level shows their arithmetic explicitly (reference value × count = total), chooses non-AI comparisons that are genuinely calibrated (same frequency, same week), and arrives at a position on the Jevons Paradox that engages with the strongest evidence on the other side before stating their own conclusion.

---

## Reference Values

Use the following approximate values for your estimates. These are order-of-magnitude figures drawn from published research; your goal is calibrated reasoning, not false precision.

| Operation | Approximate CO2eq |
|---|---|
| Single GPT-4-class query (cloud) | 0.001 – 0.01 g CO2eq |
| Single 7B local model query | 0.0001 – 0.001 g CO2eq |
| Training a large LLM (one run) | 280 – 550 tonnes CO2eq |
| Streaming video, 1 hour | 36 g CO2eq |
| Driving a gasoline car, 1 mile | 400 g CO2eq |
| A beef hamburger | 2,500 g CO2eq |

**How to use these values:** Pick a value within the range that matches your best estimate of the model size and provider. Use the lower end of the range for smaller models or providers using cleaner energy grids; use the upper end for larger models or coal-heavy grids. State which value you chose and why.

---

## Part 1: Personal Carbon Audit (one week)

**What this part is testing:** Whether you can log real behavior, apply reference values to produce a rough estimate, and reason about what the numbers mean in context — not just arithmetic, but interpretation.

Keep a log for one full week of every AI tool you use. For each interaction, record:

- Tool name and model (if known)
- Task description (one sentence)
- Approximate prompt length (short: under 50 words; medium: 50–200 words; long: over 200 words)
- Approximate response length (same scale)
- Cloud-hosted or local

**EXAMPLE — sample week of AI usage log (use your own data; this is for format illustration only):**

| Date | Tool / Model | Task | Prompt Length | Response Length | Hosted |
|------|-------------|------|---------------|-----------------|--------|
| Mon | ChatGPT / GPT-4 | Debug a Python KeyError | medium | medium | Cloud |
| Tue | Llama 3 8B (local) | Summarize a PDF | long | medium | Local |
| Wed | ChatGPT / GPT-4 | Draft email to professor | short | short | Cloud |
| Thu | GitHub Copilot | Autocomplete 3 functions | short × 12 | short × 12 | Cloud |
| Fri | ChatGPT / GPT-4 | Brainstorm essay outline | medium | long | Cloud |

*EXAMPLE — replace with your own log data. Your log should cover the full week (7 days), not just 5 rows.*

**EXAMPLE — completed conversion calculation:**

> *I sent 50 medium prompts to GPT-4 this week (cloud-hosted). Using the reference value of 0.005 g CO2eq per query (midpoint of the 0.001–0.01 range, appropriate for a large cloud-hosted model): 50 × 0.005 g = 0.25 g CO2eq for my AI use this week. For comparison, I streamed video for approximately 3 hours this week: 3 × 36 g = 108 g CO2eq. My AI use this week was about 432 times less carbon-intensive than my video streaming. However, I made roughly 50 AI queries; at this rate over a year (50 × 52 = 2,600 queries annually), my personal AI use would total approximately 13 g CO2eq/year — equivalent to about 0.03 miles of driving. The surprise: AI feels like a significant activity but its individual-level carbon footprint is dwarfed by ordinary daily habits.*

*EXAMPLE — show your own conversion steps in this format. The reference value, the multiplication, and the comparison must all be visible.*

At the end of the week, estimate the total CO2eq for your AI use that week using the reference values above. Show your conversion steps. Then identify three other activities from that same week — such as commuting, streaming, or meals — and compute their CO2eq for comparison. Choose activities that are actually comparable in frequency or purpose to your AI use.

Write a one-paragraph reflection on what surprised you most in the comparison.

> **Getting Started Hint:** Start logging on Day 1. Open a notes app or spreadsheet and record each interaction as it happens. If you forget for a day, note the gap honestly — partial data with an honest acknowledgment of the gap is better than reconstructed data presented as complete.

> **Scope check:** Your log should have at least 10–30 rows across the week (most CS students use AI tools multiple times per day). Your written analysis and reflection should be approximately 250–350 words, plus the log table as an appendix.

---

## Part 2: Project Environmental Analysis

**What this part is testing:** Whether you can apply quantitative reasoning to a system you designed — estimating costs you did not directly measure by working from first principles and stated assumptions.

Analyze your final project agent team design through an environmental lens.

1. **Per-session call count**: Walk through a typical use session of your system step by step. How many agent calls are made? What models are called? Are any calls parallelized or cached?
2. **Per-session CO2eq**: Estimate the CO2eq for one typical session using the reference values. State every assumption you make (for example: what model size, what provider, what grid mix).
3. **Annual projection at scale**: If 1,000 users each ran one session per day for a year, what is the total estimated CO2eq? Compare this to a concrete real-world equivalent (flight hours, car miles, household electricity).
4. **Hot spots**: Identify the top three environmental hot spots in your design — the three places where reducing calls, switching models, or changing architecture would have the largest impact. Rank them quantitatively.

> **Getting Started Hint:** For the per-session call count, walk through your system as if you were a user. Every time the system calls an LLM — for routing, for tool use, for synthesis, for generating the final response — that is one call. Write them out step by step. If your system makes conditional calls (sometimes it does X, sometimes Y), estimate the average across realistic sessions.

> **Scope check:** Your response to this part should be approximately 400–500 words, including the per-session calculation with visible arithmetic, the annual projection with a comparison, and the ranked hot spots with quantitative justification.

---

## Part 3: Redesign for Efficiency

**What this part is testing:** Whether you can propose concrete, project-specific improvements with honest analysis of the capability trade-offs — not generic advice, but recommendations tied to the specific architecture choices your team made.

Propose three concrete design changes that would reduce the environmental footprint of your project.

For each change:
- Name the change precisely (for example: "cache the retrieval agent's output for identical queries within a 30-minute window")
- Estimate the percentage reduction in CO2eq per session, with reasoning
- Analyze what capability, if any, is sacrificed — be honest; if the answer is "none," explain why

At least one of your three changes must involve model selection (switching to a smaller model for a specific subtask), and at least one must involve system architecture (eliminating or batching calls).

> **Getting Started Hint:** Look at your hot spots from Part 2 and ask: "What would I give up by cutting this?" The best recommendations are ones where you can honestly say the trade-off is acceptable — either the capability loss is negligible, or the environmental gain is large enough to justify it. Avoid recommending changes that would break the core functionality of your system.

> **Scope check:** Your response to this part should be approximately 350–450 words — roughly one paragraph per recommendation, each with the precise change, the estimated reduction, and the honest capability analysis.

---

## Part 4: Jevons Paradox Analysis

**What this part is testing:** Whether you can engage with a genuine intellectual controversy — argue both sides with evidence, and arrive at a defended position that acknowledges the strongest counterargument.

**Background — what the Jevons Paradox is:** In 1865, economist William Stanley Jevons observed that improvements in the efficiency of steam engines did not reduce coal consumption in Britain — they increased it. More efficient engines made steam power cheaper per unit of work, which caused demand for steam power to grow faster than efficiency improved, so total coal use went up. This pattern has been observed in many technologies since: fuel-efficient cars led to more driving; energy-efficient light bulbs led to more lighting. The question for AI is: if we make AI inference more energy-efficient, will total AI energy use go down (because each query costs less) or up (because cheaper queries cause more queries to be sent)?

The Jevons paradox (originally observed in coal consumption in the 1860s) holds that increases in the efficiency of resource use tend to increase total resource consumption because lower cost per unit enables more use. Write a structured analysis in three sections:

**For**: Argue that making AI inference more efficient *will* reduce total energy use. What mechanisms would cause total energy use to fall? What historical examples or AI-specific evidence support this position?

**Against**: Argue that making AI inference more efficient *will not* reduce total energy use because of rebound effects. What mechanisms cause efficiency gains to be consumed by expanded use? What evidence from AI adoption or comparable technology supports this?

**Your position**: State which side you find more convincing, and why. Your position must engage with the strongest argument on the other side. Close with one concrete implication of your position for how AI systems should be designed, deployed, or regulated.

> **Getting Started Hint:** The "For" section is harder to argue than it looks. The naive version ("more efficient = less energy used") ignores demand. Try to find evidence for mechanisms that would actually constrain total demand even as efficiency improves — for example, regulatory caps, market saturation, or substitution effects. The "Against" section has abundant AI-specific evidence: inference costs have dropped dramatically since 2020, yet total AI energy use has grown substantially. Use that.

> **Scope check:** Your Jevons analysis should be approximately 500–600 words total across all three sections. Your position section should be at least 150 words and must engage with the strongest counterargument, not just dismiss it.

---

## Common Mistakes

- **Comparing AI energy use to a flight or a steak rather than a daily habit.** These comparisons are technically accurate but deeply misleading. Compare AI use to other daily-frequency activities — commuting, streaming, or eating lunch — so the scale is meaningful.
- **Not showing conversion steps.** "My AI use this week produced 2 g CO2eq" earns beginning. "50 queries × 0.005 g/query (GPT-4 midpoint estimate) = 0.25 g CO2eq" earns proficient. The arithmetic must be visible.
- **Proposing generic design changes in Part 3.** "Use a smaller model" is not a recommendation — it is a category. Name the specific model, the specific subtask it would replace, and the specific capability you expect to lose or retain.
- **Mischaracterizing the Jevons Paradox as simply "efficiency makes things worse."** The Jevons paradox is about the relationship between efficiency, price, and demand — it is a claim about market dynamics, not a moral argument. State it precisely before you argue about it.
- **Writing a Jevons section that does not arrive at a position.** "Both sides have merit" is not an answer. You must commit to one side and explain why its strongest argument outweighs the other side's strongest argument.

---

## Submission Instructions

Submit a single PDF or markdown document containing all four parts. Label each part clearly. Attach your one-week usage log as an appendix (a simple table is fine).

- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did it take you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
