<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-multiagentdebate.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-multiagentdebate.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Multi-Agent Debate

In *The Critique and Refine Pattern* activity, a critic improved a draft; a **debate** improves a decision.  In this pattern, multiple agents argue *different positions* before a judge or a vote settles the question, exploiting the fact that a model is often better at *spotting* a flaw in someone else's answer than at avoiding the flaw itself.  We move from **why disagreement helps $\rightarrow$ debate protocols $\rightarrow$ implementation $\rightarrow$ measuring whether debate actually improved accuracy**.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  Please think each model and question through on your own first, then talk it over with your group.  The Recorder posts your answers to the Class Activity Questions discussion board, and the Presenter reports out wherever you disagreed or found another approach.  After class, please respond to the reflective prompt on your own in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Debate Protocol** | A structured format for multi-agent disagreement: agents first answer independently, then each agent sees the others' answers and has the opportunity to revise or rebut, and finally a judge or majority vote settles the question. | Round 1: three agents answer the water bottle problem independently; Round 2: each agent reads the others' answers and revises; final: majority vote picks the winner. |
| **Independent Errors** | Two agents make independent errors when the probability that they both make the same mistake is lower than the probability that either makes it alone. Debate is most valuable when agent errors are independent, so that one agent's wrong answer is challenged by another's correct reasoning. | At temperature 0.9, each agent explores a different reasoning path, so errors from one agent need not be shared by all. |
| **Correlated Errors** | When multiple agents share the same training data and similar biases, they may all make the same mistake regardless of how many there are. Debate cannot fix correlated errors; all agents will agree on the same wrong answer. | If all agents were trained on data that systematically misrepresents a historical event, no amount of debate between them will surface the correct information. |
| **Majority Vote** | An aggregation method where the most common answer among debating agents is taken as the final answer, treating all agents as equals regardless of their reasoning quality. | Three agents answer "10", "15", "10"; majority vote returns "10" (correct answer in the water bottle problem). |
| **Judge Agent** | An alternative to majority vote: a separate agent that reads all agents' final answers and reasoning, then selects or synthesizes the best answer based on argument quality rather than counting votes. | A judge agent with prompt "Read these three answers and their reasoning. Identify which reasoning is most rigorous." |
| **Explore-Then-Commit** | A temperature scheduling strategy where early rounds use high temperature (diverse initial answers) and later rounds use lower temperature (converging toward a well-supported conclusion). | Round 1 at temperature 0.9 for diversity; Round 2 at temperature 0.5 for more considered revision. |
| Reasoning model | A model trained by reinforcement learning against checkable outcomes, which deliberates at length inside one response. It buys more *dependent* steps; debate buys more *independent* errors. They compose, and neither substitutes for the other | Three reasoning models converging confidently on the same wrong answer, because deliberation does not decorrelate error |

---

## Today's 75 Minutes

We have seventy-five minutes together.  Here is how they are meant to go, so you can tell when a section is running long and say so.  Anything marked self-paced sits outside this budget and nothing graded assumes it.

| Minutes | What we do |
|---|---|
| 0-10 | Part I, the logic of productive disagreement, and why it is not the same thing a reasoning model does |
| 10-40 | Part II, three agents, two rounds, one vote, implemented and traced |
| 40-55 | Model 2, the autopsy: did round 2 repair the error or spread it? |
| 55-70 | Section 3, when agreement misleads, and what that means for your project's question |
| 70-75 | Part III, the experiments you will run.  The protocols Extension is self-paced |

---
# Part I: The Logic of Productive Disagreement

In this section you will examine when multi-agent debate adds value and when it does not.  You will analyze a table of question types and practice identifying which situations benefit from structured disagreement versus which are better handled by a single tool call or a single model call.

## 1.  Independent Errors and Structured Conflict

**Why this matters:** When you are unsure of an answer, it helps to get a second opinion, especially from someone who reasoned about the problem independently.  If your friend arrived at the same answer by a different route, you are more confident.  If they arrived at a different answer, that disagreement is valuable information.  Multi-agent debate formalizes this intuition: by forcing agents to independently generate answers and then critique each other's reasoning, the debate exposes flaws that no single agent would catch on its own.  The key word is "independently": if all agents read each other's answers before forming their own, the diversity that makes debate valuable disappears.

**Why should two copies of the same model disagree usefully?**  Sampling.  At nonzero temperature, independent runs explore different reasoning paths, and their *errors are partially independent* even though their training is identical.  Debate adds structure to that diversity: each agent must *see* the others' answers and either rebut or concede with reasons, forcing errors into the open where they can be attacked.

**A canonical protocol** (Du et al., 2023): in round 1, $n$ agents answer independently; in each subsequent round, every agent receives all other agents' latest answers and produces a revised answer; after $R$ rounds, aggregate by majority vote or by a judge agent.  Variants assign *adversarial roles* (advocate versus skeptic), which is especially effective for decisions with stakes on both sides.

Honesty about costs.  Debate multiplies inference cost by roughly $n \times R$. A 3-agent, 2-round debate costs approximately 6× as many LLM calls as a single-shot answer.  Additionally, debate can converge on a *confidently shared mistake* if the agents' errors correlate: all three agents can agree on the wrong answer, and the majority vote will report it with false confidence.  Debate is a tool for questions where verification is easier than generation, not a universal accuracy upgrade.  Today we will *measure* rather than assume its benefit.

---

## Model 1: Where Debate Pays

| Question | Best Approach and Why |
|----------|-----------------------|
| "What is 847 times 36?" | ? |
| "Should our club hold its fundraiser in October or February?" | ? |
| "What is the capital of Australia?" | ? |
| "Does this Python function handle the empty-list case?" | ? |

