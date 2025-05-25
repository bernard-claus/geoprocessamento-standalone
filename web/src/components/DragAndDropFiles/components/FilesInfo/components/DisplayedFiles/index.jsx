import { Tooltip, Typography } from '@mui/material'

const DisplayedFiles = ({ file, getSizeFromBytes, splitFileName }) => (
  <Tooltip title={(<Typography>{file.name}</Typography>)} key={file.name}>
    <Typography>{`${splitFileName(file.name)} (${getSizeFromBytes(file.size)})`}</Typography>
  </Tooltip>
)


export default DisplayedFiles
