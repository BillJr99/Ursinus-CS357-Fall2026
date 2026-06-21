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

# Memory in Agents: What They Remember and Why It Matters

An agent with no memory is like a new employee who forgets every conversation at the end of every day — technically skilled but unable to build on prior work. An agent with too much memory is a massive, expensive, privacy-sensitive data store that slows every response. This activity maps the four types of agent memory, explains the hard limits imposed by the context window, and introduces the external memory strategies that let agents serve users across sessions, weeks, and semesters.

---

## Directions and Group Roles

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task and on time; ensures everyone participates |
| **Recorder** | Documents the group's answers and reasoning |
| **Presenter** | Shares the group's findings with the class |
| **Reflector** | Monitors group process and leads the reflection prompt |

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|:-----|:------------------------|:------------------------|
| **Context Window** | The fixed-size token buffer that an LLM can "see" at one time — everything outside this window is invisible to the model during that generation step. Think of it as the model's desk: only what is on the desk is immediately usable. | An 8,192-token context window can hold roughly 6,000 words. A conversation that runs longer than that must either drop old content or compress it — there is no way to expand the desk. |
| **Working Memory** | The agent's active, in-context information: the current system prompt, conversation history, retrieved documents, and any intermediate reasoning. It is fast (the LLM can access it instantly), finite (bounded by the context window), and volatile (gone when the session ends or the context is cleared). | The first 10 turns of a tutoring session live in working memory. Turn 11 is added and, if the budget is tight, turn 1 may be dropped to make room — the agent "forgets" it unless it was saved externally. |
| **Episodic Memory** | Records of specific past interactions indexed by time and session — "what happened in the conversation on Tuesday." Stored externally, retrieved by timestamp or semantic similarity, and brought back into the context window when relevant. | A study assistant that recalls "last week you said you found integration by parts confusing — here's a follow-up problem" is using episodic memory retrieved from an external log. |
| **Semantic Memory** | General world knowledge and domain facts that are not tied to specific events — "what is the capital of France" or "what does FERPA protect." In agents, this is typically the model's training knowledge plus any RAG knowledge base. | A RAG agent that retrieves relevant course policy documents to answer a student's question is augmenting the model's trained semantic memory with external semantic memory. |
| **Procedural Memory** | Learned skills and behavioral patterns — "how to write a bug report" or "how to apply the chain rule." In agents, this is encoded in fine-tuned model weights or persistent few-shot examples in the system prompt. | A coding agent fine-tuned on a company's code style has "learned" (encoded in its weights) procedural knowledge about that style — but updating that knowledge requires retraining, not just editing a database. |
| **Lost in the Middle** | A research finding (Liu et al., 2023) showing that LLMs reliably attend to information at the very beginning and very end of the context window, but frequently ignore or misremember information placed in the middle. This means context *layout* — where you put things — is a design decision with measurable impact on accuracy. | If you put the most important safety rule in the middle of a 20-page system prompt, the model is statistically less likely to follow it than if you put it at the very beginning or the very end. |

---

## Model 1: Four Types of Agent Memory

> **Why this matters:** An agent's context window is like working memory — finite, fast, but gone when the session closes. Just as a student can hold about 7 items in working memory at once, an LLM can only "see" whatever fits in its context window. Understanding the four memory types helps you design agents that remember the right things for the right reasons — and that fail gracefully when memory runs out instead of silently dropping critical information.

Cognitive scientists describe human memory in multiple systems (working, episodic, semantic, procedural). Agent designers have adopted the same taxonomy because these categories map cleanly onto the different storage mechanisms available in modern AI systems.

