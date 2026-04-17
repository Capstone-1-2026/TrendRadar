# /Users/apple/TrendRadar/data/collectors/predictor.py

import os
import warnings
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from supabase import create_client
from prophet import Prophet
from datetime import datetime, timezone

warnings.filterwarnings("ignore")  # Prophet 경고 억제
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MODEL_VERSION = "prophet-v1.0"
FORECAST_MONTHS = 3  # 예측 기간 (단기 = 높은 정확도)


# ─────────────────────────────────────────
# 1. 데이터 로드
# ─────────────────────────────────────────
def fetch_history(supabase) -> pd.DataFrame:
    """trend_history 전체 조회 (페이지네이션)"""
    all_rows = []
    page_size = 1000
    offset = 0

    while True:
        res = (
            supabase.table("trend_history")
            .select("keyword_id, date, trend_score")
            .order("date", desc=False)
            .range(offset, offset + page_size - 1)
            .execute()
        )

        rows = res.data
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < page_size:
            break
        offset += page_size

    df = pd.DataFrame(all_rows)
    df["date"] = pd.to_datetime(df["date"])
    df["trend_score"] = pd.to_numeric(df["trend_score"], errors="coerce").fillna(0)
    return df


def fetch_keyword_map(supabase) -> dict:
    res = supabase.table("trend_keywords").select("id, name").execute()
    return {row["id"]: row["name"] for row in res.data}


# ─────────────────────────────────────────
# 2. Prophet 예측
# ─────────────────────────────────────────
def run_prophet(
    df_keyword: pd.DataFrame, periods: int = FORECAST_MONTHS
) -> pd.DataFrame:
    """
    단일 키워드 Prophet 예측
    반환: 예측 DataFrame (ds, yhat, yhat_lower, yhat_upper)
    """
    # Prophet 입력 형식: ds(날짜), y(값)
    prophet_df = df_keyword.rename(columns={"date": "ds", "trend_score": "y"})

    model = Prophet(
        yearly_seasonality=True,  # 연간 계절성 반영
        weekly_seasonality=False,  # 월별 데이터라 불필요
        daily_seasonality=False,
        seasonality_mode="multiplicative",  # 트렌드 크기에 비례한 계절성
        interval_width=0.8,  # 80% 신뢰구간
        changepoint_prior_scale=0.1,  # 변화점 민감도 (과적합 방지)
    )

    model.fit(prophet_df)

    # 미래 3개월 예측
    future = model.make_future_dataframe(periods=periods, freq="MS")  # MS: 월 시작
    forecast = model.predict(future)

    # 미래 구간만 반환
    forecast_only = forecast[forecast["ds"] > prophet_df["ds"].max()].copy()
    forecast_only["yhat"] = forecast_only["yhat"].clip(0, 100)  # 0~100 범위 제한
    forecast_only["yhat_lower"] = forecast_only["yhat_lower"].clip(0, 100)
    forecast_only["yhat_upper"] = forecast_only["yhat_upper"].clip(0, 100)

    return forecast_only[["ds", "yhat", "yhat_lower", "yhat_upper"]]


# ─────────────────────────────────────────
# 3. 예측 메타데이터 계산
# ─────────────────────────────────────────
def calc_prediction_meta(df_keyword: pd.DataFrame, forecast: pd.DataFrame) -> dict:
    """
    peak_expected, revival_prob, lifecycle_expected 계산
    """
    current_score = df_keyword["trend_score"].iloc[-1]
    max_score = df_keyword["trend_score"].max()
    recent_3 = df_keyword["trend_score"].tail(3).mean()
    recent_trend = df_keyword["trend_score"].pct_change().tail(3).mean() * 100

    # peak 예상 시점: 예측 구간에서 최고점
    peak_idx = forecast["yhat"].idxmax()
    peak_expected = forecast.loc[peak_idx, "ds"].date()

    # 상승 확률 (prob): 예측값이 현재보다 높을 확률
    prob = float((forecast["yhat"] > current_score).mean())

    # 부활 확률: 현재 낮은 점수 + 상승 추세
    if current_score < 35 and recent_trend > 0:
        revival_prob = min(0.9, float(recent_trend / 100 + 0.3))
    elif current_score < 35:
        revival_prob = 0.1
    else:
        revival_prob = 0.0

    # 라이프사이클 예상 개월 수: peak 도달까지 남은 개월
    months_to_peak = int(
        (forecast.loc[peak_idx, "ds"] - df_keyword["date"].iloc[-1]).days / 30
    )
    lifecycle_expected = max(1, months_to_peak)

    return {
        "prob": round(prob, 4),
        "peak_expected": str(peak_expected),
        "revival_prob": round(revival_prob, 4),
        "lifecycle_expected": lifecycle_expected,
    }


