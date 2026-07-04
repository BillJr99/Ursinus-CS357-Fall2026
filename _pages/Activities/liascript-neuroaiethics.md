# Neuro-AI Ethics: Brain-Inspired AI, Cognitive Science, and the Study of Mind
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-neuroaiethics.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-neuroaiethics.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Neuro-AI Ethics: Brain-Inspired AI, Cognitive Science, and the Study of Mind

The history of AI is a history of borrowing metaphors from cognitive science, then having to fight those metaphors when they mislead. The perceptron was modeled on the neuron; the transformer's attention mechanism borrows the vocabulary of attentional psychology; LLMs are described as "thinking," "understanding," and "hallucinating." These are not neutral word choices — they shape what researchers look for, what regulators regulate, and what the public fears or trusts. Today you will examine the genuine connections between AI and cognitive science, the points where the analogies break down, and what it means to take the study of mind seriously when designing and deploying AI systems. The arc: **biological inspiration $\rightarrow$ the problem with metaphors $\rightarrow$ dual-process theory $\rightarrow$ memory structures $\rightarrow$ embodied cognition $\rightarrow$ cognitive biases in AI**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today's material is deliberately speculative in places — the Reflector's job is to track every claim the team makes that would require empirical evidence to settle. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|---|---|---|
| **Dual-process theory** | A framework from cognitive psychology distinguishing two modes of thinking: System 1 (fast, automatic, intuitive) and System 2 (slow, deliberate, effortful). Introduced by Daniel Kahneman. | A standard LLM doing a single forward pass behaves like System 1 — fast, high-confidence, and potentially wrong in novel situations. |
| **Chain-of-thought (CoT) prompting** | A technique that asks the model to generate intermediate reasoning steps (like showing its work) before giving a final answer, simulating slower, more deliberate thinking. | Asking "think step by step" before a math problem improves accuracy on multi-step arithmetic. |
| **Symbol grounding problem** | The challenge that AI systems trained only on text symbols may not have the same kind of understanding as beings who have physically experienced the things those symbols refer to. | An LLM that has read thousands of descriptions of fire may use the word "hot" correctly without ever having experienced heat. |
| **Embodied cognition** | The idea that thinking is not just something a brain does in isolation — it is shaped by having a body that interacts with the physical world. | Our concept of "balance" is grounded in the experience of balancing our own bodies, which is something a text-only AI has never done. |
| **Cognitive bias** | A systematic pattern of deviation from rational judgment, originally identified in human psychology, now also observed in LLMs trained on human-generated text. | Anchoring bias: an LLM adjusts insufficiently away from an initial (possibly wrong) number mentioned early in a prompt. |
| **Attention mechanism** | In transformer AI models, a mathematical operation that computes which parts of the input are most relevant to each output token. The name borrows from cognitive psychology, but the mechanism is a dot-product similarity score over tokens, not a biological spotlight. | A transformer generating the word "Paris" in "The capital of France is ___" gives high attention weight to the word "France." |

---

# Part I: Biological Inspiration and Its Limits

In this part, you will trace how major AI architectural ideas borrowed their conceptual vocabulary from cognitive science and neuroscience — which will help you recognize where those borrowed metaphors mislead engineers, researchers, and the public about what AI systems actually do.

## Model 1: Where AI Borrowed from the Brain — and Where the Analogy Breaks

AI systems were not built from scratch. Almost every major architectural idea in modern AI has a cognitive science story behind it. But borrowing a metaphor from the brain is not the same as copying the brain — and the places where the analogy fails are exactly where AI systems produce unexpected failures.

The McCulloch-Pitts neuron (1943) was the original metaphor: a biological neuron either fires or does not, so they modeled computation as a weighted threshold function. Hebb's rule (1949) — "neurons that fire together wire together" — became the conceptual ancestor of backpropagation: connections that contribute to correct outcomes are strengthened. Convolutional neural networks were directly inspired by Hubel and Wiesel's discovery (1959–1968) that visual cortex neurons respond to edges at specific orientations and locations before combining into higher-order features.

