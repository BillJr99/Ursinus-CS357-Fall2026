<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-institutionalai.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-institutionalai.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Integrating AI with Institutional Systems: LMS, Assessment Software, and Student Information Systems

Your rubric pipeline grades a folder of files on your laptop. Real institutions do not keep student work in folders on laptops: it lives in a **Learning Management System** (LMS), grades flow to a **Student Information System** (SIS), and assessment software sits in between. Today we study what it takes (technically and ethically) to connect an AI pipeline to those systems. We move from **the integration landscape $\rightarrow$ a worked LMS-export-to-rubric-pipeline integration $\rightarrow$ governance: FERPA, data minimization, and when NOT to integrate**.

**Purpose (why we are doing this):** Almost every AI system you will build professionally connects to an institutional system of record: a gradebook, a medical record, a payroll database. Education is our worked example because you live inside one: your own grades flow through exactly the pipes we diagram today. **Task:** map the data flows among LMS, assessment software, and SIS; run a synthetic gradebook export through the local-LLM rubric pipeline you already built; and analyze the whole design against FERPA and the NIST AI RMF. **Criteria for success:** you can draw a complete data-flow diagram for an integration, label every arrow with what data crosses it, and defend (or reject) each arrow under FERPA's rules.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **LMS (Learning Management System)** | The web platform where courses live: assignments, submissions, discussion boards, and the gradebook. Exposes a REST API for reading and writing course data. | Canvas, Moodle, Blackboard; a `GET /api/v1/courses/:id/students/submissions` call |
| **SIS (Student Information System)** | The institution's system of record for enrollment, transcripts, financial aid, and demographics. Grades ultimately land here; it is the most sensitive system on campus. | Banner, PeopleSoft, Workday Student; the registrar's official grade roster |
| **Assessment Software** | Tools that collect and score student work (quizzing engines, proctoring tools, portfolio systems) usually exporting results as CSV or via LTI to the LMS. | A quiz platform exporting `student_id, item_1, item_2, ...` as CSV |
| **REST API** | A web interface where programs read and write data over HTTPS using URLs and JSON, the same pattern as your Ollama calls, but pointed at institutional data. | `GET /api/v1/courses/357/assignments` with an authorization token |
| **FERPA** | The Family Educational Rights and Privacy Act, the US federal law protecting student education records: it restricts who may see records and gives students the right to inspect them. | Deciding whether a gradebook CSV may be sent to a cloud AI service (usually: not without a contract) |
| **Data Minimization** | The principle of sending a system only the fields it needs for its task, nothing more. Every extra field is extra risk with zero benefit. | Dropping name, ID, and demographics before the LLM sees a submission |
| **Human-in-the-Loop (HITL)** | A design in which a person reviews and approves an AI output before it takes effect; the write path runs through a human. | A draft grade sits in a review queue; only the instructor's click posts it |
| **LTI (Learning Tools Interoperability)** | The standard protocol that lets external tools plug into an LMS and exchange rosters and scores without custom code. | A quiz tool appearing as a Canvas assignment and passing scores back automatically |

Each concept appears at least twice today: as a definition (above), as a box or arrow in a diagram (Models 1 and 2), and (for the pipeline) as runnable code. Cross-check the representations against each other.

---

# Part I: The Integration Landscape

In this Part you will map the systems that hold student data and the channels between them, so that "integrate AI with the LMS" becomes a set of specific, inspectable arrows instead of a vague ambition.

## 1. Three Systems, Many Pipes

**Why this matters:** Every arrow in an integration diagram is a place data can leak, be corrupted, or be used beyond its purpose. Institutions think in these diagrams; so do auditors and privacy officers. If you cannot draw the arrow, you cannot govern it.

## Model 1: The Campus Data-Flow Map

