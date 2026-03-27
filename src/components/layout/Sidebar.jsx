import { useTheme } from '../../context/ThemeContext'
import { Icons } from '../icons/Icons'

const NAV_ITEMS = [
  { id: 'dashboard', label: '홈',                  Icon: Icons.Dashboard, locked: false },
  { id: 'history',   label: '트렌드 히스토리',      Icon: Icons.History,   locked: false },
  { id: 'ai',        label: 'AI 예측',              Icon: Icons.AI,        locked: false },
  { id: 'pricing',   label: '요금제',               Icon: Icons.Pricing,   locked: true  },
  { id: 'mypage',    label: '로그인 / 마이페이지',  Icon: Icons.User,      locked: true  },
]

export default function Sidebar({ page, setPage }) {
  const { T } = useTheme()
  return (
    <aside style={{
      position: 'fixed', top: 0, left: 0, bottom: 0, width: 220,
      background: T.sidebar, borderRight: `1px solid ${T.border}`,
      display: 'flex', flexDirection: 'column', zIndex: 100,
    }}>
      <div
        style={{ padding: '20px 22px', borderBottom: `1px solid ${T.border}`, cursor: 'pointer' }}
        onClick={() => setPage('dashboard')}
        role="button" tabIndex={0}
        onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setPage('dashboard') } }}
      >
        <div style={{ fontSize: 19, fontWeight: 900, color: T.accent, letterSpacing: '-0.02em' }}>TrendRadar</div>
        <div style={{ fontSize: 10, color: T.muted, marginTop: 3, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
          한국 트렌드 예측 플랫폼
        </div>
      </div>

      <nav style={{ flex: 1, padding: '14px 10px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        {NAV_ITEMS.map(item => {
          const active = page === item.id && !item.locked
          return (
            <button
              key={item.id}
              disabled={item.locked}
              onClick={() => !item.locked && setPage(item.id)}
              style={{
                width: '100%', textAlign: 'left',
                padding: '9px 12px', borderRadius: 7, border: 'none',
                cursor: item.locked ? 'not-allowed' : 'pointer',
                background: active ? `${T.accent}20` : 'transparent',
                color: item.locked ? T.muted : active ? T.accent : T.textSoft,
                fontFamily: 'inherit', fontSize: 13, fontWeight: active ? 700 : 400,
                display: 'flex', alignItems: 'center', gap: 10,
                borderLeft: `2px solid ${active ? T.accent : 'transparent'}`,
                opacity: item.locked ? 0.4 : 1,
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={e => { if (!item.locked && !active) e.currentTarget.style.background = `${T.accent}10` }}
              onMouseLeave={e => { if (!item.locked && !active) e.currentTarget.style.background = 'transparent' }}
            >
              <item.Icon size={15} color={item.locked ? T.muted : active ? T.accent : T.textSoft} />
              <span style={{ flex: 1 }}>{item.label}</span>
              {item.locked && <Icons.Lock size={12} color={T.muted} />}
            </button>
          )
        })}
      </nav>

      <div style={{ padding: '12px 22px', borderTop: `1px solid ${T.border}`, fontSize: 10, color: T.muted }}>
        © 2026 TrendRadar
      </div>
    </aside>
  )
}