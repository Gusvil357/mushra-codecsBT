from flask import Flask, send_from_directory, request, jsonify
import os
import json
from datetime import datetime

# sirve todos los archivos estáticos desde la carpeta actual
app = Flask(__name__, static_folder='.', static_url_path='')

# página principal -> index.html
@app.route('/')
def index():
    return app.send_static_file('index.html')

# servir cualquier otro archivo (lib, configs, audio, etc.)
@app.route('/<path:path>')
def static_proxy(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "File not found", 404


# ===== endpoint para guardar resultados =====
@app.route('/save_result', methods=['POST', 'OPTIONS'])
def save_result():
    # preflight CORS
    if request.method == 'OPTIONS':
        resp = jsonify({"status": "ok"})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        resp.headers.add("Access-Control-Allow-Headers", "Content-Type")
        resp.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return resp

    data = request.get_json(force=True)

    os.makedirs('results', exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
    filename = os.path.join('results', f'result_{ts}.json')

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    resp = jsonify({"status": "ok"})
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp
