from flask import Flask, send_from_directory, request, jsonify
import os
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
    # si existe, lo sirve
    if os.path.exists(path):
        return send_from_directory('.', path)
    # si no existe, 404
    return "File not found", 404


# --- OPCIONAL: endpoint para guardar resultados ---
# si más adelante lo querés usar, en el YAML ponés:
# serviceResults: "https://TU-APP.onrender.com/save_result"
@app.route('/save_result', methods=['POST'])
def save_result():
    data = request.get_json(force=True)
    # carpeta donde guardar (se queda en el contenedor de Render)
    os.makedirs('results', exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
    filename = os.path.join('results', f'result_{ts}.json')
    with open(filename, 'w', encoding='utf-8') as f:
        import json
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({"status": "ok"})
