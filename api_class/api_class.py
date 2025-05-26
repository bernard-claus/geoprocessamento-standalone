import webview
import os
import requests
from api_class.functions.greet.greet import greet_main
from api_class.functions.open_file import open_file_main
from api_class.functions.gerador_perfil.gerador_perfil import gerar_perfil_main
from api_class.functions.gerador_perfil.multi_cortes_terreno_em_lines import gerar_perfil_multicortes_main
from api_class.constants.version import VERSION


__version__ = VERSION  # Update this with each release
GITHUB_REPO = 'bernard-claus/geoprocessamento-standalone'  # Replace with your actual repo

class Api:
    global __version__, GITHUB_REPO
    def __init__(self):
        self.should_cancel = False
    
    def open_file(self, path):
        return open_file_main(path)


    def open_in_explorer(self, file_path):
        if file_path and os.path.exists(file_path):
            os.startfile(os.path.dirname(file_path))
            return {'success': True}
        return {'success': False, 'error': 'File not found'}
    
    def cancel_processing(self, cancel):
        if cancel:
            self.should_cancel = True
        else:
            self.should_cancel = False
        return {'success': True}

    def check_for_update(self):
        """
        Checks GitHub for the latest release and compares with current version.
        Returns a dict with update info.
        """
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_version = data["tag_name"].lstrip("v")
                release_url = data["html_url"]
                assets = data.get("assets", [])
                download_url = None
                for asset in assets:
                    if asset["name"].endswith(".exe"):
                        download_url = asset["browser_download_url"]
                        break
                update_available = latest_version > __version__
                return {
                    "current_version": __version__,
                    "latest_version": latest_version,
                    "update_available": update_available,
                    "download_url": download_url,
                    "release_url": release_url,
                    "release_notes": data.get("body", "")
                }
            else:
                return {"error": "Could not fetch release info."}
        except Exception as e:
            return {"error": str(e)}
    
    def get_version(self):
        global __version__
        return {"version": __version__}

    def select_folder(self):
        result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
        print(result)
        if result and isinstance(result, tuple) and len(result) > 0:
            return result[0]
        return None