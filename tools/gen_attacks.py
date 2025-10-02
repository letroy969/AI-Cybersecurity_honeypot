#!/usr/bin/env python3
"""
Synthetic Attack Generator for AI Cybersecurity Honeypot
Generates realistic attack patterns for educational and testing purposes
"""

import asyncio
import aiohttp
import random
import argparse
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Synthetic IP addresses for testing
SYNTHETIC_IPS = [
    "192.168.1.100", "192.168.1.101", "192.168.1.102",
    "10.0.0.45", "10.0.0.46", "10.0.0.47",
    "172.16.0.78", "172.16.0.79", "172.16.0.80",
    "203.0.113.12", "203.0.113.13", "203.0.113.14",
    "198.51.100.34", "198.51.100.35", "198.51.100.36"
]

# Geographic data for synthetic attacks
COUNTRIES = [
    {"name": "United States", "flag": "🇺🇸", "ips": ["192.168.1.100", "192.168.1.101"]},
    {"name": "China", "flag": "🇨🇳", "ips": ["10.0.0.45", "10.0.0.46"]},
    {"name": "Russia", "flag": "🇷🇺", "ips": ["172.16.0.78", "172.16.0.79"]},
    {"name": "Germany", "flag": "🇩🇪", "ips": ["203.0.113.12", "203.0.113.13"]},
    {"name": "United Kingdom", "flag": "🇬🇧", "ips": ["198.51.100.34", "198.51.100.35"]},
    {"name": "Japan", "flag": "🇯🇵", "ips": ["203.0.113.14"]},
    {"name": "Brazil", "flag": "🇧🇷", "ips": ["172.16.0.80"]},
    {"name": "India", "flag": "🇮🇳", "ips": ["10.0.0.47"]},
]

# User agents for different attack types
USER_AGENTS = {
    "normal": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ],
    "sqlmap": [
        "sqlmap/1.0-dev (http://sqlmap.org)",
        "sqlmap/1.4.7 (http://sqlmap.org)",
        "sqlmap/1.5.2 (http://sqlmap.org)"
    ],
    "nikto": [
        "Mozilla/5.0 (compatible; Nikto/2.1.6)",
        "Mozilla/5.0 (compatible; Nikto/2.1.7)",
        "Mozilla/5.0 (compatible; Nikto/2.1.8)"
    ],
    "nmap": [
        "Mozilla/5.0 (compatible; Nmap Scripting Engine)",
        "Nmap Scripting Engine"
    ],
    "burp": [
        "Mozilla/5.0 (compatible; Burp Suite)",
        "Burp Suite Professional"
    ]
}

# Attack patterns
ATTACK_PATTERNS = {
    "sql_injection": [
        "/api/users?id=1 UNION SELECT * FROM users WHERE 1=1--",
        "/api/products?id=1' OR '1'='1",
        "/api/search?q=1'; DROP TABLE users; --",
        "/api/login?user=admin'--&pass=anything",
        "/api/data?id=1 AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
    ],
    "xss": [
        "/api/search?q=<script>alert('xss')</script>",
        "/api/comment?text=<img src=x onerror=alert('xss')>",
        "/api/feedback?message=javascript:alert('xss')",
        "/api/profile?name=<svg onload=alert('xss')>",
        "/api/post?content=<iframe src=javascript:alert('xss')></iframe>",
    ],
    "directory_traversal": [
        "/api/files/../../../etc/passwd",
        "/api/download/..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
        "/api/docs/....//....//....//etc/passwd",
        "/api/backup/../../../var/log/apache2/access.log",
        "/api/config/..%2F..%2F..%2Fetc%2Fshadow",
    ],
    "brute_force": [
        "/api/honeypots/login",
        "/api/auth/login",
        "/api/admin/login",
        "/api/user/login",
    ],
    "information_disclosure": [
        "/api/config",
        "/api/admin/config",
        "/api/system/info",
        "/api/debug/info",
        "/api/version",
        "/api/status",
    ],
    "automated_tool": [
        "/api/admin",
        "/api/admin/users",
        "/api/admin/config",
        "/api/test",
        "/api/health",
        "/api/metrics",
    ]
}

