const demoBanner = document.getElementById('demo-banner');
const video = document.querySelector('.video-wrap video');
const videoPlaceholder = document.querySelector('.video-placeholder');
const launcher = document.getElementById('chat-launcher');
const floatingChat = document.getElementById('floating-chat');
const closeChat = document.getElementById('chat-close');
const miniForm = document.getElementById('mini-form');
const miniInput = document.getElementById('mini-input');
const miniMessages = document.getElementById('mini-messages');

function addMiniMessage(text, role) {
  const node = document.createElement('div');
  node.className = `mini-message ${role}`;
  node.textContent = text;
  miniMessages.appendChild(node);
  miniMessages.scrollTop = miniMessages.scrollHeight;
}

async function checkHealth() {
  try {
    const response = await fetch('/api/health');
    const health = await response.json();
    if (!health.model_loaded && demoBanner) {
      demoBanner.textContent = 'Demo mode: model not loaded. Responses are illustrative until the trained model is available.';
      demoBanner.hidden = false;
    }
  } catch (error) {
    if (demoBanner) {
      demoBanner.textContent = 'Demo mode: the advisory service is not reachable right now.';
      demoBanner.hidden = false;
    }
  }
}

if (video && videoPlaceholder) {
  video.addEventListener('error', () => {
    video.hidden = true;
    videoPlaceholder.hidden = false;
  });
}

launcher?.addEventListener('click', () => {
  floatingChat.hidden = false;
  miniInput?.focus();
});
closeChat?.addEventListener('click', () => { floatingChat.hidden = true; });
window.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && floatingChat && !floatingChat.hidden) floatingChat.hidden = true;
});

miniForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = miniInput.value.trim();
  if (!message) return;
  miniInput.value = '';
  addMiniMessage(message, 'user');
  addMiniMessage('Thinking about that field question…', 'assistant');
  const pending = miniMessages.lastElementChild;
  try {
    const response = await fetch('/api/chat', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message, lang: 'en', session_id: 'landing'})
    });
    if (!response.ok) throw new Error('The advisory service returned an error.');
    const data = await response.json();
    pending.textContent = data.advisory || 'No advisory was returned.';
  } catch (error) {
    pending.textContent = 'The advisor is temporarily unavailable. Please try the full chat page.';
    pending.classList.add('error-message');
  }
});

checkHealth();
