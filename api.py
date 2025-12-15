"""FastAPI application for ROAMFIT with Strands."""
import logging
import time
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import base64
import json
from pathlib import Path

from agents.strands_orchestrator import create_roamfit_orchestrator
from utils.exceptions import handle_exception, ValidationError, AgentError
from utils.validation import (
    validate_image_file,
    validate_equipment_list,
    validate_location
)
from config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="ROAMFIT API (Strands)", version="2.0.0")

# Add CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests."""
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    
    return response


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
    request: Request,
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
    logger.info(f"API request: POST /chat from {request.client.host if request.client else 'unknown'}")
    
    try:
        # Input validation
        if not message or not message.strip():
            raise ValidationError("message parameter is required and cannot be empty")
        
        # Validate image if provided
        if image:
            content = await image.read()
            is_valid, error_msg = validate_image_file(content, filename=image.filename)
            if not is_valid:
                raise ValidationError(error_msg or "Invalid image file")
            
            logger.info(f"Image uploaded: {image.filename}, size: {len(content)} bytes")
        
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
        logger.info(f"Calling orchestrator with query length: {len(query)}")
        response = orchestrator(query)
        
        logger.info("Chat endpoint completed successfully")
        return JSONResponse(content={
            "response": str(response),
            "message": message,
            "has_image": image is not None
        })
        
    except ValidationError as e:
        logger.warning(f"Validation error in /chat: {e.message}")
        return handle_exception(e, context="chat_endpoint")
    except Exception as e:
        logger.error(f"Unexpected error in /chat: {str(e)}", exc_info=True)
        return handle_exception(e, context="chat_endpoint")


@app.post("/generate-workout")
async def generate_workout_endpoint(
    request: Request,
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
    logger.info(f"API request: POST /generate-workout from {request.client.host if request.client else 'unknown'}")
    
    try:
        # Input validation
        if not image and not equipment:
            raise ValidationError("Either 'image' file or 'equipment' JSON array must be provided")
        
        equipment_list = None
        
        # Validate image if provided
        if image:
            content = await image.read()
            is_valid, error_msg = validate_image_file(content, filename=image.filename)
            if not is_valid:
                raise ValidationError(error_msg or "Invalid image file")
            logger.info(f"Image uploaded: {image.filename}, size: {len(content)} bytes")
        
        # Validate equipment if provided
        if equipment:
            try:
                equipment_data = json.loads(equipment)
                is_valid, error_msg, equipment_list = validate_equipment_list(
                    equipment_data if isinstance(equipment_data, list) else [equipment_data]
                )
                if not is_valid:
                    raise ValidationError(error_msg or "Invalid equipment list")
                logger.info(f"Equipment provided: {equipment_list}")
            except json.JSONDecodeError:
                # Try as single string
                is_valid, error_msg, equipment_list = validate_equipment_list([equipment])
                if not is_valid:
                    raise ValidationError(error_msg or "Invalid equipment format")
        
        # Validate location if provided
        if location:
            is_valid, error_msg = validate_location(location)
            if not is_valid:
                raise ValidationError(error_msg or "Invalid location format")
            logger.info(f"Location provided: {location}")
        
        orchestrator = get_orchestrator()
        
        # Build query for orchestrator
        query_parts = []
        
        if image:
            content = await image.read()
            image_base64 = base64.b64encode(content).decode("utf-8")
            image_data_uri = f"data:image/jpeg;base64,{image_base64}"
            query_parts.append(f"I've uploaded an image of my available equipment: {image_data_uri}")
        
        if equipment_list:
            equipment_text = ", ".join(equipment_list)
            query_parts.append(f"Available equipment: {equipment_text}")
        
        if location:
            query_parts.append(f"Location: {location}")
        
        query_parts.append("Please generate a personalized workout plan based on the available equipment and my workout history.")
        
        query = " ".join(query_parts)
        
        # Get response from orchestrator
        logger.info(f"Calling orchestrator to generate workout")
        response = orchestrator(query)
        
        logger.info("Workout generation completed successfully")
        return JSONResponse(content={
            "workout_plan": str(response),
            "equipment": equipment_list if equipment_list else "detected from image",
            "location": location,
            "has_image": image is not None
        })
        
    except ValidationError as e:
        logger.warning(f"Validation error in /generate-workout: {e.message}")
        return handle_exception(e, context="generate_workout_endpoint")
    except Exception as e:
        logger.error(f"Unexpected error in /generate-workout: {str(e)}", exc_info=True)
        return handle_exception(e, context="generate_workout_endpoint")


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
    logger.debug("Health check requested")
    try:
        orchestrator = get_orchestrator()
        logger.debug("Health check passed")
        return {
            "status": "healthy",
            "orchestrator": "initialized"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }

