# LLMMEMORIES.md: Durable Memory

<!-- The self-updating memory file.  The canonical record of stored memories about the
     owner and the durable backup of the assistant's operational memory. The assistant
     writes acquired memories back here; every change to the live memory store must be
     reflected here BEFORE any deletion or compression happens (the memory-to-vault
     sync rule). Append and annotate; do not silently rewrite history. -->

## Identity and Roles

<durable facts about who the owner is and what they do>

## Preferences

### Meta-Interaction Preferences

<how the owner likes to be questioned, corrected, updated>

### Writing Preferences

<voice, formality, structural habits, style rules>

### Code / Implementation Preferences

<languages, patterns, error-handling and configuration conventions>

### Debugging Preferences

<how the owner wants problems investigated and reported>

## Ongoing Projects and Recurring Threads

<project name -> one-paragraph durable context each>

## Assistant Operational Preferences

<standing choices about tools, formats, and workflows the assistant should default to>

## How Future Agents Should Use This File

- Adapt writing style to the preferences above.
- Recognize recurring themes and connect new work to the ongoing threads.
- Preserve continuity: this file is a living summary of durable user-context, not a substitute for reading the vault itself.
- When a session produces a durable fact or preference, propose adding it here (see SYSTEMPROMPT.md §7), and record it as an addition (with a date) rather than an edit that erases the past.
