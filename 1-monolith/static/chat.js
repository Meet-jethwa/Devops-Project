const state = {messages: [], requestId: null, composing: false, controller: null, sessionId: 'session-' + Date.now()};
const log = document.getElementById('message-log');
const emptyState = document.getElementById('empty-state');
const form = document.getElementById('composer');
const input = document.getElementById('message-input');
const send = document.getElementById('send-button');
const stop = document.getElementById('stop-button');
const errorBox = document.getElementById('chat-error');
const language = document.getElementById('language');
const newChat = document.getElementById('new-chat');
const sessionList = document.getElementById('session-list');

const translations = {
  en: {
    language: 'Language', newChat: '+ New chat', session: 'This session', advisor: 'Sugarcane field advisor',
    tagline: 'Ask clearly. Review the reasoning. Decide locally.', home: 'Home', empty: 'How can I help with your sugarcane crop?',
    suggestions: ['When should I irrigate after rain?', 'How much urea for tillering stage?', 'Leaves are turning yellow, why?', 'Drip vs flood irrigation?'],
    message: 'Message', placeholder: 'Ask about irrigation, moisture, or crop stage...', send: 'Send message', stop: 'Stop',
    copy: 'Copy response', copied: 'Copied', helpful: 'Helpful', notHelpful: 'Not helpful or edit', regenerate: 'Regenerate response',
    overridePrompt: 'What should the advisory say instead?', feedbackError: 'Feedback could not be recorded.', thinking: 'Thinking…',
    unavailable: 'The advisory service is unavailable.', emptyResponse: 'The advisor returned an empty response.', retry: 'Please retry.',
    demo: 'Demo mode: model not loaded. Responses are illustrative until the trained model is available.',
    backend: 'The backend is not reachable. Start the API and retry.'
  },
  hi: {
    language: 'भाषा', newChat: '+ नई बातचीत', session: 'यह सत्र', advisor: 'गन्ना खेत सलाहकार',
    tagline: 'स्पष्ट पूछें। कारण समझें। स्थानीय निर्णय लें।', home: 'होम', empty: 'मैं आपके गन्ने की फसल में कैसे मदद कर सकता हूँ?',
    suggestions: ['बारिश के बाद सिंचाई कब करें?', 'कल्ले निकलने की अवस्था में यूरिया कितना दें?', 'पत्तियां पीली क्यों हो रही हैं?', 'ड्रिप और फ्लड सिंचाई में क्या अंतर है?'],
    message: 'संदेश', placeholder: 'सिंचाई, नमी या फसल की अवस्था के बारे में पूछें...', send: 'संदेश भेजें', stop: 'रोकें',
    copy: 'उत्तर कॉपी करें', copied: 'कॉपी किया गया', helpful: 'उपयोगी', notHelpful: 'अनुपयोगी या संपादित करें', regenerate: 'उत्तर फिर बनाएं',
    overridePrompt: 'सलाह में क्या लिखा होना चाहिए?', feedbackError: 'प्रतिक्रिया दर्ज नहीं हो सकी।', thinking: 'सोचा जा रहा है…',
    unavailable: 'सलाह सेवा उपलब्ध नहीं है।', emptyResponse: 'सलाहकार ने खाली उत्तर दिया।', retry: 'कृपया फिर प्रयास करें।',
    demo: 'डेमो मोड: मॉडल लोड नहीं हुआ है। प्रशिक्षित मॉडल उपलब्ध होने तक उत्तर उदाहरण के लिए हैं।',
    backend: 'बैकएंड उपलब्ध नहीं है। API शुरू करके फिर प्रयास करें।'
  },
  mr: {
    language: 'भाषा', newChat: '+ नवीन संभाषण', session: 'हे सत्र', advisor: 'ऊस शेती सल्लागार',
    tagline: 'स्पष्ट विचारा. कारण समजून घ्या. स्थानिक निर्णय घ्या.', home: 'मुख्यपृष्ठ', empty: 'तुमच्या ऊस पिकासाठी मी कशी मदत करू शकतो?',
    suggestions: ['पावसानंतर सिंचन कधी करावे?', 'फुटवे अवस्थेत युरिया किती द्यावा?', 'पाने पिवळी का पडत आहेत?', 'ठिबक आणि पाट सिंचनात काय फरक आहे?'],
    message: 'संदेश', placeholder: 'सिंचन, ओलावा किंवा पिकाच्या अवस्थेबद्दल विचारा...', send: 'संदेश पाठवा', stop: 'थांबवा',
    copy: 'उत्तर कॉपी करा', copied: 'कॉपी केले', helpful: 'उपयुक्त', notHelpful: 'उपयुक्त नाही किंवा संपादित करा', regenerate: 'उत्तर पुन्हा तयार करा',
    overridePrompt: 'सल्ल्यात त्याऐवजी काय लिहावे?', feedbackError: 'अभिप्राय नोंदवता आला नाही.', thinking: 'विचार सुरू आहे…',
    unavailable: 'सल्ला सेवा उपलब्ध नाही.', emptyResponse: 'सल्लागाराने रिक्त उत्तर दिले.', retry: 'कृपया पुन्हा प्रयत्न करा.',
    demo: 'डेमो मोड: मॉडेल लोड झालेले नाही. प्रशिक्षित मॉडेल उपलब्ध होईपर्यंत उत्तरे उदाहरणार्थ आहेत.',
    backend: 'बॅकएंड उपलब्ध नाही. API सुरू करून पुन्हा प्रयत्न करा.'
  },
  gu: {
    language: 'ભાષા', newChat: '+ નવો ચેટ', session: 'આ સત્ર', advisor: 'શેરડીના પાક માટેના સલાહકાર',
    tagline: 'સ્પષ્ટપણે પૂછો. કારણોની સમીક્ષા કરો. સ્થાનિક સ્તરે નિર્ણય લો.', home: 'હોમ', empty: 'હું તમારા શેરડીના પાકમાં કેવી રીતે મદદ કરી શકું?',
    suggestions: ['વરસાદ પછી મારે ક્યારે સિંચાઈ કરવી જોઈએ?', 'ફૂટવાની અવસ્થા (tillering stage) માટે કેટલું યુરિયા આપવું?', 'પાંદડા પીળા પડી રહ્યા છે, કેમ?', 'ટપક સિંચાઈ વિરુદ્ધ પૂર (ધોરિયા) સિંચાઈ?'],
    message: 'સંદેશ', placeholder: 'સિંચાઈ, ભેજ અથવા પાકની અવસ્થા વિશે પૂછો...', send: 'સંદેશ મોકલો', stop: 'અટકાવો',
    copy: 'જવાબ કૉપી કરો', copied: 'કૉપી થયું', helpful: 'ઉપયોગી', notHelpful: 'ઉપયોગી નથી અથવા સંપાદિત કરો', regenerate: 'જવાબ ફરી બનાવો',
    overridePrompt: 'સલાહમાં તેના બદલે શું લખવું જોઈએ?', feedbackError: 'પ્રતિસાદ નોંધાઈ શક્યો નથી.', thinking: 'વિચારી રહ્યા છીએ…',
    unavailable: 'સલાહ સેવા ઉપલબ્ધ નથી.', emptyResponse: 'સલાહકારે ખાલી જવાબ આપ્યો.', retry: 'કૃપા કરીને ફરી પ્રયાસ કરો.',
    demo: 'ડેમો મોડ: મોડેલ લોડ થયું નથી. પ્રશિક્ષિત મોડેલ ઉપલબ્ધ થાય ત્યાં સુધી જવાબો ઉદાહરણરૂપ છે.',
    backend: 'બેકએન્ડ ઉપલબ્ધ નથી. API શરૂ કરીને ફરી પ્રયાસ કરો.'
  },
  pa: {
    language: 'ਭਾਸ਼ਾ', newChat: '+ ਨਵੀਂ ਗੱਲਬਾਤ', session: 'ਇਹ ਸੈਸ਼ਨ', advisor: 'ਗੰਨੇ ਦਾ ਖੇਤ ਸਲਾਹਕਾਰ',
    tagline: 'ਸਾਫ਼ ਪੁੱਛੋ। ਕਾਰਨ ਸਮਝੋ। ਸਥਾਨਕ ਫੈਸਲਾ ਲਓ।', home: 'ਮੁੱਖ ਪੰਨਾ', empty: 'ਮੈਂ ਤੁਹਾਡੀ ਗੰਨੇ ਦੀ ਫਸਲ ਵਿੱਚ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?',
    suggestions: ['ਮੀਂਹ ਤੋਂ ਬਾਅਦ ਸਿੰਚਾਈ ਕਦੋਂ ਕਰੀਏ?', 'ਟਿਲਰਿੰਗ ਪੜਾਅ ਵਿੱਚ ਯੂਰੀਆ ਕਿੰਨੀ ਪਾਈਏ?', 'ਪੱਤੇ ਪੀਲੇ ਕਿਉਂ ਹੋ ਰਹੇ ਹਨ?', 'ਡ੍ਰਿਪ ਅਤੇ ਹੜ੍ਹ ਸਿੰਚਾਈ ਵਿੱਚ ਕੀ ਫਰਕ ਹੈ?'],
    message: 'ਸੁਨੇਹਾ', placeholder: 'ਸਿੰਚਾਈ, ਨਮੀ ਜਾਂ ਫਸਲ ਦੇ ਪੜਾਅ ਬਾਰੇ ਪੁੱਛੋ...', send: 'ਸੁਨੇਹਾ ਭੇਜੋ', stop: 'ਰੋਕੋ',
    copy: 'ਜਵਾਬ ਕਾਪੀ ਕਰੋ', copied: 'ਕਾਪੀ ਹੋ ਗਿਆ', helpful: 'ਮਦਦਗਾਰ', notHelpful: 'ਮਦਦਗਾਰ ਨਹੀਂ ਜਾਂ ਸੋਧੋ', regenerate: 'ਜਵਾਬ ਦੁਬਾਰਾ ਬਣਾਓ',
    overridePrompt: 'ਸਲਾਹ ਵਿੱਚ ਇਸ ਦੀ ਥਾਂ ਕੀ ਲਿਖਣਾ ਚਾਹੀਦਾ ਹੈ?', feedbackError: 'ਫੀਡਬੈਕ ਦਰਜ ਨਹੀਂ ਹੋ ਸਕਿਆ।', thinking: 'ਸੋਚਿਆ ਜਾ ਰਿਹਾ ਹੈ…',
    unavailable: 'ਸਲਾਹ ਸੇਵਾ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।', emptyResponse: 'ਸਲਾਹਕਾਰ ਨੇ ਖਾਲੀ ਜਵਾਬ ਦਿੱਤਾ।', retry: 'ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।',
    demo: 'ਡੈਮੋ ਮੋਡ: ਮਾਡਲ ਲੋਡ ਨਹੀਂ ਹੋਇਆ। ਸਿਖਲਾਈ ਪ੍ਰਾਪਤ ਮਾਡਲ ਉਪਲਬਧ ਹੋਣ ਤੱਕ ਜਵਾਬ ਉਦਾਹਰਨ ਵਜੋਂ ਹਨ।',
    backend: 'ਬੈਕਐਂਡ ਉਪਲਬਧ ਨਹੀਂ ਹੈ। API ਸ਼ੁਰੂ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।'
  },
  kn: {
    language: 'ಭಾಷೆ', newChat: '+ ಹೊಸ ಸಂಭಾಷಣೆ', session: 'ಈ ಸೆಷನ್', advisor: 'ಕಬ್ಬು ಹೊಲ ಸಲಹೆಗಾರ',
    tagline: 'ಸ್ಪಷ್ಟವಾಗಿ ಕೇಳಿ. ಕಾರಣ ತಿಳಿಯಿರಿ. ಸ್ಥಳೀಯ ನಿರ್ಧಾರ ತೆಗೆದುಕೊಳ್ಳಿ.', home: 'ಮುಖಪುಟ', empty: 'ನಿಮ್ಮ ಕಬ್ಬಿನ ಬೆಳೆಗೆ ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?',
    suggestions: ['ಮಳೆಯ ನಂತರ ನೀರಾವರಿ ಯಾವಾಗ ಮಾಡಬೇಕು?', 'ಟಿಲ್ಲರಿಂಗ್ ಹಂತದಲ್ಲಿ ಯೂರಿಯಾವನ್ನು ಎಷ್ಟು ಹಾಕಬೇಕು?', 'ಎಲೆಗಳು ಏಕೆ ಹಳದಿಯಾಗುತ್ತಿವೆ?', 'ಡ್ರಿಪ್ ಮತ್ತು ಫ್ಲಡ್ ನೀರಾವರಿಯಲ್ಲಿ ಏನು ವ್ಯತ್ಯಾಸ?'],
    message: 'ಸಂದೇಶ', placeholder: 'ನೀರಾವರಿ, ತೇವಾಂಶ ಅಥವಾ ಬೆಳೆಯ ಹಂತದ ಬಗ್ಗೆ ಕೇಳಿ...', send: 'ಸಂದೇಶ ಕಳುಹಿಸಿ', stop: 'ನಿಲ್ಲಿಸಿ',
    copy: 'ಉತ್ತರವನ್ನು ನಕಲಿಸಿ', copied: 'ನಕಲಿಸಲಾಗಿದೆ', helpful: 'ಉಪಯುಕ್ತ', notHelpful: 'ಉಪಯುಕ್ತವಲ್ಲ ಅಥವಾ ಸಂಪಾದಿಸಿ', regenerate: 'ಉತ್ತರವನ್ನು ಮತ್ತೆ ರಚಿಸಿ',
    overridePrompt: 'ಸಲಹೆಯಲ್ಲಿ ಬದಲಿಗೆ ಏನು ಬರೆಯಬೇಕು?', feedbackError: 'ಪ್ರತಿಕ್ರಿಯೆಯನ್ನು ದಾಖಲಿಸಲಾಗಲಿಲ್ಲ.', thinking: 'ಯೋಚಿಸಲಾಗುತ್ತಿದೆ…',
    unavailable: 'ಸಲಹೆ ಸೇವೆ ಲಭ್ಯವಿಲ್ಲ.', emptyResponse: 'ಸಲಹೆಗಾರರು ಖಾಲಿ ಉತ್ತರ ನೀಡಿದ್ದಾರೆ.', retry: 'ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.',
    demo: 'ಡೆಮೊ ಮೋಡ್: ಮಾದರಿ ಲೋಡ್ ಆಗಿಲ್ಲ. ತರಬೇತಿ ಪಡೆದ ಮಾದರಿ ಲಭ್ಯವಾಗುವವರೆಗೆ ಉತ್ತರಗಳು ಉದಾಹರಣಾತ್ಮಕವಾಗಿವೆ.',
    backend: 'ಬ್ಯಾಕೆಂಡ್ ಸಂಪರ್ಕ ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ. API ಪ್ರಾರಂಭಿಸಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.'
  }
};

