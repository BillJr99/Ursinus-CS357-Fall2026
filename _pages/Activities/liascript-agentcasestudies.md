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

Theory meets the field: with the judging tools of the *Evaluating Agents: LLM-as-Judge and Rubric Pipelines* activity in hand, today we dissect three real agentic engagements drawn from your instructor's own practice, each chosen because something instructive happened at the seams: a **course-website migration** delegated to an agentic coworker, a **browsing agent** sent to navigate a live reservation site, and a **document agent** wrangling pagination across a conference proceedings. For each, your team performs the same autopsy: reconstruct the architecture, locate the failure or friction, and prescribe the Unit 3 pattern that addresses it. The arc: **a shared autopsy protocol $\rightarrow$ three cases $\rightarrow$ cross-case principles for your projects**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Each team takes one case as its primary (assigned in class) and skims the others; we jigsaw at the end, with Presenters teaching their case to a mixed group. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Agentic engagement** | A real deployment where an AI agent takes a sequence of actions over time on behalf of a human, as opposed to answering a single question in isolation. | The instructor asks an agent to migrate a course website — not one question, but hundreds of sequential file-read, file-write, and verify actions over hours. |
| **Perception** | Everything the agent can observe about its environment at a given moment, which is always incomplete — the agent cannot see what is not in its context window or returned by its tools. | The browsing agent can read a rendered web page's visible text but cannot see the JavaScript state or the reservation database behind it. |
| **Irreversible action** | An action whose consequences cannot be undone after the fact, requiring a human confirmation gate before execution. | Clicking "Confirm Reservation" on a campsite booking site: once clicked, a credit card is charged and a site is held. |
| **Global invariant** | A constraint that must remain true across the entire document or system, not just locally — meaning fixing one place can break another place. | In a conference proceedings, every table-of-contents page number must match where that paper actually starts; changing any paper's length breaks all subsequent entries. |
| **Human-in-the-loop** | A system design where a human must approve certain actions before the agent proceeds, trading autonomy for safety on high-stakes or irreversible steps. | The instructor reviewing every file diff before the agent commits it to the repository during the website migration. |
| **MCP (Model Context Protocol)** | A standard interface that allows AI agents to interact with tools and services through structured, typed function calls rather than by scraping visual interfaces designed for humans. | An agent using an MCP-style "check availability" function call instead of visually navigating a reservation website's calendar widget. |

---

## The Autopsy Protocol

For any agentic engagement, answer five questions in order. **Goal**: what was the human's actual success criterion (often broader than the stated prompt)? **Architecture**: which patterns were in play (single agent with tools, pipeline, planner, human-in-the-loop)? **Perception**: what could the agent observe about its environment, and what was invisible to it? **Failure or friction**: where did reality diverge from plan? **Repair**: which pattern, gate, or design change addresses the divergence, and at what cost?

The discipline of asking *the same* five questions is what turns anecdotes into engineering knowledge.

| Protocol question | What you are looking for | Red flag that signals a problem |
|---|---|---|
| **Goal** | The human's actual success criterion, which is often broader or different from the literal task prompt they gave the agent. | The agent completed the literal task but missed an unstated requirement (e.g., "move the files" but break all internal links). |
| **Architecture** | Which agent patterns were in use: single agent with tools, multi-step pipeline, planner-executor, human-in-the-loop gates, or a combination. | The task required a pattern (e.g., human gate on irreversible actions) that was not included in the architecture. |
| **Perception** | Everything the agent could observe — files, web pages, API responses — and everything it could not see: implicit conventions, off-screen state, database contents behind a rendered page. | The agent acted on incomplete information and could not have known it was incomplete. |
| **Failure or friction** | The specific moment where the agent's behavior diverged from what was needed, and the underlying cause (specification gap, context limit, perception gap, global invariant violation). | The agent produced output that looked correct but was not (done-looking vs. done). |
| **Repair** | A concrete design change that addresses the failure: a specification artifact, an external state representation, a deterministic verifier, or a human gate — with an assessment of what the repair costs. | The proposed repair either does not address the root cause or is so expensive that it changes the cost-benefit calculation of using an agent at all. |

