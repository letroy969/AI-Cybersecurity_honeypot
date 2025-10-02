"""
Honeypot endpoints - Simulated vulnerable services to attract attackers
"""

from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import time
import json
import uuid
import logging
import asyncio
from datetime import datetime

from database.connection import get_db
from telemetry.ingestion import TelemetryIngestion
from ml.anomaly_detector import AnomalyDetector

logger = logging.getLogger(__name__)
router = APIRouter()

# Simulated credentials for login honeypot
FAKE_CREDENTIALS = {
    "admin": "admin123",
    "user": "password",
    "root": "root",
    "test": "test",
    "demo": "demo"
}

# Simulated vulnerable endpoints data
VULNERABLE_DATA = {
    "users": [
        {"id": 1, "username": "admin", "email": "admin@company.com", "role": "administrator"},
        {"id": 2, "username": "user1", "email": "user1@company.com", "role": "user"},
        {"id": 3, "username": "guest", "email": "guest@company.com", "role": "guest"}
    ],
    "products": [
        {"id": 1, "name": "Product A", "price": 99.99, "stock": 50},
        {"id": 2, "name": "Product B", "price": 199.99, "stock": 25},
        {"id": 3, "name": "Product C", "price": 299.99, "stock": 10}
    ],
    "config": {
        "database_host": "localhost",
        "database_password": "weak_password",
        "api_key": "sk-1234567890abcdef",
        "secret_token": "secret123"
    }
}

async def analyze_request(
    request: Request,
    response_data: Dict[str, Any],
    telemetry_service: TelemetryIngestion,
    anomaly_detector: AnomalyDetector
) -> Dict[str, Any]:
    """Analyze request for potential attacks"""
    try:
        # Extract request features
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        method = request.method
        url = str(request.url)
        
        # Analyze for common attack patterns
        attack_type = "normal"
        severity = "low"
        confidence = 0.0
        
        # Check for SQL injection attempts
        if any(pattern in url.lower() for pattern in ["union", "select", "drop", "insert", "delete", "update"]):
            attack_type = "sql_injection"
            severity = "high"
            confidence = 0.8
        
        # Check for XSS attempts
        elif any(pattern in url.lower() for pattern in ["<script>", "javascript:", "onerror=", "onload="]):
            attack_type = "xss"
            severity = "medium"
            confidence = 0.7
        
        # Check for directory traversal
        elif any(pattern in url.lower() for pattern in ["../", "..\\", "/etc/passwd", "/windows/system32"]):
            attack_type = "directory_traversal"
            severity = "high"
            confidence = 0.9
        
        # Check for suspicious user agents
        elif any(pattern in user_agent.lower() for pattern in ["sqlmap", "nikto", "nmap", "burp", "zap"]):
            attack_type = "automated_tool"
            severity = "medium"
            confidence = 0.6
        
        # Check for brute force patterns (multiple rapid requests)
        # This would need session tracking in a real implementation
        
        # Get ML anomaly score
        anomaly_score = await anomaly_detector.predict_anomaly({
            "url": url,
            "user_agent": user_agent,
            "method": method,
            "headers": dict(request.headers)
        })
        
        # Record telemetry
        await telemetry_service.record_attack_event(
            source_ip=client_ip,
            user_agent=user_agent,
            method=method,
            endpoint=request.url.path,
            url=url,
            headers=dict(request.headers),
            query_params=dict(request.query_params),
            body=await request.body() if request.method in ["POST", "PUT"] else None,
            status_code=200,
            response_time=0.0,
            attack_type=attack_type,
            severity=severity,
            confidence=confidence,
            anomaly_score=anomaly_score,
            is_anomaly=anomaly_score > 0.7,
            honeypot_type="web_application"
        )
        
        return {
            "attack_type": attack_type,
            "severity": severity,
            "confidence": confidence,
            "anomaly_score": anomaly_score,
            "is_anomaly": anomaly_score > 0.7
        }
        
    except Exception as e:
        logger.error(f"Error analyzing request: {e}")
        return {
            "attack_type": "unknown",
            "severity": "low",
            "confidence": 0.0,
            "anomaly_score": 0.0,
            "is_anomaly": False
        }

