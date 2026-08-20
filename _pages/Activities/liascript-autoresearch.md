<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-autoresearch.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-autoresearch.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Supplemental Tutorial: A Threaded Auto-Research Pipeline

A single chat session researching five topics at once produces a muddy answer: every topic's context competes for the same window, and the model blends them together. Today we build the alternative — a **fan-out/fan-in pipeline**: a dispatcher hands each topic to its own worker process, each worker holds a *small, private* context while it queries a local Ollama model (optionally grounded by a local SearXNG search endpoint), and a final merge step synthesizes the per-topic summaries into a single digest. The arc: **the architecture $\rightarrow$ why small contexts beat one big context $\rightarrow$ tracing three topics through the pipeline $\rightarrow$ extending the pipeline yourself**.

This is a **supplemental tutorial** — it is not graded and no commercial API keys are required. Everything runs on the local Ollama stack you already have.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. Because this tutorial is supplemental, there is nothing to submit for a grade — but the pipeline you build here is a strong foundation for the research component of your final project. After class, respond to the reflective prompt individually in your notebook.

**Setup:** Download the working setup script at [/files/threaded-autoresearch-setup.sh](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/files/threaded-autoresearch-setup.sh) and keep it open beside this page — every model below refers to a specific section of it.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Fan-out / Fan-in** | A parallel pattern: split a job into independent pieces, process them concurrently (fan-out), then combine the results in one final step (fan-in). | Three research topics dispatched to three workers at once; one merge step assembles the digest. |
| **Worker** | An independent process that handles exactly one unit of work with its own private state. Workers never talk to each other. | `worker.py` receives one topic on its command line, queries Ollama, and writes one summary file. |
| **Small-Context-Window Principle** | Keeping each model call's prompt focused on one task rather than accumulating everything into one giant context. Smaller, cleaner contexts produce more focused output and cost fewer tokens per call. | Each worker's prompt contains one topic and (optionally) five search snippets — never the other topics. |
| **`xargs -P`** | A shell utility flag that runs up to N copies of a command concurrently, feeding each one item from standard input. The operating system schedules them across CPU cores. | `xargs -0 -n 1 -P 3 python3 worker.py` runs up to three workers at a time, one topic each. |
| **Merge (Synthesis) Step** | The fan-in stage: a single model call that reads all worker outputs and produces one coherent document. This is the only call that sees every topic. | `merge.py` concatenates `summaries/*.md` and prompts the model to write a digest with one `##` section per topic. |
| **Graceful Degradation** | Designing a pipeline to lose a feature cleanly rather than crash when an optional dependency is missing. | If no SearXNG server answers, workers skip the search step and rely on the model's parametric knowledge; if Ollama itself is absent, the script exits immediately with install instructions. |
| **SearXNG** | A self-hosted metasearch engine you can run locally (often in Docker). It exposes a JSON API, giving your pipeline live web results without any commercial search API key. | `GET http://localhost:8888/search?q=...&format=json` returns result titles and snippets the worker prepends to its prompt. |
| **Embarrassingly Parallel** | A workload whose pieces require no communication with each other, so parallel speedup is nearly free. | Research topics are independent: summarizing "quantization" never needs to wait on "prompt injection." |

---

# Part I: The Architecture

In this Part you will map the pipeline's four stages and identify which stages run concurrently, which run alone, and why the boundaries sit exactly where they do.

**Why this matters:** Almost every production LLM system that processes many items — support tickets, documents, research questions — uses this same shape. Learn it once with three topics and a shell script, and you will recognize it later inside frameworks that hide it behind classes named `MapReduceChain` or `batch()`.

## Model 1: The Pipeline Diagram

```text
                         FAN-OUT                              FAN-IN
              ┌────────────────────────────┐        ┌──────────────────────┐
              │                            │        │                      │
topics.txt ───┤  dispatcher (xargs -P 3)   │        │   merge.py           │
 topic A  ────┼──▶ worker.py A ──▶ Ollama ─┼─▶ summaries/a.md ─┐           │
 topic B  ────┼──▶ worker.py B ──▶ Ollama ─┼─▶ summaries/b.md ─┼─▶ Ollama ─┼─▶ digest.md
 topic C  ────┼──▶ worker.py C ──▶ Ollama ─┼─▶ summaries/c.md ─┘           │
              │        │                   │        │                      │
              │        └──(optional)──▶ SearXNG     └──────────────────────┘
              └────────────────────────────┘
```

Four stages, four different responsibilities:

