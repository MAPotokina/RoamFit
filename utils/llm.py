"""LLM utility functions for ROAMFIT."""
import time
import base64
import logging
from pathlib import Path
from typing import Optional
from openai import OpenAI
from config import get_config
from database import save_llm_log

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "llm_calls.log"

logger = logging.getLogger("llm_calls")
logger.setLevel(logging.INFO)

# Custom formatter to handle extra fields
class LLMLogFormatter(logging.Formatter):
    def format(self, record):
        agent = getattr(record, 'agent', 'unknown')
        model = getattr(record, 'model', 'unknown')
        status = getattr(record, 'status', 'UNKNOWN')
        tokens_in = getattr(record, 'tokens_in', 0)
        tokens_out = getattr(record, 'tokens_out', 0)
        time_ms = getattr(record, 'time_ms', 0)
        
        return (
            f"[{self.formatTime(record)}] [{agent}] [{model}] [{status}] "
            f"[tokens: {tokens_in}+{tokens_out}] [{time_ms}ms] - {record.getMessage()}"
        )

handler = logging.FileHandler(log_file)
formatter = LLMLogFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)


def call_llm(
    prompt: str,
    model: str = "gpt-4",
    agent_name: str = "unknown"
) -> str:
    """Call LLM with prompt. Returns response text."""
    config = get_config()
    api_key = config["OPENAI_API_KEY"]
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in configuration")
    
    client = OpenAI(api_key=api_key)
    start_time = time.time()
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        
        response_time = int((time.time() - start_time) * 1000)
        tokens_in = response.usage.prompt_tokens if response.usage else 0
        tokens_out = response.usage.completion_tokens if response.usage else 0
        response_text = response.choices[0].message.content or ""
        
        logger.info(
            "LLM call successful",
            extra={
                "agent": agent_name,
                "model": model,
                "status": "SUCCESS",
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "time_ms": response_time,
            }
        )
        
        # Log to database
        try:
            save_llm_log(
                agent_name=agent_name,
                model=model,
                status="SUCCESS",
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                time_ms=response_time,
            )
        except Exception as db_error:
            # Don't fail if database logging fails
            logger.warning(f"Failed to log to database: {db_error}")
        
        return response_text
        
    except Exception as e:
        response_time = int((time.time() - start_time) * 1000)
        error_msg = str(e)
        
        logger.error(
            f"LLM call failed: {error_msg}",
            extra={
                "agent": agent_name,
                "model": model,
                "status": "FAILED",
                "tokens_in": 0,
                "tokens_out": 0,
                "time_ms": response_time,
            }
        )
        
        # Log to database
        try:
            save_llm_log(
                agent_name=agent_name,
                model=model,
                status="FAILED",
                tokens_in=0,
                tokens_out=0,
                time_ms=response_time,
                error_message=error_msg,
            )
        except Exception as db_error:
            # Don't fail if database logging fails
            logger.warning(f"Failed to log to database: {db_error}")
        
        raise


def call_vision(
    image_path: str,
    prompt: str,
    model: str = "gpt-4o",
    agent_name: str = "unknown"
) -> str:
    """Call vision API with image. Returns response text."""
    config = get_config()
    api_key = config["OPENAI_API_KEY"]
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in configuration")
    
    client = OpenAI(api_key=api_key)
    start_time = time.time()
    
    try:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ],
                }
            ],
        )
        
        response_time = int((time.time() - start_time) * 1000)
        tokens_in = response.usage.prompt_tokens if response.usage else 0
        tokens_out = response.usage.completion_tokens if response.usage else 0
        response_text = response.choices[0].message.content or ""
        
        logger.info(
            "Vision call successful",
            extra={
                "agent": agent_name,
                "model": model,
                "status": "SUCCESS",
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "time_ms": response_time,
            }
        )
        
        # Log to database
        try:
            save_llm_log(
                agent_name=agent_name,
                model=model,
                status="SUCCESS",
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                time_ms=response_time,
            )
        except Exception as db_error:
            # Don't fail if database logging fails
            logger.warning(f"Failed to log to database: {db_error}")
        
        return response_text
        
    except Exception as e:
        response_time = int((time.time() - start_time) * 1000)
        error_msg = str(e)
        
        logger.error(
            f"Vision call failed: {error_msg}",
            extra={
                "agent": agent_name,
                "model": model,
                "status": "FAILED",
                "tokens_in": 0,
                "tokens_out": 0,
                "time_ms": response_time,
            }
        )
        
        # Log to database
        try:
            save_llm_log(
                agent_name=agent_name,
                model=model,
                status="FAILED",
                tokens_in=0,
                tokens_out=0,
                time_ms=response_time,
                error_message=error_msg,
            )
        except Exception as db_error:
            # Don't fail if database logging fails
            logger.warning(f"Failed to log to database: {db_error}")
        
        raise

