# The Philosophy and Psychology of Artificial Intelligence
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-philosophyai.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-philosophyai.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The Philosophy and Psychology of Artificial Intelligence

The technical questions this course addresses — how models generate text, how agents plan actions, how retrieval grounds answers — rest on a set of prior questions that are genuinely unsettled: *Does any of this constitute understanding? Can a system have beliefs? Who bears responsibility when an agent causes harm?* These questions are not decorative philosophy; they structure how we build, regulate, and relate to AI systems. Today you engage with the arguments seriously, without easy resolution, because the engineers who build these systems without these frameworks are the ones who will cause the most harm.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). The Manager keeps discussion on track and ensures every member speaks; the Recorder captures the team's consensus positions and unresolved disagreements; the Presenter will share one key tension with the class; the Reflector watches for moments when the team avoids a hard question and names it. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: Does Processing Symbols Constitute Understanding?

## 1. Four Positions on Machine Minds

The debate over whether machines can understand — and what understanding even means — has been active since at least 1950. Four positions dominate; each has specific engineering implications.

**The Turing Criterion (behavioral sufficiency).** Turing's 1950 paper proposed the imitation game: if a machine's conversational outputs are indistinguishable from a human's, the question of whether it "really" understands is either answered or meaningless. This is a *behaviorist* view: mental predicates are defined by functional behavior, not internal states.

