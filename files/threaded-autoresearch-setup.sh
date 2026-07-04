#!/usr/bin/env bash
#
# threaded-autoresearch-setup.sh
# ------------------------------
# Sets up and runs a threaded auto-research pipeline against a local
# Ollama server.  Each research topic in topics.txt is handed to its own
# worker process; each worker (optionally) queries a local SearXNG
# metasearch endpoint for grounding snippets, then asks the model for a
# focused per-topic summary.  A final merge step asks the model to
# synthesize all of the per-topic summaries into a single digest with
# one section per topic.
#
# Usage:
#   bash threaded-autoresearch-setup.sh
#
# Configuration (override any of these from the environment):
#   MODEL=llama3.2 TEMPERATURE=0.2 PARALLELISM=4 bash threaded-autoresearch-setup.sh
#
set -euo pipefail

# ----------------------------------------------------------------------
# 1. Configuration.  Exported so the Python worker/merge steps inherit it.
# ----------------------------------------------------------------------
export MODEL="${MODEL:-llama3.2}"           # any model pulled with `ollama pull`
export TEMPERATURE="${TEMPERATURE:-0.3}"    # low = focused; raise it to brainstorm
export OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
export SEARXNG_URL="${SEARXNG_URL:-http://localhost:8888}"  # optional local search
PARALLELISM="${PARALLELISM:-3}"             # how many workers run at once
WORKDIR="${WORKDIR:-$PWD/autoresearch}"     # everything happens inside here

# ----------------------------------------------------------------------
# 2. Preflight checks -- fail early with a clear message, not mid-run.
# ----------------------------------------------------------------------
if ! command -v ollama >/dev/null 2>&1; then
  echo "ERROR: 'ollama' was not found on your PATH." >&2
  echo "Install it from https://ollama.com and pull a model, for example:" >&2
  echo "    curl -fsSL https://ollama.com/install.sh | sh" >&2
  echo "    ollama pull ${MODEL}" >&2
  exit 1
fi

if ! curl -fsS --max-time 5 "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
  echo "ERROR: no Ollama server answered at ${OLLAMA_URL}." >&2
  echo "Start it with 'ollama serve' (or launch the desktop app) and retry." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required for the worker and merge steps." >&2
  exit 1
fi

if ! python3 -c "import requests" >/dev/null 2>&1; then
  echo "ERROR: the Python 'requests' package is required by the worker and merge scripts." >&2
  echo "Install it with:  python3 -m pip install requests" >&2
  exit 1
fi

# SearXNG is optional: if a local instance answers, workers search first;
# otherwise they degrade gracefully to the model's parametric knowledge.
if curl -fsS --max-time 3 "${SEARXNG_URL}/search?q=test&format=json" >/dev/null 2>&1; then
  echo "[setup] SearXNG detected at ${SEARXNG_URL} -- workers will search first."
else
  echo "[setup] No SearXNG at ${SEARXNG_URL} -- workers use model knowledge only."
  export SEARXNG_URL=""   # empty string tells the worker to skip searching
fi

# ----------------------------------------------------------------------
# 3. Working directory and a starter topics.txt (one topic per line).
# ----------------------------------------------------------------------
mkdir -p "${WORKDIR}/summaries" "${WORKDIR}/logs"
cd "${WORKDIR}"

if [ ! -f topics.txt ]; then
  cat > topics.txt <<'EOF'
retrieval-augmented generation for small local models
prompt injection attacks against tool-using agents
quantization tradeoffs when serving LLMs on laptops
EOF
  echo "[setup] Wrote a starter topics.txt -- edit it to research your own topics."
fi

# ----------------------------------------------------------------------
# 4. The worker: one OS process per topic, each with its own SMALL
#    context (the small-context-window principle -- no topic's prompt
#    ever bleeds into another topic's prompt).
# ----------------------------------------------------------------------
cat > worker.py <<'PYEOF'
"""Research one topic; write a short summary to summaries/<slug>.md."""
import os, re, sys
import hashlib
import requests

MODEL = os.environ.get("MODEL", "llama3.2")
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.3"))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
SEARXNG_URL = os.environ.get("SEARXNG_URL", "")  # empty = skip search

