# Primeiro precisa separar as fotos com separar_fotos_multi_poligonos.py
# Usar o mesmo CAMINHO_KML_POLIGONOS nos tanto em separar_fotos_multi_poligonos.py como aqui

# Funcionamento:
# abre a janela com a imagem do drone para selecionar o ponto de controle
# vai usar os pontos em kml_poligonos


from ler_xy import abrir_imagem
import csv
import os
import utm
from ler_poligonos import ler_poligonos
# exec(open(r'associar_ptos_com_fotos.py').read())

# CAMINHO = 'G:/Gabi/drone/Britel2/Imagens/'
# CAMINHO_KML_POLIGONOS = 'G:Gabi/drone/Britel2/Britel_poligono.kml' # Usa para fazer o GCP final - verifica a pasta com nome do poligono e procura as fotos la dentro
# CAMINHO_PTOS_TRACKMAKER = 'G:/Gabi/drone/Britel2/Britel_gps-template-latlon_preenchido.csv'
# GCP_LIST_NAME = 'gcp_list.txt' # nome que vai sair o arquivo GCP com os pontos, as fotos e as coordenadas relativas da foto

################ CODIGO ################

def executar_associar_ptos_com_gcp(CAMINHO, CAMINHO_KML_POLIGONOS, CAMINHO_PTOS_TRACKMAKER, GCP_LIST_NAME):
  GCP_HEADER = '+proj=utm +zone=22 +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs'

  pontos_de_controle = []
  pontos_final = []
  poligonos = ler_poligonos(CAMINHO_KML_POLIGONOS)

  # Gerar pontos de controle
  with open(CAMINHO_PTOS_TRACKMAKER, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for index, row in enumerate(reader):
      if index == 0:
        continue
      pontos_de_controle.append(row)

  for index, ponto_c in enumerate(pontos_de_controle):
    for gen_index, file in enumerate([file for file in os.listdir(CAMINHO + ponto_c[0] + '/') if '.JPG' in file]):
      nova_linha_pc = []
      relative_coord = abrir_imagem(CAMINHO + ponto_c[0] + '/' + file, ponto_c[0])
      # if index == 0:
      #     relative_coord = abrir_imagem(CAMINHO + ponto_c[0] + '/' + file, ponto_c[0])
      # else:
      #     exit()
      coord_gpc_em_utm = utm.from_latlon(float(ponto_c[1]), float(ponto_c[2]))
      if coord_gpc_em_utm[2] != 22 or coord_gpc_em_utm[3] != 'J':
        break
      nova_linha_pc.append(coord_gpc_em_utm[0])
      nova_linha_pc.append(coord_gpc_em_utm[1])
      nova_linha_pc.append(ponto_c[3])
      nova_linha_pc.append(relative_coord[0])
      nova_linha_pc.append(relative_coord[1])
      nova_linha_pc.append(file)
      pontos_final.append(nova_linha_pc)

  # f = open(CAMINHO_OUTPUT_GCP_LIST_TXT, "a+")

  # Uso dos poligonos em CAMINHO_KML_POLIGONOS
  for poligono in poligonos:
    f = open(CAMINHO + poligono + '/' + GCP_LIST_NAME, "a+")
    pasta = CAMINHO + poligono + '/'
    for ind, ponto in enumerate(pontos_final):
      if ind == 0:
        f.write(GCP_HEADER + '\n')
      if ponto[5] in os.listdir(pasta):
        for index, item in enumerate(ponto):
          f.write(str(item))
          if index != len(ponto) -1:
            f.write('\t')
          else:
            f.write('\n')
    f.close()

  f.close()
  # exit()
  