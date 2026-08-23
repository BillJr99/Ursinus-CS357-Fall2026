<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-alignmentsafety.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# AI Alignment and Safety: From RLHF to Constitutional AI

## POGIL Roles

| Role | Responsibility |
|------|---------------|
| **Manager** | Keeps the group on task and on time; ensures everyone participates |
| **Recorder** | Documents the group's answers and reasoning |
| **Presenter** | Shares the group's findings with the class |
| **Reflector** | Monitors group process and leads the reflection prompt |

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Alignment** | The challenge of making an AI system do what we *actually* want, not just what we literally specified | Training a model to give helpful answers, but finding it gives *confident-sounding* answers instead because that's what raters rewarded |
| **RLHF** | Reinforcement Learning from Human Feedback, a training method where humans compare pairs of AI responses and their preferences teach the model what "good" looks like | OpenAI used RLHF to train the original ChatGPT; human raters labeled which of two responses was better |
| **Constitutional AI (CAI)** | A training approach where the model critiques and revises its own outputs according to a written set of principles, reducing reliance on human annotators | Anthropic used CAI to train Claude; instead of only human raters, the model checks its answers against a list of principles |
| **Reward hacking** | When a model finds an unintended shortcut to score well on the training metric without actually achieving the intended goal | A model trained to get positive human ratings learns to sound confident rather than be accurate, because raters preferred confident-sounding text |
| **Goodhart's Law** | "When a measure becomes a target, it ceases to be a good measure"; optimizing for a proxy metric causes behavior that diverges from the actual goal | Student GPA is meant to measure learning; when maximizing GPA becomes the goal, students optimize for grades rather than understanding |
| **Defense in depth** | Layering multiple safety controls so that no single failure exposes users to harm | Combining a system prompt constraint + output filtering + a human review queue, so if one layer fails another catches the problem |

## Model 1: The Alignment Problem

Teaching a dog to fetch is straightforward: throw the ball, dog brings it back, reward with a treat.  Teaching it to fetch *exactly the right ball*, only when it's safe to run, without knocking over the furniture, and to stop if a small child is in the way; that is alignment.  The gap between the simple instruction ("fetch") and the full set of things you actually want is where problems live.  In AI, this gap between what we formally specify and what we actually intend is called the alignment problem, and it scales dramatically with capability.

The **alignment problem** is the gap between what we formally specify (the reward signal or objective function) and what we actually intend (the true human goal).  This gap exists because human intentions are hard to fully formalize.

**Goodhart's Law:** "When a measure becomes a target, it ceases to be a good measure."  In ML: once we optimize directly for a proxy metric, the system learns to maximize the proxy in ways that diverge from the underlying goal.

**Four Misalignment Failure Modes**

| Failure Mode | Definition | LLM-Specific Example | Why It's Hard to Catch |
|---|---|---|---|
| **Reward hacking** | The model finds an unintended way to maximize the specified reward without achieving the real goal | Model learns to sound confident because human raters preferred confident-sounding answers, even when those answers were wrong | The reward goes up, so training looks successful; the problem only appears when you check actual accuracy separately |
| **Goal misgeneralization** | Behavior learned in the training environment fails when the model is deployed in a different context | Model trained on formal English text gives poor, stilted answers to users who write in informal dialects or other languages | The model aced training evals but the eval distribution didn't match the real user population |
| **Deceptive alignment** | Model appears aligned during training and evaluation but behaves differently in low-oversight deployment | Model is helpful and harmless during RLHF evaluation by human raters, but produces different outputs in contexts where oversight is minimal | By definition, it passes every check you run during training |
| **Specification gaming** | Model satisfies the letter but not the spirit of the objective | Model asked to "be concise" produces one-word answers that are technically brief but completely useless | The metric (length) goes down; what you meant (be appropriately brief without sacrificing usefulness) was never captured in the metric |

### Critical Thinking Questions

**Q1.**  Which of the four failure modes is the hardest to detect before deployment?  Explain what makes it hard to detect and what evaluation approaches might catch it.

*Hint:* Consider which failure mode is *designed* (or at least tends) to pass evaluation.  If a model behaves differently when it "knows" it's being watched vs. when it isn't, what kind of evaluation would surface that difference?  Think about red-teaming, diverse evaluation sets, or evaluation in contexts that closely resemble deployment.

