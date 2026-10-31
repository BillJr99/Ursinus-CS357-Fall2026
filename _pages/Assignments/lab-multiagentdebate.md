---
layout: assignment
permalink: /Assignments/MultiAgentDebate
title: "CS357: Foundations of Artificial Intelligence - Lab: Multi-Agent Patterns"

info:
  coursenum: CS357
  purpose: "To practice the three multi-agent patterns your final project can draw on (critique and refine, debate, and consensus), so that you know how each one runs, what it costs in model calls, and whether it beats a single call on a task you care about."
  tilt:
    task: "For each pattern (critique and refine, debate, and consensus), run the provided code (or the provided presets and a spreadsheet), change one setting, and record what changed.  Then run the pattern once on a task of your own choosing beside a single model call, and write one sentence on whether it helped and what it cost."
    criteria: "I assess each pattern on its Practice run, its changed setting, and its Try It comparison, plus a readme that lets me rerun what you did.  The rubric below breaks it down in full."
  points: 100
  goals:
    - To run a critique-and-refine loop, a multi-agent debate, and a sample, cluster, and synthesize consensus pipeline, and read what each one does round by round
    - To change one setting in each pattern and say what changed in its output
    - To try each pattern once on a task of your own and decide whether it beat a single call for what it cost in model calls
  rubric:
    - weight: 30
      description: "Part A: Critique and Refine"
      preemerging: "No critique-and-refine run, or the critic's issues never reach the next draft."
      beginning: "The loop runs, but no setting was changed and recorded, or the Try It run is missing.  On the no-code path: the presets exist, but the critic's issues are not pasted back to the Reviser, or the rounds are not in the spreadsheet."
      progressing: "The Practice loop (with either critic) runs until it prints a stopping reason (accepted or budget exhausted), and a saved transcript of at least two rounds shows a draft changing in response to a critique.  One setting was changed, with a line on what changed.  The Try It task of your choosing was run once beside a single call.  On the no-code path: the same runs through the Generator, Critic, and Reviser presets, with one spreadsheet row per round."
      proficient: "As progressing, and the Try It sentence points at the two drafts and says whether the loop helped and what it cost in model calls (two per round, against one).  Every model call in your code, including any you added, is wrapped in an exception handler that prints a located message and a traceback.  On the no-code path, the same Try It sentence earns this row on equal terms, with every preset setting (base model, system prompt, temperature, seed) and the round budget you enforced recorded in the readme in place of the exception handlers."
    - weight: 25
      description: "Part B: Debate"
      preemerging: "No debate runs, or the program fails to run."
      beginning: "A debate runs, but the agents never see each other's previous answers, or no setting was changed and recorded, or the Try It run is missing.  On the no-code path: the chats answer once and are never shown each other's answers."
      progressing: "The Practice debate runs three agents for two rounds from config.json, reads each answer from its ANSWER: line, combines the final round by both majority vote and the judge agent, and saves the full transcript.  One debate setting was changed, with a line on what changed.  The Try It question of your choosing was run once beside a single call.  On the no-code path: three Debater chats, a rebuttal round, a majority vote taken by hand, and a Debate Judge chat, with every answer in the spreadsheet."
      proficient: "As progressing, and the Try It sentence says whether the debate helped and what it cost in model calls (agents times rounds, plus one for the judge, against one).  A missing ANSWER: line shows up as a located warning instead of a silent wrong answer.  Every model call in your code, including any you added, is wrapped in an exception handler that prints a located message and a traceback.  On the no-code path, the same Try It sentence earns this row on equal terms, with a missing ANSWER: line recorded as no answer in the spreadsheet and every preset setting recorded in the readme in place of the exception handlers."
    - weight: 25
      description: "Part C: Consensus"
      preemerging: "No consensus run, or the program fails to run."
      beginning: "Drafts are sampled, but clustering or synthesis is missing, or no setting was changed and recorded, or the Try It run is missing.  On the no-code path: the samples are collected but never grouped, or the synthesizer is given every draft."
      progressing: "The Practice pipeline samples six drafts, clusters their normalized embeddings by cosine distance under the configured threshold, and synthesizes from one representative per cluster with its support count.  The saved printout shows the clusters and the synthesis.  One consensus setting was changed, with a line on what changed.  The Try It question of your choosing was run once beside a single call.  On the no-code path: six Sampler chats, a cluster label for each sample in the spreadsheet, and a Synthesizer chat given one representative per cluster with its support count."
      proficient: "As progressing, and the readme says whether the clusters match your own reading of the drafts, naming one draft you would have grouped differently or saying why you would not.  The Try It sentence says whether consensus helped and what it cost in model calls (samples plus one, against one).  Every model and embedding call in your code, including any you added, is wrapped in an exception handler that prints a located message and a traceback.  On the no-code path, the same reading of your hand clusters and the same Try It sentence earn this row on equal terms, with every preset setting recorded in the readme in place of the exception handlers."
    - weight: 20
      description: "Writeup and Reproducibility"
      preemerging: "No readme, or one that cannot be followed."
      beginning: "A readme exists, but a reader could not rerun the three Practice runs from it."
      progressing: "The readme names your path and records the model, the package versions, config.json, and the commands well enough to rerun all three Parts.  On the no-code path: the Open WebUI version, every preset, and the spreadsheet."
      proficient: "As progressing, plus the three Try It sentences side by side with their call counts, the Learning Log, a pair log with at least two timestamped role swaps if you worked in a pair, and an AI-use disclosure."
  readings:
    - rtitle: "Critique, Consensus, and the LLM Judge: One Loop, Three Uses"
      rlink: "Activities/liascript-critiqueconsensusjudge.md"
      liapage: true
    - rtitle: "Judge Pipeline Workshop: Build and Audit a Judge (the judge Part A's second critic reuses)"
      rlink: "Activities/liascript-rubricworkshop.md"
      liapage: true
    - rtitle: "Orchestration Activity"
      rlink: "Activities/liascript-orchestration.md"
      liapage: true
    - rtitle: "Orchestration Worked Example: Build a Pipeline, a Router, and a Supervisor (round budgets, fail-closed parsing, and call counts on one task)"
      rlink: "Activities/liascript-orchestrationworkshop.md"
      liapage: true
    - rtitle: "Measuring Multi-Agent Patterns (optional: calibration, reward hacking, the judge loop, the shootout, and the threshold sweep)"
      rlink: "../Tutorials/MultiAgentMeasurement"
    - rtitle: "The Local Agent Stack"
      rlink: "../Tutorials/AgentStack"

tags:
  - multi-agent
  - agents
  - evaluation

---

Ask a model for a docstring, and the first draft often looks fine until you read it against a checklist and notice that the usage example is missing.  You could point that out and ask again.  You could also ask three copies of the model and let them argue, or ask six times and keep what most of them agree on.  Each of those spends extra model calls in the hope of a better answer.  This lab gives you all three, ready to run, so that you can see what each one does before you decide whether your final project needs one.

There are three Parts, one per pattern:

