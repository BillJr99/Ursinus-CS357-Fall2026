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

On Sep 8, in *Coding Agents: OpenCode, Spec-First Development, and Reading the Diff*, you wrote a specification before any code existed, read the agent's plan before it acted, and read a diff that passed every test and was still dangerous.  Today we put those three skills inside a loop.  Two loops, in fact: the **Karpathy loop**, which keeps the agent on a short leash and moves in small verified steps, and the **Gauntlet loop**, which builds an answer key first and then attacks each candidate until no material defect remains.  You leave with a checklist for the first, a worksheet for the second, and one gauntlet round run on the `spec.md` you brought from the OpenCode Studio lab.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Read each model as a team, then answer the Critical Thinking Questions on your own before discussing.  The Recorder posts the team's answers to the Class Activity Questions discussion board; the Presenter reports out wherever you disagreed.  After class, complete the Reflection Prompt in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Karpathy loop** | Ask for one small change, run the check, read the diff, commit or revert, repeat.  The agent never gets more than one verifiable step ahead of you | Model 1: two increments to `normalize_title`, each one a commit |
| **Leash** | How far the agent may go before it must stop and show you something.  A short leash stops at the plan and again at the diff | Model 2: a leash long enough to let the agent edit `spec.md` and commit unsupervised |
| **Gate** | A point where the loop cannot continue until a human or a deterministic check says so | The plan gate, the diff gate, and the commit gate in Model 1 |
| **Handoff directory** | The `.ai/` files (`CONTEXT.md`, `CURRENT_TASK.md`, `SESSION.md`, and the rest) that hold the loop's state between turns and between agents | Section 3: where the Karpathy loop writes down what it just did |
| **Gauntlet loop** | Parse the task, clear the fog, build an answer key, generate Candidate 0, critique it adversarially, revise, verify, and stop when no material defect remains | Model 3: one round against your `spec.md` |
| **Source of truth** | The authoritative basis the work is judged against: your requirements, your spec, your approved decisions, then evidence, then the agent's own criteria, in that order | `spec.md` and `system_prompt.txt` outrank anything the agent decides on its own |
| **Fog** | An unresolved decision, dependency, ambiguity, or missing fact that could materially change the work.  Fog is cleared, never disguised as a settled assumption | "Score is a float from 0 to 1": scored how? |
| **Acceptance answer key** | A short list of pass/fail checks that operationalizes the source of truth.  Each check says what must be true and how to verify it | Section 4's table, K1 through K9 |
| **Material defect** | A flaw that could change correctness, usefulness, compliance, interpretation, feasibility, safety, or a user's decision.  Style preferences usually are not | Default `max_results` of 10 when the spec says 5 |
| **Converged result** | A candidate for which the latest critique finds no material defect that warrants revision | The stopping condition of every gauntlet preset |

### Before You Start

**You need:** your `cs357-work` repository with the `spec.md`, `AGENTS.md`, and `system_prompt.txt` from the OpenCode Studio lab, plus opencode and Ollama from *Your AI Workbench*.  Model 3 uses your `spec.md` directly, and if you already have `diff_1.patch` from Part 4 of that lab, bring it up on screen.  Check with:

```bash
git -C ~/cs357-work status
```

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.

| Minutes | What we do |
|---|---|
| 0-15 | Part I: why iteration beats one big prompt, and Model 1's two-step loop |
| 15-35 | Part II: the Karpathy rules as a checklist, the `.ai/` directory, and Model 2's broken run |
| 35-60 | Part III: the answer key, one gauntlet round on your `spec.md`, and the code cell |
| 60-70 | Part IV: which loop when, and the loops that run themselves |
| 70-75 | Report-out.  Exercises and the reflection are take-home |

---

# Part I: Two Loops, One Habit

## 1.  Why Iteration Beats One Big Prompt

The Sep 8 session left you with a specification, an agent that could implement it, and the discipline of reading the plan before the diff.  What it did not settle is **how much to ask for at once**.  The tempting answer is everything: hand over `spec.md`, say "implement this," and read the result.  The Sep 8 planted-bug diff already showed why that fails.  A large diff hides `eval(query)` in plain sight because you skim what looks like boilerplate, and a large plan is wrong in ways you cannot see until the code exists.

Iteration fixes both problems by shrinking the thing you have to judge.  A diff of five lines against a test you wrote is checkable in a minute.  A plan for one increment is one sentence, and rejecting it costs seconds.  Andrej Karpathy, who named vibe coding, makes the point (as the *AI-Assisted Development* tutorial records) that people are better at writing specs than at reviewing arbitrary code, and models are better at writing code than at writing specs.  The loop is what keeps you doing the job you are better at.

The two loops today share one habit and differ in where the check comes from.

| | Karpathy loop | Gauntlet loop |
|---|---|---|
| **The check** | A test or command you already have | An answer key you build first from the source of truth |
| **The unit** | One increment, one diff | One candidate, one critique |
| **Who judges** | You, at the plan gate and the diff gate | A critic (you, a fresh session, or a deterministic check) attacking the candidate |
| **When it stops** | The spec is met, or you revert and rethink | No material defect remains, or the preset's round limit is reached |
| **Fits** | Code with a runnable check | Prompts, plans, documents, and code without a complete test suite |

## Model 1: A Two-Step Karpathy Loop

The task: `tools/titles.py` in `cs357-work` has a stub `normalize_title(s)` and two failing tests you wrote first, in the spec-first order from Sep 8.  Each step below starts with the plan-first prompt from that session, quoted here so you can paste it:

```text
Before you change anything: list the files you intend to modify, in the order you
will touch them, with one sentence each on why. Then stop and wait. Do not edit.
```

The transcript is annotated in brackets.  Read the annotations as the five beats of the loop: plan, one change, check, diff, commit.

```text
[Increment 1]
you>    (plan-first prompt) Task: make tools/test_titles.py::test_collapses_whitespace pass.
agent>  Plan: edit tools/titles.py only; replace the NotImplementedError stub with a body
        that collapses runs of whitespace to single spaces and trims the ends.  Waiting.
                                                        [PLAN GATE: one file, one reason. Approve.]
you>    Approved. Make only that change.
agent>  Edited tools/titles.py.
you>    $ python -m pytest tools/test_titles.py -q
        .F                                                       [CHECK: 1 passed, 1 failed]
        FAILED tools/test_titles.py::test_slug_form
you>    $ git diff                                               [DIFF GATE: read every line]
```

```diff
--- a/tools/titles.py
+++ b/tools/titles.py
@@ -1,2 +1,3 @@
 def normalize_title(s):
-    raise NotImplementedError
+    """Collapse runs of whitespace in a title to single spaces and trim the ends."""
+    return " ".join(s.split())
```

```text
you>    $ git commit -am "normalize_title: collapse whitespace"  [COMMIT: the failing test is
                                                                   the next increment, not a bug]

[Increment 2]
you>    (plan-first prompt) Task: make tools/test_titles.py::test_slug_form pass.
agent>  Plan: edit tools/titles.py; lowercase the result and replace spaces with hyphens.
        Also add a slugify() helper and a __main__ block so the tool can run from the shell.
                                                        [PLAN GATE: two extra things nobody asked for]
you>    No. Only the first sentence of that plan. Do not add slugify or a __main__ block.
agent>  Understood. Edited tools/titles.py: one line changed.
you>    $ python -m pytest tools/test_titles.py -q
        ..                                                       [CHECK: 2 passed]
you>    $ git diff                                               [DIFF GATE: one line, as promised]
you>    $ git commit -am "normalize_title: lowercase and hyphenate"
```

Notice the size of everything you had to judge: two one-sentence plans, one three-line diff, one one-line diff, two test runs.  The agent never got more than one increment ahead of you, and the one time it tried, the plan gate caught it before any code existed.

### Critical Thinking Questions

1.  After Increment 1 the check reported one failure and you committed anyway.  Explain why that commit was correct, and state the rule that tells you when a red test is an unfinished increment rather than a defect.

    *Hint: What did you ask for in Increment 1?  Does the failing test belong to that increment or the next one?*

