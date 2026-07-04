---
layout: assignment
permalink: /Assignments/Observability
title: "CS357: Foundations of Artificial Intelligence - Lab: Instrumenting Agents with OpenTelemetry"

info:
  coursenum: CS357
  points: 100
  goals:
    - To instrument an AI agent with OpenTelemetry spans, capturing LLM call metadata, tool call metadata, and retrieval metadata as structured attributes
    - To design span attribute schemas that balance diagnostic value against verbosity and PII exposure
    - To analyze distributed traces in Jaeger or Zipkin to locate latency hotspots and diagnose failure modes
    - To write operational alert rules and a runbook that translates trace-derived thresholds into on-call actions
  rubric:
    - weight: 25
      description: Instrumentation
      preemerging: No OpenTelemetry spans are added, or the agent fails to export any traces to the backend
      beginning: A root span is added but child spans for LLM calls or tool calls are missing or incorrectly nested
      progressing: Root and child spans are present with attributes exported to Jaeger or Zipkin, but some required attributes such as prompt_tokens or finish_reason are absent or mis-typed
      proficient: Root span, LLM child spans, tool call child spans, and retrieval spans (if applicable) are all present, correctly nested, and export the full required attribute set to the running Jaeger or Zipkin instance via the supplied docker-compose file
    - weight: 25
      description: Span Design
      preemerging: Span attributes are absent or consist only of generic string labels with no diagnostic value
      beginning: Some attributes are present but attribute names do not follow OpenTelemetry semantic conventions, or high-cardinality values such as full prompt text are stored without redaction
      progressing: Attributes follow a consistent naming convention and cover the required fields, with a brief rationale for each attribute in the writeup
      proficient: Attribute schema is documented with naming rationale, cardinality justification, and explicit identification of at least one attribute that was removed or redacted due to PII risk or excessive cardinality
    - weight: 25
      description: Trace Analysis
      preemerging: No trace analysis is provided, or the Jaeger UI screenshots are absent
      beginning: Screenshots are included but analysis consists only of restating visible numbers without interpretation or a proposed optimization
      progressing: p95 latency is identified, at least one failure trace is examined, and an optimization is proposed, but the proposal lacks supporting trace evidence
      proficient: p95 latency span is identified with supporting data, failure traces are compared to success traces with a specific divergence point named, and a concrete optimization is proposed and justified with trace evidence, accompanied by one fast and one slow trace screenshot
    - weight: 25
      description: Alerting and Documentation
      preemerging: No alert rules or runbook are provided
      beginning: Alert rules are provided in pseudocode but thresholds are not justified, or the runbook lists steps without linking them to specific spans or metrics
      progressing: Three alert rules with justified thresholds are provided in pseudocode or Prometheus YAML, and the runbook covers two of the three alerts with actionable steps
      proficient: Three alert rules are provided with justified thresholds in valid pseudocode or Prometheus AlertManager YAML, and the runbook covers all three alerts with specific span names, attribute values to inspect, and escalation criteria
  readings:
    - rtitle: "Observability Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-observability.md"

tags:
  - observability
  - opentelemetry
  - monitoring

---

In this lab you will take an existing tool-using agent and transform it from a black box into a system you can actually reason about in production. By the end, every LLM call, tool invocation, and retrieval step will emit a structured **trace span** (a timed, named record of a unit of work, carrying key-value attributes) that you can query, visualize, and alert on. You will work individually.

## Before You Start

### Prerequisite Checklist

Before beginning Part 1, confirm you have completed or have access to the following:

- [ ] The ReAct agent lab (or you can write a new agent with at least 3 tool calls)
- [ ] Python 3.10 or later (`python --version`)
- [ ] Docker Desktop installed and running (`docker info`)
- [ ] A working OpenAI or Anthropic API key set in your environment

### Environment Setup

Run these commands in order and verify each expected output before continuing:

**Step 1: Install Python dependencies**

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc
```

Expected output (last few lines):
```
Successfully installed opentelemetry-api-1.x.x opentelemetry-sdk-1.x.x \
  opentelemetry-exporter-otlp-proto-grpc-1.x.x
```

**Step 2: Start Jaeger (the trace visualization backend)**

Create a file called `docker-compose.yml` with this content:

```yaml
version: "3"
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"   # Jaeger UI — open this in your browser
      - "4317:4317"     # OTLP gRPC receiver — your agent sends traces here
