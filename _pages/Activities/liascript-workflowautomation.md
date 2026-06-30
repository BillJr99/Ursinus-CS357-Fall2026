# Workflow Automation for Intake and Triage: LangChain and Power Automate
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-workflowautomation.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-workflowautomation.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Workflow Automation for Intake and Triage: LangChain and Power Automate

Most real organizational pain is not a missing algorithm — it is a flood of unstructured requests landing in an inbox or a form, each needing to be read, understood, classified, checked for missing information, and routed to whoever can act on it. This is **intake and triage**, and it is one of the highest-value, lowest-glamour places to put an agent to work. Today we study two complementary tools for it: **LangChain**, a code-first framework where you control every step, and **Microsoft Power Automate**, a low-code, connector-driven platform that lives inside the Microsoft 365 tools many institutions already use. We compare when each fits, design a triage pipeline that classifies a request, flags gaps, and routes it, and put a human gate on the consequential step. The arc: **the intake-and-triage problem $\rightarrow$ code-first vs. low-code $\rightarrow$ the triage pipeline pattern $\rightarrow$ gap detection $\rightarrow$ routing with a human gate.**

> Builds on *Agent Frameworks* (`liascript-agentframeworks.md`), *Human-in-the-Loop* (`liascript-humanintheloop.md`), and *Evaluating Outputs* (`liascript-evaluatingoutputs.md`). It motivates the **Request Intake and Triage Agent** project (`/Projects/RequestTriage`).

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss as a team. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports disagreements. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Intake** | Receiving unstructured requests from some channel and capturing them in a uniform form | A shared inbox, a web form, or a Teams channel collecting "please do X" messages |
| **Triage** | Reading each request and deciding its category, priority, and destination | Labeling a request as "facilities / urgent / route to maintenance" |
| **Gap detection** | Noticing required information a request is missing, before it is routed | A purchase request with no budget code is flagged "needs budget code" |
| **Routing** | Sending the triaged, complete request to the person or system that handles it | Creating a ticket, emailing the right team, or adding a row to a tracking sheet |
| **Low-code / connector platform** | A drag-and-connect automation tool with pre-built integrations to common apps | Power Automate wiring Outlook → AI classify → Planner → Teams notification |
| **Human gate** | A checkpoint where a person approves a consequential or low-confidence action before it executes | A reviewer confirms the routing for any request the agent classified with low confidence |

---

# Part I: The Intake-and-Triage Problem

A request flood has a predictable shape: requests arrive unstructured, vary wildly in completeness, and a human spends scarce time doing the same low-judgment reading and sorting over and over. The opportunity is to let an agent do the **first pass** — classify, check completeness, draft a routing decision — while keeping a human on the **consequential** step. Critically, this is also a textbook place for harm if done carelessly: a misrouted or auto-actioned request can have real consequences, which is why triage agents *recommend and route* far more often than they *decide and execute*.

### Critical Thinking Questions

1. Triage is mostly *classification + completeness-checking + routing*, not generation. Why does that make it a good early use case for an LLM agent compared to, say, "write the response for me"? What kinds of errors are cheaper here, and which are dangerous?

