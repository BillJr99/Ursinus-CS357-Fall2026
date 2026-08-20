<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-atriskidentification.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-atriskidentification.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Case Study: Early-Alert and At-Risk Identification with Local AI

Colleges everywhere run **early-alert** programs: systems that scan engagement and performance signals to flag students who may be struggling, so an advisor can reach out *before* a withdrawal or a failing grade. Increasingly, institutions want AI to do the scanning. Today we build one — on entirely **synthetic** data, with a local model — precisely so we can take it apart. We move from **the use case and why institutions want it $\rightarrow$ a hands-on triage pipeline on synthetic data $\rightarrow$ failure analysis: false positives, proxies, label bias, feedback loops $\rightarrow$ a decision framework for what must stay human**.

**Purpose (why we are doing this):** This is the single most common "AI for student success" proposal on real campuses, and it sits exactly at the intersection of everything you have learned: local models, structured outputs, evidence verification, bias, and governance. You will be in rooms where this system is proposed. **Task:** run a triage pipeline over synthetic gradebook and survey data, make the model cite its evidence, then probe how its judgments shift when single features are removed. **Criteria for success:** you can name, with examples from your own runs, at least three distinct failure modes of at-risk identification, and you can state which decisions in this workflow must never be automated — and why.

> **⚠️ Synthetic data only.** Every dataset in this activity ([synthetic_gradebook.csv](/files/data/synthetic_gradebook.csv), [synthetic_survey.csv](/files/data/synthetic_survey.csv)) is computer-generated for teaching. The student IDs, scores, and comments correspond to no real people. **No real student data may be used in this activity or in any course exercise derived from it** — not your own, not a classmate's, not "anonymized" real records. This is both a FERPA obligation and a course rule.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Early Alert** | An institutional process that flags possible student struggle early in a term so a human (advisor, instructor) can reach out and offer support. | An advisor receives a triage list and emails three students to offer a meeting |
| **Triage** | Sorting cases by urgency so limited human attention goes where it helps most — the output is a *priority for human attention*, not a verdict. | The model sorts 40 synthetic students into "reach out now / check in / no action" |
| **False Positive / False Negative** | A false positive flags a student who is actually fine (cost: stigma, wasted outreach); a false negative misses a student who needed help (cost: the harm the system exists to prevent). | S002 (strong scores, high logins) flagged because of a low survey score; a quietly struggling student never flagged |
| **Proxy Discrimination** | Harm that occurs when an innocent-looking feature stands in for a protected or sensitive attribute, so decisions correlate with group membership even though the attribute was "never used." | `hours_working_job` acting as a proxy for family income |
| **Label Bias** | Bias baked into the *outcome definition or historical labels* a system learns from or is judged against — if past flags were biased, a model matching them reproduces the bias. | Training on "students flagged by staff last year" instead of actual outcomes |
| **Feedback Loop** | A cycle where the system's outputs change the data it later consumes, amplifying its own patterns. | Flagged students get outreach and improve, so the features that triggered flags look *predictive of recovery* — or surveillance drives disengagement |
| **Base Rate** | How common the condition actually is in the population. When the condition is rare, even accurate flaggers produce mostly false positives. | If 5 of 40 students are truly struggling, a 90%-accurate flagger still flags several fine students |
| **Human-in-the-Loop (HITL)** | A design where AI output is advisory and a responsible person makes the decision — required here because the "action" touches a person's education and dignity. | The triage list goes to an advisor who reads the evidence and decides whether/how to reach out |

Each concept appears in at least two representations today: this table (words), the pipeline and failure diagrams (pictures), your code output (numbers), and the decision framework (rules). Cross-check them.

---

# Part I: The Use Case

In this Part you will see what an early-alert system is, why institutions invest in it, and what its inputs and outputs actually look like — before touching any code — so that the ethics questions land on a concrete design rather than a vague fear.

## 1. Why Institutions Want This

