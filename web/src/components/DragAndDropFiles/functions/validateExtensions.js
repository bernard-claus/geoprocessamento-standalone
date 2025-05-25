export const validateExtensions = (files, fullAcceptedExtensions) => {
  if (fullAcceptedExtensions.includes('*')) return true
  let output = true
  const acceptedExtensions = fullAcceptedExtensions.map(e => e.toLowerCase())
  files.forEach(file => {
    const extension = file.name.slice(file.name.length - 5).split('.')[1].toLowerCase()
    if (!acceptedExtensions.includes(extension)) output = false
  })
  return output
}
