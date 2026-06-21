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

In this lab you will take an existing tool-using agent and transform it from a black box into a system you can actually reason about in production. By the end, every LLM call, tool invocation, and retrieval step will emit a structured trace span that you can query, visualize, and alert on. You will work individually.

## Part 1: Baseline Agent (No Observability)

Start from the ReAct agent you built in the agent loops lab, or write a new agent that makes at least three distinct tool calls to answer a question (for example: search, fetch, summarize). Run your agent on **10 test prompts** that you write in advance and store in a JSON file. For each prompt record manually:

- Whether the final answer was correct (yes / no / partial)
- Wall-clock time from input to output (use `time.perf_counter()` or similar)

Produce a summary table with those two columns and write one paragraph describing what you **cannot** determine from this data alone: where is the time going, which tool is slow, why did run 7 fail?

## Part 2: Add OpenTelemetry Instrumentation

Install the required packages:

```
pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc
```

Start a local Jaeger all-in-one instance using the provided `docker-compose.yml` (create this file as part of your submission):

```yaml
version: "3"
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"   # Jaeger UI
      - "4317:4317"     # OTLP gRPC receiver
```

Wrap your agent with a **root tracer span** named `agent.run` that carries the attributes `session_id`, `prompt_length_chars`, and `agent_version`. Then add **child spans** for each of the following:

**LLM Call span** (`llm.call`): attributes must include `llm.model`, `llm.prompt_tokens`, `llm.completion_tokens`, `llm.finish_reason`, `llm.latency_ms`. Do **not** store the raw prompt text as an attribute; store only its character length.

**Tool Call span** (`tool.call`): attributes must include `tool.name`, `tool.input_length_chars`, `tool.success` (boolean), `tool.latency_ms`. If the tool raises an exception, record the exception on the span using `span.record_exception(e)` and set status to `ERROR`.

**Retrieval Call span** (`retrieval.call`, required only if your agent uses a vector store or web search): attributes must include `retrieval.num_results`, `retrieval.top_score`, `retrieval.latency_ms`.

All spans must be properly nested (child spans created inside a `with tracer.start_as_current_span(...)` block under the parent) and must export to the Jaeger OTLP endpoint at `http://localhost:4317`.

## Part 3: Trace Analysis

Re-run the same 10 prompts with instrumentation active. Open the Jaeger UI at `http://localhost:16686` and answer each of the following questions in your writeup. You must cite specific span names, attribute values, or timestamps from your traces as evidence:

**(a) Latency hotspot:** Which span has the highest p95 latency across your 10 runs? Report the p95 value in milliseconds and name the span. If Jaeger does not compute p95 directly, approximate it by sorting the 10 latency values for that span type.

**(b) Failure analysis:** Identify at least one failed or degraded trace. At which span did the trace diverge from the pattern of successful traces (different duration, missing child span, error status)? What does this tell you about the root cause?

**(c) Optimization proposal:** Based on trace evidence, propose one concrete optimization. Acceptable proposals include: cache the output of a retrieval span whose input recurs across runs; route the first tool call to a smaller and faster model; parallelize two independent tool calls. State the evidence from your traces that motivates the proposal and estimate the expected latency reduction.

Include **two screenshots** from the Jaeger UI: one of the fastest trace across your 10 runs, and one of the slowest or most error-prone. Annotate each screenshot with callout labels or arrows identifying the key spans.

## Part 4: Alerting Rules

Design **three alert rules** using either pseudocode or valid Prometheus AlertManager YAML. The three rules must cover:

1. **Latency alert:** Agent p95 end-to-end latency exceeds 5 seconds over a 5-minute window.
2. **Error rate alert:** Agent error rate (traces ending in ERROR status) exceeds 5% in any 10-minute window.
3. **Cost anomaly alert:** Any single request where `llm.prompt_tokens` exceeds 2000 tokens, which may indicate a runaway context accumulation bug.

For each rule, state the threshold and justify it: why is 5 seconds the right cutoff for your use case, and what would happen if it were set to 1 second or 30 seconds instead?

Then write a **1-page operations runbook** structured as three sections, one per alert. Each section must answer: What does this alert mean? Which span or attribute do you look at first in Jaeger? What are the three most likely root causes and how do you distinguish between them? When do you escalate versus self-resolve?

## Deliverables

Submit a ZIP file containing:

- Instrumented agent source code (`agent.py` and any supporting modules)
- `docker-compose.yml` for Jaeger
- `prompts.json` (your 10 test prompts with expected answers)
- `baseline_results.csv` (Part 1 table)
- Two annotated Jaeger screenshots (PNG or PDF, labeled `trace_fast.png` and `trace_slow.png`)
- `alert_rules.yaml` or `alert_rules.txt`
- `runbook.md` (approximately one page)
- A `writeup.md` with your trace analysis answers (Part 3 a/b/c) and reflection answers

## Reflection Prompts

- Which span attribute turned out to be the most diagnostically useful across your 10 runs? Which attribute added the most noise without helping you understand anything? What would you remove or rename?
- Your traces contain the character lengths of user prompts. Even without storing the raw text, what inferences about user behavior could someone draw from a sequence of prompt lengths, and is that a PII risk? How would you mitigate it?
- Approximately how many hours did this lab take (I will not judge you for this; I use it to calibrate assignment difficulty)?
