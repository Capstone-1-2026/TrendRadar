# /Users/apple/TrendRadar/data/collectors/youtube.py

import os
import time
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from supabase import create_client
from datetime import datetime, timezone

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

KEYWORDS = [
    "허니버터칩",
    "흑당버블티",
    "달고나커피",
    "마라탕",
    "탕후루",
    "두바이초콜릿",
    "Y2K패션",
    "레트로무드",
    "숏폼콘텐츠",
    "AI아트",
]


# ─────────────────────────────────────────
# YouTube 클라이언트
# ─────────────────────────────────────────
def get_youtube_client():
    if not YOUTUBE_API_KEY:
        raise ValueError("❌ YOUTUBE_API_KEY가 .env에 없습니다.")
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


# ─────────────────────────────────────────
# Step 1: video_id 수집 (100 유닛/키워드)
# ─────────────────────────────────────────
def search_videos(youtube, keyword: str, max_results: int = 20) -> list[str]:
    try:
        response = (
            youtube.search()
            .list(
                q=keyword,
                part="snippet",
                type="video",
                regionCode="KR",
                relevanceLanguage="ko",
                maxResults=max_results,
                order="viewCount",
            )
            .execute()
        )

        return [
            item["id"]["videoId"]
            for item in response.get("items", [])
            if item["id"].get("videoId")
        ]
    except HttpError as e:
        print(f"⚠️ search 오류 [{keyword}]: {e}")
        return []


# ─────────────────────────────────────────
# Step 2: 실제 통계 수집 (1 유닛/호출)
# ─────────────────────────────────────────
def get_video_stats(youtube, video_ids: list[str]) -> dict:
    if not video_ids:
        return {}
    try:
        response = (
            youtube.videos()
            .list(part="statistics,snippet", id=",".join(video_ids))
            .execute()
        )

        stats = {}
        for item in response.get("items", []):
            vid = item["id"]
            s = item.get("statistics", {})
            snippet = item.get("snippet", {})
            stats[vid] = {
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "view_count": int(s.get("viewCount", 0)),
                "like_count": int(s.get("likeCount", 0)),
                "comment_count": int(s.get("commentCount", 0)),
            }
        return stats
    except HttpError as e:
        print(f"⚠️ video stats 오류: {e}")
        return {}


# ─────────────────────────────────────────
# Step 3: 키워드별 수집 통합
# ─────────────────────────────────────────
def collect_keyword(youtube, keyword: str) -> pd.DataFrame:
    video_ids = search_videos(youtube, keyword)
    if not video_ids:
        return pd.DataFrame()

    stats = get_video_stats(youtube, video_ids)
    rows = []
    for vid in video_ids:
        if vid not in stats:
            continue
        row = {"keyword": keyword, "video_id": vid}
        row.update(stats[vid])
        row["collected_at"] = datetime.now(timezone.utc).isoformat()
        rows.append(row)

    return pd.DataFrame(rows)


# ─────────────────────────────────────────
# Step 4: 전체 수집
# ─────────────────────────────────────────
def collect_youtube_trends(delay: float = 1.0) -> pd.DataFrame:
    youtube = get_youtube_client()
    all_dfs = []

    for keyword in KEYWORDS:
        print(f"📡 YouTube 수집 중: {keyword}")
        df = collect_keyword(youtube, keyword)

        if not df.empty:
            all_dfs.append(df)
            print(f"  └─ {len(df)}개 영상 수집")
        else:
            print(f"  └─ ⚠️ 수집 결과 없음")

        time.sleep(delay)

    if not all_dfs:
        print("❌ 수집된 데이터 없음")
        return pd.DataFrame()

    final_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n✅ YouTube 수집 완료: {len(final_df)}개 행")
    return final_df


# ─────────────────────────────────────────
# Supabase 적재
# ─────────────────────────────────────────
def get_keyword_id_map(supabase) -> dict:
    """trend_keywords 테이블에서 name → id 매핑"""
    response = supabase.table("trend_keywords").select("id, name").execute()
    return {row["name"]: row["id"] for row in response.data}


def calc_youtube_score(df_keyword: pd.DataFrame) -> float:
    """총 조회수 기반 로그 스케일 점수 (0~100)"""
    total_views = df_keyword["view_count"].sum()
    if total_views <= 0:
        return 0.0
    return min(100.0, round(float(np.log10(total_views + 1)) * 10, 2))


def upload_to_supabase(df: pd.DataFrame) -> None:
    """수집된 YouTube 데이터를 trend_realtime 테이블에 적재"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("❌ SUPABASE_URL 또는 SUPABASE_KEY가 .env에 없습니다.")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    keyword_map = get_keyword_id_map(supabase)

    records = []
    now = datetime.now(timezone.utc).isoformat()

    for keyword, group in df.groupby("keyword"):
        keyword_id = keyword_map.get(keyword)

        if not keyword_id:
            print(f"⚠️ trend_keywords에 없는 키워드: {keyword} → 건너뜀")
            continue

        youtube_score = calc_youtube_score(group)
        records.append(
            {
                "keyword_id": keyword_id,
                "collected_at": now,
                "youtube_score": youtube_score,
                "trend_score": youtube_score,  # 추후 naver_score 합산 시 수정
                "cycle_stage": "unknown",  # 추후 Trend Cycle 로직 연동
            }
        )

    if not records:
        print("❌ 적재할 레코드 없음 (keyword_id 매핑 실패)")
        return

    supabase.table("trend_realtime").insert(records).execute()
    print(f"✅ Supabase 적재 완료: {len(records)}개 키워드")


# ─────────────────────────────────────────
# 실행
# ─────────────────────────────────────────
if __name__ == "__main__":
    df = collect_youtube_trends()

    if not df.empty:
        print(df[["keyword", "title", "view_count", "like_count"]].head(20))
        df.to_csv("youtube_trends_raw.csv", index=False, encoding="utf-8-sig")
        print("💾 youtube_trends_raw.csv 저장 완료")

        upload_to_supabase(df)
