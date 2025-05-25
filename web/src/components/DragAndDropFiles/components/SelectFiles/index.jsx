import { Upload } from '@mui/icons-material'
import { Stack, Typography } from '@mui/material'
import React from 'react'

const SelectFiles = ({ acceptedExtensions, handleDrop, multiple, text, uniqueId }) => (
  <div className='selectFilesDiv'>
    <input
      type="file"
      hidden
      id={uniqueId}
      onChange={(event) => handleDrop(event, event.target)}
      accept={acceptedExtensions.map(e => `.${e.toLowerCase()}`).join(',')}
      multiple={multiple}
    />
    <label htmlFor={uniqueId} className="browse-btn">
      <Stack direction='row' className='clickableStack'>
        <Upload />
        <Typography>{text}</Typography>
      </Stack>
    </label>
  </div>
)


export default SelectFiles
