import os
import pytest
from mcp.core.config import settings, DatabaseSettings, APISettings, SecuritySettings

def test_database_settings_defaults():
    """Test that DatabaseSettings loads default values correctly."""
    db_settings = DatabaseSettings()
    assert db_settings.DATABASE_URL == "sqlite:///./mcp_agent.db"
    assert db_settings.ENABLE_MIGRATIONS is True

def test_api_settings_defaults():
    """Test that APISettings loads default values correctly."""
    api_settings = APISettings()
    assert api_settings.GOOGLE_CALENDAR_CREDENTIALS is None
    assert api_settings.GOOGLE_CALENDAR_TOKEN is None

def test_security_settings_defaults():
    """Test that SecuritySettings loads default values correctly."""
    security_settings = SecuritySettings()
    assert security_settings.SECRET_KEY == "your-secret-key-here"
    assert security_settings.TOKEN_EXPIRE_MINUTES == 30

def test_settings_combines_all_configs():
    """Test that the main Settings class combines all configuration categories."""
    assert settings.db.DATABASE_URL == "sqlite:///./mcp_agent.db"
    assert settings.api.GOOGLE_CALENDAR_CREDENTIALS is None
    assert settings.security.SECRET_KEY == "your-secret-key-here"

def test_settings_respects_env_vars():
    """Test that settings respect environment variables."""
    # Set environment variables with the correct prefix
    os.environ["DB_DATABASE_URL"] = "postgresql://user:pass@localhost/db"
    os.environ["SECURITY_SECRET_KEY"] = "env-secret-key"
    os.environ["API_GOOGLE_CALENDAR_CREDENTIALS"] = "/path/to/credentials.json"
    
    # Create new instances to pick up environment variables
    db_settings = DatabaseSettings()
    security_settings = SecuritySettings()
    api_settings = APISettings()
    
    # Test the values
    assert db_settings.DATABASE_URL == "postgresql://user:pass@localhost/db"
    assert security_settings.SECRET_KEY == "env-secret-key"
    assert api_settings.GOOGLE_CALENDAR_CREDENTIALS == "/path/to/credentials.json"
    
    # Clean up environment variables
    del os.environ["DB_DATABASE_URL"]
    del os.environ["SECURITY_SECRET_KEY"]
    del os.environ["API_GOOGLE_CALENDAR_CREDENTIALS"] 