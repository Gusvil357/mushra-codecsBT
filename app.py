from flask import Flask, send_from_directory, request, jsonify
import os, json
from datetime import datetime
from urllib.parse import parse_qs

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

    data = None
    raw = request.get_data(as_text=True) or "" # Leemos el body crudo primero

    # 1) intentar JSON puro (si el Content-Type es correcto)
    data = request.get_json(silent=True)

    # 2) probar form normal: webMUSHRA suele mandar "session=...."
    if data is None and request.form:
        if "session" in request.form:
            data = json.loads(request.form["session"])
        elif "json" in request.form:
            data = json.loads(request.form["json"])

    # 3) último recurso: body crudo tipo "session=..."
    if data is None and raw:
        parsed = parse_qs(raw)
        if "session" in parsed:
            data = json.loads(parsed["session"][0])
        elif "json" in parsed:
            data = json.loads(parsed["json"][0])

    # 4) NUEVO: Asumir que el body ENTERO es el JSON
    if data is None and raw:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            pass # Si no es JSON, no hacemos nada, data sigue None

    if data is None:
        # Ahora si falla, es porque de verdad no vino nada
        resp = jsonify({"status": "error", "reason": "no data received or bad format"})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp, 400

    # --- guardar en /results (DISCO EFIMERO) ---
    # (Recuerda que esto se borrará en cada deploy)
    os.makedirs("results", exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join("results", f"result_{ts}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ resultado guardado en {filename}")

    resp = jsonify({"status": "ok"})
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp


