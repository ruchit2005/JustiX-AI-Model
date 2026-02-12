# Dual-Agent Context Control - Backend Integration Guide

## Overview

The AI Engine uses a **dual-agent system** where two different AI personalities interact with the user:

1. **Opposing Lawyer** - Has access to case facts and challenges the user
2. **Judge** (Neutral Arbiter) - Only has access to legal guidelines and intervenes on violations

**Critical Design Principle:** The Judge is **NEUTRAL** and should NEVER see case-specific facts or evidence. The Judge only enforces legal procedures and constitutional law.

**Architecture:** The Python AI server is **STATELESS**. It doesn't remember chat history - your Node.js backend sends the full history with every request. This makes it scalable and prevents bugs.

---

## Agent Context Access

### Opposing Lawyer
**Has Access To:**
- ✅ Case facts and evidence (from PDF)
- ✅ Legal guidelines and procedures
- ✅ Can cite specific evidence against the user
- ✅ Argues for the prosecution
- ✅ Conversation history for context

**Behavior:** Presents arguments professionally like in a real courtroom. Takes turns making points, responds to user's arguments thoughtfully. Only objects when absolutely necessary (procedural violations).

**Example Lawyer Response:**
```json
{
  "speaker": "Opposing Lawyer",
  "reply_text": "Your Honor, the GPS data [Source 1] shows the defendant's phone was within 100 meters of the crime scene at 10:43 PM. This contradicts the alibi claim.",
  "emotion": "neutral",
  "citations": [
    "Source 1: GPS data shows defendant's phone at crime scene at 10:43 PM via cell tower triangulation..."
  ]
}
```

### Judge (Neutral Arbiter)
**Has Access To:**
- ❌ NO case facts or evidence
- ✅ Legal guidelines and constitutional law ONLY
- ✅ Can cite legal procedures and ethics rules
- ✅ Does NOT argue for either side
- ✅ Conversation history for context

**Example Judge Response:**
```json
{
  "speaker": "Judge",
  "reply_text": "Counsel, you cannot force your client to testify. The Fifth Amendment protects against self-incrimination.",
  "emotion": "authoritative"
}
```

---

## How Context is Controlled

### Endpoint 1: Initialize Legal Laws (Judge's Knowledge Base)

**Route:** `POST /api/ai/init_legal_laws`

**Purpose:** Load constitutional laws, legal procedures, and ethics rules that the Judge will reference.

**When to Call:** Once at application startup or when updating legal database.

**Request:**
```json
{
  "legal_text": "Article I: Right to Legal Counsel...\nArticle II: Burden of Proof...",
  "collection_name": "legal_laws"
}
```

**Response:**
```json
{
  "message": "Legal laws database initialized successfully",
  "collection_name": "legal_laws_guidelines",
  "chunks_processed": 42
}
```

**What This Controls:**
- ✅ Judge's knowledge of legal procedures
- ✅ What legal rules the Judge can cite
- ✅ Basis for detecting legal violations

**Important:** This database contains NO case-specific information. It's pure legal theory and procedure.

---

### Endpoint 2: Initialize Case (Lawyer's Knowledge Base)

**Route:** `POST /api/ai/init_case`

**Purpose:** Load case-specific facts, evidence, and details that the Lawyer will use to challenge the user.

**When to Call:** Every time a new case is loaded for a user.

**Request:**
```json
{
  "case_id": "case_123",
  "pdf_text": "CASE NO. 2024-CR-12345\n\nThe State vs. John Doe...\n\nEVIDENCE:\n1. GPS data shows...\n2. Security footage shows..."
}
```

**Response:**
```json
{
  "message": "Case case_123 vectorized successfully",
  "summary": "This case involves the State of California vs. John Doe regarding alleged robbery. Key evidence includes GPS data and security footage."
}
```

**What This Controls:**
- ✅ Lawyer's knowledge of case facts
- ✅ What evidence the Lawyer can cite
- ✅ Basis for the Lawyer's counter-arguments

**Important:** Only the Lawyer sees this. The Judge will NEVER reference these facts.

---

### Endpoint 3: Chat Turn (Agent Selection & Response)

