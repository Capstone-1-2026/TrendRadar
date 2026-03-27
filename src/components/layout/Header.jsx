import { useState } from 'react'
import { useTheme } from '../../context/ThemeContext'
import { Icons } from '../icons/Icons'

export default function Header({ searchQuery, setSearchQuery }) {
    const { T, dark, toggleDark } = useTheme()
    const [focused, setFocused] = useState(false)
    return (
        <header style={{
            position: 'fixed', top: 0, left: 220, right: 0, height: 58,
            background: `${T.sidebar}f0`, backdropFilter: 'blur(14px)',
            borderBottom: `1px solid ${T.border}`,
            display: 'flex', alignItems: 'center', padding: '0 22px',
            zIndex: 99,
        }}>
            <div style={{ flex: 1 }} />
            <div style={{ position: 'relative', marginRight: 12 }}>
                <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', zIndex: 1 }}>
                    <Icons.Search size={15} color={focused ? T.accent : T.textSoft} />
                </span>
                <input
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="트렌드 검색..."
                    style={{
                        background: focused ? T.card : T.cardInner,
                        border: `2px solid ${focused ? T.accent : T.borderMid}`,
                        borderRadius: 9, padding: '8px 16px 8px 36px',
                        color: T.text, fontSize: 13,
                        width: 240, fontFamily: 'inherit', outline: 'none',
                        transition: 'border-color 0.2s, background 0.2s, box-shadow 0.2s',
                        boxShadow: focused ? `0 0 0 3px ${T.accent}22` : 'none',
                    }}
                    onFocus={() => setFocused(true)}
                    onBlur={() => setFocused(false)}
                />
                {searchQuery && (
                    <button
                        onClick={() => setSearchQuery('')}
                        style={{
                            position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)',
                            background: 'none', border: 'none', cursor: 'pointer', padding: 2,
                            color: T.muted, display: 'flex', alignItems: 'center',
                        }}
                    >
                        <Icons.Close size={12} color={T.muted} />
                    </button>
                )}
            </div>
            <button
                onClick={toggleDark}
                title={dark ? '라이트 모드로 전환' : '다크 모드로 전환'}
                style={{
                    width: 36, height: 36, borderRadius: 8,
                    border: `1px solid ${T.border}`,
                    background: T.card,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: 'pointer', transition: 'all 0.2s ease', color: T.textSoft,
                }}
                onMouseEnter={e => { e.currentTarget.style.background = T.cardHov; e.currentTarget.style.borderColor = T.accent }}
                onMouseLeave={e => { e.currentTarget.style.background = T.card; e.currentTarget.style.borderColor = T.border }}
            >
                {dark ? <Icons.Sun size={16} color={T.accent} /> : <Icons.Moon size={16} color={T.textSoft} />}
            </button>
        </header>
    )
}