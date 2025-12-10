import { useEffect, useMemo, useState } from 'react'
import { useSnackbar } from 'notistack'
import { Box, Button, Checkbox, Grid, Tooltip } from '@mui/material'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import DownloadIcon from '@mui/icons-material/Download'
import EditIcon from '@mui/icons-material/Edit'
import ReportGmailerrorredIcon from '@mui/icons-material/ReportGmailerrorred'
import RemoveRedEyeIcon from '@mui/icons-material/RemoveRedEye'
import { useLoadingContext } from '../../../../contexts/LoadingContext'



const Poligono = ({ distanciasFotoPto, fotosPoligono, fotoPorGcp, nomePoligono, ptosDeControle, selectedFolder, relativePositions, setRelativePositions }) => {

  const { enqueueSnackbar } = useSnackbar()
  const { loading, setLoadingState } = useLoadingContext()

  const [referencias, setReferencias] = useState({}) // { [gcp]: ['DJI_0006.JPG'], etc... }
  const [predictions, setPredictions] = useState({}) // { [gcp]: { bestPoint: [x, y], score: float }, etc... }


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
      let predX, predY
      const fotoPred = predictions?.[gcpId]?.[foto] ?? undefined
      if (fotoPred) {
        predX = predictions?.[gcpId]?.[foto]?.[0] ?? undefined
        predY = predictions?.[gcpId]?.[foto]?.[1] ?? undefined
      }
      const resp = await window.pywebview.api.associar_fotos.obter_posicao_relativa_do_pto_na_imagem(foto, selectedFolder, ptoGcp[0], predX, predY)
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

  const handleCheckboxChange = (gcpId, foto, isChecked) => {
    setReferencias(prev => {
      const currentList = prev[gcpId] || []
      if (isChecked) {
        // Add foto to the list if not already present
        if (!currentList.includes(foto)) {
          return { ...prev, [gcpId]: [...currentList, foto] }
        }
        return prev
      }
      // Remove foto from the list
      return { ...prev, [gcpId]: currentList.filter(f => f !== foto) }
    })
  }

  const getButtonColor = (matchingRelativePosition) => {
    if (!!matchingRelativePosition && matchingRelativePosition.relX != 0 && matchingRelativePosition.relY != 0) return 'green'
  }

  const handleGetGcpPrediction = async (ptoGcp, foto = null) => {
    setLoadingState({ loading: true, text: 'Gerando previsao' })
    if (!referencias?.[ptoGcp[0]]?.length) {
      enqueueSnackbar('Pelo menos use 1 referência')
      return
    }

    if (window.pywebview?.api?.associar_fotos?.predizer_gcp_em_fotos ?? false) {
      // Process each GCP that has reference images
      const newPredictions = { ...predictions }
      if (!Object.keys(predictions).includes(ptoGcp[0])) {
        newPredictions[ptoGcp[0]] = {}
      }

      for (const [gcpId, fotosReferencia] of Object.entries(referencias)) {
        if (fotosReferencia && fotosReferencia.length > 0) {
          // Get all photos for this GCP
          const fotosParaPredizer = foto ? [foto] : fotoPorGcp[gcpId] || []

          // Get relative positions for this polygon
          const relativePositionsForGcp = relativePositions[nomePoligono].reduce((acc, rp) => {
            acc[rp.file] = { relX: rp.relX, relY: rp.relY }
            return acc
          }, {})

          try {
            const result = await window.pywebview.api.associar_fotos.predizer_gcp_em_fotos(
              fotosParaPredizer,
              selectedFolder,
              gcpId,
              relativePositionsForGcp,
              fotosReferencia
            )
            // Store results for each photo
            for (const [foto, predictionData] of Object.entries(result)) {
              if (predictionData.bestPoint) {
                newPredictions[gcpId][foto] = predictionData.bestPoint
              }
            }
          } catch (error) {
            console.error(`Error predicting GCP ${gcpId}:`, error)
          }
        }
      }
      setPredictions(newPredictions)
      setLoadingState({ loading: false, text: '' })
    }
  }

  const handleErasePrediction = (ptoGcp, foto) => {
    const newPredictions = { ...predictions }
    if (newPredictions?.[ptoGcp[0]]?.[foto] ?? false) {
      delete newPredictions[ptoGcp[0]][foto]
    }
    setPredictions(newPredictions)
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
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <h4 style={{ marginBottom: '8px' }}>{`GCP ${gcpId}: (${ptoGcp[1]}, ${ptoGcp[2]})`}</h4>
                {/* Possivel call para pegar previsao de tds imagens. Nao gostei mto */}
                {/* <Button onClick={() => handleGetGcpPrediction(ptoGcp)}>Predictions for all points</Button> */}
              </div>
              <div style={{ paddingLeft: '16px' }}>
                {matchingPhotos.sort().map((foto) => {
                  const matchingRelativePosition = relativePositions[nomePoligono].find(rp => rp.gcp == ptoGcp[0] && rp.file == foto)
                  const backgroundColor = getButtonColor(matchingRelativePosition)
                  const isChecked = referencias[gcpId]?.includes(foto) || false
                  const prediction = predictions[gcpId]?.[foto] ?? null
                  return (
                    <div
                      key={`${gcpId}-${foto}`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        marginBottom: '8px',
                        gap: '8px',
                        '&:hover': {
                          backgroundColor: 'lightGray'
                        }
                      }}
                    >
                      <Tooltip title='Selecionar essa imagem como referencia para prever o GCP em outras imagens'>
                        <Checkbox
                          checked={isChecked}
                          onChange={(e) => handleCheckboxChange(gcpId, foto, e.target.checked)}
                          sx={{ padding: 0 }}
                        />
                      </Tooltip>
                      <Tooltip title='Bota as coordenadas da imagem como (0, 0) - e assim ela é ignorada para o gcp_list.txt'>
                        <Button
                          variant='contained'
                          onClick={() => handleZerarImagem(foto, ptoGcp)}
                          sx={{ padding: 0, width: '24px', height: '24px', backgroundColor }}
                        >
                          Zerar
                        </Button>
                      </Tooltip>
                      <Tooltip title='Ver a imagem. Aqui o clique não faz nada. Se já foi selecionado um GCP, ele vai aparecer no meio de um circulo'>
                        <Button
                          variant='contained'
                          onClick={() => handleVerImagem(foto, ptoGcp, matchingRelativePosition)}
                          sx={{ padding: 0, width: '24px', height: '24px', backgroundColor }}
                        >
                          <RemoveRedEyeIcon sx={{ fontSize: '14px' }} />
                        </Button>
                      </Tooltip>
                      <Tooltip title='Editar posicao relativa do GCP nesta imagem. Se existe uma previsao ela vai aparecer no centro de um circulo'>
                        <Button
                          variant='contained'
                          onClick={() => handleEditarImagem(gcpId, foto, ptoGcp)}
                          sx={{ padding: 0, width: '24px', height: '24px', backgroundColor }}
                        >
                          <EditIcon sx={{ fontSize: '14px' }} />
                        </Button>
                      </Tooltip>
                      <span><strong>{foto}</strong></span>
                      {distanciasFotoPto?.[ptoGcp[0]]?.[foto] && <span>{`${distanciasFotoPto?.[ptoGcp[0]]?.[foto] ?? ''} m`}</span>}
                      <span style={{ width: '100px' }}>{!matchingRelativePosition ? '' : `(${matchingRelativePosition.relX}, ${matchingRelativePosition.relY})`}</span>
                      <div style={{ width: '50px' }}>
                        {!!matchingRelativePosition && matchingRelativePosition.relX != 0 && matchingRelativePosition.relY != 0 && <CheckCircleOutlineIcon sx={{ color: 'green' }}/>}
                        {!!matchingRelativePosition && matchingRelativePosition.relX == 0 && matchingRelativePosition.relY == 0 && <ReportGmailerrorredIcon sx={{ color: '#ffc400ff' }}/>}
                      </div>
                      <Tooltip title='Prevê um ponto semelhante aos selecionados nas imagens usadas como referencia (as que tem o checkbox marcado)'>
                        <Button
                          variant='contained'
                          onClick={() => handleGetGcpPrediction(ptoGcp, foto)}
                          sx={{ padding: 0, width: '24px', height: '24px', backgroundColor }}
                        >
                          Prever
                        </Button>
                      </Tooltip>
                      {!!prediction && <span>{JSON.stringify(prediction)}</span>}
                      {!!prediction && (
                        <Button
                          variant='contained'
                          onClick={() => handleErasePrediction(ptoGcp, foto)}
                          sx={{ padding: 0, width: '24px', height: '24px', backgroundColor }}
                        >
                          Apagar
                        </Button>
                      )}
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
