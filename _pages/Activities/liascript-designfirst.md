<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-designfirst.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-designfirst.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Design First: Plan Your Agent System Before You Build It

Today you plan a whole agent system on paper before any of it runs.  In *How I AI* you wrote a charter and reviewed a plan before letting one agent act on one task.  On Tuesday, in *Observability, Traceability, and Handoff Protocols*, you wrote the start, stop, restart, and handoff protocol as a `SKILL.md`.  Today we scale both of those to a system of several agents, and we do it in a design document.

The reason is cost.  In traditional software engineering, the cost of a mistake rises with how late you find it: a bug caught in code review is cheaper than one caught in production.  Agentic systems make that curve steeper.  An agent that sends email, writes to a database, or calls an external API can produce an **irreversible side effect** seconds after it starts, and if the design was wrong you may not be able to undo what it did.

The design-first practice says: before you write code or deploy an agent, produce a written artifact that answers four questions.  What is each agent trying to do?  What can it touch?  How will we know it succeeded?  How will we know it failed?  This is not paperwork for its own sake.  It is the smallest protection there is against an agent that is confidently wrong at scale.

The same discipline is older than software.  Electricians draw the wiring diagram before they pull wire through conduit, because once the walls are closed, changing the circuit is expensive.  Plan your ports, your identity directories, and your data flows on paper before any agent sends its first request.

The written assignment [Design Your Agent System](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/AgentSystemDesign) is handed out today.  It asks for the agent table and pre-mortem you practice here, and it now requires an observability, traceability, and handoff protocol section: the `SKILL.md` you drafted on Tuesday, checked against Tuesday's checklist.  Bring both to every model below.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Read each model as a team before you start its questions.  The Manager keeps discussion moving.  The Reflector watches for assumptions the team makes without evidence.  The Recorder documents the team's answers.  The Presenter prepares to explain the team's pre-mortem (Model 2) to the class.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Agent Table** | A structured design document with one row per agent, capturing every agent's role, inputs, outputs, tools, temperature setting, and predicted failure mode, filled out before any code is written. | The three-row table in Model 1 describing ResearchAgent, WriterAgent, and CriticAgent. |
| **System Prompt Skeleton** | A draft of the instructions you will give an agent, written at design time to force you to be explicit about what the agent should and should not do. | "You are a research assistant. Search only for peer-reviewed academic sources. Do not fabricate citations." |
| **Temperature** | A number (usually 0.0 to 1.0) that controls how random or creative an AI model's outputs are. Lower temperature means more deterministic (same answer every time); higher temperature means more varied. | CriticAgent uses 0.0 for binary pass/fail judgment; WriterAgent uses 0.7 for creative latitude. |
| **Pre-Mortem** | A technique where a team imagines, before starting work, that the project has already failed, then identifies the most plausible causes of that failure. The goal is to find and fix risks while the cost of changing course is still low. | The seven-row table in Model 2 listing component failures and their mitigations. |
| **Adversarial Test Case** | A deliberately flawed or tricky input designed to expose weaknesses in a system, written before the system is built, not after a real failure occurs. | Injecting a draft with known fabricated citations to verify the CriticAgent catches them. |
| **Irreversible Side Effect** | An action taken by an agent that cannot be undone after the fact, such as sending an email, deleting a record, or posting to a public API. | An agent that emails 500 students with incorrect course information; you cannot un-send those emails. |
| **Charter** | The document that decides a project's recurring questions once: mission, **ranked** values, definition of done, and the guardrails no agent may cross. Written from *How I AI*; the agent table below implements it | A charter ranking correctness above speed, which settles "may an agent loosen a test to go faster" without anyone asking |
| **Reversibility Class** | A label on each agent action saying how hard it is to undo: **free** (a file in git), **costly** (a database write with a backup), or **irreversible** (an email, a payment, a public post). Assigned at design time, because you cannot assign it afterwards | The Reversibility column you add to the agent table in Model 1 |
| **Observability, isolation, reversibility** | The three properties that make delegating safe: can I see what it did, can I bound what it reaches, can I undo it. Named in *Your AI Workbench*, applied to notes and projects in *How I AI*, and designed in on purpose today | Every row of the agent table should let you answer all three for that agent |
| **Handoff Protocol** | The start, stop, restart, and handoff rules an agent follows, written as a `SKILL.md` in *Observability, Traceability, and Handoff Protocols*: what it reads on start, what it logs while working, and what it writes before any stop | The "Logged, Traced, Handed Off" column in Model 1 and the handoff row in Model 2 |
| **Right-sizing** | Choosing the cheapest tool that would still be correct for a step: stated-rule code, classical ML, a model you trained, or a general LLM. Asked once per step, before that step gets a row in the agent table | Computing a monthly total in code and asking a model only to describe what is unusual about it |
| **Classical ML** | Models trained on your own labeled examples for a narrow, fixed output (logistic regression, gradient-boosted trees). Deterministic once trained, milliseconds per call, free per call, and frequently more accurate than an LLM on the exact task it was trained for | Routing 8,000 already-labeled support tickets into three categories |

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Model 3 is at-home reading and sits outside this budget.

