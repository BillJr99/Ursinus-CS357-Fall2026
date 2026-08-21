<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-socialimpact.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# AI and the Future of Work: Automation, Displacement, and Adaptation

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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Automation displacement** | When a technology takes over tasks previously done by human workers, reducing demand for those workers in that role | ATMs handling cash withdrawals, which used to require a human teller; LLMs drafting legal memos, which used to require a paralegal |
| **Productivity paradox** | The counterintuitive finding that automating a task sometimes *increases* total employment in that occupation, because automation lowers costs and expands overall demand | ATMs reduced per-branch teller costs, so banks opened more branches, which needed more tellers; teller employment actually grew |
| **Skill-biased technical change** | The economic pattern where technology tends to automate routine tasks (assembly line, data entry) while complementing higher-skill cognitive work (design, management, judgment), meaning tech historically raised wages for educated workers | PC adoption in the 1980s-90s raised demand for workers who could use computers, while automating tasks like typing pool work |
| **AI exposure** | An index measuring how much of an occupation's task bundle could be performed or assisted by current AI systems | Paralegals score high exposure because document review, research, and drafting are all language tasks LLMs handle well |
| **Labor demand elasticity** | How much total demand for a service (and therefore workers) grows when its price drops due to automation | When legal research got cheaper, demand for legal services grew, partially offsetting the per-task automation of paralegal work |
| **Just transition** | The principle that workers displaced by technology deserve support in adapting (reskilling, income protection, and community investment), not just acknowledgment that the long run is positive | Government-funded retraining programs for coal miners when power generation shifted to natural gas and renewables |

---

## Model 1: The Automation Wave - Historical and Contemporary

You are studying AI while it reshapes the job market you are about to enter. That is not a neutral position. Every technology wave in history displaced some workers and created others, but the speed, breadth, and white-collar nature of AI automation may make this wave different from the ones that came before. Understanding the historical pattern (what has happened, and why) puts you in a much better position to make decisions about your own career and about the systems you build.

Throughout history, technology has repeatedly transformed the labor market. The fear that machines would eliminate work is as old as industrialization itself; the Luddites of the 1810s smashed textile looms, fearing for their livelihoods. Yet aggregate employment did not disappear; it shifted.

A striking contemporary example: when ATMs were introduced in the 1970s-80s, observers predicted the end of bank tellers. Instead, teller employment *grew* over the following decades. Why? ATMs reduced the cost of running a bank branch, so banks opened more branches, which required more tellers, now focused on customer relationships and complex transactions rather than cash handling. This is one instance of the **productivity paradox**: automation can increase employment in the very occupation it targets by expanding demand for the overall service.

The table below summarizes four historical automation eras:

| Era | Representative Technology | Jobs Displaced | Jobs Created | Net Effect | Speed of Transition |
|-----|--------------------------|----------------|--------------|------------|---------------------|
| **Mechanization** (1760-1850) | Steam power, textile mills | Hand-weavers, artisan crafts who made goods by hand in small workshops | Factory operatives, mechanics, engineers who maintained and operated the new machines | Positive long-run; severe short-run dislocation: entire communities lost their livelihoods over one generation | Slow by modern standards; took decades to diffuse across regions |
| **Electrification** (1880-1940) | Electric motors, assembly lines | General laborers doing low-skill tasks that electric motors could power more cheaply | Machine operators, electricians, logistics workers coordinating faster supply chains | Broadly positive; but geographically uneven: rural areas and some industrial cities lagged | Moderate; infrastructure buildout took 30-40 years to reach most workers |
| **Computerization** (1960-2000) | Mainframes, PCs, industrial robots | Bookkeepers, typists, routine manufacturing workers on assembly lines | Software engineers, data analysts, IT support, and new categories of knowledge work that didn't exist before | Positive overall; but hollowed out middle-skill jobs: created a "barbell" labor market with high-skill and low-skill work but fewer middle-wage jobs | Moderate to fast; PC adoption by firms took about 20 years |
| **AI / ML** (2010-present) | LLMs, computer vision, generative AI | Radiologists (some diagnostic tasks), paralegals (document review), coders (boilerplate generation), graphic designers (image generation), customer service agents | Prompt engineers, AI trainers, AI oversight roles, AI product managers, new roles we haven't named yet | Uncertain; early signs suggest faster disruption of white-collar work than prior waves | Potentially very fast: GPT-3 to GPT-4 in two years; firms are adopting at record speed |

### Critical Thinking Questions

**Question 1.** The ATM example shows that automation of a task does not necessarily reduce employment in that occupation. Using the concept of *demand elasticity*, explain in your own words why ATM adoption actually increased the number of bank tellers employed.

*Hint:* ATMs made cash withdrawal cheaper; each branch needed fewer tellers to handle routine transactions. But that cost reduction made it economically worthwhile to open branches in locations that were previously too expensive. More branches means more total tellers, even with fewer per branch. When the price of a service drops and total demand grows enough to offset the per-unit reduction in labor, we say demand is "elastic." Does the same logic apply to software development with AI coding assistants?

**Question 2.** Each prior automation wave caused significant short-run hardship even when the long-run employment outcome was positive. Does the fact that humanity "survived" prior automation waves guarantee that AI will produce a similar positive outcome? What assumptions must hold for the historical analogy to apply?

*Hint:* Think about what made prior waves ultimately positive: new industries absorbed displaced workers, transitions happened slowly enough for workers to retrain, and government and social institutions adapted. Are those conditions present today? Consider: a textile worker displaced in 1820 might retrain over a decade; a paralegal displaced in 2026 has a much shorter window before the next wave arrives.

**Question 3.** Looking at the table, identify at least two ways that LLM-driven automation in the AI era differs from the computerization era. Focus on *which* tasks are now automatable and how quickly the transition may occur.

*Hint:* Computerization automated *routine* tasks: well-defined processes with clear rules (like bookkeeping). LLMs automate *non-routine cognitive* tasks: things economists thought were safe, like writing, analysis, and judgment. Also look at the "Speed of Transition" column: what changed between the computerization era and today?

---

With the historical context of automation waves in hand, you are ready to examine which specific occupations face the highest AI displacement risk today, and why the pattern differs from previous technological transitions.

## Model 2: Who Gets Displaced and Who Benefits?

The standard economic story of automation (**skill-biased technical change**) holds that technology tends to automate *routine* tasks (assembly line work, data entry) while *complementing* non-routine cognitive tasks (creative work, management, judgment). This explains why, from 1980 to 2010, demand for college-educated workers rose sharply.

AI may invert this pattern. LLMs excel at exactly the non-routine cognitive tasks that economists thought were automation-proof: drafting text, analyzing documents, writing code, answering legal questions. Meanwhile, tasks requiring physical dexterity in unpredictable environments (plumbing, electrical work, carpentry) remain difficult to automate.

| Occupation | AI Displacement Risk | Reason | What AI Currently Does to This Role | In Our Course Context |
|------------|---------------------|--------|-------------------------------------|----------------------|
| Radiologist | High (partial) | Image classification is mature; AI matches or exceeds humans on specific diagnostic scans | Screens routine scans automatically; flags anomalies for human review; reduces the number of reads per radiologist | FDA-cleared AI tools like Viz.ai already route stroke scans ahead of human reads |
| Paralegal | High | Document review, contract analysis, and legal research are fundamentally language tasks | Drafts discovery requests; reviews contracts for standard clauses; summarizes case law across hundreds of documents | Harvey AI and Casetext are already deployed at major law firms |
| Software Developer | Medium | Code generation is strong for boilerplate and common patterns, but requirements gathering, system architecture, and debugging novel failures remain hard | Autocompletes code; generates tests; catches common bugs in code review; explains existing code | GitHub Copilot reports ~55% of code accepted in some studies; CS graduates using it ship faster but still make architectural decisions |
| Plumber | Low | Physical dexterity in novel, unpredictable environments; every job site is different; no two pipe configurations are the same | Scheduling software; diagnostic tools that suggest likely failure points; no direct task automation yet | Robots that can reliably navigate a random home's pipes do not exist at commercial scale |
| Nurse | Low-Medium | Empathy, physical care, and dynamic clinical judgment in changing patient conditions are hard to replicate | Documentation assistance; medication interaction alerts; triage support tools that flag high-risk patients | AI scribes like Nuance DAX transcribe patient visits, reducing documentation burden, but nurses make the care decisions |
| Graphic Designer | Medium-High | Generative image models (Midjourney, DALL-E, Stable Diffusion) produce professional-quality visual output in seconds | Generates concept art from text prompts; creates image variations; automates asset resizing and localization | Entry-level "production design" work (resizing ads, creating variations) is heavily automated; art direction and client relationship management are not |

