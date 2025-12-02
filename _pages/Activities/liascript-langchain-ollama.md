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
\rightarrow C 
\rightarrow M 
\rightarrow \hat{A}
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

---

## Example LangChain Agent System: A Student Course Planner

- We will use **LangChain** to:
  - load a **PDF catalog** and build a simple RAG retriever,
  - define **three agents** (implemented as three specialized LLM functions):
    1. **Catalog agent**: builds a term-by-term plan using the catalog.
    2. **Interests agent**: suggests majors/minors based on interests.
    3. **Checker agent**: reconciles the two and checks for errors.
- Orchestrate them in a **single function** with **one user input** and **one final output**.
- Embed an **internal log of intra-agent messages** into the output.
- Wrap everything in a **Gradio UI**.

---

### 1. Imports and global setup

```python
import os
from typing import List, Tuple

import gradio as gr

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import SystemMessage, HumanMessage
```

**Explanation**

- `ChatOpenAI` and `OpenAIEmbeddings` are the OpenAI-flavored LangChain wrappers.
- `PyPDFLoader` + `RecursiveCharacterTextSplitter` + `FAISS` give us a basic RAG stack over your catalog PDF.
- We use `SystemMessage` and `HumanMessage` to define prompts for each agent.
- Gradio provides the simple web UI wrapper.

You’ll need an `OPENAI_API_KEY` in your environment for this to work.

---

### 2. Build the catalog retriever from a PDF

This runs once at startup and is reused across calls.

```python
CATALOG_PATH = "./data/course_catalog.pdf"  # <-- put your catalog here


def build_catalog_retriever(pdf_path: str):
    """
    Load the catalog PDF, chunk it, embed it, and create a retriever.
    In a real system, you would likely persist the vector store to disk.
    """
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    splits = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectordb = FAISS.from_documents(splits, embeddings)

    retriever = vectordb.as_retriever(search_kwargs={"k": 8})
    return retriever
```

**Explanation**

- `build_catalog_retriever` is a simple RAG setup:
  - loads the PDF,
  - splits into overlapping chunks,
  - builds a FAISS index over embeddings,
  - exposes a retriever that we’ll query from the **catalog agent**.
- For a real deployment, you’d likely save the FAISS index to disk and reload it, rather than rebuilding on every run.

---

### 3. Initialize the shared LLM and retriever

```python
# Initialize LLM and retriever at module import time so Gradio
# can reuse them for multiple calls.
llm = ChatOpenAI(
    model="gpt-4o-mini",  # or "gpt-4o" etc.
    temperature=0.2
)

catalog_retriever = build_catalog_retriever(CATALOG_PATH)
```

**Explanation**

- We use a single `llm` instance for all three agents; they differ by **prompt**, not by model.
- `temperature=0.2` keeps behavior mostly deterministic while allowing minor variation.

---

### 4. Agent 1 — Catalog agent (term-by-term planner)

```python
def run_catalog_agent(student_profile: str, num_terms: int = 8) -> Tuple[str, List[str]]:
    """
    Agent 1: Reads from the catalog retriever and produces a term-by-term plan.

    Returns:
        plan_markdown: human-readable term-by-term plan.
        logs: list of log strings documenting internal behavior.
    """
    logs: List[str] = []

    # Ask the retriever for catalog sections that are likely relevant.
    retrieval_query = (
        "Degree requirements, prerequisites, allowed course loads per term, "
        "and sample four-year plans that might be relevant to the following student. "
        "Focus on majors/minors and general education requirements.\n\n"
        f"Student profile:\n{student_profile}"
    )
    docs = catalog_retriever.get_relevant_documents(retrieval_query)
    logs.append(
        f"[Catalog agent] Retrieved {len(docs)} catalog chunks for planning."
    )

    catalog_context = "\n\n---\n\n".join(d.page_content for d in docs)

    system_prompt = (
        "You are an academic planning agent that specializes in satisfying degree "
        "requirements term-by-term using the official course catalog. "
        "Given catalog excerpts and a student profile, you must propose a term-by-term "
        "course plan for the next N terms.\n\n"
        "Constraints:\n"
        "- Respect prerequisite chains as described in the catalog when possible.\n"
        "- Aim for a reasonable load (e.g., 3–5 courses or ~12–18 credits per term).\n"
        "- Ensure that the student is making progress toward at least one plausible major.\n"
        "- Cover general education / core requirements when they are mentioned.\n"
        "- If information is missing, state your assumptions explicitly.\n"
        "Output a clear Markdown outline with headings per term."
    )

    user_prompt = (
        f"CATALOG EXCERPTS:\n\n{catalog_context}\n\n"
        f"STUDENT PROFILE:\n{student_profile}\n\n"
        f"Plan for the next {num_terms} terms. "
        "Name each term (e.g., 'Year 1 – Fall') and list courses as bullet points "
        "with brief notes on how they contribute to requirements."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    plan = response.content
    logs.append("[Catalog agent] Generated a draft term-by-term plan.")

    return plan, logs
```

