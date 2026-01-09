"""
Quick API Demo - Test Google Analytics Endpoints
Run this after starting the FastAPI server with: uvicorn app.main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/google"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*80}")
    print(f"📊 {title}")
    print(f"{'='*80}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")

def test_endpoints():
    """Test all Google Analytics endpoints"""
    
    print("\n🚀 Testing Google Analytics API Endpoints")
    print("="*80)
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{BASE_URL}/analytics/health")
        print_response("Health Check", response)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Summary
    try:
        response = requests.get(f"{BASE_URL}/analytics/summary")
        print_response("Analytics Summary", response)
    except Exception as e:
        print(f"❌ Summary failed: {e}")
    
    # Test 3: Daily with limit
    try:
        response = requests.get(f"{BASE_URL}/analytics/daily?limit=5")
        print_response("Last 5 Days (limited)", response)
    except Exception as e:
        print(f"❌ Daily analytics failed: {e}")
    
    # Test 4: By Country
    try:
        response = requests.get(f"{BASE_URL}/analytics/by-country")
        print_response("Top Countries", response)
    except Exception as e:
        print(f"❌ Country analytics failed: {e}")
    
    # Test 5: Monthly Active Users
    try:
        response = requests.get(f"{BASE_URL}/analytics/monthly/active-users")
        print_response("Monthly Active Users (MAU)", response)
    except Exception as e:
        print(f"❌ MAU failed: {e}")
    
    print("\n" + "="*80)
    print("✅ Testing Complete!")
    print("="*80)

if __name__ == "__main__":
    print("""
    ⚠️  IMPORTANT: Make sure the FastAPI server is running!
    
    Start server with:
        uvicorn app.main:app --reload
    
    Then run this script to test the endpoints.
    """)
    
    input("Press Enter to start testing (or Ctrl+C to cancel)...")
    test_endpoints()
