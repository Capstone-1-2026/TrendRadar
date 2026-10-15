from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import SessionLocal
from models.schema import (
    CycleResponse,
    DeclineEvent,
    DeclineItem,
    HistoryItem,
    PredictItem,
    RealtimeItem,
    TrendHistory,
    TrendKeyword,
    TrendPrediction,
    TrendRealtime,
)

router = APIRouter()

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
    {"id": 201, "name": "러닝크루", "year": 2026, "cat": "lifestyle", "peak": 89, "score": 89, "change_rate": 42.5, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 202, "name": "단백질 디저트", "year": 2026, "cat": "food", "peak": 86, "score": 86, "change_rate": 37.2, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 203, "name": "AI 쇼핑비서", "year": 2026, "cat": "technology", "peak": 84, "score": 84, "change_rate": 33.8, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 204, "name": "초단편 드라마", "year": 2026, "cat": "content", "peak": 81, "score": 81, "change_rate": 28.6, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 205, "name": "업사이클링 패션", "year": 2026, "cat": "fashion", "peak": 77, "score": 77, "change_rate": 21.4, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 206, "name": "무알코올 페어링", "year": 2026, "cat": "food", "peak": 73, "score": 73, "change_rate": 18.9, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 207, "name": "슬립테크 루틴", "year": 2026, "cat": "technology", "peak": 70, "score": 70, "change_rate": 15.7, "collected_at": "2026-09-15T09:00:00+09:00"},
    {"id": 208, "name": "로컬 팝업투어", "year": 2026, "cat": "lifestyle", "peak": 67, "score": 67, "change_rate": 12.1, "collected_at": "2026-09-15T09:00:00+09:00"},
]

_PREDICTIONS = [
    {"id": 101, "name": "단백질 디저트", "cat": "food", "prob": 84, "score": 82,
     "analysis": "고단백 간식과 저당 디저트 관심이 함께 상승하고 있어 편의점, 카페, 홈트 소비층으로 확산 가능성이 높습니다."},
    {"id": 102, "name": "AI 쇼핑비서", "cat": "technology", "prob": 79, "score": 77,
     "analysis": "가격 비교, 사이즈 추천, 리뷰 요약 기능이 커머스 앱에 빠르게 붙으면서 개인화 쇼핑 도우미 수요가 커지고 있습니다."},
    {"id": 103, "name": "로컬 러닝크루", "cat": "lifestyle", "prob": 72, "score": 74,
     "analysis": "지역 기반 운동 모임과 기록 공유 문화가 결합되며 커뮤니티형 라이프스타일 트렌드로 성장할 가능성이 있습니다."},
    {"id": 104, "name": "업사이클링 패션", "cat": "fashion", "prob": 65, "score": 68,
     "analysis": "친환경 소비와 개성 있는 리폼 콘텐츠가 맞물리며 소규모 브랜드와 중고 플랫폼 중심으로 확산될 수 있습니다."},
    {"id": 105, "name": "초단편 드라마", "cat": "content", "prob": 58, "score": 62,
     "analysis": "숏폼 플랫폼에서 회차형 콘텐츠 소비가 늘면서 짧은 러닝타임의 연속극 포맷이 더 넓어질 가능성이 있습니다."},
    {"id": 106, "name": "슬립테크 루틴", "cat": "technology", "prob": 49, "score": 54,
     "analysis": "수면 측정 기기와 회복 중심 건강 관리 앱이 늘고 있으나 일상 사용 습관으로 자리 잡는지가 관건입니다."},
    {"id": 107, "name": "무알코올 페어링", "cat": "food", "prob": 42, "score": 47,
     "analysis": "저도수/무알코올 음료 관심은 꾸준하지만 외식 메뉴와 함께 소비되는 문화로 확장될지는 더 확인이 필요합니다."},
    {"id": 108, "name": "책맥 모임", "cat": "lifestyle", "prob": 34, "score": 39,
     "analysis": "독서 모임과 가벼운 취향 커뮤니티가 결합된 형태로 니치 수요는 있으나 대중 확산은 아직 제한적입니다."},
    {"id": 109, "name": "AI 아바타 팬덤", "cat": "content", "prob": 27, "score": 31,
     "analysis": "기술 관심은 높지만 지속적인 팬덤 소비로 이어지려면 캐릭터성과 서사가 더 필요합니다."},
    {"id": 110, "name": "스마트 텃밭", "cat": "lifestyle", "prob": 18, "score": 24,
     "analysis": "홈가드닝과 IoT가 맞닿아 있으나 설치 비용과 관리 난도가 있어 단기 대중화 가능성은 낮습니다."},
]

