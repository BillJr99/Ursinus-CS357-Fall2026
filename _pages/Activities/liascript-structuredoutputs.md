# Structured Outputs: JSON Mode, Tool Schemas, and Output Validation
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-structuredoutputs.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-structuredoutputs.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# Structured Outputs: JSON Mode, Tool Schemas, and Output Validation

When a downstream program needs to parse an LLM's response — to extract a confidence score, trigger a tool call, populate a database field — prose is a liability. A model that writes "I'm fairly confident the answer is Paris, probably around 85%" produces output that requires fragile string parsing, fails silently when the format shifts, and cannot be statically typed. **Structured outputs** solve this by constraining what the model can generate: the response is a well-typed object your code can validate before use. This activity explores the full stack, from output mode selection to schema design to validation pipelines.

---

## Directions and Group Roles

Work in your POGIL team of four with clearly assigned roles:

- **Manager**: Keeps the group on task and on time; ensures everyone contributes before moving on.
- **Recorder**: Documents the group's answers and posts the final responses to the Class Activity Questions discussion board.
- **Presenter**: Speaks for the group during debrief; articulates areas of genuine disagreement or alternative interpretations.
- **Reflector**: Monitors group process and captures lessons learned for the reflection prompt.

Consider each model and its questions individually before discussing with your group. Pay careful attention to the distinctions between output modes — the differences are subtle but consequential.

---

## Model 1: The Four Output Modes

There is not one "structured output" approach — there is a spectrum of mechanisms with different guarantees and different failure modes. Understanding what each mode actually does (not what its marketing says) determines which to reach for.

| Mode | How It Works | Guarantee Provided | Typical Failure Mode |
|------|-------------|-------------------|---------------------|
| **Plain text** | Model generates tokens with no format constraint | None; output may be anything | Cannot be parsed programmatically; format varies by phrasing |
| **JSON mode** (instruction-based) | System prompt instructs the model to output JSON; model is free to comply or not | Soft; model usually produces JSON but may produce prose, truncated JSON, or JSON with extra fields | Model ignores instruction under pressure (long context, refusals, uncertainty); no schema enforcement |
| **Function calling / tool use** | API wraps the model's output in a structured call schema; model generates `tool_calls` field | Structural validity of the function call format; argument types match schema | Model may call the wrong tool, omit required arguments, or pass arguments with wrong semantic content |
| **Grammar-constrained decoding** (Outlines, LMQL, llama.cpp grammars) | At each decoding step, the sampler masks out tokens that would violate the grammar; only valid-next-token candidates are sampled | Structural validity is *mathematically guaranteed* at the token level; output will always parse | Model may produce syntactically valid but semantically wrong output; very long required outputs may degrade quality; schema must be expressible as a finite grammar |

Three properties are worth separating clearly:

- **Syntactic validity**: Is the output parseable as JSON / valid function call / etc.?
- **Schema validity**: Does the output conform to the specific schema (required fields present, types correct, enum values in range)?
- **Semantic validity**: Does the output mean what we intended (confidence score is actually calibrated; citation actually exists)?

Grammar-constrained decoding guarantees syntactic validity. Function calling with a schema guarantees syntactic and schema validity. Nothing guarantees semantic validity — that is the domain of evaluation and human oversight.

### Critical Thinking Questions

1. A developer uses JSON mode (instruction-based) and never validates the output, arguing "the model always produces JSON in testing." Describe a production scenario in which this assumption breaks, and explain what class of failure it causes downstream.

2. Grammar-constrained decoding masks out tokens that would violate the grammar. Consider a schema that requires a field `"country": {"enum": ["US", "CA", "MX"]}`. The model is generating a response about a user in Germany. What does the constrained decoder do, and is the resulting output correct?

3. The table lists three levels of validity. For a medical triage agent that outputs `{"urgency": "high" | "medium" | "low", "rationale": string}`, which validity level matters most, and why is achieving the lower levels necessary but not sufficient?

---

## Model 2: Schema Design as Prompt Engineering

