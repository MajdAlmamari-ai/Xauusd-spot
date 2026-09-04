# presentation_layer/app.py
from flask import Flask, jsonify, render_template
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/analysis')
def analysis():
    return jsonify({
        'price': 4472.91,
        'bias': 'NEUTRAL',
        'session': 'LONDON',
        'timestamp': datetime.now().isoformat()
    })

def run_server(host='0.0.0.0', port=5000):
    app.run(host=host, port=port, debug=False)