```
                    +---------------------------+
                    |            SIS            |
                    |  (system of record:       |
                    |  enrollment, transcripts, |
                    |  demographics, final      |
                    |  grades)                  |
                    +------------+--------------+
                      ^                     |
        (5) final     |                     |  (1) roster sync
        grade posting |                     |      (nightly batch)
                      |                     v
                    +-+-------------------------+
   (2) LTI launch   |            LMS            |   (3) REST API
  +---------------->|  (courses, submissions,   |<------------------+
  |                 |  gradebook, discussions)  |                   |
  |                 +------------+--------------+                   |
  |                              |                                  |
+-+------------------+           |  (4) CSV / JSON export         +-+----------------+
| Assessment         |           v                                | Your AI pipeline |
| software           |   files on disk:                          | (local model +   |
| (quizzes,          |   submissions.zip                          | rubric + CSV     |
| portfolios,        |   gradebook_export.csv                     | report)          |
| proctoring)        |                                            +------------------+
+--------------------+
```

Five numbered channels, each with different properties:

| Channel | Direction | Mechanism | Typical data | Risk profile |
|---------|-----------|-----------|--------------|--------------|
| (1) Roster sync | SIS $\rightarrow$ LMS | nightly batch job | names, IDs, enrollments | broad but internal |
| (2) LTI launch | Assessment tool $\leftrightarrow$ LMS | LTI protocol | roster subset, scores back | governed by standard |
| (3) REST API | Program $\leftrightarrow$ LMS | HTTPS + token | anything the token allows | as broad as the token |
| (4) Export | LMS $\rightarrow$ file | CSV/ZIP download | a frozen snapshot | leaves the system's control |
| (5) Grade posting | LMS $\rightarrow$ SIS | end-of-term batch | final grades | highest stakes, write path |

### Critical Thinking Questions

1. Channel (3), the REST API token, "is as broad as the token." A read-write token scoped to all courses is issued to a grading script that only needs read access to one course's submissions. Using the diagram, name two distinct harms this over-broad token makes possible that a correctly-scoped token would not.

   > *Hint: Think about both directions. Read side: what can be read beyond the one course (other courses' gradebooks, discussion posts)? Write side: what can a buggy or compromised script change (posting grades, deleting submissions)? Least privilege is the API version of data minimization.*

2. Channel (4) is the only channel where data "leaves the system's control." What protections does the LMS enforce on data *inside* it (access logs, permissions, retention) that vanish the moment a CSV lands in someone's Downloads folder? Why might a privacy office nevertheless *prefer* channel (4) over channel (3) for a one-time AI experiment?

   > *Hint: Inside the LMS every view is authenticated and logged. A CSV on disk has no access control but also has a hard property the API lacks: it is a fixed, inspectable, minimizable snapshot. You can open it, delete columns, and know exactly what the AI will see — with a live API token, the blast radius is whatever the token allows, forever until revoked.*

3. Your AI pipeline box currently has an arrow *in* (channel 4) but no arrow *out*. Someone proposes adding an arrow: pipeline $\rightarrow$ REST API $\rightarrow$ gradebook ("auto-post the AI's scores"). Which single property of the whole diagram changes, and what does the rubric-pipeline lab's evidence-verification result suggest about whether this arrow is ready to exist? (The Recorder writes the group's position.)

   > *Hint: With no outbound arrow, the AI is advisory: a human reads its CSV and decides. The new arrow makes the AI an actor in the system of record. Recall your measured hallucinated-evidence rate from the rubric pipeline lab — would you accept that error rate writing directly to the gradebook that feeds channel (5)?*

Which channel in the Model 1 diagram represents the *highest-stakes write path* — the one where an AI error would be hardest to contain?

[( )] Channel (1), the roster sync from SIS to LMS
[( )] Channel (4), the CSV export to disk
[( )] Channel (2), the LTI score passback
[(X)] Channel (5), final grade posting from LMS into the SIS system of record

> **Common Misconception:** Students often assume "integrating AI with the LMS" means the AI model runs inside the LMS. It almost never does. The integration is plumbing: rosters, submissions, and scores flow between systems over the channels above, and the model runs wherever you put it — on your laptop, on a campus server, or (riskiest) at a cloud vendor. Where the model runs determines who can see the data, which is why our course's local-first stack is itself a privacy decision.

