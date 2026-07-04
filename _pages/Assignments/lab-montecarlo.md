---
layout: assignment
permalink: /Assignments/MonteCarlo
title: "CS357: Foundations of Artificial Intelligence - Lab: Multimodal AI and Monte Carlo Simulation"

info:
  coursenum: CS357
  points: 100
  goals:
    - To implement a Monte Carlo retirement simulation that draws annual returns from a configurable normal distribution and records portfolio paths across 1,000 simulations
    - To generate a labeled two-panel visualization showing simulated paths with median and percentile bands, and a histogram of final balances
    - To construct a multimodal API request that encodes a PNG image as a base64 string, packages it in the correct Ollama JSON payload, and parses the structured text response
    - To conduct a two-turn conversation with a multimodal model using a structured prompt that specifies role, required response sections, and audience assumptions
    - To compare AI-generated quantitative claims against ground-truth statistics and identify specific numerical errors with verbatim AI excerpts
    - To evaluate the sensitivity of simulation outcomes to parameter changes and explain the compounding effect of return mean and volatility on the outcome distribution
    - To propose a user-facing guardrail that limits over-reliance on AI numerical claims in financial contexts
  rubric:
    - weight: 30
      description: Simulation and Visualization
      preemerging: Simulation does not run or produces no output
      beginning: Simulation runs but visualization is missing axis labels, title, or key statistics
      progressing: Simulation runs with correct statistical distributions, visualization is labeled, median and percentile bands are shown
      proficient: Simulation is configurable via a JSON config file; visualization includes median, 10th and 90th percentile bands, final balance distribution histogram, and a text summary of key statistics saved alongside the image; edge cases (retirement before 65, negative balance mid-career) are handled
    - weight: 25
      description: Multimodal AI Integration
      preemerging: No AI integration attempted
      beginning: Image sent to AI but the request uses an incorrect endpoint or payload structure (e.g., base64 string missing from the images array, or /api/chat used instead of /api/generate)
      progressing: Image correctly base64-encoded and sent in the images array to /api/generate with a prompt; response parsed from the response field; no follow-up turn
      proficient: JSON payload includes model, prompt, stream (False), and images fields with a valid base64-encoded PNG string; response is parsed from response.json()["response"]; Turn 1 prompt specifies role, four required numbered sections, and assumed audience; Turn 2 follow-up presses the model on a specific quantitative claim from Turn 1; both turns are saved to model_responses.txt
    - weight: 25
      description: Comparative Analysis
      preemerging: No comparison between AI and human interpretation
      beginning: AI interpretation summarized without comparison to the student's own reading or the statistics file
      progressing: One difference between AI and human interpretation identified, with either the AI excerpt or the ground-truth statistic cited but not both
      proficient: Three specific differences identified between AI and human reading of the chart; at least one difference shows the AI giving a wrong or imprecise number, supported by an exact verbatim AI excerpt from model_responses.txt alongside the true value from simulation_stats.txt; student implements one prompt engineering change (e.g., hedging instruction or step-by-step visual reasoning request), re-runs Part 2, and records whether the AI's response improved or not
    - weight: 20
      description: Writeup and Reflection
      preemerging: No writeup
      beginning: Writeup describes what was done without interpreting what the numbers or charts mean
      progressing: Writeup reports sensitivity analysis numbers for at least 2 scenarios and notes at least one AI interpretation error
      proficient: Writeup includes (1) the four statistics (median, P10, P90, P(>$1M)) for all three sensitivity scenarios in a table, with an explicit comparison of which parameter change — raising mean return or lowering volatility — had a larger effect on the median; (2) evaluation of AI interpretation quality with at least one verbatim AI excerpt and a judgment of correct, approximately correct, or wrong; (3) a 2–3 sentence user-facing guardrail statement that names the specific risk (AI cannot reliably read precise numbers from charts) without using technical jargon
  readings:
    - rtitle: "Sampling, Temperature, and Generation Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-samplinggeneration.md"
    - rtitle: "Evaluating Agent Outputs Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md"
    - rtitle: "Multimodal Agents Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multimodalagents.md"