- **Part A: Critique and Refine.**  A **generator** writes a draft.  A **critic** checks it against a written rubric and says "accept" or "revise" with a list of issues.  A loop passes the issues back until the critic accepts or the round budget runs out.
- **Part B: Debate.**  Three agents answer a question alone, then each reads the others' answers and answers again.  You combine the final answers by majority vote and by a judge agent.
- **Part C: Consensus.**  One model answers the same question six times, the answers are grouped by meaning, and a synthesizer writes one answer from the groups.

Each Part has two pieces.  **Practice** gives you complete code (or ready presets) to run as-is.  You change one setting and record what changed.  **Try It** runs the same code once on a task you choose, beside a single model call, and asks for one sentence: did it help, and what did it cost in model calls?  Your task can come from anywhere: another course, a club, a hobby, or your team's [final project]({{ site.baseurl }}/Projects/FinalProject) if that is useful to you.

This lab does not include calibrating the critic, breaking its rubric, the judge-and-refine loop, the matched-budget shootout, or the threshold sweep.  Those are in the optional [Measuring Multi-Agent Patterns]({{ site.baseurl }}/Tutorials/MultiAgentMeasurement) tutorial, which runs on the code you build here.

**Pair policy.**  You may do this lab in pairs: driver and navigator roles, a swap at least every 30 minutes, and a swap log.  You each submit the same files, name each other in them, and earn the same grade.  You may also work alone.  If you do, skip the swap log and say so in your readme.  See the course schedule for the assigned and due dates.

---

## Choose Your Path

Both paths run the same three patterns and earn the same rubric.  Pick one before you start and name it at the top of your readme.

- **Ollama** runs a language model on your own computer and answers requests sent to `http://localhost:11434`.  `llama3.2` is the model both paths use.
- **Open WebUI** is a chat page in your browser that sends your messages to Ollama.  A saved **preset** (a custom Model in Open WebUI) is a model with its own system prompt, temperature, and seed.

| Path | What you run | What you need | Pick this if |
|------|--------------|---------------|--------------|
| **Code** | `critique_refine.py` (with `judge_critic.py` as a second critic), `lab4.py`, and one short run script per Part, all reading one `config.json` | Python 3, Ollama with `llama3.2`, and the packages below | You want the round budget, the answer parsing, and the call counts in code you can rerun |
| **No-code** | The same three patterns as Open WebUI presets, with you moving text between chats and a spreadsheet keeping the record | Open WebUI pointed at your local Ollama, and a spreadsheet | You would rather see each seam (where the critic's words become the reviser's instructions, where you decide which answers say the same thing) than write the code that crosses it |

On the no-code path you are the loop.  Every reply you paste is one model call, and every call gets a row in your spreadsheet.  To make a preset in Open WebUI, choose **Workspace**, **Models**, **+ Create a model**.  Use `llama3.2` as the base model, and put the prompt (if there is one) in **System Prompt**.  Set temperature and seed under **Advanced Params**.  If your version has no seed field, say so in your readme.

---

## Before You Start

