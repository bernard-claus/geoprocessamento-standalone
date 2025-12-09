import os
import sys
from api_class.functions.associar_fotos_com_gcp.ler_poligonos import ler_poligonos
from exif import Image
import matplotlib.path as mpltPath
from datetime import datetime
import simplekml
import csv
import mpu


def executar_separar_fotos(inputs):
  CAMINHO = inputs['CAMINHO'] + r'\\'
  CAMINHO_KML_POLIGONOS = inputs['CAMINHO_KML_POLIGONOS']
  CAMINHO_PTOS_TRACKMAKER = inputs['CAMINHO_PTOS_TRACKMAKER']
  distancia_max_entre_foto_e_gcp_em_metros = float(inputs['distancia_max_entre_foto_e_gcp_em_metros'])

  ptos_de_controle = []

  poligonos = None
  if CAMINHO_KML_POLIGONOS:
    poligonos = ler_poligonos(CAMINHO_KML_POLIGONOS)
  else:
    poligonos = { 'nenhum': [] }

  with open(CAMINHO_PTOS_TRACKMAKER, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for index, row in enumerate(reader):
      if index == 0:
        continue
      ptos_de_controle.append(row)

  fotos_dos_pc = {}

  fotos_em_poligonos = { 'nenhum': [] }

  kml_dos_poligonos = { 'nenhum': simplekml.Kml() }

  nro_fotos = len([file for file in os.listdir(CAMINHO) if '.JPG' in file])

  if nro_fotos == 0:
    print('Nao foram achados arquivos .JPG no diretorio fornecido: ' + CAMINHO)
    sys.exit()

  def iniciar_fotos_dos_pc():
    for row in ptos_de_controle:
      fotos_dos_pc[row[0]] = []

  def iniciar_fotos_em_poligonos():
    if CAMINHO_KML_POLIGONOS:
      for chave in poligonos:
        fotos_em_poligonos[chave] = []

  def iniciar_kml_dos_poligonos():
    for chave in poligonos:
      kml_dos_poligonos[chave] = simplekml.Kml()

  def decimal_coords(coords, ref):
      decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
      if ref == "S" or ref =='W' :
          decimal_degrees = -decimal_degrees
      return decimal_degrees

  def rodar():
    for gen_index, file in enumerate([file for file in os.listdir(CAMINHO) if '.JPG' in file]):
      latitude = None
      longitude = None
      try:
        with open(CAMINHO + file, 'rb') as src:
          appended = False
          img = Image(src)
          latitude = decimal_coords(img.gps_latitude,img.gps_latitude_ref)
          longitude = decimal_coords(img.gps_longitude,img.gps_longitude_ref)
          for chave in poligonos:
            caminho = None
            caminho_contem_ponto = False
            if CAMINHO_KML_POLIGONOS:
              caminho = mpltPath.Path(poligonos[chave])
              caminho_contem_ponto = caminho.contains_point((latitude, longitude))
            for ponto in ptos_de_controle:
              distancia_foto_gcp = mpu.haversine_distance((latitude, longitude), (float(ponto[1]), float(ponto[2])))
              # caminho_pto = mpltPath.Path([
                # (float(ponto[1]) + distancia_para_achar_pc, float(ponto[2]) - distancia_para_achar_pc * abs(40075 * math.cos(float(ponto[1])) / 360)),
                # (float(ponto[1]) + distancia_para_achar_pc, float(ponto[2]) + distancia_para_achar_pc * abs(40075 * math.cos(float(ponto[1])) / 360)),
                # (float(ponto[1]) - distancia_para_achar_pc, float(ponto[2]) + distancia_para_achar_pc * abs(40075 * math.cos(float(ponto[1])) / 360)),
                # (float(ponto[1]) - distancia_para_achar_pc, float(ponto[2]) - distancia_para_achar_pc * abs(40075 * math.cos(float(ponto[1])) / 360)),
              # ])
              # foto_perto_do_pc = caminho_pto.contains_point((latitude, longitude))
              if distancia_foto_gcp < distancia_max_entre_foto_e_gcp_em_metros / 1000:
                fotos_dos_pc[ponto[0]].append(file)
                fotos_dos_pc[ponto[0]] = list(set(fotos_dos_pc[ponto[0]]))
                print('Foto ' + file + ' perto do ponto de controle  ' + str(ponto[0]))
            if caminho_contem_ponto: 
              # print(str(gen_index + 1) + '/' + str(nro_fotos) + ' - ' + file.split( '.JPG')[0] + ' dentro do poligono ' + chave)
              fotos_em_poligonos[chave].append(file)
              kml_dos_poligonos[chave].newpoint(name = file.split('.JPG')[0] + '-' + chave, coords=[(longitude,latitude)])  # lon, lat, optional height
              appended = True
          if not appended:
            print(str(gen_index) + '/' + str(nro_fotos) + ' - ' + file.split( '.JPG')[0] + ' nao esta dentro de nenhum poligono')
            fotos_em_poligonos['nenhum'].append(file)
            kml_dos_poligonos['nenhum'].newpoint(name = file.split('.JPG')[0] + '-' + chave, coords=[(longitude, latitude)])  # lon, lat, optional height
      except Exception as err:
        print('ERRO lendo arquivo ' + CAMINHO + file)
        print(err)
        raise

    # Salvar o log
    try:
      f = open(CAMINHO + "LOG_arquivos_modificados_" + datetime.now().strftime("%d-%m-%Y___%H-%M-%S") + ".txt", "a")
      for chave in fotos_em_poligonos:
        f.write('################################## - ' + chave + ' - ##################################\r\n')
        for foto in fotos_em_poligonos[chave]:
          f.write(foto + '\r\n')
      f.close()
    except Exception as err:
      print('ERRO gravando log:')
      print(err)

  def criar_pasta_sessoes():
    sessoes_path = os.path.join(CAMINHO, 'sessoes')
    if not os.path.exists(sessoes_path):
      os.makedirs(sessoes_path)
    

  iniciar_fotos_dos_pc()
  iniciar_fotos_em_poligonos()
  iniciar_kml_dos_poligonos()
  rodar()
  criar_pasta_sessoes()
  
  return fotos_dos_pc, fotos_em_poligonos, nro_fotos, ptos_de_controle

