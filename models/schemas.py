"""Data models/schemas for ROAMFIT."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Exercise:
    """Represents a single exercise in a workout."""
    name: str
    sets: int
    reps: int
    rest_seconds: int
    instructions: str


@dataclass
class WorkoutPlan:
    """Represents a complete workout plan."""
    exercises: List[Exercise]
    duration_minutes: int
    focus: str  # "upper_body", "lower_body", "full_body", "cardio"
    warmup: Optional[str] = None
    cooldown: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "exercises": [
                {
                    "name": ex.name,
                    "sets": ex.sets,
                    "reps": ex.reps,
                    "rest_seconds": ex.rest_seconds,
                    "instructions": ex.instructions
                }
                for ex in self.exercises
            ],
            "duration_minutes": self.duration_minutes,
            "focus": self.focus,
            "warmup": self.warmup,
            "cooldown": self.cooldown
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkoutPlan":
        """Create from dictionary."""
        exercises = [
            Exercise(
                name=ex["name"],
                sets=ex["sets"],
                reps=ex["reps"],
                rest_seconds=ex["rest_seconds"],
                instructions=ex["instructions"]
            )
            for ex in data.get("exercises", [])
        ]
        return cls(
            exercises=exercises,
            duration_minutes=data.get("duration_minutes", 0),
            focus=data.get("focus", "full_body"),
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

