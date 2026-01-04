import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

# Use the working API key
ZENYA_API_KEY = os.getenv("ZENYA_API_KEY", "20718ce5a0a512febfd8f5a16c1c835f")
ZENYA_CUSTOMER_KEY = ZENYA_API_KEY  # Use API key as customer key
ZENYA_URL = os.getenv("ZENYA_URL", "https://appserver.zenya.io/api/v1/mapping/")

def get_room(room_id: str):
    """Fetch room details from Zenya API"""
    payload = {
        "customerKey": ZENYA_CUSTOMER_KEY,
        "route": "getRoomById",
        "data": {
            "roomId": room_id,
            "directLink": True
        }
    }
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": ZENYA_API_KEY
    }
    
    response = requests.post(
        ZENYA_URL,
        json=payload,
        headers=headers,
        timeout=10
    )
    if response.status_code != 200:
        return None
    return response.json()


def get_building(building_id: str):
    """Fetch room details from Zenya API"""
    payload = {
        "customerKey": ZENYA_CUSTOMER_KEY,
        "route": "getRoomsByBuildingId",
        "data": {
            "roomId": building_id,
            "directLink": True
        }
    }
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": ZENYA_API_KEY
    }
    
    response = requests.post(
        ZENYA_URL,
        json=payload,
        headers=headers,
        timeout=10
    )
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return None
    return response.json()


def get_rooms_by_location(lat: float, lng: float, distance: str = "20", start_date: str = "2025-11-05", end_date: str = "2025-11-10"):
    """Fetch rooms by location from Zenya API"""
    payload = {
        "customerKey": ZENYA_CUSTOMER_KEY,
        "route": "getRoomsByLocations",
        "data": {
            "location": {"lat": lat, "long": lng},
            "distance": distance,
            "startDate": start_date,
            "endDate": end_date
        }
    }
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": ZENYA_API_KEY
    }
    response = requests.post(
        ZENYA_URL,
        json=payload,
        headers=headers,
        timeout=10
    )
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return None
    return response.json()






if __name__ == "__main__":
    print(f"Using API Key: {ZENYA_API_KEY[:20]}...")
    print(f"Using Customer Key: {ZENYA_CUSTOMER_KEY[:20]}...")
    
    # Test 1: Get room by ID
    print("\n" + "="*60)
    print("TEST 1: Getting Room by ID (220678)")
    print("="*60)
    room_id = "220678"
    result = get_room(room_id)
    
    if result:
        print("\n=== Room Details ===")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to fetch room details")
    
    # Test 2: Get rooms by location
    print("\n" + "="*60)
    print("TEST 2: Getting Rooms by Location (Winnipeg)")
    print("="*60)
    # Winnipeg coordinates
    lat = 49.8790
    lng = -97.1410
    result2 = get_rooms_by_location(lat, lng, distance="20", start_date="2025-11-05", end_date="2025-11-10")
    
    if result2:
        print("\n=== Rooms by Location ===")
        print(json.dumps(result2, indent=2))
    else:
        print("Failed to fetch rooms by location")
