/**
 * PhoVite AI Assistant - Intelligent Helper
 * Provides contextual assistance for invitation creation and website navigation
 */

class PhoViteAssistant {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.isTyping = false;
        this.init();
    }

    init() {
        this.createAssistantUI();
        this.attachEventListeners();
        this.showWelcomeMessage();
    }

    createAssistantUI() {
        // Create assistant container
        const assistantHTML = `
            <!-- AI Assistant Floating Button -->
            <button id="ai-assistant-btn" class="ai-assistant-trigger" aria-label="Open AI Assistant">
                <div class="ai-glow"></div>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    <circle cx="12" cy="11" r="1" fill="currentColor"></circle>
                    <circle cx="8" cy="11" r="1" fill="currentColor"></circle>
                    <circle cx="16" cy="11" r="1" fill="currentColor"></circle>
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
                    <button id="ai-close-btn" class="ai-close-btn" aria-label="Close Assistant">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12"></path>
                        </svg>
                    </button>
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
                    <textarea 
                        id="ai-input" 
                        class="ai-input" 
                        placeholder="Ask me anything about creating invitations..."
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
        const input = document.getElementById('ai-input');
        const quickActions = document.querySelectorAll('.quick-action-btn');

        assistantBtn?.addEventListener('click', () => this.toggleAssistant());
        closeBtn?.addEventListener('click', () => this.closeAssistant());
        sendBtn?.addEventListener('click', () => this.sendMessage());

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
        }
    }

    closeAssistant() {
        this.isOpen = false;
        const panel = document.getElementById('ai-assistant-panel');
        const btn = document.getElementById('ai-assistant-btn');
        panel.classList.remove('open');
        btn.classList.remove('active');
    }

    showWelcomeMessage() {
        setTimeout(() => {
            const welcomeMsg = {
                role: 'assistant',
                content: '👋 Hi! I\'m your PhoVite AI Assistant. I can help you create stunning invitations, choose the perfect vibe, and answer any questions about our platform. How can I assist you today?'
            };
            this.addMessage(welcomeMsg);
        }, 1000);
    }

    async sendMessage() {
        const input = document.getElementById('ai-input');
        const message = input.value.trim();

        if (!message || this.isTyping) return;

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
