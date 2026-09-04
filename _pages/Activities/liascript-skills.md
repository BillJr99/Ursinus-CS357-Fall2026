<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-skills.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-skills.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Skills: Design One, Then Measure It

On Tuesday you drove opencode against a specification and read the diff it produced.  Today we work on the instructions the agent reads before it produces anything.  A **skill** is a small file of instructions that the agent loads when your request matches the skill's description, and the OpenCode Studio lab asks you to write two of them.  The question this session answers is the one that lab leaves open: after you write a skill, how do you know it changed anything?

We do three things.  First we read a skill and decide when it fires.  Then we design one together, spec-first: job, trigger, instructions, test.  Then we measure it, by running the same task with and without the skill on two local models and scoring every run against a five-item rubric.  The written assignment *Skill Design Study* repeats that experiment at home, so the protocol in Part III is the one you will follow.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board and keeps the team's results table; the Presenter reports out wherever you disagreed or where the numbers surprised you; the Reflector watches for places where the group trusted a number it had not checked.  After class, respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Skill** | A named instruction set the agent loads on demand, scoped to one purpose.  Stored as a directory with a `SKILL.md` inside | The `commit-message` skill the class writes in Part II |
| **`SKILL.md`** | The file that is the skill.  YAML front matter carries `name` and `description`; the body is the instruction text | Model 1, the safety-guardrail skill from the Local Agent lab |
| **Description-as-trigger** | There is no separate trigger field.  The agent reads each skill's `description` against your request and decides whether to load it | "Use when the user asks to delete, remove, overwrite, truncate, or drop anything" fires; "Safety utilities" does not |
| **System prompt** | Standing instructions sent ahead of every turn.  Always on, never invoked by name | The `BASELINE` string in the Part III harness |
| **Project instructions** | A file such as `AGENTS.md` in the project root, read once at startup: architecture, invariants, test commands, what not to touch | The `AGENTS.md` you wrote for `cs357-work` in Week 1 |
| **Hook** | A command the harness runs automatically at a fixed point, such as before a commit or after a file edit.  Enforced by code, so the model cannot talk its way past it | The `commit-msg` hook in Exercise 2 |
| **Golden set** | A fixed list of inputs with known expected outputs, scored automatically, so a change to a prompt or skill gets a number instead of an opinion | The capitals harness from *Prompt Engineering as Agent Design*, reused in Part III |
| **Rubric** | A short list of checkable criteria, each answered pass or fail, so two people scoring the same output get the same score | The five items in Model 2, scored by `score()` in Part III |

---

### Before You Start

**You need:** Ollama running with `llama3.2` pulled, your `cs357-work` repository, and opencode from *Your AI Workbench*.  Part III also uses a second model of a different size; if you did not pull it during *Running Your Own AI*, start this now:

```bash
ollama pull llama3.2:1b
```

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.

| Minutes | What we do |
|---|---|
| 0-15 | Part I, what a skill is and when it fires |
| 15-40 | Part II, design the `commit-message` skill together |
| 40-70 | Part III, run it with and without, on two models, and score it |
| 70-75 | Report out: each team's results table and the one number that surprised them |

---
# Part I: What a Skill Is

In this part you place skills among the other ways of instructing an agent, learn how a skill is stored and found, and read one real skill closely enough to say when it fires and when it does not.

## 1.  Four Ways to Instruct an Agent

The big idea in one sentence: a skill is guidance the agent chooses to follow, loaded only when it decides your request matches.  Think of the ways you can give a colleague standing guidance.  A team handbook everyone always consults is a system prompt.  A note taped to one project folder is a project instructions file.  A checklist handed over whenever they do a code review is a skill.  A turnstile that will not open until the badge scans is a hook.  The analogy stops where the colleague's memory starts: the agent forgets a skill the moment the task ends, and it can decline to follow one.

| Instruction form | Scope | Always active? | Invoked how? | Enforced by |
|---|---|---|---|---|
| System prompt | Every turn of every conversation | Yes | Automatically | The model reading it |
| Project instructions (`AGENTS.md`) | One project, read at startup | Yes | Automatically at launch | The model reading it |
| Skill | One named purpose | No | By name, or by the agent matching its `description` | The model reading it |
| Hook | One fixed point in the loop | Yes, at that point | Automatically, by the harness | Code |

Three of the four rows share the last column.  A system prompt, a project file, and a skill are all text the model reads, and the model can weigh any of them against your latest request and lose.  Only the hook row is code.  That is why the Local Agent lab says: if you need a rule that holds even when the model decides otherwise, the rule belongs in code.  Today's skill states rules; Exercise 2 moves one of them into a hook so you can feel the difference.

## 2.  A Skill Is a Directory

A skill is a directory containing a `SKILL.md` file, discovered from the filesystem.  There is no registry and no install command: opencode walks up from your working directory looking for skills directories, reads each `SKILL.md`, and offers the skill to the model.

```
my-project/
`-- .agents/
    `-- skills/
        |-- safety-check/
        |   `-- SKILL.md          <- the skill IS this directory
        `-- code-review/
            |-- SKILL.md
            `-- checklist.md      <- supporting files live alongside it
```

Use `.agents/skills/`, which both opencode and pi read, so your skills are not welded to one tool.  The front matter is two lines, `name:` and `description:`, and two rules about it cause almost every failure:

1. The directory name must match the `name:` field.  A mismatch means the skill silently never loads.
2. The `description` is the trigger.  The agent reads it against what you typed and decides whether to load the skill, so write it as *when to use this*, in the words a user would actually type.  "Session setup helper" is a topic and never fires.  "Use whenever the user asks to start, resume, continue, or pick up work on this project" is a trigger and does.

Here is what happens when you type `Please review my latest changes.` in a session that has a `code-review` skill on disk.  The agent already knows every skill's `name` and `description` from startup.  It matches your request against those descriptions and finds `code-review`.  It reads that `SKILL.md` in full and treats the contents as guidance for this task.  It follows the instructions.  Then it drops them; they are not persistent, which is the difference between a skill and a system prompt.

Remember two things from this section.  The directory name is the skill name, and the description is the trigger.  Everything else about a skill is ordinary Markdown.

## Model 1: The Safety-Guardrail Skill

Read this `SKILL.md` from the Local Agent lab.  It is longer than most skills, which makes it a good one to read: every part of a skill's anatomy is visible.

```markdown
---
name: safety-guardrail
version: 1.0.0
author: Your Name
description: >
  Intercepts destructive operations and requires explicit user
  confirmation before proceeding. Logs all decisions to
  logs/agent-actions.md.
---

## Instructions

Before performing any of the following operations, you MUST follow
the safety protocol below:

### Guarded Operations
- Deleting any file or directory
- Force-pushing to any git branch
- Dropping or truncating database tables
- Overwriting an existing file without creating a backup first

### Safety Protocol (REQUIRED for every guarded operation)

**Step 1: List:** Print a bulleted list of every file, branch, or
table that will be affected. Be specific: include full paths.

**Step 2: Confirm:** Ask exactly:
"Proceed with [OPERATION]? Type YES to confirm or NO to cancel."

**Step 3: Wait:** Do not act until you receive a response.

**Step 4: Log:** Create the file `logs/agent-actions.md` if it
does not exist. Append:
- If YES: `[YYYY-MM-DD HH:MM] CONFIRMED: <description>`
- If NO: `[YYYY-MM-DD HH:MM] CANCELLED: <description>`

