# Session Log

## 2026-09-03, afternoon

Resequenced the AI assignment track so that students write a system prompt and an agent skill and drive them with `opencode` before standing up the local agent stack, and pushed the Team Charter back one class meeting at each end.  The work spanned the course repository, the Canvas shell (change document prepared, not yet applied), and the CS357 Fall 2026 OneNote Class Notebook (applied).  The central finding was that the OpenCode lab did not need to be written from scratch: `lab-critiquerefine.md` was carrying an ~835-line "Coding Agents in Practice" direction inside a page that is only a spec appendix for the Week 10 multi-agent lab, so that material was harvested into the new lab rather than duplicated, and two other pages shrank as a result.

### Files created or modified

- `_pages/syllabus.md`: deliverable blocks moved between schedule entries (no dates edited, since dates derive from week/date keys); two prose counts changed from six labs to seven.
- `_pages/Assignments/lab-opencodestudio.md`: **new**, 917 lines, 100 points, permalink `/Assignments/OpenCodeStudio`.
- `_pages/Assignments/lab-critiquerefine.md`: coding-agent direction removed (1648 lines to 813), four goals and one reading retargeted, pointer added.
- `_pages/Assignments/lab-localagent.md`: Part 4 rewritten as the generated-skill experiment, rubric row and goals narrowed, prerequisite note, time budget, directions table, readings.
- `_pages/Assignments/lab-localagent-d5-agentskills.md`: prerequisite and continuation notes.
- `_pages/Assignments/asmt-overview.md`: fifth setup step (`opencode --version` plus one prompt), checklist, rubric, troubleshooting rows, added-after-handout note.
- `_pages/Activities/liascript-devenvironment.md`: Step 8.1 and 8.2, Step 5 check 5.4, Step 11, quick reference, key concepts.
- `_pages/Tutorials/tut-docker.md`: `opencode-ai` as the sample agent image's default.
- `files/devcontainer/Dockerfile`: `npm install -g opencode-ai`.
- `files/devcontainer/README.md`: opencode documented; two stale links to the parent repo and to a nonexistent `liascript-docker.md` corrected.
- `.gitignore`: `outputs/` added.
- `outputs/canvas-cs357-f2026-resequence.json` and `outputs/canvas-runbook.md`: Canvas change document and runbook (gitignored).

### External actions

- **Pushed** commit `a4044e8` to `claude/ai-assignment-opencode-sequence-fxhaxc` on `BillJr99/Ursinus-CS357-Fall2026`.  Authorized: the session's designated development branch.  No pull request was opened.
- **OneNote**: 20 targeted PATCH edits across 11 teacher-only pages (5 Class Notes, 6 Class Agendas) in the CS357 Fall 2026 Class Notebook.  Explicitly authorized in session after a full dry-run preview; all returned 204 and all 11 verified by reading back.
- **Canvas**: nothing written.  The change document was validated locally with `--check` only.

### Open items

- Apply the Canvas changes: `outputs/canvas-runbook.md` has the four-step order.  The Canvas course id is still needed.
- Canvas module items (the "Handed Out" links) are not covered by the change document; move three by hand or rebuild modules with `--existing-modules leave`.
- The Dockerfile change was not build-tested; no Docker daemon in the session container.  `opencode-ai` 1.18.27 exists on npm and provides the `opencode` command.
- Pre-existing, untouched: `_pages/syllabus.md` links `TokenPredictor`, which is not a permalink, and `bin/check-site.py` reports it.

## 2026-09-03, evening

Gave the course an instrument for measuring what an AI request actually costs, rather than looking the figure up in a table, and removed the Golden-Set Benchmark Checkpoint lab by rehoming its pedagogy into the RAG Quality Checkup rather than discarding it.  The measurement work needed no new page: the Local Agent Lab's Direction 5, Pathway 2 already listed "generated tokens" among the measures for its evaluation experiment without supplying anything that produces the number, and the deliberation-harness starter already had a `Budget` class that counted model calls and refused to proceed past a limit, so token accounting slotted into an existing mechanism.  Two findings shaped the work.  First, the `caveman` compression skill was in this repository and was deleted in `bf9e4a5` when `liascript-agentskills.md` folded into Direction 5; it is restored as the compression condition of the new three-condition experiment, where its own claim of 65 to 75 percent output compression is now something students measure rather than repeat.  Second, Written Assignment 3's rubric never reaches Canvas, because `asmt-responsibleaipractice.md` is Component 2 of the Responsible AI Capstone and the only `rubricpath` Canvas sees for that assignment is `lab-responsibleai.md`; the rubric change made here therefore alters the website and the graded expectation and changes nothing in the shell.

### Files created or modified

