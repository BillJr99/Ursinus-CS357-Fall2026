---
layout: textbook
permalink: /Tutorials/LLMJudges
title: 'CS357: Foundations of Artificial Intelligence - LLM Judges and promptfoo: A Rubric, a Judge, and How Far to Trust It'
info:
  coursenum: CS357
  purpose: "To build an LLM judge from a rubric written as data, measure how well it agrees with your own hand scores, probe it for one bias, and set a tripwire that notices when it changes, first on three provided samples and then on artifacts you choose."
  eyebrow: "Tutorial"
  numbering: false
tags:
- evaluation
- llm-judge
- promptfoo
- rubrics
---

{% include mathjax.html %}

## About This Tutorial

Suppose you have forty short essays and a rubric, and you want a model to do the first pass of grading.  You can write that judge in an afternoon.  The harder question is whether you should believe it.  This tutorial builds the judge from the *Judge Pipeline Workshop* step by step, on three sample submissions you can see in full, and then asks how far to trust it: how often it agrees with you, whether padding moves it, where it disagrees, and how you would notice if a later change made it worse.
{: .tb-lede}

There are two ways through, and you only need one.  The **code path** is Python with `requests` talking to Ollama (`llama3.2` at temperature 0).  It also includes a *stand-in judge*, a few lines of keyword counting that returns the same JSON a model would, so the scoring, agreement, and tripwire code runs on any machine before Ollama is set up.  The **no-code path** is the same judge as a promptfoo configuration run through `npx` against Ollama, with a spreadsheet for agreement.  Parts I through III use the provided samples.  Part IV points what you built at artifacts you choose; your team's project outputs are one good option, and the *Project Sprint* session does exactly that with your team.

**You need** Ollama running with `llama3.2` pulled for the real judge, Python with `requests` for the code path, and Node.js for the no-code path (promptfoo runs through `npx`, so there is nothing else to install).  Check the ones you plan to use:

```bash
curl http://localhost:11434/api/tags
python3 -c "import requests; print('requests ok')"
npx promptfoo@latest --version
```

If you work inside the course container from *Your AI Workbench*, use `host.docker.internal:11434` wherever this page says `localhost:11434`.

## Key Concepts

| Term | Plain-English Definition | Where You Meet It |
|:-----|:------------------------|:------------------|
| **Judge** | A model prompted with a rubric and an artifact that returns a score per criterion in a fixed structured format, instead of prose | `ollama_judge()` in Section 3 |
| **Rubric as data** | The rubric written as a JSON object (criteria, weights, level descriptions), so the same object feeds the prompt, the arithmetic, and the CSV columns | `RUBRIC` in Section 1 |
| **Hand score** | The level you award each sample on each criterion yourself, written down before any judge runs | `HAND` in Section 1 |
| **Stand-in judge** | A keyword counter with the same inputs and outputs as the real judge, so the rest of the pipeline can run without a model | `stand_in_judge()` in Section 3 |
| **Fail closed** | When the judge's output cannot be parsed, the row is flagged for a person instead of given a guessed score | The `PARSE_ERROR` flag in Section 4 |
| **Evidence check** | A mechanical test that the sentence the judge quoted really appears in the submission | The `_quote_found` columns in `grades.csv` |
| **`llm-rubric` assertion** | A promptfoo check that hands one rubric sentence and an output to a judge model and records PASS or FAIL | Section 5 |
| **Percent agreement** | The share of (sample, criterion) cells where the judge's level matches yours | Section 6 |
| **Verbosity bias** | A judge scoring a longer answer higher when the added length carries nothing the rubric asks for | The padding probe in Section 7 |
| **Regression tripwire** | A check that re-runs the judge and fails loudly when its results drift from a run you already checked | Section 9 |
{: .tb-full}

---

# Part I: The Rubric Comes First

## 1.  Three Samples and a Rubric as Data

All three samples argue about library hours.  They were written to land at different rubric levels, and the differences are deliberate.  The cell below saves them into a `samples/` folder, defines the rubric, and holds your hand scores.  Save it as `judge.py`; every later code cell on this page gets appended to the bottom of the same file, and you re-run the whole file each time.

The rubric has three criteria with weights summing to 100, and four levels each described by something you can see in the text: a citation, a stated position, a rebuttal.  The weighted total is

$$
\text{total} = \sum_{c} w_c \cdot \frac{\ell_c}{4}
$$

where $$w_c$$ is the weight of criterion $$c$$ and $$\ell_c$$ is the level awarded on it.  A sample at level 4 everywhere scores 100, and one at level 1 everywhere scores 25.

```python
import os

SAMPLES = {
    "s01.txt": "The library should stay open until 2 a.m. during finals week. Seventy-one percent of students surveyed last spring said they studied past midnight at least three times during finals (Student Life Survey, 2025). Late closing also cuts noise complaints in the residence halls, which rose 40 percent during finals last year (Residence Life Report, 2025). Some argue the added staffing costs too much, but two student workers for four extra hours cost less than one noise incident investigation. The extension is cheap, and it is what students already need.",
    "s02.txt": "A lot of people study late during finals, and longer hours would help them. I think the library should probably stay open later. Some students have said they wish it was open longer. It might cost a bit more, but that is probably worth it.",
    "s03.txt": "Finals week is stressful for everyone. There are many places to study on campus, and each has its own advantages. The library is a nice building with good lighting. Everyone should find the study spot that works best for them.",
}
os.makedirs("samples", exist_ok=True)
for name, text in SAMPLES.items():
    with open(os.path.join("samples", name), "w") as f:
        f.write(text + "\n")

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
assert sum(c["weight"] for c in RUBRIC["criteria"]) == 100

def weighted_total(levels, rubric=RUBRIC):
    """levels maps each criterion name to an awarded level, 1 to 4."""
    return sum(c["weight"] * levels[c["name"]] / 4 for c in rubric["criteria"])

# The levels the samples were written to land on.  Replace them with yours.
HAND = {
    "s01.txt": {"claims_cited": 4, "directness": 4, "counterargument": 4},
    "s02.txt": {"claims_cited": 2, "directness": 3, "counterargument": 2},
    "s03.txt": {"claims_cited": 1, "directness": 1, "counterargument": 1},
}
for name, levels in HAND.items():
    print(name, "hand total:", weighted_total(levels))
```

Running it prints `100.0`, `57.5`, and `25.0`, the totals for the levels the samples were designed to land on.  Those designed levels are a starting point, not an answer key.

## 2.  Hand-Score Before Any Model Sees the Samples

Before you run any judge, read the three samples and write down your own level (1 to 4) for each sample on each criterion, using only the level descriptions in `RUBRIC`.  Then replace the numbers in `HAND` with yours.  If you are working with a teammate, score separately and compare afterward; where the two of you disagree is already a finding about the rubric.  The order matters because a score you have already seen anchors the one you write.  On the no-code path, put your levels straight into a spreadsheet with columns *Sample*, *Criterion*, and *Hand level*, one row per cell, nine rows in all.

### Questions to Work Through

1.  Where did your levels differ from the designed levels in `HAND`?  For each difference, name the word in the level description that let you read it your way.

    *Hint:* `s02` says "some students have said" without naming a source.  Is that "some claims cite evidence" (level 2) or "no claims cite evidence" (level 1)?  The descriptor never says what counts as evidence.

2.  Predict, before any judge runs: on which sample and criterion will `llama3.2` disagree with you most, and in which direction?  Write the prediction down, because Question 5 checks it.

---

# Part II: Build the Judge

## 3.  A Judge That Quotes Its Evidence

A judge is a model, a prompt, and a parser.  The prompt hands the model the rubric and the artifact and demands JSON: a level and a quoted sentence for every criterion.  The quote is the part that makes the judge checkable.  A low score only says the essay is weak; a quote that does not appear in the essay says the *judge* is unreliable on that row.

We start with the stand-in judge, so you can see the shape of the output without Ollama.  It is a keyword counter and nothing more: it counts sentences with a parenthetical source and year, looks for the word "should," and looks for "argue" or "but."  Append it to `judge.py`.

```python
import re

def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text.strip()) if s]

def stand_in_judge(artifact, rubric=RUBRIC):
    """A keyword counter, not a model.  It returns the JSON shape a real judge
    must return, so the rest of the pipeline runs without Ollama."""
    sents = sentences(artifact) or [""]
    first = sents[0]
    cited = [s for s in sents if re.search(r"\([^)]*\d{4}\)", s)]
    stance = [s for s in sents if re.search(r"\bshould\b", s)]
    engaged = [s for s in sents if re.search(r"\b(argue|critics|opponents)\b", s)]
    but = [s for s in sents if re.search(r"\bbut\b", s)]
    scores = {"claims_cited": (min(len(cited) + 1, 4), cited[0]) if cited else (1, first)}
    if stance:
        scores["directness"] = (4 if stance[0] == first else 3, stance[0])
    else:
        scores["directness"] = (1, first)
    if engaged:
        scores["counterargument"] = (4 if engaged[0] in but else 3, engaged[0])
    else:
        scores["counterargument"] = (2, but[0]) if but else (1, first)
    data = {"scores": {k: {"level": l, "evidence": e} for k, (l, e) in scores.items()}}
    return weighted_total({k: l for k, (l, e) in scores.items()}, rubric), data

print(stand_in_judge(open("samples/s01.txt").read()))
```

The stand-in gives `s01` level 3 on `claims_cited`, because it counts two cited sentences, while the designed level is 4.  Keep that in mind; a rule that counts is not the same as a reader who understands, and the stand-in's mistakes will show up in Section 6.

Now the real judge.  The system prompt is the one from the workshop.  The parser is split out into `parse_reply()` so that you can test it without a model, and it fails closed: a reply that is not JSON, is missing a criterion, or awards a level outside 1 to 4 raises an error instead of producing a number.

> This cell defines a function that talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  The two parser tests at the bottom run anywhere.
{: .tb-warning data-title="Runs on your machine, not here"}

```python
import json
import requests

SYSTEM = ("You are a strict grader. Score the artifact on EACH criterion by choosing a level 1-4 "
          "that matches the level descriptions. Quote the sentence that justifies each score. "
          "Respond ONLY with JSON: "
          '{"scores": {"<criterion>": {"level": int, "evidence": str}}}')

def parse_reply(raw, rubric=RUBRIC):
    """Turn the model's text into (total, data).  Anything malformed raises."""
    data = json.loads(raw.replace("```json", "").replace("```", ""))
    levels = {c["name"]: data["scores"][c["name"]]["level"] for c in rubric["criteria"]}
    for name, level in levels.items():
        if level not in (1, 2, 3, 4):
            raise ValueError(f"{name}: level {level!r} is not 1-4")
    return weighted_total(levels, rubric), data

def ollama_judge(artifact, rubric=RUBRIC, model="llama3.2", system=SYSTEM):
    user = f"RUBRIC:\n{json.dumps(rubric, indent=1)}\n\nARTIFACT:\n{artifact}"
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": model, "stream": False,
            "options": {"temperature": 0.0, "seed": 42},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=180)
        return parse_reply(r.json()["message"]["content"], rubric)
    except Exception as e:
        print(f"[judge:parse] {e}")
        return None, {"error": str(e)}

# The parser runs without Ollama.  Two made-up replies:
print(parse_reply('```json\n{"scores": {"claims_cited": {"level": 2, "evidence": "x"}, '
                  '"directness": {"level": 3, "evidence": "y"}, '
                  '"counterargument": {"level": 2, "evidence": "z"}}}\n```')[0])
try:
    parse_reply('{"scores": {"claims_cited": {"level": "high"}}}')
except Exception as e:
    print("fails closed:", type(e).__name__, e)
```

The two tests print `57.5` and then `fails closed: KeyError 'directness'`, because the second reply never scores `directness`.  With Ollama running, try the real judge once on one sample before you build anything around it: append `print(ollama_judge(open("samples/s02.txt").read()))`, run the file, and then delete that line.  If `llama3.2` wraps its JSON in a code fence, `parse_reply()` strips the fence before parsing.  If the call prints `[judge:parse]`, read the error before you go on; Section 4 will flag that row rather than guess.

## 4.  The Batch Loop and grades.csv

The batch loop walks `samples/`, calls the judge on each file, fails closed on a parse error, checks every quoted sentence against the file it came from, and writes `grades.csv`.  One change from the workshop version: an empty quote now counts as *not* found.  In the workshop loop, `"" in text` is always `True`, so a row with no evidence at all passed the evidence check.

```python
import csv
import os

JUDGE = stand_in_judge   # change to ollama_judge once Ollama is running

def grade_folder(judge, folder="samples", out="grades.csv"):
    rows = []
    for name in sorted(os.listdir(folder)):
        text = open(os.path.join(folder, name)).read()
        total, detail = judge(text)
        row = {"filename": name, "total": total, "flag": ""}
        if total is None:
            row["flag"] = "PARSE_ERROR"   # fail closed: a human reads this row
        for c in RUBRIC["criteria"]:
            s = detail.get("scores", {}).get(c["name"], {})
            evidence = s.get("evidence", "")
            row[c["name"] + "_level"] = s.get("level", "")
            row[c["name"] + "_evidence"] = evidence
            row[c["name"] + "_quote_found"] = bool(evidence) and evidence in text
        rows.append(row)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows

rows = grade_folder(JUDGE)
for row in rows:
    print(row["filename"], row["total"], row["flag"] or "-",
          [row[c["name"] + "_level"] for c in RUBRIC["criteria"]],
          [row[c["name"] + "_quote_found"] for c in RUBRIC["criteria"]])
```

Each printed line is a filename, the weighted total, the flag (`-` when empty), the three levels, and the three evidence checks.  With the stand-in, the first line is `s01.txt 87.5 - [3, 4, 4] [True, True, True]`, and the totals for `s02` and `s03` are `45.0` and `40.0`.  The stand-in copies its quotes straight from the text, so every check passes; a model does not have to.  Open `grades.csv` in a spreadsheet and check three things in order: no row is flagged, every `_quote_found` is `True`, and the totals rank `s01` above `s02` above `s03`.  Then change `JUDGE = stand_in_judge` to `JUDGE = ollama_judge`, re-run, and check the same three things.

## 5.  The Same Judge in promptfoo

The no-code path says the same thing in a configuration file: here are the outputs, here is the judge, here are the assertions, run them all.  The workshop starts with a one-test smoke config that asks for the capital of France; run it first if you have never used promptfoo.  If promptfoo cannot reach Ollama, confirm `ollama serve` is running and that `curl http://localhost:11434/api/tags` responds; promptfoo reads the base URL from the `OLLAMA_BASE_URL` environment variable if your Ollama runs somewhere else.

The judge needs two more files.  `dataset.csv` holds one row per sample, with columns `id` and `answer`.  You can build it in a spreadsheet (paste each sample into the `answer` column and export as CSV), or save this short script as `make_dataset.py` and run it in the folder that contains `samples/`.  It also adds the padded copy of `s02` you will use in Section 7:

```python
import csv
import os

PAD = ("This essay was written with great care and attention to detail.  "
       "The author is deeply knowledgeable about campus issues.")

with open("dataset.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "answer"])
    for name in sorted(os.listdir("samples")):
        w.writerow([name.removesuffix(".txt"),
                    open(os.path.join("samples", name)).read().strip()])
    w.writerow(["s02_padded", open("samples/s02.txt").read().strip() + " " + PAD])
```

