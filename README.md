# 🧠 VerdicTech AI Engine

A high-performance Python FastAPI microservice that provides the "Intelligence" layer for the VerdicTech legal training application. This service handles Retrieval Augmented Generation (RAG), legal reasoning, and performance scoring using OpenAI and Qdrant vector database.

## 🏗️ Architecture Overview

```
┌─────────────────┐         HTTP REST API          ┌──────────────────┐
│   Node.js       │ ──────────────────────────────> │  Python FastAPI  │
│   Backend       │                                 │   AI Engine      │
│  (The Body)     │ <────────────────────────────── │  (The Brain)     │
└─────────────────┘                                 └──────────────────┘
      │                                                      │
      │                                                      │
   Audio I/O                                            RAG + LLM
   Database                                            Vector Search
   VR Sockets                                          Embeddings
```

## ✨ Features

- **🔄 RAG (Retrieval Augmented Generation)**: Context-aware responses using case-specific facts
- **🗄️ Qdrant Vector Database**: High-performance vector storage and similarity search
- **🤖 OpenAI Integration**: GPT-4o for intelligent legal reasoning
- **📊 Performance Analysis**: Automated grading and feedback generation
- **⚡ Async FastAPI**: High-performance async endpoints
- **🔌 Easy Integration**: RESTful API for seamless Node.js integration

## 📋 Prerequisites

- **Python 3.8+** installed
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- **Qdrant** (Choose one):
  - **Local Docker**: `docker run -p 6333:6333 qdrant/qdrant` (Recommended for development)
  - **Qdrant Cloud**: [Free tier available](https://qdrant.tech/cloud/)
  - **Local Binary**: [Download](https://github.com/qdrant/qdrant/releases)

## 🚀 Quick Start

### 1. Install Dependencies

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your OpenAI API key
notepad .env
```

Required configuration in `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 3. Start Qdrant

**Using Docker (Recommended):**
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

**Or use Qdrant Cloud:**
Update `.env` with:
```env
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
```

### 4. Run the Server

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
python main.py
```

The server will start at **http://localhost:8000**

## 📡 API Endpoints

### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "service": "VerdicTech AI Engine",
  "status": "running",
  "version": "1.0.0"
}
```

### 2. Initialize Case
```http
POST /api/ai/init_case
```

**Request:**
```json
{
  "case_id": "case_123",
  "pdf_text": "The State vs. Smith... [full case text]"
}
```

**Response:**
```json
{
  "message": "Case case_123 vectorized successfully",
  "summary": "This case involves a criminal dispute between..."
}
```

### 3. Chat Turn
```http
POST /api/ai/turn
```

**Request:**
```json
{
  "case_id": "case_123",
  "user_text": "My client was not at the scene.",
  "history": [
    {"role": "user", "content": "I move to dismiss..."},
    {"role": "assistant", "content": "Motion denied..."}
  ]
}
```

**Response:**
```json
{
  "reply_text": "Objection! GPS data shows your client at the scene at 10:43 PM.",
  "speaker": "Lawyer",
  "emotion": "Aggressive"
}
```

### 4. Analyze Performance
```http
POST /api/ai/analyze
```

**Request:**
```json
{
  "transcript": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

**Response:**
```json
{
  "score": 85,
  "feedback": "Strong use of evidence. Consider citing specific precedents...",
  "summary": "The user demonstrated good legal reasoning."
}
```

## 🧪 Testing the API

### Using cURL

**1. Initialize a case:**
```bash
curl -X POST http://localhost:8000/api/ai/init_case \
  -H "Content-Type: application/json" \
  -d "{\"case_id\":\"test_case\",\"pdf_text\":\"On January 1st, 2024, the defendant John Smith was accused of robbery. The prosecution claims he was at the scene at 10 PM. The defense argues he has an alibi.\"}"
```

**2. Send a chat message:**
```bash
curl -X POST http://localhost:8000/api/ai/turn \
  -H "Content-Type: application/json" \
  -d "{\"case_id\":\"test_case\",\"user_text\":\"My client has a solid alibi.\",\"history\":[]}"
```

### Using Python Test Client

See [test_client.py](test_client.py) for a complete example.

```bash
python test_client.py
```

## 🔧 Configuration

Edit `config.py` or `.env` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI model to use |
| `QDRANT_HOST` | `localhost` | Qdrant server host |
| `QDRANT_PORT` | `6333` | Qdrant server port |
| `QDRANT_URL` | `None` | Qdrant Cloud URL (optional) |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `CHUNK_SIZE` | `1000` | Text chunk size for RAG |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |

## 🔗 Node.js Integration

Update your Node.js `aiService.js`:

```javascript
const axios = require('axios');

const AI_ENGINE_URL = "http://localhost:8000/api/ai";

exports.initCase = async (caseId, pdfText) => {
    const response = await axios.post(`${AI_ENGINE_URL}/init_case`, {
        case_id: caseId,
        pdf_text: pdfText
    });
    return response.data;
};

exports.getAIResponse = async (caseId, userText, chatHistory) => {
    const response = await axios.post(`${AI_ENGINE_URL}/turn`, {
        case_id: caseId,
        user_text: userText,
        history: chatHistory
    });
    return response.data.reply_text;
};

exports.analyzePerformance = async (transcript) => {
    const response = await axios.post(`${AI_ENGINE_URL}/analyze`, {
        transcript: transcript
    });
    return response.data;
};
```

## 📊 How RAG Works

1. **Initialization**: PDF text is split into chunks and converted to embeddings
2. **Storage**: Embeddings stored in Qdrant with case-specific collection
3. **Retrieval**: User query converted to embedding → Find similar chunks
4. **Generation**: Retrieved context + query → GPT-4o → Response

```
User Query: "My client wasn't there"
     ↓
Embedding → [0.234, -0.567, ...]
     ↓
Qdrant Search → Top 3 matching chunks
     ↓
Context: "GPS logs show location at 10:43 PM..."
     ↓
GPT-4o: "Objection! GPS data contradicts..."
```

## 🐛 Troubleshooting

**Error: "OPENAI_API_KEY not found"**
- Make sure `.env` file exists and contains your API key
- Verify no typos in the variable name

**Error: "Failed to connect to Qdrant"**
- Check if Qdrant is running: `curl http://localhost:6333`
- For Docker: `docker ps` should show qdrant container
- Check firewall settings

**Error: "Case not initialized"**
- Call `/init_case` endpoint before `/turn`
- Verify case_id matches between requests

**Server won't start:**
- Check if port 8000 is already in use
- Try changing `PORT` in `.env`
- Check Python version: `python --version` (needs 3.8+)

## 📚 Project Structure

```
JustiX_AI_Model/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
├── install.bat         # Windows installer
├── start.bat           # Windows startup script
├── test_client.py      # API test client
├── README.md           # This file
└── qdrant_storage/     # Local Qdrant data (auto-created)
```

## 🚢 Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t verdictech-ai .
docker run -p 8000:8000 --env-file .env verdictech-ai
```

### Production Considerations

- Use **Qdrant Cloud** for production
- Set proper **CORS origins** in `main.py`
- Use **environment-specific configs**
- Enable **logging and monitoring**
- Consider **rate limiting**
- Use **HTTPS** with reverse proxy (nginx)

## 📝 License

[Your License Here]

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📧 Support

For questions or issues, please contact [your-email@example.com]

---

**Built with ❤️ for VerdicTech**
