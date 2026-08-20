<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-accessibilityai.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-accessibilityai.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# AI for Accessibility: Opportunity, Obligation, and Risk

The Ursinus Question "How should we live together?" is not abstract — it has a technical answer that computer scientists are currently writing in code. AI systems are already generating captions, describing images to blind users, and augmenting communication for people with complex communication needs. They are also making decisions under training conditions that systematically underrepresent people with disabilities, producing interfaces that fail screen readers, and offering tools only to those with fast internet and paid subscriptions. This activity holds both truths at once: AI is a genuine opportunity for accessibility, and it carries real risks of widening the gap it claims to close. The arc: **what AI enables $\rightarrow$ who gets access $\rightarrow$ the training data gap $\rightarrow$ universal design as an engineering practice**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Each model asks you to reason about technical choices and their human consequences together. The Recorder posts the group's answers to the Class Activity Questions discussion board; the Presenter is prepared to report where the group disagreed and why. Complete the Reflection Prompt individually in your notebook after class. This activity connects to the Ursinus Questions and to your final project's ethics section.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Assistive technology** | Any device, software, or tool that helps a person with a disability perform tasks that might otherwise be difficult or impossible. | A screen reader that converts text on a website into spoken audio for a blind user. |
| **Disaggregated metrics** | Reporting accuracy or performance broken down by subgroup (e.g., by speaker accent), rather than as a single overall average that can hide unequal performance. | Reporting caption accuracy separately for speakers with dysarthria versus fluent speakers, rather than averaging them together. |
| **AAC (Augmentative and Alternative Communication)** | Communication methods and devices used by people who cannot rely on speech, ranging from picture boards to high-tech devices that speak for the user. | An iPad app that lets a non-speaking autistic person tap symbols to form sentences, which the device speaks aloud. |
| **WCAG (Web Content Accessibility Guidelines)** | A set of internationally recognized standards (published by the W3C) defining what makes web content accessible to people with a wide range of disabilities. | A rule requiring sufficient color contrast between text and background so users with low vision can read the page. |
| **Universal design** | The practice of building products and environments to be usable by the broadest possible range of people from the start, rather than retrofitting accessibility as an add-on. | Designing a ramp at a building entrance benefits wheelchair users, parents with strollers, and delivery workers alike. |
| **Nothing about us without us** | A principle from disability justice advocacy stating that people with disabilities must be included as decision-makers — not just as test subjects — in designing tools that affect them. | Inviting actual AAC users to co-design the phrase-prediction algorithm, rather than testing the finished product on them afterward. |

---

# Part I: The Opportunity and the Gap

In this part, you will examine both the genuine benefits and access risks of AI-powered accessibility tools — building the habit of holding both truths simultaneously that any ethical AI practitioner needs.

## Model 1: Opportunity vs. Risk Matrix

AI-powered accessibility tools span a wide range of capabilities and populations. Each entry below represents a real deployed or research application. Notice that every row has both a genuine benefit and a genuine risk — the goal of this model is to hold both in mind simultaneously.

