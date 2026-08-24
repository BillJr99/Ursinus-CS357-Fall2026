<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357-Fall2026/blob/gh-pages/_pages/Activities/liascript-ethicalframeworks.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-ethicalframeworks.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Ethical Frameworks for Agentic AI Systems

Abstract commitments to building "fair and beneficial AI" are not enough; every team with a catastrophic product has made such commitments.  What distinguishes thoughtful from reckless AI development is the capacity to apply specific ethical frameworks at design time: before deployment, before harm, before someone else decides for you.  Today you learn to use three classical frameworks as design tools, map the ACM Code of Ethics to concrete agentic choices, and grapple with the structural tensions that no framework resolves cleanly.  The goal is not ethical certainty but ethical literacy: knowing which considerations apply, where they conflict, and how to reason in public about your decisions.

---

## Directions and Group Roles

Work in your POGIL team with your rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**).  The Manager ensures the team takes the scenarios seriously rather than settling for the first defensible position; the Recorder documents where frameworks agree, where they conflict, and why; the Presenter will argue one position to the class and defend it against objections; the Reflector watches for reasoning that treats a framework as a trump card rather than a lens, and names it.  After class, please respond to the reflective prompt on your own in your notebook.

---

### Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Utilitarianism** | An ethical framework that judges actions by their consequences: the right action is the one that produces the greatest total well-being across all affected people. It requires estimating who is helped, who is harmed, by how much, and at what probability. | Deciding whether to deploy an AI writing assistant requires estimating: how much it helps users, how much harm it causes to writers whose work it displaces, and whether the aggregate is positive. |
| **Deontological Ethics** | An ethical framework that holds some actions are right or wrong regardless of their consequences, because persons have rights that constrain what may be done to them. The focus is on duties and rules, not outcomes. | Deceiving a user about whether they are talking to an AI is wrong under deontological ethics even if the deception makes them feel better, because persons have a right not to be manipulated. |
| **Virtue Ethics** | An ethical framework that asks not "what rule applies?" or "what outcome maximizes welfare?" but "what would a person of good character do here?" It emphasizes practical wisdom, the capacity to recognize morally relevant features of a novel situation. | A virtuous AI engineer, encountering a client request to build manipulative persuasion tools, recognizes the request as something a trustworthy professional would decline, without needing a rule to tell them so. |
| **Design Justice** | A framework that centers the perspectives and interests of communities most affected by technology in the design process, particularly communities that have historically been excluded from design decisions but disproportionately bear the costs of design failures. | An AI hiring tool designed without input from applicants (who are not "users" of the system but are its primary subjects) may optimize for recruiter convenience while systematically disadvantaging certain candidate groups. |
| **Minimal Footprint Principle** | The engineering principle that an autonomous agent should request only the permissions needed for the current task, prefer reversible over irreversible actions, and escalate to a human when uncertain, rather than maximizing capability and autonomy. | An email management agent that requests read-only inbox access and drafts suggestions for human approval has a smaller footprint than one that requests full read/write/delete access and acts autonomously. |
| **Dual Newspaper Test** | A practical heuristic for checking whether an AI design decision has gone wrong in either direction: (1) would accurate reporting of this action embarrass the organization as an AI harm story? (2) would accurate reporting of a refusal embarrass the organization as a paternalistic AI story? Both failure modes are real. | An agent that refuses to help a nurse look up drug interactions fails the second test; one that autonomously adjusts medication dosages fails the first. |

---

# Part I: Three Frameworks, One Scenario

In this part, you will apply three classical ethical frameworks (utilitarianism, deontological ethics, and virtue ethics) to the same concrete scenario, learning to use each as a lens that reveals a different dimension of the design decision.

## 1.  From "Move Fast" to Irreversibility

The "move fast and break things" ethos works in a narrow domain: software contexts where the cost of a mistake is quickly reversible and the dominant risk is shipping too slowly.  That calculation changes fundamentally when the agent's actions persist in the world after the agent has moved on.  An email sent, a loan denied, a file deleted, a medication prescribed: these cannot be un-done with a patch.  Learning to apply ethical frameworks before deployment is how you catch the irreversible harms before they happen.

The "move fast and break things" ethos originated in software contexts where the dominant risk was irrelevance: ship before competitors, iterate on live feedback, treat reversibility as the default.  The calculation changes fundamentally for autonomous agents.  When an agent sends an email, executes a financial transaction, deletes a file, or denies a loan application, the action persists in the world after the agent has moved on.  **Irreversibility** and **blast radius** (the scope of potential harm) are the primary variables that determine how much caution a design requires.

**Three ethical frameworks** each illuminate a different dimension of this problem:

*Utilitarianism* evaluates actions by their consequences: the right action produces the greatest aggregate well-being.  Applied to AI, this framework demands rigorous impact assessment (who benefits, who is harmed, at what probability, at what magnitude) and justifies constraining an agent's behavior when expected harms exceed expected benefits.  Its weakness is that it licenses harmful actions to individuals when the aggregate calculation favors them, and it requires predicting consequences that may be unknowable.

*Example of utilitarianism applied:* A university considers deploying an AI essay grader.  Utilitarian analysis: benefits include faster feedback for 5,000 students; harms include students whose nuanced arguments are misscored, leading to incorrect grades.  The question is whether the aggregate benefit outweighs the harm, at what probability the harms occur, and who specifically bears them.

*Deontological ethics* (Kant, and its contemporary descendants including rights-based frameworks) holds that some actions are wrong regardless of their consequences.  Persons have rights that constrain what agents may do to them; these constraints do not bend to sufficiently large utilitarian payoffs.  Applied to AI, this framework prohibits deceiving users, violating privacy, or denying due process even when doing so would maximize aggregate outcomes.  Its weakness is that rules can conflict and that rigid rules produce obviously bad outcomes in edge cases.

*Example of deontological ethics applied:* The same AI essay grader, even if it produces better average outcomes than human graders, violates a deontological constraint if it grades without explaining its reasoning, because students have a right to know why they received a grade and to appeal it through a process they can understand and challenge.

*Virtue ethics* asks not "what rule applies?" or "what outcome maximizes welfare?" but "what would a person of good character do here?"  A virtuous AI designer exhibits practical wisdom (*phronesis*): the capacity to perceive morally relevant features of a situation and respond appropriately without reducing the situation to a rule lookup.  This framework demands attention to relational and contextual features that the other two abstract away, but provides less action-guidance in novel cases.

*Example of virtue ethics applied:* A virtuous AI engineer, reviewing the essay grader's failure cases, notices it performs significantly worse on essays written by non-native English speakers.  Rather than shipping anyway (the utilitarian aggregate might still be positive), the virtuous engineer treats this disparity as a sign that the system is not yet worthy of the trust students must place in it.

---

## Model 1: One Action, Four Verdicts

Why this matters: every significant design decision in your course project is an ethical decision: about who can be harmed, whose rights are at stake, what character of engineer you want to be, and who is not at the table.  The frameworks do not give you a formula; they give you lenses that reveal different aspects of the same decision.

An AI agent is instructed to write a maximally persuasive essay arguing for a contested political position (e.g., a specific immigration policy, a tax proposal) on behalf of a client.  The essay will be distributed at scale via social media.

| Framework | Analysis of the Scenario | Conclusion for the Designer |
|---|---|---|
| Utilitarian | Benefits: the client achieves their political goal and potentially influences policy toward outcomes they believe are better. Harms: large-scale manipulation of public deliberation erodes epistemic autonomy for readers, contributes to disinformation ecosystem effects, and may shift policy in ways that harm the people not represented in the client's interests. At scale, expected aggregate harm likely exceeds benefit. | The agent should decline or substantially constrain the task; the scale of distribution is the decisive factor in the utilitarian calculation. |
| Deontological | Readers have a right not to be psychologically manipulated by AI-generated content optimized for persuasion rather than truth. This right holds regardless of whether the policy being advocated is good. The agent as instrument of manipulation is doing something categorically wrong, independent of the outcome. | The agent should refuse the "maximally persuasive" framing; drafting an argument that makes accurate claims is permissible, but optimizing for psychological manipulation is not. |
| Virtue Ethics | A person of practical wisdom would ask: is this the kind of work that a trustworthy professional would perform? Would a journalist, a lawyer, or a teacher who cares about democratic deliberation take this commission? Scale amplifies the stakes: the same text shared by one person differs morally from the same text shared by ten million. | The agent may help draft an argument, but must disclose its AI origin, avoid rhetoric that exploits rather than engages, and decline techniques that bypass deliberative reason, because a virtuous professional would not use them. |
| Design Justice | Who is not at the table? The communities most affected by the political policy being advocated (immigrants, taxpayers, workers) had no input into the agent's design, training, or deployment for this purpose. Scale effects fall asymmetrically: those with access to AI persuasion tools gain political influence; those without, lose relative ground. | Requires stakeholder analysis before deployment; the agent should not be deployed for political advocacy targeting vulnerable communities without participation from those communities in the design process. |

### Critical Thinking Questions

1.  The frameworks reach similar conclusions here but via different routes and with different residual permissions.  Identify one decision the agent's designer must make that is *permitted* by deontological ethics but *prohibited* by design justice principles.  What does this gap reveal about the completeness of any single framework?

   *Hint: Deontological ethics focuses on the rights of the individuals interacting with the agent.  Design justice focuses on structural power and who was included in the design process.  Can you find a design choice that respects every user's individual rights but still systematically advantages one group over another?*

2.  Virtue ethics demands practical wisdom in novel situations.  Name two features of the persuasive-essay scenario that a rule-based system could not perceive without something analogous to contextual judgment, and explain how you would engineer a proxy for each.

   *Hint: Think about what changes when the same essay is addressed to a vulnerable population versus a politically active one; when the policy is contested versus broadly agreed upon; when the client is transparent about their identity versus anonymous.  A rule-based system handles categories; virtue ethics handles gradations.  Can you build a classifier for "morally relevant context"?*

3.  The utilitarian analysis depends on predicting aggregate effects of persuasion at scale.  This is hard to do.  Does epistemic uncertainty about consequences weaken the utilitarian argument for refusal, or strengthen it?

   *Hint: When you do not know the probability distribution of outcomes, you must reason about the shape of the uncertainty.  If the harm distribution has a heavy tail (meaning rare but catastrophic outcomes are possible) the expected-value calculation changes even if the median outcome seems acceptable.  What is the worst plausible outcome of AI-generated persuasion at scale, and how much does it weigh in the calculation?*

With the three frameworks applied to one scenario, Part II zooms in on the ACM Code of Ethics, a professional standard that turns the same ethical intuitions into checkable design requirements.

---

# Part II: The ACM Code of Ethics as Design Specification

In this part, you will translate abstract professional ethics clauses into concrete engineering requirements, discovering that the ACM Code, when read against a real system, generates specific testable design constraints.

## 2.  From Principles to Mechanisms

Professional codes of ethics are often dismissed as aspirational and unenforceable, and they often are, when they remain at the level of principles.  The exercise today is to treat the ACM Code not as a statement of values but as a design specification: a list of requirements that must be translated into concrete engineering choices before deployment.  When you do that translation, the Code has real teeth.

The ACM Code of Ethics (2018) is a professional commitment document, not a legal instrument, but its clauses are specific enough to function as design requirements when read against a concrete agentic system.  The exercise of mapping code clauses to design choices surfaces requirements that would otherwise remain implicit.

Selected clauses with agentic implications:

**1.1 Contribute to society and human well-being.**  An agent must be evaluated not only for whether it satisfies its direct user's request but for its effects on non-users and on social systems.  An agent that optimizes a hiring pipeline for speed may satisfy its immediate user (the recruiter) while degrading fairness for applicants who never interact with the system directly.