| Stage | Program | Runs | Context it sees |
|-------|---------|------|-----------------|
| 1. Dispatch | `xargs -0 -n 1 -P $PARALLELISM` | Once | Only the topic list — never any model output |
| 2. Research | `worker.py` (one process per topic) | Concurrently, up to `PARALLELISM` at a time | One topic + up to five search snippets |
| 3. Persist | `summaries/<slug>.md` files on disk | As each worker finishes | n/a — the filesystem is the pipeline's shared memory |
| 4. Synthesize | `merge.py` | Once, after **all** workers finish | Every summary at once — the only stage that does |

### Critical Thinking Questions

1. Stage 3 is "just files on disk," yet it is doing an architectural job that a shared Python list could not do if the workers were separate OS processes. What job is that, and what would break if two workers tried to write the *same* file?

   > *Hint: Separate processes do not share memory — each worker has its own Python variables. The filesystem is the only thing they all can reach. The `slugify(topic)` function names each file after its topic; when could two topics produce the same slug, and what would the second writer do to the first writer's output?*

2. The merge step cannot start until every worker finishes. Identify which single worker determines the total pipeline runtime, and explain why adding more parallelism (`-P 10`) would not help if one topic is much slower than the rest.

   > *Hint: This is the "straggler problem." If topics A and B finish in 20 seconds but topic C takes 90 seconds, the merge waits at the barrier until C arrives. Parallelism reduces the time to run *many* items; it cannot make *one* item faster.*

3. The dispatcher never sees model output and the workers never see each other's output. List one bug class that this isolation makes *impossible*, and one bug class it does *not* protect against.

   > *Hint: Impossible: topic B's summary can never contaminate topic C's prompt, because the contexts are physically separate processes. Not protected: every worker still talks to the same Ollama server — what happens to all of them if the server is overloaded, or if the model hallucinates in the same way on every topic?*

---

# Part II: The Small-Context-Window Principle

In this Part you will compare the one-big-prompt approach against the fan-out approach on the same three topics, and connect the difference to how attention over a long context actually behaves.

**Why this matters:** "Just paste everything into one prompt" is the default instinct, and it quietly fails as input grows: instructions get diluted, topics bleed into each other, and the context window eventually overflows. Splitting work so that *each model call has one job and a small context* is the single most transferable design move in this course — you will see it again in RAG chunking, in agent handoffs, and in map-reduce summarization.

## Model 2: One Big Prompt vs. Many Small Prompts

| | One big prompt | Fan-out workers + merge |
|---|---|---|
| **Calls to Ollama** | 1 | N workers + 1 merge |
| **Context per call** | All N topics + all instructions at once | One topic each; merge sees only the finished summaries |
| **Cross-topic bleed** | Common — the model blends adjacent topics | Impossible at research stage; possible only at merge |
| **Failure blast radius** | One timeout loses everything | One worker fails; the other summaries survive on disk |
| **Wall-clock time** | One long generation | Roughly the slowest worker + the merge |
| **Where quality degrades** | Middle topics get shallow treatment ("lost in the middle") | Merge may over-compress, but each summary was written with full attention |

The worker embodies the principle in one function — this is the entire context any single research call ever sees:

```python
prompt = (f"You are a careful research assistant. {context}"
          "Write a concise, factual summary (150-250 words) of what a "
          "student should know about the topic below. Use short "
          "paragraphs and note any points you are uncertain about.\n\n"
          f"Topic: {topic}\n")
```

### Critical Thinking Questions

4. In the one-big-prompt column, why do *middle* topics tend to get the shallowest treatment? Relate your answer to what you learned about attention in the transformers module.

   > *Hint: Empirically, models attend most reliably to the beginning and end of a long context (the "lost in the middle" effect). Topic 3 of 5 sits in the least-attended region. In the fan-out design, every topic is effectively at the start of its own short prompt.*

5. The merge step is itself one big prompt over all summaries. Why is this acceptable at the merge stage when it was a problem at the research stage? What property of the workers' *output* makes the merge context manageable?

   > *Hint: The workers already compressed each topic to 150-250 words of curated text. The merge reads perhaps 750 words of high-signal input rather than doing open-ended research on all topics simultaneously. Compression before combination is the whole trick.*

6. Each worker sets its own `temperature` from an environment variable. Give one reason to run the workers at a *lower* temperature than you might use for the merge, and one reason to do the opposite.

   > *Hint: Workers are doing factual summarization — low temperature reduces embellishment. The merge is doing editorial writing — a slightly higher temperature can produce smoother connective prose. The opposite argument: the merge must not invent topics, so maybe *it* is the call to pin down.*

The primary reason each worker process keeps its own small context (rather than sharing one big conversation) is:

[( )] Small contexts make the GPU run at a lower temperature
[(X)] Each model call stays focused on exactly one topic, preventing cross-topic contamination and attention dilution
[( )] Ollama forbids more than one topic per request
[( )] Python's `requests` library cannot send prompts longer than one topic

---

# Part III: Tracing the Pipeline

