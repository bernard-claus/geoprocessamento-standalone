from api_class.functions.associar_fotos_com_gcp.separar_fotos import executar_separar_fotos
from api_class.functions.associar_fotos_com_gcp.ler_xy import abrir_imagem

class AssociarFotosApi:
    def separar_fotos(self, inputs):
        return executar_separar_fotos(inputs)

    def obter_posicao_relativa_do_pto_na_imagem(self, foto, caminho, pto_controle_nome):
        return abrir_imagem(foto, caminho, pto_controle_nome)
    
    def ver_imagem(self, foto, caminho, pto_controle_nome, rel_x, rel_y):
      return abrir_imagem(foto, caminho, pto_controle_nome, rel_x, rel_y)