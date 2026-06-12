# Multi-Agent Debate
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-multiagentdebate.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multiagentdebate.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Multi-Agent Debate

A critic improves a draft; a **debate** improves a decision. In this pattern, multiple agents argue *different positions* before a judge or a vote settles the question, exploiting the fact that a model is often better at *spotting* a flaw in someone else's answer than at avoiding the flaw itself. We move from **why disagreement helps $\rightarrow$ debate protocols $\rightarrow$ implementation $\rightarrow$ measuring whether debate actually improved accuracy**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Logic of Productive Disagreement

## 1. Independent Errors and Structured Conflict

**Why should two copies of the same model disagree usefully?** Sampling. At nonzero temperature, independent runs explore different reasoning paths, and their *errors are partially independent* even though their training is identical. Debate adds structure to that diversity: each agent must *see* the others' answers and either rebut or concede with reasons, forcing errors into the open where they can be attacked.

**A canonical protocol** (Du et al., 2023): in round 1, $n$ agents answer independently; in each subsequent round, every agent receives all other agents' latest answers and produces a revised answer; after $R$ rounds, aggregate by majority vote or by a judge agent. Variants assign *adversarial roles* (advocate versus skeptic), which is especially effective for decisions with stakes on both sides.

**Honesty about costs.** Debate multiplies inference cost by roughly $n \times R$, and it can converge on a *confidently shared mistake* if the agents' errors correlate. Debate is a tool for questions where verification is easier than generation, not a universal accuracy upgrade, and today we will *measure* rather than assume its benefit.

---

## Model 1: Where Debate Pays

| Question | Debate-worthy? |
|----------|----------------|
| "What is 847 times 36?" | ? |
| "Should our club hold its fundraiser in October or February?" | ? |
| "What is the capital of Australia?" | ? |
| "Does this Python function handle the empty-list case?" | ? |

### Critical Thinking Questions

1. For each row, decide whether debate, a single tool call, or a single model call is the right instrument, and state why in one clause each.
2. The fundraiser question has no ground truth. What does "debate improved the answer" even mean there? Propose a measurable proxy.
3. When agents share training data, which kinds of errors will *correlate* and thus survive debate? Give one concrete example.

---

# Part II: Implementation

## 2. Three Agents, Two Rounds, One Vote

---

## Code Cell

```python
import requests
from collections import Counter

def llm(system, user, temperature=0.9):
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": temperature},   # deliberately unseeded: we want diversity
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[debate:llm] {e}")
        import traceback; traceback.print_exc()
        return ""

def debate(question, n_agents=3, rounds=2):
    sys = "Solve the problem. End with a line 'ANSWER: <short answer>'."
    answers = [llm(sys, question) for _ in range(n_agents)]
    for rnd in range(1, rounds):
        new_answers = []
        for i in range(n_agents):
            peers = "\n\n".join(f"Agent {j} said:\n{a}"
                                for j, a in enumerate(answers) if j != i)
            prompt = (f"Question: {question}\n\nOther agents answered:\n{peers}\n\n"
                      "Critique their reasoning, then give your final answer. "
                      "End with 'ANSWER: <short answer>'.")
            new_answers.append(llm(sys, prompt, temperature=0.5))
        answers = new_answers
    finals = [a.split("ANSWER:")[-1].strip().lower() for a in answers]
    vote = Counter(finals).most_common(1)[0]
    return finals, vote

question = ("A backpack costs 10 dollars more than a water bottle. "
            "Together they cost 30 dollars. What does the water bottle cost?")
finals, (winner, count) = debate(question)
print("final answers:", finals)
print(f"majority: {winner!r} with {count}/{len(finals)} votes")
```

---

## Model 2: Autopsy of a Debate

Run the debate (this question is a classic trap; the correct answer is 10 dollars).

### Critical Thinking Questions

4. Did any round 1 agent fall for the intuitive-but-wrong answer (15)? Did exposure to peers in round 2 repair or spread the error? Quote the decisive sentence from a transcript.
5. Round 1 uses temperature 0.9 and round 2 uses 0.5. Explain this schedule as explore-then-commit, and predict what happens at 0.0 everywhere.
6. Majority vote treats agents as equals. Sketch the judge-agent alternative: what would the judge's system prompt contain, and which earlier pattern is a judge most similar to?

[[MC]]
Multi-agent debate most reliably improves accuracy when:
- ( ) All agents run at temperature 0 for consistency
- ( ) The question requires recalling one rare fact
- (x) Errors across agents are partially independent and flaws in a wrong answer are easier to verify than to avoid
- ( ) The agents share a single context window

---

# Part III: Measure It

## 3. Exercises

1. *Debate versus single shot.* Build a 10-question arithmetic-word-problem set with known answers. Report accuracy for (a) one agent, one sample; (b) three agents, majority vote, no debate round; (c) full two-round debate. Attribute any lift to diversity versus deliberation.
2. *Adversarial roles.* Rerun the fundraiser-style question with an explicit advocate and skeptic plus a judge. Compare the *coverage of considerations* (count distinct relevant factors raised) against a single agent asked to "consider both sides."
3. *Correlated failure hunt.* Find one question where all three agents agree on the same wrong answer. Explain, using Section 1, why debate could not save them, and what *non-LLM* addition (a tool, a retrieval source) would.
4. *Cost accounting.* Tabulate the number of model calls in each condition of Exercise 1, and compute accuracy gained per additional call. Would you ship debate for this task class?

---

## Reflection Prompt

In your notebook: in your own group work this semester, when has disagreement improved the outcome, and when has it merely consumed time? Identify one feature of *productive* human disagreement that today's protocol captures, and one it misses.

---

## 4. Further Reading

- Du et al. "Improving Factuality and Reasoning in Language Models through Multiagent Debate." (2023).
- Irving, Christiano, and Amodei. "AI Safety via Debate." (2018). Debate as an oversight mechanism.
- Liang et al. "Encouraging Divergent Thinking in LLMs through Multi-Agent Debate." (2023).
