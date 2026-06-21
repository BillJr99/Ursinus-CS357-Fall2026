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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|:-----|:------------------------|:------------------------|
| **Observability** | The ability to understand what a system is doing on the inside by looking at its outputs — without having to guess or modify the code | Knowing which step of your RAG pipeline caused a slow response, just by reading the trace data |
| **Trace** | A recording of every step a single request takes as it flows through your system, stitched together with a shared ID | One user asking your agent a question produces one trace with child spans for retrieval, LLM call, and tool use |
| **Span** | A single timed unit of work inside a trace — like one function call — that records its start time, end time, and metadata attributes | The `llm_generate` span that records how many tokens were used and why the model stopped generating |
| **Metric** | A number that is measured repeatedly over time and aggregated — such as a count, average, or histogram | "Error rate rose from 1% to 8% between Tuesday and Wednesday" |
| **Log** | A timestamped record of a specific event, written in text (structured or plain), that describes something that happened at a moment in time | "2025-09-15T14:03:22Z ERROR finish_reason=content_filter query_hash=a3f9" |
| **OpenTelemetry (OTel)** | An open standard that defines a single API for collecting traces, metrics, and logs so you can swap backends without rewriting your instrumentation code | Instrument once with OTel; export to Jaeger, Honeycomb, or Grafana by changing one config line |

---

## Model 1: The Three Pillars of Observability

> **Why this matters:** Flying an agent without traces is like flying a plane with no instruments — you only know something's wrong when you crash. In production, your agent will fail in ways you did not anticipate. The three pillars below are your cockpit instruments: they let you see the problem, measure its scale, and trace it to its source before a user reports it.

Observability in distributed systems is built on three complementary data types. No single pillar is sufficient on its own; together they provide a complete picture of system behavior.

| Pillar | What It Captures | Time Granularity | Best For | Example Tool | In Our Course |
|:-------|:-----------------|:----------------|:---------|:-------------|:--------------|
| **Logs** | Discrete events with a timestamp, severity level, and message payload — may include structured key-value fields such as `user_id`, `finish_reason`, or `error_code` | Per-event at arbitrary resolution — every event gets its own entry the moment it happens | Debugging a specific failure after the fact; auditing exactly what the agent said or did at a given moment; investigating a complaint from a specific user | Loki, Elasticsearch, CloudWatch Logs | Printing `finish_reason` and `query_hash` to a structured log file every time your agent handles a request |
| **Metrics** | Numeric measurements aggregated over time — counters (how many requests), gauges (current queue depth), and histograms (distribution of latencies); e.g., request rate, error rate, token consumption per minute | Aggregated over fixed time buckets, typically one second to one minute — you see trends, not individual events | Alerting when a threshold is violated (e.g., error rate > 1%); capacity planning; identifying trends over hours or days | Prometheus, Datadog, InfluxDB | Tracking "tokens used per minute" to catch runaway loops before your API bill spikes |
| **Traces** | Causally linked spans representing the end-to-end execution of a single request through multiple services or steps — each span has a parent, a start time, an end time, and key-value attributes | Per-request at sub-millisecond resolution on individual spans — you see the full causal chain for one request | Root-cause analysis across multiple hops in a pipeline; identifying which specific step added most of the latency | Jaeger, Zipkin, Honeycomb | Visualizing that 73% of your agent's response time comes from the LLM call, not the retrieval step |

**Key insight**: A metric can tell you that error rate increased at 2:00 PM; a log can tell you the exact error message for one failing request; a trace can tell you which step in the agent pipeline caused that request to fail and how long each step took.

### Critical Thinking Questions

1. An agent processes 10,000 requests per day. If you logged the full input prompt and output for every request, what storage and privacy problems would that create? What would you log instead, and why would that information still be useful for debugging?

   *Hint:* Think about what information you actually need to diagnose a bug versus what information you only think you might need "just in case." Also consider: what if a user typed their SSN into a prompt?

2. A metric shows that 95th-percentile latency for your agent doubled between Tuesday and Wednesday. Explain why a metric alone cannot tell you *why* this happened, and describe the sequence of steps — which other pillars you would consult, in which order — to diagnose the root cause.

   *Hint:* A metric is a summary. Summaries throw away details to save space. What details were thrown away here, and which pillar preserves them?

