<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-welcomeagents.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-welcomeagents.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Welcome: What Is AI, and What Is an Agent?

This course is organized around a single guiding idea: an **agent** is a system that **perceives** its situation, **plans** what to do, and **acts** toward a goal. We move from **intuition $\rightarrow$ history $\rightarrow$ a working definition $\rightarrow$ our first conversation with an agent**, and along the way we establish how this class works: in teams, with rotating roles, building things from day one.

---

## Directions and Group Roles

Throughout this course, we work in POGIL-style teams of three or four. Today, choose roles; you will rotate them every class meeting so that everyone practices each role.

- **Manager**: keeps the team on task and watches the time.
- **Recorder**: writes the team's answers on the Class Activity Questions discussion board.
- **Presenter**: reports the team's findings to the class.
- **Reflector**: notes what helped or hindered the team, and shares one observation at the end.

Consider each model below and answer the questions provided. First reflect on the questions on your own briefly, before discussing and comparing your thoughts with your group. Report out on areas of disagreement or items for which your group identified alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| Agent | A system that senses its surroundings, decides what to do, and takes action toward a goal — all on its own | The campsite-finder in Model 1 that browses a website and returns links without being told each click to make |
| Perception | The step where an agent gathers information from its environment, such as reading a sensor, receiving a message, or seeing a web page | A thermostat reading the room temperature before deciding whether to turn the heat on |
| Policy (pi) | The rule or model that converts what the agent currently knows into the action it will take next | The language model inside an agent that reads your goal and chooses a response or tool call |
| Agency spectrum | A scale from "responds once and stops" to "pursues goals over many steps with many tools" — most systems fall somewhere in between | A spam filter sits near the reactive end; the campsite-finder sits near the autonomous end |
| AI effect | The tendency to stop calling something "intelligence" once a computer can reliably do it, moving the goalposts for what counts as AI | Chess was once seen as the pinnacle of machine thinking; today it is considered a solved, routine program |
| Large language model (LLM) | A neural network trained on vast amounts of text that can generate fluent language, answer questions, and follow instructions | The local model you will talk to in Model 2 today, running entirely on a laptop |

---

## 1. A Very Short History of a Very Big Question

**Artificial intelligence is older than the computer science department.** In 1950, Alan Turing asked whether machines can think, and proposed his famous imitation game as a substitute for that question. The 1956 Dartmouth workshop named the field. Since then, AI has cycled through eras: symbolic reasoning and search, expert systems, statistical machine learning, deep learning, and now generative models and agents.

**Each era redefined what counts as intelligence.** Chess fell in 1997, Jeopardy in 2011, Go in 2016, and fluent conversation in the early 2020s. Each time, the goalposts moved, a phenomenon sometimes called the **AI effect**: once a machine can do it, we stop calling it intelligence.

**This course enters the story at the agent era.** A large language model that only answers prompts is a remarkable artifact, but it is *reactive*. The systems reshaping work and study today wrap that model in a loop: they observe, decide, call tools, check their own work, and try again. That loop is our subject.

---

## Model 1: Three Systems

Before we look at the data, consider this: every time you ask a navigation app for directions, it perceives your location, plans a route, and acts by showing you the map — and if you miss a turn, it recalculates and tries again. AI agents work the same way, but instead of roads they navigate information and decisions. The three systems below span a wide range of that idea.

Examine these three systems and decide which, if any, is an agent.

| System | Behavior | What It Does When Something Goes Wrong |
|--------|----------|----------------------------------------|
| A | A thermostat turns the heat on when the room drops below 68 degrees, and off above 70 degrees. | It applies the same fixed rule again — it cannot diagnose a broken furnace or call a repairperson. |
| B | A chatbot answers each question you type, with no memory of the conversation once the window closes. | It has no awareness that it gave a bad answer, and takes no follow-up action unless you send another message. |
| C | A program is given the goal "find me three campsites available the weekend of October 10," browses a reservation website, filters results, and reports back with links. | It can retry failed page loads, try alternative search terms, and check availability across multiple sites before reporting. |

### Critical Thinking Questions

1. For each system, identify what it *perceives*, what it *decides*, and what *actions* it takes.

   > *Hint: Use the three-column breakdown — perception, decision, action — for each row. For System A, for example, perception is the temperature reading.*

