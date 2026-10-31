<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-iterationloops.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-iterationloops.md

import: https://raw.githubusercontent.com/LiaTemplates/Pyodide/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Karpathy Loop and the Gauntlet Loop: Iterating With an Agent

In *Coding Agents: OpenCode, Spec-First Development, Hooks, and Reading the Log*, you wrote a specification before any code existed and watched an agent implement it.  Today you put that work inside a loop, and you set the loop up so the agent runs it.

Two loops do the job, and one of them has a variant you should recognize.  The **Karpathy loop** moves in small steps, each one verified by a check that already exists; its **autoresearch** variant keeps the same shape but lets a measured number stand in for the check.  The **Gauntlet loop** writes the check first, as a rubric, and then attacks each candidate until no material defect remains.  All of them are configuration plus a command.  You leave today with the files that configure them, the commands that run them, one gauntlet round scored against a rubric you wrote, and one metric round that discards its own best idea.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Read each model as a team, then answer the Critical Thinking Questions on your own before discussing.  The Recorder posts the team's answers to the Class Activity Questions discussion board; the Presenter reports out wherever you disagreed.  After class, complete the Reflection Prompt in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Karpathy loop** | Ask for one small change, run the check, commit or restore, repeat.  The agent never gets more than one verifiable step ahead of you | Model 1: two increments to `normalize_title`, each one a commit |
| **Gate** | A point where the loop cannot continue until a person or a deterministic check says so | The plan gate and the check gate in Model 1 |
| **Rubric** | The written check: what must be true, how to verify it, and whether a failure is material.  You write it before the agent runs | Section 7: the same rubric in a qualitative form and a quantitative one |
| **Material defect** | A flaw that could change correctness, usefulness, compliance, interpretation, feasibility, safety, or a user's decision.  Style preferences usually are not | Default `max_results` of 10 when the spec says 5 |
| **Permission block** | The `permission` section of `opencode.json`, which decides what opencode may do without stopping to ask you | Section 3: `git` allowed, `rm` denied, everything else asked |
| **Auto mode** | opencode's `--auto` flag, which approves anything you did not explicitly deny.  Not for an agent running on your own machine: it belongs inside a container or a disposable VM, never on a host with your files and credentials on it | Section 9, with the isolation it requires |
| **Handoff directory** | The `.ai/` files that hold the loop's state between turns and between agents | Section 5: where the Karpathy loop writes down what it just did |
| **Gauntlet loop** | Parse the task, clear the fog, write the rubric, generate Candidate 0, critique it adversarially, revise, verify, and stop when no material defect remains | Model 3: one round against your `spec.md` |
| **Source of truth** | The authoritative basis the work is judged against: your requirements, your spec, your approved decisions, then evidence, then the agent's own criteria, in that order | `spec.md` and the rubric outrank anything the agent decides on its own |
| **Fog** | An unresolved decision, dependency, ambiguity, or missing fact that could materially change the work.  Fog is cleared, never disguised as a settled assumption | "Score is a float from 0 to 1": scored how? |
| **Converged result** | A candidate for which the latest critique finds no material defect that warrants revision | The stopping condition of every gauntlet preset |
| **Evaluation metric** | A single number a program computes from an artifact's behavior on inputs the loop may not edit, with a target fixed before the loop starts | Model 4: mean reciprocal rank over twelve held-out queries |
| **autoresearch** | Karpathy's variant of the loop, in which a metric rather than a test decides whether an attempt is kept | Model 4: a baseline and three attempts, one of them discarded for a worse score |

### Before You Start

**You need:** your `cs357-work` repository with the `spec.md`, `AGENTS.md`, and `system_prompt.txt` from the OpenCode Studio lab, plus opencode and Ollama from *Your AI Workbench*.  Sections 2 and 6 write two new files into that repository, and Model 3 runs against your own `spec.md`.  Check with:

```bash
git -C ~/cs357-work status
```

**Working without a terminal.** Everything today can be done by prompting, in the opencode desktop application or in the terminal interface.  Each command comes with the prompt that does the same job.  Two settings make the prompt-only route work, and both are easy to miss: in the desktop application, turn on **File -> Settings -> Show Agent** so the agent selector appears beside the model dropdown, and in the terminal interface press **Tab** to cycle agents and type `/models` to pick the model.

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.

| Minutes | What we do |
|---|---|
| 0-6 | Key Concepts, and why iteration beats one big prompt |
| 6-18 | Model 1's two increments, and the six parts of a loop prompt |
| 18-34 | Part II: the four files, one increment, the `.ai/` directory, and Model 2's broken run |
| 34-42 | Part III: the seven steps, and the rubric written two ways |
| 42-58 | Model 3 from prompt to convergence, and the code cell |
| 58-70 | Part IV: which loop when, unattended loops, auto mode, and Model 4's metric loop |
| 70-75 | Report-out.  Exercises, the Extension, and the reflection are take-home |

Anything marked self-paced sits outside this budget, and nothing graded assumes it.

---

# Part I: Two Loops, One Habit

## 1.  Why Iteration Beats One Big Prompt

That session left you with a specification and an agent that could implement it.  What it did not settle is **how much to ask for at once**.  The tempting answer is everything: hand over `spec.md`, say "implement this," and see what comes back.

Iteration beats that for one reason.  It shrinks the thing you have to judge, and it gives you something to judge it *against*.  A single increment is checked by a test you already wrote.  A large result has no check at all until you invent one after the fact, which is exactly when you are most inclined to accept what you are looking at.

Andrej Karpathy, who named vibe coding, makes the point (as the *AI-Assisted Development* tutorial records) that people are better at writing specifications than at reviewing arbitrary output, and models are better at producing output than at writing specifications.  Both loops today keep you on the side of that trade you are better at.  They differ in where the check comes from, and that one difference decides everything else about how they run.  The Karpathy loop has a third form worth naming now, because you will meet it in Model 4: when the artifact is a model rather than a program, the check becomes a number instead of a pass or a fail, and Karpathy calls that variant **autoresearch**.  Side by side, the three differ in five places, and every one of them follows from the first row.

| | Karpathy loop | autoresearch | Gauntlet loop |
|---|---|---|---|
| **The check** | A test or command you already have | A metric computed on inputs you hold back | A rubric you write first from the source of truth |
| **The unit** | One increment | One attempt | One candidate, one critique |
| **What decides** | The check passes or it does not | The number beats the best one recorded, or it does not | The rubric's material criteria, all of them |
| **When it stops** | The spec is met, or you restore and rethink | The target is reached, or the budget is spent | No material defect remains, or the preset's round limit is reached |
| **Fits** | Code with a runnable check | Anything whose quality is a measurable number | Prompts, plans, documents, and code without a complete test suite |

## Model 1: A Two-Step Karpathy Loop

The task: `tools/titles.py` in `cs357-work` has a stub `normalize_title(s)` and two failing tests you wrote first, in the spec-first order from *Coding Agents*.  Each increment is one command, one check, and one commit.

**Increment 1.**  Make the first test pass, and nothing else.

```bash
opencode run "Make tools/test_titles.py::test_collapses_whitespace pass.  Edit tools/titles.py only.  Do not add helpers, entry points, or tests."
python -m pytest tools/test_titles.py -q
git commit -am "normalize_title: collapse whitespace"
```

Or ask opencode to do it:

```text
Make tools/test_titles.py::test_collapses_whitespace pass.  Edit tools/titles.py only.
Do not add helpers, entry points, or tests.  Then run python -m pytest
tools/test_titles.py -q and show me the result.  If it passes, commit with the
message "normalize_title: collapse whitespace".  If it does not, stop and tell me.
```

The check reports one pass and one failure.  Commit anyway.  The failing test belongs to the next increment, and a red test you have not asked for yet is not a defect.

