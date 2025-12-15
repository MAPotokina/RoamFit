"""Graph/Trends Agent for ROAMFIT - MCP Server."""
import json
import base64
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from database import get_db_connection, get_workout_history


def get_workout_stats() -> Dict[str, Any]:
    """
    Get workout statistics from database.
    
    Returns dict compatible with WorkoutStats model.
    """
    """Get workout statistics from database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total workouts
        cursor.execute("SELECT COUNT(*) as count FROM workouts")
        total_workouts = cursor.fetchone()["count"]
        
        # Completed workouts
        cursor.execute("SELECT COUNT(*) as count FROM workouts WHERE completed = 1")
        completed_workouts = cursor.fetchone()["count"]
        
        # Workouts by date (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) as count FROM workouts 
            WHERE date >= ?
        """, (thirty_days_ago,))
        recent_workouts = cursor.fetchone()["count"]
        
        # Get all workouts for date analysis
        cursor.execute("SELECT date, completed FROM workouts ORDER BY date")
        workouts_data = cursor.fetchall()
        
        # Calculate workout frequency (workouts per week)
        if workouts_data:
            first_date = datetime.fromisoformat(workouts_data[0]["date"])
            last_date = datetime.fromisoformat(workouts_data[-1]["date"])
            days_span = (last_date - first_date).days + 1
            weeks_span = max(days_span / 7, 1)
            workouts_per_week = len(workouts_data) / weeks_span
        else:
            workouts_per_week = 0
        
        return {
            "total_workouts": total_workouts,
            "completed_workouts": completed_workouts,
            "recent_workouts_30_days": recent_workouts,
            "workouts_per_week": round(workouts_per_week, 2),
            "completion_rate": round((completed_workouts / total_workouts * 100) if total_workouts > 0 else 0, 2)
        }


def generate_charts(chart_type: str = "frequency") -> Dict[str, str]:
    """
    Generate workout progress charts.
    
    Returns dict compatible with ChartData model.
    """
    """
    Generate workout progress charts.
    
    Args:
        chart_type: Type of chart to generate ("frequency" or "equipment")
    
    Returns:
        Dict with base64 encoded chart image
    """
    workouts = get_workout_history(limit=100)  # Get more for trends
    
    if not workouts:
        # Return empty chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No workout data available", 
                ha="center", va="center", fontsize=16)
        ax.axis("off")
    else:
        if chart_type == "frequency":
            # Workout frequency chart
            dates = [datetime.fromisoformat(w["date"]) for w in workouts]
            dates.sort()
            
            # Count workouts per week
            weekly_counts = {}
            for date in dates:
                week_start = date - timedelta(days=date.weekday())
                week_key = week_start.strftime("%Y-%W")
                weekly_counts[week_key] = weekly_counts.get(week_key, 0) + 1
            
            weeks = sorted(weekly_counts.keys())
            counts = [weekly_counts[w] for w in weeks]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(range(len(weeks)), counts, color="steelblue")
            ax.set_xlabel("Week")
            ax.set_ylabel("Number of Workouts")
            ax.set_title("Workout Frequency (Workouts per Week)")
            ax.set_xticks(range(len(weeks)))
            ax.set_xticklabels([f"Week {i+1}" for i in range(len(weeks))], rotation=45)
            plt.tight_layout()
            
        elif chart_type == "equipment":
            # Equipment usage chart
            equipment_counts = {}
            for workout in workouts:
                for eq in workout.get("equipment", []):
                    equipment_counts[eq] = equipment_counts.get(eq, 0) + 1
            
            if equipment_counts:
                equipment = list(equipment_counts.keys())
                counts = list(equipment_counts.values())
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.barh(equipment, counts, color="coral")
                ax.set_xlabel("Usage Count")
                ax.set_ylabel("Equipment")
                ax.set_title("Equipment Usage Frequency")
                plt.tight_layout()
            else:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, "No equipment data available", 
                        ha="center", va="center", fontsize=16)
                ax.axis("off")
        else:
            # Default: frequency chart
            return generate_charts("frequency")
    
    # Convert to base64
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    
    return {
        "chart_type": chart_type,
        "image_base64": image_base64,
        "format": "png"
    }


# Note: MCP server implementation is in agents/graph_trends_mcp.py

