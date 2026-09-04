---
layout: assignment
permalink: /Assignments/ResponsibleAIPractice
title: "CS357: Foundations of Artificial Intelligence - Written Assignment 3: Responsible AI in Practice"

info:
  coursenum: CS357
  purpose: "To apply responsible-AI analysis to one concrete artifact; a defended philosophical position, real documentation, an enforceable governance document, a regulatory mapping of a deployed system, or a quantified carbon audit, and to produce work precise enough that a deployer, regulator, auditor, or fellow practitioner could act on it."
  tilt:
    task: "Choose one direction and carry it out in full depth: argue whether machine understanding matters for deployment; write a datasheet and model card for a course system; author an enforceable governance document mapped to NIST and the EU AI Act; map a real deployed AI system onto the regulatory landscape; or audit the carbon cost of your own AI use and your project at scale."
    criteria: "One shared rubric covers all five directions, and I apply it, analysis quality, evidence and citation, connection to course systems and concepts, and communication for your audience.  The rubric below breaks it down in full."
  points: 100
  goals:
    - "To analyze an AI system, practice, or question through a responsible-AI lens (philosophical, documentary, governance, regulatory, or environmental) at a depth a practitioner could act on"
    - To ground every claim in specific evidence (cited passages, published research, framework provisions with article numbers, reference values with visible arithmetic, or empirical observations of real systems) deployed at the point in the argument where it is needed, not decoratively
    - To engage honestly with the strongest counterargument, unknown, loophole, or trade-off rather than dismissing it, and to arrive at a defended position or an enforceable, implementable artifact
    - To connect the analysis concretely to the systems and concepts of this course, the agents you have built, your final project design, and the frameworks studied in class
    - To communicate for a named audience (a CS357 peer, a deployer, an auditor, a regulator, or an engineering team) at the level of specificity that audience needs to make a decision
  rubric:
    - weight: 35
      description: Analysis Quality
      preemerging: The submission does not arrive at a position or produce the direction's central artifact, or the analysis restates sources and frameworks without applying them
      beginning: An analysis or artifact is present but superficial, claims are asserted rather than argued, framework sections are generic enough to describe any system, bias or risk discussion names no affected population or mechanism, or numbers appear without reasoning
      progressing: The analysis is substantive and mostly specific, a clear position with coherent argument, documentation or clauses specific to the chosen system, a defensible classification, or calibrated estimates, but the hardest element is underdeveloped (the strongest objection is not fully engaged, a mechanism or enforcement path is missing, or a trade-off is acknowledged without being analyzed)
      proficient: The analysis does the direction's hardest work fully, the strongest counterargument is stated fairly and answered; each bias risk names the affected group, the specific output behavior, and the likely mechanism; substantially every governance clause passes the third-party test and the "who specifically" test; the regulatory classification is argued item-by-item against the framework's actual categories; or both sides of the Jevons paradox are argued with evidence before a defended position, and the conclusion is specific enough that someone could reasonably disagree with it or an engineer could implement it
    - weight: 25
      description: Evidence and Citation
      preemerging: No sources, reference values, or framework provisions are cited, or cited sources are not real and retrievable
      beginning: Sources are cited decoratively, quoted in the introduction or conclusion, name-checked without mapping, or reference values used without showing the conversion steps
      progressing: Evidence is real and mostly deployed where needed, passages cited in the body of the argument, Annex III or NIST functions referenced with reasonable justification, arithmetic mostly visible, but at least one key claim rests on assertion, one framework citation lacks the specific provision, or one calculation omits its assumptions
      proficient: Every load-bearing claim is supported at the point it is made, at least two specific passages from the readings deployed inside the argument; published citations or the student's own empirical testing behind each bias or risk claim; specific articles, annex categories, and provisions cited by name; every estimate showing the reference value, the conversion steps, and the stated assumptions; every token figure labelled measured or estimated with the instrument or rule named, and never an estimate presented as a measurement; the amortized training term shown as an explicit division with its assumed lifetime-request denominator stated and defended, and the result restated under one alternative denominator; and every unknown item flagged with an explanation of what harm the absence of that information could cause
    - weight: 20
      description: Connection to Course Systems and Concepts
      preemerging: No connection is made to the systems built in this course, the final project, or the frameworks studied in class
      beginning: A connection is mentioned in passing, "this has implications for how we build AI", without specifying what those implications are for a specific system or design decision
      progressing: The analysis is connected to a named course system, project, or framework with a plausible implication, but the implication would follow from almost any analysis rather than specifically from this one, or existing course artifacts (design tables, pre-mortems, evaluation plans) are restated rather than built upon
      proficient: The analysis is anchored in the concrete systems and artifacts of this course, the essay closes with an implication that would change what a CS357 student does in their next project and would not follow from the opposing position; the documentation or governance document imports and extends the student's own design table, data-flow diagram, pre-mortem, or evaluation plan; the regulatory or environmental analysis traces specific consequences for the student's project or a system they have used, and names at least one specific design, deployment, or practice decision that changes as a result
    - weight: 20
      description: Communication for Audience
      preemerging: The submission is incomplete, disorganized, or written at a level its stated audience could not use
      beginning: The submission is complete but its genre conventions are not followed, the essay has no thesis until late, documentation sections are one-line bullets, clauses assign responsibility to "the team," tables contain single words without context, or required word counts and structures are ignored
      progressing: The submission follows its direction's genre and structure with all required sections, tables, and lengths, and is readable for its audience, with minor lapses in precision, formatting, or completeness
      proficient: The submission reads as a professional artifact of its genre, a thesis-first essay within the word limit that a CS audience without philosophy background can follow; documentation a deployer could act on without further research; a governance document an auditor could check against evidence; a compliance mapping a governance lead could file; or an environmental analysis whose arithmetic a reviewer could verify, including a three-condition table a reader could act on (condition, measured input tokens, measured output tokens, operational and training terms shown apart) and a stated shipping decision with its trade-off named, with every required section, table, and count present, all reflection prompts answered specifically, and any required disclosures, certifications, or appendices included
  readings:
    - rtitle: "Turing, Computing Machinery and Intelligence (1950)"
      rlink: "https://doi.org/10.1093/mind/LIX.236.433"
    - rtitle: "Searle, Minds, Brains, and Programs (1980)"
      rlink: "https://doi.org/10.1017/S0140525X00005756"
    - rtitle: "Weizenbaum, Computer Power and Human Reason (1976), Chapter 6"
      rlink: "https://archive.org/details/computerpowerhum00weiz"
    - rtitle: "Mitchell, Artificial Intelligence: A Guide for Thinking Humans (2019), Chapter 8"
      rlink: "https://melaniemitchell.me/aibook/"
    - rtitle: "The Philosophy and Psychology of Artificial Intelligence (Direction A: the positions this essay asks you to engage, laid out with the arguments for each)"
      rlink: "../Tutorials/PhilosophyAI"
    - rtitle: "Data Cards"
      rlink: "../Tutorials/DataCards"
    - rtitle: "Bias in Data Activity"
      rlink: "Activities/liascript-biasdata.md"
      liapage: true
    - rtitle: "Governance Activity"
      rlink: "Activities/liascript-governancecost.md"
      liapage: true
    - rtitle: "NIST AI Risk Management Framework"
      rlink: "https://www.nist.gov/itl/ai-risk-management-framework"
    - rtitle: "EU AI Act, Annex III"
      rlink: "https://artificialintelligenceact.eu/"
    - rtitle: "AI Regulation"
      rlink: "../Tutorials/Regulation"
    - rtitle: "Ethical Frameworks"
      rlink: "../Tutorials/EthicalFrameworks"
    - rtitle: "Strubell et al., Energy and Policy Considerations for Deep Learning in NLP (2019)"
      rlink: "https://arxiv.org/abs/1906.02629"
    - rtitle: "Patterson et al., Carbon Emissions and Large Neural Network Training (2021)"
      rlink: "https://arxiv.org/abs/2104.10350"
    - rtitle: "Luccioni et al., Power Hungry Processing: Watts Driving the Cost of AI Deployment?  (2023)"
      rlink: "https://arxiv.org/abs/2311.16863"
    - rtitle: "Jevons, The Coal Question (1865), Chapter 7 summary"
      rlink: "https://www.econlib.org/library/YPDBooks/Jevons/jvnCQ.html"

tags:
  - responsible-ai
  - philosophy
  - ethics
  - documentation
  - bias
  - transparency
  - governance
  - regulation
  - eu-ai-act
  - nist
  - environment
  - written

---

**See the course schedule for the assigned and due dates.**

By this point in the course you have built systems that answer questions, retrieve documents, call tools, and make or support decisions.  Responsible AI is what happens when you stop asking "does it work?" and start asking "should anyone rely on it, and on what terms?"  That question can be approached from five distinct angles: whether it matters that these systems genuinely understand anything; whether their data and behavior are documented honestly; whether their operation is governed by enforceable rules; whether they comply with the regulations that increasingly bind them; and what their energy and carbon cost really is.  Each direction below takes one of those angles and applies it to a **concrete artifact**, an essay defending a position, a datasheet and model card for a system you have used, a governance document for your own project, a regulatory mapping of a real deployed system, or a carbon audit of your own AI use.

Read all five directions before choosing, then pick **one** and carry it out in full depth.  The right choice is the angle you most want to be able to defend in your future practice, or the one that most directly serves your final project.  Do not attempt more than one; depth on one is worth far more than a shallow pass over several.  Your single 100-point grade is assessed with the shared rubric above, whose four dimensions (analysis quality, evidence and citation, connection to course systems and concepts, and communication for audience) apply to whichever direction you choose.

---

## Before You Start

**This builds on:** the *Training Data, Bias, and Explainability* session, *Intellectual Property, Privacy, and the Case for Local AI*, and *Governance, Policy, and the Cost of Inference*.  Each direction leans on a different one, and all three are taught before this is due.

**You need:** no code.  Direction E needs a week of your own AI usage logged, so **start the log the day this is handed out** even if you have not chosen a direction yet; it is the only part of this assignment you cannot do retroactively.  Direction E also reads token counts off your own requests, for which `files/agent-templates/deliberation-harness/tools/token_meter.py` in the course repository is a ready-made instrument; running it is a few lines and estimating instead is an accepted fallback, so this is still a no-code direction.

**Pace yourself:** Direction C's peer review round and Direction E's week-long audit both depend on the calendar and not only on your effort, so start those early.

**Choosing a direction**, honestly:

| Take | If |
|---|---|
| **A: Does It Matter If Machines Understand?** | You want to argue, you are willing to engage a position you disagree with on its own terms, and "it depends" is not where you want to end up |
| **B: Model Cards and Datasheets** | You want to document a real system precisely, and you would rather be exact than persuasive |
| **C: Governance and Policy** | Your final project has an agent team that will need governing anyway, and you would rather write that document once and use it twice |
| **D: Regulatory Landscape** | You want to know how this technology is actually being regulated, and you can pick a real deployed system to classify |
| **E: The Carbon Cost of Intelligence** | You want a number rather than an opinion, and you will actually keep the week-long log |

> **The most common way each direction fails.**  A: summarizing three positions and declining to hold one.  B: documentation that describes the system's intended use and never its misuse.  C: a policy with no enforcement path, which is a wish list.  D: classifying a system you cannot get real information about.  E: reconstructing the week's usage from memory at the end, which produces a number that is not a measurement.

---

## What a Strong Submission Looks Like

A strong submission, in any direction, has these qualities:

- **It arrives somewhere.**  "Both sides have merit" is not a position; "the system may exhibit bias" is not an analysis; "the team will monitor the system" is not a clause; "minimal risk" without checking Annex III is not a classification; a carbon number without visible arithmetic is not an estimate.  Strong work commits: a thesis someone could disagree with, a named group and mechanism, a clause an auditor could check, a tier argued item-by-item, a calculation a reviewer could reproduce.
- **Evidence appears where it is needed.**  A quotation in the introduction is decoration; a quotation deployed to support the specific claim being made in that paragraph is evidence.  The same goes for article citations, reference values, and published research.
- **The uncomfortable part is done honestly.**  Every direction has one: the strongest objection to your thesis, the unknowns in your datasheet, the loophole your peer reviewer found, the gap you can only infer from a company's silence, the best evidence against your Jevons position.  Proficient work engages it; weak work hides it.
- **It connects back to this course.**  You have built agents, written pre-mortems, and designed evaluation plans.  Strong submissions build on those artifacts and close with something a CS357 student would actually do differently in their next project.

