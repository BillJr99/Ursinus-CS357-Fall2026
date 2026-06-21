---
layout: project
permalink: /Projects/ResponsibleAI
title: "CS357: Foundations of Artificial Intelligence - Project: Responsible AI Audit"

info:
  coursenum: CS357
  points: 100
  goals:
    - To select a specific, named, deployed AI system with identifiable affected populations and apply a structured framework (NIST AI RMF, EU AI Act, or Montreal Declaration) to it completely and systematically
    - To identify at least three concrete failure modes with named mechanisms in a deployed AI system, distinguishing risks that have materialized from risks that are foreseeable
    - To produce a governance document with a monitoring plan containing specific metrics and thresholds, an incident response procedure with named roles and timelines, a stakeholder communication plan, and an appeal process navigable without a lawyer
    - To communicate findings and recommendations to a non-technical stakeholder audience in plain English in a fifteen-minute board presentation that moves from evidence to action
  rubric:
    - weight: 20
      description: System Selection and Scoping
      preemerging: The selected system is too generic to analyze meaningfully (e.g., "AI in hiring" rather than a named product), or no proposal is submitted
      beginning: A specific system is selected but the proposal does not identify the affected populations, what the system decides or outputs, or why the chosen framework fits better than the alternatives
      progressing: The proposal identifies a specific system with named affected populations and a rationale for the chosen framework; the scope is mostly well-defined but key decisions or data flows are left unspecified, or the preliminary hypothesis is absent
      proficient: The proposal names the specific system and its operator, identifies the affected populations and how the system's decisions reach them, argues in three sentences why the chosen framework fits this system better than the two alternatives, states at least one preliminary hypothesis about where the highest risks lie, and demonstrates that enough public information exists to support the analysis (citing at least two independent sources found in the initial 30-minute search)
    - weight: 25
      description: Risk Analysis and Framework Application
      preemerging: The chosen framework is not applied, or application is superficial name-checking — for example, "the system GOVERNS by having terms of service" without naming a responsible role or artifact
      beginning: The framework is applied to some parts of the system but major steps or categories are skipped; findings are stated without citing a source for the claim
      progressing: The framework is applied systematically with most steps completed and findings grounded in cited sources; at least two failure modes are identified with mechanisms, but one or more findings describe abstract risks ("the system may exhibit bias") rather than specific, mechanistic failure modes
      proficient: Every major framework step or category produces a specific, evidenced finding with a citation; at least three distinct failure modes are documented — each names the affected group or input type, the specific erroneous output, and the mechanism by which the failure occurs; the analysis explicitly distinguishes between risks that have materialized (with evidence) and risks that are foreseeable; accountability gaps are named — not just "accountability is unclear" but specifically what role is absent and what decision it cannot be made without
    - weight: 25
      description: Governance Recommendations
      preemerging: No governance recommendations are provided, or recommendations are aspirational values without mechanisms — for example, "increase transparency" without a named artifact or process
      beginning: Recommendations are present but are generic best practices not tailored to this system, or lack owners, timelines, or the threshold that triggers review
      progressing: Recommendations are specific to the system with named roles; the monitoring plan names metrics but omits thresholds or measurement frequency; the incident response procedure and appeal process are present but incompletely specified
      proficient: The monitoring plan names each metric, its data source, its measurement frequency, the specific threshold that triggers review, and the named role responsible — for example, "demographic parity ratio measured monthly on a random 50-essay sample, review triggered if ratio falls below 0.9, owned by the District AI Coordinator"; the incident response procedure defines what constitutes an incident with a specific trigger (not "unexpectedly low scores"), names who is notified in what order within what timeframe, and names who has authority to suspend the system; the stakeholder communication table distinguishes what each stakeholder group needs to know and who delivers it; the appeal process names how to initiate, who reviews, what evidence the reviewer receives, what remedies are available, and the timeline from initiation to resolution; every recommendation is traceable to a specific risk finding from Stage 2
    - weight: 15
      description: Stakeholder Communication
      preemerging: The stakeholder presentation is missing or is addressed to a technical audience using unexplained framework terminology
      beginning: A presentation is provided but uses technical language a non-specialist board could not act on, or omits the key risks or recommendations
      progressing: The presentation is largely accessible to a non-technical audience with key risks and top recommendations communicated clearly, but at least one section lapses into jargon or the sequence from evidence to recommendation is unclear
      proficient: The presentation is fully accessible to a non-technical stakeholder audience — no unexplained acronyms or framework terms; it covers what the system does, who is at risk, what was found (organized by severity and leading with the most serious finding), and what is recommended (each recommendation with an estimated effort level and timeline); it includes at least one concrete, realistic example of an individual person who could be harmed; it anticipates and has specific evidence-based responses to the three likely board objections listed in the project instructions; it is completable in fifteen minutes
    - weight: 15
      description: Presentation and Artifacts
      preemerging: The presentation and artifact package are missing or substantially incomplete
      beginning: A presentation is delivered but without a rehearsed structure or timing; the artifact package is incomplete — one or more required documents are missing
      progressing: The presentation is organized and delivered within the time limit; the artifact package contains most required documents but at least one is incomplete (e.g., risk analysis cites fewer than eight sources, or governance document is missing the appeal process)
      proficient: The presentation is delivered within fifteen minutes with a clear narrative arc following the required section structure; visual aids are specific enough that a board member could refer to them afterward without the presenter present; the artifact package contains all five required documents — approved proposal, 4-to-6-page risk analysis report with at least 8 citations and 3 documented failure modes, 3-to-5-page governance document with all four required sections, presentation materials, and individual contribution statement if a pair — organized and complete enough to hand to a regulator without modification