| Application | What AI Enables | Who Benefits Most | Access Risk | Quality Risk |
|---|---|---|---|---|
| **Real-time captioning** (e.g., Whisper, Otter.ai) | Automatic speech-to-text at near-human accuracy; live captions for deaf and hard-of-hearing users in real time, without a human transcriptionist. | Deaf and hard-of-hearing people; users in noisy or multilingual environments who struggle to follow audio. | Requires a fast internet connection; best performance is locked behind paid subscription tiers; offline mode is limited or absent. | Accuracy drops sharply on accented speech, speech affected by motor differences, or domain-specific vocabulary (medical terms, proper nouns). |
| **Image alt-text generation** (e.g., GPT-4V, BLIP) | Describes visual content in natural language, making it accessible to screen-reader users; scales to millions of images that would never receive human-written descriptions. | Blind and low-vision users who rely on screen readers to understand image-heavy web pages and social media. | Requires API access, which is embedded in assistive technology that often costs money; not available in every app. | May misdescribe images that depend on cultural context; may omit emotionally significant details a human describer would naturally include. |
| **Voice control and navigation** (e.g., Dragon, Voice Access) | Hands-free device and application control, replacing the mouse and keyboard entirely for navigation, dictation, and commands. | Users with motor impairments, repetitive strain injuries, limb differences, or other conditions affecting hand use. | Robust performance requires high-end hardware; accent sensitivity limits effectiveness for many users. | Recognition fails most on atypical speech patterns — which are often the speech patterns of the users who most urgently need hands-free input. |
| **Reading assistance** (e.g., natural language simplification, TTS) | Simplifies complex text; reads content aloud; supports users who struggle with dense written language for a variety of reasons. | Users with dyslexia, cognitive disabilities, emerging readers, and non-native English speakers. | Web-based tools require accounts; school-licensed tools are only available while enrolled at a participating institution. | Oversimplification can strip important nuance; simplification models are trained mostly on majority-style text and may handle specialized or cultural language poorly. |
| **AAC enhancement** (augmentative and alternative communication) | Predictive text and symbol suggestion for non-speaking users, enabling faster and more natural communication than unassisted letter-by-letter selection. | Non-speaking autistic users; users with ALS, cerebral palsy, or other conditions affecting speech production. | AAC devices themselves are expensive; AI-enhanced features often require ongoing subscription fees on top of device cost. | AI-predicted phrases may not reflect the individual user's voice, personal vocabulary, or communication style — replacing their authentic expression with a statistical average. |
| **Sign language recognition** | Translates sign language to text or speech in real time, enabling deaf signers to communicate directly with hearing non-signers without a human interpreter. | Deaf signers communicating in environments where interpreters are unavailable or unaffordable. | Requires good camera hardware and consistent lighting to function reliably; not integrated into most standard devices. | Most models are trained on a small number of signers and a single regional sign language; ASL models may fail on BSL, PSE, or regional ASL dialects. |

### Critical Thinking Questions

