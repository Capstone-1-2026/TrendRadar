import { useState, useEffect, useMemo } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceArea } from 'recharts'
import { useTheme } from '../context/ThemeContext'
import { KEYWORDS, RANKING, SERIES_DATA, CAT_AVGS } from '../data/keywords'
import Card from '../components/common/Card'
import Badge from '../components/common/Badge'
import ProgressBar from '../components/common/ProgressBar'
import SectionTitle from '../components/common/SectionTitle'
import WordCloud from '../components/common/WordCloud'
import { DarkTooltip, BarDarkTooltip } from '../components/common/Tooltips'
import { Icons, catIconMap } from '../components/icons/Icons'
import { useNow } from '../hooks/useNow'

const LINE_COLORS = [
    '#F5A623', '#C084FC', '#60A5FA', '#34D399',
    '#F472B6', '#38BDF8', '#FBBF24', '#A78BFA', '#86EFAC', '#FDA4AF',
]

export default function Dashboard({ setPage }) {
    const { T } = useTheme()
    const now = useNow()
    const [activeLines, setActiveLines] = useState(() => {
        const init = {}
        KEYWORDS.forEach(kw => { init[kw.name] = true })
        return init
    })
    const [chartMounted, setChartMounted] = useState(false)
    const [zoomDomain, setZoomDomain] = useState(null)
    const [selecting, setSelecting] = useState(false)
    const [selectStart, setSelectStart] = useState(null)
    const [selectEnd, setSelectEnd] = useState(null)

    useEffect(() => {
        const id = setTimeout(() => setChartMounted(true), 80)
        return () => clearTimeout(id)
    }, [])

    const toggleLine = name => setActiveLines(prev => ({ ...prev, [name]: !prev[name] }))

    const displayData = useMemo(() => {
        if (!zoomDomain) return SERIES_DATA
        const [l, r] = zoomDomain
        return SERIES_DATA.slice(l, r + 1)
    }, [zoomDomain])

    const avgScore = Math.round(KEYWORDS.reduce((s, k) => s + k.peak, 0) / KEYWORDS.length)
    const upCount = KEYWORDS.filter(k => k.peak >= 90).length
    const downCount = KEYWORDS.filter(k => k.peak < 85).length

    const wcItems = KEYWORDS.map(kw => ({
        id: kw.id, name: kw.name,
        size: Math.round(11 + (kw.peak / 100) * 24),
        color: kw.peak >= 90 ? T.up : kw.peak >= 85 ? T.accent : T.muted,
    }))

    const handleZoomSelect = (e) => {
        if (!selecting || !selectStart || !e) return
        const idx = SERIES_DATA.findIndex(d => d.label === e.activeLabel)
        const startIdx = SERIES_DATA.findIndex(d => d.label === selectStart)
        if (idx < 0 || startIdx < 0) return
        const l = Math.min(startIdx, idx)
        const r = Math.max(startIdx, idx)
        if (r - l > 2) setZoomDomain([l, r])
        setSelecting(false); setSelectStart(null); setSelectEnd(null)
    }

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
            {/* 페이지 헤더 */}
            <div style={{ marginBottom: 20 }}>
                <h1 style={{ fontSize: 20, fontWeight: 800, color: T.text, letterSpacing: '-0.02em' }}>홈</h1>
                <p style={{ fontSize: 13, color: T.muted, marginTop: 3 }}>한국 소비 트렌드 실시간 요약 · {now} 기준</p>
            </div>

            {/* 요약 카드 4종 */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 20 }}>
                {[
                    { label: '활성 트렌드', value: KEYWORDS.length, unit: '개', Icon: Icons.Fire, color: '#D4A574', clickable: false },
                    {
                        label: '평균 트렌드 스코어', value: avgScore, unit: '점', Icon: Icons.Chart, color: T.accent, clickable: false,
                        tooltip: '네이버 DataLab 50% + YouTube 30% + 계절 보정 20%'
                    },
                    { label: '상승 키워드', value: upCount, unit: '개', Icon: Icons.TrendUp, color: T.up, clickable: true },
                    { label: '하락 키워드', value: downCount, unit: '개', Icon: Icons.TrendDown, color: T.down, clickable: true },
                ].map((s, i) => {
                    const [showTip, setShowTip] = useState(false)
                    return (
                        <Card
                            key={i} hoverable={s.clickable}
                            onClick={s.clickable ? () => document.getElementById('ranking-section')?.scrollIntoView({ behavior: 'smooth' }) : undefined}
                            style={{ position: 'relative' }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 8 }}>
                                        <p style={{ fontSize: 11, color: T.muted }}>{s.label}</p>
                                        {s.tooltip && (
                                            <span style={{ cursor: 'help' }}
                                                onMouseEnter={() => setShowTip(true)}
                                                onMouseLeave={() => setShowTip(false)}
                                            >
                                                <Icons.Info size={12} color={T.muted} />
                                            </span>
                                        )}
                                    </div>
                                    <p style={{ fontSize: 26, fontWeight: 800, color: s.color }}>
                                        {s.value}<span style={{ fontSize: 13, color: T.muted, marginLeft: 3 }}>{s.unit}</span>
                                    </p>
                                    {s.clickable && <p style={{ fontSize: 10, color: T.muted, marginTop: 5 }}>클릭 시 랭킹으로 이동</p>}
                                </div>
                                <s.Icon size={20} color={s.color} />
                            </div>
                            {s.tooltip && showTip && (
                                <div style={{
                                    position: 'absolute', top: '105%', left: 0, right: 0, zIndex: 20,
                                    background: T.cardInner, border: `1px solid ${T.border}`,
                                    borderRadius: 8, padding: '10px 13px', fontSize: 11,
                                    color: T.textSoft, lineHeight: 1.7, boxShadow: '0 8px 28px rgba(0,0,0,0.3)',
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 5, color: T.accent }}>
                                        <Icons.Info size={12} color={T.accent} />
                                        <strong style={{ fontSize: 12 }}>트렌드 스코어 산출 기준</strong>
                                    </div>
                                    <div style={{ marginBottom: 4 }}>네이버 DataLab <strong style={{ color: T.accent }}>50%</strong></div>
                                    <div style={{ marginBottom: 4 }}>YouTube <strong style={{ color: T.accent }}>30%</strong></div>
                                    <div>계절 보정 <strong style={{ color: T.accent }}>20%</strong></div>
                                </div>
                            )}
                        </Card>
                    )
                })}
            </div>

            {/* 타임라인 + 랭킹 2열 */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 20, marginBottom: 20, alignItems: 'start' }}>
                {/* 타임라인 */}
                <Card style={{ minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
                        <SectionTitle
                            icon={<Icons.History size={15} color={T.accent} />}
                            title="트렌드 스코어 타임라인"
                            sub="최근 5년 월별 트렌드 변화 추이 · 드래그로 구간 확대"
                        />
                        <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
                            {zoomDomain && (
                                <button onClick={() => setZoomDomain(null)} style={btnBase(true, T.textSoft)}>
                                    <Icons.Reset size={12} color={T.textSoft} /><span>전체 보기</span>
                                </button>
                            )}
                            <button onClick={() => {
                                const cur = zoomDomain || [0, SERIES_DATA.length - 1]
                                const range = cur[1] - cur[0]
                                const half = Math.floor(range / 4)
                                if (range - half * 2 < 3) return
                                setZoomDomain([cur[0] + half, cur[1] - half])
                            }} style={btnBase(false)}>
                                <Icons.ZoomIn size={13} color={T.muted} />
                            </button>
                            <button onClick={() => {
                                if (!zoomDomain) return
                                const [l, r] = zoomDomain
                                const expand = Math.floor((r - l) / 3)
                                setZoomDomain([Math.max(0, l - expand), Math.min(SERIES_DATA.length - 1, r + expand)])
                            }} style={btnBase(false)}>
                                <Icons.ZoomOut size={13} color={T.muted} />
                            </button>
                        </div>
                    </div>

                    {/* 순위 버튼 */}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 14 }}>
                        {RANKING.map((kw, i) => {
                            const on = activeLines[kw.name]
                            const c = LINE_COLORS[KEYWORDS.findIndex(k => k.id === kw.id)]
                            return (
                                <button key={kw.name} onClick={() => toggleLine(kw.name)} style={{
                                    ...btnBase(on, c),
                                    borderColor: on ? c : T.border,
                                    color: on ? c : T.muted,
                                    background: on ? `${c}18` : 'transparent',
                                }}>
                                    <span style={{
                                        width: 16, height: 16, borderRadius: '50%',
                                        background: on ? c : T.border,
                                        color: on ? T.bg : T.muted,
                                        fontSize: 9, fontWeight: 800,
                                        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                                    }}>{i + 1}</span>
                                    <span>{kw.name}</span>
                                </button>
                            )
                        })}
                    </div>

                    {chartMounted && (
                        <div style={{ height: 300, userSelect: 'none' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart
                                    data={displayData}
                                    margin={{ top: 5, right: 20, left: -10, bottom: 5 }}
                                    onMouseDown={e => { if (e?.activeLabel) { setSelecting(true); setSelectStart(e.activeLabel); setSelectEnd(e.activeLabel) } }}
                                    onMouseMove={e => { if (selecting && e?.activeLabel) setSelectEnd(e.activeLabel) }}
                                    onMouseUp={handleZoomSelect}
                                >
                                    <CartesianGrid strokeDasharray="3 3" stroke={T.border} />
                                    <XAxis dataKey="label" tick={{ fill: T.muted, fontSize: 9 }} tickLine={false} axisLine={{ stroke: T.border }} interval={zoomDomain ? 1 : 4} />
                                    <YAxis domain={[0, 100]} tick={{ fill: T.muted, fontSize: 9 }} tickLine={false} axisLine={{ stroke: T.border }} />
                                    <Tooltip content={<DarkTooltip />} />
                                    {selecting && selectStart && selectEnd && (
                                        <ReferenceArea x1={selectStart} x2={selectEnd} fill={`${T.accent}15`} stroke={T.accent} strokeOpacity={0.5} />
                                    )}
                                    {KEYWORDS.map((kw, i) => (
                                        activeLines[kw.name] && (
                                            <Line key={kw.name} type="monotone" dataKey={kw.name}
                                                stroke={LINE_COLORS[i]} strokeWidth={1.8} dot={false}
                                                activeDot={{ r: 4, strokeWidth: 0, fill: LINE_COLORS[i] }}
                                                isAnimationActive animationDuration={900} animationEasing="ease-in-out"
                                            />
                                        )
                                    ))}
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                </Card>

                {/* 실시간 랭킹 */}
                <Card id="ranking-section">
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                        <SectionTitle icon={<Icons.Trophy size={14} color={T.accent} />} title="실시간 랭킹" />
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: T.muted, fontSize: 10 }}>
                            <Icons.Clock size={11} color={T.muted} /><span>{now}</span>
                        </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                        {RANKING.map((kw, i) => {
                            const CatIcon = catIconMap[kw.cat] || Icons.Tag
                            const isUp = kw.peak >= 90
                            const isDown = kw.peak < 85
                            const arrowColor = isUp ? T.up : isDown ? T.down : T.neutral
                            const ArrowIcon = isUp ? Icons.TrendUp : isDown ? Icons.TrendDown : null
                            const rankColors = ['#7C6FF7', '#C084FC', '#F5A623']
                            return (
                                <div key={kw.id} style={{
                                    display: 'flex', alignItems: 'center', gap: 8,
                                    padding: '7px 10px', borderRadius: 7,
                                    background: T.cardInner, border: `1px solid ${T.border}`,
                                    transition: 'border-color 0.15s ease',
                                }}
                                    onMouseEnter={e => e.currentTarget.style.borderColor = T.borderMid}
                                    onMouseLeave={e => e.currentTarget.style.borderColor = T.border}
                                >
                                    <div style={{
                                        width: 22, height: 22, borderRadius: '50%', flexShrink: 0,
                                        background: i < 3 ? `${rankColors[i]}22` : T.border,
                                        border: `1px solid ${i < 3 ? rankColors[i] : T.borderMid}`,
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        fontSize: 10, fontWeight: 800,
                                        color: i < 3 ? rankColors[i] : T.muted,
                                    }}>{i + 1}</div>
                                    <CatIcon size={13} color={T.catColors[kw.cat]} />
                                    <span style={{ flex: 1, fontSize: 12, fontWeight: 600, color: T.text }}>{kw.name}</span>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                                        {ArrowIcon && <ArrowIcon size={11} color={arrowColor} />}
                                        <span style={{ fontSize: 12, fontWeight: 700, color: arrowColor }}>{kw.peak}</span>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </Card>
            </div>

            {/* 하단 2열: 워드클라우드 + 카테고리 */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                <Card>
                    <SectionTitle icon={<Icons.Radar size={15} color={T.accent} />} title="트렌드 사이클" sub="스코어 비례 글자 크기" />
                    <WordCloud items={wcItems} />
                </Card>
                <Card>
                    <SectionTitle icon={<Icons.Box size={15} color={T.accent} />} title="카테고리별 트렌드" sub="카테고리 평균 트렌드 스코어" />
                    <div style={{ height: 200 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={CAT_AVGS} layout="vertical" margin={{ top: 4, right: 28, left: 18, bottom: 4 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke={T.border} horizontal={false} />
                                <XAxis type="number" domain={[0, 100]} tick={{ fill: T.muted, fontSize: 9 }} tickLine={false} axisLine={{ stroke: T.border }} />
                                <YAxis type="category" dataKey="label" tick={{ fill: T.textSoft, fontSize: 11 }} tickLine={false} axisLine={false} width={68} />
                                <Tooltip content={<BarDarkTooltip />} />
                                <Bar dataKey="avg" radius={[0, 5, 5, 0]} isAnimationActive animationDuration={900}>
                                    {CAT_AVGS.map((entry, i) => <Cell key={i} fill={T.catColors[entry.cat] || T.muted} />)}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
            </div>
        </div>
    )
}