# Intellectual Property, Privacy, and the Case for Local AI
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-ipprivacy.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ipprivacy.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Intellectual Property, Privacy, and the Case for Local AI

Generative models are trained on creative work and prompted with personal information, which places two bodies of law and ethics (intellectual property and privacy) at the center of agentic practice. Today we map both, *as engineers*: not to play lawyer, but to recognize the decisions that have legal and ethical weight and to design accordingly, with our local-first stack as a recurring answer. The arc: **the IP questions $\rightarrow$ the privacy questions $\rightarrow$ regulatory landscape $\rightarrow$ design responses you already know how to build**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). These questions are contested; the Reflector again guards against premature convergence. Nothing today is legal advice, and that disclaimer is itself a lesson in professional boundaries. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Intellectual Property

## 1. Three Distinct Questions

**Input: was training a lawful use of copyrighted work?** Training corpora include books, code, journalism, and art whose creators largely did not consent. Litigation (authors, artists, and news organizations versus model vendors) turns substantially on *fair use*, a four-factor balancing test in US law (purpose and character, nature of the work, amount used, market effect). Courts are actively dividing on these questions; engineers should track outcomes, not assume them.

**Output: who owns what the model produces?** The US Copyright Office requires human authorship; purely machine-generated material is not copyrightable, while human creative selection and arrangement can be. For your projects: your prompts, curation, code, and editorial choices are where your authorship lives, so document them.

**Memorization: can the model emit its training data?** Yes, occasionally and more often for text repeated frequently in the corpus; verbatim regurgitation of protected work is the cleanest infringement risk. Mitigations include deduplication at training time and output filters at deployment, neither perfect.

---

## Model 1: The Student Artist

A student trains a small image model on 400 of their own paintings, then also fine-tunes on 50 works by a living artist they admire, and sells outputs "in the style of" that artist.

### Critical Thinking Questions

1. Separate the three IP questions for this scenario: which use is least contested, which most, and why does "style" complicate the middle one (style is traditionally not copyrightable, but the fine-tuning *copies* the works)?
2. The student argues "I learned from that artist too; the model just did it faster." Steelman this argument, then identify the strongest disanalogy between human learning and model training.
3. What documentation would you advise the student to keep about their own contribution, given the human-authorship doctrine?

---

# Part II: Privacy

## 2. Where Prompts Go, and the Special Status of Student Data

**A prompt is a disclosure.** Text sent to a hosted service transits and rests on third-party infrastructure under that provider's terms, which may permit retention, human review, or training on your inputs. The engineering questions are always the same: what data leaves, where it is stored, for how long, who can see it, and can you delete it.

**Some data is regulated, not just sensitive.** In our own context: **FERPA** protects student education records (grades, submissions, advising notes); **IRB** protocols govern human-subjects research data; **HIPAA** governs health information. Pasting a roster into a consumer chatbot is not a vibe violation; it is plausibly a compliance violation. **GDPR** (EU) and a growing patchwork of US state laws add rights of access, deletion, and limits on automated decision-making.

**Agents raise the stakes mechanically.** A chatbot leaks what you paste; an *agent with tools* can leak what it can *reach*: files, calendars, email. The tool-permission taxonomy you built (read-only, reversible, irreversible) is privacy infrastructure, and the local stack you have run all semester is the strongest single control: data that never leaves the machine cannot be retained by anyone else.

[[MC]]
An instructor wants AI-assisted feedback on essays containing student names and grades. The design that most directly addresses the FERPA concern is:
- ( ) A hosted frontier model with an enterprise logo
- ( ) Asking students not to write personal details
- (x) A local model on institutional hardware, with de-identification before processing and documented data handling
- ( ) Any model, provided temperature is 0

---

## Model 2: Data Flow Audit

Consider three pipelines you have personally built this term: Lab 2 (RAG over your own documents), Lab 5 (rubric pipeline over submissions), and your final project.

### Critical Thinking Questions

4. For each, draw the data-flow arrow diagram: what content moves, to which process, on which machine. Mark the first arrow, if any, that crosses your laptop's boundary.
5. Your Lab 5 pipeline processes synthetic essays; the same code pointed at real student work changes compliance category entirely while changing zero lines of code. What does that imply about where responsibility lives: in code, or in deployment decisions?
6. Write the three-sentence data-handling disclosure you would owe users of your final project. (This text goes directly into your governance assignment.)

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Terms-of-service safari.* Each teammate reads the data-use terms of one AI service they actually use and extracts: retention period, training-on-inputs policy, and deletion rights. The Recorder builds the comparison table; the Presenter reports the most surprising finding.
2. *Memorization probe.* Attempt (politely) to elicit verbatim famous text from your local model with increasingly specific prompts. Report at what specificity, if any, reproduction begins, and connect the result to the repeated-text mechanism above.
3. *Local-first justification memo.* For your final project, write the half-page memo a campus IT review would want: what data the system touches, why local inference is or is not required, and what would change if the project scaled beyond the class.
4. *Case watch.* Find one currently active AI copyright or privacy case or regulatory action (search the news), and summarize the question it will settle in two sentences. We will pool these next class as the governance landscape.

---

## Reflection Prompt

In your notebook: you have free, private, capable AI on your own laptop, an option most users do not know exists. Does knowing how to keep data local create any obligation to do so, for yourself, or for others whose data you hold? Where does convenience legitimately win?

---

## 4. Further Reading

- US Copyright Office. *Copyright and Artificial Intelligence* reports (2023-2025, online).
- Carlini et al. "Extracting Training Data from Large Language Models." *USENIX Security* (2021).
- US Department of Education FERPA guidance (online), and your institution's responsible-AI and data-classification policies.
