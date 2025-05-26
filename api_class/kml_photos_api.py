from api_class.functions.kml_photos.kml_photos import generate_kml_from_photos

class KmlPhotosApi:
  def generate_kml_from_photos(self, folder_path):
      return generate_kml_from_photos(folder_path)
      
  def save_kml(self, file_data_base64, file_name):
    import base64
    file_bytes = base64.b64decode(file_data_base64)
    import webview
    save_path = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename=file_name)
    if save_path:
      with open(save_path, 'wb') as f:
            f.write(file_bytes)
      return {'success': True, 'saved_path': save_path}
    return {'success': False, 'error': 'Save cancelled'}
