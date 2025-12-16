"""Tests for database operations."""
import json
from datetime import datetime

import pytest

from database import (
    create_tables,
    delete_workout,
    get_last_workout,
    get_llm_stats,
    get_workout_by_id,
    get_workout_history,
    save_equipment_detection,
    save_llm_log,
    save_workout,
    update_workout,
    update_workout_completion,
)


class TestWorkoutOperations:
    """Tests for workout CRUD operations."""

    def test_save_workout(self, temp_db):
        """Test saving a workout."""
        workout_id = save_workout(
            equipment=["dumbbells", "bench"],
            workout_plan={"format": "AMRAP", "exercises": []},
            location="Test Gym",
            completed=False,
        )

        assert workout_id > 0

    def test_get_last_workout(self, temp_db):
        """Test retrieving last workout."""
        # Save a workout
        workout_id = save_workout(
            equipment=["dumbbells"], workout_plan={"format": "EMOM", "exercises": []}
        )

        # Get last workout
        last_workout = get_last_workout()

        assert last_workout is not None
        assert last_workout["id"] == workout_id
        assert "dumbbells" in last_workout["equipment"]
        assert last_workout["workout_plan"]["format"] == "EMOM"

    def test_get_workout_history(self, temp_db):
        """Test retrieving workout history."""
        # Save multiple workouts
        for i in range(3):
            save_workout(
                equipment=[f"equipment_{i}"], workout_plan={"format": "AMRAP", "exercises": []}
            )

        # Get history
        history = get_workout_history(limit=5)

        assert len(history) == 3
        assert all("id" in w for w in history)
        assert all("equipment" in w for w in history)

    def test_get_workout_by_id(self, temp_db):
        """Test retrieving workout by ID."""
        # Save a workout
        workout_id = save_workout(
            equipment=["kettlebells"],
            workout_plan={"format": "For Time", "exercises": []},
            location="Home",
        )

        # Get by ID
        workout = get_workout_by_id(workout_id)

        assert workout is not None
        assert workout["id"] == workout_id
        assert workout["location"] == "Home"

    def test_update_workout(self, temp_db):
        """Test updating workout."""
        # Save a workout
        workout_id = save_workout(
            equipment=["dumbbells"],
            workout_plan={"format": "AMRAP", "exercises": []},
            location="Old Location",
        )

        # Update workout
        success = update_workout(
            workout_id=workout_id, equipment=["dumbbells", "bench"], location="New Location"
        )

        assert success is True

        # Verify update
        workout = get_workout_by_id(workout_id)
        assert workout is not None
        assert "bench" in workout["equipment"]
        assert workout["location"] == "New Location"

    def test_update_workout_completion(self, temp_db):
        """Test updating workout completion status."""
        # Save a workout
        workout_id = save_workout(
            equipment=["dumbbells"],
            workout_plan={"format": "AMRAP", "exercises": []},
            completed=False,
        )

        # Mark as completed
        success = update_workout_completion(workout_id, completed=True)
        assert success is True

        # Verify
        workout = get_workout_by_id(workout_id)
        assert workout is not None
        assert workout["completed"] is True

        # Mark as incomplete
        update_workout_completion(workout_id, completed=False)
        workout = get_workout_by_id(workout_id)
        assert workout is not None
        assert workout["completed"] is False

    def test_delete_workout(self, temp_db):
        """Test deleting workout."""
        # Save a workout
        workout_id = save_workout(
            equipment=["dumbbells"], workout_plan={"format": "AMRAP", "exercises": []}
        )

        # Delete workout
        success = delete_workout(workout_id)
        assert success is True

        # Verify deletion
        workout = get_workout_by_id(workout_id)
        assert workout is None

    def test_delete_nonexistent_workout(self, temp_db):
        """Test deleting non-existent workout."""
        success = delete_workout(99999)
        assert success is False


class TestEquipmentDetectionOperations:
    """Tests for equipment detection operations."""

    def test_save_equipment_detection(self, temp_db):
        """Test saving equipment detection."""
        detection_id = save_equipment_detection(
            image_path="/tmp/test_image.jpg",
            detected_equipment=["dumbbells", "bench"],
            location="Test Gym",
        )

        assert detection_id > 0


class TestLLMLogOperations:
    """Tests for LLM log operations."""

    def test_save_llm_log(self, temp_db):
        """Test saving LLM log."""
        log_id = save_llm_log(
            agent_name="test_agent",
            model="gpt-4",
            status="SUCCESS",
            tokens_in=10,
            tokens_out=20,
            time_ms=100,
        )

        assert log_id > 0

    def test_get_llm_stats(self, temp_db):
        """Test getting LLM statistics."""
        # Save some logs
        save_llm_log("agent1", "gpt-4", "SUCCESS", 10, 20, 100)
        save_llm_log("agent2", "gpt-4o", "SUCCESS", 15, 25, 150)

        # Get stats
        stats = get_llm_stats()

        assert stats["total_calls"] == 2
        assert stats["successful_calls"] == 2
        assert stats["total_tokens"] == 70  # 10+20+15+25
        assert len(stats["by_agent"]) == 2
        assert len(stats["by_model"]) == 2
