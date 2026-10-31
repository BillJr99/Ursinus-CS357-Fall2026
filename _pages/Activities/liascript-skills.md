<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-skills.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-skills.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Skills: Design One, Then Measure It

In *Coding Agents: OpenCode, Spec-First Development, Hooks, and Reading the Log*, you drove opencode against a specification and read the action log it produced.  Today we work on the instructions the agent reads before it produces anything.  A **skill** is a small file of instructions that the agent loads when your request matches the skill's description, and the OpenCode Studio lab asks you to write two of them.  The question this session answers is the one that lab leaves open: after you write a skill, how do you know it changed anything?

We do three things.  First we read a skill and decide when it fires.  Then we design one together, spec-first: job, trigger, instructions, test.  Then we measure it, by running the same task with and without the skill on two local models and scoring every run against a six-item rubric.  The written assignment *Skill Design Study* then has you write, run, and refine a skill of your own at home, one change at a time.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board and keeps the team's results table; the Presenter reports out wherever you disagreed or where the numbers surprised you; the Reflector watches for places where the group trusted a number it had not checked.  After class, respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Skill** | A named instruction set the agent loads on demand, scoped to one purpose.  Stored as a directory with a `SKILL.md` inside | The `system-prompt-author` skill the class writes in Part II |
| **`SKILL.md`** | The file that is the skill.  YAML front matter carries `name` and `description`; the body is the instruction text | Model 1, the safety-guardrail skill below |
| **Description-as-trigger** | There is no separate trigger field.  The agent reads each skill's `description` against your request and decides whether to load it | "Use when the user asks to delete, remove, overwrite, truncate, or drop anything" fires; "Safety utilities" does not |
| **System prompt** | Standing instructions sent ahead of every turn.  Always on, never invoked by name | The `BASELINE` string in the Part III harness |
| **Project instructions** | A file such as `AGENTS.md` in the project root, read once at startup: architecture, invariants, test commands, what not to touch | The `AGENTS.md` you wrote for `cs357-work` in Week 1 |
| **Hook** | A command the harness runs automatically at a fixed point, such as before a commit or after a file edit.  Enforced by code, so the model cannot talk its way past it | The `SessionStart` and `Stop` hooks in Model 1b |
| **Golden set** | A fixed list of inputs with known expected outputs, scored automatically, so a change to a prompt or skill gets a number instead of an opinion | The harness in Part III, which *Prompt Engineering as Agent Design* reuses next session on world capitals |
| **Rubric** | A short list of checkable criteria, each answered pass or fail, so two people scoring the same output get the same score | The six items in Model 2, scored by `score()` in Part III |

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
| 0-20 | Part I, what a skill is, when it fires, and what a hook can enforce about it |
| 20-42 | Part II, design the `system-prompt-author` skill together |
| 42-70 | Part III, run it with and without, on two models, and score it |
| 70-75 | Report out: each team's results table and the one number that surprised them |

---
# Part I: What a Skill Is

In this part you place skills among the other ways of instructing an agent, learn how a skill is stored and found, read one real skill closely enough to say when it fires and when it does not, and see what a hook can and cannot enforce about the skill's promises.

## 1.  Four Ways to Instruct an Agent

The big idea in one sentence: a skill is guidance the agent chooses to follow, loaded only when it decides your request matches.  Think of the ways you can give a colleague standing guidance.  A team handbook everyone always consults is a system prompt.  A note taped to one project folder is a project instructions file.  A checklist handed over whenever they do a code review is a skill.  A turnstile that will not open until the badge scans is a hook.  The analogy stops where the colleague's memory starts: the agent forgets a skill the moment the task ends, and it can decline to follow one.

| Instruction form | Scope | Always active? | Invoked how? | Enforced by |
|---|---|---|---|---|
| System prompt | Every turn of every conversation | Yes | Automatically | The model reading it |
| Project instructions (`AGENTS.md`) | One project, read at startup | Yes | Automatically at launch | The model reading it |
| Skill | One named purpose | No | By name, or by the agent matching its `description` | The model reading it |
| Hook | One fixed point in the loop | Yes, at that point | Automatically, by the harness | Code |

Three of the four rows share the last column.  A system prompt, a project file, and a skill are all text the model reads, and the model can weigh any of them against your latest request and lose.  Only the hook row is code.  That is why the Local Agent lab says: if you need a rule that holds even when the model decides otherwise, the rule belongs in code.  Today's skill states rules; Section 2c moves one of them into a hook so you can feel the difference, and Exercise 2 has you do it yourself on the commit rule.

Those three rows share a delivery route as well.  A system prompt, a project file, and a skill all reach the model as text placed in its context window, and so does memory, which is a file the program reads and pastes in.  What differs is timing: the first two go in at the start of every call, while a skill goes in only after the agent decides to load it.  Until then, the window holds just its one-line description.

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

**Where opencode looks.**  The discovery paths are fixed, and knowing all of them prevents the most common failure, which is a skill sitting in a directory that nothing reads.  opencode walks up from your working directory to the root of the git worktree, checking each project path on the way, and it also checks the global paths in your home directory.  Each of these holds one directory per skill, with that skill's `SKILL.md` inside.

