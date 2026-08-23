# START HERE

<!-- Entry funnel.  Every agent (and every human contributor) reads this file first.
     Its only job is to establish the read order and the ground rules that prevent
     an agent from acting on stale memory. Keep it under one page. -->

Welcome.  You are working on **<ProjectName>**.  Before doing anything else, read these documents **in this order**:

1. `START_HERE.md` (this file)
2. `CHARTER.md`: the project constitution.  All authority derives from it.
3. `docs/ROADMAP.md`: milestone status board: what is done, what is next.
4. `.ai/CURRENT_TASK.md`: the active milestone, active subtask, and next immediate action.
5. `.ai/SESSION.md`: the running engineering log.  Read at least the most recent entry.
6.  Review the most recent Git commit or commits.

## Ground rules

1.  The repository is the durable memory for the project.  Conversation history is not durable project state.
2.  If project documentation conflicts with remembered context, prior chat context, or assumptions, **the project documentation wins**.  If the documentation is incomplete, update it rather than relying on memory.
3.  Before beginning any nontrivial task, read `.ai/SESSION.md`, `.ai/CURRENT_TASK.md`, and the most recent Git commit.  Prefer continuing existing work over reimplementing it.
4.  Do not claim that a file, artifact, log, or build output is missing or present without checking current repository/runtime state first.  Treat prior logs and memory as hints only; repository state and fresh command output are authoritative.
5.  Do not create backup file variants such as `_old`, `_new`, `_fixed`, or `_backup`.  Git history is the only version history.
6.  Before stopping for any reason (user interruption, session exhaustion, context exhaustion, quota exhaustion, or task completion) update the handoff state: `.ai/SESSION.md`, `.ai/CURRENT_TASK.md`, and any affected document under `docs/`.
7.  Stop after Milestone 0 is complete.  Do not begin Milestone 1 until explicitly directed.

## The standard to leave behind

The repository should become easier for the next contributor than it was for the current contributor.
