# AGENT INSTRUCTIONS (MANDATORY)

<!-- The vault-as-agent-memory contract. Lives at the ROOT of your knowledge vault
     repository. Its authority claim is absolute and stated first — an agent that has
     not read it may not act. This template hardens the basic three-zone contract from
     the Second Brain activity into a production version. -->

You must read and follow all instructions in this file before performing any actions in this repository. If you have not read this file, stop and read it before continuing.

## Repository Role

This repository is a personal knowledge vault ("second brain"). It is the durable, authoritative memory shared by the owner and every agent the owner runs. It is edited by the owner in a note-taking app and by agents over Git/API.

## Zones and Write Scope (Do Not Pollute the Root)

- `/raw/` is strictly **READ-ONLY**. It is the unprocessed source inbox.
- All authored content must live inside `/wiki/`. Treat `/wiki/` as a curated layer, not a verbatim mirror of `/raw/`: synthesize, summarize, normalize, deduplicate, and organize the source material.
- The repository root is reserved for a small set of canonical meta-files (this file, `SYSTEMPROMPT.md`, `LLMMEMORIES.md`) and tool configuration. You must **not**: create new notes at the root, create new top-level directories for authored content, or scatter scratch/draft files outside `/wiki/`.
- Tool-managed directories (the note app's config directory, trash) are off-limits, except the sync-metadata file described below.

## Sync Metadata Protocol (CRITICAL)

Any time you create, modify, rename, or delete a file **outside of the note-taking app** — via Git, GitHub, or API calls — you must also update the sync tool's metadata file in the **same commit**, computing file hashes exactly the way the sync tool computes them. Commit the file change and the metadata update together, atomically. (See the Second Brain / vault-sync activity for the mechanics.)

## Organization Requirements

Organize `/wiki/` into clear, intuitive, scalable topical categories, expressed as high-level directories with meaningful subdirectories. Do not leave `/wiki/` as a flat dump of loose notes. Prefer linking over copying; keep one canonical page per topic.

## Question-Answering Mode

When the owner asks a question and tells you to use the vault, you must:

1. Open the repository.
2. Read `/wiki/` first as the primary and authoritative curated knowledge source.
3. Use `/raw/` only to fill gaps, verify details, or incorporate newly added material not yet reflected in `/wiki/`.
4. If `/wiki/` is incomplete or outdated relative to `/raw/`, update `/wiki/` first when appropriate.
5. Answer the question grounded in the curated contents of `/wiki/`.

## Memory and System Prompt

`LLMMEMORIES.md` and `SYSTEMPROMPT.md` at the root are the canonical copies of the owner's durable memory and standing instructions. Keep them **bidirectionally synchronized** with the live assistant whenever possible: memory acquired in sessions flows back into these files, and edits to these files update the live session.

## Maintenance Behavior (the Vault Linter)

Periodically, or when asked, audit the vault:

1. Discover the sync metadata file.
2. Enumerate all files.
3. Repair broken internal links (classify each as valid / file-not-found / ambiguous / heading-not-found; auto-correct only near-certain matches and mark corrections inline).
4. Audit metadata completeness.
5. Validate metadata JSON well-formedness.
6. Update timestamps.
7. Emit a dated lint report into `/wiki/`.

Before writing any file back to disk, diff the proposed content against the current content. Do not write if the diff is empty. Prefer surgical edits (targeted string replacement) over full file rewrites wherever possible.

## When in Doubt

Prefer clean structure over clutter; prefer canonical pages over duplicates; prefer linking over copying; prefer thoughtful synthesis over raw aggregation; prefer preserving useful detail over vague summarization.

## Precedence

Where this file and `SYSTEMPROMPT.md` overlap, the stricter requirement applies; where requirements are equally strict, `SYSTEMPROMPT.md` governs.