**Explanation**

- This agent treats the catalog as its **ground truth**:
  - It queries the retriever with a combined question using the student profile.
  - It gets back relevant chunks and inserts them directly into its prompt as context.
- The output is **Markdown**, structured by term, which will be used by the checker.

---

### 5. Agent 2 — Interests agent (majors and minors recommender)

```python
def run_interests_agent(student_profile: str) -> Tuple[str, List[str]]:
    """
    Agent 2: Takes student interests and background and recommends majors/minors.

    Returns:
        rec_markdown: description of recommended majors/minors and rationale.
        logs: list of log strings documenting internal behavior.
    """
    logs: List[str] = []

    system_prompt = (
        "You are an academic interests advisor. Your job is to read a student's "
        "interests, goals, constraints, and background, and then recommend:\n"
        "- 2–3 likely majors\n"
        "- 1–2 possible minors or certificates\n\n"
        "You should explicitly justify each recommendation in terms of the student's "
        "interests and goals. You don't need to know the exact catalog; imagine a "
        "typical comprehensive university with a broad set of majors."
    )

    user_prompt = (
        "Read the following student profile and propose majors/minors:\n\n"
        f"{student_profile}\n\n"
        "Output:\n"
        "1. A short narrative describing the student's goals.\n"
        "2. A ranked list of recommended majors with explanations.\n"
        "3. A list of possible minors/certificates with explanations.\n"
        "4. Any explicit constraints (e.g., time-to-degree, work schedule) you infer."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    recommendations = response.content
    logs.append("[Interests agent] Recommended majors and minors based on profile.")

    return recommendations, logs
```

**Explanation**

- This agent is “catalog-agnostic”: it imagines a typical university and focuses on **fit to interests**.
- The result is a structured Markdown description of majors/minors plus rationales.

---

### 6. Agent 3 — Checker agent (consistency and error checking)

```python
def run_checker_agent(
    student_profile: str,
    catalog_plan_markdown: str,
    interests_markdown: str,
) -> Tuple[str, List[str]]:
    """
    Agent 3: Cross-checks the catalog-driven plan and the interest-based
    major/minor recommendations, and produces a final, reconciled recommendation.

    Returns:
        final_markdown: final, checked recommendation and plan.
        logs: list of log strings documenting internal behavior.
    """
    logs: List[str] = []

    system_prompt = (
        "You are a critical academic planning auditor. You receive:\n"
        "1. A term-by-term course plan generated from the catalog.\n"
        "2. A set of recommended majors/minors generated from the student's interests.\n\n"
        "Your tasks:\n"
        "- Check for obvious inconsistencies (e.g., plan ignores student's stated goals, "
        "or seems incompatible with recommended majors/minors).\n"
        "- Identify missing prerequisites or unrealistic assumptions if they are visible "
        "from the provided plan.\n"
        "- Suggest corrections or refinements.\n"
        "- Produce a final, reconciled recommendation for the student that clearly "
        "summarizes:\n"
        "  * The likely major(s) and minor(s) you recommend.\n"
        "  * Any changes you would make to the term-by-term plan.\n"
        "  * Key caveats and follow-up questions the student should discuss with a "
        "    human advisor.\n\n"
        "Be explicit about what you are changing and why."
    )

    user_prompt = (
        "STUDENT PROFILE:\n"
        f"{student_profile}\n\n"
        "CATALOG-DRIVEN TERM-BY-TERM PLAN:\n"
        f"{catalog_plan_markdown}\n\n"
        "INTEREST-BASED MAJOR/MINOR RECOMMENDATIONS:\n"
        f"{interests_markdown}\n\n"
        "Now produce your analysis and final reconciled recommendation as Markdown, "
        "using headings:\n"
        "## Summary\n"
        "## Consistency Check\n"
        "## Suggested Adjustments to the Plan\n"
        "## Final Recommended Majors / Minors\n"
        "## Caveats and Next Steps"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    final_recommendation = response.content

    logs.append("[Checker agent] Performed consistency check and produced final recommendation.")

    return final_recommendation, logs
```

**Explanation**

- This agent is the **arbiter**:
  - Receives the outputs of both previous agents and the original student profile.
  - Analyzes consistency, flags potential problems, and outputs a **single, reconciled recommendation**.
- We structure the desired headings directly in the prompt to keep the output predictable.

---

### 7. Orchestrator — single entry point with internal logging

This is the function that Gradio will call. It:

1. Gets the user’s description/profile,
2. Calls the three agents in sequence,
3. Concatenates their logs,
4. Returns a **single Markdown string** that includes:
   - the final recommendation first,
   - then an internal log of intra-agent messages.

```python
def advise_student_single_input(student_profile: str) -> str:
    """
    High-level function: one input (student_profile), one output (Markdown).
    Internally orchestrates three agents, and appends an agent log.

    This is the function we expose through Gradio.
    """
    all_logs: List[str] = []
    all_logs.append("[Orchestrator] Starting multi-agent advising run.")
    all_logs.append(f"[Orchestrator] Received student profile:\n{student_profile}")

    # 1. Catalog agent: term-by-term plan.
    catalog_plan, log1 = run_catalog_agent(student_profile)
    all_logs.extend(log1)

    # 2. Interests agent: majors/minors recommendations.
    interests_recs, log2 = run_interests_agent(student_profile)
    all_logs.extend(log2)

    # 3. Checker agent: reconcile and verify.
    final_recommendation, log3 = run_checker_agent(
        student_profile,
        catalog_plan_markdown=catalog_plan,
        interests_markdown=interests_recs,
    )
    all_logs.extend(log3)
    all_logs.append("[Orchestrator] Completed multi-agent advising run.")

    # Prepare a single combined Markdown output:
    log_text = "\n".join(all_logs)

    output_markdown = (
        "## Final Checked Recommendation\n\n"
        f"{final_recommendation}\n\n"
        "---\n\n"
        "### Internal Agent Log (debugging / provenance)\n\n"
        "```text\n"
        f"{log_text}\n"
        "```"
    )

    return output_markdown
```

**Explanation**

- From the UI’s perspective this is **just a function from string → string**.
- Internally we collect a simple **log list** describing:
  - what each agent did,
  - at a very coarse level (you can add more detailed logging if you like, e.g., recording prompts, truncating them, etc.).
- The result is a single Markdown output, which satisfies your “single input / single output” requirement while still surfacing **intra-agent messages**.

---

### 8. Gradio interface

Finally, we wire it up with Gradio:

```python
def build_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Term-by-Term Course Planning — Multi-Agent Demo")

        gr.Markdown(
            "Describe yourself, your academic history, constraints, and interests. "
            "The system will build a term-by-term plan from the catalog, "
            "recommend majors/minors, and then reconcile them."
        )

        profile_input = gr.Textbox(
            label="Student profile and interests",
            placeholder=(
                "Example: I am a second-year student who has completed Calc I and II, "
                "intro CS, and first-year writing. I am interested in machine learning, "
                "ethics, and possibly a minor in philosophy. I can handle 4 courses per term."
            ),
            lines=8,
        )

        output_md = gr.Markdown(label="Final Recommendation and Agent Log")

        run_button = gr.Button("Generate Plan")

        run_button.click(
            fn=advise_student_single_input,
            inputs=profile_input,
            outputs=output_md,
        )

    return demo