```

Then start it:

```bash
docker compose up -d
```

Expected output:
```
[+] Running 2/2
 ✔ Network lab_default    Created
 ✔ Container lab-jaeger-1 Started
```

**Step 3: Quick sanity check — confirm Jaeger is running**

```bash
curl -s http://localhost:16686/api/services | python -m json.tool | head -5
```

Expected output:
```json
{
    "data": [],
    "total": 0,
    "limit": 0,
    "offset": 0,
```

If you see `Connection refused`, Docker is not exposing port 16686. Check `docker ps` to confirm the container is running.

---

## Part 1: Baseline Agent (No Observability)

**Why this matters:** Before adding instrumentation, you need a clear record of what you *cannot* see. This Part creates the "before" picture that makes the "after" in Part 3 meaningful.

Start from the ReAct agent you built in the agent loops lab, or write a new agent that makes at least three distinct tool calls to answer a question (for example: search, fetch, summarize).

### Steps

1. **Create your test prompts file.** Write 10 prompts that exercise your agent and save them to `prompts.json`:

```json
[
  {
    "id": "p01",
    "question": "What is the capital of France?",
    "expected_answer": "Paris"
  },
  {
    "id": "p02",
    "question": "Summarize the last paragraph of https://example.com",
    "expected_answer": "..."
  }
]
```

2. **Run each prompt and record results manually.** Use this starter script to time your agent:

```python
# baseline_runner.py
import json
import time
import csv

# TODO: import your agent — replace the line below with your actual import
# from my_agent import run_agent

def run_agent(question: str) -> str:
    # TODO: replace this stub with a call to your actual agent
    # Example: return your_agent.run(question)
    raise NotImplementedError("Replace this with your agent call")

with open("prompts.json") as f:
    prompts = json.load(f)

results = []
for item in prompts:
    start = time.perf_counter()
    answer = run_agent(item["question"])
    elapsed_ms = (time.perf_counter() - start) * 1000

    correct = input(f"\nQ: {item['question']}\nA: {answer}\nCorrect? (y/n/partial): ")
    results.append({
        "id": item["id"],
        "correct": correct,
        "latency_ms": round(elapsed_ms, 1)
    })

with open("baseline_results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "correct", "latency_ms"])
    writer.writeheader()
    writer.writerows(results)

print("Saved baseline_results.csv")
```

Expected output after running all 10 prompts:
```
Saved baseline_results.csv
```

3. **Produce your summary table.** Open `baseline_results.csv` and verify it has 10 rows with `id`, `correct`, and `latency_ms` columns.

4. **Write one paragraph** (in your `writeup.md`) describing what you *cannot* determine from this data alone: Where is the time going? Which tool is slow? Why did run 7 fail?

> **Checkpoint:** Before moving on, verify that `baseline_results.csv` exists, has exactly 10 rows, and that you can answer the question "which of my 10 runs was the slowest?" from the data alone.

> **Troubleshooting:** If your agent raises an ImportError, make sure you are running from the same directory as your agent file or that it is on your PYTHONPATH. If `time.perf_counter()` gives you a suspiciously small number, remember the value is in seconds — multiply by 1000 for milliseconds as shown above. If `input()` hangs in a notebook environment, replace it with a hardcoded `"y"` for now and update manually.

---

## Part 2: Add OpenTelemetry Instrumentation

**Why this matters:** OpenTelemetry (OTel) is the industry-standard, vendor-neutral framework for adding structured observability to any application. Adding it here means your agent emits traces compatible with Jaeger, Grafana, Datadog, and dozens of other backends — the same skill used at every major tech company.

### Steps

1. **Create `agent.py`** (or adapt your existing agent file) using this skeleton. Fill in every `# TODO` comment:

```python
# agent.py  — OpenTelemetry-instrumented agent skeleton
import time
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import StatusCode

# ── Configure the tracer to export to local Jaeger ──────────────────────────
provider = TracerProvider()
exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("my-agent")

# TODO: import your LLM client and tool functions here
# Example: from openai import OpenAI; client = OpenAI()

def call_llm(prompt: str, session_id: str) -> dict:
    """Wraps an LLM call in an llm.call span."""
    with tracer.start_as_current_span("llm.call") as span:
        start = time.perf_counter()

        # TODO: replace the stub below with your real LLM call
        # response = client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # result_text = response.choices[0].message.content
        # prompt_tokens = response.usage.prompt_tokens
        # completion_tokens = response.usage.completion_tokens
        # finish_reason = response.choices[0].finish_reason
        raise NotImplementedError("Replace this stub with your LLM call")

        latency_ms = (time.perf_counter() - start) * 1000

        # TODO: set required span attributes — do NOT store raw prompt text
        span.set_attribute("llm.model", "gpt-4o-mini")           # model name
        span.set_attribute("llm.prompt_tokens", prompt_tokens)
        span.set_attribute("llm.completion_tokens", completion_tokens)
        span.set_attribute("llm.finish_reason", finish_reason)
        span.set_attribute("llm.latency_ms", round(latency_ms, 1))
        # Store only length, not the raw prompt (privacy!)
        span.set_attribute("llm.prompt_length_chars", len(prompt))

        return {"text": result_text, "tokens": prompt_tokens + completion_tokens}


def call_tool(tool_name: str, tool_input: str) -> str:
    """Wraps a tool call in a tool.call span."""
    with tracer.start_as_current_span("tool.call") as span:
        start = time.perf_counter()
        span.set_attribute("tool.name", tool_name)
        span.set_attribute("tool.input_length_chars", len(tool_input))
        try:
            # TODO: dispatch to your actual tool implementations
            # Example:
            # if tool_name == "web_search":
            #     result = web_search(tool_input)
            # elif tool_name == "fetch_url":
            #     result = fetch_url(tool_input)
            # else:
            #     raise ValueError(f"Unknown tool: {tool_name}")
            raise NotImplementedError(f"Implement dispatch for tool: {tool_name}")

            latency_ms = (time.perf_counter() - start) * 1000
            span.set_attribute("tool.success", True)
            span.set_attribute("tool.latency_ms", round(latency_ms, 1))
            return result
        except Exception as e:
            # TODO: add child span for each tool call with tool.name, tool.success attributes
            span.record_exception(e)
            span.set_status(StatusCode.ERROR, str(e))
            span.set_attribute("tool.success", False)
            raise


def call_retrieval(query: str, vector_store) -> list:
    """Wraps a vector store retrieval in a retrieval.call span.
    Only needed if your agent uses a vector store or web search."""
    with tracer.start_as_current_span("retrieval.call") as span:
        start = time.perf_counter()

        # TODO: replace with your actual retrieval call
        # results = vector_store.similarity_search(query, k=5)
        raise NotImplementedError("Replace with your vector store call")

        latency_ms = (time.perf_counter() - start) * 1000
        span.set_attribute("retrieval.num_results", len(results))
        # TODO: set retrieval.top_score if your store returns similarity scores
        span.set_attribute("retrieval.top_score", results[0].score if results else 0.0)
        span.set_attribute("retrieval.latency_ms", round(latency_ms, 1))
        return results


def run_agent(question: str, session_id: str) -> str:
    """Root span wrapping the entire agent run."""
    with tracer.start_as_current_span("agent.run") as root_span:
        root_span.set_attribute("session_id", session_id)
        root_span.set_attribute("prompt_length_chars", len(question))
        root_span.set_attribute("agent_version", "1.0.0")

        # TODO: implement your ReAct loop here, calling call_llm() and call_tool()
        # Each call_llm / call_tool call automatically becomes a child span
        # because they are entered while agent.run is the current span
        raise NotImplementedError("Implement your agent loop here")


if __name__ == "__main__":
    import uuid
    answer = run_agent("What is the capital of France?", session_id=str(uuid.uuid4()))
    print(answer)
```

2. **Run a single test prompt** and verify a trace appears in Jaeger:

```bash
python agent.py
```

3. **Open Jaeger UI** at `http://localhost:16686`. In the "Service" dropdown, select `my-agent`. Click "Find Traces". You should see one trace.

Expected output in Jaeger: A trace with an `agent.run` root span containing nested `llm.call` and `tool.call` child spans, all with durations displayed in milliseconds.

4. **Verify span nesting.** Click into the trace. The hierarchy should look like:

```
agent.run (total: ~2000ms)
  ├─ llm.call (800ms)
  ├─ tool.call [web_search] (600ms)
  ├─ llm.call (400ms)
  └─ tool.call [fetch_url] (200ms)
```

If all spans show at the same level (no nesting), the child spans are not being created inside a `with tracer.start_as_current_span(...)` block under the parent. Fix the nesting.

> **Checkpoint:** Before moving on, verify that the Jaeger UI shows at least one trace for your agent, that the trace has a root `agent.run` span with nested child spans, and that clicking a child span shows attributes like `llm.model` or `tool.name` in the "Tags" panel.

> **Troubleshooting:** If no traces appear in Jaeger, run `docker ps` to confirm the container is running and `curl http://localhost:4317` to confirm the port is reachable. If you get `StatusCode.UNAVAILABLE` in Python, the OTLP exporter cannot reach Jaeger — double-check that `endpoint="http://localhost:4317"` and `insecure=True` are set. If spans appear but are not nested, make sure your `call_llm` and `call_tool` functions are called *inside* the `with tracer.start_as_current_span("agent.run")` block, not before or after it.

---

## Part 3: Trace Analysis

**Why this matters:** Collecting traces is only useful if you can read them. This Part builds the core skill of distributed trace analysis — the same skill used by SREs to diagnose production incidents in minutes rather than hours.

Re-run the same 10 prompts with instrumentation active. Open the Jaeger UI at `http://localhost:16686` and answer each question below in your `writeup.md`. You must cite specific span names, attribute values, or timestamps from your traces as evidence.

### Steps

1. **Run all 10 prompts** with tracing active:

```bash
python -c "
import json, uuid
from agent import run_agent

with open('prompts.json') as f:
    prompts = json.load(f)

for item in prompts:
    print(f'Running {item[\"id\"]}...')
    run_agent(item['question'], session_id=str(uuid.uuid4()))
print('Done. Open http://localhost:16686 to inspect traces.')
"
```

Expected output:
```
Running p01...
Running p02...
...
Running p10...
Done. Open http://localhost:16686 to inspect traces.
```

2. **Answer the following questions** in your writeup, citing span names and attributes as evidence:

**(a) Latency hotspot:** Which span type has the highest p95 latency across your 10 runs? Report the p95 value in milliseconds. If Jaeger does not compute p95 directly, sort the 10 latency values for that span type and report the 9th-highest (the 95th percentile of 10 samples).

**(b) Failure analysis:** Identify at least one failed or degraded trace. At which span did the trace diverge from the pattern of successful traces (different duration, missing child span, error status)? What does this tell you about the root cause?

**(c) Optimization proposal:** Based on trace evidence, propose one concrete optimization such as: caching the output of a retrieval span whose input recurs across runs; routing the first tool call to a smaller, faster model; or parallelizing two independent tool calls. State the evidence and estimate the expected latency reduction.

3. **Take two screenshots** from the Jaeger UI:
   - `trace_fast.png`: your fastest trace across the 10 runs
   - `trace_slow.png`: your slowest or most error-prone trace
   
   Annotate each with callout labels or arrows identifying the key spans.

> **Checkpoint:** Before moving on, verify that you have answered all three questions (a/b/c) with specific span names or attribute values as evidence, and that both screenshot files exist and are annotated.

> **Troubleshooting:** If you see fewer than 10 traces in Jaeger, some runs may have failed silently — check your Python terminal output for tracebacks. If the "Service" dropdown in Jaeger is empty, the `service.name` resource attribute was not set on your `TracerProvider`. Add `Resource.create({"service.name": "my-agent"})` to your provider configuration. If all traces look identical and you cannot identify a slow one, add a small `time.sleep(random.uniform(0, 1))` in one tool to simulate variability.

---

## Part 4: Alerting Rules

**Why this matters:** Traces you can only see in a dashboard are not enough in production — you need automated alerts that page you when something breaks at 3 AM. This Part bridges observability and incident response.

### Steps

1. **Design three alert rules** using either pseudocode or valid Prometheus AlertManager YAML. The three rules must cover:

   - **Latency alert:** Agent p95 end-to-end latency exceeds 5 seconds over a 5-minute window.
   - **Error rate alert:** Agent error rate (traces ending in ERROR status) exceeds 5% in any 10-minute window.
   - **Cost anomaly alert:** Any single request where `llm.prompt_tokens` exceeds 2000 tokens, which may indicate a runaway context accumulation bug.

   Here is a Prometheus AlertManager YAML template to adapt:

   ```yaml
   # alert_rules.yaml
   groups:
     - name: agent_alerts
       rules:
         - alert: AgentHighLatency
           # TODO: replace the expr with a real PromQL query referencing your span latency metric
           expr: histogram_quantile(0.95, rate(agent_span_duration_ms_bucket{span_name="agent.run"}[5m])) > 5000
           for: 5m
           labels:
             severity: warning
           annotations:
             summary: "Agent p95 latency above 5s"
             # TODO: add a description explaining what to check first in Jaeger

         - alert: AgentHighErrorRate
           # TODO: replace with your actual error rate metric
           expr: rate(agent_spans_total{status="ERROR"}[10m]) / rate(agent_spans_total[10m]) > 0.05
           for: 10m
           labels:
             severity: critical
           annotations:
             summary: "Agent error rate above 5%"

         - alert: AgentTokenSpike
           # TODO: replace with your actual token metric
           expr: agent_llm_prompt_tokens > 2000
           labels:
             severity: warning
           annotations:
             summary: "Single request exceeded 2000 prompt tokens"
   ```

2. **Justify each threshold** in your `writeup.md`: Why is 5 seconds the right cutoff? What would happen if it were set to 1 second (too noisy) or 30 seconds (too slow to respond)?

3. **Write a 1-page operations runbook** (`runbook.md`) structured as three sections, one per alert. Each section must answer:
   - What does this alert mean?
   - Which span or attribute do you look at first in Jaeger?
   - What are the three most likely root causes and how do you distinguish between them?
   - When do you escalate versus self-resolve?

> **Checkpoint:** Before moving on, verify that `alert_rules.yaml` (or `alert_rules.txt`) exists and that `runbook.md` has three sections with all four questions answered for each alert.

> **Troubleshooting:** If you are unsure what PromQL metric names to use, you can write pseudocode alerts using plain English descriptions of the condition — the rubric accepts both. If your thresholds feel arbitrary, look at your actual p95 latency from Part 3 and set the alert at 2x that value as a starting point.

---

## Extension Challenges (optional)

These challenges are not required for full credit, but they push the lab from classroom exercise to production-grade observability.

**Extension 1: Add a Grafana dashboard.** Add Grafana and Prometheus to your `docker-compose.yml` and build a dashboard that shows p50/p95/p99 latency per span type, error rate, and token count over time. Export the dashboard as `grafana_dashboard.json`.

**Extension 2: Implement trace sampling.** Add a `TraceIdRatioBased` sampler to your `TracerProvider` that samples 50% of traces. Run 100 prompts and compare the sampled trace set to the full set. Does the p95 estimate change significantly? When would you use sampling in production?

**Extension 3: Add a Slack alert.** Write a Python script that polls the Jaeger API for ERROR-status traces every 60 seconds and posts a formatted message to a Slack webhook when it finds one. Include the trace ID, failing span name, and error message in the Slack message.

---

## Deliverables

Submit a ZIP file containing:

- `agent.py` and any supporting modules (instrumented, runnable)
- `docker-compose.yml` for Jaeger
- `prompts.json` (10 test prompts with expected answers)
- `baseline_results.csv` (Part 1 table: id, correct, latency_ms)
- `trace_fast.png` and `trace_slow.png` (annotated Jaeger screenshots)
- `alert_rules.yaml` or `alert_rules.txt`
- `runbook.md` (approximately one page, three sections)
- `trace_schema.md` (document each span type and its attributes, with cardinality justification and any attributes removed for PII reasons)
- `writeup.md` with your Part 3 trace analysis answers (a/b/c) and reflection answers

## Submission Checklist

- [ ] `agent.py` runs without error and exports traces to Jaeger
- [ ] `docker-compose.yml` starts Jaeger with `docker compose up -d`
- [ ] `prompts.json` contains exactly 10 prompts
- [ ] `baseline_results.csv` contains exactly 10 rows
- [ ] Jaeger UI shows traces with correctly nested `agent.run`, `llm.call`, and `tool.call` spans
- [ ] `trace_fast.png` and `trace_slow.png` are annotated with span labels
- [ ] `alert_rules.yaml` contains three alert rules with justified thresholds
- [ ] `runbook.md` covers all three alerts with span names, root causes, and escalation criteria
- [ ] `trace_schema.md` documents each span type, attribute cardinality, and PII decisions
- [ ] `writeup.md` answers Part 3 (a), (b), (c) with specific trace evidence
- [ ] Reflection prompts answered in `writeup.md`

## Reflection Prompts

- Which span attribute turned out to be the most diagnostically useful across your 10 runs? Which attribute added the most noise without helping you understand anything? What would you remove or rename?
- Your traces contain the character lengths of user prompts. Even without storing the raw text, what inferences about user behavior could someone draw from a sequence of prompt lengths, and is that a PII risk? How would you mitigate it?
- Approximately how many hours did this lab take (I will not judge you for this; I use it to calibrate assignment difficulty)?
