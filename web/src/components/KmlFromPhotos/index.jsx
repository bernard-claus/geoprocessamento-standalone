import { useState } from 'react'
import { useSnackbar } from 'notistack'
import { Button } from '@mui/material'
import { useLoadingContext } from '../../contexts/LoadingContext'

const KmlFromPhotos = () => {
  const { setLoadingState } = useLoadingContext()
  const { enqueueSnackbar } = useSnackbar()
  const [savedPath, setSavedPath] = useState(null)
  const [selectedFolder, setSelectedFolder] = useState('')
  const [kmlData, setKmlData] = useState(null)
  const [kmlFileName, setKmlFileName] = useState('coordenadas_das_fotos.kml')

  const handleSelectFolder = async () => {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.utils.select_folder) {
      const folderPath = await window.pywebview.api.utils.select_folder()
      if (folderPath) {
        setSelectedFolder(folderPath)
      }
    }
  }

  const run = async () => {
    if (!selectedFolder) {
      enqueueSnackbar('Selecione uma pasta primeiro', { variant: 'warning' })
      return
    }
    setLoadingState({ loading: true, text: 'Gerando o KML' })
    enqueueSnackbar('Gerando o KML', { variant: 'info' })
    try {
      const res = await window.pywebview.api.kml.generate_kml_from_photos(selectedFolder)
      if (res && res.success) {
        enqueueSnackbar('KML gerado com sucesso', { variant: 'success' })
        setKmlData(res.file_data)
        setKmlFileName(res.file_name || 'coordenadas_das_fotos.kml')
        setSavedPath(null)
      } else {
        enqueueSnackbar('Erro ao gerar o KML', { variant: 'error' })
      }
      setLoadingState({ loading: false, text: '' })
    } catch (e) {
      enqueueSnackbar('Erro ao gerar o KML', { variant: 'error' })
      setLoadingState({ loading: false, text: '' })
    }
  }

  const handleSaveKml = async () => {
    if (!kmlData) return
    const res = await window.pywebview.api.kml.save_kml(kmlData, kmlFileName)
    if (res && res.success && res.saved_path) {
      setSavedPath(res.saved_path)
      enqueueSnackbar('Arquivo salvo com sucesso', { variant: 'success' })
    } else {
      enqueueSnackbar('Erro ao salvar o arquivo', { variant: 'error' })
    }
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
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'flex-start', width: '80%', }}>
        <ul style={{ fontSize: '18px' }}>
          <li><span>Selecione uma pasta contendo imagens de drone (elas devem ter coordenadas GPS)</span></li>
          <li><span>Clique em gerar para gerar um KML com os pontos onde as imagens foram tiradas</span></li>
        </ul>
      </div>
      <div style={{ margin: '100px 0 100px 0', width: '100%', display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'center' }}>
        <Button variant='outlined' onClick={handleSelectFolder} style={{ marginRight: 16 }}>
          Selecionar pasta de fotos
        </Button>
        <span style={{ fontSize: 15, color: selectedFolder ? 'green' : 'gray' }}>{selectedFolder || 'Nenhuma pasta selecionada'}</span>
      </div>
      <Button sx={{ width: '300px' }} disabled={!selectedFolder} variant='contained' onClick={run}>Gerar KML</Button>
      <Button sx={{ width: '300px' }} disabled={!kmlData} variant='contained' style={{ marginTop: 8 }} onClick={handleSaveKml}>
        Salvar KML
      </Button>
      <Button sx={{ width: '300px' }} disabled={!savedPath} variant='outlined' style={{ marginTop: 8 }} onClick={() => window.pywebview.api.utils.open_in_explorer(savedPath)}>
        Abrir pasta do arquivo KML
      </Button>
    </div>
  )
}

export default KmlFromPhotos
