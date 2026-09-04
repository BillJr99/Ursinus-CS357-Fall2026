---
layout: assignment
permalink: /Assignments/LocalAgent/Direction7
title: "CS357 Lab: Local Agent, Direction 7: Coding Agent and Cowork Agent, Same Task"

info:
  coursenum: CS357
  purpose: "To run one small, checkable change through a coding agent and through a cowork-style general agent, against the same local model, and to say from the traces which paradigm fits which kind of task."
  tilt:
    task: "Define a four-item done-when list for one change to your Local Agent's command line, drive that change through opencode and through a tools-enabled Open WebUI chat, capture both traces, and compare them on a table."
    criteria: "I assess your work on a task definition that can be checked by running something, two captured traces that each contain the plan, the diff, and the commands run, a comparison table whose every cell points at a trace line, and a one-page comparison that commits to a recommendation.  The rubric below spells out each row."
  goals:
    - To define a task and a done-when list precise enough that two different agents can be checked against it
    - To drive a coding agent through a change and capture its plan, diff, and commands as a trace
    - To drive a cowork-style general agent through the same change with only local tools and capture the same trace
    - To compare the two paradigms on steps, files touched, checks run, permission gates, and errors, with every claim tied to a trace line
    - To explain which paradigm fits which kind of task in terms of who runs the actions and where the gates sit
  rubric:
    - weight: 20
      description: Task Definition and Done-When
      preemerging: No task definition is provided, or the task is stated only as a title
      beginning: The task is stated, but the done-when list has fewer than four items or contains items that cannot be checked by running a command or opening a file
      progressing: The task and a four-item checkable done-when list are complete, but the list changed between the two runs, or the prompt handed to the two agents differs in substance
      proficient: The task is stated in one paragraph before either run; the done-when list has exactly four items, each checkable by a command or a file inspection; the same list and the same verbatim prompt are used for both runs, and the writeup quotes that prompt
    - weight: 35
      description: Two Complete Traces
      preemerging: No trace is submitted, or only one agent was run
      beginning: Two traces exist, but at least one is a retyped summary rather than a captured transcript, or the diff or the commands run are missing from either
      progressing: Both traces contain the plan, the full diff, and the commands run, but the two runs used different models or settings, or the four done-when checks were not run at the end of one trace
      proficient: Both traces are captured transcripts that each contain the agent's stated plan, the full git diff after the run, every command executed and whether the agent or you ran it, the model name and settings, and the result of all four done-when checks; both runs use the same Ollama model, temperature, and prompt
    - weight: 35
      description: Comparison Table and Analysis
      preemerging: No comparison table is submitted
      beginning: The table is present, but rows are missing or cells hold impressions instead of counts and quotes taken from the traces
      progressing: All six rows are filled from the traces, but the analysis restates the table without explaining why the two agents differed
      proficient: Every cell of the six-row table cites a line in one of the traces; the analysis explains each difference in terms of who ran the actions and where the permission gate sat; it names what each agent got wrong and whether the done-when list caught it; and it says which paradigm fits which kind of task, with a reason that follows from the table
    - weight: 10
      description: Writeup
      preemerging: No writeup is submitted
      beginning: The writeup is submitted, but it is missing the one-page comparison or the version and settings record
      progressing: The one-page comparison is present with a minor omission, and the reflection answers are superficial
      proficient: The one-page comparison commits to which paradigm fits which task and why, cites the table, and records the model name, temperature, opencode version, and Open WebUI version; the reflection answers cite specific trace lines; and the pair log continues from the core lab with timestamped swaps
  readings:
    - rtitle: "Coding Agents: OpenCode, Spec-First Development, and Reading the Diff"
      rlink: "Activities/liascript-codingagents.md"
      liapage: true
    - rtitle: "Agentic CLIs: the three paradigms, permission gates, and routing tools through your local model"
      rlink: "../../Tutorials/AgentCLIs"
    - rtitle: "Agent Observability and Tracing"
      rlink: "../../Tutorials/Observability"

tags:
  - agents
  - coding-agents
  - local-ai
  - observability
---