| Scope | Paths opencode reads |
|---|---|
| Project, walking up to the worktree root | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` |
| Global, for every project | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` |
| Project, on Windows | `.opencode\skills\`, `.claude\skills\`, `.agents\skills\` |
| Global, on Windows | `%USERPROFILE%\.config\opencode\skills\`, `%USERPROFILE%\.claude\skills\`, `%USERPROFILE%\.agents\skills\` |

Three project paths exist because three tools arrived at the same idea separately.  `.claude/skills/` is Claude Code's, `.opencode/skills/` is opencode's own, and `.agents/skills/` is the universal one, read by both tools, which is why this deck uses it.  A skill under a project path is available in that project alone and travels with the repository; a skill under a global path follows you into every project on that machine and travels nowhere else.  opencode's global path is `~/.config/opencode/skills/`, beside the `opencode.json` you already keep there.  **Everything today uses the project path**, because a skill belongs with the project whose conventions it encodes, and because a broken one is then scoped to that project rather than following you into all of them.  Moving a skill to the global path later changes the directory and nothing in the file.  A `SKILL.md` anywhere else is not a skill.  It is a Markdown file, and no agent will ever mention it.

**What the front matter may contain.**  Five keys are recognized and no others: `name` and `description`, both required, plus the optional `license`, `compatibility`, and `metadata`, which holds a map of strings.  Anything else you write there is ignored rather than rejected, so an invented key fails silently and looks exactly like success.  The one that catches people is `allowed-tools`, which is a real field in Claude Code and dead text here: carry a skill over unchanged and that line sits in the file looking like a restriction while opencode never reads it.  Tool limits live in the `permission` block, not in front matter.

Here is what happens when you type `Please review my latest changes.` in a session that has a `code-review` skill on disk.  The agent already knows every skill's `name` and `description` from startup.  It matches your request against those descriptions and finds `code-review`.  It reads that `SKILL.md` in full and treats the contents as guidance for this task.  It follows the instructions.  Then it drops them; they are not persistent, which is the difference between a skill and a system prompt.

Remember two things from this section.  The directory name is the skill name, and the description is the trigger.  Everything else about a skill is ordinary Markdown.

## 2b.  The Same Instructions, Three Ways In

A skill body is just text that reaches the model.  There are three routes it can take to get there, and you have already used two of them this term without calling them that.  Take the `system-prompt-author` body from Part II and picture it arriving each way.

**Route 1, opencode: the filesystem.**  Save the file at `.agents/skills/system-prompt-author/SKILL.md`.  There is no install step; being in a discovery path *is* the installation.

**Route 2, OpenWebUI: a custom Model.**  In the interface you stood up in *Running Your Own AI*, go to **Workspace &rarr; Models &rarr; + Create a model**, name it, pick `llama3.2:latest` as the base model, and paste the skill body, everything below the front matter, into the **System Prompt** field.  Under **Advanced Params** set temperature and seed if you want it repeatable.  Save, and it appears in the chat model selector beside the raw model.  This is the same move the *Local Agent* lab's Direction 0 uses to build a persona agent.

**Route 3, Python: a string.**  The system prompt is a parameter, so the skill body is a variable:

```python
SYSTEM = BASELINE + "\n\n" + SKILL      # the "with" condition in Part III
```

The same call through OpenWebUI's OpenAI-compatible endpoint changes only the URL, the header, and where the reply is nested:

```python
r = requests.post("http://localhost:3000/api/chat/completions",
                  headers={"Authorization": f"Bearer {os.environ['OPENWEBUI_API_KEY']}"},
                  json={"model": "llama3.2", "messages": messages,
                        "options": {"temperature": 0, "seed": 42}})
