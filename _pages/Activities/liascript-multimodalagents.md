# Multimodal Agents: Vision, Documents, and Code as First-Class Inputs
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-multimodalagents.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multimodalagents.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

## What Multimodal Means for Agents

Early language models accepted only text. Modern agents increasingly accept — and reason over — a much broader set of inputs: images, PDFs, audio recordings, video clips, and structured code files. This is what it means for an agent to be **multimodal**: its input space is not confined to a single modality.

This matters for agents more than for standalone chatbots because agents take actions. An agent that can see a screenshot can click the right button. An agent that can read a PDF contract can extract the clause that triggers a tool call. An agent that hears a voice command can act on it without a human typing an intermediate transcript.

Multimodality is not magic — it is an extension of the fundamental token-processing architecture. Every modality is ultimately encoded as a sequence of tokens before it enters the transformer. What differs is how that encoding happens, how lossy it is, and what kinds of errors result.

## Vision Language Models (VLMs)

A **Vision Language Model** (VLM) is an LLM extended with an image encoder. The image encoder (typically a Vision Transformer, or ViT) converts an image into a sequence of patch embeddings, which are then projected into the same embedding space as text tokens and concatenated with the text input.

Notable VLMs include:

- **GPT-4V / GPT-4o** (OpenAI): Widely deployed; strong on document understanding and UI interaction
- **Claude 3 / Claude Sonnet** (Anthropic): Effective on long-document vision tasks; nuanced caption and analysis
- **LLaVA** (open-source): Visual instruction tuning applied to LLaMA; good for research experiments
- **Moondream** (open-source): Small, fast, designed for edge deployment; fewer capabilities but efficient
- **PaliGemma** (Google): Gemma backbone with SigLIP vision encoder; strong on grounding tasks

The common thread: the image becomes tokens. The model never "looks" at pixels the way a human does — it processes a patch-level compressed representation. This is why fine detail, small text, and complex layouts can confuse VLMs even when they look clear to a human eye.

## Use Cases for Vision in Agents

**UI Testing and Interaction Agents**: Agents that navigate GUIs (web browsers, desktop apps) use screenshots to determine what to click. Instead of parsing the DOM, they interpret the visual rendering. This allows them to work on any UI, including those that are not web-based.

**Document Processing**: Invoices, forms, contracts, and certificates frequently arrive as scanned images or rendered PDFs. A vision agent can extract structured fields from these documents without requiring text extraction.

**Code Review**: Screenshots of error messages, IDE states, or terminal output can be processed by a vision agent to diagnose issues.

**Accessibility Agents**: Vision agents can describe UI elements for screen readers, generate alt text, or identify accessibility violations in a rendered page.

## PDF and Document Processing

When an agent needs to work with a PDF, there are three main approaches, each with different trade-offs.

**Text Extraction (parsing)**: Tools like PyMuPDF or pdfplumber extract the text layer directly from the PDF. This is fast and accurate for PDFs with a real text layer, but fails completely for scanned documents (image-only PDFs) and can produce garbled output for complex multi-column layouts.

**OCR (Optical Character Recognition)**: Tools like Tesseract or AWS Textract render the PDF to an image and then classify each region as text, performing character recognition. Better than parsing for scanned documents, but slow and prone to errors on handwriting, unusual fonts, or poor scan quality.

**Vision-Based Extraction**: Send the rendered PDF page directly to a VLM and ask it to extract the relevant fields. More flexible than OCR — the model can reason about context ("the number after the word 'Total:' is the invoice amount") — but expensive in tokens and prone to hallucination on dense numeric content.

In practice, robust document processing pipelines combine all three: extract text where available, fall back to OCR, and use vision for validation or for documents that defeat both.

## Audio Agents

