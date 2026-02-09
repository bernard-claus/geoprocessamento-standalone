import mpu
import os

from exif import Image

from api_class.functions.associar_fotos_com_gcp.separar_fotos import executar_separar_fotos
from api_class.functions.associar_fotos_com_gcp.ler_xy import abrir_imagem
from api_class.functions.associar_fotos_com_gcp.predizer_gcp import predizer_gcp

class AssociarFotosApi:
    def separar_fotos(self, inputs):
        return executar_separar_fotos(inputs)

    def obter_posicao_relativa_do_pto_na_imagem(self, foto, caminho, pto_controle_nome, pred_x, pred_y):
        return abrir_imagem(foto, caminho, pto_controle_nome, pred_x, pred_y)
    
    def ver_imagem(self, foto, caminho, pto_controle_nome, rel_x, rel_y):
      print('Ver imagem: rel_x/y: ', rel_x, rel_y)
      return abrir_imagem(foto, caminho, pto_controle_nome, rel_x, rel_y, no_return=True)
  
    def predizer_gcp_em_fotos(self, fotos, caminho, pto_controle_nome, relative_positions, fotos_referencia):
        return predizer_gcp(fotos, caminho, pto_controle_nome, relative_positions, fotos_referencia)
    
    def distancia_imagem_pto(self, foto, caminho, gcp):
        
        def decimal_coords(coords, ref):
            decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
            if ref == "S" or ref =='W' :
                decimal_degrees = -decimal_degrees
            return decimal_degrees

        im_path = os.path.join(caminho, foto)
        img = Image(im_path)
        latitude = decimal_coords(img.gps_latitude,img.gps_latitude_ref)
        longitude = decimal_coords(img.gps_longitude,img.gps_longitude_ref)
        return mpu.haversine_distance((latitude, longitude), (float(gcp[1]), float(gcp[2])))