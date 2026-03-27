import { useState, useRef, useCallback, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { useTheme } from '../context/ThemeContext'
import { PREDICTIONS, getProbBadge } from '../data/predictions'
import { catLabelMap } from '../data/keywords'
import Card from '../components/common/Card'
import Badge from '../components/common/Badge'
import ProgressBar from '../components/common/ProgressBar'
import SectionTitle from '../components/common/SectionTitle'
import WordCloud from '../components/common/WordCloud'
import { Icons, catIconMap } from '../components/icons/Icons'

function PredBarShape(props) {
    const { T } = useTheme()
    const { x, y, width, height, fill, name } = props
    const selected = props.selected
    return (
        <g>
            <rect
                x={x} y={y + 1} width={width} height={Math.max(height - 2, 1)}
                rx={4} ry={4} fill={fill}
                stroke={selected ? T.accent : 'none'}
                strokeWidth={selected ? 1.5 : 0}
                style={{ filter: selected ? 'brightness(1.25)' : 'none', transition: 'filter 0.2s ease' }}
            />
        </g>
    )
}

function PredTooltip({ active, payload }) {
    const { T } = useTheme()
    if (!active || !payload?.length) return null
    const d = payload[0].payload
    return (
        <div style={{
            background: T.cardInner, border: `1px solid ${T.border}`,
            borderRadius: 8, padding: '9px 13px', boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
        }}>
            <p style={{ fontSize: 13, fontWeight: 700, color: T.text }}>{d.name}</p>
            <p style={{ fontSize: 11, color: T.muted, marginTop: 2 }}>{catLabelMap[d.cat] || d.cat} · 스코어 {d.score}</p>
            <p style={{ fontSize: 12, color: T.catColors[d.cat] || T.up, marginTop: 4 }}>
                예측 확률: <strong>{d.prob}%</strong>
            </p>
        </div>
    )
}

export default function AIPrediction() {
    const { T } = useTheme()
    const [selectedId, setSelectedId] = useState(null)
    const detailRef = useRef(null)

    const handleBarClick = useCallback(data => {
        if (!data) return
        const id = data.activePayload?.[0]?.payload?.id
        if (!id) return
        setSelectedId(prev => prev === id ? null : id)
    }, [])

    const handleWordClick = useCallback(id => {
        setSelectedId(prev => prev === id ? null : id)
    }, [])

    const selected = PREDICTIONS.find(p => p.id === selectedId)
    const badge = selected ? getProbBadge(selected.prob) : null

    useEffect(() => {
        if (selectedId && detailRef.current) {
            requestAnimationFrame(() => {
                detailRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
            })
        }
    }, [selectedId])

    const wcItems = PREDICTIONS.map(p => ({
        id: p.id, name: p.name,
        size: Math.round(10 + (p.prob / 100) * 26),
        color: T.catColors[p.cat] || T.muted,
    }))

    return (
        <div>
            <div style={{ marginBottom: 20 }}>
                <h1 style={{ fontSize: 20, fontWeight: 800, color: T.text, letterSpacing: '-0.02em' }}>AI 트렌드 예측</h1>
                <p style={{ fontSize: 13, color: T.muted, marginTop: 3 }}>머신러닝 기반 차세대 트렌드 예측 결과 · 2026.03 분석</p>
            </div>

            <Card style={{ marginBottom: 20 }}>
                <SectionTitle
                    icon={<Icons.Crystal size={15} color={T.accent} />}
                    title="다음 트렌드 예측 결과"
                    sub="글자 크기 = 예측 확률 비례 / 클릭 시 상세 분석"
                />
                <WordCloud items={wcItems} onClick={handleWordClick} selectedId={selectedId} />
            </Card>

            <Card>
                <SectionTitle
                    icon={<Icons.Chart size={15} color={T.accent} />}
                    title="예측 확률 순위"
                    sub="막대 또는 키워드를 클릭하면 상세 분석이 펼쳐집니다"
                />
                <div style={{ height: 340 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={PREDICTIONS} layout="vertical"
                            margin={{ top: 4, right: 56, left: 84, bottom: 4 }}
                            onClick={handleBarClick} style={{ cursor: 'pointer' }}
                        >
                            <CartesianGrid strokeDasharray="3 3" stroke={T.border} horizontal={false} />
                            <XAxis type="number" domain={[0, 100]} tick={{ fill: T.muted, fontSize: 9 }} tickLine={false} axisLine={{ stroke: T.border }} tickFormatter={v => `${v}%`} />
                            <YAxis type="category" dataKey="name" tick={{ fill: T.textSoft, fontSize: 11 }} tickLine={false} axisLine={false} width={80} />
                            <Tooltip content={<PredTooltip />} cursor={{ fill: `${T.accent}08` }} />
                            <Bar
                                dataKey="prob"
                                shape={props => <PredBarShape {...props} selected={props.name === selected?.name} />}
                                isAnimationActive animationDuration={900}
                            >
                                {PREDICTIONS.map(p => (
                                    <Cell key={p.id}
                                        fill={T.catColors[p.cat] || T.muted}
                                        opacity={selectedId && p.id !== selectedId ? 0.35 : 1}
                                        style={{ transition: 'opacity 0.2s ease' }}
                                    />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* 상세 블럭 */}
                <div
                    ref={detailRef}
                    style={{
                        maxHeight: selectedId ? 500 : 0,
                        opacity: selectedId ? 1 : 0,
                        transform: selectedId ? 'translateY(0)' : 'translateY(-8px)',
                        overflow: 'hidden',
                        transition: 'max-height 0.45s cubic-bezier(0.4,0,0.2,1), opacity 0.3s ease, transform 0.3s ease',
                        pointerEvents: selectedId ? 'auto' : 'none',
                    }}
                >
                    {selected && (
                        <div style={{
                            marginTop: 16, borderRadius: 10,
                            border: `1px solid ${T.catColors[selected.cat] || T.border}55`,
                            background: T.cardInner, padding: '18px 22px',
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                    {(() => { const CI = catIconMap[selected.cat] || Icons.Tag; return <CI size={20} color={T.catColors[selected.cat]} /> })()}
                                    <div>
                                        <p style={{ fontSize: 16, fontWeight: 800, color: T.text }}>{selected.name}</p>
                                        <Badge color={T.catColors[selected.cat] || T.muted}>{catLabelMap[selected.cat] || selected.cat}</Badge>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setSelectedId(null)}
                                    style={{
                                        background: T.card, border: `1px solid ${T.border}`, borderRadius: 7,
                                        color: T.muted, fontSize: 12, padding: '5px 11px', cursor: 'pointer',
                                        fontFamily: 'inherit', display: 'flex', alignItems: 'center', gap: 5,
                                    }}
                                    onMouseEnter={e => e.currentTarget.style.background = T.cardHov}
                                    onMouseLeave={e => e.currentTarget.style.background = T.card}
                                >
                                    <Icons.Close size={12} color={T.muted} /> 닫기
                                </button>
                            </div>

                            <div style={{ marginBottom: 14 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                                    <span style={{ fontSize: 12, color: T.muted }}>예측 확률</span>
                                    <span style={{ fontSize: 15, fontWeight: 800, color: T.catColors[selected.cat] }}>{selected.prob}%</span>
                                </div>
                                <ProgressBar value={selected.prob} color={T.catColors[selected.cat] || T.up} height={7} bg={T.border} />
                            </div>

                            {badge && (
                                <div style={{
                                    background: `${badge.bg}18`, border: `1px solid ${badge.bg}44`,
                                    borderRadius: 10, padding: '12px 15px', marginBottom: 14,
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                        <div style={{ flex: 1 }}>
                                            <p style={{ fontSize: 13, fontWeight: 700, color: T.text }}>{badge.text}</p>
                                            <p style={{ fontSize: 12, color: T.muted, marginTop: 2 }}>{badge.sub}</p>
                                        </div>
                                        <span style={{
                                            padding: '4px 12px', borderRadius: 999,
                                            background: badge.bg,
                                            color: badge.bg === '#F5E97A' ? '#141410' : '#fff',
                                            fontSize: 13, fontWeight: 800, flexShrink: 0,
                                        }}>{selected.prob}%</span>
                                    </div>
                                </div>
                            )}

                            <div style={{ marginBottom: 14 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                                    <span style={{ fontSize: 12, color: T.muted }}>트렌드 스코어</span>
                                    <span style={{ fontSize: 15, fontWeight: 800, color: T.text }}>{selected.score}</span>
                                </div>
                                <ProgressBar value={selected.score} color={T.accentSub} height={6} bg={T.border} />
                            </div>

                            <div style={{ background: T.card, borderRadius: 8, padding: '12px 15px', borderLeft: `3px solid ${T.accent}` }}>
                                <p style={{ fontSize: 11, color: T.accent, fontWeight: 700, marginBottom: 5, display: 'flex', alignItems: 'center', gap: 5 }}>
                                    <Icons.Robot size={12} color={T.accent} /> AI 분석
                                </p>
                                <p style={{ fontSize: 13, color: T.textSoft, lineHeight: 1.8 }}>{selected.analysis}</p>
                            </div>
                        </div>
                    )}
                </div>
            </Card>
        </div>
    )
}