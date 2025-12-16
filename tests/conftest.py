"""Shared fixtures for ROAMFIT tests."""
import os
import tempfile
from pathlib import Path

import pytest

from database import create_tables, get_db_connection


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    # Create temporary database file
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Set environment variable for database path
    original_db_path = os.environ.get("DATABASE_PATH")
    os.environ["DATABASE_PATH"] = db_path

    # Create tables
    create_tables()

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)

    # Restore original database path
    if original_db_path:
        os.environ["DATABASE_PATH"] = original_db_path
    elif "DATABASE_PATH" in os.environ:
        del os.environ["DATABASE_PATH"]


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""

    class MockUsage:
        def __init__(self):
            self.prompt_tokens = 10
            self.completion_tokens = 20
            self.total_tokens = 30

    class MockMessage:
        def __init__(self, content):
            self.content = content

    class MockChoice:
        def __init__(self, content):
            self.message = MockMessage(content)

    class MockResponse:
        def __init__(self, content="Test response"):
            self.choices = [MockChoice(content)]
            self.usage = MockUsage()

    return MockResponse
