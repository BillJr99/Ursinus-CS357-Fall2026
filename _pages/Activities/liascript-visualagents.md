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

Every pattern we have coded by hand — through the *Agent Teams: Specialists over Monoliths* activity and everything before it (pipelines, RAG, routers, agents with tools) — exists as a **drag-and-drop component** in visual builders such as **Langflow**. Today we rebuild a known system visually — not to abandon code, but to learn when each medium wins, and to gain a shared vocabulary for collaborating with non-programmers, which your project presentations will require. The arc: **why visual builders exist $\rightarrow$ rebuilding our RAG bot in Langflow $\rightarrow$ reading a flow as an architecture diagram $\rightarrow$ the limits of low-code**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today is a hands-on build day: the Manager drives the install and canvas, the Recorder captures screenshots of each working flow, the Presenter demos your flow during the closing gallery, and the Reflector logs where the visual medium helped or fought you. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Langflow** | A visual, drag-and-drop tool for building AI pipelines where components appear as boxes on a canvas and data flows along drawn connections between them. | You will drag an "Ollama" box onto the canvas and connect it to a "Chat Output" box instead of writing `requests.post(...)` in Python. |
| **Dataflow graph** | A diagram where nodes represent processing steps and edges (arrows) represent data traveling from one step to the next; every flow you build today is a dataflow graph. | Your RAG pipeline becomes a graph: File Loader → Text Splitter → Embedder → Chroma → Prompt → Ollama → Output. |
| **RAG (Retrieval-Augmented Generation)** | A technique where the AI looks up relevant documents from a database before answering, so its answers are grounded in real source material rather than just training data. | Your RAG Knowledge Base Lab bot that searches your uploaded corpus before answering questions. |
| **REST API (Representational State Transfer Application Programming Interface)** | A standard way for programs to communicate over the internet by sending and receiving structured data; Langflow can turn any flow into a REST API endpoint that your Python code can call. | After building your RAG flow visually, you export it and call it from three lines of Python using the `requests` library. |
| **Low-code** | A style of software development where most logic is assembled visually with minimal hand-written code, making it accessible to people without programming backgrounds. | Wiring a complete RAG pipeline in Langflow by dragging boxes — no Python required — so a club officer could set it up themselves. |
| **Chunk size** | The number of characters or words each piece of a document is split into before being stored in the vector database; larger chunks preserve more context but cost more to embed and retrieve. | In the RAG Knowledge Base Lab you chose a chunk size (e.g., 500 characters); today you enter the same number in Langflow's Text Splitter component. |

---

# Part I: The Medium and the Message

In this part, you will discover that every AI pipeline you've coded this semester can be expressed visually as a drag-and-drop flow — and you will learn *when* that matters and *when* it doesn't.

## Model 1: Translation Table

Think of architectural blueprints versus a physical building. Both represent the same structure, but blueprints are easier to share with a client who has never swung a hammer, while the physical building is what actually runs. Langflow is the blueprint tool: it makes the architecture of your AI system visible and explainable to non-programmers, while the code you have been writing is the building.

Today you will discover that the blueprint and the building encode exactly the same ideas — and that choosing between them depends on your audience, not on what is technically possible. Visual builders have democratized who can *assemble* AI systems; your job today is to understand what that means for who can *audit* them.

**A flow is a dataflow graph.** Nodes are components (prompt templates, model calls, retrievers, parsers); edges carry typed data between them. Langflow renders the graph on a canvas, executes it on demand, and exposes every intermediate value for inspection — which makes it, among other things, a *teaching and debugging instrument*: the architecture diagram and the running system are the same object.

**You already know every component.** A Prompt node is your system-prompt string; an Ollama node is your `chat()` function; a Chroma node is your vector store; a chain of nodes is your pipeline. The conceptual work of weeks 1 through 10 transfers intact; only the syntax changes from Python to wiring.

