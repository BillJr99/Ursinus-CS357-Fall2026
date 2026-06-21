---
layout: project
permalink: /Projects/ResponsibleAI
title: "CS357: Foundations of Artificial Intelligence - Project: Responsible AI Audit"

info:
  coursenum: CS357
  points: 100
  goals:
    - To apply a structured framework such as the NIST AI Risk Management Framework, EU AI Act risk categories, or the Montreal Declaration to a real AI system
    - To identify concrete risks and failure modes in a deployed AI system through systematic analysis
    - To propose governance measures, monitoring systems, and accountability structures appropriate to the system's risk level
    - To communicate findings to a non-technical stakeholder audience in language they can act on
  rubric:
    - weight: 20
      description: System Selection and Scoping
      preemerging: The selected system is too generic to analyze meaningfully, or no proposal is submitted
      beginning: A specific system is selected but the proposal does not identify who is affected, what the system decides, or why the framework chosen is appropriate
      progressing: The proposal identifies a specific system, its affected populations, and a rationale for the chosen framework; the scope is mostly well-defined though some key decisions or data flows are left unspecified
      proficient: The proposal identifies a specific, non-generic AI system with named affected populations, a clearly bounded scope of analysis, a well-reasoned choice of framework with justification for why it fits this system better than the alternatives, and at least one preliminary hypothesis about where the highest risks lie
    - weight: 25
      description: Risk Analysis and Framework Application
      preemerging: The chosen framework is not applied, or application is superficial name-checking without substantive mapping
      beginning: The framework is applied to some parts of the system, but major steps or categories are skipped and findings are not grounded in evidence about the actual system
      progressing: The framework is applied systematically with most steps completed; risks are specific to the system, though some findings lack evidentiary grounding or the framework mapping contains gaps
      proficient: The framework is applied completely and systematically; every major framework step or category produces a specific, evidenced finding about this system; data sources, affected populations, and accountability gaps are documented; at least three distinct failure modes are identified with plausible mechanisms, not just abstract risks; and the analysis distinguishes between risks that have materialized and risks that are foreseeable
    - weight: 25
      description: Governance Recommendations
      preemerging: No governance recommendations are provided, or recommendations are aspirational values without mechanisms
      beginning: Recommendations are present but are generic best practices not tailored to this system, or lack owners, timelines, or detection mechanisms
      progressing: Recommendations are specific to the system, with named owners and at least some monitoring mechanisms; the incident response and appeal process are present but underdeveloped
      proficient: The governance document provides a monitoring plan with specific metrics and thresholds, an incident response procedure with named roles and decision points, a stakeholder communication plan that distinguishes between affected parties and what each needs to know, and an appeal process that an affected party could actually navigate; every recommendation passes the third-party test and is traceable to a specific risk finding
    - weight: 15
      description: Stakeholder Communication
      preemerging: The stakeholder presentation is missing or is addressed to a technical audience
      beginning: A presentation is provided but uses technical language that a non-specialist board could not act on, or fails to convey the key risks and recommendations
      progressing: The presentation is largely accessible to a non-technical audience; the key risks and top recommendations are communicated clearly, though some passages lapse into jargon or the narrative logic is unclear
      proficient: The presentation is fully accessible to a non-technical stakeholder audience, conveys what the system does, who is at risk, what was found, and what is recommended in a logical sequence that moves from evidence to action, anticipates and addresses likely board objections, and is completable in fifteen minutes
    - weight: 15
      description: Presentation and Artifacts
      preemerging: The presentation and artifact package are missing or substantially incomplete
      beginning: A presentation is delivered but without a rehearsed structure; the artifact package is incomplete
      progressing: The presentation is organized and delivered within the time limit; the artifact package contains most required documents though some are incomplete
      proficient: The presentation is delivered within the time limit with a clear narrative arc, a visual aid that a board member could refer to afterward, and at least one concrete example of a real person who could be harmed by the system; the artifact package is complete, organized, and could be handed to a regulator or compliance officer without modification

tags:
  - final-project
  - ethics
  - governance
  - responsible-ai

---

# Overview

This project is an alternative final project track for students more interested in governance, policy, and ethics than in building AI systems. Instead of constructing an agent team, you will perform a structured **responsible AI audit** of a publicly available AI system — the kind of analysis that is increasingly required by regulation, expected by investors, and demanded by affected communities.

The deliverable is not an opinion piece. It is a structured, evidenced analysis using an established framework, culminating in a governance document that a real organization could adopt and a presentation that a real board could act on.

This project may be completed individually or in pairs. If completed in pairs, the presentation must have both members presenting, and the final report must include individual contribution statements.

---

## Stage 1: Proposal (due week 11)

Select a publicly available AI system. The system must be specific: not "a chatbot" but a named, deployed system with a defined purpose and identifiable affected populations. Strong candidates include:

