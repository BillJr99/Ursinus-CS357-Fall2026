# Memory in Agents: What They Remember and Why It Matters
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-memorytypes.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-memorytypes.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Memory in Agents: What They Remember and Why It Matters

Agents that can only access their current context window are amnesiac by default: each conversation starts from zero, each session forgets the last. This module builds a precise vocabulary for the kinds of memory an agent can have, examines why the context window is a surprisingly limited working memory, and explores the architectural patterns that extend an agent's memory beyond a single request. The arc: **human memory taxonomy applied to agents $\rightarrow$ the context window as working memory $\rightarrow$ external memory systems and retrieval strategies**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: A Taxonomy of Agent Memory

## Model 1: Human Memory Taxonomy Applied to Agents

Cognitive scientists distinguish several memory systems in humans. Each has a direct analog in AI agent architecture. Understanding the taxonomy helps diagnose memory failures precisely: "the agent forgot" is underspecified; "the agent's episodic memory was truncated" is actionable.

| Memory Type | What It Stores | Where It Lives in an Agent | How It Can Fail |
|---|---|---|---|
| **Working Memory** (in-context window) | The active "scratchpad": current task, recent turns, tool results, and reasoning in progress | The token buffer passed to the LLM on each call | Finite capacity; older items are evicted or attention-diluted; performance degrades for facts placed in the middle of long contexts ("lost in the middle") |
| **Episodic Memory** (conversation history / external log) | Records of specific past events: prior conversation turns, past sessions, agent actions and their outcomes | External database (SQL, Redis, vector store); retrieved and injected into context on demand | Retrieval misses relevant episodes; storage grows unbounded; compression loses detail; privacy risk if not expired |
| **Semantic Memory** (knowledge base / RAG / embeddings) | General facts about the world, domain knowledge, documentation | Embedding index (FAISS, Pinecone, Weaviate, pgvector); retrieved via similarity search | Retrieved chunks may be off-topic or contradictory; index goes stale; retrieval returns high-similarity but wrong-intent matches |
| **Procedural Memory** (learned skills / fine-tuning / few-shot examples) | How to perform tasks: coding style, response format, domain conventions, interaction patterns | Fine-tuned model weights; few-shot examples in the system prompt; tool schemas | Fine-tuning is expensive and risks catastrophic forgetting; few-shot examples consume context budget; skills may not generalize to new task variants |

### Critical Thinking Questions

1. A student uses a course assistant that answers questions correctly but formats all code in Java even though the course uses Python. Which memory type is mis-specified, and is the problem more likely in the agent's system prompt, its fine-tuning, or its retrieval index? Explain.

2. Episodic memory and semantic memory are both stored externally. Describe a concrete retrieval scenario where conflating the two would cause the agent to behave incorrectly. (Hint: consider a fact that was true in a past session but has since changed.)

3. Working memory is bounded; the others can in principle grow without limit. What tradeoff does this asymmetry create for an agent designer who wants both "responsive on the current task" and "aware of long-term user history"?

4. A student asks the agent: "What did I struggle with last week?" Which memory type must the agent access, and what infrastructure is required to support it that a bare context-window agent does not have?

---

# Part II: The Context Window as Working Memory

## Model 2: Context Window as Working Memory

The context window is the agent's entire cognitive workspace during a single call. Everything the model "knows" in the moment — instructions, tool definitions, prior turns, retrieved documents, and the new message — must fit inside it. The window has a hard token ceiling that varies by model generation:

- **4K tokens** (~3,000 words): Early GPT-3.5 variants. Fits roughly a 5–10 turn conversation plus a system prompt.
- **8K tokens** (~6,000 words): GPT-4 base. Enough for a moderate conversation or one medium document.
- **128K tokens** (~96,000 words): GPT-4-Turbo, Claude 3 family. Enough for a full novel — but attention is not uniform across that span.

**What gets dropped when the context fills.** There is no automatic "important bits survive" logic. Common truncation strategies, each with costs:

- *Left-truncation*: drop the oldest turns. Early context — including the user's stated goal from turn 1 — is lost.
- *Middle-removal*: drop turns from the middle and keep system prompt + recent turns. Destroys conversational coherence.
- *Summarization*: compress old turns to a summary before dropping. Loses detail; the summary can hallucinate.

**The "lost in the middle" phenomenon.** Liu et al. (2023) showed that LLM performance on fact retrieval tasks degrades significantly for facts placed in the *center* of a long context, even when the total length fits within the window. Attention is highest at the beginning (primacy) and end (recency) of the context; the middle is starved.

**Token budget breakdown (typical agent call, 8K window):**

```
|<-- 8,192 tokens total ------------------------------------------>|

[System prompt  ] [Tool schemas   ] [Conversation   ] [New msg][Resp ]
 ~400–800 tokens   ~200–600 tokens   history          ~200 tok  ~500 t
                                     fills remainder
```

```
Concrete example at 8K:

| Region              | Tokens  | Cumulative |
|---------------------|---------|------------|
| System prompt       |   600   |    600     |
| Tool schemas (3)    |   400   |  1,000     |
| Retrieved doc chunk |   800   |  1,800     |
| Conversation hist.  | 5,200   |  7,000     |
| New user message    |   200   |  7,200     |
| Response budget     |   992   |  8,192     |

At 7,200 input tokens consumed, only ~1K tokens remain for the response.
```

[[MC]]
A user has a 40-turn conversation with a customer service agent. On turn 41, the agent responds as if it has never been told the user's name — even though the user stated it clearly on turn 1. The MOST likely cause is:

- ( ) The model was silently retrained between turn 40 and turn 41
- (x) The context window was truncated and the earliest turns (including turn 1) were dropped to make room for recent turns
- ( ) The agent has no semantic memory configured
- ( ) The system prompt is longer than the model's maximum system prompt length

### Critical Thinking Questions

5. A developer is debugging the "forgot my name" bug from the MC question. They inspect the message list sent to the API on turn 41 and find it contains turns 15–40 only. Which truncation strategy was used, and what would a better strategy look like for this use case?

6. The "lost in the middle" phenomenon implies that where you place information in the context matters, not just whether it is there. Redesign the token budget diagram above to maximize the probability that a key user preference (stated on turn 1) is attended to on turn 40.

7. A RAG system injects five retrieved document chunks into the context. Each chunk is 800 tokens. Where in the token budget does this injection go? What is displaced, and how does the placement interact with the "lost in the middle" phenomenon?

8. A model advertises a 128K context window. A team concludes that memory management is therefore "solved" for their use case. Argue against this conclusion using at least two distinct failure modes that persist even at 128K.

---

# Part III: External Memory Systems

## Model 3: External Memory Systems

When conversations or tasks exceed what the context window can hold — or when memory must persist across sessions — the agent must move state outside the LLM call. Three retrieval strategies handle episodic memory at different cost and fidelity points.

| Strategy | Mechanism | Token Cost | Fidelity | Implementation Complexity | Failure Mode |
|---|---|---|---|---|---|
| **Full history** | Store all turns externally; inject all of them on every call | $O(n)$ in number of turns — grows without bound | Perfect (nothing lost) | Low (just append and inject) | Context overflow once $n$ grows large; every call gets more expensive |
| **Sliding window** | Store all turns; inject only the last $k$ turns | $O(k)$ — constant regardless of session length | Partial (early turns lost) | Low (truncate before injection) | Hard cut-off: information just outside the window is completely absent, not fuzzy |
| **Summary compression** | Periodically ask an LLM to summarize old turns; inject summary + recent turns | $O(\log n)$ approximately — summaries compress history | Lossy (detail lost in compression) | Medium (requires compression step; summary must be prompted carefully) | Summary hallucinations; compressor may omit exactly the detail needed later |

**Adding long-term user preference memory with a vector store.** Summary compression handles *what happened*; a preference store handles *who the user is*. The pattern:

