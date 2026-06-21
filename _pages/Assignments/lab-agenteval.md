---
layout: assignment
permalink: /Assignments/AgentEval
title: "CS357: Foundations of Artificial Intelligence - Lab: Building an Agent Evaluation Harness"

info:
  coursenum: CS357
  points: 100
  goals:
    - To design a structured evaluation dataset with golden, stylistic, and adversarial question categories that expose distinct failure modes in an agent
    - To implement multiple automated evaluation metrics including exact match, G-Eval LLM-as-judge scoring, and semantic similarity
    - To identify regressions and improvements by running a controlled before-and-after comparison on a well-defined eval set
    - To integrate the evaluation harness into a CI/CD pipeline that enforces a minimum pass rate on every code push
  rubric:
    - weight: 25
      description: Eval Dataset
      preemerging: Fewer than 10 questions are provided, or no distinction is made between question categories
      beginning: A 20-question dataset is present but the categories are not documented, or the adversarial prompts do not meaningfully test the agent's safety or refusal behavior
      progressing: All three categories are present with documented criteria, but golden answers are not verifiable by an automated metric, or adversarial prompts all target the same failure mode
      proficient: A 20-question dataset covers all three categories with documented selection criteria; golden answers are checkable by at least one automated metric; adversarial prompts cover at least two distinct failure modes such as jailbreak and out-of-scope
    - weight: 25
      description: Evaluation Metrics
      preemerging: Fewer than two metrics are implemented, or the evaluation script fails to run
      beginning: Two or more metrics are implemented but are not aggregated into a per-question pass/fail decision, or the judge prompt for G-Eval is not included
      progressing: Three or more metrics are implemented and a results table is produced, but the judge prompt is poorly calibrated or the refusal rate metric is not computed
      proficient: At least three metrics including G-Eval with a documented judge prompt are implemented; a results table with question, expected, actual, score, and pass/fail columns is produced; and refusal rate on adversarial prompts is reported separately
    - weight: 25
      description: Regression Suite
      preemerging: No before-and-after comparison is performed, or only one configuration is evaluated
      beginning: A before-and-after comparison is run but the change made to the agent is not documented, or the diff table is missing delta values
      progressing: A controlled change is documented and a diff table is provided, but no regression or no improvement is identified, or the identification is not supported by the scores
      proficient: A single documented agent change is tested; a diff table with score_before, score_after, and delta is provided for all 20 questions; at least one regression and one improvement are identified and interpreted in the writeup
    - weight: 25
      description: CI Integration
      preemerging: No CI workflow file is provided
      beginning: A CI workflow file is provided but does not actually run the evaluation harness, or the pass rate threshold is hardcoded in a way that always passes
      progressing: The workflow runs the evaluation harness on push and fails the build when pass rate drops below 80%, but the PR summary comment step is absent or non-functional
      proficient: A valid GitHub Actions YAML file runs the evaluation harness on push to main, fails the build if pass rate drops below 80%, and posts a formatted score-table comment to the PR using the GitHub Actions API or a marketplace action
  readings:
    - rtitle: "Testing Agents Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-testingagents.md"
    - rtitle: "LLM as Judge Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmasjudge.md"

tags:
  - evaluation
  - testing
  - ci

---

How do you know when your agent got better? How do you know when a change broke it? This lab answers both questions by building an evaluation harness from scratch: a dataset, a set of metrics, a regression runner, and a CI gate that enforces quality on every push. You will work individually.

## Part 1: Design the Eval Dataset

Choose **one agent** from earlier in the course: your course assistant agent, your RAG knowledge base agent, your coding agent, or your MCP-connected agent. You will evaluate this specific agent throughout the lab, so choose one you can still run locally.

Create a **20-question eval dataset** stored as a JSON file with the schema below. The dataset must contain exactly three categories:

```json
[
  {
    "id": "golden_01",
    "category": "golden",
    "question": "...",
    "expected_answer": "...",
    "check_method": "exact_match | f1 | semantic_similarity",
    "notes": "..."
  }
]
```

**Golden questions (10):** Questions whose correct answers are objectively verifiable and stable, for example factual questions whose answers appear in a document your RAG agent indexes, or coding tasks with a deterministic correct output. For each question, record the expected answer and the check method you will use in Part 2. You must be able to point to a ground-truth source for each.

**Style questions (5):** Questions where correctness is inherently subjective: appropriate tone, target length, citation format, or helpfulness to a specific persona. For each, write the criterion you will use to evaluate it (for example, "response must be fewer than 150 words and include at least one concrete example").

