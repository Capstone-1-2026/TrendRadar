from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Query
from models.schema import (
    CycleResponse,
    DeclineItem,
    HistoryItem,
    PredictItem,
    RealtimeItem,
)
from database import get_supabase

router = APIRouter()

_CAT_LABELS = {
    "food": "음식", "fashion": "패션", "content": "콘텐츠",
    "technology": "기술", "lifestyle": "라이프스타일",
    "snack": "음식", "drink": "음식",
}
_DECLINE_CAUSES = ["대체재 등장", "계절 종료", "공급 과잉", "부정 이슈", "자연 소멸"]
_DROP_RATES = {1: 18, 2: 32, 3: 15, 4: 41, 5: 23, 6: 12, 7: 27, 8: 35, 9: 20, 10: 29}

_RAW_KEYWORDS = [
    {"id": 1,  "name": "허니버터칩",   "year": 2015, "cat": "snack",      "peak": 92},
    {"id": 2,  "name": "흑당버블티",   "year": 2018, "cat": "drink",      "peak": 90},
    {"id": 3,  "name": "달고나커피",   "year": 2020, "cat": "food",       "peak": 95},
    {"id": 4,  "name": "마라탕",       "year": 2019, "cat": "food",       "peak": 88},
    {"id": 5,  "name": "탕후루",       "year": 2022, "cat": "food",       "peak": 97},
    {"id": 6,  "name": "두바이초콜릿", "year": 2024, "cat": "food",       "peak": 85},
    {"id": 7,  "name": "Y2K패션",      "year": 2022, "cat": "fashion",    "peak": 88},
    {"id": 8,  "name": "레트로무드",   "year": 2023, "cat": "fashion",    "peak": 82},
    {"id": 9,  "name": "숏폼콘텐츠",   "year": 2022, "cat": "content",    "peak": 94},
    {"id": 10, "name": "AI아트",       "year": 2024, "cat": "technology", "peak": 91},
]

_CURRENT_TRENDS = [
    {"id": 201, "name": "러닝크루", "cat": "lifestyle", "score": 89, "change_rate": 42.5, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 202, "name": "단백질 디저트", "cat": "food", "score": 86, "change_rate": 37.2, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 203, "name": "AI 쇼핑비서", "cat": "technology", "score": 84, "change_rate": 33.8, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 204, "name": "초단편 드라마", "cat": "content", "score": 81, "change_rate": 28.6, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 205, "name": "업사이클링 패션", "cat": "fashion", "score": 77, "change_rate": 21.4, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 206, "name": "무알코올 페어링", "cat": "food", "score": 73, "change_rate": 18.9, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 207, "name": "슬립테크 루틴", "cat": "technology", "score": 70, "change_rate": 15.7, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 208, "name": "로컬 팝업투어", "cat": "lifestyle", "score": 67, "change_rate": 12.1, "collected_at": "2026-09-15T09:00:00+09:00"},
]