if __name__ == "__main__":
    # Ensure your OPENAI_API_KEY is set before running.
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY is not set. Set it before running this script.")
    app = build_interface()
    app.launch()
```

**Explanation**

- Gradio provides a **single text input** and a **single Markdown output**.
- The output includes both the reconciled recommendation and the internal log of intra-agent messages.
- The catalog PDF is **not a user input**; it is a fixed resource on the server (`CATALOG_PATH`).

---

## Runnable DAG Variant with Gradio File Upload

In this section, we sketch a more **LangChain Expression Language / Runnable DAG-style** orchestration. The idea is to:

- Keep the same **three conceptual agents**.
- Compose them as **Runnables** into a small DAG.
- Allow the catalog to come either from:
  - a **static file path** (default), or
  - an **uploaded PDF file** via Gradio.

For brevity, we will assume that:

- The implementations of `run_catalog_agent`, `run_interests_agent`, and `run_checker_agent` from the earlier slides are available.
- We slightly generalize `build_catalog_retriever` so we can call it with an arbitrary path (static or uploaded).

---

### 1. Generalizing the catalog retriever

We already have:

```python
CATALOG_PATH = "./data/course_catalog.pdf"  # static fallback
```

We can use the same `build_catalog_retriever` function, but call it with either the static path or the uploaded file path in the Gradio callback.

---

### 2. Defining Runnables for each agent

Here is a simple way to wrap each Python-based agent in a `RunnableLambda` so we can compose them in a DAG-like way. We will also let the orchestrator handle logging, similar to before, but now expressed in a pipeline style.

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

def make_catalog_runnable():
    # This Runnable expects {"student_profile": str, "num_terms": int, "retriever": Any}
    # Here, for simplicity, we assume the global catalog_retriever is already set,
    # but you could also use the "retriever" field from inputs if you want to vary it.
    return RunnableLambda(
        lambda inputs: run_catalog_agent(
            student_profile=inputs["student_profile"],
            num_terms=inputs.get("num_terms", 8),
        )
    )

def make_interests_runnable():
    # Expects {"student_profile": str}
    return RunnableLambda(
        lambda inputs: run_interests_agent(inputs["student_profile"])
    )

def make_checker_runnable():
    # Expects:
    # {
    #   "student_profile": str,
    #   "catalog_result": (plan_markdown, logs1),
    #   "interests_result": (recs_markdown, logs2)
    # }
    return RunnableLambda(
        lambda inputs: run_checker_agent(
            student_profile=inputs["student_profile"],
            catalog_plan_markdown=inputs["catalog_result"][0],
            interests_markdown=inputs["interests_result"][0],
        )
    )
```

---

### 3. Building the Runnable DAG

We can construct a small pipeline where the input is a dictionary:

- `"student_profile"` (required),
- `"num_terms"` (optional, default 8).

The DAG:

1. Computes the catalog and interests outputs in parallel.
2. Feeds both into the checker runnable.
3. Collects all logs and returns a single Markdown string.

```python
from langchain_core.runnables import RunnableParallel

def build_multi_agent_dag():
    catalog_runnable = make_catalog_runnable()
    interests_runnable = make_interests_runnable()
    checker_runnable = make_checker_runnable()

    # First stage: run catalog and interests in parallel.
    parallel_stage = RunnableParallel(
        catalog_result=catalog_runnable,
        interests_result=interests_runnable,
        student_profile=RunnablePassthrough()  # pass through unchanged
    )

    # Second stage: checker uses outputs from the first stage.
    def checker_with_logs(inputs):
        student_profile = inputs["student_profile"]
        catalog_result = inputs["catalog_result"]
        interests_result = inputs["interests_result"]

        catalog_plan, log1 = catalog_result
        interests_recs, log2 = interests_result

        final_recommendation, log3 = run_checker_agent(
            student_profile=student_profile,
            catalog_plan_markdown=catalog_plan,
            interests_markdown=interests_recs,
        )

        all_logs = []
        all_logs.append("[Orchestrator] Starting DAG-based multi-agent run.")
        all_logs.append(f"[Orchestrator] Received student profile:\n{student_profile}")
        all_logs.extend(log1)
        all_logs.extend(log2)
        all_logs.extend(log3)
        all_logs.append("[Orchestrator] Completed DAG-based multi-agent run.")

        log_text = "\n".join(all_logs)

        output_markdown = (
            "## Final Checked Recommendation (DAG pipeline)\n\n"
            f"{final_recommendation}\n\n"
            "---\n\n"
            "### Internal Agent Log (debugging / provenance)\n\n"
            "```text\n"
            f"{log_text}\n"
            "```"
        )
        return output_markdown

    final_stage = RunnableLambda(checker_with_logs)

    # Combine: input -> parallel_stage -> final_stage.
    dag = parallel_stage | final_stage
    return dag
```

**Notes**

- `RunnableParallel` runs `catalog_runnable` and `interests_runnable` side by side.
- The `checker_with_logs` function is responsible for:
  - calling `run_checker_agent`,
  - merging logs,
  - producing the final Markdown.
- The overall DAG is a **Runnable** that you can `invoke()` with a dictionary.

---

### 4. Gradio interface with file upload (plus static fallback)

Now we define a Gradio app that:

- Lets the user enter the **student profile**.
- Optionally upload a **catalog PDF**.
- Builds a retriever from either:
  - the uploaded file (if provided), or
  - the static `CATALOG_PATH` (fallback).
- Then uses the DAG to produce a single Markdown output.

```python
def advise_with_dag_and_upload(student_profile: str, catalog_file) -> str:
    # Decide which PDF to use: uploaded or static fallback.
    if catalog_file is not None:
        pdf_path = catalog_file.name  # temporary path where Gradio saved the file
    else:
        pdf_path = CATALOG_PATH

    # Rebuild (or load) the catalog retriever for this path.
    # For efficiency in production, you would cache or persist this.
    global catalog_retriever
    catalog_retriever = build_catalog_retriever(pdf_path)

    # Build the DAG using the current (global) retriever.
    dag = build_multi_agent_dag()

    # Invoke the DAG with the student profile.
    result_markdown = dag.invoke(
        {
            "student_profile": student_profile,
            "num_terms": 8,
        }
    )
    return result_markdown
```

And the corresponding Gradio UI:

```python
def build_interface_with_upload():
    with gr.Blocks() as demo:
        gr.Markdown("# Term-by-Term Course Planning — DAG-Based Multi-Agent Demo")

        gr.Markdown(
            "Describe yourself, your academic history, constraints, and interests. "
            "Optionally upload a PDF of the course catalog to use as the source "
            "for requirements and sample plans. If you do not upload a file, "
            "the app will use the static CATALOG_PATH defined in the code."
        )

        profile_input = gr.Textbox(
            label="Student profile and interests",
            placeholder=(
                "Example: I am a second-year student who has completed Calc I and II, "
                "intro CS, and first-year writing. I am interested in machine learning, "
                "ethics, and possibly a minor in philosophy. I can handle 4 courses per term."
            ),
            lines=8,
        )

        catalog_upload = gr.File(
            label="Upload course catalog PDF (optional)",
            file_types=[".pdf"],
        )

        output_md = gr.Markdown(label="Final Recommendation and Agent Log (DAG-based)")

        run_button = gr.Button("Generate Plan (DAG)")

        run_button.click(
            fn=advise_with_dag_and_upload,
            inputs=[profile_input, catalog_upload],
            outputs=output_md,
        )

    return demo


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY is not set. Set it before running this script.")

    # Choose which interface you want to launch:
    # 1. Function-based orchestrator with static catalog:
    # app = build_interface()

    # 2. DAG-based orchestrator with optional file upload:
    app = build_interface_with_upload()

    app.launch()
```

**Key points**

- The **static catalog path** is still present (`CATALOG_PATH`), so you can run this without any upload.
- When a **file is uploaded**, `advise_with_dag_and_upload` rebuilds the retriever from that file path.
- The **Runnable DAG** (`build_multi_agent_dag`) orchestrates the three agents, with catalog and interests stages in parallel, followed by a checker stage.

---
