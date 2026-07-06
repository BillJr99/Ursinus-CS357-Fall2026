---
layout: assignment
permalink: /Assignments/FineTuning
title: "CS357: Foundations of Artificial Intelligence - Lab: Hands-On Fine-Tuning with LoRA and QLoRA"

info:
  coursenum: CS357
  purpose: "To adapt a model you run to a specific domain with LoRA, and to decide from evidence whether fine-tuning was worth it against RAG and prompting."
  tilt:
    task: "Fine-tune a local model with LoRA or QLoRA on a domain dataset, instrument the loss curve, evaluate against the baseline, and write a model card."
    criteria: "Assessed on the fine-tuning pipeline, the dataset preparation, and a systematic before-and-after evaluation; see the rubric below for the full breakdown."
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

This lab walks you from a baseline local model to a domain-adapted fine-tuned model using **LoRA** (Low-Rank Adaptation — a technique that adds a tiny number of trainable parameters to a frozen base model, making fine-tuning feasible on consumer hardware). You will use a real domain-specific dataset, instrument training with loss tracking, evaluate output quality, and document the result with a model card.

**This lab requires GPU access.** Use your own hardware (if you have a compatible GPU), Google Colab (free tier with a T4 GPU is sufficient for a 7B model with QLoRA), or a provisioned cloud instance. Time budget: expect 2–3 hours of active work, with training running in the background.

## Before You Start

### Prerequisite Checklist

- [ ] GPU access confirmed: your own GPU, Google Colab free tier (T4), or a cloud VM
- [ ] Python 3.10 or later (`python --version`)
- [ ] If using a Llama model: HuggingFace account and accepted model license at `meta-llama/Meta-Llama-3-8B-Instruct`
- [ ] HuggingFace CLI installed and logged in (if downloading gated models)

### Environment Setup

**If using Google Colab:** Create a new notebook and run this setup cell first:

```python
# Cell 1: Google Colab Setup
# Run this cell first. Runtime > Change runtime type > T4 GPU

import subprocess
import sys

# Install required packages
packages = [
    "transformers>=4.40.0",
    "peft>=0.10.0",
    "datasets>=2.18.0",
    "bitsandbytes>=0.43.0",
    "accelerate>=0.29.0",
    "trl>=0.8.0",
]
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + packages)

# Verify GPU is available
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB" if torch.cuda.is_available() else "")
print("Setup complete!")
```

Expected output:
```
CUDA available: True
GPU: Tesla T4
VRAM: 15.8 GB
Setup complete!
```

**If using local hardware:** Run in your terminal:

```bash
pip install transformers peft datasets bitsandbytes accelerate trl
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"
```

### Quick Sanity Check — Confirm Model Downloads Work

```python
# Run this before starting Part 1 to confirm your HuggingFace access
from transformers import AutoTokenizer

# Use a small, freely available model for the sanity check
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-3-mini-4k-instruct", trust_remote_code=True)
tokens = tokenizer("Hello, world!")
print(f"Tokenizer OK. Token IDs: {tokens['input_ids']}")
```

Expected output:
```
Tokenizer OK. Token IDs: [1, 15043, 29892, 3186, 29991]
```

If you see `OSError: Can't load tokenizer`, check your internet connection and that you are logged into HuggingFace (`huggingface-cli login`).

**Recommended base models (choose one based on your hardware):**

| Model | Size | Min VRAM | Notes |
|-------|------|----------|-------|
| `microsoft/phi-3-mini-4k-instruct` | 3.8B | 6 GB | Best for free Colab T4 |
| `meta-llama/Meta-Llama-3-8B-Instruct` | 8B | 8 GB with QLoRA | Requires HuggingFace token |
| `mistralai/Mistral-7B-Instruct-v0.3` | 7B | 8 GB with QLoRA | Good quality, open weights |

---

## Part 1: Choose a Domain Dataset

**Why this matters:** The dataset you choose determines everything — what your model learns, what biases it might amplify, and how you can measure success. Choosing a well-structured dataset is the difference between training that converges and training that produces nonsense.

### Steps

