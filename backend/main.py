"""
AI Cybersecurity Honeypot - Main FastAPI Application
Educational security research platform for attack simulation and analysis
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging
from typing import Dict, Any

from api.routes import honeypots, analytics, reports, health
from telemetry.ingestion import TelemetryIngestion
from database.connection import get_db_connection
from ml.anomaly_detector import AnomalyDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
telemetry_service = None
anomaly_detector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global telemetry_service, anomaly_detector
    
    # Startup
    logger.info("🚀 Starting AI Cybersecurity Honeypot...")
    
    try:
        # Initialize database connection
        db = await get_db_connection()
        logger.info("✅ Database connected")
        
        # Initialize telemetry service
        telemetry_service = TelemetryIngestion()
        await telemetry_service.initialize()
        logger.info("✅ Telemetry service initialized")
        
        # Initialize ML anomaly detector
        anomaly_detector = AnomalyDetector()
        await anomaly_detector.load_model()
        logger.info("✅ ML anomaly detector loaded")
        
        logger.info("🎯 Honeypot system ready for attacks!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down honeypot system...")
    if telemetry_service:
        await telemetry_service.close()
    if anomaly_detector:
        await anomaly_detector.close()

# Create FastAPI application
app = FastAPI(
    title="AI Cybersecurity Honeypot",
    description="Educational security research platform for attack simulation and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "honeypot-frontend"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests for security analysis"""
    start_time = time.time()
    
    # Log request details
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    method = request.method
    url = str(request.url)
    
    logger.info(f"📥 {method} {url} from {client_ip} ({user_agent})")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log response
    logger.info(f"📤 {method} {url} -> {response.status_code} ({process_time:.3f}s)")
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for security monitoring"""
    logger.error(f"🚨 Unhandled exception on {request.url}: {exc}")
    
    # Send to telemetry for analysis
    if telemetry_service:
        await telemetry_service.record_exception(
            endpoint=str(request.url),
            method=request.method,
            exception=str(exc),
            client_ip=request.client.host
        )
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

# Include routers
app.include_router(honeypots.router, prefix="/api/honeypots", tags=["honeypots"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(health.router, prefix="/api/health", tags=["health"])

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AI Cybersecurity Honeypot API",
        "version": "1.0.0",
        "status": "operational",
        "warning": "⚠️ EDUCATIONAL USE ONLY - DO NOT DEPLOY TO PRODUCTION",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "honeypots": "/api/honeypots",
            "analytics": "/api/analytics",
            "reports": "/api/reports"
        }
    }

@app.get("/api/status")
async def system_status():
    """Detailed system status endpoint"""
    status = {
        "system": "AI Cybersecurity Honeypot",
        "version": "1.0.0",
        "environment": "development",
        "services": {
            "database": "connected" if await get_db_connection() else "disconnected",
            "telemetry": "active" if telemetry_service else "inactive",
            "ml_detector": "loaded" if anomaly_detector else "unloaded"
        },
        "security_notice": {
            "purpose": "Educational research only",
            "deployment": "Local development environment",
            "legal": "See LEGAL.md for terms and conditions"
        }
    }
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
