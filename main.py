"""Show the Python runtime or start a local academic conversation."""

import argparse
import sys

from llm.contracts import ChatClient, ChatMessage
from llm.ollama import OllamaClient
from llm.settings import OllamaSettings


def run_chat(client: ChatClient) -> None:
    """Send the session history with each new question."""

    history = [
        ChatMessage(
            role="system",
            content=(
                "Eres un asistente de estudio e investigación para una tesina "
                "sobre modelos de negocio, pensmiento sistémico y "
                "configuraciones organizacionales. Responde en español y "
                "con brevedad. Si una solicitud queda fuera de ese ámbito, "
                "explica el alcance. Si falta evidencia, indícalo."
            )
        )
    ]

    print("Study & Research AI Assistant. Escribe '/salir' para terminar")

    while True:
        prompt = input("\nTú: ").strip()

        if prompt == "/salir":
            return
        
        if not prompt:
            continue

        user_message = ChatMessage(role="user", content=prompt)

        try:
            reply = client.chat([*history, user_message])
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"Error al consultar el modelo: {error}", file=sys.stderr)
            continue

        history.extend([
            user_message,
            ChatMessage(role="assistant", content=reply.content)
        ])

        print(f"\nAsistente: {reply.content}")
        print(f"{reply.provider} . {reply.model} . {reply.latency_seconds:2f} s")


def main() -> None:
    """Run the selected command and report startup errors."""
    parser = argparse.ArgumentParser(description="Study and Research AI Assistant")
    parser.add_argument("--chat", action="store_true", help="Start a local chat.")
    args = parser.parse_args()

    if args.chat:
        try:
            settings = OllamaSettings()
        except ValueError as error:
            parser.exit(1, f"Configuración de Ollama inválida:\n{error}\n")

        try:
            run_chat(OllamaClient(settings))
        except (EOFError, KeyboardInterrupt):
            print("\nSesión terminada.")
        return

    print("Study and Research AI Assistant")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Python executable: {sys.executable}")


if __name__ == '__main__':
    main()