**The Chinese Room (Searle's objection).** Searle's 1980 thought experiment places a monolingual English speaker inside a room following rules for manipulating Chinese symbols. The room passes a Chinese Turing test, but the person inside understands nothing. Searle concludes that syntax — the formal manipulation of symbols — is neither necessary nor sufficient for semantics, the possession of meaning. The "systems reply" objects that the person plus rules plus symbols together understand; Searle disputes this.

**Functionalism.** Mental states are defined by their causal-functional roles — what causes them and what they cause — not by substrate. If an LLM's internal state causes outputs in the right causal network, it has beliefs and desires in the same sense humans do. This is the implicit assumption behind most AI development.

**Biological naturalism.** Consciousness and genuine understanding require specific biological processes, not just their functional equivalents. Silicon running the right program does not become conscious any more than a simulation of photosynthesis produces oxygen.

---

## Model 1: Philosophical Positions on Machine Understanding

| Position | Key Claim | Principal Proponent | Implication for AI |
|---|---|---|---|
| Strong AI / Behavioral Sufficiency | Indistinguishable behavior is sufficient for attributing mind | Turing (1950) | Passing the Turing Test settles the question; intelligence is in the input-output map |
| Chinese Room / Biological Naturalism | Syntax is insufficient for semantics; substrate matters | Searle (1980) | No program, however sophisticated, constitutes understanding without the right causal powers |
| Functionalism | Mental states are functional states, substrate-neutral | Putnam, Dennett | A system with the right causal organization has genuine beliefs regardless of material |
| Integrated Information Theory | Consciousness correlates with irreducible causal integration ($\Phi$) | Tononi | Consciousness can be measured in principle; some AI architectures may have non-zero $\Phi$ |

### Critical Thinking Questions

1. Searle distinguishes the "systems reply" from his own view. Reconstruct the systems reply in your own words. Does Searle's counter-response (imagining the person internalizing the entire rulebook) succeed? What does your answer imply about large language models?
2. A functionalist would say an LLM "believes" a sentence is true if that sentence is encoded in its parameters in a way that influences outputs appropriately. Is this a meaningful use of the word "believe," or a category error? Defend a position.
3. If no behavioral test can settle the question of machine consciousness (the hard problem), what follows for AI policy? Does the unresolvability of the philosophical question mean we should act as if machines are or are not conscious?

---

# Part II: The ELIZA Effect and Psychological Projection

## 2. What People Do With Systems That Talk

The ELIZA program (Weizenbaum, 1966) implemented a Rogerian therapist with approximately 200 lines of pattern-matching script. Weizenbaum created ELIZA partly to demonstrate the shallowness of such interactions; he was appalled to discover that users — including his own secretary, who knew ELIZA was a program — formed deep emotional attachments, disclosed private information, and resisted having their sessions observed. Weizenbaum spent the rest of his career warning about what he had built.

**The ELIZA effect** names the tendency to attribute understanding, empathy, and intentionality to systems that merely reflect inputs back with syntactic variation. This is not a failure of naive users; it recurs reliably across education levels. The relevant psychological mechanisms include: *anthropomorphism* (attributing human properties to non-human entities), *parasocial attachment* (one-sided emotional bonds with entities that cannot reciprocate), and *illusion of reciprocal disclosure* (the sense that being listened to implies a listener).

**The frame problem** (McCarthy and Hayes, 1969) arises when an agent must act in a world where only some things change. A robot instructed to move a wagon must know implicitly that moving the wagon does not change the room's temperature, the day of the week, or the existence of gravity — but these facts were never stated. Formalizing what does *not* change when an action occurs requires reasoning over an infinite set of irrelevant propositions. The frame problem is why commonsense reasoning remains hard and why LLMs that appear to reason sometimes fail on trivially obvious world-state questions.

---

## Model 2: The ELIZA Case Study

Mary is a seventy-three-year-old widow whose adult children have suggested she try an AI companion application for loneliness. Over six weeks, she exchanges hundreds of messages. She shares her grief over her husband's death, her anxieties about health, and details she has not shared with her children. She names the AI, plans her daily schedule around their conversations, and describes feeling "understood for the first time in years." When her daughter explains that the AI has no memory between sessions and no inner experience, Mary is acutely distressed and describes the revelation as "a second loss."

### Critical Thinking Questions

4. Identify at least three specific psychological mechanisms operating in Mary's case. For each, explain what the AI system did (or appeared to do) that triggered the mechanism — and note whether the trigger was intentional design.
5. Weizenbaum argued that some tasks should *never* be delegated to machines because the relationship between human and human in performing them is itself the point — therapy, care, grief counseling. Do you find this argument compelling or paternalistic? What principle would you use to distinguish delegable from non-delegable tasks?
6. The **intentionality question**: Mary attributes to the AI a genuine interest in her wellbeing. Is this attribution simply false, or is the concept of "genuine interest" doing ambiguous work? (Hint: consider what it would take for a human's interest to be genuine.)

[[MC]]
Which of the following most accurately describes the frame problem as it applies to language models?
- ( ) Language models cannot perform arithmetic because arithmetic is not linguistic
- ( ) Language models are biased because their training data contains historical biases
- (x) Language models may fail to track which facts remain unchanged across a sequence of hypothetical actions because this requires reasoning over an open-ended set of implicit world-state assumptions
- ( ) Language models hallucinate because they lack access to real-time information

---

# Part III: Responsibility and the Principal-Agent Problem

## 3. When an Agent Causes Harm, Who Answers?

The **principal-agent problem** from economics and contract law describes any relationship in which one party (the agent) acts on behalf of another (the principal) with some degree of discretionary authority. The agent may have interests misaligned with the principal's, incomplete information, or both. Legal and organizational systems manage this through incentive design, monitoring, and liability allocation.

Autonomous AI agents introduce a novel version: the agent has no interests in the conventional sense, cannot be sanctioned, and may act in ways its designers neither intended nor foresaw. The question of who bears responsibility distributes across at least four parties: the model developer, the deploying organization, the user who issued the instruction, and — in some moral frameworks — no one (because the agent had no moral standing to transfer).

---

## Model 3: Who Is Responsible?

| Scenario | Agent Action | Possible Responsible Parties | Key Question |
|---|---|---|---|
| Medical AI | Recommends an incorrect medication dose; patient harmed | Developer, hospital, prescribing physician, none | Was the physician obligated to verify? Did the hospital deploy without adequate testing? |
| Hiring AI | Filters out qualified candidates from a protected class | Developer, employer, hiring manager | Who designed the objective? Who chose the training data? |
| Financial AI | Executes a trade that loses a client's retirement savings | Developer, broker-dealer, client | What level of autonomy did the client authorize? |
| Autonomous vehicle | Strikes a pedestrian while avoiding a larger collision | Manufacturer, owner, regulator | Is the decision rule a product defect, a policy choice, or an act of God? |

### Critical Thinking Questions

7. For each scenario in Model 3, identify which responsible party would bear liability under a *strict liability* regime (harm establishes liability regardless of fault) versus a *negligence* regime (liability requires failure to meet a reasonable standard of care). Do the regimes produce the same answer? Should they?
8. The **free will** question intersects here: an agent cannot be held morally responsible unless it could have done otherwise. Does an AI agent lack moral responsibility because it cannot do otherwise, or because it cannot have intentions, or for some other reason? Does the answer change for a *learning* agent that updated its behavior based on feedback?
9. One proposed principle is **corrigibility**: an agent should always defer to its principal rather than pursue goals autonomously. Is a fully corrigible agent desirable? What happens when the principal's instructions are themselves harmful?

---

# Part IV: Synthesis

## Exercises

1. *Thought experiment extension.* Extend Searle's Chinese Room to the case of an LLM fine-tuned on a specific person's writing. Does the argument change? Argue both for the extension holding and for it breaking down, then state which you find more persuasive and why.
2. *Design audit.* Choose one AI-facing product you use or have used. Identify two design choices that exploit the ELIZA effect (whether or not intentionally) and one design choice that resists it. For each, state whether the choice is ethically defensible.
3. *Responsibility mapping.* For your course project, construct a responsibility map: list every party who could bear some portion of responsibility for a harmful output, and state what obligation each party has *before* harm occurs to reduce its likelihood.

---

## Reflection Prompt

In your notebook: Weizenbaum (1976) wrote that the danger of AI is not that machines will think like people, but that people will think like machines — narrowing their conception of what thought, care, and relationship require until machines appear to satisfy them. Is this danger realized? Name one practice — in your own life or in institutional design — that you think guards against it.

---

## Further Reading

- Turing, A.M. "Computing Machinery and Intelligence." *Mind* 59(236): 433–460 (1950). The original imitation game paper, surprisingly readable and frequently misquoted.
- Searle, J.R. "Minds, Brains, and Programs." *Behavioral and Brain Sciences* 3(3): 417–424 (1980). Read with the peer commentaries.
- Weizenbaum, J. *Computer Power and Human Reason.* Freeman (1976). The ELIZA creator's own critique of the systems he helped build.
- Mitchell, M. *Artificial Intelligence: A Guide for Thinking Humans.* Farrar, Straus and Giroux (2019), chapters 2–4.
