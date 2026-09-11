import { KEYWORDS, SERIES_DATA, CAT_AVGS } from '../data/keywords'
import { PREDICTIONS, getProbBadge as getMockProbBadge } from '../data/predictions'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const normalizeCat = cat => (cat === 'snack' || cat === 'drink' ? 'food' : cat)

const withApiBase = path => `${API_BASE_URL}/api/trends/${path}`

/**
 * Fetches a TrendRadar endpoint when VITE_API_BASE_URL is configured.
 * During frontend-only development, or when the request fails, mock data is returned.
 */
async function fetchOrMock(path, mockData) {
    if (!API_BASE_URL) return mockData

    try {
        const response = await fetch(withApiBase(path))
        if (!response.ok) throw new Error(`API request failed: ${response.status}`)
        return await response.json()
    } catch (error) {
        console.warn(`[TrendRadar] Falling back to mock data for ${path}`, error)
        return mockData
    }
}

/**
 * @returns {Promise<Array<{id: number, name: string, cat: string, peak: number, year: number, month?: number}>>}
 */
export async function getRealtimeTrends() {
    return fetchOrMock('realtime', KEYWORDS)
}

/**
 * @returns {Promise<{keywords: Array, series: Array<Record<string, number|string>>}>}
 */
export async function getCycleData() {
    return fetchOrMock('cycle', {
        keywords: KEYWORDS,
        series: SERIES_DATA,
    })
}

/**
 * @param {{cat?: string, year?: number|string, month?: number|string}} filters
 * @returns {Promise<Array<{id: number, name: string, cat: string, peak: number, year: number, month?: number}>>}
 */
export async function getHistory({ cat, year, month } = {}) {
    const params = new URLSearchParams()
    if (cat) params.set('cat', cat)
    if (year) params.set('year', year)
    if (month) params.set('month', month)
    const query = params.toString()
    const path = query ? `history?${query}` : 'history'
    const mockHistory = KEYWORDS.filter(kw => {
        const normalizedCat = normalizeCat(kw.cat)
        return (
            (!cat || normalizedCat === cat) &&
            (!year || kw.year === Number(year)) &&
            (!month || kw.month === Number(month))
        )
    })

    return fetchOrMock(path, mockHistory)
}

/**
 * @returns {Promise<Array<{id: number, name: string, cat: string, prob: number, score: number, analysis: string}>>}
 */
export async function getPredictions() {
    return fetchOrMock('predict', PREDICTIONS)
}

/**
 * @returns {Promise<Array<{cat: string, label: string, avg: number, count: number}>>}
 */
export async function getDeclineSummary() {
    return fetchOrMock('decline', CAT_AVGS)
}

export function getProbBadge(prob) {
    return getMockProbBadge(prob)
}

export { withApiBase }
