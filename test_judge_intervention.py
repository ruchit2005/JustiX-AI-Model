"""
Test Judge intervention with various scenarios
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def init_case():
    """Initialize a simple test case"""
    case_text = """
    CASE NO. 2024-CR-001: State vs. Defendant
    
    CHARGES: Robbery
    
    EVIDENCE:
    1. GPS Data: Defendant's phone at crime scene at 10:43 PM
    2. Security footage shows person matching description
    3. Witness testimony from store clerk
    """
    
    response = requests.post(f"{BASE_URL}/api/ai/init_case", json={
        "case_id": "judge_test_001",
        "pdf_text": case_text
    })
    
    print(f"Case init: {response.status_code}")
    if response.status_code == 200:
        print("✅ Case initialized")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def init_legal_laws():
    """Initialize legal laws for the Judge"""
    legal_text = """
    Article 21: Right to Life and Personal Liberty
    Every person has the right to life and personal liberty. No person shall be deprived of their liberty except by due process of law.
    
    Fifth Amendment: Right Against Self-Incrimination
    No person shall be compelled to testify against themselves in a criminal case.
    
    Legal Ethics Rule 3.4: Fairness to Opposing Party and Counsel
    A lawyer shall not:
    - Unlawfully obstruct access to evidence
    - Falsify evidence
    - Counsel or assist a witness to testify falsely
    - Offer an inducement to a witness that is prohibited by law
    
    Burden of Proof Standard:
    In criminal cases, the prosecution bears the burden of proof beyond a reasonable doubt.
    """
    
    response = requests.post(f"{BASE_URL}/api/ai/init_legal_laws", json={
        "legal_text": legal_text,
        "collection_name": "legal_laws"
    })
    
    print(f"Legal laws init: {response.status_code}")
    if response.status_code == 200:
        print("✅ Legal laws initialized")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_judge_scenarios():
    """Test scenarios that should trigger Judge intervention"""
    
    print("\n" + "="*70)
    print("TESTING JUDGE INTERVENTION SCENARIOS")
    print("="*70)
    
    test_cases = [
        {
            "name": "Opening Statement (Should get Judge acknowledgment)",
            "text": "Your Honor, I present the defense for this case",
            "expect_judge": True,
            "reason": "First turn with 'Your Honor' should trigger Judge"
        },
        {
            "name": "Forcing Client to Testify (Ethics Violation)",
            "text": "I will force my client to testify in their own defense",
            "expect_judge": True,
            "reason": "Fifth Amendment violation - coaching/forcing"
        },
        {
            "name": "Coaching Witness (Ethics Violation)",
            "text": "I'll tell the witness exactly what to say on the stand",
            "expect_judge": True,
            "reason": "Violates legal ethics rule about witness testimony"
        },
        {
            "name": "Factual Misrepresentation",
            "text": "The security footage shows my client was at the library during the crime",
            "expect_judge": False,  # Might be Lawyer correcting facts
            "reason": "Lawyer should counter with actual evidence"
        },
        {
            "name": "Normal Legal Argument",
            "text": "I believe the GPS evidence is circumstantial and unreliable",
            "expect_judge": False,
            "reason": "Valid legal strategy - Lawyer should respond"
        }
    ]
    
    history = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*70}")
        print(f"User says: \"{test['text']}\"")
        print(f"Expected: {'⚖️ JUDGE' if test['expect_judge'] else '👔 LAWYER'}")
        print(f"Reason: {test['reason']}")
        
        response = requests.post(f"{BASE_URL}/api/ai/turn", json={
            "case_id": "judge_test_001",
            "user_text": test['text'],
            "history": history
        })
        
        if response.status_code == 200:
            result = response.json()
            speaker = result['speaker']
            
            print(f"\n🎭 {speaker} responds:")
            print(f"   \"{result['reply_text']}\"")
            print(f"   [Emotion: {result['emotion']}]")
            
            # Check if result matches expectation
            if test['expect_judge'] and speaker == "Judge":
                print(f"\n✅ CORRECT: Judge intervened as expected")
            elif not test['expect_judge'] and speaker == "Opposing Lawyer":
                print(f"\n✅ CORRECT: Lawyer responded as expected")
            elif test['expect_judge'] and speaker != "Judge":
                print(f"\n⚠️ UNEXPECTED: Expected Judge but got {speaker}")
            else:
                print(f"\n✅ ACCEPTABLE: {speaker} responded")
            
            # Add to history
            history.append({"role": "user", "content": test['text']})
            history.append({"role": "assistant", "content": result['reply_text']})
            
        else:
            print(f"\n❌ Request failed: {response.text}")
        
        time.sleep(2)  # Brief pause between requests
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("="*70)
    print("If Judge never appeared, the detection logic needs adjustment.")
    print("Judge should intervene on:")
    print("  • Ethics violations (forcing testimony, coaching)")
    print("  • Opening acknowledgments ('Your Honor, I present...')")
    print("  • Procedural errors")

if __name__ == "__main__":
    try:
        print("Initializing test environment...")
        
        # Initialize legal laws first (Judge's knowledge)
        if not init_legal_laws():
            print("\n❌ Failed to initialize legal laws")
            exit(1)
        
        time.sleep(2)
        
        # Initialize case (Lawyer's knowledge)
        if not init_case():
            print("\n❌ Failed to initialize case")
            exit(1)
        
        time.sleep(2)
        
        # Run tests
        test_judge_scenarios()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server. Make sure it's running:")
        print("   python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
