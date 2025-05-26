import { useEffect, useState } from 'react'
import { Breadcrumbs, Button, Typography, Box, Stack } from '@mui/material'
import GeradorDePerfil from '../GeradorDePerfil'
import KmlFromPhotos from '../KmlFromPhotos'
import { useToolContext } from '../../contexts/ToolContext'
import CheckUpdates from '../CheckUpdates'

const MainPage = () => {
  const { currentTool, setToolState } = useToolContext()

  const [version, setVersion] = useState('')

  const AVAILABLE_TOOLS = [
    {
      name: 'Gerador de perfil',
      component: <GeradorDePerfil />,
    },
    {
      name: 'KML de fotos',
      component: <KmlFromPhotos />,
    },
  ]

  const handleSelectTool = (tool) => {
    setToolState({ currentTool: tool })
  }

  useEffect(() => {
    function fetchVersion() {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.utils && window.pywebview.api.utils.get_version) {
        window.pywebview.api.utils.get_version().then(res => {
          setVersion(res.version)
        })
      }
    }

    // If pywebview is already ready, fetch immediately
    if (window.pywebview && window.pywebview.api && window.pywebview.api.utils && window.pywebview.api.utils.get_version) {
      fetchVersion()
    } else {
      // Otherwise, wait for the event
      window.addEventListener('pywebviewready', fetchVersion)
      // Clean up event listener on unmount
      return () => window.removeEventListener('pywebviewready', fetchVersion)
    }
  }, [])

  return (
    <Box sx={{ p: 3, position: 'relative' }}>
      <span
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          textAlign: 'right',
          display: 'block',
          color: 'gray',
          fontSize: '14px',
        }}
      >
        <span>{`v${version}`}</span>
      </span>
      <CheckUpdates />
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Button
          color="inherit"
          onClick={() => handleSelectTool('')}
          disabled={!currentTool}
        >
          Home
        </Button>
        {currentTool && (
          <Typography color="text.primary">{currentTool}</Typography>
        )}
      </Breadcrumbs>
      {currentTool === '' ? (
        <Stack style={{ alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="h5" sx={{ mb: 2 }}>
            Selecione uma ferramenta:
          </Typography>
          <Stack spacing={3} sx={{ mb: 2 }}>
            {AVAILABLE_TOOLS.map((tool) => (
              <Button
                key={tool.name}
                variant="contained"
                onClick={() => handleSelectTool(tool.name)}
                sx={{ minWidth: 200, height: 48, fontSize: 16 }}
              >
                {tool.name}
              </Button>
            ))}
          </Stack>
        </Stack>
      ) : (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {AVAILABLE_TOOLS.find((t) => t.name === currentTool)?.component}
        </div>
      )}
    </Box>
  )
}

export default MainPage
