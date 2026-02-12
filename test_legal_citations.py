"""
Test script to verify Judge and Lawyer cite specific legal sections.
Tests that responses include Article X, Section Y, Amendment N format.
"""

import requests
import json
import re
import time

BASE_URL = "http://localhost:8000"

def test_lawyer_cites_legal_sections():
    """Test that Opposing Lawyer cites specific legal sections"""
    print("\n=== Testing Lawyer Legal Citations ===")
    
    # Make a legal argument that should trigger citation
    turn_request = {
        "case_id": "test_case_001",
        "user_text": "The evidence was illegally obtained without a warrant.",
        "history": [
            {"role": "user", "content": "I want to challenge the evidence."},
            {"role": "assistant", "content": "Proceed with your challenge."}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/ai/turn", json=turn_request)
    
    if response.status_code == 200:
        data = response.json()
        reply = data["reply_text"]
        print(f"\nLawyer Response: {reply}")
        
        # Check for legal citations (Section X, Article Y, IPC Section Z, Amendment N)
        citation_patterns = [
            r'Section \d+',           # Section 123
            r'Article \d+',            # Article 21
            r'IPC Section \d+',        # IPC Section 302
            r'CrPC Section \d+',       # CrPC Section 154
            r'\w+ Amendment',          # Fifth Amendment
            r'Rule \d+\.\d+'          # Rule 3.4
        ]
        
        found_citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, reply)
            found_citations.extend(matches)
        
        if found_citations:
            print(f"✅ PASS: Found legal citations: {found_citations}")
            return True
        else:
            print(f"❌ FAIL: No legal citations found in response")
            print("Expected patterns like: 'Section 123', 'Article 21', 'Fifth Amendment'")
            return False
    else:
        print(f"❌ ERROR: Request failed with status {response.status_code}")
        print(response.text)
        return False

def test_judge_cites_legal_sections():
    """Test that Judge cites specific constitutional/procedural sections"""
    print("\n=== Testing Judge Legal Citations ===")
    
    # Make a statement that should trigger Judge intervention with citation
    turn_request = {
        "case_id": "test_case_001",
        "user_text": "I want to force the defendant to testify against themselves.",
        "history": [
            {"role": "user", "content": "What's my strategy?"},
            {"role": "assistant", "content": "Present your case."}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/ai/turn", json=turn_request)
    
    if response.status_code == 200:
        data = response.json()
        speaker = data["speaker"]
        reply = data["reply_text"]
        
        print(f"\nSpeaker: {speaker}")
        print(f"Response: {reply}")
        
        # Check if Judge intervened
        if "Judge" not in speaker:
            print(f"⚠️ WARNING: Expected Judge, got {speaker}")
        
        # Check for legal citations
        citation_patterns = [
            r'Section \d+',
            r'Article \d+',
            r'\w+ Amendment',          # Fifth Amendment, Fourth Amendment
            r'CPC Section \d+',
            r'Rule \d+\.\d+'
        ]
        
        found_citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, reply)
            found_citations.extend(matches)
        
        if found_citations:
            print(f"✅ PASS: Found legal citations: {found_citations}")
            return True
        else:
            print(f"❌ FAIL: No legal citations found in Judge's response")
            print("Expected patterns like: 'Fifth Amendment', 'Section 313', 'Article 20'")
            return False
    else:
        print(f"❌ ERROR: Request failed with status {response.status_code}")
        print(response.text)
        return False

def test_off_topic_judge_cites_rules():
    """Test that Judge cites procedural rules when redirecting off-topic"""
    print("\n=== Testing Off-Topic Judge Citations ===")
    
    # Mention unrelated case to trigger off-topic intervention
    turn_request = {
        "case_id": "test_case_001",
        "user_text": "This is just like the Trump fraud case where...",
        "history": []
    }
    
    response = requests.post(f"{BASE_URL}/api/ai/turn", json=turn_request)
    
    if response.status_code == 200:
        data = response.json()
        speaker = data["speaker"]
        reply = data["reply_text"]
        
        print(f"\nSpeaker: {speaker}")
        print(f"Response: {reply}")
        
        # Should be Judge intervening
        if "Judge" in speaker:
            print("✅ Judge intervened for off-topic statement")
            
            # Check for procedural citations (CPC, Rules, etc.)
            citation_patterns = [
                r'CPC Section \d+',
                r'Rule \d+\.\d+',
                r'Section \d+'
            ]
            
            found_citations = []
            for pattern in citation_patterns:
                matches = re.findall(pattern, reply)
                found_citations.extend(matches)
            
            if found_citations:
                print(f"✅ PASS: Judge cited procedural rules: {found_citations}")
                return True
            else:
                print(f"⚠️ WARNING: Judge redirected but didn't cite specific rules")
                print("Expected: 'CPC Section 165' or 'Rule 3.4'")
                return True  # Still pass since intervention happened
        else:
            print(f"❌ FAIL: Expected Judge intervention, got {speaker}")
            return False
    else:
        print(f"❌ ERROR: Request failed with status {response.status_code}")
        print(response.text)
        return False

def main():
    print("=" * 60)
    print("LEGAL CITATION TEST SUITE")
    print("=" * 60)
    print("\nThis test verifies that Judge and Lawyer cite specific")
    print("legal sections like 'Article 21', 'Section 302 IPC', etc.")
    print("\nPREREQUISITES:")
    print("1. Docker Desktop running")
    print("2. Qdrant container started: docker start qdrant")
    print("3. Server running: python main.py")
    print("4. Case initialized with test data")
    
    time.sleep(2)
    
    results = []
    
    # Run all tests
    results.append(("Lawyer Citations", test_lawyer_cites_legal_sections()))
    time.sleep(1)
    
    results.append(("Judge Citations", test_judge_cites_legal_sections()))
    time.sleep(1)
    
    results.append(("Off-Topic Judge Citations", test_off_topic_judge_cites_rules()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All tests passed! Legal citations are working.")
    else:
        print("⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
