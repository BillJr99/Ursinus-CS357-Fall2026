<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-critiqueconsensusjudge.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-critiqueconsensusjudge.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Critique, Consensus, and the LLM Judge: One Loop, Three Uses

Every pattern today is the same loop: generate something, evaluate it, decide what to do with the evaluation.  A critic feeds its issues back to the generator (critique and refine).  Several generators produce answers that a vote or a clustering step compares by meaning (debate and stochastic consensus).  An evaluator scores one artifact against a rubric and emits JSON (the LLM as judge).  You leave with two runnable loops, a catalog of the ways each use fails, and the [Multi-Agent Patterns lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate), which is handed out today.

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Generator and critic** | The generator produces a draft or an answer and never sees the criteria; the critic evaluates the draft against an explicit rubric and returns a structured verdict.  One explores, the other judges | The call that drafts a class announcement, and the call that checks it for exactly 3 sentences, a specific date, and no exclamation points |
| **Rubric** | A written list of specific, checkable criteria, with levels described in observable terms.  It replaces "make it better" with tests | `{"verdict": "revise", "issues": ["word count 142 exceeds 100"]}` in Part II; the three-criterion essay rubric in Part IV |
| **Reward hacking** | The generator satisfies the letter of the rubric while violating its intent | "Exactly 3 sentences" met by joining three ideas with semicolons into one unreadable sentence |
| **Independent and correlated errors** | Errors are independent when two agents are unlikely to make the same mistake; correlated when shared training makes them agree on the same wrong answer.  Debate fixes the first kind only | Three agents at temperature 0.9 exploring different paths, versus three agents sharing one misconception |
| **Majority vote and judge agent** | Two ways to decide after a debate: count the most common answer, or have a separate agent read all the reasoning and pick | "10", "15", "10" votes to "10"; a judge prompt that asks which reasoning is most rigorous |
| **Stochastic consensus** | Sample the same question many times at high temperature, group the drafts by meaning with embeddings, and let a low-temperature synthesizer write the majority position while disclosing close splits | Five salsa recipes that cluster into three positions with support 3, 2, 1 |
| **Position and verbosity bias** | Two systematic errors of an LLM judge: rating the first answer in an A/B comparison higher regardless of quality, and rating longer answers higher even when the extra length adds nothing | The judge flips its answer when you swap two essays; two empty filler sentences raise an essay's score |
| **Calibration set** | A small set of artifacts already scored by humans, used to check whether the judge agrees with people before you trust it on new work | Ten essays scored by your team and by the judge; a consistent gap on one criterion means that descriptor needs work |

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Part I, one loop, and why the evaluator is a separate call (Model 1) |
| 10-30 | Part II, the critic: the forty-line loop, Model 2, and three failure modes |
| 30-50 | Part III, several generators: the debate loop, Model 4, and voting on meaning (Model 5) |
| 50-65 | Part IV, the judge: Model 6 and auditing the judge |
| 65-70 | Part V, the lab handout and the reflection prompt.  The Human-in-the-Loop Extension is self-paced |
| 70-75 | Report out: one place each use of the loop earned its cost, and one place it did not |

---
# Part I: One Loop

## 1.  Generate, Evaluate, Decide

The loop has three steps, and each of today's patterns is a choice of who fills each step.

| Step | Critique and refine | Debate and consensus | LLM as judge |
|---|---|---|---|
| Generate | One generator drafts | Several generators answer, or one generator is sampled several times | Someone else already produced the artifact |
| Evaluate | A critic checks the draft against a rubric | Agents read each other's answers, or an embedding step groups the answers by meaning | A judge scores the artifact against a rubric |
| Decide | Revise with the issues list, accept, or stop at the budget | Majority vote, a judge agent, or a synthesizer that follows the largest cluster | Emit JSON scores, then a human audits them |

Two rules hold in every column.  First, the evaluate step must add something the generate step did not have: a rubric the generator never saw, a second sample that failed differently, or a level descriptor with quoted evidence.  An extra round that adds no new information adds only cost.  Second, the decide step needs a stopping rule written in your code.  The model will not stop on its own, and the loop that runs "until it is good" runs forever.

## 2.  Why the Evaluator Is a Separate Call

Think about the best feedback you ever received on a piece of writing.  It probably did not come from the person who wrote it.  It came from someone reading it fresh, applying standards you had already agreed on.  A writer who evaluates their own draft in the same sitting tends to approve it, because they remember what they meant to say.  A model asked to "write it and make sure it's good" has the same problem: one context is doing two jobs that need different stances.  Generation explores.  Evaluation judges against criteria.  When one context does both at once, neither gets the model's full attention.

Separating the roles also lets you give the critic something the generator should not have: a rubric.  The critic needs criteria, not vibes.  "Make it better" produces drift; "Check: (1) under 100 words, (2) cites a source for each claim, (3) reading level appropriate for first-years" produces convergence.  The critic returns structured output so the generator knows exactly what to fix:

```json
{"verdict": "revise", "issues": ["word count is 142, must be under 100", "claim 2 has no citation"]}
```

