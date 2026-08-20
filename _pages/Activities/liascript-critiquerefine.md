<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-critiquerefine.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-critiquerefine.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Critique and Refine Pattern

The *Orchestration Patterns: Pipelines, Routers, and Planners* activity wired agents into pipelines; today we study the most important two-agent pipeline of all. Writers improve through revision, and so do agents: a **generator** produces a draft, a **critic** evaluates it against explicit criteria, and the generator **refines** using the critique, looping until the critic approves or a budget expires. This is the workhorse pattern of Critique and Refine. We move from **why separation helps $\rightarrow$ the loop and its stopping rules $\rightarrow$ implementation $\rightarrow$ when refinement fails**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Generator** | The agent role responsible for producing the initial draft or creative output. The generator explores possibilities and does not apply the evaluation criteria — that is the critic's job. | The agent with system prompt "You draft short announcements for a college class" that produces the first version of the text. |
| **Critic** | The agent role responsible for evaluating a draft against an explicit rubric and returning a structured verdict. The critic judges; it does not create. | The agent that checks whether an announcement has exactly 3 sentences, mentions a specific date, and contains no exclamation points. |
| **Rubric** | A written list of specific, machine-checkable criteria that the critic uses to evaluate the draft. A rubric replaces vague instructions like "make it better" with concrete, objective tests. | `{"verdict": "revise", "issues": ["word count 142 exceeds 100", "claim 2 has no citation"]}` |
| **Convergence** | The property of the critique-refine loop where each revision brings the draft closer to passing all criteria, so the loop terminates in a reasonable number of rounds. A good rubric with actionable feedback produces convergence; vague feedback produces oscillation. | A loop that starts with 3 issues, then 2 issues, then 0 issues and accepts — that is convergence. |
| **Oscillation** | A failure mode where the loop never converges: fixing one issue reintroduces a previous issue, and the draft bounces back and forth between failing states without making net progress. | Round 1: too long; Round 2: too short but now missing a date; Round 3: has date but too long again. |
| **Reward Hacking** | A failure mode where the generator satisfies the literal text of the rubric criteria while violating their intent — for example, achieving "exactly 3 sentences" by stuffing three ideas into one sentence using semicolons. | A draft that technically has 3 sentences but each sentence is 80 words long and impossible to read. |

---

# Part I: Why a Separate Critic?

In this section you will examine why separating generation from evaluation produces better results than asking one agent to do both. You will analyze two real critique transcripts and practice writing structured, actionable feedback — skills you will need when designing your own critic agents in the Critique and Refine.

## 1. Generation and Evaluation Are Different Jobs

**Why this matters:** Think about the best feedback you have ever received on a piece of writing. It probably did not come from the person who wrote it — it came from someone reading it fresh, applying standards you had already agreed on. When the same person both writes and evaluates in the same sitting, they tend to approve their own work because they remember what they meant to say. The same problem applies to LLMs: a model asked to "write it and make sure it's good" conflates two tasks that need different mental stances. Separating the generator and the critic — giving them different system prompts and different information — forces genuinely independent evaluation.

**Asking one prompt to "write it well" conflates two tasks.** Generation explores; evaluation judges against criteria. When the same context does both simultaneously, neither gets the model's full attention — a small context window argument again. Separating roles also lets us give the critic what the generator should not have: a **rubric**.

**The critic needs criteria, not vibes.** "Make it better" produces drift; "Check: (1) under 100 words, (2) cites a source for each claim, (3) reading level appropriate for first-years" produces convergence. The critic returns structured output so the generator knows exactly what to fix:

```json
{"verdict": "revise", "issues": ["word count is 142, must be under 100", "claim 2 has no citation"]}
```

**Stopping rules prevent infinite polishing.** Loop until `verdict == "accept"`, with a maximum of $R$ rounds. On budget exhaustion, return the best draft *with the outstanding critique attached* — disclosure of known defects rather than silent confidence.

