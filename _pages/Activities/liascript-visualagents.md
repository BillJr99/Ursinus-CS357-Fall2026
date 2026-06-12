# Visual Agent Building with Langflow
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-visualagents.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-visualagents.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Visual Agent Building with Langflow

Every pattern we have coded by hand (pipelines, RAG, routers, agents with tools) exists as a **drag-and-drop component** in visual builders such as **Langflow**. Today we rebuild a known system visually, not to abandon code, but to learn when each medium wins, and to gain a lingua franca for collaborating with non-programmers, which your project presentations will require. The arc: **why visual builders exist $\rightarrow$ rebuilding our RAG bot in Langflow $\rightarrow$ reading a flow as an architecture diagram $\rightarrow$ the limits of low-code**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is a hands-on build day: the Manager drives the install and canvas, the Recorder captures screenshots of each working flow, the Presenter demos your flow during the closing gallery, and the Reflector logs where the visual medium helped or fought you. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Medium and the Message

## 1. What a Flow Is

**A flow is a dataflow graph.** Nodes are components (prompt templates, model calls, retrievers, parsers); edges carry typed data between them. Langflow renders the graph on a canvas, executes it on demand, and exposes every intermediate value for inspection, which makes it, among other things, a *teaching and debugging instrument*: the architecture diagram and the running system are the same object.

**You already know every component.** A Prompt node is your system-prompt string; an Ollama node is your `chat()` function; a Chroma node is your vector store; a chain of nodes is your pipeline. The conceptual work of weeks 1 through 10 transfers intact; only the syntax changes from Python to wiring.

**Setup (one per team).** Install with `pip install langflow`, launch with `langflow run`, and browse to `http://localhost:7860`. Point model components at your local Ollama (base URL `http://localhost:11434`), keeping today fully private and free, consistent with our local-first stance.

---

## Model 1: Translation Table

### Critical Thinking Questions

1. Complete the translation table as a team: for each artifact from our codebase (system prompt, `chat()` wrapper, chunker, embedder, vector query, critique loop), name the Langflow component or wiring pattern that plays its role.
2. Which of our patterns has *no* single-component equivalent and must be expressed as graph structure? What does that tell you about what is essential (the pattern) versus incidental (the medium)?
3. Predict one class of bug that becomes *easier* to find on a canvas than in code, and one that becomes *harder*.

---

# Part II: Build Sessions

## 2. Build 1: Chat with a Persona

Construct the minimal flow: **Chat Input $\rightarrow$ Prompt (with your Lab 1 persona pasted in) $\rightarrow$ Ollama $\rightarrow$ Chat Output**. Run it in the playground and confirm the persona holds.

## 3. Build 2: RAG over Your Lab 2 Corpus

Recreate your Lab 2 pipeline visually: **File loader $\rightarrow$ Text splitter $\rightarrow$ Ollama Embeddings $\rightarrow$ Chroma (ingest)**, then a query path **Chat Input $\rightarrow$ Chroma retriever $\rightarrow$ Prompt (with your grounding-and-citation instructions) $\rightarrow$ Ollama $\rightarrow$ Chat Output**. Use the same chunk size you shipped in Lab 2.

## 4. Build 3: Export and Reenter Code

Every flow exports as JSON, and Langflow can serve any flow as a REST API endpoint. Export your RAG flow, skim the JSON to find your prompt text and chunk size, then call the flow from three lines of Python `requests`. The visual artifact and your code-world tooling (harnesses, batch evaluation) compose.

---

## Model 2: The Same System, Twice

You now possess the same RAG system in Python (Lab 2) and on a canvas (Build 2).

### Critical Thinking Questions

4. Run your Lab 2 evaluation question set through the Langflow endpoint with your week 3 harness. Do the two implementations score identically? If not, hunt the delta: which knob (chunking, k, prompt wording) silently differs?
5. Time both versions on ten queries. Attribute any overhead, and decide whether it matters for an interactive bot versus a batch pipeline.
6. Hand your canvas to a teammate who did not build it, with no narration allowed. How far can they explain the system? Try the same with your Python file. Record the asymmetry honestly: it cuts both ways.

[[MC]]
The most defensible claim about visual builders versus code for agent systems is:
- ( ) Visual builders are for beginners and code is for professionals
- ( ) Visual flows cannot implement RAG or tool use
- (x) Both express the same underlying patterns; visual excels at communication and rapid wiring, code at version control, testing, and arbitrary logic
- ( ) Flows run faster because they skip Python

---

# Part III: Synthesis and Practice

## 5. Exercises

1. *Pattern rebuild.* Choose one Unit 3 pattern (router, critique-refine, or a two-stage pipeline) and realize it on the canvas. Screenshot the working flow with one playground transcript.
2. *Limit hunt.* Attempt to express your Lab 4 debate (n agents, two rounds, majority vote) visually. Document precisely where the canvas resists (loops, dynamic fan-out), and state the general principle about what dataflow graphs express awkwardly.
3. *Stakeholder demo.* Prepare a 90-second explanation of your Build 2 flow for a non-programmer (an RA, a club officer, a professor in another department). Deliver it to another team's Reflector and collect one comprehension question you failed to anticipate. This rehearses your final presentation.

---

## Reflection Prompt

In your notebook: low-code tools widen who can build AI systems, including people who cannot audit the components they wire together. Is that democratization, risk, or both? Anchor your answer in one specific thing you wired today without fully understanding it.

---

## 6. Further Reading

- Langflow documentation: https://docs.langflow.org
- Ollama integration guide within the Langflow docs (component reference).
- Victor, Bret. "Learnable Programming" (2012, online essay), on representations that make systems visible.