tags:
  - final-project
  - ethics
  - governance
  - responsible-ai

---

## Project Overview

This project is an alternative final project track for students more interested in governance, policy, and ethics than in building AI systems. Instead of constructing an agent team, you will perform a structured **responsible AI audit** of a publicly available AI system — the kind of analysis that is increasingly required by regulation, expected by investors, and demanded by affected communities. At the end of the project, you will have a structured risk analysis report, a governance document a real organization could adopt, and a presentation that a real board could act on. The deliverable is not an opinion piece. It is evidenced, structured, and written for people who will make decisions based on it.

This project may be completed individually or in pairs. If completed in pairs, the presentation must have both members presenting, and the final report must include individual contribution statements.

---

## Example Project: Automated Essay Scoring in K-12

To calibrate the expected scope and depth, here is a fully worked example at the proficient level.

**System:** A commercial automated essay scoring (AES) tool used by a school district to grade 8th-grade writing assignments and determine which students receive additional tutoring interventions.

**Framework chosen:** NIST AI RMF, because the system is a decision-support tool used by a public institution with clearly bounded accountability structures, making the GOVERN and MANAGE functions particularly relevant.

**Preliminary hypothesis:** The highest risk lies in the MEASURE function — the district has adopted the vendor's accuracy claims without independent validation on its own student population, which differs demographically from the tool's training data.

**Three failure modes identified:**
1. The tool systematically scores essays by English language learners lower because their syntactic patterns differ from the training distribution; students are routed to intervention they do not need, and away from advanced coursework they do.
2. A rubric update by the vendor changes scoring logic mid-year; the district does not notice because it has no monitoring process.
3. A teacher overrides the AI score for a student they know personally, but the override is undocumented; the audit trail is incomplete.

**Governance recommendation example:** "Metric: Score gap between ELL and non-ELL students on matched writing samples, assessed monthly using a random sample of 50 essays from each population. Threshold: if the gap exceeds 0.5 on the district's 6-point rubric, the AES tool is suspended from influencing placement decisions pending investigation. Owner: District AI Coordinator. Timeline: monthly report due on the 15th of each month."

---

## Getting Started: First 5 Steps

1. **Find a specific system, not a category.** "AI in hiring" is a category. "HireVue's video interview analysis tool as deployed by [named employer]" is a system. You need a named, deployed product with identifiable affected populations and at least some public documentation.
2. **Verify you can find enough public information.** Before committing to a system, spend 30 minutes finding: the operator's public documentation, at least two independent news or academic sources, and any regulatory filings or audits. If you cannot find these, choose a different system.
3. **Choose your framework deliberately.** Read the first page of each of the three frameworks before choosing. Write one paragraph explaining why your chosen framework fits your system better than the alternatives. This paragraph goes in your proposal.
4. **Form your preliminary hypothesis.** Before reading deeply, write your best guess about where the highest risks lie. This is your prior — the analysis will update it.
5. **Organize your evidence.** Create a folder (or shared document) for every source you consult. Cite as you go. A finding with no citation is a finding you cannot defend in the board presentation.

---

## Common Pitfalls

1. **Choosing a system that is too generic or too inaccessible.** "ChatGPT" is too generic — it has no specific deployment context, no named affected population, and no bounded decision. A specific school district's deployment of an AI writing assistant for students with IEPs is a system. If in doubt, ask the instructor before the proposal is due.
2. **Applying the framework superficially.** A weak NIST mapping says "the system GOVERNS by having terms of service." A strong mapping names the specific organizational role responsible for each function, the artifact that produces the evidence, and the gap between what should exist and what does. Framework categories are analytical tools, not labels to attach to paragraphs.
3. **Identifying abstract risks instead of failure modes.** "Bias" is not a failure mode. "The hiring screening tool ranks resumes with women's college names 23% lower than equivalent resumes with men's college names because the training data reflected historical hiring patterns" is a failure mode with a mechanism. Every failure mode in your report must name a mechanism.
4. **Writing governance recommendations that no one can follow.** "Increase transparency" is not a governance recommendation. "Publish a model card updated quarterly, authored by the vendor's responsible AI team, reviewed and signed by the district's AI Coordinator, and made available on the district's public website within 30 days of each update" is a governance recommendation.
5. **Presenting to the wrong audience.** The board presentation is for intelligent, busy, non-technical decision-makers. Every sentence must be in plain English. Every claim must be supportable. Every recommendation must come with an estimated effort level. Practice your presentation on a non-technical friend and revise wherever they look confused.

