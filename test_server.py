#!/usr/bin/env python3
"""
Test script to verify the honeypot server is working
"""

import requests
import json
import time

def test_server():
    base_url = "http://localhost:8000"
    
    print("🛡️ Testing AI Cybersecurity Honeypot Server...")
    print("=" * 50)
    
    try:
        # Test 1: Health check
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        # Test 2: Root endpoint
        print("\n2. Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            data = response.json()
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            
        # Test 3: Login page
        print("\n3. Testing honeypot login page...")
        response = requests.get(f"{base_url}/honeypots/login", timeout=5)
        if response.status_code == 200:
            print("✅ Login honeypot working!")
            print("   📝 You can visit: http://localhost:8000/honeypots/login")
        else:
            print(f"❌ Login honeypot failed: {response.status_code}")
            
        # Test 4: Generate test attacks
        print("\n4. Generating test attacks...")
        response = requests.get(f"{base_url}/generate-attacks?count=5", timeout=10)
        if response.status_code == 200:
            print("✅ Test attacks generated!")
            data = response.json()
            print(f"   Generated: {data.get('total_attacks', 0)} attacks")
        else:
            print(f"❌ Attack generation failed: {response.status_code}")
            
        # Test 5: Check analytics
        print("\n5. Testing analytics...")
        response = requests.get(f"{base_url}/analytics", timeout=5)
        if response.status_code == 200:
            print("✅ Analytics working!")
            data = response.json()
            print(f"   Total attacks: {data.get('total_attacks', 0)}")
            print(f"   Unique attackers: {data.get('unique_attackers', 0)}")
            print(f"   Anomalies detected: {data.get('anomalies_detected', 0)}")
        else:
            print(f"❌ Analytics failed: {response.status_code}")
            
        print("\n" + "=" * 50)
        print("🎉 SERVER IS WORKING! 🎉")
        print("\n📱 Access your honeypot:")
        print("   🌐 Main API: http://localhost:8000")
        print("   📚 API Docs: http://localhost:8000/docs")
        print("   🔐 Login Honeypot: http://localhost:8000/honeypots/login")
        print("   🗃️ SQL Honeypot: http://localhost:8000/honeypots/sql")
        print("   📁 File Honeypot: http://localhost:8000/honeypots/file")
        print("   📊 Analytics: http://localhost:8000/analytics")
        print("\n💡 Try these attack examples:")
        print("   curl 'http://localhost:8000/honeypots/sql?query=1%20UNION%20SELECT%20*%20FROM%20users'")
        print("   curl 'http://localhost:8000/honeypots/file?path=../../../etc/passwd'")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("   Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_server()
