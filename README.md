# MCP Agent

A multi-agent system for AI-powered applications with specialized agents for memory, tasks, calendar, and web crawling.

## Overview

MCP Agent is a Python-based multi-agent system that provides specialized agents for different tasks:

- **Calendar Agent**: Manages calendar events and scheduling
- **Crawler Agent**: Handles web crawling and content extraction
- **Memory Agent**: Manages long-term memory storage and retrieval
- **Tasks Agent**: Handles task management and tracking

## Features

- FastAPI-based server implementation
- Asynchronous operation support
- Modular agent architecture
- Configurable server settings
- Environment variable support
- Comprehensive testing suite

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/mcp-agent.git
cd mcp-agent
```

2.Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3.Install the package in development mode:

```bash
pip install -e .
```

## Project Structure

```plaintext
mcp-agent/
├── src/
│   ├── mcp/                 # Main package
│   │   ├── agents/         # Agent implementations
│   │   │   ├── calendar_agent.py
│   │   │   ├── crawler_agent.py
│   │   │   ├── memory_agent.py
│   │   │   └── tasks_agent.py
│   │   ├── core/           # Core functionality
│   │   ├── utils/          # Utility functions
│   │   ├── server/         # Server implementation
│   │   └── client/         # Client implementation
│   ├── examples/           # Example scripts
│   │   ├── calendar_demo.py
│   │   ├── crawler_demo.py
│   │   └── memory_demo.py
│   └── tests/              # Test files
│       ├── test_agents/    # Agent tests
│       ├── test_core/      # Core functionality tests
│       ├── test_tools/     # Tool tests
│       ├── test_config.py  # Configuration tests
│       └── test_smoke.py   # Smoke tests
├── pyproject.toml          # Project configuration
├── setup.py               # Package installation
├── servers.yaml           # Server configuration
├── .python-version        # Python version specification
└── README.md             # This file
```

## Configuration

1. Create a `.env` file in the project root:

```env
# Server Configuration
CALENDAR_SERVER_PORT=8001
CALENDAR_SERVER_API_KEY=your_api_key

CRAWLER_SERVER_PORT=8002
CRAWLER_SERVER_API_KEY=your_api_key

MEMORY_SERVER_PORT=8003
MEMORY_SERVER_API_KEY=your_api_key

TASKS_SERVER_PORT=8004
TASKS_SERVER_API_KEY=your_api_key
```

2.Update `servers.yaml` with your server configurations.

## Usage

### Running Agents

Each agent can be run independently:

```bash
# Calendar Agent
python -m src.mcp.agents.calendar_agent

# Crawler Agent
python -m src.mcp.agents.crawler_agent

# Memory Agent
python -m src.mcp.agents.memory_agent

# Tasks Agent
python -m src.mcp.agents.tasks_agent
```

### Example Usage

```python
from mcp.core.mcp_client import MCPClient

# Initialize client
client = MCPClient()

# Calendar operations
events = client.get_events(start_date="2024-03-01", end_date="2024-03-31")

# Task operations
tasks = client.get_tasks(status="pending")
new_task = client.add_new_task(title="New Task", priority="high")

# Memory operations
client.save_memory(content="Important information")
memories = client.search_memories(query="information")

# Crawler operations
page_content = client.crawl_page(url="https://example.com")
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Acknowledgments

- FastAPI for the web framework
- Uvicorn for the ASGI server
- Pydantic for data validation
- SQLAlchemy for database operations
