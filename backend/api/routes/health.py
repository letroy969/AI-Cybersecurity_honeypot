"""
Health check and system status endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
import logging
import psutil
import time
from datetime import datetime

from database.connection import get_db, get_db_connection

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Cybersecurity Honeypot API",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with system metrics"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "AI Cybersecurity Honeypot API",
            "version": "1.0.0",
            "components": {}
        }
        
        # Database health
        try:
            db.execute(text("SELECT 1"))
            health_status["components"]["database"] = {
                "status": "healthy",
                "response_time": "< 1ms"
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # System metrics
        try:
            health_status["components"]["system"] = {
                "status": "healthy",
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "uptime": time.time() - psutil.boot_time()
            }
        except Exception as e:
            health_status["components"]["system"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Database connection pool
        try:
            # Check connection pool status
            pool = db.get_bind().pool
            health_status["components"]["connection_pool"] = {
                "status": "healthy",
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid()
            }
        except Exception as e:
            health_status["components"]["connection_pool"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes-style readiness check"""
    try:
        # Check if all critical components are ready
        db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/live")
async def liveness_check():
    """Kubernetes-style liveness check"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time() - psutil.boot_time()
    }

@router.get("/metrics")
async def system_metrics():
    """System performance metrics"""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics
        network = psutil.net_io_counters()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percentage": memory.percent,
                "free": memory.free
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percentage": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }
        
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        return {
            "error": "Failed to collect metrics",
            "timestamp": datetime.utcnow().isoformat()
        }
