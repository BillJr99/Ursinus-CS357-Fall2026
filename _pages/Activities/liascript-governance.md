<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-governance.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-governance.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Governance and Policy Writing

The *Intellectual Property, Privacy, and the Case for Local AI* activity mapped what is at stake; you have built agents that retrieve, decide, judge, and act; **governance** is the discipline of deciding, in advance and in writing, what they may do, who is accountable when they err, and how anyone would know.  Today you learn to *write* policy, a genre with teeth, because your final project requires a governance document and your careers will require many more.  Today we work from **what governance is $\rightarrow$ frameworks in the wild $\rightarrow$ the anatomy of an enforceable policy $\rightarrow$ drafting workshop**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Today culminates in a drafting workshop with structured peer review; bring your project's pre-mortem and data-flow audit, which become raw material.  After class, please respond to the reflective prompt on your own in your notebook.

---

### Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Governance** | The set of written rules, structures, and processes that decide what an AI system may do, who is accountable for its behavior, and how problems are detected and fixed, before harm occurs. | A university's policy stating that an AI advising tool may suggest course plans but may not register students for classes is a governance document. |
| **EU AI Act** | A 2024 European Union law that classifies AI systems by risk level and imposes different obligations depending on how much harm a system could cause, from bans on the most dangerous uses to transparency requirements for lower-risk ones. | An AI system used in college admissions falls in the Act's "high-risk" category and requires detailed documentation, human oversight, and accuracy testing. |
| **NIST AI RMF** | The National Institute of Standards and Technology AI Risk Management Framework, a voluntary US guideline that organizes AI risk work into four functions: Govern, Map, Measure, and Manage. | A team completing a pre-mortem (Map), running disaggregated evaluations (Measure), and assigning a named project owner (Govern) is implementing the NIST framework. |
| **Third-Party Test** | A practical check for whether a policy clause is real: could an independent outside party examine evidence and determine whether the clause was actually followed? If not, the clause is decoration, not policy. | "We will be fair" fails the test. "Every Friday the evaluation harness runs 40 tasks and any group accuracy gap above 5 points opens an incident" passes the test. |
| **Sunset Clause** | A provision in a policy that specifies when the policy must be revisited or when the system must be retired if conditions change, preventing outdated rules from governing a changed system indefinitely. | "This policy expires 12 months after deployment and must be renewed following a new impact assessment" is a sunset clause. |
| **Incident Response** | A documented procedure specifying exactly what steps are taken, by whom, and on what timeline when an AI system produces a harmful or unexpected output. | "Within 24 hours of a user harm report, the project owner disables the tool and opens a tracked issue; within 5 business days a root-cause analysis is posted" is an incident response process. |

---

# Part I: From Values to Mechanisms

In this part, you will learn to distinguish policy language that merely sounds good from policy language that actually commits someone to a specific, checkable action.  This is the single most important skill in this activity; everything else builds on it.

## 1.  Governance Is Engineering with Words

A value statement like "our system is fair and transparent" sounds meaningful but commits no one to any specific action.  Governance converts values into *mechanisms* that can actually be checked and enforced.  Think of it the same way you think about writing tests for code: a test that says "the function should work correctly" is useless; a test that says "given input X, output Y is returned within 200ms" is enforceable.  The same logic applies to AI governance policy.

A value is not a policy.  "Our agent is fair and transparent" commits no one to anything; a policy converts values into *mechanisms*: scopes, prohibitions, gates, logs, owners, and remedies.  The test of a policy clause is operational: could a third party determine, from evidence, whether it was followed?  Every clause failing that test is decoration.

**The risk-tiered pattern.**  Mature frameworks classify uses by risk and scale obligations accordingly.  The **EU AI Act** (a 2024 European law regulating AI systems by the potential harm they could cause) bans a small set of practices, imposes heavy obligations (documentation, human oversight, accuracy reporting) on "high-risk" systems such as those used in education admissions and grading, and lighter transparency duties elsewhere.  The **NIST AI Risk Management Framework** (a voluntary US guideline) organizes the work as four functions: *Govern* (assign accountability), *Map* (know your system and context), *Measure* (evaluate, disaggregate, monitor), and *Manage* (mitigate, respond, document).  Notice how much of NIST's *Measure* you can already execute: harnesses, disaggregated metrics, judge audits, citation checks.

