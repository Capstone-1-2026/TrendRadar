import os
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

KEYWORDS = [
    "허니버터칩", "흑당버블티", "달고나커피",
    "마라탕", "탕후루", "두바이초콜릿",
    "Y2K패션", "레트로무드", "숏폼콘텐츠", "AI아트"
]

def get_youtube_trend(keyword: str) -> dict:
    """
    YouTube Data API로 키워드 검색 결과 수집
    regionCode=KR, relevanceLanguage=ko
    """
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        q=keyword,
        part="snippet",
        type="video",
        regionCode="KR",
        relevanceLanguage="ko",
        maxResults=50,
        order="viewCount"
    )

    response = request.execute()
    return response


def parse_youtube_result(keyword: str, result: dict) -> pd.DataFrame:
    """
    YouTube API 응답을 DataFrame으로 변환
    """
    rows = []

    for item in result.get("items", []):
        snippet = item.get("snippet", {})
        rows.append({
            "keyword":      keyword,
            "video_id":     item["id"].get("videoId", ""),
            "title":        snippet.get("title", ""),
            "published_at": snippet.get("publishedAt", ""),
            "channel":      snippet.get("channelTitle", ""),
            "description":  snippet.get("description", "")[:200]
        })

    return pd.DataFrame(rows)


def collect_youtube_trends() -> pd.DataFrame:
    """
    전체 키워드 YouTube 트렌드 수집
    """
    all_dfs = []

    for keyword in KEYWORDS:
        print(f"📡 YouTube 수집 중: {keyword}")

        result = get_youtube_trend(keyword)

        if result:
            df = parse_youtube_result(keyword, result)
            all_dfs.append(df)

    if not all_dfs:
        print("❌ 수집된 데이터 없음")
        return pd.DataFrame()

    final_df = pd.concat(all_dfs, ignore_index=True)
    print(f"✅ YouTube 수집 완료: {len(final_df)}개 행")

    return final_df


if __name__ == "__main__":
    df = collect_youtube_trends()
    print(df.head(20))
    df.to_csv("youtube_trends_raw.csv", index=False, encoding="utf-8-sig")
    print("💾 youtube_trends_raw.csv 저장 완료")