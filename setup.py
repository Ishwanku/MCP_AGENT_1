from setuptools import setup, find_packages

setup(
    name="mcp-agent",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.92.0",
        "uvicorn>=0.20.0",
        "starlette>=0.25.0",
        "httpx>=0.23.3",
        "sseclient-py>=1.8.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.9.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "psycopg2-binary>=2.9.5",
        "requests>=2.28.2",
        "beautifulsoup4>=4.11.2",
        "aiohttp>=3.8.3",
        "google-auth>=2.27.0",
        "google-auth-oauthlib>=1.2.0",
        "google-auth-httplib2>=0.2.0",
        "google-api-python-client>=2.118.0",
        "qdrant-client>=1.7.0",
        "sentence-transformers>=2.5.1",
        "python-multipart>=0.0.9",
        # LLM-related dependencies
        "httpx>=0.24.0",  # For Ollama API calls
        "numpy>=1.24.0",
        "scikit-learn>=1.0.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "vllm>=0.2.0"
    ],
    python_requires=">=3.9",
) 