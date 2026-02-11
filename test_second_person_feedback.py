"""
Test the analyze endpoint with second-person feedback
"""
import requests
import json

# Sample transcript similar to what the user showed
transcript = [
    {
        "speaker": "User",
        "text": "Yes Your Honor. According to Article 21 of the Constitution, every person has the right to life and personal liberty. This includes the right to immediate medical care in emergencies.",
        "_id": {"$oid": "67879f9dd1c1854d73c618ae"},
        "timestamp": {"$date": "2025-01-15T10:23:41.281Z"}
    },
    {
        "speaker": "Judge",
        "text": "Counsel, please be more precise in your citations. Are you referring to a specific legal precedent?",
        "_id": {"$oid": "67879faad1c1854d73c618af"},
        "timestamp": {"$date": "2025-01-15T10:23:54.762Z"}
    },
    {
        "speaker": "User",
        "text": "My apologies, Your Honor. I meant to reference the principle established in healthcare cases.",
        "_id": {"$oid": "67879faad1c1854d73c618b0"},
        "timestamp": {"$date": "2025-01-15T10:24:10.123Z"}
    },
    {
        "speaker": "Opposing Lawyer",
        "text": "Your Honor, the defense's argument conflates different legal principles without proper substantiation from the case facts.",
        "_id": {"$oid": "67879faad1c1854d73c618b1"},
        "timestamp": {"$date": "2025-01-15T10:24:25.456Z"}
    }
]

print("=" * 70)
print("TESTING SECOND-PERSON FEEDBACK FORMAT")
print("=" * 70)
print("\nSending transcript to /analyze endpoint...")
print("Expected: Feedback using 'you' and 'your' (not 'the student')\n")

try:
    response = requests.post(
        "http://localhost:8000/analyze",
        json={"transcript": transcript},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"✅ Status: {response.status_code} OK\n")
        print(f"📊 SCORE: {result['score']}/100\n")
        print(f"📝 SUMMARY:")
        print(f"   {result['summary']}\n")
        print(f"💬 DETAILED FEEDBACK:")
        print(f"   {result['feedback']}\n")
        
        # Check if feedback uses second person
        feedback_lower = result['feedback'].lower()
        summary_lower = result['summary'].lower()
        
        has_you = 'you' in feedback_lower or 'your' in feedback_lower
        has_student = 'the student' in feedback_lower or 'the law student' in feedback_lower
        
        print("=" * 70)
        print("VALIDATION:")
        print("=" * 70)
        if has_you and not has_student:
            print("✅ CORRECT: Using second person ('you/your')")
        elif has_student:
            print("⚠️ ISSUE: Still using 'the student' (third person)")
        else:
            print("⚠️ UNCLEAR: Check feedback format")
            
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Connection Error - Server not running")
    print("Run: python main.py")
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()