---

## Choose One Direction

Complete **one** of the five directions below in full.  Expand your chosen direction for the full instructions.

- **Direction A: Does It Matter If Machines Understand?**  A 1000-1500 word argumentative essay engaging at least two named philosophical positions and arriving at a defended position with a concrete deployment implication.
- **Direction B: Model Cards and Datasheets**, real documentation (a Gebru et al. datasheet and a Mitchell et al. model card) for a system you have used in this course, plus a bias analysis and misuse scenarios with implementable controls.
- **Direction C: Governance and Policy**: an enforceable eight-section governance document for your final project's agent team, mapped onto the NIST AI RMF and the EU AI Act, and hardened by adversarial peer review.  Includes the Policy Clause Workshop used in the Governance and Policy Writing class session.
- **Direction D: Mapping a Real AI System to the Regulatory Landscape**: classify a real deployed AI system under the EU AI Act, map it onto the NIST AI RMF, identify the sector-specific rules it triggers, and build a structured risk register.
- **Direction E: The Carbon Cost of Intelligence**: a one-week personal AI carbon audit with measured token counts, an environmental analysis of your final project at scale including a measured three-condition comparison and the amortized cost of training the model, prioritized efficiency redesigns, and a defended position on the Jevons paradox.

<details markdown="1">
<summary><strong>Direction A: Does It Matter If Machines Understand?</strong></summary>

Long before large language models existed, philosophers argued over whether any machine could genuinely understand language, experience consciousness, or be held accountable for its actions.  Those arguments are no longer merely academic: whether or not the systems you build in this course "really" understand turns out to matter: for how we design them, deploy them, and what obligations we take on when we do.  Write a 1000-1500 word essay (excluding references) on **one** of the four prompts below.  Choose the prompt you find most interesting; the best essays come from writers who actually want to answer the question.

#### The Philosophers in Three Sentences Each

Please treat these summaries as starting points; they do not substitute for the readings:

- **Alan Turing (1950)** argues that "can machines think?" is too loaded to be useful and proposes a behavioral test: if a judge cannot distinguish the machine's conversation from a human's, the machine is, for practical purposes, thinking.  Behavioral indistinguishability suffices: we do not demand access to internal experience from other humans either.
- **John Searle (1980)** answers that behavioral indistinguishability is not sufficient for understanding.  His Chinese Room manipulates symbols by rule and produces fluent output while understanding nothing: syntax is not sufficient for semantics.  A system that passes the Turing Test might be doing exactly what the room does.
- **Joseph Weizenbaum (1976)**, creator of ELIZA, was disturbed by how readily users bonded with it.  His question is not whether machines *can* understand but what we *should* delegate to them: some activities (therapy, judgment, care) require genuine human understanding, and delegating them is a moral failure regardless of the machine's internal states.

> **Common Pitfall:** Turing is asking about behavioral indistinguishability; Searle about intentionality; Weizenbaum about appropriate delegation.  If you mix these up, your essay will argue past itself.  Define what you mean by "understanding" in your first paragraph and hold to that definition throughout.

#### The Prompts

- **Prompt A:** *"Searle's Chinese Room argument decisively shows that large language models do not understand language.  Even if that is true, does it matter for how we deploy them?"*  Engage Searle's original argument and at least one serious objection (the Systems Reply or the Robot Reply).  Then grant, for the sake of argument, that Searle is right: what follows for deployment?  Does a system need to understand in order to be useful, trustworthy, or dangerous?
- **Prompt B:** *"The ELIZA effect, the human tendency to anthropomorphize AI systems, is not a bug but a feature: it makes AI systems more usable and more effective.  Evaluate this claim."*  Engage Weizenbaum's original concern and the broader literature on anthropomorphism.  What does "more usable" mean, and for whom?  Identify the conditions under which each conclusion holds and why those conditions matter more than the others; do not simply say "it depends."
- **Prompt C:** *"If we cannot determine from behavior alone whether an AI system is conscious or sentient, what ethical stance should we take toward it?"*  Engage the problem of other minds as it applies to AI, and at least one framework for moral status (sentience-based, interests-based, relational).  Consider the asymmetry between the cost of wrongly treating a non-conscious system as conscious and the reverse.
- **Prompt D:** *"Accountability requires understanding.  Therefore, AI agents cannot be held accountable for their actions.  Evaluate."*  Engage what accountability requires (intent, understanding, or something else) drawing on at least one philosophical source and one deployment scenario where accountability arose (autonomous vehicle liability, content moderation errors, AI-assisted medical decisions).  Does the premise hold?  Does the conclusion follow?  Who *is* accountable if the agent is not?

#### Requirements

Whichever prompt you choose, your essay must:

1.  Engage with **at least two named philosophical positions or arguments**, with citation; sources must be real and retrievable.
2.  Connect the argument to **at least one concrete AI deployment scenario** (a real system, a realistic hypothetical, or a case from the news), substantively, not decoratively.
3.  **Arrive at a position.**  "Both sides have merit" is not a position; your conclusion must be a claim someone could reasonably disagree with.
4.  Close with **one implication for CS357 students**: one thing a student building or deploying an AI system should do differently because of the position you argue, specific enough that it would lead to a different decision than the opposing position would recommend.

#### How to Write It

Argue, don't summarize: every paragraph should present your thesis, present a position, object to it, evaluate the objection, or connect to deployment; if a paragraph merely describes what Turing or Searle said, cut it or transform it into analysis.  A suggested shape (deviate if your argument calls for it): introduction with thesis (~150 words); Position A with its strongest objection, evaluated (~250); Position B likewise (~250); your position, engaging the strongest argument on the other side (~200); practical implication (~100); conclusion (~100).  Do not conclude "it depends" unless you specify the conditions under which each conclusion holds and why they matter.  Do not use AI to generate your argument; an AI-generated philosophical essay looks like a competent summary with a hedge at the end, and the rubric rewards originality of position and reasoning.  You may use AI tools for brainstorming or grammar checking; if you do, note it at the end of your essay and describe how.

#### Direction A Deliverable

A single PDF: the essay, a references section (not counted in the word count), and the word count at the top of the first page.  In your reflection, name the dialectic move you made: which objection did you allow to threaten your thesis, and what changed as a result of taking it seriously?

