# Evaluating Agents: LLM-as-Judge and Rubric Pipelines
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-llmasjudge.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmasjudge.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Evaluating Agents: LLM-as-Judge and Rubric Pipelines

Exact-match accuracy served us when answers were one word; agent outputs are essays, plans, and code, and judging *those* at scale requires recruiting a model as the **judge**. Today we build a **rubric pipeline**: structured criteria in, JSON scores out, validated against human judgment, which is the architecture of Lab 5 and a live research problem in AI for education. The arc: **why scale forces this $\rightarrow$ rubric design $\rightarrow$ a judging pipeline in code $\rightarrow$ auditing the judge itself**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Judgment at Scale

## 1. The Setup and the Stakes

**Human judgment is the gold standard and does not scale.** Grading 200 essays against a rubric takes a person a week; an evaluation harness needs thousands of judgments per experiment. **LLM-as-judge** substitutes a model, prompted with the rubric, the artifact, and a demand for structured output. Used well, it correlates strongly with human raters on well-specified criteria; used carelessly, it imports every bias of the underlying model into your measurements, silently.

**A rubric is the contract.** Following our assignment rubrics, we specify per-criterion *levels with observable descriptors* and a weight:

$$
\text{score} = \sum_{c} w_c \cdot \frac{\ell_c}{L}
$$

where $w_c$ is criterion $c$'s weight, $\ell_c$ the awarded level, and $L$ the top level. Observable descriptors ("cites a source for each claim") judge reliably; aesthetic ones ("is insightful") do not, the same lesson the critique-refine module taught about actionable feedback.

**Known judge pathologies.** *Position bias*: in A/B comparisons, judges favor the first-presented response. *Verbosity bias*: longer answers score higher at equal quality. *Self-preference*: models rate their own outputs generously. *Leniency drift*: scores compress toward the top of the scale. Every pipeline we build must include countermeasures: randomized order, length-blind criteria, a different judge model than the generator, and anchor examples.

---

## Model 1: Rubric Autopsy

A draft rubric for short essays: (1) "Well written, 40 percent"; (2) "Good use of evidence, 40 percent"; (3) "Proper length, 20 percent."

### Critical Thinking Questions

1. Rewrite criterion 1 with four observable levels (preemerging, beginning, progressing, proficient). What changed about *verifiability*?
2. Criterion 3 is the only machine-checkable one; should it be sent to the LLM judge at all? Propose the cheaper instrument and state the principle.
3. Which judge pathology threatens criterion 2 most, and which countermeasure from Section 1 do you prescribe?

---

# Part II: The Pipeline

## 2. Rubric In, JSON Out, CSV Forever

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

## Model 2: Interrogating the Judge

### Critical Thinking Questions

4. The prompt demands quoted *evidence* for every score. Which judge pathology does this most directly counter, and how would you spot-check that the quotes are real (not hallucinated) automatically?
5. Run the same essay through the judge three times at temperature 0 with a fixed seed, then three times at temperature 0.7. Report score variance in both conditions, and state which configuration a grading pipeline must use and why.
6. Pad the essay with two flattering but content-free sentences and re-judge. Did any criterion move? Name the bias you just probed.

[[MC]]
The most important safeguard before trusting an LLM judge's scores on real student work is:
- ( ) Using the largest available model as the judge
- ( ) Setting temperature to 0
- (x) Validating the judge's scores against human scores on a labeled calibration set
- ( ) Asking the judge to be fair in the system prompt

---

# Part III: Auditing the Judge

## 3. Exercises

1. *Human agreement.* Each teammate hand-scores the sample essay (and two more you write) with the rubric *before* seeing the judge's output. Compute agreement between humans, then between humans and the judge. Which criterion shows the worst machine-human gap?
2. *Position bias measurement.* Build an A/B comparator prompt ("which essay better satisfies the rubric?") and feed it the same pair in both orders for five pairs. Report the order-flip rate, your first measured bias.
3. *Batch pipeline.* Wrap `judge` in a loop over a folder of text files and emit one CSV row per artifact (filename, per-criterion level, evidence, weighted total). This is the skeleton of Lab 5; bring your CSV to the next class.
4. *Judge the judge's rubric.* Trade rubrics with another team and attempt to reward-hack theirs with a maximally rubric-satisfying, minimally good essay. Report the loophole and the patch.

---

## Reflection Prompt

In your notebook: an instructor uses an LLM judge for *first-pass formative feedback* (never final grades) on drafts, with disclosure. A classmate objects on principle. Write both the strongest sentence of the objection and the strongest sentence of the defense, then state where you land today, knowing your Lab 5 builds exactly this machinery.

---

## 4. Further Reading

- Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." *NeurIPS* (2023). Pathologies and agreement rates.
- Hashemi et al. "LLM-Rubric: A Multidimensional, Calibrated Approach to Automated Evaluation." *ACL* (2024).
- Your course's MENTIR-AI context: AI analysis of student mathematical thinking is live research on exactly these questions.
