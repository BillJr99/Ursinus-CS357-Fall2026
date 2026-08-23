<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-howiai.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-howiai.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# How I AI: A Vault, a Charter, and Agents That Talk Through GitHub

You have spent seven weeks learning how agents work.  Today is about how a person actually *lives* with them.

Here is the problem this session solves.  Every AI tool you use keeps its own private memory of you.  Your coding agent knows the files you opened this morning.  Your chat window knows this conversation and forgets it tomorrow.  None of them know what the others know, and none of them survive a closed tab.  So you re-explain yourself, constantly, to tools that could in principle already know, and every session starts from zero.

The fix is not a better tool.  It is a **place**: a folder of plain Markdown files that you own, that any agent can read, that lives under version control, and that agents write back into under rules you wrote down.  Two moves make it work, and they are the two parts of today.

1.  **Your notes become memory agents can read.**  A vault of plain files, organized into zones, with a contract at the root saying what may be touched.
2.  **Your repository becomes the channel agents talk through, and the record of why.**  Not a chat window: a charter that states what the project is for, plans written before work starts, issues and pull requests as the medium, and a small set of handoff documents that let one agent stop and another pick the work up without either of them sharing a thought.

Then the room is yours for the rest of the session: bring what is stuck.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  This is a build-and-discuss day: the Manager keeps the setup moving, the Recorder captures the team's design decisions (especially the zone boundaries you choose), the Presenter shows the team's `AGENTS.md` to the class, and the Reflector notes where the group disagreed about what an agent should be allowed to write.  After class, answer the reflective prompt individually.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Vault** | A folder of plain Markdown files that is your notes. No database, no proprietary format, so any tool or agent can read it | The `vault/` tree in Model 1, edited in Obsidian and stored on GitHub |
| **Zone** | A directory whose name tells every agent what it may do there: read only, write freely, never touch | `raw/` (never modified), `wiki/` (agents author here), `.obsidian/` (hands off) |
| **Agent contract** | A file at the root of a repository or vault stating the rules any agent must follow inside it. The `AGENTS.md` you wrote for `cs357-work` in Week 1, grown up | Model 2: a contract with zone boundaries, a synthesis rule, and a stop rule |
| **Durable memory** | Project state that lives in files under version control rather than in a conversation, so it survives the session, the tool, and the model | `.ai/SESSION.md` and `.ai/CURRENT_TASK.md` in Part II |
| **Handoff** | A deliberate stop in which an agent writes down enough state that a *different* agent can continue safely | The kickoff prompt in Model 4, pasted into a fresh session |
| **Read-only mount** | Giving a program access to a directory it can read but not change, enforced by the operating system rather than by instructions | `-v "$HOME/vault:/reference:ro"` when you run an agent in a container |
| **Charter** | The constitution of a project: mission, ranked values, definition of done, and the guardrails an agent may never cross. Written once, amended deliberately, reread at the start of every session | `CHARTER.md` in Model 3, and the ranked-values list that resolves conflicts without asking you |
| **Traceability** | Being able to answer, weeks later, *why* something is the way it is: which goal it served, what was decided, who or what did it, and what was rejected | A wiki page, a decision log entry, a session entry, and a commit that all point at each other |
| **Observability, isolation, reversibility** | The three properties that make delegating safe: can I see what it did, can I bound what it reaches, can I undo it. Named in *Your AI Workbench*, Step 8.5, and applied to your own notes today | The session log, the `:ro` mount, and `git revert` |

---

### Before You Start

