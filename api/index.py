from http.server import BaseHTTPRequestHandler
import json
import os
import re
import hashlib
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import markdown

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# Simple in-memory cache for analysis results
analysis_cache = {}

def get_cache_key(text, source=""):
    """Generate a cache key for the analysis"""
    content = f"{text[:1000]}_{source}".encode('utf-8')
    return hashlib.md5(content).hexdigest()

def markdown_to_html(markdown_text):
    """Convert markdown text to HTML with proper styling"""
    # Configure markdown with extensions for better formatting
    md = markdown.Markdown(extensions=['extra', 'nl2br', 'sane_lists'])
    html = md.convert(markdown_text)
    
    # Add some custom styling for better presentation
    styled_html = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
        {html}
    </div>
    """
    
    return styled_html

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
    """Analyze Greek news text for propaganda indicators using Gemini"""
    try:
        # Check cache first
        cache_key = get_cache_key(text, source)
        if cache_key in analysis_cache:
            return analysis_cache[cache_key]
        
        prompt = f"""
        Αναλύστε αυτό το ελληνικό άρθρο για πιθανά στοιχεία προπαγάνδας και προκατάληψης:

        Κείμενο: {text[:2000]}
        Πηγή: {source if source else "Άγνωστη"}

        Παρακαλώ αξιολογήστε από 1-10 (1=πιθανή προπαγάνδα, 10=αξιόπισες ειδήσεις) και δώστε λεπτομερή ανάλυση:

        **ΣΥΝΟΛΙΚΗ ΑΞΙΟΛΟΓΗΣΗ: [Βαθμολογία 1-10]**

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

        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Convert markdown to HTML
        html_analysis = markdown_to_html(response.text)
        
        # Cache the result
        analysis_cache[cache_key] = html_analysis
        return html_analysis
        
    except Exception as e:
        return f"Σφάλμα στην ανάλυση: {str(e)}"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html lang="el">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
                <title>Ανάλυση Ελληνικών Ειδήσεων</title>
                
                <!-- PWA Meta Tags -->
                <meta name="description" content="Αναλύστε ελληνικά άρθρα ειδήσεων για στοιχεία προπαγάνδας και προκατάληψης">
                <meta name="theme-color" content="#667eea">
                <meta name="apple-mobile-web-app-capable" content="yes">
                <meta name="apple-mobile-web-app-status-bar-style" content="default">
                <meta name="apple-mobile-web-app-title" content="Greek News Analyzer">
                <meta name="mobile-web-app-capable" content="yes">
                <meta name="application-name" content="Greek News Analyzer">
                <meta name="apple-touch-fullscreen" content="yes">
                
                <!-- PWA Manifest -->
                <link rel="manifest" href="/static/manifest.json">
                
                <!-- Icons for different platforms -->
                <link rel="icon" type="image/png" sizes="32x32" href="/static/icons/icon-32x32.png">
                <link rel="icon" type="image/png" sizes="16x16" href="/static/icons/icon-16x16.png">
                <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
                <link rel="apple-touch-icon" sizes="152x152" href="/static/icons/icon-152x152.png">
                <link rel="apple-touch-icon" sizes="180x180" href="/static/icons/icon-192x192.png">
                <style>
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        max-width: 900px; 
                        margin: 0 auto; 
                        padding: 10px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        -webkit-font-smoothing: antialiased;
                        -moz-osx-font-smoothing: grayscale;
                    }
                    .container { 
                        background: rgba(255, 255, 255, 0.95); 
                        padding: 30px; 
                        border-radius: 20px; 
                        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                        backdrop-filter: blur(10px);
                    }
                    .header {
                        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 15px;
                        text-align: center;
                        margin-bottom: 30px;
                    }
                    .input-group {
                        margin-bottom: 20px;
                    }
                    label {
                        display: block;
                        margin-bottom: 8px;
                        font-weight: 600;
                        color: #333;
                    }
                    input, textarea, select {
                        width: 100%;
                        padding: 12px;
                        border: 2px solid #e9ecef;
                        border-radius: 10px;
                        font-size: 16px;
                        transition: border-color 0.3s ease;
                        box-sizing: border-box;
                    }
                    input:focus, textarea:focus, select:focus {
                        outline: none;
                        border-color: #667eea;
                        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                    }
                    textarea {
                        height: 200px;
                        resize: vertical;
                    }
                    button {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 15px 30px;
                        border: none;
                        border-radius: 25px;
                        cursor: pointer;
                        font-size: 16px;
                        font-weight: 600;
                        transition: all 0.3s ease;
                        width: 100%;
                        margin-top: 10px;
                    }
                    button:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
                    }
                    button:disabled {
                        opacity: 0.6;
                        cursor: not-allowed;
                        transform: none;
                    }
                    .result {
                        margin-top: 30px;
                        padding: 20px;
                        background: #f8f9fa;
                        border-radius: 15px;
                        border-left: 5px solid #007bff;
                    }
                    .loading {
                        text-align: center;
                        padding: 20px;
                        display: none;
                    }
                    .spinner {
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #667eea;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 10px;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    .analysis-text {
                        line-height: 1.6;
                        font-size: 14px;
                    }
                    .analysis-text h1, .analysis-text h2, .analysis-text h3, .analysis-text h4, .analysis-text h5, .analysis-text h6 {
                        color: #1e3c72;
                        margin-top: 1.5rem;
                        margin-bottom: 0.5rem;
                        font-weight: 600;
                    }
                    .analysis-text h2 {
                        font-size: 1.3rem;
                        border-bottom: 2px solid #e9ecef;
                        padding-bottom: 0.3rem;
                    }
                    .analysis-text h3 {
                        font-size: 1.1rem;
                        color: #495057;
                    }
                    .analysis-text ul, .analysis-text ol {
                        padding-left: 1.5rem;
                        margin-bottom: 1rem;
                    }
                    .analysis-text li {
                        margin-bottom: 0.5rem;
                    }
                    .analysis-text strong {
                        color: #1e3c72;
                        font-weight: 600;
                    }
                    .analysis-text p {
                        margin-bottom: 1rem;
                    }
                    .analysis-text blockquote {
                        border-left: 4px solid #007bff;
                        padding-left: 1rem;
                        margin: 1rem 0;
                        font-style: italic;
                        color: #6c757d;
                    }
                    .char-count {
                        font-size: 12px;
                        color: #666;
                        text-align: right;
                        margin-top: 5px;
                    }
                    .error {
                        color: #dc3545;
                        background: #f8d7da;
                        padding: 10px;
                        border-radius: 5px;
                        margin: 10px 0;
                    }
                    
                    /* Mobile-specific styles */
                    @media (max-width: 768px) {
                        body {
                            padding: 5px;
                        }
                        .container {
                            padding: 20px;
                            border-radius: 15px;
                            margin: 5px;
                        }
                        .header {
                            padding: 15px;
                            border-radius: 10px;
                            margin-bottom: 20px;
                        }
                        .header h1 {
                            font-size: 1.5rem;
                            margin-bottom: 10px;
                        }
                        .header p {
                            font-size: 0.9rem;
                        }
                        input, textarea, select {
                            font-size: 16px; /* Prevents zoom on iOS */
                            padding: 15px;
                        }
                        textarea {
                            height: 150px;
                        }
                        button {
                            padding: 18px 30px;
                            font-size: 18px;
                            margin-top: 15px;
                        }
                        .analysis-text {
                            font-size: 16px;
                        }
                        .analysis-text h2 {
                            font-size: 1.2rem;
                        }
                        .analysis-text h3 {
                            font-size: 1.1rem;
                        }
                    }
                    
                    @media (max-width: 480px) {
                        .container {
                            padding: 15px;
                            margin: 2px;
                        }
                        .header h1 {
                            font-size: 1.3rem;
                        }
                        .input-group {
                            margin-bottom: 15px;
                        }
                        button {
                            padding: 20px 30px;
                            font-size: 20px;
                        }
                    }
                    
                    /* PWA Install Button */
                    .install-button {
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #28a745;
                        color: white;
                        border: none;
                        padding: 10px 15px;
                        border-radius: 20px;
                        font-size: 14px;
                        font-weight: 600;
                        cursor: pointer;
                        z-index: 1000;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                        display: none;
                    }
                    
                    .install-button:hover {
                        background: #218838;
                        transform: translateY(-1px);
                    }
                    
                    /* Touch improvements */
                    button, input, textarea, select {
                        -webkit-tap-highlight-color: transparent;
                        touch-action: manipulation;
                    }
                    
                    /* Prevent text selection on buttons */
                    button {
                        -webkit-user-select: none;
                        -moz-user-select: none;
                        -ms-user-select: none;
                        user-select: none;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🇬🇷 Ανάλυση Ελληνικών Ειδήσεων</h1>
                        <p>Ελέγξτε αν ένα άρθρο περιέχει στοιχεία προπαγάνδας</p>
                    </div>
                    
                    <form id="analysisForm">
                        <div class="input-group">
                            <label for="inputType">Τρόπος Εισαγωγής:</label>
                            <select id="inputType" onchange="toggleInputType()">
                                <option value="text">Κείμενο άρθρου</option>
                                <option value="url">URL άρθρου</option>
                            </select>
                        </div>
                        
                        <div class="input-group" id="textInput">
                            <label for="text">Κείμενο Άρθρου:</label>
                            <textarea id="text" placeholder="Επικολλήστε εδώ το κείμενο του άρθρου..." maxlength="10000" oninput="updateCharCount()"></textarea>
                            <div class="char-count" id="charCount">0 / 10,000 χαρακτήρες (ελάχιστο 50)</div>
                        </div>
                        
                        <div class="input-group" id="urlInput" style="display: none;">
                            <label for="url">URL Άρθρου:</label>
                            <input type="url" id="url" placeholder="https://example.com/article">
                        </div>
                        
                        <div class="input-group">
                            <label for="source">Πηγή (προαιρετικό):</label>
                            <input type="text" id="source" placeholder="π.χ. ΕΡΤ, ΣΚΑΪ, ANT1, κ.λπ.">
                        </div>
                        
                        <button type="submit" id="analyzeBtn">Ανάλυση Άρθρου</button>
                    </form>
                    
                    <button id="installBtn" class="install-button">
                        📱 Εγκατάσταση
                    </button>
                    
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p>Ανάλυση σε εξέλιξη...</p>
                    </div>
                    
                    <div id="result" class="result" style="display: none;">
                        <h3>Αποτελέσματα Ανάλυσης:</h3>
                        <div id="analysis" class="analysis-text"></div>
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

                        if (url) {
                            // Pre-fill URL input
                            document.getElementById('inputType').value = 'url';
                            document.getElementById('url').value = url;
                            toggleInputType();
                            
                            // Auto-analyze if it's a news URL
                            if (isNewsUrl(url)) {
                                setTimeout(() => {
                                    document.getElementById('analysisForm').dispatchEvent(new Event('submit'));
                                }, 1000);
                            }
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
                                document.getElementById('analysis').innerHTML = data.analysis;
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
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'message': 'Greek News Analyzer is running'
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
                
                # Perform analysis using Gemini AI
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