tags:
  - multimodal
  - simulation
  - visualization
  - evaluation
---

Multimodal AI can read images. This lab gives it something worth reading: a Monte Carlo retirement simulation that you generate. You will discover that AI image analysis is impressively capable at pattern recognition but surprisingly fragile on numerical precision — and that the difference matters enormously when the output might influence someone's financial decisions.

This lab is completed in **pairs using driver/navigator roles**: the driver types while the navigator reviews, questions, and consults documentation, and you must **swap roles at least every 30 minutes**, keeping a brief log of swap times and who held each role.

---

## Before You Start

**Why Monte Carlo?** A spreadsheet gives you one future. Monte Carlo simulation gives you a thousand. Instead of projecting a single "expected" outcome, we draw thousands of possible annual returns from a statistical distribution, let each one play out over a 40-year career, and look at the spread of endings. That spread — not the center — is what matters when you are making a decision whose consequences will compound for decades. This is why financial planners use simulation rather than a single formula, and it is why the visualization you generate will be more informative than any average.

**Prerequisite concepts** — make sure you have completed these activities before writing any code:

- [Sampling, Temperature, and Generation Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-samplinggeneration.md) — stochastic sampling and output distributions
- [Evaluating Agent Outputs Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md) — how to critically assess AI-generated content
- [Multimodal Agents Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multimodalagents.md) — sending images to local vision models

**Tools to install:**

```bash
pip install numpy matplotlib requests
```

**Verify your multimodal model is available:**

```bash
ollama pull llava
ollama list
```

Expected output:

```
NAME               ID              SIZE    MODIFIED
llava:latest       8dd30f6b0cb1    4.7 GB  2 minutes ago
```

If `llava` is not available on your machine, any of the following will work: `moondream`, `bakllava`, `llava-phi3`. Update the `"model"` key in your config file to match whichever you pull.

**Verify the API responds:**

```bash
curl http://localhost:11434/api/tags
```

Expected output (abbreviated):

```json
{"models":[{"name":"llava:latest", ...}]}
```

**Estimated time budget:**

| Part | Task | Estimated time |
|------|------|----------------|
| Part 1 | Simulation Engine | 50–70 min |
| Part 2 | Multimodal Integration | 40–60 min |
| Part 3 | Parameter Sensitivity | 25–35 min |
| Part 4 | Critical Analysis | 20–30 min |
| Writeup | Readme and reflection | 30–45 min |

---

## Part 1: The Simulation Engine

You will write a Python script that simulates 1,000 possible futures for a person who starts saving at age 25 and retires at 65. Each simulated year draws a random annual return from a normal distribution, applies it to the portfolio, and records the resulting balance. The output is a two-panel chart saved to disk.

### Step 1: Create your configuration file.

Create `config.json` in your project root. Externalizing parameters here means you can run Part 3's sensitivity analysis by editing one file rather than hunting through your code.

```json
{
  "starting_age": 25,
  "retirement_age": 65,
  "life_expectancy": 90,
  "starting_savings": 10000,
  "monthly_contribution": 500,
  "annual_return_mean": 0.07,
  "annual_return_std": 0.12,
  "inflation_rate": 0.025,
  "num_simulations": 1000,
  "model": "llava",
  "ollama_url": "http://localhost:11434"
}
```

### Step 2: Write the simulation function.

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import base64
import io
import requests
import json
import traceback


def load_config(path="config.json"):
    """Load simulation and model parameters from a JSON config file."""
    with open(path) as f:
        return json.load(f)


def simulate_retirement(cfg):
    """
    Run a Monte Carlo retirement simulation.

    Draws annual returns from N(annual_return_mean, annual_return_std) for each
    simulated year of a career, applying monthly contributions each year.

    Returns:
        np.ndarray of shape (num_simulations, years_to_retirement), where each
        row is one simulated portfolio path and each column is the end-of-year balance.
    """
    years = cfg["retirement_age"] - cfg["starting_age"]
    results = np.zeros((cfg["num_simulations"], years))

    for sim in range(cfg["num_simulations"]):
        balance = cfg["starting_savings"]
        for year in range(years):
            # TODO: Add annual contribution (monthly_contribution * 12)
            balance += cfg["monthly_contribution"] * 12

            # TODO: Draw a random annual return from a normal distribution
            #       using annual_return_mean and annual_return_std.
            #       Hint: np.random.normal(mean, std)
            annual_return = np.random.normal(
                cfg["annual_return_mean"], cfg["annual_return_std"]
            )

            # TODO: Apply the return to the balance.
            balance *= (1 + annual_return)

            # TODO: Clip balance at 0 — a portfolio cannot go negative.
            balance = max(balance, 0)

            results[sim, year] = balance

    return results