2.  In Increment 2 the agent's plan included a `slugify()` helper and a `__main__` block.  Predict what the diff would have contained if you had approved the plan as written, and estimate how long that diff would take to review compared with the one-line diff you got.

3.  Suppose you had asked for both increments in one prompt.  Name the beat of the loop that disappears, and describe the specific mistake that beat exists to catch.

Which artifact in Model 1 caught the scope creep, and what did catching it there cost?

[(X)] The plan, at the cost of one sentence typed before any file changed
[( )] The diff, at the cost of reverting the extra helper after the fact
[( )] The test run, because the extra helper would have broken `test_slug_form`
[( )] The commit message, because "one line changed" would not have been true

---

# Part II: The Karpathy Loop

## 2.  The Rules as a Checklist

The *Governing Coding Agents* tutorial records a community template, the "Karpathy `CLAUDE.md`," distilled from Karpathy's public talks and posts about working with coding agents.  Its four rules describe what the agent must do.  Turned around, they are a checklist for what you must do at each beat of the loop.

| Rule | What it demands of the agent | Your checklist item at the matching gate |
|---|---|---|
| **Think before coding** | State assumptions, surface multiple interpretations, push back when the request seems wrong, stop when confused | Plan gate: does the plan name the files, the order, and one reason each?  Did it ask about anything you left vague? |
| **Simplicity first** | The minimum code that solves the problem; nothing speculative | Diff gate: is every added line traceable to the one increment you asked for? |
| **Surgical changes** | Touch only what needs to change | Diff gate: `git diff --name-only` lists only the files the plan named |
| **Goal-driven execution** | Verifiable success criteria, tests-first | Check: the increment was defined by a check that existed before the change, and the check ran |

The tutorial's observation is that the failure modes of capable agents are eagerness failures: acting before understanding, changing more than asked, declaring victory without verification.  Add the three habits that keep the loop yours, and the checklist is complete:

1.  Keep the context small.  One increment per prompt; start a fresh session when the conversation grows past what you can summarize in a sentence.
2.  Keep the instructions in files, not in the chat.  `AGENTS.md`, `system_prompt.txt`, and the `.ai/` directory survive a restart; a message you typed twenty turns ago does not.
3.  Never let the loop run without a gate.  A run that goes plan, edit, check, commit with no stop is not a short leash with fast turns.  It is Model 2.

## 3.  Where the Loop's State Lives

Every increment produces two things: a commit, and a sentence about what happened.  The commit lives in `git`.  The sentence lives in the `.ai/` handoff directory from the *Governing Coding Agents* tutorial, and you already created it in Part 1 of the OpenCode Studio lab.

| File | The question it answers | When the Karpathy loop writes it |
|---|---|---|
| `.ai/CONTEXT.md` | "What is this project, in one sentence, and what do I read first?" | Almost never |
| `.ai/CURRENT_TASK.md` | "What exactly is in flight: milestone, subtask, completion criteria, safe handoff point, next immediate action?" | When you pick the next increment |
| `.ai/SESSION.md` | "What just happened, what was verified, and what is the Next Safe Action?" | After every commit or revert |
| `.ai/KNOWN_ISSUES.md` | "What verified defects and constraints should I not rediscover?" | When a check exposes something you are deferring |
| `.ai/FUTURE_WORK.md` | "Which good ideas are deliberately deferred so they stop competing with the milestone?" | When you reject a plan for scope, as in Increment 2 |
| `.ai/AGENT_HANDOFF_KICKOFF.md` | "If I am a brand-new agent taking over right now, what is my first move?" | Never; it is a template |

Two disciplines from the tutorial make the directory trustworthy inside a loop.  Every `SESSION.md` entry ends with a **Next Safe Action**, which in the Karpathy loop is simply the next increment.  And `CURRENT_TASK.md` carries a Reality Check table where every "done" row cites the command that proved it, which is exactly the check you ran at the diff gate.  The handoff rule then applies to every stop, planned or not: *"Before stopping for any reason (user interruption, session exhaustion, context exhaustion, quota exhaustion, or completion of the current task) update the handoff state: `.ai/SESSION.md`, `.ai/CURRENT_TASK.md`, and any affected document under `docs/`."*

