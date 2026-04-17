# /Users/apple/TrendRadar/data/collectors/trend_cycle.py

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# ─────────────────────────────────────────
# 1. trend_history 전체 조회
# ─────────────────────────────────────────
def fetch_trend_history(supabase) -> pd.DataFrame:
    """
    trend_history 전체 조회 — 페이지네이션으로 1,000개 제한 우회
    """
    all_rows = []
    page_size = 1000
    offset = 0

    while True:
        res = (
            supabase.table("trend_history")
            .select("id, keyword_id, date, trend_score, cycle_stage")
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
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df["trend_score"] = pd.to_numeric(df["trend_score"], errors="coerce").fillna(0)
    return df


# ─────────────────────────────────────────
# 2. 키워드별 Trend Cycle 분류
# ─────────────────────────────────────────
def classify_cycle_advanced(group: pd.DataFrame) -> pd.DataFrame:
    """
    시계열 기반 고도화 분류 로직
    - 3개월 이동평균으로 노이즈 제거
    - change_rate: 3개월 전 대비 변화율
    - peak 경험 여부 누적 추적
    """
    group = group.sort_values("date").copy()
    scores = group["trend_score"]

    # 3개월 이동평균 (window=3, 데이터 부족 시 available 값만 사용)
    group["ma3"] = scores.rolling(window=3, min_periods=1).mean()

    # 3개월 전 대비 변화율
    group["change_rate"] = group["ma3"].pct_change(periods=3).fillna(0.0) * 100

    had_peak = False
    stages = []

    for _, row in group.iterrows():
        score = row["ma3"]
        change = row["change_rate"]

        # 분류 로직
        if score >= 70:
            if change >= -5:
                stage = "peak"
            else:
                stage = "declining"

        elif score >= 40:
            if change >= 10:
                stage = "growing"
            elif change <= -10:
                stage = "declining"
            else:
                stage = "peak"

        elif score >= 20:
            if had_peak and change >= 5:
                stage = "revival"
            elif change >= 15:
                stage = "emerging"
            elif change <= -5:
                stage = "declining"
            else:
                stage = "emerging"

        else:  # score < 20
            if had_peak and change >= 10:
                stage = "revival"
            elif change >= 10:
                stage = "emerging"
            else:
                stage = "declining"

        if stage == "peak":
            had_peak = True

        stages.append(stage)

    group["cycle_stage_new"] = stages
    return group


# ─────────────────────────────────────────
# 3. 전체 키워드 분류 적용
# ─────────────────────────────────────────
def classify_all(df: pd.DataFrame) -> pd.DataFrame:
    results = []
    for keyword_id, group in df.groupby("keyword_id"):
        classified = classify_cycle_advanced(group)
        results.append(classified)
    return pd.concat(results, ignore_index=True)


# ─────────────────────────────────────────
# 4. Supabase 업데이트
# ─────────────────────────────────────────
def update_cycle_stages(supabase, df: pd.DataFrame) -> None:
    updated = 0
    for _, row in df.iterrows():
        supabase.table("trend_history").update(
            {"cycle_stage": row["cycle_stage_new"]}
        ).eq("id", int(row["id"])).execute()
        updated += 1
    print(f"✅ trend_history cycle_stage 업데이트 완료: {updated}개 행")


# ─────────────────────────────────────────
# 5. 결과 요약 출력
# ─────────────────────────────────────────
def print_summary(df: pd.DataFrame, supabase) -> None:
    res = supabase.table("trend_keywords").select("id, name").execute()
    id_to_name = {row["id"]: row["name"] for row in res.data}

    # 키워드별 최신 데이터
    latest = df.sort_values("date").groupby("keyword_id").last().reset_index()
    latest["keyword"] = latest["keyword_id"].map(id_to_name)

    print("\n📊 Trend Cycle 최신 분류 결과 (trend_history 기반):")
    print("-" * 62)
    print(f"{'키워드':<15} {'trend_score':>12} {'change_rate':>12} {'cycle_stage':>12}")
    print("-" * 62)

    for _, row in latest.iterrows():
        print(
            f"{str(row['keyword']):<15} {row['trend_score']:>12.1f} "
            f"{row['change_rate']:>11.1f}% {row['cycle_stage_new']:>12}"
        )

    print("-" * 62)

    # 단계별 분포 (전체)
    stage_counts = df["cycle_stage_new"].value_counts()
    print("\n📈 전체 1,000개 행 단계별 분포:")
    for stage, count in stage_counts.items():
        bar = "█" * (count // 20)
        print(f"  {stage:<12}: {count:>4}개 {bar}")


# ─────────────────────────────────────────
# 실행
# ─────────────────────────────────────────
def run_cycle_classification():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("🔍 trend_history 데이터 조회 중...")
    df = fetch_trend_history(supabase)

    if df.empty:
        print("❌ 데이터 없음")
        return

    print(f"  └─ {len(df)}개 행 로드")
    print("🔄 시계열 기반 Trend Cycle 분류 중...")
    df_classified = classify_all(df)

    print("💾 Supabase 업데이트 중... (1,000개 행, 잠시 걸려요)")
    update_cycle_stages(supabase, df_classified)

    print_summary(df_classified, supabase)


if __name__ == "__main__":
    run_cycle_classification()
