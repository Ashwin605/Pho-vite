/**
 * PhoVite AI Assistant - Intelligent Helper
 * Provides contextual assistance for invitation creation and website navigation
 */

class PhoViteAssistant {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.isTyping = false;
        this.isListening = false;
        this.isSpeaking = false;
        this.voiceEnabled = true; // Default to voice enabled
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.init();
    }

    init() {
        this.createAssistantUI();
        this.setupVoiceRecognition();
        this.attachEventListeners();

        // Check for pending actions from cross-page navigation
        this.checkPendingActions();

        this.showWelcomeMessage();
    }

    checkPendingActions() {
        try {
            const prefillData = sessionStorage.getItem('ai_prefill');
            if (prefillData) {
                console.log("Found pending AI action data:", prefillData);
                const payload = JSON.parse(prefillData);

                // Clear it immediately so it doesn't run again on reload
                sessionStorage.removeItem('ai_prefill');

                // Wait a moment for page to fully render/hydrate
                setTimeout(() => {
                    this.handleFormFill(payload);
                    this.addMessage({
                        role: 'assistant',
                        content: 'I\'ve started your invitation based on what we discussed! 👇'
                    });
                    this.toggleAssistant(); // Open panel to show we're helping
                }, 1000);
            }
        } catch (e) {
            console.error("Error processing pending actions:", e);
        }
    }

    setupVoiceRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.lang = 'en-US';
            this.recognition.interimResults = false;

            this.recognition.onstart = () => {
                this.isListening = true;
                this.updateMicButtonState();
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.updateMicButtonState();
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const input = document.getElementById('ai-input');
                if (input) {
                    input.value = transcript;
                    // Auto-send after voice input
                    setTimeout(() => this.sendMessage(), 500);
                }
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error', event.error);
                this.isListening = false;
                this.updateMicButtonState();
            };
        } else {
            console.log("Web Speech API not supported in this browser.");
        }
    }

    createAssistantUI() {
        // Create assistant container
        const assistantHTML = `
            <!-- AI Assistant Floating Button -->
            <button id="ai-assistant-btn" class="ai-assistant-trigger" aria-label="Open AI Assistant">
                <div class="ai-glow"></div>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
                    <path d="M20 3v4"/>
                    <path d="M22 5h-4"/>
                    <path d="M4 17v2"/>
                    <path d="M5 18H3"/>
                </svg>
                <span class="notification-badge">!</span>
            </button>

            <!-- AI Assistant Panel -->
            <div id="ai-assistant-panel" class="ai-assistant-panel">
                <div class="ai-assistant-header">
                    <div class="ai-header-content">
                        <div class="ai-avatar">
                            <div class="ai-avatar-glow"></div>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                                <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
                            </svg>
                        </div>
                        <div class="ai-header-text">
                            <h3>PhoVite Assistant</h3>
                            <span class="ai-status">
                                <span class="status-dot"></span>
                                Online
                            </span>
                        </div>
                    </div>
                    <div class="ai-header-actions">
                        <button id="ai-voice-toggle" class="ai-icon-btn ${this.voiceEnabled ? 'active' : ''}" aria-label="Toggle Voice Output">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                            </svg>
                        </button>
                        <button id="ai-close-btn" class="ai-close-btn" aria-label="Close Assistant">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 6L6 18M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>

                <div id="ai-messages" class="ai-messages-container">
                    <!-- Messages will be inserted here -->
                </div>

                <div class="ai-quick-actions">
                    <button class="quick-action-btn" data-action="how-to-create">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                        </svg>
                        How to Create
                    </button>
                    <button class="quick-action-btn" data-action="best-vibe">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
                        </svg>
                        Best Vibe
                    </button>
                    <button class="quick-action-btn" data-action="event-tips">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <path d="M12 16v-4M12 8h.01"></path>
                        </svg>
                        Event Tips
                    </button>
                </div>

                <div class="ai-input-container">
                    <button id="ai-mic-btn" class="ai-mic-btn" aria-label="Voice Input">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="23"></line>
                            <line x1="8" y1="23" x2="16" y2="23"></line>
                        </svg>
                    </button>
                    <textarea 
                        id="ai-input" 
                        class="ai-input" 
                        placeholder="Ask me anything..."
                        rows="1"
                    ></textarea>
                    <button id="ai-send-btn" class="ai-send-btn" aria-label="Send Message">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', assistantHTML);
    }

    attachEventListeners() {
        const assistantBtn = document.getElementById('ai-assistant-btn');
        const closeBtn = document.getElementById('ai-close-btn');
        const sendBtn = document.getElementById('ai-send-btn');
        const micBtn = document.getElementById('ai-mic-btn');
        const voiceToggleBtn = document.getElementById('ai-voice-toggle');
        const input = document.getElementById('ai-input');
        const quickActions = document.querySelectorAll('.quick-action-btn');

        assistantBtn?.addEventListener('click', () => this.toggleAssistant());
        closeBtn?.addEventListener('click', () => this.closeAssistant());
        sendBtn?.addEventListener('click', () => this.sendMessage());

        micBtn?.addEventListener('click', () => this.toggleVoiceRecognition());

        voiceToggleBtn?.addEventListener('click', () => {
            this.voiceEnabled = !this.voiceEnabled;
            voiceToggleBtn.classList.toggle('active');
            if (!this.voiceEnabled) {
                this.synthesis.cancel();
                voiceToggleBtn.innerHTML = `
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <line x1="23" y1="9" x2="17" y2="15"></line>
                        <line x1="17" y1="9" x2="23" y2="15"></line>
                    </svg>
                 `;
            } else {
                voiceToggleBtn.innerHTML = `
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                    </svg>
                 `;
            }
        });

        input?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        input?.addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
        });

        quickActions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    toggleVoiceRecognition() {
        if (!this.recognition) return;

        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }

    updateMicButtonState() {
        const micBtn = document.getElementById('ai-mic-btn');
        if (!micBtn) return;

        if (this.isListening) {
            micBtn.classList.add('listening');
            micBtn.innerHTML = `
                <div class="mic-wave"></div>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="6" height="6" rx="1"></rect>
                </svg>
            `;
        } else {
            micBtn.classList.remove('listening');
            micBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="23"></line>
                    <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
            `;
        }
    }

    speakResponse(text) {
        if (!this.voiceEnabled || !this.synthesis) return;

        // Remove emojis and code blocks for cleaner speech
        const cleanText = text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}]/gu, '')
            .replace(/`.*?`/g, '')
            .replace(/\*/g, '');

        this.synthesis.cancel(); // Stop any previous speech
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.0;
        utterance.pitch = 1.1;

        // Try to select a female voice or a pleasant default
        const voices = this.synthesis.getVoices();
        const preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Samantha'));
        if (preferredVoice) utterance.voice = preferredVoice;

        this.synthesis.speak(utterance);
    }

    toggleAssistant() {
        this.isOpen = !this.isOpen;
        const panel = document.getElementById('ai-assistant-panel');
        const btn = document.getElementById('ai-assistant-btn');

        if (this.isOpen) {
            panel.classList.add('open');
            btn.classList.add('active');
            // Hide notification badge
            const badge = btn.querySelector('.notification-badge');
            if (badge) badge.style.display = 'none';
            // Focus input
            setTimeout(() => {
                document.getElementById('ai-input')?.focus();
            }, 300);
        } else {
            panel.classList.remove('open');
            btn.classList.remove('active');
            this.synthesis.cancel(); // Stop speaking when closed
            if (this.isListening) {
                this.recognition.stop();
            }
        }
    }

    closeAssistant() {
        this.isOpen = false;
        const panel = document.getElementById('ai-assistant-panel');
        const btn = document.getElementById('ai-assistant-btn');
        panel.classList.remove('open');
        btn.classList.remove('active');
        this.synthesis.cancel();
        if (this.isListening) {
            this.recognition.stop();
        }
    }

    showWelcomeMessage() {
        setTimeout(() => {
            const welcomeMsg = '👋 Hi! I\'m your PhoVite AI Assistant. I can help you create stunning invitations, choose the perfect vibe, and answer any questions about our platform. How can I assist you today?';
            const msgObj = {
                role: 'assistant',
                content: welcomeMsg
            };
            this.addMessage(msgObj);
            // Don't auto-speak welcome message to be less intrusive
        }, 1000);
    }

    async sendMessage() {
        const input = document.getElementById('ai-input');
        const message = input.value.trim();

        if (!message || this.isTyping) return;

        // Stop listening if we were (e.g. they typed instead)
        if (this.isListening) this.recognition.stop();

        // Add user message
        this.addMessage({ role: 'user', content: message });
        input.value = '';
        input.style.height = 'auto';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to backend
            const response = await fetch('/api/assistant-chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    context: this.getPageContext()
                })
            });

            const data = await response.json();

            this.hideTypingIndicator();

            if (data.success) {
                this.addMessage({ role: 'assistant', content: data.response });
                this.speakResponse(data.response);

                // Handle AI Actions
                if (data.action && data.action.type !== 'none') {
                    this.handleAction(data.action);
                }
            } else {
                this.addMessage({
                    role: 'assistant',
                    content: '❌ Sorry, I encountered an error. Please try again or contact support if the issue persists.'
                });
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage({
                role: 'assistant',
                content: '❌ Connection error. Please check your internet and try again.'
            });
            console.error('AI Assistant Error:', error);
        }
    }

    handleAction(action) {
        console.log("Executing AI Action:", action);

        switch (action.type) {
            case 'navigate':
                this.handleNavigation(action.payload);
                break;
            case 'fill_form':
                this.handleFormFill(action.payload);
                break;
            case 'trigger_generate':
                this.handleGenerate();
                break;
            default:
                console.warn("Unknown action type:", action.type);
        }
    }

    handleGenerate() {
        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn) {
            generateBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Small delay to make it feel natural
            setTimeout(() => {
                generateBtn.click();
            }, 800);
        } else {
            console.warn("Generate button not found");
        }
    }

    handleNavigation(payload) {
        if (payload.prefill) {
            sessionStorage.setItem('ai_prefill', JSON.stringify(payload.prefill));
        }

        if (payload.url) {
            // Add a small delay for the user to read the message
            setTimeout(() => {
                window.location.href = payload.url;
            }, 1000);
        }
    }

    handleFormFill(payload) {
        // Only works if we are on the create page
        if (!window.location.pathname.includes('create')) {
            console.warn("Cannot fill form: Not on create page");
            return;
        }

        // Helper to set value and trigger change event
        const setField = (id, value) => {
            const el = document.getElementById(id);
            if (el) {
                el.value = value;
                el.dispatchEvent(new Event('change'));
                el.dispatchEvent(new Event('input'));

                // Highlight the field briefly
                el.classList.add('ring-2', 'ring-purple-500');
                setTimeout(() => el.classList.remove('ring-2', 'ring-purple-500'), 2000);
            }
        };

        if (payload.eventType) {
            // Find the button with this event type
            const btn = document.querySelector(`.event-type-btn[data-event="${payload.eventType}"]`);
            if (btn) btn.click();
        }

        if (payload.celebrantName) setField('celebrantName', payload.celebrantName);
        if (payload.eventDate) setField('eventDate', payload.eventDate);
        if (payload.eventTime) setField('eventTime', payload.eventTime);
        if (payload.eventVenue) setField('eventVenue', payload.eventVenue);
        if (payload.eventMessage) setField('eventMessage', payload.eventMessage);

        // Handle specialized fields based on event type if needed
        if (payload.companyName) setField('companyName', payload.companyName);
        if (payload.babyName) setField('babyName', payload.babyName);
        if (payload.partyName) setField('partyName', payload.partyName);
        if (payload.brideName) setField('brideName', payload.brideName);
        if (payload.groomName) setField('groomName', payload.groomName);
    }

    handleQuickAction(action) {
        const prompts = {
            'how-to-create': 'How do I create an invitation on PhoVite?',
            'best-vibe': 'What vibe should I choose for my event?',
            'event-tips': 'Give me tips for making my invitation memorable'
        };

        const input = document.getElementById('ai-input');
        input.value = prompts[action] || '';
        input.focus();
        this.sendMessage();
    }

    addMessage(message) {
        const container = document.getElementById('ai-messages');
        const messageEl = document.createElement('div');
        messageEl.className = `ai-message ${message.role}`;

        const avatar = message.role === 'assistant'
            ? '<div class="message-avatar ai"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path></svg></div>'
            : '<div class="message-avatar user"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg></div>';

        messageEl.innerHTML = `
            ${avatar}
            <div class="message-content">
                <p>${this.formatMessage(message.content)}</p>
            </div>
        `;

        container.appendChild(messageEl);

        // Scroll to bottom with smooth animation
        setTimeout(() => {
            container.scrollTo({
                top: container.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);

        this.messages.push(message);
    }

    showTypingIndicator() {
        this.isTyping = true;
        const container = document.getElementById('ai-messages');
        const typingEl = document.createElement('div');
        typingEl.className = 'ai-message assistant typing-indicator';
        typingEl.id = 'typing-indicator';
        typingEl.innerHTML = `
            <div class="message-avatar ai"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path></svg></div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        container.appendChild(typingEl);
        container.scrollTop = container.scrollHeight;
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    formatMessage(content) {
        // Convert markdown-like syntax to HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }

    getPageContext() {
        // Provide context about current page
        const path = window.location.pathname;
        const pageContext = {
            page: path,
            url: window.location.href
        };

        if (path.includes('create')) {
            pageContext.context = 'creating_invitation';
        } else if (path.includes('dashboard')) {
            pageContext.context = 'viewing_dashboard';
        } else if (path === '/') {
            pageContext.context = 'landing_page';
        }

        return pageContext;
    }
}

// Initialize AI Assistant when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.phoViteAssistant = new PhoViteAssistant();
});