_PREDICTIONS = [
    {"id": 101, "name": "단백질 디저트", "cat": "food", "prob": 84, "score": 82, "analysis": "고단백 간식과 저당 디저트 관심이 함께 상승하고 있어 편의점, 카페, 홈트 소비층으로 확산 가능성이 높습니다."},
    {"id": 102, "name": "AI 쇼핑비서", "cat": "technology", "prob": 79, "score": 77, "analysis": "가격 비교, 사이즈 추천, 리뷰 요약 기능이 커머스 앱에 빠르게 붙으면서 개인화 쇼핑 도우미 수요가 커지고 있습니다."},
    {"id": 103, "name": "로컬 러닝크루", "cat": "lifestyle", "prob": 72, "score": 74, "analysis": "지역 기반 운동 모임과 기록 공유 문화가 결합되며 커뮤니티형 라이프스타일 트렌드로 성장할 가능성이 있습니다."},
    {"id": 104, "name": "업사이클링 패션", "cat": "fashion", "prob": 65, "score": 68, "analysis": "친환경 소비와 개성 있는 리폼 콘텐츠가 맞물리며 소규모 브랜드와 중고 플랫폼 중심으로 확산될 수 있습니다."},
    {"id": 105, "name": "초단편 드라마", "cat": "content", "prob": 58, "score": 62, "analysis": "숏폼 플랫폼에서 회차형 콘텐츠 소비가 늘면서 짧은 러닝타임의 연속극 포맷이 더 넓어질 가능성이 있습니다."},
    {"id": 106, "name": "슬립테크 루틴", "cat": "technology", "prob": 49, "score": 54, "analysis": "수면 측정 기기와 회복 중심 건강 관리 앱이 늘고 있으나 일상 사용 습관으로 자리 잡는지가 관건입니다."},
    {"id": 107, "name": "무알코올 페어링", "cat": "food", "prob": 42, "score": 47, "analysis": "저도수/무알코올 음료 관심은 꾸준하지만 외식 메뉴와 함께 소비되는 문화로 확장될지는 더 확인이 필요합니다."},
    {"id": 108, "name": "책맥 모임", "cat": "lifestyle", "prob": 34, "score": 39, "analysis": "독서 모임과 가벼운 취향 커뮤니티가 결합된 형태로 니치 수요는 있으나 대중 확산은 아직 제한적입니다."},
    {"id": 109, "name": "AI 아바타 팬덤", "cat": "content", "prob": 27, "score": 31, "analysis": "기술 관심은 높지만 지속적인 팬덤 소비로 이어지려면 캐릭터성과 서사가 더 필요합니다."},
    {"id": 110, "name": "스마트 텃밭", "cat": "lifestyle", "prob": 18, "score": 24, "analysis": "홈가드닝과 IoT가 맞닿아 있으나 설치 비용과 관리 난도가 있어 단기 대중화 가능성은 낮습니다."},
]


def _normalize_cat(cat: str) -> str:
    return "food" if cat in ("snack", "drink") else cat


def _mock_realtime():
    return sorted([
        {"id": kw["id"], "name": kw["name"], "cat": _normalize_cat(kw["cat"]),
         "score": kw["score"], "change_rate": kw["change_rate"], "collected_at": kw["collected_at"]}
        for kw in _CURRENT_TRENDS
    ], key=lambda x: x["score"], reverse=True)


def _mock_cycle():
    labels = ["2026.04", "2026.05", "2026.06", "2026.07", "2026.08", "2026.09"]
    series = []
    for index, label in enumerate(labels):
        row = {"label": label}
        for kw in _CURRENT_TRENDS:
            start = max(12, kw["score"] - kw["change_rate"] - 18)
            step = (kw["score"] - start) / (len(labels) - 1)
            row[kw["name"]] = round(start + step * index)
        series.append(row)
    keywords = sorted([
        {"id": kw["id"], "name": kw["name"], "cat": _normalize_cat(kw["cat"]),
         "peak": kw["score"], "year": int(kw["collected_at"][:4])}
        for kw in _CURRENT_TRENDS
    ], key=lambda x: x["peak"], reverse=True)
    return {"keywords": keywords, "series": series}


def _mock_history(cat, year):
    keywords = sorted([{**kw, "cat": _normalize_cat(kw["cat"])} for kw in _RAW_KEYWORDS],
                      key=lambda x: x["peak"], reverse=True)
    if cat:
        keywords = [kw for kw in keywords if kw["cat"] == cat]
    if year:
        keywords = [kw for kw in keywords if kw["year"] == year]
    result = []
    for kw in keywords:
        cause = _DECLINE_CAUSES[kw["id"] % 5]
        drop = _DROP_RATES.get(kw["id"], 20)
        result.append({**kw, "decline_cause": cause, "drop_rate": drop,
            "summary": f"{kw['name']}은(는) {kw['year']}년 {_CAT_LABELS.get(kw['cat'], kw['cat'])} 카테고리에서 최고 스코어 {kw['peak']}점을 기록했습니다. 이후 {cause} 원인으로 {drop}% 하락세를 보였습니다."})
    return result


def _mock_predict():
    return sorted(_PREDICTIONS, key=lambda x: x["prob"], reverse=True)


def _mock_decline():
    cat_data = defaultdict(list)
    for kw in _CURRENT_TRENDS:
        cat_data[_normalize_cat(kw["cat"])].append(kw["score"])
    return sorted([
        {"cat": cat, "label": _CAT_LABELS.get(cat, cat),
         "avg": round(sum(scores) / len(scores), 1), "count": len(scores)}
        for cat, scores in cat_data.items()
    ], key=lambda x: x["avg"], reverse=True)