The prompt is a one-line template that echoes each stored answer straight through, so the judge grades your dataset rather than a freshly generated reply.  promptfoo's template syntax is the variable name inside two pairs of curly braces; create the file with this command rather than typing it:

```bash
python3 -c "print('{' * 2 + 'answer' + '}' * 2)" > prompt.txt
```

Then save the judge itself as `promptfooconfig-rubric.yaml`:

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

```bash
npx promptfoo@latest eval -c promptfooconfig-rubric.yaml --output grades_promptfoo.csv
npx promptfoo@latest view   # opens the results viewer in your browser
```

With four rows in `dataset.csv` you get twelve verdicts.  Read the three `value:` blocks against `RUBRIC`: each collapses four levels to one line, where PASS means level 3 or 4 and FAIL means level 1 or 2.  That translation loses information on purpose; promptfoo answers "good enough?" while the code path answers "how good?".  The viewer shows the grader's reason for each verdict.  Read a few of them, and notice that nothing on this path checks that a quoted sentence is really in the answer.

### Questions to Work Through

3.  Predict before running promptfoo: which of the nine verdicts on `s01`, `s02`, and `s03` will be PASS?  Derive your answer from your hand scores alone (level 3 or 4 means PASS).  Then run it and count the cells where the verdict disagrees with your prediction.

    *Hint:* The same model read the same text under two different prompts in Sections 4 and 5.  When the two paths disagree, neither one is broken; the disagreement measures how much the *wording* of the rubric line moves the judge.

4.  The stand-in judge gave `s03` level 3 on `directness`.  Find the sentence it quoted, and explain which rule in `stand_in_judge()` produced that level.  Would you expect `llama3.2` to make the same mistake?
{: start="3"}

---

# Part III: How Far to Trust It

A judge that runs is not yet a judge you can use.  The workshop names the minimum: agreement with a person's scores, and a controlled probe for one known bias.  This Part adds the two records that make those numbers useful later, a disagreement table and a tripwire.  A judge you rely on for real decisions needs more than this (a larger calibration set, Cohen's kappa, which is an agreement score corrected for agreement you would expect by chance, and a study of more than one bias); here you run each check once so the shape is familiar.

## 6.  Agreement With Your Hand Scores

Percent agreement is the number of cells where the judge's level equals yours, divided by the number of cells.  Report it overall and per criterion, because the per-criterion number tells you where to look.

```python
def agreement(rows, hand):
    names = [c["name"] for c in RUBRIC["criteria"]]
    match = {n: 0 for n in names}
    for row in rows:
        for n in names:
            if row[n + "_level"] == hand[row["filename"]][n]:
                match[n] += 1
    cells = len(rows) * len(names)
    print(f"overall: {sum(match.values())} of {cells} "
          f"= {100 * sum(match.values()) / cells:.1f}%")
    for n in names:
        print(f"  {n}: {match[n]} of {len(rows)}")

agreement(rows, HAND)
```

With the stand-in and the designed levels in `HAND`, this prints `overall: 6 of 9 = 66.7%`, then 1 of 3 for `claims_cited`, 2 of 3 for `directness`, and 3 of 3 for `counterargument`.  A criterion at 1 of 3 is telling you its descriptor is ambiguous or the judge's reading of it is off, and you find out which in Section 8.  Now switch `JUDGE` to `ollama_judge`, put your own levels in `HAND`, and record the real judge's numbers.  With only three samples, each disagreement moves a criterion's number by 33 points, so treat it as a check rather than a measurement.

**On the no-code path,** add two columns to your spreadsheet.  Column D holds the judge's level from `grades.csv`, or skip it if you only ran promptfoo.  Column E holds the promptfoo verdict for that cell, copied from `grades_promptfoo.csv` or the viewer.  Then add:

| Column | Formula in row 2 (fill down to row 10) | What it gives you |
|---|---|---|
| F | `=IF(C2>=3,"PASS","FAIL")` | Your hand level, collapsed the same way promptfoo collapses it |
| G | `=IF(F2=E2,1,0)` | 1 when promptfoo agrees with you on this cell |
| H | `=IF(C2=D2,1,0)` | 1 when the code-path judge agrees with you on this cell |
{: .tb-full}