**Setup (one per team).** Install with `pip install langflow`, launch with `langflow run`, and browse to `http://localhost:7860`. Point model components at your local Ollama (base URL `http://localhost:11434`), keeping today fully private and free, consistent with our local-first stance.

| Python code artifact | Langflow component or pattern | What stays the same | What changes |
|---|---|---|---|
| System-prompt string in `llm()` | **Prompt** node with a text field for your instructions | The instructions themselves are identical | You type them into a GUI box instead of a Python string variable |
| `chat()` wrapper function calling Ollama | **Ollama** node with base URL and model name fields | The model name, temperature, and base URL are the same settings | You set them in dropdown menus rather than in a `json=` dict |
| Text chunker (e.g., `chunk_text(text, 500)`) | **Text Splitter** node with chunk size and overlap fields | The chunk size and overlap you chose in the RAG Knowledge Base Lab apply directly | The splitting algorithm is a node you wire rather than a function you call |
| `embed(text)` function | **Ollama Embeddings** node | Same embedding model (e.g., `nomic-embed-text`) | Wired visually rather than called explicitly |
| ChromaDB vector store | **Chroma** node with collection name and persist directory | The collection name and directory path are the same | Ingest and query are two separate wired paths on the canvas |
| Critique-refine loop | A cycle in the graph from checker node back to writer node | The same critique prompt logic | Loops in Langflow require special handling; some loops must stay in code |

### Critical Thinking Questions

1. Complete the translation table as a team. For each artifact from our codebase (system prompt, `chat()` wrapper, chunker, embedder, vector query, critique loop), name the Langflow component or wiring pattern that plays its role.

   *Hint:* Use the table above as a starting point. Open Langflow's component sidebar and look for components whose names match the artifacts. Some artifacts (like the critique loop) will not map to a single component.

2. Which of our patterns has *no* single-component equivalent and must be expressed as graph structure? What does that tell you about what is essential (the underlying pattern) versus incidental (the medium in which it is expressed)?

   *Hint:* A RAG query path requires multiple nodes connected in sequence. A critique-refine loop requires a cycle. Is the difficulty with Langflow about the concept being hard, or about the visual medium not supporting cycles natively?

3. Predict one class of bug that becomes *easier* to find on a canvas than in code, and one that becomes *harder*. Justify both predictions before you test them in the builds below.

   *Hint:* Think about what you can *see* on a canvas that is implicit in code (data flow direction, which nodes are connected). Then think about what you can *inspect* in code that is hidden behind a node's icon (exact prompt text, exception tracebacks).

---

# Part II: Build Sessions

Now that you understand what visual flows are and how they map to code, let's build them — starting simple and adding complexity one layer at a time.

## Model 2: Build 1 — Chat with a Persona

Construct the minimal flow: **Chat Input → Prompt (with your Local Agent Lab persona pasted in) → Ollama → Chat Output**. Run it in the playground and confirm the persona holds across at least three exchanges.

This is the visual equivalent of the four-line `llm()` call you have been writing since *The Agent Loop: Perceive, Plan, Act* activity. Build it first because it has the fewest nodes — any wiring mistake is immediately visible.

## Model 3: Build 2 — RAG over Your RAG Knowledge Base Lab Corpus

Recreate your RAG Knowledge Base Lab pipeline visually. The ingest path is: **File Loader → Text Splitter → Ollama Embeddings → Chroma (ingest mode)**. The query path is: **Chat Input → Chroma (query mode) → Prompt (with your grounding-and-citation instructions) → Ollama → Chat Output**. Use the same chunk size you shipped in the RAG Knowledge Base Lab so you can make a fair comparison.

Note that "ingest" and "query" are the same Chroma node set to different modes — a design detail that is invisible in Python (you call different methods) but explicit on the canvas (you use different Chroma nodes or toggle a mode field).

## Model 4: Build 3 — Export and Reenter Code

Visual flows don't have to stay visual — you can export them and call them from regular Python code, which means your existing test harnesses from earlier labs still work. The snippet below shows exactly how: Langflow runs your flow as a local web service (a **REST API**, meaning a program you talk to over HTTP, just like your Ollama calls), and you send it a question and receive the answer.

Every flow exports as JSON (a text-based data format), and Langflow can serve any flow as a REST API endpoint. Export your RAG flow, open the JSON in a text editor and find your prompt text and chunk size by searching for keywords you used. Then call the flow endpoint from three lines of Python `requests`:

```python
import requests
response = requests.post("http://localhost:7860/api/v1/run/<your-flow-id>",
                         json={"input_value": "What is the main argument in chapter 3?"})
print(response.json()["outputs"][0]["outputs"][0]["results"]["message"]["text"])
```

The visual artifact and your code-world tooling (harnesses, batch evaluation) compose. The endpoint you built with drag-and-drop is callable by your programmatic test harness.

### Critical Thinking Questions

4. Run your RAG Knowledge Base Lab evaluation question set through the Langflow endpoint with your harness from the *Hallucinations and Evaluating Agent Outputs* activity. Do the two implementations score identically? If not, hunt the delta: which knob (chunking, $k$ retrieved documents, prompt wording) silently differs between the Python implementation and the Langflow flow?

   *Hint:* Export the Langflow flow JSON and search for your chunk size value. Is it exactly the same number as in your Python RAG Knowledge Base Lab code? Check the retriever's $k$ parameter (number of documents retrieved) in the Chroma node settings.

5. Time both versions on ten queries. Attribute any latency overhead to a specific cause, and decide whether the difference matters for an interactive chatbot versus a batch processing pipeline.

   *Hint:* Use Python's `time.time()` before and after each query. If Langflow is slower, consider: is it doing the same computation, or is there HTTP overhead from the local API call? Does that matter if a user is waiting 2 seconds versus 0.5 seconds?

6. Hand your canvas to a teammate who did not build it, with no narration allowed. Ask them to explain the system. Try the same with your Python RAG Knowledge Base Lab file. Record the asymmetry honestly: which medium was clearer to a newcomer, and which medium revealed more detail to an expert?

   *Hint:* The Reflector should record specific moments of confusion or clarity. Which medium let the newcomer correctly predict what would happen if you changed the chunk size? Which let the expert find the exact temperature setting used?

The most defensible claim about visual builders versus code for agent systems is:

[( )] Visual builders are for beginners only; code is for professionals who need full capability
[( )] Visual flows cannot implement RAG or tool use because they hide too much from the developer
[(X)] Both express the same underlying patterns; visual excels at communication and rapid wiring, code at version control, testing, and arbitrary logic
[( )] Flows run faster because they skip the overhead of Python interpretation

> **⚠️ Common Misconception:** It is tempting to conclude that visual builders are "easier" and therefore produce systems that are less capable or less rigorous than hand-written code. This is wrong in two directions. First, Langflow can express any pattern that Python can (with the exception of certain dynamic structures like runtime loops). Second, "easier to build" does not mean "easier to audit" — a visually assembled system can be harder to review for security, bias, or correctness than well-structured Python code, because the implementation details are hidden inside opaque node icons. Ease of construction and rigor of understanding are independent dimensions.

---

# Part III: Hands-On Langflow Build (30 minutes)

> **Before starting**: Make sure Langflow is running at `http://localhost:7860`. If not installed, run `pip install langflow && langflow run` in your terminal.

One team member opens `http://localhost:7860` while the Recorder keeps notes on what each component represents and how it maps to Python code from previous labs.

---

### Step 1: Simple Chat (5 minutes)

1. Click **New Flow** → **Blank Canvas**
2. From the left sidebar, drag onto the canvas:
   - **Chat Input** (under Helpers)
   - **Ollama** (under Models) — set Model Name to `llama3.2`, Base URL to `http://localhost:11434`
   - **Chat Output** (under Helpers)
3. Connect: **Chat Input → Ollama → Chat Output** (click the output port of Chat Input, drag to input port of Ollama; repeat for Ollama → Chat Output)
4. Click **Run** (play button at top right)
5. Type a question in the Chat Input field. You should see a response in Chat Output.

**Critical Thinking**: What Python code (from the Local Agent Lab or RAG Knowledge Base Lab) does this three-node flow replace? Write out the equivalent Python in your notes.

> *Hint: The Ollama node calls the same `/api/chat` endpoint you wrote `requests.post(...)` to in the Local Agent Lab. The Chat Input is your `input()` call. The Chat Output is your `print()` call.*

---

### Step 2: Add a System Prompt (5 minutes)

1. Drag a **Prompt** component onto the canvas (under Prompts)
2. In the Prompt's template field, write a system prompt of your choice (use the ROLE/GOAL/TOOLS/FORMAT/GUARDRAILS framework from the Prompt Engineering activity)
3. Connect: **Chat Input → Prompt → Ollama → Chat Output** (remove the direct Chat Input → Ollama connection)
4. Re-run with a question and observe the difference

The Prompt node in Langflow corresponds to which part of your Python agent code?

[( )] The `requests.post()` call to Ollama
[(X)] The system message in the `messages` list (the dict with `"role": "system"`)
[( )] The `parse_response()` function
[( )] The `print()` at the end

> **⚠️ Common Misconception:** Students often assume adding a Prompt node changes what the model "knows." It does not — it changes what *instructions* the model receives at the start of each conversation. The model's weights (its actual knowledge) are fixed; only the prompt changes.

---

### Step 3: Add RAG (15 minutes)

This replicates your RAG Knowledge Base Lab RAG pipeline visually.

1. Drag onto the canvas:
   - **File** component (under Data) — click "Upload File" and upload any short text document (or create a 3-paragraph `.txt` file about any topic)
   - **RecursiveCharacterTextSplitter** (under Processing) — set `chunk_size=500`, `chunk_overlap=50`
   - **Chroma** (under Vector Stores)
   - **OllamaEmbeddings** (under Embeddings) — set Model to `nomic-embed-text`
   - **Retriever** (connected to Chroma)

2. Connect the indexing path: **File → TextSplitter → Chroma**
3. Connect embeddings: **OllamaEmbeddings → Chroma** (for storing) and **OllamaEmbeddings → Retriever** (for querying)
4. Update your Prompt template to include a `{context}` variable:

```text
You are a helpful assistant. Answer questions using ONLY the provided context.
If the answer is not in the context, say "I don't have that information."

Context: {context}
```

5. Connect: **Chat Input → Retriever** (the query path) and **Retriever output → Prompt {context} input**
6. Test with 3 questions: one answerable from the document, one not in the document, and one where the answer is split across two chunks

**Critical Thinking**:

1. In the RAG Knowledge Base Lab, you chose a chunk size and justified it. In Langflow, you see the same parameter in a GUI field. Did you use the same chunk size? What would you need to know to change it?

2. Your RAG Knowledge Base Lab RAG pipeline had explicit code to handle "no relevant chunks found" and return an abstention message. Where in the Langflow flow would you implement this?

   > *Hint: You could add a **Conditional Router** node that checks whether the retriever returned any results before passing context to the Prompt. Or you could handle it in the Prompt template itself with a fallback instruction.*

---

### Step 4: Export and Inspect the JSON (5 minutes)

1. Click the three-dot menu (⋯) at top right → **Export Flow** → save as `rag_flow.json`
2. Open the file and find:
   - The Ollama model configuration (model name, base URL, temperature)
   - The `chunk_size` value you set
   - How edges (connections) are represented in the JSON

**Critical Thinking**: The JSON export is the "source code" for your visual pipeline. Compare it to your RAG Knowledge Base Lab Python code. Which is easier to read? Which is easier to version-control and diff in a tool like `git`?