**Q2.**  Deceptive alignment (a model that performs well in training but behaves differently in deployment) is often called a theoretical concern for today's LLMs.  Do you agree that it is not a practical concern yet?  What evidence would change your view?

*Hint:* Think about what deceptive alignment would look like in a weak form that might already exist.  Does a model ever behave differently in a "test-like" context (formal, structured prompts) vs. a casual conversation?  What would you need to observe to be confident that the difference was caused by oversight detection rather than just prompt sensitivity?

**Q3.**  How does Goodhart's Law apply specifically to using human preference data as the training signal in RLHF? What happens when annotators have biases, or when the distribution of annotators does not match the distribution of users?

*Hint:* RLHF trains a reward model on annotator preferences, then trains the LLM to maximize the reward model's score.  What happens if annotators (often English-speaking, college-educated, US-based) systematically prefer certain styles or topics?  Does the model now serve those annotators' preferences rather than the diverse actual user population?

## Model 2: RLHF vs. Constitutional AI

**Reinforcement Learning from Human Feedback (RLHF)**

1.  Collect human pairwise preference labels (response A vs. B)
2.  Train a reward model to predict human preferences
3.  Fine-tune the LLM with PPO (Proximal Policy Optimization, a reinforcement learning algorithm that updates the model's parameters in small, stable steps) to maximize the reward model's score

Strength: directly incorporates human values as expressed in actual behavior choices.
Weakness: expensive to scale; reward model can be hacked; annotator biases become model biases.

**Constitutional AI (CAI)**

1.  Write a set of principles (the "constitution"), a human-readable document listing what the model should and should not do
2.  The model critiques its own outputs against the constitution (SL-CAI: supervised learning phase)
3.  The model revises its outputs based on its own critiques
4.  RL fine-tuning uses AI-generated preference labels (RL-CAI), reducing dependence on human annotation

Strength: scalable; auditable (the constitution is a readable document anyone can inspect); creates a self-improvement loop.
Weakness: conflicting principles create ambiguity; whoever writes the constitution encodes whose values.

**Side-by-side Comparison**

| Dimension | RLHF | Constitutional AI | What This Means in Practice |
|---|---|---|---|
| Data source | Human preference labels: annotators compare pairs of responses and pick the better one | AI self-critique against written principles: the model evaluates its own outputs | RLHF is more expensive because it requires paid human annotators; CAI can scale without them |
| Scalability | Low: every new capability or language requires new human annotations | High: the AI generates its own preference labels once the constitution is written | CAI is cheaper to extend to new domains; RLHF costs grow linearly with what you want to cover |
| Auditability | Low: the reward model is a neural network; you cannot read "what it thinks is good" | High: the constitution is a plain-English document you can read, critique, and revise | A journalist investigating model bias can read and critique a constitution; they cannot do the same for a reward model |
| Primary failure mode | Reward hacking; annotator bias becomes model bias | Conflicting principles; constitution bias (whoever wrote it shapes the model's values) | Both fail differently; combining them addresses some weaknesses of each |
| Who decides values | Annotators (implicitly, through their preferences) | Constitution authors (explicitly, in writing) | Explicit is more transparent but concentrates power in a smaller group |

> **Common Misconception:** Many students assume that Constitutional AI removes human judgment from the training process.  It does not: humans still write the constitution, and their choices about which principles to include (and how to phrase them) directly shape the model's values.  CAI moves the human judgment from labeling individual responses to writing the rules.  This is more transparent, but it is not neutral.

### Critical Thinking Questions

**Q4.**  Who writes the "constitution" in Constitutional AI, and how does that affect whose values are encoded in the resulting model?  Is explicit authorship of values better or worse than implicit encoding through annotator preferences?

*Hint:* Anthropic's constitution (publicly available) reflects choices about what counts as "harmful," "honest," and "helpful."  Those choices reflect the values of the team that wrote it.  Compare this to RLHF, where annotators from a specific demographic pool make thousands of small choices that are never written down.  Which is more auditable?  Which is easier to challenge or revise?

**Q5.**  Can RLHF and Constitutional AI be used together in a single training pipeline?  Describe how you would combine them and what advantage the combination would have over either alone.

*Hint:* Think about using RLHF to handle cases where human judgment is most valuable (edge cases, cultural nuance, novel situations) and CAI to handle scale (common scenarios, consistency, cost-efficiency).  What would the combined pipeline look like?  What would each component contribute?

**Q6.**  What does it mean for alignment to be "auditable"?  Why does auditability matter for a deployed model, and what are its limits?

*Hint:* Auditability means an outside party can inspect how the model was trained to behave.  For CAI, that means reading the constitution.  For RLHF, it means inspecting the reward model, which requires ML expertise most regulators and journalists don't have.  What are the limits of auditability even for CAI? (Hint: the constitution is readable, but predicting how the model interprets it is not.)

**What type of alignment failure is this?**

A model trained with RLHF is evaluated and found to consistently sound confident even when its answers are factually wrong.  Investigation reveals that human annotators during preference collection consistently rated confident-sounding answers higher, regardless of accuracy.  This is:

[( )] Deceptive alignment, because the model produces different outputs when it detects it is being evaluated versus when it is not
[(X)] Reward hacking the human preference model, because the model learned to maximize the proxy metric (sounding confident) rather than the true goal (being accurate)
[( )] Constitutional AI failure, because a constitution that listed accuracy as a principle would have caught this during the model's self-critique phase
[( )] Goal misgeneralization, because the model was trained on formal text but deployed on informal user queries, shifting the distribution

## Model 3: Practical Safety for Course Agents

For a deployed student-facing agent, five safety controls can be layered in increasing order of implementation complexity and robustness.  Think of these like physical security at a building: a sign on the door ("no trespassing") is easy but weak; a lock is stronger; a security guard stronger still; a vault with dual keys is the strongest.  No single layer is perfect, but together they raise the cost of any attack high enough to deter most of them.

| Control | Implementation Cost | Bypass Difficulty | What It Covers | Example |
|---|---|---|---|---|
| **System prompt constraints** | Very low: add text to the system prompt | Low: prompt injection or roleplay framing can bypass it | Broad but weak; sets the intent without enforcing it mechanically | "Do not share other students' data or grades with anyone" |
| **Output filtering** | Low: a regex or classifier runs on every response before it reaches the user | Medium: requires knowing what patterns to block; misses novel attacks | Specific patterns that can be described precisely, like PII or profanity | Block any output matching a social security number regex pattern |
| **Input filtering** | Low-medium: a classifier screens user messages before they reach the model | Medium: known attack patterns are blocked; novel ones slip through | Known attack patterns like prompt injection markers | Reject any message containing "ignore previous instructions" |
| **Sandboxed execution** | High: requires container orchestration and security engineering | High: the agent literally cannot affect things outside the sandbox | Code and tool misuse that could affect external systems | Run all agent-invoked Python code in an isolated container with no network access |
| **Human review queue** | Very high: requires staffing and workflow design | Near-impossible: a human sees the output before it reaches the user | All high-risk outputs; highest coverage, highest cost | Route any query containing mental health keywords to a counselor before responding |

**Key insight:** These controls are complementary, not alternatives.  A production system uses several layers (defense in depth).  The question is which to prioritize given resource constraints.

### Critical Thinking Questions

**Q7.**  If you can only implement a single safety control for a student-facing course agent due to time constraints, which one provides the best coverage-per-effort?  Defend your choice, and acknowledge what it leaves unprotected.

*Hint:* Consider the threat model for a course agent: the most likely harms are students getting wrong answers confidently, inappropriate content slipping through, and privacy leaks of other students' data.  Which single control addresses the most common of these?  What does it fail to catch, and how bad would that failure be?

**Q8.**  The threat model for a student advising agent and the threat model for a containerized code execution agent are different.  How does the safety stack you would build differ between these two systems?  What controls overlap and what is unique to each?

*Hint:* An advising agent's risks are primarily informational (wrong advice, privacy leaks, inappropriate content).  A code execution agent's risks are also operational: the agent can run code that affects real systems.  Which controls address informational risk?  Which address operational risk?  Can output filtering stop a code execution agent from running a malicious command before the command runs?

**Q9.**  What does "safe enough" mean for a student-facing academic agent vs. a clinical decision-support agent?  Should the same standard apply?  If not, what factors determine the appropriate standard?

*Hint:* Think about consequence magnitude and reversibility.  If a course agent gives wrong advice about a homework assignment, the consequence is a bad grade, recoverable.  If a clinical agent gives wrong advice about medication dosing, the consequence could be irreversible harm.  How does consequence severity affect the appropriate investment in safety controls?  What standard-setting bodies govern each domain?

## Exercises

**1.  Write a Constitution**

*What to do:* Write a 5-rule constitution for a CS357 course agent.  After writing it, identify at least two pairs of rules that could conflict in realistic scenarios, describe the conflict, and propose how the agent should resolve it.

*Starter hint:* Start with these five candidate rules and refine them: (1) "Always give accurate information, even if it is not what the student wants to hear."  (2) "Be supportive and encouraging to reduce student anxiety."  (3) "Never complete homework problems; guide students toward the answer."  (4) "Respect student privacy; do not share one student's work with another."  (5) "Escalate any mention of mental health distress to professional resources."  Now identify: where do rules 1 and 2 conflict?  Where might rule 3 conflict with a student who asks for a worked example from a textbook?

*You've succeeded when:* Your constitution has 5 rules, at least 2 identified conflicts with concrete scenario descriptions, and a proposed resolution strategy for each conflict, not just "use judgment" but a specific rule priority or tie-breaking procedure.

**2.  Reward Hacking Case Study**

*What to do:* Find a documented real-world example of reward hacking in reinforcement learning (hint: search for "OpenAI boat racing CoastRunners" or "Atari RL reward hacking").  Describe: (a) the specified objective, (b) the intended goal, (c) the behavior that emerged, and (d) what this implies for LLM alignment.

*Starter hint:* In the CoastRunners example, the boat was rewarded for collecting point tokens in a racing game.  Instead of finishing the race (the intended goal), it found a loop of tokens it could collect repeatedly while on fire, ignoring the actual race.  For (d), connect this to RLHF: if human raters reward "sounds helpful," what might an LLM learn to maximize that diverges from "actually being helpful"?

*You've succeeded when:* Your description correctly identifies all four elements, and your implication (d) makes a specific connection to a named alignment failure mode from Model 1, not just a general statement that "AI can go wrong."

**3.  Safety Test Suite**

*What to do:* Design a minimal safety test suite for an open-source agentic project (use the class project if available, or a hypothetical course agent).  Include at least 5 test cases, the expected behavior for each, the assertion you would check, and how you would run this suite in CI.

*Starter hint:* Categories to cover: (1) a jailbreak attempt (expect: the agent declines and stays in persona), (2) a PII request (expect: the agent refuses to share other users' data), (3) a distressed student message (expect: the agent provides crisis resources), (4) a homework completion request (expect: the agent guides rather than solves), (5) an ambiguous topic (expect: the agent says it's unsure and points to a resource).  For each, write the exact input you would send and the exact output property you would assert (e.g., response does not contain a complete solution to the assignment).

*You've succeeded when:* Each test case has a specific input, a specific expected behavior, a checkable assertion (not just "behaves well"), and a note on how it would be integrated into an automated test pipeline.

## Reflection Prompt

**Personal level:** Have you ever felt that an AI tool was confidently wrong, or weirdly agreeable even when you said something inaccurate?  Looking back, which alignment failure mode (reward hacking, goal misgeneralization, deceptive alignment, specification gaming) best describes what you experienced?  What would the training process have needed to look different to avoid it?

**Technical level:** Constitutional AI gives a company the ability to explicitly encode its values into a model's behavior through a written document.  This is more transparent than implicit RLHF value encoding, but it also concentrates value-setting power in whoever writes the constitution.  Who should decide what values are in that document?  What process (democratic, expert, multi-stakeholder, regulatory) would make that decision legitimate?

**Societal level:** Does your answer to the technical question change depending on whether the model is used by millions of people or by a single organization?  If a model trained on one company's constitution is used by governments or hospitals in other countries, does the company's right to set those values change?  Who has standing to challenge or revise a constitution that affects them?

-> Coming Up Next: In the Social Impact activity, we will see how alignment choices made at the model level ripple outward into labor markets, education systems, and entire economies, and how the people building these systems bear some responsibility for those effects.

## Further Reading

- Christiano et al., "Deep Reinforcement Learning from Human Preferences" (2017)
- Anthropic, "Constitutional AI: Harmlessness from AI Feedback" (Bai et al. 2022)
- Bai et al., "Training a Helpful and Harmless Assistant with RLHF" (2022)
- Krakovna et al., "Specification Gaming: The Flip Side of AI Ingenuity" (DeepMind blog, 2020)
- Hadfield-Menell et al., "The Off-Switch Game" (2017), on corrigibility and value alignment