**Why this matters:** Early alert is not a villain's scheme; it addresses a real failure of the status quo. In a 30-person seminar an instructor notices a struggling student. In a 300-person lecture, or across a 2,000-student advising caseload, nobody notices until the midterm grade posts — often past the point where support helps most. Institutions also face genuine retention pressure: each student who withdraws is a person whose goal collapsed and, bluntly, lost tuition revenue. The pitch for AI is capacity: machines can read 2,000 records weekly; humans cannot. The peril, as you know from the bias unit, is that the machine reads them with the patterns of its data and design — at scale, uniformly, with an aura of objectivity.

## Model 1: The Early-Alert Pipeline

```
 SIGNALS (weekly)                       TRIAGE                    ACTION
 
 LMS engagement                   +------------------+
   scores, missing work,   -----> |                  |      advisor reviews list,
   logins, discussion posts       |  scoring /       |      reads cited evidence,
                                  |  summarization   | ---> decides whether and
 survey self-reports              |  (today: local   |      how to reach out
   belonging, workload,    -----> |  LLM on          |
   hours at a job,                |  aggregated      |      instructor adjusts
   free-text comments             |  features)       |      course support
                                  +------------------+
                                          |
                                          v
                                 triage list with tiers:
                                 REACH_OUT_NOW / CHECK_IN / NO_ACTION
                                 each with cited evidence
```

Two signal families feed the triage stage. **Engagement signals** come from the LMS automatically (the [synthetic_gradebook.csv](/files/data/synthetic_gradebook.csv) columns: six assignment scores with realistic missingness, `logins_last_14d`, `discussion_posts`). **Self-report signals** come from a voluntary survey (the [synthetic_survey.csv](/files/data/synthetic_survey.csv) columns: `belonging_1to5`, `workload_1to5`, `hours_working_job`, and a `free_text_comment`). The output is not a grade and not a diagnosis: it is a *priority for human attention* with evidence attached.

### Critical Thinking Questions

1. The two signal families differ in consent and coverage: LMS signals are collected from everyone, automatically, whether or not they know it; survey signals are volunteered by whoever chose to answer. Name one way each family can *mislead* the triage stage precisely because of how it was collected.

   > *Hint: LMS signals measure platform behavior, not learning — a student who studies from a printed textbook and a friend's notes logs in rarely. Survey signals suffer selection effects — the students most overwhelmed may be exactly the ones who skip an optional survey, so their row is silently missing.*

2. The pipeline's output tiers are `REACH_OUT_NOW / CHECK_IN / NO_ACTION` — recommendations for *support outreach*. Suppose a well-meaning administrator proposes reusing the same list to decide priority registration holds or scholarship-renewal reviews. The pipeline is unchanged; what changed, and why does it change the ethics entirely? (The Recorder writes the group's one-sentence answer.)

   > *Hint: The action changed from offering help (a benefit, low cost when wrong) to imposing consequence (a penalty, high cost when wrong). A false positive in outreach costs an unneeded friendly email; a false positive in a registration hold costs a student their schedule. Same model, same accuracy — different stakes and different legitimacy.*

3. Why does the diagram's triage box say "aggregated features" rather than sending raw rows — including free-text comments verbatim — straight into the model? Connect this to data minimization from the institutional-systems activity.

   > *Hint: Aggregation limits what the model can leak, misquote, or fixate on, and pre-computing trends in Python keeps arithmetic out of the model's hands. But note the tension you'll test later: the free-text comment is also the most humanly informative signal ("working more shifts lately"). Minimization and context-richness pull in opposite directions; today's pipeline passes the comment through deliberately, as a design decision to examine.*

The defensible purpose of an early-alert triage list is to:

[( )] Predict each student's final grade as accurately as possible
[( )] Replace advisor judgment with a consistent automated score
[(X)] Direct limited human outreach capacity toward students who may benefit from it, with evidence a human can check
[( )] Build a permanent record of each student's engagement history

---

# Part II: Hands-On with Synthetic Data

In this Part you will run the triage stage yourself: aggregate the synthetic gradebook and survey into per-student features, then prompt a local model for a tiered triage summary that must cite its evidence. Save your outputs — Part III and the Exercises will interrogate them.

## 2. The Triage Pipeline

**Why this matters:** Everything in Part III's critique lands harder when it is *your* pipeline producing the questionable flag. The prompt pattern here — structured tiers, mandatory evidence citation, explicit "insufficient data" tier, temperature 0 — is the same discipline as the rubric pipeline, applied to people, which is why the discipline is not optional.

The code inlines a few rows of the synthetic datasets so the cell runs anywhere; the full 40-student files are at [/files/data/synthetic_gradebook.csv](/files/data/synthetic_gradebook.csv) and [/files/data/synthetic_survey.csv](/files/data/synthetic_survey.csv) (download both and swap in the `open(...)` lines to run the real exercise).

## Code Cell

```python
import csv, io, json, requests

# ALL DATA IS SYNTHETIC -- generated for teaching; no real students exist here.
# Full files: /files/data/synthetic_gradebook.csv and /files/data/synthetic_survey.csv
GRADEBOOK = """student_id,assignment1,assignment2,assignment3,assignment4,assignment5,assignment6,logins_last_14d,discussion_posts
S001,99,93,74,,55,47,3,2
S002,86,91,93,98,91,95,13,7
S003,41,60,69,82,85,81,7,5
S004,78,80,74,69,65,,6,0
"""
SURVEY = """student_id,belonging_1to5,workload_1to5,hours_working_job,free_text_comment
S001,3,4,20,Working more shifts lately so less time to study.
S002,5,3,8,No concerns right now.
S003,3,3,0,I added the class late and am still catching up.
S004,2,4,20,Hard to focus this month due to family stuff.
"""

def load(text):  # swap for: open("synthetic_gradebook.csv") etc. for the full data
    return {r["student_id"]: r for r in csv.DictReader(io.StringIO(text))}

grades, survey = load(GRADEBOOK), load(SURVEY)

def features(sid, drop=None):
    g, s = grades[sid], survey.get(sid, {})
    scores = [int(g[f"assignment{i}"]) for i in range(1, 7) if g[f"assignment{i}"]]
    early, late = scores[:len(scores)//2] or [0], scores[len(scores)//2:] or [0]
    feat = {
        "student": sid,
        "mean_score": round(sum(scores)/max(1, len(scores)), 1),
        "score_trend_late_minus_early": round(sum(late)/len(late) - sum(early)/len(early), 1),
        "missing_assignments": 6 - len(scores),
        "logins_last_14d": int(g["logins_last_14d"]),
        "discussion_posts": int(g["discussion_posts"]),
        "survey_belonging_1to5": s.get("belonging_1to5", "no survey response"),
        "survey_workload_1to5": s.get("workload_1to5", "no survey response"),
        "hours_working_job": s.get("hours_working_job", "no survey response"),
        "survey_comment": s.get("free_text_comment", "no survey response"),
    }
    if drop:                      # the bias-probe knob used in the Exercises
        feat.pop(drop, None)
    return feat

PROMPT = """You are a triage assistant helping an academic advisor prioritize
supportive outreach. You do not diagnose, predict grades, or judge students.
For the feature record below, respond with JSON only:
{"student": id,
 "tier": "REACH_OUT_NOW" | "CHECK_IN" | "NO_ACTION" | "INSUFFICIENT_DATA",
 "summary": one neutral sentence describing the pattern,
 "evidence": [each feature name and value that supports the tier]}
Rules: cite only features present in the record; if signals conflict or data
is missing, prefer CHECK_IN or INSUFFICIENT_DATA over guessing; never invent
causes for a pattern the data does not state.

Record: """

def triage(feat):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False, "format": "json",
            "options": {"temperature": 0.0, "seed": 42},
            "messages": [{"role": "user", "content": PROMPT + json.dumps(feat)}]},
            timeout=120).json()["message"]["content"]
        return json.loads(r)
    except Exception as e:
        print(f"[atrisk:triage] {e}")
        import traceback; traceback.print_exc()
        return {"student": feat["student"], "tier": "REVIEW_NEEDED", "evidence": []}

for sid in grades:
    result = triage(features(sid))
    print(json.dumps(result))
```

