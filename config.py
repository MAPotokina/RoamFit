"""Configuration management for ROAMFIT."""
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


def get_config() -> Dict[str, str]:
    """Load configuration from environment variables with defaults."""
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "DATABASE_PATH": os.getenv("DATABASE_PATH", "db/roamfit.db"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "LLM_MODEL": os.getenv("LLM_MODEL", "gpt-4"),
    }

