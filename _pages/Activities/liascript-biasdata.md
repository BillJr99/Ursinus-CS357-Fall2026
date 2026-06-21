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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Training distribution** | The full set of text or images a model was trained on — its "diet" of data; the model learns to reproduce the patterns in this distribution, including its gaps and skews. | A language model trained mostly on English-language websites will associate "nurse" more strongly with feminine pronouns than with masculine ones, because that association appears more often in the training text. |
| **Bias (in AI)** | A systematic difference in model performance or outputs across demographic groups, caused by patterns in training data, labeling choices, or deployment context — not a random error, but a consistent one that disadvantages specific groups. | The facial recognition systems in *Coded Bias* had error rates above 30% for dark-skinned women but below 1% for light-skinned men, because benchmark datasets used for training and testing were overwhelmingly light-skinned and male. |
| **Disaggregation** | Reporting performance metrics separately for each subgroup (by gender, race, age, income level, etc.) rather than only reporting an overall average, which can hide large disparities between groups. | A resume-screening model with 95% overall accuracy might be 99% accurate for applicants from one university and 70% accurate for applicants from another — disaggregation reveals this; a single average conceals it. |
| **Labeling bias** | Errors or skews introduced at the stage where humans assign labels to training data — for example, if annotators consistently describe the same behavior differently depending on the race of the person depicted. | Human annotators in sentiment analysis tasks have been shown to rate identical text as more "aggressive" when they believe the author is Black, introducing racial bias into the labeled training set. |
| **Datasheet for datasets** | A standardized documentation format that records who collected a dataset, what it contains, who is represented, who is missing, known limitations, and intended and prohibited uses — making the data's properties auditable. | The datasheet for your Lab 2 corpus would record the publication dates of included documents, the languages covered, which authors or regions are over- or under-represented, and whether any demographic group is systematically absent. |
| **Disaggregated evaluation** | Running your model's evaluation metrics separately for each subgroup and reporting all subgroup metrics alongside the overall metric — the single most important habit this module teaches. | Instead of reporting "the judge pipeline scores essays with 85% agreement with humans," you report "85% overall, 91% for essays on scientific topics, 74% for essays on social topics, 88% for longer essays, 79% for shorter essays." |

---

# Part I: Mechanism

In this part, you will trace exactly how bias enters an AI system — not as a one-time mistake, but at multiple stages from data collection through deployment. The goal is to shift from thinking "this model is biased" (vague) to "bias entered at this specific stage for this specific reason" (actionable).

## Model 1: Bias Is a Property of the Pipeline, Not a Bug in the Weights

Think of a newspaper that has been published for 100 years. If you trained a language model on every issue, the model would learn associations that reflect 100 years of editorial decisions: which occupations were described as prestigious, whose names appeared in which sections, whose voices were quoted as experts. None of this is a "bug" in the newspaper's printing press — it is a property of the cultural context in which the newspaper was written. An AI model trained on that newspaper inherits those associations. Today's code probe will show you exactly this: not a flaw in the model's reasoning, but the statistical echo of who wrote the text it was trained on.

**Models learn the distribution they are fed.** A language model's probabilities estimate $P(\text{text})$ over its training corpus; whatever that corpus over- or under-represents, the model reproduces — and our *consensus* machinery amplifies, since the mode (most common value) of a skewed distribution is its skew. *Coded Bias* documents the input side: benchmark face datasets that were overwhelmingly light-skinned and male, making error rates invisible until someone disaggregated them (broke results apart by demographic group).

**Bias enters at every stage.** *Collection*: who is in the data (whose web pages, whose dialect, whose images). *Labeling*: whose judgments define ground truth. *Objective*: what the loss function (the mathematical measure the model is trained to minimize) rewards — typically fluency, not fairness. *Deployment*: on whom the system is used versus on whom it was validated — which is the gap Buolamwini fell into, literally, when a system failed to see her face until she wore a white mask.

**A concrete worked example of training-data bias.** Suppose a model is trained on a corpus that includes many sentences like these:

- "The nurse handed the patient her chart."
- "Ask the nurse — she'll know what medication is needed."
- "The engineer reviewed his blueprints before the meeting."
- "The electrician called his supervisor about the wiring issue."

After seeing thousands of sentences like these, the model learns a strong association: *nurse* → *she*, *engineer* → *he*. This is not a random error. It reflects real historical gender distributions in those occupations — but it also *perpetuates* them. When a hiring assistant agent primed by this model drafts outreach to "nurses," it may subtly adjust its language in ways that feel more welcoming to women — systematically, across thousands of messages, without any single message being visibly discriminatory.

**Measurement requires disaggregation.** An aggregate accuracy of 95 percent can decompose into 99 percent for one group and 70 percent for another:

$$
\text{report } \text{acc}_g = \frac{1}{|G_g|} \sum_{i \in G_g} \mathbb{1}[\hat{y}_i = y_i] \ \text{ for each group } g, \text{ never only the mean.}
$$

This is the single most transferable habit from today: *never trust an average you have not disaggregated*.

---

Recall three scenes from *Coded Bias*: the white-mask discovery; the Brooklyn apartment complex where tenants resisted landlord-installed facial-entry systems; and the UK police van trials misidentifying pedestrians.

| Scene | Setting | Who was harmed | What the system got wrong | Bias entry point |
|---|---|---|---|---|
| **White-mask discovery** | MIT Media Lab research study | Dark-skinned women most severely | Facial analysis systems failed to detect Buolamwini's face until she wore a white mask; error rates for dark-skinned women were more than 10x higher than for light-skinned men. | Collection: benchmark datasets used for training and testing were overwhelmingly light-skinned and male, so the system was never validated on the demographic it failed. |
| **Brooklyn apartment complex** | Residential building, New York | Tenants without their consent | Landlord installed facial recognition entry system; tenants (disproportionately people of color) were subjects of a surveillance system they did not choose and could not opt out of. | Deployment: the system was deployed on a population (low-income renters) who were absent from the governance decisions about its use, and who bore the risk while the landlord captured the benefit. |
| **UK police van trials** | Public streets, Cardiff | Pedestrians misidentified as suspects | Real-time facial recognition deployed from police vans misidentified innocent people as wanted individuals at high rates, particularly for people of color. | Labeling: criminal databases used as "ground truth" for suspect identification reflect historical over-policing of certain communities, encoding systemic inequities into the model's definition of who is a suspect. |

### Critical Thinking Questions

1. For each of the three scenes above, identify the bias entry point using the four stages (collection, labeling, objective, deployment) and write one sentence of justification for your choice. Note that some scenes involve multiple entry points.

   *Hint:* The table above identifies one entry point per scene. Can you identify a second entry point for at least one scene? For example, the police van trial involves both labeling (biased criminal databases) and deployment (using the system on a population not represented in validation data).

2. The apartment tenants were not the system's *customers* (the landlord was); they were its *subjects*. Define both terms for an AI deployment: who is a customer, and who is a subject? Explain why the customer/subject distinction predicts who bears the error costs when the system fails.

   *Hint:* The customer pays for and benefits from the system. The subject is acted upon by the system without choosing it. In each of the three scenes, the people most harmed — Buolamwini, the tenants, the misidentified pedestrians — were subjects, not customers. What does this tell you about whose interests were optimized for in each system?

3. The film predates modern LLM (Large Language Model) agents. For each scene, describe its nearest 2026 agentic analogue: a system where an agent takes consequential actions, not just classifications.

   *Hint:* For the white-mask scene: imagine an agent that screens medical images for diagnostic flags and never flags conditions that look different from its training data. For the apartment scene: imagine an agent managing building access and flagging "unusual" entry patterns. For the police scene: imagine an agent that automatically adds individuals to watchlists. What is worse about an *agent* than a classifier in each case?

---

# Part II: Hands on the Distribution

In this part, you will run a bias probe directly on your local model — asking it to complete sentences about different occupations and counting the pronouns it chooses. This turns the abstract concept of "training data bias" into a number you measured yourself.

## Model 2: Probing a Local Model

We probe associations in your local model the disciplined way: many samples, counted, disaggregated. (We probe occupations, a domain where training-text skew is well documented.)

Why this probe matters: if a hiring-assistant agent uses the same model to draft outreach messages, and the model associates "nurse" with feminine pronouns, the agent may subtly vary its messages — using warmer language when addressing presumed women, more formal language when addressing presumed men. No single message is damning; the pattern only appears when you measure across thousands of messages. This is exactly why disaggregated measurement is the right tool.

The code below asks the model to write a sentence about a specific occupation 12 times and counts which pronoun it uses each time. A perfectly unbiased model would use "she," "he," and "they" roughly equally regardless of occupation. What you observe will likely differ — that difference is the bias you are measuring.

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

### Critical Thinking Questions

4. Tabulate your team's counts in a table with columns for occupation, "she" count, "he" count, "they" count, and dominant pronoun. Compare the dominant pronoun for each occupation to real workforce demographics (e.g., from the Bureau of Labor Statistics). Do the model's associations track real workforce demographics, exaggerate them, or sometimes contradict them? Why is *each* of those three outcomes — tracking, exaggerating, or contradicting — a design decision that someone made or failed to make explicitly?

   *Hint:* Tracking the demographics means the model reflects reality. Exaggerating them means the model amplifies existing disparities — because training text over-represents extreme cases. Contradicting them (e.g., "kindergarten teacher → he" despite a female-dominated field) is the rarest outcome but possible where media coverage skews. In each case: who decided what the training corpus would contain, and was that a considered choice?

5. This probe used $n = 12$ samples per occupation. Compute how confident you should be in a 9-versus-3 split favoring "she" over "he." Use a sign test (a statistical test that asks: if there were truly no preference, how likely would this result be by chance?) or reason from coin-flip intuition: if the model had no preference, how often would you get a 9-3 split or more extreme by chance?

   *Hint:* Under the null hypothesis (no preference, 50/50 coin flip), the probability of getting 9 or more "she" out of 12 is the probability of getting at least 9 heads in 12 flips of a fair coin. You can estimate this: getting 9, 10, 11, or 12 heads. Is that likely or unlikely by chance alone? What does this tell you about how many samples you need before claiming a real pattern?

6. Suppose a hiring-assistant *agent* drafts outreach messages and, primed by pronoun associations like the ones you measured, subtly varies warmth or formality by the occupation's inferred gender. No single message would be flagged as discriminatory. What measurement, run over *many* drafts, would expose this pattern?

   *Hint:* Generate 50 outreach messages for "nurses applying for a position" and 50 for "engineers applying for a position." Run your LLM-as-judge rubric (from last week) on all 100, scoring each for warmth, formality, encouragement, and professional tone. Compare the score distributions. What statistical test would you run to determine whether any difference is statistically significant rather than random variation?

[[MC]]
A resume-screening agent shows equal average approval rates overall but was validated only on resumes from one region's universities. The *Coded Bias*-informed concern is:
- ( ) Average approval is the wrong metric; throughput (how many resumes per hour) matters more
- (x) Performance may degrade sharply on groups absent from validation data, and the aggregate hides it
- ( ) The model's temperature was too high, causing random variation that looks like bias
- ( ) Agents cannot exhibit bias because they follow explicit prompt instructions rather than making their own judgments