The schema you write for a structured output is not just a type annotation — it is a prompt. The field names, descriptions, and constraints communicate to the model what you want in the same way that natural language instructions do. A poorly designed schema produces valid-but-useless outputs; a well-designed schema elicits better reasoning.

**Task**: Design a JSON schema for the task "analyze a news article for potential bias."

Consider what a thoughtful human analyst would record:

- What is the article's overall sentiment toward the subject?
- What is the apparent political lean, if any?
- How strong is the evidence provided?
- What perspectives are not represented?
- What sources are cited, and are they checkable?
- How confident are you in your assessment?

A raw schema attempt (Version A):

```json
{
  "sentiment": "string",
  "bias": "string",
  "score": "number",
  "notes": "string"
}
```

A schema designed to elicit structured reasoning (Version B):

```json
{
  "type": "object",
  "required": ["sentiment", "political_lean", "evidence_quality", "missing_perspectives", "citations", "confidence"],
  "properties": {
    "sentiment": {
      "type": "string",
      "enum": ["strongly_positive", "positive", "neutral", "negative", "strongly_negative"],
      "description": "Overall sentiment of the article toward its primary subject"
    },
    "political_lean": {
      "type": "string",
      "enum": ["far_left", "left", "center_left", "center", "center_right", "right", "far_right", "not_applicable"],
      "description": "Apparent political orientation of the framing, not the subject matter"
    },
    "evidence_quality": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Score from 0 (no evidence, pure assertion) to 1 (strong primary sources, verifiable claims)"
    },
    "missing_perspectives": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Viewpoints or stakeholders relevant to the story that are absent from the article"
    },
    "citations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["text", "verifiable"],
        "properties": {
          "text": {"type": "string"},
          "verifiable": {"type": "boolean"}
        }
      },
      "description": "Sources cited in the article and whether each is independently checkable"
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Model's confidence in the overall bias assessment, accounting for ambiguity in the article"
    }
  }
}
```

### Critical Thinking Questions

4. Version A has a `"bias": "string"` field. Version B has `"political_lean"` as an enum. Explain two problems with leaving bias as a free-form string in a system that will aggregate assessments across 10,000 articles.

5. The `confidence` field asks the model to report its own uncertainty. Research suggests that prompting a model to output a confidence score can actually improve the quality of its primary answer. Propose a mechanism by which requiring a confidence score might cause the model to reason more carefully. (This is a design hypothesis — reason from what you know about how models generate tokens.)

6. The `missing_perspectives` field is an array of strings. What makes this field particularly difficult to validate semantically, even if it is syntactically perfect? What would a post-hoc validation step for this field look like?

---

## Model 3: The Output Validation Pipeline

Never trust raw LLM output, even in JSON mode or with a schema. Always parse and validate before use. When validation fails, you have two options: surface the error to the caller, or attempt a repair loop. The repair loop re-prompts the model with the original request, the invalid output, and the specific validation error, asking it to fix only the structural problem.

```python
from pydantic import BaseModel, Field, ValidationError
from typing import Literal
import json

class BiasAnalysis(BaseModel):
    sentiment: Literal["strongly_positive", "positive", "neutral", "negative", "strongly_negative"]
    political_lean: Literal["far_left", "left", "center_left", "center",
                            "center_right", "right", "far_right", "not_applicable"]
    evidence_quality: float = Field(ge=0.0, le=1.0)
    missing_perspectives: list[str]
    confidence: float = Field(ge=0.0, le=1.0)

def analyze_article(article_text: str, llm, max_repair_attempts: int = 2) -> BiasAnalysis:
    prompt = build_analysis_prompt(article_text)

    for attempt in range(max_repair_attempts + 1):
        raw = llm.generate(prompt, response_format=BiasAnalysis)

        try:
            return BiasAnalysis.model_validate_json(raw)

        except ValidationError as e:
            if attempt == max_repair_attempts:
                raise RuntimeError(
                    f"Schema validation failed after {max_repair_attempts} repair attempts. "
                    f"Last error: {e}"
                ) from e

            # Build a repair prompt that gives the model the specific error
            prompt = f"""Your previous response did not conform to the required schema.

Previous response:
{raw}

Validation errors:
{e}

Please output only corrected JSON that fixes these specific errors.
Do not change any values that were already valid."""

    raise RuntimeError("Unreachable")
```

