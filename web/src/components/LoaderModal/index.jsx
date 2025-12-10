
import { Modal, CircularProgress, Box } from '@mui/material'
import { useLoadingContext } from '../../contexts/LoadingContext'

const LoaderModal = () => {

  const { loading, text } = useLoadingContext()

  return (
    <Modal
      open={loading}
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2,
          outline: 'none'
        }}
      >
        <CircularProgress sx={{ color: 'white' }} />
        {text && (
          <Box sx={{ color: 'white', mt: 1 }}>
            {text}
          </Box>
        )}
      </Box>
    </Modal>
  )
}

export default LoaderModal
