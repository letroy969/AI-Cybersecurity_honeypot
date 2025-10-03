"""
Simplified AI Cybersecurity Honeypot - Demo Version
Runs without database dependencies for quick testing
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import time
import random
import json
from datetime import datetime
from typing import Dict, Any, List

app = FastAPI(
    title="AI Cybersecurity Honeypot - Demo",
    description="Educational security research platform (Demo Version)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
attacks_db = []
attackers_db = {}

@app.get("/overview", response_class=HTMLResponse)
async def system_overview():
    """System overview and navigation page"""
    overview_path = "../system_overview.html"
    try:
        with open(overview_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Overview page not found</h1><p><a href='/'>Go to main page</a></p>", status_code=404)

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AI Cybersecurity Honeypot API - Demo Version",
        "version": "1.0.0",
        "status": "operational",
        "warning": "⚠️ EDUCATIONAL USE ONLY - DEMO VERSION",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "honeypots": "/honeypots",
            "analytics": "/analytics",
            "attacks": "/attacks",
            "overview": "/overview"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Cybersecurity Honeypot API - Demo",
        "version": "1.0.0"
    }

@app.get("/honeypots/login", response_class=HTMLResponse)
async def fake_login_page():
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
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #856404; }
        </style>
    </head>
    <body>
        <div class="login-form">
            <h2>Company Portal Login</h2>
            <div class="warning">
                <strong>⚠️ HONEYPOT WARNING:</strong> This is a simulated login page for educational purposes only.
            </div>
            <form action="/honeypots/login" method="POST">
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
            <p style="margin-top: 20px; font-size: 12px; color: #666;">
                Demo credentials: admin/admin123, user/password<br>
                ⚠️ This is a honeypot - DO NOT use real credentials
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/honeypots/login")
async def fake_login_submit(request: Request):
    """Handle fake login attempts"""
    try:
        form_data = await request.form()
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        
        # Get client info
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Simulate login processing
        import asyncio
        await asyncio.sleep(0.5)
        
        # Check against fake credentials
        valid_credentials = {
            "admin": "admin123",
            "user": "password",
            "test": "test"
        }
        
        is_valid = username in valid_credentials and valid_credentials[username] == password
        
        # Record attack
        attack = {
            "id": len(attacks_db) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "source_ip": client_ip,
            "user_agent": user_agent,
            "method": "POST",
            "endpoint": "/honeypots/login",
            "attack_type": "brute_force" if not is_valid else "credential_theft",
            "severity": "high" if not is_valid else "medium",
            "confidence": 0.8 if not is_valid else 0.6,
            "anomaly_score": random.uniform(0.6, 0.9) if not is_valid else random.uniform(0.3, 0.5),
            "is_anomaly": not is_valid,
            "username": username,
            "success": is_valid
        }
        
        attacks_db.append(attack)
        
        if is_valid:
            return JSONResponse(
                status_code=302,
                headers={"Location": "/honeypots/dashboard"},
                content={"message": "Login successful", "redirect": "/dashboard"}
            )
        else:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Invalid credentials",
                    "message": "Username or password is incorrect",
                    "attack_detected": True
                }
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )

@app.get("/honeypots/sql", response_class=HTMLResponse)
async def fake_sql_interface(request: Request, query: str = ""):
    """Professional SQL database interface honeypot"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Analyze for SQL injection
    sql_patterns = [
        "union", "select", "insert", "update", "delete", "drop", "create",
        "alter", "exec", "execute", "script", "javascript", "vbscript",
        "onload", "onerror", "onclick", "or 1=1", "and 1=1", "'; drop",
        "admin'--", "' or '1'='1", "1' or '1'='1", "1' or 1=1--"
    ]
    
    attack_detected = any(pattern.lower() in query.lower() for pattern in sql_patterns)
    attack_type = "sql_injection" if attack_detected else None
    
    # Record the attack
    attack = {
        "id": len(attacks_db) + 1,
        "timestamp": datetime.utcnow().isoformat(),
        "source_ip": client_ip,
        "user_agent": user_agent,
        "method": "GET",
        "endpoint": "/honeypots/sql",
        "query": query,
        "attack_type": attack_type,
        "severity": "high" if attack_detected else "low",
        "confidence": 0.9 if attack_detected else 0.1,
        "anomaly_score": random.uniform(0.8, 0.95) if attack_detected else random.uniform(0.1, 0.3),
        "is_anomaly": attack_detected,
    }
    attacks_db.append(attack)
    
    # Generate fake SQL results for demonstration
    fake_results = []
    if attack_detected and "union" in query.lower() and "select" in query.lower():
        fake_results = [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "admin", "password": "5f4dcc3b5aa765d61d8327deb882cf99"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "role": "user", "password": "098f6bcd4621d373cade4e832627b4f6"},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "role": "user", "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"},
        ]
    
    # Professional SQL Interface HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Database Management System - SQL Interface</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                background: linear-gradient(135deg, #0f1724 0%, #1e293b 100%);
                color: #ffffff;
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(30, 41, 59, 0.95);
                border-radius: 15px;
                border: 1px solid #374151;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(90deg, #1e293b 0%, #374151 100%);
                padding: 25px 30px;
                border-bottom: 2px solid #ef4444;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .header h1 {{
                color: #ef4444;
                font-size: 1.8rem;
                font-weight: bold;
                text-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
            }}
            
            .header .status {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .status-indicator {{
                width: 12px;
                height: 12px;
                background: #10b981;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
                100% {{ opacity: 1; }}
            }}
            
            .warning-banner {{
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid #ef4444;
                padding: 15px 30px;
                text-align: center;
                color: #ef4444;
                font-weight: bold;
            }}
            
            .main-content {{
                padding: 30px;
            }}
            
            .sql-interface {{
                background: rgba(15, 23, 36, 0.9);
                border: 1px solid #374151;
                border-radius: 10px;
                padding: 25px;
                margin-bottom: 30px;
            }}
            
            .sql-title {{
                color: #f59e0b;
                font-size: 1.3rem;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .query-form {{
                margin-bottom: 25px;
            }}
            
            .query-input {{
                width: 100%;
                background: rgba(30, 41, 59, 0.9);
                border: 1px solid #4b5563;
                border-radius: 8px;
                padding: 15px;
                color: #ffffff;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                resize: vertical;
                min-height: 100px;
            }}
            
            .query-input:focus {{
                outline: none;
                border-color: #ef4444;
                box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
            }}
            
            .execute-btn {{
                background: #ef4444;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1rem;
                font-weight: 600;
                transition: all 0.3s ease;
                margin-top: 15px;
            }}
            
            .execute-btn:hover {{
                background: #dc2626;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(239, 68, 68, 0.3);
            }}
            
            .results-section {{
                margin-top: 25px;
            }}
            
            .results-table {{
                width: 100%;
                border-collapse: collapse;
                background: rgba(15, 23, 36, 0.9);
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid #374151;
            }}
            
            .results-table th {{
                background: #374151;
                color: #f59e0b;
                padding: 15px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #ef4444;
            }}
            
            .results-table td {{
                padding: 12px 15px;
                border-bottom: 1px solid #374151;
                color: #e5e7eb;
            }}
            
            .results-table tr:hover {{
                background: rgba(239, 68, 68, 0.05);
            }}
            
            .attack-alert {{
                background: rgba(239, 68, 68, 0.1);
                border: 2px solid #ef4444;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                text-align: center;
            }}
            
            .attack-alert h3 {{
                color: #ef4444;
                margin-bottom: 10px;
                font-size: 1.2rem;
            }}
            
            .attack-alert p {{
                color: #94a3b8;
                margin-bottom: 5px;
            }}
            
            .info-section {{
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid #3b82f6;
                border-radius: 10px;
                padding: 20px;
                margin-top: 20px;
            }}
            
            .info-section h3 {{
                color: #3b82f6;
                margin-bottom: 15px;
                font-size: 1.1rem;
            }}
            
            .info-section ul {{
                color: #94a3b8;
                margin-left: 20px;
                line-height: 1.6;
            }}
            
            .info-section li {{
                margin-bottom: 5px;
            }}
            
            .footer {{
                text-align: center;
                padding: 20px;
                color: #6b7280;
                border-top: 1px solid #374151;
                background: rgba(15, 23, 36, 0.9);
            }}
            
            .footer a {{
                color: #ef4444;
                text-decoration: none;
            }}
            
            .footer a:hover {{
                text-decoration: underline;
            }}
            
            @media (max-width: 768px) {{
                .header {{
                    flex-direction: column;
                    gap: 15px;
                    text-align: center;
                }}
                
                .main-content {{
                    padding: 20px;
                }}
                
                .results-table {{
                    font-size: 0.9rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🗄️ Database Management System</h1>
                <div class="status">
                    <span class="status-indicator"></span>
                    <span>Connected</span>
                </div>
            </div>
            
            <div class="warning-banner">
                ⚠️ HONEYPOT WARNING: This is a simulated SQL interface for educational purposes only.
            </div>
            
            <div class="main-content">
                <div class="sql-interface">
                    <h2 class="sql-title">
                        <span>💻</span>
                        SQL Query Interface
                    </h2>
                    
                    <div class="query-form">
                        <form method="GET">
                            <textarea 
                                name="query" 
                                class="query-input" 
                                placeholder="Enter your SQL query here...&#10;Example: SELECT * FROM users&#10;Example: 1 UNION SELECT * FROM users"
                            >{query}</textarea>
                            <button type="submit" class="execute-btn">▶️ Execute Query</button>
                        </form>
                    </div>
    """
    
    if query:
        html_content += """
                    <div class="results-section">
        """
        
        if attack_detected:
            html_content += f"""
                        <div class="attack-alert">
                            <h3>🚨 SQL Injection Attack Detected!</h3>
                            <p><strong>Query:</strong> {query}</p>
                            <p><strong>Attack Type:</strong> SQL Injection</p>
                            <p><strong>Severity:</strong> High</p>
                            <p><strong>Confidence:</strong> 90%</p>
                            <p><strong>Timestamp:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                        
                        <h3 style="color: #f59e0b; margin: 20px 0 15px 0;">📊 Query Results</h3>
                        <table class="results-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Password Hash</th>
                                </tr>
                            </thead>
                            <tbody>
            """
            
            for row in fake_results:
                html_content += f"""
                                <tr>
                                    <td>{row['id']}</td>
                                    <td>{row['name']}</td>
                                    <td>{row['email']}</td>
                                    <td>{row['role']}</td>
                                    <td style="font-family: monospace; font-size: 0.8rem;">{row['password']}</td>
                                </tr>
                """
            
            html_content += """
                            </tbody>
                        </table>
                        <p style="color: #94a3b8; margin-top: 15px; font-style: italic;">
                            ⚠️ This data was extracted using SQL injection - this would be a critical security vulnerability!
                        </p>
            """
        else:
            html_content += f"""
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 10px; padding: 20px; text-align: center;">
                            <h3 style="color: #10b981; margin-bottom: 10px;">✅ Query Executed Successfully</h3>
                            <p style="color: #94a3b8;"><strong>Query:</strong> {query}</p>
                            <p style="color: #94a3b8;">No malicious patterns detected.</p>
                        </div>
            """
        
        html_content += """
                    </div>
        """
    
    html_content += """
                    <div class="info-section">
                        <h3>ℹ️ About This Interface</h3>
                        <ul>
                            <li>This is a simulated SQL database interface for educational purposes</li>
                            <li>Try SQL injection attacks like: <code>1 UNION SELECT * FROM users</code></li>
                            <li>Common injection patterns: UNION, SELECT, INSERT, UPDATE, DELETE</li>
                            <li>All attacks are logged and analyzed for security research</li>
                            <li>No real data is accessed or modified</li>
                        </ul>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <p style="color: #6b7280; margin-bottom: 15px;">
                        🛡️ AI Cybersecurity Honeypot - Educational Security Research Platform
                    </p>
                    <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                        <a href="/honeypots/login" style="color: #ef4444;">Login Honeypot</a>
                        <a href="/honeypots/file" style="color: #ef4444;">File Honeypot</a>
                        <a href="/analytics-page" style="color: #ef4444;">Analytics</a>
                        <a href="/overview" style="color: #ef4444;">System Overview</a>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>⚠️ Educational Use Only - Do not use real credentials or sensitive data</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/honeypots/dashboard", response_class=HTMLResponse)
async def fake_dashboard(request: Request):
    """Simulate an admin dashboard"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Record dashboard access
    attack = {
        "id": len(attacks_db) + 1,
        "timestamp": datetime.utcnow().isoformat(),
        "source_ip": client_ip,
        "user_agent": user_agent,
        "method": "GET",
        "endpoint": "/honeypots/dashboard",
        "attack_type": "dashboard_access",
        "severity": "medium",
        "confidence": 0.7,
        "anomaly_score": random.uniform(0.4, 0.6),
        "is_anomaly": True,
    }
    attacks_db.append(attack)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - Honeypot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
            .dashboard { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto; }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #856404; }
            .section { margin-bottom: 30px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #f8f9fa; }
            .success { color: #28a745; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <h1>🛡️ Admin Dashboard - Honeypot</h1>
            <div class="warning">
                <strong>⚠️ HONEYPOT WARNING:</strong> This is a simulated admin dashboard for educational purposes only.
                <br><strong>🎯 Attack Detected:</strong> Dashboard access has been logged as a security event.
            </div>
            
            <div class="section">
                <h2>📊 System Overview</h2>
                <p><strong>Status:</strong> <span class="success">Operational</span></p>
                <p><strong>Total Attacks Logged:</strong> """ + str(len(attacks_db)) + """</p>
                <p><strong>Your IP:</strong> """ + client_ip + """</p>
                <p><strong>Access Time:</strong> """ + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            </div>
            
            <div class="section">
                <h2>🔐 Available Honeypot Endpoints</h2>
                <ul>
                    <li><a href="/honeypots/login">Login Portal</a> - Brute force detection</li>
                    <li><a href="/honeypots/sql">SQL Interface</a> - SQL injection detection</li>
                    <li><a href="/honeypots/file">File Access</a> - Directory traversal detection</li>
                    <li><a href="/analytics">Analytics API</a> - View attack statistics</li>
                    <li><a href="/attacks">Attack Logs</a> - Recent security events</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>🎯 Test Attack Examples</h2>
                <p>Try these URLs to test the honeypot:</p>
                <ul>
                    <li><code>/honeypots/sql?query=1 UNION SELECT * FROM users</code></li>
                    <li><code>/honeypots/file?path=../../../etc/passwd</code></li>
                    <li><code>/generate-attacks?count=10</code></li>
                </ul>
            </div>
            
            <div class="section">
                <h2>📈 View Analytics</h2>
                <p><a href="/analytics" target="_blank">📊 Open Analytics Dashboard</a></p>
                <p><a href="/attacks" target="_blank">📋 View Recent Attacks</a></p>
                <p><a href="/docs" target="_blank">📚 API Documentation</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/honeypots/file", response_class=HTMLResponse)
async def fake_file_access(request: Request, path: str = ""):
    """Simulate file access vulnerabilities"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Analyze for directory traversal
    is_traversal = any(pattern in path.lower() for pattern in ["../", "..\\", "/etc/passwd", "/windows/system32"])
    
    attack = {
        "id": len(attacks_db) + 1,
        "timestamp": datetime.utcnow().isoformat(),
        "source_ip": client_ip,
        "user_agent": user_agent,
        "method": "GET",
        "endpoint": "/honeypots/file",
        "attack_type": "directory_traversal" if is_traversal else "normal",
        "severity": "critical" if is_traversal else "low",
        "confidence": 0.9 if is_traversal else 0.1,
        "anomaly_score": random.uniform(0.85, 0.95) if is_traversal else random.uniform(0.1, 0.3),
        "is_anomaly": is_traversal,
        "path": path
    }
    
    attacks_db.append(attack)
    
    if path:
        fake_files = {
            "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\nbin:x:1:1:bin:/bin:/sbin/nologin",
            "/etc/hosts": "127.0.0.1 localhost\n::1 localhost",
            "/windows/system32/drivers/etc/hosts": "127.0.0.1 localhost"
        }
        
        content = fake_files.get(path, "File not found or access denied")
        
        # Create HTML response for file access
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>File Access - Honeypot</title>
            <style>
                body {{ font-family: monospace; background: #0f1724; color: #fff; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .header {{ background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .warning {{ background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .file-content {{ background: #1e293b; padding: 20px; border-radius: 8px; white-space: pre-wrap; font-family: monospace; }}
                .attack-alert {{ background: rgba(239, 68, 68, 0.2); border: 2px solid #ef4444; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; }}
                .nav {{ text-align: center; margin-top: 30px; }}
                .nav a {{ color: #ef4444; text-decoration: none; margin: 0 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📁 File System Browser</h1>
                    <p>⚠️ HONEYPOT WARNING: Educational use only</p>
                </div>
                
                <form method="GET" style="margin-bottom: 20px;">
                    <input type="text" name="path" placeholder="Enter file path..." value="{path}" style="width: 70%; padding: 10px; background: #1e293b; border: 1px solid #374151; color: #fff; border-radius: 5px;">
                    <button type="submit" style="padding: 10px 20px; background: #ef4444; color: white; border: none; border-radius: 5px; margin-left: 10px;">Access File</button>
                </form>
                
                <div style="margin-bottom: 20px;">
                    <strong>Quick Test:</strong>
                    <a href="?path=/etc/passwd" style="color: #ef4444; margin: 0 5px;">/etc/passwd</a>
                    <a href="?path=../../../etc/passwd" style="color: #ef4444; margin: 0 5px;">../../../etc/passwd</a>
                    <a href="?path=/windows/system32/hosts" style="color: #ef4444; margin: 0 5px;">/windows/system32/hosts</a>
                </div>
        """
        
        if is_traversal:
            html_content += f"""
                <div class="attack-alert">
                    <h3>🚨 Directory Traversal Attack Detected!</h3>
                    <p><strong>Path:</strong> {path}</p>
                    <p><strong>Attack Type:</strong> Directory Traversal</p>
                    <p><strong>Severity:</strong> Critical</p>
                </div>
            """
        
        html_content += f"""
                <h3>📄 File Content:</h3>
                <div class="file-content">{content}</div>
                
                <div class="nav">
                    <a href="/honeypots/login">Login Honeypot</a>
                    <a href="/honeypots/sql">SQL Honeypot</a>
                    <a href="/analytics-page">Analytics</a>
                    <a href="/overview">System Overview</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
    else:
        # Create HTML response for no path
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>File Access - Honeypot</title>
            <style>
                body { font-family: monospace; background: #0f1724; color: #fff; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .warning { background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; padding: 15px; border-radius: 8px; margin: 20px 0; }
                .info { background: #1e293b; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .nav { text-align: center; margin-top: 30px; }
                .nav a { color: #ef4444; text-decoration: none; margin: 0 10px; }
                .example { background: #374151; padding: 10px; border-radius: 5px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📁 File System Browser</h1>
                    <p>⚠️ HONEYPOT WARNING: Educational use only</p>
                </div>
                
                <div class="warning">
                    <strong>⚠️ This interface is intentionally vulnerable for demonstration</strong>
                </div>
                
                <form method="GET" style="margin-bottom: 20px;">
                    <input type="text" name="path" placeholder="Enter file path..." style="width: 70%; padding: 10px; background: #1e293b; border: 1px solid #374151; color: #fff; border-radius: 5px;">
                    <button type="submit" style="padding: 10px 20px; background: #ef4444; color: white; border: none; border-radius: 5px; margin-left: 10px;">Access File</button>
                </form>
                
                <div class="info">
                    <h3>📋 Test Examples:</h3>
                    <div class="example">
                        <strong>Normal file:</strong> <a href="?path=/etc/hosts" style="color: #ef4444;">/etc/hosts</a>
                    </div>
                    <div class="example">
                        <strong>Directory traversal:</strong> <a href="?path=../../../etc/passwd" style="color: #ef4444;">../../../etc/passwd</a>
                    </div>
                    <div class="example">
                        <strong>Windows path:</strong> <a href="?path=/windows/system32/hosts" style="color: #ef4444;">/windows/system32/hosts</a>
                    </div>
                </div>
                
                <div class="nav">
                    <a href="/honeypots/login">Login Honeypot</a>
                    <a href="/honeypots/sql">SQL Honeypot</a>
                    <a href="/analytics-page">Analytics</a>
                    <a href="/overview">System Overview</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)

@app.get("/analytics-page", response_class=HTMLResponse)
async def analytics_page():
    """HTML analytics dashboard page"""
    total_attacks = len(attacks_db)
    unique_attackers = len(set(attack["source_ip"] for attack in attacks_db))
    anomalies = len([a for a in attacks_db if a["is_anomaly"]])
    
    # Attack types breakdown
    attack_types = {}
    severity_breakdown = {}
    for attack in attacks_db:
        attack_type = attack["attack_type"]
        severity = attack["severity"]
        attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
        severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
    
    # Recent attacks for display
    recent_attacks = attacks_db[-10:] if attacks_db else []
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security Analytics Dashboard</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #0f1724 0%, #1e293b 100%);
                color: #ffffff;
                min-height: 100vh;
            }}
            .container {{ 
                max-width: 1200px; 
                margin: 0 auto; 
            }}
            .header {{ 
                text-align: center; 
                margin-bottom: 30px; 
            }}
            .header h1 {{ 
                color: #ef4444; 
                margin: 0; 
                font-size: 2.5rem;
                text-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
            }}
            .header p {{ 
                color: #94a3b8; 
                margin: 10px 0 0 0;
                font-size: 1.1rem;
            }}
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin-bottom: 30px; 
            }}
            .stat-card {{ 
                background: rgba(30, 41, 59, 0.8); 
                padding: 25px; 
                border-radius: 12px; 
                border: 1px solid #374151;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                transition: transform 0.3s ease;
            }}
            .stat-card:hover {{ 
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0, 0, 0, 0.4);
            }}
            .stat-number {{ 
                font-size: 2.5rem; 
                font-weight: bold; 
                color: #ef4444; 
                margin: 0;
                text-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
            }}
            .stat-label {{ 
                color: #94a3b8; 
                font-size: 1rem; 
                margin: 5px 0 0 0;
            }}
            .charts-grid {{ 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 20px; 
                margin-bottom: 30px; 
            }}
            .chart-card {{ 
                background: rgba(30, 41, 59, 0.8); 
                padding: 25px; 
                border-radius: 12px; 
                border: 1px solid #374151;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }}
            .chart-title {{ 
                color: #f59e0b; 
                font-size: 1.3rem; 
                margin: 0 0 20px 0;
                font-weight: 600;
            }}
            .attack-type {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                padding: 10px 0; 
                border-bottom: 1px solid #374151;
            }}
            .attack-type:last-child {{ 
                border-bottom: none; 
            }}
            .attack-name {{ 
                color: #ffffff; 
                font-weight: 500;
            }}
            .attack-count {{ 
                color: #ef4444; 
                font-weight: bold;
                background: rgba(239, 68, 68, 0.1);
                padding: 5px 10px;
                border-radius: 6px;
            }}
            .severity-item {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                padding: 10px 0; 
                border-bottom: 1px solid #374151;
            }}
            .severity-item:last-child {{ 
                border-bottom: none; 
            }}
            .severity-name {{ 
                color: #ffffff; 
                font-weight: 500;
                text-transform: capitalize;
            }}
            .severity-count {{ 
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 6px;
            }}
            .critical {{ color: #ef4444; background: rgba(239, 68, 68, 0.1); }}
            .high {{ color: #f59e0b; background: rgba(245, 158, 11, 0.1); }}
            .medium {{ color: #3b82f6; background: rgba(59, 130, 246, 0.1); }}
            .low {{ color: #10b981; background: rgba(16, 185, 129, 0.1); }}
            .recent-attacks {{ 
                background: rgba(30, 41, 59, 0.8); 
                padding: 25px; 
                border-radius: 12px; 
                border: 1px solid #374151;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }}
            .attack-item {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                padding: 15px 0; 
                border-bottom: 1px solid #374151;
            }}
            .attack-item:last-child {{ 
                border-bottom: none; 
            }}
            .attack-info {{ 
                flex: 1; 
            }}
            .attack-type-badge {{ 
                display: inline-block; 
                padding: 4px 8px; 
                border-radius: 4px; 
                font-size: 0.8rem; 
                font-weight: bold; 
                margin-right: 10px;
            }}
            .attack-time {{ 
                color: #94a3b8; 
                font-size: 0.9rem; 
                margin-top: 5px;
            }}
            .attack-ip {{ 
                color: #f59e0b; 
                font-family: monospace; 
                font-weight: bold;
            }}
            .refresh-btn {{ 
                background: #ef4444; 
                color: white; 
                border: none; 
                padding: 12px 24px; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 1rem; 
                font-weight: 600;
                transition: background 0.3s ease;
                margin: 20px 0;
            }}
            .refresh-btn:hover {{ 
                background: #dc2626; 
            }}
            .warning-box {{ 
                background: rgba(239, 68, 68, 0.1); 
                border: 1px solid #ef4444; 
                padding: 15px; 
                border-radius: 8px; 
                margin-bottom: 20px;
                text-align: center;
            }}
            .warning-box strong {{ 
                color: #ef4444; 
            }}
            @media (max-width: 768px) {{
                .charts-grid {{ 
                    grid-template-columns: 1fr; 
                }}
                .stats-grid {{ 
                    grid-template-columns: 1fr; 
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ Security Analytics Dashboard</h1>
                <p>Real-time threat monitoring and analysis</p>
            </div>
            
            <div class="warning-box">
                <strong>⚠️ Educational Use Only:</strong> This is a simulated security dashboard for learning purposes.
            </div>
            
            <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh Data</button>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_attacks}</div>
                    <div class="stat-label">Total Attacks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{unique_attackers}</div>
                    <div class="stat-label">Unique Attackers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{anomalies}</div>
                    <div class="stat-label">Anomalies Detected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([a for a in attacks_db if a.get('severity') in ['high', 'critical']])}</div>
                    <div class="stat-label">High/Critical Threats</div>
                </div>
            </div>
            
            <div class="charts-grid">
                <div class="chart-card">
                    <h3 class="chart-title">🎯 Attack Types</h3>
                    <div class="attack-types">
    """
    
    for attack_type, count in attack_types.items():
        html_content += f"""
                        <div class="attack-type">
                            <span class="attack-name">{attack_type.replace('_', ' ').title()}</span>
                            <span class="attack-count">{count}</span>
                        </div>
        """
    
    html_content += f"""
                    </div>
                </div>
                
                <div class="chart-card">
                    <h3 class="chart-title">⚠️ Severity Distribution</h3>
                    <div class="severity-breakdown">
    """
    
    for severity, count in severity_breakdown.items():
        html_content += f"""
                        <div class="severity-item">
                            <span class="severity-name">{severity}</span>
                            <span class="severity-count {severity}">{count}</span>
                        </div>
        """
    
    html_content += f"""
                    </div>
                </div>
            </div>
            
            <div class="recent-attacks">
                <h3 class="chart-title">📋 Recent Security Events</h3>
                <div class="attacks-list">
    """
    
    if recent_attacks:
        for attack in reversed(recent_attacks):
            timestamp = attack.get('timestamp', '')[:19].replace('T', ' ')
            attack_type = attack.get('attack_type', 'unknown').replace('_', ' ').title()
            severity = attack.get('severity', 'unknown')
            source_ip = attack.get('source_ip', 'unknown')
            
            html_content += f"""
                    <div class="attack-item">
                        <div class="attack-info">
                            <span class="attack-type-badge {severity}">{attack_type}</span>
                            <span class="attack-ip">{source_ip}</span>
                            <div class="attack-time">{timestamp}</div>
                        </div>
                    </div>
            """
    else:
        html_content += """
                    <div style="text-align: center; color: #94a3b8; padding: 20px;">
                        No attacks detected yet. Try accessing the honeypot endpoints!
                    </div>
        """
    
    html_content += """
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px; color: #94a3b8;">
                <p>🛡️ AI Cybersecurity Honeypot - Educational Security Research Platform</p>
                <p>
                    <a href="/honeypots/login" style="color: #ef4444;">Login Honeypot</a> | 
                    <a href="/honeypots/sql" style="color: #ef4444;">SQL Honeypot</a> | 
                    <a href="/honeypots/file" style="color: #ef4444;">File Honeypot</a> | 
                    <a href="/docs" style="color: #ef4444;">API Docs</a>
                </p>
            </div>
        </div>
        
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(() => {{
                window.location.reload();
            }}, 30000);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/analytics")
async def get_analytics():
    """Get analytics data"""
    total_attacks = len(attacks_db)
    unique_attackers = len(set(attack["source_ip"] for attack in attacks_db))
    anomalies = len([a for a in attacks_db if a["is_anomaly"]])
    
    # Attack types breakdown
    attack_types = {}
    severity_breakdown = {}
    for attack in attacks_db:
        attack_type = attack["attack_type"]
        severity = attack["severity"]
        attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
        severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
    
    return {
        "total_attacks": total_attacks,
        "unique_attackers": unique_attackers,
        "anomalies_detected": anomalies,
        "active_alerts": len([a for a in attacks_db if a["severity"] in ["high", "critical"]]),
        "attack_types": attack_types,
        "severity_breakdown": severity_breakdown,
        "time_range": "24 hours",
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/attacks")
async def get_attacks(limit: int = 50):
    """Get recent attacks"""
    recent_attacks = attacks_db[-limit:] if attacks_db else []
    
    return {
        "attacks": recent_attacks,
        "total_count": len(attacks_db),
        "limit": limit
    }

@app.get("/generate-attacks")
async def generate_test_attacks(count: int = 10):
    """Generate test attacks for demonstration"""
    attack_types = ["sql_injection", "xss", "brute_force", "directory_traversal", "normal"]
    severities = ["low", "medium", "high", "critical"]
    
    for i in range(count):
        attack = {
            "id": len(attacks_db) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "source_ip": f"192.168.1.{random.randint(100, 200)}",
            "user_agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "sqlmap/1.0-dev (http://sqlmap.org)",
                "Mozilla/5.0 (compatible; Nikto/2.1.6)"
            ]),
            "method": random.choice(["GET", "POST"]),
            "endpoint": random.choice([
                "/honeypots/login",
                "/honeypots/sql",
                "/honeypots/file",
                "/honeypots/admin"
            ]),
            "attack_type": random.choice(attack_types),
            "severity": random.choice(severities),
            "confidence": random.uniform(0.1, 0.95),
            "anomaly_score": random.uniform(0.1, 0.95),
            "is_anomaly": random.choice([True, False])
        }
        attacks_db.append(attack)
    
    return {
        "message": f"Generated {count} test attacks",
        "total_attacks": len(attacks_db)
    }

if __name__ == "__main__":
    import uvicorn
    import asyncio
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)
