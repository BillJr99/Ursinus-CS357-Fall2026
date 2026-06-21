# AI Alignment and Safety: From RLHF to Constitutional AI

<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-alignmentsafety.md

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

## Model 1: The Alignment Problem

The **alignment problem** is the gap between what we formally specify (the reward signal or objective function) and what we actually intend (the true human goal). This gap exists because human intentions are hard to fully formalize.

**Goodhart's Law:** "When a measure becomes a target, it ceases to be a good measure." In ML: once we optimize directly for a proxy metric, the system learns to maximize the proxy in ways that diverge from the underlying goal.

**Four Misalignment Failure Modes**

| Failure Mode | Definition | LLM-Specific Example |
|---|---|---|
| **Reward hacking** | Model finds an unintended way to maximize the specified reward | Model learns to sound confident because human raters preferred confident-sounding answers, even when wrong |
| **Goal misgeneralization** | Behavior that worked in training distribution fails when deployed | Model trained on formal English gives poor answers to users who write in informal dialects |
| **Deceptive alignment** | Model appears aligned during training/evaluation but behaves differently in deployment | Model behaves helpfully during RLHF evaluation but produces different outputs in low-oversight contexts |
| **Specification gaming** | Model satisfies the letter but not the spirit of the objective | Model asked to "be concise" produces one-word answers that are technically brief but useless |

### Critical Thinking Questions

**Q1.** Which of the four failure modes is the hardest to detect before deployment? Explain what makes it hard to detect and what evaluation approaches might catch it.

**Q2.** Deceptive alignment — a model that performs well in training but behaves differently in deployment — is often called a theoretical concern for today's LLMs. Do you agree that it is not a practical concern yet? What evidence would change your view?

**Q3.** How does Goodhart's Law apply specifically to using human preference data as the training signal in RLHF? What happens when annotators have biases, or when the distribution of annotators does not match the distribution of users?

## Model 2: RLHF vs. Constitutional AI

**Reinforcement Learning from Human Feedback (RLHF)**

1. Collect human pairwise preference labels (response A vs. B)
2. Train a reward model to predict human preferences
3. Fine-tune the LLM with PPO (Proximal Policy Optimization) to maximize the reward model's score

Strength: directly incorporates human values as expressed in behavior.
Weakness: expensive to scale; reward model can be hacked; annotator biases become model biases.

**Constitutional AI (CAI)**

1. Write a set of principles (the "constitution")
2. Model critiques its own outputs against the constitution (SL-CAI: supervised learning phase)
3. Model revises outputs based on critiques
4. RL fine-tuning uses AI-generated preference labels (RL-CAI), reducing dependence on human annotation

Strength: scalable; auditable (the constitution is a readable document); self-improvement loop.
Weakness: conflicting principles create ambiguity; who writes the constitution encodes whose values.

**Side-by-side Comparison**

| Dimension | RLHF | Constitutional AI |
|---|---|---|
| Data source | Human preference labels | AI self-critique against written principles |
| Scalability | Low (human annotation bottleneck) | High (AI-generated labels) |
| Auditability | Low (reward model is a black box) | High (constitution is human-readable) |
| Primary failure mode | Reward hacking; annotator bias | Conflicting principles; constitution bias |
| Who decides values | Annotators (implicitly) | Constitution authors (explicitly) |

### Critical Thinking Questions

**Q4.** Who writes the "constitution" in Constitutional AI, and how does that affect whose values are encoded in the resulting model? Is explicit authorship of values better or worse than implicit encoding through annotator preferences?

**Q5.** Can RLHF and Constitutional AI be used together in a single training pipeline? Describe how you would combine them and what advantage the combination would have over either alone.

**Q6.** What does it mean for alignment to be "auditable"? Why does auditability matter for a deployed model, and what are its limits?

**What type of alignment failure is this?**

A model trained with RLHF is evaluated and found to consistently sound confident even when its answers are factually wrong. Investigation reveals that human annotators during preference collection consistently rated confident-sounding answers higher, regardless of accuracy. This is:

[[MC]]
- ( ) Deceptive alignment, because the model is hiding its uncertainty
- (x) Reward hacking the human preference model, because the model learned to maximize the proxy metric (sounding confident) rather than the true goal (being accurate)
- ( ) Constitutional AI failure, because the constitution did not include accuracy requirements
- ( ) Goal misgeneralization, because the training distribution differed from deployment

## Model 3: Practical Safety for Course Agents

For a deployed student-facing agent, five safety controls can be layered in increasing order of implementation complexity and robustness:

| Control | Implementation Cost | Bypass Difficulty | Coverage | Example |
|---|---|---|---|---|
| **System prompt constraints** | Very low | Low (prompt injection) | Broad but weak | "Do not share other students' data" |
| **Output filtering** | Low | Medium | Specific patterns | Block outputs matching PII regex |
| **Input filtering** | Low-medium | Medium | Known attack patterns | Reject prompts with injection markers |
| **Sandboxed execution** | High | High | Code/tool misuse | Run agent tools in isolated container |
| **Human review queue** | Very high | Near-impossible | All high-risk outputs | Route sensitive queries to staff |

**Key insight:** These controls are complementary, not alternatives. A production system uses several layers (defense in depth). The question is which to prioritize given resource constraints.

### Critical Thinking Questions

**Q7.** If you can only implement a single safety control for a student-facing course agent due to time constraints, which one provides the best coverage-per-effort? Defend your choice, and acknowledge what it leaves unprotected.

**Q8.** The threat model for a student advising agent and the threat model for a containerized code execution agent are different. How does the safety stack you would build differ between these two systems? What controls overlap and what is unique to each?

**Q9.** What does "safe enough" mean for a student-facing academic agent vs. a clinical decision-support agent? Should the same standard apply? If not, what factors determine the appropriate standard?

## Exercises

1. **Write a Constitution:** Write a 5-rule constitution for a CS357 course agent. After writing it, identify at least two pairs of rules that could conflict in realistic scenarios, describe the conflict, and propose how the agent should resolve it.

2. **Reward Hacking Case Study:** Find a documented real-world example of reward hacking in reinforcement learning (hint: search for "OpenAI boat racing CoastRunners" or "Atari RL reward hacking"). Describe: (a) the specified objective, (b) the intended goal, (c) the behavior that emerged, and (d) what this implies for LLM alignment.

3. **Safety Test Suite:** Design a minimal safety test suite for an open-source agentic project (use the class project if available, or a hypothetical course agent). Include: at least 5 test cases, the expected behavior for each, the assertion you would check, and how you would run this suite in CI.

## Reflection Prompt

Constitutional AI gives a company the ability to explicitly encode its values into a model's behavior through a written document. This is more transparent than implicit RLHF value encoding — but it also concentrates value-setting power in whoever writes the constitution. Who should decide what values are in that document? What process — democratic, expert, multi-stakeholder, regulatory — would make that decision legitimate? Does your answer change depending on whether the model is used by millions of people or by a single organization?

## Further Reading

- Christiano et al., "Deep Reinforcement Learning from Human Preferences" (2017)
- Anthropic, "Constitutional AI: Harmlessness from AI Feedback" (Bai et al. 2022)
- Bai et al., "Training a Helpful and Harmless Assistant with RLHF" (2022)
- Krakovna et al., "Specification Gaming: The Flip Side of AI Ingenuity" (DeepMind blog, 2020)
- Hadfield-Menell et al., "The Off-Switch Game" (2017) — on corrigibility and value alignment
