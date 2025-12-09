import { useState } from 'react'
import { Box, Button, Grid } from '@mui/material'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import DownloadIcon from '@mui/icons-material/Download'
import EditIcon from '@mui/icons-material/Edit'
import ReportGmailerrorredIcon from '@mui/icons-material/ReportGmailerrorred'
import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye'


const Poligono = ({ fotosPoligono, fotoPorGcp, nomePoligono, ptosDeControle, selectedFolder, relativePositions, setRelativePositions }) => {

  // Cada poligono vai gerar um gcp list
  const downloadGcp = async () => {
    const GCP_HEADER = '+proj=utm +zone=22 +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs\n'
    let gcp = GCP_HEADER

    for (let i = 0; i < relativePositions[nomePoligono].length; i++) {
      const thisRelativePosition = relativePositions[nomePoligono][i]
      // Pular os (0, 0)
      if (thisRelativePosition.relX == 0 && thisRelativePosition.relY == 0) continue
      for (const key of ['lat', 'long', 'alt', 'relX', 'relY', 'file']) {
        gcp += `${thisRelativePosition[key]}`
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
      const novoRelativePositions = relativePositions[nomePoligono].filter(rp => {
        if (rp.gcp === gcpId && rp.file === foto) return false
        return true
      })
      setRelativePositions({ ...relativePositions, [nomePoligono]: [...novoRelativePositions, novoPonto] })
    }
  }

  const handleVerImagem = async (foto, ptoGcp, matchingRelativePosition) => {
    if (window.pywebview?.api?.associar_fotos?.ver_imagem ?? false) {
      if (matchingRelativePosition) await window.pywebview.api.associar_fotos.ver_imagem(foto, selectedFolder, ptoGcp[0], matchingRelativePosition.relX, matchingRelativePosition.relY)
      else await window.pywebview.api.associar_fotos.ver_imagem(foto, selectedFolder, ptoGcp[0], null, null)
    }
  }

  const handleZerarImagem = (foto, ptoGcp) => {
    const novoRelativePosition = relativePositions[nomePoligono].map(rp => {
      if (rp.gcp === ptoGcp[0] && rp.file === foto) {
        return { ...rp, relX: '0', relY: '0' }
      }
      return rp
    })
    setRelativePositions({ ...relativePositions, [nomePoligono]: novoRelativePosition })
  }

  const getButtonColor = (matchingRelativePosition) => {
    if (!!matchingRelativePosition && matchingRelativePosition.relX != 0 && matchingRelativePosition.relY != 0) return 'green'
    if (!!matchingRelativePosition && matchingRelativePosition.relX == 0 && matchingRelativePosition.relY == 0) return '#ceaf00'
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
        <h3 style={{ marginTop: 0, marginBottom: '16px' }}>{`Poligono: ${nomePoligono}`}</h3>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'absolute', top: '10px', right: '10px' }}>
          <Button variant='contained' sx={{textTransform: 'none' }} onClick={downloadGcp}>
            <DownloadIcon sx={{ fontSize: '14px' }} />
            gcp_list.txt
          </Button>
          <p style={{ maxWidth: '100px' }}>Todas fotos com posição relativa (0, 0) serão desconsiderados</p>
        </div>
        {Object.entries(fotoPorGcp).map(([gcpId, gcpPhotos]) => {
          // Filter photos that exist in fotosPoligono
          const matchingPhotos = gcpPhotos.filter((photo) => fotosPoligono.includes(photo))
          const ptoGcp = ptosDeControle.find(p => p[0] == gcpId)
          return (
            <div key={gcpId} style={{ marginBottom: '16px' }}>
              <h4 style={{ marginBottom: '8px' }}>{`GCP ${gcpId}: (${ptoGcp[1]}, ${ptoGcp[2]})`}</h4>
              <div style={{ paddingLeft: '16px' }}>
                {matchingPhotos.map((foto) => {
                  const matchingRelativePosition = relativePositions[nomePoligono].find(rp => rp.gcp == ptoGcp[0] && rp.file == foto)
                  const backgroundColor = getButtonColor(matchingRelativePosition)
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
                        onClick={() => handleZerarImagem(foto, ptoGcp)}
                        sx={{ padding: 0, width: '24px', height: '24px', backgroundColor }}
                      >
                        Zerar
                      </Button>
                      <Button
                        variant='contained'
                        onClick={() => handleVerImagem(foto, ptoGcp, matchingRelativePosition)}
                        sx={{ padding: 0, width: '24px', height: '24px', backgroundColor }}
                      >
                        <RemoveRedEyeIcon sx={{ fontSize: '14px' }} />
                      </Button>
                      <Button
                        variant='contained'
                        onClick={() => handleEditarImagem(gcpId, foto, ptoGcp)}
                        sx={{ padding: 0, width: '24px', height: '24px', backgroundColor }}
                      >
                        <EditIcon sx={{ fontSize: '14px' }} />
                      </Button>
                      <span>{foto}</span>
                      <span style={{ width: '100px' }}>{!matchingRelativePosition ? '' : `(${matchingRelativePosition.relX}, ${matchingRelativePosition.relY})`}</span>
                      {!!matchingRelativePosition && matchingRelativePosition.relX != 0 && matchingRelativePosition.relY != 0 && <CheckCircleOutlineIcon sx={{ color: 'green' }}/>}
                      {!!matchingRelativePosition && matchingRelativePosition.relX == 0 && matchingRelativePosition.relY == 0 && <ReportGmailerrorredIcon sx={{ color: '#ceaf00' }}/>}
                    </div>
                  ) })}
              </div>
            </div>
          )
        })}
      </Box>
    </Grid>
  )
}

export default Poligono
