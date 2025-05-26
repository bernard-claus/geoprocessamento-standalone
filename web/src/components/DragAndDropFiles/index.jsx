import { useRef, useState } from 'react'
import { useSnackbar } from 'notistack'
import { v4 } from 'uuid'
import { Upload } from '@mui/icons-material'
import { MainDiv } from './styles'
import { validateExtensions } from './functions/validateExtensions'
import MainStack from './components/MainStack'

const DragAndDropFiles = ({
  acceptedExtensions = ['dxf'],
  isDir=false,
  backgroundColor = '#c9e0f580',
  borderRadius = '25px',
  borderColor = '#243782',
  borderWidth = '5px',
  disabled = false,
  files,
  fontSize = '15px',
  height = '300px',
  multiple = false,
  setFiles,
  text = 'Arraste ou clique aqui',
  uniqueId = v4(),
  width = '300px',
}) => {

  const { enqueueSnackbar } = useSnackbar()

  const currentUniqueId = useRef(uniqueId)
  const [dragOver, setDragOver] = useState(false)

  const handleDragOver = (event) => {
    if (disabled) return
    event.preventDefault()
    setDragOver(true)
  }

  const handleDrop = (event, eventTarget) => {
    if (disabled) return
    event.preventDefault()
    const droppedFiles = eventTarget.files
    console.log({droppedFiles})
    if ((!multiple && droppedFiles.length > 1) || (!multiple && files.length > 0)) {
      enqueueSnackbar('This drag and drop accepts only one file', { variant: 'warning' })
      setDragOver(false)
      return
    }
    if (!droppedFiles.length) {
      enqueueSnackbar('Could not identify file', { variant: 'error' })
      setDragOver(false)
      return
    }
    const newFiles = Array.from(droppedFiles)
    const validExtensions = validateExtensions(newFiles, acceptedExtensions, isDir)
    if (!validExtensions) {
      enqueueSnackbar('One or more file extensions are not accepted', { variant: 'error' })
      setDragOver(false)
      return
    }
    setFiles((prevFiles) => [...prevFiles, ...newFiles])
    setDragOver(false)
  }

  return (
    <MainDiv
      backgroundColor={backgroundColor}
      borderRadius={borderRadius}
      borderColor={borderColor}
      borderWidth={borderWidth}
      dragOver={dragOver}
      fontSize={fontSize}
      height={height}
      width={width}
      onDragOver={(event) => handleDragOver(event)}
      onDragLeave={() => { if (disabled) return; setDragOver(false) }}
      onDrop={(event) => handleDrop(event, event.dataTransfer)}
    >
      {dragOver ? <Upload /> : <MainStack acceptedExtensions={acceptedExtensions} files={files} handleDrop={handleDrop} multiple={multiple} setFiles={setFiles} text={text} uniqueId={currentUniqueId.current} /> }
    </MainDiv>
  )
}

export default DragAndDropFiles