| Memory Type | What It Stores | Where It Lives Technically | How Much It Costs | How It Fails | In Our Course |
|:------------|:---------------|:--------------------------|:-----------------|:------------|:--------------|
| **Working memory** | The current conversation and all active context: system prompt, retrieved documents, tool call results, and intermediate reasoning produced so far in this session | In-context token buffer — the LLM's context window, held in GPU memory during inference | Free in the sense that you are already paying for inference, but each additional token increases cost proportionally | Exhausted when the token budget is exceeded; oldest content is dropped (or the entire request fails if you do not implement truncation logic) | Every call to the Hermes-3 model uses a context window — the system prompt plus your conversation turns consume the budget |
| **Episodic memory** | Records of specific past interactions with timestamps: what the user said on turn 3, what the agent replied, what tool was called and what it returned | External database (SQL or document store), external log file, or vector store indexed by session ID and timestamp | Database storage and retrieval query cost per session lookup | Retrieval fails if events are not indexed correctly; the log grows without bound if no retention policy is set; old episodes become irrelevant as context changes | Saving conversation turns to a PostgreSQL table so they survive container restarts — this is the Session Database pattern from the Deployment activity |
| **Semantic memory** | General world knowledge, domain facts, and concept relationships that are not tied to specific events — the "encyclopedia" the agent can consult | Trained model weights (baked in during training); external RAG vector store (retrieved at query time) | Vector store query cost per retrieval; training cost is amortized across all uses of the model | Stale or conflicting facts when the world changes after training; retrieval misses when the query does not match the relevant chunk's embedding | The RAG lab stores course documents as embeddings in a vector database — this is semantic memory the agent retrieves at query time |
| **Procedural memory** | How to perform tasks: code style conventions, step-by-step problem-solving approaches, formatting preferences, behavioral patterns | Fine-tuned model weights; persistent few-shot examples in the system prompt | Very expensive to update — requires retraining or fine-tuning the model, not just editing a database row | Catastrophic forgetting: retraining on new tasks can overwrite previously learned behaviors; updating one procedure may degrade others | A model fine-tuned to always format code responses in a specific way has procedural memory baked into its weights |

### Critical Thinking Questions

1. Which of the four memory types is the most volatile — most likely to be lost during a normal agent session without any server failure? Explain your reasoning by describing the specific mechanism that causes each type to be lost, and rank them from most to least volatile.

   *Hint:* "Volatile" means easily lost, not just eventually lost. Working memory is lost when the context fills up or the session ends. Episodic memory is lost only if the external database fails. Walk through each type and identify the specific condition that destroys it, then rank them.

2. Retrieval-Augmented Generation (RAG) retrieves relevant documents and places them in the prompt at query time. Which memory type does RAG primarily implement? Could a single RAG system implement more than one type simultaneously? Give a concrete example of a RAG configuration that implements two different memory types.

   *Hint:* RAG retrieves "facts about the world" — that sounds like semantic memory. But what if the RAG corpus contains past conversation logs indexed by session ID? What memory type is that? A RAG system that retrieves both course policy documents (general knowledge) and the student's past question history (session records) is implementing two types simultaneously.

3. When working memory is exhausted mid-conversation, the system must make a choice about what to do. Describe at least three distinct choices the system could make, explain what the user experiences in each case, and identify the trade-off each choice forces.

   *Hint:* The three obvious options are: (a) stop accepting new messages (return an error), (b) drop the oldest turns silently and continue, (c) compress old turns into a summary and continue. Are there other options? For each, ask: what does the user see? What information is lost? What is the cost in latency or accuracy?

---

## Model 2: Context Window as Working Memory

> **Why this matters:** The context window is the hardest constraint in agent design. You cannot ignore it, you cannot wish it away, and a larger window does not eliminate the problem — it changes its scale. More importantly, *where* you put things in the context window affects whether the model actually uses them. A system prompt that buries the critical safety rule on page 3 is providing less protection than one that leads with it. Context layout is a design decision, not an afterthought.

The context window is the agent's "desk": everything on the desk is immediately usable; anything not on the desk must be fetched. Modern LLMs offer context windows from 4K to 1M+ tokens, but larger windows do not eliminate the problem — they change its scale and add cost.

**Token budget breakdown for an 8K context window example:**

```
Total budget: 8,192 tokens
  ├── [system prompt]         ~800 tokens   (10%)
  ├── [tool definitions]      ~400 tokens   (5%)
  ├── [conversation history] ~5,600 tokens  (68%)
  ├── [new user message]      ~100 tokens   (1%)
  └── [response space]      ~1,100 tokens  (13%)

When does the context fill up?
  After budget is assigned to system prompt + tools: 8,192 - 800 - 400 = 6,992 tokens remain
  Reserved for response: 6,992 - 1,100 = 5,892 tokens for history + new message
  At ~200 tokens/turn: 5,892 / 200 ≈ 29 turns before history must be truncated
```

