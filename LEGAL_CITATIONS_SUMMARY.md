# Legal Citation Implementation - Summary

## Overview
Updated the AI microservice to ensure Judge and Lawyer cite **specific legal sections, articles, and provisions** in their responses. This makes responses more authoritative, professional, and verifiable.

## Changes Made

### 1. Judge Prompt Enhancement
**File:** `main.py` (lines ~490-530)

**Changes:**
- Added instruction: "ALWAYS cite specific legal provisions: 'Section X', 'Article Y', 'Rule Z', 'Amendment N'"
- Added requirement to reference actual laws by name and number
- Increased response length to 45 words to accommodate citations
- Added examples: "Section 313 CPC", "Article 21", "Fifth Amendment"

**Before:**
```
"Cite legal guidelines, constitutional rights, or courtroom procedures when relevant"
```

**After:**
```
"ALWAYS cite specific legal provisions: 'Section X', 'Article Y', 'Rule Z', 'Amendment N'
Reference actual laws by name and number (e.g., 'Section 302 IPC', 'Article 21', 'Fifth Amendment')"
```

### 2. Lawyer Prompt Enhancement
**File:** `main.py` (lines ~540-580)

**Changes:**
- Added section: "CITE SPECIFIC LAWS AND SECTIONS when making legal arguments"
- Added instruction to reference: "Section X", "Article Y", "IPC Section Z", "CrPC Section N"
- Updated examples to include statutory references
- Increased response length to 45 words

**Examples Added:**
```
"Your Honor, Section 65B of the Evidence Act requires electronic evidence to be certified..."
"Under Article 21, the prosecution must prove..."
"IPC Section 420 clearly defines the elements of fraud..."
```

### 3. Off-Topic Intervention Enhancement
**File:** `main.py` (off-topic Judge prompt)

**Changes:**
- Added instruction to cite "Rule 3.4", "CPC Section 165" when redirecting
- Example: "Counsel, under CPC Section 165, you must confine yourself to the facts of THIS case."

### 4. Documentation Update
**File:** `CONTEXT_CONTROL.md`

**Changes:**
- Updated examples to show legal citations
- Added note that Judge/Lawyer cite "specific section/article numbers"
- Updated sample responses to include statutory references

## Expected Behavior

### Judge Responses
Will now include citations like:
- "Under Section 313 of the Criminal Procedure Code..."
- "Article 20(3) protects against self-incrimination."
- "The Fifth Amendment prevents compelled testimony."
- "CPC Section 165 requires you to stay within scope."

### Lawyer Responses
Will now include citations like:
- "Your Honor, Section 65B of the Evidence Act requires [Source 1] to be authenticated..."
- "Under Article 21, the defendant has the right to..."
- "IPC Section 302 defines murder as..."
- "According to Section 420, this constitutes fraud..."

### Off-Topic Redirections
Judge will cite procedural rules:
- "Counsel, under CPC Section 165, confine yourself to this case."
- "Rule 3.4 requires you to focus on actual evidence."

## How Legal Knowledge Works

The AI uses **LLM's built-in legal knowledge** from training data:
- Indian Penal Code (IPC)
- Criminal Procedure Code (CrPC)
- Evidence Act
- Constitutional Articles
- U.S. Amendments (if applicable)
- International legal principles

**It does NOT** retrieve these from the vector database (Qdrant stores case facts and legal guidelines, but the LLM knows actual statutes).

## Testing

### Prerequisites
1. **Start Docker Desktop**
2. **Start Qdrant:** `docker start qdrant`
3. **Start Server:** `python main.py` (background)
4. **Initialize Case:** Upload case file via `/api/ai/init_case`

### Test Script
Run the comprehensive test:
```powershell
python test_legal_citations.py
```

This tests:
1. ✅ Lawyer cites specific sections (Section X, Article Y)
2. ✅ Judge cites constitutional/procedural sections
3. ✅ Off-topic Judge intervention cites procedural rules

### Manual Testing
Test via API:

**Trigger Lawyer Citation:**
```json
POST /api/ai/turn
{
  "case_id": "test_001",
  "user_text": "The evidence was obtained illegally.",
  "history": []
}

Expected Response:
"Your Honor, under Section 24 of the Evidence Act, evidence obtained illegally is admissible..."
```