1. **Choose one of the following datasets,** or propose your own (get instructor approval first):

   | Dataset | HuggingFace ID | Domain | Format |
   |---------|----------------|--------|--------|
   | Medical Q&A | `medalpaca/medical_meadow_medical_flashcards` | Medical | instruction/output |
   | Python codegen | `iamtarun/python_code_instructions_18k_alpaca` | Code | instruction/input/output |
   | Legal reasoning | `nguha/legalbench` | Legal | varies by subset |
   | Science questions | `sciq` | Science | question/answer/support |

2. **Load and inspect your dataset:**

```python
# dataset_inspect.py
from datasets import load_dataset

# TODO: replace with your chosen dataset ID
DATASET_ID = "sciq"  # change this

dataset = load_dataset(DATASET_ID)
print(f"Dataset splits: {list(dataset.keys())}")
print(f"Train size: {len(dataset['train'])}")
print(f"\nFirst example:\n{dataset['train'][0]}")
```

Expected output (for `sciq`):
```
Dataset splits: ['train', 'validation', 'test']
Train size: 11679

First example:
{'question': 'What type of force keeps planets in orbit?', 
 'distractor3': 'electromagnetic', 'distractor1': 'nuclear', 
 'distractor2': 'friction', 'correct_answer': 'gravitational',
 'support': 'Gravitational force keeps planets in orbit around the Sun.'}
```

3. **Format the dataset for instruction tuning.** Models trained with SFTTrainer expect a single string per example in a consistent instruction format. Here is a starter formatter — adapt it for your dataset's field names:

```python
# dataset_format.py
from datasets import load_dataset

# TODO: replace with your dataset ID
DATASET_ID = "sciq"

dataset = load_dataset(DATASET_ID)

def format_example(example: dict) -> dict:
    """Convert a raw dataset row into an instruction-tuning string.
    TODO: adapt the field names below to match your chosen dataset."""
    # Example for sciq:
    instruction = example.get("question", "")
    # TODO: replace 'correct_answer' with the answer field in your dataset
    answer = example.get("correct_answer", example.get("output", ""))
    # TODO: include supporting context if available in your dataset
    context = example.get("support", "")

    if context:
        text = f"### Instruction:\n{instruction}\n\n### Context:\n{context}\n\n### Response:\n{answer}"
    else:
        text = f"### Instruction:\n{instruction}\n\n### Response:\n{answer}"

    return {"text": text}

# Apply formatting and create train/validation split
formatted = dataset["train"].map(format_example)

# TODO: adjust split sizes based on your dataset size
# Use 90% train, 10% validation if no validation split exists
if "validation" not in dataset:
    split = formatted.train_test_split(test_size=0.1, seed=42)
    train_data = split["train"]
    val_data = split["test"]
else:
    train_data = formatted
    val_data = dataset["validation"].map(format_example)

print(f"Train examples: {len(train_data)}")
print(f"Validation examples: {len(val_data)}")
print(f"\nFormatted example:\n{train_data[0]['text'][:300]}")
```

4. **Write the dataset section of your model card** (`model_card.md`). Include: source URL, number of examples, format (instruction/input/output or chat turns), your train/validation split sizes, and one known limitation of the dataset.

> **Checkpoint:** Before moving on, verify that your formatted dataset has a `text` field, that the formatted string contains `### Instruction:` and `### Response:` sections, and that you have a validation split with at least 100 examples.

> **Troubleshooting:** If `load_dataset` hangs, you may be behind a firewall that blocks HuggingFace CDN — try `load_dataset(..., cache_dir="/tmp/hf_cache")` or download the dataset manually. If the field names in `format_example` don't match your dataset, print `dataset['train'][0].keys()` to see what fields are available. If the formatted text is empty for some rows, those rows likely have `None` values — add `if not instruction or not answer: return None` and call `.filter(lambda x: x is not None)` after mapping.

---

## Part 2: Fine-Tune with LoRA / QLoRA

