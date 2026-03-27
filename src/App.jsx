import { useState } from 'react'
import { ThemeProvider, useTheme } from './context/ThemeContext'
import Sidebar from './components/layout/Sidebar'
import Header from './components/layout/Header'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import AIPrediction from './pages/AIPrediction'

function AppLayout() {
  const { T } = useTheme()
  const [page, setPage] = useState('dashboard')
  const [searchQuery, setSearchQuery] = useState('')

  const pageMap = {
    dashboard: <Dashboard setPage={setPage} />,
    history: <History />,
    ai: <AIPrediction />,
  }

  return (
    <div style={{ minHeight: '100vh', background: T.bg, transition: 'background 0.3s ease' }}>
      <Sidebar page={page} setPage={setPage} />
      <Header searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
      <main style={{ marginLeft: 220, paddingTop: 58, minHeight: '100vh' }}>
        <div style={{ padding: 22 }}>
          {pageMap[page] || <Dashboard setPage={setPage} />}
        </div>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <AppLayout />
    </ThemeProvider>
  )
}