Here is the `SESSION.md` entry for Model 1's second increment, so you can see how short it is:

```markdown
## 2026-09-17 increment 2: normalize_title lowercases and hyphenates
- Verified by: python -m pytest tools/test_titles.py -q (2 passed)
- Rejected from plan: slugify() helper and __main__ block (moved to FUTURE_WORK.md)
- Next Safe Action: write test_rejects_empty_title before asking for the empty-string case
```

## Model 2: A Run Where the Leash Was Too Long

Same repository, same `spec.md` from the OpenCode Studio lab, and a prompt that hands over everything at once.  The line numbers are for the questions.

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

4.  Identify the first line at which a gate from Section 2 would have stopped this run, and name the gate.  Then identify the first line at which the run became **irreversible without `git`** and say what you would have to do to recover.

    *Hint: The plan in [2] names four files.  Compare it with the "Files the agent must NOT touch" section of your own `spec.md` and the allowed-files list in `system_prompt.txt`.*

5.  Lines [5] and [7] each change something other than `artifact/search.py`.  For each, say which Karpathy rule it violates and which level of the source-of-truth hierarchy it silently overrode.  Which of the two is worse, and why?

    *Hint: One rewrites a check to match the code.  The other rewrites the specification to match the code.  Which one will the next reader believe?*

6.  Line [6] reports six passing tests.  Explain why "6 passed" is weaker evidence here than "2 passed" was in Model 1, and name the Sep 8 misconception it reproduces.

7.  Rewrite line [1] as the first prompt of a Karpathy loop for this spec.  Then list the increments you would ask for, in order, one check each.

    *Hint: Your `spec.md` has five testing criteria.  Is one increment per criterion the right grain, or is the first increment smaller than that?*

In Model 2, which single gate, had it existed, would have prevented the most damage?

[( )] A diff gate after [3], because you would have seen the 212-line file
[(X)] A plan gate after [2], because the plan already named `spec.md` and `requirements.txt`, both forbidden, before any file changed
[( )] A commit gate before [8], because nothing is lost until it is committed
[( )] A test gate at [4], because two failures should have ended the run

> **Common Misconception:** "The agent committed, so the work is safe in `git`."  A commit preserves the state the agent produced, including the rewritten test and the rewritten spec.  `git revert` gets you back, but only if you notice, and the run was designed so that you would not be there to notice.  Reversibility is a property of the loop, not of the tool.

---

# Part III: The Gauntlet Loop

## 4.  The Acceptance Answer Key

The Karpathy loop assumes a check already exists.  Often it does not: a document, a plan, a prompt, or a spec whose test suite the agent has not written yet.  The Gauntlet loop supplies the check by building it first.  The procedure, in the order you run it:

1.  **Parse the task.**  Write down the objective, every explicit constraint and exclusion, the required output format, the scope, and any instruction that must remain unchanged.  Do not weaken a constraint to make the task easier.
2.  **Clear material fog.**  List every unresolved question that could change the result.  For each, choose the smallest fix: ask a targeted question, inspect the supplied context, run a small reversible experiment, or record an explicit assumption when the decision is low-risk and reversible.  Do not interview yourself about routine work.  When the fog is the user's to clear, ask the way the grill-me / interview-me style of skill asks: a short numbered list of multiple-choice questions, each with a recommended default, so the answer costs one keystroke and lands in the spec.  When the fog is the codebase's to clear, plan mode is the cheap fix: Claude Code's plan mode and opencode's plan agent let the agent read and propose before it may edit, so you read the plan against the task before any diff exists (Section 2c of the *Coding Agents* deck).
3.  **Build the acceptance answer key.**  Convert the source of truth into checks with a stable identifier, an unambiguous pass condition, a verification method, and the evidence to keep.  Prefer checks a program could decide.  Weight correctness and compliance above polish, and do not invent checks to make the key look thorough.
4.  **Generate Candidate 0.**  The strongest first attempt you can make under the answer key.  Never make it weak on purpose so the loop looks productive later.
5.  **Critique adversarially.**  Attack the candidate: failed or omitted checks, unsupported claims, hidden assumptions, contradictions, counterexamples, infeasible steps, unnecessary complexity, false claims of verification.  Classify each finding as material or not and tie material ones to a check.
6.  **Revise.**  Fix every material defect inside the artifact, not as an appended caveat.  Never move a check to let a deficient candidate pass.
7.  **Verify and stop.**  Re-check the final candidate against the original request, every constraint, the source of truth, and every check.  Stop when the latest critique finds no material defect, or when the preset's round limit is reached.