Stopping rules prevent infinite polishing.  Loop until the verdict is `accept`, with a maximum number of rounds.  When the budget runs out, return the best draft with the outstanding critique attached: disclosure of known defects, not silent confidence.

*Why Different Answers Every Time?* introduced reasoning models, which deliberate inside the model in one long response.  Today's loop deliberates outside the model, in code you wrote: the stopping rule is yours, the rubric is a string you can read, every draft and issue list is an object you can log, and you can swap the critic for a different model, a test suite, or a person.  When a reasoning model's answer is wrong, you have a trace and a shrug; when this loop's answer is wrong, you have the exact rubric line that failed to catch it, and you can fix that line.

The point that survives both: an extra round only helps if it introduces something the previous round did not have.  Here that is the critic's rubric, which the generator never sees and therefore cannot simply agree with.  A loop that feeds a draft back with "make it better" adds rounds and no evidence, and you will watch that fail in Model 1.

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

---

# Part II: Use One, a Critic That Feeds Issues Back

Read the full working loop, run it, and connect it back to Part I.  Then study the three ways the loop fails, because the Multi-Agent Patterns lab asks you to measure each one; the specification for that part of the lab lives at [Part A: Critique and Refine](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/CritiqueRefine).

## 3.  The Loop in Forty Lines

The code below is the entire critique-refine loop.  Three design decisions implement Part I directly: (1) the generator and critic are separate `llm` calls with different system prompts, (2) the critic receives the RUBRIC but the generator does not, since the generator sees only the issues list from the critic's output, and (3) the loop has a hard maximum of `rounds` iterations so it cannot run forever.  The temperatures encode a choice: the generator runs warm (0.8 to explore the first draft, then 0.3 for disciplined revision) and the critic runs cold (0.0 for deterministic evaluation).

Run it locally with `ollama run llama3.2` in one terminal and the script in another:

```bash
ollama run llama3.2
python critique_refine.py
```

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

## Model 2: Instrumenting the Loop

### Critical Thinking Questions

4.  The code runs the generator warm (temperature 0.8 for the first draft, then 0.3 for revisions) and the critic cold (temperature 0.0).  Justify each specific choice: what would go wrong if the critic ran at 0.8?  What would go wrong if the first draft ran at 0.0?

   > *Hint: A critic at 0.8 might flag different issues each time it evaluates the same unchanged draft; what would that do to the convergence of the loop?  A generator at 0.0 produces the same draft every time; if the first draft fails, what happens when you try to revise it?*

5.  The fallback when the critic emits invalid JSON is to demand revision (failing *closed*).  The alternative is to assume the draft is acceptable (failing *open*).  Argue which default is correct for (a) a class announcement and (b) a medical summary, explaining what goes wrong in each case if you choose the wrong default.

   > *Hint: Failing closed means "when uncertain, reject and retry."  Failing open means "when uncertain, pass."  For a class announcement, what is the cost of a false rejection?  For a medical summary, what is the cost of a false approval?*

6.  Before you run it, predict the rounds-to-accept for the announcement task in the code.  Then run the loop three times on the same task and record the rounds-to-accept for each run.  Is the variance coming from the generator (different drafts), the critic (different verdicts on the same draft), or both?  Design a one-variable experiment (changing exactly one thing) that would let you tell which source of variance is larger.

   > *Hint: To isolate generator variance, fix the seed of the critic and vary the generator's seed.  To isolate critic variance, fix the draft (use the same input every time) and run the critic multiple times.  Which experiment is easier to set up with the code above?*

> **Common Misconception:** More revision rounds do not always produce better output.  After the loop converges (all criteria met), additional rounds do nothing useful.  If the loop oscillates, more rounds only waste time and tokens.  Set the round budget from measurement: run the loop on 20 representative tasks, plot rounds-to-accept, and set your budget at the 90th percentile.  Setting it at 10 "to be safe" often means 9 wasted rounds on tasks that converge in 1.

The principal reason the critic receives a rubric while the generator does not is:

[( )] Rubrics are too long for the generator's context
[(X)] Separating exploration from criterion-checking gives each small, focused context one job, improving both
[( )] The generator cannot read JSON
[( )] Critics require higher temperature than generators

## 4.  Three Ways the Critic Loop Fails

Each failure has a measurable signature, and you detect it by instrumenting the loop rather than only checking the final output.  Build the measurement into your lab code from the start instead of discovering the failure at submission time.

**Rubber-stamping.**  The critic accepts everything, often because the criteria are vague, because the critic sees the generator's reasoning and is anchored by it, or because the model is trained to be agreeable.  Detect it by measuring the acceptance rate on deliberately flawed drafts: if the critic accepts a draft with a known planted defect, it is rubber-stamping.

**Oscillation.**  Fixing issue 1 reintroduces issue 2, and the loop cycles without net progress.  Detect it by tracking the set of issues across rounds: if the same issue appears in round 1, disappears in round 2, and reappears in round 3, you have oscillation.

**Reward hacking.**  The generator satisfies the letter of the rubric while betraying its intent.  Example: "exactly 3 sentences" achieved by connecting three ideas with semicolons into one grammatical but unreadable run-on.  Detect it with a human spot-audit of accepted outputs: look for drafts that passed every criterion but that a person would rate as poor.

Each failure has a measurement:

- Rubber-stamping: acceptance rate on known-flawed drafts (should be 0%; a high rate is failure)
- Oscillation: issue-recurrence rate across rounds (should fall every round; non-monotone is failure)
- Reward hacking: human quality rating of accepted drafts versus rubric-passing rate (a gap is failure)

---

# Part III: Use Two, Several Generators Compared by Meaning

## 5.  Independent Errors and Structured Conflict

A second opinion helps most when the second person reasoned independently: the same answer by a different route raises your confidence, and a different answer is information.  Debate formalizes this.  Agents answer independently, then critique each other's reasoning, so flaws surface that no single agent would catch alone.  If all agents read each other before forming an answer, the diversity that makes debate valuable disappears.

Why should two copies of the same model disagree usefully?  Sampling.  At nonzero temperature, independent runs explore different reasoning paths, and their errors are partially independent even though their training is identical.  Debate adds structure to that diversity: each agent must see the others' answers and either rebut or concede with reasons, forcing errors into the open where they can be attacked.

The canonical protocol (Du et al., 2023): in round 1, every agent answers independently; in each later round, every agent receives the others' latest answers and revises; after the last round, aggregate by majority vote or by a judge agent.  Variants assign adversarial roles (advocate versus skeptic), which helps on decisions with stakes on both sides.

Honesty about costs.  Debate multiplies inference cost by roughly the number of agents times the number of rounds; a 3-agent, 2-round debate makes about 6 times as many calls as a single-shot answer.  And debate can converge on a confidently shared mistake if the agents' errors correlate: all three agree on the wrong answer, and the vote reports it with false confidence.  Debate is a tool for questions where verification is easier than generation, not a universal accuracy upgrade.  Today we measure its benefit rather than assume it.

## Model 3: Where Debate Pays

| Question | Best Approach and Why |
|----------|-----------------------|
| "What is 847 times 36?" | ? |
| "Should our club hold its fundraiser in October or February?" | ? |
| "What is the capital of Australia?" | ? |
| "Does this Python function handle the empty-list case?" | ? |

### Critical Thinking Questions

7.  For each row in the table, decide whether debate, a single tool call (like a calculator or a lookup), or a single model call is the most appropriate instrument, and write a one-clause justification for each choice.

   > *Hint: Debate adds value when there is real ambiguity and independent reasoning can catch errors.  A tool call is better when there is a ground truth that can be computed or retrieved exactly.  A single model call is fine when the task is simple and errors are unlikely.  Which category does each question fall into?*

8.  The fundraiser question has no ground truth; there is no objectively correct month.  What does "debate improved the answer" even mean in that case?  Propose a measurable proxy for "improvement" that does not require a ground truth.

   > *Hint: Even without a correct answer, you can measure whether the debate surfaced more relevant considerations (count distinct factors raised), whether the final recommendation was better justified (count supporting reasons), or whether participants were more confident in the final answer.  Pick one and explain how you would measure it.*

9.  When agents share training data and similar biases, which kinds of errors will *correlate* across agents and therefore survive debate?  Give one concrete example of a question where debate would confidently produce the wrong answer.

   > *Hint: Think about what all LLMs trained on similar internet text might systematically misrepresent or underrepresent.  A question whose correct answer contradicts common misconceptions in that training data is a candidate for a correlated error.  Can you name one?*

### Debate Is Not the Same Thing a Reasoning Model Does

It is easy to hear "the model thinks before it answers" and conclude that debate is the same idea with extra steps.  It is not, and the difference is the thing this part is about.

| | Reasoning model | Multi-agent debate |
|---|---|---|
| Where deliberation happens | Inside one context, one response | Across several contexts that started separately |
| What it buys | More *dependent* steps: step B can use step A's result | More *independent* errors: two wrong answers that are wrong differently |
| What it cannot fix | A misconception held throughout that one pass | A misconception all the agents share |
| Cost shape | One call, a long one | Agents times rounds calls |

The row that matters is the second.  A reasoning model lifts the cap on how many steps depend on each other, which is why it helps on problems that need a chain of inference.  It does nothing about correlated error: a model reasoning at length from a wrong premise reaches a wrong conclusion carefully.  Debate attacks the other axis.  Its whole premise is that two runs fail differently, so one can catch the other.  They compose: nothing stops you running a debate among three reasoning models, and you would then be buying both properties at both costs.  What you cannot do is substitute one for the other and expect the same protection.

#### Critical Thinking Questions

10.  Your team runs a 3-agent debate and all three agents are reasoning models.  All three produce long, internally consistent reasoning and converge on the same wrong answer.  Which of debate's two assumptions failed, and would swapping in three *different* models have helped?

    > *Hint: The independence assumption failed, not the deliberation one; every agent reasoned carefully and correlated anyway, because they share training data and inductive biases.  Different model families genuinely decorrelate errors more than different samples from one model, so it would likely help, and it is not a guarantee: models trained on overlapping web data can share the same misconception.  The honest move is to measure disagreement rate rather than assume it.*

## 6.  Three Agents, Two Rounds, One Vote

The code below runs the full Du et al. (2023) protocol (independent answers, then peer review, then a vote) in about 30 lines.  The most important design choice is the temperature schedule: round 1 uses temperature 0.9 (high diversity, because we want agents to explore different reasoning paths) and round 2 uses 0.5 (lower, because agents are now refining rather than exploring).  The seed is intentionally absent, so each agent's round 1 run is random and independent.  That is the opposite of our usual practice of seeding for reproducibility, and it is deliberate: without diversity in round 1, there is nothing to debate in round 2.

Run this locally with:

```bash
ollama run llama3.2
python debate.py
```

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import requests
from collections import Counter

def llm(system, user, temperature=0.9):
    """
    Call the local LLM. Note: no seed is set here.
    This is intentional; we want genuine randomness for debate diversity.
    The caller controls temperature per round.
    """
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": temperature},   # deliberately unseeded for diversity
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[debate:llm] {e}")
        import traceback; traceback.print_exc()
        return ""

def debate(question, n_agents=3, rounds=2):
    """
    Run the Du et al. (2023) debate protocol.
    Returns: (list of final answers, (winning answer, vote count))
    """
    # Round 1: all agents answer independently, no communication yet
    # "ANSWER: <short answer>" at the end makes extraction consistent
    sys = "Solve the problem step by step. End your response with a line 'ANSWER: <your short answer>'."
    answers = [llm(sys, question, temperature=0.9) for _ in range(n_agents)]
    print("--- Round 1 answers ---")
    for i, a in enumerate(answers):
        print(f"Agent {i}: {a.split('ANSWER:')[-1].strip()}")

    # Rounds 2+: each agent reads the others' answers and revises
    for rnd in range(1, rounds):
        new_answers = []
        for i in range(n_agents):
            # Build the peer context: what everyone else said
            peers = "\n\n".join(
                f"Agent {j} answered:\n{a}"
                for j, a in enumerate(answers) if j != i
            )
            prompt = (
                f"Original question: {question}\n\n"
                f"The other agents gave these answers:\n{peers}\n\n"
                "Read their reasoning carefully. If you see an error in their reasoning, "
                "point it out specifically. Then give your final answer. "
                "End with 'ANSWER: <your short answer>'."
            )
            # Lower temperature in revision rounds: more focused, less exploratory
            new_answers.append(llm(sys, prompt, temperature=0.5))
        answers = new_answers
        print(f"\n--- Round {rnd + 1} answers ---")
        for i, a in enumerate(answers):
            print(f"Agent {i}: {a.split('ANSWER:')[-1].strip()}")

    # Extract the final short answers and vote
    finals = [a.split("ANSWER:")[-1].strip().lower() for a in answers]
    vote = Counter(finals).most_common(1)[0]   # (answer_text, vote_count)
    return finals, vote

