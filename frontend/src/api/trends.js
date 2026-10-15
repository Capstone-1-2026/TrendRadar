import { KEYWORDS, catLabelMap } from '../data/keywords'
import { PREDICTIONS, getProbBadge as getMockProbBadge } from '../data/predictions'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? ''
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA !== 'false'
const FALLBACK_TO_MOCK = import.meta.env.VITE_API_FALLBACK_TO_MOCK !== 'false'

const VALID_CATS = new Set(['food', 'snack', 'drink', 'fashion', 'content', 'technology', 'lifestyle'])
const VALID_DECLINE_CAUSES = new Set(['대체재 등장', '계절 종료', '공급 과잉', '부정 이슈', '자연 소멸'])

const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value)
const isNumber = value => typeof value === 'number' && Number.isFinite(value)
const isKeywordItem = item =>
    isObject(item) &&
    isNumber(item.id) &&
    typeof item.name === 'string' &&
    VALID_CATS.has(item.cat) &&
    isNumber(item.peak) &&
    isNumber(item.year)

const isHistoryItem = item =>
    isKeywordItem(item) &&
    typeof item.decline_cause === 'string' &&
    VALID_DECLINE_CAUSES.has(item.decline_cause) &&
    isNumber(item.drop_rate) &&
    typeof item.summary === 'string'

const isRealtimeItem = item =>
    isObject(item) &&
    isNumber(item.id) &&
    typeof item.name === 'string' &&
    VALID_CATS.has(item.cat) &&
    isNumber(item.score) &&
    isNumber(item.change_rate) &&
    typeof item.collected_at === 'string'

const isPredictItem = item =>
    isObject(item) &&
    isNumber(item.id) &&
    typeof item.name === 'string' &&
    VALID_CATS.has(item.cat) &&
    isNumber(item.prob) &&
    isNumber(item.score) &&
    typeof item.analysis === 'string'

const isDeclineItem = item =>
    isObject(item) &&
    typeof item.cat === 'string' &&
    typeof item.label === 'string' &&
    isNumber(item.avg) &&
    isNumber(item.count)

const isCycleResponse = data =>
    isObject(data) &&
    Array.isArray(data.keywords) &&
    data.keywords.every(isKeywordItem) &&
    Array.isArray(data.series) &&
    data.series.every(row => isObject(row) && typeof row.label === 'string')

const validateArray = (data, validator, endpoint) => {
    if (!Array.isArray(data) || !data.every(validator)) {
        throw new Error(`${endpoint} 응답 형식이 API_SPEC.md와 다릅니다.`)
    }
    return data
}

const normalizeCat = cat => (cat === 'snack' || cat === 'drink' ? 'food' : cat)

const CURRENT_TRENDS = [
    { id: 201, name: '러닝크루', cat: 'lifestyle', score: 89, peak: 89, year: 2026, change_rate: 42.5, collected_at: '2026-09-15T09:00:00+09:00' },
    { id: 202, name: '단백질 디저트', cat: 'food', score: 86, peak: 86, year: 2026, change_rate: 37.2, collected_at: '2026-09-15T09:00:00+09:00' },
    { id: 203, name: 'AI 쇼핑비서', cat: 'technology', score: 84, peak: 84, year: 2026, change_rate: 33.8, collected_at: '2026-09-15T09:00:00+09:00' },
    { id: 204, name: '초단편 드라마', cat: 'content', score: 81, peak: 81, year: 2026, change_rate: 28.6, collected_at: '2026-09-15T09:00:00+09:00' },
    { id: 205, name: '업사이클링 패션', cat: 'fashion', score: 77, peak: 77, year: 2026, change_rate: 21.4, collected_at: '2026-09-15T09:00:00+09:00' },
    { id: 206, name: '무알코올 페어링', cat: 'food', score: 73, peak: 73, year: 2026, change_rate: 18.9, collected_at: '2026-09-15T09:00:00+09:00' },
    { id: 207, name: '슬립테크 루틴', cat: 'technology', score: 70, peak: 70, year: 2026, change_rate: 15.7, collected_at: '2026-09-15T09:00:00+09:00' },
    { id: 208, name: '로컬 팝업투어', cat: 'lifestyle', score: 67, peak: 67, year: 2026, change_rate: 12.1, collected_at: '2026-09-15T09:00:00+09:00' },
]

