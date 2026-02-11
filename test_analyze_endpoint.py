"""
Test the /analyze endpoint with the exact format the backend sends
"""
import requests
import json

# Test 1: Using /analyze (backend's expected path)
print("=" * 70)
print("TEST 1: POST /analyze (backend's path)")
print("=" * 70)

transcript_data = [
    {
        "speaker": "User",
        "text": "Yes Your Honor. According to Article 21 of the Constitution, every person has the right to life and personal liberty.",
        "_id": {"$oid": "67879f9dd1c1854d73c618ae"},
        "timestamp": {"$date": "2025-01-15T10:23:41.281Z"}
    },
    {
        "speaker": "Opposing Lawyer",
        "text": "Your Honor, I must point out that the defendant's argument overlooks key evidence in this case.",
        "_id": {"$oid": "67879faad1c1854d73c618af"},
        "timestamp": {"$date": "2025-01-15T10:23:54.762Z"}
    }
]

try:
    response = requests.post(
        "http://localhost:8000/analyze",  # Backend expects this path
        json={"transcript": transcript_data}  # Backend sends this format
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"Score: {result.get('score')}")
        print(f"Summary: {result.get('summary')}")
        print(f"Feedback: {result.get('feedback')[:100]}...")
    else:
        print(f"\n❌ FAILED!")
        print(f"Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error - Server not running")
except Exception as e:
    print(f"\n❌ Exception: {e}")

# Test 2: Using /api/ai/analyze (original path - should still work)
print("\n" + "=" * 70)
print("TEST 2: POST /api/ai/analyze (original path)")
print("=" * 70)

try:
    response = requests.post(
        "http://localhost:8000/api/ai/analyze",  # Original path
        json={"transcript": transcript_data}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"Score: {result.get('score')}")
    else:
        print(f"\n❌ FAILED!")
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print("Both /analyze and /api/ai/analyze should return 200 OK")
print("Your Node.js backend can now use: AI_SERVICE_URL/analyze")