3. Logs, metrics, and traces all have associated costs: storage, compute, and egress bandwidth. If you had to pick only two of the three pillars for an MVP deployment of a new agent, which two would you choose and why? Be explicit about what visibility you are giving up by omitting the third.

   *Hint:* Consider the order of operations for debugging: what do you need first when something goes wrong? What do you add when you have more time and budget?

---

## Model 2: Distributed Tracing for Agent Pipelines

> **Why this matters:** An agent is not a single function — it is a pipeline with multiple steps that each take time and can each fail independently. When a user complains that your agent gave a wrong answer, you need to know *which step* failed: was it the retriever that returned irrelevant documents, the LLM that ignored those documents, or the tool call that returned bad data? Distributed tracing gives you a map of every step so you can pinpoint the failure without guessing.

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

> **Common Misconception:** Many developers assume that adding more span attributes is always better — "the more data, the more observability." In practice, storing raw prompt text as a span attribute can expose private user data to your tracing vendor, violate GDPR or FERPA, and generate storage costs that make your traces unusable at scale. Good observability is about storing the *right* attributes — identifiers and measurements — not the raw content.

### Critical Thinking Questions

4. Looking at the span tree above, the `llm_generate` span consumed 73% of the total request duration (1710ms out of 2340ms). Before you decide to optimize the LLM call, what information would you need to determine whether that latency is acceptable or problematic? Consider both technical and business factors in your answer.

   *Hint:* What does your SLA say? Is this a synchronous user-facing call or a background batch job? Does the user experience the full 2340ms, or do you stream tokens as they are generated?

5. A teammate suggests adding a `prompt_text` attribute to the `llm_generate` span so you can inspect what was sent to the model during debugging. Identify at least two categories of information that might appear in a RAG prompt that would be inappropriate to store in a tracing backend. Then propose an alternative approach that gives you the debugging benefit without the privacy risk.

   *Hint:* What documents does a RAG system retrieve? Who wrote those documents, and did they consent to their content being stored in a third-party analytics system? What about the user's original question?

6. The `retrieve` span shows `db_latency_ms=388` out of a total span duration of 410ms. The remaining 22ms is presumably Python serialization overhead. If you needed to reduce retrieval latency by 50% (from 410ms to under 205ms), what specific options would you consider, and how would you use the span data to validate that a change actually worked?

   *Hint:* The span tells you where the time is going. Is it network round-trip to Pinecone, or is it the vector search itself? Those have different solutions. How would you measure before and after?

---

## Model 3: OpenTelemetry Integration

> **Why this matters:** Before OpenTelemetry existed, every observability vendor had its own SDK. Switching from Datadog to Honeycomb meant rewriting all your instrumentation. OTel solves this the same way USB solved the "every device needs its own cable" problem: one standard API, any backend. For agents, this means you can instrument your code once and export to whatever backend your employer uses.

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
        # NOTE: we store query_length (a number), not query text (raw content)

        with tracer.start_as_current_span("llm_generate") as llm_span:
            response = call_llm(user_query)
            llm_span.set_attribute("model_name", response.model)
            llm_span.set_attribute("prompt_tokens", response.usage.prompt_tokens)
            llm_span.set_attribute("completion_tokens", response.usage.completion_tokens)
            llm_span.set_attribute("finish_reason", response.finish_reason)
            # finish_reason values: "stop" (normal), "length" (truncated),
            # "content_filter" (blocked by safety policy)

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

7. The SLA requires "95th-percentile latency under 2 seconds." Looking at the pseudocode above, which span attributes are strictly necessary to compute and track this SLA, and which attributes are useful for debugging but contribute nothing to the SLA metric itself? Be specific about which attributes belong in which category and why.

   *Hint:* To compute a latency percentile, what is the minimum information you need? The span start and end times are recorded automatically by OTel — what else do you need, and what attributes in the code above are you collecting beyond that minimum?

8. The `finish_reason` attribute can take values such as `stop` (normal completion), `length` (truncated because the model hit the token limit), or `content_filter` (blocked by a safety policy). Explain why `finish_reason` is particularly important for detecting quality regressions in production, and write a specific alert rule using it — describe what you monitor, what threshold triggers the alert, and what time window you evaluate over.

   *Hint:* If `finish_reason=length` spikes from 2% to 15% of requests, what does that tell you about your system? What changed? What would you check first?

9. The exporter in the pseudocode sends trace data to `http://otel-collector:4317` — note the `http://` prefix (not `https://`). In a production system, what specific security concerns does this configuration raise, and what would you change to address each concern?

   *Hint:* Trace data contains user IDs, token counts, and model names. Who can intercept unencrypted HTTP traffic on your network? What else might be in those traces that you would not want intercepted?

