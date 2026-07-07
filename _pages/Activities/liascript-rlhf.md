<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-rlhf.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-rlhf.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# From Rewards to Preferences: Reinforcement Learning and RLHF

Before language models could be aligned to human values, AI researchers had to solve a more fundamental problem: how do you teach an agent to make good decisions when you cannot write down every rule? The answer — reinforcement learning — turns out to be both powerful and tricky to harness for the subtlety of human preferences. In this activity we trace the path from **basic RL mechanics $\rightarrow$ Q-learning intuition $\rightarrow$ the RLHF training loop $\rightarrow$ DPO as a simpler alternative $\rightarrow$ Constitutional AI**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

| Role | Responsibility |
|------|----------------|
| **Manager** | Keeps the group on task and on time; ensures everyone participates |
| **Recorder** | Documents the group's answers and reasoning |
| **Presenter** | Shares the group's findings with the class |
| **Reflector** | Monitors group process and leads the reflection prompt |

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Reinforcement Learning (RL)** | A training paradigm where an agent learns by taking actions in an environment and receiving numerical rewards or penalties — no labeled answers needed, just trial and error | A model is given the action of generating a response; a human rates it; the rating (reward) adjusts the model's future behavior |
| **MDP (Markov Decision Process)** | The formal framework for RL: a set of states, a set of actions, a reward function, and a policy — the four components that define any sequential decision problem | States = conversation history; actions = next token; reward = human preference score; policy = the language model itself |
| **Policy** | The function an agent uses to choose actions — maps each state to a probability distribution over possible actions | GPT generates text according to a policy: given prior tokens (state), the policy outputs a probability over the next token (action) |
| **Q-learning** | An RL algorithm that learns the expected future reward of taking each action in each state — the Q-table stores this "quality" score | Q("hungry", "eat sandwich") = high; Q("hungry", "juggle bowling pins") = low |
| **Exploration-exploitation tradeoff** | The tension between trying new actions (exploration, to discover better rewards) and repeating known good actions (exploitation, to collect reward now) | A model trained only on exploitation always generates its top-1 response; exploration occasionally generates unusual responses that turn out to be better |
| **RLHF** | Reinforcement Learning from Human Feedback — the process of training a reward model on human preference labels, then using RL (PPO) to maximize that reward model's score | OpenAI trained the original ChatGPT with RLHF; humans picked which of two responses was better, and the model was updated toward the preferred response |
| **PPO (Proximal Policy Optimization)** | The RL algorithm most commonly used in RLHF — it updates the model's parameters in small, controlled steps to avoid destabilizing the policy | PPO constrains each parameter update to be close to the previous policy, preventing the model from forgetting everything it knew after a single bad batch |
| **DPO (Direct Preference Optimization)** | A training method that skips the reward model and PPO entirely — it directly adjusts model weights using preference pairs, making RLHF-style training dramatically simpler | Instead of training a separate reward neural network and then running PPO, DPO uses a single mathematical loss function applied straight to the preference data |
| **Constitutional AI (CAI)** | An alignment approach where the model critiques and revises its own outputs according to a written list of principles, generating AI-labeled preference data that replaces or supplements human annotators | Anthropic's Claude is trained with CAI: the model reads its own draft response, asks "does this violate principle #4?", revises it, and the revised response is treated as the preferred output |
| **KL divergence** | A measure of how different two probability distributions are — in RLHF/PPO, it constrains the updated policy to stay close to the base model, preventing "reward hacking" the reward model | If KL divergence is not constrained, the model quickly learns to produce responses that fool the reward model while becoming gibberish to real users |

---

# Part I: Reinforcement Learning Fundamentals

In this part, you will build intuition for how reinforcement learning works — why it is fundamentally different from supervised learning, how the four components of an MDP interact, and why the exploration-exploitation tradeoff is unavoidable. These concepts are prerequisites for understanding why RLHF is structured the way it is.

## 1. Teaching Without Labels

**Why this matters:** Supervised learning requires a correct answer for every training example. But for many valuable behaviors — writing a compelling essay, choosing a good chess move, keeping a conversation helpful over many turns — no single "correct" answer exists. Reinforcement learning sidesteps this by replacing correct answers with reward signals, making it possible to train behaviors that are easy to evaluate but hard to specify. Every major alignment technique used to train today's large language models (RLHF, DPO, Constitutional AI) builds on this foundation.

Imagine you are training a dog versus programming a vending machine. Programming a vending machine is supervised learning: you write exact rules for every input ("if coin ≥ 50¢ and button = B3, dispense soda"). There is a perfectly correct output for every input. The dog is different. You do not hand the dog a manual — you give it treats for behaviors you liked and ignore (or discourage) behaviors you didn't. Over many repetitions, the dog builds a model of what earns rewards. It generalizes: a dog trained to sit on command will often also learn to sit politely before its food bowl without being explicitly taught.

Reinforcement learning formalizes the dog-training insight. An **agent** (the dog, or the LLM) lives in an **environment** (your living room, or a conversation), observes the current **state** (the dog sees you reaching for the treat bag; the LLM sees the conversation history), takes an **action** (the dog sits; the LLM generates a token), and receives a **reward** (a treat; a human preference rating). The agent's goal is to learn a **policy** — a function from states to actions — that maximizes total expected reward over time.

The four components — **states (S)**, **actions (A)**, **rewards (R)**, and **policy (π)** — together with a rule for how states transition to new states when actions are taken, define a **Markov Decision Process (MDP)**. Every sequential decision problem that RL addresses can be described as an MDP.

---

## Model 1: The RL Loop

The RL training loop, applied to a language model:

| Loop Step | Symbol | What It Means for an LLM |
|-----------|--------|---------------------------|
| Observe state | $s_t$ | The conversation so far (all prior tokens, system prompt, etc.) |
| Choose action | $a_t \sim \pi(s_t)$ | Sample the next token from the model's current probability distribution |
| Environment transitions | $s_{t+1}$ | The token is appended; the new state is the extended conversation |
| Receive reward | $r_t$ | A human (or reward model) rates the completed response |
| Update policy | $\pi \leftarrow \pi + \Delta$ | Adjust model weights so actions that led to high reward become more probable |

The Markov property — "the current state contains all information needed for the decision" — means history beyond the current state is ignored. For LLMs, the "state" is the context window, and the Markov property holds approximately (a longer context window is a better state representation).

### Critical Thinking Questions

**Q1.** An LLM generates a 200-token response to a user question. The human rates the complete response with a score of 8 out of 10. Identify the state, action(s), and reward for this interaction using the MDP vocabulary. Is the action a single 200-token generation, or 200 individual token choices? What does your answer imply about how credit is assigned for good responses?

> *Hint: Consider that the reward (8/10) arrives at the end, but the 200 tokens were chosen sequentially. This is the "credit assignment problem" in RL — which of the 200 actions deserves credit for the high score? In practice, the reward is typically applied to the full generation as a single episode. Why might this be inaccurate?*

**Q2.** Contrast the vending machine (supervised) with the dog (RL) metaphor. Name a specific NLP task that is better framed as supervised learning and explain why. Then name a specific NLP task that is better framed as RL and explain why. Your two examples should differ in whether a "correct" output can be specified in advance.

> *Hint: For supervised learning, think about a task where a human expert could write out the correct output for any given input. For RL, think about a task where "correctness" depends on user satisfaction, long-term conversation quality, or criteria that vary across users — things that are easier to judge than to specify.*

**Q3.** What happens if the reward function is imperfect? Describe a realistic way the reward function used in RLHF (human preference ratings) could be systematically wrong, and predict what the trained model's behavior would look like after training on that flawed signal.

> *Hint: Think about what human annotators actually reward when they rate AI responses: clarity, confidence, length, politeness, or agreement with the user's premise — even when the user's premise is wrong. If annotators consistently rate confident-sounding responses higher than accurate-but-hedged responses, what does the model learn?*

---

## 2. Q-Learning Intuition and the Exploration-Exploitation Tradeoff

**Why this matters:** Q-learning is the conceptual foundation for how RL agents decide which actions are worth taking — not just in games, but in the RLHF training process. The exploration-exploitation tradeoff is fundamental to why alignment training is hard: a model trained only to exploit its current best responses never discovers better ones, but a model that explores too much generates dangerous or unhelpful outputs.

**Q-learning** builds a table — the Q-table — that stores the expected total future reward of taking each action $a$ in each state $s$. The Q-value $Q(s, a)$ answers the question: "if I am in state $s$ and take action $a$, how much total reward can I expect, on average, from here onward?"

