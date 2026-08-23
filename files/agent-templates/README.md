# Agent Operating System Templates

Copy-paste skeletons for governing AI agents in real, long-running work.  These templates come from a production system, anonymized and made application-agnostic.  They implement one idea:

> **The repository is the durable memory for the project.  Conversation history is not durable project state.**

Every file here exists so that an agent can be reset, swapped for a different agent, or interrupted mid-task, and the *next* agent (or the next you) can continue safely by reading documents instead of remembering conversations.

## Two layers

**Layer 1: Project governance** (for coding agents working on a repository):

| Template | Deploy as | Role |
|---|---|---|
| `START_HERE.md` | `/START_HERE.md` | Entry funnel: the fixed read order for any new agent |
| `CHARTER.md` | `/CHARTER.md` | The constitution: mission, philosophy, rules, milestones, guardrails |
| `ai/CONTEXT.md` | `/.ai/CONTEXT.md` | One-line orientation pointer |
| `ai/CURRENT_TASK.md` | `/.ai/CURRENT_TASK.md` | The active-work pointer, with a Reality Check |
| `ai/SESSION.md` | `/.ai/SESSION.md` | Append-only engineering journal; every entry ends with a Next Safe Action |
| `ai/KNOWN_ISSUES.md` | `/.ai/KNOWN_ISSUES.md` | Verified defects and constraints |
| `ai/FUTURE_WORK.md` | `/.ai/FUTURE_WORK.md` | Deferred-enhancements parking lot |
| `ai/AGENT_HANDOFF_KICKOFF.md` | `/.ai/AGENT_HANDOFF_KICKOFF.md` | Ready-to-paste prompt for a mid-project agent swap |
| `KICKOFF_PROMPT.txt` | (paste into a fresh agent) | Cold-start prompt: role, authority, read order, scope, prohibitions |
| `RFC-template.md` | `/docs/rfcs/0000-template.md` | Proposal / design record |
| `DECISION_LOG.md` | `/docs/DECISION_LOG.md` | Running record of decisions, rationale, and alternatives |

**Layer 2: Personal assistant governance** (for a standing agent with tool access to your life/work systems):

| Template | Deploy as | Role |
|---|---|---|
| `AGENTS-vault.md` | `/AGENTS.md` (vault root) | The vault-as-agent-memory contract: zones, write scope, protocols |
| `SYSTEMPROMPT.md` | `/SYSTEMPROMPT.md` | The standing prompt: habits, style, confirmation gates, escalation |
| `LLMMEMORIES.md` | `/LLMMEMORIES.md` | Self-updating durable memory about you and how to work with you |
| `RUNBOOK.md` | `/wiki/Technical/agent-setup.md` | Living runbook: the agent's memory of its own infrastructure |

The `ai/` folder here is deployed as `.ai/` in your repository (it is unhidden in this template set only so the files are easy to browse and download).

## How to adopt

1.  Copy the layer you need into your repository or vault.
2.  Replace every `<angle-bracket placeholder>` with your project's reality.  Delete sections that do not apply; a rule nobody enforces is worse than no rule.
3.  Point your agent at `START_HERE.md` (projects) or `AGENTS.md` (vaults) as its first read, every session.
4.  Keep the documents current: **updating these files is part of every task, not an afterthought.**

These templates accompany the course activities *Governing Coding Agents: Charters, Handoffs, and Durable Memory* and *From Second Brain to Chief of Staff: A Personal Agent in Production*.
