"""
Analytics endpoints for attack data analysis and visualization
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from database.connection import get_db
from database.models import AttackEvent, AttackerFingerprint, SecurityAlert

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get overview analytics for the dashboard"""
    try:
        # Get time range (last 24 hours)
        time_threshold = datetime.utcnow() - timedelta(hours=24)
        
        # Total attacks in last 24 hours
        total_attacks = db.query(AttackEvent).filter(
            AttackEvent.timestamp >= time_threshold
        ).count()
        
        # Unique attackers
        unique_attackers = db.query(AttackEvent.source_ip).filter(
            AttackEvent.timestamp >= time_threshold
        ).distinct().count()
        
        # Attack types breakdown
        attack_types = db.query(
            AttackEvent.attack_type,
            func.count(AttackEvent.id).label('count')
        ).filter(
            AttackEvent.timestamp >= time_threshold,
            AttackEvent.attack_type != 'normal'
        ).group_by(AttackEvent.attack_type).all()
        
        # Severity breakdown
        severity_stats = db.query(
            AttackEvent.severity,
            func.count(AttackEvent.id).label('count')
        ).filter(
            AttackEvent.timestamp >= time_threshold
        ).group_by(AttackEvent.severity).all()
        
        # Anomalies detected
        anomalies = db.query(AttackEvent).filter(
            AttackEvent.timestamp >= time_threshold,
            AttackEvent.is_anomaly == True
        ).count()
        
        # Active alerts
        active_alerts = db.query(SecurityAlert).filter(
            SecurityAlert.status.in_(['open', 'investigating'])
        ).count()
        
        return {
            "total_attacks": total_attacks,
            "unique_attackers": unique_attackers,
            "anomalies_detected": anomalies,
            "active_alerts": active_alerts,
            "attack_types": {at.attack_type: at.count for at in attack_types},
            "severity_breakdown": {s.severity: s.count for s in severity_stats},
            "time_range": "24 hours",
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        return {"error": "Failed to fetch analytics overview"}

@router.get("/attacks")
async def get_attacks(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    severity: Optional[str] = Query(None),
    attack_type: Optional[str] = Query(None),
    source_ip: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168)
):
    """Get filtered attack events"""
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(AttackEvent).filter(
            AttackEvent.timestamp >= time_threshold
        )
        
        # Apply filters
        if severity:
            query = query.filter(AttackEvent.severity == severity)
        if attack_type:
            query = query.filter(AttackEvent.attack_type == attack_type)
        if source_ip:
            query = query.filter(AttackEvent.source_ip == source_ip)
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results
        attacks = query.order_by(desc(AttackEvent.timestamp)).offset(offset).limit(limit).all()
        
        # Convert to dict format
        attack_list = []
        for attack in attacks:
            attack_dict = {
                "id": attack.id,
                "timestamp": attack.timestamp.isoformat(),
                "source_ip": attack.source_ip,
                "method": attack.method,
                "endpoint": attack.endpoint,
                "attack_type": attack.attack_type,
                "severity": attack.severity,
                "confidence": attack.confidence,
                "anomaly_score": attack.anomaly_score,
                "is_anomaly": attack.is_anomaly,
                "country": attack.country,
                "user_agent": attack.user_agent[:100] + "..." if len(attack.user_agent) > 100 else attack.user_agent
            }
            attack_list.append(attack_dict)
        
        return {
            "attacks": attack_list,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "filters": {
                "severity": severity,
                "attack_type": attack_type,
                "source_ip": source_ip,
                "hours": hours
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting attacks: {e}")
        return {"error": "Failed to fetch attacks"}

@router.get("/attackers")
async def get_attackers(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    hours: int = Query(24, ge=1, le=168)
):
    """Get attacker fingerprint analysis"""
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Get attacker statistics
        attacker_stats = db.query(
            AttackEvent.source_ip,
            func.count(AttackEvent.id).label('attack_count'),
            func.count(func.distinct(AttackEvent.endpoint)).label('unique_endpoints'),
            func.count(func.distinct(AttackEvent.attack_type)).label('attack_types'),
            func.max(AttackEvent.timestamp).label('last_seen'),
            func.min(AttackEvent.timestamp).label('first_seen'),
            func.avg(AttackEvent.anomaly_score).label('avg_anomaly_score'),
            func.max(AttackEvent.severity).label('max_severity'),
            func.string_agg(func.distinct(AttackEvent.country), ',').label('countries')
        ).filter(
            AttackEvent.timestamp >= time_threshold
        ).group_by(AttackEvent.source_ip).order_by(
            desc('attack_count')
        ).limit(limit).all()
        
        attackers = []
        for stat in attacker_stats:
            attacker_dict = {
                "source_ip": stat.source_ip,
                "attack_count": stat.attack_count,
                "unique_endpoints": stat.unique_endpoints,
                "attack_types": stat.attack_types,
                "first_seen": stat.first_seen.isoformat() if stat.first_seen else None,
                "last_seen": stat.last_seen.isoformat() if stat.last_seen else None,
                "avg_anomaly_score": float(stat.avg_anomaly_score) if stat.avg_anomaly_score else 0.0,
                "max_severity": stat.max_severity,
                "countries": stat.countries.split(',') if stat.countries else [],
                "risk_score": min(stat.attack_count * 10 + stat.unique_endpoints * 5, 100)
            }
            attackers.append(attacker_dict)
        
        return {
            "attackers": attackers,
            "total_attackers": len(attackers),
            "time_range": f"{hours} hours"
        }
        
    except Exception as e:
        logger.error(f"Error getting attackers: {e}")
        return {"error": "Failed to fetch attackers"}

@router.get("/timeline")
async def get_attack_timeline(
    db: Session = Depends(get_db),
    hours: int = Query(24, ge=1, le=168),
    interval: str = Query("1h", regex="^(1m|5m|15m|1h|6h|1d)$")
):
    """Get attack timeline data for visualization"""
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Convert interval to PostgreSQL format
        interval_map = {
            "1m": "1 minute",
            "5m": "5 minutes", 
            "15m": "15 minutes",
            "1h": "1 hour",
            "6h": "6 hours",
            "1d": "1 day"
        }
        pg_interval = interval_map[interval]
        
        # Get timeline data
        timeline_data = db.query(
            func.date_trunc('hour', AttackEvent.timestamp).label('time_bucket'),
            func.count(AttackEvent.id).label('attack_count'),
            func.count(func.distinct(AttackEvent.source_ip)).label('unique_attackers'),
            func.avg(AttackEvent.anomaly_score).label('avg_anomaly_score'),
            func.count(func.filter(AttackEvent.id, AttackEvent.is_anomaly == True)).label('anomalies')
        ).filter(
            AttackEvent.timestamp >= time_threshold
        ).group_by('time_bucket').order_by('time_bucket').all()
        
        timeline = []
        for data in timeline_data:
            timeline.append({
                "timestamp": data.time_bucket.isoformat(),
                "attack_count": data.attack_count,
                "unique_attackers": data.unique_attackers,
                "avg_anomaly_score": float(data.avg_anomaly_score) if data.avg_anomaly_score else 0.0,
                "anomalies": data.anomalies
            })
        
        return {
            "timeline": timeline,
            "interval": interval,
            "time_range": f"{hours} hours",
            "total_points": len(timeline)
        }
        
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        return {"error": "Failed to fetch timeline data"}

@router.get("/geographic")
async def get_geographic_data(
    db: Session = Depends(get_db),
    hours: int = Query(24, ge=1, le=168)
):
    """Get geographic distribution of attacks"""
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Get geographic data
        geo_data = db.query(
            AttackEvent.country,
            AttackEvent.region,
            AttackEvent.city,
            AttackEvent.latitude,
            AttackEvent.longitude,
            func.count(AttackEvent.id).label('attack_count'),
            func.count(func.distinct(AttackEvent.source_ip)).label('unique_ips'),
            func.max(AttackEvent.severity).label('max_severity')
        ).filter(
            AttackEvent.timestamp >= time_threshold,
            AttackEvent.country.isnot(None)
        ).group_by(
            AttackEvent.country,
            AttackEvent.region, 
            AttackEvent.city,
            AttackEvent.latitude,
            AttackEvent.longitude
        ).all()
        
        locations = []
        for geo in geo_data:
            locations.append({
                "country": geo.country,
                "region": geo.region,
                "city": geo.city,
                "latitude": float(geo.latitude) if geo.latitude else None,
                "longitude": float(geo.longitude) if geo.longitude else None,
                "attack_count": geo.attack_count,
                "unique_ips": geo.unique_ips,
                "max_severity": geo.max_severity
            })
        
        return {
            "locations": locations,
            "total_locations": len(locations),
            "time_range": f"{hours} hours"
        }
        
    except Exception as e:
        logger.error(f"Error getting geographic data: {e}")
        return {"error": "Failed to fetch geographic data"}

@router.get("/patterns")
async def get_attack_patterns(
    db: Session = Depends(get_db),
    hours: int = Query(24, ge=1, le=168)
):
    """Get attack patterns and TTPs (Tactics, Techniques, Procedures)"""
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Common attack patterns
        patterns = db.query(
            AttackEvent.attack_type,
            func.count(AttackEvent.id).label('frequency'),
            func.avg(AttackEvent.confidence).label('avg_confidence'),
            func.string_agg(func.distinct(AttackEvent.endpoint), ',').label('common_endpoints')
        ).filter(
            AttackEvent.timestamp >= time_threshold,
            AttackEvent.attack_type != 'normal'
        ).group_by(AttackEvent.attack_type).order_by(desc('frequency')).all()
        
        # User agent patterns
        user_agent_patterns = db.query(
            func.substring(AttackEvent.user_agent, 1, 50).label('user_agent_short'),
            func.count(AttackEvent.id).label('frequency')
        ).filter(
            AttackEvent.timestamp >= time_threshold
        ).group_by('user_agent_short').order_by(desc('frequency')).limit(10).all()
        
        # Time-based patterns (hour of day)
        hourly_patterns = db.query(
            func.extract('hour', AttackEvent.timestamp).label('hour'),
            func.count(AttackEvent.id).label('attack_count')
        ).filter(
            AttackEvent.timestamp >= time_threshold
        ).group_by('hour').order_by('hour').all()
        
        pattern_analysis = {
            "attack_types": [
                {
                    "type": p.attack_type,
                    "frequency": p.frequency,
                    "avg_confidence": float(p.avg_confidence) if p.avg_confidence else 0.0,
                    "common_endpoints": p.common_endpoints.split(',')[:5] if p.common_endpoints else []
                }
                for p in patterns
            ],
            "user_agents": [
                {
                    "user_agent": ua.user_agent_short,
                    "frequency": ua.frequency
                }
                for ua in user_agent_patterns
            ],
            "hourly_distribution": [
                {
                    "hour": int(h.hour),
                    "attack_count": h.attack_count
                }
                for h in hourly_patterns
            ]
        }
        
        return pattern_analysis
        
    except Exception as e:
        logger.error(f"Error getting attack patterns: {e}")
        return {"error": "Failed to fetch attack patterns"}

@router.get("/alerts")
async def get_security_alerts(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500)
):
    """Get security alerts and incidents"""
    try:
        query = db.query(SecurityAlert)
        
        # Apply filters
        if status:
            query = query.filter(SecurityAlert.status == status)
        if severity:
            query = query.filter(SecurityAlert.severity == severity)
        
        # Get alerts
        alerts = query.order_by(desc(SecurityAlert.timestamp)).limit(limit).all()
        
        alert_list = []
        for alert in alerts:
            alert_dict = {
                "id": alert.id,
                "alert_id": alert.alert_id,
                "timestamp": alert.timestamp.isoformat(),
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "description": alert.description,
                "source_ip": alert.source_ip,
                "affected_endpoint": alert.affected_endpoint,
                "confidence": alert.confidence,
                "status": alert.status,
                "assigned_to": alert.assigned_to
            }
            alert_list.append(alert_dict)
        
        return {
            "alerts": alert_list,
            "total_alerts": len(alert_list),
            "filters": {
                "status": status,
                "severity": severity
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return {"error": "Failed to fetch security alerts"}