reply = r.json()["choices"][0]["message"]   # OpenWebUI nests under choices[0]
```

Now the question: same instructions, same model, three routes.  What is actually different?

Only Route 1 has a **trigger**.  In opencode the `description` decides whether the body is loaded at all, so the instructions are absent from every request that does not match.  In Routes 2 and 3 the body is pasted into the system prompt, which means it is present on *every* turn whether or not it is relevant.  **Routes 2 and 3 do not install a skill; they turn a skill into a system prompt.**  Look back at the table in Section 1: you have moved the instructions from the "Skill" row into the "System prompt" row, and given up the "No" in the always-active column.

Hold onto that, because it is what Part III does on purpose.  The harness pastes the body into the system prompt, so it measures the *instructions* with the trigger taken out of the picture.  You test the trigger separately, by watching the skill load and not load at the end of Part II.  Two tests, two different things.

> **Watch out:** a skill body written for Route 1 often says "when the user asks you to write a system prompt."  Pasted into a Route 2 system prompt, that sentence becomes standing instruction on a model that will also be asked about unrelated things, and a small model may start drafting an agent persona in reply to a question about the weather.  An instruction that assumed a trigger is not automatically safe without one.

## Model 1: The Safety-Guardrail Skill

Read this `SKILL.md`, a safety-guardrail skill.  It is longer than most skills, which makes it a good one to read: every part of a skill's anatomy is visible.

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
## 2c.  A Fourth Route, and the Two Jobs a Hook Does for a Skill

Section 2b gave you three routes by which a skill body reaches the model, and all three end the same way: the text arrives, and the model decides.  Section 1 said why in one column of a table.  A system prompt, a project file, and a skill are enforced by the model reading them, and only the hook row is enforced by code.  The fourth route is the harness putting the text there and then checking what came of it, and it is worth being precise about what that buys you, because a hook does two quite different jobs for a skill and they are easy to run together.

The first job is **load-time**.  A skill loads only when the agent matches your request against its `description`, which is exactly the failure the *Skill Design Study* has you troubleshoot when a skill never fires.  A `SessionStart` hook sidesteps the match: whatever the hook prints on standard output is placed in the context at the start of the session, so the rules are present whether or not the model would have chosen to load them.  `UserPromptSubmit` does the same once per turn, which matters in a long session where the opening context has since been compacted away.

The second job is **exit-time**.  Injection guarantees that the text arrived, and it guarantees nothing about compliance, because a rule in the context window is still a rule the model reads.  A `Stop` hook runs when the agent wants to end its turn, and it may refuse: exit 2, and whatever the hook wrote to standard error goes back to the model as the reason it has to keep working.  That refusal is a gate in the sense of *Coding Agents*, because the check runs in code and looks at the state of the filesystem rather than at the model's account of itself.

Hold on to the distinction, because it is the whole of this section.  **Load-time puts the instruction where the model can see it.  Exit-time checks whether the model did it.**  Only the second one is enforcement.

## Model 1b:  The Skill Says It, the Hook Checks It

The `kickoff-interview` skill you write in *OpenCode Studio* promises, among other things, that the interview answers are written to `.ai/CURRENT_TASK.md` before any file is touched.  That clause was chosen carefully: it names an operation and it leaves a trace on disk, which is what makes it checkable at all.  Here is the same promise arriving both ways.

Load-time, so the rules are in context on turn one:

`.claude/settings.json` (Claude Code)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/kickoff-rules.sh" }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/sh
# .claude/hooks/kickoff-rules.sh: whatever this prints is added to the context.
cat "$CLAUDE_PROJECT_DIR/.agents/skills/kickoff-interview/SKILL.md"
```

Exit-time, so the promise is checked rather than trusted:

`.claude/settings.json` (Claude Code)

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/require-task-file.sh" }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/sh
# .claude/hooks/require-task-file.sh: the interview has to be written down
event=$(cat)
echo "$event" | grep -q '"stop_hook_active": *true' && exit 0
[ -s "$CLAUDE_PROJECT_DIR/.ai/CURRENT_TASK.md" ] && exit 0
echo "The kickoff interview is not recorded in .ai/CURRENT_TASK.md.  Run it and write the answers down before stopping." >&2
exit 2
```

The `stop_hook_active` line is the loop breaker: when the agent is already continuing because this hook sent it back, let it stop rather than trap it forever on a file it cannot produce.  You meet the same guard again in Recipe E.5 of *Coding Agents*, where the thing being checked is a test suite instead of a file.

Two runs, compressed.  In **Run A** the skill is on disk and nothing else is.  You ask for help with a feature, your request does not read like a kickoff, the skill never loads, the agent edits three files, and the turn ends.  Nothing went wrong that anyone would notice; you simply did not get the interview.  In **Run B** both hooks are installed.  The rules are in context whether the description matched or not, and when the agent tries to end the turn with no `.ai/CURRENT_TASK.md`, the turn does not end.  **The hook in Run B never read the skill and never weighed your request against it.**  It ran one test against the filesystem and answered with a number.

### Critical Thinking Questions

3.  Your `kickoff-interview` skill has four clauses: (a) ask at most five questions, (b) offer lettered options with a default, (c) write the answers to `.ai/CURRENT_TASK.md` before touching a file, and (d) keep the questions relevant to the task.  Sort them into the clauses a `Stop` hook could enforce and the clauses it could not, then say in one sentence what distinguishes the two groups.

   > *Hint: A hook sees arguments, exit codes, and the filesystem.  It never sees whether a question was relevant.  Clause (a) is a counting problem, so ask where the thing to be counted would have to be written down before a hook could count it.*

A teammate installs the `SessionStart` hook from Model 1b and says: "Good, now the agent has to run the interview."  Which statement below names what is wrong with that claim?

[( )] A `SessionStart` hook cannot print into the context; only `UserPromptSubmit` can
[(X)] The hook guarantees the rules are in the context, and the model still decides whether to follow them; only the `Stop` gate makes the interview required
[( )] The hook fires after the first tool call, so the rules arrive too late to matter
[( )] Nothing is wrong: text injected by a hook is followed, unlike text the model loads on its own

---
# Part II: Design One

## 3.  Spec-First for a Skill

A skill that is vague will be applied differently on every run, and you will not be able to predict or test it.  So the design steps are the ones that make a skill testable, and there are four.

1. **Job.**  One sentence, ten words or fewer.  If you cannot name the purpose in ten words, split the skill.
2. **Trigger.**  The `description`, written as the situation in the words a user would type.  Also write one request the skill must *not* fire on, because a skill that fires on everything trains you to ignore it.
3. **Instructions.**  Numbered rules, each concrete enough to check.  Not "write a good subject line" but "keep the subject to 50 characters or fewer."  Concrete constraints can be tested; abstract ones cannot.
4. **Test.**  One pass-or-fail check per rule, plus the negative-trigger request from step 2.

Steps 1 and 2 are where most of the ambiguity lives, and the fastest way to clear it is to let the agent ask.  A skill in the grill-me / interview-me style does exactly that: before it builds anything, it asks you numbered multiple-choice questions, each with a recommended default, and it records your answers as part of the spec.  Three menued questions ("Which files may this skill touch?  (a) only `src/`, recommended; (b) `src/` and `tests/`; (c) anywhere") cost less than one wrong guess, and the answers become the constraints that step 3's rules enforce and step 4's tests check.  The OpenCode Studio lab's kickoff skill is this pattern, so the `system-prompt-author` skill below is a good place to practice it: decide now which two questions it should ask before it writes a single line of the prompt.

The body of a skill has a recognizable shape, and this security-review skill from the design-first session shows it: a role sentence, a numbered list of checks, and an exact output format.

```markdown
# Security Review Skill

