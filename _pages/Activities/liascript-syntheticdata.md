<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?... or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-syntheticdata.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Synthetic Data: Using AI to Train AI

CS357 - Foundations of Artificial Intelligence / Agentic AI | Ursinus College

---

## POGIL Roles

This activity uses the **POGIL** (Process Oriented Guided Inquiry Learning) structure. Assign one role to each group member before beginning.

| Role | Responsibilities |
|------|-----------------|
| **Manager** | Keeps the group on task, monitors time, ensures everyone contributes, and moves the group to the next question when ready |
| **Recorder** | Writes down the group's agreed answers and keeps a record of key decisions and reasoning |
| **Spokesperson** | Presents the group's answers during class discussion and asks the instructor clarifying questions on behalf of the group |
| **Reflector** | Monitors group process, notes what is working and what is not, and leads the end-of-activity reflection |

> Rotate roles across activities so everyone practices each one.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Synthetic Data** | Data that is artificially generated rather than collected from real-world events or people — created by rules, simulation, or generative AI models | GPT-3.5 generating 52,000 instruction-response pairs to train Stanford's Alpaca model at a cost of ~$500, replacing expensive human labeling |
| **Instruction Tuning** | Fine-tuning a language model on thousands of (instruction, response) pairs so it learns to follow natural language commands rather than just predict the next token | Training a base model on synthetic examples like "Summarize the following paragraph: ..." and the expected response |
| **Model Collapse** | The phenomenon where models trained on AI-generated data across multiple generations progressively lose the rare and diverse patterns found in real human data — like a photocopy of a photocopy getting blurrier each time | After 10 generations of synthetic-to-synthetic training, models produce only the most common, central outputs and fail on unusual inputs |
| **Self-Instruct** | A pipeline in which a model uses a small seed set of human-written examples to generate new instruction-response pairs, then uses those to generate more — bootstrapping a large dataset from a small one | Stanford Alpaca generated 52K examples from 175 human seeds using this approach |
| **Evol-Instruct** | An approach to synthetic data generation that takes simple instructions and iteratively rewrites them to be harder, more constrained, or more nuanced — evolving easy examples into hard ones | Transforming "Write a function that sorts a list" into "Write a function that sorts a list without any built-in sort functions, in O(n log n) time, with an explanation of the algorithm" |
| **Sim-to-Real Gap** | The difference in difficulty between a task in a controlled simulation and the same task in messy real-world conditions — data generated in clean simulation may not prepare an agent for real-world variation | An agent trained on clean, synthetic customer service dialogues that struggles with real user queries that include typos, implicit assumptions, and mid-conversation topic changes |

---

## Model 1: Why Synthetic Data?

The key insight behind synthetic data is that data labeling is often the bottleneck, not compute. A radiologist who can label 20 chest X-rays per day costs ~$300,000 per year and produces roughly 5,000 labeled examples annually. A single GPU running a generative model can produce thousands of synthetic medical descriptions per hour. The question is not whether this is useful — it obviously is — but whether synthetic data is a complete substitute for real data, a dangerous shortcut, or something in between. As you will see in this activity, the honest answer depends entirely on what you are generating, how carefully you filter it, and whether you have any real data to validate against.

### The Data Scarcity Problem

High-quality labeled data is the fuel of modern machine learning, but it is expensive, slow, or sometimes impossible to obtain:

- **Medical data** requires expert annotation by radiologists, pathologists, or clinicians; IRB approval; and patient de-identification. A single labeled CT scan dataset may cost hundreds of thousands of dollars to produce.
- **Legal data** is often confidential and jurisdiction-specific. Training a legal reasoning model requires annotated case law that cannot be freely shared even among researchers.
- **Specialized domains** such as semiconductor design, drug interaction prediction, and rare language translation have few practitioners and even fewer labeled examples.
- **Future scenarios** do not yet exist: you cannot collect data about how an agent should handle a new type of cyberattack before that attack type is publicly known.

**Synthetic data** is artificially generated data. It can be generated by hand-coded rules, by physics simulations, or — increasingly — by generative AI models. The goal is to fill gaps where real data is scarce, expensive, or impossible to obtain.

### Four Use Cases for Synthetic Data

