<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-ipprivacy.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-ipprivacy.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Intellectual Property, Privacy, and the Case for Local AI

The *Training Data and Bias* activity showed what models absorb from their training distributions; today we ask who owns that material and who gets watched.  Generative models are trained on creative work and prompted with personal information, which places two bodies of law and ethics (intellectual property and privacy) at the center of agentic practice.  Today we map both, *as engineers*: not to play lawyer, but to recognize the decisions that have legal and ethical weight and to design accordingly, with our local-first stack as a recurring answer.  The path today: **the IP questions $\rightarrow$ the privacy questions $\rightarrow$ regulatory landscape $\rightarrow$ design responses you already know how to build**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  These questions are contested; the Reflector again guards against premature convergence.  Nothing today is legal advice, and that disclaimer is itself a lesson in professional boundaries.  After class, please respond to the reflective prompt on your own in your notebook.

---

### Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Copyright** | A legal right that gives the creator of an original work exclusive control over its use and distribution for a limited time. | An author owns the text of their novel; a model trained on that novel raises questions about whether that use was authorized. |
| **Fair Use** | A legal doctrine in US copyright law that permits limited use of copyrighted material without permission, based on four factors: purpose, nature of the work, amount used, and market effect. | Courts use fair use to decide whether AI training on copyrighted books is lawful; the answer is not yet settled. |
| **FERPA** | The Family Educational Rights and Privacy Act, a US law that restricts who may access student educational records such as grades, transcripts, and advising notes. | Pasting a class roster with student names and grades into a consumer chatbot could violate FERPA. |
| **Data Minimization** | The privacy engineering principle of collecting, processing, and retaining only the data actually needed for a specific task, nothing extra, nothing "just in case." | Stripping student names before running essays through an AI grading assistant is a data minimization practice. |
| **Memorization** | The phenomenon where a model reproduces verbatim text from its training data in its outputs, creating potential copyright infringement risk. | Researchers have demonstrated that repeating a prompt about a specific book excerpt can cause a model to reproduce full passages. |
| **Local Inference** | Running an AI model entirely on your own hardware so that no input data ever travels to a third-party server. | Using Ollama on your laptop to analyze sensitive documents keeps those documents off any external service's infrastructure. |

---

# Part I: Intellectual Property

In this part, you will learn to separate three legally distinct questions about AI and intellectual property that news coverage routinely conflates.  Keeping these three questions distinct will help you reason more carefully about your own projects and about the legal landscape you'll navigate as a practitioner.

## 1.  Three Distinct Questions

Three separate questions arise at the intersection of AI and intellectual property, and conflating them produces confused reasoning.  Keep them apart whenever you read news coverage, policy proposals, or vendor terms of service.

Question 1 - Input: was training a lawful use of copyrighted work?  Training corpora include books, code, journalism, and art whose creators largely did not consent.  Litigation (authors, artists, and news organizations versus model vendors) turns substantially on *fair use* (a four-factor balancing test in US law: purpose and character of the use, nature of the work, amount used, and market effect).  Courts are actively dividing on these questions; engineers should track outcomes, not assume them.

Question 2 - Output: who owns what the model produces?  The US Copyright Office requires human authorship; purely machine-generated material is not copyrightable, while human creative selection and arrangement can be.  For your projects: your prompts, curation, code, and editorial choices are where your authorship lives, so document them.

Question 3 - Memorization: can the model emit its training data?  Yes, occasionally and more often for text repeated frequently in the corpus; verbatim regurgitation of protected work is the cleanest infringement risk.  **Memorization** (when a model reproduces word-for-word text it saw during training) is mitigated by deduplication at training time and output filters at deployment; neither is perfect.

---

## Model 1: The Student Artist

Why this matters: every time you use a generative model for a course project, a creative assignment, or a side project, you are navigating real intellectual property questions, even if no one is suing you today.  Understanding where the law is unsettled helps you document your own creative contributions and avoid the practices most likely to create future liability for you or your employer.

A student trains a small image model on 400 of their own paintings, then also fine-tunes on 50 works by a living artist they admire, and sells outputs "in the style of" that artist.

### Critical Thinking Questions

1.  Separate the three IP questions for this scenario: which use is least contested, which most, and why does "style" complicate the middle one (style is traditionally not copyrightable, but the fine-tuning *copies* the works)?

   *Hint: Start with the simplest case: training on your own work you created yourself.  Then consider what changes when you add someone else's work.  Finally, think about what "copying" means: is imitating a style the same as copying a painting?*