```

### Step 3: Write the visualization function.

```python
def plot_simulation(balances, cfg):
    """
    Create a labeled two-panel visualization of simulation results.

    Left panel: all simulated portfolio paths (light gray) plus median (blue)
    and 10th/90th percentile bands (red dashed).

    Right panel: histogram of final balances at retirement, with vertical
    lines at the median and at $1 million.

    Saves the figure to retirement_simulation.png and also returns a
    base64-encoded PNG string for sending to the multimodal model.

    Returns:
        str: base64-encoded PNG image.
    """
    ages = list(range(cfg["starting_age"] + 1, cfg["retirement_age"] + 1))
    median_path = np.median(balances, axis=0)
    p10_path = np.percentile(balances, 10, axis=0)
    p90_path = np.percentile(balances, 90, axis=0)
    final_balances = balances[:, -1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- Left panel: portfolio paths ---
    # TODO: Plot each simulated path in light gray with alpha=0.05
    for path in balances:
        ax1.plot(ages, path, color="gray", alpha=0.05, linewidth=0.5)

    # TODO: Plot median in solid blue, labeled "Median"
    ax1.plot(ages, median_path, color="blue", linewidth=2, label="Median")

    # TODO: Plot 10th percentile in red dashed, labeled "10th / 90th percentile"
    ax1.plot(ages, p10_path, color="red", linewidth=1.5, linestyle="--",
             label="10th / 90th percentile")

    # TODO: Plot 90th percentile in red dashed (same label so it shares the legend entry)
    ax1.plot(ages, p90_path, color="red", linewidth=1.5, linestyle="--")

    # TODO: Label x-axis ("Age"), y-axis ("Portfolio Balance"), add title and legend
    ax1.set_xlabel("Age", fontsize=12)
    ax1.set_ylabel("Portfolio Balance", fontsize=12)
    ax1.set_title(
        f"Monte Carlo Retirement Simulation\n"
        f"{cfg['num_simulations']:,} paths | "
        f"${cfg['monthly_contribution']:,}/mo contribution | "
        f"Mean return {cfg['annual_return_mean']:.0%}",
        fontsize=11
    )
    ax1.legend(fontsize=10)

    # TODO: Format the y-axis as currency using mticker.FuncFormatter
    ax1.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
    )

    # --- Right panel: final balance histogram ---
    # TODO: Plot a histogram of final_balances with 50 bins
    ax2.hist(final_balances, bins=50, color="steelblue", edgecolor="white", alpha=0.8)

    # TODO: Add a vertical line at the median final balance (blue, solid)
    ax2.axvline(np.median(final_balances), color="blue", linewidth=2,
                label=f"Median: ${np.median(final_balances):,.0f}")

    # TODO: Add a vertical line at $1,000,000 (green, dashed)
    ax2.axvline(1_000_000, color="green", linewidth=1.5, linestyle="--",
                label="$1 Million milestone")

    ax2.set_xlabel("Final Balance at Retirement", fontsize=12)
    ax2.set_ylabel("Number of Simulations", fontsize=12)
    ax2.set_title("Distribution of Final Balances at Age 65", fontsize=11)
    ax2.legend(fontsize=10)
    ax2.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M")
    )

    plt.tight_layout()
    plt.savefig("retirement_simulation.png", dpi=150, bbox_inches="tight")
    print("Saved: retirement_simulation.png")

    # Encode as base64 for the multimodal model API
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
```

### Step 4: Add a statistics summary.

```python
def save_statistics(balances, cfg, path="simulation_stats.txt"):
    """
    Compute and save key statistics from the simulation to a text file.
    """
    final = balances[:, -1]
    prob_million = (final >= 1_000_000).mean()

    lines = [
        f"Simulation parameters:",
        f"  Monthly contribution: ${cfg['monthly_contribution']:,}",
        f"  Mean annual return:   {cfg['annual_return_mean']:.1%}",
        f"  Return std dev:       {cfg['annual_return_std']:.1%}",
        f"  Number of paths:      {cfg['num_simulations']:,}",
        f"",
        f"Final balance at retirement (age {cfg['retirement_age']}):",
        f"  10th percentile: ${np.percentile(final, 10):>12,.0f}",
        f"  Median (50th):   ${np.median(final):>12,.0f}",
        f"  90th percentile: ${np.percentile(final, 90):>12,.0f}",
        f"  Mean:            ${final.mean():>12,.0f}",
        f"",
        f"Probability of reaching $1 million: {prob_million:.1%}",
    ]

    text = "\n".join(lines)
    print(text)
    with open(path, "w") as f:
        f.write(text)
    print(f"Saved: {path}")
    return text
