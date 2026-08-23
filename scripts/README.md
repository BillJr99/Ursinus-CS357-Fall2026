# scripts/

Course-maintenance scripts that are specific to this repository. The general-purpose
course tooling lives in the `code/` submodule ([Ursinus-Boilerplate-Code](https://github.com/BillJr99/Ursinus-Boilerplate-Code));
anything here is either a narrower variant of one of those tools or something not yet
worth promoting into the boilerplate.

## `canvas_sync_rubrics.py`

Replaces Canvas rubrics for a **named subset** of assignments, so a rubric edit can reach
the live shell without re-running the full course deploy and without rewriting every
rubric in the course.

`code/course/ursinus_canvas_update_rubrics.py` already does rubric-only replacement, but
it does it for *every* deliverable with a `rubricpath`. Replacing a rubric deletes it, and
deleting a rubric discards the rubric assessments recorded against it, so an unscoped run
on a live mid-term shell can destroy per-criterion scores on assignments you never touched.
This script narrows the blast radius and refuses, by default, to replace a rubric that has
already been used for grading.

It builds the same payload as the boilerplate script, including the 25/50/85/100 percent
rating scale, so the two cannot produce different rubrics from the same markdown.

```bash
pip install canvasapi python-frontmatter

# what would change, locally, with no credentials and no network
python scripts/canvas_sync_rubrics.py -m _pages/syllabus.md --changed --list

# dry run against the shell: current vs. new rubric, submission and grading exposure
python scripts/canvas_sync_rubrics.py -m _pages/syllabus.md -c <course_id> \
    --only Assignments/AgentSystemDesign

# commit it
python scripts/canvas_sync_rubrics.py -m _pages/syllabus.md -c <course_id> \
    --only Assignments/AgentSystemDesign --apply
```

Selection is by `--only` (repeatable; matches a `dlink`, a `rubricpath`, or the Canvas
assignment name) or `--changed [REF]` (defaults to uncommitted working-tree edits, and
skips files whose rubric block is unchanged even though the file itself was edited).
One of the two is required; there is deliberately no "every rubric" mode.

The API key comes from `--apikey`, `$CANVAS_API_KEY`, or an interactive prompt. Writing to
a live shell is a credentialed LMS write; dry runs are read-only.
