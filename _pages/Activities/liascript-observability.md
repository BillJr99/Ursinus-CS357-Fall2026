# Agent Observability and Tracing
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-observability.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-observability.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Agent Observability and Tracing

A deployed agent that silently fails is worse than one that visibly crashes. A crash produces an error message and a stack trace. Silent failure produces a wrong answer, a missed tool call, or a hallucination — and the operator has no idea it happened. **Observability** is the discipline of making the internal state of a system legible from the outside, so that you can ask arbitrary questions about its behavior without knowing in advance what questions you will need to ask. This activity introduces the three pillars of observability, distributed tracing for agent pipelines, and the OpenTelemetry standard for instrumenting LLM applications.

---

## Directions and Group Roles

Work in your POGIL team of four with clearly assigned roles:

- **Manager**: Keeps the group on task and on time; ensures everyone contributes before moving on.
- **Recorder**: Documents the group's answers and posts the final responses to the Class Activity Questions discussion board.
- **Presenter**: Speaks for the group during debrief; articulates areas of genuine disagreement or alternative interpretations.
- **Reflector**: Monitors group process and captures lessons learned for the reflection prompt.

Consider each model and its questions individually before discussing with your group. The goal is to build a shared mental model, not to reach consensus quickly.

---

## Model 1: The Three Pillars of Observability

Observability in distributed systems is built on three complementary data types. No single pillar is sufficient on its own; together they provide a complete picture of system behavior.

| Pillar | What It Captures | Time Granularity | Best For | Example Tool |
|:-------|:-----------------|:----------------|:---------|:-------------|
| **Logs** | Discrete events with a timestamp, severity level, and message payload; may include structured key-value fields | Per-event (arbitrary resolution) | Debugging a specific failure; auditing what the agent said or did at a moment in time | Loki, Elasticsearch, CloudWatch Logs |
| **Metrics** | Numeric measurements aggregated over time (counters, gauges, histograms); e.g., request rate, error rate, token consumption per minute | Aggregated (typically 1s–1m buckets) | Alerting on threshold violations; capacity planning; trend analysis over hours or days | Prometheus, Datadog, InfluxDB |
| **Traces** | Causally linked spans representing the end-to-end execution of a single request through multiple services or steps | Per-request (sub-millisecond resolution on individual spans) | Root-cause analysis across multiple hops; identifying which step in a pipeline added latency | Jaeger, Zipkin, Honeycomb |

**Key insight**: A metric can tell you that error rate increased at 2:00 PM; a log can tell you the exact error message for one failing request; a trace can tell you which step in the agent pipeline caused that request to fail and how long each step took.

### Critical Thinking Questions

1. An agent processes 10,000 requests per day. If you logged the full input prompt and output for every request, what storage and privacy problems would that create? What would you log instead?

2. A metric shows that 95th-percentile latency for your agent doubled between Tuesday and Wednesday. Explain why a metric alone cannot tell you *why* this happened, and what you would look at next.

3. Logs, metrics, and traces all have associated costs: storage, compute, and egress. If you had to pick only two of the three pillars for an MVP deployment of a new agent, which two would you choose and why? What visibility would you be giving up?

---

## Model 2: Distributed Tracing for Agent Pipelines

When an agent receives a query, it may invoke a retriever, call an LLM, execute a tool, and format a response — each of these is a **span** in a **trace**. A span records its start time, end time, parent span, and any attributes (key-value metadata). The spans are linked by a common trace ID, so you can visualize the entire causal chain for a single request.

Below is the span tree for an agent handling a Retrieval-Augmented Generation (RAG) query:

```
[root span] handle_query   duration: 2340ms
│   attributes: user_id=u-42, query_hash=a3f9...
│
├── [child] retrieve       duration: 410ms
│       attributes: vector_db=pinecone, top_k=5, db_latency_ms=388
│
├── [child] llm_generate   duration: 1710ms
│       attributes: model=hermes-3, prompt_tokens=1842,
│                  completion_tokens=317, finish_reason=stop
│
└── [child] tool_call      duration: 180ms
        attributes: tool_name=search_web, success=true,
                   result_chars=4200
```

Attributes on spans are the primary mechanism for answering questions about production behavior. They turn a timing graph into a searchable, filterable record of what the agent did. However, attributes must be chosen carefully: they are stored in your tracing backend, may be retained for weeks, and may be exported to third-party vendors.

### Critical Thinking Questions

4. Looking at the span tree above, the `llm_generate` span consumed 73% of the total request duration. Before you decide to optimize the LLM call, what information would you need to determine whether that latency is acceptable or problematic?

5. A teammate suggests adding a `prompt_text` attribute to the `llm_generate` span so you can inspect what was sent to the model during debugging. Identify at least two categories of information that might appear in a RAG prompt that would be inappropriate to store in a tracing backend. How would you get the debugging benefit without the privacy risk?

6. The `retrieve` span shows `db_latency_ms=388` out of a total span duration of 410ms. The remaining 22ms is presumably Python overhead. If you needed to reduce retrieval latency by 50%, what options would you consider, and how would you use the span data to validate that a change worked?

---

## Model 3: OpenTelemetry Integration

**OpenTelemetry** (OTel) is a vendor-neutral open standard for collecting and exporting telemetry data (traces, metrics, and logs) from applications. It provides a unified API and SDK so you can instrument your agent once and export to any compatible backend (Jaeger, Honeycomb, Grafana Tempo, etc.) by changing configuration, not code.

The following pseudocode shows how to wrap an agent invocation with OpenTelemetry tracing in Python:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# --- Setup (done once at application startup) ---
provider = TracerProvider()
exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("cs357.agent")

# --- Per-request instrumentation ---
def handle_query(user_query: str, user_id: str) -> str:
    with tracer.start_as_current_span("handle_query") as root:
        root.set_attribute("user_id", user_id)
        root.set_attribute("query_length", len(user_query))

        with tracer.start_as_current_span("llm_generate") as llm_span:
            response = call_llm(user_query)
            llm_span.set_attribute("model_name", response.model)
            llm_span.set_attribute("prompt_tokens", response.usage.prompt_tokens)
            llm_span.set_attribute("completion_tokens", response.usage.completion_tokens)
            llm_span.set_attribute("finish_reason", response.finish_reason)

        return response.text
```

For **SLA tracking**, the attributes you instrument determine what you can measure. A service level agreement (SLA) might specify: "95th-percentile latency under 2 seconds," "error rate below 0.1%," or "completion token usage under 500 per request." Each of these requires a specific attribute to be present on spans.

[[MC]]
A production agent is silently failing on approximately 8% of queries — users receive a response, but it is unhelpful or factually wrong. There are currently no logs, metrics, or traces in place. Which observability pillar would you add FIRST to diagnose this problem?

- ( ) Metrics — aggregate error rates will tell you exactly which requests failed
- ( ) Traces — the span tree will immediately reveal which model produced the wrong answer
- (x) Logs — structured per-request logging of the input, model response, and finish reason gives you the raw evidence needed to identify patterns in the failures before you know what to measure
- ( ) All three simultaneously — you cannot diagnose anything without all pillars in place

### Critical Thinking Questions

7. The SLA requires "95th-percentile latency under 2 seconds." Which span attributes in the pseudocode above are strictly necessary to track this SLA, and which are nice-to-have for debugging but not required for the SLA metric itself?

8. The `finish_reason` attribute can take values like `stop` (normal completion), `length` (truncated by token limit), or `content_filter` (blocked by safety). Why is `finish_reason` particularly important for detecting quality regressions in production, and what alert rule would you write using it?

9. The exporter sends trace data to an OTLP endpoint at `http://otel-collector:4317`. In a production system, what security concerns does this exporter URL raise, and what would you change about it?

---

## Exercises

1. **Trace tree design.** A 3-step ReAct loop for a research agent consists of: (1) the agent deciding to search the web, (2) executing the web search tool, (3) the agent synthesizing results and deciding whether to search again or answer. Draw the full span tree for one complete ReAct iteration that ends with an answer. Label each span with its name, key attributes, and approximate duration. Indicate which spans are children of which.

2. **PII audit.** Review the following list of candidate span attributes and classify each as "safe to store in traces," "store with caution (explain why)," or "do not store (explain why)": `user_id`, `full_prompt_text`, `retrieved_document_ids`, `retrieved_document_content`, `model_name`, `finish_reason`, `user_email`, `response_text`, `session_duration_ms`, `ip_address`.

3. **Alert design.** You are the on-call engineer for a deployed advising agent at a university. Design an alerting policy: specify (a) which metric or trace attribute to monitor, (b) the threshold value that triggers the alert, (c) the time window over which the threshold is evaluated, (d) who gets paged, and (e) what the first step of the runbook is. Consider at least three separate alert rules for different failure modes.

---

## Reflection Prompt

In your notebook: what would you need to observe to prove — not just believe, but demonstrate with evidence — that your agent is NOT hallucinating in production? Describe the specific logs, metrics, or trace attributes you would collect, how you would analyze them, and what limitation you would still have even with perfect observability in place.

---

## Further Reading

- OpenTelemetry Documentation: https://opentelemetry.io/docs/
- OpenTelemetry Semantic Conventions for LLMs (GenAI): https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Honeycomb. "Observability Engineering." O'Reilly Media, 2022.
- Charity Majors. "Observability — the Big Picture." https://charity.wtf/2020/03/03/observability-is-a-many-splendored-thing/
- Jaeger Distributed Tracing: https://www.jaegertracing.io/
