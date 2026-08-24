<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-critiquerefine.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-critiquerefine.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Critique and Refine Pattern

The *Orchestration Patterns: Pipelines, Routers, and Planners* activity wired agents into pipelines; today we study the most important two-agent pipeline of all.  Writers improve through revision, and so do agents: a **generator** produces a draft, a **critic** evaluates it against explicit criteria, and the generator **refines** using the critique, looping until the critic approves or a budget expires.  This is the workhorse pattern of Critique and Refine.  We move from **why separation helps $\rightarrow$ the loop and its stopping rules $\rightarrow$ implementation $\rightarrow$ when refinement fails**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Generator** | The agent role responsible for producing the initial draft or creative output. The generator explores possibilities and does not apply the evaluation criteria; that is the critic's job. | The agent with system prompt "You draft short announcements for a college class" that produces the first version of the text. |
| **Critic** | The agent role responsible for evaluating a draft against an explicit rubric and returning a structured verdict. The critic judges; it does not create. | The agent that checks whether an announcement has exactly 3 sentences, mentions a specific date, and contains no exclamation points. |
| **Rubric** | A written list of specific, machine-checkable criteria that the critic uses to evaluate the draft. A rubric replaces vague instructions like "make it better" with concrete, objective tests. | `{"verdict": "revise", "issues": ["word count 142 exceeds 100", "claim 2 has no citation"]}` |
| **Convergence** | The property of the critique-refine loop where each revision brings the draft closer to passing all criteria, so the loop terminates in a reasonable number of rounds. A good rubric with actionable feedback produces convergence; vague feedback produces oscillation. | A loop that starts with 3 issues, then 2 issues, then 0 issues and accepts; that is convergence. |
| **Oscillation** | A failure mode where the loop never converges: fixing one issue reintroduces a previous issue, and the draft bounces back and forth between failing states without making net progress. | Round 1: too long; Round 2: too short but now missing a date; Round 3: has date but too long again. |
| **Reward Hacking** | A failure mode where the generator satisfies the literal text of the rubric criteria while violating their intent, for example, achieving "exactly 3 sentences" by stuffing three ideas into one sentence using semicolons. | A draft that technically has 3 sentences but each sentence is 80 words long and impossible to read. |

---

# Part I: Why a Separate Critic?

In this section you will examine why separating generation from evaluation produces better results than asking one agent to do both.  You will analyze two real critique transcripts and practice writing structured, actionable feedback, skills you will need when designing your own critic agents in the Critique and Refine.

## 1.  Generation and Evaluation Are Different Jobs

**Why this matters:** Think about the best feedback you have ever received on a piece of writing.  It probably did not come from the person who wrote it; it came from someone reading it fresh, applying standards you had already agreed on.  When the same person both writes and evaluates in the same sitting, they tend to approve their own work because they remember what they meant to say.  The same problem applies to LLMs: a model asked to "write it and make sure it's good" conflates two tasks that need different mental stances.  Separating the generator and the critic (giving them different system prompts and different information) forces independent evaluation.

Asking one prompt to "write it well" conflates two tasks.  Generation explores; evaluation judges against criteria.  When the same context does both simultaneously, neither gets the model's full attention, a small context window argument again.  Separating roles also lets us give the critic what the generator should not have: a **rubric**.

The critic needs criteria, not vibes.  "Make it better" produces drift; "Check: (1) under 100 words, (2) cites a source for each claim, (3) reading level appropriate for first-years" produces convergence.  The critic returns structured output so the generator knows exactly what to fix:

```json
{"verdict": "revise", "issues": ["word count is 142, must be under 100", "claim 2 has no citation"]}
```

Stopping rules prevent infinite polishing.  Loop until `verdict == "accept"`, with a maximum of $R$ rounds.  On budget exhaustion, return the best draft *with the outstanding critique attached*, disclosure of known defects rather than silent confidence.

The following equation summarizes this loop compactly: at each round $t$, the critic $C$ evaluates the current draft against the rubric and returns a list of issues, and the generator $G$ produces an improved draft using those issues.  The loop runs until the critic accepts or round $R-1$ is reached.

$$
d_{t+1} = G(d_t, C(d_t, \text{rubric})), \quad t = 0, 1, \dots, R-1
$$

Where $d_t$ is the draft at round $t$, $G$ is the generator, and $C$ is the critic applying the rubric.

---

## Model 1: Two Transcripts

**Transcript A:** The critic says "This is pretty good, maybe tighten it up a bit."  Five rounds later the draft is oscillating between slightly different versions with no clear improvement direction.

**Transcript B:** The critic says `{"verdict": "revise", "issues": ["word count 142 exceeds limit of 100", "claim 2 ('enrollment increased 15%') has no citation"]}`.  One round later the draft passes.

### Critical Thinking Questions

1.  Diagnose Transcript A: which specific property of the critique caused oscillation rather than convergence?  Name at least two properties that are present in Transcript B's critique and absent in Transcript A's.

   > *Hint: Transcript B tells the generator (a) what criterion was violated and (b) specifically which part of the draft violated it.  Transcript A tells the generator neither.  Without knowing where a problem is, what can the generator do except guess?*

