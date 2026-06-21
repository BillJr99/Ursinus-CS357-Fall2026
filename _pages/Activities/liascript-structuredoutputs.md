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

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Structured Output** | An LLM response that conforms to a predefined format — like a JSON object with specific fields — rather than free-form prose | `{"sentiment": "negative", "confidence": 0.87}` instead of "This article seems pretty negative, maybe around 87% confident" |
| **JSON Schema** | A standard language for describing the shape of a JSON object: what fields exist, what types they must be, which are required, and what values are valid | `{"type": "object", "required": ["sentiment"], "properties": {"sentiment": {"type": "string", "enum": ["positive","negative","neutral"]}}}` |
| **Syntactic Validity** | Whether the output can be parsed as valid JSON (or another format) — it opens and closes brackets correctly and uses proper quoting | `{"key": "value"}` is syntactically valid; `{"key": value}` is not (missing quotes around `value`) |
| **Schema Validity** | Whether the output conforms to the specific schema — required fields are present, types are correct, enum values are within the allowed set | `{"sentiment": "very bad"}` is syntactically valid JSON but schema-invalid because "very bad" is not in the allowed enum |
| **Semantic Validity** | Whether the output means what was intended — the values are not just correctly formatted but actually accurate and calibrated | `{"sentiment": "positive", "confidence": 0.99}` for an article that is clearly negative is schema-valid but semantically wrong |
| **Pydantic** | A Python library that defines data models with type annotations and validates that incoming data conforms to the model, raising a `ValidationError` with a detailed message if it does not | `class BiasAnalysis(BaseModel): confidence: float = Field(ge=0.0, le=1.0)` rejects `confidence: 1.5` automatically |

---

## Model 1: The Four Output Modes

There is not one "structured output" approach — there is a spectrum of mechanisms with different guarantees and different failure modes. Understanding what each mode actually does (not what its marketing says) determines which one to reach for in a given situation.

**Before/After: What the output looks like in each mode**

```
SAME PROMPT: "Classify the sentiment of: 'The product broke after one day.'"

Plain text output:   "The sentiment of this review is clearly negative. The customer
                      is unhappy because the product failed quickly."
                      → Cannot parse; requires fragile regex; breaks if phrasing changes

JSON mode output:    {"sentiment": "negative", "reasoning": "Product failure = negative"}
                      → Usually works, but model might also output prose on a bad day

Tool/function call:  tool_calls=[{"name":"classify","args":{"sentiment":"negative"}}]
                      → Structural format guaranteed; values still up to the model

Grammar-constrained: {"sentiment": "negative"}
                      → Mathematically guaranteed to match the schema; no other output possible
```

| Mode | How It Works | Guarantee Provided | Typical Failure Mode |
|------|-------------|-------------------|---------------------|
| **Plain text** | The model generates tokens with no format constraint at all — it produces whatever prose seems most natural | None — output may be anything; format varies based on phrasing of the question | Cannot be parsed programmatically; format changes unpredictably when the prompt is reworded or the model version changes |
| **JSON mode** (instruction-based) | The system prompt instructs the model to output JSON; the model is free to comply or not — it is just a strong suggestion | Soft — the model usually produces valid JSON but may produce prose, truncated JSON, or JSON with extra unexpected fields on a bad day | Model ignores the instruction when the context is long, when it is uncertain, or when the question triggers a refusal; no enforcement mechanism catches this |
| **Function calling / tool use** | The API wraps the model's output in a structured function-call schema; the model generates a `tool_calls` field rather than prose | The format of the function call is guaranteed to be structurally valid; argument types match the declared schema | Model may call the wrong tool when multiple tools are available, omit required arguments, or pass arguments with the right type but wrong semantic content (a valid-format but wrong value) |
| **Grammar-constrained decoding** (Outlines, LMQL, llama.cpp grammars) | At each decoding step, the token sampler masks out any token that would violate the grammar; only valid-next-token candidates can be sampled | Syntactic validity is mathematically guaranteed at the token level — the output will always parse as valid JSON matching the schema | Model may produce syntactically valid but semantically wrong output (correct format, wrong meaning); very complex required outputs can degrade overall response quality |

Three properties worth separating clearly — these are the "levels" of correctness:

- **Syntactic validity**: Is the output parseable as JSON (or another format)? Does it have matching brackets and correct quoting?
- **Schema validity**: Does the output conform to the specific schema — required fields present, types correct, enum values within the allowed set?
- **Semantic validity**: Does the output mean what was intended — is the confidence score actually calibrated, does the citation actually exist, is the sentiment label actually accurate?

Grammar-constrained decoding guarantees syntactic validity only. Function calling with a schema guarantees syntactic and schema validity. Nothing guarantees semantic validity — that requires evaluation, human oversight, or both.

### Critical Thinking Questions

1. A developer uses JSON mode (instruction-based) for a production system and never validates the output, arguing "the model always produces valid JSON in my testing." Describe a specific production scenario where this assumption breaks, explain exactly what class of failure it causes in the downstream system, and estimate how long it might go undetected.

   *Hint: Testing typically uses short, clean inputs. What happens when a user submits an unusually long article, an article in a foreign language, or a prompt that contains characters the model tries to escape in JSON? What does the downstream code do when it receives `None` where it expected a dict?*

2. Grammar-constrained decoding masks out tokens that would violate the grammar. Consider a schema that requires `"country": {"enum": ["US", "CA", "MX"]}`. The model is generating a response about a user who is in Germany. What does the constrained decoder do when it reaches the `country` field, and is the output it produces correct in any meaningful sense?

   *Hint: The decoder cannot output "DE" because it is not in the enum. It must output one of "US", "CA", or "MX". How does the decoder choose, and what does that choice mean for the accuracy of the output? Is structural guarantee the same as accuracy?*

3. The model produces output at all three validity levels: syntactic, schema, and semantic. For a medical triage agent that outputs `{"urgency": "high" | "medium" | "low", "rationale": string}`, which validity level matters most for patient safety, and why are the lower levels (syntactic, schema) necessary but not sufficient?

   *Hint: A schema-valid output like `{"urgency": "low", "rationale": "Patient reports mild discomfort"}` might describe a patient who is actually in critical condition. Which validity level catches the difference between "correctly formatted" and "actually right"?*

---

## Model 2: Schema Design as Prompt Engineering

The schema you write for a structured output is not just a type annotation — it is a prompt. The field names, descriptions, and constraints communicate to the model what you want in the same way that natural language instructions do. A poorly designed schema produces valid-but-useless outputs; a well-designed schema elicits better reasoning.

**Task**: Design a JSON schema for the task "analyze a news article for potential bias."

Consider what a thoughtful human analyst would record:
- What is the article's overall sentiment toward the subject?
- What is the apparent political lean, if any?
- How strong is the evidence provided?
- What perspectives are not represented?
- What sources are cited, and are they independently checkable?
- How confident are you in your overall assessment?

**Version A — poorly designed schema:**

```json
{
  "sentiment": "string",
  "bias": "string",
  "score": "number",
  "notes": "string"
}
```

Problems with Version A: `bias` is a free-form string, so 10,000 articles might produce 10,000 different bias descriptions — impossible to aggregate. `score` has no minimum, maximum, or meaning. `notes` is a catch-all that will absorb anything the model wanted to say but had no proper field for.

**Version B — schema designed to elicit structured reasoning:**

```json
{
  "type": "object",
  "required": ["sentiment", "political_lean", "evidence_quality", "missing_perspectives", "citations", "confidence"],
  "properties": {
    "sentiment": {
      "type": "string",
      "enum": ["strongly_positive", "positive", "neutral", "negative", "strongly_negative"],
      "description": "Overall sentiment of the article toward its primary subject — use the closest enum value"
    },
    "political_lean": {
      "type": "string",
      "enum": ["far_left", "left", "center_left", "center", "center_right", "right", "far_right", "not_applicable"],
      "description": "Apparent political orientation of the article's framing — assess the framing, not the subject matter"
    },
    "evidence_quality": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Score from 0.0 (pure assertion with no evidence) to 1.0 (strong primary sources with verifiable claims)"
    },
    "missing_perspectives": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of viewpoints or stakeholders relevant to the story that are absent from the article — each item is one missing perspective"
    },
    "citations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["text", "verifiable"],
        "properties": {
          "text": {"type": "string", "description": "The text of the source as it appears in the article"},
          "verifiable": {"type": "boolean", "description": "True if the citation can be independently checked; false if it is vague or unnamed"}
        }
      },
      "description": "Sources cited in the article with a judgment about whether each is checkable"
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Model's confidence in the overall bias assessment — use lower values when the article is ambiguous or mixed"
    }
  }
}
```

