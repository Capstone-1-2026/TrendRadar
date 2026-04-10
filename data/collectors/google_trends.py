import time
import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime

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


def chunks(lst: list, n: int):
    """리스트를 n개씩 나누기"""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_google_trends(
    keywords: list, start_date: str = "2016-01-01", end_date: str = None
) -> pd.DataFrame:
    """
    Google Trends 수집
    keywords: 키워드 리스트 (최대 5개)
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    pytrends = TrendReq(hl="ko", tz=540)

    pytrends.build_payload(keywords, timeframe=f"{start_date} {end_date}", geo="KR")

    df = pytrends.interest_over_time()

    if df.empty:
        return pd.DataFrame()

    # isPartial 컬럼 제거
    if "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])

    # wide → long 변환
    df = df.reset_index()
    df = df.melt(id_vars=["date"], var_name="keyword", value_name="google_score")

    return df


def collect_google_trends(
    start_date: str = "2016-01-01", end_date: str = None
) -> pd.DataFrame:
    """
    전체 키워드 Google Trends 수집
    5개씩 배치 처리
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    all_dfs = []

    for batch in chunks(KEYWORDS, 5):
        print(f"📡 Google Trends 수집 중: {batch}")

        df = get_google_trends(batch, start_date, end_date)

        if not df.empty:
            all_dfs.append(df)

        # 요청 간격 조절 (429 오류 방지)
        time.sleep(10)

    if not all_dfs:
        print("❌ 수집된 데이터 없음")
        return pd.DataFrame()

    final_df = pd.concat(all_dfs, ignore_index=True)
    # 날짜 월별 정규화
    final_df["date"] = (
        pd.to_datetime(final_df["date"]).dt.to_period("M").dt.to_timestamp()
    )
    final_df = (
        final_df.groupby(["date", "keyword"])["google_score"].mean().reset_index()
    )

    print(f"✅ Google Trends 수집 완료: {len(final_df)}개 행")

    return final_df


if __name__ == "__main__":
    df = collect_google_trends(start_date="2016-01-01", end_date="2025-12-31")
    print(df.head(20))
    df.to_csv("google_trends_raw.csv", index=False, encoding="utf-8-sig")
    print("💾 google_trends_raw.csv 저장 완료")