**Route:** `POST /api/ai/turn`

**Purpose:** Process user's statement and get response from appropriate agent (Judge or Opposing Lawyer).

**When to Call:** Every time user speaks in VR.

**Important:** Server is **STATELESS** - you MUST send the full conversation history with every request.

**Request:**
```json
{
  "case_id": "case_123",
  "user_text": "I want to challenge the GPS evidence reliability",
  "history": [
    {"role": "user", "content": "Your Honor, I present..."},
    {"role": "assistant", "content": "Proceed, Counsel."}
  ]
}
```

**Response Format:**

The response format is the same regardless of which agent responds:

#### If Opposing Lawyer Responds (Normal Flow):
```json
{
  "speaker": "Opposing Lawyer",
  "reply_text": "Your Honor, the GPS data [Source 1] shows consistent positioning for 45 minutes across multiple cell towers. The defense must explain this sustained presence at the scene.",
  "emotion": "questioning",
  "citations": [
    "Source 1: GPS data shows defendant's phone was within 100 meters of the crime scene at 10:43 PM...",
    "Source 2: Security footage confirms person matching defendant's description entering store..."
  ]
}
```

#### If Judge Responds (Intervention):
```json
{
  "speaker": "Judge",
  "reply_text": "Counsel, I must intervene. You cannot coach witnesses on their testimony. That violates legal ethics.",
  "emotion": "authoritative",
  "citations": []
}
```

**Note:** Judge responses do not include case fact citations (only legal procedure references).

**Emotion Values:****
- `"neutral"` - Calm, matter-of-fact
- `"aggressive"` - Forceful, objecting
- `"questioning"` - Probing, inquisitive
- `"authoritative"` - Judge ruling, commanding

---

## Endpoint 4: Analyze Performance (Post-Session)

**Route:** `POST /analyze` or `POST /api/ai/analyze`

**Purpose:** Analyze the full conversation transcript and provide scoring/feedback after session ends.

**When to Call:** When user completes a VR training session.

**Request:**
```json
{
  "transcript": [
    {
      "speaker": "User",
      "text": "Your Honor, I present the case...",
      "_id": {"$oid": "..."},
      "timestamp": {"$date": "..."}
    },
    {
      "speaker": "Opposing Lawyer",
      "text": "Objection, Your Honor...",
      "_id": {"$oid": "..."},
      "timestamp": {"$date": "..."}
    }
  ]
}
```

**Response:**
```json
{
  "score": 78,
  "summary": "The student demonstrated good legal reasoning but needs to improve evidence application.",
  "feedback": "Detailed performance analysis covering legal reasoning, use of facts, clarity, objection handling, and professionalism."
}
```

**Backend Integration:**
```javascript
const generatePostSessionAnalysis = async (transcript) => {
  try {
    const response = await axios.post(`${AI_SERVICE_URL}/analyze`, { transcript });
    return response.data;  // { score, summary, feedback }
  } catch (error) {
    return { summary: "Analysis Failed", feedback: "Check Python Server", score: 0 };
  }
};
```

**Important:** Transcript accepts MongoDB format with `{speaker, text, _id, timestamp}` or standard format with `{role, content}`.

---

## Agent Selection Logic (Automatic - "The Director Pattern")

The system automatically decides which agent responds based on user's statement and conversation context:

### Opposing Lawyer Responds When:
- User makes valid legal arguments (presents counter-arguments)
- User challenges evidence properly (responds with case facts)
- User follows legal procedure (continues case presentation)
- No violations detected (normal courtroom flow)

**Lawyer's Style:** Professional case presentation, thoughtful rebuttals, evidence-based arguments. Like a real trial where both sides take turns presenting their case.

**Examples:**
- "I want to present an alibi defense" → "Your Honor, the State has timeline evidence that contradicts..."
- "The GPS evidence may be unreliable" → "But the data was verified by multiple cell towers..."
- "I'd like to cross-examine the witness" → "Your Honor, our witness testimony already establishes..."

### Judge Intervenes When:
- User makes specific factual claims that contradict case evidence
- User explicitly violates legal ethics or procedure
- User misrepresents evidence