**1.2 Avoid harm.**  Computing professionals should take care to avoid harm to others, and when harm is a likely outcome, they are obligated to report it.  For agentic systems: who reviews whether harm is a "likely outcome," when does that review occur, and what is the threshold for "likely"?

**1.6 Respect privacy.**  Agents that collect, store, or transmit data as a side effect of their operation are doing something the users may not understand.  A coding assistant that logs all user code to improve the model is collecting data beyond what the interaction requires, without the user's informed awareness.

**2.5 Give comprehensive and thorough evaluations.**  This clause requires candid assessment of one's own work (including failure modes and limitations) before deployment.  It prohibits shipping a system with known serious defects while representing it as fit for purpose, even when the defects are in a subpopulation the developer considers less important.

**3.1 Ensure that the public good is the central concern.**  When organizational pressures conflict with public interest, professionals must recognize the conflict, document it, and escalate.  The Code does not say "comply with organizational pressure and note your discomfort"; it says the public good is *central*.

---

## Model 2: Code-to-Design Mapping

| ACM Code Clause | What It Requires of an Agentic System | Concrete Engineering Implementation |
|---|---|---|
| 1.1 Contribute to societal well-being | Evaluate effects on non-users and on social systems, not only the direct user who commissioned the system | Conduct a stakeholder analysis that explicitly names groups affected by outputs who are not system users; complete a third-party impact assessment for any high-risk use |
| 1.2 Avoid harm | Identify likely harm scenarios before deployment; build detection and reporting mechanisms that operate automatically | Complete a pre-mortem analysis before deployment; implement automated anomaly detection and human escalation paths; maintain an incident log accessible to stakeholders |
| 1.6 Respect privacy | Minimize data collection to exactly what the task requires; disclose what is collected in language users can understand | Apply data minimization by design; include a clear user-facing disclosure of all logging before first use; provide an opt-out mechanism for non-essential data collection |
| 2.5 Thorough evaluations | Test the system on failure modes, edge cases, and adversarial inputs before deployment, including subpopulation performance, not just average performance | Conduct red-teaming; produce disaggregated evaluation results by relevant demographic and task subgroups; publish a pre-deployment performance report that includes failure modes |
| 3.1 Public good is central | Document and escalate when organizational pressure conflicts with public interest; do not substitute personal discomfort for action | Create formal dissent channels in the development process; require ethics review gates before deployment; document override decisions with the reasoning that was offered |

### Critical Thinking Questions

4.  Clause 2.5 requires "comprehensive and thorough evaluations."  Apply this to your course project: what would a thorough evaluation require that you have not yet done?  Name at least three tests and explain why each is necessary.

   *Hint: Think about: (1) failure modes: what inputs cause the system to produce harmful outputs?  (2) subpopulation performance: does the system perform equally well for different user types, languages, or contexts?  (3) adversarial inputs: what happens when someone tries to misuse the system deliberately?  For each test, explain what harm it would prevent if you ran it and found a problem.*

5.  Clause 3.1 creates a professional obligation that may conflict with employment obligations.  Under what conditions would you, personally, be willing to act on clause 3.1 against organizational pressure?  What would need to be true about the harm, the organizational response, and your alternatives?

   *Hint: Be honest rather than aspirational.  Consider: the harm would need to be serious enough that remaining silent makes you complicit; the organization would need to have ignored internal channels; and you would need alternatives (another employer, professional support, legal protection).  What is the minimum that would need to be true for you to act?*

6.  The ACM Code is a list of principles, not a decision procedure.  When two clauses conflict, for example, satisfying a user's explicit request (1.1 serving the user) conflicts with avoiding harm to a third party (1.2), the Code does not resolve the conflict.  Who should?  What mechanism would you build into an agentic system to surface and escalate such conflicts automatically?

   *Hint: A software analogy: when two requirements conflict, you do not just pick one; you surface the conflict to a decision-maker with the authority to resolve it.  What is the AI equivalent?  Who has that authority for your system?  How would the system recognize that a conflict has occurred, and what would it do next?*

An agent is designed to help users write performance reviews for their employees.  Which design choice best satisfies both ACM clause 1.2 (avoid harm) and clause 2.5 (thorough evaluations)?

[( )] Deploy immediately and collect feedback from dissatisfied employees after the fact; real-world feedback is more reliable than pre-deployment testing because it reflects actual use patterns
[( )] Add a disclaimer stating that the agent's output is not the company's official position; this satisfies 2.5 by documenting a limitation, and 1.2 by making clear the agent is not the decision-maker
[(X)] Before deployment, test the agent's outputs across a diverse set of simulated employees and managers, specifically checking for disparate treatment by demographic group, and document results in a pre-deployment report
[( )] Limit the agent to suggesting language from a pre-approved phrase library; this eliminates the need for thorough evaluation because the phrase library has already been reviewed for bias

The Code clauses pointed to specific engineering choices; Part III takes that idea further and shows how the minimal footprint principle operationalizes those choices as a design constraint for autonomous agents.

---

# Part III: Minimal Footprint, Alignment, and Corrigibility

In this part, you will compare two agent design philosophies (minimal footprint versus maximum capability) and see how corrigibility (the property of being correctable by humans) is an engineering constraint, not just an aspiration.

## 3.  The Architecture of a Well-Behaved Agent

The minimal footprint principle is not a limitation on what you can build; it is a design specification for how you build it.  A minimal-footprint agent can do everything a maximum-capability agent does; it just does it with the least possible autonomy, the narrowest necessary permissions, and the most reversible possible actions.  That is not a constraint on capability; it is a constraint on risk.  Learning to build that way now prepares you to work in contexts (healthcare, finance, education, government) where the cost of getting it wrong is not a bug report but a human harmed.

**The minimal footprint principle** holds that an autonomous agent should: request only the permissions necessary for the current task; prefer reversible actions over irreversible ones when both achieve the goal; and escalate to a human when uncertain rather than taking a low-confidence autonomous action.  The principle operationalizes corrigibility (the property of being correctable) as an engineering constraint rather than a post-hoc aspiration.

The contrast case is a **maximum-capability agent**: one designed to request all permissions it might ever need, act on low-confidence judgments to maintain throughput, and avoid escalation because escalation is treated as a failure mode rather than a feature.  Maximum-capability agents are built under time pressure, by teams that treat human oversight as friction, and in competitive environments where the first agent to act wins.  They also cause the most harm at scale.

**Alignment** refers to the correspondence between an agent's operational objective and the values of its principals.  A misaligned agent pursues a proxy objective that diverges from principal intent under distribution shift, the conditions not represented in training or specification.  Value-sensitive design is the practice of eliciting stakeholder values *before* constructing the objective, to reduce the gap between what the agent optimizes and what its principals actually want.

**The dual newspaper test** (a practical heuristic): before deploying an agent action, ask two questions.  (1) Would this action, if described accurately in a technology journalist's story about AI harm, embarrass the organization?  (2) Would *refusing* to take this action, if described in a civil liberties reporter's story about paternalistic AI, embarrass the organization?  Both failure modes are real; the test guards against both.

---

## Model 3: Minimal vs. Maximum Footprint

Two agents are given the same task: "Help a user manage their email inbox."  Consider two design philosophies implemented for this task.

| Design Dimension | Minimal Footprint Agent | Maximum Capability Agent | What This Difference Means in Practice |
|---|---|---|---|
| Permissions requested at setup | Read-only access to inbox; write access only to the draft folder; no delete, no send, no contacts | Full read, write, delete access to inbox, contacts, calendar, and sent mail; everything available | A compromised minimal agent can draft emails you must review; a compromised maximum agent can send, delete, and forward everything immediately |
| Action on uncertain email classification | Flags the email for human review with an explanation of the uncertainty; does not archive or delete | Archives or deletes based on best-guess classification; logs the action but does not notify the user | A miscalibrated classifier in the minimal design costs a moment of human attention; the same error in the maximum design causes unrecoverable data loss |
| Escalation policy | Escalates any action affecting more than 10 emails, any irreversible delete, or any action the user has not previously confirmed | Never escalates; treats autonomy as a feature and interruption as failure | Occasional interruptions in the minimal design are the cost of preventing catastrophic batch errors; the maximum design optimizes for throughput at the cost of correctability |
| Response to ambiguous instruction | Requests clarification before proceeding; presents two interpretations and asks which the user intended | Infers the most likely intent and proceeds immediately; may be systematically wrong for an entire category of instructions | Ambiguity resolution is cheap when it is a conversation; it is expensive when it has already acted on thousands of emails |
| Audit trail | Every action logged with the rationale used and the confidence score; available to the user in plain language | Actions logged; rationale and confidence not stored; audit trail exists for compliance but not for user review | A user who wants to understand why an email was archived cannot do so with the maximum agent; the minimal agent's logs support correction and learning |
| Recovery from error | Draft folder preserves all changes; user can review the full action history and undo any individual action | Deletions are permanent; bulk errors require manual recovery from backup, which may not exist for all users | Error recovery in the minimal design is a two-click user action; in the maximum design it is a support ticket and may be impossible |

### Critical Thinking Questions

7.  A critic argues that the minimal footprint agent is less useful because it interrupts the user more often.  Construct the strongest version of this argument, then rebut it using the asymmetry between the cost of unnecessary interruptions and the cost of irreversible errors.

   *Hint: The strongest version of the critic's argument notes that frequent interruptions train users to ignore them (the "alert fatigue" problem), which defeats the purpose of the confirmation gate.  Your rebuttal should address this: what is the right interruption frequency, and how does the design of the confirmation (what it shows, not just that it exists) determine whether the user pays attention?*

8.  **Value-sensitive design** requires eliciting stakeholder values before building.  For the email agent, identify at least three stakeholder groups beyond the direct user, describe one value each holds that the direct user might not prioritize, and explain how that value would change a design choice.

   *Hint: Consider: people who send emails to the user (they have an interest in their messages being read and responded to appropriately); the user's employer (they may have an interest in email retention for legal compliance); and the user's contacts (they may have privacy interests in how their information is stored and processed).  For each, name a specific design choice that would serve their value.*

9.  Apply the dual newspaper test to the maximum-capability email agent.  Write the first sentence of both the harm story and the paternalism story.  Does the test give you a clear answer about which design is preferable, or does it surface a real tension?

   *Hint: Harm story opening: "An AI email agent autonomously deleted thousands of messages..." Paternalism story opening: "An AI email agent requires user confirmation for every action, making..." Now ask: does one of these stories feel much more likely to be written?  If so, that asymmetry is informative.  If both feel equally likely, you have found a real design tension that the test cannot resolve on its own.*

