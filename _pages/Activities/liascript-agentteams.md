# Agent Teams: Specialists over Monoliths
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-agentteams.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentteams.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Agent Teams: Specialists over Monoliths

Everything in Unit 3 converges here: pipelines, routers, critics, debaters, and synthesizers are *roles*, and an **agent team** is a deliberate composition of roles around a shared task, exactly what your final project will build. The design thesis of this course is that **a team of small, specialized agents with focused contexts beats one monolithic agent with a giant prompt**, and today we argue it, architect with it, and stress-test it. The arc: **the case for specialists $\rightarrow$ team topologies $\rightarrow$ shared state and handoffs $\rightarrow$ designing your project team**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook. Today's final model is project-facing: your project team and your POGIL team may be the same people, by design.

---

# Part I: The Case for Specialists

## 1. Why Small Contexts Win Again

**A monolith carries everything everywhere.** One agent doing research, drafting, fact-checking, and formatting needs all four instruction sets, all intermediate state, and all retrieved evidence in one context: maximal cost (attention is $O(n^2)$), maximal distraction, and instructions stranded mid-context where attention is weakest.

**A team carries only what each role needs.** The researcher sees the question and search results; the writer sees verified facts and a style guide; the checker sees claims and sources; the formatter sees the approved draft. Each context stays small, each system prompt stays unburied, and each role can be **evaluated in isolation** with the week 3 harness, which is the property that makes teams *debuggable*.

**Teams also fail in new ways.** Handoffs lose information; roles deadlock awaiting each other; an upstream error launders itself into downstream confidence. Team design is therefore interface design: what, exactly, crosses each seam.

---

## Model 1: Monolith Versus Team

A student org wants an agent system that turns raw meeting notes into (a) a polished minutes document, (b) an action-item list with owners, and (c) a one-paragraph public summary.

### Critical Thinking Questions

1. Draft the monolithic system prompt (just its section headers). How many distinct jobs is one context holding?
2. Decompose into the smallest sensible team. For each role, specify its *exact* input and output (be format-precise: JSON fields, markdown, or prose).
3. Identify the seam where a hallucinated action item would most plausibly enter, and station one of Unit 3's patterns there as a guard.
4. Which single role would you evaluate *first* if the final summaries are coming out wrong, and what does that choice reveal about why decomposition aids debugging?

---

# Part II: Topology and State

## 2. Team Shapes and the Blackboard

Three topologies cover most systems. **Hierarchical**: a supervisor decomposes, delegates to specialists, and integrates, which is predictable and auditable, at the cost of a supervisor bottleneck. **Peer-to-peer**: specialists hand off directly along a known workflow, which is lean, but implicit. **Blackboard**: all agents read and write a shared, *structured* state object, and act when their preconditions are met.

A minimal blackboard is just a dictionary with discipline:

```
state = {
  "goal":        "...",
  "facts":       [{"claim": "...", "source": "...", "verified": false}],
  "draft":       null,
  "issues":      [],
  "status":      "researching"   # researching -> drafting -> checking -> done
}
```

The `status` field is a tiny state machine; each agent's contract is "when status is X and my inputs exist, produce Y and advance status." The blackboard makes the team's entire cognition *inspectable at every step*, our explainability theme made concrete.

[[MC]]
An agent team keeps stalling: the checker waits for verified facts while the researcher believes its job is done. The most diagnostic artifact to inspect first is:
- ( ) The model weights
- ( ) Each agent's temperature setting
- (x) The shared state object and each role's precondition/postcondition contract
- ( ) The total token count

---

## Code Cell

```python
import requests

def llm(system, user, temperature=0.2):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": temperature, "seed": 42},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[agentteams:llm] {e}")
        import traceback; traceback.print_exc()
        return ""

NOTES = ("Attendance: Sam, Riley, Jo. Budget: 240 dollars left. Riley will book Olin 107 "
         "for Nov 14 by Friday. Bake sale raised 180 dollars. Jo to email the advisor "
         "about van reservations by Monday. Next meeting Nov 5.")

state = {"goal": "produce minutes, action items, and a public summary",
         "notes": NOTES, "actions": None, "minutes": None, "summary": None,
         "status": "extracting"}

def extractor(s):
    s["actions"] = llm("Extract action items as lines 'owner | task | deadline'. Output only the lines.",
                       s["notes"])
    s["status"] = "drafting"

def writer(s):
    s["minutes"] = llm("Write brief formal minutes (under 90 words) from these notes.", s["notes"])
    s["summary"] = llm("Write a one-sentence public summary (no names, no budget figures).", s["notes"])
    s["status"] = "checking"

def checker(s):
    verdict = llm("Do the minutes contradict the notes or the summary leak names/figures? "
                  "Answer 'PASS' or 'FAIL: <reason>'.",
                  f"Notes:\n{s['notes']}\n\nMinutes:\n{s['minutes']}\n\nSummary:\n{s['summary']}")
    s["status"] = "done" if verdict.startswith("PASS") else "drafting"
    return verdict

pipeline = {"extracting": extractor, "drafting": writer}
guard = 0
while state["status"] != "done" and guard < 6:
    if state["status"] in pipeline:
        pipeline[state["status"]](state)
    elif state["status"] == "checking":
        print("checker says:", checker(state))
    guard += 1

print("\nACTIONS:\n", state["actions"])
print("\nMINUTES:\n", state["minutes"])
print("\nSUMMARY:\n", state["summary"])
```

---

## Model 2: Reading the Blackboard

### Critical Thinking Questions

5. Trace one full pass of the `while` loop: which role fired at each `status`, and what did it write? The Recorder draws the state machine.
6. The checker can send `status` back to `drafting`, creating a critique-refine loop *inside* the team. What prevents an infinite loop, and where have you seen that safeguard twice before in this course?
7. Each `llm` call sees only a slice of state. For each role, name one piece of state it deliberately does *not* see, and the failure that omission prevents.

---

# Part III: Design Your Project Team

## 3. Exercises

1. *Team charter, agent edition.* For your final project concept, produce the design table: one row per agent with columns for role, system-prompt summary, inputs, outputs, temperature, tools, and the evaluation you will run on it in isolation. This table is a required artifact of your project proposal.
2. *Topology defense.* State which topology your team uses and write a three-sentence defense referencing at least one failure mode it mitigates and one it accepts.
3. *Seam test.* Pick your riskiest handoff. Write five synthetic inputs for the upstream agent and assert properties of its output format programmatically. Report the pass rate.
4. *Monolith baseline.* Implement your project's core task as a single mega-prompt and keep it: your final report must compare your team against this baseline with the harness. Design the comparison now (task set, metric, protocol).

---

## Reflection Prompt

In your notebook: your POGIL team rotates roles so every human learns every job, yet today you assigned your *agents* permanent specialties. What is different about people and models that justifies the asymmetry, or does it? Would there be value in rotating your agents' roles too?

---

## 4. Further Reading

- Anthropic engineering blog. "Building Effective Agents" (2024) and "How we built our multi-agent research system" (2025, online).
- Wu et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." (2023).
- Hong et al. "MetaGPT: Meta Programming for Multi-Agent Collaborative Frameworks." *ICLR* (2024).
