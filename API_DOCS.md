# VerdicTech AI Engine - API Documentation

## Overview

The VerdicTech AI Engine is an intelligent legal training system featuring a **dual-agent architecture**:

### Dual-Agent System
- **Lawyer Agent** (Opposing Counsel): Challenges user's arguments, presents counter-evidence, and acts as prosecution
- **Judge Agent** (Neutral Arbiter): Monitors the conversation and intervenes when the user makes:
  - **Factual errors**: Claims not supported by case evidence
  - **Legal errors**: Violations of legal procedures or constitutional rights

### Dual-RAG Architecture
The system uses two separate vector databases:
1. **Case-Specific RAG**: Contains facts, evidence, and details from the current case
2. **Legal Laws RAG**: Contains constitutional laws, legal procedures, and guidelines

Both agents have access to both knowledge bases, enabling them to ground responses in case facts while citing legal authority.

### Intelligent Role Switching
On each turn:
1. System analyzes user statement for errors using LLM
2. **If errors detected** → Judge intervenes with educational correction
3. **If no errors** → Lawyer responds with challenging counter-arguments

This creates a realistic legal training environment where users learn from mistakes while building advocacy skills.

---

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required. Add API keys in production.

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /`

**Description:** Check if the server is running

**Response:**
```json
{
  "service": "VerdicTech AI Engine",
  "status": "running",
  "version": "1.0.0"
}
```

---

### 2. Initialize Case

**Endpoint:** `POST /api/ai/init_case`

**Description:** Initialize a new legal case by vectorizing the case text and storing it in Qdrant. This must be called before any chat interactions for a case.

**Request Body:**
```json
{
  "case_id": "string (required) - Unique identifier for the case",
  "pdf_text": "string (required) - Full text content of the PDF case file"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/ai/init_case \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case_123",
    "pdf_text": "The State of California vs. John Smith..."
  }'
```

**Response:**
```json
{
  "message": "Case case_123 vectorized successfully",
  "summary": "This case involves a criminal dispute between the State and John Smith regarding alleged robbery. Key evidence includes GPS data and security footage. The defense claims an alibi."
}
```

**Status Codes:**
- `200 OK` - Case initialized successfully
- `500 Internal Server Error` - Failed to process case

---

### 3. Initialize Legal Laws

**Endpoint:** `POST /api/ai/init_legal_laws`

**Description:** Initialize the legal laws vector database with constitutional laws, procedures, and guidelines. This creates a separate knowledge base that both agents (Lawyer and Judge) can reference.

**Request Body:**
```json
{
  "legal_text": "string (required) - Full text of constitutional laws and legal guidelines",
  "collection_name": "string (optional) - Collection name, defaults to 'legal_laws'"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/ai/init_legal_laws \
  -H "Content-Type: application/json" \
  -d '{
    "legal_text": "Article I: Right to Legal Counsel...",
    "collection_name": "legal_laws"
  }'
```

**Response:**
```json
{
  "message": "Legal laws vectorized successfully",
  "collection_name": "legal_laws",
  "chunks_processed": 42
}
```

**Status Codes:**
- `200 OK` - Legal laws initialized successfully
- `500 Internal Server Error` - Failed to process legal text

---

### 4. Chat Turn (Dual-Agent System)

**Endpoint:** `POST /api/ai/turn`

**Description:** Process a conversation turn using RAG with intelligent dual-agent system. The AI dynamically switches between **Lawyer** (opposing counsel) and **Judge** (neutral arbiter) roles based on user behavior:
- **Lawyer responds** when user makes valid legal arguments
- **Judge intervenes** when user makes factual errors or violates legal procedures

**Request Body:**
```json
{
  "case_id": "string (required) - Case identifier",
  "user_statement": "string (required) - User's argument or statement",
  "turn_number": "integer (required) - Current turn number"
}
```

**Example Request (Normal Lawyer Response):**
```bash
curl -X POST http://localhost:8000/api/ai/turn \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case_123",
    "user_statement": "I believe the GPS evidence is unreliable due to signal interference in urban areas.",
    "turn_number": 1
  }'
```

**Response (Lawyer):**
```json
{
  "agent_role": "lawyer",
  "agent_response": "While you raise an interesting technical point about GPS accuracy, the data shows your client's phone was consistently near the crime scene for 45 minutes, not just a brief ping. Multiple cell towers triangulated the location. How do you explain this sustained presence?",
  "case_context_used": "GPS data from phone records; Cell tower triangulation data",
  "legal_context_used": "GPS and Electronic Evidence standards",
  "errors_detected": false
}
```

**Example Request (Triggering Judge Intervention):**
```bash
curl -X POST http://localhost:8000/api/ai/turn \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case_123",
    "user_statement": "I will force my client to testify even though they do not want to.",
    "turn_number": 2
  }'
