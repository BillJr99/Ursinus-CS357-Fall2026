# AI for Accessibility: Opportunity, Obligation, and Risk
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

# Part I: The Opportunity and the Gap

## Model 1: Opportunity vs. Risk Matrix

AI-powered accessibility tools span a wide range of capabilities and populations. Each entry below represents a real deployed or research application.

| Application | What AI Enables | Who Benefits Most | Access Risk | Quality Risk |
|---|---|---|---|---|
| Real-time captioning (e.g., Whisper, Otter.ai) | Automatic speech-to-text at near-human accuracy; live captions for deaf and hard-of-hearing users | Deaf and hard-of-hearing people; users in noisy or multilingual environments | Requires fast internet; best performance on paid tiers; offline mode limited | Accuracy drops sharply on accented speech, speech with motor differences, or domain-specific vocabulary |
| Image alt-text generation (e.g., GPT-4V, BLIP) | Describes visual content in natural language; scales to millions of images that would never receive human alt-text | Blind and low-vision users relying on screen readers | Requires API access; embedded in assistive tech that itself costs money | May misdescribe images with cultural specificity; may omit emotionally salient details a human would include |
| Voice control and navigation (e.g., Dragon, Voice Access) | Hands-free device and application control; replaces mouse and keyboard | Users with motor impairments, repetitive strain injury, or limb differences | Requires high-end hardware for robust performance; accent sensitivity limits effectiveness | Recognition fails on atypical speech patterns — often the very users who most need the tool |
| Reading assistance (e.g., natural language simplification, TTS) | Simplifies complex text; reads aloud; supports users with dyslexia, cognitive differences, or low literacy | Users with dyslexia, cognitive disabilities, emerging readers, non-native speakers | Web-based tools require accounts; school-licensed tools are school-dependent | Oversimplification can strip nuance; simplification models trained on majority text styles |
| AAC enhancement (augmentative and alternative communication) | Predictive text and symbol suggestion for non-speaking users; faster, more natural communication | Non-speaking autistic users; users with ALS, CP, or other conditions affecting speech | AAC devices are expensive; AI enhancements often require ongoing subscriptions | AI-predicted phrases may not reflect the individual's voice, vocabulary, or communication style |
| Sign language recognition | Translates sign language to text or speech in real-time | Deaf signers communicating with non-signers | Requires good camera hardware and lighting; trained mostly on a small number of signers | Most models trained on a single regional sign language; ASL models may fail on BSL or PSE |

### Critical Thinking Questions

1. Across the six applications in Model 1, identify the single most consistent pattern in the "Access Risk" column. What structural feature of how AI tools are distributed creates this pattern?

2. The "Quality Risk" column for voice control notes that "the very users who most need the tool" face the highest error rates. Explain why training data composition causes this outcome. What would a more equitable data collection process look like?

3. AAC users communicate through symbols, pre-programmed phrases, or letter boards, often building a personal vocabulary over years. An AI that auto-completes their phrases based on majority-user patterns may predict fluently but inauthentically. Why does this matter beyond minor inconvenience, and how does it connect to questions of identity and autonomy?

---

# Part II: The Training Data Gap

## Model 2: When Aggregate Accuracy Hides Inequity

Consider the following scenario. A captioning AI achieves **99% word accuracy** across its full benchmark test set. The company publishes this figure in its marketing materials and in a published paper. A disability advocate argues the metric is insufficient. Here is the data beneath the headline:

| Speaker Group | Test Set Proportion | Word Accuracy |
|---|---|---|
| Standard American English, no speech difference | 78% | 99.5% |
| Regional accent (Southern US, AAVE, etc.) | 12% | 96.8% |
| Non-native English speaker | 7% | 93.1% |
| Speaker with dysarthria or other motor speech difference | 3% | 84.3% |

The weighted average across these groups is approximately 99% — the headline number. The group with the highest error rate (15.7% errors on average) is the group for whom captioning is most critical: users whose speech is already difficult for some listeners to understand, for whom captions are not a convenience but a necessary communication bridge.

[[MC]]
An AI caption generator achieves 98% word accuracy across all test speakers. A disability advocate argues this metric is insufficient. The most compelling reason is:
- (x) The 2% error rate likely concentrates among speakers with speech differences, meaning the people who most need captions may face substantially higher error rates than the headline metric suggests
- ( ) 98% accuracy is objectively sufficient for all real-world captioning use cases
- ( ) The advocate should test the system personally before criticizing the published metric
- ( ) Word accuracy is not an established metric and should be replaced with a different one

---

### Critical Thinking Questions

4. What would a *disaggregated* accuracy report look like? Define at least three speaker subgroups that should be reported separately in any captioning benchmark, and explain why each matters.

5. The model in question was trained on 78% standard-accent data because that data was easiest to collect at scale. Propose a concrete data collection strategy that would improve representation of speakers with dysarthria. What obstacles would you face, and which require technical solutions versus policy solutions?

6. The principle "nothing about us without us" originates in disability justice advocacy and demands that disabled people be included as decision-makers — not just as test subjects — in the design of tools intended to serve them. What would this require of a team building a new captioning AI? Name two specific decisions where inclusion of users with disabilities would change the outcome.