> **Common Misconception:** Many students assume that studying computer science or a STEM field guarantees protection from AI displacement. The table above shows this is not true. Software development, data analysis, and technical writing (all strongly associated with STEM degrees) are in the medium-to-high exposure range. What appears to protect workers is not the *prestige* of their field but the *physical unpredictability* of their tasks and the *depth of human judgment* required per decision.

### Critical Thinking Questions

**Question 4.** Examine the table. Prior to AI, higher education generally *reduced* automation risk. Based on the table, does that pattern still hold? Identify at least one occupation where higher formal education does *not* protect against AI displacement risk, and explain why.

*Hint:* Compare the Radiologist row (MD, 4+ years specialty training) and the Plumber row (vocational training, apprenticeship). Which has higher AI displacement risk? Why does higher formal education not protect the radiologist? What about the *nature* of the work, rather than the credential, determines AI exposure?

**Question 5.** Identify one occupation from the table (or from your own knowledge) where AI is likely to *create more work* rather than simply replace existing work. Explain the mechanism: why does AI assistance expand the demand for this role rather than contract it?

*Hint:* Think about the ATM/teller analogy from Model 1. AI lowers the cost of producing some service. If that lower cost expands overall demand for the service, then more workers may be needed even though each unit of output requires less human labor. Which occupation in the table is most analogous to bank tellers? What happens to demand for software if software becomes cheaper to build?

**Question 6.** "Automation risk" (the technical capability to automate a task) and "automation happening" (that task actually being automated at scale) are different things. List two factors (other than technical capability) that determine whether automation actually occurs in a given occupation.

*Hint:* Consider: regulatory approval requirements (a medical AI tool must receive FDA clearance before clinical use, this takes years); labor contract and union rules (some industries have negotiated protections against automation); cost-benefit economics (automating a task is only worthwhile if the automation is cheaper than the human worker); and liability (who is responsible if an AI-automated decision causes harm?).

---

Which of the following best explains the labor-economics effect of AI coding assistants (e.g., GitHub Copilot) that allow developers to complete tasks approximately 55% faster?

[( )] Immediate mass unemployment of software developers, since fewer are needed to produce the same amount of code
[(X)] Increased demand for developers, because software becomes cheaper to produce and therefore more of it gets built, the same productivity-paradox mechanism as the ATM example
[( )] Decreased demand for junior developers specifically, since AI handles entry-level tasks, while senior developer roles remain unchanged and grow in number
[( )] Developers being fully replaced by the tools within two years as capability continues to scale

---

Having analyzed who is displaced and who benefits, you are now ready to evaluate the policy tools that could buffer displacement and shape how you, as a future AI builder, navigate these dynamics.

## Model 3: Policy Responses and Student Agency

Governments, firms, and individuals have several tools to respond to labor displacement from automation. The table below compares five policy approaches:

| Policy Response | What It Addresses | Who It Helps Most | Who Pays | Political Feasibility | Real-World Examples |
|-----------------|------------------|-------------------|----------|-----------------------|---------------------|
| **Education and reskilling programs** | Skills mismatch: displaced workers need new skills to access available jobs | Displaced workers who are willing and able to retrain; most effective for workers under 50 with some educational background | Governments (via tax revenue) and employers (via training levies or voluntary investment) | Moderate: widely supported in principle, but historically underfunded and hard to scale to the pace of AI adoption | Germany's Kurzarbeit short-time work scheme; US Trade Adjustment Assistance (TAA); Amazon's Upskilling 2025 pledge |
| **Portable benefits** | Benefits (health insurance, retirement, paid leave) are tied to employers in the US, leaving gig and contract workers unprotected when they lose a job | Part-time, freelance, and displaced workers who lack employer-provided benefits and cannot afford private alternatives | Employers (higher labor costs) and consumers (via slightly higher prices) | Low-Moderate: strongly opposed by gig economy companies (Uber, Instacart) that profit from the current classification of workers as contractors | Some European countries have portable benefit systems; US has limited portable benefit pilots in a few states |
| **Universal Basic Income (UBI)** | Income floor regardless of employment status: everyone receives a baseline payment, eliminating poverty-level deprivation caused by job loss | All citizens, with the largest impact on low-income and displaced workers | Taxpayers: requires significant redistribution via higher taxes, especially on capital income and AI productivity gains | Low: deeply polarizing; pilot programs exist (Stockton CA, Kenya, Finland) but no large-scale national adoption has occurred | Stockton SEED pilot found recipients more likely to get full-time employment; Finland pilot found wellbeing gains |
| **Tax on automation** (robot tax) | Two goals: fund displaced worker assistance programs and slow the pace of automation to give workers time to adapt | Displaced workers and communities that lose employer tax base | Firms adopting automation, passed on partly to consumers and partly absorbed as reduced profit margins | Very Low: widely opposed by business lobbying; proposed in Europe and US but not implemented at scale anywhere | Bill Gates proposed a robot tax publicly in 2017; South Korea adjusted robot tax incentives slightly but no direct robot tax exists |
| **Working-time reduction** | Share available work across more workers: if each job requires fewer hours, more people can be employed | Employed workers who benefit from shorter hours; unemployed workers who gain access to hours freed up | Firms: lower output per worker-week unless productivity rises enough to compensate | Moderate: gaining real traction; several countries have run 4-day week pilots with positive results | Microsoft Japan's 4-day pilot saw 40% productivity increase; UK's 2022 six-month pilot found 92% of companies continued reduced hours |

### Critical Thinking Questions

**Question 7.** As a computer science student who is learning to build AI systems, consider your own position in the labor market. Does studying AI tools and agentic systems make you *more* or *less* vulnerable to automation, or does the answer depend on factors beyond what you study? Explain your reasoning.

*Hint:* Consider two CS graduates: one who knows how to call an API and deploy a web app; one who understands how models work, can evaluate their outputs critically, design evaluation harnesses, and reason about where they fail. Which is more replaceable by AI tools? Also consider: the fastest-growing CS roles in industry right now are not just "developer" but "AI evaluator," "prompt engineer," "AI safety specialist," and "MLOps engineer." How does your course trajectory intersect with those roles?

**Question 8.** Suppose you are advising a national government facing significant AI-driven job displacement over the next decade. Choose **two** policies from the table above (or propose your own) and explain why that combination addresses displacement more effectively than either policy alone.

*Hint:* Think about sequencing: some policies address immediate income loss (UBI, portable benefits) while others address medium-term re-entry into the labor market (reskilling). What happens if you only do income support without reskilling? What happens if you only do reskilling without income support during the transition? A good combination addresses both the immediate crisis and the longer-term structural shift.

**Question 9.** The people building automation technologies (including computer science students like you) are in a position to foresee displacement effects before they happen. What ethical obligations, if any, do AI builders have toward workers who will be displaced by systems they create? Are those obligations enforceable, and by whom?

*Hint:* Think about analogies: doctors have ethical obligations not to cause unnecessary harm; architects have legal obligations for building safety. Should software engineers have similar obligations regarding labor displacement? What would it mean in practice: a displacement impact assessment before deploying an automation system? Disclosure to workers? Financial contribution to retraining funds? Who would enforce any such obligation?

---

## Exercises

**Exercise 1: BLS and AI Exposure Research**

*What to do:* Using the Bureau of Labor Statistics Occupational Outlook Handbook (bls.gov/ooh), look up employment projections for three careers you have personally considered. Then find their AI exposure scores on the Felten, Raj, and Seamans (2023) occupational exposure scale or a comparable index. For each occupation, write 2-3 sentences comparing the BLS projection with the AI exposure rating.

*Starter hint:* Go to bls.gov/ooh and search for careers like "software developer," "data scientist," or "healthcare administrator." For the AI exposure index, search for "Felten Raj Seamans occupational exposure AI" or look for the O*NET-based AI exposure datasets at aiindex.stanford.edu. You are looking for a mismatch: occupations where BLS projects growth but AI exposure is high are the most interesting to analyze.

