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

## Local inference with Ollama

Run these commands in the same Linux or WSL2 environment where you run the
Python application. Phase 1 uses `qwen3:4b` for local inference.

### 1. Install Ollama and download the model

If Ollama is missing, follow the [Ollama installation guide for Linux](https://docs.ollama.com/linux)
or run the official installer.

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Check whether the local server is responding.

```bash
curl --fail --silent --show-error --max-time 5 \
  http://127.0.0.1:11434/api/version
```

If the connection is refused, run `ollama serve` in a separate terminal and
leave it running. Then download the model and confirm it is available.

```bash
ollama pull qwen3:4b
ollama list
```

### 2. Configure the application

From the repository root, create `.env` from the example if you do not
already have one.

```bash
cp -n .env.example .env
```

The example uses `http://127.0.0.1:11434`, `qwen3:4b`, a 4096-token context
window, and a 120-second socket timeout. If you already have a `.env`, check
that it defines `SR_OLLAMA_BASE_URL`, `SR_OLLAMA_MODEL`,
`SR_OLLAMA_CONTEXT_TOKENS`, and `SR_OLLAMA_TIMEOUT_SECONDS`.

Keep `.env` local to each computer and commit only `.env.example`.

### 3. Start a terminal conversation

```bash
uv run --locked python main.py --chat
```

Ask a question related to the thesis, then ask a follow-up in the same
session. The application sends the prior turns to Ollama and prints the
provider, model, and latency after each successful reply. Type `/salir`
or press `Ctrl+C` to end the session. The conversation history is held
in memory for the current session.

To verify that the chat carries context across turns, try these prompts in order:

1. «Imagina una cooperativa editorial llamada Faro que recibe donaciones
   de papel. Explica en una frase por qué es un sistema abierto».
2. «¿Cómo se llamaba la organización y qué recurso recibía?».

The second reply should identify Faro and paper.

### 4. Check model connectivity in the browser

```bash
uv run --locked streamlit run streamlit_app.py --server.address 127.0.0.1
```

Open [localhost:8501](http://localhost:8501) and click **Probar modelo**.
The page sends one academic question to Ollama and displays the reply,
model name, and latency.

## Project status

- **Phase 0 — Project setup:** Reproducible Python 3.12 environment managed
  with uv and a minimal command-line entry point.
- **Phase 1 — Local inference:** Ollama with `qwen3:4b`, an interactive
  terminal chat with in-memory session history, and a Streamlit page for
  checking model connectivity.
