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

Everything in Unit 3 converges here: the pipelines and routers of *Orchestration Patterns*, the critics of *The Critique and Refine Pattern*, and the debaters of *Multi-Agent Debate* are *roles*, and an **agent team** is a deliberate composition of roles around a shared task — exactly what your final project will build. The design thesis of this course is that **a team of small, specialized agents with focused contexts beats one monolithic agent with a giant prompt**, and today we argue it, architect with it, and stress-test it. The arc: **the case for specialists $\rightarrow$ team topologies $\rightarrow$ shared state and handoffs $\rightarrow$ designing your project team**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook. Today's final model is project-facing: your project team and your POGIL team may be the same people, by design.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Monolith** | A single AI agent given one enormous prompt that asks it to do every job at once, resulting in a long, cluttered context where instructions crowd each other out. | One agent told to "read notes, extract actions, write minutes, write a summary, and verify accuracy" all in one prompt. |
| **Agent team** | A group of AI agents where each agent has a narrow, clearly defined role, a small focused context, and passes structured output to the next agent. | Three agents: Extractor (pulls action items), Writer (formats minutes and summary), Checker (verifies consistency). |
| **Handoff** | The moment when one agent finishes and passes its structured output to the next agent; the format and content of this transfer is the most important design decision in any pipeline. | The Extractor outputs `"Riley | book Olin 107 | Friday"` as a formatted line that the Writer can reliably read. |
| **Blackboard** | A shared dictionary that all agents can read from and write to, recording the current state of the whole task so every agent knows what has happened and what still needs to happen. | `state = {"notes": "...", "actions": None, "minutes": None, "status": "extracting"}` |
| **State machine** | A formal way of tracking which stage a system is in and which transitions are allowed, preventing agents from acting out of turn or skipping steps. | The `status` field advances from `"extracting"` to `"drafting"` to `"checking"` to `"done"` in order. |
| **Context window** | The maximum amount of text a model can read at once; keeping each agent's context small means instructions stay near the top where the model pays most attention. | A checker agent that only sees the notes, the minutes, and the summary — not the full conversation history. |

---

# Part I: The Case for Specialists

In this section you will compare a monolithic agent (one enormous prompt doing everything) against a three-agent team, using a concrete meeting-notes task. You will decompose the task yourself, identify where errors enter, and practice the debugging logic that makes teams more maintainable than monoliths.

## Model 1: Monolith Versus Team

Think of the difference between a general practitioner (GP) and a team of specialists in a hospital. A GP must hold the entire medical textbook in mind for every appointment, and you cannot easily blame one section when something goes wrong. A specialist team — cardiologist, radiologist, pharmacist — each holds deep knowledge in a narrow domain, passes structured findings (lab reports, imaging reads) to the next specialist, and can each be evaluated and replaced independently. Agent teams work the same way. A monolith carries everything everywhere; a team carries only what each role needs. Today we see exactly what that distinction means in code.

**A monolith carries everything everywhere.** One agent doing research, drafting, fact-checking, and formatting needs all four instruction sets, all intermediate state, and all retrieved evidence in one context: maximal cost (attention is $O(n^2)$), maximal distraction, and instructions stranded mid-context where attention is weakest.

**A team carries only what each role needs.** The researcher sees the question and search results; the writer sees verified facts and a style guide; the checker sees claims and sources; the formatter sees the approved draft. Each context stays small, each system prompt stays unburied, and each role can be **evaluated in isolation** with the harness from the *Hallucinations and Evaluating Agent Outputs* activity — which is the property that makes teams *debuggable*.

**Teams also fail in new ways.** Handoffs lose information; roles deadlock awaiting each other; an upstream error launders itself into downstream confidence. Team design is therefore interface design: what, exactly, crosses each seam.

**A concrete 3-agent pipeline for meeting notes:**

| Agent | Role | Input | Output | Temperature |
|---|---|---|---|---|
| **Extractor** | Pulls action items from raw notes into a structured list | Raw meeting notes text | Lines in format `owner \| task \| deadline` | 0.2 (accuracy matters, not creativity) |
| **Writer** | Produces formal minutes and a public-facing summary from verified facts | Raw notes + action item list | Formal minutes (under 90 words) and one-sentence summary with no names or budget figures | 0.3 (light creativity for prose quality) |
| **Checker** | Verifies that minutes do not contradict notes and summary does not leak private information | Notes + minutes + summary | `PASS` or `FAIL: <specific reason>` | 0.0 (deterministic verification) |

A student org wants an agent system that turns raw meeting notes into (a) a polished minutes document, (b) an action-item list with owners, and (c) a one-paragraph public summary.