const languageNames = {
  en: {en: 'English', hi: 'Hindi', mr: 'Marathi', gu: 'Gujarati', pa: 'Punjabi', kn: 'Kannada'},
  hi: {en: 'अंग्रेज़ी', hi: 'हिन्दी', mr: 'मराठी', gu: 'गुजराती', pa: 'पंजाबी', kn: 'कन्नड़'},
  mr: {en: 'इंग्रजी', hi: 'हिंदी', mr: 'मराठी', gu: 'गुजराती', pa: 'पंजाबी', kn: 'कन्नड'},
  gu: {en: 'અંગ્રેજી', hi: 'હિન્દી', mr: 'મરાઠી', gu: 'ગુજરાતી', pa: 'પંજાબી', kn: 'કન્નડ'},
  pa: {en: 'ਅੰਗਰੇਜ਼ੀ', hi: 'ਹਿੰਦੀ', mr: 'ਮਰਾਠੀ', gu: 'ਗੁਜਰਾਤੀ', pa: 'ਪੰਜਾਬੀ', kn: 'ਕੰਨੜ'},
  kn: {en: 'ಇಂಗ್ಲಿಷ್', hi: 'ಹಿಂದಿ', mr: 'ಮರಾಠಿ', gu: 'ಗುಜರಾತಿ', pa: 'ಪಂಜಾಬಿ', kn: 'ಕನ್ನಡ'}
};