**Increment 2.**  Make the second test pass.  This is where the loop earns its keep:

```bash
opencode run "Make tools/test_titles.py::test_slug_form pass.  Before editing, list the files you will change and why, then stop."
```

The agent proposes editing `tools/titles.py` to lowercase and hyphenate, and then proposes adding a `slugify()` helper and a `__main__` block so the tool can run from the shell.  Nobody asked for either.  You reject both at the plan gate, before any file changes:

```text
Only the first sentence of that plan.  Do not add slugify or a __main__ block.
```

The agent changes one line.  The check reports two passing tests.  You commit.

Notice the size of what you had to judge: two one-sentence plans and two test runs.  The agent never got more than one increment ahead of you, and the one time it tried, the plan gate caught it before any code existed.

### Critical Thinking Questions

1.  After Increment 1 the check reported one failure and you committed anyway.  Explain why that commit was correct, and state the rule that tells you when a red test is an unfinished increment rather than a defect.

    *Hint: What did you ask for in Increment 1?  Does the failing test belong to that increment or the next one?*

2.  In Increment 2 the agent proposed a `slugify()` helper and a `__main__` block.  Predict what would have had to happen before you could reject them if there had been no plan gate, and say what that costs compared with the one sentence you typed.

3.  Suppose you had asked for both increments in one prompt.  Name the beat of the loop that disappears, and describe the specific mistake that beat exists to catch.

Which artifact in Model 1 caught the scope creep, and what did catching it there cost?

[(X)] The plan, at the cost of one sentence typed before any file changed
[( )] The test run, because the extra helper would have broken `test_slug_form`
[( )] The commit, because the change could be reverted afterward
[( )] The commit message, because "one line changed" would not have been true

## 2.  The Anatomy of a Loop Prompt

Model 1 worked, and it is worth asking why, because the answer is reusable.  In *Prompt Engineering as Agent Design* you learned an anatomy for a prompt: a role, a goal, the tools, the format, and the guardrails.  That template configures **who the agent is**.  What you need now is a smaller one that configures **one turn of a loop**, and it has six parts.

Here is Increment 2 from Model 1 with those parts labeled.  The brackets are for you, not for the agent; what you send is the same sentences without them.

```text
[Scope]     Make tools/test_titles.py::test_slug_form pass.  Edit tools/titles.py only.
[Truth]     The criterion is spec.md's slug requirement.  Do not edit spec.md or any test.
[Check]     Run python -m pytest tools/test_titles.py -q and quote its output exactly.
[Gate]      Before editing, list the files you will change and why, then stop and wait.
[Stop]      When that one test passes, commit and stop.  The next criterion is a new turn.
[Report]    Say what changed, what the check said, what you committed, and what is next.
```

Each part does one job, and naming them is what lets you carry the shape from one loop to the next.  Every part is filled in differently by a different loop, but one of them decides the rest: change the **Check** and the Gate, the Stopping rule, and the Report all have to change with it, because they are the parts that handle what the check returns.

| Part | What it pins down | Karpathy (Model 1) | Gauntlet (Model 3) | autoresearch (Model 4) |
|---|---|---|---|---|
| **Scope** | The one thing this turn may change | One file, one criterion | The candidate artifact | The scoring function |
| **Source of truth** | What the turn is judged against, named as a file the agent must read and may not edit | `spec.md` | `spec.md` and `rubric.md` | `spec.md`, and the query set it may not see into |
| **Check** | The command or measurement that decides the turn, quoted so its output can be quoted back | `pytest`, which passes or fails | Every criterion in the rubric, scored | `eval/score.py`, which prints one number |
| **Gate** | Where the turn stops and waits | Before editing, on the plan | After the critique, before revising | After the measurement, before keeping |
| **Stopping rule** | What ends the loop, not the turn | The criterion passes | No material defect remains | The target is reached, or the budget is spent |
| **Report** | The four facts the turn comes back with | What changed, what the check said, what was committed, what is next | The scored table, then what was revised and what still fails | The number, whether it was kept, and what to try next |

Read the **Check** row across.  A test answers yes or no, a rubric answers one question per criterion, and a metric answers with a number, but all three name something that existed **before** the turn started and that the agent may not edit.  That is the whole design.  When Model 2 rewrote a failing test to match its own code, it did not break a rule about diligence; it broke the Check part, and every other part of that run was worthless afterward.

Three of the six parts never change between turns, which is why the next section puts them in a file.  **Gate**, **Stopping rule**, and **Report** are properties of the loop, so they belong in `AGENTS.md` and you write them once.  **Scope**, **Source of truth**, and **Check** are properties of this turn, so you retype them each time, and they are short enough that retyping is the cheap part of the loop.

Model 2's opening prompt was "Implement spec.md end to end.  Run the tests.  Commit when they pass.  I'll be back in an hour."  Which parts of the anatomy does it supply?

[( )] Scope and Check, but no Gate, which is why the run went wrong
[(X)] Scope only.  It names what to change, and leaves the source of truth, the gate, the stopping rule, and the report for the agent to decide
[( )] All six, badly worded
[( )] Scope, Check, and Stopping rule, since "commit when they pass" is a stopping rule

---

# Part II: Setting Up the Karpathy Loop

## 3.  The Four Files

The loop is four files and one command repeated.  Two of the files you already have.

| File | What it does for the loop | Where it comes from |
|---|---|---|
| `spec.md` | The source of truth.  Every increment traces to one of its criteria | OpenCode Studio lab, Part 2 |
| `system_prompt.txt` | The prohibitions: what the agent must never touch | OpenCode Studio lab, Part 2 |
| `AGENTS.md` | The loop's rules, so you do not retype them every turn | You write it now |
| `opencode.json` | The permission block, so the tool enforces what the rules only request | You write it now |

**`AGENTS.md`** puts the loop in a file instead of in the chat.  A message you typed twenty turns ago is gone; this survives a restart.

```markdown
# Agent Contract

## The loop
- One increment per run.  An increment is one criterion from spec.md.
- Before editing, list the files you will change and why, then stop and wait.
- After editing, run the check and report its exact output.  Do not summarize it.

## Track your own work in git
- Commit every increment whose check passes.  The message names the criterion.
- When the check fails, restore the working tree and say so.  Never leave a
  failed increment half-applied for the next run to trip over.
- Append one entry to .ai/SESSION.md after every commit or restore.

## Report in plain sentences
- Say what you changed, what the check said, what you committed, and what is next.
- Name the files you changed and the behavior that changed, not line numbers.
- If you could not do something, say which part and why, before anything else.

## Never
- Do not edit spec.md, rubric.md, rubric.json, or system_prompt.txt.
- Do not edit a test to make it pass.
- Do not add helpers, entry points, or dependencies nobody asked for.
```

