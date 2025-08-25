import webview
import shapefile

def msg_front(message: str):
    window = webview.windows[0]
    window.evaluate_js(f"window.handleProgress('{message}')")

def percentage_front(percent: int):
    window = webview.windows[0]
    window.evaluate_js(f"window.handlePercentageComplete('{percent}')")

def get_shapefile_vertices(self, shp_path):
    percentage_front(20)
    ok = False
    # Setting shape file. Attempt encoding ISO8859-1 and if it does not work try utf-8
    try:
        percentage_front(40)
        msg_front('Testando encoding ISO8859-1')
        shape_read = shapefile.Reader(shp_path, encoding='ISO8859-1')
        msg_front('Sucesso com encoding ISO8859-1')
        ok = True
    except Exception as e:
        print(e)
        msg_front('Erro com encoding ISO8859-1.')
        
    try:
        if not ok:
            percentage_front(60)
            msg_front('Testando encoding UTF-8')
            shape_read = shapefile.Reader(shp_path, encoding='utf-8')
            msg_front('Sucesso com encoding UTF-8')
    except Exception as e:
        print(e)
        msg_front('Erro com encoding UTF-8.')
        msg_front('Abortando')
        return []
    
    feature = shape_read.shapeRecords()[0]
    first = feature.shape.__geo_interface__
    
    percentage_front(70)
    
    try:
        ret = first['coordinates'][0]
        ret_final = [[p[0], p[1]] for p in ret]
        msg_front('Vertices obtidos com sucesso')
        percentage_front(100)
        for index, point in enumerate(first['coordinates'][0]):
            msg_front(str(index) + ' ' + str(point))    		
        return ret_final
    except Exception:
        return []

def gerar_shapefile(vertices: list, file_path: str):
    try:
        new_array = [(p[0], p[1]) for p in vertices]
        shape_write = shapefile.Writer(file_path.split('.shp')[0] + '_vertices.shp')
        percentage_front(20)
        shape_write.field('vertices','C')
        index_secundario = 0
        for index, i in enumerate(new_array):
            if (index==0):
                index_secundario = index_secundario + 1
                vertice_name = 'V' + str(index_secundario)
                shape_write.record(vertice_name)
                shape_write.point(float(i[0]),float(i[1]))
                msg_front(f'Lendo {vertice_name}')
            if (index>0):
                percentage_front(round(20 + (index / len(new_array) * 80)))
                if(new_array[index][0]!=new_array[index-1][0] and new_array[index][1]!=new_array[index-1][1]):
                    index_secundario = index_secundario + 1
                    vertice_name = 'V' + str(index_secundario)
                    shape_write.record(vertice_name)
                    shape_write.point(float(i[0]),float(i[1]))
                    msg_front(f'Lendo {vertice_name}')
        shape_write.close()
        percentage_front(100)
        msg_front('Concluido. os arquivos novos se encontram na mesma pasta')
        return True
    except Exception as e:
        print(e)
        return False