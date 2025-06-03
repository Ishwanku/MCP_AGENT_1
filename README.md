# 🧠 MCP Agent with Mem0 and Task/Calendar Integration

A Model Context Protocol (MCP) Agent that integrates with multiple MCP servers to provide AI agents with long-term memory, task management, calendar event capabilities, and web crawling functionality. This project uses Mem0, Qdrant, and FastMCP to deliver an intelligent and extensible agent system.

## 📁 Project Structure

```plaintext
.
├── client/                     # Client-side code
│   ├── agents/                # LangChain agent implementations
│   ├── utils/                 # Client utility functions
│   ├── 01a_simple_client.py   # Basic task manager interaction
│   ├── 01b_client.py         # Multi-server memory, task, calendar
│   ├── 02_llm.py             # LLM-driven tool use
│   ├── 03_agents.py          # Full LangChain agent
│   ├── chat_client.py        # Chat interface implementation
│   ├── llm_client.py         # LLM client implementation
│   ├── sse_client.py         # Server-Sent Events client
│   └── tool_discovery.py     # Tool discovery utilities
├── server/                    # Server-side code
│   ├── tools/                # Server utility tools
│   │   └── crawler_tools.py  # Web crawling tools implementation
│   ├── utils/                # Server utility functions
│   ├── server_memory.py      # Memory management server
│   ├── server_tasks.py       # Task management server
│   ├── server_calendar.py    # Calendar management server
│   └── crawler_server.py     # Web crawler server
├── tasks/                    # Task-related data and utilities
├── assets/                   # Project assets and resources
├── qdrant_db/               # Qdrant vector database storage
├── .env                     # Environment variables (create from .env.example)
├── servers.yaml             # Server configurations
├── pyproject.toml           # Project dependencies
└── README.md               # This file
```

## 🚀 Core Components

### Server Components

1. **Memory Server** (`server/server_memory.py`)
   - Manages long-term memory using Mem0 and Qdrant
   - Tools: `save_memory`, `search_memories`, `get_all_memories`
   - Runs on port 8030 by default

2. **Task Server** (`server/server_tasks.py`)
   - Handles task management operations
   - Tools: `get_tasks`, `add_new_task`, `complete_task`
   - Runs on port 8010 by default

3. **Calendar Server** (`server/server_calendar.py`)
   - Manages calendar events
   - Tool: `get_events`
   - Runs on port 8020 by default

4. **Crawler Server** (`server/crawler_server.py`)
   - Provides web crawling capabilities
   - Tools:
     - `crawl_page`: Extract content from a single webpage
     - `crawl_site`: Recursively crawl a website
     - `search_page`: Search for text within a webpage
   - Runs on port 3005 by default
   - Stores results in `crawler_data.json`

### Client Components

1. **Simple Client** (`client/01a_simple_client.py`)
   - Basic task manager interaction
   - Demonstrates direct MCP server communication

2. **Multi-Server Client** (`client/01b_client.py`)
   - Interacts with all MCP servers
   - Shows memory, task, calendar, and crawler integration

3. **LLM Client** (`client/02_llm.py`)
   - Implements LLM-driven tool use
   - Uses OpenAI-compatible API for intent classification

4. **LangChain Agent** (`client/03_agents.py`)
   - Full agent implementation using LangChain
   - Integrates all tools and capabilities

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.13+
- `uv` package manager
- OpenAI API key or compatible local API (e.g., Ollama)
- Qdrant running locally
- Git
- Additional dependencies for web crawling:
  - `aiohttp`
  - `beautifulsoup4`

### Environment Setup

1. **Install Dependencies**

   ```bash
   uv sync
   ```

2. **Configure Environment**

   Create a `.env` file with:

   ```env
   # For Ollama (local LLM)
   MODEL="qwen2:7b-instruct"
   OPENAI_API_KEY="ollama"
   OPENAI_BASE_URL="http://localhost:11434/v1"
   OLLAMA_BASE_URL="http://localhost:11434/v1"

   # For OpenAI API
   MODEL="gpt-4o-mini"
   OPENAI_API_KEY="your-api-key"
   ```

3. **Start Qdrant**

   ```bash
   docker run -p 6333:6333 -v "$(pwd)/qdrant_db":/qdrant/storage qdrant/qdrant
   ```

## 🏃‍♂️ Running the Project

1. **Start MCP Servers**

   ```bash
   uv run server/server_memory.py
   uv run server/server_tasks.py
   uv run server/server_calendar.py
   uv run server/crawler_server.py
   ```

2. **Run Client Scripts**

   ```bash
   # Basic task manager
   uv run client/01a_simple_client.py

   # Multi-server client
   uv run client/01b_client.py

   # LLM-driven client
   uv run client/02_llm.py

   # Full LangChain agent
   uv run client/03_agents.py
   ```

## 🔧 Technical Details

### Server Architecture

- Each server runs independently using FastMCP
- Servers communicate via Server-Sent Events (SSE)
- Authentication using API keys
- Environment-based configuration

### Client Architecture

- Modular design with separate components
- SSE client for real-time communication
- LLM integration for intelligent responses
- LangChain for agent orchestration

### Memory System

- Mem0 for memory management
- Qdrant for vector storage
- Semantic search capabilities
- User-based memory isolation

### Task System

- JSON-based task storage
- CRUD operations for tasks
- User-based task isolation
- Task completion tracking

### Calendar System

- YAML-based event storage
- Event retrieval capabilities
- Extensible for calendar API integration

### Crawler System

- Web page content extraction
- Recursive site crawling
- Text search within pages
- JSON-based result storage
- Rate limiting and depth control
- BeautifulSoup for HTML parsing

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgements

- Mem0
- Qdrant
- LangChain
- FastMCP
- Ollama
- BeautifulSoup4
- aiohttp
