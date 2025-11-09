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

    # 1) LEER UNA SOLA VEZ EL CUERPO
    raw = request.get_data(as_text=True) or ""

    # opcional: guardar siempre el crudo para debug
    os.makedirs("results", exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    raw_filename = os.path.join("results", f"raw_{ts}.txt")
    with open(raw_filename, "w", encoding="utf-8") as f:
        f.write(raw)

    data = None

    # 2) primero intentar parsear como JSON directo (lo que vimos que manda webMUSHRA)
    try:
        data = json.loads(raw)
    except Exception:
        data = None

    # 3) si no era JSON puro, probar formato form: "session=..."/"json=..."
    if data is None and raw:
        parsed = parse_qs(raw)
        if "session" in parsed:
            session_str = unquote_plus(parsed["session"][0])
            data = json.loads(session_str)
        elif "json" in parsed:
            session_str = unquote_plus(parsed["json"][0])
            data = json.loads(session_str)

    if data is None:
        # no se pudo interpretar, pero el raw ya quedó guardado
        resp = jsonify({"status": "error", "reason": "no data received"})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp, 400

    # 4) guardar el JSON ya parseado
    result_filename = os.path.join("results", f"result_{ts}.json")
    with open(result_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ guardado: {result_filename}")

    resp = jsonify({"status": "ok"})
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp


