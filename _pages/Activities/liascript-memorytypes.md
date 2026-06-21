# Memory in Agents: What They Remember and Why It Matters

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-memorytypes.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

## POGIL Roles

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task and on time; ensures everyone participates |
| **Recorder** | Documents the group's answers and reasoning |
| **Presenter** | Shares the group's findings with the class |
| **Reflector** | Monitors group process and leads the reflection prompt |

## Model 1: Four Types of Agent Memory

Cognitive scientists describe human memory in multiple systems (working, episodic, semantic, procedural). Agent designers have adopted the same taxonomy.

| Memory Type | What It Stores | Where It Lives in an Agent System | How It Fails |
|---|---|---|---|
| **Working memory** | The current conversation and active context | In-context window (token buffer) | Exhausted when the token budget is exceeded; oldest content is dropped |
| **Episodic memory** | Past interactions and events with timestamps | External conversation log or database | Retrieval fails if events are not indexed well; log grows without bound |
| **Semantic memory** | Facts, concepts, domain knowledge | Knowledge base, RAG vector store, embeddings | Stale or conflicting facts; retrieval misses relevant chunks |
| **Procedural memory** | How to perform tasks; learned behaviors | Fine-tuned model weights; few-shot examples in prompt | Expensive to update; catastrophic forgetting on re-training |

### Critical Thinking Questions

**Q1.** Which of the four memory types is the most volatile (most likely to be lost during a session)? Explain your reasoning.

**Q2.** Retrieval-Augmented Generation (RAG) retrieves relevant documents and places them in the prompt. Which memory type does RAG primarily implement? Could RAG implement more than one type?

**Q3.** What happens — at the system level and at the user experience level — when working memory is exhausted mid-conversation? What choices does the system have?

## Model 2: Context Window as Working Memory

The context window is the agent's "desk": everything on the desk is immediately usable; anything not on the desk must be fetched. Modern LLMs offer 4K to 1M+ token windows, but larger windows do not eliminate the problem — they change its scale.

**Token budget breakdown (8K example):**

```
[system prompt: ~800 tokens] [tool definitions: ~400 tokens] [conversation history: ~5,600 tokens] [new message: ~100 tokens] [response: ~1,100 tokens]
```

**The "Lost in the Middle" Phenomenon:** Research (Liu et al. 2023) shows that facts placed in the middle of a long context are retrieved less reliably than facts at the very beginning or very end. This means context layout is a design decision, not just a technical detail.

### Critical Thinking Questions

**Q4.** You have an 8,192-token context window. Your system prompt uses 2,000 tokens and tool definitions use 500 tokens. Each conversation turn averages 200 tokens (user + assistant combined). Approximately how many turns can fit before the oldest turns must be dropped?

**Q5.** A user told the agent their name on turn 1. By turn 35 the agent calls the user "User" instead of their name. What is the most likely explanation, and what could have been done differently?

**Q6.** Given the "lost in the middle" effect, where in the context would you place: (a) the most important safety constraints, (b) background reference documents, (c) the most recent user message? Explain each choice.

**What is the most likely cause of the agent forgetting the user's name?**

A user has a 40-turn conversation with an agent. On turn 41, the agent addresses the user as "there" instead of by name, even though the user introduced themselves on turn 1. The most likely cause is:

[[MC]]
- ( ) The model was retrained overnight and lost the conversation
- (x) The context window was truncated and the early turns containing the introduction were dropped
- ( ) The agent has no semantic memory module configured
- ( ) The system prompt is too long and overwrote the user's name

## Model 3: External Memory Strategies

When conversations outlast the context window, the system must choose what to keep, what to drop, and what to store externally.

| Strategy | Description | Cost | Fidelity | Implementation Complexity | Failure Mode |
|---|---|---|---|---|---|
| **Full history** | Store everything; load all of it | High (tokens + latency) | Perfect | Low | Hits context limit anyway |
| **Sliding window** | Keep the last N turns only | Low | Lossy for old facts | Low | Forgets important early context |
| **Summary compression** | LLM summarizes old turns; keep summary | Medium | Moderate | Medium | Hallucinated or lossy summaries |
| **Vector store retrieval** | Embed all turns; retrieve relevant ones | Medium-high | High if retrieved | High | Retrieval misses; relevance errors |

Long-term user preference memory can be maintained in a vector store: after each session, key facts (preferences, progress, decisions) are extracted and stored as embeddings, then retrieved at the start of the next session.

### Critical Thinking Questions

**Q7.** You are building a study assistant that tracks a student's progress across an entire semester (16 weeks, 3 sessions/week). Which memory strategy or combination of strategies would you recommend? Justify your answer in terms of cost, fidelity, and failure modes.

**Q8.** Summary compression uses an LLM to compress old turns. What specific risks does this introduce for factual accuracy, and how would you detect if a summary introduced errors?

**Q9.** How would you design an evaluation to test whether adding long-term memory retrieval actually improves agent response quality? What metrics would you use?

## Exercises

1. **MemGPT Mapping:** Read the MemGPT paper abstract (Packer et al. 2023) and map each component of the MemGPT architecture (main context, archival storage, recall storage, and the memory management functions) to the four memory types from Model 1. Provide a one-sentence justification for each mapping.

2. **Study Assistant Memory Design:** Design the complete memory system for a personal study assistant that tracks a student's progress across a 16-week semester. Specify: which memory types you use, where each lives technically, how information flows between them, and how you handle the end-of-semester data.

3. **Token Cost Estimation:** Estimate the total token cost for a 100-turn conversation (average 200 tokens/turn) under three strategies: (a) full history loaded each turn, (b) sliding window of 10 turns, (c) summary compression with a 300-token rolling summary. At $0.002 per 1,000 tokens, what does each strategy cost?

## Reflection Prompt

An agent that remembers everything about you across months of interactions is more useful and more personalized — but it is also a larger and more sensitive data store. Where should agents be designed to forget, and who should make that decision? Should it be the developer, the deploying organization, the user, or a regulator?

## Further Reading

- Packer et al., "MemGPT: Towards LLMs as Operating Systems" (2023)
- Liu et al., "Lost in the Middle: How Language Models Use Long Contexts" (2023)
- LangChain Memory module documentation — https://python.langchain.com/docs/modules/memory/
- Zhong et al., "MemoryBank: Enhancing Large Language Models with Long-Term Memory" (2023)
