// Navigation
function openArticle(articleId) {
    window.location.href = `/article/${articleId}`;
}

// Floating Chat Logic
function toggleChat() {
    const popup = document.getElementById('chat-popup');
    popup.style.display = (popup.style.display === 'flex') ? 'none' : 'flex';
}

function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const query = input.value.trim();
    if (!query) return;

    appendMessage('user', query);
    input.value = '';

    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(res => res.json())
    .then(data => {
        appendMessage('bot', data.answer);
    })
    .catch(err => {
        appendMessage('bot', 'Neural link failed. Please check your connection.');
    });
}

const chatInput = document.getElementById('chat-input');
if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
}

function appendMessage(role, text) {
    const chatMessages = document.getElementById('chat-messages');
    const div = document.createElement('div');
    const isBot = role === 'bot';
    
    div.className = `message ${role}-message`;
    // Clean styling handled by CSS, but keep core alignment here for safety
    div.style.padding = '1rem';
    div.style.borderRadius = isBot ? '18px 18px 18px 4px' : '18px 18px 4px 18px';
    div.style.marginBottom = '1rem';
    div.style.fontSize = '0.95rem';
    div.style.lineHeight = '1.5';
    div.style.maxWidth = '85%';
    
    if (isBot) {
        div.style.background = 'var(--accent-blue)';
        div.style.color = 'var(--text-main)';
        div.style.alignSelf = 'flex-start';
        div.style.border = '1px solid rgba(99,102,241,0.1)';
    } else {
        div.style.background = 'var(--primary)';
        div.style.color = 'white';
        div.style.alignSelf = 'flex-end';
        div.style.marginLeft = 'auto';
    }
    
    div.innerText = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Refresh News
function refreshNews() {
    const btn = event.currentTarget;
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Syncing...';
    btn.disabled = true;

    fetch('/api/refresh-news', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
            if (data.count > 0) {
                location.reload();
            }
        })
        .catch(() => {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
        });
}