let copy = translations[language.value] || translations.en;

function applyLanguage() {
  copy = translations[language.value] || translations.en;
  document.documentElement.lang = language.value;
  document.title = `${copy.advisor} | FLoraAI`;
  document.querySelector('.sidebar').setAttribute('aria-label', copy.advisor);
  document.querySelector('.sidebar-label[for="language"]').textContent = copy.language;
  newChat.textContent = copy.newChat;
  document.querySelector('.sidebar > .sidebar-label:not([for])').textContent = copy.session;
  document.querySelector('.chat-topbar strong').textContent = copy.advisor;
  document.querySelector('.chat-topbar p').textContent = copy.tagline;
  document.querySelector('.chat-topbar a').textContent = copy.home;
  document.querySelector('.empty-state h1').textContent = copy.empty;
  document.querySelectorAll('.suggestion').forEach((button, index) => { button.textContent = copy.suggestions[index]; });
  input.setAttribute('aria-label', copy.message);
  input.placeholder = copy.placeholder;
  send.setAttribute('aria-label', copy.send);
  stop.textContent = copy.stop;
  document.querySelectorAll('option').forEach((option) => { option.textContent = languageNames[language.value][option.value]; });
  if (!state.messages.length) renderConversation();
  setError('');
  checkHealth();
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character]));
}

