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

# Part I: Biological Inspiration and Its Limits

## 1. Where AI Borrowed from the Brain

The McCulloch-Pitts neuron (1943) was the original metaphor: a biological neuron either fires or does not, so they modeled computation as a weighted threshold function. Hebb's rule (1949) — "neurons that fire together wire together" — became the conceptual ancestor of backpropagation: connections that contribute to correct outcomes are strengthened. Convolutional neural networks were directly inspired by Hubel and Wiesel's discovery (1959–1968) that visual cortex neurons respond to edges at specific orientations and locations before combining into higher-order features — exactly what convolutional filters do.

The transformer's attention mechanism borrows the vocabulary of the **attentional spotlight**: the idea from cognitive psychology that perception is not passive but directed, that the mind selects and amplifies certain stimuli. In transformers, attention weights determine which parts of the input most influence each output token. The analogy is suggestive but inexact: biological attention is selective suppression and amplification implemented in prefrontal-parietal circuits, not a dot-product similarity score over a flat token sequence.

**Why metaphors matter.** George Lakoff and Mark Johnson argue in *Philosophy in the Flesh* that conceptual metaphors are not decorative — they are the cognitive substrate of abstract thought. When we call an LLM a "brain," we import expectations: that it has goals, that it learns continuously, that its errors are like forgetting. All three expectations are wrong in important ways, and each has caused real misjudgments in AI policy and public discourse.

---

## 2. The Cognitive Turn in Evaluation

Historically, AI systems were evaluated on task accuracy: percentage correct, BLEU score, win rate. A newer approach — partly inspired by cognitive science — asks whether AI systems make the same *types of errors* as humans. This matters for two reasons: systems that err humanly may be more interpretable and their failure modes more predictable; systems that err in alien ways may be trusted inappropriately because their confidence is high even when they are wrong.

Vision models were found to be susceptible to adversarial perturbations invisible to humans, which initially looked like a radical difference from biological vision. Later research showed human vision is also susceptible to certain illusions and context effects that mirror adversarial phenomena at a different scale. LLMs make errors that look like human cognitive biases — anchoring, availability, confirmation — but also errors that have no human analog, such as radical inconsistency across paraphrases of the same question.

---

# Part II: Dual-Process Theory and Memory

## 3. System 1 and System 2 in AI

Daniel Kahneman's dual-process theory distinguishes two cognitive modes. **System 1** is fast, automatic, associative, high-confidence, and largely unconscious — the part of your mind that instantly reads the word "cat" without effort. **System 2** is slow, deliberate, effortful, and self-monitoring — the part that checks the work, asks "wait, is that right?" and changes course. System 1 is indispensable for most of cognition; its failure modes include overconfidence, susceptibility to priming, and failure in novel situations that don't match prior patterns.

A standard LLM doing a single forward pass is a **System 1 machine**: it produces a high-confidence output extremely fast, without verification or backtracking, based entirely on learned patterns. **Chain-of-thought prompting** is an attempt to simulate System 2 by requiring the model to generate intermediate reasoning steps before a final answer. It works partially — CoT improves accuracy on tasks requiring multi-step arithmetic and logic — but the "reasoning" is still generated in the same forward-pass manner, without genuine backtracking or error-checking. A **self-correction loop** (generate → critique → revise) more closely approximates System 2, though the critique is itself generated by the same pattern-matching process.

## Model 2: Dual-Process Theory Applied to AI Systems

| System | Type | Speed | Confidence | Error Pattern | Chain-of-Thought Helps? |
|---|---|---|---|---|---|
| Standard LLM (single forward pass) | System 1 | Very fast | High, often uncalibrated | Confident errors on novel patterns | N/A — no CoT |
| LLM with chain-of-thought | System 1 + simulated System 2 | Slower | Somewhat better calibrated | Fewer arithmetic/logic errors; still fails novel situations | Yes, moderately |
| LLM with self-correction loop | Closer to System 2 | Much slower | Improved in tested domains | Can catch some surface errors; blind to own deep biases | Depends on critic quality |
| Human fast thinking (System 1) | System 1 | Very fast | High | Optical illusions, heuristic errors, priming effects | N/A |
| Human deliberate thinking (System 2) | System 2 | Slow | Appropriately uncertain | Logic errors when fatigued; can correct System 1 mistakes | N/A |

[[MC]]
The dual-process theory suggests LLMs are primarily System 1 machines. The most important implication for deploying LLMs as agents is:
- (x) LLMs will tend to give fast, confident, but potentially wrong answers, especially in novel situations — which is why deliberate reasoning structures (CoT, multi-agent critique) and human oversight are essential
- ( ) LLMs should only be used for tasks that require fast responses and not for slow analytical tasks
- ( ) System 1 thinking is less useful than System 2 and should be avoided in all agent designs
- ( ) LLMs should always use chain-of-thought regardless of task type or cost

---

## 4. Memory Structures in Humans and AI

Cognitive psychology distinguishes multiple memory systems that serve very different functions. The table below maps these onto AI equivalents — but mapping is not identity, and the "limitations" column is as important as the others.

## Model 1: Human Memory Types vs. AI Equivalents