### Critical Thinking Questions

1.  For each row in the table, decide whether debate, a single tool call (like a calculator or a lookup), or a single model call is the most appropriate instrument, and write a one-clause justification for each choice.

   > *Hint: Debate adds value when there is real ambiguity and independent reasoning can catch errors.  A tool call is better when there is a ground truth that can be computed or retrieved exactly.  A single model call is fine when the task is simple and errors are unlikely.  Which category does each question fall into?*

2.  The fundraiser question has no ground truth; there is no objectively correct month.  What does "debate improved the answer" even mean in that case?  Propose a measurable proxy for "improvement" that does not require a ground truth.

   > *Hint: Even without a correct answer, you can measure whether the debate surfaced more relevant considerations (count distinct factors raised), whether the final recommendation was better justified (count supporting reasons), or whether participants were more confident in the final answer.  Pick one and explain how you would measure it.*

3.  When agents share training data and similar biases, which kinds of errors will *correlate* across agents and therefore survive debate?  Give one concrete example of a question where debate would confidently produce the wrong answer.

   > *Hint: Think about what all LLMs trained on similar internet text might systematically misrepresent or underrepresent.  A question whose correct answer contradicts common misconceptions in that training data is a candidate for a correlated error.  Can you name one?*

### Debate Is Not the Same Thing a Reasoning Model Does

*Why Different Answers Every Time?* introduced **reasoning models**: models trained by reinforcement learning against checkable outcomes, which deliberate at length inside a single response before answering.  It is easy to hear "the model thinks before it answers" and conclude that debate is the same idea with extra steps.  It is not, and the difference is exactly the thing this session is about.

| | Reasoning model | Multi-agent debate |
|---|---|---|
| Where deliberation happens | Inside one context, one response | Across $n$ contexts that started separately |
| What it buys | More *dependent* steps: step B can use step A's result | More *independent* errors: two wrong answers that are wrong differently |
| What it cannot fix | A misconception held throughout that one pass | A misconception all $n$ agents share |
| Cost shape | One call, a long one | $n \times R$ calls |

The row that matters is the second.  A reasoning model lifts the cap on how many steps *depend on each other*, which is why it helps on problems that need a chain of inference.  It does nothing about correlated error: a model reasoning at length from a wrong premise reaches a wrong conclusion carefully.  Debate attacks the other axis entirely.  Its whole premise is that two runs fail *differently*, so one can catch the other.

They compose, and the composition is the interesting case.  Nothing stops you running a debate among three reasoning models, and you would then be buying both properties, at both costs.  What you cannot do is substitute one for the other and expect the same protection.

> **Watch out!**  Reasoning models make debate *harder to evaluate*, not easier.  Each agent now emits a long reasoning stream, and a stream that reads like careful deliberation is more persuasive to the other agents and to you.  Section 3 below is about agreement that misleads; a confident, well-argued, wrong reasoning trace is the most misleading kind of agreement there is.

#### Critical Thinking Questions

4.  Your team runs a 3-agent debate and all three agents are reasoning models.  All three produce long, internally consistent reasoning and converge on the same wrong answer.  Which of debate's two assumptions failed, and would swapping in three *different* models have helped?

    > *Hint: The independence assumption failed, not the deliberation one; every agent reasoned carefully and correlated anyway, because they share training data and inductive biases. Different model families genuinely decorrelate errors more than different samples from one model, so it would likely help, and it is not a guarantee: models trained on overlapping web data can share the same misconception. The honest move is to measure disagreement rate rather than assume it.*

---

With the theory of when debate works (and fails) established, Part II shows the protocol running on a real problem so you can observe these dynamics directly in the output.

---

# Part II: Implementation

In this section you will read the complete debate implementation and run it on a classic algebra problem where the intuitive answer is wrong.  Your goal is to observe whether the debate protocol surfaces and corrects errors, and to connect the temperature scheduling choices directly to the theory from Part I.

## 2.  Three Agents, Two Rounds, One Vote

**Why this matters:** The code below implements the full Du et al. (2023) protocol (a published research recipe for multi-agent debate: independent answers, then peer review, then a vote) in about 30 lines.  The most important design choice is the temperature schedule: round 1 uses temperature 0.9 (high diversity; we want agents to explore different reasoning paths) and round 2 uses temperature 0.5 (lower; agents are now refining rather than exploring, anchored by the debate).  The seed is intentionally absent in round 1 so that each agent's run is random and independent.  This is the opposite of our usual practice of seeding for reproducibility, and it is intentional: without diversity in round 1, there is nothing useful to debate in round 2.

Run this locally with:

```bash
ollama run llama3.2
python debate.py
```

---

## Code Cell

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import requests
from collections import Counter

def llm(system, user, temperature=0.9):
    """
    Call the local LLM. Note: no seed is set here.
    This is intentional; we want genuine randomness for debate diversity.
    The caller controls temperature per round.
    """
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2", "stream": False,
            "options": {"temperature": temperature},   # deliberately unseeded for diversity
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}, timeout=120)
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[debate:llm] {e}")
        import traceback; traceback.print_exc()
        return ""

