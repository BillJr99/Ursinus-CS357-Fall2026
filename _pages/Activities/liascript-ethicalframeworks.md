# Ethical Frameworks for Agentic AI Systems
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-ethicalframeworks.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ethicalframeworks.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Ethical Frameworks for Agentic AI Systems

Abstract commitments to building "fair and beneficial AI" are not enough — every team with a catastrophic product has made such commitments. What distinguishes thoughtful from reckless AI development is the capacity to apply specific ethical frameworks at design time: before deployment, before harm, before someone else decides for you. Today you learn to use three classical frameworks as design tools, map the ACM Code of Ethics to concrete agentic choices, and grapple with the structural tensions that no framework resolves cleanly. The goal is not ethical certainty but ethical literacy: knowing which considerations apply, where they conflict, and how to reason in public about your decisions.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Manager ensures the team takes the scenarios seriously rather than settling for the first defensible position; the Recorder documents where frameworks agree, where they conflict, and why; the Presenter will argue one position to the class and defend it against objections; the Reflector watches for reasoning that treats a framework as a trump card rather than a lens, and names it. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Three Frameworks, One Scenario

## 1. From "Move Fast" to Irreversibility

The "move fast and break things" ethos originated in software contexts where the dominant risk was irrelevance: ship before competitors, iterate on live feedback, treat reversibility as the default. The calculation changes fundamentally for autonomous agents. When an agent sends an email, executes a financial transaction, deletes a file, or denies a loan application, the action persists in the world after the agent has moved on. **Irreversibility** and **blast radius** — the scope of potential harm — are the primary variables that determine how much caution a design requires.

**Three ethical frameworks** each illuminate a different dimension of this problem:

*Utilitarianism* evaluates actions by their consequences: the right action produces the greatest aggregate well-being. Applied to AI, this framework demands rigorous impact assessment — who benefits, who is harmed, at what probability, at what magnitude — and justifies constraining an agent's behavior when expected harms exceed expected benefits. Its weakness is that it licenses harmful actions to individuals when the aggregate calculation favors them, and it requires predicting consequences that may be unknowable.

*Deontological ethics* (Kant, and its contemporary descendants including rights-based frameworks) holds that some actions are wrong regardless of their consequences. Persons have rights that constrain what agents may do to them; these constraints do not bend to sufficiently large utilitarian payoffs. Applied to AI, this framework prohibits deceiving users, violating privacy, or denying due process even when doing so would maximize aggregate outcomes. Its weakness is that rules can conflict and that rigid rules produce obviously bad outcomes in edge cases.

*Virtue ethics* asks not "what rule applies?" or "what outcome maximizes welfare?" but "what would a person of good character do here?" A virtuous AI designer exhibits practical wisdom (*phronesis*): the capacity to perceive morally relevant features of a situation and respond appropriately without reducing the situation to a rule lookup. This framework demands attention to relational and contextual features that the other two abstract away, but provides less action-guidance in novel cases.

---

## Model 1: One Action, Four Verdicts

An AI agent is instructed to write a maximally persuasive essay arguing for a contested political position (e.g., a specific immigration policy, a tax proposal) on behalf of a client. The essay will be distributed at scale via social media.