```

### Step 5: Wire Part 1 together and run a smoke test.

```python
if __name__ == "__main__":
    cfg = load_config()
    np.random.seed(42)

    print("Running simulation...")
    balances = simulate_retirement(cfg)

    print("Generating visualization...")
    image_b64 = plot_simulation(balances, cfg)

    print("Computing statistics...")
    stats_text = save_statistics(balances, cfg)
```

**Expected output when Part 1 is complete:**

```
Running simulation...
Generating visualization...
Saved: retirement_simulation.png
Computing statistics...
Simulation parameters:
  Monthly contribution: $500
  Mean annual return:   7.0%
  Return std dev:       12.0%
  Number of paths:      1,000

Final balance at retirement (age 65):
  10th percentile: $      341,208
  Median (50th):   $    1,042,577
  90th percentile: $    2,847,031
  Mean:            $    1,298,451

Probability of reaching $1 million: 53.2%
Saved: simulation_stats.txt
```

Your exact numbers will vary by random seed. The two-panel PNG should show: (left) a fan of gray paths narrowing to a few wide-spread outcomes at age 65, with a visible median line and two outer dashed bands; (right) a right-skewed histogram of final balances with a vertical median line and a $1M milestone line.

### Troubleshooting — Part 1

**`ValueError: could not broadcast input array from shape...` in `simulate_retirement`**
Check that `results` is indexed as `results[sim, year]` and that `year` runs from `0` to `years - 1`. Off-by-one errors here cause shape mismatches.

**Chart y-axis shows scientific notation instead of dollar amounts**
The `FuncFormatter` must be assigned *after* `ax1` is populated. If you call it before plotting, matplotlib may overwrite it. Move the formatter call to just before `plt.tight_layout()`.

**Simulation runs but all paths converge to zero**
The balance clip at zero combined with a very negative return draw can zero out a portfolio early. Check that you are adding the contribution *before* applying the return, and that `annual_return_std` is not set unreasonably high in your config.

---

> **Checkpoint: Before moving to Part 2, make sure you can answer:**
> 1. What does the width of the fan (the gap between the 10th and 90th percentile lines) represent in plain English? How would you expect it to change if you doubled `num_simulations`?
> 2. Why does the histogram in the right panel skew right rather than form a symmetric bell curve?
> 3. If `starting_savings` were $0, what would change in the simulation? In the chart? Test it.

---

## Part 2: Connecting to a Multimodal Model

You will send the PNG you just generated to a local multimodal model via the Ollama API and conduct a two-turn conversation about the chart.

### Step 1: Write the API call function.

```python
def ask_multimodal_model(image_b64, question, cfg):
    """
    Send an image and a text question to a local multimodal model via Ollama.

    Args:
        image_b64: base64-encoded PNG string (from plot_simulation).
        question:  text prompt to accompany the image.
        cfg:       config dict containing 'model' and 'ollama_url'.

    Returns:
        str: the model's text response, or an error message.
    """
    payload = {
        "model": cfg["model"],
        "prompt": question,
        "images": [image_b64],
        "stream": False,
    }
    try:
        url = cfg["ollama_url"] + "/api/generate"
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        print(f"[montecarlo:ask_multimodal_model] {e}")
        traceback.print_exc()
        raise