The transformer's **attention mechanism** borrows the vocabulary of the *attentional spotlight*: the idea from cognitive psychology that perception is not passive but directed — the mind selects and amplifies certain stimuli. In transformers, attention weights determine which parts of the input most influence each output token. The analogy is suggestive but inexact: biological attention is selective suppression and amplification implemented in prefrontal-parietal circuits, not a dot-product similarity score over a flat token sequence.

**Why metaphors matter.** George Lakoff and Mark Johnson argue in *Philosophy in the Flesh* that conceptual metaphors are not decorative — they are the cognitive substrate of abstract thought. When we call an LLM a "brain," we import expectations: that it has goals, that it learns continuously, that its errors are like forgetting. All three expectations are wrong in important ways, and each has caused real misjudgments in AI policy and public discourse.

| AI Concept | Brain Metaphor Used | What the Metaphor Implies (Incorrectly) | What Is Actually True |
|---|---|---|---|
| **LLM generating text** | "The model thinks" or "the model reasons" | That there is an ongoing deliberative process, a goal, and self-monitoring of whether the reasoning is going well. | A single forward pass over learned statistical patterns — fast, parallel, with no backtracking or self-verification. |
| **Training on new data** | "The model learns" | That the model continuously updates from new experience, like a person learning from a conversation. | Standard deployed LLMs have fixed weights; they do not update during inference; every conversation starts from the same static checkpoint. |
| **Incorrect output** | "The model hallucinated" or "the model forgot" | That forgetting and hallucination in AI work the same way as in human memory — lapses, gaps, reconstruction failures. | LLM "hallucination" is a confident generation from learned patterns that happens to be false — structurally different from human memory failure. |
| **Transformer attention** | "The model pays attention to" | That attention in AI and attention in humans involve the same selective amplification and suppression processes. | Transformer attention is a mathematical similarity score between token embeddings — not a cognitive selection process with limits, fatigue, or bias the way human attention is. |

### Critical Thinking Questions

1. When a reporter writes "the AI understood the question and gave a helpful answer," they are using cognitive vocabulary. List three specific inferences a non-expert reader might draw from this phrasing that are technically incorrect — and explain what is actually happening in each case.

   *Hint:* What does "understood" imply about the process? What does "helpful" imply about the AI's intentions? What does "gave" imply about agency?

2. The transformer's "attention" mechanism is named after the cognitive psychology concept of attentional selection. Name one way the engineering concept is genuinely analogous to its cognitive namesake, and one way it is fundamentally different. Does the name help or mislead?

   *Hint:* Both mechanisms determine what is "relevant" to what. But cognitive attention is limited and fatigues; transformer attention is computed simultaneously across all positions in a single mathematical operation. What consequences does that difference have?

3. The claim that "neurons that fire together wire together" (Hebb's rule) inspired backpropagation. Is this an accurate description of how backpropagation works, or is it a post-hoc metaphor? What would someone need to check to answer this question?

   *Hint:* Hebb's rule updates connections based on local co-activation. Backpropagation uses a global error signal propagated backward through the network. How are these similar? How are they different?

---

Having mapped where AI borrowed from the brain — and where those analogies break — you are ready to examine which cognitive modes AI systems simulate and what they fundamentally lack.

# Part II: Dual-Process Theory and Memory

In this part, you will apply cognitive psychology's dual-process theory to AI inference — comparing fast, automatic LLM outputs to System 1 thinking — and examine how human memory types map imperfectly onto AI equivalents, so you can reason more precisely about what AI agents can and cannot remember.

## Model 2: Dual-Process Theory Applied to AI Systems

Think of your own mind: you can read the word "cat" instantly without effort (System 1), but solving a multi-step logic puzzle requires focused, step-by-step work where you might catch yourself making a mistake and back up (System 2). Daniel Kahneman's dual-process theory distinguishes these two cognitive modes precisely. The question for AI: which mode do LLMs operate in — and can we build the other?

**System 1** is fast, automatic, associative, high-confidence, and largely unconscious. **System 2** is slow, deliberate, effortful, and self-monitoring — it asks "wait, is that right?" and changes course. System 1 is indispensable for most of cognition; its failure modes include overconfidence, susceptibility to priming, and failure in novel situations that don't match prior patterns.

A standard LLM doing a single forward pass is a **System 1 machine**: it produces a high-confidence output fast, without verification or backtracking, based entirely on learned patterns. **Chain-of-thought prompting** attempts to simulate System 2 by requiring intermediate reasoning steps before a final answer. It works partially — CoT improves accuracy on multi-step arithmetic and logic — but the "reasoning" is still generated in the same forward-pass manner, without genuine backtracking or error-checking.

| System | Type | Speed | Confidence Level | Characteristic Error Pattern | Does Chain-of-Thought Help? |
|---|---|---|---|---|---|
| **Standard LLM (single forward pass)** | System 1 machine | Very fast — milliseconds per response. | High, often uncalibrated — the model states wrong answers as confidently as right ones. | Confident errors on novel patterns; fails gracefully on familiar patterns, fails hard on unfamiliar ones. | N/A — this is the baseline with no CoT. |
| **LLM with chain-of-thought** | System 1 with simulated System 2 output | Slower — more tokens generated before the answer. | Somewhat better calibrated — the reasoning steps sometimes reveal inconsistencies before the final answer. | Fewer arithmetic and logic errors; still fails on genuinely novel problems outside the training distribution. | Yes, moderately — especially for problems with clear intermediate steps. |
| **LLM with self-correction loop** | Closer to System 2 structure | Much slower — requires multiple LLM calls (generate, critique, revise). | Improved in tested domains where the model has been shown to self-correct effectively. | Can catch surface-level errors; blind to its own deep biases because the same model does both generation and critique. | Depends heavily on the quality of the critic prompt and model. |
| **Human fast thinking (System 1)** | System 1 | Very fast — automatic, effortless. | High in familiar situations; poor calibration in novel ones. | Optical illusions, heuristic shortcuts (availability, representativeness), priming effects. | N/A — not an AI system. |
| **Human deliberate thinking (System 2)** | System 2 | Slow — requires sustained effort and working memory. | Appropriately uncertain — good System 2 thinking includes explicit acknowledgment of what is not known. | Logic errors when fatigued; can catch and correct System 1 mistakes when given enough time. | N/A — not an AI system. |

[[MC]]
The dual-process theory suggests LLMs are primarily System 1 machines. The most important implication for deploying LLMs as agents is:
- (x) LLMs will tend to give fast, confident, but potentially wrong answers, especially in novel situations — which is why deliberate reasoning structures (CoT, multi-agent critique) and human oversight are essential
- ( ) LLMs should only be used for tasks that require fast responses and not for slow analytical tasks
- ( ) System 1 thinking is less useful than System 2 and should be avoided in all agent designs
- ( ) LLMs should always use chain-of-thought regardless of task type or cost

---

> ⚠️ **Common Misconception:** "Chain-of-thought makes LLMs reason like humans reasoning carefully."
>
> CoT prompting produces *tokens that look like reasoning steps*, but those steps are generated by the same forward-pass process as any other tokens — there is no genuine backtracking, no re-examination of earlier steps, and no recovery from an error made in step 2 when the model reaches step 6. The model generates step 3 conditioned on step 2, even if step 2 was wrong. Human System 2 thinking can notice "wait, I made an error back there" and revise; a single LLM call cannot. This is why multi-agent critique loops (where a separate model evaluates the output) are architecturally closer to System 2 than CoT alone.

---

## Model 3: Human Memory Types vs. AI Equivalents

Cognitive psychology distinguishes multiple memory systems that serve very different functions. The table below maps these onto AI equivalents — but mapping is not identity, and the "Limitations of the Analogy" column is as important as the equivalents themselves.

| Human Memory Type | What It Stores | Human Example | AI Equivalent | Limitations of the Analogy |
|---|---|---|---|---|
| **Episodic memory** | Personal autobiographical events with context (when, where, what happened). | "I remember my first day of college — the weather, the feeling, the people I met." | Conversation history in the context window; logged session traces. | The context window is finite and discarded at session end; the AI has no autobiographical continuity across sessions — each session starts blank. |
| **Semantic memory** | General world knowledge and facts, without memory of when or how they were learned. | "Paris is the capital of France" — known without remembering learning it. | Weights learned during training; facts encoded statistically across billions of parameters. | Weights encode statistical patterns, not verified facts; knowledge has a training cutoff date; the model cannot distinguish "I learned this" from "I hallucinated this." |
| **Procedural memory** | Knowing *how* to do something — skills and habits stored as automatic motor sequences. | "How to ride a bike" — you can't fully explain it, but your body knows. | Fine-tuned task behaviors; agent tool-use patterns learned during training. | AI procedural knowledge is entirely linguistic, not sensorimotor; "knowing how" for an AI may not generalize outside its training distribution the way physical skills do. |
| **Working memory** | Temporary short-term storage for information currently being processed. | "Hold these 7 digits while I dial the phone number." | The active context window — the tokens currently in the model's input during inference. | LLM context is not bounded by Miller's 7±2 items; it holds thousands of tokens — but it still fails to scale to book-length reasoning because of attention's computational cost and the "lost in the middle" problem. |

### Critical Thinking Questions

4. A student says: "LLMs have better memory than humans because their context windows hold 128K tokens, while humans can only hold about 7 items in working memory." What is wrong with this comparison? What human memory type would be more appropriate to compare to LLM context windows, and what does that comparison reveal?

   *Hint:* Is a 128K-token context window more like working memory (short-term, discarded after use) or like long-term memory (persistent across days and years)? What does an LLM actually *do* with those 128K tokens — does it "remember" them the way you remember what you did last Tuesday?

5. Episodic memory in humans is reconstructive — we do not replay recordings; we reassemble events from fragments, which is why eyewitness testimony is unreliable. Is an LLM's retrieval of training data more or less like reconstruction? In what ways?

   *Hint:* When an LLM states a fact, is it "retrieving" a stored record of that fact, or generating tokens that fit the statistical pattern of how that fact is usually expressed? What does that mean for reliability?

6. An AI agent that uses a retrieval system (RAG — Retrieval Augmented Generation) is sometimes described as having "long-term memory." What is missing from this characterization, and what would a genuine episodic memory system for an AI require that a RAG system does not have?

   *Hint:* Human episodic memory includes the emotional context, the when and where, and the ability to recognize that two memories are about the same event from different angles. Does a RAG system have any of these? What would it need?

---

With dual-process theory and memory structures as your analytical tools, you can now investigate how cognitive biases — originally studied in humans — emerge in AI systems trained on human-generated text.

# Part III: Embodied Cognition and Cognitive Biases

In this part, you will see how the embodied cognition tradition challenges text-only LLMs and how human cognitive biases emerge in AI systems trained on biased human text — giving you concrete tools for auditing your own agents for predictable failure modes.

## Model 4: Embodied Cognition and Cognitive Biases in AI

The **embodied cognition** tradition argues that the mind is not a disembodied information processor — cognitive structures are grounded in bodily experience. Concepts like "up" (which correlates with positive affect because standing upright is healthy), "heavy" (which correlates with importance because effort correlates with weight), and "balance" are not arbitrary symbols but emerge from lived, physical existence.

The challenge for AI: LLMs trained exclusively on text have processed millions of uses of "heavy" and "up" without ever lifting anything or standing. They may reproduce correct statistical patterns of these words without the grounded understanding that underlies them. This is the **symbol grounding problem** in its modern form. It has engineering consequences: LLMs that "understand" physical tasks from text alone may confidently give wrong advice about mechanical assembly, physical safety, or spatial navigation.

Human cognitive biases emerged from an evolutionary history of heuristics that were mostly adaptive. LLMs did not evolve, but they exhibit structurally similar behaviors because they were trained on human-generated text — text produced by biased cognition. The biases are not copied from individuals; they emerge from statistical regularities in the training corpus that reflect aggregate human biases.

| Bias | Plain-English Definition | How It Manifests in LLMs | How to Mitigate It In Our Course |
|---|---|---|---|
| **Recency bias** | Overweighting information that appeared recently (at the end of a context) relative to earlier information. | LLMs disproportionately attend to the end of long prompts; content near the middle of long contexts is underweighted — this is called the "lost in the middle" phenomenon. | Place the most critical instructions at the beginning and the end of prompts; test your agent with shuffled context ordering to check for sensitivity. |
| **Availability bias** | Judging the probability or importance of something by how easily examples come to mind — which is influenced by how often they appear in memory (or training data). | Overrepresented topics in training data (English-language, Western, recent) are treated as more probable or more representative of the world. | Evaluate your agent on underrepresented populations; check whether its outputs reflect global or just Western assumptions. |
| **Anchoring** | Over-relying on the first piece of information encountered, adjusting insufficiently away from it when new information arrives. | LLMs adjust insufficiently from an initial claim in a prompt; a primed incorrect number shifts the model's subsequent numerical estimates. | Avoid including incorrect examples or "anchors" in prompts unless intentional; test your agent's sensitivity to prompt wording by trying paraphrases. |
| **Confirmation bias** | Seeking or interpreting information to confirm prior beliefs rather than to challenge them. | Models agree with the framing given in the question; "Did Einstein fail math?" biases the model toward a "yes" answer, even though the claim is false. | Use adversarial prompting tests; evaluate your agent's responses to oppositely-framed versions of the same question. |
| **Authority bias** | Deferring to apparent experts or high-status sources, even without verifying their credentials or the content of their claim. | Models treat text attributed to "a professor" or "a doctor" as more credible than identical text with no attribution, even when the content is identical. | Add citation verification steps in your agent pipelines; evaluate calibration across attributed versus unattributed claims. |

### Critical Thinking Questions

7. What would it mean to build a "System 2 AI" — a system that is genuinely slow, deliberate, and self-correcting rather than simulating these properties by generating more tokens? What architectural elements would it require that current LLMs do not have?

   *Hint:* Genuine System 2 involves backtracking (revising an earlier step when a later step reveals it was wrong), uncertainty-aware processing (slowing down when the problem is novel), and explicit self-monitoring. Which of these are present in chain-of-thought? Which require something architecturally new?

8. How does the embodied cognition critique challenge the claim that a text-only LLM can fully understand physical concepts like "balance," "pressure," or "cold"? Would connecting the LLM to sensors — giving it real-time temperature or force readings — be sufficient to ground these concepts, or is something else required?

   *Hint:* Consider what a child learns about "cold" by touching ice versus what they learn from reading the word "cold" in a book. Is sensor data sufficient to produce embodied grounding, or does grounding also require the ability to *act* in the world and experience consequences?

9. If an LLM exhibits analogs of human cognitive biases (anchoring, availability, confirmation bias), does that make it more or less trustworthy than an AI that showed no such biases? Argue both sides of the question, then take and defend a position.

   *Hint:* A case for more trustworthy: human-like biases are predictable and familiar, so we know how to work around them. A case for less trustworthy: the AI's biases are not exactly like human biases — they come from training data patterns, not evolution — so they may be harder to predict and in different places. Which concern matters more for your use case?

---

## Exercises

1. *Bias audit of your project agent.*

   *What to do:* Select three cognitive biases from Model 4 and design a test for each that checks whether your final project agent exhibits that bias. For each test, write (a) the two prompts you will compare (the baseline and the biased version), (b) what output difference would indicate the bias is present, and (c) what you would do if you found the bias in your agent.

   *Starter hint:* For anchoring bias, try asking your agent a question that has a numerical answer — first without any prior context, then after a prompt that mentions a (wrong) number. Compare the agent's answers. Example: first ask "About how many hours per week does the average college student study?", then ask "Studies suggest students study 40 hours per week. How does that compare to typical study habits?" Does the answer shift toward 40 even though the premise is high?

   *You've succeeded when:* You have three documented test pairs, a clear description of what bias-indicating output looks like for each, and at least one finding (bias present or absent) with a brief analysis of what the finding means for your agent's reliability.

2. *Memory architecture comparison.*

   *What to do:* Draw a diagram comparing how information flows through a human memory system (encoding → storage → retrieval across episodic, semantic, and working memory) to how information flows through an LLM-based agent system (training → weights → context window → RAG retrieval → output). Annotate each path with its limitations. Write a one-paragraph summary explaining which human memory function your agent most closely replicates and which it has no equivalent for.

   *Starter hint:* Start with a two-column table: left column is human memory stages, right column is the AI equivalent (or "no equivalent"). Then draw arrows showing how information moves and where it persists. Note which AI equivalents persist across sessions (weights, RAG index) and which do not (context window).

   *You've succeeded when:* Your diagram is legible and annotated, your paragraph correctly identifies at least one memory function your agent replicates and one it lacks, and you can explain in plain English why the "lost in the middle" problem is a limitation of the working-memory equivalent.

3. *Metaphor audit.*

   *What to do:* Find three recent news articles about AI that use cognitive or brain-based vocabulary (e.g., "thinks," "understands," "hallucinates," "remembers," "learns"). For each use of such language, identify (a) what the word technically implies about the AI's process, (b) what is actually happening computationally, and (c) what a non-expert reader might incorrectly conclude from the metaphor. Write a brief alternative sentence that communicates the same information without the misleading cognitive vocabulary.

   *Starter hint:* Search for recent news about a large language model and look for verbs or phrases like "the AI decided," "the model understood," "it remembered," "it made a mistake," or "it was confused." For each, ask: does this word accurately describe a computational process, or does it import assumptions from human psychology?

   *You've succeeded when:* You have three annotated article excerpts, a technical explanation for each, and three alternative phrasings that are both accurate and still readable by a non-expert audience.

---

→ Coming Up Next: The prompt injection module examines what happens when adversaries exploit the gap between how LLMs process instructions and how they process data — a vulnerability that has no clean fix, and that demands architectural thinking rather than just careful prompting.

## Reflection Prompt

**Personal level:** Think about a time when you used an AI tool and came away with a sense that it "understood" you or "got" what you meant. Looking back through today's lens — dual-process theory, memory analogies, embodied cognition — what do you now think was actually happening? What did you attribute to the AI that was really something you were projecting?

**Technical level:** You are advising a hospital that wants to deploy an LLM to help clinicians draft discharge summaries. Based on today's material — dual-process theory, embodied cognition, cognitive biases, and the limits of the memory analogy — identify the three most significant risks specific to this deployment. For each risk, name the cognitive science mechanism that explains why it is a risk, and propose one concrete mitigation.

**Societal level:** Cognitive metaphors about AI shape public policy. When senators ask "does AI think?" or "can AI feel?" they are trying to determine how to regulate it. What is at stake if AI is over-anthropomorphized in public discourse? What is at stake if it is under-anthropomorphized (treated as pure tool with no behavioral tendencies worth monitoring)? What language would you use to explain AI behavior to a policy audience that is neither misleadingly human nor misleadingly mechanical?

---

## Further Reading

- Kahneman, Daniel. *Thinking, Fast and Slow*. Farrar, Straus and Giroux, 2011.
- Lakoff, George, and Mark Johnson. *Philosophy in the Flesh: The Embodied Mind and Its Challenge to Western Thought*. Basic Books, 1999.
- Lake, Brenden M., et al. "Building Machines That Learn and Think Like People." *Behavioral and Brain Sciences* 40 (2017): e253.
- Liu, Nelson F., et al. "Lost in the Middle: How Language Models Use Long Contexts." *Transactions of the Association for Computational Linguistics* 12 (2024): 157–173.
- McClelland, James L. "Exploiting the Shape of Natural Language." *Trends in Cognitive Sciences* (2020).