---

# Part I: The Cases

In this part, you will apply the autopsy protocol to three real deployments — one case per team — and then share your findings across groups. As you read your case, fill in the five autopsy questions before looking at the table; the tables show what actually happened, which is most useful *after* you've made your own predictions.

## Model 1: Case A — Migrating a Course Website

Think of delegating the relocation of an office to a moving company. You tell them "move everything from room 101 to room 205." They execute perfectly — every box is moved — but your filing system relied on a drawer-numbering convention you never wrote down, the movers used a different system, and now you cannot find anything. The agent is not at fault; the specification is. Case A is exactly this scenario, scaled to dozens of markdown files and an implicit naming convention no one thought to document.

**The engagement.** An instructor delegates to an agentic desktop coworker: migrate an introductory course's site (dozens of markdown activity files, a syllabus with structured frontmatter, image assets) from one repository format to a new one, preserving meaning while transforming structure. The agent can read files, write files, and run commands, with the human reviewing diffs before anything is committed.

**What happened at the seams.** The bulk transformations went fast; the instructive frictions were that (1) implicit conventions — an unstated frontmatter field order (the metadata block at the top of each markdown file), naming idioms like `liascript-` prefixes — were nowhere written down, so the agent inferred them, sometimes wrongly, from examples; (2) long-running work hit **context limits** (the maximum amount of text a model can hold in memory at once), so the agent had to summarize its own progress and re-derive state, occasionally redoing or skipping a file; and (3) verification was the bottleneck: every file *looked* plausible, and only systematic checks (does every page render, does every internal link resolve) separated done from done-looking.

| Autopsy question | Answer for Case A |
|---|---|
| **Goal** | Move files AND preserve all meaning, rendering, internal links, and naming conventions — not just copy bytes from one place to another. |
| **Architecture** | Single agent with file-read, file-write, and shell-command tools; human-in-the-loop gate on every commit via diff review. |
| **Perception** | The agent could read file contents and directory listings, but could NOT see the implicit naming convention, the rendering output in a browser, or whether internal links resolved to real pages. |
| **Failure or friction** | (1) Inferred conventions incorrectly from examples; (2) context limit forced re-derivation of progress state; (3) output looked plausible but systematic verification was missing. |
| **Repair** | (1) Write a specification document before starting; (2) maintain an external progress log as a structured file the agent updates; (3) build a verification harness that programmatically checks rendering and link resolution. |

### Critical Thinking Questions

1. Apply the full autopsy protocol to Case A. Identify the goal beyond "move the files" — what would a human course instructor consider a failed migration even if every file was copied correctly?

   *Hint:* Think about what a student experiences when visiting the site. Does the page load? Do the links work? Does the navigation make sense? Does the LiaScript rendering produce a readable activity? Any of these failing = the migration failed, even if all bytes were copied.

2. Friction (1) is a *specification* failure, not a model failure. The agent performed exactly as a reasonable agent would given incomplete information. What written artifact, had it existed before the migration began, would have prevented this friction, and which assignment in this course has been quietly training you to write such artifacts?

   *Hint:* The artifact is something like a style guide or specification document: "all activity files must be named `liascript-<topic>.md`, frontmatter fields must appear in this order: title, author, date, layout." Which course assignment asks you to write exactly this kind of technical specification?

3. Friction (2) is the memory problem made concrete. When the agent hits a context limit, it must summarize its own progress — and summaries lose detail. Prescribe a concrete external state representation that the agent should have maintained from the start: what fields, in what format, stored where?

   *Hint:* Think of a structured JSON or CSV file the agent writes after processing each file: `{"filename": "liascript-consensus.md", "status": "done", "output_path": "_pages/Activities/liascript-consensus.md", "checks_passed": ["renders", "links_valid"]}`. Where should this file live so the agent can read it after a context reset?