The following equation summarizes this loop compactly: at each round $t$, the critic $C$ evaluates the current draft against the rubric and returns a list of issues, and the generator $G$ produces an improved draft using those issues. The loop runs until the critic accepts or round $R-1$ is reached.

$$
d_{t+1} = G(d_t, C(d_t, \text{rubric})), \quad t = 0, 1, \dots, R-1
$$

Where $d_t$ is the draft at round $t$, $G$ is the generator, and $C$ is the critic applying the rubric.

---

## Model 1: Two Transcripts

**Transcript A:** The critic says "This is pretty good, maybe tighten it up a bit." Five rounds later the draft is oscillating between slightly different versions with no clear improvement direction.

**Transcript B:** The critic says `{"verdict": "revise", "issues": ["word count 142 exceeds limit of 100", "claim 2 ('enrollment increased 15%') has no citation"]}`. One round later the draft passes.

### Critical Thinking Questions

1. Diagnose Transcript A: which specific property of the critique caused oscillation rather than convergence? Name at least two properties that are present in Transcript B's critique and absent in Transcript A's.

   > *Hint: Transcript B tells the generator (a) what criterion was violated and (b) specifically which part of the draft violated it. Transcript A tells the generator neither. Without knowing where a problem is, what can the generator do except guess?*

2. Rewrite a vague critique in Transcript B's structured style for a draft announcement of your choosing. Start by planting at least two specific defects in the draft, then write the JSON critique that identifies them precisely. What makes a critique *actionable*: reference to criteria, location of the defect, or both?

   > *Hint: "The draft is too long" is a criterion reference. "Sentence 3 adds 40 words that repeat what sentence 1 already said" is both a criterion reference and a location. Which one gives the generator enough information to make the right change?*

3. The critic in Transcript B never suggests specific wording for the fix. Should critics propose fixes or only identify defects? Take a clear position and note one risk of each policy.

   > *Hint: If the critic suggests specific wording, is it acting as a generator now? What happens to the separation of roles? On the other hand, if the critic only says "sentence 2 is unclear," can the generator always figure out how to fix it?*

With the design principles from Part I in hand, Part II shows the complete implementation of the critique-refine loop so you can see exactly how those principles translate to code.

---

# Part II: Implementation

In this section you will read the full working implementation of the critique-refine loop and answer questions that connect the code back to the design principles from Part I. Pay close attention to the temperature settings and the separation of what the generator and critic each receive.

## 2. The Loop in Forty Lines

**Why this matters:** The code below implements the entire critique-refine loop. Notice three design decisions that directly implement the principles from Part I: (1) the generator and critic are separate `llm` calls with different system prompts, (2) the critic receives the RUBRIC but the generator does not — the generator only receives the issues list from the critic's output, and (3) the loop has a hard maximum of `rounds` iterations so it cannot run forever. The temperature settings encode a meaningful choice: the generator runs warm (temperature 0.8 for exploration, then 0.3 for disciplined revision), while the critic runs cold (0.0 for deterministic evaluation).

You can run this locally with `ollama run llama3.2` in one terminal and then run the script in another:

```bash
ollama run llama3.2
python critique_refine.py
```

---

## Code Cell

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

# The RUBRIC is the critic's instructions — specific, checkable criteria.
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
        return {"verdict": "revise", "issues": ["critic output was not valid JSON — treating as revise"]}

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

        # Pass only the issues list to the generator — not the rubric itself
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

4. The code runs the generator warm (temperature 0.8 for the first draft, then 0.3 for revisions) and the critic cold (temperature 0.0). Justify each specific choice: what would go wrong if the critic ran at 0.8? What would go wrong if the first draft ran at 0.0?

   > *Hint: A critic at 0.8 might flag different issues each time it evaluates the same unchanged draft — what would that do to the convergence of the loop? A generator at 0.0 produces the same draft every time — if the first draft fails, what happens when you try to revise it?*

