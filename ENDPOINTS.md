# AI Engine API Endpoints - Backend Integration Guide

## Base Configuration

**Base URL:** `http://localhost:8000/api/ai`  
**Production URL:** `https://your-domain.com/api/ai`

**Content-Type:** `application/json`  
**Timeout Recommendations:**
- init_case: 60 seconds
- init_legal_laws: 60 seconds
- turn: 30 seconds
- analyze: 60 seconds

---

## Endpoint 1: Initialize Legal Laws Database

**Method:** `POST`  
**Endpoint:** `/api/ai/init_legal_laws`  
**When to call:** Once at application startup or when updating legal database

### Request Body
```json
{
  "legal_text": "string (required) - Full text of constitutional laws, procedures, and guidelines",
  "collection_name": "string (optional) - Collection name, defaults to 'legal_laws'"
}
```

### Response (200 OK)
```json
{
  "message": "Legal laws database initialized successfully",
  "collection_name": "legal_laws_guidelines",
  "chunks_processed": 8
}
```

### Example cURL
```bash
curl -X POST http://localhost:8000/api/ai/init_legal_laws \
  -H "Content-Type: application/json" \
  -d '{
    "legal_text": "Article I: Right to Legal Counsel...",
    "collection_name": "legal_laws"
  }'
```

### Example Node.js
```javascript
const response = await axios.post('http://localhost:8000/api/ai/init_legal_laws', {
  legal_text: constitutionalLawsText,
  collection_name: 'legal_laws'
});
console.log(`Loaded ${response.data.chunks_processed} legal chunks`);
```

---

## Endpoint 2: Initialize Case

**Method:** `POST`  
**Endpoint:** `/api/ai/init_case`  
**When to call:** Each time a new case is loaded for a user

### Request Body
```json
{
  "case_id": "string (required) - Unique identifier for the case",
  "pdf_text": "string (required) - Full text content extracted from PDF case file"
}
```

### Response (200 OK)
```json
{
  "message": "Case case_123 vectorized successfully",
  "summary": "The parties involved in this case are the State of California and the defendant, John Doe. The main legal issue revolves around..."
}
```

### Example cURL
```bash
curl -X POST http://localhost:8000/api/ai/init_case \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case_123",
    "pdf_text": "The State of California vs. John Doe..."
  }'
```

### Example Node.js
```javascript
const caseText = await extractPdfText('case_file.pdf');
const response = await axios.post('http://localhost:8000/api/ai/init_case', {
  case_id: 'case_123',
  pdf_text: caseText
});
console.log('Case Summary:', response.data.summary);
```

---

## Endpoint 3: Chat Turn (Dual-Agent System)

**Method:** `POST`  
**Endpoint:** `/api/ai/turn`  
**When to call:** Every time user sends a message in VR

### Request Body
```json
{
  "case_id": "string (required) - Case identifier",
  "user_statement": "string (required) - User's argument or statement",
  "turn_number": "integer (required) - Current turn number (1, 2, 3...)"
}
```

### Response (200 OK)
```json
{
  "agent_role": "lawyer | judge",
  "agent_response": "AI agent's response text",
  "case_context_used": "Snippet of case facts used in response",
  "legal_context_used": "Snippet of legal guidelines used",
  "errors_detected": false
}
```

### Agent Roles
- **`lawyer`** - Opposing counsel. Responds when user makes valid legal arguments
- **`judge`** - Neutral arbiter. Intervenes when user makes factual/legal errors

### Example cURL (Lawyer Response)
```bash
curl -X POST http://localhost:8000/api/ai/turn \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case_123",
    "user_statement": "I want to challenge the GPS evidence reliability",
    "turn_number": 1
  }'
```

**Response:**
```json
{
  "agent_role": "lawyer",
  "agent_response": "While you raise GPS reliability, the data shows consistent location for 45 minutes across multiple cell towers. How do you explain this sustained presence?",
  "case_context_used": "GPS data from phone records; Cell tower triangulation...",
  "legal_context_used": "Article VII: GPS and Electronic Evidence...",
  "errors_detected": false
}
```

### Example cURL (Judge Intervention)
```bash
curl -X POST http://localhost:8000/api/ai/turn \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "case_123",
    "user_statement": "I will force my client to testify",
    "turn_number": 2
  }'
```

**Response:**
```json
{
  "agent_role": "judge",
  "agent_response": "Counsel, I must intervene. You cannot compel your client to testify. The Fifth Amendment protects against self-incrimination.",
  "case_context_used": "",
  "legal_context_used": "Fifth Amendment: Right against self-incrimination...",
  "errors_detected": true
}
```

### Example Node.js
```javascript
const response = await axios.post('http://localhost:8000/api/ai/turn', {
  case_id: currentCase.id,
  user_statement: userInput,
  turn_number: currentTurn
});

// Check which agent responded
if (response.data.agent_role === 'judge') {
  // Judge intervention - play judge avatar/audio
  console.log('⚖️ Judge:', response.data.agent_response);
  playJudgeAnimation();
} else {
  // Lawyer response - play lawyer avatar/audio
  console.log('👔 Lawyer:', response.data.agent_response);
  playLawyerAnimation();
}

// Send to TTS for voice
await textToSpeech(response.data.agent_response);
```

---

## Endpoint 4: Analyze Performance

**Method:** `POST`  
**Endpoint:** `/api/ai/analyze`  
**When to call:** After case/session ends for performance review

### Request Body
```json
{
  "transcript": [
    {
      "role": "user | assistant",
      "content": "Message content"
    }
  ]
}
```

### Response (200 OK)
```json
{
  "score": 85,
  "feedback": "Strong use of evidence and clear articulation. You effectively challenged the GPS data. Consider citing specific legal precedents to strengthen arguments.",
  "summary": "The user demonstrated good legal reasoning and evidence presentation skills."
}
```

### Score Ranges
- **90-100:** Excellent
- **80-89:** Good
- **70-79:** Satisfactory
- **60-69:** Needs Improvement
- **0-59:** Poor

### Example cURL
```bash
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": [
      {"role": "user", "content": "I want to present an alibi defense"},
      {"role": "assistant", "content": "An alibi requires corroboration..."},
      {"role": "user", "content": "My client was home with his girlfriend"}
    ]
  }'
```

### Example Node.js
```javascript
const transcript = conversationHistory.map(msg => ({
  role: msg.sender === 'user' ? 'user' : 'assistant',
  content: msg.text
}));

const analysis = await axios.post('http://localhost:8000/api/ai/analyze', {
  transcript: transcript
});

console.log(`Score: ${analysis.data.score}/100`);
console.log(`Feedback: ${analysis.data.feedback}`);

// Save to database
await savePerformanceReport(userId, caseId, analysis.data);
```

---

## Endpoint 5: Health Check

**Method:** `GET`  
**Endpoint:** `/`  
**When to call:** Application startup, periodic health checks

### Response (200 OK)
```json
{
  "service": "VerdicTech AI Engine",
  "status": "running",
  "version": "1.0.0"
}
```

### Example cURL
```bash
curl http://localhost:8000/
```

### Example Node.js
```javascript
try {
  const response = await axios.get('http://localhost:8000/');
  if (response.data.status === 'running') {
    console.log('✅ AI Engine is healthy');
  }
} catch (error) {
  console.error('❌ AI Engine is down');
}
```

---

## Error Responses

All endpoints may return error responses:

### 422 Unprocessable Entity (Validation Error)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "case_id"],
      "msg": "Field required"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to initialize case: Connection timeout"
}
```

---

## Complete Integration Flow

```javascript
// 1. On application startup - Initialize legal laws (once)
await axios.post('/api/ai/init_legal_laws', {
  legal_text: fs.readFileSync('legal_laws.txt', 'utf8')
});

// 2. When user selects a case - Initialize case
const pdfText = await extractPdfText(casePdfPath);
const caseInit = await axios.post('/api/ai/init_case', {
  case_id: `case_${userId}_${timestamp}`,
  pdf_text: pdfText
});
console.log('Case Summary:', caseInit.data.summary);

// 3. During VR session - Chat turns
let turnNumber = 1;
while (sessionActive) {
  const userInput = await getUserVoiceInput(); // From VR
  
  const response = await axios.post('/api/ai/turn', {
    case_id: currentCaseId,
    user_statement: userInput,
    turn_number: turnNumber++
  });
  
  // Play appropriate avatar based on agent
  if (response.data.agent_role === 'judge') {
    await playJudgeAvatar(response.data.agent_response);
  } else {
    await playLawyerAvatar(response.data.agent_response);
  }
  
  // Store in conversation history
  conversationHistory.push({
    turn: turnNumber - 1,
    user: userInput,
    agent_role: response.data.agent_role,
    agent_response: response.data.agent_response
  });
}

// 4. After session ends - Get performance analysis
const analysis = await axios.post('/api/ai/analyze', {
  transcript: conversationHistory.map(h => [
    { role: 'user', content: h.user },
    { role: 'assistant', content: h.agent_response }
  ]).flat()
});

// Display results to user
displayPerformanceReport(analysis.data);
```

---

## Node.js Client Library

Use the included `aiEngineClient.js` wrapper for easier integration:

```javascript
const aiEngine = require('./services/aiEngineClient');

// Initialize (startup)
await aiEngine.initLegalLaws(legalText);

// Per case
await aiEngine.initCase(caseId, pdfText);

// Chat
const response = await aiEngine.getChatResponse(caseId, userStatement, turnNumber);

// Analyze
const analysis = await aiEngine.analyzePerformance(transcript);
```

---

## Environment Variables

Required on AI Engine server:
```env
OPENAI_API_KEY=sk-your-api-key
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

Required in Node.js backend:
```env
AI_ENGINE_URL=http://localhost:8000/api/ai
```

---

## Performance Characteristics

**Response Times (with gpt-3.5-turbo):**
- init_legal_laws: 3-5s
- init_case: 5-10s (depends on PDF size)
- turn: 0.5-2s (optimized for VR)
- analyze: 10-15s

**Recommendations:**
- Cache case initialization results
- Show loading indicators in VR during calls
- Implement retry logic with exponential backoff
- Monitor health endpoint every 30 seconds

---

## Support

- Full API documentation: See [API_DOCS.md](API_DOCS.md)
- Performance optimization guide: See [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md)
- Docker deployment: See [DOCKER.md](DOCKER.md)
