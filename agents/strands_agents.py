"""Strands tool agents for ROAMFIT."""
from strands import Agent, tool
from agents.clients import (
    equipment_detection_client,
    workout_summary_client,
    workout_generator_client,
    graph_trends_client,
    location_activity_client,
    workout_management_client,
    llm_model
)
from agents.prompts import (
    EQUIPMENT_DETECTION_PROMPT,
    WORKOUT_SUMMARY_PROMPT,
    WORKOUT_GENERATOR_PROMPT,
    GRAPH_TRENDS_PROMPT,
    LOCATION_ACTIVITY_PROMPT,
    WORKOUT_MANAGEMENT_PROMPT,
)


@tool
def equipment_detection_agent(query: str) -> str:
    """
    Detect fitness equipment from images or descriptions.
    
    Example queries:
    - "Detect equipment from this image"
    - "What equipment is in this photo?"
    
    Note: If query mentions "uploaded image", you should use the detect_equipment_tool.
    However, since we can't pass the image directly through Strands, this agent
    will need to be called with the image data separately or the image should be
    passed through the query in a way that doesn't exceed token limits.
    """
    with equipment_detection_client:
        tools = equipment_detection_client.list_tools_sync()
        
        agent = Agent(
            system_prompt=EQUIPMENT_DETECTION_PROMPT,
            tools=tools,
            model=llm_model,
        )
        
        # Clean query - remove any base64 data URIs to reduce token usage
        clean_query = query
        if "data:image" in query:
            # Remove the long base64 string to avoid rate limits
            parts = query.split("data:image")
            if len(parts) > 1:
                # Keep everything before "data:image" and after the base64
                before = parts[0]
                # Find where the base64 ends (usually at a space or end of string)
                after_part = parts[1]
                # Try to find the end of base64 (look for space or newline)
                base64_end = after_part.find(" ")
                if base64_end == -1:
                    base64_end = after_part.find("\n")
                if base64_end == -1:
                    base64_end = len(after_part)
                after = after_part[base64_end:].strip()
                clean_query = before + "the uploaded image " + after
        
        response = agent(clean_query)
        return str(response)


@tool
def workout_summary_agent(query: str) -> str:
    """
    Retrieve and summarize workout history.
    
    Example queries:
    - "What was my last workout?"
    - "Summarize my workout history"
    - "How many workouts have I done?"
    """
    with workout_summary_client:
        tools = workout_summary_client.list_tools_sync()
        
        agent = Agent(
            system_prompt=WORKOUT_SUMMARY_PROMPT,
            tools=tools,
            model=llm_model,
        )
        
        response = agent(query)
        return str(response)


@tool
def workout_generator_agent(query: str) -> str:
    """
    Generate personalized workout plans.
    
    Example queries:
    - "Generate a workout with dumbbells and bench"
    - "Create a workout plan for the equipment: [list]"
    """
    with workout_generator_client:
        tools = workout_generator_client.list_tools_sync()
        
        agent = Agent(
            system_prompt=WORKOUT_GENERATOR_PROMPT,
            tools=tools,
            model=llm_model,
        )
        
        response = agent(query)
        return str(response)


@tool
def graph_trends_agent(query: str) -> str:
    """
    Get workout statistics and progress charts.
    
    Example queries:
    - "Show my workout statistics"
    - "Generate a frequency chart"
    - "What's my workout progress?"
    
    Returns statistics and a reference to chart data (to avoid context overflow).
    """
    import json
    from agents.graph_trends import get_workout_stats, generate_charts
    
    # Check if query asks for charts
    wants_charts = any(word in query.lower() for word in ["chart", "visual", "graph", "progress", "trend"])
    
    # Get stats first (always useful)
    stats = get_workout_stats()
    stats_text = f"""Workout Statistics:
- Total Workouts: {stats.get('total_workouts', 0)}
- Completed: {stats.get('completed_workouts', 0)}
- Recent (30 days): {stats.get('recent_workouts_30_days', 0)}
- Workouts per Week: {stats.get('workouts_per_week', 0)}
- Completion Rate: {stats.get('completion_rate', 0)}%
"""
    
    # If charts are requested, generate them but return a reference (not the full base64)
    if wants_charts:
        # Determine chart type from query
        chart_type = "equipment" if "equipment" in query.lower() else "frequency"
        
        # Generate chart directly and store reference
        chart_data = generate_charts(chart_type=chart_type)
        
        # Return a reference marker that the UI can detect and fetch the chart
        # Use a special marker to indicate chart is available without including base64
        return json.dumps({
            "text": stats_text + f"\nGenerated {chart_type} chart. [CHART:{chart_type}]",
            "chart_type": chart_type,
            "has_chart": True
        })
    else:
        # Just return stats without charts
        return stats_text


@tool
def location_activity_agent(query: str) -> str:
    """
    Find nearby gyms and running tracks.
    
    Example queries:
    - "Find gyms near New York, NY"
    - "Where are the running tracks near San Francisco?"
    - "Show me nearby fitness locations"
    """
    with location_activity_client:
        tools = location_activity_client.list_tools_sync()
        
        agent = Agent(
            system_prompt=LOCATION_ACTIVITY_PROMPT,
            tools=tools,
            model=llm_model,
        )
        
        response = agent(query)
        return str(response)


@tool
def workout_management_agent(query: str) -> str:
    """
    Manage workouts: list, view, edit, delete, and mark as complete.
    
    Example queries:
    - "List my workouts"
    - "Show me workout #5"
    - "Delete workout #3"
    - "Edit workout #2 to add location"
    - "Mark workout #1 as completed"
    """
    with workout_management_client:
        tools = workout_management_client.list_tools_sync()
        
        agent = Agent(
            system_prompt=WORKOUT_MANAGEMENT_PROMPT,
            tools=tools,
            model=llm_model,
        )
        
        response = agent(query)
        return str(response)