## Model 2: Reading a Triage Output

A run of this pipeline produced (your output will be similar in structure):

```
{"student": "S001", "tier": "REACH_OUT_NOW",
 "summary": "Scores declined from the 90s to the 40s with one missing assignment, few recent logins, and a comment reporting increased work shifts.",
 "evidence": ["score_trend_late_minus_early: -37.3", "missing_assignments: 1",
              "logins_last_14d: 3", "survey_comment: Working more shifts lately so less time to study."]}
{"student": "S002", "tier": "NO_ACTION",
 "summary": "Consistently high scores with frequent logins and active discussion participation.",
 "evidence": ["mean_score: 92.3", "logins_last_14d: 13", "discussion_posts: 7"]}
{"student": "S003", "tier": "CHECK_IN",
 "summary": "Scores are rising from a weak start and the comment reports a late add still catching up.",
 "evidence": ["score_trend_late_minus_early: +26.0", "survey_comment: I added the class late and am still catching up."]}
```

### Critical Thinking Questions

4. For S003 the *mean* score is mediocre, but the model assigned `CHECK_IN`, not `REACH_OUT_NOW`, citing the positive trend and the late-add comment. What would a simple threshold rule ("flag mean < 75") have done, and what does this reveal about why summarization-with-context is proposed for triage at all — and what new risk arrives with that flexibility?

   > *Hint: The threshold flags S003 (false positive: an improving late-adder needs no urgent intervention) and the flexibility fixed it. But flexibility means the model *interprets* — and interpretation can import assumptions (about jobs, about who "sounds" struggling) that a dumb threshold cannot. You trade auditable rigidity for unauditable judgment.*

5. Check each evidence item in the Model 2 output against the input rows at the top of the code cell. Is every citation real and correctly valued? Why is this verification — which you did in seconds — the *load-bearing* step that makes HITL genuine rather than theatrical when an advisor uses this list?

   > *Hint: An advisor who can check "logins_last_14d: 3" against the record in one glance can meaningfully disagree with the tier. If the summary said "student appears disengaged" with no citations, the advisor can only accept or reject a vibe. Evidence citation is what converts AI output from a verdict into an argument.*

6. The prompt forbids inventing causes, yet the S001 summary links the score decline with the work-shifts comment in one sentence. Is that a stated fact from the data or an implied causal story? Draft a one-clause prompt amendment that would keep the *facts* but flag the *inference*.

   > *Hint: The record contains both facts, but placing them in one sentence implies "scores fell because of work." Maybe true — the advisor should explore it, not inherit it. Consider adding: "list co-occurring signals separately; if you suggest a possible connection, label it explicitly as 'possible connection, unverified'."*

The prompt includes an `INSUFFICIENT_DATA` tier. Its most important function is to:

[( )] Reduce the number of API calls to the local model
[(X)] Give the model a legitimate output for students with missing signals, instead of forcing a confident tier from thin evidence
[( )] Ensure every student receives some form of outreach
[( )] Penalize students who skipped the survey

> **⚠️ Common Misconception:** Because the output is JSON with cited evidence at temperature 0, it *looks* like the deterministic output of an audited algorithm. It is not: it is a language model's judgment call, shaped by patterns in its training text — including cultural patterns about what struggle "sounds like." Two records with identical numbers and differently-phrased comments can receive different tiers. The structure makes the output *checkable*; it does not make it *objective*.

---

# Part III: Failure Analysis

In this Part you will name the specific ways this system fails — false positives and negatives, proxy discrimination, label bias, and feedback loops — and assemble a decision framework separating what may be assisted by AI from what must never be automated. This continues the [Training Data and Bias activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-biasdata.md) with a case where the stakes are your own campus.

## 3. Four Ways It Breaks

**Why this matters:** Every failure below has occurred in real deployed early-alert and risk-scoring systems — in education, child welfare, healthcare, and criminal justice. None of them is fixed by a bigger model. They are properties of the *problem setup*: what is measured, what counts as ground truth, and what the outputs do to the world.

**Failure 1: False positives and false negatives have asymmetric, non-obvious costs.** A false positive ("flagged but fine") seems cheap — an unneeded kind email. At scale it is not: outreach capacity is finite (100 flags for 10 advisor-hours means real cases buried in noise), and being labeled at-risk is not neutral (records persist; students who learn they were flagged report feeling surveilled and doubted). A false negative is the system failing at its one job — and it is *invisible*: nobody audits the students who were never flagged. With low base rates, even good flaggers are mostly wrong when they flag (revisit the base-rate row of the Key Concepts).

**Failure 2: Proxy discrimination.** Our features never mention income, disability, family status, or race. But `hours_working_job` tracks family wealth; `logins_last_14d` tracks broadband access, commuting, and caregiving; `discussion_posts` tracks language confidence and cultural norms about speaking up; even survey completion tracks trust in the institution. A system can be scrupulously blind to protected attributes and still sort students by them — this is the *proxy* mechanism from the bias unit, now with named columns you can point to.

**Failure 3: Label bias.** Suppose we "improve" the pipeline by training or calibrating it on historical data. Which history? If the label is "students staff flagged in the past," we learn past staff attention patterns — including whom staff *noticed* and whom they overlooked. If the label is "students who eventually failed or withdrew," we inherit every past inequity that produced those outcomes, including the institution's own past failures to support. The label defines the target; a biased target makes accuracy itself a form of bias reproduction.

**Failure 4: Feedback loops.** The system acts on the world it measures. Flagged students receive support and improve — so the data now "shows" that flag-pattern students recover, muddying every future evaluation. Students who learn that logins are monitored change their login behavior (or their honesty on surveys), degrading the signals. Unflagged struggling students never appear in anyone's records as a miss. The system curates its own future training data — the same loop mechanism from the bias unit, operating on people who know they are being watched.

## Model 3: A Decision Framework

| Decision | May AI assist? | Must a human decide? | Should it ever be automated? |
|----------|----------------|----------------------|------------------------------|
| Aggregate signals into a summary with cited evidence | yes — this is today's pipeline | human reads and verifies | summarization may be automated; its *use* may not |
| Prioritize which records an advisor reads first | yes, as a sort order | advisor can re-order and must see all tiers, including unflagged | ordering yes; hiding records, never |
| Decide to reach out, and how (email, meeting, referral) | drafting support only | **yes — always** | never: the contact is a human relationship |
| Impose a consequence (hold, required program, aid review) | no | **yes — with due process, and the student can see and contest the evidence** | **never** |
| Define what counts as "at risk" at all | no — this is a values choice | institution, with student voice, in public | **never: this is policy, not inference** |

The framework's logic: automation may flow *toward* evidence-gathering and *away from* consequence and definition. The closer a step sits to a person's opportunities, dignity, or record, the more the human role must be real (able to see evidence, able to disagree, accountable for the choice) — and the two bottom rows are not automatable at any accuracy level, because they are not accuracy problems.

### Critical Thinking Questions

7. Run the false-positive/false-negative cost analysis concretely: for the outreach use (email offering support) and the consequence use (registration hold), fill a 2x2 table — cost of FP and FN under each use. Using your table, explain why the *same* triage model can be acceptable for the first use and unacceptable for the second, even at identical accuracy. (The Recorder writes the table.)

   > *Hint: Outreach: FP = mild (unneeded email, some surveillance cost), FN = the harm the system exists to prevent — so tuning toward sensitivity is defensible. Hold: FP = concrete injury to a fine student with contest costs, FN = status quo. The action, not the model, sets the acceptable error trade-off — this is why Model 3's framework keys on the decision, not the algorithm.*

