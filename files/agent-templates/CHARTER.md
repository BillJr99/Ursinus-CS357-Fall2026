# <ProjectName>

## Master Project Charter, Engineering Workflow, and Autonomous Development Plan

<!-- The constitution. Written once at project start, amended deliberately and rarely.
     Every agent session begins by (re)reading this document. Everything an agent is
     allowed or forbidden to do should trace back to a section here. -->

# Project Mission

<One or two sentences: what is being built and why. State the product, not the technology.>

# Engineering Philosophy

Every engineering decision should prioritize, in order:

1. <Highest-ranked value, e.g., Correctness / Preservation / Safety>
2. Reproducibility
3. Maintainability
4. Automation
5. Documentation

<!-- The ranking matters more than the list. When two values conflict mid-task,
     the agent resolves the conflict by rank instead of asking or guessing. -->

# Definition of Success

<A concrete, observable test for "done." Example: "A new contributor can clone the
repository, run one documented command, and produce a working build that passes the
standing test gate.">

# Long-Term Architecture

<The one durable design idea that survives individual tasks: the seam you refuse to
blur. Example: "a generic engine plus swappable configuration profiles.">

# Repository Layout

```
<ProjectName>/
|-- START_HERE.md          # entry funnel
|-- CHARTER.md             # this file
|-- .ai/                   # agent handoff state (see .ai/ templates)
|-- docs/                  # roadmap, decisions, rfcs, build/test guides
|-- sources/               # IMMUTABLE inputs - never edited, only read
`-- work/                  # all development happens here
```

Everything under `sources/` is immutable. Development occurs only inside `work/`.

# Git Policy

Git is the only version history. Never create `*_new`, `*_old`, `*_backup`, `*_fixed`, or duplicate edited files. Overwrite files normally. Commit frequently. Each commit should represent one logical engineering change. Documentation is committed alongside implementation.

# Documentation Authority Rule

The agent shall never work from memory when project documentation exists. Before every engineering session, the agent shall reread the charter, roadmap, current task, and session log.

If project documentation conflicts with remembered context, prior chat context, historical notes, or assumptions, the project documentation wins. If the documentation is incomplete, update it rather than relying on memory. This rule exists to prevent context drift across long-running autonomous sessions.

# Development Workflow

Every task follows this loop:

1. Investigate.
2. Read existing documentation.
3. Read historical notes.
4. Document findings.
5. Produce a short implementation plan.
6. Implement the smallest useful change.
7. Automatically build.
8. Automatically test.
9. Automatically collect logs.
10. Update documentation.
11. Commit a single logical change.

# Autonomous Operation Rules

- Verify state before asserting it. Do not claim an artifact is missing or present without checking the current repository/runtime state first. Treat prior logs and memory as hints only; repository state and fresh command output are authoritative.
- Long-running builds and CI wrappers must be polled sparingly. Prefer 60-120 second polling intervals unless a command is near its timeout or the user explicitly asks for a status update.
- When a session window, context limit, quota limit, or time limit is approaching, stop new work and prepare a clean handoff before failure.
- Whenever a bug is fixed, create a regression test that would have detected it.

# Testing Charter

Testing infrastructure is part of the project; the project should become increasingly self-verifying. Every milestone should leave behind an automated check that the next contributor can run. If a manual observation is unavoidable, document the exact command, input, expected output, and the reason automation is not yet practical.

# Project Milestones

<!-- Milestone 0 is always initialization: scaffolding, docs, and inventory only.
     No feature work. This gate is what makes everything else recoverable. -->

## Milestone 0: Project Initialization

Objectives:
- Create the repository scaffolding, documentation set, and input inventory.
- Establish the build and test baseline. No feature work.

Deliverable: a repository in which every later milestone can be executed by a fresh agent using only these documents.

Success Criteria: a new agent reading only this repository can state the mission, the current task, and the next safe action.

**Stop after Milestone 0 is complete. Do not begin Milestone 1 until explicitly directed.**

## Milestone 1: <Name>

Objectives:
- <objective>

Deliverable: <deliverable>

Success Criteria: <observable criteria>

<!-- ...repeat per milestone... -->

# Decision Logging

Every architectural decision should be recorded in `docs/DECISION_LOG.md`. Include: decision, rationale, alternatives considered, long-term implications. Future contributors should understand why the project evolved as it did.

# Guiding Principle

Every completed task should improve at least one of: correctness, reproducibility, documentation, test coverage, logging, observability, maintainability, or autonomous verification. The repository should become easier for the next contributor than it was for the current contributor.
