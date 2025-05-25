import { Box, CircularProgress, Typography } from '@mui/material'

const CircularProgressDetermined = ({ value, boxSx }) => (
  <Box sx={{ ...boxSx }}>
    <CircularProgress variant='determinate' value={value} />
    <Box
      sx={{
        top: 0,
        left: 0,
        bottom: 0,
        right: 0,
        position: 'absolute',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Typography
        variant='caption'
        component='div'
        sx={{ color: 'text.secondary' }}
      >
        {`${Math.round(value)}%`}
      </Typography>
    </Box>
  </Box>
)

export default CircularProgressDetermined