def debate(question, n_agents=3, rounds=2):
    """
    Run the Du et al. (2023) debate protocol.
    Returns: (list of final answers, (winning answer, vote count))
    """
    # Round 1: all agents answer independently, no communication yet
    # "ANSWER: <short answer>" at the end makes extraction consistent
    sys = "Solve the problem step by step. End your response with a line 'ANSWER: <your short answer>'."
    answers = [llm(sys, question, temperature=0.9) for _ in range(n_agents)]
    print("--- Round 1 answers ---")
    for i, a in enumerate(answers):
        print(f"Agent {i}: {a.split('ANSWER:')[-1].strip()}")

    # Rounds 2+: each agent reads the others' answers and revises
    for rnd in range(1, rounds):
        new_answers = []
        for i in range(n_agents):
            # Build the peer context: what everyone else said
            peers = "\n\n".join(
                f"Agent {j} answered:\n{a}"
                for j, a in enumerate(answers) if j != i
            )
            prompt = (
                f"Original question: {question}\n\n"
                f"The other agents gave these answers:\n{peers}\n\n"
                "Read their reasoning carefully. If you see an error in their reasoning, "
                "point it out specifically. Then give your final answer. "
                "End with 'ANSWER: <your short answer>'."
            )
            # Lower temperature in revision rounds: more focused, less exploratory
            new_answers.append(llm(sys, prompt, temperature=0.5))
        answers = new_answers
        print(f"\n--- Round {rnd + 1} answers ---")
        for i, a in enumerate(answers):
            print(f"Agent {i}: {a.split('ANSWER:')[-1].strip()}")

    # Extract the final short answers and vote
    finals = [a.split("ANSWER:")[-1].strip().lower() for a in answers]
    vote = Counter(finals).most_common(1)[0]   # (answer_text, vote_count)
    return finals, vote

