import { useState } from 'react'
import { useTheme } from '../../context/ThemeContext'

export default function Card({ children, style = {}, onClick, hoverable, id }) {
    const { T } = useTheme()
    const [hov, setHov] = useState(false)
    return (
        <div
            id={id}
            style={{
                background: hov && hoverable ? T.cardHov : T.card,
                borderRadius: 10, padding: '18px 22px',
                border: `1px solid ${hov && hoverable ? T.borderMid : T.border}`,
                transition: 'background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease',
                boxShadow: hov && hoverable ? '0 4px 20px rgba(0,0,0,0.12)' : 'none',
                cursor: onClick ? 'pointer' : undefined,
                ...style,
            }}
            onClick={onClick}
            onMouseEnter={() => hoverable && setHov(true)}
            onMouseLeave={() => hoverable && setHov(false)}
            role={onClick ? 'button' : undefined}
            tabIndex={onClick ? 0 : undefined}
            onKeyDown={onClick ? e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(e) } } : undefined}
        >
            {children}
        </div>
    )
}