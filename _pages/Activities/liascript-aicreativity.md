<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-aicreativity.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# AI Creativity: Generative Models, Authorship, and the Nature of Originality

CS357 - Foundations of Artificial Intelligence / Agentic AI | Ursinus College

---

## POGIL Roles

This activity uses the **POGIL** (Process Oriented Guided Inquiry Learning) structure. Assign one role to each group member before beginning.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the group on task, monitors time, ensures everyone contributes, and moves the group to the next question when ready |
| **Recorder** | Writes down the group's agreed answers and keeps a record of key decisions and reasoning |
| **Spokesperson** | Presents the group's answers during class discussion and asks the instructor clarifying questions on behalf of the group |
| **Reflector** | Monitors group process, notes what is working and what is not, and leads the end-of-activity reflection |

> Rotate roles across activities so everyone practices each one.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Combinatorial Creativity** | Producing novel, surprising combinations of familiar elements — the most common everyday form of creativity | A poet connecting "grief" and "software debugging" in a metaphor that makes both feel newly seen |
| **Transformational Creativity** | Changing the rules of a creative domain itself — not just producing something new within existing rules, but rewriting what the rules allow | Cubism didn't just paint differently; it redefined what painting was allowed to represent |
| **Style Mimicry** | Generating new content that imitates the distinctive visual, musical, or written style of a named artist without reproducing any specific original work | Generating an image "in the style of" a living illustrator using only the illustrator's name in a text prompt |
| **Fair Use** | A US copyright doctrine that permits certain uses of copyrighted material without permission, based on four factors including transformativeness and market impact — currently at the center of most AI copyright litigation | Whether training a generative model on millions of copyrighted images constitutes fair use is unresolved in US courts as of 2025 |
| **Moral Rights** | Rights beyond copyright that protect creators' connection to their work — including the right of attribution and the right to object to distortions — stronger in Europe than in the US | A European artist has the right to be credited as the creator of their work even if they have sold the copyright; an AI-mimicked style may violate the spirit of this even if no specific work is copied |
| **Collaboration Spectrum** | The range of human-AI creative relationships, from AI as a minor autocomplete tool to AI as the primary creator with humans only curating the output | GitHub Copilot (AI as autocomplete) vs. a fully autonomous AI music composition released without human review (AI as sole creator) |

---

## Model 1: What Makes Something Creative?

Ask someone whether an AI can be creative and you will get a confident "yes" or a confident "no" — and both confident people are probably thinking about different things when they say "creative." Cognitive scientist Margaret Boden gave the field a more useful tool: not a yes/no question about creativity, but a taxonomy of three different *types* of creativity that do different things and can be evaluated separately. Some of these types AI systems clearly do well; others remain genuinely debated. By the end of this activity, you should be able to say something more precise than "AI is/isn't creative" — you should be able to say *which type* of creativity is at issue in any specific claim.

### Boden's Three Types of Creativity

**Combinatorial creativity:** Producing novel and surprising combinations of familiar elements. Most everyday creativity is combinatorial — a poet connects two concepts that are rarely paired, a chef combines ingredients from different cuisines, a programmer applies a sorting algorithm to a problem it was not designed for. The space of possible combinations is vast but fixed; creativity means navigating it in a surprising and useful direction.

**Exploratory creativity:** Systematically exploring the edges of an existing conceptual space — pushing a style, genre, or tradition to its limits while still operating within its structural rules. A jazz musician improvising within bebop conventions, or a mathematician exploring the implications of a given axiom system, is practicing exploratory creativity. The rules are given; the creativity is in how far the exploration goes.

**Transformational creativity:** Changing the rules of the conceptual space itself — making previously impossible or inconceivable ideas possible by redefining the constraints. Cubism didn't just paint differently; it redefined what painting was allowed to represent. This is rarer and more disruptive than the other two types.

### Can AI Do These?

| Human Creative Act | Type | Can Current AI Do This? | Evidence or Example |
|-------------------|------|--------------------------|---------------------|
| Writing a poem that connects "grief" and "software debugging" in an unexpected metaphor | Combinatorial | Yes — reliably | GPT-class models generate unexpected thematic metaphors on demand |
| Composing jazz variations within the bebop harmonic and rhythmic conventions | Exploratory | Yes — within trained styles | Music generation models trained on genre-specific corpora can extend a style convincingly |
| Inventing haiku as a new poetic form where none previously existed | Transformational | Debated — unclear | A model trained on existing forms may recombine them, not invent new ones |
| Designing a programming language with genuinely novel type-system semantics | Transformational | Not yet demonstrated | AI-assisted PL research exists but all examples remain within known semantic frameworks |

