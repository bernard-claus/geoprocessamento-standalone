export const validateExtensions = (files, fullAcceptedExtensions, isDir) => {
  if (isDir) {
    if (files.map(f => f.size).any(s => s !== 0)) return false
    if (files.map(f => f.type).any(t => s !== '')) return false
    return true
  }
  if (fullAcceptedExtensions.includes('*')) return true
  let output = true
  const acceptedExtensions = fullAcceptedExtensions.map(e => e.toLowerCase())
  files.forEach(file => {
    const extension = file.name.slice(file.name.length - 5).split('.')[1].toLowerCase()
    if (!acceptedExtensions.includes(extension)) output = false
  })
  return output
}