---

### In-Activity Closing Reflection

Answer these in your Recorder's notes before moving on:

1. List three things Langflow made easier than writing Python code directly.
2. List two things Langflow hides or obscures that a developer should understand.
3. A teammate who does not code says "I can build any AI system now without programming." What would you tell them?

---

# Part IV: Synthesis and Practice

Now that you've built, tested, and exported flows, this part asks you to push those flows to their limits — and to practice explaining them to someone without a programming background.

---

**🛑 In-class work stops here.** The exercises below are homework and going-deeper material — attempt them before the related lab.

## Exercises

1. *Pattern rebuild.*

   *What to do:* Choose one Unit 3 pattern (router, critique-refine, or a two-stage pipeline) and realize it on the Langflow canvas. Capture a screenshot of the working flow with at least one playground transcript showing the expected behavior.

   *Starter hint:* A two-stage pipeline is the simplest: one Prompt+Ollama node for the first stage, whose output feeds a second Prompt+Ollama node. The "router" pattern requires a conditional — look for a "Conditional Router" component in Langflow's sidebar.

   *You've succeeded when:* You can show the screenshot to a teammate who did not build it, and they correctly explain what the flow does without your help.

2. *Limit hunt.*

   *What to do:* Attempt to express your Multi-Agent Patterns Lab debate (n agents, two rounds, majority vote) visually on the canvas. Document precisely where the canvas resists (loops, dynamic fan-out, variable number of agents), and state the general principle about what dataflow graphs express awkwardly.

   *Starter hint:* Dynamic fan-out means "create $n$ parallel paths where $n$ is determined at runtime." Can you wire $n$ Ollama nodes when you do not know $n$ at flow-design time? What does this tell you about the difference between *static* and *dynamic* computation graphs?

   *You've succeeded when:* You can write one precise sentence stating the structural limitation (e.g., "Langflow flows are static graphs; they cannot spawn a variable number of parallel nodes at runtime") and give a concrete example from the debate pipeline that hits this limit.

3. *Stakeholder demo.*

   *What to do:* Prepare a 90-second explanation of your Build 2 RAG flow for a non-programmer (an RA, a club officer, a professor in another department). Deliver it to another team's Reflector and collect one comprehension question you failed to anticipate.

   *Starter hint:* Your explanation should answer: "What does it do? Where does the knowledge come from? What does it NOT know?" Avoid the words "embedding," "vector," and "Chroma." Use analogies: "It's like a search engine that reads your documents before answering."

   *You've succeeded when:* The other team's Reflector asks a question you had not prepared for, you can record that question, and you can improve your explanation to preemptively answer it next time.

---

## Reflection Prompt

*Personal:* Today you wired at least one component (a Text Splitter, a Chroma node, an Embeddings node) without fully reading its source code. Identify that component and describe what you know about what it does, what you are uncertain about, and how you would find out.

*Technical:* Low-code tools reduce the barrier to assembling AI systems. Describe a specific security or correctness risk that is harder to catch in a visually assembled system than in equivalent Python code, and propose a concrete mitigation (a documentation requirement, a code review step, an automated test).

*Societal:* Low-code tools widen who can build AI systems, including people who cannot audit the components they wire together. Is that democratization, risk, or both? Anchor your answer in one specific thing you wired today that you did not fully understand, and describe what harm could result if someone deployed that component in a high-stakes setting without understanding it.

---

→ Coming Up Next: In the *Evaluating Agents: LLM-as-Judge and Rubric Pipelines* activity, we measure agent output quality at scale — which requires recruiting a model to act as the judge of other models' outputs.

## Further Reading

- Langflow documentation: https://docs.langflow.org
- Ollama integration guide within the Langflow docs (component reference).
- Victor, Bret. "Learnable Programming" (2012, online essay), on representations that make systems visible and understandable.