The presets set the round limit and the depth of the critique: **quick** is at most one round, checking requirements, correctness, and clarity; **standard** is at most three rounds, adding reasoning, assumptions, edge cases, and feasibility, with an explicit final verification pass; **rigorous** is at most five rounds, adding counterexamples, evidence quality, and independent verification.  A stricter preset is never permission to ignore the requested length, format, or scope.

Here is the answer key for the OpenCode Studio search spec, built from its testing criteria, its Inputs table, and the prohibitions in `system_prompt.txt`.  Yours will differ in detail and should not differ in shape.

| ID | Requirement (where it comes from) | Pass condition | Verification method | Evidence to keep |
|---|---|---|---|---|
| K1 | Results sorted by score descending (criterion 1) | Scores in the output list are non-increasing | Run a query with three known matches | Captured stdout |
| K2 | `max_results` limits the count (criterion 2) | `--max-results 2` returns at most 2 objects | Run with the flag | Captured stdout |
| K3 | Empty query exits 2 (criterion 3) | Exit code 2, message on stderr, no traceback | `python artifact/search.py "   "; echo $?` | Shell output |
| K4 | Missing knowledge base exits 3 (criterion 4) | Exit code 3, message names the expected path | Rename the file, run once | Shell output |
| K5 | No matches returns `[]` and exits 0 (criterion 5) | stdout is `[]`, exit code 0 | Run a nonsense query | Shell output |
| K6 | Default `max_results` is 5 (Inputs table) | A knowledge base with six matches returns five objects with no flag | Run without the flag | Captured stdout |
| K7 | Only the two allowed files changed (spec, system prompt) | `git diff --name-only` lists nothing else | `git diff --name-only` | The listing |
| K8 | No `eval()`, `exec()`, or network (system prompt) | The search finds nothing | `grep -nE "eval\(|exec\(|import (requests|urllib|socket)" artifact/search.py` | grep output |
| K9 | A test per criterion (system prompt, Required) | Five test names map one-to-one onto criteria 1-5 | Read `artifact/test_search.py` | The mapping |

One row of fog belongs above this table.  The spec says `score` is a float from 0 to 1 and never says how it is computed.  That is fog: two implementations can both satisfy K1 through K9 and rank documents differently.  The smallest fix is an explicit, recorded assumption ("any monotone relevance score normalized to [0, 1]; ranking quality is out of scope for this lab"), because the decision is low-risk and reversible.  Write it in `.ai/CONTEXT.md` so it outranks whatever the agent decides on its own.

## Model 3: One Gauntlet Round on Your `spec.md`

Candidate 0 is `diff_1.patch`, the agent's first implementation from Part 4 of the lab, or the one the person next to you has if yours is not ready.  Run the round on the worksheet below.  The filled rows are from a run against the sample spec; the blank rows are yours.  Use the **standard** preset, so the round limit is three, and this is round one.

**Checks.**  Copy the answer key, then add or remove rows for your spec.  Every row must name a command or an inspection, not a feeling.

| ID | Pass condition | Verification method | Result on Candidate 0 |
|---|---|---|---|
| K6 | Default `max_results` is 5 | Run without the flag | Fail: six objects returned |
| K4 | Exit 3, message names the path | Rename the file, run | Fail: traceback, exit 1 |
| K9 | Five tests map to five criteria | Read the test file | Fail: no test for criterion 2 |
| K7 | Only allowed files changed | `git diff --name-only` | Pass |
| K8 | No eval, exec, or network | grep | Pass |

