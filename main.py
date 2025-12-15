"""Streamlit UI for ROAMFIT."""
import streamlit as st
import requests  # type: ignore
import json
from pathlib import Path
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="ROAMFIT",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_URL = "http://localhost:8000"


def call_api(endpoint: str, method: str = "GET", **kwargs) -> Optional[dict]:
    """Call FastAPI endpoint."""
    try:
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}", timeout=30)
        elif method == "POST":
            response = requests.post(f"{API_URL}{endpoint}", **kwargs, timeout=60)
        else:
            return None
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to API. Make sure the FastAPI server is running:")
        st.code("uvicorn api:app --reload", language="bash")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API Error: {e}")
        try:
            error_detail = response.json().get("detail", str(e))
            st.error(f"Details: {error_detail}")
        except:
            pass
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def display_workout_plan(workout_plan: dict):
    """Display workout plan in formatted way."""
    if not workout_plan or workout_plan.get("error"):
        st.error(workout_plan.get("error", "Failed to generate workout plan"))
        return
    
    exercises = workout_plan.get("exercises", [])
    if not exercises:
        st.warning("No exercises in workout plan")
        return
    
    # Header
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Focus", workout_plan.get("focus", "N/A").replace("_", " ").title())
    with col2:
        st.metric("Duration", f"{workout_plan.get('duration_minutes', 0)} min")
    with col3:
        st.metric("Exercises", len(exercises))
    
    # Warmup
    if workout_plan.get("warmup"):
        with st.expander("🔥 Warm-up", expanded=False):
            st.write(workout_plan["warmup"])
    
    # Exercises
    st.subheader("💪 Exercises")
    for i, exercise in enumerate(exercises, 1):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.markdown(f"**{i}. {exercise.get('name', 'Unknown Exercise')}**")
            with col2:
                st.write(f"{exercise.get('sets', 0)} sets")
            with col3:
                st.write(f"{exercise.get('reps', 0)} reps")
            with col4:
                st.write(f"{exercise.get('rest_seconds', 0)}s rest")
            
            if exercise.get("instructions"):
                st.caption(f"💡 {exercise['instructions']}")
            
            if i < len(exercises):
                st.divider()
    
    # Cooldown
    if workout_plan.get("cooldown"):
        with st.expander("🧘 Cool-down", expanded=False):
            st.write(workout_plan["cooldown"])


# Main app
st.title("💪 ROAMFIT")
st.markdown("**Keep fit while on the road** - Multi-agentic fitness assistant")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    api_url = st.text_input("API URL", value=API_URL)
    if api_url != API_URL:
        API_URL = api_url
    
    st.divider()
    st.markdown("### 📖 About")
    st.markdown("""
    ROAMFIT helps you maintain your fitness routine while traveling.
    
    - Upload equipment photos
    - Generate personalized workouts
    - Track your progress
    """)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏋️ Generate Workout", "📊 Workout History", "🔍 Detect Equipment", "📈 Progress", "📍 Find Nearby"])

# Tab 1: Generate Workout
with tab1:
    st.header("Generate Workout")
    
    # Input method selection
    input_method = st.radio(
        "How would you like to provide equipment?",
        ["📷 Upload Photo", "✍️ Manual Entry"],
        horizontal=True
    )
    
    image_file = None
    equipment_list = None
    
    if input_method == "📷 Upload Photo":
        image_file = st.file_uploader(
            "Upload equipment photo",
            type=["jpg", "jpeg", "png"],
            help="Upload a photo of your available fitness equipment"
        )
        if image_file:
            st.image(image_file, caption="Uploaded image", use_container_width=True)
    else:
        equipment_input = st.text_area(
            "Enter equipment (one per line or comma-separated)",
            placeholder="dumbbells\nbench\nyoga_mat\nresistance_bands",
            help="List the equipment you have available"
        )
        if equipment_input:
            # Parse equipment list
            equipment_list = [
                item.strip() 
                for item in equipment_input.replace("\n", ",").split(",")
                if item.strip()
            ]
            if equipment_list:
                st.write("**Equipment detected:**", ", ".join(equipment_list))
    
    location = st.text_input("Location (optional)", placeholder="Hotel Gym, Room 205")
    
    # Generate button
    if st.button("🚀 Generate Workout", type="primary", use_container_width=True):
        if not image_file and not equipment_list:
            st.warning("Please upload a photo or enter equipment list")
        else:
            with st.spinner("Generating your personalized workout..."):
                # Prepare request
                files = {}
                data = {}
                
                if image_file:
                    files["image"] = (image_file.name, image_file.getvalue(), image_file.type)
                
                if equipment_list:
                    data["equipment"] = json.dumps(equipment_list)
                
                if location:
                    data["location"] = location
                
                # Call API
                result = call_api("/generate-workout", method="POST", files=files, data=data)
                
                if result:
                    st.success("✅ Workout generated successfully!")
                    
                    # Display equipment
                    if result.get("equipment"):
                        st.info(f"**Equipment:** {', '.join(result['equipment'])}")
                    
                    # Display workout plan
                    workout_plan = result.get("workout_plan")
                    if workout_plan:
                        display_workout_plan(workout_plan)
                    
                    # Display history context
                    if result.get("workout_history"):
                        history = result["workout_history"]
                        with st.expander("📈 Workout History Context", expanded=False):
                            st.write(f"**Total workouts:** {history.get('total_workouts', 0)}")
                            st.write(f"**Last workout:** {history.get('last_workout_date', 'N/A')}")
                            st.write(f"**Summary:** {history.get('summary', 'N/A')}")