**Why this matters:** LoRA does not modify the original model weights at all — it learns two small matrices (called A and B, with rank `r`) that approximate the weight update. This means you can fine-tune a 7B model on a consumer GPU with 8–16 GB of VRAM. **QLoRA** adds 4-bit quantization on top, cutting VRAM usage roughly in half again.

### Steps

1. **Create your training script** (`train.py` or a Colab notebook cell). Fill in every `# TODO`:

```python
# train.py — LoRA/QLoRA fine-tuning with SFTTrainer
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer
from datasets import load_dataset

# ── Configuration ─────────────────────────────────────────────────────────────
# TODO: set to your chosen model
MODEL_ID = "microsoft/phi-3-mini-4k-instruct"
# TODO: set to your chosen dataset (or "local" if you saved it)
DATASET_ID = "sciq"
OUTPUT_DIR = "./lora-finetuned"

# LoRA hyperparameters — these are your starting point, justify your choices
LORA_R = 8           # rank: higher = more capacity, more VRAM. Try 8 or 16.
LORA_ALPHA = 16      # typically 2× rank
LORA_DROPOUT = 0.05  # regularization
# TODO: adjust target_modules for your model family
# Phi-3 / LLaMA family: ["q_proj", "v_proj"] or ["q_proj", "k_proj", "v_proj", "o_proj"]
TARGET_MODULES = ["q_proj", "v_proj"]

# ── 4-bit Quantization (QLoRA) — comment out if you have enough VRAM ─────────
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# ── Load model and tokenizer ──────────────────────────────────────────────────
print(f"Loading {MODEL_ID}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token  # required for batch training

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,  # remove this line if not using QLoRA
    device_map="auto",
    trust_remote_code=True,
)

# ── Apply LoRA adapters ───────────────────────────────────────────────────────
lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    target_modules=TARGET_MODULES,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ── Load and format dataset ───────────────────────────────────────────────────
# TODO: replace with your formatted dataset loading
# If you saved it locally: dataset = load_from_disk("./formatted_dataset")
dataset = load_dataset(DATASET_ID)

def format_example(example):
    # TODO: adapt field names to your dataset
    instruction = example.get("question", "")
    answer = example.get("correct_answer", example.get("output", ""))
    return {"text": f"### Instruction:\n{instruction}\n\n### Response:\n{answer}"}

train_data = dataset["train"].map(format_example)
val_data = dataset.get("validation", dataset["train"].select(range(500))).map(format_example)

# ── Training arguments ────────────────────────────────────────────────────────
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=1,          # TODO: increase to 2-3 if you have time/VRAM
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,          # TODO: justify your choice in the writeup
    fp16=True,
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=50,
    save_steps=100,
    warmup_ratio=0.03,
    report_to="none",            # change to "wandb" if you want W&B tracking
)

# ── Train ─────────────────────────────────────────────────────────────────────
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
    eval_dataset=val_data,
    dataset_text_field="text",
    max_seq_length=512,
)

print("Starting training...")
trainer.train()
trainer.save_model(OUTPUT_DIR)
print(f"Model saved to {OUTPUT_DIR}")
```

2. **Run training** and watch the loss output:

```bash
python train.py
```

Expected training output (your exact numbers will differ, but the pattern should show decreasing loss):
```
trainable params: 4,194,304 || all params: 3,825,160,192 || trainable%: 0.1097
Starting training...
{'loss': 2.3421, 'learning_rate': 0.0002, 'epoch': 0.01}
{'loss': 1.8834, 'learning_rate': 0.00019, 'epoch': 0.05}
{'loss': 1.5201, 'learning_rate': 0.00018, 'epoch': 0.10}
{'loss': 1.3012, 'learning_rate': 0.00015, 'epoch': 0.20}
{'loss': 1.1478, 'learning_rate': 0.00010, 'epoch': 0.40}
{'eval_loss': 1.2341, 'epoch': 0.40}
...
Model saved to ./lora-finetuned
```

A healthy training run shows loss decreasing from roughly 2.3 toward 1.1 over 200 steps. If loss is stuck above 2.0 or oscillates wildly, see troubleshooting below.

3. **Plot your loss curve.** After training, add this cell to your notebook or script:

```python
# plot_loss.py
import json
import matplotlib.pyplot as plt

# Load training logs (saved by Trainer in output_dir/trainer_state.json)
with open("./lora-finetuned/trainer_state.json") as f:
    state = json.load(f)

train_steps = [e["step"] for e in state["log_history"] if "loss" in e]
train_loss  = [e["loss"] for e in state["log_history"] if "loss" in e]
eval_steps  = [e["step"] for e in state["log_history"] if "eval_loss" in e]
eval_loss   = [e["eval_loss"] for e in state["log_history"] if "eval_loss" in e]

plt.figure(figsize=(10, 5))
plt.plot(train_steps, train_loss, label="Training loss", color="blue")
plt.plot(eval_steps, eval_loss, label="Validation loss", color="orange", linestyle="--")
plt.xlabel("Steps")
plt.ylabel("Loss")
plt.title("Training vs. Validation Loss")
plt.legend()
plt.grid(True)
plt.savefig("loss_curve.png", dpi=150)
plt.show()
print("Saved loss_curve.png")
```

4. **Annotate the curve** in your writeup: Does loss converge? Is there overfitting (training loss keeps falling but validation loss rises or plateaus)? Justify at least one hyperparameter choice (why you chose your value of `r`, number of epochs, or learning rate).

> **Checkpoint:** Before moving on, verify that `./lora-finetuned/` directory exists and contains adapter files, that `loss_curve.png` was saved, and that training loss decreased from the first logged step to the last.

> **Troubleshooting:** If you get `CUDA out of memory`, reduce `per_device_train_batch_size` to 2 or 1, and increase `gradient_accumulation_steps` to keep effective batch size the same. If loss is `nan` from step 1, your learning rate is too high — try `1e-4` or `5e-5`. If `target_modules` raises a `ValueError` saying the module does not exist, print `[name for name, _ in model.named_modules()]` to see the actual module names in your model. If training takes longer than 2 hours on Colab, reduce the dataset to 2000 examples with `train_data = train_data.select(range(2000))`.

---

## Part 3: Evaluate Before and After

**Why this matters:** Without systematic evaluation, fine-tuning is a black box — you spent hours training, but do you actually know if the model improved? This Part builds the habit of measuring before you ship.

### Steps

1. **Load both the base model and your fine-tuned model** for comparison:

```python
# evaluate_models.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# TODO: set to your model ID
MODEL_ID = "microsoft/phi-3-mini-4k-instruct"
LORA_PATH = "./lora-finetuned"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

def load_base_model():
    return AutoModelForCausalLM.from_pretrained(
        MODEL_ID, device_map="auto", trust_remote_code=True, torch_dtype=torch.float16
    )

def load_finetuned_model(base_model):
    return PeftModel.from_pretrained(base_model, LORA_PATH)

def generate(model, prompt: str, max_new_tokens: int = 200) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    # Return only the newly generated tokens, not the prompt
    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)
```

2. **Run 10 test prompts** (not seen during training) through both models:

```python
# Add to evaluate_models.py

# TODO: write 10 test prompts relevant to your chosen domain
# These must NOT be from the training set
TEST_PROMPTS = [
    "### Instruction:\nWhat is the primary mechanism of action of beta-blockers?\n\n### Response:",
    "### Instruction:\nExplain the difference between supervised and unsupervised learning.\n\n### Response:",
    # TODO: add 8 more prompts
]

import csv

base_model = load_base_model()
ft_model = load_finetuned_model(load_base_model())

rows = []
for i, prompt in enumerate(TEST_PROMPTS):
    print(f"Prompt {i+1}/{len(TEST_PROMPTS)}...")
    base_out = generate(base_model, prompt)
    ft_out = generate(ft_model, prompt)

    # TODO: manually rate each pair and fill in 'improvement' and 'notes'
    rows.append({
        "prompt": prompt[:80],
        "base_output": base_out[:200],
        "finetuned_output": ft_out[:200],
        "improvement": "?",  # fill in: Y / N / Partial
        "notes": ""
    })

with open("eval_comparison.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["prompt","base_output","finetuned_output","improvement","notes"])
    writer.writeheader()
    writer.writerows(rows)

print("Saved eval_comparison.csv — open it and fill in the improvement and notes columns.")
```

