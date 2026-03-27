import { useTheme } from '../../context/ThemeContext'

export default function SectionTitle({ icon, title, sub }) {
  const { T } = useTheme()
  return (
    <div style={{ marginBottom: 14, display: 'flex', alignItems: 'flex-start', gap: 8 }}>
      {icon && <span style={{ color: T.accent, marginTop: 1 }}>{icon}</span>}
      <div>
        <h2 style={{ fontSize: 15, fontWeight: 700, color: T.text, letterSpacing: '-0.01em' }}>{title}</h2>
        {sub && <p style={{ fontSize: 12, color: T.muted, marginTop: 3 }}>{sub}</p>}
      </div>
    </div>
  )
}