```

**Response (Judge Intervention):**
```json
{
  "agent_role": "judge",
  "agent_response": "Counselor, I must stop you there. You cannot compel your client to testify against their will. The Fifth Amendment protects your client's right against self-incrimination. As their attorney, you must respect their decision whether or not to take the stand. This is a fundamental constitutional protection.",
  "case_context_used": "",
  "legal_context_used": "Fifth Amendment: Right against self-incrimination; Attorney Conduct standards",
  "errors_detected": true
}
```

**Agent Roles:**
- `lawyer` - Opposing counsel (prosecution). Challenges user's arguments, presses on weaknesses, presents counter-evidence
- `judge` - Neutral arbiter. Intervenes when user makes factual errors or violates legal procedures. Educates on proper legal conduct

**Dual-Agent Logic:**
- System analyzes user statement for factual/legal errors
- **If errors detected** → Judge responds with correction and guidance
- **If no errors** → Lawyer responds with counter-arguments and challenges

**Status Codes:**
- `200 OK` - Response generated successfully
- `500 Internal Server Error` - Failed to process turn

---

### 5. Analyze Performance

**Endpoint:** `POST /api/ai/analyze`

**Description:** Analyze the full conversation transcript and provide performance feedback and scoring.

**Request Body:**
```json
{
  "transcript": [
    {
      "role": "string - 'user' or 'assistant'",
      "content": "string - Message content"
    }
  ]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": [
      {"role": "user", "content": "I move to dismiss the GPS evidence."},
      {"role": "assistant", "content": "On what grounds?"},
      {"role": "user", "content": "The evidence is unreliable."},
      {"role": "assistant", "content": "Objection overruled."}
    ]
  }'
```

**Response:**
```json
{
  "score": 85,
  "feedback": "Strong use of evidence and clear articulation. You effectively challenged the GPS data and presented a credible alibi defense. However, consider citing specific legal precedents to strengthen your arguments. Your handling of objections was professional.",
  "summary": "The user demonstrated good legal reasoning and evidence presentation skills. Minor improvements needed in citing precedents."
}
```

**Score Range:** 0-100
- 90-100: Excellent
- 80-89: Good
- 70-79: Satisfactory
- 60-69: Needs Improvement
- 0-59: Poor

**Status Codes:**
- `200 OK` - Analysis completed successfully
- `500 Internal Server Error` - Failed to analyze

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common errors:
- `Case not initialized` - Call `/init_case` first
- `OPENAI_API_KEY not found` - Check environment configuration
- `Failed to connect to Qdrant` - Ensure Qdrant is running

---

## Rate Limits

Currently no rate limits. Implement in production:
- Recommended: 100 requests/minute per IP
- Burst: 20 requests/second

---

## Data Flow

```
1. Initialize Legal Laws (One-time setup)
   Node.js → POST /init_legal_laws → Python
   Python → Split text → Embeddings → Qdrant (legal_laws collection)
   Python → Confirmation → Node.js

2. Initialize Case (Per case)
   Node.js → POST /init_case → Python
   Python → Split text → Embeddings → Qdrant (case collection)
   Python → GPT-3.5 summary → Node.js

3. Chat Turn (Dual-Agent System)
   Node.js → POST /turn → Python
   
   Python → Query Qdrant (case collection) → Retrieve case context
   Python → Query Qdrant (legal_laws collection) → Retrieve legal context
   Python → GPT-3.5 error detection → Analyze user statement
   
   IF errors detected:
     Python → Generate Judge response (with legal citations) → Node.js
   ELSE:
     Python → Generate Lawyer response (with case facts) → Node.js
   
   Node.js → TTS → Audio → VR Application

4. Analysis
   Node.js → POST /analyze → Python
   Python → GPT-3.5 evaluation → Node.js
   Node.js → Save to database → Display to user
```

---

## Node.js Integration Example

```javascript
const axios = require('axios');

class AIEngineClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.apiURL = `${baseURL}/api/ai`;
  }

  async initCase(caseId, pdfText) {
    const response = await axios.post(`${this.apiURL}/init_case`, {
      case_id: caseId,
      pdf_text: pdfText
    });
    return response.data;
  }

  async initLegalLaws(legalText, collectionName = 'legal_laws') {
    const response = await axios.post(`${this.apiURL}/init_legal_laws`, {
      legal_text: legalText,
      collection_name: collectionName
    });
    return response.data;
  }

  async chatTurn(caseId, userStatement, turnNumber) {
    const response = await axios.post(`${this.apiURL}/turn`, {
      case_id: caseId,
      user_statement: userStatement,
      turn_number: turnNumber
    });
    return response.data;
  }

  async analyze(transcript) {
    const response = await axios.post(`${this.apiURL}/analyze`, {
      transcript: transcript
    });
    return response.data;
  }
}

// Usage
const aiEngine = new AIEngineClient();

// Initialize legal laws (once at startup)
const legalInit = await aiEngine.initLegalLaws(constitutionalLawsText);
console.log('Legal laws loaded:', legalInit.chunks_processed, 'chunks');

// Initialize a case
const initResult = await aiEngine.initCase('case_123', pdfText);
console.log('Case summary:', initResult.summary);

// Chat with dual-agent system
const turn1 = await aiEngine.chatTurn('case_123', 'I want to present an alibi defense.', 1);
console.log(`${turn1.agent_role}:`, turn1.agent_response);
// Output: "lawyer: An alibi defense requires solid corroboration..."

const turn2 = await aiEngine.chatTurn('case_123', 'I will coach my witness on what to say.', 2);
console.log(`${turn2.agent_role}:`, turn2.agent_response);
// Output: "judge: Counselor! You cannot coach witnesses. That violates legal ethics..."

// Analyze performance
const analysis = await aiEngine.analyze(transcript);
console.log('Score:', analysis.score);
console.log('Feedback:', analysis.feedback);
```

---

## Testing

Use the provided `test_client.py`:

```bash
python test_client.py
```

Or use the FastAPI interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