**Before/After: what the model outputs with each schema for the same article**

```
ARTICLE: "Officials respond to criticism of new highway project."

Version A output:
{"sentiment": "mixed", "bias": "somewhat political", "score": 5.2, "notes": "hard to tell"}
→ Useless for aggregation; "score" has no unit; "somewhat political" cannot be compared across articles

Version B output:
{"sentiment": "neutral", "political_lean": "center_right", "evidence_quality": 0.4,
 "missing_perspectives": ["environmental groups", "local residents displaced by construction"],
 "citations": [{"text": "city council report", "verifiable": false},
               {"text": "state transportation department study", "verifiable": true}],
 "confidence": 0.72}
→ Every field is comparable across articles; missing_perspectives reveals editorial gaps;
  citations are individually assessable; confidence signals where to apply extra scrutiny
```

### Critical Thinking Questions

4. Version A has a `"bias": "string"` field. Version B replaces it with `"political_lean"` as an enum. Explain two specific problems that arise when analyzing 10,000 articles using Version A's free-form bias string, and how the enum in Version B solves each problem.

   *Hint: Problem 1 is about aggregation — if one article is labeled "left-leaning" and another "progressive bias" and a third "liberal slant," how do you count how many articles have a left-leaning bias? Problem 2 is about consistency across time — if the same model labels the same article as "somewhat biased" in January and "moderately biased" in March (because the model updated), how do you detect this inconsistency?*

5. The `confidence` field asks the model to report its own uncertainty. Research on chain-of-thought prompting suggests that requiring a model to explain its reasoning improves the quality of its primary answer. Propose a mechanism by which requiring a `confidence` field might cause the model to reason more carefully about the `political_lean` field that comes before it.

   *Hint: Token generation is sequential — the model generates the `political_lean` value before it generates the `confidence` value. If the model "knows" it will need to report a confidence score, how might that shape what it pays attention to while choosing the `political_lean` value? This is a design hypothesis — reason from what you know about sequential generation.*

6. The `missing_perspectives` field is an array of strings. It can always be syntactically valid (any list of strings passes) and always be schema-valid (the schema only requires the items to be strings). But what makes this field particularly hard to validate *semantically*, even when it is perfectly formatted? What would a realistic post-hoc validation step for this field look like?

   *Hint: To validate that "environmental groups" is a genuinely missing perspective for a highway article, you need to know what perspectives actually exist for highway projects and which ones the article addressed. You cannot determine this from the JSON alone. What external resource or process would you need?*

---

## Model 3: The Output Validation Pipeline

Never trust raw LLM output, even in JSON mode or with a schema. Always parse and validate before your code uses the data. When validation fails, you have two options: surface the error to the caller, or attempt a **repair loop** — re-prompting the model with the specific validation error and asking it to fix only that problem.

```python
# Pydantic data model — defines the expected structure and validates incoming data
from pydantic import BaseModel, Field, ValidationError
from typing import Literal
import json

class BiasAnalysis(BaseModel):
    # Literal["a","b","c"] means the value MUST be exactly one of these strings
    sentiment: Literal["strongly_positive", "positive", "neutral", "negative", "strongly_negative"]
    political_lean: Literal["far_left", "left", "center_left", "center",
                            "center_right", "right", "far_right", "not_applicable"]
    # Field(ge=0.0, le=1.0) means: greater-than-or-equal-to 0.0 AND less-than-or-equal-to 1.0
    # Pydantic raises ValidationError if the model outputs 1.5 or -0.1
    evidence_quality: float = Field(ge=0.0, le=1.0)
    missing_perspectives: list[str]    # List of strings — any content is schema-valid
    confidence: float = Field(ge=0.0, le=1.0)

def analyze_article(article_text: str, llm, max_repair_attempts: int = 2) -> BiasAnalysis:
    prompt = build_analysis_prompt(article_text)    # Build the initial prompt

    # Try up to max_repair_attempts + 1 times (first attempt + repairs)
    for attempt in range(max_repair_attempts + 1):
        raw = llm.generate(prompt, response_format=BiasAnalysis)
        # raw is a string containing JSON — we have not validated it yet

        try:
            # model_validate_json parses the JSON AND validates against the schema
            # If both succeed, we return the validated object immediately
            return BiasAnalysis.model_validate_json(raw)

        except ValidationError as e:
            # Validation failed — either JSON is malformed or values violate the schema
            if attempt == max_repair_attempts:
                # We've used all our repair attempts — fail loudly, do not silently return garbage
                raise RuntimeError(
                    f"Schema validation failed after {max_repair_attempts} repair attempts. "
                    f"Last error: {e}"
                ) from e

            # Build a TARGETED repair prompt that gives the model the specific error message
            # "Fix only the specific errors" prevents the model from changing valid fields
            prompt = f"""Your previous response did not conform to the required schema.

Previous response:
{raw}

Validation errors:
{e}

Please output only corrected JSON that fixes these specific errors.
Do not change any values that were already valid."""
            # Loop continues — next iteration will try again with the repair prompt

    raise RuntimeError("Unreachable")    # Should never get here (loop always returns or raises)
```

**Before/After: a repair loop in action**

```
First attempt output (invalid):
{"sentiment": "negative", "political_lean": "center_left",
 "evidence_quality": 1.5,   ← INVALID: exceeds maximum of 1.0
 "missing_perspectives": ["opposition parties"],
 "confidence": 0.8}

ValidationError message Pydantic generates:
1 validation error for BiasAnalysis
evidence_quality
  Input should be less than or equal to 1 [type=less_than_equal, input_value=1.5, ...]

Repair prompt sent to the model:
"Your previous response did not conform to the required schema.
 Previous response: {...}
 Validation errors: evidence_quality: Input should be less than or equal to 1 [input_value=1.5]
 Please output only corrected JSON that fixes these specific errors.
 Do not change any values that were already valid."

Second attempt output (valid):
{"sentiment": "negative", "political_lean": "center_left",
 "evidence_quality": 0.9,   ← Fixed: now within [0.0, 1.0]
 "missing_perspectives": ["opposition parties"],
 "confidence": 0.8}         ← Unchanged: was already valid
```

Key properties of this pipeline:

- **Parse first, use second**: `model_validate_json` raises an exception before any downstream code touches potentially invalid data.
- **Targeted repair**: The repair prompt includes the *specific* validation error with the actual bad value, not just "try again." This gives the model actionable information about exactly what to fix.
- **Bounded retries**: The loop has a hard limit. Without it, an unfixable validation error (like a model that consistently outputs the wrong type) becomes an infinite loop and unbounded API cost.
- **Fail loudly**: When repair is exhausted, the exception propagates to the caller. Silent failures — returning `None` or default values — hide the problem and allow bad data to flow downstream.

> **⚠️ Common Misconception:** Many students assume that using "JSON mode" or telling the model to "output JSON" in the system prompt provides the same guarantees as grammar-constrained decoding or function calling with a schema. It does not. JSON mode is a *suggestion* — the model can and sometimes will ignore it, especially under pressure (long context, unusual inputs, refusals). The only way to get a mathematical guarantee that the output parses as valid JSON is to use grammar-constrained decoding at the token level. The only way to get schema validity without grammar constraints is to validate with a library like Pydantic *after* the model responds and repair or reject on failure.

### Critical Thinking Questions

7. The repair prompt says "Do not change any values that were already valid." Why is this specific constraint important? Describe a concrete scenario where a repair prompt that just said "output the correct JSON" could accidentally make the response worse, not better.

   *Hint: Consider a case where the model correctly identified `political_lean` as "center_right" but had an invalid `evidence_quality` of 1.5. If the repair prompt just says "output correct JSON," the model might re-evaluate the article from scratch and now classify `political_lean` as "right" — changing a valid field while fixing the invalid one. What does the more constrained repair prompt do differently?*

8. Pydantic's `Field(ge=0.0, le=1.0)` on `evidence_quality` catches the case where the model outputs `1.5` (a range violation). But it does not catch the case where the model outputs `0.9` for an article that cites zero sources and makes no verifiable claims — semantically, `0.9` is wildly wrong here, but it is structurally valid. What layer of the system is responsible for catching semantic errors like this, and describe what that layer would concretely look like?

   *Hint: One approach is a separate "quality check" LLM call that reads both the original article and the BiasAnalysis output and asks "is this analysis consistent with the article?" Another approach is statistical: track the distribution of `evidence_quality` scores across thousands of articles and flag outliers. Which approach is more scalable?*

