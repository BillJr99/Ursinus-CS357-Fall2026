---
layout: default-standard
permalink: /Tutorials/MultimodalAgents
title: 'CS357: Foundations of Artificial Intelligence - Multimodal Agents'
info:
  coursenum: CS357
  purpose: "To treat images, documents, and code as first-class inputs to an agent rather than attachments it cannot see."
tags:
- multimodal
- vision
- documents
---
# CS357: Foundations of Artificial Intelligence - Multimodal Agents

## Purpose

To treat images, documents, and code as first-class inputs to an agent rather than attachments it cannot see.

## About This Tutorial

A multimodal agent is like a colleague who can not only read your email but also glance at the whiteboard photo you attached, scan the PDF contract you dropped in the chat, and look at the screenshot of the error you're seeing.  The ability to reason across formats (not just text) dramatically expands what an agent can perceive and act on.  But every modality conversion introduces new failure modes, and understanding those failures is essential for building reliable systems.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|---|---|---|
| Vision Language Model (VLM) | A language model extended with an image encoder that converts images into token sequences, allowing the model to reason about images and text together in a single context. | GPT-4o and Claude Sonnet can receive an image of a form and extract its fields as structured JSON. |
| Modality | A type of input or output format: text, image, audio, video, and code are each a distinct modality. | A multimodal agent handles at least two modalities: most commonly text + images, or text + audio via transcription. |
| Patch Embedding | The way vision models process images: they divide the image into small rectangular patches, encode each patch as a vector, and concatenate those vectors as if they were word tokens. | A 512×512 pixel image divided into 16×16 patches produces 1,024 patch tokens, before it even reaches the language model. |
| Grounding | The ability of a model to point to the specific region of an image, sentence in a document, or line of code that supports its claim, connecting the output back to the input. | A grounded model says "The invoice total is $1,247 (found in the bottom-right cell of the table at row 14)" rather than just "$1,247". |
| OCR (Optical Character Recognition) | A technique that renders a document as an image and then identifies and extracts the text characters visible in that image; used when a PDF has no text layer. | Tesseract (`pip install pytesseract`) can extract text from a scanned photo of a handwritten form, though with higher error rates than text-layer extraction. |
| CLIP | Contrastive Language-Image Pretraining, a model that jointly trains image and text encoders so that an image and its description produce similar embeddings, enabling text-to-image search and vice versa. | `pip install clip` from OpenAI enables queries like "find me images of broken login forms" against an image database; no manual labels required. |

---

# Part I: What Multimodal Means for Agents

In this part, you will learn how different input types (images, PDFs, audio, video, code) are all converted to the same token format that LLMs process.  Understanding this conversion pipeline is essential because every failure mode in multimodal agents originates at a conversion step.

## How Modalities Become Tokens

Early language models accepted only text.  Modern agents increasingly accept (and reason over) a much broader set of inputs: images, PDFs, audio recordings, video clips, and structured code files.  This is what it means for an agent to be **multimodal**: its input space is not confined to a single modality.

This matters for agents more than for standalone chatbots because agents take actions.  An agent that can see a screenshot can click the right button.  An agent that can read a PDF contract can extract the clause that triggers a tool call.  An agent that hears a voice command can act on it without a human typing an intermediate transcript.

Multimodality is not magic; it is an extension of the fundamental token-processing architecture.  Every modality is ultimately encoded as a sequence of tokens before it enters the transformer.  What differs is how that encoding happens, how lossy it is, and what kinds of errors result.

