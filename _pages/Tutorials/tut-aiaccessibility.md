---
layout: default-standard
permalink: /Tutorials/AIAccessibility
title: 'CS357: Foundations of Artificial Intelligence - AI for Accessibility: Opportunity, Gaps, and Universal Design'
info:
  coursenum: CS357
  purpose: "To hold two truths at once: the same AI that opens a door for a person with a disability can also fail that person at scale, and you need to be able to tell which one is happening."
tags:
- accessibility
- ethics
- universal-design
---
# CS357: Foundations of Artificial Intelligence - AI for Accessibility: Opportunity, Gaps, and Universal Design

## Purpose

To hold two truths at once: the same AI that opens a door for a person with a disability can also fail that person at scale, and you need to be able to tell which one is happening.

## About This Tutorial

Accessibility is where the promise of AI and its risk sit closest together.  The same captioning, image description, and text simplification that opens a door for one person can also encode a wrong assumption about that person, and then repeat it for everyone like them.  This self-paced tutorial is not assumed by the governance activity.  If your project touches a community partner with access needs, start here.

You will work through three sections.  First, you map where AI accessibility tools succeed and where they fail.  Second, you see how a single headline accuracy number can hide the failures that matter most.  Third, you audit a typical AI chat interface against real disability contexts and connect the results to concrete engineering choices.

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

> **Why this matters:** An ethical AI practitioner needs one habit above all others: holding a tool's benefit and its harm in mind at the same time.  Accessibility tools make that habit easy to practice, because every one of them has a clear benefit and a clear failure mode sitting side by side.

### Opportunity vs. Risk Matrix

AI-powered accessibility tools cover a wide range of capabilities and populations.  Each row below is a real deployed or research application.  Every row has a real benefit and a real risk.  Read the table with both in mind, and notice which column the risks tend to fall in.

| Application | What AI Enables | Who Benefits Most | Access Risk | Quality Risk |
|---|---|---|---|---|
| **Real-time captioning** (e.g., Whisper, Otter.ai) | Automatic speech-to-text at near-human accuracy; live captions for deaf and hard-of-hearing users in real time, without a human transcriptionist. | Deaf and hard-of-hearing people; users in noisy or multilingual environments who struggle to follow audio. | Requires a fast internet connection; best performance is locked behind paid subscription tiers; offline mode is limited or absent. | Accuracy drops sharply on accented speech, speech affected by motor differences, or domain-specific vocabulary (medical terms, proper nouns). |
| **Image alt-text generation** (e.g., GPT-4V, BLIP) | Describes visual content in natural language, making it accessible to screen-reader users; scales to millions of images that would never receive human-written descriptions. | Blind and low-vision users who rely on screen readers to understand image-heavy web pages and social media. | Requires API access, which is embedded in assistive technology that often costs money; not available in every app. | May misdescribe images that depend on cultural context; may omit emotionally significant details a human describer would naturally include. |
| **Voice control and navigation** (e.g., Dragon, Voice Access) | Hands-free device and application control, replacing the mouse and keyboard entirely for navigation, dictation, and commands. | Users with motor impairments, repetitive strain injuries, limb differences, or other conditions affecting hand use. | Robust performance requires high-end hardware; accent sensitivity limits effectiveness for many users. | Recognition fails most on atypical speech patterns, which are often the speech patterns of the users who most urgently need hands-free input. |
| **Reading assistance** (e.g., natural language simplification, TTS) | Simplifies complex text; reads content aloud; supports users who struggle with dense written language for a variety of reasons. | Users with dyslexia, cognitive disabilities, emerging readers, and non-native English speakers. | Web-based tools require accounts; school-licensed tools are only available while enrolled at a participating institution. | Oversimplification can strip important nuance; simplification models are trained mostly on majority-style text and may handle specialized or cultural language poorly. |
| **AAC enhancement** (augmentative and alternative communication) | Predictive text and symbol suggestion for non-speaking users, enabling faster and more natural communication than unassisted letter-by-letter selection. | Non-speaking autistic users; users with ALS, cerebral palsy, or other conditions affecting speech production. | AAC devices themselves are expensive; AI-enhanced features often require ongoing subscription fees on top of device cost. | AI-predicted phrases may not reflect the individual user's voice, personal vocabulary, or communication style, replacing their authentic expression with a statistical average. |
| **Sign language recognition** | Translates sign language to text or speech in real time, enabling deaf signers to communicate directly with hearing non-signers without a human interpreter. | Deaf signers communicating in environments where interpreters are unavailable or unaffordable. | Requires good camera hardware and consistent lighting to function reliably; not integrated into most standard devices. | Most models are trained on a small number of signers and a single regional sign language; ASL models may fail on BSL, PSE, or regional ASL dialects. |