**You need:** your `cs357-work` repository, opencode (from *Your AI Workbench*), and a GitHub account.  Obsidian is a free download and takes about two minutes; get it started now if you want to follow Part I on your own machine: [obsidian.md](https://obsidian.md).

**You do not need** to have finished any particular lab.  If you are behind, Part III of today is explicitly for that.

**What you will have at the end:** a vault with zone boundaries and a written agent contract, one repository configured with handoff documents, and a plan for the thing you are currently stuck on.

---

# Part I: The Vault as Memory You Own

In this part you build the read side: a place your agents can consult so that you stop re-explaining yourself, and a set of boundaries that make it safe to let them write there.

## 1.  Why a Folder of Text Files

The design has four pieces, each independently replaceable, and the replaceability is the point: nothing here locks you into a vendor.

| Piece | What it replaces | Why | What you lose without it |
|---|---|---|---|
| **Obsidian** as the editor | Five note apps in five formats no agent can read | The vault is *just Markdown files in a folder*. Any agent, any language, any tool reads and writes them with no special library | Interoperability. Your notes become a format agents cannot reach |
| **GitHub** as the host | Local files only reachable by a program on the same machine | A versioned API surface that an agent in a container, on a server, or on your phone can reach with a scoped token | History, portability, and any audit trail of what an agent changed |
| **Zones** (directory boundaries) | "Be careful" as an instruction | A directory layout that encodes what may be modified, so the rule is visible in `ls` rather than remembered | Safety. An agent asked to "help with my notes" has no way to know what is sacred |
| **`AGENTS.md`** at the root | Configuring each tool separately | The contract travels *inside* the repository, so every agent reads it with zero per-tool setup | Consistency. Each tool behaves differently, and you find out when it matters |

Note what is *not* in that table: any particular AI company.  The vault outlives whichever model you are using this year, which is most of the argument for building it this way.

---

## Model 1: The Three-Zone Vault

Structure is what turns a pile of notes into a system an agent can be trusted inside.

```text
vault/
|-- AGENTS.md           # the contract: read completely before acting
|-- LLMMEMORIES.md      # standing context: who I am, what I am working on
|-- SYSTEMPROMPT.md     # standing instructions, the ones you retype everywhere
|-- raw/                # READ-ONLY inbox: PDFs, transcripts, exports. Never modified.
|-- wiki/               # the curated knowledge base. Agents author HERE.
|   `-- index.md        # hub page, links out to every topical section
`-- .obsidian/          # editor state. Agents never touch this.
```

The boundaries *are* the design.

- **`raw/` is a one-way inbox.**  Humans and automations drop source material in; nobody, human or agent, edits it.  Sources stay pristine, which means that if an agent's interpretation turns out to be wrong, you can reprocess from the original.
- **`wiki/` is where authored knowledge lives**, in topical folders with links between pages.  Agents are its primary authors, and their job is **synthesis** from `raw/`, not transcription of it.
- **The three root files** carry the context you would otherwise retype: who you are, what you are working on, and how you want an agent to behave.

An agent processing a new PDF in `raw/` notices a typo in the PDF, and also notices that `wiki/index.md` has no link to the page it just wrote.  Under this structure, the correct actions are:

[( )] Fix the typo in the PDF and add the index link
[(X)] Leave the PDF untouched, add the index link, and note the source's error on the wiki page if it matters
[( )] Fix the typo and skip the index; navigation is the human's job
[( )] Move the PDF into `wiki/` so it can be edited

    --{{0}}--
The instinct to fix the typo is a good instinct about writing and a bad instinct about archives.  The moment an agent edits a source, you no longer know what the source said, and every downstream summary becomes unverifiable.  Leave the record alone; annotate the interpretation.

> **Common Misconception:** "It is my private repository, so agents can write anywhere; I can always fix mistakes."  Two problems.  An agent that overwrites something in `raw/` destroys the pristine record, and you cannot fix what you can no longer read.  And an agent that writes into `.obsidian/` can corrupt the editor's sync state in a way that fails *silently*: your edits simply stop propagating, with no error, for days.  Zone boundaries exist precisely because "I will fix it later" is not a recovery strategy for a failure you do not notice.

---

## 2.  The Contract

`AGENTS.md` is the same kind of file you wrote for `cs357-work` in Week 1, doing a bigger job.  It opens with a non-negotiable instruction and then answers four questions:

```markdown
# Agent Contract for this Vault

Read this entire file before taking any action in this repository.

## Zones
- `raw/` is READ-ONLY. Never modify, rename, or delete anything here.
- `wiki/` is yours to author. Prefer enriching an existing page over creating a new one.
- `.obsidian/` is editor state. Never touch it.

## How to work
1. Read this contract, then `wiki/index.md`, then the relevant `raw/` material.
2. Synthesize; do not transcribe. If two sources disagree, say so on the page
   rather than smoothing it over.
3. Link every new page from `wiki/index.md`.
4. Commit atomically, one topic per commit, with a message naming the source.

## Answering questions
Answer from `wiki/` first. Consult `raw/` only to fill a gap, and when you do,
update the wiki page before you answer me.

## Stop and ask
- Anything that would delete a file.
- Anything touching `raw/` or `.obsidian/`.
- Any claim you cannot ground in a file in this vault.
```

Look at what the last section buys you.  "Any claim you cannot ground in a file in this vault" is a hallucination guard written as a permission rule, and it is enforceable in a way "please be accurate" is not.

### Belt and braces: make the boundary real

A contract is an instruction, and instructions are advisory.  When you run an agent in a container, you can make `raw/` read-only by construction:

```bash
docker run --rm -it \
  -v "$HOME/vault/wiki:/vault/wiki" \
  -v "$HOME/vault/raw:/vault/raw:ro" \
  course-agent
```

The `:ro` is the whole difference between a rule the agent is asked to follow and a rule the operating system enforces.  This is the blast-radius principle from *Your AI Workbench*, applied to your own notes.

### Critical Thinking Questions

1.  The contract says "synthesize, do not transcribe."  Give a concrete example of an agent obeying the letter of that instruction while defeating its purpose.  Then propose a sentence you would add to the contract to close the gap you found.

   > *Hint: What does a "summary" that is 90 percent of the original's length accomplish?  What about one that drops every caveat?*

2.  Compare the two enforcement mechanisms above: the `AGENTS.md` sentence "`raw/` is READ-ONLY," and the `:ro` on the mount.  Name one failure each one catches that the other does not.

   > *Hint: One survives a model that ignores instructions.  The other only applies when the agent runs in a container you configured.*

3.  Your vault will hold personal context by design.  Name three categories of information you would deliberately keep *out* of even a private, synced vault, and state the principle behind each.  Consider both a leaked token and a compromised account.

   > *Hint: Credentials are the easy one.  What about information that is not yours to store, such as someone else's messages?  What about categories that carry breach-notification duties regardless of who saw them?*

4.  The vault is a retrieval problem, and you are in the middle of building the machinery for it right now in the *RAG Knowledge Base* lab.  Compare two ways of answering a question from your notes: hand the agent the whole `wiki/` folder, or index it and retrieve only the relevant chunks.  At what vault size does the first one stop working, and what exactly breaks?

   > *Hint: You do not need a number to answer this; you need the reason.  A model can only read a fixed amount of text at once.  What happens to the oldest part of what you handed it when the folder outgrows that limit, and how would you notice?  Next session, *Memory and the Small Context Window Principle*, gives that limit its name and its arithmetic.*

---

# Part II: The Repository as the Channel Agents Talk Through

In this part you build the write side, and the collaboration side.  In *Coding Agents* you saw the basic pattern: an issue is the task, a pull request is one agent's attempt, and a review comment is an instruction a *second* agent can pick up without ever sharing the first one's context.  Today we make that survive a long project, which takes three things a chat window cannot give you: a **charter** that decides the recurring questions once, **plans** reviewed before work starts, and a **written record** that lets anyone reconstruct why the project is the way it is.

## 3.  Conversation Is Not Project State

Here is the single sentence this part is built on:

> **The repository is the durable memory for the project.  Conversation history is not durable project state.**

Everything an agent "knows" at the end of a working session evaporates when that session ends.  It evaporates when the context window fills, when a quota runs out, when you switch tools, when the model is upgraded under you.  If the only record of *why* the code looks like this lived in that conversation, it is gone, and the next agent, or the next you, starts by guessing.

So write it down, in files, in the repository.  The course provides a set of ready-made skeletons for exactly this at [`files/agent-templates/`](https://www.billmongan.com/Ursinus-CS357/files/agent-templates/README.md).  The core five:

| File | Job | Written by |
|---|---|---|
| `START_HERE.md` | The fixed read order for any agent arriving at this repository | You, once |
| `CHARTER.md` | Mission, non-negotiable rules, milestones, guardrails. The constitution | You, revised rarely |
| `.ai/CURRENT_TASK.md` | The active-work pointer. A new agent should be able to resume from this file alone | The agent, before every stop |
| `.ai/SESSION.md` | Append-only journal, one dated entry per working session, each ending with a **Next Safe Action** | The agent, as it works |
| `.ai/KNOWN_ISSUES.md` | Verified defects and constraints, with stable IDs so commits can reference them | Either, when verified |

Two design choices are worth naming because they are not obvious.

**`SESSION.md` is append-only.**  Old entries are never deleted, only annotated ("superseded by the entry below").  A journal you can rewrite is a journal that cannot tell you what you used to believe, and *what you used to believe* is exactly what you need when a decision turns out wrong.

Every session entry ends with a Next Safe Action.  Not "next steps," which is a wish list.  One concrete action that is safe to take with no further context.  It is the handoff, written before it is needed.

---

## 3b.  The Charter: Deciding Once Instead of Every Time

`AGENTS.md` told an agent what it may *touch*.  A **charter** tells it what the project is *for*, and that turns out to answer a different and harder class of question.

Watch the difference.  Halfway through a task an agent notices that making the tests pass quickly would mean loosening an assertion.  Nothing in `AGENTS.md` forbids editing a test.  So it either stops and asks you (interrupting, and it will ask again tomorrow) or it guesses.  A charter that ranks **correctness above speed** answers the question without either.

That is the whole trick: a charter is where you make a decision **once**, in writing, so that neither you nor any agent has to relitigate it at three in the afternoon.

The course template at [`files/agent-templates/CHARTER.md`](https://www.billmongan.com/Ursinus-CS357/files/agent-templates/CHARTER.md) has six sections that earn their place:

| Section | The question it settles in advance |
|---|---|
| **Mission** | What is being built, and for whom. One or two sentences, product not technology |
| **Ranked values** | When two goods conflict mid-task, which one wins. The *ranking* matters more than the list |
| **Definition of success** | A concrete, observable test for "done," so nobody has to have an opinion about it |
| **Long-term architecture** | The one design seam you refuse to blur, however convenient blurring it would be |
| **Repository layout** | Which directories are immutable sources and which are workspace. Zones again, one level up |
| **Git policy** | That history lives in git, and never in `file_old.py`, `file_v2.py`, or `file_final_FIXED.py` |

Two of those deserve a second look.

**Ranked values, not listed values.**  "We value correctness, speed, and maintainability" resolves nothing, because every conflict is between two things on that list.  Ranking them is what makes the document operational:

```markdown
# Engineering Philosophy

Every engineering decision prioritizes, in order:

1. Correctness
2. Reproducibility
3. Maintainability
4. Automation
5. Documentation
```

Now "loosen the assertion to go faster" resolves itself: correctness outranks everything, so no.

**The documentation authority rule**, which is the sentence that makes long-running agent work possible at all:

> The agent shall never work from memory when project documentation exists.  Before every session, reread the charter, the current task, and the session log.  If project documentation conflicts with remembered context, prior chat context, or assumptions, **the documentation wins.**  If the documentation is incomplete, update it rather than relying on memory.

Read that as a policy about **context drift**.  Over a long project an agent (or a person) accumulates half-remembered decisions, some of which were reversed.  The rule says the file is the truth and the memory is a rumor.  It is the same instinct as `raw/` being read-only, aimed at beliefs instead of files.

### Plan, then act, then record

Your charter, your plans, and your session log form one loop, and each piece is doing a job the others cannot:

```text
CHARTER.md          why this project exists, and what always wins   (rarely changes)
   |
   v
.ai/CURRENT_TASK.md what we are doing now, and what "done" means    (per milestone)
   |
   v
the plan            what the agent intends to do about it, before   (per task)
   |                it touches anything -- reject it here
   v
the diff / the PR   what it actually did                            (per change)
   |
   v
.ai/SESSION.md      what happened, what did not, what is next       (per session)
docs/DECISION_LOG   what we decided and what we rejected, and why   (when it matters)
```

Read that column top to bottom and you have **traceability**: six weeks from now, a line of code traces back to a diff, which traces to a session entry, which traces to a task, which traces to the charter.  Nobody has to remember anything, and "why is it like this?" has a written answer instead of an argument.

The [decision log](https://www.billmongan.com/Ursinus-CS357/files/agent-templates/DECISION_LOG.md) is the one people skip, and it is the one that pays.  It records not only what you chose but **what you rejected and why**, which is the only thing that stops a project from re-proposing the same bad idea every three weeks, whether the proposer is a teammate or an agent starting from a fresh context.

Your team's charter ranks **reproducibility above automation**.  An agent proposes replacing your pinned dependency versions with floating ones so that upgrades happen automatically.  Under the charter, what happens?

[( )] The agent asks you, because the charter does not mention dependencies
[(X)] The proposal is rejected without asking: floating versions trade reproducibility for automation, and the charter already ranked those
[( )] The agent implements it, because automation is on the list of values
[( )] The charter needs a new section on dependency management before this can be resolved

    --{{0}}--
The charter never mentions dependencies, and it does not need to.  That is exactly what ranking buys you: it resolves cases the author never anticipated.  A charter that had to enumerate every decision would be a rulebook, and it would be out of date the day after you wrote it.

---

## 3c.  Observability, Isolation, Reversibility, Applied to Your Own Work

You met these three in *Your AI Workbench*, Step 8.5, as properties of a container and a git repository.  Everything in today's session is those same three properties, applied to your notes and your projects instead of to one afternoon's code.

| Property | In the vault (Part I) | In the repository (Part II) | The failure it prevents |
|---|---|---|---|
| **Observability** | `git log` on the vault shows every agent write, with a diff. The wiki cites `raw/`, so a claim traces to a source | `SESSION.md` says what was done and *not* done; the PR shows the change; the decision log says why | "Something in my notes is wrong and I have no idea when it got there or what it was based on" |
| **Isolation** | Zones, plus `:ro` on the `raw/` mount. An agent authoring the wiki cannot corrupt the sources it is summarizing | A scoped token for one repository; a branch per attempt; an agent that can open a PR and cannot merge it | "The agent asked to tidy my notes and rewrote a source I can no longer recover" |
| **Reversibility** | Every vault write is a commit. `git revert` puts a bad synthesis back | Every change arrives as a reviewable, revertible commit on a branch, not as an edit to `main` | "The agent's cleanup pass was wrong and there is no earlier version" |

The pattern is worth naming because it generalizes past this course.  Each property is bought the same way in both columns: **observability by writing things down in files**, **isolation by boundaries the system enforces rather than boundaries you ask for**, and **reversibility by never having exactly one copy of anything that matters.**

And notice which one is most often missing in practice.  Isolation is the one people think of, because it sounds like security.  Reversibility is the one that actually saves the semester, and it is nearly free: it is a commit before you start.

> **Common Misconception:** "Reversibility means I can undo anything, so I can be less careful about the other two."  Reversibility is bounded by observability.  You can only revert a change you *noticed*, and the dangerous agent failure is not the dramatic one; it is the small wrong edit that lands in a wiki page you do not reread for a month, by which time you have written three things on top of it.  Git will happily let you undo it; nothing will tell you that you should.

---

## Model 2: A Handoff, Concretely

An agent is at the end of its useful context.  Before it stops, it writes:

```markdown
## 2026-10-15 Continuation: retrieval eval harness

Added `eval/run_goldenset.py`, which loads `goldenset.json` and scores each
item with the substring rule. 7/10 pass.

The three failures are all citation-shaped items (see KNOWN_ISSUES KI-004);
the retriever returns the right chunk and the generator invents a page number
that is not in it. This is a generation problem, not a retrieval problem, and
I did not change the retriever.

Did NOT do: the normalized-match rule. `goldenset.json` items 4 and 9 assume it.

**Next Safe Action:** implement `normalize()` in `eval/rules.py` (lowercase,
strip punctuation, collapse whitespace) and re-run; expect items 4 and 9 to
flip to PASS with no other change.
```

A new agent is then started cold with a kickoff prompt that says, in effect: *you are working on this repository, your authority is X, read `START_HERE.md` then `CHARTER.md` then `.ai/CURRENT_TASK.md` then the last three entries of `.ai/SESSION.md`, and do not begin work until you have.*

Nothing was remembered.  Everything was **read**.

### Critical Thinking Questions

5.  The entry above explicitly records what the agent did *not* do, and why item 4 and 9 depend on it.  Why is the not-done list often more valuable to the next agent than the done list?

   > *Hint: The done work is visible in `git diff`.  Where is the not-done work visible?*

6.  "Next Safe Action" carries two constraints: it is *next*, and it is *safe*.  Write a Next Safe Action for your own project thread as it stands right now, then check it against both words.  Which of the two was harder to satisfy honestly?

7.  Compare this handoff mechanism with the review-comment pattern from *Coding Agents*, where one agent responds to a comment another agent left on a PR. Both let agents coordinate without sharing a context window.  When would you reach for each, and what does the session journal give you that a PR thread does not?

   > *Hint: One is scoped to a single change.  The other spans every change.  Consider what you would read six weeks from now, and where it lives.*

8.  Your Project Thread team has four people and probably several agents.  Name one specific failure this whole apparatus prevents that a group chat would not, and one failure it does *not* prevent.

> **Common Misconception:** "This is a lot of paperwork for something a bigger context window will solve."  Context windows have grown by orders of magnitude and this practice has become *more* common, not less, because the problem was never only size.  A conversation is unreviewable by your teammates, invisible to CI, unsearchable next semester, and gone when the tool changes.  Files in a repository are none of those things.  The paperwork is not a workaround for small models; it is what makes the work legible to anyone who is not the person who was in the room.

---

## 4.  Do This Now (about thirty minutes)

Pick **one** of your own repositories: `cs357-work`, or your Project Thread repository if your team is ready to adopt this together.

1.  **Charter.**  Copy [`CHARTER.md`](https://www.billmongan.com/Ursinus-CS357/files/agent-templates/CHARTER.md) into the repository root and fill in three sections for real: the mission in one sentence, **five ranked values**, and a definition of success someone else could check.  Leave the rest as template for now.  Ranking the values is the part that takes the longest and the part that is worth doing.
2.  **Handoff state.**  Create `.ai/` and copy in `CONTEXT.md`, `CURRENT_TASK.md`, and `SESSION.md`.  Fill in `CONTEXT.md` with one true sentence about your project.
3.  **Contract.**  Write `AGENTS.md` (or extend the one you already have) with a **Stop and ask** section of at least three items that are true for your project, and one line pointing at the charter.
4.  **Commit all of it before the agent runs.**  This is your reversibility line, and it takes ten seconds.
5.  **Plan first.**  Start `opencode` with a small, real task from your backlog, and open with: *read `CHARTER.md`, `AGENTS.md`, and `.ai/CURRENT_TASK.md`.  Then tell me what you intend to do and stop.*  Read the plan.  Reject it if it conflicts with your ranked values, and note which value caught it.
6.  **Then let it work**, and when it finishes: *append a dated entry to `.ai/SESSION.md` describing what you changed, what you did not do, and one Next Safe Action.*
7.  **Read what it wrote.  Correct it.**  Then commit.

> **You've succeeded when** your repository has a charter with ranked values, a session entry an agent wrote and you edited, and you can point to one sentence in that entry you had to fix.  That sentence is the reason step 7 exists.  Bonus, and it is the real one: if a plan got rejected in step 5, write down which ranked value did the rejecting.

---

# Part III: Studio

The rest of the session is yours, and it is deliberately unstructured.  This is the mid-semester catch-up point, and the schedule assumes you will use it.

Bring one of these:

- **A lab that is not running.**  Bring the error, the command that produced it, and what you already tried.  Teams that have solved it are the first line of help; I am the second.
- **A design decision your team is stuck on.**  Stakeholder brief scope, project direction, which lab direction to take.  Fifteen minutes of arguing it out loud with someone outside your team is usually enough.
- **Something you want to build that is not on any assignment.**  This is the best possible use of a studio day.
- **The vault you started in Part I**, if you want to keep going on it.

For the visual-building route through a local agent stack (Langflow, wiring containers together into a system), the *Local Agent Stack* material remains the reference and is linked from the Local Agent Lab's Direction 2.

---

## Exercises

1.  *Zone audit.*

   - *What to do*: Take a folder you already have (course notes, project files, downloads) and sort it into the three zones: what is a pristine source, what is authored, and what is machine state.  Write the resulting tree.
   - *Starter hint*: Most people find their existing folder has no `raw/` at all, because sources were edited in place.  Note what you would not be able to reprocess.
   - *You've succeeded when*: You have a tree with three zones, and you can name at least one file whose zone was ambiguous, plus the rule you used to decide.

2.  *Contract stress test.*

   - *What to do*: Trade `AGENTS.md` files with another team.  Find one instruction in theirs that an agent could obey literally while producing a result they would not want.  Write the counterexample; propose the fix.
   - *Starter hint*: Look for adjectives.  "Concise," "relevant," "appropriate," and "clean" are where the gaps live.
   - *You've succeeded when*: The other team agrees your counterexample is real, and their revised sentence closes it.

3.  *Rank your values, and find where it hurts.*

   - *What to do*: Write the five ranked values for your Project Thread as a team, then find a real decision your team has already made that the ranking would have *reversed*.  If you cannot find one, your ranking is probably too agreeable to be useful; try again with a harder pair.
   - *Starter hint*: The productive conflicts are the ones you actually feel: correctness against shipping by Thursday, reproducibility against convenience, thoroughness against the number of hours you have.
   - *You've succeeded when*: Your team can name one past decision the ranking contradicts, and has decided out loud whether to change the decision or change the ranking.

4.  *Traceability drill.*

   - *What to do*: Pick one file in your project and trace it upward: which commit last changed it, which session entry or PR describes that change, which task it served, and which charter goal that task served.  Write the chain.
   - *Starter hint*: Expect the chain to break.  Note the exact link that is missing; that missing link is the document you are not keeping.
   - *You've succeeded when*: You have either a complete four-link chain, or a precise statement of which link broke and what you would have had to write down to keep it.

5.  *Cold-start test.*

   - *What to do*: Hand your `.ai/` documents to a teammate who has never seen your project, and ask them to state, in one minute and without asking you anything, what the project is and what they would do next.
   - *Starter hint*: If they need to ask you a question, the answer to that question belongs in a file.  Add it.
   - *You've succeeded when*: A teammate outside your project can name your Next Safe Action after reading only your files.

6.  *Read-only proof.*

   - *What to do*: Run an agent in a container with your `raw/` mounted `:ro`, and explicitly instruct it to modify a file there.  Capture the error.
   - *Starter hint*: The point is to see the operating system refuse, not the model refuse.  Note which one of the two you would rather rely on.
   - *You've succeeded when*: You have a terminal transcript in which the agent tried and the filesystem said no.

---

## Reflection Prompt

*Personal*: You just built a place where a machine can read your notes.  Sit with that for a moment.  What did you decide to keep out, and was that decision about risk, about privacy, or about something harder to name?  Did writing the contract change what you were willing to store?

*Technical*: Compare the two memory mechanisms in this session: the vault (durable, semantic, human-authored) and the session journal (append-only, procedural, agent-authored).  For a system you would actually run, which one would you build first, and what does the other one buy you that the first cannot?  Then take the three properties from Section 3c and rank *them* for your own project: if you could only have two of observability, isolation, and reversibility, which do you give up, and what goes wrong the first time you need it?

*Societal*: The argument for this architecture is autonomy: your context lives in files you own rather than inside a company's product.  But it also means a very complete record of your thinking exists in one place, readable by any agent you point at it.  Who else could want that folder, under what circumstances, and does "it is private" mean what you would want it to mean?  Compare the risk you are accepting here against the risk of leaving the same context scattered across five vendors' servers.

---

-> Coming Up Next: In *Memory and the Small Context Window Principle* we take the idea underneath today's vault and make it precise.  You have just built external memory by hand; next session asks why an agent needs it, what the context window actually costs, and how to keep each agent's working set small enough to be reliable.

## Further Reading

- [`files/agent-templates/`](https://www.billmongan.com/Ursinus-CS357/files/agent-templates/README.md), the full set of course templates: charter, kickoff prompt, decision log, RFC skeleton, and the personal-assistant layer.
- Obsidian: [obsidian.md](https://obsidian.md).  The vault is a folder; nothing here depends on the app.
- Andrej Karpathy on the "LLM wiki" pattern: a curated, linked knowledge base maintained *with* a model rather than retrieved *by* one.
- Tiago Forte.  *Building a Second Brain*.  The knowledge-management tradition this borrows from, written before agents could read your notes.