**Adversarial questions (5):** Prompts your agent should refuse, hedge, or redirect rather than answer directly. Cover at least two distinct failure modes: for example, a prompt that asks the agent to ignore its instructions, a question that is entirely outside its documented scope, and a prompt that contains a subtle factual falsehood that the agent should correct rather than accept. For each, document the expected behavior.

Write a one-paragraph rationale for each category explaining how you selected the questions and what failure mode each category is designed to surface.

## Part 2: Implement Evaluation Metrics

Implement a Python evaluation script (`evaluate.py`) that runs all 20 questions through your agent and computes at least **three of the following metrics**. You must include G-Eval as one of your three:

**Exact match / Token F1:** Compare the agent's response to the expected answer using string normalization (lowercase, strip punctuation). Report both exact match accuracy and token-level F1 across the golden question set. Use the SQuAD F1 formula.

**G-Eval rubric scoring (required):** Call an LLM-as-judge with a rubric prompt you write. The judge must score each response on three dimensions: correctness (1–5), helpfulness (1–5), and safety (1–5), where safety penalizes responses that comply with adversarial prompts that should be refused. Include the full judge prompt in your writeup and explain why you chose each dimension and scale.

**Semantic similarity:** Embed both the expected and actual answers using `sentence-transformers` (model `all-MiniLM-L6-v2` or similar) and compute cosine similarity. Report mean cosine similarity across golden questions, with a threshold of 0.80 for pass.

**Refusal rate:** For adversarial prompts, define a binary classifier: did the agent refuse or significantly hedge? You may use simple keyword detection ("I cannot", "I'm not able to", "that is outside my scope") or a lightweight LLM-as-judge call. Report refusal rate as a percentage of adversarial questions.

Produce a **results table** as a CSV and print it to stdout with the columns: `id`, `category`, `question_truncated`, `expected_truncated`, `actual_truncated`, `g_eval_score`, `semantic_sim`, `exact_match`, `pass`. A question passes if it meets the threshold for all applicable metrics.

## Part 3: Regression Suite

Make **one documented change** to your agent. Acceptable changes include: rewriting the system prompt to change its persona or scope, switching to a different model, adding or removing a tool, or changing the retrieval k parameter. Document the change in your writeup in one sentence.

Re-run `evaluate.py` against both the original agent and the modified agent. Produce a **regression diff table** with columns: `id`, `score_before`, `score_after`, `delta`, `verdict` (where verdict is `improved`, `regressed`, or `unchanged` based on delta sign and magnitude). A delta is meaningful if its absolute value exceeds 0.1 for continuous scores or changes the pass/fail verdict.

In your writeup, identify and discuss:
- At least **one regression**: a question where the modified agent scored worse. Why did this happen? Is it an acceptable trade-off for the change you made?
- At least **one improvement**: a question where the modified agent scored better. Is this improvement likely to generalize or is it specific to this question?

## Part 4: CI Integration

Write a **GitHub Actions workflow** (`.github/workflows/eval.yml`) that does the following on every push to `main` and on every pull request targeting `main`:

1. Checks out the repository, sets up Python, and installs dependencies from `requirements.txt`.
2. Runs `python evaluate.py` and captures the output, including a final line formatted as `PASS_RATE=0.NN`.
3. Fails the workflow with exit code 1 if `PASS_RATE` is below `0.80`.
4. Posts a comment to the pull request (using `actions/github-script` or `peter-evans/create-or-update-comment`) that includes the full score table as a Markdown table.

Your workflow file must be syntactically valid YAML. If you do not have a GitHub repository to test against, include the YAML file and a written description of how you verified it would work (for example, using `act` to run Actions locally, or manual inspection against the GitHub Actions schema).

## Deliverables

Submit a ZIP file containing:

- `eval_dataset.json` (20-question dataset)
- `evaluate.py` (evaluation script)
- `results_before.csv` and `results_after.csv` (Part 2 and Part 3 tables)
- `regression_diff.csv` (Part 3 diff table)
- `.github/workflows/eval.yml`
- `writeup.md` with: dataset rationale, judge prompt, metric threshold justifications, regression discussion, and reflection answers

## Reflection Prompts

- Your LLM judge is itself a model that can be wrong. How would you validate that your judge is calibrated, meaning that a score of 3 actually means something consistent across questions and runs? Describe at least one concrete calibration check you could perform.
- What percentage of your adversarial prompts were successfully refused by your agent? Does that percentage surprise you? What does it reveal about the gap between your agent's intended behavior and its actual behavior?
- Approximately how many hours did this lab take (I will not judge you for this; I use it to calibrate assignment difficulty)?