### Questions to Work Through

1.  Across the six applications in the matrix above, identify the single most consistent pattern in the "Access Risk" column.  What structural feature of how AI tools are distributed (a business or infrastructure choice, not a technical limitation) creates this pattern?

   *Hint:* Look at what nearly every Access Risk cell has in common.  Is the barrier technical (the AI cannot do it), or is it about how the tool is packaged and sold?

2.  The "Quality Risk" column for voice control notes that the users who most need the tool face the highest error rates.  Explain specifically why the composition of the training data causes this outcome.  What would a more equitable data collection process look like, and what would it cost?

   *Hint:* If most voice training data comes from fluent, accent-neutral speakers (because they are easy to recruit at scale), what does the model learn to recognize well, and what does it learn to recognize poorly?

3.  AAC users communicate through symbols, pre-programmed phrases, or letter boards, and they often build a personal vocabulary over years.  An AI that auto-completes their phrases from majority-user patterns may predict fluently but inauthentically.  Why does this matter beyond minor inconvenience, and how does it connect to identity and personal autonomy?

   *Hint:* If someone spent years building a set of phrases that express their humor, their interests, and their personality, and an AI replaces those phrases with generic predictions, what exactly has been lost?

Two things to remember from this section.  Nearly every access risk in the matrix is about cost, connectivity, or packaging rather than what the model can do, and nearly every quality risk falls hardest on the users the tool exists to serve.  The next section shows why headline accuracy numbers hide that second pattern.

---

## The Training Data Gap

> **Why this matters:** A single accuracy number can be mathematically correct and still hide serious inequity.  This pattern recurs in every domain where AI affects underrepresented groups, and captioning is the clearest place to see it.

### When Aggregate Accuracy Hides Inequity

A captioning AI reaches **99% word accuracy** across its full benchmark test set.  The company prints that figure in its marketing materials and in a published paper.  A disability advocate argues that the metric is insufficient.  The table below shows the data beneath the headline.

An impressive overall number can hide serious failures for specific groups.  That is most dangerous when the groups the failure harms most are the groups who most need the tool to work.

| Speaker Group | Test Set Proportion | Word Accuracy | What a 99% Headline Hides |
|---|---|---|---|
| Standard American English, no speech difference | 78% of test speakers | 99.5% accuracy, near-perfect. | This group dominates the test set, so its performance dominates the headline number. |
| Regional accent (Southern US, AAVE, etc.) | 12% of test speakers | 96.8% accuracy, noticeably lower but still often described as "good." | Errors cluster on culturally specific vocabulary and pronunciation patterns underrepresented in training. |
| Non-native English speaker | 7% of test speakers | 93.1% accuracy, approximately one error per sentence in continuous speech. | Non-native speakers are often excluded from training data collection entirely due to language and logistics barriers. |
| Speaker with dysarthria or other motor speech difference | 3% of test speakers | 84.3% accuracy, roughly one word in six is wrong, making captions difficult to follow. | This is the group for whom real-time captioning is most critical, and they experience the worst performance. |

The weighted average across these groups is about 99%, the headline number.  The group with the highest error rate (15.7% of words wrong) is the group for whom captioning is not a convenience but a necessary communication bridge.

An AI caption generator achieves 98% word accuracy across all test speakers.  A disability advocate argues this metric is insufficient.  Which of the following is the most compelling reason?

