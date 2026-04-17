import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

from collectors.naver import collect_naver_trends
from collectors.youtube import collect_youtube_trends
from collectors.google_trends import collect_google_trends

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 카테고리 매핑
KEYWORD_META = {
    "허니버터칩": {"category": "food", "year": 2015},
    "흑당버블티": {"category": "food", "year": 2018},
    "달고나커피": {"category": "food", "year": 2020},
    "마라탕": {"category": "food", "year": 2019},
    "탕후루": {"category": "food", "year": 2022},
    "두바이초콜릿": {"category": "food", "year": 2024},
    "Y2K패션": {"category": "fashion", "year": 2022},
    "레트로무드": {"category": "fashion", "year": 2023},
    "숏폼콘텐츠": {"category": "content", "year": 2022},
    "AI아트": {"category": "technology", "year": 2024},
}


def get_season(month: int) -> str:
    """월 → 계절 변환"""
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"


def calculate_trend_score(
    naver: float, youtube: float, season_factor: float = 1.0
) -> float:
    """
    Trend Score 계산
    네이버 50% + YouTube 30% + 계절 보정 20%
    """
    naver_w = (naver or 0) * 0.5
    youtube_w = (youtube or 0) * 0.3
    season_w = season_factor * 0.2 * 100
    return round(naver_w + youtube_w + season_w, 2)


def upsert_keywords():
    """trend_keywords 테이블에 키워드 기본 정보 적재"""
    for name, meta in KEYWORD_META.items():
        data = {
            "name": name,
            "category": meta["category"],
        }
        supabase.table("trend_keywords").upsert(data, on_conflict="name").execute()
    print("✅ trend_keywords 적재 완료")


def get_keyword_id_map() -> dict:
    """키워드명 → id 매핑 딕셔너리 반환"""
    result = supabase.table("trend_keywords").select("id, name").execute()
    return {row["name"]: row["id"] for row in result.data}


def run_pipeline():
    """전체 데이터 수집 → 정제 → DB 적재 파이프라인"""
    print("🚀 파이프라인 시작:", datetime.now())

    # 1. 키워드 기본 정보 적재
    upsert_keywords()
    keyword_id_map = get_keyword_id_map()

    # 2. 데이터 수집
    print("\n📡 데이터 수집 시작...")
    naver_df = collect_naver_trends()
    google_df = collect_google_trends()

    if naver_df.empty:
        print("❌ 네이버 데이터 없음 - 파이프라인 중단")
        return

    # 3. 날짜 정규화
    naver_df["date"] = (
        pd.to_datetime(naver_df["date"]).dt.to_period("M").dt.to_timestamp()
    )
    google_df["date"] = pd.to_datetime(google_df["date"])

    # 4. 병합
    merged_df = pd.merge(naver_df, google_df, on=["keyword", "date"], how="left")

    # 5. 컬럼 추가
    merged_df["year"] = pd.to_datetime(merged_df["date"]).dt.year
    merged_df["month"] = pd.to_datetime(merged_df["date"]).dt.month
    merged_df["season"] = merged_df["month"].apply(get_season)
    merged_df["youtube_score"] = 0.0  # YouTube는 별도 처리
    merged_df["trend_score"] = merged_df.apply(
        lambda row: calculate_trend_score(
            row.get("naver_score", 0), row.get("youtube_score", 0)
        ),
        axis=1,
    )

    # 6. Trend Cycle 단계 분류
    def classify_cycle(score, prev_score):
        if prev_score is None:
            return "emergence"
        change = score - prev_score
        if score >= 60 and change <= 2:
            return "peak"
        elif score >= 60:
            return "growth"
        elif change <= -15:
            return "decline"
        elif score < 20 and change >= 10:
            return "emergence"
        else:
            return "growth"

    merged_df = merged_df.sort_values(["keyword", "date"])
    merged_df["cycle_stage"] = "growth"

    # 7. DB 적재
    print("\n💾 DB 적재 시작...")
    success_count = 0

    for _, row in merged_df.iterrows():
        keyword_id = keyword_id_map.get(row["keyword"])
        if not keyword_id:
            continue

        data = {
            "keyword_id": keyword_id,
            "date": str(row["date"])[:10],
            "year": int(row["year"]),
            "month": int(row["month"]),
            "season": row["season"],
            "naver_score": float(row.get("naver_score", 0) or 0),
            "youtube_score": float(row.get("youtube_score", 0) or 0),
            "google_score": float(row.get("google_score", 0) or 0),
            "trend_score": float(row.get("trend_score", 0) or 0),
            "cycle_stage": row.get("cycle_stage", "growth"),
            "lifecycle_month": 1,
        }

        supabase.table("trend_history").upsert(
            data, on_conflict="keyword_id,date"
        ).execute()
        success_count += 1

    print(f"✅ DB 적재 완료: {success_count}개 행")
    print("🎉 파이프라인 완료:", datetime.now())


if __name__ == "__main__":
    run_pipeline()