```

### Step 2: Write the two-turn conversation.

The first turn sends a structured prompt that tells the model its role, what to look at, how to format its response, and what audience to assume. The second turn presses it on a specific quantitative claim.

```python
def run_analysis_conversation(image_b64, cfg):
    """
    Conduct a two-turn conversation with the multimodal model about the chart.

    Turn 1: structured analysis with four required sections.
    Turn 2: follow-up pressing the model to estimate a specific probability.

    Returns:
        tuple: (response_turn1: str, response_turn2: str)
    """
    initial_prompt = (
        "You are a financial educator analyzing a Monte Carlo retirement simulation "
        "chart for a college student audience with no prior finance background.\n\n"
        "The chart has two panels:\n"
        "- Left panel: 1,000 simulated portfolio paths from age 25 to 65, with a "
        "solid blue median line and two red dashed lines showing the 10th and 90th "
        "percentile bounds.\n"
        "- Right panel: a histogram of final portfolio balances at age 65, with a "
        "vertical blue line at the median and a vertical green dashed line at $1 million.\n\n"
        "Please analyze the chart and respond in exactly four numbered sections:\n"
        "1. What the spread of paths (the gap between the dashed red lines) tells us "
        "about retirement savings risk.\n"
        "2. Your estimate of what percentage of simulations ended above $1 million, "
        "based on the histogram.\n"
        "3. One specific, actionable insight for a 25-year-old starting their career.\n"
        "4. One limitation of this simulation that a tool deployer should disclose to users."
    )

    print("=== Turn 1: Initial Analysis ===")
    response1 = ask_multimodal_model(image_b64, initial_prompt, cfg)
    print(response1)

    # TODO: Formulate a follow-up question that presses the model on a specific
    # quantitative claim from its Turn 1 response.
    # The suggested follow-up below asks it to show its reasoning for the percentage
    # estimate — this is where numerical precision often breaks down.
    followup = (
        "Based specifically on the histogram in the right panel, walk me through your "
        "reasoning for the percentage estimate you gave in section 2. What visual "
        "features of the histogram did you use, and how confident are you in that number?"
    )

    print("\n=== Turn 2: Follow-Up ===")
    response2 = ask_multimodal_model(image_b64, followup, cfg)
    print(response2)

    # Save both turns to a file for your writeup
    with open("model_responses.txt", "w") as f:
        f.write("=== Turn 1 ===\n")
        f.write(response1 + "\n\n")
        f.write("=== Turn 2 ===\n")
        f.write(response2 + "\n")
    print("\nSaved: model_responses.txt")

    return response1, response2
```

### Step 3: Add Part 2 to your main block.

Extend the `if __name__ == "__main__":` block from Part 1:

```python
    print("\nRunning multimodal analysis...")
    response1, response2 = run_analysis_conversation(image_b64, cfg)
