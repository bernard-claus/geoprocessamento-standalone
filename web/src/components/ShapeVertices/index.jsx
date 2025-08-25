import { useRef, useState } from 'react'
import { useSnackbar } from 'notistack'
import ReactECharts from 'echarts-for-react'
import FileOpenIcon from '@mui/icons-material/FileOpen'
import FolderOpenIcon from '@mui/icons-material/FolderOpen'
import GpsFixedIcon from '@mui/icons-material/GpsFixed'
import SaveIcon from '@mui/icons-material/Save'
import SwapHorizIcon from '@mui/icons-material/SwapHoriz'
import { Button, Stack } from '@mui/material'
import { useLoadingContext } from '../../contexts/LoadingContext'
import CircularProgressDetermined from '../CircularProgressDetermined'

const ShapeVertices = () => {

  const { loading, setLoadingState } = useLoadingContext()
  const { enqueueSnackbar } = useSnackbar()

  const [filePath, setFilePath] = useState('')
  const [messages, setMessages] = useState([])
  const [percComplete, setPercComplete] = useState(99)
  const [finished, setFinished] = useState(false)
  const [savedPath, setSavedPath] = useState(null)
  const [vertices, setVertices] = useState([])
  const [option, setOption] = useState({
    xAxis: { show: false },
    yAxis: { show: false },
    series: [{ data: [], type: 'line' }],
    dataZoom: [{ type: 'inside', xAxisIndex: 0, yAxisIndex: 0, filterMode: 'none' }],
  })

  const chartRef = useRef(null)

  const reorderList = (array, firstPoint) => {
    if (!Array.isArray(array) || array.length === 0) return []
    const n = array.length
    if (firstPoint <= 0 || firstPoint >= n) return array
    const newArray = [...array.slice(1)] // Retirar o primeiro ponto que é repetido com o ultimo
    const orederedArray = [...newArray.slice(firstPoint - 1), ...newArray.slice(0, firstPoint - 1)]
    return [...orederedArray, orederedArray[0]] // repetir o primeiro ponto
  }

  const inverterVertices = () => {
    const array = [...option.series[0].data]
    const reveresedArray = [...array.reverse()]
    setOption({
      ...option,
      series: [{ ...option.series[0], data: reveresedArray }],
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          const ind = params.dataIndex
          const matchingPoint = reveresedArray[ind]
          return `
            <b>Ponto:</b> ${ind}
            <br>
            <b>Lat:</b> ${matchingPoint[0]}
            <br>
            <b>Long:</b> ${matchingPoint[1]}`
        }
      }
    })
    setVertices([...vertices.reverse()])
  }

  const handleChartClick = (params) => {
    if (params && params.data) {
      // Dummy function call with clicked point data
      setMessages(prev => [`Ponto inicial: ${params.dataIndex} (${JSON.stringify(params.data)})`, ...prev])
      const reorderedData = reorderList(option.series[0].data, params.dataIndex)
      setOption({
        ...option,
        series: [{
          ...option.series[0],
          data: reorderedData
        }],
        tooltip: {
          trigger: 'item',
          formatter: (_) => {
            const ind = params.dataIndex
            const matchingPoint = reorderedData[ind]
            return `
              <b>Ponto:</b> ${ind}
              <br>
              <b>Lat:</b> ${matchingPoint[0]}
              <br>
              <b>Long:</b> ${matchingPoint[1]}`
          }
        }
      })
      setVertices(reorderList(vertices, params.dataIndex))
    }
  }

  const onEvents = {
    click: handleChartClick,
  }

  const gerarNovoArquivo = async () => {
    setLoadingState({ loading: true, text: 'Obtendo vertices' })
    try {
      const res = await window.pywebview.api.read_shapefile.gerar_arquivo(vertices, filePath)
      if (res) {
        setFinished(true)
      }
    } catch (e) {
      enqueueSnackbar('Erro gerando arquivos', { variant: 'error' })
    } finally {
      setLoadingState({ loading: false, text: '' })
    }
  }

  const getVertices = async () => {
    setLoadingState({ loading: true, text: 'Obtendo vertices' })
    try {
      const folder = `${filePath.split('\\').slice(0, -1).join('\\')}\\`
      setSavedPath(folder)
      const res = await window.pywebview.api.read_shapefile.get_vertices(filePath)
      if (Array.isArray(res)) setVertices(res)
      const minLat = Math.min(...res.map(p => p[0]))
      const minLng = Math.min(...res.map(p => p[1]))

      const normalizedPoints = res.map(p => [
        p[0] - minLat,
        p[1] - minLng
      ])
      setOption({
        ...option,
        series: [{
          data: normalizedPoints,
          type: 'line',
          label: {
            show: true,
            formatter: (params) => `${params.dataIndex}`
          } }],
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            const ind = params.dataIndex
            const matchingPoint = res[ind]
            return `
              <b>Ponto:</b> ${ind}
              <br>
              <b>Lat:</b> ${matchingPoint[0]}
              <br>
              <b>Long:</b> ${matchingPoint[1]}`
          }
        }
      })
      enqueueSnackbar('Vertices obtidos com sucesso', { variant: 'success' })
      setLoadingState({ loading: false, text: '' })
    } catch (e) {
      enqueueSnackbar('Erro ao obter vertices. Verifique o arquivo', { variant: 'error' })
      setLoadingState({ loading: false, text: '' })
    } finally {
      setPercComplete(0)
    }
  }

  const handleSelectFile = async () => {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.utils.select_file) {
      const shpPath = await window.pywebview.api.utils.select_file()
      if (shpPath) {
        setFilePath(shpPath)
      }
    }
  }

  window.handleProgress = (msg) => {
    setMessages(prev => [msg, ...prev])
  }

  window.handlePercentageComplete = (msg) => {
    setPercComplete(parseInt(msg))
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        width: '100%',
        height: '100%'
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'flex-start', width: '80%', height: '100%', paddingLeft: '20px' }}>
        <ul style={{ fontSize: '18px' }}>
          <li><span>O programa irá gerar os vértices nas extremidades das linhas</span></li>
          <li><span>1 - Selecionar um arquivo shapefile</span></li>
          <li><span>2 - Selecionar o ponto que deve ser o primeiro ponto</span></li>
          <li><span>3 - Verificar se os pontos estão na ordem certa, ou devem inverter</span></li>
        </ul>
      </div>
      <div style={{ width: '80%', height: '100%', marginBottom: '20px', display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'center' }}>
        <Button variant='outlined' onClick={handleSelectFile} style={{ marginRight: 16 }}>
          Selecionar arquivo shp
          <FileOpenIcon sx={{ marginLeft: '10px' }} />
        </Button>
      </div>
      <Button disabled={filePath === ''} variant='contained' onClick={() => getVertices()}>
        Obter vertices
        <GpsFixedIcon sx={{ marginLeft: '10px' }} />
      </Button>
      <div style={{ position: 'relative', display: 'flex', flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'flex-start', width: '80%' }}>
        <Stack spacing={3} sx={{ width: '20%', marginTop: '40px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', height: '400px', overflowY: 'scroll', border: '1px solid black', borderRadius: '10px', padding: '20px', width: '100%' }}>
            {messages.map(m => <span key={`${m}`}>{m}</span>)}
          </div>
          {/* !!finished */}
          {true && (
            <>
              <Button disabled={!vertices.length} fullWidth variant='contained' onClick={() => gerarNovoArquivo()}>
                Gerar novo arquivo
                <SaveIcon sx={{ marginLeft: '10px' }} />
              </Button>
              <Button fullWidth disabled={!savedPath || !finished} variant='contained' style={{ marginTop: 8 }} onClick={() => window.pywebview.api.utils.open_in_explorer(savedPath)}>
                Abrir pasta do arquivo
                <FolderOpenIcon sx={{ marginLeft: '10px' }} />
              </Button>
              {/* !!vertices.length && */}
            </>
          )}
        </Stack>
        {/* !!vertices.length */}
        {true && (
          <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '80%', margin: '20px' }}>
            <span style={{ fontSize: '18px', margin: '20px 0' }}>Clique no ponto que será o ponto zero</span>
            <Button
              variant='contained'
              onClick={() => inverterVertices()}
              sx={{ position: 'absolute', top: '10px', right: 0 }}
              disabled={!vertices.length}
            >
              Inverter Seleção
              <SwapHorizIcon sx={{ marginLeft: '10px' }} />
            </Button>
            <ReactECharts
              ref={chartRef}
              option={option}
              notMerge
              style={{ height: '600px', width: '100%' }}
              onEvents={onEvents}
            />
          </div>
        )}
        {loading && (
          <CircularProgressDetermined value={percComplete} boxSx={{ position: 'absolute', top: -20, left: 0 }} />
        )}
      </div>
    </div>
  )
}

export default ShapeVertices