_DECLINE_CAUSES = ["대체재 등장", "계절 종료", "공급 과잉", "부정 이슈", "자연 소멸"]
_DROP_RATES = {1: 18, 2: 32, 3: 15, 4: 41, 5: 23, 6: 12, 7: 27, 8: 35, 9: 20, 10: 29}
_CAT_LABELS = {
    "food": "음식",
    "fashion": "패션",
    "content": "콘텐츠",
    "technology": "기술",
    "lifestyle": "라이프스타일",
    "snack": "음식",
    "drink": "음식",
}


def _normalize_cat(cat: str) -> str:
    return "food" if cat in ("snack", "drink") else cat


def _normalize_keywords():
    return [{**kw, "cat": _normalize_cat(kw["cat"])} for kw in _RAW_KEYWORDS]


def _current_category_averages():
    cat_data: dict[str, list[int]] = defaultdict(list)
    for kw in _CURRENT_TRENDS:
        cat_data[_normalize_cat(kw["cat"])].append(kw["score"])

    return sorted(
        [
            {
                "cat": cat,
                "label": _CAT_LABELS.get(cat, cat),
                "avg": round(sum(scores) / len(scores), 1),
                "count": len(scores),
            }
            for cat, scores in cat_data.items()
        ],
        key=lambda x: x["avg"],
        reverse=True,
    )


def _current_series():
    labels = ["2026.04", "2026.05", "2026.06", "2026.07", "2026.08", "2026.09"]
    series = []
    for index, label in enumerate(labels):
        row = {"label": label}
        for kw in _CURRENT_TRENDS:
            start = max(12, kw["score"] - kw["change_rate"] - 18)
            step = (kw["score"] - start) / (len(labels) - 1)
            row[kw["name"]] = round(start + step * index)
        series.append(row)
    return series


def _db_session():
    if SessionLocal is None:
        return None
    return SessionLocal()


def _with_db(loader, fallback):
    db = _db_session()
    if db is None:
        return fallback()

    try:
        data = loader(db)
        return data or fallback()
    except Exception:
        return fallback()
    finally:
        db.close()


def _keyword_item(keyword: TrendKeyword, peak: float, year: int) -> dict:
    return {
        "id": keyword.id,
        "name": keyword.name,
        "cat": _normalize_cat(keyword.category),
        "peak": int(round(peak or 0)),
        "year": int(year or 0),
    }


def _mock_realtime():
    items = [
        {
            "id": kw["id"],
            "name": kw["name"],
            "cat": _normalize_cat(kw["cat"]),
            "score": kw["score"],
            "change_rate": kw["change_rate"],
            "collected_at": kw["collected_at"],
        }
        for kw in _CURRENT_TRENDS
    ]
    return sorted(items, key=lambda x: x["score"], reverse=True)


def _mock_cycle_keywords():
    items = [
        {
            "id": kw["id"],
            "name": kw["name"],
            "cat": _normalize_cat(kw["cat"]),
            "peak": kw["score"],
            "year": int(kw["collected_at"][:4]),
        }
        for kw in _CURRENT_TRENDS
    ]
    return sorted(items, key=lambda x: x["peak"], reverse=True)


def _mock_cycle():
    return {"keywords": _mock_cycle_keywords(), "series": _current_series()}


def _mock_history(cat: Optional[str], year: Optional[int]):
    keywords = sorted(_normalize_keywords(), key=lambda x: x["peak"], reverse=True)
    if cat:
        keywords = [kw for kw in keywords if kw["cat"] == cat]
    if year:
        keywords = [kw for kw in keywords if kw["year"] == year]

    result = []
    for kw in keywords:
        cause = _DECLINE_CAUSES[kw["id"] % 5]
        drop = _DROP_RATES.get(kw["id"], 20)
        result.append({
            **kw,
            "decline_cause": cause,
            "drop_rate": drop,
            "summary": (
                f"{kw['name']}은(는) {kw['year']}년 {_CAT_LABELS.get(kw['cat'], kw['cat'])} "
                f"카테고리에서 최고 스코어 {kw['peak']}점을 기록했습니다. "
                f"이후 {cause} 원인으로 {drop}% 하락세를 보였습니다."
            ),
        })
    return result


def _mock_predict():
    return sorted(_PREDICTIONS, key=lambda x: x["prob"], reverse=True)


def _mock_decline():
    return _current_category_averages()


def _load_realtime(db: Session):
    latest_subquery = (
        db.query(
            TrendRealtime.keyword_id,
            func.max(TrendRealtime.collected_at).label("latest_collected_at"),
        )
        .group_by(TrendRealtime.keyword_id)
        .subquery()
    )

    rows = (
        db.query(TrendKeyword, TrendRealtime)
        .join(TrendRealtime, TrendRealtime.keyword_id == TrendKeyword.id)
        .join(
            latest_subquery,
            (latest_subquery.c.keyword_id == TrendRealtime.keyword_id)
            & (latest_subquery.c.latest_collected_at == TrendRealtime.collected_at),
        )
        .all()
    )

    items = [
        {
            "id": keyword.id,
            "name": keyword.name,
            "cat": _normalize_cat(keyword.category),
            "score": int(round(realtime.trend_score or 0)),
            "change_rate": round(float(realtime.change_rate or 0), 1),
            "collected_at": realtime.collected_at.isoformat(),
        }
        for keyword, realtime in rows
        if realtime.trend_score is not None and realtime.collected_at is not None
    ]
    return sorted(items, key=lambda x: x["change_rate"], reverse=True)


def _load_cycle(db: Session):
    rows = (
        db.query(TrendKeyword, TrendHistory)
        .join(TrendHistory, TrendHistory.keyword_id == TrendKeyword.id)
        .order_by(TrendHistory.date.asc(), TrendKeyword.name.asc())
        .all()
    )
    if not rows:
        return None

    keyword_peaks = {}
    series_map = defaultdict(dict)
    for keyword, history in rows:
        if history.trend_score is None or history.date is None:
            continue
        current_peak = keyword_peaks.get(keyword.id)
        if current_peak is None or history.trend_score > current_peak["peak"]:
            keyword_peaks[keyword.id] = _keyword_item(keyword, history.trend_score, history.year)

        label = f"{history.year}.{history.month:02d}"
        series_map[label][keyword.name] = int(round(history.trend_score))

    if not keyword_peaks or not series_map:
        return None

    return {
        "keywords": sorted(keyword_peaks.values(), key=lambda x: x["peak"], reverse=True),
        "series": [{"label": label, **scores} for label, scores in sorted(series_map.items())],
    }


def _load_history(db: Session, cat: Optional[str], year: Optional[int]):
    peak_subquery = (
        db.query(
            TrendHistory.keyword_id,
            func.max(TrendHistory.trend_score).label("peak"),
        )
        .group_by(TrendHistory.keyword_id)
        .subquery()
    )

    rows = (
        db.query(TrendKeyword, peak_subquery.c.peak, TrendHistory.year, DeclineEvent)
        .join(peak_subquery, peak_subquery.c.keyword_id == TrendKeyword.id)
        .join(
            TrendHistory,
            (TrendHistory.keyword_id == TrendKeyword.id)
            & (TrendHistory.trend_score == peak_subquery.c.peak),
        )
        .outerjoin(DeclineEvent, DeclineEvent.keyword_id == TrendKeyword.id)
        .all()
    )

    result = []
    seen = set()
    for keyword, peak, peak_year, decline in rows:
        if keyword.id in seen:
            continue
        seen.add(keyword.id)
        normalized_cat = _normalize_cat(keyword.category)
        if cat and normalized_cat != cat:
            continue
        if year and peak_year != year:
            continue

        cause = decline.cause_type if decline and decline.cause_type else "자연 소멸"
        drop_rate = int(round(decline.decline_rate)) if decline and decline.decline_rate is not None else 0
        result.append({
            "id": keyword.id,
            "name": keyword.name,
            "cat": normalized_cat,
            "peak": int(round(peak or 0)),
            "year": int(peak_year or 0),
            "decline_cause": cause,
            "drop_rate": drop_rate,
            "summary": (
                f"{keyword.name}은(는) {peak_year}년 {_CAT_LABELS.get(normalized_cat, normalized_cat)} "
                f"카테고리에서 최고 스코어 {int(round(peak or 0))}점을 기록했습니다. "
                f"이후 {cause} 원인으로 {drop_rate}% 하락세를 보였습니다."
            ),
        })

    return sorted(result, key=lambda x: x["peak"], reverse=True)