# The classic algebra trap: the intuitive answer (15) is wrong; the correct answer is 10.
# A backpack costs $10 more than a water bottle; together they cost $30.
# If water bottle = x, then (x + 10) + x = 30, so 2x = 20, so x = 10.
question = (
    "A backpack costs 10 dollars more than a water bottle. "
    "Together they cost 30 dollars. What does the water bottle cost?"
)
finals, (winner, count) = debate(question, n_agents=3, rounds=2)
print(f"\n=== Majority vote: '{winner}' with {count}/{len(finals)} agents agreeing ===")
print("Correct answer: 10 dollars")
```

## Model 4: Autopsy of a Debate

Before you run the debate, predict what round 1 will produce: how many of the three agents will say 15?  Then run it.  The correct answer is **10 dollars** (if the water bottle costs $x$ and the backpack costs $x + 10$, then $x + (x+10) = 30$, giving $x = 10$).  The common wrong answer is **15 dollars**, from the intuition "they cost 30 together and differ by 10, so each is 15," which ignores the 10-dollar difference.

### Critical Thinking Questions

11.  Did any round 1 agent fall for the intuitive-but-wrong answer of 15 dollars?  Did exposure to the other agents' reasoning in round 2 repair the error (converging toward 10) or spread the error (pulling correct agents toward 15)?  Quote the decisive sentence from the transcript that shows which happened.

   > *Hint: Look at round 2 transcripts for any agent that changed its answer.  Did the agent that changed provide a clear reason for the change?  Is "the other agents said 10 so I will too" a good reason?  What distinguishes persuasion by evidence from persuasion by social pressure?*

12.  Round 1 uses temperature 0.9 and round 2 uses temperature 0.5.  Explain this scheduling as an "explore then commit" strategy: what does each temperature level accomplish, and what would go wrong at temperature 0.0 everywhere?

   > *Hint: At 0.0, every independent agent produces the same answer (the model's mode).  If that mode answer is wrong, all agents start with the same wrong answer and there is nothing to debate.  What is the minimum diversity you need in round 1 for debate to be possible?*

13.  Majority vote treats all agents as equal regardless of the quality of their reasoning.  Sketch the judge-agent alternative: write out the system prompt the judge would use, and explain which role from Part II a judge agent most resembles.

   > *Hint: The judge reads everyone's reasoning, not only their final answers.  A judge that can explain why it chose one answer over another is more useful than a vote counter.  Which role from the critique-and-refine loop does this most closely resemble?*

> **Common Misconception:** More agents and more rounds do not always produce more accurate results.  They do only if (a) the agents' errors are independent and (b) the question has a verifiable ground truth that correct reasoning can converge toward.  For questions with correlated errors (all agents share the same bias) or no ground truth (matters of opinion), more debate may only produce more confident wrong answers.  Du et al. (2023) report accuracy gains on specific benchmark tasks; those gains do not automatically transfer to every question type.  Always measure.

Multi-agent debate most reliably improves accuracy when:

[( )] All agents run at temperature 0 for consistency
[( )] The question requires recalling one rare fact
[(X)] Errors across agents are partially independent and flaws in a wrong answer are easier to verify than to avoid
[( )] The agents share a single context window

## 7.  Voting on Meaning Instead of Strings

The debate's vote works because `Counter(finals)` can compare short answers as strings.  When answers are paragraphs, string voting collapses: "simmer the tomatillos" and "boil them briefly" should count together, and a string comparison says they are unrelated.  Stochastic consensus is the same generate-evaluate-decide loop with the evaluate step done on meaning.

A language model at high temperature is a sampler, not an oracle.  Ask it the same question six times and you get six different drafts drawn from a distribution of plausible answers.  Any one draft might be idiosyncratic or wrong.  But if you group the drafts by meaning (not by exact wording), the sizes of the groups tell you something no single draft can: which positions the model keeps returning to (high support) and which are one-off flukes (low support).

The grouping step is where embeddings come in.  An embedding model maps each draft to a vector such that drafts with similar meaning land close together, even when they share few words.  Normalize those vectors, cluster them by cosine distance, and "six drafts" becomes "three positions, with support counts of 3, 2, and 1."  A final low-temperature synthesizer then receives one representative draft per cluster (plus its support count), never all six raw transcripts, and writes a single answer that follows the majority and discloses any close disagreement instead of papering over it.  That disclosure rule is the pattern's honesty mechanism: when the samples split, the user deserves to know.

```
question --> sample k drafts at high temperature      (k model calls)
                    |
                    v
             embed each draft --> normalize vectors
                    |
                    v
             cluster by cosine distance (threshold)
                    |
                    v
      one representative per cluster + support count
                    |
                    v
             synthesizer at low temperature            (1 model call)
                    |
                    v
   single answer, majority-following, close-disagreement disclosed