> **⚠️ Common Misconception:** A common but dangerous belief is that "the agent just follows instructions — it can't be biased." This is wrong on two levels. First, the model underlying the agent was trained on biased text, so its probability distributions already encode the associations in that text. Second, even a perfectly neutral model can be made biased by prompts that introduce biased assumptions (e.g., "draft a professional outreach message for a nurse named Alex" — the model's completion of "professional for a nurse" already carries occupational gender associations). Bias is not a property of whether the agent "means" to discriminate; it is a property of the statistical patterns in its outputs, measured across many runs on many people.

---

Now that you've measured bias directly, this part examines the tools that can reduce it — and why each tool has a ceiling. The goal is an honest engineering stance: not "our system is unbiased," but "here are the mitigations we applied and what they do and don't cover."

# Part III: Mitigation Without Illusion

## Model 3: The Toolbox and Its Limits

Mitigations exist at every stage — and none of them is complete. The honest stance is layered defenses plus ongoing measurement, not a declaration of fairness.

| Mitigation | What it does | Its limit |
|---|---|---|
| **Curate and document training data (datasheets, model cards)** | Records who is in the data, who is absent, and what the known limitations are — making bias auditable rather than hidden. | Documentation can be ignored, falsified, or written after the fact. A datasheet for a dataset does not reduce bias in the data; it only makes the bias visible to those who read it. |
| **Disaggregate evaluation by default** | Reports model performance for each demographic subgroup rather than only the overall average — the practice that would have revealed the facial recognition failures before deployment. | Disaggregation requires knowing which subgroups matter, which requires thinking in advance about who the system will be deployed on. Systems are often evaluated on a convenient test set, not a representative one. |
| **Constrain agents with explicit rubrics** | A rubric that scores qualifications is harder to skew than an agent evaluating "general fit" — because the rubric forces the agent to justify each decision against observable criteria. | Rubrics can encode bias in polite language. "Strong communication skills" can be a proxy for accent or dialect. "Cultural fit" is notoriously unverifiable. The rubric must itself be audited. |
| **Keep humans on consequential decisions** | A human reviewer on high-stakes decisions (hiring, lending, medical triage, parole) can catch systematic errors the model makes — especially if the human is not simply rubber-stamping the model's output. | Human reviewers bring their own biases. Research shows that humans often defer to algorithmic outputs even when they would otherwise disagree — a phenomenon called "automation bias." |
| **Support external accountability and auditing** | Allow independent researchers (like Buolamwini) to test the system, publish findings, and demand repairs — rather than relying only on vendor self-audits. | Operators have economic incentives to restrict access to auditors. Buolamwini's audit succeeded because she obtained the commercial software herself; most researchers cannot do this at scale. |

---

## Exercises

1. *Disaggregation drill.*

   *What to do:* Take your Lab 5 rubric pipeline and a set of 10 short essays. Create 10 slightly varied versions of the same essay by changing only the author byline at the top (use names that statistically connote different gender and national origin — e.g., "by Alex Johnson," "by Priya Sharma," "by Wei Zhang," "by Mohammed Al-Rashid"). Submit all 10 to your judge. Report per-byline score distributions. Any score gap is a directly measured judging bias you must now explain or propose to fix.

   *Starter hint:* Keep the essay body *identical* across all 10 versions — only the byline changes. If scores vary, the variation can only come from the byline. Record the actual scores in a table and compute the range (highest minus lowest) across bylines.

   *You've succeeded when:* You have a table of scores across bylines and can state whether there is a statistically meaningful gap (more than one rubric level difference on any criterion). If there is a gap, you can identify which criterion drove it and propose a rubric revision that would reduce it.

2. *Datasheet sprint.*

   *What to do:* Write a one-page datasheet for the corpus you indexed in Lab 2. Cover: sources (where did the documents come from?), time range (what period do they cover?), languages represented, who is represented as an author or subject, who is absent or underrepresented, and known limitations that would affect a model trained on this data.

   *Starter hint:* Use the Gebru et al. "Datasheets for Datasets" structure: Motivation, Composition, Collection Process, Preprocessing/Cleaning, Uses, Distribution, and Maintenance. You do not need to fill every subsection — focus on the ones where you actually know the answer and where gaps would matter for a deployed system.

   *You've succeeded when:* Your datasheet would allow a researcher who has never seen your corpus to understand who is and is not represented in it, and to make an informed judgment about whether using a model trained on it is appropriate for their intended task.

3. *Audit proposal.*

   *What to do:* Buolamwini audited a commercial facial recognition system from *outside* the company, without the company's cooperation, by purchasing the software herself. Design an external audit for an AI agent system deployed on your campus (a study-abroad advising bot, a student-support chatbot, a course-recommendation system). Specify: what data you would need, what access the operator would have to grant, what metric you would use, and where you would publish the findings.

   *Starter hint:* Think about who is in the system's training or fine-tuning data. Is it representative of your campus's full demographic diversity? Your audit metric could be: "does the system give materially different advice to demographically similar students who differ only on a protected characteristic (race, gender, disability status, first-generation college student status)?"

   *You've succeeded when:* You have a specific audit design that could be carried out by a student researcher with access to the system, and you have identified at least one access requirement the operator would have an economic incentive to refuse — and stated what public pressure or regulatory mechanism could override that incentive.

---

## Reflection Prompt

*Personal:* *Coded Bias* argues that the question is not whether AI systems are biased but who has the power to find out and to demand repair. After this semester, you can build, measure, and audit. Which of those three capabilities do you feel most personally responsible to exercise, and in what specific setting will you most likely get your first opportunity to do so?

*Technical:* You measured pronoun bias in a local language model using 12 samples per occupation. Describe what a rigorous, publishable version of this measurement would require: how many samples, how many occupations, what statistical tests, what control conditions, and what limitations you would need to acknowledge. How far are you from that bar, and what would it take to close the gap?

*Societal:* The mitigations in Model 3 (datasheets, disaggregated evaluation, rubrics, human oversight, external auditing) all have costs — in time, money, and access. Who currently bears those costs in the AI industry, and who should bear them? Is there a case for mandatory external auditing of high-stakes AI systems (like we have for financial auditing or pharmaceutical trials), and what would the governance structure look like?

---

→ Coming Up Next: We bring together everything from Unit 4 — training data, bias measurement, agent design, and evaluation — as you finalize and present your course projects, demonstrating that you can build, measure, and audit AI systems responsibly.

## Further Reading

- *Coded Bias* (2020), dir. Shalini Kantayya, and Buolamwini and Gebru, "Gender Shades." *FAccT* (2018).
- Gebru et al. "Datasheets for Datasets." *CACM* (2021); Mitchell et al. "Model Cards for Model Reporting." *FAccT* (2019).
- Bender, Gebru, McMillan-Major, and Mitchell. "On the Dangers of Stochastic Parrots." *FAccT* (2021).
