"""
Report generation endpoints for incident reports and analysis
"""

from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import os
from pathlib import Path

from database.connection import get_db
from database.models import AttackEvent, AttackerFingerprint, SecurityAlert

logger = logging.getLogger(__name__)
router = APIRouter()

# Report templates directory
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

@router.get("/generate")
async def generate_incident_report(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    report_type: str = Query("incident", regex="^(incident|threat_intel|summary)$"),
    hours: int = Query(24, ge=1, le=168),
    format: str = Query("html", regex="^(html|json|pdf)$")
):
    """Generate an incident report"""
    try:
        # Generate unique report ID
        report_id = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{report_type}"
        
        # Collect data for the report
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Get attack events
        attacks = db.query(AttackEvent).filter(
            AttackEvent.timestamp >= time_threshold
        ).order_by(desc(AttackEvent.timestamp)).all()
        
        # Get unique attackers
        attackers = db.query(
            AttackEvent.source_ip,
            func.count(AttackEvent.id).label('attack_count'),
            func.count(func.distinct(AttackEvent.endpoint)).label('unique_endpoints'),
            func.max(AttackEvent.severity).label('max_severity'),
            func.max(AttackEvent.timestamp).label('last_seen')
        ).filter(
            AttackEvent.timestamp >= time_threshold
        ).group_by(AttackEvent.source_ip).all()
        
        # Get alerts
        alerts = db.query(SecurityAlert).filter(
            SecurityAlert.timestamp >= time_threshold
        ).order_by(desc(SecurityAlert.timestamp)).all()
        
        # Generate report data
        report_data = {
            "report_id": report_id,
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "time_range": f"{hours} hours",
            "summary": {
                "total_attacks": len(attacks),
                "unique_attackers": len(attackers),
                "total_alerts": len(alerts),
                "critical_attacks": len([a for a in attacks if a.severity == "critical"]),
                "high_attacks": len([a for a in attacks if a.severity == "high"]),
                "anomalies_detected": len([a for a in attacks if a.is_anomaly])
            },
            "attack_types": {},
            "geographic_distribution": {},
            "top_attackers": [],
            "recent_alerts": [],
            "attack_timeline": []
        }
        
        # Analyze attack types
        attack_type_counts = {}
        for attack in attacks:
            attack_type = attack.attack_type or "unknown"
            attack_type_counts[attack_type] = attack_type_counts.get(attack_type, 0) + 1
        report_data["attack_types"] = attack_type_counts
        
        # Geographic distribution
        geo_counts = {}
        for attack in attacks:
            if attack.country:
                country = attack.country
                geo_counts[country] = geo_counts.get(country, 0) + 1
        report_data["geographic_distribution"] = geo_counts
        
        # Top attackers
        for attacker in attackers[:10]:
            report_data["top_attackers"].append({
                "source_ip": attacker.source_ip,
                "attack_count": attacker.attack_count,
                "unique_endpoints": attacker.unique_endpoints,
                "max_severity": attacker.max_severity,
                "last_seen": attacker.last_seen.isoformat() if attacker.last_seen else None
            })
        
        # Recent alerts
        for alert in alerts[:5]:
            report_data["recent_alerts"].append({
                "alert_id": alert.alert_id,
                "timestamp": alert.timestamp.isoformat(),
                "severity": alert.severity,
                "title": alert.title,
                "description": alert.description[:200] + "..." if len(alert.description) > 200 else alert.description
            })
        
        # Attack timeline (hourly)
        hourly_attacks = {}
        for attack in attacks:
            hour = attack.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_attacks[hour] = hourly_attacks.get(hour, 0) + 1
        
        for hour, count in sorted(hourly_attacks.items()):
            report_data["attack_timeline"].append({
                "timestamp": hour.isoformat(),
                "attack_count": count
            })
        
        # Save report based on format
        if format == "json":
            report_file = REPORTS_DIR / f"{report_id}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            return {
                "report_id": report_id,
                "file_path": str(report_file),
                "format": format,
                "status": "generated"
            }
        
        elif format == "html":
            html_content = generate_html_report(report_data)
            report_file = REPORTS_DIR / f"{report_id}.html"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                "report_id": report_id,
                "file_path": str(report_file),
                "format": format,
                "status": "generated",
                "preview": html_content[:500] + "..." if len(html_content) > 500 else html_content
            }
        
        else:  # PDF
            # For PDF generation, we'd need additional libraries like reportlab
            # For now, return JSON format
            return await generate_incident_report(
                background_tasks, db, report_type, hours, "json"
            )
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """Download a generated report"""
    try:
        # Look for report files
        report_files = list(REPORTS_DIR.glob(f"{report_id}.*"))
        
        if not report_files:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Return the first matching file
        report_file = report_files[0]
        
        if report_file.suffix == ".html":
            return HTMLResponse(
                content=report_file.read_text(encoding='utf-8'),
                headers={"Content-Disposition": f"attachment; filename={report_id}.html"}
            )
        elif report_file.suffix == ".json":
            return FileResponse(
                path=report_file,
                filename=f"{report_id}.json",
                media_type="application/json"
            )
        else:
            return FileResponse(
                path=report_file,
                filename=report_file.name
            )
        
    except Exception as e:
        logger.error(f"Error downloading report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to download report")

