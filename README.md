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

## Pre-Merge Checks

The Pages workflow builds only on a push to `gh-pages`, so a bad layout name or a
stray Liquid delimiter is not caught until after the merge. `bin/check-site.py`
runs the checks that would have caught the ones we have actually hit:

```bash
git submodule update --init _layouts     # the layout check needs these present
pip install pyyaml
python3 bin/check-site.py
```

It verifies that every `layout:` names a file that exists in `_layouts/`, that
the deck invariant below holds, that no deck uses Liquid, that no page has a
literal `{{ }}` outside `{% raw %}`, and that every relative front-matter link
resolves to a real permalink.

Two of those deserve a word, because both fail silently rather than loudly:

- **Layouts.** Jekyll warns and drops the page's chrome when `layout:` names a
  file that is not in `_layouts/`. The available layouts come from the
  `_layouts` submodule, so check there rather than guessing: `default-standard`
  is the one course pages use, and there is no `tutorial` layout.
- **Literal braces.** Liquid runs before Markdown, so a `{{ ... }}` in prose or
  inside a fenced code block is evaluated and deleted even though it looks
  quoted. GitHub Actions YAML and Python `.format()` examples are the usual
  victims. Wrap the block in `{% raw %}` / `{% endraw %}`. This does not apply
  to decks, which Jekyll never processes.

To reproduce the Pages build locally, `bundle install` then build with Jekyll;
`jekyll-github-metadata` needs `JEKYLL_GITHUB_TOKEN` set or it cannot reach the
API and the build stops.

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

**A file in `_pages/Activities/` is a deck if and only if it is a `link:` on a
syllabus schedule day.** That is the whole rule, and it is checkable:

```bash
# prints the decks present that are not a scheduled lecture; should print nothing
python3 - <<'CHECK'
import yaml, os, glob
d = yaml.safe_load(open('_pages/syllabus.md').read().split('---', 2)[1])
lecture = {os.path.basename(e['link']) for e in d['schedule']
           if isinstance(e.get('link'), str) and e['link'].startswith('Activities/')}
have = {os.path.basename(f) for f in glob.glob('_pages/Activities/liascript-*.md')}
print('\n'.join(sorted(have - lecture)))
CHECK
```

Everything else lives in `_pages/Tutorials/` as an ordinary Jekyll page. A deck
is what a class works through together in seventy-five minutes; a page is what
someone reads on their own, and the reading lists point at pages.

Reading lists therefore do not use the `liapage` flag. The only `liapage: true`
in `_pages/syllabus.md` is the day's own `link:`. Readings point at books,
papers, external sites, or a page under `_pages/Tutorials/`. Those pages use
`layout: default-standard` and are linked by permalink:

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

One further sweep is unavoidable, and it covers two things rather than one.
LiaScript fetches deck files straight from GitHub raw, so Jekyll never processes
them: a deck has no front matter, and `{{ site.baseurl }}` inside one renders as
literal text rather than a URL. That means both the `comment: Render with ...`
header lines **and** any link from a deck to a course page name the repository
literally. Retarget both with:

```bash
sed -i -e 's|BillJr99/Ursinus-CS357-Fall2026/|BillJr99/<new-repo>/|g' \
       -e 's|billmongan.com/Ursinus-CS357-Fall2026/|billmongan.com/<new-repo>/|g' \
       _pages/Activities/liascript-*.md
```

Inside a deck, a link to a course page must be the absolute URL for that reason:

```
[Docker from Zero](https://www.billmongan.com/Ursinus-CS357-Fall2026/Tutorials/Docker)
```

Pages are Jekyll-processed and use `{{ site.baseurl }}` in their bodies as usual.
Page **front matter** is a third case: Liquid does not run there either, so
`rlink` values are relative paths resolved against the page's own URL
(`Tutorials/Docker` from the syllabus at the site root, `../Tutorials/Docker`
from a page one level down).

The Class Agendas and Class Notes pages in the OneNote notebook's `_Teacher Only`
section carry the same literal repository name in their links, so they need the
same retarget when the term rolls over.

---

## Course License

All original course materials in this repository (slides, activities, notes, and assessments authored by the course instructor) are licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** license. See the [LICENSE](LICENSE) file for the full license text.

Third-party submodules in `files/` retain their original licenses as listed above.