Audio is increasingly a first-class input modality for agents. The dominant approach is **transcription first**: convert audio to text using a speech recognition model (most commonly OpenAI's Whisper), then pass the text to the language model for reasoning.

**Meeting Summarizers**: Record a meeting, transcribe it, chunk it, and have an agent extract action items, decisions, and summaries. This is a mature, widely deployed use case.

**Voice-Controlled Agents**: A user speaks a command. The audio is transcribed, the transcript is the agent's input, and the agent's text output is synthesized back to speech. The agent never processes audio natively — the modality conversion happens before and after the LLM.

**Native Audio Models**: More recent architectures (GPT-4o Audio, Gemini 1.5 Pro) can process audio tokens directly, enabling the model to reason about tone, pace, and speaker identity — capabilities that are lost in a transcription pipeline.

## Code as Structured Input

Source code can be treated as text — and often is. You can paste a Python file into a model and ask it to explain or refactor the code. But this treats code as flat text, ignoring its structure.

**Code as Text**: Fast and flexible. The model uses its training on code corpora to understand syntax and idioms. Fails on large codebases that don't fit in context.

**Code via AST**: Parse the code into an Abstract Syntax Tree and serialize the AST as structured data (JSON, S-expressions) before passing it to the model. This preserves structural relationships but produces verbose representations that consume many tokens.

**Code via Tools**: Rather than ingesting the entire file, give the agent tools to query the codebase incrementally — look up a function definition, list imports, find all callers of a method. This is the approach used by coding agents like GitHub Copilot Workspace and Aider.

The choice depends on task: understanding a small function favors text; refactoring a large system favors tool-based access.

## The Modality Bottleneck

All modalities eventually become tokens. This unification is the source of multimodal models' power — a single architecture reasons across modalities — but it introduces a fundamental limitation: **lossy conversion**.

When an image is encoded into patch embeddings, fine spatial detail is compressed and potentially lost. When audio is transcribed, tone, emphasis, and speaker identity may be lost. When a PDF is parsed, layout relationships may be lost. When code is summarized, implementation details may be lost.

These losses are not bugs — they are the cost of compression. The implication for agents is that **errors introduced at modality conversion propagate through the entire pipeline**. If the VLM misreads a digit in an invoice, every downstream tool call based on that digit will be wrong. If the transcription of a voice command mis-hears a name, the agent will act on the wrong entity.

Mitigation strategies include: confidence scoring (flag low-confidence extractions), multi-pass verification (extract twice and compare), human-in-the-loop validation for high-stakes fields, and format validation (extracted invoice amounts should be numeric and within a plausible range).

## Grounding

**Grounding** refers to connecting a model's output back to specific locations in its input — pointing at the exact region of an image, the exact sentence in a document, or the exact line of code that the model's response refers to.

Grounding is not automatic. A model can say "the error is in the header section" without specifying where the header is. A model can say "the invoice total is $1,247" without citing which pixel region it read that from.

Models trained for grounding tasks (like PaliGemma with referring expression comprehension, or GPT-4V with bounding box output) can produce coordinates or region identifiers along with their claims. This matters for agents because:

- **Verification**: If the agent can point to the evidence, a human reviewer or a downstream tool can verify the claim
- **UI interaction**: An agent clicking on a UI element must specify coordinates, not just describe what it wants to click
- **Debugging**: When a grounded model is wrong, you can see exactly what region misled it

## Multimodal Retrieval

Standard RAG (Retrieval-Augmented Generation) retrieves text documents using embedding similarity. **Multimodal retrieval** extends this to images and mixed-content documents.

**CLIP** (Contrastive Language-Image Pretraining) trains image and text encoders jointly so that images and captions describing them have similar embeddings. This enables queries like "find me images of broken login forms" against an image database, or "find me documents that visually look like W-2 forms."

Multimodal retrieval enables agents to search over screenshot libraries, document archives, and diagram repositories using natural language — without requiring that every artifact be manually transcribed to text first.

## Modality Comparison

| Modality | Input Format | How Model Receives It | Capabilities | Limitations |
|:---------|:------------|:---------------------|:-------------|:------------|
| Image / Screenshot | PNG, JPEG, WebP | Encoded as patch embeddings by a vision encoder; projected to text token space | Describe scenes, read text, identify UI elements, detect objects | Small text, fine detail, complex layouts can be missed; no spatial precision without grounding |
| PDF Document | Binary PDF | Parsed to text, OCR'd to text, or rendered to image and vision-encoded | Extract structured fields, summarize, answer questions | Scanned PDFs lose text layer; complex layouts confuse parsers; tables often misread |
| Audio | WAV, MP3, OGG | Transcribed to text (Whisper) or encoded as audio tokens (native audio models) | Transcription, speaker diarization, tone analysis (native models only) | Transcription errors propagate; accents and background noise increase error rate |
| Video | MP4, frames | Sampled as sequences of image frames; audio track transcribed separately | Temporal scene understanding, action recognition, caption per frame | High token cost; temporal reasoning across long videos is poor; sampling loses frames |
| Code File | .py, .js, .ts, etc. | Passed as text or as AST serialization | Explanation, refactoring, bug finding, docstring generation | Large files exceed context; structural relationships lost in flat text |

## Agent Pipeline: Extracting Data from a Hospital Intake Form

Consider an agent tasked with digitizing handwritten hospital intake forms. Each step uses different tools and introduces different failure modes.

| Step | Tool Used | Input | Output | Failure Mode |
|:-----|:---------|:------|:-------|:------------|
| 1. Receive image | File ingestion API | Scanned JPEG of handwritten form | Raw image bytes | Image too low-resolution; file corrupt; wrong document type |
| 2. Vision LLM extracts fields | GPT-4V / Claude Vision | Image + prompt requesting JSON field extraction | JSON: `{"name": "...", "dob": "...", "medications": [...]}` | Misread handwriting; merged fields; hallucinated values for unclear regions |
| 3. Validate JSON against schema | Pydantic / JSON Schema validator | Extracted JSON | Validated JSON or validation errors | Schema mismatch if model invents fields; type errors for dates formatted unexpectedly |
| 4. Flag low-confidence fields | Confidence scoring heuristic | Validated JSON + model logprobs or re-extraction comparison | Flagged fields with `"confidence": "low"` | Overconfidence — model can be wrong and confident; slow to re-extract every field |
| 5. Write to database | Database write tool | Validated (and flagged) JSON | Database record | Race condition if form submitted twice; PII handling requirements; flagged fields written without review |

Note that Steps 4 and 5 are critical controls: flagging low-confidence fields prevents bad data from entering the database silently, and Step 5 should route flagged records to a human reviewer rather than writing them directly.

## Grounding Exercise: Identifying a Broken UI Element

Imagine an agent performing visual regression testing. It receives a screenshot of a web page and must identify which element is broken.

**Why This Is Hard**:

- The model sees the entire screenshot, not individual elements. Without grounding, it can say "the login button looks wrong" but not specify which pixel region.
- "Broken" is ambiguous: is it a style issue? A positioning issue? A functional issue (the button exists but does nothing)?
- The model has no access to the DOM, CSS, or JavaScript — it sees only the rendered output.
- False positives (reporting a correctly rendered element as broken) are as problematic as false negatives.

**What Grounding Means Here**:

Grounding means the model outputs a bounding box or click coordinate alongside its diagnosis: "The 'Submit' button at coordinates (412, 678) to (598, 712) appears to be overlapping with the footer, and its background color (#f5f5f5) is identical to the page background, making it invisible." This is actionable — an engineer can navigate to exactly that region.

**How to Verify the Agent Pointed to the Right Element**:

- **Ground truth comparison**: If you have a reference screenshot of the correct UI, diff the flagged region between the broken and correct screenshots and confirm they differ.
- **DOM cross-reference**: Map the bounding box back to a DOM element using browser automation tooling (Playwright's `page.locator` at those coordinates) and confirm the element's identity.
- **Human review**: For high-stakes testing, route flagged regions to a human reviewer who confirms the diagnosis before filing a bug report.
- **Re-query with crop**: Crop the flagged region and re-query the model asking it to describe only that region. If the description is consistent with the original diagnosis, confidence increases.

## Knowledge Check

A VLM is processing a screenshot of a spreadsheet to extract all cell values. The most likely failure mode is:

- [(X)] Small text, merged cells, or unusual formatting confuses the model, causing extraction errors or missed values.
- [( )] The model refuses to process spreadsheets on ethical grounds.
- [( )] All values are extracted correctly but stored in the wrong column order.
- [( )] The model can only process image files smaller than 1 MB.

## Discussion Questions

**Question 1**: In what circumstances might a vision agent be *more* reliable for PDF extraction than a text-extraction pipeline? Consider the types of PDFs that each approach handles well and poorly. Give a concrete example of a PDF where you would choose the vision approach and explain your reasoning.

**Question 2**: An agent that "sees" a UI by processing screenshots differs fundamentally from an agent that "reads" a UI by parsing its DOM. List at least three capabilities that each approach has that the other lacks. In what scenario would you want both approaches working together?

**Question 3**: You are evaluating a multimodal agent that is supposed to identify and describe specific regions in medical images. How would you design an evaluation methodology to measure whether the agent correctly identified regions? What metrics would you use, and what would constitute a passing score for clinical use?