function genCurrentSeries(keywords) {
    const labels = ['2026.04', '2026.05', '2026.06', '2026.07', '2026.08', '2026.09']
    return labels.map((label, index) => {
        const row = { label }
        keywords.forEach(kw => {
            const start = Math.max(12, kw.score - kw.change_rate - 18)
            const step = (kw.score - start) / (labels.length - 1)
            row[kw.name] = Math.round(start + step * index)
        })
        return row
    })
}

function getCurrentCategoryAverages() {
    const map = {}
    CURRENT_TRENDS.forEach(kw => {
        const cat = normalizeCat(kw.cat)
        if (!map[cat]) map[cat] = { total: 0, count: 0 }
        map[cat].total += kw.score
        map[cat].count++
    })

    return Object.entries(map).map(([cat, value]) => ({
        cat,
        label: catLabelMap[cat] || cat,
        avg: Math.round(value.total / value.count),
        count: value.count,
    }))
}

export const withApiBase = path => `${API_BASE_URL}/api/trends/${path.replace(/^\//, '')}`

const buildUrl = (path, params = {}) => {
    const url = new URL(withApiBase(path))
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '' && value !== '전체') {
            url.searchParams.set(key, value)
        }
    })
    return url.toString()
}

async function request(path, params, mockData, validate) {
    if (!API_BASE_URL || USE_MOCK_DATA) return mockData

    try {
        const response = await fetch(buildUrl(path, params), { headers: { Accept: 'application/json' } })
        if (!response.ok) throw new Error(`API request failed: ${response.status}`)
        return validate(await response.json())
    } catch (error) {
        if (FALLBACK_TO_MOCK) {
            console.warn(`[TrendRadar] Falling back to mock data for ${path}`, error)
            return mockData
        }
        throw error
    }
}

const withHistoryFields = keywords => keywords.map(kw => {
    const declineCauses = ['대체재 등장', '계절 종료', '공급 과잉', '부정 이슈', '자연 소멸']
    const declineCause = declineCauses[kw.id % declineCauses.length]
    const dropRate = Math.round((100 - kw.peak * 0.6) * 0.4 + 10)

    return {
        ...kw,
        decline_cause: declineCause,
        drop_rate: dropRate,
        summary: `${kw.name}은(는) ${kw.year}년 ${catLabelMap[kw.cat] || kw.cat} 카테고리에서 최고 스코어 ${kw.peak}점을 기록했습니다. 이후 ${declineCause} 원인으로 ${dropRate}% 하락세를 보였습니다.`,
    }
})

export async function getRealtimeTrends() {
    return request(
        'realtime',
        {},
        CURRENT_TRENDS,
        data => validateArray(data, isRealtimeItem, '/realtime')
    )
}

export async function getCycleData() {
    return request(
        'cycle',
        {},
        { keywords: CURRENT_TRENDS, series: genCurrentSeries(CURRENT_TRENDS) },
        data => {
            if (!isCycleResponse(data)) throw new Error('/cycle 응답 형식이 API_SPEC.md와 다릅니다.')
            return data
        }
    )
}

export async function getHistory({ cat, year } = {}) {
    const params = { cat: cat === '전체' ? undefined : cat, year: year === '전체' ? undefined : year }
    const mockHistory = withHistoryFields(KEYWORDS).filter(kw => {
        const normalizedCat = normalizeCat(kw.cat)
        return (!params.cat || normalizedCat === params.cat) && (!params.year || kw.year === Number(params.year))
    })

    return request(
        'history',
        params,
        mockHistory,
        data => validateArray(data, isHistoryItem, '/history')
    )
}

export async function getPredictions() {
    return request(
        'predict',
        {},
        PREDICTIONS,
        data => validateArray(data, isPredictItem, '/predict')
    )
}

export async function getDeclineSummary() {
    return request(
        'decline',
        {},
        getCurrentCategoryAverages(),
        data => validateArray(data, isDeclineItem, '/decline')
    )
}

export function getProbBadge(prob) {
    return getMockProbBadge(prob)
}

export { catLabelMap }