4. Design the verification harness for friction (3). Describe three programmatic checks that distinguish "done" from "done-looking" for a website migration, including what tool you would use for each check.

   *Hint:* Check 1 could use Python's `subprocess` to run `jekyll build` and count errors. Check 2 could parse every markdown file with a regex looking for `[text](url)` patterns and verify each URL returns HTTP 200. Check 3 could compare a list of expected filenames against the files actually present in the output directory.

---

## Model 2: Case B — The Browsing Agent and the Campsite

Think of hiring a personal assistant to book a campsite for you. You give them dates, a preferred region, and amenity requirements. They can read the reservation website perfectly well — but you tell them not to click "Confirm" without calling you first, because that charges your card and commits your vacation dates. The assistant's reading ability is fine; the human gate exists because the consequence of a wrong click is irreversible. Case B shows why every browsing agent needs a taxonomy of action reversibility, not just a capability list.

**The engagement.** A browsing agent is asked to find and hold a reservable campsite meeting constraints (dates, region, amenities) on a public reservation site, navigating search forms, result pages, and availability calendars rendered for human eyes.

**What happened at the seams.** The web is a hostile perception environment for agents: state lives in visual layout, controls change behavior with JavaScript (a programming language that makes websites interactive), and the same button means different things on different pages. The agent succeeded at *reading* (extracting which sites had availability) but needed tight supervision at *acting*: each click is a potentially irreversible state change, the difference between a search and a booking being one button. The human kept a confirmation gate on consequential actions, trading autonomy for safety.

| Action type | Definition | Example from Case B | Requires human gate? |
|---|---|---|---|
| **Read-only** | Observes state without changing it; can be repeated safely as many times as needed. | Loading a search results page to see which campsites have availability on given dates. | No — the agent can do this freely. |
| **Reversible write** | Changes state in a way that can be undone by a subsequent action. | Adding a campsite to a shopping cart or a "watch list" — this can be removed before payment. | Depends on cost of reversal; usually no gate needed. |
| **Irreversible write** | Changes state permanently or with significant cost to reverse; cannot be safely undone. | Clicking "Confirm Reservation" — charges a credit card, holds a campsite, sends a confirmation email. | Yes — mandatory human confirmation gate required. |

### Critical Thinking Questions

5. Classify each of the following browsing actions the agent might take as read-only, reversible-write, or irreversible-write. For each, state exactly where the human gate should sit, and explain why "gate every action" is also a wrong answer.

   Actions to classify: (a) loading the search form, (b) entering search criteria, (c) reading availability calendar, (d) adding to a cart, (e) entering credit card details, (f) clicking "Confirm Reservation."

   *Hint:* "Gate everything" fails because it eliminates the value of the agent — you might as well do it yourself. Gates should sit immediately before actions whose consequences are both irreversible and high-stakes. What makes an action high-stakes vs. merely irreversible?

6. The agent perceives a rendered web page (what a human would see in a browser), not the reservation site's database. Give one concrete misperception this gap permits — a case where what the agent reads on the page does not match the actual state of the database.

   *Hint:* Imagine the site shows "3 sites available" but between the agent reading the page and the agent clicking "Reserve," another user booked one of those sites. The page did not refresh. What does the agent believe, and what is actually true?

7. The site updates its visual layout overnight (buttons move, menus rename). Which agent architecture survives this change better: one that navigates by visual instruction ("click the green button in the top right") or one that navigates semantically ("activate the control with accessibility label 'Check Availability'")?

   *Hint:* Connect this to why MCP-style (Model Context Protocol) structured interfaces — where the site exposes typed function calls like `check_availability(dates, region)` — are fundamentally more robust than screen-scraping. What would need to change in an MCP interface for the same update to break the agent?

---

After reading Case B, notice how the action-reversibility taxonomy you built earlier in the semester reappears here as safety infrastructure — not abstract theory, but a concrete design requirement.

# Part II: Cross-Case Synthesis