function markdownLite(value) {
  return escapeHtml(value).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/^[-*] (.+)$/gm, '• $1').replace(/\n/g, '<br>');
}

function setError(message) {
  errorBox.textContent = message;
  errorBox.hidden = !message;
}

function appendMessage(role, content, data = null) {
  const wrapper = document.createElement('article');
  wrapper.className = `message ${role}`;
  const avatar = role === 'assistant' ? '<div class="avatar"><img src="/static/logo.png" alt="FLoraAI"></div>' : '';
  let details = '';
  if (role === 'assistant' && data) {
    const hasSuggestions = Array.isArray(data.suggestions) && data.suggestions.length > 0;
    const suggestions = hasSuggestions ? data.suggestions.map((suggestion) => `<button class="next-suggestion" data-next-question="${escapeHtml(suggestion)}">${escapeHtml(suggestion)}</button>`).join('') : '';
    const sugLabel = (hasSuggestions && data.suggestions_label) ? `<p class="suggestions-label">${escapeHtml(data.suggestions_label)}</p>` : '';
    const nextQuestionsBlock = hasSuggestions ? `<div class="next-questions">${sugLabel}<div>${suggestions}</div></div>` : '';
    details = `<div class="action-row"><button data-action="copy" aria-label="${copy.copy}" title="${copy.copy}">⧉</button><button data-action="accept" aria-label="${copy.helpful}" title="${copy.helpful}">✓</button><button data-action="override" aria-label="${copy.notHelpful}" title="${copy.notHelpful}">✎</button><button data-action="regenerate" aria-label="${copy.regenerate}" title="${copy.regenerate}">↻</button></div>${nextQuestionsBlock}`;
  }
  wrapper.innerHTML = `${avatar}<div class="message-body"><div class="message-content">${markdownLite(content)}</div>${details}</div>`;
  if (role === 'assistant' && data) bindActions(wrapper, data, content);
  log.appendChild(wrapper);
  return wrapper;
}