Accountability has names in it.  Policies designate an owner per system, an escalation path, and an incident process.  "The team is responsible" means no one is.

---

## Model 1: Toothless Versus Enforceable

Why this matters: when you build a real AI system (even a class project) someone will eventually ask "who is accountable if this produces a harmful output?"  Learning to write clauses that survive the third-party test now prepares you to answer that question with documentation rather than apologies.

Clause A: "The advising agent should be used responsibly and its suggestions taken with appropriate caution."

Clause B: "The advising agent may draft degree-plan suggestions but may not submit registrations.  Every suggestion shown to a student must display the data sources used.  The CS department chair owns this system; suspected errors are reported via the form at [link] and acknowledged within 5 business days.  Logs of all suggestions are retained for one semester and audited each January against the disaggregation protocol in Appendix B."

### Critical Thinking Questions

1.  Apply the **third-party test** (could an independent outside party examine evidence and determine whether this clause was actually followed, without asking anyone to interpret what it means?) to each sentence of both clauses.  Which sentences are checkable from evidence, and which are not?

   *Hint: For each sentence, ask: if I gave this sentence to an outside auditor along with all of the system's logs, could they determine with certainty whether the clause was followed or violated?  If the answer requires judgment about what "responsible" means, the clause fails the test.*

2.  Identify in Clause B the scope, the prohibition, the transparency duty, the owner, the remedy, and the audit.  Which single element, if deleted, most weakens the rest?

   *Hint: Try removing each element one at a time and ask what breaks.  If there is no owner, who fixes problems?  If there is no audit, how does anyone know if the transparency duty is being met?  If there is no remedy, what incentivizes compliance?*

3.  Under the EU AI Act's logic, why would an advising agent that *recommends* differ in risk tier from one that *registers*?  Connect to the irreversible-action taxonomy you built in the tool-use module.

   *Hint: Think about what a student can do after a bad recommendation versus after a bad registration.  Can they undo it?  How much does it cost to fix?  How quickly must it be fixed to avoid serious harm?*

---

# Part II: The Anatomy of Your Policy

Now that you can distinguish real policy from decoration, this part gives you the structure for your project's governance document.  Every section has a specific job; if you can't fill a section, that gap tells you something important about your system design.

## 2.  The Eight Sections

A governance document is not a formality; it is an engineering artifact that specifies what your system does, who is accountable for it, and what happens when things go wrong.  Every section below earns its place because it answers a question that cannot be answered any other way.  If you cannot fill a section, that gap is itself a finding: something about your system is unspecified.

Your governance document (for the written assignment and your project) uses this skeleton, each section earning its place by the third-party test:

1.  **Purpose and scope**: what the system does, for whom, and explicitly what is out of scope.
2.  **System description**: agents, models, tools, data flows (your design table and audit, imported).
3.  **Permitted and prohibited uses**: concrete, with the prohibition list as specific as the permission list.
4.  **Human oversight**: which actions require confirmation, who confirms, and what the human sees before deciding.
5.  **Data handling**: what is collected, where it lives, how long it is retained, and which regulated categories it touches (FERPA, IRB).
6.  **Evaluation and monitoring**: metrics, disaggregation plan, audit schedule, and the harness that produces the data.
7.  **Accountability and incident response**: the owner by name or role, the reporting path, and response timelines measured in hours or days.
8.  **Review and sunset**: when the policy is re-examined and the conditions under which the system is retired.

A team writes: "Section 6: We will continuously evaluate the system for quality and bias."  The revision that survives the third-party test is:

[( )] "We will evaluate rigorously and transparently using best-practice methods."
[( )] "Evaluation is a core value of our team and we take it seriously."
[(X)] "Each Friday the harness in /eval runs the 40-item task set; per-group accuracy and judge-human agreement are posted to the repository; any group gap exceeding 5 points opens an incident."
[( )] "Users are encouraged to report problems and we will respond appropriately."

---

## Model 2: Frameworks Meet Your Project

### Critical Thinking Questions

4.  Map your project onto NIST's four functions: for each of Govern, Map, Measure, and Manage, name the artifact you have already produced this semester that does that work, and the one artifact still missing.

   > *Hint:* Govern = who owns this and what are they accountable for?  Map = what does the system do and who is affected?  Measure = how do you know if it's working or failing?  Manage = what do you do when something goes wrong?  Match each function to something you have actually built, written, or run this semester: your rubric pipeline, your pre-mortem, your data flow diagram, your test harness all count.

5.  Would your project be "high-risk" under the EU AI Act's education provisions if deployed for real students rather than a class demo?  What single design change most reduces its tier?

   *Hint: The EU AI Act's Annex III lists education systems that "determine access to, assignment to, or advancement of persons in educational institutions."  Does your system make, recommend, or inform any of those decisions?  If so, what would you remove or add to change that?*

6.  Your pre-mortem predicted a specification gap, an irreversible action, and a global invariant.  Write the policy clause (one sentence each) that addresses each prediction.

   *Hint: A specification-gap clause should say what happens when the agent encounters a request it was not designed to handle.  An irreversible-action clause should name the action, require human confirmation, and name the confirming party.  A global-invariant clause should specify what the system must always do (or never do) regardless of user instruction.*

> **Common Misconception:** "Governance is something we add after the system works."  Many teams treat governance documentation as a final step before submission, something to write once the code is done.  In practice, writing a governance document *first* surfaces design requirements you would otherwise miss: who is accountable forces you to define ownership; what is prohibited forces you to define scope; how you audit forces you to build the logging infrastructure.  Teams that write governance last typically discover they built an unsupervised, unauditable system.

---

# Part III: Drafting Workshop

> **Second half of today's session.**  After the drafting workshop we take up **[Environmental Impact and the Carbon Cost of Inference](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-environmentalai.md)**, which supplies the numbers your policy's sustainability section has to answer to.

Now that your policy has a structure and you've mapped your project onto real frameworks, this workshop turns those materials into actual written policy, and then tests it against peer review and adversarial reading.

## 3.  Exercises

1.  *Draft sections 3 and 4.*

   *What to do:* In class, write your project's permitted/prohibited uses and human-oversight sections in full, enforceable prose.  The Recorder types; everyone argues.

   *Starter hint:* For permitted uses, list specific tasks the system was designed for (e.g., "The agent may draft feedback comments on student code submissions").  For prohibited uses, be equally specific (e.g., "The agent may not assign grades, submit grades to the registrar, or send emails to students directly").  For human oversight, name every action that requires a human to see evidence and click confirm before proceeding.

   *You've succeeded when:* An outside auditor could read sections 3 and 4 and determine, from your system's logs, whether any violation occurred, without having to ask you what you meant.

2.  *Structured peer review.*

   *What to do:* Exchange drafts with another team.  Reviewers apply exactly two tests to every sentence: the third-party test, and the "who, specifically" test.  Return the draft with each failing sentence flagged.

   *Starter hint:* Mark every sentence that contains the words "we will," "the team," "regularly," "appropriately," or "as needed" as a likely failure.  These words almost always indicate that a specific actor, schedule, or threshold has been omitted.

   *You've succeeded when:* You return a draft with every vague clause flagged and a specific suggested revision for at least three of them, not just criticism but a concrete alternative.

3.  *Red-team the prohibition list.*

   *What to do:* For the other team's section 3, devise one use that violates the policy's *intent* while complying with its *letter*.  The drafting team must then close the gap.

   *Starter hint:* Look for underspecified actions.  If the policy says "the agent may not send emails," ask whether it can schedule emails, draft emails that a human then sends, or forward existing emails.  Each of these is a plausible gap.  Reward hacking, you will notice, is not only for models.

   *You've succeeded when:* You have identified a real gap (a use case that violates intent but passes a literal reading) and the drafting team has written a revised clause that closes it.

4.  *Incident drill.*

   *What to do:* Write the first three steps your team executes when a user reports your agent gave a harmful answer, with owners and timestamps.

   *Starter hint:* Step 1 should include who receives the report and within what time window they must acknowledge it.  Step 2 should specify what they do immediately (disable the system? preserve logs? notify a supervisor?).  Step 3 should specify what analysis is required and when it must be completed.  If you cannot name the owner, your section 7 is not done.

   *You've succeeded when:* A new team member who has never seen your project could read your three steps and execute them correctly in a real incident, without asking anyone for clarification.

---

## Reflection Prompt

*Personal:* Which of the four roles (builder, evaluator, auditor, policy author) felt most natural to you during this course?  Which felt most uncomfortable?

*Technical:* The governance document you are writing commits you, in writing, to specific evaluation schedules, data handling practices, and incident response times.  What would it mean to actually enforce those commitments on yourself and your team after the course ends?

*Societal:* The world is arguably most short of one of these four roles right now.  Which is it, and why?  Consider who currently writes AI governance policy for large organizations and whether those people have the technical background to make the third-party test meaningful.

---

## -> Coming Up Next

Next session, *The Environmental Cost of Inference*, supplies a section your governance document does not yet have: what the system costs to run, in energy and water, and what you are willing to commit to about it.  A policy that governs an agent's behavior and says nothing about its footprint is incomplete, and the numbers you work out next session are the ones that section needs.  Today's drafting also feeds Written Assignment 3 and the Responsible AI Capstone.

## Further Reading

- NIST. *AI Risk Management Framework 1.0* (2023, online), especially the Govern function.
- European Union.  *AI Act* (2024), Annex III on high-risk systems, including education uses.
- Your institution's acceptable-use and responsible-AI policies, read now with an author's eye.

---

# Extension: AI for Accessibility (self-paced)

Not assumed by the policy work above.  Accessibility is where AI's promise and its risk sit closest together: the same captioning, description, and simplification that opens a door can also encode a wrong assumption about the person using it at scale.  If your project touches a community partner with access needs, start here.

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Assistive technology** | Any device, software, or tool that helps a person with a disability perform tasks that might otherwise be difficult or impossible. | A screen reader that converts text on a website into spoken audio for a blind user. |
| **Disaggregated metrics** | Reporting accuracy or performance broken down by subgroup (e.g., by speaker accent), rather than as a single overall average that can hide unequal performance. | Reporting caption accuracy separately for speakers with dysarthria versus fluent speakers, rather than averaging them together. |
| **AAC (Augmentative and Alternative Communication)** | Communication methods and devices used by people who cannot rely on speech, ranging from picture boards to high-tech devices that speak for the user. | An iPad app that lets a non-speaking autistic person tap symbols to form sentences, which the device speaks aloud. |
| **WCAG (Web Content Accessibility Guidelines)** | A set of internationally recognized standards (published by the W3C) defining what makes web content accessible to people with a wide range of disabilities. | A rule requiring sufficient color contrast between text and background so users with low vision can read the page. |
| **Universal design** | The practice of building products and environments to be usable by the broadest possible range of people from the start, rather than retrofitting accessibility as an add-on. | Designing a ramp at a building entrance benefits wheelchair users, parents with strollers, and delivery workers alike. |
| **Nothing about us without us** | A principle from disability justice advocacy stating that people with disabilities must be included as decision-makers (not just as test subjects) in designing tools that affect them. | Inviting actual AAC users to co-design the phrase-prediction algorithm, rather than testing the finished product on them afterward. |

---

## The Opportunity and the Gap

In this part, you will examine both the benefits and the access risks of AI-powered accessibility tools, building the habit of holding both truths simultaneously that any ethical AI practitioner needs.

### Opportunity vs. Risk Matrix

AI-powered accessibility tools span a wide range of capabilities and populations.  Each entry below represents a real deployed or research application.  Notice that every row has both a real benefit and a real risk; the goal of this model is to hold both in mind simultaneously.

