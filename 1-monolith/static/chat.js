/* Phase 1 copied frontend asset; behavior intentionally unchanged. */`r`nconst state = {messages: [], requestId: null, composing: false, controller: null};
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
    overridePrompt: 'What should the advisory say instead?', feedbackError: 'Feedback could not be recorded.', thinking: 'Thinkingâ€¦',
    unavailable: 'The advisory service is unavailable.', emptyResponse: 'The advisor returned an empty response.', retry: 'Please retry.',
    demo: 'Demo mode: model not loaded. Responses are illustrative until the trained model is available.',
    backend: 'The backend is not reachable. Start the API and retry.'
  },
  hi: {
    language: 'à¤­à¤¾à¤·à¤¾', newChat: '+ à¤¨à¤ˆ à¤¬à¤¾à¤¤à¤šà¥€à¤¤', session: 'à¤¯à¤¹ à¤¸à¤¤à¥à¤°', advisor: 'à¤—à¤¨à¥à¤¨à¤¾ à¤–à¥‡à¤¤ à¤¸à¤²à¤¾à¤¹à¤•à¤¾à¤°',
    tagline: 'à¤¸à¥à¤ªà¤·à¥à¤Ÿ à¤ªà¥‚à¤›à¥‡à¤‚à¥¤ à¤•à¤¾à¤°à¤£ à¤¸à¤®à¤à¥‡à¤‚à¥¤ à¤¸à¥à¤¥à¤¾à¤¨à¥€à¤¯ à¤¨à¤¿à¤°à¥à¤£à¤¯ à¤²à¥‡à¤‚à¥¤', home: 'à¤¹à¥‹à¤®', empty: 'à¤®à¥ˆà¤‚ à¤†à¤ªà¤•à¥‡ à¤—à¤¨à¥à¤¨à¥‡ à¤•à¥€ à¤«à¤¸à¤² à¤®à¥‡à¤‚ à¤•à¥ˆà¤¸à¥‡ à¤®à¤¦à¤¦ à¤•à¤° à¤¸à¤•à¤¤à¤¾ à¤¹à¥‚à¤?',
    suggestions: ['à¤¬à¤¾à¤°à¤¿à¤¶ à¤•à¥‡ à¤¬à¤¾à¤¦ à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ à¤•à¤¬ à¤•à¤°à¥‡à¤‚?', 'à¤•à¤²à¥à¤²à¥‡ à¤¨à¤¿à¤•à¤²à¤¨à¥‡ à¤•à¥€ à¤…à¤µà¤¸à¥à¤¥à¤¾ à¤®à¥‡à¤‚ à¤¯à¥‚à¤°à¤¿à¤¯à¤¾ à¤•à¤¿à¤¤à¤¨à¤¾ à¤¦à¥‡à¤‚?', 'à¤ªà¤¤à¥à¤¤à¤¿à¤¯à¤¾à¤‚ à¤ªà¥€à¤²à¥€ à¤•à¥à¤¯à¥‹à¤‚ à¤¹à¥‹ à¤°à¤¹à¥€ à¤¹à¥ˆà¤‚?', 'à¤¡à¥à¤°à¤¿à¤ª à¤”à¤° à¤«à¥à¤²à¤¡ à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ à¤®à¥‡à¤‚ à¤•à¥à¤¯à¤¾ à¤…à¤‚à¤¤à¤° à¤¹à¥ˆ?'],
    message: 'à¤¸à¤‚à¤¦à¥‡à¤¶', placeholder: 'à¤¸à¤¿à¤‚à¤šà¤¾à¤ˆ, à¤¨à¤®à¥€ à¤¯à¤¾ à¤«à¤¸à¤² à¤•à¥€ à¤…à¤µà¤¸à¥à¤¥à¤¾ à¤•à¥‡ à¤¬à¤¾à¤°à¥‡ à¤®à¥‡à¤‚ à¤ªà¥‚à¤›à¥‡à¤‚...', send: 'à¤¸à¤‚à¤¦à¥‡à¤¶ à¤­à¥‡à¤œà¥‡à¤‚', stop: 'à¤°à¥‹à¤•à¥‡à¤‚',
    copy: 'à¤‰à¤¤à¥à¤¤à¤° à¤•à¥‰à¤ªà¥€ à¤•à¤°à¥‡à¤‚', copied: 'à¤•à¥‰à¤ªà¥€ à¤•à¤¿à¤¯à¤¾ à¤—à¤¯à¤¾', helpful: 'à¤‰à¤ªà¤¯à¥‹à¤—à¥€', notHelpful: 'à¤…à¤¨à¥à¤ªà¤¯à¥‹à¤—à¥€ à¤¯à¤¾ à¤¸à¤‚à¤ªà¤¾à¤¦à¤¿à¤¤ à¤•à¤°à¥‡à¤‚', regenerate: 'à¤‰à¤¤à¥à¤¤à¤° à¤«à¤¿à¤° à¤¬à¤¨à¤¾à¤à¤‚',
    overridePrompt: 'à¤¸à¤²à¤¾à¤¹ à¤®à¥‡à¤‚ à¤•à¥à¤¯à¤¾ à¤²à¤¿à¤–à¤¾ à¤¹à¥‹à¤¨à¤¾ à¤šà¤¾à¤¹à¤¿à¤?', feedbackError: 'à¤ªà¥à¤°à¤¤à¤¿à¤•à¥à¤°à¤¿à¤¯à¤¾ à¤¦à¤°à¥à¤œ à¤¨à¤¹à¥€à¤‚ à¤¹à¥‹ à¤¸à¤•à¥€à¥¤', thinking: 'à¤¸à¥‹à¤šà¤¾ à¤œà¤¾ à¤°à¤¹à¤¾ à¤¹à¥ˆâ€¦',
    unavailable: 'à¤¸à¤²à¤¾à¤¹ à¤¸à¥‡à¤µà¤¾ à¤‰à¤ªà¤²à¤¬à¥à¤§ à¤¨à¤¹à¥€à¤‚ à¤¹à¥ˆà¥¤', emptyResponse: 'à¤¸à¤²à¤¾à¤¹à¤•à¤¾à¤° à¤¨à¥‡ à¤–à¤¾à¤²à¥€ à¤‰à¤¤à¥à¤¤à¤° à¤¦à¤¿à¤¯à¤¾à¥¤', retry: 'à¤•à¥ƒà¤ªà¤¯à¤¾ à¤«à¤¿à¤° à¤ªà¥à¤°à¤¯à¤¾à¤¸ à¤•à¤°à¥‡à¤‚à¥¤',
    demo: 'à¤¡à¥‡à¤®à¥‹ à¤®à¥‹à¤¡: à¤®à¥‰à¤¡à¤² à¤²à¥‹à¤¡ à¤¨à¤¹à¥€à¤‚ à¤¹à¥à¤† à¤¹à¥ˆà¥¤ à¤ªà¥à¤°à¤¶à¤¿à¤•à¥à¤·à¤¿à¤¤ à¤®à¥‰à¤¡à¤² à¤‰à¤ªà¤²à¤¬à¥à¤§ à¤¹à¥‹à¤¨à¥‡ à¤¤à¤• à¤‰à¤¤à¥à¤¤à¤° à¤‰à¤¦à¤¾à¤¹à¤°à¤£ à¤•à¥‡ à¤²à¤¿à¤ à¤¹à¥ˆà¤‚à¥¤',
    backend: 'à¤¬à¥ˆà¤•à¤à¤‚à¤¡ à¤‰à¤ªà¤²à¤¬à¥à¤§ à¤¨à¤¹à¥€à¤‚ à¤¹à¥ˆà¥¤ API à¤¶à¥à¤°à¥‚ à¤•à¤°à¤•à¥‡ à¤«à¤¿à¤° à¤ªà¥à¤°à¤¯à¤¾à¤¸ à¤•à¤°à¥‡à¤‚à¥¤'
  },
  mr: {
    language: 'à¤­à¤¾à¤·à¤¾', newChat: '+ à¤¨à¤µà¥€à¤¨ à¤¸à¤‚à¤­à¤¾à¤·à¤£', session: 'à¤¹à¥‡ à¤¸à¤¤à¥à¤°', advisor: 'à¤Šà¤¸ à¤¶à¥‡à¤¤à¥€ à¤¸à¤²à¥à¤²à¤¾à¤—à¤¾à¤°',
    tagline: 'à¤¸à¥à¤ªà¤·à¥à¤Ÿ à¤µà¤¿à¤šà¤¾à¤°à¤¾. à¤•à¤¾à¤°à¤£ à¤¸à¤®à¤œà¥‚à¤¨ à¤˜à¥à¤¯à¤¾. à¤¸à¥à¤¥à¤¾à¤¨à¤¿à¤• à¤¨à¤¿à¤°à¥à¤£à¤¯ à¤˜à¥à¤¯à¤¾.', home: 'à¤®à¥à¤–à¥à¤¯à¤ªà¥ƒà¤·à¥à¤ ', empty: 'à¤¤à¥à¤®à¤šà¥à¤¯à¤¾ à¤Šà¤¸ à¤ªà¤¿à¤•à¤¾à¤¸à¤¾à¤ à¥€ à¤®à¥€ à¤•à¤¶à¥€ à¤®à¤¦à¤¤ à¤•à¤°à¥‚ à¤¶à¤•à¤¤à¥‹?',
    suggestions: ['à¤ªà¤¾à¤µà¤¸à¤¾à¤¨à¤‚à¤¤à¤° à¤¸à¤¿à¤‚à¤šà¤¨ à¤•à¤§à¥€ à¤•à¤°à¤¾à¤µà¥‡?', 'à¤«à¥à¤Ÿà¤µà¥‡ à¤…à¤µà¤¸à¥à¤¥à¥‡à¤¤ à¤¯à¥à¤°à¤¿à¤¯à¤¾ à¤•à¤¿à¤¤à¥€ à¤¦à¥à¤¯à¤¾à¤µà¤¾?', 'à¤ªà¤¾à¤¨à¥‡ à¤ªà¤¿à¤µà¤³à¥€ à¤•à¤¾ à¤ªà¤¡à¤¤ à¤†à¤¹à¥‡à¤¤?', 'à¤ à¤¿à¤¬à¤• à¤†à¤£à¤¿ à¤ªà¤¾à¤Ÿ à¤¸à¤¿à¤‚à¤šà¤¨à¤¾à¤¤ à¤•à¤¾à¤¯ à¤«à¤°à¤• à¤†à¤¹à¥‡?'],
    message: 'à¤¸à¤‚à¤¦à¥‡à¤¶', placeholder: 'à¤¸à¤¿à¤‚à¤šà¤¨, à¤“à¤²à¤¾à¤µà¤¾ à¤•à¤¿à¤‚à¤µà¤¾ à¤ªà¤¿à¤•à¤¾à¤šà¥à¤¯à¤¾ à¤…à¤µà¤¸à¥à¤¥à¥‡à¤¬à¤¦à¥à¤¦à¤² à¤µà¤¿à¤šà¤¾à¤°à¤¾...', send: 'à¤¸à¤‚à¤¦à¥‡à¤¶ à¤ªà¤¾à¤ à¤µà¤¾', stop: 'à¤¥à¤¾à¤‚à¤¬à¤µà¤¾',
    copy: 'à¤‰à¤¤à¥à¤¤à¤° à¤•à¥‰à¤ªà¥€ à¤•à¤°à¤¾', copied: 'à¤•à¥‰à¤ªà¥€ à¤•à¥‡à¤²à¥‡', helpful: 'à¤‰à¤ªà¤¯à¥à¤•à¥à¤¤', notHelpful: 'à¤‰à¤ªà¤¯à¥à¤•à¥à¤¤ à¤¨à¤¾à¤¹à¥€ à¤•à¤¿à¤‚à¤µà¤¾ à¤¸à¤‚à¤ªà¤¾à¤¦à¤¿à¤¤ à¤•à¤°à¤¾', regenerate: 'à¤‰à¤¤à¥à¤¤à¤° à¤ªà¥à¤¨à¥à¤¹à¤¾ à¤¤à¤¯à¤¾à¤° à¤•à¤°à¤¾',
    overridePrompt: 'à¤¸à¤²à¥à¤²à¥à¤¯à¤¾à¤¤ à¤¤à¥à¤¯à¤¾à¤à¤µà¤œà¥€ à¤•à¤¾à¤¯ à¤²à¤¿à¤¹à¤¾à¤µà¥‡?', feedbackError: 'à¤…à¤­à¤¿à¤ªà¥à¤°à¤¾à¤¯ à¤¨à¥‹à¤‚à¤¦à¤µà¤¤à¤¾ à¤†à¤²à¤¾ à¤¨à¤¾à¤¹à¥€.', thinking: 'à¤µà¤¿à¤šà¤¾à¤° à¤¸à¥à¤°à¥‚ à¤†à¤¹à¥‡â€¦',
    unavailable: 'à¤¸à¤²à¥à¤²à¤¾ à¤¸à¥‡à¤µà¤¾ à¤‰à¤ªà¤²à¤¬à¥à¤§ à¤¨à¤¾à¤¹à¥€.', emptyResponse: 'à¤¸à¤²à¥à¤²à¤¾à¤—à¤¾à¤°à¤¾à¤¨à¥‡ à¤°à¤¿à¤•à¥à¤¤ à¤‰à¤¤à¥à¤¤à¤° à¤¦à¤¿à¤²à¥‡.', retry: 'à¤•à¥ƒà¤ªà¤¯à¤¾ à¤ªà¥à¤¨à¥à¤¹à¤¾ à¤ªà¥à¤°à¤¯à¤¤à¥à¤¨ à¤•à¤°à¤¾.',
    demo: 'à¤¡à¥‡à¤®à¥‹ à¤®à¥‹à¤¡: à¤®à¥‰à¤¡à¥‡à¤² à¤²à¥‹à¤¡ à¤à¤¾à¤²à¥‡à¤²à¥‡ à¤¨à¤¾à¤¹à¥€. à¤ªà¥à¤°à¤¶à¤¿à¤•à¥à¤·à¤¿à¤¤ à¤®à¥‰à¤¡à¥‡à¤² à¤‰à¤ªà¤²à¤¬à¥à¤§ à¤¹à¥‹à¤ˆà¤ªà¤°à¥à¤¯à¤‚à¤¤ à¤‰à¤¤à¥à¤¤à¤°à¥‡ à¤‰à¤¦à¤¾à¤¹à¤°à¤£à¤¾à¤°à¥à¤¥ à¤†à¤¹à¥‡à¤¤.',
    backend: 'à¤¬à¥…à¤•à¤à¤‚à¤¡ à¤‰à¤ªà¤²à¤¬à¥à¤§ à¤¨à¤¾à¤¹à¥€. API à¤¸à¥à¤°à¥‚ à¤•à¤°à¥‚à¤¨ à¤ªà¥à¤¨à¥à¤¹à¤¾ à¤ªà¥à¤°à¤¯à¤¤à¥à¤¨ à¤•à¤°à¤¾.'
  },
  gu: {
    language: 'àª­àª¾àª·àª¾', newChat: '+ àª¨àªµà«‹ àªšà«‡àªŸ', session: 'àª† àª¸àª¤à«àª°', advisor: 'àª¶à«‡àª°àª¡à«€àª¨àª¾ àªªàª¾àª• àª®àª¾àªŸà«‡àª¨àª¾ àª¸àª²àª¾àª¹àª•àª¾àª°',
    tagline: 'àª¸à«àªªàª·à«àªŸàªªàª£à«‡ àªªà«‚àª›à«‹. àª•àª¾àª°àª£à«‹àª¨à«€ àª¸àª®à«€àª•à«àª·àª¾ àª•àª°à«‹. àª¸à«àª¥àª¾àª¨àª¿àª• àª¸à«àª¤àª°à«‡ àª¨àª¿àª°à«àª£àª¯ àª²à«‹.', home: 'àª¹à«‹àª®', empty: 'àª¹à«àª‚ àª¤àª®àª¾àª°àª¾ àª¶à«‡àª°àª¡à«€àª¨àª¾ àªªàª¾àª•àª®àª¾àª‚ àª•à«‡àªµà«€ àª°à«€àª¤à«‡ àª®àª¦àª¦ àª•àª°à«€ àª¶àª•à«àª‚?',
    suggestions: ['àªµàª°àª¸àª¾àª¦ àªªàª›à«€ àª®àª¾àª°à«‡ àª•à«àª¯àª¾àª°à«‡ àª¸àª¿àª‚àªšàª¾àªˆ àª•àª°àªµà«€ àªœà«‹àªˆàª?', 'àª«à«‚àªŸàªµàª¾àª¨à«€ àª…àªµàª¸à«àª¥àª¾ (tillering stage) àª®àª¾àªŸà«‡ àª•à«‡àªŸàª²à«àª‚ àª¯à«àª°àª¿àª¯àª¾ àª†àªªàªµà«àª‚?', 'àªªàª¾àª‚àª¦àª¡àª¾ àªªà«€àª³àª¾ àªªàª¡à«€ àª°àª¹à«àª¯àª¾ àª›à«‡, àª•à«‡àª®?', 'àªŸàªªàª• àª¸àª¿àª‚àªšàª¾àªˆ àªµàª¿àª°à«àª¦à«àª§ àªªà«‚àª° (àª§à«‹àª°àª¿àª¯àª¾) àª¸àª¿àª‚àªšàª¾àªˆ?'],
    message: 'àª¸àª‚àª¦à«‡àª¶', placeholder: 'àª¸àª¿àª‚àªšàª¾àªˆ, àª­à«‡àªœ àª…àª¥àªµàª¾ àªªàª¾àª•àª¨à«€ àª…àªµàª¸à«àª¥àª¾ àªµàª¿àª¶à«‡ àªªà«‚àª›à«‹...', send: 'àª¸àª‚àª¦à«‡àª¶ àª®à«‹àª•àª²à«‹', stop: 'àª…àªŸàª•àª¾àªµà«‹',
    copy: 'àªœàªµàª¾àª¬ àª•à«‰àªªà«€ àª•àª°à«‹', copied: 'àª•à«‰àªªà«€ àª¥àª¯à«àª‚', helpful: 'àª‰àªªàª¯à«‹àª—à«€', notHelpful: 'àª‰àªªàª¯à«‹àª—à«€ àª¨àª¥à«€ àª…àª¥àªµàª¾ àª¸àª‚àªªàª¾àª¦àª¿àª¤ àª•àª°à«‹', regenerate: 'àªœàªµàª¾àª¬ àª«àª°à«€ àª¬àª¨àª¾àªµà«‹',
    overridePrompt: 'àª¸àª²àª¾àª¹àª®àª¾àª‚ àª¤à«‡àª¨àª¾ àª¬àª¦àª²à«‡ àª¶à«àª‚ àª²àª–àªµà«àª‚ àªœà«‹àªˆàª?', feedbackError: 'àªªà«àª°àª¤àª¿àª¸àª¾àª¦ àª¨à«‹àª‚àª§àª¾àªˆ àª¶àª•à«àª¯à«‹ àª¨àª¥à«€.', thinking: 'àªµàª¿àªšàª¾àª°à«€ àª°àª¹à«àª¯àª¾ àª›à«€àªâ€¦',
    unavailable: 'àª¸àª²àª¾àª¹ àª¸à«‡àªµàª¾ àª‰àªªàª²àª¬à«àª§ àª¨àª¥à«€.', emptyResponse: 'àª¸àª²àª¾àª¹àª•àª¾àª°à«‡ àª–àª¾àª²à«€ àªœàªµàª¾àª¬ àª†àªªà«àª¯à«‹.', retry: 'àª•à«ƒàªªàª¾ àª•àª°à«€àª¨à«‡ àª«àª°à«€ àªªà«àª°àª¯àª¾àª¸ àª•àª°à«‹.',
    demo: 'àª¡à«‡àª®à«‹ àª®à«‹àª¡: àª®à«‹àª¡à«‡àª² àª²à«‹àª¡ àª¥àª¯à«àª‚ àª¨àª¥à«€. àªªà«àª°àª¶àª¿àª•à«àª·àª¿àª¤ àª®à«‹àª¡à«‡àª² àª‰àªªàª²àª¬à«àª§ àª¥àª¾àª¯ àª¤à«àª¯àª¾àª‚ àª¸à«àª§à«€ àªœàªµàª¾àª¬à«‹ àª‰àª¦àª¾àª¹àª°àª£àª°à«‚àªª àª›à«‡.',
    backend: 'àª¬à«‡àª•àªàª¨à«àª¡ àª‰àªªàª²àª¬à«àª§ àª¨àª¥à«€. API àª¶àª°à«‚ àª•àª°à«€àª¨à«‡ àª«àª°à«€ àªªà«àª°àª¯àª¾àª¸ àª•àª°à«‹.'
  },
  pa: {
    language: 'à¨­à¨¾à¨¸à¨¼à¨¾', newChat: '+ à¨¨à¨µà©€à¨‚ à¨—à©±à¨²à¨¬à¨¾à¨¤', session: 'à¨‡à¨¹ à¨¸à©ˆà¨¸à¨¼à¨¨', advisor: 'à¨—à©°à¨¨à©‡ à¨¦à¨¾ à¨–à©‡à¨¤ à¨¸à¨²à¨¾à¨¹à¨•à¨¾à¨°',
    tagline: 'à¨¸à¨¾à¨«à¨¼ à¨ªà©à©±à¨›à©‹à¥¤ à¨•à¨¾à¨°à¨¨ à¨¸à¨®à¨à©‹à¥¤ à¨¸à¨¥à¨¾à¨¨à¨• à¨«à©ˆà¨¸à¨²à¨¾ à¨²à¨“à¥¤', home: 'à¨®à©à©±à¨– à¨ªà©°à¨¨à¨¾', empty: 'à¨®à©ˆà¨‚ à¨¤à©à¨¹à¨¾à¨¡à©€ à¨—à©°à¨¨à©‡ à¨¦à©€ à¨«à¨¸à¨² à¨µà¨¿à©±à¨š à¨•à¨¿à¨µà©‡à¨‚ à¨®à¨¦à¨¦ à¨•à¨° à¨¸à¨•à¨¦à¨¾ à¨¹à¨¾à¨‚?',
    suggestions: ['à¨®à©€à¨‚à¨¹ à¨¤à©‹à¨‚ à¨¬à¨¾à¨…à¨¦ à¨¸à¨¿à©°à¨šà¨¾à¨ˆ à¨•à¨¦à©‹à¨‚ à¨•à¨°à©€à¨?', 'à¨Ÿà¨¿à¨²à¨°à¨¿à©°à¨— à¨ªà©œà¨¾à¨… à¨µà¨¿à©±à¨š à¨¯à©‚à¨°à©€à¨† à¨•à¨¿à©°à¨¨à©€ à¨ªà¨¾à¨ˆà¨?', 'à¨ªà©±à¨¤à©‡ à¨ªà©€à¨²à©‡ à¨•à¨¿à¨‰à¨‚ à¨¹à©‹ à¨°à¨¹à©‡ à¨¹à¨¨?', 'à¨¡à©à¨°à¨¿à¨ª à¨…à¨¤à©‡ à¨¹à©œà©à¨¹ à¨¸à¨¿à©°à¨šà¨¾à¨ˆ à¨µà¨¿à©±à¨š à¨•à©€ à¨«à¨°à¨• à¨¹à©ˆ?'],
    message: 'à¨¸à©à¨¨à©‡à¨¹à¨¾', placeholder: 'à¨¸à¨¿à©°à¨šà¨¾à¨ˆ, à¨¨à¨®à©€ à¨œà¨¾à¨‚ à¨«à¨¸à¨² à¨¦à©‡ à¨ªà©œà¨¾à¨… à¨¬à¨¾à¨°à©‡ à¨ªà©à©±à¨›à©‹...', send: 'à¨¸à©à¨¨à©‡à¨¹à¨¾ à¨­à©‡à¨œà©‹', stop: 'à¨°à©‹à¨•à©‹',
    copy: 'à¨œà¨µà¨¾à¨¬ à¨•à¨¾à¨ªà©€ à¨•à¨°à©‹', copied: 'à¨•à¨¾à¨ªà©€ à¨¹à©‹ à¨—à¨¿à¨†', helpful: 'à¨®à¨¦à¨¦à¨—à¨¾à¨°', notHelpful: 'à¨®à¨¦à¨¦à¨—à¨¾à¨° à¨¨à¨¹à©€à¨‚ à¨œà¨¾à¨‚ à¨¸à©‹à¨§à©‹', regenerate: 'à¨œà¨µà¨¾à¨¬ à¨¦à©à¨¬à¨¾à¨°à¨¾ à¨¬à¨£à¨¾à¨“',
    overridePrompt: 'à¨¸à¨²à¨¾à¨¹ à¨µà¨¿à©±à¨š à¨‡à¨¸ à¨¦à©€ à¨¥à¨¾à¨‚ à¨•à©€ à¨²à¨¿à¨–à¨£à¨¾ à¨šà¨¾à¨¹à©€à¨¦à¨¾ à¨¹à©ˆ?', feedbackError: 'à¨«à©€à¨¡à¨¬à©ˆà¨• à¨¦à¨°à¨œ à¨¨à¨¹à©€à¨‚ à¨¹à©‹ à¨¸à¨•à¨¿à¨†à¥¤', thinking: 'à¨¸à©‹à¨šà¨¿à¨† à¨œà¨¾ à¨°à¨¿à¨¹à¨¾ à¨¹à©ˆâ€¦',
    unavailable: 'à¨¸à¨²à¨¾à¨¹ à¨¸à©‡à¨µà¨¾ à¨‰à¨ªà¨²à¨¬à¨§ à¨¨à¨¹à©€à¨‚ à¨¹à©ˆà¥¤', emptyResponse: 'à¨¸à¨²à¨¾à¨¹à¨•à¨¾à¨° à¨¨à©‡ à¨–à¨¾à¨²à©€ à¨œà¨µà¨¾à¨¬ à¨¦à¨¿à©±à¨¤à¨¾à¥¤', retry: 'à¨•à¨¿à¨°à¨ªà¨¾ à¨•à¨°à¨•à©‡ à¨¦à©à¨¬à¨¾à¨°à¨¾ à¨•à©‹à¨¸à¨¼à¨¿à¨¸à¨¼ à¨•à¨°à©‹à¥¤',
    demo: 'à¨¡à©ˆà¨®à©‹ à¨®à©‹à¨¡: à¨®à¨¾à¨¡à¨² à¨²à©‹à¨¡ à¨¨à¨¹à©€à¨‚ à¨¹à©‹à¨‡à¨†à¥¤ à¨¸à¨¿à¨–à¨²à¨¾à¨ˆ à¨ªà©à¨°à¨¾à¨ªà¨¤ à¨®à¨¾à¨¡à¨² à¨‰à¨ªà¨²à¨¬à¨§ à¨¹à©‹à¨£ à¨¤à©±à¨• à¨œà¨µà¨¾à¨¬ à¨‰à¨¦à¨¾à¨¹à¨°à¨¨ à¨µà¨œà©‹à¨‚ à¨¹à¨¨à¥¤',
    backend: 'à¨¬à©ˆà¨•à¨à¨‚à¨¡ à¨‰à¨ªà¨²à¨¬à¨§ à¨¨à¨¹à©€à¨‚ à¨¹à©ˆà¥¤ API à¨¸à¨¼à©à¨°à©‚ à¨•à¨°à¨•à©‡ à¨¦à©à¨¬à¨¾à¨°à¨¾ à¨•à©‹à¨¸à¨¼à¨¿à¨¸à¨¼ à¨•à¨°à©‹à¥¤'
  },
  kn: {
    language: 'à²­à²¾à²·à³†', newChat: '+ à²¹à³Šà²¸ à²¸à²‚à²­à²¾à²·à²£à³†', session: 'à²ˆ à²¸à³†à²·à²¨à³', advisor: 'à²•à²¬à³à²¬à³ à²¹à³Šà²² à²¸à²²à²¹à³†à²—à²¾à²°',
    tagline: 'à²¸à³à²ªà²·à³à²Ÿà²µà²¾à²—à²¿ à²•à³‡à²³à²¿. à²•à²¾à²°à²£ à²¤à²¿à²³à²¿à²¯à²¿à²°à²¿. à²¸à³à²¥à²³à³€à²¯ à²¨à²¿à²°à³à²§à²¾à²° à²¤à³†à²—à³†à²¦à³à²•à³Šà²³à³à²³à²¿.', home: 'à²®à³à²–à²ªà³à²Ÿ', empty: 'à²¨à²¿à²®à³à²® à²•à²¬à³à²¬à²¿à²¨ à²¬à³†à²³à³†à²—à³† à²¨à²¾à²¨à³ à²¹à³‡à²—à³† à²¸à²¹à²¾à²¯ à²®à²¾à²¡à²¬à²¹à³à²¦à³?',
    suggestions: ['à²®à²³à³†à²¯ à²¨à²‚à²¤à²° à²¨à³€à²°à²¾à²µà²°à²¿ à²¯à²¾à²µà²¾à²— à²®à²¾à²¡à²¬à³‡à²•à³?', 'à²Ÿà²¿à²²à³à²²à²°à²¿à²‚à²—à³ à²¹à²‚à²¤à²¦à²²à³à²²à²¿ à²¯à³‚à²°à²¿à²¯à²¾à²µà²¨à³à²¨à³ à²Žà²·à³à²Ÿà³ à²¹à²¾à²•à²¬à³‡à²•à³?', 'à²Žà²²à³†à²—à²³à³ à²à²•à³† à²¹à²³à²¦à²¿à²¯à²¾à²—à³à²¤à³à²¤à²¿à²µà³†?', 'à²¡à³à²°à²¿à²ªà³ à²®à²¤à³à²¤à³ à²«à³à²²à²¡à³ à²¨à³€à²°à²¾à²µà²°à²¿à²¯à²²à³à²²à²¿ à²à²¨à³ à²µà³à²¯à²¤à³à²¯à²¾à²¸?'],
    message: 'à²¸à²‚à²¦à³‡à²¶', placeholder: 'à²¨à³€à²°à²¾à²µà²°à²¿, à²¤à³‡à²µà²¾à²‚à²¶ à²…à²¥à²µà²¾ à²¬à³†à²³à³†à²¯ à²¹à²‚à²¤à²¦ à²¬à²—à³à²—à³† à²•à³‡à²³à²¿...', send: 'à²¸à²‚à²¦à³‡à²¶ à²•à²³à³à²¹à²¿à²¸à²¿', stop: 'à²¨à²¿à²²à³à²²à²¿à²¸à²¿',
    copy: 'à²‰à²¤à³à²¤à²°à²µà²¨à³à²¨à³ à²¨à²•à²²à²¿à²¸à²¿', copied: 'à²¨à²•à²²à²¿à²¸à²²à²¾à²—à²¿à²¦à³†', helpful: 'à²‰à²ªà²¯à³à²•à³à²¤', notHelpful: 'à²‰à²ªà²¯à³à²•à³à²¤à²µà²²à³à²² à²…à²¥à²µà²¾ à²¸à²‚à²ªà²¾à²¦à²¿à²¸à²¿', regenerate: 'à²‰à²¤à³à²¤à²°à²µà²¨à³à²¨à³ à²®à²¤à³à²¤à³† à²°à²šà²¿à²¸à²¿',
    overridePrompt: 'à²¸à²²à²¹à³†à²¯à²²à³à²²à²¿ à²¬à²¦à²²à²¿à²—à³† à²à²¨à³ à²¬à²°à³†à²¯à²¬à³‡à²•à³?', feedbackError: 'à²ªà³à²°à²¤à²¿à²•à³à²°à²¿à²¯à³†à²¯à²¨à³à²¨à³ à²¦à²¾à²–à²²à²¿à²¸à²²à²¾à²—à²²à²¿à²²à³à²².', thinking: 'à²¯à³‹à²šà²¿à²¸à²²à²¾à²—à³à²¤à³à²¤à²¿à²¦à³†â€¦',
    unavailable: 'à²¸à²²à²¹à³† à²¸à³‡à²µà³† à²²à²­à³à²¯à²µà²¿à²²à³à²².', emptyResponse: 'à²¸à²²à²¹à³†à²—à²¾à²°à²°à³ à²–à²¾à²²à²¿ à²‰à²¤à³à²¤à²° à²¨à³€à²¡à²¿à²¦à³à²¦à²¾à²°à³†.', retry: 'à²¦à²¯à²µà²¿à²Ÿà³à²Ÿà³ à²®à²¤à³à²¤à³† à²ªà³à²°à²¯à²¤à³à²¨à²¿à²¸à²¿.',
    demo: 'à²¡à³†à²®à³Š à²®à³‹à²¡à³: à²®à²¾à²¦à²°à²¿ à²²à³‹à²¡à³ à²†à²—à²¿à²²à³à²². à²¤à²°à²¬à³‡à²¤à²¿ à²ªà²¡à³†à²¦ à²®à²¾à²¦à²°à²¿ à²²à²­à³à²¯à²µà²¾à²—à³à²µà²µà²°à³†à²—à³† à²‰à²¤à³à²¤à²°à²—à²³à³ à²‰à²¦à²¾à²¹à²°à²£à²¾à²¤à³à²®à²•à²µà²¾à²—à²¿à²µà³†.',
    backend: 'à²¬à³à²¯à²¾à²•à³†à²‚à²¡à³ à²¸à²‚à²ªà²°à³à²• à²¸à²¾à²§à³à²¯à²µà²¾à²—à³à²¤à³à²¤à²¿à²²à³à²². API à²ªà³à²°à²¾à²°à²‚à²­à²¿à²¸à²¿ à²®à²¤à³à²¤à³† à²ªà³à²°à²¯à²¤à³à²¨à²¿à²¸à²¿.'
  }
};

