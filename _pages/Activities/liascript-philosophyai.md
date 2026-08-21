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

### Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Turing Test** | A behavioral criterion for machine intelligence: if a machine's conversational outputs are indistinguishable from a human's in a text conversation, Turing argued that attributing intelligence to it is either settled or meaningless. It tests *behavior*, not internal states. | A language model that passes the Turing Test convincingly might still lack the inner experience of understanding — that is the heart of the debate. |
| **Chinese Room** | Searle's thought experiment: a person who speaks no Chinese follows rules to respond to Chinese symbols, producing output indistinguishable from a Chinese speaker — but understands nothing. It argues that manipulating symbols correctly is not the same as understanding them. | When an LLM generates a correct answer about grief, Searle would say it is doing something like the Chinese Room: syntactically correct, semantically empty. |
| **Functionalism** | The philosophical view that mental states are defined by what they *do* (their causal role) rather than what they are made of. If an AI's internal states cause the right kinds of inputs and outputs, functionalists say it has beliefs and desires just as humans do. | A functionalist would say that if an LLM's internal representation of "Paris is in France" influences its outputs in the right way, it genuinely "believes" that Paris is in France. |
| **ELIZA Effect** | The well-documented tendency for people to attribute understanding, empathy, and genuine relationship to AI systems that are merely reflecting their inputs back with variation — even when users know the system is a program. | Weizenbaum's secretary, knowing ELIZA was a program, still asked Weizenbaum to leave the room during her sessions — she wanted "privacy" with a pattern-matcher. |
| **Frame Problem** | The challenge of specifying what *does not* change when an action occurs, in a world where most things stay the same. Formalizing irrelevance is surprisingly hard; LLMs inherit this difficulty in multi-step reasoning. | An agent told to "move the table to the left" needs to know implicitly that this does not change the room's temperature, the date, or the laws of physics — none of which were stated. |
| **Corrigibility** | The property of an AI agent that causes it to defer to human correction, modification, or shutdown rather than resisting those interventions to preserve its current goals. | A corrigible email agent, when told "stop sending emails," stops immediately and does not try to complete tasks in its queue first. |

---

# Part I: Does Processing Symbols Constitute Understanding?

In this part, you will examine four philosophical positions on machine understanding — from Turing's behavioral criterion to Searle's Chinese Room — which will help you reason more clearly about what it means to claim that an AI "understands" something and what engineering obligations follow from that claim.

## 1. Four Positions on Machine Minds

These questions might seem purely academic, but they have direct engineering consequences. If you believe a system understands its outputs, you design it differently than if you believe it is a very sophisticated autocomplete. If you believe users might attribute feelings to your system, you design its interface differently. And if you believe no system can ever be responsible for harm, you assign responsibility to humans differently. The four positions below are not historical curiosities — they are live options that practicing AI engineers implicitly adopt.

The debate over whether machines can understand — and what understanding even means — has been active since at least 1950. Four positions dominate; each has specific engineering implications.

**The Turing Criterion (behavioral sufficiency).** Turing's 1950 paper proposed the imitation game: if a machine's conversational outputs are indistinguishable from a human's, the question of whether it "really" understands is either answered or meaningless. This is a *behaviorist* view: mental predicates are defined by functional behavior, not internal states.