# Tab 2: Workout History
with tab2:
    st.header("Workout History")
    
    limit = st.slider("Number of workouts to show", 1, 20, 5)
    
    if st.button("📊 Load History", type="primary"):
        with st.spinner("Loading workout history..."):
            result = call_api(f"/workout-history?limit={limit}")
            
            if result:
                st.success("✅ History loaded")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Workouts", result.get("total_workouts", 0))
                with col2:
                    st.metric("Last Workout", result.get("last_workout_date", "N/A")[:10] if result.get("last_workout_date") else "N/A")
                
                st.subheader("📝 Summary")
                st.write(result.get("summary", "No summary available"))

# Tab 3: Detect Equipment
with tab3:
    st.header("Detect Equipment")
    st.markdown("Upload a photo to detect available fitness equipment")
    
    detect_image = st.file_uploader(
        "Upload equipment photo",
        type=["jpg", "jpeg", "png"],
        key="detect_equipment"
    )
    
    detect_location = st.text_input("Location (optional)", key="detect_location", placeholder="Hotel Gym")
    
    if st.button("🔍 Detect Equipment", type="primary", use_container_width=True):
        if not detect_image:
            st.warning("Please upload an image")
        else:
            with st.spinner("Detecting equipment..."):
                files = {"image": (detect_image.name, detect_image.getvalue(), detect_image.type)}
                data = {}
                if detect_location:
                    data["location"] = detect_location
                
                result = call_api("/detect-equipment", method="POST", files=files, data=data)
                
                if result:
                    st.success("✅ Equipment detected!")
                    
                    equipment = result.get("equipment", [])
                    if equipment:
                        st.subheader("🏋️ Detected Equipment")
                        for item in equipment:
                            st.write(f"• {item.replace('_', ' ').title()}")
                    else:
                        st.info("No equipment detected in the image")
                    
                    if result.get("detection_id"):
                        st.caption(f"Detection ID: {result['detection_id']}")

# Tab 4: Progress
with tab4:
    st.header("Workout Progress")
    
    chart_type = st.radio(
        "Chart Type",
        ["frequency", "equipment"],
        format_func=lambda x: "Workout Frequency" if x == "frequency" else "Equipment Usage",
        horizontal=True
    )
    
    if st.button("📈 Load Progress", type="primary", use_container_width=True):
        with st.spinner("Loading progress data..."):
            result = call_api(f"/progress?chart_type={chart_type}")
            
            if result:
                st.success("✅ Progress loaded")
                
                # Display stats
                stats = result.get("stats", {})
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Workouts", stats.get("total_workouts", 0))
                with col2:
                    st.metric("Completed", stats.get("completed_workouts", 0))
                with col3:
                    st.metric("Workouts/Week", stats.get("workouts_per_week", 0))
                with col4:
                    st.metric("Completion Rate", f"{stats.get('completion_rate', 0)}%")
                
                # Display chart
                chart = result.get("chart", {})
                if chart.get("image_base64"):
                    import base64
                    from PIL import Image
                    from io import BytesIO
                    
                    image_data = base64.b64decode(chart["image_base64"])
                    img = Image.open(BytesIO(image_data))
                    st.image(img, caption=f"{chart.get('chart_type', 'Chart').title()} Chart", use_container_width=True)

# Tab 5: Find Nearby
with tab5:
    st.header("Find Nearby Gyms & Tracks")
    
    location_input = st.text_input(
        "Location",
        placeholder="New York, NY or 123 Main St, San Francisco",
        help="Enter an address, city, or location"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        place_type = st.radio(
            "Search for",
            ["gyms", "tracks"],
            format_func=lambda x: "🏋️ Gyms" if x == "gyms" else "🏃 Running Tracks",
            horizontal=True
        )
    with col2:
        radius_km = st.slider("Search Radius (km)", 0.5, 10.0, 2.0, 0.5)
    
    limit = st.slider("Maximum Results", 5, 20, 10)
    
    if st.button("🔍 Search", type="primary", use_container_width=True):
        if not location_input:
            st.warning("Please enter a location")
        else:
            with st.spinner(f"Searching for nearby {place_type}..."):
                result = call_api(
                    f"/find-nearby?location={location_input}&place_type={place_type}&radius_km={radius_km}&limit={limit}"
                )
                
                if result:
                    st.success(f"✅ Found {result.get('count', 0)} {place_type}")
                    
                    results = result.get("results", [])
                    if results:
                        for i, place in enumerate(results, 1):
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(f"**{i}. {place.get('name', 'Unknown')}**")
                                    st.caption(place.get("address", "Address not available"))
                                with col2:
                                    distance = place.get("distance_km", 0)
                                    if distance < 1:
                                        st.metric("Distance", f"{place.get('distance_m', 0):.0f}m")
                                    else:
                                        st.metric("Distance", f"{distance:.2f}km")
                                
                                if i < len(results):
                                    st.divider()
                    else:
                        st.info(f"No {place_type} found within {radius_km}km of {location_input}")