You are performing a security review of the change provided. Check for each of the following
OWASP top-10 risks for LLM-integrated applications:

1. **Prompt Injection**: does any user-supplied string reach a model prompt without sanitization?
2. **Insecure Output Handling**: does any model output reach `eval()`, `exec()`, or a shell?
3. **Excessive Agency**: does the agent take destructive actions (delete, overwrite) without confirmation?
4. **Sensitive Data Exposure**: are API keys, tokens, or PII logged or returned to the user?
5. **Unbounded Resource Consumption**: are there loops or queries with no upper bound?

For each risk, state: FOUND / NOT FOUND / CANNOT DETERMINE, with a one-line explanation.
If any risk is FOUND, suggest the minimal fix.

Review the most recent change provided by the user.
```

## Model 2: The `system-prompt-author` Skill

The job today is one you will do many times this term: write the system prompt that configures an agent.  Work through the four steps with the class, then compare to the version below.

**Job:** write a system prompt for an agent.

**Trigger:** fires on "write a system prompt", "give this agent a persona", "harden this prompt", "red-team this agent's instructions".  Must not fire on "what is a system prompt?", which is a question about the idea, not a request for one.

**Instructions and test** are in the file and the rubric that follow.  Create it at `.agents/skills/system-prompt-author/SKILL.md`; the directory name must match `name:`.

```markdown
---
name: system-prompt-author
description: Use when the user asks to write, revise, harden, or red-team a system prompt, an agent persona, or an agent's job description.
---

You are writing a system prompt for an agent.

## Rules
1. Open with the role.  The first sentence names the agent, says what it does, and says who it works for, because models anchor on early text.
2. State behavior positively.  Say what the agent should do, not only what it should not.
3. Constrain the format.  Name a length ceiling in words or sentences, and say how a reply is structured.
4. Handle uncertainty explicitly.  Say what the agent does when it does not know, and where it sends the user instead.
5. Name one escalation path.  Say which situation is handed to a human, and that the agent stops there.
6. End with a version stamp on its own line, in the form `v<major>.<minor> <YYYY-MM-DD>`.

Reply with the system prompt only: no code fence, no greeting, no commentary.
```

Those six rules are not invented for this session.  They are the six principles for effective system prompts that *Prompt Engineering as Agent Design* takes apart next session, written here in the shape a skill file takes, which is the point worth noticing: a skill is usually a thing you could already say, written down where an agent can read it.

The test is a six-item rubric, one item per rule.  Each item is one check a program can make on the reply.

| # | Rubric item | Checks rule | How the check works |
|---|---|---|---|
| 1 | The first line names a role | 1 | the line matches `you are` and contains a capitalized name |
| 2 | The prompt states a refusal | 2 | it contains one of: do not, never, refuse, decline |
| 3 | The prompt constrains the format | 3 | a number followed by words, sentences, or bullets |
| 4 | The prompt handles uncertainty | 4 | it contains one of: unsure, uncertain, do not know |
| 5 | The prompt names an escalation path | 5 | it contains one of: escalate, professor, instructor, a human |
| 6 | The prompt carries a version stamp | 6 | it matches `v<digits>.<digits>` and a `YYYY-MM-DD` date |

Install it and confirm the trigger before you measure anything: create `.agents/skills/system-prompt-author/`, save the file above inside it as `SKILL.md`, and start opencode.  Then type "Write a system prompt for a course assistant" and watch the skill load.  Then type "What is a system prompt?" and confirm it does not.

### Critical Thinking Questions

4.  Rule 2 has two halves: say what the agent should do, and do not rely only on prohibitions.  Only the prohibition half has a rubric item.  Why was the positive half left out of the rubric, and what would you need to score it?

   > *Hint: "Contains the word never" is a string check.  "Is framed positively" is a judgment about the whole prompt.  The *Critique, Consensus, and the LLM Judge* session later in the term is about scoring judgments; today's rubric sticks to what a string check can decide.*

5.  Predict, before Part III runs anything: which rubric item will `llama3.2` fail most often *without* the skill?  Which will it still fail *with* the skill?  Write both predictions down; you will check them against the table.

   > *Hint: Without instructions, a model writes something that reads well and asks for nothing it was not asked for, so the items most often missed are the two nobody would think to include.  With instructions, the check most often missed is the one that requires an exact format.*

---
# Part III: Measure It

In this part you find out whether the skill did anything.  The method is a golden-set harness, the same one *Prompt Engineering as Agent Design* reuses next session: hold everything fixed, change one thing, and score.  The one thing that changes is whether the skill's instructions are present.

## 4.  The Protocol

A measurement is only as good as what it holds still.  Here is everything the harness pins.  Keep it in mind for the *Skill Design Study*, where you change one thing at a time as you refine your own skill.

| What | Fixed value | Why it is fixed |
|---|---|---|
| Models | `llama3.2` and `llama3.2:1b` | Two sizes, so a result that holds on one and not the other is visible |
| Temperature | `0.0` | Pins the wording, so runs are repeatable (*Running Your Own AI*, Section 3c) |
| Seed | `42` | Pins the random draw itself |
| Task prompt | `TASK`, the same design brief every run | The brief is the input; it does not change between conditions |
| Condition "without" | `BASELINE` as the system prompt | The control |
| Condition "with" | `BASELINE` plus the skill body as the system prompt | The one change |
| Runs per cell | `RUNS = 3` | Shows whether a score is a property of the skill or of one run |
| Score | Six-item rubric, 0 to 6 per run | The same items for every cell |

One honest note about the "with" condition.  When a skill fires inside opencode, the agent reads the `SKILL.md` body into its context.  The harness hands that body over directly as part of the system prompt, so it measures the instructions on their own, separately from the trigger.  You tested the trigger at the end of Part II by watching it load and not load; the harness tests the rest.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.  Before you run it, write down the score you expect in each of the four cells.

```python
import re
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
        print(f"[skills:chat] {e}")
        import traceback; traceback.print_exc()
        return ""

