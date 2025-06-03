# MCP Agent

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

A modular, extensible agent framework for building AI-powered applications with specialized agents for memory, tasks, calendar, and web crawling.

## Overview

The MCP Agent is a multi-agent system where each agent specializes in a specific domain:

- **Memory Agent**: Manages long-term memory storage and retrieval using vector databases.
- **Tasks Agent**: Handles task management with priority and status tracking.
- **Calendar Agent**: Manages scheduling and time-based operations with Google Calendar integration.
- **Crawler Agent**: Performs web crawling and data extraction with metadata storage.

This framework uses FastMCP for server implementation, providing Server-Sent Events (SSE) for real-time communication and a RESTful API for tool execution.

## Project Structure

```plaintext
mcp-agent/
│
├── core/                # Core utilities and base classes
│   ├── utils/           # Utility modules (Starlette, memory)
│   ├── config.py        # Configuration management
│   ├── database.py      # Database connection and migrations
│   ├── models.py        # Database models
│   └── mcp_client.py    # MCP client implementation
│
├── agents/              # Agent implementations
│   ├── memory_agent.py  # Memory agent implementation
│   ├── tasks_agent.py   # Tasks agent implementation
│   ├── calendar_agent.py# Calendar agent implementation
│   └── crawler_agent.py # Crawler agent implementation
│
├── tools/               # Tool definitions for agents
│   ├── memory_tools.py  # Memory-related tools
│   ├── tasks_tools.py   # Task management tools
│   ├── calendar_tools.py# Calendar and scheduling tools
│   └── crawler_tools.py # Web crawling and data extraction tools
│
├── server/              # Server implementations (if separate from agents)
│
├── client/              # Client examples and utilities
│   └── 01a_simple_client.py  # Simple client example
│
├── tests/               # Test files
│
├── examples/            # Example usage and tutorials
│
├── assets/              # Static assets and documentation images
│
├── .env                 # Environment variables (not in version control)
├── .gitignore           # Git ignore file
├── pyproject.toml       # Project dependencies and configuration
├── uv.lock              # Dependency lock file
└── README.md            # Project documentation (this file)
```

## Installation

### Prerequisites

- Python 3.9 or higher
- Git (for cloning the repository)
- A virtual environment tool (recommended: `venv` or `virtualenv`)
- Mem0 API key for memory operations (get it from [Mem0](https://mem0.ai))
- Google Calendar API credentials (optional, for calendar integration)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Ishwanku/MCP_AGENT_1.git
   cd mcp-agent-poc
   ```

2. **Set Up a Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**

   Using `uv` (recommended for faster installation):

   ```bash
   pip install uv
   uv sync
   ```

   Or using standard pip:

   ```bash
   pip install -e .
   ```

4. **Configure Environment Variables**

   Copy the `.env.example` file to `.env` and update the values:

   ```bash
   cp .env.example .env
   # Edit .env to add your Mem0 API key and other configurations
   ```

   Key configurations:

   - `MEM0_API_KEY`: Your Mem0 API key for memory operations
   - `API_GOOGLE_CALENDAR_CREDENTIALS` and `API_GOOGLE_CALENDAR_TOKEN`: Paths to Google Calendar API credentials (if using calendar integration)
   - `SECURITY_SECRET_KEY`: A secure key for JWT token generation (change in production)

## Running the Agents

Each agent runs as a separate server on its own port. Start each agent server in a separate terminal window or as a background process.

### Start the Memory Agent

```bash
python -m agents.memory_agent
```

- Default port: 8030
- Handles memory storage and retrieval

### Start the Tasks Agent

```bash
python -m agents.tasks_agent
```

- Default port: 8010
- Manages task creation, updates, and status tracking

### Start the Calendar Agent

```bash
python -m agents.calendar_agent
```

- Default port: 8020
- Handles scheduling and calendar events

### Start the Crawler Agent

```bash
python -m agents.crawler_agent
```

- Default port: 3006
- Performs web crawling and data extraction

## Using the Client

You can interact with the agents using the provided client examples or build your own client.

Run a simple client example:

```bash
python client/01a_simple_client.py
```

## API Documentation

Each agent exposes two main endpoints:

1. **SSE Endpoint**: `/sse` - For real-time Server-Sent Events
2. **Tool Execution Endpoint**: `/tools/{tool_name}` - For executing specific tools (POST request)

### Authentication

API keys are used for authentication. Include the appropriate API key in the `X-API-Key` header for each request.

### Available Tools

- **Memory Agent**:
  - `store_information`: Store data in long-term memory
  - `retrieve_information`: Retrieve data from memory
  - `search_information`: Search memory with vector similarity

- **Tasks Agent**:
  - `create_task`: Create a new task
  - `update_task`: Update an existing task
  - `list_tasks`: List all tasks
  - `delete_task`: Delete a task

- **Calendar Agent**:
  - `create_event`: Create a new calendar event
  - `update_event`: Update an existing event
  - `list_events`: List calendar events
  - `delete_event`: Delete an event

- **Crawler Agent**:
  - `crawl_url`: Crawl a specified URL
  - `extract_content`: Extract content from crawled data
  - `save_data`: Save extracted data

## Development

### Running Tests

```bash
pytest
```

### Code Style

We follow PEP 8 for Python code. Use tools like `black` and `isort` for code formatting:

```bash
pip install black isort
black .
isort .
```

### Type Checking

We use `mypy` for static type checking:

```bash
pip install mypy
mypy .
```

## Troubleshooting

- **Agent Server Won't Start**: Check if the port is already in use. Update the port in `.env` if needed.
- **Connection Errors**: Ensure all agents are running and accessible at their configured host/port.
- **Mem0 API Key Issues**: Verify that your Mem0 API key is correctly set in the `.env` file.
- **Database Errors**: Check the database URL in `.env` and ensure the database file is writable.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with descriptive messages
4. Push your changes to your fork
5. Submit a pull request with a detailed description of your changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