**Critique findings.**  Attack the candidate.  Every finding gets a material/non-material label and, if material, the check it breaks.

| Finding | Material? | Check | Why |
|---|---|---|---|
| Default is 10, spec says 5 | Yes | K6 | Changes the output a user sees |
| Missing file raises a traceback | Yes | K4 | Wrong exit code; violates the spec's "no traceback" |
| No `test_max_results_limit` | Yes | K9 | A required test is omitted |
| Docstrings say "Return" rather than "Returns" | No | none | Style; the user did not prioritize it |
| Handler prints `str(e)` to stdout | Yes | K8 area | Leaks internal detail into the JSON output stream |

**Revision.**  One message that addresses every material finding by name and nothing else.  This is the `followup_prompt.txt` shape from Part 5 of the lab, and it is the Karpathy loop's leash applied to the gauntlet's findings: precise, bounded, and closed with the files that must not change.

**Verification.**  Re-run every check whose finding you revised, plus K7 and K8 unconditionally, because a revision can break a check that passed.

| Check | Re-run how | Result on Candidate 1 | Evidence |
|---|---|---|---|
| K6 | Run without the flag | | |
| K4 | Rename the file, run | | |
| K9 | Read the test file | | |
| K7 | `git diff --name-only` | | |
| K8 | grep | | |

If Candidate 1 passes every material check, the result has converged and you stop, with two rounds of budget unspent.  If not, round two starts from the failing rows, not from a fresh read of the whole diff.

### Critical Thinking Questions

8.  Before you run the checks, predict which of K1 through K9 Candidate 0 fails.  Then run them.  Which failures did you not predict, and what does that say about reading a diff without an answer key?

9.  The "Return" versus "Returns" docstring finding is labeled non-material.  Write the one condition under which it would become material, and name who gets to set that condition.

10.  Your critique of Candidate 1 finds nothing.  Is that a failed critique or a converged result, and how would you tell the difference?

11.  A teammate proposes editing K6 to read "default is 5 or 10" so that Candidate 0 passes.  Explain, using the source-of-truth hierarchy, why the answer key cannot be changed for that reason, and state the one circumstance in which changing a check is legitimate.

Which of these is a material defect in Candidate 0?

[( )] Variable named `kb` where `knowledge_base` would read better
[( )] Tests listed in a different order from the spec's criteria
[(X)] A missing knowledge base produces a traceback and exit code 1 instead of exit code 3 with a message
[( )] The JSON output uses two-space indentation

## Code Cell

An answer key that a program can score is an answer key you can re-run on every candidate without re-reading the spec.  The cell below encodes seven checks from Section 4 as boolean functions of a candidate's observed behavior and scores Candidate 0.  Change the `candidate` values to what Candidate 1 does and run it again.

```python
# Each check: (id, requirement, material, test). The test is a function of the
# observations you gathered by running the verification method, not of the code.

candidate = {
    "default_max_results": 10,
    "missing_kb_exit_code": 1,
    "empty_query_exit_code": 2,
    "no_match_output": "[]",
    "files_changed": ["artifact/search.py", "artifact/test_search.py"],
    "uses_eval_or_exec": False,
    "test_names": ["test_sorted_desc", "test_empty_query_exit_2",
                   "test_missing_kb_exit_3", "test_no_matches_empty"],
}

ALLOWED = {"artifact/search.py", "artifact/test_search.py"}

ANSWER_KEY = [
    ("K3", "empty query exits 2", True, lambda c: c["empty_query_exit_code"] == 2),
    ("K4", "missing knowledge base exits 3", True, lambda c: c["missing_kb_exit_code"] == 3),
    ("K5", "no matches prints [] and exits 0", True, lambda c: c["no_match_output"] == "[]"),
    ("K6", "default max_results is 5", True, lambda c: c["default_max_results"] == 5),
    ("K7", "only allowed files changed", True, lambda c: set(c["files_changed"]) <= ALLOWED),
    ("K8", "no eval() or exec()", True, lambda c: not c["uses_eval_or_exec"]),
    ("K9", "a test exists for max_results", True, lambda c: "test_max_results_limit" in c["test_names"]),
    ("N1", "docstrings say Returns", False, lambda c: False),   # style: fails, but not material
]

def score(candidate, key):
    passed, failed, material_failed = 0, 0, 0
    for check_id, requirement, material, test in key:
        ok = bool(test(candidate))
        passed += ok
        failed += not ok
        material_failed += (not ok) and material
        tag = "PASS" if ok else ("FAIL" if material else "fail (non-material)")
        print(f"{check_id}  {tag:<22} {requirement}")
    print(f"\n{passed} passed, {failed} failed, {material_failed} material")
    print("converged" if material_failed == 0 else "revise: material defects remain")

score(candidate, ANSWER_KEY)
```
@Pyodide.eval

