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
     * Get AI response for a conversation turn
     * @param {string} caseId - Case identifier
     * @param {string} userText - User's argument or statement
     * @param {Array<{role: string, content: string}>} history - Chat history
     * @returns {Promise<{reply_text: string, speaker: string, emotion: string}>}
     */
    async getChatResponse(caseId, userText, history = []) {
        try {
            const response = await this.client.post('/turn', {
                case_id: caseId,
                user_text: userText,
                history: history
            });
            
            return response.data;
            
        } catch (error) {
            console.error(`❌ Failed to get chat response:`, error.message);
            
            // Return fallback response instead of throwing
            return {
                reply_text: "I object! There seems to be a technical issue. Please try again.",
                speaker: "System",
                emotion: "Neutral"
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
// EXAMPLE USAGE
// ============================================================================

/*

// Example 1: Initialize a case
const caseId = 'case_123';
const pdfText = 'The State of California vs. John Smith...';

const initResult = await aiEngineClient.initCase(caseId, pdfText);
console.log('Summary:', initResult.summary);

// Example 2: Chat conversation
const chatHistory = [];
const userText = 'My client was not at the scene of the crime.';

const aiResponse = await aiEngineClient.getChatResponse(caseId, userText, chatHistory);
console.log('AI:', aiResponse.reply_text);
console.log('Speaker:', aiResponse.speaker);
console.log('Emotion:', aiResponse.emotion);

// Update history
chatHistory.push({ role: 'user', content: userText });
chatHistory.push({ role: 'assistant', content: aiResponse.reply_text });

// Example 3: Analyze performance
const analysis = await aiEngineClient.analyzePerformance(chatHistory);
console.log('Score:', analysis.score);
console.log('Feedback:', analysis.feedback);

// Example 4: Health check
const isHealthy = await aiEngineClient.healthCheck();
if (!isHealthy) {
    console.error('AI Engine is not available!');
}

*/
