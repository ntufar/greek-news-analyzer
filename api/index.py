from http.server import BaseHTTPRequestHandler
import json
import os
import re
import hashlib
from mistralai import Mistral
import requests
from bs4 import BeautifulSoup
# Configure Mistral AI
mistral_client = Mistral(api_key=os.getenv('MISTRAL_API_KEY'))

# Simple in-memory cache for analysis results
analysis_cache = {}

def get_cache_key(text, source=""):
    """Generate a cache key for the analysis"""
    content = f"{text[:1000]}_{source}".encode('utf-8')
    return hashlib.md5(content).hexdigest()

def extract_text_from_url(url):
    """Extract text content from a news URL"""
    try:
        if not url.startswith(('http://', 'https://')):
            raise ValueError("Invalid URL format")
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "advertisement"]):
            element.decompose()
        
        # Try multiple selectors for main content
        content_selectors = [
            'main', 'article', '[role="main"]',
            '.content', '.article-content', '.post-content',
            '.entry-content', '.story-content', '.news-content'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if main_content:
            text = main_content.get_text()
        else:
            body = soup.find('body')
            text = body.get_text() if body else soup.get_text()
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) < 100:
            raise ValueError("Insufficient text content extracted")
            
        return text[:3000]  # Limit to 3000 characters
        
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def analyze_greek_news(text, source=""):
    """Analyze Greek news text for propaganda indicators using Mistral"""
    try:
        # Check cache first
        cache_key = get_cache_key(text, source)
        if cache_key in analysis_cache:
            return analysis_cache[cache_key]
        
        prompt = f"""
        Αναλύστε αυτό το ελληνικό άρθρο για πιθανά στοιχεία προπαγάνδας και προκατάληψης:

        Κείμενο: {text[:2000]}
        Πηγή: {source if source else "Άγνωστη"}

        Παρακαλώ αξιολογήστε από 1-100 (1=πιθανή προπαγάνδα, 100=αξιόπισες ειδήσεις) και δώστε λεπτομερή ανάλυση:

        **ΣΥΝΟΛΙΚΗ ΑΞΙΟΛΟΓΗΣΗ: [Βαθμολογία 1-100]**

        **1. ΣΥΝΑΙΣΘΗΜΑΤΙΚΗ ΧΕΙΡΑΓΩΓΗΣΗ:**
        - Χρήση φορτωμένων λέξεων και φράσεων
        - Εκφοβιστική γλώσσα
        - Συναισθηματικές εκφράσεις

        **2. ΔΕΙΚΤΕΣ ΠΡΟΚΑΤΑΛΗΨΗΣ:**
        - Πολιτική ή ιδεολογική κλίση
        - Μονόπλευρη παρουσίαση γεγονότων
        - Επιλογή πηγών και μαρτύρων

        **3. ΑΝΑΛΟΓΙΑ ΓΕΓΟΝΟΤΩΝ vs ΓΝΩΜΕΣ:**
        - Ποσοστό αντικειμενικών γεγονότων
        - Ποσοστό υποκειμενικών ερμηνειών
        - Διαχωρισμός ειδήσεων από σχολιασμό

        **4. ΑΞΙΟΠΙΣΤΙΑ ΠΗΓΗΣ:**
        - Ιστορικό αξιοπιστίας
        - Διαφάνεια και ευθύνη
        - Συνέπεια στην αναφορά

        **5. ΓΛΩΣΣΙΚΗ ΑΝΑΛΥΣΗ:**
        - Χρήση υπερβολών και υπερθετικών
        - Αποφυγή συγκεκριμένων όρων
        - Επιλογή λεξιλογίου

        **6. ΛΟΓΙΚΕΣ ΠΛΑΝΕΣ:**
        - Αναγνώριση λογικών σφαλμάτων
        - Χειραγώγηση δεδομένων
        - Αποφυγή αντίθετων επιχειρημάτων

        **7. ΣΥΣΤΑΣΗ:**
        - Σύσταση για περαιτέρω έλεγχο
        - Προτεινόμενες πηγές για επιπλέον πληροφόρηση

        Απαντήστε στα ελληνικά με σαφή, κατανοητό και δομημένο τρόπο.
        """

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            temperature=0.7
        )
        
        if not response or not response.choices or len(response.choices) == 0:
            raise ValueError("Empty response from Mistral API")
        
        analysis_text = response.choices[0].message.content
        
        if not analysis_text:
            raise ValueError("Empty content in Mistral API response")

        # Cache the result (keep as markdown for mobile app)
        analysis_cache[cache_key] = analysis_text
        return analysis_text
        
    except Exception as e:
        return f"Σφάλμα στην ανάλυση: {str(e)}"