> **Grading:** This page is one of the directions for the [Local Agent Lab]({{ site.baseurl }}/Assignments/LocalAgent).  It carries no points on its own.  I grade your core work and your direction work together with the Local Agent Lab rubric on the core lab page, and the rubric above says how this direction earns its share.

> **Rather not write the code?**  [Direction 0: The OpenWebUI Route]({{ site.baseurl }}/Assignments/LocalAgent/Direction0) reaches the same objectives for the Local Agent Lab with no code to author.  This direction is different: the agents write the code, and you write the specification and the comparison.  If you took Direction 0 for the core, the alternative task in Part 1 keeps this direction open to you.

> **What this direction requires**
>
> - **Accounts:** none.  Both agents run against your local Ollama model.
> - **API costs:** none.
> - **Installs / disk:** opencode, which you installed in Week 1 during *Your AI Workbench*, and Open WebUI, which you have from the *Running Your Own AI* session or from Direction 0.  Nothing new to pull.
> - **Hardware:** any machine that runs the core lab.
> - **No-cost fallback:** not needed; this direction is fully local by design.  If you have a desktop cowork agent such as Claude Cowork, you may use it for Part 3 instead of Open WebUI, but you do not need one, and the two traces must still use the same local model.

---

Run one small change twice, once through a coding agent and once through a general-purpose agent, against the same local model, and find out from the traces what each paradigm is good for.  The change is deliberately small (a `--json` flag and a test for your Local Agent's command line) so that the difference you observe comes from the agent, not from the task.

Work with your core-lab partner and keep the swap log going.  The person who is not driving reads the trace as it scrolls by, because the comparison in Part 4 is built entirely from what the traces recorded.

---

#### Before You Start

##### Prerequisite Concepts

Finish core Parts 1 through 4 before starting here.  Your agent from Part 1 (`agent.py`, `config.json`, and the two tools from Part 2) is the code both agents will change.  Re-read these before lab day:

- [Coding Agents]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-codingagents.md): the plan before the diff, and reading the diff adversarially
- [Agentic CLIs]({{ site.baseurl }}/Tutorials/AgentCLIs): the three paradigms and permission gates
- [Agent Observability and Tracing]({{ site.baseurl }}/Tutorials/Observability): why a captured trace beats a summary

##### Tools to Check

Confirm both agents can reach your local model before you define the task.  Run `opencode --version` and `ollama list`, then start `opencode`, run `/model`, and confirm your Ollama provider is listed with the model you used in the core lab.  Open Open WebUI, start a chat with the same model, and confirm it answers.  Record the opencode version, the Open WebUI version (Settings -> About), and the model tag; the writeup asks for all three.

Budget about four hours: twenty minutes to define the task, forty-five for the coding agent, an hour for the cowork agent, forty-five for the table, and thirty for the writeup.

---

#### Background: Chat, Code, and Cowork

The three paradigms differ in who runs the actions and where those actions land, not in the model behind them.  A chat assistant tells you what to do and you do it.  A coding agent acts on one repository, behind permission gates.  A cowork agent acts across your whole machine: files, apps, and services, with the task as its only scope.  The analogy from the Agentic CLIs tutorial is a colleague on the phone, a contractor with the keys to one room, and an assistant loose in the whole office; the analogy stops matching when you notice that all three can be the same model, which is exactly what this direction arranges.

Three terms carry the rest of this page.  A **permission gate** is a pause where the tool stops and asks you to approve or refuse an action before it runs; every `allow?` line in an opencode session is one.  A done-when list is a short list of conditions, each checkable by a command or a file inspection, that must all hold before the task counts as finished.  A trace is the captured record of what an agent did: its plan, the commands it ran, and the diff it produced.

The paradigms form a ladder of blast radius.  Chat can only mislead you.  Code can change your repository.  Cowork can touch anything it has a tool for.  The oversight habits from the coding agents session matter more as you climb that ladder, not less, and Part 3 is where you feel the difference.