2.  Rewrite a vague critique in Transcript B's structured style for a draft announcement of your choosing.  Start by planting at least two specific defects in the draft, then write the JSON critique that identifies them precisely.  What makes a critique *actionable*: reference to criteria, location of the defect, or both?

   > *Hint: "The draft is too long" is a criterion reference.  "Sentence 3 adds 40 words that repeat what sentence 1 already said" is both a criterion reference and a location.  Which one gives the generator enough information to make the right change?*

3.  The critic in Transcript B never suggests specific wording for the fix.  Should critics propose fixes or only identify defects?  Take a clear position and note one risk of each policy.

   > *Hint: If the critic suggests specific wording, is it acting as a generator now?  What happens to the separation of roles?  On the other hand, if the critic only says "sentence 2 is unclear," can the generator always figure out how to fix it?*

With the design principles from Part I in hand, Part II shows the complete implementation of the critique-refine loop so you can see exactly how those principles translate to code.

---

# Part II: Implementation

In this section you will read the full working implementation of the critique-refine loop and answer questions that connect the code back to the design principles from Part I. Pay close attention to the temperature settings and the separation of what the generator and critic each receive.

## 2.  The Loop in Forty Lines

**Why this matters:** The code below implements the entire critique-refine loop.  Notice three design decisions that directly implement the principles from Part I: (1) the generator and critic are separate `llm` calls with different system prompts, (2) the critic receives the RUBRIC but the generator does not; the generator only receives the issues list from the critic's output, and (3) the loop has a hard maximum of `rounds` iterations so it cannot run forever.  The temperature settings encode a meaningful choice: the generator runs warm (temperature 0.8 for exploration, then 0.3 for disciplined revision), while the critic runs cold (0.0 for deterministic evaluation).

You can run this locally with `ollama run llama3.2` in one terminal and then run the script in another:

```bash
ollama run llama3.2
python critique_refine.py
```

---

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import json
import requests

def llm(system, user, temperature=0.3):
    """Call the local LLM. Temperature controls creativity vs. determinism."""
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": temperature, "seed": 42},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[critique:llm] {e}")
        import traceback; traceback.print_exc()
        return ""

# The RUBRIC is the critic's instructions, specific, checkable criteria.
# Crucially, the GENERATOR never sees this rubric directly.
# It only sees the list of issues the critic identified.
RUBRIC = """Evaluate the draft against ALL of these criteria:
1. Exactly 3 sentences (count them carefully).
2. Mentions a specific date (day of week, date, or both).
3. No exclamation points anywhere in the draft.
Respond ONLY with valid JSON in this exact format:
{"verdict": "accept" or "revise", "issues": ["specific defect 1", "specific defect 2"]}
If all criteria are met, return: {"verdict": "accept", "issues": []}"""

def critique(draft):
    """Run the critic on a draft. Returns a dict with 'verdict' and 'issues'."""
    out = llm(RUBRIC, draft, temperature=0.0)  # cold: deterministic evaluation
    try:
        # Strip markdown code fences if the model adds them
        clean = out.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception as e:
        print(f"[critique:parse] {e} on output: {out[:80]}")
        import traceback; traceback.print_exc()
        # Fail closed: if we cannot parse the verdict, assume "revise"
        # This is safer than failing open (assuming "accept") for most use cases
        return {"verdict": "revise", "issues": ["critic output was not valid JSON; treating as revise"]}

def critique_refine(task, rounds=3):
    """
    Run the critique-refine loop.
    Returns: (final_draft, final_verdict_dict, rounds_used)
    """
    # Round 0: generate the initial draft (warm temperature for creative exploration)
    draft = llm(
        "You draft short announcements for a college class.",
        task,
        temperature=0.8  # warm: explore different phrasings
    )
    print(f"--- initial draft ---\n{draft}\n")

    for r in range(rounds):
        verdict = critique(draft)
        print(f"--- round {r}: {verdict['verdict']} | issues: {verdict['issues']}")

        if verdict["verdict"] == "accept":
            return draft, verdict, r  # success: return before budget is exhausted

        # Pass only the issues list to the generator, not the rubric itself
        draft = llm(
            "Revise the draft to fix EXACTLY the listed issues, changing nothing else.",
            f"Draft:\n{draft}\n\nIssues to fix:\n{json.dumps(verdict['issues'], indent=2)}",
            temperature=0.3  # cooler: disciplined revision rather than free exploration
        )

    # Budget exhausted: return the best draft we have, with outstanding issues attached
    return draft, verdict, rounds

final, verdict, used = critique_refine(
    "Announce that Critique and Refine is due October 27 and office hours moved to Wednesday."
)
print(f"\n=== FINAL DRAFT (after {used} revision rounds) ===\n{final}")
if verdict["verdict"] != "accept":
    print(f"\n[Note: budget exhausted; outstanding issues: {verdict['issues']}]")
