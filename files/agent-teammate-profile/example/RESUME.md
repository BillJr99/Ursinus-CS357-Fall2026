# Resume — "Scribe"

> Worked example for the CTP2 case study.

## Summary
A course-content maintenance agent specialized in LiaScript/Markdown authoring
and Jekyll site upkeep. Hire it for content edits, new activities/labs in an
established style, and keeping the build green — not for novel research or
high-stakes infrastructure changes.

## Core skills
- LiaScript and Markdown authoring in the CS357 POGIL house style.
- Jekyll site mechanics: front-matter, the `schedule:`/`textbooks:` YAML, build.
- Git: branching, chunked commits, clear messages.
- Light Python/shell for validation scripts.

## Tools & access
| Tool / MCP | What it's used for | Permission level |
|------------|--------------------|------------------|
| shell | run `jekyll build`, YAML checks | reads free; writes scoped to repo |
| git   | branch, commit on `claude/*`   | no force-push, never `gh-pages` |
| filesystem | edit `_pages/`, `files/`   | scoped to the mounted workspace |

## Model & runtime
- Models: a strong model for planning and authoring; a cheaper model is fine for
  mechanical batch edits (see `liascript-costoptimization.md`).
- Runtime: the hardened container in `files/agent-yolo-container/`.

## Selected prior work / track record
- Batch "beginner-friendliness" passes across dozens of activity files.
- Added POGIL activities (Agent Skills & Plugins; Obsidian↔GitHub sync) matching
  the existing template, with schedule wiring.

## Known limitations (read this)
- Can hallucinate library APIs and flag names — verify against real docs/MCP.
- Weak at long-horizon work without checkpointing; relies on stop/start discipline.
- Not to be trusted with merges, pushes to shared branches, or any irreversible
  or outward-facing action unsupervised.
