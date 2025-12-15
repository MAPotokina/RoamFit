"""Workout History Page for ROAMFIT."""
import streamlit as st
import json
from database import (
    get_workout_history, 
    update_workout_completion, 
    update_workout,
    delete_workout,
    get_workout_by_id,
    create_tables
)
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Workout History - ROAMFIT",
    page_icon="📋",
    layout="wide"
)

# Initialize database tables if needed
create_tables()

st.title("📋 Workout History")
st.markdown("View and manage your saved workouts")

# Get workout history
try:
    workouts = get_workout_history(limit=20)
    
    if not workouts:
        st.info("No workouts saved yet. Generate a workout to see it here!")
    else:
        st.metric("Total Workouts", len(workouts))
        st.divider()
        
        for workout in workouts:
            with st.container():
                workout_id = workout["id"]
                
                # Check if this workout is being edited
                edit_key = f"edit_{workout_id}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False
                
                # Parse date
                try:
                    date_obj = datetime.fromisoformat(workout["date"])
                    date_str = date_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    date_str = workout["date"]
                
                # Get workout plan
                workout_plan = workout.get("workout_plan", {})
                format_name = workout_plan.get("format", "Unknown")
                description = workout_plan.get("workout_description", "No description")
                
                if st.session_state[edit_key]:
                    # Edit mode
                    st.markdown(f"### ✏️ Editing Workout #{workout_id}")
                    
                    with st.form(key=f"edit_form_{workout_id}"):
                        # Equipment
                        equipment_text = st.text_input(
                            "Equipment (comma-separated)",
                            value=", ".join(workout.get("equipment", [])),
                            key=f"equipment_{workout_id}"
                        )
                        
                        # Location
                        location_text = st.text_input(
                            "Location",
                            value=workout.get("location", "") or "",
                            key=f"location_{workout_id}"
                        )
                        
                        # Workout description
                        description_text = st.text_area(
                            "Workout Description",
                            value=description,
                            key=f"description_{workout_id}"
                        )
                        
                        # Format
                        format_options = ["EMOM", "AMRAP", "For Time", "Rounds for Time", "Tabata", "Chipper", "Other"]
                        format_index = format_options.index(format_name) if format_name in format_options else 0
                        selected_format = st.selectbox(
                            "Format",
                            format_options,
                            index=format_index,
                            key=f"format_{workout_id}"
                        )
                        
                        # Duration
                        duration = st.number_input(
                            "Duration (minutes)",
                            min_value=1,
                            max_value=120,
                            value=workout_plan.get("duration_minutes", 20),
                            key=f"duration_{workout_id}"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)
                        with col2:
                            cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)
                        
                        if save_btn:
                            # Parse equipment
                            equipment_list = [e.strip() for e in equipment_text.split(",") if e.strip()]
                            
                            # Update workout plan
                            updated_plan = workout_plan.copy()
                            updated_plan["format"] = selected_format
                            updated_plan["duration_minutes"] = duration
                            updated_plan["workout_description"] = description_text
                            
                            # Update workout
                            if update_workout(
                                workout_id=workout_id,
                                equipment=equipment_list,
                                workout_plan=updated_plan,
                                location=location_text if location_text else None
                            ):
                                st.success("Workout updated successfully! 🎉")
                                st.session_state[edit_key] = False
                                st.rerun()
                            else:
                                st.error("Failed to update workout")
                        
                        if cancel_btn:
                            st.session_state[edit_key] = False
                            st.rerun()
                else:
                    # View mode
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        # Display workout info
                        status_icon = "✅" if workout.get("completed") else "⏳"
                        st.markdown(f"### {status_icon} Workout #{workout_id} - {format_name}")
                        st.markdown(f"**Date:** {date_str}")
                        st.markdown(f"**Equipment:** {', '.join(workout.get('equipment', []))}")
                        if workout.get("location"):
                            st.markdown(f"**Location:** {workout['location']}")
                        st.markdown(f"**Description:** {description}")
                        
                        # Show exercises if available
                        exercises = workout_plan.get("exercises", [])
                        if exercises:
                            st.markdown("**Exercises:**")
                            for ex in exercises:
                                ex_name = ex.get("name", "Unknown")
                                ex_reps = ex.get("reps", 0)
                                st.markdown(f"- {ex_name}: {ex_reps} reps")
                    
                    with col2:
                        st.markdown("")  # Spacing
                        if workout.get("completed"):
                            st.success("✅ Completed")
                        else:
                            st.info("⏳ Pending")
                    
                    with col3:
                        st.markdown("")  # Spacing
                        if not workout.get("completed"):
                            if st.button("✅ Complete", key=f"complete_{workout_id}", use_container_width=True):
                                if update_workout_completion(workout_id, completed=True):
                                    st.success("Workout marked as completed! 🎉")
                                    st.rerun()
                                else:
                                    st.error("Failed to update workout status")
                        else:
                            if st.button("↩️ Incomplete", key=f"incomplete_{workout_id}", use_container_width=True):
                                if update_workout_completion(workout_id, completed=False):
                                    st.info("Workout marked as incomplete")
                                    st.rerun()
                                else:
                                    st.error("Failed to update workout status")
                    
                    with col4:
                        st.markdown("")  # Spacing
                        col4a, col4b = st.columns(2)
                        with col4a:
                            if st.button("✏️", key=f"edit_btn_{workout_id}", help="Edit workout", use_container_width=True):
                                st.session_state[edit_key] = True
                                st.rerun()
                        with col4b:
                            if st.button("🗑️", key=f"delete_btn_{workout_id}", help="Delete workout", use_container_width=True):
                                if delete_workout(workout_id):
                                    st.success("Workout deleted! 🗑️")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete workout")
                
                st.divider()
    
except Exception as e:
    st.error(f"Error loading workout history: {str(e)}")

