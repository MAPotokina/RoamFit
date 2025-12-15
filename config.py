"""Configuration management for ROAMFIT."""
import os
import logging
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


def get_config() -> Dict[str, str]:
    """Load configuration from environment variables with defaults."""
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "DATABASE_PATH": os.getenv("DATABASE_PATH", "db/roamfit.db"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "LLM_MODEL": os.getenv("LLM_MODEL", "gpt-4"),
        "MAX_IMAGE_SIZE_MB": int(os.getenv("MAX_IMAGE_SIZE_MB", "10")),
    }


def setup_logging():
    """
    Set up centralized logging configuration.
    Logs to both file (logs/app.log) and console.
    """
    log_level = get_config()["LOG_LEVEL"]
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Prevent duplicate logs from other loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    return root_logger


# Initialize logging on import
setup_logging()

