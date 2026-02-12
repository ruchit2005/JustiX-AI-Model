"""
VerdicTech AI Microservice
A high-performance FastAPI backend for legal case analysis using RAG with Qdrant.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
import logging

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VerdicTech AI Engine",
    description="Legal AI microservice with RAG capabilities",
    version="1.0.0"
)

# CORS configuration for Node.js backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY
)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Initialize Qdrant Client
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if QDRANT_URL:
    # Use Qdrant Cloud
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
    logger.info(f"Connected to Qdrant Cloud at {QDRANT_URL}")
else:
    # Use local Qdrant
    qdrant_client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT
    )
    logger.info(f"Connected to local Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")

# In-memory storage for vector stores
vector_stores: Dict[str, Qdrant] = {}  # Case-specific RAG
legal_laws_store: Optional[Qdrant] = None  # Legal laws and guidelines RAG

# ==================== REQUEST/RESPONSE MODELS ====================

class InitCaseRequest(BaseModel):
    case_id: str = Field(..., description="Unique identifier for the case")
    pdf_text: str = Field(..., description="Full text content of the PDF case file")

class InitCaseResponse(BaseModel):
    message: str
    summary: str

class InitLegalLawsRequest(BaseModel):
    legal_text: str = Field(..., description="Constitutional laws, guidelines, and legal procedures text")

class InitLegalLawsResponse(BaseModel):
    message: str
    collection_name: str
    chunks_processed: int

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class TurnRequest(BaseModel):
    case_id: str = Field(..., description="Case identifier")
    user_text: str = Field(..., description="User's argument/statement")
    history: List[ChatMessage] = Field(default=[], description="Chat history")

class TurnResponse(BaseModel):
    speaker: str = Field(..., description="'Judge' or 'Opposing Lawyer'")
    reply_text: str = Field(..., description="AI response text")
    emotion: str = Field(default="neutral", description="Emotion for VR animation (neutral, aggressive, questioning, authoritative)")
    citations: List[str] = Field(default=[], description="Source references from case documents")

class AnalyzeRequest(BaseModel):
    transcript: List[Dict] = Field(..., description="Full conversation transcript - accepts {role,content} or {speaker,text} format")
    
    class Config:
        # Allow extra fields from MongoDB (like _id, timestamp)
        extra = "allow"

class AnalyzeResponse(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Performance score (0-100)")
    feedback: str = Field(..., description="Detailed feedback")
    summary: str = Field(..., description="Brief summary of user's performance")

# ==================== HELPER FUNCTIONS ====================

def create_collection_if_not_exists(collection_name: str):
    """Create a Qdrant collection if it doesn't exist"""
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if collection_name not in collection_names:
            # OpenAI embeddings have 1536 dimensions
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            logger.info(f"Created collection: {collection_name}")
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise

def get_relevant_context(case_id: str, query: str, top_k: int = 3) -> tuple[str, List[str]]:
    """Retrieve relevant context from case vector store with citations"""
    if case_id not in vector_stores:
        return "", []
    
    try:
        retriever = vector_stores[case_id].as_retriever(search_kwargs={"k": top_k})
        docs = retriever.invoke(query)
        
        # Build context with citation markers
        context_parts = []
        citations = []
        
        for i, doc in enumerate(docs, 1):
            citation_marker = f"[Source {i}]"
            context_parts.append(f"{citation_marker} {doc.page_content}")
            
            # Extract citation info from metadata or content
            citation_text = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            citations.append(f"Source {i}: {citation_text}")
        
        context = "\n\n".join(context_parts)
        return context, citations
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return "", []

def get_legal_laws_context(query: str, top_k: int = 2) -> str:
    """Retrieve relevant legal laws and guidelines"""
    if legal_laws_store is None:
        return ""
    
    try:
        retriever = legal_laws_store.as_retriever(search_kwargs={"k": top_k})
        docs = retriever.invoke(query)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        logger.error(f"Error retrieving legal laws: {e}")
        return ""

