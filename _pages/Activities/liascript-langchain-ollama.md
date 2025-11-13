<!--
author:   William M. Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-langchain-ollama.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-langchain-ollama.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap
-->

# LangChain, Ollama, & Multi-Agent LLM Systems

William M. Mongan  
Department of Mathematics, Computer Science, and Statistics

---

## Agenda & Learning Objectives

**Goals**

- Understand how LangChain interfaces with **Ollama** over arbitrary `base_url` endpoints.
- Implement **raw LLM chat**, **tool calling**, and **RAG** using a local directory of documents.
- Explore **function tools** and safe Python execution (e.g., product computation).
- Construct a **supervisor-based multi-agent system** that delegates to specialized agents.
- Discuss architectural patterns, evaluation, scaling, and safety considerations.

---

## Slide Map (You Are Here)

1. LangChain–Ollama Basics  
2. Raw Chat Pipeline  
3. Tool Calling Framework  
4. Implementing a `multiply(a,b)` tool  
5. Document Loading & Chunking  
6. Embeddings and Vector Stores  
7. RAG Pipeline Assembly  
8. Sub-agents: calculator & researcher  
9. Supervisor LLM pattern  
10. Multi-agent orchestration  
11. Evaluation & Diagnostics  
12. Extensions (memory, routing, streaming)  
13. Ethics & operational safety  

---

## 1) LangChain + Ollama: Architectural Overview

**Ollama** exposes HTTP endpoints serving local or remote models.  
LangChain provides structured composition: chat models, tools, retrievers, and agents.

```
User → PromptTemplate → ChatOllama → (tool calls / RAG) → Output
```

---

## Open Colab: Langchain Tutorial

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BillJr99/Ursinus-CS357/blob/gh-pages/files/notebooks/langchain_ollama_multiagent_tutorial.ipynb)

---

## 2) Raw Chat Chain: Minimal Pipeline

A runnable chain:

```
PromptTemplate → ChatOllama → StrOutputParser
```

Mathematically:

$$
	ext{Output} = R(M(P(	ext{question})))
$$

---

## 3) Tool Calling: Why

Tools give controlled execution for:

- Math  
- Database queries  
- Environment operations  
- Other agents  

LLMs emit JSON-like tool call objects.

---

## 4) Example Tool: multiply(a,b)

```python
@tool
def multiply(a: int, b: int) -> int:
    return a * b
```

LLM emits call → Python executes → result returned as ToolMessage → final LLM synthesis.

---

## 5) Loading Docs for RAG

Use DirectoryLoader:

```python
loader = DirectoryLoader("docs/", glob="**/*.txt", loader_cls=TextLoader)
docs = loader.load()
```

Split into overlapping chunks for retrieval.

---

## 6) Embeddings & Chroma Vector Store

```python
emb = OllamaEmbeddings(model="llama3")
vs = Chroma.from_documents(chunks, emb)
retriever = vs.as_retriever(k=4)
```

Similarity search returns top‑k relevant chunks.

---

## 7) RAG Prompt Composition

```
Question: {question}

Context:
{context}
```

Pipeline:

$$
Q 
ightarrow C 
ightarrow M 
ightarrow \hat{A}
$$

---

## 8) Sub-Agents

### Calculator Agent
Uses tool-aware model (multiply).

### Research Agent
Wraps RAG chain for document-grounded answers.

---

## 9) Supervisor LLM Pattern

Supervisor routes queries:

- math → calculator_subagent  
- document → research_subagent  
- otherwise → direct answer  

Uses LLM-as-router (similar to MoE gating).

---

## 10) Multi-Agent Orchestration Diagram

```
Query → Supervisor → (Calculator | Research Agent)
                             ↓
                        Tool or RAG
                             ↓
                  Supervisor Synthesis → Answer
```

---

## 11) Evaluation & Diagnostics

Check:

- Tool invocation correctness  
- Retrieval grounding  
- Routing accuracy  
- Latency vs. interpretability  

---

## 12) Extensions

- Conversational memory  
- Advanced retrievers (hybrid)  
- Streaming responses  
- Additional specialized agents  
- Remote multi-node Ollama clusters  

---

## 13) Ethics & Operational Safety

Concerns:

- Over-reliance on tool autonomy  
- Unauthorized document access  
- Embedded model biases  
- Supervisor misrouting  

**Prompt:**  
Draft a safety policy restricting LLM tool access in your lab.

{{1}}

---

## 14) Activity Checklist

1. Connect to Ollama instance  
2. Run raw chat  
3. Add multiply tool  
4. Build RAG index  
5. Create calculator & research agents  
6. Implement supervisor  
7. Test routing on diverse queries  

---

## 15) LangChain Handoffs: Conceptual Overview

“Handoffs” refer to the **controlled transfer of conversational state, context, or execution responsibility** between distinct agents, chains, or workflows inside LangChain.

A handoff is appropriate when:

- A query transitions between **domains** (e.g., math → research).
- A conversation phase changes (e.g., clarification → execution).
- A task must be escalated to another agent with specialized tools.
- A pipeline performs **multi-stage transformations** (e.g., rewrite → retrieve → synthesize).

Handoffs help maintain:

- **Traceability**
- **Task locality**
- **Role specialization**
- **Error isolation**

---

## 16) Formalizing a Handoff

Let:

- \(A_1, A_2, \dots, A_n\) be agents.
- Each agent implements:

\[
A_i: (H, u) \mapsto (r, H')
\]

where  
- \(H\) = conversation history,  
- \(u\) = user input,  
- \(r\) = agent response or tool call,  
- \(H'\) = updated history.

A **handoff** is:

\[
\text{handoff}: (A_i, r, H') \mapsto (A_j, H'')
\]

LangChain implements this using:

- **Runnables** (`RunnableBranch`, `RunnableParallel`, `RunnableSequence`)
- **Agents + tools**
- **Router chains**
- **Supervisor LLMs**

---

## 17) Example: Clarification → Execution Handoff

Two-agent pattern:

1. **Clarifier agent**  
   - Interprets or verifies user intent.  
   - Reformulates ambiguous questions.  
   - Produces a canonical task specification.

2. **Executor agent**  
   - Performs math, data retrieval, RAG, tool calls, or structured actions.

Workflow:

```
User Query → Clarifier → Handoff → Executor → Final Answer
```

This separates *understanding* from *acting*.

---

## 18) Handoff via RouterChain

Use LLM classification to choose the next agent.

Routing prompt example:

```
Decide which specialist should answer:
- math_agent
- research_agent
Return ONLY the agent name.
```

Then:

```
router.invoke(question) → "math_agent"
math_agent.invoke(question)
```

This is a clean, declarative handoff.

---

## 19) Handoff via Tool Calls (Supervisor Model)

Supervisor LLM emits a tool call:

```json
{
  "tool": "research_subagent",
  "arguments": {"query": "Summarize the documents on privacy."}
}
```

Developer code:

1. Executes the sub-agent.  
2. Wraps its result in a ToolMessage.  
3. Returns it to the supervisor for synthesis.

This forms a **two-step handoff loop**.

---

## 20) Handoff via RunnableBranch

Pure programmatic routing:

```python
chain = RunnableBranch(
    (lambda x: "math" in x.lower(), math_chain),
    (lambda x: True, research_chain),  # fallback
)
```

Pros: deterministic, robust  
Cons: less flexible than LLM-based routing

---

## 21) Preserving Context Across Handoffs

Strategies:

1. **Full history transfer** — complete but expensive.
2. **Summarized history** — cheaper; improves focus.
3. **Task-specific context** — only relevant parts of conversation.
4. **Hidden metadata state** — not exposed to LLM but preserved in flow.

Handling context carefully prevents error propagation.

---

## 22) State Transformation Handoff

Sometimes the output of one agent must be transformed before another agent can act.

Examples:

- Natural language → numeric parameters  
- Free text → SQL  
- Query → RAG-ready search terms  
- Summary → structured schema

Formally:

\[
T: r_i \rightarrow u_j
\]

Implementations with:

- `RunnableLambda`
- Pydantic models
- Output parsers

---

## 23) Multi-Step Handoffs (Pipeline Architecture)

Example pipeline:

```
User → Intent Classifier
        │
        ├─► Math Agent
        └─► Rewrite → Retriever → Synthesizer
```

Each stage has:

- defined responsibilities  
- strict input/output schemas  
- corresponding handoff rules  

---

## 24) Failure Modes & Diagnostics

Issues:

- Incorrect routing  
- Missing context  
- Overlong transcripts  
- Hallucinated tool names  
- Malformed agent output  

Mitigations:

- Add guardrails to router prompts  
- Validate tool schemas  
- Log and trace decision flow  
- Summaries before handoff  
- Default fallback agents

---

## 25) Design Heuristics for Reliable Handoffs

- Keep agents **highly specialized**.  
- Make routing categories **mutually exclusive**.  
- Use programmatic routing for safety-critical decisions.  
- Use structured schemas everywhere.  
- Compress history before transitions.  
- Test routing using adversarial prompts.

---

## 26) Activity: Build a Two-Agent Handoff System

**Goal:** Implement a clarifier → executor handoff.

Tasks:

1. Create:
   - `rewriter_agent`
   - `answer_agent`
2. Implement a router or supervisor to choose which agent receives each message.
3. Add logging to inspect routing decisions.
4. Evaluate correctness with multiple queries.

**Deliverable:**  
Short demonstration showing one successful handoff of each type.

---

## References

- LangChain Documentation  
- Ollama API Reference  
- Lewis et al. (2020) Retrieval-Augmented Generation  
- OpenAI Function-Calling Papers