### Critical Thinking Questions

1. Draft the monolithic system prompt (just its section headers). How many distinct jobs is one context holding, and which job would most likely be performed poorly because the model's attention is diluted?

   > *Hint: Try writing out the headers: "## Your job", "## Action item format", "## Minutes format", "## Summary rules", "## Verification steps". Count the headers and ask yourself which would be forgotten in a long context.*

2. Decompose into the smallest sensible team. For each role, specify its *exact* input and output — be format-precise: JSON fields, markdown, or prose.

   > *Hint: The 3-agent pipeline in the table above is a starting point. Could you break any role down further? Could you merge any two without losing clarity?*

3. Identify the seam where a hallucinated action item would most plausibly enter, and station one of Unit 3's patterns there as a guard.

   > *Hint: A "hallucinated action item" is one the model invented that does not appear in the original notes. Which agent produces action items? What should the Checker do if it detects one?*

4. Which single role would you evaluate *first* if the final summaries are coming out wrong, and what does that choice reveal about why decomposition aids debugging?

   > *Hint: Work backwards from the output. The summary is produced by the Writer. But the Writer depends on the Extractor's action list. If the action list is wrong, the Writer cannot fix it.*

With the roles defined, Part II shows how to organize those roles into a running system — choosing a team topology and managing shared state so every agent knows where the task currently stands.

---

# Part II: Topology and State

In this section you will compare three ways agent teams can be arranged — hierarchical, peer-to-peer, and blackboard — and you will read the working implementation of the meeting-notes team. The questions connect the code's state machine directly to the critique-refine and safety-control patterns you have already studied.

## Model 2: Team Shapes and the Blackboard

Different problems call for different team shapes, just as different organizations structure themselves as flat teams, hierarchies, or project boards. In AI agent systems, there are three main topologies. **Hierarchical**: a supervisor decomposes the task, delegates to specialists, and integrates results — predictable and auditable, at the cost of a supervisor bottleneck. **Peer-to-peer**: specialists hand off directly along a known workflow — lean, but the workflow must be explicit. **Blackboard**: all agents read and write a shared, *structured* state object, and act when their preconditions are met — the most flexible topology and the most visible, because any team member (human or agent) can inspect the full state at any moment.

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

The `status` field is a tiny state machine; each agent's contract is "when status is X and my inputs exist, produce Y and advance status." The blackboard makes the team's entire cognition *inspectable at every step* — our explainability theme made concrete.

| Topology | How agents communicate | Best for | Main risk |
|---|---|---|---|
| **Hierarchical** | All specialists report to a supervisor who delegates and integrates results | Complex tasks where subtasks are not predictable in advance | Supervisor bottleneck; supervisor failure breaks the whole team |
| **Peer-to-peer** | Specialists pass output directly to the next specialist in a fixed sequence | Well-understood workflows where each step's output is the next step's input | Implicit dependencies; hard to add a new step without redesigning the chain |
| **Blackboard** | All agents read and write a shared state dictionary; each agent fires when its preconditions are met | Tasks where multiple agents may need to revisit earlier steps or work in parallel | Concurrent writes can conflict; state can become large and hard to audit |

[[MC]]
An agent team keeps stalling: the checker waits for verified facts while the researcher believes its job is done. The most diagnostic artifact to inspect first is:
- ( ) The model weights
- ( ) Each agent's temperature setting
- (x) The shared state object and each role's precondition/postcondition contract
- ( ) The total token count

---

## Code Cell

The code below implements the three-agent meeting-notes team using a blackboard pattern: a shared `state` dictionary holds all the data, and a `while` loop fires whichever agent matches the current `status` field. Read the `extractor`, `writer`, and `checker` functions in order — each one reads only the slice of the state it needs, writes its output back to a specific key, and advances the `status` to the next stage.

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

### Critical Thinking Questions

5. Trace one full pass of the `while` loop: which role fired at each `status`, and what did it write to the shared state? The Recorder draws the state machine on paper with boxes for each status and arrows labeled with which agent causes the transition.

   > *Hint: Start at `status = "extracting"`. The `extractor` function fires. After it runs, what is `state["status"]`? Then which function fires next?*

6. The checker can send `status` back to `"drafting"`, creating a critique-refine loop *inside* the team. What prevents an infinite loop, and where have you seen that same safeguard at least twice before in this course?

   > *Hint: Look at the variable `guard`. What would happen if the checker kept failing and `guard` was not there? Where did we use a similar guard count in the debate and critique-refine modules?*

