# AI and the Future of Work: Automation, Displacement, and Adaptation

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-socialimpact.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

**CS357: Foundations of Artificial Intelligence / Agentic AI**
Ursinus College

---

## POGIL Roles

In this activity, your team will work together using the following roles. Rotate roles with each new activity.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the team on task and on time; ensures everyone contributes; calls for consensus before moving on |
| **Recorder** | Writes down the team's agreed answers; manages the shared document or whiteboard |
| **Presenter** | Speaks for the team during class discussion; summarizes findings to the class |
| **Reflector** | Monitors team process; notes what is working and what is not; leads the Reflection section |

> Before starting, confirm your roles aloud. If your team has fewer than 4 members, one person may take two roles (e.g., Manager + Reflector).

---

## Model 1: The Automation Wave — Historical and Contemporary

Throughout history, technology has repeatedly transformed the labor market. The fear that machines would eliminate work is as old as industrialization itself — the Luddites of the 1810s smashed textile looms, fearing for their livelihoods. Yet aggregate employment did not disappear; it shifted.

A striking contemporary example: when ATMs were introduced in the 1970s–80s, observers predicted the end of bank tellers. Instead, teller employment *grew* over the following decades. Why? ATMs reduced the cost of running a bank branch, so banks opened more branches, which required more tellers — now focused on customer relationships and complex transactions rather than cash handling. This is one instance of the **productivity paradox**: automation can increase employment in the very occupation it targets by expanding demand for the overall service.

The table below summarizes four historical automation eras:

| Era | Representative Technology | Jobs Displaced | Jobs Created | Net Effect Estimate |
|-----|--------------------------|----------------|--------------|---------------------|
| **Mechanization** (1760–1850) | Steam power, textile mills | Hand-weavers, artisan crafts | Factory operatives, mechanics, engineers | Positive long-run; severe short-run dislocation |
| **Electrification** (1880–1940) | Electric motors, assembly lines | General laborers doing low-skill tasks | Machine operators, electricians, logistics workers | Broadly positive; geography uneven |
| **Computerization** (1960–2000) | Mainframes, PCs, industrial robots | Bookkeepers, typists, routine manufacturing | Software engineers, data analysts, IT support | Positive overall; hollowed out middle-skill jobs |
| **AI / ML** (2010–present) | LLMs, computer vision, generative AI | Radiologists (some tasks), paralegals (some tasks), coders (some tasks) | Prompt engineers, AI trainers, oversight roles | Uncertain; potentially faster than prior waves |

### Critical Thinking Questions

**Question 1.** The ATM example shows that automation of a task does not necessarily reduce employment in that occupation. Using the concept of *demand elasticity*, explain in your own words why ATM adoption actually increased the number of bank tellers employed.

[[___ Your answer here ___]]

**Question 2.** Each prior automation wave caused significant short-run hardship even when the long-run employment outcome was positive. Does the fact that humanity "survived" prior automation waves guarantee that AI will produce a similar positive outcome? What assumptions must hold for the historical analogy to apply?

[[___ Your answer here ___]]

**Question 3.** Looking at the table, identify at least two ways that LLM-driven automation in the AI era differs from the computerization era. Focus on *which* tasks are now automatable and how quickly the transition may occur.

[[___ Your answer here ___]]

---

## Model 2: Who Gets Displaced and Who Benefits?

The standard economic story of automation — **skill-biased technical change** — holds that technology tends to automate *routine* tasks (assembly line work, data entry) while *complementing* non-routine cognitive tasks (creative work, management, judgment). This explains why, from 1980 to 2010, demand for college-educated workers rose sharply.

AI may invert this pattern. LLMs excel at exactly the non-routine cognitive tasks that economists thought were automation-proof: drafting text, analyzing documents, writing code, answering legal questions. Meanwhile, tasks requiring physical dexterity in unpredictable environments — plumbing, electrical work, carpentry — remain difficult to automate.

| Occupation | AI Displacement Risk | Reason | What AI Currently Does to This Role |
|------------|---------------------|--------|-------------------------------------|
| Radiologist | High (partial) | Image classification is mature; AI matches or exceeds humans on specific scans | Screens routine scans; flags anomalies; reduces reads per radiologist |
| Paralegal | High | Document review, contract analysis, legal research are language tasks | Drafts discovery requests; reviews contracts; summarizes case law |
| Software Developer | Medium | Code generation is strong but requirements gathering and architecture remain hard | Autocompletes code; generates boilerplate; catches bugs in review |
| Plumber | Low | Physical dexterity in novel environments; each job is unique | Scheduling software; diagnostic tools; no direct task automation |
| Nurse | Low–Medium | Empathy, physical care, dynamic judgment are hard to replicate | Documentation assistance; medication alerts; triage support tools |
| Graphic Designer | Medium–High | Generative image models produce professional-quality output on demand | Generates concept art; creates image variations; automates resizing |

### Critical Thinking Questions

**Question 4.** Examine the table. Prior to AI, higher education generally *reduced* automation risk. Based on the table, does that pattern still hold? Identify at least one occupation where higher formal education does *not* protect against AI displacement risk, and explain why.

[[___ Your answer here ___]]

**Question 5.** Identify one occupation from the table (or from your own knowledge) where AI is likely to *create more work* rather than simply replace existing work. Explain the mechanism — why does AI assistance expand the demand for this role rather than contract it?