9. The function raises `RuntimeError` after exhausting `max_repair_attempts`. The caller must handle this exception. Propose a **graceful degradation** strategy for a system that is analyzing news articles and must always return *something* to the user — even if validation fails after all repair attempts. What should be returned, and what metadata should accompany the degraded response to make its limitations clear to downstream consumers?

   *Starter hint: One option is to return a partially valid response — the fields that passed validation — alongside an explicit `is_degraded: True` flag and a `validation_errors` field listing what failed. Another option is to return a "manual review required" placeholder. Which is more useful to a downstream system? What does a system that relies on this output need to know to handle both cases correctly?*

[[MC]]
You ask an LLM to output a JSON object with a field `"confidence": float` constrained to values between 0 and 1. The model outputs `{"confidence": "high"}`. The most likely root cause of this failure is:
- (x) The JSON schema or response format was not provided to the model (or was provided only as a natural language instruction), so the model produced a plausible English description instead of a number
- ( ) The model does not understand the concept of numbers and cannot generate them
- ( ) The schema definition contained a syntax error that caused it to be silently ignored
- ( ) The model is malfunctioning and needs to be restarted

---

## Exercises

1. **Schema gap analysis.**

   *What to do:* The `BiasAnalysis` Pydantic model in Model 3 omits `citations` (which is present in the Version B schema from Model 2). Add `citations` as a nested Pydantic model. Write the complete class definition, then write a unit test that creates a `BiasAnalysis` from a JSON string where `verifiable` is a string instead of a boolean, and confirm that a `ValidationError` is raised.

   *Starter hint:*
   ```python
   from pydantic import BaseModel, Field, ValidationError
   from typing import Literal
   import pytest

   class Citation(BaseModel):
       text: str                  # The citation text as it appears in the article
       verifiable: bool           # Must be exactly True or False, not "true" or 1

   class BiasAnalysis(BaseModel):
       sentiment: Literal["strongly_positive", "positive", "neutral", "negative", "strongly_negative"]
       political_lean: Literal["far_left", "left", "center_left", "center",
                               "center_right", "right", "far_right", "not_applicable"]
       evidence_quality: float = Field(ge=0.0, le=1.0)
       missing_perspectives: list[str]
       citations: list[Citation]   # Add this field — a list of Citation objects
       confidence: float = Field(ge=0.0, le=1.0)

   def test_citation_verifiable_must_be_bool():
       bad_json = '''{"sentiment": "neutral", "political_lean": "center",
                      "evidence_quality": 0.5, "missing_perspectives": [],
                      "citations": [{"text": "some source", "verifiable": "yes"}],
                      "confidence": 0.7}'''
       # "verifiable": "yes" is a string, not a boolean — this should raise ValidationError
       with pytest.raises(ValidationError):
           BiasAnalysis.model_validate_json(bad_json)
   ```

   *You've succeeded when* running `pytest` on your test file shows the test passes (meaning Pydantic correctly rejected the invalid input).

2. **Grammar vs. instruction comparison.**

   *What to do:* Using a local LLM (Ollama with `ollama run llama3` or similar), run the same bias-analysis prompt 10 times with (a) a plain text instruction to output JSON and (b) `response_format` set to your schema if your library supports it. Record how many times each mode produces parseable output. Report the failure modes you observe.

   *Starter hint:*
   ```python
   import ollama
   import json

   prompt = """Analyze the following article for bias. Output ONLY valid JSON with these fields:
   sentiment (string), political_lean (string), evidence_quality (float 0-1), confidence (float 0-1).

   Article: 'Officials defend new highway project despite protests.'"""

   # Run 10 times and count parse failures
   results = {"success": 0, "json_parse_error": 0, "schema_error": 0}
   for i in range(10):
       response = ollama.chat(model="llama3", messages=[{"role":"user","content":prompt}])
       raw = response['message']['content']
       try:
           parsed = json.loads(raw)    # Does it parse as JSON at all?
           # Check for required fields
           assert "sentiment" in parsed and "confidence" in parsed
           results["success"] += 1
       except json.JSONDecodeError:
           results["json_parse_error"] += 1    # Not even valid JSON
       except AssertionError:
           results["schema_error"] += 1         # Valid JSON but missing fields
   print(results)
   ```

   *You've succeeded when* you have a table comparing success rates between instruction-only and schema-constrained modes, and you can name at least two distinct failure modes you observed.

