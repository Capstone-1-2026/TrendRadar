import { KEYWORDS, RANKING, SERIES_DATA, CAT_AVGS, catLabelMap } from '../data/keywords'
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
        RANKING,
        data => validateArray(data, isKeywordItem, '/realtime')
    )
}

export async function getCycleData() {
    return request(
        'cycle',
        {},
        { keywords: KEYWORDS, series: SERIES_DATA },
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
    const mockSummary = CAT_AVGS.map(item => ({
        ...item,
        count: item.count ?? KEYWORDS.filter(kw => normalizeCat(kw.cat) === item.cat).length,
    }))

    return request(
        'decline',
        {},
        mockSummary,
        data => validateArray(data, isDeclineItem, '/decline')
    )
}

export function getProbBadge(prob) {
    return getMockProbBadge(prob)
}

export { catLabelMap }
