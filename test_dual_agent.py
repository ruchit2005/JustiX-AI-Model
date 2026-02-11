"""
Test script for dual-agent system (Lawyer vs Judge)
Tests the intelligent role-switching based on user statements
"""

import requests
import json
import time
from sample_legal_laws import get_sample_legal_laws

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/ai"

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")

def test_init_legal_laws():
    """Initialize the legal laws vector database"""
    print_section("TEST 1: Initialize Legal Laws Database")
    
    url = f"{BASE_URL}{API_PREFIX}/init_legal_laws"
    
    # Get sample legal laws
    legal_text = get_sample_legal_laws()
    
    payload = {
        "legal_text": legal_text,
        "collection_name": "legal_laws"
    }
    
    print("📤 Sending request to initialize legal laws...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        elapsed = time.time() - start_time
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {elapsed:.2f}s")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_init_case():
    """Initialize case with PDF text"""
    print_section("TEST 2: Initialize Case Files")
    
    url = f"{BASE_URL}{API_PREFIX}/init_case"
    
    # Sample case text
    sample_case_text = """
    CASE NO. 2024-CR-12345
    
    THE STATE OF CALIFORNIA vs. JOHN DOE
    
    CRIMINAL COMPLAINT - ROBBERY
    
    FACTS OF THE CASE:
    On January 15, 2024, at approximately 10:43 PM, a robbery occurred at QuickMart convenience store 
    located at 456 Main Street, Los Angeles, CA. The store clerk, Maria Rodriguez, reported that a 
    masked individual entered the store and demanded cash from the register.
    
    EVIDENCE:
    1. GPS DATA: Cell phone records from the defendant's phone show he was within 100 meters of the 
       crime scene at 10:43 PM on January 15, 2024. The GPS data was collected from cell tower 
       triangulation and verified by telecommunications expert Dr. Sarah Chen.
    
    2. SECURITY FOOTAGE: The store's security camera captured footage of the robbery. However, due to 
       poor lighting conditions and the perpetrator wearing a mask, facial identification is not possible 
       from this footage. The footage does show the approximate height (5'10") and build of the suspect.
    
    3. WITNESS TESTIMONY: Store clerk Maria Rodriguez provided a statement that the robber was 
       approximately 5'10" tall, wore dark clothing, and had a distinctive tattoo visible on the left hand.
    
    DEFENSE POSITION:
    The defendant, John Doe, claims he was at home with his girlfriend, Sarah Thompson, at the time of 
    the robbery. Ms. Thompson has agreed to testify as an alibi witness. The defense argues that GPS 
    data can be unreliable in urban areas with tall buildings.
    
    PROSECUTION POSITION:
    The prosecution argues that the GPS data, combined with the physical description matching the 
    defendant and his prior criminal record for similar offenses, provides strong evidence of guilt beyond 
    a reasonable doubt.
    
    KEY LEGAL ISSUES:
    - Reliability and admissibility of GPS location data
    - Sufficiency of alibi defense
    - Weight of circumstantial evidence
    - Burden of proof and reasonable doubt standard
    """
    
    payload = {
        "case_id": "test_case_001",
        "pdf_text": sample_case_text
    }
    
    print("📤 Sending request to initialize case...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        elapsed = time.time() - start_time
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {elapsed:.2f}s")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_lawyer_response():
    """Test normal Lawyer response (no errors from user)"""
    print_section("TEST 3: Normal Lawyer Response (No User Errors)")
    
    url = f"{BASE_URL}{API_PREFIX}/turn"
    
    payload = {
        "case_id": "test_case_001",
        "user_text": "I believe the prosecution's timeline is flawed and I'd like to present an alibi defense.",
        "history": []
    }
    
    print("💬 User (Defense Lawyer): \"I believe the prosecution's timeline is flawed and I'd like to present an alibi defense.\"")
    print("\n📤 Sending request...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {elapsed:.2f}s")
        
        result = response.json()
        print(f"\n🤖 Agent: {result.get('speaker', 'Unknown')}")
        print(f"💭 Response:\n{result.get('reply_text', '')}")
        print(f"😤 Emotion: {result.get('emotion', 'Unknown')}")
        
        return response.status_code == 200 and result.get('speaker') == 'Opposing Lawyer'
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_judge_intervention_factual_error():
    """Test Judge intervention when user makes factual error"""
    print_section("TEST 4: Judge Intervention (Factual Error)")
    
    url = f"{BASE_URL}{API_PREFIX}/turn"
    
    # User makes up a fact that's not in the case
    payload = {
        "case_id": "test_case_001",
        "user_text": "The video surveillance clearly shows my client was at the library during the time of the incident, which proves innocence.",
        "history": [
            {"role": "user", "content": "Your Honor, I present the case for the defense."},
            {"role": "assistant", "content": "Proceed, Counsel."}
        ]
    }
    
    print("💬 User (Defense Lawyer): \"The video surveillance clearly shows my client was at the library during the time of the incident, which proves innocence.\"")
    print("⚠️  Expected: Judge should intervene if no such video exists in case files")
    print("\n📤 Sending request...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {elapsed:.2f}s")
        
        result = response.json()
        speaker = result.get('speaker', 'Unknown')
        print(f"\n⚖️  Speaker: {speaker}")
        print(f"💭 Response:\n{result.get('reply_text', '')}")
        print(f"😤 Emotion: {result.get('emotion', 'Unknown')}")
        
        if speaker == 'Judge':
            print("\n✅ SUCCESS: Judge correctly intervened for factual error!")
        else:
            print(f"\n⚠️  WARNING: Expected 'Judge' but got '{speaker}'")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_judge_intervention_legal_error():
    """Test Judge intervention when user makes legal error"""
    print_section("TEST 5: Judge Intervention (Legal Error)")
    
    url = f"{BASE_URL}{API_PREFIX}/turn"
    
    # User violates legal procedure
    payload = {
        "case_id": "test_case_001",
        "user_text": "I'm going to force my client to testify even though they don't want to, because it's the only way to win this case.",
        "history": [
            {"role": "user", "content": "Your Honor, I present the case for the defense."},
            {"role": "assistant", "content": "Proceed, Counsel."},
            {"role": "user", "content": "I want to challenge the GPS evidence."},
            {"role": "assistant", "content": "What is your basis for challenging it?"}
        ]
    }
    
    print("💬 User (Defense Lawyer): \"I'm going to force my client to testify even though they don't want to, because it's the only way to win this case.\"")
    print("⚠️  Expected: Judge should intervene (violates Fifth Amendment right against self-incrimination)")
    print("\n📤 Sending request...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {elapsed:.2f}s")
        
        result = response.json()
        speaker = result.get('speaker', 'Unknown')
        print(f"\n⚖️  Speaker: {speaker}")
        print(f"💭 Response:\n{result.get('reply_text', '')}")
        print(f"😤 Emotion: {result.get('emotion', 'Unknown')}")
        
        if speaker == 'Judge':
            print("\n✅ SUCCESS: Judge correctly intervened for legal error!")
        else:
            print(f"\n⚠️  WARNING: Expected 'Judge' but got '{speaker}'")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_lawyer_after_correction():
    """Test that Lawyer continues normally after Judge correction"""
    print_section("TEST 6: Lawyer Response After Judge Correction")
    
    url = f"{BASE_URL}{API_PREFIX}/turn"
    
    payload = {
        "case_id": "test_case_001",
        "user_text": "Thank you, Your Honor. I understand. Let me instead focus on questioning the reliability of the GPS evidence.",
        "history": [
            {"role": "user", "content": "I will force my client to testify."},
            {"role": "assistant", "content": "Counsel, you cannot compel testimony. The Fifth Amendment protects against self-incrimination."},
            {"role": "user", "content": "Thank you, Your Honor. I understand. Let me instead focus on questioning the reliability of the GPS evidence."}
        ]
    }
    
    print("💬 User (Defense Lawyer): \"Thank you, Your Honor. I understand. Let me instead focus on questioning the reliability of the GPS evidence.\"")
    print("✅ Expected: Lawyer should respond normally (correct legal approach)")
    print("\n📤 Sending request...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {elapsed:.2f}s")
        
        result = response.json()
        speaker = result.get('speaker', 'Unknown')
        print(f"\n🤖 Speaker: {speaker}")
        print(f"💭 Response:\n{result.get('reply_text', '')}")
        print(f"😤 Emotion: {result.get('emotion', 'Unknown')}")
        
        if speaker == 'Opposing Lawyer':
            print("\n✅ SUCCESS: Lawyer correctly handled normal statement!")
        else:
            print(f"\n⚠️  INFO: Got '{speaker}' instead of 'Opposing Lawyer'")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_all_tests():
    """Run all dual-agent tests"""
    print("\n" + "="*60)
    print(" 🧪 DUAL AGENT SYSTEM TEST SUITE")
    print(" Testing Lawyer vs Judge Role Switching")
    print("="*60)
    
    results = []
    
    # Test 1: Initialize legal laws
    results.append(("Initialize Legal Laws", test_init_legal_laws()))
    time.sleep(2)
    
    # Test 2: Initialize case
    results.append(("Initialize Case", test_init_case()))
    time.sleep(2)
    
    # Test 3: Normal Lawyer response
    results.append(("Normal Lawyer Response", test_lawyer_response()))
    time.sleep(2)
    
    # Test 4: Judge intervention for factual error
    results.append(("Judge Intervention (Factual)", test_judge_intervention_factual_error()))
    time.sleep(2)
    
    # Test 5: Judge intervention for legal error
    results.append(("Judge Intervention (Legal)", test_judge_intervention_legal_error()))
    time.sleep(2)
    
    # Test 6: Lawyer after correction
    results.append(("Lawyer After Correction", test_lawyer_after_correction()))
    
    # Print summary
    print_section("TEST RESULTS SUMMARY")
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Dual-agent system is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")

if __name__ == "__main__":
    print("🔧 Make sure the FastAPI server is running on http://localhost:8000")
    print("   Run: python main.py")
    input("\nPress Enter to start tests...")
    
    run_all_tests()
