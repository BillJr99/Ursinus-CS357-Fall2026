<!--
author: Prof. Bill Mongan
language: en
narrator: US English Male
import: https://raw.githubusercontent.com/liaScript/coderunner/master/README.md
link: https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap
-->

# Why Doesn't AI Give the Same Answer Twice? Deterministic and Probabilistic Computing

### Before You Start

**What you need:** Nothing installed — this one is discussion and paper first. Python only if you run the optional demo.

**What you will have at the end:** a working rule for telling deterministic systems from probabilistic ones, and why that changes how you test them.

Work through the sections in order — each one builds on the last, and the code blocks are meant to be run as you reach them, not read past.

---

## Overview and Roles

Most software you have used behaves predictably: the same input always produces the same output. AI systems built on large language models deliberately do not. Understanding *why* — and what that means for how you interpret and rely on AI outputs — is one of the most practically important ideas in this course.

This activity connects to the **sampling and generation** material from earlier in the term. You will classify computing systems as deterministic or probabilistic, examine the cognitive trap called *automation bias*, and reason about the specific dangers that arise when people treat probabilistic AI outputs as reliable ground truth.

**Estimated time:** 45-60 minutes

**Team roles (rotate for each Part):**

- **Manager** — Keeps the group on task and on time.
- **Recorder** — Writes down the group's agreed answers.
- **Presenter** — Shares the group's findings with the class.
- **Reflector** — Notes what surprised the group and what questions remain.

---

# Part I: Two Kinds of Computation

In this part, you will classify computing systems as deterministic or probabilistic and build intuition for why the distinction matters before you encounter it in AI.

## Model 1: Deterministic Systems

A **deterministic** program always produces exactly the same output given the same input and the same starting state. There is no randomness; the result is fully predictable.

```python
def add(a, b):
    return a + b

# Always returns 5 — no exceptions, no surprises.
print(add(2, 3))
```

Database queries, sorting algorithms, cryptographic hashes, and arithmetic are all deterministic. This predictability is a feature: it makes these systems easy to test, debug, and trust because you can verify them exhaustively.

### Three key properties of deterministic systems:

1. **Reproducibility** — Run it again, get the same answer.
2. **Verifiability** — You can prove correctness by checking every possible input (for finite input spaces).
3. **Debuggability** — The bug that produced output X will always produce output X under the same conditions, making it findable.

---

## Model 2: Probabilistic Systems

A **probabilistic** (or *stochastic*) program intentionally samples from a probability distribution, so the output varies across runs even with identical input.

```python
import random

def flip_coin():
    return random.choice(["heads", "tails"])

# Could return either — by design.
print(flip_coin())
```

Randomness is not a bug here; it is a feature. Probabilistic systems are used when we want to explore a space of possibilities, when the real-world phenomenon being modeled is inherently uncertain, or when avoiding predictability is itself valuable (cryptography, game fairness).

Examples outside AI: Monte Carlo retirement simulations, weather forecast models, network routing under load, randomized algorithms in competitive programming.

---

## Questions

**Q1.** Classify each of the following as **deterministic (D)** or **probabilistic (P)**. For each, briefly explain why.

| System | D or P? | Why? |
|---|---|---|
| Python's `sorted([3, 1, 2])` | | |
| Rolling a die in a board-game simulator | | |
| A search engine returning results for "best pizza" | | |
| SHA-256 hash of a file | | |
| A 10-day weather forecast model | | |
| `SELECT * FROM students WHERE grade = 'A'` | | |
| An LLM generating the next token at temperature = 0.7 | | |

> *Hint:* Ask yourself: "If I run this again with exactly the same input, am I guaranteed the same output?" Be careful with the search engine — the answer may surprise you.

**Q2.** A classmate argues: "LLMs aren't really random — they just look at patterns in training data and output the most likely word." What is accurate about this claim, and what is it missing?

> *Hint:* Recall what the temperature parameter does. Even at temperature = 0, many production implementations produce slightly different results across runs because of floating-point rounding and GPU non-determinism. The model samples from a distribution; it does not look up a deterministic answer.

**Q3.** The table below shows two outputs from the same prompt ("What is the capital of France?") submitted to the same model twice. Which output is more dangerous from a user-trust perspective, and why?

| Run | Output |
|---|---|
| Run 1 | "The capital of France is Paris." |
| Run 2 | "The capital of France is Lyon, though Paris serves as the main administrative hub." |

[(X)] Run 2 — it is factually wrong, yet it is presented in the same confident, authoritative prose as the correct answer. A user cannot tell the difference from the output alone.
[( )] Run 1 — consistent outputs suggest the model has memorized rather than understood, which is worse than variance.
[( )] Both are equally dangerous because any AI output should be distrusted.
[( )] Neither — this question is too simple for an LLM to get wrong, so the scenario is unrealistic.

> In practice, the same kind of confident-sounding error occurs on far less checkable claims — legal citations, medical statistics, historical dates — where most readers cannot spot the mistake.

---