| Modality | Input Format | How the Model Receives It | Typical Token Count | Key Capability | Key Limitation |
|:---------|:------------|:---------------------|:---------------------|:-------------|:------------|
| Image or Screenshot | PNG, JPEG, WebP | Divided into patches by a Vision Transformer (ViT); each patch becomes an embedding projected into the text token space | ~256-1,024 tokens per image (depending on resolution and model) | Describe scenes, read printed text, identify UI elements, detect objects, extract structured fields from forms | Fine text, merged cells, unusual fonts, and dense numeric tables are frequently misread; no spatial precision without grounding |
| PDF Document | Binary PDF file | Three possible pipelines: (1) extract embedded text layer, (2) OCR the rendered image, or (3) render pages as images and send to a VLM | 500-5,000 tokens per page (text extraction); 500-2,000 tokens per page (VLM) | Extract structured fields, summarize, answer questions, identify tables | Scanned PDFs have no text layer; multi-column layouts confuse text extraction; tables are reliably difficult for all three approaches |
| Audio | WAV, MP3, OGG | Transcribed to text via a speech recognition model (most commonly Whisper: `pip install openai-whisper`) then treated as text, OR processed as audio tokens by a native audio model | Varies by speech rate: ~150 words/minute -> ~200 tokens/minute | Transcription, speaker identification, meeting summarization | Transcription errors (wrong words) propagate through the entire pipeline; accents and background noise increase error rate; tone and emotion are lost in text transcription |
| Video | MP4, MOV, frames | Sampled as a sequence of image frames (typically 1 frame/second to 1 frame/5 seconds); audio track transcribed separately | Very high: 100 frames × 512 tokens/frame = 51,200 tokens for a 100-second video | Temporal scene understanding, action recognition, caption generation per frame | Extremely high token cost makes long videos expensive; temporal reasoning across hundreds of frames is unreliable; sampling strategy loses frames containing important moments |
| Code File | .py, .js, .ts, .java, etc. | Passed as plain text (most common), as a serialized Abstract Syntax Tree, or queried incrementally via tools (look up function definition, list imports) | Proportional to file size; a 500-line Python file ≈ 2,000-3,000 tokens | Explanation, refactoring, bug detection, docstring generation, test writing | Files larger than ~1,000 lines exceed context windows; structural relationships (call graphs, inheritance) are invisible in flat text |

### Questions to Work Through

1.  An agent is asked to process a 100-page PDF invoice archive.  Calculate the approximate token cost of each approach (text extraction, OCR, and VLM) for 100 pages.  At the rate of $0.003 per 1,000 input tokens (a rough mid-range API price), what is the cost difference between the cheapest and most expensive approaches?

   *Hint:* Text extraction: ~500 tokens/page × 100 pages = 50,000 tokens.  VLM (one image per page): ~768 tokens/image × 100 pages = 76,800 tokens.  But what happens when the PDFs are scanned (image-only), which approaches still work?

2.  A customer service agent transcribes voice calls and then processes the transcripts to extract action items.  The transcription error rate is 3% of words (a realistic Whisper error rate in noisy call centers).  For a 500-word conversation, estimate the number of errors.  How many of those errors are likely to affect downstream extraction of fields like names, dates, and dollar amounts?

   *Hint:* 3% of 500 words = 15 expected errors.  Names, dates, and amounts are high-information words; the model cannot guess them from context if it mishears them.  Compare this to common words like "the" or "and" where context allows recovery.

3.  The same image is processed by a VLM to extract an invoice total.  The first extraction returns "$1,247".  The second extraction (with the same prompt, same image) returns "$1,274".  What does this tell you about the reliability of VLM extraction for numeric fields, and what mitigation strategy would you add to the pipeline?

   *Hint:* The model has some uncertainty about the digits; its output is sampled, not deterministic at temperature > 0.  Running extraction twice and comparing results is a simple way to detect low-confidence extractions.  What would you do when the two runs disagree?

Now that we understand the token-level mechanics of modality conversion, we can look at specific models and tools, and what makes each one the right choice for a given document type.

---

# Part II: Vision Language Models

In this part, you will survey the landscape of Vision Language Models (VLMs) and learn the document processing pipeline that real agents use for PDFs.  The goal is to know which tool to reach for and when, and to understand why the "obvious" choice (just send the image to the model) often fails on structured data like tables.

## 2.  Notable VLMs

A **Vision Language Model** (VLM) is an LLM extended with an image encoder.  The image encoder (typically a Vision Transformer, or ViT) converts an image into a sequence of patch embeddings, which are then projected into the same embedding space as text tokens and concatenated with the text input.

Notable VLMs include:

