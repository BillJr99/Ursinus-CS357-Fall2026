#!/usr/bin/env python3
"""Point every hardcoded course link at a different repository, in one command.

Most links in this repo can be Liquid variables, but two kinds cannot:

  * links inside `_pages/Activities/liascript-*.md`, because those files have no
    front matter and LiaScript fetches them straight from GitHub raw rather than
    from the built site, so Jekyll never touches them; and
  * links inside any page's YAML front matter, because Jekyll does not evaluate
    Liquid there and the layouts emit `{{ reading.rlink }}` verbatim.

Those stay hardcoded. This script retargets them.

    python3 retarget-links.py BillJr99/Ursinus-CS357          # render from the parent
    python3 retarget-links.py BillJr99/Ursinus-CS357-Spring2027
    python3 retarget-links.py --check                          # report, change nothing

Page *bodies* use {{ site.activity_url }} and {{ site.baseurl }}; edit
`_config.yml` for those, not this script.
"""
import argparse, glob, io, os, re, sys

RAW  = "https://raw.githubusercontent.com/{repo}/gh-pages/"
BLOB = "https://github.com/{repo}/blob/gh-pages/"
PAT  = re.compile(r"(https://(?:raw\.githubusercontent\.com|github\.com)/)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(/(?:blob/)?gh-pages/)")
# Hardcoded course-site URLs, e.g. https://www.billmongan.com/Ursinus-CS357/Assignments/...
# Deliberately does not match https://www.billmongan.com/LiaScript/?...
SITE = re.compile(r"(https://www\.billmongan\.com/)(Ursinus-[A-Za-z0-9-]+)(/)")

def targets():
    out = []
    for pat in ("_pages/**/*.md", "_pages/**/*.html", "files/**/*.md",
                "files/**/*.ipynb", "README.md"):
        out += glob.glob(pat, recursive=True)
    return sorted(set(p for p in out if os.path.isfile(p)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?", help="owner/repo to point at")
    ap.add_argument("--check", action="store_true", help="report current targets only")
    a = ap.parse_args()
    if not a.repo and not a.check:
        ap.error("give a repo, or --check")

    seen, files, hits = {}, 0, 0
    for f in targets():
        s = io.open(f, encoding="utf-8").read()
        found = PAT.findall(s) 
        sfound = SITE.findall(s)
        if not found and not sfound:
            continue
        for _, repo, _ in found:
            seen[repo] = seen.get(repo, 0) + 1
        for _, site, _ in sfound:
            seen["site: " + site] = seen.get("site: " + site, 0) + 1
        if a.check:
            continue
        site_path = a.repo.split("/")[-1]
        new = PAT.sub(lambda m: m.group(1) + a.repo + m.group(3), s)
        new = SITE.sub(lambda m: m.group(1) + site_path + m.group(3), new)
        if new != s:
            io.open(f, "w", encoding="utf-8").write(new)
            files += 1
            hits += len(found) + len(sfound)

    if a.check:
        for repo, n in sorted(seen.items(), key=lambda kv: -kv[1]):
            print(f"  {n:>4}  {repo}")
        print(f"  {sum(seen.values()):>4}  total hardcoded links")
    else:
        print(f"retargeted {hits} links across {files} files -> {a.repo}")
        print("note: _config.yml activity_url is separate; update it too if the "
              "render host changed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
