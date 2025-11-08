import { useEffect } from 'react'
import { useThemeStore } from './stores/theme'
import Router from './pages/Router'

function App() {
  const { isDark } = useThemeStore()

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

  return <Router />
}

export default App