| Model | Provider | Access Method | Strengths | Best For | Cost Note |
|---|---|---|---|---|---|
| GPT-4o | OpenAI | API (`pip install openai`) | Widely deployed; strong on document understanding, UI interaction, and dense text in images | Production deployments where reliability and support matter | ~$0.005 per image input (1024×1024) |
| Claude Sonnet / Opus | Anthropic | API (`pip install anthropic`) | Effective on long-document vision tasks; strong at nuanced caption and structured analysis; 200K context window | Document-heavy RAG pipelines; tasks requiring long reasoning over multi-page documents | ~$0.003-$0.015 per image depending on model |
| LLaVA (open-source) | Multiple research groups | Local via Ollama (`ollama pull llava:7b`) | Visual instruction tuning on LLaMA base; good for research experiments; free to run locally | Research and education; tasks where data privacy prohibits sending images to the cloud | Free to run locally; requires 8+ GB RAM |
| Moondream (open-source) | Vikhyat Kopula | Local via Ollama (`ollama pull moondream`) | Very small (1.8B parameters); designed for edge deployment; fast even on CPU | Embedded devices, offline use, situations where a 7B model is too large | Free; fits in 4 GB RAM |
| Gemma 3 multimodal | Google DeepMind | Local via Ollama (`ollama pull gemma3:12b`) | Vision-capable variant; strong grounding; 128K context for long documents | Long-document vision tasks locally | Free to run locally; requires 16 GB RAM |

The common thread: the image becomes tokens.  The model never "looks" at pixels the way a human does; it processes a patch-level compressed representation.  This is why fine detail, small text, and complex layouts can confuse VLMs even when they look clear to a human eye.

---

## PDF and Document Processing Approaches

When an agent needs to work with a PDF, there are three main approaches, each with different trade-offs.  Understanding these trade-offs lets you choose the right tool for the document type in front of you.

| Approach | Tool | Install Command | When It Works Well | When It Fails | Typical Speed |
|---|---|---|---|---|---|
| Text Layer Extraction | PyMuPDF (`fitz`) | `pip install pymupdf` | Digitally created PDFs with an embedded text layer (most modern office documents, contracts, reports) | Scanned documents (image-only PDFs) where there is no text layer; multi-column layouts where text order is extracted incorrectly | Very fast: 100 pages in under 1 second |
| OCR (Optical Character Recognition) | Tesseract via pytesseract | `pip install pytesseract` (requires Tesseract binary: `brew install tesseract` or `apt-get install tesseract-ocr`) | Scanned documents, photos of text, handwritten forms (with lower accuracy) | Handwriting, unusual fonts, very poor scan quality, rotated text | Slow: 2-5 seconds per page |
| Vision-Based Extraction | Any VLM (GPT-4o, Claude Vision, LLaVA) | `pip install openai` or `pip install anthropic` | Complex layouts where context matters for interpretation (e.g., "the amount in the 'Total' row"), forms with unusual structures, documents where text and graphics must be interpreted together | Dense tables with many small numbers (high hallucination risk); documents requiring pixel-perfect numeric accuracy | Medium: 3-10 seconds per page via API |

In practice, robust document processing pipelines combine all three: extract text where available, fall back to OCR for scanned pages, and use vision for validation or for documents that defeat both.

> **Common Misconception:** Many developers assume that a VLM "sees" a PDF the way a human reads it: understanding layout, inferring meaning from position, and reading left-to-right correctly.  In reality, **VLMs frequently misread tables, merge adjacent cells, transpose rows and columns, and hallucinate values in dense numeric regions**.  Always validate extracted numbers against a range check (is this dollar amount plausible for this type of invoice?) before using them downstream.

### Questions to Work Through

4.  You are building an agent to process medical imaging reports that arrive as scanned PDFs.  Some are typed, some are handwritten, and all contain critical numeric values (lab results, dosages).  Sketch a multi-stage pipeline that maximizes accuracy on numeric values while minimizing cost.  Justify each stage.

   *Hint:* Stage 1: try text extraction (fast, accurate for typed documents).  Stage 2: if text extraction returns empty or garbled text, try OCR. Stage 3: for all numeric fields, use a VLM to cross-check (extract the same field twice using different prompts and compare).  Stage 4: flag any extraction where Stage 1, 2, and 3 disagree for human review.

5.  A coding agent is given a 2,000-line Python codebase to refactor.  It cannot fit the entire codebase in its context window.  Design a tool-based approach where the agent queries the codebase incrementally rather than reading it all at once.  What tools would you give it, and in what order would it use them?

   *Hint:* Tools to consider: `list_files()`, `read_function(name: str)`, `find_all_callers(function_name: str)`, `search_code(pattern: str)`.  The agent should plan its refactoring by understanding the structure first (which functions exist, which call which), then reading only the functions it needs to modify.

6.  An audio processing agent transcribes a doctor-patient consultation and extracts the patient's current medications and dosages.  What specific types of transcription errors are most dangerous in this scenario, and how would you design a validation step to catch them before the extracted data is written to an electronic health record?

   *Hint:* "Metformin 500mg" vs. "Metformin 50mg": a single dropped digit can cause a 10x dosage error.  "Lisinopril" vs. "Lisinopril": drug names are often unfamiliar to the ASR model and easily mangled.  What validation can you do with just a known drug name list and a dose range table?