5. The fallback when the critic emits invalid JSON is to demand revision (failing *closed*). The alternative is to assume the draft is acceptable (failing *open*). Argue which default is correct for (a) a class announcement and (b) a medical summary, explaining what goes wrong in each case if you choose the wrong default.

   > *Hint: Failing closed means "when uncertain, reject and retry." Failing open means "when uncertain, pass." For a class announcement, what is the cost of a false rejection? For a medical summary, what is the cost of a false approval?*

6. Run the loop three times on the same task and record the rounds-to-accept for each run. Is the variance coming from the generator (different drafts), the critic (different verdicts on the same draft), or both? Design a one-variable experiment — changing exactly one thing — that would let you tell which source of variance is larger.

   > *Hint: To isolate generator variance, fix the seed of the critic and vary the generator's seed. To isolate critic variance, fix the draft (use the same input every time) and run the critic multiple times. Which experiment is easier to set up with the code above?*

> **⚠️ Common Misconception:** Students often assume that more revision rounds always produce better output. This is not true. After the loop converges (all criteria met), additional rounds do nothing useful. And if the loop oscillates, more rounds only waste time and tokens without improving the draft. The number of rounds to budget should be set based on empirical measurement — run the loop on 20 representative tasks, plot rounds-to-accept, and set your budget at the 90th percentile. Setting it at 10 "to be safe" often means 9 wasted rounds on tasks that converge in 1.

Now that you can read and run the loop, Part III examines the three ways it commonly fails — so you can detect and fix these problems in your own Critique and Refine implementation.

The principal reason the critic receives a rubric while the generator does not is:

[( )] Rubrics are too long for the generator's context
[(X)] Separating exploration from criterion-checking gives each small, focused context one job, improving both
[( )] The generator cannot read JSON
[( )] Critics require higher temperature than generators

---

# Part III: When Refinement Fails

In this section you will study three failure modes that can make the critique-refine loop produce worse results than a single-shot approach. Knowing these failure signatures — and how to measure them — is what separates a loop that works in a demo from one that works reliably in production.

## 3. Failure Modes to Hunt in Critique and Refine

**Why this matters:** Understanding how the critique-refine loop fails is as important as knowing how it works. Each of the three failure modes below has a measurable signature — you can detect them by instrumenting the loop rather than only checking the final output. Building this measurement into Critique and Refine from the start (rather than discovering failures at submission time) is the application of the design-first principle from the earlier activity.

**Rubber-stamping:** The critic accepts everything — often because the criteria are vague, because the critic sees the generator's reasoning and is anchored by it, or because the model is trained to be agreeable. You can detect this by measuring the acceptance rate on deliberately flawed drafts: if the critic accepts a draft with a known planted defect, it is rubber-stamping.

**Oscillation:** Fixing issue 1 reintroduces issue 2, and the loop cycles without net progress. You can detect this by tracking the set of issues across rounds — if the same issue appears in round 1, disappears in round 2, and reappears in round 3, you have oscillation.

**Reward hacking:** The generator satisfies the letter of the rubric while betraying its intent. Example: "exactly 3 sentences" achieved by connecting three ideas with semicolons into one grammatical but unreadable run-on. You can detect this with a human spot-audit of "accepted" outputs — look specifically for drafts that passed all criteria but that a human would rate as poor quality.

Each failure has a measurement:
- Rubber-stamping → acceptance rate on known-flawed drafts (should be 0%, high rate = failure)
- Oscillation → issue-recurrence rate across rounds (should decrease monotonically, non-monotone = failure)
- Reward hacking → human quality rating of accepted drafts vs. rubric-passing rate (gap = failure)

---

## 4. Exercises

1. **Calibrate the critic.**

   *What to do:* Write five announcements yourself, each with exactly one planted defect that violates one of the three rubric criteria. Feed each to the critic alone (without running the full loop) and record whether it correctly identifies each defect. Report the detection rate per criterion (e.g., "the critic detected the sentence-count violation 4/5 times"). Identify which criterion the critic is weakest on and try rewriting that criterion in the rubric to improve detection.

   *Starter hint:* To test the critic in isolation, call `critique(your_draft)` directly with `draft` set to one of your planted-defect announcements. To test each criterion separately, write one draft that violates only criterion 1, one that violates only criterion 2, and one that violates only criterion 3. This isolates which criterion the critic struggles with.

   *You've succeeded when:* You have a per-criterion detection rate and a revised rubric wording that improves the weakest criterion's detection rate by at least 20 percentage points in a re-run.