Key properties of this pipeline:

- **Parse first, use second**: `model_validate_json` raises before any downstream code touches the data.
- **Targeted repair**: The repair prompt includes the *specific* validation error, not just "try again." This gives the model actionable information.
- **Bounded retries**: The loop has a hard limit. Infinite repair loops can become runaway API cost.
- **Fail loudly**: When repair is exhausted, the exception propagates. Silent failures (returning `None` or default values) hide the problem.

### Critical Thinking Questions

7. The repair prompt says "Do not change any values that were already valid." Why is this constraint important? What could go wrong if the repair prompt just said "output the correct JSON"?

8. Pydantic's `Field(ge=0.0, le=1.0)` on `evidence_quality` catches the case where the model outputs `1.5`. But it does not catch the case where the model outputs `0.9` for an article with no sources. What layer of the system is responsible for catching semantic errors like this, and what would that layer look like?

9. The function raises `RuntimeError` after `max_repair_attempts`. The caller must handle this. Propose a graceful degradation strategy for a system that must always return *something* to the user. What should be returned, and what metadata should accompany it to make the degraded response trustworthy?

[[MC]]
You ask an LLM to output a JSON object with a field `"confidence": float` constrained to values between 0 and 1. The model outputs `{"confidence": "high"}`. The most likely root cause of this failure is:
- (x) The JSON schema or response format was not provided to the model (or was provided only as a natural language instruction), so the model produced a plausible English description instead of a number
- ( ) The model does not understand the concept of numbers and cannot generate them
- ( ) The schema definition contained a syntax error that caused it to be silently ignored
- ( ) The model is malfunctioning and needs to be restarted

---

## Exercises

1. **Schema gap analysis.** The `BiasAnalysis` schema in Model 3 omits `citations` (present in the Version B schema from Model 2). Add `citations` as a nested Pydantic model. Write the class definition and a unit test that confirms a response with a non-boolean `verifiable` field raises `ValidationError`.

2. **Grammar vs. instruction comparison.** Using a local LLM (Ollama), run the same bias-analysis prompt 10 times with (a) a plain instruction to output JSON and (b) `response_format` set to your schema. Record how many times each mode produces parseable output. Report the failure modes you observe.

3. **Repair prompt design.** Consider a case where the model outputs `{"evidence_quality": null}`. Write the repair prompt you would generate from this specific `ValidationError`, following the pattern in Model 3. Then explain why a generic "please try again" repair prompt performs worse on average.

4. **Confidence as a quality signal.** Design an experiment to test whether requiring a `confidence` field improves the accuracy of the `political_lean` field. Describe your dataset, your metric for "accuracy," your control condition, and what result would confirm or disconfirm the hypothesis.

---

## Reflection Prompt

In your notebook: structured outputs are a form of specification. When you write a schema, you are encoding what you believe a good answer looks like. But the model's "understanding" of that schema may differ from yours. Describe a situation — in software development or in everyday life — where specifying the format of an answer did not actually communicate what you wanted. What was the gap between the specification and the intent, and how did you discover it?

---

## Further Reading

- Pydantic documentation, "Structured Outputs with LLMs": https://docs.pydantic.dev/latest/concepts/pydantic_ai/
- Willard and Louf. "Efficient Guided Generation for LLMs." *arXiv* 2307.09702 (2023). (The paper behind the Outlines library.)
- OpenAI. "Structured Outputs." https://platform.openai.com/docs/guides/structured-outputs
- Anthropic. "Tool Use (Function Calling)." https://docs.anthropic.com/en/docs/tool-use
- Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *NeurIPS* (2022). https://arxiv.org/abs/2201.11903