7. Each `llm` call sees only a slice of the state dictionary. For each role (extractor, writer, checker), name one piece of state it deliberately does *not* see, and explain the specific failure that omission prevents.

   > *Hint: For example, the extractor does not see `state["minutes"]` because minutes have not been written yet — but also because seeing a draft might bias the action-item extraction. What analogous risks exist for the writer and checker?*

> **⚠️ Common Misconception:** Students often assume that giving every agent access to the *full* state object is safer — "the more context, the better." In practice, the opposite is often true. An agent given irrelevant context is more likely to be distracted by it, to over-fit its output to previous stages, or to reproduce upstream errors with false confidence. The discipline of passing only what each role needs is not a technical limitation — it is a deliberate design choice that makes each agent's behavior more predictable and more testable in isolation.

With the pattern fully understood, Part III applies it directly to your final project — this is where the activity becomes a design session for the work you will submit.

---

# Part III: Design Your Project Team

In this section you will design the agent team for your final project, choose a topology, identify your riskiest seam, and build a monolith baseline to compare against. The artifacts you produce here are required components of your project proposal.

## Exercises

1. *Team charter, agent edition.*

   *What to do:* For your final project concept, produce the design table: one row per agent with columns for role, system-prompt summary, inputs, outputs, temperature, tools used, and the evaluation you will run on it in isolation. This table is a required artifact of your project proposal.

   *Starter hint:* Copy the 3-agent pipeline table from Model 1 and adapt it to your project domain. For each agent, write the first sentence of its system prompt — that sentence should fully capture its role.

   *You've succeeded when:* A teammate can read your table, write code that calls your agents in sequence, and produce output in the format you specified — without asking you any clarifying questions.

2. *Topology defense.*

   *What to do:* State which topology (hierarchical, peer-to-peer, or blackboard) your team uses, and write a three-sentence defense referencing at least one failure mode it mitigates and one it accepts.

   *Starter hint:* Most simple projects start as peer-to-peer because the workflow is linear. Ask: does your project ever need an agent to re-run an earlier step based on later information? If yes, you may need a blackboard.

   *You've succeeded when:* Your defense acknowledges a real weakness of your chosen topology and names a concrete scenario where that weakness could appear in your project.

3. *Seam test.*

   *What to do:* Pick your riskiest handoff — the one where a formatting mistake or missing field would silently corrupt all downstream output. Write five synthetic inputs for the upstream agent and assert properties of its output format programmatically. Report the pass rate.

   *Starter hint:* "Assert properties programmatically" means writing Python like `assert "|" in output`, `assert len(output.split("\n")) >= 1`, or parsing it with `json.loads()` and checking required keys.

   *You've succeeded when:* You can report a pass rate (e.g., "4 of 5 synthetic inputs produced correctly formatted output") and have identified what specifically broke in the failing case.

4. *Monolith baseline.*

   *What to do:* Implement your project's core task as a single mega-prompt and keep the output. Your final report must compare your team against this baseline using the evaluation harness. Design the comparison now: what task set, what metric, and what protocol will you use?

   *Starter hint:* The mega-prompt should ask for all outputs at once (action items, minutes, summary, verification) in a single call. The metric could be a rubric score, factual accuracy count, or LLM-as-judge score from the next module.

   *You've succeeded when:* You have a working monolith, a list of 10 test inputs, and a defined metric so that anyone could run the comparison and get the same result.

---

## Reflection Prompt

*Personal:* Your POGIL team rotates roles so every human learns every job, yet today you assigned your *agents* permanent specialties. In your own learning, when has being forced to do every part of a task (like a monolith) helped you understand it more deeply, versus when has specialization made you more effective?

*Technical:* The blackboard pattern makes team state inspectable at every step. Describe a specific debugging scenario in your project where that inspectability would save you significant time compared to debugging a monolith.

*Societal:* An agent team processing job applications might have an Extractor, a Scorer, a Ranker, and a Recommender — each responsible for only one step. If the Scorer is biased, the Ranker faithfully ranks biased scores, and the Recommender faithfully recommends from a biased ranking. Would you rather debug a monolith that does all four steps in one prompt, or a team where the bias is localized to one agent? Is there a case where decomposition makes bias *harder* to detect?

---

→ Coming Up Next: In the *Visual Agent Building with Langflow* activity, we turn to visual tools — drag-and-drop builders — that let us design and share these same architectures without writing every line of code from scratch.

## Further Reading

- Anthropic engineering blog. "Building Effective Agents" (2024) and "How we built our multi-agent research system" (2025, online).
- Wu et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." (2023).
- Hong et al. "MetaGPT: Meta Programming for Multi-Agent Collaborative Frameworks." *ICLR* (2024).
