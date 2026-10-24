"""Run with: uv run streamlit run ap.py"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import APIConnectionError, APIStatusError, AuthenticationError, Groq, RateLimitError

MODEL = "openai/gpt-oss-120b"
SYSTEM_PROMPT = "You are a helpful personal assistant. Be clear, accurate, and concise."

load_dotenv(Path(__file__).with_name(".env"))


def get_api_key() -> str:
    """Support local .env files and Streamlit Cloud secrets."""
    if key := os.environ.get("GROQ_API_KEY"):
        return key
    try:
        return st.secrets.get("GROQ_API_KEY", "")
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return ""


def get_reply(api_key: str, history: list[dict[str, str]]) -> str:
    # Bound the context and response size for the public demo.
    with Groq(api_key=api_key, timeout=30.0, max_retries=0) as client:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history[-20:]],
            max_completion_tokens=2048,
        )
    if not response.choices or not response.choices[0].message.content:
        raise ValueError("The model returned no text. Please try again.")
    return response.choices[0].message.content


def main() -> None:
    st.set_page_config(page_title="Agent Harness | Chat Demo", page_icon="💬")
    st.title("Agent Harness")
    st.caption("An interactive assistant powered by Groq · GPT OSS 120B")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("About this demo")
        st.write("Ask a question, explore an idea, or get help understanding code.")
        st.caption("Conversation history is kept in your browser session and sent to Groq when you chat. Avoid sharing sensitive information.")
        st.caption("This demo shows conversational chat. File tools, MCP, and persistent memory are available in the repository's terminal examples.")
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    api_key = get_api_key()
    if not api_key:
        st.info("The demo needs a Groq API key. The app owner can add GROQ_API_KEY to Streamlit Secrets or a local .env file.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask me anything…", disabled=not api_key, max_chars=4000)
    if not prompt or not prompt.strip():
        return

    user_message = {"role": "user", "content": prompt.strip()}
    with st.chat_message("user"):
        st.markdown(user_message["content"])

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking…"):
                reply = get_reply(api_key, [*st.session_state.messages, user_message])
        except AuthenticationError:
            st.error("The demo's API key was rejected. The app owner needs to update GROQ_API_KEY.")
        except RateLimitError:
            st.warning("The demo has reached its API usage limit. Please try again later.")
        except APIConnectionError:
            st.error("Could not reach Groq. Please try again shortly.")
        except APIStatusError:
            st.error("Groq could not complete this request. Please try again later.")
        except ValueError as error:
            st.warning(str(error))
        else:
            st.markdown(reply)
            st.session_state.messages.extend([user_message, {"role": "assistant", "content": reply}])


if __name__ == "__main__":
    main()
