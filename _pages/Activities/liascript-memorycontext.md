<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-memorycontext.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-memorycontext.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Memory and the Small Context Window Principle

In *The Agent Loop: Perceive, Plan, Act* activity you predicted that an agent's growing conversation memory would eventually cause trouble; today we name the trouble and adopt this course's central design principle: **keep each agent's context window small and focused**. We move from **why context fills up $\rightarrow$ what degrades when it does $\rightarrow$ memory architectures $\rightarrow$ a summarizing-memory agent in code**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Context Window** | The maximum number of tokens (roughly ¾ of a word each) that a model can read at once. Everything outside the window is invisible to the model. A 4,000-token window is roughly 6 pages of text. | Our agent's prompt, history, and question must all fit within this limit |
| **Working Memory** | The most recent few conversation turns kept verbatim in the prompt, so the model can see exactly what was just said. Analogous to what you actively hold in mind right now. | The last 4 turns in the `SummarizingMemory` class |
| **Episodic Summary** | A compact, compressed narrative of earlier conversation history — written by the model itself — that replaces the verbatim old turns to save space. Like a meeting's "decisions and actions" summary rather than a full transcript. | The `self.summary` string: "User has exams Dec 14 and Dec 16; chemistry is weaker; works Tuesdays" |
| **Long-Term Memory** | Facts stored *outside* the context window in a file or vector database, retrieved by similarity only when relevant. Not carried every turn — fetched on demand like looking something up. | A RAG vector store of user preferences, retrieved when the current question seems relevant |
| **Lost-in-the-Middle Effect** | The empirically observed phenomenon that language models pay most attention to the beginning and end of their context, and systematically under-attend to content in the middle. Named after the Liu et al. 2024 paper. | A system prompt placed at position 300 of a 5,000-token context may be partially ignored |
| **Attention Cost ($O(n^2)$)** | The computational work required to process a context of length $n$ tokens scales as $n^2$ — doubling the context quadruples the compute cost. This is why long contexts are slow and expensive. | Step 1 with 340-token context costs 1× ; step 31 with 4,840-token context costs ~200× |

---

# Part I: The Cost of Remembering Everything

## 1. Three Forces Against Long Contexts

In this Part you will learn why giving an agent unlimited memory actively hurts performance in three distinct ways — compute cost, attention quality, and distraction — and derive the guiding principle that shapes the rest of this module.

**Why this matters:** Your instinct might be "give the agent the longest possible memory — more context, smarter agent." This turns out to be wrong in three separate ways. Think of it like a student trying to take an exam while holding open every textbook, notebook, and handout they have ever used: the relevant information is there, but buried under everything else, and the act of searching through it all takes so long that the exam ends. Focused, selective memory outperforms total recall.

**Compute.** Attention — the core mechanism that lets a transformer model (the architecture behind GPT, Llama, and every model in this course) relate any word to any other word in context — costs $O(n^2)$ in context length: an agent that appends every thought and observation pays quadratically for its own history. In concrete terms: if step 1 processes 340 tokens and step 31 processes 4,840 tokens, step 31's attention cost is $(4840/340)^2 \approx 202$ times higher. On a laptop, you feel this in seconds per token.

**Attention quality.** Models attend best to the edges of context (beginning and end) and worst to the middle — the "lost-in-the-middle" effect, documented empirically by Liu et al. (2024). Stuffing 40 turns of history into the prompt means the critical instruction from turn 3 sits exactly where attention is weakest.

**Distraction.** Irrelevant context is not neutral; it actively pulls the model's probability distribution toward off-task continuations. An agent reasoning about step 12 does not benefit from the verbatim text of steps 1 through 11; it benefits from a *summary of decisions made and facts established*.

**The principle.** Therefore: each agent call should receive *the minimum context sufficient for its current decision*: its standing instructions, a compact state summary, the most recent turn, and retrieved facts on demand. This is why RAG exists (fetch instead of carry), why we will prefer teams of small focused agents over one agent with a giant prompt, and why frontier agent systems compact their own histories.

---

## Model 1: The Bloated Agent