---

# Part III: Universal Design and the AI Interface

## Model 3: Accessibility Audit of a Generic AI Chat Interface

Universal design means building for the broadest range of users from the start, not adding accessibility as an afterthought. Below are five concrete design choices in a typical AI chatbot interface, evaluated across different disability contexts.

| Design Choice | Default Implementation | Impact on Keyboard-Only Users | Impact on Screen Reader Users | Impact on Users with Cognitive Disabilities | Impact on Users with Motor Impairments |
|---|---|---|---|---|---|
| Response timeout | Session times out after 5 minutes of inactivity; user must re-authenticate | Neutral | May lose context if session expires mid-navigation | Very harmful: longer processing time needed to read and respond | Harmful: typing takes longer; 5 minutes is insufficient |
| Font and layout | 14px sans-serif, low-contrast gray on white text, dense UI | Neutral | Irrelevant to screen reader (reads DOM) | Harmful: low contrast, dense layout increase cognitive load | Neutral |
| Keyboard navigation | Tab order follows visual layout; some interactive elements lack keyboard focus | Harmful: non-linear tab order causes disorientation | Harmful: focus management lost after AI response appears | Neutral | Harmful: requires many keystrokes to navigate |
| Response length | AI produces verbose multi-paragraph responses by default | Neutral | Harmful: screen reader reads entire response before user can interrupt | Harmful: long responses overwhelm working memory | Harmful: longer responses require more navigation |
| Audio feedback | No audio confirmation when message is sent or response arrives | Neutral | Neutral (screen reader announces changes) | Helpful for some users; harmful if non-dismissible | Helpful: confirms action without visual check |

### Critical Thinking Questions

7. The Web Content Accessibility Guidelines (WCAG) 2.2 define four principles for accessible interfaces: **Perceivable, Operable, Understandable, Maintainable** (POUR). For each row in Model 3, identify which WCAG principle the design choice most affects.

8. The "response timeout" row reveals a tension between security (sessions should expire) and accessibility (some users need more time). This is a genuine values conflict, not a technical problem. How would you resolve it? What design pattern preserves both security and accessibility?

9. Whose responsibility is it when an AI accessibility tool fails — the developer of the AI model, the organization that deployed it, or the AI company that provides the underlying API? Construct an argument assigning primary responsibility to each of the three parties, then state which argument you find most convincing and why.

10. The concept of *ableism* refers to discrimination and social prejudice against people with disabilities, including the assumption that a non-disabled way of functioning is the default or the ideal. Identify one design decision in a typical AI system (not necessarily in Model 3) that reflects an ableist assumption, and propose a concrete alternative.

---

## Exercises

1. *Accessibility audit.* Choose any publicly available AI-powered tool (a chatbot, a caption generator, an image describer, or another tool). Using only a keyboard (no mouse) and, if possible, a screen reader (NVDA, JAWS, or VoiceOver), attempt to complete one full task with the tool. Document every point where the interface failed or required workarounds. Write a one-page audit report structured around the WCAG POUR principles. Compare your findings to the tool's published accessibility statement if one exists.

2. *Disaggregated evaluation design.* Design an evaluation protocol for a reading-assistance AI (which simplifies complex text for users with cognitive disabilities or dyslexia). Specify: (a) how you would recruit a representative sample of users, (b) what metrics you would collect beyond aggregate accuracy, (c) how you would report results so that subgroup differences are visible rather than averaged away, and (d) what threshold would constitute "good enough" and who should decide that threshold.

3. *Universal design proposal.* For your final project, identify three specific design choices in your agent's interface or output format that affect users with disabilities. For each choice, describe the current default, who it disadvantages, and what a universally designed alternative would be. If your project has no interface (it is a pure backend API), describe three choices in the output format or documentation that affect accessibility of the system as a whole.

---

## Reflection Prompt

In your notebook: The Ursinus Question "Who am I?" connects to identity. For users who rely on AAC, a voice synthesizer, or a captioning system to communicate, the AI mediates how they appear to the world. When an AI generates captions with 15% errors on a specific speaker's voice, or predicts AAC phrases that don't match a user's vocabulary, it misrepresents that person to the people around them. How should this shape the ethical obligations of the AI developers who built those systems? And how does it change the responsibility of people like you — who are learning to build these systems — toward the communities who will use them?

---

## Further Reading

- Treviranus, J. "The Three Dimensions of Inclusive Design." *Inclusive Design Research Centre*, OCAD University (2019).
- Microsoft. "AI for Accessibility: Program Overview and Case Studies." (microsoft.com/en-us/ai/ai-for-accessibility, 2024).
- Be My Eyes. "Virtual Volunteer: GPT-4V Integration for Vision Assistance." (bemyeyes.com, 2023).
- Web Accessibility Initiative. "Web Content Accessibility Guidelines (WCAG) 2.2." W3C (2023, w3.org/TR/WCAG22).
- Disability Justice Network. "Principles of Disability Justice." (2015, onlinelibrary.wiley.com).
- Blodgett et al. "Language (Technology) is Power: A Critical Survey of 'Bias' in NLP." *ACL* (2020).