</details>

<details markdown="1">
<summary><strong>Direction B: Model Cards and Datasheets</strong></summary>

Documentation is not bureaucracy; it is the primary mechanism by which future deployers, researchers, regulators, and users understand what an AI system is and is not designed for.  In this direction you write real documentation for a system you have actually used in this course.  Write every section for a reader who has never seen your system and cannot just "Google it."  "Unknown" is a legitimate answer, but it must be explained: unknown provenance is a red flag a deployer needs to investigate, so for each unknown, write down what harm could happen if the system is deployed without that information.

#### Part 1: Choose Your Subject (setup)

Select one documentation subject and state your choice in a one-paragraph subject description (100-150 words, naming the specific dataset and model, with one sentence on why you chose it):

1.  **A pretrained model you ran locally** (Llama 3, Mistral, Hermes, Phi-3, Gemma): write the datasheet for a training dataset it likely used (The Pile, RedPajama, Common Crawl) and the model card for the model itself.  Best if you can write from firsthand experience and cite the dataset's published research.
2.  **An agent you built in the course** (coding agent, MCP agent, RAG agent): write the datasheet for the data your agent accesses and a model card treating your agent system as the "model."
3.  **The RAG knowledge base from the RAG lab**: write the datasheet for the documents you indexed and a model card for the retrieval-augmented system.

Avoid a subject where you cannot answer at least 5 of the 7 datasheet sections with something more than "unknown."

#### Part 2: Datasheet for Datasets (Gebru et al.)

Write a datasheet addressing at least **6 of the 7 sections** below, answering the key Gebru et al. (2021) questions for each.  Minimum 500 words total; 2-4 substantive sentences per section, not one-line bullets.

- **Motivation:** For what purpose was the dataset created?  Who created it, and on whose behalf?  Who funded it?
- **Composition:** What do the instances represent?  How many are there?  Is there a label or target?  Does it contain data that might be considered confidential or sensitive?
- **Collection Process:** How was the data collected?  Directly observed, reported by subjects, or inferred?  Who collected it?
- **Preprocessing / Cleaning / Labeling:** What preprocessing was done?  Was the raw data saved and is it accessible?  Is the preprocessing software available?
- **Uses:** What tasks has it been used for?  What else could it be used for?  Does anything about its composition, collection, or preprocessing impact future uses?
- **Distribution:** How is it distributed?  When was it released, and under what license?  Were third parties involved?
- **Maintenance:** Who maintains it?  Is there an erratum?  Will it be updated, on what schedule?  Are older versions supported?

Flag at least 2 items across any section that are unknown or unverifiable, and explain why the absence of that information is a risk.  For well-known datasets, the original paper (search "[dataset name] datasheet") contains much of this; for your own RAG knowledge base or agent data, you are the creator; answer honestly about your own choices.

**Example, Motivation section for ImageNet (illustration only; use a different dataset):**
> *ImageNet was created to support large-scale visual object recognition research, by Fei-Fei Li and colleagues at Stanford with collection coordinated through Princeton, on behalf of the academic computer vision community, funded by the NSF, Google, and Microsoft Research.  It was designed as a research benchmark, not for commercial deployment, which matters for deployers, because ImageNet-pretrained models import assumptions baked in during academic benchmarking that may not hold outside the lab.*

#### Part 3: Model Card (Mitchell et al.)

Write a model card with **all** of the following sections; minimum 400 words total, with Ethical Considerations alone at least 150 words:

- **Model Details**: name, version, type, training date (if known), contact, license
- **Intended Use**: primary use cases, intended users, and **at least two specific out-of-scope uses** ("not intended for medical diagnosis" beats "not for high-stakes decisions")
- **Factors**: relevant groups (demographic, linguistic, domain) where performance may vary
- **Metrics**: what metrics evaluated the model, and why those
- **Evaluation Data**: what data was used, and whether it represents intended use
- **Training Data**: a summary that explicitly references your datasheet from Part 2 and notes at least one known gap identified there
- **Quantitative Analyses**: any disaggregated performance metrics you can find or infer (accuracy by language, technical vs. casual prompts in your own testing)
- **Ethical Considerations**: **at least 2 fully specified bias risks**: for each, name the affected group, describe the specific model output that exhibits the bias (e.g., "disproportionate use of masculine pronouns when completing sentences about surgeons regardless of context"), and explain the likely mechanism in terms of training-data distribution; support at least one with a published citation or your own empirical testing, and calibrate severity by describing the real-world context where it would cause harm
- **Caveats and Recommendations**: what deployers should know that isn't captured elsewhere; what monitoring is recommended

Do not start by asking "is this model biased?"  Start with: "Who uses this model, and in what contexts could its outputs disadvantage some users more than others?", then work backward to the mechanism.

#### Part 4: Unintended Use Analysis

Write approximately one page (400-500 words) identifying **3 realistic misuse scenarios**.  For each:

1.  **Describe the misuse:** who is the bad actor, what do they want, how do they use your model/agent?  Realistic beats theatrical: "a hiring manager deploys the model to screen resumes without disclosing AI use, violating state transparency laws" is more useful than a nation-state supervillain.
2.  **What in the documentation alerts a careful deployer:** point to the specific section and quote or paraphrase the warning.
3.  **Propose one control:** either (a) a technical control naming the mechanism (input filtering against a regex for HIPAA-regulated terms, rate limiting to N requests per user per hour, sandboxing) or (b) a policy control naming the enforcement mechanism (a terms-of-service clause requiring human clinical review before acting on any output, with a named audit role).

#### Common Mistakes

Writing "unknown" without naming the risk it creates; describing intended use without specific out-of-scope uses; treating the bias section as a checkbox (name the group, the output, and the mechanism, all three); theatrical misuse scenarios whose controls don't match; and ignoring the interaction between the two documents; if your datasheet identified a risk, it should reappear in the model card's Ethical Considerations or Caveats.

#### Direction B Deliverable

A single PDF or markdown document: subject description, datasheet, model card, unintended use analysis, and the shared reflection responses.  In your reflection, also address: model cards are voluntary, and a company that publishes a thorough card exposes weaknesses a more secretive competitor hides; what market incentive problem does this create, and how might it be solved (contractually, legally, or through standards)?  And: did writing the bias section change how you think about using the system yourself?

