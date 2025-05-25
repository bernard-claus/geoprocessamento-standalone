import webview
import os
from api_class.functions.greet.greet import greet_main
from api_class.functions.open_file import open_file_main
from api_class.functions.gerador_perfil.gerador_perfil import gerar_perfil_main
from api_class.functions.gerador_perfil.multi_cortes_terreno_em_lines import gerar_perfil_multicortes_main


class Api:
    
    def __init__(self):
        self.should_cancel = False
    
    def greet(self, name):
        return greet_main(self, f"Hello, {name}!")
    
    def open_file(self, path):
        return open_file_main(path)
        
    def gerar_perfil(self, file):
        return gerar_perfil_main(file)
        
    def gerar_perfil_multicortes(self, file, inputs):
        result = gerar_perfil_multicortes_main(self, file, inputs)
        # If result is a dict already, just return it. If not, wrap as dict.
        if isinstance(result, dict):
            return result
        # Assume result is file_b64 and OUTPUT_FILE_NAME is available as a global or static var (should be improved for thread safety)
        # For now, return only file_data
        return {'file_data': result, 'file_path': None}

    def save_dxf(self, file_data_base64, file_name):
        import base64
        file_bytes = base64.b64decode(file_data_base64)
        print('asking to create file dialog')
        save_path = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename=f'{file_name}_SAIDA.dxf')
        print('file dialog closed')
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(file_bytes)
            return {'success': True, 'saved_path': save_path}
        return {'success': False, 'error': 'Save cancelled'}

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