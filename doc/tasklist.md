# ROAMFIT - Development Task List

## Progress Report

| Iteration | Status | Description | Test Status |
|-----------|--------|-------------|-------------|
| 1. Project Setup | ✅ Complete | Project structure, dependencies, config | ✅ Passed |
| 2. Database Foundation | ✅ Complete | SQLite schema and basic operations | ✅ Passed |
| 3. LLM Utilities | ✅ Complete | LLM wrapper functions with logging | ✅ Passed |
| 4. Workout Summary Agent | ✅ Complete | First agent - tracks workout history | ✅ Passed |
| 5. Equipment Detection Agent | ✅ Complete | Vision-based equipment detection | ✅ Passed |
| 6. Workout Generator Agent | ✅ Complete | Generates workouts from equipment/history | ✅ Passed |
| 7. Orchestrator Agent | ✅ Complete | Coordinates agents using Strands | ✅ Passed |
| 8. API Layer | ✅ Complete | FastAPI endpoints | ✅ Passed |
| 9. UI Layer | ✅ Complete | Streamlit interface | ✅ Passed |
| 10. Graph/Trends Agent | ✅ Complete | Progress visualization | ✅ Passed |
| 11. Location Agent | ✅ Complete | Nearby gyms and tracks | ✅ Passed |
| 12. Integration & Polish | ⏳ Not Started | End-to-end testing and refinements | - |

**Legend**: ✅ Complete | 🚧 In Progress | ⏳ Not Started | ❌ Blocked

---

## Iteration 1: Project Setup

**Goal**: Create project structure and basic configuration

- [x] Create project directory structure (agents/, models/, utils/, db/, logs/)
- [x] Create `requirements.txt` with dependencies (strands, fastapi, streamlit, sqlite3, pillow, openai, python-dotenv)
- [x] Create `config.py` with environment variable loading
- [x] Create `.env.example` template
- [x] Create `README.md` with setup instructions
- [x] Initialize git repository and `.gitignore`
- [x] Test: Verify project structure and config loading

**Test**: Run `python -c "from config import get_config; print(get_config())"` - should load without errors

---

## Iteration 2: Database Foundation

**Goal**: Set up SQLite database with schema

- [x] Create `database.py` with database initialization
- [x] Implement `create_tables()` for workouts, equipment_detections, user_preferences
- [x] Create basic CRUD functions: `save_workout()`, `get_last_workout()`, `save_equipment_detection()`
- [x] Add database connection management (context managers)
- [x] Test: Create database, insert sample data, query it

**Test**: Run database operations manually - insert workout, retrieve it, verify data integrity

---

## Iteration 3: LLM Utilities

**Goal**: Create LLM wrapper functions with logging

- [x] Create `utils/llm.py` with `call_llm()` function
- [x] Create `call_vision()` function for image analysis
- [x] Implement logging to `logs/llm_calls.log` (timestamp, model, tokens, success)
- [x] Add error handling with single retry
- [x] Test: Make test LLM call, verify logging, check response format

**Test**: Call `call_llm("Say hello")` - verify response and log entry created

---

## Iteration 4: Workout Summary Agent

**Goal**: First working agent - retrieves and summarizes workout history

- [x] Create `agents/workout_summary.py`
- [x] Implement `get_last_workout()` - queries database
- [x] Implement `summarize_workout_history()` - uses LLM to create summary
- [x] Return structured data (dict with summary text)
- [x] Test: Save sample workouts, call agent, verify summary generation

**Test**: Create 2-3 sample workouts in DB, call agent, verify it returns workout history summary

---

## Iteration 5: Equipment Detection Agent

**Goal**: Detect equipment from photos using vision API

- [x] Create `agents/equipment_detection.py`
- [x] Implement `detect_equipment(image_path)` - uses `call_vision()`
- [x] Parse LLM response to extract equipment list (JSON)
- [x] Save detection to database
- [x] Test: Upload test image, verify equipment detection, check database entry

**Test**: Upload gym photo, verify agent returns list of detected equipment, check DB entry

---

