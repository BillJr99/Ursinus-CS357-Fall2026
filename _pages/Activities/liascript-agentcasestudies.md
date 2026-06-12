# Agentic Case Studies: Migration, Browsing, and Research Agents
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-agentcasestudies.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentcasestudies.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Agentic Case Studies: Migration, Browsing, and Research Agents

Theory meets the field. Today we dissect three real agentic engagements drawn from your instructor's own practice, each chosen because something instructive happened at the seams: a **course-website migration** delegated to an agentic coworker, a **browsing agent** sent to navigate a live reservation site, and a **document agent** wrangling pagination across a conference proceedings. For each, your team performs the same autopsy: reconstruct the architecture, locate the failure or friction, and prescribe the Unit 3 pattern that addresses it. The arc: **a shared autopsy protocol $\rightarrow$ three cases $\rightarrow$ cross-case principles for your projects**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Each team takes one case as its primary (assigned in class) and skims the others; we jigsaw at the end, with Presenters teaching their case to a mixed group. After class, respond to the reflective prompt individually in your notebook.

---

## 1. The Autopsy Protocol

For any agentic engagement, answer five questions in order. **Goal**: what was the human's actual success criterion (often broader than the stated prompt)? **Architecture**: which patterns were in play (single agent with tools, pipeline, planner, human-in-the-loop)? **Perception**: what could the agent observe about its environment, and what was invisible to it? **Failure or friction**: where did reality diverge from plan? **Repair**: which pattern, gate, or design change addresses the divergence, and at what cost? The discipline of asking *the same* five questions is what turns anecdotes into engineering knowledge.

---

# Part I: The Cases

## Case A: Migrating a Course Website

**The engagement.** An instructor delegates to an agentic desktop coworker: migrate an introductory course's site (dozens of markdown activity files, a syllabus with structured frontmatter, image assets) from one repository format to a new one, preserving meaning while transforming structure. The agent can read files, write files, and run commands, with the human reviewing diffs before anything is committed.

**What happened at the seams.** The bulk transformations went fast; the instructive frictions were that (1) implicit conventions (an unstated frontmatter field order, naming idioms like `liascript-` prefixes) were nowhere written down, so the agent inferred them, sometimes wrongly, from examples; (2) long-running work hit context limits, so the agent had to summarize its own progress and re-derive state, occasionally redoing or skipping a file; and (3) verification was the bottleneck: every file *looked* plausible, and only systematic checks (does every page render, does every internal link resolve) separated done from done-looking.

### Critical Thinking Questions

1. Apply the protocol: identify the goal beyond "move the files," and name each architecture element you can infer.
2. Friction (1) is a *specification* failure, not a model failure. What artifact, had it existed, would have prevented it, and which assignment in this course has been quietly training you to write such artifacts?
3. Friction (2) is the memory module made flesh. Prescribe a concrete state representation (fields, format) the agent should have maintained, and where it should live.
4. Design the verification harness for friction (3): three programmatic checks that distinguish done from done-looking for a website migration.

---

## Case B: The Browsing Agent and the Campsite

**The engagement.** A browsing agent is asked to find and hold a reservable campsite meeting constraints (dates, region, amenities) on a public reservation site, navigating search forms, result pages, and availability calendars rendered for human eyes.

**What happened at the seams.** The web is a hostile perception environment for agents: state lives in visual layout, controls change behavior with JavaScript, and the same button means different things on different pages. The agent succeeded at *reading* (extracting which sites had availability) but needed tight supervision at *acting*: each click is a potentially irreversible state change, the difference between a search and a booking being one button. The human kept a confirmation gate on consequential actions, trading autonomy for safety.

### Critical Thinking Questions

5. Classify each browsing action the agent might take as read-only, reversible-write, or irreversible-write (recall the tool-use taxonomy). Where exactly should the human gate sit, and why is "gate everything" also a wrong answer?
6. The agent perceives a rendered page, not the site's database. Give one concrete misperception this gap permits, and one design (an API, structured data, or a verification read-back) that closes it.
7. APEX-day thought experiment: the site updates its layout overnight. Which architecture survives better, an agent navigating visually by instruction ("click the green button") or one navigating semantically ("activate the control labeled Check Availability")? Connect to why MCP-style structured interfaces beat screen-scraping.

---

## Case C: Pagination and the Proceedings

**The engagement.** A document agent assembles and repaginates a large conference proceedings: hundreds of papers, front matter, and a table of contents whose page numbers must match where papers actually land, a global constraint over a long document.

**What happened at the seams.** Local edits have global consequences: inserting one paper shifts every subsequent page number, so the table of contents is stale the moment anything moves. An agent fixing entries one at a time chased its own tail; the durable solution was to change the *order of operations*: freeze content first, compute pagination once as a deterministic pass, then generate the table of contents from the computed result. The general lesson: when a task has a global invariant, do not ask a stochastic local editor to maintain it; restructure the workflow so a deterministic tool enforces it.

### Critical Thinking Questions

8. State the global invariant formally (a sentence with a universal quantifier suffices).
9. Why is an LLM, however capable, the wrong instrument for *maintaining* this invariant, while being a fine instrument for other parts of the task? Which parts?
10. Generalize: name one global invariant in *your* final project (a citation that must match a source, a budget that must sum, a schedule with no conflicts) and specify the deterministic checker that will own it.

---

# Part II: Cross-Case Synthesis

[[MC]]
Across all three cases, the single most recurrent engineering lesson is:
- ( ) Larger models would have prevented every friction
- (x) Agent reliability comes from the surrounding structure: explicit specifications, externalized state, deterministic verification, and gates on irreversible actions
- ( ) Browsing agents should never be used
- ( ) Humans should review every individual model call

---

## 2. Exercises

1. *Jigsaw teach-back.* In mixed groups, each Presenter teaches their case in three minutes using only the five-question protocol. Recorders capture one repair idea per case that their home team had not considered.
2. *Pattern bingo.* As a class, tally which Unit 3 patterns appeared as repairs across the cases. Which pattern earned its keep most often, and is that consistent with the "least dynamic pattern" heuristic?
3. *Pre-mortem.* Run the autopsy protocol *prospectively* on your own project proposal: predict its Case-A-style specification gap, its Case-B-style irreversible action, and its Case-C-style global invariant. Append the pre-mortem to your proposal; it is part of the deliverable.

---

## Reflection Prompt

In your notebook: in each case, the human's judgment moved *up* a level, from doing the task to specifying, gating, and verifying it. Does that shift make the human more essential or less? Answer with reference to the case you found most personally relevant, and to your own intended career.

---

## 3. Further Reading

- Anthropic engineering blog. "How we built our multi-agent research system" (2025, online), on verification and state in long-running agents.
- Yao et al. "WebShop" and successors on web agents (2022 onward), for the perception problems of Case B.
- Your Lab 5 specification, which industrializes the verification mindset of all three cases.