A simple way to update Q-values after observing a transition $(s, a, r, s')$:

$$Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \cdot \max_{a'} Q(s', a') - Q(s, a) \right]$$

where $\alpha$ is the learning rate (how much to update per step), $\gamma$ is the discount factor (how much future rewards are worth relative to immediate rewards), and $\max_{a'} Q(s', a')$ is our best estimate of the future from the new state. The term in brackets is the **temporal difference error**: the gap between what we expected and what we actually got plus future prospects.

For language models, Q-learning in its raw form is intractable — the state space (all possible token sequences) and action space (the full vocabulary at each step) are astronomically large. Instead, modern RLHF uses PPO, which approximates Q-learning with neural networks and additional stability constraints. But the Q-learning intuition — "assign credit for actions that lead to good futures" — remains the conceptual core.

**The exploration-exploitation tradeoff** is unavoidable in any RL system. If the agent always exploits — always choosing the action with the highest current Q-value — it may miss better actions it has never tried. If it always explores — choosing randomly to discover new actions — it never uses what it has learned and accumulates low rewards. The standard solution is an **epsilon-greedy** policy: with probability $\epsilon$, choose randomly (explore); with probability $1 - \epsilon$, choose the current best action (exploit). Decreasing $\epsilon$ over training is called **annealing**: explore a lot early, exploit more late.

---

## Model 2: Q-Values by Hand

A toy Q-table for a tiny two-state ("question-answering" vs. "question-pending"), two-action ("answer directly", "ask clarifying question") chatbot:

| State | Action | Current Q-value |
|-------|--------|-----------------|
| question-answering | answer directly | 7.0 |
| question-answering | ask clarifying question | 3.0 |
| question-pending | answer directly | 1.0 |
| question-pending | ask clarifying question | 9.0 |

### Critical Thinking Questions

**Q4.** Using the Q-table above: in the "question-pending" state, which action does an epsilon-greedy policy with $\epsilon = 0.1$ choose 90% of the time? If the agent chose "answer directly" in this state and received reward 2, with $\alpha = 0.5$ and $\gamma = 0.9$, compute the updated Q-value using the formula above (assume $\max_{a'} Q(\text{question-answering}, a') = 7.0$).

> *Hint: The formula is $Q(s,a) \leftarrow Q(s,a) + \alpha [r + \gamma \cdot \max_{a'} Q(s',a') - Q(s,a)]$. Plug in: $Q = 1.0$, $\alpha = 0.5$, $r = 2$, $\gamma = 0.9$, $\max_{a'} Q = 7.0$. Compute the bracket first, then multiply by $\alpha$, then add to the old Q.*

**Q5.** Why is applying Q-learning directly to language generation intractable? Estimate the size of the Q-table for a model with a 50,000-token vocabulary generating responses up to 500 tokens long. What architectural change would you need to make Q-learning feasible at this scale?

> *Hint: The Q-table has one entry per (state, action) pair. The state is the full token sequence seen so far; the action is the next token. If responses can be up to 500 tokens and the vocabulary has 50,000 entries, how many possible states are there? (Think $50000^{500}$ — an astronomically large number.) What replaces the table in deep RL?*

**Q6.** In the context of RLHF for language models, what plays the role of "exploration" and what plays the role of "exploitation"? How does the temperature parameter from our sampling activity connect to this tradeoff?

> *Hint: Exploitation in LLM RLHF means generating the model's current best responses. Exploration means occasionally generating lower-probability responses to discover if they are actually better. Recall from the sampling activity that temperature controls how peaked or flat the sampling distribution is. High temperature = more exploration; low temperature = more exploitation.*

**Which of the following correctly lists all four components of a Markov Decision Process?**

[[MC]]
- ( ) Agent, environment, training data, loss function
- ( ) Policy, gradient, learning rate, optimizer
- (x) States, actions, rewards, and policy (or equivalently, a transition function)
- ( ) Supervised labels, features, model weights, evaluation metric

---

# Part II: RLHF and DPO

In this part, you will trace the full RLHF training pipeline — from supervised fine-tuning through reward model training to PPO — and understand why DPO emerged as a simpler alternative. You will also simulate the preference data collection process in code to see concretely what RLHF's input data looks like before any neural network touches it.

## 3. The RLHF Training Loop

**Why this matters:** RLHF is how GPT-4, Claude, Gemini, and virtually every production LLM is aligned to be helpful, harmless, and honest. Understanding its structure — and its failure modes — is essential for anyone building on top of these models, because the RLHF pipeline shapes not just safety behavior but also style, verbosity, confidence, and subtle biases that affect every downstream application. The PPO complexity motivating DPO is also a live area of ML systems engineering.

The RLHF pipeline has three distinct training phases, each building on the last:

**Phase 1: Supervised Fine-Tuning (SFT).** Start with a pretrained base model (trained on raw internet text) and fine-tune it on a curated dataset of high-quality demonstrations — human-written responses to a diverse set of prompts. This teaches the model roughly what good responses look like before RL begins. Without SFT, the RL signal is too weak: the base model generates too much garbage for preference labels to be informative.

**Phase 2: Reward Model Training.** Collect pairs of model responses to the same prompt, have human annotators pick which response is better, and train a separate neural network (the reward model, RM) to predict those preferences. The RM takes a (prompt, response) pair and outputs a scalar score — higher is better. The RM generalizes from the labeled pairs to score any new response.

**Phase 3: PPO Fine-Tuning.** Use Proximal Policy Optimization — a policy gradient RL algorithm — to update the language model's weights to maximize the reward model's predicted scores. A crucial constraint: the PPO update includes a KL divergence penalty that keeps the updated model from drifting too far from the SFT model. Without this constraint, the model rapidly learns to generate gibberish that happens to fool the reward model (reward hacking), since the RM is itself an imperfect proxy for human preferences.

The three-phase structure creates significant practical challenges: you need separate training infrastructure for the SFT model, the reward model, and the PPO training loop; PPO requires loading both the policy model and a frozen reference copy in memory simultaneously; and the RM can be hacked if RL runs too long. These difficulties motivated the search for simpler alternatives.

---

## Model 3: RLHF Loop Diagram

| Phase | Input | Process | Output |
|-------|-------|---------|--------|
| **1. SFT** | Raw pretrained model + human demonstrations | Supervised fine-tuning on curated (prompt, response) pairs | SFT model: knows roughly how to respond helpfully |
| **2. Reward Model** | SFT model + human preference labels (A > B for same prompt) | Train a separate classifier to predict human preferences | Reward model (RM): scores (prompt, response) pairs |
| **3. PPO** | SFT model + reward model | RL loop: generate responses, score with RM, update policy; KL penalty keeps policy near SFT model | Aligned model: maximizes RM scores while staying coherent |

> **⚠️ Common Misconception:** Many students assume the reward model *is* the language model, or that RLHF means "training the model to get positive ratings." In reality, RLHF trains a *separate* reward model on human preference data, then uses that reward model as the environment's reward signal in an RL loop that updates the *language model*. There are three models involved: the SFT model, the reward model, and the PPO-updated policy.

### Critical Thinking Questions

**Q7.** The KL divergence penalty in PPO constrains the updated model to stay close to the SFT base model. Why is this constraint necessary? What would happen if PPO were run for thousands of steps without the KL penalty, given that the reward model is an imperfect neural network?

> *Hint: The reward model learned to predict human preferences from a finite dataset. It is a neural network, not a perfect oracle. If the policy model is optimized to maximize the RM's score without constraint, it will eventually find responses that score very high on the RM but that look nothing like what humans actually prefer — because the RM has blind spots and attack surfaces. This is reward hacking applied to a learned reward function.*

**Q8.** Compare the annotation bottleneck in RLHF (humans must label preference pairs) to the annotation bottleneck in supervised learning (humans must provide correct answers). Which bottleneck is easier to scale past, and why? What does this imply for the quality of the reward model as the dataset grows?

> *Hint: Pairwise preference judgments ("A or B?") are easier for annotators than generating correct answers from scratch ("write the ideal response"). This makes RLHF data slightly cheaper to collect. But the reward model quality still depends on annotator agreement and diversity — if annotators consistently disagree, the RM trains on noisy labels. What techniques (majority vote, calibration, inter-annotator agreement scores) might help?*

**Q9.** DPO (Direct Preference Optimization) eliminates the reward model and the PPO training loop. It applies a single loss function directly to (prompt, chosen-response, rejected-response) triples. What practical advantages does this give a team running RLHF-style training? What capability does DPO lose by removing the explicit reward model?

> *Hint: Practical advantages of DPO: only one model needs to be loaded at training time (not two), no RL training instability, simpler infrastructure. What does the explicit reward model give you that DPO's implicit reward doesn't? Think about the ability to score arbitrary new responses at inference time — if you wanted to use reward model scores for best-of-N sampling (generate N responses, return the one with the highest RM score), can you still do this with DPO?*

---

## 4. Simulating Preference Data Collection

**Why this matters:** Before any neural network is trained, RLHF requires collecting preference labels from humans. This code cell simulates that process at small scale — given pairs of model responses, you will label which you prefer, compute a naive reward score from those labels, and rank the responses. This is concretely what annotation platforms like Scale AI or Surge AI do at industrial scale to produce the training data that shapes every production LLM.

The code below generates three prompt-response pairs, simulates a human labeling session, computes naive reward scores by counting "preferred" votes, and ranks the responses.

## Code Cell

```python
# Simulating RLHF preference data collection
# Run this cell to see preference data structure and naive reward scoring

import random

random.seed(42)

# Three prompts, each with two candidate responses (A and B)
# Imagine these were generated by two slightly different model versions
preference_pairs = [
    {
        "prompt": "Explain what a neural network is.",
        "response_A": "A neural network is a computational system loosely inspired by biological neurons. It consists of layers of interconnected nodes that transform input data through weighted sums and nonlinear activation functions, learning those weights from examples via backpropagation.",
        "response_B": "Neural networks are amazing! They basically think like a brain and can do anything. You just give them data and they learn. Super powerful stuff.",
    },
    {
        "prompt": "What should I do if my Python code raises a KeyError?",
        "response_A": "A KeyError means you tried to access a dictionary key that does not exist. Check your key spelling, use .get(key, default) to provide a fallback, or check membership with 'if key in my_dict' before accessing it.",
        "response_B": "Just wrap everything in a try/except block. That way errors won't crash your program.",
    },
    {
        "prompt": "Is reinforcement learning the same as supervised learning?",
        "response_A": "No. Supervised learning requires labeled examples of correct outputs. Reinforcement learning requires only a reward signal after taking actions — there is no labeled 'correct' answer, only feedback on what worked.",
        "response_B": "They are both machine learning, so yes, kind of the same. Both use data to train models.",
    },
]

# --- SIMULATE ANNOTATION ---
# In real RLHF, humans see both responses and choose the better one.
# Here we hardcode "ground truth" preferences to simulate a labeled dataset.
# 1 = A is better, 0 = B is better

ground_truth_preferred = [1, 1, 1]  # A is better in all three (inspect the text above!)

# Compute naive reward scores: count how many times each response was preferred
reward_scores = {}
for i, pair in enumerate(preference_pairs):
    preferred = "A" if ground_truth_preferred[i] == 1 else "B"
    rejected  = "B" if ground_truth_preferred[i] == 1 else "A"
    reward_scores[f"Pair {i+1} Response {preferred}"] = reward_scores.get(
        f"Pair {i+1} Response {preferred}", 0) + 1
    reward_scores[f"Pair {i+1} Response {rejected}"] = reward_scores.get(
        f"Pair {i+1} Response {rejected}", 0)

print("=== Preference Data Summary ===\n")
for i, pair in enumerate(preference_pairs):
    preferred_label = "A" if ground_truth_preferred[i] == 1 else "B"
    rejected_label  = "B" if ground_truth_preferred[i] == 1 else "A"
    print(f"Prompt {i+1}: {pair['prompt'][:60]}...")
    print(f"  Preferred: Response {preferred_label}")
    print(f"  Rejected:  Response {rejected_label}")
    print()

print("=== Naive Reward Scores (fraction of times preferred) ===\n")
# Compute win rate per response (out of 1 comparison each)
total = len(preference_pairs)
wins_A = sum(ground_truth_preferred)
wins_B = total - wins_A
print(f"  Response A total wins: {wins_A}/{total}  (naive reward score: {wins_A/total:.2f})")
print(f"  Response B total wins: {wins_B}/{total}  (naive reward score: {wins_B/total:.2f})")

print()
print("=== What a real reward model would do ===")
print("  A reward model (RM) is trained on thousands of these (prompt, chosen, rejected) triples.")
print("  It learns to assign a scalar score to any (prompt, response) pair.")
print("  PPO then updates the language model to generate responses the RM scores highly.")
print()

# --- STUDENT EXERCISE: change ground_truth_preferred to disagree with one pair ---
print("=== STUDENT EXERCISE ===")
print("Edit ground_truth_preferred to flip one judgment (e.g., [1, 0, 1])")
print("Then re-run. What does this mean for the training signal the reward model receives?")
print("Which response in pair 2 is actually better? Do you agree with the annotation?")
```

---

## Model 4: Reading Preference Data

### Critical Thinking Questions

**Q10.** Examine the three prompt-response pairs in the code cell. For Pair 2 (KeyError), Response B ("just use try/except") is shorter and pragmatic — some annotators might prefer it for brevity. How would annotator disagreement on this pair affect the reward model trained downstream? Does the "right" answer depend on who the user is?

> *Hint: If 60% of annotators prefer A (specific debugging guidance) and 40% prefer B (try/except shortcut), the reward model receives a noisy training signal for this pair. The RM might learn a low-confidence score difference for responses like these. How might the model's output change if it were deployed for novice programmers vs. experienced engineers?*

**Q11.** The naive reward score computed in the code is simply the fraction of comparisons a response won. A real reward model is a neural network trained to predict these preferences. Name two ways a neural reward model is strictly more powerful than the naive win-rate score, and one way it can be worse.

> *Hint: More powerful: (1) the RM can score a response it has never seen before by generalizing from the training data; the naive score requires direct comparison. (2) The RM can capture subtle quality dimensions. Worse: the RM can be fooled — it has blind spots, and optimizing against it for too long leads to reward hacking.*

**Q12.** Change `ground_truth_preferred` in the code to `[1, 0, 1]` (making Response B preferred for Pair 2). Re-examine the printed output. Write one sentence describing what the training signal now implies about the quality of "use try/except everywhere" — and whether you agree.

> *Hint: With [1, 0, 1], the training data tells the reward model that a vague, catch-all error-handling suggestion is preferred over a specific, diagnostic answer. If this bias appeared in a large-scale annotation study, what would a production LLM trained on it learn to do when asked debugging questions?*

---

# Part III: Constitutional AI and the Alignment Tension

In this part, you will examine Constitutional AI — the alignment approach that replaces (or supplements) human preference annotators with an AI critic guided by written principles — and grapple with the fundamental tension between alignment (making models safe and helpful) and raw capability (making models maximally powerful).

## 5. Constitutional AI: Replacing Annotators with Principles

**Why this matters:** Human annotation is expensive, slow, and biased toward the demographics of the annotation pool. Constitutional AI (CAI) addresses this by shifting the human judgment from labeling individual responses to writing a document of principles — and then having the model itself apply those principles to generate preference data. This is the approach Anthropic used for Claude. Understanding CAI helps you see alignment not as a black box but as an auditable, revisable process.

Constitutional AI operates in two stages:

**Stage 1 (SL-CAI): Supervised Learning with AI Feedback.** The model is given a potentially harmful prompt and generates an initial response. Then, it is shown the response alongside a randomly sampled principle from the constitution (e.g., "Choose the response that is less likely to contain harmful, unethical, racist, sexist, toxic, dangerous, or illegal content") and asked to critique its own response. It then revises the response based on the critique. The original and revised responses form a (chosen, rejected) pair for supervised fine-tuning.

**Stage 2 (RL-CAI): Reinforcement Learning with AI Feedback.** The model generates pairs of responses. An AI feedback model (often a prompted version of the same or a more capable model) evaluates which response better satisfies a constitutional principle and produces preference labels. These AI-generated labels train a preference model (equivalent to RLHF's reward model) without requiring human annotation. PPO or DPO then fine-tunes the model against this AI-generated preference model.

The result: a model that has been trained on thousands of critique-and-revision cycles and preference comparisons, all generated by the model itself according to explicit, human-readable principles.

---

## Model 5: CAI vs. RLHF Comparison

| Dimension | RLHF | Constitutional AI | What This Means in Practice |
|-----------|------|-------------------|-----------------------------|
| **Preference data source** | Human annotators pick between pairs of responses | AI evaluates pairs against written principles | CAI is cheaper to scale; RLHF more directly captures diverse human intuitions |
| **Transparency of values** | Implicit — encoded in annotator choices, never written down | Explicit — the constitution is a readable document anyone can inspect | A CAI constitution can be audited, challenged, and revised; RLHF reward models cannot be "read" |
| **Scalability** | Scales with annotation budget — expensive | Scales with compute — once the constitution is written, AI generates unlimited preference data | CAI can be extended to new domains by adding principles; RLHF requires new human annotation |
| **Primary failure mode** | Reward hacking; annotator bias | Conflicting principles; bias in the constitution itself | Both fail differently; production systems often combine both |
| **Who encodes values** | Annotators (implicitly, through choices) | Constitution authors (explicitly, in writing) | CAI's values are more legible but concentrate power in the team that writes the constitution |

> **⚠️ Common Misconception:** Students often assume Constitutional AI eliminates human judgment from alignment. It does not — humans still write the constitution, and the specific wording of each principle directly shapes how the model resolves edge cases. The difference is *where* the human judgment occurs: at the level of individual response labels (RLHF) versus at the level of general principles (CAI). CAI makes values more transparent but does not make them more neutral.

### Critical Thinking Questions

**Q13.** What happens when two principles in a constitution conflict? For example: Principle 3 says "prefer responses that are honest, even if the truth is uncomfortable" and Principle 7 says "prefer responses that are kind and avoid causing emotional distress." Describe a realistic prompt where these two principles produce opposite preference rankings for the same pair of responses.

> *Hint: Imagine a user who has submitted code for review and asks "is this good code?" The code has significant architectural problems. A response following Principle 3 might say "this code has serious issues in X, Y, and Z." A response following Principle 7 might say "great start! Here are some areas to develop." Which is "preferred" depends entirely on which principle is sampled. How should a constitution specify priority among conflicting principles?*

**Q14.** The alignment vs. capability tension: some researchers argue that RLHF and CAI make models safer but also make them less capable — more hedging, more refusals, more diplomatic non-answers. Others argue that a well-aligned model is more useful precisely because it is more reliable. What empirical evidence would you want to see to distinguish these two positions?

> *Hint: Think about what you would measure. If alignment reduces capability, you would expect aligned models to score lower on factual question-answering benchmarks, coding tasks, and mathematical reasoning — tasks where there is a clear correct answer that doesn't require social judgment. If alignment improves usefulness, you would expect aligned models to score higher on user satisfaction and task completion in real-world settings. Can both be true simultaneously for different task types?*

**Q15.** Suppose you are tasked with writing a five-principle constitution for a CS357 course assistant. The assistant helps students with programming assignments, but must not complete assignments for them. Write two principles that directly address this tension, and then describe a student query where your two principles conflict.

> *Hint: One principle might be "prefer responses that help students understand the underlying concept without providing a complete solution to the assignment problem." Another might be "prefer responses that are maximally helpful and give students the specific guidance they ask for." Now consider a student who asks: "Can you write the first 10 lines of my assignment for me to get me started?" Which principle wins?*

---

## Exercises

**1. Design a Reward Model Training Set**

*What to do:* Create a mini reward model training dataset: write 5 (prompt, response-A, response-B, preferred) quadruples for a CS course assistant. Each prompt should be a plausible student question. Your responses should differ in a specific, identifiable dimension (accuracy, specificity, length, hedging, or helpfulness). For each pair, explain in one sentence why you labeled the preferred response as preferred, and identify which RLHF failure mode your labeling might accidentally introduce if extended to thousands of examples.

*Starter hint:* Categories of prompts to cover: (1) a factual CS question, (2) a debugging request, (3) a conceptual question about AI, (4) a request to complete an assignment, (5) an ambiguous or vague question. For each, write response A that is clearly better on one dimension and response B that is better on another — then force yourself to choose and explain why. This simulates the ambiguity real annotators face.

*You've succeeded when:* You have 5 complete quadruples, 5 one-sentence justifications, and 5 identified potential biases — and at least one of your identified biases maps to a specific failure mode from Part I (reward hacking, goal misgeneralization, specification gaming, or deceptive alignment).

**2. RLHF vs. DPO Implementation Comparison**

*What to do:* Research and summarize the key implementation differences between PPO-based RLHF and DPO fine-tuning. Specifically: (a) how many models must be loaded in GPU memory simultaneously for each approach, (b) what training infrastructure each requires (distributed training, separate reward model server, etc.), (c) which open-source libraries support each approach (search for Hugging Face TRL, OpenRLHF, or LLaMA-Factory), and (d) give one scenario where DPO is clearly the better choice and one where PPO-based RLHF remains necessary.

*Starter hint:* DPO requires only the policy model and a frozen reference model (same size) simultaneously — 2× model memory. PPO additionally requires the reward model and a value network — roughly 4× model memory for a similarly-sized RM. For (d), DPO cannot score arbitrary new responses at inference time, so best-of-N sampling (a common RLHF inference technique) requires an explicit reward model.

*You've succeeded when:* Your summary addresses all four points with specific numbers or library names where applicable, and your two scenarios are concrete (not generic statements like "when you need quality").

**3. Write and Test a Mini Constitution**

*What to do:* Write a 6-principle constitution for an AI assistant deployed in a hospital triage context (not a diagnosis tool — a scheduling and information assistant). Then: (a) identify two pairs of principles that could conflict, (b) write a concrete patient query that triggers each conflict, and (c) propose a priority ordering (which principle wins) with a justification for each. Finally, explain how you would empirically validate that the assistant trained on your constitution actually follows your intended priority ordering.

*Starter hint:* Candidate principles to start from: (1) "prefer responses that accurately describe the scheduling system's capabilities without overpromising," (2) "prefer responses that reduce patient anxiety and stress," (3) "prefer responses that direct emergency situations to emergency services immediately," (4) "prefer responses in the patient's language if detectable," (5) "prefer responses that protect patient privacy," (6) "prefer responses that are concise to minimize reading time for distressed patients." Now identify where 1 and 2 conflict, where 2 and 6 conflict, and so on.

*You've succeeded when:* Your constitution has 6 principles, two identified conflicts with concrete patient queries, a priority ordering with justification, and a specific empirical validation procedure — not just "test it and see" but a specific test prompt set, evaluation metric, and success threshold.

---

## Reflection Prompt

**Personal:** Think about a time a person — a tutor, a mentor, a parent — gave you feedback that felt harsh in the moment but was actually helpful in hindsight. Then think of a time feedback was technically positive (encouraging, agreeable) but ultimately unhelpful or misleading. Which of these failure modes — reward hacking (optimizing for approval rather than accuracy) or specification gaming (satisfying the letter of a rule but not the spirit) — best describes the unhelpful feedback you received? What would a "better reward function" for that human relationship have looked like?

**Technical:** RLHF encodes values through annotator choices; Constitutional AI encodes them through written principles. Both reflect the values of whoever designs the system. In your notebook: identify one value you personally hold that you think would be hard to encode in either approach, and explain specifically why (too contextual? too culturally specific? depends on information the model cannot access? requires long-term reasoning the annotation process cannot capture?).

**Societal:** Constitutional AI's principles are written by teams at AI companies — currently Anthropic, primarily. These principles affect billions of people who had no input into the document. Is this fundamentally different from values encoded in laws, professional codes of ethics, or platform content policies? Who should have standing to participate in writing a model's constitution, and what process — democratic vote, expert committee, multistakeholder negotiation, or regulatory approval — would make that participation legitimate?

---

## → Coming Up Next

In the next activity we examine how the transformer architecture and attention mechanism actually learn from pre-training data — and how scaling laws (the relationship between model size, dataset size, and performance) determine why the largest models are trained the way they are.

---

## 6. Further Reading

- Christiano et al. "Deep Reinforcement Learning from Human Preferences." *NeurIPS* (2017). The foundational RLHF paper.
- Bai et al. "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback." Anthropic (2022).
- Bai et al. "Constitutional AI: Harmlessness from AI Feedback." Anthropic (2022).
- Rafailov et al. "Direct Preference Optimization: Your Language Model is Secretly a Reward Model." *NeurIPS* (2023). The DPO paper.
- Sutton and Barto. *Reinforcement Learning: An Introduction* (2nd ed., 2018). Chapters 1–6 cover MDP, Q-learning, and the exploration-exploitation tradeoff.

> **Sources:** This activity draws on material from *AI Engineering from Scratch* (Phases 9, 10, and 18) and the "ML Animated" YouTube series (Reinforcement Learning chapters), supplemented by the primary papers listed above.