class SyntheticAttackGenerator:
    """Generate synthetic attack patterns for testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate_normal_traffic(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate normal web traffic"""
        attacks = []
        
        for i in range(count):
            country = random.choice(COUNTRIES)
            ip = random.choice(country["ips"])
            
            attack = {
                "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
                "source_ip": ip,
                "country": country["name"],
                "user_agent": random.choice(USER_AGENTS["normal"]),
                "method": random.choice(["GET", "POST"]),
                "endpoint": random.choice([
                    "/api/users", "/api/products", "/api/search", 
                    "/api/about", "/api/contact", "/api/help"
                ]),
                "attack_type": "normal",
                "severity": "low",
                "confidence": random.uniform(0.1, 0.3),
                "anomaly_score": random.uniform(0.1, 0.4),
            }
            attacks.append(attack)
        
        return attacks
    
    async def generate_sql_injection_attacks(self, count: int = 30) -> List[Dict[str, Any]]:
        """Generate SQL injection attacks"""
        attacks = []
        
        for i in range(count):
            country = random.choice(COUNTRIES)
            ip = random.choice(country["ips"])
            
            attack = {
                "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
                "source_ip": ip,
                "country": country["name"],
                "user_agent": random.choice(USER_AGENTS["sqlmap"] + USER_AGENTS["normal"]),
                "method": "GET",
                "endpoint": random.choice(ATTACK_PATTERNS["sql_injection"]),
                "attack_type": "sql_injection",
                "severity": random.choice(["high", "critical"]),
                "confidence": random.uniform(0.7, 0.95),
                "anomaly_score": random.uniform(0.6, 0.9),
            }
            attacks.append(attack)
        
        return attacks
    
    async def generate_xss_attacks(self, count: int = 25) -> List[Dict[str, Any]]:
        """Generate XSS attacks"""
        attacks = []
        
        for i in range(count):
            country = random.choice(COUNTRIES)
            ip = random.choice(country["ips"])
            
            attack = {
                "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
                "source_ip": ip,
                "country": country["name"],
                "user_agent": random.choice(USER_AGENTS["normal"]),
                "method": random.choice(["GET", "POST"]),
                "endpoint": random.choice(ATTACK_PATTERNS["xss"]),
                "attack_type": "xss",
                "severity": random.choice(["medium", "high"]),
                "confidence": random.uniform(0.6, 0.8),
                "anomaly_score": random.uniform(0.5, 0.8),
            }
            attacks.append(attack)
        
        return attacks
    
    async def generate_directory_traversal_attacks(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate directory traversal attacks"""
        attacks = []
        
        for i in range(count):
            country = random.choice(COUNTRIES)
            ip = random.choice(country["ips"])
            
            attack = {
                "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
                "source_ip": ip,
                "country": country["name"],
                "user_agent": random.choice(USER_AGENTS["nikto"] + USER_AGENTS["nmap"]),
                "method": "GET",
                "endpoint": random.choice(ATTACK_PATTERNS["directory_traversal"]),
                "attack_type": "directory_traversal",
                "severity": random.choice(["high", "critical"]),
                "confidence": random.uniform(0.8, 0.95),
                "anomaly_score": random.uniform(0.7, 0.9),
            }
            attacks.append(attack)
        
        return attacks
    
    async def generate_brute_force_attacks(self, count: int = 40) -> List[Dict[str, Any]]:
        """Generate brute force attacks"""
        attacks = []
        
        for i in range(count):
            country = random.choice(COUNTRIES)
            ip = random.choice(country["ips"])
            
            attack = {
                "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
                "source_ip": ip,
                "country": country["name"],
                "user_agent": random.choice(USER_AGENTS["normal"]),
                "method": "POST",
                "endpoint": random.choice(ATTACK_PATTERNS["brute_force"]),
                "attack_type": "brute_force",
                "severity": random.choice(["medium", "high"]),
                "confidence": random.uniform(0.5, 0.8),
                "anomaly_score": random.uniform(0.4, 0.7),
            }
            attacks.append(attack)
        
        return attacks
    
    async def generate_automated_tool_attacks(self, count: int = 35) -> List[Dict[str, Any]]:
        """Generate automated tool attacks"""
        attacks = []
        
        for i in range(count):
            country = random.choice(COUNTRIES)
            ip = random.choice(country["ips"])
            
            attack = {
                "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
                "source_ip": ip,
                "country": country["name"],
                "user_agent": random.choice(USER_AGENTS["nikto"] + USER_AGENTS["nmap"] + USER_AGENTS["burp"]),
                "method": "GET",
                "endpoint": random.choice(ATTACK_PATTERNS["automated_tool"]),
                "attack_type": "automated_tool",
                "severity": random.choice(["medium", "high"]),
                "confidence": random.uniform(0.6, 0.9),
                "anomaly_score": random.uniform(0.5, 0.8),
            }
            attacks.append(attack)
        
        return attacks
    
    async def generate_all_attacks(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate a mix of all attack types"""
        logger.info(f"🎯 Generating {count} synthetic attacks...")
        
        # Distribute attacks across types
        normal_count = int(count * 0.4)
        sql_count = int(count * 0.15)
        xss_count = int(count * 0.1)
        traversal_count = int(count * 0.1)
        brute_count = int(count * 0.15)
        automated_count = int(count * 0.1)
        
        all_attacks = []
        
        # Generate different types of attacks
        all_attacks.extend(await self.generate_normal_traffic(normal_count))
        all_attacks.extend(await self.generate_sql_injection_attacks(sql_count))
        all_attacks.extend(await self.generate_xss_attacks(xss_count))
        all_attacks.extend(await self.generate_directory_traversal_attacks(traversal_count))
        all_attacks.extend(await self.generate_brute_force_attacks(brute_count))
        all_attacks.extend(await self.generate_automated_tool_attacks(automated_count))
        
        # Shuffle and sort by timestamp
        random.shuffle(all_attacks)
        all_attacks.sort(key=lambda x: x["timestamp"])
        
        logger.info(f"✅ Generated {len(all_attacks)} synthetic attacks")
        return all_attacks
    
    async def simulate_real_time_attacks(self, duration_minutes: int = 10, interval_seconds: int = 30):
        """Simulate real-time attack generation"""
        logger.info(f"🚀 Starting real-time attack simulation for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        attack_count = 0
        
        while time.time() < end_time:
            # Generate a random attack
            attack_types = [
                self.generate_sql_injection_attacks(1),
                self.generate_xss_attacks(1),
                self.generate_directory_traversal_attacks(1),
                self.generate_brute_force_attacks(1),
                self.generate_automated_tool_attacks(1),
            ]
            
            attacks = await random.choice(attack_types)
            if attacks:
                attack = attacks[0]
                attack["timestamp"] = datetime.utcnow()
                
                # Simulate sending to honeypot
                try:
                    await self._send_attack_to_honeypot(attack)
                    attack_count += 1
                    logger.info(f"📡 Sent attack #{attack_count}: {attack['attack_type']} from {attack['source_ip']}")
                except Exception as e:
                    logger.error(f"❌ Error sending attack: {e}")
            
            # Wait before next attack
            await asyncio.sleep(interval_seconds)
        
        logger.info(f"🏁 Simulation complete. Generated {attack_count} real-time attacks.")
    
    async def _send_attack_to_honeypot(self, attack: Dict[str, Any]):
        """Send attack to honeypot endpoint"""
        if not self.session:
            return
        
        try:
            # Choose appropriate endpoint based on attack type
            if attack["attack_type"] == "brute_force":
                endpoint = "/api/honeypots/login"
                method = "POST"
                data = {"username": "admin", "password": "password"}
            elif attack["attack_type"] == "sql_injection":
                endpoint = "/api/honeypots/sql"
                method = "GET"
                data = None
                params = {"query": attack["endpoint"]}
            elif attack["attack_type"] == "directory_traversal":
                endpoint = "/api/honeypots/file"
                method = "GET"
                data = None
                params = {"path": attack["endpoint"]}
            else:
                endpoint = attack["endpoint"]
                method = attack["method"]
                data = None
                params = None
            
            # Send request
            url = f"{self.base_url}{endpoint}"
            headers = {
                "User-Agent": attack["user_agent"],
                "X-Forwarded-For": attack["source_ip"],
            }
            
            if method == "GET":
                async with self.session.get(url, headers=headers, params=params) as response:
                    pass
            elif method == "POST":
                async with self.session.post(url, headers=headers, data=data) as response:
                    pass
            
        except Exception as e:
            logger.error(f"Error sending attack to honeypot: {e}")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate synthetic attacks for honeypot testing")
    parser.add_argument("--count", type=int, default=100, help="Number of attacks to generate")
    parser.add_argument("--type", choices=["all", "normal", "sql", "xss", "traversal", "brute", "automated"], 
                       default="all", help="Type of attacks to generate")
    parser.add_argument("--real-time", action="store_true", help="Generate real-time attacks")
    parser.add_argument("--duration", type=int, default=10, help="Duration in minutes for real-time simulation")
    parser.add_argument("--interval", type=int, default=30, help="Interval between attacks in seconds")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the honeypot")
    parser.add_argument("--output", help="Output file for generated attacks")
    
    args = parser.parse_args()
    
    async with SyntheticAttackGenerator(args.url) as generator:
        if args.real_time:
            await generator.simulate_real_time_attacks(args.duration, args.interval)
        else:
            if args.type == "all":
                attacks = await generator.generate_all_attacks(args.count)
            elif args.type == "normal":
                attacks = await generator.generate_normal_traffic(args.count)
            elif args.type == "sql":
                attacks = await generator.generate_sql_injection_attacks(args.count)
            elif args.type == "xss":
                attacks = await generator.generate_xss_attacks(args.count)
            elif args.type == "traversal":
                attacks = await generator.generate_directory_traversal_attacks(args.count)
            elif args.type == "brute":
                attacks = await generator.generate_brute_force_attacks(args.count)
            elif args.type == "automated":
                attacks = await generator.generate_automated_tool_attacks(args.count)
            
            # Output results
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(attacks, f, indent=2, default=str)
                logger.info(f"💾 Saved {len(attacks)} attacks to {args.output}")
            else:
                # Print summary
                attack_types = {}
                for attack in attacks:
                    attack_type = attack["attack_type"]
                    attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
                
                logger.info("📊 Attack Summary:")
                for attack_type, count in attack_types.items():
                    logger.info(f"   {attack_type}: {count}")

if __name__ == "__main__":
    asyncio.run(main())