# ─── Supabase 실DB 로더 ───────────────────────────────────────────

def _load_realtime(sb):
    res = sb.table("trend_realtime").select(
        "keyword_id, trend_score, change_rate, collected_at, trend_keywords(name, category)"
    ).order("trend_score", desc=True).execute()

    items = []
    for row in res.data:
        kw = row.get("trend_keywords") or {}
        if row.get("trend_score") is None:
            continue
        items.append({
            "id": row["keyword_id"],
            "name": kw.get("name", ""),
            "cat": _normalize_cat(kw.get("category", "food")),
            "score": int(round(row["trend_score"])),
            "change_rate": round(float(row.get("change_rate") or 0), 1),
            "collected_at": str(row.get("collected_at", "")),
        })
    return items or None


def _load_cycle(sb):
    res = sb.table("trend_history").select(
        "keyword_id, date, year, month, trend_score, trend_keywords(name, category)"
    ).order("date", desc=False).execute()

    if not res.data:
        return None

    keyword_peaks = {}
    series_map = defaultdict(dict)
    for row in res.data:
        kw = row.get("trend_keywords") or {}
        if row.get("trend_score") is None or row.get("date") is None:
            continue
        kid = row["keyword_id"]
        score = row["trend_score"]
        name = kw.get("name", "")
        cat = _normalize_cat(kw.get("category", "food"))
        year = row.get("year", 0)

        if kid not in keyword_peaks or score > keyword_peaks[kid]["peak"]:
            keyword_peaks[kid] = {"id": kid, "name": name, "cat": cat, "peak": int(round(score)), "year": int(year)}

        label = f"{row.get('year')}.{str(row.get('month', 1)).zfill(2)}"
        series_map[label][name] = int(round(score))

    if not keyword_peaks:
        return None

    return {
        "keywords": sorted(keyword_peaks.values(), key=lambda x: x["peak"], reverse=True),
        "series": [{"label": label, **scores} for label, scores in sorted(series_map.items())],
    }


def _load_history(sb, cat, year):
    res = sb.table("trend_history").select(
        "keyword_id, trend_score, year, trend_keywords(name, category)"
    ).execute()

    if not res.data:
        return None

    keyword_peaks = {}
    for row in res.data:
        kw = row.get("trend_keywords") or {}
        kid = row["keyword_id"]
        score = row.get("trend_score") or 0
        if kid not in keyword_peaks or score > keyword_peaks[kid]["peak"]:
            keyword_peaks[kid] = {
                "id": kid,
                "name": kw.get("name", ""),
                "cat": _normalize_cat(kw.get("category", "food")),
                "peak": int(round(score)),
                "year": int(row.get("year") or 0),
            }

    result = []
    for kid, kw in keyword_peaks.items():
        if cat and kw["cat"] != cat:
            continue
        if year and kw["year"] != year:
            continue
        cause = _DECLINE_CAUSES[kid % 5]
        drop = _DROP_RATES.get(kid, 20)
        result.append({**kw, "decline_cause": cause, "drop_rate": drop,
            "summary": f"{kw['name']}은(는) {kw['year']}년 {_CAT_LABELS.get(kw['cat'], kw['cat'])} 카테고리에서 최고 스코어 {kw['peak']}점을 기록했습니다. 이후 {cause} 원인으로 {drop}% 하락세를 보였습니다."})
    return sorted(result, key=lambda x: x["peak"], reverse=True) or None


def _load_predict(sb):
    res = sb.table("trend_predictions").select(
        "keyword_id, prob, trend_score, predicted_at, trend_keywords(name, category)"
    ).order("predicted_at", desc=True).execute()

    if not res.data:
        return None

    seen = set()
    result = []
    for row in res.data:
        kid = row["keyword_id"]
        if kid in seen:
            continue
        seen.add(kid)
        kw = row.get("trend_keywords") or {}
        prob_raw = row.get("prob") or 0
        prob = int(round(prob_raw * 100 if prob_raw <= 1 else prob_raw))
        score = int(round(row.get("trend_score") or 0))
        name = kw.get("name", "")
        result.append({
            "id": kid, "name": name,
            "cat": _normalize_cat(kw.get("category", "food")),
            "prob": prob, "score": score,
            "analysis": f"{name}의 향후 트렌드 스코어는 {score}점으로 예측되며 유행 가능성은 {prob}%입니다.",
        })
    return sorted(result, key=lambda x: x["prob"], reverse=True) or None