**`opencode.json`** is the part a rule alone cannot do.  `AGENTS.md` asks the agent not to touch `spec.md`; the permission block makes the tool refuse.  Values are `allow`, `ask`, or `deny`, keys are tool names, patterns use `*` and `?`, and the last matching rule wins.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",
    "bash": {
      "*": "ask",
      "git *": "allow",
      "python -m pytest*": "allow",
      "rm *": "deny"
    }
  }
}
```

Read it from the top.  Ask about everything.  Allow any `git` command and the check, because you will run both dozens of times and approving each one teaches you nothing.  Deny `rm` outright.  Everything else stops and asks, which is the setting you want all term.

Or ask opencode to do it:

```text
Write AGENTS.md at the project root with these rules: one increment per run, list
files before editing and stop, run the check and report its exact output, commit
every increment whose check passes with a message naming the criterion, restore the
working tree when a check fails, and append to .ai/SESSION.md after every commit or
restore.  Add a reporting rule: plain sentences saying what changed, what the check
said, what was committed, and what is next, naming the files changed and the
behavior that changed rather than line numbers.  Forbid editing spec.md, rubric.md,
rubric.json, system_prompt.txt, and any test.  Then write opencode.json with a
permission block that asks by default, allows "git *" and "python -m pytest*" under
bash, and denies "rm *".  Show me both files before you write them.
```

> **Checkpoint.**  Reopen the project after writing `opencode.json`, in the desktop application or by restarting `opencode` in that directory.  opencode reads the config from the folder it is working in, and a session that was already open does not pick up a file that did not exist when it started.

## 4.  Running One Increment

With the four files in place, an increment is one command:

```bash
opencode run "Make <the next check> pass.  Edit <the one file> only.  List the files you will change first, then stop."
```

Or ask opencode to do it: type the same sentence into the message bar.  The `run` subcommand and the message bar reach the same agent with the same contract; the only difference is where the transcript ends up.

Then the check, then the commit or the restore.  The agent can run all three for you, because `git` and `pytest` are already allowed:

```text
Run the check.  If it passes, commit with a message naming the criterion.  If it
fails, restore the working tree and tell me what the failure said.
```

### What the agent should tell you

The contract asked for four facts in plain sentences, and this is the shape it produces.  Four facts, in this order: what changed, what the check said, what was committed, what is next.

```text
Changed tools/titles.py so normalize_title lowercases the result and joins words
with hyphens.  No other file touched.

Check: python -m pytest tools/test_titles.py -q, 2 passed, 0 failed.

Committed as 4a91c2e "normalize_title: lowercase and hyphenate".

Next: test_rejects_empty_title does not exist yet, so the empty-string case has no
check to make pass.  Write that test before the next increment.
```

Read what that report does and does not ask of you.  It names a file and a behavior, so you can tell whether the agent did the thing you asked; it quotes the check verbatim, so "it works" is never the evidence; it names the commit, so you can go look if you want to; and it ends by telling you what the loop is blocked on, which is the sentence that decides the next prompt.  Notice that you can accept or reject this increment without reading a line of the code.  The check is the evidence, the commit is the record, and if the report and the check disagree, believe the check.

The whole run reads back the same way, because the agent committed as it went:

```bash
git log --oneline
```

```text
4a91c2e normalize_title: lowercase and hyphenate
7f30bd1 normalize_title: collapse whitespace
```

One line per increment, each one a criterion that passed its check.  That is the session's progress report, and it cost nothing to produce.

## 5.  Where the Loop's State Lives

Every increment produces two things: a commit, and a sentence about what happened.  The commit lives in `git`.  The sentence lives in the `.ai/` handoff directory from the *Governing Coding Agents* tutorial, which you created in Part 1 of the OpenCode Studio lab.

Of the four files, the loop touches two often and two rarely.  `.ai/SESSION.md` gets an entry after every commit or restore, and `.ai/FUTURE_WORK.md` gets one whenever you reject a plan for scope, as you did in Increment 2; `.ai/CURRENT_TASK.md` changes when you pick the next increment, and `.ai/CONTEXT.md` almost never changes at all.  The *Governing Coding Agents* tutorial carries all four in full.

Every `SESSION.md` entry ends with a **Next Safe Action**, which in the Karpathy loop is simply the next increment.  Here is the entry for Model 1's second increment, so you can see how short it is:

```markdown
## 2026-09-17 increment 2: normalize_title lowercases and hyphenates
- Verified by: python -m pytest tools/test_titles.py -q (2 passed)
- Rejected from plan: slugify() helper and __main__ block (moved to FUTURE_WORK.md)
- Next Safe Action: write test_rejects_empty_title before asking for the empty-string case
```

## Model 2: A Run Handed Everything at Once

Same repository, same `spec.md`, and a prompt with no increment, no gate, and no permission block in front of it.  The line numbers are for the questions.

```text
[1] you>    Implement spec.md end to end. Run the tests. Commit when they pass.
            I'll be back in an hour.
[2] agent>  Plan: edit artifact/search.py, artifact/test_search.py, spec.md (clarify the
            max_results default), requirements.txt (add rapidfuzz for scoring). Proceeding.
[3] agent>  Wrote artifact/search.py (212 lines). Wrote artifact/test_search.py (6 tests).
[4] agent>  pytest: 5 passed, 1 failed (test_missing_kb_exit_3)
[5] agent>  test_missing_kb_exit_3 expected exit 3 but got a traceback. Updated the test to
            expect SystemExit(1), which matches the implementation.
[6] agent>  pytest: 6 passed.
[7] agent>  Updated spec.md: max_results default is now 10 to match the implementation.
[8] agent>  git commit -am "Implement search feature per spec"
            [main 4f1c2e9] 4 files changed, 268 insertions(+), 9 deletions(-)
```

Every line after [1] is the agent doing what it was told.  That is the problem.

### Critical Thinking Questions

4.  Identify the first line at which a gate from Section 3 would have stopped this run, and name the gate.  Then identify the first line at which the run became **irreversible without `git`** and say what you would have to do to recover.

    *Hint: The plan in [2] names four files.  Compare it with the "Never" section of the `AGENTS.md` in Section 3 and with your own `system_prompt.txt`.*

5.  Lines [5] and [7] each change something other than `artifact/search.py`.  For each, say which rule it violates and which level of the source-of-truth hierarchy it silently overrode, and say which of the two is worse.  Then explain why line [6]'s "6 passed" is weaker evidence than Model 1's "2 passed."

    *Hint: One rewrites a check to match the code.  The other rewrites the specification to match the code.  Which one will the next reader believe?*

6.  Write the `permission` block that would have stopped line [7] at the tool rather than at the rule.  Then list the increments you would ask for instead of line [1], in order, one check each.

    *Hint: Your `spec.md` has five testing criteria.  Is one increment per criterion the right grain, or is the first increment smaller than that?*

In Model 2, which single gate, had it existed, would have prevented the most damage?

[( )] A check gate after [3], because the 212-line file was never verified
[(X)] A plan gate after [2], because the plan already named `spec.md` and `requirements.txt`, both forbidden, before any file changed
[( )] A commit gate before [8], because nothing is lost until it is committed
[( )] A test gate at [4], because one failure should have ended the run

> **Common Misconception:** "The agent committed, so the work is safe in `git`."  A commit preserves the state the agent produced, including the rewritten test and the rewritten spec.  `git revert` gets you back, but only if you notice, and the run was designed so that you would not be there to notice.  Reversibility is a property of the loop, not of the tool.

---

# Part III: Setting Up the Gauntlet Loop

## 6.  The Seven Steps

The Karpathy loop assumes a check already exists.  Often it does not: a document, a plan, a prompt, or a spec whose tests nobody has written.  The Gauntlet loop supplies the check by writing it first.  The procedure, in the order you run it:

1.  **Parse the task.**  Write down the objective, every explicit constraint and exclusion, the required output format, the scope, and any instruction that must remain unchanged.  Do not weaken a constraint to make the task easier.
2.  **Clear material fog.**  List every unresolved question that could change the result.  For each, choose the smallest fix: ask a targeted question, inspect the supplied context, run a small reversible experiment, or record an explicit assumption when the decision is low-risk and reversible.  When the fog is the codebase's to clear, plan mode is the cheap fix: opencode's `plan` agent reads and proposes but may not edit.
3.  **Write the rubric.**  Convert the source of truth into criteria with a stable identifier, an unambiguous pass condition, a verification method, and a materiality judgment.  Prefer criteria a program could decide.  Do not invent criteria to make the rubric look thorough.
4.  **Generate Candidate 0.**  The strongest first attempt you can make under the rubric.  Never make it weak on purpose so the loop looks productive later.
5.  **Critique adversarially.**  Attack the candidate against the rubric: failed criteria, unsupported claims, hidden assumptions, contradictions, counterexamples, false claims of verification.  Tie every finding to a criterion and label it material or not.
6.  **Revise.**  Fix every material defect inside the artifact, not as an appended caveat.  Never move a criterion to let a deficient candidate pass.
7.  **Verify and stop.**  Re-score the revised candidate against every criterion, not only the ones you changed.  Stop when the latest critique finds no material defect, or when the preset's round limit is reached.

The presets set the round limit and the depth of the critique: **quick** is at most one round, checking requirements, correctness, and clarity; **standard** is at most three rounds, adding reasoning, assumptions, edge cases, and feasibility; **rigorous** is at most five rounds, adding counterexamples, evidence quality, and independent verification.  A stricter preset is never permission to ignore the requested length, format, or scope.

## 7.  The Rubric, Two Ways

Step 3 is the one that makes the rest work, so write it in a file rather than in your head.  Two forms do the job, and the choice is about what you are checking rather than about rigor.

**Qualitative,** `rubric.md`.  Use it when a criterion needs a judgment that a person makes and a sentence can describe.  Levels, not points.

```markdown
# Rubric: search artifact

