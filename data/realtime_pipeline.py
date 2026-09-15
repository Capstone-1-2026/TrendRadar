# /Users/apple/TrendRadar/data/realtime_pipeline.py
#
# "지금 뜨는" 현재 트렌드 키워드를 주기적으로 수집해 trend_realtime에 적재하는 파이프라인.
# trend_history(과거 유행 히스토리)와는 별도 테이블/별도 키워드 세트를 사용한다 — 과거 키워드가
# 홈(realtime)에 다시 노출되는 일이 없도록 완전히 분리되어 있다.

import time
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
import os

from supabase import create_client

from collectors.naver import get_naver_trend, parse_naver_result
from collectors.youtube import get_youtube_client, collect_keyword, calc_youtube_score
from pipeline import calculate_trend_score

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# "현재 뜨는" 키워드 세트 — trend_history/trend_keywords(과거 KEYWORD_META)와는 분리된
# 별도 목록. 이 목록을 바꾸면 홈 화면에 노출되는 현재 트렌드 키워드가 바뀐다.
CURRENT_KEYWORD_META = {
    "러닝크루": "lifestyle",
    "단백질 디저트": "food",
    "AI 쇼핑비서": "technology",
    "초단편 드라마": "content",
    "업사이클링 패션": "fashion",
    "무알코올 페어링": "food",
    "슬립테크 루틴": "technology",
    "로컬 팝업투어": "lifestyle",
}


def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL 또는 SUPABASE_KEY가 .env에 없습니다.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def upsert_current_keywords(supabase) -> None:
    """trend_keywords에 현재 트렌드 키워드를 등록 (과거 키워드와 같은 테이블, 이름으로 upsert)"""
    for name, category in CURRENT_KEYWORD_META.items():
        supabase.table("trend_keywords").upsert(
            {"name": name, "category": category}, on_conflict="name"
        ).execute()


def get_keyword_id_map(supabase, names: list[str]) -> dict:
    result = (
        supabase.table("trend_keywords")
        .select("id, name")
        .in_("name", names)
        .execute()
    )
    return {row["name"]: row["id"] for row in result.data}


def get_previous_scores(supabase, keyword_ids: list[int]) -> dict:
    """change_rate 계산용 — 키워드별 가장 최근 trend_score"""
    if not keyword_ids:
        return {}

    result = (
        supabase.table("trend_realtime")
        .select("keyword_id, trend_score, collected_at")
        .in_("keyword_id", keyword_ids)
        .order("collected_at", desc=True)
        .execute()
    )

    previous: dict[int, float] = {}
    for row in result.data:
        kid = row["keyword_id"]
        if kid not in previous and row.get("trend_score") is not None:
            previous[kid] = float(row["trend_score"])
    return previous


def collect_naver_realtime_score(keyword: str) -> float:
    """
    최근 7일 일별 검색 비율(timeUnit=date)의 최신값을 현재 naver_score로 사용.
    월 단위 히스토리 파이프라인과 달리 짧은 구간을 봐야 "지금" 뜨는지 감지할 수 있다.
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    result = get_naver_trend([keyword], start_date, end_date, time_unit="date")
    if not result:
        return 0.0

    df = parse_naver_result(result)
    if df.empty:
        return 0.0

    df = df.sort_values("date")
    return float(df.iloc[-1]["naver_score"])


def collect_youtube_realtime_score(youtube, keyword: str) -> float:
    df = collect_keyword(youtube, keyword)
    if df.empty:
        return 0.0
    return calc_youtube_score(df)


def run_realtime_pipeline() -> None:
    """현재 트렌드 키워드 세트를 수집해 trend_realtime에 스냅샷 한 행씩 적재"""
    supabase = get_supabase_client()

    print("🚀 실시간 파이프라인 시작:", datetime.now())

    upsert_current_keywords(supabase)
    keyword_id_map = get_keyword_id_map(supabase, list(CURRENT_KEYWORD_META.keys()))
    previous_scores = get_previous_scores(supabase, list(keyword_id_map.values()))

    youtube = get_youtube_client()

    records = []
    now = datetime.now(timezone.utc).isoformat()

    for name in CURRENT_KEYWORD_META:
        keyword_id = keyword_id_map.get(name)
        if not keyword_id:
            print(f"⚠️ trend_keywords 매핑 실패, 건너뜀: {name}")
            continue

        print(f"📡 실시간 수집 중: {name}")
        naver_score = collect_naver_realtime_score(name)
        youtube_score = collect_youtube_realtime_score(youtube, name)
        trend_score = calculate_trend_score(naver_score, youtube_score)

        prev = previous_scores.get(keyword_id)
        change_rate = round(((trend_score - prev) / prev) * 100, 1) if prev else 0.0

        records.append({
            "keyword_id": keyword_id,
            "collected_at": now,
            "naver_score": naver_score,
            "youtube_score": youtube_score,
            "trend_score": trend_score,
            "change_rate": change_rate,
            "cycle_stage": "growth" if change_rate >= 0 else "decline",
        })

        time.sleep(0.5)  # API 과부하 방지

    if not records:
        print("❌ 적재할 레코드 없음")
        return

    supabase.table("trend_realtime").insert(records).execute()
    print(f"✅ trend_realtime 적재 완료: {len(records)}개 키워드")
    print("🎉 실시간 파이프라인 완료:", datetime.now())


if __name__ == "__main__":
    run_realtime_pipeline()
