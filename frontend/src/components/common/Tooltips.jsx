import { useTheme } from '../../context/ThemeContext'

export function DarkTooltip({ active, payload, label }) {
    const { T } = useTheme()
    if (!active || !payload?.length) return null
    return (
        <div style={{
            background: T.cardInner, border: `1px solid ${T.border}`,
            borderRadius: 8, padding: '9px 13px', boxShadow: '0 8px 24px rgba(0,0,0,0.25)',
        }}>
            <p style={{ fontSize: 11, color: T.muted, marginBottom: 6 }}>{label}</p>
            {payload.map((p, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 3 }}>
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: p.color, display: 'inline-block', flexShrink: 0 }} />
                    <span style={{ fontSize: 12, color: T.textSoft }}>{p.name}</span>
                    <span style={{ fontSize: 12, fontWeight: 700, color: p.color, marginLeft: 'auto', paddingLeft: 8 }}>{p.value}</span>
                </div>
            ))}
        </div>
    )
}

export function BarDarkTooltip({ active, payload, label }) {
    const { T } = useTheme()
    if (!active || !payload?.length) return null
    return (
        <div style={{
            background: T.cardInner, border: `1px solid ${T.border}`,
            borderRadius: 8, padding: '9px 13px', boxShadow: '0 8px 24px rgba(0,0,0,0.25)',
        }}>
            <p style={{ fontSize: 13, fontWeight: 700, color: T.text }}>{label}</p>
            {payload.map((p, i) => (
                <p key={i} style={{ fontSize: 12, color: T.accentSub, marginTop: 3 }}>
                    평균 스코어: <strong style={{ color: T.accent }}>{p.value}</strong>
                </p>
            ))}
        </div>
    )
}