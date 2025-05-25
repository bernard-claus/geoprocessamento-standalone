import { Stack, Typography } from '@mui/material'

const AcceptedExtensions = ({ acceptedExtensions }) => (
  <Stack className='stack'>
    <Typography>Extensões aceitas:</Typography>
    <Typography>{acceptedExtensions.join(', ')}</Typography>
  </Stack>
)


export default AcceptedExtensions
