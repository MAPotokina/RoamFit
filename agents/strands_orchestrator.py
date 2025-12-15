"""Strands Orchestrator for ROAMFIT."""
from strands import Agent
from agents.strands_agents import (
    equipment_detection_agent,
    workout_summary_agent,
    workout_generator_agent,
    graph_trends_agent,
    location_activity_agent,
    workout_management_agent,
)
from agents.prompts import ORCHESTRATOR_PROMPT
from agents.clients import llm_model


def create_roamfit_orchestrator():
    """
    Create the main orchestrator agent for ROAMFIT.
    
    The orchestrator uses LLM-based decision making to choose which agents to call.
    The prompt guides it to only call necessary agents based on the query.
    """
    orchestrator = Agent(
        system_prompt=ORCHESTRATOR_PROMPT,
        tools=[
            equipment_detection_agent,
            workout_summary_agent,
            workout_generator_agent,
            graph_trends_agent,
            location_activity_agent,
            workout_management_agent,
        ],
        model=llm_model,
    )
    
    return orchestrator

