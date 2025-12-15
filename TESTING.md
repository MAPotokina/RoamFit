# Testing ROAMFIT

## Prerequisites

1. Make sure you have your `.env` file with `OPENAI_API_KEY` set
2. Install all dependencies: `pip install -r requirements.txt`

## Step 1: Start the FastAPI Server

Open a terminal and run:

```bash
cd /Users/margot/Documents/RoamFit
source venv/bin/activate
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`

You can verify it's running by visiting:
- `http://localhost:8000/` - Root endpoint
- `http://localhost:8000/health` - Health check
- `http://localhost:8000/docs` - Interactive API documentation

## Step 2: Start the Streamlit UI

Open a **new terminal** (keep the FastAPI server running) and run:

```bash
cd /Users/margot/Documents/RoamFit
source venv/bin/activate
streamlit run main.py
```

The UI will open automatically in your browser at `http://localhost:8501`

## Step 3: Test the UI

### Tab 1: Generate Workout

**Option A: Upload Photo**
1. Click "📷 Upload Photo"
2. Upload `test_image.jpg` (or any gym equipment photo)
3. Optionally enter a location
4. Click "🚀 Generate Workout"
5. Wait for the workout plan to appear

**Option B: Manual Equipment Entry**
1. Click "✍️ Manual Entry"
2. Enter equipment (one per line or comma-separated):
   ```
   dumbbells
   bench
   resistance_bands
   ```
3. Optionally enter a location
4. Click "🚀 Generate Workout"
5. View the generated workout plan

### Tab 2: Workout History
1. Click on "📊 Workout History" tab
2. Adjust the slider for number of workouts
3. Click "📊 Load History"
4. View the summary and statistics

### Tab 3: Detect Equipment
1. Click on "🔍 Detect Equipment" tab
2. Upload an equipment photo
3. Optionally enter location
4. Click "🔍 Detect Equipment"
5. View the detected equipment list

## Troubleshooting

**"Cannot connect to API" error:**
- Make sure the FastAPI server is running in another terminal
- Check that it's running on `http://localhost:8000`
- Verify the API URL in the sidebar settings

**Workout generation fails:**
- Check that `OPENAI_API_KEY` is set in `.env`
- Check the FastAPI server logs for errors
- Verify you have workout data in the database

**Image upload issues:**
- Make sure the image is a valid jpg/png file
- Check file size (should be reasonable)
- Try a different image

## Quick Test Commands

Test API directly:
```bash
# Health check
curl http://localhost:8000/health

# Workout history
curl http://localhost:8000/workout-history?limit=3

# Generate workout with equipment
curl -X POST http://localhost:8000/generate-workout \
  -F "equipment=[\"dumbbells\", \"bench\"]" \
  -F "location=Hotel Gym"
```