Self-hosted general agents already exist in this course.  The [Local Agent Stack]({{ site.baseurl }}/Assignments/LocalAgent/Direction2) runs Hermes as its agent tier: a tool-calling agent with a persistent identity directory, driven through the gateway rather than a terminal.  That is the cowork column with a local model behind it.  If you already have Hermes running, it qualifies for Part 3; otherwise, an Open WebUI chat with a file tool enabled is the same paradigm with less setup.

###### Questions to Work Through

1.  Your `agent.py` from the core lab has a loop, a parser, and two tools.  Which paradigm was it, and what would you have to add to move it one column to the right?

    *Hint: it runs actions you wrote, on inputs you chose.  The move to the code column is a file tool plus a gate; the move to cowork is removing the scope.*

2.  The same Ollama model sits behind both runs in this direction.  Name two things that can still differ between the two traces even though the weights are identical.

    *Hint: the system prompt each harness prepends, and the tools each harness exposes, are both outside the model.*

Remember two things from this section.  The paradigm is set by the harness, not the model.  And the wider the reach, the more a captured trace is worth.

---

#### Part 1: Define the Task and the Done-When List

**Goal:** Write the task and its four checks before either agent sees them, so that both runs are measured against the same target.

##### The task

Add a `--json` flag to your Local Agent's command line, plus one test.  Today, `python agent.py` runs a hardcoded goal and prints a per-step trace followed by the answer.  After the change:

- `python agent.py "goal text"` behaves exactly as it does now.
- `python agent.py --json "goal text"` prints exactly one JSON object on standard output, with the keys `answer`, `steps`, and `reason`, and nothing else on standard output.  The per-step trace may go to standard error or be suppressed.
- A new file `test_agent.py` holds one pytest test that replaces `call_model` with a stub returning `Final Answer: Paris.`, runs the agent in JSON mode, and asserts that the output parses and has all three keys.  The test makes no network call.

That is the whole task.  Do not let either agent enlarge it.

##### The alternative task

If your core agent has no Python command line (you took Direction 0 for the core), use this equivalent of the same size: add a `--config PATH` flag to the from-scratch loop in the core lab's *Code Cell*, so that model name, temperature, and step budget load from the named JSON file, plus one pytest test that loads a temporary config and asserts the values were applied.  Keep the same four-item shape below.

##### The done-when list

Write these four items into `docs/task.md` before Part 2, and do not edit them afterward:

1.  `python agent.py --json "What is the capital of France?"` prints one line that `python -m json.tool` accepts, and the parsed object has the keys `answer`, `steps`, and `reason`.
2.  `python agent.py "What is the capital of France?"` prints the same per-step output it printed before the change (compare against a saved run).
3.  `pytest test_agent.py` reports one test passed, with the Ollama server stopped.
4.  `git diff --stat` shows changes to `agent.py` and `test_agent.py` only.

Save a baseline run now, because item 2 needs it:

```bash
python agent.py > transcripts/00-baseline.txt 2>&1
git add -A && git commit -m "Baseline before Direction 7"
```

##### The prompt

Both agents receive the same text.  Write it once in `docs/prompt.txt` and paste it verbatim into each:

```
Read agent.py.  Add a --json command-line flag: when present, print exactly one JSON object
with keys answer, steps, and reason to stdout and nothing else on stdout.  Without the flag,
behavior must not change.  Add test_agent.py with one pytest test that stubs call_model to
return "Final Answer: Paris." and asserts the JSON output has all three keys, with no network
call.  Show me your plan first and stop.  Do not change any other file.
```

> **Checkpoint 1.**  Can each of your four items be settled by running one command and reading its output?  If any item needs a judgment call, rewrite it until it does not.

---

#### Part 2: Run It Through the Coding Agent

**Goal:** Drive opencode through the task and capture the plan, the diff, and every command as one trace.

Start from a clean tree in your core-lab repository and capture the whole session:

```bash
git status          # must be clean
opencode run "$(cat docs/prompt.txt)" 2>&1 | tee transcripts/01-coding-agent.txt
```

You may instead run `opencode` interactively and paste the prompt; either way, the session goes into `transcripts/01-coding-agent.txt`, because you cannot reconstruct it afterward.  Then:

1.  Read the plan before you approve anything.  If it names a file other than `agent.py` or `test_agent.py`, reject it and say why; keep that exchange in the trace.
2.  Approve the edits and let it run the tests.  Note every permission gate as it appears; each one is a line in the trace you will cite in Part 4.
3.  When it declares itself done, run the four done-when checks yourself and append the output to the trace:

```bash
{
  echo "=== done-when checks ==="
  python agent.py --json "What is the capital of France?" | python -m json.tool
  python agent.py "What is the capital of France?" | diff - transcripts/00-baseline.txt && echo "item 2: same output"
  pytest test_agent.py
  git diff --stat
} 2>&1 | tee -a transcripts/01-coding-agent.txt
```

For item 3, stop the Ollama server before running pytest (`pkill ollama` or close the app), then start it again.  A test that only passes with the server running is making a network call.

4.  Save the diff on its own: `git diff > transcripts/01-coding-agent.diff`.
5.  Commit on a branch so the second run starts from the same baseline: `git checkout -b coding-agent && git commit -am "Direction 7: coding agent run" && git checkout main`.

> **What you should see:** a plan naming the two files, a gate before each edit or command, a test run, and the four checks.  If any check fails, that is a finding, not a failure of the lab: record it, and do not fix it by hand before Part 4.  If the agent skips the plan and starts editing, interrupt it, restart with "Show me your plan first and stop." as the first sentence, and note the retry in the trace.

---

#### Part 3: Run It Through the Cowork Agent

**Goal:** Give a general agent the same prompt and the same model, with only local tools, and capture the same trace.

A cowork-style agent needs a way to touch your files.  Open WebUI gives it one through Tools: Python that runs on the Open WebUI server when the model calls it.  Set it up from the fresh baseline:

1.  Return to the baseline: `git checkout main && git status` (clean, at the baseline commit).
2.  In Open WebUI, go to Workspace -> Tools and create one tool with three methods: `read_file(path)`, `write_file(path, content)`, and `run_command(command)`.  Restrict every path to your repository directory and refuse anything outside it.  The method signature and docstring are the schema the model reads, so write both carefully.  If Open WebUI runs in Docker, bind-mount your repository into the container so the tool can reach it, and use the container-side path in the tool.
3.  Read your own tool's source once more before you enable it.  It runs with whatever access the Open WebUI server has, and there is no gate between the model's call and its execution unless you write one.
4.  Create a Workspace model on the same Ollama tag you used in Part 2, at the same temperature, with the tool enabled.  Leave the system prompt empty or minimal so that the harness, not your prompt, is what differs.
5.  Start a new chat, paste `docs/prompt.txt` verbatim, and let it work.  Answer its questions the same way you answered opencode's.

Capture the trace.  Open WebUI has no terminal to `tee`, so export the chat (the chat menu offers a download or export) to `transcripts/02-cowork-agent.txt`, and add to the same file every tool call the chat displayed, in order, with the argument each was called with.  Then run the same four done-when checks from Part 2, appending to `transcripts/02-cowork-agent.txt`, save `git diff > transcripts/02-cowork-agent.diff`, and commit on a `cowork-agent` branch.

If you use a desktop cowork agent instead, the requirements do not change: same model tag, same prompt, an exported or copied transcript that lists every action taken, and the four checks appended.

> **What you should see:** the model calling `read_file` on `agent.py`, then `write_file` once or more, then `run_command` for pytest, or some subset of those.  Note what it did not do.  A cowork agent that never runs the tests, or that rewrites `agent.py` from memory with parts missing, has told you something about where the gates are: record it, `git checkout agent.py`, and re-run once, noting the second attempt.  If the model answers in prose and never calls a tool, confirm the tool is checked in the model editor, then ask explicitly "use the read_file tool on agent.py" as a second turn, noted in the trace.  If `write_file` succeeds but the file on disk is unchanged, the container sees a different filesystem: check the bind mount and the path prefix in your tool.

---

#### Part 4: Compare on the Table

**Goal:** Fill one table from the two traces, with every cell pointing at a line.