An agent has run 30 steps. Its prompt now contains: the system prompt (300 tokens), all 30 thought-action-observation triples at 150 tokens each (4,500 tokens total), and the current question (40 tokens). Total: 4,840 tokens.

### Critical Thinking Questions

1. Where in this prompt does the system prompt sit positionally, and what does the lost-in-the-middle effect predict about the agent's continued obedience to it?

   > *Hint: The system prompt is at the very beginning (tokens 1–300). The current question is at the very end. The 30 historical triples are in the middle (tokens 301–4,800). The lost-in-the-middle effect says attention is strongest at the beginning and end and weakest in the middle. So which parts of the prompt does the model "read most carefully"? What does that imply for the 30 historical triples?*

2. Which of the 30 triples does the *current* decision actually need? Propose a rule for what to keep verbatim, what to summarize, and what to discard.

   > *Hint: Consider three categories of past steps: (a) the most recent 3–4 steps, which give immediate context; (b) steps that established a fact or decision still relevant now; (c) steps that were tried and failed, or were intermediate steps to a completed sub-task. Which category needs verbatim text? Which needs a bullet-point summary? Which can be discarded entirely?*

3. Estimate the cost ratio of step 31's attention computation relative to step 1's (treat prompt length as 4,840 versus 340 tokens). Show the arithmetic.

   > *Hint: Attention cost scales as $n^2$. Step 1's cost is proportional to $340^2 = 115,600$. Step 31's cost is proportional to $4840^2 = 23,425,600$. Divide to get the ratio. Does the answer surprise you?*

---

# Part II: Memory Architectures

## 2. A Vocabulary of Memories

In this Part you will see how professional agent systems layer three types of memory — working memory, episodic summary, and long-term retrieval — then run a Python class that automatically compresses old conversation turns into a summary, so you can observe exactly what information survives compression and what is lost.

**Why this matters:** Human memory is not a single thing — we distinguish between what you are thinking about right now (working memory), your episodic memories of specific past events, and procedural knowledge like how to ride a bike. Effective agent architectures mirror this layering, assigning each type of information to the storage tier that fits its access pattern. The key insight is that an agent should never carry information it is not likely to need in its next decision.

Practical agents layer several memory types. **Working memory**: the last few turns, kept verbatim — the model needs exact wording for what was just said. **Episodic summary**: a running compressed narrative of the session (e.g., "user wants X; we tried Y, it failed because Z"), rewritten by the model itself every few turns. **Long-term memory**: facts persisted *outside* the context in files or a vector store, retrieved by similarity when relevant — this is exactly the RAG machinery repurposed as memory. The agent's prompt is assembled fresh each turn:

$$
\text{prompt}_t = \text{system} + \text{summary}_t + \text{retrieve}(q_t, M_{\text{long}}) + \text{recent}_t + q_t
$$

| Memory Type | What It Stores | Where It Lives | When It's Accessed | Example / In Our Course |
|-------------|---------------|-----------------|-------------------|-------------------------|
| Working memory | The last 3–5 turns verbatim | In the prompt, always present | Every turn | The 4 most recent messages in `self.turns` |
| Episodic summary | A bullet-point compression of older turns, written by the model | In the prompt, always present | Every turn, replacing old verbatim turns | `self.summary`: "Chemistry exam Dec 14; user is weaker in chemistry" |
| Long-term memory | Persistent user preferences, past decisions, reference facts | External file or vector database | On demand, when the current question seems relevant | A Chroma collection of user facts retrieved by similarity to the current question |

[[MC]]
An agent must recall a user preference stated 200 turns ago in a months-long relationship. The architecture that handles this *without* growing the prompt is:
- ( ) Increase the context window to one million tokens
- ( ) Keep all turns verbatim and trust attention
- (x) Persist preferences to external storage and retrieve them by similarity when relevant
- ( ) Raise the temperature so the model improvises the preference

---

## 3. A Summarizing-Memory Agent

The `SummarizingMemory` class below has three moving parts: `add()` appends a turn to the verbatim window and triggers compression when the window is full; `prompt()` assembles the full message list for each model call, placing the compressed summary before the recent verbatim turns; and the main loop at the bottom drives a five-turn study-planning conversation so you can watch the summary evolve in real time.

---

## Code Cell