```

**Example of a good AI response (Turn 1):** The model might correctly observe that the fan widens dramatically after age 40, that the histogram is right-skewed indicating many paths cluster below the median, and offer a concrete suggestion like "increasing monthly contributions by even $100 reduces your worst-case (10th percentile) outcome significantly." These are pattern-level observations that vision models handle well.

**Example of a flawed AI response (Turn 1, section 2):** A model might state: *"Based on the histogram, approximately 68% of simulations reached $1 million by retirement."* If your statistics file shows the true probability is 53%, this is a fabricated number — the model estimated from visual impression rather than counting. This is the kind of specific, confident numerical claim that looks authoritative but is wrong, and is exactly what Part 4 asks you to analyze.

### Troubleshooting — Part 2

**`KeyError: 'response'` from the API call**
The `/api/generate` endpoint returns `{"response": "..."}` for non-chat completions. The `/api/chat` endpoint returns `{"message": {"content": "..."}}`. Make sure you are using `/api/generate` in `ask_multimodal_model`, not `/api/chat`.

**Model returns an empty string or very short response**
Add `"Describe the image in detail before analyzing it."` as the first sentence of your prompt. Some vision models require an explicit grounding instruction before they will engage with the analytical questions.

**Image is too large and the request times out**
Add a resize step before encoding: `fig.savefig(buf, ...)` then `from PIL import Image; img = Image.open(buf); img = img.resize((800, 600)); ...` and re-encode. Alternatively, lower the `dpi` parameter in `fig.savefig` to `100`.

**`ollama pull llava` fails or the model is not recognized**
Try `ollama pull moondream` (smaller, faster) or `ollama pull bakllava`. Update `"model"` in `config.json` to match.

---

> **Checkpoint: Before moving to Part 3, make sure you can answer:**
> 1. What specific percentage did the model report for simulations reaching $1 million? What does your statistics file say the true value is? Are they the same?
> 2. In Turn 2, did the model's confidence in its estimate increase, decrease, or stay the same? What does this tell you about using follow-up questioning as a verification strategy?
> 3. Look at the model's response to section 4 (simulation limitations). Did it identify any limitation that you had not already considered?

---

## Part 3: Parameter Sensitivity

Run your simulation under three configurations and record the results. Edit `config.json` between runs, or write a loop that overrides specific keys programmatically.

| Configuration | `annual_return_mean` | `annual_return_std` | Label |
|---------------|----------------------|----------------------|-------|
| Pessimistic | 0.04 | 0.15 | Poor market, high volatility |
| Baseline | 0.07 | 0.12 | Historical average (default) |
| Optimistic | 0.10 | 0.08 | Strong market, lower volatility |

For each configuration, record in your writeup:

- Median final balance
- Probability of reaching $1 million
- 10th percentile (worst-case) balance
- 90th percentile (best-case) balance

Then answer: which parameter change had a larger effect on the median — raising the mean return from 0.07 to 0.10, or lowering the standard deviation from 0.12 to 0.08? Use numbers from your runs, not intuition.

**To automate the three runs:**

```python
def run_sensitivity_analysis(base_cfg):
    """Run the simulation under three parameter configurations and print a comparison table."""
    scenarios = [
        {"label": "Pessimistic",  "annual_return_mean": 0.04, "annual_return_std": 0.15},
        {"label": "Baseline",     "annual_return_mean": 0.07, "annual_return_std": 0.12},
        {"label": "Optimistic",   "annual_return_mean": 0.10, "annual_return_std": 0.08},
    ]

    print(f"\n{'Scenario':<14} {'Median':>14} {'P(>$1M)':>10} {'10th pct':>14} {'90th pct':>14}")
    print("-" * 70)

    for scenario in scenarios:
        cfg = {**base_cfg, **scenario}
        np.random.seed(42)
        balances = simulate_retirement(cfg)
        final = balances[:, -1]
        print(
            f"{scenario['label']:<14} "
            f"${np.median(final):>13,.0f} "
            f"{(final >= 1_000_000).mean():>9.1%} "
            f"${np.percentile(final, 10):>13,.0f} "
            f"${np.percentile(final, 90):>13,.0f}"
        )
```

**Expected output (your numbers will vary slightly):**

```
Scenario       Median   P(>$1M)       10th pct       90th pct
----------------------------------------------------------------------
Pessimistic    $  314,042       4.2%   $   73,501   $  877,209
Baseline       $1,042,577      53.2%   $  341,208   $2,847,031
Optimistic     $2,891,044      89.7%   $1,201,330   $5,912,448
```

---

> **Checkpoint: Before moving to Part 4, make sure you can answer:**
> 1. Between the pessimistic and baseline scenarios, the median more than tripled. What does this tell you about the compounding effect of even a moderate improvement in average returns over 40 years?
> 2. The pessimistic scenario has a higher `annual_return_std` than the baseline. How does higher volatility affect the 10th percentile differently than the median? Why?
> 3. If a user only saw the optimistic chart and made contribution decisions based on it, what harm could result?

---

## Part 4: Critical Analysis

This is the most important part of the lab. In Parts 1–3 you built a tool. Now you evaluate what happens when AI interprets that tool's output.

### Step 1: Read the chart yourself first.

Before re-reading the model's responses, look at your baseline chart and note:

- Approximately what percentage of paths appear to end above $1 million (your best visual estimate)
- Where roughly the median falls
- Whether the 10th percentile line ever reaches zero during the accumulation years
- Whether the histogram distribution is symmetric, right-skewed, or left-skewed

Write down your estimates. Do not change them after reading the model's responses.

### Step 2: Compare to the model's Turn 1 response.

Identify **three specific differences** between what you read from the chart and what the model reported. For each difference, record:

- The exact AI output excerpt (copy-paste from `model_responses.txt`)
- Whether the AI was correct, approximately correct, or wrong
- Your best explanation for why the discrepancy occurred

At least one of your three differences must be a case where the model was **wrong or imprecise** about a number, not just phrased something differently.

### Step 3: Propose a prompt engineering improvement.

For the one numerical error you identified, propose a single change to the `initial_prompt` in `run_analysis_conversation` that would have reduced the chance of that error. Implement it, re-run Part 2, and record whether the response improved.

Useful strategies to try:
- Adding an explicit disclaimer: *"If you cannot read a precise number from the chart, say 'approximately' and give a range."*
- Asking the model to reason step by step before stating a number: *"Before giving a percentage, describe what you see in the histogram bin by bin."*
- Restricting the scope: *"Only comment on what is visually unambiguous. Flag anything that requires precise numerical reading as uncertain."*

### Step 4: Address the deployment question.

Write a 2–3 sentence **guardrail statement** you would add to a financial planning tool that uses this AI chart interpretation feature. The statement should appear to the user before they see the AI's analysis, and should protect against over-reliance on numerical claims that the AI cannot read precisely.

---

> **Checkpoint: You have succeeded at this lab when:**
> - Your simulation produces a labeled two-panel PNG and a statistics text file
> - The multimodal model provides a four-section analysis with at least one follow-up exchange
> - You have identified at least one specific numerical error in the AI's response with an exact AI output excerpt
> - You have proposed and tested a prompt engineering change
> - Your sensitivity analysis table covers all three configurations with four statistics each

---

## Reflection Prompts

Answer in your readme:

1. What does the spread of simulation paths tell you that a single projected number (like "you will have $800,000 at retirement") does not? Point to a specific visual feature of your chart that would disappear if you replaced the simulation with a single-path projection.
2. The AI reported a specific probability from the histogram. How would you verify whether it was right? What tools would you need, and what does this verification challenge tell you about using AI for quantitative analysis of charts?
3. If you were deploying this as a financial planning tool, what disclosure would you require the user to read before the AI's interpretation is displayed? Draft it in two sentences as if you were writing terms of service.
4. In Part 3, the pessimistic and optimistic scenarios produced dramatically different outcomes despite both using "reasonable" parameters. What does this imply about how a financial planning tool should present parameter uncertainty to a non-expert user?
5. If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
6. Approximately how many hours did this lab take?

---

## Submission Checklist

Submit a ZIP file containing all of the following. Items marked with a checkbox must be present for the submission to be graded.

- [ ] `montecarlo.py` — complete simulation, visualization, and multimodal analysis code
- [ ] `config.json` — your baseline configuration file
- [ ] `retirement_simulation.png` — the two-panel chart from your baseline run
- [ ] `simulation_stats.txt` — the statistics summary from your baseline run
- [ ] `model_responses.txt` — both turns of the AI conversation from your baseline run
- [ ] `sensitivity_results.txt` or equivalent — the three-scenario comparison table
- [ ] `readme.md` — writeup covering: (1) sensitivity analysis with all three scenarios and four statistics each, (2) critical analysis with three AI/human comparison items including at least one AI error with verbatim excerpt, (3) the prompt engineering change you tested and whether it helped, (4) your guardrail statement for deployment
- [ ] `pair_log.txt` — driver/navigator swap log with timestamps and roles
- [ ] Reflection prompts answered in the readme