## Iteration 6: Workout Generator Agent

**Goal**: Generate workout plans based on equipment and history

- [x] Create `agents/workout_generator.py`
- [x] Implement `generate_workout(equipment, workout_history)` - uses LLM
- [x] Request structured JSON response (exercises, sets, reps, duration)
- [x] Return workout plan as dict
- [x] Test: Pass equipment list and history, verify workout plan generation

**Test**: Call with equipment=["dumbbells", "bench"] and history, verify structured workout plan

---

## Iteration 7: Orchestrator Agent

**Goal**: Coordinate all agents using Strands framework

- [x] Create `agents/orchestrator.py`
- [x] Set up orchestrator agent (simple coordination pattern)
- [x] Register simple function agents (workout_summary, equipment_detection, workout_generator)
- [ ] Register MCP servers (location_activity, graph_trends) - embedded, explicit registration (iterations 10-11)
- [x] Implement `generate_workout_flow()` - coordinates equipment detection → summary → generator
- [x] Handle errors and return unified response
- [x] Test: End-to-end flow - photo → equipment → history → workout plan

**Test**: Full workflow: upload photo, orchestrator calls all agents (functions + MCP), returns complete workout plan

---

## Iteration 8: API Layer

**Goal**: Create FastAPI endpoints for agent interactions

- [x] Create `api.py` with FastAPI app
- [x] Implement `/generate-workout` endpoint (accepts image or equipment list)
- [x] Implement `/detect-equipment` endpoint
- [x] Implement `/workout-history` endpoint
- [x] Add error handling and response models
- [x] Test: Use curl/Postman to test all endpoints

**Test**: POST to `/generate-workout` with image, verify JSON response with workout plan

---

## Iteration 9: UI Layer

**Goal**: Create Streamlit interface for user interaction

- [x] Create `main.py` with Streamlit app
- [x] Add file uploader for equipment photos
- [x] Add button to generate workout
- [x] Display workout plan in formatted way
- [x] Add section to view workout history
- [x] Connect UI to FastAPI endpoints
- [x] Test: Run `streamlit run main.py`, test all UI interactions

**Test**: Launch app, upload photo, generate workout, verify display and functionality

---

## Iteration 10: Graph/Trends Agent

**Goal**: Visualize workout progress (MCP Server)

- [x] Create `agents/graph_trends.py` as MCP server
- [x] Implement MCP tools: `get_workout_stats()`, `generate_charts()`
- [x] Queries database for statistics
- [x] Generate simple charts (matplotlib) - workout frequency, equipment usage
- [x] Return chart data as base64 encoded images
- [ ] Register MCP server in orchestrator (will be done in integration)
- [x] Add endpoint `/progress` to API
- [x] Add progress view to Streamlit UI
- [x] Test: Generate charts from workout data, display in UI

**Test**: Create multiple workouts, call agent via MCP, verify charts display correctly in UI

---

## Iteration 11: Location Agent

**Goal**: Find nearby gyms and running tracks (MCP Server)

- [x] Create `agents/location_activity.py` as MCP server
- [x] Implement MCP tools: `find_nearby_gyms(location)`, `find_running_tracks(location)`
- [x] Uses geocoding API (Nominatim via geopy)
- [x] Return list of locations with distances (adjustable radius)
- [ ] Register MCP server in orchestrator (will be done in integration)
- [x] Add endpoint `/find-nearby` to API
- [x] Add location search to Streamlit UI
- [x] Test: Enter location, verify nearby gyms/tracks returned via MCP

**Test**: Enter address, verify agent returns list of nearby gyms with distances via MCP

---

## Iteration 12: Integration & Polish

**Goal**: End-to-end testing and refinements

- [ ] Test complete user workflows (all paths)
- [ ] Fix any bugs or edge cases
- [ ] Improve error messages and user feedback
- [ ] Add input validation
- [ ] Optimize LLM prompts based on testing
- [ ] Update README with usage instructions
- [ ] Final testing: Complete workout generation flow

**Test**: Full end-to-end test: upload photo → generate workout → save → view progress → find nearby gyms

