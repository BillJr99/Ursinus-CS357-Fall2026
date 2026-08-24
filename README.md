# CS357: Foundations of Artificial Intelligence, Fall 2026

This repository contains the course website and materials for **CS357: Foundations of Artificial Intelligence** at Ursinus College. The course explores how modern AI systems are built, from traditional machine learning and deep learning through large language models, retrieval-augmented generation, and autonomous agents, with sustained attention to ethics, safety, and societal impact.

**Course Website:** [https://www.billmongan.com/Ursinus-CS357/](https://www.billmongan.com/Ursinus-CS357/)

---

## Third-Party Materials

This repository includes six open-source educational resources as git submodules in the `files/` directory. These resources are not reproduced verbatim; rather, concepts and themes from them were adapted and restructured into original course activities. Citations appear in the individual activity files where relevant.

| Resource | Author(s) | License | Description |
|----------|-----------|---------|-------------|
| [AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch) | Rohit Ghumare et al. | MIT License | A 20-phase curriculum covering math foundations, ML, deep learning, LLMs from scratch, agents, production systems, and ethics. |
| [ML Course](https://github.com/ML-course/master) | ML-course team | CC0 License | Open-source ML course with Jupyter notebooks covering supervised and unsupervised learning, deep learning, and statistical methods. |
| [ML Animated](https://github.com/markhliu/ml_animated) | Mark Liu | License not specified; please check the repository before redistribution | Animated Jupyter notebooks for gradient descent, CNNs, and reinforcement learning. |
| [RAG from Scratch](https://github.com/pguso/rag-from-scratch) | pguso | MIT License | JavaScript-based RAG tutorials covering embeddings, vector stores, and retrieval strategies. |
| [RAG from Scratch (LangChain)](https://github.com/langchain-ai/rag-from-scratch) | LangChain AI | MIT License | Python notebooks covering indexing, retrieval, and generation for RAG systems. |
| [AI Agents from Scratch](https://github.com/pguso/ai-agents-from-scratch) | pguso | MIT License | Fifteen progressive examples covering agent reasoning patterns (ReAct, ToT, GoT, CoT, AoT), tool use, and memory. |

> **Note:** Concepts from the above repositories were adapted (not copied verbatim) into course activities. Where a specific resource inspired a section of an activity, a citation is included in that activity file.

---

## Course Framework

This course is based on **The AI Fluency Framework** by Prof. Rick Dakan (Ringling College of Art and Design) and Prof. Joseph Feller (University College Cork), developed with Anthropic. Its four competencies (Delegation, Description, Discernment, and Diligence) organize the early activities. The summary slide is included at `files/ai-fluency/`, and the framework and its summary materials are released under **CC BY-NC-SA 4.0** (compatible with this course's license). Attribution appears in the materials that draw on it (e.g., the [Ursinus-CS357-Overview](https://www.billmongan.com/Ursinus-CS357-Overview) welcome slide deck and `_pages/Activities/liascript-promptengineering.md`).

---

## Term Rollover

Deck links are not written out in full. A page body composes them from config:

```
{{ site.lia_viewer_url }}{{ site.raw_pages_url }}Activities/liascript-agentloop.md
```

and front matter, where Jekyll does not evaluate Liquid, uses a flag the syllabus
and assignment layouts expand:

```yaml
link: "Activities/liascript-agentloop.md"
liapage: true
```

Reading lists do not use that flag. A LiaScript deck is the thing the class works
through together, so the only `liapage: true` in `_pages/syllabus.md` is the day's
own `link:`. Readings point at books, papers, external sites, or a page under
`_pages/Tutorials/`, which holds the reference and procedural material that used
to live in decks. Those are ordinary Jekyll pages on `layout: default-standard`,
linked by permalink:

```yaml
rlink: "/Tutorials/Docker"
```

Depth that belongs with a session lives at the bottom of that session's own deck
under an `# Extension: ... (self-paced)` heading, rather than as a separate deck
in the reading list.

When starting a new term, the semester appears in exactly three places, all of
which have to be updated together:

- `baseurl` in `_config.yml`
- `raw_pages_url` in `_config.yml`
- `info.course_homepage` in `_pages/syllabus.md`

One further sweep is unavoidable. The `comment: Render with ...` header lines
inside `_pages/Activities/liascript-*.md` name the repository literally, because
LiaScript fetches those files straight from GitHub raw and Jekyll never processes
them. Retarget them with:

```bash
sed -i 's|BillJr99/Ursinus-CS357-Fall2026/|BillJr99/<new-repo>/|g' _pages/Activities/liascript-*.md
```

The Class Agendas and Class Notes pages in the OneNote notebook's `_Teacher Only`
section carry the same literal repository name in their links, so they need the
same retarget when the term rolls over.

---

## Course License

All original course materials in this repository (slides, activities, notes, and assessments authored by the course instructor) are licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** license. See the [LICENSE](LICENSE) file for the full license text.

Third-party submodules in `files/` retain their original licenses as listed above.
