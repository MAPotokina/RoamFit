"""Streamlit Chat UI for ROAMFIT with Strands."""
import base64
import re
from io import BytesIO
from typing import Any, Dict

import streamlit as st
from PIL import Image

from agents.strands_orchestrator import create_roamfit_orchestrator
from database import create_tables, get_last_workout, update_workout_completion

# Initialize database tables
create_tables()

# Page configuration
st.set_page_config(
    page_title="ROAMFIT", page_icon="💪", layout="wide", initial_sidebar_state="expanded"
)


# Initialize orchestrator (cached)
@st.cache_resource
def get_orchestrator():
    """Get or create the Strands orchestrator."""
    return create_roamfit_orchestrator()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = get_orchestrator()


# Sidebar
with st.sidebar:
    st.header("⚙️ ROAMFIT")
    st.markdown("**Multi-agentic fitness assistant**")

    st.divider()
    st.markdown("### 📖 About")
    st.markdown(
        """
    ROAMFIT helps you maintain your fitness routine while traveling.

    **Capabilities:**
    - 📷 Detect equipment from photos
    - 🏋️ Generate personalized workouts
    - 📊 Track your progress
    - 📍 Find nearby gyms and tracks

    **How to use:**
    - Upload a photo of equipment
    - Ask to generate a workout
    - Chat naturally with the assistant
    """
    )

    st.divider()
    if st.button(
        "🗑️ Clear Chat", use_container_width=True
    ):  # use_container_width still works for buttons
        st.session_state.messages = []
        st.rerun()


# Main chat interface
st.title("💪 ROAMFIT")
st.markdown("**Chat with your fitness assistant**")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Display uploaded image if present
        if "image" in message:
            st.image(message["image"], caption="Uploaded image", width="stretch")

        # Display chart if present
        if "chart" in message and "image_base64" in message["chart"]:
            try:
                chart_image = base64.b64decode(message["chart"]["image_base64"])
                chart_img = Image.open(BytesIO(chart_image))
                chart_type = message["chart"].get("chart_type", "Chart")
                st.image(chart_img, caption=f"{chart_type.title()} Chart", width="stretch")
            except Exception:
                pass


# Image uploader
uploaded_file = st.file_uploader(
    "Upload equipment photo (optional)",
    type=["jpg", "jpeg", "png"],
    help="Upload a photo of your available fitness equipment",
)