</details>

<details markdown="1">
<summary><strong>Direction C: Governance and Policy</strong></summary>

In this direction you author a governance document for your final project's agent team, the same document you will defend during your in-class governance discussion.  Every organization deploying AI is expected to have one, regulators increasingly require it, and a vague or aspirational governance document is worse than useless because it creates false confidence.  By the end you will know the difference between a value and a mechanism, and you will have written a document that could be handed to an auditor rather than framed on a wall.

#### The Two Tests

Apply these to every sentence before submitting; they are the same tests real compliance teams use:

- **The Third-Party Test:** Could an outsider determine, from evidence (logs, artifacts, outputs), whether this clause was followed?  If the answer is "only if they asked us," the clause fails.  Strong: "The system logs every agent invocation to `logs/agent_audit.jsonl` with a timestamp, agent name, input hash, and output hash; logs are retained for 90 days and reviewed weekly by the Evaluator role."  Weak: "The system will be monitored to ensure responsible use."
- **The "Who Specifically" Test:** Does every responsibility name a specific role (Coordinator, Evaluator, Scribe) rather than "the team" or "we"?  Diffuse responsibility means no one is responsible.  Strong: "If a user reports a harmful output, the Scribe notifies the Coordinator within 24 hours; the Coordinator investigates within 72 hours and either patches the system or escalates to the instructor."

#### Part 0: Policy Clause Workshop (Warm-Up)

> This workshop is run during the **Governance, Policy, and the Cost of Inference class session**; when that session says "see the Governance direction," this is the sub-section it means.  The workshop itself is an **in-class activity for everyone**: students in class that day complete it there regardless of which direction they choose, and doing so is credited as class participation.  **Only Direction C students** additionally submit the workshop artifact as part of this assignment; your instructor will provide brief written feedback on it before the full governance document is due.

**The Hospital Sepsis AI Scenario.**  Read this abbreviated incident report:

> A regional hospital deployed an AI clinical decision support tool to flag patients at high risk for sepsis.  It was validated at 87% accuracy on a 2019 pilot.  In production, nurses began treating the AI's "low risk" flag as authoritative, skipping their own assessments.  Eighteen months later, an internal audit found the tool performed at 62% accuracy for patients over 75 and for non-English-speaking patients.  Two sentinel events (serious patient harm) occurred.

**Your task (30 minutes):**

1.  **Identify two NIST AI RMF gaps** in the hospital's approach.  Map each to one of the four NIST functions (Map, Measure, Manage, Govern) and write one sentence explaining what that function would have caught.
2.  **Write one policy clause** (≤100 words) that would have prevented the primary failure, specifying **scope** (who and what it applies to), **requirement** (what must happen, specifically), **enforcement** (what happens if violated), and **exception** (one valid exception to prevent over-application).  Example format, from a different domain: *"Automated resume-screening tools shall flag all candidates rejected by the AI for human review before any rejection letter is sent.  Reviews shall be logged with the reviewer's name and reasoning.  Violations by hiring managers shall be escalated to the Chief People Officer within 48 hours.  Exception: internal transfer applications are exempt."*
3.  **Stress-test your clause:** identify one way it could be gamed (met in letter but not spirit) and write a one-sentence amendment that closes the gap.

#### Step 1: Author the Governance Document

Write approximately four to six pages covering all eight sections below.  Import, rather than restate, your existing artifacts from earlier work: your agent design table, data-flow diagram, pre-mortem table, and evaluation plan.  Governance is proportional to consequence, not complexity: a simple two-agent summarizer still needs all eight sections; they will just be shorter.

