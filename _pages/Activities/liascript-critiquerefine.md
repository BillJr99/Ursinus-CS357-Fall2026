# The Critique and Refine Pattern
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

Writers improve through revision, and so do agents: a **generator** produces a draft, a **critic** evaluates it against explicit criteria, and the generator **refines** using the critique, looping until the critic approves or a budget expires. This is the workhorse pattern of Lab 3. We move from **why separation helps $\rightarrow$ the loop and its stopping rules $\rightarrow$ implementation $\rightarrow$ when refinement fails**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Why a Separate Critic?

## 1. Generation and Evaluation Are Different Jobs

**Asking one prompt to "write it well" conflates two tasks.** Generation explores; evaluation judges against criteria. When the same context does both simultaneously, neither gets the model's full attention, a small context window argument again. Separating roles also lets us give the critic what the generator should not have: a **rubric**.

**The critic needs criteria, not vibes.** "Make it better" produces drift; "Check: (1) under 100 words, (2) cites a source for each claim, (3) reading level appropriate for first-years" produces convergence. The critic returns structured output:

```
{"verdict": "revise" | "accept", "issues": ["...", "..."]}
```

**Stopping rules prevent infinite polishing.** Loop until `verdict == accept`, with a maximum of $R$ rounds; on budget exhaustion, return the best draft *with the outstanding critique attached*, honest disclosure of known defects rather than silent confidence.

$$
d_{t+1} = G(d_t, C(d_t, \text{rubric})), \quad t = 0, 1, \dots, R-1
$$

---

## Model 1: Two Transcripts

Transcript A: critic says "This is pretty good, maybe tighten it." Five rounds later the draft oscillates between versions. Transcript B: critic says "Reject: claim 2 has no citation; word count 142 exceeds 100." One round later the draft passes.

### Critical Thinking Questions

1. Diagnose Transcript A: which property of the critique caused oscillation rather than convergence?
2. Rewrite Transcript A's critique in Transcript B's style for a draft of your choosing. What makes a critique *actionable*: reference to criteria, location of the defect, or both?
3. The critic in B never suggests wording. Should critics propose fixes or only identify defects? Take a position and note one risk of each policy.

---

# Part II: Implementation

## 2. The Loop in Forty Lines

---

## Code Cell

```python
import json
import requests

def llm(system, user, temperature=0.3):
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

RUBRIC = """Evaluate the draft against ALL criteria:
1. Exactly 3 sentences.
2. Mentions a specific date.
3. No exclamation points.
Respond ONLY with JSON: {"verdict": "accept" or "revise", "issues": [list of specific defects]}"""

def critique(draft):
    out = llm(RUBRIC, draft, temperature=0.0)
    try:
        return json.loads(out.replace("```json", "").replace("```", ""))
    except Exception as e:
        print(f"[critique:parse] {e} on: {out[:80]}")
        import traceback; traceback.print_exc()
        return {"verdict": "revise", "issues": ["critic output was not valid JSON"]}

def critique_refine(task, rounds=3):
    draft = llm("You draft short announcements for a college class.", task, temperature=0.8)
    for r in range(rounds):
        verdict = critique(draft)
        print(f"--- round {r}: {verdict['verdict']} | issues: {verdict['issues']}")
        if verdict["verdict"] == "accept":
            return draft, verdict, r
        draft = llm("Revise the draft to fix EXACTLY these issues, changing nothing else.",
                    f"Draft:\n{draft}\n\nIssues:\n{json.dumps(verdict['issues'])}",
                    temperature=0.3)
    return draft, verdict, rounds

final, verdict, used = critique_refine(
    "Announce that Lab 3 is due October 27 and office hours moved to Wednesday.")
print(f"\nFINAL (after {used} revision rounds):\n{final}")
```

---

## Model 2: Instrumenting the Loop

### Critical Thinking Questions

4. We run the generator warm (temperature 0.8 then 0.3) and the critic cold (0.0). Justify each choice using week 3's sampling theory.
5. The fallback when the critic emits invalid JSON is to demand revision. Argue whether failing *closed* (revise) or failing *open* (accept) is the right default for (a) a class announcement and (b) a medical summary.
6. Run the loop three times on the same task and record rounds-to-accept. Is the variance in the generator, the critic, or both? Design a one-variable experiment to tell.

[[MC]]
The principal reason the critic receives a rubric while the generator does not is:
- ( ) Rubrics are too long for the generator's context
- (x) Separating exploration from criterion-checking gives each small, focused context one job, improving both
- ( ) The generator cannot read JSON
- ( ) Critics require higher temperature than generators

---

# Part III: When Refinement Fails

## 3. Failure Modes to Hunt in Lab 3

**Rubber-stamping**: the critic accepts everything (often when criteria are vague or the critic sees the generator's reasoning and is anchored by it). **Oscillation**: fixes for issue 1 reintroduce issue 2. **Reward hacking**: the generator satisfies the letter of the rubric while betraying its intent (three sentences achieved by stuffing one sentence with semicolons). Each failure has a measurement: acceptance rate on deliberately flawed drafts, issue-recurrence across rounds, and human spot-audit of "accepted" outputs.

---

## 4. Exercises

1. *Calibrate the critic.* Feed the critic five drafts you wrote with known, planted defects. Report its detection rate per criterion. Which criterion is it weakest on, and can a rubric rewording fix it?
2. *Adversarial generator.* Try to reward-hack your own rubric: produce a draft that passes all three checks while being a bad announcement. Then add a fourth criterion that closes the loophole.
3. *Convergence plot.* For ten runs, plot rounds-to-accept. Propose a budget $R$ that accepts 90 percent of runs, and state what your system does with the other 10 percent.
4. *Self versus other.* Replace the separate critic call with a single prompt asking the generator to self-critique and revise in one shot. Compare quality on five tasks; report whether separation earned its extra latency.

---

## Reflection Prompt

In your notebook: think of the best piece of feedback you ever received on your own work. Did it resemble Transcript A or Transcript B? What rubric was your reviewer implicitly using, and would you hand that rubric to an AI critic reviewing your drafts?

---

## 5. Further Reading

- Madaan et al. "Self-Refine: Iterative Refinement with Self-Feedback." *NeurIPS* (2023).
- Bai et al. "Constitutional AI: Harmlessness from AI Feedback." (2022). Critique against explicit principles at training scale.
- Anthropic engineering blog. "Building Effective Agents" (2024), evaluator-optimizer pattern.