1. Across the six applications in Model 1, identify the single most consistent pattern in the "Access Risk" column. What structural feature of how AI tools are distributed — not a technical limitation, but a business or infrastructure choice — creates this pattern?

   *Hint:* Look at what nearly every Access Risk cell has in common. Is the barrier technical (the AI can't do it), or is it about how the tool is packaged and sold?

2. The "Quality Risk" column for voice control notes that "the very users who most need the tool" face the highest error rates. Explain specifically why training data composition causes this outcome. What would a more equitable data collection process look like — and what would it cost?

   *Hint:* If most voice training data comes from fluent, accent-neutral speakers (because they're easy to recruit at scale), what does the model learn to recognize well — and what does it learn to recognize poorly?

3. AAC users communicate through symbols, pre-programmed phrases, or letter boards, often building a personal vocabulary over years. An AI that auto-completes their phrases based on majority-user patterns may predict fluently but inauthentically. Why does this matter beyond minor inconvenience — and how does it connect to questions of identity and personal autonomy?

   *Hint:* If someone spent years building a set of phrases that express their humor, their interests, and their personality — and an AI replaces those phrases with generic predictions — what exactly has been lost?

Now that you have mapped where AI accessibility tools succeed and fail, Part II shows you why headline accuracy numbers can obscure the most important failures.

---

# Part II: The Training Data Gap

In this part, you will see how a technically accurate accuracy metric can hide serious inequity — a pattern that recurs across every domain where AI affects underrepresented groups.

## Model 2: When Aggregate Accuracy Hides Inequity

Consider the following scenario. A captioning AI achieves **99% word accuracy** across its full benchmark test set. The company publishes this figure in its marketing materials and in a published paper. A disability advocate argues the metric is insufficient. Here is the data beneath the headline:

One of the most important lessons in AI evaluation is that an impressive overall number can hide serious failures for specific groups. This is especially dangerous when the groups most harmed by the failure are the groups who most need the tool to work.

| Speaker Group | Test Set Proportion | Word Accuracy | What a 99% Headline Hides |
|---|---|---|---|
| Standard American English, no speech difference | 78% of test speakers | 99.5% accuracy — near-perfect. | This group dominates the test set, so its performance dominates the headline number. |
| Regional accent (Southern US, AAVE, etc.) | 12% of test speakers | 96.8% accuracy — noticeably lower but still often described as "good." | Errors cluster on culturally specific vocabulary and pronunciation patterns underrepresented in training. |
| Non-native English speaker | 7% of test speakers | 93.1% accuracy — approximately one error per sentence in continuous speech. | Non-native speakers are often excluded from training data collection entirely due to language and logistics barriers. |
| Speaker with dysarthria or other motor speech difference | 3% of test speakers | 84.3% accuracy — roughly one word in six is wrong, making captions difficult to follow. | This is the group for whom real-time captioning is most critical — and they experience the worst performance. |

The weighted average across these groups is approximately 99% — the headline number. The group with the highest error rate (15.7% errors) is the group for whom captioning is not a convenience but a necessary communication bridge.

An AI caption generator achieves 98% word accuracy across all test speakers. A disability advocate argues this metric is insufficient. The most compelling reason is:

[(X)] The 2% error rate likely concentrates among speakers with speech differences, meaning the people who most need captions may face substantially higher error rates than the headline metric suggests
[( )] 98% accuracy is high enough that any remaining errors are distributed roughly equally across all speaker groups
[( )] The advocate's concern would only be valid if the tool had no human captioner fallback available
[( )] Word accuracy is a flawed metric because it counts every word equally, making it impossible to identify subgroup disparities

---

### Critical Thinking Questions

4. What would a *disaggregated* accuracy report look like in practice? Define at least three speaker subgroups that should be reported separately in any captioning benchmark — and explain specifically why each one matters for the people who rely on the tool.

   *Hint:* Consider subgroups defined by hearing status, speech production differences, native language, and regional dialect. For each, ask: does this group have fewer alternative communication options if the tool fails?

5. The model in question was trained on 78% standard-accent data because that data was easiest to collect at scale. Propose a concrete data collection strategy that would improve representation of speakers with dysarthria. What obstacles would you face — and which require technical solutions versus policy or community partnership solutions?

   *Hint:* Consider who you would need to partner with, how you would compensate participants fairly, how you would handle the extra annotation time required for atypical speech, and how you would ensure participants retain rights over their voice data.

6. The principle "nothing about us without us" originates in disability justice advocacy. It demands that disabled people be included as decision-makers — not just as test subjects — in the design of tools intended to serve them. What would this require of a team building a new captioning AI? Name two specific decisions in the design process where inclusion of users with disabilities would change the outcome.

   *Hint:* Think about decisions made early in a project — what to optimize for, how to define "good enough," which error types to prioritize reducing — and how those decisions might differ if disabled users were in the room when they were made.

---

> ⚠️ **Common Misconception:** "A high accuracy number means the system works well for everyone."
>
> Aggregate accuracy metrics can be mathematically accurate and deeply misleading at the same time. If 78% of your test set performs at 99.5% accuracy, that group will dominate any weighted average — even if a minority group experiences 84% accuracy. In accessibility contexts, the groups with the worst performance are often the groups with the fewest alternatives. Reporting only the aggregate number is not just a statistical oversight; it is a choice about whose experience counts.

Understanding who gets left out by training data gaps sets up the design question in Part III: how do we build AI interfaces that do not recreate those gaps by accident?

---

# Part III: Universal Design and the AI Interface

In this part, you will audit a generic AI interface against real disability contexts, connecting the "nothing about us without us" principle to concrete engineering choices.

## Model 3: Accessibility Audit of a Generic AI Chat Interface

Universal design means building for the broadest range of users from the start, not adding accessibility as an afterthought. The principle is captured well by the ramp analogy: a ramp built into a building's entrance from day one serves wheelchair users, parents with strollers, and delivery workers — while a ramp bolted onto the side six months later is more expensive, harder to reach, and signals that some users were an afterthought.

Below are five concrete design choices in a typical AI chatbot interface, evaluated across different disability contexts.

| Design Choice | Default Implementation | Impact on Keyboard-Only Users | Impact on Screen Reader Users | Impact on Users with Cognitive Disabilities | Impact on Users with Motor Impairments |
|---|---|---|---|---|---|
| **Response timeout** | Session times out after 5 minutes of inactivity; the user must re-authenticate from scratch. | Neutral — keyboard-only users can type quickly enough. | May lose all context if the session expires while the user is navigating the response with a screen reader. | Very harmful — users who need more time to read and process a response lose their work and must start over. | Harmful — users who type slowly or use switch access may regularly hit the timeout mid-response. |
| **Font and layout** | 14px sans-serif, low-contrast gray text on a white background, densely packed UI elements. | Neutral — font rendering doesn't affect keyboard navigation. | Irrelevant to screen reader users, who hear the DOM read aloud rather than seeing the visual layout. | Harmful — low contrast and dense layout increase cognitive load and make the interface harder to parse. | Neutral — motor impairments don't affect visual perception of the interface. |
| **Keyboard navigation** | Tab order follows visual layout; some interactive elements (e.g., copy buttons) are not reachable by keyboard. | Harmful — non-linear tab order causes disorientation; some functions are completely unreachable. | Harmful — focus management is lost after the AI's response appears; the screen reader cursor is stranded. | Neutral — keyboard navigation doesn't inherently affect cognitive load. | Harmful — a poor tab order requires many extra keystrokes to reach common functions. |
| **Response length** | The AI produces verbose multi-paragraph responses by default, with no option to request a shorter version. | Neutral — keyboard users can scroll without extra effort. | Harmful — the screen reader reads the entire response aloud before the user can interrupt or skip ahead. | Harmful — long responses overwhelm working memory; users may lose track of the question they originally asked. | Harmful — longer responses require more navigation to reach the input field for a follow-up. |
| **Audio feedback** | No audio confirmation when a message is sent or when a new response appears. | Neutral — keyboard users can see the response appear visually. | Neutral — the screen reader automatically announces DOM changes when a response arrives. | Helpful for some users who benefit from multimodal confirmation; harmful if the sound is non-dismissible. | Helpful — confirms that an action succeeded without requiring the user to visually scan the screen. |

### Critical Thinking Questions

7. The Web Content Accessibility Guidelines (WCAG) 2.2 define four principles for accessible interfaces, known as **POUR**: **Perceivable** (users can perceive the content), **Operable** (users can operate the interface), **Understandable** (users can understand content and UI behavior), and **Robust** (content works reliably with assistive technologies). For each row in Model 3, identify which WCAG POUR principle the design choice most directly affects and explain your reasoning.

   *Hint:* Font contrast is primarily a Perceivable issue (can the user detect the content?). Keyboard navigation is primarily an Operable issue. Think about what each design choice prevents users from doing.

8. The "response timeout" row reveals a genuine tension between security (idle sessions should expire to prevent unauthorized access) and accessibility (some users need more time). This is a real values conflict, not a technical limitation. How would you resolve it? Name a specific design pattern that preserves both values simultaneously.

   *Hint:* Consider solutions like warning the user before timeout with enough notice to respond, offering a re-authentication that doesn't require re-entering all context, or using activity signals beyond typing (e.g., mouse movement, keyboard focus) to detect engagement.

9. Whose responsibility is it when an AI accessibility tool fails — the developer of the underlying AI model, the organization that deployed it, or the AI company that provides the API? Construct a brief argument assigning primary responsibility to each of the three parties, then state which argument you find most convincing and why.

   *Hint:* Think about who made each decision: who chose the training data? Who chose to deploy without testing with disabled users? Who controls the API's output quality? Does responsibility depend on who had the most information and the most power to change the outcome?

10. The concept of *ableism* refers to discrimination and social prejudice against people with disabilities, including the assumption that a non-disabled way of interacting with the world is the natural default. Identify one design decision in a typical AI system — not necessarily one listed in Model 3 — that reflects an ableist assumption. Propose a concrete alternative design that does not make that assumption.

    *Hint:* Think about defaults: what does the system assume about how fast a user reads, how a user inputs text, or what a "normal" interaction looks like? Any default that works for a non-disabled user but creates friction for a disabled user is worth examining.

---

## Exercises

1. *Accessibility audit.*

   *What to do:* Choose any publicly available AI-powered tool (a chatbot, a caption generator, an image describer, or another tool of your choice). Using only a keyboard — no mouse — and, if possible, a screen reader (NVDA on Windows, JAWS, or VoiceOver on Mac/iOS), attempt to complete one full task with the tool. Document every point where the interface failed, required workarounds, or produced an error. Write a one-page audit report organized around the WCAG POUR principles. Compare your findings to the tool's published accessibility statement, if one exists.

   *Starter hint:* On a Mac, enable VoiceOver with Command + F5. On Windows, press Windows + Ctrl + Enter for Narrator, or download NVDA (free at nvaccess.org). Start by navigating only with Tab, Shift+Tab, Enter, and arrow keys. Note every moment where you are uncertain where focus is, where a button has no label, or where content appears without your screen reader announcing it.

   *You've succeeded when:* Your audit report names at least three specific interface failures, maps each to a WCAG principle, and compares at least one finding to what the tool's accessibility statement claims about that feature.

2. *Disaggregated evaluation design.*

   *What to do:* Design an evaluation protocol for a reading-assistance AI that simplifies complex text for users with cognitive disabilities or dyslexia. Specify: (a) how you would recruit a representative sample of participants, (b) what metrics you would collect beyond aggregate accuracy, (c) how you would structure and report results so that subgroup differences are visible rather than averaged away, and (d) what threshold would constitute "good enough" performance — and who should have the authority to decide that threshold.

   *Starter hint:* Think about recruiting through disability advocacy organizations, university disability services offices, and community groups — not just general survey platforms. For metrics, consider comprehension scores (did users understand the simplified text?), preference ratings (did it feel natural?), and error rates by user subgroup. For reporting, sketch a table with one row per subgroup, not just an overall average.

   *You've succeeded when:* Your protocol includes at least three distinct participant subgroups, at least two metrics beyond aggregate accuracy, a reporting structure that makes subgroup differences visible, and a written argument for who should set the "good enough" threshold and why.

3. *Universal design proposal.*

   *What to do:* For your final project, identify three specific design choices in your agent's interface or output format that affect users with disabilities. For each choice, describe (a) the current default behavior, (b) which users it disadvantages and why, and (c) a universally designed alternative that serves a broader range of users without removing functionality for anyone. If your project has no user-facing interface (it is a pure backend API), describe three choices in your output format, API contract, or documentation that affect the accessibility of the system as a whole.

   *Starter hint:* If your agent returns long text outputs, consider: does it always return plain text, or can it return structured Markdown? Does it always return the same length regardless of the question, or can users request a summary? Does it return one monolithic paragraph or a bulleted list? Each of these is a design choice with accessibility implications.

   *You've succeeded when:* All three proposals clearly identify a specific user group that is disadvantaged by the current default, and your proposed alternative genuinely improves their experience without creating new barriers for other users.

---

→ Coming Up Next: The neuro-AI ethics module examines how cognitive science shapes the way we build and evaluate AI systems — and what happens when the brain metaphors we borrow turn out to be misleading.

## Further Reading

- Treviranus, J. "The Three Dimensions of Inclusive Design." *Inclusive Design Research Centre*, OCAD University (2019).
- Microsoft. "AI for Accessibility: Program Overview and Case Studies." (microsoft.com/en-us/ai/ai-for-accessibility, 2024).
- Be My Eyes. "Virtual Volunteer: GPT-4V Integration for Vision Assistance." (bemyeyes.com, 2023).
- Web Accessibility Initiative. "Web Content Accessibility Guidelines (WCAG) 2.2." W3C (2023, w3.org/TR/WCAG22).
- Disability Justice Network. "Principles of Disability Justice." (2015, onlinelibrary.wiley.com).
- Blodgett et al. "Language (Technology) is Power: A Critical Survey of 'Bias' in NLP." *ACL* (2020).