```

---

## Model 2: Instrumenting the Loop

### Critical Thinking Questions

4.  The code runs the generator warm (temperature 0.8 for the first draft, then 0.3 for revisions) and the critic cold (temperature 0.0).  Justify each specific choice: what would go wrong if the critic ran at 0.8?  What would go wrong if the first draft ran at 0.0?

   > *Hint: A critic at 0.8 might flag different issues each time it evaluates the same unchanged draft; what would that do to the convergence of the loop?  A generator at 0.0 produces the same draft every time; if the first draft fails, what happens when you try to revise it?*

5.  The fallback when the critic emits invalid JSON is to demand revision (failing *closed*).  The alternative is to assume the draft is acceptable (failing *open*).  Argue which default is correct for (a) a class announcement and (b) a medical summary, explaining what goes wrong in each case if you choose the wrong default.

   > *Hint: Failing closed means "when uncertain, reject and retry."  Failing open means "when uncertain, pass."  For a class announcement, what is the cost of a false rejection?  For a medical summary, what is the cost of a false approval?*

6.  Run the loop three times on the same task and record the rounds-to-accept for each run.  Is the variance coming from the generator (different drafts), the critic (different verdicts on the same draft), or both?  Design a one-variable experiment (changing exactly one thing) that would let you tell which source of variance is larger.

   > *Hint: To isolate generator variance, fix the seed of the critic and vary the generator's seed.  To isolate critic variance, fix the draft (use the same input every time) and run the critic multiple times.  Which experiment is easier to set up with the code above?*

> **Common Misconception:** Students often assume that more revision rounds always produce better output.  This is not true.  After the loop converges (all criteria met), additional rounds do nothing useful.  And if the loop oscillates, more rounds only waste time and tokens without improving the draft.  The number of rounds to budget should be set based on empirical measurement: run the loop on 20 representative tasks, plot rounds-to-accept, and set your budget at the 90th percentile.  Setting it at 10 "to be safe" often means 9 wasted rounds on tasks that converge in 1.

Now that you can read and run the loop, Part III examines the three ways it commonly fails, so you can detect and fix these problems in your own Critique and Refine implementation.

The principal reason the critic receives a rubric while the generator does not is:

[( )] Rubrics are too long for the generator's context
[(X)] Separating exploration from criterion-checking gives each small, focused context one job, improving both
[( )] The generator cannot read JSON
[( )] Critics require higher temperature than generators

---

# Part III: When Refinement Fails

In this section you will study three failure modes that can make the critique-refine loop produce worse results than a single-shot approach.  Knowing these failure signatures (and how to measure them) is what separates a loop that works in a demo from one that works reliably in production.

## 3.  Failure Modes to Hunt in Critique and Refine

**Why this matters:** Understanding how the critique-refine loop fails is as important as knowing how it works.  Each of the three failure modes below has a measurable signature; you can detect them by instrumenting the loop rather than only checking the final output.  Building this measurement into Critique and Refine from the start (rather than discovering failures at submission time) is the application of the design-first principle from the earlier activity.

**Rubber-stamping:** The critic accepts everything, often because the criteria are vague, because the critic sees the generator's reasoning and is anchored by it, or because the model is trained to be agreeable.  You can detect this by measuring the acceptance rate on deliberately flawed drafts: if the critic accepts a draft with a known planted defect, it is rubber-stamping.

**Oscillation:** Fixing issue 1 reintroduces issue 2, and the loop cycles without net progress.  You can detect this by tracking the set of issues across rounds: if the same issue appears in round 1, disappears in round 2, and reappears in round 3, you have oscillation.

**Reward hacking:** The generator satisfies the letter of the rubric while betraying its intent.  Example: "exactly 3 sentences" achieved by connecting three ideas with semicolons into one grammatical but unreadable run-on.  You can detect this with a human spot-audit of "accepted" outputs: look specifically for drafts that passed all criteria but that a human would rate as poor quality.

Each failure has a measurement:
- Rubber-stamping -> acceptance rate on known-flawed drafts (should be 0%, high rate = failure)
- Oscillation -> issue-recurrence rate across rounds (should decrease monotonically, non-monotone = failure)
- Reward hacking -> human quality rating of accepted drafts vs. rubric-passing rate (gap = failure)

---

## 4.  Exercises

1.  **Calibrate the critic.**

   *What to do:* Write five announcements yourself, each with exactly one planted defect that violates one of the three rubric criteria.  Feed each to the critic alone (without running the full loop) and record whether it correctly identifies each defect.  Report the detection rate per criterion (e.g., "the critic detected the sentence-count violation 4/5 times").  Identify which criterion the critic is weakest on and try rewriting that criterion in the rubric to improve detection.

   *Starter hint:* To test the critic in isolation, call `critique(your_draft)` directly with `draft` set to one of your planted-defect announcements.  To test each criterion separately, write one draft that violates only criterion 1, one that violates only criterion 2, and one that violates only criterion 3.  This isolates which criterion the critic struggles with.

   *You've succeeded when:* You have a per-criterion detection rate and a revised rubric wording that improves the weakest criterion's detection rate by at least 20 percentage points in a re-run.

2.  **Adversarial generator: reward hacking.**

   *What to do:* Try to manually reward-hack your own rubric: write a draft that passes all three criteria checks (exactly 3 sentences, mentions a specific date, no exclamation points) while being a bad announcement by any human standard.  Then add a fourth criterion to the rubric that closes the loophole you exploited, and verify that the critic now flags your hacked draft.

   *Starter hint:* Common reward-hacking strategies: (1) meet "exactly 3 sentences" by combining three ideas with semicolons into one long unreadable sentence; (2) meet "mentions a specific date" by burying it in parentheses at the end of an unrelated sentence; (3) replace exclamation points with ALL CAPS for emphasis.  After finding your hack, add a criterion like "each sentence must be under 25 words" or "the date must appear in the first sentence."

   *You've succeeded when:* You can show (a) the hacked draft that passes the original 3-criterion rubric, (b) the new criterion that catches it, and (c) a revised draft that passes all 4 criteria and is also a good announcement.

3.  **Convergence plot.**

   *What to do:* Run the full critique-refine loop ten times on different announcement tasks.  For each run, record the number of rounds used before acceptance (or the maximum if it never accepted).  Plot rounds-to-accept (x-axis: run number, y-axis: rounds used).  Propose a budget $R$ that accepts at least 90% of runs.  State explicitly what your system does with the remaining 10% (return with outstanding issues, escalate to human, etc.).

   *Starter hint:*
   ```python
   import matplotlib.pyplot as plt

   tasks = [
       "Announce the lab 3 deadline of October 27.",
       "Remind students that office hours moved to Wednesday at 3pm.",
       # ... add 8 more varied announcement tasks
   ]

   rounds_used = []
   for task in tasks:
       _, _, used = critique_refine(task, rounds=5)
       rounds_used.append(used)

   plt.bar(range(len(tasks)), rounds_used)
   plt.xlabel("Run")
   plt.ylabel("Rounds to accept")
   plt.title("Critique-Refine Convergence")
   plt.savefig("convergence.png")
   ```

   *You've succeeded when:* Your plot shows the distribution of rounds-to-accept, and your proposed budget $R$ is justified by the data rather than chosen arbitrarily.

4.  **Self versus other critic comparison.**

   *What to do:* Replace the separate critic call with a single prompt asking the generator to self-critique and revise in one shot (e.g., "Write an announcement, then evaluate it against these criteria, then revise it").  Compare the quality of the final output against the two-agent version on five different tasks.  Report: (a) does the self-critique version meet the rubric criteria as often?  (b) is the output quality higher or lower by human judgment?  (c) how do the token costs compare?

   *Starter hint:*
   ```python
   def self_critique_refine(task):
       combined_prompt = f"""Complete this in three steps:
   1. Write a draft announcement for: {task}
   2. Evaluate your draft against: {RUBRIC}
   3. Revise to fix any issues you found.
   Output only the final revised announcement."""
       return llm("You are an expert announcement writer.", combined_prompt, temperature=0.3)
   ```

   *You've succeeded when:* You have a side-by-side comparison on 5 tasks with a rubric pass rate for each approach and a one-sentence conclusion about whether separation earned its extra latency and API cost.

---

## Reflection Prompt

Respond to all three levels in your notebook:

**Personal:** Think of the best piece of feedback you ever received on your own work: a paper, a project, a presentation.  Did it resemble Transcript A (vague, general) or Transcript B (specific, criterion-based)?  What rubric was your reviewer implicitly using?  Would you hand that rubric to an AI critic reviewing your work today, and what would you need to add or clarify to make it machine-usable?

**Technical:** The critique-refine pattern adds latency proportional to the number of revision rounds.  For a system that serves 1,000 requests per day, each request taking an average of 2 revision rounds at 3 seconds per LLM call, compute the total additional time per day spent on revision versus a zero-round baseline.  At what scale does this latency cost justify investing in a better generator (fewer revision rounds needed) rather than a better critic (more accurate first-pass evaluation)?

**Societal:** The critic in today's loop applies a human-written rubric mechanically.  In journalism, academic publishing, and legal review, human editors and peer reviewers apply judgment that goes beyond any written rubric; they know context, they catch implications, they apply community standards that are not fully articulable.  What kinds of evaluation should not be delegated to an automated critic, even a well-calibrated one?  What criteria would you use to decide?

---

-> **Coming Up Next:** The *Multi-Agent Debate* activity extends the critique-refine idea: instead of one critic evaluating one generator's output, multiple agents argue different positions before a judge resolves the disagreement.  The generator-critic loop you built today is the heart of the Critique and Refine, *Critique and Refine*.

---

## Further Reading

- Madaan et al. "Self-Refine: Iterative Refinement with Self-Feedback."  *NeurIPS* (2023).
- Bai et al. "Constitutional AI: Harmlessness from AI Feedback."  (2022).  Critique against explicit principles at training scale.
- Anthropic engineering blog.  "Building Effective Agents" (2024), evaluator-optimizer pattern.

---

# Extension: Human-in-the-Loop (self-paced)

Optional, and not assumed by the parts above.  Critique and refine puts a second model in the loop.  The harder design question is where a *person* goes in the loop: what gets escalated, who approves what, and how much autonomy is appropriate for a given blast radius.  Your final project will make you answer that in writing, so this is worth a read before the proposal.

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Human-in-the-Loop (HITL)** | A system design where a human must review and approve specific agent actions before they are executed, rather than letting the agent act freely | An agent pausing before sending an email to 847 customers and showing a human the draft for approval |
| **Human-on-the-Loop** | A design where the agent acts immediately but a human monitors the activity stream and can intervene if something goes wrong | An agent filing support tickets autonomously while a supervisor watches a dashboard showing each ticket as it is filed |
| **Escalation Trigger** | A specific condition that causes an agent to pause and ask for human approval instead of proceeding | "If the estimated cost of the action exceeds $50, always ask for approval" |
| **Approval Fatigue** | The phenomenon where a reviewer who sees too many approval prompts starts clicking "approve" without reading them, eliminating the safety benefit of the checkpoint | A human who approves 200 checkpoints per day in an average of 1.5 seconds each is not actually reading the checkpoints |
| **Minimal Footprint Principle** | The design heuristic that says: when multiple actions could accomplish a goal, prefer the one with the smallest scope, fewest side effects, and highest reversibility | Moving duplicate files to an archive folder (reversible) rather than deleting them permanently (irreversible) |
| **Trust Calibration** | The ongoing process of adjusting how much autonomy an agent gets based on its measured error rate in a domain: more autonomy as it proves reliable, less if errors rise | Reducing the agent's confidence threshold for escalation after it makes three wrong classifications in a row |

---

In this first model, you will map out the space between fully manual and fully autonomous agent operation, and you will learn to apply five specific trigger conditions that determine when a human checkpoint is warranted.  This is the foundation of all the design decisions that follow.

### The Autonomy Spectrum and Checkpoint Criteria

Agent deployment exists on a spectrum from fully manual (the human does every step) to fully autonomous (the agent acts without any checkpoints).  Between these extremes are two important operating modes:

- **Human-on-the-loop**: The agent acts immediately but a human monitors and can intervene.  Used for low-stakes, reversible, high-volume tasks where errors are catchable before they cause harm.
- **Human-in-the-loop**: The agent *pauses before acting* on specific trigger conditions and waits for explicit human approval.  Used for high-stakes, irreversible, or ambiguous situations where a mistake before intervention could cause lasting harm.

The key design decision is identifying the **trigger conditions** that promote an action from autonomous execution to human review.  Research and practice have converged on five primary triggers:

1.  **Irreversibility**: The action cannot be undone: file deletion, sent email, financial transaction, published post.
2.  **High stakes**: The consequences of error are large: production deployment, external communication to many people, legally binding document.
3.  **Low confidence**: The agent's own uncertainty about the goal or the action is above a threshold: the model is less than 70% confident in its classification.
4.  **Novelty**: The situation does not closely match any prior successful pattern in the agent's history: this type of request has never been handled before.
5.  **Ambiguity**: The user's intent admits multiple reasonable interpretations that would lead to different actions: "clean up the folder" could mean archive, delete, or reorganize.

The **minimal footprint principle** is a design heuristic that says: when multiple actions could accomplish a goal, prefer the one with the smallest scope, fewest side effects, and highest reversibility.  Escalate *before* taking large actions, not after.

| Situation | Action Type | Reversible? | Stakes | Escalate? | Rationale for This Decision |
|-----------|-------------|-------------|--------|-----------|-----------|
| Agent identifies 3 files as duplicates and is about to delete them permanently | File deletion | No: deleted files may not be recoverable even from trash | Medium: data loss is costly but not catastrophic | Yes | Deletion is irreversible; false positives are common in duplicate detection; user should verify before data is lost |
| Agent is about to send an email on the user's behalf to a client | External communication | No: recipient has received the email and cannot un-receive it | High: professional reputation and client relationship are at stake | Yes | Irreversible action; high stakes; the agent cannot know the full context of the client relationship |
| Agent is adding a calendar event for a meeting the user explicitly requested in the same conversation | Calendar write | Yes: the event can be deleted or edited immediately | Low: a wrong event is easily corrected | No | Low stakes; reversible; user intent is unambiguous (they just asked for this); escalation would add friction with no safety benefit |
| Agent is about to purchase a $500 software license using the user's payment method | Financial transaction | No: refund may or may not be possible; time and effort are lost | High: $500 expenditure; potentially non-refundable | Yes | Financial cost; irreversibility uncertain; exceeds routine spending threshold |
| Agent is pushing code to a production branch that serves real users | Code deployment | Partially: rollback is possible but requires effort and causes downtime | Critical: a bug in production affects real users immediately | Yes | Production impact; blast radius is very high; even small errors affect users who cannot wait for a fix |
| Agent is fetching a public webpage to answer a factual question | Read-only web request | N/A: reads have no lasting effect | Low: the worst outcome is a wrong answer | No | No side effects; nothing is changed; any error is easily corrected by asking again |

#### Questions to Work Through

1.  The table marks calendar-event creation as "No escalation" because it is reversible.  Describe a realistic scenario in which creating a calendar event *should* trigger escalation despite being easy to undo.  What specific property of the situation changes the calculus?

   > *Hint: Consider an agent that creates a meeting invitation and sends it to 50 external attendees.  The event itself is deletable, but what side effect of creating a recurring meeting invitation cannot be easily undone?  Think about what the act of sending the invitation does, independent of whether the event is later deleted.*

2.  The minimal footprint principle says prefer smaller-scope actions.  An agent is asked to "clean up the project folder."  It could (a) move files to a dated archive folder with a name like `archive-2026-06-21/`, (b) delete files it deems unnecessary, or (c) ask the user for an explicit list of files to remove before doing anything.  Rank these three options by their footprint from smallest to largest, and identify which escalation trigger applies to each option.

   *Hint: Think about what information is destroyed or moved beyond easy recovery in each option.  Which option creates the smallest blast radius if the agent makes a mistake?*

3.  Confidence-based escalation requires the agent to know when it does not know.  How would you operationalize a "confidence threshold" in practice: what specific numeric signal from the model would you measure, and what are its failure modes (situations where the confidence score is wrong)?

   > *Hint: LLMs produce a probability score for each possible next token.  One approach is to look at the probability of the top choice versus the second choice: a high-probability first choice suggests confidence; a near-tie suggests uncertainty.  But calibration is imperfect: when might a model produce a high-probability answer that is nevertheless wrong?  Think about domains where the training data was mostly confident assertions, even when those assertions were incorrect.*

---

*Model 1 defined when to escalate.  Model 2 shows how: specifically, how to pause the agent's execution, save everything it needs to resume, and communicate with the human in a format that supports a real decision rather than a rubber-stamp click.*

### The Escalation Protocol

When a trigger condition fires, the agent must pause execution, preserve its current state, communicate the reason for escalation to the human in a way that enables an informed decision, and then resume (or abort) once the human responds.  A naive implementation blocks the entire process synchronously; the agent freezes and waits.  A production-grade implementation suspends state asynchronously (saving its work and returning immediately, resuming only when the human responds): the agent saves its work and resumes when the human responds, potentially hours later.

The following Python pseudocode (simplified illustration, not runnable as-is) shows the escalation logic:

```python
def execute_action(action, context, confidence):
    """
    Attempt to execute an action. Escalate to a human if any trigger fires.
    Returns the action result, or raises EscalationPending if human approval is needed.
    """
    reasons = []    # Collect all reasons for escalation; there may be more than one

    # Trigger 1: irreversibility, cannot be undone once executed
    if action.is_irreversible():
        reasons.append(f"irreversible: {action.describe_side_effects()}")
        # Example: "irreversible: sends email to client@example.com"

    # Trigger 2: cost exceeds a threshold defined in configuration
    if action.estimated_cost > COST_THRESHOLD:
        reasons.append(f"cost exceeds threshold: ${action.estimated_cost:.2f}")
        # Example: "cost exceeds threshold: $523.00"

    # Trigger 3: the model's own confidence in this action is too low
    if confidence < CONFIDENCE_THRESHOLD:
        reasons.append(f"confidence below threshold: {confidence:.2f}")
        # Example: "confidence below threshold: 0.43"

    # Trigger 4: certain categories of actions always require approval (configured at deployment time)
    if action.category in HIGH_STAKES_CATEGORIES:
        reasons.append(f"action category requires approval: {action.category}")
        # Example: "action category requires approval: external_communication"

    if reasons:
        # One or more triggers fired; create a checkpoint and notify the human
        checkpoint = Checkpoint(
            task_id=context.task_id,         # ID of the parent task this action belongs to
            action=action,                    # The full action object, including all parameters
            reasons=reasons,                  # List of reasons so the human understands why this was escalated
            state_snapshot=context.serialize()  # Complete agent state, everything needed to resume later
        )
        checkpoint.save()       # Persist to database so it survives if the server restarts
        notify_human(checkpoint)    # Send notification (email, Slack, dashboard alert, etc.)
        raise EscalationPending(checkpoint.id)  # Caller catches this and suspends the task

    # No triggers fired; execute the action normally and return the result
    return sandbox.execute(action, context)