2.  The student argues "I learned from that artist too; the model just did it faster."  Steelman this argument, then identify the strongest disanalogy between human learning and model training.

   *Hint: A human who studies 50 paintings retains impressions and influences.  A model that trains on 50 paintings retains the actual pixel data in its weights.  Is that difference morally significant?  Is it legally significant?*

3.  What documentation would you advise the student to keep about their own contribution, given the human-authorship doctrine?

   *Hint: Think about what a copyright examiner would need to see to confirm a human made creative choices: prompt text, selection decisions, editing steps, rejected outputs.*

---

# Part II: Privacy

In this part, you will trace what actually happens to a prompt when you hit enter (legally and technically) and learn why the pipelines you've already built have different privacy implications depending on what data you run through them.

## 2.  Where Prompts Go, and the Special Status of Student Data

Privacy is not just a personal preference; in educational and research contexts, it is a legal obligation.  Understanding which laws apply to which data, and what "sending a prompt" actually means for data handling, turns you from a user who hopes for the best into an engineer who designs for compliance.

A prompt is a disclosure.  Text sent to a hosted service transits and rests on third-party infrastructure under that provider's terms, which may permit retention, human review, or training on your inputs.  The engineering questions are always the same: what data leaves, where it is stored, for how long, who can see it, and can you delete it.

Some data is regulated, not just sensitive.  In our own context: **FERPA** (Family Educational Rights and Privacy Act) protects student education records such as grades, submissions, and advising notes; **IRB** (Institutional Review Board) protocols govern human-subjects research data; **HIPAA** (Health Insurance Portability and Accountability Act) governs health information.  Pasting a class roster into a consumer chatbot is not just bad practice; it is plausibly a compliance violation.  **GDPR** (General Data Protection Regulation, EU) and a growing patchwork of US state laws add rights of access, deletion, and limits on automated decision-making.

Agents raise the stakes mechanically.  A chatbot leaks what you paste; an *agent with tools* can leak what it can *reach*: files, calendars, email.  The tool-permission taxonomy you built (read-only, reversible, irreversible) is privacy infrastructure, and the local stack you have run all semester is the strongest single control: data that never leaves the machine cannot be retained by anyone else.

An instructor wants AI-assisted feedback on essays containing student names and grades.  The design that most directly addresses the FERPA concern is:

[( )] A hosted frontier model with an enterprise logo, because enterprise agreements always cover FERPA
[( )] Asking students not to write personal details in their essays, because the data never enters the system
[(X)] A local model on institutional hardware, with de-identification before processing and documented data handling
[( )] Any model, provided temperature is 0, because deterministic outputs are not considered personal data

---

## Model 2: Data Flow Audit

Consider three pipelines you have personally built this term: the RAG Knowledge Base Lab (RAG over your own documents), the Rubric Pipeline Lab (rubric pipeline over submissions), and your final project.

### Critical Thinking Questions

4.  For each, draw the data-flow arrow diagram: what content moves, to which process, on which machine.  Mark the first arrow, if any, that crosses your laptop's boundary.

   *Hint: Start from the raw input (a file, a prompt, a submission) and trace every step forward: file reader, embedding model, vector store, LLM call, output display.  Each arrow between steps is where a privacy question lives.*

5.  Your Rubric Pipeline Lab pipeline processes synthetic essays; the same code pointed at real student work changes compliance category entirely while changing zero lines of code.  What does that imply about where responsibility lives: in code, or in deployment decisions?

   *Hint: Consider a fire extinguisher used as a doorstop; the object did not change, but the use did.  Now apply that framing to your pipeline.  Is the code "responsible" for how it is deployed?*

   > *Hint:* A law like FERPA doesn't care what language your pipeline is written in or whether you meant to violate it.  It cares whether protected data was processed in an unauthorized context.  Who in your pipeline decides the context, the code, or the person who runs it?

6.  Write the three-sentence data-handling disclosure you would owe users of your final project.  (This text goes directly into the Data Handling section of the Governance direction of the Responsible AI in Practice assignment, if you choose that direction.)

   *Hint: Include (a) what data the system collects or processes, (b) where that data goes and how long it is kept, and (c) what the user can do if they want their data deleted or have a concern.*