def _load_decline(sb):
    res = sb.table("trend_history").select(
        "trend_score, trend_keywords(category)"
    ).execute()

    if not res.data:
        return None

    cat_data = defaultdict(list)
    for row in res.data:
        kw = row.get("trend_keywords") or {}
        cat = _normalize_cat(kw.get("category", "food"))
        if row.get("trend_score") is not None:
            cat_data[cat].append(row["trend_score"])

    return sorted([
        {"cat": cat, "label": _CAT_LABELS.get(cat, cat),
         "avg": round(sum(scores) / len(scores), 1), "count": len(scores)}
        for cat, scores in cat_data.items()
    ], key=lambda x: x["avg"], reverse=True) or None


def _with_sb(loader_fn, fallback_fn):
    sb = get_supabase()
    if sb is None:
        return fallback_fn()
    try:
        result = loader_fn(sb)
        return result if result else fallback_fn()
    except Exception as e:
        print(f"⚠️ DB 조회 실패 → 목업: {e}")
        return fallback_fn()


@router.get("/realtime", response_model=list[RealtimeItem])
def get_realtime():
    return _with_sb(_load_realtime, _mock_realtime)


@router.get("/cycle", response_model=CycleResponse)
def get_cycle():
    return _with_sb(_load_cycle, _mock_cycle)


@router.get("/history", response_model=list[HistoryItem])
def get_history(
    cat: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
):
    return _with_sb(lambda sb: _load_history(sb, cat, year), lambda: _mock_history(cat, year))


@router.get("/predict", response_model=list[PredictItem])
def get_predict():
    return _with_sb(_load_predict, _mock_predict)


@router.get("/decline", response_model=list[DeclineItem])
def get_decline():
    return _with_sb(_load_decline, _mock_decline)
EOFcat > /Users/apple/TrendRadar/backend/api/trends.py << 'EOF'
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Query
from models.schema import (
    CycleResponse,
    DeclineItem,
    HistoryItem,
    PredictItem,
    RealtimeItem,
)
from database import get_supabase

router = APIRouter()

_CAT_LABELS = {
    "food": "음식", "fashion": "패션", "content": "콘텐츠",
    "technology": "기술", "lifestyle": "라이프스타일",
    "snack": "음식", "drink": "음식",
}
_DECLINE_CAUSES = ["대체재 등장", "계절 종료", "공급 과잉", "부정 이슈", "자연 소멸"]
_DROP_RATES = {1: 18, 2: 32, 3: 15, 4: 41, 5: 23, 6: 12, 7: 27, 8: 35, 9: 20, 10: 29}

_RAW_KEYWORDS = [
    {"id": 1,  "name": "허니버터칩",   "year": 2015, "cat": "snack",      "peak": 92},
    {"id": 2,  "name": "흑당버블티",   "year": 2018, "cat": "drink",      "peak": 90},
    {"id": 3,  "name": "달고나커피",   "year": 2020, "cat": "food",       "peak": 95},
    {"id": 4,  "name": "마라탕",       "year": 2019, "cat": "food",       "peak": 88},
    {"id": 5,  "name": "탕후루",       "year": 2022, "cat": "food",       "peak": 97},
    {"id": 6,  "name": "두바이초콜릿", "year": 2024, "cat": "food",       "peak": 85},
    {"id": 7,  "name": "Y2K패션",      "year": 2022, "cat": "fashion",    "peak": 88},
    {"id": 8,  "name": "레트로무드",   "year": 2023, "cat": "fashion",    "peak": 82},
    {"id": 9,  "name": "숏폼콘텐츠",   "year": 2022, "cat": "content",    "peak": 94},
    {"id": 10, "name": "AI아트",       "year": 2024, "cat": "technology", "peak": 91},
]

