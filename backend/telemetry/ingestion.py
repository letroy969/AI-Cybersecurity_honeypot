"""
Telemetry ingestion system for collecting and processing attack data
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid
import hashlib
import ipaddress

from database.connection import SessionLocal
from database.models import AttackEvent, AttackerFingerprint, HoneypotSession, SecurityAlert

logger = logging.getLogger(__name__)

class TelemetryIngestion:
    """Main telemetry ingestion service"""
    
    def __init__(self):
        self.session_cache = {}
        self.fingerprint_cache = {}
        self.alert_thresholds = {
            "critical": 10,  # 10 critical attacks trigger alert
            "high": 20,      # 20 high severity attacks trigger alert
            "medium": 50,    # 50 medium severity attacks trigger alert
        }
    
    async def initialize(self):
        """Initialize the telemetry service"""
        logger.info("🔧 Initializing telemetry ingestion service...")
        
        # Load existing fingerprints into cache
        await self._load_fingerprint_cache()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_old_sessions())
        asyncio.create_task(self._update_attacker_fingerprints())
        
        logger.info("✅ Telemetry ingestion service initialized")
    
    async def close(self):
        """Close the telemetry service"""
        logger.info("🛑 Closing telemetry ingestion service...")
        # Cleanup resources
        self.session_cache.clear()
        self.fingerprint_cache.clear()
    
    async def record_attack_event(
        self,
        source_ip: str,
        user_agent: str,
        method: str,
        endpoint: str,
        url: str,
        headers: Dict[str, str],
        query_params: Dict[str, str],
        body: Optional[str],
        status_code: int,
        response_time: float,
        attack_type: str = "normal",
        severity: str = "low",
        confidence: float = 0.0,
        anomaly_score: float = 0.0,
        is_anomaly: bool = False,
        honeypot_type: str = "web",
        country: Optional[str] = None,
        region: Optional[str] = None,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> str:
        """Record an attack event in the database"""
        try:
            # Generate unique request ID
            request_id = f"req_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Create attack event record
            attack_event = AttackEvent(
                source_ip=source_ip,
                user_agent=user_agent,
                method=method,
                endpoint=endpoint,
                url=url,
                headers=headers,
                query_params=query_params,
                body=body,
                status_code=status_code,
                response_time=response_time,
                attack_type=attack_type,
                severity=severity,
                confidence=confidence,
                anomaly_score=anomaly_score,
                is_anomaly=is_anomaly,
                honeypot_type=honeypot_type,
                country=country,
                region=region,
                city=city,
                latitude=latitude,
                longitude=longitude,
                request_id=request_id,
                session_id=self._get_or_create_session(source_ip, endpoint, honeypot_type),
                tags=self._extract_tags(url, headers, query_params)
            )
            
            # Save to database
            db = SessionLocal()
            try:
                db.add(attack_event)
                db.commit()
                db.refresh(attack_event)
                
                logger.info(f"📊 Recorded attack event: {request_id} from {source_ip} ({attack_type}/{severity})")
                
                # Update attacker fingerprint
                await self._update_attacker_fingerprint(attack_event)
                
                # Check for alert conditions
                await self._check_alert_conditions(source_ip, attack_type, severity)
                
                return request_id
                
            except Exception as e:
                db.rollback()
                logger.error(f"❌ Error saving attack event: {e}")
                raise
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error recording attack event: {e}")
            raise
    
    async def record_exception(
        self,
        endpoint: str,
        method: str,
        exception: str,
        client_ip: str,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Record an exception as a potential attack"""
        try:
            # Analyze exception for attack patterns
            attack_type = "exception"
            severity = "medium"
            confidence = 0.5
            
            if any(pattern in exception.lower() for pattern in ["sql", "injection", "union", "select"]):
                attack_type = "sql_injection"
                severity = "high"
                confidence = 0.8
            elif any(pattern in exception.lower() for pattern in ["xss", "script", "javascript"]):
                attack_type = "xss"
                severity = "medium"
                confidence = 0.7
            elif "timeout" in exception.lower() or "connection" in exception.lower():
                attack_type = "dos"
                severity = "high"
                confidence = 0.6
            
            # Record as attack event
            await self.record_attack_event(
                source_ip=client_ip,
                user_agent="Unknown",
                method=method,
                endpoint=endpoint,
                url=endpoint,
                headers={},
                query_params={},
                body=exception,
                status_code=500,
                response_time=0.0,
                attack_type=attack_type,
                severity=severity,
                confidence=confidence,
                anomaly_score=0.8,  # Exceptions are usually anomalous
                is_anomaly=True,
                honeypot_type="exception_handler"
            )
            
        except Exception as e:
            logger.error(f"❌ Error recording exception: {e}")
    
    def _get_or_create_session(self, source_ip: str, endpoint: str, honeypot_type: str) -> str:
        """Get or create a honeypot session for tracking"""
        session_key = f"{source_ip}:{honeypot_type}"
        
        if session_key not in self.session_cache:
            session_id = f"session_{uuid.uuid4().hex[:12]}"
            self.session_cache[session_key] = {
                "session_id": session_id,
                "source_ip": source_ip,
                "honeypot_type": honeypot_type,
                "start_time": datetime.utcnow(),
                "request_count": 0,
                "endpoints": set()
            }
        
        session = self.session_cache[session_key]
        session["request_count"] += 1
        session["endpoints"].add(endpoint)
        session["last_activity"] = datetime.utcnow()
        
        return session["session_id"]
    
    def _extract_tags(self, url: str, headers: Dict[str, str], query_params: Dict[str, str]) -> List[str]:
        """Extract relevant tags from request data"""
        tags = []
        
        # Check for common attack patterns
        if any(pattern in url.lower() for pattern in ["admin", "login", "auth"]):
            tags.append("authentication_related")
        
        if any(pattern in url.lower() for pattern in ["api", "rest", "json"]):
            tags.append("api_endpoint")
        
        if any(pattern in url.lower() for pattern in ["sql", "database", "query"]):
            tags.append("database_related")
        
        if any(pattern in url.lower() for pattern in ["file", "upload", "download"]):
            tags.append("file_operation")
        
        # Check headers
        if "x-forwarded-for" in headers:
            tags.append("proxied_request")
        
        if "user-agent" in headers:
            ua = headers["user-agent"].lower()
            if any(tool in ua for tool in ["sqlmap", "nikto", "nmap", "burp", "zap"]):
                tags.append("automated_tool")
        
        return tags
    
    async def _update_attacker_fingerprint(self, attack_event: AttackEvent):
        """Update attacker behavioral fingerprint"""
        try:
            source_ip = attack_event.source_ip
            
            # Get or create fingerprint
            if source_ip not in self.fingerprint_cache:
                await self._load_attacker_fingerprint(source_ip)
            
            fingerprint = self.fingerprint_cache.get(source_ip, {})
            
            # Update fingerprint data
            if "attack_patterns" not in fingerprint:
                fingerprint["attack_patterns"] = {}
            
            attack_type = attack_event.attack_type or "normal"
            fingerprint["attack_patterns"][attack_type] = fingerprint["attack_patterns"].get(attack_type, 0) + 1
            
            # Update user agents
            if "user_agents" not in fingerprint:
                fingerprint["user_agents"] = set()
            fingerprint["user_agents"].add(attack_event.user_agent or "Unknown")
            
            # Update endpoints
            if "endpoints" not in fingerprint:
                fingerprint["endpoints"] = set()
            fingerprint["endpoints"].add(attack_event.endpoint)
            
            # Update timing patterns
            if "timing_patterns" not in fingerprint:
                fingerprint["timing_patterns"] = []
            fingerprint["timing_patterns"].append({
                "timestamp": attack_event.timestamp,
                "response_time": attack_event.response_time
            })
            
            # Update statistics
            fingerprint["total_requests"] = fingerprint.get("total_requests", 0) + 1
            fingerprint["unique_endpoints"] = len(fingerprint.get("endpoints", set()))
            fingerprint["last_seen"] = attack_event.timestamp
            fingerprint["first_seen"] = fingerprint.get("first_seen", attack_event.timestamp)
            
            # Calculate risk score
            fingerprint["risk_score"] = self._calculate_risk_score(fingerprint)
            
            # Cache updated fingerprint
            self.fingerprint_cache[source_ip] = fingerprint
            
        except Exception as e:
            logger.error(f"❌ Error updating attacker fingerprint: {e}")
    
    def _calculate_risk_score(self, fingerprint: Dict[str, Any]) -> float:
        """Calculate risk score for attacker"""
        score = 0.0
        
        # Base score from request count
        score += min(fingerprint.get("total_requests", 0) * 2, 50)
        
        # Endpoint diversity
        score += min(fingerprint.get("unique_endpoints", 0) * 3, 30)
        
        # Attack type diversity
        attack_types = len(fingerprint.get("attack_patterns", {}))
        score += min(attack_types * 5, 20)
        
        # User agent diversity (potential bot detection)
        user_agents = len(fingerprint.get("user_agents", set()))
        if user_agents > 3:
            score += 10  # Multiple user agents suggest automation
        
        return min(score, 100.0)
    
    async def _check_alert_conditions(self, source_ip: str, attack_type: str, severity: str):
        """Check if alert conditions are met"""
        try:
            # Get recent attack count for this IP
            db = SessionLocal()
            try:
                recent_attacks = db.query(AttackEvent).filter(
                    and_(
                        AttackEvent.source_ip == source_ip,
                        AttackEvent.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0),
                        AttackEvent.severity == severity
                    )
                ).count()
                
                # Check threshold
                threshold = self.alert_thresholds.get(severity, 100)
                if recent_attacks >= threshold:
                    await self._create_security_alert(source_ip, severity, recent_attacks, attack_type)
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error checking alert conditions: {e}")
    
    async def _create_security_alert(
        self, 
        source_ip: str, 
        severity: str, 
        attack_count: int, 
        attack_type: str
    ):
        """Create a security alert"""
        try:
            alert_id = f"alert_{uuid.uuid4().hex[:12]}"
            
            alert = SecurityAlert(
                alert_id=alert_id,
                alert_type="attack_pattern",
                severity=severity,
                title=f"High Volume {severity.title()} Attacks from {source_ip}",
                description=f"Detected {attack_count} {severity} severity attacks from {source_ip} in the last 24 hours. Attack type: {attack_type}",
                source_ip=source_ip,
                detection_method="threshold_based",
                confidence=0.8,
                status="open"
            )
            
            db = SessionLocal()
            try:
                db.add(alert)
                db.commit()
                logger.info(f"🚨 Created security alert: {alert_id} for {source_ip}")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error creating security alert: {e}")
    
    async def _load_fingerprint_cache(self):
        """Load existing fingerprints into cache"""
        try:
            db = SessionLocal()
            try:
                # Get recent fingerprints
                fingerprints = db.query(AttackerFingerprint).filter(
                    AttackerFingerprint.last_seen >= datetime.utcnow().replace(day=1)  # This month
                ).all()
                
                for fp in fingerprints:
                    self.fingerprint_cache[fp.source_ip] = {
                        "attack_patterns": fp.attack_patterns or {},
                        "user_agents": set(fp.user_agents or []),
                        "endpoints": set(fp.common_endpoints or []),
                        "total_requests": fp.total_requests or 0,
                        "unique_endpoints": fp.unique_endpoints or 0,
                        "risk_score": fp.risk_score or 0.0,
                        "first_seen": fp.first_seen,
                        "last_seen": fp.last_seen
                    }
                
                logger.info(f"📚 Loaded {len(fingerprints)} fingerprints into cache")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error loading fingerprint cache: {e}")
    
    async def _load_attacker_fingerprint(self, source_ip: str):
        """Load specific attacker fingerprint"""
        try:
            db = SessionLocal()
            try:
                fingerprint = db.query(AttackerFingerprint).filter(
                    AttackerFingerprint.source_ip == source_ip
                ).first()
                
                if fingerprint:
                    self.fingerprint_cache[source_ip] = {
                        "attack_patterns": fingerprint.attack_patterns or {},
                        "user_agents": set(fingerprint.user_agents or []),
                        "endpoints": set(fingerprint.common_endpoints or []),
                        "total_requests": fingerprint.total_requests or 0,
                        "unique_endpoints": fingerprint.unique_endpoints or 0,
                        "risk_score": fingerprint.risk_score or 0.0,
                        "first_seen": fingerprint.first_seen,
                        "last_seen": fingerprint.last_seen
                    }
                else:
                    # Create new fingerprint entry
                    self.fingerprint_cache[source_ip] = {
                        "attack_patterns": {},
                        "user_agents": set(),
                        "endpoints": set(),
                        "total_requests": 0,
                        "unique_endpoints": 0,
                        "risk_score": 0.0,
                        "first_seen": datetime.utcnow(),
                        "last_seen": datetime.utcnow()
                    }
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error loading attacker fingerprint: {e}")
    
    async def _cleanup_old_sessions(self):
        """Background task to cleanup old sessions"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for key, session in self.session_cache.items():
                    if (current_time - session["last_activity"]).total_seconds() > 3600:  # 1 hour timeout
                        expired_sessions.append(key)
                
                for key in expired_sessions:
                    del self.session_cache[key]
                
                if expired_sessions:
                    logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
                    
            except Exception as e:
                logger.error(f"❌ Error in session cleanup: {e}")
    
    async def _update_attacker_fingerprints(self):
        """Background task to update attacker fingerprints in database"""
        while True:
            try:
                await asyncio.sleep(1800)  # Run every 30 minutes
                
                if not self.fingerprint_cache:
                    continue
                
                db = SessionLocal()
                try:
                    for source_ip, fingerprint_data in self.fingerprint_cache.items():
                        # Get or create fingerprint record
                        fingerprint = db.query(AttackerFingerprint).filter(
                            AttackerFingerprint.source_ip == source_ip
                        ).first()
                        
                        if not fingerprint:
                            fingerprint = AttackerFingerprint(source_ip=source_ip)
                            db.add(fingerprint)
                        
                        # Update fingerprint data
                        fingerprint.attack_patterns = fingerprint_data["attack_patterns"]
                        fingerprint.user_agents = list(fingerprint_data["user_agents"])
                        fingerprint.common_endpoints = list(fingerprint_data["endpoints"])
                        fingerprint.total_requests = fingerprint_data["total_requests"]
                        fingerprint.unique_endpoints = fingerprint_data["unique_endpoints"]
                        fingerprint.risk_score = fingerprint_data["risk_score"]
                        fingerprint.first_seen = fingerprint_data["first_seen"]
                        fingerprint.last_seen = fingerprint_data["last_seen"]
                        
                        # Calculate threat level
                        if fingerprint_data["risk_score"] > 80:
                            fingerprint.threat_level = "critical"
                        elif fingerprint_data["risk_score"] > 60:
                            fingerprint.threat_level = "high"
                        elif fingerprint_data["risk_score"] > 40:
                            fingerprint.threat_level = "medium"
                        else:
                            fingerprint.threat_level = "low"
                        
                        # Detect potential bots
                        fingerprint.is_bot = len(fingerprint_data["user_agents"]) > 3
                    
                    db.commit()
                    logger.info(f"💾 Updated {len(self.fingerprint_cache)} attacker fingerprints")
                    
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"❌ Error updating attacker fingerprints: {e}")