| Use Case | What Synthetic Data Generates | Real-World Benefit | Key Risk | Example in Practice |
|----------|------------------------------|-------------------|-----------|--------------------|
| **Instruction tuning** | Diverse (instruction, response) pairs covering many task types at scale | Scale fine-tuning to produce capable assistant models without expensive human labeling for each example | The model learns the generator model's biases, errors, and blindspots; mode collapse reduces diversity over iterations | Stanford Alpaca (2023) — 52,000 examples from GPT-3.5 at a cost of ~$500 |
| **Adversarial robustness** | Edge-case prompts and scenarios the model would rarely encounter in normal operation | Better robustness to unusual inputs, jailbreak attempts, and distribution shift | Synthetic adversarial examples may not cover the specific adversarial strategies real attackers actually use | Red-teaming augmentation in model safety pipelines |
| **Privacy preservation** | Statistically similar fake records that replace real patient, user, or financial records | Share sensitive datasets safely in research collaborations without exposing individual records | Residual privacy leakage if the synthetic distribution closely mirrors specific real records | Synthetic patient record generation for medical AI research |
| **Simulation environments** | Agent training scenarios such as customer service dialogues, code review sessions, or tool-use chains | Scale agent training to millions of scenarios without real user interactions or risks | Sim-to-real gap: the agent learns behaviors that work in clean simulation but fail on the messy variation in real deployments | OpenAI Codex training included synthetic verified code problems |

### Critical Thinking Questions

**Question 1.** Consider this thought experiment: you use an AI model (generation 1) to generate synthetic training data. You train a new model (generation 2) on that data. You use generation 2 to generate more synthetic data. You train generation 3. Can you repeat this indefinitely and keep improving, or does something eventually go wrong?

[[___ Your answer here ___]]

> *Hint:* Think about what information is preserved and what is lost at each step. The generation-1 model's outputs capture the common, high-probability patterns in its training data well, but rare patterns — unusual phrasing, low-frequency facts, edge cases — appear only occasionally in its outputs. When generation 2 trains on generation 1's outputs, it sees fewer examples of those rare patterns. Generation 3 sees even fewer. Each generation drifts toward the most common, central outputs and loses the tails of the distribution. Is this a problem? It depends on what the rare patterns represent — if they are noise, losing them is fine; if they are linguistically or factually important edge cases, losing them is harmful.

---

**Question 2.** Shumailov et al. (2023) describe "model collapse" — a phenomenon observed when models are trained on AI-generated data across multiple generations. What specific property of real-world data distributions do they argue is progressively lost? Why does this matter for the quality of a model trained many generations deep in a synthetic pipeline?

[[___ Your answer here ___]]

> *Hint:* The property being lost is the **tails of the distribution** — the rare, unusual, low-frequency patterns. Real human language and real-world scenarios include enormous diversity: people with unusual accents, unusual names, unusual situations, unusual combinations of facts. A model trained on real data sees this diversity. A model trained on synthetic data generated by another model sees only what that model generates frequently. After several generations, the model becomes a caricature: it handles the common cases well but is brittle on anything unusual. For an agent deployed in the real world, "unusual" is exactly what you need to handle — because it is often the unusual cases that matter most (rare medical conditions, unusual legal situations, edge-case security scenarios).

---

**Question 3.** Name one domain where using synthetic data for AI training is clearly acceptable with low risk and high benefit. Name one domain where it is clearly problematic with high risk of harm from distribution mismatch or bias amplification. Justify both choices with specific reasoning.

[[___ Your answer here ___]]

> *Hint:* Clearly acceptable: generating synthetic examples for a game-playing agent where the simulation is the real environment and there is no real-world deployment risk — the agent will only ever operate in the game world. Clearly problematic: generating synthetic medical training data for a diagnostic AI where the synthetic data reflects the biases and gaps of the generator model, and those biases map onto real patient harm. The key distinction is: how severe are the consequences of distribution mismatch? In a game, the worst case is the agent loses. In medicine, the worst case is a misdiagnosis.

---

## Model 2: Generating Synthetic Instruction Data

The most widely used form of synthetic data for LLM fine-tuning is **instruction-following data**: pairs of (instruction, response) that teach a model to respond helpfully to natural language requests rather than simply predicting the next token in a document.

### Self-Instruct (Wang et al., 2022)

Self-Instruct is the pipeline behind several influential open-source instruction-tuned models. It works as a bootstrapping loop:

1. Start with a **seed set** of roughly 175 human-written instruction examples covering a range of task types.
2. Prompt a large model (originally GPT-3) to generate new instructions by analogy with randomly sampled examples from the seed set: "Here are 8 example instructions. Generate 4 more that are different in task type and topic."
3. For each new instruction, prompt the same model to generate a high-quality response.
4. Apply **quality filters**: remove exact duplicates, near-duplicates (by cosine similarity), toxic content, and low-quality or incoherent responses.
5. Add the surviving instances to the growing dataset.
6. Return to step 2, now sampling from the full (and growing) dataset rather than just the original seeds.

Stanford's **Alpaca** model (2023) applied this pipeline: it used GPT-3.5 to generate 52,000 instruction-response pairs from 175 human-written seeds, at a cost of approximately $500 in API fees. The resulting model was competitive with early GPT-3.5 on many tasks despite being 10× smaller — a remarkable demonstration of the efficiency of synthetic instruction tuning.

### Evol-Instruct (WizardLM, Xu et al., 2023)

Evol-Instruct takes a different approach: rather than generating new instructions from scratch, it **evolves** existing simple instructions into progressively harder ones through iterative rewriting. Each evolution step applies one of several transformations:

- **Add constraints:** "Write a function that sorts a list" → "Write a function that sorts a list without using any built-in sorting functions or the sorted() built-in, in O(n log n) time."
- **Deepen complexity:** "Explain photosynthesis" → "Explain photosynthesis at the biochemical level, addressing specifically whether recent research on quantum coherence in light-harvesting complexes changes the classical explanation."
- **Require multi-step reasoning:** Single-step questions become chains of reasoning with explicit intermediate conclusions required.

The result is a dataset with a natural difficulty gradient, which is particularly valuable for training models to handle challenging queries rather than just easy ones.

### Quality Filtering Pipeline

```
seed_instructions
    → generate_variants(LLM)
    → filter_quality(judge_LLM_or_rules)
    → deduplicate(exact + semantic_similarity)
    → measure_diversity(embedding_spread)
    → add_to_dataset
    → loop
```

**Quality filter criteria — each generated pair must pass all of these:**

- **Length check:** The response is not trivially short (one word) or obviously padded with filler content.
- **Coherence check:** The response actually addresses the instruction rather than drifting to an unrelated topic.
- **Non-duplication check:** Cosine similarity to existing dataset items is below a threshold (typically 0.7–0.8) so the dataset remains diverse.
- **Safety check:** The instruction and response do not contain toxic, harmful, or inappropriate content.

> ⚠️ **Common Misconception:** Generating more synthetic data is not the same as generating *better* synthetic data. A common error is to generate enormous quantities of synthetic instruction data and assume that more is always better. In practice, quality filters are more important than quantity: a dataset of 10,000 high-quality, diverse, well-filtered examples typically produces better fine-tuning results than 100,000 low-quality or highly redundant examples. The Alpaca model demonstrated this: 52,000 carefully generated examples from a seed of 175 produced a capable model. Simply running the generation loop for 10 more hours to produce 500,000 examples would not have produced a model 10× better — and might have introduced more mode collapse.

### Critical Thinking Questions

**Question 4.** If you use GPT-4 to generate synthetic instruction-tuning data and then fine-tune a smaller model on that data, you are arguably distilling GPT-4's knowledge and reasoning patterns into the smaller model. But are you also distilling GPT-4's biases, factual errors, and blindspots? How would you detect whether this happened?

[[___ Your answer here ___]]

> *Hint:* GPT-4 has documented biases: it may handle certain demographic groups differently in certain contexts, may have gaps in knowledge of non-English languages and non-Western culture, and may generate factually wrong information with high confidence in low-frequency topic areas. If your fine-tuning data was generated entirely by GPT-4 and your fine-tuned model shows the same systematic patterns of error or bias that GPT-4 shows — making the same factual mistakes, having the same gaps — that is strong evidence of bias distillation. How would you specifically test for this? What reference dataset of known-correct, diverse, and culturally representative examples would you compare against?

---

**Question 5.** How would you measure whether your synthetic instruction dataset is sufficiently diverse to train a well-rounded model? Describe at least two concrete metrics you could compute before starting fine-tuning, and explain what threshold or warning sign would lead you to generate more data or adjust your generation pipeline.

[[___ Your answer here ___]]