1.  **Purpose and Scope**: what this document governs, who it applies to, what it does not cover; the specific system, its enumerated intended use cases, and at least two explicit out-of-scope uses someone might mistakenly assume are permitted.
2.  **System Description**: the agent architecture: your design table (by reference or inclusion), the topology (pipeline, router, blackboard, planner, or hybrid) with a one-sentence rationale, and the model versions and temperature settings for each agent.
3.  **Permitted and Prohibited Uses**: at least three permitted uses (with conditions) and at least three prohibited uses, each with the reason **and the mechanism that enforces it**: not just a label.  Example mechanism: "Prohibited: processing transcripts containing protected health information.  Enforcement: the system checks the first 500 characters of any uploaded document against a regex for HIPAA-regulated terms; on a match, it refuses to process and directs the user to an appropriate tool."
4.  **Human Oversight**: every consequential or irreversible action in the system (apply the irreversible-action taxonomy from class), the human gate before each, the role responsible for the confirmation, and what information the human sees at the moment of decision.
5.  **Data Handling**: a data inventory; an explicit statement for each regulated category (health, financial, biometric, minors' data): either "this system does not process X" or the specific controls that apply; retention periods, access controls, and a deletion procedure with a timeline.
6.  **Evaluation and Monitoring**: the actual metrics from your evaluation plan (not "we will evaluate performance"), the disaggregation protocol (which subgroups are analyzed separately), the re-evaluation frequency, and the threshold at which a metric failure triggers review.
7.  **Accountability and Incident Response**: what constitutes an incident; at least two severity levels with distinct response timelines; a named role for each step of detection, reporting, and response; and a binding clause for **each** failure mode predicted in your pre-mortem (if a risk is accepted rather than mitigated, say so in your revision memo and why).
8.  **Review and Sunset**: the review schedule, who reviews, the conditions that trigger an immediate review (a new model version, a reported incident), and the condition under which the system is shut down.

Use this structural skeleton (you may add subsections but may not omit a numbered section):

```
# Governance Document: [System Name]

> **This page is Component 2 of the Responsible AI Capstone, not a separate assignment.** It has no deadline of its own. Its rubric contributes 100 of the capstone's 200 points, and it is submitted together with Component 1. See **[Responsible AI Capstone]({{ site.baseurl }}/Assignments/ResponsibleAI)** for the due date and the submission instructions.
>
> Your argument here must be grounded in the findings you produced in Component 1 - the audit you ran, not a study you read.


Version 1.0 | Date | Authors: [team members and roles]
## 1. Purpose and Scope        ## 5. Data Handling
## 2. System Description       ## 6. Evaluation and Monitoring
## 3. Permitted and Prohibited ## 7. Accountability and Incident Response
## 4. Human Oversight          ## 8. Review and Sunset
## Appendix A: NIST AI RMF Mapping
## Appendix B: EU AI Act Classification Argument
## Appendix C: Peer Review (verbatim)
## Appendix D: Revision Memo
```

#### Step 2: Map Your System to External Frameworks

**NIST AI RMF (Appendix A):** map your system onto all four functions, naming the specific artifact or activity in your project (a file, a log, a test, a human review step) that performs each of GOVERN (policies, culture, accountability), MAP (context, risk identification, affected populations), MEASURE (metrics, testing, trustworthiness assessment), and MANAGE (controls, incident response, residual risk).  "We GOVERN by having good norms" names nothing and earns nothing.

**EU AI Act (Appendix B):** argue your system's plausible risk tier if deployed for real users in an educational setting (unacceptable / high risk per Annex III / limited / minimal).  Name the tier, cite the specific Annex III category (or argue why none applies, engaging the education provisions: do not simply state "our system is low risk"), and name the obligation that would bind first if the system were deployed beyond the classroom.

#### Step 3: Peer Review and Red Team

Exchange your governance document with another team.  That team applies the third-party test to every sentence, flags failures, and finds **one loophole**, a way to use the system harmfully that is not explicitly prohibited or gated.  (Example loophole: prohibiting "processing medical records" but not "processing a diary entry that describes health conditions"; or gating email *sending* but not *drafting*, so a draft can be sent by accident.)  You will receive the same treatment.  Include: the peer review verbatim (Appendix C); the loophole quoted from their review; your patch showing the original clause alongside the revised clause; and a one-paragraph revision memo (Appendix D) explaining what the original clause permitted that it should not have, and how the patch closes it.

#### Direction C Deliverable

The governance document (four to six pages), committed to your project repository as `GOVERNANCE.md`, plus the Part 0 workshop, the peer review packet (review received verbatim, loophole patch, revision memo), and the shared reflection responses; submitted as a repository link plus PDF export, or a single combined PDF/ZIP. In your reflection, also address: which clause was hardest to make enforceable, and what does that difficulty reveal about the underlying value?  And: your incident-response section names an owner; if your system harmed a user tomorrow, would you want to be that owner, and what would change in your design if the answer is no?

</details>

<details markdown="1">
<summary><strong>Direction D: Mapping a Real AI System to the Regulatory Landscape</strong></summary>

In this direction you take the regulatory frameworks from class and apply them to a real, deployed AI system.  The goal is not to find a "bad" system to criticize, but to practice the rigorous thinking a compliance officer, auditor, or governance lead must perform: think like an auditor, stay close to publicly available evidence, and treat unknown information as data: if a company does not publish its model card, that absence tells you something about its Govern function, and you should say so explicitly.

> **Glossary:** The **EU AI Act** (in force from 2024) creates a risk pyramid) unacceptable -> high -> limited -> minimal (with obligations by tier.  **Annex III** lists the high-risk categories: biometric identification, critical infrastructure, education, employment, essential services (credit, insurance), law enforcement, migration, and administration of justice.  **GPAI** (general-purpose AI) models face a separate obligation tier, with additional obligations above a systemic-risk compute threshold.  The **NIST AI RMF** is voluntary in the US and organizes AI risk management into Govern, Map, Measure, and Manage.

> **Common Pitfall:** Classifying a system as "minimal risk" without actually checking Annex III. Many systems that look benign (a resume screener, a credit-scoring tool, a medical symptom checker) are explicitly listed as high-risk.  Work through the checklist item by item and show that you checked.  Also: the EU AI Act and GDPR are separate regulations with different obligations; your system may be subject to both.

#### Part 1: Select and Describe a System

Choose one real AI system currently deployed.  Good choices make or significantly influence decisions about employment, credit, education, healthcare, or justice (Annex III categories); are deployed in or by companies with EU operations; or use a foundation model that might qualify as GPAI. Rich examples: GitHub Copilot, Google Health AI / Med-PaLM, Workday Skills Cloud, COMPAS, ChatGPT Enterprise, an AI hiring screener (HireVue, Pymetrics).  A system with interesting regulatory ambiguity beats both the obviously high-risk and the obviously minimal-risk case; "a chatbot on a retail website" is hard to write 400 words about.

Write **two paragraphs** (200-250 words total): (a) what the system does and who the end users are; (b) what data it processes and what decisions it influences or makes.  Cite at least one primary source (company documentation, research paper, or investigative reporting).

#### Part 2: EU AI Act Classification

Classify the system using the risk pyramid, completing a tier table (Unacceptable / High / Limited / Minimal, with your system's fit argued in each row, see the spam-filter example pattern: "No; spam filtering does not appear in Annex III categories").  Justify your classification with:

1.  Direct reference to **Annex III** categories (for high risk) or the **GPAI provisions** (for foundation models): search the Act's text for your system's domain keyword (employment, credit, biometric) and work through the specific article
2.  An explanation if the system spans multiple tiers
3.  **Three specific compliance obligations** that would apply, with article citations (e.g., "Article 13 transparency: users must be informed they are interacting with an AI system")

If your system is a GPAI model, address the GPAI-tier obligations separately.  Approximately 350-450 words including the table.

#### Part 3: NIST AI RMF Mapping

Complete the following table for all four functions, basing the "likely does" column on publicly available information; documentation, model cards, press releases, lawsuits, academic papers.  Lawsuits and investigative journalism are often more informative than press releases.  If you find nothing for a function, write "no public evidence found", that itself is a finding worth analyzing, not a gap to hide.

| Function | What It Means | What the Developer Likely Does | One Gap You Can Infer | One Artifact That Would Fill the Gap |
|----------|--------------|-------------------------------|----------------------|-------------------------------------|
| Govern | Policies, accountability structures | | | |
| Map | Identify context, stakeholders, risks | | | |
| Measure | Define, collect, and interpret risk metrics | | | |
| Manage | Prioritize and act on risks | | | |

Example row (hypothetical customer-service chatbot): *Govern, has a published responsible-AI policy and a Chief AI Officer; gap, the policy does not specify who is accountable when the chatbot gives incorrect legal or medical information; artifact; a RACI chart naming the team responsible for flagging and reviewing high-stakes outputs.*  Plan 3-5 substantive sentences per row across the last three columns (400-500 words total).

#### Part 4: Risk Register

Write a structured risk register with exactly 5 rows:

| Risk ID | Risk Description | Likelihood (H/M/L) | Impact (H/M/L) | Regulatory Touchpoint | Proposed Mitigation |
|---------|-----------------|-------------------|----------------|----------------------|---------------------|

**Requirements:** at least one **technical** risk (model accuracy failure, adversarial attack), at least one **social/fairness** risk (disparate impact on a protected group), at least one **legal/compliance** risk (GDPR right to explanation, sector rule violation); every cell substantive, single words like "bias" or "high" will not earn proficient credit; and mitigations implementable, not generic.  "Ensure fairness" is not a mitigation; "run a quarterly disparate impact analysis broken down by gender and race, reviewed by the ethics board, with a remediation protocol triggered if the 4/5ths rule is violated" is.  Example row (AI hiring screener): *R-01, model trained on historical hiring data produces lower scores for candidates from HBCUs, creating disparate impact on Black applicants, H/H, EU AI Act Art. 10 (data governance); US EEOC adverse impact doctrine; annual adverse impact analysis by race and school type, with human review for any candidate within 5 points of the threshold.*

For each row, ask in order: What could go wrong?  Who is harmed and how seriously?  What existing law or standard already speaks to this failure mode?  If nothing does, that regulatory gap is itself worth noting.

#### Direction D Deliverable

A single PDF or markdown document containing all four parts, clearly labeled, with citations.  In your reflection, also address: if your system is deployed globally, which jurisdiction's rules govern it and how do conflicts get resolved (2-3 sentences)?  And: the NIST AI RMF is voluntary in the US: what market incentives (enterprise procurement, liability exposure, reputation) might cause a company to adopt it anyway, and what might cause them to ignore it (1 paragraph)?

</details>

<details markdown="1">
<summary><strong>Direction E: The Carbon Cost of Intelligence</strong></summary>

Every query you send to a language model consumes electricity, and electricity has a carbon cost that varies by model size, inference provider, and grid energy mix.  In this direction you measure that cost for your own behavior, analyze it for your final project, propose design changes that reduce it, and then grapple with the uncomfortable question of whether efficiency improvements actually reduce total energy use at all.  Throughout: calibrated reasoning over false precision: round to one or two significant figures, show your work, and state where the uncertainty lies.

#### Reference Values

| Operation | Approximate CO2eq |
|---|---|
| Single GPT-4-class query (cloud) | 0.001-0.01 g CO2eq |
| Single 7B local model query | 0.0001-0.001 g CO2eq |
| Training a large LLM (one run) | 280-550 tonnes CO2eq |
| Streaming video, 1 hour | 36 g CO2eq |
| Driving a gasoline car, 1 mile | 400 g CO2eq |
| A beef hamburger | 2,500 g CO2eq |

Every figure above is **operational**: the cost of serving the request.  A request also carries a share of the one-time cost of *training* the model that serves it, and that share is **additive**:

$$
\text{total per request} = \text{operational} + \frac{\text{training total}}{\text{assumed lifetime requests}}
$$

| Model class | Published training total | Assumed lifetime requests | Additive share per request |
|---|---|---|---|
| Commercial frontier (GPT-3 scale, hosted) | ~500 tonnes CO2eq (Patterson et al. 2021) | 1 x 10^12 | ~0.0005 g CO2eq |
| Offline open-weights (Llama 3 8B, local) | 390 tonnes CO2eq ([Meta's model card](https://github.com/meta-llama/llama3/blob/main/MODEL_CARD.md)) | 1 x 10^11 | ~0.004 g CO2eq |

Notice what that second row does.  A local request's *operational* cost is roughly a tenth of a hosted one, which is the usual argument for running locally, and its *training share* at these denominators is several times larger than its own operational cost.  The 8B model was cheaper to train and is amortized over far fewer requests, and the second effect is the bigger one.  Whether that holds depends entirely on the denominator, which nobody publishes.

> **The denominators are assumptions, not measurements.**  They are the largest source of uncertainty in this entire direction, and they are the one number you are expected to argue with rather than accept.  Run your figures under the denominators above and under one you defend yourself, report both, and say which way the conclusion moved.  A part that reports one number and hides the assumption inside it earns *progressing* at best.

> **A note on offsets.**  Meta states that 100 percent of the Llama 3 emissions above were offset by its sustainability program.  The table counts the emissions rather than the offset, for the reason the *Governance, Policy, and the Cost of Inference* activity gives: an offset shifts accounting responsibility without reducing the energy the training run consumed.  If you disagree, argue it; that is a legitimate position and it needs to be argued rather than assumed.

Pick a value within each range that matches your best estimate of model size and provider (lower end for smaller models or cleaner grids), and state which value you chose and why.

> **Common Pitfall:** Comparing AI energy use to a flight (a one-time event, ~1,000,000 g CO2eq) rather than a daily habit.  Your week of AI use probably emits between 1 and 50 g CO2eq; the flight comparison is technically accurate but deeply misleading.  Compare AI use to other daily-frequency activities (streaming, commuting, lunch) so the scale is meaningful.  The relevant question is what the habit costs at scale, over a year, across millions of users.

#### Part 1: Personal Carbon Audit (one week)

**Start logging on Day 1 of the assignment week**: real-time logs beat memory reconstruction, and a gap honestly acknowledged beats reconstructed data presented as complete.  For one full week, record every AI interaction: tool and model (if known), one-sentence task description, **input and output tokens**, whether those counts are measured or estimated, and cloud-hosted vs. local.  Expect 10-30 rows.

**Measure the tokens where the tool will tell you, and estimate them where it will not.**  Any request you make to your own Ollama returns `prompt_eval_count` and `eval_count`, and `files/agent-templates/deliberation-harness/tools/token_meter.py` reads them for you; many hosted APIs return an equivalent `usage` block.  A browser chat window will not tell you anything, and for those rows the old rule stands: estimate at roughly four characters per token, or use the word-length buckets (short: <50 words; medium: 50-200; long: >200) and convert.  **Add a column saying which each row is.**  A log that is half measured and says so is worth more than one that is uniformly estimated and does not admit it, and far more than one that presents estimates as measurements.

At the end of the week, estimate your total CO2eq using the reference values, **showing every conversion step**: "50 medium prompts × 0.005 g/query (GPT-4 midpoint, cloud) = 0.25 g CO2eq" earns proficient; "my AI use produced 2 g" earns beginning.  Then compute the CO2eq of three other activities from that same week that are comparable in frequency (commuting, streaming, meals) and write a one-paragraph reflection on what surprised you most.  Analysis and reflection: approximately 250-350 words, plus the log table as an appendix.

#### Part 2: Project Environmental Analysis

Analyze your final project agent team design through an environmental lens (approximately 400-500 words with visible arithmetic):

1.  **Per-session call count:** walk through a typical session step by step as if you were a user; every LLM call for routing, tool use, synthesis, or final response counts; estimate averages for conditional calls; note anything parallelized or cached.
2.  **Per-session CO2eq:** estimate using the reference values, stating every assumption (model size, provider, grid mix).
3.  **Annual projection at scale:** if 1,000 users each ran one session per day for a year, what is the total CO2eq?  Compare to a concrete real-world equivalent (flight hours, car miles, household electricity).
4.  **Hot spots:** identify and quantitatively rank the top three places where reducing calls, switching models, or changing architecture would have the largest impact, at least one should reflect a design choice your team could realistically change.
5.  **Three conditions, measured.**  Take one representative task from your project and run it three ways, changing nothing else: as a **verbose one-shot** prompt, as a **compressed** prompt (terse, article-free, same acceptance criteria), and as an **agentic loop** with tool calls across turns.  Report a four-column table: condition, measured input tokens, measured output tokens, and total g CO2eq with the operational and training terms shown separately.  Then answer in two or three sentences: which condition would you ship, and what are you giving up?

    Predict the ordering before you run it.  Input tokens should dominate in the loop, because every turn re-reads the conversation so far, and across $n$ turns that term grows with $n^2$ while output grows with $n$.  If your measurements contradict the prediction, report the measurements and work out why; that is a better result than a table that agrees with the theory.

#### Part 3: Redesign for Efficiency

Propose **three concrete, project-specific design changes** that reduce your project's footprint (approximately 350-450 words).  For each: name the change precisely ("cache the retrieval agent's output for identical queries within a 30-minute window"; not "use a smaller model," which is a category, not a recommendation); estimate the percentage reduction in CO2eq per session with reasoning; and analyze honestly what capability is sacrificed; if the answer is "none," explain why.  At least one change must involve model selection (a specific smaller model for a specific subtask) and at least one must involve system architecture (eliminating or batching calls).  Prioritize the three.  Start from your Part 2 hot spots and ask: "What would I give up by cutting this?"

#### Part 4: Jevons Paradox Analysis

In 1865, Jevons observed that more efficient steam engines did not reduce Britain's coal consumption (they increased it, because cheaper steam power grew demand faster than efficiency improved.  The pattern recurs: fuel-efficient cars led to more driving; efficient bulbs to more lighting.  The question for AI: if inference becomes more energy-efficient, does total AI energy use fall (each query costs less) or rise (cheaper queries mean more queries)?  Note the paradox is a claim about efficiency, price, and demand), market dynamics, not a moral argument; so state it precisely before arguing about it.

Write a structured analysis (approximately 500-600 words total):

- **For:** argue that efficiency gains *will* reduce total energy use.  This is harder than it looks: the naive version ignores demand.  Look for mechanisms that actually constrain total demand: regulatory caps, market saturation, substitution effects.
- **Against:** argue that rebound effects will consume the gains.  AI-specific evidence is abundant: inference costs have dropped dramatically since 2020, yet total AI energy use has grown substantially.
- **Your position** (at least 150 words): commit to a side, engage the strongest argument on the other side rather than dismissing it, and close with one concrete implication for how AI systems should be designed, deployed, or regulated.  "Both sides have merit" is not an answer.

#### Direction E Deliverable

A single PDF or markdown document containing all four parts, clearly labeled, with your one-week usage log as an appendix (a simple table is fine).

</details>

---

## Submission Instructions

Submit your chosen direction's deliverable as described inside that direction, together with your reflection responses.  State at the top of the first page which direction you chose.

---

## Reflection Prompts

Answer each of the following with a specific observation from this assignment (plus any direction-specific reflection questions listed in your chosen direction's deliverable section):

1.  **What was the uncomfortable part of your direction**, the objection that threatened your thesis, the unknown in your documentation, the loophole in your governance document, the gap you could only infer from silence, or the evidence against your Jevons position, and how did engaging it honestly change your submission?
2.  **What will you do differently in your next project because of this analysis?**  Name one specific design, deployment, documentation, or usage decision.
3.  If you used an AI tool for any part of this assignment (brainstorming, grammar checking, drafting), note it here and describe how you used it.  The analysis, argument, and writing must be your own.
4.  If collaboration with a buddy was permitted, did you work with a buddy on this assignment?  If so, who?  If not, do you certify that this submission represents your own original work?  Please identify any and all portions of your submission that were not originally written by you.
5.  Approximately how many hours did it take you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

## Self-Check Before You Submit

**Every direction**

- [ ] I picked one direction and went deep, rather than sampling several.
- [ ] Every claim about a real system is sourced, and every source resolves.
- [ ] The work is about a **specific** system, deployment, or question, not about AI in general.
- [ ] Real names and sensitive data are redacted.
- [ ] AI disclosure names what was AI-assisted and how I verified it.
- [ ] Hours reported.

**Direction A** — at least two named philosophical positions engaged on their own terms; a defended position, not a survey; a concrete deployment implication that would change what someone builds.

**Direction B** — a real datasheet and a real model card in the established formats; a bias analysis grounded in the actual training data or its documented absence; misuse scenarios with **implementable** controls, not aspirations.

**Direction C** — all eight sections present and enforceable; the NIST AI RMF and EU AI Act mappings argued rather than asserted; the peer review included **verbatim**; a revision memo saying what changed because of it.

**Direction D** — a real deployed system, named; an EU AI Act classification with the argument for it; the NIST mapping; sector-specific rules identified; a structured risk register with owners.

**Direction E** — a week of logged usage, logged **as it happened**, with every row marked measured or estimated; the project-at-scale analysis with its arithmetic shown, including the three-condition comparison and the training term under two denominators; efficiency redesigns prioritized by impact; a defended position on the Jevons paradox that engages the strongest counterargument.