function renderConversation() {
  log.innerHTML = '';
  if (!state.messages.length) { log.appendChild(emptyState); return; }
  state.messages.forEach((message) => appendMessage(message.role, message.content, message.data));
  log.scrollTop = log.scrollHeight;
}

function bindActions(wrapper, data, content) {
  wrapper.querySelector('[data-action="copy"]')?.addEventListener('click', async (event) => {
    await navigator.clipboard.writeText(content);
    event.currentTarget.textContent = copy.copied;
  });
  wrapper.querySelector('[data-action="accept"]')?.addEventListener('click', () => sendFeedback('accept', null));
  wrapper.querySelector('[data-action="override"]')?.addEventListener('click', () => {
    const note = prompt(copy.overridePrompt);
    if (note) sendFeedback('override', note);
  });
  wrapper.querySelector('[data-action="regenerate"]')?.addEventListener('click', () => {
    const lastUser = [...state.messages].reverse().find((message) => message.role === 'user');
    if (lastUser) requestAdvice(lastUser.content);
  });
  wrapper.querySelectorAll('[data-next-question]').forEach((button) => button.addEventListener('click', () => {
    requestAdvice(button.dataset.nextQuestion);
  }));
}

async function sendFeedback(action, overrideText) {
  if (!state.requestId) return;
  try {
    await fetch('/api/feedback', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({request_id: state.requestId, action, override_text: overrideText})});
  } catch (error) { setError(copy.feedbackError); }
}

