"""
Database connection and session management for the honeypot system
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging
from typing import Generator

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://honeypot_user:honeypot_password@localhost:5432/honeypot_db"
)

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def get_db_connection():
    """
    Get database connection for async operations
    """
    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

def create_tables():
    """
    Create all database tables
    """
    try:
        from .models import Base, create_indexes
        Base.metadata.create_all(bind=engine)
        create_indexes(engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise

def drop_tables():
    """
    Drop all database tables (use with caution!)
    """
    try:
        from .models import Base
        Base.metadata.drop_all(bind=engine)
        logger.warning("🗑️ All database tables dropped")
    except Exception as e:
        logger.error(f"❌ Error dropping database tables: {e}")
        raise

def init_database():
    """
    Initialize database with tables and initial data
    """
    try:
        create_tables()
        
        # Add any initial data here
        db = SessionLocal()
        try:
            # Example: Create default ML model entry
            from .models import MLModel
            existing_model = db.query(MLModel).filter(MLModel.model_name == "default_anomaly_detector").first()
            if not existing_model:
                default_model = MLModel(
                    model_name="default_anomaly_detector",
                    model_version="1.0.0",
                    model_type="anomaly_detection",
                    is_active=True
                )
                db.add(default_model)
                db.commit()
                logger.info("✅ Default ML model created")
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding initial data: {e}")
        finally:
            db.close()
            
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