Across all three cases, the single most recurrent engineering lesson is:

[( )] Larger models would have prevented every friction, since capability failures caused each problem
[(X)] Agent reliability comes from the surrounding structure: explicit specifications, externalized state, deterministic verification, and gates on irreversible actions
[( )] Browsing agents should never be used because the web is too unpredictable for automation
[( )] Humans should review every individual model call to prevent any errors from reaching users

> **⚠️ Common Misconception:** Students often conclude from cases like these that the agent "wasn't smart enough" and that a more powerful model would have avoided the friction. This is almost never the right diagnosis. In Case A, no model — however capable — can infer a naming convention that was never written down. In Case B, no model can safely decide whether to charge your credit card without human authorization. In Case C, no model can maintain a global mathematical invariant through probabilistic text generation. The frictions in all three cases are structural, not capability failures. Better model → better output quality; better surrounding structure → better reliability. Both matter, but only one of them is under your control as a system designer.

---

## Exercises

> **A third case, for teams who want it.** Two cases carry the session; this one is here for anyone whose project involves paginated or rate-limited sources.

## Model 3 (At Home, Optional): Case C — Pagination and the Proceedings

Think of editing a printed book where every chapter references page numbers in the table of contents. You add one paragraph to chapter 3, pushing every subsequent chapter back by a page. Now the entire table of contents is wrong. You could fix each entry manually — but fixing entry 5 does not know that you already "fixed" entry 4, and your fixes might cascade into new errors. The only robust solution is to freeze the content first, then compute all page numbers in one deterministic pass, then generate the table of contents from that computed result. Case C shows why some problems require restructuring the *order of operations*, not improving the *quality of operations*.

**The engagement.** A document agent assembles and repaginates a large conference proceedings: hundreds of papers, front matter, and a table of contents whose page numbers must match where papers actually land — a global constraint over a long document.

**What happened at the seams.** Local edits have global consequences: inserting one paper shifts every subsequent page number, so the table of contents is stale the moment anything moves. An agent fixing entries one at a time chased its own tail; the durable solution was to change the *order of operations*: freeze content first, compute pagination once as a deterministic pass, then generate the table of contents from the computed result. The general lesson: when a task has a global invariant, do not ask a stochastic local editor to maintain it; restructure the workflow so a deterministic tool enforces it.

| Task component | Right tool | Wrong tool | Why |
|---|---|---|---|
| Formatting each paper's title page consistently | LLM with a formatting prompt | Hard-coded regex | The LLM can handle varied input formats and produce consistently styled output. |
| Computing page numbers from final layout | Deterministic algorithm (count pages from start) | LLM asked to "figure out" page numbers | An LLM can hallucinate or drift; page numbers must be computed, not estimated. |
| Writing an abstract summary for each paper | LLM with a summarization prompt | Regex or keyword extraction | Summarization requires reading comprehension that only a language model can provide. |
| Verifying that all table-of-contents entries match their paper's actual starting page | Programmatic check (`assert toc[paper] == actual_start[paper]`) | LLM asked to "double-check" the table | A programmatic check is deterministic and exhaustive; an LLM check is probabilistic and may miss errors. |

### Critical Thinking Questions

8. State the global invariant of the proceedings document as a formal sentence with a universal quantifier (a statement that begins with "for every" or "for all"). A global invariant is a condition that must be true across the entire document simultaneously — not just for one paper at a time.

   *Hint:* A universal quantifier means the statement must be true for every paper in the proceedings, without exception. "For every paper P in the proceedings, the page number listed in the table of contents for P equals the actual page on which P begins in the assembled document."

9. Why is an LLM, however capable, the wrong instrument for *maintaining* this invariant — even if it is excellent at other parts of the task? Which parts of the proceedings assembly task is the LLM genuinely the right tool for?

   *Hint:* The invariant is a mathematical constraint that must be exactly true for every element. LLMs generate text probabilistically — they can be correct most of the time but not all of the time. What are the consequences of being wrong on even one entry? What parts of assembly require language understanding rather than mathematical precision?

