/**
 * VerdicTech AI Engine Client for Node.js
 * 
 * This module provides a clean interface to interact with the Python AI Engine.
 * Copy this file to your Node.js project's services/ directory.
 * 
 * Installation:
 *   npm install axios
 * 
 * Usage:
 *   const aiEngine = require('./services/aiEngineClient');
 *   const result = await aiEngine.initCase(caseId, pdfText);
 */

const axios = require('axios');

class AIEngineClient {
    constructor(baseURL = null) {
        this.baseURL = baseURL || process.env.AI_ENGINE_URL || 'http://localhost:8000/api/ai';
        this.timeout = 30000; // 30 seconds default
        
        // Create axios instance with default config
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: this.timeout,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log(`🤖 AI Engine Client initialized: ${this.baseURL}`);
    }

    /**
     * Initialize a legal case
     * @param {string} caseId - Unique identifier for the case
     * @param {string} pdfText - Full text content of the PDF
     * @returns {Promise<{message: string, summary: string}>}
     */
    async initCase(caseId, pdfText) {
        try {
            console.log(`📝 Initializing case: ${caseId}`);
            
            const response = await this.client.post('/init_case', {
                case_id: caseId,
                pdf_text: pdfText
            }, {
                timeout: 60000 // Longer timeout for initialization
            });
            
            console.log(`✅ Case ${caseId} initialized`);
            return response.data;
            
        } catch (error) {
            console.error(`❌ Failed to initialize case ${caseId}:`, error.message);
            throw this._handleError(error, 'Case initialization failed');
        }
    }

    /**
     * Initialize legal laws database (constitutional laws, procedures, guidelines)
     * This should be called once at application startup
     * @param {string} legalText - Full text of legal laws and guidelines
     * @param {string} collectionName - Optional collection name (defaults to 'legal_laws')
     * @returns {Promise<{message: string, collection_name: string, chunks_processed: number}>}
     */
    async initLegalLaws(legalText, collectionName = 'legal_laws') {
        try {
            console.log(`⚖️  Initializing legal laws database: ${collectionName}`);
            
            const response = await this.client.post('/init_legal_laws', {
                legal_text: legalText,
                collection_name: collectionName
            }, {
                timeout: 60000 // Longer timeout for initialization
            });
            
            console.log(`✅ Legal laws initialized: ${response.data.chunks_processed} chunks`);
            return response.data;
            
        } catch (error) {
            console.error(`❌ Failed to initialize legal laws:`, error.message);
            throw this._handleError(error, 'Legal laws initialization failed');
        }
    }

    /**
     * Get AI response for a conversation turn (Dual-Agent System)
     * The AI will respond as either:
     * - Lawyer (opposing counsel) - if user statement is valid
     * - Judge (neutral arbiter) - if user makes factual/legal errors
     * @param {string} caseId - Case identifier
     * @param {string} userStatement - User's argument or statement
     * @param {number} turnNumber - Current turn number
     * @returns {Promise<{agent_role: string, agent_response: string, case_context_used: string, legal_context_used: string, errors_detected: boolean}>}
     */
    async getChatResponse(caseId, userStatement, turnNumber) {
        try {
            const response = await this.client.post('/turn', {
                case_id: caseId,
                user_statement: userStatement,
                turn_number: turnNumber
            });
            
            const data = response.data;
            console.log(`🤖 Agent: ${data.agent_role.toUpperCase()}`);
            return data;
            
        } catch (error) {
            console.error(`❌ Failed to get chat response:`, error.message);
            
            // Return fallback response instead of throwing
            return {
                agent_role: 'system',
                agent_response: "There seems to be a technical issue. Please try again.",
                case_context_used: '',
                legal_context_used: '',
                errors_detected: false
            };
        }
    }

    /**
     * Analyze conversation performance
     * @param {Array<{role: string, content: string}>} transcript - Full conversation
     * @returns {Promise<{score: number, feedback: string, summary: string}>}
     */
    async analyzePerformance(transcript) {
        try {
            console.log(`📊 Analyzing performance (${transcript.length} messages)`);
            
            const response = await this.client.post('/analyze', {
                transcript: transcript
            }, {
                timeout: 60000 // Longer timeout for analysis
            });
            
            console.log(`✅ Analysis complete: Score ${response.data.score}/100`);
            return response.data;
            
        } catch (error) {
            console.error(`❌ Failed to analyze performance:`, error.message);
            throw this._handleError(error, 'Performance analysis failed');
        }
    }