`=AVERAGE(G2:G10)` is promptfoo's agreement with you, and `=AVERAGE(H2:H10)` is the code-path judge's.  Use `AVERAGEIF` on the criterion column, or sort by criterion, for the per-criterion numbers.

## 7.  One Bias Probe: Padding

Append two content-free sentences to `s02` and grade it again.  They add no citation, no position, and no counterargument, so a judge that reads the rubric returns the same three levels before and after.  The padded sentences also praise the author, so a judge that moves is reading tone as well as length.

```python
PAD = ("This essay was written with great care and attention to detail.  "
       "The author is deeply knowledgeable about campus issues.")

def padding_probe(judge, name="s02.txt"):
    text = open(os.path.join("samples", name)).read()
    before, detail_before = judge(text)
    after, detail_after = judge(text.strip() + " " + PAD)
    print(f"{name} before padding: {before}  after padding: {after}")
    for c in RUBRIC["criteria"]:
        b = detail_before["scores"][c["name"]]["level"]
        a = detail_after["scores"][c["name"]]["level"]
        print(f"  {c['name']}: {b} -> {a}  (delta {a - b:+d})")

padding_probe(JUDGE)
```

The stand-in prints a delta of `+0` on all three criteria, and it would on any padding: it counts features, and the padding has none of them.  That is why the stand-in cannot tell you anything about verbosity bias, and the run that matters is the one with `JUDGE = ollama_judge`.  On the no-code path, compare the `s02` and `s02_padded` rows in the promptfoo viewer; any verdict that changes from FAIL to PASS is the same finding.  A delta of zero does not clear the judge either: it is one sample, one padding string, and one model.

## 8.  The Disagreement Table

The table puts every cell side by side, so you can see the row you would revise.  This cell prints it in Markdown, ready to paste into your notes.

```python
print("| Sample | Criterion | Human | Judge | Gap (human minus judge) |")
print("|---|---|---|---|---|")
for row in rows:
    for c in RUBRIC["criteria"]:
        h = HAND[row["filename"]][c["name"]]
        j = row[c["name"] + "_level"]
        gap = h - j if j != "" else "n/a"
        print(f"| {row['filename']} | {c['name']} | {h} | {j} | {gap} |")
```

With the stand-in, the largest gap is `s03` on `directness`: the designed level is 1 and the stand-in said 3, a gap of -2 (the judge scored higher than the human).  For the real judge, add a column for the padded level on `s02` and a column for the promptfoo verdict, and fill both by hand.  Then take the row with the largest gap and follow it back to its evidence: is the quoted sentence really in the sample, and does it satisfy the level description as written?  If the quote is real and the description lets two careful readers disagree, the repair belongs in the rubric.  If the quote is real and the description is clear, the judge may simply be right and your hand score generous.

## 9.  A Regression Tripwire

So far your confidence in the judge lives in a table you typed and a run you watched.  A tripwire turns that into a check you can repeat after every change to the prompt, the model, or the rubric.  The cell below saves the first run as `baseline.json`.  Every later run compares against it and reports two kinds of trouble: a level that changed, and a quote that is no longer in the text.