2. Identify one intake-and-triage workflow you have personally been on the *receiving* end of (a help desk, an advising request, a club's form). Where in that flow would a first-pass agent have helped, and where would you have insisted a human stay in the loop?

---

# Part II: Code-First vs. Low-Code

## Model 1: LangChain vs. Power Automate

| Dimension | LangChain (code-first) | Power Automate (low-code) |
|---|---|---|
| Who builds it | A developer writing Python | Anyone, via a visual designer |
| Control / flexibility | Maximum — any logic, any model, any store | Bounded by available connectors and actions |
| Integrations | Whatever you code | Hundreds of pre-built connectors (Outlook, Teams, SharePoint, Forms, Planner) |
| Best when | Custom logic, custom models, full control, version-controlled code | The data already lives in Microsoft 365 and the logic is mostly "when X, do Y" |
| Observability | LangSmith / OTel traces (`liascript-observability.md`) | Built-in run history in the platform |
| Hidden cost | You own everything, including the boilerplate | Vendor lock-in; logic spread across a GUI is hard to review/diff |

Neither is "better." A useful hybrid: Power Automate handles the **plumbing** (catch the email, post the notification, update the sheet) and calls out to a LangChain agent (or a hosted model) for the **judgment** (classify, detect gaps). This mirrors the framework-vs-raw-code tradeoff from the Agent Frameworks activity: convenience is bought with visibility.

### Critical Thinking Questions

3. An institution's requests already arrive as Outlook emails and the team lives in Teams. Argue for starting in Power Automate. Then argue for the part of the pipeline you would still write in LangChain, and why.

4. "Logic spread across a GUI is hard to review and diff" is listed as a hidden cost of low-code. Connect this to the course value of *environment as code* (`liascript-aidevenv.md`). What governance problem appears when the triage rules live only in a vendor's visual editor?

---

# Part III: The Triage Pipeline Pattern

## Model 2: Classify → Detect Gaps → Route (with a gate)

A robust triage pipeline is a short, inspectable sequence. Here it is conceptually in LangChain-style pseudocode; the same shape maps onto Power Automate actions.

```python
# Each step is small and traceable; the model does judgment, code does plumbing.
def triage(request_text: str) -> dict:
    category   = classify(request_text)                 # LLM: which bucket?
    priority   = score_priority(request_text, category) # LLM or rules
    missing    = detect_gaps(request_text, category)    # LLM: required fields absent?
    confidence = estimate_confidence(category, missing) # how sure are we?

    decision = {
        "category": category, "priority": priority,
        "missing": missing, "route_to": route_for(category),
        "needs_human": confidence < THRESHOLD or priority == "urgent",
    }
    return decision   # RECOMMEND + ROUTE; a human gate handles `needs_human`
```

The schema-shaped output (a dict/JSON) matters: downstream plumbing (ticket creation, notification) is deterministic code that consumes structured fields, not free text. Recall *Evaluating Outputs*: validate that the model returned the schema you expect before you act on it.

### Critical Thinking Questions

5. Why force the model's output into a fixed schema (category, priority, missing, route_to, needs_human) instead of letting it write a paragraph? Name two failure modes the schema prevents downstream.

6. The pipeline *routes* even when `needs_human` is true — it just flags it. Contrast this with a design that *blocks* and does nothing until a human acts. When is each better? (Consider an urgent safety request vs. a routine one.)

---

# Part IV: Gap Detection and Routing with a Human Gate

## Model 3: Finding What's Missing, Then Handing Off

The most useful and least flashy step is **gap detection**: catching that a request lacks something required *before* it wastes a human's time bouncing back. It turns "the team processes requests" into "the team processes *complete, correctly-routed* requests." Pair it with a **human gate** on the consequential action (the actual routing/ticket), gated by confidence and priority. This is the *Human-in-the-Loop* pattern applied to operations: autonomy on the cheap, reversible parts (reading, classifying, drafting); a human on the consequential, hard-to-reverse part (assigning work to a person).

### Critical Thinking Questions

7. Design the gap-detection rule for one request type (e.g., a room-reservation request). List the required fields, and decide for each whether a *missing* field should (a) block routing, (b) route with a "needs info" flag, or (c) be auto-filled with a default. Defend one of your (c) choices and its risk.

8. Where should the human gate sit, and what should the human *see* at the gate to decide quickly? Tie this to the explainability idea of "surface the evidence at the moment of decision" from the explainability activity.

---

## Reflective Prompt

In your notebook (3–5 sentences): Pick a real intake-and-triage workflow (on campus, in a club, or at a job). Sketch where you would draw the line between what an agent does first-pass (classify, detect gaps, draft routing) and what a human must approve, and say whether you would build it code-first (LangChain) or low-code (Power Automate) — and why. Name the one gap-detection check that would save the most human time.
