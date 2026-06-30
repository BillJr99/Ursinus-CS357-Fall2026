# Resume — <Agent Name>

> The resume tells you (and the agent) what it is actually good at, what tools it
> can use, and — just as important — where its limits are. An honest resume
> prevents you from handing an agent a job it will fail at, and prevents the
> agent from over-claiming.

## Summary
<Two sentences: the agent's specialty and the kind of work it should be hired for.>

## Core skills
- <e.g. "Python and shell scripting for automation.">
- <e.g. "Editing LiaScript/Markdown course content.">
- <e.g. "Git workflows: branching, committing, opening PRs.">

## Tools & access
| Tool / MCP | What it's used for | Permission level |
|------------|--------------------|------------------|
| <e.g. shell> | <run tests, build> | <gated on writes> |
| <e.g. git>   | <branch, commit>   | <no force-push, no gh-pages> |
| <e.g. MCP: github> | <read issues/PRs> | <read-only> |

## Model & runtime
- Preferred model(s): <e.g. "a strong model for planning; a cheaper model for mechanical edits" — see `liascript-costoptimization.md`.>
- Runtime: <the hardened container in files/agent-yolo-container/.>

## Selected prior work / track record
- <Concrete past engagements or representative tasks, with outcomes. Honest, not aspirational.>

## Known limitations (read this)
- <e.g. "Can hallucinate APIs that don't exist — verify against real docs/MCP.">
- <e.g. "Weak at long-horizon tasks without checkpointing; needs stop/start discipline.">
- <e.g. "Should not be trusted with irreversible or outward-facing actions unsupervised.">