- A **hiring screening tool** that ranks or filters job applicants
- A **medical imaging AI** used to flag or diagnose conditions
- A **content moderation system** that removes or demotes posts
- A **predictive risk tool** used in criminal justice, child welfare, or benefits eligibility
- An **educational AI** that grades, places, or recommends interventions for students

Avoid general-purpose chatbots unless you scope to a specific deployment context (for example, a school district's licensed deployment of an AI writing assistant).

Your one-page proposal must include:

- The system's name, operator, and a brief description of what it does and where it is deployed
- Who is directly affected by the system's decisions, and how
- Which framework you will apply (NIST AI RMF, EU AI Act risk categories, or the Montreal Declaration for Responsible Development of AI) and a three-sentence justification for why this framework fits this system
- A preliminary hypothesis: where do you expect the highest risks to lie, and why?

Submit the proposal for instructor approval before proceeding. Systems that are too generic, inaccessible to public analysis, or outside the course's scope will be redirected.

---

## Stage 2: Systematic Risk Analysis (due week 13)

Apply your chosen framework to the system in full.

**If using the NIST AI RMF**, complete all four functions:
- **GOVERN**: Who is accountable? What policies govern the system? What is the organizational context?
- **MAP**: What is the AI system's purpose, context of use, and affected populations? What are the reasonably foreseeable risks?
- **MEASURE**: What metrics or tests are used to assess the system's trustworthiness? What evidence exists about actual performance, including on demographic subgroups?
- **MANAGE**: What controls are in place? What is the incident response process? What are the residual risks?

**If using the EU AI Act**, classify the system's risk level (unacceptable, high, limited, or minimal) and assess its compliance with the obligations that apply to that tier, with reference to Annex III for high-risk systems.

**If using the Montreal Declaration**, evaluate the system against each of the Declaration's ten principles, with a finding (satisfies, partially satisfies, or does not satisfy) and a one-paragraph evidentiary basis for each.

Document your analysis in a structured report (approximately four to six pages). The report must include: what data the system uses and where it comes from, who is affected and how decisions reach them, at least three specific failure modes with plausible mechanisms, and who is accountable when something goes wrong.

You are not expected to have access to the system's internals. Base your analysis on public documentation, news coverage, academic studies, regulatory filings, and the system's own published materials. Cite every claim.

---

## Stage 3: Governance Recommendations (due week 14)

Produce a governance document (three to five pages) that a real organization could adopt. The document must include:

1. **Monitoring plan**: What metrics will be tracked, at what frequency, with what thresholds that trigger review?
2. **Incident response procedure**: What constitutes an incident? Who is notified, in what order, within what timeframe? Who has authority to suspend the system?
3. **Stakeholder communication plan**: Which affected parties need to know what, and in what form? Distinguish between the general public, directly affected individuals, and regulators.
4. **Appeal process**: How can an individual who believes they were harmed by the system's decision challenge that decision? Who reviews the appeal? What remedies are available?

Every recommendation must pass the third-party test: could an outside auditor determine, from evidence, whether the recommendation was followed? Every accountability assignment must name a role (not a department) and a timeline.

---

## Stage 4: Board Presentation (final class meeting)

Deliver a fifteen-minute presentation to the class, which will role-play as the board of the organization operating the system. The board includes technical and non-technical members; assume they are intelligent, busy, and skeptical.

Your presentation must cover, in order:
1. What the system does and who uses it (two minutes)
2. Who is at risk and how (three minutes) — include at least one concrete example of a real or realistic individual who could be harmed
3. What you found in the analysis, organized by severity (five minutes)
4. What you recommend, in priority order, with estimated effort and timeline (three minutes)
5. Questions (remaining time)

Non-technical language is required throughout. Jargon must be defined the first time it is used. Every claim must be supportable; you may be asked where a finding came from.

---

## Deliverables Summary

1. **Proposal** (one page): system description, affected populations, framework choice and justification, preliminary hypothesis
2. **Risk analysis report** (four to six pages): complete framework application, documented failure modes, accountability mapping, all sources cited
3. **Governance document** (three to five pages): monitoring plan, incident response, stakeholder communication plan, appeal process
4. **Presentation materials**: slides or equivalent visual aid, suitable for a non-technical board
5. **Individual contribution statement** (if pair): one paragraph per person describing their specific contributions

---

## Reflection Prompts

Answer individually in your submission:

- What was the hardest part of applying the framework to this system, and what does that difficulty reveal about the framework or the system?
- If your governance recommendations were adopted, which one do you think would make the most practical difference to affected individuals, and why?
- Did the analysis change your initial hypothesis about where the highest risks lay? If so, what changed your mind?
- Do you certify that your submission accurately represents your own work? Please identify any and all portions of your submission that were not originally written by you, including any AI-assisted writing.
- Approximately how many hours did the project take you personally (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
