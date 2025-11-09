from flask import Flask, send_from_directory, request, jsonify
import os, json
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_proxy(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "File not found", 404


@app.route('/save_result', methods=['POST', 'OPTIONS'])
def save_result():
    # --- CORS / preflight ---
    if request.method == 'OPTIONS':
        resp = jsonify({"status": "ok"})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        resp.headers.add("Access-Control-Allow-Headers", "Content-Type")
        resp.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return resp

    # 1) intentá leer JSON "normal"
    data = request.get_json(silent=True)

    # 2) si no vino, leemos el body crudo y lo parseamos como JSON
    if data is None:
        raw = request.get_data(as_text=True) or ""
        try:
            data = json.loads(raw)
        except Exception:
            data = None

    if data is None:
        # sigue sin haber datos válidos
        resp = jsonify({"status": "error", "reason": "no data received"})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp, 400

    # 3) guardar
    os.makedirs("results", exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join("results", f"result_{ts}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ resultado guardado en {filename}")

    resp = jsonify({"status": "ok"})
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp


