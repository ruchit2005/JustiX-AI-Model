"""
Test the analyze endpoint with MongoDB transcript format
"""
import requests
import json

# Your actual production data
mongodb_transcript = [
    {
        "speaker": "User",
        "text": "Yes Your Honor. According to Article 21 of the Constitution, every person has the right to life and personal liberty. This includes the right to a fair trial and to be heard. My client was not given a chance to testify in his own defense.",
        "_id": {"$oid": "67879f9dd1c1854d73c618ae"},
        "timestamp": {"$date": "2025-01-15T10:23:41.281Z"}
    },
    {
        "speaker": "Opposing Lawyer",
        "text": "Your Honor, I understand the defendant's concerns regarding their right to testify. However, it is important to clarify that the decision not to call the defendant as a witness was made strategically to protect their interests. The evidence presented by the prosecution was strong, and we believed that putting the defendant on the stand could potentially harm their case further. Additionally, the defendant had the opportunity to consult with me throughout the proceedings, and we made the decision together not to testify. This was a calculated choice based on the circumstances of the case.",
        "_id": {"$oid": "67879faad1c1854d73c618af"},
        "timestamp": {"$date": "2025-01-15T10:23:54.762Z"}
    }
]

# Make request to analyze endpoint
url = "http://localhost:8000/api/ai/analyze"
payload = {
    "transcript": mongodb_transcript
}

print("Testing analyze endpoint with MongoDB format...")
print(f"URL: {url}")
print(f"\nPayload transcript format:")
print(f"  - speaker: {mongodb_transcript[0]['speaker']}")
print(f"  - text: {mongodb_transcript[0]['text'][:50]}...")
print(f"  - _id: {mongodb_transcript[0]['_id']}")
print(f"  - timestamp: {mongodb_transcript[0]['timestamp']}")

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! Analysis completed:")
        print(f"Score: {result.get('score', 'N/A')}")
        print(f"Summary: {result.get('summary', 'N/A')}")
        print(f"Feedback: {result.get('feedback', 'N/A')}")
    else:
        print(f"\n❌ ERROR:")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error: Make sure the FastAPI server is running")
    print("Run: python main.py")
except Exception as e:
    print(f"\n❌ Exception: {e}")
