import { useState } from 'react';
import { ToolContextProvider } from './contexts/ToolContext'
import { ErrorContextProvider } from './contexts/ErrorContext'
import { LoadingContextProvider } from './contexts/LoadingContext'
import MainPage from './components/MainPage'

function App() {
  const [name, setName] = useState("")
  const [greeting, setGreeting] = useState("")

  const sayHello = async () => {
    const result = await window.pywebview.api.greet(name)
    setGreeting(result)
  }

  return (
    <ToolContextProvider>
      <ErrorContextProvider>
        <LoadingContextProvider>
          <MainPage />
        </LoadingContextProvider>
      </ErrorContextProvider>
    </ToolContextProvider>
  );
}

export default App;