```python
# On each turn, extract and upsert user preferences
def update_preference_store(user_id, turn, vector_store):
    extraction_prompt = f"""
    From this conversation turn, extract any user preferences,
    constraints, or facts about the user. Return as JSON list
    of {{"key": ..., "value": ..., "confidence": ...}} or [].
    Turn: {turn}
    """
    prefs = json.loads(llm_call(extraction_prompt))
    for pref in prefs:
        vector_store.upsert(user_id, pref)

# On each new session, retrieve relevant preferences
def load_preferences(user_id, current_query, vector_store):
    return vector_store.retrieve(
        user_id, query=current_query, top_k=5
    )
```

Preferences retrieved from the vector store are injected at the *top* of the context (primacy position) before the conversation history, making them maximally attended to.

### Critical Thinking Questions

9. A study assistant uses a sliding window of $k = 10$ turns. A student spent 15 turns in a prior session establishing that they are a visual learner who prefers diagrams over equations. At turn 11 of the next session, these preferences are gone. Redesign the memory architecture to preserve this preference without sending all 15 turns on every new call.

10. Summary compression relies on an LLM to compress history. Identify two ways the compressor could introduce errors that a downstream agent would treat as ground truth, and propose one verification step for each.

11. The full-history strategy has perfect fidelity. At what approximate conversation length (in turns, assuming 200 tokens per turn and an 8K context window) does the full-history strategy overflow the context, assuming a 600-token system prompt, 400-token tool schemas, and 200-token new message? Show your calculation.

12. The preference extraction pattern above stores inferred preferences without asking the user whether the inferences are correct. Describe a scenario where a wrong preference inference compounds across sessions, and propose a protocol that gives users agency over their stored preferences.

---

# Part IV: Synthesis and Practice

## Exercises

1. **MemGPT Memory Mapping.** MemGPT (Packer et al., 2023) introduces a hierarchical memory architecture for LLM agents: main context (in-context), external context (archival + recall storage), and a memory manager that moves information between tiers. Map each MemGPT memory tier to the four-type taxonomy from Model 1 (working, episodic, semantic, procedural). For each mapping, explain whether it is a 1-to-1 correspondence or a partial mapping, and identify any aspect of MemGPT that the human memory taxonomy does not cleanly capture.

2. **Study Assistant Memory Design.** You are designing the memory system for a personal study assistant that helps a student prepare for exams over a 16-week semester. The assistant must: (a) remember the student's learning goals set in week 1, (b) track which topics the student has reviewed and how confidently, (c) recall specific questions the student got wrong in prior sessions, and (d) adapt explanations to the student's stated preferred style. For each requirement, specify which memory type handles it, where it is stored, how it is retrieved, and how it is updated. Produce a system architecture diagram.

3. **Token Cost Calculation.** A user has a 100-turn conversation with a study assistant. Each turn averages 150 tokens (user + assistant combined). The pricing is $0.002 per 1,000 input tokens. Calculate the total input token cost over the full conversation for each of the three retrieval strategies (full history, sliding window with $k = 20$, summary compression where each summary is 300 tokens and is recomputed every 20 turns). Show all work and discuss which strategy you would recommend for a free-tier student product with a $0.10/user/month budget.

---

## Reflection Prompt

In your notebook: an agent that remembers everything about you across months of interactions is more useful — it knows your learning style, your goals, your past struggles — but it is also a more dangerous data store. A breach exposes not just messages but a behavioral profile. Where should agents forget? Should there be a mandatory retention limit (e.g., 90 days), a user-controlled "forget this" button, or a legal right to be forgotten that applies to agent memory? Who enforces it, and what happens to the model's fine-tuned weights if they encoded your data?

---

## Further Reading

- Liu, N. F., et al. "Lost in the Middle: How Language Models Use Long Contexts." *Transactions of the Association for Computational Linguistics* (2023). The empirical basis for the primacy-recency attention pattern discussed today.
- Packer, C., et al. "MemGPT: Towards LLMs as Operating Systems." *arXiv:2310.08560* (2023). The tiered memory architecture mapped in Exercise 1.
- Shi, W., et al. "In-Context Pretraining: Language Modeling Beyond Document Boundaries." *arXiv:2310.10638* (2023). How document ordering in context affects model performance — closely related to the "lost in the middle" phenomenon.
- LangChain documentation. "Memory." *python.langchain.com* (2024). Practical implementations of sliding window, summary buffer, and vector store memory.
