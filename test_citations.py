"""
Test RAG citation system
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_citations():
    """Test that lawyer responses include citations from case documents"""
    
    print("=" * 70)
    print("TESTING RAG CITATION SYSTEM")
    print("=" * 70)
    
    # 1. Initialize a case with clear evidence sections
    case_text = """
    CASE NO. 2024-CR-12345: State of California vs. John Doe
    
    CHARGES: Robbery at convenience store on Main Street
    
    EVIDENCE SECTION 1 - GPS DATA:
    GPS data from Sprint cell towers shows the defendant's mobile phone 
    (number ending in 5678) was located within 100 meters of the crime 
    scene at 415 Main Street between 10:40 PM and 10:50 PM on January 15, 2024. 
    The data was triangulated using three separate cell towers with 95% accuracy.
    
    EVIDENCE SECTION 2 - SECURITY FOOTAGE:
    Security camera footage from the convenience store shows a person matching 
    the defendant's physical description (5'10", brown jacket, baseball cap) 
    entering the store at 10:42 PM. The person is seen approaching the counter 
    with what appears to be a weapon at 10:43 PM.
    
    EVIDENCE SECTION 3 - WITNESS TESTIMONY:
    Store clerk Maria Rodriguez identified the defendant in a photo lineup 
    with high confidence. She stated the robber had a distinctive tattoo 
    on his left forearm, matching the defendant's documented tattoos.
    
    TIMELINE:
    - 10:40 PM: Defendant's phone detected near crime scene
    - 10:42 PM: Person enters store (captured on video)
    - 10:43 PM: Robbery occurs
    - 10:45 PM: Suspect flees
    - 10:50 PM: Defendant's phone still in area
    """
    
    print("\n1. Initializing case with detailed evidence...")
    response = requests.post(f"{BASE_URL}/api/ai/init_case", json={
        "case_id": "citation_test_001",
        "pdf_text": case_text
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Case initialized")
        print(f"   Summary: {result['summary'][:100]}...")
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    time.sleep(3)  # Let Qdrant index
    
    # 2. Test with user challenging GPS evidence
    print("\n" + "=" * 70)
    print("TEST 1: User challenges GPS evidence")
    print("=" * 70)
    
    test_queries = [
        {
            "query": "The GPS evidence seems unreliable and circumstantial",
            "expected_citation": "GPS",
            "test_name": "GPS Evidence Challenge"
        },
        {
            "query": "What about the security footage? It could be anyone",
            "expected_citation": "Security",
            "test_name": "Video Evidence Challenge"
        },
        {
            "query": "The witness identification could be wrong",
            "expected_citation": "witness",
            "test_name": "Witness Testimony Challenge"
        }
    ]
    
    for test in test_queries:
        print(f"\n{'='*70}")
        print(f"Test: {test['test_name']}")
        print(f"{'='*70}")
        print(f"User says: \"{test['query']}\"")
        
        response = requests.post(f"{BASE_URL}/api/ai/turn", json={
            "case_id": "citation_test_001",
            "user_text": test['query'],
            "history": []
        })
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n🎭 {result['speaker']} responds:")
            print(f"   {result['reply_text']}")
            print(f"   [Emotion: {result['emotion']}]")
            
            # Check citations
            citations = result.get('citations', [])
            print(f"\n📚 Citations ({len(citations)} total):")
            if citations:
                for i, citation in enumerate(citations, 1):
                    print(f"   {i}. {citation[:80]}...")
                print(f"\n✅ SUCCESS: Citations included!")
                
                # Check if response references sources
                if "[Source" in result['reply_text']:
                    print(f"✅ Response includes [Source X] references in text")
                else:
                    print(f"⚠️ Response doesn't explicitly reference sources")
            else:
                print(f"   ❌ NO CITATIONS FOUND")
            
        else:
            print(f"❌ Request failed: {response.text}")
        
        time.sleep(2)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Citations should:")
    print("  1. Be present in citations[] array")
    print("  2. Reference relevant case document sections")
    print("  3. Be mentioned in AI response as [Source 1], [Source 2], etc.")
    print("\nThis allows users to verify claims against source documents!")

if __name__ == "__main__":
    try:
        test_citations()
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error - Server not running")
        print("Run: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
