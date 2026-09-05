<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-rubricworkshop.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-rubricworkshop.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Evaluating Agents With a Rubric: The Judge Pipeline Workshop

Today is a build session.  You leave with a judge that reads a rubric, scores three sample submissions with your local model, and writes a `grades.csv` you can open in a spreadsheet, and then with the same judge expressed a second time as a promptfoo configuration with no Python at all.  Last session (*Critique, Consensus, and the LLM Judge*) taught why vague rubrics fail and what biases a judge carries; today you run the machinery, so keep that deck open for the rubric autopsy and the pathology list rather than re-reading them here.  Two deliverables meet today: the *Design Your Agent System* written assignment is due, and the [Rubric Pipeline Lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RubricPipeline) is handed out; everything you build in the next seventy-five minutes is the first hour of that lab.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.  Today one laptop per team runs the code; rotate who types at each Part.

---

## Key Concepts

| Term | Plain-English Definition | Where You Meet It Today |
|---|---|---|
| **Judge** | A model prompted with a rubric and an artifact that returns a score per criterion, in a fixed structured format, instead of prose. | The `judge()` function in Part I. |
| **Rubric as data** | The rubric written as a JSON object (criteria, weights, level descriptions) so the same file feeds the prompt, the scoring arithmetic, and the CSV header. | `RUBRIC` at the top of the code cell. |
| **Fail closed** | When the judge's output cannot be parsed, the pipeline flags the row for a human instead of guessing a score. | The `PARSE_ERROR` flag in the batch loop. |
| **Evidence check** | A mechanical test that the sentence the judge quoted actually appears in the submission. | The `_quote_found` column in `grades.csv`. |
| **promptfoo and the `llm-rubric` assertion** | A command-line harness that runs prompts and assertions from a YAML file; `llm-rubric` hands a rubric sentence and the output to a judge model and records PASS or FAIL. | Part II, three assertions, one per criterion. |
| **Percent agreement** | The share of (sample, criterion) cells where the judge's level matches the human's. | Part III, nine cells. |
| **Verbosity bias** | A judge scoring a longer answer higher when the added length carries no rubric-relevant content. | The padding probe in Part III. |

### Before You Start

**You need** Ollama running with `llama3.2` pulled, Python with `requests` installed (every lab so far), and Node.js for Part II (promptfoo runs through `npx`, so nothing else to install).  Check all three now:

```bash
curl http://localhost:11434/api/tags
python3 -c "import requests; print('requests ok')"
npx promptfoo@latest --version
```

If you work inside the course container from *Your AI Workbench*, use `host.docker.internal:11434` wherever this deck says `localhost:11434`.  The model must return JSON: `llama3.2` does when the system prompt demands it, and if it wraps the JSON in a code fence, the cell strips the fence before parsing.

**Create the three sample submissions.**  Make a folder `samples/` and save each block below as the named file.  All three argue about library hours; they are written to land at different rubric levels, and the differences are deliberate.

`samples/s01.txt`:

```text
The library should stay open until 2 a.m. during finals week. Seventy-one percent of students surveyed last spring said they studied past midnight at least three times during finals (Student Life Survey, 2025). Late closing also cuts noise complaints in the residence halls, which rose 40 percent during finals last year (Residence Life Report, 2025). Some argue the added staffing costs too much, but two student workers for four extra hours cost less than one noise incident investigation. The extension is cheap, and it is what students already need.
```

`samples/s02.txt`:

```text
I think the library should probably stay open later during finals. A lot of people study late and it would help them. Some students have said they wish it was open longer. It might cost a bit more, but that is probably worth it.
```

`samples/s03.txt`:

```text
Finals week is stressful for everyone. There are many places to study on campus, and each has its own advantages. The library is a nice building with good lighting. Everyone should find the study spot that works best for them.
```

**What you will have at the end:** `grades.csv` from the code route, `grades_promptfoo.csv` from the no-code route, a nine-cell agreement score against your own hand grades, and one measured bias number.

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Before You Start: checks pass, three sample files exist, hand-score the samples before any model sees them |
| 10-35 | Part I, the pipeline in one pass: rubric, judge, batch loop, read `grades.csv` |
| 35-50 | Part II, the same pipeline as a promptfoo config, then compare the two CSVs |
| 50-70 | Part III, make it trustworthy: agreement, the padding probe, the disagreement table |
| 70-75 | Presenters report out: your agreement number and your padding delta |

