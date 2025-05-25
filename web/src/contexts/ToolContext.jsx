import { createContext, useState, useMemo, useContext } from 'react'

const INITIAL_OPTION = {
  currentTool: '',
  setToolState: () => {},
}

const context = createContext(INITIAL_OPTION)

const useToolContext = () => useContext(context)

const ToolContextProvider = ({ children }) => {
  const [toolState, setToolState] = useState(INITIAL_OPTION)

  const value = useMemo(() => ({
    ...toolState,
    setToolState: (data) => setToolState(prev => ({ ...prev, ...data }))
  }), [toolState])

  return (
    <context.Provider value={value}>
      { children }
    </context.Provider>
  )
}

export { ToolContextProvider, useToolContext }






