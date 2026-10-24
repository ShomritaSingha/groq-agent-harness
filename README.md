# Agent Harness

**A hands-on exploration of how an AI chat assistant grows into an agent with tools, memory, and external services.**

This project includes an interactive Streamlit chat app and a series of Python examples that build toward a complete agent harness. All model requests use **Groq** with **`openai/gpt-oss-120b`**.

## Try the assistant

<p align="center">
  <a href="https://groq-agent-harnesssimplebot.streamlit.app/">
    <img src="assets/demo-arrow.gif" width="64" height="56" alt="Jumping arrow pointing to the live chatbot">
  </a>
  <br>
  <strong><a href="https://groq-agent-harnesssimplebot.streamlit.app/">🚀 TRY THE LIVE CHATBOT</a></strong>
</p>

**[Open the interactive demo →](https://groq-agent-harnesssimplebot.streamlit.app/)** — chat directly in your browser. No installation or API key needed.

Once the app is open:

1. Type a question in the chat box and press Enter.
2. Ask a follow-up to try conversation history.
3. Select **Clear conversation** in the sidebar to start again.

Try these prompts:

> Explain the difference between a chatbot and an AI agent with a simple example.

> Write a Python function that counts words in a sentence, then explain it.

> Now show me how to test that function.

The web demo supports conversational chat. The terminal examples add file tools, MCP servers, and persistent memory, as described below.

## What this project demonstrates

- **LLM integration:** synchronous and asynchronous requests through the Groq Python SDK.
- **Tool calling:** the model selects a function, Python executes it, and the result returns to the model.
- **Agent loops:** repeated tool calls until the model produces a final response.
- **MCP integration:** external time and web-fetch tools through the Model Context Protocol.
- **Memory:** saved facts loaded into the assistant's prompt across terminal sessions.
- **Web interaction:** a Streamlit interface with separate conversation histories per visitor session and clear API error messages.

## Quick start

You need **Python 3.13 or newer**, **[uv](https://docs.astral.sh/uv/getting-started/installation/)**, and a **[Groq API key](https://console.groq.com/keys)**.

### 1. Get the code

Clone this repository using its GitHub **Code** button, then open the cloned project folder in your terminal. Alternatively, download and extract the ZIP.

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure your key

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows, you can copy the file using your editor or file explorer. Edit `.env` and replace the placeholder:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

The scripts load `.env` automatically. If `GROQ_API_KEY` is already exported in your environment, that value takes precedence. Your actual key stays out of Git through `.gitignore`.

### 4. Launch the chat app

```bash
uv run streamlit run ap.py
```

Open the local URL shown in your terminal, usually `http://localhost:8501`.

Local users supply their own Groq key. Visitors to a hosted deployment use the key configured by the app owner and do not need to install anything.

## Explore the agent examples

The numbered scripts show the progression from a single model request to an agent with tools and memory.

| File | What it demonstrates |
| --- | --- |
| [`ap.py`](ap.py) | Streamlit chat interface, session history, and API error handling |
| [`v0.py`](v0.py) | Basic chat; each question is independent |
| [`v1.py`](v1.py) | List/read tools with one round of tool execution |
| [`v2.py`](v2.py) | Repeated tool execution, including writing files |
| [`v3.py`](v3.py) | Async agent with local tools and time/fetch MCP servers |
| [`v4.py`](v4.py) | Conversation history and persistent memory in `memory.md` |
| [`harness.py`](harness.py) | Combined async harness with file tools, MCP, memory, and commands |

Run any terminal example from the project folder:

```bash
uv run v0.py
```

For the file tools, create a workspace and put sample files inside it:

```bash
mkdir -p workspace
```

The `workspace/` directory is ignored by Git. Write tools can overwrite files in it.

Run the combined harness:

```bash
uv run harness.py
```

| Command | Action |
| --- | --- |
| `/models` | List configured models |
| `/model groq` | Select the configured Groq model |
| `/tools` | Show available local and MCP tools |
| `/memory` | Display saved memory |
| `/quit` | Exit the harness |

`v3.py` launches time and fetch MCP servers using `uvx`. The combined harness reads its server configuration from [`mcp_servers.json`](mcp_servers.json). First startup may download server packages.

### How the agent loop works

```text
User message → Model request → Final answer
                     ↓
                 Tool call
                     ↓
              Execute function
                     ↓
           Return result to model
```

For the terminal assistants with memory, `memory.md` is loaded at startup and updated through the `save_memory` tool. The file is created when a fact is first saved if it does not exist. Personal memory is ignored by Git.

## Deploy your own web demo

1. Push the project to GitHub, including `ap.py`, `pyproject.toml`, `uv.lock`, and `.streamlit/config.toml`.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and create an app from your repository and branch.
3. Set the entrypoint to **`ap.py`**. In Advanced settings, select **Python 3.13**.
4. Add this configuration under **Secrets**, replacing the placeholder with your real key:

   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   ```

5. Deploy and test the app. Add its public URL to the **Try the assistant** section above and your GitHub repository's **About → Website** field.

Community Cloud supports the committed `uv.lock`; no separate `requirements.txt` is needed. Follow Streamlit's official [deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app), [dependency guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies), and [secrets guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## Conversation data and demo limits

The web app keeps history in Streamlit session state and does not write conversations to disk. Each visitor session has its own history. Requests send messages to Groq for inference; avoid entering sensitive information.

The web app does not load personal workspace files or `memory.md`. File tools and MCP run through the terminal examples.

Each web request includes up to the last 20 messages, accepts up to 4,000 input characters, and uses a 2,048-token response budget. Hosted requests consume the app owner's Groq quota. These request limits do not set an account-wide spending cap.

## Tests

```bash
uv run python -m unittest discover -s tests -v
```

The tests use Streamlit's testing framework and mocked Groq responses. They cover conversation history, session isolation, clearing history, environment and Streamlit Secrets configuration, and authentication/rate-limit errors. They do not make live LLM requests.

## Troubleshooting

| Issue | What to check |
| --- | --- |
| Chat input is disabled | Set `GROQ_API_KEY` in local `.env` or deployed Streamlit Secrets. |
| `401 Invalid API Key` | Check the key value and any exported variable overriding `.env`. Use `Groq()`, rather than passing the literal string `"GROQ_API_KEY"` as the key. |
| API usage limit message | Check the Groq account's quota and try again later. |
| File tools cannot find a workspace | Create `workspace/` beside the scripts and add sample files. |
| MCP server fails to start | Check that `uvx` is available, internet access works, and `mcp_servers.json` contains valid commands. |

## Built with

Python · Groq · GPT OSS 120B · Streamlit · MCP · Pydantic · python-dotenv · uv