*You've succeeded when:* You have three occupations, each with a BLS projected growth rate, a reported AI exposure score, and a 2-3 sentence synthesis that identifies whether the BLS projection seems to account for AI exposure or not.

**Exercise 2: Agent Design and Human Judgment Audit**

*What to do:* Interview a family member, friend, or classmate about a task they perform regularly at work (paid or unpaid). Sketch, in plain language or pseudocode, an agent that could automate at least part of that task. Then identify at least two forms of human judgment or contextual knowledge that your agent would lack and that could cause it to fail or cause harm.

*Starter hint:* Choose a task that involves repeated steps: reviewing applications, answering customer questions, scheduling, data entry, or quality inspection. Your pseudocode sketch can be simple: "Step 1: Read the incoming email. Step 2: Classify as complaint, inquiry, or compliment. Step 3: Draft a response template. Step 4: Send." Then ask: What would happen if the email is sarcastic? What if the customer is in a special situation the template doesn't cover? What if the complaint involves a potential safety issue? Those are your human judgment gaps.

*You've succeeded when:* You have a named task, a pseudocode sketch of an automation agent, and two specific, concrete human judgment failures, not just "the agent would make mistakes" but specific scenarios where the agent's lack of context would cause a named harm.

**Exercise 3: Automation Layoff Case Study**

*What to do:* Research one real company that has publicly attributed layoffs (at least partially) to the adoption of AI automation (examples exist in customer service, media, and financial services sectors). Evaluate the credibility of the claim: Is the timing consistent? Did the company provide data? Are there alternative explanations for the layoffs? Write a 150-200 word assessment.

*Starter hint:* Look for documented examples: Chegg (online tutoring company) lost significant revenue after ChatGPT launched and cited AI competition in their 2023 earnings calls; IBM announced pausing hiring for roles "that could be replaced by AI" in 2023; Dropbox, Google, and Meta all announced layoffs in 2023-2024 while simultaneously increasing AI investment. For each, ask: Did they say AI caused the layoffs, or did a journalist infer the connection? Is there financial data showing the link? Were there also broader economic factors like rising interest rates or post-pandemic normalization?

*You've succeeded when:* Your assessment names the company and the specific claim, evaluates at least two pieces of evidence for the claim, identifies at least one alternative explanation, and reaches a reasoned conclusion about the claim's credibility.

---

## Reflection Prompt

**Personal level:** What careers have you seriously considered for yourself? Look back at the occupations in Model 2's table and the broader patterns from Model 1. Does what you learned today change how you think about your own career plans? What would you do differently (or the same) and why?

**Technical level:** You are studying artificial intelligence, the technology at the center of this displacement debate. That puts you in an unusual position: you are learning to build the systems that may automate work across many sectors. Does that make you **part of the problem**, **part of the solution**, or **both**? What specific responsibilities, if any, come with that position: to your future employers, to users of the systems you build, and to workers whose livelihoods may be affected?

**Societal level:** The "long-run is positive" argument for technology waves assumes that society's institutions (education systems, social safety nets, regulatory frameworks) can adapt fast enough to cushion the transition. Looking at the policy table from Model 3, are current institutions moving fast enough given the pace of AI adoption? What one institutional change would you prioritize if you had the political power to make it, and why?

-> Coming Up Next: In the AI in Education activity, we will look at how these same forces are reshaping learning itself, and how you, as a student and future builder, can use AI as a thinking partner rather than a shortcut.

---

## Further Reading

- Acemoglu, D., and Restrepo, P. (2019). "Automation and New Tasks: How Technology Displaces and Reinstates Labor." *Journal of Economic Perspectives*, 33(2), 3-30.
- Felten, E., Raj, M., and Seamans, R. (2023). "Occupational Heterogeneity in Exposure to Generative AI." *SSRN Working Paper*.
- Acemoglu, D. (2024). "The Simple Macroeconomics of AI." *NBER Working Paper No. 32122*.
- Autor, D. (2015). "Why Are There Still So Many Jobs? The History and Future of Workplace Automation." *Journal of Economic Perspectives*, 29(3), 3-30.
- Brynjolfsson, E., and McAfee, A. (2014). *The Second Machine Age*. W. W. Norton.