| Application | What AI Enables | Who Benefits Most | Access Risk | Quality Risk |
|---|---|---|---|---|
| **Real-time captioning** (e.g., Whisper, Otter.ai) | Automatic speech-to-text at near-human accuracy; live captions for deaf and hard-of-hearing users in real time, without a human transcriptionist. | Deaf and hard-of-hearing people; users in noisy or multilingual environments who struggle to follow audio. | Requires a fast internet connection; best performance is locked behind paid subscription tiers; offline mode is limited or absent. | Accuracy drops sharply on accented speech, speech affected by motor differences, or domain-specific vocabulary (medical terms, proper nouns). |
| **Image alt-text generation** (e.g., GPT-4V, BLIP) | Describes visual content in natural language, making it accessible to screen-reader users; scales to millions of images that would never receive human-written descriptions. | Blind and low-vision users who rely on screen readers to understand image-heavy web pages and social media. | Requires API access, which is embedded in assistive technology that often costs money; not available in every app. | May misdescribe images that depend on cultural context; may omit emotionally significant details a human describer would naturally include. |
| **Voice control and navigation** (e.g., Dragon, Voice Access) | Hands-free device and application control, replacing the mouse and keyboard entirely for navigation, dictation, and commands. | Users with motor impairments, repetitive strain injuries, limb differences, or other conditions affecting hand use. | Robust performance requires high-end hardware; accent sensitivity limits effectiveness for many users. | Recognition fails most on atypical speech patterns, which are often the speech patterns of the users who most urgently need hands-free input. |
| **Reading assistance** (e.g., natural language simplification, TTS) | Simplifies complex text; reads content aloud; supports users who struggle with dense written language for a variety of reasons. | Users with dyslexia, cognitive disabilities, emerging readers, and non-native English speakers. | Web-based tools require accounts; school-licensed tools are only available while enrolled at a participating institution. | Oversimplification can strip important nuance; simplification models are trained mostly on majority-style text and may handle specialized or cultural language poorly. |
| **AAC enhancement** (augmentative and alternative communication) | Predictive text and symbol suggestion for non-speaking users, enabling faster and more natural communication than unassisted letter-by-letter selection. | Non-speaking autistic users; users with ALS, cerebral palsy, or other conditions affecting speech production. | AAC devices themselves are expensive; AI-enhanced features often require ongoing subscription fees on top of device cost. | AI-predicted phrases may not reflect the individual user's voice, personal vocabulary, or communication style, replacing their authentic expression with a statistical average. |
| **Sign language recognition** | Translates sign language to text or speech in real time, enabling deaf signers to communicate directly with hearing non-signers without a human interpreter. | Deaf signers communicating in environments where interpreters are unavailable or unaffordable. | Requires good camera hardware and consistent lighting to function reliably; not integrated into most standard devices. | Most models are trained on a small number of signers and a single regional sign language; ASL models may fail on BSL, PSE, or regional ASL dialects. |

#### Questions to Work Through