**The "Lost in the Middle" Phenomenon:** Research (Liu et al., 2023) shows that facts placed in the middle of a long context are retrieved less reliably than facts at the very beginning or very end. This is not a quirk of one model — it has been replicated across multiple LLM families. It means that context *layout* — the order in which you place system prompt, retrieved documents, conversation history, and new messages — is a design decision with measurable impact on model accuracy.

[[MC]]
A user has a 40-turn conversation with an agent. On turn 41, the agent addresses the user as "there" instead of by name, even though the user introduced themselves on turn 1. The most likely cause is:

- ( ) The model was retrained overnight and lost the conversation
- (x) The context window was truncated and the early turns containing the introduction were dropped
- ( ) The agent has no semantic memory module configured
- ( ) The system prompt is too long and overwrote the user's name

> **Common Misconception:** Students often assume that a larger context window eliminates the need to think carefully about memory architecture. In reality, larger context windows introduce new problems: they cost more per token (inference cost scales with context length), they are slower (attention is quadratic in sequence length for most architectures), and the "Lost in the Middle" effect becomes more pronounced as context grows. A 100K-token context window does not mean you can dump 100K tokens of information into it and trust the model to find what it needs — it means the layout and relevance of what you put in matters even more.

### Critical Thinking Questions

4. You have an 8,192-token context window. Your system prompt uses 2,000 tokens and tool definitions use 500 tokens. Each conversation turn averages 200 tokens (user + assistant combined). You need to reserve 1,000 tokens for the model's response. Approximately how many turns can fit before the oldest turns must be dropped? Show your arithmetic, then explain what a user experiences at exactly the moment when turn dropping begins.

   *Hint:* Available tokens for history = total - system prompt - tool defs - response reserve = 8,192 - 2,000 - 500 - 1,000 = 4,692 tokens. At 200 tokens/turn: 4,692 / 200 = 23.46 turns. What happens on turn 24? What does the user notice, if anything?

5. A user told the agent their name on turn 1. The agent addressed them correctly through turn 34. On turn 35, the agent calls them "User" instead of their name. What is the most likely technical explanation? What specific design choice at the beginning of the project could have prevented this from happening?

   *Hint:* If turn 1 was dropped from the context window at around turn 23, why did the agent remember the name through turn 34? Perhaps the name appeared in subsequent turns as well. What if the agent had been designed to extract the user's name at turn 1 and store it in a persistent profile rather than relying on the name remaining in the context window?

6. Given the "Lost in the Middle" effect, where in the context window would you place each of the following: (a) the most important safety constraints the agent must always follow, (b) background reference documents retrieved from a knowledge base, (c) the most recent user message? Explain each placement decision and how it relates to the empirical finding.

   *Hint:* The LiM finding says beginning and end are most reliably attended to. The most recent user message logically belongs at the end (it is the current task). Safety constraints that must never be ignored should therefore go at the beginning. What about the background documents? Placing them in the middle means they may be less reliably used — is there a better placement? What are the trade-offs?

---

## Model 3: External Memory Strategies

> **Why this matters:** A study assistant that only remembers the last 23 turns of a conversation is not very useful over a 16-week semester. External memory strategies are what make long-horizon personalization possible — but they introduce their own costs, failure modes, and privacy risks. Choosing the right strategy (or combination) for your specific use case is one of the first architectural decisions you make when designing a production agent system.

When conversations outlast the context window, the system must choose what to keep in the active window, what to drop entirely, and what to store externally for potential future retrieval.

