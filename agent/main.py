"""
AI Healing Pipeline - Main FastAPI Application

OBJECTIVES:
- FastAPI: routes, models, responses
- REST API design patterns
- Health check implementation
- Error handling
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
from datetime import datetime

# ============================================
# Configure logging
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# Create FastAPI app with metadata
# ============================================
app = FastAPI(
    title="AI Healing Pipeline Agent",
    description="Autonomous CI/CD failure detection and healing",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# ============================================
# Pydantic models for request/response validation
# ============================================

class PipelineFailure(BaseModel):
    """
    LEARNING: Pydantic automatically validates incoming data
    - Type checking
    - Required field validation
    - Documentation generation
    """
    stage: str = Field(..., description="Pipeline stage that failed", example="test")
    error_message: str = Field(..., description="Error message from pipeline")
    logs: str = Field(..., description="Relevant log output")
    timestamp: str = Field(..., description="When the failure occurred")
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional context (branch, commit, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "stage": "test",
                "error_message": "AssertionError: test_login failed",
                "logs": "Traceback...\nAssertionError: expected True, got False",
                "timestamp": "2024-01-27T12:00:00Z",
                "metadata": {
                    "branch": "main",
                    "commit": "abc123"
                }
            }
        }


class HealingResult(BaseModel):
    """Result of healing attempt"""
    success: bool = Field(..., description="Whether healing succeeded")
    fix_applied: Optional[str] = Field(None, description="Description of fix")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    iterations: int = Field(..., ge=0, description="Number of investigation iterations")
    message: str = Field(..., description="Human-readable result message")


# ============================================
# Route Handlers (Endpoints)
# ============================================

@app.get("/")
async def root():
    """
    LEARNING: Root endpoint
    - async def for async operations (better performance)
    - Returns JSON automatically
    """
    return {
        "service": "AI Healing Pipeline Agent",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """
    LEARNING: Health check endpoint
    - Used by Docker HEALTHCHECK
    - Used by Kubernetes liveness/readiness probes
    - Should be fast and simple
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/heal", response_model=HealingResult)
async def heal_pipeline(failure: PipelineFailure):
    """
    Main healing endpoint
    
    LEARNING:
    - POST method for creating/modifying resources
    - Automatic request validation via Pydantic
    - response_model ensures response matches schema
    - Raises HTTPException for errors (converted to proper HTTP codes)
    """
    logger.info(f"Received healing request for stage: {failure.stage}")
    logger.debug(f"Failure details: {failure.model_dump()}")
    
    try:
        # TODO: Implement actual healing logic in Week 2
        # For now, return placeholder response
        
        result = HealingResult(
            success=True,
            fix_applied="Placeholder - Week 2 will implement AI agent",
            confidence=0.95,
            iterations=1,
            message=f"Acknowledged failure in {failure.stage}. Ready for AI implementation."
        )
        
        logger.info(f"Healing result: {result.model_dump()}")
        return result
        
    except Exception as e:
        logger.error(f"Error during healing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@app.get("/metrics")
async def get_metrics():
    """
    LEARNING: Metrics endpoint
    - Provides observability
    - Can be scraped by Prometheus (Week 1 Day 6-7)
    """
    return {
        "total_healings": 0,
        "success_rate": 0.0,
        "average_resolution_time": 0.0,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================
# Startup/Shutdown Events
# ============================================

@app.on_event("startup")
async def startup_event():
    """Runs when application starts"""
    logger.info("🚀 AI Healing Agent starting up...")
    logger.info("API documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Runs when application shuts down"""
    logger.info("👋 AI Healing Agent shutting down...")


# ============================================
# Run directly (for local testing)
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
