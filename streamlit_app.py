"""Run a real Ollama generation check from the local browser interface."""

import streamlit as st

from llm.contracts import ChatMessage
from llm.ollama import OllamaClient
from llm.settings import OllamaSettings

st.title("S&R AI Assistant")

question = (
    "¿Qué significa que una organización sea un sistema abierto? "
    "Responde en dos frases y en español."
)
st.write(question)

# Streamlit reruns te script on interaction. The button scopes the model call to an explocot click.

if st.button("Probar modelo"):
    try:
        client = OllamaClient(OllamaSettings())
        with st.spinner("Esperando la respuesta de Ollama..."):
            reply = client.chat([ChatMessage(role="user", content=question)])
    except(OSError, ValueError, KeyError, TypeError) as error:
        st.error(f"La prueba de Ollama falló. {error}")
    else:
        st.success(f"{reply.provider} respondió con {reply.model}.")
        st.write(reply.content)
        st.caption(f"Latencia: {reply.latency_seconds:.2f} s")