_CURRENT_TRENDS = [
    {"id": 201, "name": "러닝크루", "cat": "lifestyle", "score": 89, "change_rate": 42.5, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 202, "name": "단백질 디저트", "cat": "food", "score": 86, "change_rate": 37.2, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 203, "name": "AI 쇼핑비서", "cat": "technology", "score": 84, "change_rate": 33.8, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 204, "name": "초단편 드라마", "cat": "content", "score": 81, "change_rate": 28.6, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 205, "name": "업사이클링 패션", "cat": "fashion", "score": 77, "change_rate": 21.4, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 206, "name": "무알코올 페어링", "cat": "food", "score": 73, "change_rate": 18.9, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 207, "name": "슬립테크 루틴", "cat": "technology", "score": 70, "change_rate": 15.7, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 208, "name": "로컬 팝업투어", "cat": "lifestyle", "score": 67, "change_rate": 12.1, "collected_at": "2026-09-15T09:00:00+09:00"},
]

_PREDICTIONS = [
    {"id": 101, "name": "단백질 디저트", "cat": "food", "prob": 84, "score": 82, "analysis": "고단백 간식과 저당 디저트 관심이 함께 상승하고 있어 편의점, 카페, 홈트 소비층으로 확산 가능성이 높습니다."},
    {"id": 102, "name": "AI 쇼핑비서", "cat": "technology", "prob": 79, "score": 77, "analysis": "가격 비교, 사이즈 추천, 리뷰 요약 기능이 커머스 앱에 빠르게 붙으면서 개인화 쇼핑 도우미 수요가 커지고 있습니다."},
    {"id": 103, "name": "로컬 러닝크루", "cat": "lifestyle", "prob": 72, "score": 74, "analysis": "지역 기반 운동 모임과 기록 공유 문화가 결합되며 커뮤니티형 라이프스타일 트렌드로 성장할 가능성이 있습니다."},
    {"id": 104, "name": "업사이클링 패션", "cat": "fashion", "prob": 65, "score": 68, "analysis": "친환경 소비와 개성 있는 리폼 콘텐츠가 맞물리며 소규모 브랜드와 중고 플랫폼 중심으로 확산될 수 있습니다."},
    {"id": 105, "name": "초단편 드라마", "cat": "content", "prob": 58, "score": 62, "analysis": "숏폼 플랫폼에서 회차형 콘텐츠 소비가 늘면서 짧은 러닝타임의 연속극 포맷이 더 넓어질 가능성이 있습니다."},
    {"id": 106, "name": "슬립테크 루틴", "cat": "technology", "prob": 49, "score": 54, "analysis": "수면 측정 기기와 회복 중심 건강 관리 앱이 늘고 있으나 일상 사용 습관으로 자리 잡는지가 관건입니다."},
    {"id": 107, "name": "무알코올 페어링", "cat": "food", "prob": 42, "score": 47, "analysis": "저도수/무알코올 음료 관심은 꾸준하지만 외식 메뉴와 함께 소비되는 문화로 확장될지는 더 확인이 필요합니다."},
    {"id": 108, "name": "책맥 모임", "cat": "lifestyle", "prob": 34, "score": 39, "analysis": "독서 모임과 가벼운 취향 커뮤니티가 결합된 형태로 니치 수요는 있으나 대중 확산은 아직 제한적입니다."},
    {"id": 109, "name": "AI 아바타 팬덤", "cat": "content", "prob": 27, "score": 31, "analysis": "기술 관심은 높지만 지속적인 팬덤 소비로 이어지려면 캐릭터성과 서사가 더 필요합니다."},
    {"id": 110, "name": "스마트 텃밭", "cat": "lifestyle", "prob": 18, "score": 24, "analysis": "홈가드닝과 IoT가 맞닿아 있으나 설치 비용과 관리 난도가 있어 단기 대중화 가능성은 낮습니다."},
]


def _normalize_cat(cat: str) -> str:
    return "food" if cat in ("snack", "drink") else cat


def _mock_realtime():
    return sorted([
        {"id": kw["id"], "name": kw["name"], "cat": _normalize_cat(kw["cat"]),
         "score": kw["score"], "change_rate": kw["change_rate"], "collected_at": kw["collected_at"]}
        for kw in _CURRENT_TRENDS
    ], key=lambda x: x["score"], reverse=True)


