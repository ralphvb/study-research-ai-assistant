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
Python application. The project uses `qwen3:4b` for local inference.

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

### 2. Configure Ollama for this checkout

From the repository root, create `.env` if it does not already exist.

```bash
cp -n .env.example .env
```

Add these settings to your local `.env`.

```dotenv
SR_OLLAMA_BASE_URL=http://127.0.0.1:11434
SR_OLLAMA_MODEL=qwen3:4b
SR_OLLAMA_CONTEXT_TOKENS=4096
SR_OLLAMA_TIMEOUT_SECONDS=300
```

Use 300 seconds as a starting socket timeout for the local model test.
Adjust it on each computer based on observed response times. Leave the
optional generation cap unset for the initial test. An explicit cap can
stop generation before the model produces its final answer.

Keep `.env` local to each computer. Use `.env.example` as a template for
variable names and leave its values blank.

### 3. Disable Ollama cloud features for local-only use

Open `~/.ollama/server.json` with `vim` as the account that runs the Ollama
server. For a new file, use this JSON object. If the file already exists,
add the `disable_ollama_cloud` property to its existing object and preserve
the other settings.

```json
{
  "disable_ollama_cloud": true
}
```

Restart the Ollama server to apply the setting. This setting applies to
Ollama. The OpenAI option in Streamlit uses a separate API.

See the [Ollama local FAQ](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features).

### 4. Start a terminal conversation

```bash
uv run --locked python main.py --chat
```

Ask a question related to the thesis, then ask a follow-up in the same
session. The application sends the prior turns to Ollama and prints the
provider, model, and latency after each successful reply. Type `/salir`
or press `Ctrl+C` to end the session. The conversation history is held
in memory for the current session.

To verify that the chat carries context across turns, try these prompts in
order.

1. «Imagina una cooperativa editorial llamada Faro que recibe donaciones
   de papel. Explica en una frase por qué es un sistema abierto».
2. «¿Cómo se llamaba la organización y qué recurso recibía?».

The second reply should identify Faro and paper.

## Cloud inference with OpenAI

Use an OpenAI API project with access to `gpt-4.1-mini`. For a restricted
project key, grant write access to **Model capabilities → Responses**
(`/v1/responses`).

If you are setting up OpenAI on a fresh checkout, create `.env` from
`.env.example` as shown above. Add these settings to your local `.env`.

```dotenv
OPENAI_API_KEY=<your-project-api-key>
SR_OPENAI_MODEL=gpt-4.1-mini
SR_OPENAI_TIMEOUT_SECONDS=30
```

Replace the API key placeholder before running the OpenAI test. Use
30 seconds as a starting request timeout. Keep the key in your local
`.env` and leave its entry blank in `.env.example`.

See [OpenAI API project settings](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform)
and the [Responses API reference](https://developers.openai.com/api/reference/resources/responses/methods/create).

## Test both providers in Streamlit

From the repository root, run:

```bash
uv sync --locked
uv run --locked streamlit run streamlit_app.py --server.address 127.0.0.1
```

Open [127.0.0.1:8501](http://127.0.0.1:8501) and run the same test with
each configured provider.

1. Select **Ollama (local)** and click **Probar modelo**.
2. Select **OpenAI (cloud)** and click **Probar modelo** again.

The page loads and validates the settings for the selected provider and
sends one question in Spanish about organizations as open systems. A
successful test shows the provider, reported model, answer, latency, and
token counts when available. If the request fails, the page displays the
error for the selected provider.

### Phase 2 verification

Both providers returned a two-sentence answer in Spanish on the work
computer.

| Provider | Reported model | Latency | Input tokens | Reported output tokens |
| --- | --- | ---: | ---: | ---: |
| Ollama | `qwen3:4b` | 176.02 s | 32 | 1405 |
| OpenAI | `gpt-4.1-mini-2025-04-14` | 2.31 s | 26 | 47 |

These figures come from one run per provider. Local latency can vary with
the computer and the number of tokens generated. Verification of the final
commit on the personal computer is pending.

## Project status

- **Phase 0 — Project setup.** Reproducible Python 3.12 environment managed
  with uv and a minimal command-line entry point.
- **Phase 1 — Local inference.** Ollama with `qwen3:4b`, an interactive
  terminal chat with in-memory session history, and a Streamlit page for
  checking model connectivity.
- **Phase 2 — Provider selection.** Streamlit can test the same prompt
  with local Ollama or the OpenAI Responses API and display the model,
  latency, and token usage returned by the selected provider.