---
# Part I: The Pipeline in One Pass

The idea in one sentence: a rubric is data, so the same JSON object can be shown to the model, used to compute the weighted total, and used to name the CSV columns.  You will run the judge from last session unchanged, then wrap it in a loop over the `samples/` folder.

## 1.  Hand-Score First

Before you run anything, each teammate writes down a level (1 to 4) for each sample on each of the three criteria below, using only the level descriptions in the rubric.  Do not discuss yet; you compare in Part III.  This order matters because seeing the judge's score first anchors yours.

## Model 1: The Rubric as a JSON Schema

Read the `RUBRIC` object at the top of the code cell before you read the function.  Three criteria, weights summing to 100, and four levels each described by something you can see in the text (a citation, a stated position, a rebuttal).  The weighted total is $\text{total} = \sum_{c} w_c \cdot \ell_c / 4$, where $w_c$ is the weight and $\ell_c$ the level the judge awarded, the formula last session derived.  Every other piece of the pipeline reads from this object: the system prompt embeds it, the total loops over `rubric["criteria"]`, and the batch loop below builds column names from `c["name"]`.  Change the rubric and nothing else needs editing; that is the whole reason to write it as data rather than as sentences in a prompt.

### Critical Thinking Questions

1.  Predict before running: for each sample, which level will the judge award on `claims_cited`?  Write the three numbers down.  Then state which sample you expect the judge to get *wrong* and on which criterion.

   *Hint:* `s02` says "some students have said" without naming a source.  Is that "some claims cite evidence" (level 2) or "no claims cite evidence" (level 1)?  The descriptor does not say what counts as evidence, and that gap is where you and the judge will diverge.

2.  The system prompt asks for a quoted sentence per score.  Which column in the batch loop below checks that quote, and what does a `False` in that column tell you that a low score does not?

   *Hint:* A low score says the essay is weak.  A quote that does not appear in the essay says the *judge* is unreliable on that row, whatever the score.

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Save it as `judge.py` in the folder that contains `samples/`.

```python
import json
import requests

RUBRIC = {
  "criteria": [
    {"name": "claims_cited", "weight": 50,
     "levels": {"1": "no claims cite evidence", "2": "some claims cite evidence",
                "3": "most claims cite evidence", "4": "every claim cites evidence"}},
    {"name": "directness", "weight": 30,
     "levels": {"1": "never states a position", "2": "position implied",
                "3": "position stated", "4": "position stated in the first sentence"}},
    {"name": "counterargument", "weight": 20,
     "levels": {"1": "absent", "2": "mentioned", "3": "engaged", "4": "engaged and rebutted"}},
  ]
}

def judge(artifact, rubric=RUBRIC, model="llama3.2"):
    system = ("You are a strict grader. Score the artifact on EACH criterion by choosing a level 1-4 "
              "that matches the level descriptions. Quote the sentence that justifies each score. "
              "Respond ONLY with JSON: "
              '{"scores": {"<criterion>": {"level": int, "evidence": str}}}')
    user = f"RUBRIC:\n{json.dumps(rubric, indent=1)}\n\nARTIFACT:\n{artifact}"
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": 0.0, "seed": 42},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=180)
        raw = r.json()["message"]["content"]
        data = json.loads(raw.replace("```json", "").replace("```", ""))
        total = sum(c["weight"] * data["scores"][c["name"]]["level"] / 4
                    for c in rubric["criteria"])
        return total, data
    except Exception as e:
        print(f"[judge:parse] {e}")
        import traceback; traceback.print_exc()
        return None, {"error": str(e)}

essay = ("Campus dining should extend weekend hours. The biggest reason is that 64 percent of "
         "surveyed students reported missing breakfast on Saturdays (Dining Survey, 2025). "
         "Some argue costs would rise, but the survey shows staffing two extra hours costs less "
         "than the lost meal-plan value. Therefore the change pays for itself.")

total, detail = judge(essay)
print(f"weighted score: {total}/100")
print(json.dumps(detail, indent=1))
```

