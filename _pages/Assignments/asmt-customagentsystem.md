
---
layout: assignment
permalink: Assignments/CustomAgentSystem
title: "Assignment: Custom Agent Systems - LangFlow (Part 1) + LangChain (Part 2)"

info:
  points: 100
  goals:
    - "Develop a working understanding of agentic systems using both a no‑code canvas (LangFlow) and a programmatic library (LangChain)."
    - "Construct Retrieval‑Augmented Generation (RAG) pipelines and/or tool‑enabled agents in LangFlow."
    - "Design and implement a custom agent using LangFlow with either external tools (APIs/functions) or a document corpus."
    - "Build an equivalent or complementary custom agent in LangChain (Python), using tools and/or RAG."
    - "Critically evaluate UX, ethics, and reliability of agentic systems."

  rubric:
    - weight: 15
      description: Implementation and Functionality of Solutions (LangFlow + LangChain)
      preemerging: Solutions fail to run end‑to‑end or exhibit major errors.
      beginning: Solutions run with limited capability; minimal customization.
      progressing: Solutions are functional with moderate customization and sound architecture.
      proficient: Solutions are robust, thoughtfully engineered, and demonstrate innovative customization.
    - weight: 20 
      description: Human‑Centric Design & Usability
      preemerging: Interface and interaction affordances are unclear or non‑existent.
      beginning: Basic UX present, but guidance and affordances are inconsistent.
      progressing: Mostly clear user interactions with minor ambiguities; evidence of informal testing.
      proficient: Cohesive UX with deliberate affordances; evidence‑based refinements from testing.
    - weight: 20
      description: Design Report      
      preemerging: No design report included.
      beginning: Report summarizes approach superficially; limited discussion of alternatives.
      progressing: Report analyzes trade‑offs for one stakeholder and documents design choices.
      proficient: Report synthesizes requirements, architecture, testing, and stakeholder perspectives with traceability.
    - weight: 15
      description: Reflective Write‑Up on Personalization and Usability
      preemerging: Absent or purely descriptive.
      beginning: Basic reflection with few concrete examples.
      progressing: Substantive reflection with relevant examples and analysis.
      proficient: Insightful, evidence‑backed reflection that connects design decisions to user outcomes.
    - weight: 10
      description: Ethics, Safety, and Responsible Use
      preemerging: Minimal or generic ethical commentary.
      beginning: Identifies key issues but lacks practical mitigations.
      progressing: Discusses risks, mitigations, and monitoring strategies.
      proficient: Thorough risk analysis including abuse cases, data governance, consent, transparency, and evaluation plans.
    - weight: 20
      description: Creation and Customization of Agents and Tools
      preemerging: Limited understanding of agents/tools and composition.
      beginning: Can create basic agents and connect tools with little customization.
      progressing: Competently composes agents, tools, and memory/RAG with moderate complexity.
      proficient: Designs sophisticated agent/tool ecosystems with testing, observability, and failure‑mode handling.

  readings:
    - rtitle: "LangFlow Documentation"
      rlink: "https://docs.langflow.org/"
    - rtitle: "LangChain Python - Agents"
      rlink: "https://python.langchain.com/docs/modules/agents/"
    - rtitle: "LangChain - Tools Integrations"
      rlink: "https://python.langchain.com/docs/integrations/tools/"
    - rtitle: "LangChain - Ollama Provider"
      rlink: "https://docs.langchain.com/oss/python/integrations/providers/ollama"
    - rtitle: "JSON‑Based Agents with LangChain (blog)"
      rlink: "https://blog.langchain.com/json-based-agents-with-ollama-and-langchain/"

tags:
  - ai
  - agents
  - rag
  - langflow
  - langchain

---

In recent years, AI has evolved from single‑turn chat to *agentic systems* capable of planning, invoking tools, retrieving knowledge, and orchestrating multi‑step workflows. This lab guides you through building parallel implementations of a custom agent system using **LangFlow** (a visual, no‑code canvas) and **LangChain** (a Python framework).

> **Source tutorials used to structure this lab (watch first):**
> 1. *Build a RAG Based LLM App in 20 Minutes! | Full LangFlow Tutorial* [(YouTube, LangFlow RAG walk‑through)](https://www.youtube.com/watch?v=rz40ukZ3krQ)
> 2. *ADVANCED Python AI Agent Tutorial - Using RAG, LangFlow* [(YouTube, multi‑agent & advanced LangFlow concepts)](https://www.youtube.com/watch?v=QmUsG_3wHPg)
> 3. *How to Build a Local AI Agent with Python (Ollama, LangChain & RAG)* [(YouTube, local agents with LangChain + Ollama)](https://www.youtube.com/watch?v=E4l91XKQSgw)

---

## Part 1 - LangFlow Tutorial (Canvas‑First)

### 1.1  Installation & Project Setup
- Install and run LangFlow (latest stable):
  ```bash
  pip install langflow
  langflow run
  ```
  LangFlow launches a local web UI (default: `http://127.0.0.1:7860`). Create a new **Project** and **Flow**.

- Recommended data and keys:
  - Pick an LLM provider (e.g., OpenAI, OpenRouter, or local via Ollama). Configure in **Settings → Environment**.
  - Prepare a small document corpus (e.g., PDFs or Markdown) for RAG testing. Place files under a `data/` folder.

### 1.2  Core Building Blocks (from the RAG video structure)【rz40ukZ3krQ】
- **Inputs/Outputs:** `ChatInput` → `ChatOutput`.
- **LLM:** Connect a `ChatModel` node (e.g., GPT‑4‑o, Llama‑3 via Ollama).
- **Text Preprocessing:** `TextLoader` → `TextSplitter` (e.g., RecursiveCharacterSplitter).
- **Indexing:** `Embeddings` → `VectorStore` (FAISS/Chroma) with `VectorStoreRetriever`.
- **Prompting:** `Prompt`/`ChatPrompt` with system + user blocks.
- **RAG Chain:** Wire `Retriever` + `LLM` with a `Stuff/RAG` node (or `RetrievalChain`).

**Checklist:** Load documents → split → embed → index → retrieve top‑k → compose prompt → generate.

### 1.3  Adding Tools & Multi‑Agent Concepts (advanced video)【QmUsG_3wHPg】
- **Tools:** Use LangFlow’s *Tool* components (e.g., Python function, web search, HTTP) and connect to the agent/LLM via a `ToolNode`.
- **Agents:** Add an `Agent` node (ReAct/Tool‑Calling style). Provide it a toolset. Configure stop conditions and observation formatting.
- **Memory:** Add a `ChatHistory`/`Memory` component for longer sessions.
- **Orchestration Tips:**
  - Keep tools pure and idempotent; log inputs/outputs to a `Console` node.
  - Guard calls with validation prompts; include tool schemas and preconditions.

### 1.4  Minimal RAG Flow (you implement)
1. **Nodes:** `TextLoader` → `TextSplitter` → `Embeddings` → `VectorStore` → `Retriever`  
2. **Chain:** `ChatPrompt` (system: *answer strictly from sources*; user: `{question}` + citations), connect to `LLM`.  
3. **Wire:** `ChatInput → Retriever + Prompt → LLM → ChatOutput`.  
4. **Test:** Ask: *Summarize the late‑breaking policy in document X and cite chunks.* Confirm sources.

### 1.5  Minimal Tool‑Using Agent (you implement)
1. Create a **Python Function Tool**: e.g., `def get_weather(city): ...` or a domain API.
2. Register the tool node; connect to `Agent (ReAct/Tools)` with your LLM.
3. Prompt the agent to decide between **RAG** vs **Tool** given the query. Inspect the tool call trace.

### 1.6  Deliverable A - Custom LangFlow System
Build and demo **one** of the following (or propose your own):
- **RAG Advisor:** Upload a curated corpus (e.g., policies, syllabi, handbooks) and answer questions with citations and refusal rules.
- **Tool‑First Assistant:** Integrate at least **two** tools (e.g., web search + calendar mock API) with planning prompts.
- **Hybrid:** Retrieval + tools, plus short‑term memory.

**Submission artifacts:**
- Exported `.json` (or `.yaml`) **Flow** file and a screenshot of the canvas.
- A **Design Report** explaining nodes, data flow, prompting, and guardrails.
- A **User Guide** describing how a non‑technical user runs the flow.

---

## Part 2 - LangChain Tutorial (Code‑First)

### 2.1  Environment Setup
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install "langchain>=0.3" "langchain-community" "faiss-cpu" "chromadb" "pydantic>=2.0" "tiktoken"
# Optional local models:
pip install "ollama" ; # then run:  ollama pull llama3
```

> The video on local agents with Python + Ollama shows end‑to‑end agent setup on a local stack; adapt that workflow here.

### 2.2  A Minimal RAG Chain (baseline)
```python
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI  # or use Ollama via langchain_ollama
# from langchain_ollama import ChatOllama

# 1) Load & split
loader = DirectoryLoader("data", glob="**/*.pdf", loader_cls=PyPDFLoader)
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

# 2) Embed & index
emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vs = FAISS.from_documents(chunks, emb)

# 3) Retrieve
retriever = vs.as_retriever(search_kwargs={"k": 4})

# 4) Prompt + LLM
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the provided context. Cite sources as [S{index}]. If unsure, say you don't know."),
    ("human", "Question: {question}\n\nContext:\n{context}")
])

llm = ChatOpenAI(model="gpt-4o-mini")  # or ChatOllama(model="llama3")

def rag_answer(question: str):
    ctx_docs = retriever.get_relevant_documents(question)
    ctx = "\n\n".join(f"[S{i}] {d.page_content[:1000]}" for i, d in enumerate(ctx_docs))
    msg = prompt.format_messages(question=question, context=ctx)
    return llm.invoke(msg).content
```

### 2.3  Adding Tools & an Agent
```python
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

search = DuckDuckGoSearchRun()

toolset = [search]  # you may add custom Python tools as well

react_tmpl = PromptTemplate.from_template(
    "You are an assistant that decides when to use tools.\n"
    "Use tools ONLY if needed. Show reasoning as thoughts, actions, observations.\n"
    "Question: {input}"
)

react_agent = create_react_agent(llm, tools=toolset, prompt=react_tmpl)
agent = AgentExecutor(agent=react_agent, tools=toolset, verbose=True)

def ask_agent(q: str):
    return agent.invoke({"input": q})
```

### 2.4  Local LLM (Ollama) Variant
```python
from langchain_ollama import ChatOllama
llm_local = ChatOllama(model="llama3", temperature=0.2)  # requires `ollama pull llama3`
# Reuse RAG or agent with llm_local
```

### 2.5  Deliverable B - Custom LangChain System
Implement one of the following (or propose alternate with approval):
- **Corpus‑Grounded Assistant:** RAG over your own PDFs/notes with transparent citations.
- **Tool‑Enabled Planner:** Agent with at least **two** tools (e.g., search + calculator, or HTTP + local file I/O) and explicit error handling.
- **Local‑First Agent:** Use Ollama for offline inference; compare output quality/speed vs hosted LLMs.

**Submission artifacts:**
- Executable **Python script(s)** or a notebook.
- **README** with environment setup and run instructions.
- **Evaluation notes** (prompt tests, failure cases, latency measurements).

---

## Reporting & Reflection (for both Parts)

Include a combined **Design Report** (4–6 pages) covering:
1. **Requirements & Use Case.** Who is the target user? What tasks? Success criteria?
2. **Architecture.** Diagrams for LangFlow canvas and LangChain modules (RAG, tools, memory).
3. **Prompting & Safety.** System prompts, refusal rules, and jailbreak mitigations.
4. **Evaluation.** Test prompts, edge cases, latency/resource metrics.
5. **Ethics.** Misuse risks, bias, privacy, consent, transparency (model & data cards), data retention, opt‑out.
6. **Comparative Analysis.** LangFlow vs LangChain trade‑offs (dev speed, observability, portability, reliability).

---

## Grading & Submission

- Submit: LangFlow export, Python code, screenshots, report PDF, and a short demo video (≤5 minutes).
- Academic integrity: If you use external flows or code, cite them.
- Reproducibility: Provide seed config, model versions, and exact dependency list.

---

## Appendix A - Suggested Prompts (for testing)
- Given these policies, what are the prerequisites for **X**? Cite sources.
- Plan an agenda using calendar constraints; call the API only when the date is valid.
- Summarize each document into 3 bullets with a confidence estimate.

## Appendix B - Troubleshooting
- **Vector store empty?** Check file paths and splitter. Ensure embeddings installed.
- **Agent loops?** Add stop tokens; constrain tool use; add when to use instructions.
- **Local models slow?** Try smaller Ollama models; lower `k`; reduce chunk size/overlap.

<!-- Citations: The tutorial structure is informed by the following videos. -->
<!--
  rz40ukZ3krQ - Build a RAG Based LLM App in 20 Minutes! | Full LangFlow Tutorial (YouTube).
  QmUsG_3wHPg - ADVANCED Python AI Agent Tutorial - Using RAG, LangFlow (YouTube).
  E4l91XKQSgw - How to Build a Local AI Agent with Python (Ollama, LangChain & RAG) (YouTube).
-->