[[___ Your answer here ___]]

**Question 6.** "Automation risk" (the technical capability to automate a task) and "automation happening" (that task actually being automated at scale) are different things. List two factors — other than technical capability — that determine whether automation actually occurs in a given occupation.

[[___ Your answer here ___]]

---

Which of the following best explains the labor-economics effect of AI coding assistants (e.g., GitHub Copilot) that allow developers to complete tasks approximately 55% faster?

- ( ) Immediate mass unemployment of software developers, since fewer are needed to produce the same amount of code
- (x) Increased demand for developers, because software becomes cheaper to produce and therefore more of it gets built
- ( ) No meaningful change in developer employment, since the productivity gain is offset by quality degradation
- ( ) Developers being fully replaced by the tools within two years as capability continues to scale

---

## Model 3: Policy Responses and Student Agency

Governments, firms, and individuals have several tools to respond to labor displacement from automation. The table below compares five policy approaches:

| Policy Response | What It Addresses | Who It Helps Most | Who Pays | Political Feasibility |
|-----------------|------------------|-------------------|----------|-----------------------|
| **Education and reskilling programs** | Skills mismatch; workers whose jobs are displaced need new skills | Displaced workers willing and able to retrain | Governments, employers | Moderate — widely supported in principle, hard to scale |
| **Portable benefits** | Benefits tied to jobs, not employers, so gig/contract workers are protected | Part-time, freelance, and displaced workers | Employers, consumers via prices | Low–Moderate — opposed by firms that benefit from status quo |
| **Universal Basic Income (UBI)** | Income floor regardless of employment status | All citizens, especially low-income workers | Taxpayers; requires significant redistribution | Low — polarizing; pilot programs exist but no large-scale adoption |
| **Tax on automation** (robot tax) | Funds displaced worker assistance; slows automation pace | Displaced workers and communities | Firms adopting automation | Low — widely opposed by business; rarely implemented |
| **Working-time reduction** | Share available work across more workers; 4-day workweek proposals | Employed workers; reduces overwork | Firms (lower output per week unless productivity rises enough) | Moderate — gaining traction in some countries |

### Critical Thinking Questions

**Question 7.** As a computer science student who is learning to build AI systems, consider your own position in the labor market. Does studying AI tools and agentic systems make you *more* or *less* vulnerable to automation — or does the answer depend on factors beyond what you study? Explain your reasoning.

[[___ Your answer here ___]]

**Question 8.** Suppose you are advising a national government facing significant AI-driven job displacement over the next decade. Choose **two** policies from the table above (or propose your own) and explain why that combination addresses displacement more effectively than either policy alone.

[[___ Your answer here ___]]

**Question 9.** The people building automation technologies — including computer science students like you — are in a position to foresee displacement effects before they happen. What ethical obligations, if any, do AI builders have toward workers who will be displaced by systems they create? Are those obligations enforceable, and by whom?

[[___ Your answer here ___]]

---

## Exercises

**Exercise 1.** Using the Bureau of Labor Statistics Occupational Outlook Handbook (bls.gov/ooh), look up employment projections for three careers you have personally considered. Then find their AI exposure scores on the Felten, Raj, and Seamans (2023) occupational exposure scale or a comparable index. For each occupation, write 2–3 sentences comparing the BLS projection with the AI exposure rating.

[[___ Your answer here ___]]

**Exercise 2.** Interview a family member, friend, or classmate about a task they perform regularly at work (paid or unpaid). Sketch, in plain language or pseudocode, an agent that could automate at least part of that task. Then identify at least two forms of human judgment or contextual knowledge that your agent would lack and that could cause it to fail or cause harm.

[[___ Your answer here ___]]

**Exercise 3.** Research one real company that has publicly attributed layoffs — at least partially — to the adoption of AI automation (examples exist in customer service, media, and financial services sectors). Evaluate the credibility of the claim: Is the timing consistent? Did the company provide data? Are there alternative explanations for the layoffs? Write a 150–200 word assessment.

[[___ Your answer here ___]]

---

## Reflection Prompt

You are studying artificial intelligence — the technology at the center of the displacement debate. That puts you in an unusual position: you are learning to build the systems that may automate work across many sectors.

Does that make you **part of the problem**, **part of the solution**, or **both**? What specific responsibilities, if any, come with that position — to your future employers, to users of the systems you build, and to workers whose livelihoods may be affected? Write a personal reflection of 150–250 words. The Reflector on your team should be prepared to share a key insight with the class.

[[___ Your reflection here ___]]

---

## Further Reading

- Acemoglu, D., and Restrepo, P. (2019). "Automation and New Tasks: How Technology Displaces and Reinstates Labor." *Journal of Economic Perspectives*, 33(2), 3–30.
- Felten, E., Raj, M., and Seamans, R. (2023). "Occupational Heterogeneity in Exposure to Generative AI." *SSRN Working Paper*.
- Acemoglu, D. (2024). "The Simple Macroeconomics of AI." *NBER Working Paper No. 32122*.
- Autor, D. (2015). "Why Are There Still So Many Jobs? The History and Future of Workplace Automation." *Journal of Economic Perspectives*, 29(3), 3–30.
- Brynjolfsson, E., and McAfee, A. (2014). *The Second Machine Age*. W. W. Norton.
