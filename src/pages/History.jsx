import { useState } from 'react'
import { useTheme } from '../context/ThemeContext'
import { KEYWORDS, catLabelMap } from '../data/keywords'
import Card from '../components/common/Card'
import Badge from '../components/common/Badge'
import ProgressBar from '../components/common/ProgressBar'
import SectionTitle from '../components/common/SectionTitle'
import { Icons, catIconMap } from '../components/icons/Icons'

const HALO_CAUSES = ['대체재 등장', '계절 종료', '공급 과잉', '부정 이슈', '자연 소멸']
const SOURCE_TIPS = {
    '네이버 DataLab': '네이버 검색 데이터 기반 트렌드 지수 (search.naver.com/datalab)',
    'YouTube': 'YouTube 검색 및 조회수 기반 분석 (youtube.com/trends)',
    '계절 보정': '월별 계절성 요인 보정 (기상청 + 유통 데이터 복합 적용)',
}

function HistoryKeywordCard({ kw }) {
    const { T } = useTheme()
    const [open, setOpen] = useState(false)
    const [tipSource, setTipSource] = useState(null)
    const catKey = kw.cat === 'snack' || kw.cat === 'drink' ? 'food' : kw.cat
    const CatIcon = catIconMap[kw.cat] || Icons.Tag
    const summary = `${kw.name}은(는) ${kw.year}년 ${catLabelMap[kw.cat] || kw.cat} 카테고리에서 최고 스코어 ${kw.peak}점을 기록했습니다. SNS 중심 확산 이후 빠르게 대중화되었으나, 경쟁 제품 등장과 함께 관심이 감소하기 시작했습니다.`
    const cause = HALO_CAUSES[kw.id % HALO_CAUSES.length]
    const dropRate = Math.round((100 - kw.peak * 0.6) * 0.4 + 10)
    const sources = [
        { name: '네이버 DataLab', pct: 50, color: '#34D399' },
        { name: 'YouTube', pct: 30, color: '#F07B8A' },
        { name: '계절 보정', pct: 20, color: '#60A5FA' },
    ]

    return (
        <div style={{
            borderRadius: 10, border: `1px solid ${T.border}`,
            overflow: 'hidden', background: T.card,
            transition: 'border-color 0.2s ease',
        }}
            onMouseEnter={e => e.currentTarget.style.borderColor = T.borderMid}
            onMouseLeave={e => e.currentTarget.style.borderColor = T.border}
        >
            <div
                role="button" tabIndex={0}
                onClick={() => setOpen(v => !v)}
                onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setOpen(v => !v) } }}
                style={{ padding: '14px 18px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12 }}
            >
                <CatIcon size={18} color={T.catColors[catKey]} />
                <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 14, fontWeight: 700, color: T.text }}>{kw.name}</p>
                    <p style={{ fontSize: 11, color: T.muted }}>{kw.cat} · {kw.year}년</p>
                    <div style={{ marginTop: 7 }}>
                        <ProgressBar value={kw.peak} color={T.catColors[catKey] || T.up} height={4} bg={T.bg} />
                    </div>
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <Badge color={T.down}>
                        <Icons.TrendDown size={10} color={T.down} />-{dropRate}%
                    </Badge>
                    <p style={{ fontSize: 10, color: T.muted, marginTop: 4 }}>스코어 {kw.peak}</p>
                </div>
                <div style={{ transform: open ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.25s ease', color: T.muted, flexShrink: 0 }}>
                    <Icons.ChevronDown size={14} color={T.muted} />
                </div>
            </div>

            <div style={{ maxHeight: open ? 600 : 0, overflow: 'hidden', transition: 'max-height 0.4s cubic-bezier(0.4,0,0.2,1)' }}>
                <div style={{ padding: '0 18px 18px', borderTop: `1px solid ${T.border}`, background: T.cardInner }}>
                    <div style={{ padding: '12px 0 10px' }}>
                        <p style={{ fontSize: 11, color: T.muted, marginBottom: 5, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 5 }}>
                            <Icons.Robot size={12} color={T.muted} /> AI 한줄 요약
                        </p>
                        <p style={{ fontSize: 13, color: T.textSoft, lineHeight: 1.7 }}>{summary}</p>
                    </div>
                    <div style={{ marginBottom: 12 }}>
                        <p style={{ fontSize: 11, color: T.muted, marginBottom: 5, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 5 }}>
                            <Icons.Pin size={12} color={T.muted} /> 하락 원인
                        </p>
                        <Badge color={T.down} bg={`${T.down}28`}>
                            <Icons.TrendDown size={10} color={T.down} />{cause}
                        </Badge>
                    </div>
                    <div style={{ marginBottom: 12 }}>
                        <p style={{ fontSize: 11, color: T.muted, marginBottom: 8, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 5 }}>
                            <Icons.Ruler size={12} color={T.muted} /> 트렌드 스코어 산출 과정
                        </p>
                        {sources.map(s => (
                            <div key={s.name} style={{ marginBottom: 7 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                                    <span style={{ fontSize: 11, color: T.textSoft }}>{s.name}</span>
                                    <span style={{ fontSize: 11, color: s.color, fontWeight: 700 }}>{s.pct}%</span>
                                </div>
                                <ProgressBar value={s.pct} color={s.color} height={4} bg={T.border} />
                            </div>
                        ))}
                    </div>
                    <div>
                        <p style={{ fontSize: 11, color: T.muted, marginBottom: 6, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 5 }}>
                            <Icons.Link size={12} color={T.muted} /> 데이터 출처
                        </p>
                        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                            {sources.map(s => (
                                <div key={s.name} style={{ position: 'relative' }}>
                                    <button
                                        onMouseEnter={() => setTipSource(s.name)}
                                        onMouseLeave={() => setTipSource(null)}
                                        style={{
                                            padding: '3px 10px', borderRadius: 999,
                                            border: `1px solid ${s.color}55`, background: `${s.color}10`,
                                            color: s.color, fontSize: 11, fontWeight: 600,
                                            cursor: 'default', fontFamily: 'inherit',
                                        }}
                                    >{s.name}</button>
                                    {tipSource === s.name && (
                                        <div style={{
                                            position: 'absolute', bottom: '115%', left: 0,
                                            background: T.cardInner, border: `1px solid ${T.border}`,
                                            borderRadius: 7, padding: '7px 11px', fontSize: 11,
                                            color: T.textSoft, whiteSpace: 'nowrap', zIndex: 10,
                                            boxShadow: '0 4px 16px rgba(0,0,0,0.3)', pointerEvents: 'none',
                                        }}>{SOURCE_TIPS[s.name]}</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

function getSelStyle(T) {
    return {
        background: T.card, border: `1px solid ${T.border}`, borderRadius: 7,
        color: T.text, fontSize: 13, padding: '7px 12px',
        fontFamily: 'inherit', outline: 'none', cursor: 'pointer',
    }
}

export default function History() {
    const { T } = useTheme()
    const CATS = ['전체', 'food', 'fashion', 'content', 'technology', 'lifestyle']
    const catDisplayName = { '전체': '전체', food: '음식', fashion: '패션', content: '콘텐츠', technology: '기술', lifestyle: '라이프' }
    const catColorMap = {
        food: T.catColors.food, fashion: T.catColors.fashion,
        content: T.catColors.content, technology: T.catColors.technology, lifestyle: T.catColors.lifestyle,
    }
    const CatIcons = {
        food: Icons.FoodIcon, fashion: Icons.FashionIcon, content: Icons.ContentIcon,
        technology: Icons.TechIcon, lifestyle: Icons.LifeIcon,
    }
    const [selCat, setSelCat] = useState('전체')
    const [selYear, setSelYear] = useState('전체')
    const [selMonth, setSelMonth] = useState('전체')

    const filtered = KEYWORDS.filter(kw => {
        const k = kw.cat === 'snack' || kw.cat === 'drink' ? 'food' : kw.cat
        return (selCat === '전체' || k === selCat) && (selYear === '전체' || kw.year === Number(selYear))
    })

    const catSummary = CATS.filter(c => c !== '전체').map(c => {
        const items = KEYWORDS.filter(kw => {
            const k = kw.cat === 'snack' || kw.cat === 'drink' ? 'food' : kw.cat
            return k === c
        })
        const avg = items.length ? Math.round(items.reduce((s, k) => s + k.peak, 0) / items.length) : 0
        return { cat: c, avg, count: items.length }
    })

    const btnBase = (active, c) => ({
        padding: '5px 12px', borderRadius: 6,
        border: `1px solid ${active ? (c || T.accent) : T.border}`,
        background: active ? `${(c || T.accent)}18` : 'transparent',
        color: active ? (c || T.accent) : T.muted,
        fontSize: 12, fontWeight: 600, cursor: 'pointer',
        fontFamily: 'inherit', transition: 'all 0.15s ease',
        display: 'flex', alignItems: 'center', gap: 5,
    })

    return (
        <div>
            <div style={{ marginBottom: 20 }}>
                <h1 style={{ fontSize: 20, fontWeight: 800, color: T.text, letterSpacing: '-0.02em' }}>트렌드 히스토리</h1>
                <p style={{ fontSize: 13, color: T.muted, marginTop: 3 }}>과거 트렌드의 흐름과 하락 원인을 분석합니다</p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
                <Card style={{ padding: '14px 18px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                        <Icons.Filter size={13} color={T.accent} />
                        <span style={{ fontSize: 12, fontWeight: 700, color: T.accent, letterSpacing: '0.04em', textTransform: 'uppercase' }}>카테고리</span>
                    </div>
                    <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
                        {CATS.map(c => {
                            const CIcon = CatIcons[c]
                            const active = selCat === c
                            const col = catColorMap[c] || T.accent
                            return (
                                <button key={c} onClick={() => setSelCat(c)} style={{
                                    padding: '6px 14px', borderRadius: 7, fontSize: 12, fontWeight: 600,
                                    border: `1px solid ${active ? (c === '전체' ? T.accent : col) : T.border}`,
                                    background: active ? `${c === '전체' ? T.accent : col}18` : 'transparent',
                                    color: active ? (c === '전체' ? T.accent : col) : T.muted,
                                    cursor: 'pointer', fontFamily: 'inherit',
                                    display: 'flex', alignItems: 'center', gap: 6,
                                    transition: 'all 0.15s ease',
                                }}>
                                    {CIcon && <CIcon size={13} color={active ? (c === '전체' ? T.accent : col) : T.muted} />}
                                    {catDisplayName[c] || c}
                                </button>
                            )
                        })}
                    </div>
                </Card>

                <Card style={{ padding: '14px 18px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                        <Icons.Calendar size={13} color={T.accentSub} />
                        <span style={{ fontSize: 12, fontWeight: 700, color: T.accentSub, letterSpacing: '0.04em', textTransform: 'uppercase' }}>기간 필터</span>
                    </div>
                    <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                        <select value={selYear} onChange={e => setSelYear(e.target.value)} style={getSelStyle(T)}>
                            <option value="전체">전체 연도</option>
                            {Array.from({ length: 11 }, (_, i) => 2015 + i).map(y => <option key={y} value={y}>{y}년</option>)}
                        </select>
                        <select value={selMonth} onChange={e => setSelMonth(e.target.value)} style={getSelStyle(T)}>
                            <option value="전체">전체 월</option>
                            {Array.from({ length: 12 }, (_, i) => i + 1).map(m => <option key={m} value={m}>{m}월</option>)}
                        </select>
                        {(selYear !== '전체' || selMonth !== '전체') && (
                            <button onClick={() => { setSelYear('전체'); setSelMonth('전체') }} style={{ ...btnBase(false), color: T.down, borderColor: `${T.down}44` }}>
                                <Icons.Reset size={12} color={T.down} />초기화
                            </button>
                        )}
                    </div>
                </Card>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12, marginBottom: 18 }}>
                {catSummary.map(s => {
                    const CIcon = CatIcons[s.cat]
                    const isActive = selCat === s.cat
                    return (
                        <Card key={s.cat} hoverable
                            onClick={() => setSelCat(isActive ? '전체' : s.cat)}
                            style={{
                                border: `1px solid ${isActive ? catColorMap[s.cat] : T.border}`,
                                background: isActive ? `${catColorMap[s.cat]}10` : T.card,
                            }}
                        >
                            <div style={{ marginBottom: 8 }}>
                                {CIcon && <CIcon size={20} color={catColorMap[s.cat]} />}
                            </div>
                            <p style={{ fontSize: 12, fontWeight: 700, color: isActive ? catColorMap[s.cat] : T.textSoft, marginBottom: 4 }}>{catDisplayName[s.cat] || s.cat}</p>
                            <p style={{ fontSize: 22, fontWeight: 800, color: catColorMap[s.cat], marginBottom: 2 }}>{s.avg}</p>
                            <p style={{ fontSize: 10, color: T.muted, marginBottom: 8 }}>트렌드 {s.count}개</p>
                            <ProgressBar value={s.avg} color={catColorMap[s.cat]} height={3} bg={T.bg} />
                        </Card>
                    )
                })}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
                {filtered.map(kw => <HistoryKeywordCard key={kw.id} kw={kw} />)}
                {filtered.length === 0 && (
                    <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: 40, color: T.muted, fontSize: 14 }}>
                        해당 조건의 트렌드가 없습니다.
                    </div>
                )}
            </div>
        </div>
    )
}