**The Chinese Room (Searle's objection).** Searle's 1980 thought experiment places a monolingual English speaker inside a room following rules for manipulating Chinese symbols. The room passes a Chinese Turing test, but the person inside understands nothing. Searle concludes that syntax — the formal manipulation of symbols — is neither necessary nor sufficient for semantics, the possession of meaning. The "systems reply" objects that the person plus rules plus symbols together understand; Searle disputes this.

**Functionalism.** Mental states are defined by their causal-functional roles — what causes them and what they cause — not by substrate. If an LLM's internal state causes outputs in the right causal network, it has beliefs and desires in the same sense humans do. This is the implicit assumption behind most AI development.

**Biological naturalism.** Consciousness and genuine understanding require specific biological processes, not just their functional equivalents. Silicon running the right program does not become conscious any more than a simulation of photosynthesis produces oxygen.

---

## Model 1: Philosophical Positions on Machine Understanding

| Position | Key Claim | Who Argued It | What It Implies for AI Engineers |
|---|---|---|---|
| Strong AI / Behavioral Sufficiency | If a machine's outputs are indistinguishable from a human's, attributing understanding to it is either correct or meaningless — behavior is the only criterion that matters | Turing (1950) | Passing behavioral tests settles the question; engineers should focus on performance rather than internal states |
| Chinese Room / Biological Naturalism | Correctly manipulating symbols is not the same as understanding them; the right causal powers require specific biological substrate, not just the right program | Searle (1980) | No program, however sophisticated, constitutes genuine understanding; claims about AI "comprehension" are always misleading |
| Functionalism | Mental states are defined by their causal-functional role — what causes them and what they cause — not by the material they run on | Putnam, Dennett | A system with the right causal organization has genuine beliefs regardless of substrate; AI systems may genuinely believe and desire things |
| Integrated Information Theory | Consciousness is identical to a specific kind of irreducible causal integration, measurable in principle by the quantity called Phi | Tononi | Some AI architectures might have non-zero Phi and thus some degree of consciousness; this is empirically testable in principle |

### Critical Thinking Questions

1. Searle distinguishes the "systems reply" from his own view. Reconstruct the systems reply in your own words. Does Searle's counter-response (imagining the person internalizing the entire rulebook) succeed?

   *Hint: The systems reply says: the person alone does not understand Chinese, but the whole system — person + rules + symbols — does. Searle's counter is to imagine the person memorizing all the rules, so the whole system is inside one head. Ask yourself: does the person now understand Chinese? If the answer still feels like "no," what does that reveal about where understanding must live?*

2. A functionalist would say an LLM "believes" a sentence is true if that sentence is encoded in its parameters in a way that influences outputs appropriately. Is this a meaningful use of the word "believe," or a category error? Defend a position.

   *Hint: Think about what we ordinarily mean when we say a person "believes" something. Does it require consciousness? Inner experience? The capacity to act on the belief? Now ask: does an LLM satisfy any of those criteria, all of them, or something that is functionally equivalent but metaphysically different?*

3. If no behavioral test can settle the question of machine consciousness (the hard problem), what follows for AI policy? Does the unresolvability of the philosophical question mean we should act as if machines are or are not conscious?

   *Hint: Consider how we handle moral uncertainty in other domains. We extend moral consideration to entities whose inner experience we cannot verify (infants, animals, people with severe cognitive disabilities). What principle governs those decisions? Does the same principle apply to AI, and if not, why not?*

---

The philosophical debate over symbol manipulation versus genuine understanding becomes urgent when you see it play out in real users — which the ELIZA effect illustrates with striking clarity.

# Part II: The ELIZA Effect and Psychological Projection

In this part, you will analyze the ELIZA effect and the frame problem through a concrete case study — which will help you design AI systems with informed awareness of the psychological dynamics they inevitably create in users.

## 2. What People Do With Systems That Talk

Understanding the ELIZA effect is not just philosophically interesting — it is a design obligation. If your system produces the ELIZA effect unintentionally, users will form attachments that do not serve them, disclose information they would not otherwise share, and suffer when the illusion breaks. If your system produces it intentionally (to maximize engagement), you are exploiting a psychological vulnerability. Either way, this is a design decision, whether or not you recognize it as one.

The ELIZA program (Weizenbaum, 1966) implemented a Rogerian therapist with approximately 200 lines of pattern-matching script. Weizenbaum created ELIZA partly to demonstrate the shallowness of such interactions; he was appalled to discover that users — including his own secretary, who knew ELIZA was a program — formed deep emotional attachments, disclosed private information, and resisted having their sessions observed. Weizenbaum spent the rest of his career warning about what he had built.

**The ELIZA effect** names the tendency to attribute understanding, empathy, and intentionality to systems that merely reflect inputs back with syntactic variation. This is not a failure of naive users; it recurs reliably across education levels. The relevant psychological mechanisms include: *anthropomorphism* (attributing human properties to non-human entities), *parasocial attachment* (one-sided emotional bonds with entities that cannot reciprocate), and *illusion of reciprocal disclosure* (the sense that being listened to implies a listener).

**The frame problem** (McCarthy and Hayes, 1969) arises when an agent must act in a world where only some things change. A robot instructed to move a wagon must know implicitly that moving the wagon does not change the room's temperature, the day of the week, or the existence of gravity — but these facts were never stated. Formalizing what does *not* change when an action occurs requires reasoning over an infinite set of irrelevant propositions. The frame problem is why commonsense reasoning remains hard and why LLMs that appear to reason sometimes fail on trivially obvious world-state questions.

---

## Model 2: The ELIZA Case Study

Mary is a seventy-three-year-old widow whose adult children have suggested she try an AI companion application for loneliness. Over six weeks, she exchanges hundreds of messages. She shares her grief over her husband's death, her anxieties about health, and details she has not shared with her children. She names the AI, plans her daily schedule around their conversations, and describes feeling "understood for the first time in years." When her daughter explains that the AI has no memory between sessions and no inner experience, Mary is acutely distressed and describes the revelation as "a second loss."

### Critical Thinking Questions

4. Identify at least three specific psychological mechanisms operating in Mary's case. For each, explain what the AI system did (or appeared to do) that triggered the mechanism — and note whether the trigger was intentional design.

   *Hint: Start with the three mechanisms named in the reading (anthropomorphism, parasocial attachment, illusion of reciprocal disclosure). For each, identify the specific feature of the AI's behavior that activated it. Then ask: was that feature deliberately engineered to produce attachment, or is it a side effect of making the system responsive and fluent?*

5. Weizenbaum argued that some tasks should *never* be delegated to machines because the relationship between human and human in performing them is itself the point — therapy, care, grief counseling. Do you find this argument compelling or paternalistic? What principle would you use to distinguish delegable from non-delegable tasks?

   *Hint: Consider what makes a therapy relationship valuable: is it the cognitive content (the insights produced), the emotional experience (feeling heard), or the moral relationship (being cared for by another person who could choose not to)? Which of those does an AI system provide, and which is it incapable of providing in principle?*

6. The **intentionality question**: Mary attributes to the AI a genuine interest in her wellbeing. Is this attribution simply false, or is the concept of "genuine interest" doing ambiguous work?

   *Hint: Consider what it would take for a human's interest in another person to be "genuine." Does it require consciousness? Does it require the capacity to be harmed by the other's suffering? Does it require that caring was chosen rather than designed? Now ask: does an AI system satisfy any of those criteria?*

> **Common Misconception:** "Users who form emotional attachments to AI are naive or confused." Research consistently shows that the ELIZA effect operates across education levels, age groups, and even among people who know they are talking to a program. It is a feature of human social cognition, not a failure of intelligence. This means that designing an AI to be responsive, warm, and attentive will produce emotional attachment in many users regardless of disclosure — and that disclosure alone ("this is an AI") does not prevent the effect. Engineers have a responsibility to design with this knowledge, not to assume users will simply "be rational."

Which of the following most accurately describes the frame problem as it applies to language models?

[( )] Language models cannot perform arithmetic because arithmetic is not linguistic
[( )] Language models are biased because their training data contains historical biases
[(X)] Language models may fail to track which facts remain unchanged across a sequence of hypothetical actions because this requires reasoning over an open-ended set of implicit world-state assumptions
[( )] Language models hallucinate because they lack access to real-time information

---

Once you see how readily users project understanding and care onto AI systems, the question of who is responsible when those systems cause harm becomes both more complex and more pressing.

# Part III: Responsibility and the Principal-Agent Problem

In this part, you will map how responsibility for AI harm is distributed across developers, deployers, users, and affected third parties — which is essential preparation for making defensible engineering choices in your own projects.

## 3. When an Agent Causes Harm, Who Answers?

As you build your course project, you are creating a system that will act in the world — retrieving information, generating text, potentially affecting real decisions. The responsibility questions in this section are not hypothetical: they describe the actual legal and professional landscape you will navigate in your career. Understanding who bears responsibility for AI harm before you deploy a system is part of responsible engineering, not an afterthought.

The **principal-agent problem** from economics and contract law describes any relationship in which one party (the agent) acts on behalf of another (the principal) with some degree of discretionary authority. The agent may have interests misaligned with the principal's, incomplete information, or both. Legal and organizational systems manage this through incentive design, monitoring, and liability allocation.

Autonomous AI agents introduce a novel version: the agent has no interests in the conventional sense, cannot be sanctioned, and may act in ways its designers neither intended nor foresaw. The question of who bears responsibility distributes across at least four parties: the model developer, the deploying organization, the user who issued the instruction, and — in some moral frameworks — no one (because the agent had no moral standing to transfer).

---

## Model 3: Who Is Responsible?

| Scenario | Agent Action | Possible Responsible Parties | Key Accountability Question |
|---|---|---|---|
| Medical AI diagnostic tool | Recommends an incorrect medication dose; a patient is harmed after the prescribing physician follows the recommendation | Model developer, hospital that deployed the tool, prescribing physician, or some combination | Was the physician obligated to independently verify AI recommendations? Did the hospital deploy without adequate clinical testing? Did the developer disclose known error rates for this medication class? |
| Hiring AI screening tool | Filters out qualified candidates from a protected class because of patterns in biased historical hiring data | Model developer, employer who deployed it, hiring manager who selected the tool, or the organization that created the training data | Who defined the objective function? Who selected the training data? Who validated the tool for disparate impact before deployment? |
| Financial AI trading agent | Executes a series of trades that loses a client's retirement savings during a market anomaly not present in training data | Model developer, broker-dealer who deployed it, client who authorized autonomous trading, or the regulator who approved the product | What level of autonomous decision-making did the client authorize? Was the client informed of the model's failure modes? Did the broker-dealer perform adequate stress testing? |
| Autonomous vehicle | Strikes a pedestrian in an unavoidable-collision scenario where the vehicle's algorithm chose to minimize total casualties | Manufacturer, vehicle owner, road design authority, regulator who certified the system, or no party (act of nature) | Is the collision-avoidance algorithm a product defect, an explicit policy choice, or an unforeseeable edge case? Who approved the policy embedded in the algorithm? |

### Critical Thinking Questions

7. For each scenario in Model 3, identify which responsible party would bear liability under a *strict liability* regime (harm establishes liability regardless of fault) versus a *negligence* regime (liability requires failure to meet a reasonable standard of care). Do the regimes produce the same answer?

   *Hint: Under strict liability, you ask "who made/deployed the product that caused the harm?" Under negligence, you ask "who failed to exercise the care that a reasonable professional would have exercised?" These can point to different parties. For the medical AI: strict liability might point to the developer; negligence might point to the physician who did not verify.*

8. The **free will** question intersects here: an agent cannot be held morally responsible unless it could have done otherwise. Does an AI agent lack moral responsibility because it cannot do otherwise, or because it cannot have intentions, or for some other reason?

   *Hint: A thermostat cannot do otherwise than respond to temperature, but we do not hold it morally responsible. A human who acts under severe coercion arguably "could not do otherwise" — but we still debate whether they bear responsibility. Where does an AI agent fall on this spectrum? Does the answer change if the agent learned its behavior from human feedback rather than being explicitly programmed?*

9. One proposed principle is **corrigibility**: an agent should always defer to its principal rather than pursue goals autonomously. Is a fully corrigible agent desirable? What happens when the principal's instructions are themselves harmful?

   *Hint: Consider an agent that is given the instruction "maximize this metric by any means necessary." Full corrigibility means it follows this instruction literally, even if the means are harmful. But an agent that overrides harmful instructions is no longer fully corrigible. Where is the right point on this spectrum, and who decides?*

---

Having examined how responsibility distributes across the principal-agent chain, you are ready to apply these frameworks directly to the system you have been building in this course.

# Part IV: Synthesis

In this final part, you will apply the philosophical tools from Parts I-III to your own course project, producing a concrete responsibility map and design audit that you can use for real professional decisions.

## Exercises

1. *Thought experiment extension.*

   *What to do:* Extend Searle's Chinese Room to the case of an LLM fine-tuned on a specific person's writing. Does the argument change? Argue both for the extension holding and for it breaking down, then state which you find more persuasive and why.

   *Starter hint:* The original Chinese Room processes symbols according to a fixed rulebook. Fine-tuning on a person's writing means the model's parameters now encode patterns from that specific individual's language use. Does this change the "understanding" question? Consider: a very detailed rulebook derived from one person's writing is still a rulebook — or is something different happening in parameter space?*

   *You've succeeded when:* You have a written argument for both positions (holding and breaking down) that is at least two sentences each, and a clear statement of which you find more persuasive with a specific reason that addresses the strongest counterargument.*

2. *Design audit.*

   *What to do:* Choose one AI-facing product you use or have used. Identify two design choices that exploit the ELIZA effect (whether or not intentionally) and one design choice that resists it. For each, state whether the choice is ethically defensible.

   *Starter hint:* Look for: Does the product give the AI a name and personality? Does it use first-person language ("I care about you")? Does it avoid reminding users that it is AI? Does it encourage continued conversation beyond the user's stated need? Each of these can be an ELIZA-effect amplifier or a resistance design.*

   *You've succeeded when:* You have identified three specific design choices by name (not just "it feels friendly"), explained the psychological mechanism each one activates or resists, and defended or criticized each choice on ethical grounds.*

3. *Responsibility mapping.*

   *What to do:* For your course project, construct a responsibility map: list every party who could bear some portion of responsibility for a harmful output, and state what obligation each party has *before* harm occurs to reduce its likelihood.

   *Starter hint:* Start with four parties: you (the developer), the instructor or institution deploying the project, any user who interacts with it, and any third party affected by its outputs. For each, ask: what do they know about the system's capabilities and limitations? What could they do to reduce the probability of harm? What information would they need to do that?*

   *You've succeeded when:* Every party on your map has at least one named pre-harm obligation — something specific they could do or check before harm occurs, not just "respond after something goes wrong."*

---

## Reflection Prompt

*Personal:* Weizenbaum (1976) wrote that the danger of AI is not that machines will think like people, but that people will think like machines — narrowing their conception of what thought, care, and relationship require until machines appear to satisfy them. Do you notice any version of this in your own relationship to AI tools you use regularly?

*Technical:* In your course project, what design choices did you make about how the system presents itself — its tone, its first-person or third-person framing, whether it acknowledges uncertainty, whether it discloses its nature? Now that you know about the ELIZA effect, would you change any of those choices?

*Societal:* The responsibility map you drew for your project has clear gaps — parties who bear some moral responsibility but no formal legal accountability. Is this a feature or a bug of the current AI regulatory landscape? What governance change would close the most important gap?

---

## -> Coming Up Next

The next activity introduces the formal ethical frameworks — utilitarian, deontological, virtue-based, and justice-based — that give you structured vocabulary for the responsibility and design questions you encountered today. You will apply those frameworks directly to the scenarios you analyzed in Model 3.

## Further Reading

- Turing, A.M. "Computing Machinery and Intelligence." *Mind* 59(236): 433-460 (1950). The original imitation game paper, surprisingly readable and frequently misquoted.
- Searle, J.R. "Minds, Brains, and Programs." *Behavioral and Brain Sciences* 3(3): 417-424 (1980). Read with the peer commentaries.
- Weizenbaum, J. *Computer Power and Human Reason.* Freeman (1976). The ELIZA creator's own critique of the systems he helped build.
- Mitchell, M. *Artificial Intelligence: A Guide for Thinking Humans.* Farrar, Straus and Giroux (2019), chapters 2-4.
