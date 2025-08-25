from api_class.functions.read_shapefile.read_shapefile_funcion import get_shapefile_vertices, gerar_shapefile

class ReadShapeFile:
  def get_vertices(self, shp_path):
      return get_shapefile_vertices(self, shp_path)
    
  def gerar_arquivo(self, vertices, file_path):
      return gerar_shapefile(vertices, file_path)
      
  def save_shape(self, file_data_base64, file_name):
    import base64
    file_bytes = base64.b64decode(file_data_base64)
    import webview
    save_path = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename=file_name)
    if save_path:
      with open(save_path, 'wb') as f:
            f.write(file_bytes)
      return {'success': True, 'saved_path': save_path}
    return {'success': False, 'error': 'Save cancelled'}