---

# Part II: A Worked Integration

In this Part you will run a synthetic LMS gradebook export through the same local-LLM rubric machinery you built in the rubric pipeline lab — experiencing channel (4) of Model 1 end to end, entirely on your own machine, with entirely synthetic data.

## 2. From Export to Report

**Why this matters:** This is the smallest real integration that exists in the wild: export from the system of record, process with a local model, and produce a human-reviewable report. It builds directly on your [Lab: An LLM Rubric-Grading Pipeline](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RubricPipeline) — same model, same discipline (temperature 0, structured output, evidence required), new data source. Everything here uses the synthetic dataset `synthetic_gradebook.csv`; **no real student data is ever used in this course, and none may be**.

The code below plays both roles: first it stands in for the LMS by writing a small synthetic gradebook export (the same format as the course dataset [/files/data/synthetic_gradebook.csv](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/data/synthetic_gradebook.csv), which you can substitute), then it aggregates each row into a *minimized* feature summary — no names, no demographics — and asks the local model for a one-line, evidence-cited progress note per student, exactly as the rubric pipeline demanded evidence per criterion.

## Code Cell

```python
import csv, io, json, requests

# --- Stage 1: the "LMS export" (channel 4) ---------------------------------
# In practice: download gradebook_export.csv from the LMS, or fetch it from
# /files/data/synthetic_gradebook.csv. Here we inline a few rows of the same
# synthetic format so the cell is self-contained. ALL DATA IS SYNTHETIC.
EXPORT = """student_id,assignment1,assignment2,assignment3,assignment4,assignment5,assignment6,logins_last_14d,discussion_posts
S001,99,93,74,,55,47,3,2
S002,86,91,93,98,91,95,13,7
S004,78,80,74,69,65,,6,0
"""

# --- Stage 2: data minimization -- aggregate before the model sees anything -
def summarize(row):
    scores = [int(row[f"assignment{i}"]) for i in range(1, 7) if row[f"assignment{i}"]]
    missing = 6 - len(scores)
    early = scores[:3]; late = scores[3:]
    return {
        "student": row["student_id"],           # pseudonymous ID only
        "mean_score": round(sum(scores) / max(1, len(scores)), 1),
        "trend": round((sum(late)/len(late) - sum(early)/len(early)), 1) if late and early else 0.0,
        "missing_assignments": missing,
        "logins_last_14d": int(row["logins_last_14d"]),
        "discussion_posts": int(row["discussion_posts"]),
    }

features = [summarize(r) for r in csv.DictReader(io.StringIO(EXPORT))]

# --- Stage 3: the local model writes an evidence-cited note -----------------
PROMPT = """You are a course-progress summarizer. For the student feature record
below, write JSON: {"student": id, "note": one sentence, "evidence": [list of
the specific feature names and values that support the note]}. Cite only
features present in the record. Do not invent facts or guess causes.

Record: """

def note_for(feat):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False, "format": "json",
            "options": {"temperature": 0.0, "seed": 42},
            "messages": [{"role": "user", "content": PROMPT + json.dumps(feat)}]},
            timeout=120).json()["message"]["content"]
        return json.loads(r)
    except Exception as e:
        print(f"[institutionalai:note_for] {e}")
        import traceback; traceback.print_exc()
        return {"student": feat["student"], "note": "REVIEW_NEEDED", "evidence": []}

for feat in features:
    result = note_for(feat)
    # Stage 4: verify cited evidence against the source record (rubric-lab habit)
    verified = all(str(k) in json.dumps(feat) for k in result.get("evidence", []) if isinstance(k, str))
    print(json.dumps(result), " evidence_verified:", verified)
```

## Model 2: What Crossed Each Boundary

| Stage | Boundary crossed | What the data looked like | What was removed |
|-------|------------------|---------------------------|------------------|
| 1. Export | LMS $\rightarrow$ disk | full gradebook rows | (nothing yet) |
| 2. Aggregate | disk $\rightarrow$ pipeline memory | 6 derived features per student | raw per-assignment scores, any names/demographics an export might carry |
| 3. Model call | pipeline $\rightarrow$ local model | one JSON feature record | everything about every *other* student |
| 4. Report | pipeline $\rightarrow$ human reader | note + cited evidence + verification flag | model's freedom to assert unverified claims |

