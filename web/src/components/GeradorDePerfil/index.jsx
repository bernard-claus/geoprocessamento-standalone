import { useState } from 'react'
import { useSnackbar } from 'notistack'
import { Button, Stack, TextField } from '@mui/material'
import DragAndDropFiles from '../DragAndDropFiles'
import { useLoadingContext } from '../../contexts/LoadingContext'
import { INPUT_FIELDS } from './constants/inputFields'
import CircularProgressDetermined from '../CircularProgressDetermined'

const GeradorDePerfil = () => {

  const { loading, setLoadingState } = useLoadingContext()
  const { enqueueSnackbar } = useSnackbar()

  const [files, setFiles] = useState([])
  const [messages, setMessages] = useState([])
  const [percComplete, setPercComplete] = useState(0)
  const [result, setResult] = useState(null)
  const [savedPath, setSavedPath] = useState(null)

  // result.file_data is the base64 string from the backend
  const downloadDxf = async () => {
    const res = await window.pywebview.api.perfil.save_dxf(result.file_data, files[0].name.split('.dxf').join(''))
    if (res && res.success && res.saved_path) {
      setSavedPath(res.saved_path)
    }
  }

  const run = async () => {
    setLoadingState({ loading: true, text: 'Gerando o perfil' })
    enqueueSnackbar('Gerando o perfil', { variant: 'info' })
    try {
      const file = files[0]
      const reader = new FileReader()
      reader.onload = async (e) => {
        const fileData = e.target.result
        const inputs = Object.fromEntries(INPUT_FIELDS.map(i => {
          const val = document.getElementById(i.name).value
          return [i.name, val]
        }))
        // CHANGED: Use window.pywebview.api.perfil.gerar_perfil_multicortes
        const res = await window.pywebview.api.perfil.gerar_perfil_multicortes(fileData, inputs)
        if (res === null) throw new Error('Something went wrong')
        enqueueSnackbar('Perfil gerado com sucesso', { variant: 'success' })
        setResult(res)
        setLoadingState({ loading: false, text: '' })
      }
      reader.readAsDataURL(file)
    } catch (e) {
      enqueueSnackbar('Erro ao gerar o perfil. Verifique o arquivo', { variant: 'error' })
      setLoadingState({ loading: false, text: '' })
    }
  }

  window.handleProgress = (msg) => {
    setMessages(prev => [msg, ...prev])
  }

  window.handlePercentageComplete = (msg) => {
    setPercComplete(parseInt(parseFloat(msg) * 0.9 * 100))
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
          <li><span>Deixar apenas uma linha de perfil por arquivo (se tiver mais de uma, apenas 1 será lida)</span></li>
          <li><span>Deixar o terreno inteiro em tipo LINE (nao usar POLYLINE)</span></li>
          <li><span>Deixar a linha de corte no layer com o nome configurado ao lado</span></li>
          <li><span>Deixar todo o terreno no layer com o nome configurado ao lado</span></li>
          <li><span>Verificar se nao tem linhas com altitude = 0 nos extremos</span></li>
          <li><span>Sempre o perfil é gerado da esquerda para a direita. Para arrumar, tem que fazer mirror depois de pronto</span></li>
          <li><span>De preferencia, fazer um arquivo separado só com a linha de corte e as linhas que intersectam ela (o resto do terreno pode ser descartado pois não é usado) - isso diminui bastante o tempo de processamento</span></li>
        </ul>
      </div>
      <div style={{ width: '80%', height: '100%', marginBottom: '20px', display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '50%', height: '100%' }}>
          <DragAndDropFiles files={files} setFiles={setFiles} width='100%' />
        </div>
        <Stack>
          {INPUT_FIELDS.map(field => (
            <Stack direction='row' sx={{ justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }} key={field.id}>
              <span>{field.titulo}</span>
              <TextField defaultValue={field.standardValue} id={field.name} sx={{ '& input': { padding: '2px 2px 2px 10px' }, margin: '0 20px 0 10px' }} />
            </Stack>
          ))}
        </Stack>
      </div>
      <Button disabled={!files.length} variant='contained' onClick={() => run()}>Gerar o perfil</Button>
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '80%' }}>
        <div style={{ display: 'flex', flexDirection: 'column', height: '200px', overflowY: 'scroll', border: '1px solid black', borderRadius: '10px', padding: '20px', width: '100%', margin: '20px' }}>
          {messages.map((m, i) => <span key={`${m}`}>{m}</span>)}
        </div>
        {loading && (
          <CircularProgressDetermined value={percComplete} boxSx={{ position: 'absolute', bottom: -30, right: 30 }} />
        )}
      </div>
      <Button disabled={!result} variant='contained' onClick={() => downloadDxf()}>Baixar o arquivo</Button>
      <Button disabled={!savedPath} variant='outlined' style={{marginTop: 8}} onClick={() => window.pywebview.api.utils.open_in_explorer(savedPath)}>
        Abrir pasta do arquivo
      </Button>
    </div>
  )
}

export default GeradorDePerfil
