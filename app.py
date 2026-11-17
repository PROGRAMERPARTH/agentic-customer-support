"""Streamlit interface for the Agentic Customer Support demo."""

import os

import streamlit as st


st.set_page_config(
    page_title="Customer Support Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
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


def start_new_chat() -> None:
    st.session_state.messages = []


def set_suggested_prompt(prompt: str) -> None:
    st.session_state.suggested_prompt = prompt


def display_message(role: str, content: str) -> None:
    avatar = "🧑🏽" if role == "user" else "✨"
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


st.markdown(
    """
    <style>
        .stApp { background: #f7f9fc; }
        [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e8edf5; }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
        .block-container { max-width: 1060px; padding-top: 2.1rem; padding-bottom: 7rem; }
        .hero {
            background: linear-gradient(120deg, #14213d 0%, #1d4ed8 100%);
            border-radius: 24px;
            padding: 2.4rem 2.6rem;
            color: #ffffff;
            box-shadow: 0 18px 42px rgba(29, 78, 216, .16);
            margin-bottom: 1.6rem;
        }
        .hero h1 { color: #ffffff; font-size: 2.5rem; margin: 0 0 .5rem; letter-spacing: -.04em; }
        .hero p { color: #dbeafe; font-size: 1.05rem; margin: 0; }
        .eyebrow { color: #93c5fd; font-size: .76rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
        .feature-card {
            background: #ffffff; border: 1px solid #e6ebf3; border-radius: 16px;
            padding: 1rem 1.1rem; min-height: 92px;
        }
        .feature-card strong { display: block; color: #14213d; margin-bottom: .2rem; }
        .feature-card span { color: #64748b; font-size: .9rem; }
        [data-testid="stChatMessage"] { border-radius: 18px; }
        [data-testid="stChatInput"] { border-radius: 18px; }
        .sidebar-note { color: #64748b; font-size: .85rem; line-height: 1.55; }
        .status-dot { color: #16a34a; font-weight: 700; }
        @media (max-width: 740px) {
            .block-container { padding-top: 1.2rem; }
            .hero { padding: 1.7rem; border-radius: 18px; }
            .hero h1 { font-size: 2rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Support desk")
    st.markdown('<p class="status-dot">● Assistant online</p>', unsafe_allow_html=True)
    st.divider()

    st.markdown("#### Try a quick question")
    st.button(
        "Track order 12345",
        use_container_width=True,
        on_click=set_suggested_prompt,
        args=("What is the status of order 12345?",),
    )
    st.button(
        "Check a refund",
        use_container_width=True,
        on_click=set_suggested_prompt,
        args=("What refund would I get for order 12345 if it is damaged?",),
    )
    st.button(
        "View return policy",
        use_container_width=True,
        on_click=set_suggested_prompt,
        args=("What is your return policy?",),
    )

    st.divider()
    st.markdown("#### Demo orders")
    st.caption("**12345** · Shipped\n\n**12346** · Processing")
    st.markdown(
        '<p class="sidebar-note">This is a simulated support experience. Please do not enter personal, payment, or account information.</p>',
        unsafe_allow_html=True,
    )
    st.button("Start a new chat", use_container_width=True, on_click=start_new_chat)

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">AI-powered customer care</div>
        <h1>How can we help?</h1>
        <p>Get fast answers about demo orders, refunds, returns, and store policies.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

feature_1, feature_2, feature_3 = st.columns(3)
with feature_1:
    st.markdown('<div class="feature-card"><strong>📦 Order tracking</strong><span>Check the latest status for a demo order.</span></div>', unsafe_allow_html=True)
with feature_2:
    st.markdown('<div class="feature-card"><strong>↩️ Returns</strong><span>Find out whether a return can be started.</span></div>', unsafe_allow_html=True)
with feature_3:
    st.markdown('<div class="feature-card"><strong>💳 Refunds</strong><span>Understand the refund amount and policy.</span></div>', unsafe_allow_html=True)

with st.expander("What can I ask the assistant?", expanded=False):
    st.markdown(
        """
        The assistant works with **two predefined demo orders**. It can help with:

        - **Order status:** “What is the status of order 12345?”
        - **Return eligibility:** “Can I return order 12345 because it is damaged?”
        - **Refund estimates:** “What refund would I get for order 12345 if I changed my mind?”
        - **Start a return:** “Start a return for order 12345 because it is defective.”
        - **Store policies:** “What is your return policy?” or “When will I receive my refund?”
        """
    )

    st.markdown("##### Predefined order data")
    st.dataframe(
        [
            {"Order ID": "12345", "Items": "item1, item2", "Total": "$100.00", "Status": "Shipped"},
            {"Order ID": "12346", "Items": "item3, item4", "Total": "$200.00", "Status": "Processing"},
        ],
        hide_index=True,
        use_container_width=True,
    )
    st.caption("These are simulated records for demonstration only. The assistant cannot access real customer orders.")

st.markdown("#### Conversation")

api_key = get_gemini_api_key()
if not api_key:
    st.error("Gemini API key is not configured.")
    st.info("In Streamlit Community Cloud, add `GEMINI_API_KEY` in Advanced settings → Secrets, then redeploy.")
    st.stop()

# The agent reads its key at import time. This supports local .env files and
# Streamlit Cloud secrets without ever writing the secret to the repository.
os.environ["GEMINI_API_KEY"] = api_key

try:
    from agentic_rag import ask_agent
except Exception:
    st.error("The support assistant could not start. Check the app logs and Gemini API configuration.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    display_message(message["role"], message["content"])

suggested_prompt = st.session_state.pop("suggested_prompt", None)
typed_prompt = st.chat_input("Ask about an order, a return, refund, or store policy…")
prompt = suggested_prompt or typed_prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    display_message("user", prompt)

    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Looking into that for you…"):
            try:
                response = ask_agent(prompt)
            except Exception:
                response = (
                    "I couldn't complete that request right now. Please try again in a moment. "
                    "If the issue continues, check the Gemini API key and app logs."
                )
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
