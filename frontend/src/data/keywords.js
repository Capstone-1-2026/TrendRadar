export const KEYWORDS = [
    { id: 1, name: '허니버터칩', year: 2015, cat: 'snack', peak: 92 },
    { id: 2, name: '흑당버블티', year: 2018, cat: 'drink', peak: 90 },
    { id: 3, name: '달고나커피', year: 2020, cat: 'food', peak: 95 },
    { id: 4, name: '마라탕', year: 2019, cat: 'food', peak: 88 },
    { id: 5, name: '탕후루', year: 2022, cat: 'food', peak: 97 },
    { id: 6, name: '두바이초콜릿', year: 2024, cat: 'food', peak: 85 },
    { id: 7, name: 'Y2K패션', year: 2022, cat: 'fashion', peak: 88 },
    { id: 8, name: '레트로무드', year: 2023, cat: 'fashion', peak: 82 },
    { id: 9, name: '숏폼콘텐츠', year: 2022, cat: 'content', peak: 94 },
    { id: 10, name: 'AI아트', year: 2024, cat: 'technology', peak: 91 },
]

export const RANKING = [...KEYWORDS].sort((a, b) => b.peak - a.peak)

export const catLabelMap = {
    food: '음식', snack: '음식', drink: '음식',
    fashion: '패션', content: '콘텐츠',
    technology: '기술', lifestyle: '라이프',
}

function genSeries(kw) {
    const months = []
    for (let y = 2021; y <= 2026; y++) {
        for (let m = 1; m <= 12; m++) {
            if (y === 2026 && m > 3) break
            const peakMonth = kw.year * 12 + 7
            const curMonth = y * 12 + m
            const dist = Math.abs(curMonth - peakMonth)
            const raw = kw.peak * Math.exp(-Math.pow(dist / 18, 2))
            const noise = Math.sin(dist * 0.7 + kw.id) * 4
            const score = Math.max(2, Math.min(100, Math.round(raw + noise)))
            months.push({ label: `${y}.${String(m).padStart(2, '0')}`, score })
        }
    }
    return months
}

export const TIME_LABELS = genSeries(KEYWORDS[0]).map(d => d.label)

export const SERIES_DATA = TIME_LABELS.map((label, i) => {
    const pt = { label }
    KEYWORDS.forEach(kw => { pt[kw.name] = genSeries(kw)[i]?.score ?? 0 })
    return pt
})

export const CAT_AVGS = (() => {
    const map = {}
    KEYWORDS.forEach(kw => {
        const c = kw.cat === 'snack' || kw.cat === 'drink' ? 'food' : kw.cat
        if (!map[c]) map[c] = { total: 0, count: 0 }
        map[c].total += kw.peak
        map[c].count++
    })
    const korNames = {
        food: '음식', fashion: '패션',
        content: '콘텐츠', technology: '기술', lifestyle: '라이프'
    }
    return Object.entries(map).map(([cat, v]) => ({
        cat, label: korNames[cat] || cat,
        avg: Math.round(v.total / v.count),
    }))
})()