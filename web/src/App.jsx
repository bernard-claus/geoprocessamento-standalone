import { ToolContextProvider } from './contexts/ToolContext'
import { ErrorContextProvider } from './contexts/ErrorContext'
import { LoadingContextProvider } from './contexts/LoadingContext'
import MainPage from './components/MainPage'

function App() {
  return (
    <ToolContextProvider>
      <ErrorContextProvider>
        <LoadingContextProvider>
          <MainPage />
        </LoadingContextProvider>
      </ErrorContextProvider>
    </ToolContextProvider>
  )
}

export default App

