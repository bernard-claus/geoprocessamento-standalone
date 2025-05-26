import webview
from api_class.functions.gerador_perfil.gerador_perfil import gerar_perfil_main
from api_class.functions.gerador_perfil.multi_cortes_terreno_em_lines import gerar_perfil_multicortes_main

class GeradorPerfilApi:
    def gerar_perfil(self, file):
        return gerar_perfil_main(file)

    def gerar_perfil_multicortes(self, file, inputs):
        result = gerar_perfil_multicortes_main(self, file, inputs)
        if isinstance(result, dict):
            return result
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