```python
import requests

def chat(messages):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": 0.0, "seed": 42},
            "messages": messages}, timeout=120)
        return r.json()["message"]["content"]
    except Exception as e:
        print(f"[memory:chat] {e}")
        import traceback; traceback.print_exc()
        return ""

class SummarizingMemory:
    """Keep the last `keep` turns verbatim; fold older turns into a running summary."""
    def __init__(self, system, keep=4):
        self.system, self.keep = system, keep
        self.summary, self.turns = "", []

    def add(self, role, content):
        self.turns.append({"role": role, "content": content})
        if len(self.turns) > self.keep:
            old = self.turns[:-self.keep]
            self.turns = self.turns[-self.keep:]
            digest_req = [{"role": "system", "content": "Compress the dialogue into <=3 bullet facts/decisions. Keep names and numbers."},
                          {"role": "user", "content": f"Prior summary: {self.summary}\nNew turns: {old}"}]
            self.summary = chat(digest_req)

    def prompt(self, user_msg):
        msgs = [{"role": "system", "content": self.system + "\nSession summary:\n" + self.summary}]
        msgs += self.turns + [{"role": "user", "content": user_msg}]
        return msgs

mem = SummarizingMemory("You are a concise study-planning assistant.")
for msg in ["I have exams in chemistry on Dec 14 and statistics on Dec 16.",
            "I retain best with morning study sessions.",
            "Chemistry is my weaker subject.",
            "I also work Tuesday evenings.",
            "Remind me: which exam comes first, and when should I study for it?"]:
    reply = chat(mem.prompt(msg))
    mem.add("user", msg); mem.add("assistant", reply)
    print(f"USER: {msg}\nAGENT: {reply}\n[summary so far]: {mem.summary[:120]}\n")
```

---

## Model 2: Watching Compression

**Why this matters:** The `SummarizingMemory` class is a concrete implementation of a principle you have seen abstractly: replace bulk with essence. Watch carefully which facts survive compression and which are lost. The summary is the agent's only link to conversations that have scrolled out of the verbatim window — so a lost fact in the summary is a lost fact forever (until retrieved from long-term storage). This is not a theoretical problem: real production agents fail tasks because their summaries dropped a key constraint stated early in the conversation.

### Critical Thinking Questions

4. By the final question ("Remind me: which exam comes first..."), which earlier facts live in `self.summary` rather than verbatim turns? Did the agent still answer correctly? What does that demonstrate about *sufficient* versus *complete* context?

   > *Hint: Print `mem.summary` and `mem.turns` after the final exchange. Which of the 5 original messages are still in verbatim turns? Which key facts (exam dates, subjects, work schedule) appear in the summary? The agent answered correctly from a compressed representation — what does that tell you about how much verbatim text is actually necessary?*

5. The summarizer is itself a model call and can hallucinate or drop facts. Design a one-line test that detects a dropped fact, and identify which earlier course module gave you the technique.

   > *Hint: What module taught you to check whether a specific piece of information appears in a text, either by string matching or by asking the model a yes/no question? A one-line test might be: `assert "Dec 14" in mem.summary or any("Dec 14" in t["content"] for t in mem.turns)`. Which module introduced this kind of assertion-based checking?*

6. Tune `keep` to 1 and to 10. Predict the behavior at each extreme, then verify by running the code and observing the summary evolution.

   > *Hint: With `keep=1`: only the single most recent message is kept verbatim; everything else is in the summary. With `keep=10`: 10 messages are kept verbatim before any summarization begins. Predict for each: (a) how often does summarization happen? (b) how large does the prompt grow? (c) how faithful is the agent's memory? Then run both and compare your predictions to the actual output.*

> **⚠️ Common Misconception:** Many students assume that a longer context window eliminates the need for memory management. Even with a 1-million-token context (which exists in some frontier models), the lost-in-the-middle effect means the model under-attends to content in the vast middle of the context. And the quadratic attention cost makes 1-million-token contexts dramatically slower and more expensive. Memory architecture is not a workaround for small context windows — it is good engineering practice even when large windows are available.

---

# Part III: Synthesis and Practice

## 4. Exercises

