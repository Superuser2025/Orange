"""
AppleTrader Pro - Backend API Server
FastAPI application for subscription management and user authentication
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .api.subscription_routes import router as subscription_router
from .models.database import init_db

# Create FastAPI app
app = FastAPI(
    title="AppleTrader Pro API",
    description="Subscription management and authentication API for AppleTrader Pro",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    init_db()
    print("✅ Database initialized")


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AppleTrader Pro API",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["system"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AppleTrader Pro API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(subscription_router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# Run server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload in development
        log_level="info"
    )
