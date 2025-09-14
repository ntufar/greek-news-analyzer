from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'message': 'Hello from Vercel!'})

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)