# The classic algebra trap: the intuitive answer (15) is wrong; the correct answer is 10.
# A backpack costs $10 more than a water bottle; together they cost $30.
# If water bottle = x, then (x + 10) + x = 30, so 2x = 20, so x = 10.
question = (
    "A backpack costs 10 dollars more than a water bottle. "
    "Together they cost 30 dollars. What does the water bottle cost?"
)
finals, (winner, count) = debate(question, n_agents=3, rounds=2)
print(f"\n=== Majority vote: '{winner}' with {count}/{len(finals)} agents agreeing ===")
print("Correct answer: 10 dollars")
```

---

## Model 2: Autopsy of a Debate

Run the debate on this question.  The correct answer is **10 dollars** (if the water bottle costs $x$ and the backpack costs $x + 10$, then $x + (x+10) = 30$, giving $x = 10$).  The common wrong answer is **15 dollars** (from the intuition "they cost 30 together and differ by 10, so each is 15", but this ignores the $10 difference).

### Critical Thinking Questions

5.  Did any round 1 agent fall for the intuitive-but-wrong answer of 15 dollars?  Did exposure to the other agents' reasoning in round 2 repair the error (converging toward 10) or spread the error (pulling correct agents toward 15)?  Quote the decisive sentence from the transcript that shows which happened.

   > *Hint: Look at round 2 transcripts for any agent that changed its answer.  Did the agent that changed provide a clear reason for the change?  Is "the other agents said 10 so I will too" a good reason?  What distinguishes persuasion by evidence from persuasion by social pressure?*

6.  Round 1 uses temperature 0.9 and round 2 uses temperature 0.5.  Explain this scheduling as an "explore then commit" strategy: what does each temperature level accomplish, and what would go wrong at temperature 0.0 everywhere?

   > *Hint: At 0.0, every independent agent produces the same answer (the model's mode).  If that mode answer is wrong, all agents start with the same wrong answer and there is nothing to debate.  What is the minimum diversity you need in round 1 for debate to be possible?*

7.  Majority vote treats all agents as equal regardless of the quality of their reasoning.  Sketch the judge-agent alternative: write out the system prompt the judge would use, and explain which pattern from earlier in the course a judge agent most resembles.

   > *Hint: The judge reads everyone's reasoning, not just their final answers.  A judge that can explain why it chose one answer over another is more useful than a vote counter.  Which agent role from the critique-and-refine activity does this most closely resemble?*

> **Common Misconception:** Many students assume that more agents and more rounds always produce more accurate results.  This is only true if (a) the agents' errors are independent and (b) the question has a verifiable ground truth that correct reasoning can converge toward.  For questions with correlated errors (all agents have the same bias) or no ground truth (matters of opinion), more debate may only produce more confident wrong answers.  The research paper that introduced this protocol (Du et al., 2023) reports accuracy gains on specific benchmark tasks; those gains do not automatically transfer to every question type.  Always measure, do not assume.

Part III gives you the structured experiments to generate those measurements yourself, replacing claims about debate with data.

Multi-agent debate most reliably improves accuracy when:

[( )] All agents run at temperature 0 for consistency
[( )] The question requires recalling one rare fact
[(X)] Errors across agents are partially independent and flaws in a wrong answer are easier to verify than to avoid
[( )] The agents share a single context window

---

## 3.  When Agreement Misleads

Debate and consensus both aggregate the model's *distribution*, so both amplify whatever that distribution over-represents: popular framings, mainstream defaults, training-data majorities.  For factual questions with a checkable answer, that is usually a feature, and it is why the vote in Part II works at all.

For questions of taste, values, or contested policy, it is a hazard.  "The average of six samples" can quietly erase a legitimate minority position, and the erasure looks identical to a strong result: a big cluster, a confident synthesis, no visible dissent.  We take this up squarely in *Training Data, Bias, and Explainability*, and it is the reason the Multi-Agent Patterns Lab requires your synthesizer to **disclose** close disagreement in one line rather than resolve it silently.

Sit with the distinction before you move on, because your lab design depends on which side of it your question falls:

- Where would you *want* the majority to win outright, and why is disclosure just noise there?
- Where would a candid "the samples split three to two, and here is the other position" be more useful to your stakeholder than a clean single answer?
- Your project's community partner will ask you a question of one kind or the other.  Which is it, and what does that imply about whether you should be aggregating samples at all?
---

# Part III: Measure It

In this section you will run controlled experiments to quantify exactly when debate earns its extra cost.  The goal is to replace the intuition "more agents = better" with actual numbers showing where debate helps and where it does not.

## 3.  Exercises

1.  **Debate versus single-shot: a controlled experiment.**

   *What to do:* Build a set of 10 arithmetic word problems with known correct answers (vary the difficulty: some easy single-step, some harder two-step).  Measure accuracy for three conditions: (a) one agent, one call; (b) three agents, majority vote with no debate round (just round 1); (c) full two-round debate with three agents.  Report accuracy for each condition and attribute any accuracy lift to diversity (more agents) versus deliberation (the debate round).

   *Starter hint:*
   ```python
   problems = [
       ("A train travels 60mph for 2 hours. How far does it travel?", "120 miles"),
       ("A backpack costs $10 more than a water bottle; together $30. Water bottle cost?", "$10"),
       # ... add 8 more with known answers
   ]

   def single_shot(question):
       answer = llm("Answer briefly. End with 'ANSWER: <answer>'.", question, temperature=0.3)
       return answer.split("ANSWER:")[-1].strip().lower()

   # For each condition, record whether the answer matches the correct answer
   # Condition (a): single_shot(q) == correct
   # Condition (b): run debate(q, n_agents=3, rounds=1) and check majority vote
   # Condition (c): run debate(q, n_agents=3, rounds=2) and check majority vote
   ```

   *You've succeeded when:* You have a three-column table showing accuracy per condition for all 10 problems, and you can say specifically whether the accuracy gain (if any) came from having more agents in the vote pool (diversity) or from the revision rounds (deliberation).

2.  **Adversarial roles: advocate and skeptic.**

   *What to do:* For an open-ended question like "Should our club hold its fundraiser in October or February?", run two versions: (a) the standard protocol with three neutral agents, and (b) one advocate (assigned to argue for October), one skeptic (assigned to argue against October), and one judge that reads both and decides.  Compare the two versions on "coverage of considerations": count the number of distinct relevant factors (cost, weather, student availability, competition with other events, etc.) mentioned across all agents.

   *Starter hint:*
   ```python
   def adversarial_debate(question, topic_for):
       advocate = llm(
           f"You are assigned to argue FOR {topic_for}. Give your strongest arguments.",
           question, temperature=0.7
       )
       skeptic = llm(
           f"You are assigned to argue AGAINST {topic_for}. Give your strongest objections.",
           question, temperature=0.7
       )
       judge = llm(
           "You are a fair judge. Read both arguments and make the best decision, explaining why.",
           f"FOR:\n{advocate}\n\nAGAINST:\n{skeptic}",
           temperature=0.0
       )
       return advocate, skeptic, judge
   ```

   *You've succeeded when:* You can show a count of distinct relevant factors mentioned in each version, and you can explain whether the adversarial structure surfaced considerations that the neutral debate missed.

3.  **Correlated failure hunt: finding what debate cannot fix.**

   *What to do:* Design a question where you predict all three agents will agree on the same wrong answer, because the correct answer contradicts a widespread misconception that appears in training data.  Run the debate and verify.  Then explain, using the concept of correlated errors from Part I, why the debate could not help.  Finally, identify what non-LLM addition (a specific tool call, a retrieval source) would provide the information needed to correct the error.

   *Starter hint:* Common LLM misconceptions include: facts that changed recently (a country's capital that moved, a record that was broken), statistics from training data that are now outdated, or common wisdom that is scientifically contested.  Pick one you are confident about, state the correct answer and why you believe agents will get it wrong, then run the debate to verify your prediction.

   *You've succeeded when:* All three agents in round 1 agree on the same wrong answer, and you can name the specific retrieval source (e.g., a Wikipedia page, a government database URL) that would supply the correct information as a tool call.

4.  **Cost accounting.**

   *What to do:* Tabulate the number of model calls made in each condition of Exercise 1 (single-shot, 3-agent vote, 2-round debate).  Compute the accuracy improvement per additional model call for each step up in complexity.  Based on this data, make a recommendation: for this specific task class (arithmetic word problems), would you ship the debate protocol in production?  Justify your answer with numbers.

   *Starter hint:*
   - Single-shot: 1 call per question × 10 questions = 10 total calls
   - 3-agent vote (round 1 only): 3 calls × 10 questions = 30 total calls
   - 2-round debate: (3 + 3) calls × 10 questions = 60 total calls
   - Accuracy gain per additional call = (accuracy_condition_B - accuracy_condition_A) / (calls_B - calls_A)

   *You've succeeded when:* You have a table with three rows (one per condition), columns for total calls, accuracy, and accuracy-per-call, and a one-paragraph recommendation that cites the numbers rather than making a general claim.

---

## Reflection Prompt

Respond to all three levels in your notebook:

**Personal:** In your own group work this semester (or in any team context) when has disagreement improved the outcome, and when has it merely consumed time without adding value?  Identify one feature of *productive* human disagreement that today's protocol captures (such as structured rounds, explicit rebuttal, or a deciding vote), and one feature of productive human disagreement that today's protocol misses (such as building on others' ideas, acknowledging uncertainty, or changing your mind for social rather than logical reasons).

**Technical:** Today's debate protocol aggregates by majority vote or by a judge agent.  Neither approach is perfect.  Majority vote can be fooled by a coordinated wrong answer; a judge agent introduces another LLM call with its own failure modes.  Design a hybrid: propose a protocol that uses majority vote as the primary signal but escalates to a judge agent only when the vote is not unanimous.  Write out the decision logic in pseudocode.

**Societal:** Multi-agent debate has been proposed as a safety mechanism for AI systems: have one model check another's outputs, or have multiple models argue before a decision is made.  Based on what you learned today about correlated errors, what is the fundamental limitation of using AI models to check other AI models trained on the same data?  What would it take to make AI-oversight-of-AI reliable rather than a false sense of security?

---

-> **Coming Up Next:** Debate and consensus both need something to score the answers they produce, and today you did that scoring by hand.  Next session, *Evaluating Agents: LLM-as-Judge and Rubric Pipelines*, automates it, and then asks the harder question of who audits the judge.  The debate protocol you implemented today is the core of the Multi-Agent Patterns Lab.

---

## Further Reading

- Du et al. "Improving Factuality and Reasoning in Language Models through Multiagent Debate."  (2023).
- Irving, Christiano, and Amodei.  "AI Safety via Debate."  (2018).  Debate as an oversight mechanism.
- Liang et al. "Encouraging Divergent Thinking in LLMs through Multi-Agent Debate."  (2023).

---

# Extension: Multi-Agent Communication (self-paced)

Nothing above requires this.  Today's agents talked by taking turns appending to a shared transcript, which is the simplest protocol there is and works fine for three agents and two rounds.  This section covers what you reach for when that stops scaling: message passing, shared state, blackboards, and the coordination failures each one introduces.

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Message passing** | One agent sends a structured message directly to another agent, who reads and replies, like sending an email that demands a response before the sender continues working | Agent A asks Agent B for a research summary using a JSON-RPC call; B sends back the result |
| **Shared blackboard** | All agents read from and write to a single shared storage location, like a collaborative Google Doc where nobody talks to each other directly, but everyone updates the same file | Three agents each write their section of a report to a shared JSON document |
| **Event streaming** | Agents emit events to a central channel; other agents subscribe and react when relevant events arrive, like subscribing to a group chat where you only respond to messages addressed to you | Agent B starts summarizing as soon as Agent A posts a "search complete" event |
| **Race condition** | When two agents read the same data, make decisions based on it, and write back at the same time, potentially overwriting each other's work or acting on stale information | Two agents both claim task #7 from a queue and execute it twice |
| **Deadlock** | A standstill where Agent A waits for Agent B, while Agent B simultaneously waits for Agent A; neither can ever proceed | Agent A holds a database lock waiting for a file that Agent B holds, while B waits for the database |
| **A2A / MCP** | A2A (Agent-to-Agent) is an emerging protocol for how agents discover and delegate to each other; MCP (Model Context Protocol) is the standardized way agents call external tools like databases and APIs | An orchestrator agent uses A2A to delegate a research task to a specialist, which uses MCP to query a paper database |

---

### How Agents Communicate

Message passing between agents is like email between colleagues: you need to agree on a format, a subject line, and what kind of response you expect, or nothing gets understood.  When one agent simply shouts data into the void and another has to guess what it means, the system breaks down quickly.  The three communication primitives below are the fundamental building blocks that real multi-agent frameworks use, and each one solves a different coordination problem.

When multiple agents collaborate on a task, they must exchange information.  There is no single correct way to do this; the right choice depends on the task structure, how frequently agents need to coordinate, and what kinds of failures must be tolerated.

Three fundamental communication primitives appear across multi-agent frameworks:

| Primitive | How It Works | Best For | Failure Mode | Example in Course Tools |
|-----------|-------------|----------|--------------|------------------------|
| **Message passing** | Agent A sends a structured message directly to Agent B; B reads it and responds. Common standards: FIPA ACL (formal performatives, the "speech act" type of the message), JSON-RPC (function-call style), HTTP REST (request and response over the web). | Sequential pipelines; tasks with clear handoffs where one step must complete before the next begins; situations where a response is needed before continuing | Message lost in transit; receiver crashes before reading; malformed message schema that neither agent can parse | Anthropic A2A agent-to-agent calls; MCP tool request/response |
| **Shared blackboard** | All agents read from and write to a common state object (e.g., a JSON document, database, or file). Agents communicate indirectly by changing what they see in the shared state; no direct agent-to-agent messages. | Parallel tasks where multiple agents each contribute a piece of the whole; stigmergic coordination (agents react to changes in the environment rather than to each other) | Race conditions when multiple agents write simultaneously; stale reads where an agent acts on outdated data; one agent accidentally overwrites another's completed work | Shared tool-call memory object; Anthropic shared context window |
| **Event streaming** | Agents emit events (e.g., "search complete," "error occurred") to a bus or stream; other agents subscribe to event types they care about. Producers and consumers are loosely coupled; they never address each other directly. | Loose coupling where producers and consumers should not need to know about each other; broadcast notifications; reactive pipelines where Agent B should act automatically whenever Agent A finishes | Events delivered out of order; subscriber misses events if it was not connected when they were emitted; event schema mismatches between producer and consumer | Server-Sent Events in streaming tool responses; Kafka-style agent coordination |

#### Questions to Work Through

**Question 1.**  In a multi-agent system where three agents all have write access to the same JSON document (shared blackboard), what can go wrong if two agents try to update the same field at the same time?  Describe the problem concretely: what state does the document end up in, and how does that compare to what either agent intended?

*Hint:* Imagine both agents read the field at the same moment (both see `"status": "pending"`), each decides to update it, and each writes their update, but the second write simply overwrites the first.  Think about what gets lost, and whether the final state reflects either agent's intention.

**Question 2.**  FIPA ACL messages include a **performative** field that specifies the communicative intent of the message, for example: `inform` (I am telling you a fact), `request` (I am asking you to do something), `propose` (I am suggesting a deal), `agree`, `refuse`, `query-if`.  What does this add over sending raw JSON? Give one example where knowing the performative changes how the receiving agent should respond.

*Hint:* Consider what a receiving agent would do differently upon receiving `{"type": "inform", "content": "task complete"}` versus `{"type": "request", "content": "task complete"}`.  The performative tells the receiver *what kind of reply or action is expected*, not just what the content says.

**Question 3.**  A research pipeline has three agents: a searcher that queries a database, an analyst that processes results, and a writer that drafts a report.  Under what circumstances would **event streaming** be a better choice than direct message passing between these agents?  Under what circumstances would message passing be the better choice?  Identify the trade-off.

*Hint:* Think about what happens when you want to add a fourth agent (e.g., a fact-checker) to the pipeline.  With message passing, who needs to be updated?  With event streaming, who needs to be updated?  Then think about a situation where the writer must not start until the analyst has fully finished; which primitive enforces that guarantee more naturally?

Choosing the right communication primitive avoids some failures, but once agents share any state at all, a new class of coordination problems emerges that no communication style alone can prevent.

---

### Coordination Problems

Real pipelines fail in predictable ways, and those failure patterns have names.  Distributed systems engineers discovered these problems while building databases in the 1970s and 80s, and multi-agent LLM systems run into exactly the same traps.  Learning the vocabulary now means you can diagnose failures in your own systems instead of spending hours wondering what went wrong.

Multi-agent systems inherit the coordination problems of distributed computing, plus new ones specific to LLM agents.  The four most important coordination problems are:

| Problem | Description | Example with Agents | Prevention Strategy |
|---------|-------------|--------------------|--------------------|
| **Race condition** | Two agents read shared state, both decide to act based on what they read, both write, but the second write overwrites the first, or both take an action that should only happen once | Agent A and Agent B both read a task queue, both claim task #7 as "in progress," and both execute it; the task runs twice and produces duplicate output | Atomic compare-and-swap (write only if the value is still what you read); locking; task queue with acknowledgment; optimistic concurrency with version numbers |
| **Deadlock** | Agent A is waiting for Agent B to finish before it can proceed; Agent B is simultaneously waiting for Agent A. Neither can ever move forward because each holds something the other needs. | Agent A holds a database lock and is waiting for Agent B to release a file lock; Agent B holds the file lock and is waiting for Agent A to release the database lock | Lock ordering (always acquire locks in the same order everywhere in the system); timeouts with retry; lock-free designs; leader arbitration |
| **Priority inversion** | A high-priority agent is blocked waiting for a resource held by a low-priority agent, so the low-priority task effectively determines when the high-priority task runs | A critical summary agent is blocked waiting for a low-priority formatting agent to finish writing to the shared document; the urgent output is delayed by a trivial task | Priority inheritance (the low-priority agent temporarily inherits the high-priority agent's priority while it holds the resource); preemption; avoiding shared resources between agents of different priorities |
| **Consensus failure** | Agents must agree on a value or decision but cannot reach agreement; no majority or quorum forms, leaving the system stuck | Three analyst agents each produce a different numerical summary of the same dataset; the orchestrator cannot determine which to use and must stall or escalate | Quorum protocols (2-of-3 agreement required before proceeding); designated tiebreaker agent; confidence-weighted voting; human-in-the-loop for unresolved conflicts |

Classic distributed systems solutions (developed over decades for databases and networked systems) apply directly to agents:

- **Mutex/lock**: only one agent may write a shared resource at a time; others wait until the lock is released
- **Optimistic concurrency**: agents write freely, but include a version number with every write; if the version has changed since they last read, the write is rejected and they must re-read and retry with fresh data
- **Leader election**: one agent is designated coordinator for a given task or resource; others send requests to the leader rather than acting directly on shared state
- **Vector clocks**: each message carries a logical timestamp that captures which events preceded it, allowing receivers to determine the causal order of events even without synchronized clocks; think of it as a "happened-before" tracker

#### Questions to Work Through

**Question 4.**  Two research agents are both querying the same paper database.  Agent A queries for "machine learning + climate" and Agent B queries for "deep learning + weather."  Both find paper P, which is relevant to both queries.  Both agents independently decide to add paper P to a shared "relevant papers" list.  Describe specifically how a race condition could produce an incorrect final state of the list, and what that incorrect state might look like.

*Hint:* Both agents read the list, see it does not contain paper P, and each decides to append it.  Trace through what the list looks like after both writes complete.  Is paper P listed once or twice?  Does the list reflect what either agent intended?

**Question 5.**  You need to implement a mutex so that only one agent at a time can update a shared JSON document.  The agents communicate over HTTP and do not share memory.  Describe, in concrete steps, how you would implement this mutex.  (Hint: consider what a "lock file" or "lock key" in a database would look like, and how an agent would acquire and release it.)

*Hint:* Think of a "lock token" stored in the database.  An agent acquires the lock by writing its own ID to a special `lock_holder` field, but only if that field is currently empty (an atomic check-and-set).  It releases the lock by clearing the field.  What happens if an agent crashes while holding the lock?  How do you prevent the lock from being held forever?

**Question 6.**  A two-phase commit protocol (2PC) is used in distributed databases to ensure that either all nodes commit a transaction or none do.  Describe the "agent equivalent" of 2PC: a protocol where a group of agents must either all take an action or all abort, with no partial execution.  What would the two phases look like, and who would play the role of the "coordinator"?

*Hint:* Phase 1 is the "can you do this?" round: the coordinator asks each agent to prepare and confirm readiness.  Phase 2 is the "commit or abort" round: only if all agents say yes does the coordinator tell everyone to execute.  What should the coordinator do if even one agent says it cannot proceed?

These coordination problems are not hypothetical; they motivated the development of industry standards that allow real multi-agent systems to interoperate safely across team and organizational boundaries.

---

> **Common Misconception:** Students often assume that if agents each have their own context window and their own prompt, they cannot interfere with each other.  This is only true if agents never share state.  The moment two agents read from and write to the same resource (a file, a database record, a task queue) all the classical coordination problems apply, regardless of how sophisticated the agents are.  The problem is not in the agents' "minds"; it is in the shared resource they both touch.

---

Three agents are collaborating on a report.  Agent A finishes writing its section and writes the string `"DONE"` to a shared status file to signal completion.  Agent B reads the status file before Agent A writes, sees nothing (or sees the old status), concludes the file is empty, and begins writing its own content, overwriting Agent A's completed section.  This scenario is best described as:

[( )] A deadlock, because both agents are waiting for each other; a deadlock requires both agents to be *blocked waiting*, but here Agent B proceeds immediately; neither agent is stuck waiting for the other
[(X)] A race condition caused by missing synchronization between the read and write operations
[( )] A consensus failure, because the agents disagree on the content of the report; consensus failure requires multiple agents to have produced conflicting outputs and be unable to choose; here Agent B simply overwrote Agent A without negotiation
[( )] An example of priority inversion, because Agent B executed before Agent A's higher-priority write completed; priority inversion requires a low-priority agent to *hold a resource* that a high-priority agent is waiting for; here no priority ordering or blocking is involved

---

### The Anthropic Agent-to-Agent (A2A) and MCP Standards

Real-world multi-agent systems need more than clever coordination logic; they need agreed-upon standards so that an orchestrator built by one team can delegate to a specialist built by a completely different team.  The A2A and MCP standards are the industry's current answer to this problem, and they are the foundation of the agent pipelines you will build in this course.

As multi-agent systems move from research prototypes to production, the field has developed emerging standards for how agents should discover, delegate to, and communicate with each other.

**The A2A (Agent-to-Agent) Protocol** addresses three core needs:

1.  **Discovery**: An agent advertises its capabilities in a machine-readable format (its "agent card"), allowing an orchestrator to identify which specialist agent to delegate to for a given subtask, without needing to be pre-programmed with every specialist's capabilities.
2.  **Delegation**: Agent A (the orchestrator) spawns Agent B (a specialist) to handle a subtask, passing it the necessary context.  Crucially, Agent B operates in its own context window; it does not automatically see everything Agent A knows.  The orchestrator must explicitly decide what context to send.
3.  **Trust boundaries**: Agent B cannot exceed the permissions of the user who authorized Agent A. If the user authorized "read-only access to documents," Agent B cannot acquire write access, even if Agent B's own system prompt would otherwise allow it.  This principle prevents privilege escalation through agent delegation.

**MCP (Model Context Protocol)** serves as the standardized tool interface: agents use MCP to call tools (file systems, databases, APIs, other services) in a consistent, discoverable format.  Multi-agent systems can compose MCP servers: one agent's tools can include calling another agent that exposes itself as an MCP server.

**Example pipeline (described as a table):**

| Component | Role | Communicates Via | Tools Used |
|-----------|------|-----------------|------------|
| Orchestrator Agent | Receives the user's task; plans subtasks; delegates to specialist agents; collects and assembles results | A2A delegation to specialists | Task planner; memory store |
| Research Specialist | Finds and summarizes relevant sources from academic databases and the web | A2A (receives task from Orchestrator); MCP tool calls to retrieve documents | Semantic Scholar MCP; web search MCP |
| Analysis Specialist | Processes and interprets research findings; performs calculations or data transformations | A2A (receives task from Orchestrator); MCP tool calls to run code | Code execution MCP; data analysis MCP |
| Writer Specialist | Drafts the final document from the assembled analysis and research | A2A (receives task from Orchestrator); reads from shared blackboard where prior agents wrote results | Document MCP; shared context store |

#### Questions to Work Through

**Question 7.**  The A2A trust boundary rule states that a sub-agent cannot have *more* permissions than its spawning agent (which in turn cannot exceed the permissions of the user who authorized it).  Why is this rule necessary?  Describe a specific attack or failure mode that would be possible if sub-agents could acquire additional permissions not granted to the original user.

*Hint:* Imagine a user grants an orchestrator "read-only" access to their files.  If that orchestrator could delegate to a sub-agent with "read-write" permissions, what could a malicious or buggy sub-agent do that the user never authorized?  Consider that sub-agents might themselves delegate further; how far could permissions escalate without this rule?

**Question 8.**  When Agent A receives a message claiming to be from "Agent B, Research Specialist," how does Agent A know that the message really comes from the legitimate Agent B and not from a malicious actor impersonating it?  Describe at least two mechanisms (one cryptographic and one architectural) that could provide this assurance.

*Hint:* For the cryptographic mechanism, think about how websites prove their identity (TLS certificates, digital signatures).  For the architectural mechanism, think about whether there is a trusted intermediary (like the orchestrator itself) that controls which agents are even allowed to communicate in the system.

**Question 9.**  Agent C is writing a long document section to a shared workspace.  Midway through the write operation, Agent C crashes (network failure, resource exhaustion, or model error).  The shared workspace now contains a partial write: some sections are written, some are absent, and one section ends mid-sentence.  What problems does this cause for the other agents, and describe a protocol (using concepts from Model 2) that would ensure the shared workspace is always in a consistent state even if an agent crashes mid-write.

*Hint:* What do the other agents see when they read the workspace?  Can they tell the difference between "Agent C finished" and "Agent C crashed"?  Look back at the two-phase commit idea from Question 6: how could you apply the same principle to writing a document section?  What would "commit" and "abort" look like here?

---

### Exercises

**Exercise 1.**  Design a shared blackboard schema in JSON for a three-agent report-writing pipeline with a **Researcher**, an **Analyst**, and an **Editor**.  Your schema must include: (a) a task status field for each agent, (b) the content each agent produces, (c) a version number for optimistic concurrency control, and (d) a field for inter-agent notes or flags.  Write the JSON structure with example values and annotate each field with a comment explaining its purpose.

*What to do:* Draft a JSON object that all three agents would share.  Every agent reads the whole document and writes only to its own designated fields.  Include at least one field that a downstream agent uses to know whether an upstream agent has finished.

*Starter hint:* The JSON schema below shows a complete example; notice how the `version` field enables optimistic concurrency (an agent can detect a conflict by checking whether the version changed since it last read), and how the `lock_holder` field provides mutual exclusion for writes:

```json
{
  "version": 3,
  "agents": {
    "researcher": {
      "status": "done",           // "pending" | "in_progress" | "done" | "error"
      "output": "Found 12 papers on...",
      "notes": ""
    },
    "analyst": {
      "status": "in_progress",
      "output": "",
      "notes": "Waiting on researcher"
    },
    "editor": {
      "status": "pending",
      "output": "",
      "notes": ""
    }
  },
  "lock_holder": null             // null means no agent holds the write lock right now
}
```

*You've succeeded when:* The schema makes it possible for the Editor to check whether both the Researcher and Analyst are done before it starts, and makes it impossible (by convention) for two agents to write at the same time.

**Exercise 2.**  Implement a naive "turn-taking" protocol in pseudocode that prevents the race condition from Model 2.  Your protocol should allow the three agents from Exercise 1 to take turns writing to the shared blackboard, ensuring that no two agents write simultaneously.  Include: (a) how an agent requests the turn, (b) how it is granted, (c) how it is released, and (d) what happens if an agent holding the turn crashes.

*What to do:* Write pseudocode (plain English structured like code) that an individual agent would follow before and after every write operation.  Think about the crash case carefully: what is the mechanism that prevents the lock from being held forever?

*Starter hint:* The pseudocode below implements a mutex using atomic compare-and-set; read the crash-handling comment at the bottom carefully, because it addresses the most dangerous failure mode (an agent dies while holding the lock and blocks everyone else forever):

```
function write_to_blackboard(agent_id, field, value):
    # Step 1: acquire the lock
    loop until lock acquired:
        result = atomic_set_if_null("lock_holder", agent_id)
        if result == "success":
            break
        wait(0.5 seconds)  # back off before retrying

    # Step 2: perform the write
    blackboard[field] = value
    increment blackboard["version"]

    # Step 3: release the lock
    blackboard["lock_holder"] = null

    # Crash handling: set a lock_expiry timestamp when acquiring;
    # any agent may steal an expired lock from a crashed holder