# The task: one design brief, identical in every run.
BRIEF = """Write the system prompt for Aria, the CS357 course assistant at Ursinus College.

Aria answers student questions about CS357: the activities, the labs, the project,
and the tools the course uses, which are Ollama, opencode, and Docker.  Students
reach her from the course website at any hour, including the night before a
deadline.  She is not a grader, and she has no access to Canvas or to any
student's record.  Today is 2026-09-22."""
TASK = BRIEF

# The control: a system prompt with no skill in it.
BASELINE = "You are a helpful assistant."

# The skill body, exactly as it appears below the front matter in SKILL.md.
SKILL = """You are writing a system prompt for an agent.

## Rules
1. Open with the role.  The first sentence names the agent, says what it does, and says who it works for, because models anchor on early text.
2. State behavior positively.  Say what the agent should do, not only what it should not.
3. Constrain the format.  Name a length ceiling in words or sentences, and say how a reply is structured.
4. Handle uncertainty explicitly.  Say what the agent does when it does not know, and where it sends the user instead.
5. Name one escalation path.  Say which situation is handed to a human, and that the agent stops there.
6. End with a version stamp on its own line, in the form `v<major>.<minor> <YYYY-MM-DD>`.

Reply with the system prompt only: no code fence, no greeting, no commentary.
"""

# The six-item rubric, one item per rule.  One string check per item, pass or fail.
HEDGES = ("unsure", "uncertain", "not certain", "do not know", "don't know")
REFUSALS = ("do not", "don't", "never", "refuse", "decline", "will not")
ESCALATIONS = ("escalate", "professor", "instructor", "a human")

def score(prompt):
    text = prompt.strip()
    low = text.lower()
    first = (text.splitlines() or [""])[0]
    return [
        ("1 role named in line 1",
         bool(re.search(r"\byou are\b", first, re.I))
         and bool(re.search(r"\b[A-Z][a-z]{2,}\b", first))),
        ("2 states a refusal",        any(w in low for w in REFUSALS)),
        ("3 constrains the format",
         bool(re.search(r"\b\d+\s*(words|sentences|bullets?)\b", low))),
        ("4 handles uncertainty",     any(w in low for w in HEDGES)),
        ("5 names an escalation path", any(w in low for w in ESCALATIONS)),
        ("6 carries a version stamp",
         bool(re.search(r"\bv\d+\.\d+\b", low))
         and bool(re.search(r"\b20\d{2}-\d{2}-\d{2}\b", text))),
    ]

MODELS = ["llama3.2", "llama3.2:1b"]
RUNS = 3
CONDITIONS = {"without": BASELINE, "with": BASELINE + "\n\n" + SKILL}

for model in MODELS:
    for label, system in CONDITIONS.items():
        totals = []
        for run in range(RUNS):
            reply = chat(system, TASK, model=model)
            checks = score(reply)
            passed = sum(ok for _, ok in checks)
            totals.append(passed)
            failed = [name for name, ok in checks if not ok]
            print(f"{model:12} {label:8} run {run + 1}: {passed}/6  failed: {failed}")
        print(f"{model:12} {label:8} mean = {sum(totals) / RUNS:.2f}\n")