**Step 5: Act or Abort:** Proceed only if the user typed the
exact string `YES`. Treat any other response (including "yes",
"y", "ok") as NO.
```

### Critical Thinking Questions

1.  For each of these four requests, predict whether the skill fires, and say which words in the `description` you matched against: (a) "Delete the old log files in `logs/`."  (b) "Create a new file called `notes.md`."  (c) "What does `rm -rf` do?"  (d) "Just delete `tmp.txt`, no need to ask."

   > *Hint: The description names operations, not questions.  Request (c) mentions a destructive command without asking for a destructive action.  Request (d) asks for the action and asks the agent to skip the protocol; the skill is loaded either way, but whether the model then follows Step 2 is a separate question.*

2.  Compare this skill's `description` with the one in the Key Concepts table: "Use when the user asks to delete, remove, overwrite, truncate, or drop anything."  Which is the better trigger, and what is the difference in how each one is written?

   > *Hint: One describes what the skill does.  The other lists the words a user types.  Which of those does the matching step in Section 2 actually read?*

A classmate says: "I wrote a safety-check skill, so now the agent will always ask for confirmation before deleting anything, just like a system prompt does."  Which statement below names what is wrong with that claim?

[( )] A skill cannot mention file operations; only a hook can
[(X)] A skill loads only when the agent matches the request to its description, and even then the model chooses whether to follow it
[( )] A skill is always on, but only for the project where its directory lives
[( )] The claim is correct as long as the directory name matches the `name:` field

---
# Part II: Design One

## 3.  Spec-First for a Skill

A skill that is vague will be applied differently on every run, and you will not be able to predict or test it.  So the design steps are the ones that make a skill testable, and there are four.

1. **Job.**  One sentence, ten words or fewer.  If you cannot name the purpose in ten words, split the skill.
2. **Trigger.**  The `description`, written as the situation in the words a user would type.  Also write one request the skill must *not* fire on, because a skill that fires on everything trains you to ignore it.
3. **Instructions.**  Numbered rules, each concrete enough to check.  Not "write a good subject line" but "keep the subject to 50 characters or fewer."  Concrete constraints can be tested; abstract ones cannot.
4. **Test.**  One pass-or-fail check per rule, plus the negative-trigger request from step 2.

Steps 1 and 2 are where most of the ambiguity lives, and the fastest way to clear it is to let the agent ask.  A skill in the grill-me / interview-me style does exactly that: before it builds anything, it asks you numbered multiple-choice questions, each with a recommended default, and it records your answers as part of the spec.  Three menued questions ("Which files may this skill touch?  (a) only `src/`, recommended; (b) `src/` and `tests/`; (c) anywhere") cost less than one wrong guess, and the answers become the constraints that step 3's rules enforce and step 4's tests check.  The OpenCode Studio lab's kickoff skill is this pattern, so the `commit-message` skill below is a good place to practice it: decide now which two questions it should ask before it writes a subject line.

The body of a skill has a recognizable shape, and this security-review skill from the design-first session shows it: a role sentence, a numbered list of checks, and an exact output format.

```markdown
# Security Review Skill

You are performing a security review of the diff provided. Check for each of the following
OWASP top-10 risks for LLM-integrated applications:

1. **Prompt Injection**: does any user-supplied string reach a model prompt without sanitization?
2. **Insecure Output Handling**: does any model output reach `eval()`, `exec()`, or a shell?
3. **Excessive Agency**: does the agent take destructive actions (delete, overwrite) without confirmation?
4. **Sensitive Data Exposure**: are API keys, tokens, or PII logged or returned to the user?
5. **Unbounded Resource Consumption**: are there loops or queries with no upper bound?

For each risk, state: FOUND / NOT FOUND / CANNOT DETERMINE, with a one-line explanation.
If any risk is FOUND, suggest the minimal fix.

Review the most recent diff provided by the user.
```

## Model 2: The `commit-message` Skill

The job today is one every coding agent does many times a day: write the commit message for a diff.  Work through the four steps with the class, then compare to the version below.

**Job:** write a git commit message from a diff.

**Trigger:** fires on "commit this", "write a commit message", "summarize the staged changes".  Must not fire on "what does `git rebase` do?", which is a question about git, not a request for a message.

**Instructions and test** are in the file and the rubric that follow.  Create it at `.agents/skills/commit-message/SKILL.md`; the directory name must match `name:`.

```markdown
---
name: commit-message
description: Use when the user asks to commit, write a commit message, describe the staged changes, or summarize a diff for git.
---

You are writing the commit message for the diff the user provides.

