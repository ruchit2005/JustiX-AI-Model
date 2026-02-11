"""
Test client for VerdicTech AI Engine API
Run this script to test all endpoints
"""
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/ai"

# Sample case data
SAMPLE_CASE_ID = "test_case_001"
SAMPLE_CASE_TEXT = """
STATE OF CALIFORNIA vs. JOHN SMITH
Case No. 2024-CR-12345

FACTS:
On January 15, 2024, at approximately 10:43 PM, a robbery occurred at the QuickMart convenience 
store located at 123 Main Street. The perpetrator allegedly stole $500 in cash and fled the scene.

The prosecution alleges that the defendant, John Smith, was identified by security camera footage 
wearing a blue jacket. GPS data from the defendant's phone places him within 100 meters of the 
crime scene at 10:43 PM.

DEFENSE POSITION:
The defense argues that John Smith was at his friend's house, located at 456 Oak Avenue, 
approximately 2 miles from the crime scene. His friend, Michael Johnson, provided a sworn 
statement confirming Smith's presence at his residence from 9:00 PM to 11:30 PM on the night 
in question.

The defense also contests the reliability of the GPS data and the clarity of the security 
camera footage for positive identification.

KEY EVIDENCE:
1. Security camera footage (grainy, suspect wearing blue jacket)
2. GPS phone data placing defendant near scene
3. Alibi witness statement from Michael Johnson
4. Defendant's blue jacket (seized as evidence)
"""


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response: requests.Response):
    """Print a formatted response"""
    print(f"\nStatus Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_health_check():
    """Test the health check endpoint"""
    print_section("1. Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_init_case() -> bool:
    """Test case initialization"""
    print_section("2. Testing Case Initialization")
    try:
        payload = {
            "case_id": SAMPLE_CASE_ID,
            "pdf_text": SAMPLE_CASE_TEXT
        }
        response = requests.post(f"{API_URL}/init_case", json=payload)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_chat_turn(user_text: str, history: list = None) -> Dict[str, Any]:
    """Test a chat turn"""
    if history is None:
        history = []
    
    try:
        payload = {
            "case_id": SAMPLE_CASE_ID,
            "user_text": user_text,
            "history": history
        }
        response = requests.post(f"{API_URL}/turn", json=payload)
        print_response(response)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_chat_conversation():
    """Test a full conversation"""
    print_section("3. Testing Chat Conversation")
    
    history = []
    
    # Turn 1
    print("\n📝 User: \"Your Honor, I move to dismiss the GPS evidence as unreliable.\"")
    response1 = test_chat_turn(
        "Your Honor, I move to dismiss the GPS evidence as unreliable.",
        history
    )
    if response1:
        history.append({"role": "user", "content": "Your Honor, I move to dismiss the GPS evidence as unreliable."})
        history.append({"role": "assistant", "content": response1["reply_text"]})
    
    # Turn 2
    print("\n📝 User: \"My client has a credible alibi witness.\"")
    response2 = test_chat_turn(
        "My client has a credible alibi witness.",
        history
    )
    if response2:
        history.append({"role": "user", "content": "My client has a credible alibi witness."})
        history.append({"role": "assistant", "content": response2["reply_text"]})
    
    # Turn 3
    print("\n📝 User: \"The security footage is too grainy for positive identification.\"")
    response3 = test_chat_turn(
        "The security footage is too grainy for positive identification.",
        history
    )
    if response3:
        history.append({"role": "user", "content": "The security footage is too grainy for positive identification."})
        history.append({"role": "assistant", "content": response3["reply_text"]})
    
    return history


def test_analyze(transcript: list):
    """Test performance analysis"""
    print_section("4. Testing Performance Analysis")
    try:
        payload = {
            "transcript": transcript
        }
        response = requests.post(f"{API_URL}/analyze", json=payload)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n🚀 Starting VerdicTech AI Engine Tests")
    print(f"Target: {BASE_URL}")
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n❌ Server is not responding. Make sure it's running!")
        print("Run: python main.py")
        return
    print("✅ Health check passed")
    
    # Test 2: Initialize Case
    if not test_init_case():
        print("\n❌ Failed to initialize case")
        return
    print("✅ Case initialization passed")
    
    # Test 3: Chat Conversation
    transcript = test_chat_conversation()
    if not transcript:
        print("\n❌ Chat conversation failed")
        return
    print("✅ Chat conversation passed")
    
    # Test 4: Analysis
    if not test_analyze(transcript):
        print("\n❌ Analysis failed")
        return
    print("✅ Analysis passed")
    
    # Summary
    print_section("✅ ALL TESTS PASSED!")
    print("\nThe AI Engine is working correctly.")
    print("You can now integrate it with your Node.js backend.")


if __name__ == "__main__":
    main()