1.  Across the six applications in Model 1, identify the single most consistent pattern in the "Access Risk" column.  What structural feature of how AI tools are distributed (not a technical limitation, but a business or infrastructure choice) creates this pattern?

   *Hint:* Look at what nearly every Access Risk cell has in common.  Is the barrier technical (the AI can't do it), or is it about how the tool is packaged and sold?

2.  The "Quality Risk" column for voice control notes that "the very users who most need the tool" face the highest error rates.  Explain specifically why training data composition causes this outcome.  What would a more equitable data collection process look like, and what would it cost?

   *Hint:* If most voice training data comes from fluent, accent-neutral speakers (because they're easy to recruit at scale), what does the model learn to recognize well, and what does it learn to recognize poorly?

3.  AAC users communicate through symbols, pre-programmed phrases, or letter boards, often building a personal vocabulary over years.  An AI that auto-completes their phrases based on majority-user patterns may predict fluently but inauthentically.  Why does this matter beyond minor inconvenience, and how does it connect to questions of identity and personal autonomy?

   *Hint:* If someone spent years building a set of phrases that express their humor, their interests, and their personality, and an AI replaces those phrases with generic predictions, what exactly has been lost?

Now that you have mapped where AI accessibility tools succeed and fail, Part II shows you why headline accuracy numbers can obscure the most important failures.

---

## The Training Data Gap

In this part, you will see how a technically accurate accuracy metric can hide serious inequity, a pattern that recurs across every domain where AI affects underrepresented groups.

### When Aggregate Accuracy Hides Inequity

Consider the following scenario.  A captioning AI achieves **99% word accuracy** across its full benchmark test set.  The company publishes this figure in its marketing materials and in a published paper.  A disability advocate argues the metric is insufficient.  Here is the data beneath the headline:

One of the most important lessons in AI evaluation is that an impressive overall number can hide serious failures for specific groups.  This is especially dangerous when the groups most harmed by the failure are the groups who most need the tool to work.

| Speaker Group | Test Set Proportion | Word Accuracy | What a 99% Headline Hides |
|---|---|---|---|
| Standard American English, no speech difference | 78% of test speakers | 99.5% accuracy, near-perfect. | This group dominates the test set, so its performance dominates the headline number. |
| Regional accent (Southern US, AAVE, etc.) | 12% of test speakers | 96.8% accuracy, noticeably lower but still often described as "good." | Errors cluster on culturally specific vocabulary and pronunciation patterns underrepresented in training. |
| Non-native English speaker | 7% of test speakers | 93.1% accuracy, approximately one error per sentence in continuous speech. | Non-native speakers are often excluded from training data collection entirely due to language and logistics barriers. |
| Speaker with dysarthria or other motor speech difference | 3% of test speakers | 84.3% accuracy, roughly one word in six is wrong, making captions difficult to follow. | This is the group for whom real-time captioning is most critical, and they experience the worst performance. |

The weighted average across these groups is approximately 99%, the headline number.  The group with the highest error rate (15.7% errors) is the group for whom captioning is not a convenience but a necessary communication bridge.

An AI caption generator achieves 98% word accuracy across all test speakers.  A disability advocate argues this metric is insufficient.  The most compelling reason is:

[(X)] The 2% error rate likely concentrates among speakers with speech differences, meaning the people who most need captions may face substantially higher error rates than the headline metric suggests
[( )] 98% accuracy is high enough that any remaining errors are distributed roughly equally across all speaker groups
[( )] The advocate's concern would only be valid if the tool had no human captioner fallback available
[( )] Word accuracy is a flawed metric because it counts every word equally, making it impossible to identify subgroup disparities

---

#### Questions to Work Through

4.  What would a *disaggregated* accuracy report look like in practice?  Define at least three speaker subgroups that should be reported separately in any captioning benchmark, and explain specifically why each one matters for the people who rely on the tool.

   *Hint:* Consider subgroups defined by hearing status, speech production differences, native language, and regional dialect.  For each, ask: does this group have fewer alternative communication options if the tool fails?

5.  The model in question was trained on 78% standard-accent data because that data was easiest to collect at scale.  Propose a concrete data collection strategy that would improve representation of speakers with dysarthria.  What obstacles would you face, and which require technical solutions versus policy or community partnership solutions?

   *Hint:* Consider who you would need to partner with, how you would compensate participants fairly, how you would handle the extra annotation time required for atypical speech, and how you would ensure participants retain rights over their voice data.

6.  The principle "nothing about us without us" originates in disability justice advocacy.  It demands that disabled people be included as decision-makers, not just as test subjects, in the design of tools intended to serve them.  What would this require of a team building a new captioning AI? Name two specific decisions in the design process where inclusion of users with disabilities would change the outcome.

   *Hint:* Think about decisions made early in a project) what to optimize for, how to define "good enough," which error types to prioritize reducing (and how those decisions might differ if disabled users were in the room when they were made.

---

> **Common Misconception:** "A high accuracy number means the system works well for everyone."
>
> Aggregate accuracy metrics can be mathematically accurate and deeply misleading at the same time.  If 78% of your test set performs at 99.5% accuracy, that group will dominate any weighted average, even if a minority group experiences 84% accuracy.  In accessibility contexts, the groups with the worst performance are often the groups with the fewest alternatives.  Reporting only the aggregate number is not just a statistical oversight; it is a choice about whose experience counts.

Understanding who gets left out by training data gaps sets up the design question in Part III: how do we build AI interfaces that do not recreate those gaps by accident?

---

## Universal Design and the AI Interface

In this part, you will audit a generic AI interface against real disability contexts, connecting the "nothing about us without us" principle to concrete engineering choices.

### Accessibility Audit of a Generic AI Chat Interface

Universal design means building for the broadest range of users from the start, not adding accessibility as an afterthought.  The principle is captured well by the ramp analogy: a ramp built into a building's entrance from day one serves wheelchair users, parents with strollers, and delivery workers, while a ramp bolted onto the side six months later is more expensive, harder to reach, and signals that some users were an afterthought.

Below are five concrete design choices in a typical AI chatbot interface, evaluated across different disability contexts.

| Design Choice | Default Implementation | Impact on Keyboard-Only Users | Impact on Screen Reader Users | Impact on Users with Cognitive Disabilities | Impact on Users with Motor Impairments |
|---|---|---|---|---|---|
| **Response timeout** | Session times out after 5 minutes of inactivity; the user must re-authenticate from scratch. | Neutral, keyboard-only users can type quickly enough. | May lose all context if the session expires while the user is navigating the response with a screen reader. | Very harmful: users who need more time to read and process a response lose their work and must start over. | Harmful: users who type slowly or use switch access may regularly hit the timeout mid-response. |
| **Font and layout** | 14px sans-serif, low-contrast gray text on a white background, densely packed UI elements. | Neutral: font rendering doesn't affect keyboard navigation. | Irrelevant to screen reader users, who hear the DOM read aloud rather than seeing the visual layout. | Harmful: low contrast and dense layout increase cognitive load and make the interface harder to parse. | Neutral: motor impairments don't affect visual perception of the interface. |
| **Keyboard navigation** | Tab order follows visual layout; some interactive elements (e.g., copy buttons) are not reachable by keyboard. | Harmful: non-linear tab order causes disorientation; some functions are completely unreachable. | Harmful: focus management is lost after the AI's response appears; the screen reader cursor is stranded. | Neutral: keyboard navigation doesn't inherently affect cognitive load. | Harmful: a poor tab order requires many extra keystrokes to reach common functions. |
| **Response length** | The AI produces verbose multi-paragraph responses by default, with no option to request a shorter version. | Neutral: keyboard users can scroll without extra effort. | Harmful: the screen reader reads the entire response aloud before the user can interrupt or skip ahead. | Harmful: long responses overwhelm working memory; users may lose track of the question they originally asked. | Harmful: longer responses require more navigation to reach the input field for a follow-up. |
| **Audio feedback** | No audio confirmation when a message is sent or when a new response appears. | Neutral: keyboard users can see the response appear visually. | Neutral: the screen reader automatically announces DOM changes when a response arrives. | Helpful for some users who benefit from multimodal confirmation; harmful if the sound is non-dismissible. | Helpful: confirms that an action succeeded without requiring the user to visually scan the screen. |

#### Questions to Work Through

7.  The Web Content Accessibility Guidelines (WCAG) 2.2 define four principles for accessible interfaces, known as **POUR**: **Perceivable** (users can perceive the content), **Operable** (users can operate the interface), **Understandable** (users can understand content and UI behavior), and **Robust** (content works reliably with assistive technologies).  For each row in Model 3, identify which WCAG POUR principle the design choice most directly affects and explain your reasoning.

   *Hint:* Font contrast is primarily a Perceivable issue (can the user detect the content?).  Keyboard navigation is primarily an Operable issue.  Think about what each design choice prevents users from doing.

8.  The "response timeout" row reveals a real tension between security (idle sessions should expire to prevent unauthorized access) and accessibility (some users need more time).  This is a real values conflict, not a technical limitation.  How would you resolve it?  Name a specific design pattern that preserves both values simultaneously.

   *Hint:* Consider solutions like warning the user before timeout with enough notice to respond, offering a re-authentication that doesn't require re-entering all context, or using activity signals beyond typing (e.g., mouse movement, keyboard focus) to detect engagement.

9.  Whose responsibility is it when an AI accessibility tool fails: the developer of the underlying AI model, the organization that deployed it, or the AI company that provides the API? Construct a brief argument assigning primary responsibility to each of the three parties, then state which argument you find most convincing and why.

   *Hint:* Think about who made each decision: who chose the training data?  Who chose to deploy without testing with disabled users?  Who controls the API's output quality?  Does responsibility depend on who had the most information and the most power to change the outcome?

10.  The concept of *ableism* refers to discrimination and social prejudice against people with disabilities, including the assumption that a non-disabled way of interacting with the world is the natural default.  Identify one design decision in a typical AI system (not necessarily one listed in Model 3) that reflects an ableist assumption.  Propose a concrete alternative design that does not make that assumption.

    *Hint:* Think about defaults: what does the system assume about how fast a user reads, how a user inputs text, or what a "normal" interaction looks like? Any default that works for a non-disabled user but creates friction for a disabled user is worth examining.

---

### Exercises

1.  *Accessibility audit.*

   *What to do:* Choose any publicly available AI-powered tool (a chatbot, a caption generator, an image describer, or another tool of your choice).  Using only a keyboard) no mouse (and, if possible, a screen reader (NVDA on Windows, JAWS, or VoiceOver on Mac/iOS), attempt to complete one full task with the tool.  Document every point where the interface failed, required workarounds, or produced an error.  Write a one-page audit report organized around the WCAG POUR principles.  Compare your findings to the tool's published accessibility statement, if one exists.

   *Starter hint:* On a Mac, enable VoiceOver with Command + F5.  On Windows, press Windows + Ctrl + Enter for Narrator, or download NVDA (free at nvaccess.org).  Start by navigating only with Tab, Shift+Tab, Enter, and arrow keys.  Note every moment where you are uncertain where focus is, where a button has no label, or where content appears without your screen reader announcing it.

   *You've succeeded when:* Your audit report names at least three specific interface failures, maps each to a WCAG principle, and compares at least one finding to what the tool's accessibility statement claims about that feature.

2.  *Disaggregated evaluation design.*

   *What to do:* Design an evaluation protocol for a reading-assistance AI that simplifies complex text for users with cognitive disabilities or dyslexia.  Specify: (a) how you would recruit a representative sample of participants, (b) what metrics you would collect beyond aggregate accuracy, (c) how you would structure and report results so that subgroup differences are visible rather than averaged away, and (d) what threshold would constitute "good enough" performance, and who should have the authority to decide that threshold.

   *Starter hint:* Think about recruiting through disability advocacy organizations, university disability services offices, and community groups, not just general survey platforms.  For metrics, consider comprehension scores (did users understand the simplified text?), preference ratings (did it feel natural?), and error rates by user subgroup.  For reporting, sketch a table with one row per subgroup, not just an overall average.

   *You've succeeded when:* Your protocol includes at least three distinct participant subgroups, at least two metrics beyond aggregate accuracy, a reporting structure that makes subgroup differences visible, and a written argument for who should set the "good enough" threshold and why.

3.  *Universal design proposal.*

   *What to do:* For your final project, identify three specific design choices in your agent's interface or output format that affect users with disabilities.  For each choice, describe (a) the current default behavior, (b) which users it disadvantages and why, and (c) a universally designed alternative that serves a broader range of users without removing functionality for anyone.  If your project has no user-facing interface (it is a pure backend API), describe three choices in your output format, API contract, or documentation that affect the accessibility of the system as a whole.

   *Starter hint:* If your agent returns long text outputs, consider: does it always return plain text, or can it return structured Markdown?  Does it always return the same length regardless of the question, or can users request a summary?  Does it return one monolithic paragraph or a bulleted list?  Each of these is a design choice with accessibility implications.

   *You've succeeded when:* All three proposals clearly identify a specific user group that is disadvantaged by the current default, and your proposed alternative improves their experience without creating new barriers for other users.

---

-> Coming Up Next: The neuro-AI ethics module examines how cognitive science shapes the way we build and evaluate AI systems, and what happens when the brain metaphors we borrow turn out to be misleading.
