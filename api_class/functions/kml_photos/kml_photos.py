import simplekml
import os
from exif import Image
import base64
import io
import matplotlib.path as mpltPath

def generate_kml_from_photos(folder_path):
    def decimal_coords(coords, ref):
        decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
        if ref == "S" or ref == "W":
            decimal_degrees = -decimal_degrees
        return decimal_degrees

    kml = simplekml.Kml()

    for index, file in enumerate([f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]):
        latitude = None
        longitude = None
        with open(os.path.join(folder_path, file), 'rb') as src:
            img = Image(src)
            latitude = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
            longitude = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
        kml.newpoint(name=''.join(file.upper().split('.JPG')), coords=[(longitude, latitude)])  # lon, lat
    # Save to a BytesIO buffer instead of disk
    buffer = io.BytesIO()
    kml_content = kml.kml()
    buffer.write(kml_content.encode('utf-8'))
    buffer.seek(0)
    file_b64 = base64.b64encode(buffer.read()).decode('utf-8')
    return {'success': True, 'file_data': file_b64, 'file_name': 'coordenadas_das_fotos.kml'}