| Strategy | Description | Token Cost per Turn | Fidelity of Old Information | Implementation Complexity | Failure Mode |
|:---------|:------------|:--------------------|:---------------------------|:--------------------------|:-------------|
| **Full history** | Store every turn in a database; load all of it into the context window on every request | Very high — grows linearly with conversation length; a 100-turn conversation costs 100x more per turn than a 1-turn conversation | Perfect — nothing is lost | Low — just append to a database and load everything | Eventually hits context limit regardless; query latency grows with history length |
| **Sliding window** | Keep only the most recent N turns in the context; older turns are dropped permanently | Low and constant — the cost is the same on turn 1 and turn 1,000 | Lossy for anything discussed more than N turns ago | Low — trivial to implement with a fixed deque | Forgets important early context — the user's name, their stated preferences, the problem they are working on — once it scrolls out of the window |
| **Summary compression** | Use an LLM to summarize old turns into a compact representation; keep the summary in the context instead of the raw turns | Medium — the summary is typically 5–10x smaller than the original turns it replaces | Moderate — summaries capture gist but lose detail; the LLM may hallucinate facts it did not actually see | Medium — requires a summarization step with its own prompt and latency | The summarization LLM may hallucinate or omit important details; the original turns are gone once summarized |
| **Vector store retrieval** | Embed all turns as vectors; at each new turn, retrieve the K most semantically relevant prior turns and include only those | Medium-high — embedding cost plus vector search cost; pay only for what is retrieved | High if retrieved — but misses are invisible (the relevant turn may not be retrieved if the query does not match well) | High — requires embedding infrastructure, vector database, relevance tuning, and retrieval quality evaluation | Retrieval misses: a turn from two weeks ago that is highly relevant to today's question may not be retrieved because today's phrasing does not match the original embedding |

Long-term user preference memory can be maintained in a vector store: after each session, key facts (user preferences, progress milestones, important decisions) are extracted by an LLM and stored as structured embeddings. At the start of the next session, these facts are retrieved and injected at the top of the context window as a "user profile" — before the conversation history begins.

### Critical Thinking Questions

7. You are building a study assistant that tracks a student's progress across an entire 16-week semester, with three sessions per week (approximately 48 sessions total, each lasting 20 turns — roughly 960 total turns). Recommend a memory strategy or combination of strategies. Justify your recommendation in terms of cost (how much does it cost to run the 960th turn?), fidelity (what does the agent remember from week 1 when you are in week 16?), and failure mode (what goes wrong most often?).

   *Hint:* No single strategy from the table above is optimal for all three criteria simultaneously. Think about which combination addresses each criterion: what keeps cost bounded (sliding window or retrieval), what preserves critical long-term information (summary compression or vector store), and what provides perfect fidelity for recent context (full history for recent turns). Sketch the architecture of your hybrid approach.

