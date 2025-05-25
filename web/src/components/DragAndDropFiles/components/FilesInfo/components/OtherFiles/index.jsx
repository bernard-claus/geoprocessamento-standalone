import { Stack, Tooltip, Typography } from '@mui/material'

const OtherFiles = ({ files, getSizeFromBytes }) => (
  <Tooltip title={(
    <Stack>
      {files.filter((_, i) => i >= 3).map(f => (
        <Typography key={`drag_drop_more_files_${f.name}`}>{`${f.name} (${getSizeFromBytes(f.size)})`}</Typography>
      ))}
    </Stack>
  )}
  >
    <Typography className='dottedBottom'>{`+ ${files.length - 3} files`}</Typography>
  </Tooltip>
)

export default OtherFiles
