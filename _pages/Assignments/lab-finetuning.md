---
layout: assignment
permalink: /Assignments/FineTuning
title: "CS357: Foundations of Artificial Intelligence - Lab: Hands-On Fine-Tuning with LoRA and QLoRA"

info:
  coursenum: CS357
  points: 100
  goals:
    - To apply parameter-efficient fine-tuning (LoRA/QLoRA) to a local model using a real dataset
    - To instrument training with loss curves and evaluate output quality before and after fine-tuning
    - To understand the trade-offs between fine-tuning, RAG, and prompting for knowledge injection
    - To document a fine-tuned model with a model card and identify potential bias shifts
  rubric:
    - weight: 30
      description: Fine-Tuning Pipeline
      preemerging: Training does not run or produces nonsense output at every step
      beginning: Training runs but no evaluation is performed and the output quality is unknown
      progressing: Training runs with a loss curve and qualitative comparison of before/after outputs on at least 5 prompts
      proficient: Training runs with loss curve, quantitative evaluation (perplexity or task-specific metric), before/after comparison table, and at least one hyperparameter choice is justified with evidence
    - weight: 25
      description: Dataset and Preprocessing
      preemerging: No dataset or a random dataset with no domain relevance
      beginning: A dataset is used but formatting or tokenization errors are present
      progressing: A domain-relevant dataset is formatted correctly for instruction tuning with train/validation split
      proficient: The dataset is described with source, size, format, and any cleaning applied; a validation set is used to catch overfitting; at least one dataset limitation is identified
    - weight: 25
      description: Evaluation and Comparison
      preemerging: No comparison to baseline
      beginning: One or two anecdotal output comparisons with no systematic approach
      progressing: Five or more prompts compared systematically with base vs. fine-tuned side by side
      proficient: Systematic evaluation with a defined metric (perplexity, task accuracy, LLM-as-judge), at least one regression (something the fine-tuned model does worse), and a recommendation for whether fine-tuning was worth it vs. the alternatives
    - weight: 20
      description: Model Card and Reflection
      preemerging: No model card
      beginning: Model card present but fewer than 4 sections
      progressing: Model card with at least 6 sections following the Mitchell framework
      proficient: Complete model card with all required sections, bias risk section identifies at least one bias shift introduced or amplified by fine-tuning, and reflection answers are substantive
  readings:
    - rtitle: "Fine-Tuning vs. RAG"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-finetuningvsrag.md"
    - rtitle: "Running Local Models"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-localmodels.md"
    - rtitle: "Data Cards and Model Cards"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-datacards.md"

tags:
  - fine-tuning
  - lora
  - local-models
  - evaluation

---

## Overview

This lab walks you from a baseline local model to a domain-adapted fine-tuned model using LoRA (Low-Rank Adaptation), which adds a tiny number of trainable parameters while keeping the base model frozen. You will use a real domain-specific dataset, instrument training with loss tracking, evaluate output quality, and document the result with a model card.

**This lab requires GPU access.** Use your own hardware (if you have a compatible GPU), Google Colab (free tier with a T4 GPU is sufficient for a 7B model with QLoRA), or a provisioned cloud instance. Time budget: expect 2–3 hours of active work, with training running in the background.

## Setup: Environment and Tools

Install the required libraries (or use the provided Colab notebook skeleton):

```bash
pip install transformers peft datasets bitsandbytes accelerate trl
```

Recommended base models (choose one based on your hardware):

- `microsoft/phi-3-mini-4k-instruct` (3.8B, fastest, fits on free Colab)
- `meta-llama/Meta-Llama-3-8B-Instruct` (8B, requires HuggingFace token)
- `mistralai/Mistral-7B-Instruct-v0.3` (7B, good quality)

## Part 1: Choose a Domain Dataset (30%)

Choose one of the following datasets for domain adaptation, or propose your own (get approval first):

- **Medical Q&A**: `medalpaca/medical_meadow_medical_flashcards` — medical question/answer pairs
- **Code generation**: `iamtarun/python_code_instructions_18k_alpaca` — Python instruction tuning
- **Legal reasoning**: `nguha/legalbench` (a subset) — legal analysis
- **Science questions**: `sciq` — science exam questions with explanations
- **Your domain**: any HuggingFace dataset with instruction/response format

**Deliverable:** Write the dataset section of your model card. Include: source, number of examples, format (instruction/input/output or chat turns), train/validation split you used, and one known limitation.

## Part 2: Fine-Tune with LoRA / QLoRA (30%)

Use `peft` + `trl`'s `SFTTrainer` for instruction fine-tuning. The key LoRA hyperparameters to set:

- `r` (rank): start with 8 or 16
- `lora_alpha`: typically 2× rank
- `target_modules`: usually `["q_proj", "v_proj"]` for LLaMA-family models
- `lora_dropout`: 0.05–0.1

For QLoRA (if VRAM-constrained), add 4-bit quantization via `BitsAndBytesConfig`.

**Deliverable:** Your training script (Python file or Colab notebook) plus a loss curve (plot of training loss vs. steps). Annotate the curve: does loss converge? Is there overfitting (training loss continues falling but validation loss rises)? Choose at least one hyperparameter deliberately (justify your choice of `r`, epochs, or learning rate).

## Part 3: Evaluate Before and After (25%)

Run both the base model and your fine-tuned model on at least **10 test prompts** (prompts NOT seen during training). For each prompt, record:

| Prompt | Base Model Output | Fine-Tuned Output | Improvement? (Y/N) | Notes |
|--------|-------------------|-------------------|-------------------|-------|
| ... | ... | ... | ... | ... |

Additionally, compute at least **one quantitative metric**:

- **Perplexity** on a held-out test set (lower = better)
- **Task accuracy** (for MCQ datasets: % correct)
- **LLM-as-judge** score (1–5 on relevance and accuracy, using a judge model)

Report: did fine-tuning help? Where did it hurt? Find at least one regression — a prompt where the base model was better. This is normal and important to document.

## Part 4: Model Card and Reflection (15%)

Write a model card using the Mitchell et al. framework with these required sections: Model Details, Intended Use (and explicitly Out-of-Scope Use), Factors, Metrics (what you measured), Training Data (reference Part 1), Quantitative Analyses (Part 3 table), Ethical Considerations (at least one bias risk specific to your chosen domain), Caveats.

## Deliverables

Submit a ZIP containing:

- Training script or Colab notebook (`.ipynb`)
- Loss curve image
- Before/after evaluation table (CSV or markdown)
- Quantitative metric result
- Model card (markdown)
- Reflection answers

## Reflection Prompts

- You spent hours fine-tuning a model on 1,000 examples. A colleague says "just put those examples in the system prompt instead." Evaluate that suggestion: when would they be right, and when would fine-tuning be worth the effort?
- Your fine-tuned model may now perform better in your domain but worse on general questions. Who is responsible for communicating that trade-off to users?
- How many hours did this lab take?
