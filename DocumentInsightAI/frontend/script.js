class DocumentAnalyzer {
    constructor() {
        this.sessionId = null;
        this.currentMode = 'ask';
        this.isProcessing = false;
        this.conversationHistory = [];
        this.challengeQuestions = [];
        this.initializeEventListeners();
        this.initializeDragAndDrop();
        this.initializeAutoResize();
    }

    initializeEventListeners() {
        // File upload
        document.getElementById('uploadBtn').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });
        
        document.getElementById('fileInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadDocument(e.target.files[0]);
            }
        });

        // Mode switching
        document.getElementById('askModeBtn').addEventListener('click', () => {
            this.switchMode('ask');
        });
        
        document.getElementById('challengeModeBtn').addEventListener('click', () => {
            this.switchMode('challenge');
        });

        // Chat functionality
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        document.getElementById('messageInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                if (e.shiftKey) {
                    // Allow line break with Shift+Enter
                    return;
                } else {
                    e.preventDefault();
                    this.sendMessage();
                }
            }
        });

        document.getElementById('messageInput').addEventListener('input', (e) => {
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = !e.target.value.trim();
        });

        // Challenge mode
        document.getElementById('generateQuestionsBtn').addEventListener('click', () => {
            this.generateQuestions();
        });

        // Clear chat
        document.getElementById('clearChatBtn').addEventListener('click', () => {
            this.clearChat();
        });

        // New chat
        document.getElementById('newChatBtn').addEventListener('click', () => {
            this.newChat();
        });
    }

    initializeDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('drag-over');
            }, false);
        });

        uploadArea.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                this.uploadDocument(files[0]);
            }
        }, false);
    }

    initializeAutoResize() {
        const textarea = document.getElementById('messageInput');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    showLoading(text = 'Processing...') {
        const overlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        loadingText.textContent = text;
        overlay.style.display = 'flex';
        this.isProcessing = true;
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
        this.isProcessing = false;
    }

    showError(message) {
        const errorToast = document.getElementById('errorToast');
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = message;
        errorToast.style.display = 'flex';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        document.getElementById('errorToast').style.display = 'none';
    }

    async uploadDocument(file) {
        if (!file) return;

        const allowedTypes = ['application/pdf', 'text/plain'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('Please upload a PDF or TXT file only.');
            return;
        }

        this.showLoading('Analyzing your document...');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.showDocumentAnalysis(data);
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Failed to upload document. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    showDocumentAnalysis(data) {
        this.sessionId = data.session_id;
        
        // Hide welcome screen
        document.getElementById('welcomeScreen').style.display = 'none';
        
        // Show document info in sidebar
        document.getElementById('documentInfo').style.display = 'block';
        document.getElementById('documentTitle').textContent = data.filename;
        document.getElementById('documentSummary').textContent = data.summary;
        
        // Show mode selection
        document.getElementById('modeSelection').style.display = 'block';
        
        // Show chat interface
        this.switchMode('ask');
        
        // Reset conversation history
        this.conversationHistory = [];
        this.challengeQuestions = [];
    }

    switchMode(mode) {
        this.currentMode = mode;
        
        // Update mode buttons
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (mode === 'ask') {
            document.getElementById('askModeBtn').classList.add('active');
            document.getElementById('chatInterface').style.display = 'flex';
            document.getElementById('challengeInterface').style.display = 'none';
            document.getElementById('chatModeTitle').textContent = 'Ask Anything';
        } else {
            document.getElementById('challengeModeBtn').classList.add('active');
            document.getElementById('chatInterface').style.display = 'none';
            document.getElementById('challengeInterface').style.display = 'flex';
            document.getElementById('chatModeTitle').textContent = 'Challenge Mode';
        }
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message || this.isProcessing || !this.sessionId) return;

        // Add user message to chat
        this.addMessageToChat(message, 'user');
        
        // Clear input
        input.value = '';
        input.style.height = 'auto';
        document.getElementById('sendBtn').disabled = true;
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add AI response to chat
            this.addMessageToChat(data.answer, 'ai', data.justification);
            
            // Update conversation history
            this.conversationHistory.push({
                question: message,
                answer: data.answer,
                justification: data.justification
            });
            
        } catch (error) {
            console.error('Question error:', error);
            this.hideTypingIndicator();
            this.showError('Failed to get response. Please try again.');
        }
    }

    addMessageToChat(text, sender, justification = null) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const textP = document.createElement('p');
        textP.textContent = text;
        contentDiv.appendChild(textP);
        
        if (justification && sender === 'ai') {
            const justificationP = document.createElement('p');
            justificationP.style.fontSize = '0.9em';
            justificationP.style.opacity = '0.8';
            justificationP.style.marginTop = '10px';
            justificationP.innerHTML = `<strong>Source:</strong> ${justification}`;
            contentDiv.appendChild(justificationP);
        }
        
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        metaDiv.textContent = new Date().toLocaleTimeString();
        contentDiv.appendChild(metaDiv);
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator.style.display = 'flex';
        
        // Scroll to bottom
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'none';
    }

    async generateQuestions() {
        if (!this.sessionId || this.isProcessing) return;

        this.showLoading('Generating challenging questions...');

        try {
            const response = await fetch('/api/generate-questions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.challengeQuestions = data.questions;
            this.displayChallengeQuestions();
            
        } catch (error) {
            console.error('Question generation error:', error);
            this.showError('Failed to generate questions. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    displayChallengeQuestions() {
        const content = document.getElementById('challengeContent');
        content.innerHTML = '';

        this.challengeQuestions.forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'challenge-question';
            questionDiv.innerHTML = `
                <div class="question-header">
                    <div class="question-number">${index + 1}</div>
                    <h3>Question ${index + 1}</h3>
                </div>
                <div class="question-text">${question}</div>
                <div class="question-input">
                    <textarea 
                        placeholder="Type your answer here..." 
                        id="answer-${index}"
                        rows="4"
                    ></textarea>
                </div>
                <div class="question-actions">
                    <button class="btn btn-primary" onclick="app.evaluateAnswer(${index})">
                        <i class="fas fa-check"></i> Submit Answer
                    </button>
                </div>
                <div id="evaluation-${index}" class="evaluation-result" style="display: none;"></div>
            `;
            content.appendChild(questionDiv);
        });
    }

    async evaluateAnswer(questionIndex) {
        const answerTextarea = document.getElementById(`answer-${questionIndex}`);
        const userAnswer = answerTextarea.value.trim();
        
        if (!userAnswer || this.isProcessing) return;

        this.showLoading('Evaluating your answer...');

        try {
            const response = await fetch('/api/evaluate-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_index: questionIndex,
                    answer: userAnswer,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.displayEvaluation(questionIndex, data.evaluation);
            
        } catch (error) {
            console.error('Evaluation error:', error);
            this.showError('Failed to evaluate answer. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    displayEvaluation(questionIndex, evaluation) {
        const evaluationDiv = document.getElementById(`evaluation-${questionIndex}`);
        evaluationDiv.innerHTML = `
            <div class="evaluation-score">
                <span class="score-badge">${evaluation.score}/10</span>
                <span>Score</span>
            </div>
            <div class="evaluation-feedback">
                <strong>Feedback:</strong> ${evaluation.feedback}
            </div>
            <div class="evaluation-justification">
                <strong>Justification:</strong> ${evaluation.justification}
            </div>
        `;
        evaluationDiv.style.display = 'block';
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        // Keep only the welcome message
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        chatMessages.innerHTML = '';
        if (welcomeMessage) {
            chatMessages.appendChild(welcomeMessage);
        }
        
        // Reset conversation history
        this.conversationHistory = [];
    }

    newChat() {
        // Reset everything
        this.sessionId = null;
        this.currentMode = 'ask';
        this.conversationHistory = [];
        this.challengeQuestions = [];
        
        // Hide document info and mode selection
        document.getElementById('documentInfo').style.display = 'none';
        document.getElementById('modeSelection').style.display = 'none';
        
        // Hide chat and challenge interfaces
        document.getElementById('chatInterface').style.display = 'none';
        document.getElementById('challengeInterface').style.display = 'none';
        
        // Show welcome screen
        document.getElementById('welcomeScreen').style.display = 'flex';
        
        // Reset file input
        document.getElementById('fileInput').value = '';
        
        // Reset mode buttons
        document.getElementById('askModeBtn').classList.add('active');
        document.getElementById('challengeModeBtn').classList.remove('active');
    }
}

// Global functions for onclick handlers
window.hideError = function() {
    document.getElementById('errorToast').style.display = 'none';
};

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DocumentAnalyzer();
});

// Add some utility functions for better UX
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scrolling behavior
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Escape key to close error toast
        if (e.key === 'Escape') {
            window.hideError();
        }
        
        // Ctrl/Cmd + Enter to send message
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (window.app && !window.app.isProcessing) {
                window.app.sendMessage();
            }
        }
    });
    
    // Add focus management
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        // Focus input when chat interface is shown
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const chatInterface = document.getElementById('chatInterface');
                    if (chatInterface && chatInterface.style.display === 'flex') {
                        setTimeout(() => messageInput.focus(), 100);
                    }
                }
            });
        });
        
        const chatInterface = document.getElementById('chatInterface');
        if (chatInterface) {
            observer.observe(chatInterface, { attributes: true });
        }
    }
});