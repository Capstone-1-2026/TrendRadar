from fastapi import APIRouter, Query
from typing import Optional
from models.schema import KeywordItem, CycleResponse, HistoryItem, PredictItem, DeclineItem

router = APIRouter()

# ── 원본 데이터 ────────────────────────────────────────────────────────────────

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

_PREDICTIONS = [
    {"id": 1,  "name": "두바이초콜릿",     "cat": "food",      "prob": 82, "score": 85,
     "analysis": "SNS 확산 속도와 검색량 증가율을 기반으로 높은 유행 가능성을 보입니다. 특히 20대 여성층에서 급격한 관심 증가가 감지되었으며, 글로벌 트렌드 연계성도 높게 나타났습니다."},
    {"id": 2,  "name": "글로우스킨케어",   "cat": "fashion",   "prob": 75, "score": 79,
     "analysis": "피부 광채 관련 뷰티 키워드 수요가 꾸준히 증가하고 있습니다. 뷰티 앱 다운로드 수와 관련 콘텐츠 소비량이 전년 대비 40% 이상 상승했습니다."},
    {"id": 3,  "name": "하이볼칵테일",     "cat": "food",      "prob": 68, "score": 72,
     "analysis": "홈술 문화의 확장과 함께 프리미엄 혼술 키워드가 부상하고 있습니다. 편의점 하이볼 상품 판매량이 전년 동기 대비 62% 증가했습니다."},
    {"id": 4,  "name": "미니멀패션",       "cat": "fashion",   "prob": 61, "score": 65,
     "analysis": "과잉 소비 반작용으로 간결하고 기능적인 스타일 수요가 증가하는 추세입니다."},
    {"id": 5,  "name": "버추얼인플루언서", "cat": "content",   "prob": 54, "score": 58,
     "analysis": "AI 생성 가상 인물에 대한 관심이 높아지고 있으나 아직 주류 단계는 아닙니다."},
    {"id": 6,  "name": "제로웨이스트쿡",   "cat": "lifestyle", "prob": 47, "score": 51,
     "analysis": "친환경 인식 확산에 따른 요리 트렌드로 관심은 있으나 실천율은 아직 낮은 편입니다."},
    {"id": 7,  "name": "레트로게임카페",   "cat": "content",   "prob": 39, "score": 44,
     "analysis": "Y2K 감성의 연장선으로 향수를 자극하는 오프라인 공간에 대한 수요가 있습니다."},
    {"id": 8,  "name": "비건베이킹",       "cat": "food",      "prob": 31, "score": 36,
     "analysis": "건강·윤리 소비 트렌드와 맞닿아 있으나 국내 소비자 수용도가 아직 낮습니다."},
    {"id": 9,  "name": "스페이스코어패션", "cat": "fashion",   "prob": 22, "score": 27,
     "analysis": "해외 패션 위크에서 등장하고 있으나 국내 트렌드 반영까지는 시간이 필요합니다."},
    {"id": 10, "name": "달팽이슬라임",     "cat": "lifestyle", "prob": 14, "score": 18,
     "analysis": "해외 숏폼에서 간헐적으로 바이럴되고 있으나 국내 확산 사례는 미미합니다."},
]

_DECLINE_CAUSES = ["대체재 등장", "계절 종료", "공급 과잉", "부정 이슈", "자연 소멸"]

_CAT_LABELS = {
    "food": "음식", "fashion": "패션", "content": "콘텐츠",
    "technology": "기술", "lifestyle": "라이프스타일",
    "snack": "음식", "drink": "음식",
}

_DROP_RATES = {1: 18, 2: 32, 3: 15, 4: 41, 5: 23, 6: 12, 7: 27, 8: 35, 9: 20, 10: 29}


def _normalize_cat(cat: str) -> str:
    """snack, drink → food 통합"""
    return "food" if cat in ("snack", "drink") else cat


def _normalize_keywords():
    """전체 키워드 cat 정규화 적용"""
    return [
        {**kw, "cat": _normalize_cat(kw["cat"])}
        for kw in _RAW_KEYWORDS
    ]