**Examples:**
- "The video shows my client at the library" (when no such video exists)
- "I will force my client to testify" (Fifth Amendment violation)
- "I'll coach my witness on what to say" (ethics violation)

---

## Backend Implementation Guide

### Setup Phase (Once per application startup)

```javascript
// Step 1: Load legal laws for Judge
const legalLawsText = fs.readFileSync('constitutional_laws.txt', 'utf8');
await axios.post('http://localhost:8000/api/ai/init_legal_laws', {
  legal_text: legalLawsText,
  collection_name: 'legal_laws'
});
console.log('✅ Judge knowledge base loaded');
```

### Case Start Phase (Once per case)

```javascript
// Step 2: Load case for Opposing Lawyer
const casePdfText = await extractPdfText('case_file.pdf');
await axios.post('http://localhost:8000/api/ai/init_case', {
  case_id: `case_${userId}_${timestamp}`,
  pdf_text: casePdfText
});
console.log('✅ Lawyer knowledge base loaded');
```

### VR Session Phase (Every turn - STATELESS)

```javascript
// Step 3: Maintain conversation history in Node.js
let conversationHistory = [];

// VR Game Loop
while (sessionActive) {
  const userInput = await getUserVoiceInput();
  
  // Add user message to history
  conversationHistory.push({
    role: 'user',
    content: userInput
  });
  
  // Send FULL history to Python (stateless design)
  const response = await axios.post('http://localhost:8000/api/ai/turn', {
    case_id: currentCaseId,
    user_text: userInput,
    history: conversationHistory  // ← IMPORTANT: Send full history every time
  });
  
  // Add AI response to history
  conversationHistory.push({
    role: 'assistant',
    content: response.data.reply_text
  });
  
  // Handle response based on which agent responded
  if (response.data.speaker === 'Judge') {
    // Judge intervention - user made a mistake
    console.log('⚖️ JUDGE INTERVENES');
    console.log('Response:', response.data.reply_text);
    console.log('Emotion:', response.data.emotion);
    
    // VR: Show judge avatar with authoritative animation
    displayJudgeAvatar();
    playAudio(response.data.reply_text, 'judge_voice', response.data.emotion);
    
  } else if (response.data.speaker === 'Opposing Lawyer') {
    // Normal flow - opposing lawyer challenges user
    console.log('👔 OPPOSING LAWYER RESPONDS');
    console.log('Response:', response.data.reply_text);
    console.log('Emotion:', response.data.emotion);
    
    // VR: Show lawyer avatar with appropriate animation
    displayLawyerAvatar();
    playAudio(response.data.reply_text, 'lawyer_voice', response.data.emotion);
  }
}
```

---

## Context Verification

### How to Verify Context Separation

**Test 1: Check Judge Never Sees Case Facts**
```javascript
// Make user violate legal procedure
const response = await axios.post('http://localhost:8000/api/ai/turn', {
  case_id: 'case_123',
  user_text: 'I will force my client to testify',
  history: []
});

// Verify Judge responded
assert(response.data.speaker === 'Judge');

// Verify emotion is authoritative
assert(response.data.emotion === 'authoritative');

// Verify response cites legal rules, NOT case facts
assert(response.data.reply_text.includes('Fifth Amendment') || 
       response.data.reply_text.includes('legal') ||
       response.data.reply_text.includes('procedure'));
```

**Test 2: Check Opposing Lawyer Has Case Facts**
```javascript
// Make valid legal challenge
const response = await axios.post('http://localhost:8000/api/ai/turn', {
  case_id: 'case_123',
  user_text: 'The GPS evidence is unreliable',
  history: []
});

// Verify Lawyer responded (most likely, unless you violated procedure)
// Note: Could be Judge if you phrased it as a factual lie

if (response.data.speaker === 'Opposing Lawyer') {
  // Verify response references case facts
  assert(response.data.reply_text.includes('GPS') ||
         response.data.reply_text.includes('data') ||
         response.data.reply_text.includes('evidence'));
  
  // Check emotion (should be aggressive or questioning)
  assert(['aggressive', 'questioning', 'neutral'].includes(response.data.emotion));
}
```

