"""
Quick test of new lawyer behavior with a simple example
"""
import requests

url = "http://localhost:8000/api/ai/turn"

# Initialize case first
case_init = requests.post("http://localhost:8000/api/ai/init_case", json={
    "case_id": "quick_test_123",
    "pdf_text": """
    CASE: State vs. Defendant
    EVIDENCE: GPS shows defendant's phone at crime scene at 10:43 PM
    Security footage shows person matching defendant at store at same time
    """
})

print(f"Case init: {case_init.status_code}")

# Test 1: User presents argument
print("\n" + "="*60)
print("TEST: User presents GPS evidence challenge")
print("="*60)

response1 = requests.post(url, json={
    "case_id": "quick_test_123",
    "user_text": "Your Honor, I believe the GPS evidence is unreliable and doesn't prove my client was at the crime scene.",
    "history": []
})

result1 = response1.json()
print(f"\n{result1['speaker']} says:")
print(f'"{result1["reply_text"]}"')
print(f"Emotion: {result1['emotion']}")

# Check if it starts with "Objection!"
if result1['reply_text'].lower().startswith('objection'):
    print("\n❌ PROBLEM: Still using 'Objection!' - too aggressive")
else:
    print("\n✅ GOOD: Not starting with objection - more professional")

# Test 2: User makes another point
print("\n" + "="*60)
print("TEST: User challenges witness testimony")
print("="*60)

response2 = requests.post(url, json={
    "case_id": "quick_test_123",
    "user_text": "The witness testimony may be unreliable due to poor lighting conditions.",
    "history": [
        {"role": "user", "content": "I believe the GPS evidence is unreliable"},
        {"role": "assistant", "content": result1["reply_text"]}
    ]
})

result2 = response2.json()
print(f"\n{result2['speaker']} says:")
print(f'"{result2["reply_text"]}"')
print(f"Emotion: {result2['emotion']}")

if result2['reply_text'].lower().startswith('objection'):
    print("\n❌ PROBLEM: Still using 'Objection!'")
else:
    print("\n✅ GOOD: Professional response without objection")

print("\n" + "="*60)
print("SUMMARY:")
print("="*60)
print("The lawyer should now present arguments like:")
print('  "Your Honor, the GPS data shows..." ')
print('  "The evidence demonstrates..."')
print('  "But the testimony confirms..."')
print("\nInstead of constantly saying:")
print('  "Objection! The GPS data shows..."')
print('  "Objection! I must refute..."')