In this Part you will trace three concrete topics through every stage of the running script, so that when your own run misbehaves you know exactly which file and which process to inspect.

## Model 3: Three Topics, Start to Finish

Assume `topics.txt` contains the script's three starter topics, `PARALLELISM=3`, and a SearXNG instance is running. The trace below is what actually happens, in order:

| Time | Event | Evidence you can inspect |
|------|-------|--------------------------|
| t=0 | `bash threaded-autoresearch-setup.sh` checks `ollama` on PATH, then `curl`s `$OLLAMA_URL/api/tags` | If either fails, the script exits with install/start instructions — nothing else runs |
| t=0 | Probe `GET $SEARXNG_URL/search?q=test&format=json` succeeds | `[setup] SearXNG detected ...` printed; `SEARXNG_URL` stays set |
| t=1 | `xargs -0 -n 1 -P 3` launches three `worker.py` processes, one per topic | `ps aux \| grep worker.py` shows three separate PIDs |
| t=1–2 | Each worker queries SearXNG for *its* topic, gets ≤5 snippets | Worker prompt = 1 topic + its snippets; the other two topics appear nowhere in it |
| t=2–40 | Each worker POSTs to `$OLLAMA_URL/api/generate` with `{"model": $MODEL, "options": {"temperature": $TEMPERATURE}, "stream": false}` | Ollama serves the three requests; each returns a 150–250-word summary |
| t≈40 | Workers write `summaries/retrieval-augmented-generation-....md`, `...prompt-injection....md`, `...quantization....md` and exit | Three files exist; `[worker] '<topic>' -> summaries/<slug>.md` printed per worker |
| t≈40 | `xargs` returns only after all three workers exit — this is the fan-in barrier | The shell line after `xargs` has not printed yet until now |
| t≈41 | `merge.py summaries/*.md` concatenates the three summaries with `---` separators and sends **one** synthesis prompt | The merge prompt contains all three summaries but none of the raw search snippets |
| t≈60 | `digest.md` written: overview paragraph, one `##` section per topic, `## Open Questions` | `[done] Digest written to .../digest.md` |

Now run a single worker's model call yourself to see stage 2 in isolation (requires a local Ollama server; adjust the model name to one you have pulled):

```python
import requests

topic = "quantization tradeoffs when serving LLMs on laptops"
prompt = ("You are a careful research assistant. Write a concise, factual "
          "summary (150-250 words) of what a student should know about the "
          f"topic below.\n\nTopic: {topic}\n")

r = requests.post("http://localhost:11434/api/generate",
                  json={"model": "llama3.2", "prompt": prompt,
                        "stream": False, "options": {"temperature": 0.3}},
                  timeout=300)
print(r.json()["response"])
```

### Critical Thinking Questions

7. At t≈40 the trace calls the end of `xargs` a "barrier." Suppose the prompt-injection worker crashes (its Ollama request times out). Using the trace, state exactly what the merge step will and will not contain, and where you would look first to diagnose the missing section.

   > *Hint: The other two workers still wrote their files, so `merge.py summaries/*.md` runs over two summaries instead of three — the digest silently loses a topic. First look: does `summaries/` contain two files or three? Second look: the worker's error output. What one-line check could the script add between the fan-out and the merge?*

8. The merge prompt explicitly says "Do not invent topics that are not present." Trace why this instruction exists: at which earlier stage could a topic disappear, and what would an unconstrained merge model plausibly do about a digest that "feels short"?

   > *Hint: Combine your answer to CTQ 7 with what you know about hallucination. If the model was told to expect a research digest and receives thin input, filling the gap with plausible-sounding material is exactly the failure mode of a generative model asked to be helpful.*

9. `PARALLELISM=3` matches the number of topics, so all workers start together. Predict what changes in the trace with 10 topics and `PARALLELISM=3`, and identify which single line of the script implements that scheduling behavior without any Python code.

   > *Hint: `xargs -P 3` keeps at most three workers alive at once; as each exits, xargs launches the next topic from stdin. The line is the `xargs -0 -n 1 -P "${PARALLELISM}" python3 worker.py` pipeline. The OS, not your code, does the scheduling.*

> **⚠️ Common Misconception:** Students often assume that running three workers in parallel means the model generates three answers three times faster. On a single local GPU (or CPU), Ollama largely *serializes or shares* the underlying computation — parallel workers overlap network waits, search calls, and file I/O, but the token generation itself competes for the same hardware. Fan-out buys you *pipeline* concurrency and *isolation*, not free inference speedup. Measure it (Exercise 3) rather than assuming it.

After the fan-out stage completes, the merge step's prompt contains:

[( )] The raw SearXNG snippets for every topic
[( )] The full conversation history of each worker, including its system prompt
[(X)] Only the finished per-topic summaries, concatenated with separators
[( )] Nothing — the merge step reads `topics.txt` directly and re-researches each topic