@router.get("/login", response_class=HTMLResponse)
async def fake_login_page(request: Request, background_tasks: BackgroundTasks):
    """Simulate a vulnerable login page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Company Portal - Login</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; background: #f5f5f5; }
            .login-form { background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 400px; margin: 0 auto; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 3px; box-sizing: border-box; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; width: 100%; }
            button:hover { background: #0056b3; }
            .error { color: red; margin-top: 10px; }
            .info { color: blue; margin-top: 10px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="login-form">
            <h2>Company Portal Login</h2>
            <form action="/api/honeypots/login" method="POST">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
            <div class="info">
                <p>Demo credentials: admin/admin123, user/password</p>
                <p>⚠️ This is a honeypot - DO NOT use real credentials</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Analyze the request in background
    background_tasks.add_task(analyze_request, request, {}, None, None)
    
    return HTMLResponse(content=html_content)

@router.post("/login")
async def fake_login_submit(request: Request, background_tasks: BackgroundTasks):
    """Handle fake login attempts"""
    form_data = await request.form()
    username = form_data.get("username", "")
    password = form_data.get("password", "")
    
    # Simulate login processing time
    await asyncio.sleep(0.5)
    
    # Check against fake credentials
    is_valid = username in FAKE_CREDENTIALS and FAKE_CREDENTIALS[username] == password
    
    # Determine attack type
    attack_type = "brute_force" if not is_valid else "credential_theft"
    severity = "medium" if not is_valid else "high"
    
    # Analyze request
    analysis = await analyze_request(request, {"login_attempt": True}, None, None)
    
    if is_valid:
        # Redirect to fake dashboard
        return JSONResponse(
            status_code=302,
            headers={"Location": "/api/honeypots/dashboard"},
            content={"message": "Login successful", "redirect": "/dashboard"}
        )
    else:
        # Show error message
        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid credentials",
                "message": "Username or password is incorrect",
                "attack_detected": analysis
            }
        )

@router.get("/dashboard", response_class=HTMLResponse)
async def fake_dashboard(request: Request):
    """Simulate an admin dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
            .dashboard { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .section { margin-bottom: 30px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #f8f9fa; }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <h1>Admin Dashboard</h1>
            <div class="warning">
                <strong>⚠️ HONEYPOT WARNING:</strong> This is a simulated dashboard for educational purposes only.
            </div>
            
            <div class="section">
                <h2>System Users</h2>
                <table>
                    <tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th></tr>
                    <tr><td>1</td><td>admin</td><td>admin@company.com</td><td>administrator</td></tr>
                    <tr><td>2</td><td>user1</td><td>user1@company.com</td><td>user</td></tr>
                    <tr><td>3</td><td>guest</td><td>guest@company.com</td><td>guest</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h2>System Configuration</h2>
                <p><strong>Database Host:</strong> localhost</p>
                <p><strong>API Key:</strong> sk-1234567890abcdef</p>
                <p><strong>Secret Token:</strong> secret123</p>
            </div>
            
            <div class="section">
                <h2>Available Endpoints</h2>
                <ul>
                    <li><a href="/api/honeypots/users">/api/honeypots/users</a> - User API</li>
                    <li><a href="/api/honeypots/products">/api/honeypots/products</a> - Product API</li>
                    <li><a href="/api/honeypots/config">/api/honeypots/config</a> - Configuration</li>
                    <li><a href="/api/honeypots/sql">/api/honeypots/sql</a> - SQL Query Interface</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Analyze the request
    await analyze_request(request, {"dashboard_access": True}, None, None)
    
    return HTMLResponse(content=html_content)

@router.get("/users")
async def fake_users_api(request: Request):
    """Simulate a vulnerable users API endpoint"""
    # Analyze request for attacks
    analysis = await analyze_request(request, {}, None, None)
    
    return JSONResponse(content={
        "users": VULNERABLE_DATA["users"],
        "total": len(VULNERABLE_DATA["users"]),
        "attack_analysis": analysis
    })

@router.get("/products")
async def fake_products_api(request: Request):
    """Simulate a vulnerable products API endpoint"""
    # Analyze request for attacks
    analysis = await analyze_request(request, {}, None, None)
    
    return JSONResponse(content={
        "products": VULNERABLE_DATA["products"],
        "total": len(VULNERABLE_DATA["products"]),
        "attack_analysis": analysis
    })

@router.get("/config")
async def fake_config_api(request: Request):
    """Simulate a vulnerable configuration endpoint"""
    # This is intentionally vulnerable to demonstrate configuration exposure
    analysis = await analyze_request(request, {}, None, None)
    
    return JSONResponse(content={
        "config": VULNERABLE_DATA["config"],
        "warning": "This endpoint exposes sensitive configuration data",
        "attack_analysis": analysis
    })

@router.get("/sql")
async def fake_sql_interface(request: Request, query: str = ""):
    """Simulate a vulnerable SQL query interface"""
    # This is extremely dangerous in real applications!
    analysis = await analyze_request(request, {"sql_query": query}, None, None)
    
    if query:
        # Simulate SQL execution (fake results)
        fake_results = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
        ]
        
        return JSONResponse(content={
            "query": query,
            "results": fake_results,
            "rows_affected": len(fake_results),
            "warning": "⚠️ SQL injection vulnerability detected!",
            "attack_analysis": analysis
        })
    else:
        return JSONResponse(content={
            "message": "SQL Query Interface",
            "usage": "Add ?query=SELECT * FROM users to execute SQL",
            "warning": "This interface is intentionally vulnerable for demonstration",
            "attack_analysis": analysis
        })

@router.get("/file")
async def fake_file_access(request: Request, path: str = ""):
    """Simulate file access vulnerabilities"""
    analysis = await analyze_request(request, {"file_path": path}, None, None)
    
    if path:
        # Simulate file content (fake)
        fake_files = {
            "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\nbin:x:1:1:bin:/bin:/sbin/nologin",
            "/etc/hosts": "127.0.0.1 localhost\n::1 localhost",
            "/windows/system32/drivers/etc/hosts": "127.0.0.1 localhost"
        }
        
        content = fake_files.get(path, "File not found or access denied")
        
        return JSONResponse(content={
            "path": path,
            "content": content,
            "warning": "⚠️ Directory traversal vulnerability detected!",
            "attack_analysis": analysis
        })
    else:
        return JSONResponse(content={
            "message": "File Access Interface",
            "usage": "Add ?path=/etc/passwd to access files",
            "warning": "This interface is intentionally vulnerable for demonstration",
            "attack_analysis": analysis
        })

@router.get("/admin")
async def fake_admin_panel(request: Request):
    """Simulate an admin panel with various vulnerabilities"""
    analysis = await analyze_request(request, {"admin_access": True}, None, None)
    
    return JSONResponse(content={
        "admin_panel": {
            "users": VULNERABLE_DATA["users"],
            "config": VULNERABLE_DATA["config"],
            "logs": [
                {"timestamp": "2025-01-01 10:00:00", "action": "login", "user": "admin", "ip": "192.168.1.100"},
                {"timestamp": "2025-01-01 10:01:00", "action": "config_change", "user": "admin", "ip": "192.168.1.100"},
                {"timestamp": "2025-01-01 10:02:00", "action": "user_created", "user": "admin", "ip": "192.168.1.100"}
            ]
        },
        "attack_analysis": analysis
    })

@router.get("/status")
async def honeypot_status():
    """Get honeypot system status"""
    return JSONResponse(content={
        "honeypot_status": "active",
        "endpoints": [
            "/login - Fake login page",
            "/dashboard - Admin dashboard",
            "/users - User API",
            "/products - Product API", 
            "/config - Configuration endpoint",
            "/sql - SQL query interface",
            "/file - File access interface",
            "/admin - Admin panel"
        ],
        "warning": "All endpoints are intentionally vulnerable for educational purposes",
        "legal_notice": "This is a honeypot for educational use only"
    })