---

## Stage 1: Proposal (due week 11)

Select a publicly available AI system. The system must be specific: not "a chatbot" but a named, deployed system with a defined purpose and identifiable affected populations.

**Strong system candidates:**
- A **hiring screening tool** that ranks or filters job applicants
- A **medical imaging AI** used to flag or diagnose conditions
- A **content moderation system** that removes or demotes posts
- A **predictive risk tool** used in criminal justice, child welfare, or benefits eligibility
- An **educational AI** that grades, places, or recommends interventions for students

Avoid general-purpose chatbots unless you scope to a specific deployment context (for example, a school district's licensed deployment of an AI writing assistant for students receiving special education services).

**Your one-page proposal must include:**

| Proposal Element | What to Include |
|---|---|
| System identification | Name, operator, brief description of what it does and where it is deployed |
| Affected populations | Who is directly affected by the system's decisions, and how those decisions reach them |
| Framework choice | Which framework (NIST AI RMF, EU AI Act, or Montreal Declaration) and a 3-sentence justification for why it fits this system better than the alternatives |
| Preliminary hypothesis | Where do you expect the highest risks to lie, and why? (Write this before your deep analysis — it is your prior.) |

Submit the proposal for instructor approval before proceeding. Systems that are too generic, inaccessible to public analysis, or outside the course scope will be redirected.

**Stage 1 checkpoint:** By the end of Stage 1, you have a 1-page approved proposal, an evidence folder with at least 5 sources, and a preliminary hypothesis in writing.

---

## Stage 2: Systematic Risk Analysis (due week 13)

Apply your chosen framework to the system in full. Every major framework step or category must produce a specific, evidenced finding. "No information available" is an acceptable finding if you have searched and documented your search; "the system is probably fine" is not.

**If using the NIST AI RMF**, complete all four functions and fill in this table:

| NIST Function | Key Questions | Your Findings (with evidence citations) |
|---|---|---|
| **GOVERN** | Who is accountable? What policies govern the system? What is the organizational context? | |
| **MAP** | What is the system's purpose, context of use, and affected populations? What are the reasonably foreseeable risks? | |
| **MEASURE** | What metrics or tests assess the system's trustworthiness? What evidence exists about actual performance, including on demographic subgroups? | |
| **MANAGE** | What controls are in place? What is the incident response process? What are the residual risks? | |

**If using the EU AI Act**, classify the system's risk level (unacceptable, high, limited, or minimal) and assess compliance with the obligations that apply to that tier, with reference to Annex III for high-risk systems. Your classification must be argued, not asserted.

**If using the Montreal Declaration**, evaluate the system against each of the Declaration's ten principles. For each principle, provide: the finding (satisfies, partially satisfies, or does not satisfy) and a one-paragraph evidentiary basis citing a specific source.

**Document your analysis in a structured report (approximately 4 to 6 pages).** The report must include:
- What data the system uses and where it comes from
- Who is affected and how decisions reach them
- At least three specific failure modes with plausible mechanisms (not abstract risks)
- Who is accountable when something goes wrong, and what the accountability gap is if no one is

You are not expected to have access to the system's internals. Base your analysis on public documentation, news coverage, academic studies, regulatory filings, and the system's own published materials. Cite every claim with a specific source.

**Stage 2 checkpoint:** By the end of Stage 2, you have a 4-to-6-page risk analysis report with at least 8 citations, a completed framework mapping table, and at least 3 failure modes documented with mechanisms.

---

## Stage 3: Governance Recommendations (due week 14)

Produce a governance document (3 to 5 pages) that a real organization could adopt. Every recommendation must pass the third-party test: could an outside auditor determine, from evidence, whether the recommendation was followed? Every accountability assignment must name a role (not a department) and a timeline.

**Required sections:**

**1. Monitoring Plan**
Write 2-3 paragraphs. For each monitored metric, state: the metric name, the data source, the measurement frequency, the threshold that triggers review, and who is responsible for the measurement. Example: "Demographic parity ratio between ELL and non-ELL student scores, measured monthly on a random sample of 50 essays from each group, with review triggered if the ratio falls below 0.9. Owner: District AI Coordinator."

**2. Incident Response Procedure**
Write 2-3 paragraphs. Define what constitutes an incident (be specific — "unexpectedly low scores for a demographic group" is not an incident definition; "a demographic parity ratio below 0.8 on two consecutive monthly measurements" is). State: who is notified, in what order, within what timeframe, and who has authority to suspend the system.

**3. Stakeholder Communication Plan**
Produce a table:

| Stakeholder Group | What They Need to Know | How They Are Informed | Who Is Responsible |
|---|---|---|---|
| General public | | | |
| Directly affected individuals | | | |
| Regulators | | | |

**4. Appeal Process**
Write 2-3 paragraphs describing the process an individual who believes they were harmed by the system's decision can follow. State: how to initiate an appeal, who reviews it, what evidence the reviewer receives, what remedies are available, and the timeline from initiation to resolution. The process must be realistic — navigable by a person without a lawyer.

**Stage 3 checkpoint:** By the end of Stage 3, you have a 3-to-5-page governance document with a monitoring plan containing specific metrics and thresholds, a complete incident response procedure, a stakeholder communication table, and a navigable appeal process.

---

## Stage 4: Board Presentation (final class meeting)

Deliver a **15-minute presentation** to the class, which will role-play as the board of the organization operating the system. The board includes technical and non-technical members; assume they are intelligent, busy, and skeptical. They will ask where your findings came from.

**Required structure (timing is part of the grade):**

| Section | Time | What to Cover |
|---|---|---|
| What the system does and who uses it | 2 minutes | Plain English only. No jargon without definition. |
| Who is at risk and how | 3 minutes | Include at least one concrete, realistic example of an individual who could be harmed |
| What you found, organized by severity | 5 minutes | Lead with the most serious finding. Cite your source for each finding when asked. |
| What you recommend, in priority order | 3 minutes | State the estimated effort (low / medium / high) and timeline for each recommendation |
| Questions | Remaining time | |

Non-technical language is required throughout. Every claim must be supportable — you may be asked where a finding came from, and "I read it somewhere" is not an acceptable answer.

**Prepare for these likely board objections:**
- "These risks are theoretical — we've been using this system for two years without a problem."
- "The vendor told us it was tested for fairness."
- "We don't have the resources to implement all of these recommendations."

Have specific, evidence-based responses to each.

---

## Deliverables Summary

Submit the following as a complete artifact package. The package should be organized so it could be handed to a regulator or compliance officer without modification — which means clear labels, complete citations, and no broken references.

1. **Proposal** (1 page, instructor-approved): system description, affected populations, framework choice and justification, preliminary hypothesis
2. **Risk analysis report** (4 to 6 pages): complete framework application, documented failure modes (with mechanisms), accountability mapping, all sources cited
3. **Governance document** (3 to 5 pages): monitoring plan with metrics and thresholds, incident response procedure, stakeholder communication plan, appeal process
4. **Presentation materials**: slides or equivalent visual aid, suitable for a non-technical board, including at least one concrete individual harm example
5. **Individual contribution statement** (if pair): one paragraph per person describing their specific contributions

---

## Frequently Asked Questions

**Q: Can I analyze an AI system I personally use, like a recommendation algorithm?**
A: Yes, if it meets the specificity requirement. "TikTok's recommendation algorithm as experienced by minors aged 13-17 in the US" is specific enough. "Social media algorithms" is not. The key test: can you name the operator, identify the affected population, and find enough public documentation to support your claims?

**Q: I cannot find information about how the system works internally. Can I still complete the analysis?**
A: Yes. You are not expected to have access to the system's internals. Some of the most important governance gaps (lack of documentation, opacity about training data, no published performance metrics) are themselves findings. Document what you searched for and what you found or did not find — the absence of information is analyzable.

**Q: My framework has 10 principles (Montreal Declaration) and analyzing all of them takes a lot of space. Is there a page limit?**
A: The 4-to-6-page estimate applies to a focused analysis. If your framework requires 10 sections, each section will be shorter. Prioritize depth over length: a 2-paragraph finding with a specific citation and a concrete mechanism is better than a 1-page finding that restates the principle.

**Q: The board presentation is 15 minutes, but I have too much to say. What should I cut?**
A: Cut methodology. The board does not need to hear how you applied the framework; they need to hear what you found and what to do about it. Lead with findings and recommendations. The methodology is in your written report if they want to check your work.

---

## Reflection Prompts

Answer individually in your submission:

- What was the hardest part of applying the framework to this system, and what does that difficulty reveal about the framework or the system?
- If your governance recommendations were adopted, which one do you think would make the most practical difference to affected individuals, and why?
- Did the analysis change your initial hypothesis about where the highest risks lay? If so, what changed your mind?
- Do you certify that your submission accurately represents your own work? Please identify any and all portions of your submission that were not originally written by you, including any AI-assisted writing.
- Approximately how many hours did the project take you personally (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
