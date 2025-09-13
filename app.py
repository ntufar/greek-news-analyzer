import os
import re
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # In production, use Redis: "redis://localhost:6379"
)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-lite')

def extract_text_from_url(url):
    """Extract text content from a news URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:3000]  # Limit to 3000 characters for API efficiency
        
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def analyze_greek_news(text, source=""):
    """Analyze Greek news text for propaganda indicators using Gemini"""
    try:
        # Enhanced prompt with more detailed analysis criteria
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
        return response.text
        
    except Exception as e:
        return f"Σφάλμα στην ανάλυση: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
@limiter.limit("10 per minute")  # More restrictive for analysis endpoint
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
            # Validate URL format
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
        return jsonify({'error': f'Σφάλμα: {str(e)}', 'success': False}), 500

# Rate limit error handler
@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded errors"""
    return jsonify({
        'error': 'Έχετε υπερβεί το όριο αιτημάτων. Παρακαλώ περιμένετε πριν κάνετε νέα ανάλυση.',
        'retry_after': e.retry_after,
        'limit': str(e.description),
        'success': False
    }), 429

# Rate limit status endpoint
@app.route('/rate-limit-status')
@limiter.limit("5 per minute")
def rate_limit_status():
    """Get current rate limit status for the user"""
    try:
        return jsonify({
            'status': 'active',
            'limits': {
                'daily': '200 per day',
                'hourly': '50 per hour', 
                'analysis': '10 per minute'
            },
            'message': 'Rate limiting is active. Check response headers for current usage.'
        })
    except Exception as e:
        return jsonify({
            'error': f'Σφάλμα λήψης κατάστασης: {str(e)}'
        }), 500

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'Greek News Analyzer',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
