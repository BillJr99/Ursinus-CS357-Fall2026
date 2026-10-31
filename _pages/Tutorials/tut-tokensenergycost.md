---
layout: textbook
permalink: /Tutorials/TokensEnergyCost
title: 'CS357: Foundations of Artificial Intelligence - Tokens, Energy, and Cost: Measuring What Your Agent Spends'
info:
  coursenum: CS357
  purpose: "To count the tokens an agent actually spends, from the numbers the model server hands back, and to turn those counts into an energy, carbon, and cost estimate whose every assumption is named, sourced, and replaceable."
  eyebrow: "Tutorial"
  numbering: false
tags:
- tokens
- observability
- responsible-ai
- cost
---

## About This Tutorial

Your teammate writes "our agent use had no cost" because the OpenCode sidebar said `$0.00`.  No one can check that sentence, and it is not true.  A local model still reads and writes every token, and each token costs your machine seconds and draws watts from the wall.  This tutorial shows you how to replace that sentence with numbers that someone else can check against your logs.
{: .tb-lede}

This tutorial is also the how-to guide for **Area 1 of the Responsible AI Report**, which every final-project team submits.  Area 1 is "Environmental Tracking and Token Use" on the [Final Project page](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/FinalProject#the-responsible-ai-report-required-in-every-direction).  Part I counts the tokens in one recorded model response by itself, so you can see where every number comes from.  Part II builds trace lines from those measured numbers and adds them up per run, per task, and per agent.  Part III turns the totals into energy, carbon, and cost, with every assumption written down as a named parameter.  Part IV maps all of it onto the report.

Each part has two paths, and either one is enough:

- **The code path** is plain Python over a saved Ollama JSON response.  Every cell runs as written, with no network and no Ollama.  Run the cells in order in one folder.
- **The no-code path** reads the same counts from OpenCode or Open WebUI and does the arithmetic in a spreadsheet.

Once the practice numbers make sense, try the same steps on runs of a system you choose.  Your team's final project is the obvious choice, but any agent you have run this semester works.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|:-----|:------------------------|:------------------------|
| **Input (prompt) tokens** | The tokens the model read on one call: the system prompt, the history you resent, tool results, and the new question | Ollama's `prompt_eval_count`; OpenCode's input total |
| **Output (completion) tokens** | The tokens the model wrote on one call.  The model writes each one in a separate step, so output tokens cost far more time than input tokens | Ollama's `eval_count`; OpenCode's output total |
| **Measured versus estimated** | A measured count is the number the model server handed back.  An estimate is one you computed yourself, for example by dividing characters by four.  The report asks for measured counts, and it marks any rows that are not | The `measured` field in every trace line in Part II |
| **Trace line** | One JSON object per model call, with a run identifier, the agent, the model, the token counts, and the time | `trace.jsonl`, the same file the Observability session writes |
| **Named parameter** | An assumption stored under a name, with its unit and its source, so a reader can see it and replace it | The `P` dictionary in Part III, or the Assumptions tab of your spreadsheet |
| **Grid carbon intensity** | Grams of CO2 equivalent emitted per kilowatt-hour of electricity where your machine is plugged in.  It varies by region | `grid_g_per_kwh` in Part III |
| **Hosted price avoided** | Your token counts priced at a comparable hosted model's published rate: the bill you would have paid if you had not run locally | `price_in_per_million` and `price_out_per_million` in Part III |
{: .tb-full}

---

# Part I: One Response, Counted by Hand

## 1.  Where the Counts Come From

You never have to compute a token count.  The model server counts every token it reads and writes, and it hands you the number.  Your job is to read that number, keep it, and add it up.  This semester you can read it in the places below, taken from the [token accounting section of the Observability tutorial](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Observability#token-accounting-counting-what-every-call-spends):

| Where | Input tokens | Output tokens | Also there |
|:--|:--|:--|:--|
| **OpenCode**, the sidebar (`ctrl+x b` if hidden) | The session's running token count, and the share of the context window used | (same panel) | Cost, which reads `$0.00` for a local model |
| **OpenCode**, `opencode stats --days 1 --project ""` | Input, totaled | Output, totaled | Cache reads, cost, tokens per session; add `--models` for a per-model split |
| **OpenCode**, `opencode export <sessionID>` | `tokens.input` on each assistant message | `tokens.output` | `tokens.cache.read`, `agent`, `modelID`; the prompt the model saw is `input` plus `cache.read` |
| **Ollama**, every `/api/chat` or `/api/generate` response | `prompt_eval_count` | `eval_count` | `prompt_eval_duration`, `eval_duration`, `total_duration`, `load_duration`, all in **nanoseconds** |
{: .tb-full}

> Ollama reports every duration in nanoseconds.  A `total_duration` of `2773000000` is 2.773 seconds, not 2,773 seconds.  Divide by one billion before you do anything else with it.
{: .tb-warning data-title="Watch out"}

**To save a response of your own** (this needs Ollama running on your machine; inside the course container, change `localhost` to `host.docker.internal`):

```bash
curl -s http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "In one sentence, what is a token?"}],
  "stream": false
}' > response.json
```

Keep `"stream": false`.  With streaming on, the counts arrive only in the last chunk (the one with `"done": true`).  A helper that keeps only the text loses them.

## 2.  Code Path: Read One Saved Response

The response below comes from step 1 of Model 4 in the *Agents That Talk, Observability, and Handoff Protocols* session, trimmed to its usage fields.  The cell writes it to `response.json`, the same file that the `curl` command above makes.  Then the cell reads the file back, so it runs with no network.  To use your own response, delete the two lines that write the file.

```python
import json

# A recorded Ollama /api/chat response, trimmed to the usage fields.  Every duration is in nanoseconds.
# Writing it to a file stands in for the `curl ... > response.json` you would run on your own machine.
RECORDED = """{"model": "hermes-3", "done": true, "done_reason": "stop",
 "total_duration": 2773000000, "load_duration": 12000000,
 "prompt_eval_count": 412, "prompt_eval_duration": 610000000,
 "eval_count": 41, "eval_duration": 2100000000}"""
with open("response.json", "w") as f:
    f.write(RECORDED)

with open("response.json") as f:
    resp = json.load(f)

NS = 1e9
in_tok = resp["prompt_eval_count"]       # input (prompt) tokens
out_tok = resp["eval_count"]             # output (completion) tokens
read_s = resp["prompt_eval_duration"] / NS
write_s = resp["eval_duration"] / NS
total_s = resp["total_duration"] / NS

print(f"read  {in_tok:>4} input tokens  in {read_s:.2f} s  ({in_tok / read_s:.0f} tokens/s)")
print(f"wrote {out_tok:>4} output tokens in {write_s:.2f} s  ({out_tok / write_s:.1f} tokens/s)")
print(f"total {total_s:.2f} s, and writing was {write_s / total_s:.0%} of it")

# The trace line, built from measured numbers rather than estimates
measured = "prompt_eval_count" in resp and "eval_count" in resp
line = {"run_id": "t-77b0", "task": "T1", "agent": "planner", "model": resp["model"],
        "prompt_tokens": in_tok, "completion_tokens": out_tok,
        "latency_ms": int(total_s * 1000), "finish_reason": resp["done_reason"],
        "measured": measured}
with open("trace.jsonl", "a") as f:
    f.write(json.dumps(line) + "\n")
print(json.dumps(line))
```

It prints:

```
read   412 input tokens  in 0.61 s  (675 tokens/s)
wrote   41 output tokens in 2.10 s  (19.5 tokens/s)
total 2.77 s, and writing was 76% of it
{"run_id": "t-77b0", "task": "T1", "agent": "planner", "model": "hermes-3", "prompt_tokens": 412, "completion_tokens": 41, "latency_ms": 2773, "finish_reason": "stop", "measured": true}
```

The model read ten times as many input tokens in well under a second, but it took two seconds to write forty-one output tokens.  Reading the prompt is one parallel pass, and writing is one pass per token.  Notice also that every number in the trace line came from the response.  Nobody typed in or guessed any of them, and the `measured` field says so.

## 3.  No-Code Path: Read the Same Numbers on Screen

- **OpenCode.**  At the end of a run, open the sidebar (`ctrl+x b`) and write down the session's token count.  Then run `opencode stats --days 1 --project ""` and find the same session's input and output tokens in the totals.  The sidebar's `$0.00` is the bill you avoided, not the energy you spent.
- **Open WebUI.**  When the reply comes from an Ollama model, hover over the small information icon under the reply.  Open WebUI shows the response's usage fields there, including `prompt_eval_count`, `eval_count`, and the durations.  If your version shows nothing there, use OpenCode or the `curl` command above instead.  Do not fill the gap with a guess.

Copy each reading into one row of a spreadsheet.  Use the columns that the report's token table asks for: **run, task, agent, model, input tokens, output tokens, time**.  If your tool does not report time, write down the clock time when the run starts and when it ends.  Label that column as wall-clock time, because it includes time spent in tools as well as in the model.

### Questions to Work Through

1.  Use the two speeds from the cell to predict how long a call with 3,690 input and 512 output tokens should take on the same machine.  Write your prediction down before you look at question 2.

2.  Model 4 in the Observability session logged that call at 8,422 milliseconds.  Compare your prediction with it, and say what the gap suggests: a faster machine, a prompt served partly from cache, or a trace line you should not trust.

    *Hint:* Which of the two speeds dominates your prediction, and which of the two token counts does a cache change?

3.  A streamed response, or a reply from a provider that does not report counts, reaches the Section 2 cell without `prompt_eval_count`.  Which line of the cell fails first?  Is a cell that stops better or worse than one that quietly writes a zero into your token table, and why?

---

# Part II: From One Call to a Whole Run

## 4.  A Trace Line per Call, Summed per Run, Task, and Agent

One response is one call.  A run of your system is many calls, made by several agents across several tasks.  Area 1 asks you to report tokens **per run, per task, and per agent**, so a reader can see which agent or step dominates the cost.  If every call writes one trace line with a `run_id`, a `task`, and an `agent`, each of those totals is the same loop with a different key.

The cell below uses a small practice trace.  The two planner rows are Model 4's two plan steps from the Observability session.  **The two critic rows are made up for practice; they are not measurements.**  Before you run it, predict which agent reads more input tokens and which writes more output tokens.

```python
import json
from collections import defaultdict

# Practice trace: one run, two tasks, two agents.  The planner rows are Model 4's two
# plan steps from the Observability session; the critic rows are made up for practice.
TRACE = """\
{"run_id": "t-77b0", "task": "T1", "agent": "planner", "model": "hermes-3", "prompt_tokens": 412, "completion_tokens": 41, "latency_ms": 2773, "measured": true}
{"run_id": "t-77b0", "task": "T1", "agent": "critic", "model": "hermes-3", "prompt_tokens": 980, "completion_tokens": 60, "latency_ms": 1900, "measured": true}
{"run_id": "t-77b0", "task": "T2", "agent": "planner", "model": "hermes-3", "prompt_tokens": 3690, "completion_tokens": 512, "latency_ms": 8422, "measured": true}
{"run_id": "t-77b0", "task": "T2", "agent": "critic", "model": "hermes-3", "prompt_tokens": 4310, "completion_tokens": 88, "latency_ms": 4600, "measured": true}
"""
with open("practice_trace.jsonl", "w") as f:
    f.write(TRACE)

with open("practice_trace.jsonl") as f:
    rows = [json.loads(line) for line in f if line.strip()]

unmeasured = [r for r in rows if not r.get("measured")]
if unmeasured:
    print(f"WARNING: {len(unmeasured)} rows are estimates, not measurements")

def total_by(key):
    sums = defaultdict(lambda: {"calls": 0, "in": 0, "out": 0, "s": 0.0})
    for r in rows:
        t = sums[r[key]]
        t["calls"] += 1
        t["in"] += r["prompt_tokens"]
        t["out"] += r["completion_tokens"]
        t["s"] += r["latency_ms"] / 1000
    return sums

for key in ["run_id", "task", "agent"]:
    print(f"\nper {key}")
    print(f"{key:<8} {'calls':>5} {'input':>7} {'output':>7} {'seconds':>8}")
    for name, t in total_by(key).items():
        print(f"{name:<8} {t['calls']:>5} {t['in']:>7} {t['out']:>7} {t['s']:>8.1f}")

tasks = total_by("task")
avg_in = sum(t["in"] for t in tasks.values()) / len(tasks)
avg_out = sum(t["out"] for t in tasks.values()) / len(tasks)
print(f"\naverage per task: {avg_in:.0f} input, {avg_out:.0f} output tokens")
```

The run totals 9,392 input and 701 output tokens over 17.7 seconds.  The cell also prints the per-task and per-agent tables and the average per task.  To use your own system, point the `open` call at your own `trace.jsonl` (or at the `token_usage.csv` that the Observability tutorial's `metered` decorator writes) and delete the lines that write the practice file.  If your trace has more than one run, the `run_id` table gets one row per run.

## 5.  No-Code Path: Totals in the Spreadsheet

Put one call (or, from OpenCode, one session) per row in a tab named **Tokens**, with the columns from Section 3.  Then:

- **Per run:** `=SUMIF(A:A, "t-77b0", E:E)` totals the input tokens of run `t-77b0` when column A is the run and column E is input tokens.  Change the column letter for output tokens and time.
- **Per task and per agent:** the same `SUMIF`, with the condition on the task column or the agent column.  A pivot table does all three at once if you know how to make one.  It is optional.
- **Average per task:** the per-task totals divided by the number of tasks.

OpenCode's sidebar and `opencode stats` give you totals per session, not per agent.  If your system has several agents and you are on the no-code path, give each agent its own rows.  Run each agent in its own session, or read the counts for each reply in Open WebUI.

### Questions to Work Through

4.  Check the prediction you made before running the cell.  Which agent read more input tokens, and which wrote more output tokens?  What does high input with low output suggest that agent is being sent?

    *Hint:* Question 11 of the Observability tutorial asks the same thing about a critic that uses 70% of the input tokens.  Does a critic need the whole transcript, or only the draft it is judging?

5.  Task T2 cost far more than task T1.  Using the [Memory and Context tutorial](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/MemoryAndContext), say where you would expect the extra input tokens to come from, and which column of your table would show a fix working.

6.  One teammate's rows come from OpenCode and another's from a characters-divided-by-four estimate.  What should the report's token table say about those rows, and why does the `measured` field exist?
{: start="4"}

---

# Part III: From Tokens to Energy, Carbon, and Cost

## 6.  Every Assumption Gets a Name

Each conversion is one multiplication by an assumption.  That is fine, but a hidden assumption is not.  The method comes from Part VII of the [Training Data, Bias, IP, Privacy, Governance, and the Cost of Inference](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-biasdata.md) session, which Area 1 points to:

- **Energy** is measured generation time multiplied by your machine's power draw under load.
- **Carbon** is that energy multiplied by your region's grid carbon intensity.  The Cost of Inference session also asks you to compute it a second way, as tokens multiplied by a per-token rate, and to report both.
- **Cost** is the token count priced at a comparable hosted model's published rate (the bill you avoided by running locally), plus the electricity.

Here is where each parameter's value comes from, and which ones you must find yourself:

| Parameter | Unit | Value in the cell | Where it comes from |
|:--|:--|:--|:--|
| `machine_watts` | watts | **blank, you fill it** | No course source.  Measure your machine under load (a plug-in meter, `nvidia-smi`, or `powermetrics` on a Mac) and say how |
| `grid_g_per_kwh` | g CO2e per kWh | 770.9 lb per MWh, converted | EPA eGRID2023 U.S. total output rate, as cited in Part VII of the Cost of Inference session.  Replace it with your region's rate from the EPA Power Profiler (epa.gov/egrid/power-profiler) |
| `g_per_input_token`, `g_per_output_token` | g CO2e per token | 5.3e-7 and 1.6e-6 | The offline profile in the course's [`energy-profiles.json`](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/deliberation-harness/config/energy-profiles.json), derived from a 0.0005 g per local query midpoint; the file names its sources |
| `price_in_per_million`, `price_out_per_million` | dollars per million tokens | **blank, you fill it** | Look up a comparable hosted model's published price.  Write down the model, the page, and the date you read it |
| `dollars_per_kwh` | dollars per kWh | **blank, you fill it** | The rate on your electricity bill |
{: .tb-full}

## 7.  Code Path: The Estimate

The cell takes the run totals from Part II and leaves every unsourced parameter as `None`.  It computes whatever it can from the parameters that have values, and it lists the ones still missing instead of inventing them.

```python
# Run t-77b0, totaled in the previous cell
input_tokens = 9392
output_tokens = 701
generation_seconds = 17.695

# ---- Parameters: every assumption has a name, a unit, and a source.  Replace them. ----
LB_TO_G = 453.592
P = {
    # MEASURE: no source in the course gives your machine's draw.  Use a plug-in meter,
    # nvidia-smi, or powermetrics on a Mac, and write down which.
    "machine_watts": None,
    # SOURCE: EPA eGRID2023 U.S. total output rate, 770.9 lb CO2e/MWh, as cited in Part VII
    # of the Cost of Inference session.  Replace with your region (epa.gov/egrid/power-profiler).
    "grid_g_per_kwh": 770.9 * LB_TO_G / 1000,
    # SOURCE: energy-profiles.json, offline profile (0.0005 g per local query midpoint).
    "g_per_input_token": 5.3e-7,
    "g_per_output_token": 1.6e-6,
    # LOOK UP: a comparable hosted model's published price, in dollars per million tokens.
    # Write down the model, the page, and the date you read it.
    "price_in_per_million": None,
    "price_out_per_million": None,
    # LOOK UP: the rate on your electricity bill, in dollars per kWh.
    "dollars_per_kwh": None,
}

missing = [name for name, value in P.items() if value is None]

def need(*names):
    """True only when every named parameter has a value."""
    return all(P[n] is not None for n in names)

kwh = None
if need("machine_watts"):
    kwh = P["machine_watts"] * generation_seconds / 3600 / 1000
    print(f"Energy: {kwh * 1000:.3f} Wh")
    print(f"Carbon from measured time: {kwh * P['grid_g_per_kwh']:.4f} g CO2e")

carbon_tokens = input_tokens * P["g_per_input_token"] + output_tokens * P["g_per_output_token"]
print(f"Carbon from per-token rates: {carbon_tokens:.4f} g CO2e")

if need("price_in_per_million", "price_out_per_million"):
    hosted = (input_tokens / 1e6) * P["price_in_per_million"] + (output_tokens / 1e6) * P["price_out_per_million"]
    print(f"Hosted price avoided: ${hosted:.4f}")
if kwh is not None and need("dollars_per_kwh"):
    print(f"Electricity: ${kwh * P['dollars_per_kwh']:.6f}")

print(f"grid intensity in use: {P['grid_g_per_kwh']:.1f} g CO2e per kWh")
print("still to fill and source:", ", ".join(missing) if missing else "nothing")
```

As shipped, the cell can compute only the per-token carbon line.  It prints that line and then names the four parameters you still have to fill and source.  Fill in your measured wattage, and the energy and time-based carbon lines appear.  Fill in a price, and the hosted price line appears.  Change nothing else.  If the two carbon figures disagree, that is a finding, not a bug.  Report both, and say which assumption drives the gap.

The course's [`token_meter.py`](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/deliberation-harness/tools/token_meter.py) computes the per-token part from an Ollama response.  It also adds a share of the model's one-time training emissions.  That share is optional for Area 1.  If you include it, say in your report that `energy-profiles.json` itself calls its lifetime-request denominator an assumption.

## 8.  No-Code Path: An Assumptions Tab

Add a second tab named **Assumptions** with four columns: **name, value, unit, source**.  Put each parameter from the table in Section 6 on its own row.  Leave a value blank until you have a source for it.  Then name each value cell with the parameter names above (in Google Sheets, Data > Named ranges; in Excel, Formulas > Define Name), so the formulas read like the code:

| Result | Formula, for a row where E is input tokens, F is output tokens, and G is seconds |
|:--|:--|
| Energy (kWh) | `=G2*machine_watts/3600/1000` |
| Carbon from time (g) | `=H2*grid_g_per_kwh`, where H holds the energy |
| Carbon from tokens (g) | `=E2*g_per_input_token + F2*g_per_output_token` |
| Hosted price avoided ($) | `=E2/1000000*price_in_per_million + F2/1000000*price_out_per_million` |
| Electricity ($) | `=H2*dollars_per_kwh` |
{: .tb-full}

A blank assumption shows up as a zero or an error in every cell that uses it.  That is how the spreadsheet tells you which values still need a source.  Do not type a number into a formula.  Anyone who wants to check your estimate should be able to change one cell on the Assumptions tab and see every total change.

### Questions to Work Through

7.  Before you fill in `machine_watts`, predict whether the time-based and token-based carbon figures will agree to within a factor of two.  Then fill it in with your own measured number and check.

8.  Which parameter in the table has the most assumptions between it and the thing it describes?  Which one could you settle with a single measurement?

    *Hint:* The per-token rate was derived from a per-query band, not from your machine.  Your wattage can be read off a meter.

9.  The estimate for one run is a fraction of a gram.  What do you multiply it by before it is a number a policy could govern?
{: start="7"}

> "The dashboard said $0.00, so the run was free."  The token count is the same whether or not anyone bills for it.  That is why the report asks for tokens rather than dollars, and then converts them to energy, carbon, and cost with every assumption stated.
{: .tb-pitfall data-title="Common Misconception"}

---

# Part IV: Your Area 1 Write-Up

## 9.  What the Report Asks For

Area 1 asks for four things, and its evidence list has three items.  Here they are with the part of this tutorial that produces each one:

| Area 1 requires | What you submit | Made in |
|:--|:--|:--|
| **Count the tokens**: input and output for every evaluation run, from OpenCode's session display or Ollama's `prompt_eval_count` and `eval_count`, with `eval_duration` and `total_duration` for time | A token table with the columns run, task, agent, model, input tokens, output tokens, time | Part I |
| **Total and average them**: tokens per run, per task, and per agent | The same table, with the totals and the average per task | Part II |
| **Estimate energy, carbon, and cost**, stating and citing every assumption; an order-of-magnitude estimate is acceptable, a hidden assumption is not | The estimate with its assumptions and sources | Part III |
| **Compare one alternative**: a smaller model, fewer agents, a shorter context, or the monolith baseline, and say whether the difference in quality justifies the difference in cost | The comparison | Exercise 3 below |
{: .tb-full}

For each of the four areas, the report's deliverables also ask for at least one change that the team made, or deliberately declined to make, because of what it measured.  For Area 1, that change usually comes from the comparison.

**How it fits your direction.**  The Final Project page says what to measure in each direction:

- **Direction A:** run it on the frozen 10-task evaluation set, for both the monolith baseline and the multi-agent system, so the token and cost comparison sits beside the accuracy comparison.
- **Direction B:** count the tokens of your team's own AI use: the model you probed during adversarial probing and any AI tools you used in the research.  Do not count the audited system.
- **Direction C:** run it on the published artifact, using its worked examples and property-test inputs, and publish the token figures in the README or in GOVERNANCE.md's known limitations.  In the contribution variant, measure the feature you contributed.

> Start measuring in Sprint 1.  You cannot rebuild token counts from memory in week 14.  The Final Project page also says that a report assembled at the end from a single run cannot score above beginning.  Your proposal's Responsible AI measurement plan already names how you will count tokens and who owns this area.  This tutorial shows that person how to do it.
{: .tb-warning data-title="Watch out"}

On Demo Day, the technical segment shows the token and cost table next to your evaluation results, and the stakeholder segment gives one plain-language sentence about what the system costs to run.

---

## Exercises

Everything below is optional.  This is a tutorial, so nothing here is collected or graded.  If you are on a final-project team, though, keep this work: it is the start of your Area 1 evidence.

1.  **Count one response of your own.**

    *What to do:* Save one Ollama response with the `curl` command in Section 1 (or read one reply's counts in Open WebUI or OpenCode), and put it through the Section 2 cell or one row of your spreadsheet.

    *Starter hint:* In the Section 2 cell, delete the two lines that write `RECORDED` to the file, and the cell reads your `response.json` instead.

    *You've succeeded when:* You have one trace line or spreadsheet row whose token counts and time came from the response, not from you, and you can say how many tokens per second your machine read and wrote.

2.  **Total a real run of a system you choose.**

    *What to do:* Pick a system you can run several times: your team's final project, or any agent from this semester.  Run it at least three times on the same tasks, and record every call with a `run_id`, `task`, and `agent`.

    *Starter hint:* The Observability tutorial's `metered` decorator writes these rows to `token_usage.csv` without changing your agent loop.  On the no-code path, one row per OpenCode session or Open WebUI reply is enough.

    *You've succeeded when:* You have a token table with the columns run, task, agent, model, input tokens, output tokens, and time, plus totals per run, per task, and per agent, and the average per task.  Every row is either measured or marked as an estimate.

3.  **Fill the parameters, and compare one cheaper option.**

    *What to do:* Fill every blank parameter in Section 6 with a value you measured or looked up, and write its source beside it.  Then run the same tasks with one cheaper option (a smaller model, fewer agents, a shorter context, or the monolith baseline) and estimate both.

    *Starter hint:* For the price, name the hosted model you chose as comparable and the date you read its price page.  For the cheaper option, keep the tasks identical, so the only thing that changes is the option.

    *You've succeeded when:* A reader can change any one assumption and recompute your estimate, and you can say in one sentence whether the difference in quality between the two options justifies the difference in cost.

---

## Reflection Prompt

**Personal level:** In your notebook: before this tutorial, how much did you think one evening of agent work cost in energy?  What number would you now put in its place, and which assumption are you least sure of?

**Technical level:** Your estimate has two carbon figures that may disagree.  Which one would you defend to an auditor, and what one measurement would change your mind?

**Societal level:** A local model has no invoice, so its cost is easy to leave out of a report.  Who pays the cost of a run that no one bills for, and who should be told about it?

---

## Further Reading

- This course: [Agent Observability and Tracing](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Observability), especially its [token accounting section](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Observability#token-accounting-counting-what-every-call-spends), with `token_usage.py`, the `metered` decorator, and the `opencode export` script.
- This course: [Agents That Talk, Observability, and Handoff Protocols](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-observability.md), whose Extension "Counting Tokens, the Number Under Every Cost" is where the response in Part I comes from.
- This course: [Training Data, Bias, IP, Privacy, Governance, and the Cost of Inference](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-biasdata.md), Part VII, for the method and the orders of magnitude behind it.
- This course: [The Responsible AI Report](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/FinalProject#the-responsible-ai-report-required-in-every-direction) on the Final Project page, and the Responsible AI measurement plan on the [Final Project Proposal](https://www.billmongan.com/Ursinus-CS357-Fall2026/Projects/FinalProjectProposal) page.
- This course: [Memory and the Small Context Window Principle](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/MemoryAndContext), for why input tokens grow as an agent resends its history.
- This course: the deliberation harness's [`energy-profiles.json`](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/deliberation-harness/config/energy-profiles.json) and [`token_meter.py`](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/agent-templates/deliberation-harness/tools/token_meter.py).
- Ollama API, usage fields: https://docs.ollama.com/api/usage
- opencode CLI reference, including `stats`, `export`, and `session list`: https://opencode.ai/docs/cli/
- Patterson, D. et al. "Carbon Emissions and Large Neural Network Training."  *arXiv* 2104.10350 (2021).
- Strubell, E., Ganesh, A., and McCallum, A. "Energy and Policy Considerations for Deep Learning in NLP." *ACL* (2019).