# ── 1. GET /api/trends/realtime ───────────────────────────────────────────────
@router.get("/realtime", response_model=list[KeywordItem])
def get_realtime():
    """peak 점수 기준 내림차순 키워드 목록 반환"""
    keywords = _normalize_keywords()
    return sorted(keywords, key=lambda x: x["peak"], reverse=True)


# ── 2. GET /api/trends/cycle ──────────────────────────────────────────────────
@router.get("/cycle", response_model=CycleResponse)
def get_cycle():
    """타임라인 차트 + 워드클라우드용 월별 시계열 데이터 반환 (2021.01 ~ 2026.03)"""
    keywords = _normalize_keywords()

    # 2021.01 ~ 2026.03 월별 레이블 생성
    months = []
    for year in range(2021, 2027):
        end_month = 4 if year == 2026 else 13
        for month in range(1, end_month):
            months.append((year, month))

    series = []
    for year, month in months:
        label = f"{year}.{month:02d}"
        row: dict = {"label": label}
        for kw in keywords:
            # 피크 연도 기준 앞뒤 점수를 간단히 시뮬레이션
            diff = (year - kw["year"]) * 12 + (month - 6)
            if diff < -18:
                score = 0
            elif diff < 0:
                score = round(kw["peak"] * (1 + diff / 18) * 0.8)
            elif diff == 0:
                score = kw["peak"]
            elif diff <= 18:
                score = round(kw["peak"] * (1 - diff / 18) * 0.9)
            else:
                score = 0
            row[kw["name"]] = max(0, score)
        series.append(row)

    return {"keywords": keywords, "series": series}


# ── 3. GET /api/trends/history ────────────────────────────────────────────────
@router.get("/history", response_model=list[HistoryItem])
def get_history(
    cat: Optional[str] = Query(None, description="카테고리 필터 (food, fashion, content, technology, lifestyle)"),
    year: Optional[int] = Query(None, description="연도 필터 (예: 2022)"),
):
    """히스토리 페이지용. 카테고리/연도 필터, 하락 원인·drop_rate·AI 요약 포함"""
    keywords = _normalize_keywords()

    # 필터 적용
    if cat:
        keywords = [kw for kw in keywords if kw["cat"] == cat]
    if year:
        keywords = [kw for kw in keywords if kw["year"] == year]

    result = []
    for kw in keywords:
        cause = _DECLINE_CAUSES[kw["id"] % 5]
        drop = _DROP_RATES.get(kw["id"], 20)
        summary = (
            f"{kw['name']}은(는) {kw['year']}년 {_CAT_LABELS.get(kw['cat'], kw['cat'])} "
            f"카테고리에서 최고 스코어 {kw['peak']}점을 기록했습니다. "
            f"이후 {cause} 원인으로 {drop}% 하락세를 보였습니다."
        )
        result.append({
            **kw,
            "decline_cause": cause,
            "drop_rate": drop,
            "summary": summary,
        })

    return result


# ── 4. GET /api/trends/predict ────────────────────────────────────────────────
@router.get("/predict", response_model=list[PredictItem])
def get_predict():
    """AI 예측 페이지용. 예측 확률(prob) 내림차순 반환"""
    return sorted(_PREDICTIONS, key=lambda x: x["prob"], reverse=True)


# ── 5. GET /api/trends/decline ────────────────────────────────────────────────
@router.get("/decline", response_model=list[DeclineItem])
def get_decline():
    """히스토리 페이지 카테고리 요약 카드용. 카테고리별 평균 스코어·키워드 수 반환"""
    keywords = _normalize_keywords()

    # 카테고리별 집계
    cat_data: dict[str, list[int]] = {}
    for kw in keywords:
        cat_data.setdefault(kw["cat"], []).append(kw["peak"])

    result = []
    for cat, scores in cat_data.items():
        result.append({
            "cat": cat,
            "label": _CAT_LABELS.get(cat, cat),
            "avg": round(sum(scores) / len(scores), 1),
            "count": len(scores),
        })

    return sorted(result, key=lambda x: x["avg"], reverse=True)