def detect_judge_intervention_needed(user_text: str, case_context: str, legal_context: str, turn_count: int) -> tuple[bool, str]:
    """Detect if Judge should intervene for educational/procedural guidance"""
    detection_prompt = f"""You are a Judge in an educational legal training simulation. Analyze if you need to intervene.

CASE FACTS:
{case_context}

LEGAL GUIDELINES:
{legal_context}

USER STATEMENT:
{user_text}

JUDGE SHOULD INTERVENE if the statement:
1. Violates legal procedure or ethics (e.g., "I'll coach my witness", "force client to testify")
2. Makes factual claims that contradict case evidence (e.g., "video shows X" when it doesn't exist)
3. Shows misunderstanding of legal rights (e.g., misquoting constitutional protections)
4. Contains improper courtroom conduct (e.g., attacking opposing counsel personally)
5. Shows lack of understanding about burden of proof or legal standards
6. Makes procedurally incorrect requests

JUDGE LETS LAWYER HANDLE (responds with OK) if:
- General strategic arguments ("I challenge the GPS reliability")
- Valid legal tactics ("I want to present alibi defense")
- Proper procedural requests ("I'd like to cross-examine")
- Normal case argumentation

Respond with:
- "INTERVENE: [explanation]" if Judge should provide guidance/correction
- "OK" if Opposing Lawyer should respond normally
"""
    
    try:
        response = llm.invoke(detection_prompt)
        result = response.content.strip()
        
        if result.startswith("INTERVENE:"):
            return True, result.replace("INTERVENE:", "").strip()
        return False, ""
    except:
        return False, ""

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "VerdicTech AI Engine",
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/api/ai/init_case", response_model=InitCaseResponse)
async def init_case(request: InitCaseRequest):
    """
    Initialize a case by vectorizing the PDF text and storing in Qdrant.
    This must be called before any chat turns for a case.
    """
    try:
        logger.info(f"Initializing case: {request.case_id}")
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_text(request.pdf_text)
        logger.info(f"Split text into {len(chunks)} chunks")
        
        # Create collection for this case
        collection_name = f"case_{request.case_id}"
        create_collection_if_not_exists(collection_name)
        
        # Create vector store and add documents
        if QDRANT_URL:
            vector_store = Qdrant.from_texts(
                texts=chunks,
                embedding=embeddings,
                collection_name=collection_name,
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY
            )
        else:
            vector_store = Qdrant.from_texts(
                texts=chunks,
                embedding=embeddings,
                collection_name=collection_name,
                host=QDRANT_HOST,
                port=QDRANT_PORT
            )
        
        # Store in memory for quick access
        vector_stores[request.case_id] = vector_store
        logger.info(f"Vectorized and stored {len(chunks)} chunks for case {request.case_id}")
        
        # Generate case summary
        summary_prompt = f"""You are a legal expert. Summarize this legal case in 3 clear sentences.
        Focus on: 1) The parties involved, 2) The main legal issue, 3) The key facts.
        
        Case text: {request.pdf_text[:3000]}"""
        
        summary_response = llm.invoke(summary_prompt)
        summary = summary_response.content
        
        return InitCaseResponse(
            message=f"Case {request.case_id} vectorized successfully",
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error in init_case: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize case: {str(e)}")

@app.post("/api/ai/init_legal_laws", response_model=InitLegalLawsResponse)
async def init_legal_laws(request: InitLegalLawsRequest):
    """
    Initialize the legal laws and guidelines RAG system.
    This should be called once at startup or when updating legal database.
    """
    global legal_laws_store
    
    try:
        logger.info("Initializing legal laws database")
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_text(request.legal_text)
        logger.info(f"Split legal text into {len(chunks)} chunks")
        
        # Create collection for legal laws
        collection_name = "legal_laws_guidelines"
        create_collection_if_not_exists(collection_name)
        
        # Create vector store
        if QDRANT_URL:
            legal_laws_store = Qdrant.from_texts(
                texts=chunks,
                embedding=embeddings,
                collection_name=collection_name,
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY
            )
        else:
            legal_laws_store = Qdrant.from_texts(
                texts=chunks,
                embedding=embeddings,
                collection_name=collection_name,
                host=QDRANT_HOST,
                port=QDRANT_PORT
            )
        
        logger.info(f"Legal laws database initialized with {len(chunks)} chunks")
        
        return InitLegalLawsResponse(
            message="Legal laws database initialized successfully",
            collection_name=collection_name,
            chunks_processed=len(chunks)
        )
        
    except Exception as e:
        logger.error(f"Error in init_legal_laws: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize legal laws: {str(e)}")

@app.post("/api/ai/turn", response_model=TurnResponse)
async def chat_turn(request: TurnRequest):
    """
    Handle a conversation turn using RAG to generate contextually relevant responses.
    Decides whether Judge or Opposing Lawyer responds based on context.
    STATELESS: Receives history from Node.js every time.
    """
    try:
        logger.info(f"Processing turn for case: {request.case_id}")
        
        # Check if case is loaded
        if request.case_id not in vector_stores:
            logger.warning(f"Case {request.case_id} not found in memory, attempting to load...")
            
            # Try to load from Qdrant
            collection_name = f"case_{request.case_id}"
            try:
                vector_store = Qdrant(
                    qdrant_client,
                    collection_name=collection_name,
                    embeddings=embeddings
                )
                vector_stores[request.case_id] = vector_store
                logger.info(f"Loaded case {request.case_id} from Qdrant")
            except Exception as e:
                return TurnResponse(
                    speaker="Judge",
                    reply_text="Error: Case not initialized. Please upload the case file first.",
                    emotion="neutral",
                    citations=[]
                )
        
        # Retrieve relevant context from case and legal laws with citations
        case_context, case_citations = get_relevant_context(request.case_id, request.user_text, top_k=3)
        legal_context = get_legal_laws_context(request.user_text, top_k=2)
        
        # Build conversation history string for context
        history_str = ""
        for msg in request.history[-4:]:  # Last 4 messages for context
            history_str += f"{msg.role.capitalize()}: {msg.content}\n"
        
        # Check if Judge should intervene (errors, violations, or teaching moments)
        turn_count = len(request.history) // 2  # Approximate turn number
        should_intervene, intervention_reason = detect_judge_intervention_needed(
            request.user_text, case_context, legal_context, turn_count
        )
        
        # Also check for periodic Judge guidance (educational intervention)
        # Judge provides procedural guidance on first turn or occasionally
        if not should_intervene and legal_context:
            # First user statement should often get Judge acknowledgment
            if turn_count == 0 and any(word in request.user_text.lower() for word in ['your honor', 'judge', 'present']):
                should_intervene = True
                intervention_reason = "Judge acknowledges opening statement and sets courtroom expectations"
        
        if should_intervene:
            # JUDGE INTERVENES (NEUTRAL - Only uses legal guidelines)
            logger.info(f"Judge intervening - Reason: {intervention_reason}")
            
            # If no legal context available, use general procedural knowledge
            legal_guidance = legal_context if legal_context else "General legal procedure and courtroom conduct standards"
            
            judge_prompt = f"""You are a fair and NEUTRAL judge presiding over this legal training simulation.
The attorney made a statement that requires your guidance or correction.

LEGAL GUIDELINES AVAILABLE:
{legal_guidance}

CONVERSATION HISTORY:
{history_str}

ATTORNEY'S STATEMENT:
{request.user_text}

REASON FOR YOUR INTERVENTION:
{intervention_reason}

INSTRUCTIONS FOR NEUTRAL JUDGE:
- You are NOT advocating for either side (prosecution or defense)
- Provide professional guidance and educate on proper legal procedure
- Cite legal guidelines, constitutional rights, or courtroom procedures when relevant
- Do NOT mention case facts or evidence (you're not arguing the case)
- Focus on teaching proper legal conduct
- Keep response under 40 words
- Be authoritative but educational
- For opening statements, acknowledge professionally: "Proceed, Counsel. Please present your argument."
- For violations, start with "Counsel," or "I must intervene,"

Generate your NEUTRAL judicial response:""" 
            
            response = llm.invoke(judge_prompt)
            reply_text = response.content
            speaker = "Judge"
            emotion = "authoritative"
            citations = []  # Judge doesn't cite case facts
            
        else:
            # OPPOSING LAWYER RESPONDS
            # Analyze conversation context to determine appropriate response type
            lawyer_prompt = f"""You are the opposing counsel in a legal case. Present your arguments professionally like in a real courtroom.

CASE FACTS:
{case_context}

LEGAL GUIDELINES:
{legal_context}

CONVERSATION HISTORY:
{history_str}

USER'S CURRENT ARGUMENT:
{request.user_text}

INSTRUCTIONS FOR REALISTIC COURTROOM BEHAVIOR:
- Present your case arguments using specific facts and evidence
- When citing case facts, reference them using [Source 1], [Source 2], etc.
- Respond thoughtfully to the user's points with counter-arguments
- Build on your previous arguments in the conversation
- Only say "Objection!" if there's a clear procedural violation (rare)
- Most responses should be: "Your Honor, [present argument/evidence]..." or "But the evidence clearly shows..."
- Be professional and persuasive, not constantly combative
- Use legal terminology but remain clear
- Keep responses under 40 words
- Take turns presenting your case, like a real trial

Generate your professional opposition response (include [Source X] citations when referencing case facts):"""
            
            response = llm.invoke(lawyer_prompt)
            reply_text = response.content
            speaker = "Opposing Lawyer"
            citations = case_citations if case_citations else []
            
            # Determine emotion based on response content
            if "Objection" in reply_text or "!" in reply_text:
                emotion = "aggressive"
            elif "?" in reply_text:
                emotion = "questioning"
            else:
                emotion = "neutral"
        
        logger.info(f"Generated {speaker} response for case {request.case_id}")
        
        return TurnResponse(
            speaker=speaker,
            reply_text=reply_text,
            emotion=emotion,
            citations=citations
        )
        
    except Exception as e:
        logger.error(f"Error in chat_turn: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process turn: {str(e)}")

@app.post("/api/ai/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze the full conversation transcript and provide feedback and scoring.
    This is typically called when the user ends the session.
    """
    try:
        logger.info("Analyzing transcript")
        
        # Convert transcript to readable format
        # Support both formats: {role, content} and {speaker, text}
        transcript_text = ""
        for msg in request.transcript:
            # MongoDB/Node.js format: {speaker: 'User'|'Opposing Lawyer'|'Judge', text: '...', _id, timestamp}
            if 'speaker' in msg and 'text' in msg:
                speaker = msg['speaker']
                text = msg['text']
            # Standard format: {role: 'user'|'assistant', content: '...'}
            elif 'role' in msg and 'content' in msg:
                speaker = "User" if msg['role'] == "user" else "AI"
                text = msg['content']
            else:
                # Skip malformed messages
                logger.warning(f"Skipping malformed message in transcript: {msg}")
                continue
            
            transcript_text += f"{speaker}: {text}\n\n"
        
        if not transcript_text:
            raise HTTPException(status_code=400, detail="Transcript is empty or malformed")
        
        # Create analysis prompt
        analysis_prompt = f"""You are a legal mentor providing personal, direct feedback to your student after their mock trial performance.

Write your feedback as if you're speaking DIRECTLY to the student in a one-on-one conversation. Use "you", "your", "you've" throughout.

Analyze this conversation transcript and provide:
1. A numerical score from 0-100
2. Personal feedback addressed directly to the student
3. A brief personal summary (2-3 sentences)

EVALUATION CRITERIA:
- Legal reasoning and argument structure (30%)
- Use of case facts and evidence (25%)
- Clarity and articulation (20%)
- Handling of objections (15%)
- Professional demeanor (10%)

TRANSCRIPT:
{transcript_text}

CRITICAL INSTRUCTION: Write ONLY in second person. Imagine you're talking directly to the student.

✅ CORRECT examples:
- "You demonstrated strong legal reasoning when you cited Article 21..."
- "Your argument would have been stronger if you had referenced specific case facts..."
- "You handled the judge's correction professionally by acknowledging and clarifying..."
- "I noticed you maintained good professional demeanor throughout..."

❌ NEVER write like this:
- "The student demonstrated..." (WRONG - too formal and distant)
- "Their argument..." (WRONG - use "your" instead)
- "The law student shows..." (WRONG - address them directly as "you")

Think of this as a personal coaching session where you're talking TO the student, not ABOUT them.

Provide your analysis in this EXACT format:
SCORE: [number]
FEEDBACK: [Write as if speaking directly to the student using "you/your"]
SUMMARY: [2-3 sentences speaking directly to student using "you/your"]"""
        
        # Generate analysis
        analysis_response = llm.invoke(analysis_prompt)
        analysis_text = analysis_response.content
        
        # Parse the response
        score = 75  # Default
        feedback = ""
        summary = ""
        
        lines = analysis_text.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("SCORE:"):
                try:
                    score = int(''.join(filter(str.isdigit, line.split(":")[1])))
                    score = max(0, min(100, score))  # Clamp to 0-100
                except:
                    pass
            elif line.startswith("FEEDBACK:"):
                feedback = line.replace("FEEDBACK:", "").strip()
                # Get remaining lines until SUMMARY
                for j in range(i+1, len(lines)):
                    if lines[j].startswith("SUMMARY:"):
                        break
                    feedback += " " + lines[j].strip()
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
                # Get remaining lines
                for j in range(i+1, len(lines)):
                    summary += " " + lines[j].strip()
        
        # Fallback if parsing failed
        if not feedback:
            feedback = analysis_text
        if not summary:
            summary = "Analysis completed. Review the detailed feedback above."
        
        logger.info(f"Analysis complete. Score: {score}")
        
        return AnalyzeResponse(
            score=score,
            feedback=feedback,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error in analyze: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze transcript: {str(e)}")

# Alias route for backend compatibility (expects /analyze instead of /api/ai/analyze)
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_alias(request: AnalyzeRequest):
    """Alias for /api/ai/analyze endpoint for backend compatibility"""
    return await analyze(request)

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting VerdicTech AI Engine on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