| Human Memory Type | Human Example | AI Equivalent | Limitations of the Analogy |
|---|---|---|---|
| Episodic memory | "I remember my 7th birthday party" | Conversation history in context window; logged traces | Context window is finite and discarded; AI has no autobiographical continuity across sessions |
| Semantic memory | "Paris is the capital of France" | Weights learned during training | Weights encode statistical patterns, not verified facts; knowledge has a training cutoff |
| Procedural memory | "How to ride a bike" | Fine-tuned task behaviors; agent tool-use patterns | AI procedural knowledge is linguistic, not sensorimotor; "knowing how" for AI may not generalize outside training distribution |
| Working memory | "Hold these 7 digits while I do arithmetic" | Active context window (~limited tokens of live state) | LLM context is not bounded by Miller's 7±2; it is bounded by token count, which is much larger but still fails to scale to book-length reasoning |

### Critical Thinking Questions

1. A student says: "LLMs have better memory than humans because their context windows hold 128K tokens and humans can only hold 7 items in working memory." What is wrong with this comparison, and what human memory capacity would be more apt to compare?
2. Episodic memory in humans is reconstructive — we do not replay recordings, we reassemble events from fragments, which is why eyewitness testimony is unreliable. Is an LLM's retrieval of training data more or less like reconstruction? In what ways?
3. An AI agent that uses a retrieval system (RAG) is sometimes described as having "long-term memory." What is missing from this characterization, and what would a genuine episodic memory system for an AI require?

---

# Part III: Embodied Cognition and Cognitive Biases

## 5. Embodied Cognition

The **embodied cognition** tradition (Lakoff, Varela, Maturana, Thompson) argues that the mind is not a disembodied information processor — cognitive structures are grounded in bodily experience. Concepts like "up" (which correlates with positive affect because standing upright is healthy), "heavy" (which correlates with importance because effort correlates with weight), and "in front" (which is defined relative to a facing body) are not arbitrary symbols but emerge from lived, physical existence.

The challenge for AI: LLMs trained exclusively on text have processed millions of uses of "heavy" and "up" without ever lifting anything or standing. They may reproduce the correct statistical patterns of these words without the grounded understanding that underlies them. This is the **symbol grounding problem** in its modern form. Multimodal models trained on image-text pairs have more grounding than text-only models, but still lack proprioception, embodied action, and the feedback loops of a body navigating the world.

This is not merely a philosophical puzzle. It has engineering consequences: LLMs that "understand" physical tasks from text alone may confidently give wrong advice about mechanical assembly, physical safety, or spatial navigation — not because they lack information, but because their representation of the concepts is ungrounded.

---

## 6. Cognitive Biases in AI

Human cognitive biases emerged from an evolutionary history of heuristics that were mostly adaptive. LLMs did not evolve, but they exhibit structurally similar behaviors because they were trained on human-generated text — text produced by biased cognition. The biases are not copied from individual humans; they emerge from statistical regularities in the training corpus that reflect aggregate human biases.

## Model 3: Cognitive Biases in AI

| Bias | Definition | How It Manifests in LLMs | Mitigation |
|---|---|---|---|
| Recency bias | Overweighting recent information relative to earlier information | LLMs disproportionately attend to the end of long prompts; context near the middle is underweighted ("lost in the middle" phenomenon) | Place critical instructions at the beginning and end of prompts; test with shuffled context ordering |
| Availability bias | Judging probability by how easily examples come to mind | Overrepresented topics in training data (English-language, Western, recent) are treated as more probable or more representative | Deliberate dataset balancing; evaluation on underrepresented populations |
| Anchoring | Over-relying on the first piece of information encountered | LLMs adjust insufficiently from an initial claim in a prompt; a primed incorrect number shifts the model's numerical estimates | Avoid including anchors unless intentional; test sensitivity to prompt wording |
| Confirmation bias | Seeking or interpreting information to confirm prior beliefs | Models agree with the framing given in the question; "Did Einstein fail math?" biases toward yes | Adversarial prompting tests; evaluate model responses to oppositely framed versions of the same question |
| Authority bias | Deferring to apparent experts or high-status sources | Models treat text attributed to "a professor" or "a doctor" as more credible even with identical content | Citation verification steps in agent pipelines; calibration evaluation across attributed vs. unattributed claims |

### Critical Thinking Questions

4. What would it mean to build a "System 2 AI" — a system that is genuinely slow, deliberate, and self-correcting rather than simulating these properties through faster generation? What architectural elements would it require?
5. How does the embodied cognition critique challenge the claim that a text-only LLM can fully understand physical concepts like "balance," "pressure," or "cold"? Would connecting the LLM to sensors be sufficient, or is something else required?
6. If an LLM exhibits analogs of human cognitive biases, does that make it more or less trustworthy than an AI that showed no such biases? Argue both sides, then take a position.

---

## Reflection Prompt

In your notebook: you are advising a hospital that wants to deploy an LLM to help clinicians draft discharge summaries. Based on today's material — dual-process theory, embodied cognition, cognitive biases, and the limits of the memory analogy — identify the three most significant risks specific to this deployment, and for each risk, name the mechanism from cognitive science that explains why it is a risk and one concrete mitigation.

---

## Further Reading

- Kahneman, Daniel. *Thinking, Fast and Slow*. Farrar, Straus and Giroux, 2011.
- Lakoff, George, and Mark Johnson. *Philosophy in the Flesh: The Embodied Mind and Its Challenge to Western Thought*. Basic Books, 1999.
- Lake, Brenden M., et al. "Building Machines That Learn and Think Like People." *Behavioral and Brain Sciences* 40 (2017): e253.
- Liu, Nelson F., et al. "Lost in the Middle: How Language Models Use Long Contexts." *Transactions of the Association for Computational Linguistics* 12 (2024): 157–173.
- McClelland, James L. "Exploiting the Shape of Natural Language." *Trends in Cognitive Sciences* (2020).