3. **Compute at least one quantitative metric.** Choose one:

   **Option A — Perplexity on held-out test set (lower is better):**

   ```python
   # perplexity.py
   import torch
   import math

   def compute_perplexity(model, tokenizer, texts: list[str], max_length: int = 512) -> float:
       model.eval()
       total_loss = 0
       total_tokens = 0
       for text in texts:
           inputs = tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True).to(model.device)
           with torch.no_grad():
               outputs = model(**inputs, labels=inputs["input_ids"])
           total_loss += outputs.loss.item() * inputs["input_ids"].shape[1]
           total_tokens += inputs["input_ids"].shape[1]
       return math.exp(total_loss / total_tokens)

   # TODO: load test texts from your dataset
   test_texts = ["### Instruction:\n...\n\n### Response:\n..."]  # replace with real test set

   base_ppl = compute_perplexity(base_model, tokenizer, test_texts)
   ft_ppl   = compute_perplexity(ft_model,   tokenizer, test_texts)
   print(f"Base model perplexity:        {base_ppl:.2f}")
   print(f"Fine-tuned model perplexity:  {ft_ppl:.2f}")
   print(f"Improvement: {((base_ppl - ft_ppl) / base_ppl * 100):.1f}%")
   ```

   Expected output (numbers will vary):
   ```
   Base model perplexity:        24.31
   Fine-tuned model perplexity:  11.87
   Improvement: 51.2%
   ```

   **Option B — Task accuracy (for MCQ datasets):**
   ```python
   # For sciq or similar: compare model's top predicted answer to correct_answer
   # TODO: implement for your dataset
   ```

   **Option C — LLM-as-judge score (1–5):**
   ```python
   # Use your evaluate.py judge from the AgentEval lab, or write a simple one here
   # TODO: call your judge on each of the 10 test prompts
   ```

4. **Document at least one regression** in your writeup — a prompt where the base model was better. This is expected and important to be honest about.

> **Checkpoint:** Before moving on, verify that `eval_comparison.csv` has 10 rows, that you have manually filled in the `improvement` column for each row, and that your quantitative metric (perplexity, accuracy, or judge score) has been computed for both base and fine-tuned models.

> **Troubleshooting:** If the fine-tuned model produces repetitive output (same phrase repeated over and over), add `repetition_penalty=1.2` to the `generate()` call. If both models produce identical output, the LoRA adapter may not have loaded correctly — check that `PeftModel.from_pretrained` is pointing to the correct directory and that `adapter_config.json` exists there. If perplexity of the fine-tuned model is higher than the base model, the model may have overfit — check your loss curve for a rising validation loss.

---

## Part 4: Model Card and Reflection

**Why this matters:** A model without documentation is a liability. The model card format (from Mitchell et al. 2019) is the industry standard for responsible AI deployment — every major model on HuggingFace uses it. Writing one forces you to articulate what your model does, what it does not do, and what could go wrong.

### Steps

1. **Create `model_card.md`** with all eight required sections. Use this template:

