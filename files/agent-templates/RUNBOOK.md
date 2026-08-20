# Agent Setup Runbook

<!-- The living runbook: the agent's durable memory of its OWN infrastructure,
     versioned inside the vault alongside everything else. This file is the INDEX;
     detailed content lives in one topic page per subject. The agent maintains this
     document itself: every setup change (new skill, plugin, connector, credential
     variable, provider, fix) is recorded in the topic page that owns the subject. -->

## Environment Topology

<!-- Name your deployments precisely. If the assistant runs in more than one place,
     ambiguity about WHICH instance owns a capability causes real incidents. -->

| Instance | Role | Runtime | Durable config source |
|---|---|---|---|
| <instance A> | <e.g., containerized worker> | <runtime> | <config path> |
| <instance B> | <e.g., always-on control plane> | <runtime> | <config path> |

Avoid using the bare assistant name when the distinction between instances affects paths, credentials, service ownership, or uptime assumptions.

## Topic Pages

| Topic | Page | Read or update when... |
|---|---|---|
| Conventions and policies | `<Assistant>/Conventions-and-Policies.md` | any cross-instance rule changes |
| Environment variables | `<Assistant>/Env-Reference.md` | a credential or setting is added (names and purposes ONLY — never values) |
| Known issues | `<Assistant>/Known-Issues.md` | a defect is verified or a workaround applied (use stable KI-NN ids) |
| Skills inventory | `<Assistant>/Skills-Inventory.md` | a skill is added, renamed, or retired (keep the reconstruction manifest current) |
| Scheduled routines | `<Assistant>/Routines.md` | a cron job is added or its policy changes |
| Local services | `<Assistant>/Local-Services.md` | a sidecar service, port, or health check changes |

## Service Ownership and Cutover

<!-- Prevents two instances from silently duplicating or disabling one another. -->

| Capability | Current owner | Target owner | Verification state | Notes |
|---|---|---|---|---|
| <capability> | <instance> | <instance> | <verified how, when> | |

Cutover gate for any owner change of a user-facing capability — all boxes checked before the old owner is disabled:

- [ ] New owner starts successfully
- [ ] Receives a real input
- [ ] Responds on the correct channel
- [ ] Survives a service restart
- [ ] Survives a host reboot / autostart tested
- [ ] Logs and recovery documented
- [ ] Owner explicitly confirms the old instance may be disabled

## Maintenance Directive

Keep these pages current whenever the setup changes. Make each update in the topic page that owns the subject. Never record secret values — variable names, file paths, ownership, and purpose only. Commit durable changes (with sync metadata) when made.