- `files/agent-templates/deliberation-harness/tools/token_meter.py`: **new**, 282 lines.  Reads `prompt_eval_count` and `eval_count` off an Ollama response, converts measured tokens to grams CO2eq as an operational term plus an additive amortized training term, and expresses the result in operational anchors.  Every estimate is labelled with the method that produced it, and a failed conversion refuses to print a zero.
- `files/agent-templates/deliberation-harness/config/energy-profiles.json`: **new**.  Two model classes.  Commercial is anchored on the ~500 tonne GPT-3 training figure the course already cites to Patterson et al. 2021; offline is anchored on the 390 tCO2eq Llama 3 8B figure read from Meta's published model card and cited by URL in the file.  The lifetime-request denominators are labelled as assumptions in the file itself.
- `files/agent-templates/deliberation-harness/tools/deliberate_loop.py`: `Budget` gains token fields and `spend_tokens`; `exhausted()` gains a `max_total_tokens` arm that is a real gate; `call_model` keeps the whole response so usage survives; the repair log, evidence report, and `summary.json` carry the totals and the carbon breakdown.
- `files/agent-templates/deliberation-harness/config/loop-config.json`: `max_total_tokens` budget added.
- `files/agent-templates/deliberation-harness/README.md`: file tree, the "what to change, and where" table, and a new section on measuring what a run cost.
- `_pages/Assignments/lab-localagent-d5-agentskills.md`: E7's measure list splits the two token terms and explains why they grow differently; new **E7b**, a three-condition experiment (verbose one-shot, compressed, agentic loop); the `caveman` catalog entry restored; Key Concepts gains token-meter and amortized-training-cost rows.
- `_pages/Assignments/asmt-responsibleaipractice.md`: Direction E's reference table gains the additive training term for both model classes with denominators stated; the Part 1 log records measured tokens with an estimated-versus-measured column; Part 2 gains the three-condition comparison; rubric rows 2 and 4 extended.  No weight changes.
- `_pages/Assignments/lab-ragcheckup.md`: restructured to Part 1 Design (25), Part 2 Worksheet (45), Part 3 Harness (30).  Absorbs the deleted lab's worked items, design sequence, miss classification, and troubleshooting rows, and adds a RAG-specific third failure category.
- `_pages/Assignments/lab-goldenset.md`: **deleted**.
- `_pages/Activities/liascript-evaluatingoutputs.md`: minute-budget rows and Part IIb reframed around the activity's own Exercise 1 as the same-day output, with RAG Checkup named as the eventual consumer.
- `_pages/syllabus.md`: both Golden-Set deliverable blocks removed; RAG Quality Checkup added to the no-code enumeration.  The "7 labs" prose deliberately unchanged.

### External actions

- **Pushed** to `claude/token-usage-estimation-8vktzt`, then opened and **merged** [PR #48](https://github.com/BillJr99/Ursinus-CS357-Fall2026/pull/48) into `gh-pages`.  Authorized: Bill asked for the PR and the merge in session.  The `Update ical` and `Reset and Sync Submodules` workflows both succeeded and the two Golden-Set VEVENTs left `files/CS357.ics` without a hand edit.
- **Canvas**: nothing written.  A change document was produced **in chat only**, per Bill's instruction that it not enter the repository.  Two operations against the updated `ursinus_canvas_inline_changes.py`: `assignment.delete` on `Lab: Golden-Set Benchmark Checkpoint`, which now sweeps both the handed-out and the due module items itself, and `rubric.replace` on `Lab: RAG Quality Checkup Checkpoint` from `_pages/Assignments/lab-ragcheckup.md`.  Validated with `--check` twice, against two successive versions of the script; Canvas was never contacted.
- **OneNote**: **8 pages patched** in the CS357 Fall 2026 Class Notebook's `_Teacher Only` section group, 4 Class Agendas and 2 Class Notes carrying corrections plus 2 more carrying enrichments.  Explicitly authorized in session after a full preview of all 14 edits.  All returned 204 and all 8 were read back and verified at the normalized-text level.
- Cloned `BillJr99/Ursinus-Boilerplate-Code` read-only, with permission, to read the Canvas script schemas, and re-pulled it twice as Bill extended the inline-changes script.

### Open items

- **The Canvas change document has not been applied.**  It is written and validated but needs the course id, which is still unknown, carried over from the previous session.  The dry run must show **0 submissions** on the Golden-Set assignment and **0 rubric assessments** on the RAG Checkup before `--apply`; if either is non-zero, stop rather than reaching for `--allow-delete-with-submissions` or `--force-graded`.
- **Open question for Bill:** whether the script's new submission-file-types and available-until-last-day behaviors should be backfilled across the assignments already in the shell.  Nothing this session created an assignment, so neither binds on these edits.
- **Written Assignment 3 still has no Canvas assignment.**  Its rubric change reached the website and not the shell.  `assignment.create` could now give it one with `rubricpath`, `submission_types: written`, and `handout`, but that restructures how the capstone's 200 points appear in Canvas, so it was not assumed.
- **`bin/check-site.py` reports a false positive, not a broken link.**  The previous session's log lists the syllabus's `TokenPredictor` link as a real problem.  It is not: `_pages/token-predictor.html` carries `permalink: /TokenPredictor`, but `pages()` globs only `*.md`, so the checker cannot see it.  A one-line glob fix would clear it; left alone as out of scope.
- **A pre-existing scheduling bug, flagged and not fixed.**  The RAG Quality Checkup calls itself a mid-flight diagnostic of the RAG Knowledge Base pipeline, but it is handed out Week 9 Day 0, one session before that pipeline is due, and is itself due Week 11 Day 0, two weeks after.  Moving its handout to Week 7 Day 1, the open-studio session, would fix it and would also shorten the gap from the Week 4 benchmark-design work.
