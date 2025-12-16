"""MCP Client setup for ROAMFIT agents."""
import os
from pathlib import Path

from dotenv import load_dotenv
from mcp import StdioServerParameters, stdio_client
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient

# Load environment variables
load_dotenv()

# Get project root directory
project_root = Path(__file__).parent.parent

# Get OpenAI configuration
openai_api_key = os.getenv("OPENAI_API_KEY") or ""
openai_model_id = os.getenv("OPENAI_MODEL_ID", "gpt-4")
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

# Create LLM model for agents
llm_model = OpenAIModel(
    client_args={
        "api_key": openai_api_key,
    },
    model_id=openai_model_id,
    params={
        "temperature": openai_temperature,
    },
)

# MCP Client for Equipment Detection
equipment_detection_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python",
            args=["-m", "mcp_servers.equipment_detection"],
            env={
                **os.environ,
                "PYTHONPATH": str(project_root),
            },
        )
    )
)

# MCP Client for Workout Summary
workout_summary_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python",
            args=["-m", "mcp_servers.workout_summary"],
            env={
                **os.environ,
                "PYTHONPATH": str(project_root),
            },
        )
    )
)

# MCP Client for Workout Generator
workout_generator_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python",
            args=["-m", "mcp_servers.workout_generator"],
            env={
                **os.environ,
                "PYTHONPATH": str(project_root),
            },
        )
    )
)

# MCP Client for Graph/Trends
graph_trends_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python",
            args=["-m", "mcp_servers.graph_trends"],
            env={
                **os.environ,
                "PYTHONPATH": str(project_root),
            },
        )
    )
)

# MCP Client for Location Activity
location_activity_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python",
            args=["-m", "mcp_servers.location_activity"],
            env={
                **os.environ,
                "PYTHONPATH": str(project_root),
            },
        )
    )
)

# MCP Client for Workout Management
workout_management_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python",
            args=["-m", "mcp_servers.workout_management"],
            env={
                **os.environ,
                "PYTHONPATH": str(project_root),
            },
        )
    )
)