2. Which systems pursue a **goal** over multiple steps? Which respond once and stop?

   > *Hint: Ask yourself whether the system would do anything differently if its first response turned out to be wrong or incomplete.*

3. System A contains no machine learning at all. Can something be an agent without being "AI"? Defend your answer.

   > *Hint: Look back at the definition in section 2 below. Does it say anything about learning, or only about perceiving, deciding, and acting?*

4. What would System B need in order to behave like System C?

   > *Hint: Think about what System C has that System B lacks — memory, tools, a goal that persists across steps. List at least two additions.*

---

## 2. A Working Definition

In this section, you will lock down the formal definition of an agent and place it on a spectrum from simple reflex to fully autonomous — so that every system you encounter this semester has a precise vocabulary to describe it.

**An agent is anything that perceives its environment through sensors and acts upon it through actuators in pursuit of a goal** (Russell and Norvig). For the software agents in this course:

$$
\text{action}_t = \pi(\text{observation}_t, \text{memory}_t, \text{goal})
$$

where $\pi$ is the agent's **policy**: the rule, program, or model that maps what the agent knows to what it does next. In the agents we build, $\pi$ is implemented by a **large language model** plus the scaffolding we write around it.

**Agency is a spectrum, not a switch.** A system is *more agentic* when it takes more steps autonomously, uses more tools, and recovers from more errors without a human in the loop. Greater agency brings greater usefulness, and greater responsibility — which is why governance occupies the final unit of this course.

Now that you have a working definition of agency, the next section previews the arc of the entire semester so you can see where each future topic fits.

[[MC]]
A spam filter classifies each incoming email as spam or not, one message at a time, and takes no further action. According to our working definition, the *most* accurate description is:
- ( ) It is a fully agentic system because it perceives and acts
- (x) It exhibits minimal agency: it perceives and acts, but pursues no multi-step goal and uses no tools
- ( ) It is not an agent because it uses machine learning
- ( ) It is not an agent because it has no body

> **⚠️ Common Misconception:** Many people assume that "AI" and "agent" mean the same thing, and that any system using machine learning is therefore an agent. In fact, a spam filter is an AI system (it learned from data) but barely qualifies as an agent, because it reacts to one email at a time with no goal that spans multiple steps. Conversely, the thermostat in System A is agent-like — it pursues a temperature goal continuously — but uses no AI at all. Agency and machine learning are separate ideas that often appear together but do not require each other.

---

## 3. Where We Are Going

The semester unfolds in four units, each building on the last. In Unit 1, *Anatomy of an Agent*, we build and run our own local agents within the first two weeks. In Unit 2, *Foundations on Demand*, we open the hood exactly when we need to: embeddings when our agent must search, attention when we wonder how it reads, retrieval when it must cite sources. In Unit 3, *Multi-Agent Systems*, we compose agents into teams that critique, debate, and reach consensus. In Unit 4, *Responsibility and Governance*, we ask who is accountable when agents act, and you will write policy for the agent team you build as your final project.

---

## Going Deeper (read at home): The AI Fluency Framework

Building an agent is only half the story; **working well with one is a human competency**, not just a technical one. This course is organized around **The AI Fluency Framework**, whose four interconnected competencies — **Delegation** (deciding whether, when, and how to engage AI), **Description** (describing goals well enough to prompt useful behavior), **Discernment** (assessing the usefulness of AI outputs), and **Diligence** (taking responsibility for what we do with AI) — make our interactions with AI effective, efficient, ethical, and safe. The framework also distinguishes three modes of interaction (automation, augmentation, and agency) that map onto the agency spectrum from Section 2. You will meet the four D's throughout the course: Description when we engineer prompts, Discernment when we evaluate and test outputs, and Diligence in the closing unit on responsibility and governance. **Before *The Agent Loop: Perceive, Plan, Act* activity**, read the framework summary: [/files/ai-fluency/1.2_AI_Fluency_Summary_16x9.pdf](/files/ai-fluency/1.2_AI_Fluency_Summary_16x9.pdf).

*Source: The AI Fluency Framework summary ([/files/ai-fluency/1.2_AI_Fluency_Summary_16x9.pdf](/files/ai-fluency/1.2_AI_Fluency_Summary_16x9.pdf)). Copyright 2025 Rick Dakan, Joseph Feller, and Anthropic. Released under the CC BY-NC-SA 4.0 license. This course is based on The AI Fluency Framework by Dakan and Feller.*

---

## The AI Capabilities and Limitations Framework

Delegating well — and, later, discerning good output from bad — depends on a realistic picture of what today's AI is actually good at. This companion framework names **four properties that shape what AI can and can't do for you.** Each sits on a spectrum: the further toward the *limitation* end your task falls, the more you should verify the output and compensate for it.

| Property | The question it answers | Works well (capability) | Gets shaky (limitation) |
|----------|-------------------------|-------------------------|-------------------------|
| **Next Token Prediction** | Where do AI answers come from? | Well-worn paths: summarize, reformat, explain common concepts | Novel territory, sparse patterns; "true" vs. "sounds true" |
| **Knowledge** | What does the AI actually know? | Frequent, recent-in-training, consistent: mainstream topics, popular languages | Rare, post-cutoff, niche, local, or contested topics |
| **Working Memory** | What is the AI paying attention to right now? | Material fits comfortably, session is current, you supply the relevant context | Very long documents/conversations; expecting cross-session continuity (the "cliff") |
| **Steerability** | How much am I in control? | Short, concrete, verifiable instructions ("respond as a table," "under 100 words") | Long reasoning chains, abstract asks, native precision |

Read the table as a checklist for **Delegation** and **Discernment**: before handing a task to AI, ask where it lands on each spectrum. A task built from common concepts, mainstream knowledge, a short context, and a concrete instruction is a safe delegation. A task in novel territory, on post-cutoff or contested facts, over a huge context, and requiring a long, precise chain of reasoning is one to supervise closely — or keep for a human.