Run `python3 judge.py` once and confirm you get a weighted score and a JSON block for the dining essay.  Then append the batch loop below to the bottom of `judge.py` and run it again.  It walks `samples/`, calls `judge()` on each file, fails closed on a parse error, checks every quoted sentence against the source, and writes `grades.csv`.

```python
import csv
import os

rows = []
for name in sorted(os.listdir("samples")):
    text = open(os.path.join("samples", name)).read()
    total, detail = judge(text)
    row = {"filename": name, "total": total, "flag": ""}
    if total is None:
        row["flag"] = "PARSE_ERROR"   # fail closed: a human reads this row, nobody guesses
    for c in RUBRIC["criteria"]:
        s = detail.get("scores", {}).get(c["name"], {})
        row[c["name"] + "_level"] = s.get("level", "")
        row[c["name"] + "_evidence"] = s.get("evidence", "")
        row[c["name"] + "_quote_found"] = s.get("evidence", "") in text
    rows.append(row)

with open("grades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
```

## 2.  Read grades.csv

Open `grades.csv` in a spreadsheet or with `column -s, -t grades.csv`.  One row per sample; per criterion a level, the quoted evidence, and whether that quote was found verbatim in the file; a weighted total; and a flag column that is empty unless the judge's output failed to parse.  Check three things in this order: (1) no row is flagged, (2) every `_quote_found` is `True`, (3) the totals rank `s01` above `s02` above `s03`.  If any check fails, note which one; you diagnose it in Part III.

Recap: the rubric is one JSON object that drives the prompt, the arithmetic, and the CSV shape.  The batch loop adds only three behaviors of its own: walk a folder, fail closed, and verify quotes.

---
# Part II: The Same Pipeline Without Code

promptfoo lets you say the same thing in a configuration file: here are the outputs, here is the judge, here are the assertions, run them all.  The Rubric Pipeline Lab's Direction 0 takes this route end to end; today you take it far enough to see that the two routes measure the same thing.

## 3.  Wire promptfoo to Ollama

In the same folder, run the smoke test from the lab, which asks the model one question and asserts on the answer.  Save this as `promptfooconfig.yaml`:

```yaml
# smoke-test promptfooconfig.yaml - verify Ollama connectivity
description: "Rubric Pipeline Lab Direction 0 smoke test"

prompts:
  - "Reply with exactly one word: the capital of France."

providers:
  - ollama:chat:llama3.2

tests:
  - assert:
      - type: contains
        value: "Paris"
```

Run it:

```bash
npx promptfoo@latest eval
npx promptfoo@latest view   # opens the results viewer in your browser
```

Expected: 1 test, 1 pass.  If promptfoo cannot reach Ollama, confirm `ollama serve` is running and that `curl http://localhost:11434/api/tags` responds; promptfoo reads the base URL from the `OLLAMA_BASE_URL` environment variable if your Ollama runs elsewhere.

## Model 2: The Rubric as promptfoo Assertions

Two files replace the batch loop.  The first is `dataset.csv`, one row per sample with columns `id` and `answer`; build it from the same `samples/` folder so both routes grade identical text:

```python
import csv
import os

with open("dataset.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "answer"])
    for name in sorted(os.listdir("samples")):
        w.writerow([name.removesuffix(".txt"),
                    open(os.path.join("samples", name)).read().strip()])
```

The second is the config.  Its prompt is a template that echoes each stored answer straight through, so the judge grades your dataset rather than a freshly generated reply.  promptfoo's template syntax is the variable name inside two pairs of curly braces (the form you saw on the lab's Direction 0 page); create that one-line file with the command below rather than typing it, then save the YAML as `promptfooconfig-rubric.yaml`:

```bash
python3 -c "print('{' * 2 + 'answer' + '}' * 2)" > prompt.txt
```

```yaml
# promptfooconfig-rubric.yaml
# Judge: ollama llama3.2, temperature 0
description: "Rubric Workshop: the three-criterion rubric as promptfoo assertions"

prompts:
  - file://prompt.txt

providers:
  - echo

defaultTest:
  options:
    # The judge model that grades every llm-rubric assertion:
    provider: ollama:chat:llama3.2
  assert:
    - type: llm-rubric
      value: >
        Criterion claims_cited: PASS only if most or every factual claim in the
        answer cites evidence (a named source, survey, or report). FAIL otherwise.
    - type: llm-rubric
      value: >
        Criterion directness: PASS only if the answer states its position outright,
        anywhere in the text. FAIL if the position is only implied or never stated.
    - type: llm-rubric
      value: >
        Criterion counterargument: PASS only if the answer engages an opposing view
        in a full sentence, with or without a rebuttal. FAIL if the opposing view is
        absent or mentioned only in passing.

tests: file://dataset.csv
```