@router.get("/list")
async def list_reports():
    """List all available reports"""
    try:
        reports = []
        
        for report_file in REPORTS_DIR.glob("report_*"):
            stat = report_file.stat()
            reports.append({
                "report_id": report_file.stem,
                "format": report_file.suffix[1:],
                "size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "reports": reports,
            "total_reports": len(reports)
        }
        
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        return {"error": "Failed to list reports"}

def generate_html_report(report_data: Dict[str, Any]) -> str:
    """Generate HTML report content"""
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security Incident Report - {report_data['report_id']}</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: #f5f5f5; 
                color: #333;
            }}
            .report-container {{ 
                background: white; 
                padding: 40px; 
                border-radius: 8px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{ 
                border-bottom: 3px solid #dc3545; 
                padding-bottom: 20px; 
                margin-bottom: 30px;
            }}
            .header h1 {{ 
                color: #dc3545; 
                margin: 0; 
                font-size: 28px;
            }}
            .header .meta {{ 
                color: #666; 
                margin-top: 10px; 
                font-size: 14px;
            }}
            .section {{ 
                margin-bottom: 30px; 
                padding: 20px; 
                background: #f8f9fa; 
                border-radius: 5px;
                border-left: 4px solid #007bff;
            }}
            .section h2 {{ 
                color: #007bff; 
                margin-top: 0; 
                font-size: 20px;
            }}
            .summary-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 15px; 
                margin-top: 15px;
            }}
            .summary-card {{ 
                background: white; 
                padding: 15px; 
                border-radius: 5px; 
                text-align: center;
                border: 1px solid #dee2e6;
            }}
            .summary-card .number {{ 
                font-size: 24px; 
                font-weight: bold; 
                color: #dc3545;
            }}
            .summary-card .label {{ 
                font-size: 12px; 
                color: #666; 
                margin-top: 5px;
            }}
            .critical {{ color: #dc3545; font-weight: bold; }}
            .high {{ color: #fd7e14; font-weight: bold; }}
            .medium {{ color: #ffc107; font-weight: bold; }}
            .low {{ color: #28a745; font-weight: bold; }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 15px;
                background: white;
            }}
            th, td {{ 
                border: 1px solid #dee2e6; 
                padding: 12px; 
                text-align: left;
            }}
            th {{ 
                background: #e9ecef; 
                font-weight: bold;
                color: #495057;
            }}
            .warning {{ 
                background: #fff3cd; 
                border: 1px solid #ffeaa7; 
                padding: 15px; 
                border-radius: 5px; 
                margin: 20px 0;
                color: #856404;
            }}
            .footer {{ 
                margin-top: 40px; 
                padding-top: 20px; 
                border-top: 1px solid #dee2e6; 
                text-align: center; 
                color: #666; 
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <div class="header">
                <h1>🛡️ Security Incident Report</h1>
                <div class="meta">
                    <strong>Report ID:</strong> {report_data['report_id']}<br>
                    <strong>Generated:</strong> {datetime.fromisoformat(report_data['generated_at']).strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                    <strong>Time Range:</strong> {report_data['time_range']}<br>
                    <strong>Report Type:</strong> {report_data['report_type'].title()}
                </div>
            </div>
            
            <div class="warning">
                <strong>⚠️ HONEYPOT REPORT:</strong> This report contains data from a simulated honeypot environment for educational purposes only. 
                Do not use this data for real security decisions.
            </div>
            
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="number">{report_data['summary']['total_attacks']}</div>
                        <div class="label">Total Attacks</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">{report_data['summary']['unique_attackers']}</div>
                        <div class="label">Unique Attackers</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">{report_data['summary']['critical_attacks']}</div>
                        <div class="label">Critical Attacks</div>
                    </div>
                    <div class="summary-card">
                        <div class="number">{report_data['summary']['anomalies_detected']}</div>
                        <div class="label">Anomalies Detected</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🎯 Attack Types Distribution</h2>
                <table>
                    <tr><th>Attack Type</th><th>Frequency</th><th>Percentage</th></tr>
    """
    
    total_attacks = report_data['summary']['total_attacks']
    for attack_type, count in sorted(report_data['attack_types'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_attacks * 100) if total_attacks > 0 else 0
        html_template += f"<tr><td>{attack_type.replace('_', ' ').title()}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>"
    
    html_template += """
                </table>
            </div>
            
            <div class="section">
                <h2>🌍 Geographic Distribution</h2>
                <table>
                    <tr><th>Country</th><th>Attack Count</th><th>Percentage</th></tr>
    """
    
    for country, count in sorted(report_data['geographic_distribution'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_attacks * 100) if total_attacks > 0 else 0
        html_template += f"<tr><td>{country}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>"
    
    html_template += """
                </table>
            </div>
            
            <div class="section">
                <h2>🎭 Top Attackers</h2>
                <table>
                    <tr><th>Source IP</th><th>Attack Count</th><th>Endpoints</th><th>Max Severity</th><th>Last Seen</th></tr>
    """
    
    for attacker in report_data['top_attackers']:
        severity_class = attacker['max_severity'].lower() if attacker['max_severity'] else 'unknown'
        html_template += f"""
        <tr>
            <td>{attacker['source_ip']}</td>
            <td>{attacker['attack_count']}</td>
            <td>{attacker['unique_endpoints']}</td>
            <td><span class="{severity_class}">{attacker['max_severity']}</span></td>
            <td>{attacker['last_seen'][:19] if attacker['last_seen'] else 'N/A'}</td>
        </tr>
        """
    
    html_template += """
                </table>
            </div>
            
            <div class="section">
                <h2>🚨 Recent Alerts</h2>
    """
    
    if report_data['recent_alerts']:
        html_template += """
                <table>
                    <tr><th>Alert ID</th><th>Timestamp</th><th>Severity</th><th>Title</th><th>Description</th></tr>
        """
        for alert in report_data['recent_alerts']:
            severity_class = alert['severity'].lower()
            html_template += f"""
            <tr>
                <td>{alert['alert_id']}</td>
                <td>{alert['timestamp'][:19]}</td>
                <td><span class="{severity_class}">{alert['severity']}</span></td>
                <td>{alert['title']}</td>
                <td>{alert['description']}</td>
            </tr>
            """
        html_template += "</table>"
    else:
        html_template += "<p>No recent alerts in the specified time range.</p>"
    
    html_template += """
            </div>
            
            <div class="footer">
                <p>This report was generated by the AI Cybersecurity Honeypot system for educational purposes.</p>
                <p>⚠️ <strong>Educational Use Only</strong> - Do not deploy honeypots to production environments without proper authorization.</p>
                <p>For questions or concerns, refer to the LEGAL.md documentation.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template