def slugify(text):
    # short stable hash suffix keeps truncated names unique per topic
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    stem = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]
    return f"{stem}-{digest}"

def search(topic):
    """Optionally pull a few result snippets from a local SearXNG instance."""
    if not SEARXNG_URL:
        return ""
    try:
        r = requests.get(f"{SEARXNG_URL}/search",
                         params={"q": topic, "format": "json"}, timeout=10)
        r.raise_for_status()
        hits = r.json().get("results", [])[:5]
        return "\n".join(f"- {h.get('title','')}: {h.get('content','')}" for h in hits)
    except Exception as e:
        print(f"[worker] search failed ({e}); continuing without it", file=sys.stderr)
        return ""

def generate(prompt):
    r = requests.post(f"{OLLAMA_URL}/api/generate",
                      json={"model": MODEL, "prompt": prompt, "stream": False,
                            "options": {"temperature": TEMPERATURE}},
                      timeout=300)
    r.raise_for_status()
    return r.json()["response"]

def main():
    topic = sys.argv[1].strip()
    snippets = search(topic)
    context = f"Search snippets:\n{snippets}\n\n" if snippets else ""
    prompt = (f"You are a careful research assistant. {context}"
              "Write a concise, factual summary (150-250 words) of what a "
              "student should know about the topic below. Use short "
              "paragraphs and note any points you are uncertain about.\n\n"
              f"Topic: {topic}\n")
    summary = generate(prompt)
    path = os.path.join("summaries", slugify(topic) + ".md")
    with open(path, "w") as f:
        f.write(f"# {topic}\n\n{summary.strip()}\n")
    print(f"[worker] {topic!r} -> {path}")

if __name__ == "__main__":
    main()
PYEOF

# ----------------------------------------------------------------------
# 5. The merge step: reads every per-topic summary and asks the model to
#    synthesize a single digest with one section per topic.
# ----------------------------------------------------------------------
cat > merge.py <<'PYEOF'
"""Synthesize per-topic summaries into one digest with per-topic sections."""
import os, sys
import requests

MODEL = os.environ.get("MODEL", "llama3.2")
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.3"))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

def main():
    parts = [open(p).read().strip() for p in sys.argv[1:]]
    corpus = "\n\n---\n\n".join(parts)
    prompt = ("You are an editor assembling a research digest. Below are "
              "independent single-topic summaries separated by '---'. "
              "Produce a Markdown digest that:\n"
              "1. opens with a 3-4 sentence overview connecting the topics,\n"
              "2. contains one '## <topic>' section per summary, lightly edited,\n"
              "3. ends with a '## Open Questions' section.\n"
              "Do not invent topics that are not present.\n\n" + corpus)
    r = requests.post(f"{OLLAMA_URL}/api/generate",
                      json={"model": MODEL, "prompt": prompt, "stream": False,
                            "options": {"temperature": TEMPERATURE}},
                      timeout=600)
    r.raise_for_status()
    print(r.json()["response"].strip())

if __name__ == "__main__":
    main()
PYEOF

# ----------------------------------------------------------------------
# 6. Fan out: run one worker per topic, up to PARALLELISM at a time.
#    tr+xargs -0 is portable (GNU and BSD); -n 1 gives each worker one
#    topic; -P runs them concurrently as separate processes.
# ----------------------------------------------------------------------
echo "[run] Researching topics with up to ${PARALLELISM} parallel workers..."
grep -v '^[[:space:]]*$' topics.txt | grep -v '^#' \
  | tr '\n' '\0' \
  | xargs -0 -n 1 -P "${PARALLELISM}" python3 worker.py

# ----------------------------------------------------------------------
# 7. Fan in: merge every summary into digest.md.
# ----------------------------------------------------------------------
if ! ls summaries/*.md >/dev/null 2>&1; then
  echo "ERROR: no summaries were produced; check logs above." >&2
  exit 1
fi
echo "[run] Merging per-topic summaries into digest.md ..."
python3 merge.py summaries/*.md > digest.md
echo "[done] Digest written to ${WORKDIR}/digest.md"