```python
import json

def tripwire(judge, baseline_file="baseline.json"):
    """Re-grade, then compare with a run you already checked by hand."""
    now = grade_folder(judge, out="grades_check.csv")
    if not os.path.exists(baseline_file):
        json.dump(now, open(baseline_file, "w"), indent=1)
        return print("baseline saved; run again after your next change")
    base = {r["filename"]: r for r in json.load(open(baseline_file))}
    problems = []
    for row in now:
        for c in RUBRIC["criteria"]:
            key, old = c["name"] + "_level", base[row["filename"]][c["name"] + "_level"]
            if row[key] != old:
                problems.append(f"{row['filename']} {key}: {old} -> {row[key]}")
            if not row[c["name"] + "_quote_found"]:
                problems.append(f"{row['filename']} {c['name']}: quote not in the text")
    print("PASS" if not problems else f"TRIPPED: {len(problems)} problems")
    for p in problems[:3]:
        print("  " + p)

def paraphrasing_judge(artifact):
    """Stands in for a judge whose prompt lost 'Quote the sentence...'."""
    total, detail = stand_in_judge(artifact)
    for s in detail["scores"].values():
        s["evidence"] = "The essay " + s["evidence"][:20].lower() + "..."
    return total, detail

tripwire(JUDGE)                 # the first run ever saves the baseline
tripwire(JUDGE)                 # the same judge again
tripwire(paraphrasing_judge)    # the same levels, but the quotes are gone
```

The first time you run the file, this prints `baseline saved; run again after your next change`, then `PASS` for the unchanged judge, then `TRIPPED: 9 problems` and the first three of them, each ending in `quote not in the text`.  The last judge stands in for a real regression the workshop asks you to try: delete the sentence `Quote the sentence that justifies each score.` from `SYSTEM`, and the model is free to paraphrase.  Its levels did not move, so a check on levels alone would have passed it; only the evidence check caught it.  Later runs print `PASS` twice before the `TRIPPED` lines, because the baseline already exists.  Delete `baseline.json` when you switch from the stand-in to `ollama_judge`, so the baseline is a run of the judge you actually mean to keep.

**On the no-code path,** the tripwire is a second configuration file.  Save a baseline, copy the config, make one plausible-looking change (for example, loosen the `claims_cited` line to "PASS if the answer mentions any evidence"), and run the copy:

```bash
npx promptfoo@latest eval -c promptfooconfig-rubric.yaml --output run_baseline.json
cp promptfooconfig-rubric.yaml promptfooconfig-regressed.yaml
# edit one value: line in promptfooconfig-regressed.yaml, then:
npx promptfoo@latest eval -c promptfooconfig-regressed.yaml --output run_regressed.json
```

Find which verdicts changed and in which direction, then confirm the original config still gives the baseline verdicts.

### Questions to Work Through

5.  Look back at your prediction from Question 2.  Was the largest gap where you predicted?  Quote the sample and the level description that explain the gap.

6.  Rewrite the level descriptions of your worst criterion so that the disagreement could not happen: name the countable feature (a source in parentheses, an opposing view in a full sentence, a rebuttal that gives a reason).  Re-run the judge with the revised `RUBRIC` and report that criterion's agreement before and after.  Will your tripwire pass after the rewrite?  Should it?

    *Hint:* Revise the description, not the sample.  A tripwire that trips after a deliberate repair is doing its job; save a new baseline only after you have checked the new run by hand.

7.  The tripwire compares the judge with its own earlier run, not with your hand scores.  What can it catch that agreement cannot, and what can agreement catch that it cannot?
{: start="5"}

---

# Part IV: Your Own Artifacts

## 10.  Pointing the Judge at Something You Chose

Everything so far ran on three paragraphs written to land at known levels.  Your own artifacts did not.  Pick three artifacts of one kind: summaries your team's project produced this week, answers your agent gave to three test questions, three sections of a lab report, or three essays you wrote for another class.  Use work that is yours or that the authors have agreed to let you grade this way.

What is enough for this Part:

- A `RUBRIC` of two to four criteria, each level described by something a reader can point to in the text.  Anything a line of code can check (length, a required heading, a word count) belongs in code, not in the rubric.
- Your hand scores, written down before the judge runs.  If a teammate scores too, score separately.
- One run of the judge, from either path, and the agreement number per criterion.
- One padding probe on one artifact, and the disagreement table.