3. **Repair prompt design.**

   *What to do:* Consider the specific case where the model outputs `{"evidence_quality": null}` — the field is present but its value is `null` (Python `None`) instead of a float. Write the exact repair prompt you would generate from the `ValidationError` that Pydantic produces for this input, following the targeted-repair pattern from Model 3. Then explain in two sentences why a generic "please try again" repair prompt would likely perform worse on this specific error.

   *Starter hint:* Run this in Python to see what error Pydantic actually generates:
   ```python
   from pydantic import BaseModel, Field, ValidationError
   class Test(BaseModel):
       evidence_quality: float = Field(ge=0.0, le=1.0)

   try:
       Test.model_validate({"evidence_quality": None})
   except ValidationError as e:
       print(e)   # Copy this error message into your repair prompt
   ```
   Your repair prompt should include the previous response, the exact error message Pydantic generated, and the specific instruction not to change already-valid fields.

   *You've succeeded when* your repair prompt is specific enough that a different developer could use it verbatim and the model would have enough information to correct the `null` value without changing anything else.

4. **Confidence as a quality signal.**

   *What to do:* Design a controlled experiment to test whether requiring a `confidence` field in the output schema improves the accuracy of the `political_lean` field. Describe your dataset, your metric for measuring accuracy, your control condition (no confidence field), your experimental condition (with confidence field), and what result would confirm or disconfirm the hypothesis.

   *Starter hint:* You need a dataset of news articles with ground-truth political lean labels (e.g., from a media bias rating service like AllSides). Your metric for accuracy is whether the model's `political_lean` output matches the ground-truth label. The control condition uses a schema without a `confidence` field; the experimental condition adds the `confidence` field. Run both conditions on the same 100 articles and compare accuracy rates. What result would confirm that confidence improves accuracy? What alternative explanation would you need to rule out?

   *You've succeeded when* your experiment design is specific enough that another student could run it independently and produce comparable results — the dataset source, sample size, metric definition, and analysis method are all specified.

---

## Reflection Prompt

*Personal:* Structured outputs are a form of specification — you write a schema encoding what you believe a good answer looks like. Think of a time in everyday life when you specified the format of an answer and the person (or system) you were asking gave you something that met the format but missed the point entirely. What was the gap between your specification and your intent? How did you discover it, and what would a better specification have said?

*Technical:* The repair loop in Model 3 has a hard limit on retries to avoid infinite loops. But the right number of retries depends on how often the model fails and how valuable each successful validation is. Describe a principled method for choosing `max_repair_attempts` — what data would you collect, what tradeoffs would you weigh, and how would you know when to raise or lower the limit?

*Societal:* Structured outputs make LLM behavior more predictable and auditable — you can inspect the JSON fields and verify that the output conforms to expectations. But this auditability is only as good as the schema. If an AI system is making consequential decisions (approving loans, triaging medical cases, screening job applications) and the schema captures the wrong things, structured outputs create an illusion of rigor without the substance. What governance process should exist around schema design for high-stakes AI applications? Who should be involved in designing, reviewing, and updating the schema?

---

→ Coming Up Next: You have now seen how to make agents produce structured, validatable outputs. The next module brings together the full agent stack — filesystem isolation, container security, authentication, human oversight, and structured outputs — to examine end-to-end agentic pipeline design and the failure modes that only emerge when all the components interact.

---

## Further Reading

- Pydantic documentation, "Structured Outputs with LLMs": https://docs.pydantic.dev/latest/concepts/pydantic_ai/
- Willard and Louf. "Efficient Guided Generation for LLMs." *arXiv* 2307.09702 (2023). (The paper behind the Outlines library.)
- OpenAI. "Structured Outputs." https://platform.openai.com/docs/guides/structured-outputs
- Anthropic. "Tool Use (Function Calling)." https://docs.anthropic.com/en/docs/tool-use
- Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *NeurIPS* (2022). https://arxiv.org/abs/2201.11903
