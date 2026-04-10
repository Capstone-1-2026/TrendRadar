import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 수집할 키워드 목록
KEYWORDS = [
    "허니버터칩", "흑당버블티", "달고나커피",
    "마라탕", "탕후루", "두바이초콜릿",
    "Y2K패션", "레트로무드", "숏폼콘텐츠", "AI아트"
]

def get_naver_trend(keywords: list, start_date: str, end_date: str) -> dict:
    """
    네이버 데이터랩 검색어 트렌드 API 호출
    keywords: 키워드 리스트 (최대 5개)
    start_date: 시작일 (YYYY-MM-DD)
    end_date: 종료일 (YYYY-MM-DD)
    """
    url = "https://openapi.naver.com/v1/datalab/search"

    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        "Content-Type":          "application/json"
    }

    keyword_groups = [
        {"groupName": kw, "keywords": [kw]}
        for kw in keywords
    ]

    body = {
        "startDate":     start_date,
        "endDate":       end_date,
        "timeUnit":      "month",
        "keywordGroups": keyword_groups
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        print(f"❌ 네이버 API 오류: {response.status_code} {response.text}")
        return {}

    return response.json()


def parse_naver_result(result: dict) -> pd.DataFrame:
    """
    API 응답을 DataFrame으로 변환
    """
    rows = []

    for item in result.get("results", []):
        keyword = item["title"]
        for data in item["data"]:
            rows.append({
                "keyword":     keyword,
                "date":        data["period"],
                "naver_score": data["ratio"]
            })

    return pd.DataFrame(rows)


def collect_naver_trends(start_date: str = "2016-01-01", end_date: str = None) -> pd.DataFrame:
    """
    전체 키워드 네이버 트렌드 수집
    5개씩 배치 처리 (API 한도 고려)
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    all_dfs = []

    # 5개씩 배치 처리
    for i in range(0, len(KEYWORDS), 5):
        batch = KEYWORDS[i:i+5]
        print(f"📡 네이버 수집 중: {batch}")

        result = get_naver_trend(batch, start_date, end_date)

        if result:
            df = parse_naver_result(result)
            all_dfs.append(df)

    if not all_dfs:
        print("❌ 수집된 데이터 없음")
        return pd.DataFrame()

    final_df = pd.concat(all_dfs, ignore_index=True)
    print(f"✅ 네이버 수집 완료: {len(final_df)}개 행")

    return final_df


if __name__ == "__main__":
    df = collect_naver_trends(
        start_date="2016-01-01",
        end_date="2025-12-31"
    )
    print(df.head(20))
    df.to_csv("naver_trends_raw.csv", index=False, encoding="utf-8-sig")
    print("💾 naver_trends_raw.csv 저장 완료")