> *Hint:* (1) **Embedding-space coverage**: embed all instructions using a sentence embedding model; compute the average pairwise cosine distance. Low average distance (instructions cluster tightly) means low diversity — the generation pipeline is producing variations on the same few themes. A diverse dataset should show a spread of embedding clusters covering many task types. (2) **Task-type distribution**: categorize each instruction by task type (question answering, summarization, code generation, translation, classification, etc.) and measure the entropy of the distribution. A dataset dominated by one or two task types will produce a model that is strong on those types and weak on others. What fraction of your target capability surface should each task type cover?

---

**Question 6.** Generating more synthetic data is cheap once the pipeline is set up — API costs are relatively low and generation can run in parallel. At what point do you get diminishing returns from adding more synthetic examples to a training set? What factors determine that threshold?

[[___ Your answer here ___]]

> *Hint:* Diminishing returns set in when: (1) the new synthetic examples are not adding new patterns — they are high-similarity duplicates of existing examples, adding no new information to the model; (2) the quality of new examples decreases as the generation loop continues (later generations of the self-instruct loop tend to produce lower-quality examples because the model starts generating less natural instructions); (3) the model has already saturated the capability that the synthetic data is targeting — additional examples of the same task type produce no measurable improvement on that task. The threshold depends on the target capability's complexity: simple tasks saturate quickly (the model can summarize after a few thousand examples); complex multi-step reasoning tasks may benefit from hundreds of thousands of diverse examples.

---

### Multiple Choice Question

A research team trains a model entirely on AI-generated text. They then use that model to generate more training data for the next model version and repeat this process 10 times. The most likely outcome, based on current research, is:

[[ ]] Each generation produces a progressively better model because the pipeline iteratively refines and improves the quality of the synthetic data
[[ ]] The models converge to a stable, consistent quality level after a few generations and then stop changing
[[x]] Model quality degrades over generations as rare but important patterns in the real-world data distribution are progressively lost from the synthetic outputs — a phenomenon called model collapse
[[ ]] The model learns to generate infinitely creative and diverse output as it samples more broadly from its own expanding distribution

> **Why this answer?** Shumailov et al. (2023) demonstrated model collapse empirically: when models are trained on outputs of previous models, the tails of the distribution — rare but important patterns — are systematically underrepresented in the training data of each subsequent generation. The model becomes progressively more "average," handling common cases well but becoming brittle and unreliable on unusual inputs. This is why real-world data anchoring is critical: mixing some proportion of real human-generated data into each generation's training set significantly slows or prevents collapse.

---

## Model 3: Synthetic Data for Agent Training

Instruction-response pairs are the simplest form of synthetic data for LLMs, but agents require something more complex: **trajectories** — sequences of observations, decisions, tool calls, and outcomes that represent a complete task-solving episode.

### Synthetic Trajectories

An agent trajectory is a sequence of tuples: `(observation₁, action₁, result₁, observation₂, action₂, result₂, ...)` continuing until the task is complete or abandoned.

Generating synthetic trajectories allows agent training to scale beyond what human demonstration collection alone can support:

- **Verified code problems:** Generate a programming problem, generate a candidate solution, execute the solution in a sandboxed environment, and use pass/fail against test cases as ground-truth labels. OpenAI's Codex training pipeline included synthetic problems with verified solutions generated this way — at a scale impossible to achieve with human demonstrators.
- **Customer service dialogues:** Generate a synthetic customer persona, a synthetic initial complaint or question, and a range of synthetic agent responses. Have a judge model rate each response on helpfulness and policy compliance. This provides training signal without accessing real user data that might contain PII.
- **Tool-use chains:** Generate tasks that require specific sequences of tool calls (look up a weather forecast, then look up a transit schedule, then combine them to recommend departure time), execute those chains in a sandboxed environment, and label complete trajectories by whether the task was accomplished correctly.

### Synthetic Evaluation Sets: The "LLM Generates Its Own Exam" Pattern

A practical technique for rapidly building evaluation benchmarks for new domains:

1. Prompt a capable model: "Generate 20 challenging questions about [domain] that require [specific capability]. For each question, also provide the correct answer."
2. Filter the generated pairs for quality, accuracy, and non-duplication.
3. Use the resulting pairs as a benchmark to evaluate a fine-tuned model on that domain.

