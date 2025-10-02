"""
Database models for the AI Cybersecurity Honeypot system
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import json

Base = declarative_base()

class AttackEvent(Base):
    """Model for storing attack events and telemetry data"""
    __tablename__ = "attack_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Request Information
    source_ip = Column(String(45), index=True)  # IPv6 support
    user_agent = Column(Text)
    method = Column(String(10), index=True)
    endpoint = Column(String(255), index=True)
    url = Column(Text)
    
    # Request Details
    headers = Column(JSON)
    query_params = Column(JSON)
    body = Column(Text)
    content_type = Column(String(100))
    
    # Response Information
    status_code = Column(Integer, index=True)
    response_time = Column(Float)  # in milliseconds
    
    # Attack Classification
    attack_type = Column(String(100), index=True)  # e.g., "sql_injection", "xss", "brute_force"
    severity = Column(String(20), index=True)  # "low", "medium", "high", "critical"
    confidence = Column(Float)  # ML confidence score 0-1
    
    # ML Analysis
    anomaly_score = Column(Float, index=True)
    is_anomaly = Column(Boolean, default=False, index=True)
    ml_features = Column(JSON)
    prediction_metadata = Column(JSON)
    
    # Geolocation (if available)
    country = Column(String(100))
    region = Column(String(100))
    city = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Additional Metadata
    session_id = Column(String(255), index=True)
    request_id = Column(String(255), unique=True, index=True)
    honeypot_type = Column(String(50), index=True)
    tags = Column(JSON)
    
    # Relationships
    fingerprints = relationship("AttackerFingerprint", back_populates="attack_event")

class AttackerFingerprint(Base):
    """Model for storing attacker behavioral fingerprints"""
    __tablename__ = "attacker_fingerprints"
    
    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String(45), index=True)
    
    # Behavioral Patterns
    attack_patterns = Column(JSON)  # Common attack types
    timing_patterns = Column(JSON)  # Request timing analysis
    tool_signatures = Column(JSON)  # Identified tools/frameworks
    
    # Technical Fingerprint
    user_agents = Column(JSON)  # List of user agents used
    common_endpoints = Column(JSON)  # Frequently targeted endpoints
    payload_patterns = Column(JSON)  # Common payload structures
    
    # Statistics
    total_requests = Column(Integer, default=0)
    unique_endpoints = Column(Integer, default=0)
    attack_types_count = Column(JSON)
    
    # Time Analysis
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    session_duration = Column(Float)  # Total session time
    
    # Risk Assessment
    risk_score = Column(Float, default=0.0)
    threat_level = Column(String(20), default="unknown")
    is_bot = Column(Boolean, default=False)
    
    # Relationships
    attack_event_id = Column(Integer, ForeignKey("attack_events.id"))
    attack_event = relationship("AttackEvent", back_populates="fingerprints")

class HoneypotSession(Base):
    """Model for tracking honeypot sessions and interactions"""
    __tablename__ = "honeypot_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    source_ip = Column(String(45), index=True)
    
    # Session Details
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration = Column(Float)  # in seconds
    
    # Honeypot Configuration
    honeypot_type = Column(String(50), index=True)
    endpoint_pattern = Column(String(255))
    
    # Interaction Tracking
    request_count = Column(Integer, default=0)
    unique_endpoints = Column(Integer, default=0)
    attack_count = Column(Integer, default=0)
    
    # Session Data
    session_data = Column(JSON)  # Custom session information
    interactions = Column(JSON)  # List of interactions in this session
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    was_compromised = Column(Boolean, default=False)

class MLModel(Base):
    """Model for storing ML model metadata and performance"""
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, index=True)
    model_version = Column(String(50))
    model_type = Column(String(50))  # "anomaly_detection", "classification", etc.
    
    # Model Performance
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_score = Column(Float)
    
    # Training Information
    training_data_size = Column(Integer)
    training_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Model Configuration
    hyperparameters = Column(JSON)
    feature_importance = Column(JSON)
    model_path = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_training = Column(Boolean, default=False)

class SecurityAlert(Base):
    """Model for storing security alerts and incidents"""
    __tablename__ = "security_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(255), unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Alert Information
    alert_type = Column(String(100), index=True)  # "anomaly", "attack", "intrusion"
    severity = Column(String(20), index=True)  # "low", "medium", "high", "critical"
    title = Column(String(255))
    description = Column(Text)
    
    # Related Data
    source_ip = Column(String(45), index=True)
    affected_endpoint = Column(String(255))
    attack_event_ids = Column(JSON)  # List of related attack event IDs
    
    # Alert Details
    detection_method = Column(String(100))  # "ml_anomaly", "rule_based", "manual"
    confidence = Column(Float)
    false_positive_probability = Column(Float)
    
    # Response
    status = Column(String(50), default="open")  # "open", "investigating", "resolved", "false_positive"
    assigned_to = Column(String(100))
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    
    # Metadata
    tags = Column(JSON)
    metadata = Column(JSON)

class SystemMetrics(Base):
    """Model for storing system performance and monitoring metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # System Performance
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    network_io = Column(Float)
    
    # Application Metrics
    requests_per_second = Column(Float)
    average_response_time = Column(Float)
    error_rate = Column(Float)
    active_connections = Column(Integer)
    
    # Security Metrics
    attacks_detected = Column(Integer)
    anomalies_found = Column(Integer)
    false_positives = Column(Integer)
    
    # ML Metrics
    model_predictions = Column(Integer)
    model_accuracy = Column(Float)
    feature_extraction_time = Column(Float)
    
    # Custom Metrics
    custom_metrics = Column(JSON)

class AuditLog(Base):
    """Model for storing system audit logs"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # User/System Information
    user_id = Column(String(100))
    session_id = Column(String(255))
    source_ip = Column(String(45))
    
    # Action Information
    action = Column(String(100), index=True)  # "login", "logout", "data_access", etc.
    resource = Column(String(255))
    method = Column(String(10))
    
    # Result
    success = Column(Boolean, index=True)
    status_code = Column(Integer)
    error_message = Column(Text)
    
    # Additional Context
    request_data = Column(JSON)
    response_data = Column(JSON)
    metadata = Column(JSON)

# Indexes for performance optimization
def create_indexes(engine):
    """Create additional indexes for performance optimization"""
    from sqlalchemy import Index
    
    # Composite indexes for common queries
    Index('idx_attack_events_ip_time', AttackEvent.source_ip, AttackEvent.timestamp)
    Index('idx_attack_events_type_severity', AttackEvent.attack_type, AttackEvent.severity)
    Index('idx_attack_events_anomaly', AttackEvent.is_anomaly, AttackEvent.anomaly_score)
    Index('idx_fingerprints_ip_seen', AttackerFingerprint.source_ip, AttackerFingerprint.last_seen)
    Index('idx_sessions_ip_active', HoneypotSession.source_ip, HoneypotSession.is_active)
    Index('idx_alerts_severity_status', SecurityAlert.severity, SecurityAlert.status)
    Index('idx_metrics_timestamp_type', SystemMetrics.timestamp)
    Index('idx_audit_user_action', AuditLog.user_id, AuditLog.action)