Complete these first: [Critique, Consensus, and the LLM Judge]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-critiqueconsensusjudge.md) (the loop, debate, and clustering ideas this lab runs) and the [Orchestration Worked Example]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-orchestrationworkshop.md) (round budgets in configuration, fail-closed parsing, and counting calls).  If you want the judge option in Part A, keep your work from the [Judge Pipeline Workshop]({{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-rubricworkshop.md) nearby.

**Code path.**  `requests` is how your code talks to Ollama.  `sentence-transformers`, `scikit-learn`, and `numpy` do the embedding and clustering in Part C.  Activate your virtual environment first if you keep one, so the packages land in the Python you will use.

```bash
pip install requests
pip install sentence-transformers scikit-learn numpy
curl http://localhost:11434/api/tags
```

> **You should see.** Each install finishes without an error, and `curl` prints a JSON list that includes `llama3.2`.
>
> **If it fails.** "Connection refused" means Ollama is not running; start it with `ollama serve` in a separate terminal.  If `llama3.2` is missing, run `ollama pull llama3.2`.

Then run this health check.  It sends one chat request and prints the reply, so you know the model answers and can produce the small piece of JSON the critic needs.  It then embeds three sentences, normalizes the vectors, and prints how similar the first two are.  The first run downloads the embedding model, so give it a minute.

```bash
python -c "
import requests, json
r = requests.post('http://localhost:11434/api/chat', json={
    'model': 'llama3.2',
    'messages': [{'role': 'user', 'content': 'Reply with exactly: {\"verdict\": \"accept\", \"issues\": []}'}],
    'stream': False
})
print(r.json()['message']['content'])
from sentence_transformers import SentenceTransformer
import numpy as np
model = SentenceTransformer('all-MiniLM-L6-v2')
vecs = model.encode(['hello world', 'hi there', 'the sky is blue'])
# Normalize
norms = np.linalg.norm(vecs, axis=1, keepdims=True)
normed = vecs / norms
print('Embedding shape:', vecs.shape)
print('Cosine similarity (should be ~0.7 for similar sentences):')
print(normed[0] @ normed[1])
"
```

> **You should see.** The JSON line (the model may add text around it; what matters is that the JSON is there), then a shape of `(3, 384)` and a similarity near 0.7.  An import error means `pip install` went to a different Python than the one you ran.

**No-code path.**  Open Open WebUI, confirm `llama3.2` is in the model list, and send it one message.  Start a spreadsheet with one tab per Part.

**Both paths.**  Make a folder for this lab (for example `cs357-multiagent`) and create `config.json` in it.  Every setting in all three Parts lives here, so you can change a temperature, the round budget, or the number of agents without editing code.  The top-level keys are Part A's, the `debate` block is Part B's, and the `consensus` block is Part C's.  On the no-code path, this file is your record of the settings your presets use.

```json
{
  "model": "llama3.2",
  "provider_url": "http://localhost:11434/api/chat",
  "api_key": null,
  "generator_temp_first": 0.8,
  "generator_temp_revise": 0.3,
  "critic_temp": 0.0,
  "critic_seed": 42,
  "round_budget": 5,
  "rubric_file": "rubric.json",
  "debate": {"num_agents": 3, "num_rounds": 2, "temperature_schedule": [0.7, 0.4], "seed_base": 100},
  "consensus": {"num_samples": 6, "sample_temperature": 0.8, "synthesizer_temperature": 0.1,
                "distance_threshold": 0.3, "embed_model": "all-MiniLM-L6-v2"}
}
```

Leave `api_key` as `null` for local Ollama.  If your computer cannot run the model, point `provider_url` at a hosted Ollama server and set `api_key` to its key, as in the Local Agent lab.  Ask me if you need help choosing a server.

> **You should see.** `python3 -m json.tool config.json` prints the file back with no error.  An error means a missing comma or quote near the line it names.

> **Time budget.** Plan on more than one sitting: roughly an hour and a half for each Part and an hour for the readme.

---

## Part A: Critique and Refine (30 points)

One call writes, a second call checks the draft against a written rubric, and a loop hands the second call's complaints back to the first.  Three rules keep the loop honest.  The critic runs at temperature 0 with a fixed seed, so the same draft gets the same verdict every time.  A critic reply that is not valid JSON **fails closed**: the loop treats it as "revise" and logs it, so it never accepts something it could not read.  When the round budget runs out, the loop returns the last draft with the outstanding critique attached, so whoever called it knows it did not finish.

You may use either of two critics.  `critique_draft` is the accept-or-revise critic below.  `judge_critic` reuses the rubric judge from the *Judge Pipeline Workshop*: it scores each criterion from 1 to 4 with a quoted sentence, and anything below 4 becomes an issue.  Using one is enough; trying both is optional.

### Practice

> **Code path: do this.**
> 1. Create `rubric.json` with the four docstring criteria below.
> 2. Create `critique_refine.py` and `run_a.py` with the code below.
> 3. Run `python3 run_a.py | tee practice_a.txt`.  `tee` shows the output and saves it to the file.  You need at least two loop rounds; if it accepts in round 1, run it again.

```json
{
  "task": "function_docstring",
  "criteria": [
    {"id": "C1", "name": "Purpose", "descriptor": "The docstring contains a one-sentence summary of what the function does, not how it does it."},
    {"id": "C2", "name": "Parameters", "descriptor": "Every parameter is listed with its name, type, and a brief description."},
    {"id": "C3", "name": "Return value", "descriptor": "The return value's type and meaning are explicitly described. If the function returns None, this is stated."},
    {"id": "C4", "name": "Example", "descriptor": "At least one usage example is provided in a doctest-compatible format (>>> function_call())."}
  ],
  "accept_threshold": "All four criteria must be met for a verdict of 'accept'."
}
```

```python
import requests
import json
import traceback

def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def load_rubric(config):
    with open(config["rubric_file"]) as f:
        return json.load(f)

def generate_draft(task_description, previous_draft=None, critique=None, config=None):
    """
    Generate a draft for the given task.
    If previous_draft and critique are provided, this is a revision call.
    """
    temperature = config["generator_temp_first"] if previous_draft is None else config["generator_temp_revise"]
    if previous_draft is None:
        user_message = f"Generate a draft for the following task:\n\n{task_description}"
    else:
        user_message = (
            f"Here is the task:\n\n{task_description}\n\n"
            f"Here is your previous draft:\n\n{previous_draft}\n\n"
            f"Here is the critique you must address:\n\n{json.dumps(critique, indent=2)}\n\n"
            f"Please revise the draft to address every issue listed. Return only the revised draft, no commentary."
        )
    messages = [{"role": "user", "content": user_message}]
    payload = {"model": config["model"], "messages": messages, "stream": False,
               "options": {"temperature": temperature}}
    try:
        response = requests.post(config["provider_url"], json=payload, headers=({"Authorization": f"Bearer {config['api_key']}"} if config.get("api_key") else {}), timeout=60)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab3:generate_draft] {e}")
        traceback.print_exc()
        raise

def critique_draft(draft, rubric, config):
    """
    Ask the critic to evaluate the draft against the rubric.
    Returns a dict: {"verdict": "accept"|"revise", "issues": [...]}
    On JSON parse failure, returns a "revise" verdict whose issue holds the raw output.
    """
    criteria_text = "\n".join(
        f"- {c['id']} ({c['name']}): {c['descriptor']}"
        for c in rubric["criteria"]
    )
    system_prompt = (
        "You are a strict quality critic. Evaluate the draft against every criterion below. "
        "Return ONLY valid JSON in this exact format, with no additional text:\n"
        '{"verdict": "accept" or "revise", "issues": ["issue 1", "issue 2", ...]}\n\n'
        "Use 'accept' only if ALL criteria are fully met. "
        "Use 'revise' if ANY criterion is not met. "
        "List every unmet criterion as a separate issue string.\n\n"
        f"CRITERIA:\n{criteria_text}\n\n"
        f"ACCEPT THRESHOLD: {rubric['accept_threshold']}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"DRAFT TO EVALUATE:\n\n{draft}"}
    ]
    payload = {"model": config["model"], "messages": messages, "stream": False,
               "options": {"temperature": config["critic_temp"], "seed": config["critic_seed"]}}
    try:
        response = requests.post(config["provider_url"], json=payload, headers=({"Authorization": f"Bearer {config['api_key']}"} if config.get("api_key") else {}), timeout=60)
        response.raise_for_status()
        raw = response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab3:critique_draft:network] {e}")
        traceback.print_exc()
        raise
    # Try to parse JSON; fail closed on malformed output
    try:
        # Strip markdown code fences if present
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        critique = json.loads(clean)
        assert "verdict" in critique and "issues" in critique
        return critique
    except Exception as e:
        print(f"[lab3:critique_draft:json_parse] Malformed critic output, failing closed. Raw: {raw!r}")
        return {"verdict": "revise", "issues": [f"[JSON parse failure] Raw output: {raw[:200]}"]}

def critique_refine_loop(task_description, config, rubric, critic=critique_draft):
    """
    Run the generate/critique/refine loop.
    critic is any function (draft, rubric, config) -> {"verdict", "issues"}.
    Returns (final_draft, final_critique, rounds_used, termination_reason).
    """
    draft = None
    critique = None
    for round_num in range(1, config["round_budget"] + 1):
        print(f"\n=== Round {round_num} ===")
        # Generate
        draft = generate_draft(task_description, previous_draft=draft, critique=critique, config=config)
        print(f"[Generator] Draft (first 200 chars): {draft[:200]}...")
        # Critique
        critique = critic(draft, rubric, config)
        print(f"[Critic] Verdict: {critique['verdict']}")
        if critique["issues"]:
            print(f"[Critic] Issues: {critique['issues']}")
        if critique["verdict"] == "accept":
            return (draft, critique, round_num, "accepted")
    # Budget exhausted: return the last draft with the critique attached
    final_output = f"{draft}\n\n--- OUTSTANDING CRITIQUE (budget exhausted after {config['round_budget']} rounds) ---\n{json.dumps(critique, indent=2)}"
    return (final_output, critique, config["round_budget"], "budget_exhausted")
```

```python
# run_a.py: one single call, then the critique-and-refine loop, on the same task
from critique_refine import load_config, load_rubric, generate_draft, critique_draft, critique_refine_loop

TASK = "Write a Python docstring for a function called `merge_sorted_lists` that takes two sorted lists of integers and returns a single sorted list."
RUBRIC_FILE = "rubric.json"
USE_JUDGE = False  # True uses judge_critic and JUDGE_RUBRIC from judge_critic.py

config = load_config()
if USE_JUDGE:
    from judge_critic import judge_critic, JUDGE_RUBRIC
    critic, rubric = judge_critic, JUDGE_RUBRIC
else:
    critic, rubric = critique_draft, load_rubric({**config, "rubric_file": RUBRIC_FILE})

single = generate_draft(TASK, config=config)
print(f"=== SINGLE CALL (1 model call) ===\n{single}")

draft, critique, rounds, reason = critique_refine_loop(TASK, config, rubric, critic=critic)
print(f"\n=== LOOP: {reason} after {rounds} rounds ({2 * rounds} model calls) ===\n{draft}")
```

The `[lab3:generate_draft]` tag in each `except` block is a **located message**: it names the function that failed, and the traceback after it says why.  Keep these handlers, and give any model call you add one of its own.

> **You should see.** The single draft, then a banner, a draft preview, and a verdict per round, then `accepted` or an `OUTSTANDING CRITIQUE` block.  Abbreviated; your drafts and round count will differ.

```text
=== Round 1 ===
[Generator] Draft (first 200 chars): """Merge two sorted lists.
[Critic] Verdict: revise
[Critic] Issues: ['C4 (Example): No usage example in doctest format is provided.']

=== Round 2 ===
[Generator] Draft (first 200 chars): """Merge two sorted lists of integers into one sorted list.
[Critic] Verdict: accept

=== LOOP: accepted after 2 rounds (4 model calls) ===
```

**Predict:** if the critic wraps its JSON in a sentence such as "Here is my evaluation:", which branch of `critique_draft` runs, and what verdict does the loop receive?

**The judge as critic (optional).**  To use the workshop's judge instead, create `judge_critic.py` below, set `USE_JUDGE = True` in `run_a.py`, and run it again.  It keeps the workshop's prompt and its 1-to-4 levels, rewritten for the docstring task with the same ids C1 to C4.  It reads `critic_temp` and `critic_seed` (0 and 42, the workshop's settings) from `config.json`.  The code, not the model, decides the verdict: it returns "accept" only when every criterion is at level 4.

```python
import json
import traceback
import requests

# The workshop's leveled rubric shape, written for the docstring task.
JUDGE_RUBRIC = {
  "criteria": [
    {"id": "C1", "name": "Purpose",
     "levels": {"1": "no summary", "2": "a summary of how the function works, not what it does",
                "3": "a summary of what it does, longer than one sentence", "4": "a one-sentence summary of what it does"}},
    {"id": "C2", "name": "Parameters",
     "levels": {"1": "no parameters listed", "2": "some parameters listed",
                "3": "every parameter listed, but a type or description is missing", "4": "every parameter listed with name, type, and description"}},
    {"id": "C3", "name": "Return value",
     "levels": {"1": "return value not mentioned", "2": "return value mentioned without its type",
                "3": "type given but meaning vague", "4": "type and meaning both stated"}},
    {"id": "C4", "name": "Example",
     "levels": {"1": "no example", "2": "an example that is not in doctest format",
                "3": "a doctest with no expected output", "4": "a doctest (>>> call) with its expected output"}},
  ]
}

def judge_critic(draft, rubric, config):
    """
    Score the draft 1-4 on each criterion with the workshop judge's prompt.
    Returns {"verdict": "accept"|"revise", "issues": [...]}; every criterion below 4 is an issue.
    Fails closed: an unparseable reply is a "revise".
    """
    system = ("You are a strict grader. Score the artifact on EACH criterion by choosing a level 1-4 "
              "that matches the level descriptions. Quote the sentence that justifies each score. "
              "Respond ONLY with JSON: "
              '{"scores": {"<criterion id>": {"level": int, "evidence": str}}}')
    user = f"RUBRIC:\n{json.dumps(rubric, indent=1)}\n\nARTIFACT:\n{draft}"
    payload = {"model": config["model"], "stream": False,
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
               "options": {"temperature": config["critic_temp"], "seed": config["critic_seed"]}}
    try:
        response = requests.post(config["provider_url"], json=payload, headers=({"Authorization": f"Bearer {config['api_key']}"} if config.get("api_key") else {}), timeout=180)
        response.raise_for_status()
        raw = response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab3:judge_critic:network] {e}")
        traceback.print_exc()
        raise
    try:
        data = json.loads(raw.replace("```json", "").replace("```", ""))
        issues = []
        for c in rubric["criteria"]:
            s = data["scores"][c["id"]]
            level = int(s["level"])
            if level < 4:
                issues.append(f"{c['id']} ({c['name']}): level {level} of 4, evidence {s.get('evidence', '')!r}. "
                              f"Level 4 needs: {c['levels']['4']}.")
        return {"verdict": "accept" if not issues else "revise", "issues": issues}
    except Exception as e:
        print(f"[lab3:judge_critic:json_parse] Malformed judge output, failing closed. Raw: {raw!r}")
        return {"verdict": "revise", "issues": [f"[JSON parse failure] Raw output: {raw[:200]}"]}
```

**No-code path.**  Make three presets.  The Generator and Reviser have no system prompt.  Their instructions travel in the message you paste, exactly as in the code.

| Preset | System Prompt | Temperature | Seed |
|---|---|---|---|
| Generator | (none) | 0.8 | (none) |
| Reviser | (none) | 0.3 | (none) |
| Critic | the text below | 0 | 42 |

The Critic's system prompt is the one `critique_draft` builds from `rubric.json`:

```text
You are a strict quality critic. Evaluate the draft against every criterion below. Return ONLY valid JSON in this exact format, with no additional text:
{"verdict": "accept" or "revise", "issues": ["issue 1", "issue 2", ...]}

Use 'accept' only if ALL criteria are fully met. Use 'revise' if ANY criterion is not met. List every unmet criterion as a separate issue string.

CRITERIA:
- C1 (Purpose): The docstring contains a one-sentence summary of what the function does, not how it does it.
- C2 (Parameters): Every parameter is listed with its name, type, and a brief description.
- C3 (Return value): The return value's type and meaning are explicitly described. If the function returns None, this is stated.
- C4 (Example): At least one usage example is provided in a doctest-compatible format (>>> function_call()).

ACCEPT THRESHOLD: All four criteria must be met for a verdict of 'accept'.
```

If you would rather use the workshop's judge as your critic, put its grader prompt and a leveled version of these four criteria in the Critic preset instead, and treat any criterion below level 4 as an issue.

> **Do this.**
> 1. In a Generator chat, send: `Generate a draft for the following task:` followed by a blank line and the `merge_sorted_lists` task from the code above.
> 2. In a fresh Critic chat, send `DRAFT TO EVALUATE:`, a blank line, and the draft.
> 3. If the verdict is "revise", open a fresh Reviser chat and send the message below, with a blank line between its parts, then take the new draft back to step 2:
>
>    ```text
>    Here is the task:
>    <task>
>    Here is your previous draft:
>    <draft>
>    Here is the critique you must address:
>    <the critic's JSON>
>    Please revise the draft to address every issue listed. Return only the revised draft, no commentary.
>    ```
>
> 4. Stop at "accept" or after five rounds, whichever comes first.  A Critic reply that is not valid JSON counts as "revise".  Write it down.
> 5. Log one row per round in the spreadsheet: `round`, `verdict`, `issues`, `valid JSON?`, `calls so far`.

**Both paths: change one setting.**  Pick one, rerun, and write one line in your readme: the setting, its old and new value, and what changed (round count, verdicts, or the drafts themselves).  Then put it back.

- `round_budget` from 5 to 1
- `generator_temp_first` from 0.8 to 0.1
- delete criterion C4 from `rubric.json` (no-code: from the Critic's system prompt)
- switch critics, `critique_draft` to `judge_critic` or the other way

### Try It

Pick one task of your own with criteria a reader can check by looking at the result: an email to a professor, a lab report abstract, a commit message, a set of instructions for a club event, or a piece of your team's project.

> **Do this.**
> 1. Copy `rubric.json` to `rubric_mytask.json` and rewrite the four descriptors for your task.  Keep the ids C1 to C4 and the `accept_threshold` line.  (No-code: make a second Critic preset with your criteria.)
> 2. Code path: in `run_a.py`, set `TASK` to your task and `RUBRIC_FILE` to `"rubric_mytask.json"`, then run `python3 run_a.py | tee tryit_a.txt`.  (With `USE_JUDGE = True`, rewrite the levels in `JUDGE_RUBRIC` for your task instead.)  No-code: send your task to a Generator chat once and keep that draft as the single call, then run the Practice loop on the same task.
> 3. Read the two drafts against your own rubric and write one sentence in your readme: did the loop help, and what did it cost in model calls?  The single call is one model call; the loop is two per round.

---

## Part B: Debate (25 points)

Ask three copies of the same model "What is 15% of 240?" and you may get two that say 36 and one that says 34.  Now show each one what the other two said and ask again.  Does the odd one out fix its arithmetic, does it talk the others into its answer, or does nobody move?

Round one is independent: each agent answers alone.  Later rounds are peer-informed: each agent sees the *other* agents' previous answers and may revise or hold its position.  Every response must end with an `ANSWER:` line, and the code reads the answer from that line only.  When the line is missing, the code prints a located warning and records no answer instead of guessing.  The final round is combined two ways: **majority vote**, which counts the answers, and a **judge agent**, which is one more model call that reads every agent's reasoning and picks the best-supported answer, even if only one agent gave it.

### Practice

> **Code path: do this.**
> 1. Create `lab4.py` with the code below.  Part C adds to this same file.
> 2. Create `run_b.py` below and run `python3 run_b.py | tee practice_b.txt`.  The saved output is your debate transcript.

```python
import requests
import json
import re
import traceback
from collections import Counter

def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def agent_respond(question, agent_id, round_num, peer_answers, config):
    """
    Generate one agent's response for the given round.
    round_num: 1-indexed
    peer_answers: list of (agent_id, answer_text) from the previous round (empty for round 1)
    Returns the full response text.
    """
    schedule = config["debate"]["temperature_schedule"]
    temp = schedule[min(round_num - 1, len(schedule) - 1)]
    seed = config["debate"]["seed_base"] + agent_id * 100 + round_num
    if round_num == 1:
        # Independent first round
        user_content = (
            f"Question: {question}\n\n"
            f"Think through this carefully and provide your answer. "
            f"End your response with a line in exactly this format:\n"
            f"ANSWER: <your answer here>"
        )
    else:
        # Peer-informed revision round
        peer_section = "\n\n".join(
            f"Agent {pid} said:\n{ans}" for pid, ans in peer_answers
        )
        user_content = (
            f"Question: {question}\n\n"
            f"Here are the answers from the other agents in the previous round:\n\n"
            f"{peer_section}\n\n"
            f"Review their reasoning. You may revise your answer if you find their arguments convincing, "
            f"or maintain your position with a rebuttal. "
            f"End your response with a line in exactly this format:\n"
            f"ANSWER: <your answer here>"
        )
    messages = [{"role": "user", "content": user_content}]
    payload = {"model": config["model"], "messages": messages, "stream": False,
               "options": {"temperature": temp, "seed": seed}}
    try:
        response = requests.post(config["provider_url"], json=payload, headers=({"Authorization": f"Bearer {config['api_key']}"} if config.get("api_key") else {}), timeout=60)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab4:agent_respond:agent{agent_id}:round{round_num}] {e}")
        traceback.print_exc()
        raise

def extract_answer(response_text, agent_id, round_num):
    """
    Extract the ANSWER: line from a response.
    Returns the answer string, or None if not found (with a located warning).
    """
    matches = re.findall(r"ANSWER:\s*(.+)", response_text, re.IGNORECASE)
    if matches:
        return matches[-1].strip()       # the last ANSWER: line, so an echoed template line is not counted
    else:
        print(f"[lab4:extract_answer] WARNING: Agent {agent_id}, round {round_num}: no ANSWER: line found. Full response: {response_text[:200]!r}")
        return None

def run_debate(question, config):
    """
    Run a full multi-agent debate.
    Returns (final_answers_by_agent, all_round_transcripts, total_calls).
    """
    num_agents = config["debate"]["num_agents"]
    num_rounds = config["debate"]["num_rounds"]
    total_calls = 0
    # round_answers[round][agent_id] = (full_response, extracted_answer)
    round_answers = {}
    for round_num in range(1, num_rounds + 1):
        print(f"\n=== Debate Round {round_num} ===")
        round_answers[round_num] = {}
        for agent_id in range(num_agents):
            # Peer answers: all agents from previous round except self
            if round_num == 1:
                peer_answers = []
            else:
                peer_answers = [
                    (pid, extract_answer(data[0], pid, round_num - 1) or "(no answer)")
                    for pid, data in round_answers[round_num - 1].items()
                    if pid != agent_id
                ]
            response = agent_respond(question, agent_id, round_num, peer_answers, config)
            answer = extract_answer(response, agent_id, round_num)
            round_answers[round_num][agent_id] = (response, answer)
            total_calls += 1
            print(f"  Agent {agent_id}: ANSWER = {answer}")
    # Final answers from last round
    final_answers = {
        agent_id: data[1]
        for agent_id, data in round_answers[num_rounds].items()
        if data[1] is not None
    }
    return final_answers, round_answers, total_calls

def majority_vote(final_answers):
    """
    Return the most common answer among the agents.
    In case of a tie, return the answer that reached the top count first.
    """
    if not final_answers:
        return None
    counts = Counter(final_answers.values())
    return counts.most_common(1)[0][0]

def judge_aggregate(question, round_answers, config):
    """
    Send every agent's final-round response to a separate judge call.
    Returns (chosen_answer, judge_response_text); chosen_answer is None if the judge gave no ANSWER: line.
    """
    num_rounds = config["debate"]["num_rounds"]
    candidates = "\n\n".join(
        f"Agent {agent_id} (ANSWER: {answer or '(no answer)'}):\n{response}"
        for agent_id, (response, answer) in round_answers[num_rounds].items()
    )
    user_content = (
        f"Question: {question}\n\n"
        f"Several agents debated this question. Here is each agent's final response:\n\n"
        f"{candidates}\n\n"
        f"You are the judge. Do not count votes. Choose the answer that is best supported by correct reasoning, "
        f"even if only one agent gave it. Explain your choice in one or two sentences, then end with a line "
        f"in exactly this format:\n"
        f"ANSWER: <the answer you choose>"
    )
    payload = {"model": config["model"], "messages": [{"role": "user", "content": user_content}], "stream": False,
               "options": {"temperature": config["critic_temp"], "seed": config["critic_seed"]}}
    try:
        response = requests.post(config["provider_url"], json=payload, headers=({"Authorization": f"Bearer {config['api_key']}"} if config.get("api_key") else {}), timeout=60)
        response.raise_for_status()
        judge_text = response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab4:judge_aggregate:network] {e}")
        traceback.print_exc()
        raise
    return extract_answer(judge_text, "judge", num_rounds), judge_text
```

```python
# run_b.py: one single call, then a full debate combined both ways, on the same question
from lab4 import load_config, agent_respond, extract_answer, run_debate, majority_vote, judge_aggregate

QUESTION = "What is 15% of 240?"

config = load_config()
single = extract_answer(agent_respond(QUESTION, 0, 1, [], config), "single", 1)
print(f"=== SINGLE CALL (1 model call) ===\nANSWER = {single}")

final_answers, transcripts, calls = run_debate(QUESTION, config)
judge_choice, judge_text = judge_aggregate(QUESTION, transcripts, config)
print(f"\nFinal answers: {final_answers}")
print(f"Majority vote: {majority_vote(final_answers)}")
print(f"Judge agent: {judge_choice}")
print(f"Debate model calls: {calls + 1}")
```

The single call is agent 0's round-1 call made on its own, so the comparison asks whether the debate changed what one agent would have said alone.

> **You should see.** The single answer, two rounds of three agents, then both aggregates.  Your answers will differ, but the debate's call count is agents times rounds, plus one for the judge.

```text
=== SINGLE CALL (1 model call) ===
ANSWER = 36
=== Debate Round 1 ===
  Agent 0: ANSWER = 36
  Agent 1: ANSWER = 36
  Agent 2: ANSWER = 34
=== Debate Round 2 ===
  Agent 0: ANSWER = 36
  Agent 1: ANSWER = 36
  Agent 2: ANSWER = 36
Final answers: {0: '36', 1: '36', 2: '36'}
Majority vote: 36
Judge agent: 36
Debate model calls: 7
```

**Predict:** with the `config.json` above, what temperature and seed does agent 2 get in round 2?  Work it out from the first three lines of `agent_respond`.

**Predict:** if the three final answers are `36`, `36.0`, and `$36`, what does `majority_vote` return, and is that the answer you wanted?

**No-code path.**  Make two presets, Debater R1 (temperature 0.7) and Debater R2 (temperature 0.4), with no system prompt and **no seed**, so three chats on the same preset can give different answers.  Make a third, Debate Judge, with temperature 0 and seed 42.

> **Do this.**
> 1. Round 1: open three Debater R1 chats (agents 0, 1, and 2) and send each the same message:
>
>    ```text
>    Question: What is 15% of 240?
>
>    Think through this carefully and provide your answer. End your response with a line in exactly this format:
>    ANSWER: <your answer here>
>    ```
>
> 2. Round 2: open three Debater R2 chats.  Send each agent the message below, filled in with the *other two* agents' numbers and the answers from their round-1 `ANSWER:` lines (agent 0 sees agents 1 and 2, agent 1 sees 0 and 2, and so on):
>
>    ```text
>    Question: What is 15% of 240?
>
>    Here are the answers from the other agents in the previous round:
>
>    Agent <id> said:
>    <that agent's answer>
>    Agent <id> said:
>    <that agent's answer>
>
>    Review their reasoning. You may revise your answer if you find their arguments convincing, or maintain your position with a rebuttal. End your response with a line in exactly this format:
>    ANSWER: <your answer here>
>    ```
>
> 3. Take the majority vote of the round-2 answers by hand.  Then open a Debate Judge chat and send this, with each agent's full round-2 response filled in:
>
>    ```text
>    Question: What is 15% of 240?
>
>    Several agents debated this question. Here is each agent's final response:
>
>    Agent 0 (ANSWER: <its answer>):
>    <its full response>
>    (and the same for agents 1 and 2)
>
>    You are the judge. Do not count votes. Choose the answer that is best supported by correct reasoning, even if only one agent gave it. Explain your choice in one or two sentences, then end with a line in exactly this format:
>    ANSWER: <the answer you choose>
>    ```
>
> 4. Log one row per response in the spreadsheet: `agent`, `round`, `ANSWER`, `changed from round 1?`.  A response with no `ANSWER:` line gets "no answer", not your best guess.

**Both paths: change one setting.**  Pick one, rerun, and write one line in your readme: the setting, its old and new value, and what changed.  Then put it back.

- `num_rounds` from 2 to 3 (no-code: a third round with Debater R2)
- `temperature_schedule` from `[0.7, 0.4]` to `[1.0, 1.0]`
- `num_agents` from 3 to 5

### Try It

Pick one question of your own with a short answer you can check: a calculation from another course, a scheduling puzzle, a factual question you can look up, or a decision your team has to make between named options.

> **Do this.**
> 1. Code path: set `QUESTION` in `run_b.py` to your question and run `python3 run_b.py | tee tryit_b.txt`.  No-code: send your question to one Debater R1 chat as the single call, then run the Practice debate on it.
> 2. Check the answers yourself and write one sentence in your readme: did the debate help, and what did it cost in model calls?

**Predict:** in a debate where two agents answer `34` and one answers `36` with correct working, which answer will `majority_vote` return, and which do you expect `judge_aggregate` to return?

---

## Part C: Consensus (25 points)

Ask the model "What makes a great study group, and what are the biggest pitfalls to avoid?" six times and you get six different paragraphs.  No two match word for word, so the vote from Part B has nothing to count.  Yet several of them clearly say the same thing in different words.

**Stochastic consensus** handles this.  At a temperature above zero, the model is a sampler: each call draws one answer from many plausible ones.  An **embedding** model turns each draft into a list of numbers, so that drafts with similar meaning get nearby lists.  We normalize those vectors to length 1 and group them by **cosine distance** (1 minus the cosine similarity).  Two drafts whose distance is under `distance_threshold` can share a group.  The size of each group is its **support count**.  A low-temperature **synthesizer** then gets one representative draft per group with its support count, never all six drafts.  It writes one answer that follows the majority, and when the split is close, it says so in one line.  That is six sampling calls and one synthesis call, seven in all.

> **Watch out.** Sampling helps only when the drafts' mistakes scatter.  If every draft shares the same bias, they land in one big group and look exactly like a strong consensus.

### Practice

**Code path.**  The embedding and clustering code is provided complete.  `sentence-transformers` and scikit-learn's `AgglomerativeClustering` do the work.  Your job is to run it and read what it returns.

> **Do this.**
> 1. Add the code below to the end of `lab4.py`.
> 2. Create `run_c.py` below and run `python3 run_c.py | tee practice_c.txt`.  The saved output is your consensus transcript.

```python
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering

def sample_drafts(question, config):
    """
    Sample k independent drafts at high temperature.
    Returns list of draft strings.
    """
    k = config["consensus"]["num_samples"]
    temp = config["consensus"]["sample_temperature"]
    drafts = []
    for i in range(k):
        seed = config["debate"]["seed_base"] + i  # different seed per sample
        messages = [{"role": "user", "content": question}]
        payload = {"model": config["model"], "messages": messages, "stream": False,
                   "options": {"temperature": temp, "seed": seed}}
        try:
            response = requests.post(config["provider_url"], json=payload, headers=({"Authorization": f"Bearer {config['api_key']}"} if config.get("api_key") else {}), timeout=60)
            response.raise_for_status()
            draft = response.json()["message"]["content"]
            drafts.append(draft)
            print(f"  Sample {i+1}/{k}: {draft[:80]}...")
        except Exception as e:
            print(f"[lab4:sample_drafts:sample{i}] {e}")
            traceback.print_exc()
            raise
    return drafts

def cluster_drafts(drafts, config):
    """
    Embed drafts, normalize vectors, cluster by cosine distance.
    Returns (labels, normed, cluster_representatives).
    labels[i] = cluster ID for draft i.
    cluster_representatives: dict {cluster_id: (representative_draft, support_count)}
    """
    embed_model_name = config["consensus"]["embed_model"]
    threshold = config["consensus"]["distance_threshold"]
    try:
        embed_model = SentenceTransformer(embed_model_name)
        embeddings = embed_model.encode(drafts)
    except Exception as e:
        print(f"[lab4:cluster_drafts:embed] {e}")
        traceback.print_exc()
        raise
    # Normalize to unit vectors so cosine distance = 1 - dot product
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normed = embeddings / norms
    # Merge groups while their average cosine distance stays under the threshold
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=threshold,
        metric="cosine",
        linkage="average"
    )
    labels = clustering.fit_predict(normed)
    # Find representative (draft closest to cluster centroid) and support count
    cluster_ids = set(labels)
    representatives = {}
    for cid in cluster_ids:
        indices = [i for i, l in enumerate(labels) if l == cid]
        support = len(indices)
        # Centroid of normalized vectors
        centroid = normed[indices].mean(axis=0)
        centroid /= np.linalg.norm(centroid)
        # Draft closest to centroid
        similarities = [normed[i] @ centroid for i in indices]
        best_idx = indices[int(np.argmax(similarities))]
        representatives[cid] = (drafts[best_idx], support)
    print(f"\nClustering: {len(drafts)} drafts -> {len(cluster_ids)} clusters (threshold={threshold})")
    for cid, (rep, support) in sorted(representatives.items()):
        print(f"  Cluster {cid} (support={support}): {rep[:80]}...")
    return labels, normed, representatives

def synthesize(question, representatives, config):
    """
    Build a context from cluster representatives and synthesize a final answer.
    Returns the synthesized answer string.
    """
    # Sort by support (descending) so the synthesizer sees majority first
    sorted_clusters = sorted(representatives.items(), key=lambda x: -x[1][1])
    total_support = sum(s for _, (_, s) in sorted_clusters)
    context_parts = []
    for cid, (rep, support) in sorted_clusters:
        pct = support / total_support * 100
        context_parts.append(f"[Cluster {cid}, support={support}/{total_support} ({pct:.0f}%)]\n{rep}")
    context = "\n\n---\n\n".join(context_parts)
    majority_support = sorted_clusters[0][1][1]
    close_disagreement = len(sorted_clusters) > 1 and (majority_support / total_support) < 0.6
    system_prompt = (
        "You are a synthesizer. You receive several response clusters from independent samples. "
        "Each cluster is labeled with its support count. "
        "Your job:\n"
        "1. Follow the majority position on any factual conflicts.\n"
        "2. If there is a close disagreement (majority < 60% of samples), disclose it in one sentence at the end.\n"
        "3. Produce a single coherent, well-written response. Do not just concatenate the clusters.\n\n"
        + ("NOTE: There is a close disagreement among the samples. Disclose it." if close_disagreement else "")
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Question: {question}\n\nClusters:\n\n{context}"}
    ]
    payload = {"model": config["model"], "messages": messages, "stream": False,
               "options": {"temperature": config["consensus"]["synthesizer_temperature"],
                           "seed": config["debate"]["seed_base"]}}
    try:
        response = requests.post(config["provider_url"], json=payload, headers=({"Authorization": f"Bearer {config['api_key']}"} if config.get("api_key") else {}), timeout=60)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"[lab4:synthesize] {e}")
        traceback.print_exc()
        raise

def run_consensus(question, config):
    """Full sample-cluster-synthesize pipeline."""
    print(f"\n=== Sampling {config['consensus']['num_samples']} drafts ===")
    drafts = sample_drafts(question, config)
    print("\n=== Clustering ===")
    labels, embeddings, representatives = cluster_drafts(drafts, config)
    print("\n=== Synthesizing ===")
    synthesis = synthesize(question, representatives, config)
    total_calls = config["consensus"]["num_samples"] + 1  # samples + synthesizer
    return synthesis, drafts, labels, representatives, total_calls
```

```python
# run_c.py: one single call, then the consensus pipeline, on the same question
from lab4 import load_config, sample_drafts, run_consensus

QUESTION = "What makes a great study group, and what are the biggest pitfalls to avoid?"

config = load_config()
one_call = {**config, "consensus": {**config["consensus"], "num_samples": 1}}
single = sample_drafts(QUESTION, one_call)[0]
print(f"=== SINGLE CALL (1 model call) ===\n{single}")

synthesis, drafts, labels, reps, calls = run_consensus(QUESTION, config)
for i, (label, draft) in enumerate(zip(labels, drafts)):
    print(f"Draft {i + 1} -> cluster {label}: {draft[:80]}...")
print(f"\n=== SYNTHESIZED ANSWER ({calls} model calls) ===\n{synthesis}")
```

> **You should see.** The single answer, six sample previews, a clustering summary with support counts, each draft's cluster, and one synthesized answer, with a disclosure line when the split is close.  Abbreviated:

```text
=== Clustering ===
Clustering: 6 drafts -> 3 clusters (threshold=0.3)
  Cluster 0 (support=3): A great study group needs clear goals...
  Cluster 1 (support=2): The key ingredients are...
  Cluster 2 (support=1): Study groups work best when...

=== SYNTHESIZED ANSWER (7 model calls) ===
A great study group combines clear shared goals, consistent meeting times, and mutual accountability...
Note: there was minor disagreement about whether size or structure matters more.
```

**Predict:** look at the `close_disagreement` line in `synthesize`.  With six samples split 3, 2, and 1, does the synthesizer get the "disclose it" note?  What about a 4 and 2 split?

**No-code path.**  Make two presets: Sampler (temperature 0.8, no system prompt, **no seed**) and Synthesizer (temperature 0.1, seed 100).  The Synthesizer's system prompt is the one `synthesize` builds:

```text
You are a synthesizer. You receive several response clusters from independent samples. Each cluster is labeled with its support count. Your job:
1. Follow the majority position on any factual conflicts.
2. If there is a close disagreement (majority < 60% of samples), disclose it in one sentence at the end.
3. Produce a single coherent, well-written response. Do not just concatenate the clusters.
```

> **Do this.**
> 1. Send the study-group question to six fresh Sampler chats.  Paste each answer into the spreadsheet: `sample`, `first sentence`, `cluster`, `why`.
> 2. Read all six and give each one a cluster letter: drafts that take the same position share a letter.  In `why`, write the position in a few words.
> 3. For each cluster, pick the draft that best represents it, and count its support.
> 4. Open a Synthesizer chat and send `Question:` with the question, then `Clusters:` and one block per cluster, largest first.  Use the code's format: `[Cluster A, support=3/6 (50%)]` followed by the representative draft, with a line holding only `---` between blocks.  If the largest cluster has under 60% of the samples, add the line `NOTE: There is a close disagreement among the samples. Disclose it.` to the end of your message.

**Both paths: read the clusters.**  Read the drafts in each cluster yourself.  In your readme, say whether the grouping matches your own reading, and name one draft you would have put in a different group, or say why you would not.  (No-code: did any draft take you more than a moment to place?  Which one, and what made it hard?)

**Both paths: change one setting.**  Pick one, rerun, and write one line in your readme: the setting, its old and new value, and what changed in the clusters or the synthesis.  Then put it back.

- `distance_threshold` from 0.3 to 0.1 or to 0.5 (no-code: merge your two closest clusters into one, or split your largest)
- `sample_temperature` from 0.8 to 0.3
- `num_samples` from 6 to 3 (keep it at 2 or more; clustering needs at least two drafts)

### Try It

Pick one open-ended question of your own, one with several reasonable answers: how to structure a project timeline, what to include in a lab safety briefing, which features a club website needs, or a design question your team is weighing.

> **Do this.**
> 1. Code path: set `QUESTION` in `run_c.py` to your question and run `python3 run_c.py | tee tryit_c.txt`.  No-code: one Sampler chat is the single call.  Then run the Practice pipeline on your question.
> 2. Read the single answer and the synthesis side by side, and write one sentence in your readme: did consensus help, and what did it cost in model calls?

**Predict:** the single call uses the same prompt, temperature, and seed as Sample 1 of the consensus run.  How will the two compare, and what would it tell you about your model server if they differ?

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Connection refused, or an error tagged `[lab3:...]` or `[lab4:...]` with a connection message | Ollama is not running | Start it with `ollama serve` and retry |
| The critic says "revise" every round | The critic's JSON is not parsing, or a descriptor is too strict | Look for the `json_parse` line and the raw reply; loosen one descriptor as a test |
| `ANSWER = None` with a `[lab4:extract_answer] WARNING` | The model wrote `**ANSWER:**` or left the line off | Add `response_text = re.sub(r'\*+', '', response_text)` at the top of `extract_answer`, or rerun |
| All debate agents agree in round 1 every time | Temperature too low, or the question has one obvious answer | Try `[0.9, 0.5]`, or a question people often get wrong |
| `ValueError` from `AgglomerativeClustering` about too few samples | `num_samples` is below 2 | Set it to 2 or more |
| Every draft lands in one cluster, or each in its own | The threshold is too loose or too tight for your drafts | Move `distance_threshold` toward 0.15 or 0.5 and rerun |
| (No-code) Three Debater or Sampler chats give the same answer word for word | A seed is set on the preset | Clear the seed field and start fresh chats |

---

## Deliverables

Submit one ZIP.  The readme names your path at the top.

| File or artifact | What it shows | Rubric row |
|---|---|---|
| `config.json`, `rubric.json`, `rubric_mytask.json`, `critique_refine.py` (and `judge_critic.py` if you used it), `run_a.py`, `practice_a.txt`, and `tryit_a.txt` (no-code: the Generator, Reviser, and Critic presets and the Part A spreadsheet tab) | The loop running to a stop, a draft changing in response to a critique, your changed setting, and the Try It comparison | Part A: Critique and Refine (30) |
| `lab4.py`, `run_b.py`, `practice_b.txt`, and `tryit_b.txt` (no-code: the Debater and Debate Judge presets, the chats, and the Part B tab) | A three-agent, two-round debate combined by vote and by judge, your changed setting, and the Try It comparison | Part B: Debate (25) |
| `lab4.py`, `run_c.py`, `practice_c.txt`, and `tryit_c.txt` (no-code: the Sampler and Synthesizer presets, the chats, and the Part C tab with your clusters) | Six samples, their clusters, the synthesis, your reading of the clusters, your changed setting, and the Try It comparison | Part C: Consensus (25) |
| A readme with your path, model and package versions (`pip show requests sentence-transformers scikit-learn numpy`), the commands you ran, the three changed-setting lines, the three Try It sentences side by side with their call counts, the Learning Log, a pair log if you worked in a pair, and an AI-use disclosure (no-code: the Open WebUI version and every preset setting) | A reader could rerun everything | Writeup and Reproducibility (20) |

---

## Self-Check Before You Submit

- [ ] My readme names my path, code or no-code.
- [ ] **Part A:** the loop ran to a printed stop (accepted or budget exhausted), and my saved transcript shows at least two rounds with a draft changing in response to a critique.
- [ ] **Part B:** a three-agent, two-round debate ran, with every answer read from its `ANSWER:` line and the final round combined by both majority vote and the judge.
- [ ] **Part C:** six samples were clustered and synthesized from one representative per cluster with its support count, and I wrote whether the clusters match my own reading.
- [ ] For each Part, one changed setting with its old value, new value, and what changed.
- [ ] For each Part, one Try It run on a task I chose, beside a single call, with one sentence on whether it helped and what it cost in model calls.
- [ ] Code path: every model and embedding call, including any I added, sits inside an exception handler with a located message and a traceback.  No-code path: every preset setting is in the readme.
- [ ] Model name and package versions (or the Open WebUI version) are recorded, with `config.json`.
- [ ] Learning Log, AI-use disclosure, and (if I worked in a pair) a pair log with at least two timestamped role swaps.

---

## Learning Log

Keep a learning log for this lab in your readme.  You may answer each prompt in prose, in bullet points, or with an annotated diagram, whichever best shows your thinking.  (Prompt 4 adapts the AI-Assisted Learning Template by Marc Watkins.)

1. **What I ran.**  One paragraph a friend outside of computer science could follow.
2. **What surprised me.**
3. **What I checked and how.**  Point to a transcript, not a feeling.
4. **How I used AI during this lab**, and what I learned from that use.
5. **What I'd tell the next student** before they start.
6. **Which of the three patterns, if any, I would put in my final project**, and for which step.