8. For each of the four synthetic feature columns `hours_working_job`, `logins_last_14d`, `discussion_posts`, and `survey_belonging_1to5`, name the plausible off-dataset attribute it proxies for, and mark which of these proxies you could *detect* using the disaggregated-evaluation technique from the bias unit — and which you could not, because the protected attribute is not in any table you have.

   > *Hint: Detection requires the sensitive attribute to disaggregate by. If you have no income data, you cannot compute flag rates by income — the proxy operates invisibly. This is the practical bite of proxy discrimination: the blindness that prevents *using* the attribute also prevents *auditing* for it. What governance response does that suggest (collect-with-consent for audit? external review?)?*

9. A vendor proposes improving on today's zero-shot pipeline by fine-tuning on five years of the institution's advising records: features plus whether staff flagged the student, labeled "ground truth." Using Failure 3 and Failure 4, write the two-sentence objection your team would raise in the procurement meeting, and propose one label definition that is less biased (not unbiased — less).

   > *Hint: Objection: staff flags encode staff attention patterns, not student need (label bias), and five years of the system's own outreach effects contaminate outcomes (feedback loop). A less-bad label anchors on outcomes the institution did not itself mediate and defines them before looking at the data — but even "withdrew or failed" inherits historical inequity. There is no clean label; there are only labels whose bias you have named.*

10. In Model 3, the last row says defining "at risk" is policy, not inference. Who is affected by that definition but absent from the table? Name two concrete mechanisms (not sentiments) for including them, and one reason each mechanism can fail.

    > *Hint: Students — especially those most likely to be flagged. Mechanisms: student membership on the governance committee that approves the definition (fails if tokenized or under-informed); a published definition with a feedback/contest channel (fails if buried or if contesting carries social cost); opt-in/opt-out for survey signals (fails if opting out itself becomes a signal). The explainability lab's contestability requirement is the same principle downstream.*

An early-alert system's false negatives are especially dangerous to the institution's understanding of its own system because:

[( )] They cost more advisor time than false positives
[( )] They cause the model to retrain itself automatically
[(X)] They are invisible in normal operation — no one reviews the students who were never flagged, so the system's misses generate no complaints and no data
[( )] They only affect students with complete data

---

# Part IV: Synthesis and Practice

## Exercises

1. *The bias probe: remove one feature, watch the triage move.*

   - *What to do:* Download both full synthetic files ([synthetic_gradebook.csv](/files/data/synthetic_gradebook.csv), [synthetic_survey.csv](/files/data/synthetic_survey.csv)) and run the pipeline over all 40 students twice: once with full features, once passing `drop="hours_working_job"` to the `features()` function. Hold temperature at 0 and the seed fixed so the *only* variable is the feature. Build a table: student, tier-with, tier-without; report how many tiers changed, in which direction, and quote one summary sentence that changed.
   - *Starter hint:* `results_full = {sid: triage(features(sid)) for sid in grades}` then `results_drop = {sid: triage(features(sid, drop="hours_working_job")) for sid in grades}`; compare `["tier"]` fields. Then repeat for `drop="survey_comment"` — the free-text field — and compare the *size* of the two effects.
   - *You've succeeded when:* You report changed-tier counts for at least two dropped features, identify which feature the model leans on most, and write three sentences on what this implies: if removing a proxy feature changes who gets flagged, the feature was carrying decision weight — was that weight justified?