8. Summary compression uses an LLM to compress older conversation turns into a shorter summary that is kept in the context window instead of the raw turns. Identify at least two specific risks this introduces for factual accuracy, and describe how you would detect in production if a summary had introduced errors — before a student acts on the wrong information.

   *Hint:* The compression LLM might confidently summarize "the student found integration by parts easy" when the student actually said it was difficult — a hallucinated valence flip. The compression LLM might drop specific numbers (the student's quiz score of 67%) and keep only vague descriptions ("the student performed below average"). How would you detect these errors? Can you compare the summary against the original turns automatically?

9. How would you design an empirical evaluation to test whether adding long-term memory retrieval actually improves agent response quality — and not just agent response confidence? Specify the metrics you would use, what the control condition would be (the baseline), what the treatment condition would be (what you are testing), and what a statistically meaningful improvement would look like.

   *Hint:* "Improvement" could mean many things: higher accuracy on factual questions about prior sessions, higher user satisfaction ratings, more personalized responses, or fewer "I don't remember what we discussed" failures. Choose at least two metrics, one objective (automatically measurable) and one subjective (requires human or LLM-judge evaluation). What would your control condition look like — an agent with no external memory, or an agent with a different memory strategy?

---

## Exercises

1. **MemGPT Mapping.**

   *What to do:* Read the abstract of the MemGPT paper (Packer et al., 2023 — linked in Further Reading) and map each component of the MemGPT architecture to one of the four memory types from Model 1. The four MemGPT components are: main context (the active context window), archival storage (a persistent external database for long-term facts), recall storage (a searchable log of prior conversation turns), and the memory management functions (the agent's ability to move content between tiers). For each mapping, write one sentence explaining why that component corresponds to that memory type.

   *Starter hint:* Main context → working memory is straightforward. For the others, ask: does archival storage store time-indexed events (episodic) or general facts (semantic)? Does recall storage store what happened in past conversations (episodic) or how to perform tasks (procedural)? The memory management functions are trickier — they are more like metacognition than a memory type. How would you handle a component that does not fit neatly into one category?

   *You've succeeded when:* Each of the four MemGPT components has a clear mapping with a one-sentence justification, and you explicitly acknowledge any components that are ambiguous between types rather than forcing a clean mapping.

2. **Study Assistant Memory Design.**

   *What to do:* Design the complete memory architecture for a personal study assistant that tracks a student's learning progress across a 16-week semester. Specify: which of the four memory types you use for each category of information (recent conversation, domain knowledge, student preferences, past session summaries), where each type lives technically (in-context, SQL database, vector store, model weights), how information flows between memory tiers during a session and at session end, and how you handle the end-of-semester data (retain it, archive it, or delete it?).

   *Starter hint:* Draw a data flow diagram with four boxes: Context Window (working memory), Session Database (episodic), Knowledge Base (semantic), and System Prompt (procedural). Label each arrow with what information flows along it and when — at session start, during a turn, after a turn, and at session end. For the end-of-semester question, think about the competing interests: the student wants their progress data for future courses; the institution wants to delete it for privacy; the model provider cannot delete information baked into its training weights. How do you design for all three?

   *You've succeeded when:* Your design specifies a distinct technical mechanism for each of the four memory types, shows explicit data flow at each phase of a session, and addresses the end-of-semester scenario with a concrete policy rather than "we will figure it out later."

3. **Token Cost Estimation.**

   *What to do:* Estimate the total token cost for a 100-turn conversation (assume 200 tokens per turn on average, combining user and assistant messages) under three strategies: (a) full history loaded on every turn, (b) sliding window of the last 10 turns only, (c) summary compression with a 300-token rolling summary replacing all but the last 5 turns. At an API rate of $0.002 per 1,000 tokens input, calculate the total dollar cost of the 100-turn conversation for each strategy and show your work.

   *Starter hint:* For strategy (a), the input to the LLM on turn N includes N prior turns. On turn 1 you send 1 × 200 = 200 tokens; on turn 100 you send 100 × 200 = 20,000 tokens. The total input tokens is the sum of 200 + 400 + 600 + ... + 20,000 = 200 × (1 + 2 + ... + 100) = 200 × 5,050 = 1,010,000 tokens. At $0.002/1K: $2.02 for strategy (a). Now compute strategies (b) and (c) using the same approach and compare.

   *You've succeeded when:* You have a correct numerical result for all three strategies, the arithmetic is shown step-by-step, and you include a one-sentence interpretation of what each cost difference means for a startup deciding which strategy to use for a product with 10,000 daily active users.

---

## Reflection Prompt

**Personal level:** Think about a time when you used a tool or service that "forgot" your preferences between sessions — a website that reset your settings, a voice assistant that did not remember your name. How did that feel? How does persistent agent memory change the nature of the human-AI relationship, and how does it change what you would be willing to share with an agent?

**Technical level:** An agent that remembers everything about a user across months of interactions is more useful and more personalized — but it is also a larger and more sensitive data store that becomes a high-value target for data breaches. Where should agents be designed to forget by default, and what should require explicit user action to retain? Make a technical argument, not just a policy argument.

**Societal level:** Who should make the decision about how much an agent remembers about you — the developer, the deploying organization, you as the user, or a regulator? Consider a student who uses a course AI tutor for four years of college: who owns that memory? If the student transfers to another university, can they take their memory data with them? If the AI company is acquired, what rights does the student have over four years of learning data?

---

→ **Coming Up Next:** This is the final activity in the CS357 sequence. In the semester synthesis, you will integrate memory, observability, robustness, deployment, documentation, and regulation into a complete design review of your capstone agent project.

---

## Further Reading

- Packer et al. "MemGPT: Towards LLMs as Operating Systems" (2023). The paper that formalized the OS-style memory hierarchy for LLM agents: https://arxiv.org/abs/2310.08560
- Liu et al. "Lost in the Middle: How Language Models Use Long Contexts" (2023). The empirical study behind the layout-matters finding: https://arxiv.org/abs/2307.03172
- LangChain Memory module documentation: https://python.langchain.com/docs/modules/memory/
- Zhong et al. "MemoryBank: Enhancing Large Language Models with Long-Term Memory" (2023). An alternative architecture to MemGPT using a structured memory bank with forgetting curves.