# ─────────────────────────────────────────
# 4. Supabase 저장
# ─────────────────────────────────────────
def save_predictions(
    supabase, keyword_id: int, forecast: pd.DataFrame, meta: dict
) -> None:
    """예측 결과를 trend_predictions 테이블에 upsert"""
    records = []

    for _, row in forecast.iterrows():
        records.append(
            {
                "keyword_id": keyword_id,
                "predicted_at": str(row["ds"].date()),
                "trend_score": round(float(row["yhat"]), 2),
                "prob": meta["prob"],
                "peak_expected": meta["peak_expected"],
                "lifecycle_expected": meta["lifecycle_expected"],
                "revival_prob": meta["revival_prob"],
                "model_version": MODEL_VERSION,
            }
        )

    supabase.table("trend_predictions").upsert(
        records, on_conflict="keyword_id,predicted_at"
    ).execute()


# ─────────────────────────────────────────
# 5. 결과 요약 출력
# ─────────────────────────────────────────
def print_summary(results: list, keyword_map: dict) -> None:
    print("\n🔮 Prophet 예측 결과 요약 (향후 3개월):")
    print("-" * 75)
    print(
        f"{'키워드':<15} {'현재점수':>8} {'1개월후':>8} {'2개월후':>8} {'3개월후':>8} {'상승확률':>8} {'부활확률':>8}"
    )
    print("-" * 75)

    for r in results:
        name = keyword_map.get(r["keyword_id"], r["keyword_id"])
        scores = r["forecast_scores"]
        print(
            f"{str(name):<15} "
            f"{r['current_score']:>8.1f} "
            f"{scores[0]:>8.1f} "
            f"{scores[1]:>8.1f} "
            f"{scores[2]:>8.1f} "
            f"{r['prob']:>8.1%} "
            f"{r['revival_prob']:>8.1%}"
        )
    print("-" * 75)


# ─────────────────────────────────────────
# 6. 메인 실행
# ─────────────────────────────────────────
def run_prediction():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    keyword_map = fetch_keyword_map(supabase)

    print("🔍 trend_history 로드 중...")
    df = fetch_history(supabase)
    print(f"  └─ {len(df)}개 행 로드")

    results = []

    for keyword_id, group in df.groupby("keyword_id"):
        name = keyword_map.get(keyword_id, keyword_id)
        group = group.sort_values("date").copy()

        # 최소 12개월 데이터 필요
        if len(group) < 12:
            print(f"⚠️ {name}: 데이터 부족 ({len(group)}개월) → 건너뜀")
            continue

        print(f"🔮 예측 중: {name} ({len(group)}개월 데이터)")

        try:
            forecast = run_prophet(group)
            meta = calc_prediction_meta(group, forecast)

            save_predictions(supabase, keyword_id, forecast, meta)

            results.append(
                {
                    "keyword_id": keyword_id,
                    "current_score": group["trend_score"].iloc[-1],
                    "forecast_scores": forecast["yhat"].tolist(),
                    "prob": meta["prob"],
                    "revival_prob": meta["revival_prob"],
                }
            )

        except Exception as e:
            print(f"  └─ ❌ 오류: {e}")
            continue

    print(f"\n✅ 예측 완료: {len(results)}개 키워드 → trend_predictions 저장")
    print_summary(results, keyword_map)


if __name__ == "__main__":
    run_prediction()
