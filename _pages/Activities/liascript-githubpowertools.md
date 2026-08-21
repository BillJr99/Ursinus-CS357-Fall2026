<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-githubpowertools.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-githubpowertools.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# GitHub Superpowers for AI Developers

This module introduces five URL **domain-swap tricks** that unlock new superpowers when working with GitHub repositories. We move from **the problem of feeding code to AI $\rightarrow$ domain-swap tools that solve it $\rightarrow$ grounding agents in real code $\rightarrow$ navigating unfamiliar codebases in minutes**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Domain swap** | Replacing `github.com` in a repo URL with a different domain to activate a specialized tool on that same repo | `github.com/owner/repo` -> `gitingest.com/owner/repo` |
| **Token budget** | The maximum amount of text (measured in tokens) a model can process in one call; large repos may exceed it | A 50,000-line codebase flattened to text may be 200 000+ tokens, more than most local models can handle at once |
| **MCP server** | A running process that exposes resources and tools to an AI agent via the Model Context Protocol; the agent queries it instead of guessing from training data | `getmcp.io` wraps a GitHub repo as a live MCP server the agent can query at runtime |
| **Architecture diagram** | A visual map of a codebase's modules, their responsibilities, and how data flows between them | `gdagram.com` generates one automatically from a repo URL |
| **Hallucination** | A model generating plausible-sounding but factually incorrect output, often about APIs it learned about during training but that have since changed | A model inventing a method name that never existed in the `requests` library |
| **Grounding** | Connecting a model's responses to verified, current information rather than relying solely on training data | Pointing an agent at a live MCP server instead of asking it to recall an API from memory |

---

# Part I: The Big Idea

In this part, you will learn how swapping a single domain in a GitHub URL unlocks six different power tools (from in-browser editors to instant MCP servers) turning any public repo into an AI-ready resource without cloning anything.

## 1. Domain Swapping

You already know that pressing the `.` key on any GitHub repository opens `github.dev`, a full VS Code editor in the browser, no installation required. That one-key trick is a domain swap in disguise: the browser replaces `github.com` with `github.dev` and GitHub serves a different application. Five specialized services have extended this pattern to deliver capabilities that matter specifically for AI-assisted development.

**Every tool in this activity works on public repositories only.** Never paste a private repository URL into any of these services, and never include secrets (API keys, tokens, database passwords) in any file you commit to a public repo. These tools are designed for reading and understanding open-source code; treat them as read-only research instruments.

The table below maps each tool to its purpose. Some tools belong in your daily workflow; others are situational; you reach for them when a specific problem appears.

| Domain swap | What it does | Use case | Daily or situational? | Public only? |
|---|---|---|---|---|
| `github.dev` (`.` key) | In-browser VS Code editor for any repo | Explore code before forking; read an agent framework | Daily | No (works with private repos you have access to) |
| `gitingest.com` | Flattens a repo into one AI-readable text block with token count | Feed a whole codebase to a coding agent in one paste | Situational | Yes, public repos only |
| `getmcp.io` | Turns a repo into a live MCP server | Ground an agent in real, current API code | Situational | Yes, public repos only |
| `deepwiki.com` | Auto-generates Wikipedia-style docs + Q&A for any repo | Understand a framework you've never seen before | Situational | Yes, public repos only |
| `gdagram.com` | Generates an interactive architecture diagram | See module structure and data flow before reading code | Situational | Yes, public repos only |

---

# Part II: Feeding Code to AI

In this part, you will practice two complementary techniques for getting code into an AI context window: browsing it interactively with `github.dev` before committing to a fork, and ingesting an entire repo as a single prompt-ready block with `gitingest.com`.

## 2. Reading Before Forking (`github.dev`)

When you discover an agent framework on GitHub (say, a RAG pipeline or a multi-tool orchestrator) your first instinct might be to clone it and start reading locally. But cloning takes time, requires git configured on your machine, and can fill your disk with large model checkpoints or datasets. The `.` trick solves all three problems: press `.` on any GitHub repository page and the URL changes from `github.com` to `github.dev`, opening a full VS Code instance in your browser within seconds.

**The in-browser editor is not just a viewer.** You can open the built-in terminal (if the repository has a `devcontainer.json`), use the file explorer to navigate the directory tree, and search across all files with `Ctrl+Shift+F` exactly as you would in a local editor. For AI developers, the most valuable use is reading the agent scaffolding (the entry point, the tool definitions, the memory management) before deciding whether this is the right framework to build on.

---

## 3. One-Block Repo Ingestion (`gitingest.com`)

Even with a great editor, copying code into a coding agent one file at a time is tedious and error-prone. You might miss a utility module, paste files in the wrong order, or accidentally omit the configuration that makes everything else make sense. `gitingest.com` solves this by flattening an entire repository into a single, structured text block with a token count displayed prominently at the top.

**The format that `gitingest.com` produces is designed for a specific workflow:** paste the entire block as the first message to a coding agent, then ask it questions about the codebase or ask it to generate new code that fits the existing patterns. The token count tells you immediately whether the full repo fits in the model's context window or whether you need to filter to a subdirectory.

There is also a CLI version for automation:

```bash
pip install gitingest
gitingest https://github.com/owner/repo --output repo_context.txt
```

---

## Model 1: Hands-On Ingestion Workflow

Your team will work through the following steps using the `litellm` repository (`github.com/BerriAI/litellm`) as the target, a popular proxy that lets one codebase talk to many LLM providers (the same gateway pattern used in the *The Local Agent Stack: Wiring Containers into a System* activity). If that repo is too large, your instructor will direct you to a smaller example.

**Step 1**: Navigate to `github.com/BerriAI/litellm` and press `.`. Locate the main entry point (`__main__.py` or equivalent) and the directory where provider adapters live.

**Step 2**: Open `gitingest.com/BerriAI/litellm` in a second tab. Note the token count displayed. If it exceeds 100 000 tokens, use the path filter to select only the `litellm/` subdirectory.

**Step 3**: Copy the filtered text block. In your team's shared document, paste the first 30 lines (the file-tree summary) and record the total token count.

### Critical Thinking Questions

1. `gitingest.com` reports a token count for the whole repository. What would you do if that count exceeded the context window of the local model you are running (for example, `llama3.2` with a 128k context window)? Describe at least two strategies for reducing the input to a manageable size.

   > *Hint: Think about what you actually need the agent to understand. Does it need every file, or just the interface definitions and the main loop? The path filter on gitingest.com lets you select a subdirectory. File extension filters let you exclude generated files and test fixtures.*

2. A teammate suggests using `gitingest.com` on a private company repository that contains database credentials in a `.env.example` file. What is the specific risk, and what would you tell them?

   > *Hint: "Public only" is not just a terms-of-service issue; consider where the text block ends up, who processes it, and whether it can be logged by a third-party service.*

3. Compare the experience of finding the entry point via `github.dev` (keyboard shortcuts, file explorer) versus scanning the `gitingest.com` text dump. For which task is each approach faster? Is there a task where you would use both together?

   > *Hint: The gitingest text dump preserves file boundaries but loses the IDE's navigation features. The browser editor preserves navigation but requires you to open files one at a time.*

> **Common Misconception:** Students often assume that pasting a codebase into a model's context gives the model "access" to the code in the way a compiler has access, allowing it to run the code or verify that it compiles. The model only reads the text. It cannot execute the code, check for import errors, or confirm that dependencies are installed. It will reason about the code as text, which means it can misinterpret dynamic behavior, miss runtime configuration, and confidently describe code paths that are never actually reached.

---

# Part III: Real-Time AI Grounding

In this part, you will turn any GitHub repo into a live MCP server via `getmcp.io`, giving a coding agent real-time access to a library's source instead of relying on potentially stale training data.

## 4. MCP Servers from Repos (`getmcp.io`)

When a model generates code that calls a library, it draws on patterns it saw during training. If that library's API has changed since the model's training cutoff (a new method name, a renamed parameter, a deprecated class) the model will use the old API confidently and produce broken code. This is one of the most common sources of agent failures in practice.

**`getmcp.io` attacks this problem at the source.** You give it a GitHub repository URL; it reads the current code and spins up a live MCP server that your agent can query at runtime. Instead of the model guessing what `chromadb.Client()` accepts as parameters, the agent calls the MCP server and gets the actual current signature from the actual current source. Hallucinated method names become impossible when the model can check.

The workflow has three steps: (1) paste the repo URL into `getmcp.io` and copy the server address it gives you, (2) add that server address to your agent's MCP configuration, (3) run your agent; it will query the server before generating any code that touches that library.

---

## Code Cell

```python
# Example: Ollama agent configured to use an MCP server
# In practice, MCP configuration lives in your agent framework's config file.
# This snippet shows the logical structure of an MCP-grounded agent call.

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

# System prompt that tells the agent it has access to live API documentation
SYSTEM = """You are a Python coding assistant. You have access to a live MCP server
that provides up-to-date API documentation for the chromadb library. Before writing
any code that calls chromadb, query the MCP server to confirm the current method
signatures. Do not rely on your training data for API details."""

def chat_with_context(user_message, temperature=0.3):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "options": {"temperature": temperature}
        }, timeout=120)
        return response.json()["message"]["content"]
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ""

result = chat_with_context("Write a function that adds a document to a chromadb collection.")
print(result)
```

---

## Model 2: Hallucination Before and After Grounding

For this model, your instructor will demonstrate the same request sent to a local `llama3.2` model (a) without MCP grounding and (b) with a `getmcp.io` MCP server for `chromadb` configured. The Recorder notes any differences in the generated API calls.

### Critical Thinking Questions

4. In the un-grounded response, identify any method names or parameter names that do not appear in the current `chromadb` documentation. What is the most likely explanation for the discrepancy?

   > *Hint: The model's training data has a cutoff date. Libraries that move fast (particularly in the AI ecosystem) may have changed their public API after that cutoff. The model has no way to know this unless it is given current information.*

5. MCP grounding adds a network call at agent runtime. Describe one scenario where this latency cost is worth paying and one scenario where you would skip MCP grounding and use `gitingest.com` instead.

   > *Hint: Think about whether the code being generated will run once or thousands of times. Think about whether the library changes frequently or is extremely stable. Think about whether you are in a development/debugging workflow or a production pipeline.*

Why does connecting an agent to a live MCP server reduce hallucinated API calls, even though the underlying language model's weights have not changed?

[( )] The MCP server retrains the model weights on current library code before each call
[( )] The agent refuses to generate code for any library that has an MCP server configured
[(X)] The agent can query the MCP server for current method signatures and include that verified information in its context before generating code
[( )] MCP servers patch the model's training data in memory at runtime

> **Common Misconception:** "Grounding" does not change the model itself; no weights are updated, and the model does not "learn" the library. It is simply given accurate, current text in its context window at the moment it needs to generate API calls. Remove the MCP server from the configuration and the hallucinations return, because the underlying model still only knows what was in its training data.

---

# Part IV: Understanding Unfamiliar Codebases

In this part, you will use `deepwiki.com` and `gdagram.com` to generate instant documentation and architecture diagrams for any repo, the fastest way to orient yourself in an unfamiliar codebase before you start modifying it.

## 5. Auto-Documentation (`deepwiki.com`)

When you encounter an agent framework for the first time, the README rarely answers the question you actually have: "Where does the agent decide to call a tool versus answer directly?" `deepwiki.com` addresses this by reading the repository and generating a structured, Wikipedia-style explanation of the project, with a Q&A interface for follow-up questions. It is not a search engine; it synthesizes an explanation of the code's design.

**Use `deepwiki.com` when you need to understand the *intent* behind a codebase**, not just its file structure. Ask it questions like "What is the agent's decision-making loop?" or "Where is memory managed?" and it will point you to the relevant modules. Then use `github.dev` or `gitingest.com` to read those specific files in full.

---

## 6. Architecture Diagrams (`gdagram.com`)

Before reading code, it helps to see the map. `gdagram.com` takes a GitHub repository URL and generates an interactive diagram showing modules, their dependencies, and (for many frameworks) the data flow between components. For a RAG pipeline, this typically reveals the ingestion path (documents -> chunker -> embedder -> vector store) and the query path (question -> retriever -> context assembler -> model -> answer) as distinct visual flows.

**The diagram is a starting point, not a source of truth.** Generated diagrams may omit dynamically loaded modules, miss optional components, or draw connections that exist only in certain configurations. Use it to identify entry points and major components, then verify in the actual code.

---

## Model 3: Codebase Orientation Sprint

Your team has 12 minutes to answer five questions about an unfamiliar agent framework, using only `deepwiki.com` and `gdagram.com`. Your instructor will name the repository at the start of the sprint. The Presenter will report your answers and which tool was more useful for each question.

**Questions to answer**:
- What is the main entry point of the application?
- How many distinct "agent" classes or roles does the framework define?
- Where is the model's response parsed for tool calls?
- What happens when the agent exceeds its step budget?
- Which module would you edit to add a new tool?

### Critical Thinking Questions

6. For each of the five questions above, record which tool (deepwiki or gdagram) your team used and how confident you are in the answer (high / medium / low). What patterns do you notice about which tool works better for which type of question?

   > *Hint: Diagram tools are good at "what connects to what" questions. Text explanation tools are good at "why" and "how" questions. Neither is good at questions that require reading actual code logic.*

7. `deepwiki.com` generates its explanations by processing the repository's code and comments. If a module has no comments and uses cryptic variable names, how does this affect the quality of the generated explanation? What does this tell you about good coding practice for AI-assisted development?

   > *Hint: The documentation generator reads the same signals a human reader would: function names, docstrings, comments, variable names. A module named `proc.py` with a function named `do_thing` gives the generator almost nothing to work with.*

8. Neither `deepwiki.com` nor `gdagram.com` can tell you what a piece of code *actually does* when it runs. Name two things about a codebase that these tools cannot reveal, and for each, describe how you would find the answer instead.

   > *Hint: Think about runtime behavior: what happens when an exception is thrown? What does the model actually return for a given prompt? What values does a configuration variable take in production? These are observable only by running the code.*

A teammate wants to use `gdagram.com` to verify that a dependency they plan to remove is not used anywhere in the codebase. Which of the following is the most accurate assessment of this approach?

[( )] This is reliable because gdagram.com performs static analysis equivalent to a compiler
[( )] This is reliable for dynamically loaded modules but not for statically imported ones
[(X)] This is a useful starting point but should be verified with a code search, because generated diagrams may miss dynamic imports and optional dependencies
[( )] This is unreliable in all cases; the only correct approach is to read every file manually

> **Common Misconception:** Automatically generated architecture diagrams show the relationships that are visible through static analysis of import statements and class definitions. They typically miss plugins loaded at runtime, modules imported conditionally based on configuration, and monkey-patching. Treat the diagram as a hypothesis about the structure (a helpful starting point) and confirm any dependency you plan to remove with a full-text search (`Ctrl+Shift+F` in `github.dev`).

---

# Part V: Synthesis and Practice

In this part, you will combine the tools from Parts I-IV in a real codebase sprint: orient, ingest, ground, and extend: the complete GitHub power-user workflow.

## 7. Exercises

1. *Domain-swap scavenger hunt.*

   - *What to do*: Choose any open-source agent project from GitHub (not one used in today's examples). Apply all five domain-swap tools to it and fill in one row of the key-concepts table from this activity: domain swap, what it revealed, whether it was useful for this particular repo.
   - *Starter hint*: Start with `github.dev` (press `.`) to orient yourself, then `gdagram.com` for the diagram, then `deepwiki.com` for the explanation. Use `gitingest.com` last so you know which subdirectory to filter to. Save `getmcp.io` for a library you actually plan to use in code.
   - *You've succeeded when*: You can answer the five codebase-orientation questions from Model 3 for your chosen repo, citing which tool gave you each answer.

2. *Token budget math.*

   - *What to do*: Use `gitingest.com` on a repo of your choice. Record the full-repo token count. Then apply at least two filters (subdirectory, file extension) and record the reduced counts. Calculate the percentage reduction each filter achieves.
   - *Starter hint*: A token is approximately 3-4 characters of English text or code. If the full repo is 500 000 tokens and your local model has a 128k context window, what fraction of the repo can you fit? Which subdirectory contains the most tokens? (gitingest shows a breakdown by directory.)
   - *You've succeeded when*: You have a table showing full-repo token count, at least two filtered counts, percentage reductions, and a written recommendation: which filter strategy would you use to prepare this repo for a coding agent, and why?

3. *Grounding comparison.*

   - *What to do*: Ask a local `mistral` or `llama3.2` model to write a Python function that uses a popular library (your team chooses: `httpx`, `chromadb`, `langchain`, or `pydantic`). Record the generated code. Then look up the actual current API in the library's documentation or source code. Identify any discrepancies.
   - *Starter hint*: Pay attention to constructor arguments, method names, and return types. Libraries like `chromadb` have changed their client API significantly across versions. A model trained before a major release will use the old API.
   - *You've succeeded when*: You have a side-by-side comparison of the model's generated API calls and the actual current API, with each discrepancy annotated with "hallucinated" or "correct."

4. *Security audit of the workflow.*

   - *What to do*: Write a one-page team policy for using the five tools in this activity safely. Cover: which tools are appropriate for which types of repositories, what to check before pasting a URL into any external service, and what to do if a teammate accidentally exposes a private URL.
   - *Starter hint*: Consider the data flow for each tool: where does the repo content go, who processes it, and is it stored? The answers differ by tool; some process client-side, some send repo content to external servers.
   - *You've succeeded when*: Your policy covers all five tools, addresses both public and private repo scenarios, and includes at least one concrete "red line" action that is never acceptable (for example: "Never paste a URL containing credentials into any external tool").

---

## Reflection Prompt

*Personal*: Before today, how did you typically explore an unfamiliar codebase? Did you read files top-to-bottom, search for keywords, or ask someone who had used the project before? How do the five tools today compare to your existing approach, and which one would you actually add to your personal workflow?

*Technical*: In your notebook: You are building an agent that generates database queries using `psycopg2`. The library has been updated twice since your local model was trained. Design a grounding strategy using the tools from today. Which tool(s) would you use, at what stage of development (prototyping vs. production), and what would you do differently for each stage?

*Societal*: Services like `gitingest.com`, `deepwiki.com`, and `gdagram.com` process public open-source code to provide their services. Open-source licenses require attribution and impose conditions on how code can be used. Does automatically ingesting a repository and feeding it to an AI model comply with typical open-source licenses (MIT, Apache 2.0, GPL)? Who is responsible for checking: the tool provider, the developer using the tool, or both?

---

## -> Coming Up Next

Now that you can efficiently read and feed any public codebase to an AI agent, the next activity asks a deeper question: how do you communicate with a local model at the protocol level, without relying on a high-level SDK? We examine the OpenAI-compatible REST API pattern (the common language spoken by Ollama, LiteLLM, and most local inference servers) so you can write agent code that works across providers without being locked into any single library.

---

## 8. Further Reading

- Simon Willison. "Things I've learned about LLMs." *simonwillison.net* (2024). Practical field notes on working with language models, including grounding strategies and the limits of training-data knowledge.
- `gitingest.com` documentation and CLI reference: `github.com/cyclotruc/gitingest`. Covers filtering options, token estimation, and the programmatic API for automation pipelines.
- Model Context Protocol specification: `modelcontextprotocol.io/specification`. The formal definition of the MCP server interface that `getmcp.io` implements, relevant to understanding what an agent can and cannot query at runtime.
