#!/usr/bin/env python3
"""Pre-merge checks for the course site.

The Pages workflow only builds on a push to gh-pages, so a mistake in a layout
name or a stray Liquid delimiter is not caught until after the merge. These are
the checks that would have caught the ones we have actually hit.

    python3 bin/check-site.py

Exits non-zero and prints what is wrong. Needs PyYAML and a checked-out
_layouts submodule (git submodule update --init _layouts).
"""
import glob
import os
import posixpath
import re
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

# Liquid expressions the site genuinely uses. Anything else in {{ }} on a
# Jekyll-processed page is literal text that Liquid will silently eat.
REAL_LIQUID = re.compile(
    r"\{\{ *(site\.(baseurl|raw_pages_url|lia_viewer_url)|page\.info\.[a-z_]+) *\}\}"
)
RAW_BLOCK = re.compile(r"\{%-?\s*raw\s*-?%\}.*?\{%-?\s*endraw\s*-?%\}", re.S)

failures = []


def note(check, msg):
    failures.append(f"[{check}] {msg}")


def pages():
    """(path, front matter dict) for every file Jekyll will process."""
    for path in sorted(set(glob.glob("_pages/**/*.md", recursive=True) + glob.glob("*.md"))):
        text = open(path, encoding="utf-8").read()
        if not text.startswith("---"):
            continue
        try:
            fm = yaml.safe_load(text.split("---", 2)[1])
        except Exception as exc:                        # noqa: BLE001
            note("yaml", f"{path}: front matter does not parse: {exc}")
            continue
        if isinstance(fm, dict):
            yield path, fm, text


ALL = list(pages())


# 1. Every layout named in front matter has to exist, or Jekyll warns and drops
#    the page's chrome. This is the failure that bit CS374.
def check_layouts():
    if not os.path.isdir("_layouts") or not os.listdir("_layouts"):
        note("layout", "_layouts is empty; run: git submodule update --init _layouts")
        return
    available = {os.path.splitext(f)[0] for f in os.listdir("_layouts") if f.endswith(".html")}
    for path, fm, _ in ALL:
        layout = fm.get("layout")
        if layout in (None, "null"):
            continue
        if layout not in available:
            note("layout", f"{path}: layout '{layout}' not in _layouts "
                           f"(have: {', '.join(sorted(available))})")


# 2. A deck is a syllabus lecture link and nothing else.
def check_deck_invariant():
    syl = next((fm for p, fm, _ in ALL if p.endswith("syllabus.md")), None)
    if not syl:
        note("decks", "could not read _pages/syllabus.md front matter")
        return
    lecture = {os.path.basename(e["link"]) for e in syl.get("schedule", [])
               if isinstance(e.get("link"), str) and e["link"].startswith("Activities/")}
    have = {os.path.basename(f) for f in glob.glob("_pages/Activities/liascript-*.md")}
    for extra in sorted(have - lecture):
        note("decks", f"{extra} is a deck but not a scheduled lecture; it belongs in _pages/Tutorials/")
    for missing in sorted(lecture - have):
        note("decks", f"syllabus links Activities/{missing}, which does not exist")


# 3. Decks are fetched raw from GitHub, so Liquid never runs in them.
def check_no_liquid_in_decks():
    for path in sorted(glob.glob("_pages/Activities/liascript-*.md")):
        text = open(path, encoding="utf-8").read()
        if "{{ site." in text:
            note("decks", f"{path}: uses {{{{ site.* }}}}, which renders as literal text in a "
                          f"raw-served deck; use the absolute URL instead")


# 4. On a Jekyll page, literal {{ }} in prose or a code fence is eaten by Liquid
#    before Markdown ever sees it. Wrap it in {% raw %}.
def check_literal_braces():
    for path, _, text in ALL:
        if "/Activities/" in path:
            continue
        stripped = RAW_BLOCK.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
        for lineno, line in enumerate(stripped.split("\n"), 1):
            if "{{" in REAL_LIQUID.sub("", line):
                note("liquid", f"{path}:{lineno}: literal {{{{ }}}} outside {{% raw %}}; "
                               f"Liquid will delete it: {line.strip()[:70]}")


# 5. Front matter is not Liquid-evaluated, so rlink/dlink are emitted verbatim
#    and resolve in the browser against the page's own URL (no trailing slash).
def check_front_matter_links():
    perms = {"/" + fm["permalink"].strip("/"): p for p, fm, _ in ALL if fm.get("permalink")}
    # _pages/Exercises is a submodule that may not be checked out
    have_exercises = os.path.isdir("_pages/Exercises") and os.listdir("_pages/Exercises")

    def walk(obj):
        if isinstance(obj, dict):
            for key, val in obj.items():
                if key in ("rlink", "dlink", "link") and isinstance(val, str):
                    yield val
                else:
                    yield from walk(val)
        elif isinstance(obj, list):
            for val in obj:
                yield from walk(val)

    for path, fm, _ in ALL:
        if not fm.get("permalink"):
            continue
        parent = posixpath.dirname("/" + fm["permalink"].strip("/"))
        for link in walk(fm):
            if not link or link.startswith(("http", "mailto", "#")):
                continue
            if re.search(r"\.(md|pdf|ipynb|zip|png|jpg|html)$", link):
                continue
            target = link if link.startswith("/") else posixpath.normpath(posixpath.join(parent, link))
            target = "/" + target.strip("/")
            if target not in perms:
                if not have_exercises:
                    continue          # can't tell a real break from an absent submodule
                note("links", f"{path}: '{link}' resolves to {target}, which is not a permalink")


for check in (check_layouts, check_deck_invariant, check_no_liquid_in_decks,
              check_literal_braces, check_front_matter_links):
    check()

if failures:
    print(f"{len(failures)} problem(s):\n")
    print("\n".join(failures))
    sys.exit(1)
print(f"OK: {len(ALL)} pages, layouts resolve, deck invariant holds, no stray Liquid.")