## Rules
1. The first line is the subject.  Start it with one of: Add, Fix, Remove, Update, Rename, Refactor, Guard.
2. Keep the subject to 50 characters or fewer, with no period at the end.
3. Leave one blank line after the subject.
4. In the body, name every file the diff changes and say why the change was made, not what the code does.
5. Reply with the commit message only: no code fence, no greeting, no commentary.
```

The test is a five-item rubric.  Each item is one check a program can make on the reply, and each maps back to a rule.

| # | Rubric item | Checks rule | How the check works |
|---|---|---|---|
| 1 | Subject is 50 characters or fewer | 2 | `len(subject) <= 50` |
| 2 | Subject starts with a listed verb | 1 | first word is in the verb list |
| 3 | Subject has no trailing period | 2 | `not subject.endswith(".")` |
| 4 | A blank line follows the subject | 3 | second line is empty |
| 5 | Body names every changed file | 4 | each filename from the diff appears in the body |

Install it and confirm the trigger before you measure anything: create `.agents/skills/commit-message/`, save the file above inside it as `SKILL.md`, and start opencode.  Then type "Write a commit message for my staged changes" and watch the skill load.  Then type "What does git rebase do?" and confirm it does not.

### Critical Thinking Questions

4.  Rule 4 has two halves: name every file, and say why rather than what.  Only the first half has a rubric item.  Why was the second half left out of the rubric, and what would you need to score it?

   > *Hint: "Names `search_memory.py`" is a string check.  "Explains why" is a judgment.  The *LLM-as-Judge* session later in the term is about scoring judgments; today's rubric sticks to what a string check can decide.*

5.  Predict, before Part III runs anything: which rubric item will `llama3.2` fail most often *without* the skill?  Which will it still fail *with* the skill?  Write both predictions down; you will check them against the table.

   > *Hint: Without instructions, models tend to open with a greeting or a code fence and to write long subjects.  With instructions, the check most often missed is the one that requires counting.*

---
# Part III: Measure It

In this part you find out whether the skill did anything.  The method is the golden-set harness from *Prompt Engineering as Agent Design*: hold everything fixed, change one thing, and score.  The one thing that changes is whether the skill's instructions are present.

## 4.  The Protocol

A measurement is only as good as what it holds still.  Here is everything the harness pins, and the *Skill Design Study* assignment asks you to record every row of this table for your own skill.

| What | Fixed value | Why it is fixed |
|---|---|---|
| Models | `llama3.2` and `llama3.2:1b` | Two sizes, so a result that holds on one and not the other is visible |
| Temperature | `0.0` | Pins the wording, so runs are repeatable (*Running Your Own AI*, Section 3c) |
| Seed | `42` | Pins the random draw itself |
| Task prompt | `TASK`, the same diff every run | The diff is the input; it does not change between conditions |
| Condition "without" | `BASELINE` as the system prompt | The control |
| Condition "with" | `BASELINE` plus the skill body as the system prompt | The one change |
| Runs per cell | `RUNS = 3` | Shows whether a score is a property of the skill or of one run |
| Score | Five-item rubric, 0 to 5 per run | The same items for every cell |

One honest note about the "with" condition.  When a skill fires inside opencode, the agent reads the `SKILL.md` body into its context.  The harness hands that body over directly as part of the system prompt, so it measures the instructions on their own, separately from the trigger.  You tested the trigger at the end of Part II by watching it load and not load; the harness tests the rest.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.  Before you run it, write down the score you expect in each of the four cells.

```python
import requests

# temperature=0.0 pins the wording (Running Your Own AI, Section 3c).
# seed=42 pins the random draw itself: any fixed number works, the same one
# every run means the same dice rolls every run. Together they make this
# harness repeatable, which is what lets a test tell you something.
def chat(system, user, temperature=0.0, seed=42, model="llama3.2"):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": temperature, "seed": seed},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[promptengineering:eval] {e}")
        import traceback; traceback.print_exc()
        return ""

# The task: one small diff, identical in every run.  Two files change.
DIFF = """diff --git a/search_memory.py b/search_memory.py
--- a/search_memory.py
+++ b/search_memory.py
@@ -12,7 +12,9 @@ def search_memory(query, k=3):
-    results = col.query(query_texts=[query], n_results=k)
+    if not query.strip():
+        return []
+    results = col.query(query_texts=[query], n_results=min(k, col.count()))
     return results["documents"][0]
diff --git a/tests/test_search_memory.py b/tests/test_search_memory.py
--- a/tests/test_search_memory.py
+++ b/tests/test_search_memory.py
@@ -20,3 +20,6 @@ def test_returns_k_results():
     assert len(search_memory("lab 3 due date")) == 3
+
+def test_empty_query_returns_nothing():
+    assert search_memory("   ") == []
"""
FILES = ["search_memory.py", "tests/test_search_memory.py"]
TASK = "Write the commit message for this diff.\n\n" + DIFF