# Chat input
if prompt := st.chat_input("Ask about workouts, upload a photo, or request a workout plan..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Handle image if uploaded
    image_base64 = None
    if uploaded_file:
        image_data = uploaded_file.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        # Add image to message
        st.session_state.messages[-1]["image"] = uploaded_file

        # Display user message with image
        with st.chat_message("user"):
            st.markdown(prompt)
            st.image(uploaded_file, caption="Uploaded image", width="stretch")
    else:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

    # Prepare query for orchestrator
    detected_equipment = None

    # If image is provided, detect equipment first (before calling orchestrator)
    # This avoids including the large base64 string in the LLM prompt
    if image_base64:
        try:
            import os
            import tempfile

            from agents.equipment_detection import detect_equipment

            # Decode base64 and save to temp file
            image_data = base64.b64decode(image_base64)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(image_data)
                tmp_path = tmp_file.name

            # Detect equipment
            result = detect_equipment(tmp_path)
            detected_equipment = result.get("equipment", [])

            # Clean up temp file
            os.unlink(tmp_path)

            # Update query to include detected equipment
            if detected_equipment:
                equipment_text = ", ".join(detected_equipment)
                query = f"Available equipment: {equipment_text}. {prompt}"
            else:
                query = f"No equipment detected in the image. {prompt}"
        except Exception as e:
            # If detection fails, fall back to original query
            query = f"I've uploaded an image but equipment detection failed: {str(e)}. {prompt}"
    else:
        query = prompt

    # Get response from orchestrator
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # If we have an image, we need to pass it to the equipment detection agent
                # For now, we'll use a workaround: store image in a way the agent can access it
                # The query already mentions "uploaded image", so the agent should handle it

                # Use the query (already cleaned - no base64 included)
                # The orchestrator LLM will decide which agents to call based on the query
                response = st.session_state.orchestrator(query)
                response_str = str(response)

                # Try to parse chart data from response
                chart_data = None
                chart_type = None
                try:
                    import json

                    from agents.graph_trends import generate_charts

                    # First, try to parse as complete JSON response
                    try:
                        parsed = json.loads(response_str)
                        if isinstance(parsed, dict):
                            # Check for chart reference (avoids context overflow)
                            if "has_chart" in parsed and parsed["has_chart"]:
                                chart_type = parsed.get("chart_type", "frequency")
                                # Generate chart directly in UI (don't pass through LLM)
                                chart_data = generate_charts(chart_type=chart_type)
                                response_str = parsed.get("text", response_str)
                                # Remove the chart marker from text
                                response_str = re.sub(r"\[CHART:[^\]]+\]", "", response_str).strip()
                            elif "chart" in parsed and "image_base64" in parsed["chart"]:
                                chart_data = parsed["chart"]
                                response_str = parsed.get("text", response_str)
                            elif "image_base64" in parsed:
                                # Direct chart dict
                                chart_data = parsed
                    except json.JSONDecodeError:
                        # Not valid JSON, check for chart reference marker in text
                        chart_match = re.search(r"\[CHART:([^\]]+)\]", response_str)
                        if chart_match:
                            chart_type = chart_match.group(1)
                            # Generate chart directly in UI
                            chart_data = generate_charts(chart_type=chart_type)
                            # Remove marker from text
                            response_str = re.sub(r"\[CHART:[^\]]+\]", "", response_str).strip()
                        else:
                            # Try to extract JSON from text
                            json_match = re.search(
                                r'\{"chart"[^{}]*\{[^{}]*"image_base64"[^{}]*"[^"]*"[^{}]*\}[^{}]*\}',
                                response_str,
                                re.DOTALL,
                            )
                            if json_match:
                                parsed = json.loads(json_match.group())
                                if "chart" in parsed and "image_base64" in parsed["chart"]:
                                    chart_data = parsed["chart"]
                                    response_str = parsed.get(
                                        "text", response_str.replace(json_match.group(), "").strip()
                                    )
                except Exception:
                    # Silently fail - just show text response
                    pass

                # Display text response
                st.markdown(response_str)

                # Display chart if available
                if chart_data and "image_base64" in chart_data:
                    try:
                        chart_image = base64.b64decode(chart_data["image_base64"])
                        chart_img = Image.open(BytesIO(chart_image))
                        st.image(
                            chart_img,
                            caption=f"{chart_data.get('chart_type', 'Chart').title()} Chart",
                            width="stretch",
                        )
                    except Exception as e:
                        st.warning(f"Could not display chart: {str(e)}")

                # Check if a workout was generated and offer to mark as completed
                # Look for workout-related keywords in the response
                workout_keywords = [
                    "workout",
                    "emom",
                    "amrap",
                    "for time",
                    "tabata",
                    "chipper",
                    "exercise",
                    "reps",
                ]
                is_workout_response = any(
                    keyword in response_str.lower() for keyword in workout_keywords
                )

                # Try to get the last workout from database (if it was just saved)
                if is_workout_response:
                    try:
                        last_workout = get_last_workout()
                        if last_workout and not last_workout.get("completed", False):
                            workout_id = last_workout["id"]
                            st.divider()
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.info(f"💪 Workout saved! ID: {workout_id}")
                            with col2:
                                if st.button(
                                    "✅ Mark as Completed",
                                    key=f"complete_{workout_id}",
                                    use_container_width=True,
                                ):
                                    if update_workout_completion(workout_id, completed=True):
                                        st.success("Workout marked as completed! 🎉")
                                        st.rerun()
                                    else:
                                        st.error("Failed to update workout status")
                    except Exception:
                        # Silently fail if we can't check/get workout
                        pass

                # Add assistant response to chat
                message_data: Dict[str, Any] = {"role": "assistant", "content": response_str}
                if chart_data and isinstance(chart_data, dict):
                    message_data["chart"] = chart_data
                st.session_state.messages.append(message_data)

            except Exception as e:
                error_msg = str(e)

                # Handle specific error types
                if "rate limit" in error_msg.lower():
                    error_display = "⚠️ **Rate Limit Error**\n\nOpenAI API rate limit exceeded. Please wait a moment and try again."
                    st.warning(error_display)
                elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                    error_display = "🔑 **Authentication Error**\n\nPlease check your OpenAI API key in the `.env` file."
                    st.error(error_display)
                else:
                    error_display = f"❌ **Error**\n\n{error_msg}"
                    st.error(error_display)

                st.session_state.messages.append({"role": "assistant", "content": error_display})
