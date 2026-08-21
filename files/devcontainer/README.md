# CS357 Course Development Container

One environment that runs every CS357 lab: Python 3.11 with the course
libraries (`requests`, `chromadb`, `sentence-transformers`, `scikit-learn`,
`numpy`, `spacy` with `en_core_web_sm`, `shap`, `lime`, `matplotlib`,
`pandas`, `flask`), plus Node.js with `promptfoo` for the evaluation lab, and
`git` so you commit and push from inside the container.

**Ollama is the one thing that stays on your host.** It runs natively for
model performance; code inside the container reaches it at
`http://host.docker.internal:11434`, the host-bridge pattern from the
[Docker from Zero activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-docker.md).

The full walk-through (Ollama first, then Docker, then GitHub setup,
credential options, practice steps, and troubleshooting) is the
[Development Environment activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-devenvironment.md).
This README is the quickstart version.

## Files

| File | Purpose |
|---|---|
| `Dockerfile` | Recipe for the course image (each package commented with the lab that uses it) |
| `docker-compose.yml` | One-command build/run with the workspace bind mount and the Linux `host.docker.internal` fix |
| `devcontainer.json` | VS Code Dev Containers configuration |

## Setup (common to routes A and B)

1. Install [Ollama](https://ollama.com/download) **on your host** (not in
   Docker) and pull the course model: `ollama pull llama3.2`.
2. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   (macOS/Windows) or Docker Engine (Linux) and confirm `docker run hello-world` works.
3. Create a **private** GitHub repository named `cs357-work` and clone it.
4. Copy the three files above into a `.devcontainer/` folder inside the clone:

   ```
   cs357-work/
     .devcontainer/
       Dockerfile
       docker-compose.yml
       devcontainer.json
     (your lab work lives here, at the repo root)
   ```

The bind mount in `docker-compose.yml` (and the `workspaceMount` in
`devcontainer.json`) exposes **your cloned GitHub repo** (and nothing else on
your machine) at `/workspace` inside the container. You edit, test, commit,
and push there; the files live on your disk and on GitHub, so the container
itself is disposable.

## Route A: VS Code Dev Containers

1. Install VS Code and the **Dev Containers** extension.
2. Open the `cs357-work` folder in VS Code.
3. Run **Dev Containers: Reopen in Container** from the command palette. The
   first build downloads the ML libraries and takes a while; later opens are fast.
4. Open a terminal in VS Code; you are inside the container at `/workspace`.

## Route B: plain Docker Compose

From the `.devcontainer/` folder of your clone:

```bash
docker compose build            # first time, and after any Dockerfile change
docker compose run --rm cs357   # opens bash inside the container
```

Verify the stack from the container prompt (Ollama must be running on the host):

```bash
python3 -c "import requests; print(requests.get('http://host.docker.internal:11434/api/tags').json())"
promptfoo --version
python3 -c "import spacy; spacy.load('en_core_web_sm'); print('spacy OK')"
```

Exit with `exit` or Ctrl-D. `--rm` discards the container; your work is safe
in the mounted repo.

## Route C: native fallback (no Docker)

Every lab's "Before You Start" section already lists its native installs, and
those remain valid. In short: install Ollama on your machine as above, use
[uv](https://docs.astral.sh/uv/) (or `pip`) to add each lab's packages as that
lab documents (`uv add requests`, then `chromadb sentence-transformers` for
the retrieval lab, `scikit-learn numpy` for the ML labs, `spacy`/`shap`/
`lime`/`matplotlib`/`pandas` for the explainability directions, `flask` for
the web-endpoint direction), install Node.js from [nodejs.org](https://nodejs.org/)
and `npm install -g promptfoo` for the evaluation lab, and use
`http://localhost:11434` instead of `host.docker.internal` in every URL.

## Troubleshooting

- `Cannot connect to the Docker daemon`: Docker Desktop is not running; start it.
- Connection refused to `host.docker.internal:11434`: either Ollama is not
  running on the host, or (Linux) the container was started without the
  `extra_hosts`/`--add-host` mapping. The compose file and `devcontainer.json`
  here both include it.
- Slow first build: normal (the ML libraries are large); later builds reuse
  cached layers.
- Push rejected / authentication failures: see the credential section of the
  [Development Environment activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-devenvironment.md).
