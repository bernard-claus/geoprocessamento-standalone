import os
import sys
from ler_poligonos import ler_poligonos
from exif import Image
import matplotlib.path as mpltPath
from datetime import datetime
import simplekml
import csv
import shutil
import mpu

#################### CONFIGURACOES #######################

CAMINHO = 'G:/Gabi/drone/Britel2/Imagens/'
CAMINHO_KML_POLIGONOS = 'G:Gabi/drone/Britel2/Britel_poligono.kml'
CAMINHO_PTOS_TRACKMAKER = 'G:/Gabi/drone/Britel2/Britel_gps-template-latlon_preenchido.csv'
distancia_max_entre_foto_e_gcp_em_metros = 100

##########################################################

######################## CODIGO ##########################


def executar_separar_fotos(CAMINHO, CAMINHO_KML_POLIGONOS, CAMINHO_PTOS_TRACKMAKER, distancia_max_entre_foto_e_gcp_em_metros):
  ptos_de_controle = []

  poligonos = ler_poligonos(CAMINHO_KML_POLIGONOS)

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
            caminho = mpltPath.Path(poligonos[chave])
            caminhoContemPonto = caminho.contains_point((latitude, longitude))
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
                print('Foto ' + file + ' perto do ponto de controle  ' + str(ponto[0]))
            if caminhoContemPonto: 
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

  def copiar_arquivos_para_gpc():
    for ponto_controle in fotos_dos_pc:
      if not os.path.isdir(CAMINHO + ponto_controle + '/'):
        try:
          os.mkdir(CAMINHO + ponto_controle + '/')
        except Exception as err:
          print('ERRO ao tentar criar diretorio de ponto de controle ' + ponto_controle + ':')
          print(err)
      for foto in fotos_dos_pc[ponto_controle]:
        try:
          shutil.copy(CAMINHO + foto, CAMINHO + ponto_controle + '/' + foto)
        except Exception as err:
          print('ERRO ao tentar copiar foto ' + foto + ' para pasta do ponto de controle ' + ponto_controle + ':')
          print(err)

  def renomear_arquivos():
    fotos_a_copiar = []
    # Verificar se tem fotos que estao em mais de um poligono
    for file in [file for file in os.listdir(CAMINHO) if '.JPG' in file]:
      arq_contendo_a_chave = 0
      for chave in fotos_em_poligonos:
        if file in fotos_em_poligonos[chave]:
          arq_contendo_a_chave += 1
      if arq_contendo_a_chave > 1:
        fotos_a_copiar.append(file)
    # Criar diretorios e renomear arquivos
    for chave in fotos_em_poligonos:
      if not os.path.isdir(CAMINHO + chave + '/'):
        try:
          os.mkdir(CAMINHO + chave + '/')
        except Exception as err:
          print('ERRO ao tentar criar diretorio ' + chave + ':')
          print(err)
      if not os.path.isdir(CAMINHO + 'todos_KML/'):
        try:
          os.mkdir(CAMINHO + 'todos_KML/')
        except Exception as err:
            print('ERRO ao tentar criar diretorio ' + chave + ':')
            print(err)
      try:
        kml_dos_poligonos[chave].save(CAMINHO + chave + '/' + str(len(fotos_em_poligonos[chave])) + '_fotos_no_poligono.kml')
        kml_dos_poligonos[chave].save(CAMINHO + 'todos_KML/' + str(len(fotos_em_poligonos[chave])) + '_fotos_no_poligono_' + chave + '.kml')
      except Exception as err:
        print('ERRO salvando KML:')
        print(err)
      for arquivo in fotos_em_poligonos[chave]:
        try:
          if arquivo in fotos_a_copiar:
            shutil.copyfile(CAMINHO + arquivo, CAMINHO + chave + '/' + arquivo)
          else:
            os.rename(CAMINHO + arquivo,  CAMINHO + chave + '/' + arquivo)
        except Exception as err:
          print('ERRO renomeando arquivo para ' + CAMINHO + chave + '/' + arquivo)
          print(err)
    for arquivo in fotos_a_copiar:
      os.remove(CAMINHO + arquivo)
    if len(fotos_a_copiar) > 1:
      print('Fotos duplicadas (foram para mais de um poligono):')
      for arquivo in fotos_a_copiar:
        for chave in fotos_em_poligonos:
          if arquivo in fotos_em_poligonos[chave]:
            print(arquivo + ' - Poligono ' + chave)

  iniciar_fotos_dos_pc()
  iniciar_fotos_em_poligonos()
  iniciar_kml_dos_poligonos()
  rodar()
  copiar_arquivos_para_gpc()
  renomear_arquivos()

