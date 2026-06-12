# Welcome: What Is AI, and What Is an Agent?
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

## 1. A Very Short History of a Very Big Question

**Artificial intelligence is older than the computer science department.** In 1950, Alan Turing asked whether machines can think, and proposed his famous imitation game as a substitute for that question. The 1956 Dartmouth workshop named the field. Since then, AI has cycled through eras: symbolic reasoning and search, expert systems, statistical machine learning, deep learning, and now generative models and agents.

**Each era redefined what counts as intelligence.** Chess fell in 1997, Jeopardy in 2011, Go in 2016, and fluent conversation in the early 2020s. Each time, the goalposts moved, a phenomenon sometimes called the **AI effect**: once a machine can do it, we stop calling it intelligence.

**This course enters the story at the agent era.** A large language model that only answers prompts is a remarkable artifact, but it is *reactive*. The systems reshaping work and study today wrap that model in a loop: they observe, decide, call tools, check their own work, and try again. That loop is our subject.

---

## Model 1: Three Systems

Examine these three systems and decide which, if any, is an agent.

| System | Behavior |
|--------|----------|
| A | A thermostat turns the heat on when the room drops below 68 degrees, and off above 70. |
| B | A chatbot answers each question you type, with no memory of the conversation once the window closes. |
| C | A program is given the goal "find me three campsites available the weekend of October 10," browses a reservation website, filters results, and reports back with links. |

### Critical Thinking Questions

1. For each system, identify what it *perceives*, what it *decides*, and what *actions* it takes.
2. Which systems pursue a **goal** over multiple steps? Which respond once and stop?
3. System A contains no machine learning at all. Can something be an agent without being "AI"? Defend your answer.
4. What would System B need in order to behave like System C?

---

## 2. A Working Definition

**An agent is anything that perceives its environment through sensors and acts upon it through actuators in pursuit of a goal** (Russell and Norvig). For the software agents in this course:

$$
\text{action}_t = \pi(\text{observation}_t, \text{memory}_t, \text{goal})
$$

where $\pi$ is the agent's **policy**: the rule, program, or model that maps what the agent knows to what it does next. In the agents we build, $\pi$ is implemented by a **large language model** plus the scaffolding we write around it.

**Agency is a spectrum, not a switch.** A system is *more agentic* when it takes more steps autonomously, uses more tools, and recovers from more errors without a human in the loop. Greater agency brings greater usefulness, and greater responsibility, which is why governance occupies the final unit of this course.

[[MC]]
A spam filter classifies each incoming email as spam or not, one message at a time, and takes no further action. According to our working definition, the *most* accurate description is:
- ( ) It is a fully agentic system because it perceives and acts
- (x) It exhibits minimal agency: it perceives and acts, but pursues no multi-step goal and uses no tools
- ( ) It is not an agent because it uses machine learning
- ( ) It is not an agent because it has no body

---

## 3. Where We Are Going

The semester unfolds in four units, each building on the last. In Unit 1, *Anatomy of an Agent*, we build and run our own local agents within the first two weeks. In Unit 2, *Foundations on Demand*, we open the hood exactly when we need to: embeddings when our agent must search, attention when we wonder how it reads, retrieval when it must cite sources. In Unit 3, *Multi-Agent Systems*, we compose agents into teams that critique, debate, and reach consensus. In Unit 4, *Responsibility and Governance*, we ask who is accountable when agents act, and you will write policy for the agent team you build as your final project.

---

## Model 2: Your First Conversation with a Local Model

Your instructor will demonstrate a model running entirely on a laptop using Ollama, with no internet connection. We will pose the same prompt three times.

### Critical Thinking Questions

5. The model produced three different answers to the identical prompt. Brainstorm with your group: how can a deterministic computer program produce different outputs from the same input? List at least two hypotheses. (We will test them in week 3.)
6. The laptop's network connection is off. What does that imply about where the model's "knowledge" lives?
7. Name one task you would trust this offline model with, and one you would not. What distinguishes them?

---

## 4. Exercises

1. *Agent inventory.* As a team, list five systems you interacted with this week. Place each on an agency spectrum from "tool" to "autonomous agent," and justify the placement of the most contested one.
2. *Goalpost archaeology.* Find one news headline from before 2020 declaring that some capability "is not really AI." Bring it to the next class.
3. *Team charter.* Draft your team's working agreement: how you will rotate roles, communicate, and resolve disagreement. The Recorder posts it to the discussion board.

---

## Reflection Prompt

In your notebook: before today, what did the word "agent" mean to you, and what does it mean now? Identify one task in your own life that you would delegate to an agent, and one you never would. What is the difference between them?

---

## 5. Further Reading

- Melanie Mitchell. *Artificial Intelligence: A Guide for Thinking Humans* (2019). Prologue and Chapter 1 frame the questions of this course.
- Stuart Russell and Peter Norvig. *Artificial Intelligence: A Modern Approach* (4th ed., 2020). Chapter 2 defines agents and environments.
- Alan Turing. "Computing Machinery and Intelligence." *Mind* (1950). The original imitation game paper, freely available online.