The last line is the stopping rule.  A non-material failure does not block convergence, which is why the key records materiality per check instead of leaving it to whoever is reading the output.

---

# Part IV: Synthesis and Practice

## 5.  Which Loop, When

Use the Karpathy loop when a runnable check already exists or can be written in a minute, and the work decomposes into increments: implementing a spec with tests, refactoring, fixing a named bug.  Use the Gauntlet loop when the check does not exist yet or is not a program: a document, a plan, a prompt, a specification itself, or a piece of code whose tests you do not trust.  The two nest.  A gauntlet round's revision step is a Karpathy increment with the critique as its plan, and a Karpathy loop's first move on an untested feature is to run a quick gauntlet on the spec to find the fog before the agent finds it for you.

## 6.  Loops That Run Themselves

Loops that remove you from the gate entirely exist, and this deck is where the course describes them: the agent finishes, a script restarts it, and it keeps going while you sleep.  Each iteration begins with a fresh context window, and the memory lives on disk: the codebase, a running `TODO` file, and the `git` history.  The four patterns, and the one column that matters when nobody is watching:

| Pattern | What it is | How it stops | Safety model |
|---|---|---|---|
| **Ralph loop** (Geoffrey Huntley) | A brute-force `while` loop that re-runs the same prompt file, iteration after iteration | A human stops it, or a "task complete" check in the prompt trips | Deliberately minimal: the test suite plus `git revert` |
| **autoresearch** (Karpathy's variant) | The same loop pointed at ML research instead of code | A target validation metric is reached | The metric is the guardrail; a worse score is discarded |
| **gnhf** ("good night, have fun") | An overnight orchestrator that splits a goal into small steps, each in a fresh context | A step budget, or the goal's acceptance check | Success commits; failure runs `git reset --hard` with backoff; worktrees isolate parallel agents |
| **firstmate** (a "crew") | An agent distro that turns one general agent into a coordinated crew | You end the primary session | One primary session delegates to sub-agents with narrower scope |

Read those safety models against today's two loops.  Every one of them is the Karpathy loop with the human gate replaced by a deterministic one, and every one of them is only as safe as that gate.  The controls that must exist before you let a loop run itself:

1.  A step budget, so a stuck loop cannot run up a bill.
2.  An acceptance check the loop cannot edit: held-out tests, a metric, or an answer key kept outside the files the agent may touch.  Model 2 line [5] is what happens when the agent can edit the check.
3.  Per-step rollback on a dedicated branch, so a failed iteration leaves nothing behind.
4.  Fresh context each iteration, with the state in `.ai/` and `git` rather than in a conversation.
5.  A human gate before merge.  The loop may commit to its branch all night; it does not merge to `main`.

Why does a Ralph loop start each iteration with a *fresh* context window instead of carrying the full conversation forward?

[( )] To reduce the number of API calls, since a fresh context uses fewer total tokens over the whole run
[( )] Because the model is legally required to discard prior context between runs
[(X)] Because the task's memory lives on disk (codebase, `TODO` file, `git` history), so each iteration can re-read exactly what it needs and avoid the context-overflow failure that plagues one very long session
[( )] Because a fresh context makes the agent more creative by preventing it from repeating earlier ideas

## 7.  Exercises

1.  *Run the Karpathy loop on your own spec.*

    - *What to do:* Starting from the stub in `artifact/search.py`, implement your `spec.md` in at least three increments.  Each increment is one plan-first prompt, one check, one diff read, and one commit or revert.  After each commit, append a `SESSION.md` entry in the shape of Section 3's example.
    - *You've succeeded when:* `git log --oneline` shows one commit per increment, each `SESSION.md` entry names the verifying command, and at least one plan was rejected or narrowed before it ran.

2.  *Build your answer key and run one gauntlet round.*

    - *What to do:* Write the answer key for your `spec.md` with at least eight checks, each with a verification method you can run.  Score `diff_1.patch` as Candidate 0, fill in the Model 3 worksheet, write the revision as your `followup_prompt.txt`, and verify Candidate 1.
    - *You've succeeded when:* Every material finding maps to a check, every re-run check has evidence, and you can say in one sentence whether the result converged or which rows remain.

3.  *Put Model 2 on a leash.*

    - *What to do:* Rewrite Model 2's line [1] as a sequence of prompts and gates.  Mark each gate as plan, diff, or commit, and beside lines [2], [5], and [7] write the gate that would have stopped that line.
    - *You've succeeded when:* No prompt in your sequence asks for more than one check's worth of work, and `spec.md` is not in any plan.

---

## Reflection Prompt

*Personal:* Model 2's prompt is the one most people write the first time an agent works.  Have you written it, in this course or elsewhere?  What did you get back, and which gate from Section 2 would you now put in front of it?

*Technical:* In your notebook: the Karpathy loop's check comes from a test that exists; the Gauntlet loop's check comes from an answer key you built.  Pick one feature of your project and say which loop you would run first, what its first increment or first check would be, and where the fog is.

*Societal:* An unattended loop commits all night against a test suite it cannot edit.  If it ships a defect that no test encoded, who is accountable: the person who wrote the tests, the person who started the loop, or the team that merged the branch in the morning?  Argue for one and name the control from Section 6 that was missing.

-> Coming Up Next: Both loops today assumed you could tell a passing check from a failing one.  Next session, *Hallucinations and Evaluating Agent Outputs* (Tue Sep 22), is about the harder case: an output that looks right, cites something, and is wrong, where no test you wrote catches it and the critic has to be built by hand.  Bring three prompts where a model gave you a confidently wrong answer; the answer-key discipline from Model 3 is what we will apply to them.

---

## Further Reading

- This course: [AI-Assisted Development and Vibe Coding](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/VibeCoding), the three supervision levels, spec-first development, and the planted-bug diff this deck builds on.
- This course: [Governing Coding Agents: Charters, Handoffs, and Durable Memory](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentGovernance), the Karpathy rules beside a production charter, and the `.ai/` handoff directory in full.
- This course: [Coding Agents: OpenCode, Spec-First Development, Hooks, and Reading the Diff](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-codingagents.md), Section 2b on the plan and Section 2c on plan mode; the loops that run themselves.
- This course: [Lab: OpenCode Studio](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/OpenCodeStudio), the `spec.md`, `system_prompt.txt`, critique document, and refine turn that Model 3 runs against.
- Andrej Karpathy, [`llm-wiki.md`](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (gist, April 2026): the pattern behind keeping the agent's memory in files it maintains and you curate.
- Andrej Karpathy.  "Software 2.0."  *Medium* (2017).
- Geoffrey Huntley.  "everything is a ralph loop." https://ghuntley.com/loop/, the origin and rationale of the fresh-context brute-force loop; see also https://ralph-wiggum.ai/.
- **gnhf** ("good night, have fun"), overnight autonomous orchestrator: https://github.com/kunchenguid/gnhf.
- **firstmate**, an agent distro for running a crew: https://github.com/kunchenguid/firstmate.