2. **Adversarial generator — reward hacking.**

   *What to do:* Try to manually reward-hack your own rubric: write a draft that passes all three criteria checks (exactly 3 sentences, mentions a specific date, no exclamation points) while being a bad announcement by any human standard. Then add a fourth criterion to the rubric that closes the loophole you exploited, and verify that the critic now flags your hacked draft.

   *Starter hint:* Common reward-hacking strategies: (1) meet "exactly 3 sentences" by combining three ideas with semicolons into one long unreadable sentence; (2) meet "mentions a specific date" by burying it in parentheses at the end of an unrelated sentence; (3) replace exclamation points with ALL CAPS for emphasis. After finding your hack, add a criterion like "each sentence must be under 25 words" or "the date must appear in the first sentence."

   *You've succeeded when:* You can show (a) the hacked draft that passes the original 3-criterion rubric, (b) the new criterion that catches it, and (c) a revised draft that passes all 4 criteria and is also a genuinely good announcement.

3. **Convergence plot.**

   *What to do:* Run the full critique-refine loop ten times on different announcement tasks. For each run, record the number of rounds used before acceptance (or the maximum if it never accepted). Plot rounds-to-accept (x-axis: run number, y-axis: rounds used). Propose a budget $R$ that accepts at least 90% of runs. State explicitly what your system does with the remaining 10% (return with outstanding issues, escalate to human, etc.).

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

4. **Self versus other critic comparison.**

   *What to do:* Replace the separate critic call with a single prompt asking the generator to self-critique and revise in one shot (e.g., "Write an announcement, then evaluate it against these criteria, then revise it"). Compare the quality of the final output against the two-agent version on five different tasks. Report: (a) does the self-critique version meet the rubric criteria as often? (b) is the output quality higher or lower by human judgment? (c) how do the token costs compare?

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

**Personal:** Think of the best piece of feedback you ever received on your own work — a paper, a project, a presentation. Did it resemble Transcript A (vague, general) or Transcript B (specific, criterion-based)? What rubric was your reviewer implicitly using? Would you hand that rubric to an AI critic reviewing your work today, and what would you need to add or clarify to make it machine-usable?

**Technical:** The critique-refine pattern adds latency proportional to the number of revision rounds. For a system that serves 1,000 requests per day, each request taking an average of 2 revision rounds at 3 seconds per LLM call, compute the total additional time per day spent on revision versus a zero-round baseline. At what scale does this latency cost justify investing in a better generator (fewer revision rounds needed) rather than a better critic (more accurate first-pass evaluation)?

**Societal:** The critic in today's loop applies a human-written rubric mechanically. In journalism, academic publishing, and legal review, human editors and peer reviewers apply judgment that goes beyond any written rubric — they know context, they catch implications, they apply community standards that are not fully articulable. What kinds of evaluation should not be delegated to an automated critic, even a well-calibrated one? What criteria would you use to decide?

---

→ **Coming Up Next:** The *Multi-Agent Debate* activity extends the critique-refine idea — instead of one critic evaluating one generator's output, multiple agents argue different positions before a judge resolves the disagreement. The generator-critic loop you built today is the heart of the Critique and Refine, *Critique and Refine*.

---

## Further Reading

- Madaan et al. "Self-Refine: Iterative Refinement with Self-Feedback." *NeurIPS* (2023).
- Bai et al. "Constitutional AI: Harmlessness from AI Feedback." (2022). Critique against explicit principles at training scale.
- Anthropic engineering blog. "Building Effective Agents" (2024), evaluator-optimizer pattern.