Accept when: every material criterion is at Meets.

| ID | Criterion | Meets | Approaching | Does not meet | Material | How to verify |
|----|-----------|-------|-------------|---------------|----------|---------------|
| K1 | Results sorted by score | Scores non-increasing | Sorted except ties | Unsorted | Yes | Query with three known matches |
| K2 | max_results limits the count | `--max-results 2` returns at most 2 | n/a | More than 2 | Yes | Run with the flag |
| K3 | Empty query exits 2 | Exit 2, message on stderr, no traceback | Exit 2, message on stdout | Traceback or another exit code | Yes | `python artifact/search.py " "; echo $?` |
| K4 | Missing knowledge base | Exit 3, message names the path | Exit 3, vague message | Traceback | Yes | Rename the file, run once |
| K5 | No matches | stdout is `[]`, exit 0 | n/a | Anything else | Yes | A nonsense query |
| K6 | Default max_results | Returns 5 with no flag | n/a | Any other count | Yes | Run without the flag |
| K7 | Only the allowed files changed | Only `artifact/search.py` and `artifact/test_search.py` | n/a | Any other file | Yes | `git status --porcelain --untracked-files=all` |
| K8 | No eval, exec, or network | grep finds nothing | n/a | Any hit | Yes | grep the source |
| K9 | A test per testing criterion | Five tests map one-to-one onto criteria 1-5 | Five tests, one criterion doubled | Fewer than five | Yes | Read `artifact/test_search.py` |
| N1 | Docstring style | "Returns" | "Return" | Absent | No | Read the file |
```

**Quantitative,** `rubric.json`.  Use it when the criteria are mechanical, you will score more than one candidate, and you want a number you can compare across rounds.

```json
{
  "threshold": 0.85,
  "criteria": [
    {"id": "K1", "requirement": "results sorted by score descending", "weight": 3, "material": true},
    {"id": "K2", "requirement": "max_results limits the count", "weight": 2, "material": true},
    {"id": "K3", "requirement": "empty query exits 2", "weight": 2, "material": true},
    {"id": "K4", "requirement": "missing knowledge base exits 3", "weight": 3, "material": true},
    {"id": "K5", "requirement": "no matches returns [] and exits 0", "weight": 2, "material": true},
    {"id": "K6", "requirement": "default max_results is 5", "weight": 2, "material": true},
    {"id": "K7", "requirement": "only the allowed files changed", "weight": 3, "material": true},
    {"id": "K8", "requirement": "no eval, exec, or network", "weight": 4, "material": true},
    {"id": "K9", "requirement": "a test per testing criterion", "weight": 2, "material": true},
    {"id": "N1", "requirement": "docstrings say Returns", "weight": 1, "material": false}
  ]
}
```

Two rules keep either form honest.  A non-material criterion may fail without blocking convergence, which is why materiality is recorded per criterion rather than decided by whoever is reading the output.  And the weighted score is a summary, not the stopping rule: a candidate above the threshold with one material criterion failed has not converged.

There is a third form of the same idea, and it is worth naming here so you recognize it when it arrives in Section 9.  An **evaluation metric** is a single number a program computes from the artifact's behavior on inputs the agent may not edit.  The difference is what the check can express: a rubric decides whether each criterion is *met*, which is the right question for a requirement, and a metric decides how *well* one thing is done, which is the right question when two candidates both meet every requirement and one of them is still better.  Model 4 runs a loop against one.

One row of fog belongs beside the rubric.  Your spec says `score` is a float from 0 to 1 and never says how it is computed.  That is fog: two implementations can satisfy every criterion and rank documents differently.  The smallest fix is an explicit, recorded assumption ("any monotone relevance score normalized to [0, 1]; ranking quality is out of scope for this lab"), because the decision is low-risk and reversible.  Write it in `.ai/CONTEXT.md` so it outranks whatever the agent decides on its own.

Or ask opencode to do it:

```text
Read spec.md and system_prompt.txt.  Write rubric.md with one row per testing
criterion and per prohibition: ID, criterion, Meets, Approaching, Does not meet,
Material, and how to verify.  Then write rubric.json with the same IDs, a weight,
and a material flag for each, plus a threshold.  Do not invent criteria that are
not in spec.md or system_prompt.txt.  List anything in spec.md too vague to verify
instead of guessing at it.
```

## Model 3: One Gauntlet Round, From Prompt to Convergence

Use the **standard** preset, so the round limit is three and this is round one.  Every number below comes from the practice kit, so you can reproduce the whole round yourself; the last part of this section says how.

**Step 4, Candidate 0.**  Generate the strongest first attempt:

```bash
opencode run --agent plan "Read spec.md and rubric.md.  Propose an implementation of artifact/search.py.  Do not edit anything."
opencode run "Implement that plan in artifact/search.py and artifact/test_search.py only."
```

What comes back, in the four-fact shape from Section 4:

```text
Wrote artifact/search.py and artifact/test_search.py.  search.py loads the knowledge
base, scores each document by the fraction of query terms it contains, sorts by score,
and prints JSON.

Check: python3 artifact/test_search.py, ran 4 tests, 1 error.
test_missing_kb_exit_3 raised FileNotFoundError instead of returning 3.

Committed as candidate-0.

Next: the missing-knowledge-base case needs handling.
```

Stop on the first line of the check before you go anywhere near the error.  The suite has **four** tests, and `spec.md` lists **five** testing criteria.  The one with no test is criterion 2, that `max_results` limits the number returned, and the agent did not skip it out of laziness; it wrote tests for the behaviors it happened to implement.  A suite the candidate wrote is not the check.  The rubric is.

**Step 5, critique.**  A fresh session is the better critic, because the session that wrote the code is invested in it:

```bash
opencode run "Score artifact/search.py against every criterion in rubric.md.  For each: the ID, the level, material or not, and the evidence you ran.  Do not fix anything."
```

What comes back, one row per criterion, each with the evidence that produced it:

```text
K1  Meets          Queried "agent memory": scores [1.0, 0.5, 0.5, 0.5, 0.5, 0.5], non-increasing.
K2  Meets          --max-results 2 on "agent": two objects.
K3  Meets          Query " ": "[search:main] query must not be empty" on stderr, exit 2.
K4  Does not meet  Renamed kb/knowledge_base.json, ran once: FileNotFoundError traceback,
                   exit 1.  The spec says exit 3 with a message naming the path.  MATERIAL.
K5  Meets          Nonsense query: stdout [], exit 0.
K6  Does not meet  Ran with no flag on a query matching six documents: six came back, so the
                   default is not 5.  argparse says default=10.  MATERIAL.
