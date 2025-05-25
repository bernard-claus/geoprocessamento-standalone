export const splitFileName = (fullName) => {
  const extention = fullName.slice(fullName.length - 5).split('.')[1]
  const name = fullName.split(`.${extention}`)[0]
  if (name.length < 15) return `${name}.${extention}`
  return `${name.slice(0, 15)}...${extention}`
}