The tripwire is optional here, and it is worth adding if you will keep using the judge.  Nothing else in `judge.py` changes when the rubric changes, because every function reads `RUBRIC`; replace the files in `samples/` and the `HAND` dictionary and re-run.  On the no-code path, rebuild `dataset.csv` from your artifacts and rewrite the three `llm-rubric` lines to match your criteria.  If the artifacts are your team project's outputs, the *Project Sprint* session runs this same procedure with two blind scorers and an audit of one disagreement, so bring your table.

---

## Exercises

Everything below is optional, and none of it is collected.  Each exercise ends with a check you apply yourself.

1.  **Twelve samples.**

    *What to do:* Three samples are too few to trust a judge.  Write nine more into `samples/`, including an empty file and an off-topic one, and add their hand scores to `HAND`.  Re-run the judge.

    *Starter hint:* An empty artifact gives the judge nothing to quote.  Watch whether it invents evidence or fails to parse; either is a finding.

    *You've succeeded when:* `grades.csv` has twelve rows, every `_quote_found` on a non-empty file is `True` or explained, and the empty file's row is flagged or scored all ones with a reason you can state.

2.  **A fourth criterion.**

    *What to do:* Add a fourth criterion to `RUBRIC` (a conclusion sentence is a good candidate) with weights that still sum to 100, and add the matching `llm-rubric` block to the YAML.

    *Starter hint:* Nothing else in `judge.py` changes.  Count how many lines the YAML change took.

    *You've succeeded when:* Both CSVs grow by one criterion, the `assert` in the first cell still passes, and the totals still fall between 25 and 100.

3.  **Break the real judge on purpose.**

    *What to do:* With `JUDGE = ollama_judge` and a fresh `baseline.json`, delete `Quote the sentence that justifies each score.` from `SYSTEM`, re-run, and read the tripwire's report.  Then restore the sentence and run once more.

    *Starter hint:* This is a regression test in miniature: a deliberate degradation, a measurable drop, and a recovery.

    *You've succeeded when:* You can show the tripwire's output before, during, and after, and say in one sentence what a versioned config would have caught.

---

## Reflection Prompt

**Personal level:** You scored the samples yourself before any judge did.  On which criterion did you hesitate most, and did reading the judge's quoted sentence change your mind or make you more sure?  What does that tell you about using a judge on your own work?

**Technical level:** Name the smallest set of numbers you would want to see before you let this judge grade a class of forty, and give a threshold for each.  What would you do if one criterion clears its threshold and another does not?

**Societal level:** The judge you built runs on your laptop against text you can read.  The same design scores admissions essays and job applications elsewhere.  What changes about the agreement check when the submissions come from people who cannot see the rubric, and who should be required to publish the agreement numbers?

---

## Further Reading

- [Judge Pipeline Workshop: Build and Audit a Judge](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-rubricworkshop.md), the in-class session this tutorial follows, with its disagreement table and padding probe.
- [Critique, Consensus, and the LLM Judge](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-critiqueconsensusjudge.md), Part IV, for the rubric autopsy and the four judge biases (position, verbosity, self-preference, leniency drift).
- [Project Sprint: Run Your Rubric Against Your Project, and Threat Model It](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-projectsprint.md), where the judge meets your project's outputs and the run is frozen as a regression check.
- The [Multi-Agent Patterns lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate), whose Part A may use this judge as its critic, and [Measuring Multi-Agent Patterns](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/MultiAgentMeasurement), where it drives a judge-and-refine loop.
- [Testing Agents](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/TestingAgents), for eval harnesses and running them on every change.
- [promptfoo documentation](https://www.promptfoo.dev/docs/intro/), including the full list of assertion types and the results viewer.
- Hamel Husain, ["Your AI Product Needs Evals"](https://hamel.dev/blog/posts/evals/), the error-analysis-first approach behind the disagreement table.
- [Inspect AI](https://inspect.aisi.org.uk/) (UK AI Security Institute), a Python-native alternative to promptfoo.
- Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena."  *NeurIPS* (2023).  Pathologies and agreement rates.
- Hashemi et al. "LLM-Rubric: A Multidimensional, Calibrated Approach to Automated Evaluation."  *ACL* (2024).
