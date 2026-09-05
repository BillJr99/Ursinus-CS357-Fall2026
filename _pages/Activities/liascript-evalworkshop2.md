<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-evalworkshop2.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-evalworkshop2.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Evaluation Workshop II: Run Your Rubric Against Your Project

Two weeks ago the Rubric Pipeline lab handed you a synthetic corpus and asked you to build a judge you could trust.  Today you point that judge at your own final project and find out whether the trust survives contact with real outputs.  You leave with a disagreement table for three real artifacts, one disagreement traced to its evidence and repaired, and the run frozen into your project repository as a regression check that fails the next time the judge quietly changes.

The Literature Review Team Synthesis is due today.  The Rubric Pipeline lab is due Tuesday, so everything you produce this session can go straight into it.

---

## Directions and Group Roles

Project roles are in effect today: **Coordinator**, **Builder(s)**, **Evaluator**, **Scribe**.  The Coordinator keeps the run on the clock.  The Builder runs the judge and, later, writes the harness configuration.  The Evaluator is one of the two blind human scorers and owns the audit in Model 2.  The Scribe keeps the disagreement table, the repair record, and the triage you leave with.  If your team built more than one judge in the lab (the lab is a pair assignment), the Evaluator picks the one with the better human-agreement number and the team uses that one.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Blind scoring** | Two humans score an artifact independently, on separate sheets, before anyone sees the judge's score, so the human scores are not anchored to the machine | The score sheet template in Model 1, filled in before the judge runs |
| **Disagreement table** | One row per artifact and criterion, holding the judge's level, both human levels, and the gap between them | The six-column table you fill in Model 1 |
| **Gap** | The largest absolute difference between the judge's level and either human's level on one row | Judge 4, Human A 2, Human B 3: gap 2 |
| **Audit to evidence** | Following one disagreement back to the quote the judge cited and the descriptor it applied, and checking both against the artifact | Model 2, on your largest-gap row |
| **Rubric repair** | Rewriting a level descriptor so that it names something a reader can observe, because the old wording let the judge and the humans read it differently | "Adequate evidence" becomes "quotes at least two sources by name" |
| **Artifact repair** | Fixing the project output (or the prompt that produced it) because the judge was right and the humans were generous | The summary the judge scored at level 2 really does omit the citation |
| **Reasoning trace** | The visible thinking a reasoning model emits before its verdict; generated text, produced by the same mechanism as the verdict, and not a substitute for a checkable quote | Model 2's warning, and the shown-versus-hidden audit step |
| **Golden set** | The artifacts and their agreed human levels that a harness compares the judge against on every run | Your three artifacts plus two adversarial cases, in Model 3 |
| **Regression check** | A versioned eval configuration, committed next to the code, that re-verifies the judge with one command and fails when a change degrades it | The `promptfooconfig.yaml` (or Inspect task) you commit in Model 3 |

---

### Before You Start

**You need:** the judge from the Rubric Pipeline lab (code route: the batch scorer, its rubric JSON, and a `grades.csv` from a working run; Direction 0: your `promptfooconfig.yaml` and `run_baseline.json`), Ollama running with the model the judge was validated against, the rubric your judge reads adapted to your project's outputs, and three artifacts your project produced this week (answers, summaries, plans, report sections: whatever the rubric is written to score).  Put the three artifacts in one folder before class.  If you wrote the evaluation and monitoring section of your governance one-pager on Tuesday, bring it; today tests whether its measurements are ones you can actually take.

**What you will have at the end:** a filled disagreement table, one documented repair, and a harness configuration committed to your project repository.

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Stand-up: judge status, agreement numbers, the three artifacts |
| 10-35 | Model 1: blind human scores, run the judge, fill the disagreement table |
| 35-50 | Model 2: audit the largest gap to its evidence and repair the rubric or the artifact |
| 50-62 | Model 3: freeze the run as a regression check in the project repository |
| 62-70 | Triage the remaining rows |
| 70-75 | Report out: one number and one repair per team |

---

# Part I: Stand-Up and the Run

## 1.  Stand-Up (10 minutes)

Each team answers, in two minutes at the board, exactly four questions: What does the judge do end-to-end today (which model, which route, what it emits)?  What did the lab's human-to-judge agreement come out to, per criterion (a number, not an adjective)?  What are the three artifacts you brought, and why those three?  What do you need from the instructor or another team?  Stand-ups are status synchronization, not performance; the discipline is *saying the number*.  "It agreed with us most of the time" is not a number.  "C3 was 62% and the others were above 80%" is, and it tells the room where to look.

---

*Your judge has a track record on synthetic essays.  It has none on your project's outputs.  Model 1 builds that record the same way the lab did: humans first, judge second, then the two side by side.*

## Model 1: Run the Judge and Fill the Disagreement Table

The order matters.  If you see the judge's scores first, your human scores will be anchored to them and the comparison will be biased.  So the two scorers work first, on separate sheets, and do not talk until both sheets are complete.

1.  **Score blind.**  The Evaluator and one other teammate each score all three artifacts, one sheet per artifact, using the lab's template.  Record the level (1-4) and a one-sentence justification for each criterion.

    ```
    Scorer: [your name]   Date: [today]
    Submission: s01_excellent.txt

    C1 (Claim): Level ___ | Justification: ___
    C2 (Evidence): Level ___ | Justification: ___
    C3 (Counterargument): Level ___ | Justification: ___
    C4 (Conclusion): Level ___ | Justification: ___
    ```

    Substitute your own criterion names and file names; keep the shape.

2.  **Run the judge** on the folder of three artifacts, exactly as you ran it in the lab.  The Builder does this while the scorers work, and does not announce the results until both sheets are done.

3.  **Fill the table.**  The Scribe enters one row per artifact and criterion.  The gap is the largest absolute difference between the judge's level and either human's level.  If the two humans disagree with each other by 2 or more on a row, mark that row with an asterisk: it is a rubric problem before it is a judge problem.

| Artifact | Criterion | Judge | Human A | Human B | Gap |
|---|---|---|---|---|---|
| (file name) | C1 | | | | |
| (file name) | C2 | | | | |
| (file name) | C3 | | | | |
| (file name) | C4 | | | | |

[[___ Your disagreement table here (all three artifacts) ___]]

## Code Cell

Run this after both sheets are complete, with your three files in place of the eight.  It is the lab's agreement function unchanged; a printed number per criterion is what you report at the stand-up on Tuesday.

```python
# After both partners have scored independently:
# partner_a_scores[file][criterion] = level (int)
# partner_b_scores[file][criterion] = level (int)

def percent_agreement(scores_a, scores_b, criterion_id, files):
    """Exact-match agreement rate for one criterion."""
    matches = sum(
        1 for f in files
        if scores_a[f][criterion_id] == scores_b[f][criterion_id]
    )
    return matches / len(files)

# Example (fill in your actual scores):
partner_a = {
    "s01_excellent.txt": {"C1": 4, "C2": 4, "C3": 4, "C4": 4},
    "s12_borderline.txt": {"C1": 3, "C2": 3, "C3": 2, "C4": 3},
    # ... add all 8 files
}
partner_b = {
    "s01_excellent.txt": {"C1": 4, "C2": 4, "C3": 4, "C4": 4},
    "s12_borderline.txt": {"C1": 3, "C2": 2, "C3": 3, "C4": 3},
    # ...
}

calibration_files = list(partner_a.keys())
criteria = ["C1", "C2", "C3", "C4"]

print("Human-to-human agreement:")
for cid in criteria:
    agr = percent_agreement(partner_a, partner_b, cid, calibration_files)
    print(f"  {cid}: {agr:.0%}")
```

With three files, each disagreement moves a criterion's number by 33 points, so treat the percentage as a check and the table as the deliverable.  The lab's eight-file calibration set is still the number that goes in your report.

### Critical Thinking Questions

**Question 1.**  Before the judge runs, predict: which artifact and which criterion will show the largest gap, and in which direction (judge high or judge low)?  Write the prediction down; the Scribe compares it to the table afterward.

[[___ Your prediction here ___]]

*Hint:* The lab's weakest criterion is the first suspect.  The second is any criterion whose descriptor uses a word like "clear," "adequate," or "thoughtful," because two people can read the same artifact and reach different levels without either being wrong.

**Question 2.**  On a row marked with an asterisk (the humans disagree with each other by 2), what does the judge's gap on that row tell you?  Can the judge be "right" on a row where the humans cannot agree what right is?

[[___ Your answer here ___]]

*Hint:* Human-to-human agreement is the ceiling on human-to-judge agreement.  A judge cannot agree with both of two humans who disagree.  The row is telling you the descriptor is not observable, which is a rubric repair, and no change to the judge will fix it.

**Question 3.**  Your judge's `grades.csv` marks one row `REVIEW_NEEDED` (or, on Direction 0, one item returned unparseable output).  Does that row go in the disagreement table?  What level do you enter for the judge?

[[___ Your answer here ___]]

*Hint:* Enter it with no judge level and no gap, and count it separately: a judge that fails closed on one artifact in three has a 33% coverage problem, which is a different finding from a disagreement and belongs in the report's limitations.

---

# Part II: Audit and Repair

*You have a table with gaps in it.  A gap is a symptom.  Model 2 finds the cause for one of them and fixes the right thing.*

## Model 2: Audit One Disagreement to Its Evidence

Take the row with the largest gap (break ties toward the row the humans agreed on, since that gap is entirely the judge's).  The Evaluator leads; the Scribe records each step.

1.  **Pull the judge's evidence.**  Copy the quoted span the judge cited for that criterion, exactly as it appears in the CSV or the run output.
2.  **Verify the quote.**  Search the artifact for the quoted span as an exact substring.  If it is not there, stop: the judge fabricated evidence, and the row is a judge fault (see the table below).
3.  **Read the descriptor against the quote.**  Open the level descriptor the judge applied.  Does the quoted span satisfy that descriptor as written?  Would a stranger reading only the descriptor and the quote reach the same level?
4.  **Read the human justifications.**  Each scorer wrote one sentence.  Do the two sentences point at the same feature of the artifact as the judge's quote, or at a different one?
5.  **Decide the fault and make the repair.**

| Where the fault is | What you saw in steps 2-4 | The repair | Proof the repair worked |
|---|---|---|---|
| Rubric | The quote is real, but the descriptor uses a word the judge and the humans read differently; often the humans disagreed with each other too | Rewrite that level's descriptor so it names something observable (a count, a presence, a named section) | Both humans and the judge re-score the artifact; the gap closes to 0 or 1 |
| Artifact | The quote is real, the descriptor is observable, and the judge is right: the artifact really does lack what the descriptor asks for | Fix the artifact, or the prompt or pipeline step that produced it | Re-run the judge on the fixed artifact; its level rises and both humans agree |
| Judge | The quote does not appear in the artifact, or the level tracks length or position rather than content | Not a rubric or artifact change: flag the row, record it for the lab's hallucinated-evidence rate or bias section, and add the mechanical validator below | Re-run; the row now carries the flag instead of a confident wrong level |

Make exactly one repair today, write it down, and re-run.  A repair without a re-run is a hypothesis.

[[___ Your audit record: row, quote, descriptor, fault, repair, re-run result ___]]

### When the Judge Is a Reasoning Model

Sooner or later someone on your team proposes a reasoning model as the judge, on the theory that a model which deliberates before answering will grade more carefully.  That instinct is half right.  Multi-criterion rubrics are exactly the shape of problem extra dependent steps help with: hold four criteria in mind, check the artifact against each, keep the levels straight, and do not let a strong showing on criterion 1 bleed into criterion 3.  A reasoning model is measurably steadier at that bookkeeping.

The wrong half is what the visible trace is.  It is generated text, produced by the same next-token mechanism as the verdict.  It reads like the judge's justification.  It is not, necessarily: research on chain-of-thought faithfulness finds cases where a model's stated reasoning does not match what drove its answer.

> **Never paste a reasoning trace into a rubric as evidence.**  Your judge prompt demands quoted evidence *from the artifact* for every score, and that requirement is doing real work: a quote is checkable against the source, and a trace is not.  A trace saying "the summary lacks a clear citation" is the judge asserting the score a second time in longer form, not supporting it.

There is a second-order effect to watch for.  A long, fluent, confident trace is more persuasive to *you*, the human auditing the judge.  The pathologies you catalogued in the judge activity do not disappear when the judge thinks longer; they arrive better argued.

**One more audit step, whichever judge you use.**  Score the same artifacts twice, once with the reasoning trace shown to you and once with it hidden, and compare your agreement numbers across the two conditions.  If your agreement with the judge goes *up* when you can see its reasoning, ask the uncomfortable question: did the trace help you evaluate the score, or did it persuade you to accept it?  Those look identical from the inside, and only the numbers can tell them apart.

### Critical Thinking Questions

**Question 4.**  Your judge is a reasoning model.  For one artifact it scores criterion 2 at level 3, and its trace argues carefully for level 3 while quoting a sentence that does not appear anywhere in the artifact.  Name what went wrong, and say which of your existing checks would have caught it and which would not.

[[___ Your answer here ___]]

*Hint:* The judge fabricated a quotation, which the trace's fluency disguises rather than reveals.  The evidence requirement catches it, but only if somebody actually verifies the quote against the source, which is a check no amount of reading the trace performs.  Human agreement scoring would not catch it either, since a human reading a persuasive trace may simply agree.  The cheap fix is mechanical: assert every quoted span appears verbatim in the input, which is a validator rather than a judgment.

**Question 5.**  Your largest-gap row turned out to be an artifact fault: the judge was right and both humans were generous.  What does that tell you about the humans' one-sentence justifications, and what should change on the score sheet before Tuesday's calibration run?

[[___ Your answer here ___]]

*Hint:* Generous human scores usually come from scoring the artifact's intent rather than its text.  If both justifications say what the artifact "tries to" do, the sheet needs a rule: the justification must quote the artifact, the same rule you imposed on the judge.

**Question 6.**  Predict the shown-versus-hidden result for your team before you run it: will your agreement with the judge go up, down, or stay flat when the trace is visible?  What would each outcome mean?

[[___ Your prediction here ___]]

*Hint:* Flat is the healthy result: the trace is not moving you.  Up is the warning: the trace is persuading you.  Down is rare and worth a note; it usually means the trace exposed a fabricated quote you would otherwise have missed.

---

# Part III: Freeze, Triage, and Practice

*You now have three artifacts with agreed human levels and one repaired disagreement.  That is a golden set.  Model 3 turns it into a check the repository runs, so the judge cannot drift without someone noticing.*

## Model 3: Freeze the Run as a Regression Check

So far your confidence in the judge lives in a table the Scribe typed and a re-run someone watched.  Industry teams encode that confidence as a versioned eval configuration: a declarative file that says "given these inputs, the judge must produce these outputs," checked into the repository next to the code so that every future change to the prompt, model, or rubric can be re-verified with one command.  You built one in the lab's Part 5 (promptfoo by default, Inspect AI if you chose it).  Today it moves into the project repository and grows a golden set drawn from your own outputs.

1.  **Define the golden set.**  Your three artifacts, with the human-consensus level for each criterion (after today's repair).  Add two adversarial cases from the lab's bias probe, for example the padded and unpadded versions of one artifact, which must receive the same level.
2.  **Encode assertions.**  For each case, at least one assertion: the judge's returned level equals the human-consensus level (exact match on the parsed JSON field), or, for the adversarial pair, that the two levels are equal to each other.  In promptfoo these are `assert:` blocks; in Inspect they are scorers.  Assert on the *parsed* field, not the raw text; if parsing itself fails, that is a legitimate eval failure worth counting.
3.  **Run the harness against your local model** and capture the results (promptfoo's `output.json` or web viewer screenshot, or Inspect's `.eval` log).  Record the pass rate.  It will likely not be 100%: that is a finding, not a failure.
4.  **Demonstrate a regression.**  Make a deliberate, plausible-seeming degradation to your judge prompt in a copy of the config (delete the instruction that evidence must be quoted verbatim, or weaken one criterion's rubric text).  Re-run and diff:

    ```bash
    npx promptfoo@latest eval -c promptfooconfig-regressed.yaml --output run_regressed.json
    ```

    Identify which items' verdicts changed and in which direction.  Then revert the change and confirm the baseline verdicts recover.

5.  **Commit the configuration** to the project repository alongside the code, with a comment header stating the model, temperature, and seed it was validated against.  From here on the harness *is* your verification of the judge; the table you built today is its first golden set.

If promptfoo cannot reach Ollama, set the provider to Ollama's OpenAI-compatible endpoint, e.g. `openai:chat:llama3.2` with `apiBaseUrl: http://localhost:11434/v1` (any non-empty API key satisfies the client), and verify first with `curl http://localhost:11434/v1/models`.

[[___ Pass rate on the baseline run, pass rate on the regressed run, and the commit hash ___]]

### Critical Thinking Questions

**Question 7.**  Before the first harness run, predict which assertion will fail.  Then explain why a failing assertion on the first run is the harness doing its job rather than a reason to loosen the assertion.

[[___ Your prediction and answer here ___]]

*Hint:* The row you audited but did not repair is the likely failure.  Loosening an assertion to make it pass converts a tripwire into decoration; the honest moves are to repair the rubric, repair the artifact, or record the disagreement as a known limitation and keep the assertion red.

**Question 8.**  Your governance one-pager's section 6 promises an audit schedule and "the harness that produces the data."  After today, name the file in your repository that is that harness, the command that runs it, and the one thing the policy promised that the harness still cannot measure.

[[___ Your answer here ___]]

*Hint:* Disaggregation by population is the usual gap: a golden set of three artifacts cannot tell you whether the judge treats two user groups differently.  Say so in the policy rather than letting the promise stand.

---

## 4.  Triage (8 minutes)

The Coordinator reads each remaining row of the disagreement table aloud and the team sorts it into exactly one bucket: **Fix before December 1** (a rubric or artifact repair you can make and re-run before the gallery walk), **Disclose in the report** (a real disagreement you understand and will state in the limitations section, in one honest sentence), or **Future work**.  The Scribe converts the first bucket into assigned, dated backlog items on the spot, and writes the disclosure sentences for the second.

[[___ Your triage table here ___]]

## 5.  Evaluation Readiness Check

Two of these rows come from the release-readiness checklist you will sign on December 1; the other two are today's additions.  "Yes" requires evidence, not belief.

| Item | Check | Evidence Required |
|------|-------|-------------------|
| 2. The evaluation table (harness, metrics, monolith baseline comparison) is current and in the repository | Yes / No | Link to the file in the repository; confirm the date on the most recent run |
| 6. Reproducibility: seeds fixed, model versions pinned and listed, setup steps tested by the teammate who did not write them | Yes / No | The teammate who did not write the README has successfully set up the system from scratch |
| 7. The judge's golden set and assertions live in the project repository and run with one command | Yes / No | The command, and the pass rate it printed today |
| 8. One disagreement is audited to its evidence, repaired, and re-run | Yes / No | The Scribe's audit record from Model 2 |

---

## 6.  Exercises

**Exercise 1.**  Write the one-sentence disclosure for each row in your "Disclose in the report" bucket.

*What to do:* For each row, draft one sentence in this form: "On [criterion], the judge and our human scorers disagree by [gap] on [kind of artifact] because [the reason the audit found], and we [repaired it / report it as a limitation]."

*Starter hint:* A good disclosure: "On C3, the judge scores summaries of documents without a counterargument section one level higher than our human scorers, because the descriptor rewards any mention of an opposing view; we rewrote the descriptor and report the pre-repair gap here."  A bad disclosure: "The judge is sometimes a little off on C3."

*You've succeeded when:* Each sentence names the criterion, the gap, the cause, and what you did about it, and a reader who has never seen your rubric can tell how much to trust the number.

[[___ Your disclosure sentences here ___]]

**Exercise 2.**  Add the mechanical validator from Question 4 to your judge and report its result on today's three artifacts.

*What to do:* For every quoted span the judge returns, assert that it appears verbatim in the artifact (exact substring on the code route; a `javascript` assertion that parses the JSON first on Direction 0).  Count the quotes that fail.

*Starter hint:* The lab's `HALLUCINATED_EVIDENCE` marker is the code-route shape: flag the row in the CSV and report the rate as a fraction ("1 of 12 quotes").  The point is that the check runs without anyone reading a trace.

*You've succeeded when:* The validator runs as part of the harness, and your report states a hallucinated-evidence rate for the three artifacts, even if it is zero.

[[___ Your validator result here ___]]

**Exercise 3.**  Run the shown-versus-hidden audit step from Model 2 on the three artifacts.

*What to do:* If your judge emits a trace, score the three artifacts once with the trace visible and once with it hidden (the Builder redacts it before the scorers see the output).  Compute agreement with the judge in each condition using the Code Cell.

*Starter hint:* If your judge does not emit a trace, hide the judge's one-sentence evidence field instead; the question is the same: does seeing the judge's argument change your score?

*You've succeeded when:* You have two agreement numbers per criterion and one sentence saying what the difference between them means for how you will audit the judge in the report.

[[___ Your two conditions and interpretation here ___]]

---

## Reflection Prompt

**Personal level:** Where in today's table did you find yourself wanting to move a human score toward the judge's after you saw it?  What did the blind-first rule protect you from, and where else in your work do you read the machine's answer before forming your own?

**Technical level:** The harness you committed today will pass or fail on every future change to your judge.  Name one change to your project that would break the harness for a good reason (the rubric improved and the golden set is now stale) and one that would break it for a bad reason (the prompt regressed).  How would a teammate reading only the failing run tell the two apart?

> *Hint:* The comment header on the config (model, temperature, seed) and the commit that touched the rubric are the two signals.  If the rubric changed, the golden set needs re-scoring by humans; if only the prompt changed, the failure is a regression.  A harness that cannot distinguish the two will be ignored the first time it is wrong.

**Societal level:** Your policy promises an audit schedule.  Today showed how much human time one audited disagreement costs.  If that cost is what a real audit looks like, who pays it in a deployed system, and what happens to the promise when nobody does?

Write a combined reflection of 150-200 words addressing at least two of the three levels.  The Evaluator should be prepared to report the team's largest gap and its repair to the class.

[[___ Your reflection here ___]]

---

-> Coming Up Next: *Project Studio: Sprint and Threat Model* (Tuesday, November 24) opens with the cross-team proposal review round, gives your team a thirty-minute sprint block, and then turns the incident simulation from the case-studies material on your own system: what an outsider could write that your agent will read, and what you would do in the first hour after it went wrong.  Bring today's committed harness; it is item 7 on the readiness check, and the sprint block is where the "Fix before December 1" bucket gets worked.  The Rubric Pipeline lab is due that day.

---

## 7.  Further Reading

- Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena."  *NeurIPS* (2023).  Pathologies and agreement rates.
- Hashemi et al. "LLM-Rubric: A Multidimensional, Calibrated Approach to Automated Evaluation."  *ACL* (2024).
- The [Rubric Pipeline lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RubricPipeline), Parts 2 and 5, and the [Direction 0 promptfoo route](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RubricPipeline/Direction0), Part E, which today's Models 1 and 3 reuse.
- [promptfoo](https://www.promptfoo.dev/) and [Inspect AI](https://inspect.aisi.org.uk/), the two harnesses the lab accepts.