The conversion failures you've seen in specific tools are all instances of a deeper structural problem, and grounding is the technique that makes those failures detectable rather than silent.

---

# Part III: The Modality Bottleneck and Grounding

In this part, you will examine the fundamental limitation of multimodal systems (lossy conversion) and the concept of grounding, which connects a model's claims back to specific locations in its input.  Grounding is what makes multimodal agent outputs verifiable rather than just plausible.

## 3.  The Modality Bottleneck

All modalities eventually become tokens.  This unification is the source of multimodal models' power (a single architecture reasons across modalities), but it introduces a fundamental limitation: **lossy conversion**.

When an image is encoded into patch embeddings, fine spatial detail is compressed and potentially lost.  When audio is transcribed, tone, emphasis, and speaker identity may be lost.  When a PDF is parsed, layout relationships may be lost.  When code is summarized, implementation details may be lost.

These losses are not bugs; they are the cost of compression.  The implication for agents is that **errors introduced at modality conversion propagate through the entire pipeline**.  If the VLM misreads a digit in an invoice, every downstream tool call based on that digit will be wrong.  If the transcription of a voice command mis-hears a name, the agent will act on the wrong entity.

## Mitigation Strategies for Modality Errors

| Failure Mode | Example | Mitigation Strategy | How to Implement |
|---|---|---|---|
| VLM misreads a small digit in a table | Invoice total read as "$1,274" instead of "$1,247" | Multi-pass verification: extract the field twice with different prompts and compare | Run extraction twice with prompts "What is the total amount?" and "What number appears in the bottom-right of the table?"; flag discrepancies |
| OCR fails on handwritten text | Patient name "McEnroe" read as "Mc Enroe" or "Mcenroe" | Phonetic fuzzy matching against a known entity list | `pip install thefuzz`; match extracted name against patient roster using fuzzy string matching with threshold > 90 |
| Audio transcription mishears a drug name | "Metformin" transcribed as "Metformine" | Dictionary constraint: only accept drug names on an approved formulary | After transcription, check every noun against a drug name database; flag unrecognized names for human review |
| VLM hallucinates a value for an unclear region | Invoice field is partially obscured; VLM guesses "$500" | Confidence scoring: extract logprobs or re-extract and compare | Use model's logprobs (available in OpenAI API) to estimate confidence; alternatively, extract the same field three times and flag majority-vote disagreements |
| Video frame sampling misses a key event | A 1-frame-per-second sample misses a 0.5-second event at 0:47 | Adaptive sampling: use motion detection to identify high-activity frames | `pip install opencv-python`; compute frame-to-frame pixel difference and oversample during high-motion periods |

## 4.  Grounding

**Grounding** refers to connecting a model's output back to specific locations in its input: pointing at the exact region of an image, the exact sentence in a document, or the exact line of code that the model's response refers to.

Grounding is not automatic.  A model can say "the error is in the header section" without specifying where the header is.  A model can say "the invoice total is $1,247" without citing which pixel region it read that from.

Models trained for grounding tasks (like PaliGemma with referring expression comprehension, or GPT-4o with bounding box output) can produce coordinates or region identifiers along with their claims.  This matters for agents because:

- **Verification**: If the agent can point to the evidence, a human reviewer or a downstream tool can verify the claim
- **UI interaction**: An agent clicking on a UI element must specify coordinates, not just describe what it wants to click
- **Debugging**: When a grounded model is wrong, you can see exactly what region misled it

**Multimodal Retrieval:** Standard RAG retrieves text documents using embedding similarity.  **Multimodal retrieval** extends this to images and mixed-content documents.  CLIP (Contrastive Language-Image Pretraining, `pip install clip`) trains image and text encoders jointly so that images and captions describing them have similar embeddings.  This enables queries like "find me images of broken login forms" against an image database, or "find me documents that visually look like W-2 forms", without requiring that every artifact be manually transcribed to text first.

---

## Grounding Exercise: Identifying a Broken UI Element

Imagine an agent performing visual regression testing.  It receives a screenshot of a web page and must identify which element is broken.

**Why This Is Hard:**