> **Try it:** The [Token Prediction Playground](https://www.billmongan.com/Ursinus-CS357-Fall2026/TokenPredictor) is a tiny in-browser next-word model: feed it a common phrase and watch it get confident (capability); feed it rare or ungrounded words and watch it shrug (limitation). It makes the top row of the table above tangible — and it is the tool you will use in the icebreaker below.

*Copyright 2026 Anthropic. Original work building on the AI Fluency Framework developed by Prof. Rick Dakan (Ringling College of Art and Design) and Prof. Joseph Feller (University College Cork). Released under the CC BY-NC-SA 4.0 license.*

---

## Icebreaker: Predict the Next Token

*Estimated time: 20 minutes.*

Today's first practice is **seeing where AI answers come from**. No accounts, no installs — just your team, paper, and the course's [Token Prediction Playground](https://www.billmongan.com/Ursinus-CS357-Fall2026/TokenPredictor), a tiny next-word model that runs entirely in your browser. The goal is to feel the top row of the Capabilities and Limitations table — *Next Token Prediction* — from the inside.

**Step 1 — Predict by hand (7 minutes).** As a team, take these prompt stems (the Manager keeps time; the Recorder writes everything down). For each, every member privately writes the **three most likely next words** and a confidence (high/medium/low) — before anyone opens the Playground:

- "The capital of France is ___"
- "Once upon a ___"
- "To be or not to ___"
- "My professor's favorite ___"
- "The 2027 Nobel Prize in Physics was awarded to ___"

Compare within the team: where did everyone agree? Where did predictions scatter?

**Step 2 — Compare with the simulator (7 minutes).** Now type each stem into the [Token Prediction Playground](https://www.billmongan.com/Ursinus-CS357-Fall2026/TokenPredictor) and record what it predicts, and how confidently. Score your team against the machine. Watch for the pattern: on well-worn phrases the model is confident and so were you; on rare, personal, or future-facing stems it shrugs — and so, honestly, did you.

**Step 3 — What prediction can and cannot do (6 minutes).** Discuss as a team, and the Recorder posts your answers to the discussion board:

- Which stems were easy for both humans and the model, and *why*? (What makes a continuation "well-worn"?)
- Which stems *cannot* be answered by pattern-completion at all, no matter how much text the model has seen? What would a system need instead?
- If a model always continues with what "sounds right," when will "sounds true" diverge from "is true"? Name one concrete task where you would therefore verify its output.

### Reflection

- What surprised you about how well (or poorly) your team predicted the model's behavior?
- Where does your own knowledge come from, and how is that different from — or similar to — next-token prediction?
- Name one task from your own week that next-token prediction alone could handle, and one it could not.

---

## Model 2: Your First Conversation with a Local Model

In this model, you will observe a language model (a large neural network trained to predict text) running entirely on a laptop — no cloud, no internet — and you will form hypotheses about why its answers vary. These hypotheses will be tested rigorously in the *Why Different Answers Every Time? Sampling, Temperature, and Generation* activity.

Your instructor will demonstrate a model running entirely on a laptop using Ollama (a free tool for downloading and running AI models locally), with no internet connection. We will pose the same prompt three times.

### Critical Thinking Questions

5. The model produced three different answers to the identical prompt. Brainstorm with your group: how can a deterministic computer program produce different outputs from the same input? List at least two hypotheses. (We will test them in the *Why Different Answers Every Time? Sampling, Temperature, and Generation* activity.)

   > *Hint: Think about randomness. Is a coin flip "deterministic"? Where in a process that assigns probabilities to words might randomness enter?*

6. The laptop's network connection is off. What does that imply about where the model's "knowledge" lives?

   > *Hint: If no data came in over the network, everything the model "knows" must have arrived at some earlier time. When and how?*

7. Name one task you would trust this offline model with, and one you would not. What distinguishes them?

   > *Hint: Think about tasks that require up-to-date information versus tasks that rely on stable, long-established knowledge.*

---

## 4. Exercises

1. *Agent inventory.*

   - *What to do*: As a team, list five systems you interacted with this week. Place each on an agency spectrum from "tool" to "autonomous agent," and justify the placement of the most contested one.
   - *Starter hint*: Start with a simple axis drawn on paper: label the left end "one-shot tool" and the right end "fully autonomous agent." Place each system and then argue about the two most controversial placements.
   - *You've succeeded when*: Your team can articulate, in one sentence per system, *why* it sits where it does on the spectrum using the perceive-decide-act vocabulary from today.

2. *Goalpost archaeology.*

   - *What to do*: Find one news headline from before 2020 declaring that some capability "is not really AI." Bring it to *The Agent Loop: Perceive, Plan, Act* activity.
   - *Starter hint*: Search for phrases like "that's not real AI" or "just a program" alongside the name of a system (chess engine, recommendation algorithm, autocorrect) that we now take for granted.
   - *You've succeeded when*: You can name the capability, the year it was dismissed, and explain using the AI effect why the dismissal was predictable in hindsight.

3. *Team charter.*

   - *What to do*: Draft your team's working agreement: how you will rotate roles, communicate, and resolve disagreement. The Recorder posts it to the discussion board.
   - *Starter hint*: Address at least three things: role rotation schedule, how you handle absences, and one norm about disagreement (for example, "we must hear every voice before voting").
   - *You've succeeded when*: Every team member has read the charter and the Recorder has posted it with everyone's name attached.

---

## Reflection Prompt

*Personal*: Before today, what did the word "agent" mean to you — perhaps a travel agent, a secret agent, or something else entirely? How has today's definition changed or complicated that intuition? Identify one moment during the activity where your thinking shifted.

*Technical*: You now have a formal definition of agency: perceive, decide, act, toward a goal, over multiple steps. If you were designing System B to become more agentic, which capability would you add first and why? Sketch what the new system would look like after that one addition.

*Societal*: Identify one task in your own life that you would delegate to an autonomous agent, and one you never would. What is the difference between them? Now extend that reasoning: if millions of people made the same choices you did, what kinds of decisions would agents be making at scale — and what kinds would remain with humans?

---

→ Coming Up Next: In *The Agent Loop: Perceive, Plan, Act* activity, we zoom inside the agent loop itself — the repeating cycle of perceive, plan, and act — and we write our first working agent in Python that calls a tool and loops until it finds an answer.

## 5. Further Reading

- Melanie Mitchell. *Artificial Intelligence: A Guide for Thinking Humans* (2019). Prologue and Chapter 1 frame the questions of this course.
- Stuart Russell and Peter Norvig. *Artificial Intelligence: A Modern Approach* (4th ed., 2020). Chapter 2 defines agents and environments.
- Alan Turing. "Computing Machinery and Intelligence." *Mind* (1950). The original imitation game paper, freely available online.
- Rick Dakan and Joseph Feller, with Anthropic. *The AI Fluency Framework* (2025). The Delegation, Description, Discernment, and Diligence competencies that organize this course. Released under CC BY-NC-SA 4.0.
