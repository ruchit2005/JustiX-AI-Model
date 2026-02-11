# VerdicTech AI Engine - API Documentation

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

### 3. Chat Turn

**Endpoint:** `POST /api/ai/turn`

**Description:** Process a conversation turn using RAG. The AI retrieves relevant facts from the case and generates a response as opposing counsel or judge.

**Request Body:**
```json
{
  "case_id": "string (required) - Case identifier",
  "user_text": "string (required) - User's argument or statement",
  "history": [
    {
      "role": "string - 'user' or 'assistant'",
      "content": "string - Message content"
    }
  ]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/ai/turn \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case_123",
    "user_text": "My client was not at the scene.",
    "history": [
      {"role": "user", "content": "I move to dismiss..."},
      {"role": "assistant", "content": "Motion denied..."}
    ]
  }'
```

**Response:**
```json
{
  "reply_text": "Objection! GPS data from your client's phone places him within 100 meters of the crime scene at 10:43 PM.",
  "speaker": "Lawyer",
  "emotion": "Aggressive"
}
```

**Speaker Types:**
- `Lawyer` - Opposing counsel
- `Judge` - Neutral arbiter
- `System` - Error or system message

**Emotion Types:**
- `Assertive` - Confident, professional
- `Aggressive` - Forceful objection
- `Questioning` - Probing, inquisitive
- `Neutral` - Calm, matter-of-fact

**Status Codes:**
- `200 OK` - Response generated successfully
- `500 Internal Server Error` - Failed to process turn

---

### 4. Analyze Performance

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
1. Initialize Case
   Node.js → POST /init_case → Python
   Python → Split text → Embeddings → Qdrant
   Python → GPT-4 summary → Node.js

2. Chat Turn
   Node.js → POST /turn → Python
   Python → Query Qdrant → Retrieve context
   Python → GPT-4 generation → Node.js
   Node.js → TTS → Audio → VR

3. Analysis
   Node.js → POST /analyze → Python
   Python → GPT-4 evaluation → Node.js
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

  async chatTurn(caseId, userText, history = []) {
    const response = await axios.post(`${this.apiURL}/turn`, {
      case_id: caseId,
      user_text: userText,
      history: history
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

// Initialize a case
const initResult = await aiEngine.initCase('case_123', pdfText);
console.log('Summary:', initResult.summary);

// Chat
const chatResult = await aiEngine.chatTurn('case_123', 'My client is innocent.');
console.log('AI:', chatResult.reply_text);

// Analyze
const analysis = await aiEngine.analyze(transcript);
console.log('Score:', analysis.score);
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
