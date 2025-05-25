import { Delete } from '@mui/icons-material'
import { Stack, Typography } from '@mui/material'
import React from 'react'

const SizeInfo = ({ files, getSizeFromBytes, setFiles }) => (
  <Stack direction='row' className='totalSizeStack'>
    <div className='totalSizeDiv'>
      <Typography className='totalSize'>{`Total size: ${getSizeFromBytes(files.map(f => f.size).reduce((a, b) => a + b))}`}</Typography>
    </div>
    <div className='clearButton'>
      <Typography onClick={() => setFiles([])} className='clickable'>Limpar</Typography>
      <Delete onClick={() => setFiles([])} className='clickable'/>
    </div>
  </Stack>
)


export default SizeInfo