| Minutes | What we do |
|---|---|
| 0-10 | Why design first, and what a bad first prompt actually costs |
| 10-22 | Right-sizing: which steps need a model at all, and which are cheaper and safer as code |
| 22-45 | Draft your system design: components, contracts, and failure modes |
| 45-65 | Trade drafts and review a teammate's design against the same checklist |
| 65-75 | Revise your own draft with what the review surfaced |

---

## Designing for Observability, Isolation, and Reversibility

The agent table in Model 1 is a good design artifact, and it is missing three columns that this course keeps insisting on.  Add them, and the table stops describing what each agent *does* and starts describing what happens when it is wrong.

You already have the tool for the first column.  On Tuesday you wrote the protocol itself: one trace line per loop phase, a `rule` field on every action, a dated `SESSION.md` entry on every stop.  Today's job is to point each agent's row at that protocol and say, for this agent specifically, what the trace line and the session entry contain.

For every agent in your system, before it exists, answer:

| Column | The question | Why it belongs at design time |
|---|---|---|
| **Observed how** | When this agent acts, what record is left, and who reads it? | You cannot bolt logging onto a decision that was never written down. If the answer is "the model explains itself in chat," you have no record |
| **Reaches what** | Exactly which files, services, credentials, and network destinations can this agent touch? | The honest answer is usually wider than the intended answer. Narrowing it costs nothing on paper and is a rewrite once it ships |
| **Undone how** | If this action was wrong, what is the exact undo, and who can perform it? | This is the column that turns "irreversible side effect" from a vocabulary word into a design constraint |

The last column is the one that changes designs.  Work through your system and label each action **free** to undo (a commit in a repository you control), **costly** (a database write you have a backup for, restorable in an hour), or **irreversible** (an email sent, a payment made, a message posted, a record deleted from a system you do not own).

Then apply the rule the labels imply: every irreversible action gets a human gate, and the gate goes in the design, not in a later hardening pass.  Agents are not unusually careless.  "Confidently wrong at scale, quickly" is simply the failure mode of this technology, and the only defense that survives a real deployment is that the irreversible step could not happen without someone approving it.

One design move is worth knowing here: convert irreversible into reversible before you gate it.  An agent that sends email is irreversible.  An agent that *drafts* email into a folder, with a human pressing send, is free to undo, and it keeps almost all of the value.  Most irreversible agent actions have a draft-shaped version, and finding it is usually a better answer than adding a confirmation dialog.

Your team designs an agent that files issues in your project's GitHub repository when it finds a bug.  Classify its reversibility and decide whether it needs a gate.

[( )] Irreversible, so it needs a human gate before every filing
[(X)] Costly rather than irreversible: an issue can be closed and edited, but it notified everyone watching the repository and that notification cannot be recalled.  A gate is optional; a rate limit and a label marking it agent-filed are not
[( )] Free, since issues can be deleted
[( )] It depends entirely on how good the model is

The interesting part of this question is the notification.  The artifact is editable, so the state is recoverable; the side effect on other people's attention is not.  Many agent actions look free when you consider only the data and turn out to be costly when you consider who got pinged.  Ask about both.

Two things to remember from this section.  Every row in your design must answer how the agent is observed, what it reaches, and how its work is undone.  The observability answer is not new work: it is the protocol from Tuesday, applied to one agent at a time.

---

## The Question That Comes Before the Table

The agent table you are about to read has one row per agent, and that shape quietly assumes something: that every step in your system needs a model.  Most systems that disappoint their builders got that assumption wrong somewhere.  So ask the prior question on every step before you give it a row.

> **For each step: what is the cheapest thing that would be correct here?**

"Cheapest" means cheapest in the ways you will care about at three in the morning, which is not only dollars.  A language model is the most expensive tool in your kit on almost every axis that matters:

| | Deterministic code | Classical ML | A model you trained | A general LLM |
|---|---|---|---|---|
| Same input, same output | Always | Yes, once trained | Yes, once trained | No, and that is by design |
| Testable with an assertion | Yes | Yes, plus held-out metrics | Yes, plus held-out metrics | Only statistically |
| Latency | Microseconds | Milliseconds | Milliseconds | Hundreds of milliseconds to minutes |
| Explains a decision | The code is the explanation | Feature weights, and honestly | Sometimes | It will produce an explanation, which is not the same thing |
| Fails how | Loudly, with a stack trace | Degrades measurably | Degrades measurably | Confidently and plausibly |
| Needs labeled data | No | Yes | Yes, usually a lot | No |
| Handles input you did not anticipate | No | Poorly | Poorly | Well, and this is the whole reason to use one |

Read that last row against all the others.  The one thing an LLM does that nothing else on the table does is cope with open-ended input it was never shown.  That capability is remarkable, and you pay for it on every other row.  When the input is not open-ended, you are paying and getting nothing.

### Four Tools, and How to Tell Which One You Are Looking At

**Deterministic code, when you can state the rule.**  If you can write down what correct means as a rule (a valid email has an `@`, an order total is the sum of its line items, a date in ISO format sorts lexicographically), write the rule.  Code that implements a stated rule is faster, free, always right, and testable with `assert`.  A model asked to do the same job will be right most of the time, which is a plain downgrade from always.

**Classical machine learning, when you have labels and a narrow output.**  If the output space is small and fixed (spam or not, which of six categories, a number in a known range) and you have, or can label, a few thousand examples, a logistic regression or a gradient-boosted tree is often more accurate than an LLM on that exact task.  It runs in milliseconds, costs nothing per call, and gives you feature importances you can argue with.  This is not a legacy technique you are humoring; on tabular data it is frequently still the state of the art.

**A model you train or fine-tune, when the task is narrow, repeated, and yours.**  If you run the same specialized judgment millions of times, and you have domain data nobody else has, training a small model or fine-tuning an open one buys you something you cannot rent: a system that encodes *your* institution's definitions, runs on your hardware, keeps your data on your premises, and does not change underneath you when a vendor ships an update.  The cost is real, in labeled data and in the obligation to monitor it, so this earns its place at volume and by specificity, not by ambition.

**A general LLM, when the input is open-ended and the task varies.**  Free-form text, tasks you cannot enumerate in advance, instructions given in English at runtime, a long tail where every case is a little different, and no labeled data to learn from.  This is the real zone, and it is a large one.  Use the model here without apology.

### The Pattern That Actually Ships

The answer is rarely one tool for the whole system.  The pattern that survives production is narrower than "build an agent" and better than it:

> **Use the model at the boundary where structure is missing.  Use code everywhere structure exists.**

An agent that reads a messy email and files an expense should use a model for exactly one step, turning unstructured prose into a structured record, and then deterministic code for every step after it: validating the fields, checking the amount against a policy limit, looking up the vendor, computing the total, writing the row.  Ask the model to do the arithmetic and you have taken a solved problem and made it probabilistic.

That framing also tells you where to put your tests.  The code steps get ordinary unit tests with exact expected values.  The one model step gets the treatment from *Evaluating Agent Outputs*: a labeled set, a measured pass rate, and a threshold.  Systems designed this way are debuggable, because when the output is wrong you can usually tell which side of that boundary failed.

### Model 0: Right-Sizing Six Steps

Below are six steps drawn from real student projects.  For each, decide which of the four tools is the cheapest thing that would be correct, and name what goes wrong with the tempting alternative.  Two are filled in.

| Step | Cheapest correct tool | What goes wrong if you reach for an LLM instead |
|---|---|---|
| Sort 10,000 support tickets by their creation timestamp | Deterministic code | The model cannot see all 10,000 at once, sorting is not a language task, and a sort that is right 97% of the time is not a sort |
| Decide whether an incoming support ticket is about billing, technical trouble, or account access, given 8,000 past tickets already labeled by staff | Classical ML, or a fine-tune | Nothing catastrophic, and you are paying per call and per second for accuracy a trained classifier likely matches or beats on this exact distribution, with no labels wasted |
| Check whether a submitted student ID matches the format `A` followed by seven digits | | |
| Summarize an open-ended student feedback comment into one sentence | | |
| Flag which of last term's 40,000 transactions are anomalous, with no labels available | | |
| Extract the assignment due date from whatever phrasing a professor used in an announcement | | |

### Critical Thinking Questions

1.  Your teammate proposes an agent whose job is to validate that a form's fields are all present and correctly typed, arguing that the model will be more flexible about odd input than a validator would be.  Give the strongest version of their argument, then say what you would build instead and why.

    > *Hint: The strong version is real: a validator rejects `"Jan 3rd, 2027"` where a model would understand it, and rigid validators generate support tickets. The answer is not to pick a side; it is to notice there are two jobs. Interpretation of messy input is a model job. Deciding whether a value is acceptable is a rule you can state, so it is a code job. Normalize with the model, validate with code, and log every case where the model's normalization was rejected, because that log is your list of validator bugs.*