class handler(BaseHTTPRequestHandler):
    def get_main_html(self, url_params=None):
        """Generate the main HTML page with optional URL parameters for sharing"""
        if url_params is None:
            url_params = {}
            
        # Extract shared data from URL parameters
        shared_url = url_params.get('url', [None])[0] if url_params.get('url') else None
        shared_title = url_params.get('title', [None])[0] if url_params.get('title') else None
        shared_text = url_params.get('text', [None])[0] if url_params.get('text') else None
        
        html = """
            <!DOCTYPE html>
            <html lang="el">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
                <title>ΕΠΑΠ - Εληνική Πλατφόρμα Ανάλυσης Παραπληροφόρισης</title>
                
                <!-- PWA Meta Tags -->
                <meta name="description" content="Αναλύστε ελληνικά άρθρα ειδήσεων για στοιχεία προπαγάνδας και προκατάληψης">
                <meta name="keywords" content="ανάλυση ειδήσεων, ελληνικές ειδήσεις, προπαγάνδα, ανίχνευση προπαγάνδας, ανάλυση προκατάληψης, ελληνική ενημέρωση, αξιοπιστία ειδήσεων, fake news, παραπληροφόρηση, ανάλυση μέσων ενημέρωσης">
                <meta name="msvalidate.01" content="7AE8D16C48F5201D71FAF4F7A52231E1" />
                <meta name="theme-color" content="#1e3c72">
                <meta name="apple-mobile-web-app-capable" content="yes">
                <meta name="apple-mobile-web-app-status-bar-style" content="default">
                <meta name="apple-mobile-web-app-title" content="ΕΠΑΠ">
                <meta name="mobile-web-app-capable" content="yes">
                <meta name="application-name" content="ΕΠΑΠ">
                <meta name="apple-touch-fullscreen" content="yes">
                
                <!-- PWA Manifest -->
                <link rel="manifest" href="/static/manifest.json">
                
                <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9549967181261078" crossorigin="anonymous"></script>
                
                <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
                <script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>

                <!-- Icons for different platforms -->
                <link rel="icon" type="image/png" sizes="32x32" href="/static/icons/icon-32x32.png">
                <link rel="icon" type="image/png" sizes="16x16" href="/static/icons/icon-16x16.png">
                <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
                <link rel="apple-touch-icon" sizes="152x152" href="/static/icons/icon-152x152.png">
                <link rel="apple-touch-icon" sizes="180x180" href="/static/icons/icon-192x192.png">
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                        max-width: 860px;
                        margin: 0 auto;
                        padding: 10px;
                        background: linear-gradient(135deg, #e8edf5 0%, #d5dce8 100%);
                        min-height: 100vh;
                        -webkit-font-smoothing: antialiased;
                    }
                    .container {
                        background: #fff;
                        padding: 24px;
                        border-radius: 12px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
                    }
                    .header {
                        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        color: white;
                        padding: 16px 20px;
                        border-radius: 10px;
                        text-align: center;
                        margin-bottom: 20px;
                    }
                    .header h1 { margin: 0; font-size: 1.4rem; }
                    .header p { margin: 4px 0 0; font-size: 0.9rem; opacity: 0.85; }
                    .logo-alpha {
                        display: inline-flex; align-items: center; justify-content: center;
                        width: 40px; height: 40px; border-radius: 10px;
                        background: linear-gradient(135deg, #1e3c72, #2563eb);
                        font-family: Georgia, 'Times New Roman', serif;
                        font-size: 1.5rem; font-weight: 900; color: #fff;
                        vertical-align: middle; margin-right: 10px;
                    }
                    .logo-alpha .check { color: #22c55e; font-size: 0.7rem; margin-left: 1px; }
                    .input-group { margin-bottom: 12px; }
                    label {
                        display: block;
                        margin-bottom: 4px;
                        font-weight: 600;
                        color: #333;
                        font-size: 0.9rem;
                    }
                    input, textarea, select {
                        width: 100%;
                        padding: 10px 12px;
                        border: 1.5px solid #e0e3e8;
                        border-radius: 8px;
                        font-size: 0.95rem;
                        transition: border-color 0.2s;
                        box-sizing: border-box;
                    }
                    input:focus, textarea:focus, select:focus {
                        outline: none;
                        border-color: #2a5298;
                        box-shadow: 0 0 0 3px rgba(42,82,152,0.12);
                    }
                    textarea { height: 140px; resize: vertical; }
                    button {
                        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        color: white;
                        padding: 10px 24px;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 0.95rem;
                        font-weight: 600;
                        transition: all 0.2s;
                        width: 100%;
                    }
                    button:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
                    button:disabled { opacity: 0.6; cursor: not-allowed; }
                    .result {
                        margin-top: 16px;
                        padding: 16px;
                        background: #f8f9fa;
                        border-radius: 10px;
                        border-left: 4px solid #007bff;
                        transition: border-color 0.3s;
                    }
                    .result.card-grade-low { border-left-color: #dc3545; }
                    .result.card-grade-medium { border-left-color: #fd7e14; }
                    .result.card-grade-high { border-left-color: #ffc107; }
                    .result.card-grade-excellent { border-left-color: #28a745; }
                    .loading { text-align: center; padding: 16px; display: none; }
                    .spinner {
                        border: 3px solid #f3f3f3;
                        border-top: 3px solid #2a5298;
                        border-radius: 50%;
                        width: 28px;
                        height: 28px;
                        animation: spin 0.8s linear infinite;
                        margin: 0 auto 8px;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    .analysis-text { line-height: 1.5; font-size: 0.95rem; }
                    .analysis-text h2 {
                        font-size: 1.1rem;
                        color: #1e3c72;
                        margin: 1rem 0 0.4rem;
                        font-weight: 600;
                        border-bottom: 1px solid #e9ecef;
                        padding-bottom: 0.25rem;
                    }
                    .analysis-text h3 {
                        font-size: 1rem;
                        color: #495057;
                        margin: 0.8rem 0 0.3rem;
                        font-weight: 600;
                    }
                    .analysis-text h4, .analysis-text h5, .analysis-text h6 {
                        color: #1e3c72;
                        margin: 0.8rem 0 0.3rem;
                        font-weight: 600;
                    }
                    .analysis-text ul, .analysis-text ol { padding-left: 1.3rem; margin-bottom: 0.75rem; }
                    .analysis-text li { margin-bottom: 0.35rem; }
                    .analysis-text strong { color: #1e3c72; }
                    .analysis-text .grade-low { color: #dc3545; }
                    .analysis-text .grade-medium { color: #fd7e14; }
                    .analysis-text .grade-high { color: #ffc107; }
                    .analysis-text .grade-excellent { color: #28a745; }
                    .analysis-text p { margin-bottom: 0.75rem; }
                    .analysis-text blockquote {
                        border-left: 3px solid #007bff;
                        padding-left: 0.75rem;
                        margin: 0.75rem 0;
                        font-style: italic;
                        color: #6c757d;
                    }
                    .char-count { font-size: 0.8rem; color: #666; margin-top: 4px; }
                    .error { color: #dc3545; background: #f8d7da; padding: 8px 12px; border-radius: 6px; margin: 8px 0; }
                    
                    .install-button {
                        position: fixed; top: 16px; right: 16px;
                        background: #22c55e; color: white; border: none;
                        padding: 8px 14px; border-radius: 8px;
                        font-size: 0.85rem; font-weight: 600; cursor: pointer;
                        z-index: 1000; box-shadow: 0 2px 8px rgba(0,0,0,0.12);
                        display: none;
                    }
                    .install-button:hover { background: #16a34a; }
                    
                    button, input, textarea, select {
                        -webkit-tap-highlight-color: transparent;
                        touch-action: manipulation;
                    }
                    button { -webkit-user-select: none; user-select: none; }
                    
                    @media (max-width: 768px) {
                        body { padding: 6px; }
                        .container { padding: 16px; border-radius: 10px; margin: 4px; }
                        .header { padding: 12px; border-radius: 8px; margin-bottom: 16px; }
                        .header h1 { font-size: 1.2rem; }
                        input, textarea, select { font-size: 16px; padding: 12px; }
                        textarea { height: 120px; }
                        button { padding: 12px 20px; }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1><span class="logo-alpha">Ε<span class="check">✓</span></span>ΕΠΑΠ Εληνική Πλατφόρμα Ανάλυσης Παραπληροφόρισης</h1>
                        <p>Ελέγξτε αν ένα άρθρο περιέχει στοιχεία προπαγάνδας</p>
                        <div style="margin-top: 12px;">
                            <a href="/about" style="color: white; text-decoration: none; background: rgba(255,255,255,0.2); padding: 5px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 500;">
                                <i class="fas fa-info-circle me-1"></i>Σχετικά
                            </a>
                            <a href="/privacy" style="color: white; text-decoration: none; background: rgba(255,255,255,0.2); padding: 5px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 500; margin-left: 6px;">
                                <i class="fas fa-shield-alt me-1"></i>Απόρρητο
                            </a>
                        </div>
                    </div>
                    
                    <div style="background: #f1f8e9; border-left: 4px solid #4caf50; border-radius: 10px; padding: 12px 16px; margin: 16px 0;">
                        <h3 style="color: #2e7d32; font-size: 1rem; margin: 0 0 6px;"><i class="fas fa-book me-1"></i>Οδηγίες Χρήσης</h3>
                        <ol style="margin: 0; padding-left: 1.2rem; color: #424242; font-size: 0.9rem; line-height: 1.7;">
                            <li><strong>Επιλέξτε τρόπο εισαγωγής:</strong> Επικολλήστε κείμενο ή εισάγετε URL.</li>
                            <li><strong>Προσθέστε την πηγή (προαιρετικά):</strong> Το όνομα της εφημερίδας.</li>
                            <li><strong>Κάντε κλικ στο "Ανάλυση":</strong> Η AI αναλύει σε δευτερόλεπτα.</li>
                            <li><strong>Διαβάστε την αναφορά:</strong> Ανάλυση με παραδείγματα και συστάσεις.</li>
                        </ol>
                    </div>
                    
                    
                    <form id="analysisForm">
                        <div class="input-group">
                            <label for="inputType"><i class="fas fa-edit me-1"></i>Τρόπος Εισαγωγής:</label>
                            <select id="inputType" onchange="toggleInputType()">
                                <option value="text">Κείμενο άρθρου</option>
                                <option value="url" selected>URL άρθρου</option>
                            </select>
                        </div>
                        
                        <div class="input-group" id="textInput" style="display: none;">
                            <label for="text"><i class="fas fa-file-text me-1"></i>Κείμενο Άρθρου:</label>
                            <textarea id="text" placeholder="Επικολλήστε εδώ το κείμενο του άρθρου..." maxlength="10000" oninput="updateCharCount()"></textarea>
                            <div class="char-count" id="charCount">0 / 10,000 χαρακτήρες</div>
                        </div>
                        
                        <div class="input-group" id="urlInput">
                            <label for="url"><i class="fas fa-link me-1"></i>URL Άρθρου:</label>
                            <input type="url" id="url" placeholder="https://example.com/article">
                        </div>
                        
                        <div class="input-group">
                            <label for="source"><i class="fas fa-building me-1"></i>Πηγή (προαιρετικό):</label>
                            <input type="text" id="source" placeholder="π.χ. ΕΡΤ, ΣΚΑΪ, ANT1">
                        </div>
                        
                        <button type="submit" id="analyzeBtn"><i class="fas fa-search me-1"></i>Ανάλυση Άρθρου</button>
                    </form>
                    
                    <button id="installBtn" class="install-button">
                        <i class="fas fa-download me-1"></i>Εγκατάσταση
                    </button>
                    
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p style="font-size: 0.9rem;">Ανάλυση σε εξέλιξη...</p>
                    </div>
                    
                    <div id="result" class="result" style="display: none;">
                        <h5 style="margin: 0 0 8px;"><i class="fas fa-chart-line me-1"></i>Αποτελέσματα</h5>
                        <div id="analysis" class="analysis-text"></div>
                    </div>
                    
                    <div style="background: #fff7f0; border-left: 4px solid #f97316; border-radius: 10px; padding: 12px 16px; margin: 16px 0;">
                        <h3 style="color: #c2410c; font-size: 1rem; margin: 0 0 4px;"><i class="fas fa-exclamation-triangle me-1"></i>Προειδοποίηση</h3>
                        <p style="font-size: 0.9rem; color: #5d4037; margin: 0 0 4px;">Η παραπληροφόρηση είναι σοβαρό πρόβλημα. Τα άρθρα μπορεί να περιέχουν:</p>
                        <ul style="margin: 0; padding-left: 1.2rem; color: #5d4037; font-size: 0.85rem; line-height: 1.6;">
                            <li><strong>Μερικές πληροφορίες:</strong> Επιλεκτική παρουσίαση γεγονότων</li>
                            <li><strong>Συναισθηματική χειραγώγηση:</strong> Φορτωμένες λέξεις αντί λογικής</li>
                            <li><strong>Απομόνωση πληροφοριών:</strong> Μόνο μία πλευρά του θέματος</li>
                            <li><strong>Λογικά σφάλματα:</strong> Λογικές πλάνες για πειθώ</li>
                        </ul>
                    </div>
                    
                    <!-- Bottom Ad Unit -->
                    <div style="text-align: center; margin: 12px 0;">
                        <ins class="adsbygoogle"
                             style="display:block"
                             data-ad-client="ca-pub-9549967181261078"
                             data-ad-slot="5866895841"
                             data-ad-format="auto"
                             data-full-width-responsive="true"></ins>
                        <script>
                             (adsbygoogle = window.adsbygoogle || []).push({});
                        </script>
                    </div>
                </div>
                
                <script>
                    // PWA Installation and Service Worker
                    let deferredPrompt;
                    let isInstalled = false;

                    // Check if app is already installed
                    if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true) {
                        isInstalled = true;
                        console.log('App is running in standalone mode');
                    }

                    // Register Service Worker
                    if ('serviceWorker' in navigator) {
                        window.addEventListener('load', async () => {
                            try {
                                console.log('Attempting to register service worker...');
                                const registration = await navigator.serviceWorker.register('/static/sw.js', {
                                    scope: '/'
                                });
                                console.log('SW registered successfully: ', registration);
                                
                                // Check for updates
                                registration.addEventListener('updatefound', () => {
                                    console.log('Service worker update found');
                                    const newWorker = registration.installing;
                                    newWorker.addEventListener('statechange', () => {
                                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                            console.log('New service worker installed, reloading page');
                                            window.location.reload();
                                        }
                                    });
                                });
                            } catch (error) {
                                console.error('SW registration failed: ', error);
                            }
                        });
                    } else {
                        console.log('Service Worker not supported');
                    }

                    // Handle PWA install prompt
                    window.addEventListener('beforeinstallprompt', (e) => {
                        e.preventDefault();
                        deferredPrompt = e;
                        showInstallButton();
                    });

                    // Handle app installed
                    window.addEventListener('appinstalled', (evt) => {
                        console.log('App was installed');
                        isInstalled = true;
                        hideInstallButton();
                    });

                    function showInstallButton() {
                        if (!isInstalled && deferredPrompt) {
                            const installButton = document.getElementById('installBtn');
                            installButton.style.display = 'block';
                        }
                    }

                    function hideInstallButton() {
                        const installButton = document.getElementById('installBtn');
                        installButton.style.display = 'none';
                    }

                    // Install button click handler
                    document.getElementById('installBtn').addEventListener('click', async () => {
                        if (deferredPrompt) {
                            deferredPrompt.prompt();
                            const { outcome } = await deferredPrompt.userChoice;
                            console.log(`User response to the install prompt: ${outcome}`);
                            deferredPrompt = null;
                            hideInstallButton();
                        }
                    });

                    // Handle URL parameters for deep linking
                    function handleUrlParameters() {
                        const urlParams = new URLSearchParams(window.location.search);
                        const url = urlParams.get('url');
                        const title = urlParams.get('title');
                        const text = urlParams.get('text');

                        console.log('URL parameters:', { url, title, text });

                        if (url) {
                            // Pre-fill URL input
                            document.getElementById('inputType').value = 'url';
                            document.getElementById('url').value = url;
                            toggleInputType();
                            
                            // Auto-analyze if it's a news URL
                            if (isNewsUrl(url)) {
                                setTimeout(() => {
                                    console.log('Auto-analyzing shared URL:', url);
                                    document.getElementById('analysisForm').dispatchEvent(new Event('submit'));
                                }, 1000);
                            }
                        } else if (text) {
                            // If text is provided instead of URL, use text input
                            document.getElementById('inputType').value = 'text';
                            document.getElementById('text').value = text;
                            toggleInputType();
                            updateCharCount();
                        }

                        if (title) {
                            document.getElementById('source').value = title;
                        }
                    }

                    function isNewsUrl(url) {
                        const newsDomains = [
                            'kathimerini.gr', 'tovima.gr', 'naftemporiki.gr', 'protothema.gr',
                            'skai.gr', 'ert.gr', 'ant1.gr', 'mega.gr', 'alpha.gr',
                            'news247.gr', 'in.gr', 'lifo.gr', 'efsyn.gr'
                        ];
                        return newsDomains.some(domain => url.includes(domain));
                    }

                    // Handle share target
                    if ('serviceWorker' in navigator && 'navigator' in window) {
                        navigator.serviceWorker.addEventListener('message', (event) => {
                            if (event.data && event.data.type === 'SHARE_TARGET') {
                                const { title, text, url } = event.data.data;
                                if (url) {
                                    document.getElementById('inputType').value = 'url';
                                    document.getElementById('url').value = url;
                                    toggleInputType();
                                }
                                if (title) {
                                    document.getElementById('source').value = title;
                                }
                            }
                        });
                    }

                    // Check for shared data from service worker
                    async function checkSharedData() {
                        if ('caches' in window) {
                            try {
                                const cache = await caches.open('shared-data');
                                const response = await cache.match('shared-data');
                                if (response) {
                                    const data = await response.json();
                                    if (data.url) {
                                        document.getElementById('inputType').value = 'url';
                                        document.getElementById('url').value = data.url;
                                        toggleInputType();
                                    }
                                    if (data.title) {
                                        document.getElementById('source').value = data.title;
                                    }
                                    // Clear the shared data after using it
                                    await cache.delete('shared-data');
                                }
                            } catch (error) {
                                console.log('No shared data found');
                            }
                        }
                    }

                    // Initialize on page load
                    document.addEventListener('DOMContentLoaded', () => {
                        handleUrlParameters();
                        checkSharedData();
                    });

                    function toggleInputType() {
                        const inputType = document.getElementById('inputType').value;
                        const textInput = document.getElementById('textInput');
                        const urlInput = document.getElementById('urlInput');
                        
                        if (inputType === 'text') {
                            textInput.style.display = 'block';
                            urlInput.style.display = 'none';
                        } else {
                            textInput.style.display = 'none';
                            urlInput.style.display = 'block';
                        }
                    }
                    
                    function colorizeGrade() {
                        const el = document.getElementById('analysis');
                        if (!el) return;
                        let html = el.innerHTML;
                        let gradeCls = '';
                        html = html.replace(/(ΣΥΝΟΛΙΚΗ ΑΞΙΟΛΟΓΗΣΗ:\s*)(\d{1,3})/, (match, prefix, grade) => {
                            const num = parseInt(grade, 10);
                            let cls;
                            if (num >= 81) { cls = 'grade-excellent'; gradeCls = 'card-grade-excellent'; }
                            else if (num >= 61) { cls = 'grade-high'; gradeCls = 'card-grade-high'; }
                            else if (num >= 31) { cls = 'grade-medium'; gradeCls = 'card-grade-medium'; }
                            else { cls = 'grade-low'; gradeCls = 'card-grade-low'; }
                            return prefix + '<span class="' + cls + '">' + grade + '</span>';
                        });
                        el.innerHTML = html;
                        const card = document.getElementById('result');
                        if (card && gradeCls) {
                            card.className = card.className.replace(/card-grade-\S+/g, '').trim() + ' ' + gradeCls;
                        }
                    }
                    
                    function updateCharCount() {
                        const textarea = document.getElementById('text');
                        const charCount = document.getElementById('charCount');
                        const count = textarea.value.length;
                        charCount.textContent = count + ' / 10,000 χαρακτήρες (ελάχιστο 50)';

                        if (count < 50) {
                            charCount.style.color = '#dc3545';
                        } else if (count > 9000) {
                            charCount.style.color = '#ffc107';
                        } else {
                            charCount.style.color = '#28a745';
                        }
                    }

                    function convertMarkdownToHTML(markdown) {
                        // Use marked.js library to convert markdown to HTML
                        try {
                            if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
                                return marked.parse(markdown);
                            } else if (typeof marked !== 'undefined' && typeof marked === 'function') {
                                // Fallback for older marked versions
                                return marked(markdown);
                            } else {
                                console.error('Marked library not loaded');
                                return '<pre>' + markdown + '</pre>';
                            }
                        } catch (e) {
                            console.error('Error parsing markdown:', e);
                            return '<pre>' + markdown + '</pre>';
                        }
                    }
                    
                    document.getElementById('analysisForm').addEventListener('submit', async function(e) {
                        e.preventDefault();
                        
                        const inputType = document.getElementById('inputType').value;
                        const text = document.getElementById('text').value;
                        const url = document.getElementById('url').value;
                        const source = document.getElementById('source').value;
                        
                        if (inputType === 'text' && !text.trim()) {
                            alert('Παρακαλώ εισάγετε κείμενο άρθρου');
                            return;
                        }
                        
                        if (inputType === 'text' && text.length < 50) {
                            alert('Το κείμενο πρέπει να έχει τουλάχιστον 50 χαρακτήρες');
                            return;
                        }
                        
                        if (inputType === 'url' && !url.trim()) {
                            alert('Παρακαλώ εισάγετε URL άρθρου');
                            return;
                        }
                        
                        // Show loading
                        document.getElementById('loading').style.display = 'block';
                        document.getElementById('result').style.display = 'none';
                        document.getElementById('analyzeBtn').disabled = true;
                        
                        try {
                            const response = await fetch('/analyze', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ 
                                    text: inputType === 'text' ? text : '', 
                                    url: inputType === 'url' ? url : '',
                                    source: source 
                                })
                            });
                            
                            const data = await response.json();
                            
                            if (data.error) {
                                document.getElementById('analysis').innerHTML = '<div class="error">Σφάλμα: ' + data.error + '</div>';
                            } else {
                                // Convert markdown to HTML for display
                                const htmlContent = convertMarkdownToHTML(data.analysis);
                                document.getElementById('analysis').innerHTML = htmlContent;
                                colorizeGrade();
                            }
                            
                            document.getElementById('result').style.display = 'block';
                        } catch (error) {
                            document.getElementById('analysis').innerHTML = '<div class="error">Σφάλμα: ' + error.message + '</div>';
                            document.getElementById('result').style.display = 'block';
                        } finally {
                            document.getElementById('loading').style.display = 'none';
                            document.getElementById('analyzeBtn').disabled = false;
                        }
                    });
                </script>
                <div class="text-center py-3 mt-4" style="border-top: 1px solid #dee2e6; font-size: 0.8rem; color: #6c757d;">
                    <a href="/privacy" style="color: #6c757d; text-decoration: none;">Πολιτική Απορρήτου</a>
                </div>
            </body>
            </html>
            """
        return html
    
    def get_about_html(self):
        """Generate the About page HTML"""
        html = """
        <!DOCTYPE html>
        <html lang="el">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
            <title>Σχετικά - ΕΠΑΠ</title>
            
            <!-- PWA Meta Tags -->
            <meta name="description" content="Σχετικά με την πλατφόρμα ανάλυσης παραπληροφόρισης">
            <meta name="keywords" content="ανάλυση ειδήσεων, ελληνικές ειδήσεις, προπαγάνδα, ανίχνευση προπαγάνδας, ανάλυση προκατάληψης, ελληνική ενημέρωση, αξιοπιστία ειδήσεων, fake news, παραπληροφόρηση, ανάλυση μέσων ενημέρωσης">
            <meta name="theme-color" content="#1e3c72">
            <meta name="apple-mobile-web-app-capable" content="yes">
            <meta name="apple-mobile-web-app-status-bar-style" content="default">
            <meta name="apple-mobile-web-app-title" content="ΕΠΑΠ">
            <meta name="mobile-web-app-capable" content="yes">
            <meta name="application-name" content="ΕΠΑΠ">
            
            <!-- PWA Manifest -->
            <link rel="manifest" href="/static/manifest.json">
            
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9549967181261078" crossorigin="anonymous"></script>
            
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            
            <!-- Icons for different platforms -->
            <link rel="icon" type="image/png" sizes="32x32" href="/static/icons/icon-32x32.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/static/icons/icon-16x16.png">
            <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
            
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                    max-width: 860px;
                    margin: 0 auto;
                    padding: 10px;
                    background: linear-gradient(135deg, #e8edf5 0%, #d5dce8 100%);
                    min-height: 100vh;
                    -webkit-font-smoothing: antialiased;
                }
                .container {
                    background: #fff;
                    padding: 24px;
                    border-radius: 12px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
                }
                .header {
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 16px 20px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 24px;
                }
                .header h1 { margin: 0; font-size: 1.4rem; }
                .header p { margin: 4px 0 0; font-size: 0.9rem; opacity: 0.85; }
                .content { line-height: 1.7; color: #333; font-size: 0.95rem; }
                .content h2 {
                    color: #1e3c72;
                    margin-top: 1.5rem;
                    margin-bottom: 0.75rem;
                    font-size: 1.2rem;
                    border-bottom: 1px solid #e9ecef;
                    padding-bottom: 0.35rem;
                }
                .content p { margin-bottom: 0.85rem; }
                .author-card {
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 1.5rem 0;
                    text-align: center;
                }
                .author-avatar {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    margin: 0 auto 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    color: white;
                    font-weight: bold;
                }
                .author-name { font-size: 1.15rem; font-weight: 600; color: #1e3c72; margin-bottom: 4px; }
                .author-title { color: #6c757d; margin-bottom: 12px; font-style: italic; font-size: 0.9rem; }
                .author-card p { font-size: 0.9rem; color: #495057; }
                .github-link {
                    display: inline-block;
                    background: #24292e;
                    color: white;
                    padding: 8px 18px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 500;
                    font-size: 0.9rem;
                    transition: all 0.2s;
                    margin: 4px;
                }
                .github-link:hover { background: #0366d6; }
                .back-button {
                    display: inline-block;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 10px 22px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 500;
                    font-size: 0.95rem;
                    transition: all 0.2s;
                    margin-top: 16px;
                }
                .back-button:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
                .feature-list { list-style: none; padding: 0; }
                .feature-list li {
                    background: #f8f9fa;
                    margin: 6px 0;
                    padding: 10px 16px;
                    border-radius: 8px;
                    border-left: 3px solid #2a5298;
                    font-size: 0.9rem;
                }
                .tech-stack { display: flex; flex-wrap: wrap; gap: 8px; margin: 0.75rem 0; }
                .tech-badge {
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 4px 12px;
                    border-radius: 6px;
                    font-size: 0.8rem;
                    font-weight: 500;
                }
                @media (max-width: 768px) {
                    body { padding: 6px; }
                    .container { padding: 16px; border-radius: 10px; margin: 4px; }
                    .header { padding: 12px; border-radius: 8px; margin-bottom: 16px; }
                    .header h1 { font-size: 1.2rem; }
                    .author-card { padding: 16px; margin: 1rem 0; }
                    .tech-stack { justify-content: center; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><span class="logo-alpha">Α<span class="check">✓</span></span>Σχετικά με την Εφαρμογή</h1>
                    <p>ΕΠΑΠ - Εληνική Πλατφόρμα Ανάλυσης Παραπληροφόρισης</p>
                </div>
                
                <div class="content">
                    <h2><i class="fas fa-bullseye me-2"></i>Σκοπός της Εφαρμογής</h2>
                    <p>Η εφαρμογή "ΕΠΑΠ" δημιουργήθηκε με στόχο την προστασία των πολιτών από την προπαγάνδα και την παραπληροφόρηση. Χρησιμοποιώντας την τεχνητή νοημοσύνη Google Gemini, η εφαρμογή αναλύει ελληνικά άρθρα ειδήσεων και εντοπίζει στοιχεία προπαγάνδας, προκατάληψης και χειραγώγησης.</p>
                    
                    <h2><i class="fas fa-search me-2"></i>Χαρακτηριστικά Ανάλυσης</h2>
                    <ul class="feature-list">
                        <li><strong>Εντοπισμός Συναισθηματικής Χειραγώγησης:</strong> Αναγνώριση φορτωμένων όρων και συναισθηματικών τριγέρων</li>
                        <li><strong>Αξιολόγηση Προκατάληψης:</strong> Εντοπισμός πολιτικών και ιδεολογικών κλίσεων</li>
                        <li><strong>Ανάλυση Γεγονός vs Άποψη:</strong> Ισορροπία μεταξύ πραγματικών γεγονότων και σχολιασμού</li>
                        <li><strong>Αξιοπιστία Πηγής:</strong> Αξιολόγηση της αξιοπιστίας της πηγής ειδήσεων</li>
                        <li><strong>Τεχνικές Προπαγάνδας:</strong> Εντοπισμός τεχνικών προπαγάνδας και λογικών σφαλμάτων</li>
                        <li><strong>Σύστημα Βαθμολόγησης:</strong> Βαθμολόγηση 1-100 για την αξιοπιστία των ειδήσεων</li>
                    </ul>
                    
                    <h2><i class="fas fa-code me-2"></i>Τεχνολογίες</h2>
                    <div class="tech-stack">
                        <span class="tech-badge">Python 3.8+</span>
                        <span class="tech-badge">Google Gemini AI</span>
                        <span class="tech-badge">Vercel Serverless</span>
                        <span class="tech-badge">PWA (Progressive Web App)</span>
                        <span class="tech-badge">BeautifulSoup</span>
                        <span class="tech-badge">Markdown</span>
                        <span class="tech-badge">Mobile-First Design</span>
                    </div>
                    
                    <h2><i class="fas fa-mobile-alt me-2"></i>Mobile & PWA Features</h2>
                    <p>Η εφαρμογή είναι σχεδιασμένη mobile-first και υποστηρίζει:</p>
                    <ul class="feature-list">
                        <li><strong>Εγκατάσταση σε Mobile:</strong> Προσθήκη στην αρχική οθόνη του κινητού</li>
                        <li><strong>Share Target:</strong> Λήψη και ανάλυση συνδέσμων που μοιράζονται από άλλες εφαρμογές</li>
                        <li><strong>Offline Support:</strong> Λειτουργία offline με service worker</li>
                        <li><strong>Responsive Design:</strong> Βέλτιστη εμπειρία σε όλες τις συσκευές</li>
                    </ul>
                    
                    <div class="author-card">
                        <div class="author-avatar">NT</div>
                        <div class="author-name">Nicolai Tufar</div>
                        <div class="author-title">Developer & Creator</div>
                        <p>Αυτή η εφαρμογή δημιουργήθηκε με αγάπη για την ελληνική κοινότητα και την προστασία της από την παραπληροφόρηση. Στόχος είναι η παροχή ενός εργαλείου που θα βοηθήσει τους πολίτες να κάνουν πιο ενημερωμένες επιλογές.</p>
                        <a href="https://github.com/ntufar" target="_blank" class="github-link">
                            <i class="fab fa-github me-1"></i>GitHub Profile
                        </a>
                    </div>
                    
                    <div class="author-card" style="background: #e8f4fd; border-color: #bee5eb;">
                        <div class="author-avatar" style="background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);">NT</div>
                        <div class="author-name">Νίκος Τσολοζίδης</div>
                        <div class="author-title">Ιδέα & Έμπνευση</div>
                        <p>Η ιδέα για αυτή την εφαρμογή ανήκει στον Νίκο Τσολοζίδη, ο οποίος πρότεινε την ανάπτυξη ενός εργαλείου ανάλυσης ελληνικών ειδήσεων.</p>
                        <a href="https://www.facebook.com/tsolozidis.nick" target="_blank" class="github-link" style="background: #1877f2;">
                            <i class="fab fa-facebook me-1"></i>Facebook Profile
                        </a>
                    </div>
                    
                    <h2><i class="fas fa-hands-helping me-2"></i>Συνεισφορά</h2>
                    <p>Αν θέλετε να συμβάλετε στην ανάπτυξη της εφαρμογής, μπορείτε να:</p>
                    <ul class="feature-list">
                        <li>Αναφέρετε bugs ή προτάσεις βελτίωσης</li>
                        <li>Συμβάλετε στον κώδικα μέσω Pull Requests</li>
                        <li>Μοιραστείτε την εφαρμογή με φίλους και οικογένεια</li>
                        <li>Προτείνετε νέες λειτουργίες ανάλυσης</li>
                    </ul>
                    
                    <div style="background: #e8f0fe; border-left: 4px solid #2196f3; padding: 16px 20px; margin: 20px 0; border-radius: 10px;">
                        <h3 style="color: #1565c0; font-size: 1rem; margin-bottom: 0.5rem;"><i class="fas fa-star me-1"></i>Από πού Ξεκίνησε η Ιδέα</h3>
                        <p style="font-size: 0.9rem; line-height: 1.6; color: #424242; margin-bottom: 0.5rem;">
                            Σε μια εποχή όπου η παραπληροφόρηση διαδίδεται γρήγορα, η ανάγκη για εργαλεία κριτικής αξιολόγησης είναι πιο σημαντική από ποτέ.
                        </p>
                        <p style="font-size: 0.9rem; line-height: 1.6; color: #424242; margin-bottom: 0;">
                            Χρησιμοποιώντας την τεχνητή νοημοσύνη, παρέχουμε αντικειμενική ανάλυση που βοηθά τους χρήστες να κάνουν πιο ενημερωμένες αποφάσεις.
                        </p>
                    </div>
                    
                    <!-- Ad Unit on About Page -->
                    <div style="text-align: center; margin: 20px 0;">
                        <ins class="adsbygoogle"
                             style="display:block"
                             data-ad-client="ca-pub-9549967181261078"
                             data-ad-slot="5866895841"
                             data-ad-format="auto"
                             data-full-width-responsive="true"></ins>
                        <script>
                             (adsbygoogle = window.adsbygoogle || []).push({});
                        </script>
                    </div>
                    
                    <h2><i class="fas fa-file-alt me-2"></i>Άδεια Χρήσης</h2>
                    <p>Αυτό το έργο είναι διαθέσιμο υπό την άδεια MIT. Μπορείτε να το χρησιμοποιήσετε, να το τροποποιήσετε και να το διανείμετε ελεύθερα.</p>
                    
                    <div style="text-align: center; margin-top: 2rem;">
                        <a href="/" class="back-button"><i class="fas fa-arrow-left me-1"></i>Επιστροφή στην Αρχική</a>
                    </div>
                    <div class="text-center mt-4" style="padding-top: 1rem; border-top: 1px solid #e9ecef; font-size: 0.8rem; color: #6c757d;">
                        <a href="/privacy" style="color: #6c757d; text-decoration: none;">Πολιτική Απορρήτου</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    

    def get_privacy_html(self):
        """Generate the Privacy Policy page HTML"""
        html = """
        <!DOCTYPE html>
        <html lang="el">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
            <title>Πολιτική Απορρήτου - ΕΠΑΠ</title>
            
            <meta name="description" content="Πολιτική απορρήτου της ΕΠΑΠ - Ελληνική Πλατφόρμα Ανάλυσης Παραπληροφόρησης">
            <meta name="theme-color" content="#1e3c72">
            <meta name="apple-mobile-web-app-capable" content="yes">
            <meta name="apple-mobile-web-app-status-bar-style" content="default">
            <meta name="apple-mobile-web-app-title" content="ΕΠΑΠ">
            <meta name="mobile-web-app-capable" content="yes">
            <meta name="application-name" content="ΕΠΑΠ">
            
            <link rel="manifest" href="/static/manifest.json">
            
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9549967181261078" crossorigin="anonymous"></script>
            
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            
            <link rel="icon" type="image/png" sizes="32x32" href="/static/icons/icon-32x32.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/static/icons/icon-16x16.png">
            <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
            
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                    max-width: 860px;
                    margin: 0 auto;
                    padding: 10px;
                    background: linear-gradient(135deg, #e8edf5 0%, #d5dce8 100%);
                    min-height: 100vh;
                    -webkit-font-smoothing: antialiased;
                }
                .container {
                    background: #fff;
                    padding: 24px;
                    border-radius: 12px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
                }
                .header {
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 16px 20px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 24px;
                }
                .header h1 { margin: 0; font-size: 1.4rem; }
                .header p { margin: 4px 0 0; font-size: 0.9rem; opacity: 0.85; }
                .content { line-height: 1.7; color: #333; font-size: 0.95rem; }
                .content h2 {
                    color: #1e3c72;
                    margin-top: 1.5rem;
                    margin-bottom: 0.75rem;
                    font-size: 1.2rem;
                    border-bottom: 1px solid #e9ecef;
                    padding-bottom: 0.35rem;
                }
                .content h3 {
                    color: #2a5298;
                    margin-top: 1.2rem;
                    margin-bottom: 0.5rem;
                    font-size: 1.05rem;
                }
                .content p { margin-bottom: 0.85rem; }
                .content ul { margin-bottom: 0.85rem; padding-left: 1.5rem; }
                .content li { margin-bottom: 0.5rem; }
                .back-button {
                    display: inline-block;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 10px 22px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 500;
                    font-size: 0.95rem;
                    transition: all 0.2s;
                    margin-top: 16px;
                }
                .back-button:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
                .last-updated {
                    font-size: 0.85rem;
                    color: #6c757d;
                    text-align: center;
                    margin-top: 1.5rem;
                    padding-top: 1rem;
                    border-top: 1px solid #e9ecef;
                }
                .info-box {
                    background: #e8f0fe;
                    border-left: 4px solid #2196f3;
                    padding: 14px 18px;
                    margin: 1rem 0;
                    border-radius: 8px;
                    font-size: 0.9rem;
                }
                @media (max-width: 768px) {
                    body { padding: 6px; }
                    .container { padding: 16px; border-radius: 10px; margin: 4px; }
                    .header { padding: 12px; border-radius: 8px; margin-bottom: 16px; }
                    .header h1 { font-size: 1.2rem; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><span class="logo-alpha">Ε<span class="check">✓</span></span>Πολιτική Απορρήτου</h1>
                    <p>ΕΠΑΠ - Εληνική Πλατφόρμα Ανάλυσης Παραπληροφόρισης</p>
                </div>
                
                <div class="content">
                    <p><strong>Τελευταία ενημέρωση:</strong> 31 Μαΐου 2026</p>

                    <h2>1. Εισαγωγή</h2>
                    <p>Η ΕΠΑΠ (Ελληνική Πλατφόρμα Ανάλυσης Παραπληροφόρησης) δεσμεύεται για την προστασία του απορρήτου σας. Αυτή η Πολιτική Απορρήτου εξηγεί πώς συλλέγουμε, χρησιμοποιούμε και προστατεύουμε τα δεδομένα σας όταν χρησιμοποιείτε την εφαρμογή μας.</p>
                    <p>Χρησιμοποιώντας την εφαρμογή μας, συμφωνείτε με τις πρακτικές που περιγράφονται στην παρούσα πολιτική.</p>

                    <h2>2. Δεδομένα που Συλλέγουμε</h2>
                    
                    <h3>2.1 Δεδομένα που Παρέχετε Εσείς</h3>
                    <ul>
                        <li><strong>Κείμενο άρθρων:</strong> Το κείμενο ή η διεύθυνση URL που εισάγετε για ανάλυση.</li>
                        <li><strong>Πηγή ειδήσεων:</strong> Το όνομα του ειδησεογραφικού μέσου που αναφέρετε προαιρετικά.</li>
                    </ul>

                    <h3>2.2 Δεδομένα που Συλλέγονται Αυτόματα</h3>
                    <ul>
                        <li><strong>Διεύθυνση IP:</strong> Η διεύθυνση IP σας καταγράφεται προσωρινά για σκοπούς περιορισμού ρυθμού αιτήσεων (rate limiting) και ασφάλειας. Δεν αποθηκεύεται μόνιμα.</li>
                        <li><strong>Δεδομένα χρήσης:</strong> Συλλέγονται ανώνυμα στατιστικά χρήσης μέσω της υπηρεσίας Google AdSense.</li>
                    </ul>

                    <h3>2.3 Δεδομένα Τρίτων</h3>
                    <ul>
                        <li><strong>Google AdSense:</strong> Χρησιμοποιούμε το Google AdSense για την προβολή διαφημίσεων.</li>
                        <li><strong>Mistral AI:</strong> Τα κείμενα που υποβάλλετε αποστέλλονται στο Mistral AI API για επεξεργασία.</li>
                    </ul>

                    <h2>3. Πώς Χρησιμοποιούμε τα Δεδομένα σας</h2>
                    <p>Χρησιμοποιούμε τα δεδομένα σας αποκλειστικά για:</p>
                    <ul>
                        <li>Την ανάλυση άρθρων ειδήσεων για εντοπισμό προπαγάνδας</li>
                        <li>Τη βελτίωση της ποιότητας των υπηρεσιών μας</li>
                        <li>Την προστασία από κακόβουλη χρήση</li>
                        <li>Την προβολή σχετικών διαφημίσεων</li>
                    </ul>

                    <div class="info-box">
                        <strong>Σημείωση:</strong> Δεν πωλούμε, δεν ενοικιάζουμε και δεν μοιραζόμαστε τα προσωπικά σας δεδομένα με τρίτους για σκοπούς μάρκετινγκ.
                    </div>

                    <h2>4. Διατήρηση Δεδομένων</h2>
                    <p>Τα κείμενα που υποβάλλετε αποθηκεύονται προσωρινά στη μνήμη του διακομιστή για λόγους προσωρινής αποθήκευσης (caching) και διαγράφονται αυτόματα όταν γίνει επανεκκίνηση του διακομιστή. Δεν διατηρούμε μόνιμη βάση δεδομένων.</p>

                    <h2>5. Ασφάλεια Δεδομένων</h2>
                    <p>Λαμβάνουμε εύλογα μέτρα ασφαλείας για την προστασία των δεδομένων σας. Η επικοινωνία με τον διακομιστή γίνεται μέσω κρυπτογραφημένης σύνδεσης HTTPS.</p>

                    <h2>6. Δικαιώματά σας</h2>
                    <p>Σύμφωνα με τον GDPR, έχετε τα ακόλουθα δικαιώματα:</p>
                    <ul>
                        <li><strong>Δικαίωμα πρόσβασης:</strong> Να ζητήσετε αντίγραφο των δεδομένων σας</li>
                        <li><strong>Δικαίωμα διαγραφής:</strong> Να ζητήσετε τη διαγραφή των δεδομένων σας</li>
                        <li><strong>Δικαίωμα περιορισμού:</strong> Να περιορίσετε την επεξεργασία</li>
                        <li><strong>Δικαίωμα εναντίωσης:</strong> Να εναντιωθείτε στην επεξεργασία</li>
                        <li><strong>Δικαίωμα φορητότητας:</strong> Να λάβετε τα δεδομένα σας σε δομημένη μορφή</li>
                    </ul>

                    <h2>7. Παιδιά</h2>
                    <p>Η εφαρμογή μας δεν απευθύνεται σε παιδιά κάτω των 13 ετών.</p>

                    <h2>8. Σύνδεσμοι προς Τρίτους</h2>
                    <p>Η εφαρμογή μας ενδέχεται να περιέχει συνδέσμους προς ιστότοπους τρίτων. Δεν ευθυνόμαστε για τις πρακτικές απορρήτου αυτών των ιστότοπων.</p>

                    <h2>9. Αλλαγές στην Πολιτική Απορρήτου</h2>
                    <p>Ενδέχεται να ενημερώνουμε αυτήν την πολιτική από καιρό σε καιρό. Οι αλλαγές θα δημοσιεύονται σε αυτήν τη σελίδα.</p>

                    <h2>10. Επικοινωνία</h2>
                    <ul>
                        <li><strong>Email:</strong> <a href="mailto:ntufar@gmail.com">ntufar@gmail.com</a></li>
                        <li><strong>GitHub:</strong> <a href="https://github.com/ntufar/epap" target="_blank">https://github.com/ntufar/epap</a></li>
                    </ul>

                    <div class="last-updated">
                        Τελευταία ενημέρωση: 31 Μαΐου 2026
                    </div>

                    <div style="text-align: center; margin-top: 2rem;">
                        <a href="/" class="back-button">Επιστροφή στην Αρχική</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self.get_main_html()
            self.wfile.write(html.encode())
            
        elif self.path.startswith('/?') or (self.path != '/' and '?' in self.path):
            # Handle main page with potential URL parameters for sharing
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Check for URL parameters (for shared links)
            url_params = {}
            if '?' in self.path:
                from urllib.parse import parse_qs, urlparse
                parsed_url = urlparse(self.path)
                url_params = parse_qs(parsed_url.query)
            
            # Generate the same HTML as the main route
            html = self.get_main_html(url_params)
            self.wfile.write(html.encode())
            
        elif self.path == '/about':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self.get_about_html()
            self.wfile.write(html.encode())
            
        elif self.path == '/privacy':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self.get_privacy_html()
            self.wfile.write(html.encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'message': 'ΕΠΑΠ is running'
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/static/manifest.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                with open('static/manifest.json', 'r', encoding='utf-8') as f:
                    manifest_content = f.read()
                self.wfile.write(manifest_content.encode())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Manifest not found')
                
        elif self.path == '/static/sw.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Service-Worker-Allowed', '/')
            self.end_headers()
            
            try:
                with open('static/sw.js', 'r', encoding='utf-8') as f:
                    sw_content = f.read()
                self.wfile.write(sw_content.encode())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Service worker not found')
        elif self.path in ['/ads.txt', '/Ads.txt']:
            # Serve IAB ads.txt/Ads.txt from ads.txt file
            # Try multiple locations for compatibility
            candidate_paths = [
                os.path.join('static', 'ads.txt'),              # project root static lowercase
                os.path.join(os.path.dirname(__file__), 'static', 'ads.txt'),  # api/static lowercase
                os.path.join('static', 'Ads.txt'),              # fallback: capitalized
                os.path.join(os.path.dirname(__file__), 'static', 'Ads.txt')   # fallback: api/static capitalized
            ]
            file_found = False
            for file_path in candidate_paths:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.send_header('Cache-Control', 'public, max-age=3600')
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
                    file_found = True
                    break
                except FileNotFoundError:
                    continue
            if not file_found:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'ads.txt not found')
                
        elif self.path in ['/robots.txt', '/Robots.txt']:
            # Serve robots.txt
            candidate_paths = [
                os.path.join('static', 'robots.txt'),
                os.path.join(os.path.dirname(__file__), 'static', 'robots.txt'),
                os.path.join('static', 'Robots.txt'),
                os.path.join(os.path.dirname(__file__), 'static', 'Robots.txt')
            ]
            file_found = False
            for file_path in candidate_paths:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
                    file_found = True
                    break
                except FileNotFoundError:
                    continue
            if not file_found:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'robots.txt not found')

        elif self.path in ['/sitemap.xml', '/Sitemap.xml']:
            # Serve sitemap.xml
            candidate_paths = [
                os.path.join('static', 'sitemap.xml'),
                os.path.join(os.path.dirname(__file__), 'static', 'sitemap.xml'),
                os.path.join('static', 'Sitemap.xml'),
                os.path.join(os.path.dirname(__file__), 'static', 'Sitemap.xml')
            ]
            file_found = False
            for file_path in candidate_paths:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-type', 'application/xml; charset=utf-8')
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
                    file_found = True
                    break
                except FileNotFoundError:
                    continue
            if not file_found:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'sitemap.xml not found')

        elif self.path.startswith('/static/icons/'):
            # Handle icon requests
            icon_name = self.path.split('/')[-1]
            icon_path = f'static/icons/{icon_name}'
            
            try:
                with open(icon_path, 'rb') as f:
                    icon_content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header('Cache-Control', 'public, max-age=31536000')
                self.end_headers()
                self.wfile.write(icon_content)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Icon not found')
        elif re.match(r'^/google[a-z0-9]+\.html$', self.path):
            # Serve Google Search Console verification files placed under api/static/
            filename = self.path.lstrip('/')
            file_path = os.path.join('static', filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Verification file not found')
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        if self.path == '/analyze':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                text = data.get('text', '').strip()
                url = data.get('url', '').strip()
                source = data.get('source', '').strip()
                
                # Validate input
                if not text and not url:
                    error_response = {
                        'error': 'Παρακαλώ εισάγετε κείμενο ή URL',
                        'success': False
                    }
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(error_response).encode())
                    return
                
                # Extract text from URL if provided
                if url and not text:
                    if not url.startswith(('http://', 'https://')):
                        error_response = {
                            'error': 'Μη έγκυρη διεύθυνση URL',
                            'success': False
                        }
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(error_response).encode())
                        return
                    
                    text = extract_text_from_url(url)
                    if text.startswith("Error"):
                        error_response = {
                            'error': text,
                            'success': False
                        }
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(error_response).encode())
                        return
                
                # Check minimum text length
                if len(text) < 50:
                    error_response = {
                        'error': 'Το κείμενο είναι πολύ σύντομο για ανάλυση (ελάχιστο 50 χαρακτήρες)',
                        'success': False
                    }
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(error_response).encode())
                    return
                
                # Check maximum text length
                if len(text) > 10000:
                    error_response = {
                        'error': 'Το κείμενο είναι πολύ μεγάλο (μέγιστο 10,000 χαρακτήρες)',
                        'success': False
                    }
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(error_response).encode())
                    return
                
                # Perform analysis using Mistral AI
                analysis = analyze_greek_news(text, source)
                
                response = {
                    'analysis': analysis,
                    'text_length': len(text),
                    'source': source if source else 'Άγνωστη',
                    'success': True
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                error_response = {
                    'error': f'Σφάλμα: {str(e)}',
                    'success': False
                }
                
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')