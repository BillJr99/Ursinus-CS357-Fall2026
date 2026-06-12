# Orchestration Patterns: Pipelines, Routers, and Planners
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-orchestration.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-orchestration.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Orchestration Patterns: Pipelines, Routers, and Planners

Unit 3 begins: instead of making one agent smarter, we make **several simple agents cooperate**. The enabling insight comes straight from the small context window principle: a model given one narrow job and a tiny prompt outperforms the same model juggling five jobs in a bloated prompt. We move from **why decompose $\rightarrow$ the pipeline $\rightarrow$ the router $\rightarrow$ the planner $\rightarrow$ composing them in code**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Decomposition

## 1. Three Foundational Patterns

**Pipeline (fixed sequence).** Stage outputs feed stage inputs: extract $\rightarrow$ draft $\rightarrow$ polish. Each stage has its own small system prompt and sees *only* what it needs. Pipelines are predictable, debuggable (inspect any intermediate), and cheap, and they are the right default when the workflow is known in advance.

**Router (one decision, then dispatch).** A classifier agent reads the input and forwards it to one of several specialists: billing questions to the billing agent, technical questions to the tech agent. The router's entire context is the input plus the menu of destinations, about as small as a context gets. Reliability comes from constraining its output to a closed set of labels.

**Planner (dynamic decomposition).** When the workflow is *not* known in advance, a planner agent writes a step list, worker agents execute steps, and the planner revises on failures. Planners buy flexibility at the cost of predictability, so we bound them with step budgets, exactly as in week 1.

A useful design heuristic follows: **choose the least dynamic pattern that solves the problem.** Pipelines before routers, routers before planners, planners before free-roaming autonomy.

---

## Model 1: Match the Pattern

| Task | ? |
|------|---|
| Every night, summarize the day's club announcements into one digest email draft | ? |
| Triage incoming help-desk tickets to hardware, software, or accounts queues | ? |
| "Plan my study schedule for finals, adapting if I fall behind" | ? |

### Critical Thinking Questions

1. Assign a pattern to each task and justify each choice using the heuristic above.
2. For the triage task, the router sometimes invents a fourth category. Give two distinct fixes: one in the prompt, one in the surrounding code.
3. For the digest pipeline, name the intermediate artifact between the stages, and explain how inspecting it helps you localize a quality bug, contrasting this with debugging a single mega-prompt.

---

# Part II: A Pipeline and Router in Code

## 2. Small Agents, Explicit Seams

---

## Code Cell

```python
import requests

def llm(system, user, temperature=0.0):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": temperature, "seed": 42},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[orchestration:llm] {e}")
        import traceback; traceback.print_exc()
        return ""

# --- Pipeline: extract -> draft -> polish ---
def digest_pipeline(raw_announcements):
    facts = llm("Extract every event as 'name | date | location', one per line. Output only the lines.",
                raw_announcements)
    draft = llm("Write a friendly 3-sentence digest of these events for students.", facts)
    final = llm("Edit for concision and warmth. Keep under 60 words.", draft)
    return facts, draft, final

raw = ("The chess club meets Thursday at 7 in Olin 107. "
       "Hawk Hacks is Saturday 10am in IDDC. Bring laptops! "
       "Ultimate frisbee pickup moved to Sunday 2pm on the quad.")
facts, draft, final = digest_pipeline(raw)
print("FACTS:\n", facts, "\n\nFINAL:\n", final)

# --- Router: classify, then dispatch ---
SPECIALISTS = {
    "hardware": "You fix physical computer problems. Give 2 concrete steps.",
    "software": "You fix application problems. Give 2 concrete steps.",
    "accounts": "You handle login/password issues. Give 2 concrete steps.",
}

def route(ticket):
    label = llm("Classify the ticket as exactly one word: hardware, software, or accounts. Output only that word.",
                ticket).lower()
    label = label if label in SPECIALISTS else "software"   # guard the closed set
    return label, llm(SPECIALISTS[label], ticket)

for t in ["My laptop screen flickers and goes black.",
          "I cannot log into the campus portal after the password reset."]:
    label, response = route(t)
    print(f"\n[{label}] {t}\n -> {response}")
```

---

## Model 2: Reading the Seams

### Critical Thinking Questions

4. Each `llm` call above has a one-sentence system prompt and sees only its own input. Connect this design directly to the lost-in-the-middle and distraction findings from the memory module.
5. The router guard `label if label in SPECIALISTS else "software"` makes a silent default decision. Argue for or against silence here, and propose what a *louder* failure would look like.
6. The polish stage can introduce errors the extract stage never made. Where would you insert a verification step, and which earlier course tool (harness, judge, citation check) would you reuse?

[[MC]]
According to the design heuristic developed today, a team should reach for a planner agent only when:
- ( ) The task involves more than two steps
- ( ) Maximum autonomy is a project goal
- (x) The sequence of steps cannot be determined before runtime
- ( ) The budget allows a larger model

---

# Part III: Synthesis and Practice

## 3. Exercises

1. *Fourth stage.* Add a fact-check stage to the pipeline that compares the final digest against the extracted facts and flags discrepancies. Demonstrate it catching a seeded error.
2. *Router evaluation.* Build a 12-ticket labeled test set and report your router's classification accuracy with the week 3 harness. Then degrade the router's prompt (remove the closed-set instruction) and re-measure.
3. *Planner sketch.* On paper, design the planner-worker message format (JSON) for the study-schedule task in Model 1, including how a worker reports failure and how the planner revises. Bring it to the next class: critique and refine is tomorrow's topic, and your design will receive exactly that treatment.

---

## Reflection Prompt

In your notebook: decomposition into narrow roles is also how human organizations work, and it produces both efficiency and silos. Describe one place in today's designs where information lost at a seam could cause a poor outcome, and one mechanism (human or technical) that organizations use to repair exactly that loss.

---

## 4. Further Reading

- Anthropic engineering blog. "Building Effective Agents" (2024, online). The workflow patterns formalized today.
- Wu et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." (2023).
- Leon Festinger's classic organizational-communication literature, for the human analogy (optional browse).