2.  A team has 8,000 labeled tickets and picks an LLM anyway, because "we already have the API set up and we don't know how to train a classifier."  That is an honest reason.  Name two costs they are accepting, and one condition under which their choice is genuinely the right call.

    > *Hint: Costs: per-call money and latency forever, and no calibrated confidence, so they cannot route uncertain cases for review the way a classifier's probability output lets them. Genuinely right when: the label set is expected to change soon, or the volume is low enough that engineering time dominates inference cost. A prototype that ships this week and gets replaced is a legitimate engineering decision as long as somebody wrote down that it is one.*

3.  A step in your pipeline computes a monthly total from a list of transactions.  Which is the correct design?
   [( )] An agent that reads the transactions and reports the total, since it can also explain anomalies it notices
   [(X)] Code that computes the total, optionally with a separate model step that describes anything unusual about the result
   [( )] An agent that computes the total and a second agent that verifies it
   [( )] Either, since a modern model does arithmetic reliably enough for this

    > *Hint: The first and fourth options make a solved deterministic problem probabilistic to get a feature (the explanation) that does not require it. The third pays twice and still has no guarantee, since two models drawing on the same training can agree on the same wrong answer. The second gets an exactly correct total and still gets the narration, because the model is being asked for the thing only it can do, and is not being asked to add.*

