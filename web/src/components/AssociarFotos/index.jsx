import { useState } from 'react'
import { Button, Grid, TextField } from '@mui/material'
import Poligono from './components/Poligono'
import { useLoadingContext } from '../../contexts/LoadingContext'

const AssociarFotos = () => {

  const { loading, setLoadingState } = useLoadingContext()

  const [distanciaGcpFoto, setDistanciaGcpFoto] = useState(100)
  const [selectedFolder, setSelectedFolder] = useState('')
  const [selectedFiles, setSelectedFiles] = useState({ kml: '', gcp: '' })
  const [res, setRes] = useState([{}, {}, 0])

  const fotoPorGcp = res[0]
  const poligonos = res[1]
  const nFotos = res[2]
  const ptosDeControle = res[3]
  const distanciasFotoPto = res[4]

  const [relativePositions, setRelativePositions] = useState(Object.fromEntries(Object.keys(poligonos).map(k => [k, []]))) //  { nenhum: [{ gcp: 1, poligono: 'nenhum', lat: gcpLat, long: gcpLong, alt: gcpAlt, relX: 200, relY: 1500, file: 'DJI_0006.JPG' }]}

  const handleSelectFolder = async () => {
    if (window.pywebview?.api?.utils?.select_folder) {
      const folderPath = await window.pywebview.api.utils.select_folder()
      if (folderPath) {
        setSelectedFolder(folderPath)
      }
    }
  }

  const handleSelectFile = async (type) => {
    if (window.pywebview?.api?.utils?.select_file) {
      const filePath = await window.pywebview.api.utils.select_file()
      if (filePath) {
        setSelectedFiles({ ...selectedFiles, [type]: filePath })
      }
    }
  }

  const handleLerArquivos = async () => {
    setLoadingState({ loading: true, text: 'Lendo a pasta e o arquivo' })
    if (window.pywebview?.api?.associar_fotos?.separar_fotos) {
      const response = await window.pywebview.api.associar_fotos.separar_fotos({
        CAMINHO: selectedFolder,
        CAMINHO_KML_POLIGONOS: selectedFiles.kml,
        CAMINHO_PTOS_TRACKMAKER: selectedFiles.gcp,
        distancia_max_entre_foto_e_gcp_em_metros: distanciaGcpFoto
      })
      setRes(response)
      setRelativePositions(Object.fromEntries(Object.keys(response[1]).map(k => [k, []])))
    }
    setLoadingState({ loading: false, text: '' })
  }

  const salvarSessao = async () => {
    if (window.pywebview?.api?.utils?.salvar_json) {
      const objSalvo = {
        distanciaGcpFoto,
        selectedFolder,
        selectedFiles,
        relativePositions,
      }
      await window.pywebview.api.utils.salvar_json(JSON.stringify(objSalvo))
    }
  }

  const carregarSessao = async () => {
    setLoadingState({ loading: true, text: 'Carregando sessão' })
    if (window.pywebview?.api?.utils?.carregar_json) {
      const json = await window.pywebview.api.utils.carregar_json()
      if (json.data ?? false) {
        const response = await window.pywebview.api.associar_fotos.separar_fotos({
          CAMINHO: json.data.selectedFolder,
          CAMINHO_KML_POLIGONOS: json.data.selectedFiles.kml,
          CAMINHO_PTOS_TRACKMAKER: json.data.selectedFiles.gcp,
          distancia_max_entre_foto_e_gcp_em_metros: json.data.distanciaGcpFoto
        })
        setSelectedFolder(json.data.selectedFolder)
        setSelectedFiles(json.data.selectedFiles)
        setRes(response)
        setRelativePositions(json.data.relativePositions)
        setDistanciaGcpFoto(json.data.distanciaGcpFoto)
      }
    }
    setLoadingState({ loading: false, text: '' })
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        width: '100%',
        height: '100%',
        position: 'relative'
      }}
    >
      <div style={{ position: 'absolute', width: '300px', top: 0, right: 0, display: 'flex', flexDirection: 'column' }}>
        <span><strong>CONTROLES</strong></span>
        <span>I, J, K, L - Setas direcionais</span>
        <span>S - Salvar e sair</span>
        <span>Z - Zerar</span>
        <span>M - Mascara (branco)</span>
        <span>________________</span>
        <span><strong>Use as checkboxes para usar uma imagem como referencia para as previsões</strong></span>
      </div>
      <div style={{ width: '80%', height: '100%', marginBottom: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'left', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left', width: '100%', height: '100%' }}>
          <Button variant='contained' sx={{ width: '250px', textTransform: 'none', marginRight: '10px' }} onClick={salvarSessao}>Salvar Sessão</Button>
          <Button variant='contained' sx={{ width: '250px', textTransform: 'none' }} onClick={carregarSessao}>Carregar Sessão</Button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left', width: '100%', height: '100%', overflowX: 'auto' }}>
          <Button sx={{ width: '120px', padding: 0, textTransform: 'none', marginRight: '10px' }} variant='outlined' onClick={handleSelectFolder}>{selectedFolder === '' ? 'Selecionar' : 'Trocar'}</Button>
          <span style={{ width: '120px' }}><strong>Pasta das fotos: </strong></span>
          {selectedFolder !== '' && (
            <span style={{ width: '1000px', overflowX: 'auto', marginLeft: '10px', whiteSpace: 'nowrap' }}>
              {selectedFolder}
            </span>
          )}
        </div>
        {Object.keys(selectedFiles).map(type => (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left', width: '100%', height: '100%', overflowX: 'auto' }}>
            <Button sx={{ width: '120px', padding: 0, textTransform: 'none', marginRight: '10px' }} variant='outlined' onClick={() => handleSelectFile(type)}>{selectedFiles[type] === '' ? 'Selecionar' : 'Trocar'}</Button>
            <span style={{ width: '120px' }}><strong>{`Arquivo ${type}:`}</strong></span>
            {selectedFolder !== '' && <span style={{ width: '1000px', overflowX: 'auto', marginLeft: '10px', whiteSpace: 'nowrap' }}>{selectedFiles[type]}</span>}
          </div>
        ))}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left', width: '100%', height: '100%' }}>
          <span style={{ whiteSpace: 'nowrap' }}><strong>Distancia maxima entre GCP e foto</strong></span>
          <TextField sx={{ marginLeft: '10px' }} value={distanciaGcpFoto} onChange={(e) => setDistanciaGcpFoto(e.target.value)} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left', width: '100%', height: '100%' }}>
          <Button variant='contained' onClick={handleLerArquivos}>Ler arquivos</Button>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'start', justifyContent: 'center', width: '80%', height: '100%' }}>
        <span>{`${nFotos} imagens achadas na pasta`}</span>
        <span>{`${Object.keys(poligonos).length} poligonos achados no KML`}</span>
        <span>{`${Object.keys(fotoPorGcp).length} GCPs achados no csv`}</span>
      </div>
      <Grid container spacing={2} sx={{ width: '80%', heigth: 'auto' }} >
        {Object.keys(poligonos).map(poligono => (
          <Poligono
            distanciasFotoPto={distanciasFotoPto}
            nomePoligono={poligono}
            fotosPoligono={poligonos[poligono]}
            fotoPorGcp={fotoPorGcp}
            ptosDeControle={ptosDeControle}
            selectedFolder={selectedFolder}
            relativePositions={relativePositions}
            setRelativePositions={setRelativePositions}
          />
        ))}
      </Grid>
    </div>
  )
}

export default AssociarFotos