- The 2% error rate likely concentrates among speakers with speech differences, meaning the people who most need captions may face substantially higher error rates than the headline metric suggests
- 98% accuracy is high enough that any remaining errors are distributed roughly equally across all speaker groups
- The advocate's concern would only be valid if the tool had no human captioner fallback available
- Word accuracy is a flawed metric because it counts every word equally, making it impossible to identify subgroup disparities

<details markdown="1"><summary>Answer</summary>

The first option: the 2% error rate likely concentrates among speakers with speech differences, so the people who most need captions may face substantially higher error rates than the headline metric suggests.  A headline average says nothing about how the errors are distributed.  The second option assumes the distribution is even, which the table above contradicts.  The third option treats a fallback as an excuse for unequal performance.  The fourth option blames the metric, but word accuracy can identify subgroup disparities as soon as you report it per subgroup.

</details>

### Questions to Work Through

4.  What would a *disaggregated* accuracy report look like in practice?  Define at least three speaker subgroups that any captioning benchmark should report separately, and explain specifically why each one matters for the people who rely on the tool.

   *Hint:* Consider subgroups defined by hearing status, speech production differences, native language, and regional dialect.  For each, ask: does this group have fewer alternative communication options if the tool fails?

5.  The model in question was trained on 78% standard-accent data because that data was easiest to collect at scale.  Propose a concrete data collection strategy that would improve representation of speakers with dysarthria.  What obstacles would you face, and which of them need technical solutions versus policy or community partnership solutions?

   *Hint:* Consider who you would need to partner with, how you would compensate participants fairly, how you would handle the extra annotation time that atypical speech requires, and how you would ensure participants keep rights over their voice data.

6.  The principle "nothing about us without us" comes from disability justice advocacy.  It demands that disabled people be included as decision-makers, not just as test subjects, in the design of tools intended to serve them.  What would this require of a team building a new captioning AI?  Name two specific decisions in the design process where including users with disabilities would change the outcome.

   *Hint:* Think about decisions made early in a project (what to optimize for, how to define "good enough", which error types to prioritize reducing) and how those decisions might differ if disabled users were in the room when the team made them.

---

> **Common Misconception:** "A high accuracy number means the system works well for everyone."
>
> Aggregate accuracy metrics can be mathematically accurate and deeply misleading at the same time.  If 78% of your test set performs at 99.5% accuracy, that group will dominate any weighted average, even if a minority group experiences 84% accuracy.  In accessibility contexts, the groups with the worst performance are often the groups with the fewest alternatives.  Reporting only the aggregate number is not a statistical oversight; it is a choice about whose experience counts.

Two things to remember from this section.  A weighted average is dominated by whoever dominates the test set, so it tells you almost nothing about the smallest groups.  Report accuracy per subgroup, and pay closest attention to the subgroup with the fewest alternatives if the tool fails.  The next section turns to the design question: how do you build AI interfaces that do not recreate those gaps by accident?

---

## Universal Design and the AI Interface

> **Why this matters:** Universal design means building for the broadest range of users from the start, not adding accessibility as an afterthought.  The ramp analogy captures it: a ramp built into a building's entrance on day one serves wheelchair users, parents with strollers, and delivery workers alike, while a ramp bolted onto the side six months later costs more, is harder to reach, and signals that some users were an afterthought.  The analogy stops there, though.  An interface has many more "entrances" than a building, and each default you choose is one of them.

### Accessibility Audit of a Generic AI Chat Interface

The table below takes five concrete design choices in a typical AI chatbot interface and evaluates each one across four disability contexts.  Read it row by row.  Notice that the same default can be neutral for one group and very harmful for another.