```

## Model 3: The Results Table

The Recorder fills this in from the printed output.  The *Skill Design Study* asks for a lighter version of the same habit: a log of each run of your own skill and the one change you made in response.

| Model | Condition | Run 1 | Run 2 | Run 3 | Mean (of 6) | Items that failed |
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

   > *Hint: Compare the difference between cells to the spread within a cell.  A one-item gap between conditions means little when one condition's own three runs already differ by one.  Which rubric item moved also matters: a skill that says "end with a version stamp" and fixes only that item did exactly one thing.*

8.  Why two models?  Write one sentence that would be true if the skill effect were large on `llama3.2` and zero on `llama3.2:1b`, and a different sentence for the reverse.  Then say what you can conclude about the *skill* from either.

   > *Hint: A skill is guidance the model chooses to follow, and a smaller model follows a numbered list less reliably.  A result on one model is a fact about that pair.  Two models let you say whether the effect belongs to the skill or to the model.*

9.  Your rubric has six items and your brief describes one agent.  If you edited the skill until every cell scored 6.00 on Aria, what could happen on a different agent?  Name the risk and the guard.

   > *Hint: This is the same risk as tuning a prompt to the five inputs it was tested on.  A second brief you never tuned on is a held-out case.  Write one for an agent with a different audience and a different refusal.*

---
# Part IV: Synthesis and Practice

## 5.  Exercises

1.  **A held-out brief.**

   *What to do:* Write a second design brief for an agent with a different audience and a different refusal, such as a lab assistant that must never run a command for a student.  Rerun the Part III cell with it as `BRIEF`.  Fill in a second results table.

   *Starter hint:* Do not edit the skill between the two briefs.  The question is whether the ranking of the four cells holds on input the skill was not tuned on.

   *You've succeeded when:* You can state in one sentence whether the skill effect on each model survived the new brief, with the two tables as evidence.

2.  **Move one rule into code.**

   *What to do:* Rubric item 6 asks for a version stamp.  The skill asks for one, and a model may still forget.  Write a check that reads a prompt file and refuses it when the stamp is missing, then run it against a prompt the model produced without the skill.

   *Starter hint:*
   ```bash
   #!/bin/sh
   # require-stamp.sh <prompt-file>
   grep -Eq 'v[0-9]+\.[0-9]+ [0-9]{4}-[0-9]{2}-[0-9]{2}' "$1" && exit 0
   echo "require-stamp: no version stamp in $1" >&2
   exit 1
   ```

   *You've succeeded when:* Your transcript shows one prompt accepted and one refused, and you can say in one sentence what the skill could not guarantee that the check does.

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

-> Coming Up Next: You now have a harness that scores one instruction change across two models.  Next session, *Prompt Engineering as Agent Design: System Prompts, Personas, and Comparing Models*, turns that harness on the system prompt itself: what each of its six principles does to the output, how a persona changes the distribution of answers rather than the facts, and how to compare two models on the same prompt without fooling yourself.  Bring today's results table; the comparison method is the one you just used.

---

## Further Reading

- OpenCode documentation. https://opencode.ai/docs/skills/, which covers where skills are discovered, the three values `permission.skill` takes (`allow`, `ask`, `deny`), and a short checklist to work through when a skill you wrote never appears.
- Superpowers, a community skill bundle for agent CLIs: https://github.com/obra/superpowers.  Read a few of its `SKILL.md` files as further models of description-as-trigger.
- Anthropic.  "Building Effective Agents." https://www.anthropic.com/research/building-effective-agents, the evaluator-optimizer pattern is today's measurement loop in general form.
- On evaluation: this course's *Evaluating Agent Outputs*, *Benchmarking*, and *Testing Agents* activities extend today's six-item rubric into larger golden-test, benchmark, and property-based harnesses.
- Claude Code hooks: https://code.claude.com/docs/en/hooks, the reference for the events in Section 2c, the exit-code contract, and the JSON form a hook uses when it needs to say more than yes or no.
- The eight-recipe hook cookbook from Week 1, including the `Stop` gate that Model 1b adapts: [Coding Agents: OpenCode, Spec-First Development, Hooks, and Reading the Log](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-codingagents.md), Part E.
- planning-with-files, a planning skill distributed with its enforcement attached: https://github.com/OthmanAdi/planning-with-files (MIT).  It registers six lifecycle hooks so that its plan files are re-injected every turn, and its `Stop` gate holds the stop while any phase is still marked `in_progress`.  Read it as a worked answer to the question Section 2c raises: what does it take to ship a skill that does not depend on the model remembering to use it?

---

# Extension: A Skill Big Enough to Need a Filing System (self-paced)

Optional, and nothing above assumes it.  Today you wrote skills that fit on a page.  This one does not, and why it cannot is the lesson.

## What it is, in plain language

Download it and look inside: [small-model-orchestrator.skill](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/small-model-orchestrator.skill).  It is an ordinary zip, so you can read it without installing it, which is the right order of operations for any skill someone else wrote:

```bash
unzip -l small-model-orchestrator.skill          # what is in here?
unzip -p small-model-orchestrator.skill small-model-orchestrator/SKILL.md | head -40
```

Here is what that second command prints first, and it is the same shape as the front matter on the skill you wrote today:

```yaml
---
name: small-model-orchestrator
description: Reliability and orchestration protocol for difficult coding, tool-use,
  research, data, document, and mixed tasks, especially with small local or offline
  language models. Use when correctness matters more than latency or token cost and
  the agent should plan progressively, keep an always-current RESUME.md handoff
  checkpoint, version its work with Git, compact context proactively, verify every
  consequential action, diagnose failures, retry and replan, and perform adversarial
  gauntlet review before declaring success.
license: MIT
metadata:
  author: Bill + OpenAI
  version: "0.4.0-platform-agnostic"
  primary-use-case: "local-offline-private-models"
  optimization-target: "maximum-verified-task-success"