```

There are three ways to aggregate the samples, and they are not interchangeable.  Self-consistency votes on the answer: extract each final answer and return the most common one, which is what the debate code does and which works when answers are short and checkable.  Clustered consensus votes on the meaning: embed the drafts, cluster by cosine similarity, and treat the largest cluster as the consensus position.  Synthesis writes the merged view: a synthesizer receives the cluster representatives with their support counts and drafts one output that keeps majority positions and names real disagreements.  Its context stays small on purpose.  The two dials you will turn in the lab are the sampling temperature (how diverse the drafts are) and the distance threshold (how aggressively meanings are merged).

## Model 5: Five Recipes, Three Positions

Five agents at temperature 1.0 propose tomatillo salsa recipes.  Three roast the tomatillos, one boils them, one uses them raw; four include cilantro; opinions split on jalapeño versus serrano.  Work the three questions below out on paper before you build anything in the lab, because they are the design decisions the code will otherwise make for you.

| Agent | Cooking technique | Chile | Key aromatics | Cluster |
|---|---|---|---|---|
| Agent 1 | Roasts under broiler until charred | Jalapeño | Cilantro, white onion, garlic | A |
| Agent 2 | Roasts in dry skillet | Serrano | Cilantro, white onion | A |
| Agent 3 | Roasts on open flame | Jalapeño | Cilantro, garlic, lime | A |
| Agent 4 | Boils for 10 minutes | Jalapeño | Cilantro, cumin | B |
| Agent 5 | Uses raw, no heat | Serrano | Cilantro, avocado, lime | C |

### Critical Thinking Questions

14.  Which choice here is *load-bearing* (it fundamentally changes the dish) and which is garnish-level?  If you swapped jalapeño for serrano, would the dish taste radically different?  What if you swapped raw for roasted?  Your answer tells you what the clustering has to be sensitive to, and where embeddings are likely to mislead you.

15.  Write, in two sentences, the synthesis you would want.  It should commit where the majority is strong (3 of 5 roast) and stay candid where it is split (the chile).  That is the behavior your synthesizer prompt has to produce.

16.  State precisely why exact-match voting on the full recipe texts yields five singleton answers.  The distinction you need is *string* identity versus *semantic* identity.

Independence is the load-bearing assumption here too.  Sampling helps only when the errors scatter.  If all the drafts share a systematic bias, whether a misconception baked into the model or a misleading phrase in your own prompt, they will agree confidently and be wrong together, and a large cluster will look exactly like a strong consensus.  The lab's shootout deliberately includes questions with well-known intuitive-but-wrong answers so you can watch this happen.

## 8.  When Agreement Misleads

Debate and consensus both aggregate the model's distribution, so both amplify whatever that distribution over-represents: popular framings, mainstream defaults, training-data majorities.  For factual questions with a checkable answer, that is usually a feature, and it is why the vote in Section 6 works at all.

For questions of taste, values, or contested policy, it is a hazard.  "The average of six samples" can quietly erase a legitimate minority position, and the erasure looks identical to a strong result: a big cluster, a confident synthesis, no visible dissent.  We take this up in *Training Data, Bias, and Explainability*, and it is the reason the [Multi-Agent Patterns lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate) requires your synthesizer to disclose close disagreement in one line rather than resolve it silently.

Sit with the distinction before you move on, because your lab design depends on which side of it your question falls:

- Where would you *want* the majority to win outright, and why is disclosure just noise there?
- Where would a candid "the samples split three to two, and here is the other position" be more useful to your stakeholder than a clean single answer?
- Your project's community partner will ask you a question of one kind or the other.  Which is it, and what does that imply about whether you should be aggregating samples at all?

---

# Part IV: Use Three, an Evaluator That Scores Against a Rubric

The third use turns the loop outward: the artifact already exists (an essay, a plan, a pull request) and the model's only job is to score it against a rubric and emit JSON.  You will take apart a bad rubric, then ask who audits the judge.  The judging pipeline, batch scoring, and bias measurements are the Nov 5 workshop; today is the design work that comes first.

## 9.  Judgment at Scale

Think of academic peer review: a journal sends a paper to three reviewers, each scores it against a list of criteria with written justifications, and the editors synthesize the reviews.  LLM-as-judge is the same process, automated.  The rubric is the reviewer's checklist, the judge's prompt is the call to review, and the JSON output is the review report.  The lesson from peer review carries over: a vague criterion ("is this paper good?") produces reviews that disagree, and a precise one ("does the methodology section specify sample size, exclusion criteria, and statistical tests?") produces reviews that different reviewers agree on.

Human judgment is the gold standard and does not scale.  Grading 200 essays against a rubric takes a person a week; an evaluation harness needs thousands of judgments per experiment.  An LLM judge substitutes a model, prompted with the rubric, the artifact, and a demand for structured output.  Used well, it agrees strongly with human raters on well-specified criteria.  Used carelessly, it imports every bias of the underlying model into your measurements, silently.

The rubric is the contract.  As in our assignment rubrics, each criterion has levels with observable descriptors and a weight, and the total is the weighted sum of the awarded levels.  Observable descriptors ("cites a source for each claim") judge reliably; aesthetic ones ("is insightful") do not, the same lesson Model 1 taught about actionable critique.

The judge has known pathologies, systematic errors it makes consistently rather than randomly.  *Position bias*: in A/B comparisons, judges favor the first-presented response.  *Verbosity bias*: longer answers score higher at equal quality.  *Self-preference*: models rate their own outputs more generously than outputs from other models.  *Leniency drift*: scores compress toward the top of the scale over many judgments, so good and excellent become hard to tell apart.  Every pipeline you build must include countermeasures: randomized order, length-blind criteria, a different judge model than the generator, and anchor examples showing what each level looks like.

## Model 6: Rubric Autopsy

A draft rubric for short essays: (1) "Well written, 40 percent"; (2) "Good use of evidence, 40 percent"; (3) "Proper length, 20 percent."

| Criterion (draft) | Problem with this version | Improved version |
|---|---|---|
| "Well written, 40 percent" | "Well written" is not observable; different judges will disagree on what it means, making scores unreliable. | Split into two observable criteria: "Each sentence expresses exactly one idea (no run-ons)" and "Position is stated in the first paragraph." |
| "Good use of evidence, 40 percent" | "Good use" is a judgment, not a description. Vulnerable to verbosity bias: a judge may reward quantity of citations over quality. | "Every factual claim is followed by a parenthetical source. Sources are cited in the text, not only in a bibliography." |
| "Proper length, 20 percent" | Length is trivially machine-checkable with `len(text.split())`. Sending it to an LLM judge wastes tokens and adds noise. | Replace with a programmatic check: `assert 150 <= word_count <= 300`. Save the LLM for criteria that require reading comprehension. |

### Critical Thinking Questions

17.  Rewrite criterion 1 ("Well written") with four observable levels labeled preemerging, beginning, progressing, and proficient.  What changed about *verifiability*, meaning, could two different people independently arrive at the same level?

   *Hint:* Preemerging might be "no clear thesis statement anywhere in the essay."  Proficient might be "thesis stated in the first sentence of the first paragraph, consistent throughout."  Check each level: could you identify it by reading the first sentence only, without making a judgment call?

18.  Criterion 3 ("Proper length") is the only machine-checkable one; should it be sent to the LLM judge at all?  Propose the cheaper instrument and state the general principle about what belongs in an LLM rubric versus what belongs in a programmatic check.

   *Hint:* One line of Python (`150 <= len(essay.split()) <= 300`) is more reliable, cheaper, and faster than an LLM call.  The general principle: use an LLM only when the criterion requires reading comprehension that a simple rule cannot capture.

19.  Which judge pathology (position bias, verbosity bias, self-preference, or leniency drift) threatens criterion 2 ("Good use of evidence") most, and which countermeasure from Section 9 do you prescribe?

   *Hint:* Criterion 2 asks about citations.  A longer essay has more opportunities to include citations, even superficial ones.  Which pathology does that suggest?  How would you rewrite the descriptor to be length-neutral?

## 10.  Auditing the Judge

A judge is a model, so the loop needs one more evaluate step: someone has to score the judge.  The instrument is a calibration set, a small collection of artifacts already scored by people.  Run the judge on it and compare, criterion by criterion, before trusting it on new work.  Setting the temperature to 0 makes the judge consistent, and consistency is not accuracy: a judge that reliably over-scores verbose essays is worse than a slightly noisy but well-calibrated one, because the bias is systematic and invisible.  The Nov 5 workshop builds the pipeline that runs this audit and measures position bias directly.

The most important safeguard before trusting an LLM judge's scores on real student work is:

[( )] Using the largest available model as the judge, because bigger models are inherently fairer
[( )] Setting temperature to 0, because that eliminates bias by making the model deterministic
[(X)] Validating the judge's scores against human scores on a labeled calibration set before using it on new work
[( )] Asking the judge to be fair in the system prompt, so it knows to ignore its biases

### Judging With a Reasoning Model

Sooner or later someone on your team will propose a reasoning model as the judge, on the theory that a model which deliberates before answering will grade more carefully.  That instinct is half right.  Multi-criterion rubrics are exactly the shape of problem extra dependent steps help with (hold four criteria in mind, check the essay against each, and do not let a strong showing on criterion 1 bleed into criterion 3), and a reasoning model is measurably steadier at that bookkeeping than a single forward pass.  What it does not buy is a justification.  The visible reasoning stream is generated text, produced by the same next-token mechanism as the verdict, and research on chain-of-thought faithfulness finds cases where a model's stated reasoning does not match what drove its answer.

> **Never paste a reasoning trace into a rubric as evidence.**  A judge prompt that demands quoted evidence *from the essay* for every score is doing real work: a quote is checkable against the source, and a trace is not.  A trace saying "the essay lacks a clear thesis" is the judge asserting the score a second time in longer form, not supporting it.  Swapping checkable evidence for persuasive narration is a downgrade that looks like an upgrade.

There is a second-order effect.  A long, fluent, confident trace is more persuasive to *you*, the human auditing the judge.  The pathologies in Section 9 do not disappear when the judge thinks longer; they arrive better argued, and verbosity bias gets worse because the judge now produces verbosity of its own.  So add one audit step whichever judge you use: score the same essays twice, once with the reasoning trace shown to you and once with it hidden, and compare your human agreement numbers.  If your agreement with the judge goes *up* when you can see its reasoning, ask whether the trace helped you evaluate the score or persuaded you to accept it.  Those look identical from the inside, and only the numbers can tell them apart.

#### Critical Thinking Questions

20.  Your judge is a reasoning model.  For one essay it scores criterion 2 at level 3, and its trace argues carefully for level 3 while quoting a sentence that does not appear anywhere in the essay.  Name what went wrong, and say which of your existing checks would have caught it and which would not.

    > *Hint: The judge fabricated a quotation, which the trace's fluency disguises rather than reveals.  The evidence requirement catches it, but only if somebody actually verifies the quote against the source, which is a check no amount of reading the trace performs.  Human agreement scoring would not catch it either, since a human reading a persuasive trace may simply agree.  The cheap fix is mechanical: assert every quoted span appears verbatim in the input, which is a validator rather than a judgment.*

---

# Part V: Synthesis and Practice

The [Multi-Agent Patterns lab](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/MultiAgentDebate) is handed out today.  Its Part A (critique and refine) has its own specification at [Critique and Refine](https://www.billmongan.com/Ursinus-CS357-Fall2026/Assignments/CritiqueRefine); do Part A first, because the debate and consensus parts reuse its scaffolding.  The exercises below are the measurements the lab expects you to be able to make.

## 11.  Exercises

1.  **Debate versus single-shot, with cost accounting.**

   *What to do:* Build a set of 10 arithmetic word problems with known correct answers (vary the difficulty: some single-step, some two-step).  Measure accuracy for three conditions: (a) one agent, one call; (b) three agents, majority vote with no debate round (`rounds=1`); (c) full two-round debate with three agents.  Tabulate the calls per condition (10, 30, and 60 in total), compute accuracy gain per additional call for each step up, and recommend with numbers whether you would ship the debate protocol for this task class.

   *Starter hint:* A single-shot helper is `llm("Answer briefly. End with 'ANSWER: <answer>'.", question, temperature=0.3)` with the same `split("ANSWER:")` extraction the debate code uses.  Accuracy gain per call is (accuracy_B minus accuracy_A) divided by (calls_B minus calls_A).

   *You've succeeded when:* You have a three-row table with total calls, accuracy, and accuracy-per-call, and you can say whether any gain came from more agents in the vote pool (diversity) or from the revision round (deliberation).

2.  **Correlated failure hunt: what debate cannot fix.**

   *What to do:* Design a question where you predict all three agents will agree on the same wrong answer, because the correct answer contradicts a widespread misconception in training data.  Run the debate and verify.  Explain, using correlated errors from Section 5, why the debate could not help.  Then name the non-LLM addition (a specific tool call or retrieval source) that would supply the information needed to correct the error.

   *Starter hint:* Candidates: facts that changed recently, statistics that are now outdated, or common wisdom that is scientifically contested.  Pick one you are confident about, state the correct answer and why you expect the agents to miss it, then run the debate.

   *You've succeeded when:* All three agents in round 1 agree on the same wrong answer, and you can name the specific retrieval source (a Wikipedia page, a government database URL) that would supply the correct information as a tool call.

3.  **Reward-hack a rubric, then close the hole.**

   *What to do:* Write an announcement that passes all three criteria in the critique code (exactly 3 sentences, a specific date, no exclamation points) while being a bad announcement by any human standard, then add a fourth criterion that catches it.  Do the same to the essay rubric in Model 6: write the essay that satisfies the letter of every descriptor while being as weak as possible, and name the word in the descriptor that permitted the exploit.

   *You've succeeded when:* You can show the hacked draft, the criterion that catches it, and a one-sentence patch to the essay descriptor that would have caught your essay.

## Reflection Prompt

*Personal:* Think of the best piece of feedback you ever received on your own work.  Did it resemble Transcript A (vague, general) or Transcript B (specific, criterion-based)?  What rubric was your reviewer implicitly using?  Would you hand that rubric to an AI critic or an AI judge reviewing your work today, and what would you need to add to make it machine-usable?

*Technical:* Today's loop decides three ways: a critic's verdict, a majority vote, and a judge's score.  Design a hybrid for the debate: use majority vote as the primary signal, escalate to a judge agent only when the vote is not unanimous, and require the judge to quote evidence from the transcripts for its choice.  Write the decision logic in pseudocode, and state which pathology from Section 9 the evidence requirement is there to catch.

*Societal:* Multi-agent debate has been proposed as a safety mechanism (one model checks another), and LLM judges are already used in hiring, admissions, and formative feedback on student drafts.  Based on what you learned about correlated errors and judge pathologies, what is the fundamental limitation of using AI models to check other AI models trained on the same data, and who should be responsible for running the calibration audit before such a system touches a person's outcome?

---

-> Coming Up Next: Every agent today talked through a shared transcript in one Python process, which works for three agents and two rounds and stops working the moment agents live on different machines.  Next session, *Agents That Talk: Multi-Agent Communication Through GitHub and Dropbox, and Threat Modeling* (Tue Nov 3), moves the conversation into repositories and shared folders, and asks what an attacker can do with a channel that agents trust.  The loop you built today is the core of the Multi-Agent Patterns lab; the judge you designed returns as code in the Nov 5 workshop.

---

## Further Reading

- Madaan et al. "Self-Refine: Iterative Refinement with Self-Feedback."  *NeurIPS* (2023).
- Bai et al. "Constitutional AI: Harmlessness from AI Feedback."  (2022).  Critique against explicit principles at training scale.
- Anthropic engineering blog.  "Building Effective Agents" (2024), evaluator-optimizer pattern.
- Du et al. "Improving Factuality and Reasoning in Language Models through Multiagent Debate."  (2023).
- Irving, Christiano, and Amodei.  "AI Safety via Debate."  (2018).  Debate as an oversight mechanism.
- Liang et al. "Encouraging Divergent Thinking in LLMs through Multi-Agent Debate."  (2023).
- Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena."  *NeurIPS* (2023).  Pathologies and agreement rates.
- Hashemi et al. "LLM-Rubric: A Multidimensional, Calibrated Approach to Automated Evaluation."  *ACL* (2024).

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

In **asynchronous HITL**, the agent saves a complete state snapshot before raising `EscalationPending`.  The human reviews the checkpoint (potentially hours later) approves, rejects, or modifies the action, and the agent reloads the snapshot and continues.  The human's response must be cryptographically tied to the specific checkpoint (not merely "approve the last thing") to prevent replay attacks where an old approval is reused for a new action.

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

   *You've succeeded when* your trigger list covers all five of the actions above, has specific thresholds (not merely "if it seems dangerous"), and includes an explicit cost-benefit statement for each trigger's false-positive rate.

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

---
