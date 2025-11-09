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

    # --- DEBUG: Imprimimos la petición cruda en los Logs de Render ---
    raw = request.get_data(as_text=True) or ""
    content_type = request.headers.get('Content-Type', 'N/A')
    
    print("--- DEBUG WEB_MUSHRA ---")
    print(f"Content-Type recibido: {content_type}")
    print(f"Body Crudo (primeros 500 caracteres): {raw[:500]}...")
    print("--------------------------")
    # --- FIN DEL DEBUG ---

    data = None

    # 1) intentar JSON puro
    data = request.get_json(silent=True)

    # 2) probar form normal
    if data is None and request.form:
        if "session" in request.form:
            data = json.loads(request.form["session"])

    # 3) body crudo tipo "session=..."
    if data is None and raw:
        parsed = parse_qs(raw)
        if "session" in parsed:
            data = json.loads(parsed["session"][0])
    
    # 4) body crudo como JSON
    if data is None and raw:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            pass 

    if data is None:
        print("❌ PARSEO FALLIDO: No se pudieron extraer datos.")
        resp = jsonify({"status": "error", "reason": "no data received or bad format"})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp, 400

    # --- Guardado en disco efímero (como querías probar) ---
    os.makedirs("results", exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join("results", f"result_{ts}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ ¡ÉXITO! Resultado guardado en {filename}")

    resp = jsonify({"status": "ok"})
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp