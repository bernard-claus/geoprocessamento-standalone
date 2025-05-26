from api_class.gerador_perfil_api import GeradorPerfilApi
from api_class.kml_photos_api import KmlPhotosApi
from api_class.api_class import Api

class ApiRoot:
    def __init__(self):
        self.perfil = GeradorPerfilApi()
        self.kml = KmlPhotosApi()
        self.utils = Api()