| Design Choice | Default Implementation | Impact on Keyboard-Only Users | Impact on Screen Reader Users | Impact on Users with Cognitive Disabilities | Impact on Users with Motor Impairments |
|---|---|---|---|---|---|
| **Response timeout** | Session times out after 5 minutes of inactivity; the user must re-authenticate from scratch. | Neutral, keyboard-only users can type quickly enough. | May lose all context if the session expires while the user is navigating the response with a screen reader. | Very harmful: users who need more time to read and process a response lose their work and must start over. | Harmful: users who type slowly or use switch access may regularly hit the timeout mid-response. |
| **Font and layout** | 14px sans-serif, low-contrast gray text on a white background, densely packed UI elements. | Neutral: font rendering doesn't affect keyboard navigation. | Irrelevant to screen reader users, who hear the DOM read aloud rather than seeing the visual layout. | Harmful: low contrast and dense layout increase cognitive load and make the interface harder to parse. | Neutral: motor impairments don't affect visual perception of the interface. |
| **Keyboard navigation** | Tab order follows visual layout; some interactive elements (e.g., copy buttons) are not reachable by keyboard. | Harmful: non-linear tab order causes disorientation; some functions are completely unreachable. | Harmful: focus management is lost after the AI's response appears; the screen reader cursor is stranded. | Neutral: keyboard navigation doesn't inherently affect cognitive load. | Harmful: a poor tab order requires many extra keystrokes to reach common functions. |
| **Response length** | The AI produces verbose multi-paragraph responses by default, with no option to request a shorter version. | Neutral: keyboard users can scroll without extra effort. | Harmful: the screen reader reads the entire response aloud before the user can interrupt or skip ahead. | Harmful: long responses overwhelm working memory; users may lose track of the question they originally asked. | Harmful: longer responses require more navigation to reach the input field for a follow-up. |
| **Audio feedback** | No audio confirmation when a message is sent or when a new response appears. | Neutral: keyboard users can see the response appear visually. | Neutral: the screen reader automatically announces DOM changes when a response arrives. | Helpful for some users who benefit from multimodal confirmation; harmful if the sound is non-dismissible. | Helpful: confirms that an action succeeded without requiring the user to visually scan the screen. |

### Questions to Work Through

7.  The Web Content Accessibility Guidelines (WCAG) 2.2 define four principles for accessible interfaces, known as **POUR**: Perceivable (users can perceive the content), Operable (users can operate the interface), Understandable (users can understand content and UI behavior), and Robust (content works reliably with assistive technologies).  For each row in the audit table above, identify which POUR principle the design choice most directly affects and explain your reasoning.

   *Hint:* Font contrast is primarily a Perceivable issue (can the user detect the content?).  Keyboard navigation is primarily an Operable issue.  Think about what each design choice prevents users from doing.

8.  The "response timeout" row reveals a real tension between security (idle sessions should expire to prevent unauthorized access) and accessibility (some users need more time).  This is a values conflict, not a technical limitation.  How would you resolve it?  Name a specific design pattern that preserves both values at the same time.

   *Hint:* Consider warning the user before the timeout with enough notice to respond, offering a re-authentication that does not require re-entering all context, or using activity signals beyond typing (e.g., mouse movement, keyboard focus) to detect engagement.

9.  Whose responsibility is it when an AI accessibility tool fails: the developer of the underlying AI model, the organization that deployed it, or the AI company that provides the API?  Construct a brief argument assigning primary responsibility to each of the three parties, then state which argument you find most convincing and why.

   *Hint:* Think about who made each decision.  Who chose the training data?  Who chose to deploy without testing with disabled users?  Who controls the API's output quality?  Does responsibility depend on who had the most information and the most power to change the outcome?

10.  *Ableism* is discrimination and social prejudice against people with disabilities, including the assumption that a non-disabled way of interacting with the world is the natural default.  Identify one design decision in a typical AI system (not necessarily one listed in the audit table) that reflects an ableist assumption.  Propose a concrete alternative design that does not make that assumption.

    *Hint:* Think about defaults.  What does the system assume about how fast a user reads, how a user inputs text, or what a "normal" interaction looks like?  Any default that works for a non-disabled user but creates friction for a disabled user is worth examining.

Two things to remember from this section.  A default is a design decision, and every default assumes something about the user.  Universal design asks you to make those assumptions visible and to choose defaults that serve the widest range of people without taking anything away from anyone.