- The model sees the entire screenshot, not individual elements.  Without grounding, it can say "the login button looks wrong" but not specify which pixel region.
- "Broken" is ambiguous: is it a style issue?  A positioning issue?  A functional issue (the button exists but does nothing)?
- The model has no access to the DOM, CSS, or JavaScript; it sees only the rendered output.
- False positives (reporting a correctly rendered element as broken) are as problematic as false negatives.

**What Grounding Means Here:**

Grounding means the model outputs a bounding box or click coordinate alongside its diagnosis: "The 'Submit' button at coordinates (412, 678) to (598, 712) appears to be overlapping with the footer, and its background color (#f5f5f5) is identical to the page background, making it invisible."  This is actionable; an engineer can navigate to exactly that region.

**How to Verify the Agent Pointed to the Right Element:**

- **Ground truth comparison**: If you have a reference screenshot of the correct UI, diff the flagged region between the broken and correct screenshots and confirm they differ.
- **DOM cross-reference**: Map the bounding box back to a DOM element using browser automation tooling (Playwright's `page.locator` at those coordinates) and confirm the element's identity.
- **Human review**: For high-stakes testing, route flagged regions to a human reviewer who confirms the diagnosis before filing a bug report.
- **Re-query with crop**: Crop the flagged region and re-query the model asking it to describe only that region.  If the description is consistent with the original diagnosis, confidence increases.

A VLM is processing a screenshot of a spreadsheet to extract all cell values.  The most likely failure mode is:

- Small text, merged cells, or unusual formatting confuses the model, causing extraction errors or missed values.
- The model refuses to process spreadsheets on ethical grounds; VLMs do not treat spreadsheet images as a restricted category; refusals occur for content policy reasons, not document type.
- All values are extracted correctly but stored in the wrong column order; column-order confusion is a real failure mode, but extraction errors and missed values from visual ambiguity are far more common.
- The model can only process image files smaller than 1 MB; file size limits are an API constraint, not a capability limitation of the model itself; most APIs accept images well above 1 MB.

<details markdown="1"><summary>Answer</summary>

Small text, merged cells, or unusual formatting confuses the model, causing extraction errors or missed values.

</details>

With the failure modes of individual components understood, we can now see how they combine (and compound) in a real end-to-end agent pipeline.

---

# Part IV: Agent Pipeline Deep Dive

In this part, you will trace a complete, real-world multimodal pipeline step by step, from receiving a raw image to writing validated data to a database.  Each step in the table reveals a different failure mode and its mitigation, illustrating why production pipelines require multiple stages rather than a single model call.

## Extracting Data from a Hospital Intake Form

Consider an agent tasked with digitizing handwritten hospital intake forms.  Each step uses different tools and introduces different failure modes.

| Step | Tool Used | Install / Access | Input | Output | Failure Mode | Mitigation |
|:-----|:---------|:------|:-------|:------------|:------------|:------------|
| 1. Receive image | File ingestion via Python `open()` or S3 client | `pip install boto3` for S3 | Scanned JPEG of handwritten form | Raw image bytes | Image too low-resolution (below 150 DPI), file corrupt, or wrong document type (staff uploaded wrong form) | Validate image resolution before processing: `from PIL import Image; img = Image.open(path); assert min(img.size) >= 1200` |
| 2. Vision LLM extracts fields | GPT-4o or Claude Vision | `pip install openai` or `pip install anthropic` | Image bytes + structured extraction prompt requesting JSON | JSON: `{"patient_name": "...", "dob": "...", "medications": [...], "allergies": [...]}` | Misread handwriting; merged adjacent fields; hallucinated values for unclear regions; refused to read medical content | Provide a few-shot example in the prompt showing the exact JSON format expected; use temperature=0 for determinism |
| 3. Validate JSON against schema | Pydantic or JSON Schema | `pip install pydantic` | Extracted JSON string | Validated Pydantic model object, or validation error | Schema mismatch if model invents fields; type errors for dates formatted as "Jan 5" instead of "2024-01-05" | Use `model = IntakeForm.model_validate_json(raw_json)` and catch `ValidationError` explicitly |
| 4. Flag low-confidence fields | Re-extraction comparison heuristic | No additional install; re-run Step 2 with same prompt | Validated JSON + second extraction run | Same JSON with added `"confidence": "low"` on fields where two runs disagree | Overconfidence: model can be wrong and highly confident; double extraction does not catch systematic errors | Add range checks independent of the model: dates must be plausible birth years (1900-2010), medication names must appear in a formulary |
| 5. Write to database | Database write tool (psycopg2 for Postgres, etc.) | `pip install psycopg2-binary` | Validated (and flagged) JSON | Database record with timestamp, form_id, operator_id | Race condition if form submitted twice; flagged fields written without human review; PII handling requirements not met | Use database transactions for idempotency (`INSERT ... ON CONFLICT DO NOTHING`); route flagged records to a human review queue rather than writing directly |

Note that Steps 4 and 5 are critical controls: flagging low-confidence fields prevents bad data from entering the database silently, and Step 5 should route flagged records to a human reviewer rather than writing them directly.

---

# Part V: Synthesis and Practice

In this part, you will build and evaluate real multimodal pipelines using the tools covered in earlier parts.  The exercises are designed to surface failure modes you can only discover by running the system on real data; accuracy numbers that surprise you are the most valuable result.

## Exercises

1.  *VLM extraction benchmark.*  Take 10 screenshots of web forms, invoices, or structured documents.  Using a VLM of your choice (LLaVA locally via `ollama pull llava:7b`, or GPT-4o/Claude via API), extract the structured fields from each.  Manually compare the extracted values to the ground truth.  Report: field-level accuracy, which field types are most often wrong, and the cost of API calls if you used a cloud model.

   *What to do:* Create a simple evaluation script that compares extracted JSON to a manually labeled ground truth JSON. Use exact match for numeric fields and case-insensitive match for text fields.

   *Starter hint:* The code below shows the full extraction pipeline for a single image; notice the `temperature=0` setting (which makes extraction deterministic) and the prompt that requests `null` for any field not visible (which prevents hallucination of missing fields):

   ```python
   import base64
   from openai import OpenAI
   from pathlib import Path

   client = OpenAI()  # uses OPENAI_API_KEY from environment

   def extract_fields_from_image(image_path: str) -> dict:
       """Extract structured fields from a document image using GPT-4o."""
       image_data = base64.b64encode(Path(image_path).read_bytes()).decode()

       response = client.chat.completions.create(
           model="gpt-4o",
           messages=[{
               "role": "user",
               "content": [
                   {
                       "type": "text",
                       "text": """Extract the following fields from this document and return ONLY valid JSON:
   {"vendor_name": str, "invoice_date": "YYYY-MM-DD", "total_amount": float, "invoice_number": str}
   If a field is not visible, use null."""
                   },
                   {
                       "type": "image_url",
                       "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                   }
               ]
           }],
           temperature=0  # deterministic for extraction tasks
       )
       import json
       return json.loads(response.choices[0].message.content)

   # For local inference with LLaVA via Ollama:
   # from openai import OpenAI
   # client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
   # model = "llava:7b"  # then same call structure
   ```

   *You've succeeded when:* You have a table of 10 documents × field count with accuracy percentages, and you can identify which field type (text name, date, dollar amount, address) has the lowest extraction accuracy and explain why.

2.  *Audio pipeline construction.*  Using Whisper (`pip install openai-whisper`) and an LLM, build a meeting-to-action-items pipeline: record or use a sample audio file, transcribe it, and extract a structured list of action items with assignee and due date.

   *What to do:* Transcribe the audio, then send the transcript to an LLM with a structured extraction prompt.  Validate that each action item has the required fields.

   *Starter hint:* The code below chains two steps (Whisper transcription followed by LLM extraction) look for how the transcript is passed verbatim into the extraction prompt, and consider what happens to the extraction if the transcription contains a word error:

   ```python
   import whisper  # pip install openai-whisper

   # Load model (first run downloads ~1.5 GB for "medium", ~150 MB for "tiny")
   model = whisper.load_model("medium")  # or "tiny" for speed, "large" for accuracy

   # Transcribe
   result = model.transcribe("meeting_recording.mp3")
   transcript = result["text"]
   print(f"Transcript ({len(transcript.split())} words): {transcript[:200]}...")

   # Extract action items with an LLM
   from openai import OpenAI
   client = OpenAI()

   extraction_prompt = f"""From this meeting transcript, extract all action items.
   Return ONLY valid JSON with this schema:
   {% raw %}{{"action_items": [{{"description": str, "assignee": str, "due_date": str or null}}]}}{% endraw %}

   Transcript:
   {transcript}"""

   response = client.chat.completions.create(
       model="gpt-4o-mini",  # cheaper model for extraction tasks
       messages=[{"role": "user", "content": extraction_prompt}],
       temperature=0
   )
   import json
   action_items = json.loads(response.choices[0].message.content)
   print(f"Found {len(action_items['action_items'])} action items")
   for item in action_items['action_items']:
       print(f"  - {item['description']} (Owner: {item['assignee']}, Due: {item['due_date']})")
   ```

   *You've succeeded when:* You can demonstrate the full pipeline (audio in, structured JSON action items out) and you have tested it on at least one audio file where you know the ground truth (either you recorded it yourself or you have a transcript).

3.  *Modality comparison experiment.*  Take the same 5 documents in two formats: as a text file (typed text) and as a screenshot.  Extract the same structured fields using the text directly vs. using the VLM on the screenshot.  Report: accuracy difference, token cost difference, and which document types favor one approach over the other.

   *What to do:* For text extraction, send the document text directly to the LLM. For vision extraction, encode the screenshot as base64 and send it to a VLM. Compare accuracy and cost.

   *Starter hint:* Expected finding: text extraction is almost always more accurate and cheaper than VLM extraction for digitally-created documents.  VLM wins for documents with complex layout where text extraction loses column structure, and for scanned documents where there is no text layer to extract.

   *You've succeeded when:* You have a 5×2 table (documents × approaches) with per-field accuracy and cost in tokens/dollars, and a written recommendation for each document type.

4.  *Grounding implementation.*  Using a VLM that supports bounding box output (GPT-4o with structured output, or a grounding-trained model), process a screenshot of a web page and ask the model to identify three specific UI elements (a button, a form field, and an error message) and return their bounding box coordinates.  Verify by cropping the image to those coordinates and confirming the element is present.

   *What to do:* Ask the VLM to return `{"elements": [{"name": "Submit button", "bbox": [x1, y1, x2, y2], "confidence": "high/low"}]}`.  Crop the image using Pillow and display the crops.

   *Starter hint:*
   ```python
   from PIL import Image

   def crop_and_show(image_path: str, bbox: list, label: str):
       """Crop an image to a bounding box and save for verification."""
       img = Image.open(image_path)
       x1, y1, x2, y2 = bbox
       cropped = img.crop((x1, y1, x2, y2))
       cropped.save(f"crop_{label}.png")
       print(f"Saved crop_{label}.png ({x2-x1}×{y2-y1} pixels)")

   # After extracting bboxes from VLM response:
   for element in extracted["elements"]:
       crop_and_show("screenshot.png", element["bbox"], element["name"].replace(" ", "_"))
   ```

   *You've succeeded when:* You have saved cropped images for each element and can confirm visually that the VLM pointed to the correct region (not just the right general area).  Note and document any cases where the bounding box was incorrect.

---

## Reflection Prompt

*Personal:* Think about how you process information differently when you read a text description of something versus when you see a photo or diagram.  What kinds of information do you extract from images that you would miss in a text description?  Now think about what a VLM might miss that a human would catch: what does this suggest about where humans should remain in the loop?

*Technical:* All modalities eventually become tokens.  This means lossy conversion is unavoidable; some information is always lost in the encoding step.  For a medical imaging agent that processes X-ray images, what specific information might be lost when a complex radiological image is encoded as ~512 patch tokens?  What does this loss imply about deploying VLMs as autonomous decision-makers in radiology?

*Societal:* Multimodal agents can process photos of people, audio recordings of conversations, and documents that were not intended to be machine-readable.  What new privacy risks emerge when AI agents can extract structured data from a photo of a whiteboard taken at a business meeting, or from a voice recording captured in a public space?  What norms or regulations would you want to see govern these capabilities?

---

## Where This Goes Next

Now that you understand multimodal agents and how they process different input types, the next module examines the frameworks (LangChain, CrewAI, AutoGen, and Agno) that provide scaffolding for multi-agent pipelines, and helps you decide which level of abstraction belongs in which project.

---

## Further Reading

- Radford et al. "Learning Transferable Visual Models From Natural Language Supervision."  (CLIP paper) *ICML* (2021).
- Liu et al. "Visual Instruction Tuning."  (LLaVA paper) *NeurIPS* (2023).
- OpenAI. "GPT-4 Technical Report." arXiv:2303.08774 (2023).  Section on vision capabilities.
- Whisper model card and documentation: https://github.com/openai/whisper
- PaliGemma model card (for grounding tasks): https://ai.google.dev/gemma/docs/paligemma