    /**
     * Health check - verify AI Engine is running
     * @returns {Promise<boolean>}
     */
    async healthCheck() {
        try {
            const response = await axios.get(
                this.baseURL.replace('/api/ai', '/'),
                { timeout: 5000 }
            );
            return response.status === 200;
        } catch (error) {
            console.error('❌ AI Engine health check failed:', error.message);
            return false;
        }
    }

    /**
     * Handle errors and provide user-friendly messages
     * @private
     */
    _handleError(error, defaultMessage) {
        if (error.response) {
            // Server responded with error status
            const detail = error.response.data?.detail || error.response.statusText;
            return new Error(`${defaultMessage}: ${detail}`);
        } else if (error.request) {
            // Request made but no response
            return new Error(`${defaultMessage}: AI Engine not responding. Is it running?`);
        } else {
            // Something else went wrong
            return new Error(`${defaultMessage}: ${error.message}`);
        }
    }
}

// Export singleton instance
const aiEngineClient = new AIEngineClient();

// Also export the class for custom instances
module.exports = aiEngineClient;
module.exports.AIEngineClient = AIEngineClient;

// ============================================================================
// EXAMPLE USAGE (Dual-Agent System)
// ============================================================================

/*

// STEP 1: Initialize legal laws (once at application startup)
const legalLawsText = `
Article I: Right to Legal Counsel
Every defendant has the constitutional right to legal representation...

Article II: Burden of Proof
In criminal cases, the prosecution bears the burden of proving guilt...
`;

const legalInit = await aiEngineClient.initLegalLaws(legalLawsText);
console.log('Legal laws loaded:', legalInit.chunks_processed, 'chunks');

// STEP 2: Initialize a case
const caseId = 'case_123';
const pdfText = 'The State of California vs. John Smith...';

const initResult = await aiEngineClient.initCase(caseId, pdfText);
console.log('Case summary:', initResult.summary);

// STEP 3: Chat conversation with dual-agent system
let turnNumber = 1;

// Turn 1: Normal lawyer response
const turn1 = await aiEngineClient.getChatResponse(
    caseId,
    'I believe the GPS evidence is unreliable.',
    turnNumber++
);
console.log(`${turn1.agent_role}:`, turn1.agent_response);
// Output: "lawyer: While you raise an interesting point about GPS accuracy..."

// Turn 2: Judge intervenes if user makes an error
const turn2 = await aiEngineClient.getChatResponse(
    caseId,
    'I will coach my witness on what to say in their testimony.',
    turnNumber++
);
console.log(`${turn2.agent_role}:`, turn2.agent_response);
// Output: "judge: Counselor! You cannot coach witnesses. That violates legal ethics..."
console.log('Errors detected?', turn2.errors_detected); // true

// Turn 3: Back to lawyer after correction
const turn3 = await aiEngineClient.getChatResponse(
    caseId,
    'You are right, Your Honor. Let me focus on cross-examining the prosecution witness.',
    turnNumber++
);
console.log(`${turn3.agent_role}:`, turn3.agent_response);
// Output: "lawyer: Very well. During cross-examination, you should challenge..."

// STEP 4: Analyze performance
const transcript = [
    { role: 'user', content: 'I believe the GPS evidence is unreliable.' },
    { role: 'assistant', content: turn1.agent_response },
    { role: 'user', content: 'I will coach my witness on what to say.' },
    { role: 'assistant', content: turn2.agent_response },
    { role: 'user', content: 'Let me focus on cross-examining the witness.' },
    { role: 'assistant', content: turn3.agent_response }
];

const analysis = await aiEngineClient.analyzePerformance(transcript);
console.log('Score:', analysis.score);
console.log('Feedback:', analysis.feedback);

// STEP 5: Health check
const isHealthy = await aiEngineClient.healthCheck();
if (!isHealthy) {
    console.error('AI Engine is not available!');
}

// UNDERSTANDING AGENT ROLES:
// - agent_role === 'lawyer'  → Opposing counsel challenging user
// - agent_role === 'judge'   → Neutral arbiter correcting errors
// - errors_detected === true → Judge intervention was triggered

*/