**Bridge to Part II:** Now that you can classify systems as deterministic or probabilistic, Part II examines a cognitive trap that makes probabilistic systems especially risky: the human tendency to treat computed outputs as authoritative regardless of whether the system is reliable.

---

# Part II: Automation Bias — Why Humans Trust Machines

In this part, you will examine the research on *automation bias* — the tendency to over-rely on automated systems — and classify the specific failure modes it produces.

## Model 3: Automation Bias Defined

**Automation bias** (Parasuraman & Manzey, 2010) is the tendency for humans to over-rely on automated decision aids in two ways:

1. **Omission errors** — The human skips manual checks they would have performed without the automated aid, because the machine's output feels sufficient.
2. **Commission errors** — The human acts on an incorrect automated recommendation without questioning it, because they defer to the machine's apparent authority.

Automation bias arises even among trained experts, even when the automated system has a known error rate, and even when stakes are high. In a landmark study, Skitka et al. (1999) found that experienced pilots failed to detect autopilot errors at significantly higher rates when an automation aid was present — *even after being explicitly warned that the aid was imperfect*.

> **Common Misconception:** Automation bias is a problem only for non-technical or "tech-naive" users. Research consistently shows that trained professionals — pilots, radiologists, financial analysts, software engineers — exhibit automation bias at similar or higher rates than non-experts, precisely because their professional workflow incorporates these tools and they have learned to trust them.

---

## Model 4: A Taxonomy of Trust Failure Modes

Not all trust miscalibration looks the same. The following four modes each cause a different kind of harm:

| Mode | Description | Example |
|---|---|---|
| **Under-trust** | Human ignores a correct automated recommendation | Dismissing a correct fraud alert because "it feels fine" |
| **Over-trust / automation bias** | Human accepts an incorrect automated recommendation | Following GPS directions into a lake |
| **Complacency** | Human stops monitoring an automated system once it is running | Autopilot disengages silently; pilot doesn't notice for 90 seconds |
| **Skill fade** | Long-term loss of the ability to perform the task manually after years of automation | Unable to navigate without GPS after a decade of relying on it |

---

## Questions

**Q4.** In 2023, the attorneys representing a client in *Mata v. Avianca, Inc.* submitted a federal court brief that cited six legal precedent cases — all of which were entirely fictional cases generated by a chatbot. Neither attorney independently verified any citation. The judge sanctioned both attorneys.

Which failure mode from the taxonomy above best describes what happened? What would "appropriately calibrated trust" have looked like?

> *Hint:* Attorneys have a professional and ethical obligation to verify every citation before submitting a brief. The question is not whether they trusted the tool, but why the trust was not bounded by the verification step they knew was required.

**Q5.** A hospital deploys an AI system that flags potential drug interactions for nursing review. A nurse, disagreeing with a specific flag based on her clinical experience, overrides it without documenting her reasoning.

Is this automation bias, appropriate expert judgment, or something else? What information would you need to determine which?

> *Hint:* Both under-trust and over-trust are errors. The right answer depends on: the nurse's track record vs. the AI's precision and recall on this flag type, whether the patient is harmed by the override, and whether lack of documentation creates institutional risk regardless of outcome.

**Q6.** Which of the following best explains why automation bias persists even when humans consciously know that a system is fallible?

[(X)] Checking automated outputs requires effortful cognition. The brain conserves effort when it perceives a trusted external source — a process psychologists call "cognitive offloading." This is adaptive in most contexts but becomes dangerous when the trusted source is unreliable.
[( )] Humans inherently distrust their own judgment and will always prefer any external signal over their own reasoning.
[( )] Automation bias has been largely debunked; modern users who understand AI do not exhibit it.
[( )] Trained users never exhibit automation bias — only untrained or non-expert users do.

---

**Bridge to Part III:** You have now seen that humans over-trust automated systems even when they know better. Part III asks: what happens when the automated system is not just fallible but *cannot* signal its own uncertainty? That combination — probabilistic outputs delivered with authoritative-looking confidence — is what makes LLMs distinctively risky.

---

# Part III: The Danger When Probabilistic Meets Authoritative

In this part, you will synthesize Parts I and II to reason about the failure mode that is specific to large language models: high-confidence-sounding outputs from an inherently probabilistic system, consumed by users who are primed to over-trust.

## Model 5: The Confidence-Calibration Gap

Most probabilistic systems explicitly communicate their uncertainty. A weather app shows "70% chance of rain." A spam filter says "94% confidence." A Bayesian classifier outputs a posterior distribution.

LLMs typically do not. They generate fluent, confident-sounding prose regardless of whether the underlying probability distribution is sharply peaked (the model is, in some sense, "sure") or flat (it is guessing).

Read the following two outputs. Both come from the same model in the same fluent style:

```yaml
User: What is the boiling point of water at sea level?
AI:   The boiling point of water at sea level is 100°C (212°F).

User: Who won the 1987 Ursinus College intramural chess tournament?
AI:   The 1987 Ursinus College intramural chess tournament was won by
      Michael Chen, a junior majoring in mathematics.
```

The first answer is verifiable and correct. The second is almost certainly fabricated — but the model delivers both in identical, authoritative prose with no hedging, no uncertainty signal, and no difference in tone.

> **Common Misconception:** If an AI "sounds confident," it probably is correct. In fact, the fluency and grammatical correctness of an LLM's output are driven by the language modeling objective — predict the next plausible token — not by the accuracy of the underlying claim. A model can generate a perfectly grammatical, confidently phrased, completely false sentence.

---

## Model 6: Three Compounding Risk Factors

When probabilistic AI outputs are treated as authoritative, three factors compound to make the problem worse than it would be with any other unreliable information source:

| Risk Factor | Why It Matters |
|---|---|
| **Surface credibility** | Well-formed prose, plausible structure, and specific-sounding details make false claims hard to distinguish from true ones without independent verification. Fabricated citations look like real citations. |
| **Volume** | AI can generate hundreds of plausible-sounding claims per minute. The cognitive load to verify each one is multiplicatively larger than the cost to generate them. |
| **Domain opacity** | Many high-stakes AI use cases — medical, legal, scientific, financial — are precisely the domains where most users lack the expertise to evaluate the output independently. The highest-stakes domains have the lowest baseline for catching errors. |

---

## Questions

**Q7.** Design a concise "sanity check" protocol (at most four steps) that a student should apply before using any piece of AI-generated information in a graded assignment. Be specific — avoid vague steps like "check if it's right."

> *Hint:* Think about: (1) Is this the kind of claim that *can* be verified with a primary source? (2) What would happen if it were wrong? (3) How would I explain to an instructor that I verified this?

**Q8.** A classmate argues: "This problem will go away once AI systems always display explicit confidence scores on every output." Do you agree? What risk factors from Model 6 would still remain even if confidence scores were perfect?

> *Hint:* Think about calibration: does "80% confidence" mean the model is right 80% of the time on this type of claim? Who would check? And consider: does a confidence score on each sentence solve the volume problem, or does reading 200 scores per document just add another layer of cognitive load?

**Q9.** Match each real-world scenario to the primary risk factor from Model 6 (Surface Credibility, Volume, or Domain Opacity) that makes it most dangerous:

| Scenario | Primary Risk Factor |
|---|---|
| A student submits a 15-source bibliography; three citations are AI-generated and fictional, but formatted correctly and plausibly titled | |
| A content moderation system flags 40,000 posts per hour; human reviewers approve AI decisions without reading flagged content because the queue never clears | |
| An AI-generated radiology summary misidentifies a lesion; the reviewing radiologist, who is not an AI expert, assumes the AI output reflects ground truth | |

**Q10.** Which design change most directly reduces automation bias without requiring users to become AI experts?

[(X)] Displaying explicit uncertainty language ("I am not confident about this — please verify"), requiring confirmation before high-stakes outputs are acted upon, and showing alternative responses alongside the primary one — so the user perceives the system as offering options, not delivering verdicts.
[( )] Making the AI system fully deterministic, so it always gives the same answer and users know what to expect.
[( )] Increasing the AI's accuracy to 99% — at that threshold, automation bias becomes statistically acceptable.
[( )] Removing AI from high-stakes domains entirely until the technology is perfect.

---

# Synthesis: Discussion

Before your Presenter shares with the class, agree on answers to the following as a group:

1. In one sentence, complete this argument: "It is specifically dangerous to treat probabilistic AI outputs as authoritative because ___."

2. Name one domain *outside of AI* where deterministic outputs are treated as more authoritative than they deserve to be.

3. State one concrete habit you will adopt after today to protect yourself from automation bias when using AI tools in this course or professionally.

4. *Challenge question:* Could an AI system be designed that is both probabilistic *and* well-calibrated in its expressed confidence? What would that require, and why don't current LLMs do it?

---

## Key Terms

| Term | Definition |
|---|---|
| Deterministic | A system that always produces the same output for the same input |
| Probabilistic / stochastic | A system that samples from a probability distribution, so outputs vary across runs |
| Automation bias | The tendency to over-rely on automated systems, accepting their outputs without independent verification |
| Calibration | A system is calibrated if its stated confidence matches its actual accuracy rate — e.g., a calibrated model that says "80% confidence" is correct 80% of the time |
| Cognitive offloading | Delegating mental work to an external tool or system, reducing cognitive effort at the cost of reduced engagement with the result |

---

## Further Reading

- Parasuraman, R. & Manzey, D. H. (2010). Complacency and bias in human use of automation. *Human Factors, 52*(3), 381-410.
- Skitka, L. J., Mosier, K. L., & Burdick, M. (1999). Does automation bias decision-making? *International Journal of Human-Computer Studies, 51*(5), 991-1006.
- Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the dangers of stochastic parrots: Can language models be too big? *FAccT 2021.*
- Carr, N. (2014). *The Glass Cage: How Our Computers Are Changing Us.* W. W. Norton.
- Marcus, G. & Davis, E. (2019). *Rebooting AI: Building Artificial Intelligence We Can Trust.* Pantheon.