**Critical pitfall — self-evaluation inflation:** A model performs systematically better on questions it generated than on questions generated by humans or by a different model. The model "knows" the style and framing of its own questions and can answer them more easily. This inflates apparent capability on the synthetic benchmark compared to real-world performance. Always validate a synthetic evaluation set against a sample of real human-written questions in the same domain before relying on it for deployment decisions.

### Critical Thinking Questions

**Question 7.** If you fine-tune a model on synthetic data, then use that fine-tuned model to generate more synthetic data for the next training round, and repeat — how do you prevent the model from progressively reinforcing its own errors? Describe at least one specific structural safeguard you would build into the pipeline.

[[___ Your answer here ___]]

> *Hint:* The core danger is error amplification: if the fine-tuned model has a systematic error (always recommending the wrong medication dose, always getting a specific logic pattern wrong), it will generate synthetic data that reflects that error, and the next model will learn the error even more strongly. Structural safeguards include: (1) **Real data anchoring** — always include a fixed proportion of human-verified real data in each training round, so the model cannot drift arbitrarily far from reality; (2) **Verification gating** — for domains where outputs can be automatically checked (code that runs, math answers that can be verified, logical proofs that can be checked), only include synthetic examples in the next training round if the output passes an automatic correctness check; (3) **Diversity filtering** — use embedding-based deduplication at each round to prevent the pipeline from collapsing to a narrow mode.

---

**Question 8.** What is the difference between **synthetic** data and **augmented** data? Give a concrete example of each in the context of a text-classification task for classifying customer support tickets by urgency. Does the distinction matter for how you evaluate the resulting model?

[[___ Your answer here ___]]

> *Hint:* **Augmented data** is derived from real data through transformations that preserve the label: taking a real support ticket classified as "urgent" and paraphrasing it, translating it, or adding typos. The result is a new example that is artificial, but it is grounded in a real human-written ticket with a verified label. **Synthetic data** is generated from scratch without reference to any specific real example: prompting a model to "write an example urgent customer support ticket about a missed delivery." The distinction matters for evaluation because: if you evaluate on augmented data, you are testing whether the model generalizes to variations of real examples; if you evaluate on synthetic data, you are testing whether the model handles the generator's idea of what an urgent ticket looks like — which may not match real urgent tickets.

---

**Question 9.** Design a quality filter for synthetic instruction data. Specify exactly three criteria that every generated (instruction, response) pair must satisfy before it is added to the training set. For each criterion, explain how you would test it automatically and what failure rate you would tolerate before revising the generation pipeline.

[[___ Your answer here ___]]

> *Hint:* Criterion 1: **Relevance** — the response must address the instruction rather than drift to an unrelated topic. Test automatically by checking whether the top 3 most important noun phrases from the instruction appear in the response (simple heuristic) or by embedding both instruction and response and checking cosine similarity (more robust). Tolerate at most 5% failure rate before revisiting the generation prompt. Criterion 2: **Minimum length** — the response must be at least 50 characters and at most 2,000 characters for the task types in your dataset. Test by character count. Tolerate at most 10% failure rate (responses that are too short are often low-quality; responses that are too long may be padded). Criterion 3: **Non-toxicity** — the instruction and response must not contain harmful, discriminatory, or violating content. Test using a toxicity classifier. Tolerate 0% failure rate; any toxic generation indicates a problem with the generation prompt that must be fixed immediately.

---

## Exercises

**Exercise 1.**

*What to do:* Using a local model or API access, generate 20 synthetic instruction-tuning examples for a domain of your choice (options: cooking, Python debugging, academic writing, local Ursinus College history, or anything else that interests you). Apply at least 2 quality filters from the pipeline described in Model 2.

*Starter hint:* Use this generation prompt structure: "You are generating instruction-tuning data for a language model assistant. Generate 5 (instruction, response) pairs for the domain of [your domain]. Each instruction should be a specific, realistic task a user might ask. Each response should be accurate, helpful, and 2–4 sentences long. Format your output as a JSON array." Run this prompt 4 times to get 20 candidates. Then apply your filters: (1) remove any response shorter than 50 words; (2) remove any pair where the response does not mention any key term from the instruction.

*You've succeeded when:* You know how many of your 20 generated examples passed both filters, you have read the examples that failed and identified the most common failure mode, and you have written a one-paragraph reflection on what the failure pattern tells you about the limitations of this generation approach.

