# ROAMFIT

Multi-agentic fitness application designed to help users maintain their fitness routine while traveling.

## Features

- 📷 **Equipment Detection**: Upload photos to detect available fitness equipment
- 🏋️ **Workout Generation**: Generate personalized workouts based on available equipment and history
- 📊 **Progress Tracking**: View workout history and progress charts
- 📍 **Location Services**: Find nearby gyms and running tracks
- 🤖 **Multi-Agent Architecture**: Powered by Strands agents with MCP integration

## Architecture

ROAMFIT uses a multi-agentic architecture:
- **Orchestrator Agent**: Coordinates workflow between all agents
- **Equipment Detection Agent**: Analyzes photos to detect fitness equipment
- **Workout Summary Agent**: Tracks and summarizes workout history
- **Workout Generator Agent**: Creates personalized workout plans
- **Graph/Trends Agent** (MCP): Visualizes workout progress
- **Location Agent** (MCP): Finds nearby gyms and running tracks

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd RoamFit
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Configuration

Edit `.env` file:
```
OPENAI_API_KEY=your_api_key_here
DATABASE_PATH=db/roamfit.db
LOG_LEVEL=INFO
LLM_MODEL=gpt-4
```

## Usage

### Starting the Application

**Terminal 1 - Start FastAPI Server:**
```bash
source venv/bin/activate
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

**Terminal 2 - Start Streamlit UI:**
```bash
source venv/bin/activate
streamlit run main.py
```

The UI will open automatically at `http://localhost:8501`

### Using the Application

1. **Generate Workout**:
   - Upload an equipment photo OR enter equipment manually
   - Optionally add location
   - Click "Generate Workout"
   - View your personalized workout plan

2. **View History**:
   - Go to "Workout History" tab
   - Adjust number of workouts to show
   - View summary and statistics

3. **Detect Equipment**:
   - Go to "Detect Equipment" tab
   - Upload a photo
   - View detected equipment list

4. **View Progress**:
   - Go to "Progress" tab
   - Select chart type (frequency or equipment)
   - View statistics and charts

5. **Find Nearby**:
   - Go to "Find Nearby" tab
   - Enter location
   - Select gyms or tracks
   - Adjust search radius
   - View nearby locations with distances

## API Endpoints

### POST `/generate-workout`
Generate workout from image or equipment list.

**Parameters:**
- `image` (file, optional): Equipment photo
- `equipment` (string, optional): JSON array of equipment names
- `location` (string, optional): Location string

**Example:**
```bash
curl -X POST http://localhost:8000/generate-workout \
  -F "equipment=[\"dumbbells\", \"bench\"]" \
  -F "location=Hotel Gym"
```

### POST `/detect-equipment`
Detect equipment from image.

**Parameters:**
- `image` (file, required): Equipment photo
- `location` (string, optional): Location string

### GET `/workout-history`
Get workout history summary.

**Parameters:**
- `limit` (int, optional): Number of workouts (default: 5, max: 50)

### GET `/progress`
Get workout progress statistics and charts.

**Parameters:**
- `chart_type` (string, optional): "frequency" or "equipment" (default: "frequency")

### GET `/find-nearby`
Find nearby gyms or running tracks.

**Parameters:**
- `location` (string, required): Location string
- `place_type` (string, optional): "gyms" or "tracks" (default: "gyms")
- `radius_km` (float, optional): Search radius in km (default: 2.0, max: 50)
- `limit` (int, optional): Max results (default: 10, max: 50)

## Project Structure

```
roamfit/
├── main.py                 # Streamlit UI
├── api.py                  # FastAPI endpoints
├── config.py               # Configuration
├── database.py             # Database operations
├── agents/
│   ├── orchestrator.py     # Main orchestrator
│   ├── equipment_detection.py
│   ├── workout_summary.py
│   ├── workout_generator.py
│   ├── graph_trends.py     # MCP Server
│   └── location_activity.py # MCP Server
├── models/
│   └── schemas.py
├── utils/
│   └── llm.py              # LLM utilities
├── db/                     # Database files
├── logs/                   # Log files
└── requirements.txt
```

## Development

See [doc/tasklist.md](./doc/tasklist.md) for development plan and [doc/workflow.md](./doc/workflow.md) for workflow guidelines.

## Testing

See [TESTING.md](./TESTING.md) for detailed testing instructions.

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]