```

In **asynchronous HITL**, the agent saves a complete state snapshot before raising `EscalationPending`.  The human reviews the checkpoint (potentially hours later) approves, rejects, or modifies the action, and the agent reloads the snapshot and continues.  The human's response must be cryptographically tied to the specific checkpoint (not just "approve the last thing") to prevent replay attacks where an old approval is reused for a new action.

> **Common Misconception:** Many students assume that "human-in-the-loop" means a human watches every single action the agent takes.  This is not scalable and, paradoxically, produces worse oversight; humans who must approve hundreds of actions per day stop reading them carefully.  Good HITL design is *selective*: humans review the actions that most need their judgment, and the agent handles everything else autonomously.  The goal is quality of oversight, not quantity of approvals.

#### Questions to Work Through

4.  The pseudocode saves `context.serialize()` before escalating.  This snapshot must contain everything needed for the agent to resume correctly after the human approves, potentially hours later.  List at least five specific fields that must be in the snapshot and explain why each is necessary for correct resumption.

   *Hint: Think about what the agent knew at the moment it paused: the original task description, what it has done so far, the action it wants to take, the files it has already modified, and the tool call history.  What would happen if any of these were missing when the agent tried to resume?*

5.  The human receives a notification: "Agent wants to delete `/project/data/results_old.csv`.  Approve?"  This single-line notification is not enough for an informed decision.  Design a richer notification format that includes everything a human needs to make a meaningful choice.  Write out the fields and example values.

   *Starter hint: Think about what questions you would ask before approving this deletion:*
   - *Why does the agent want to delete this file?  (What task is it working on?)*
   - *How large is the file?  When was it last modified?  Is it tracked in git?*
   - *What happens to the task if the human says No?*
   - *Is there a backup?  Can this be undone?*

6.  The code raises `EscalationPending` and the caller suspends the task.  In a web-based agent system, what happens to the HTTP connection between the browser and the server while the agent waits for human approval?  Propose two different architectural patterns for handling this (one synchronous approach and one asynchronous approach) and identify the key tradeoff between them.

   *Hint: Synchronous approach: keep the HTTP connection open (long-poll) and respond when the human approves; simple to implement, but HTTP connections time out after ~30 seconds.  Asynchronous approach: return immediately with a task ID, and the browser polls or uses a WebSocket to check for updates; more complex, but scales to waits of hours or days.*

---

*Model 2 showed how to build escalation infrastructure.  Model 3 addresses a paradox: too much escalation is as dangerous as too little, because humans who see too many checkpoints stop reading them.  This section asks you to design for quality of oversight, not quantity.*

### Approval Fatigue and Trust Calibration

Human oversight only has value if humans engage thoughtfully with the checkpoints they are given.  When the approval rate approaches 100% and the average review time drops to under two seconds, the human is no longer providing oversight; they are providing a rubber stamp.  This is **approval fatigue** (the cognitive phenomenon where frequent, low-stakes approvals train reviewers to stop reading), and it is actively harmful: it creates the *appearance* of oversight without the substance, while adding latency and annoying the reviewer.

Compare two designs for an agent that processes 50 incoming support tickets per day:

**Design A** (checkpoint-heavy): The agent asks for human approval before (1) classifying each ticket, (2) selecting a response template, (3) personalizing the template, and (4) sending the response.  That is up to 200 approval prompts per day from a single agent.

**Design B** (trigger-based): The agent acts autonomously on routine tickets (classification confidence > 0.9, template match score > 0.8, no refund or account-closure language).  It escalates only when a trigger fires.  On average, 8 of 50 tickets per day reach a human reviewer.

| Metric | Design A: Checkpoint-Heavy | Design B: Trigger-Based |
|--------|----------|----------|
| Approvals per day | ~200: human approves every sub-step of every ticket | ~8: human reviews only the tickets that hit a trigger condition |
| Avg. human review time per approval | 1.5 seconds: reviewer is skimming because there are too many | 45 seconds: reviewer is engaged because each escalation is unusual and important |
| Probability human catches an actual error | Low: reviewer skimming at 1.5 sec per prompt does not read carefully | High: reviewer spending 45 seconds on 8 focused cases can read, question, and decide thoughtfully |
| Total human time per day | ~5 minutes total, but low quality and low attention | ~6 minutes total, but high quality and high attention |
| Agent latency per ticket | High: every ticket blocks multiple times waiting for human clicks | Low: 84% of tickets flow through without any pause |

**Trust calibration** is the practice of periodically reviewing autonomous decisions in shadow mode (where the agent acts but a human also reviews the same cases after the fact) to detect systematic errors and adjust thresholds.  As the agent proves reliable in a domain, checkpoint frequency decreases.  If error rates climb, thresholds tighten automatically.  This is not a one-time setup but an ongoing measurement process.

#### Questions to Work Through

7.  Design A has a higher approval count but lower actual oversight quality.  Explain the specific cognitive mechanism by which reviewing more checkpoints leads to *worse* attention per checkpoint.  What psychological phenomenon is at work, and what analogies from other fields (medicine, aviation, nuclear power) show the same pattern?

   *Hint: Research on checklists in high-stakes environments shows that when every item on a checklist is always green, operators stop reading the checklist.  This is sometimes called "alarm fatigue" in medical monitoring.  What does a human brain do differently when it expects a problem versus when it expects everything to be fine?*

8.  In Design B, the agent handles 42 of 50 tickets autonomously, 84% of the workload with no human in the loop.  A critic argues this is dangerous: "If the agent makes a systematic error in how it classifies tickets, 42 tickets per day will be mishandled before anyone notices."  Write a specific counterargument that defends Design B as providing *better* oversight than Design A, using the numbers in the table and the concept of shadow mode review.

   *Hint: Design A provides the illusion of oversight (200 rubber-stamp approvals) while Design B provides actual oversight (8 focused reviews + shadow mode sampling that catches systematic errors).  Which approach is more likely to notice a systematic classification error?*

9.  Trust calibration gradually reduces checkpoint frequency as the agent proves reliable.  What safeguard should prevent this process from reducing oversight to zero, even for a perfect agent?  Who should be authorized to change the trust calibration parameters, and what governance structure should exist around that authority?

   *Hint: Even a perfectly reliable agent might make different errors in novel situations it has never encountered.  What is the minimum checkpoint frequency that should exist regardless of the agent's track record?  Is there a category of actions (by stakes or irreversibility) that should always require human review, no matter how well-calibrated the agent is?*

An agent is given a task that runs overnight as a batch job: process 1,000 customer records and generate personalized outreach emails.  No human is available to review approvals until morning.  The most appropriate human-in-the-loop design for this scenario is:

[( )] Synchronous HITL: pause the batch job for every high-stakes action and wait for a human response before continuing; the human is not available; the job would simply freeze all night
[( )] Disable HITL entirely for batch jobs since no human is available anyway; "no human is available now" is not a reason to abandon oversight; it is a reason to design asynchronous oversight
[(X)] Asynchronous HITL with a pre-approved action policy: define which actions are pre-approved for batch context, escalate exceptions to a human review queue, and do not send any emails until a human clears the queue in the morning
[( )] Run the job fully autonomously and review the sent emails after the fact; reviewing after sending is not oversight; it is auditing after irreversible harm may have occurred

---

### Exercises

1.  **Escalation trigger design.**

   *What to do:* You are building a coding agent that can write files, run tests, and commit to a git repository.  Define a complete set of escalation triggers with specific, measurable thresholds.  For each trigger, explain what harm it prevents and what the cost of a false positive (unnecessary escalation) would be for the developer's workflow.

   *Starter hint:* Think about each action type separately:
   ```
   write_file:   trigger if file is in /etc/, /usr/, or any path outside /workspace/
   run_tests:    no escalation (read-only operation with no side effects)
   git_commit:   trigger if any file containing "secret", "key", or "token" is staged
   git_push:     ALWAYS trigger - push to remote is irreversible and affects others
   delete_file:  ALWAYS trigger - even in /workspace/, deletion is irreversible
   ```
   For each trigger, ask: what is the worst thing that happens if this fires unnecessarily (false positive), and what is the worst thing that happens if it fails to fire (false negative)?

   *You've succeeded when* your trigger list covers all five of the actions above, has specific thresholds (not just "if it seems dangerous"), and includes an explicit cost-benefit statement for each trigger's false-positive rate.

2.  **Checkpoint notification design.**

   *What to do:* Design the human-facing notification for this scenario: "Agent wants to send the following email to 847 customers."  Format it as structured text that includes all the information a human needs to make an informed, non-fatigued decision in under 60 seconds.

   *Starter hint:* A good checkpoint notification answers these questions without requiring the reviewer to ask:
   ```
   CHECKPOINT REQUIRED: External Communication
   Task: [What is the agent trying to accomplish overall?]
   Action: Send email to 847 customers
   Subject: [The email subject line]
   Preview: [First 3 sentences of the email body]
   Triggered by: [Which trigger fired and why]
   If approved: [What happens next]
   If rejected: [What the agent will do instead]
   Estimated impact if wrong: [What goes wrong if this email is incorrect]
   Reversibility: [Can customers be un-emailed? Can a correction be sent?]
   [APPROVE]  [REJECT]  [MODIFY AND APPROVE]
   ```

   *You've succeeded when* your notification design could be handed to a reviewer who has never seen the task before and they could make a confident decision in under 60 seconds without needing to look up additional information.

3.  **Approval fatigue audit.**

   *What to do:* You have logs showing that a human reviewer approved 312 of 315 agent checkpoints last month (99% approval rate), with an average review time of 2.1 seconds per checkpoint.  Write a brief analysis: is oversight functioning?  What specific changes would you make to the checkpoint design, and how would you measure whether the changes improved oversight quality?

   *Starter hint:* A 99% approval rate at 2.1 seconds per review strongly suggests the reviewer is not reading.  To diagnose: pull the 3 rejections and look at what properties they shared.  To fix: consider raising the confidence threshold (so fewer, more important things escalate), adding a "why does this need review?" explanation to each checkpoint, and implementing shadow mode to catch systematic errors that approvals are missing.

   *You've succeeded when* your analysis includes: (1) a diagnosis of why the current system is not working, (2) at least two specific changes to the checkpoint design, and (3) a metric you would track to confirm the changes improved oversight quality.

4.  **Async HITL state machine.**

   *What to do:* Design a state diagram for an agent task that supports asynchronous HITL. Represent it as a table showing all states and the transitions between them, with the event or condition that triggers each transition.

   *Starter hint:* Minimum states to include: Running, Escalated, AwaitingApproval, Approved, Rejected, Resumed, Completed, Aborted.  For each transition, name the event: for example, "Running -> Escalated" is triggered by "trigger condition fires."  Some states should have timeout transitions: what happens if a checkpoint sits in AwaitingApproval for 48 hours with no response?

   *You've succeeded when* your state diagram is complete enough that a developer could implement it directly: every state has at least one incoming transition and at least one outgoing transition, and there are no dead ends except Completed and Aborted.

---

### Reflection Prompt

*Personal:* Approval fatigue is not unique to AI systems; it appears in security certificate warnings in web browsers, terms-of-service agreements, and safety checklists in high-pressure environments.  Describe a specific time when you or someone you know clicked "approve" or "accept" without reading carefully.  What was the system designer assuming about human attention that turned out to be wrong?  How does that experience shape how you would design a checkpoint in an agent system?

*Technical:* Based on today's models, write a specific escalation policy for one of the following agent types: (a) a coding agent that can write files and run tests, (b) a customer service agent that can read and respond to support tickets, or (c) a research agent that can search the web and save documents.  Your policy should include specific trigger conditions with thresholds, a trust calibration schedule, and a minimum checkpoint frequency that cannot be reduced regardless of performance.

*Societal:* Human-in-the-loop is sometimes described as the solution to AI safety problems.  But this activity shows that HITL has real costs: latency, reviewer attention limits, approval fatigue, and the need for humans to be available at arbitrary times.  As AI agents become more capable and are deployed in higher-stakes domains (medical diagnosis, legal advice, financial planning), is HITL a sustainable long-term solution, or does it need to evolve into something else?  What would that something else look like?

---

-> Coming Up Next: Human-in-the-loop oversight relies on the agent communicating clearly about what it wants to do and why.  The next activity examines how to make agent outputs structured and machine-readable, so that downstream systems can validate what the agent produces before acting on it.

---
