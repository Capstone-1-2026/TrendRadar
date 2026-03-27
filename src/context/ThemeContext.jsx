import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { LIGHT_THEME, DARK_THEME } from '../theme/tokens'

export const ThemeContext = createContext({
  T: LIGHT_THEME, dark: false, toggleDark: () => {}
})

export const useTheme = () => useContext(ThemeContext)

export function ThemeProvider({ children }) {
  const [dark, setDark] = useState(false)
  const theme = dark ? DARK_THEME : LIGHT_THEME
  const toggleDark = useCallback(() => setDark(d => !d), [])

  useEffect(() => {
    document.body.style.background = theme.bg
    document.body.style.color = theme.text
    if (dark) {
      document.documentElement.classList.add('dark-mode')
    } else {
      document.documentElement.classList.remove('dark-mode')
    }
  }, [dark])

  return (
    <ThemeContext.Provider value={{ T: theme, dark, toggleDark }}>
      {children}
    </ThemeContext.Provider>
  )
}