# The control: a system prompt with no skill in it.
BASELINE = "You are a helpful coding assistant."

# The skill body, exactly as it appears below the front matter in SKILL.md.
SKILL = """You are writing the commit message for the diff the user provides.

## Rules
1. The first line is the subject.  Start it with one of: Add, Fix, Remove, Update, Rename, Refactor, Guard.
2. Keep the subject to 50 characters or fewer, with no period at the end.
3. Leave one blank line after the subject.
4. In the body, name every file the diff changes and say why the change was made, not what the code does.
5. Reply with the commit message only: no code fence, no greeting, no commentary.
"""

# The five-item rubric.  One string check per item, pass or fail.
VERBS = ("Add", "Fix", "Remove", "Update", "Rename", "Refactor", "Guard")

def score(msg):
    lines = msg.strip().splitlines() or [""]
    subject = lines[0].strip()
    body = "\n".join(lines[1:])
    return [
        ("1 subject <= 50 chars",        len(subject) <= 50),
        ("2 subject starts with verb",   subject.split(" ")[0] in VERBS),
        ("3 no trailing period",         not subject.endswith(".")),
        ("4 blank line after subject",   len(lines) > 1 and lines[1].strip() == ""),
        ("5 body names every file",      all(f in body for f in FILES)),
    ]

MODELS = ["llama3.2", "llama3.2:1b"]
RUNS = 3
CONDITIONS = {"without": BASELINE, "with": BASELINE + "\n\n" + SKILL}

for model in MODELS:
    for label, system in CONDITIONS.items():
        totals = []
        for run in range(RUNS):
            msg = chat(system, TASK, model=model)
            checks = score(msg)
            passed = sum(ok for _, ok in checks)
            totals.append(passed)
            failed = [name for name, ok in checks if not ok]
            print(f"{model:12} {label:8} run {run + 1}: {passed}/5  failed: {failed}")
        print(f"{model:12} {label:8} mean = {sum(totals) / RUNS:.2f}\n")