4.  Under what circumstances would you train your own small model rather than call a general one, when the general one is more capable in every benchmark you can find?

    > *Hint: Capability is not the only axis, and benchmarks measure the axis you care about least here. Volume (per-call cost times millions), data residency (the records cannot leave your network), stability (a vendor update must not silently change your outputs), latency (the decision has a hard budget), and specificity (your definition of "at risk" is your institution's, not a general one) each independently justify it. Notice that four of those five are not about accuracy at all.*

> **Common Misconception: "Using a simpler tool means you are not doing AI."**  The engineering judgment asked for here *is* the AI skill.  Anyone can call a model on everything.  Deciding that step four does not need one, and defending that decision with a cost, a latency, and a test you can write, is what separates a system that works from a demo that impressed someone once.  Every step you move out of the model becomes deterministic, testable, fast, free, and inspectable.  Spend the model where it earns its keep.

Now go to the agent table, and bring the question with you: every row you write should survive being asked why it is a model at all.

---

## Model 1: The Agent Table

In this model you read a completed agent table for a three-agent research pipeline, then fill in a fourth row from scratch.  That is the fastest way to learn what the table captures before you need it for your own project.

**Why this matters:** "Measure twice, cut once" is the carpenter's version of design-first.  In carpentry, cutting a board too short means buying new wood.  In agentic AI, deploying an agent with a poorly defined role can mean sending incorrect information to thousands of users, corrupting a database, or spending hundreds of dollars on API calls that accomplished nothing.  The agent table makes you write down every important decision about each agent before any of those decisions has consequences.

The agent table is the core design artifact for a multi-agent system.  One row per agent.  Before you write a line of code, you should be able to fill in every cell.  Empty cells are not gaps in the document; they are unresolved risks in your system.

The table below carries the original columns plus one that Tuesday's protocol makes possible: for each agent, what is logged, which rule each action traces back to, and what the handoff file contains when the agent stops.  When you build your own table for *Design Your Agent System*, also add the three from the section above: **observed how**, **reaches what**, and **undone how**.

| Agent Name | Role and Goal | System Prompt Skeleton | Inputs | Outputs | Temperature | Tools Available | Failure Mode | Logged, Traced, Handed Off |
|---|---|---|---|---|---|---|---|---|
| **ResearchAgent** | Find and summarize the top 5 peer-reviewed sources on a given topic, providing structured citations the WriterAgent can use directly. | "You are a research assistant. Search only for peer-reviewed academic sources. Do not fabricate citations. Return structured JSON." | Topic string from the orchestrator, specifying the research question. | JSON list of objects, each with fields: title, authors, year, url, and a one-sentence summary. | 0.2: low temperature for factual precision; we do not want creative variation in citations. | `web_search`, `fetch_url` | Hallucinates a plausible-sounding citation that does not exist at the provided URL. | One trace line per search: `query_hash`, source count, and `rule: cite-before-claim`. On stop, the `SESSION.md` entry names the JSON file written, which URLs were fetched and verified, and the Next Safe Action (hand the list to WriterAgent). |
| **WriterAgent** | Draft a 500-word section using the research summaries provided by ResearchAgent, with inline citations. | "You are a technical writer. Use only the sources provided. Cite inline. Do not introduce new claims." | JSON research list from ResearchAgent, plus the original topic string. | Markdown text string, approximately 500 words, with inline citations in [Author, Year] format. | 0.7: moderate temperature for some creative latitude in phrasing and structure. | None: text generation only, no tool calls. | Ignores the JSON source list and generates claims from training data, producing confident but unsupported assertions. | One trace line per draft: word count, citation count, `finish_reason`, and `rule: use-only-provided-sources`. On stop, the entry names the draft path, the source JSON it was written from, and whether CriticAgent has seen this version. |
| **CriticAgent** | Evaluate the draft against a rubric and flag any unsupported claims before the output reaches the user. | "You are a fact-checker. For each claim in the draft, identify which source supports it. Flag claims with no source." | Draft markdown from WriterAgent, plus the original research JSON from ResearchAgent. | JSON list of objects, each with fields: claim (quoted from draft), supported_by (source ID or null), and flag (true/false). | 0.0: deterministic; claim support is a binary pass/fail judgment that should not vary across runs. | None: evaluation only, no tool calls. | Passes a hallucinated claim because the confident phrasing sounds plausible, even though no source supports it. | One trace line per verdict: flag count, the claim IDs flagged, and `rule: every-claim-needs-a-source`. On stop, the entry records pass or fail, which draft version was judged, and whether the draft may proceed to the user. |

### Critical Thinking Questions

5.  The system prompt skeleton for ResearchAgent includes "Do not fabricate citations."  Why is this instruction necessary; doesn't the model already "know" citations should be real?  What does this tell us about how system prompts function?

   > *Hint: Think about the difference between knowing a rule in general and following it under pressure.  When a model is "trying to be helpful" and no sources exist, what might it do instead of saying "I don't know"?*

6.  Temperature is set differently for each agent.  WriterAgent has temperature 0.7 while CriticAgent has 0.0.  Explain the reasoning: what would go wrong if their temperatures were swapped?

   > *Hint: Imagine a critic that gives a different verdict each time you run it on the same draft.  Is that useful?  Now imagine a writer that produces the exact same sentence structure every single time.  Is that a problem?*

7.  The "Failure Mode" column is filled in *before* building the system.  What information source are you drawing on when you predict how an agent might fail?  Is this prediction reliable?

   > *Hint: You are not predicting from test data; the system does not exist yet.  What general knowledge about LLMs are you applying?  What kinds of failures are hardest to predict in advance?*

8.  A new agent is needed: a **FormatterAgent** that converts the critic-approved draft into HTML. Fill in a complete row for this agent in your team's Recorder notes.  Be specific about its system prompt skeleton and its failure mode; do not leave any cell as "TBD."

   > *Hint: What should FormatterAgent do if it receives a draft that CriticAgent marked as having unfixed issues?  Should it proceed anyway?  How would you encode that decision in the system prompt?*

9.  Fill in the "Logged, Traced, Handed Off" cell for your FormatterAgent.  Name the fields in its trace line, the rule its one action (writing the HTML file) traces back to, and what its `SESSION.md` entry must contain so that a fresh agent knows whether the HTML on disk came from an approved draft.

   > *Hint: Start from the checklist you wrote on Tuesday.  Which row of it would fail if FormatterAgent wrote HTML from an unapproved draft and stopped cleanly?  The trace line must let you answer "which draft version, and who approved it" without opening the HTML; the session entry must let the next agent decide whether to ship or regenerate.*

In the agent table, WriterAgent runs at temperature 0.7 while CriticAgent runs at 0.0.  The key distinction this encodes is:

[( )] WriterAgent is a larger model, so it can tolerate more randomness
[(X)] Generation benefits from creative variation, but evaluation must be deterministic; a critic that gives different verdicts on identical drafts is useless
[( )] Higher temperature makes WriterAgent's citations more accurate
[( )] Temperature 0.0 disables CriticAgent's tools, which is safer

Complete the design principle: an empty cell in the agent table is not a gap in the document; it is an unresolved [[risk]] waiting to become a bug.

Two things to remember from this model.  A row is complete when every cell holds a decision, including what the agent logs and what it writes before it stops.  The FormatterAgent row you just wrote is the shape of every row in your assignment.

---

With your agent table complete, the next model turns to how those agents can fail, and specifically how to predict failures before they happen, while the cost of changing the design is still low.

## Model 2: The Pre-Mortem

In this model you work through a seven-row pre-mortem table covering every component of the research pipeline and its handoff, identify one failure mode the table does not yet cover, and add it with all four columns filled in.

**Why this matters:** Most teams think about how their system could fail after it fails.  The pre-mortem inverts this: you imagine failure before it happens, when you still have time to prevent it.  For agentic systems this matters more than usual, because agents can fail in ways that are hard to detect from the outside: the system appears to run while quietly producing wrong outputs.  A pre-mortem makes you ask not only "what could go wrong?" but "how would we even know?"

A pre-mortem is a technique from project management.  Before starting a project, the team imagines it is six months in the future and the project has *failed*.  Working backward, they identify the most plausible causes and design mitigations now, while the cost is low.

| Component | What Could Go Wrong | How We Would Detect It | Mitigation |
|---|---|---|---|
| **ResearchAgent** | Returns 5 results, but 2 are from predatory journals or retracted papers, polluting the entire pipeline with low-quality sources. | Spot-check a sample of outputs against known databases; CriticAgent flags source quality using a domain whitelist. | Add a `validate_source_credibility` tool; include an approved domain whitelist in the ResearchAgent system prompt. |
| **ResearchAgent** | Context window fills before processing all candidate results, causing the agent to silently truncate its search and return fewer than 5 sources without warning. | Log token counts for every run; compare the output source count against the expected count of 5. | Paginate search results; process in batches with explicit count assertions before returning. |
| **WriterAgent** | Ignores the JSON source list passed as input and writes from its training memory instead, producing confident but unsourced claims. | CriticAgent finds claims with no supporting source; a high flag rate signals this failure. | Instruct WriterAgent to cite inline as it writes each sentence; CriticAgent rejects any draft with more than N flagged claims. |
| **CriticAgent** | Approves everything because it is too agreeable, a failure mode called sycophancy, where the model avoids giving negative feedback. | Inject a known-bad draft with planted fabricated claims and verify that CriticAgent flags them; if it does not, the critic is failing. | Include adversarial test cases in the evaluation suite; compare CriticAgent output against a ground-truth flag list on those cases. |
| **Orchestrator** | Passes outputs between agents out of order or with wrong dictionary keys, causing agents to operate on the wrong data without realizing it. | Type-check and schema-validate every payload at each agent handoff; log all inter-agent messages with timestamps. | Use Pydantic models or JSON Schema to validate every payload structure before passing it to the next agent. |
| **The handoff** | An agent stops mid-run (context, quota, or a crash) and the next session cannot tell which sources were verified or which draft the critic judged, so it re-verifies some, skips others, and ships an unapproved draft. | The last `SESSION.md` entry has no Next Safe Action, or the trace has `act` lines with no `rule` field, or the draft on disk has no matching critic verdict in the trace. | Apply the protocol from *Observability, Traceability, and Handoff Protocols*: one trace line per phase, a dated session entry on every stop, and the checklist run against the design before it is submitted. |
| **The whole pipeline** | Runs for 45 minutes and produces plausible-looking output that is subtly wrong in ways no single agent caught, because errors compounded across handoffs. | End-to-end human review of a random 10% of outputs; compare cost of review against cost of fully manual research. | Define an evaluation rubric before building; run a blind comparison of agent output versus human-written output on the same topics. |

### Critical Thinking Questions

10.  The pre-mortem row for CriticAgent includes injecting a "known-bad draft" as a test.  This is called an **adversarial test case**.  Why must this test be designed *before* the system is built, and not added later when a real failure is discovered?

   > *Hint: Think about what happens to your objectivity once you have already seen the system run successfully 100 times.  Is it harder or easier to design a truly adversarial test at that point?  Why?*

11.  The last row covers the "whole pipeline" failing in a way no single agent caught.  What property of multi-agent systems makes this kind of failure possible even when each individual agent passes its own tests?

   > *Hint: Think about a game of telephone.  Each person in the chain repeats correctly what they heard, but what happens at the end?  What is the difference between "each step is correct" and "the composition is correct"?*

12.  Identify one failure mode that is *not* in this table but that you believe is plausible given what you know about LLMs.  Add it to the table with all four columns filled in; do not leave any cell empty.

   > *Hint: Consider: what happens if the WriterAgent or CriticAgent receives an unusually long input that approaches its context limit?  What happens if two agents receive slightly different versions of the same source document?*

13.  Take the handoff row and make its detection column concrete for your own project.  Name the file the next agent reads first, the one trace field that lets a reviewer connect a shipped draft back to the rule that allowed it, and the two lines the `SESSION.md` entry must contain for the "re-verifies some, skips others" failure to be impossible.

   > *Hint: Detection that says "look at the logs" is not detection.  A reviewer should be able to run one `grep` on the trace for the draft's version and see its critic verdict and the rule on the same line.  The session entry needs a Completed list with the proving command and a Next Safe Action; if either is missing, the next agent must not act, and the protocol should say so.*

> **Common Misconception:** Many students treat the pre-mortem as a pessimistic exercise, or feel that spending time on it is wasteful when they are eager to start coding.  The opposite is true: the pre-mortem is the most cost-effective work you will do on the project.  Every failure mode you identify and mitigate in writing takes about five minutes to address.  The same failure mode discovered after deployment may take days or weeks to diagnose, and may leave outputs that cannot be recalled or corrected.  Designing for failure is not pessimism; it is professionalism.

A pre-mortem is most useful when it is conducted:

[( )] After the system is deployed, so real failure data informs the analysis
[( )] During the debugging phase, when actual failures have been observed
[(X)] Before building begins, when changing the design is still cheap
[( )] After the first end-to-end test, when the team has hands-on intuition about the system

Every agent in the pipeline passes its own individual tests, yet the end-to-end output is still subtly wrong.  The pre-mortem's key distinction that explains this is:

[( )] Individual tests are unreliable for language models, so passing them means nothing
[( )] The orchestrator must be a larger model than the agents it coordinates
[(X)] Component correctness does not imply composition correctness; errors can compound across handoffs that no single agent's test examines
[( )] Temperature settings drift over the course of a long run

Two things to remember from this model.  Every row needs a detection column you could check before or during a run, not after a complaint.  The handoff is a component, and it fails like one.

---

The pre-mortem identified what could go wrong.  The next model shows, week by week, how skipping it plays out in a real project compared to a team that did the design work first.  Read it before the next session; it is the narrative version of what you just did on paper.

## Model 3 (At Home): A Six-Week Timeline, Design-First vs. Code-First

In this model you compare two student teams building the same pipeline on parallel tracks and trace exactly when, and why, the code-first team's early-saved time is spent back, with interest.

**Why this matters:** The design-first approach is sometimes dismissed as "slowing down" development.  This timeline shows that the total time spent is similar, but *where* the work happens differs.  Design-first front-loads effort into cheap, reversible planning.  Code-first back-loads the same effort into expensive, disruptive rework.  The question is not whether to do the hard thinking; it is whether to do it on paper or in production.

Two student teams build the same 3-agent research pipeline.  Team A starts coding immediately.  Team B spends the first three days writing a one-page design document (agent table, pre-mortem, data flow diagram, evaluation rubric).

| Milestone | Team A: Code-First | Team B: Design-First |
|---|---|---|
| **Week 1** | ResearchAgent is running, but its output format varies call to call (sometimes JSON, sometimes plain prose) because format was never specified. WriterAgent has not been started yet. | Design document is complete. The agent table contains agreed-upon input/output schemas for all three agents. No code exists yet, but the entire team knows exactly what they are building toward. |
| **Week 2** | WriterAgent is added, but it immediately breaks because ResearchAgent output format is inconsistent. Team A rewrites ResearchAgent to standardize output format. Two days of progress are lost to a problem that could have been decided in 30 minutes on paper. | ResearchAgent and WriterAgent are both implemented against the agreed schema. The first end-to-end run succeeds. A CriticAgent stub is in place for integration next week. |
| **Week 3** | CriticAgent is added. The team discovers they never defined what "a supported claim" means, so the critic's prompt is vague and its output is unreliable. The team spends a full day arguing about the rubric. | CriticAgent is complete and running. The team executes their pre-designed adversarial test cases and discovers that WriterAgent ignores sources approximately 30% of the time. They fix the system prompt and rerun the tests. |
| **Week 4** | Team A runs an end-to-end pipeline for the first time. The output looks reasonable, but they have no rubric to evaluate it against. They ask their instructor "Is this good?" with no quantitative answer available. | Team B runs their full evaluation rubric (defined in the design document) against 20 test outputs. They compute a flag rate and a source accuracy score. They have concrete numbers to report and defend. |
| **Week 5** | Team A discovers their ResearchAgent has been hallucinating citations since Week 1. They have three weeks of pipeline outputs they cannot trust and cannot easily reprocess. | Team B's CriticAgent caught hallucinated citations in Week 3. Their Week 5 outputs are clean, auditable, and backed by a known-good source list. |
| **Week 6** | Team A submits a system that mostly works most of the time. They cannot clearly explain their design choices because those choices were made reactively, under pressure, without documentation. | Team B submits a system with documented design rationale, a working evaluation pipeline, quantified error rates, and a clear audit trail of every decision made. |

### Critical Thinking Questions

14.  Team A lost two days in Week 2 to a schema disagreement they could have resolved in 30 minutes during a design session.  What is the general principle here, and does it apply to non-agentic software projects as well?

   > *Hint: The cost of a decision is the cost of reversing it plus the cost of everything built on top of it before you reversed it.  How does this principle scale with how late the reversal happens?*

15.  In Week 4, Team A asks "Is this good?" but has no rubric to answer the question.  Why is it impossible to evaluate an AI system without criteria that were defined *before* seeing the output?

   > *Hint: If you define "good" after seeing the output, you are at risk of unconsciously defining "good" as "what the system produced."  What is the technical name for this kind of reasoning error in statistics?*

16.  Team B's design document took three days.  Team A saved three days at the start and lost them elsewhere.  What does this suggest about the relationship between upfront design cost and total project cost?  Under what circumstances might Team A's approach actually be *better*?

    > *Hint: Is there any project type where the requirements are so unstable or unknown that writing a design doc first would be wasted effort? What would a project like that look like, and is a 3-agent research pipeline that kind of project?*

---

## Exercises

These exercises give you practice writing the artifacts yourself (agent table, pre-mortem, and a team debate) before you face a blank page on your final project.

1.  **Write a one-page design document.**

   *What to do:* Choose one of these 2-agent systems: (a) a ticket triage system that classifies support requests and drafts responses, (b) a code review system that reads a pull request diff and flags potential bugs, (c) a meeting summarizer that transcribes audio and extracts action items.  Write a complete agent table with all columns filled in, plus a 5-row pre-mortem using the four-column format from Model 2.

   *Starter hint:* Start by writing down the output of the *last* agent in the pipeline: what does the final user receive?  Work backward from there: what does the second-to-last agent need to produce to enable that output?  Then ask the same question of the first agent.  Working backward from the output often reveals design gaps faster than working forward.

   *You've succeeded when:* Every cell in your agent table contains a complete sentence or value, and your pre-mortem includes at least one failure mode that involves agents interacting in an unexpected way, not just individual agents failing in isolation.

2.  **Minimum viable design: a team debate.**

   *What to do:* As a team, debate and agree on the answer to this question: what is the *minimum* design artifact you need before starting to build an agentic system?  What can you skip if you are in a hurry?  Produce a ranked list of design artifacts from "never skip under any circumstances" down to "skip if you are pressed for time."  The Presenter defends the team's top-priority item to the class.

   *Team vote first:* Before any discussion, each member votes silently, **agent table** (structure-first) or **evaluation rubric** (measurement-first), as the single never-skip artifact.  The Recorder tallies the votes and announces the split.  If the vote is not unanimous, the team must reconcile it: each side states the most expensive failure its artifact would have prevented, and the team debates until it agrees on one answer (and records what argument moved the minority).  Only then build the full ranked list.

   *Starter hint:* Consider these candidates: (1) agent table, (2) data flow diagram, (3) pre-mortem, (4) evaluation rubric, (5) system prompt drafts.  Which single artifact, if it were all you had, would prevent the most expensive failures?

   *You've succeeded when:* The team can defend the top item on the list with a concrete example of a catastrophic failure it would have prevented in a real project.

3.  **Evaluate a design document from a previous semester.**

   *What to do:* I will share a sample design document from a previous semester project.  As a team, apply the pre-mortem technique to it: identify two failure modes the original team missed.  Write each one in the full four-column format from Model 2.

   *Starter hint:* Pay special attention to handoff points between agents: where does one agent's output become another agent's input?  These seams are the most common source of missed failure modes in real design documents.

   *You've succeeded when:* Each of your two identified failure modes has a plausible detection mechanism that is not "run the system and see if it fails"; it should be something you could check proactively, before or during a run.

---

## Reflection Prompt

Respond to all three levels in your notebook:

**Personal:** Describe a personal experience (in software development, in school, or in any other domain) where skipping planning cost you more time than planning would have taken.  What conditions were you in when you decided to skip planning?  What conditions would have made you more likely to plan first?

**Technical:** The design-first principle is in tension with agile development practices, which favor delivering working software quickly over extensive documentation.  How would you adapt the agent table and pre-mortem to fit a two-week sprint cycle?  What is the minimum version of each artifact that still provides meaningful protection?

**Societal:** Design-first practices were developed in contexts where individual engineers or small teams made design decisions with limited accountability.  In large organizations, design reviews can become bureaucratic gatekeeping that slows innovation without proportionally improving outcomes.  What governance structures would make design-first practices protective rather than performative?

---

-> **Coming Up Next:** *Orchestration and Multi-Agent Patterns* (Tue Oct 27) is next: how the agents you designed on paper today get wired into pipelines, routers, and planner-led workflows, and the five shapes those wirings take.  Today's agent table, pre-mortem, and protocol section feed directly into *Design Your Agent System* and your Final Project's design document.

---

## Further Reading

- Gary Klein.  "Performing a Project Premortem."  *Harvard Business Review* (2007).  The origin of the pre-mortem technique applied here.
- Chip Heath and Dan Heath.  *Decisive: How to Make Better Choices in Life and Work* (2013), Chapter 7.  The "premortem" and "preparade" as decision tools.
- Anthropic.  "Building Effective Agents." https://www.anthropic.com/research/building-effective-agents, the orchestration and agent design patterns section is directly relevant.
- Fred Brooks.  *The Mythical Man-Month* (1975/1995), Chapter 1.  "Plan to throw one away", still the most candid advice about first-system costs.
- This course: [Observability, Traceability, and Handoff Protocols](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-observability.md), where the `SKILL.md` and checklist that today's protocol section relies on were written.

The self-paced extension on `AGENTS.md`, global instructions, and skills that used to close this deck now lives in [Skills: Design One, Then Measure It](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-skills.md), from Sep 10.  Read it there if you want the skill file layout and the measurement harness that go with the protocol you are designing today.

---
