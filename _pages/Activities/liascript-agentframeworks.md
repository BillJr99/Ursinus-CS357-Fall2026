# Agent Frameworks: LangChain, CrewAI, AutoGen, and Agno
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-agentframeworks.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentframeworks.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Agent Frameworks: LangChain, CrewAI, AutoGen, and Agno

Every framework is a wager: *we think these patterns repeat often enough to justify hiding them.* When the wager pays off, you write a research agent in twenty lines instead of two hundred. When it doesn't, you spend an afternoon fighting the framework's assumptions instead of building your system. This activity examines what the major 2024–2025 agent frameworks actually hide, what they cost you when they get it wrong, and how to decide which level of abstraction belongs in which project. The arc: **why frameworks exist $\rightarrow$ the leaky abstraction problem $\rightarrow$ framework comparison $\rightarrow$ choosing the right tool**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Read each model carefully before answering the questions beneath it. The Recorder collects the group's answers to post to the Class Activity Questions discussion board; the Presenter is prepared to report out disagreements and alternative framings. After class, complete the Reflection Prompt individually in your course notebook.

---

# Part I: Why Frameworks Exist

## Model 1: Framework Comparison

Every agent system, regardless of framework, must solve the same four boilerplate problems: **memory management** (which prior turns does the agent see?), **tool routing** (how does the model's function-call land in real code?), **prompt templating** (how do dynamic values get inserted without string bugs?), and **conversation history** (how is the message list accumulated and truncated?). Frameworks pre-solve these so you don't re-solve them on every project. The cost is **abstraction leakage**: the moment the framework's assumptions diverge from your requirements, the hidden machinery becomes your adversary.

| Framework | Best For | Abstraction Level | Code Volume | Control Level | Key Concept |
|---|---|---|---|---|---|
| LangChain / LangGraph | Complex pipelines, stateful multi-agent graphs | High (LCEL, chains) | Verbose | Moderate | Chains, runnables, graphs |
| CrewAI | Role-based agent teams; pedagogically clear structure | High (Crew/Task/Agent) | Concise | Low-moderate | Role, Task, Crew, Process |
| AutoGen | Conversational multi-agent; code execution feedback loops | Medium-high | Moderate | Moderate-high | AssistantAgent, UserProxy |
| Agno (formerly Phi Data) | Lightweight, fast iteration; clean tool and memory API | Low-medium | Concise | High | Agent, Tool, Memory |
| LlamaIndex | Retrieval-heavy systems; RAG pipelines; data connectors | Medium (query engines) | Moderate | Moderate | Index, QueryEngine, Router |
| Raw OpenAI / Ollama SDK | Maximum control, learning how agents work | None | High | Maximum | Direct API calls |

### Critical Thinking Questions

1. For each row in Model 1, identify one thing the framework hides that a developer writing raw code must implement explicitly. Which hidden mechanism is most likely to surprise a beginner?

2. "Abstraction level" and "control level" move in opposite directions across the table. State this as a general engineering principle and give one example from outside AI where the same tradeoff appears.

3. A classmate says "I'll just use LangChain for everything — it has the biggest ecosystem." What is the strongest argument *against* this as a default strategy?

---

# Part II: The Leaky Abstraction Problem

## Model 2: The Same Pipeline, Three Frameworks

Consider a three-agent pipeline: **Researcher** (searches the web and retrieves relevant passages) → **Drafter** (writes a response using those passages) → **Critic** (identifies weaknesses and returns a revision list). Below is the conceptual structure in three frameworks.

**LangChain / LangGraph:**
```
graph = StateGraph(PipelineState)
graph.add_node("researcher", researcher_chain)  # LCEL: prompt | llm | parser
graph.add_node("drafter",    drafter_chain)
graph.add_node("critic",     critic_chain)
graph.add_edge("researcher", "drafter")
graph.add_conditional_edges("critic", should_revise, {"yes": "drafter", "no": END})
app = graph.compile()
result = app.invoke({"question": q})
```
*Easy*: stateful loops, conditional branching, streaming. *Hard*: understanding what's in `PipelineState` at any moment; LCEL operator overloading hides the prompt structure.

**CrewAI:**
```
researcher = Agent(role="Researcher", goal="...", backstory="...", tools=[search_tool])
drafter    = Agent(role="Drafter",    goal="...", backstory="...")
critic     = Agent(role="Critic",     goal="...", backstory="...")
task_r = Task(description="Research: {question}", agent=researcher, expected_output="passages")
task_d = Task(description="Draft a response using: {passages}", agent=drafter, expected_output="draft")
task_c = Task(description="Critique the draft", agent=critic,     expected_output="revision list")
crew = Crew(agents=[researcher, drafter, critic], tasks=[task_r, task_d, task_c], process=Process.sequential)
crew.kickoff(inputs={"question": q})
```
*Easy*: role semantics are human-readable; great for demos and pedagogy. *Hard*: inter-task data passing is implicit; memory isolation between agents is not guaranteed; the framework decides the prompt wording around your `description`.

**AutoGen:**
```
researcher = AssistantAgent("researcher", system_message="You search and retrieve...", llm_config=cfg)
drafter    = AssistantAgent("drafter",    system_message="You write responses...",    llm_config=cfg)
critic     = UserProxyAgent("critic",     human_input_mode="NEVER", code_execution_config=False)
groupchat  = GroupChat(agents=[researcher, drafter, critic], messages=[], max_round=6)
manager    = GroupChatManager(groupchat=groupchat, llm_config=cfg)
researcher.initiate_chat(manager, message=q)
```
*Easy*: conversational handoffs; code execution built-in for the UserProxy pattern; async support. *Hard*: all agents share the group chat history, so context isolation is the developer's burden; the conversation can meander without explicit routing.

### Critical Thinking Questions

4. In the LangGraph version, the `PipelineState` object is the blackboard. What is the equivalent shared-state artifact in the CrewAI and AutoGen versions, and which is most visible to the developer?

5. In the AutoGen version, all three agents share the group chat message list. Describe a concrete scenario where this causes the Drafter to behave incorrectly because of something the Critic said to the Researcher.

6. The CrewAI framework writes part of each agent's prompt for you (the `backstory` and `role` fields are injected into the system prompt automatically). Is this an advantage or a risk? Under what circumstances would you want to read the exact system prompt your agent receives?

7. A student migrates her three-agent pipeline from raw OpenAI SDK calls to LangGraph. She finds that her Researcher agent now receives the Critic's feedback even though she didn't intend this. Explain in terms of abstraction leakage why this happened and what she should inspect.

---

# Part III: Choosing the Right Tool

## Model 3: Framework Selection Decision Table

| Scenario | Recommended Approach | Why |
|---|---|---|
| Learning how agents work for the first time | Raw OpenAI / Ollama SDK | Abstraction hides exactly what you need to see; learn the mechanism before the shortcut |
| Building a RAG system over company documents | LlamaIndex | Purpose-built for data connectors, retrieval pipelines, and query routing |
| Creating a team of specialized agents for a long, complex task | LangGraph or AutoGen | Both handle stateful, multi-turn, conditional workflows with explicit control |
| Rapid prototype needed this afternoon | CrewAI or Agno | Minimal boilerplate; role semantics are clear; easy to demo |
| Production system needing audit logs and monitoring | LangGraph + LangSmith | Graph structure makes each step inspectable; LangSmith captures traces per node |
| Teaching a team of students the agent-team pattern | CrewAI | Role/Task/Crew maps directly onto POGIL roles; code is readable without framework expertise |

[[MC]]
A student builds a 4-agent pipeline using LangChain and notices the agents are sharing more context than they should — the Formatter agent is responding to instructions that were only meant for the Researcher. The most likely cause is:
- (x) LangChain's default memory sharing is exposing more conversation history than intended; they need to configure per-agent memory isolation rather than passing the full shared state to every node
- ( ) LangChain contains a bug that routes messages to wrong agents
- ( ) The agents have become too capable and are reading each other's system prompts
- ( ) They should switch to a different LLM provider

---

### Critical Thinking Questions

8. The table recommends raw SDK code for learning. Once you have learned the mechanism, what specific signal should tell you it is time to introduce a framework? Name at least two concrete repetitions that would justify the abstraction.

9. LlamaIndex is categorized as a "data framework" rather than an "agent framework," yet it supports agents. What does this distinction reveal about the designers' primary mental model, and how does mental model shape API design?

10. Agno (formerly Phi Data) markets itself as "lightweight and fast." In the context of LLM applications, what does *fast* mean — inference speed, developer iteration speed, or runtime startup speed — and why does the distinction matter for your project?

---

## Exercises

1. *Framework audit.* Choose any two frameworks from Model 1 and install them in a local environment. Write the minimal code in each to call one LLM with one tool and print the result. Count the lines of code. Which boilerplate problems does each framework eliminate versus require you to handle? Report your findings as a table with the same columns as Model 1.

2. *Leaky abstraction hunt.* Take your existing agent project (or the pipeline from the Agent Loop activity) and wrap it in one framework from Model 1 that you have not used before. Identify one place where the framework's default behavior conflicts with your existing design. Document the conflict, the fix, and what you learned about the framework's assumptions.

3. *Selection defense.* For your final project, write a one-page technical memo (addressed to a hypothetical engineering manager) justifying your framework choice. Explicitly acknowledge the strongest counterargument and rebut it. The memo must reference at least one failure mode of your chosen framework and explain how you will mitigate it.

---

## Reflection Prompt

In your notebook: A framework is someone else's opinion about which patterns repeat. Every design choice in a framework reflects the designers' assumptions about what problems are most common. Looking at CrewAI's role-based abstraction and LangGraph's state-machine abstraction, what does each reveal about what its designers thought agent systems were *for*? Which assumption is closer to your own mental model of AI agents, and why does that matter for how you learn?

---

## Further Reading

- Chase, H. "LangChain Blog: LangGraph: Multi-Actor Applications with LLMs." (2024, online).
- Wu et al. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." arXiv:2308.08155 (2023).
- CrewAI documentation. "Core Concepts: Agents, Tasks, Crews, Processes." (2024, online).
- Agno documentation. "Quickstart and Architecture Overview." (2025, online).
- Liu, J. "LlamaIndex: A Data Framework for LLM Applications." (2023, online).
