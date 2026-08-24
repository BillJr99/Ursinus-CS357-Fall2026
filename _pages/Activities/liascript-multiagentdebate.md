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

4.  Did any round 1 agent fall for the intuitive-but-wrong answer of 15 dollars?  Did exposure to the other agents' reasoning in round 2 repair the error (converging toward 10) or spread the error (pulling correct agents toward 15)?  Quote the decisive sentence from the transcript that shows which happened.

   > *Hint: Look at round 2 transcripts for any agent that changed its answer.  Did the agent that changed provide a clear reason for the change?  Is "the other agents said 10 so I will too" a good reason?  What distinguishes persuasion by evidence from persuasion by social pressure?*

5.  Round 1 uses temperature 0.9 and round 2 uses temperature 0.5.  Explain this scheduling as an "explore then commit" strategy: what does each temperature level accomplish, and what would go wrong at temperature 0.0 everywhere?

   > *Hint: At 0.0, every independent agent produces the same answer (the model's mode).  If that mode answer is wrong, all agents start with the same wrong answer and there is nothing to debate.  What is the minimum diversity you need in round 1 for debate to be possible?*

6.  Majority vote treats all agents as equal regardless of the quality of their reasoning.  Sketch the judge-agent alternative: write out the system prompt the judge would use, and explain which pattern from earlier in the course a judge agent most resembles.

   > *Hint: The judge reads everyone's reasoning, not just their final answers.  A judge that can explain why it chose one answer over another is more useful than a vote counter.  Which agent role from the critique-and-refine activity does this most closely resemble?*

> **Common Misconception:** Many students assume that more agents and more rounds always produce more accurate results.  This is only true if (a) the agents' errors are independent and (b) the question has a verifiable ground truth that correct reasoning can converge toward.  For questions with correlated errors (all agents have the same bias) or no ground truth (matters of opinion), more debate may only produce more confident wrong answers.  The research paper that introduced this protocol (Du et al., 2023) reports accuracy gains on specific benchmark tasks; those gains do not automatically transfer to every question type.  Always measure, do not assume.

Part III gives you the structured experiments to generate those measurements yourself, replacing claims about debate with data.

Multi-agent debate most reliably improves accuracy when:

[( )] All agents run at temperature 0 for consistency
[( )] The question requires recalling one rare fact
[(X)] Errors across agents are partially independent and flaws in a wrong answer are easier to verify than to avoid
[( )] The agents share a single context window

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
