# Study and Research AI Assistant

An AI engineering portfolio project focused on building, evaluating, and
running an LLM application with Python and LangGraph. A graduate thesis
provides the real-world use case for document retrieval and evidence-based
research workflows.

## Engineering skills

The project is designed to demonstrate:

- Reproducible Python environments, dependency management, and automated testing.
- Local and cloud LLM integration, with provider selection and usage tracking.
- LangGraph orchestration with persistent state and human review.
- Retrieval-augmented generation (RAG), source attribution, and evaluation
  of retrieval and response quality.

## Installation

Use a Linux terminal. On Windows, run these commands inside your WSL2
distribution. Repeat the setup on each computer to create its own `.venv`.

### 1. Install Git and uv

If Git or curl is missing on Debian or Ubuntu, install the prerequisites.

```bash
sudo apt update
sudo apt install git curl ca-certificates
```

If uv is missing, use the [official uv installer](https://docs.astral.sh/uv/getting-started/installation/).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Open a new terminal and verify that both tools are available.

```bash
git --version
uv --version
```

### 2. Get the project

For a fresh checkout, run the following from your projects directory.

```bash
git clone https://github.com/ralphvb/study-research-ai-assistant.git
cd study-research-ai-assistant
```

For an existing checkout on `main`, run `git pull --ff-only origin main`
from the repository root.

### 3. Set up Python and verify the installation

Run these commands from the repository root.

```bash
uv python install 3.12
uv sync --locked
uv run --locked python main.py
```

`uv sync --locked` creates or updates `.venv` using the committed `uv.lock`.
It fails if the lockfile needs to be updated. The command-line entry point
prints the application name, the Python 3.12.x version, and the path to the
interpreter inside `.venv`.

When verifying the same setup on two computers, compare the output of
`git rev-parse HEAD` and check `git status --short` for local changes.
The Python 3.12 patch version and interpreter path may differ.

## Project status

Phase 0 establishes a reproducible Python 3.12 environment and a minimal
command-line entry point.