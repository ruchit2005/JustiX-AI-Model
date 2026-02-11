"""
Test the new realistic courtroom behavior of the Opposing Lawyer
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_lawyer_behavior():
    """Test that lawyer presents arguments professionally instead of constant objections"""
    
    print("=" * 60)
    print("Testing New Realistic Courtroom Behavior")
    print("=" * 60)
    
    # 1. Initialize case (simple example)
    case_text = """
    CASE NO. 2024-CR-12345: State vs. John Doe
    
    CHARGES: Robbery at convenience store
    
    EVIDENCE:
    1. GPS Data: Defendant's phone was within 100 meters of crime scene at 10:43 PM
    2. Security Footage: Shows person matching defendant's description entering store at 10:42 PM
    3. Witness Testimony: Store clerk identified defendant in photo lineup
    4. Timeline: Crime occurred between 10:40 PM - 10:50 PM
    """
    
    print("\n1. Initializing case...")
    response = requests.post(f"{BASE_URL}/api/ai/init_case", json={
        "case_id": "test_realistic_001",
        "pdf_text": case_text
    })
    
    if response.status_code == 200:
        print("✅ Case initialized")
    else:
        print(f"❌ Failed to initialize case: {response.text}")
        return
    
    time.sleep(2)  # Let Qdrant finish indexing
    
    # 2. Test multiple turns to see natural conversation flow
    test_scenarios = [
        {
            "name": "User presents opening argument",
            "user_text": "Your Honor, I believe the GPS evidence is circumstantial and doesn't prove my client committed the robbery.",
            "expected_style": "Professional counter-argument, NOT 'Objection!'"
        },
        {
            "name": "User challenges witness credibility",
            "user_text": "The witness identification may be unreliable due to stress and poor lighting conditions.",
            "expected_style": "Thoughtful rebuttal about witness reliability"
        },
        {
            "name": "User proposes alibi defense",
            "user_text": "I want to present evidence that my client was at a different location during the crime.",
            "expected_style": "Counter-argument using case facts, NOT objection"
        },
        {
            "name": "User makes legal argument",
            "user_text": "The prosecution has not met the burden of proof beyond a reasonable doubt.",
            "expected_style": "Professional response about strength of evidence"
        }
    ]
    
    history = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {scenario['name']}")
        print(f"{'='*60}")
        print(f"User says: \"{scenario['user_text']}\"")
        print(f"Expected: {scenario['expected_style']}")
        
        response = requests.post(f"{BASE_URL}/api/ai/turn", json={
            "case_id": "test_realistic_001",
            "user_text": scenario['user_text'],
            "history": history
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🎭 {result['speaker']} responds:")
            print(f"   \"{result['reply_text']}\"")
            print(f"   [Emotion: {result['emotion']}]")
            
            # Analyze if response is objection-focused or argumentative
            reply_lower = result['reply_text'].lower()
            has_objection = reply_lower.startswith('objection')
            has_your_honor = 'your honor' in reply_lower
            has_evidence = 'evidence' in reply_lower or 'data' in reply_lower
            
            print(f"\n📊 Analysis:")
            print(f"   • Starts with 'Objection': {'❌ YES (too aggressive)' if has_objection else '✅ NO (good)'}")
            print(f"   • Addresses 'Your Honor': {'✅ YES (professional)' if has_your_honor else '⚠️ NO'}")
            print(f"   • References evidence: {'✅ YES' if has_evidence else '⚠️ NO'}")
            
            # Add to history
            history.append({"role": "user", "content": scenario['user_text']})
            history.append({"role": "assistant", "content": result['reply_text']})
            
        else:
            print(f"❌ Request failed: {response.text}")
        
        time.sleep(1)  # Brief pause between requests
    
    print(f"\n{'='*60}")
    print("Test Complete!")
    print("="*60)
    print("\n✅ The lawyer should now:")
    print("   1. Present arguments professionally")
    print("   2. Take turns like a real trial")
    print("   3. Use 'Your Honor, ...' instead of 'Objection!'")
    print("   4. Only object when there's a real procedural violation")

if __name__ == "__main__":
    try:
        test_lawyer_behavior()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server. Make sure it's running:")
        print("   python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