### Critical Thinking Questions

**Question 1.** Consider a computer program that produces sentences by randomly selecting words from a vocabulary. Is its output "creative"? What additional ingredients — beyond mere novelty — seem to be required for something to count as creative? Does the *process* that produced the output matter, or only the output itself?

[[___ Your answer here ___]]

> *Hint:* Random selection produces novelty in a trivial sense — the sentence "purple philosophy sleeps honestly" is novel because it has probably never been written before. But most people would not call it creative. What is missing? Consider: intentionality (did something choose this because it expected it to have a particular effect?), coherence (does it mean something?), appropriateness (is it surprising in a way that resonates with the audience?), and purpose (was it produced to achieve something?). Does the process matter — if a human and a random word-picker both produce the same novel sentence, are they equally creative? Or does the process of searching purposefully through a space of possibilities matter independently of the output?

---

**Question 2.** When a human audience judges something as creative, what role do their expectations and cultural context play in that judgment? Could the exact same output be considered creative in one context and completely uncreative in another? Give a concrete example.

[[___ Your answer here ___]]

> *Hint:* Consider Marcel Duchamp's "Fountain" (1917) — a urinal submitted to an art exhibition. In the context of the avant-garde art world of 1917, it was considered radically creative because it challenged the definition of art itself. The exact same object in a hardware store in 1917 was not creative at all — it was just plumbing. The object did not change; the context and audience expectations did. Now consider: what does this imply about AI-generated poetry being judged as creative? Does it matter whether the audience knows it was written by an AI? Would the same poem be judged more or less creative if audiences knew the process?

---

**Question 3.** Is there any form of human creativity that is purely transformational — with no combinatorial or exploratory elements at all? Or does transformation always build on prior combination and exploration? Use a specific historical example from art, science, music, or mathematics to support your answer.

[[___ Your answer here ___]]

> *Hint:* Consider Einstein's special relativity (1905). It transformed physics by changing what time and space were allowed to mean — a genuinely transformational move. But it built on Lorentz transformations that already existed, on Maxwell's equations that had already been derived, and on the exploratory tradition of thought experiments going back decades. Was the transformation in the specific insight Einstein had, or in the combination of existing elements into a new framework? Is it possible to have transformation *without* any prior combination and exploration, or does transformational creativity always require standing on the shoulders of combinatorial and exploratory work?

---

With Boden's framework in hand for evaluating creative claims, you are ready to examine the legal and ethical landscape that forms the context in which AI creativity is currently being deployed and contested.

## Model 2: Copyright, Attribution, and the Artist's Dilemma

The rise of generative AI has created a legal and ethical crisis in creative fields. Three separate issues are often conflated in public debate, but they must be kept distinct because they have different legal frameworks, different affected parties, and different potential remedies.

### 1. Training on Copyrighted Work

When an AI company scrapes copyrighted images, books, or music to train a model, is that infringement? The legal question is whether training constitutes a reproduction of the original work, or a "transformative use" protected under the US fair use doctrine, or a permissible "text-and-data mining" activity under EU law. Key active cases include **Getty Images v. Stability AI** (filed 2023), **Andersen v. Stability AI** (illustrators' class action), and several consolidated author class actions against OpenAI and Meta.

The **training/output distinction** matters legally: even if training is eventually found to infringe, a specific AI output that does not reproduce copyrightable expression from a specific work may itself be non-infringing. And even if training is found to be fair use, an AI output that is substantially similar to a specific work it was trained on could still infringe that specific work's copyright.

### 2. Style Mimicry

AI systems can generate output explicitly "in the style of" a named living artist. Under current US copyright law, **style itself is generally not copyrightable** — only specific original expression is. You cannot copyright "impressionism" or "Hemingway's prose style" as such. But many artists feel their livelihood is directly undermined when their distinctive style can be replicated at scale by anyone with a text prompt, without payment, permission, or attribution.

**Moral rights** (recognized more broadly in Europe than the US) include the right of attribution (the right to be identified as the creator of your work) and the right of integrity (the right to object to distortions or modifications). Some argue that AI style mimicry at scale violates the spirit of moral rights even where it doesn't technically violate copyright law.

### 3. Attribution and Disclosure

| Creative Domain | What AI Can Do at Scale | Legal or Ethical Issue | Current Industry Practice |
|----------------|-------------------------|----------------------|--------------------------|
| **Visual art** | Generate images in a named living artist's distinctive style | Style mimicry; training on unlicensed work; displacement of commissioned work | No universal standard; platforms vary widely on disclosure requirements |
| **Literature** | Generate text at book length; ghost-write articles or academic work | Disclosure to readers; academic integrity; potentially misleading consumers about authorship | Academic journals increasingly require disclosure; fiction publishers vary |
| **Music** | Generate instrumentals; clone a specific voice from a small sample | Voice likeness rights; sound-alike recordings that may deceive listeners | AI music platforms emerging; voice cloning legal status unsettled |
| **Journalism** | Draft articles; summarize and paraphrase sources | Factual accuracy responsibility; disclosure of AI's role in production | Major news outlets have varying and evolving disclosure policies |
| **Film and TV** | Generate scripts; de-age or digitally resurrect actors | SAG-AFTRA consent and compensation protections; estates' control over deceased performers' likenesses | Under active negotiation since the 2023 strikes; some protections now in contracts |

> ⚠️ **Common Misconception:** Many students assume that "AI-generated content cannot be copyrighted" or "AI-generated content is always in the public domain." The legal reality is more complex. In the US, the Copyright Office has stated that purely AI-generated content with no human creative input is not copyrightable. But work where a human makes specific creative choices — selecting, arranging, editing, and directing AI outputs — may be protectable to the extent of the human creative contribution. The exact threshold of human involvement required for copyright protection is actively being litigated and determined through Copyright Office guidance as of 2025.

### Critical Thinking Questions

**Question 4.** If an AI generates an image using a model trained on 5 million images as training data, and no single training image can be identified as a direct visual template for the output, has copyright infringement occurred? What legal test would you apply, and what additional facts would you need to know to apply it?

[[___ Your answer here ___]]

> *Hint:* US copyright infringement requires showing: (1) the plaintiff owned a valid copyright in the original work; (2) the defendant copied protected expression from that work. The second element is usually proven through showing access (the defendant saw the work) and substantial similarity (the output is too similar to be coincidental). At mass scale, access is trivially established — the model trained on the web clearly had access. The harder question is substantial similarity: if no specific work can be identified as the source of any specific output, is there infringement? Some legal scholars argue that the *training process itself* is the infringement, not the specific output. Others argue only output-level similarity matters. What additional facts would change your analysis?

---

**Question 5.** A musician has spent 20 years developing a distinctive vocal style and has posted hundreds of recordings publicly online. An AI company trains a voice-cloning model on those recordings without asking permission. The company generates no tracks that are identical to the musician's recordings. Why might the musician still feel — and arguably be — harmed? What interests beyond copyright are at stake?

[[___ Your answer here ___]]

> *Hint:* The musician's interests go beyond copyright: (1) **Economic harm** — if AI can generate unlimited music "in their voice" at zero marginal cost, the market for their recordings may collapse even if no specific recording is infringed; (2) **Right of publicity** — some jurisdictions protect the commercial use of a person's voice, name, and likeness independently of copyright; (3) **Autonomy and consent** — the musician may have views about what messages, genres, or contexts their voice should be associated with, and voice cloning removes their ability to control this; (4) **Dignity** — having one's voice used to generate content one would personally find offensive or objectionable. Which of these interests, if any, are addressed by existing law? Which require new law?

---

**Question 6.** Propose a specific attribution policy for AI-assisted creative work that you consider fair to all parties. Your policy must address: (a) what creators of training data are owed, (b) what AI system developers are permitted to do without additional compensation, and (c) what users who produce AI-assisted work must disclose to audiences and consumers. Defend each of your three choices explicitly.

[[___ Your answer here ___]]

> *Hint:* This is a genuine design challenge with tradeoffs at every step. Consider: creators of training data could be owed nothing (current US law leans this way), a one-time license payment, or an ongoing royalty every time their work influenced a generation. AI developers might be permitted to train on publicly posted work without permission (transformative use argument) or might be required to use only licensed or public-domain works. Users might be required to disclose AI assistance whenever more than X% of the final work was AI-generated — but how do you measure that percentage? Choose specific positions and defend them. Identify the hardest tradeoff in your policy.

---

### Multiple Choice Question

An artist claims that an AI system was trained on their publicly posted portfolio without consent and now generates work that looks strikingly similar to their distinctive visual style. Under current US copyright law as of 2025, the most accurate statement is:

[[ ]] The AI system owner is clearly liable for copyright infringement because they used the artist's work without a license during training
[[ ]] The artist has no legal recourse whatsoever because publicly posted content is in the public domain and can be used for any purpose
[[x]] The legal status is genuinely unsettled; multiple court cases are actively pending and legal scholars disagree, though style itself is generally not considered copyrightable under existing doctrine
[[ ]] The artist can only sue if an AI-generated output is found to be identical pixel-for-pixel to one of their specific original works

> **Why this answer?** As of 2025, no US court has issued a final ruling on whether training generative AI models on copyrighted works constitutes infringement. The cases are ongoing. Style — as distinct from specific original expression — has historically not been protectable under US copyright law: you cannot copyright "impressionism" or "a distinctive color palette." But whether training on copyrighted work constitutes fair use is an open question, and the answer may differ depending on the scale of copying, the commercial purpose, and the market impact on the original creator. "Publicly posted" does not mean "in the public domain" — copyright attaches automatically to original creative work at the moment of creation, not upon registration or upon certain types of publication.

---

The legal debates around training data and style mimicry set the stage for understanding the full spectrum of ways humans and AI systems can work together creatively — which is where you have the most direct agency as a builder.

## Model 3: Human-AI Creative Collaboration

Generative AI does not only replace human creativity — increasingly it collaborates with it in ways that exist along a broad spectrum. Where any particular human-AI creative relationship falls on that spectrum determines questions of authorship, attribution, copyright, and how to evaluate the work's quality.

### The Collaboration Spectrum

| Position | Description | The Human's Role | Concrete Example |
|----------|-------------|-----------------|-----------------|
| **AI as autocomplete** | AI suggests the next word, line, or chunk; human accepts, modifies, or rejects each suggestion | Primary creator — the human drives all high-level decisions | GitHub Copilot completing a function body; Gmail Smart Compose finishing a sentence |
| **AI as creative collaborator** | Back-and-forth refinement between human and AI; human directs and revises, AI proposes and extends | Co-creator — creative decisions are genuinely shared | Iterative image generation in Midjourney with human prompt refinement; AI-assisted screenwriting with human editing |
| **AI as primary creator with human direction** | AI generates complete artifacts; human provides prompts, selects among outputs, and sequences the final work | Curator and director — creative authorship is mostly in the curation decisions | AI-generated novel chapters with a human editor selecting, sequencing, and revising |
| **AI as sole creator** | Fully autonomous generation with minimal human input beyond system configuration | None meaningful — human is closer to a programmer than a creator | Fully automated AI music composition or stock image generation released without human review of individual outputs |

### Case Studies

**"Now and Then" (The Beatles, 2023).** Paul McCartney used AI audio separation technology — developed by Peter Jackson's team during the "Get Back" documentary — to isolate John Lennon's vocal track from a 1970s home demo tape of low audio quality. The resulting song was completed with contributions from all four original Beatles, including archived guitar parts from George Harrison. Questions of authorship (is a 50-year-old reconstructed performance an authored contribution?), the resurrection of a deceased artist's voice, and consent from estates all arose simultaneously. Was this restoration or creation? Does the answer change if the voice was 95% AI-reconstructed rather than 30% AI-reconstructed?

**AI-assisted novel writing.** Several published novels have used a pipeline of AI tools: Midjourney for concept art to establish scene mood, a language model for draft prose, and human editors for selection, revision, voice, and coherence. At what percentage of AI-generated words does authorship shift meaningfully? Does the answer change if the human's contribution is primarily *choosing* among AI outputs rather than writing prose directly?

**AI in drug discovery.** Generative models propose novel molecular structures; human researchers validate computationally and then through wet-lab experiments. AlphaFold's protein structure predictions and generative chemistry models have dramatically shortened drug discovery timelines. Here, AI collaboration is widely seen as unambiguously beneficial — the AI generates candidates, humans verify and make deployment decisions. Does the fact that lives are saved change the ethical calculus around the collaboration?

### The Diminishing-Returns Hypothesis

As AI reduces the marginal cost of generating creative content toward zero, the supply of generated content explodes. Economic theory suggests that the oversupply of algorithmically generated content will drive down the value of average-quality creative work, while simultaneously **increasing** the premium on work that is genuinely novel, contextually embedded, or deeply rooted in specific human experience. The scarcity of authentic human perspective and embodied experience may become *more* economically valuable, not less, as AI-generated content floods the market. This is not guaranteed — it depends on whether consumers can distinguish AI-generated from human-generated work, and whether they care to.

### Critical Thinking Questions

**Question 7.** In the "Now and Then" case — is the song a human-created song or an AI-assisted song? Does your answer depend on how you define "the work" — the final mixed recording, the original demo, the performance decisions, the songwriting? Does it depend on who owns the masters, who receives royalties, or what the listening audience believes about how it was made? Is there a single objectively correct answer, or is this a case where the question itself reveals the limits of our existing categories?

[[___ Your answer here ___]]

> *Hint:* The song's elements are: Lennon's 1970s vocal performance (clearly human-authored, though AI-processed to extract it); McCartney's new bass parts (human-authored in 2023); Harrison's archived guitar parts (human-authored before his death); Starr's new drums (human-authored in 2023); the AI audio separation that made the restoration possible (tool or co-creator?). Different definitions of "the work" (the songwriting, the performances, the production) give different answers about AI's role. Compare this to how we think about film: a director doesn't operate the camera, light the scene, or edit the footage — yet we unambiguously attribute authorship to the director. What makes directorial creative choices authorship while AI prompt choices might not be?

---

**Question 8.** If AI can generate 10,000 novels in the time it takes a human to write one, how do readers find the ones worth reading? What new infrastructure, institutions, or practices might emerge to solve the discovery and curation problem? Do your answers suggest that some human roles become *more* valuable as AI generation scales, not less?

[[___ Your answer here ___]]

> *Hint:* When the cost of content creation drops to near zero, the bottleneck shifts from creation to curation and discovery. Think about what already exists for other content-oversupply problems: streaming algorithms that surface music from millions of tracks; editorial teams that curate from thousands of submissions; Goodreads reviewers who read widely and share recommendations. Would any of these scale to a world with 10 million new AI-generated novels per day? What new roles might emerge: AI-output curators, provenance verifiers who certify human authorship, specialized critics for different AI-generation aesthetics? Does the human whose judgment you trust to curate become more valuable than the human who wrote?

---

**Question 9.** Name one creative domain where AI collaboration is unambiguously beneficial — where the benefits clearly outweigh the harms and the risks are manageable enough that you would not hesitate to recommend it. Explain your reasoning. Then name one domain where you are most uncertain about the net effect, and describe specifically what evidence would help you decide.

[[___ Your answer here ___]]

> *Hint:* For the unambiguously beneficial case, consider domains where: the creative task has a clear, measurable outcome (the drug works or it doesn't; the code runs or it doesn't); human expertise remains in the loop for all deployment decisions; the AI accelerates exploration without replacing human judgment; and the people affected by the outcome have consented to AI involvement. For the uncertain case, consider domains where: the line between augmentation and replacement is unclear; the audiences who consume the output cannot tell whether AI was involved; the economic effects on human practitioners are severe and concentrated; or the creative choices encode values that matter deeply to communities who were not consulted. What specific data would change your uncertainty into a clearer assessment?

---

## Exercises

**Exercise 1.**

*What to do:* Use an AI tool to generate a creative artifact and then revise it substantially until you feel genuine ownership of the result. Then reflect carefully on the process.

*Starter hint:* Try this specific creative prompt to generate a starting point: "Write a short poem (8–12 lines) about the experience of debugging code at 2 AM, using extended metaphors from nature — storms, erosion, something slow and inevitable. Do not rhyme." Take the poem the AI generates and revise it: change specific word choices that don't feel right, add an image from your own experience, cut lines that feel generic, shift the ending to land differently. Keep revising until you feel you would be willing to put your name on it.

*You've succeeded when:* You have documented (a) the exact AI-generated original, (b) your final revised version, (c) a line-by-line or section-by-section account of what you changed and why, and (d) a one-paragraph reflection on the point in the process — if there was one — where you felt the work shift from "the AI's poem I'm editing" to "my poem that started from an AI draft." If that shift never happened, explain why not.

---

**Exercise 2.**

*What to do:* Find one ongoing or recently decided legal case about AI and copyright. Research the case using primary and secondary sources and write a structured summary.

*Starter hint:* Good cases to research (search by name): Getty Images v. Stability AI (visual artists, UK and US cases running in parallel); Andersen v. Stability AI (illustrator class action, ongoing); Authors Guild class action against OpenAI (book authors, multiple consolidated cases); Concord Music Group v. Anthropic (song lyrics in AI outputs). For each case, look for: the original complaint (available on PACER or summarized in legal news), any published opinions or orders, and commentary by intellectual property law professors or practitioners.

*You've succeeded when:* Your summary covers: (a) who the plaintiff is and what specific harm they allege in concrete terms; (b) who the defendant is and what specific legal defense they assert (fair use? lack of substantial similarity? something else?); and (c) the central legal question the court must resolve — stated precisely enough that someone unfamiliar with the case could understand what outcome would matter and why. You do not need to predict the outcome.

---

**Exercise 3.**

*What to do:* Propose a licensing framework for AI-generated creative work that attempts to balance the interests of four stakeholder groups. Write your framework as a structured policy document.

*Starter hint:* Your four stakeholder groups are: (1) Creators whose work was used as training data — what are they owed, and is it practical to identify and compensate them individually? (2) AI system developers — what uses are permitted without additional licensing, and what requires explicit permission? (3) Users who prompt AI to produce outputs — what are their rights to the outputs they direct? (4) Consumers and audiences of the final creative work — what do they have a right to know about how it was made? For each group, first identify what they most want, then identify what constraint from another group makes getting everything they want impossible. Your hardest tradeoff is probably between groups 1 and 2.

*You've succeeded when:* Your framework document specifies what each of the four stakeholder groups receives and what it asks of them, identifies the hardest tradeoff in the framework and defends your resolution of it, and is written precisely enough that someone could reasonably agree or disagree with each specific provision.

---

## Reflection Prompt

**Personal:** Have you used AI for a creative task — writing, coding, design, music? If so, how did it feel compared to working without AI? Did the output feel like yours? If you haven't used AI creatively, describe what you imagine the experience would feel like, and what would determine whether the result felt authentic.

**Technical:** Technology has always changed what creativity means. Photography made realistic portraiture available to everyone and freed painters to become Impressionists. The printing press created an author economy that did not previously exist. Synthesizers made orchestral textures available to solo musicians without orchestras. Is AI different in kind from these prior disruptions, or different only in degree? Previous technologies augmented human creative capacity — does AI do the same, or does it replicate it? What specifically would make AI different in kind rather than degree?

**Societal:** Creative work supports livelihoods. Illustrators, novelists, voice actors, musicians, and journalists depend on being paid for creative output. If AI makes their specific form of creative output freely and abundantly available, what happens to them economically — and does society have an obligation to respond? Should that response come through law (copyright reform, AI royalty frameworks), through market structures (platforms that prioritize human-made content), through education (training people for post-AI creative roles), or through some other mechanism?

Write at least 200 words addressing at least two of the three levels above. Your Reflector should be prepared to share your group's key idea during class discussion.

[[___ Your reflection here ___]]

---

→ Coming Up Next: This was the final activity in the series. Bring your reflections to the course's final discussion: what does it mean to build AI systems responsibly, and what role do you want to play in that work?

## Further Reading

- Boden, M. "The Creative Mind: Myths and Mechanisms." 2nd ed. Routledge, 2004. The foundational text on computational creativity; introduces combinatorial, exploratory, and transformational creativity with extensive examples.

- Epstein, R. "The Empty Brain." Aeon Magazine (2016). A critical perspective on computational metaphors for cognition; useful counterpoint when evaluating strong claims about AI creativity.

- Rothman, J. "Is A.I. Art Stealing from Artists?" The New Yorker, November 14, 2022. Accessible long-form journalism covering the artists' perspective on AI image generation and style mimicry.

- Samuelson, P. "Generative AI Meets Copyright." Science, Vol. 381 (2023). A law professor's concise and authoritative analysis of the key legal questions raised by generative AI training and output.

- Marcus, G. and Davis, E. "Rebooting AI: Building Artificial Intelligence We Can Trust." Pantheon, 2019. Chapter 6 covers creativity and common sense; useful for contextualizing current generative AI capabilities and limitations.
