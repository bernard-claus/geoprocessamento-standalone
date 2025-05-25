import { createContext, useState, useMemo, useContext } from 'react'

const INITIAL_OPTION = {
  loading: false,
  text: '',
  setLoading: () => {},
}

const context = createContext(INITIAL_OPTION)

const useLoadingContext = () => useContext(context)

const LoadingContextProvider = ({ children }) => {
  const [loadingState, setLoadingState] = useState(INITIAL_OPTION)

  const value = useMemo(() => ({
    ...loadingState,
    setLoadingState: (data) => setLoadingState(prev => ({ ...prev, ...data }))
  }), [loadingState])

  return (
    <context.Provider value={value}>
      { children }
    </context.Provider>
  )
}

export { LoadingContextProvider, useLoadingContext }






