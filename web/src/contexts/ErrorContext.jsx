import { createContext, useState, useMemo, useContext } from 'react'

const INITIAL_OPTION = {
  error: false,
  errorObj: null,
  setError: () => {},
}

const context = createContext(INITIAL_OPTION)

const useErrorContext = () => useContext(context)

const ErrorContextProvider = ({ children }) => {
  const [errorState, setErrorState] = useState(INITIAL_OPTION)

  const value = useMemo(() => ({
    ...errorState,
    setErrorState: (data) => setErrorState(prev => ({ ...prev, ...data }))
  }), [errorState])

  return (
    <context.Provider value={value}>
      { children }
    </context.Provider>
  )
}

export { ErrorContextProvider, useErrorContext }






