"""FastAPI application for ROAMFIT."""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
import json
import tempfile
import os
from pathlib import Path

from agents.orchestrator import generate_workout_flow
from agents.equipment_detection import detect_equipment
from agents.workout_summary import summarize_workout_history
from agents.graph_trends import get_workout_stats, generate_charts
from agents.location_activity import find_nearby_gyms, find_running_tracks

app = FastAPI(title="ROAMFIT API", version="1.0.0")


@app.post("/generate-workout")
async def generate_workout_endpoint(
    image: Optional[UploadFile] = File(None),
    equipment: Optional[str] = Form(None),
    location: Optional[str] = Form(None)
):
    """
    Generate workout from image or equipment list.
    
    Either provide:
    - image: Equipment photo file
    - equipment: JSON string array of equipment names
    
    Optional:
    - location: Location string
    """
    image_path = None
    
    try:
        # Handle image upload
        if image:
            # Save uploaded file temporarily
            suffix = Path(image.filename).suffix if image.filename else ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                content = await image.read()
                tmp_file.write(content)
                image_path = tmp_file.name
        
        # Parse equipment list if provided
        equipment_list = None
        if equipment:
            try:
                equipment_list = json.loads(equipment)
                if not isinstance(equipment_list, list):
                    raise ValueError("equipment must be a JSON array")
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON format for equipment parameter"
                )
        
        # Call orchestrator
        result = generate_workout_flow(
            image_path=image_path,
            location=location,
            equipment=equipment_list
        )
        
        # Clean up temporary file
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)
        
        # Check for errors
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temporary file on error
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/detect-equipment")
async def detect_equipment_endpoint(
    image: UploadFile = File(...),
    location: Optional[str] = Form(None)
):
    """
    Detect equipment from image.
    
    Required:
    - image: Equipment photo file
    
    Optional:
    - location: Location string
    """
    image_path = None
    
    try:
        # Save uploaded file temporarily
        suffix = Path(image.filename).suffix if image.filename else ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await image.read()
            tmp_file.write(content)
            image_path = tmp_file.name
        
        # Call equipment detection agent
        result = detect_equipment(image_path, location=location or None)  # type: ignore
        
        # Clean up temporary file
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)
        
        return JSONResponse(content=result)
        
    except FileNotFoundError as e:
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Clean up temporary file on error
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/workout-history")
async def workout_history_endpoint(limit: int = 5):
    """
    Get workout history summary.
    
    Optional:
    - limit: Number of recent workouts to include (default: 5)
    """
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=400,
                detail="limit must be between 1 and 50"
            )
        
        result = summarize_workout_history(limit=limit)
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ROAMFIT API",
        "version": "1.0.0",
        "endpoints": {
            "generate_workout": "/generate-workout",
            "detect_equipment": "/detect-equipment",
            "workout_history": "/workout-history"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/progress")
async def progress_endpoint(chart_type: str = "frequency"):
    """
    Get workout progress statistics and charts.
    
    Optional:
    - chart_type: Type of chart ("frequency" or "equipment", default: "frequency")
    """
    try:
        if chart_type not in ["frequency", "equipment"]:
            raise HTTPException(
                status_code=400,
                detail="chart_type must be 'frequency' or 'equipment'"
            )
        
        stats = get_workout_stats()
        chart = generate_charts(chart_type)
        
        return JSONResponse(content={
            "stats": stats,
            "chart": chart
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/find-nearby")
async def find_nearby_endpoint(
    location: str,
    place_type: str = "gyms",
    radius_km: float = 2.0,
    limit: int = 10
):
    """
    Find nearby gyms or running tracks.
    
    Required:
    - location: Location string (address, city, etc.)
    
    Optional:
    - place_type: "gyms" or "tracks" (default: "gyms")
    - radius_km: Search radius in kilometers (default: 2.0)
    - limit: Maximum number of results (default: 10)
    """
    try:
        if radius_km < 0.1 or radius_km > 50:
            raise HTTPException(
                status_code=400,
                detail="radius_km must be between 0.1 and 50"
            )
        
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=400,
                detail="limit must be between 1 and 50"
            )
        
        if place_type == "gyms":
            results = find_nearby_gyms(location, radius_km, limit)
        elif place_type == "tracks":
            results = find_running_tracks(location, radius_km, limit)
        else:
            raise HTTPException(
                status_code=400,
                detail="place_type must be 'gyms' or 'tracks'"
            )
        
        return JSONResponse(content={
            "location": location,
            "place_type": place_type,
            "radius_km": radius_km,
            "results": results,
            "count": len(results)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