---
```

Compare it with your own `description`.  Yours probably names what the skill does.  This one names **when it should fire**: the task types, then a condition (*when correctness matters more than latency or token cost*), then the behaviors it imposes.  A model decides whether to load a skill from this block alone, so a description that reads like a title gets loaded at the wrong times, or never.

A `.skill` file is a zip archive of one skill directory, which is also how you would share your own skill from the Skill Design Study if you chose to.  Installing it by hand is the whole procedure: extract it into one of the discovery paths from Section 2, at the top of the project you want the agent to work in.  Use `.agents/skills/`, the same path this deck has used throughout.

```bash
mkdir -p .agents/skills
unzip -q small-model-orchestrator.skill -d .agents/skills/
ls .agents/skills/small-model-orchestrator/SKILL.md
```

Two habits belong with that command, because this is the moment you hand a stranger's instructions to your agent.  **Gate it.**  Once anything in a discovery path came from somewhere else, set `"skill": { "*": "ask" }` in `opencode.json` and allow your own skills by name; `ask` prompts you before a skill loads, where `allow` does not.  **And prefer the skill you wrote.**  Suspicion is not the argument.  Writing one costs you five minutes and no build step, where an installed one leaves you holding instructions you did not write, whatever sits in its `scripts/` directory, and a `description` that now competes with your own for every trigger.  Read published skills constantly and borrow their structure; install them when they do something you cannot write yourself, as this one does.

Check that last path rather than assuming, because the directory is the installation and a wrong directory fails without an error message.  `SKILL.md` belongs exactly one folder deep, at `.agents/skills/small-model-orchestrator/SKILL.md`; if your unzip tool added an extra folder named after the archive, move the inner one up a level.  On Windows, rename the file to `.zip` first and run `Expand-Archive -Path small-model-orchestrator.zip -DestinationPath .agents/skills`.  Start opencode afterward and ask it to list the skills it can see; a skill that does not appear is in the wrong place, not broken.

It is a set of working habits for an AI model that has been given a long, fiddly job and no supervision.  Think of the model you ran today as a capable assistant with an excellent vocabulary and a terrible short-term memory.  Left alone for twenty minutes it will do three things, and only the third one is frightening:

| What you see | What is actually going on |
|---|---|
| It forgets a rule you gave it early on | Its working memory filled up and the oldest part was quietly discarded.  It was not told, so it does not know |
| It stops in the middle of a sentence | It hit a hard limit on how much it may write at once |
| It announces that it finished, and it did not | Nothing ever checked.  A confident summary and a correct one read identically |

The third one is the problem this skill exists for.  The sentence at the heart of it is worth writing down:

> A fluent response, successful command, or generated file is not proof of completion.

## How it works, without the jargon

The skill is a checklist discipline, of the same kind that surgical teams and flight crews adopted for the same reason: not because anyone involved is incompetent, but because competent people under load skip steps and do not notice they skipped them.

Before the habits, the story that produced them.  The authors watched a small model fail, and wrote down what they saw:

> These changes respond to an observed failure pattern: with frequent compaction, a small model trusted drifting summaries over disk, stopped updating its checkpoint, edited from memory, and lost work to an unversioned delete.

That is four mistakes in a row, and each one made the next one possible.  Its notes about the work drifted away from what was actually in the files.  Believing the notes, it stopped bothering to update them.  Working from memory instead of from notes, it edited a file it only *thought* it remembered.  And because nothing was backed up, a deletion had no undo.  **Only the last step looks like a disaster.  The first three look like an agent working normally.**

Five habits, and each one breaks that chain at a different link:

1.  **Write it down where the conversation cannot reach.**  The model keeps a file in your project that says what the job is, what it has genuinely finished, and what it is about to do next.  When the conversation is lost, the file is not.  Version 0.4.0 adds a list of exact moments to update it, because "keep it current" is the kind of instruction a small model quietly stops following.
2.  **Say what you are about to do before you do it, and mark the result unknown.**  This is the clever one.  Before it changes anything, it records "I am about to do this, and I do not yet know whether it worked."  If the power goes out mid-step, whoever picks up the job later knows there is something to go and check, rather than assuming nothing happened.
3.  **Commit every finished step, so there is always an undo.**  This is new in 0.4.0 and it is the answer to the deleted work.  The model makes a save point in Git after each verified step, on its own branch, so any mistake can be rewound to the last known-good state.  Notice how carefully that permission is drawn: it may make local save points, and it may **not** push, merge, or delete branches without being asked.  It is allowed to protect its work, not to publish it.
4.  **Prove it, do not assert it.**  Reading a file back is better evidence than a tool saying "success".  A test someone else wrote is better than a test the model wrote to check its own work, because the model's test inherits the model's misunderstanding.
5.  **Attack your own work before calling it done.**  A separate pass that goes looking for nine specific kinds of problem, of which the sharpest is "fake completeness": leftover TODOs, stubbed-out functions, tests that were quietly skipped, comments describing behavior the code does not have.

Habit 2 deserves a sentence on its own, because it is the one that generalizes furthest beyond AI.  **A lost reply is not proof that nothing happened.**  If your connection drops while a payment is being submitted, the payment may well have gone through.  An assistant that assumes failure and tries again has just paid twice.

There is a sixth rule that is less a habit than a reflex, and it is short enough to adopt yourself today: **never edit from memory.**  Re-read the exact lines right before changing them, never from a summary or from a read you took several edits ago.  An agent that remembers a file as it was three changes back will write its next change against a version that no longer exists.

## Why the file is so big

Your `system-prompt-author` skill is one page because it does one thing.  This one has sixteen reference documents and ten templates, and that creates a problem it then has to solve: guidance the model cannot afford to read is guidance the model will not follow.

Its answer is worth stealing for your own skill work.  The main file stays short and acts as a switchboard, pulling in exactly one reference for the phase it is currently in, and it says outright that the agent must not load everything at the start.  A skill that respects its own reader's limited attention is a better skill.  That is true of the model, and it is true of your teammates.

Two other things to notice as an author, both of which are today's lessons arriving from a different direction:

- **The description is still the trigger.**  It names the *situation*, not the tool, right down to the condition "when correctness matters more than latency or token cost".  That one sentence is all the model reads when deciding whether this skill applies.
- **It says what it cannot do.**  Its own documentation states that it cannot restart a dead process, cannot force a model to comply, and cannot tell you the outcome of something whose answer was lost.  A skill that is honest about its limits is easier to trust about everything else.

## Try it against what you built today

Run the same with-and-without comparison from Part III, but on a task long enough that memory becomes the bottleneck: something with six or seven steps rather than one.  Watch specifically for whether the model checks its own work when nobody asked it to.

Expect `llama3.2` to struggle.  That is the point, and it is the most useful thing you will see: every place the small model drops a step is a place where the instruction relied on good intentions instead of structure.  Rewriting one of those steps so that it is hard to skip rather than merely requested is exactly the move the Skill Design Study is asking you to make.

## Where to go next

The technical treatment, with the checkpoint format, the evidence hierarchy, the nine-point review, the failure-recovery table, and guidance on which model to point at it:

- [A Skill That Scaffolds a Small Model](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/FilesystemIsolation#a-skill-that-scaffolds-a-small-model)

To run it against a real agent in a container, on your own model:

- [One Script Instead of an Image, and What That Convenience Costs](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/FilesystemIsolation#one-script-instead-of-an-image-and-what-that-convenience-costs)

---

# Extension: Making the Skill Load Every Time (self-paced)

Optional, and nothing above assumes it.  Section 2c drew a line between putting an instruction in front of the model and checking that the model acted on it.  This extension has you build both sides of that line against a skill you already wrote, and it closes a gap Exercise 3 leaves open on purpose.

## Where this picks up

Exercise 3 asks you to score your `kickoff-interview` skill on five conditions and then concedes that one of them, "touch no file," is not visible in the reply text at all.  It asks you to say where that check would have to live.  Here is the answer, made concrete: it lives outside the model, in code, looking at the filesystem at the moment the agent tries to stop.

## What to do

1.  **Install the load-time hook.**  Build `kickoff-rules.sh` from Model 1b, make it executable with `chmod +x`, and register it under `SessionStart` in `.claude/settings.json`.  Start a session and ask the agent, in your first message, to repeat back the rules it is working under.  You are checking one thing: that the rules are there without your having named the skill.

2.  **Run without the gate.**  With only the `SessionStart` hook installed, ask for a change to a file in a way that does not sound like a kickoff request, for example "add a `--verbose` flag to the CLI."  Capture the transcript.  Note whether `.ai/CURRENT_TASK.md` was written, and whether the agent edited anything before writing it.

3.  **Install the exit-time gate.**  Build `require-task-file.sh` from Model 1b, `chmod +x` it, register it under `Stop`, delete `.ai/CURRENT_TASK.md`, and run exactly the same request again.  Capture this transcript too.

4.  **Score the item you could not score.**  Return to your five-item rubric from Exercise 3 and rewrite the "touch no file" item so that it is decided by the hook's exit code rather than by reading the reply.  Run your `score()` over both transcripts with the new item included.

5.  **Write two sentences.**  The first names what changed between Step 2 and Step 3 and what caused it.  The second names something the gate still cannot tell you.

## You've succeeded when

You have two transcripts of the same request, a rubric in which every item including the fifth is decided by something other than your own reading of the text, and a sentence that honestly states the gate's limit.

## The limit, stated plainly

The gate proves that `.ai/CURRENT_TASK.md` exists and is not empty.  It does not prove that the file contains a real interview.  A model that wanted to get past this gate could write one line of nonsense into it and stop, and the hook would let it.  That is not a flaw in hooks; it is the general shape of the problem.  **Every gate checks a proxy for the thing you actually care about, and the engineering question is how far the proxy sits from the thing.**  Tightening the proxy, by checking that the file contains five answered questions rather than merely that it exists, is worth an afternoon on your own project, and it is the same move you make when you turn a vague rubric item into a string check.

## Where to go next

- The full treatment of hooks as gates, with eight recipes and the table of what each one can and cannot see: [Coding Agents: OpenCode, Spec-First Development, Hooks, and Reading the Log](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-codingagents.md), Part IIb and Part E.
- The authoring consequence, which is that you should write the clauses you intend to enforce so a check outside the model can see them: [Agent Skills and Plugins](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/AgentSkills#enforcing-what-a-skill-asks-for).
