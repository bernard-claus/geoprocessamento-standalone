import { Stack } from '@mui/material'
import { getSizeFromBytes } from '../../functions/getSizeFromBytes'
import { splitFileName } from '../../functions/splitFileName'
import SelectFiles from '../SelectFiles'
import AcceptedExtensions from '../AcceptedExtensions'
import SizeInfo from '../SizeInfo'
import FilesInfo from '../FilesInfo'

const MainStack = ({ acceptedExtensions, files, handleDrop, multiple, setFiles, text, uniqueId }) => (
  <Stack className='stack'>
    <SelectFiles acceptedExtensions={acceptedExtensions} handleDrop={handleDrop} multiple={multiple} text={text} uniqueId={uniqueId} />
    <AcceptedExtensions acceptedExtensions={acceptedExtensions} />
    {files.length > 0 && (
      <SizeInfo files={files} getSizeFromBytes={getSizeFromBytes} setFiles={setFiles} />
    )}
    {files.length > 0 && (
      <FilesInfo files={files} getSizeFromBytes={getSizeFromBytes} splitFileName={splitFileName} />
    )}
  </Stack>
)

export default MainStack
