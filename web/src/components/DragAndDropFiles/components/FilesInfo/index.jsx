import { Stack } from '@mui/material'
import DisplayedFiles from './components/DisplayedFiles'
import OtherFiles from './components/OtherFiles'

const FilesInfo = ({ files, getSizeFromBytes, splitFileName }) => (
  <Stack className='stack'>
    {files.filter((_, i) => i < 3).map(file => (
      <DisplayedFiles file={file} getSizeFromBytes={getSizeFromBytes} splitFileName={splitFileName} key={`drag_drop_${splitFileName}`}/>
    ))}
    {files.length > 3 && (
      <OtherFiles files={files} getSizeFromBytes={getSizeFromBytes} />
    )}
  </Stack>
)

export default FilesInfo