def _mock_cycle():
    labels = ["2026.04", "2026.05", "2026.06", "2026.07", "2026.08", "2026.09"]
    series = []
    for index, label in enumerate(labels):
        row = {"label": label}
        for kw in _CURRENT_TRENDS:
            start = max(12, kw["score"] - kw["change_rate"] - 18)
            step = (kw["score"] - start) / (len(labels) - 1)
            row[kw["name"]] = round(start + step * index)
        series.append(row)
    keywords = sorted([
        {"id": kw["id"], "name": kw["name"], "cat": _normalize_cat(kw["cat"]),
         "peak": kw["score"], "year": int(kw["collected_at"][:4])}
        for kw in _CURRENT_TRENDS
    ], key=lambda x: x["peak"], reverse=True)
    return {"keywords": keywords, "series": series}


def _mock_history(cat, year):
    keywords = sorted([{**kw, "cat": _normalize_cat(kw["cat"])} for kw in _RAW_KEYWORDS],
                      key=lambda x: x["peak"], reverse=True)
    if cat:
        keywords = [kw for kw in keywords if kw["cat"] == cat]
    if year:
        keywords = [kw for kw in keywords if kw["year"] == year]
    result = []
    for kw in keywords:
        cause = _DECLINE_CAUSES[kw["id"] % 5]
        drop = _DROP_RATES.get(kw["id"], 20)
        result.append({**kw, "decline_cause": cause, "drop_rate": drop,
            "summary": f"{kw['name']}은(는) {kw['year']}년 {_CAT_LABELS.get(kw['cat'], kw['cat'])} 카테고리에서 최고 스코어 {kw['peak']}점을 기록했습니다. 이후 {cause} 원인으로 {drop}% 하락세를 보였습니다."})
    return result


def _mock_predict():
    return sorted(_PREDICTIONS, key=lambda x: x["prob"], reverse=True)


def _mock_decline():
    cat_data = defaultdict(list)
    for kw in _CURRENT_TRENDS:
        cat_data[_normalize_cat(kw["cat"])].append(kw["score"])
    return sorted([
        {"cat": cat, "label": _CAT_LABELS.get(cat, cat),
         "avg": round(sum(scores) / len(scores), 1), "count": len(scores)}
        for cat, scores in cat_data.items()
    ], key=lambda x: x["avg"], reverse=True)


# ─── Supabase 실DB 로더 ───────────────────────────────────────────

def _load_realtime(sb):
    res = sb.table("trend_realtime").select(
        "keyword_id, trend_score, change_rate, collected_at, trend_keywords(name, category)"
    ).order("trend_score", desc=True).execute()

    items = []
    for row in res.data:
        kw = row.get("trend_keywords") or {}
        if row.get("trend_score") is None:
            continue
        items.append({
            "id": row["keyword_id"],
            "name": kw.get("name", ""),
            "cat": _normalize_cat(kw.get("category", "food")),
            "score": int(round(row["trend_score"])),
            "change_rate": round(float(row.get("change_rate") or 0), 1),
            "collected_at": str(row.get("collected_at", "")),
        })
    return items or None


def _load_cycle(sb):
    res = sb.table("trend_history").select(
        "keyword_id, date, year, month, trend_score, trend_keywords(name, category)"
    ).order("date", desc=False).execute()

    if not res.data:
        return None

    keyword_peaks = {}
    series_map = defaultdict(dict)
    for row in res.data:
        kw = row.get("trend_keywords") or {}
        if row.get("trend_score") is None or row.get("date") is None:
            continue
        kid = row["keyword_id"]
        score = row["trend_score"]
        name = kw.get("name", "")
        cat = _normalize_cat(kw.get("category", "food"))
        year = row.get("year", 0)

        if kid not in keyword_peaks or score > keyword_peaks[kid]["peak"]:
            keyword_peaks[kid] = {"id": kid, "name": name, "cat": cat, "peak": int(round(score)), "year": int(year)}

        label = f"{row.get('year')}.{str(row.get('month', 1)).zfill(2)}"
        series_map[label][name] = int(round(score))

    if not keyword_peaks:
        return None

    return {
        "keywords": sorted(keyword_peaks.values(), key=lambda x: x["peak"], reverse=True),
        "series": [{"label": label, **scores} for label, scores in sorted(series_map.items())],
    }


