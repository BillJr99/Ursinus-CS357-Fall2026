<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-llmasjudge.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-llmasjudge.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Evaluating Agents: LLM-as-Judge and Rubric Pipelines

Exact-match accuracy (our metric since the *Hallucinations and Evaluating Agent Outputs* activity) served us when answers were one word; agent outputs are essays, plans, and code, and judging *those* at scale requires recruiting a model as the **judge**.  Today we build a **rubric pipeline**: structured criteria in, JSON scores out, validated against human judgment, which is the architecture of the Rubric Pipeline Lab and a live research problem in AI for education.  Here is where today goes: **why scale forces this $\rightarrow$ rubric design $\rightarrow$ a judging pipeline in code $\rightarrow$ auditing the judge itself**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **LLM-as-judge (Large Language Model as judge)** | Using an AI model as an automated grader that reads an artifact, applies a rubric, and outputs a structured score, the same role a human grader plays, but executable thousands of times per minute. | The `judge()` function calls `llama3.2` with a rubric and an essay, and the model returns JSON scores with quoted evidence. |
| **Rubric** | A scoring guide that lists each quality criterion, describes what each level of performance looks like in observable, verifiable terms, and assigns a weight to each criterion. | The rubric in the code has three criteria: `claims_cited` (50%), `directness` (30%), `counterargument` (20%). |
| **Observable descriptor** | A level description that refers to something you can actually see in the text, not a judgment of quality, but a factual statement about what is or is not present. | "Every claim cites a source" is observable (you can count claims and citations). "Is insightful" is not observable (it is a judgment). |
| **Position bias** | The tendency of an LLM judge to rate the first answer in an A/B comparison higher than the second, regardless of which answer is actually better. | If you always put the AI-generated essay first and the human essay second, your judge may systematically favor the AI, not because it is better, but because it came first. |
| **Verbosity bias** | The tendency of an LLM judge to rate longer answers as higher quality, even when the extra length adds no meaningful content. | Adding two empty filler sentences to an essay before submitting it to the judge, and watching the score go up. |
| **Calibration set** | A small collection of artifacts that have already been scored by humans, used to check whether the LLM judge agrees with human judgment before trusting it on new artifacts. | Ten essays scored by your team and by the judge; if they disagree on criterion 2 consistently, that criterion needs better descriptors. |

---

# Part I: Judgment at Scale

In this part, you will examine what a rubric actually is, why vague rubrics produce unreliable scores, and how the same design mistakes show up whether the grader is human or AI. This foundation determines whether the judge you build in Part II is trustworthy.

## Model 1: Rubric Autopsy

Think of academic peer review.  A journal sends a submitted paper to three expert reviewers, each of whom independently evaluates the work against a list of criteria (originality, methodology rigor, clarity of writing, significance of results) and assigns scores with written justifications.  The editors synthesize the reviews.  LLM-as-judge is the same process, automated: the rubric is the reviewer's checklist, the judge's prompt is the call to review, and the JSON output is the review report.  The crucial insight from peer review carries over: a vague criterion ("is this paper good?") produces unreliable reviews, while a precise criterion ("does the methodology section specify sample size, exclusion criteria, and statistical tests?") produces reviews that different reviewers agree on.  Today we apply that lesson to AI-generated rubrics.

Human judgment is the gold standard and does not scale.  Grading 200 essays against a rubric takes a person a week; an evaluation harness needs thousands of judgments per experiment.  **LLM-as-judge** substitutes a model, prompted with the rubric, the artifact, and a demand for structured output.  Used well, it correlates strongly with human raters on well-specified criteria; used carelessly, it imports every bias of the underlying model into your measurements, silently.

A rubric is the contract.  Following our assignment rubrics, we specify per-criterion *levels with observable descriptors* and a weight:

$$
\text{score} = \sum_{c} w_c \cdot \frac{\ell_c}{L}
$$

where $w_c$ is criterion $c$'s weight, $\ell_c$ the awarded level, and $L$ the top level.  Observable descriptors ("cites a source for each claim") judge reliably; aesthetic ones ("is insightful") do not, the same lesson the critique-refine module taught about actionable feedback.

**Known judge pathologies (systematic errors the judge makes consistently, not randomly).**  *Position bias*: in A/B comparisons, judges favor the first-presented response.  *Verbosity bias*: longer answers score higher at equal quality.  *Self-preference*: models rate their own outputs more generously than outputs from other models.  *Leniency drift*: scores compress toward the top of the scale over many judgments, making it hard to distinguish good from excellent.

Every pipeline we build must include countermeasures: randomized order, length-blind criteria, a different judge model than the generator, and anchor examples showing what each level actually looks like.

A draft rubric for short essays: (1) "Well written, 40 percent"; (2) "Good use of evidence, 40 percent"; (3) "Proper length, 20 percent."

| Criterion (draft) | Problem with this version | Improved version |
|---|---|---|
| "Well written, 40 percent" | "Well written" is not observable; different judges will disagree on what it means, making scores unreliable. | Split into two observable criteria: "Each sentence expresses exactly one idea (no run-ons)" and "Position is stated in the first paragraph." |
| "Good use of evidence, 40 percent" | "Good use" is a judgment, not a description. Vulnerable to verbosity bias: a judge may reward quantity of citations over quality. | "Every factual claim is followed by a parenthetical source. Sources are cited in the text, not only in a bibliography." |
| "Proper length, 20 percent" | Length is trivially machine-checkable with `len(text.split())`. Sending it to an LLM judge wastes tokens and adds noise. | Replace with a programmatic check: `assert 150 <= word_count <= 300`. Save the LLM for criteria that require reading comprehension. |

### Critical Thinking Questions

1.  Rewrite criterion 1 ("Well written") with four observable levels labeled preemerging, beginning, progressing, and proficient.  What changed about *verifiability*, meaning, could two different people independently arrive at the same level?

   *Hint:* Preemerging might be "no clear thesis statement anywhere in the essay."  Proficient might be "thesis stated in the first sentence of the first paragraph, consistent throughout."  Check each level: could you identify it by reading the first sentence only, without making a judgment call?

2.  Criterion 3 ("Proper length") is the only machine-checkable one; should it be sent to the LLM judge at all?  Propose the cheaper instrument and state the general principle about what belongs in an LLM rubric versus what belongs in a programmatic check.

   *Hint:* One line of Python (`150 <= len(essay.split()) <= 300`) is more reliable, cheaper, and faster than an LLM call.  The general principle: use an LLM only when the criterion requires reading comprehension that a simple rule cannot capture.

3.  Which judge pathology (position bias, verbosity bias, self-preference, or leniency drift) threatens criterion 2 ("Good use of evidence") most, and which countermeasure from Section 1 do you prescribe?

   *Hint:* Criterion 2 asks about citations.  A longer essay has more opportunities to include citations, even superficial ones.  Which pathology does that suggest?  How would you rewrite the descriptor to be length-neutral?

---

# Part II: The Pipeline

In this part, you will turn the rubric you analyzed in Part I into working code: a `judge()` function that sends an essay and the rubric to your local model and gets back a structured score with quoted evidence.  Run the code yourself, then answer the questions to understand what the judge is doing and where it can go wrong.

## Model 2: Rubric In, JSON Out, CSV Forever

The function below sends an essay to your local Ollama model along with a rubric and receives a JSON-formatted score (a structured text format using `{key: value}` pairs) with one entry per criterion.  Setting `temperature=0.0` and `seed=42` makes the judge give the same score every time for the same input, important for fairness, as you'll explore in Question 5.

---

## Code Cell

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

---

### Critical Thinking Questions

4.  The prompt demands quoted *evidence* for every score.  Which judge pathology does this most directly counter, and how would you automatically spot-check that the quoted sentences actually appear in the artifact (rather than being fabricated by the judge)?

   *Hint:* If the judge invents a sentence that does not appear in the essay, that is a hallucination.  One line of Python can catch it: `assert detail["scores"]["claims_cited"]["evidence"] in essay`.  What pathology does requiring a real quote discourage?

5.  Run the same essay through the judge three times at temperature 0 with a fixed seed, then three times at temperature 0.7.  Report score variance in both conditions, and state which configuration a grading pipeline must use and why.

   *Hint:* At temperature 0 with a fixed seed, the model makes the same token choices every time.  At temperature 0.7, choices vary.  For a grading pipeline used on student work, what is the professional obligation when it comes to consistency?

6.  Pad the essay with two flattering but content-free sentences ("This essay was written with great care and attention to detail.  The author is deeply knowledgeable about campus issues.") and re-judge.  Did any criterion move?  Name the bias you just probed, and explain why the existing rubric descriptors are or are not resistant to it.

   *Hint:* The two added sentences contain no citations, no counterargument, and no new position.  If the score goes up, which pathology is responsible?  Does the criterion descriptor for `claims_cited` say anything about the *ratio* of cited claims to total claims, or just whether citations exist?

The most important safeguard before trusting an LLM judge's scores on real student work is:

[( )] Using the largest available model as the judge, because bigger models are inherently fairer
[( )] Setting temperature to 0, because that eliminates bias by making the model deterministic
[(X)] Validating the judge's scores against human scores on a labeled calibration set before using it on new work
[( )] Asking the judge to be fair in the system prompt, so it knows to ignore its biases

> **Common Misconception:** A very common mistake is to believe that setting the judge's temperature to 0 guarantees fair, unbiased grading.  Temperature 0 makes the judge *consistent* (it will give the same score every time for the same input), but consistency is not the same as accuracy.  A consistently biased judge that always over-scores verbose essays is worse than a slightly inconsistent but well-calibrated one, because the bias is systematic and invisible.  The only way to catch systematic bias is to compare judge scores to human scores on a set of pre-graded examples (a calibration set) before using the judge on new work.

---

# Part III: Auditing the Judge

Now that you have a working judge and understand its failure modes, this part asks you to stress-test it in ways that mirror real deployment risks: measuring human agreement, quantifying position bias, and building the batch infrastructure for the Rubric Pipeline Lab.

## Exercises

1.  *Human agreement.*

   *What to do:* Each teammate independently hand-scores the sample essay and two more essays you write yourself, using only the rubric, without seeing the judge's output first.  Then reveal the judge's scores and compute: (a) agreement between humans, and (b) agreement between each human and the judge.  Report which criterion shows the worst machine-human gap.

   *Starter hint:* "Agreement" here can be as simple as: for each criterion, how often does the human and the judge choose the same level (out of 4)?  A gap of more than 1 level on a consistent basis signals a rubric descriptor that needs revision.

   *You've succeeded when:* You can name the specific criterion where machine-human disagreement is largest, quote the level descriptor that caused confusion, and propose a one-sentence revision that would make the criterion clearer.

2.  *Position bias measurement.*

   *What to do:* Build an A/B comparator prompt that asks "which essay better satisfies the rubric?"  Feed it the same pair of essays in both orders (A then B, then B then A) for five different pairs.  Report the rate at which the judge changes its answer when the order flips, your first directly measured bias.

   *Starter hint:* The comparator prompt should be: "Given these two essays and the rubric below, which essay scores higher overall?  Answer only 'ESSAY_A' or 'ESSAY_B'."  Run it twice per pair, swapping positions.  If the answer changes when you swap, that is a position-bias instance.

   *You've succeeded when:* You have a flip rate (e.g., "the judge changed its answer in 3 of 5 pairs when order was reversed") and can state what this means for the reliability of A/B comparisons in your evaluation harness.

3.  *Batch pipeline.*

   *What to do:* Wrap the `judge` function in a loop over a folder of text files and emit one CSV (comma-separated values) row per artifact, with columns for filename, per-criterion level, evidence quote, and weighted total score.  This is the skeleton of the Rubric Pipeline Lab; save your CSV; it feeds directly into that lab.

   *Starter hint:* Use `import os; os.listdir("essays/")` to get filenames, `open(filepath).read()` to load each essay, and `import csv; writer.writerow([...])` to append to the CSV. Wrap each judge call in a `try/except` so one parse error does not stop the whole batch.

   *You've succeeded when:* You have a CSV file with at least 5 rows (one per essay) that opens correctly in a spreadsheet, and you can sort by weighted total to identify the highest- and lowest-scoring essays at a glance.

4.  *Judge the judge's rubric.*

   *What to do:* Trade rubrics with another team.  Attempt to write a "reward-hacked" essay, one that maximally satisfies the letter of their rubric descriptors while being as substantively weak as possible.  Report the loophole you found and propose the one-sentence patch that closes it.

   *Starter hint:* Reward hacking means gaming the rules.  If their rubric says "cites at least one source," you can cite a source for every sentence, even the filler sentences.  If it says "counterargument mentioned," one throwaway sentence ("Some disagree") might satisfy the level.  Find the weakest descriptor and exploit it.

   *You've succeeded when:* You can show a weak essay that scores in the top level on at least two criteria under the other team's rubric, identify the specific word or phrase in the descriptor that permitted the exploit, and write a revised descriptor that would have caught it.

---

## Reflection Prompt

*Personal:* An instructor uses an LLM judge for first-pass formative feedback (feedback intended to help you improve, not to determine your grade) on drafts, with full disclosure to students.  A classmate objects on principle.  Write the strongest possible sentence of the objection and the strongest possible sentence of the defense, then state where you personally land today, knowing that your Rubric Pipeline Lab builds exactly this machinery.

*Technical:* The rubric pipeline produces a score and a quoted evidence string for each criterion.  Describe a complete audit protocol you would run before deploying this pipeline on a real class of students: what data you would collect, what agreement threshold you would require, and what you would do if the judge fails the audit on one criterion but passes on others.

*Societal:* LLM judges are already being used in hiring (resume scoring), college admissions (essay review assistance), and parole decisions (risk assessment).  For each of these three contexts, state whether you believe LLM-as-judge is appropriate, under what conditions, and who should be responsible for running the calibration audit.  Are these three cases meaningfully different from each other?

---

-> Coming Up Next: You just built a machine that assigns grades, and then found the biases in it.  Next session, *Training Data and Bias*, follows that thread all the way down: where the judge's preferences came from in the first place, and what it means to deploy a scoring system on people.  The rubric pipeline you built today is the architecture of the Rubric Pipeline Lab.

## Further Reading

- Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena."  *NeurIPS* (2023).  Pathologies and agreement rates.
- Hashemi et al. "LLM-Rubric: A Multidimensional, Calibrated Approach to Automated Evaluation."  *ACL* (2024).
- Your course's MENTIR-AI context: AI analysis of student mathematical thinking is live research on exactly these questions.