### Critical Thinking Questions

4. Stage 2 computes `mean_score` and `trend` and discards the raw scores before the model call. Give one concrete benefit of this minimization *for accuracy* (think: what can a model hallucinate about six raw numbers vs. two derived ones?) and one *for privacy* (think: what re-identification risk does a full score vector carry that a mean does not?).

   > *Hint: For accuracy — fewer numbers means fewer opportunities to misread, transpose, or invent arithmetic; the aggregation is done by Python, which does arithmetic correctly, rather than by the model, which may not. For privacy — a full vector of six scores is close to a fingerprint that could be matched back to a public leaderboard or a peer's knowledge; a rounded mean is far less identifying.*

5. This pipeline sends data to `localhost:11434`. Rewrite Model 1's diagram arrow for stage 3 as it would look if the model were a commercial cloud API instead. What new party appears in the data flow, and what FERPA-relevant question must now be answered before the first request is sent? (Preview of Part III.)

   > *Hint: A new box appears outside the campus boundary: the vendor's servers, retention policies, and staff. The question is whether the vendor qualifies as a "school official" with a "legitimate educational interest" under a contract that limits use and redistribution — the standard FERPA mechanism for outsourcing. Without it, transmitting identifiable records is a disclosure.*

6. Stage 4 re-checks the model's citations against the source record — the same hallucinated-evidence audit you built in the [rubric pipeline lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/RubricPipeline). Why does this verification become *more* important, not less, as the integration gets closer to institutional systems?

   > *Hint: On your laptop, a hallucinated quote wastes your time. In a report that an advisor, registrar, or academic-standards committee treats as coming "from the system," a fabricated claim inherits institutional authority. The closer to the system of record, the more a false statement costs and the less likely a busy reader is to re-check it.*

In the worked integration, data minimization happens at which stage?

[( )] Stage 1, because the LMS export contains only a few columns
[(X)] Stage 2, where raw rows are reduced to derived features before any model call
[( )] Stage 3, because the local model promises not to memorize inputs
[( )] Stage 4, where the report is printed

---

# Part III: Governance — When Integration Is (Not) Appropriate

In this Part you will apply FERPA, data minimization, and human-in-the-loop requirements to integration designs — including learning to say the most important sentence in AI engineering: "we should not build this arrow."

## 3. The Rules of the Road

**Why this matters:** In the governance activity we organized AI risk work with the **NIST AI RMF** — *Govern, Map, Measure, Manage* — and saw that the EU AI Act treats education (admissions, assessment, grading) as **high-risk** by default. Institutional integration is where those abstractions become concrete: Model 1's diagram *is* the Map function; the rubric lab's agreement and bias measurements *are* the Measure function; today's HITL and minimization decisions *are* Govern and Manage.

**FERPA in one paragraph.** FERPA protects *education records* — records directly related to a student and maintained by the institution. Practically, for AI integration: (a) grades, submissions, and advising notes are education records; (b) disclosing them to an outside party (including a cloud AI vendor) generally requires either consent or a contractual "school official" arrangement limiting use; (c) students have the right to inspect records about them — including, arguably, AI-generated notes stored about them; and (d) de-identification helps only if re-identification is not reasonably possible, which a rich feature vector can defeat. A local model on institution-controlled hardware sidesteps (b) entirely — the record never leaves — which is a major reason local AI matters in education.

**Three governance requirements for any campus AI integration:**

| Requirement | What it demands | In today's worked example |
|-------------|-----------------|---------------------------|
| Data minimization | Send each component only the fields its task needs | Stage 2's aggregation; no names or demographics |
| Human-in-the-loop | AI outputs are drafts until a responsible person approves; the write path to the system of record runs through a human | No arrow from pipeline to gradebook; a human reads the report |
| Auditability | Every AI-derived claim is traceable to source evidence; runs are logged and reproducible | Stage 4 evidence verification; temperature 0 and fixed seed |

