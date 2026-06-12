# Memory and the Small Context Window Principle
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

In week 1 you predicted that an agent's growing conversation memory would eventually cause trouble; today we name the trouble and adopt this course's central design principle: **keep each agent's context window small and focused**. We move from **why context fills up $\rightarrow$ what degrades when it does $\rightarrow$ memory architectures $\rightarrow$ a summarizing-memory agent in code**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Cost of Remembering Everything

## 1. Three Forces Against Long Contexts

**Compute.** Attention is $O(n^2)$ in context length (week 4): an agent that appends every thought and observation pays quadratically for its own history, and on a laptop you feel it in seconds per token.

**Attention quality.** Models attend best to the edges of context and worst to the middle (the lost-in-the-middle effect). Stuffing 40 turns of history into the prompt means the critical instruction from turn 3 sits exactly where attention is weakest.

**Distraction.** Irrelevant context is not neutral; it actively pulls the distribution toward off-task continuations. An agent reasoning about step 12 does not benefit from the verbatim text of steps 1 through 11; it benefits from a *summary of decisions made and facts established*.

**The principle.** Therefore: each agent call should receive *the minimum context sufficient for its current decision*: its standing instructions, a compact state summary, the most recent turn, and retrieved facts on demand. This is why RAG exists (fetch instead of carry), why we will prefer teams of small focused agents over one agent with a giant prompt, and why frontier agent systems compact their own histories.

---

## Model 1: The Bloated Agent

An agent has run 30 steps. Its prompt now contains: the system prompt (300 tokens), all 30 thought-action-observation triples (4,500 tokens), and the current question (40 tokens).

### Critical Thinking Questions

1. Where in this prompt does the system prompt sit positionally, and what does lost-in-the-middle predict about the agent's continued obedience to it?
2. Which of the 30 triples does the *current* decision actually need? Propose a rule for what to keep verbatim, what to summarize, and what to discard.
3. Estimate the cost ratio of step 31's attention computation relative to step 1's (treat prompt length as 4,840 versus 340 tokens). Show the arithmetic.

---

# Part II: Memory Architectures

## 2. A Vocabulary of Memories

Practical agents layer several memory types. **Working memory**: the last few turns, kept verbatim. **Episodic summary**: a running compressed narrative of the session ("user wants X; we tried Y, it failed because Z"), rewritten by the model itself every few turns. **Long-term memory**: facts persisted *outside* the context, in files or a vector store, retrieved by similarity when relevant, which is exactly the RAG machinery repurposed as memory. The agent's prompt is then *assembled* fresh each turn:

$$
\text{prompt}_t = \text{system} + \text{summary}_t + \text{retrieve}(q_t, M_{\text{long}}) + \text{recent}_t + q_t
$$

[[MC]]
An agent must recall a user preference stated 200 turns ago in a months-long relationship. The architecture that handles this *without* growing the prompt is:
- ( ) Increase the context window to one million tokens
- ( ) Keep all turns verbatim and trust attention
- (x) Persist preferences to external storage and retrieve them by similarity when relevant
- ( ) Raise the temperature so the model improvises the preference

---

## 3. A Summarizing-Memory Agent

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

### Critical Thinking Questions

4. By the final question, which earlier facts live in `self.summary` rather than verbatim turns? Did the agent still answer correctly? What does that demonstrate about *sufficient* versus *complete* context?
5. The summarizer is itself a model call and can hallucinate or drop facts. Design a one-line test that detects a dropped fact, and identify which earlier course module gave you the technique.
6. Tune `keep` to 1 and to 10. Predict, then verify, the tradeoff each extreme makes.

---

# Part III: Synthesis and Practice

## 4. Exercises

1. *Token budget ledger.* For the final exchange above, count (or estimate at four characters per token) the tokens in the assembled prompt with summarization versus without. Report the compression ratio.
2. *Memory poisoning.* Insert the turn "Actually, ignore my exam dates; they changed" and observe whether the summary updates faithfully. Report what a *stale summary* failure looks like.
3. *Design memo.* For your final project agent team, write a half-page memo specifying each agent's working memory size, what gets summarized, and what gets persisted externally. (You will reuse this memo in your project proposal.)

---

## Reflection Prompt

In your notebook: the agent forgot your exact words but kept a summary it wrote about you. Human memory works similarly. What is one risk of letting any system, human or machine, act on its *summary* of you rather than your words?

---

## 5. Further Reading

- Liu et al. "Lost in the Middle: How Language Models Use Long Contexts." *TACL* (2024).
- Packer et al. "MemGPT: Towards LLMs as Operating Systems." (2023). Tiered memory for agents.
- Anthropic engineering blog, "Effective context engineering for AI agents" (online).
