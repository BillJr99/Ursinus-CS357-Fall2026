# AI Creativity: Generative Models, Authorship, and the Nature of Originality

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-aicreativity.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

## POGIL Roles

This activity uses the POGIL (Process Oriented Guided Inquiry Learning) structure. Assign one role to each group member before beginning.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the group on task, monitors time, ensures everyone contributes, moves the group to the next question when ready |
| **Recorder** | Writes down the group's agreed answers, keeps a record of key decisions and reasoning |
| **Spokesperson** | Presents the group's answers during class discussion, asks the instructor clarifying questions on behalf of the group |
| **Reflector** | Monitors group process, notes what is working and what is not, leads the end-of-activity reflection |

---

## Model 1: What Makes Something Creative?

The word "creative" is used loosely in everyday language. Cognitive scientist Margaret Boden proposed a more precise framework with three types of creativity:

**Combinatorial creativity:** Producing novel and surprising combinations of familiar elements. Most everyday creativity is combinatorial — a poet connects two concepts that are rarely paired, a chef combines ingredients from different cuisines. The space of possibilities is fixed; creativity means navigating it unusually.

**Exploratory creativity:** Systematically exploring the edges of an existing conceptual space — pushing a style, genre, or tradition to its limits while still operating within its rules. A jazz musician improvising within bebop conventions, or a mathematician exploring implications of a known axiom system.

**Transformational creativity:** Changing the rules of the conceptual space itself — making previously impossible ideas possible by redefining the constraints. Cubism didn't just explore painting differently; it redefined what painting was. This is rarer and more disruptive.

### Can AI Do This?

| Human Creative Act | Type | AI Can Do This? | Example |
|-------------------|------|-----------------|---------|
| Writing a poem that connects "grief" and "software debugging" | Combinatorial | Yes | GPT models generating unexpected thematic metaphors |
| Composing jazz variations within the bebop style | Exploratory | Yes | Music generation models trained on genre-specific corpora |
| Inventing haiku as a poetic form | Transformational | Debated | Latent diffusion models themselves as a new medium? |
| Designing a programming language with novel semantics | Transformational | Debated | AI-assisted PL research is early-stage |

### Critical Thinking Questions

**Question 1.** Consider a computer program that produces sentences by randomly selecting words from a vocabulary. Is its output "creative"? What additional ingredients — beyond novelty — seem to be required for something to count as creative? Does the process matter, or only the output?

[[___ Your answer here ___]]

**Question 2.** When a human judges something as creative, what role do the judging audience's expectations and cultural context play? Could the same output be creative in one context and uncreative in another? Give a concrete example.

[[___ Your answer here ___]]

**Question 3.** Is there any form of human creativity that is purely transformational — that has no combinatorial or exploratory elements at all? Or does transformation always build on prior combination and exploration? Use a specific historical example (in art, science, music, or mathematics) to support your answer.

[[___ Your answer here ___]]

---

## Model 2: Copyright, Attribution, and the Artist's Dilemma

The rise of generative AI has created a legal and ethical crisis in creative fields. Three separate issues are often conflated but should be kept distinct:

### 1. Training on Copyrighted Work

When an AI company scrapes copyrighted images, books, or music to train a model, is that infringement? The legal question is whether training constitutes a reproduction or a transformative use under fair use doctrine (in the US) or text-and-data mining exceptions (in the EU). Key ongoing cases include **Getty Images v. Stability AI** (filed 2023) and several consolidated author class actions against OpenAI and Meta.

The **training/output distinction** matters: even if training is found infringing, an output that doesn't reproduce copyrightable expression may itself be non-infringing. And even if training is found to be fair use, outputs that are substantially similar to a specific training work could still infringe.

### 2. Style Mimicry

AI systems can generate output "in the style of" a named living artist. Under current US law, **style itself is generally not copyrightable** — only specific expression is. But many artists feel their livelihood is undermined when their style can be replicated at scale by anyone with a text prompt.

**Moral rights** (stronger in Europe than the US) include the right of attribution and the right of integrity. Some argue that AI style mimicry violates the spirit of moral rights even where it doesn't violate the letter of copyright.

