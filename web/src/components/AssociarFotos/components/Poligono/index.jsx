import { useState } from 'react'
import { Box, Button, Grid } from '@mui/material'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import DownloadIcon from '@mui/icons-material/Download'
import EditIcon from '@mui/icons-material/Edit'
import ReportGmailerrorredIcon from '@mui/icons-material/ReportGmailerrorred'
import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye'


const Poligono = ({ fotosPoligono, fotoPorGcp, nomePoligono, ptosDeControle, selectedFolder }) => {
  // Cada poligono vai gerar um gcp list

  const [relativePositions, setRelativePositions] = useState([]) //  { gcp: 1, poligono: 'nenhum', lat: gcpLat, long: gcpLong, alt: gcpAlt, relX: 200, relY: 1500, file: 'DJI_0006.JPG' }
  const [text1, setText1] = useState('')

  const downloadGcp = async () => {
    const GCP_HEADER = '+proj=utm +zone=22 +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs\n'
    let gcp = GCP_HEADER

    for (let i = 0; i < relativePositions.length; i++) {
      for (const key of ['lat', 'long', 'alt', 'relX', 'relY', 'file']) {
        gcp += `${relativePositions[i][key]}`
        if (key === 'file') gcp += '\n'
        else gcp += '\t'
      }
    }

    if (window.pywebview?.api?.utils?.downloadTxt ?? false) {
      await window.pywebview.api.utils.downloadTxt(gcp)
    }
  }

  const handleEditarImagem = async (gcpId, foto, ptoGcp) => {
    if (window.pywebview?.api?.associar_fotos?.obter_posicao_relativa_do_pto_na_imagem ?? false) {
      const resp = await window.pywebview.api.associar_fotos.obter_posicao_relativa_do_pto_na_imagem(foto, selectedFolder, ptoGcp[0])
      const novoPonto = {
        gcp: gcpId,
        lat: ptoGcp[1],
        long: ptoGcp[2],
        alt: ptoGcp[3],
        relX: resp[0],
        relY: resp[1],
        file: foto
      }
      const novoRelativePositions = relativePositions.filter(rp => {
        if (rp.gcp === gcpId && rp.file === foto) return false
        return true
      })
      setRelativePositions([...novoRelativePositions, novoPonto])
    }
  }

  const handleVerImagem = async (foto, ptoGcp, matchingRelativePosition) => {
    setText1(`${typeof (matchingRelativePosition)} / ${JSON.stringify(matchingRelativePosition)}`)
    if (window.pywebview?.api?.associar_fotos?.ver_imagem ?? false) {
      if (matchingRelativePosition) await window.pywebview.api.associar_fotos.ver_imagem(foto, selectedFolder, ptoGcp[0], matchingRelativePosition.relX, matchingRelativePosition.relY)
      else await window.pywebview.api.associar_fotos.ver_imagem(foto, selectedFolder, ptoGcp[0], null, null)
    }
  }

  return (
    <Grid item size={12} sx={{ padding: '10px' }}>
      <Box
        sx={{
          borderRadius: '12px',
          border: '1px solid #ddd',
          padding: '16px',
          backgroundColor: '#f9f9f9',
          height: '100%',
          maxHeight: '800px',
          overflowY: 'auto',
          position: 'relative'
        }}
      >
        <h3 style={{ marginTop: 0, marginBottom: '16px' }}>{nomePoligono}</h3>
        <Button variant='contained' sx={{ position: 'absolute', top: '10px', right: '10px', textTransform: 'none' }} onClick={downloadGcp}>
          <DownloadIcon sx={{ fontSize: '14px' }} />
          gcp_list.txt
        </Button>
        {Object.entries(fotoPorGcp).map(([gcpId, gcpPhotos]) => {
          // Filter photos that exist in fotosPoligono
          const matchingPhotos = gcpPhotos.filter((photo) => fotosPoligono.includes(photo))
          const ptoGcp = ptosDeControle.find(p => p[0] == gcpId)
          return (
            <div key={gcpId} style={{ marginBottom: '16px' }}>
              <h4 style={{ marginBottom: '8px' }}>{`GCP ${gcpId} - (${ptoGcp[1]}, ${ptoGcp[2]})`}</h4>
              <div style={{ paddingLeft: '16px' }}>
                {matchingPhotos.map((foto) => {
                  const matchingRelativePosition = relativePositions.find(rp => rp.gcp == ptoGcp[0] && rp.file == foto)
                  return (
                    <div
                      key={`${gcpId}-${foto}`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        marginBottom: '8px',
                        gap: '8px',
                      }}
                    >
                      <Button
                        variant='contained'
                        onClick={() => handleVerImagem(foto, ptoGcp, matchingRelativePosition)}
                        sx={{ padding: 0, width: '24px', height: '24px' }}
                      >
                        <RemoveRedEyeIcon sx={{ fontSize: '14px' }} />
                      </Button>
                      <Button
                        variant='contained'
                        onClick={() => handleEditarImagem(gcpId, foto, ptoGcp)}
                        sx={{ padding: 0, width: '24px', height: '24px' }}
                      >
                        <EditIcon sx={{ fontSize: '14px' }} />
                      </Button>
                      <span>{foto}</span>
                      <span style={{ width: '400px' }}>{!matchingRelativePosition ? '' : `(${matchingRelativePosition.relX}, ${matchingRelativePosition.relY})`}</span>
                    </div>
                  ) })}
              </div>
            </div>
          )
        })}
        <p>{text1}</p>
        {relativePositions.map(r => <p>{JSON.stringify(r)}</p>)}
      </Box>
    </Grid>
  )
}

export default Poligono
