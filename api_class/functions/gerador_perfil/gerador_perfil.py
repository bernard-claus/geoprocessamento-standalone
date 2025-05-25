# um perfil de cada vez, deve estar em formato line_corte
# todas as cn em um so layer chamado terreno (maiuscula)
# ponto inicial do corte sempre o mais a esquerda
# conferir no final, pode estar espelhado
# NA JANELA DE COMANDO, DIGITAR 'python' (sem as aspas) PARA ENTRAR NO TERMINAL DO PYTHON
# COPIAR E COLAR O COMANDO ABAIXO NO TERMINAL DO PYTHON
#  exec(open(r'gerador_perfil_27_set_23.py').read())

# DATA - 27 DE SETEMBRO DE 2023
# INCLUI:
# Grid com texto
# Processa terreno no tipo LINE (menor chance de erro - apagando linhas desnecessarias torna o processamento muito mais rapido)
# Escala em Y configuravel

import ezdxf
from ezdxf.math import ABS_TOL
from ezdxf.enums import TextEntityAlignment
from sympy import Point, Line, Segment
from sympy import *
import time
import math
import tempfile
import base64
import io

def gerar_perfil_main(input_file_b64):
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
        if input_file_b64.startswith('data:'):
            input_file_b64 = input_file_b64.split(',', 1)[1]
        file_bytes = base64.b64decode(input_file_b64)
        file_obj = io.BytesIO(file_bytes)
        tmp.write(file_obj.read())
        tmp_path = tmp.name

    # CONFIGURE GRID:
    x_distance = 10
    y_distance = 2
    y_scale = 2

    GRID_COLOR_CODE = 254
    PROFILE_COLOR_CODE = 45
    OUTPUT_FILE_NAME = f'{''.join(tmp_path.split('.dxf'))}_SAIDA.dxf'
    CORTE_LAYER='PERFIL'
    TERRENO_LAYER='TERRENO'

    time_start = time.time()

    try:
        doc = ezdxf.readfile(tmp_path)
    except IOError:
        error = f'Not a DXF file or a generic I/O error.' 
        print(error)
        return { 'error': error }
    except ezdxf.DXFStructureError:
        error = f'Invalid or corrupted DXF file.'
        print(error)
        return { 'error': error }

    line_corte = Line((0,0),(0,1))
    p1_corte_x = 0
    p1_corte_y = 0
    p2_corte_x = 0
    p2_corte_y = 0
    p1_corte = Point(p1_corte_x,p1_corte_y)
    p2_corte= Point(p2_corte_x,p2_corte_y)
    intersections=[]
    points_list=[]
    poligono_corte = Polygon((0,0),(0,1),(1,1),(1,0))
    count_plines=0
    min_x=10000000000
    min_y=10000000000
    max_x=-100000000
    max_y=-100000000
    elevation_min = 100000000
    elevation_max = -100000000
    grid_length = 0
    lines_not_evaluated=0
    lines_evaluated=0
    # layers_terreno=[]
    # layers_corte=[]
    # numero_cortes=int(input('Digite o numero de cortes: '))
    # for i in range(1,numero_cortes+1):
    #     temp_layer_corte = input('-- Digite o nome do layer de corte ' + str(i) + ': ')
    #     layers_corte.append(temp_layer_corte)
    # numero_layers_terreno=int(input('Digite o numero de layers do terreno: '))
    # for i in range(1,numero_layers_terreno+1):
    #     temp_layer_name = input('-- Digite o nome do layer de terreno ' + str(i) + ': ')
    #     layers_terreno.append(temp_layer_name)
    # print('Configure o espaçamento do GRID: ')
    # espacamento_x = float(input('-- Digite o espaçamento em x: '))
    # espacamento_y = float(input('-- Digite o espaçamento em y: '))

    def print_entity(e):
        print("Linha de perfil no layer %s" % e.dxf.layer)
        print("Ponto inicial: %s" % e.dxf.start)
        print("Ponto final: %s" % e.dxf.end)
        nonlocal line_corte, p1_corte, p2_corte, p1_corte_x, p1_corte_y, p2_corte_x, p2_corte_y, poligono_corte, grid_length
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
        poligono_corte = Polygon((p1_corte_x,p1_corte_y),(p1_corte_x,p2_corte_y),(p2_corte_x,p2_corte_y),(p2_corte_x,p1_corte_y))

    def print_pline(c):
        nonlocal intersections, count_plines, min_x, min_y, max_x, max_y, elevation_max, elevation_min, lines_not_evaluated, lines_evaluated
        ##print("Reading %s #%s in layer: %s" % (e.dxftype(), count_plines, e.dxf.layer))
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
            if (c.dxf.start[0] < p1_corte_x and c.dxf.end[0] < p1_corte_x) or (c.dxf.start[0] > p2_corte_x and c.dxf.end[0] > p2_corte_x) or (c.dxf.start[1] < min(p1_corte_y, p2_corte_y) and c.dxf.end[1] < min(p1_corte_y, p2_corte_y)) or (c.dxf.start[1] > max(p1_corte_y,p2_corte_y) and c.dxf.end[1] > max(p1_corte_y,p2_corte_y)):
                lines_not_evaluated += 1      
            else:     
                lines_evaluated+=1             
                p1_terreno = Point(c.dxf.start[0],c.dxf.start[1])
                p2_terreno = Point(c.dxf.end[0],c.dxf.end[1])
                altura_terreno = c.dxf.start[2]
                line_terreno=Segment(p1_terreno,p2_terreno)
                intersection=line_corte.intersection(line_terreno)
                if(intersection!=[]):
                    try:
                        pos_x = float(eval(str(intersection[0]).split('(')[1].split(')')[0].split(',')[0]))
                        pos_y = float(eval(str(intersection[0]).split('(')[1].split(')')[0].split(', ')[1]))
                        print('Intersecao em (%s, %s, %s)' % (pos_x, pos_y, altura_terreno))
                        if altura_terreno < elevation_min and altura_terreno != 0:
                            elevation_min = altura_terreno
                        if altura_terreno > elevation_max:
                            elevation_max = altura_terreno
                        intersections.append([pos_x,pos_y,altura_terreno ])
                    except:
                        print('Erro na intersecao. Ponto descartado')
                        print(intersection)
                        return
        except:
            print('Erro lendo linha: ')
            print(c)
            print(c.dxftype())
            print(c.dxf.layer)
            print(c.dxf.start)
    

    msp = doc.modelspace()

    for e in msp:
        if e.dxftype() == 'LINE' and e.dxf.layer==CORTE_LAYER:
            print_entity(e)
            
    for e in msp:
        if e.dxftype() == 'LINE' and e.dxf.layer == TERRENO_LAYER:
            print_pline(e)

    def sort_x(e):
        return e[0]

    intersections.sort(reverse=False, key=sort_x)

    x_0 = max_x  + (max_x-min_x)*1.15 
    y_0 = min_y + (max_y-min_y)/2
    grid_x0 = x_0
    grid_y0s = y_0
    points_list.append(Point(x_0,y_0))

    for index, point in enumerate(intersections):
        if index==0:
            x = x_0 + N(p1_corte.distance(Point(point[0],point[1])))
            #print('Evaluating intersection #%s' % index)
            y = y_0
            p0 = Point(x,y)
            points_list.append(p0)
            # msp.add_line(p0, p1)
        if index>0 and index<len(intersections):
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
            x = float(x_0 + N(p2_corte.distance(Point(point[0],point[1]))))
            y = y_0
            p = Point(x,y)
            points_list.append(p)

    points_list.sort(key=sort_x)

    temp_str = ''

    for index, point in enumerate(points_list):
        if index==0:
            temp_str += str(point).split('2D')[0] + str(point).split('2D')[1]
        if index>0:
            temp_str += ', ' + str(point).split('2D')[0] + str(point).split('2D')[1]

    # NEW DOC FOR GRID
    new_doc = ezdxf.new("R2010")
    new_msp = new_doc.modelspace()

    # GRID
    new_doc.layers.new(name='GRID_AUTO', dxfattribs={'linetype': 'CONTINUOUS', 'color': GRID_COLOR_CODE})
    new_doc.layers.new(name='PROFILE_AUTO', dxfattribs={'linetype': 'CONTINUOUS', 'color': PROFILE_COLOR_CODE})
    grid_x1 = grid_x0 + math.ceil(grid_length/x_distance)*x_distance
    grid_height = y_distance * math.ceil ((elevation_max - elevation_min)/y_distance) + y_distance
    temp_extra = math.ceil(elevation_min % y_distance)
    grid_y0 =  grid_y0s - ((intersections[0][2] - elevation_min) - temp_extra) * y_scale
    grid_y1 = grid_y0 + grid_height * y_scale
    grid_str='Point(grid_x0, grid_y0), Point(grid_x0, grid_y1), Point(grid_x1, grid_y1), Point(grid_x1,grid_y0), Point(grid_x0, grid_y0)'
    new_msp.add_polyline2d(eval(grid_str), dxfattribs={'layer': 'GRID_AUTO'})

    range_x = math.ceil(grid_length/x_distance)
    for i in range (1, range_x):
        temp_x=grid_x0+x_distance*i
        grid_strx='Point(temp_x, grid_y0), Point(temp_x, grid_y1)'
        new_msp.add_polyline2d(eval(grid_strx), dxfattribs={'layer': 'GRID_AUTO'})
        new_msp.add_text(str(i * x_distance),
                    dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
            ).set_placement((temp_x, grid_y0 - y_distance / 10), align=TextEntityAlignment.TOP_CENTER)
        if i == 1:
            new_msp.add_text(str((i - 1) * x_distance),
                    dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
            ).set_placement((temp_x - x_distance, grid_y0 - y_distance / 10), align=TextEntityAlignment.TOP_CENTER)
        if i == range_x - 1:
            new_msp.add_text(str((i + 1) * x_distance),
                    dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
            ).set_placement((temp_x + x_distance, grid_y0 - y_distance / 10), align=TextEntityAlignment.TOP_CENTER)
            new_msp.add_text('Dist (m)',
                    dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
            ).set_placement((temp_x + 1.1 * x_distance, grid_y0 - y_distance / 10), align=TextEntityAlignment.TOP_LEFT)

    range_y = math.ceil(grid_height/y_distance)
    for i in range(1, range_y):
        temp_y = grid_y0+y_distance * i * y_scale
        altitude_atual = round(elevation_min + y_distance * i - elevation_min % y_distance)
        grid_stry='Point(grid_x0, temp_y), Point(grid_x1, temp_y)'
        new_msp.add_polyline2d(eval(grid_stry), dxfattribs={'layer': 'GRID_AUTO'})
        new_msp.add_text(str(altitude_atual),
                    dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
            ).set_placement((grid_x0 - 0.1 * x_distance, temp_y), align=TextEntityAlignment.MIDDLE_RIGHT)
        if i == 1:
            new_msp.add_text(str(altitude_atual - y_distance),
                    dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
            ).set_placement((grid_x0 - 0.1 * x_distance, temp_y - (y_distance * y_scale)) , align=TextEntityAlignment.MIDDLE_RIGHT)
        if i == range_y - 1:
            new_msp.add_text(str(altitude_atual + y_distance),
                    dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
            ).set_placement((grid_x0 - 0.1 * x_distance, temp_y + (y_distance * y_scale)), align=TextEntityAlignment.MIDDLE_RIGHT)
            new_msp.add_text('Alt (m)',
                    dxfattribs={'layer': 'GRID_AUTO_LEGENDA'}
            ).set_placement((grid_x0 - 0.1 * x_distance, temp_y + 1.5 * y_distance * y_scale), align=TextEntityAlignment.BOTTOM_RIGHT)

    new_msp.add_polyline2d(eval(temp_str), dxfattribs={'layer': 'PROFILE_AUTO'})

    time_elapsed = time.time() - time_start
    try: 
        new_doc.saveas(OUTPUT_FILE_NAME)
        with open(OUTPUT_FILE_NAME, "rb") as f:
            file_bytes = f.read()
            file_b64 = base64.b64encode(file_bytes).decode("utf-8")
        return { 'error': None, 'file_data': file_b64, 'info': {
            'linhas_avaliadas': lines_evaluated,
            'linhas_nao_avaliadas': lines_not_evaluated,
            'cota_minima': elevation_min,
            'cota_maxima': elevation_max,
            'tempo_decorrido': time_elapsed,
            'x_0': x_0,
            'y_0': y_0
        } }
    except:
        error = 'Erro salvando documento'
        return { 'error': error, 'output_file': OUTPUT_FILE_NAME }