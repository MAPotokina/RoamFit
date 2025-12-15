"""FastAPI application for ROAMFIT with Strands."""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import base64
import tempfile
import os
from pathlib import Path

from agents.strands_orchestrator import create_roamfit_orchestrator

app = FastAPI(title="ROAMFIT API (Strands)", version="2.0.0")

# Add CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator (singleton)
_orchestrator = None


def get_orchestrator():
    """Get or create the orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = create_roamfit_orchestrator()
    return _orchestrator


@app.post("/chat")
async def chat_endpoint(
    message: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    """
    Chat endpoint for interactive conversations with ROAMFIT.
    
    Required:
    - message: User's message/query
    
    Optional:
    - image: Equipment photo file (jpg, jpeg, png)
    """
    # Input validation
    if not message or not message.strip():
        raise HTTPException(
            status_code=400,
            detail="message parameter is required and cannot be empty"
        )
    
    if image:
        file_size = getattr(image, 'size', None) or 0
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=400,
                detail="Image file too large. Maximum size is 10MB"
            )
        
        allowed_types = ["image/jpeg", "image/jpg", "image/png"]
        content_type = getattr(image, 'content_type', None) or ""
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
    
    try:
        orchestrator = get_orchestrator()
        
        # Prepare query
        query = message.strip()
        
        # Handle image if provided
        if image:
            content = await image.read()
            image_base64 = base64.b64encode(content).decode("utf-8")
            image_data_uri = f"data:image/jpeg;base64,{image_base64}"
            query = f"I've uploaded an image of my available equipment. Please detect the equipment from this image: {image_data_uri}. {query}"
        
        # Get response from orchestrator
        response = orchestrator(query)
        
        return JSONResponse(content={
            "response": str(response),
            "message": message,
            "has_image": image is not None
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/generate-workout")
async def generate_workout_endpoint(
    image: Optional[UploadFile] = File(None),
    equipment: Optional[str] = Form(None),
    location: Optional[str] = Form(None)
):
    """
    Generate workout from image or equipment list (using Strands orchestrator).
    
    Either provide:
    - image: Equipment photo file (jpg, jpeg, png)
    - equipment: JSON string array of equipment names (e.g., ["dumbbells", "bench"])
    
    Optional:
    - location: Location string (e.g., "Hotel Gym, Room 205")
    """
    # Input validation
    if not image and not equipment:
        raise HTTPException(
            status_code=400,
            detail="Either 'image' file or 'equipment' JSON array must be provided"
        )
    
    if image:
        file_size = getattr(image, 'size', None) or 0
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=400,
                detail="Image file too large. Maximum size is 10MB"
            )
    
    try:
        orchestrator = get_orchestrator()
        
        # Build query for orchestrator
        query_parts = []
        
        if image:
            content = await image.read()
            image_base64 = base64.b64encode(content).decode("utf-8")
            image_data_uri = f"data:image/jpeg;base64,{image_base64}"
            query_parts.append(f"I've uploaded an image of my available equipment: {image_data_uri}")
        
        if equipment:
            import json
            try:
                equipment_list = json.loads(equipment)
                equipment_text = ", ".join(equipment_list) if isinstance(equipment_list, list) else equipment
                query_parts.append(f"Available equipment: {equipment_text}")
            except json.JSONDecodeError:
                query_parts.append(f"Available equipment: {equipment}")
        
        if location:
            query_parts.append(f"Location: {location}")
        
        query_parts.append("Please generate a personalized workout plan based on the available equipment and my workout history.")
        
        query = " ".join(query_parts)
        
        # Get response from orchestrator
        response = orchestrator(query)
        
        return JSONResponse(content={
            "workout_plan": str(response),
            "equipment": equipment if equipment else "detected from image",
            "location": location,
            "has_image": image is not None
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ROAMFIT API (Strands)",
        "version": "2.0.0",
        "endpoints": {
            "chat": "/chat",
            "generate_workout": "/generate-workout",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        orchestrator = get_orchestrator()
        return {
            "status": "healthy",
            "orchestrator": "initialized"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