K7  Meets          Only artifact/search.py and artifact/test_search.py changed.
K8  Meets          grep -nE "eval\(|exec\(|socket|urllib|requests" artifact/search.py: no hits.
                   But line 15 prints {"error": str(e)} to stdout and returns [], so a bad
                   knowledge base puts two JSON documents on stdout.  MATERIAL (K8 area).
K9  Does not meet  Four tests; none for testing criterion 2 (max_results).  The suite also
                   reports FAILED (errors=1) from test_missing_kb_exit_3.  MATERIAL.
N1  Does not meet  Three docstrings begin "Return", none begin "Returns".  Not material.
```

Three material failures and one material risk, and none of them was visible in the agent's own report.  K4 is the one the suite caught and the agent described as a next step.  K9 is the suite itself falling short of the spec: criterion 2 has no test.  K6 is the one **nothing** caught, because no test covered it and the code looked reasonable.  That is the case the rubric exists for.  The line-15 finding passes K8's grep and still breaks the output contract, which is why a critique reads the code around a row and not only the row's command.

**Step 6, revise.**  One message naming every material failure and nothing else:

```bash
opencode run "Address only these material failures: K4, K6, K9, and the str(e) print on line 15.  Do not change spec.md, rubric.md, rubric.json, system_prompt.txt, or any existing test."
```

```text
Caught FileNotFoundError in main and returned 3 with a message naming the path.
Changed the --max-results default from 10 to 5.  Added test_max_results_limit, which
covers spec.md testing criterion 2.  A knowledge base that is not valid JSON now prints a
located message to stderr with a traceback instead of writing str(e) to stdout.

Check: python3 artifact/test_search.py, ran 5 tests, OK.

Committed as candidate-1.
```

**Step 7, verify.**  Re-score everything, not only what you changed, because a revision can break a criterion that passed:

```bash
opencode run "Re-score artifact/search.py against every criterion in rubric.md and report the table again."
```

```text
K1  Meets          Still non-increasing.
K2  Meets          --max-results 2: two objects.
K3  Meets          Empty query: message on stderr, exit 2.
K4  Meets          Renamed the file, ran once: exit 3, stderr
                   "[search:main] knowledge base not found at kb/knowledge_base.json".
K5  Meets          Nonsense query: [], exit 0.
K6  Meets          No flag, six-document query: five results.
K7  Meets          Still only artifact/search.py and artifact/test_search.py.
K8  Meets          grep: no hits, and line 15 no longer writes to stdout.
K9  Meets          Five tests, one per testing criterion; ran 5 tests, OK.
N1  Does not meet  Still "Return".  Not material.
```

Now the stopping decision, which is the step people skip.  The weighted score moved from **16 of 24, or 0.67**, to **23 of 24, or 0.96**, against a threshold of 0.85.  Both conditions are satisfied: the score is above the threshold, and no material criterion is failing.  This is a converged result in round one, with two rounds of budget unspent.

N1 still fails, and it stays failing.  It is non-material, so it does not block convergence, and the correct move is to write it into `.ai/FUTURE_WORK.md`, not to fix it now and not to quietly delete the row so the table looks clean.

**Run the round yourself.**  Two scripts build the state this model walks through, and they need nothing but Python and `git`.  The rubric is not in the kit: use the `rubric.md` from Section 7, which is written against this exact spec.

```bash
bash setup_gauntlet_sample.sh     # builds the practice repo, ends at tag candidate-0
cd gauntlet-sample
python3 artifact/test_search.py   # 4 tests, 1 error: the state Step 4 leaves you in
bash ../apply_reference_fix.sh    # stands in for Step 6, tags candidate-1
python3 artifact/test_search.py   # 5 tests, OK
```

Download them from [setup_gauntlet_sample.sh](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/gauntlet-sample/setup_gauntlet_sample.sh) and [apply_reference_fix.sh](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/gauntlet-sample/apply_reference_fix.sh).  Every criterion above has a command beside it, so you can check the table rather than believe it.

### Critical Thinking Questions

7.  Before you run the critique, predict which criteria Candidate 0 will fail.  Then run it.  Which failures did you not predict, and what does that say about accepting an agent's output without a rubric?

8.  The docstring criterion is labeled non-material.  Write the one condition under which it would become material, and name who gets to set that condition.

9.  Your critique of Candidate 1 finds nothing.  Is that a failed critique or a converged result, and how would you tell the difference?

10.  A teammate proposes editing K6 to read "default is 5 or 10" so that Candidate 0 passes.  Explain, using the source-of-truth hierarchy, why the rubric cannot be changed for that reason, and state the one circumstance in which changing a criterion is legitimate.

11.  Candidate 0's own test suite reported four tests, and `spec.md` lists five testing criteria.  Name the criterion the suite did not cover, and explain why the rubric caught K6 when the suite could not.  Then state the rule this gives you about accepting a passing test suite as evidence that a candidate has converged.

    *Hint: Who wrote the suite, and what were they trying to demonstrate when they wrote it?*

Suppose the Step 7 re-score had come back differently: Candidate 1 clears the weighted threshold, but K4 is still at "Does not meet."  What would the correct call have been?

[( )] Converged, because the weighted score cleared the threshold
[(X)] Not converged, because K4 is material, and clearing the threshold does not override a failed material criterion
[( )] Converged, because one failing criterion out of ten is within tolerance
[( )] Not converged, but only until you lower K4's weight so the score reflects reality

## Code Cell

A rubric a program can score is a rubric you can re-run on every candidate without re-reading the spec.  The cell below loads the quantitative rubric from Section 7, scores a candidate's observed behavior, and applies both stopping rules.  The values shown are Candidate 0 from Model 3, so it prints 0.67 and names K4, K6, and K9; set `K4`, `K6`, and `K9` to `True` and it prints 0.96 and `converged`.  Change them to what your own Candidate 1 does and run it again.

```python
# The candidate is what you observed by running the verification methods.

RUBRIC = {
    "threshold": 0.85,
    "criteria": [
        {"id": "K1", "requirement": "results sorted by score descending", "weight": 3, "material": True},
        {"id": "K2", "requirement": "max_results limits the count",       "weight": 2, "material": True},
        {"id": "K3", "requirement": "empty query exits 2",                "weight": 2, "material": True},
        {"id": "K4", "requirement": "missing knowledge base exits 3",     "weight": 3, "material": True},
        {"id": "K5", "requirement": "no matches returns [] and exits 0",  "weight": 2, "material": True},
        {"id": "K6", "requirement": "default max_results is 5",           "weight": 2, "material": True},
        {"id": "K7", "requirement": "only the allowed files changed",     "weight": 3, "material": True},
        {"id": "K8", "requirement": "no eval, exec, or network",          "weight": 4, "material": True},
        {"id": "K9", "requirement": "a test per testing criterion",       "weight": 2, "material": True},
        {"id": "N1", "requirement": "docstrings say Returns",             "weight": 1, "material": False},
    ],
}

candidate = {
    "K1": True,
    "K2": True,
    "K3": True,
    "K4": False,      # traceback, exit 1
    "K5": True,
    "K6": False,      # default is 10
    "K7": True,
    "K8": True,
    "K9": False,      # four tests, none for criterion 2
    "N1": False,      # says "Return"
}