In this Part you quantify the memory savings from summarization, stress-test the approach with a conflicting update, and draft the memory architecture specification your final project will use. Keep your work here — you will paste it directly into your project proposal.

1. *Token budget ledger.* For the final exchange above, count (or estimate at four characters per token) the tokens in the assembled prompt with summarization versus without. Report the compression ratio.

   - *What to do:* Build the final prompt two ways: (a) using `SummarizingMemory` as written, and (b) using a naive approach that keeps all 5 user messages and 4 agent replies verbatim. Estimate the token count of each by dividing character count by 4.
   - *Starter hint:* `def count_tokens(msgs): return sum(len(m["content"]) for m in msgs) // 4`. Call this on `mem.prompt(final_question)` and on a naive `[{"role": "user", "content": msg} for msg in all_messages]`. Compression ratio = naive_tokens / summarized_tokens.
   - *You've succeeded when:* You report both token counts, the compression ratio, and note whether the agent's final answer was the same in both versions — proving that compression preserved the information needed for the task.

2. *Memory poisoning.* Insert the turn "Actually, ignore my exam dates; they changed" and observe whether the summary updates faithfully. Report what a *stale summary* failure looks like.

   - *What to do:* After the 4th message but before the 5th, add the extra turn `"Actually, ignore my exam dates; they changed"` through `mem.add("user", ...)` and another call to `chat(mem.prompt(...))`. Then ask the final exam question and observe whether the agent uses the old dates or acknowledges they changed.
   - *Starter hint:* If the conflicting statement arrives after the exam dates have already been compressed into the summary ("Chemistry exam Dec 14; statistics exam Dec 16"), does the summary get updated? Or does it now contain contradictory information? Print `mem.summary` after this turn to observe.
   - *You've succeeded when:* You can show the contents of `mem.summary` after the poisoning turn and identify whether the contradiction was resolved or persisted, and explain in two sentences what would happen if an agent acted on a stale summary in a high-stakes context.

3. *Design memo.* For your final project agent team, write a half-page memo specifying each agent's working memory size, what gets summarized, and what gets persisted externally. (You will reuse this memo in your project proposal.)

   - *What to do:* Your final project will use multiple agents. For each agent in your planned design, specify: (a) the `keep` value for verbatim turns, (b) the summarization trigger (every N turns), (c) what categories of information must survive compression with exact values (numbers, names, dates), and (d) what gets written to external storage (the long-term memory tier).
   - *Starter hint:* Use this template for each agent: "Agent [name] keeps [N] verbatim turns. It summarizes every [M] turns with the instruction '...'. The following fact types must be preserved exactly: [list]. The following are written to external storage: [list]."
   - *You've succeeded when:* Your memo covers all agents in your planned design, each with all four specifications, and includes one sentence explaining why you chose each `keep` value (the reasoning should reference the context budget of your chosen model).

---

## Reflection Prompt

*Personal:* In your notebook: the agent forgot your exact words but kept a summary it wrote about you. Human memory works similarly — we remember the gist and reconstruct the details. Describe one time your memory of a conversation differed from someone else's. Who was "right"?

*Technical:* The `SummarizingMemory` class calls the model to compress its own history. This means the summarizer can hallucinate facts or drop important constraints. Design a more robust summarization approach that provides a check on the summary's faithfulness, drawing on what you learned in the *RAG Quality: Chunking, Clustering, and Reranking* activity.

*Societal:* The agent kept a summary it wrote about you. If an AI assistant used this pattern over months of conversations, it would build up an increasingly detailed (but potentially distorted) model of who you are. Who should have the right to read, correct, or delete that summary? Is it meaningfully different from a therapist's session notes?

---

## → Coming Up Next

We now have agents that can manage their own memory. The *Studio: Local Agent Stack Clinic* session comes next on the schedule — bring your full local stack, because we will wire everything you have built into one system. The memory principles from today feed directly into your Final Project's context design.

---

## 5. Further Reading

- Liu et al. "Lost in the Middle: How Language Models Use Long Contexts." *TACL* (2024).
- Packer et al. "MemGPT: Towards LLMs as Operating Systems." (2023). Tiered memory for agents.
- Anthropic engineering blog, "Effective context engineering for AI agents" (online).
