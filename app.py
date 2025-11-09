from flask import Flask, send_from_directory, request, jsonify
import os, json
from datetime import datetime
from urllib.parse import parse_qs, unquote_plus

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
    # CORS / preflight
    if request.method == 'OPTIONS':
        resp = jsonify({"status": "ok"})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        resp.headers.add("Access-Control-Allow-Headers", "Content-Type")
        resp.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return resp

    raw = request.get_data(as_text=True) or ""
    os.makedirs("results", exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")

    # guardo siempre el crudo
    with open(f"results/raw_{ts}.txt", "w", encoding="utf-8") as f:
        f.write(raw)

    data = None

    # 1) intentar JSON directo
    try:
        data = json.loads(raw)
    except Exception:
        data = None

    # 2) si no era json directo, viene como form: sessionJSON=...
    if data is None:
        parsed = parse_qs(raw)
        if "sessionJSON" in parsed:
            session_str = unquote_plus(parsed["sessionJSON"][0])
            data = json.loads(session_str)

    if data is None:
        resp = jsonify({"status": "error", "reason": "no data received"})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp, 400

    # guardar el json lindo
    fname = f"results/result_{ts}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ guardado en {fname}")

    resp = jsonify({"status": "ok"})
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp
