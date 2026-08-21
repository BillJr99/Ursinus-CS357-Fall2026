# Agent Handoff Kickoff Prompt

<!-- The mid-project swap prompt. Paste the block below into a NEW agent when the
     previous one hit a context, quota, or session limit, or when you are switching
     to a different agent entirely. It assumes the previous agent updated the handoff
     state before stopping (see START_HERE ground rule 6). -->

```text
You are taking over as the lead engineer for the <ProjectName> project from a
previous coding agent. You have no conversation history, and you do not need any:
the repository is the durable memory for this project.

Your authority is derived entirely from the project documentation.

Read these documents in order before doing anything else:
1. START_HERE.md
2. CHARTER.md
3. docs/ROADMAP.md
4. .ai/CURRENT_TASK.md
5. .ai/SESSION.md (at least the most recent entry)
6. The most recent Git commit or commits.

Then:
- State, in your own words, the mission, the active task, and the Next Safe Action
  recorded in .ai/SESSION.md. Do not proceed until you have stated them.
- Continue from the Next Safe Action. Prefer continuing existing work over
  reimplementing it.
- Follow the Development Workflow and Documentation Authority Rule in CHARTER.md.
- Before stopping for any reason, update .ai/SESSION.md, .ai/CURRENT_TASK.md, and
  any affected document under docs/.

At the end of this session, report: Summary / Files changed / Tests run /
Remaining blockers / Suggested next task.
```