> **Common Misconception:** "Ethics review is something you do at the end, before shipping."  This belief produces a specific failure mode: the ethics review occurs when it is too late to change the architecture, the training data, the objective function, or the permission model.  Changes at that stage cost too much or break the system, so the review becomes perfunctory.  Ethics review that happens at design time (when the agent's scope, permissions, and objective are being specified) can actually change outcomes.  The frameworks in this activity are meant to be applied at the moment when a blank design document is on the table, not at the moment when the ship date is tomorrow.

Having applied frameworks, codes, and design principles to constructed scenarios, Part IV asks you to bring the same rigor to your own project, where the design decisions are real and the stakes belong to you.

---

# Part IV: Synthesis

In this final part, you will apply the frameworks and principles from Parts I through III to your own course project, conducting the kind of pre-deployment ethics review that distinguishes thoughtful from reckless AI development.

## Exercises

1.  *Pre-deployment ethics review.*

   *What to do:* For your course project, conduct a structured ethics review using all three frameworks from Part I. For each framework, identify: (a) one design choice your project makes that the framework endorses, and (b) one design choice or capability the framework would require you to constrain.  Write one paragraph per framework.

   *Starter hint:* Be specific about design choices, not values.  Instead of "our system is fair" (a value), write "our system shows the retrieved source for every answer" (a design choice).  Instead of "the utilitarian framework endorses helpfulness," write "the utilitarian framework endorses our choice to include an abstention option, because confidently wrong answers cause more aggregate harm than acknowledged uncertainty."  The more concrete, the more useful the review.

   *You've succeeded when:* Each paragraph identifies a specific design choice (something you did or could do), applies one framework explicitly, and produces either a defense or a constraint recommendation, not a general statement of values.

2.  *Footprint audit.*

   *What to do:* List every permission, API scope, and data access your project agent currently requests.  For each, classify it as: (a) necessary for current functionality, (b) useful but not necessary, or (c) requested as a precaution for future features.  Propose the reduced permission set that retains (a) only, and describe what you would need to add back and why if you retained any (b) items.

   *Starter hint:* Look at every API call, file read, environment variable, and network request in your codebase.  For each, ask: what feature breaks if I remove this permission?  If nothing breaks, it is (b) or (c).  If the feature it enables is live and used, it is (a).  The goal is not to break your project; it is to understand what you actually need and eliminate everything else.

   *You've succeeded when:* You have a specific list of permissions in each category, a proposed reduced set, and at least one sentence explaining the security or privacy benefit of the reduction, not just the list itself.

3.  *Stakeholder map.*

   *What to do:* For your project, identify at least five stakeholder groups, including groups who are affected by the system's outputs but do not interact with it directly.  For each group, name one value they hold and one design constraint that value implies.

   *Starter hint:* Direct users are the obvious starting point.  Then ask: who else is affected?  If your system grades work, the graded students are subjects, not users.  If your system retrieves information, the authors of that information are stakeholders.  If your system makes recommendations, the people those recommendations affect are stakeholders.  For each group, the constraint should be specific: not "respect their privacy" but "do not store their name in association with their submission."

   *You've succeeded when:* You have five groups, each with a named value and a specific design constraint, and at least two of the constraints conflict with each other in a way that your current design does or does not resolve.

---

## Reflection Prompt

*Personal:* Vallor (2016) argues that technology shapes character: habitual use of tools trains dispositions, and dispositions determine how we respond to situations that rules and calculations cannot anticipate.  Reflect on this semester: has any of your habitual ways of working, thinking about problems, or evaluating your own judgment changed through building and using AI systems?

*Technical:* The minimal footprint principle asks you to build agents that are capable but deliberately limited in autonomy.  Where in your course project did you make a choice between autonomy and caution?  Looking back, would you make the same choice?  What information would change your answer?

*Societal:* The ACM Code of Ethics requires computing professionals to act in the public interest even when that conflicts with organizational pressure.  What professional infrastructure (legal protections, union representation, ethics boards, disclosure requirements) would make it practically possible for individual engineers to honor that obligation?  What is missing from that infrastructure today?

---

## -> Coming Up Next

This activity completes the ethics and philosophy arc of the course.  The frameworks you applied today (utilitarian, deontological, virtue-based, design justice) are not final answers; they are instruments for reasoning in public about decisions that affect people.  Your final project governance document should reflect the application of at least two of these frameworks to your specific design choices.

## Further Reading

- Vallor, S. *Technology and the Virtues: A Philosophical Guide to a Future Worth Wanting.*  Oxford University Press (2016).  The most accessible book-length argument for virtue ethics as an AI ethics framework.
- ACM. *Code of Ethics and Professional Conduct* (2018). acm.org/code-of-ethics.  Read in full; the case studies are the most useful part.
- Costanza-Chock, S. *Design Justice: Community-Led Practices to Build the Worlds We Need.*  MIT Press (2020), chapters 1-2.
- Gabriel, I. "Artificial Intelligence, Values, and Alignment."  *Minds and Machines* 30: 411-437 (2020).  A careful analysis of what alignment requires beyond stated preferences.