> **Common Misconception:** "If I'm not storing the data, there's no privacy risk."  Many users believe that as long as they do not save a transcript or export a file, no data is retained.  In reality, every call to a hosted API transmits your input to the provider's servers under their terms of service, which may allow retention for logging, abuse detection, or model improvement for months or years.  "I didn't save it" and "the service didn't save it" are very different claims.

---

# Part III: Synthesis and Practice

Now that you understand both IP and privacy as legal frameworks, this part asks you to apply them practically: reading real terms of service, probing memorization behavior in your local model, and writing the compliance memo your project will actually need.

## 3.  Exercises

1.  *Terms-of-service safari.*

   *What to do:* Each teammate reads the data-use terms of one AI service they actually use and extracts: retention period, training-on-inputs policy, and deletion rights.  The Recorder builds a comparison table; the Presenter reports the most surprising finding.

   *Starter hint:* Search the service's terms of service or privacy policy for the words "training," "retain," "delete," and "opt out."  Many services bury opt-out options in account settings rather than the terms themselves; check both.

   *You've succeeded when:* Your team has a table with at least three services compared on the same three dimensions, and the Presenter can explain in plain language what happens to a prompt after you hit enter on each service.

2.  *Memorization probe.*

   *What to do:* Attempt (politely) to elicit verbatim famous text from your local model with increasingly specific prompts.  Report at what specificity, if any, reproduction begins, and connect the result to the repeated-text mechanism above.

   *Starter hint:* Start vague ("write a sentence about a boy wizard") and gradually increase specificity ("write the opening line of Harry Potter") until you observe verbatim text or confirm the model will not produce it.  Note what prompt phrasing triggers different behaviors.

   *You've succeeded when:* You can describe the threshold at which reproduction occurred (or did not), form a hypothesis about why, and connect your finding to the concept of training-data memorization via repetition frequency.

3.  *Local-first justification memo.*

   *What to do:* For your final project, write the half-page memo a campus IT review would want: what data the system touches, why local inference is or is not required, and what would change if the project scaled beyond the class.

   *Starter hint:* Use this structure: (1) what data categories does the system process?  (2) which of those categories are regulated (FERPA, IRB, HIPAA, or state privacy law)?  (3) what is the strongest argument for local inference?  (4) what capability tradeoff, if any, does local inference impose?

   *You've succeeded when:* A campus IT officer unfamiliar with your project could read the memo, understand the data flows, and make an informed decision about whether to approve the system for use with real students.

4.  *Case watch.*

   *What to do:* Find one currently active AI copyright or privacy case or regulatory action (search the news), and summarize the question it will settle in two sentences.  We will pool these in the *Governance and Policy Writing* activity as the governance landscape.

   *Starter hint:* Search for terms like "AI copyright lawsuit 2024 2025," "generative AI training data lawsuit," "AI privacy enforcement action," or "state AI privacy law."  Look for cases involving large language models, image generators, or AI training data scraping.

   *You've succeeded when:* You can state, in plain language, (a) who is suing whom, (b) what specific legal question the case will decide, and (c) why the outcome matters for how AI systems are built or deployed.

---

## Reflection Prompt

*Personal:* You have free, private, capable AI on your own laptop, an option most users do not know exists.  When you use a local model for personal tasks that involve sensitive information (health questions, relationship problems, financial concerns), does knowing how to keep data local make you feel differently about using AI at all?

*Technical:* As someone who can now build both local and cloud-connected AI pipelines, what technical obligations do you think you have when building systems that other people (including people who do not understand where their data goes) will use?

*Societal:* Most people who use AI assistants have no practical ability to run local models, cannot read terms of service, and have no visibility into how their inputs are used.  Does the gap between technically informed and technically naive users create a fairness problem?  Who should close it, and how?

---

## -> Coming Up Next

In the *Governance and Policy Writing* activity, you will move from understanding what data your systems handle to writing the governance documents that formally commit you to handling it responsibly.  Bring your data-flow diagrams and the three-sentence disclosure you drafted in Question 6; they become direct inputs to your policy, and the privacy analysis feeds the Responsible AI Capstone.

## Further Reading

- US Copyright Office.  *Copyright and Artificial Intelligence* reports (2023-2025, online).
- Carlini et al. "Extracting Training Data from Large Language Models."  *USENIX Security* (2021).
- US Department of Education FERPA guidance (online), and your institution's responsible-AI and data-classification policies.
