import os
import re
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

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
        prompt = f"""
        Αναλύστε αυτό το ελληνικό άρθρο για πιθανά στοιχεία προπαγάνδας:

        Κείμενο: {text}
        Πηγή: {source}

        Παρακαλώ αξιολογήστε από 1-10 (1=πιθανή προπαγάνδα, 10=αξιόπισες ειδήσεις) και εξηγήστε:

        1. Στοιχεία συναισθηματικής χειραγώγησης
        2. Δείκτες προκατάληψης
        3. Αναλογία γεγονότων vs γνώμες
        4. Αξιοπιστία πηγής
        5. Χρήση φορτωμένης γλώσσας
        6. Λογικές πλάνες

        Απαντήστε στα ελληνικά με σαφή και κατανοητό τρόπο.
        """

        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Σφάλμα στην ανάλυση: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        text = data.get('text', '')
        url = data.get('url', '')
        source = data.get('source', '')
        
        if url and not text:
            text = extract_text_from_url(url)
            if text.startswith("Error"):
                return jsonify({'error': text}), 400
        
        if not text.strip():
            return jsonify({'error': 'Παρακαλώ εισάγετε κείμενο ή URL'}), 400
        
        analysis = analyze_greek_news(text, source)
        
        return jsonify({
            'analysis': analysis,
            'text_length': len(text)
        })
        
    except Exception as e:
        return jsonify({'error': f'Σφάλμα: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
