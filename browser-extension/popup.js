// Cross-browser API shim (Firefox uses `browser`, Chrome/Edge use `chrome`)
const api = typeof browser !== 'undefined' ? browser : chrome;

const API_URL = 'https://epap.vercel.app/analyze';

const $ = id => document.getElementById(id);

let currentTab = null;

// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
  const [tab] = await api.tabs.query({ active: true, currentWindow: true });
  currentTab = tab;

  const urlEl = $('currentUrl');
  if (tab && tab.url) {
    urlEl.textContent = tab.url;
    urlEl.title = tab.url;
    // Pre-fill source from hostname
    try {
      const hostname = new URL(tab.url).hostname.replace(/^www\./, '');
      $('sourceInput').placeholder = `π.χ. ${hostname}`;
    } catch (_) {}
  } else {
    urlEl.textContent = 'Δεν βρέθηκε URL';
    $('analyzeBtn').disabled = true;
  }
}

// ── Article text extraction ───────────────────────────────────────────────────

async function extractText(tabId) {
  // MV3 Chrome/Edge: inject content script on demand
  if (api.scripting) {
    const results = await api.scripting.executeScript({
      target: { tabId },
      files: ['content.js'],
    });
    // content.js is now injected; send message to get text
    return new Promise(resolve => {
      chrome.tabs.sendMessage(tabId, { type: 'EXTRACT_TEXT' }, response => {
        resolve(response ? response.text : '');
      });
    });
  }

  // MV2 Firefox: content script already injected via manifest
  return new Promise(resolve => {
    api.tabs.sendMessage(tabId, { type: 'EXTRACT_TEXT' }, response => {
      resolve(response ? response.text : '');
    });
  });
}

// ── Score helpers ─────────────────────────────────────────────────────────────

function parseScore(analysis) {
  const match = analysis.match(/ΣΥΝΟΛΙΚΗ ΑΞΙΟΛΟΓΗΣΗ[:\s*]*(\d+)/);
  return match ? parseInt(match[1], 10) : null;
}

function scoreClass(score) {
  if (score >= 67) return 'high';
  if (score >= 34) return 'mid';
  return 'low';
}

function scoreDescription(score) {
  if (score >= 80) return 'Υψηλή αξιοπιστία';
  if (score >= 60) return 'Μέτρια αξιοπιστία — ελέγξτε τις πηγές';
  if (score >= 40) return 'Χαμηλή αξιοπιστία — προσοχή απαιτείται';
  return 'Πιθανή προπαγάνδα — πολύ χαμηλή αξιοπιστία';
}

// ── Markdown → HTML (minimal) ─────────────────────────────────────────────────

function markdownToHtml(md) {
  return md
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^#{1,3}\s+(.+)$/gm, '<h3>$1</h3>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/^(?!<[hup])/gm, '')
    .replace(/\n/g, ' ')
    .trim();
}

// ── Analyze ───────────────────────────────────────────────────────────────────

async function analyze() {
  setLoading(true);
  hideError();
  $('results').classList.remove('visible');

  try {
    const text = await extractText(currentTab.id);

    if (!text || text.length < 50) {
      showError('Δεν ήταν δυνατή η εξαγωγή αρκετού κειμένου από αυτή τη σελίδα. Δοκιμάστε να ανοίξετε την πλήρη εφαρμογή και να επικολλήσετε το κείμενο χειροκίνητα.');
      return;
    }

    const source = $('sourceInput').value.trim() ||
      (currentTab.url ? new URL(currentTab.url).hostname.replace(/^www\./, '') : '');

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, url: currentTab.url, source }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      showError(data.error || 'Σφάλμα κατά την ανάλυση.');
      return;
    }

    renderResults(data.analysis);

  } catch (err) {
    showError(`Σφάλμα σύνδεσης: ${err.message}`);
  } finally {
    setLoading(false);
  }
}

// ── Render ────────────────────────────────────────────────────────────────────

function renderResults(analysis) {
  const score = parseScore(analysis);

  if (score !== null) {
    const cls = scoreClass(score);
    $('scoreValue').textContent = score;
    $('scoreValue').className = `score-value ${cls}`;
    $('scoreBar').style.width = `${score}%`;
    $('scoreBar').className = `score-bar-fill ${cls}`;
    $('scoreDesc').textContent = scoreDescription(score);
  } else {
    $('scoreValue').textContent = '—';
    $('scoreDesc').textContent = 'Δεν βρέθηκε βαθμολογία';
  }

  $('analysisBox').innerHTML = markdownToHtml(analysis);

  // Link to full app with the current URL pre-filled
  const appUrl = `https://epap.vercel.app/?url=${encodeURIComponent(currentTab.url)}`;
  $('openFull').href = appUrl;

  $('results').classList.add('visible');
}

// ── UI helpers ────────────────────────────────────────────────────────────────

function setLoading(on) {
  $('spinner').classList.toggle('visible', on);
  $('analyzeBtn').disabled = on;
}

function showError(msg) {
  const box = $('errorBox');
  box.textContent = msg;
  box.classList.add('visible');
}

function hideError() {
  $('errorBox').classList.remove('visible');
}

// ── Wire up ───────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  init();
  $('analyzeBtn').addEventListener('click', analyze);
});
