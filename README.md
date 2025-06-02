# 🧠 MCP Agent with Mem0 and Task/Calendar Integration

A MCP Agent that integrates with multiple **Model Context Protocol (MCP)** servers to provide AI agents with long-term memory, task management, and calendar event capabilities. This project uses **Mem0**, **Qdrant**, and **FastMCP** to deliver an intelligent and extensible agent system.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Running the Project](#running-the-project)
- [Assets](#assets)
- [Tech Stack](#tech-stack)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Overview

This POC demonstrates an MCP Agent that connects to **three MCP servers**:

- **Memory Server** — Stores and retrieves memory using Mem0 and Qdrant.
- **Task Manager Server** — Adds, retrieves, and marks tasks as completed.
- **Calendar Manager Server** — Fetches calendar events.

Core components:

- **LangChain Agent** — For orchestrating tool use.
- **OpenAI-Compatible API** — For intent classification and LLM-powered responses.
- **Mem0 + Qdrant** — Long-term memory with vector search.
- **FastMCP** — Communication over Server-Sent Events (SSE).

---

## Features

- 📚 **Memory Management**
  - Store, search, and retrieve memories via Mem0 and Qdrant.
  
- ✅ **Task Management**
  - Add, list, and complete tasks using JSON-backed MCP server.
  
- 📅 **Calendar Management**
  - Query and retrieve upcoming calendar events.
  
- 🤖 **Intent Classification**
  - Classify queries to determine whether to use memory, task, or calendar tools.
  
- 🌐 **Multi-Server Communication**
  - Supports multiple MCP endpoints using SSE and authentication.

- 🧠 **Agent Intelligence**
  - Uses LangChain agents to reason over which tool to use and manage dialogue.

---

## Prerequisites

- Python **3.13+**
- [`uv`](https://github.com/astral-sh/uv) (fast dependency manager)
- OpenAI API key or compatible local API (e.g., Ollama)
- Qdrant running locally (configured in `qdrant_db/`)
- Git (for cloning the repo)

---

## Environment Setup

### 1. Install dependencies using `uv`

```bash
uv sync
```

### 2. Install and Configure Ollama

If you're using a local LLM backend (like Ollama):

```bash
# Install Ollama from https://ollama.com

# For features involving LLM-driven tool use (like in client/02_llm.py and client/03_agents.py),
# you need an Ollama model that supports OpenAI-compatible function/tool calling.
# 'qwen2:7b-instruct' is a good candidate for this. Ensure it's pulled and available:
ollama pull qwen2:7b-instruct

# Other models like llama3:latest might not support tool calling out-of-the-box.
# You can list your installed models with `ollama list`.
# If using a different model, verify its tool-calling capabilities.
```

Or configure your .env for OpenAI or Inferix endpoints.

### 3. Set Environment Variables

Create a `.env` file in the project root (you can copy `.env.example` if it exists):

```bash
cp .env.example .env
```

Edit the `.env` file with the necessary configurations. Here are the key variables:

**For using Ollama (local LLM):**

```env
# Specify the Ollama model to use (e.g., llama3, qwen2:7b-instruct)
MODEL="qwen2:7b-instruct" # or LLM_CHOICE for 03_agents.py
# Set a placeholder API key for the OpenAI library
OPENAI_API_KEY="ollama"
# Point to your local Ollama server's OpenAI-compatible API endpoint
OPENAI_BASE_URL="http://localhost:11434/v1"
# OLLAMA_BASE_URL might also be used by some scripts if OPENAI_BASE_URL is not picked up.
OLLAMA_BASE_URL="http://localhost:11434/v1"
```

**For using OpenAI API (cloud LLM):**

```env
# Specify the OpenAI model to use (e.g., gpt-3.5-turbo, gpt-4o-mini)
MODEL="gpt-4o-mini" # or LLM_CHOICE for 03_agents.py
# Your actual OpenAI API key
OPENAI_API_KEY="sk-your_openai_api_key_here"
# Ensure OPENAI_BASE_URL and OLLAMA_BASE_URL are commented out or removed if using OpenAI directly.
# # OPENAI_BASE_URL="http://localhost:11434/v1"
# # OLLAMA_BASE_URL="http://localhost:11434/v1"
```

The API keys `secret-key1`, `secret-key2`, `secret-key3` found in `servers.yaml` are for the internal authentication of this project's MCP servers and are separate from your LLM provider API keys.

### 4. Start Qdrant Locally

You can run Qdrant via Docker (adjust path as needed):

```bash
docker run -p 6333:6333 -v $(pwd)/qdrant_db:/qdrant/storage qdrant/qdrant
```

**Note for Windows Users:** If using Command Prompt or PowerShell, replace `$(pwd)` with the absolute path to the project's `qdrant_db` directory (e.g., `-v C:\\Users\\YourUser\\path\\to\\ishwanku-mcp-agent-poc\\qdrant_db:/qdrant/storage`).

## Running the Project

**Important Run Order:**

1. Ensure prerequisite services (Qdrant, and Ollama if used) are started and running.
2. Start the MCP servers.
3. Then, run the client scripts.

### 1. Start MCP Servers

Each MCP server runs independently:

```bash
uv run server/server_memory.py     # Memory server
uv run server/server_tasks.py      # Task manager
uv run server/server_calendar.py   # Calendar manager
```

### 2. Run Client Scripts

From the `client/` directory, choose a script based on your use case:

```bash
uv run client/01a_simple_client.py    # Basic task manager interaction
uv run client/01b_client.py           # Multi-server memory, task, calendar
uv run client/02_llm.py               # LLM-driven tool use with multiple MCP servers
uv run client/03_agents.py            # Full LangChain agent
```

## Assets

Additional resources such as screenshots or diagrams can be found in the assets/ directory (if provided).

## Tech Stack

| Component         | Tool / Library        |
|-------------------|-----------------------|
| LLM               | Ollama / OpenAI API   |
| Memory DB         | Qdrant                |
| Vector Interface  | Mem0                  |
| Agent Framework   | LangChain             |
| API Protocol      | FastMCP (SSE)         |
| Language          | Python 3.13+          |
| Dependency Mgmt   | uv                    |

## License

This project is licensed under the MIT License — feel free to use, modify, and distribute.

## Acknowledgements

Mem0

Qdrant

LangChain

FastMCP

Ollama
