// Extracts article text from the current page DOM
function extractArticleText() {
  const clone = document.cloneNode(true);
  const doc = clone.documentElement || clone;

  // Remove noise elements
  ['script', 'style', 'nav', 'footer', 'header', 'aside',
   'advertisement', 'noscript', 'iframe'].forEach(tag => {
    doc.querySelectorAll(tag).forEach(el => el.remove());
  });

  // Try semantic content selectors in priority order
  const selectors = [
    'article',
    'main',
    '[role="main"]',
    '.article-content',
    '.article-body',
    '.post-content',
    '.entry-content',
    '.story-content',
    '.news-content',
    '.content-body',
    '#article-body',
    '#content',
    '.content',
  ];

  for (const selector of selectors) {
    const el = doc.querySelector(selector);
    if (el) {
      const text = el.innerText || el.textContent || '';
      const cleaned = text.replace(/\s+/g, ' ').trim();
      if (cleaned.length >= 50) return cleaned.slice(0, 10000);
    }
  }

  // Fall back to body
  const bodyText = (document.body.innerText || document.body.textContent || '')
    .replace(/\s+/g, ' ')
    .trim();
  return bodyText.slice(0, 10000);
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === 'EXTRACT_TEXT') {
    sendResponse({ text: extractArticleText() });
  }
  return true;
});