```

## Model 3: The Results Table

The Recorder fills this in from the printed output.  This is also the table the *Skill Design Study* assignment asks for, with your own skill, your own rubric, and the number of runs it specifies.

| Model | Condition | Run 1 | Run 2 | Run 3 | Mean (of 5) | Items that failed |
|---|---|---|---|---|---|---|
| `llama3.2` | without | | | | | |
| `llama3.2` | with | | | | | |
| `llama3.2:1b` | without | | | | | |
| `llama3.2:1b` | with | | | | | |

Two derived numbers matter more than any single cell.  The **skill effect** for a model is the "with" mean minus the "without" mean.  The **spread** within a cell is the largest run score minus the smallest.  Report both.

### Critical Thinking Questions

6.  Before reading your numbers, check the predictions from Question 5.  Then look at the spread.  At temperature 0 and a fixed seed, the three runs in a cell are supposed to agree.  Did they?  If any cell has a spread of 1 or more, what does that say about the phrase "deterministic" as a promise the system makes you?

   > *Hint: Temperature 0 buys a great deal of repeatability, not a guarantee.  Whatever the spread turns out to be, it is the noise floor for everything else in the table.*

7.  Suppose `llama3.2` scores a mean of 3.00 without the skill and 4.00 with it.  That is a difference of one rubric item.  Under what condition is that difference evidence that the skill worked, and under what condition is it noise?

   > *Hint: Compare the difference between cells to the spread within a cell.  A one-item gap between conditions means little when one condition's own three runs already differ by one.  Which rubric item moved also matters: a skill that says "no trailing period" and fixes only that item did exactly one thing.*

8.  Why two models?  Write one sentence that would be true if the skill effect were large on `llama3.2` and zero on `llama3.2:1b`, and a different sentence for the reverse.  Then say what you can conclude about the *skill* from either.

   > *Hint: A skill is guidance the model chooses to follow, and a smaller model follows a numbered list less reliably.  A result on one model is a fact about that pair.  Two models let you say whether the effect belongs to the skill or to the model.*

9.  Your rubric has five items and your diff changes two files.  If you edited the skill until every cell scored 5.00 on this diff, what could happen on a different diff?  Name the risk and the guard.

   > *Hint: This is the same risk as tuning a prompt to five countries in the capitals harness.  A second diff you never tuned on is a held-out case.*

---
# Part IV: Synthesis and Practice

## 5.  Exercises

1.  **A held-out diff.**

   *What to do:* Write a second diff that changes three files, and rerun the Part III cell with it as `DIFF` and the three filenames as `FILES`.  Fill in a second results table.

   *Starter hint:* Do not edit the skill between the two diffs.  The question is whether the ranking of the four cells holds on input the skill was not tuned on.

   *You've succeeded when:* You can state in one sentence whether the skill effect on each model survived the new diff, with the two tables as evidence.

2.  **Move one rule into code.**

   *What to do:* Put rubric item 1 into a git `commit-msg` hook so that a subject line longer than 50 characters is rejected no matter who wrote it.  Save this as `.git/hooks/commit-msg` and make it executable with `chmod +x`.  Then ask opencode to commit with a deliberately long subject and capture what happens.

   *Starter hint:*
   ```bash
   #!/bin/sh
   subject=$(head -n 1 "$1")
   [ ${#subject} -le 50 ] || { echo "commit-msg: subject is over 50 characters" >&2; exit 1; }
   ```

   *You've succeeded when:* Your transcript shows the commit refused by the hook, and you can say in one sentence what the skill could not guarantee that the hook does.

3.  **Measure your own lab skill.**

   *What to do:* Your `kickoff-interview` skill from OpenCode Studio has five testable conditions (at most five questions, in groups of three or fewer, lettered options with a default, no file touched first, task read back).  Turn them into a five-item rubric, write a `score()` for the reply text, and run the Part III protocol on it with your own kickoff request as `TASK`.

   *Starter hint:* Some of the five are string checks (count the numbered questions, look for "[default:").  One of them, "touch no file," is not visible in reply text at all.  Say which item you could not score and where that check would have to live.

   *You've succeeded when:* You have a filled results table for your own skill and one item honestly marked "not measurable from the reply."

---

## Reflection Prompt

Respond to all three levels in your notebook:

**Personal:** Before today, how did you decide whether an instruction you gave an agent had worked?  Name one instruction you have been repeating to a model this semester that you never measured.  Would a five-item rubric for it be easy or hard to write, and what does that difficulty tell you about the instruction?

**Technical:** The harness measured the skill's instructions by pasting them into the system prompt, and you tested the trigger separately by watching opencode load the skill or not.  What could go wrong in the real system that neither test would catch?  Design a third test that closes that gap, and estimate what it would cost to run.

**Societal:** Skills are shared: the lab has you post one for classmates to install, and community bundles like Superpowers are cloned into thousands of projects.  A skill is a directory anyone can read before running, yet most people will not.  Who is responsible when an installed skill causes an agent to do something its user did not intend: the author, the installer, or the harness that offered to load it?  Argue for one and name what that party would have to do differently.

---

-> Coming Up Next: You now have a harness that scores one instruction change across two models.  Next session, *Prompt Engineering as Agent Design: System Prompts, Personas, and Comparing Models*, turns that harness on the system prompt itself: what each of its five elements does to the output, how a persona changes the distribution of answers rather than the facts, and how to compare two models on the same prompt without fooling yourself.  Bring today's results table; the comparison method is the one you just used.

---

## Further Reading

- OpenCode documentation. https://opencode.ai/docs/, the skills and permissions sections cover where skills are discovered and how `permission.skill` controls what loads.
- Superpowers, a community skill bundle for agent CLIs: https://github.com/obra/superpowers.  Read a few of its `SKILL.md` files as further models of description-as-trigger.
- Anthropic.  "Building Effective Agents." https://www.anthropic.com/research/building-effective-agents, the evaluator-optimizer pattern is today's measurement loop in general form.
- On evaluation: this course's *Evaluating Agent Outputs*, *Benchmarking*, and *Testing Agents* activities extend today's five-item rubric into larger golden-test, benchmark, and property-based harnesses.
