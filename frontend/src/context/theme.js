import { createContext, useContext } from 'react'
import { LIGHT_THEME } from '../theme/tokens'

export const ThemeContext = createContext({
  T: LIGHT_THEME, dark: false, toggleDark: () => {}
})

export const useTheme = () => useContext(ThemeContext)
