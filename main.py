import os
import requests
import webbrowser
import threading
import webview
from flask import Flask, send_from_directory, Response
import mimetypes
from api_class.api_class import Api
from api_class.constants.version import VERSION
from api_class.gerador_perfil_api import GeradorPerfilApi
from api_class.kml_photos_api import KmlPhotosApi
from api_class.api_root import ApiRoot

# Config
PORT = 5000
DIST_DIR = os.path.join(os.path.dirname(__file__), "web", "dist")
GITHUB_REPO = "bernard-claus/geoprocessamento-standalone"

__version__ = VERSION

app = Flask(__name__, static_folder=DIST_DIR)

# Ensure correct MIME types for .js and .css files (Windows fix)
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# Route: serve index.html
@app.route("/")
def index():
    return send_from_directory(DIST_DIR, "index.html")

# Route: serve all static files (JS, CSS, images, etc.)
@app.route('/<path:path>')
def static_proxy(path):
    file_path = os.path.join(DIST_DIR, path)
    print(f"[Flask] Requested: {path} | Exists: {os.path.isfile(file_path)}")
    if os.path.isfile(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        with open(file_path, 'rb') as f:
            content = f.read()
        return Response(content, mimetype=mime_type or 'application/octet-stream')
    else:
        # Fallback to index.html for SPA routes
        print(f"[Flask] Fallback to index.html for: {path}")
        return send_from_directory(DIST_DIR, "index.html")

# Route: serve assets
@app.route("/assets/<path:path>")
def assets(path):
    return send_from_directory(os.path.join(DIST_DIR, "assets"), path)

def start_flask():
    app.run(port=PORT, debug=False)

if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()
    webview.create_window(
        "Ferramentas de Geoprocessamento - Gabriela Figueiredo",
        f"http://localhost:{PORT}",
        js_api=ApiRoot(),
        maximized=True
    )
    webview.start(debug=False, gui='edgechromium')
