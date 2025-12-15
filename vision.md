# ROAMFIT - Technical Vision

## Technologies

- **Python 3.11+**: Core language
- **Strands**: Multi-agent framework for orchestrating agents
- **FastAPI**: REST API backend
- **Streamlit**: Web interface for user interaction
- **SQLite**: Local database for storing workouts and user data
- **PIL/Pillow**: Image processing for equipment detection
- **OpenAI API**: LLM capabilities (GPT-4 for text, GPT-4 Vision for image analysis)
- **python-dotenv**: Environment-based configuration

## Development Principles

- **KISS (Keep It Simple, Stupid)**: Always choose the simplest solution that works
- **MVP First**: Build minimal features to validate the idea
- **Single Responsibility**: Each agent does one thing well
- **Fail Fast**: Clear error handling and validation
- **Iterative Development**: Build, test, refine
- **No Premature Optimization**: Optimize only when needed

## Project Structure

```
roamfit/
├── main.py                 # Streamlit entry point
├── api.py                  # FastAPI endpoints
├── config.py              # Configuration management
├── database.py             # SQLite database setup/queries
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py     # Main orchestrator agent
│   ├── equipment_detection.py
│   ├── workout_summary.py
│   ├── workout_generator.py
│   ├── graph_trends.py
│   └── location_activity.py
├── models/
│   ├── __init__.py
│   └── schemas.py          # Data models/schemas
├── utils/
│   ├── __init__.py
│   └── llm.py              # LLM helper functions
├── db/
│   └── roamfit.db          # SQLite database (gitignored)
├── .env                    # Environment variables (gitignored)
├── requirements.txt
└── README.md
```

## Project Architecture

**Flow:**
1. User interacts via Streamlit UI
2. Streamlit calls FastAPI endpoints
3. FastAPI routes requests to Orchestrator Agent
4. Orchestrator uses Strands to coordinate specialized agents
5. Agents return results to Orchestrator
6. Orchestrator returns final response to API
7. API returns to Streamlit for display

**Agent Communication:**
- Orchestrator is the central coordinator
- Agents are tools/functions the Orchestrator calls
- Simple request/response pattern (no complex messaging)
- Each agent is independent and stateless

**Key Components:**
- **UI Layer**: Streamlit (user-facing)
- **API Layer**: FastAPI (business logic routing)
- **Agent Layer**: Strands agents (orchestration + specialized agents)
- **Data Layer**: SQLite (persistence)

## Data Model

**Tables:**

1. **workouts**
   - `id` (INTEGER PRIMARY KEY)
   - `date` (TEXT - ISO format)
   - `equipment` (TEXT - JSON array of equipment names)
   - `workout_plan` (TEXT - JSON workout details)
   - `location` (TEXT - optional)
   - `completed` (BOOLEAN)

2. **equipment_detections**
   - `id` (INTEGER PRIMARY KEY)
   - `timestamp` (TEXT - ISO format)
   - `image_path` (TEXT - path to uploaded image)
   - `detected_equipment` (TEXT - JSON array)
   - `location` (TEXT - optional geolocation)

3. **user_preferences**
   - `id` (INTEGER PRIMARY KEY)
   - `key` (TEXT UNIQUE)
   - `value` (TEXT - JSON)

**Notes:**
- Simple schema with minimal tables
- JSON for flexible data storage
- No complex relationships (single user for MVP)
- SQLite handles this easily

## Working with LLM

**LLM Usage:**
- **OpenAI API** for all LLM calls
- **GPT-4** for text generation (workout generation, summaries)
- **GPT-4 Vision** for equipment detection from images
- Simple wrapper function in `utils/llm.py` to handle API calls

**Pattern:**
- Each agent uses the LLM helper function
- Pass prompts and parameters
- Return structured responses (JSON when possible)
- Simple error handling (retry once on failure)

**Key Functions:**
- `call_llm(prompt, model="gpt-4")` - text generation
- `call_vision(image_path, prompt, model="gpt-4-vision-preview")` - image analysis

**Prompting:**
- Keep prompts clear and concise
- Request JSON responses when structure is needed
- Include context (previous workouts, equipment) in prompts

## LLM Monitoring

**Monitoring:**
- Log all LLM API calls (request/response)
- Track token usage per call
- Log errors and retries
- Simple file-based logging (no complex tools)

**What to Log:**
- Timestamp
- Agent name
- Model used
- Tokens used (input/output)
- Success/failure
- Response time

**Implementation:**
- Add logging to `utils/llm.py` wrapper functions
- Use Python's `logging` module
- Log to file: `logs/llm_calls.log`
- Optional: console output for development

**Metrics (Simple):**
- Track daily token usage
- Count API failures
- No complex dashboards (just logs for now)

## Workflows

**Main Workflow: Generate Workout**
1. User uploads equipment photo OR selects location
2. Orchestrator calls Equipment Detection Agent (if photo) OR Location Agent (if location)
3. Orchestrator calls Workout Summary Agent (get last workout)
4. Orchestrator calls Workout Generator Agent (equipment + history → workout plan)
5. Return workout plan to user
6. Save workout to database

**Secondary Workflows:**
- **View Progress**: Orchestrator → Graph/Trends Agent → return charts
- **Detect Equipment**: User uploads photo → Equipment Detection Agent → save detection
- **Find Nearby**: User provides location → Location Agent → return gyms/tracks

**Error Handling:**
- If any agent fails, return error message to user
- No complex retry logic (fail fast)

**Agent Dependencies:**
- Orchestrator coordinates all
- Agents are independent (no direct agent-to-agent calls)

## Deployment

**For MVP/Development:**
- Run locally: `streamlit run main.py`
- FastAPI runs as part of Streamlit or separate process
- SQLite database in `db/` folder
- No cloud deployment needed initially

**Simple Setup:**
- `requirements.txt` for dependencies
- `.env` file for API keys
- README with setup instructions
- No Docker/containers for MVP

**Future (if needed):**
- Can deploy Streamlit to Streamlit Cloud (free tier)
- Or deploy FastAPI + separate frontend
- Keep SQLite or migrate to PostgreSQL if needed

**Environment:**
- Development: local
- Production: TBD (only if MVP succeeds)

## Configuration Approach

**Configuration Method:**
- Use `.env` file for all environment variables
- `python-dotenv` to load variables
- `config.py` module to access config values

**Configuration Variables:**
- `OPENAI_API_KEY` - LLM API key
- `DATABASE_PATH` - SQLite database path (default: `db/roamfit.db`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `LLM_MODEL` - Default model (default: `gpt-4`)

**Implementation:**
- Single `config.py` file with `get_config()` function
- Load from `.env`, use defaults if missing
- No complex config files (YAML/JSON)
- `.env.example` template in repo

## Logging Approach

**Logging Strategy:**
- Use Python's built-in `logging` module
- Single logger configuration
- Log to both file and console

**Log Files:**
- `logs/app.log` - General application logs
- `logs/llm_calls.log` - LLM-specific logs (from monitoring section)

**Log Levels:**
- `DEBUG` - Development only
- `INFO` - Normal operations
- `WARNING` - Non-critical issues
- `ERROR` - Errors that need attention

**What to Log:**
- Agent calls (which agent, what action)
- API requests/responses (FastAPI)
- Database operations (errors only)
- LLM calls (detailed, as per monitoring section)
- User actions (high-level: "user generated workout")

**Implementation:**
- Configure logging in `config.py` or separate `logging_config.py`
- Simple format: `[TIMESTAMP] [LEVEL] [MODULE] - MESSAGE`
- Rotate logs if they get too large (optional for MVP)

