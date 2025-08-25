---
layout: assignment
permalink: Assignments/ExploringAI
title: "Written Assignment: Exploring Generative AI"

info:
  points: 100
  goals:
    - Implement an AI technique such as prompt engineering, chaining, API integration
    - Demonstrate an AI technique through a working reproduction
    - Explain and illustrate a technical process in a brief presentation
    - Evaluate the strengths and weaknesses of the reproduced method, and reflect on its broader technical and ethical implications
  rubric:
    - weight: 20
      description: Conceptual Analysis
      preemerging: Names the chosen concept without explanation or shows major misunderstandings.
      beginning: States the concept and provides a partial explanation with some accurate details.
      progressing: Explains the concept accurately, identifies its purpose, and illustrates it with at least one relevant example.
      proficient: Explains the concept in depth, uses multiple relevant examples, and connects it to broader applications or implications of LLMs.
    - weight: 20
      description: Demonstration
      preemerging: Shows an attempt at reproduction but the process is incomplete or does not run.
      beginning: Shows a working attempt with partial steps explained; audience cannot fully reproduce it from the description.
      progressing: Demonstrates a working version and explains the key steps so the audience could reasonably reproduce it.
      proficient: Demonstrates a complete working version, explains all steps and decisions, and highlights potential challenges or variations for others who attempt it.
    - weight: 20
      description: Synthesis
      preemerging: Restates information from the video with little or no personal perspective.
      beginning: Adds a brief personal reflection or observation connected to the demonstration.
      progressing: Connects the reproduced work with personal reflection and identifies at least one implication or limitation.
      proficient: Integrates reflection with the demonstration, offers original insights about implications or improvements, and proposes at least one extension or application.
    - weight: 20
      description: Presentation
      preemerging: Presentation lacks structure or is difficult to follow.
      beginning: Presentation follows a basic structure (introduction, body, conclusion) but has unclear transitions or uneven pacing.
      progressing: Presentation is organized with clear transitions, uses appropriate visual/code artifacts.
      proficient: Presentation is well-organized with smooth transitions, and uses visual/code artifacts that directly support understanding.
    - weight: 20
      description: Report
      preemerging: Report is incomplete, lacks structure, or contains major inaccuracies; no citations or supporting evidence.
      beginning: Report includes introduction, body, and conclusion with some accurate content; citations are minimal or inconsistently formatted.
      progressing: Report is structured with accurate content, clear sections, and appropriate citations; explanations support reproducibility.
      proficient: Report is well-structured with accurate, detailed content, precise explanations for reproducibility, and consistent, properly formatted citations.
      
tags:
  - ai
  
---

## Exploration: Exploring AI with Andrej Karpathy

In this icebreaker assignment, you will watch the below video from Andrej Karpathy, one of the founders of OpenAI, which demonstrates several modern uses and techniques in generative AI systems.  Choose one of the techniques he demonstrates in that video, and reproduce it on the LLM model of your choice.

<iframe width="560" height="315" src="https://www.youtube.com/embed/EWvNQjAaOHw?si=kkcWK7yayKcz9fHx" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Specifically, he demonstrates the following techniques below.  

- **Model selection and context management**: using separate chats for separate conversations, and switching between models based on their underlying trained capabilities.
- **Reasoning models**: Use of reasoning-enhanced or "thinking" models for use in complex tasks like mathematics.  What does it mean for an AI tool to **think**?
- **Tool use**: Using web serach to augment the pre-trained text model, and using those tools to conduct "deep research."  What does **deep research** mean in this context?
- **Code writing**: Writing code with ChatGPT or Claude.  Does this code tend to work?  What are the risks in using automatically generated code?  How does this compare with the risks of copying code from the Internet?  What is an appropriate use of a tool like this?  Do some models write code of higher quality than others?
- **Multimodal AI**: Generate audo, images, or video using DALL-E or other tools, or ask the AI to inspect a song, video, or image and answer questions about it.
- **Memory**: LLMs seem to be able to remember information about you and about prior chats.  But it's a pre-trained model.  How do you think it does this?
- **Configuration**: Go to the Settings page of an LLM and configure its temperature or other parameters.  Configure its system message.  How do these affect the conversation you have with it or the answers it gives to questions?

### Your Task

1. Choose one of these topics and reproduce it using an LLM system of your choice (or, better yet, more than one to compare!)
2. Consider the questions I pose about each topic above.  How do you think it accomplishes this thing?
3. How might your tool be used effectively in practice?  Have you used it before, and how?  What are some of the risks or dangers in this technique?
4. Prepare a short (approximately 5 minute) presentation in which you demonstrate the technique and discuss your thoughts on these questions.
5. Summarize this presentation in a brief (1-2 pages) writeup report.  Be sure to cite any sources, including this video, your chosen LLM, and any outside references you consult.  If you conversed with an AI, include a log of the conversation you had.

### LLM Systems

Here are a few models that have free tiers that you could consider experimenting with:

- [ChatGPT (OpenAI)](https://chat.openai.com/)
- [Claude (Anthropic)](https://claude.ai/)
- [Poe (Quora)](https://poe.com/)
- [Grok (xAI)](https://x.ai/)
- [Gemini (Google DeepMind)](https://gemini.google.com/)
- [Mistral (Le Chat)](https://chat.mistral.ai/)