Copy this table into `docs/comparison.md` and fill every cell.  A cell holds a count or a short quote and a trace line number, in the form `01:L42`.  No cell may hold an impression.

| Row | Coding agent (opencode) | Cowork agent (Open WebUI) |
|-----|-------------------------|---------------------------|
| Steps taken (model turns or tool calls) | | |
| Files touched (read and written, from the trace and the diff) | | |
| Checks run by the agent itself (tests, syntax, running the script) | | |
| Tokens, if the tool shows them | | |
| Where it asked permission (quote each gate) | | |
| What it got wrong, and which done-when item caught it | | |

Then write the analysis under the table, one short paragraph per row.  For each difference, say which of two causes explains it: who ran the action (the harness with a gate, or the model calling a tool directly) or what the harness told the model before your prompt arrived.  If tokens were not visible in one tool, say so rather than estimating.  Close by putting the two diffs side by side (`diff transcripts/01-coding-agent.diff transcripts/02-cowork-agent.diff`) and saying which one you would merge, and what in the diff, not in the agent's summary, decided that.

---

#### Part 5: Write the One-Page Comparison

**Goal:** Say which paradigm fits which kind of task, and why, in one page.

Write `docs/writeup.md`, at most one page, with these sections in this order:

1.  **The task and the prompt**, quoted, with the four done-when items.
2.  **What happened**, two sentences per run, citing the traces.
3.  **Which paradigm fits which kind of task.**  Commit to an answer.  A useful shape: name one kind of task where the gates of a coding agent earn their cost, and one kind where a general agent's reach is the whole point, and connect each to a row of the table.
4.  **Versions and settings:** model tag, temperature, opencode version, Open WebUI version.

The comparison is graded on whether it follows from the table.  A recommendation that the table does not support is a paragraph, not a finding.

---

#### Deliverables

Fold these into the core lab's submission ZIP and name the direction at the top of your readme.

| File | Description |
|------|-------------|
| `docs/task.md` | The task and the four-item done-when list, unchanged since before Part 2 |
| `docs/prompt.txt` | The verbatim prompt given to both agents |
| `transcripts/00-baseline.txt` | The saved run before any change |
| `transcripts/01-coding-agent.txt` and `.diff` | The captured opencode session with the four checks appended, and its diff |
| `transcripts/02-cowork-agent.txt` and `.diff` | The exported Open WebUI chat with tool calls and the four checks appended, and its diff |
| The tool source | The Open WebUI tool you wrote for Part 3, as a `.py` file |
| `docs/comparison.md` | The six-row table with trace citations and the per-row analysis |
| `docs/writeup.md` | The one-page comparison |
| Pair log | Continued from the core lab, with timestamped swaps during this direction |

---

#### Reflection Prompts

Answer in complete sentences, and cite a trace line in each answer.

- Which gate, in either trace, would you have removed, and which one would you have added?  What would each change have cost or caught?
- The same model produced both diffs.  Name the largest difference between them and say what in the harness, not in the model, caused it.
- Your file tool in Part 3 had no gate.  What is the smallest change to that tool that would have given the cowork run the one gate you most wanted?
- If collaboration beyond your pair occurred, identify it.  Do you certify that this submission represents your pair's original work?  Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this direction take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

---

#### Self-Check Before You Submit

- [ ] `docs/task.md` states the task in one paragraph and lists exactly four done-when items, each checkable by a command or a file inspection.
- [ ] `docs/prompt.txt` is the same text both agents received, and the writeup quotes it.
- [ ] Both traces are captured, not retyped; each ends with the output of all four checks; both diffs are saved on their own branches from the same baseline.
- [ ] Both runs used the same Ollama tag and temperature, and the versions and settings are recorded in the writeup.
- [ ] Every cell of the six-row table cites a trace line, and the analysis explains each difference by who ran the action or by what the harness said first.
- [ ] The writeup commits to which paradigm fits which kind of task, and the table supports it.
- [ ] The Open WebUI tool source is included, and I read it before enabling it.
- [ ] Pair log continues from the core lab with timestamped swaps.