def _load_history(sb, cat, year):
    res = sb.table("trend_history").select(
        "keyword_id, trend_score, year, trend_keywords(name, category)"
    ).execute()

    if not res.data:
        return None

    keyword_peaks = {}
    for row in res.data:
        kw = row.get("trend_keywords") or {}
        kid = row["keyword_id"]
        score = row.get("trend_score") or 0
        if kid not in keyword_peaks or score > keyword_peaks[kid]["peak"]:
            keyword_peaks[kid] = {
                "id": kid,
                "name": kw.get("name", ""),
                "cat": _normalize_cat(kw.get("category", "food")),
                "peak": int(round(score)),
                "year": int(row.get("year") or 0),
            }

    result = []
    for kid, kw in keyword_peaks.items():
        if cat and kw["cat"] != cat:
            continue
        if year and kw["year"] != year:
            continue
        cause = _DECLINE_CAUSES[kid % 5]
        drop = _DROP_RATES.get(kid, 20)
        result.append({**kw, "decline_cause": cause, "drop_rate": drop,
            "summary": f"{kw['name']}은(는) {kw['year']}년 {_CAT_LABELS.get(kw['cat'], kw['cat'])} 카테고리에서 최고 스코어 {kw['peak']}점을 기록했습니다. 이후 {cause} 원인으로 {drop}% 하락세를 보였습니다."})
    return sorted(result, key=lambda x: x["peak"], reverse=True) or None


def _load_predict(sb):
    res = sb.table("trend_predictions").select(
        "keyword_id, prob, trend_score, predicted_at, trend_keywords(name, category)"
    ).order("predicted_at", desc=True).execute()

    if not res.data:
        return None

    seen = set()
    result = []
    for row in res.data:
        kid = row["keyword_id"]
        if kid in seen:
            continue
        seen.add(kid)
        kw = row.get("trend_keywords") or {}
        prob_raw = row.get("prob") or 0
        prob = int(round(prob_raw * 100 if prob_raw <= 1 else prob_raw))
        score = int(round(row.get("trend_score") or 0))
        name = kw.get("name", "")
        result.append({
            "id": kid, "name": name,
            "cat": _normalize_cat(kw.get("category", "food")),
            "prob": prob, "score": score,
            "analysis": f"{name}의 향후 트렌드 스코어는 {score}점으로 예측되며 유행 가능성은 {prob}%입니다.",
        })
    return sorted(result, key=lambda x: x["prob"], reverse=True) or None


def _load_decline(sb):
    res = sb.table("trend_history").select(
        "trend_score, trend_keywords(category)"
    ).execute()

    if not res.data:
        return None

    cat_data = defaultdict(list)
    for row in res.data:
        kw = row.get("trend_keywords") or {}
        cat = _normalize_cat(kw.get("category", "food"))
        if row.get("trend_score") is not None:
            cat_data[cat].append(row["trend_score"])

    return sorted([
        {"cat": cat, "label": _CAT_LABELS.get(cat, cat),
         "avg": round(sum(scores) / len(scores), 1), "count": len(scores)}
        for cat, scores in cat_data.items()
    ], key=lambda x: x["avg"], reverse=True) or None


def _with_sb(loader_fn, fallback_fn):
    sb = get_supabase()
    if sb is None:
        return fallback_fn()
    try:
        result = loader_fn(sb)
        return result if result else fallback_fn()
    except Exception as e:
        print(f"⚠️ DB 조회 실패 → 목업: {e}")
        return fallback_fn()


@router.get("/realtime", response_model=list[RealtimeItem])
def get_realtime():
    return _with_sb(_load_realtime, _mock_realtime)


@router.get("/cycle", response_model=CycleResponse)
def get_cycle():
    return _with_sb(_load_cycle, _mock_cycle)


@router.get("/history", response_model=list[HistoryItem])
def get_history(
    cat: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
):
    return _with_sb(lambda sb: _load_history(sb, cat, year), lambda: _mock_history(cat, year))


@router.get("/predict", response_model=list[PredictItem])
def get_predict():
    return _with_sb(_load_predict, _mock_predict)


@router.get("/decline", response_model=list[DeclineItem])
def get_decline():
    return _with_sb(_load_decline, _mock_decline)
