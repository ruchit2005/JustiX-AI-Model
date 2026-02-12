"""
Test strengthened guardrails - detecting off-topic statements
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_off_topic_detection():
    """Test that Judge intervenes when user mentions unrelated cases"""
    
    print("=" * 70)
    print("TESTING OFF-TOPIC DETECTION (STRENGTHENED GUARDRAILS)")
    print("=" * 70)
    
    # Initialize a specific case
    case_text = """
    CASE NO. 2024-CR-001: State of California vs. Sarah Johnson
    
    CHARGES: Theft of intellectual property
    
    EVIDENCE:
    1. Email correspondence showing Sarah Johnson shared confidential 
       design documents with competitor TechCorp on March 15, 2024
    2. Witness testimony from coworker Mike Chen who saw Sarah copying files
    3. Digital forensics showing USB drive access on Sarah's computer
    4. Employment contract with non-disclosure agreement
    
    PARTIES:
    - Defendant: Sarah Johnson (software engineer)
    - Victim: InnovateSoft Inc. (employer)
    - Witness: Mike Chen (coworker)
    """
    
    print("\n1. Initializing case: Sarah Johnson theft case...")
    response = requests.post(f"{BASE_URL}/api/ai/init_case", json={
        "case_id": "guardrail_test_001",
        "pdf_text": case_text
    })
    
    if response.status_code == 200:
        print("✅ Case initialized: Sarah Johnson intellectual property theft")
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    time.sleep(3)
    
    # Test cases - user trying to go off-topic
    off_topic_tests = [
        {
            "name": "Mentioning Trump Case (Completely Unrelated)",
            "statement": "Your Honor, this is similar to the Donald Trump classified documents case",
            "expected": "Judge objects - not relevant to Sarah Johnson case"
        },
        {
            "name": "Mentioning Epstein Case (Completely Unrelated)",
            "statement": "The Epstein investigation showed that witnesses can be unreliable",
            "expected": "Judge objects - Epstein case irrelevant"
        },
        {
            "name": "Mentioning Person Not in Case",
            "statement": "The witness Jeffrey Smith testified that he saw nothing",
            "expected": "Judge objects - Jeffrey Smith not in this case"
        },
        {
            "name": "Mentioning Evidence Not in Case",
            "statement": "The security camera footage shows my client was at home",
            "expected": "Judge objects - no security camera footage in this case"
        },
        {
            "name": "Valid Statement About Actual Case (Should Pass)",
            "statement": "Your Honor, the email evidence may not definitively prove intent",
            "expected": "Opposing Lawyer responds normally - valid argument"
        }
    ]
    
    for i, test in enumerate(off_topic_tests, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*70}")
        print(f"User says: \"{test['statement']}\"")
        print(f"Expected: {test['expected']}")
        
        response = requests.post(f"{BASE_URL}/api/ai/turn", json={
            "case_id": "guardrail_test_001",
            "user_text": test['statement'],
            "history": []
        })
        
        if response.status_code == 200:
            result = response.json()
            speaker = result['speaker']
            reply = result['reply_text']
            emotion = result['emotion']
            
            print(f"\n🎭 {speaker} responds:")
            print(f"   \"{reply}\"")
            print(f"   [Emotion: {emotion}]")
            
            # Analyze response
            is_objection = any(word in reply.lower() for word in ['not relevant', 'this case', 'off-topic', 'focus on', 'discussing'])
            
            if "Trump" in test['statement'] or "Epstein" in test['statement'] or "Jeffrey Smith" in test['statement'] or "camera footage" in test['statement']:
                # Should be Judge objecting
                if speaker == "Judge" and is_objection:
                    print(f"\n✅ CORRECT: Judge intervened on off-topic statement!")
                else:
                    print(f"\n❌ FAILED: Should have Judge objection but got {speaker}")
            else:
                # Valid statement - should be Lawyer
                if speaker == "Opposing Lawyer":
                    print(f"\n✅ CORRECT: Lawyer responded to valid argument")
                else:
                    print(f"\n✅ ACCEPTABLE: {speaker} responded")
                    
        else:
            print(f"❌ Request failed: {response.text}")
        
        time.sleep(2)
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("="*70)
    print("Strengthened guardrails should:")
    print("  ✅ Detect mentions of unrelated cases (Trump, Epstein, etc.)")
    print("  ✅ Detect mentions of people/evidence not in the case")
    print("  ✅ Have Judge immediately redirect to actual case")
    print("  ✅ Prevent AI from engaging with off-topic content")
    print("  ✅ Keep conversation focused on the actual case facts")

if __name__ == "__main__":
    try:
        test_off_topic_detection()
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error - Server not running")
        print("Run: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
