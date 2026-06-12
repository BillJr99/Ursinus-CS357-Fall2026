# Training Data and Bias
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-biasdata.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-biasdata.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Training Data and Bias

Unit 4 begins where every model begins: with data. You watched *Coded Bias* before class; today we connect Joy Buolamwini's discovery (facial analysis failing darkest-skinned women at rates orders of magnitude above lightest-skinned men) to the mechanics you now command: training distributions, sampling, consensus, and agents that *act*. The arc: **where bias enters $\rightarrow$ measuring it $\rightarrow$ what agents add to the stakes $\rightarrow$ mitigations and their limits**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today's questions include matters on which thoughtful people disagree; the Reflector's added duty is to notice when the team converges too quickly and to voice the strongest absent perspective. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Mechanism

## 1. Bias Is a Property of the Pipeline, Not a Bug in the Weights

**Models learn the distribution they are fed.** A language model's probabilities estimate $P(\text{text})$ over its training corpus; whatever that corpus over- or under-represents, the model reproduces, and our *consensus* machinery amplifies, since the mode of a skewed distribution is its skew. *Coded Bias* documents the input side: benchmark face datasets that were overwhelmingly light-skinned and male, making error rates invisible until someone disaggregated them.

**Bias enters at every stage.** *Collection*: who is in the data (whose web pages, whose dialect, whose images). *Labeling*: whose judgments define ground truth. *Objective*: what the loss function rewards (fluency, not fairness). *Deployment*: on whom the system is used versus on whom it was validated, which is the gap Buolamwini fell into, literally, when a system failed to see her face until she wore a white mask.

**Measurement requires disaggregation.** An aggregate accuracy of 95 percent can decompose into 99 percent for one group and 70 percent for another:

$$
\text{report } \text{acc}_g = \frac{1}{|G_g|} \sum_{i \in G_g} \mathbb{1}[\hat{y}_i = y_i] \ \text{ for each group } g, \text{ never only the mean.}
$$

This is the single most transferable habit from today: *never trust an average you have not disaggregated*.

---

## Model 1: Scenes from Coded Bias

Recall three scenes: the white-mask discovery; the Brooklyn apartment complex where tenants resisted landlord-installed facial-entry systems; and the UK police van trials misidentifying pedestrians.

### Critical Thinking Questions

1. For each scene, locate the bias entry point using the four stages above, with one sentence of justification each.
2. The apartment tenants were not the system's *customers*; they were its *subjects*. Define both terms for an AI deployment, and explain why the distinction predicts who bears error costs.
3. The film predates modern LLM agents. For each scene, write its nearest 2026 agentic analogue (an agent screening rental applications, an agent flagging exam misconduct, and so on).

---

# Part II: Hands on the Distribution

## 2. Probing a Local Model

We probe associations in your local model the disciplined way: many samples, counted, disaggregated. (We probe occupations, a domain where training-text skew is well documented.)

---

## Code Cell

```python
import requests
from collections import Counter

def chat(prompt, temperature=1.0):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": temperature},
            "messages": [{"role": "user", "content": prompt}]}, timeout=120)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[biasdata:chat] {e}")
        import traceback; traceback.print_exc()
        return ""

def pronoun_count(occupation, n=12):
    counts = Counter()
    prompt = (f"Write one sentence about the {occupation} finishing their shift, "
              f"using a third-person pronoun for them.")
    for _ in range(n):
        text = chat(prompt).lower()
        for p, label in [(" she ", "she"), (" her ", "she"), (" he ", "he"),
                         (" his ", "he"), (" they ", "they"), (" their ", "they")]:
            if p in " " + text + " ":
                counts[label] += 1
                break
    return counts

for occ in ["nurse", "engineer", "kindergarten teacher", "electrician"]:
    print(occ, dict(pronoun_count(occ)))
```

---

## Model 2: Reading the Counts

### Critical Thinking Questions

4. Tabulate your team's counts. Do pronoun distributions track real workforce demographics, exaggerate them, or contradict them? Why is *each* of those three outcomes a design decision someone made or failed to make?
5. This probe used $n = 12$ samples per occupation. Compute how confident you should be in a 9-versus-3 split (a sign test or just intuition about coin flips is fine), and restate the week 3 lesson about protocols before claims.
6. Suppose a hiring-assistant *agent* drafts outreach messages and, primed by such associations, subtly varies warmth by inferred gender. No single message is damning. What measurement, run over *many* drafts, would expose the pattern, and which of our pipelines (judge, disaggregated harness) is the right instrument?

[[MC]]
A resume-screening agent shows equal average approval rates overall but was validated only on resumes from one region's universities. The *Coded Bias*-informed concern is:
- ( ) Average approval is the wrong metric; throughput matters more
- (x) Performance may degrade sharply on groups absent from validation data, and the aggregate hides it
- ( ) The model's temperature was too high
- ( ) Agents cannot exhibit bias because they follow prompts

---

# Part III: Mitigation Without Illusion

## 3. The Toolbox and Its Limits

Mitigations exist at every stage: curate and document data (datasheets, model cards), disaggregate evaluation by default, constrain agents with explicit criteria (a rubric that scores qualifications is harder to skew than vibes), keep humans on consequential decisions, and, the *Coded Bias* throughline, support accountability from *outside* the system, because Buolamwini's audit, not the vendor's, found the failure. No mitigation is complete: documentation can be ignored, rubrics can encode bias in politer language, and human reviewers bring their own. The honest stance is layered defenses plus measurement, not declarations of fairness.

---

## 4. Exercises

1. *Disaggregation drill.* Take your Lab 5 rubric pipeline and a set of short essays; vary only the author byline (names connoting different genders/origins) on otherwise identical essays. Report per-byline score distributions. Any gap is a judged bias you must now explain or fix.
2. *Datasheet sprint.* Write a one-page datasheet for the corpus you indexed in Lab 2: sources, time range, who is represented, who is absent, known limitations. Append it to your project repository.
3. *Audit proposal.* Buolamwini audited from outside. Design an external audit (data needed, access required, metric, publication venue) for any agent system on a campus. What access would the operator have to grant, and what incentive do they have to refuse?

---

## Reflection Prompt

In your notebook: *Coded Bias* argues that the question is not whether AI systems are biased but who has the power to find out and to demand repair. After this semester, you can build, measure, and audit. Which of those three capabilities do you feel most responsible to exercise, and in what setting will you first get the chance?

---

## 5. Further Reading

- *Coded Bias* (2020), dir. Shalini Kantayya, and Buolamwini and Gebru, "Gender Shades." *FAccT* (2018).
- Gebru et al. "Datasheets for Datasets." *CACM* (2021); Mitchell et al. "Model Cards for Model Reporting." *FAccT* (2019).
- Bender, Gebru, McMillan-Major, and Mitchell. "On the Dangers of Stochastic Parrots." *FAccT* (2021).