### 3. Attribution and Disclosure

| Creative Domain | What AI Can Do | Legal/Ethical Issue | Current Practice |
|----------------|----------------|-------------------|-----------------|
| **Visual art** | Generate images in named artist's style | Style mimicry; unlicensed training data | No universal standard; platforms vary |
| **Literature** | Generate text ghostwritten or AI-assisted | Disclosure to readers; academic integrity | Academic journals increasingly require disclosure |
| **Music** | Generate instrumentals; clone voices | Voice likeness rights; sound-alike releases | AI music platforms emerging; legal status unsettled |
| **Journalism** | Draft articles; summarize sources | Factual accuracy; attribution of AI role | Major outlets have varying disclosure policies |
| **Film/TV** | Generate scripts; de-age actors; clone voices | SAG-AFTRA protections; consent | Under active negotiation; 2023 strikes addressed this |

### Critical Thinking Questions

**Question 4.** If an AI generates an image using 5 million images as training data, and no single training image can be identified as a direct template for the output, is the output infringing? What legal test would you apply, and what additional facts would you need to know?

[[___ Your answer here ___]]

**Question 5.** A musician has spent 20 years developing a distinctive vocal style and has posted hundreds of recordings publicly online. An AI company trains a voice-cloning model on those recordings without asking permission. The company generates no tracks that are identical to the musician's recordings. Why might the musician still feel — and arguably be — harmed? What interests beyond copyright are at stake?

[[___ Your answer here ___]]

**Question 6.** Propose a policy for AI attribution in creative work that you consider fair to all parties. Your policy should address: (a) what creators of training data are owed, (b) what AI system developers are permitted to do, and (c) what users who produce AI-assisted work must disclose. Defend your choices.

[[___ Your answer here ___]]

### Check Your Understanding

An artist claims that an AI system was trained on their publicly posted portfolio without consent and now generates work "in their style." Under current US copyright law, the most accurate statement is:

- ( ) The AI system owner is clearly liable for copyright infringement because they used the artist's work without a license
- ( ) The artist has no legal recourse because publicly posted content is in the public domain
- (x) The legal status is genuinely unsettled; multiple court cases are actively pending and legal scholars disagree, though style itself is generally not considered copyrightable under existing doctrine
- ( ) The artist can sue only if a specific AI-generated output is identical pixel-for-pixel to one of their works

---

## Model 3: Human-AI Creative Collaboration

Generative AI does not only replace human creativity — it increasingly collaborates with it. But collaboration exists on a spectrum.

### The Collaboration Spectrum

| Position | Description | Human Role | Example |
|----------|-------------|-----------|---------|
| **AI as autocomplete** | AI suggests the next word, line, or chunk; human accepts or rejects | Primary creator | GitHub Copilot for code; Gmail Smart Compose |
| **AI as collaborator** | Back-and-forth refinement; human directs, AI proposes, human revises | Co-creator | Iterative image generation with Midjourney; AI-assisted screenwriting |
| **AI as primary with human direction** | AI generates complete artifacts; human provides prompts and selects | Curator/Director | AI-generated novel chapters with human editor selecting and sequencing |
| **AI as sole creator** | Fully autonomous generation with minimal human input | None (or minimal) | AI-composed music released without human review |

### Case Studies

**"Now and Then" (The Beatles, 2023).** Paul McCartney used AI audio separation tools to isolate John Lennon's vocal from a 1970s home demo tape. Peter Jackson's team developed the technology during the "Get Back" documentary. The resulting song included all four original Beatles. Questions of authorship, resurrection of deceased artists' voices, and consent from estates arose.

**AI-assisted novel writing.** Several published novels have used a pipeline of Midjourney (concept art for scene mood), ChatGPT (draft prose), and human editors (selection, revision, voice). At what percentage of AI-generated words does authorship shift?

**AI in drug discovery.** Generative models propose novel molecular structures; human researchers validate computationally, then in wet-lab experiments. AlphaFold and generative chemistry models have shortened drug discovery timelines. Here, AI collaboration is widely seen as beneficial.

