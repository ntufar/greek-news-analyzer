from http.server import BaseHTTPRequestHandler
import json
import os

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
                <title>Greek News Analyzer</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
                    textarea { width: 100%; height: 200px; margin: 10px 0; }
                    button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                    .result { margin-top: 20px; padding: 15px; background: white; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🇬🇷 Greek News Analyzer</h1>
                    <p>Analyze Greek news articles for propaganda indicators</p>
                    
                    <form id="analysisForm">
                        <label for="text">Article Text:</label>
                        <textarea id="text" placeholder="Paste your Greek news article here..."></textarea>
                        <br>
                        <label for="source">Source (optional):</label>
                        <input type="text" id="source" placeholder="e.g., ΕΡΤ, ΣΚΑΪ, ANT1">
                        <br>
                        <button type="submit">Analyze Article</button>
                    </form>
                    
                    <div id="result" class="result" style="display: none;">
                        <h3>Analysis Results:</h3>
                        <div id="analysis"></div>
                    </div>
                </div>
                
                <script>
                    document.getElementById('analysisForm').addEventListener('submit', async function(e) {
                        e.preventDefault();
                        const text = document.getElementById('text').value;
                        const source = document.getElementById('source').value;
                        
                        if (!text.trim()) {
                            alert('Please enter some text to analyze');
                            return;
                        }
                        
                        try {
                            const response = await fetch('/analyze', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ text, source })
                            });
                            
                            const data = await response.json();
                            
                            if (data.error) {
                                document.getElementById('analysis').innerHTML = '<p style="color: red;">Error: ' + data.error + '</p>';
                            } else {
                                document.getElementById('analysis').innerHTML = '<pre>' + data.analysis + '</pre>';
                            }
                            
                            document.getElementById('result').style.display = 'block';
                        } catch (error) {
                            document.getElementById('analysis').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
                            document.getElementById('result').style.display = 'block';
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
                text = data.get('text', '')
                source = data.get('source', '')
                
                # Simple analysis (placeholder)
                analysis = f"""
                **ANALYSIS RESULTS**
                
                Text Length: {len(text)} characters
                Source: {source if source else 'Unknown'}
                
                This is a placeholder analysis. The full AI analysis feature requires:
                1. Setting up the GEMINI_API_KEY environment variable
                2. Installing the required Python packages
                
                For now, this demonstrates that the basic functionality is working.
                """
                
                response = {
                    'analysis': analysis,
                    'text_length': len(text),
                    'source': source if source else 'Unknown',
                    'success': True
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                error_response = {
                    'error': f'Analysis failed: {str(e)}',
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