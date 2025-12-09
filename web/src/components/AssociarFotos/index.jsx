import { useState } from 'react'
import { Button, Grid, TextField } from '@mui/material'
import Poligono from './components/Poligono'

const AssociarFotos = () => {

  const [distanciaGcpFoto, setDistanciaGcpFoto] = useState(100)
  const [selectedFolder, setSelectedFolder] = useState('')
  const [selectedFiles, setSelectedFiles] = useState({ kml: '', gcp: '' })
  const [res, setRes] = useState([{}, {}, 0])
//   const [res, setRes] = useState([
// 	{ 	
// 		"1":["DJI_0935.JPG","DJI_0935.JPG"],
// 		"2":["DJI_0970.JPG","DJI_0970.JPG"]
// 	},
// 	{
// 		"nenhum":[],
// 		"Poligono Norte":["DJI_0970.JPG"],
// 		"Poligono Sul":["DJI_0935.JPG"]
// 	},
// 	2
// ])

  const fotoPorGcp = res[0]
  const poligonos = res[1]
  const nFotos = res[2]
  const ptosDeControle = res[3]

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
    if (window.pywebview?.api?.associar_fotos?.separar_fotos) {
      const response = await window.pywebview.api.associar_fotos.separar_fotos({
        CAMINHO: selectedFolder,
        CAMINHO_KML_POLIGONOS: selectedFiles.kml,
        CAMINHO_PTOS_TRACKMAKER: selectedFiles.gcp,
        distancia_max_entre_foto_e_gcp_em_metros: distanciaGcpFoto
      })
      setRes(response)
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
        height: '100%',
      }}
    >
      <div style={{ width: '80%', height: '100%', marginBottom: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'left', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left', width: '100%', height: '100%' }}>
          <span style={{ width: '120px' }}><strong>Pasta das fotos: </strong></span>
          {selectedFolder !== '' && (
            <span style={{ width: '1000px', overflowX: 'auto', marginLeft: '10px', whiteSpace: 'nowrap' }}>
              {selectedFolder}
            </span>
          )}
          <Button sx={{ padding: 0, textTransform: 'none', marginLeft: '10px' }} variant='outlined' onClick={handleSelectFolder}>{selectedFolder === '' ? 'Selecionar' : 'Trocar'}</Button>
        </div>
        {Object.keys(selectedFiles).map(type => (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left', width: '100%', height: '100%' }}>
            <span style={{ width: '120px' }}><strong>{`Arquivo ${type}:`}</strong></span>
            {selectedFolder !== '' && <span style={{ width: '1000px', overflowX: 'auto', marginLeft: '10px', whiteSpace: 'nowrap' }}>{selectedFiles[type]}</span>}
            <Button sx={{ padding: 0, textTransform: 'none', marginLeft: '10px' }} variant='outlined' onClick={() => handleSelectFile(type)}>{selectedFiles[type] === '' ? 'Selecionar' : 'Trocar'}</Button>
          </div>
        ))}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left', width: '100%', height: '100%' }}>
          <span style={{ width: '120px' }}><strong>Distancia maxima entre GCP e foto</strong></span>
          <TextField sx={{ marginLeft: '10px' }} value={distanciaGcpFoto} onChange={(e) => setDistanciaGcpFoto(e.target.value)} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'left', width: '100%', height: '100%' }}>
          <Button variant='contained' onClick={handleLerArquivos}>Ler arquivos</Button>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'start', justifyContent: 'center', width: '100%', height: '100%'}}>
        <span>{`${nFotos} imagens achadas na pasta`}</span>
        <span>{`${Object.keys(poligonos).length} poligonos achados no KML`}</span>
        <span>{`${Object.keys(fotoPorGcp).length} GCPs achados no csv`}</span>
      </div>
      <Grid container spacing={2} sx={{ width: '100%', heigth: 'auto' }} >
        {Object.keys(poligonos).map(poligono => (
          <Poligono
            nomePoligono={poligono}
            fotosPoligono={poligonos[poligono]}
            fotoPorGcp={fotoPorGcp}
            ptosDeControle={ptosDeControle}
            selectedFolder={selectedFolder}
          />
        ))}
      </Grid>
    </div>
  )
}

export default AssociarFotos