### The Diminishing-Returns Hypothesis

As AI reduces the marginal cost of creative production toward zero, the supply of generated content explodes. Economic theory suggests this oversupply drives down the value of average creative work while **increasing** the premium on genuinely novel, contextually embedded, or deeply personal work. The scarcity of authentic human experience and perspective may become more valuable, not less.

### Critical Thinking Questions

**Question 7.** In the "Now and Then" case — is the song a human-created song or an AI-assisted song? Does your answer depend on how you define "the work"? Does it depend on who owns the masters, who receives royalties, or who the listening audience thinks created it? Is there a single correct answer?

[[___ Your answer here ___]]

**Question 8.** If AI can generate 10,000 novels in the time it takes a human to write one, how do readers find the ones worth reading? What new infrastructure, institutions, or practices might emerge to solve the discovery problem? Does your answer suggest that some human roles become more valuable as AI generation scales?

[[___ Your answer here ___]]

**Question 9.** Name one creative domain where AI collaboration is unambiguously beneficial — where the benefits clearly outweigh the harms and the risks are manageable. Explain your reasoning. Then name one domain where you are most uncertain about the net effect of AI, and describe what evidence would help you decide.

[[___ Your answer here ___]]

---

## Exercises

**Exercise 1.** Use an AI tool to generate a creative artifact: a poem, a piece of code, a visual concept description, a short piece of music, or a paragraph of fiction. Then revise it substantially until you feel ownership of the result. Document the process: what did the AI produce, what did you change, and why? At what point in the revision process did you feel it had become "yours"? Write a one-paragraph reflection on the experience.

**Exercise 2.** Find one ongoing or recently decided legal case about AI and copyright (suggestions: Getty Images v. Stability AI, Andersen v. Stability AI, Authors Guild lawsuits against OpenAI, Concord Music Group v. Anthropic). Summarize: (a) who the plaintiff is and what harm they allege, (b) who the defendant is and what fair use or other defense they assert, and (c) the key legal question the court must resolve. You do not need to predict the outcome.

**Exercise 3.** Propose a licensing framework for AI-generated creative work that attempts to balance the interests of four stakeholder groups: (a) creators whose work was used as training data, (b) AI system developers, (c) users who prompt the AI to create outputs, and (d) consumers of the final output. For each group, describe what your framework gives them and what it asks of them. Identify the hardest tradeoff in your framework.

---

## Reflection Prompt

Technology has always changed what creativity means. Photography made portraiture accessible to all and freed painters to become Impressionists. The printing press created an author economy that did not previously exist. Synthesizers made orchestral textures available to musicians without orchestras.

> **Is AI different in kind from these prior disruptions, or different only in degree?** Previous technologies augmented human creative capacity; some argue AI replaces it. What does your answer to that question imply for how society should respond — through law, through education, through market structures, or through some other means?

Write at least one paragraph responding to this prompt. Your Reflector should share your group's key idea during class discussion.

[[___ Your reflection here ___]]

---

## Further Reading

- Boden, M. "The Creative Mind: Myths and Mechanisms." 2nd ed. Routledge, 2004. The foundational text on computational creativity; introduces combinatorial, exploratory, and transformational creativity.

- Epstein, R. "The Empty Brain." Aeon Magazine (2016). A critical perspective on computational metaphors for cognition; useful counterpoint when evaluating AI creativity claims.

- Rothman, J. "Is A.I. Art Stealing from Artists?" The New Yorker, November 14, 2022. Accessible long-form journalism covering the artists' perspective on AI image generation.

- Samuelson, P. "Generative AI Meets Copyright." Science, Vol. 381 (2023). A law professor's analysis of the key legal questions raised by generative AI training and output; concise and authoritative.

- Marcus, G. and Davis, E. "Rebooting AI: Building Artificial Intelligence We Can Trust." Pantheon, 2019. Ch. 6 covers creativity and common sense; useful for contextualizing current generative AI capabilities.
