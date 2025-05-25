# um perfil de cada vez, deve estar em formato line_corte
# todas as cn em um so layer chamado terreno (maiuscula)
# ponto inicial do corte sempre o mais a esquerda
# conferir no final, pode estar espelhado
# NA JANELA DE COMANDO, DIGITAR 'python' (sem as aspas) PARA ENTRAR NO TERMINAL DO PYTHON
# COPIAR E COLAR O COMANDO ABAIXO NO TERMINAL DO PYTHON
#  exec(open(r'multi_cortes_terreno_em_lines.py').read())

# INCLUI:
# Grid com texto
# Escala em y
# Aceita multiplas linhas de PERFIL (gera um grid para cada linha de corte)

import sys
import ezdxf
from ezdxf.math import ABS_TOL
from ezdxf.enums import TextEntityAlignment
from sympy import Point, Line, Segment
from sympy import *
import webview
import time
import math
import tempfile
import base64
import io
import traceback


################################################################
############################ CODIGO ############################
################################################################

def gerar_perfil_multicortes_main(self, input_file_b64, inputs):
    
    window = webview.windows[0]
    
    window.evaluate_js(f"window.handleProgress('Iniciando com os parametros:')")
    for key in inputs:
        window.evaluate_js(f"window.handleProgress('{key}: {inputs[key]}')")
    
    # CONFIGURACOES DO USUARIO:
    # Distancia x entre as linhas verticais de grid:
    x_distance = float(inputs['x_distance'])
    # Distancia y entre as linhas horizontais de grid:
    y_distance = float(inputs['y_distance'])
    # Escala em y dos graficos gerados. Pode ser qualquer valor (1 é sem transformacao)
    y_scale = float(inputs['y_scale'])
    # Codigo da cor do grid (padrao eh 254 - quase branco)
    GRID_COLOR_CODE = float(inputs['GRID_COLOR_CODE'])
    # Codigo da cor do perfil (padrao eh 45 - meio laranja ou marrom)
    PROFILE_COLOR_CODE = float(inputs['PROFILE_COLOR_CODE'])
    # NOME DOS ARQUIVOS DE ENTRADA E SAIDA

    # NOME DOS PERFIS DE CORTE E DE TERRENO. O PADRAO EH 'PERFIL' E 'TERRENO'
    CORTE_LAYER = inputs['CORTE_LAYER']
    TERRENO_LAYER = inputs['TERRENO_LAYER']

    time_start = time.time()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
        try:
            if input_file_b64.startswith('data:'):
                input_file_b64 = input_file_b64.split(',', 1)[1]
            file_bytes = base64.b64decode(input_file_b64)
            file_obj = io.BytesIO(file_bytes)
            tmp.write(file_obj.read())
            tmp_path = tmp.name
        except Exception as e:
            print(f"Error decoding base64 file: {e}")
            tb_str = traceback.format_exc()
            window.evaluate_js("window.handleProgress('Erro ao decodificar o arquivo base64')")
            window.evaluate_js(f"window.handleProgress('{tb_str}')")
            return None

    OUTPUT_FILE_NAME = f'{''.join(tmp_path.split('.dxf'))}_SAIDA.dxf'
    
    try:
        doc = ezdxf.readfile(tmp_path)
    except IOError as e:
        tb_str = traceback.format_exc()
        print(f'Not a DXF file or a generic I/O error.')
        window.evaluate_js("window.handleProgress('Not a DXF file or a generic I/O error')")
        window.evaluate_js(f"window.handleProgress('{tb_str}')")
        return None
    except ezdxf.DXFStructureError as e:
        tb_str = traceback.format_exc()
        print(f'Invalid or corrupted DXF file.')
        window.evaluate_js("window.handleProgress('Invalid or corrupted DXF file')")
        window.evaluate_js(f"window.handleProgress('{tb_str}')")
        return None

    # line_corte = Line((0,0),(0,1))
    # p1_corte_x = 0
    # p1_corte_y = 0
    # p2_corte_x = 0
    # p2_corte_y = 0
    # p1_corte = Point(p1_corte_x,p1_corte_y)
    # p2_corte= Point(p2_corte_x,p2_corte_y)
    count_plines=0
    erros_encontrados=0
    min_x=10000000000
    min_y=10000000000
    max_x=-100000000
    max_y=-100000000
    elevation_min = 100000000
    elevation_max = -100000000
    # grid_length = 0
    lines_not_evaluated=0
    lines_evaluated=0
    linhas_de_corte=[]
    linhas_com_intersecao=[]
    grid_number = 0
    grid_heights = []
    total_grid_offset = 0

    def sort_x(e):
        if e != None and len(e) > 0:
            return e[0]

    def definir_linhas_de_corte(e):
        nonlocal erros_encontrados
        if len(linhas_de_corte) > 0:
            window.evaluate_js(f"window.handleProgress('Já existe uma linha de corte definida')")
            window.evaluate_js(f"window.handleProgress('Ignorando linha de corte: ({e.dxf.start}, {e.dxf.end})')")
            print('Já existe uma linha de corte definida')
            print('Ignorando linha de corte: (%s, %s)' % (e.dxf.start, e.dxf.end))
            return
        window.evaluate_js("window.handleProgress('Iniciando...')")
        print("Linha de perfil no layer %s" % e.dxf.layer)
        print("Ponto inicial: %s" % e.dxf.start)
        print("Ponto final: %s" % e.dxf.end)
        window.evaluate_js(f"window.handleProgress('Linha de perfil no layer {e.dxf.layer}')")
        window.evaluate_js(f"window.handleProgress('Ponto inicial: {e.dxf.start}')")
        window.evaluate_js(f"window.handleProgress('Ponto final: {e.dxf.end}')")
        
        try:
            if e.dxf.start[0]<e.dxf.end[0]:
                p1_corte_x = e.dxf.start[0]
                p1_corte_y = e.dxf.start[1]
                p2_corte_x = e.dxf.end[0]
                p2_corte_y = e.dxf.end[1]
            else: 
                p1_corte_x = e.dxf.end[0]
                p1_corte_y = e.dxf.end[1]
                p2_corte_x = e.dxf.start[0]
                p2_corte_y = e.dxf.start[1]
            p1_corte = Point(p1_corte_x,p1_corte_y)
            p2_corte = Point(p2_corte_x,p2_corte_y)
            line_corte = Segment(p1_corte,p2_corte)
            grid_length = p1_corte.distance(p2_corte)
            output_dict = {}
            output_dict['p1_corte_x'] = p1_corte_x
            output_dict['p1_corte_y'] = p1_corte_y
            output_dict['p2_corte_x'] = p2_corte_x
            output_dict['p2_corte_y'] = p2_corte_y
            output_dict['p1_corte'] = p1_corte
            output_dict['p2_corte'] = p2_corte
            output_dict['line_corte'] = line_corte
            output_dict['grid_length'] = grid_length
            linhas_de_corte.append(output_dict)
        except:
            erros_encontrados += 1
            window.evaluate_js("window.handleProgress('Erro ao ler a linha acima')")
            print('Erro ao ler a linha acima')


    def obter_intersecoes(c, line):
        nonlocal count_plines, min_x, min_y, max_x, max_y, elevation_max, elevation_min, lines_not_evaluated, lines_evaluated, erros_encontrados
        try:
            count_plines+=1  
            if c.dxf.start[0]<min_x:
                min_x=c.dxf.start[0]
            if c.dxf.start[1]<min_y:
                min_y=c.dxf.start[1]
            if c.dxf.start[0]>max_x:
                max_x=c.dxf.start[0]
            if c.dxf.start[1]>max_y:
                max_y=c.dxf.start[1]
            if (c.dxf.start[0] < line['p1_corte_x'] and c.dxf.end[0] < line['p1_corte_x']) or (c.dxf.start[0] > line['p2_corte_x'] and c.dxf.end[0] > line['p2_corte_x']) or (c.dxf.start[1] < min(line['p1_corte_y'], line['p2_corte_y']) and c.dxf.end[1] < min(line['p1_corte_y'], line['p2_corte_y'])) or (c.dxf.start[1] > max(line['p1_corte_y'], line['p2_corte_y']) and c.dxf.end[1] > max(line['p1_corte_y'], line['p2_corte_y'])):
                lines_not_evaluated += 1      
            else:     
                lines_evaluated+=1             
                # p1_terreno = Point(c.dxf.start[0],c.dxf.start[1])
                # p2_terreno = Point(c.dxf.end[0],c.dxf.end[1])
                altura_terreno = c.dxf.start[2]
                # line_terreno=Segment(p1_terreno,p2_terreno)
                intersection=line['line_corte'].intersection(Segment((c.dxf.start[0], c.dxf.start[1]),(c.dxf.end[0],c.dxf.end[1])))
                if(intersection!=[]):
                    try:
                        pos_x = float(eval(str(intersection[0]).split('(')[1].split(')')[0].split(',')[0]))
                        pos_y = float(eval(str(intersection[0]).split('(')[1].split(')')[0].split(', ')[1]))
                        print('Intersecao em (%s, %s, %s)' % (pos_x, pos_y, altura_terreno))
                        window.evaluate_js(f"window.handleProgress('Intersecao em ({pos_x}, {pos_y}, {altura_terreno})')")
                        if altura_terreno < elevation_min and altura_terreno != 0:
                            elevation_min = altura_terreno
                        if altura_terreno > elevation_max:
                            elevation_max = altura_terreno
                        return [pos_x,pos_y,altura_terreno]
                    except:
                        erros_encontrados +=1
                        print('Erro na intersecao. Ponto descartado')
                        print(intersection)
                        window.evaluate_js(f"window.handleProgress('Erro na intersecao. Ponto descartado. {intersection}')")
                        return
        except:
            erros_encontrados +=1
            window.evaluate_js(f"window.handleProgress('Erro ao ler intersecao: {e.dxftype()}')")
            print('Erro ao ler intersecao: ')
            print(e.dxftype())
            print(e)
    
    msp = doc.modelspace()

    # Definir linhas de corte
    for e in [e for e in msp.query('LINE') if e.dxftype() == 'LINE' and e.dxf.layer==CORTE_LAYER]:
        if self.should_cancel:
            return None
        definir_linhas_de_corte(e)
            
    # Definir intersecoes
    for index, line in enumerate(linhas_de_corte):
        if self.should_cancel:
            return None
        try:
            intersecoes_da_linha = []
            output_dict = {}
            output_dict['p1_corte_x'] = line['p1_corte_x']
            output_dict['p1_corte_y'] = line['p1_corte_y']
            output_dict['p2_corte_x'] = line['p2_corte_x']
            output_dict['p2_corte_y'] = line['p2_corte_y']
            output_dict['p1_corte'] = line['p1_corte']
            output_dict['p2_corte'] = line['p2_corte']
            output_dict['line_corte'] = line['line_corte']
            output_dict['grid_length'] = line['grid_length']
            lines_to_read = [e for e in msp.query('LINE') if e.dxftype() == 'LINE' and e.dxf.layer==TERRENO_LAYER]
            for line_nr, e in enumerate(lines_to_read):
                window.evaluate_js(f"window.handlePercentageComplete('{line_nr / len(lines_to_read)}')")
                temp_intersection = obter_intersecoes(e, line)
                if temp_intersection != None:
                    intersecoes_da_linha.append(temp_intersection)
            intersecoes_da_linha.sort(reverse=False, key=sort_x)
            output_dict['intersecoes_da_linha'] = intersecoes_da_linha
            linhas_com_intersecao.append(output_dict)
        except:
            erros_encontrados += 1
            print('Erro ao ler intersecao acima')
            return None


    # Gerando o grid
    for index_line, line in enumerate(linhas_com_intersecao):
        if self.should_cancel:
            return None
        try:
            points_list = []
            intersections = line['intersecoes_da_linha']

            x_0 = max_x  + (max_x-min_x) * 1.15 
            
            # Codigo para multi grids, por enquanto desativado
            print('len(grid_heights): ' + str(len(grid_heights)))
            if len(grid_heights) > 0:
                total_grid_offset += grid_heights[-1] * 2
                print('Using grid_offset: ' + str(total_grid_offset))
            y_0 = (min_y + (max_y-min_y) / 2) - total_grid_offset
            grid_x0 = x_0
            grid_y0s = y_0
            points_list.append(Point(x_0,y_0))

            for index, point in enumerate(intersections):
                if self.should_cancel:
                    return None
                if index==0:
                    x = x_0 + N(line['p1_corte'].distance(Point(point[0],point[1])))
                    #print('Evaluating intersection #%s' % index)
                    y = y_0
                    p0 = Point(x,y)
                    points_list.append(p0)
                    # msp.add_line(p0, p1)
                if index > 0 and index < len(intersections):
                    #print('Evaluating intersection #%s' % index)
                    x_0 = N(str(points_list[-1]).split('2D(')[1].split(', ')[0])
                    y_0 = N(str(points_list[-1]).split(', ')[1].split(')')[0])
                    x = float(x_0 + abs(Point(point[0],point[1]).distance(Point(intersections[index-1][0],intersections[index-1][1]))))
                    y = y_0 + (point[2] - intersections[index-1][2]) * y_scale
                    p = Point(x,y)
                    points_list.append(p)
                    # msp.add_line(p0, p1)
                if index == len(intersections):
                    #print('Evaluating intersection #%s' % index)
                    x_0 = N(str(points_list[-1]).split('2D(')[1].split(', ')[0])
                    y_0 = N(str(points_list[-1]).split(', ')[1].split(')')[0])
                    x = float(x_0 + N(line['p2_corte'].distance(Point(point[0],point[1]))))
                    y = y_0
                    p = Point(x,y)
                    points_list.append(p)

            points_list.sort(key=sort_x)

            temp_str = ''
            
            window.evaluate_js(f"window.handlePercentageComplete('0.95')")
            window.evaluate_js(f"window.handleProgress('Gerando o Grid')")
            
            for index, point in enumerate(points_list):
                if self.should_cancel:
                    return None
                if index==0:
                    temp_str += str(point).split('2D')[0] + str(point).split('2D')[1]
                if index>0:
                    temp_str += ', ' + str(point).split('2D')[0] + str(point).split('2D')[1]

            # GRID
            doc.layers.new(name='GRID_AUTO_' + str(index_line), dxfattribs={'linetype': 'CONTINUOUS', 'color': GRID_COLOR_CODE})
            doc.layers.new(name='PROFILE_AUTO_' + str(index_line), dxfattribs={'linetype': 'CONTINUOUS', 'color': PROFILE_COLOR_CODE})
            grid_x1 = grid_x0 + math.ceil(line['grid_length']/x_distance) * x_distance
            grid_height = y_distance * math.ceil ((elevation_max - elevation_min)/y_distance) + y_distance
            temp_extra = math.ceil(elevation_min % y_distance)
            grid_y0 =  grid_y0s - ((intersections[0][2] - elevation_min) + temp_extra) * y_scale
            grid_y1 = grid_y0 + grid_height * y_scale
            grid_str='Point(grid_x0, grid_y0), Point(grid_x0, grid_y1), Point(grid_x1, grid_y1), Point(grid_x1,grid_y0), Point(grid_x0, grid_y0)'
            msp.add_polyline2d(eval(grid_str), dxfattribs={'layer': 'GRID_AUTO_' + str(index_line)})
            grid_heights.append(grid_height)
            range_x = math.ceil(line['grid_length']/x_distance)
            for i in range (1, range_x):
                if self.should_cancel:
                    return None
                temp_x=grid_x0+x_distance*i
                grid_strx='Point(temp_x, grid_y0), Point(temp_x, grid_y1)'
                msp.add_polyline2d(eval(grid_strx), dxfattribs={'layer': 'GRID_AUTO_' + str(index_line)})
                
                # Adding all points except zero and last point to grid X axis
                msp.add_text(str(int(i * x_distance)),
                            dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
                    ).set_placement((temp_x, grid_y0 - y_distance / 10), align=TextEntityAlignment.TOP_CENTER)
                
                # Adding zero to grid X axis
                if i == 1:
                    msp.add_text('0',
                            dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
                    ).set_placement((grid_x0,  grid_y0 - y_distance / 10) , align=TextEntityAlignment.TOP_CENTER)
                
                # Adding last value to grid X axis
                if i == range_x - 1:
                    msp.add_text(str((i + 1) * x_distance),
                            dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
                    ).set_placement((temp_x + x_distance,  grid_y0 - y_distance / 10), align=TextEntityAlignment.TOP_CENTER)
                    msp.add_text('(m)',
                            dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
                    ).set_placement((temp_x + x_distance + 0.1 * x_distance, grid_y0 - y_distance / 10), align=TextEntityAlignment.BOTTOM_RIGHT)

            range_y = math.ceil(grid_height/y_distance)
            for i in range(1, range_y):
                if self.should_cancel:
                    return None
                temp_y = grid_y0 + y_distance * i * y_scale
                altitude_atual = round(elevation_min + y_distance * i - elevation_min % y_distance)
                grid_stry='Point(grid_x0, temp_y), Point(grid_x1, temp_y)'
                msp.add_polyline2d(eval(grid_stry), dxfattribs={'layer': 'GRID_AUTO_' + str(index_line)})
                msp.add_text(str(int(altitude_atual)),
                            dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
                    ).set_placement((grid_x0 - 0.1 * x_distance, temp_y), align=TextEntityAlignment.MIDDLE_RIGHT)
                if i == 1:
                    msp.add_text(str(int(altitude_atual - y_distance)),
                            dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
                    ).set_placement((grid_x0 - 0.1 * x_distance, temp_y - (y_distance * y_scale)) , align=TextEntityAlignment.MIDDLE_RIGHT)
                if i == range_y - 1:
                    msp.add_text(str(int(altitude_atual + y_distance)),
                            dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
                    ).set_placement((grid_x0 - 0.1 * x_distance, temp_y + (y_distance * y_scale)), align=TextEntityAlignment.MIDDLE_RIGHT)
                    msp.add_text('Alt (m)',
                            dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
                    ).set_placement((grid_x0 - 0.1 * x_distance, temp_y + 1.5 * y_distance * y_scale), align=TextEntityAlignment.BOTTOM_RIGHT)

            msp.add_polyline2d(eval(temp_str), dxfattribs={'layer': 'PROFILE_AUTO_' + str(index_line)})
            grid_number += 1
        except Exception as e:
            erros_encontrados += 1
            print(e)
            print('ERRO AO ADICIONAR LINHA')
            window.evaluate_js(f"window.handleProgress('ERRO AO ADICIONAR LINHA')")

    time_elapsed = time.time() - time_start
    print('Linhas avaliadas: %s. Linhas nao avaliadas: %s' % (lines_evaluated, lines_not_evaluated))
    print('Cota minima: %s' % elevation_min)
    print('Cota maxima: %s' % elevation_max)
    print('Tempo decorrido: %s seconds' % time_elapsed)
    print('=========== ERROS ENCONTRADOS ===========')
    print('================= ' + str(erros_encontrados) + ' =================')

    window.evaluate_js(f"window.handleProgress('Linhas avaliadas: {lines_evaluated}. Linhas nao avaliadas: {lines_not_evaluated}')")
    window.evaluate_js(f"window.handleProgress('Cota minima: {elevation_min}')")
    window.evaluate_js(f"window.handleProgress('Cota maxima: {elevation_max}')")
    window.evaluate_js(f"window.handleProgress('Tempo decorrido: {time_elapsed} seconds')")
    window.evaluate_js(f"window.handleProgress('=========== ERROS ENCONTRADOS: {erros_encontrados} ===========')")
    window.evaluate_js(f"window.handleProgress('=========== Seu nome era B - I - N - G - O ===========')")
    window.evaluate_js(f"window.handlePercentageComplete('0.99')")
    
    try: 
        doc.saveas(OUTPUT_FILE_NAME)
        print('Documento salvo')
        with open(OUTPUT_FILE_NAME, "rb") as f:
            file_bytes = f.read()
            file_b64 = base64.b64encode(file_bytes).decode("utf-8")
        window.evaluate_js(f"window.handlePercentageComplete('1')")
        return {'file_data': file_b64, 'file_path': OUTPUT_FILE_NAME}
    except:
        erros_encontrados += 1
        print('Erro ao tentar salvar o documento')
        return None
