"""Data models/schemas for ROAMFIT."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Exercise:
    """Represents a single exercise in a workout."""
    name: str
    reps: int
    instructions: str
    sets: Optional[int] = None  # Optional for CrossFit formats
    rest_seconds: Optional[int] = None  # Optional for CrossFit formats


@dataclass
class WorkoutPlan:
    """Represents a complete CrossFit-style workout plan."""
    format: str  # "EMOM", "AMRAP", "For Time", "Rounds for Time", "Tabata", "Chipper"
    exercises: List[Exercise]
    duration_minutes: int
    focus: str  # "upper_body", "lower_body", "full_body", "cardio"
    workout_description: Optional[str] = None  # Description of how to perform the workout
    warmup: Optional[str] = None
    cooldown: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "format": self.format,
            "exercises": [
                {
                    "name": ex.name,
                    "reps": ex.reps,
                    "instructions": ex.instructions
                }
                for ex in self.exercises
            ],
            "duration_minutes": self.duration_minutes,
            "focus": self.focus,
        }
        # Add optional fields
        if self.workout_description:
            result["workout_description"] = self.workout_description
        if self.warmup:
            result["warmup"] = self.warmup
        if self.cooldown:
            result["cooldown"] = self.cooldown
        # Add optional exercise fields if present
        for i, ex in enumerate(self.exercises):
            if ex.sets is not None:
                result["exercises"][i]["sets"] = ex.sets
            if ex.rest_seconds is not None:
                result["exercises"][i]["rest_seconds"] = ex.rest_seconds
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkoutPlan":
        """Create from dictionary."""
        exercises = [
            Exercise(
                name=ex["name"],
                reps=ex["reps"],
                instructions=ex["instructions"],
                sets=ex.get("sets"),
                rest_seconds=ex.get("rest_seconds")
            )
            for ex in data.get("exercises", [])
        ]
        return cls(
            format=data.get("format", "AMRAP"),
            exercises=exercises,
            duration_minutes=data.get("duration_minutes", 20),
            focus=data.get("focus", "full_body"),
            workout_description=data.get("workout_description"),
            warmup=data.get("warmup"),
            cooldown=data.get("cooldown")
        )


@dataclass
class WorkoutHistory:
    """Represents workout history summary."""
    summary: str
    last_workout_date: Optional[str] = None
    total_workouts: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "last_workout_date": self.last_workout_date,
            "total_workouts": self.total_workouts
        }


@dataclass
class WorkoutStats:
    """Represents workout statistics."""
    total_workouts: int
    completed_workouts: int
    recent_workouts_30_days: int
    workouts_per_week: float
    completion_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_workouts": self.total_workouts,
            "completed_workouts": self.completed_workouts,
            "recent_workouts_30_days": self.recent_workouts_30_days,
            "workouts_per_week": self.workouts_per_week,
            "completion_rate": self.completion_rate
        }


@dataclass
class ChartData:
    """Represents chart/graph data."""
    chart_type: str  # "frequency" or "equipment"
    image_base64: str
    format: str = "png"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "chart_type": self.chart_type,
            "image_base64": self.image_base64,
            "format": self.format
        }


@dataclass
class Location:
    """Represents a location (gym, track, etc.)."""
    name: str
    address: str
    latitude: float
    longitude: float
    distance_km: float
    distance_m: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "distance_km": self.distance_km,
            "distance_m": self.distance_m
        }


@dataclass
class EquipmentDetection:
    """Represents equipment detection result."""
    equipment: List[str]
    detection_id: Optional[int] = None
    image_path: Optional[str] = None
    location: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "equipment": self.equipment,
        }
        if self.detection_id:
            result["detection_id"] = self.detection_id
        if self.image_path:
            result["image_path"] = self.image_path
        if self.location:
            result["location"] = self.location
        if self.error:
            result["error"] = self.error
        return result

