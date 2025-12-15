# Strands Integration Task List

## Decisions Made

1. **Agent Architecture**: ✅ Convert ALL agents to MCP-based and Strands tool agents
2. **Equipment Detection**: ✅ Interactive chat with photo upload capability
3. **Orchestrator**: ✅ Replace current `generate_workout_flow()` with Strands orchestrator
4. **MCP Servers**: ✅ Use FastMCP with separate processes (stdio) - standard MCP pattern
5. **System Prompts**: ✅ Each agent gets its own system prompt
6. **Backward Compatibility**: ✅ No - update API endpoints to use Strands orchestrator

---

## Implementation Plan

### Phase 1: MCP Server Creation (FastMCP)
- [x] Create `agents/equipment_detection_mcp.py` - FastMCP server for equipment detection
  - Tool: `detect_equipment(image_base64, location)` - accepts base64 image
- [x] Create `agents/workout_summary_mcp.py` - FastMCP server for workout history
  - Tools: `get_last_workout()`, `summarize_workout_history(limit)`
- [x] Create `agents/workout_generator_mcp.py` - FastMCP server for workout generation
  - Tool: `generate_workout(equipment, workout_history)`
- [x] Convert `agents/graph_trends.py` to FastMCP server
  - Tools: `get_workout_stats()`, `generate_charts(chart_type)`
- [x] Convert `agents/location_activity.py` to FastMCP server
  - Tools: `find_nearby_gyms(location, radius_km, limit)`, `find_running_tracks(...)`
- [ ] Test all MCP servers independently (run as stdio processes)

### Phase 2: MCP Client Setup
- [x] Create `agents/clients.py` with MCPClient setup for all servers
- [x] Set up MCPClient for equipment_detection_mcp
- [x] Set up MCPClient for workout_summary_mcp
- [x] Set up MCPClient for workout_generator_mcp
- [x] Set up MCPClient for graph_trends_mcp
- [x] Set up MCPClient for location_activity_mcp
- [ ] Test all MCP client connections

### Phase 3: System Prompts & Tool Agents
- [x] Create `agents/prompts.py` with system prompts:
  - `EQUIPMENT_DETECTION_PROMPT`
  - `WORKOUT_SUMMARY_PROMPT`
  - `WORKOUT_GENERATOR_PROMPT`
  - `GRAPH_TRENDS_PROMPT`
  - `LOCATION_ACTIVITY_PROMPT`
  - `ORCHESTRATOR_PROMPT`
- [x] Create `agents/strands_agents.py` with tool agents:
  - `equipment_detection_agent(query)` - uses equipment_detection MCP client
  - `workout_summary_agent(query)` - uses workout_summary MCP client
  - `workout_generator_agent(query)` - uses workout_generator MCP client
  - `graph_trends_agent(query)` - uses graph_trends MCP client
  - `location_activity_agent(query)` - uses location_activity MCP client
- [x] Each tool agent uses `@tool` decorator and creates Agent with MCP tools

### Phase 4: Strands Orchestrator
- [x] Create `agents/strands_orchestrator.py`
- [x] Implement `create_roamfit_orchestrator()` function
- [x] Register all 5 tool agents as tools
- [x] Write comprehensive orchestrator system prompt
- [x] Replace `generate_workout_flow()` with orchestrator-based approach
- [ ] Test orchestrator with various requests

### Phase 5: Interactive Chat Interface
- [x] Update to use Streamlit chat interface (replaced old `main.py` with Strands version)
- [x] Add chat message history
- [x] Add file uploader for photos in chat
- [x] Connect chat to Strands orchestrator
- [x] Handle image uploads (convert to base64 for MCP)
- [x] Display orchestrator responses in chat
- [x] Add clear conversation flow

### Phase 6: API Integration
- [x] Update to use Strands orchestrator (replaced old `api.py` with Strands version)
- [x] Replace `/generate-workout` endpoint to use orchestrator
- [x] Update other endpoints as needed
- [x] Add chat endpoint `/chat` for interactive conversations
- [x] Handle image uploads in API
- [ ] Test all API endpoints

### Phase 7: Testing & Polish
- [ ] Test complete chat workflow with photo upload
- [ ] Test all agent interactions via orchestrator
- [ ] Verify MCP server communication
- [ ] Test error handling in chat interface
- [ ] Update README with Strands usage and chat interface
- [ ] Update TESTING.md with new workflow

---

## Implementation Details

### MCP Server Structure (FastMCP with stdio)
```python
# agents/equipment_detection_mcp.py
import sys
from mcp.server.fastmcp import FastMCP
from agents.equipment_detection import detect_equipment
import base64
import tempfile

mcp = FastMCP("equipment_detection")

@mcp.tool()
async def detect_equipment_tool(image_base64: str, location: str = None) -> Dict[str, Any]:
    """Detect equipment from base64 encoded image."""
    # Decode image, save to temp file, call detect_equipment, return result

def main():
    print("Starting Equipment Detection MCP server...", file=sys.stderr)
    mcp.run()

if __name__ == "__main__":
    main()
```

### MCP Client Setup
```python
# agents/clients.py
from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient

equipment_detection_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python",
            args=["agents/equipment_detection_mcp.py"],
        )
    )
)
# Similar for other clients...
```

### Tool Agent Structure
```python
# agents/strands_agents.py
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from agents.clients import equipment_detection_client, ...
from agents.prompts import EQUIPMENT_DETECTION_PROMPT, ...

@tool
def equipment_detection_agent(query: str) -> str:
    """Detect equipment from image or description."""
    with equipment_detection_client:
        tools = equipment_detection_client.list_tools_sync()
        agent = Agent(
            system_prompt=EQUIPMENT_DETECTION_PROMPT,
            tools=tools,
            model=llm_model
        )
        return str(agent(query))
```

### Orchestrator Structure
```python
# agents/strands_orchestrator.py
from strands import Agent
from agents.strands_agents import (
    equipment_detection_agent,
    workout_summary_agent,
    workout_generator_agent,
    graph_trends_agent,
    location_activity_agent
)
from agents.prompts import ORCHESTRATOR_PROMPT

def create_roamfit_orchestrator():
    orchestrator = Agent(
        system_prompt=ORCHESTRATOR_PROMPT,
        tools=[
            equipment_detection_agent,
            workout_summary_agent,
            workout_generator_agent,
            graph_trends_agent,
            location_activity_agent
        ],
        model=llm_model
    )
    return orchestrator
```

### Interactive Chat Interface
```python
# main.py - Chat interface
import streamlit as st
from agents.strands_orchestrator import create_roamfit_orchestrator
import base64

orchestrator = create_roamfit_orchestrator()

# Chat interface
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

if prompt := st.chat_input("Ask about workouts..."):
    # Handle image upload if present
    if uploaded_file:
        image_base64 = base64.b64encode(uploaded_file.read()).decode()
        prompt = f"Image uploaded. {prompt}"
    
    # Call orchestrator
    response = orchestrator(prompt)
    st.chat_message("assistant").write(response)
```

---

## Files to Create/Modify

### New Files:
- `agents/clients.py` - MCP client setup for all servers
- `agents/prompts.py` - System prompts for all agents
- `agents/strands_agents.py` - Tool agents with @tool decorator
- `agents/strands_orchestrator.py` - Strands orchestrator
- `agents/equipment_detection_mcp.py` - FastMCP server
- `agents/workout_summary_mcp.py` - FastMCP server
- `agents/workout_generator_mcp.py` - FastMCP server
- `agents/graph_trends_mcp.py` - FastMCP server (convert from existing)
- `agents/location_activity_mcp.py` - FastMCP server (convert from existing)

### Files to Modify:
- `agents/orchestrator.py` - Replace with Strands orchestrator
- `api.py` - FastAPI with Strands orchestrator, `/chat` endpoint
- `main.py` - Interactive chat interface with photo upload
- `requirements.txt` - Add any missing Strands/MCP dependencies
- `README.md` - Update with Strands usage and chat interface
- `TESTING.md` - Update with new workflow

### Files to Keep (for reference/fallback):
- `agents/equipment_detection.py` - Keep functions, MCP server will use them
- `agents/workout_summary.py` - Keep functions, MCP server will use them
- `agents/workout_generator.py` - Keep functions, MCP server will use them
- `agents/graph_trends.py` - Keep functions, MCP server will use them
- `agents/location_activity.py` - Keep functions, MCP server will use them

---

## Implementation Order

1. **Phase 1**: Create all MCP servers (FastMCP with stdio)
2. **Phase 2**: Set up MCP clients
3. **Phase 3**: Create system prompts and tool agents
4. **Phase 4**: Build Strands orchestrator
5. **Phase 5**: Create interactive chat interface
6. **Phase 6**: Update API endpoints
7. **Phase 7**: Test and polish

---

## Key Considerations

- **Image Handling**: Convert uploaded images to base64 for MCP tools
- **Chat Interface**: Use Streamlit chat components for interactive experience
- **Error Handling**: Graceful degradation if MCP servers fail
- **Testing**: Test each MCP server independently before integration
- **KISS Principle**: Keep implementation simple, follow demo patterns

## Dependencies

Check if we need:
- `fastmcp` package (or is it part of `mcp`?)
- Any additional Strands dependencies
- Update `requirements.txt` accordingly