| Framework | Analysis | Conclusion |
|---|---|---|
| Utilitarian | Benefits: client achieves political goal, potentially influences policy toward (in client's view) better outcomes. Harms: large-scale manipulation of public deliberation, reduced epistemic autonomy of readers, potential for disinformation ecosystem effects. Expected aggregate harm likely exceeds benefit at scale. | Agent should decline or substantially constrain the task |
| Deontological | Readers have a right not to be manipulated; persuasion that exploits psychological vulnerabilities rather than engaging reason violates this right regardless of outcome. The agent as instrument of manipulation is doing something categorically wrong. | Agent should refuse the persuasion framing; informing or arguing is permissible, maximally persuading is not |
| Virtue Ethics | A person of practical wisdom would ask: is this the kind of work that a trustworthy advisor would perform? Scale amplifies the stakes. A virtuous designer would build in friction, disclosure, and a constraint against techniques that exploit rather than engage. | Agent may draft an argument but must disclose AI origin, avoid dark-pattern rhetoric, and flag techniques that bypass rather than engage deliberation |
| Design Justice | Who is not at the table? Those most affected by the policy being argued may have had no input into the agent's design, training, or deployment. Scale effects fall asymmetrically on less powerful groups. | Requires stakeholder analysis before deployment; at minimum, the agent should not be deployed for advocacy that targets vulnerable or underrepresented communities without their participation in design |

### Critical Thinking Questions

1. The frameworks reach similar conclusions here but via different routes and with different residual permissions. Identify one decision the agent's designer must make that is *permitted* by deontological ethics but *prohibited* by design justice principles. What does this gap reveal about the completeness of any single framework?
2. Virtue ethics demands practical wisdom in novel situations. Name two features of the persuasive-essay scenario that a rule-based system could not perceive without something analogous to contextual judgment, and explain how you would engineer a proxy for each.
3. The utilitarian analysis depends on predicting aggregate effects of persuasion at scale. This is genuinely hard to do. Does epistemic uncertainty about consequences weaken the utilitarian argument for refusal, or strengthen it? (Consider: what is the expected-value calculation when the harm distribution has a heavy tail?)

---

# Part II: The ACM Code of Ethics as Design Specification

## 2. From Principles to Mechanisms

The ACM Code of Ethics (2018) is a professional commitment document, not a legal instrument, but its clauses are specific enough to function as design requirements when read against a concrete agentic system. The exercise of mapping code clauses to design choices surfaces requirements that would otherwise remain implicit.

Selected clauses with agentic implications:

**1.1 Contribute to society and human well-being.** An agent must be evaluated not only for whether it satisfies its direct user's request but for its effects on non-users and on social systems. An agent that optimizes a hiring pipeline for speed may satisfy its immediate user while degrading fairness for applicants who never interact with the system.

**1.2 Avoid harm.** Computing professionals should take care to avoid harm to others, and when harm is a likely outcome, they are obligated to report it. For agentic systems: who reviews whether harm is a "likely outcome" and when does that review occur?

**1.6 Respect privacy.** Agents that collect, store, or transmit data as a side effect of their operation are doing something the users may not understand. A coding assistant that logs all user code to improve the model is collecting data beyond what the interaction requires.

**2.5 Give comprehensive and thorough evaluations.** This clause requires honest assessment of one's own work — including failure modes and limitations — before deployment. It prohibits shipping a system with known serious defects while representing it as fit for purpose.

**3.1 Ensure that the public good is the central concern.** When organizational pressures conflict with public interest, professionals must recognize the conflict, document it, and escalate.

---

## Model 2: Code-to-Design Mapping

| ACM Code Clause | Design Obligation for an Agentic System | Concrete Implementation |
|---|---|---|
| 1.1 Contribute to societal well-being | Evaluate effects on non-users and on social systems, not only direct users | Stakeholder analysis before deployment; third-party impact assessment for high-risk uses |
| 1.2 Avoid harm | Identify likely harm scenarios before deployment; build detection and reporting | Pre-mortem analysis; automated anomaly flags; human escalation paths; incident logging |
| 1.6 Respect privacy | Minimize data collection to what the task requires; disclose what is collected | Data minimization by design; clear user-facing disclosure of logging; opt-out for non-essential collection |
| 2.5 Thorough evaluations | Test the system on failure modes, edge cases, and adversarial inputs before deployment | Red-teaming; disaggregated evaluation; performance reporting by subgroup |
| 3.1 Public good is central | Document and escalate when organizational pressure conflicts with public interest | Dissent channels; ethics review gates before deployment; documentation of override decisions |

### Critical Thinking Questions

4. Clause 2.5 requires "comprehensive and thorough evaluations." Apply this to your course project: what would a thorough evaluation require that you have not yet done? Name at least three tests and explain why each is necessary.
5. Clause 3.1 creates a professional obligation that may conflict with employment obligations. Under what conditions would you, personally, be willing to act on clause 3.1 against organizational pressure? What would need to be true about the harm, the organizational response, and your alternatives?
6. The ACM Code is a list of principles, not a decision procedure. When two clauses conflict — for example, satisfying a user's explicit request (1.1 serving the user) conflicts with avoiding harm to a third party (1.2) — the Code does not resolve the conflict. Who should? What mechanism would you build into an agentic system to surface and escalate such conflicts?

[[MC]]
An agent is designed to help users write performance reviews for their employees. Which design choice best satisfies both ACM clause 1.2 (avoid harm) and clause 2.5 (thorough evaluations)?
- ( ) Deploy immediately and collect feedback from dissatisfied employees after the fact
- ( ) Add a disclaimer stating that the agent's output is not the company's official position
- (x) Before deployment, test the agent's outputs across a diverse set of simulated employees and managers, specifically checking for disparate treatment by demographic group, and document results in a pre-deployment report
- ( ) Limit the agent to suggesting language from a pre-approved phrase library

---

# Part III: Minimal Footprint, Alignment, and Corrigibility

## 3. The Architecture of a Well-Behaved Agent

**The minimal footprint principle** holds that an autonomous agent should: request only the permissions necessary for the current task; prefer reversible actions over irreversible ones when both achieve the goal; and escalate to a human when uncertain rather than taking a low-confidence autonomous action. The principle operationalizes corrigibility — the property of being correctable — as an engineering constraint rather than a post-hoc aspiration.

The contrast case is a **maximum-capability agent**: one designed to request all permissions it might ever need, act on low-confidence judgments to maintain throughput, and avoid escalation because escalation is treated as a failure mode rather than a feature. Maximum-capability agents are built under time pressure, by teams that treat human oversight as friction, and in competitive environments where the first agent to act wins. They also cause the most harm at scale.

**Alignment** refers to the correspondence between an agent's operational objective and the values of its principals. A misaligned agent pursues a proxy objective that diverges from principal intent under distribution shift — the conditions not represented in training or specification. Value-sensitive design is the practice of eliciting stakeholder values *before* constructing the objective, to reduce the gap between what the agent optimizes and what its principals actually want.

**The dual newspaper test** (a practical heuristic): before deploying an agent action, ask two questions. (1) Would this action, if described accurately in a technology journalist's story about AI harm, embarrass the organization? (2) Would *refusing* to take this action, if described in a civil liberties reporter's story about paternalistic AI, embarrass the organization? Both failure modes are real; the test guards against both.

---

## Model 3: Minimal vs. Maximum Footprint

Two agents are given the same task: "Help a user manage their email inbox." Consider two design philosophies implemented for this task.

| Design Dimension | Minimal Footprint Agent | Maximum Capability Agent |
|---|---|---|
| Permissions requested | Read-only access to inbox; write access only to draft folder | Full read/write/delete access to inbox, contacts, calendar, and sent mail |
| Action on uncertain classification | Flag email for human review; explain uncertainty | Delete or archive based on best guess; log action |
| Escalation policy | Escalates any action affecting more than 10 emails or any irreversible delete | Never escalates; autonomy is a feature |
| Response to ambiguous instruction | Requests clarification before proceeding | Infers intent and proceeds; may be wrong |
| Audit trail | Every action logged with rationale and confidence | Actions logged; rationale not stored |
| Recovery from error | Drafts folder preserves all changes; user can review and undo | Deletions are permanent; no undo path |

### Critical Thinking Questions

7. A critic argues that the minimal footprint agent is less useful because it interrupts the user more often. Construct the strongest version of this argument, then rebut it using the asymmetry between the cost of unnecessary interruptions and the cost of irreversible errors.
8. **Value-sensitive design** requires eliciting stakeholder values before building. For the email agent, identify at least three stakeholder groups beyond the direct user, describe one value each holds that the direct user might not prioritize, and explain how that value would change a design choice.
9. Apply the dual newspaper test to the maximum-capability email agent. Write the first sentence of both the harm story and the paternalism story. Does the test give you a clear answer about which design is preferable, or does it surface a genuine tension? If the latter, how do you resolve it?

---

# Part IV: Synthesis

## Exercises

1. *Pre-deployment ethics review.* For your course project, conduct a structured ethics review using all three frameworks from Part I. For each framework, identify: (a) one design choice your project makes that the framework endorses, and (b) one design choice or capability the framework would require you to constrain. Write one paragraph per framework.
2. *Footprint audit.* List every permission, API scope, and data access your project agent currently requests. For each, classify it as: (a) necessary for current functionality, (b) useful but not necessary, or (c) requested as a precaution for future features. Propose the reduced permission set that retains (a) only, and describe what you would need to add back and why if you retained any (b) items.
3. *Stakeholder map.* For your project, identify at least five stakeholder groups, including groups who are affected by the system's outputs but do not interact with it directly. For each group, name one value they hold and one design constraint that value implies. Compare the constraint list: where are there conflicts, and how does your current design resolve (or fail to resolve) them?

---

## Reflection Prompt

In your notebook: Vallor (2016) argues that virtue ethics is the most appropriate framework for technology ethics because technology shapes character — habitual use of tools trains dispositions, and dispositions determine how we respond to situations that rules and calculations cannot anticipate. Reflect on your experience this semester building and using AI systems: have any of your habitual ways of working, thinking about problems, or evaluating your own judgment changed? If so, in what direction? If virtue ethics is right that this matters, what follows for how the course should be taught?

---

## Further Reading

- Vallor, S. *Technology and the Virtues: A Philosophical Guide to a Future Worth Wanting.* Oxford University Press (2016). The most accessible book-length argument for virtue ethics as an AI ethics framework.
- ACM. *Code of Ethics and Professional Conduct* (2018). acm.org/code-of-ethics. Read in full; the case studies are the most useful part.
- Costanza-Chock, S. *Design Justice: Community-Led Practices to Build the Worlds We Need.* MIT Press (2020), chapters 1–2.
- Gabriel, I. "Artificial Intelligence, Values, and Alignment." *Minds and Machines* 30: 411–437 (2020). A careful analysis of what alignment requires beyond stated preferences.