```

*You've succeeded when:* Your protocol prevents two agents from writing at the same time and includes a mechanism so a crashed agent does not block the others forever.

**Exercise 3.**  In class, we discussed the "Orchestrator to Specialist" agent pattern.  Map this pattern to *either* the message-passing primitive *or* the shared blackboard primitive from Model 1 (choose one).  Justify your choice: explain why the pattern maps more naturally to your chosen primitive and identify one limitation of that primitive in this context that would push you to consider the other option.

*What to do:* Pick one primitive and draw (or describe) the flow of information in an Orchestrator-Specialist system using only that primitive.  Then honestly identify one scenario where your chosen primitive fails and the other would handle it better.

*Starter hint:* Consider: does the Orchestrator need to wait for each Specialist's response before delegating the next task?  Or can it fire off all delegations at once and collect results later?  Your answer should shape which primitive fits better.

*You've succeeded when:* You have named a specific, concrete limitation (not just "it can be slower") and explained exactly which aspect of the Orchestrator-Specialist pattern that limitation affects.

---

### Reflection Prompt

Distributed systems researchers spent decades (from Lamport's work in the 1970s through the CAP theorem debates of the 2000s) developing protocols for coordination, consistency, and fault tolerance in networked systems.  Multi-agent AI systems face structurally similar problems: concurrent access, partial failures, and the need for consistent shared state.

**Personal level:** Think about a group project you have worked on with other people.  Did you encounter any of the coordination problems from today: race conditions in who was editing the shared document, deadlocks waiting for someone else to respond?  How did your team resolve them, and what "protocol" did you end up following?

**Technical level:** What can the AI agent field learn directly from distributed systems research, and what is new about multi-agent LLM systems that has no clear parallel in classical distributed computing?  (Consider: classical distributed nodes execute deterministic code; LLM agents produce probabilistic outputs.  How does that change coordination?)

**Societal level:** Multi-agent systems are increasingly making decisions that affect real people: approving loans, routing emergency services, flagging content.  If a race condition or consensus failure causes an incorrect outcome, who is responsible?  How should accountability be assigned when the failure is an emergent property of agent interaction rather than a bug in any single agent?

Write a combined reflection of 150-250 words addressing at least two of the three levels.  The Reflector should be prepared to share one specific distributed systems concept the team thinks is most directly applicable to multi-agent LLMs.

---

-> Coming Up Next: In the next activity, we look inside the agents themselves: specifically at how we can explain *why* an agent made the decision it did, and why that turns out to be much harder than it sounds.

---