2. *The advisor's audit.*

   - *What to do:* Play the human in the loop for ten of your 40 triage outputs (include at least two `REACH_OUT_NOW` and two `NO_ACTION`). For each: verify every evidence citation against the source rows, then record agree/disagree with the tier and one sentence why. Report your disagreement rate and any citation errors found.
   - *Starter hint:* Automate the citation check (adapt the rubric-lab evidence verifier: does each cited feature name and value appear in the input record?) but do the agree/disagree judgment yourself — that judgment is the thing being practiced.
   - *You've succeeded when:* You have a 10-row audit table, a disagreement rate, and a one-paragraph answer to: at what disagreement rate would you tell the institution this tool is not ready for advisors?

3. *Failure-mode hunting on your own output.*

   - *What to do:* Search your 40 triage results for one likely false positive and one likely false negative (you know the data-generating archetypes: improving late-adders, quiet-but-fine students, missing-survey students). For each, identify which feature pattern misled the model and which of Part III's four failures it instantiates.
   - *Starter hint:* Students with `no survey response` in every survey field are the natural false-something candidates: does the model read absence-of-survey as risk (surveillance penalty for non-participation) or as fine (missing the overwhelmed non-responder)? Either error is instructive.
   - *You've succeeded when:* You have two concrete cases with feature-level explanations, each tagged with its Part III failure number, and one prompt or pipeline change that would have helped that case (and a note on what the change might break).

4. *The one-page deployment memo.*

   - *What to do:* Synthesize the activity into a one-page recommendation to your institution: should it deploy this pipeline for advisor triage? Use Model 3's framework rows as section headings, cite your exercise 1 and 2 measurements as evidence, state the FERPA posture (local model, synthetic-tested, minimized features), and end with the two decisions your memo forbids automating, with one sentence of justification each.
   - *Starter hint:* A credible memo includes the conditions under which you would *reverse* your recommendation — what measurement, at what threshold, would change your mind?
   - *You've succeeded when:* Every claim in the memo traces to something you measured or to a named framework row, and a skeptical reader can tell exactly what is being recommended, forbidden, and monitored.

---

## Reflection Prompt

*Personal:* This system would have read your own first semester. Would it have flagged you? Would being flagged — or being invisible to it — have helped you, stung, or both? What would you have wanted the human who received the flag to do?

*Technical:* Your bias probe measured how triage shifts when one feature disappears — an ablation, the same experimental logic as SHAP's feature attributions in the [explainability lab](/Assignments/Explainability). What can your ablation detect that a SHAP analysis of a numeric model cannot, and vice versa? Where does *neither* tool reach (recall question 8)?

*Societal (Open Questions):* The Ursinus Open Questions ask "How should we live together?" and "What should matter to me?" An early-alert system is one institutional answer: we should notice one another's struggle early, and we should delegate part of the noticing to machines so that no one is overlooked. Write a short paragraph defending that answer, and a second paragraph giving the strongest reply — that being *noticed by a machine* is not the same as being *cared for by a community*, and may crowd it out. Which paragraph do you believe, and what would an early-alert design that took *both* seriously look like?

---

## → Coming Up Next

We built the most defensible version of this system — local, minimized, evidence-cited, human-gated — and still found four structural failure modes. The remaining course units give you the vocabulary institutions use to manage exactly this tension: governance frameworks, regulation, and the question of what we owe the people inside our systems.

---

## 4. Further Reading

- Course cross-links: the [Training Data and Bias activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-biasdata.md) (proxies, disaggregated evaluation, feedback loops) and the [Explainability lab](/Assignments/Explainability) (feature attribution, contestable explanations).
- Virginia Eubanks. *Automating Inequality: How High-Tech Tools Profile, Police, and Punish the Poor.* St. Martin's Press (2018).
- Cathy O'Neil. *Weapons of Math Destruction*, chapter on predictive models in education (2016).
- Obermeyer et al. "Dissecting racial bias in an algorithm used to manage the health of populations." *Science* (2019). The canonical label-bias case study.
- U.S. Department of Education, Office of Educational Technology. "Artificial Intelligence and the Future of Teaching and Learning" (2023), section on human-in-the-loop.
- New America. "Predictive Analytics in Higher Education: Five Guiding Practices for Ethical Use" (2016).
