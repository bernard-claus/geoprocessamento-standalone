export const getSizeFromBytes = (size) => {
  if (size < 1024) return `${size}B`
  const kb = size / 1024
  if (kb < 1024) return `${kb.toFixed(1)}kB`
  const mb = size / (1024 * 1024)
  if (mb < 1024) return `${mb.toFixed(1)}MB`
  const gb = size / (1024 * 1024 * 1024)
  return `${gb.toFixed(1)}GB`
}