---

## Exercises

1. **Trace tree design.**

   *What to do:* A 3-step ReAct loop for a research agent consists of: (1) the agent deciding to search the web, (2) executing the web search tool, (3) the agent synthesizing results and deciding whether to search again or answer. Draw the full span tree for one complete ReAct iteration that ends with an answer. Label each span with its name, key attributes, and approximate duration. Indicate parent-child relationships with indentation or arrows.

   *Starter hint:* Start with a root span called `react_loop` that contains the full iteration. Under it, create child spans for `plan` (the LLM deciding what to do), `tool_execute` (the actual web search), and `synthesize` (the LLM reading results). For each span, think: what measurement or identifier would help you debug a failure in that specific step? Example attributes for `tool_execute`: `tool_name=search_web`, `query_text_length=45`, `results_returned=5`, `duration_ms=320`.

   *You've succeeded when:* Your tree shows clear parent-child relationships, every span has at least two non-trivial attributes, and a classmate could use your diagram to identify which step was the bottleneck in a hypothetical slow request.

2. **PII audit.**

   *What to do:* Review the following list of candidate span attributes and classify each as "safe to store in traces," "store with caution (explain the specific concern)," or "do not store (explain the specific harm)." Attributes: `user_id`, `full_prompt_text`, `retrieved_document_ids`, `retrieved_document_content`, `model_name`, `finish_reason`, `user_email`, `response_text`, `session_duration_ms`, `ip_address`.

   *Starter hint:* Ask yourself three questions for each attribute: (1) Is this a measurement/identifier, or is it raw content? (2) Could it reveal information about a specific person to someone who reads the trace? (3) Is it needed for debugging, or is a derived version (like a hash or length) equally useful? For example, `user_id` is typically a pseudonymous identifier — safer than `user_email`, which is directly identifying.

   *You've succeeded when:* Every attribute has a classification and a one-sentence justification that cites a specific risk or a specific reason it is safe. You should have at least one attribute in each category.

3. **Alert design.**

   *What to do:* You are the on-call engineer for a deployed advising agent at a university. Design an alerting policy with at least three separate alert rules covering different failure modes. For each rule, specify: (a) which metric or trace attribute to monitor, (b) the threshold value that triggers the alert, (c) the time window over which the threshold is evaluated, (d) who gets paged, and (e) what the first step of the runbook is.

   *Starter hint:* Consider these three failure modes as a starting point: (1) the agent is returning `finish_reason=content_filter` too often, which may indicate the system prompt is misconfigured; (2) the `retrieve` span latency is spiking, which may indicate the vector database is under load; (3) `completion_tokens` per request is rising, which may indicate a prompt injection is causing the model to generate unusually long responses. Each of these needs different thresholds and different first responders.

   *You've succeeded when:* Each rule has a concrete, measurable threshold (not "if it gets too slow") and a runbook step that a new team member could follow without guessing what to do.

---

## Reflection Prompt

**Personal level:** Describe a time when you could not tell why a program you wrote was behaving unexpectedly. What would you have needed to observe to diagnose it faster? How does that experience relate to what you learned today about observability?

**Technical level:** What would you need to observe to prove — not just believe, but demonstrate with evidence — that your agent is NOT hallucinating in production? Describe the specific logs, metrics, or trace attributes you would collect, how you would analyze them, and what limitation you would still have even with perfect observability in place.

**Societal level:** Observability data creates a detailed record of what users asked an AI system and what it said. Who should have access to that record — the deploying organization, the model vendor, regulators, the users themselves? What privacy rights should users have over the observability data collected about their interactions with AI?

---

→ **Coming Up Next:** In the next activity, we examine how regulatory frameworks — the EU AI Act, NIST AI RMF, and sector rules — determine what you are legally required to observe, log, and audit, and what records you must keep when something goes wrong.

---

## Further Reading

- OpenTelemetry Documentation: https://opentelemetry.io/docs/
- OpenTelemetry Semantic Conventions for LLMs (GenAI): https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Honeycomb. "Observability Engineering." O'Reilly Media, 2022.
- Charity Majors. "Observability — the Big Picture." https://charity.wtf/2020/03/03/observability-is-a-many-splendored-thing/
- Jaeger Distributed Tracing: https://www.jaegertracing.io/