---

**Exercise 2.**

*What to do:* Research the original Stanford Alpaca dataset (2023). Investigate its generation, its known problems, and how successor datasets addressed those problems.

*Starter hint:* Start with the Alpaca GitHub repository and the Stanford CRFM blog post about the project. Then search for "Alpaca limitations" or "instruction tuning quality critique 2023." Look specifically for: (1) What specific quality issues were found in the Alpaca dataset after release (factual errors, low diversity in certain task types, specific language bias)? (2) How did Alpaca-GPT4 — which used GPT-4 as the generator instead of GPT-3.5 — address those issues? (3) How did the OpenHermes dataset go further, and what tradeoffs did it introduce?

*You've succeeded when:* Your response answers all three questions with specific details (not vague generalities), cites at least three sources, and concludes with your own assessment: given what you now know about Alpaca's limitations, would you use it as the sole fine-tuning dataset for a production application? Why or why not?

---

**Exercise 3.**

*What to do:* Choose a specialized agent you care about — in healthcare, legal assistance, scientific research, or education — and design a synthetic data generation pipeline for training or fine-tuning that agent.

*Starter hint:* For a healthcare agent that helps patients prepare questions for doctor appointments, your pipeline might look like: (1) generate synthetic patient profiles (age range, chronic conditions from a controlled list, medication list from drug databases) — this avoids using real patient data; (2) generate synthetic "preparing for appointment" instruction-response pairs where the instruction is a patient's concern and the response is the kind of question they should ask their doctor; (3) verify each response against a clinical terminology check (does it use accurate medical language?); (4) filter for empathetic tone using a sentiment classifier. What are the three biggest risks in this specific pipeline?

*You've succeeded when:* Your pipeline design specifies: (a) the type of synthetic data to generate with a concrete example; (b) the generation pipeline in pseudocode or a labeled diagram; (c) your quality filtering approach with at least 2 specific filters; and (d) the 3 biggest risks and your mitigation strategy for each.

---

## Reflection Prompt

**Personal:** Think about content you have created — social media posts, papers, code, artwork. If that content was scraped and used to generate synthetic training data for an AI model, which in turn trained another model, and so on for 10 generations — what of your original "voice" or style would remain after 10 iterations? Does that matter to you, and why or why not?

**Technical:** Using AI to generate training data for AI creates a feedback loop. The first generation is trained on human-created data. The second is trained partly on AI-generated data. The tenth generation may be trained almost entirely on AI-generated data. At what point does "synthetic" become indistinguishable from "real"? If a synthetic dataset is statistically identical to a real one on every measurable dimension, does the distinction still matter? What might be lost in the unmeasured dimensions — and who would notice?

**Societal:** High-quality labeled data has historically been expensive, which meant that only well-resourced labs and companies could train capable AI systems. Synthetic data generation is cheap, which could democratize AI training. But synthetic data pipelines also require access to capable generator models (which are themselves owned by a small number of companies) and significant compute. Does synthetic data democratize AI, or does it just shift the barrier from "who can label data" to "who can afford API access to generate data"? What would genuinely democratized AI training require?

Write at least 200 words addressing at least two of the three levels above. Your Reflector should be prepared to share your group's key idea during class discussion.

[[___ Your reflection here ___]]

---

→ Coming Up Next: In the next activity, we examine what it means for AI to be "creative" — and whether creativity requires something that generative models fundamentally cannot have.

## Further Reading

- Wang, Y. et al. "Self-Instruct: Aligning Language Models with Self-Generated Instructions." ACL 2023. The foundational paper for synthetic instruction generation pipelines; describes the seed set, generation loop, and quality filters in detail.

- Shumailov, I. et al. "The Curse of Recursion: Training on Generated Data Makes Models Forget." arXiv:2305.17493 (2023). Introduces and formalizes the model collapse phenomenon with empirical demonstrations across multiple model architectures.

- Taori, R. et al. "Alpaca: A Strong, Replicable Instruction-Following Model." Stanford CRFM Blog (2023). Describes the Alpaca pipeline and its known limitations; a good starting point for critiquing self-instruct quality.

- Xu, C. et al. "WizardLM: Empowering Large Language Models to Follow Complex Instructions." arXiv:2304.12244 (2023). The Evol-Instruct paper; describes the instruction evolution methodology in detail and provides ablation studies.
