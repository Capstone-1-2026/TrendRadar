import { useTheme } from '../../context/ThemeContext'

export default function WordCloud({ items, onClick, selectedId }) {
    const { T } = useTheme()
    const sorted = [...items].sort((a, b) => b.size - a.size)
    return (
        <div style={{
            display: 'flex', flexWrap: 'wrap', alignItems: 'center',
            justifyContent: 'center', gap: '6px 10px', padding: '10px 4px',
        }}>
            {sorted.map((item, i) => {
                const isSelected = selectedId === item.id
                const mt = [0, 8, -4, 12, -8, 4, -12, 6][i % 8]
                return (
                    <span
                        key={item.id}
                        onClick={() => onClick && onClick(item.id)}
                        tabIndex={onClick ? 0 : undefined}
                        onKeyDown={onClick ? e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(item.id) } } : undefined}
                        style={{
                            display: 'inline-block', fontSize: item.size,
                            fontWeight: item.size > 26 ? 800 : item.size > 18 ? 700 : 500,
                            color: item.color, marginTop: mt,
                            cursor: onClick ? 'pointer' : 'default',
                            opacity: selectedId && !isSelected ? 0.35 : 1,
                            transition: 'all 0.2s ease',
                            padding: '2px 4px', borderRadius: 4,
                            background: isSelected ? `${item.color}28` : 'transparent',
                            border: isSelected ? `1px solid ${item.color}60` : '1px solid transparent',
                            userSelect: 'none',
                        }}
                    >
                        {item.name}
                    </span>
                )
            })}
        </div>
    )
}