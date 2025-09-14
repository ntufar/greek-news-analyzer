import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# Simple in-memory cache for analysis results
analysis_cache = {}

def get_cache_key(text, source=""):
    """Generate a cache key for the analysis"""
    import hashlib
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
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) < 100:
            raise ValueError("Insufficient text content extracted")
            
        return text[:3000]  # Limit to 3000 characters
        
    except Exception as e:
        logger.error(f"Error extracting text from {url}: {str(e)}")
        return f"Error extracting text: {str(e)}"

def analyze_greek_news(text, source=""):
    """Analyze Greek news text for propaganda indicators using Gemini"""
    try:
        # Check cache first
        cache_key = get_cache_key(text, source)
        if cache_key in analysis_cache:
            logger.info("Returning cached analysis result")
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

        logger.info("Sending request to Gemini API")
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Cache the result
        analysis_cache[cache_key] = response.text
        logger.info("Analysis completed and cached")
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        return f"Σφάλμα στην ανάλυση: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/static/sw.js')
def service_worker():
    response = app.send_static_file('sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': os.environ.get('VERCEL_REGION', 'unknown'),
        'cache_size': len(analysis_cache)
    })

@app.route('/status')
def status():
    """Status endpoint with more detailed information"""
    return jsonify({
        'status': 'running',
        'timestamp': os.environ.get('VERCEL_REGION', 'unknown'),
        'cache_size': len(analysis_cache),
        'api_status': 'operational'
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Μη έγκυρα δεδομένα'}), 400
            
        text = data.get('text', '').strip()
        url = data.get('url', '').strip()
        source = data.get('source', '').strip()
        
        # Validate input
        if not text and not url:
            return jsonify({'error': 'Παρακαλώ εισάγετε κείμενο ή URL'}), 400
        
        if url and not text:
            if not url.startswith(('http://', 'https://')):
                return jsonify({'error': 'Μη έγκυρη διεύθυνση URL'}), 400
                
            text = extract_text_from_url(url)
            if text.startswith("Error"):
                return jsonify({'error': text}), 400
        
        # Check minimum text length
        if len(text) < 50:
            return jsonify({'error': 'Το κείμενο είναι πολύ σύντομο για ανάλυση (ελάχιστο 50 χαρακτήρες)'}), 400
        
        # Check maximum text length
        if len(text) > 10000:
            return jsonify({'error': 'Το κείμενο είναι πολύ μεγάλο (μέγιστο 10,000 χαρακτήρες)'}), 400
        
        # Perform analysis
        analysis = analyze_greek_news(text, source)
        
        return jsonify({
            'analysis': analysis,
            'text_length': len(text),
            'source': source if source else 'Άγνωστη',
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return jsonify({'error': f'Σφάλμα: {str(e)}', 'success': False}), 500

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda *args: None)

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)