Read the three `value:` blocks against `RUBRIC`.  Each one collapses four levels to a single line: PASS means level 3 or 4, FAIL means level 1 or 2.  That is the only translation between the two routes, and it is lossy on purpose; promptfoo answers "good enough?" while the code route answers "how good?".

Run it and write the results as a CSV:

```bash
npx promptfoo@latest eval -c promptfooconfig-rubric.yaml --output grades_promptfoo.csv
npx promptfoo@latest view
```

Expected: 3 rows times 3 assertions, nine verdicts.

### Critical Thinking Questions

3.  Predict before running: which of the nine verdicts will be PASS?  Derive your answer from `grades.csv` alone (level 3 or 4 means PASS), then run and count the cells where the promptfoo verdict disagrees with the level the code route awarded.

   *Hint:* The same model read the same text under two different prompts.  Disagreement between the routes is not a bug in either one; it measures how much the *wording* of the rubric line moves the judge.

Recap: the promptfoo YAML is the rubric with each criterion collapsed to a pass line, and both routes grade the same `samples/` with the same model.  A configuration file is not more accurate than a script; what it buys you is one file holding rubric, judge, and tests that you can diff, which is the Part 5 harness discipline in the lab.

---
# Part III: Make It Trustworthy

A judge that runs is not yet a judge you can use.  Two checks make it trustworthy enough to hand in: agreement with a human score, and a controlled probe for one known bias.  The lab asks for both at larger scale (a calibration set, Cohen's kappa, and a bias study); today you run each once so the shape is familiar.

## 4.  Agreement With Your Hand Scores

Bring back the levels you wrote down in Section 1.  Where teammates disagree with each other, talk it through and record one consensus level, but keep the original marks; human-to-human disagreement is a finding.  Then compute percent agreement as the number of cells where the consensus level equals the judge's level, divided by 9, times 100, and report it overall and per criterion (three cells each).  A criterion at 1 of 3 is telling you its descriptor is ambiguous, not that the model is stupid.

## 5.  One Bias Probe: Padding

Append the two content-free sentences below to `judge.py` and run it.  They add no citation, no position, and no counterargument, so a rubric-faithful judge returns the same three levels before and after.

```python
PAD = ("This essay was written with great care and attention to detail.  "
       "The author is deeply knowledgeable about campus issues.")
text = open("samples/s02.txt").read()
before, detail_before = judge(text)
after, detail_after = judge(text + " " + PAD)
print("s02 before padding:", before, " after padding:", after)
for c in RUBRIC["criteria"]:
    print(c["name"], detail_before["scores"][c["name"]]["level"],
          "->", detail_after["scores"][c["name"]]["level"])
```

Record the delta per criterion.  Any criterion that moves up is verbosity bias, measured; the padded sentences even praise the author, so a move is also the judge reading tone instead of the text.  A delta of zero on three cells does not clear the judge; it is one sample, one padding string, one model, and the lab asks for the larger study.

## Model 3: The Disagreement Table

The human column holds the levels the three samples were written to land on; check them against your own consensus before you trust them.  Fill the judge columns from `grades.csv` and the padding run, and the promptfoo column from `grades_promptfoo.csv`.

| Sample | Criterion | Human level (as designed) | Judge level | Judge level, padded | promptfoo verdict | Gap (human minus judge) |
|---|---|---|---|---|---|---|
| s01 | claims_cited | 4 | | | | |
| s01 | directness | 4 | | | | |
| s01 | counterargument | 4 | | | | |
| s02 | claims_cited | 2 | | | | |
| s02 | directness | 3 | | | | |
| s02 | counterargument | 2 | | | | |
| s03 | claims_cited | 1 | | | | |
| s03 | directness | 1 | | | | |
| s03 | counterargument | 1 | | | | |

Only `s02` has a padded value today.  The row with the largest gap is the row you revise.

### Critical Thinking Questions

4.  Predict before filling the table: which row will show the largest gap?  Defend the prediction with a quote from the sample and a quote from the level descriptor.

   *Hint:* `s02` says "it might cost a bit more, but that is probably worth it."  Is that a counterargument "mentioned" (level 2) or "engaged" (level 3)?  The descriptor has one word to decide with.

5.  Take the worst row and rewrite that criterion's level descriptors so the disagreement could not happen: name the countable feature (a source in parentheses, an opposing view in a full sentence, a rebuttal that gives a reason).  Re-run `judge.py` with the revised `RUBRIC` and report agreement on that criterion before and after.

   *Hint:* Revise the descriptor, not the sample.  The lab grades the revise-and-remeasure step, not the first number.

Recap: agreement tells you whether the rubric wording means the same thing to you and the model; the padding probe tells you whether the model is reading the text or its length.  Both numbers, with the revision they prompted, are the core of the lab writeup.

---

## 6.  Exercises

1.  *Twelve samples.*

   - *What to do*: The lab needs at least twelve synthetic submissions including an empty file and an off-topic one.  Write nine more into `samples/`, re-run `judge.py`, and confirm the empty file produces a flagged row rather than a score.
   - *Starter hint*: An empty artifact gives the judge nothing to quote; watch whether it invents evidence or fails to parse.  Either is a finding.
   - *You've succeeded when*: `grades.csv` has twelve rows, every `_quote_found` on a non-empty file is `True`, and the empty file's row is flagged or scored all ones with a reason you can state.

2.  *Four criteria.*

   - *What to do*: Add a fourth criterion to `RUBRIC` (a conclusion sentence is a good candidate; the lab's example rubric has one) with weights that still sum to 100, and add the matching `llm-rubric` block to the YAML.
   - *Starter hint*: Nothing else in `judge.py` changes; that is the payoff of the rubric as data.  Count how many lines the YAML change took.
   - *You've succeeded when*: Both CSVs grow by one criterion and the weighted totals still fall between 0 and 100.

3.  *Regression tripwire.*

   - *What to do*: Delete the sentence "Quote the sentence that justifies each score." from the system prompt, re-run, and look at the `_quote_found` column.  Then restore it.
   - *Starter hint*: This is Part 5 of the lab in miniature: a deliberate degradation, a measurable drop, a recovery.
   - *You've succeeded when*: You can show the column before, during, and after, and say in one sentence what a versioned config would have caught.

---

## Reflection Prompt

*Personal:* You hand-scored three paragraphs today and then compared yourself to a model.  On which criterion did you and a teammate disagree, and did reading the judge's quoted evidence change your mind or dig you in?  Write two sentences on what that tells you about using a judge on your own work.

*Technical:* Your pipeline produces a level, a quote, and a `_quote_found` flag per criterion.  Name the smallest set of numbers you would need to see before you let this judge grade a class of forty, and state the threshold for each.  Say what you would do if one criterion passes the threshold and another fails.

*Societal:* The judge you built runs on your laptop against text you wrote.  The same architecture scores admissions essays and job applications elsewhere.  What changes about the calibration step when the submissions come from real people who cannot see the rubric, and who should be required to publish the agreement numbers?

---

-> Coming Up Next: *Training Data, Bias, and Explainability* (Tue Nov 10) follows the judge's preferences back to where they came from: the corpus the model learned from, and what it means to deploy a scoring system trained on it.  Then *Evaluation Workshop II: Run Your Rubric Against Your Project* (Thu Nov 19) brings today's judge to your own project outputs, so keep `judge.py`, both YAML files, and your disagreement table where you can find them.

---

## Further Reading

- [promptfoo documentation](https://www.promptfoo.dev/docs/intro/): the harness from Part II, including the full list of assertion types and the results viewer.
- Hamel Husain, ["Your AI Product Needs Evals"](https://hamel.dev/blog/posts/evals/): the error-analysis-first approach to evaluation, which is the discipline behind the disagreement table.
- [Inspect AI](https://inspect.aisi.org.uk/) (UK AI Security Institute): the Dataset, Solver, and Scorer framework, the Python-native alternative harness for Part 5 of the lab.