10. Generalize: identify one global invariant in *your* final project (e.g., a citation that must match a real source, a budget that must sum to a correct total, a generated schedule with no time conflicts). Specify the deterministic checker you will build to own and enforce it.

    *Hint:* "Deterministic" means the checker always gives the same answer for the same input, and its answer is always provably correct. A Python `assert` statement, a checksum, a database constraint, or a unit test can all be deterministic. Which one is right for your invariant?

---


1. *Jigsaw teach-back.*

   *What to do:* In mixed groups (one member from each home team in each new group), each Presenter teaches their assigned case in three minutes using only the five-question autopsy protocol as a guide. Recorders from each home team capture at least one repair idea per case that their home team had not considered.

   *Starter hint:* Structure your three-minute teach-back as: Goal (30s) → Architecture (30s) → Perception (30s) → Friction (45s) → Repair (45s). Practice the timing before the jigsaw.

   *You've succeeded when:* Every member of your mixed group can state the central engineering lesson of each case without looking at notes, and your Recorder has written down at least one new repair idea per case.

2. *Pattern bingo.*

   *What to do:* As a class, tally which Unit 3 patterns (human-in-the-loop gate, external state representation, specification document, deterministic verifier, critique-refine loop, programmatic check) appeared as the prescribed repair across all three cases. Which pattern earned its keep most often, and does that pattern match the "use the least dynamic pattern that solves the problem" heuristic?

   *Starter hint:* Make a 3×6 table: rows are Case A, B, C; columns are the six patterns listed above. Check each cell where that pattern appeared as a repair. Which column has the most checks?

   *You've succeeded when:* You can defend a claim about which pattern is most universally applicable across agent systems, with evidence from at least two of the three cases.

3. *Pre-mortem.*

   *What to do:* Run the autopsy protocol *prospectively* on your own project proposal: predict its Case-A-style specification gap, its Case-B-style irreversible action, and its Case-C-style global invariant. Write up the pre-mortem and append it to your project proposal as a required deliverable.

   *Starter hint:* For the specification gap: what assumption are you making about your data format, naming convention, or user behavior that you have not written down? For the irreversible action: what is the worst thing your agent could do if it misunderstands a user request? For the global invariant: what constraint must be true across your entire output, not just locally?

   *You've succeeded when:* Your pre-mortem identifies a real risk in each of the three categories — not a hypothetical risk you invented for the exercise — and proposes a concrete mitigation for each one that you will actually implement.

---

## Reflection Prompt

*Personal:* In each case, the human's judgment moved *up* a level — from doing the task directly to specifying, gating, and verifying work done by an agent. Which of these three higher-level roles (specifier, gatekeeper, verifier) comes most naturally to you, and which would require the most deliberate practice to develop?

*Technical:* The autopsy protocol asks five questions in a fixed order. Design a sixth question that you believe is missing — one that would have surfaced an additional important lesson from at least one of the three cases. Justify your addition.

*Societal:* In each case, the human retained meaningful control — reviewing diffs, confirming reservations, restructuring the pagination workflow. As agentic systems become faster and more capable, the economic incentive will be to remove those human gates. For each case, state the minimum level of human oversight you would require if the stakes were higher (the migration is for a medical records system, the booking is for a charter flight, the document is a legal brief). Does your answer change based on the stakes, and if so, what principle underlies that change?

---

→ Coming Up Next: In the *Training Data and Bias* activity, we zoom out from individual agent systems to the training data and design choices that shape every model's behavior — and examine how bias enters the pipeline at every stage, from data collection through deployment.

## Further Reading

- Anthropic engineering blog. "How we built our multi-agent research system" (2025, online), on verification and state in long-running agents.
- Yao et al. "WebShop" and successors on web agents (2022 onward), for the perception problems of Case B.
- Your Rubric Pipeline Lab specification, which industrializes the verification mindset of all three cases.