```markdown
# Model Card: [Your Model Name]

## Model Details
- **Base model:** [model ID]
- **Fine-tuning method:** LoRA (r=[your r], alpha=[your alpha], target_modules=[your modules])
- **Training dataset:** [dataset name and size]
- **Training duration:** [steps, epochs, wall-clock time]
- **Developer:** [your name]
- **Date:** [date]

## Intended Use
**Primary use case:** [what this model is for, e.g., "answering medical flashcard questions"]

**Out-of-scope use cases:**
- TODO: list at least 2 uses this model should NOT be used for
- Example: "Clinical diagnosis or treatment decisions"

## Factors
- **Relevant factors:** [language, domain, question type, etc.]
- **Evaluation factors:** [what variables you held constant and which you varied]

## Metrics
- **Evaluation metric(s):** [perplexity / accuracy / LLM-as-judge]
- **Threshold for acceptable performance:** [what number would you be happy with?]

## Training Data
[Reference Part 1. Include: source, size, format, train/val split, known limitations]

## Quantitative Analyses
[Reference Part 3 table. Include your before/after metric values.]

| Metric | Base Model | Fine-Tuned Model | Change |
|--------|-----------|------------------|--------|
| Perplexity | X | Y | -Z% |
| Qualitative improvement rate | X/10 | Y/10 | +N |

## Ethical Considerations
**Bias risks:**
- TODO: identify at least one bias that your chosen dataset might introduce or amplify
- Example: "The medical_meadow dataset skews toward Western clinical practice. The fine-tuned model may perform poorly on questions about traditional or non-Western medicine."

**Privacy risks:** [does the training data contain PII?]

## Caveats
- TODO: list at least 2 known limitations of your fine-tuned model
- Example: "Performance degrades on questions longer than 200 tokens"
```

2. **Answer the reflection prompts** in your writeup.

> **Checkpoint:** Before submitting, verify that `model_card.md` has all eight sections and that the Ethical Considerations section names a specific bias risk tied to your chosen dataset.

> **Troubleshooting:** If you are unsure what biases your dataset introduces, search for published papers or datasheets about your chosen dataset — most HuggingFace datasets have a "Dataset Card" tab that discusses known biases and limitations.

---

## Extension Challenges (optional)

These challenges push the lab from a working fine-tune to a research-grade experiment.

**Extension 1: LoRA rank ablation.** Train three versions of your model with `r=4`, `r=8`, and `r=16`. Plot all three loss curves on the same axes. Does increasing rank improve final loss? Does it improve perplexity on the test set? How does it affect VRAM usage? Report all three in a table.

**Extension 2: LoRA vs QLoRA memory comparison.** Train once with 4-bit quantization (QLoRA) and once without. Use `torch.cuda.max_memory_allocated()` after training to measure peak VRAM. How much memory did quantization save? Did it hurt final model quality?

**Extension 3: Few-shot prompting vs. fine-tuning.** Take 10 of your training examples and put them directly into the base model's context window as few-shot examples. Compare the few-shot base model's output quality to your fine-tuned model on the test set. When does fine-tuning win, and when does few-shot prompting match it with far less effort?

---

## Deliverables

Submit a ZIP containing:

- `train.py` or Colab notebook (`.ipynb`) — runnable training script
- `dataset_format.py` — dataset loading and formatting code
- `evaluate_models.py` — comparison script
- `loss_curve.png` — annotated training/validation loss plot
- `eval_comparison.csv` — before/after comparison table (10 rows)
- Quantitative metric results (printed output, screenshot, or CSV)
- `model_card.md` — complete model card with all 8 sections
- `writeup.md` — reflection answers and hyperparameter justifications

## Submission Checklist

- [ ] `train.py` (or `.ipynb`) runs without error and saves adapter files to `./lora-finetuned/`
- [ ] `loss_curve.png` shows both training and validation loss and is annotated
- [ ] Training loss visibly decreases (roughly 2.3 → 1.1 direction) over the run
- [ ] `eval_comparison.csv` has 10 rows with `improvement` column filled in manually
- [ ] At least one quantitative metric computed for both base and fine-tuned model
- [ ] At least one regression documented (a prompt where base model was better)
- [ ] `model_card.md` has all 8 sections (Model Details, Intended Use, Factors, Metrics, Training Data, Quantitative Analyses, Ethical Considerations, Caveats)
- [ ] Ethical Considerations section names a specific bias risk tied to the dataset
- [ ] At least one hyperparameter choice (r, learning rate, or epochs) justified with evidence
- [ ] Reflection prompts answered in `writeup.md`

## Reflection Prompts

- You spent hours fine-tuning a model on 1,000 examples. A colleague says "just put those examples in the system prompt instead." Evaluate that suggestion: when would they be right, and when would fine-tuning be worth the effort?
- Your fine-tuned model may now perform better in your domain but worse on general questions. Who is responsible for communicating that trade-off to users?
- How many hours did this lab take?