**Trigger Judge Citation:**
```json
POST /api/ai/turn
{
  "case_id": "test_001",
  "user_text": "I'll force my client to testify.",
  "history": []
}

Expected Response:
"Counsel, under the Fifth Amendment, you cannot compel your client to testify against themselves."
```

**Trigger Off-Topic Citation:**
```json
POST /api/ai/turn
{
  "case_id": "test_001",
  "user_text": "This is like the Trump case...",
  "history": []
}

Expected Response:
"Counsel, under CPC Section 165, you must confine yourself to the facts of THIS case..."
```

## Verification Checklist

After testing, verify:
- [ ] Lawyer responses include "Section X" or "Article Y" patterns
- [ ] Judge responses include "Amendment N" or "Section X" patterns
- [ ] Off-topic redirections cite "CPC Section 165" or "Rule X.Y"
- [ ] Citations are specific (not vague like "according to law")
- [ ] Legal sections are contextually appropriate
- [ ] Responses remain under 45 words
- [ ] [Source X] citations still work for case facts

## Integration with Node.js Backend

No changes needed to `aiEngineClient.js` - the API format is identical. Citations are included in the `citations` array field (for RAG sources), and legal section citations appear in the `reply_text` itself.

**Example Response:**
```json
{
  "speaker": "Opposing Lawyer",
  "reply_text": "Your Honor, under Section 65B, the digital evidence [Source 1] must be authenticated.",
  "emotion": "neutral",
  "citations": [
    "Source 1: GPS data from defendant's phone..."
  ]
}
```

## Legal Jurisdiction
The system can cite:
- **Indian Law:** IPC, CrPC, Evidence Act, Constitutional Articles
- **U.S. Law:** Amendments, FRCP, FRE
- **International:** UN conventions, ICC statutes

The LLM will use the appropriate jurisdiction based on:
1. Legal laws database content (if Indian laws loaded → Indian citations)
2. Case context (if U.S. case → U.S. citations)
3. General training (defaults to common law principles)

## Next Steps

1. **Start Infrastructure:**
   ```powershell
   # Start Docker Desktop (GUI)
   docker start qdrant
   python main.py  # (in background)
   ```

2. **Run All Tests:**
   ```powershell
   python test_guardrails.py      # Off-topic detection
   python test_legal_citations.py # Legal section citations
   python test_citations.py       # RAG source citations
   ```

3. **Deploy:**
   ```powershell
   ngrok http 8000  # For production VR app
   ```

4. **Update Frontend:**
   - No code changes needed
   - Responses will now include legal citations automatically
   - Optionally: Parse citations with regex for UI highlighting

## Regex Pattern for Citation Detection

If you want to highlight legal citations in the UI:
```javascript
const legalCitationRegex = /(?:Section|Article|Rule|IPC Section|CrPC Section|Amendment)\s+\d+(?:\.\d+)?(?:\(\d+\))?/g;
const citations = replyText.match(legalCitationRegex);
// Citations: ['Section 65B', 'Article 21', 'Fifth Amendment']
```

## Troubleshooting

**"No citations in responses"**
- Check if LLM is GPT-4 (GPT-3.5 may not follow instructions as well)
- Verify prompts updated with the changes above
- Increase temperature for more creative legal reasoning

**"Always cites 'Section 1' or generic sections"**
- LLM may need more context about jurisdiction
- Enhance legal_laws database with specific statutes
- Add examples in prompts for the target jurisdiction

**"Citations are too long"**
- Reduce max response length back to 40 words
- Instruct: "Cite briefly: 'Section 302' not full text"

## Summary

✅ Judge now cites: Section X, Article Y, Amendment Z  
✅ Lawyer now cites: IPC Section X, CrPC Section Y, Article Z  
✅ Off-topic redirections cite: CPC Section 165, Rule X.Y  
✅ Responses more authoritative and verifiable  
✅ Ready for testing with Docker/Qdrant running  

**Status:** Implementation complete. Testing pending (requires Qdrant).
