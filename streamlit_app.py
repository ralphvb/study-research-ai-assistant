"""Provide a PDF workspace and model connectivity tests in Streamlit."""

import streamlit as st
from openai import APIConnectionError, APIStatusError
from pydantic import ValidationError

from documents.pdf import read_pdf_pages
from llm.contracts import ChatClient, ChatMessage
from llm.ollama import OllamaClient
from llm.openai import OpenAICLient
from llm.settings import OllamaSettings, OpenAISettings

QUESTION = (
    "¿Qué significa que una organización sea un sistema abierto? "
    "Responde en dos frases y en español."
)

# QUESTION = "Responde únicamente listo."


def render_workspace() -> None:
    """Preview extracted text by physical PDF page number."""
    upload = st.file_uploader("PDF Document", type=["pdf"])

    if upload is None:
        return

    try:
        pages = read_pdf_pages(upload.getvalue())
    except ValueError as error:
        st.error(str(error))

    page_number = st.selectbox("PDF page", [page.number for page in pages])
    page = pages[page_number - 1]
    st.text(page.text or "This page does not extractable text.")


def render_model_test() -> None:
    """Send the fixed test propmt to the seected provider on demand."""
    provider = st.radio("Proveedor", ["Ollama (local)", "OpenAI (cloud)"])

    st.write(QUESTION)

    if not st.button("Probar modelo"):
        return

    # Load only the selected provider's settings.
    client: ChatClient
    try:
        if provider == "OpenAI (cloud)":
            client = OpenAICLient(OpenAISettings())
        else:
            client = OllamaClient(OllamaSettings())

        with st.spinner(f"Esperando respuesta de {provider}"):
            reply = client.chat([ChatMessage(role="user", content=QUESTION)])
    except ValidationError:
        st.error(f"Revisa las credenciales para {provider}.")
        return
    except APIStatusError as error:
        st.error(f"{provider} rechazó la solicitud HTTP: {error.status_code}")
        return
    except APIConnectionError:
        st.error(f"La conexión con {provider} falló o agotó el tiempo de espera.")
        return
    except (OSError, ValueError, KeyError, TypeError) as error:
        st.error(f"La prueba con {provider} falló: {error}")
        return

    st.success(f"{reply.provider} respondió con {reply.model}.")
    st.write(reply.content)
    st.caption(f"Latencia: {reply.latency_seconds:.2f} s")

    if reply.input_tokens is not None:
        st.caption(f"Tokens de entrada: {reply.input_tokens}")

    if reply.output_tokens is not None:
        st.caption(f"Token de salida: {reply.output_tokens}")


def main() -> None:
    """Show the document workspace or the model connectivity test."""
    st.title("S&R AI Assistant")
    section = st.radio("Section", ["Workspace", "Test models"])

    if section == "Workspace":
        render_workspace()
    else:
        render_model_test()


if __name__ == "__main__":
    main()
