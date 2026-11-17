"""Streamlit interface for the Agentic Customer Support demo."""

import os

import streamlit as st


st.set_page_config(
    page_title="Customer Support Assistant",
    page_icon="💬",
    layout="centered",
)


def get_gemini_api_key() -> str | None:
    """Read the API key from Streamlit secrets first, then the environment."""
    for key_name in ("GEMINI_API_KEY", "Gemini_Api_Key"):
        try:
            value = st.secrets.get(key_name)
        except FileNotFoundError:
            value = None
        if value:
            return str(value)

        value = os.getenv(key_name)
        if value:
            return value
    return None


st.title("Customer Support Assistant")
st.caption("Ask about a demo order, a refund, a return, or the store policies.")

with st.sidebar:
    st.header("Demo data")
    st.write("Try order **12345** (shipped) or **12346** (processing).")
    st.divider()
    st.caption("This demo uses simulated order data. Do not enter personal or payment information.")

api_key = get_gemini_api_key()
if not api_key:
    st.error("Gemini API key is not configured.")
    st.info(
        "For Streamlit Community Cloud, add `GEMINI_API_KEY` under "
        "Advanced settings → Secrets, then redeploy."
    )
    st.stop()

# The agent reads its key at import time. Setting this variable lets the same code
# work locally with .env and in Streamlit Cloud with st.secrets.
os.environ["GEMINI_API_KEY"] = api_key

try:
    from agentic_rag import ask_agent
except Exception as exc:
    st.error("The support agent could not start.")
    st.exception(exc)
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("For example: Can I return order 12345 because it is damaged?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking the available information…"):
            try:
                response = ask_agent(prompt)
            except Exception:
                response = (
                    "I couldn't complete that request right now. Please check the "
                    "Gemini API key and try again."
                )
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