---

## Exercises

1. *Run the pipeline.* Download [threaded-autoresearch-setup.sh](https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/files/threaded-autoresearch-setup.sh), replace the starter `topics.txt` with three topics from your final project domain, and run it end to end.

   - *What to do:* `bash threaded-autoresearch-setup.sh`, then read `autoresearch/digest.md` and each file in `autoresearch/summaries/`. Compare a digest section against its source summary: what did the merge keep, cut, and rephrase?
   - *Starter hint:* If the script exits at the preflight stage, it tells you exactly what to install or start. Set `MODEL=` to any model shown by `ollama list`.
   - *You've succeeded when:* You have a digest with one section per topic plus an Open Questions section, and you can point to one concrete difference between a summary and its digest section.

2. *Add a fourth stage: critique-and-refine the digest.* Extend the pipeline with a `critique.py` stage that runs **after** the merge: one model call critiques `digest.md` (unsupported claims, missing connections, unclear prose, sections that drifted from their source summaries), and a second call rewrites the digest using the critique. This is the critique-refine pattern from earlier in the course, now applied at pipeline scale.

   - *What to do:* Copy `merge.py` to `critique.py`. First call: prompt = "You are a demanding editor. List 3-5 specific weaknesses of this digest as bullets. Digest:\n" + digest text. Second call: prompt = digest + critique + "Rewrite the digest addressing every critique point; do not add new topics." Write the result to `digest-refined.md`, and add one line to the shell script to invoke it after the merge.
   - *Starter hint:* Keep the two calls separate rather than asking for "critique then rewrite" in one prompt — you want the critique on disk so you can evaluate whether the rewrite actually addressed it.
   - *You've succeeded when:* You have `digest.md`, the critique bullets, and `digest-refined.md`, and at least one critique point is visibly fixed in the refined version.

3. *Measure the parallelism.* Time the pipeline (`time bash threaded-autoresearch-setup.sh`) with `PARALLELISM=1` and `PARALLELISM=3` on the same `topics.txt` (delete `autoresearch/summaries/*.md` between runs).

   - *What to do:* Record both wall-clock times and compute the speedup. Then explain the number using the Common Misconception box above: how much of the win came from overlapping generation vs. overlapping search/network waits?
   - *You've succeeded when:* You can report the measured speedup and give a hardware-based explanation for why it is (almost certainly) less than 3×.

4. *Grounded vs. ungrounded.* Run the same topics once with SearXNG available and once with `SEARXNG_URL=""` forced, and diff the summaries.

   - *What to do:* If you do not have SearXNG, run it locally with Docker (`docker run -d -p 8888:8080 searxng/searxng`) or simply compare against a classmate's grounded run. Look for: dates, version numbers, named systems — the concrete details parametric memory gets stale on.
   - *You've succeeded when:* You can name one claim that appears only in the grounded run and one claim you would want to verify in the ungrounded run.

---

## Reflection Prompt

*Personal:* You just delegated research to a team of workers you never watched. Recall a time you delegated a task to several people and combined their results — where did the combination step introduce errors that no individual contributor made? What does that suggest about where to focus quality control in fan-out systems?

*Technical:* The pipeline's stages communicate only through files. List two benefits and two costs of using the filesystem as the interface between stages, compared with keeping everything in one Python process with shared variables. Which choice makes the pipeline easier to debug at 2 a.m., and why?

*Societal:* This tutorial's pipeline can research dozens of topics per hour with no human reading the intermediate output. Name one setting where auto-generated research digests genuinely help (consider accessibility, small newsrooms, literature triage) and one where unreviewed synthesis at scale causes harm. What checkpoint would you make mandatory before a digest like this is shown to a decision-maker?

---

## → Coming Up Next

The pipeline you built fans work out to identical workers. The RAG modules ahead give each call something better than parametric memory to work with — retrieved passages from your own document collection — and the agent-teams material replaces identical workers with *specialized* roles that plan, execute, and critique.

---

## Further Reading

- Ollama API documentation (`/api/generate`, options, and model parameters): https://github.com/ollama/ollama/blob/main/docs/api.md
- SearXNG documentation (self-hosted metasearch with a JSON API): https://docs.searxng.org
- Dean, J. and Ghemawat, S. "MapReduce: Simplified Data Processing on Large Clusters." *OSDI* (2004) — the fan-out/fan-in pattern at datacenter scale.
- Liu et al. "Lost in the Middle: How Language Models Use Long Contexts." *TACL* (2024) — the empirical basis for the small-context-window principle.
- GNU Findutils manual, `xargs` invocation (`-P`, `-n`, `-0`): https://www.gnu.org/software/findutils/manual/html_node/find_html/Invoking-xargs.html