def score(candidate, rubric):
    earned = total = 0
    material_failed = []
    for c in rubric["criteria"]:
        ok = bool(candidate.get(c["id"], False))
        total += c["weight"]
        earned += c["weight"] if ok else 0
        if not ok and c["material"]:
            material_failed.append(c["id"])
        tag = "meets" if ok else ("DOES NOT MEET" if c["material"] else "does not meet (non-material)")
        print(f"{c['id']}  w={c['weight']}  {tag:<28} {c['requirement']}")
    ratio = earned / total if total else 0.0
    print(f"\nweighted score {earned}/{total} = {ratio:.2f}, threshold {rubric['threshold']}")
    if material_failed:
        print("revise: material criteria failed: " + ", ".join(material_failed))
    elif ratio < rubric["threshold"]:
        print("revise: below threshold on non-material criteria")
    else:
        print("converged")

score(candidate, RUBRIC)
```
@Pyodide.eval

Read the last branch carefully.  A material failure blocks convergence no matter how high the score climbs, and the threshold only decides cases where everything material already passes.  That ordering is the whole reason the rubric records materiality per criterion instead of leaving it to whoever is reading the output.

---

# Part IV: Synthesis and Practice

## 8.  Which Loop, When

Use the Karpathy loop when a runnable check already exists or can be written in a minute, and the work decomposes into increments: implementing a spec with tests, refactoring, fixing a named bug.  Use the Gauntlet loop when the check does not exist yet or is not a program: a document, a plan, a prompt, a specification itself, or code whose tests you do not trust.  Reach for autoresearch in the case neither of those covers, when the work already meets every requirement and the question left is how well it does something: ranking, accuracy, latency, cost.

One question separates them, and it is worth asking before you choose.  Is the thing you want *true or false* about this artifact, or is it a *degree*?  A test and a rubric both answer the first kind, one mechanically and one by judgment.  Only a metric answers the second, and reaching for a rubric when you needed a metric is how criteria like "results are well ranked" end up in a rubric, where nobody can score them the same way twice.

All three nest.  A gauntlet round's revision step is a Karpathy increment with the critique as its plan, a Karpathy loop's first move on an untested feature is a quick gauntlet on the spec, to find the fog before the agent finds it for you, and an autoresearch attempt is a Karpathy increment whose check happens to print a number instead of a verdict.

## 9.  Loops That Run Themselves

Loops that remove you from the gate entirely exist, and this deck is where the course describes them: the agent finishes, a script restarts it, and it keeps going while you sleep.  Each iteration begins with a fresh context window, and the memory lives on disk: the codebase, a running `TODO` file, and the `git` history.

| Pattern | What it is | How it stops | Safety model |
|---|---|---|---|
| **Ralph loop** (Geoffrey Huntley) | A brute-force `while` loop that re-runs the same prompt file, iteration after iteration | A human stops it, or a "task complete" check in the prompt trips | Deliberately minimal: the test suite plus `git revert` |
| **autoresearch** (Karpathy's variant) | The same loop pointed at ML research instead of code | A target validation metric is reached | The metric is the guardrail; a worse score is discarded.  Model 4 runs one |
| **gnhf** ("good night, have fun") | An overnight orchestrator that splits a goal into small steps, each in a fresh context | A step budget, or the goal's acceptance check | Success commits; failure runs `git reset --hard` with backoff; worktrees isolate parallel agents |
| **firstmate** (a "crew") | An agent distro that turns one general agent into a coordinated crew | You end the primary session | One primary session delegates to sub-agents with narrower scope |

Every one of them is the Karpathy loop with the human gate replaced by a deterministic one, and every one of them is only as safe as that gate.  The controls that must exist before you let a loop run itself:

1.  A step budget, so a stuck loop cannot run up a bill.
2.  An acceptance check the loop cannot edit: held-out tests, a metric, or a rubric kept outside the files the agent may touch.  Model 2 line [5] is what happens when the agent can edit the check.
3.  Per-step rollback on a dedicated branch, so a failed iteration leaves nothing behind.
4.  Fresh context each iteration, with the state in `.ai/` and `git` rather than in a conversation.
5.  A human gate before merge.  The loop may commit to its branch all night; it does not merge to `main`.

### Auto mode, and the isolation it requires

A loop that stops to ask permission is not unattended, so these patterns need the permission prompts off.  opencode does that two ways.  The flag is `--auto`:

```bash
opencode --auto
opencode run --auto "Work the next item in TODO.md, run the check, and commit if it passes."
```

The configuration equivalent turns the whole permission block to `allow`:

```json
{
  "permission": {
    "*": "allow"
  }
}
```

Three facts about the flag are worth having exactly right.  An explicit `deny` rule still applies under `--auto`, so a denied `rm *` stays denied.  The desktop application has no flag to pass, so the configuration block is the only route there.  And the block form above is the one the OpenCode Studio lab uses and grades: `permission` takes a map of tool names, with `"*"` as the catch-all, rather than a bare string.

**Do not run this on your own machine.**  An agent acting without prompts acts on the real filesystem, the real network, and the real credentials of whatever host it runs on, and it does so while you are asleep.  The only responsible place for auto mode is a container or a virtual machine you are willing to discard: no credentials you care about, no directories outside the project, and a snapshot to roll back to.

For everything in this course, leave the permission block at `ask`.  You are seeing auto mode so that you recognize it in somebody's setup instructions and know what it turns off, not so that you adopt it this semester.

Why does a Ralph loop start each iteration with a *fresh* context window instead of carrying the full conversation forward?

[( )] To reduce the number of API calls, since a fresh context uses fewer total tokens over the whole run
[( )] Because the model is legally required to discard prior context between runs
[(X)] Because the task's memory lives on disk (codebase, `TODO` file, `git` history), so each iteration can re-read exactly what it needs and avoid the context-overflow failure that plagues one very long session
[( )] Because a fresh context makes the agent more creative by preventing it from repeating earlier ideas

## Model 4: An autoresearch Round, Scored by a Metric

Of the five controls above, the second is the one worth seeing run, because a check the loop cannot edit is easy to agree with and easy to get wrong.  This model makes it concrete on the artifact you already have.

Candidate 1 from Model 3 passes every material criterion in `rubric.md`, so the gauntlet is finished with it.  That does not make it *good*.  Ask it "the basic definition of an agent" and three documents tie at 0.5, so the one that comes back first, "Agents and tools," wins on nothing but the order it happens to sit in the file.  Six of the eight documents contain the word "agent," and the scorer has no way to prefer one of them.  No criterion in the rubric decides that, and none should: the rubric asks whether each requirement is met, and ranking quality is not a requirement at all.  It is a **degree**, and degrees need a number.

This runs on the practice repository, not on your graded lab artifact.

**The setup.**  Two files, written before the loop starts:

- `eval/queries.json`, twelve queries a student might actually type, each labeled with the one document that should rank first.
- `eval/score.py`, which runs each query through `artifact/search.py` as a subprocess, finds the rank of the labeled document, and prints the **mean reciprocal rank**: rank 1 scores 1.0, rank 2 scores 0.5, rank 4 scores 0.25, absent scores 0.

Two rules turn that number into a check rather than a suggestion.  The agent may not edit either file, and the target is written down **before** the first attempt, in `eval/BEST.md`: reach 0.80, with a budget of five attempts.  A target chosen after you see the scores is not a target at all; it is a description.

**The prompt.**  In the six parts from Section 2:

```text
[Scope]     Change only the score() function in artifact/search.py.
[Truth]     spec.md still holds.  Do not edit eval/queries.json or eval/score.py.
[Check]     Run python3 eval/score.py and report the number it prints, exactly.
[Gate]      After the measurement, before keeping anything: tell me the number first.
[Stop]      Stop when the number reaches 0.80, or after five attempts, whichever comes first.
[Report]    Say what you changed, what it scored, whether you kept it, and what you will try next.
```

Or ask opencode to do it: paste that into the message bar without the brackets.

Change the **Check** from a test to a measurement and watch what it drags with it.  "It worked" is no longer available as an answer, so the **Report** has to carry a number.  The **Gate** moves from before the edit to after the measurement, because there is nothing to judge until the number exists.  And the **Stopping rule** grows a second arm, because a metric can always be nudged a little higher and a loop optimizing a number will keep going until something stops it.  That is the claim from Section 2 doing its work: one part changed, and three followed.

**The discard rule.**  This is what the Gate buys you, and it belongs in `AGENTS.md` beside the others:

```markdown
## Keeping an attempt
- After every attempt, run the metric and compare with the best score in eval/BEST.md.
- Better: commit, and append one row to eval/BEST.md.
- Worse or equal: restore the working tree.  Do not commit a regression to try to fix it later.
```

**The execution.**  Four measurements, starting from Candidate 1 as the gauntlet left it:

| Attempt | What changed in `score()` | MRR | Kept? |
|---|---|---|---|
| baseline | Candidate 1 unchanged: fraction of query terms found anywhere in the document | 0.667 | recorded as best |
| 1 | Drop stopwords, so "the", "a", "of", and "how" stop earning credit | **0.785** | kept, better than 0.667 |
| 2 | Match whole words instead of substrings, so a query term must equal a document word | 0.646 | **discarded**, worse than 0.785 |
| 3 | Restore attempt 1, then count a term found in the title twice | **0.826** | kept, target reached |

Attempt 2 is the row that earns the loop.  Whole-word matching is the change any of us would have argued for, because substring matching is obviously sloppy and will match fragments nobody meant.  The metric said 0.646, and three queries say why.  "How is an agent checked for quality" and "serving a model on my own machine" both fall to zero because the corpus says *agents* and *models* where the query says *agent* and *model*, and "perceive plan act" falls to zero because the document reads "An agent perceives, plans, and acts," where whole-word matching sees `perceives,` with the comma attached.  Sloppy substring matching was quietly absorbing every one of those, and in this corpus that is worth more than the fragments it costs.  A discussion would have gone the other way, and it would have been wrong.

The loop stopped at attempt 3 with 0.826, above the 0.80 target, two attempts of budget unspent.  It stopped because the target was reached, not because the agent ran out of ideas.

**Run it yourself**, after the two scripts from Model 3:

```bash
bash setup_autoresearch_eval.sh   # writes eval/, commits nothing
python3 eval/score.py             # 0.667, the baseline
python3 eval/score.py -v          # the rank of every query, which is where the ideas come from
```

Download it from [setup_autoresearch_eval.sh](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/gauntlet-sample/setup_autoresearch_eval.sh).

Two hazards are worth stating plainly before you run one of these.  The first is that the metric has to be held out and unwritable.  If the agent can edit `eval/queries.json`, the fastest path to 0.80 is to delete the queries it gets wrong, and it will find that path.  This is Model 2 line [5] again, where the agent rewrote a failing test to match its code, except that a metric fails more quietly: a rewritten test still has to sit in the suite where somebody may read it, while a deleted query leaves nothing behind but a better number.

And a rising metric is not a rising artifact.  Twelve queries are a sample of the behaviors somebody thought to check, and a loop that keeps seeing them will eventually fit them rather than the thing they stand for.  Two habits keep that honest: fix the target in advance so the loop stops when it is met instead of grinding, and re-score the winner against `rubric.md` before merging, because a change that improves ranking can quietly break a criterion the rubric cares about.  Attempt 3 was re-scored: still 23 of 24, still converged.

### Critical Thinking Questions

12.  Attempt 2 scored 0.646 against a recorded best of 0.785, and the agent restored the working tree.  Rewrite that attempt as a gauntlet round instead: name what the critique would have to find for the same change to be discarded, and say which of the two checks you would trust more if the change also made the code shorter and easier to read.

    *Hint: Could a criterion in `rubric.md`, as written, have caught this at all?*

## 10.  Exercises

1.  *Set up and run the Karpathy loop.*

    - *What to do:* Write the `AGENTS.md` and `opencode.json` from Section 3 into your `cs357-work` repository.  Then implement your `spec.md` in at least three increments, each one a single `opencode run` or message-bar prompt, one check, and one commit or restore.  After each commit, append a `SESSION.md` entry in the shape of Section 5's example.
    - *You've succeeded when:* `git log --oneline` shows one commit per increment with a message naming its criterion, every agent report names what changed, what the check said, and what is next, each `SESSION.md` entry names the verifying command, at least one plan was rejected or narrowed before it ran, and your permission block stopped at least one command you had to approve by hand.

2.  *Write both rubrics and run one gauntlet round.*

    - *What to do:* Write `rubric.md` and `rubric.json` for your own `spec.md`, with at least eight criteria covering every testing criterion and every prohibition in `system_prompt.txt`.  Generate Candidate 0, run the critique, revise, and verify, using the commands in Model 3 or the prompts beside them.  Paste your criteria into the code cell and score both candidates.
    - *You've succeeded when:* Every finding maps to a criterion by ID, the code cell prints a weighted score and a verdict for Candidate 0 and Candidate 1, and you can say in one sentence whether the result converged or which criteria remain.

3.  *Point a metric at your own artifact.*

    - *What to do:* Pick one thing your artifact does by degree rather than by requirement, the way ranking quality is a degree in Model 4.  Write at least ten labeled cases in the shape of `eval/queries.json`, a scorer that prints one number, and a target in `eval/BEST.md` fixed **before** you start.  Then run three attempts using the six-part prompt from Section 2, recording the score of each and whether you kept or restored it.  Finish by writing the `ask` permission block from Section 3 beside the auto-mode configuration from Section 9, and one paragraph on the isolation you would require before letting this loop run unattended.
    - *You've succeeded when:* Your target was written down before the first score, at least one attempt was restored for a worse number, your three rows name what changed rather than only what it scored, you can state what `--auto` does *not* override, and the isolation paragraph names the credentials and directories at risk rather than only saying "use a VM."

---

# Extension: Two Loops You Can Run Yourself (self-paced)

Nothing above assumes this part, and nothing graded does either.  It is here because both loops in this deck are small enough to run end to end on a laptop, and a loop you have run once is a different thing from a loop you have read about.

## A.  The practice kit

Three scripts build the whole thing.  They need Python and `git` and nothing else, and they run in a directory of their own, so they cannot disturb your lab work.

```bash
bash setup_gauntlet_sample.sh      # spec, knowledge base, and Candidate 0, tagged candidate-0
cd gauntlet-sample
bash ../apply_reference_fix.sh     # the refine turn from Model 3, tagged candidate-1
bash ../setup_autoresearch_eval.sh # the held-out metric from Model 4
```

The three files are [setup_gauntlet_sample.sh](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/gauntlet-sample/setup_gauntlet_sample.sh), [apply_reference_fix.sh](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/gauntlet-sample/apply_reference_fix.sh), and [setup_autoresearch_eval.sh](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/gauntlet-sample/setup_autoresearch_eval.sh).  Every number in Model 3 and Model 4 came from running exactly these, so any row you cannot reproduce is a row worth asking about.

## B.  Scripting the gauntlet round

A gauntlet round repeats, so it is worth a script.  This one automates the counting and the stop condition, nothing else:

```bash
#!/usr/bin/env bash
# gauntlet.sh: run the gauntlet until it converges or the round limit is reached.
ROUNDS=${1:-3}
for ((r=1; r<=ROUNDS; r++)); do
  echo "== round $r =="
  opencode run "Score artifact/search.py against every criterion in rubric.md.  End your reply with exactly CONVERGED or REVISE." | tee "round_$r.txt"
  grep -q CONVERGED "round_$r.txt" && { echo "converged in $r round(s)"; exit 0; }
  opencode run "Address only the material failures you just reported.  Change nothing else."