const languageNames = {
  en: {en: 'English', hi: 'Hindi', mr: 'Marathi', gu: 'Gujarati', pa: 'Punjabi', kn: 'Kannada'},
  hi: {en: 'à¤…à¤‚à¤—à¥à¤°à¥‡à¤œà¤¼à¥€', hi: 'à¤¹à¤¿à¤¨à¥à¤¦à¥€', mr: 'à¤®à¤°à¤¾à¤ à¥€', gu: 'à¤—à¥à¤œà¤°à¤¾à¤¤à¥€', pa: 'à¤ªà¤‚à¤œà¤¾à¤¬à¥€', kn: 'à¤•à¤¨à¥à¤¨à¤¡à¤¼'},
  mr: {en: 'à¤‡à¤‚à¤—à¥à¤°à¤œà¥€', hi: 'à¤¹à¤¿à¤‚à¤¦à¥€', mr: 'à¤®à¤°à¤¾à¤ à¥€', gu: 'à¤—à¥à¤œà¤°à¤¾à¤¤à¥€', pa: 'à¤ªà¤‚à¤œà¤¾à¤¬à¥€', kn: 'à¤•à¤¨à¥à¤¨à¤¡'},
  gu: {en: 'àª…àª‚àª—à«àª°à«‡àªœà«€', hi: 'àª¹àª¿àª¨à«àª¦à«€', mr: 'àª®àª°àª¾àª à«€', gu: 'àª—à«àªœàª°àª¾àª¤à«€', pa: 'àªªàª‚àªœàª¾àª¬à«€', kn: 'àª•àª¨à«àª¨àª¡'},
  pa: {en: 'à¨…à©°à¨—à¨°à©‡à¨œà¨¼à©€', hi: 'à¨¹à¨¿à©°à¨¦à©€', mr: 'à¨®à¨°à¨¾à¨ à©€', gu: 'à¨—à©à¨œà¨°à¨¾à¨¤à©€', pa: 'à¨ªà©°à¨œà¨¾à¨¬à©€', kn: 'à¨•à©°à¨¨à©œ'},
  kn: {en: 'à²‡à²‚à²—à³à²²à²¿à²·à³', hi: 'à²¹à²¿à²‚à²¦à²¿', mr: 'à²®à²°à²¾à² à²¿', gu: 'à²—à³à²œà²°à²¾à²¤à²¿', pa: 'à²ªà²‚à²œà²¾à²¬à²¿', kn: 'à²•à²¨à³à²¨à²¡'}
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
  return escapeHtml(value).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/^[-*] (.+)$/gm, 'â€¢ $1').replace(/\n/g, '<br>');
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
    const suggestions = (data.suggestions || []).map((suggestion) => `<button class="next-suggestion" data-next-question="${escapeHtml(suggestion)}">${escapeHtml(suggestion)}</button>`).join('');
    const sugLabel = data.suggestions_label ? `<p class="suggestions-label">${escapeHtml(data.suggestions_label)}</p>` : '';
    details = `<div class="action-row"><button data-action="copy" aria-label="${copy.copy}" title="${copy.copy}">â§‰</button><button data-action="accept" aria-label="${copy.helpful}" title="${copy.helpful}">âœ“</button><button data-action="override" aria-label="${copy.notHelpful}" title="${copy.notHelpful}">âœŽ</button><button data-action="regenerate" aria-label="${copy.regenerate}" title="${copy.regenerate}">â†»</button></div><div class="next-questions">${sugLabel}<div>${suggestions}</div></div>`;
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
    const response = await fetch('/api/chat', {method: 'POST', headers: {'Content-Type': 'application/json'}, signal: state.controller.signal, body: JSON.stringify({message, lang: language.value, session_id: 'browser-session'})});
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
newChat.addEventListener('click', () => { state.messages = []; state.requestId = null; setError(''); renderConversation(); input.focus(); });
language.addEventListener('change', () => {
  state.controller?.abort();
  state.controller = null;
  state.messages = [];
  state.requestId = null;
  sessionList.innerHTML = '';
  input.value = '';
  applyLanguage();
  updateComposer();
  input.focus();
});

function updateSessionList(title) {
  const item = document.createElement('p');
  item.textContent = title.length > 27 ? `${title.slice(0, 27)}â€¦` : title;
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
