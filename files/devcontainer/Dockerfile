# CS357 Course Development Container
# ----------------------------------
# One image that runs every CS357 lab: the Python libraries for retrieval,
# classical ML, NLP, and explainability, plus Node.js and promptfoo for the
# evaluation lab. The ONE thing that stays OUTSIDE this container is Ollama:
# it runs natively on your host for model performance, and code inside the
# container reaches it at http://host.docker.internal:11434 -- exactly the
# host-bridge pattern from the "Docker from Zero" activity.
#
# Build it (from inside your work repo's .devcontainer/ folder):
#   docker compose build
# Enter it:
#   docker compose run --rm cs357
#
# The container sees ONLY the directory you mount at /workspace (your
# cloned GitHub work repo). Nothing else on your machine is visible to it.

FROM python:3.11-slim

LABEL org.opencontainers.image.title="CS357 course development environment" \
      org.opencontainers.image.description="Python 3.11 with the CS357 lab libraries (requests, chromadb, sentence-transformers, scikit-learn, spacy, shap, lime, flask, ...) plus Node.js and promptfoo; talks to host Ollama via host.docker.internal" \
      org.opencontainers.image.authors="CS357 course staff" \
      org.opencontainers.image.url="https://www.billmongan.com/Ursinus-CS357-Fall2026/"

# System packages:
#   git    -- commit and push your work from inside the container
#   curl   -- probe the Ollama API and other HTTP endpoints
#   nodejs, npm -- run promptfoo (Rubric Pipeline Lab)
#   zip    -- package submissions
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
        nodejs \
        npm \
        zip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python packages, one per line, each tagged with the lab that uses it.
# (Comment lines inside a RUN continuation are stripped by the Dockerfile
# parser, so this reads as one pip install.)
RUN pip install --no-cache-dir \
        # requests -- every lab: HTTP calls to the Ollama API on the host
        requests \
        # chromadb -- RAG Knowledge Base Lab: the vector store for retrieval
        chromadb \
        # sentence-transformers -- RAG Knowledge Base Lab: embedding text for retrieval
        sentence-transformers \
        # scikit-learn -- Multi-Agent Patterns, Rubric Pipeline, Responsible AI: classical ML models and metrics
        scikit-learn \
        # numpy -- Multi-Agent Patterns, Rubric Pipeline, Responsible AI: the arrays underneath everything
        numpy \
        # spacy -- Responsible AI Capstone Direction 2: NLP pipelines
        spacy \
        # shap -- Responsible AI Capstone Direction 3: model explanations
        shap \
        # lime -- Responsible AI Capstone Direction 3: model explanations
        lime \
        # matplotlib -- Responsible AI Capstone Direction 3: plots
        matplotlib \
        # pandas -- Responsible AI Capstone Direction 3: tabular data
        pandas \
        # flask -- Local Agent Lab Direction 4: a small web endpoint for your agent
        flask

# The small English model spacy needs (Responsible AI Capstone Direction 2), baked into the
# image so the lab works offline.
RUN python -m spacy download en_core_web_sm

# promptfoo -- Rubric Pipeline Lab: prompt/agent evaluation harness.
RUN npm install -g promptfoo

# Code inside the container reaches the HOST's Ollama server here. This is
# the special DNS name Docker provides for "my host machine"; on Linux the
# compose file adds it explicitly via extra_hosts.
ENV OLLAMA_HOST=http://host.docker.internal:11434

# Work as a regular (non-root) user, like you would on your own machine.
RUN useradd --create-home --shell /bin/bash student
USER student

# All course work happens here; docker-compose.yml bind-mounts your cloned
# GitHub repo at this path.
WORKDIR /workspace

# Default to an interactive shell.
CMD ["bash"]