done
echo "round limit reached without convergence"
```

Or run the four prompts from Model 3 in sequence in the message bar and keep the count yourself.  The prompt-only route reaches the same place, with you holding the round number instead of the shell.

## C.  Scoring the metric yourself

The cell below is a standalone version of `eval/score.py` with the corpus inlined, so it runs here rather than on your laptop.  It scores the same twelve queries against the four variants from Model 4's table, and it should print the same four numbers.  Change `stopwords` or `title_weight` and watch what happens.

```python
# The corpus and the twelve labeled queries are the practice kit's.  Each variant is a
# scoring function; the metric is mean reciprocal rank, and higher is better.

DOCS = [
    ("kb/docs/01.md", "Agents and tools", "An agent calls tools to act on the world; tools extend what agents can do."),
    ("kb/docs/02.md", "What is an agent", "An agent perceives, plans, and acts in a loop."),
    ("kb/docs/03.md", "Agent memory", "Agents forget between requests unless memory is written down."),
    ("kb/docs/04.md", "Local models with Ollama", "Ollama serves local models on port 11434."),
    ("kb/docs/05.md", "Prompt patterns", "Personas and few-shot examples shape a model's output."),
    ("kb/docs/06.md", "Agent safety gates", "A gate in the tool path stops an agent before an irreversible action."),
    ("kb/docs/07.md", "Agents and skills", "Skills are instructions an agent loads on demand."),
    ("kb/docs/08.md", "Evaluating agents", "Agents are evaluated against an answer key of checks."),
]