function updateComposer() {
  send.disabled = !input.value.trim() || state.controller !== null;
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 150)}px`;
}

async function requestAdvice(message) {
  state.controller = new AbortController();
  send.disabled = true;
  stop.hidden = false;
  setError('');
  state.messages.push({role: 'user', content: message});
  renderConversation();
  const thinking = appendMessage('assistant', copy.thinking);
  try {
    const response = await fetch('/api/chat', {method: 'POST', headers: {'Content-Type': 'application/json'}, signal: state.controller.signal, body: JSON.stringify({message, lang: language.value, session_id: state.sessionId})});
    if (!response.ok) throw new Error(copy.unavailable);
    const data = await response.json();
    if (!data.advisory) throw new Error(copy.emptyResponse);
    thinking.remove();
    state.requestId = data.request_id;
    state.messages.push({role: 'assistant', content: data.advisory, data});
    renderConversation();
    updateSessionList(message);
  } catch (error) {
    thinking.remove();
    if (error.name !== 'AbortError') setError(`${error.message} ${copy.retry}`);
  } finally {
    state.controller = null;
    stop.hidden = true;
    updateComposer();
  }
}

stop.addEventListener('click', () => state.controller?.abort());

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || state.controller) return;
  input.value = '';
  updateComposer();
  requestAdvice(message);
});
input.addEventListener('input', updateComposer);
input.addEventListener('compositionstart', () => { state.composing = true; });
input.addEventListener('compositionend', () => { state.composing = false; });
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey && !state.composing) { event.preventDefault(); form.requestSubmit(); }
});

document.querySelectorAll('.suggestion').forEach((button) => button.addEventListener('click', () => requestAdvice(button.textContent)));
newChat.addEventListener('click', () => { state.messages = []; state.requestId = null; state.sessionId = 'session-' + Date.now(); setError(''); renderConversation(); input.focus(); });
language.addEventListener('change', () => {
  state.controller?.abort();
  state.controller = null;
  state.messages = [];
  state.requestId = null;
  state.sessionId = 'session-' + Date.now();
  sessionList.innerHTML = '';
  input.value = '';
  applyLanguage();
  updateComposer();
  input.focus();
});

function updateSessionList(title) {
  const item = document.createElement('p');
  item.textContent = title.length > 27 ? `${title.slice(0, 27)}…` : title;
  item.style.color = 'var(--text-muted)';
  item.style.fontSize = '13px';
  sessionList.prepend(item);
}

async function checkHealth() {
  try {
    const response = await fetch('/api/health');
    const health = await response.json();
    if (!health.model_loaded) {
      const banner = document.getElementById('demo-banner');
      banner.textContent = copy.demo;
      banner.hidden = false;
    }
  } catch (error) {
    setError(copy.backend);
  }
}

applyLanguage();
renderConversation();
updateComposer();
checkHealth();
