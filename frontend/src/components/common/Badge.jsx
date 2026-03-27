import { useTheme } from '../../context/ThemeContext'

export default function Badge({ children, color, bg, style: s = {} }) {
    const { T } = useTheme()
    const c = color || T.muted
    return (
        <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 4,
            padding: '2px 8px', borderRadius: 999,
            fontSize: 11, fontWeight: 600,
            background: bg || `${c}22`, color: c,
            ...s,
        }}>
            {children}
        </span>
    )
}