QUERIES = [
    ("agent that remembers earlier requests", "kb/docs/03.md"),
    ("agent that asks permission first", "kb/docs/06.md"),
    ("what port does the local server use", "kb/docs/04.md"),
    ("how is an agent checked for quality", "kb/docs/08.md"),
    ("extra instructions the agent picks up when needed", "kb/docs/07.md"),
    ("how do I stop it before it does something irreversible", "kb/docs/06.md"),
    ("agent that uses outside capabilities", "kb/docs/01.md"),
    ("the basic definition of an agent", "kb/docs/02.md"),
    ("giving the model examples in the prompt", "kb/docs/05.md"),
    ("serving a model on my own machine", "kb/docs/04.md"),
    ("agent scoring against an answer key", "kb/docs/08.md"),
    ("perceive plan act", "kb/docs/02.md"),
]

STOPWORDS = {"a", "an", "the", "of", "do", "does", "is", "it", "i", "my", "on",
             "in", "for", "so", "what", "how", "to", "and", "that", "when", "up"}


def make_scorer(drop_stopwords=False, whole_word=False, title_weight=1):
    """Return a scoring function for one variant from Model 4's table."""
    def score(query, title, body):
        terms = query.lower().split()
        if drop_stopwords:
            terms = [t for t in terms if t not in STOPWORDS]
        if not terms:
            return 0.0
        if whole_word:
            in_title = set(title.lower().split())
            in_body = set(body.lower().split())
        else:
            in_title, in_body = title.lower(), body.lower()
        earned = 0
        for t in terms:
            if t in in_title:
                earned += title_weight
            elif t in in_body:
                earned += 1
        return earned / (title_weight * len(terms))
    return score


def mrr(score):
    """Return the mean reciprocal rank of the labeled document over every query."""
    total = 0.0
    for query, expected in QUERIES:
        ranked = sorted(DOCS, key=lambda d: -score(query, d[1], d[2]))
        hits = [d for d in ranked if score(query, d[1], d[2]) > 0]
        rank = next((i for i, d in enumerate(hits, 1) if d[0] == expected), 0)
        total += 1 / rank if rank else 0.0
    return total / len(QUERIES)


variants = [
    ("baseline: fraction of terms found", make_scorer()),
    ("attempt 1: drop stopwords", make_scorer(drop_stopwords=True)),
    ("attempt 2: whole words only", make_scorer(drop_stopwords=True, whole_word=True)),
    ("attempt 3: stopwords + title counts twice", make_scorer(drop_stopwords=True, title_weight=2)),
]

best = 0.0
for name, score in variants:
    value = mrr(score)
    kept = "kept" if value > best else "discarded"
    if value > best:
        best = value
    print(f"{value:.3f}  {kept:<10} {name}")
print(f"\nbest {best:.3f}, target 0.80")
```
@Pyodide.eval

The `kept` line inside the loop is the discard rule from Model 4, so the cell decides rather than printing four numbers and leaving the judgment to you.  That is the difference between measuring and looping: the loop has a rule about what to do with the measurement, decided before the measurement arrives.

---

## Reflection Prompt

*Personal:* Model 2's prompt is the one most people write the first time an agent works.  Have you written it, in this course or elsewhere?  What did you get back, and which of the four files from Section 3 would you now put in front of it?

*Technical:* In your notebook: the Karpathy loop's check comes from a test that exists, the Gauntlet loop's check comes from a rubric you wrote, and autoresearch's check is a number you agreed to before you started.  Pick one feature of your project and say which of the three you would run first, what its first increment, first criterion, or first measurement would be, and where the fog is.

*Societal:* An unattended loop commits all night against a rubric it cannot edit.  If it ships a defect no criterion encoded, who is accountable: the person who wrote the rubric, the person who started the loop, or the team that merged the branch in the morning?  Argue for one and name the control from Section 9 that was missing.

-> Coming Up Next: Both loops today assumed you could tell a passing criterion from a failing one.  In *Hallucinations and Evaluating Agent Outputs*, we take up the harder case: an output that looks right, cites something, and is wrong, where no criterion you wrote catches it and the judge has to be built by hand.  Bring three prompts where a model gave you a confidently wrong answer; the rubric discipline from Model 3 is what we will apply to them.

---

## Further Reading

- [Tokens, Embeddings, and Attention: How Models Represent Meaning, Part I](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/TokensEmbeddingsAttention)
- This course: [AI-Assisted Development and Vibe Coding](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/VibeCoding), the three supervision levels and the spec-first development this deck builds on.
- This course: [Governing Coding Agents: Charters, Handoffs, and Durable Memory](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentGovernance), the Karpathy rules beside a production charter, and the `.ai/` handoff directory in full.
- This course: [Coding Agents: OpenCode, Spec-First Development, Hooks, and Reading the Log](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-codingagents.md), Section 2c on plan mode and Part IIb on the permission block and plugin hooks.
- This course: [Lab: OpenCode Studio](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/OpenCodeStudio), the `spec.md`, `system_prompt.txt`, and rubric that Model 3 runs against.
- opencode permissions and CLI: https://opencode.ai/docs/permissions/ and https://opencode.ai/docs/cli/, the source for the `permission` block, the pattern rules, and the `--auto` flag.
- Andrej Karpathy, [`llm-wiki.md`](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (gist, April 2026): the pattern behind keeping the agent's memory in files it maintains and you curate.
- The practice kit this deck runs on, three scripts under `files/gauntlet-sample/`: [setup_gauntlet_sample.sh](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/gauntlet-sample/setup_gauntlet_sample.sh) builds the repo, [apply_reference_fix.sh](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/gauntlet-sample/apply_reference_fix.sh) runs the refine turn, and [setup_autoresearch_eval.sh](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/gauntlet-sample/setup_autoresearch_eval.sh) writes the held-out metric.
- Andrej Karpathy.  "[Software 2.0](https://karpathy.medium.com/software-2-0-a64152b37c35)."  *Medium* (2017).
- Geoffrey Huntley.  "everything is a ralph loop." https://ghuntley.com/loop/, the origin and rationale of the fresh-context brute-force loop; see also https://ralph-wiggum.ai/.
- **gnhf** ("good night, have fun"), overnight autonomous orchestrator: https://github.com/kunchenguid/gnhf.
- **firstmate**, an agent distro for running a crew: https://github.com/kunchenguid/firstmate.
