# Agentic Customer Support

A Streamlit customer-support demo powered by Gemini, LangChain, and LangGraph. It can look up the included demo orders, calculate a potential refund, start an eligible return, and explain return policies.

## Run locally

1. Create a `.env` file containing `GEMINI_API_KEY=your_key`.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Start the app: `python -m streamlit run app.py`.

Demo order IDs: `12345` (shipped) and `12346` (processing).

## Deploy to Streamlit Community Cloud

Create a Community Cloud app from `app.py`, then add this secret in the app's **Advanced settings → Secrets**:

```toml
GEMINI_API_KEY = "your_key"
```

Never commit `.env` or a `secrets.toml` file.