**When integration is NOT appropriate.** Decline to build the integration when any of these hold: the task requires demographic or protected-class fields the model has no need for; the output would write directly to a system of record with no human gate; errors are high-stakes and the measured error rate (you measured one in the rubric lab!) exceeds what the stakes tolerate; the data would leave institutional control without a FERPA-adequate contract; or the affected people (students) have no way to know, contest, or correct what the AI recorded about them.

## Model 3: Four Proposed Integrations

| Proposal | Data used | Output goes to | Human gate? |
|----------|-----------|----------------|-------------|
| A. Draft feedback on essays, instructor reviews before release | submission text only | instructor's review queue | yes |
| B. Auto-post quiz scores computed by AI directly to SIS | submissions + roster | SIS gradebook | no |
| C. Weekly summary of ungraded-submission backlog per course | counts only, no content | department chair email | yes (chair reads) |
| D. Predict final grades from demographics + gradebook, shown to advisors | grades + demographics + financial aid status | advising dashboard | nominally (advisor sees a score) |

### Critical Thinking Questions

7. Rank proposals A-D from most to least appropriate, applying the three governance requirements and the "not appropriate" list. For the proposal you rank last, name *every* criterion it violates. (The Recorder writes the ranking with one justification per proposal; the Presenter reports where the group disagreed.)

   > *Hint: C uses minimal, non-content data with a human reader — hard to object to. A keeps a strong human gate over content. B violates HITL on the highest-stakes write path (Model 1's channel 5). D uses protected-class and financial data as predictive features, outputs a score a busy advisor may treat as fact, and touches the early-alert case study from the *Case Study: Early-Alert and At-Risk Identification with Local AI* activity — count its violations carefully: minimization? auditability? contestability?*

8. For proposal D, the vendor argues the human gate is satisfied because "an advisor sees the prediction before acting." Using the idea of *automation bias* (people tend to accept a machine's suggestion rather than re-derive it), explain why a nominal human gate can fail to be a real one, and propose one concrete interface change that makes the human's judgment genuinely load-bearing.

   > *Hint: A bare score ("risk: 87") invites acceptance; there is nothing to disagree *with*. Showing the cited evidence (as our stage 4 did), requiring the advisor to record a reason before acting, or presenting the features without a conclusive score all force engagement. A gate is real when the human can — and sometimes does — reach a different conclusion.*

9. Map each of today's artifacts onto the four NIST AI RMF functions (*Govern, Map, Measure, Manage*): Model 1's diagram, the rubric lab's kappa and bias experiments, the minimization in stage 2, and the decision to leave out the pipeline-to-gradebook arrow. Which function does your team have the *least* practice with so far in this course?

   > *Hint: Map = knowing your system and context (the diagram). Measure = evaluation and monitoring (kappa, hallucinated-evidence rate, bias probes). Manage = mitigations in the design (minimization, no write arrow). Govern = assigning accountability — who is named as responsible when the pipeline is wrong? That last one rarely appears in code, which is exactly the point.*

Under FERPA, the cleanest reason a *local* model changes the compliance analysis is:

[( )] Local models are more accurate than cloud models
[( )] FERPA only applies to data transmitted over the internet
[(X)] The education record never leaves institutional control, so no disclosure to an outside party occurs
[( )] Local models automatically de-identify their inputs

---

# Part IV: Synthesis and Practice

## Exercises

1. *Design an integration on paper.*

   - *What to do:* Choose a campus AI use case (examples: AI-drafted discussion-board summaries for instructors; a chatbot answering "when is it due?" questions from the syllabus; AI-suggested regrade candidates). Draw a complete data-flow diagram in Model 1's style: every system as a box, every channel as a numbered arrow, every arrow labeled with the exact fields that cross it and the mechanism (API, LTI, export).
   - *Starter hint:* Start from the data's home (LMS or SIS), and place the model box explicitly — local or cloud — because that placement changes everything downstream. Mark the human gate with a distinct symbol.
   - *You've succeeded when:* Another team can look only at your diagram and answer: what data does the model see, who sees the output, where is the human gate, and does anything write to a system of record?

2. *FERPA analysis of your design.*

   - *What to do:* For each arrow in your exercise 1 diagram, write one row of a FERPA table: fields crossing, is it an education record, does it leave institutional control, what makes the flow permissible (consent, school-official contract, de-identification, or never-leaves), and the minimization applied.
   - *Starter hint:* Be honest about "de-identified": if the flow includes a feature vector rich enough to match to a known student, write "pseudonymous," not "de-identified," and treat it as a record.
   - *You've succeeded when:* Every arrow has a defensible justification or has been redesigned/deleted — and at least one arrow in your first draft *did* get redesigned or deleted (if none did, your first draft was suspiciously perfect; probe harder).

3. *Run the worked integration against the full synthetic dataset.*

   - *What to do:* Replace the inline `EXPORT` string in the code cell with the full course dataset [/files/data/synthetic_gradebook.csv](https://www.billmongan.com/Ursinus-CS357-Fall2026/files/data/synthetic_gradebook.csv) (40 synthetic students), run the pipeline, and report: how many notes were produced, how many failed JSON parsing or evidence verification, and one note you would *not* forward to a human reader as-is.
   - *Starter hint:* Load the file with `open(...)` in place of `io.StringIO(EXPORT)`. Handle blank score cells (they are realistic missingness, not errors) — the `summarize` function already skips them; confirm it.
   - *You've succeeded when:* You report counts (produced / parse-failed / verification-failed) like the rubric lab's CSV report did, plus a two-sentence quality judgment of the weakest note.

4. *The "should we build it" memo.*

   - *What to do:* Write a half-page memo recommending for or against proposal D from Model 3, addressed to a campus AI governance committee. Cite specific rows of your FERPA table format, at least one measured quantity from the rubric pipeline lab (agreement or hallucinated-evidence rate) as evidence about AI reliability, and the NIST function each recommendation serves.
   - *Starter hint:* A strong memo proposes an alternative that captures some benefit at lower risk (for example, proposal C's aggregate-counts approach), rather than a bare "no."
   - *You've succeeded when:* The memo makes a clear recommendation, every claim is tied to a criterion or measurement, and it names who would be accountable (Govern) if the recommendation is adopted.

---

## Reflection Prompt

*Personal:* You are a student inside these systems right now. Which arrow in Model 1's diagram were you unaware of before today, and does knowing it exists change what you would want to ask your institution?

*Technical:* The strongest privacy control in today's pipeline was architectural (a local model; a missing arrow), not textual (nothing in the prompt said "be private"). Give one more example from this course where a guarantee you needed was enforced in architecture rather than in a prompt, and state the general principle.

*Societal:* The Ursinus Question "How should we live together?" is partly a question about institutions — the systems we build to hold each other's records, judgments, and futures. When a college adds AI to those systems, the students affected did not choose it and often cannot see it. What does living together *well* require here: consent, transparency, contestability, all three, or something more? Who at an institution should be able to say "no" to an integration, and on whose behalf?

---

## -> Coming Up Next

Today's most contested proposal (D) predicted student outcomes from behavioral and demographic data. Next we take that exact use case seriously as a case study: **early-alert and at-risk identification with local AI** — how it works, why institutions want it, and how it fails.

---

## 4. Further Reading

- U.S. Department of Education, Family Educational Rights and Privacy Act (FERPA) guidance: https://studentprivacy.ed.gov/
- NIST AI Risk Management Framework (AI RMF 1.0): https://www.nist.gov/itl/ai-risk-management-framework
- Canvas LMS REST API documentation: https://canvas.instructure.com/doc/api/
- 1EdTech, Learning Tools Interoperability (LTI) standard: https://www.1edtech.org/standards/lti
- U.S. Department of Education, Office of Educational Technology. "Artificial Intelligence and the Future of Teaching and Learning" (2023).
