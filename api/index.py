from http.server import BaseHTTPRequestHandler
import json
import os
import re
import hashlib
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-lite')

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
        
        # Cache the result
        analysis_cache[cache_key] = response.text
        return response.text
        
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
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Ανάλυση Ελληνικών Ειδήσεων</title>
                <style>
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        max-width: 900px; 
                        margin: 0 auto; 
                        padding: 20px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
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
                        white-space: pre-wrap;
                        line-height: 1.6;
                        font-size: 14px;
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