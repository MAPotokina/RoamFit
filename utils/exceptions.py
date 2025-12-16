"""Centralized exception handling for ROAMFIT."""
import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ROAMFITException(Exception):
    """Base exception for ROAMFIT."""

    def __init__(
        self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ROAMFITException):
    """Input validation error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class AgentError(ROAMFITException):
    """Agent execution error."""

    def __init__(self, message: str, agent_name: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["agent"] = agent_name
        super().__init__(message, status_code=500, details=details)


class DatabaseError(ROAMFITException):
    """Database operation error."""

    def __init__(self, message: str, operation: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["operation"] = operation
        super().__init__(message, status_code=500, details=details)


def handle_exception(e: Exception, context: Optional[str] = None) -> JSONResponse:
    """
    Centralized exception handler.
    Translates exceptions into standardized JSON error responses.
    """
    logger.error(
        f"Exception in {context or 'unknown context'}: {type(e).__name__}: {str(e)}", exc_info=True
    )

    if isinstance(e, ROAMFITException):
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {"type": type(e).__name__, "message": e.message, "details": e.details}
            },
        )
    elif isinstance(e, HTTPException):
        return JSONResponse(
            status_code=e.status_code,
            content={"error": {"type": "HTTPException", "message": e.detail, "details": {}}},
        )
    else:
        # Generic exception
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "details": {"error_type": type(e).__name__, "error_message": str(e)},
                }
            },
        )


def safe_agent_call(agent_func, query: str, agent_name: str):
    """
    Safely call an agent with error handling.
    Returns (success: bool, response: str, error: Optional[Exception])
    """
    try:
        logger.info(f"Calling agent: {agent_name} with query: {query[:100]}...")
        response = agent_func(query)
        logger.info(f"Agent {agent_name} completed successfully")
        return True, str(response), None
    except Exception as e:
        logger.error(f"Agent {agent_name} failed: {str(e)}", exc_info=True)
        return (
            False,
            "",
            AgentError(
                message=f"Agent {agent_name} failed: {str(e)}",
                agent_name=agent_name,
                details={"original_error": str(e)},
            ),
        )