---

## Exercises

1.  **Accessibility audit.**

   *What to do:* Choose any publicly available AI-powered tool (a chatbot, a caption generator, an image describer, or another tool of your choice).  Using only a keyboard (no mouse) and, if possible, a screen reader (NVDA on Windows, JAWS, or VoiceOver on Mac/iOS), attempt to complete one full task with the tool.  Document every point where the interface failed, required a workaround, or produced an error.  Write a one-page audit report organized around the WCAG POUR principles.  Compare your findings to the tool's published accessibility statement, if one exists.

   *Starter hint:* On a Mac, enable VoiceOver with Command + F5.  On Windows, press Windows + Ctrl + Enter for Narrator, or download NVDA (free at nvaccess.org).  Start by navigating only with Tab, Shift+Tab, Enter, and the arrow keys.  Note every moment where you are uncertain where focus is, where a button has no label, or where content appears without your screen reader announcing it.

   *You've succeeded when:* Your audit report names at least three specific interface failures, maps each to a WCAG principle, and compares at least one finding to what the tool's accessibility statement claims about that feature.

2.  **Disaggregated evaluation design.**

   *What to do:* Design an evaluation protocol for a reading-assistance AI that simplifies complex text for users with cognitive disabilities or dyslexia.  Specify: (a) how you would recruit a representative sample of participants, (b) what metrics you would collect beyond aggregate accuracy, (c) how you would structure and report results so that subgroup differences stay visible rather than averaged away, and (d) what threshold would count as "good enough" performance, and who should have the authority to decide that threshold.

   *Starter hint:* Recruit through disability advocacy organizations, university disability services offices, and community groups, not just general survey platforms.  For metrics, consider comprehension scores (did users understand the simplified text?), preference ratings (did it feel natural?), and error rates by user subgroup.  For reporting, sketch a table with one row per subgroup, not just an overall average.

   *You've succeeded when:* Your protocol includes at least three distinct participant subgroups, at least two metrics beyond aggregate accuracy, a reporting structure that makes subgroup differences visible, and a written argument for who should set the "good enough" threshold and why.

3.  **Universal design proposal.**

   *What to do:* For your final project, identify three specific design choices in your agent's interface or output format that affect users with disabilities.  For each choice, describe (a) the current default behavior, (b) which users it disadvantages and why, and (c) a universally designed alternative that serves a broader range of users without removing functionality for anyone.  If your project has no user-facing interface (it is a pure backend API), describe three choices in your output format, API contract, or documentation that affect the accessibility of the system as a whole.

   *Starter hint:* If your agent returns long text outputs, ask: does it always return plain text, or can it return structured Markdown?  Does it always return the same length regardless of the question, or can users request a summary?  Does it return one monolithic paragraph or a bulleted list?  Each of these is a design choice with accessibility implications.

   *You've succeeded when:* All three proposals clearly identify a specific user group that the current default disadvantages, and your proposed alternative improves their experience without creating new barriers for other users.

---

## Reflection Prompt

**Personal level:** Describe a time when a tool or interface assumed something about you that was not true (how fast you read, what device you had, what language you spoke).  What did you do to work around it, and what would it have cost you if there had been no workaround?

**Technical level:** Pick one accuracy number you have reported or read in this course.  What subgroups does it average over, and which of those subgroups would you need to report separately before you would trust the number for an accessibility use?

**Societal level:** "Nothing about us without us" asks that disabled people be decision-makers, not test subjects.  Who is in the room when your project's defaults get chosen, and who is not?  What would it take to change that?

---

**Coming Up Next:** The neuro-AI ethics module examines how cognitive science shapes the way we build and evaluate AI systems, and what happens when the brain metaphors we borrow turn out to be misleading.

---

## Further Reading

- W3C.  *Web Content Accessibility Guidelines (WCAG) 2.2.* https://www.w3.org/TR/WCAG22/
- NV Access.  *NVDA screen reader* (free download for Windows). https://www.nvaccess.org/
