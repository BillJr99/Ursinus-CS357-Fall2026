---
layout: assignment
permalink: /Assignments/EnvironmentalImpact
title: "CS357: Foundations of Artificial Intelligence - Written Assignment: The Carbon Cost of Intelligence"

info:
  coursenum: CS357
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

---

## Part 1: Personal Carbon Audit (one week)

Keep a log for one full week of every AI tool you use. For each interaction, record:

- Tool name and model (if known)
- Task description (one sentence)
- Approximate prompt length (short: under 50 words; medium: 50–200 words; long: over 200 words)
- Approximate response length (same scale)
- Cloud-hosted or local

At the end of the week, estimate the total CO2eq for your AI use that week using the reference values above. Show your conversion steps. Then identify three other activities from that same week — such as commuting, streaming, or meals — and compute their CO2eq for comparison. Choose activities that are actually comparable in frequency or purpose to your AI use.

Write a one-paragraph reflection on what surprised you most in the comparison.

---

## Part 2: Project Environmental Analysis

Analyze your final project agent team design through an environmental lens.

1. **Per-session call count**: Walk through a typical use session of your system step by step. How many agent calls are made? What models are called? Are any calls parallelized or cached?
2. **Per-session CO2eq**: Estimate the CO2eq for one typical session using the reference values. State every assumption you make (for example: what model size, what provider, what grid mix).
3. **Annual projection at scale**: If 1,000 users each ran one session per day for a year, what is the total estimated CO2eq? Compare this to a concrete real-world equivalent (flight hours, car miles, household electricity).
4. **Hot spots**: Identify the top three environmental hot spots in your design — the three places where reducing calls, switching models, or changing architecture would have the largest impact. Rank them quantitatively.

---

## Part 3: Redesign for Efficiency

Propose three concrete design changes that would reduce the environmental footprint of your project.

For each change:
- Name the change precisely (for example: "cache the retrieval agent's output for identical queries within a 30-minute window")
- Estimate the percentage reduction in CO2eq per session, with reasoning
- Analyze what capability, if any, is sacrificed — be honest; if the answer is "none," explain why

At least one of your three changes must involve model selection (switching to a smaller model for a specific subtask), and at least one must involve system architecture (eliminating or batching calls).

---

## Part 4: Jevons Paradox Analysis

The Jevons paradox (originally observed in coal consumption in the 1860s) holds that increases in the efficiency of resource use tend to increase total resource consumption because lower cost per unit enables more use. Write a structured analysis in three sections:

**For**: Argue that making AI inference more efficient *will* reduce total energy use. What mechanisms would cause total energy use to fall? What historical examples or AI-specific evidence support this position?

**Against**: Argue that making AI inference more efficient *will not* reduce total energy use because of rebound effects. What mechanisms cause efficiency gains to be consumed by expanded use? What evidence from AI adoption or comparable technology supports this?

**Your position**: State which side you find more convincing, and why. Your position must engage with the strongest argument on the other side. Close with one concrete implication of your position for how AI systems should be designed, deployed, or regulated.

---

## Submission Instructions

Submit a single PDF or markdown document containing all four parts. Label each part clearly. Attach your one-week usage log as an appendix (a simple table is fine).

- If collaboration with a buddy was permitted, did you work with a buddy on this assignment? If so, who? If not, do you certify that this submission represents your own original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did it take you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