def _load_predict(db: Session):
    latest_subquery = (
        db.query(
            TrendPrediction.keyword_id,
            func.max(TrendPrediction.predicted_at).label("latest_predicted_at"),
        )
        .group_by(TrendPrediction.keyword_id)
        .subquery()
    )

    rows = (
        db.query(TrendKeyword, TrendPrediction)
        .join(TrendPrediction, TrendPrediction.keyword_id == TrendKeyword.id)
        .join(
            latest_subquery,
            (latest_subquery.c.keyword_id == TrendPrediction.keyword_id)
            & (latest_subquery.c.latest_predicted_at == TrendPrediction.predicted_at),
        )
        .all()
    )

    result = []
    for keyword, prediction in rows:
        prob = int(round((prediction.prob or 0) * 100 if (prediction.prob or 0) <= 1 else prediction.prob or 0))
        score = int(round(prediction.trend_score or 0))
        result.append({
            "id": keyword.id,
            "name": keyword.name,
            "cat": _normalize_cat(keyword.category),
            "prob": prob,
            "score": score,
            "analysis": f"{keyword.name}의 향후 트렌드 스코어는 {score}점으로 예측되며 유행 가능성은 {prob}%입니다.",
        })

    return sorted(result, key=lambda x: x["prob"], reverse=True)


def _load_decline(db: Session):
    rows = (
        db.query(
            TrendKeyword.category,
            func.avg(TrendHistory.trend_score).label("avg_score"),
            func.count(func.distinct(TrendKeyword.id)).label("keyword_count"),
        )
        .join(TrendHistory, TrendHistory.keyword_id == TrendKeyword.id)
        .group_by(TrendKeyword.category)
        .all()
    )
    if not rows:
        return None

    merged = defaultdict(lambda: {"total": 0.0, "count": 0})
    for category, avg_score, keyword_count in rows:
        cat = _normalize_cat(category)
        merged[cat]["total"] += float(avg_score or 0) * int(keyword_count or 0)
        merged[cat]["count"] += int(keyword_count or 0)

    result = []
    for cat, values in merged.items():
        count = values["count"]
        if not count:
            continue
        result.append({
            "cat": cat,
            "label": _CAT_LABELS.get(cat, cat),
            "avg": round(values["total"] / count, 1),
            "count": count,
        })

    return sorted(result, key=lambda x: x["avg"], reverse=True)


@router.get("/realtime", response_model=list[RealtimeItem])
def get_realtime():
    return _with_db(_load_realtime, _mock_realtime)


@router.get("/cycle", response_model=CycleResponse)
def get_cycle():
    return _with_db(_load_cycle, _mock_cycle)


@router.get("/history", response_model=list[HistoryItem])
def get_history(
    cat: Optional[str] = Query(None, description="카테고리 필터 (food, fashion, content, technology, lifestyle)"),
    year: Optional[int] = Query(None, description="연도 필터 (예: 2022)"),
):
    return _with_db(lambda db: _load_history(db, cat, year), lambda: _mock_history(cat, year))


@router.get("/predict", response_model=list[PredictItem])
def get_predict():
    return _with_db(_load_predict, _mock_predict)


@router.get("/decline", response_model=list[DeclineItem])
def get_decline():
    return _with_db(_load_decline, _mock_decline)