---

## Summary Table

| Endpoint | Route | Purpose | When to Call | Key Parameters |
|----------|-------|---------|--------------|----------------|
| **Initialize Legal Laws** | `POST /api/ai/init_legal_laws` | Load Judge's knowledge base | Once at app startup | `legal_text`, `collection_name` |
| **Initialize Case** | `POST /api/ai/init_case` | Load Lawyer's knowledge base | Once per case | `case_id`, `pdf_text` |
| **Chat Turn** | `POST /api/ai/turn` | Get AI response (Judge or Lawyer) | Every user statement | `case_id`, `user_text`, `history` |
| **Analyze Performance** | `POST /analyze` | Score & feedback on session | After session ends | `transcript` |

| Agent | Endpoint That Loads Context | Context Type | Can Cite Case Facts? | Purpose | Emotion Types |
|-------|----------------------------|--------------|---------------------|---------|---------------|
| **Judge** | `POST /api/ai/init_legal_laws` | Constitutional laws, procedures, ethics | ❌ NO | Enforce legal rules, educate on procedure | authoritative, neutral |
| **Opposing Lawyer** | `POST /api/ai/init_case` | Case evidence, facts, witness statements | ✅ YES | Challenge user's arguments with evidence | aggressive, questioning, neutral |

---

## Important Notes for Backend

1. **Judge Never Sees Case PDFs**: The legal laws text should contain ZERO case-specific information.

2. **Context Separation is Automatic**: You don't control which agent responds - the AI detects violations automatically based on user's statement.

3. **Stateless Design**: Your Node.js backend MUST send the full `history` array with every `/turn` request. The Python server doesn't remember previous conversations.

4. **VR Display Logic**: Use `speaker` field to determine which avatar/voice to display:
   ```javascript
   if (speaker === 'Judge') {
     showJudgeAvatar(); // Serious, authoritative
     playAnimation(emotion); // Use emotion field for animation
   } else if (speaker === 'Opposing Lawyer') {
     showLawyerAvatar(); // Aggressive, challenging
     playAnimation(emotion); // Use emotion field for animation
   }
   ```

5. **Emotion Animations**: Map emotion values to VR animations:
   - `"neutral"` → Calm talking animation
   - `"aggressive"` → Forceful gestures, raised voice
   - `"questioning"` → Curious expression, head tilt
   - `"authoritative"` → Firm stance, gavel pound (Judge only)

6. **History Management**: Keep conversation history in your Node.js state/database. Send last 10-20 messages for context (Python uses last 4 internally for token efficiency).

---

## Example Conversation Flow

```javascript
// Initialize
let history = [];

// Turn 1: User opens
const turn1 = await turn('case_123', 'Your Honor, I present the case of Smith vs State', history);
// Response: { speaker: "Judge", reply_text: "Proceed, Counsel.", emotion: "neutral" }
history.push(
  { role: 'user', content: 'Your Honor, I present the case of Smith vs State' },
  { role: 'assistant', content: turn1.reply_text }
);

// Turn 2: User makes factual claim
const turn2 = await turn('case_123', 'The GPS data shows my client was at home', history);
// Response: { speaker: "Opposing Lawyer", reply_text: "Your Honor, the GPS data actually places the defendant within 100 meters of the crime scene, not at their residence.", emotion: "neutral" }
history.push(
  { role: 'user', content: 'The GPS data shows my client was at home' },
  { role: 'assistant', content: turn2.reply_text }
);

// Turn 3: User violates procedure
const turn3 = await turn('case_123', 'I will force my witness to change their testimony', history);
// Response: { speaker: "Judge", reply_text: "Counsel! You cannot coach witnesses...", emotion: "authoritative" }
history.push(
  { role: 'user', content: 'I will force my witness to change their testimony' },
  { role: 'assistant', content: turn3.reply_text }
);
```

---

## Questions?

- See [ENDPOINTS.md](ENDPOINTS.md) for complete API reference
- See [API_DOCS.md](API_DOCS.md) for detailed dual-agent documentation
- Test using [test_dual_agent.py](test_dual_agent.py)
